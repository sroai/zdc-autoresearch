"""Usage: uv run scripts/476_msf_t_resolution.py [row ...]   (default: Y9_external_pair MSF5_X9)
−t resolution of the truth-matched Λ → nπ⁰ of a Phase 5 row on the MSF search halves.
Matched Λ and their candidate mass come from 210's per-Λ record (space/perf/msf-regimes-<row>-<ds>.json); the candidate is
the in-window ReconstructedLambdas entry with that mass. −t = −(P_beam − P_Λ)²; reco uses the nominal beam (meson-structure
kaon-lambda/config.py: E_p, crossing −25 mrad in xz), truth uses the event's generator beam proton (status 4) and the
generator Λ. Also: the detector-only part (truth Λ with the nominal beam)."""
import json, math, sys
from pathlib import Path
import awkward as ak, numpy as np, uproot
REPO = Path("/home/romanov/dev/zdc-autoresearch")
MP = 0.9382720813
rows = sys.argv[1:] or ["Y9_external_pair", "MSF5_X9"]


def beam(E):
    p = math.sqrt(E * E - MP * MP); a = -25e-3
    return np.array([E, p * math.sin(a), 0.0, p * math.cos(a)])


def mt(b, l):
    d = b - l
    return -(d[0] ** 2 - d[1] ** 2 - d[2] ** 2 - d[3] ** 2)


def robust(x):
    x = np.asarray(x); med = float(np.median(x))
    q16, q84 = np.percentile(x, [16, 84])
    return med, 0.5 * (q84 - q16), float(np.sqrt(np.mean((x - x.mean()) ** 2)))


