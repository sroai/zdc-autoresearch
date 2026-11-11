#!/usr/bin/env python3
"""Summary of the leave-one-out ranking (`485`): what each change of the reference row is worth on the MSF search halves.

For every row given, reads 463's space/perf/msf-select-<row>-vs-<ref>-D6s.json (485 calls 463 with the reference as
"best" and the ablation as "candidate"). Per row it reports N_found per
beam and pooled, the loss against the reference (the change's worth), b (Λ found only with the change), c (only without
it), the paired z of the loss (b − c) / √(b + c), N_window and purity, and the found Λ in the three main regimes (210:
all photons in the ZDC, one in B0 and one in the ZDC, both in B0). Rows are ranked by the change's worth.

Writes space/perf/leave-one-out-<ref>.json and prints the ranking as nested markdown lists (lists, not tables).

Usage: uv run scripts/486_leave_one_out_summary.py Z8_hcal_axis_law AB1_no_depth_cut AB2_no_pairing ...
"""
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PERF = REPO / "space" / "perf"
REGIMES = {"all-ZDC": "n ZDC | γ ZDC+ZDC", "B0+ZDC": "n ZDC | γ B0+ZDC", "B0+B0": "n ZDC | γ B0+B0"}
BEAMS = ("9x275", "9x130")


def regimes(row):
    out = {}
    for b in BEAMS:
        p = PERF / f"msf-regimes-{row}-D6s_{b}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        by = {r["regime"]: r for r in d["regimes"]}
        out[b] = {k: (by[v][row]["matched"] if v in by and row in by[v] else None) for k, v in REGIMES.items()}
    return out


def main():
    ref, rows = sys.argv[1], sys.argv[2:]
    res = []
    for row in rows:
        p = PERF / f"msf-select-{row}-vs-{ref}-D6s.json"
        if not p.exists():
            res.append({"row": row, "missing": str(p.name)})
            continue
        s = json.loads(p.read_text())
        b, c = s["b"], s["c"]
        res.append({
            "row": row,
            "found": {k: s["beams"][k]["candidate"]["N_found"] for k in BEAMS},
            "found_ref": {k: s["beams"][k]["best"]["N_found"] for k in BEAMS},
            "pooled": s["N_found"]["candidate"], "pooled_ref": s["N_found"]["best"],
            "worth": s["N_found"]["best"] - s["N_found"]["candidate"],
            "b_only_with": b, "c_only_without": c,
            "z_worth": (b - c) / math.sqrt(b + c) if b + c else 0.0,
            "window": s["N_window"]["candidate"], "window_ref": s["N_window"]["best"],
            "purity": s["purity"]["candidate"], "purity_ref": s["purity"]["best"],
            "regimes": regimes(row), "regimes_ref": regimes(ref),
        })
    done = sorted([r for r in res if "worth" in r], key=lambda r: -r["worth"])
    out = {"reference": ref, "rows": done, "missing": [r for r in res if "missing" in r]}
    (PERF / f"leave-one-out-{ref}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    for r in done:
        f, fr = r["found"], r["found_ref"]
        print(f"- **{r['row']}**: worth {r['worth']:+d} Λ ({100 * r['worth'] / r['pooled_ref']:+.0f} %), "
              f"z {r['z_worth']:+.1f}")
        print(f"  - found without it: 9x275 {f['9x275']} (ref {fr['9x275']}), 9x130 {f['9x130']} (ref {fr['9x130']}); "
              f"pooled {r['pooled']} (ref {r['pooled_ref']})")
        print(f"  - paired: {r['b_only_with']} found only with it, {r['c_only_without']} only without it")
        print(f"  - window {r['window']} (ref {r['window_ref']}); purity {100 * r['purity']:.1f} % "
              f"(ref {100 * r['purity_ref']:.1f} %)")
        for b in BEAMS:
            g, gr = r["regimes"].get(b, {}), r["regimes_ref"].get(b, {})
            print(f"  - {b} by regime: " + ", ".join(f"{k} {g.get(k)} (ref {gr.get(k)})" for k in REGIMES))
    for m in out["missing"]:
        print(f"- **{m['row']}**: not scored ({m['missing']} missing)")
    print("wrote", PERF / f"leave-one-out-{ref}.json")


if __name__ == "__main__":
    main()
