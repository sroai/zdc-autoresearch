#!/usr/bin/env python3
"""Where the Λ → nπ⁰ events of a row are lost, per D4 momentum (Phase 4 diagnostic; never a selector).

Every D4 event falls in the first category that applies, in this order:
  matched      the in-EICrecon Λ is truth-matched in the scoring window (S4a_tm, 410's .lambda.npz)
  clustering   a daughter's best-matched cluster has purity < purity_min, or two daughters share one
               (the "truth-identified" precondition of 415 fails)
  photon_tag   a true photon's best cluster carries no PDG 22 neutral in ReconstructedHcalFarForwardZDCNeutrals
  no_lambda    both photons tagged, but no Λ written
  pairing      a Λ written with other photon clusters than the true photons' best ones
  window       the Λ uses the true photons' clusters, but its mass is outside the window (or it is not matched)
The tags and the Λ's photon clusters are read from the row's ROOT (ReconstructedLambdas → daughters →
clusters); the truth roles and best clusters from 410's per-particle table (<file>.npz).

Writes space/perf/lambda-losses-<row>.json and prints the table (fractions of D4 events per momentum).

Usage: uv run scripts/470_lambda_losses.py X1_offline_chain [--reco-dir DIR]
"""
import argparse
import json
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, metrics_config, repo_path  # noqa: E402
from zdc.edm import collection_ids  # noqa: E402

CATS = ("matched", "clustering", "photon_tag", "no_lambda", "pairing", "window")
NEU = "ReconstructedHcalFarForwardZDCNeutrals"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("row")
    ap.add_argument("--reco-dir")
    args = ap.parse_args()
    profile = load_profile()
    pmin = float(metrics_config().truth_match.purity_min)
    reco = Path(args.reco_dir) if args.reco_dir else Path(profile.reco_root) / args.row / "D4_lambda"
    out = {"row": args.row, "per_momentum": {}}
    print(f"{args.row}: fraction of D4 events per category")
    print("   p | " + " ".join(f"{c:>10s}" for c in CATS) + " |  events")
    for root in sorted(reco.glob("D4_lambda_*GeV_seed1.edm4eic.root")):
        p = root.name.split("_")[2].replace("GeV", "")
        base = next((d for d in (reco, reco / "truth") if (d / f"{root.name[:-5]}.npz").exists()), None)
        if base is None:
            print(f"{p}: no 410 tables beside {root.name}")
            continue
        parts = np.load(base / f"{root.name[:-5]}.npz")["table"]
        lam = np.load(base / f"{root.name[:-5]}.lambda.npz")["table"]
        matched = {int(e): bool(m) for e, m in zip(lam["event"], lam["matched"])}
        ids = collection_ids(root)
        t = uproot.open(root)["events"]
        a = t.arrays([f"{NEU}.PDG", f"{NEU}.clusters_begin", f"{NEU}.clusters_end", f"_{NEU}_clusters.index",
                      "ReconstructedLambdas.particles_begin", "ReconstructedLambdas.particles_end",
                      "_ReconstructedLambdas_particles.index", "_ReconstructedLambdas_particles.collectionID"], library="ak")
        pdg = ak.to_list(a[f"{NEU}.PDG"]); cb = ak.to_list(a[f"{NEU}.clusters_begin"]); ce = ak.to_list(a[f"{NEU}.clusters_end"])
        ci = ak.to_list(a[f"_{NEU}_clusters.index"])
        lb = ak.to_list(a["ReconstructedLambdas.particles_begin"]); le = ak.to_list(a["ReconstructedLambdas.particles_end"])
        li = ak.to_list(a["_ReconstructedLambdas_particles.index"]); lc = ak.to_list(a["_ReconstructedLambdas_particles.collectionID"])
        zid = ids.get(NEU)
        counts = {c: 0 for c in CATS}
        events = sorted(set(int(e) for e in parts["event"]))
        for ev in events:
            rows = parts[parts["event"] == ev]
            role = {str(r["role"]): r for r in rows}
            if matched.get(ev):
                counts["matched"] += 1; continue
            best = [int(role[k]["cluster"]) if k in role else -1 for k in ("n", "g1", "g2")]
            pur = [float(role[k]["purity"]) if k in role else 0.0 for k in ("n", "g1", "g2")]
            if min(pur) < pmin or -1 in best or len(set(best)) < 3:
                counts["clustering"] += 1; continue
            # photon tags: the first linked cluster of each PDG 22 neutral is its own (makeGamma)
            gam_cl = {ci[ev][cb[ev][k]] for k in range(len(pdg[ev])) if pdg[ev][k] == 22 and ce[ev][k] > cb[ev][k]}
            if best[1] not in gam_cl or best[2] not in gam_cl:
                counts["photon_tag"] += 1; continue
            if not lb[ev]:
                counts["no_lambda"] += 1; continue
            used = set()
            for j in range(lb[ev][0], le[ev][0]):
                if lc[ev][j] == zid and pdg[ev][li[ev][j]] == 22:
                    k = li[ev][j]
                    used.add(ci[ev][cb[ev][k]])
            counts["pairing" if used != {best[1], best[2]} else "window"] += 1
        n = len(events)
        out["per_momentum"][p] = {"events": n, **{c: counts[c] / n for c in CATS}, "counts": counts}
        print(f"{p:>4s} | " + " ".join(f"{counts[c] / n:10.3f}" for c in CATS) + f" | {n:6d}")
    path = repo_path("space", "perf", f"lambda-losses-{args.row}.json")
    path.write_text(json.dumps(out, indent=1))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
