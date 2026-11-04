# ZDC autoresearch loop — version 1

Read `zdc-setup.md` and `work-common.md` first. This file is the loop: the
phases in order, each with its Step 0, its ruler and its done criterion. It
holds no program numbers; every pin, path, dataset size, metric and budget
sits in the setup file, and this file names them by section.

Version 1 is the draft that went to expert review (`docs/expert-review-v1.md`).
The file to run is `zdc-autoresearch-loop-v2.md`.

## What the program produces

1. A reconstruction configuration for the square-tile ZDC that separates the
   two photons of `π⁰ → γγ` and keeps the neutron, measured on a fixed
   scoreboard, with the review findings on PR 3064 explained by mechanism.
2. The validation the reviewers asked for: benchmark plots, capybara
   comparisons and `Λ → nπ⁰` reconstruction on MSF events with enough
   statistics, as a PR draft the user posts.
3. The record: every experiment with its hypothesis, numbers and verdict,
   including the rejected ones.

## Words used in this file

- **reference R0, candidate R1**: the two reconstructions of the setup file
  (section References) that every experiment is measured against.
- **scoreboard, row, band**: the fixed metric set (setup file, Scoreboard),
  one row per reconstruction, and the noise band of each metric.
- **search set, guard, confirmation set**: datasets that select experiments
  (D1 to D5), metrics that must not regress (S3, G1 to G4), and the dataset
  that is never used to select (D6b).
- **parameter experiment, code experiment**: a change expressed as JANA
  `-P` overrides on the pinned build (no rebuild), or a change to the
  ZDC-owned source files (rebuild, patch under `{space}/notes/patches/`).
- **the gate**: G4, non-ZDC collections byte-identical to R0.
- **the switch test**: one pair of runs with a parameter at two values whose
  outputs must differ before any verdict rests on that parameter.

## Files

```
{repo}/
  CLAUDE.md  zdc-setup.md  work-common.md  zdc-autoresearch-loop-v{1,2}.md
  configs/        local.yaml, ifarm.yaml (machine facts); datasets.yaml, metrics.yaml (frozen after Phase 0);
                  experiments/<name>.yaml (one per experiment: eicrecon ref + parameters)
  scripts/        1xx foundation, 2xx understanding, 3xx experiments, 4xx evaluation, 5xx farm, 7xx figures (section The scripts)
  zdc/            the shared Python code the scripts import (config loader, uproot readers, fits)
  submodules/     EICrecon, detector_benchmarks, epic-capybara, meson-structure, skill-eicrecon (frozen except the ZDC-owned files)
  docs/           zdc-problem.md, ifarm-tunnel.md, expert-review-v1.md
  space/          STATUS.md, QUESTIONS.md, LEDGER.md (phases), EXPERIMENTS.md (experiments), FROZEN, notes/, reports/, plots/, perf/
{data}/           build/, install/, datasets/ (frozen inputs), reco/<experiment>/<dataset>/, logs/
```

## Every run

After the start protocol of `work-common.md` (STATUS.md, then QUESTIONS.md):

1. `scripts/101_check_environment.sh` — the image digest, the submodule
   SHAs, the dataset manifest and the reference checksums must reproduce. A
   mismatch follows the "Step 0 reference numbers no longer reproduce" row.
2. If Phase 0 is done: `scripts/131_prove_gates.sh --check` re-runs the gate
   on the stored damaged copies (no reconstruction). A gate that passes a
   damaged copy follows the "want to change the gate" row — the ruler is
   broken.
3. Resume the phase STATUS.md names.

## Phase 0 — the foundation

Everything the loop measures against is built here, proven, and frozen.
Nothing in later phases changes a file this phase freezes. The phase ends
with the scoreboard rows of R0 and R1 on every dataset, the noise band, and
the frozen list in place.

Ruler of this phase: the EICrecon `AGENTS.md` build recipe, the benchmark
generators as they are, and the official campaign files as they are. Phase 0
is the one phase where editing the gate scripts and the metric scripts is
normal work.

### Step 0 items, each with its decisive outcome

