# Phase 0 report — foundation

Status: done 2026-11-05 (started 2026-11-04). Each Step 0 item lists its decisive
outcome and the evidence. Decisions are in `space/notes/DECISIONS.md`;
findings in `space/reports/phase0_findings.md`.

User answers at the start line (2026-11-04): checkpoint Q1 LYSO+SiPM (D-user-4),
Q2 selector S0 (D-user-5), Q3 `LambdaReconstruction` unchanged at least through
Phase 1 (D-user-6), Q4 to Q6 defaults (D-user-7).

## Summary

- The ruler stands: the image and builds (R0, R1, Rt, dist0p3), 39 gun points,
  D5 at the cluster budget, two MSF slices that pass the hit-level gate, a G4
  gate seen to fail, deterministic references (`references.json`), and paired
  errors shown honest on three seeds for R0 and R1 (`noise-validation.json`).
- PR 3064 in S0 terms (D4, 100–275 GeV): S0γ 0.04–0.07 → 0.33–0.40,
  S0n 0.64–0.67 → 0.03–0.07, S0all ≈ 0.01–0.02 for both. It separates photons
  by cutting every shower into single-subcell columns: 100 % of R1 clusters on
  D5 are one subcell wide, at φ = ±180°, √λ2 = 0. On the π⁰ gun this buys a lot
  (S1a_truth +0.3 to +0.6); on single particles it costs containment (D2 S0
  0.99 → 0.75, D3 0.97 → 0.085 at 100 GeV) and 20–26 % of the neutron energy.
- `LambdaReconstruction`'s IP-pointing π⁰ window passes no decay beyond 4 m:
  with ideal inputs the S4a ceiling on D4 is 0 at 100–125 GeV and at most 0.068
  (F4, measured). R1 already reaches 50–90 % of it at 200–225 GeV.
- Observations in owned code (backlog, not FINDINGS):
  - O1: on R0 no ZDC photon is tagged above 70 GeV. Both transverse √λ
    exceed `gammaMaxWidth` = 12 mm, so the γ calibration and length cut never
    act, R0 has no Λ at all, and S2 runs at 1.15–1.22.
  - O2: the HCal ZDC truth clusters (tile RecHits, `sampFrac` 1.0) are no
    perfect-clustering input.
  - O3: the stock calibration does not fit R0's clusters. With the stock
    photon law the residual scale is 0.69–0.87, 13–31 % low (the a·E^b form
    itself fits the photon points poorly, χ²/ndf = 65/6, so the refit a = 1.76,
    b = 0.920 and its pulls are indicative only). The neutron refit is good
    (a = 2.08, b = 0.911, χ²/ndf = 2.2/4); stock is 3–9 % high there.
  - O4: the benchmark π⁰ and photon scripts crash on R1's output.
- Open question for the user before Phase 2: Q7 (the S2 acceptance limit fails
  for R0 itself; recommended: judge S2 after the per-clustering refit).
- Live hook enforcement is not available to this session (see item 16).

## Item 1 — image and detector configurations

Outcome: PASS. The LYSO gun configuration exists in the image.

- Image `eicweb/eic_xl:26.11.0-stable`, digest
  `sha256:37e7fb527c8b3421bf2d353f4fc3146b1efb07a3a07ebd01bbced8417d29add3`
  (recorded in `zdc-setup.md`).
- Inside: `thisepic.sh` loads epic-main; present: `epic_zdc_lyso_sipm.xml`,
  `epic_zdc_sipm_on_tile_only.xml`, `epic_craterlake.xml` (the default 18x275
  beamline), `epic_craterlake_9x130.xml`, `epic_craterlake_9x275.xml`. The
  image has no `epic_craterlake_18x275.xml` (D-default-13).
- EICrecon 1.43.0 (image), ROOT 6.40.04, npsim from DD4hep in Python 3.13
  (`npsim --version` does not exist).
- `ZDC_SiPMonTile.xml` has the same md5 (`dd955e9c…`) in every epic release the
  image ships, 26.07.0 to 26.11.0 and main; `ZDC_Crystal_LYSO.xml` likewise
  (`42a010a8…`). The image ships no epic git history, so "unchanged since
  epic PR #1070" rests on these checksums. The MSF campaign (26.06) is
  checked at the hit level by item 6.

## Item 2 — EICrecon builds R0 and R1

Outcome: PASS. Both installs exist; the R1 patch applies to the pin without conflict.

- R0: `/data/zdc-autoresearch/install/eicrecon-e5e2a60c60b6`, `eicrecon --version` → `v1.43.0-3-ge5e2a60c`. Build 101 s (ccache in the image).
- R1: `space/notes/patches/R1_pr3064.patch` (`git diff 66b8cf62 fdbb773d` on
  the three files, 75 lines), `git apply --check` clean on the pin; install
  `/data/zdc-autoresearch/install/eicrecon-R1` (`v1.43.0-3-ge5e2a60c-dirty`).
  Build 102 s. Submodule restored, `git status` clean.
