# ZDC program — setup file

Everything specific to this program lives here: names, pins, datasets,
metrics, budgets, farm paths. `work-common.md` holds the rules of every
run; `zdc-autoresearch-loop-v2.md` holds the phases. Every number that
belongs to this program is here and nowhere else; a number marked
*Step 0 fills* is written into this file by the agent during Phase 0 with
its evidence, and never changed afterwards without a `D-user` decision.

## Names

| name | value |
|---|---|
| `{repo}` | this repository (`zdc-autoresearch`), submodules included; `/work` inside the container |
| `{space}` | `{repo}/space` |
| `{ledger}` | `{space}/LEDGER.md` |
| `{data}` | `/data/zdc-autoresearch` (host and container alike; `btrfs`, 940 GB free on 2026-11-04) |
| `{scratch}` | the scratch folder Claude Code reports |
| `{memory}` | the memory folder Claude Code reports at session start |
| `{git}` | `off` — the user grants commits in chat with `please-git`; the EICrecon submodule then uses branch `zdc-autoresearch/<experiment>` |
| `{online}` | `no` unless the user says otherwise at the start line |
| `{image}` | `eicweb/eic_xl:26.11.0-stable` (digest: *Step 0 fills*); on ifarm `/cvmfs/singularity.opensciencegrid.org/eicweb/eic_xl:26.11.0-stable` |
| `{wrapper}` | `scripts/100_in_container.sh` — runs one command inside `{image}` with `{repo}` at `/work` and `{data}` at `/data`, EIC environment loaded |
| `{eicrecon}` | `submodules/EICrecon` at `e5e2a60c60b6a10a25cbe35497da1d4996a492df` (main, 2026-11-04) |
| `{pr}` | EICrecon PR 3064, head `fdbb773d6e4f03d034c843dfffce391f625f3a93`, branch `baptiste/zdc-clustering-calibration` |
| `{benchmarks}` | `submodules/detector_benchmarks` at `e72103b9` (master, 2026-11-04) |
| `{capybara}` | `submodules/epic-capybara` at `4b6b41cc` (v1.3.0) |
| `{msf}` | `submodules/meson-structure` at `f0dff480` (main, 2026-11-04); its own submodules are not initialized |

Where you run: on the user's workstation (24 cores, 62 GB, one shared GPU
not needed here), as Claude Code in this repository in auto mode. EIC
software runs only through `{wrapper}` (docker) locally and through the
ifarm skills on the farm. Keep two cores free.

## Farm

| name | value |
|---|---|
| tunnel | `ssh -p 4333 -o BatchMode=yes romanov@localhost` (the user opens it: `docs/ifarm-tunnel.md`) |
| interactive job name | `zdc-node` |
| code mirror | `/work/eic3/users/romanov/zdc-autoresearch` |
| small results | `/work/eic3/users/romanov/zdc-autoresearch-out/<run>/` |
| bulky outputs | `/volatile/eic/romanov/zdc-autoresearch/<run>/` |
| logs | `/farm_out/romanov/zdc-autoresearch/<run>/` |
| array throttle | `%16`; more is a question to the user |
| memory | `2G` per CPU unless a measured `MaxRSS` says more; above `4G` per CPU is a question |
| MSF DD4hep inputs | `/work/eic3/users/romanov/meson-structure-2026-07/dd4hep/{5x41,9x100,9x130,9x275}/msf_ev1000_NNNN.edm4hep.root` (read-only) |

## Datasets

All simulated inputs are made once in Phase 0, listed with sha256 in
`{space}/perf/manifest-datasets.json`, and frozen. Reconstruction outputs
are never frozen (they are regenerated per experiment). Detector
configurations are from the epic install inside `{image}`;
`epic_zdc_sipm_on_tile_only` exists there as a generated configuration
(`configurations/zdc_sipm_on_tile_only.yml` in epic) — Step 0 verifies the
file is present inside the image before anything else.

