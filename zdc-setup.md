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
| `{pr}` | EICrecon PR 3064, head `fdbb773d6e4f03d034c843dfffce391f625f3a93`, base `66b8cf62` (14 commits behind the pin), branch `baptiste/zdc-clustering-calibration`; R1 is its three-file diff applied to the pin (`space/notes/patches/R1_pr3064.patch`) |
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

All simulated inputs are made once in Phase 0, listed with sha256 and event
count in `{space}/perf/manifest-datasets.json`, and frozen. Reconstruction
outputs are never frozen (they are regenerated per experiment). Detector
configurations are from the epic install inside `{image}`. The guns use
`epic_zdc_lyso_sipm` (the ZDC with the 7 cm LYSO crystal ECal in front of
the HCal, as in every physics sample; epic `configurations/zdc_lyso_sipm.yml`);
`epic_zdc_sipm_on_tile_only` is what the benchmarks' CI uses and is one flag
away for a cross-check. Step 0 verifies the files are present inside the
image before anything else. Every generator gets an explicit seed (the
benchmark macros clock-seed when given 0).

| id | content | generator | detector config | size (Step 0 confirms) | role |
|---|---|---|---|---|---|
| D1 | π⁰ gun, θ 0 to 4 mrad around the proton axis | `{benchmarks}/benchmarks/zdc_pi0/analysis/gen_pi0_decay.cxx` | `epic_zdc_lyso_sipm` | p = 20, 30, 50, 70 GeV (the π⁰ energies of Λ daughters: 6 to 25 % of E_Λ) and 60, 80, 100, 130, 160 GeV (the benchmark's); 2000 events each; seed 1 | search set (S1 diagnostic) |
| D1h | the same, held out | same | same | p = 30, 70, 100 GeV; 2000 events; generator and npsim seed 101 | held-out (checkpoints only) |
| D2 | photon gun | `{benchmarks}/benchmarks/zdc_photon/analysis/gen_particles.cxx` | same | p = 20, 30, 50, 70, 100, 150, 200, 275 GeV (the benchmark's list plus the low Λ-daughter energies); 1000 events each; seed 1 | search set and guard (S2) |
| D3 | neutron gun, θ 0 to 4 mrad | npsim particle gun (`--gun.particle neutron`, uniform θ inside 4 mrad around the proton axis); the benchmark's `gen_forward_neutrons.cxx` hard-codes 100 GeV and 6 mrad and runs on the full detector, so it is not used | same | p = 20, 50, 100, 150, 200, 275 GeV; 1000 events each; seed 1 | guard (S3) |
| D4 | Λ gun, decays to n π⁰, all three daughters inside 4 mrad at the ZDC face (the generator's acceptance cut) | `{benchmarks}/benchmarks/zdc_lambda/analysis/gen_lambda_decay.cxx` | same | p = 100, 125, 150, 175, 200, 225, 250, 275 GeV; 2000 events each; seed 1 | search set: the selector S0 and the outcome S4 |
| D4h | the same, held out | same | same | p = 125, 175, 250 GeV; 2000 events; seed 101 | held-out (checkpoints only) |
| D4n | noise validation | same | same | p = 175 GeV; 2000 events; seeds 2, 3 (with seed 1 of D4: three independent samples); likewise D1 at 100 GeV seeds 2, 3 | Step 0 item 13 only |
| D5 | DIS, the CI's guard samples | official campaign FULL files from XRootD (`root://dtn2304.jlab.org:8443//jlab-osdf-ro/eic/EPIC/volatile/FULL/<latest campaign>/epic_craterlake_18x275/DIS/NC/18x275/minQ2=100/` and `…/SIDIS/pythia6-eic/1.0.0/18x275/q2_0to1/`), or, when absent, npsim of the EVGEN files the EICrecon CI uses (`.github/workflows/linux-eic-shell.yml`, jobs `npsim-dis` and `npsim-dis-nc`) | `epic_craterlake_18x275` | sized in **ZDC clusters**: ≥ 2000 R0 clusters per sample (36 φ bins × 50 entries with margin); the DIS samples have a forward neutron in a minority of events, so Step 0 fetches files until the R0 cluster count is met and records clusters per event | guard (G1 to G4): the review findings reproduced on the reviewers' own inputs |
| D6a | MSF Λ, local slice | `/data/meson-structure-2026-07/dd4hep/9x130/msf_9x130_1000evt_*.edm4hep.root` (the files present on 2026-11-04) | the campaign's configuration (Step 0 confirms from `{msf}/docs/campaign-2026-07/` and the pipeline configs; default `epic_craterlake_9x130`) | all local files | quick Λ-in-events check (S5 quick) |
| D6b | MSF Λ at scale | the farm paths above, `9x275` and `9x130` (file-name pattern confirmed at Step 0 item 5) | same | 100 files = 100 000 events per energy | the confirmation set (S5), farm array, Phase 4 |

Held-out rules: D1h and D4h are reconstructed only at checkpoints with the
current best, never to choose between experiments; D6b is never used to
choose and is reconstructed only for the references and the Phase 4
confirmation.

## References (the ruler)

Two reference reconstructions exist for every dataset from Phase 0 on:

| ref | EICrecon | role |
|---|---|---|
| R0 | `{eicrecon}` at the pin, stock parameters | the baseline every experiment is measured against; the identical-output guard for non-ZDC collections |
| R1 | the pin plus `{pr}`'s three-file diff (`space/notes/patches/R1_pr3064.patch`; build label `R1`) | the candidate; its scoreboard row is the first thing Phase 1 explains. Never the PR's own commit: its base is 14 commits behind the pin (#3061 changed HEXPLIT truth links, #3051 attenuation, #3031 particle flow) |
| Rt | the pin plus `space/notes/patches/truthchain.patch` (a second neutrals and Λ factory instance reading `HcalFarForwardZDCTruthClusters`) | the truth-cluster ceiling of S4a: what perfect clustering would give under the same `LambdaReconstruction` |

All reference reconstructions run single-threaded (`-Pjana:nthreads=1`), so
that outputs are deterministic and G4 can demand identity (the PR's CI shows
Δ 840 on the multithreaded page against Δ 148 single-threaded for the same
sample). Their scoreboard rows and the sha256 of their output files are in
`{space}/perf/references.json` (*Step 0 fills*). The reference outputs live
under `{data}/reco/R0_stock/`, `{data}/reco/R1_pr3064/`, `{data}/reco/Rt_truthchain/`
and are listed in the frozen manifest.

## Scoreboard (the fixed metrics)

`scripts/400_scoreboard.py` (with `scripts/410_truth_match.py` for the
truth-matched cells) computes every metric below for one reconstruction and
appends one row to `{space}/perf/scoreboard.csv`. Every experiment reports
the whole row; a row with a missing cell is not a verdict. Collection names
are in `configs/metrics.yaml` and are verified against the reconstructed
files in Step 0 (EICrecon main at the pin writes `ReconstructedLambdas` and
`ReconstructedHcalFarForwardZDCNeutrals`; the benchmarks still use the
pre-2026-05-29 names, hence the patched copies under `scripts/700_benchmarks/`).

Truth matching uses `HcalFarForwardZDCClusterAssociations` (cluster ↔
MCParticle with the energy-fraction weight). For a true particle, its
best-matched cluster is the one with the largest weight × cluster energy;
**purity** is that cluster's weight for the particle; **containment** is the
share of the particle's total associated energy (summed over all clusters)
held by the best cluster. A particle is **separated** when purity ≥ 0.8 and
containment ≥ 0.5 (limits in `configs/metrics.yaml`).

| id | dataset | metric | role |
|---|---|---|---|
| S0 | D4 | **separation efficiency**: the fraction of true photons (each of the two) and of true neutrons that are separated, per momentum; S0γ, S0n and the event fraction with all three separated (S0all) | **the selector** |
| S1a | D1 | fraction of events whose two true photons are both separated (truth-matched two-cluster fraction); the raw "exactly two clusters" fraction beside it | diagnostic |
| S1b | D1 | γγ invariant mass from the two best-matched clusters: peak and σ; fraction within ±3σ of m(π⁰) | diagnostic |
| S1c | D1 | π⁰ energy scale μ/E and resolution σ/μ (the benchmark's fit) per momentum | diagnostic |
| S1d | D1 | photon position resolution at the ZDC face (best cluster vs the true impact point) | diagnostic |
| S2 | D2 | photon energy scale |μ/E − 1| per momentum from the best-matched cluster's corrected energy; resolution σ/μ; θ resolution; γ-tag efficiency (the best-matched cluster is tagged PDG 22 in the neutrals) | **guard** on the scale (limit per momentum in `configs/metrics.yaml`): a calibration must not inflate photons to pass the π⁰ window |
| S3 | D3 | neutron **raw** cluster-energy sum Σ E(`HcalFarForwardZDCClusters`) / E_true (mean and σ, no `corrPower`); corrected scale and resolution; θ resolution; clusters per neutron; energy fraction tagged γ in neutron events; n mis-tag rate (best cluster tagged PDG 22) | **guard**: raw sum, clusters per neutron and γ-tagged fraction inside their limits |
| S4a | D4 | Λ reconstruction efficiency, **truth-matched**: events with a `ReconstructedLambdas` entry built from clusters associated to the true n, γ, γ (each with purity ≥ 0.8) and mass inside the window, divided by generated events, per momentum; beside it the raw count-any-Λ fraction, and the Rt ceiling | outcome, reported, never the selector |
| S4b | D4 | Λ mass peak and σ; θ* and decay-z resolution (the benchmark's fits), on the truth-matched Λ | guard: σ not worse than the current best beyond the paired error |
| S4c | D4 | mean number of `ReconstructedHcalFarForwardZDCNeutrals` tagged γ per event | guard against fragment combinatorics: inside its limit |
| S5 | D6a (quick) / D6b (confirmation) | Λ → nπ⁰ candidates per 1000 events, ZDC-only and all-calorimeter separately; mass peak and σ; efficiency against MC-truth Λ with all three daughters inside the face; the acceptance row (events with ≥ 1 HCal RecHit) | the physics goal; confirmation only |
| G1 | D5 | fraction of clusters with intrinsic φ within 5° of ±180°; fraction of clusters with exactly one distinct subcell (x, y) ("columns"); intrinsic θ distribution; lateral width √λ2 against energy | guard: inside the limits the user set at the Phase 0 checkpoint |
| G2 | D5 | fraction of cluster energy above 50 GeV; the cluster-energy spectrum χ² against R0 | guard: same |
| G3 | D5 | clusters per event with E < 1 GeV; nhits per cluster median; clusters per event | guard: same |
| G4 | every dataset | every collection outside the owned list identical to R0 (`scripts/130_compare_collections.py`, single-threaded reconstruction); capybara Δ outside the owned collections = 0. Owned: every `*FarForwardZDC*` collection, `ReconstructedHcalFarForwardZDCNeutrals`, `ReconstructedB0EcalNeutrals`, `ReconstructedEcalEndcapPNeutrals`, `ReconstructedLFHCALNeutrals` (the four outputs of the one neutrals factory), `ReconstructedLambdas`, `ReconstructedLambdaDecayProductsCM` | **gate**: fails → REJECTED, no exceptions |
| T | every dataset | reconstruction wall seconds per 1000 events | report line; a 2× slowdown is a question |

Out of scope, said once: timing (`tRes = 0`, no clustering stage uses time);
the LYSO clusters as photon candidates (a Phase 3 candidate, not a metric).

## Noise and significance

Every configuration is reconstructed on the **same simulated events**, so
the test of a change is paired:

- efficiencies (S0, S1a, S4a): McNemar's test on the discordant events
  (separated under A and not under B, and the reverse); the quoted error is
  the paired binomial error;
- fitted peaks and widths (S1b, S2, S3, S4b): a bootstrap over events
  (200 resamples), the same resamples for A and B;
- a change is **significant** at the limit `configs/metrics.yaml` sets
  (default 3σ of the paired error).

Determinism, which the paired test assumes: the same input reconstructed
twice gives identical output (checked at Step 0 and after every rebuild).
Honesty of the paired error: Step 0 item 13 reconstructs three independent
seeds (D4n and D1 seeds 1 to 3) with R0 and checks that the seed spread of
each metric lies within the quoted error (`{space}/perf/noise-validation.json`,
*Step 0 fills*). Overfitting to the fixed seeds: the held-out D1h and D4h
at every checkpoint.

Acceptance (Phases 2 and 3): ACCEPTED when S0all improves significantly in
the paired test (and no S0 component falls significantly), S2 scale, S3 raw
sum, S3 clusters per neutron, S4b and S4c stay inside their limits, G4
passes, and G1 to G3 are inside the limits the user set. A held-out check
that does not reproduce the gain reverts it. Everything else is REJECTED
with the measured deltas kept. Calibration refits are never experiments:
they follow an accepted clustering and are fit on D2 and D3 truth
(`scripts/420_refit_calibration.py`), never on S4a.

Frozen through Phases 1 to 3 unless the Phase 0 checkpoint opens them:
every parameter of `ReconstructedLambdas` (`pi0Window`, `lambdaMassWindow`,
`iterations`, `globalToProtonRotation`) and the `LambdaReconstruction`
source. Its IP-pointing π⁰ preselection caps S4a (the review's estimate:
only decays within about 3.6 m of the IP pass the ±10 % π⁰ window); Rt
measures that cap, and the cap is a finding for upstream, not a knob.

## Statistics budget (how the sizes above were chosen)

- S0 with 2000 events per momentum and a separation fraction near 0.5:
  ±1.1 % absolute unpaired; the paired test on the same events is tighter
  (only discordant events count).
- S4a: the unpaired error at ε ≈ 0.3 is 0.0102 (3.4 % relative), but ε is
  capped by `LambdaReconstruction` and near zero at 100 GeV (the Λ-gun
  acceptance cut keeps only late decays there), so the eight-momentum
  average is in practice four or five points; S4a is reported, not selected on.
- S5: on square tiles R0 is expected near zero, so Phase 4 compares about 0
  with the accepted configuration's X. At X = 2 %, 100 000 events give
  2000 Λ and 2.2 % relative. D6b at 100 files per energy is sized for that;
  the local D6a slice is a smoke check only.
- D5: ≥ 2000 R0 ZDC clusters per sample for the 36-bin φ histogram; sized by
  the measured cluster count at Step 0, not by events.

## Budgets

| item | value | source |
|---|---|---|
| parameter experiment (no rebuild) | ≤ 30 minutes wall on D1 to D4 (D5 and full G4 at checkpoints only) | ZDC-only reconstruction of 2000 events takes seconds; D5 full-detector reconstruction dominates (Step 0 measures T) |
| code experiment | the above plus one incremental build and full G4 on every dataset; a clean build (30 to 60 minutes) only when the incremental one fails | EICrecon `AGENTS.md` |
| experiments per run before a checkpoint | 5 (held-out check, report, question sweep); the run ends for user review after 10 | the ilreco journal rule |
| farm (Phase 4) | one array per (configuration, energy): 20 tasks of 5 files, `%16`, ≤ 4 h each, submitted one after another; six arrays in all | the farm rules; ≤ 200 tasks per run |
| reading plots | once per checkpoint, on the current best; the G diagnostics are numbers | token thrift |

## Review delivery

When the user is remote, every checkpoint sends to the chat: the checkpoint
section of the phase report, the current best's benchmark plots (PDF), and
`space/QUESTIONS.md` when it gained a question. Otherwise the files are
named in STATUS.md.

## Frozen after Phase 0

`{space}/FROZEN` (read by `.claude/hooks/protect.py`) lists, after Phase 0:
every submodule except the owned ZDC files of `{eicrecon}` (list in
`docs/zdc-problem.md`; `LambdaReconstruction*` is NOT among them through
Phase 3), `configs/datasets.yaml`, `configs/metrics.yaml`, the experiment
configs of the references, `scripts/13*` (the gates), `scripts/400_scoreboard.py`,
`scripts/410_truth_match.py`, `scripts/700_benchmarks/`,
`{space}/perf/manifest-datasets.json`, `{space}/perf/references.json`,
`{space}/perf/noise-validation.json`, and the three protocol files. A change
to any of them is a question, never an edit.

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
