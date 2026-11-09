#!/usr/bin/env python3
"""Held-out check (loop rule 8): the paired test of an experiment against a reference on D1h / D4h.

400_scoreboard.py's paired section covers the search datasets (D1_pi0, D4_lambda) only; this script runs the
same McNemar test on the held-out sets from 410_truth_match.py's per-event flags
({space}/perf/truth-<exp>-<dataset>.json, "event_flags"): S0all / S1a_truth_all per event (all target
particles separated), and S0γ, S0n per particle. Significance at 3σ (configs/metrics.yaml).
Writes {space}/perf/heldout-<exp>-vs-<ref>.json and prints the verdict against the criterion pre-registered
in the Phase 2 header of space/EXPERIMENTS.md: on D4h the paired Δ S0all is significant and positive at ≥ 2 of
the 3 momenta and no S0 component falls significantly; on D1h S1a_truth_all falls significantly nowhere.

Usage:
  uv run scripts/405_heldout_check.py P1b_R0_thr R0_stock
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import metrics_config, repo_path  # noqa: E402

PERF = repo_path("space", "perf")


def mcnemar(a, b):
    """a, b: dict key -> bool for the same units. Returns Δ, error, z, gained, lost, n."""
    keys = sorted(set(a) & set(b))
    gained = sum(1 for k in keys if a[k] and not b[k])
    lost = sum(1 for k in keys if b[k] and not a[k])
    n = len(keys)
    d = (gained - lost) / n if n else float("nan")
    err = math.sqrt(gained + lost) / n if n else float("nan")
    z = (gained - lost) / math.sqrt(gained + lost) if gained + lost else 0.0
    return d, err, z, gained, lost, n


def flags(exp, ds):
    return json.loads((PERF / f"truth-{exp}-{ds}.json").read_text())["event_flags"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment")
    ap.add_argument("reference")
    args = ap.parse_args()
    sig = float(metrics_config().get("significance_sigma", 3.0))
    out = {"experiment": args.experiment, "reference": args.reference, "significance_sigma": sig, "cells": []}
    for ds, label in (("D4h_lambda_heldout", "S0"), ("D1h_pi0_heldout", "S1a_truth")):
        fa, fb = flags(args.experiment, ds), flags(args.reference, ds)
        for p in sorted(fa, key=int):
            ev_a = dict(zip(fa[p]["events"], fa[p]["all_separated"]))
            ev_b = dict(zip(fb[p]["events"], fb[p]["all_separated"]))
            cells = [(f"{label}_all", mcnemar(ev_a, ev_b))]
            pa = {(e, r): s for e, r, s in fa[p]["particles"]}
            pb = {(e, r): s for e, r, s in fb[p]["particles"]}
            g = lambda d: {k: v for k, v in d.items() if k[1] in ("g1", "g2")}  # noqa: E731
            nn = lambda d: {k: v for k, v in d.items() if k[1] == "n"}  # noqa: E731
            cells.append((f"{label}_g", mcnemar(g(pa), g(pb))))
            if ds.startswith("D4"):
                cells.append(("S0_n", mcnemar(nn(pa), nn(pb))))
            for name, (d, err, z, gn, ls, n) in cells:
                verdict = "SIGNIFICANT" if abs(z) >= sig else "not significant"
                print(f"  {ds:20s} {int(p):4d} GeV {name:16s} Δ {d:+.4f} ± {err:.4f}  (gained {gn}, lost {ls} of {n})  z {z:+.2f}  {verdict}")
                out["cells"].append({"dataset": ds, "momentum": int(p), "cell": name, "delta": d, "err": err, "z": z,
                                     "gained": gn, "lost": ls, "n": n})
    c = out["cells"]
    d4_all = [x for x in c if x["dataset"].startswith("D4h") and x["cell"] == "S0_all"]
    pos = sum(1 for x in d4_all if x["z"] >= sig)
    falls = [x for x in c if x["dataset"].startswith("D4h") and x["z"] <= -sig]
    d1_falls = [x for x in c if x["dataset"].startswith("D1h") and x["cell"] == "S1a_truth_all" and x["z"] <= -sig]
    ok = pos >= 2 and not falls and not d1_falls
    out["criterion"] = {"D4h_S0all_significant_positive": pos, "D4h_components_falling": len(falls),
                        "D1h_S1a_truth_all_falling": len(d1_falls), "reproduces": ok}
    print(f"held-out criterion: S0all significant and positive at {pos} of {len(d4_all)} D4h momenta; "
          f"{len(falls)} D4h component(s) fall; {len(d1_falls)} D1h fall → {'REPRODUCES' if ok else 'DOES NOT REPRODUCE (revert)'}")
    path = PERF / f"heldout-{args.experiment}-vs-{args.reference}.json"
    path.write_text(json.dumps(out, indent=1))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
