#!/usr/bin/env python3
"""F1a + F1d of `460` on the as-built source of an uncommitted code try (Phase 6, D-default-49).

`460` walks the static cone of ReconstructedLambdas from a commit (`git show <commit>:<path>`) and checks at run time
(janadot, F1d) that every factory the install reaches is in that cone. Without `please-git` a code try is a patch on
the working tree, not a commit, so `460` walks the base commit; when the try adds an input to a factory (Z1: the crystal
clusters to the neutrals), the run-time chain then holds factories the base commit's cone does not, and F1d fails for
the wrong source. This script runs the same two checks with 460's own functions, the static walk on the working tree
(the source the install was built from) or on a commit:

  F1a the static walk (460's `walk`): no truth factory in the cone, every input produced or *RawHits;
  F1d every factory janadot reaches from ReconstructedLambdas is in that cone (460's `run_janadot`).

Controls (Step 0 record): the Z1 install against the base commit a15b0db6 FAILs (the crystal chain outside the cone);
against the working tree it PASSes; MSF6_Y9's install against a15b0db6 PASSes.

Usage:
  uv run scripts/478_f1_as_built.py configs/experiments/Z1b_crystal_column.yaml --tree submodules/EICrecon --tag Z1b
  uv run scripts/478_f1_as_built.py configs/experiments/Z1_crystal_photons.yaml --commit a15b0db6 --tag CTL6_478_commit
Writes space/perf/f1-as-built-<tag>.json; exit 1 on FAIL.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, load_yaml, repo_path  # noqa: E402

spec = importlib.util.spec_from_file_location("fp460", repo_path("scripts", "460_fair_play.py"))
fp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fp)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--tree", help="the source tree the install was built from (submodules/EICrecon)")
    src.add_argument("--commit", help="a commit of submodules/EICrecon")
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    profile = load_profile()
    exp = load_yaml(args.experiment)
    install = Path(profile.install_root) / (f"eicrecon-{exp.install_label}" if exp.get("install_label") else f"eicrecon-{fp.PIN[:12]}")
    sources = fp.sources_at(tree=args.tree) if args.tree else fp.sources_at(fp.git("rev-parse", args.commit).strip())
    regs = fp.registrations_of(sources)
    cone, leaves, f1a, notes = fp.walk(regs)
    reached = fp.run_janadot(exp, install, profile)
    known = {r["tag"] for r in cone} | {o for r in cone for o in r["outputs"]} | leaves
    f1d = [f"factory {n} runs in the chain but is not in the static cone" for n in reached if n not in known and n != fp.START]
    verdict = "PASS" if not (f1a or f1d) else "FAIL"
    out = {"experiment": exp.name, "install": str(install), "source": args.tree or args.commit, "verdict": verdict,
           "F1a": {"failures": f1a, "cone_factories": len(cone), "leaves": sorted(leaves)},
           "F1d": {"failures": f1d, "reached": len(reached)}}
    path = repo_path("space", "perf", f"f1-as-built-{args.tag}.json")
    path.write_text(json.dumps(out, indent=1))
    for x in (f1a + f1d)[:5]:
        print("  " + x)
    print(f"478 {args.tag}: {verdict} — F1a {len(f1a)} failure(s) (cone {len(cone)} factories, leaves {sorted(leaves)}), "
          f"F1d {len(f1d)} failure(s) ({len(reached)} factories reached) → {path}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