| # | item | decisive outcome (write it to the phase report with the evidence) |
|---|---|---|
| 1 | Pull `{image}`, record its digest in the setup file. Inside it: `thisepic.sh` loads; `$DETECTOR_PATH/epic_zdc_sipm_on_tile_only.xml` and `epic_craterlake_18x275.xml` exist; `eicrecon --version`, `npsim --version`, ROOT version printed. | The ZDC-only configuration exists in the image, or Phase 0 stops with a question (the generated configuration may have been dropped from the install). |
| 2 | Build `{eicrecon}` at the pin into `{data}/install/eicrecon-<sha>` with `scripts/102_build_eicrecon.sh`; build the PR head `fdbb773d` into its own prefix. Record build times. | Both installs exist and `eicrecon` from each runs on one event. |
| 3 | Generate the gun datasets D1 to D4 with `scripts/110_generate_guns.py` from `configs/datasets.yaml` (one `npsim` per momentum and seed, the generator macro of the benchmark, fixed seeds, the ZDC-only configuration). Write the sha256 manifest. Replace the placeholder momenta of D2 and D3 with the benchmark Snakefile values first. | Every file in the manifest; event counts match the config; a second run of the generator on one point reproduces the sha256 (fixed seed) or the manifest records that `npsim` output is not bit-reproducible and the event count is the identity instead. |
| 4 | Fetch D5 with `scripts/111_fetch_dis_inputs.sh`: find the newest campaign on XRootD that has the two sample paths, fetch files until `min_events` is reached, write the campaign name into `configs/datasets.yaml` and the files into the manifest. If no campaign has them, simulate from the EVGEN files the EICrecon CI names (fallback in the config). | D5 exists with ≥ the minimum events per sample, or the fallback ran, and the choice is a `D-default` entry. |
| 5 | D6a: list the local MSF files, verify each opens and holds 1000 events (truncated campaign files look normal-sized), confirm the detector configuration the campaign used from `{msf}/simulation-pipeline/configs`, write the manifest. | D6a's file list, event counts and detector configuration are recorded. |
| 6 | **MSF compatibility gate.** Reconstruct one D6a file with R0 in `{image}` and compare it with the campaign's own `reco` file of the same index (`/data/meson-structure-2026-07/reco/9x130`) with capybara and `scripts/130_compare_collections.py` on the ZDC collections. | Either the ZDC rec-hit cellIDs decode and the hit counts agree (the square-tile geometry of 26.06 and 26.11 is the same readout), and D6 stays in the program; or they do not, D6 is dropped, S5 moves to the Λ gun only, and a BLOCKING question asks the user whether to simulate fresh MSF events on the farm. |
| 7 | **Expose the two XY distances as parameters** (`sameLayerDistXYmm`, `diffLayerDistXYmm`, doubles in mm, override the config when set) in `ImagingTopoCluster_factory.h`; rebuild R0's install. | G4 on every dataset: R0 before and after the factory change are byte-identical. Only then does the parameter tier cover PR 3064 (R1 config). The change is also the first entry of `{space}/notes/patches/` and a candidate upstream PR of its own. |
| 8 | Reconstruct R0 and R1 (from the PR commit and from the R1 parameter config) on every dataset with `scripts/120_reconstruct.py`; record wall time per 1000 events (T). | R1-from-parameters and R1-from-commit agree on every ZDC collection (the parameter tier is equivalent to the code); their scoreboard rows are the first two in `scoreboard.csv`; the reference output checksums are in `references.json`. |
| 9 | **Switch tests.** For each parameter in `configs/experiments/R1_pr3064.yaml`, one pair of runs on D1 at 100 GeV with the stock value and the PR value; outputs must differ. Find the parameter table dump (`-Pplugins=dump_flags -Pdump_flags:json=…`) and confirm every name is registered. | Every parameter of the PR demonstrably changes the output; a parameter that does not is a finding (F-entry) and a question before any verdict rests on it. |
| 10 | **Gate proofs.** `scripts/131_prove_gates.sh`: copy an R0 output, damage one non-ZDC leaf (flip one value in a tracking collection) and one ZDC leaf; the gate must FAIL on the first and PASS on the second (ZDC is allowed to change); capybara must report the damaged leaf. Store the damaged copies for the every-run check. | The gate has been seen to fail, and the stored damaged copies reproduce the verdicts. |
| 11 | **Scoreboard and noise band.** `scripts/400_scoreboard.py` on R0 for every dataset; the collection names of `configs/metrics.yaml` verified against the files (correct the file once, record it); R0 again on the second seeds of D1 (100 GeV) and D4 (175 GeV) and once more on the same files; the band per metric written to `noise-band.json`. The Λ mass window (±3σ of the R0 peak) written to `references.json`. | Every scoreboard cell has a value and a band; a cell that cannot be computed is a finding, not a blank. |
| 12 | **Benchmark plots.** `scripts/401_benchmark_plots.sh` runs the four benchmark plot scripts (`zdc_pi0_plots.py`, `lambda_plots.py`, `zdc_photon_plots.py`, `fwd_neutrons_recon.C`) on the R0 and R1 outputs, in the layout the scripts expect. | The plots the reviewers know exist for both references under `{space}/plots/phase0/`. |
| 13 | **Review findings as numbers.** G1 to G3 on D5 for R0 and R1 (`scripts/200_cluster_distributions.py`): the φ histogram, the energy spectrum, the nhits distribution, side by side. | The three findings of the review are reproduced (or not) on the reviewers' own inputs, with numbers. |
| 14 | Freeze: copy `space/FROZEN.after-phase0` to `space/FROZEN` (with the Step 7 exception for the factory file added), fill every *Step 0 fills* value of the setup file, write the Phase 0 report. | The hook refuses a test edit under `submodules/detector_benchmarks` and allows one under `src/detectors/ZDC`. |

