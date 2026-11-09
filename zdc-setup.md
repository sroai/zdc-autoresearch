# ZDC program — setup file

Everything specific to this program lives here: names, pins, datasets,
metrics, budgets, farm paths. `work-common.md` holds the rules of every
run; `zdc-autoresearch-loop-v3.md` holds the phases (v2 holds the
Step 0 tables of the finished Phases 0 and 1). Every number that
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
| `{image}` | `eicweb/eic_xl:26.11.0-stable` (digest: `eicweb/eic_xl@sha256:37e7fb527c8b3421bf2d353f4fc3146b1efb07a3a07ebd01bbced8417d29add3`); on ifarm `/cvmfs/singularity.opensciencegrid.org/eicweb/eic_xl:26.11.0-stable` |
| `{wrapper}` | `scripts/100_in_container.sh` — runs one command inside `{image}` with `{repo}` at `/work` and `{data}` at `/data`, EIC environment loaded |
| `{eicrecon}` | `submodules/EICrecon` at `e5e2a60c60b6a10a25cbe35497da1d4996a492df` (main, 2026-11-04) |
| `{pr}` | EICrecon PR 3064, head `fdbb773d6e4f03d034c843dfffce391f625f3a93`, base `66b8cf62` (14 commits behind the pin), branch `baptiste/zdc-clustering-calibration`; R1 is its three-file diff applied to the pin (`space/notes/patches/R1_pr3064.patch`). Its head moved to `92288da4` on 2026-11-05 (a merge of main only; the three files unchanged); CONFLICTING with main since PR 3114 merged |
| `{pr3114}` | EICrecon PR 3114 (photon box 100/12 → 110/22 mm), MERGED 2026-11-05 21:08 UTC, backported as 3117; parameter-tier on the pin = reference R2 |
| `{pr3063}` | EICrecon PR 3063 (Λ mass windows removed, IDOLA on every triplet, χ² ranking), head `364a310a`, OPEN, 18 commits behind main; `LambdaReconstruction.cc` is unchanged on main since the PR's base, so its one-file diff applies to the pin = reference R3 (`space/notes/patches/R3_pr3063.patch`, Phase 3 Step 0 writes) |
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
the full detector `epic_craterlake` (D-user-8), which carries the ZDC with the
7 cm LYSO crystal ECal in front of the SiPM-on-tile HCal (`ZDC_Crystal_LYSO.xml`,
`ZDC_SiPMonTile.xml`, as in every physics sample) and the beamline material in
front of it. Step 0 found that the ZDC-only configurations
(`epic_zdc_lyso_sipm`, `epic_zdc_sipm_on_tile_only`) give empty ZDC neutrals
and Λs at the pin (finding F5); ZDC-only points made before that finding are
kept under `{data}/datasets_zdconly/` as a material-free cross-check of the
cluster-level cells. Step 0 verifies the files are present inside the
image before anything else. Every generator gets an explicit seed (the
benchmark macros clock-seed when given 0).

