#!/usr/bin/env python3
"""Simulate the DIS guard inputs D5 (configs/datasets.yaml, section dis) with npsim.

Each sample is one EVGEN file on JLab XRootD, read in place by npsim and cut
into chunks of `events_per_chunk` events (--skipNEvents), one npsim process per
chunk with seed `seed_base + chunk`, on the full detector `detector_config_dis`.
Outputs: {datasets_root}/<sample>/<sample>_chunkNNN.edm4hep.root, written as
.part and renamed on success, so a rerun resumes and skips finished chunks.
Logs: {logs_root}/sim/<sample>_chunkNNN.log. At the end the manifest section
`dis` of space/perf/manifest-datasets.json is rewritten.

Usage:
  uv run scripts/113_simulate_dis.py                    # every sample, all configured chunks
  uv run scripts/113_simulate_dis.py --only D5_dis_minq2_0 --chunks 20 --jobs 20

The sample size is set in ZDC clusters, not events: after a first production,
count R0 clusters (scripts/120_reconstruct.py, then the cluster count) and raise
`chunks` in the config until `min_clusters` is met.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import datasets_config, load_profile, repo_path  # noqa: E402

WRAPPER = repo_path("scripts", "100_in_container.sh")


def run_chunk(profile, dis, detector_config, sample_id, sample, chunk):
    out_dir = Path(profile.datasets_root) / sample_id
    logs = Path(profile.logs_root) / "sim"
    out_dir.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    stem = f"{sample_id}_chunk{chunk:03d}"
    final = out_dir / f"{stem}.edm4hep.root"
    partial = out_dir / f"{stem}.part.edm4hep.root"
    if final.exists():
        return stem, "exists"
    n = int(dis.events_per_chunk)
    # The data root keeps its host path inside the container (data_mount), so host paths work as they are.
    cmd = (f"set -e; npsim --compactFile $DETECTOR_PATH/{detector_config}.xml "
           f"--inputFiles {dis.xrootd}/{sample.evgen} --skipNEvents {chunk * n} -N {n} "
           f"--random.seed {int(dis.seed_base) + chunk} --outputFile {partial} -v WARNING && mv {partial} {final}")
    with open(logs / f"{stem}.log", "w") as log:
        rc = subprocess.call([str(WRAPPER), "bash", "-c", cmd], stdout=log, stderr=subprocess.STDOUT)
    return stem, "ok" if rc == 0 and final.exists() else f"FAILED (rc={rc}, log {logs / (stem + '.log')})"


def main():
    sys.stdout.reconfigure(line_buffering=True)  # progress lines reach the log as they happen under nohup
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", action="append", help="sample id(s) (default: all)")
    ap.add_argument("--chunks", type=int, help="override the chunk count of every selected sample")
    ap.add_argument("--jobs", type=int, help="parallel npsim processes (default: profile cores)")
    args = ap.parse_args()
    profile, cfg = load_profile(), datasets_config()
    dis = cfg.dis
    samples = {k: v for k, v in dis.samples.items() if not args.only or k in args.only}
    work = [(sid, s, c) for sid, s in samples.items() for c in range(args.chunks or int(s.chunks))]
    jobs = args.jobs or int(profile.cores)
    print(f"{len(work)} chunks, {jobs} parallel", flush=True)
    failed = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for stem, status in pool.map(lambda w: run_chunk(profile, dis, cfg.detector_config_dis, *w), work):
            print(f"{status:10s} {stem}", flush=True)
            if status.startswith("FAILED"):
                failed.append(stem)
    if failed:
        sys.exit(f"ERROR: {len(failed)} chunk(s) failed: {failed}")
    manifest = repo_path("space", "perf", "manifest-datasets.json")
    subprocess.check_call([sys.executable, str(repo_path("scripts", "121_manifest.py")), "write", str(manifest),
                           *[str(Path(profile.datasets_root) / sid) for sid in samples], "--section", "dis"])


if __name__ == "__main__":
    main()
