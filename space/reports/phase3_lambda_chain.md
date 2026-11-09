# Phase 3 — the Λ chain, then the algorithm loop

Loop v3 (`zdc-autoresearch-loop-v3.md`), started 2026-11-06 18:14 UTC (try 2). Every number below comes
from a file under `space/perf/` named beside it; per-thrown numbers are per thrown Λ → nπ⁰ (D4 events ×
the acceptance of `413`). Current best clustering: P1b_R0_thr (E01). Λ baseline: R2 (R0 + PR 3114).

## Summary

- **The Λ chain runs offline on every row's real clusters** (`scripts/415_lambda_chain_offline.py`,
  Step 0 item 1). Validated: it reproduces `414` on ideal inputs exactly, and its tagged stock variant
  agrees with the in-EICrecon `S4a_tm` on every event where EICrecon's Λ used the photons' best-matched
  clusters (L01 z −1.0; R1 z +1.1 overall, |z| ≤ 1.6 per momentum).
- **The clustering, not only the chain, caps the deliverable.** With the stable-vertex pairing and each
  row's own calibration refit, P1b's clusters allow 0.56 % per thrown (mean 100–275 GeV) and R0's
  0.27 %, while perfect separation would allow 14.1 % (`414`). The column clusterings of PR 3064 reach
  3.4 % (R1) and 4.0 % (P1d) — paired against P1b on the same events z = 43 and 48. S0 ranks the same
  rows in the opposite order. The reversal comes from the neutron: the columns separate the photons best
  (S0_g 0.32–0.41 for R1 against 0.04–0.15 for P1b) and shred the neutron shower (S0_n 0.03–0.07 against
  0.65–0.70), which the chain does not need in one cluster. Q16 answered A (D-user-31): clustering now
  selects on S4o vertex_fixed `tagrefit` (EICrecon's tags and neutron, the row's refit), G1–G3 unchanged.
- **S4a_tm credits Λs built from photon fragments**: 101 of R1's 289 truth-matched Λs take a photon from a
  cluster other than that photon's best. Q15 answered B (D-user-30): `S4a_tm_best` (photon daughters on
  their best clusters) is the clustering co-selector under rule 3; Q14 answered A (D-user-29): 410's photon-tag
  column repaired. Both changes to the frozen `410` are `space/notes/patches/q14-q15-410.patch`, for the user to apply.
- **F10**: `LambdaReconstruction` reads the ZDC neutron's position from the event's first cluster;
  placing it at the neutron's leader keeps 20–57 % more stable-vertex Λs (`416`).
- **PR 3063 (R3) gives the first in-EICrecon Λ on the 3×3 clustering**: 0.17 % per thrown, +162 / −0 against R2. On MSF its
  candidates are background (22 per 1000 events, none of the 23 accepted true Λ).
- **B9d (stable vertex) INCONCLUSIVE**: +2 / −0 over R3; judged against R3, the chain it modifies (D-default-39, Q17).
- **B9e (neutron at its leader, F10) INCONCLUSIVE**: 195 Λ against R3's 162 (the offline prediction exactly; 0.221 % against
  0.171 % per thrown), no momentum at 3σ (largest z 2.89; pooled z +3.76, reported only; Q18).
- **B11 (chain high, collect low)** built, knob proven and pre-registered (predicted 0.294 → 0.446 % per thrown); launched
  and stopped at the user's request 2026-11-07 03:04 UTC before any output. Phase 3 halted for a loop restart.
- Step 0 items 1–8 and 10 done; item 9 (SHOULD) skipped. Phase 3 tally 19 ✓ / 6 ✗.

## Step 0

### Item 1 — the Λ chain on real clusters (`415`, `lambda-offline-<row>.json`)

Contract and choices: D-default-33 (variants, energies, positions, calibration), D-default-34
(validation criterion). The chain code moved from `414` to `zdc/lambda_chain.py`; `414`'s output was
reproduced byte for byte after the move.

Validation (`space/perf/lambda-offline-validation.json`; tagged stock vs in-EICrecon S4a_tm, events):

| row | S4a_tm | offline | only in EICrecon | of which fragment-built | only offline | z (all) | z (best clusters) |
|---|---|---|---|---|---|---|---|
| L01_box3114 | 25 | 24 | 1 | 0 | 0 | −1.00 | −1.00 |
| R1_pr3064 | 289 | 194 | 112 | 101 | 17 | −8.36 | +1.13 |

