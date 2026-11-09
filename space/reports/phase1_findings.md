# Phase 1 findings ledger

Append-only. Full entries; one line each in `FINDINGS.md`.

## F6 — the stock ZDC calibration coefficients do not fit the stock clusters (OPEN, measured 2026-11-05)
- Where: `src/global/reco/reco.cc` (`gammaScaleCorrCoeffHcalZDC` {1.1, 0.98}, `neutronScaleCorrCoeffHcalZDC` {2.4, 0.89}) and the form `a·E^b` of `FarForwardNeutralsReconstruction::corrPower`.
- Defect: the refit of `scripts/420_refit_calibration.py` on R0 (D2/D3 truth; peak of the raw best-cluster energy per gun energy) gives photon a = 1.758 ± 0.016, b = 0.920 ± 0.002 (χ²/ndf 65/6) and neutron a = 2.079, b = 0.911 (χ²/ndf 2.2/4). The stock photon law is 13–31 % low on R0 photon clusters (residual scale 0.69–0.87), the stock neutron law 3–9 % high. Pulls of the stock values from the refit: 20–40σ. The refit does not reproduce the stock coefficients: the program's Phase 1 calibration check fails, so the discrepancy is this finding.
- Second part: the a·E^b form itself misses the photon points on every 3×3 clustering (χ²/ndf 65–76 / 6; R0, P1a, P1b, P1f), the 20 GeV point most (Q10). On 1×1 column clusterings the neutron form misses (χ²/ndf 126–202 / 4).
- In practice: on R0 no photon is tagged above 70 GeV (F8), so the photon law never acts on stock; once PR 3114 tags photons it will.
- Evidence: `space/perf/calib-<exp>.json` for R0, R1, P1a–P1f.
- Severity: medium (energy scale of every ZDC photon and neutron). Owner: upstream PR with refit coefficients, per clustering, after Phase 2/3.

## F7 — the ZDC photon z cut sits 1.3 m behind the front face (OPEN, measured 2026-11-05)
- Where: `src/algorithms/reco/FarForwardNeutralsReconstruction.cc:21-27` (`m_gammaZMax = gammaZMaxOffset + constant(offsetPositionName)`), `src/global/reco/reco.cc:247,261` (`offsetPositionName = "HcalFarForwardZDC_SiPMonTile_r_pos"`, `gammaZMaxOffset = 400`).
- Defect: in epic 26.11, `HcalFarForwardZDC_SiPMonTile_r_pos` = front face + length/2 = 35800 + 916.4 = 36716.4 mm (`compact/far_forward/ZDC_SiPMonTile.xml:58-59`; length 1832.7 mm, evaluated with DD4hep). The cut is therefore z_cl < front + 1316 mm. The photon identification of S. J. Paul et al. (arXiv:2412.12346, section 3) cuts z_cl − z_front < 300 mm. A cut tuned against the front face is applied against the centre: on the former geometry the constant may have been the front.
- Evidence: the cluster-shape view of `scripts/430_shape_decayz.py` (space/plots/phase1/<exp>/shape_decayz/shape_D4_*.png, dashed lines) and the pass fractions in `space/perf/shape-<exp>.json` (cut sets `stock` vs `paper_z300`).
- Severity: low to medium (the z cut barely acts; neutrons interacting late are not excluded by it). Owner: issue to EICrecon (use `..._r_pos_front_face`, or set the offset to −616 mm).

## F8 — the stock photon cut box rejects every ZDC photon (OPEN; upstream fix proposed in eic/EICrecon#3114)
- Where: `src/algorithms/reco/FarForwardNeutralsReconstructionConfig.h` and `src/global/reco/reco.cc` (`gammaMaxLength = 100`, `gammaMaxWidth = 12` mm).
- Defect: on the square-tile ZDC the transverse √eigenvalues of photon clusters are 12–21 mm (R0, D4 175 GeV) and 2 of 3 above 12 mm fail; R0 tags 3 % of D2 photons (0 above 70 GeV) and 0.1–0.2 % of the truth-best photon clusters in Λ events (`shape-R0_stock.json`: D2 pass 0–9.5 % stock vs 88–99 % with PR 3114's 110 / 22 mm). Phase 0 observation O1; independently found and fixed by eic/EICrecon#3114 (B. Fraïsse, open 2026-11-05).
- But: in Λ events on stock clustering only 5–9 % of the truth-best photon clusters pass even PR 3114's box, because 87–98 % of the photon pairs are merged into one cluster with each other or the neutron (decay-position view, R0). The cut box is necessary, not sufficient.
- Severity: high for Λ (no Λ at all on stock). Owner: eic/EICrecon#3114; R2 measures it here.

## Status lines appended 2026-11-06
- F8 — FIXED upstream: eic/EICrecon#3114 merged 2026-11-05 21:08 UTC (backport #3117); R2 is the equivalent at the pin. The program's measurement: 0 Λ on stock clustering at every momentum (R2), +25 gained / 0 lost on P1b (L01, below 3σ): necessary, not sufficient, since 87–98 % of the photon pairs are merged on 3×3 clustering.
