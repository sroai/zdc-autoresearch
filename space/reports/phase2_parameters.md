# Phase 2 report — the parameter loop (closed under loop v3)

Status: CLOSED 2026-11-06 without further runs (D-user-21 stopped the loop at
six judged experiments on 2026-11-05; D-user-23 closed the phase). Ledger:
`space/EXPERIMENTS.md`, section Phase 2 (E01–E05, L01, the backlog).
Decisions this phase: D-user-18 to D-user-23, D-default-25 to D-default-32.
Written by the designer session from the record; every number cites its
file; no reconstruction was run (441, 442, 443 and 701 ran on 2026-11-06). Numbers per thrown Λ → nπ⁰ come from
`scripts/441_headline.py` (`space/perf/headline.csv`), the gate table from
`scripts/442_gate_evidence.py`, the tally recounted from the ledger.

## Summary

- **One accepted change.** E01 adopted P1b (R0 + `minClusterCenterEdep`
  25 → 5 MeV, `minClusterNhits` 10 → 2) after the pre-registered held-out
  check on D4h: ΔS0all +0.058 / +0.031 / +0.012 at 125 / 175 / 250 GeV,
  lost 0 (`space/perf/heldout-P1b_R0_thr-vs-R0_stock.json`). The current
  best is P1b with its refit calibration recorded, never reconstructed.
- **The parameter space is exhausted for the deliverable.** The Phase 2
  Step 0 measured that 89–97 % of the Λ photon pairs are merged into one
  cluster on P1b and that the survival thresholds can only recover the 1–3 %
  "missing" photons; the chaining threshold (E02, E04) buys separation with
  neutron energy. Both families are closed (rule 7). The Λ yield is 0.00 %
  per thrown for every 3×3 clustering (headline below).
- **The cap is in the Λ chain, and it is lifted by code the program may
  change.** Under the pin's `LambdaReconstruction` the yield cannot exceed
  0.85 % per thrown (mean 100–275 GeV; 2.1 % at 275 GeV) whatever the
  clustering (`414`, stock pairing, perfect separation); a stable
  vertex-aware pairing reaches 14.1 % (27.8 % at 275 GeV). Upstream PR 3063
  now removes the π⁰ window (F4) and exposes the IDOLA divergence (F9);
  `414`'s `vertex` pairing predicts it at 0.8–25.6 % per thrown
  (`try1-assessment.md`, section 5). Try 2 starts there (loop v3).
- **No other calorimeter moved.** Every experiment's G4 compared all 62 D5
  chunks against R0: 9043 non-ZDC leaves identical on each (gate table).
  D5 is DIS, every detector fills, so the other calorimeters' benchmark
  plots are identical by construction. The capybara views of the current
  best vs R0 are in the section below.

## The scoreboard rows (D4, S0all per momentum, mean over 100–275 GeV)

From `space/reports/phase1_dissection.md` (R0, P1b) and the paired deltas
of the ledger (E02–E05 vs P1b, significant at 3σ unless marked n.s.):

| row | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | mean |
|---|---|---|---|---|---|---|---|---|---|
| R0_stock | 0.006 | 0.019 | 0.022 | 0.023 | 0.021 | 0.022 | 0.015 | 0.011 | 0.017 |
| P1b_R0_thr = E01 (current best) | 0.075 | 0.075 | 0.057 | 0.051 | 0.042 | 0.039 | 0.032 | 0.018 | 0.048 |
| E02 − P1b | +0.016 | +0.016 | +0.020 | +0.015 | +0.017 | +0.017 | +0.018 | +0.012 | 0.065 |
| E03 − P1b | significant at 100–125 GeV only | | | | | | | | 0.053 |
| E04 − P1b | +0.006 to +0.011 at every momentum | | | | | | | | 0.057 |
| E05 − P1b | no cell moves | | | | | | | | 0.049 |
| L01 (= P1b clustering) | identical S0 | | | | | | | | 0.048 |

## Waterfall