`415 --check-ideal P1b_R0_thr` reproduces `414`'s stock, vertex and vertex_fixed ideal columns at every
momentum (largest difference 0). Two traps found on the way, both in the inputs EICrecon hands its chain:
the stock preselection aims the neutron at its leader cluster while IDOLA reads `getClusters(0)` (F10),
and the neutrals factory's law returns the neutron's total energy, not its momentum.

Decision point — does any clustering row beat R0 on S4o vertex-fixed per thrown? Yes, by up to 3.7
points (headline below; paired tests `space/perf/lambda-offline-compare-<A>-vs-P1b_R0_thr-vertex_fixed_refit.json`):

| A vs P1b_R0_thr (S4o vertex_fixed_refit) | gained | lost | z |
|---|---|---|---|
| P1d_R1_nlr1 | 3139 | 307 | 48.2 |
| R1_pr3064 | 2692 | 309 | 43.5 |
| P1e_R1_thr | 786 | 653 | 3.5 |
| P1c_R0_dist | 720 | 663 | 1.5 |
| P1b_R0_thr vs R0_stock | 447 | 0 | 21.1 |

The neutron position (`416`, `lambda-neutron-position-<row>.json`): tagged triplets whose
`getClusters(0)` is the neutron's leader: 0 / 236 (R2), 0 / 566 (L01), 52 / 3638 (R1); stable-vertex Λs
with the neutron at cluster 0 → at its leader: 164 → 197, 332 → 522, 1053 → 1349.

### Item 2 — headline as data (`441`, `space/perf/headline.csv`)

The table is in the section Headline. `441` reads every key of `lambda-offline-<row>.json`; the S4o
columns are `stock`/`vertex_fixed` × `truth`/`tagged`/`refit`.

### Item 3 — cost of a parameter experiment

Template `configs/experiments/_template_parameter.yaml` (output collections `MCParticles`, `EventHeader`,
`.*FarForwardZDC.*`, `Reconstructed.*Neutrals.*`, `ReconstructedLambda.*`). Measured with
`T_R0_restricted` and `T_R0_full` (R0, D4 175 GeV and chunk000 of both D5 samples, run side by side;
`{data}/reco/T_R0_*/timing.csv`; `space/perf/restricted-template.json`):

<!-- T:begin -->
`uv run scripts/444_restricted_template.py` (`space/perf/restricted-template.json`, log `{data}/logs/phase3/444.log`):

| file | T restricted / full (s per 1000 events) | size restricted / full | owned collections (`130 --zdc`) |
|---|---|---|---|
| D4 175 GeV (2000 events) | 245 / 455 | 1409 / 1889 MB (0.746) | 960 leaves identical |
| D5 NC Q² > 100, chunk000 (100) | 436 / 3553 | 72 / 703 MB (0.103) | 960 leaves identical |
| D5 SIDIS Q² < 1, chunk000 (100) | 520 / 836 | 83 / 245 MB (0.337) | 960 leaves identical |

`410` (every S0 and S4a cell) and `200` (every G1–G3 number) are equal from the two outputs. One parameter
experiment on D1–D5: 67.4 GB full → 30.4 GB restricted (25.7 GB of it the guns, whose ZDC hit collections
dominate), above the setup's 10 GB target; the D5 reconstruction, which dominated the wall time, drops
5–8×. Load caveat: the full D5 NC chunk ran beside R3's 16 processes, the restricted one beside 6; the
setup's stock T for NC (2417 s per 1000, Phase 0) bounds the full-collection cost from below.
<!-- T:end -->

### Item 4 — preflight and integrity in `300`

`300` now refuses a launch when the free space is under 2 × the expected output or 150 GB, or when the
eicrecon processes running plus requested exceed the cores; after every reconstruction it checks each
output's JSON, log errors (ENOSPC, Traceback, segmentation, timeout; JANA's parameter table exempt) and
size (± 50 % of the reference counterpart, scaled by the restricted ratio), and stops before any number
(`{data}/logs/phase3/preflight-tests.log`):

| test | result |
|---|---|
| free-space floor 100 000 GB (free 379 GB) | refused, rc 1 |
| process cap 4 with 4 eicrecon running + 11 requested | refused, rc 1 |
| default thresholds | PASS |
| integrity on a damaged hard-link copy of P1b D4 (200 GeV cut to 50 MB, 225 GeV JSON removed, Traceback in the 250 GeV log) | 3 failures named, rc 1 |
| integrity on P1b (every dataset) | 91 outputs, 91 JSON, 91 clean logs, 91 sizes in ± 50 %; rc 0 |

