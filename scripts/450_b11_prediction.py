#!/usr/bin/env python3
"""B11 pre-registration input: the clustering selector's expected yield for "chain high, collect low".

B11 is predicted to keep E02's separation (chaining at 480 keV) while restoring P1b's collected energy.
The selector is 415's vertex_fixed_tagrefit; E02 has no tag cache (its ROOT was deleted before the
tagged variants existed), so its gain is taken from the truth-identified variant: per D4 momentum,
B11_tagrefit = L01_tagrefit × E02_truth / P1b_truth. Also the McNemar z the gain would reach if every
change were a gain (lost = 0) and with the loss rate L01 → E02-like rows show (lost = 10 % of gained).

Usage: uv run scripts/450_b11_prediction.py
"""
import csv
import json
import math
from pathlib import Path

PERF = Path(__file__).resolve().parents[1] / "space" / "perf"


def load(row):
    return json.loads((PERF / f"lambda-offline-{row}.json").read_text())["per_momentum"]


def main():
    l01, p1b, e02 = load("L01_box3114"), load("P1b_R0_thr"), load("E02_chain480")
    out = {"inputs": ["L01_box3114 vertex_fixed_tagrefit", "P1b_R0_thr vertex_fixed_truth", "E02_chain480 vertex_fixed_truth"],
           "per_momentum": {}}
    print(f"{'p':>4s} {'L01 tagrefit':>12s} {'P1b truth':>9s} {'E02 truth':>9s} {'ratio':>6s} {'B11 pred':>8s} {'gain':>5s} {'z(l=0)':>7s} {'z(l=.1g)':>8s}")
    tot_l, tot_b = 0, 0.0
    for p in sorted(l01, key=int):
        lt = l01[p]["vertex_fixed_tagrefit_n"]
        pt, et = p1b[p]["vertex_fixed_truth_n"], e02[p]["vertex_fixed_truth_n"]
        ratio = et / pt if pt else float("nan")
        pred = lt * ratio
        gain = pred - lt
        z0 = gain / math.sqrt(gain) if gain > 0 else 0.0
        g, l = gain / 0.9, gain / 0.9 * 0.1
        z1 = (g - l) / math.sqrt(g + l) if gain > 0 else 0.0
        out["per_momentum"][p] = {"L01_tagrefit_n": lt, "P1b_truth_n": pt, "E02_truth_n": et, "ratio": ratio,
                                  "B11_tagrefit_pred_n": pred, "gain_n": gain, "z_lost0": z0, "z_lost10pct": z1}
        tot_l += lt
        tot_b += pred
        print(f"{p:>4s} {lt:12d} {pt:9d} {et:9d} {ratio:6.2f} {pred:8.1f} {gain:5.1f} {z0:7.2f} {z1:8.2f}")
    out["sum"] = {"L01_tagrefit_n": tot_l, "B11_tagrefit_pred_n": tot_b}
    head = {r["row"]: r for r in csv.DictReader((PERF / "headline.csv").open())}["L01_box3114"]
    pt = [float(head[f"S4o_vertex_fixed_tagrefit_per_thrown_{p}"]) * out["per_momentum"][p]["ratio"] for p in sorted(l01, key=int)]
    out["B11_tagrefit_per_thrown_pct_mean_pred"] = sum(pt) / len(pt)
    out["L01_tagrefit_per_thrown_pct_mean"] = float(head["S4o_vertex_fixed_tagrefit_per_thrown_mean"])
    print(f"per thrown, mean: L01 {out['L01_tagrefit_per_thrown_pct_mean']:.3f} %, B11 predicted {out['B11_tagrefit_per_thrown_pct_mean_pred']:.3f} %")
    print(f"sum: L01 {tot_l}, B11 predicted {tot_b:.1f} ({100 * (tot_b / tot_l - 1):+.0f} %)")
    path = PERF / "b11-prediction.json"
    path.write_text(json.dumps(out, indent=1))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