- The patch changes, besides the six parameters of
  `configs/experiments/R1_pr3064.yaml`, the XY neighbour distances
  `0.75 → 0.3 × side_length` in `ZDC.cc`.
- Builds take under two minutes, so code-tier experiments cost little build
  time.

## Item 3 — gun datasets

Outcome: done. 39 gun points on `epic_craterlake` (D-user-8), produced
2026-11-04 21:10 – 2026-11-05 00:22, every file in
`space/perf/manifest-datasets.json` (section `guns`, 78 files: HepMC and
edm4hep) with its event count, and every count equals the configured one:
D1 (50, 60, 70, 80, 100, 130, 160 GeV), D1h (50, 70, 100), D1n (100 GeV
seeds 2, 3), D4 (100–275 GeV in 25 GeV steps), D4h (125, 175, 250) and D4n
(175 GeV seeds 2, 3) hold 2000 events per file; D2 (20, 30, 50, 70, 100,
150, 200, 275) and D3 (20, 50, 100, 150, 200, 275) 1000. One manifest
defect fixed on the way: two writers of different sections finishing
together lost the `dis` section (read-modify-write without a lock, with the
read before minutes of hashing). `scripts/121_manifest.py` now hashes first
and reads, merges and renames under a file lock.

Gun geometry: at the pin the ZDC neutrals and Λs are empty on the ZDC-only
configurations (finding F5): `FarForwardNeutralsReconstruction` requires the
B0 ECal, EEMC-P and LFHCAL clusters, whose factories throw without those
detectors. A trial R0 reco of 1000 ZDC-only photons gave 0 neutrals; the
campaign MSF reco on the full geometry has 131 ZDC neutrals in 1000 events.
The user chose full-detector guns (`epic_craterlake` carries the same
`ZDC_SiPMonTile.xml` and `ZDC_Crystal_LYSO.xml`). The ZDC-only points that
finished first (D1 50–80 GeV, D1h, D1n, D2 20–200 GeV, D3 20–150 GeV) stay
in `/data/zdc-autoresearch/datasets_zdconly/` as a material-free cross-check.

Generator checks done before the production:

- 10-event dry run of every generator signature: PASS for D1 (`gen_pi0_decay`),
  D2 and D3 (python gun), D4 (`gen_lambda_decay`).
- `gen_particles.cxx` (photon benchmark generator) takes no seed and
  clock-seeds; D2 uses the seeded python gun (D-default-17).
- `gen_pi0_decay.cxx` drops events outside the acceptance from a fixed loop
  count. Accepted per 4000 generated: 20 GeV 0, 30 GeV 0, 50 GeV 810,
  60 GeV 1245, 70 GeV 1576, 80 GeV 1893, 100 GeV 2352, 130 GeV 2757,
  160 GeV 3021. D1 drops 20 and 30 GeV, D1h uses 50 GeV instead of 30 GeV,
  and every π⁰ point generates 6× its count (D-default-16).
- npsim reproducibility: same seed twice → HepMC bit-identical; edm4hep
  content identical in 77 of 78 leaves, only `EventHeader.timeStamp` differs;
  file sha256 differ (D-default-18).

## Item 4 — DIS inputs D5

Outcome: done. D5 meets the cluster budget (≥ 2000 R0 ZDC clusters per sample)
with npsim of the CI's EVGEN files on `epic_craterlake` (D-default-14; no
XRootD campaign usable: the campaigns holding these samples, 25.12.0
`NC/18x275/minQ2=100` and 26.02.0 `minQ2=1`, predate the 26.05 square-tile
ZDC, and `SIDIS q2_0to1` is in no FULL campaign).

| sample | EVGEN | chunks × 100 events | R0 ZDC clusters | per event | R1 clusters |
|---|---|---|---|---|---|
| D5_dis_minq2_100 | pythia8.316 NC Q² 100–1000 run000 | 40 | 2220 | 0.555 | 14 559 |
| D5_dis_minq2_0 | pythia6-eic SIDIS Q² 0–1 run1.ab | 22 | 2164 | 0.984 | 22 351 |

The first 30 + 15 chunks gave 1676 and 1470 clusters; `chunks` was raised
to 40 and 22 (`configs/datasets.yaml`) and the 17 new chunks simulated and
reconstructed with R0 and R1. All 62 files in the manifest (section `dis`,
100 events each). Full-detector npsim: about 20 s per event under full
machine load; reconstruction 1000–2550 s per 1000 events.

## Item 5 — MSF slice D6a

