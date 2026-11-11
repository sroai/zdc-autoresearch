# Leave-one-out ranking — what each Phase 4–6 change is worth

(2026-11-09 evening ET, after the Phase 6 close. D-user-46: a colleague asked which changes are practical in EICrecon and give the
best results, so that a few high-priority pull requests can be chosen. Loop v7 is unchanged until the user decides.)

## Summary

Seventeen reconstructions of the MSF search halves, each switching one change off, paired Λ by Λ against its base
(run 2026-11-09 16:49 EST – 22:02 EST, every output clean).

- **Without any ZDC Hcal clustering change, the rest of the work keeps half of Z8's yield, at higher purity and the
  same −t resolution.** Stock ZDC clustering plus everything else (AB9): 954 Λ → nπ⁰ found, purity 49 %, −t σ68
  0.115 / 0.124 GeV². Z8 (split clusters): 1946, 31 %, 0.114 / 0.118. Stock EICrecon: 3.
- **The core split (the colleague's "over-fragmenting") is worth +374 Λ on Z8, but only 17 % of the candidates it adds
  are true Λ, and it fragments the clusters for every user.** Drop it (units P2 and P8's split part).
- **On stock clustering the Λ pairing works only through the crystal photons.** The pairing family is worth +553;
  without the crystal photons the pairing adds nothing (+4) and about 200 wrong candidates. The B0+ZDC pairing Y5, the
  change the colleague liked, is worth +252 inside that, because its ZDC photon is mostly a crystal photon.
- **The B0 island split and B0 photon law are worth +222 to +257 on every base.** They alone make the both-photons-in-B0
  regime, which is most of the 9x130 yield.
- **LambdaReconstruction (the open PR 3063 plus the stable vertex P3) with stock clustering, stock B0 and no pairing
  finds 179 Λ at 90 % purity and the best −t (0.099 / 0.087 GeV²).** Measured as AB16, which also carries the
  calibration refit (worth about 20); PR 3063 and P3 are not separated.
- **The photon depth limit (X5) and the calibration refit are worth −2 and +21 on stock clusters.** Correct fixes,
  but not reasons for a pull request by themselves.
- **Proposed high-priority pull requests:** 1) LambdaReconstruction (PR 3063 + P3); 2) the B0 split and law (P7);
  3) the crystal package (P6 + P5 + the pairing core with Y5). Section Proposed high-priority pull requests has the
  details and the rest.

## How it was measured