### Item 5 — predictions as data (`440`)

`440_hypothesis_tally.py` reads the ledger (free-text `Hypothesis check:` of Phases 1–2, the
`hypothesis:` table from Phase 3 on) and reproduces try 1's 45 ✓ / 20 ✗ (section Hypothesis tally).

### Item 6 — G4 evidence visible (`442`, `443`)

P1b vs R0 (`space/perf/capybara-P1b_R0_thr-vs-R0_stock.json`): non-owned view 1613 (NC) and 1656
(SIDIS) leaves reported, 0 differing; the ZDC view 142 differing leaves in 8 owned collections. The
summarizer's counting check on the stored gate control (EEMC-N threshold ×10, `131`):

<!-- capy:begin -->
`scripts/443_capybara_views.sh GC_nonzdc --reference GC_reference --chunk gc --datasets D6a_local` on the stored
controls (`{data}/gate-controls/{reference,nonzdc}.edm4eic.root`, 300 MSF events; summary
`space/perf/capybara-GC_nonzdc-vs-GC_reference.json`): non-owned view 1366 leaves reported, 565 differing, 102
below p = 1, led by `EcalEndcapNRemnantClusters`, `EcalEndcapNClusters` (42 each) and `EcalEndcapNRecHits` (18);
the script flags the view as a failure (exit 1). ZDC view 157 leaves, 0 differing. The summarizer has been
seen to count the damage in the view that must print nothing.
<!-- capy:end -->

### Item 7 — reference rows R3 and R1p

Pre-registered in `space/EXPERIMENTS.md` (entries R3, R1p) before their runs. R3 = R2 + PR 3063
(`space/notes/patches/R3_pr3063.patch`, build label R3, 103 s with ccache); R1p = R1 + PR 3114's box
110 / 22 mm (D-default-36). Numbers: `space/EXPERIMENTS.md` (entries R3, R1p), `space/perf/lambda-paired-*.json`.

- **R3 (PR 3063) makes the first in-EICrecon Λ on the 3×3 clustering**: truth-matched Λ in the fixed window
  9 / 21 / 26 / 27 / 25 / 24 / 19 / 11 of 2000 at 100–275 GeV against R2's 0 (+162 / −0, McNemar z 3.0–5.2 at every
  momentum), 0.171 % per thrown (mean; `441` headline 0.170 %, events denominator). Untruthful candidates in the
  window: 4 in 16000. Only the two Λ collections change (capybara owned view on D5); G4 PASS. On MSF 9x275: 22.0
  candidates per 1000 events, 4.4 in the window, 0 of the 23 accepted true Λ — on physics events the candidates are
  background. Tally 5 / 1 (the miss: untruthful candidates on the gun, predicted ≥ 2 × S4a_tm, measured 4).