Outcome: PASS.

- Files: `/data/meson-structure-2026-07/dd4hep/9x130/msf_9x130_1000evt_0001` and `_0002` (`.edm4hep.root`), 1000 events each; the campaign reco exists for index 0001 only.
- Detector configuration `epic_craterlake_9x130`, image `eic_xl:26.06-stable`
  (`simulation-pipeline/simulation_pipeline/20_create_npsim_jobs.py`,
  `docs/campaign-2026-07/campaign-2026-07.md`).
- Background: none. `dd4hep_input` is `afterburner/<energy>-priority`, and the
  campaign has no background variant.
- D6b pattern confirmed by a farm listing: `dd4hep/<energy>/msf_<energy>_1000evt_NNNN.edm4hep.root`
  (1002 entries in `dd4hep/9x275`). `{msf}/docs/data.md` says `msf_ev1000_NNNN`, which is wrong.
- D6a_9x275 (D-user-9): campaign 2026-07's highest-yield energy for Λ → nπ⁰ in
  the ZDC (it has no 10x275 or 18x275); files 0001–0005 and the campaign reco
  of 0001 copied from the farm to `/data/zdc-autoresearch/msf-9x275/`.

## Item 6 — MSF compatibility gate

Outcome: PASS — D6 stays in the program.

`scripts/132_msf_hit_compat.py` reconstructed `msf_9x130_1000evt_0001` with R0
(single-threaded, only the four ZDC hit collections) and compared it event by
event with the campaign's `reco/9x130/msf_9x130_1000evt_0001.edm4eic.root`
(EICrecon of `eic_xl:26.06-stable`): identical hit counts, cellID sets and
energy sums in all 1000 events for `HcalFarForwardZDCRawHits` (96 146 hits),
`HcalFarForwardZDCRecHits` (38 545), `EcalFarForwardZDCRawHits` (12 882) and
`EcalFarForwardZDCRecHits` (7 057).

Repeated on 9x275 (D6a_9x275, file 0002, `epic_craterlake_9x275`): PASS —
identical counts, cellID sets and energy sums in all 1000 events for
`HcalFarForwardZDCRawHits` (1 126 107 hits), `HcalFarForwardZDCRecHits`
(490 124), `EcalFarForwardZDCRawHits` (85 255), `EcalFarForwardZDCRecHits`
(48 995). The ZDC holds about 12 times more hits per event at 9x275 than at
9x130.

## Item 7 — neighbour-distance tier

Outcome: decided (D-default-15): option (b), three code-tier builds (below
the 24.4 mm pitch, 3×3, 5×5) when Phase 1 needs them. No parameter is exposed,
`ImagingTopoCluster_factory.h` stays untouched, and no patch is written in
Phase 0.

## Item 8 — R0 and R1 on every dataset

Outcome: done. `scripts/120_reconstruct.py`, single-threaded, `.*` output, with
R0 (`eicrecon-e5e2a60c60b6`) and R1 (`eicrecon-R1`) on D1, D2, D3, D4, both D5
samples, D6a_local and D6a_9x275, and on the noise seeds D1n/D4n (item 13).
Rt (`eicrecon-truthchain`) ran on D4. `space/perf/scoreboard.csv` holds the rows
R0_stock, R1_pr3064 and Rt_truthchain (D4 only, partial) in that order;
`space/perf/metrics-<exp>.json` has every cell with its error. The `S4a_Rt_eff`
cells are the truth chain as built (0 in every row, observation O2), not the
ceiling. The ceiling is `space/perf/lambda-ceiling-R0_stock.json` (item 12).
`space/perf/references.json` holds the sha256 of every output (102 R0, 102 R1,
8 Rt files).

Determinism: D4 175 GeV reconstructed twice more with R0 on a quiet machine
(`/data/zdc-autoresearch/determinism/`): all 9048 non-ZDC and 960 ZDC leaves
identical over 2000 events between the two repeats and against the stored
production output. The MSF gate controls (item 10) give the same on D6a.

R1 from the patched build against R1 from parameters: identical on every ZDC
leaf when the distances come from the `dist0p3` build (item 9). With
parameters alone (`R1param_pr3064.yaml`) the distances stay at 0.75 ×
side_length, so that configuration is not R1 (D-default-15).

Wall time per 1000 events (median over files, single-threaded, 9–18
processes in parallel on 24 cores; the quiet repeat of D4 175 GeV took
501 s per 1000, the same as under load):

| dataset | R0 [s/1000] | R1 [s/1000] |
|---|---|---|
| D1 π⁰ | 279 | 270 |
| D2 γ | 236 | 236 |
| D3 n | 415 | 418 |
| D4 Λ | 504 | 498 |
| D5 NC Q² > 100 | 2417 | 2548 |
| D5 SIDIS Q² < 1 | 1338 | 1001 |
| D6a 9x130 | 692 | 624 |
| D6a 9x275 | 696 | 742 |

