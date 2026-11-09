#!/usr/bin/env python3
"""F1b for a Phase 5 try kept as a patch (zdc-autoresearch-loop-v5.md, F6: no commits this phase).

`460` scans the added lines of pin..<commit>, or, for a source tree, only the factory registration files
(src/detectors/*/*.cc, src/global/*/*.cc). A Phase 5 try is an uncommitted patch on top of the accepted stack and
may change algorithm code, so this script scans every added line of the patch file itself, with `460`'s own
patterns (imported, not copied): no line may name truth (MC particles, sim hits, associations, links, the event
header, event or run numbers, the input file) or carry a dataset-keyed constant. Tests and benchmarks are exempt,
as in `460`. Comments are stripped first.

Writes space/perf/patch-scan-<tag>.json; exit 1 on a FAIL.

Usage:
  uv run scripts/465_patch_scan.py space/notes/patches/Y2_vertex_lever_arm.patch
  uv run scripts/465_patch_scan.py <damaged copy> --tag CTL5_patch_truth          # the control
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import repo_path  # noqa: E402

spec = importlib.util.spec_from_file_location("fp460", repo_path("scripts", "460_fair_play.py"))
fp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("patch")
    ap.add_argument("--tag", help="JSON name (default: the patch file's stem)")
    args = ap.parse_args()
    path = Path(args.patch)
    tag = args.tag or path.stem
    failures, fname, n_added, files = [], None, 0, set()
    for line in path.read_text().splitlines():
        if line.startswith("+++ "):
            fname = line[6:] if line.startswith("+++ b/") else None
            if fname:
                files.add(fname)
            continue
        if not line.startswith("+") or fname is None or re.match(r"src/(tests|benchmarks)/", fname):
            continue
        n_added += 1
        code = fp.strip_comments(line[1:])
        if not code.strip():
            continue
        if fp.TRUTH_CODE.search(code):
            failures.append(f"{fname}: names truth: {code.strip()[:140]}")
        if fp.DATASET_CODE.search(code) or sum(bool(re.search(rf"(?<![\d.]){p}(?![\d])", code)) for p in fp.D4_MOMENTA) >= 3:
            failures.append(f"{fname}: dataset-keyed constant: {code.strip()[:140]}")
    verdict = "FAIL" if failures else "PASS"
    if n_added == 0:
        verdict, failures = "FAIL", ["no added source lines: not a patch"]
    out = {"tag": tag, "patch": str(path), "files": sorted(files), "added_lines": n_added, "verdict": verdict,
           "failures": failures[:20], "n_failures": len(failures)}
    dst = repo_path("space", "perf", f"patch-scan-{tag}.json")
    dst.write_text(json.dumps(out, indent=1))
    print(f"{verdict} F1b patch {tag}: {n_added} added lines in {sorted(files)}; {len(failures)} failure(s)"
          + (f" — {failures[0]}" if failures else "") + f" -> {dst.relative_to(repo_path())}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
