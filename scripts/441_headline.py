#!/usr/bin/env python3
"""The headline side table: per-thrown Λ → nπ⁰ numbers for every reconstruction row.

Every brief report line and every deck number comes from this file (D-user-20,
loop v3: a number computed in chat is not a result). For each row with a D4
truth-match file it writes, per D4 momentum p:

  S0all_per_thrown[p]  = S0_all_sep[p]  × acceptance[p]
  S4a_tm_per_thrown[p] = S4a_tm_eff[p]  × acceptance[p]
  S4o_<pairing>_<variant>_per_thrown[p] = the offline Λ chain of 415 (when its
                                          file exists) × acceptance[p]

with acceptance[p] = all3_inside_4mrad of space/perf/lambda-gun-acceptance.json
(413: the fraction of thrown Λ → nπ⁰ whose three daughters reach the ZDC face,
the generator's cut that defines the D4 events). Each column also gets its mean
over the D4 momenta and its value at the highest momentum.

Writes space/perf/headline.csv (one row per reconstruction, every column in per
cent; rows given on the command line replace their lines, the others stay) and
prints the table in markdown.

Usage: uv run scripts/441_headline.py [row ...]      (default: every row with a truth file)
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import repo_path  # noqa: E402

PERF = repo_path("space", "perf")


def load(path):
    with open(path) as fh:
        return json.load(fh)


def per_thrown(values, acc):
    """values, acc: dict momentum -> fraction; returns per-momentum per-thrown, mean, and the top momentum's value."""
    moms = sorted(acc, key=int)
    pt = {p: values[p] * acc[p] for p in moms if p in values}
    mean = sum(pt.values()) / len(pt) if pt else float("nan")
    top = pt[moms[-1]] if moms and moms[-1] in pt else float("nan")
    return pt, mean, top


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rows", nargs="*")
    args = ap.parse_args()
    acc = {p: v["all3_inside_4mrad"] for p, v in load(PERF / "lambda-gun-acceptance.json").items()}
    moms = sorted(acc, key=int)
    rows = args.rows or sorted(f.name[len("truth-"):-len("-D4_lambda.json")] for f in PERF.glob("truth-*-D4_lambda.json")
                               if "heldout" not in f.name and "noise" not in f.name)
    columns = ["S0all", "S4a_tm"]
    table = []
    for row in rows:
        truth = load(PERF / f"truth-{row}-D4_lambda.json")["per_momentum"]
        s0 = {p: truth[p]["S0_all_sep"] for p in truth}
        s4 = {p: truth[p]["S4a_tm_eff"] for p in truth}
        rec = {"row": row}
        for name, vals in (("S0all", s0), ("S4a_tm", s4)):
            pt, mean, top = per_thrown(vals, acc)
            rec.update({f"{name}_per_thrown_{p}": pt.get(p, float("nan")) for p in moms})
            rec[f"{name}_per_thrown_mean"] = mean
            rec[f"{name}_per_thrown_top"] = top
        off = PERF / f"lambda-offline-{row}.json"
        if off.exists():  # 415's output: per_momentum[p][<pairing>_<variant>] per accepted event
            pm = load(off)["per_momentum"]
            for key in sorted({k for v in pm.values() for k in v if not k.endswith(("_n", "_sigma"))}):
                name = f"S4o_{key}"
                if name not in columns:
                    columns.append(name)
                pt, mean, top = per_thrown({p: pm[p][key] for p in pm if key in pm[p]}, acc)
                rec.update({f"{name}_per_thrown_{p}": pt.get(p, float("nan")) for p in moms})
                rec[f"{name}_per_thrown_mean"] = mean
                rec[f"{name}_per_thrown_top"] = top
        table.append(rec)
    out = PERF / "headline.csv"
    existing = {}
    if out.exists() and args.rows:  # a subset call updates its rows only; the other rows stay as written
        with open(out, newline="") as fh:
            existing = {r["row"]: r for r in csv.DictReader(fh)}
            for c in {k.rsplit("_per_thrown_", 1)[0] for r in existing.values() for k in r if "_per_thrown_" in k}:
                if c not in columns:
                    columns.append(c)
    fields = ["row"] + [f"{c}_per_thrown_{s}" for c in columns for s in moms + ["mean", "top"]]
    new_rows = {rec["row"]: {k: (f"{100 * rec[k]:.3f}" if k != "row" and k in rec else rec.get(k, "")) for k in fields} for rec in table}
    existing.update(new_rows)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in sorted(existing):
            w.writerow({k: existing[row].get(k, "") for k in fields})
    acc_mean = sum(acc.values()) / len(acc)
    print(f"| row | " + " | ".join(f"{c} mean / {moms[-1]} GeV (% per thrown)" for c in columns) + " |")
    print("|---|" + "---|" * len(columns))
    print(f"| acceptance (ceiling of S0all) | {100 * acc_mean:.2f} / {100 * acc[moms[-1]]:.2f} |" + " |" * (len(columns) - 1))
    for rec in table:
        cells = []
        for c in columns:
            m, t = rec.get(f"{c}_per_thrown_mean"), rec.get(f"{c}_per_thrown_top")
            cells.append("—" if m is None or m != m else f"{100 * m:.2f} / {100 * t:.2f}")
        print(f"| {rec['row']} | " + " | ".join(cells) + " |")
    print(f"written {out} ({len(table)} rows, {len(columns)} quantities)")


if __name__ == "__main__":
    main()
