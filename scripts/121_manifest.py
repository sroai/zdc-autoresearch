#!/usr/bin/env python3
"""Write or verify a sha256 manifest of files, the identity of a frozen dataset.

A manifest is a JSON file {section: {relative_or_absolute_path: {"sha256", "bytes", "events"?}}}.
`write` replaces the named section with the files found under the given
directories (`*.root`, `*.hepmc`); `verify` recomputes every hash and prints the
first mismatch. The tool's git SHA is recorded per section so a regenerated
dataset can be traced to the generator version (work-common.md, the
missing-artifact row).

Usage:
  uv run scripts/121_manifest.py write <manifest.json> <dir>... --section guns [--follow-links] [--events]
  uv run scripts/121_manifest.py verify <manifest.json> [--section guns]
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import REPO_ROOT  # noqa: E402
from zdc.edm import n_events, sha256_of  # noqa: E402


def git_sha():
    try:
        return subprocess.check_output(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], text=True).strip()[:12]
    except Exception:
        return "unknown"


def write(args):
    manifest = json.loads(Path(args.manifest).read_text()) if Path(args.manifest).exists() else {}
    entries = {}
    for d in args.dirs:
        for f in sorted(Path(d).rglob("*")):
            if f.suffix not in (".root", ".hepmc") or (f.is_symlink() and not args.follow_links):
                continue
            if not f.is_file():
                continue
            entry = {"sha256": sha256_of(f), "bytes": f.stat().st_size}
            if args.events and f.suffix == ".root":
                try:
                    entry["events"] = int(n_events(f))
                except Exception as e:  # a damaged file is a finding, not a crash of the manifest
                    entry["events"] = f"ERR {e}"
            entries[str(f)] = entry
            print(f"{entry['sha256'][:12]}  {entry['bytes']:>12}  {f}")
    manifest[args.section] = {"_written": datetime.now(timezone.utc).isoformat(timespec="seconds"), "_tool_git_sha": git_sha(), "files": entries}
    Path(args.manifest).parent.mkdir(parents=True, exist_ok=True)
    Path(args.manifest).write_text(json.dumps(manifest, indent=1, sort_keys=True))
    print(f"wrote {len(entries)} file(s) into section '{args.section}' of {args.manifest}")


def verify(args):
    manifest = json.loads(Path(args.manifest).read_text())
    sections = [args.section] if args.section else [k for k in manifest if not k.startswith("_")]
    bad = 0
    total = 0
    for s in sections:
        for path, entry in manifest[s]["files"].items():
            total += 1
            p = Path(path)
            if not p.exists():
                print(f"MISSING  {path}")
                bad += 1
                continue
            if sha256_of(p) != entry["sha256"]:
                print(f"MISMATCH {path}")
                bad += 1
    print(f"{'PASS' if bad == 0 else 'FAIL'}: {total - bad}/{total} files verify")
    sys.exit(0 if bad == 0 else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("manifest")
    w.add_argument("dirs", nargs="+")
    w.add_argument("--section", required=True)
    w.add_argument("--follow-links", action="store_true")
    w.add_argument("--events", action="store_true", help="also record the event count of ROOT files")
    w.set_defaults(func=write)
    v = sub.add_parser("verify")
    v.add_argument("manifest")
    v.add_argument("--section")
    v.set_defaults(func=verify)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
