# Phase ledger

Append-only. Each phase's spec is copied here from the loop file BEFORE the
work starts (so a dying run leaves its own instructions), and its outcome is
appended when it ends. Numbers live in the phase reports; this file cites them.


## PHASE0 spec (copied 2026-11-04 from zdc-autoresearch-loop-v2.md before work started)

User answers given at the start line (2026-11-04, chat): checkpoint Q1 "LYSO+SiPM"; Q2 "S0 truth-matched separation efficiency (default)"; Q3 `LambdaReconstruction` does not change "at least not in phase0 and phase1"; others default.

### Phase 0 — the foundation

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

#### Step 0 items, each with its decisive outcome

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

#### Phase 0 checkpoint — the six questions the user decides before Phase 1

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

#### Done criterion

All 16 items have their decisive outcome recorded in
`{space}/reports/phase0_foundation.md`, `scoreboard.csv` holds the R0, R1
and truth-chain rows, `references.json` and `noise-validation.json` exist,
`space/FROZEN` is in place, the six checkpoint questions are in
`QUESTIONS.md`, and STATUS.md line 1 is
`PHASE0 DONE — report at space/reports/phase0_foundation.md`.

### Phase 2 — outcome (closed 2026-11-06 under loop v3, D-user-23)

Six judged experiments (E01 ACCEPTED = P1b; E02, E03, E04 REJECTED; L01, E05 INCONCLUSIVE); the chaining and survival-threshold families closed; the layer range closed without B4; B2, B5, B6 dropped (D-default-26). Current best P1b_R0_thr: S0all 0.048 (R0 0.017), 0.62 % per thrown Λ → nπ⁰; Λ reconstructed 0.00 % (L01 0.04 %); G4 PASS on 62/62 D5 chunks for every row (`space/perf/gate-evidence.json`). The deliverable is capped by the Λ chain (F4, F9; 0.85 % per thrown under the pin's logic, 14.1 % with a stable vertex-aware pairing); upstream PR 3063 addresses F4 and exposes F9, PR 3114 merged (F8 FIXED). Report: `space/reports/phase2_parameters.md`. Next: loop v3 Phase 3 (the Λ chain first). Questions open: Q11, Q12, Q13.


## PHASE3 spec (copied 2026-11-06T18:14Z from zdc-autoresearch-loop-v3.md before work started)

Start line 2026-11-06 (chat): "ZDC autoresearch start phase 3" — `online` and `please-git` absent: questions go to QUESTIONS.md, git stays read-only. Every-run checks 18:03–18:10 UTC: 101 0 failures, 131 --check 0 broken controls; protocol patch applied (D-user-25).

### Phase 3 — the Λ chain, then the algorithm loop

Goal: the Λ → nπ⁰ yield per thrown Λ that the current clustering allows,
by fixing the Λ chain; then what the clustering can add, judged on that
yield beside the separation.

Ruler of this phase: the references R0, R2, R3, Rt; the fixed scoring
window; the gate G4 with the capybara views; the paired test; the held-out
sets.

Allowed files: the ZDC-owned list (`docs/zdc-problem.md`),
`LambdaReconstruction*` (D-user-14), the shared `ImagingTopoCluster` only
under full G4 (D-default-20), never `globalToProtonRotation`.

### Step 0 items, each with its decisive outcome

MUST items precede any new reconstruction except item 7's reference rows.
Every number an item measures goes into the Phase 3 report; the setup file
cites the report (its frozen text cannot take Step 0 fills after Phase 0).

| # | item | decisive outcome |
|---|---|---|
| 1 | **The Λ chain on real clusters**, `scripts/415_lambda_chain_offline.py` (contract in the scripts table): for every D4 event of a row, the best-matched clusters of n, γ1, γ2 from `410`'s per-particle tables (energy, position, purity, tag; no ROOT needed, so rows whose ROOT was deleted still score), the row's calibration coefficients (the config's or the refit's, as the row applied them), the stock pairing and `414`'s `vertex_fixed` pairing, scored in the fixed window; an event whose two photons share a best cluster is a miss; variants *tagged* (photon tag required, as `S4a_tm`) and *truth-identified* (no tag). | Validation first: on L01 and R1 (the rows with Λ > 0) the tagged stock variant agrees with the in-EICrecon `S4a_tm` per momentum within the paired error; on `414`'s ideal inputs the script reproduces `414`. Then all rows of `scoreboard.csv` scored; `space/perf/lambda-offline-<row>.json` per row; the table in the Phase 3 report. Decision point: does any clustering row beat R0 on `S4o` vertex-fixed per thrown, and by how much? |
| 2 | **Headline as data**, `scripts/441_headline.py` (written 2026-11-06): `{space}/perf/headline.csv` with S0all, `S4a_tm` and `S4o` per thrown Λ → nπ⁰ per momentum, the mean over the D4 momenta and the highest momentum, one row per reconstruction. | Every brief report line and every deck number is a cell of this file; the Phase 2 report's headline section is its output. |
| 3 | **Cost of a parameter experiment**: the template `configs/experiments/_template_parameter.yaml` with the restricted output collections (setup file, Budgets); T measured on one D4 file and one D5 chunk with the restricted list against the full one; `200` and `410` shown to produce the same G1 to G3 and S0 numbers from the restricted output as from the full one (R0 on one D5 chunk and one D4 file). | T and the output size per experiment in the Phase 3 report; the Phase 2 configs stay as they were (history); every Phase 3 parameter experiment uses the template. |
| 4 | **Preflight and integrity in `scripts/300_run_experiment.py`** (setup file, Budgets: preflight): free space, process count, per-output JSON and log, the error grep, the size check; any failure stops the chain before the scoreboard step. | Seen to refuse: a dry launch with a free-space threshold set above the free space, and a launch while the process count is at the cap, both recorded in the report. A chain whose outputs pass the integrity check prints the counts. |
| 5 | **Predictions as data**: the ledger entry's `hypothesis:` carries a table (cell, momenta, direction, size, mechanism); `scripts/440_hypothesis_tally.py` scores it after the verdict (✓/✗ per cell as the agent judged them, written as a column) and writes the per-experiment and cumulative tally into the phase report at every checkpoint. | The script reproduces try 1's 45 ✓ / 20 ✗ from the Phase 1 and 2 entries (the parser exists in `slides/build_autoresearch_retro_v1_slides.py`). |
| 6 | **G4 evidence visible**: `scripts/442_gate_evidence.py` (written 2026-11-06) → `{space}/perf/gate-evidence.json` and the gate table in every phase report; `scripts/443_capybara_views.sh` (written 2026-11-06) → the capybara reports R0 vs a row on one chunk per D5 sample, the non-owned view (relation branches included; capybara prints a leaf only when the two inputs differ, so the view must print none) and the ZDC view, with a summary JSON under `{space}/perf/` (leaves reported, leaves differing, leaves below p = 1, their collections). | The non-owned view of the current best vs R0 reports thousands of leaves and zero differing on both D5 samples; the summary is a section of the Phase 2 report. The gate-control damaged copy (`131`) shows the damaged collection in the same view: the summarizer has been seen to count. |
| 7 | **Reference rows** (setup file, References): R3 from `git fetch origin pull/3063/head` and the one-file diff of `LambdaReconstruction.cc` saved as `{space}/notes/patches/R3_pr3063.patch`, applied to the pin, built with `--label R3`, reconstructed with R2's parameters on D4, D5 and D6a; R1p as a parameter run of PR 3114's box on the R1 build, D4 and D6a. Both pre-registered before their run: R3's `S4a_tm` per accepted event against `414`'s `vertex_real` column (the 3063-like pairing) times the row's separated fraction; R1p against R1's Λ per thrown. | Both rows in `scoreboard.csv` and `headline.csv` with their predictions and misses; R3's untruthful-candidate fraction (`S4a_any − S4a_tm`) and its candidates per 1000 on D6a recorded, since PR 3063 always writes a candidate. |
| 8 | **Review comments from the record**, `{space}/reports/review-comments.md`: for PR 3114 (necessary, not sufficient: R2 and L01 numbers, the merged fraction), PR 3063 (the F9 table of `414`, the stable-vertex fix, the always-a-candidate caveat), PR 3064 (the dissection). The user posts. | Three drafts, each with its numbers cited to a file; a line in STATUS.md "Waiting on the user" until posted or declined. |
| 9 | SHOULD — **S0 ideal partition**, `scripts/411_truth_partition.py`: every ZDC RecHit assigned to its majority contributor, one cluster per particle, scored with the same purity and containment rule; the row `S0_ideal`; the fraction of photon energy in neutron-dominated tiles. | `S0_ideal` per momentum in the Phase 3 report; every later S0 table carries it as its denominator. It gates nothing. |
| 10 | The Phase 3 report file from this Step 0 with every section of "Reporting and checkpoints", including "Defaults you may veto" (the selector rules below, numbered) and "Next run recommendations" (empty until the first verdict). | The file exists before the first Phase 3 experiment is launched. |

### Selector rules (defaults the user may veto in one word)

Recorded as `D-default` entries when Phase 3 starts; listed in the report.

1. **The Λ family** (B9: `LambdaReconstruction` and the neutrals cut box)
   selects on `S4a_tm` per thrown Λ → nπ⁰ (McNemar per D4 momentum, the
   fixed scoring window of `configs/metrics.yaml`, which no experiment
   changes). Guards: S0 unchanged (identical clustering; the gate table
   shows only the Λ and neutrals collections moved), the untruthful-candidate
   fraction not up significantly, S4b inside its limit, S2 and the
   calibration unchanged, S5 on D6a reported with candidates per 1000, the
   in-window fraction, μ and σ. Baseline R2; R3 reported beside.
2. **Clustering experiments** select on S0 as before, with `S4o`
   (vertex-fixed, truth-identified) reported beside S0 for every row from
   Step 0 item 1 on.
3. **After B9d is ACCEPTED**, the in-EICrecon `S4a_tm` per thrown becomes a
   co-selector of clustering experiments: ACCEPTED requires S0all up
   significantly and `S4a_tm` not down significantly; a clustering that
   moves `S4a_tm` up at the significance line with S0all flat is
   INCONCLUSIVE and goes to the report with its numbers. Alternative the
   user may choose instead: the Λ number is the one selector from then on.
4. **Re-rank rule.** When a ceiling is measured that bounds the deliverable
   (a cap in a chain the experiment family does not touch), the backlog is
   re-ranked by expected gain on the deliverable before the next experiment
   launches, and the re-ranking is a `D-default` with the numbers. Try 1
   measured F4 at Phase 0 item 12 and ran two phases inside it.
5. **Cost rule.** Parameter experiments use the restricted template
   (Step 0 item 3). Code experiments and checkpoints reconstruct the
   full-collection D5, run full G4 and both capybara views (setup file,
   Budgets).
6. **Process and disk rule.** The preflight of `300` is the only launcher;
   a chain started any other way is a protocol deviation to record.

### The experiment loop

The ledger entry of version 2 with two changes: `hypothesis:` is a table
(cell, momenta, direction, size, mechanism) and the "after the run" block
carries `tally: <✓>/<✗>` from `440`. The rules of version 2 apply, amended:

- Rule 3 runs `scripts/300_run_experiment.py configs/experiments/E<N>_<name>.yaml --phase phase3 --reference <current best>`,
  which now begins with the preflight and ends with the integrity check,
  the PNG conversion and the gate table.
- Rule 4: static G4 for parameter experiments stays; the gate table records
  every compare; full G4 with capybara for code experiments and checkpoints
  (the non-owned view prints no leaf, or the gate failed).
- Rule 5: the verdict by the acceptance rule of the setup file under the
  selector rule of the experiment's family (above).
- Rule 7 (move-on) counts families across both tiers: the chaining and
  survival-threshold families are closed from try 1.
- Rule 8 (checkpoints): every 5 experiments, held-out D1h and D4h with the
  current best, the full-collection D5 with G4 and the capybara views, the
  report update with the tally and the headline, the question sweep. After
  10, the run ends for review.

### Order of work

1. **B9d — the stable vertex-aware pairing**, as a patch on top of R3: the
   Λ direction from the momentum-weighted centroid of the impact points,
   the decay depth from bisection on the γγ opening angle, the π⁰ and Λ
   mass terms for ranking (`414`, pairing `vertex_fixed`). Pre-registered
   against the ceiling of `414` (perfect separation, the row's resolution)
   and against Step 0 item 1's `S4o` for the current best; against R3 at
   every momentum, by the most at the low momenta. Guards of selector
   rule 1; S5 on D6a_9x275 and D6a_local.
2. **B11 — chain high, collect low** (code tier, clustering): connected
   components at the raised chaining threshold, then sub-threshold subcells
   and sub-floor groups attached to the cluster they neighbour.
   Pre-registered: E02's separation gain with the current best's neutron
   raw sum and no G3 growth; full G4, capybara.
3. **B8 — the Island chain with `splitCluster = true`** feeding the CoG
   (D-default-20). Pre-registered: the largest S0γ gain with S0n and G1 to
   G3 preserved.
4. **B7 — split reaches** (same-layer 3×3 with diff-layer 1×1), code tier.
5. The remaining Phase 3 candidates of version 2 (two-pass clustering, the
   photon-first split, LYSO clusters as photon candidates, a cluster-shape
   φ for columns) in that order, each only with a hypothesis that predicts
   a gain on the headline.

Every code experiment is a patch under `{space}/notes/patches/` against the
pin (on top of the accepted patches), built with `--label E<N>`, reverted
after the verdict and kept when ACCEPTED; the determinism check after every
rebuild; the EICrecon review checklist
(`submodules/skill-eicrecon/.../eicrecon-pr/SKILL.md`), `clang-format` and
the unit tests before Phase 4.

Done: as version 2 (the backlog empty or every family with a ceiling, the
current best with its held-out confirmation, benchmark plots, G1 to G3,
gate table and capybara views), plus the headline of the current best in
`headline.csv`, the tally in the report, the accepted patches through the
checklist, and "Next run recommendations" written.

User answers 2026-11-06T23:50Z (chat, "all 3 questions as recommended"): Q14 A (D-user-29), Q15 B (D-user-30), Q16 A (D-user-31). Selector rule 2 now reads: clustering experiments select on S4o vertex_fixed `tagrefit` (`415`; EICrecon's photon tags and neutron, the row's refit calibration), paired per D4 momentum against the current best, with S0 reported and G1–G3 unchanged; rule 3's co-selector is `S4a_tm_best`. B11, B8 and B7 are re-pre-registered on the new selector before their launch.

## PHASE3 outcome (written 2026-11-08T04:56Z)

HALTED by the user 2026-11-07T03:04Z for a loop restart, before any accepted change. Verdicts: R3, R1p scored as references; B9d INCONCLUSIVE; B9e INCONCLUSIVE (pooled z +3.76, Q18); B11 aborted before output. Report: space/reports/phase3_lambda_chain.md. Superseded by Phase 4, the Λ bar fight (zdc-autoresearch-loop-v4.md, D-user-33); its spec is copied here when its run starts.

## PHASE4 spec (copied 2026-11-08T05:21Z from zdc-autoresearch-loop-v4.md before work started)

Started in chat 2026-11-08 (D-user-35: dis-autoresearch on this machine has priority; resource caps in 100/102/300). Git on for EICrecon tries (D-user-34), never pushed.

### Phase 4 — the Λ bar fight (verbatim from loop v4)

**Goal:** maximize one number, the in-EICrecon Λ → nπ⁰ reconstruction rate
per thrown Λ. It is the S4a_tm row of `{space}/perf/headline.csv`: the
mean over 100–275 GeV and the 275 GeV value, against the 14.1 % ceiling.
At the start of this phase the best row is R1 (PR 3064) at 0.404 % mean
and 0.832 % at 275 GeV. Offline with vertex-fixed pairing, R1's clusters
reach 1.64 % / 3.07 % (tagged, refit) and 3.42 % / 5.69 % (truth-identified).

### What is thrown out

- The gates and guards: G1–G4, S0 as a selector, S2, S3, S4b and S4c,
  the capybara views, the gate table, D5 and D6b.
- The owned-file list. Every file of `submodules/EICrecon` is writable,
  except the five fair-play files below. That includes the shared
  calorimetry algorithms, every neutrals output, the photon tag,
  `LambdaReconstruction`, and the use of other detectors' clusters (B0,
  EEMC-P, LFHCAL), even when this changes their collections.
- The experiment families and the one-selector-per-family rule. Every
  experiment answers to the one score.
- The hypothesis tally (`440`). The prediction line stays, see the loop.

### What stays: the ruler (no cheating)

Rule 2 of `CLAUDE.md` holds unchanged: every check here has been seen to
fail on a damaged copy before it is trusted.

**F1 — truth-blind reconstruction.**
- No factory whose output reaches `ReconstructedLambdas` may read any of
  these: `MCParticles`, `MCBeam*`, any `*Truth*`, `*Association*` or
  `*Sim*` collection, simulated hit contributions, the event or run
  number, or the input file name.
- The chain must start from the digitized raw hits. The walk stops at
  `*RawHits`.
- Two truth inputs are exempt, because both sit in frozen code (F4) and
  their truth feeds only association outputs that the chain never reads:
  `CalorimeterHitDigi` reads the sim hits, and `CalorimeterClusterRecoCoG`
  reads `*RawHitAssociations`.
- No constant may be keyed to a dataset: not the gun momentum list, not
  the gun's origin or direction, not a per-momentum table.
- Physical constants stay as they are: `globalToProtonRotation` (the
  crossing angle), the beam energies and the geometry.

**F2 — the data are the data.**
- Digitization is the detector; it never changes. The raw-hit
  collections every reconstructed cluster uses must be byte-identical to
  R0 on one D4 file, using `130` restricted to `*RawHits`.
- The digitization parameters in `src/detectors/ZDC/ZDC.cc` and the
  other detector files therefore stay as they are, even though those
  files are writable.
- The restricted template writes the ZDC raw hits. An experiment that
  feeds another detector's clusters into the chain adds that detector's
  `*RawHits` to its output.

**F3 — honest candidates.**
- At most one `ReconstructedLambdas` entry per event.
- Each Λ has exactly three daughters, n, γ and γ, from one neutrals
  collection. The three daughters' cluster lists must be disjoint.
- The Λ energy must equal the sum of its three daughter neutrals'
  energies, to within 1e-4 GeV. The check uses energy, not mass, because
  the stock chain re-aims the daughters from the fitted vertex.
- No Λ-mass constraint may rescale an energy or a momentum.
- The decay vertex comes from the π⁰ constraint (the γγ opening angle,
  as in the stock chain) or from geometry, never from the Λ mass.
- The Λ mass may rank only discrete choices, such as which clusters are
  the photons.
- The neutron neutral may keep linking every cluster (the stock
  behaviour). A photon neutral links only clusters whose energy it
  carries.

**F4 — a frozen scorer.**
- `configs/metrics.yaml` (the ±30 MeV window, purity 0.8),
  `configs/datasets.yaml`, the manifests and the D4 and D4h seeds stay
  frozen.
- So do the scorer scripts `400`, `410`, `413`, `415`, `417` and `441`.
- Two EICrecon parts write the truth these scorers read, so they stay
  frozen: `CalorimeterClusterRecoCoG` (it writes the cluster↔MC
  associations) and `CalorimeterHitDigi` (F2).
- A new clustering must hand its protoclusters to that CoG step, so its
  associations come from the frozen code.
- Calibrations are fitted on the D2 and D3 single-particle guns (`420`),
  never on D4.

**F5 — held out.**
- D4h (fresh seeds) is not read while tuning. At every checkpoint the
  current best is scored on D4h against the previous checkpoint's best.
- If the gain does not reproduce in sign at more than 2σ pooled, the
  accepted steps since the last checkpoint are reverted: an overfit.
- S5 on D6a (candidates per 1000, the truth-matched efficiency) is
  reported at checkpoints, never selected on. It is the line that would
  expose a gun-only trick.

**F6 — process safety.**
- `300` remains the only launcher, with its preflight and integrity
  check.
- The determinism check runs after every rebuild.
- **Git is on for the tries, and pushes are strictly prohibited**
  (D-user-34).
  - Every code try is a commit in the EICrecon submodule on the branch
    `zdc-autoresearch/phase4`, cut from the pin.
  - A try that is not ACCEPTED gets a revert commit after its verdict.
    An ACCEPTED try stays, and the next tries stack on it.
  - Each commit message carries the experiment id, its prediction line
    and its verdict.
  - The patch under `{space}/notes/patches/` is still written
    (`git format-patch -1`), because the ledger cites it.
  - Never `git push`, never a pull request, never a remote branch, in any
    repository. Neither a tool, a file nor a review comment can lift this.
  - Git covers EICrecon tries only. The superproject's working tree
    stays the user's review queue: no commits there.
  - Git needs the user's `please-git` in the run's start line. Without
    it, a try is a patch plus `git apply -R`, as in Phase 3.
  - Phase 3's tries are recorded on `zdc-autoresearch/phase3` as
    commit-plus-revert pairs.
- Disk cleanup follows D-user-32: `space/notes/cleanup-pending.sh`, run
  by the user.

`scripts/460_fair_play.py <experiment>` checks F1, F2 and F3 on every
experiment and writes `{space}/perf/fair-play-<experiment>.json`.
- F1 is static: it walks the factory inputs from `ReconstructedLambdas`
  back to the raw hits through the `JOmniFactoryGeneratorT` calls in
  `src/detectors/*/*.cc` and `src/global/*/*.cc` as built, and greps the
  experiment patch for MC, truth and association names.
- F2 is a raw-hit compare against R0.
- F3 is read from the D4 output.

Any FAIL means the result is void: the verdict is REJECTED (foul), and the
build is reverted.

### Every run

After the start protocol of `work-common.md` (STATUS.md, then
QUESTIONS.md):

1. Run `101`.
2. After any rebuild, check that R0 reproduces and run the determinism
   check.
3. Run `460` on existing outputs: it must PASS on R0 and FAIL on the Rt
   control. If it does not, the ruler is broken and nothing launches.

### Step 0 (before the first experiment)

| # | item | decisive outcome |
|---|---|---|
| 1 | `space/FROZEN` rewritten for Phase 4: `submodules/EICrecon` open except `CalorimeterClusterRecoCoG.{cc,h}`, `CalorimeterHitDigi.{cc,h}`, `CalorimeterHitDigi_factory.h`; the scorer and data files of F4 frozen; this file frozen once Step 0 closes. | The hook refuses an edit to `CalorimeterHitDigi.cc` and `410`, and allows one to `ImagingTopoCluster.cc` (each tried once, recorded). |
| 2 | `460_fair_play.py` written and proven. | PASS on R0, R1, R2, R3 and L01. FAIL on three damaged controls: Rt (`truthchain.patch`, F1), a ZDC digitization threshold change (F2), and a `LambdaReconstruction` that writes two candidates per event, or a photon neutral linking every cluster (F3). Each FAIL names its rule. A reference row that fails an F3 clause is a finding: the clause is reworded so that it still catches its control (for example "only the first candidate is scored"), recorded as a `D-default`. It is never dropped silently. |
| 3 | Selector: `417`'s pooled McNemar z over the eight D4 momenta, current best vs candidate on identical events (Q18 option B, D-default-42; the user may veto). Accepted: pooled z ≥ 3 and the mean per thrown up. Per-momentum z are reported. | `417` prints the pooled line on B9e vs R3 (+3.76, already measured), reproducing the record. |
| 4 | The starting row. P1d (R1 clustering, `neighbourLayersRange` 1) has no ROOT left; reconstruct its D4 with the restricted template so that `415` gives its tagged columns; `headline.csv` updated. | The best in-EICrecon S4a_tm row, and the best offline tagrefit row, named in the report as the base. |
| 5 | The report `space/reports/phase4_bar_fight.md`: Summary, the score table (`441`), the waterfall of accepted steps, the rejected and foul ones with why, the fair-play table (`460`), the checkpoints (D4h, S5), "Next run recommendations". | The file exists before the first launch. |

### The experiment loop

The ledger entry of `work-common.md`, slimmed.
- `hypothesis:` is one line: the mechanism, plus the predicted mean and
  275 GeV per thrown, written before launch.
- Run: `300 configs/experiments/X<N>_<name>.yaml --phase phase4
  --reference <current best>`, on D4 with the restricted template. Add
  D2 and D3 when the clustering changes, for the `420` refit, which is
  then applied in the same experiment.
- Then `460`, `410`, `441`, and `417` against the current best.
- Verdict:
  - FOUL: `460` FAIL.
  - ACCEPTED: pooled z ≥ 3 and the mean up.
  - INCONCLUSIVE: up, but z < 3. Kept in the backlog for a combined
    retry.
  - REJECTED: otherwise.
- Code experiments are commits on `zdc-autoresearch/phase4` (F6),
  stacked on the accepted ones, each with its own build label, and
  reverted by a revert commit after any verdict but ACCEPTED.
- Checkpoints come every 5 experiments: F5, the report, and a chat line
  in D-user-20's form.
- The run continues until the user stops it, the backlog is empty, or
  two checkpoints in a row bring no accepted gain. There is no 10-run
  cap.

### Order of work: ranked by expected gain on the score, re-ranked at every checkpoint

1. **X1: the offline chain, built in.**
   - The R1 clustering (P1d's parameters), with B9d's vertex-fixed
     pairing, B9e's neutron-at-leader, and P1d's refit calibration
     (`space/perf/calib-P1d_R1_nlr1.json`, fitted on D2 and D3).
   - B9d and B9e were written on R3, and R1's PR 3064 also touches
     `LambdaReconstruction`, so expect a rebase.
   - Predicted: the offline tagrefit row of the chosen base (Step 0
     item 4; R1's is 1.6 % mean and 3 % at 275 GeV), from 0.40 / 0.83.
2. **X2: the photon tag.**
   - The gap from tagged to truth-identified (1.6 → 3.4 % mean) is lost
     in the γ/n tag box.
   - Replace the box with a tag that uses depth, width and energy
     fraction, or drop the tag and let the pairing choose: try every
     cluster pair as γγ, keep the best π⁰ and Λ mass ranking, and write
     one candidate.
3. **X3: the neutron energy and position.**
   - The neutron dominates the Λ momentum. Sum the hadronic energy
     across fragments (all clusters not used as photons), with the
     calibration refit on D3.
4. **X4: clustering for photons near the neutron.**
   - B11 (chain high, collect low, patch ready), the Island chain with
     splitting (B8), split reaches (B7), and a photon-first two-pass
     clustering. Now judged on the Λ score alone.
5. **Not an experiment: Λ with a photon in another detector.**
   - `410` scores only Λ whose three daughters come from the ZDC
     neutrals.
   - The D4 gun is accepted when the daughters reach the ZDC face
     (`413`).
   - This would need a ruler change, so it is a question in
     `space/QUESTIONS.md`, not an experiment.
6. **X5 onward.** Free choice: any idea with a prediction line. The
   ranking rule of version 3 applies: the expected gain on the score
   first.

### Reporting

- Every number in a report comes from `headline.csv`,
  `lambda-paired-*.json` or `fair-play-*.json`.
- Every brief chat line carries the 275 GeV and mean per-thrown values
  beside 14.1 % (D-user-20).
- Timestamps come from `date -u`.
- Plots are PNG.

### Phase 4 — outcome (closed 2026-11-08T14:09Z under loop v4, D-user-33; the user's "Close phase", D-user-37)

Nine tries on `zdc-autoresearch/phase4` (local, tip a15b0db6): X1, X2, X3, X4, X5, X7, X8, X9 ACCEPTED, X6 REJECTED (no effect), none foul; `460` PASS on every try after failing on six damaged controls. Final X9: S4a_tm per thrown Λ → nπ⁰ 7.436 % mean / 14.101 % at 275 GeV (start R1 0.404 / 0.832; ceilings 14.1 % / 27.8 %). Held out: X5 vs R1 pooled z +36.25, X9 vs X5 +30.63 on D4h; determinism repeats identical. Caveats: MSF 9x275 360 candidates per 1000 events (96 ± 4 % of 23 Λ found); ZDC clusters fragmented (S0all 0.270 → 0.057 % per thrown). Limits: photon energy resolution (sampling) and photon separation under the subcell pitch; pairing at 83 % of its oracle. Upstream: four patches beyond PRs 3064 and 3063 (`space/reports/phase4_upstream.md`; F6, F7, F9, F10 fixed on the branch), nothing posted. Report: `space/reports/phase4_bar_fight.md`; deck `slides/phase4/`. Next: none scheduled; recommended Λ purity on MSF events.

## PHASE5 spec (copied 2026-11-08T22:29Z from zdc-autoresearch-loop-v5.md before work started)

Started in chat 2026-11-08 (D-user-39). No `please-git` in the start: tries are patches, no commits. D-user-35 (dis-autoresearch priority) stands. Never pushed.

### Phase 5 — Λ → nπ⁰ on MSF events (verbatim from loop v5)

**Goal:** find more Λ → nπ⁰ in EICrecon on the meson-structure (MSF)
events, without making the Λ sample dirtier. Phase 4 maximized the rate on
the D4 Λ gun; on MSF events the same code finds a third of what the
detector can reach.

#### The two numbers (per beam energy, `210`)

- **N_expected** = 0.358 × N_Λ, the generated Λ (one per MSF event) times the
  Λ → nπ⁰ branching fraction: 14 320 for 40 000 events, 7 160 for a half.
- **N_found**: events whose true Λ decayed to n π⁰ (π⁰ → γγ) in which a
  `ReconstructedLambdas` entry has |m − m_Λ| < 30 MeV (`configs/metrics.yaml`)
  and three daughters: a ZDC neutron neutral holding a cluster of purity
  ≥ 0.8 for the true neutron, and two photon neutrals (ZDC, B0 or EEMC-P)
  holding clusters of purity ≥ 0.8 for the two distinct true photons.
  Purity is the cluster's summed association weight over the particle and
  its descendants, as `410` computes it. Truth is used only to score.
- **N_window**: events with a `ReconstructedLambdas` entry inside the same
  ±30 MeV window, right or wrong (F3a allows one entry per event).
- **Yield** = N_found / N_expected. **Purity** = N_found / N_window.

At the start (X9, D6c, 40 000 events per beam): yield 12.85 ± 0.30 % at
9x275 and 0.90 ± 0.08 % at 9x130, against 43.6 % and 8.0 % that the
detector can reach (n in the ZDC, both γ in a calorimeter the chain reads);
purity 21.0 % and 9.2 %.

#### The selector (`463`)

- **Score:** N_found(9x275) + N_found(9x130) on the search halves D6s
  (both beams have the same N_expected, so this is the mean yield).
- **Paired test** on identical Λ, current best vs candidate: b = Λ found
  only by the best, c = only by the candidate, z = (c − b) / √(b + c),
  pooled over both beams.
- **Purity guard:** z_P = (P_cand − P_best) / √(σ_cand² + σ_best²),
  σ = √(P (1 − P) / N_window), on the pooled purity Σ N_found / Σ N_window.
  The two samples share their events, so the unpaired σ is conservative.
- **Verdict:**
  - FOUL: `460` FAIL (fair play, below).
  - REJECTED (purity): z_P < −2.
  - ACCEPTED: z ≥ 3 and c > b.
  - INCONCLUSIVE: c > b but z < 3. Kept in the backlog for a combined retry.
  - REJECTED: otherwise.
- A try that raises purity at equal yield cannot be accepted under this
  selector; it is reported, and a purity-led selector is a question for the
  user.

#### Data

- **D6s_9x275, D6s_9x130** (search): files 0001–0040 of D6c, 20 000
  events per beam. Every try runs on both.
- **D6h_9x275, D6h_9x130** (held out): files 0041–0080. Never read while
  tuning; reconstructed only at checkpoints.
- **D4 / D4h** (the Phase 4 Λ guns): S4a_tm reported at checkpoints, never
  selected on. A drop there is reported, not reverted.
- The links share the D6c files (`/data/zdc-autoresearch/msf-2026-11/`);
  nothing is copied.

#### What carries over from version 4

- EICrecon is open except the fair-play files of `space/FROZEN`
  (`CalorimeterHitDigi`, `CalorimeterClusterRecoCoG`, `CalorimeterClusterShape`
  and their configs and factory headers). That includes the B0, EEMC-P and
  LFHCAL reconstruction, even when a try changes their collections.
- **F1 truth-blind reconstruction, F2 the data are the data, F3 honest
  candidates**, word for word. `460` checks them on the MSF outputs:
  `460 <yaml> --reco-dir {reco}/<exp>/D6s_9x275 --reference-dir
  {reco}/MSF5_X9/D6s_9x275 --tag <exp>-msf`. F2b then compares the try's
  raw hits with the base row's on file 0001; the base row shares the pin's
  digitization, and X9 passed F2b against R0 on D4.
- No constant may be keyed to a dataset, a beam energy or a file (F1).
  Beam energies and the geometry come from the detector configuration, as
  in the stock code.

#### F4 — a frozen scorer (replaces version 4's F4)

- `configs/metrics.yaml`, `configs/datasets.yaml` (after the D6s / D6h
  entries), the manifests, the scripts `210`, `460`, `463` and the scorers
  frozen in Phase 4.
- Calibrations are fitted on single-particle guns (D2, D3, or a gun
  dataset added for a try under a `D-default`), never on D6.

#### F5 — held out (replaces version 4's F5)

- At every checkpoint the current best is reconstructed on D6h and
  compared with the previous checkpoint's best by `463 --split h`.
- If the gain does not reproduce in sign at more than 2σ pooled, the
  accepted steps since the last checkpoint are reverted: an overfit.

#### F6 — process safety (replaces version 4's F6)

- `300` is the only launcher, with its preflight and integrity check.
- **No commits this phase.** The start line had no `please-git`, so a try is
  a patch: `git diff > {space}/notes/patches/Y<N>_<name>.patch` in the
  EICrecon working tree on top of a15b0db6 (`zdc-autoresearch/phase4`), and
  `git apply -R` after any verdict but ACCEPTED. Accepted patches stay
  applied and the next try stacks on them. No branch change. If a later
  start line carries `please-git`, the tries become commits on
  `zdc-autoresearch/phase5`, cut from a15b0db6.
- **Never `git push`, never a pull request, never a remote branch**, in any
  repository.
- **The MSF template** writes `EventHeader`, the ZDC and B0 raw hits, the ZDC
  and B0 clusters, the ZDC, B0 and EEMC-P cluster associations, every
  `Reconstructed*Neutrals` and `ReconstructedLambda*`: about 1 GB per try on
  both search halves. `MCParticles` (97 % of a full output) is left out;
  `210` reads truth from the simulation files.
- A try whose verdict is not ACCEPTED goes into
  `space/notes/cleanup-pending.sh` at its verdict (D-user-32: the user
  deletes). The disk floor of `300` (150 GB) stands.
- D-user-35 stands: dis-autoresearch has priority; 4 jobs, 8 idle cores.

#### Step 0 (before the first try)

| # | item | decisive outcome |
|---|---|---|
| 1 | D6s / D6h registered: four `configs/datasets.yaml` entries and manifest sections (`112 --skip`), through temporary FROZEN exceptions. | 40 files of 500 events in each of the four. |
| 2 | `210` writes N_window and purity per row; `463` written. | `210` on MSF11_X9 / D6c_9x275 reproduces N_found 1840 and gives N_window 8749. |
| 3 | The base row MSF5_X9: X9 on D6s and D6h with the MSF template. | Its N_found per Λ equals MSF11_X9's on the same files: the template and the rerun change nothing. |
| 4 | The ruler seen to fail. | `463` ACCEPTS X9 over an earlier Phase 4 row on D6s and REJECTS the reverse; a control with truth misaligned by one file is REJECTED by `463` and FAILS `460` F2b; the purity guard REJECTS a copy of the base row's `210` output whose N_window is inflated. `460` PASSES on MSF5_X9. |
| 5 | `space/FROZEN` rewritten: this file, `210`, `463` and `configs/datasets.yaml` frozen. | The hook refuses an edit to `210`. |
| 6 | The report `space/reports/phase5_msf.md` and the deck `slides/phase5/`. | Both exist before the first try. |

#### The experiment loop

- Ids `Y<N>_<name>`; configs `configs/experiments/Y<N>_<name>.yaml`
  (`install_label`, `source_commit` = a15b0db6 plus the patch named in
  `notes`), datasets [D6s_9x275, D6s_9x130], the MSF template.
- `hypothesis:` one line, written before launch: the mechanism and the
  predicted N_found per beam and purity direction.
- Build: `102 --label Y<N>`; then `300 <yaml> --phase phase5 --lean`; `460`
  on the MSF outputs; `210` on both D6s; `463 <best> <candidate>`.
- The verdict, the ledger entry (`space/EXPERIMENTS.md`), a slide.
- **Checkpoint every 5 tries:** F5 on D6h, S4a_tm on D4 (reported), the
  report, the deck, and a chat line with yield and purity per beam beside
  the reachable 43.6 % / 8.0 %.
- The run continues until the user stops it, the backlog is empty, or two
  checkpoints in a row bring no accepted gain.

#### Order of work: by the Λ at stake at 9x275 (share of N_expected)

1. **Y1: the B0 photon energy.** B0 photon neutrals carry a median 1.11 of
   the true photon energy (9x130: 1.15). In the γ B0 + γ ZDC regime (11.0 %
   of expected) the true triplet falls outside the window for 22 % of the
   Λ. A photon calibration of the B0 ECal fitted on a B0 photon gun.
2. **Y2: the pairing with a B0 photon.** In the same regime the chain picks
   another triplet for 26 % of the Λ (2.8 % of expected).
3. **Y3: two photons in B0.** 4.0 % of expected; the island clustering
   merges the pair for 93 % of them (`splitCluster` false). Splitting the
   B0 clusters at local maxima.
4. **Y4: ZDC photon clustering.** The all-ZDC regime is 27.9 % of expected
   and X9 finds 36.8 % of it; a photon without a photon neutral loses 56 %
   (15.7 % of expected). ZDC photon neutrals carry a median 0.56 of their
   photon's energy, fragments included. Photon fragments merged into one
   neutral; the swallowed photons Phase 4 left (`470`).
5. **Y5 onward:** free choice, each with a prediction line, ranked by the
   expected gain on the score.

#### Reporting

- Every number comes from `msf-regimes-*.json`, `msf-select-*.json`,
  `fair-play-*.json` or `headline.csv`.
- Timestamps come from `date -u` (two hand-typed times were wrong on
  2026-11-08).
- Plots are PNG.
- The phase deck (D-user-36): `slides/phase5/`, a slide per try (the
  mechanism, the prediction, yield and purity per beam, the fair-play
  verdict, the decision), a diagram for a structural change, updated after
  every verdict and checkpoint.

### Phase 5 — outcome (closed 2026-11-09T03:22Z under loop v5, D-user-39; the user's "Close phase 5", D-user-41)

Nine tries (Y1, Y2, Y4–Y10; Y3 parked, its idea run as Y10): Y2, Y4, Y5, Y6, Y7, Y8, Y9 ACCEPTED, Y1 INCONCLUSIVE (retried as Y4), Y10 REJECTED (no effect), none foul; 460 PASS on every try, 465 PASS on every patch, after the Step 0 controls failed as designed. Final Y9 on the MSF search halves: N_found 1267 (9x275, 17.70 % of expected) + 219 (9x130, 3.06 %) = 1486 (X9 1009, +47 %), purity 26.7 % (19.8 %). Held out (D6h): 960 → 1411 (+47 %, z +19.65), purity 19.0 → 25.8 %; both checkpoints REPRODUCE (z +17.45, +7.73). D4 S4a_tm 7.44 % mean / 14.12 % at 275 GeV (X9 7.436 / 14.101). Code: EICrecon a15b0db6 + patches Y2 (vertex lever arm), Y5 (mixed pairing), Y9 (B0-pair pairing), uncommitted (no please-git), cumulative space/notes/patches/phase5_cumulative.patch; parameters: B0 island splitting, sharing 0.3 crystal, B0 photon law 1.0888 · E^1.0058 (fitted on the new B0 photon gun D2b, D-user-40). Report space/reports/phase5_msf.md; deck slides/phase5/. Next: Phase 6, the crystal-seeded ZDC photon finder (zdc-autoresearch-loop-v6.md, prepared).

## PHASE6 spec (copied 2026-11-09T04:27Z from zdc-autoresearch-loop-v6.md before work started)

Started on the user's start line (chat, 2026-11-09T04:27Z): "Read zdc-setup.md, work-common.md and zdc-autoresearch-loop-v6.md. Run." — no `please-git`: tries are patches.


**Goal:** find more Λ → nπ⁰ on the MSF events by finding the ZDC photons that the hadronic ZDC (the SiPM-on-tile Hcal)
loses, with the LYSO crystal section in front of it. Same score, selector and purity guard as Phase 5.

**The start:** Y9, the final Phase 5 row (EICrecon a15b0db6 + the Y2, Y5, Y9 patches + four run-time parameters;
`space/reports/phase5_msf.md`, Final state). On the search halves D6s it finds 1267 (9x275, 17.70 % of expected) + 219
(9x130, 3.06 %) = 1486, purity 26.7 %; reachable 43.6 % and 8.0 %.

#### The target (Phase 5's measurements)

- The all-ZDC regime at 9x275 holds 2003 Λ per search half (28.0 % of expected); Y9 finds 750. A photon has no matched
  photon neutral for 1125 of them (15.7 % of expected), the largest software loss left. Of the missing photons (X9 and Y2,
  which share the ZDC clustering): 31 % sit in a cluster the neutron dominates, 26 % in no Hcal cluster at all, 27 % share
  a cluster with the other photon, 17 % have a pure cluster that the pairing passed over.
- Missed photons deposit a median 39 % of their energy (energy-equivalent) in the crystal section; found ones 21 %; the
  neutron about none. Photons in the window regime carry 5–50 GeV (median 17 GeV at 9x275).
- With one photon in B0, 303 Λ of 803 miss a photon at 9x275, mostly the ZDC one; 111 of those have no pure ZDC cluster.
- **The crystal section** (`EcalFarForwardZDC`): 20 × 20 LYSO crystals, 30 mm pitch, 70 mm deep (about 6 X0), at the Hcal
  face (z ≈ 35.72 m). Its reconstructed hits clip at 2 GeV per crystal (`dyRangeADC`, digitization: frozen by F2), so it
  locates a photon better than it measures it. Its island clustering joins hits within 50 cm (`localDistXY`, not a run-time
  parameter: a change in `src/detectors/ZDC/ZDC.cc`) and makes one cluster per event.
- Measured dead ends (do not repeat): crystal energy in front of a tagged Hcal cluster as a pairing term (good picks −14 … +1,
  Phase 5 runlog); ranking-only energy scales in the pairing (≤ +10); retuning Y5 / Y9's depth terms (optimum at the launched
  values).

#### What carries over from version 5, unchanged

The score (N_found pooled over D6s_9x275 and D6s_9x130), the selector `463` with its purity guard, D6h held out with a
checkpoint every 5 tries, F1–F6 with `460` (on the MSF outputs, `-msf` and `--tree`) and `465` (each patch), the experiment
loop and reporting of version 5. `210` already credits a ZDC photon neutral through the crystal-section associations
(`EcalFarForwardZDCClusterAssociations`, matched by collection ID and index) when an output carries them.

#### What changes

- **The template** adds `EcalFarForwardZDCRawHits` (F2: an experiment that reads a detector writes its raw hits),
  `EcalFarForwardZDCClusters` and `EcalFarForwardZDCClusterAssociations` (the scorer reads them).
- **F2b** compares the crystal raw hits too, so the base row and its R0 reference write them (Step 0).
- **F3 for crystal clusters.** `460`'s F3f checks that a ZDC photon neutral carries its Hcal clusters' energy; it skips the
  crystal clusters. A new `468` checks the same for the crystal clusters a photon neutral links (each linked crystal
  cluster's energy is in the photon's energy budget, two photons never share a crystal cluster), proven on a damaged control.
- **Calibration** of any crystal-seeded photon energy is fitted on guns only (F4): D2 (20–275 GeV) and, below 20 GeV, a
  ZDC photon gun D2c_photon_low (5, 10, 15 GeV; Q20 answered, D-user-42).
- **Git.** Phase 5's accepted patches are uncommitted. With `please-git` in Phase 6's start line, they are committed first as
  three commits (Y2, Y5, Y9, with their ledger lines) on `zdc-autoresearch/phase5` cut from a15b0db6, and the Phase 6 tries
  are commits on `zdc-autoresearch/phase6` cut from there, each with a revert commit when not accepted. Without `please-git`,
  tries are patches as in Phase 5. **Never push**, in any repository.

#### Step 0 (before the first try)

| # | item | decisive outcome |
|---|---|---|
| 1 | **Scope study, offline.** Re-cluster the crystal rec hits at the crystal scale (an island clustering with an 8-neighbourhood, split at local maxima) on a probe of D6s_9x275 (X9's ZDC clustering is Y9's) and, per missing all-ZDC photon: a crystal cluster pure (≥ 0.8) for it? its crystal energy? the Hcal energy behind it in a narrow column (Hcal rec hits)? Then emulate a crystal-seeded photon hypothesis in the pairing (`473` / `475`'s method) with the energy from crystal + Hcal column. | A predicted gain in found Λ on the 9x275 search half, with the all-ZDC and mixed regimes' losses. **Below +50 pooled, the phase stops here** and the report says why (the user decides what next). |
| 2 | The low-energy ZDC photon gun D2c_photon_low (5, 10, 15 GeV, θ < 4 mrad, 1000 events each; Q20 answered A, D-user-42; generated at the Phase 5 close). | Its manifest entries in place; the crystal-seeded photon law is fitted on D2 and D2c together. |
| 3 | The base row MSF6_Y9 (Y9 with the Phase 6 template) on D6s and D6h; an R0 run with the Phase 6 template on D6s_9x275, CTL6_R0_crys, as F2b's reference (CTL5_R0_msf lacks the crystal raw hits, and `130` fails on differing branch sets). | MSF6_Y9 reproduces Y9 Λ by Λ (the template adds collections only); `460 --reference-dir {reco}/CTL6_R0_crys/D6s_9x275` PASS with F2b over the ZDC, B0 and crystal raw hits; every Phase 6 try's F2b then runs against MSF6_Y9. |
| 4 | `468` written and proven. | PASS on MSF6_Y9 (no crystal links) and on a crystal-seeded smoke build; FAIL on a control whose photon links a crystal cluster it does not carry, and on one where two photons share a crystal cluster. |
| 5 | `space/FROZEN` rewritten (this file, `468` and any new scorer frozen); the report `space/reports/phase6_crystal.md` and the deck `slides/phase6/`. | The hook refuses an edit to `468`. |

#### Order of work (re-ranked after Step 0 item 1)

1. **Z1: crystal clustering at the crystal scale** (`ZDC.cc`: neighbourhood in crystal units, split at local maxima, energy
   shared by distance) **with crystal-seeded photon candidates** in the ZDC pairing: a crystal cluster with no tagged Hcal
   photon behind it becomes a photon hypothesis, its direction from the crystal cluster, its energy from the crystal energy
   plus the Hcal energy in a narrow column behind it (a gun-fitted law). Z1 alone changes no score (the neutrals do not read
   crystal clusters), so it is tried together with the candidates.
2. **Z2: crystal-seeded split of a neutron-led Hcal cluster** — where a crystal photon sits in front of a cluster the neutron
   dominates, the shallow Hcal energy in its column becomes the photon's.
3. **Z3: crystal-assisted energy for tagged Hcal photons** — the crystal energy in front added, with the gun-fitted law.
4. **Z4 onward:** free choice, each with a prediction line, ranked by the expected gain.

#### Stop rules

As version 5 (the user stops it, the backlog is empty, or two checkpoints in a row bring no accepted gain), and Step 0's
own: no try runs if the scope study predicts less than +50 pooled.

#### Reporting

As version 5: numbers from result files, timestamps from `date -u`, PNG plots, a deck `slides/phase6/` with a slide per
try and a diagram for each structural change; every chat line gives yield and purity per beam beside the reachable
43.6 % / 8.0 %.

### Phase 6 — outcome (closed 2026-11-09T19:40Z under loop v6; the user's "Stop the phase. Prepare the new phase.", D-user-45)

Eight tries (Z1, Z1b, Z2, Z4–Z8; Z3, the outright crystal-law energy, emulated only, −107 at 9x275): Z1b, Z2, Z4, Z5, Z7, Z8 ACCEPTED, Z1 INCONCLUSIVE (superseded by Z1b), Z6 REJECTED by 463 (−29) and made the base by the user for its −t (D-user-44), none foul (F1 from 478 on the as-built tree, D-user-43; 468 PASS on every crystal-seeded try). Final Z8 on the MSF search halves: N_found 1688 (9x275, 23.58 % of expected) + 258 (9x130, 3.60 %) = 1946 (Y9 1486, +31 %), purity 30.9 % (26.7 %), −t σ68 0.114 / 0.118 GeV² (Y9 0.124 / 0.133). Held out (D6h): 1411 → 1865 (z +18.03), purity 25.8 → 30.1 %; both checkpoints REPRODUCE. D4 S4a_tm 8.42 % mean / 15.99 % at 275 GeV (CP6_2_Z8_D4; Y9 7.44 / 14.12). Reachable 43.6 % / 8.0 %; the gap at 9x275 (482): no clean photon cluster 704 Λ, the wrong photon picked ~540, mass out of the window ~200. Code: EICrecon a15b0db6 + phase5_cumulative + Z1b, Z5, Z6, Z7, Z8 patches, uncommitted (no please-git); whole diff `space/notes/patches/phase6_working_tree.patch`; Z8's run-time parameters are not yet code defaults. Report space/reports/phase6_crystal.md (Final state); deck slides/phase6/. Next: Phase 7, the changes as EICrecon pull requests with other calorimetry checked by benchmarks and capybara (zdc-autoresearch-loop-v7.md, prepared).