| step | change | S0all mean | S0all per thrown | Λ (S4a_tm) per thrown | why it stopped here |
|---|---|---|---|---|---|
| R0 | stock pin | 0.017 | 0.29 % | 0.00 % | — |
| R2 | R0 + PR 3114 box (baseline for Λ from 2026-11-06) | 0.017 | 0.29 % | 0.00 % | no 3×3 photon has its own cluster to tag |
| E01 = P1b | seed 5 MeV, size 2 hits | 0.048 | 0.62 % | 0.00 % | the soft photon groups that the 25 MeV seed discarded now survive |
| L01 | P1b + PR 3114 box (Λ family) | 0.048 | 0.62 % | 0.04 % (0.07 % at 275 GeV) | 25 gained, 0 lost, below 3σ at every momentum: INCONCLUSIVE |

Every Phase 2 gain is S0γ at the low momenta (P1b +0.09 at 100 GeV, +0.01
at 275 GeV). The merged pairs are untouched.

## Rejected hypotheses, with their deltas

| row | change | predicted | measured | verdict |
|---|---|---|---|---|
| E02 | `minClusterHitEdep` 315 → 480 keV (chaining) | S0γ up +0.01–0.03 at 175–275 GeV; D3 raw sum −2 to −5 % | S0all +0.012–0.020 at every momentum; **D3 raw sum −13.4 % at 20 GeV**, −8.3 / −6.1 % at 50 / 100 GeV; S0n −0.024 at 275 GeV | REJECTED (S3, S0n) |
| E03 | `minClusterEdep` 50 → 20 MeV (survival floor) | S0γ up at 100–150 GeV; G3 toward its limit | S0all up at 100–125 GeV; **G3 0.97 low-energy clusters per SIDIS event (limit 0.5)**, clusters per neutron +0.69 (limit +0.5) | REJECTED (G3, S3) |
| E04 | `minClusterHitEdep` 315 → 400 keV (chaining, second point) | linear branch: raw sum −7 % at 20 GeV → REJECTED | S0all +0.006–0.011 at every momentum; **D3 raw sum −7.6 % at 20 GeV**; S0n −0.012 at 275 GeV | REJECTED, as pre-registered for the linear branch |
| E05 | `minClusterCenterEdep` 5 → 2 MeV (seed, second point) | null | no S0 or S1a cell moves | INCONCLUSIVE (the predicted null) |

