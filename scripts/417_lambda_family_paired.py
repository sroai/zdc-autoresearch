#!/usr/bin/env python3
"""Paired tests of a Λ-family row against a reference on the same D4 events (selector rule 1).

From 410's per-event Λ tables (`<file>.lambda.npz`: any = a Λ in the scoring window, matched = a
truth-matched one), per D4 momentum:

  S4a_tm        the selector: events gained / lost (matched), McNemar z, and per thrown Λ → nπ⁰
  untruthful    the guard: events with a Λ in the window that is not truth-matched (any ∧ ¬matched),
                gained / lost and z — "not up significantly" (D-default-25, D-default-37)

Significance is the limit of configs/metrics.yaml (default 3σ). Writes
space/perf/lambda-paired-<row>-vs-<reference>.json and prints the table.

Usage: uv run scripts/417_lambda_family_paired.py B9d_stable_vertex R2_pr3114
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, repo_path  # noqa: E402

PERF = repo_path("space", "perf")


def momentum_of(path):
    return int(path.name.split("GeV")[0].split("_")[-1])


def flags(path):
    t = np.load(path)["table"]
    return {int(e): (bool(a), bool(m)) for e, a, m in zip(t["event"], t["any"], t["matched"])}


def mcnemar(x, y):
    g, l = int((x & ~y).sum()), int((~x & y).sum())
    return g, l, ((g - l) / np.sqrt(g + l) if g + l else 0.0)


def main():
    row, ref = sys.argv[1], sys.argv[2]
    profile = load_profile()
    acc = {p: v["all3_inside_4mrad"] for p, v in json.loads((PERF / "lambda-gun-acceptance.json").read_text()).items()}
    da = Path(profile.reco_root) / row / "D4_lambda" / "truth"
    db = Path(profile.reco_root) / ref / "D4_lambda" / "truth"
    out = {"row": row, "reference": ref, "per_momentum": {}}
    print(f"{row} vs {ref}, D4 events per momentum")
    print(f"{'p':>4s} | {'tm A':>5s} {'tm B':>5s} {'gain':>5s} {'lost':>5s} {'z':>6s} | {'untr A':>6s} {'untr B':>6s} {'gain':>5s} {'lost':>5s} {'z':>6s} | {'A % thrown':>10s}")
    sums = []
    for fa in sorted(da.glob("*.lambda.npz"), key=momentum_of):
        fb = db / fa.name
        if not fb.exists():
            continue
        p = momentum_of(fa)
        a, b = flags(fa), flags(fb)
        events = sorted(set(a) & set(b))
        tm_a = np.array([a[e][1] for e in events]); tm_b = np.array([b[e][1] for e in events])
        un_a = np.array([a[e][0] and not a[e][1] for e in events]); un_b = np.array([b[e][0] and not b[e][1] for e in events])
        g, l, z = mcnemar(tm_a, tm_b)
        ug, ul, uz = mcnemar(un_a, un_b)
        per_thrown = tm_a.mean() * acc[str(p)]
        sums.append((per_thrown, tm_b.mean() * acc[str(p)]))
        out["per_momentum"][str(p)] = {"events": len(events), "S4a_tm_A": int(tm_a.sum()), "S4a_tm_B": int(tm_b.sum()),
                                       "gained": g, "lost": l, "z": z, "untruthful_A": int(un_a.sum()), "untruthful_B": int(un_b.sum()),
                                       "untruthful_gained": ug, "untruthful_lost": ul, "untruthful_z": uz,
                                       "S4a_tm_per_thrown_A": per_thrown, "S4a_tm_per_thrown_B": tm_b.mean() * acc[str(p)]}
        print(f"{p:4d} | {int(tm_a.sum()):5d} {int(tm_b.sum()):5d} {g:5d} {l:5d} {z:6.2f} | {int(un_a.sum()):6d} {int(un_b.sum()):6d} {ug:5d} {ul:5d} {uz:6.2f} | {100 * per_thrown:10.3f}")
    out["S4a_tm_per_thrown_mean_A"] = float(np.mean([s[0] for s in sums]))
    out["S4a_tm_per_thrown_mean_B"] = float(np.mean([s[1] for s in sums]))
    print(f"S4a_tm per thrown, mean over momenta: {row} {100 * out['S4a_tm_per_thrown_mean_A']:.3f} %, {ref} {100 * out['S4a_tm_per_thrown_mean_B']:.3f} %")
    # pooled McNemar over the momenta: reported beside the per-momentum selector, never used to select (Q18)
    pg = sum(v["gained"] for v in out["per_momentum"].values())
    pl = sum(v["lost"] for v in out["per_momentum"].values())
    pz = (pg - pl) / np.sqrt(pg + pl) if pg + pl else 0.0
    out["pooled"] = {"gained": pg, "lost": pl, "z": float(pz)}
    print(f"pooled over momenta (reported only, not a selector): gained {pg}, lost {pl}, z {pz:+.2f}")
    path = PERF / f"lambda-paired-{row}-vs-{ref}.json"
    path.write_text(json.dumps(out, indent=1))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