- **Two base rows**, both on the MSF search halves D6s (9x275 and 9x130, the Phase 5 and 6 score):
  - **Z8_hcal_axis_law**, the Phase 6 final row, with split ZDC Hcal clusters: 1946 Λ → nπ⁰ found (9x275 1688,
    9x130 258), purity 30.9 %, −t σ68 0.114 / 0.118 GeV².
  - **AB9_stock_clustering**: Z8 with the stock ZDC Hcal clustering of the EICrecon pin (XY distances 0.75 × cell side,
    seed 25 MeV, cluster floor 50 MeV, ≥ 10 hits, no core split; checked against the pin's `ZDC.cc`), the photon shape
    box of the merged PR 3114 (length 110 mm, width 22 mm) and the calibration fitted on stock clusters in Phase 1 (R0:
    photon 1.7582·E^0.9198, neutron 2.0790·E^0.9109). Everything else as Z8. 954 found (747 / 207), purity 49.3 %,
    −t σ68 0.115 / 0.124 GeV².
  - For scale: stock EICrecon with PR 3114 finds 3.
- **One row per change**: the base with that change switched off by its run-time parameters (AB9 alone needed a build:
  the XY distances are not parameters). Same events, same scorer (`210`, ±30 MeV window, truth matching), each Λ paired
  between base and row (`463`).
- **Worth** = Λ found by the base − Λ found by the row. Positive means the change helps. "Found only with it" and "only
  without it" are the paired counts.
- **The worths do not add up.** Each is measured with all the other changes present, and the changes depend on each
  other. On Z8 the seven single worths sum to 2025, more than Z8's whole gain over stock (1943). On AB9 the three
  pairing-family worths (crystal photons 549, Y5 252, Y9 30) sum to 831 against the family's whole worth of 553,
  because Y5's worth sits inside the crystal photons' worth.
- **Checks**: every row has 80 / 80 clean outputs (`300` integrity). The switches of AB1–AB15 were first seen to
  change the output on one file (`TAB_*` proofs, runlog 2026-11-09T21:52Z and 23:11Z = 16:52 and 18:11 EST); those of AB16 and AB17 by
  their paired differences on the full run (225 / 3 and 32 / 11).
- Scripts: `485` runs a list of rows, `486` ranks them, `476` gives −t. Results:
  `space/perf/leave-one-out-Z8_hcal_axis_law.json`, `space/perf/leave-one-out-AB9_stock_clustering.json`,
  `space/perf/leave-one-out-AB10_stock_clustering_no_pairing.json`, `space/perf/t-resolution-AB*.json`.

## Ranking on stock clustering (AB9 base)

The base a pull request series would start from. AB9: 954 found, purity 49.3 %, −t σ68 0.115 / 0.124 GeV².

1. **The ZDC Λ pairing family** (row AB10, `lambdaPairingHcalZDC` off; this also switches off the B0+ZDC pairing Y5,
   the B0 pair Y9 and the crystal photons, which all run inside the pairing, checked in the code)
   - worth **+553 Λ** (−58 %); 559 found only with it, 6 only without it.
   - purity without it 61.2 %.
   - −t σ68 without it 0.103 / 0.104 GeV².
   - 9x275: both photons in the ZDC 302 → 53, one in B0 326 → 90, both in B0 119 → 121.
2. **The crystal-seeded photons and the axis law** (unit P5; row AB15: `lambdaPairingCrystal`,
   `crystalEnergyAlternative`, `crystalAltColumnOut`, `hcalAxisAlternative` off; the pairing stays on)
   - worth **+549** (−58 %); 555 only with them, 6 only without.
   - **This is the whole pairing gain.** Without the crystal photons the pairing finds 405, the same as no pairing
     (401), and adds about 200 wrong candidates (window 854 against 655).
   - 9x275: both photons in the ZDC 302 → 53, one in B0 326 → 90.
   - −t σ68 without them 0.105 / 0.105 GeV².
3. **The B0 ECal island split and the B0 photon law** (unit P7; row AB14, stock B0)
   - worth **+257** (−27 %); 274 only with it, 17 only without.
   - both photons in B0: 119 → 7 at 9x275, 123 → 14 at 9x130. At 9x130 that is most of the yield (207 → 93).
   - it costs purity: 57.7 % without it. It adds about 725 window candidates, 257 of them true Λ (35 %).
   - −t σ68 without it 0.112 / 0.123 GeV².
4. **The B0+ZDC pairing, Y5** (part of P4; row AB12, `lambdaPairingMixed` off)
   - worth **+252** (−26 %); 259 only with it, 7 only without.
   - purity unchanged (48.9 % without it).
   - one photon in B0: 326 → 126 at 9x275, 61 → 18 at 9x130.
   - −t σ68 of the Λ with a B0 photon at 9x275: 0.180 GeV² without it, 0.127 with it.
   - Its ZDC photon is a crystal photon in most of these Λ: Y5's worth is part of the crystal photons' worth above.
5. **The B0 photon pair, Y9** (part of P4; row AB13, `lambdaPairingExternalPair` off)
   - worth **+30** (−3 %); 36 only with it, 6 only without.
   - purity 51.8 % without it; −t σ68 of the Λ with B0 photons 0.146 GeV² without it, 0.127 with it.
6. **The photon depth limit from the ZDC face** (unit P1, X5; row AB11, `gammaZMaxOffset` back to the stock 400 mm)
   - worth **−2**; 0 only with it, 2 only without. Window 1934 against 1937, purity unchanged.
   - On stock clusters with the PR 3114 shape box it changes nothing measurable.

## Ranking on Z8 (split clusters)

The Phase 6 final row. "Without it" numbers are the row's; Z8 has purity 30.9 % and −t σ68 0.114 / 0.118 GeV².

1. **The ZDC Λ pairing family** (row AB2, as AB10 above)
   - worth **+716 Λ** (−37 %); 798 found only with it, 82 only without it.
   - purity without it 22.2 %: on split clusters the pairing also removes wrong candidates.
   - −t σ68 without it 0.134 / 0.130 GeV².
   - every regime loses (9x275): both photons in the ZDC 1077 → 667, one in B0 488 → 319, both in B0 121 → 82.
2. **The Hcal photon-core split** (unit P2 and its refit in P8; row AB7: no split, cluster floor 50 MeV, X5's
   calibration: photon 3.9015·E^0.8757, neutron 8.0639·E^0.6999)
   - worth **+374** (−19 %); 454 only with it, 80 only without.
   - purity without it 37.9 %: it adds about 2150 candidates to the window, about 374 of them true Λ (17 %).
   - −t σ68 without it 0.128 / 0.159 GeV².
   - It fragments the clusters (Phase 4, `410`, 275 GeV gun, X5 → X9): photons whose best cluster holds at least half
     their energy 49 % → 27 %; the neutron's best cluster holds a median 28 % of its energy; S0all 0.270 % → 0.057 %.
     Every other user of `HcalFarForwardZDCClusters` sees the fragments.
3. **The crystal-seeded photons and the axis law** (row AB6, as AB15 above)
   - worth **+325** (−17 %); 454 only with them, 129 only without.
   - purity without them 27.8 %; −t σ68 0.122 / 0.131 GeV², bias −0.029 GeV² at 9x275 (Z8 −0.007).
   - both photons in the ZDC: 1077 → 845 at 9x275. On split clusters the Hcal supplies most photons by itself.
4. **The B0+ZDC pairing, Y5** (row AB3)
   - worth **+315** (−16 %); 351 only with it, 36 only without.
   - purity without it 25.6 %.
   - one photon in B0: 488 → 274 at 9x275, 77 → 31 at 9x130.
   - −t σ68 of the Λ with a B0 photon at 9x275: 0.217 GeV² without it, 0.127 with it.
5. **The B0 ECal island split and the B0 photon law** (row AB5)
   - worth **+238** (−12 %); 271 only with it, 33 only without.
   - both photons in B0: 121 → 7 at 9x275, 130 → 16 at 9x130.
   - purity 30.1 % without it; −t unchanged at 9x275.
6. **The B0 photon pair, Y9** (row AB4)
   - worth **+40** (−2 %); 49 only with it, 9 only without.
7. **The photon depth limit** (row AB1)
   - worth **+17** (−1 %, z +2.3); 35 only with it, 18 only without.
   - purity without it 19.7 %: the window holds 9803 candidates without it, 6296 with it. On split clusters with the
     150 × 12 mm shape box it removes about 3500 wrong candidates.
   - In Phase 4 (gun, X5 over X4) it gave +33 % yield; the later pairing photon depth term (X9) probably took over that
     part.
   - It acts only on the photon shape cut (`isGamma`); the vertex range uses the ZDC position, not this offset (checked
     in the code).

## The pairing without the split

The open question of the colleague's note: Y5 and the pairing were measured only on split clusters.

- **On X5's clusters (no split)**: 1572 found with the pairing family, 987 without (AB7, AB8): worth **+585** (+59 %).
- **On stock clusters**: 954 with, 401 without (AB9, AB10): worth **+553** (+138 %).
- **On stock clusters all of it comes through the crystal photons** (AB15). The pairing on stock Hcal clusters alone
  adds nothing; the crystal section supplies the photons that the stock Hcal clusters merge away. Y5 is worth +252
  there because its ZDC photon is mostly a crystal photon.
- Who supplies the two ZDC photons of each truth-matched all-ZDC Λ at 9x275 (cluster links):
  - AB9 (stock clusters), 302 Λ: two crystal-only photons 168, one crystal-only and one Hcal 80, two Hcal-only 52.
    Photons: crystal only 417, Hcal only 163, Hcal + crystal 22.
  - Z8 (split clusters), 1077 Λ: two Hcal-only photons 531, an Hcal photon with crystal energy in 381, a crystal-only
    photon in 210. Photons: Hcal only 1492, Hcal + crystal 444, crystal only 214.
- −t σ68 (9x275 / 9x130): AB10 0.103 / 0.104, AB9 0.115 / 0.124, AB8 0.152 / 0.190, AB7 0.128 / 0.159, Z8 0.114 / 0.118.
  Stock clusters measure −t as well as Z8.

## The cheap set (AB10 base)

AB10: stock ZDC clustering, the PR 3114 box, the R0 calibration, the pairing family off: 401 Λ (264 / 137), purity
61.2 %, −t σ68 0.103 / 0.104 GeV². Two rows split it (reference AB10, `space/perf/leave-one-out-AB10_stock_clustering_no_pairing.json`):

1. **The B0 island split and law** (row AB16, stock B0)
   - worth **+222** (−55 %); 225 only with it, 3 only without.
   - both photons in B0: 121 → 7 at 9x275, 120 → 14 at 9x130; the other regimes unchanged.
   - purity without it **89.9 %** (window 199 against 655). It adds about 456 window candidates, 222 of them true Λ
     (49 %).
   - −t σ68 without it 0.099 / 0.087 GeV².
2. **The calibration refit R0 against the pin's stock laws** (row AB17: photon 1.1·E^0.98, neutron 2.4·E^0.89)
   - worth **+21** (−5 %, z +3.2); 32 only with it, 11 only without.
   - purity 60.0 % without it; −t σ68 0.105 / 0.100 GeV².
   - The ±30 MeV window tolerates the stock laws; the refit matters little for the count.

**What is left in AB16 (179 Λ, purity 89.9 %, −t 0.099 / 0.087 GeV²)** is the code that differs from stock and stays
active with the pairing off and stock B0: the open PR 3063 (LambdaReconstruction without the IP-pointing π⁰
preselection, finding F4), P3 (the stable vertex and the neutron at its reference point, F9 and F10), the depth limit
(worth nothing here, AB11) and small changes in the neutrals factory (the neutron position from the cluster centroid).
PR 3064's changes are all overridden in these rows. Separating PR 3063 from P3 needs a build of each.

## Cost per change

Lines added to EICrecon by the patches (`space/notes/patches/`), and what each touches:

- **P1, depth limit (X5)**: one constant in `reco.cc` (patch +5 / −3).
- **P7, B0 split and law**: three B0 island parameters and the B0 photon law (run-time parameters in Phase 5); a few
  lines in `B0ECAL.cc` and `reco.cc`. Changes `B0ECalClusters` for every user (far_forward_dvcs benchmark).
- **P3, Λ vertex (U1 + Y2)**: U1 +30 / −25 and Y2 +33 in `LambdaReconstruction.cc`. No switch: on in every row, so not
  ranked here.
- **Calibration refit**: four constants in `reco.cc` for the clustering that is kept.
- **P4, the pairing**: X2 +165, X3 +8, X9 +9, Z7 +63 (isolation), Y5 +179, Y9 +123: about 550 lines in
  FarForwardNeutralsReconstruction. It overwrites the neutrals' particle IDs from a Λ hypothesis; reviewers may want the
  Λ combinatorics in LambdaReconstruction instead, which is a redesign.
- **P5, crystal photons**: Z1b's neutrals part (about 430), Z5 +156, Z6 +37, Z8 +91: about 710 lines, three new factory
  inputs, a dozen run-time parameters.
- **P6, LYSO clustering at the crystal scale**: Z1b's `ZDC.cc` part, 10 lines. Changes the `EcalFarForwardZDC*` clusters
  (zdc_lyso benchmark). On in every row, so not ranked; P5 needs it.
- **P2, core split**: X7 +145, X8 +57 in ImagingTopoCluster, which BEMC and LFHCAL also use.

## Caveats

- Search halves only: nothing here was confirmed on the held-out halves D6h.
- The pairing weights, the mass width and the isolation were tuned on split clusters and not re-tuned on stock
  clusters, so the stock-base worths of P4 and P5 are lower bounds.
- The calibrations are best-cluster fits on photon and neutron guns; the factory sums clusters for the neutron.
- P3 (Λ vertex), P6 (LYSO clustering) and the open PR 3063 that the tree carries are on in every row; their worth is
  inside the base rows and not measured separately. The open PR 3064 changes only settings, and every row replaces
  them with its own.
- Purity counts every candidate in the window; half of the wrong ones have no Λ → nπ⁰ at all (Phase 6 report, `483`).

## Proposed high-priority pull requests

Practical means: on stock ZDC Hcal clustering, a clear gain per line, few collections changed. Ordered by priority.

1. **LambdaReconstruction: the open PR 3063 plus P3 (stable vertex, neutron at its reference point)**
   - value: with stock clustering, stock B0, no pairing (and the refit calibration, worth about 20), 179 Λ at 90 %
     purity and the best −t (AB16). Without PR 3063 the stock
     IP-pointing π⁰ preselection caps every other gain (finding F4).
   - cost: one file, P3 adds about 60 lines to PR 3063; changes only `ReconstructedLambda*`.
   - form: P3 as a follow-up to PR 3063 (or a review suggestion on it), since PR 3063 exposes the vertex runaway (F9).
   - open: the split between PR 3063 and P3 is not measured.
2. **B0 ECal: islands split at local maxima, energy shared at 0.3 crystal, the B0 photon law refit (P7)**
   - value: +222 on the cheap set, +257 on AB9, +238 on Z8; the whole both-in-B0 regime, most of 9x130.
   - cost: three B0 island parameters and two law coefficients.
   - price: purity 90 → 61 % on the cheap set; `B0ECalClusters` change for every user, so it needs the far_forward_dvcs
     benchmark and the B0 owners.
3. **The crystal package: LYSO clustering at the crystal scale (P6), crystal-seeded photons (P5), the pairing core and
   Y5 (part of P4)**
   - value: +553 on stock clustering, all of it with the crystal photons in; Y5 +252 within it. A lower bound: its
     parameters were tuned on split clusters.
   - cost: P6 10 lines in `ZDC.cc`; P5 about 710 lines and three new factory inputs; the pairing core about 245 lines;
     Y5 179 lines; a dozen run-time parameters.
   - design: the pairing overwrites the neutrals' particle IDs from a Λ hypothesis inside FarForwardNeutralsReconstruction;
     reviewers may want the Λ combinatorics in LambdaReconstruction. The colleague's own description of Y5 ("2 gammas +
     1 unidentified ZDC cluster") fits that design.
   - form: P6 first (small, its own benchmark, zdc_lyso); then the crystal photons with the pairing as one pull request
     (the pairing alone gives nothing on stock clusters); Y5 inside it or right after.

**Lower priority**

- **Y9, the B0 photon pair**: +30 / +40, 123 lines; it improves −t of the Λ with B0 photons (0.146 → 0.127 GeV² on
  AB9). A follow-up to item 3.
- **P1, the photon depth limit**: a correct fix (the stock cut sits 1.3 m deep and never acts), worth nothing on stock
  clusters and purity only on split clusters. One constant: ride along with item 3.
- **The calibration refit**: +21 on stock clusters. Four constants: ride along with item 3, refit for whatever
  clustering is kept.
- **P2, the Hcal core split, and P8's split configuration**: drop. +374 on Z8 at a purity cost, and it fragments the
  clusters for every user.

**What it means for loop v7** (unchanged until you decide): P1 joins another unit; P2 and the split part of P8 drop out;
P3 goes with PR 3063; P4 and P5 become one unit on top of P6; P7 stays. Not tested here: the series on the held-out
halves D6h, and the crystal package re-tuned on stock clusters.
