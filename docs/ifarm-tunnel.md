# Using the JLab farm from the local agent through the ifarm tunnel

**What this is.** The agent runs on your machine (JLab nodes cannot reach
Anthropic: a default-deny URL whitelist resets TLS to api.anthropic.com from
ifarm and the compute nodes alike). It reaches the farm through your normal
ssh tunnel to ifarm, with your normal key, and runs commands either on the
ifarm login node (short things: `squeue`, `sbatch`, `rsync`) or as a Slurm
step inside an Apptainer container on a compute node you allocated. The
price: the agent holds your real key, so it *can* run anything on ifarm;
the rules in the skill are what it is told to use, not a wall. Run the agent
with bash commands prompting, never with `--dangerously-skip-permissions`,
while the tunnel is open.

Adapted from `~/dev/optim/use_ifarm_gpu_straight.md` (verified on ifarm on
2026-09-23, job 11680127, sciml2102) for the ZDC program: CPU work by
default, GPU optional.

```
your machine                              ifarm                    compute node
┌────────────────────────┐  -L 4333:22   ┌──────────────┐  srun    ┌───────────────────────────┐
│ agent (host or         │──────────────►│ sshd (you)   │─overlap─►│ apptainer eic_xl (cvmfs)  │
│  container), repo rw   │  your key     │ squeue/sbatch│          │  $U read-only             │
│  ~/.ssh                │               └──────────────┘          │  $U/zdc-autoresearch* rw  │
└────────────────────────┘                                         │  /volatile, /farm_out  rw │
                                                                   └───────────────────────────┘
```

Paths used throughout (the setup file `zdc-setup.md` is the canonical home):

| name | path |
|---|---|
| `U` | `/work/eic3/users/romanov` |
| code mirror | `$U/zdc-autoresearch` (rsync of the local repo, `.git/` excluded) |
| results | `$U/zdc-autoresearch-out/<run>/` (small files: json, csv, png, logs copied once at the end) |
| bulky outputs | `/volatile/eic/romanov/zdc-autoresearch/<run>/` (ROOT files; purgeable) |
| logs | `/farm_out/romanov/zdc-autoresearch/<run>/` — never on `/work` |
| image | `/cvmfs/singularity.opensciencegrid.org/eicweb/eic_xl:<tag>` (the tag pinned in `zdc-setup.md`) |

Your ifarm login shell is tcsh: **type `bash` first** in every ifarm terminal.

References: hardware https://scicomp.jlab.org/scicomp/nodeStatus/hardware ·
jobLimit list https://scicomp.jlab.org/scicomp/slurmJob/jobLimit ·
EPSCI apptainer+GPU https://wiki.jlab.org/epsciwiki/index.php/Create_apptainer+GPU_interactive_farm_job_(can_be_used_w/_Jupyter)

## Step 1 — on ifarm: allocate a node (only for interactive steps)

Batch work (`sbatch` arrays, the normal path for re-reconstruction) needs no
allocation: the agent submits from the login node through the tunnel. An
interactive node is for builds and quick tests. In `tmux`, sized to what you
will use (farm rules below). `--job-name=zdc-node` is how the agent finds it.

```bash
tmux new -s zdc
srun --job-name=zdc-node --account=eic --partition=production --cpus-per-task=16 --mem-per-cpu=2G --time=24:00:00 --pty bash
```

GPU variant (only if a phase needs one): `--partition=gpu --gres=gpu:T4:1`.
Keep this shell open — exiting it releases the node. Verify on the node:
`hostname; nproc`.

Make sure the directories exist (once):

```bash
bash
U=/work/eic3/users/romanov
mkdir -p $U/zdc-autoresearch $U/zdc-autoresearch-out /volatile/eic/romanov/zdc-autoresearch /farm_out/romanov/zdc-autoresearch
```

## Step 2 — on your machine: the tunnel

```bash
ssh -L localhost:4333:localhost:22 ifarm      # your `hopifarm` alias
```

Leave it open. Verify from another terminal (also shows the job):

```bash
ssh -p 4333 romanov@localhost 'squeue --me'
```

## Step 3 — on your machine: the agent

Run Claude Code on the host in this repository (the farm skills live in
`.claude/skills/`). Then `/ifarm-tunnel` and ask for `hostname` on ifarm, or
`/ifarm-slurm` for batch work.

