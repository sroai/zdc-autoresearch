#!/usr/bin/env python3
"""One experiment, end to end: reconstruct, gate, score, plot, ledger stub.

The one command of the experiment loop (loop file, Phase 2). Given an experiment
config it: (1) runs scripts/120_reconstruct.py on the search datasets (a code
experiment first needs scripts/102_build_eicrecon.sh --label <name> and passes
--install), (2) runs the gate G4 (scripts/130_compare_collections.py) on every
DIS output against the reference R0 (fails -> REJECTED, the rest is skipped),
(3) runs scripts/400_scoreboard.py --compare R0_stock and scripts/420_refit_calibration.py
(S2 is judged on the refit residuals, D-user-13), (4) runs
scripts/200_cluster_distributions.py and scripts/401_benchmark_plots.sh into
{space}/plots/<phase>/<experiment>/, and (5) appends the "after the run" stub to
{space}/EXPERIMENTS.md with the row id, the deltas and the gate verdict, leaving
`verdict:` for the agent to fill with the mechanism.

Every launch begins with the preflight (setup file, Budgets): free space on {data} at least twice the
expected output and never under 150 GB; eicrecon processes running plus the jobs requested at most the
profile's cores. After the reconstruction the integrity check requires, for every output, its per-file JSON,
a non-empty log without ENOSPC / Traceback / segmentation / timeout errors, and a size within 50 % of the
reference row's counterpart (scaled by the restricted-template ratio when the experiment writes the
restricted collections and the reference all). Any failure stops the chain before the scoreboard.

Usage:
  uv run scripts/300_run_experiment.py configs/experiments/E03_nhits5.yaml --phase phase2
  uv run scripts/300_run_experiment.py configs/experiments/E06_x.yaml --phase phase3 --preflight-only           # check, launch nothing
  uv run scripts/300_run_experiment.py ... --preflight-only --min-free-gb 100000                                # seen to refuse (disk)
  uv run scripts/300_run_experiment.py configs/experiments/E12_split.yaml --phase phase3 --install /data/zdc-autoresearch/install/eicrecon-E12
  uv run scripts/300_run_experiment.py ... --reference R0_stock --datasets D1_pi0 D4_lambda   # a quick partial run (no ledger stub)
"""
import argparse
import os
import json
import re
import shutil
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


MIN_FREE_GB = 150                  # setup file, Budgets: preflight
# D-user-35 (2026-11-08): dis-autoresearch runs on this machine and has priority. Leave it cores and memory.
DEFAULT_JOBS = 4                   # parallel eicrecon processes unless --jobs says otherwise
PRIORITY_IDLE_CORES = 8            # cores kept free beyond everything already running
MEM_RESERVE_GB = 16                # MemAvailable kept free after the jobs start
MEM_PER_JOB_GB = 3                 # a single-threaded eicrecon, generous
SIZE_TOLERANCE = 0.5               # an output within ±50 % of its reference counterpart
ERROR_RE = re.compile(r"ENOSPC|No space left|Traceback|segmentation (fault|violation)|timeout|timed out", re.IGNORECASE)
ERROR_EXEMPT = ("jana:timeout", "jana:warmup_timeout", "description:")   # JANA's parameter table, printed by every run
RESTRICTED_TEMPLATE = repo_path("space", "perf", "restricted-template.json")


def is_restricted(exp):
    return list(exp.get("output_collections") or [".*"]) != [".*"]


SLIM_TEMPLATE = repo_path("space", "perf", "slim-template.json")


def is_slim(exp):
    """Phase 4 slim template (D-default-45): no simulated hits, no rec/subcell hits; raw hits kept for F2."""
    cols = list(exp.get("output_collections") or [".*"])
    return is_restricted(exp) and not any("FarForwardZDC.*" in c for c in cols)


def size_ratio(exp, reference_exp, dataset):
    """Expected output size relative to the reference's counterpart: 1, or the measured template ratios."""
    if is_slim(exp) != is_slim(reference_exp) and is_restricted(exp) and is_restricted(reference_exp):
        # slim / restricted, measured on one D4 file (D-default-45)
        r = json.loads(SLIM_TEMPLATE.read_text())["ratio"] if SLIM_TEMPLATE.exists() else 1.0
        return r if is_slim(exp) else 1.0 / r
    if is_restricted(exp) == is_restricted(reference_exp):
        return 1.0
    # Measured per dataset by 444 (one file each); a dataset without its own measurement takes the gun ratio,
    # the largest (ZDC hits dominate a gun event), which is the safe side for the preflight's disk estimate.
    ratios = json.loads(RESTRICTED_TEMPLATE.read_text())["size_ratio"] if RESTRICTED_TEMPLATE.exists() else {}
    r = ratios.get(dataset, ratios.get("guns", 1.0))
    return r if is_restricted(exp) else 1.0 / r


