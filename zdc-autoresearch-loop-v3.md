# ZDC autoresearch loop — version 3

Read `zdc-setup.md` and `work-common.md` first. This file is the loop: the
phases in order, each with its Step 0, its ruler and its done criterion. It
holds no program numbers; every pin, path, dataset size, metric, limit and
budget sits in the setup file, and this file names them by section.

Version 3 applies try 1 of version 2 (run 2026-11-04/05): the run agent's
self-review `try1-expert.md`, the designer's review of it
`try1-assessment.md`, and the three upstream PRs by the author of issue
#2737 (`try1-assessment.md`, section 5). Phases 0 and 1 are complete under
version 2 and their Step 0 tables stay there; version 3 governs from the
Phase 2 close-out on. What changed, in one paragraph: the parameter space
of the clustering was exhausted in try 1 while the deliverable (Λ → nπ⁰ per
thrown Λ) stayed at zero, capped by the Λ chain the clustering does not
own; the cap is measured and a stable vertex-aware pairing lifts it by an
order of magnitude. Try 2 therefore starts in the Λ chain, judged on the
Λ yield, with the clustering experiments tied to that yield by an offline
chain on real clusters. The cost per experiment drops by restricting output
collections; preflight and integrity checks become part of the launcher;
predictions and headline numbers become script output; plots are PNG; the
G4 evidence (nothing outside the ZDC moved) is published per experiment.

## What the program produces

Unchanged from version 2, with one addition to item 2: the validation now
includes the per-experiment gate table and the capybara views R0 vs the
current best (setup file, Budgets: checkpoint), so a reader sees that no
collection outside the owned list moved, without opening a log.

## Words used in this file

As in version 2, plus:

- **baseline R2**: R0 + PR 3114 (merged upstream 2026-11-05); every Λ
  comparison is against R2 from 2026-11-06 (setup file, References). S0 is
  identical between R0 and R2, so the clustering comparisons keep R0.
- **R3**: R2 + PR 3063 (the Λ chain upstream proposes); **R1p**: the
  author's package R1 + PR 3114 (setup file, References).
- **S4o**: the Λ chain run offline on a row's real clusters (setup file,
  Scoreboard): the number that ties a clustering row to a Λ yield.
- **headline**: the side table of per-thrown numbers every report line
  comes from (setup file, Scoreboard, row H).
- **gate table**: the per-experiment record of the G4 compares (files,
  leaves, events, PASS count), `scripts/442_gate_evidence.py`.
- **protocol patch**: a revision of the frozen protocol files between
  runs, written as a patch under `{space}/notes/patches/` and applied by
  the user (`work-common.md`, Git; setup file, Frozen after Phase 0).

## Every run

After the start protocol of `work-common.md` (STATUS.md, then QUESTIONS.md):

1. `scripts/101_check_environment.sh`, `scripts/131_prove_gates.sh --check`
   and the determinism check after a rebuild, as in version 2.
2. The protocol patch `{space}/notes/patches/protocol-v3.patch`: if
   `zdc-setup.md` does not yet contain the `{pr3063}` row, the patch is not
   applied. Its values govern this run regardless (D-user-23); Q13 stays
   open and the run proceeds.
3. Resume the phase STATUS.md names.

## Phases 0 and 1 — done under version 2

Their Step 0 tables, checkpoint questions and done criteria are in
`zdc-autoresearch-loop-v2.md`; their reports are
`{space}/reports/phase0_foundation.md` and `phase1_dissection.md`. Nothing
in them is reopened by version 3.

## Phase 2 — close-out

Try 1 ran six judged experiments under version 2 and stopped on the user's
instruction (D-user-21). Version 3 closes the phase without further runs:

1. The report `{space}/reports/phase2_parameters.md` with the sections of
   "Reporting and checkpoints" below: the waterfall R0 → current best, the
   rejected hypotheses with their deltas, the family ceilings (chaining
   threshold, survival thresholds), the G1 to G3 numbers of the current
   best, the gate table, the hypothesis tally, the headline, "Defaults you
   may veto", "Next run recommendations".
2. The remaining parts of the 5-experiment checkpoint: the held-out check
   (done in try 1, E01) and the question sweep (Q11, Q12, Q13 in
   `QUESTIONS.md`).
3. The backlog: B4 (`neighbourLayersRange` 2) is dropped: P1a measured 3 as
   a loss with nothing gained and P1d measured 1 as best on columns, so one
   run at 2 cannot change the current best. B2 is dropped (inert at the
   current best's seed, switch test), B5 (second order) and B6 (no mechanism
   inside one module) too. B11 moves to Phase 3 after B8.
4. Plots under `{space}/plots/` converted to PNG (setup file, Review
   delivery, Plot format).

Done: the report exists with every section, STATUS.md line 1 is
`PHASE2 DONE — report at space/reports/phase2_parameters.md`, and the
Phase 3 report file exists from its Step 0.

## Phase 3 — the Λ chain, then the algorithm loop

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

