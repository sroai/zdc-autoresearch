# ZDC autoresearch loop — version 2

Read `zdc-setup.md` and `work-common.md` first. This file is the loop: the
phases in order, each with its Step 0, its ruler and its done criterion. It
holds no program numbers; every pin, path, dataset size, metric and budget
sits in the setup file, and this file names them by section.

Version 2 applies the expert review of version 1
(`docs/expert-review-v1.md`): the selector is now a truth-matched separation
efficiency, the Λ reconstruction code and its windows are frozen while the
clustering is tuned, the neutron is guarded on raw cluster energy, the guns
run on the geometry with the LYSO crystal ECal in front of the HCal, the
noise band is a paired test on identical events plus a held-out seed set,
and the review's own mechanism for the three findings (clusters collapsing
to single subcell columns when the neighbour distance drops below the
24.4 mm subcell pitch) is written down as the first hypothesis to confirm.

## What the program produces

1. A reconstruction configuration for the square-tile ZDC that keeps each
   photon of `π⁰ → γγ` and the neutron in clusters of their own, measured
   by truth matching, with the neutron response unchanged and the three
   review findings on PR 3064 inside limits the user set.
2. The validation the reviewers asked for: benchmark plots, capybara
   comparisons and `Λ → nπ⁰` reconstruction on MSF events with enough
   statistics, as a PR draft the user posts.
3. The record: every experiment with its hypothesis, numbers and verdict,
   including the rejected ones, and the findings about code the program
   does not own.

## Words used in this file

- **reference R0, candidate R1**: the two reconstructions of the setup file
  (section References). R1 is the PR's three-file diff applied to the pin,
  never the PR's own commit (which is 14 commits behind the pin).
- **scoreboard, row**: the fixed metric set (setup file, Scoreboard), one
  row per reconstruction.