The ZDC clustering is not the cost: R0 and R1 agree within the
file-to-file spread. A full gun-plus-DIS experiment (44 000 gun and 6 200
DIS events) costs about 40 min on 9 parallel processes.

## Item 9 — switch tests

Outcome: every PR parameter changes the ZDC output on a clustering where it
can act; three of the six are inert on R0, which is observation O1 (owned code: a backlog entry, not a FINDINGS item).
`scripts/133_switch_tests.sh`, 300 events per run, verdicts in
`space/perf/switch-tests.json`:

| parameter (stock → PR) | dataset, clustering | ZDC output |
|---|---|---|
| `neighbourLayersRange` 1 → 3 | D1 100 GeV, R0 | differs (associations, event 270) |
| `minClusterCenterEdep` 25 → 5 MeV | D1 100 GeV, R0 | differs (event 10) |
| `minClusterNhits` 10 → 2 | D1 100 GeV, R0 | **identical** (no R0 cluster has fewer than 10 hits) |
| same, 2 → 10 | D1 100 GeV, R1 | differs (event 1) |
| `gammaScaleCorrCoeffHcalZDC` (1.1, 0.98) → (2.7, 1.27) | D2 100 GeV, R0 | **identical** |
| same, PR → stock | D2 100 GeV, R1 | differs (neutral energy 56.9 vs 11.6 GeV) |
| `gammaMaxLength` 100 → 150 mm | D2 and D3 100 GeV, R0 | **identical** |
| same, 150 → 100 | D2 100 GeV, R1 | differs (neutral PDG counts) |
| `neutronScaleCorrCoeffHcalZDC` (2.4, 0.89) → (16.65, 0.66) | D3 100 GeV, R0 | differs (109.7 vs 283.4 GeV) |

Why the γ parameters are inert on R0 (observation O1): `isGamma` requires fewer
than two of the three √eigenvalues above `gammaMaxWidth` = 12 mm. R0 photon
clusters at 100 GeV have √λ medians (74, 14.2, 12.5) mm, so every one fails
the width test: no ZDC photon is ever tagged on R0 (D2 γ-tag efficiency 0 at
100–275 GeV, 3–9 % at 20–70 GeV), and the γ coefficients and length never
apply. On R1 the single-column clusters have widths (96.8, 0, 0) mm, so
nearly every cluster is tagged a photon (D2: 5630 photon neutrals from 1000
photons).

Equivalence (item 8): the R1 build against the `dist0p3` build (only the
PR's XY distances, `space/notes/patches/dist0p3.patch`, install
`eicrecon-dist0p3`, 187 s) plus the six PR parameters: all 960 ZDC leaves
identical on D1 100 GeV and D4 175 GeV (300 events each). R1 is exactly
"distances (code) + six parameters"; `R1param_pr3064.yaml` alone (no
distances) is therefore not R1, as the ledger states.

## Item 10 — gate proofs

Outcome: PASS — the gate has been seen to fail. `scripts/131_prove_gates.sh`
reconstructs the first 300 events of `msf_9x130_1000evt_0001` four times with
R0; controls under `/data/zdc-autoresearch/gate-controls/`:

| control | expected | got |
|---|---|---|
| R0 twice, non-ZDC leaves | PASS | PASS, 9043 leaves identical (determinism) |
| R0 twice, ZDC leaves (`--zdc`) | PASS | PASS, 960 leaves identical |
| `EEMC:EcalEndcapNRecHits:thresholdValue` 4 → 40 | FAIL | FAIL at `EcalClusterAssociations_objIdx`, event 86 |
| `ZDC:HcalFarForwardZDCImagingProtoClusters:minClusterHitEdep` 315 keV → 3 MeV | PASS | PASS |
| the same, `--zdc` | FAIL | FAIL at `HcalFarForwardZDCClusterAssociations.weight`, event 36 |
| capybara on the non-ZDC control | names EcalEndcapN | names EcalEndcapN |

The proof found two defects of the ruler, both fixed before it passed:
`minClusterNhits` 10 → 40 changed no ZDC leaf (MSF ZDC clusters have a median
of 488 hits), so it could not serve as a ZDC control; and the gate counted
podio relation branches `_<collection>_<relation>` of ZDC collections as
non-ZDC (a ZDC change failed G4). `collection_of` in
`scripts/130_compare_collections.py` now maps a relation branch to its
collection.