def reference_config(name):
    for f in sorted(repo_path("configs", "experiments").glob("*.yaml")):
        cfg = load_yaml(f)
        if cfg.get("name") == name:
            return cfg
    return None


def eicrecon_processes():
    out = subprocess.run(["pgrep", "-c", "-x", "eicrecon"], capture_output=True, text=True).stdout.strip()
    return int(out or 0)


def preflight(exp, datasets, reference, profile, jobs, min_free_gb, proc_cap):
    """The launch conditions of the setup file (Budgets: preflight). Returns a list of failures."""
    ref_exp = reference_config(reference) or exp
    expected = 0
    for ds in datasets:
        ref_dir = Path(profile.reco_root) / reference / ds
        expected += sum(f.stat().st_size for f in ref_dir.glob("*.edm4eic.root")) * size_ratio(exp, ref_exp, ds)
    free = shutil.disk_usage(profile.reco_root).free
    need = max(2 * expected, min_free_gb * 1e9)
    running = eicrecon_processes()
    print(f"preflight: free {free / 1e9:.0f} GB, need {need / 1e9:.0f} GB (2 × expected {expected / 1e9:.1f} GB, floor {min_free_gb} GB); "
          f"eicrecon running {running} + requested {jobs} vs cap {proc_cap}")
    failures = []
    if free < need:
        failures.append(f"free space {free / 1e9:.0f} GB < {need / 1e9:.0f} GB")
    if running + jobs > proc_cap:
        failures.append(f"processes {running} running + {jobs} requested > cap {proc_cap}")
    # priority project (D-user-35): the load of everything else plus our jobs leaves PRIORITY_IDLE_CORES idle
    other = max(0.0, os.getloadavg()[0] - running)
    allowed = int(os.cpu_count() - PRIORITY_IDLE_CORES - other)
    mem_avail = int(next(l.split()[1] for l in open("/proc/meminfo") if l.startswith("MemAvailable"))) / 1e6
    print(f"preflight (D-user-35 priority): load of others {other:.1f}, cores {os.cpu_count()}, idle kept "
          f"{PRIORITY_IDLE_CORES} -> jobs allowed {allowed}; MemAvailable {mem_avail:.0f} GB, "
          f"need {MEM_RESERVE_GB + MEM_PER_JOB_GB * jobs} GB")
    if jobs > max(1, allowed):
        failures.append(f"jobs {jobs} > {max(1, allowed)} allowed beside the priority project (rerun with --jobs {max(1, allowed)} or wait)")
    if mem_avail < MEM_RESERVE_GB + MEM_PER_JOB_GB * jobs:
        failures.append(f"MemAvailable {mem_avail:.0f} GB < {MEM_RESERVE_GB + MEM_PER_JOB_GB * jobs} GB")
    return failures