- **R1p (PR 3064 + main's box)**: the in-EICrecon Λ yield is unchanged by the box, 0.395 against 0.405 % per thrown;
  untruthful candidates halve at 250–275 GeV (z −3.3, −5.4); γ-tagged neutrals per Λ event 4.9 → 2.4. Tally 1 / 3
  (the box's length cut removes more column clusters than its width admits).

### Item 8 — review comments

`space/reports/review-comments.md`: drafts for PR 3114, PR 3063 and PR 3064, every number cited to its file; for
the user to post or decline.

### Item 9 — S0 ideal partition (SHOULD)

Not started.

## Scoreboard rows

% per thrown Λ → nπ⁰, mean over 100–275 GeV (`space/perf/headline.csv`, from `441`; full rows in
`space/perf/scoreboard.csv`). S4o tagged / tagrefit: the stable-vertex chain on EICrecon's own tags (tagrefit: with
the row's refit calibration, the clustering selector, D-default-38; rows without a refit show —).

| row | S0all | S4a_tm (in EICrecon) | S4o tagged | S4o tagrefit | S4o refit (truth-identified) |
|---|---|---|---|---|---|
| R0 stock | 0.291 | 0.000 | 0.000 | 0.000 | 0.273 |
| R2 = R0 + 3114 box | 0.291 | 0.000 | 0.173 | 0.187 | 0.273 |
| R3 = R2 + PR 3063 | 0.291 | 0.170 | 0.173 | — | — |
| B9d = R3 + stable vertex | 0.291 | 0.172 | 0.173 | — | — |
| B9e = R3 + neutron at its leader | 0.291 | 0.221 | 0.173 | — | — |
| P1b (current best clustering, stock box) | 0.623 | 0.000 | 0.000 | 0.000 | 0.560 |
| L01 = P1b + 3114 box | 0.623 | 0.038 | 0.294 | 0.294 | 0.560 |
| R1 = PR 3064 (fails G1) | 0.186 | 0.404 | 1.100 | 1.643 | 3.419 |
| R1p = R1 + 3114 box (fails G1) | 0.186 | 0.394 | 1.126 | — | — |

## Waterfall of accepted changes

None in Phase 3 yet. Current best clustering P1b_R0_thr (E01, Phase 2).

## Rejected hypotheses

- B9d (stable vertex on R3) — "S4a_tm up over R3 at every momentum, most at 100–150 GeV": +2 / −0, z ≤ 1.0.
  On the 3×3 clustering the decays IDOLA loses have merged photons anyway; INCONCLUSIVE (D-default-39).
- B9e (neutron at its leader on R3) — "S4a_tm vs R3 significant (z ≥ 3) at 175 and 200 GeV": z 2.00 and 2.89; the count
  (+33 net, 195) is the prediction exactly, the statistics per momentum are too small (Q18).
- R3 — "untruthful candidates ≥ 2 × S4a_tm on the gun": 4 against 162; inside the fixed 30 MeV window nearly
  every gun candidate is the true Λ.
- R1p — "S4c up ≥ 20 %", "S4a_tm down ≥ 20 % at 225–275 GeV", "untruthful up": −51 %, only 275 GeV, down.

## Family ceilings

- Clustering on the deliverable (Step 0 item 1): S4o vertex_fixed_refit, % per thrown, mean 100–275 GeV:
  R0 0.27, P1b 0.56, E02 0.79 (3×3 rows); R1 3.42, P1d 4.02 (column rows, outside G1); perfect
  separation 14.1 (`414`).
- Chaining and survival-threshold families: closed in Phase 2 (`phase2_parameters.md`).

## G1 to G3 of the current best

Unchanged from Phase 2 (`phase2_parameters.md`, G1 to G3): P1b inside every limit.

## Gate table

`space/perf/gate-evidence.json` (`442`); every D5 file of the row against R0's, non-ZDC leaves leaf by leaf.

| row | reference | D5 files compared | non-ZDC leaves per file | events | G4 |
|---|---|---|---|---|---|
| R3_pr3063 | R0_stock | 62/62 | 9043 | 6200 | PASS |
| B9d_stable_vertex | R0_stock | 62/62 | 9043 | 6200 | PASS |
| B9e_neutron_leader | R0_stock | 62/62 | 9043 | 6200 | PASS |

R1p reconstructed no DIS sample (parameter tier, D4 and D6a): G4 static, no PASS claimed. Capybara (`443`) R3 and B9d
vs R2 on both D5 samples: non-owned view 0 differing leaves; owned view: `ReconstructedLambdas` and
`ReconstructedLambdaDecayProductsCM` only (36 leaves each). B9e vs R3: non-owned 0; owned: the same two collections only.

## Capybara views

See Step 0 item 6.

## Hypothesis tally

<!-- tally:begin -->
| experiment | phase | ✓ | ✗ | cumulative ✓ / ✗ |
|---|---|---|---|---|
| P1a | 1 | 2 | 2 | 2 / 2 |
| P1b | 1 | 2 | 3 | 4 / 5 |
| P1c | 1 | 3 | 3 | 7 / 8 |
| P1d | 1 | 1 | 3 | 8 / 11 |
| P1e | 1 | 4 | 1 | 12 / 12 |
| P1f | 1 | 5 | 0 | 17 / 12 |
| E02 | 2 | 5 | 4 | 22 / 16 |
| E03 | 2 | 4 | 4 | 26 / 20 |
| L01 | 2 | 7 | 0 | 33 / 20 |
| E04 | 2 | 7 | 0 | 40 / 20 |
| E05 | 2 | 5 | 0 | 45 / 20 |
| R3 | 3 | 5 | 1 | 50 / 21 |
| R1p | 3 | 1 | 3 | 51 / 24 |
| B9d | 3 | 6 | 1 | 57 / 25 |
| B9e | 3 | 7 | 1 | 64 / 26 |
| B11 | 3 | 0 | 0 | 64 / 26 |

Per phase: Phase 1: 17 ✓ / 12 ✗; Phase 2: 28 ✓ / 8 ✗; Phase 3: 19 ✓ / 6 ✗
Cumulative: 64 ✓ / 26 ✗ (71 % of the scored predictions held).
<!-- tally:end -->

## Headline

<!-- headline:begin -->
`uv run scripts/441_headline.py` (all rows), % per thrown Λ → nπ⁰, mean 100–275 GeV / 275 GeV:

| row | S0all mean / 275 GeV (% per thrown) | S4a_tm mean / 275 GeV (% per thrown) | S4o_stock_tagged mean / 275 GeV (% per thrown) | S4o_stock_truth mean / 275 GeV (% per thrown) | S4o_vertex_fixed_tagged mean / 275 GeV (% per thrown) | S4o_vertex_fixed_truth mean / 275 GeV (% per thrown) | S4o_stock_refit mean / 275 GeV (% per thrown) | S4o_vertex_fixed_refit mean / 275 GeV (% per thrown) | S4o_stock_tagrefit mean / 275 GeV (% per thrown) | S4o_vertex_fixed_tagrefit mean / 275 GeV (% per thrown) |
|---|---|---|---|---|---|---|---|---|---|---|
| acceptance (ceiling of S0all) | 16.91 / 32.64 | | | | | | | | | |
| B9d_stable_vertex | 0.29 / 0.34 | 0.17 / 0.18 | 0.00 / 0.00 | 0.00 / 0.00 | 0.17 / 0.18 | 0.24 / 0.31 | — | — | — | — |
| B9e_neutron_leader | 0.29 / 0.34 | 0.22 / 0.31 | 0.00 / 0.00 | 0.00 / 0.00 | 0.17 / 0.18 | 0.24 / 0.31 | — | — | — | — |
| E02_chain480 | 0.89 / 0.97 | 0.00 / 0.00 | — | 0.00 / 0.00 | — | 0.63 / 0.64 | 0.07 / 0.13 | 0.79 / 0.85 | — | — |
| E03_clEdep20 | 0.66 / 0.66 | 0.00 / 0.00 | — | 0.00 / 0.00 | — | 0.43 / 0.38 | 0.06 / 0.08 | 0.58 / 0.56 | — | — |
| E04_chain400 | 0.76 / 0.77 | 0.00 / 0.00 | — | 0.00 / 0.00 | — | 0.53 / 0.49 | 0.07 / 0.15 | 0.67 / 0.66 | — | — |
| E05_seed2 | 0.62 / 0.59 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.42 / 0.38 | 0.06 / 0.08 | 0.56 / 0.51 | — | — |
| L01_box3114 | 0.62 / 0.59 | 0.04 / 0.07 | 0.04 / 0.07 | 0.06 / 0.08 | 0.29 / 0.30 | 0.56 / 0.51 | 0.06 / 0.08 | 0.56 / 0.51 | 0.04 / 0.07 | 0.29 / 0.30 |
| P1a_R0_nlr3 | 0.17 / 0.20 | 0.00 / 0.00 | — | 0.00 / 0.00 | — | 0.14 / 0.16 | 0.03 / 0.07 | 0.16 / 0.20 | — | — |
| P1b_R0_thr | 0.62 / 0.59 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.42 / 0.38 | 0.06 / 0.08 | 0.56 / 0.51 | 0.00 / 0.00 | 0.00 / 0.00 |
| P1c_R0_dist | 0.76 / 1.54 | 0.00 / 0.00 | — | 0.00 / 0.00 | — | 1.15 / 2.57 | 0.22 / 0.66 | 1.13 / 2.95 | — | — |
| P1d_R1_nlr1 | 0.27 / 0.48 | 0.39 / 0.95 | — | 0.51 / 0.93 | — | 1.93 / 2.74 | 0.47 / 1.13 | 4.02 / 6.98 | — | — |
| P1e_R1_thr | 0.79 / 1.36 | 0.14 / 0.33 | — | 0.19 / 0.31 | — | 0.50 / 1.07 | 0.24 / 0.64 | 1.20 / 2.66 | — | — |
| P1f_R1_dist | 0.36 / 0.34 | 0.00 / 0.00 | — | 0.01 / 0.00 | — | 0.04 / 0.03 | 0.03 / 0.07 | 0.32 / 0.31 | — | — |
| R0_stock | 0.29 / 0.34 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.24 / 0.31 | 0.05 / 0.08 | 0.27 / 0.33 | 0.00 / 0.00 | 0.00 / 0.00 |
| R1_pr3064 | 0.19 / 0.26 | 0.40 / 0.83 | 0.26 / 0.46 | 0.44 / 0.72 | 1.10 / 1.49 | 1.61 / 2.18 | 0.44 / 0.95 | 3.42 / 5.69 | 0.18 / 0.44 | 1.64 / 3.07 |
| R1p_pr3064_3114 | 0.19 / 0.26 | 0.39 / 0.64 | 0.27 / 0.41 | 0.44 / 0.72 | 1.13 / 1.28 | 1.61 / 2.18 | — | — | — | — |
| R2_pr3114 | 0.29 / 0.34 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.17 / 0.18 | 0.24 / 0.31 | 0.05 / 0.08 | 0.27 / 0.33 | 0.04 / 0.05 | 0.19 / 0.20 |
| R3_pr3063 | 0.29 / 0.34 | 0.17 / 0.18 | 0.00 / 0.00 | 0.00 / 0.00 | 0.17 / 0.18 | 0.24 / 0.31 | — | — | — | — |
| Rt_truthchain | 0.29 / 0.34 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.24 / 0.31 | — | — | — | — |
| T_R0_full | 0.32 / nan | 0.00 / nan | — | — | — | — | — | — | — | — |
| T_R0_restricted | 0.32 / nan | 0.00 / nan | — | — | — | — | — | — | — | — |
written /home/romanov/dev/zdc-autoresearch/space/perf/headline.csv (21 rows, 10 quantities)
<!-- headline:end -->

## Defaults you may veto

1. Selector rule 1 (D-default-28, user-confirmed D-user-24): the Λ family selects on `S4a_tm` per thrown.
2. Selector rule 2, as answered (Q16 A, D-user-31): clustering selects on S4o vertex_fixed `tagrefit`, paired per D4
   momentum against the current best (McNemar, 3σ), S0 beside, G1–G3 unchanged.
3. Selector rule 3, as answered (Q15 B, D-user-30): after B9d is ACCEPTED, `S4a_tm_best` co-selects clustering.
4. Selector rule 4 (D-default-29) and its first use, D-default-35: B9d stays first; clustering families
   follow (unfrozen by D-user-31).
5. Selector rule 5 (D-default-30): parameter experiments use the restricted template.
6. Selector rule 6 (D-default-30): `300`'s preflight is the only launcher. Step 0 item 3's two timing
   reconstructions ran through `120` directly before the preflight existed.
7. D-default-33: the S4o definitions (truth, tagged, refit variants).
8. D-default-34: the 415 validation is judged on events whose EICrecon Λ used the best clusters.
9. D-default-36: R1p uses main's box 110 / 22 mm.
10. D-default-37: Λ-family changes built on R3 take the untruthful-candidate guard against R3 (PR 3063 writes a
    candidate in every event with a triplet, so against R2 the guard fails by that PR's design); the selector
    stays S4a_tm per thrown vs R2.
11. Protocol deviation (recorded in `space/EXPERIMENTS.md`, B9d): B9d was launched before Step 0 items 7–8
    finished; its verdict waits for them.
12. D-default-38: the clustering selector is `415`'s `vertex_fixed_tagrefit`; its reference is L01 (P1b's clustering
    with the merged box), since P1b itself carries the stock box and tags no photon.
13. D-default-39 (Q17): an R3-based Λ change is judged against R3; B9d INCONCLUSIVE on that reading (ACCEPTED on
    rule 1's letter against R2).
14. D-default-40: B9e is built on R3 and predicted with `416 --pairing vertex`.
15. D-default-41: `space/FROZEN` opens the four shared ImagingTopoCluster files for Phase 3 (Q5 A); every change there is a
    new field whose default is the stock path, proven by a knob-off build reproducing L01.

## Next run recommendations

1. Re-test the stable vertex (B9d's patch, `space/notes/patches/B9d_stable_vertex.patch`) once a clustering with a
   materially higher S0_g than P1b is accepted: with ideal inputs IDOLA keeps 0.62–0.86 of its yield (`414`), and on
   the 3×3 clustering nothing is there to recover (B9d INCONCLUSIVE).
2. Post the review comments (`space/reports/review-comments.md`) — the user's step. The PR 3063 comment now carries
   B9e's measured gain for the one-line neutron-position fix.
3. Λ-family verdicts need more than 2000 events per momentum, or a pooled test (Q18): every Λ-code fix on the 3×3
   clustering is otherwise INCONCLUSIVE by construction.
