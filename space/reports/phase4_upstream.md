# Phase 4 — the accepted chain as upstream pieces (drafts; nothing posted)

Written 2026-11-08 at the Phase 4 close. The user decides what goes upstream and posts it; nothing here was pushed,
and no branch was cut for it (git in this program covers the EICrecon tries only, D-user-34).

## Base and proof of the split

The Phase 4 branch `zdc-autoresearch/phase4` (local, tip `a15b0db6`) stacks on the pin `e5e2a60c` and contains
two open upstream PRs, folded in by X1:

- eic/EICrecon PR 3064 (ZDC clustering, calibration, n/γ box; OPEN, last updated 2026-11-05),
  `space/notes/patches/R1_pr3064.patch`;
- eic/EICrecon PR 3063 (Λ mass windows removed, every triplet fitted; OPEN, last updated 2026-11-06),
  `space/notes/patches/R3_pr3063.patch`.

The four pieces below hold what Phase 4 adds beyond those two PRs, one patch per algorithm, under
`space/notes/patches/upstream/`. Applying 3064, 3063, U1, U2, U3 and U4 in that order to the pin's files gives the
branch tip byte for byte (checked 2026-11-08 with `patch -p1` on copies of the eleven files; scratch script
`split_upstream.py`). U4 needs U2 and U3, because it switches on their parameters.

| piece | patch | files | Phase 4 tries | findings fixed | lines +/− |
|---|---|---|---|---|---|
| U1 | `U1_lambda_stable_vertex.patch` | `LambdaReconstruction.cc` | X1 (B9d, B9e of Phase 3) | F9, F10 | 30 / 25 |
| U2 | `U2_neutrals_lambda_pairing.patch` | `FarForwardNeutralsReconstruction.{cc,h}`, its Config.h and factory | X2, X3, X5 (default), X8 (centroid), X9; the refit laws as defaults | F7 (default) | 222 / 15 |
| U3 | `U3_imaging_topo_core_split.patch` | `ImagingTopoCluster.{cc,h}`, its Config.h and factory | X7, X8 (core depth) | — | 157 / 4 |
| U4 | `U4_zdc_configuration.patch` | `src/detectors/ZDC/ZDC.cc`, `src/global/reco/reco.cc` | X1 (neighbourLayersRange 1), X5, X7, X8 | F6 (refit), F7 | 15 / 6 |

The findings are those of `space/reports/FINDINGS.md`: F6 the stock calibration does not fit the clusters, F7 the
photon depth cut measured from the ZDC centre, F9 the vertex iteration running away far from the IP, F10 the
neutron placed at the event's first cluster.

## Evidence per piece

Every number is S4a_tm per thrown Λ → nπ⁰ from `space/perf/headline.csv` and a pooled McNemar test on identical D4
events from `space/perf/verdict-<row>.json`. Ceilings: 14.1 % mean over 100–275 GeV, 27.8 % at 275 GeV.

| step | piece | mean / 275 GeV after the step | against | pooled gained / lost, z |
|---|---|---|---|---|
| X1 | U1 + U4 (+ 3064, 3063, refit) | 1.970 % / 4.309 % | R1 0.404 % / 0.832 % | 1325 / 154, +30.45 |
| X2 | U2 | 2.913 % / 5.500 % | X1 | 1433 / 416, +23.65 |
| X3 | U2 (weights) | 3.236 % / 5.957 % | X2 | 384 / 88, +13.62 |
| X5 | U2 default + U4 (depth limit at the face) | 4.373 % / 8.030 % | X4 | 972 / 28, +29.85 |
| X7 | U3 + U4 (+ refit) | 6.853 % / 12.942 % | X5 | 2827 / 308, +44.99 |
| X8 | U3 (core depth) + U2 (centroid) + U4 | 7.271 % / 13.970 % | X7 | 842 / 535, +8.27 |
| X9 | U2 (photon depth term) | 7.436 % / 14.101 % | X8 | 355 / 160, +8.59 |

