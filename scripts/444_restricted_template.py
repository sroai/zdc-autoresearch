#!/usr/bin/env python3
"""The restricted-collection template measured against the full output (loop v3, Phase 3 Step 0 item 3).

Reads the two timing rows T_R0_restricted and T_R0_full (R0, the same input files: one D4 file and
chunk000 of both D5 samples, reconstructed side by side) and reports:

  T      wall seconds per 1000 events, restricted and full, per dataset;
  size   output bytes per file and the restricted / full ratio (the ratio 300's preflight and
         integrity check scale the reference sizes by);
  same   the owned (ZDC, neutrals, Λ) collections identical leaf by leaf (130 --zdc), and the numbers
         410 (S0 per momentum) and 200 (G1 to G3) compute from each output equal.

Writes space/perf/restricted-template.json.
Usage: uv run scripts/444_restricted_template.py
"""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, repo_path  # noqa: E402

ROWS = ("T_R0_restricted", "T_R0_full")
UV = ["uv", "run", "--project", str(repo_path())]


def timing(reco, row):
    with open(reco / row / "timing.csv") as fh:
        return {r["dataset"]: float(r["s_per_1000"]) for r in csv.DictReader(fh)}


def main():
    profile = load_profile()
    reco = Path(profile.reco_root)
    t = {row: timing(reco, row) for row in ROWS}
    out = {"T_s_per_1000": t, "files": {}, "size_ratio": {}, "zdc_identical": {}, "same_numbers": {}}
    ratios = {}
    # pairs: every T_R0_full output, plus restricted outputs whose full counterpart is R0_stock's (D6a: no timing pair)
    pairs = [(f.parent.name, reco / "T_R0_restricted" / f.parent.name / f.name, f) for f in sorted((reco / "T_R0_full").glob("*/*.edm4eic.root"))]
    pairs += [(f.parent.name, f, reco / "R0_stock" / f.parent.name / f.name) for f in sorted((reco / "T_R0_restricted").glob("D6a*/*.edm4eic.root"))]
    for ds, f_res, f_full in pairs:
        size = {"restricted_bytes": f_res.stat().st_size, "full_bytes": f_full.stat().st_size}
        size["ratio"] = size["restricted_bytes"] / size["full_bytes"]
        out["files"][f"{ds}/{f_full.name}"] = size
        ratios.setdefault(ds, []).append(size["ratio"])
        gate = subprocess.run(UV + [str(repo_path("scripts", "130_compare_collections.py")), str(f_full), str(f_res), "--zdc"],
                              capture_output=True, text=True)
        out["zdc_identical"][f"{ds}/{f_full.name}"] = gate.stdout.strip().splitlines()[-1] if gate.stdout.strip() else gate.stderr.strip()[-200:]
        print(f"{ds}: restricted {size['restricted_bytes'] / 1e6:.0f} MB / full {size['full_bytes'] / 1e6:.0f} MB = {size['ratio']:.3f}; "
              f"T {t['T_R0_restricted'].get(ds, float('nan')):.0f} / {t['T_R0_full'].get(ds, float('nan')):.0f} s per 1000; --zdc: {out['zdc_identical'][f'{ds}/{f_full.name}']}")
    # per dataset; "guns" = the D4 ratio, which 300 applies to the gun datasets without their own measurement
    out["size_ratio"] = {k: max(v) for k, v in ratios.items() if v}
    out["size_ratio"]["guns"] = out["size_ratio"].get("D4_lambda", 1.0)

    # One parameter experiment on D1–D5: R0's full output per dataset × the measured ratio of its kind
    estimate = {}
    for ds in ("D1_pi0", "D2_photon", "D3_neutron", "D4_lambda", "D5_dis_minq2_100", "D5_dis_minq2_0"):
        full = sum(f.stat().st_size for f in (reco / "R0_stock" / ds).glob("*.edm4eic.root"))
        key = f"{ds}/{ds}_chunk000.edm4eic.root" if ds.startswith("D5") else None
        ratio = out["files"][key]["ratio"] if key in out["files"] else out["size_ratio"]["guns"]
        estimate[ds] = {"full_GB": full / 1e9, "restricted_GB": full * ratio / 1e9}
    out["experiment_estimate_GB"] = estimate
    tot_full = sum(v["full_GB"] for v in estimate.values())
    tot_res = sum(v["restricted_GB"] for v in estimate.values())
    out["experiment_total_GB"] = {"full": tot_full, "restricted": tot_res}
    print(f"one parameter experiment (D1–D5): full {tot_full:.1f} GB → restricted {tot_res:.1f} GB "
          f"(guns {sum(v['restricted_GB'] for k, v in estimate.items() if not k.startswith('D5')):.1f} GB)")

    # 410 on the D4 file of each row: the S0 cells must be equal
    s0 = {}
    for row in ROWS:
        subprocess.run(UV + [str(repo_path("scripts", "410_truth_match.py")), row, "--datasets", "D4_lambda"], capture_output=True, text=True)
        pm = json.loads(repo_path("space", "perf", f"truth-{row}-D4_lambda.json").read_text())["per_momentum"]
        s0[row] = {p: {k: v for k, v in cells.items() if k.startswith(("S0_", "S4a"))} for p, cells in pm.items()}
    out["same_numbers"]["410_S0_and_S4a"] = s0[ROWS[0]] == s0[ROWS[1]]
    print(f"410 S0/S4a cells equal: {out['same_numbers']['410_S0_and_S4a']}")

    # 200 on the D5 chunks: the G1 to G3 table lines must be equal for the two rows
    res = subprocess.run(UV + [str(repo_path("scripts", "200_cluster_distributions.py")), "T_R0_full", "T_R0_restricted",
                               "--datasets", "D5_dis_minq2_100", "D5_dis_minq2_0", "--phase", "phase3/restricted_check"],
                         capture_output=True, text=True)
    lines = [ln for ln in res.stdout.splitlines() if re.match(r"\s*\|?\s*T_R0_(full|restricted)\b", ln)]
    by_row = {}
    for ln in lines:
        row = re.search(r"T_R0_(full|restricted)", ln).group(0)
        by_row.setdefault(row, []).append(ln.split()[1:])     # the numbers, without the row name and its padding
    equal = bool(by_row) and by_row.get("T_R0_full") == by_row.get("T_R0_restricted")
    out["same_numbers"]["200_G1_G3"] = equal
    out["same_numbers"]["200_lines"] = lines
    print(f"200 G1–G3 lines equal: {equal} ({len(lines)} lines)")
    if not lines:
        print(res.stdout[-2000:], res.stderr[-2000:])
    path = repo_path("space", "perf", "restricted-template.json")
    path.write_text(json.dumps(out, indent=1))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
