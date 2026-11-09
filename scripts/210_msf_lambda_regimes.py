#!/usr/bin/env python3
"""Λ → nπ⁰ on MSF events by detector regime: where the n and the two γ land, the ceiling each regime sets, and
what a reconstruction row recovers in it. Phase 5 (zdc-autoresearch-loop-v5.md) scores its tries with it: N_found,
N_window and purity per row, compared by 463.

Truth (the dataset's edm4hep sim files): every generator Λ (PDG 3122, generatorStatus 1, decayed by Geant4, or 2,
decayed by the gun) is classified by its decay (npi0, ppi, npi0_dalitz, other, undecayed). For nπ⁰, each daughter
(n, γ1, γ2; π⁰ → γγ) owns itself and every saved descendant (conversions, neutron secondaries), and its
calorimeter deposits are summed from the sim-hit contributions. A daughter's home is the detector group with the
largest energy-equivalent deposit (deposit / sampling fraction), if that is at least --home-min GeV: ZDC
(HcalFarForwardZDC + EcalFarForwardZDC), B0 (B0ECal), EEMCP (EcalEndcapP), LFHCAL (LFHCAL + HcalEndcapPInsert),
else none. The regime is the n's home and the γ homes, e.g. "n ZDC | γ B0+ZDC". The ceiling of a regime is its
share of all Λ → nπ⁰ (perfect reconstruction of every Λ in it).

Reconstruction (with --row): a Λ → nπ⁰ is recovered when a ReconstructedLambdas entry within the scoring window
(configs/metrics.yaml, ±30 MeV) has three daughters: a ZDC neutron neutral holding a cluster of purity ≥ 0.8 for
the true n, and two photon neutrals holding clusters of purity ≥ 0.8 for the two distinct true photons (ZDC, B0 or
EEMC-P neutrals). Purity is the sum of the cluster's association weights over the particle and its descendants, as
410 does for the ZDC. A slim row has no B0 / EEMC-P associations: --assoc-from names a full-template row whose B0
and EEMC-P neutrals are checked identical, event by event, and whose associations are then used.
Per regime the script also records why an event is lost: no matched neutron neutral, a true photon without a
matched photon neutral, the true triplet built but outside the window, another triplet chosen.
Groups: the regimes merged as the chain sees them, normalized to the expected Λ → nπ⁰ (generator Λ × BR 0.358).
Per row (Phase 5, loop v5): N_found (recovered Λ → nπ⁰), N_window (events with a ReconstructedLambdas entry inside
the window, right or wrong), yield = N_found / N_expected and purity = N_found / N_window, with binomial errors.

Writes space/perf/msf-regimes-<rows or truth>-<dataset>.json and prints the regime table.

Usage: uv run scripts/210_msf_lambda_regimes.py D6a_9x275 --row CP2_X9_S5 --row R1_pr3064 --assoc-from R1_pr3064
       uv run scripts/210_msf_lambda_regimes.py D4_lambda --files D4_lambda_275GeV_seed1 --row X9_pairing_photon_depth
       uv run scripts/210_msf_lambda_regimes.py D6s_9x275 --row Y1_b0_photon_energy        # a Phase 5 try
"""
import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import dataset_dir, load_profile, metrics_config, reco_dir, repo_path  # noqa: E402
from zdc.edm import binomial_error, collection_ids  # noqa: E402

# detector group -> [(sim-hit collection, sampling fraction)]; the fractions only rank groups against each other
GROUPS = {
    "ZDC": [("HcalFarForwardZDCHits", 0.0273), ("EcalFarForwardZDCHits", 1.0)],
    "B0": [("B0ECalHits", 1.0)],
    "EEMCP": [("EcalEndcapPHits", 0.03)],
    "LFHCAL": [("LFHCALHits", 0.025), ("HcalEndcapPInsertHits", 0.02)],
}
NEUTRALS = {"ZDC": "ReconstructedHcalFarForwardZDCNeutrals", "B0": "ReconstructedB0EcalNeutrals",
            "EEMCP": "ReconstructedEcalEndcapPNeutrals", "LFHCAL": "ReconstructedLFHCALNeutrals"}
BR_NPI0 = 0.358   # PDG Λ → nπ⁰ branching fraction
ASSOC = {"ZDC": "HcalFarForwardZDCClusterAssociations", "B0": "B0ECalClusterAssociations",
         "EEMCP": "EcalEndcapPClusterAssociations"}
