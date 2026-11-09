#!/usr/bin/env python3
"""Which neutron position the Λ chain reads, and what it costs (finding F10).

LambdaReconstruction places the neutron at `n.getClusters(0).getPosition()`. The ZDC neutrals factory
links every ZDC cluster to the neutron (`associateAllClustersToNeutron = true`), so cluster 0 is the
first cluster of the event's collection, not the neutron's leader; the neutron's momentum and
reference point aim at the leader. This script runs 415's tagged inputs (EICrecon's own photon tags,
neutron energy and positions) through the stable-vertex chain twice — neutron at cluster 0 and at the
leader — and counts the Λs in the fixed scoring window, per D4 momentum.

--pairing vertex runs the same comparison under the IDOLA-first pairing (zdc/lambda_chain.py), the model of
PR 3063's chain (R3), where the neutron position also enters the iteration.

Writes space/perf/lambda-neutron-position-<row>.json (vertex_fixed) or ...-<row>-<pairing>.json.
Usage: uv run scripts/416_neutron_position.py R2_pr3114 L01_box3114 R1_pr3064   (rows with ROOT files)
       uv run scripts/416_neutron_position.py --pairing vertex R3_pr3063
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, metrics_config, repo_path  # noqa: E402
from zdc.lambda_chain import M_L, chain, to_proton  # noqa: E402

spec = importlib.util.spec_from_file_location("offline415", repo_path("scripts", "415_lambda_chain_offline.py"))
o415 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(o415)


def main():
    profile, mcfg = load_profile(), metrics_config()
    half = float(mcfg.windows.lambda_mass_half_window_gev)
    purity_min = float(mcfg.truth_match.purity_min)
    ap = argparse.ArgumentParser()
    ap.add_argument("rows", nargs="+")
    ap.add_argument("--pairing", default="vertex_fixed", choices=("vertex_fixed", "vertex"))
    args = ap.parse_args()
    for row in args.rows:
        td = Path(profile.reco_root) / row / "D4_lambda" / "truth"
        result = {"row": row, "pairing": args.pairing, "per_momentum": {}}
        for f in sorted(td.glob("*.edm4eic.npz"), key=o415.momentum_of):
            t = np.load(f)["table"]
            gamma, neutron = o415.tags_for(td.parent / f.name.replace(".npz", ".root"), f.with_suffix(".tags.npz"), mcfg)
            cnt = {"triplets": 0, "cluster0_is_leader": 0, "cluster0": 0, "leader": 0}
            for ev in np.unique(t["event"]):
                rows = {r["role"]: r for r in t[t["event"] == ev]}
                if set(rows) != {"n", "g1", "g2"} or any(rows[k]["n_clusters"] == 0 for k in rows):
                    continue
                cl = [int(rows[k]["cluster"]) for k in ("n", "g1", "g2")]
                g = gamma.get(int(ev), {})
                if len(set(cl)) < 3 or any(rows[k]["purity"] < purity_min for k in rows) or cl[1] not in g or cl[2] not in g or int(ev) not in neutron:
                    continue
                e_n, pos0, _, leader = neutron[int(ev)]
                cnt["triplets"] += 1
                cnt["cluster0_is_leader"] += pos0 == leader
                E = {"g1": g[cl[1]], "g2": g[cl[2]], "n": e_n}
                X = {k: o415.proton_pos(rows[k]) for k in ("g1", "g2")}
                for label, pos in (("cluster0", pos0), ("leader", leader)):
                    X["n"] = np.array(to_proton(*pos))
                    m = chain(E, X, args.pairing)
                    cnt[label] += m is not None and abs(m - M_L) <= half
            result["per_momentum"][str(o415.momentum_of(f))] = {k: int(v) for k, v in cnt.items()}
        tot = {k: sum(v[k] for v in result["per_momentum"].values()) for k in ("triplets", "cluster0_is_leader", "cluster0", "leader")}
        result["all"] = tot
        print(f"{row}: tagged triplets {tot['triplets']} (cluster 0 is the leader in {tot['cluster0_is_leader']}); "
              f"{args.pairing} Λ in window: neutron at cluster 0 {tot['cluster0']}, at its leader {tot['leader']} "
              f"({100 * (tot['leader'] / max(tot['cluster0'], 1) - 1):+.0f} %)")
        suffix = "" if args.pairing == "vertex_fixed" else f"-{args.pairing}"
        path = repo_path("space", "perf", f"lambda-neutron-position-{row}{suffix}.json")
        path.write_text(json.dumps(result, indent=1))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
