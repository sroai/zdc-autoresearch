#!/usr/bin/env python3
"""The gate table: what G4 compared for every experiment, as numbers a reader can see.

300_run_experiment.py runs scripts/130_compare_collections.py on every DIS output
of an experiment against the reference (the config's reference_reco, else
R0_stock) and logs one line per file:
  PASS: <N> non-ZDC leaves identical over <M> events
  FAIL: <first differing leaf> ...
This script reads {data}/logs/experiments/<row>.log for every row, counts the
PASS and FAIL lines (the compares), the leaves, the events, and writes
space/perf/gate-evidence.json (rows given on the command line replace their
entries; the other rows stay) plus a markdown table of the rows given on stdout. D5 is DIS (every
detector fills), so "every non-ZDC leaf identical on every D5 chunk" is the
proof that no other calorimeter, the tracking or the PID moved (D-user-22).

Usage: uv run scripts/442_gate_evidence.py [row ...]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, load_yaml, repo_path  # noqa: E402

PASS = re.compile(r"^PASS: (\d+) non-ZDC leaves identical over (\d+) events")
FAIL = re.compile(r"^FAIL: (.*)$")


def reference_of(row):
    cfg = repo_path("configs", "experiments", f"{row}.yaml")
    if cfg.exists():
        exp = load_yaml(cfg)
        return exp.get("reference_reco", "R0_stock"), [d for d in exp.get("datasets", []) if d.startswith("D5")]
    return "R0_stock", []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rows", nargs="*")
    args = ap.parse_args()
    logdir = Path(load_profile().logs_root) / "experiments"
    rows = args.rows or sorted(p.stem for p in logdir.glob("*.log"))
    out = {}
    for row in rows:
        log = logdir / f"{row}.log"
        if not log.exists():
            out[row] = {"log": str(log), "compares": 0, "note": "no log"}
            continue
        passes = fails = 0
        leaves = set()
        events = 0
        first_fail = None
        reference, datasets = reference_of(row)
        for line in log.read_text(errors="replace").splitlines():
            m = PASS.match(line)
            if m:
                passes += 1
                leaves.add(int(m.group(1)))
                events += int(m.group(2))
                continue
            m = FAIL.match(line)
            if m:
                fails += 1
                first_fail = first_fail or m.group(1)
        compares = passes + fails
        out[row] = {"log": str(log), "reference": reference, "datasets": datasets, "compares": compares,
                    "pass": passes, "fail": fails, "leaves_per_file": sorted(leaves), "events": events,
                    "first_fail": first_fail, "verdict": "PASS" if compares and fails == 0 and passes == compares else ("FAIL" if fails else "INCOMPLETE")}
    dest = repo_path("space", "perf", "gate-evidence.json")
    merged = json.loads(dest.read_text()) if dest.exists() else {}   # a subset call updates its rows only
    merged.update(out)
    dest.write_text(json.dumps(dict(sorted(merged.items())), indent=1))
    print("| row | reference | D5 files compared | non-ZDC leaves per file | events | G4 |")
    print("|---|---|---|---|---|---|")
    for row, r in out.items():
        if r["compares"] == 0:
            print(f"| {row} | — | 0 | — | — | {r.get('note', 'no compare')} |")
            continue
        lv = "/".join(str(x) for x in r["leaves_per_file"]) or "—"
        v = r["verdict"] + (f" ({r['first_fail']})" if r["first_fail"] else "")
        print(f"| {row} | {r['reference']} | {r['pass']}/{r['compares']} | {lv} | {r['events']} | {v} |")
    print(f"written {dest}")


if __name__ == "__main__":
    main()
