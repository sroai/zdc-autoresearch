#!/usr/bin/env python3
"""Reconstruct the datasets of one experiment config with eicrecon.

An experiment file (configs/experiments/<name>.yaml) names the EICrecon commit
whose install to use, the JANA parameter overrides (`-P<factory>:<param>=<value>`),
the datasets and the output collections. For every input file of every dataset
this script runs one eicrecon inside the pinned image and writes
{reco_root}/<experiment>/<dataset>/<stem>.edm4eic.root, with the full command
line and the wall time in <stem>.json beside it. Existing outputs are skipped
(resume); --force redoes them. Wall seconds per 1000 events (the T line of the
scoreboard) are appended to {reco_root}/<experiment>/timing.csv.

Usage:
  uv run scripts/120_reconstruct.py configs/experiments/R0_stock.yaml
  uv run scripts/120_reconstruct.py configs/experiments/E03_nhits5.yaml --datasets D1_pi0 D4_lambda
  uv run scripts/120_reconstruct.py configs/experiments/R0_stock.yaml --install /data/zdc-autoresearch/install/eicrecon-E12 --jobs 8
  uv run scripts/120_reconstruct.py ... --nevents 50 --dry-run

The install defaults to {install_root}/eicrecon-<eicrecon_ref[:12]>; a code
experiment passes its own label with --install. The detector configuration per
dataset comes from configs/datasets.yaml (guns: detector_config_guns; dis:
detector_config_dis; msf: the dataset's own detector_config).
"""
import argparse
import csv
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import REPO_ROOT, datasets_config, install_dir, load_profile, load_yaml, metrics_config, repo_path  # noqa: E402
from zdc.edm import n_events  # noqa: E402

WRAPPER = repo_path("scripts", "100_in_container.sh")


def to_container(path, profile):
    return str(path).replace(str(REPO_ROOT), profile.repo_mount, 1).replace(str(profile.data_root), profile.data_mount, 1)


def detector_config_for(dataset_id, dcfg):
    if dataset_id in dcfg.guns:
        return dcfg.detector_config_guns
    if dataset_id in dcfg.dis.samples:
        return dcfg.detector_config_dis
    if dataset_id in dcfg.msf:
        return dcfg.msf[dataset_id].detector_config
    raise SystemExit(f"dataset {dataset_id} is not in configs/datasets.yaml")


def parameter_flags(exp):
    flags = []
    for key, value in (exp.get("parameters") or {}).items():
        flags.append(f"-P{key}={value}")
    return flags


def run_one(profile, exp, install_c, dataset_id, detector_config, infile, outdir, args):
    stem = infile.name.replace(".edm4hep.root", "")
    out = outdir / f"{stem}.edm4eic.root"
    meta = outdir / f"{stem}.json"
    if out.exists() and out.stat().st_size > 0 and not args.force:
        return stem, "exists", None
    # podio:output_collections entries are regular expressions; ".*" means everything.
    collections = ",".join(exp.output_collections) if exp.get("output_collections") else ".*"
    frozen = set(metrics_config().get("frozen_parameters", []))
    leaked = [k for k in (exp.get("parameters") or {}) if k in frozen]
    if leaked:
        sys.exit(f"experiment {exp.name} sets frozen parameters {leaked} (zdc-setup.md, Noise and significance)")
    cmd = ["eicrecon", f"-Ppodio:output_file={to_container(out, profile)}",
           f"-Ppodio:output_collections={collections}", "-Pjana:warmup_timeout=600", "-Pjana:timeout=600",
           f"-Pjana:nthreads={int(exp.get('nthreads', 1))}",   # single-threaded by default: deterministic output for G4
           *parameter_flags(exp)]
    if args.nevents:
        cmd.append(f"-Pjana:nevents={args.nevents}")
    cmd.append(to_container(infile, profile))
    shell = f"export DETECTOR_CONFIG={detector_config}; " + " ".join(cmd)
    if args.dry_run:
        print(f"[dry-run] {stem}: EICRECON_INSTALL={install_c} {shell}")
        return stem, "dry-run", None
    log = Path(profile.logs_root) / "reco" / exp.name / f"{dataset_id}_{stem}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    env = {"EICRECON_INSTALL": install_c, "ZDC_CONFIG": str(Path(args.profile_path))} if args.profile_path else {"EICRECON_INSTALL": install_c}
    start = time.time()
    with open(log, "w") as lf:
        rc = subprocess.call([str(WRAPPER), "bash", "-c", shell], stdout=lf, stderr=subprocess.STDOUT, env={**dict(__import__("os").environ), **env})
    wall = time.time() - start
    if rc != 0 or not out.exists():
        return stem, f"FAILED (rc={rc}, log {log})", None
    events = int(n_events(out))
    meta.write_text(json.dumps({"experiment": exp.name, "dataset": dataset_id, "input": str(infile), "output": str(out),
                                "install": install_c, "detector_config": detector_config, "command": shell,
                                "events": events, "wall_s": round(wall, 2)}, indent=1))
    return stem, "ok", (events, wall)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment", help="configs/experiments/<name>.yaml")
    ap.add_argument("--datasets", nargs="*", help="subset of the experiment's datasets")
    ap.add_argument("--install", help="install prefix (host path); default from eicrecon_ref")
    ap.add_argument("--jobs", type=int, help="parallel eicrecon processes (default: profile cores / 2)")
    ap.add_argument("--nevents", type=int, help="limit events per file (smoke runs)")
    ap.add_argument("--force", action="store_true", help="redo existing outputs")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    args.profile_path = __import__("os").environ.get("ZDC_CONFIG")

    profile = load_profile()
    dcfg = datasets_config()
    exp = load_yaml(args.experiment)
    install = Path(args.install) if args.install else install_dir(profile, exp.eicrecon_ref)
    if not install.exists() and not args.dry_run:
        sys.exit(f"install not found: {install} (scripts/102_build_eicrecon.sh --ref {exp.eicrecon_ref})")
    install_c = to_container(install, profile)
    datasets = args.datasets or list(exp.datasets)
    jobs = args.jobs or max(1, int(profile.cores) // 2)

    work = []
    for ds in datasets:
        indir = Path(profile.datasets_root) / ds
        files = sorted(indir.glob("*.edm4hep.root"))
        if not files:
            sys.exit(f"no inputs under {indir} (Phase 0 generates/fetches them)")
        outdir = Path(profile.reco_root) / exp.name / ds
        outdir.mkdir(parents=True, exist_ok=True)
        for f in files:
            work.append((ds, detector_config_for(ds, dcfg), f, outdir))
    print(f"{exp.name}: {len(work)} file(s) over {len(datasets)} dataset(s), {jobs} parallel, install {install}")

    timing = Path(profile.reco_root) / exp.name / "timing.csv"
    results = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futs = [pool.submit(run_one, profile, exp, install_c, ds, dc, f, od, args) for ds, dc, f, od in work]
        for (ds, _, f, _), fut in zip(work, futs):
            stem, status, t = fut.result()
            print(f"{status:10s} {ds}/{stem}")
            results.append((ds, stem, status, t))
    failed = [r for r in results if r[2].startswith("FAILED")]
    if not args.dry_run:
        new = not timing.exists()
        with open(timing, "a", newline="") as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(["dataset", "file", "events", "wall_s", "s_per_1000"])
            for ds, stem, status, t in results:
                if t:
                    w.writerow([ds, stem, t[0], round(t[1], 2), round(1000 * t[1] / max(t[0], 1), 2)])
    if failed:
        print(f"ERROR: {len(failed)} reconstruction(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
