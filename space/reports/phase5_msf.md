# Phase 5 — Λ → nπ⁰ on MSF events

Loop: `zdc-autoresearch-loop-v5.md` (D-user-39, started 2026-11-08T22:29Z). Deck: `slides/phase5/`.

## Summary

**Closed 2026-11-09T03:22Z (D-user-41).** After checkpoint 2 (2026-11-09T03:06Z). Nine tries since Step 0, seven accepted (Y2, Y4–Y9), one inconclusive (Y1, kept as Y4),
one rejected (Y10, no effect), none foul. The current best Y9 runs the X9 code plus three patches (Y2 the vertex with each
daughter's lever arm, Y5 a ZDC pairing that may take one photon from B0, Y9 one that may take both) and four parameters (B0
island splitting with a 0.3-crystal sharing profile, the B0 photon law fitted on the B0 photon gun D2b).

| Λ → nπ⁰ found, per expected (yield) | X9 (start) | Y9 | reachable |
|---|---|---|---|
| 9x275, search half | 943 (13.17 %) | 1267 (17.70 %) | 43.6 % |
| 9x275, held-out half | 897 (12.53 %) | 1206 (16.84 %) | 43.6 % |
| 9x130, search half | 66 (0.92 %) | 219 (3.06 %) | 8.0 % |
| 9x130, held-out half | 63 (0.88 %) | 205 (2.86 %) | 8.0 % |
| purity (pooled): search / held out | 19.8 % / 19.0 % | 26.7 % / 25.8 % | |

Search halves +47 %, held-out halves +47 % (z +19.65); the D4 Λ gun is unchanged (S4a_tm 7.44 % mean, 14.12 % at 275 GeV;
X9 7.436 / 14.101; every Phase 5 try on D4 gives 7.436–7.439 % / 14.101–14.117 %, D4P5_*). The gain is in the B0 regimes: one photon in B0 (9x275 193 → 395 found) and both in B0 (0 → 123); the all-ZDC
regime stays at 750, its photons limited by the ZDC clustering.

## The score

Per beam energy, from `210` (`space/perf/msf-regimes-<row>-<dataset>.json`):

- N_expected = 0.358 × generated Λ (one per MSF event): 7 160 per search half.
- N_found: events whose true Λ decayed to n π⁰ in which a `ReconstructedLambdas` entry lies within ±30 MeV of
  m_Λ and holds a ZDC neutron neutral with a cluster of purity ≥ 0.8 for the true neutron and two photon neutrals
  with clusters of purity ≥ 0.8 for the two true photons.
- N_window: events with a `ReconstructedLambdas` entry inside the window, right or wrong.
- Yield = N_found / N_expected; purity = N_found / N_window.

Selector (`463`): N_found pooled over D6s_9x275 and D6s_9x130, paired on identical Λ against the current best,
z = (c − b) / √(b + c) ≥ 3 to accept; the pooled purity may not fall by more than 2σ. D6h is held out for the
checkpoints.

## Step 0 record

| # | item | outcome |
|---|---|---|
| 1 | D6s / D6h registered | 2026-11-08T22:34Z: four datasets of 40 files × 500 events (D6c files 0001–0040 and 0041–0080), manifest sections written, FROZEN exceptions removed. |
| 2 | `210` purity, `463` | `210` on MSF11_X9 / D6c_9x275 reproduces N_found 1840 and the per-Λ results exactly, N_window 8749 (purity 21.0 %). `463` written. |
| 3 | base row MSF5_X9 | X9 on D6s + D6h with the MSF template (22:35Z–23:02Z, integrity clean). On files 0001–0040 it reproduces MSF11_X9 Λ by Λ: N_found 943 (9x275) and 66 (9x130), score 1009; purity 21.5 % and 9.4 %. `460` PASS on its MSF outputs, F2b against R0 on MSF (CTL5_R0_msf: ZDC and B0 raw hits identical). R0 itself finds 3 of 7160 (0.04 %). |
| 4 | ruler controls | `463`: the purity control (N_window × 1.3) → REJECTED (purity), z_P −6.42; the base row against itself → REJECTED (z 0). Truth misaligned by one file (CTL5_swap): `210` stops with MISMATCH, `460` FAILS F2b. `465`: PASS on Y2's patch, FAIL on a copy with one MCParticles line. `463` X9 over X1 (CTL5_X1_msf: N_found 285 + 5, purity 6.7 %) → ACCEPTED, z +24.22, z_P +19.32; X1 over X9 → REJECTED (purity), z −24.22. |
| 5 | FROZEN | 2026-11-08T23:26Z: loop v5, `210`, `463`, `464`, `465` frozen; the hook refuses an edit to `210` (tried once). |
| 6 | report, deck | this file; `slides/phase5/build_phase5_slides.py` (4 slides at Step 0, 22 at the close; rendered and checked). |

