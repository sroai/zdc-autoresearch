#!/usr/bin/env python3
"""Write the Slurm array job for re-reconstructing MSF files on ifarm (D6b, Phase 4).

Produces, under out/farm/<experiment>-<energy>/: `inputs.list` (one DD4hep file
per line), `array.slurm.sh` (the shape of the ifarm-slurm skill: logs on
/farm_out, 2G/CPU, --gres=disk, node-local staging, atomic deliverables,
gzip-copied logs, no set -e) and `submit.sh` with the exact sbatch line. Nothing
is submitted by this script: rsync the folder to the farm (ifarm-tunnel Rule 3)
and submit from the login node (ifarm-slurm 2.3), smoke task first.

Usage:
  uv run scripts/500_farm_array.py configs/experiments/R0_stock.yaml --energy 9x275 --files 100
  uv run scripts/500_farm_array.py configs/experiments/E07_best.yaml --energy 9x130 --files 100 --install /work/eic3/users/romanov/zdc-autoresearch-out/install/eicrecon-E07

The input list is generated from the farm path pattern in configs/datasets.yaml
(msf.D6b_farm) by index, because the farm directory is not visible from here;
the smoke task checks the first file exists. The custom EICrecon install on the
farm is built once with scripts/102_build_eicrecon.sh through the ifarm-tunnel
skill (ZDC_CONFIG=configs/ifarm.yaml), and its prefix is passed with --install.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import datasets_config, load_yaml, repo_path  # noqa: E402


def parameter_flags(exp):
    return " ".join(f"-P{k}={v}" for k, v in (exp.get("parameters") or {}).items())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment")
    ap.add_argument("--energy", required=True, help="9x275 | 9x130 | 9x100 | 5x41")
    ap.add_argument("--files", type=int, default=100)
    ap.add_argument("--first-index", type=int, default=0)
    ap.add_argument("--install", required=True, help="EICrecon install prefix ON THE FARM")
    ap.add_argument("--files-per-task", type=int)
    args = ap.parse_args()
    exp = load_yaml(args.experiment)
    farm = load_yaml(repo_path("configs", "ifarm.yaml"))
    dcfg = datasets_config()
    msf = dcfg.msf.D6b_farm
    s = farm.slurm
    per_task = args.files_per_task or int(s.files_per_task)
    run = f"{exp.name}-{args.energy}"
    out = repo_path("out", "farm", run)
    out.mkdir(parents=True, exist_ok=True)
    inputs = [f"{msf.dd4hep_root}/{args.energy}/msf_ev1000_{i:04d}.edm4hep.root" for i in range(args.first_index, args.first_index + args.files)]
    (out / "inputs.list").write_text("\n".join(inputs) + "\n")
    n_tasks = (len(inputs) + per_task - 1) // per_task
    detector_config = f"epic_craterlake_{args.energy}"
    reco_out = f"{farm.reco_root}/{exp.name}/{args.energy}"
    small = f"{farm.small_results_root}/{run}"
    logs = f"{farm.logs_root}/{run}"
    flags = parameter_flags(exp)
    script = f"""#!/bin/bash
#SBATCH --account={s.account}
#SBATCH --partition={s.partition}
#SBATCH --job-name=zdc-{run}
#SBATCH --time={s.time}
#SBATCH --cpus-per-task={s.cpus_per_task}
#SBATCH --mem-per-cpu={s.mem_per_cpu}
#SBATCH --gres=disk:{s.gres_disk}
#SBATCH --output={logs}/array_%A_%a.log
#SBATCH --error={logs}/array_%A_%a.err
set -uo pipefail                       # no set -e: one bad file must not kill the chunk
OUT={reco_out}
SMALL={small}
IMG={farm.image}
INSTALL={args.install}
FILES_PER_TASK=${{FILES_PER_TASK:-{per_task}}}
mkdir -p "$OUT" "$SMALL/logs"
save_logs() {{ for f in {logs}/array_${{SLURM_ARRAY_JOB_ID}}_${{SLURM_ARRAY_TASK_ID}}.log {logs}/array_${{SLURM_ARRAY_JOB_ID}}_${{SLURM_ARRAY_TASK_ID}}.err; do [ -f "$f" ] && gzip -c "$f" > "$SMALL/logs/$(basename "$f").gz"; done; }}
STAGE=$(mktemp -d -p "${{TMPDIR:?TMPDIR unset: no node scratch}}" zdc.XXXX)
trap 'rm -rf "$STAGE"; save_logs' EXIT; trap 'exit 143' TERM INT HUP
TASK=$((SLURM_ARRAY_TASK_ID + ${{OFFSET:-0}}))
n_fail=0
for LINE in $(seq $((TASK*FILES_PER_TASK+1)) $(((TASK+1)*FILES_PER_TASK))); do
  IN=$(sed -n "${{LINE}}p" "$SMALL/jobs/inputs.list"); [ -n "$IN" ] || break
  NAME=$(basename "$IN" .edm4hep.root)
  [ -s "$OUT/$NAME.edm4eic.root" ] && continue
  [ -s "$IN" ] || {{ echo "ERROR missing input $IN"; n_fail=$((n_fail+1)); continue; }}
  cp "$IN" "$STAGE/" || {{ echo "ERROR staging $IN"; n_fail=$((n_fail+1)); continue; }}
  singularity exec -B /work/eic3/users/romanov:/work/eic3/users/romanov:ro -B "$OUT:$OUT" -B "$STAGE:$STAGE" -B /farm_out/romanov:/farm_out/romanov "$IMG" bash -c "
    source /opt/detector/epic-main/bin/thisepic.sh
    export PATH=$INSTALL/bin:\\$PATH LD_LIBRARY_PATH=$INSTALL/lib:\\$LD_LIBRARY_PATH JANA_PLUGIN_PATH=$INSTALL/lib/EICrecon/plugins:\\${{JANA_PLUGIN_PATH:-}}
    export DETECTOR_CONFIG={detector_config}
    /usr/bin/time -v eicrecon {flags} -Ppodio:output_file=$STAGE/$NAME.edm4eic.root $STAGE/$NAME.edm4hep.root" \\
    || {{ echo "ERROR eicrecon failed on $NAME"; n_fail=$((n_fail+1)); rm -f "$STAGE/$NAME".*; continue; }}
  mv "$STAGE/$NAME.edm4eic.root" "$OUT/$NAME.edm4eic.root.part" && mv "$OUT/$NAME.edm4eic.root.part" "$OUT/$NAME.edm4eic.root"
  rm -f "$STAGE/$NAME".*
done
[ "$n_fail" -eq 0 ]
"""
    (out / "array.slurm.sh").write_text(script)
    submit = f"""#!/bin/bash
# Run ON IFARM from {small}/jobs (rsync this folder there first). Smoke task first, then the rest.
mkdir -p {logs} {reco_out}
sbatch --array=0-0 array.slurm.sh                      # smoke: one task; check $OUT and sacct MaxRSS before the rest
# sbatch --array=1-{n_tasks - 1}%{s.throttle} array.slurm.sh   # the rest, throttled
"""
    (out / "submit.sh").write_text(submit)
    print(f"wrote {out}/: inputs.list ({len(inputs)} files), array.slurm.sh ({n_tasks} tasks of {per_task}), submit.sh")
    print(f"farm job dir: {small}/jobs  (rsync {out}/ there); outputs {reco_out}; logs {logs}")


if __name__ == "__main__":
    main()