- **selector, outcome, guard, gate**: the one metric that decides (S0, the
  separation efficiency), the physics outcome reported beside it (S4a, S5),
  the metrics that must not regress (S2 scale, S3 raw sum, G1 to G3 within
  the user's limits), and G4 (non-ZDC collections identical), whose failure
  rejects without appeal.
- **paired test**: the statistical test of a change on the same simulated
  events (setup file, Noise and significance).
- **held-out set**: D1h and D4h, fresh generator and npsim seeds,
  reconstructed only at checkpoints, never used to choose.
- **parameter experiment, code experiment**: JANA `-P` overrides on the
  pinned build (no rebuild), or a patch to the ZDC-owned files (rebuild,
  patch under `{space}/notes/patches/`).
- **subcell pitch**: 24.4 mm, the HEXPLIT S2 grid shared by all layers;
  the neighbour distance acts as a step function of it (below 24.4 mm no
  lateral neighbours; 24.4 to 48.8 mm a 3×3 neighbourhood; above, 5×5).

## Files

```
{repo}/
  CLAUDE.md  zdc-setup.md  work-common.md  zdc-autoresearch-loop-v{1,2}.md
  configs/        local.yaml, ifarm.yaml (machine facts); datasets.yaml, metrics.yaml (frozen after Phase 0);
                  experiments/<name>.yaml (one per experiment: eicrecon ref + parameters)
  scripts/        1xx foundation, 2xx understanding, 3xx experiments, 4xx evaluation, 5xx farm,
                  7xx figures (7xx/benchmarks: the benchmark plot scripts with EICrecon main's collection names)
  zdc/            the shared Python the scripts import
  submodules/     EICrecon, detector_benchmarks, epic-capybara, meson-structure, skill-eicrecon (frozen except the ZDC-owned files)
  docs/           zdc-problem.md, ifarm-tunnel.md, expert-review-v1.md
  space/          STATUS.md, QUESTIONS.md, LEDGER.md (phases), EXPERIMENTS.md (experiments), FROZEN, notes/, reports/, plots/, perf/
{data}/           build/, install/, datasets/ (frozen inputs), reco/<experiment>/<dataset>/, logs/, gate-controls/
```

## Every run

After the start protocol of `work-common.md` (STATUS.md, then QUESTIONS.md):

1. `scripts/101_check_environment.sh` — the image digest, the submodule
   SHAs, the dataset manifest and the reference checksums must reproduce. A
   mismatch follows the "Step 0 reference numbers no longer reproduce" row.
2. If Phase 0 is done: `scripts/131_prove_gates.sh --check` re-runs the gate
   on the stored damaged copies. A gate that passes a damaged copy follows
   the "want to change the gate" row — the ruler is broken.
3. If an EICrecon install was rebuilt since the last run: the determinism
   check (R0 on one D4 file twice, outputs identical).
4. Resume the phase STATUS.md names.

## Phase 0 — the foundation

Everything the loop measures against is built here, proven, and frozen.
Nothing in later phases changes a file this phase freezes. The phase ends
with the scoreboard rows of R0 and R1 on every dataset, the truth-cluster
ceiling, the paired-test validation, the frozen list in place, and the six
questions of the Phase 0 checkpoint written for the user.

Ruler of this phase: the EICrecon `AGENTS.md` build recipe, the benchmark
generators as they are, the official campaign files as they are, and the
truth associations EICrecon writes. Phase 0 is the one phase where editing
the gate scripts, the metric scripts and the benchmark plot copies is normal
work.

### Step 0 items, each with its decisive outcome

| # | item | decisive outcome (write it to the phase report with the evidence) |
|---|---|---|
| 1 | Pull `{image}`, record its digest in the setup file. Inside it: `thisepic.sh` loads; `$DETECTOR_PATH/epic_zdc_lyso_sipm.xml`, `epic_zdc_sipm_on_tile_only.xml`, `epic_craterlake_18x275.xml` and the MSF config exist; `eicrecon --version`, `npsim --version`, ROOT version printed; `git log -1` of the epic the image ships, to confirm `ZDC_SiPMonTile.xml` is unchanged since epic PR #1070. | The gun configuration with LYSO exists in the image, or Phase 0 stops with a question. The epic ZDC geometry in the image is the 26.05 square-tile geometry (the MSF 26.06 files are compatible at the hit level) or the compatibility gate (item 6) is already decided. |
| 2 | Build `{eicrecon}` at the pin into `{data}/install/eicrecon-<sha>` with `scripts/102_build_eicrecon.sh`. Make the R1 patch: in the submodule, `git fetch origin pull/3064/head` (a read; the PR head is not in the clone until fetched), then `git diff 66b8cf62 fdbb773d -- src/detectors/ZDC/ZDC.cc src/algorithms/reco/FarForwardNeutralsReconstructionConfig.h src/global/reco/reco.cc` saved as `{space}/notes/patches/R1_pr3064.patch`; apply it to the submodule, build with `--label R1`, restore the tree (`git checkout -- .`, allowed by the Git section). Record build times. | Both installs exist, `eicrecon` from each runs on one event, and the R1 patch applies to the pin without conflict (or the conflict is the first finding). |
| 3 | Generate the guns D1 to D4 and the held-out D1h and D4h with `scripts/110_generate_guns.py` from `configs/datasets.yaml` (explicit seeds — the generators clock-seed when given 0; the LYSO+SiPM configuration; D3 as an npsim particle gun scan, since the benchmark's neutron generator hard-codes 100 GeV). Write the sha256 manifest with event counts. | Every file in the manifest with its event count; a 10-event dry run of every generator signature passed first; npsim bit-reproducibility recorded (same seed twice → same sha256, or "not reproducible, the count is the identity"). |
| 4 | Fetch D5 with `scripts/111_fetch_dis_inputs.sh`: the newest campaign on XRootD with the two sample paths; fetch until the **cluster** budget of the setup file is met (count ZDC clusters with a first R0 reconstruction of the fetched files; the DIS samples have a forward neutron in a minority of events). Fallback: npsim of the EVGEN files the EICrecon CI names. | D5 exists with ≥ the minimum R0 ZDC clusters per sample, the campaign name is in the config, and the choice is a `D-default` entry. |
| 5 | D6a: list the local MSF files (`/data/meson-structure-2026-07/dd4hep/9x130`, names like `msf_9x130_1000evt_NNNN`), verify each opens and holds 1000 events, find the campaign's detector configuration and whether the `dd4hep` step read `bg_merged` (background) from the campaign documentation in `{msf}/docs/campaign-2026-07/` and the pipeline configs in `{msf}/simulation-pipeline/configs/` (the nested `msf-simulation-pipeline` submodule; the scaffold initialized it, and on a fresh clone the one git read allowed here is `git submodule update --init submodules/meson-structure/simulation-pipeline`), write the manifest. Confirm the farm file-name pattern of D6b from the same documentation. | D6a's file list, event counts, detector configuration and background status are recorded; the D6b pattern in `configs/datasets.yaml` is confirmed or corrected. |
| 6 | **MSF compatibility gate.** Reconstruct one D6a file with R0 and compare **RawHits and RecHits only** (cellID decode, hit count and energy sum per event; tolerance: identical) against the campaign's own `reco` file of the same index; never the clusters (a 26.06-era EICrecon made them). | Hits identical → D6 stays in the program. Otherwise D6 is dropped, S5 moves to the Λ gun only, and a BLOCKING question asks whether to simulate fresh MSF events on the farm. |
| 7 | **The neighbour-distance tier.** Decide, as a `D-default`, between (a) exposing the two XY distances as a 2-vector parameter in dd4hep units in `ImagingTopoCluster_factory.h` (shared with BEMC and FHCAL; G4 on every dataset must stay identical for R0 before and after) and (b) running the three distance settings that matter (below the subcell pitch, 3×3, 5×5) as code-tier builds. Default: (b); the parameter is a Phase 3 nicety and an upstream API discussion. | The decision recorded; if (a), G4 passes on every dataset and the patch is the first entry of `{space}/notes/patches/`. |
| 8 | Reconstruct R0 and R1 on every dataset with `scripts/120_reconstruct.py` (single-threaded, `-Pjana:nthreads=1`, so that outputs are deterministic for G4); record wall time per 1000 events. R1 from the patched build and R1 from the parameter config (`configs/experiments/R1_pr3064.yaml`, without the distances unless item 7 chose (a)) must agree on every ZDC collection; where they cannot (the distances), the ledger says so. | The scoreboard rows of R0 and R1 are the first two in `scoreboard.csv`; the reference output checksums are in `references.json`; the determinism check (one D4 file twice, identical) passes. |
| 9 | **Switch tests.** Each parameter of the PR on the dataset where it acts: clustering parameters on D1, the γ coefficients and `gammaMaxLength` on D2, the neutron coefficients on D3; stock value vs PR value; the ZDC output must differ. `eicrecon` aborts on an unregistered name (parameter strictness 2), so the test catches only registered-but-inert parameters. | Every PR parameter demonstrably changes the output, or it is a finding and a question before any verdict rests on it. |
| 10 | **Gate proofs.** `scripts/131_prove_gates.sh`: damage one non-ZDC leaf and one ZDC leaf of an R0 output; the gate must FAIL on the first, PASS on the second, and `--zdc` must FAIL on the second; capybara must report the damaged leaf. Store the damaged copies. Also: find which leaves carry the Δ 40 of the PR's `tracking_only` capybara page, so that G4's prefix list is complete (`ReconstructedB0EcalNeutrals`, `ReconstructedEcalEndcapPNeutrals`, `ReconstructedLFHCALNeutrals` are outputs of the neutrals factory and are owned, see the setup file). | The gate has been seen to fail; the stored copies reproduce the verdicts; the owned-collection list is complete. |
| 11 | **Truth matching and the scoreboard.** `scripts/410_truth_match.py` on R0 and R1 for D1 to D4: per true γ and n, the best-matched cluster's purity and the fraction of the particle's deposited energy it holds, from `HcalFarForwardZDCClusterAssociations`; S0 per momentum. `scripts/400_scoreboard.py` for every dataset; the collection and association field names of `configs/metrics.yaml` verified against the files (correct the file once, record it). | Every scoreboard cell has a value; a cell that cannot be computed is a finding, not a blank. S0 of R0 shows the merging (γ purity low at the D4 momenta) and S0 of R1 shows what the PR bought and cost. |
| 12 | **Truth-cluster ceiling.** A code-tier Phase 0 build (`--label truthchain`) with one ZDC-owned change in `reco.cc`: a second `FarForwardNeutralsReconstruction` instance and a second `LambdaReconstruction` instance reading `HcalFarForwardZDCTruthClusters`, writing `ReconstructedLambdasTruth`. Run on D4; S4a from truth clusters per momentum, against true decay z. | The ceiling of S4a with perfect clustering is recorded per momentum, and the IP-pointing π⁰-window cap (the review's estimate: only decays within about 3.6 m of the IP pass; near zero at 100 GeV) is confirmed or corrected with numbers. This is also the first finding about `LambdaReconstruction` for the report. |
| 13 | **Noise and significance.** The determinism check; the paired test implemented in `scripts/400_scoreboard.py --compare` (McNemar on discordant events for efficiencies, event bootstrap for fitted μ and σ); three independent seeds at one momentum of D1 and D4 reconstructed with R0 to show that the analytic paired error is honest (the seed spread of the metric lies within its quoted error). | `{space}/perf/noise-validation.json` holds the three-seed spread against the analytic error per metric; the paired test is what `--compare` prints from here on. |
| 14 | **Benchmark plots.** The four benchmark plot scripts copied to `scripts/700_benchmarks/` with EICrecon main's collection names (`ReconstructedLambdas`, `ReconstructedHcalFarForwardZDCNeutrals`); `scripts/401_benchmark_plots.sh` runs the copies on R0 and R1. The submodule stays untouched. | Each output PDF has at least one non-empty histogram per momentum, checked by the script (not by looking). |
| 15 | **Review findings as numbers.** `scripts/200_cluster_distributions.py` on D5 for R0 and R1 with the three column diagnostics (distinct subcell (x, y) per cluster; intrinsic θ beside φ; lateral width √λ2 against energy). The predictions to confirm, written first: with the PR's 14.6 mm distance, the fraction of clusters with exactly one distinct (x, y) is above 0.9 and the fraction of φ within 5° of ±180° is above 0.9 (the review's mechanism); with R0 both are small. | The three findings are reproduced on the reviewers' own inputs with numbers, and the mechanism prediction is confirmed or refuted. |
| 16 | Freeze: copy `space/FROZEN.after-phase0` to `space/FROZEN`, fill every *Step 0 fills* value of the setup file, write the Phase 0 report and the **Phase 0 checkpoint questions** (next section). | The hook refuses a test edit under `submodules/detector_benchmarks` and under `LambdaReconstruction.cc`, and allows one under `src/detectors/ZDC`. |

### Phase 0 checkpoint — the six questions the user decides before Phase 1

Written as plain questions with the agent's recommendation as the default
(the user answers `Q<N> <letter>` or `all defaults`); each has a
`D-default` already applied so Phase 1 can start on `all defaults`:

1. Gun geometry: LYSO+SiPM (default), SiPM-only, or both.
2. Selector: S0 truth-matched separation efficiency (default) or S4a.
3. Whether `LambdaReconstruction` may change at all in this program,
   including its IP-pointing π⁰ preselection (default: no; it is shared
   physics code used by MSF; a finding and a proposal instead).
4. The numeric limits for G1 to G3 (defaults proposed from the R0 numbers
   and the column diagnostics of item 15).
5. Whether the shared `ImagingTopoCluster` algorithm, or switching the ZDC
   to the existing Island chain with splitting, is in scope for Phase 3
   (default: both, under G4).
6. Whether D6 contains machine background (from item 5) and whether that
   matters for S5 (default: report both if two D6 variants exist).

### Done criterion

All 16 items have their decisive outcome recorded in
`{space}/reports/phase0_foundation.md`, `scoreboard.csv` holds the R0, R1
and truth-chain rows, `references.json` and `noise-validation.json` exist,
`space/FROZEN` is in place, the six checkpoint questions are in
`QUESTIONS.md`, and STATUS.md line 1 is
`PHASE0 DONE — report at space/reports/phase0_foundation.md`.

## Phase 1 — confirm the mechanism and seed the backlog

Goal: confirm, with four reconstructions, the one mechanism behind the three
review findings, measure what PR 3064 bought and cost in S0 terms, and seed
the experiment backlog.

Step 0: the R0, R1 and truth-chain rows side by side at the top of
`{space}/reports/phase1_dissection.md`; the hypotheses below written in
`EXPERIMENTS.md` before any run.

Work, in order:

1. **Clustering only, four runs.** R0 + each of the PR's three clustering
   changes that are parameters (`neighbourLayersRange`, `minClusterCenterEdep`
   + `minClusterNhits` as the threshold pair, and the distance as the
   code-tier 1×1 setting), and R1 − each. The PR's calibration coefficients
   are excluded: they were fitted on R1's column clusters and are
   predictable garbage on any other clustering; calibration is a refit per
   clustering (step 3).
2. **The mechanism as hypothesis.** H1: the distance below the subcell pitch
   alone produces G1 (φ at ±180°, single-column clusters) and most of G2
   and G3; the threshold pair keeps the shards. Predicted numbers from
   Phase 0 item 15. Confirmed or refuted with the column diagnostics.
3. **Calibration refit protocol.** For any clustering, the γ and n `a·E^b`
   coefficients are refit on D2 and D3 **truth** (cluster energy of the
   truth-matched cluster against true energy), never on S4a; the refit is a
   script (`scripts/420_refit_calibration.py`, written here) that prints
   the coefficients and the residual scale per momentum. The PR's
   coefficients are compared with the refit on R1's clustering.
4. **Seed the backlog**, ordered, each with its mechanism and predicted
   S0 effect: `minClusterHitEdep` scan (the chaining threshold, 0.5 to 4
   MIP-equivalent per subcell; 1 MIP = 630 keV per tile = about 160 keV
   per subcell); `minClusterCenterEdep` and `minClusterNhits` at the 3×3
   distance; `neighbourLayersRange` 1 to 3 at 3×3; the three distance
   settings; `sectorDist`; HEXPLIT `Emin_in_MIPs` and `delta_in_MIPs`; the
   Island chain with `splitCluster = true` feeding the CoG as the first
   Phase 3 candidate.
5. **S5 quick**: R0 and R1 on D6a; Λ candidates per 1000 events, ZDC-only
   and all-calorimeter separately. A report line.

Done: H1 confirmed or refuted with numbers, the PR's S0 balance (γ purity
gained vs neutron energy lost) in the report, the backlog ≥ 8 entries, the
calibration refit script proven on R0 (refit reproduces the stock
coefficients within their errors, or the discrepancy is a finding).

## Phase 2 — the parameter loop

Goal: the best parameter set of the ZDC clustering chain on the selector,
with mechanisms, without any code change.

Step 0: the Phase 1 backlog, the current best (R0 at first), the paired-test
errors from `noise-validation.json`.

### The experiment loop

One entry per experiment in `{space}/EXPERIMENTS.md`, written in two steps:

```markdown
## E<N> <date>: <one-line change>
tier: parameter | code
config: configs/experiments/E<N>_<name>.yaml   (and notes/patches/E<N>_<name>.patch for code)
hypothesis: <falsifiable, written BEFORE the run: which scoreboard cells move, which direction, by how much, and the mechanism>
expected cost: <minutes; reco wall time from T>
--- after the run ---
row: <the scoreboard.csv row id>
result: <S0 per momentum with the paired test; the cells that moved>
guards: S2 scale <in limit / out>, S3 raw sum <…>, S4b <…>, G4 <PASS/FAIL>, G1..G3 <in the user's limits / out>
verdict: ACCEPTED | REJECTED | INCONCLUSIVE, one line why
understanding: <what is now believed about the chain>
next: <the next hypothesis, and why>
```

Rules of the loop:

1. **Hypothesis first.** If the expected effect cannot be stated with a
   mechanism, the experiment is not run; it goes to the report as a
   recommended next step.
2. **One change.** One parameter, or one named pair when the mechanism
   predicts an interaction.
3. **Run** `scripts/300_run_experiment.py configs/experiments/E<N>_<name>.yaml --phase phase2`:
   reconstruction on D1 to D4, truth matching, the scoreboard row with the
   paired test against the current best, the column diagnostics.
4. **Gate G4**: for parameter experiments, static (the parameter prefix is
   a ZDC factory and strictness 2 accepted it) plus a full G4 at every
   checkpoint; for code experiments, full G4 on every dataset. A failure
   is REJECTED, no exceptions.
5. **Verdict** by the acceptance rule of the setup file: S0 improves
   significantly in the paired test, S2 scale, S3 raw sum and S4b inside
   their limits, G1 to G3 inside the user's limits. ACCEPTED → the config
   becomes the current best. REJECTED on a premise that may not last → note
   what would revive it.
6. **Calibration** is never an experiment of its own: after an ACCEPTED
   clustering change the refit script runs and its coefficients become part
   of the current best; S4a and S5 are then reported with them.
7. **Move-on rule**: two consecutive experiments on one parameter family
   (chaining threshold; seed thresholds; distance; layer range; HEXPLIT)
   each not significant or REJECTED → record the family's ceiling, move on.
8. **Checkpoints**: after every 5 experiments, the held-out set D1h and D4h
   is reconstructed with the current best and its S0 compared with the
   search-set S0 (an accepted chain whose held-out S0 does not reproduce
   the gain is reverted to the previous best, and the ledger says so); the
   report is updated; the question sweep runs. After 10, the run ends for
   user review (`PHASE2 CHECKPOINT — waiting for user review`), unless the
   user's answer to the last checkpoint question was `continue`.
9. **Plots are read once per checkpoint**, on the current best; the G
   diagnostics are numbers.

Done: the backlog is empty, every family has a recorded ceiling, the
current best has its benchmark plots, its held-out confirmation and its G1
to G3 numbers, and the report's "Next run recommendations" section names
what a code change could reach that parameters cannot.

## Phase 3 — the algorithm loop

Goal: what parameters cannot reach. Same loop, same ruler, code tier.

Allowed files: the ZDC-owned list (`docs/zdc-problem.md`), plus the shared
`ImagingTopoCluster` only if the Phase 0 checkpoint question 5 allowed it,
with full G4 on every dataset (BEMC and FHCAL use the same algorithm).
`LambdaReconstruction` stays frozen unless question 3 opened it.

Additions to the loop:

- Every code experiment is a patch `{space}/notes/patches/E<N>_<name>.patch`
  against the pin, applied to the submodule for the build (`--label E<N>`)
  and reverted after the verdict (kept when ACCEPTED, as the new base
  patch). With `{git}` on, a commit on the submodule branch instead.
- A rebuild is incremental; a clean rebuild only when the incremental one
  fails. The build log is read with `tail`/`grep` only. The determinism
  check runs after every rebuild.
- Candidates, in order, each written as a hypothesis with a mechanism before
  it runs: (1) feed the existing `HcalFarForwardZDCIslandProtoClusters`
  (subcell island clustering) with `splitCluster = true` into the CoG
  instead of the topological clusters — it exists in `ZDC.cc` and nothing
  consumes it; (2) a two-pass clustering (coarse neighbours for the
  neutron, fine for photons, merged by a shape test); (3) a photon-first
  split of a merged cluster from its EM-like core; (4) the LYSO ECal
  clusters as photon candidates in `FarForwardNeutralsReconstruction`
  (it never reads them today); (5) a cluster-shape computation that gives
  a meaningful intrinsic φ for column-like clusters.
- The EICrecon review checklist
  (`submodules/skill-eicrecon/.../eicrecon-pr/SKILL.md`) applies to every
  accepted patch before Phase 4; `clang-format` and the unit tests
  (`ctest --test-dir build`) pass.

Done: as Phase 2, plus the accepted patches pass the checklist and the
tests, and the findings index lists every defect met on the way (the
`LambdaReconstruction` mm/cm fallback, the HEXPLIT S2 subcell dimensions,
the stale benchmark names, and whatever else).

## Phase 4 — confirmation at scale and the deliverable

Goal: validate the accepted configuration where the reviewers asked, and
hand the user a PR draft.

1. **Farm confirmation**: D6b reconstructed with R0, R1 and the accepted
   configuration: one Slurm array per (configuration, energy), 20 tasks of
   5 files each, submitted one after another under the throttle
   (`scripts/500_farm_array.py`, ifarm-slurm skill); output collections
   restricted to MCParticles, the ZDC chain, the four `Reconstructed*Neutrals`
   and the Λ collections, so that tracking does not run; S5 computed on the
   farm (`scripts/402_lambda_msf_metrics.py`) ZDC-only and all-calorimeter
   separately, with the acceptance row (events with ≥ 1 HCal RecHit and the
   three daughters inside the face) so the S5 ceiling is known; small
   results pulled. The statistics budget of the setup file says what the
   comparison can resolve.
2. **Benchmark plots** for the three configurations on every gun dataset
   from the `700_benchmarks` copies, and the capybara reports R0 vs accepted
   on D5 and D6a.
3. **The PR draft** `{space}/reports/pr-draft.md`: motivation, the
   mechanism behind the three review findings with the column diagnostics,
   the scoreboard before/after with the paired-test errors, the held-out
   confirmation, the Λ confirmation with its statistics, the parameter
   table, the patches, and the separate findings (stale benchmark names as
   a detector_benchmarks PR; the `LambdaReconstruction` cap as an issue).
   The user posts it (as a review reply on #3064 or a new PR).
4. **Slides** (`scripts/700_build_slides.py`, the slides skill): the story
   for the ZDC and MSF meetings, numbers loaded from `scoreboard.csv`.

Done: the PR draft and the deck exist, S5 on D6b is in the report with its
error, and the question sweep names what the user must decide before
posting.

## Reporting and checkpoints

- `{space}/reports/phase<N>_*.md` exists from the phase's Step 0 and grows
  at every verdict: the scoreboard rows, the waterfall of accepted changes,
  the rejected hypotheses with why, the G1 to G3 numbers, "Defaults you may
  veto", "Next run recommendations".
- `{space}/perf/scoreboard.csv` is the one table every number comes from;
  the slides and the PR draft load it at build time.
- Plots under `{space}/plots/phase<N>/<experiment>/`, never overwritten;
  `{space}/plots/current/` mirrors the latest best.
- Every 5 experiments: held-out check, report, question sweep. Every 10:
  the run ends for review.
- When the user is remote (`zdc-setup.md`, Review delivery): the report
  section of the checkpoint and the current best's benchmark plots are
  sent to the chat with the file-sending tool.

## Rows for the decision table

Checked before the table of `work-common.md`, top to bottom, first match wins:

| you observe | response |
|---|---|
| the gun configuration with LYSO is missing from the image | **STOP**: question (SiPM-only for everything, or a different image tag) |
| D6 fails the MSF compatibility gate (Step 0 item 6) | **PARK** D6 with the question; continue with the guns and D5 |
| the R1 patch does not apply to the pin | **FIX** by resolving the conflict in the three files only, record it; if `reco.cc` moved the factory, that is a finding |
| a PR parameter fails its switch test (Step 0 item 9) | finding + **ASK**; no verdict may rest on that parameter until answered |
| G4 fails on a code experiment | **REJECTED** and a finding (a shared algorithm or a shared output moved); never waive |
| S0 improves but a guard (S2 scale, S3 raw sum, S4b) is out of limit | **REJECTED**; the mechanism of the loss is the next hypothesis, not a waiver |
| the held-out S0 does not reproduce an accepted gain | revert to the previous best, record the overfit, and the next experiment tests the same idea with a mechanism that predicts the held-out result |
| a wish to change a window of `LambdaReconstruction` (`pi0Window`, `lambdaMassWindow`, `iterations`) | frozen through Phase 3 unless checkpoint question 3 opened it → **PARK** as a proposal |
| the farm array fails more than 5 % of its tasks | **FIX** by resubmitting the missing deliverables once; still failing → finding + ASK |
| an idea needs a geometry (epic) change | out of scope → **PARK** as a proposal; no work on it |
| the reconstruction wall time doubles | report line; **ASK** whether the cost is acceptable; the verdict is unaffected |

## The scripts

Every script takes its paths as arguments or from `configs/local.yaml`
(`ZDC_CONFIG` selects another profile), runs with `uv run` (Python) or bash,
prints what it did and the verdict with the offending item, and exits
non-zero on failure. `--help` on each. Logs go under `{data}/logs/`. Scripts
marked *Phase 0 writes* do not exist yet; their contract is fixed here.

| script | reads | writes | when |
|---|---|---|---|
| `100_in_container.sh <cmd…>` | `configs/local.yaml` | — | every EIC command |
| `101_check_environment.sh` | setup pins, manifests | a report line per check | every run start |
| `102_build_eicrecon.sh [--ref SHA] [--label L]` | the submodule (with any patch applied) | `{data}/install/eicrecon-<sha or label>` | Phase 0; code experiments |
| `110_generate_guns.py` | `configs/datasets.yaml` | `{data}/datasets/D{1..4}[h]_*/…edm4hep.root`, the manifest | Phase 0 |
| `111_fetch_dis_inputs.sh` | `configs/datasets.yaml` | `{data}/datasets/D5_*/`, the manifest | Phase 0 |
| `112_msf_sample.sh` | `configs/datasets.yaml` | the D6a manifest entries | Phase 0 |
| `120_reconstruct.py <experiment.yaml> [--datasets …] [--install …]` | an experiment config, the install | `{data}/reco/<experiment>/<dataset>/…edm4eic.root`, timing | references, experiments |
| `121_manifest.py write\|verify` | a folder | `{space}/perf/manifest-*.json` | Phase 0, run start |
| `130_compare_collections.py ref.root new.root [--zdc] [--capybara DIR]` | two edm4eic files, `configs/metrics.yaml` | PASS/FAIL with the first differing leaf | G4 |
| `131_prove_gates.sh [--check]` | an R0 output | the damaged copies, their verdicts | Phase 0, run start |
| `200_cluster_distributions.py` | reco outputs | the G1 to G3 numbers, the column diagnostics, plots | Phase 0, 1, checkpoints |
| `300_run_experiment.py <experiment.yaml> --phase P` | everything above | a scoreboard row, plots, the ledger stub | Phases 2, 3 |
| `400_scoreboard.py <experiment> [--compare REF]` | reco outputs, truth-match outputs, `configs/metrics.yaml` | `scoreboard.csv` row, `metrics-<experiment>.json`, the paired test | every experiment |
| `401_benchmark_plots.sh <experiment> --phase P` | reco outputs, `scripts/700_benchmarks/` | the benchmarks' plots under `{space}/plots/` | Phase 0, checkpoints, Phase 4 |
| `402_lambda_msf_metrics.py <experiment> <dataset>` | D6 reco outputs | S5 (ZDC-only and all-calorimeter) with the acceptance row | Phase 1 (quick), 4 |
| `410_truth_match.py <experiment> [--datasets …]` | reco outputs with the cluster associations | `{space}/perf/truth-<experiment>-<dataset>.json`: per particle purity and energy fraction, S0 per momentum | every experiment (*written in the scaffold, proven in Phase 0*) |
| `420_refit_calibration.py <experiment>` | truth-match outputs on D2, D3 | γ and n `a·E^b` coefficients with errors, residual scale per momentum | after every ACCEPTED clustering (*Phase 1 writes*) |
| `500_farm_array.py <experiment.yaml> --energy …` | `configs/ifarm.yaml` | the array job script and input list | Phase 4 |
| `700_benchmarks/*` | reco outputs in the benchmark layout | the benchmark PDFs | through `401` |
| `700_build_slides.py` | `scoreboard.csv`, plots | the deck | Phase 4 |
