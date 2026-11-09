#!/usr/bin/env python3
"""The Phase 4 verdict of an experiment (zdc-autoresearch-loop-v4.md, the experiment loop; D-default-42).

Reads the experiment's fair play (`460`: space/perf/fair-play-<row>.json) and its paired test against the current
best (`417`: space/perf/lambda-paired-<row>-vs-<best>.json), and prints the verdict:

  FOUL          460 FAIL (any of F1-F3)
  ACCEPTED      pooled McNemar z ≥ 3 over the D4 momenta and the mean S4a_tm per thrown up
  INCONCLUSIVE  the mean up but z < 3 (kept for a combined retry)
  REJECTED      otherwise

417 still prints its Phase 3 caption "reported only, not a selector" beside the pooled line; in Phase 4 that pooled
line is the selector (D-default-42), and this script is where it is applied. Writes
space/perf/verdict-<row>.json and prints one line in D-user-20's form (275 GeV and mean per thrown, 14.1 % ceiling),
the numbers taken from headline.csv.

Usage: uv run scripts/461_phase4_verdict.py X1_offline_chain R1_pr3064
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import repo_path  # noqa: E402

PERF = repo_path("space", "perf")
Z_ACCEPT = 3.0
CEILING = 14.1


def headline(row):
    with open(PERF / "headline.csv") as fh:
        for r in csv.DictReader(fh):
            if r["row"] == row:
                return r
    return None


def main():
    row, best = sys.argv[1], sys.argv[2]
    fp_path = PERF / f"fair-play-{row}.json"
    pt_path = PERF / f"lambda-paired-{row}-vs-{best}.json"
    fp = json.loads(fp_path.read_text()) if fp_path.exists() else None
    pt = json.loads(pt_path.read_text()) if pt_path.exists() else None
    if fp is None:
        sys.exit(f"no fair play for {row} ({fp_path}): run 460 first")
    if pt is None:
        sys.exit(f"no paired test {pt_path}: run 417 {row} {best} first")
    z = pt["pooled"]["z"]
    mean_a, mean_b = pt["S4a_tm_per_thrown_mean_A"], pt["S4a_tm_per_thrown_mean_B"]
    if fp["verdict"] != "PASS":
        verdict = "FOUL"
    elif z >= Z_ACCEPT and mean_a > mean_b:
        verdict = "ACCEPTED"
    elif mean_a > mean_b:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "REJECTED"
    h = headline(row) or {}
    top, mean = h.get("S4a_tm_per_thrown_275"), h.get("S4a_tm_per_thrown_mean")
    out = {"row": row, "best": best, "verdict": verdict, "fair_play": fp["verdict"], "failed_rules": fp["failed_rules"],
           "pooled": pt["pooled"], "mean_per_thrown_row": mean_a, "mean_per_thrown_best": mean_b,
           "headline_275_pct": top, "headline_mean_pct": mean, "ceiling_pct": CEILING,
           "written": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")}
    (PERF / f"verdict-{row}.json").write_text(json.dumps(out, indent=1))
    print(f"{verdict}: {row} vs {best} — S4a_tm per thrown Λ→nπ⁰ {top} % at 275 GeV, {mean} % mean "
          f"(best {100 * mean_b:.3f} % mean; ceiling {CEILING} %); pooled gained {pt['pooled']['gained']}, "
          f"lost {pt['pooled']['lost']}, z {z:+.2f}; fair play {fp['verdict']}"
          + (f" ({', '.join(fp['failed_rules'])})" if fp["failed_rules"] else ""))


if __name__ == "__main__":
    main()
