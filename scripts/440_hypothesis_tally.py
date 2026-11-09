#!/usr/bin/env python3
"""The hypothesis tally: how many pre-registered predictions came true, per experiment and in total.

Every ledger entry of space/EXPERIMENTS.md (a `## <name> <YYYY-MM-DD>: <title>` section) is read for
its scored predictions, in either form:

  Phases 1–2   a free-text `Hypothesis check:` paragraph (up to the `guards:` line) with ✓ / ✗ marks
               after each predicted cell, as the agent judged them;
  Phase 3 on   the `hypothesis:` table (cell | momenta | direction | size | mechanism | ✓/✗), whose
               last column is filled after the verdict, and the line `tally: <✓>/<✗>` that 300's
               ledger stub carries. The table is counted when present; the tally line is checked against it.

The phase of an entry is taken from the `## Phase <N>` heading above it. The script prints the table and,
with --write <report>, replaces the block between `<!-- tally:begin -->` and `<!-- tally:end -->` in that
phase report (the section "Hypothesis tally").

Usage:
  uv run scripts/440_hypothesis_tally.py                       # every entry, cumulative
  uv run scripts/440_hypothesis_tally.py --phase 3 --write space/reports/phase3_lambda_chain.md
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import repo_path  # noqa: E402

LEDGER = repo_path("space", "EXPERIMENTS.md")
ENTRY = re.compile(r"^## (\S+) (\d{4}-\d{2}-\d{2}): (.*)$", re.M)
PHASE = re.compile(r"^## Phase (\d+)\b", re.M)


def entries(text):
    """(phase, name, date, title, body) for every ledger entry, in file order."""
    marks = sorted([(m.start(), "phase", m) for m in PHASE.finditer(text)] + [(m.start(), "entry", m) for m in ENTRY.finditer(text)])
    heads = [m.start() for m in re.finditer(r"^## ", text, re.M)] + [len(text)]
    phase, out = None, []
    for pos, kind, m in marks:
        if kind == "phase":
            phase = int(m.group(1))
            continue
        end = next(h for h in heads if h > pos)
        out.append((phase, m.group(1), m.group(2), m.group(3), text[m.end():end]))
    return out


def score(body):
    """(✓, ✗, source) of one entry; source names which form was counted."""
    table = re.search(r"^hypothesis:\s*\n((?:\|.*\|\s*\n)+)", body, re.M)
    if table:
        rows = [r for r in table.group(1).splitlines() if r.strip().startswith("|") and not set(r) <= set("|-: ")][1:]
        marks = [r.rstrip(" |").rsplit("|", 1)[-1] for r in rows]
        return sum("✓" in c for c in marks), sum("✗" in c for c in marks), "table"
    check = re.search(r"Hypothesis check:(.*?)(?:^guards:|\Z)", body, re.S | re.M)
    if check:
        return check.group(1).count("✓"), check.group(1).count("✗"), "check"
    return None, None, "none"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", type=int, help="also print the subtotal of this phase")
    ap.add_argument("--write", help="phase report whose tally block is replaced")
    args = ap.parse_args()
    rows, total, per_phase = [], [0, 0], {}
    for phase, name, day, title, body in entries(LEDGER.read_text()):
        ok, bad, src = score(body)
        if ok is None:
            continue
        line = re.search(r"^tally:\s*(\d+)\s*/\s*(\d+)", body, re.M)
        mismatch = line and (int(line.group(1)), int(line.group(2))) != (ok, bad)
        total[0] += ok
        total[1] += bad
        acc = per_phase.setdefault(phase, [0, 0])
        acc[0] += ok
        acc[1] += bad
        rows.append(f"| {name} | {phase} | {ok} | {bad} | {total[0]} / {total[1]} |" + (" tally line differs |" if mismatch else ""))
    lines = ["| experiment | phase | ✓ | ✗ | cumulative ✓ / ✗ |", "|---|---|---|---|---|", *rows, "",
             "Per phase: " + "; ".join(f"Phase {p}: {v[0]} ✓ / {v[1]} ✗" for p, v in sorted(per_phase.items(), key=lambda kv: kv[0] or 0)),
             f"Cumulative: {total[0]} ✓ / {total[1]} ✗ ({100 * total[0] / max(sum(total), 1):.0f} % of the scored predictions held)."]
    text = "\n".join(lines)
    print(text)
    if args.write:
        report = Path(args.write)
        body = report.read_text()
        block = f"<!-- tally:begin -->\n{text}\n<!-- tally:end -->"
        if "<!-- tally:begin -->" not in body:
            sys.exit(f"{report} has no tally block (<!-- tally:begin --> … <!-- tally:end -->)")
        report.write_text(re.sub(r"<!-- tally:begin -->.*?<!-- tally:end -->", lambda _: block, body, flags=re.S))
        print(f"wrote the tally block of {report}")


if __name__ == "__main__":
    main()