### Done criterion

All 14 items have their decisive outcome recorded in
`{space}/reports/phase0_foundation.md`, `scoreboard.csv` holds the R0 and R1
rows, `noise-band.json` and `references.json` exist, `space/FROZEN` is in
place, and the question sweep is written. STATUS.md line 1:
`PHASE0 DONE — report at space/reports/phase0_foundation.md`.

## Phase 1 — dissect PR 3064

Goal: explain each of the three review findings by a mechanism, one
parameter at a time, and seed the experiment backlog from what the
dissection shows.

Step 0: the R0 and R1 rows side by side with their deltas and bands, written
at the top of `{space}/reports/phase1_dissection.md` before any run.

Work, in order:

1. **One parameter at a time.** Eight parameter experiments on D1 to D5:
   R0 plus exactly one of the PR's eight changes. Each is an experiment
   ledger entry with the expected effect written first (what the φ, energy
   and nhits distributions should do, from the clustering algorithm's
   definition). Scoreboard row for each.
2. **Attribute the findings.** For G1 (φ at ±180°), G2 (high-energy
   clusters gone), G3 (low-energy clusters), name the parameter(s) that
   produce each and the mechanism, with the plots. The expected mechanisms
   to test, written as hypotheses in the ledger before running:
   `minClusterNhits` 10 → 2 and `minClusterCenterEdep` 25 → 5 MeV admit
   low-energy fragments (G3); the neighbour distance 36.6 → 14.6 mm splits
   large showers so the energy spectrum loses its high tail (G2); the
   intrinsic φ of a two-subcell cluster is a line and the S2 stagger makes
   that line ±180° (G1 would then be a geometry artifact of small
   clusters, not a bug).
3. **Energy-correction coefficients.** The neutron and photon `a·E^b`
   coefficients were refit on the PR's clusters; check them on D2 and D3:
   scale μ/E per momentum for R0 and R1. A refit against D2/D3 is a
   parameter experiment of this phase.
4. **Seed the backlog**: from the attribution, the ordered hypotheses for
   Phase 2 (at least: each PR parameter alone and the pairwise interactions
   the mechanisms predict; a `minClusterNhits` between 2 and 10; a distance
   between 14.6 and 36.6 mm; the calibration refit).
5. **S5 quick**: R0 and R1 on D6a; Λ candidates per 1000 events and the
   mass peak. A report line, not a verdict.

Done: the report names a mechanism (or "unexplained, size X") for each of
G1 to G3, the backlog holds ≥ 8 ordered entries with expected effects, and
the questions the user must decide before Phase 2 are written (at least:
is a φ collapse that is a geometry artifact acceptable to the reviewers, or
must the cluster shape computation change?).

## Phase 2 — the parameter loop

Goal: the best parameter set of the ZDC chain on the scoreboard, with
mechanisms, without any code change.

Step 0: the Phase 1 backlog, the current best (R0 at first), the band.

### The experiment loop

One entry per experiment in `{space}/EXPERIMENTS.md`, written in two steps:

```markdown
## E<N> <date>: <one-line change>
tier: parameter | code
config: configs/experiments/E<N>_<name>.yaml
hypothesis: <falsifiable, written BEFORE the run: which scoreboard cells move, which direction, by how much, and why (the mechanism)>
expected cost: <minutes; reco wall time from T>
--- after the run ---
row: <the scoreboard.csv row id>
result: <the cells that moved, with deltas and bands>
guards: S3 <in band / out>, S4b <…>, G4 <PASS/FAIL>, G1..G3 <in band / explained: …>
verdict: ACCEPTED | REJECTED | INCONCLUSIVE, one line why
understanding: <what is now believed about the chain>
next: <the next hypothesis, and why>
```