Held out (D4h, fresh seeds): X5 against R1 pooled z +36.25; X9 against X5 pooled z +30.63. Fair play (`460`):
PASS on every row (truth-blind chain, raw hits identical to R0, one honest candidate per event).

## U1 — LambdaReconstruction: stable decay vertex, neutron at its reference point

**Best posted as a review comment on PR 3063** (a draft follows), or as a follow-up PR after 3063 merges.

Draft description:

> PR 3063 fits every n γγ triplet. Two problems remain in `reconstruct_from_triplet`:
>
> 1. *The vertex iteration diverges for decays far from the IP.* It moves the vertex along the Λ direction
>    recomputed from the current vertex, so a 10–30 m decay walks off transversely. A Λ from the IP has a fixed
>    slope at small angles: the momentum-weighted centroid of the impact points, Σ pᵢxᵢ / Σ pᵢzᵢ, whatever the decay
>    depth. Only the depth is unknown, and the γγ opening angle grows monotonically with it, so the depth follows by
>    bisection on [0, zMax].
> 2. *`n_in.getClusters(0)` is not the neutron's position.* The ZDC neutrals factory links every cluster of the
>    event to the neutron (`associateAllClustersToNeutron`), so the first linked cluster is often a photon's. The
>    neutron's reference point is where its momentum points.
>
> Measured on single-Λ guns (100–275 GeV, 16 000 events, truth-matched Λ in ±30 MeV): on top of 3063 the two
> changes raise the Λ yield in a paired test on identical events (Phase 3 B9d / B9e: B9e against R3 pooled z +3.76).

## U2 — FarForwardNeutralsReconstruction: the photon pair chosen by the Λ hypothesis

Draft description:

> The ZDC photon box tags 5–9 clusters per Λ event at 100–275 GeV, most of them neutron fragments. Each becomes a
> photon, and their energy is missing from the neutron. This PR adds an option (`lambdaPairingHcalZDC`) to keep
> only the pair of tagged clusters that best fits Λ → n π⁰ → n γγ. The neutron of each hypothesis holds every other
> cluster, so the right pair also gets the right neutron energy.
>
> For each pair: the decay depth from the γγ opening angle (π⁰ constraint) along the momentum-weighted slope, as in
> LambdaReconstruction; the score is the fitted π⁰ and Λ mass χ², plus the Λ decay-depth density (cτ = 78.9 mm),
> plus the photons' depth in the ZDC (true photons shower earlier than neutron fragments that pass the box).
> Energies are never rescaled; the Λ mass only ranks a discrete choice.
>
> Also: `gammaZMaxOffset` is added to `HcalFarForwardZDC_SiPMonTile_r_pos`, which is the ZDC **centre** (front
> face 3580.0 cm + half of 183.27 cm), not its face, so the stock 400 mm sits 1316 mm past the face and cuts
> nothing. The default becomes −691.4 mm: photon candidates start within 225 mm of the face. Optionally the
> neutron sits at the energy centroid of its clusters (`neutronPositionCentroid`), better for a fragmented shower.

The depth-limit convention is the smallest independent fix in the set and could also go upstream on its own, as a
bug report with the one-line default change. It was measured only on top of the pairing (X5 against X4, z +29.85);
on the stock chain it is untested.

## U3 — ImagingTopoCluster: photon-core split (default off)

Draft description:

> A photon that lands within a few cells of the neutron in the ZDC merges into the neutron's topological cluster.
> Photons shower in the first layers, neutrons deep. With `coreSplitSeedEdep` > 0, each saved group is split
> between its shallow energy cores (local maxima ≥ seed in layers ≤ `coreSplitMaxLayer`, the more energetic of two
> closer than `coreSplitMinDistXY`) and one shared region seeded by every deeper maximum. Hits join the region of
> their most energetic neighbour, in decreasing energy; optionally a core keeps only its first
> `coreSplitCoreMaxLayer` layers. A group with no core, or one core and nothing deeper, stays whole. The
> protoclusters still go through the stock CoG step, so their associations are unchanged code.
>
> Default off (`coreSplitSeedEdep = 0`): BEMC and FHCAL clustering is unchanged. This is argued from the code, not
> measured — Phase 4 ran no comparison of the other detectors' collections.

