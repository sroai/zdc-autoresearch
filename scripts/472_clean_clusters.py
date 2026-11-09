#!/usr/bin/env python3
"""Clustering yardstick for Phase 4 scans (diagnostic, never a selector): per row and D4 momentum, the share of events
whose three daughters each own a pure best cluster (purity ≥ purity_min) distinct from the others — the precondition
of a truth-matched Λ — split by what fails, and the in-EICrecon S4a_tm count (410's .lambda.npz).

Reads only 410's tables, so any row with them (full or partial D4) works.
Writes space/perf/clean-clusters.json (rows replace their entries) and prints the table.

Usage: uv run scripts/472_clean_clusters.py X3_pairing_weights SCAN_W5 SCAN_W10 ...
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, metrics_config, repo_path  # noqa: E402


def classify(parts, pmin):
    out = {"clean": 0, "photon_impure": 0, "photon_in_neutron": 0, "photons_merged": 0, "neutron_impure": 0,
           "no_cluster": 0, "events": 0}
    for ev in np.unique(parts["event"]):
        r = {str(x["role"]): x for x in parts[parts["event"] == ev]}
        out["events"] += 1
        if any(k not in r or int(r[k]["cluster"]) < 0 for k in ("n", "g1", "g2")):
            out["no_cluster"] += 1
            continue
        cl = [int(r[k]["cluster"]) for k in ("n", "g1", "g2")]
        pu = [float(r[k]["purity"]) for k in ("n", "g1", "g2")]
        if cl[1] == cl[2]:
            out["photons_merged"] += 1
        elif cl[0] in cl[1:]:
            out["photon_in_neutron"] += 1
        elif min(pu[1], pu[2]) < pmin:
            out["photon_impure"] += 1
        elif pu[0] < pmin:
            out["neutron_impure"] += 1
        else:
            out["clean"] += 1
    return out


def main():
    profile = load_profile()
    pmin = float(metrics_config().truth_match.purity_min)
    path = repo_path("space", "perf", "clean-clusters.json")
    store = json.loads(path.read_text()) if path.exists() else {}
    print(f"{'row':22s}    p | clean  ph_imp ph_in_n ph_merg  n_imp no_cl | S4a_tm  events")
    for row in sys.argv[1:]:
        reco = Path(profile.reco_root) / row / "D4_lambda"
        store[row] = {}
        for npz in sorted(list(reco.glob("*.edm4eic.npz")) + list((reco / "truth").glob("*.edm4eic.npz"))):
            if npz.name.endswith((".lambda.npz", ".offline.npz", ".tags.npz")):
                continue
            p = npz.name.split("_")[2].replace("GeV", "")
            c = classify(np.load(npz)["table"], pmin)
            lam = npz.with_name(npz.name.replace(".npz", ".lambda.npz"))
            c["S4a_tm"] = int(np.load(lam)["table"]["matched"].sum()) if lam.exists() else None
            store[row][p] = c
            n = c["events"]
            print(f"{row:22s} {p:>4s} | {c['clean'] / n:.3f}  {c['photon_impure'] / n:.3f}   {c['photon_in_neutron'] / n:.3f}   "
                  f"{c['photons_merged'] / n:.3f}  {c['neutron_impure'] / n:.3f} {c['no_cluster'] / n:.3f} | {c['S4a_tm']!s:>6}  {n:6d}")
    path.write_text(json.dumps(store, indent=1))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
