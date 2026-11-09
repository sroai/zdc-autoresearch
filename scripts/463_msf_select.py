#!/usr/bin/env python3
"""Phase 5 selector (zdc-autoresearch-loop-v5.md): a candidate row against the current best on the MSF halves.

Reads the `210` outputs space/perf/msf-regimes-<row>-D6<split>_<beam>.json of both rows (each written by `210` with
that single --row) for the beams 9x275 and 9x130, and pairs the Λ → nπ⁰ by (file, event): the truth is the same
simulation files, so both rows must list the same Λ.

  b   Λ found by the best only;  c   Λ found by the candidate only (pooled over both beams)
  z   (c − b) / √(b + c)                                   the paired test on the score N_found
  P   Σ N_found / Σ N_window per row (pooled purity);  z_P = (P_cand − P_best) / √(σ_cand² + σ_best²),
      σ = √(P (1 − P) / Σ N_window)                       the purity guard (unpaired, conservative)

Verdict (search split s): REJECTED (purity) if z_P < −2; ACCEPTED if z ≥ 3 and c > b; INCONCLUSIVE if c > b;
REJECTED otherwise. FOUL is `460`'s, not this script's. Held-out split h (checkpoints, F5): REPRODUCES if c > b and
z > 2, else NOT REPRODUCED.

Writes space/perf/msf-select-<candidate>-vs-<best>-D6<split>.json and prints one line per beam and the verdict.

Usage:
  uv run scripts/463_msf_select.py MSF5_X9 Y1_b0_photon_energy                 # a try on the search halves
  uv run scripts/463_msf_select.py MSF5_X9 Y3_x --split h                       # a checkpoint on the held-out halves
  uv run scripts/463_msf_select.py MSF5_X9 CTL5_purity --perf-dir <dir>         # a control's 210 outputs elsewhere
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import repo_path  # noqa: E402

BEAMS = ("9x275", "9x130")


def load(perf, row, ds):
    path = Path(perf) / f"msf-regimes-{row}-{ds}.json"
    if not path.exists():
        sys.exit(f"missing {path}: run `uv run scripts/210_msf_lambda_regimes.py {ds} --row {row}`")
    d = json.loads(path.read_text())
    if row not in d.get("rows", {}):
        sys.exit(f"{path} has no N_window for {row}: rerun 210 (Phase 5 version)")
    found = {(l["file"], l["event"]): bool(l[row]["matched"]) for l in d["per_lambda"]}
    return d, found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("best")
    ap.add_argument("candidate")
    ap.add_argument("--split", choices=["s", "h"], default="s", help="s: search halves (tries), h: held out (checkpoints)")
    ap.add_argument("--perf-dir", help="where the candidate's 210 outputs are (default space/perf)")
    args = ap.parse_args()
    perf = repo_path("space", "perf")
    out = {"best": args.best, "candidate": args.candidate, "split": args.split, "beams": {}}
    B = C = 0
    sums = {"best": [0, 0], "cand": [0, 0]}   # [N_found, N_window]
    for beam in BEAMS:
        ds = f"D6{args.split}_{beam}"
        db, fb = load(perf, args.best, ds)
        dc, fc = load(args.perf_dir or perf, args.candidate, ds)
        if fb.keys() != fc.keys() or db["files"] != dc["files"]:
            sys.exit(f"{ds}: the two rows do not list the same Λ → nπ⁰ (different files or truth): no paired test")
        b = sum(1 for k in fb if fb[k] and not fc[k])
        c = sum(1 for k in fb if fc[k] and not fb[k])
        B, C = B + b, C + c
        rb, rc = db["rows"][args.best], dc["rows"][args.candidate]
        for key, r in (("best", rb), ("cand", rc)):
            sums[key][0] += r["N_found"]
            sums[key][1] += r["N_window"]
        out["beams"][beam] = {"dataset": ds, "N_expected": rb["N_expected"], "b": b, "c": c,
                              "best": {k: rb[k] for k in ("N_found", "N_window", "yield", "yield_err", "purity", "purity_err")},
                              "candidate": {k: rc[k] for k in ("N_found", "N_window", "yield", "yield_err", "purity", "purity_err")}}
    z = (C - B) / math.sqrt(B + C) if B + C else 0.0
    pur = {}
    for key in ("best", "cand"):
        k, n = sums[key]
        p = k / n if n else 0.0
        pur[key] = (p, math.sqrt(p * (1 - p) / n) if n else 0.0)
    den = math.hypot(pur["best"][1], pur["cand"][1])
    zp = (pur["cand"][0] - pur["best"][0]) / den if den else 0.0
    if args.split == "s":
        if zp < -2:
            verdict = "REJECTED (purity)"
        elif z >= 3 and C > B:
            verdict = "ACCEPTED"
        elif C > B:
            verdict = "INCONCLUSIVE"
        else:
            verdict = "REJECTED"
    else:
        verdict = "REPRODUCES" if C > B and z > 2 else "NOT REPRODUCED"
    out.update({"b": B, "c": C, "z": z, "N_found": {"best": sums["best"][0], "candidate": sums["cand"][0]},
                "N_window": {"best": sums["best"][1], "candidate": sums["cand"][1]},
                "purity": {"best": pur["best"][0], "best_err": pur["best"][1], "candidate": pur["cand"][0], "candidate_err": pur["cand"][1]},
                "z_purity": zp, "verdict": verdict})
    path = perf / f"msf-select-{args.candidate}-vs-{args.best}-D6{args.split}.json"
    path.write_text(json.dumps(out, indent=1))
    for beam, x in out["beams"].items():
        xb, xc = x["best"], x["candidate"]
        print(f"{x['dataset']}: N_found {xb['N_found']} → {xc['N_found']} of {x['N_expected']:.0f} "
              f"(yield {100 * xb['yield']:.2f} → {100 * xc['yield']:.2f} %), b {x['b']} c {x['c']}; "
              f"purity {100 * (xb['purity'] or 0):.1f} → {100 * (xc['purity'] or 0):.1f} % (N_window {xb['N_window']} → {xc['N_window']})")
    print(f"pooled: N_found {sums['best'][0]} → {sums['cand'][0]}, b {B} c {C}, z {z:+.2f}; purity "
          f"{100 * pur['best'][0]:.1f} → {100 * pur['cand'][0]:.1f} %, z_P {zp:+.2f} → {verdict}")
    print("wrote", path)


if __name__ == "__main__":
    main()