# Phase 5: a ZDC neutral may also link clusters of the LYSO crystal section in front of the Hcal; their associations
# count for the ZDC group when the output carries them. Clusters are matched by (collection ID, index).
ASSOC_EXTRA = {"ZDC": ["EcalFarForwardZDCClusterAssociations"]}


def assoc_names(grp):
    return [ASSOC[grp]] + ASSOC_EXTRA.get(grp, [])


def leaf_names(t):
    return {k.split("/")[-1] for k in t.keys()}   # nested branch paths end in the leaf name


def mc_arrays(t):
    f = ["PDG", "generatorStatus", "momentum.x", "momentum.y", "momentum.z", "mass", "endpoint.z",
         "daughters_begin", "daughters_end"]
    return t.arrays([f"MCParticles.{x}" for x in f] + ["_MCParticles_daughters.index"], library="ak")


def truth_event(a, ev):
    """The generator Λ of one event and, for nπ⁰, the owner array: owner[i] = 3·(nπ⁰ Λ number) + role
    (0 n, 1 γ1, 2 γ2) for each daughter and its saved descendants, else -1."""
    pdg = ak.to_numpy(a["MCParticles.PDG"][ev]); st = ak.to_numpy(a["MCParticles.generatorStatus"][ev])
    db = ak.to_numpy(a["MCParticles.daughters_begin"][ev]); de = ak.to_numpy(a["MCParticles.daughters_end"][ev])
    dl = ak.to_numpy(a["_MCParticles_daughters.index"][ev])
    px = ak.to_numpy(a["MCParticles.momentum.x"][ev]); py = ak.to_numpy(a["MCParticles.momentum.y"][ev])
    pz = ak.to_numpy(a["MCParticles.momentum.z"][ev]); m = ak.to_numpy(a["MCParticles.mass"][ev])
    endz = ak.to_numpy(a["MCParticles.endpoint.z"][ev])
    kids = lambda i: dl[db[i]:de[i]].tolist()
    energy = lambda k: float(math.sqrt(px[k] ** 2 + py[k] ** 2 + pz[k] ** 2 + m[k] ** 2))
    out, owner, n_npi0 = [], np.full(len(pdg), -1, dtype=np.int64), 0
    for il in np.flatnonzero((pdg == 3122) & ((st == 1) | (st == 2))):
        d = kids(il)
        dp = sorted(int(pdg[k]) for k in d)
        rec = {"p": float(math.sqrt(px[il] ** 2 + py[il] ** 2 + pz[il] ** 2)), "decay_z": float(endz[il])}
        if not d:
            rec["mode"] = "undecayed"
        elif dp == [-211, 2212]:
            rec["mode"] = "ppi"
        elif dp != [111, 2112]:
            rec["mode"] = "other"
        else:
            i_n = next(k for k in d if pdg[k] == 2112); i_pi = next(k for k in d if pdg[k] == 111)
            g = [k for k in kids(i_pi) if pdg[k] == 22]
            if len(g) != 2 or len(kids(i_pi)) != 2:
                rec["mode"] = "npi0_dalitz"
            else:
                rec["mode"] = "npi0"
                base = 3 * n_npi0
                n_npi0 += 1
                for r, root in enumerate([i_n, g[0], g[1]]):
                    stack = [root]
                    while stack:
                        j = stack.pop()
                        if owner[j] == -1:
                            owner[j] = base + r
                            stack.extend(kids(j))
                rec.update({"owner_base": base, "E": [energy(k) for k in (i_n, g[0], g[1])]})
        out.append(rec)
    return out, owner


def deposits_event(sa, ev, owner):
    """Energy-equivalent deposit (GeV) per detector group and owner."""
    dep = {grp: defaultdict(float) for grp in GROUPS}
    for grp, colls in GROUPS.items():
        for coll, sf in colls:
            key = f"{coll}Contributions.energy"
            if key not in sa.fields:
                continue
            e = ak.to_numpy(sa[key][ev]); pi = ak.to_numpy(sa[f"_{coll}Contributions_particle.index"][ev])
            if len(e) == 0:
                continue
            o = owner[pi]
            sel = o >= 0
            if sel.any():
                uo, inv = np.unique(o[sel], return_inverse=True)
                for oo, s in zip(uo, np.bincount(inv, weights=e[sel])):
                    dep[grp][int(oo)] += float(s) / sf
    return dep