def integrity(exp, datasets, reference, profile):
    """Every output complete and clean (setup file, Budgets: preflight, after every chain). Returns failures."""
    ref_exp = reference_config(reference) or exp
    failures, counts = [], {"outputs": 0, "json": 0, "logs_clean": 0, "size_ok": 0}
    for ds in datasets:
        indir = Path(profile.datasets_root) / ds
        inputs = sorted(f for f in indir.glob("*.edm4hep.root") if ".part." not in f.name)
        outdir = Path(profile.reco_root) / exp.name / ds
        ratio = size_ratio(exp, ref_exp, ds)
        for inp in inputs:
            stem = inp.name.replace(".edm4hep.root", "")
            out, meta = outdir / f"{stem}.edm4eic.root", outdir / f"{stem}.json"
            log = Path(profile.logs_root) / "reco" / exp.name / f"{ds}_{stem}.log"
            if not out.exists():
                failures.append(f"{ds}/{stem}: output missing")
                continue
            counts["outputs"] += 1
            if meta.exists():
                counts["json"] += 1
            else:
                failures.append(f"{ds}/{stem}: no per-file JSON (truncated or failed run)")
            if log.exists() and log.stat().st_size > 0:
                bad = [ln for ln in log.read_text(errors="replace").splitlines()
                       if ERROR_RE.search(ln) and not any(x in ln for x in ERROR_EXEMPT)]
                if bad:
                    failures.append(f"{ds}/{stem}: log error: {bad[0][:120]}")
                else:
                    counts["logs_clean"] += 1
            elif meta.exists() and json.loads(meta.read_text()).get("experiment") != exp.name:
                failures.append(f"{ds}/{stem}: output belongs to another experiment")
            else:
                failures.append(f"{ds}/{stem}: log missing or empty ({log})")
            ref = Path(profile.reco_root) / reference / ds / out.name
            if ref.exists() and ref.stat().st_size > 0:
                rel = out.stat().st_size / (ref.stat().st_size * ratio)
                if abs(rel - 1) <= SIZE_TOLERANCE:
                    counts["size_ok"] += 1
                else:
                    failures.append(f"{ds}/{stem}: size {out.stat().st_size / 1e6:.0f} MB is {rel:.2f} × the expected {ref.stat().st_size * ratio / 1e6:.0f} MB")
            else:
                counts["size_ok"] += 1   # no counterpart: nothing to compare
    print(f"integrity: {counts['outputs']} outputs, {counts['json']} with JSON, {counts['logs_clean']} clean logs, "
          f"{counts['size_ok']} sizes in ±{SIZE_TOLERANCE:.0%}; {len(failures)} failure(s)")
    return failures


