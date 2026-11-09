#!/usr/bin/env python3
"""F5 of Phase 4 (zdc-autoresearch-loop-v4.md): the held-out check of a checkpoint.

The current best and the previous checkpoint's best, both reconstructed on D4h (fresh seeds, never read while
tuning), are compared event by event on S4a_tm (410's `<file>.lambda.npz`, flag `matched`): per D4h momentum and
pooled over the momenta, McNemar gained / lost / z, as 417 does on D4. The gain reproduces when the pooled z is
positive and above 2 (loop v4: "in sign at more than 2σ pooled"); otherwise the steps accepted since the previous
checkpoint are reverted (an overfit). Per-thrown values use the gun acceptance of 413 at each momentum.

Writes space/perf/checkpoint-heldout-<best>-vs-<previous>.json and prints the table.

Usage: uv run scripts/462_checkpoint_heldout.py CP1_X5_D4h CP1_R1_D4h
       (rows reconstructed with datasets [D4h_lambda_heldout]; 410 run on them)
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, repo_path  # noqa: E402

PERF = repo_path("space", "perf")
DS = "D4h_lambda_heldout"


def tables(row):
    d = Path(load_profile().reco_root) / row / DS
    out = {}
    for f in sorted(list(d.glob("*.lambda.npz")) + list((d / "truth").glob("*.lambda.npz"))):
        p = int(f.name.split("GeV")[0].split("_")[-1])
        t = np.load(f)["table"]
        out[p] = {int(e): bool(m) for e, m in zip(t["event"], t["matched"])}
    return out


def main():
    best, prev = sys.argv[1], sys.argv[2]
    a, b = tables(best), tables(prev)
    acc = json.loads((PERF / "lambda-gun-acceptance.json").read_text())
    rows, G, Lo = [], 0, 0
    print(f"{best} vs {prev} on {DS} (S4a_tm, truth-matched Λ in the window)")
    print("    p |  tm A  tm B  gain  lost      z | A % thrown  B % thrown")
    for p in sorted(set(a) & set(b)):
        keys = sorted(set(a[p]) & set(b[p]))
        g = sum(1 for k in keys if a[p][k] and not b[p][k])
        lo = sum(1 for k in keys if b[p][k] and not a[p][k])
        z = (g - lo) / math.sqrt(g + lo) if g + lo else 0.0
        ta, tb = sum(a[p][k] for k in keys), sum(b[p][k] for k in keys)
        ac = acc.get(str(p), {}).get("all3_inside_4mrad")
        pa = 100 * ta / len(keys) * ac if ac else None
        pb = 100 * tb / len(keys) * ac if ac else None
        rows.append({"p": p, "events": len(keys), "tm_A": ta, "tm_B": tb, "gained": g, "lost": lo, "z": z,
                     "A_per_thrown_pct": pa, "B_per_thrown_pct": pb, "acceptance": ac})
        G += g; Lo += lo
        print(f"  {p:3d} | {ta:5d} {tb:5d} {g:5d} {lo:5d} {z:+6.2f} | {pa if pa is None else round(pa, 3)!s:>10} {pb if pb is None else round(pb, 3)!s:>10}")
    zp = (G - Lo) / math.sqrt(G + Lo) if G + Lo else 0.0
    reproduces = zp > 2.0
    print(f"pooled: gained {G}, lost {Lo}, z {zp:+.2f} -> {'REPRODUCES' if reproduces else 'DOES NOT REPRODUCE (revert the steps since the previous checkpoint)'}")
    out = {"best": best, "previous": prev, "dataset": DS, "per_momentum": rows,
           "pooled": {"gained": G, "lost": Lo, "z": zp}, "reproduces": reproduces}
    (PERF / f"checkpoint-heldout-{best}-vs-{prev}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