def sim_branches(t):
    have = leaf_names(t)
    br = []
    for colls in GROUPS.values():
        for coll, _ in colls:
            br += [f"{coll}Contributions.energy", f"_{coll}Contributions_particle.index"]
    return [b for b in br if b in have]


def reco_arrays(path, groups_assoc):
    """The row's Λ, neutrals and associations; groups_assoc: the groups whose associations to read from this file."""
    t = uproot.open(path)["events"]
    have = leaf_names(t)
    br = ["ReconstructedLambdas.mass", "ReconstructedLambdas.particles_begin", "ReconstructedLambdas.particles_end",
          "_ReconstructedLambdas_particles.index", "_ReconstructedLambdas_particles.collectionID"]
    for col in NEUTRALS.values():
        br += [f"{col}.PDG", f"{col}.energy", f"{col}.clusters_begin", f"{col}.clusters_end", f"_{col}_clusters.index",
               f"_{col}_clusters.collectionID"]
    for grp in groups_assoc:
        for a in assoc_names(grp):
            br += [f"{a}.weight", f"_{a}_rec.index", f"_{a}_rec.collectionID", f"_{a}_sim.index"]
    missing = [b for b in br if b not in have]
    arr = t.arrays([b for b in br if b in have], library="ak")
    ids = collection_ids(path)
    cid = {grp: ids.get(col, -999) for grp, col in NEUTRALS.items()}
    return arr, cid, t.num_entries, missing


