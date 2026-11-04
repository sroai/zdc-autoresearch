---
name: ifarm-tunnel
description: Run commands on the JLab ifarm login node, and Slurm --overlap steps inside the eic_xl apptainer image on a node the user allocated, through the user's ssh tunnel on localhost:4333 with the user's own key. Use when the user says "on the farm", "on ifarm", "through the tunnel", or when a step needs farm data under /work/eic3 or /volatile. Batch submission (sbatch arrays, collecting results) is the ifarm-slurm skill.
---

# Run work on the JLab farm through the ifarm tunnel

You run on the user's machine. The farm cannot reach the internet. You reach
ifarm through the user's tunnel with the user's own key, so you *could* run
anything there — you use only the shapes below. The human-side setup
(tunnel, interactive allocation) is in `docs/ifarm-tunnel.md`; you cannot do
those steps. Paths come from `zdc-setup.md` (section Farm); the values below
are its defaults.

## Fixed facts

| | |
|---|---|
| tunnel | `ssh -p 4333 -o BatchMode=yes romanov@localhost` |
| interactive job name | `zdc-node` — allocated by the user, found with `squeue` |
| image on farm | `/cvmfs/singularity.opensciencegrid.org/eicweb/eic_xl:<tag from zdc-setup.md>` |
| code on farm | `/work/eic3/users/romanov/zdc-autoresearch` (mirror of the local repo) |
| results on farm | `/work/eic3/users/romanov/zdc-autoresearch-out/<run>/` (small files) |
| bulky outputs | `/volatile/eic/romanov/zdc-autoresearch/<run>/` (ROOT; purgeable) |
| logs on farm | `/farm_out/romanov/zdc-autoresearch/<run>/` — **never on /work** |
| results locally | `out/<run>/` in the repo (git-ignored) |

## Rule 1 — ifarm's login shell is tcsh: scripts go on stdin, never as arguments

Login-node command (short things only: `squeue`, `sacct`, `ls`, `rsync`):

```bash
ssh -p 4333 -o BatchMode=yes romanov@localhost bash -s <<'REMOTE'
squeue --me -h -o '%i %j %T %M %R'
REMOTE
```

Use a distinctive heredoc delimiter (`REMOTE`) so heredocs inside the payload
do not collide. Never run reconstruction, simulation or a build on the login
node.

## Rule 2 — compute on a node: the step shape

```bash
ssh -p 4333 -o BatchMode=yes romanov@localhost bash -s <<'REMOTE'
JID=$(squeue --me -h -n zdc-node -t RUNNING -o %i | head -1)
[ -n "$JID" ] || { echo "NO zdc-node JOB RUNNING"; exit 1; }
U=/work/eic3/users/romanov
srun --input=none --jobid=$JID --overlap apptainer exec \
  -B $U:$U:ro \
  -B $U/zdc-autoresearch:$U/zdc-autoresearch \
  -B $U/zdc-autoresearch-out:$U/zdc-autoresearch-out \
  -B /volatile/eic/romanov/zdc-autoresearch:/volatile/eic/romanov/zdc-autoresearch \
  -B /farm_out/romanov:/farm_out/romanov \
  --pwd $U/zdc-autoresearch \
  /cvmfs/singularity.opensciencegrid.org/eicweb/eic_xl:26.11.0-stable \
  bash -c 'source /opt/detector/epic-main/bin/thisepic.sh; hostname; eicrecon --version'
REMOTE
```

Replace only the `bash -c '...'` payload. Keep everything else:

- `--input=none` — without it `srun` forwards stdin to the step and **eats
  the rest of your script**; every line after the `srun` silently never runs.
- `--overlap` — without it the step blocks waiting for CPUs the allocation holds.
- the binds — the user's farm directory is read-only except the program's
  two dirs; `/volatile` and `/farm_out` are not bound by default. Do not add
  binds or drop `:ro`.
- `source thisepic.sh` inside the payload — the container's EIC environment
  is not loaded otherwise.
- `--nv` and `--gres=gpu:1` only when the allocation has a GPU.

## Rule 3 — push code before running, pull results after

```bash
rsync -a --delete --exclude='.git/' --exclude='build/' --exclude='data/' --exclude='out/' \
  --exclude='.venv/' --exclude='__pycache__/' --exclude='*.root' --exclude='.snakemake/' \
  -e 'ssh -p 4333 -o BatchMode=yes' ./ romanov@localhost:/work/eic3/users/romanov/zdc-autoresearch/
```