def main():
    sys.stdout.reconfigure(line_buffering=True)  # the preflight and integrity lines reach the log as they happen under nohup
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment")
    ap.add_argument("--phase", required=True, help="plots and ledger label, e.g. phase2")
    ap.add_argument("--reference", default="R0_stock")
    ap.add_argument("--install", help="install prefix for a code experiment")
    ap.add_argument("--datasets", nargs="*", help="partial run: these datasets only, no ledger stub")
    ap.add_argument("--skip-reco", action="store_true", help="outputs exist already; gate/score/plot only")
    ap.add_argument("--jobs", type=int, help="parallel eicrecon processes (default: DEFAULT_JOBS, D-user-35)")
    ap.add_argument("--preflight-only", action="store_true", help="run the preflight and stop")
    ap.add_argument("--lean", action="store_true", help="Phase 4: reconstruction, integrity, 410 (and 420 with D2/D3) only")
    ap.add_argument("--integrity-only", action="store_true", help="run the integrity check on existing outputs and stop")
    ap.add_argument("--min-free-gb", type=float, default=MIN_FREE_GB, help="free-space floor (the refusal test raises it)")
    ap.add_argument("--proc-cap", type=int, help="eicrecon process cap (default: the profile's cores)")
    args = ap.parse_args()
    profile, dcfg = load_profile(), datasets_config()
    exp = load_yaml(args.experiment)
    name = exp.name
    logdir = Path(profile.logs_root) / "experiments"
    logdir.mkdir(parents=True, exist_ok=True)
    log = logdir / f"{name}.log"
    uv = ["uv", "run", "--project", str(repo_path())]

    datasets = args.datasets or list(exp.datasets)
    jobs = args.jobs or DEFAULT_JOBS

    # 0. preflight: the only launcher checks disk and processes before anything starts
    if not args.skip_reco and not args.integrity_only:
        failures = preflight(exp, datasets, args.reference, profile, jobs, args.min_free_gb, args.proc_cap or int(profile.cores))
        if failures:
            sys.exit("PREFLIGHT FAIL: " + "; ".join(failures) + " — launch refused (free disk under the retention rule or wait)")
        print("preflight: PASS")
        if args.preflight_only:
            return

    # 1. reconstruction
    if not args.skip_reco and not args.integrity_only:
        cmd = uv + [SCRIPTS / "120_reconstruct.py", args.experiment, "--jobs", str(jobs)]
        if args.datasets:
            cmd += ["--datasets", *args.datasets]
        if args.install:
            cmd += ["--install", args.install]
        if run(cmd, log) != 0:
            sys.exit(f"reconstruction failed (log {log})")

    # 1b. integrity: a truncated output or an error in a log stops the chain before any number is computed
    failures = integrity(exp, datasets, args.reference, profile)
    if failures:
        for f in failures[:20]:
            print(f"INTEGRITY FAIL: {f}")
        sys.exit("integrity check failed: remove the listed outputs and reconstruct them alone; the verdict waits")
    if args.integrity_only:
        return
    if args.lean:
        # Phase 4 (loop v4): no gates, guards, plots or capybara views; the truth match on D4 (and D1), and the
        # calibration refit when the run includes the D2 / D3 guns. 460 / 441 / 417 / 461 follow by hand.
        run(uv + [SCRIPTS / "410_truth_match.py", name, "--datasets", *[d for d in datasets if d.startswith(("D1", "D2", "D3", "D4"))]], log)
        if {"D2_photon", "D3_neutron"} <= set(datasets):
            run(uv + [SCRIPTS / "420_refit_calibration.py", name], log)
        print(f"lean chain done for {name} (log {log})")
        return

    # 2. the gate on every DIS sample (the loop file: G4 runs on the DIS outputs; on the guns a ZDC-only
    #    change cannot reach a non-ZDC leaf that the DIS events, which fill every detector, would not show)
    gate_ok = True
    for ds in [d for d in datasets if d in dcfg.dis.samples]:
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
    compared = [d for d in datasets if d in dcfg.dis.samples]
    if not compared:
        print("gate G4: no DIS dataset in this launch — G4 static (loop rule 4); nothing compared, no PASS claimed")
    else:
        print(f"gate G4: {'PASS' if gate_ok else 'FAIL'} ({', '.join(compared)} against {args.reference})")

    # 3. truth matching and the scoreboard, 4. plots (also when the gate failed: the numbers explain why)
    run(uv + [SCRIPTS / "410_truth_match.py", name] + (["--datasets", *[d for d in datasets if d.startswith(("D1", "D4"))]] if args.datasets else []), log)
    cmd = uv + [SCRIPTS / "400_scoreboard.py", name, "--compare", args.reference]
    if args.datasets:
        cmd += ["--datasets", *args.datasets]
    run(cmd)
    # 3b. per-clustering calibration refit (D-user-13, Q7 answer A): S2 scale is judged on the refit residuals
    if not args.datasets:  # partial runs truth-match only D1/D4
        run(uv + [SCRIPTS / "420_refit_calibration.py", name])
        # 3c. decay-z and cluster-shape views (D-user-15): space/perf/shape-<name>.json and plots
        run(uv + [SCRIPTS / "430_shape_decayz.py", name, "--phase", args.phase, "--compare", args.reference])
    run(uv + [SCRIPTS / "200_cluster_distributions.py", args.reference, name, "--phase", f"{args.phase}/{name}"])
    run(["bash", SCRIPTS / "401_benchmark_plots.sh", name, "--phase", args.phase], log)
    # 4b. every plot a PNG (D-user-22): the benchmark copies and ROOT macros write PDF; a PNG per page beside each
    run(["bash", SCRIPTS / "701_pdf_to_png.sh", repo_path("space", "plots", args.phase, name)], log)
    # 4c. the gate table (D-user-22): what G4 compared, as numbers in space/perf/gate-evidence.json
    run(uv + [SCRIPTS / "442_gate_evidence.py", name])

    # 5. the ledger stub
    if not args.datasets:
        stub = (f"\n--- after the run ({date.today().isoformat()}) ---\n"
                f"row: metrics-{name}.json (scoreboard.csv, experiment={name})\n"
                f"result: <fill from the deltas printed by 400_scoreboard.py --compare {args.reference}>\n"
                f"guards: G4 {'PASS' if gate_ok else 'FAIL'}; S2 after refit <space/perf/calib-{name}.json residuals in ±limit / out>; S3 raw sum <drop ≤ 5 % / out>; S4b <...>; G1..G3 <in band / explained: ...>\n"
                f"verdict: {'REJECTED (gate G4)' if not gate_ok else '<ACCEPTED | REJECTED | INCONCLUSIVE>, one line why'}\n"
                f"understanding: <...>\nnext: <...>\n")
        with open(repo_path("space", "EXPERIMENTS.md"), "a") as fh:
            fh.write(stub)
        print("ledger stub appended to space/EXPERIMENTS.md; fill verdict/understanding/next")
    sys.exit(0 if gate_ok else 1)


if __name__ == "__main__":
    main()