def reco_event(ra, aa, cid, ev, lams, owner, purity_min, win_c, win_h, stats):
    """Per nπ⁰ Λ of the event: matched flag and loss reason. ra: the row; aa: where the B0 / EEMC-P associations
    come from (the row itself or --assoc-from, with identical neutrals)."""
    g = lambda arr, k: ak.to_numpy(arr[k][ev]) if k in arr.fields else np.array([])
    neu = {grp: {"pdg": g(ra, f"{col}.PDG"), "E": g(ra, f"{col}.energy"), "cb": g(ra, f"{col}.clusters_begin"),
                 "ce": g(ra, f"{col}.clusters_end"), "ci": g(ra, f"_{col}_clusters.index"),
                 "cc": g(ra, f"_{col}_clusters.collectionID")} for grp, col in NEUTRALS.items()}
    asc = {}
    for grp in ASSOC:
        src = ra if grp == "ZDC" else aa
        parts = []
        for a in assoc_names(grp):
            if f"{a}.weight" not in src.fields:
                continue
            si = g(src, f"_{a}_sim.index").astype(np.int64)
            parts.append((g(src, f"{a}.weight"), g(src, f"_{a}_rec.collectionID").astype(np.int64),
                          g(src, f"_{a}_rec.index").astype(np.int64), owner[si] if len(si) else np.array([], dtype=np.int64)))
        if parts:
            asc[grp] = tuple(np.concatenate([p[i] for p in parts]) for i in range(4))

    def matches(grp, k, own):
        """Neutral k of group grp holds a cluster of purity ≥ purity_min for owner own."""
        if grp not in asc:
            return False
        w, rcid, rc, so = asc[grp]
        n = neu[grp]
        links = range(n["cb"][k], n["ce"][k])
        return any(float(w[(rcid == int(n["cc"][j])) & (rc == int(n["ci"][j])) & (so == own)].sum()) >= purity_min for j in links)

    m = g(ra, "ReconstructedLambdas.mass"); lb = g(ra, "ReconstructedLambdas.particles_begin")
    le = g(ra, "ReconstructedLambdas.particles_end"); li = g(ra, "_ReconstructedLambdas_particles.index")
    lc = g(ra, "_ReconstructedLambdas_particles.collectionID")
    gid = {v: k for k, v in cid.items()}
    results = []
    for lam in lams:
        if lam["mode"] != "npi0":
            continue
        base = lam["owner_base"]
        n_ok = any(neu["ZDC"]["pdg"][k] == 2112 and matches("ZDC", k, base) for k in range(len(neu["ZDC"]["pdg"])))
        g_av = []
        for r in (1, 2):
            av = None
            for grp in ("ZDC", "B0", "EEMCP"):
                for k in range(len(neu[grp]["pdg"])):
                    if neu[grp]["pdg"][k] == 22 and matches(grp, k, base + r):
                        av = grp
                        stats["photon_ratio"][grp].append(float(neu[grp]["E"][k] / lam["E"][r]))
            g_av.append(av)
        matched, mass, true_triplet_mass = False, None, None
        for j in range(len(m)):
            if le[j] - lb[j] != 3:
                continue
            parts = [(gid.get(int(lc[x])), int(li[x])) for x in range(lb[j], le[j])]
            if any(p[0] is None for p in parts):
                continue
            ns = [p for p in parts if neu[p[0]]["pdg"][p[1]] == 2112]
            gs = [p for p in parts if neu[p[0]]["pdg"][p[1]] == 22]
            if len(ns) != 1 or len(gs) != 2 or ns[0][0] != "ZDC" or not matches("ZDC", ns[0][1], base):
                continue
            a1 = [matches(gs[0][0], gs[0][1], base + r) for r in (1, 2)]
            a2 = [matches(gs[1][0], gs[1][1], base + r) for r in (1, 2)]
            if (a1[0] and a2[1]) or (a1[1] and a2[0]):
                true_triplet_mass = float(m[j])
                if abs(m[j] - win_c) < win_h:
                    matched, mass = True, float(m[j])
                    break
        in_window = bool(len(m) and (np.abs(m - win_c) < win_h).any())
        if matched:
            reason = "matched"
        elif not n_ok:
            reason = "no_neutron"
        elif not all(g_av):
            reason = "photon_missing"
        elif true_triplet_mass is not None:
            reason = "true_triplet_out_of_window"
        else:
            reason = "other_triplet_chosen"
        results.append({"matched": matched, "reason": reason, "mass": mass, "any_in_window": in_window,
                        "photon_groups": g_av, "true_triplet_mass": true_triplet_mass})
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--row", action="append", default=[])
    ap.add_argument("--assoc-from", help="full-template row giving B0 / EEMC-P associations to slim rows")
    ap.add_argument("--files", nargs="*", help="file stems to use (default: every file of the dataset)")
    ap.add_argument("--home-min", type=float, default=0.5, help="GeV energy-equivalent deposit for a home")
    args = ap.parse_args()
    prof = load_profile(); mcfg = metrics_config()
    files = sorted(dataset_dir(prof, args.dataset).glob("*.edm4hep.root"))
    if args.files:
        files = [f for f in files if f.name.split(".")[0] in args.files]
    win_c, win_h = float(mcfg.windows.lambda_mass_gev), float(mcfg.windows.lambda_mass_half_window_gev)
    purity_min = float(mcfg.truth_match.purity_min)
    lambdas, per_row = [], {r: [] for r in args.row}
    stats = {r: {"photon_ratio": {"ZDC": [], "B0": [], "EEMCP": []}} for r in args.row}
    n_events = 0
    cand = {r: {"events_with_candidate": 0, "events_in_window": 0} for r in args.row}
    for f in files:
        t = uproot.open(f)["events"]
        a = mc_arrays(t)
        sa = t.arrays(sim_branches(t), library="ak")
        readers = {}
        for r in args.row:
            rp = reco_dir(prof, r, args.dataset) / f.name.replace(".edm4hep.root", ".edm4eic.root")
            ra, cid, ne, missing = reco_arrays(rp, ["ZDC", "B0", "EEMCP"])
            assert ne == t.num_entries, f"{rp}: {ne} events, sim {t.num_entries}"
            aa = ra
            if any(f"{ASSOC[x]}.weight" in missing for x in ("B0", "EEMCP")) and args.dataset.startswith("D6"):
                assert args.assoc_from, f"{r} has no B0 / EEMC-P associations: give --assoc-from"
                aa, _, ne2, _ = reco_arrays(reco_dir(prof, args.assoc_from, args.dataset) / rp.name, ["B0", "EEMCP"])
                assert ne2 == ne
                for grp in ("B0", "EEMCP"):     # the associations apply only if the neutrals are the same objects
                    for fld in ("energy", "clusters_begin"):
                        x, y = ra[f"{NEUTRALS[grp]}.{fld}"], aa[f"{NEUTRALS[grp]}.{fld}"]
                        assert ak.all(ak.num(x) == ak.num(y)) and np.array_equal(ak.to_numpy(ak.flatten(x)), ak.to_numpy(ak.flatten(y))), \
                            f"{grp} neutrals differ between {r} and {args.assoc_from}"
            # the reconstruction must belong to this simulation file: every association's MC index inside the event's
            # MCParticles (a row whose outputs are shuffled against the inputs stops here, by name)
            n_mc = ak.num(a["MCParticles.PDG"])
            for grp, an in ((g_, an_) for g_ in ASSOC for an_ in assoc_names(g_)):
                src = ra if grp == "ZDC" else aa
                col = f"_{an}_sim.index"
                if col in src.fields and ak.any(ak.fill_none(ak.max(src[col], axis=1), -1) >= n_mc):
                    sys.exit(f"MISMATCH {rp}: {grp} associations point past the MCParticles of {f.name}: "
                             "the reconstruction does not belong to this simulation file")
            readers[r] = (ra, aa, cid)
            if "ReconstructedLambdas.mass" in ra.fields:
                lm = ra["ReconstructedLambdas.mass"]
                cand[r]["events_with_candidate"] += int(ak.sum(ak.num(lm) > 0))
                cand[r]["events_in_window"] += int(ak.sum(ak.any(abs(lm - win_c) < win_h, axis=1)))
        for ev in range(t.num_entries):
            lams, owner = truth_event(a, ev)
            dep = deposits_event(sa, ev, owner)
            for lam in lams:
                lam["file"] = f.name
                lam["event"] = ev
                if lam["mode"] != "npi0":
                    continue
                homes, eqs = [], []
                for r in range(3):
                    eq = {grp: dep[grp].get(lam["owner_base"] + r, 0.0) for grp in GROUPS}
                    best = max(eq, key=eq.get)
                    homes.append(best if eq[best] >= args.home_min else "none")
                    eqs.append({k: round(v, 3) for k, v in eq.items() if v > 0})
                lam["homes"], lam["eq"] = homes, eqs
                lam["regime"] = f"n {homes[0]} | γ {'+'.join(sorted(homes[1:]))}"
            lambdas += lams
            for r, (ra, aa, cid) in readers.items():
                per_row[r] += reco_event(ra, aa, cid, ev, lams, owner, purity_min, win_c, win_h, stats[r])
        n_events += t.num_entries
    npi0 = [l for l in lambdas if l["mode"] == "npi0"]
    modes = Counter(l["mode"] for l in lambdas)
    table = []
    for reg, n in Counter(l["regime"] for l in npi0).most_common():
        idx = [i for i, l in enumerate(npi0) if l["regime"] == reg]
        row = {"regime": reg, "n": n, "share_of_npi0": n / len(npi0), "share_of_lambda": n / len(lambdas),
               "lambda_p_median": float(np.median([npi0[i]["p"] for i in idx])),
               "decay_z_median_m": float(np.median([npi0[i]["decay_z"] for i in idx]) / 1000)}
        for r in args.row:
            res = [per_row[r][i] for i in idx]
            k = sum(x["matched"] for x in res)
            row[r] = {"matched": k, "eff": k / n, "eff_err": binomial_error(k, n),
                      "reasons": dict(Counter(x["reason"] for x in res)),
                      "any_in_window": sum(x["any_in_window"] for x in res),
                      "masses": [x["mass"] for x in res if x["matched"]]}
        table.append(row)
    def group_of(l):
        n, gs = l["homes"][0], l["homes"][1:]
        if n != "ZDC":
            return "n in B0" if n == "B0" else "n lost or elsewhere"
        if "none" in gs:
            return "n ZDC, a γ lost"
        if any(x in ("EEMCP", "LFHCAL") for x in gs):
            return "n ZDC, a γ in EEMC-P / LFHCAL"
        return {("ZDC", "ZDC"): "all three in the ZDC", ("B0", "ZDC"): "n ZDC, γ B0 + γ ZDC",
                ("B0", "B0"): "n ZDC, γ γ in B0"}[tuple(sorted(gs))]
    expected = BR_NPI0 * len(lambdas)
    groups = []
    for name in ("all three in the ZDC", "n ZDC, γ B0 + γ ZDC", "n ZDC, γ γ in B0", "n ZDC, a γ in EEMC-P / LFHCAL",
                 "n ZDC, a γ lost", "n in B0", "n lost or elsewhere"):
        idx = [i for i, l in enumerate(npi0) if group_of(l) == name]
        gr = {"group": name, "n": len(idx), "share_of_expected_npi0": len(idx) / expected}
        for r in args.row:
            res = [per_row[r][i] for i in idx]
            k = sum(x["matched"] for x in res)
            gr[r] = {"matched": k, "per_expected_npi0": k / expected, "eff_in_group": k / len(idx) if idx else None,
                     "eff_err": binomial_error(k, len(idx)) if idx else None, "reasons": dict(Counter(x["reason"] for x in res)),
                     "true_triplet_masses": [x["true_triplet_mass"] for x in res if x["true_triplet_mass"] is not None]}
        groups.append(gr)
    lost_before = {"material_interaction": modes.get("other", 0) / len(lambdas),   # "other": >2 products, nuclei among them
                   "undecayed": modes.get("undecayed", 0) / len(lambdas)}
    ratio = {r: {grp: ({"n": len(v), "median": float(np.median(v)), "p16_p84": [float(x) for x in np.percentile(v, [16, 84])]}
                       if v else {"n": 0}) for grp, v in s["photon_ratio"].items()} for r, s in stats.items()}
    rows = {}
    for r in args.row:
        k, nw = sum(x["matched"] for x in per_row[r]), cand[r]["events_in_window"]
        rows[r] = {"N_found": k, "N_window": nw, "events_with_candidate": cand[r]["events_with_candidate"],
                   "N_expected": BR_NPI0 * len(lambdas), "yield": k / (BR_NPI0 * len(lambdas)),
                   "yield_err": binomial_error(k, BR_NPI0 * len(lambdas)),
                   "purity": k / nw if nw else None, "purity_err": binomial_error(k, nw) if nw else None}
    out = {"dataset": args.dataset, "rows": rows, "files": [f.name for f in files], "events": n_events, "lambdas": len(lambdas),
           "modes": dict(modes), "npi0": len(npi0), "home_min_gev": args.home_min, "assoc_from": args.assoc_from,
           "expected_npi0": expected, "br_npi0": BR_NPI0, "groups": groups,
           "lambda_lost_before_decay_share_of_all": lost_before,
           "regimes": table, "photon_E_reco_over_true": ratio,
           "per_lambda": [{**l, **{r: per_row[r][i] for r in args.row}} for i, l in enumerate(npi0)]}
    tag = "+".join(args.row) if args.row else "truth"
    if args.files:
        tag += "-" + "+".join(args.files)
    path = repo_path("space", "perf", f"msf-regimes-{tag}-{args.dataset}.json")
    path.write_text(json.dumps(out, indent=1))
    print(f"{args.dataset}: {n_events} events, {len(lambdas)} generator Λ, modes {dict(modes)}")
    print(f"{'regime':26s} {'n':>5s} {'% nπ0':>6s} {'p med':>6s} {'z med m':>7s}" + "".join(f" | {r[:22]:>22s}" for r in args.row))
    for row in table:
        line = f"{row['regime']:26s} {row['n']:5d} {100 * row['share_of_npi0']:6.1f} {row['lambda_p_median']:6.0f} {row['decay_z_median_m']:7.1f}"
        for r in args.row:
            line += f" | {row[r]['matched']:4d} {100 * row[r]['eff']:5.1f} ± {100 * row[r]['eff_err']:4.1f} %"
        print(line)
    print(f"expected Λ → nπ⁰ {expected:.0f}; per expected Λ → nπ⁰:")
    for gr in groups:
        line = f"  {gr['group']:32s} {gr['n']:5d} {100 * gr['share_of_expected_npi0']:6.1f} %"
        for r in args.row:
            x = gr[r]
            line += f" | {r[:9]} {x['matched']:4d} = {100 * x['per_expected_npi0']:5.2f} % {x['reasons']}"
        print(line)
    for r in args.row:
        x = rows[r]
        print(f"{r}: N_found {x['N_found']} of N_expected {x['N_expected']:.0f}: yield {100 * x['yield']:.2f} ± "
              f"{100 * x['yield_err']:.2f} %; N_window {x['N_window']}: purity "
              + (f"{100 * x['purity']:.1f} ± {100 * x['purity_err']:.1f} %" if x["purity"] is not None else "—"))
    for r in args.row:
        print(r, "photon E_reco / E_true of matched photon neutrals:", ratio[r])
    print("wrote", path)


if __name__ == "__main__":
    main()