The chaining threshold separates the halo that bridges photons and the
halo that is the low-energy neutron shower equally; it cannot select
between them (E02's understanding line). The premise survives as B11
(chain high, collect low), code tier, in Phase 3.

## Family ceilings (rule 7)

| family | points | ceiling |
|---|---|---|
| chaining threshold `minClusterHitEdep` | E02 (480 keV) REJECTED, E04 (400 keV) REJECTED | closed at 315 keV (stock); the gain is real (+0.012–0.020 S0all) and costs neutron energy at 20–100 GeV |
| survival thresholds `minClusterCenterEdep`, `minClusterNhits`, `minClusterEdep` | P1b ACCEPTED (5 MeV / 2 hits), E03 REJECTED (floor 20 MeV), E05 null (seed 2 MeV) | closed at P1b's values |
| layer range `neighbourLayersRange` | P1a (3) REJECTED, P1d (1 on columns) best | closed at 1 without the B4 run: 3 gained nothing at any momentum and 1 is best on columns, so 2 cannot change the current best (D-default-26) |
| XY distance | P1c (code tier) REJECTED on G1, G2, S3 | code tier only; B7 split reaches in Phase 3 |
| HEXPLIT, `sectorDist` | not run | dropped (second order; no mechanism inside one module; D-default-26) |

## G1 to G3 of the current best (D5, from `space/perf/scoreboard.csv`)

| guard | NC Q² > 100 | SIDIS Q² < 1 | limit (D-default-19) | R0 for reference |
|---|---|---|---|---|
| G1 φ within 5° of ±180° | 0.061 | 0.068 | ≤ 0.15 | 0.068 / 0.074 |
| G1 single-column clusters | 0.0003 | 0.000 | ≤ 0.05 | 0 / 0 |
| G2 cluster fraction above 50 GeV | 0.467 | 0.686 | ≥ 50 % of R0 | 0.612 / 0.864 |
| G3 clusters below 5 GeV per event | 0.110 | 0.182 | ≤ 0.5 | 0.006 / 0.010 |
| G3 clusters per event | 0.733 | 1.244 | — | 0.555 / 0.984 |
| G3 nhits median | 338 | 924 | — | 505 / 1079 |

S3 raw neutron sum (D3): P1b 0.500 / 0.616 / 0.680 / 0.721 / 0.737 / 0.760
at 20 / 50 / 100 / 150 / 200 / 275 GeV against R0 0.087 / 0.432 / 0.662 /
0.714 / 0.733 / 0.758: P1b keeps the low-energy neutron that R0's 25 MeV
seed discarded.

## Gate table (`scripts/442_gate_evidence.py`, `space/perf/gate-evidence.json`)

| row | reference | D5 files compared | non-ZDC leaves per file | events | G4 |
|---|---|---|---|---|---|
| P1a_R0_nlr3 | R0_stock | 62/62 | 9043 | 6200 | PASS |
| P1b_R0_thr | R0_stock | 62/62 | 9043 | 6200 | PASS |
| P1c_R0_dist | R0_stock | 62/62 | 9043 | 6200 | PASS |
| P1d_R1_nlr1 | R0_stock | 62/62 | 9043 | 6200 | PASS |
| P1e_R1_thr | R0_stock | 62/62 | 9043 | 6200 | PASS |
| P1f_R1_dist | R0_stock | 62/62 | 9043 | 6200 | PASS |
| R2_pr3114 | R0_stock | 62/62 | 9043 | 6200 | PASS |
| E02_chain480 | R0_stock | 113/113 | 9043 | 11300 | PASS (62 chunks; the post-disk-fill rerun appended 51 more compares) |
| E03_clEdep20 | R0_stock | 114/114 | 9043 | 11400 | PASS (as E02) |
| L01_box3114 | R0_stock | 62/62 | 9043 | 6200 | PASS |
| E04_chain400 | R0_stock | 62/62 | 9043 | 6200 | PASS |
| E05_seed2 | R0_stock | 62/62 | 9043 | 6200 | PASS |

The gate is the leaf-level identity of `scripts/130_compare_collections.py`
on single-threaded outputs; it was seen to fail on a damaged non-ZDC leaf
and on a changed non-ZDC parameter in Phase 0 (`131_prove_gates.sh`). A
benchmark plot of any other calorimeter, the tracking or the PID is a
function of these leaves and therefore identical between R0 and every row
above.

## Capybara views (current best P1b vs R0, D5 chunk000 of each sample)

`scripts/443_capybara_views.sh P1b_R0_thr --reference R0_stock`; reports under
`/data/zdc-autoresearch/capybara/P1b_R0_thr-vs-R0_stock/`, summary
`space/perf/capybara-P1b_R0_thr-vs-R0_stock.json`. The non-owned view
excludes the owned prefixes of `configs/metrics.yaml` (relation branches
included); capybara prints a leaf only when the two inputs differ, so the
view must print none. The ZDC view shows what P1b changed.

| D5 sample (chunk000, 100 events) | view | leaves compared | leaves differing | below p = 1 | collections that differ |
|---|---|---|---|---|---|
| NC Q² > 100 | non-owned (every other detector, tracking, PID; relation branches included) | 1613 | **0** | 0 | none |
| NC Q² > 100 | ZDC (owned) | 165 | 142 | 46 | `HcalFarForwardZDCClusters*`, `HcalFarForwardZDCImagingProtoClusters`, the cluster links and associations, `ReconstructedHcalFarForwardZDCNeutrals` |
| SIDIS Q² < 1 | non-owned | 1656 | **0** | 0 | none |
| SIDIS Q² < 1 | ZDC (owned) | 153 | 142 | 39 | the same owned collections |

Capybara prints a leaf only when its two inputs differ in shape, per-event
count or any value, so a non-owned view with no leaf printed is the
per-leaf proof on the reviewers' own tool. The ZDC view shows the 142 leaves
P1b changes (cluster energy, nhits, hits ranges, shapes, the neutrals built
from them); the Bokeh reports under the directory above are the overlays.

## Hypothesis tally (recounted from the ledger on 2026-11-06)

| phase | row | ✓ | ✗ |
|---|---|---|---|
| 1 | P1a | 2 | 2 |
| 1 | P1b | 2 | 3 |
| 1 | P1c | 3 | 3 |
| 1 | P1d | 1 | 3 |
| 1 | P1e | 4 | 1 |
| 1 | P1f | 5 | 0 |
| 2 | E02 | 5 | 4 |
| 2 | E03 | 4 | 4 |
| 2 | L01 | 7 | 0 |
| 2 | E04 | 7 | 0 |
| 2 | E05 | 5 | 0 |
| total | | 45 | 20 |

69 % of pre-registered cells right (Phase 1 59 %, Phase 2 78 %); the misses
are sizes, the directions were right in every Phase 2 experiment. From
Phase 3 the tally is a script's output (`440`, loop v3).

## Headline (`space/perf/headline.csv`, % per thrown Λ → nπ⁰; mean over 100–275 GeV / at 275 GeV)

| row | S0all (separation) | S4a_tm (Λ reconstructed) |
|---|---|---|
| acceptance (the ceiling of S0all) | 16.91 / 32.64 | |
| R0_stock | 0.29 / 0.34 | 0.00 / 0.00 |
| R1_pr3064 | 0.19 / 0.26 | 0.40 / 0.83 |
| R2_pr3114 | 0.29 / 0.34 | 0.00 / 0.00 |
| P1b_R0_thr (current best) | 0.62 / 0.59 | 0.00 / 0.00 |
| L01_box3114 | 0.62 / 0.59 | 0.04 / 0.07 |
| E02_chain480 | 0.89 / 0.97 | 0.00 / 0.00 |
| E03_clEdep20 | 0.66 / 0.66 | 0.00 / 0.00 |
| E04_chain400 | 0.76 / 0.77 | 0.00 / 0.00 |
| E05_seed2 | 0.62 / 0.59 | 0.00 / 0.00 |

Λ ceilings per thrown with P1b's resolution and perfect separation
(`space/perf/lambda-ceiling-variants-P1b_R0_thr.json`): stock pairing
0.85 / 2.1; PR 3063's pairing (IDOLA first) 12.0 / 25.6; stable vertex-aware
pairing 14.1 / 27.8.

## Defaults you may veto

- D-default-26 — the Phase 2 backlog is closed without B4, B2, B5, B6
  (reasons in Family ceilings); B11 moves to Phase 3 after B9d and B8.
- D-default-27 — R2 (R0 + PR 3114) is the baseline of every Λ comparison
  from 2026-11-06; S0 comparisons keep R0 (identical clustering).
- D-default-28 — the selector rules of loop v3 Phase 3: the Λ family on
  `S4a_tm` per thrown under the fixed window; clustering on S0 with `S4o`
  beside; after B9d is ACCEPTED, `S4a_tm` co-selects (S0all up and `S4a_tm`
  not down). Alternative: the Λ number as the one selector.
- D-default-29 — the re-rank rule: a measured ceiling that bounds the
  deliverable re-ranks the backlog before the next launch.
- D-default-30 — parameter experiments reconstruct every dataset with the
  restricted collections; full-collection D5, full G4 and capybara at
  checkpoints and for code experiments; the preflight of `300` is the only
  launcher (numbers in the setup file, Budgets, via the protocol patch).
- D-default-31 — the G4 evidence is published: the gate table in every
  phase report, the capybara non-owned and ZDC views at checkpoints.
- D-default-32 — plots: own scripts write PNG; PDFs from tools the program
  does not own get a PNG per page beside them (`701`, run by `300`).
- Q11 (a question, since it edits frozen `configs/metrics.yaml`): the S3
  raw-sum guard's momentum range. Recommended: guard at 50–275 GeV, 20 GeV
  reported. No Phase 2 verdict changes under either answer (E02 and E04
  also fail S0n at 275 GeV).

## Next run recommendations (loop v3, Phase 3 Step 0)

1. Apply the protocol patch (Q13), then start with the loop v3 start line.
2. Step 0 items 1–8 in order: the Λ chain on real clusters (`415`) on all
   rows; the headline extended with it; the restricted-collection template
   and the measured T; preflight and integrity in `300`; the hypothesis
   table and tally (`440`); the capybara views proven on the gate control;
   the reference rows R3 (PR 3063 on the pin) and R1p (the author's
   package); the three review comments.
3. Phase 3 experiments: B9d (R3 + the stable vertex) first, pre-registered
   against 14.1 / 27.8 % per thrown and against `415`'s number for P1b;
   then B11, B8, B7.
4. File the findings (F4 + F9 as one issue with B9d as the fix; F1 as a
   `detector_benchmarks` PR; F2, F3, F5, F6, F7 as issues).
