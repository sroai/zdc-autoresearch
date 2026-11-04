---
name: ifarm-slurm
description: Submit, monitor and collect Slurm batch jobs (sbatch arrays running eic_xl containers) on the JLab farm through the ifarm tunnel, and every quirk that bit this user there - tcsh login shell, srun eating stdin, logs never on /work, 2 GB/CPU, no /tmp scratch, --gres=disk for /scratch, array throttle, /farm_out purge, schema-matched images, xrootd host. Use for "submit on the farm", "run the array", "re-reconstruct on ifarm", "check my jobs", "collect results", or any sbatch/squeue/sacct question. Interactive --overlap steps on a node the user allocated are the ifarm-tunnel skill.
---

# Batch jobs on the JLab farm

You reach ifarm through the user's tunnel (`ssh -p 4333 -o BatchMode=yes
romanov@localhost`, the ifarm-tunnel skill). Batch work needs no interactive
allocation: you write a job script into the program's farm directory, submit
it from the login node, poll `squeue`/`sacct`, and collect the small outputs.
Paths come from `zdc-setup.md` (section Farm); the values below are its
defaults. The user has been sanctioned by the farm admins before: the rules
in sections 3 and 4 are hard constraints, not style.

## 1. Fixed facts

| | |
|---|---|
| account / partitions | `--account=eic`; `production` (4 d) for CPU, `gpu` (10 d), `priority` (1 d, quick tests), `scavenger` (4 d). Labels are 2025; `sinfo -s` is the truth |
| code on farm | `/work/eic3/users/romanov/zdc-autoresearch` (rsync mirror of the repo, `.git/` excluded) |
| job scripts | `/work/eic3/users/romanov/zdc-autoresearch-out/<run>/jobs/` |
| bulky outputs | `/volatile/eic/romanov/zdc-autoresearch/<run>/` (ROOT; purgeable without notice) |
| small results | `/work/eic3/users/romanov/zdc-autoresearch-out/<run>/` (json, csv, png, gz logs) |
| Slurm logs | `/farm_out/romanov/zdc-autoresearch/<run>/` — **never on /work**; purged after a few days |
| image | `/cvmfs/singularity.opensciencegrid.org/eicweb/eic_xl:<tag from zdc-setup.md>` |
| MSF inputs | `/work/eic3/users/romanov/meson-structure-2026-07/dd4hep/<energy>/msf_ev1000_NNNN.edm4hep.root` (read-only) |

## 2. The shapes

### 2.1 Every farm command: bash on stdin

The login shell is tcsh. Bash syntax passed as an argument fails with
`Illegal variable name`. Always:

```bash
ssh -p 4333 -o BatchMode=yes romanov@localhost bash -s <<'REMOTE'
squeue --me -h -o '%i %j %T %M %r' | head -20
REMOTE
```

A distinctive delimiter (`REMOTE`) keeps heredocs inside the payload from
colliding. Full paths everywhere; the login node is for `sbatch`, `squeue`,
`sacct`, `ls`, `rsync`, `sed`, nothing heavier.

### 2.2 Writing a job script

Generate the script locally from `scripts/5xx_*` (so it is in the repo and
reviewable), rsync it to the farm (ifarm-tunnel Rule 3), submit from the
login node. The known-good array shape (from
`msf-simulation-pipeline/simulation_pipeline/job_creator.py`, verified in
the 2026-07 and 2026-10 campaigns):

```bash
#!/bin/bash
#SBATCH --account=eic
#SBATCH --partition=production
#SBATCH --job-name=zdc-<run>
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=2G
#SBATCH --gres=disk:20G
#SBATCH --output=/farm_out/romanov/zdc-autoresearch/<run>/array_%A_%a.log
#SBATCH --error=/farm_out/romanov/zdc-autoresearch/<run>/array_%A_%a.err
set -uo pipefail                       # no set -e: one bad file must not kill the chunk
OUT=/volatile/eic/romanov/zdc-autoresearch/<run>
SMALL=/work/eic3/users/romanov/zdc-autoresearch-out/<run>
IMG=/cvmfs/singularity.opensciencegrid.org/eicweb/eic_xl:<tag>
save_logs() { mkdir -p "$SMALL/logs"; for f in /farm_out/romanov/zdc-autoresearch/<run>/array_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.{log,err}; do [ -f "$f" ] && gzip -c "$f" > "$SMALL/logs/$(basename "$f").gz"; done; }
trap save_logs EXIT; trap 'exit 143' TERM INT HUP
TASK=$((SLURM_ARRAY_TASK_ID + ${OFFSET:-0}))
STAGE=$(mktemp -d -p "${TMPDIR:?TMPDIR unset}" zdc.XXXX); trap 'rm -rf "$STAGE"; save_logs' EXIT
n_fail=0
for LINE in $(seq $((TASK*FILES_PER_TASK+1)) $(((TASK+1)*FILES_PER_TASK))); do
  IN=$(sed -n "${LINE}p" "$SMALL/jobs/inputs.list"); [ -n "$IN" ] || break
  NAME=$(basename "$IN" .edm4hep.root)
  [ -s "$OUT/$NAME.edm4eic.root" ] && continue             # idempotent: resubmits fast-forward
  cp "$IN" "$STAGE/" || { n_fail=$((n_fail+1)); continue }  # read /work once, work on node disk
  singularity exec -B /work/eic3/users/romanov:/work/eic3/users/romanov:ro -B "$OUT:$OUT" -B "$STAGE:$STAGE" -B /farm_out/romanov:/farm_out/romanov "$IMG" \
    bash -c "source /opt/detector/epic-main/bin/thisepic.sh && <PATH/LD_LIBRARY_PATH/JANA_PLUGIN_PATH for the custom EICrecon install> && /usr/bin/time -v eicrecon <flags> -Ppodio:output_file=$STAGE/$NAME.edm4eic.root $STAGE/$NAME.edm4hep.root" \
    || { n_fail=$((n_fail+1)); continue; }
  mv "$STAGE/$NAME.edm4eic.root" "$OUT/$NAME.edm4eic.root.part" && mv "$OUT/$NAME.edm4eic.root.part" "$OUT/$NAME.edm4eic.root"
  rm -f "$STAGE/$NAME".*