Owned-collection list: R0 against R1 on both D6a files passes G4 (9043
non-ZDC leaves identical over 1000 events each). Of the owned collections
outside the ZDC prefix, R1 leaves `ReconstructedB0EcalNeutrals` (640),
`ReconstructedEcalEndcapPNeutrals` (91) and `ReconstructedLFHCALNeutrals` (2)
identical and changes `ReconstructedHcalFarForwardZDCNeutrals` (63 → 277 in
file 0001), `ReconstructedLambdas` (0 → 1) and
`ReconstructedLambdaDecayProductsCM` (0 → 3). The Δ 40 of the PR's
`tracking_only` capybara page therefore does not come from a single-threaded
R1 change outside the owned list; the list is complete for what R1 touches.

## Item 11 — truth matching and the scoreboard

Outcome: every gun cell computed for R0 and R1 (`scripts/410_truth_match.py`,
`scripts/400_scoreboard.py`; `space/perf/metrics-<exp>.json`). The field names of
`configs/metrics.yaml` matched the files; no correction was needed. Cells that
cannot be computed are findings, not blanks: on R0, S4b (Λ mass and decay-z
resolution) has no Λ to measure (S4a = 0 at every momentum), and S1b/S1c need
two distinct photon clusters, which R0 rarely makes above 60 GeV.

S0 on D4 (separated: purity ≥ 0.8 and containment ≥ 0.5):

| p [GeV] | R0 S0γ | R1 S0γ | R0 S0n | R1 S0n | R0 S0all | R1 S0all | R1 S4a_tm |
|---|---|---|---|---|---|---|---|
| 100 | 0.056 | 0.343 | 0.673 | 0.070 | 0.006 | 0.015 | 0.0015 |
| 125 | 0.067 | 0.363 | 0.662 | 0.057 | 0.019 | 0.022 | 0.005 |
| 150 | 0.070 | 0.395 | 0.664 | 0.041 | 0.022 | 0.016 | 0.0115 |
| 175 | 0.065 | 0.399 | 0.648 | 0.042 | 0.023 | 0.015 | 0.0175 |
| 200 | 0.060 | 0.395 | 0.647 | 0.036 | 0.021 | 0.011 | 0.028 |
| 225 | 0.057 | 0.373 | 0.653 | 0.034 | 0.022 | 0.011 | 0.031 |
| 250 | 0.043 | 0.352 | 0.640 | 0.037 | 0.015 | 0.010 | 0.0245 |
| 275 | 0.036 | 0.326 | 0.647 | 0.033 | 0.011 | 0.008 | 0.0255 |

R0 merges the Λ photons (S0γ ≈ 0.06); R1 separates a third of them and
shatters the neutron (S0n 0.65 → 0.04); the event-level S0all is near zero
for both, with no significant difference at most momenta (paired McNemar:
|z| < 3 at all eight). On D1 (π⁰, two photons) R1 gains strongly:
S1a_truth (both photons separated) +0.31 to +0.62 at 60–160 GeV, z > 20.
On single particles R1 costs: D2 photon S0 0.99 → 0.75 at 100 GeV (shards
fail containment), D3 neutron S0 0.97 → 0.085 at 100 GeV, and the raw neutron
energy sum loses 20–26 % above 50 GeV (bootstrap z −24 to −145): the shards
below `minClusterEdep` = 50 MeV are dropped.

Corrected energies: R0 tags every ZDC photon a neutron (O1), so S2 is the
neutron calibration applied to photons (scale 1.15–1.22). R1 applies the PR
γ coefficients to the best shard: median corrected scale 1.48 at 20 GeV
rising to 4.36 at 275 GeV, against R0 by +0.31 to +3.21 (paired bootstrap
of the median, z > 11). Two ruler defects fixed on the way: `fit_peak`
accepted a Gaussian whose mean left the fit window (R1's S2 scale came out
−137); it now rejects such fits, the S2/S3 cells carry median and robust-σ
companions, and the paired S2 test bootstraps the median.

## Item 12 — truth-cluster ceiling

Outcome: the IP-pointing π⁰-window cap is confirmed with numbers; the truth
chain as built gives no ceiling (observation O2, owned code in ZDC.cc).

The build: `space/notes/patches/truthchain.patch` (38 lines in `reco.cc`: a second
`FarForwardNeutralsReconstruction` on `HcalFarForwardZDCTruthClusters`, a second
`LambdaReconstruction` writing `ReconstructedLambdasTruth`; all new names under owned
prefixes), install `eicrecon-truthchain`, 225 s, config `configs/experiments/Rt_truthchain.yaml`.
The Rt build ran on all of D4 (16 000 events): `ReconstructedLambdasTruth` is
empty at every momentum. The cause is not `LambdaReconstruction`:
EICrecon's `HcalFarForwardZDCTruthClusters` come from tile RecHits with
`sampFrac = 1.0` (the imaging clusters use 0.0273), so their energies are 3 %
of the imaging cluster energies (median event sum 3.8 vs 125.9 GeV at
175 GeV). Their tile-level shapes fail the photon width cut: of the photon
truth clusters, 0.3 % would be tagged γ at `gammaMaxWidth` = 12 mm (22 % at
20 mm, 41 % at 30 mm, while 44 % and 61 % of neutron truth clusters would
pass the same cuts). No parameter setting makes the truth chain a fair
perfect-clustering input.

