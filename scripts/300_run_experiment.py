#!/usr/bin/env python3
"""One experiment, end to end: reconstruct, gate, score, plot, ledger stub.

The one command of the experiment loop (loop file, Phase 2). Given an experiment
config it: (1) runs scripts/120_reconstruct.py on the search datasets (a code
experiment first needs scripts/102_build_eicrecon.sh --label <name> and passes
--install), (2) runs the gate G4 (scripts/130_compare_collections.py) on every
DIS output against the reference R0 (fails -> REJECTED, the rest is skipped),
(3) runs scripts/400_scoreboard.py --compare R0_stock, (4) runs
scripts/200_cluster_distributions.py and scripts/401_benchmark_plots.sh into
{space}/plots/<phase>/<experiment>/, and (5) appends the "after the run" stub to
{space}/EXPERIMENTS.md with the row id, the deltas and the gate verdict, leaving
`verdict:` for the agent to fill with the mechanism.

Usage:
  uv run scripts/300_run_experiment.py configs/experiments/E03_nhits5.yaml --phase phase2
  uv run scripts/300_run_experiment.py configs/experiments/E12_split.yaml --phase phase3 --install /data/zdc-autoresearch/install/eicrecon-E12
  uv run scripts/300_run_experiment.py ... --reference R0_stock --datasets D1_pi0 D4_lambda   # a quick partial run (no ledger stub)
"""
import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import datasets_config, load_profile, load_yaml, repo_path  # noqa: E402

SCRIPTS = repo_path("scripts")


def run(cmd, log=None):
    print("+", " ".join(str(c) for c in cmd))
    if log:
        with open(log, "a") as lf:
            return subprocess.call([str(c) for c in cmd], stdout=lf, stderr=subprocess.STDOUT)
    return subprocess.call([str(c) for c in cmd])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment")
    ap.add_argument("--phase", required=True, help="plots and ledger label, e.g. phase2")
    ap.add_argument("--reference", default="R0_stock")
    ap.add_argument("--install", help="install prefix for a code experiment")
    ap.add_argument("--datasets", nargs="*", help="partial run: these datasets only, no ledger stub")
    ap.add_argument("--skip-reco", action="store_true", help="outputs exist already; gate/score/plot only")
    args = ap.parse_args()
    profile, dcfg = load_profile(), datasets_config()
    exp = load_yaml(args.experiment)
    name = exp.name
    logdir = Path(profile.logs_root) / "experiments"
    logdir.mkdir(parents=True, exist_ok=True)
    log = logdir / f"{name}.log"
    uv = ["uv", "run", "--project", str(repo_path())]

    # 1. reconstruction
    if not args.skip_reco:
        cmd = uv + [SCRIPTS / "120_reconstruct.py", args.experiment]
        if args.datasets:
            cmd += ["--datasets", *args.datasets]
        if args.install:
            cmd += ["--install", args.install]
        if run(cmd, log) != 0:
            sys.exit(f"reconstruction failed (log {log})")

    # 2. the gate on every DIS sample (and every other dataset that has a reference output)
    gate_ok = True
    datasets = args.datasets or list(exp.datasets)
    for ds in datasets:
        ref_dir = Path(profile.reco_root) / args.reference / ds
        new_dir = Path(profile.reco_root) / name / ds
        for new in sorted(new_dir.glob("*.edm4eic.root")):
            ref = ref_dir / new.name
            if not ref.exists():
                print(f"NOTE: no reference output for {ds}/{new.name}; gate skipped for it")
                continue
            rc = run(uv + [SCRIPTS / "130_compare_collections.py", ref, new], log)
            if rc != 0:
                gate_ok = False
                print(f"GATE FAIL: {ds}/{new.name} (non-ZDC collections differ from {args.reference}; see {log})")
                break
        if not gate_ok:
            break
    print(f"gate G4: {'PASS' if gate_ok else 'FAIL'}")

    # 3. truth matching and the scoreboard, 4. plots (also when the gate failed: the numbers explain why)
    run(uv + [SCRIPTS / "410_truth_match.py", name] + (["--datasets", *[d for d in datasets if d.startswith(("D1", "D4"))]] if args.datasets else []), log)
    cmd = uv + [SCRIPTS / "400_scoreboard.py", name, "--compare", args.reference]
    if args.datasets:
        cmd += ["--datasets", *args.datasets]
    run(cmd)
    run(uv + [SCRIPTS / "200_cluster_distributions.py", args.reference, name, "--phase", f"{args.phase}/{name}"])
    run(["bash", SCRIPTS / "401_benchmark_plots.sh", name, "--phase", args.phase], log)

    # 5. the ledger stub
    if not args.datasets:
        stub = (f"\n--- after the run ({date.today().isoformat()}) ---\n"
                f"row: metrics-{name}.json (scoreboard.csv, experiment={name})\n"
                f"result: <fill from the deltas printed by 400_scoreboard.py --compare {args.reference}>\n"
                f"guards: G4 {'PASS' if gate_ok else 'FAIL'}; S3 <in band / out>; S4b <...>; G1..G3 <in band / explained: ...>\n"
                f"verdict: {'REJECTED (gate G4)' if not gate_ok else '<ACCEPTED | REJECTED | INCONCLUSIVE>, one line why'}\n"
                f"understanding: <...>\nnext: <...>\n")
        with open(repo_path("space", "EXPERIMENTS.md"), "a") as fh:
            fh.write(stub)
        print("ledger stub appended to space/EXPERIMENTS.md; fill verdict/understanding/next")
    sys.exit(0 if gate_ok else 1)


if __name__ == "__main__":
    main()