## Phase 4 — confirmation at scale and the deliverable

As version 2, with: R2 and R3 among the farm configurations; benchmark
plots as PNG; the capybara views R0 vs accepted on D5 and D6a in the PR
draft; the findings filed as drafted in the Phase 2 report (F4 + F9 as one
issue with B9d as the proposed fix, F1 as a `detector_benchmarks` PR,
F2, F3, F5, F6, F7 as issues); the review comments of Phase 3 Step 0
item 8 posted or declined.

## Reporting and checkpoints

- `{space}/reports/phase<N>_*.md` exists from the phase's Step 0 and grows
  at every verdict. Sections, in order: Summary; the scoreboard rows; the
  waterfall of accepted changes; the rejected hypotheses with why; the
  family ceilings; the G1 to G3 numbers of the current best; the gate
  table (`442`); the capybara views (checkpoints); the hypothesis tally
  (`440`); the headline (`441`); "Defaults you may veto"; "Next run
  recommendations". A report missing a section is not a phase close.
- `{space}/perf/scoreboard.csv` and `{space}/perf/headline.csv` are the
  tables every number comes from; the slides and the PR draft load them at
  build time. A number computed in chat is not a result.
- Plots under `{space}/plots/phase<N>/<experiment>/`, never overwritten,
  PNG (setup file, Review delivery, Plot format).
- Timestamps from `date -u` (`work-common.md`, How you work).
- When the user is remote: the checkpoint section, the benchmark PNGs, the
  gate table and the capybara non-owned view go to the chat with the
  file-sending tool.

## Rows for the decision table

Checked before the table of `work-common.md`, top to bottom, first match
wins; the rows of version 2 stay in force, these come first:

| you observe | response |
|---|---|
| the protocol patch is not applied (Every run, item 2) | its values govern; Q13 stays open; continue |
| a ceiling is measured that bounds the deliverable independently of the family under study | selector rule 4: re-rank the backlog before the next launch; `D-default` with the numbers |
| a lesson is written | the config or script that caused the trap changes in the same step; the lesson names the edit (`work-common.md`) |
| an upstream PR touches an owned file or the Λ chain | a reference row (parameter tier when its change is parameters, else a one-file patch on the pin) before the next experiment; a merged PR moves the baseline of the comparisons it affects, recorded as a `D-default` and in the setup file by the next protocol patch |
| the preflight of `300` fails (disk, processes) | the launch stops; free disk under the retention rule or wait; never launch around it |
| the integrity check finds a truncated output or an error in a log | the output is removed and reconstructed alone; the verdict waits |
| a Λ-family change moves S0 | the gate table shows a clustering collection moved: REJECTED (the family rule forbids it) and a finding if the change was meant to be Λ-only |
| the user's answer to a selector rule changes the selector | the ledger records the rule change with its date; verdicts before it stand; no experiment is re-judged |

## The scripts

As version 2, with these additions and changes (contracts; *Phase 3 Step 0
writes* marks scripts that do not exist yet):

| script | reads | writes | when |
|---|---|---|---|
| `300_run_experiment.py <experiment.yaml> --phase P [--reference R]` | as before | as before, plus: preflight before launch; integrity check after every chain; `701` after `401`; `442` after the gate | Phases 3, 4 (preflight and integrity: *Phase 3 Step 0 writes*) |
| `411_truth_partition.py <experiment>` | reco outputs with hit contributions | `S0_ideal` per momentum | Phase 3 Step 0 item 9 (*writes*, SHOULD) |
| `415_lambda_chain_offline.py <experiment> [--pairing stock\|vertex_fixed] [--variant tagged\|truth]` | `410`'s per-particle tables, the row's calibration | `{space}/perf/lambda-offline-<experiment>.json`: per momentum, per accepted event and per thrown, both pairings, both variants | Phase 3 Step 0 item 1 (*writes*); every experiment after |
| `440_hypothesis_tally.py [--phase P]` | `EXPERIMENTS.md` | the per-experiment and cumulative tally, printed and written to the phase report | after every verdict; checkpoints (*writes*) |
| `441_headline.py [rows…]` | `truth-<row>-D4_lambda.json`, `lambda-gun-acceptance.json`, `lambda-offline-<row>.json` when present | `{space}/perf/headline.csv`, the markdown table on stdout | after every verdict; every report line |
| `442_gate_evidence.py [rows…]` | `{data}/logs/experiments/<row>.log` | `{space}/perf/gate-evidence.json`, the markdown table on stdout | after every gate; every report |
| `443_capybara_views.sh <experiment> [--reference R0_stock] [--chunk chunk000]` | two reco outputs per D5 sample | capybara reports under `{data}/capybara/<experiment>-vs-<reference>/<dataset>/{nonowned,zdc}/`, the summary `{space}/perf/capybara-<experiment>-vs-<reference>.json` | checkpoints, code experiments |
| `701_pdf_to_png.sh <dir>` | every PDF under the directory | a PNG per page beside it | after `401`; once on the existing plots |