done
[ "$n_fail" -eq 0 ]
```

Why each line is there:

- `#SBATCH` lines flush-left: Slurm silently ignores an indented directive
  (bit on 2026-09-30, `--gres=disk` never registered).
- `--gres=disk:NNG`: without it the per-job `/scratch` has a quota of ~0
  (`df` shows 4K, ENOSPC with 724G free). Size it at input + output +
  headroom. Some nodes have 8 GB scratch.
- `$TMPDIR` is set by Slurm to `/scratch/slurm/<jobid>/…`; `SLURM_TMPDIR` is
  NOT set on this farm, so `${SLURM_TMPDIR:-/tmp}` silently falls to `/tmp`,
  which is forbidden. Never `mktemp -d` without `-p`.
- Logs under `/farm_out`, gzip-copied once into the small-results tree at
  exit because `/farm_out` is purged after a few days.
- Deliverables are written atomically (`.part` then rename) so an existing
  file is complete and completeness is countable:
  `ls $OUT/*.edm4eic.root | wc -l` against the input count.
- Several files per task so a task runs minutes, not seconds (admins flag
  floods of sub-2-minute jobs).
- `MaxArraySize` is 10001: at most 10000 tasks per `sbatch --array`; bigger
  sets go in chunks with `--export=ALL,OFFSET=<n>`.
- The container's EIC environment is loaded by `thisepic.sh` inside the
  payload; the custom EICrecon build (section 5) is prepended after it.
- `set -e` is absent on purpose; the final `[ "$n_fail" -eq 0 ]` still shows
  the task FAILED in `sacct`.

### 2.3 Submitting

```bash
ssh -p 4333 -o BatchMode=yes romanov@localhost bash -s <<'REMOTE'
cd /work/eic3/users/romanov/zdc-autoresearch-out/<run>/jobs || exit 1
mkdir -p /farm_out/romanov/zdc-autoresearch/<run> /volatile/eic/romanov/zdc-autoresearch/<run>
sbatch --array=0-<N-1>%16 --export=ALL,OFFSET=0,FILES_PER_TASK=<k> array.slurm.sh
squeue --me -h -o '%j' | sort | uniq -c
REMOTE
```

- `%16` is the self-imposed throttle. The admin cap of 10 running jobs was
  lifted (verified 2026-10-03) but campaign arrays were admin-cancelled on
  2026-09-29 for saturating the eic file server (205 tasks at once) and the
  account was limited to one running job. Keep `%16` (the background program
  used `%8`); more concurrency is a question to the user, never a default.
