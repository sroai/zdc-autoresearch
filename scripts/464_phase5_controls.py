#!/usr/bin/env python3
"""Damaged controls of the Phase 5 ruler (zdc-autoresearch-loop-v5.md, Step 0 item 4; CLAUDE.md rule 2).

  swap     {reco}/CTL5_swap/<D6s dataset>/: links to the base row's outputs shifted by one file (file i holds the
           reconstruction of file i+1, the last wraps to the first). The truth no longer belongs to the
           reconstruction: `210` must find almost nothing, `463` must REJECT it, `460` F2b must FAIL (the raw
           hits of file 0001 differ from the base row's).
  purity   {data}/gate-controls/phase5/perf/msf-regimes-CTL5_purity-<D6s dataset>.json: the base row's `210`
           outputs with every N_window raised by --inflate (default 1.3) and the purity recomputed, the per-Λ
           results unchanged: `463 --perf-dir` must return REJECTED (purity) at z = 0.

Links and copies only; nothing is deleted. Usage:
  uv run scripts/464_phase5_controls.py swap
  uv run scripts/464_phase5_controls.py purity [--inflate 1.3]
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, reco_dir, repo_path  # noqa: E402

BASE = "MSF5_X9"
DATASETS = ("D6s_9x275", "D6s_9x130")


def swap(prof):
    for ds in DATASETS:
        src = reco_dir(prof, BASE, ds)
        outs = sorted(f for f in src.glob("*.edm4eic.root") if ".part." not in f.name)
        if len(outs) != 40:
            sys.exit(f"{src}: {len(outs)} outputs, expected 40")
        dst = reco_dir(prof, "CTL5_swap", ds)
        dst.mkdir(parents=True, exist_ok=True)
        for i, f in enumerate(outs):
            link = dst / f.name
            if link.is_symlink() or link.exists():
                continue
            os.symlink(outs[(i + 1) % len(outs)], link)
        print(f"{dst}: {len(outs)} links, file i -> {BASE} file i+1")


def purity(prof, inflate):
    out = Path(prof.data_root) / "gate-controls" / "phase5" / "perf"
    out.mkdir(parents=True, exist_ok=True)
    for ds in DATASETS:
        d = json.loads(repo_path("space", "perf", f"msf-regimes-{BASE}-{ds}.json").read_text())
        r = dict(d["rows"][BASE])
        r["N_window"] = int(round(r["N_window"] * inflate))
        r["purity"] = r["N_found"] / r["N_window"]
        r["purity_err"] = (r["purity"] * (1 - r["purity"]) / r["N_window"]) ** 0.5
        d["rows"] = {"CTL5_purity": r}
        d["control"] = f"{BASE} with N_window × {inflate} (464 purity)"
        d["per_lambda"] = [{**{k: v for k, v in l.items() if k != BASE}, "CTL5_purity": l[BASE]} for l in d["per_lambda"]]
        path = out / f"msf-regimes-CTL5_purity-{ds}.json"
        path.write_text(json.dumps(d))
        print(f"{path}: N_window {d['rows']['CTL5_purity']['N_window']}, purity {100 * r['purity']:.1f} %")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("control", choices=["swap", "purity"])
    ap.add_argument("--inflate", type=float, default=1.3)
    args = ap.parse_args()
    prof = load_profile()
    swap(prof) if args.control == "swap" else purity(prof, args.inflate)


if __name__ == "__main__":
    main()