The ceiling was therefore measured offline (`scripts/412_lambda_ceiling.py`,
`space/perf/lambda-ceiling-R0_stock.json`). It feeds `LambdaReconstruction`'s
own steps (π⁰ window on IP-pointing photons, the nγγ window, the IDOLA vertex
iteration and the mass window again; pin defaults) with ideal inputs: true
energies, the true daughter lines at shower depth, and acceptance = energy
in any ZDC cluster.

| p [GeV] | in ZDC | pass π⁰ window | ceiling | pass fraction in true decay z bins 0–1/1–2/2–3/3–4/4–6/>6 m |
|---|---|---|---|---|
| 100 | 0.875 | 0.000 | 0.000 | no decays below 6 m in D4; 0 above |
| 125 | 0.929 | 0.000 | 0.000 | none below 4 m; 0 above |
| 150 | 0.962 | 0.007 | 0.007 | –/–/–/0.50/0/0 |
| 175 | 0.969 | 0.025 | 0.025 | 1.00/1.00/1.00/0.76/0/0 |
| 200 | 0.976 | 0.030 | 0.030 | 1.00/1.00/1.00/0.40/0/0 |
| 225 | 0.980 | 0.050 | 0.050 | 1.00/1.00/1.00/0.72/0/0 |
| 250 | 0.986 | 0.062 | 0.062 | 1.00/1.00/1.00/0.59/0/0 |
| 275 | 0.987 | 0.068 | 0.068 | 1.00/1.00/1.00/0.58/0/0 |

With perfect clustering and identification, every decay within 3 m passes
and none beyond 4 m does. The π⁰ window alone decides it: the γγ mass from
IP-pointing photons scales as (L − z_d)/L, and ±10 % of m_π0 allows
z_d ≲ 0.1 L ≈ 3.6 m. The review's estimate holds. S4a cannot exceed
0.07 at any D4 momentum and is zero at 100–125 GeV whatever the clustering
does. R1's measured S4a_tm (0.028–0.031 at 200–225 GeV) is already 50–90 %
of this ceiling. First `LambdaReconstruction` finding for the report: the
preselection, not the ZDC clustering, caps the Λ efficiency (proposal, not
an edit: checkpoint question 3).

## Item 13 — noise and significance

Outcome: the analytic errors are honest at both validation points.
`scripts/404_noise_validation.py` computes each metric on three independent
seeds alone (seed 1 from D1/D4, seeds 2 and 3 from D1n/D4n), all R0, with
the error the scoreboard quotes (binomial for efficiencies, event bootstrap
for means). It sets the seed spread against that error
(`space/perf/noise-validation.json`):

| point | metric | spread / quoted error | p(χ², 2 dof) |
|---|---|---|---|
| D1 100 GeV | S0γ | 0.80 | 0.53 |
| D1 100 GeV | S0all | 1.71 | 0.055 |
| D1 100 GeV | S0γ purity mean | 0.53 | 0.77 |
| D1 100 GeV | S1a_raw | 1.59 | 0.094 |
| D1 100 GeV | clusters per event | 1.97 | 0.031 |
| D4 175 GeV | S0γ | 0.99 | 0.39 |
| D4 175 GeV | S0n | 1.11 | 0.29 |
| D4 175 GeV | S0all | 0.72 | 0.58 |
| D4 175 GeV | S0γ purity mean | 0.96 | 0.41 |
| D4 175 GeV | S1a_raw | 1.46 | 0.12 |
| D4 175 GeV | clusters per event | 1.59 | 0.086 |

S0γ counts the two photons of an event as independent trials; the seed
spread shows this does not understate the error. The fitted cells (S1b, S1c,
S4a, S4b) cannot be validated on R0 (no π⁰ pairs, no Λ), so the same three
seeds were reconstructed with R1 as well:

| point (R1) | metric | spread / quoted error | p |
|---|---|---|---|
| D1 100 GeV | S0γ / S0all | 0.63 / 0.75 | 0.68 / 0.57 |
| D1 100 GeV | S1b mass μ / σ (bootstrap) | 0.53 / 0.26 | 0.71 / 0.94 |
| D4 175 GeV | S0γ / S0n / S0all | 1.35 / 1.71 / 0.51 | 0.16 / 0.044 / 0.76 |
| D4 175 GeV | S4a_tm / S4a_any | 1.57 / 1.33 | 0.11 / 0.19 |
| D4 175 GeV | S4b mass σ (bootstrap) | 0.60 | 0.73 |