**What changes for users of `HcalFarForwardZDCClusters`:** with U3 and U4, a ZDC cluster is no longer one shower.
On D4 at 275 GeV the photons' best clusters are purer (purity ≥ 0.8: 0.46 → 0.69 of photons, X5 → X9), but hold less
of the photon's energy (containment ≥ 0.5: 0.49 → 0.27), and the neutron's best cluster holds less of the neutron
(median containment 0.33 → 0.28; `space/perf/cluster-containment-phase4.json`). The truth-matched separation S0all (purity ≥ 0.8 and containment ≥ 0.5) falls
from 0.270 % to 0.057 % per thrown (mean; `headline.csv`). The Λ chain does not care, because the neutrals factory
sums the neutron's clusters and the photon calibration is refit for 5-layer cores, but a benchmark that reads the
clusters directly (for example the `zdc_photon` and `zdc_pi0` plots) sees fragments.

## U4 — the ZDC configuration that turns it on

`ZDC.cc`: `neighbourLayersRange` 3 → 1 (P1d), `minClusterEdep` 50 → 20 MeV, the core split at 5 MeV / layer 4 /
50 mm / 5 layers. `reco.cc`: photon law {3.952, 0.938}, neutron law {6.214, 0.740} (refit on the D2 / D3 guns for this
clustering, `scripts/420`), the depth limit −691.4 mm, `neutronPositionCentroid = true`. The calibration belongs to
the clustering: any change to U3's parameters needs the refit again.

## Before any of these is a pull request (checklist of `eicrecon-pr`)

- **Formatting.** 40 added lines of the four U patches exceed the 100-column limit (U1 7, U2 22, U3 9, U4 2);
  `clang-format` 23.1.4 with EICrecon's
  `.clang-format` warns on 6 of the 11 files (31 warnings, most in U2). `pre-commit` is not installed here.
- **Use what exists.** U2 hand-rolls vector math (`V3`, `sub`, `norm`, `unit`, `angle`) and repeats
  LambdaReconstruction's vertex bisection: factor the fit into one shared helper and use `edm4hep::utils`.
- **Units and constants.** `gammaZMaxOffset`, `lambdaCTau` (mm), `lambdaPairingLambdaSigma` (GeV) carry no unit
  tags; the 100 mm photon-depth scale, the 1e-12 guard and the 35800 mm fallback are magic numbers.
- **Defaults.** `lambdaPairingHcalZDC = true` in the Config struct changes behaviour for every user of the struct;
  default it to false and switch it on in `reco.cc`.
- **Tests.** Catch2 tests for `core_split_group` and `chooseLambdaPhotonPair` (none written).
- **Cost.** `core_split_group` builds an O(n²) neighbour list per group, and the pairing fits every pair of tagged
  clusters. Wall time on D4 at 275 GeV rose from 73 s (X5) to 85 s (X9) per 1000 events, in 1-core containers
  under another project's load: not a benchmark, so measure before posting.
- **Leftovers from PR 3063** in `LambdaReconstruction.cc` ("start of temporary reconstruction" comments, two
  temporary collections per triplet) belong to that PR's review.
- **Physics caveat.** On MSF 9x275 events the chain finds 96 ± 4 % of the Λ in the acceptance, but writes 360
  candidates per 1000 events, most of them not Λ (`space/perf/msf-CP2_X9_S5-D6a_9x275.json`). A candidate-quality
  cut belongs with any PR that claims a physics gain.