Rules of the loop:

1. **Hypothesis first.** If the expected effect cannot be stated with a
   mechanism, the experiment is not run; it goes to the report as a
   recommended next step.
2. **One change.** One parameter, or one named pair when the mechanism
   predicts an interaction. Unrelated cleanups are separate entries.
3. **Run** `scripts/300_run_experiment.py configs/experiments/E<N>_<name>.yaml`:
   reconstruction on the search set, the gate, the scoreboard row, the
   benchmark plots under `{space}/plots/phase2/E<N>/`.
4. **Gate** G4 fails → REJECTED, no exceptions.
5. **Verdict** by the acceptance rule of the setup file (Scoreboard,
   Acceptance). ACCEPTED → the config becomes the current best; the next
   experiment starts from it. REJECTED on a premise that may not last →
   note what would revive it.
6. **Move-on rule**: two consecutive experiments on one parameter family
   (clustering distances; thresholds; calibration; neutron/photon
   separation) each inside the band or REJECTED → record the family's
   ceiling, move on.
7. **Checkpoints**: after every 5 experiments, the report is updated and the
   question sweep runs; after 10, the run ends for user review (STATUS.md
   says `PHASE2 CHECKPOINT — waiting for user review`), unless the user's
   answer to the checkpoint question was `continue`.
8. **Repeat** an experiment once when its primary delta is within 1.5 bands;
   never more.

Done: the backlog is empty, every family has a recorded ceiling, the
current best has its benchmark plots and its G1 to G3 explanation, and the
report's "Next run recommendations" section names what a code change could
reach that parameters cannot.

## Phase 3 — the algorithm loop

Goal: what parameters cannot reach. Same loop, same ruler, code tier.

Allowed files: the ZDC-owned list (`docs/zdc-problem.md`); the shared
`ImagingTopoCluster` and `HEXPLIT` only after the user answers the Phase 2
question that opens them, with G4 as the guard on every dataset.

Additions to the loop:

- Every code experiment is a patch `{space}/notes/patches/E<N>_<name>.patch`
  against the pin, applied to the submodule for the build and reverted
  after the verdict (or kept when ACCEPTED, as the new base patch). With
  `{git}` on, a commit on the submodule branch instead.
- A rebuild is incremental; a clean rebuild only when the incremental one
  fails. The build log is read with `tail`/`grep` only.
- Candidate ideas, to be written as hypotheses with mechanisms before any
  is run: a two-pass clustering (coarse neighbours for neutrons, fine for
  photons, merged by a shower-shape test); a photon-first split of a
  merged cluster using the EM-like subcell core; a cluster-shape
  computation that gives an intrinsic φ for two-subcell clusters;
  calibration as a function of the cluster shape instead of `a·E^b`.
- The EICrecon review checklist
  (`submodules/skill-eicrecon/.../eicrecon-pr/SKILL.md`) applies to every
  accepted patch before Phase 4.

Done: as Phase 2, plus every accepted patch passes `clang-format` and the
checklist, and the unit tests of EICrecon (`ctest --test-dir build`) pass.

## Phase 4 — confirmation at scale and the deliverable

Goal: validate the accepted configuration where the reviewers asked, and
hand the user a PR draft.

1. **Farm confirmation**: D6b (100 files per energy) reconstructed with R0,
   R1 and the accepted configuration, as one Slurm array per configuration
   (ifarm-slurm skill; `scripts/500_farm_array.py`), S5 computed on the
   farm (`scripts/402_lambda_msf_metrics.py`), small results pulled. The
   statistics budget of the setup file says what the comparison can resolve.
2. **Benchmark plots** for the three configurations on every gun dataset,
   in the benchmarks' own layout, and the capybara reports R0 vs accepted on
   D5 and D6a.
