"""Why a reachable Λ → nπ⁰ has a photon without any pure candidate (477's oracle: tagged Hcal, crystal or B0 cluster of
purity ≥ 0.8). Per such photon: the Hcal cluster holding most of its energy and who else is in it, the best crystal
cluster, the B0 side, and the truth distance to the neutron at the Hcal face. Clusters from MSF6_Y9 (identical Hcal and
B0 clusters to Z8); found / missed from Z8's 210 record.

Writes space/perf/no-candidate-causes-<json row>-<dataset>.json. Phase 6, after run 2: where the gap to the reachable yield goes.

Usage: uv run scripts/482_no_candidate_causes.py D6s_9x275 [--files 40]
"""
import argparse
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

REPO = Path("/home/romanov/dev/zdc-autoresearch")
sys.path.insert(0, str(REPO))
spec = importlib.util.spec_from_file_location("e477", REPO / "scripts" / "477_crystal_scope.py")
e477 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e477)
e473, r210 = e477.e473, e477.r210
C, A, B, BA, EH, HH = e477.C, e477.A, e477.B, e477.BA, e477.EH, e477.HH
np_ = e477.np_
e477.CRYS_MIN = 0.3   # the oracle of 477 --why-all on Z8 (params CRYS_MIN 0.3, R_VETO 60)

ap = argparse.ArgumentParser()
ap.add_argument("dataset")
ap.add_argument("--files", type=int, default=40)
ap.add_argument("--geo-row", default="MSF6_Y9")
ap.add_argument("--json-row", default="Z8_hcal_axis_law")
args = ap.parse_args()

J = json.loads((REPO / "space" / "perf" / f"msf-regimes-{args.json_row}-{args.dataset}.json").read_text())
per = defaultdict(list)
for l in J["per_lambda"]:
    h = l["homes"]
    if h[0] == "ZDC" and sorted(h[1:]) in (["ZDC", "ZDC"], ["B0", "ZDC"], ["B0", "B0"]):
        per[(l["file"], l["event"])].append(l)

REG = {("ZDC", "ZDC"): "all-ZDC", ("B0", "ZDC"): "B0+ZDC", ("B0", "B0"): "B0+B0"}
lam_cnt = Counter()            # (regime, status)
pho_cat = Counter()            # (regime, photon home, category)
lam_cat = Counter()            # (regime, category of the Λ: the first photon without a candidate)
dist = defaultdict(list)       # category -> truth distance photon-neutron at the Hcal face (mm)
etrue = defaultdict(list)      # category -> photon energy
share = defaultdict(list)      # category -> neutron share of the photon's main Hcal cluster
dist_ok = []                   # photons with a candidate: distance
eqf = defaultdict(list)        # category -> the photon's ZDC energy-equivalent deposit / its energy (210's eq; < 0.2: leaked)

def mc_vertex(t):
    return t.arrays([f"MCParticles.vertex.{q}" for q in "xyz"], library="ak")

def roots(a, ev):
    """Per nπ⁰ Λ, in truth_event's order: (i_n, i_g1, i_g2)."""
    pdg = ak.to_numpy(a["MCParticles.PDG"][ev]); st = ak.to_numpy(a["MCParticles.generatorStatus"][ev])
    db = ak.to_numpy(a["MCParticles.daughters_begin"][ev]); de = ak.to_numpy(a["MCParticles.daughters_end"][ev])
    dl = ak.to_numpy(a["_MCParticles_daughters.index"][ev])
    kids = lambda i: dl[db[i]:de[i]].tolist()
    out = []
    for il in np.flatnonzero((pdg == 3122) & ((st == 1) | (st == 2))):
        d = kids(il)
        if sorted(int(pdg[k]) for k in d) != [111, 2112]:
            continue
        i_n = next(k for k in d if pdg[k] == 2112); i_pi = next(k for k in d if pdg[k] == 111)
        g = [k for k in kids(i_pi) if pdg[k] == 22]
        if len(g) != 2 or len(kids(i_pi)) != 2:
            continue
        out.append((i_n, g[0], g[1]))
    return out

def face(a, v, ev, i):
    p = e473.to_proton(*(np.array([float(a[f"MCParticles.momentum.{q}"][ev][i])]) for q in "xyz"))[0]
    x0 = e473.to_proton(*(np.array([float(v[f"MCParticles.vertex.{q}"][ev][i])]) for q in "xyz"))[0]
    s = (e477.Z_HCAL - x0[2]) / p[2] if p[2] > 0 else float("nan")
    return x0[:2] + p[:2] * s