```bash
mkdir -p out && rsync -a --include='*/' --include='*.log' --include='*.json' --include='*.csv' \
  --include='*.txt' --include='*.png' --include='*.md' --exclude='*' \
  -e 'ssh -p 4333 -o BatchMode=yes' romanov@localhost:/work/eic3/users/romanov/zdc-autoresearch-out/ out/
```

ROOT output stays on the farm under `/volatile/eic/romanov/zdc-autoresearch/`.
Submodules are part of the code mirror; the first push moves ~1 GB.

## Rule 4 — long runs: keep the step open, background the ssh

A `nohup … &` **inside** an `srun --overlap` step dies the moment the step
exits — Slurm reaps the step's cgroup (hit 2026-09-30; the tell is apptainer
printing `INFO: Terminating squashfuse_ll after timeout … caused by a running
background process`). So for anything longer than ~2 minutes, keep the
command in the foreground of the step and put the whole ssh in the
background on your side, logging to `/farm_out`:

```bash
nohup ssh -p 4333 -o BatchMode=yes romanov@localhost bash -s > /data/zdc-autoresearch/logs/<run>.ssh.log 2>&1 <<'REMOTE' &
JID=$(squeue --me -h -n zdc-node -t RUNNING -o %i | head -1)
[ -n "$JID" ] || { echo "NO zdc-node JOB RUNNING"; exit 1; }
U=/work/eic3/users/romanov; RUN=<run>
mkdir -p /farm_out/romanov/zdc-autoresearch/$RUN $U/zdc-autoresearch-out/$RUN
srun --input=none --jobid=$JID --overlap apptainer exec <the binds of Rule 2> \
  /cvmfs/singularity.opensciencegrid.org/eicweb/eic_xl:26.11.0-stable \
  bash -c "source /opt/detector/epic-main/bin/thisepic.sh; /usr/bin/time -v <command> > /farm_out/romanov/zdc-autoresearch/$RUN/run.log 2>&1"
cp /farm_out/romanov/zdc-autoresearch/$RUN/run.log $U/zdc-autoresearch-out/$RUN/
REMOTE
```

One background launch per tool call. Then poll with
`tail -n 20 /farm_out/romanov/zdc-autoresearch/<run>/run.log` in a later
login-node command; the ssh exiting is the completion signal. The last line
copies the log once into `zdc-autoresearch-out/<run>/` so the Rule 3 pull
picks it up. `/usr/bin/time -v` is not optional: its `Maximum resident set
size` sizes the next request. Write the run in the LIVE block of STATUS.md
the moment it starts. Anything longer than a few hours is batch work: use
the ifarm-slurm skill instead.

## Farm rules — hard constraints from JLab admins

The user has been sanctioned by the farm admins before. These are not style.

1. **Use what was requested.** The offense is idle resources. 2 GB/CPU is the
   provisioned default; reconstruction may need more — measure first.
2. **Measure before asking for more.** Scaled-down run under `/usr/bin/time -v`;
   `sacct -j $JID --format=JobID,JobName,ReqMem,MaxRSS,Elapsed` after.
3. **Logs never on `/work`.** `/farm_out/romanov/zdc-autoresearch/` only.
4. **Don't leave a node busy and walk away.** Report what runs; never start a
   second long job on top of a running one without asking.
5. If a farm command is refused with a limit message, stop and report it
   verbatim (https://scicomp.jlab.org/scicomp/slurmJob/jobLimit is the strike).

## When something fails

- `ssh: connect to host localhost port 4333` refused/timeout, or
  `Permission denied` → the user's tunnel is down. **Stop and tell the user.**
  Do not retry in a loop.
- `NO zdc-node JOB RUNNING` → the allocation ended. Use batch (ifarm-slurm)
  or tell the user.
- The script's later lines never ran, no error → you dropped `--input=none`.
- `Illegal variable name` → bash syntax reached tcsh; you bypassed Rule 1.
- `EROFS: mkdir '/scratch'` → ROOT on the login node with `TMPDIR` in
  `/scratch`; pass `env TMPDIR=/work/eic3/users/romanov/zdc-autoresearch-out/tmp`.

## Never

- Never `scancel` a job you did not submit this run; never allocate
  interactive nodes (`salloc`, a bare `srun` without `--jobid`). `sbatch` is
  the ifarm-slurm skill's job, under its rules.
- Never write outside `/work/eic3/users/romanov/zdc-autoresearch/`,
  `…/zdc-autoresearch-out/`, `/volatile/eic/romanov/zdc-autoresearch/` and
  `/farm_out/romanov/zdc-autoresearch/`. Never delete under them without asking.
- Never stage tape files (`jcache`) or touch `/mss` unless the user asks.