| id | content | generator | detector config | size (Step 0 confirmed 2026-11-05: every count in `space/perf/manifest-datasets.json`) | role |
|---|---|---|---|---|---|
| D1 | π⁰ gun, θ 0 to 4 mrad around the proton axis | `{benchmarks}/benchmarks/zdc_pi0/analysis/gen_pi0_decay.cxx` | `epic_craterlake` | p = 50, 60, 70, 80, 100, 130, 160 GeV; 2000 events each (the macro generates 6× and npsim keeps the first 2000 accepted); seed 1. 20 and 30 GeV accept no event (opening angle ≥ 2m/E exceeds the 8 mrad face for a decay at the IP; D-default-16) |  search set (S1 diagnostic) |
| D1h | the same, held out | same | same | p = 50, 70, 100 GeV; 2000 events; generator and npsim seed 101 | held-out (checkpoints only) |
| D2 | photon gun, θ 0 to 4 mrad | the seeded python gun of `scripts/110_generate_guns.py` (the kinematics of `gen_particles.cxx`, which has no seed argument; D-default-17) | same | p = 20, 30, 50, 70, 100, 150, 200, 275 GeV (the benchmark's list plus the low Λ-daughter energies); 1000 events each; seed 1 | search set and guard (S2) |
| D3 | neutron gun, θ 0 to 4 mrad | the seeded python gun of `scripts/110_generate_guns.py` (uniform θ inside 4 mrad around the proton axis); the benchmark's `gen_forward_neutrons.cxx` hard-codes 100 GeV and 6 mrad and runs on the full detector, so it is not used | same | p = 20, 50, 100, 150, 200, 275 GeV; 1000 events each; seed 1 | guard (S3) |
| D4 | Λ gun, decays to n π⁰, all three daughters inside 4 mrad at the ZDC face (the generator's acceptance cut) | `{benchmarks}/benchmarks/zdc_lambda/analysis/gen_lambda_decay.cxx` | same | p = 100, 125, 150, 175, 200, 225, 250, 275 GeV; 2000 events each; seed 1 | search set: the selector S0 and the outcome S4 |
| D4h | the same, held out | same | same | p = 125, 175, 250 GeV; 2000 events; seed 101 | held-out (checkpoints only) |
| D4n | noise validation | same | same | p = 175 GeV; 2000 events; seeds 2, 3 (with seed 1 of D4: three independent samples); likewise D1 at 100 GeV seeds 2, 3 | Step 0 item 13 only |
| D5 | DIS, the CI's guard samples | npsim (`scripts/113_simulate_dis.py`) of the EVGEN files the EICrecon CI uses for its 18x275 pages: pythia8.316 NC Q² 100–1000 run000 and pythia6-eic SIDIS Q² 0–1 run1.ab on `/jlab-osdf-ro/eic/EPIC/volatile/EVGEN/` (D-default-14: the XRootD campaigns holding these samples predate the 26.05 square-tile ZDC) | `epic_craterlake` (the image has no `epic_craterlake_18x275.xml`) | sized in **ZDC clusters**: ≥ 2000 R0 clusters per sample (36 φ bins × 50 entries with margin); Step 0 raises the chunk count until the R0 cluster count is met and records clusters per event | guard (G1 to G4): the review findings reproduced on the reviewers' own inputs |
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
| R2 | R0 + `{pr3114}` (parameter tier, `configs/experiments/R2_pr3114.yaml`; D-user-15) | **the baseline of every Λ comparison from 2026-11-06** (main carries the box fix); S0 identical to R0 |
| R3 | R2 + `{pr3063}` (one-file patch on the pin, build label `R3`; Phase 3 Step 0 writes) | the Λ chain upstream proposes; B9d is judged against it, and `414`'s `vertex` pairing is its pre-registered prediction |
| R1p | R1 + `{pr3114}` (parameter tier on the R1 build) | the author's package (clustering + box) as the author tuned it; owed to a fair review of PR 3064 |

All reference reconstructions run single-threaded (`-Pjana:nthreads=1`), so
that outputs are deterministic and G4 can demand identity (the PR's CI shows
Δ 840 on the multithreaded page against Δ 148 single-threaded for the same
sample). Their scoreboard rows and the sha256 of their output files are in
`{space}/perf/references.json` (*Step 0 filled 2026-11-05*: sha256 of 102 R0, 102 R1 and 8 Rt outputs; the rows R0_stock, R1_pr3064, Rt_truthchain lead `{space}/perf/scoreboard.csv`; determinism verified on D4 175 GeV, 9048 non-ZDC and 960 ZDC leaves identical in three runs). The reference outputs live
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
| S4a | D4 | Λ reconstruction efficiency, **truth-matched** (`S4a_tm`): events with a `ReconstructedLambdas` entry built from clusters associated to the true n, γ, γ (each with purity ≥ 0.8) and mass inside the fixed scoring window, divided by generated events, per momentum; beside it the raw count-any-Λ fraction, and the Rt ceiling | outcome; **the selector of the Λ family** (D-default-25) and, once B9d is ACCEPTED, a co-selector of clustering experiments (loop v3, Phase 3) |
| S4o | D4 | the Λ chain **offline on real clusters** (`scripts/415_lambda_chain_offline.py`, Phase 3 Step 0 writes): the stock pairing and `414`'s `vertex_fixed` pairing applied to each row's best-matched clusters with the row's calibration, scored in the fixed window; *tagged* (needs the photon tag) and *truth-identified* variants, per accepted event and per thrown | reported beside S0 for every row; the number that ties a clustering row to a Λ yield |
| H | D4 | the headline side table `{space}/perf/headline.csv` (`scripts/441_headline.py`): S0all, S4a_tm and S4o per thrown Λ → nπ⁰ (× the acceptance of `413`) per momentum, the mean over 100–275 GeV and the 275 GeV value | every brief report line and every deck number comes from it (D-user-20) |
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
*Step 0 filled 2026-11-05*: R0 and R1, 26 metric tests, spread / quoted error 0.26–1.97, none below p = 0.01). Overfitting to the fixed seeds: the held-out D1h and D4h
at every checkpoint.

Acceptance (Phases 2 and 3): ACCEPTED when S0all improves significantly in
the paired test (and no S0 component falls significantly), S2 scale, S3 raw
sum, S3 clusters per neutron, S4b and S4c stay inside their limits, G4
passes, and G1 to G3 are inside the limits the user set. A held-out check
that does not reproduce the gain reverts it. Everything else is REJECTED
with the measured deltas kept. Calibration refits are never experiments:
they follow an accepted clustering and are fit on D2 and D3 truth
(`scripts/420_refit_calibration.py`), never on S4a.
*D-user-13 (Q7, 2026-11-05)*: every candidate's S2 scale is judged on the
residuals of its own refit (`300_run_experiment.py` runs 420 after the
scoreboard); the γ-tag efficiency is reported beside it. *D-user-12 (Q8)*:
the S3 raw-sum guard is one-sided (fails on a drop > 5 %; an increase passes
when σ/mean does not worsen and clusters per neutron stays in its limit).
*D-user-26 (Q11, 2026-11-06)*: the guard applies at D3 momenta ≥ 50 GeV
(`S3_raw_sum_guard_min_momentum_gev`); 20 GeV is reported beside it. *D-user-16 (Q9)*: a one-sided photon
raw-sum guard on D2 (drop ≤ 5 %, `430_shape_decayz.py`). *D-user-17 (Q10)*:
S2 passes when |μ/E − 1| − 2σ ≤ 0.05, σ the refit residual's statistical error.

Frozen through Phases 1 to 3 unless the Phase 0 checkpoint opens them:
every parameter of `ReconstructedLambdas` (`pi0Window`, `lambdaMassWindow`,
`iterations`, `globalToProtonRotation`) and the `LambdaReconstruction`
source. Its IP-pointing π⁰ preselection caps S4a (the review's estimate:
only decays within about 3.6 m of the IP pass the ±10 % π⁰ window); Rt
measures that cap, and the cap is a finding for upstream, not a knob.
*D-user-14 (2026-11-05)*: checkpoint question 3 opened `LambdaReconstruction`
from Phase 2 on (source and `pi0Window`, `lambdaMassWindow`, `iterations`;
`globalToProtonRotation` stays frozen). Its changes are a separate family
with S4a_tm as selector under the fixed scoring window (D-default-25); the
cap is then a knob as well as a finding for upstream.

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
  the measured cluster count at Step 0, not by events. *Step 0 filled 2026-11-05*: NC Q² > 100
  0.555 R0 clusters per event → 40 chunks (4000 events, 2220 clusters); SIDIS Q² < 1 0.984 per
  event → 22 chunks (2200 events, 2164 clusters).

## Budgets

| item | value | source |
|---|---|---|
| parameter experiment (no rebuild) | every dataset D1–D5 reconstructed with the **restricted output collections** (`MCParticles`, `EventHeader`, `.*FarForwardZDC.*`, `Reconstructed.*Neutrals.*`, `ReconstructedLambda.*`; the template `configs/experiments/_template_parameter.yaml`, Phase 3 Step 0 writes); G1–G3 come from the ZDC clusters of D5, G4 is static (loop rule) and the gate table records the compare of the owned collections; target ≤ 10 GB and ≤ 30 minutes wall per experiment (T measured on one D4 file and one D5 chunk at Phase 3 Step 0, *written here then*). Try 1 wrote every collection on every dataset: 63 GB and about one hour per experiment | ZDC-only reconstruction of 2000 events takes seconds; D5 full-detector reconstruction dominates. *Step 0 filled*: T per 1000 events, single-threaded, R0: D1 279 s, D2 236 s, D3 415 s, D4 504 s, D5 NC 2417 s, D5 SIDIS 1338 s (the guns run on the full detector, D-user-8); D1–D4 (46 000 events) on 9 processes ≈ 30 min, D5 (6200 events) ≈ 25 min |
| code experiment | the above plus one incremental build, a full-collection D5 and full G4 on every dataset with the capybara reports (non-owned and ZDC views); a clean build (30 to 60 minutes) only when the incremental one fails | EICrecon `AGENTS.md` |
| checkpoint | the full-collection D5 of the current best, full G4 and the two capybara views against R0, the held-out D1h/D4h, the report, the question sweep | loop v3 |
| preflight (every launch, `300`) | free space on `{data}` ≥ 2 × the expected output of the launch and never under 150 GB; eicrecon processes running + requested ≤ cores − 2 (22 on the workstation); after every chain: each output has its per-file JSON and a non-empty log, no `ENOSPC`/`Traceback`/`segmentation`/`timeout` in the logs, sizes within 50 % of the reference row's counterpart; any failure stops the chain before the scoreboard | try 1: /data full at 865 GB, 24 processes on 24 cores (`notes/lesson-disk-budget.md`) |
| retention | full reco ROOT only for R0, R1, R2, R3, Rt and the current best; a REJECTED row's ROOT deleted right after its verdict | D-user-19 |
| experiments per run before a checkpoint | 5 (held-out check, report, question sweep); the run ends for user review after 10 | the ilreco journal rule |
| farm (Phase 4) | one array per (configuration, energy): 20 tasks of 5 files, `%16`, ≤ 4 h each, submitted one after another; six arrays in all | the farm rules; ≤ 200 tasks per run |
| reading plots | once per checkpoint, on the current best; the G diagnostics are numbers | token thrift |

## Review delivery

When the user is remote, every checkpoint sends to the chat: the checkpoint
section of the phase report, the current best's benchmark plots (PNG), the
gate table and the capybara non-owned view, and `space/QUESTIONS.md` when it
gained a question. Otherwise the files are named in STATUS.md.

Plot format (D-user-22): every plot the program writes is a PNG under
`{space}/plots/`. A tool the program does not own that writes PDF (the
benchmark copies, ROOT macros) keeps its PDF and gets a PNG per page beside
it from `scripts/701_pdf_to_png.sh` (pdftoppm, 110 dpi), which `300` runs
after the benchmark step. Decks embed PNGs.

## Frozen after Phase 0

`{space}/FROZEN` (read by `.claude/hooks/protect.py`) lists, after Phase 0:
every submodule except the owned ZDC files of `{eicrecon}` (list in
`docs/zdc-problem.md`; `LambdaReconstruction*` is NOT among them through
Phase 3), `configs/datasets.yaml`, `configs/metrics.yaml`, the experiment
configs of the references, `scripts/13*` (the gates), `scripts/400_scoreboard.py`,
`scripts/410_truth_match.py`, `scripts/700_benchmarks/`,
`{space}/perf/manifest-datasets.json`, `{space}/perf/references.json`,
`{space}/perf/noise-validation.json`, and the protocol files (this file,
`work-common.md`, loop v2 and v3). A change to any of them is a question,
never an edit; a protocol revision between runs is a patch under
`space/notes/patches/` that the user applies (D-user-23).

## People and threads

- Baptiste Fraisse (`baptistefraisse`): author of issue #2737 and of the
  three PRs 3064 (clustering + calibration), 3114 (photon box, merged) and
  3063 (Λ chain); the MSF Λ analysis.
- Wouter Deconinck (`wdconinc`): the review finding of 2026-10-30.
- Sebouh Paul (`sebouh137`): ZDC reconstruction and benchmarks author
  (HEXPLIT, FarForwardNeutralsReconstruction, zdc_* benchmarks).
- Dmitry Kalinkin (`veprbl`): capybara, benchmark CI, the 80 GeV pion
  comment on the issue.
- Markus Diefenthaler (`mdiefent`): MSF lead.

The user posts on GitHub; the agent drafts (`{space}/reports/pr-draft.md`).