files = sorted({k[0] for k in per})[: args.files]
for fname in files:
    sim = uproot.open(f"/data/zdc-autoresearch/datasets/{args.dataset}/{fname}")["events"]
    a = r210.mc_arrays(sim); v = mc_vertex(sim); sa = sim.arrays(e477.sim_branches(), library="ak")
    R = uproot.open(f"/data/zdc-autoresearch/reco/{args.geo_row}/{args.dataset}/{fname.replace('.edm4hep', '.edm4eic')}")["events"].arrays(
        e477.reco_branches(), library="ak")
    for ev in range(len(R)):
        ls = per.get((fname, ev))
        if not ls:
            continue
        lams, owner = r210.truth_event(a, ev)
        rts = roots(a, ev)
        E = np_(R, f"{C}.energy", ev).astype(float)
        P = e473.to_proton(*(np_(R, f"{C}.position.{q}", ev).astype(float) for q in "xyz"))
        sb, sp = np_(R, f"{C}.shapeParameters_begin", ev), np_(R, f"_{C}_shapeParameters", ev)
        cand = e477.tagged_candidates(E, P, sb, sp)
        w = np_(R, f"{A}.weight", ev); rc = np_(R, f"_{A}_rec.index", ev); si = np_(R, f"_{A}_sim.index", ev).astype(int)
        own = owner[si] if len(si) else np.array([], dtype=int)
        Eb_all = np_(R, f"{B}.energy", ev).astype(float)
        keep = [k for k in np.argsort(-Eb_all) if Eb_all[k] >= 1.0][:4]
        wb = np_(R, f"{BA}.weight", ev); rb = np_(R, f"_{BA}_rec.index", ev); sb2 = np_(R, f"_{BA}_sim.index", ev).astype(int)
        ownb = owner[sb2] if len(sb2) else np.array([], dtype=int)
        ce = np_(R, f"{EH}.energy", ev).astype(float); cid = np_(R, f"{EH}.cellID", ev)
        cp = e473.to_proton(*(np_(R, f"{EH}.position.{q}", ev).astype(float) for q in "xyz")) if len(ce) else np.zeros((0, 3))
        cls = e477.recluster(ce, cp[:, 0], cp[:, 1]) if len(ce) else []
        truth = e477.cell_truth(sa, ev, owner)
        for l in ls:
            base = l["owner_base"]
            regime = REG[tuple(sorted(l["homes"][1:]))]
            found = bool(l[args.json_row]["matched"])
            for cl in cls:
                cl["pur"] = {r: e477.cluster_purity(cl, cid, truth, base + r) for r in (1, 2)}
            # 477's crystal candidates (veto split)
            xc_all = []
            for k, cl in enumerate(cls):
                if cl["E"] < e477.CRYS_MIN:
                    continue
                behind = [c for c in cand if math.hypot(P[c][0] * e477.Z_CRYS / P[c][2] - cl["x"], P[c][1] * e477.Z_CRYS / P[c][2] - cl["y"]) <= e477.R_VETO]
                xc_all.append({"k": k, "behind": behind})
            front = Counter(c for x in xc_all for c in x["behind"])
            split = {x["k"] for x in xc_all if not x["behind"] or any(front[c] >= 2 for c in x["behind"])}
            fn = face(a, v, ev, rts[base // 3][0]) if base // 3 < len(rts) else None
            cats = []
            for r in (1, 2):
                home = l["homes"][r]
                pur_c = lambda c, o: float(w[(rc == c) & (own == o)].sum())
                pz = [c for c in cand if pur_c(c, base + r) >= 0.8]
                pb = [k for k in keep if float(wb[(rb == k) & (ownb == base + r)].sum()) >= 0.8]
                pc = [k for k, cl in enumerate(cls) if cl["pur"][r] >= 0.8 and k in split]
                gface = face(a, v, ev, rts[base // 3][r]) if base // 3 < len(rts) else None
                d = float(np.hypot(*(gface - fn))) if gface is not None and fn is not None else float("nan")
                if pz or pb or pc:
                    cats.append(None)
                    if home == "ZDC":
                        dist_ok.append(d)
                    continue
                if home == "B0":
                    tot_b = [(float(wb[(rb == k) & (ownb == base + r)].sum()), k) for k in range(len(Eb_all))]
                    best = max(tot_b, default=(0.0, -1))
                    if best[1] < 0 or best[0] < 0.05:
                        cat = "B0: no B0 cluster"
                    elif best[0] >= 0.8 and Eb_all[best[1]] < 1.0:
                        cat = "B0: pure, below 1 GeV"
                    elif best[0] >= 0.8:
                        cat = "B0: pure, not in the top 4"
                    else:
                        k = best[1]
                        fo = float(wb[(rb == k) & (ownb == base + 3 - r)].sum()); fnb = float(wb[(rb == k) & (ownb == base)].sum())
                        dom = max((fo, "the other photon"), (fnb, "the neutron"), (1 - best[0] - fo - fnb, "other particles"))[1]
                        cat = f"B0: shares a B0 cluster with {dom}"
                else:
                    contrib = [(pur_c(c, base + r) * E[c], c) for c in range(len(E))]
                    emain, cm = max(contrib, default=(0.0, -1))
                    best_cr = max(cls, key=lambda c: c["pur"][r] * c["E"], default=None)
                    cr_pure = best_cr is not None and best_cr["pur"][r] >= 0.8
                    if cm < 0 or emain <= 0:
                        cat = "ZDC: no Hcal cluster" + ((", crystal pure but " + ("< 0.3 GeV" if best_cr["E"] < e477.CRYS_MIN else "vetoed")) if cr_pure else ", no pure crystal")
                    else:
                        fs, fnn = pur_c(cm, base + r), pur_c(cm, base)
                        fg = pur_c(cm, base + 3 - r)
                        share[("n", )].append(fnn)
                        if fs >= 0.8:
                            deep = P[cm][2] > e473.ZMAX
                            cat = "ZDC: pure Hcal cluster, photon tag fails" + (" (depth)" if deep else " (shape)")
                        else:
                            other = 1 - fs - fnn - fg
                            dom = max((fnn, "the neutron"), (fg, "the other photon"), (other, "other particles"))[1]
                            cat = f"ZDC: shares its Hcal cluster with {dom}"
                        if not ("pure Hcal" in cat) and cr_pure:
                            cat += "; crystal pure but " + ("< 0.3 GeV" if best_cr["E"] < e477.CRYS_MIN else "vetoed")
                cats.append(cat)
                pho_cat[(regime, home, cat)] += 1
                dist[cat].append(d); etrue[cat].append(l["E"][r])
                eqf[cat].append(l["eq"][r].get("ZDC", 0.0) / l["E"][r])
            missing = [c for c in cats if c]
            status = "found" if found else ("no candidate" if missing else "candidates, missed")
            lam_cnt[(regime, status)] += 1
            if missing:
                lam_cat[(regime, missing[0] if len(missing) == 1 else "both photons: " + missing[0])] += 1
                if found:
                    lam_cnt[(regime, "found although no 477 candidate")] += 1

print(f"== {args.dataset}: {len(files)} files")
for k, n in sorted(lam_cnt.items()):
    print(f"  {k[0]:8s} {k[1]:34s} {n:5d}")
print("-- photons without a candidate, by cause")
for k, n in sorted(pho_cat.items(), key=lambda kv: (kv[0][0], -kv[1])):
    q = np.nanpercentile(dist[k[2]], [16, 50, 84]) if dist[k[2]] else [float("nan")] * 3
    e = np.median(etrue[k[2]]) if etrue[k[2]] else float("nan")
    lk = np.mean(np.array(eqf[k[2]]) < 0.2) if eqf[k[2]] else float("nan")
    print(f"  {k[0]:8s} {n:5d}  {k[2]:75s} d(γ,n) {q[1]:6.0f} mm [{q[0]:.0f}, {q[2]:.0f}]  E_γ {e:5.1f} GeV  leaked (eq/E < 0.2) {100 * lk:3.0f} %")
if dist_ok:
    q = np.nanpercentile(dist_ok, [16, 50, 84])
    print(f"  ZDC photons with a candidate: d(γ,n) {q[1]:.0f} mm [{q[0]:.0f}, {q[2]:.0f}]  n={len(dist_ok)}")
out = {"dataset": args.dataset, "lambda": {f"{a}|{b}": n for (a, b), n in lam_cnt.items()},
       "photons": {f"{a}|{b}|{c}": n for (a, b, c), n in pho_cat.items()},
       "lambda_by_cause": {f"{a}|{b}": n for (a, b), n in lam_cat.items()},
       "dist_median": {k: float(np.nanmedian(v)) for k, v in dist.items() if v},
       "dist_ok_median": float(np.nanmedian(dist_ok)) if dist_ok else None,
       "leaked_share": {k: float(np.mean(np.array(v) < 0.2)) for k, v in eqf.items() if v}}
(REPO / "space" / "perf" / f"no-candidate-causes-{args.json_row}-{args.dataset}.json").write_text(json.dumps(out, indent=1))