Step 0 closed 2026-11-08T23:26Z.

## Tries

| try | change | 9x275 N_found | 9x130 N_found | b / c, z | purity | z_P | fair play | verdict |
|---|---|---|---|---|---|---|---|---|
| Y1_b0_split | B0 islands split at local maxima (parameters) | 943 → 944 | 66 → 71 | 9 / 15, +1.22 | 19.8 → 19.0 % | -1.01 | PASS | INCONCLUSIVE |
| Y2_vertex_lever_arm | Λ vertex with each daughter's lever arm (code) | 943 → 953 | 66 → 83 | 7 / 34, +4.22 | 19.8 → 20.4 % | +0.71 | PASS | ACCEPTED |
| Y4_b0_split_on_y2 | Y1's B0 splitting on top of Y2 (parameters) | 953 → 975 | 83 → 123 | 8 / 70, +7.02 | 20.4 → 20.0 % | -0.50 | PASS | ACCEPTED |
| Y5_mixed_pairing | ZDC pairing with a B0 photon hypothesis (code) | 975 → 1164 | 123 → 147 | 22 / 235, +13.29 | 20.0 → 23.8 % | +4.84 | PASS | ACCEPTED |
| Y6_b0_profile | B0 split sharing scale 1.0 → 0.5 crystal (parameter) | 1164 → 1209 | 147 → 182 | 9 / 89, +8.08 | 23.8 → 24.7 % | +1.17 | PASS | ACCEPTED |
| Y7_b0_photon_law | B0 photon law fitted on the B0 gun (parameter) | 1209 → 1238 | 182 → 190 | 31 / 68, +3.72 | 24.7 → 25.1 % | +0.38 | PASS | ACCEPTED |
| Y8_b0_profile_03 | B0 split sharing 0.5 → 0.3 crystal (parameter) | 1238 → 1252 | 190 → 194 | 5 / 23, +3.40 | 25.1 → 25.3 % | +0.28 | PASS | ACCEPTED |
| Y9_external_pair | ZDC pairing with a B0-pair hypothesis (code) | 1252 → 1267 | 194 → 219 | 10 / 50, +5.16 | 25.3 → 26.7 % | +1.76 | PASS | ACCEPTED |
| Y10_lambda_mass_rank | Λ-mass term 0.1 → 0.036 in the final choice (parameter) | 1267 → 1267 | 219 → 219 | 0 / 0, +0.00 | 26.7 → 26.7 % | -0.02 | PASS | REJECTED (no effect) |

## Checkpoints

### Checkpoint 1 (2026-11-09T01:21Z, after Y1, Y2, Y4, Y5, Y6)

F5 on the held-out halves D6h (files 0041–0080), the current best Y6 against the previous checkpoint's best, the base row MSF5_X9 (`463 --split h`):

| held-out half | MSF5_X9 | Y6_b0_profile | reachable |
|---|---|---|---|
| 9x275 N_found (yield) | 897 (12.53 %) | 1151 (16.08 %) | 43.6 % |
| 9x130 N_found (yield) | 63 (0.88 %) | 165 (2.30 %) | 8.0 % |
| purity (pooled) | 19.0 % | 23.8 % | |