- Print the job id into the LIVE block of STATUS.md the moment it is submitted.
- A **smoke task first**: `--array=0-0` on one file, check the output and
  `sacct` memory, then submit the rest. A refused submission with a limit
  message: stop and report it verbatim; the jobLimit list
  (https://scicomp.jlab.org/scicomp/slurmJob/jobLimit) is the strike.

### 2.4 Monitoring

```bash
ssh -p 4333 -o BatchMode=yes romanov@localhost bash -s <<'REMOTE'
squeue --me -h -o '%i %j %T %M %r' | head
sacct -j <jobid> -X --format=State | sort | uniq -c                                   # census
sacct -j <jobid> --units=G --format=JobID,JobName,ReqMem,MaxRSS,Elapsed,State | head # sizing
ls /volatile/eic/romanov/zdc-autoresearch/<run>/*.edm4eic.root 2>/dev/null | wc -l   # deliverables
zcat /work/eic3/users/romanov/zdc-autoresearch-out/<run>/logs/array_<jid>_<task>.err.gz | tail -20
REMOTE
```

- Pending reasons `AssocMaxJobsLimit` / `QOSMaxJobs` in `squeue -t PENDING
  -o %r` mean a cap; do not work around it.
- `sacct` State says only FAILED; the per-task gz log says why. A handful of
  FAILED tasks in a conversion array is usually bad source files, not code:
  campaign files can be truncated and still look a normal size (a 144 MB
  file holding 32 of 5000 entries). Check entry counts, never sizes.
- Poll at most every few minutes; a monitor loop in your context dies with
  the session, so the LIVE block carries the job id and what to check first.

### 2.5 Collecting

Small results: ifarm-tunnel Rule 3 (rsync of `zdc-autoresearch-out/`).
Bulky ROOT stays on `/volatile`; the analysis scripts run on the farm
(section 2.2 shape, one task) and write small files; pull single ROOT files
only for inspection, one at a time with `scp -P 4333`.

## 3. Resource rules (admin notices 2026-07-12, 2026-07-29, 2026-09-29)

1. **Logs never on `/work`** — streaming logs overloaded the eic work file
   server; the account was limited to one running job for it.
2. **2 GB per CPU is the provisioned default.** More memory bills extra CPUs
   (`--mem=5G` → 2 CPUs) and idles nodes; 383 jobs were once flagged at under
   0.6 % memory use. Measure first (`/usr/bin/time -v`, `sacct MaxRSS`),
   request peak + ~20 %. Above 4 GB/CPU: ask the user.
3. **The offense is idle resources, not big requests.** A job that needs
   5 GB/CPU requests 5 GB/CPU; a job that holds a node and waits is the sin.
4. **No scratch in `/tmp`**, in jobs or interactively on ifarm (admins deleted
   stray dirs). Node `/tmp` is an 8 GB volume anyway.
5. **Never `$PWD` for paths**: jobs start in the submit directory; a
   `$PWD`-scratch campaign littered hundreds of job dirs into a repo.
6. **Read each input once** (stage to node disk), throttle arrays, keep tasks
   minutes long.
7. **`/volatile` is for bulky files only**, and can be purged; anything that
   must survive goes to `/work` (small) with the user's OK.

## 4. Never

- Never `scancel` a job you did not submit this run; never `salloc`; never a
  bare `srun` without `--jobid`; never submit more than one array per run
  without the user's word; never raise the throttle above `%16`.
- Never write outside the program's four farm paths (section 1); never delete
  under them without asking; never touch `/mss`, `jcache` (tape staging) or
  other users' directories unless the user asks.
- Never run reconstruction on the login node. Never leave a job running and
  end the run without the job id in STATUS.md LIVE.

## 5. Custom EICrecon on the farm

Two ways, pick by what the loop file says:

- **Install prefix on `/work`** (default): build once inside the pinned image
  on an interactive node (ifarm-tunnel Rule 2, `cmake -B build -S
  submodules/EICrecon -DCMAKE_INSTALL_PREFIX=$U/zdc-autoresearch-out/install-<sha>`,
  30 to 60 minutes, never cancel), then every job prepends
  `PATH=$PREFIX/bin:$PATH LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH
  JANA_PLUGIN_PATH=$PREFIX/lib/EICrecon/plugins:$JANA_PLUGIN_PATH` after
  `thisepic.sh`. Parameter-only experiments need no rebuild: they are
  `-P<factory>:<param>=<value>` flags on the command line.
- **A `.sif` built FROM `eic_xl`** with `singularity build --fakeroot` (recipe
  in `submodules/meson-structure/docs/tutorials/ifarm.md`): heavier, used when
  an install prefix cannot be bound.

The image release must match the data schema: campaign 26.07 edm4eic files
(schema 81000) are silently unreadable in 26.06 containers — collections are
absent, no error. The pin in `zdc-setup.md` is the one image for simulation,
reconstruction and analysis of this program.

## 6. Data access without the farm

- XRootD host: `root://dtn2304.jlab.org:8443//jlab-osdf-ro/eic/EPIC/{volatile,cache,work}/…`
  (`dtn-eic.jlab.org` is retired; docs that name it are stale). Needs a 5.9+
  client (`eic_xl` has it; set `X509_CERT_DIR=/etc/ssl/certs` elsewhere).
- `/work/eic3/users/romanov` is **not** exported over XRootD: the MSF campaign
  files are reachable only on the farm or by `scp -P 4333` through the tunnel.
- Rucio is a partial index; absence there means "not registered".

## 7. When something fails

| symptom | cause → action |
|---|---|
| `Illegal variable name` | bash reached tcsh → bash on stdin (2.1) |
| later lines of a script never ran | an `srun` without `--input=none` ate stdin |
| `ENOSPC` with free space on `df /` | no `--gres=disk` → add it |
| `EROFS: mkdir '/scratch'` | ROOT on the login node → `env TMPDIR=<writable>` |
| `TFile::Open … does not exist` inside the container | the path is not bound → add `-B` |
| collections silently missing in a file | image release older than the file's schema → the pinned image |
| `remote port forwarding failed`, tunnel refused, `Permission denied` | the user's tunnel is down → stop and tell the user |
| submission refused with a limit message | jobLimit strike → stop, report verbatim |
| `Login failed: Got invalid login response` (xrootd) | client < 5.9 or no CA dir → `eic_xl`, `X509_CERT_DIR` |