3. **The PR draft** `{space}/reports/pr-draft.md`: motivation, the
   mechanism behind each review finding, the scoreboard before/after with
   bands, the Λ confirmation with its statistics, the parameter table, the
   patches. The user posts it (as a review reply on #3064 or a new PR).
4. **Slides** (`scripts/700_build_slides.py`, the slides skill): the story
   for the ZDC and MSF meetings, numbers loaded from `scoreboard.csv`.

Done: the PR draft and the deck exist, S5 on D6b is in the report with its
error, and the question sweep names what the user must decide before
posting.

## Reporting and checkpoints

- `{space}/reports/phase<N>_*.md` exists from the phase's Step 0 and grows
  at every verdict: the scoreboard rows, the waterfall of accepted changes,
  the rejected hypotheses with why, the G1 to G3 explanations, "Defaults
  you may veto", "Next run recommendations".
- `{space}/perf/scoreboard.csv` is the one table every number comes from;
  the slides and the PR draft load it at build time.
- Plots under `{space}/plots/phase<N>/<experiment>/`, never overwritten;
  `{space}/plots/current/` mirrors the latest best.
- Every 5 experiments: report updated, question sweep. Every 10: the run
  ends for review.

## Rows for the decision table

Checked before the table of `work-common.md`, top to bottom, first match wins:

| you observe | response |
|---|---|
| the ZDC-only detector configuration is missing from the image | **STOP**: question (use the full configuration at 10× the cost, or a different image tag) |
| D6 fails the MSF compatibility gate (Step 0 item 6) | **PARK** D6 with the question; continue with the guns and D5 |
| a PR parameter fails its switch test (Step 0 item 9) | finding + **ASK**; no verdict may rest on that parameter until answered |
| G4 fails on a parameter experiment | the parameter leaks outside the ZDC → **REJECTED** and a finding (a shared factory reads it); never waive |
| S4a improves but G1 to G3 move out of band with no mechanism | **REJECTED** for now; the mechanism search is the next experiment, not a waiver |
| the farm array fails more than 5 % of its tasks | **FIX** by resubmitting the missing deliverables once; still failing → finding + ASK |
| an idea needs a geometry (epic) change | out of scope → **PARK** as a proposal; no work on it |
| the reconstruction wall time doubles | report line; **ASK** whether the cost is acceptable; the experiment's verdict is unaffected |

## The scripts

Every script takes its paths as arguments or from `configs/local.yaml`
(`ZDC_CONFIG` selects another profile), runs with `uv run` (Python) or bash,
prints what it did and the verdict with the offending item, and exits
non-zero on failure. `--help` on each. Logs go under `{data}/logs/`.

| script | reads | writes | when |
|---|---|---|---|
| `100_in_container.sh <cmd…>` | `configs/local.yaml` | — | every EIC command |
| `101_check_environment.sh` | setup pins, manifests | a report line per check | every run start |
| `102_build_eicrecon.sh [--ref SHA]` | the submodule | `{data}/install/eicrecon-<sha>` | Phase 0; code experiments |
| `110_generate_guns.py` | `configs/datasets.yaml` | `{data}/datasets/D{1..4}_*/…edm4hep.root`, the manifest | Phase 0 |
| `111_fetch_dis_inputs.sh` | `configs/datasets.yaml` | `{data}/datasets/D5_*/`, the manifest | Phase 0 |
| `112_msf_sample.sh` | `configs/datasets.yaml` | the D6a manifest entries | Phase 0 |
| `120_reconstruct.py <experiment.yaml> [--datasets …]` | an experiment config, the install | `{data}/reco/<experiment>/<dataset>/…edm4eic.root`, timing | references, experiments |
| `121_manifest.py write|verify` | a folder | `{space}/perf/manifest-*.json` | Phase 0, run start |
| `130_compare_collections.py ref.root new.root` | two edm4eic files, `configs/metrics.yaml` | PASS/FAIL with the first differing leaf; a capybara report | every experiment (G4) |
| `131_prove_gates.sh [--check]` | an R0 output | the damaged copies, their verdicts | Phase 0, run start |
| `200_cluster_distributions.py` | reco outputs on D5 | the G1 to G3 numbers and plots | Phase 0, 1 |
| `300_run_experiment.py <experiment.yaml>` | everything above | a scoreboard row, plots, the ledger stub | Phases 2, 3 |
| `400_scoreboard.py <experiment>` | reco outputs, `configs/metrics.yaml`, the band | `scoreboard.csv` row, `metrics-<experiment>.json` | every experiment |
| `401_benchmark_plots.sh <experiment>` | reco outputs | the benchmarks' plots under `{space}/plots/` | Phase 0, accepted experiments, Phase 4 |
| `402_lambda_msf_metrics.py` | D6 reco outputs | S5 | Phase 1 (quick), 4 |
| `500_farm_array.py <experiment.yaml> --energy …` | `configs/ifarm.yaml` | the array job script and input list | Phase 4 |
| `700_build_slides.py` | `scoreboard.csv`, plots | the deck | Phase 4 |