| id | content | generator | detector config | size (Step 0 confirms) | role |
|---|---|---|---|---|---|
| D1 | π⁰ gun, θ 0 to 4 mrad around the proton axis | `{benchmarks}/benchmarks/zdc_pi0/analysis/gen_pi0_decay.cxx` | `epic_zdc_sipm_on_tile_only` | p = 60, 80, 100, 130, 160 GeV; 2000 events each; seeds 1, 2 (second seed only at 100 GeV, for the noise band) | search set (S1) |
| D2 | photon gun | `{benchmarks}/benchmarks/zdc_photon/analysis/gen_particles.cxx` | same | the benchmark's momenta; 1000 events each | search set (S2) |
| D3 | neutron gun | `{benchmarks}/benchmarks/zdc_neutron/gen_forward_neutrons.cxx` | same | the benchmark's momenta; 1000 events each | guard (S3) |
| D4 | Λ gun, decays to n π⁰ | `{benchmarks}/benchmarks/zdc_lambda/analysis/gen_lambda_decay.cxx` | same | p = 100, 125, 150, 175, 200, 225, 250, 275 GeV; 2000 events each; seeds 1, 2 at 175 GeV | search set (S4, the primary metric) |
| D5 | DIS, the CI's guard samples | official campaign FULL files from XRootD (`root://dtn2304.jlab.org:8443//jlab-osdf-ro/eic/EPIC/volatile/FULL/<latest campaign>/epic_craterlake_18x275/DIS/NC/18x275/minQ2=100/` and `…/SIDIS/pythia6-eic/1.0.0/18x275/q2_0to1/`), or, when absent, npsim of the EVGEN files the EICrecon CI uses (`.github/workflows/linux-eic-shell.yml`, jobs `npsim-dis` and `npsim-dis-nc`) | `epic_craterlake_18x275` | ≥ 2000 events per sample | guard (G1 to G4): the review findings reproduced on the reviewers' own inputs |
| D6a | MSF Λ, local slice | `/data/meson-structure-2026-07/dd4hep/9x130/*.edm4hep.root` (the files present on 2026-11-04) | `epic_craterlake_9x130` (Step 0 confirms the campaign's config from `{msf}/simulation-pipeline/configs`) | all local files | quick Λ-in-events check (S5 quick) |
| D6b | MSF Λ at scale | the farm paths above, `9x275` and `9x130` | same | 100 files = 100 000 events per energy | the confirmation set (S5), farm array, Phase 4 |

Held-out rule: D6b is never used to choose between experiments. It is
reconstructed only for the Phase 1 baselines and for the Phase 4
confirmation of accepted configurations.

## References (the ruler)

Two reference reconstructions exist for every dataset from Phase 0 on:

| ref | EICrecon | role |
|---|---|---|
| R0 | `{eicrecon}` at the pin, stock parameters | the baseline every experiment is measured against; the byte-identical guard for non-ZDC collections |
| R1 | `{pr}` head `fdbb773d` | the candidate; its scoreboard row is the first thing Phase 1 explains |

Their scoreboard rows and the sha256 of their output files are in
`{space}/perf/references.json` (*Step 0 fills*). The reference outputs
themselves live under `{data}/reco/R0/` and `{data}/reco/R1/` and are
listed in the frozen manifest.

## Scoreboard (the fixed metrics)

`scripts/400_scoreboard.py` computes every metric below for one
reconstruction and appends one row to `{space}/perf/scoreboard.csv`. Every
experiment reports the whole row; a row with a missing cell is not a verdict.
Collection names are in `configs/metrics.yaml` and are verified against the
reconstructed files in Step 0 (the benchmarks name
`ReconstructedFarForwardZDCLambdas`; EICrecon main at the pin writes
`ReconstructedLambdas` and `ReconstructedHcalFarForwardZDCNeutrals`).

| id | dataset | metric | role |
|---|---|---|---|
| S1a | D1 | fraction of events with exactly two `HcalFarForwardZDCClusters` | diagnostic: two-photon separation |
| S1b | D1 | γγ invariant mass from the two clusters: peak position and σ from a Gaussian fit; fraction within ±3σ of m(π⁰) | diagnostic |
| S1c | D1 | π⁰ energy scale μ/E and resolution σ/μ (the benchmark's fit) per momentum | diagnostic |
| S2 | D2 | photon energy scale and resolution; θ resolution; `isGamma` efficiency (fraction of events whose leading neutral is PDG 22) | search |
| S3 | D3 | neutron energy scale and resolution; θ resolution; fraction of events with one cluster; `isGamma` false-positive rate | **guard**: must stay inside its noise band |
| S4a | D4 | Λ reconstruction efficiency: events with a reconstructed Λ whose mass lies within the window of `configs/metrics.yaml` (default ±3σ of the R0 peak), divided by generated events, per momentum and averaged | **primary** |
| S4b | D4 | Λ mass peak and σ; θ* and decay-z resolution (the benchmark's fits) | guard: σ not worse than R0 beyond the noise band |
| S5 | D6a (quick) / D6b (confirmation) | Λ → nπ⁰ candidates per 1000 events; mass peak and σ; efficiency against MC-truth Λ with all three daughters in the ZDC acceptance | the physics goal; confirmation only |
| G1 | D5 | fraction of ZDC clusters with intrinsic φ within 5° of ±180°, and the φ histogram χ² against R0 | guard: the review's first finding, explained before acceptance |
| G2 | D5 | fraction of cluster energy above 50 GeV and the cluster-energy spectrum χ² against R0 | guard: second finding |
| G3 | D5 | clusters per event with E < 1 GeV; nhits per cluster median | guard: third finding |
| G4 | every dataset | every non-ZDC collection byte-identical to R0 (`scripts/130_compare_collections.py`), capybara Δ outside ZDC collections = 0 | **gate**: fails → REJECTED, no exceptions |
| T | every dataset | reconstruction wall seconds per 1000 events | report line; a 2× slowdown is a question |

Noise band: Step 0 reconstructs R0 on both seeds of D1 (100 GeV) and D4
(175 GeV) and once more on the same files, and records per metric the larger
of the seed-to-seed difference and the statistical error as the band
(*Step 0 fills* `{space}/perf/noise-band.json`). A change inside the band is
not a change.

Acceptance (Phases 2 and 3): ACCEPTED when S4a improves by more than its band,
S3, S4b and G4 stay inside theirs, and G1 to G3 are each either inside their
band or explained in the ledger entry by a mechanism the plots show. A S1 gain
with a S4a loss is REJECTED. Everything else is REJECTED with the measured
deltas kept.

## Statistics budget (how the sizes above were chosen)

- S4a with ε ≈ 0.3 and 2000 events per momentum: σ(ε) = √(0.3·0.7/2000) =
  0.010 absolute, 3 % relative; over eight momenta the averaged metric
  resolves a 2 % relative change.
- S1a with 2000 events: ±1.1 % absolute on a fraction near 0.5.
- S5 with the MSF efficiency last measured at about 4.5 % (26.02 campaign,
  issue #2737): 10 000 events give about 450 reconstructed Λ (4.7 % relative);
  100 000 events give 1.5 %. D6b at 100 files per energy is sized for the
  Phase 4 confirmation; the local D6a slice is a smoke check only.
- D5 at ≥ 2000 events per sample: the φ histogram at 36 bins has ≥ 50 entries
  per bin for the χ² to mean anything; the CI's 100-event samples do not.

## Budgets

| item | value | source |
|---|---|---|
| parameter experiment (no rebuild) | ≤ 30 minutes wall on D1 to D5 | ZDC-only reconstruction of 2000 events takes seconds; D5 full-detector reconstruction dominates (Step 0 measures T) |
| code experiment | the above plus one incremental build; a clean build (30 to 60 minutes) only when the incremental one fails | EICrecon `AGENTS.md` |
| experiments per run before a report checkpoint | 5 | the ilreco journal rule: a report every 5 loops, a stop for user review every 10 |
| farm array (Phase 4) | ≤ 200 tasks, `%16`, ≤ 4 h each | the farm rules; one array per run |
| reading plots | once per milestone and when a G1 to G3 explanation needs it | token thrift |

## Frozen after Phase 0

`{space}/FROZEN` (read by `.claude/hooks/protect.py`) lists, after Phase 0:
every submodule except the owned ZDC files of `{eicrecon}` (list in
`docs/zdc-problem.md`), `configs/datasets.yaml`, `configs/metrics.yaml`,
`scripts/13*` (the gates), `{space}/perf/manifest-datasets.json`,
`{space}/perf/references.json`, `{space}/perf/noise-band.json`, and this
file. A change to any of them is a question, never an edit.

## People and threads

- Baptiste Fraisse (`baptistefraisse`): author of issue #2737 and PR #3064;
  the MSF Λ analysis.
- Wouter Deconinck (`wdconinc`): the review finding of 2026-10-30.
- Sebouh Paul (`sebouh137`): ZDC reconstruction and benchmarks author
  (HEXPLIT, FarForwardNeutralsReconstruction, zdc_* benchmarks).
- Dmitry Kalinkin (`veprbl`): capybara, benchmark CI, the 80 GeV pion
  comment on the issue.
- Markus Diefenthaler (`mdiefent`): MSF lead.

The user posts on GitHub; the agent drafts (`{space}/reports/pr-draft.md`).
