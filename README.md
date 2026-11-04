# zdc-autoresearch

Autonomous optimization of the ePIC Zero-Degree Calorimeter (ZDC) reconstruction
in EICrecon, run as a phase-gated autoresearch loop by Claude Code. The physics:
`Λ → n π⁰ → n γ γ` in the Meson Structure Function program; the trigger:
EICrecon issue [#2737](https://github.com/eic/EICrecon/issues/2737) (the
square-tile ZDC merges nearby showers) and PR
[#3064](https://github.com/eic/EICrecon/pull/3064) (new clustering parameters,
under review with open questions about the cluster distributions and Λ
statistics). `docs/zdc-problem.md` has the whole story.

## The three protocol files

| file | holds |
|---|---|
| `zdc-setup.md` | everything specific to this program: pins, paths, datasets, the scoreboard, the acceptance rule, budgets, the frozen list |
| `work-common.md` | the rules of every run: environment, FIX / DECIDE / ASK / PARK / STOP, memory, findings, writing, coding, git |
| `zdc-autoresearch-loop-v2.md` | the phases: 0 foundation, 1 dissect PR 3064, 2 parameter loop, 3 algorithm loop, 4 confirmation at scale and the PR draft |

`autoresearch-loops.md` surveys every autoresearch loop in `~/dev` (what
existed, what worked, what had to change). `zdc-autoresearch-loop-v1.md` is
the first draft; `docs/expert-review-v1.md` is the independent review of it
(22 ranked changes, every code claim with file and line); v2 applies them:
a truth-matched separation efficiency as the selector instead of the Λ
efficiency (which `LambdaReconstruction`'s own π⁰ window caps), the Λ code
and windows frozen while the clustering is tuned, the neutron guarded on raw
cluster energy, guns on the geometry with the LYSO ECal, a paired test on
identical events plus a held-out seed set instead of a noise band, and the
review's mechanism for the three findings (clusters collapsing to single
subcell columns below the 24.4 mm pitch) as the first hypothesis.

## Start a run

```
Read zdc-setup.md, work-common.md and zdc-autoresearch-loop-v2.md. Run.
```

That is the whole start line, typed into Claude Code in this folder (auto
mode). Add `online` when you will answer in chat during the run. The agent
resumes from `space/STATUS.md`, answers to its questions go into
`space/QUESTIONS.md` after `ANSWER:`.

## Run it yourself (no agent)

Every step is a numbered script with `--help`; the number says what kind of
step it is:

| range | meaning | examples |
|---|---|---|
| 1xx | foundation: environment, build, datasets, references, gates | `101_check_environment.sh`, `102_build_eicrecon.sh`, `110_generate_guns.py`, `120_reconstruct.py`, `130_compare_collections.py` |
| 2xx | understanding (no experiments) | `200_cluster_distributions.py` |
| 3xx | experiments | `300_run_experiment.py configs/experiments/<name>.yaml` |
| 4xx | evaluation | `400_scoreboard.py`, `401_benchmark_plots.sh`, `402_lambda_msf_metrics.py` |
| 5xx | farm | `500_farm_array.py` |
| 7xx | figures and slides | `700_build_slides.py` (Phase 4) |

Phase 0 by hand, on this workstation:

```bash
docker pull eicweb/eic_xl:26.11.0-stable
scripts/101_check_environment.sh --record-digest
scripts/102_build_eicrecon.sh                       # the pin; 30 to 60 minutes
scripts/102_build_eicrecon.sh --ref fdbb773d        # PR 3064
uv run scripts/110_generate_guns.py                 # D1..D4 with npsim, ZDC-only geometry
scripts/111_fetch_dis_inputs.sh --list              # pick the campaign, then without --list
scripts/112_msf_sample.sh                           # the local MSF files
uv run scripts/120_reconstruct.py configs/experiments/R0_stock.yaml
uv run scripts/120_reconstruct.py configs/experiments/R1_pr3064.yaml
scripts/131_prove_gates.sh /data/zdc-autoresearch/reco/R0_stock/D5_dis_minq2_100/<file>.edm4eic.root
uv run scripts/400_scoreboard.py R0_stock
uv run scripts/400_scoreboard.py R1_pr3064 --compare R0_stock
uv run scripts/200_cluster_distributions.py R0_stock R1_pr3064 --phase phase0
scripts/401_benchmark_plots.sh R0_stock --phase phase0
```

One experiment: write `configs/experiments/E<N>_<name>.yaml` (copy
`R1_pr3064.yaml`, change the parameters), then

```bash
uv run scripts/300_run_experiment.py configs/experiments/E<N>_<name>.yaml --phase phase2
```

Machine facts live in `configs/local.yaml` (another machine: copy it, point
`ZDC_CONFIG` at the copy). EIC software never runs on the host: every script
goes through `scripts/100_in_container.sh`, which runs the command inside the
pinned `eic_xl` image with the repo at `/work` and `/data/zdc-autoresearch` at
`/data`. On the farm: `docs/ifarm-tunnel.md` and the two skills under
`.claude/skills/`.

## Layout

```
configs/      local.yaml, ifarm.yaml (machine), datasets.yaml, metrics.yaml (frozen), experiments/*.yaml
scripts/      the numbered steps;  zdc/  the shared Python (config loader, edm4eic readers, fits)
submodules/   EICrecon (the code under study; only its ZDC files are writable after Phase 0),
              detector_benchmarks (generators, plot scripts), epic-capybara (file comparison),
              meson-structure (the Λ analysis and campaign docs), skill-eicrecon (PR style checklist)
docs/         zdc-problem.md, ifarm-tunnel.md, expert-review-v1.md
space/        STATUS.md (resume), QUESTIONS.md, LEDGER.md (phases), EXPERIMENTS.md (experiments),
              FROZEN (after Phase 0), notes/ (decisions, lessons, patches), reports/, plots/, perf/ (scoreboard.csv, manifests)
.claude/      settings.json (the protect hook), hooks/protect.py, skills/{ifarm-tunnel,ifarm-slurm,slides}
/data/zdc-autoresearch/   build/, install/, datasets/, reco/<experiment>/<dataset>/, logs/   (never in git)
```

State on 2026-11-04: scaffold complete, no script executed yet; Phase 0 of the
loop is where they first run. Open item carried from the MSF repository:
`JeffersonLab/meson-structure` PR #9 is conflicting with main (parked in
`space/STATUS.md`).

## Git

Nothing is committed by the agent unless the chat message says `please-git`.
Submodules are pinned in `zdc-setup.md`; `git submodule update --init` (not
`--recursive`: meson-structure's own submodules are not needed).