No metric fails at p < 0.01 (26 tests, 11 on R0 and 15 on R1; one in a hundred fails by chance).
S1c is not computable on either clustering at 100 GeV: R0 rarely and R1
almost never (0.1–0.35 %) produce exactly two clusters. The
paired test (`400_scoreboard.py --compare`: McNemar on discordant events,
event bootstrap with shared resamples) is what every comparison prints from
here on.

## Item 14 — benchmark plots

Outcome: the four benchmark scripts run on R0 and every momentum has filled
histograms. On R1 the Λ and neutron scripts pass, and the π⁰ and photon
scripts crash inside the benchmark's own fits. Copies in
`scripts/700_benchmarks/` with three edits, all about reading: the collection
names, a skip for absent index files, and a branch filter. Reading all
~9000 branches of a full-detector file took more than 30 CPU minutes and
6.5 GB for the π⁰ script alone. `scripts/401_benchmark_plots.sh` runs them
in the pinned image; the neutron macro runs once per momentum.
`scripts/403_benchmark_entries.py` checks the result automatically: per
momentum, the entries of the collection and selection each script
histograms, and that the PDFs exist (`space/plots/phase0/<exp>/benchmarks/*.entries.txt`).

| benchmark | R0 | R1 |
|---|---|---|
| zdc_pi0 (events with exactly 2 ZDC clusters) | 3 PDFs; 1484 / 753 / 262 / 87 / 11 / 1 / 3 at 50–160 GeV | **crash**: `curve_fit` gets one point (69 / 29 / 19 / 7 / 7 / 5 / 3 two-cluster events) |
| zdc_lambda (cluster multiplicity; Λ) | 13 PDFs; multiplicity filled at every momentum; **0 Λ** at every momentum | 13 PDFs; Λ filled at every momentum |
| zdc_photon (PDG-22 neutrals) | 2 PDFs; 41 / 85 / 93 / 31 at 20–70 GeV, **0** at 100–275 GeV | **crash**: negative `yerr` in the resolution plot (1833 to 8823 photon neutrals: 1.8 to 8.8 per photon) |
| zdc_neutron (PDG-2112 neutrals) | 6 PDFs; 153 / 681 / 967 / 993 / 994 / 996 | 6 PDFs; 38 / 483 / 843 / 965 / 981 / 991 |

The empty cells are real, not reading failures. On R0 no ZDC photon is
tagged above 70 GeV (item 9), so the photon benchmark and every Λ
histogram are empty. The benchmark plots of the PR's CI could not have
shown R1's photon shards either.

## Item 15 — review findings as numbers (predictions written first)

