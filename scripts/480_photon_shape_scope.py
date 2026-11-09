#!/usr/bin/env python3
"""Which features tell a tagged Hcal photon cluster from a neutron fragment? (Phase 6, loop v6; a diagnostic for the
shower-shape chooser term, never a selector.)

EICrecon tags an Hcal ZDC cluster as a photon when it passes the shape box (length / width / depth). In the all-ZDC
regime the chooser then picks two tagged clusters; 477 --why found the second photon wrong for 227 missed Λ at 9x275
(Z5). This script measures, per tagged cluster of the row's MSF output, features that a photon-likeness term could use,
and how well each one separates the clusters that are pure (≥ 0.8) for a photon of the target Λ from the others, over
all clusters (AUC) and within one event (the pairs the chooser has to order).

Features (proton frame; z_ZDC the Hcal front used by 473):
  e_front30 / e_front60   crystal rec-hit energy within 30 / 60 mm of the cluster's projective line (GeV)
  front_frac              e_front60 / the cluster's photon-law energy (ag · E^bg)
  depth                   cluster z − z_ZDC (mm)
  l1, l2, l3              the cluster's shape parameters 4, 5, 6 (sqrt; the tag reads them)
  log_e                   log of the cluster energy
  d_lead                  distance to the most energetic Hcal cluster of the event (mm; 0 for that cluster)
  e_rel_lead              cluster energy / the most energetic cluster's energy

With --guns, the same features on gun clusters: every tagged cluster of the photon guns (CAL6_D2_Y9: D2c, D2 ≤ 50 GeV)
against every tagged cluster that is not the leading one in the neutron gun (the row given by --neutron-row, D3). These
are the samples a photon-likeness term may be fitted on (F4).

Usage:
  uv run scripts/480_photon_shape_scope.py Z6_alt_column_out --dataset D6s_9x275 [--files 40]
  uv run scripts/480_photon_shape_scope.py --guns --photon-row CAL6_D2_Y9 --neutron-row CAL6_D3_Z6
"""
import argparse
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import repo_path  # noqa: E402

spec = importlib.util.spec_from_file_location("s477", repo_path("scripts", "477_crystal_scope.py"))
s477 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s477)
e473, r210, STOCK, Z_ZDC, Z_CRYS = s477.e473, s477.r210, s477.STOCK, s477.Z_ZDC, s477.Z_CRYS
C, A, EH, HH = s477.C, s477.A, s477.EH, s477.HH
np_ = s477.np_

FEATURES = ["e_front30", "e_front60", "front_frac", "depth", "l1", "l2", "l3", "log_e", "d_lead", "e_rel_lead"]


def cluster_features(R, ev):
    """Tagged clusters of one event and their features: (cand, {c: {feature: value}})."""
    E = np_(R, f"{C}.energy", ev).astype(float)
    if not len(E):
        return [], {}
    P = e473.to_proton(*(np_(R, f"{C}.position.{q}", ev).astype(float) for q in "xyz"))
    sb, sp = np_(R, f"{C}.shapeParameters_begin", ev), np_(R, f"_{C}_shapeParameters", ev)
    cand = s477.tagged_candidates(E, P, sb, sp)
    ce = np_(R, f"{EH}.energy", ev).astype(float)
    cp = e473.to_proton(*(np_(R, f"{EH}.position.{q}", ev).astype(float) for q in "xyz")) if len(ce) else np.zeros((0, 3))
    lead = int(np.argmax(E))
    feats = {}
    for c in cand:
        px, py = P[c][0] * Z_CRYS / P[c][2], P[c][1] * Z_CRYS / P[c][2]
        d = np.hypot(cp[:, 0] - px, cp[:, 1] - py) if len(ce) else np.zeros(0)
        e60 = float(ce[d <= 60.0].sum()) if len(ce) else 0.0
        eg = STOCK["ag"] * E[c] ** STOCK["bg"]
        feats[c] = {"e_front30": float(ce[d <= 30.0].sum()) if len(ce) else 0.0, "e_front60": e60, "front_frac": e60 / eg,
                    "depth": float(P[c][2] - Z_ZDC),
                    "l1": math.sqrt(max(sp[sb[c] + 4], 0)), "l2": math.sqrt(max(sp[sb[c] + 5], 0)), "l3": math.sqrt(max(sp[sb[c] + 6], 0)),
                    "log_e": math.log(E[c]), "d_lead": float(np.hypot(P[c][0] - P[lead][0], P[c][1] - P[lead][1])),
                    "e_rel_lead": float(E[c] / E[lead])}
    return cand, feats