out = {}
summary = {}
for row in rows:
    for beamname, E in (("9x275", 275.0), ("9x130", 130.0)):
        ds = f"D6s_{beamname}"
        J = json.load(open(REPO / "space" / "perf" / f"msf-regimes-{row}-{ds}.json"))
        mlist = [l for l in J["per_lambda"] if l.get(row, {}).get("matched")]
        byfile = {}
        for l in mlist:
            byfile.setdefault(l["file"], []).append(l)
        B = beam(E)
        recs = []
        for fname, ls in sorted(byfile.items()):
            a = uproot.open(f"/data/zdc-autoresearch/datasets/{ds}/{fname}")["events"].arrays(
                [f"MCParticles.{x}" for x in ("PDG", "generatorStatus", "momentum.x", "momentum.y", "momentum.z", "mass",
                                              "daughters_begin", "daughters_end")] + ["_MCParticles_daughters.index"], library="ak")
            r = uproot.open(f"/data/zdc-autoresearch/reco/{row}/{ds}/{fname.replace('.edm4hep', '.edm4eic')}")["events"].arrays(
                [f"ReconstructedLambdas.{x}" for x in ("mass", "energy", "momentum.x", "momentum.y", "momentum.z")], library="ak")
            for l in ls:
                ev = l["event"]
                pdg = ak.to_numpy(a["MCParticles.PDG"][ev]); st = ak.to_numpy(a["MCParticles.generatorStatus"][ev])
                px, py, pz, m = (ak.to_numpy(a[f"MCParticles.{q}"][ev]) for q in ("momentum.x", "momentum.y", "momentum.z", "mass"))
                db = ak.to_numpy(a["MCParticles.daughters_begin"][ev]); de = ak.to_numpy(a["MCParticles.daughters_end"][ev])
                dl = ak.to_numpy(a["_MCParticles_daughters.index"][ev])
                # the k-th nπ⁰ Λ (210's order) has owner_base 3k
                k = 0; il_hit = None
                for il in np.flatnonzero((pdg == 3122) & ((st == 1) | (st == 2))):
                    d = dl[db[il]:de[il]]
                    if sorted(int(pdg[q]) for q in d) != [111, 2112]:
                        continue
                    ipi = next(q for q in d if pdg[q] == 111)
                    gk = dl[db[ipi]:de[ipi]]
                    if len(gk) != 2 or not all(pdg[q] == 22 for q in gk):
                        continue
                    if 3 * k == l["owner_base"]:
                        il_hit = il; break
                    k += 1
                assert il_hit is not None
                ib = int(np.flatnonzero((st == 4) & (pdg == 2212))[0])
                eb = math.sqrt(px[ib] ** 2 + py[ib] ** 2 + pz[ib] ** 2 + m[ib] ** 2)
                Bt = np.array([eb, px[ib], py[ib], pz[ib]])
                el = math.sqrt(px[il_hit] ** 2 + py[il_hit] ** 2 + pz[il_hit] ** 2 + m[il_hit] ** 2)
                Lt = np.array([el, px[il_hit], py[il_hit], pz[il_hit]])
                rm = ak.to_numpy(r["ReconstructedLambdas.mass"][ev])
                js = np.flatnonzero(np.isclose(rm, l[row]["mass"], rtol=0, atol=1e-7))
                assert len(js) >= 1, (fname, ev)
                j = js[0]
                Lr = np.array([float(r[f"ReconstructedLambdas.{q}"][ev][j]) for q in ("energy", "momentum.x", "momentum.y", "momentum.z")])
                recs.append({"t_true": mt(Bt, Lt), "t_true_nom": mt(B, Lt), "t_reco": mt(B, Lr),
                             "E_true": el, "E_reco": Lr[0], "pt_true": math.hypot(Lt[1], Lt[2]),
                             "zdc_only": l["homes"] == ["ZDC", "ZDC", "ZDC"], "multi": len(js)})
        out[(row, beamname)] = recs
        tt = np.array([x["t_true"] for x in recs]); tr = np.array([x["t_reco"] for x in recs]); tn = np.array([x["t_true_nom"] for x in recs])
        d = tr - tt
        med, s68, rms = robust(d)
        sm = summary.setdefault(row, {})[beamname] = {"n": len(recs), "t_true_median": float(np.median(tt)), "bias": med, "sigma68": s68, "rms": rms, "within_0.1": float(np.mean(abs(d) < 0.1)), "within_0.05": float(np.mean(abs(d) < 0.05)), "bins": {}, "regimes": {}}
        medb, s68b, _ = robust(tn - tt)
        medd, s68d, _ = robust(tr - tn)
        print(f"\n{row} {beamname}: {len(recs)} matched Λ (multi-mass hits {sum(x['multi'] > 1 for x in recs)}); "
              f"true −t median {np.median(tt):.3f}, 68 % range {np.percentile(tt, 16):.3f}–{np.percentile(tt, 84):.3f} GeV²")
        print(f"  Δ(−t) reco − true: median {med:+.4f}, σ68 {s68:.4f}, RMS {rms:.4f} GeV²;  |Δ| < 0.1: {100 * np.mean(abs(d) < 0.1):.1f} %, "
              f"< 0.05: {100 * np.mean(abs(d) < 0.05):.1f} %")
        sm["beam_part_sigma68"], sm["detector_part_sigma68"] = s68b, s68d
        print(f"  beam part (nominal vs event beam, truth Λ): median {medb:+.4f}, σ68 {s68b:.4f};  detector part: median {medd:+.4f}, σ68 {s68d:.4f}")
        for lo, hi in ((0, 0.2), (0.2, 0.5), (0.5, 1.0), (1.0, 3.0)):
            s = (tt >= lo) & (tt < hi)
            if s.sum() >= 10:
                mm, ss, _ = robust(d[s])
                sm["bins"][f"{lo:.1f}-{hi:.1f}"] = {"n": int(s.sum()), "bias": mm, "sigma68": ss}
                print(f"    true −t {lo:.1f}–{hi:.1f}: n {s.sum():4d}  bias {mm:+.4f}  σ68 {ss:.4f} GeV²  (rel {ss / np.median(tt[s]):.2f})")
        z = np.array([x["zdc_only"] for x in recs])
        for lab, s in (("all in ZDC", z), ("with B0 photon(s)", ~z)):
            if s.sum() >= 10:
                mm, ss, _ = robust(d[s])
                sm["regimes"][lab] = {"n": int(s.sum()), "bias": mm, "sigma68": ss}
                print(f"    {lab:18s}: n {s.sum():4d}  bias {mm:+.4f}  σ68 {ss:.4f} GeV²")
        er = np.array([x["E_reco"] / x["E_true"] for x in recs])
        print(f"  E_Λ reco/true: median {np.median(er):.3f}, σ68 {0.5 * (np.percentile(er, 84) - np.percentile(er, 16)):.3f}")
np.save(Path("/data/zdc-autoresearch/logs") / "476_t_resolution.npy", np.array([{"row": k[0], "beam": k[1], "recs": v} for k, v in out.items()], dtype=object))
for row, v in summary.items():
    (REPO / "space" / "perf" / f"t-resolution-{row}.json").write_text(json.dumps(v, indent=1))
    print("wrote", REPO / "space" / "perf" / f"t-resolution-{row}.json")