If you run the agent in a container instead, add `--network host` (to reach
`127.0.0.1:4333`) and mount your ssh dir at `/home/ubuntu/.ssh:ro` — OpenSSH
resolves `~` from the passwd database and uid 1000 is `ubuntu` in the
eicdev images, so `/myhome/.ssh` would not be found.

## Step 4 — the command shapes (what the skills do)

Login-node command (short, no heavy compute):

```bash
ssh -p 4333 -o BatchMode=yes romanov@localhost bash -s <<'REMOTE'
squeue --me -h -o '%i %j %T %M' | head
REMOTE
```

Interactive-node step inside the container:

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

- `bash -s` with the script on stdin: ifarm's tcsh never parses bash syntax.
- `--input=none`: otherwise `srun` forwards stdin to the step and **eats the
  rest of the script** — every line after the `srun` silently never runs.
- `--overlap`: without it the step waits for CPUs the `--pty bash` holds.
- The binds: your user dir read-only, the program's two dirs writable on
  top, `/volatile` and `/farm_out` explicit (not bound by default).

## How code and results move

| what | lives | moves | how |
|---|---|---|---|
| code | local repo (source of truth) | local → farm before a run | `rsync … -e 'ssh -p 4333' ./ romanov@localhost:$U/zdc-autoresearch/` (`.git/`, `build/`, `data/`, `.venv/` excluded) |
| input data | `/volatile/eic/romanov/...`, `/work/eic3/users/romanov/meson-structure-2026-07/dd4hep` | never | the `-B` binds |
| logs | `/farm_out/romanov/zdc-autoresearch/<run>/` | copied once into `zdc-autoresearch-out/<run>/` when a run ends | |
| results | `$U/zdc-autoresearch-out/<run>/` | farm → local after a run | `rsync … romanov@localhost:$U/zdc-autoresearch-out/ ./out/` (small files only) |
| bulky ROOT | `/volatile/eic/romanov/zdc-autoresearch/<run>/` | stays; a few files pulled for inspection | `scp -P 4333` one file at a time |

## Farm rules — from JLab admins, learned the hard way

1. **Request only what you use.** Idle resources are the offense: memory
   asked for and under half used, a node held doing nothing. The farm is
   provisioned at 2 GB per CPU; asking for more bills extra CPUs.
2. **Measure before requesting more than 2 GB/CPU.** Scaled-down run first
   under `/usr/bin/time -v` (`Maximum resident set size`); `sacct -j <jobid>
   --format=JobID,JobName,ReqMem,MaxRSS,Elapsed` after a step. Request peak +
   ~20 %.
3. **Logs never on `/work`.** Slurm stdout/stderr go under `/farm_out/romanov/…`.
4. **Scratch never in `/tmp`** and never `$PWD` (jobs inherit the submit
   directory). Use an explicit path under the run's output tree, created and
   trap-removed by the job script.
5. **Arrays throttled at `%16`.** The admin cap is lifted, the self-imposed
   throttle stays: the eic file server was saturated once and the account was
   limited to one running job.
6. **Check the jobLimit list** after anything unusual.
7. `--account=eic`. Partition limits (2025): `gpu` 10 d, `production` 4 d,
   `jupyter`/`ifarm`/`priority` 1 d.

Sources: `submodules/meson-structure/simulation-pipeline/README.md` § "Farm
etiquette", `~/dev/notes/jlab/farm-slurm.md`, the agent memory file
`jlab-farm-job-policies`.

## Teardown

Exit the `srun` shell (frees the node), close the tunnel.

## Gotchas, all hit in practice

- tcsh login shell → `bash -s` on stdin, always. `Illegal variable name`
  means bash syntax reached tcsh.
- `srun` eats stdin → `--input=none`, always.
- Compute nodes' port 22 is filtered from ifarm; steps are the only way in.
- ifarm is a load balancer (ifarm2401/2402); pin a host when two tunnels must
  meet.
- `TMPDIR` on the ifarm login node points into `/scratch`, which Apptainer
  does not bind → `EROFS: mkdir '/scratch'`; on compute nodes Slurm sets a
  bound scratch. Pass `env TMPDIR=<writable>` when running ROOT on the login
  node.
- `/volatile` and `/farm_out` are not bound by default; `$HOME`, `/work`,
  `/u`, `/group` are.

## What this does not protect

The agent holds your real key. Route B (`~/dev/optim/use_ifarm_gpu.md`: an
sshd inside the farm sandbox, agent key only) removes the key from the agent
entirely; it was never verified on ifarm and is not used here.
