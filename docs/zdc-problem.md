# The ZDC problem — what is being optimized and why

The ePIC Zero-Degree Calorimeter (ZDC) reconstructs neutrons and photons at
zero degrees along the proton beam. The Meson Structure Function (MSF)
program needs it to reconstruct `Λ → n π⁰ → n γ γ`: one neutron and two
photons in the same calorimeter, a few centimetres apart at the ZDC face
(35.8 m from the interaction point).

## What changed

- epic PR #1070 (merged 2026-04-19, first in epic 26.05.0) replaced the ZDC
  HCal SiPM-on-tile hexagonal tiles (31.3 mm side, HEXPLIT H4 → 12 subcells)
  with square tiles (`CartesianGridXYStaggered`, 48.8 mm side, S2 stagger →
  4 subcells), matching the engineering CAD.
- EICrecon PR #2618 (2026-04-15) added S2 support and widened the
  `ImagingTopoCluster` neighbour thresholds for the ZDC from {15.65, 13.55} mm
  to `0.75 × side_length` = {36.6, 36.6} mm. Nearby neutron and photon
  showers chain into one cluster.
- Measured by Baptiste Fraisse on the MSF campaigns 26.02 (hex) vs 26.07
  (square), first 1000 events, same EICrecon (EICrecon issue
  [#2737](https://github.com/eic/EICrecon/issues/2737)):

| quantity | 26.02 (hex) | 26.07 (square) |
|---|---|---|
| events with ≥1 HCal cluster | 84.4 % | 46.3 % |
| HCal clusters / event | 1.027 | 0.511 |
| gamma-like clusters / event | 0.335 | 0.153 |
| median cluster energy | 26 GeV | 131 GeV |
| median RecHits / cluster | 127 | 1023 |
| events with HCal RecHits | 95.0 % | 68.5 % |
| RecHits / event | 800 | 479 |

- The Λ → nπ⁰ reconstruction efficiency in the MSF analysis collapsed
  (about 4.5 % → about 0) between the campaigns.
- Upstream knows: detector_benchmarks PR #276 (merged 2026-04-17) set the
  `zdc_pi0` benchmark to `allow_fail` with the note "pi0s are merged because
  forward insert changes are not backwards compatible"; the revert (#306)
  and "Update zdc_lambda benchmark" (#309) were still open in 2026-07.

## The candidate fix under review

EICrecon PR [#3064](https://github.com/eic/EICrecon/pull/3064)
(`baptiste/zdc-clustering-calibration`, head `fdbb773d`, 2 commits, 3 files):

| file | change |
|---|---|
| `src/detectors/ZDC/ZDC.cc` | `HcalFarForwardZDCImagingProtoClusters`: `neighbourLayersRange` 1 → 3; `sameLayerDistXY` and `diffLayerDistXY` 0.75 → 0.3 × side_length (36.6 → 14.6 mm); `minClusterCenterEdep` 25 → 5 MeV; `minClusterNhits` 10 → 2 |
| `src/algorithms/reco/FarForwardNeutralsReconstructionConfig.h` and `src/global/reco/reco.cc` | `neutronScaleCorrCoeffHcalZDC` {2.4, 0.89} → {16.65, 0.66}; `gammaScaleCorrCoeffHcalZDC` {1.1, 0.98} → {2.7, 1.27}; `gammaMaxLength` 100 → 150 |

Energy corrections are `E_corr = a · E^b` (`corrPower`); `isGamma` requires
cluster z before `gammaZMaxOffset` + ZDC position, the longest shower axis
under `gammaMaxLength` and at most one of the three axes over `gammaMaxWidth`.

Review feedback (wdconinc, 2026-10-30): "This seems to significantly affect
cluster distributions, in particular it removes essentially all cluster
intrinsic phi that isn't -180/+180 deg. Also removes essentially all higher
energy clusters, and results in many low energy clusters. Too few Lambda
events in CI to tell if it has an impact there." The capybara summary for
the PR shows leaf differences (Δ) on every DIS sample; the largest on
`rec_dis_18x275_minQ2=100_craterlake_18x275_Seeding_Seeding2` (Δ 1705) and
`rec_dis_18x275_minQ2=0_craterlake_18x275_MT` (Δ 840).

So three findings have to be turned into numbers and explained before the
PR can merge:

1. the intrinsic-φ distribution of ZDC clusters collapses to ±180°;
2. high-energy clusters disappear;
3. many low-energy clusters appear;

and Λ reconstruction has to be validated with enough statistics.

## What the loop may change

The reconstruction of the ZDC only. Owned files in `submodules/EICrecon`:

- `src/detectors/ZDC/ZDC.cc` — the factory chain and every clustering
  parameter (digitization, HEXPLIT subcells, `ImagingTopoCluster`, island
  clustering, cluster shapes, calibration `sampFrac`, `logWeightBaseCoeffs`);
- `src/algorithms/reco/FarForwardNeutralsReconstruction*` — neutron/photon
  separation and energy corrections;
- `src/algorithms/reco/LambdaReconstruction*` — the Λ from the neutrals;
- the ZDC block of `src/global/reco/reco.cc` (the two factories above).

Shared algorithms (`ImagingTopoCluster`, `HEXPLIT`, `CalorimeterIslandCluster`,
`CalorimeterClusterRecoCoG`, `CalorimeterClusterShape`) serve other
calorimeters. They may be edited only in the algorithm phase, under the guard
that every non-ZDC collection stays byte-identical to the reference.

Parameters need no rebuild: every config value above is a JANA parameter,
set on the command line as `-P<factory>:<name>=<value>` (for example
`-PHcalFarForwardZDCImagingProtoClusters:neighbourLayersRange=3`). Code
changes need a rebuild (30 to 60 minutes clean, minutes incremental).

## Where the metrics come from

- `detector_benchmarks` (`submodules/detector_benchmarks/benchmarks/zdc_*`):
  single-particle generators (`gen_pi0_decay.cxx`, `gen_lambda_decay.cxx`,
  `gen_particles.cxx` for photons, `gen_forward_neutrons.cxx`), the
  ZDC-only detector configuration `epic_zdc_sipm_on_tile_only`, and the plot
  scripts the collaboration reads (`zdc_pi0_plots.py`, `lambda_plots.py`,
  `zdc_photon_plots.py`, `fwd_neutrons_recon.C`).
- `epic-capybara` (`submodules/epic-capybara`): `capybara bara ref.root
  new.root` projects every TTree leaf and reports the differences — the
  same tool the EICrecon CI runs on every PR.
- The MSF campaign 2026-07 (`submodules/meson-structure/docs/data.md`):
  `k_lambda` DIS events through the full detector, 1000 events per file,
  about 1000 files per energy (`5x41`, `9x100`, `9x130`, `9x275`), DD4hep
  output on ifarm under `/work/eic3/users/romanov/meson-structure-2026-07/dd4hep`,
  simulated with `eic_xl:26.06-stable`. A few `9x130` files are local under
  `/data/meson-structure-2026-07/dd4hep/9x130`. The Λ analysis is
  `submodules/meson-structure/analysis/zdc-lambda` and
  `analysis/multicalo-lambda`.

## Open item carried from the MSF repository

JeffersonLab/meson-structure PR [#9](https://github.com/JeffersonLab/meson-structure/pull/9)
("Kaon SF post-analysis with models", Baptiste Fraisse, branch
`analysis/multi-calo-lambda`, 2026-07-02) is open and CONFLICTING with
`main`; it touches only `analysis/multicalo-lambda/`. Resolving it is a task
of its own, parked in `space/STATUS.md` until the user schedules it.