def auc(pos, neg):
    """P(a positive value > a negative value) + ½ P(equal)."""
    pos, neg = np.asarray(pos), np.asarray(neg)
    if not len(pos) or not len(neg):
        return float("nan")
    allv = np.concatenate([pos, neg])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv) + 1)
    # average ranks over ties
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=ranks)
    ranks = (sums / cnt)[inv]
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def msf(args):
    J = json.loads(repo_path("space", "perf", f"msf-regimes-{args.row}-{args.dataset}.json").read_text())
    per = {(l["file"], l["event"]): l for l in J["per_lambda"] if l["homes"] == ["ZDC", "ZDC", "ZDC"]}
    vals = {"photon": defaultdict(list), "neutron": defaultdict(list), "other": defaultdict(list)}
    within = {f: [0.0, 0] for f in FEATURES}     # Σ within-event AUC contributions, number of (photon, non-photon) pairs
    cnt = Counter()
    for fname in sorted({k[0] for k in per})[: args.files]:
        sim = uproot.open(f"/data/zdc-autoresearch/datasets/{args.dataset}/{fname}")["events"]
        a = r210.mc_arrays(sim)
        R = uproot.open(f"/data/zdc-autoresearch/reco/{args.row}/{args.dataset}/{fname.replace('.edm4hep', '.edm4eic')}")["events"].arrays(
            s477.reco_branches(), library="ak")
        for ev in range(len(R)):
            l = per.get((fname, ev))
            if l is None:
                continue
            _, owner = r210.truth_event(a, ev); base = l["owner_base"]
            cand, feats = cluster_features(R, ev)
            w = np_(R, f"{A}.weight", ev); rc = np_(R, f"_{A}_rec.index", ev); si = np_(R, f"_{A}_sim.index", ev).astype(int)
            own = owner[si] if len(si) else np.array([], dtype=int)
            lab = {}
            for c in cand:
                if any(w[(rc == c) & (own == base + r)].sum() >= 0.8 for r in (1, 2)):
                    lab[c] = "photon"
                elif w[(rc == c) & (own == base)].sum() >= 0.5:
                    lab[c] = "neutron"
                else:
                    lab[c] = "other"
                cnt[lab[c]] += 1
                for f in FEATURES:
                    vals[lab[c]][f].append(feats[c][f])
            ph = [c for c in cand if lab[c] == "photon"]; no = [c for c in cand if lab[c] != "photon"]
            if ph and no:
                cnt["events with photon and non-photon candidates"] += 1
                cnt[f"found by the row: {bool(l[args.row]['matched'])}"] += 1
                for f in FEATURES:
                    for p in ph:
                        for q in no:
                            within[f][0] += 1.0 if feats[p][f] > feats[q][f] else (0.5 if feats[p][f] == feats[q][f] else 0.0)
                            within[f][1] += 1
    out = {"row": args.row, "dataset": args.dataset, "counts": dict(cnt), "features": {}}
    print(f"tagged clusters: {dict(cnt)}")
    print(f"  {'feature':12s} {'AUC γ vs rest':>14s} {'AUC γ vs n':>11s} {'within-event':>13s}   medians γ / n / other")
    for f in FEATURES:
        rest = vals["neutron"][f] + vals["other"][f]
        a1, a2 = auc(vals["photon"][f], rest), auc(vals["photon"][f], vals["neutron"][f])
        we = within[f][0] / within[f][1] if within[f][1] else float("nan")
        med = [float(np.median(vals[k][f])) if vals[k][f] else float("nan") for k in ("photon", "neutron", "other")]
        out["features"][f] = {"auc_photon_vs_rest": a1, "auc_photon_vs_neutron": a2, "within_event": we, "medians": med}
        print(f"  {f:12s} {a1:14.3f} {a2:11.3f} {we:13.3f}   {med[0]:.3g} / {med[1]:.3g} / {med[2]:.3g}")
    path = repo_path("space", "perf", f"photon-shape-{args.row}-{args.dataset}.json")
    path.write_text(json.dumps(out, indent=1))
    print("wrote", path)


def guns(args):
    """Tagged clusters of the photon guns against the non-leading tagged clusters of the neutron gun."""
    vals = {"photon": defaultdict(list), "fragment": defaultdict(list)}
    cnt = Counter()
    for row, ds_list, kind in ((args.photon_row, ["D2c_photon_low", "D2_photon"], "photon"), (args.neutron_row, ["D3_neutron"], "fragment")):
        for ds in ds_list:
            for path in sorted(Path(f"/data/zdc-autoresearch/reco/{row}/{ds}").glob("*.edm4eic.root")):
                gev = float(path.name.split("_")[-2].replace("GeV", ""))
                if kind == "photon" and gev > args.fit_max_gev:
                    continue
                R = uproot.open(path)["events"].arrays(s477.reco_branches(), library="ak")
                for ev in range(len(R)):
                    cand, feats = cluster_features(R, ev)
                    if not cand:
                        continue
                    E = np_(R, f"{C}.energy", ev)
                    lead = int(np.argmax(E))
                    for c in cand:
                        if kind == "fragment" and c == lead:
                            continue
                        if kind == "photon" and c != lead:     # a photon gun's sub-leading tagged clusters are its own fragments
                            continue
                        cnt[f"{kind} {gev:g} GeV"] += 1
                        for f in FEATURES:
                            vals[kind][f].append(feats[c][f])
    out = {"photon_row": args.photon_row, "neutron_row": args.neutron_row, "counts": dict(cnt), "features": {}}
    print(dict(cnt))
    for f in FEATURES:
        a1 = auc(vals["photon"][f], vals["fragment"][f])
        med = [float(np.median(vals[k][f])) if vals[k][f] else float("nan") for k in ("photon", "fragment")]
        out["features"][f] = {"auc_photon_vs_fragment": a1, "medians": med}
        print(f"  {f:12s} AUC {a1:.3f}   medians γ / fragment {med[0]:.3g} / {med[1]:.3g}")
    np.savez_compressed(repo_path("space", "perf", f"photon-shape-guns-{args.neutron_row}.npz"),
                        **{f"{k}_{f}": np.asarray(vals[k][f]) for k in vals for f in FEATURES})
    path = repo_path("space", "perf", f"photon-shape-guns-{args.neutron_row}.json")
    path.write_text(json.dumps(out, indent=1))
    print("wrote", path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("row", nargs="?")
    ap.add_argument("--dataset", default="D6s_9x275")
    ap.add_argument("--files", type=int, default=40)
    ap.add_argument("--guns", action="store_true")
    ap.add_argument("--photon-row", default="CAL6_D2_Y9")
    ap.add_argument("--neutron-row", default="CAL6_D3_Z6")
    ap.add_argument("--fit-max-gev", type=float, default=50.0)
    args = ap.parse_args()
    guns(args) if args.guns else msf(args)


if __name__ == "__main__":
    main()