Written 2026-11-05 00:45, before any D5 reconstruction existed. Predictions
(the review's mechanism, docs/expert-review-v1.md section 2.4), for ZDC
clusters of D5 (both samples):

| quantity | R0 predicted | R1 predicted |
|---|---|---|
| fraction of clusters with exactly one distinct subcell (x, y) | small (< 0.1) | > 0.9 |
| fraction of clusters with intrinsic φ within 5° of ±180° | small (< 0.1; D6a 9x130 R0 measured 0.037) | > 0.9 |
| intrinsic θ | spread | piles at 0 or a single value (a column has no transverse axis) |
| √λ2 lateral width vs energy | grows with energy | near zero at every energy |

Mechanism: R1's 0.3 × side_length = 14.6 mm neighbour distance is below the
24.4 mm subcell pitch, so no two subcells of one layer are neighbours and a
cluster can grow only along z.

Outcome (measured on the full D5: 40 + 22 chunks; `scripts/200_cluster_distributions.py`,
plots in `space/plots/phase0/cluster_distributions/`, cells in
`space/perf/metrics-<exp>.json`): **the mechanism prediction is confirmed** on
all four quantities.

| quantity | sample | R0 | R1 |
|---|---|---|---|
| single distinct subcell (x, y) per cluster | NC / SIDIS | 0.000 / 0.000 | **1.000 / 1.000** |
| φ within 5° of ±180° | NC / SIDIS | 0.068 / 0.074 | **1.000 / 1.000** |
| intrinsic θ, 16/50/84 % | NC | 1.4° / 2.9° / 7.6° | 1.4° / 1.4° / 1.4° (the 25 mrad beam crossing angle: a column along the proton axis) |
| √λ2 median, E < 5 / 5–20 / 20–50 / > 50 GeV | NC | 19 / 17 / 23 / 29 mm | 0.0 mm at every energy |
| clusters per event | NC / SIDIS | 0.555 / 0.984 | 3.64 / 10.16 |
| fraction above 50 GeV (G2) | NC / SIDIS | 0.612 / 0.864 | 0.006 / 0.016 |
| clusters below 5 GeV per event (G3) | NC / SIDIS | 0.006 / 0.010 | 2.13 / 5.44 |
| χ² of the log-energy spectrum vs R0 | SIDIS | — | 1062 |

Two ruler defects found and fixed before these numbers: the column count used
global (x, y), in which a subcell column drifts about 0.6 mm per layer at
−25 mrad, so it gave 0 for R1. It now rotates to the proton frame and rounds
to 1 mm, in both `200_cluster_distributions.py` and `400_scoreboard.py`.
And `shapeParameters` is a podio VectorMember with no `Coll.shapeParameters`
leaf; it is now read through its begin/end indices
(`zdc.edm.read_vector_member`).


## Item 16 — freeze

Outcome: `space/FROZEN` is in place (copy of `space/FROZEN.after-phase0`), and
extended by the shared readers (`zdc/edm.py`, `zdc/config.py`) and the ruler scripts written in Step 0 (121, 133, 200, 401, 403, 404, 412; `420_refit_calibration.py` stays writable until Phase 1 proves it), and the *Step 0 fills* values of `zdc-setup.md` are written (references, noise
validation, D5 sizing, T). The checkpoint questions Q4–Q6 are in
`space/QUESTIONS.md`, closed on the recommendations by D-user-7
(D-default-19 to 21); Q7 is open for Phase 2. Hook test: `.claude/hooks/protect.py`
fed the tool calls refuses an edit under `submodules/detector_benchmarks`,
under `LambdaReconstruction.cc`, of `configs/metrics.yaml`, of
`scripts/400_scoreboard.py` and a `sed -i` on `LambdaReconstruction.cc`, and
allows edits under `src/detectors/ZDC`, of
`FarForwardNeutralsReconstruction.cc` and of `space/EXPERIMENTS.md`. **Live
enforcement in this session: no.** A real Write under
`submodules/detector_benchmarks` went through (file removed at once, submodule
clean). This session was started from `/home/romanov/dev/meson-structure`,
so the hook in `zdc-autoresearch/.claude/settings.json` is not loaded. A run
started from the zdc-autoresearch directory gets it. For the rest of this
run the frozen list is kept by hand.

## Scripts repaired in Step 0

Before Step 0 established the ruler (editing checking scripts is normal work then):

- `scripts/120_reconstruct.py`, `132`, `131`: `-Pjana:nthreads` aborts eicrecon (unused key under strictness 2); the key is `-Pnthreads`. Parameter keys carry the plugin prefix (`ZDC:`, `reco:`, `EEMC:`); `configs/experiments/R1param_pr3064.yaml` and the frozen-parameter list in `configs/metrics.yaml` corrected.
- Outputs of npsim and eicrecon are written as `.part` and renamed on success (a killed run left files a rerun would have skipped).
- `scripts/121_manifest.py` records event counts by default.
- `scripts/130_compare_collections.py` compares leaf branches only and reports unreadable leaves; capybara runs through `uvx` (the submodule's `requires-python` makes `uv run --project` fail and would write a lock file into it).
- `scripts/131_prove_gates.sh` rewritten: the controls are real reconstructions (R0 twice, a non-ZDC parameter changed, a ZDC parameter changed) instead of uproot-rewritten flat copies, which the gate and capybara never see in practice.
- `scripts/410_truth_match.py` stores per particle the true kinematics, the neutral built from the best cluster and the cluster count, and per Λ event the truth-matched Λ; `scripts/400_scoreboard.py` rewritten to the v2 table with the paired tests (McNemar, event bootstrap).
- `configs/experiments/R1_pr3064.yaml` is the patched build (`install_label: R1`); the six-parameter form is `R1param_pr3064.yaml`.
- `zdc/edm.py` `fit_peak` rejects fits whose mean leaves the window (R1's S2 scale came out −137); S2/S3 have median and robust-σ companions; the paired S2 test bootstraps the median.
- Column diagnostics in the proton frame (`200`, `400`); `shapeParameters` read as a VectorMember (`zdc.edm.read_vector_member`); G3 threshold 5 GeV (the calibrated floor is 1.83 GeV).
- `scripts/121_manifest.py` writes under a lock after hashing (a section was lost).
- `scripts/300_run_experiment.py` gates the DIS samples only, as its docstring and the loop file say.
- New: `133_switch_tests.sh`, `403_benchmark_entries.py`, `404_noise_validation.py`, `412_lambda_ceiling.py`, `420_refit_calibration.py`; benchmark copies read only the branches they plot.

## Defaults you may veto

D-default-12 to D-default-24 (`space/notes/DECISIONS.md`).