Pooled b 30, c 386, z +17.45; z_P +6.06 → **REPRODUCES**. The search halves moved 1009 → 1391 (+38 %), the held-out halves 960 → 1316 (+37 %): no overfit; Y2, Y4, Y5 and Y6 stand. D4 Λ gun (CP5_1_Y6_D4, Phase 4's slim template, `410` / `441`): S4a_tm per thrown Λ → nπ⁰ 7.44 % mean, 14.12 % at 275 GeV (X9 7.436 / 14.101): unchanged — the Phase 5 steps act on the B0 regimes, which the gun barely reaches.

### Checkpoint 2 (2026-11-09T03:06Z, after Y7, Y8, Y9, Y10)

F5: the current best Y9 against checkpoint 1's best Y6 on D6h (`463 --split h`):

| held-out half | Y6_b0_profile | Y9_external_pair |
|---|---|---|
| 9x275 N_found (yield) | 1151 (16.08 %) | 1206 (16.84 %) |
| 9x130 N_found (yield) | 165 (2.30 %) | 205 (2.86 %) |
| purity (pooled) | 23.8 % | 25.8 % |

Pooled b 28, c 123, z +7.73; z_P +2.48 → **REPRODUCES** (search halves 1391 → 1486, held out
1316 → 1411: the same +95). Against the base row on D6h: 960 → 1411, z +19.65. D4 (CP5_2_Y9_D4): S4a_tm 7.44 % mean, 14.12 %
at 275 GeV, unchanged. Y7, Y8 and Y9 stand.

## Open questions

- Q19 answered (D-user-40): the B0 photon gun D2b was added; the try is Y7 (ACCEPTED).

## Final state and upstream pieces

- EICrecon working tree = a15b0db6 (Phase 4's X9 accept commit on `zdc-autoresearch/phase4`) + three uncommitted patches, in order:
  `Y2_vertex_lever_arm.patch` (LambdaReconstruction, 33 added lines), `Y5_mixed_pairing.patch` and `Y9_external_pair.patch`
  (FarForwardNeutralsReconstruction, its config, factory and reco.cc; switches lambdaPairingMixed and lambdaPairingExternalPair,
  default false, true in reco.cc). `phase5_cumulative.patch` is their sum; applied in order to a15b0db6 they reproduce the tree.
- Parameters of Y9 (run-time): `B0ECAL:B0ECalIslandProtoClusters:splitCluster 1`, `transverseEnergyProfileMetric
  dimScaledLocalDistXY`, `transverseEnergyProfileScale 0.3`; `reco:ReconstructedFarForwardNeutrals:gammaScaleCorrCoeffB0Ecal
  1.0888,1.0058` (467 on the B0 photon gun D2b).
- Upstream candidates: U5 = Y2 (the vertex for daughters at different depths; a bug fix for any B0 photon), U6 = Y5 + Y9 (the
  pairing across ZDC and B0), U7 = the B0 splitting and the gun-fitted B0 photon law. Before a PR: a guard on the B0 collections
  (they change), clang-format, Catch2 tests, and the three switches' defaults reviewed.

## Process record

- 2026-11-08: two hand-typed timestamps were wrong and were corrected from file times; one test JSON was removed with
  `rm -f` instead of moved (D-user-32); a wait loop matched its own command line and was stopped.
- 2026-11-09T00:51Z: `110 --only D2b_photon_B0` rewrote the manifest's `guns` section with that gun alone (`121 write`
  replaces a section), dropping the D1–D4 gun entries. `110` now lists every configured gun on disk; the section was
  rewritten from the files (88 entries). The hashes are recomputed, so the check against the original entries is the
  user's diff of `space/perf/manifest-datasets.json`. The fix was seen to hold at 2026-11-09T04:21Z: generating D2c with `--only` left the
  88 earlier entries unchanged and added 6.
- The auto-mode classifier refused an agent-opened FROZEN exception for the B0 gun; the user approved it (Q19, D-user-40).
- 2026-11-09T03:57Z: the close records counted ten tries in the ledger and the deck; nine ran (Y1, Y2, Y4–Y10; Y3 parked). Corrected.

## Next run recommendations

(written 2026-11-09T03:06Z, after checkpoint 2; per expected Λ → nπ⁰ on the 9x275 search half unless noted)

The cheap levers are spent: the last parameter try changed nothing (Y10), and three more ideas were closed by measurement
(a B0 split peak threshold, a crystal-energy pairing term, a retune of the mixed and B0-pair depth terms). What is left needs
new methods, ranked by the Λ at stake:

1. **ZDC photon finding in the all-ZDC regime** (photon missing 1125 of 2003 Λ, 15.7 %). Of the missing photons 31 % sit in a
   cluster the neutron dominates, 26 % in no Hcal cluster at all (they shower in the LYSO crystal section: missed photons carry a
   median 39 % of their deposit there; the crystal readout clips at 2 GeV per crystal, so it locates photons better than it
   measures them), 27 % share a cluster with the other photon. A crystal-seeded photon finder (crystal clustering fixed: today one
   island per event) with the Hcal energy behind it is the largest lever; it needs the crystal raw hits in F2's reference.
2. **The ZDC photon with one photon in B0** (303 of 803 Λ missing a photon, mostly the ZDC one; 148 of them have a pure tagged
   ZDC cluster that another hypothesis outscored): a photon-likeness term beyond depth, or the crystal seed of item 1.
3. **Two photons in B0 closer than ~2 crystals** (82 + 64 Λ, 9x275 + 9x130, photon missing; merged pairs lie a median 2.5
   crystals apart): a two-photon shower fit in place of the island split.
4. **9x130 is acceptance-bound**: the neutron lands in B0 for 30 % of expected and is lost for 23 %. Scoring B0 neutrons is a
   ruler change (210 requires a ZDC neutron) and the B0 ECal is an EM calorimeter: a question for the user, not a try.
5. **Upstream**: Y2 (the vertex, 33 lines), Y5 + Y9 (the mixed and B0-pair pairing, behind switches off by default) and the B0
   parameters (splitting, 0.3-crystal profile, the gun-fitted photon law) are the Phase 5 pieces; the D2b gun and 467 document the
   law. Before any PR: a guard on non-ZDC collections (B0 clusters change), clang-format, Catch2 tests for the vertex and pairing.
6. **Purity**: the sample is 26 % pure on the search halves. A purity-led selector (candidate quality: fitted π⁰ mass, decay
   depth) would be a new phase's ruler, the user's choice.
