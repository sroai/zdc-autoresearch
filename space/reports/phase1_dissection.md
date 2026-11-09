# Phase 1 report — dissection of PR 3064

Status: runs and verdicts done (2026-11-05); R2 (PR eic/EICrecon#3114) and the views added on the user's request
(D-user-15) — see the sections marked R2. Ledger: `space/EXPERIMENTS.md` (P1a–P1f, R2, backlog B1–B10).
Decisions this phase: D-user-12 (S3 raw-sum guard one-sided), D-user-13 (S2 judged after each clustering's
refit), D-user-14 (`LambdaReconstruction` open from Phase 2; family rules D-default-25), D-user-15 (views, R2),
D-user-16 (Q9: containment stays "not split", plus a one-sided photon raw-sum guard on D2), D-user-17 (Q10: S2
passes when |μ/E − 1| − 2σ ≤ 0.05). No question is open.

## Summary

- **H1, split into its parts.** The XY distance below the subcell pitch alone makes G1 and G2 (P1c: φ@180 and
  single-column 1.000 on NC and SIDIS; P1f, the PR without it: back to R0's 0.07 and 0). It gives about half of
  R1's photon-separation gain at 175 GeV (S0γ +0.168 of +0.334; 13 % at 100 GeV, 85 % at 275 GeV) and a third of
  its neutron loss (S0n −0.21 of −0.61). The threshold pair is not a bystander: on 1×1 columns it decides
  whether a soft photon has a cluster at all (P1e: putting R0's 25 MeV / 10-hit cut back costs S0γ −0.05 to
  −0.23), and at 3×3 it alone gives the best S0all of the program (P1b). The layer range 3 costs photon
  separation at 3×3 (P1a, gained 0 at every momentum) and is nearly neutral on columns (P1d). **H1 is confirmed
  for G1/G2 and refuted for the claim that the thresholds "only decide which shards survive".**
- **The PR's S0 balance** (S0all means over 100–275 GeV): P1b 0.048 > P1c 0.035 > P1f 0.029 > P1d 0.018 ≈ R0
  0.017 > R1 0.013. R1 gains photon separation (S0γ 0.057 → 0.368) and pays with the neutron (S0n 0.654 →
  0.044, raw neutron sum 0.56 → 0.38); its all-three separation is below stock. The PR's threshold change
  alone (P1b) beats stock at every momentum with zero events lost; adding the PR's distance to it costs about
  0.02–0.03 of S0all at 100–150 GeV.
- **P1b (R0 + 5 MeV seed / 2-hit size) is ACCEPTED by the rule** once Q9/Q10 were answered: every S0 component
  up or unchanged with lost 0 at every momentum (S0all 0.006 → 0.075 at 100 GeV), every guard in (S2 20 GeV
  0.9488 ± 0.0092 within 2σ; photon and neutron raw sums up; G1–G3 inside). Read in Phase 1, it changes no
  current best; it is the proposed start of Phase 2 after the held-out check.
- **Calibration refit proven on R0, and it does not reproduce stock** (F6): photons stock 13–31 % low (form χ²
  65/6), neutrons 3–9 % high. The PR's coefficients are off its own clustering's refit by 7σ (γ a) to 40σ (γ b).
- **Cut box and z cut.** The stock photon box rejects every ZDC photon (F8; PR 3114 fixes the box: R2). The
  photon z cut is measured from the ZDC centre, 1316 mm past the front face (F7; the paper uses 300 mm).
  On stock clustering 87–98 % of the Λ photon pairs are merged (decay-position view), so the box alone cannot
  make Λs: clustering and algorithm both matter.

## The six runs (D4 S0, mean over 100–275 GeV, and per momentum)

S0all
| exp | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | mean |
|---|---|---|---|---|---|---|---|---|---|
| R0_stock | 0.006 | 0.019 | 0.022 | 0.023 | 0.021 | 0.022 | 0.015 | 0.011 | 0.017 |
| P1a_R0_nlr3 | 0.005 | 0.012 | 0.014 | 0.014 | 0.013 | 0.012 | 0.009 | 0.006 | 0.010 |
| P1b_R0_thr | 0.075 | 0.075 | 0.057 | 0.051 | 0.042 | 0.039 | 0.032 | 0.018 | 0.048 |
| P1c_R0_dist | 0.005 | 0.014 | 0.031 | 0.037 | 0.043 | 0.056 | 0.050 | 0.047 | 0.035 |
| R1_pr3064 | 0.015 | 0.022 | 0.016 | 0.015 | 0.011 | 0.011 | 0.010 | 0.008 | 0.013 |
| P1d_R1_nlr1 | 0.025 | 0.026 | 0.018 | 0.020 | 0.017 | 0.012 | 0.016 | 0.015 | 0.018 |
| P1e_R1_thr | 0.008 | 0.017 | 0.040 | 0.047 | 0.055 | 0.055 | 0.048 | 0.042 | 0.039 |
| P1f_R1_dist | 0.050 | 0.046 | 0.033 | 0.028 | 0.024 | 0.022 | 0.019 | 0.011 | 0.029 |

S0g
| exp | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | mean |
|---|---|---|---|---|---|---|---|---|---|
| R0_stock | 0.056 | 0.067 | 0.070 | 0.065 | 0.060 | 0.057 | 0.043 | 0.036 | 0.057 |
| P1a_R0_nlr3 | 0.037 | 0.047 | 0.043 | 0.039 | 0.036 | 0.033 | 0.026 | 0.022 | 0.035 |
| P1b_R0_thr | 0.150 | 0.130 | 0.111 | 0.097 | 0.085 | 0.077 | 0.062 | 0.046 | 0.095 |
| P1c_R0_dist | 0.094 | 0.147 | 0.203 | 0.233 | 0.262 | 0.279 | 0.279 | 0.282 | 0.222 |
| R1_pr3064 | 0.343 | 0.363 | 0.395 | 0.399 | 0.395 | 0.373 | 0.352 | 0.326 | 0.368 |
| P1d_R1_nlr1 | 0.362 | 0.388 | 0.420 | 0.432 | 0.428 | 0.410 | 0.392 | 0.370 | 0.400 |
| P1e_R1_thr | 0.113 | 0.167 | 0.219 | 0.256 | 0.281 | 0.282 | 0.282 | 0.277 | 0.235 |
| P1f_R1_dist | 0.100 | 0.091 | 0.065 | 0.061 | 0.051 | 0.046 | 0.039 | 0.028 | 0.060 |

S0n
| exp | 100 | 125 | 150 | 175 | 200 | 225 | 250 | 275 | mean |
|---|---|---|---|---|---|---|---|---|---|
| R0_stock | 0.673 | 0.662 | 0.664 | 0.648 | 0.647 | 0.653 | 0.640 | 0.647 | 0.654 |
| P1a_R0_nlr3 | 0.667 | 0.666 | 0.661 | 0.645 | 0.649 | 0.655 | 0.636 | 0.652 | 0.654 |
| P1b_R0_thr | 0.696 | 0.668 | 0.666 | 0.648 | 0.648 | 0.653 | 0.640 | 0.647 | 0.658 |
| P1c_R0_dist | 0.656 | 0.583 | 0.514 | 0.436 | 0.407 | 0.342 | 0.291 | 0.253 | 0.435 |
| R1_pr3064 | 0.070 | 0.057 | 0.041 | 0.042 | 0.036 | 0.034 | 0.037 | 0.033 | 0.044 |
| P1d_R1_nlr1 | 0.097 | 0.070 | 0.051 | 0.049 | 0.041 | 0.039 | 0.044 | 0.044 | 0.054 |
| P1e_R1_thr | 0.645 | 0.565 | 0.503 | 0.430 | 0.391 | 0.326 | 0.273 | 0.234 | 0.421 |
| P1f_R1_dist | 0.687 | 0.671 | 0.661 | 0.645 | 0.650 | 0.655 | 0.636 | 0.652 | 0.657 |

| exp | S1a_truth_all | S2_gamma_tag_eff | S3_rawsum | S3_clusters_per_neutron | S4c_gammas_per_event | S4a_tm_eff | G1_phi_at_180_frac/q0 | G1_column_frac/q0 | G2_highE_frac/q0 | G2_highE_frac/q100 | G3_lowE_per_event/q0 | G3_lowE_per_event/q100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R0_stock | 0.186 | 0.0312 | 0.564 | 0.817 | 0.00213 | 0 | 0.0739 | 0 | 0.864 | 0.612 | 0.00955 | 0.006 |
| P1a_R0_nlr3 | 0.159 | 0.0312 | 0.582 | 0.809 | 0.00131 | 0 | 0.0719 | 0 | 0.887 | 0.636 | 0.00591 | 0.0035 |
| P1b_R0_thr | 0.225 | 0.0312 | 0.669 | 1.16 | 0.00819 | 0 | 0.068 | 0 | 0.686 | 0.467 | 0.182 | 0.11 |
| P1c_R0_dist | 0.552 | 0.538 | 0.243 | 2.49 | 0.932 | 0 | 1 | 1 | 0.0447 | 0.0176 | 0.215 | 0.129 |
| R1_pr3064 | 0.6 | 0.947 | 0.381 | 7.52 | 4.87 | 0.0181 | 1 | 1 | 0.0159 | 0.00611 | 5.44 | 2.13 |
| P1d_R1_nlr1 | 0.602 | 0.967 | 0.366 | 7.11 | 6.41 | 0.0167 | 1 | 1 | 0.0162 | 0.00631 | 5.04 | 2.02 |
| P1e_R1_thr | 0.594 | 0.931 | 0.247 | 2.5 | 2.08 | 0.00538 | 1 | 1 | 0.046 | 0.0174 | 0.22 | 0.138 |
| P1f_R1_dist | 0.194 | 0.034 | 0.689 | 1.08 | 0.00475 | 0 | 0.0675 | 0 | 0.757 | 0.51 | 0.111 | 0.079 |

Columns q0 / q100: D5 SIDIS (minQ2 = 0) / NC (minQ2 = 100). Limits: G1 φ@180 ≤ 0.15, columns ≤ 0.05, G2 drop
≤ 50 % vs R0 (0.864 / 0.612), G3 ≤ 0.5, S3 clusters per neutron +0.5, S4c ≤ 4.

| run | change | reference | verdict | why |
|---|---|---|---|---|
| P1a | R0 + nlr 3 | R0 | REJECTED | S0all −0.005 to −0.010 (125–275 GeV); S0γ only loses |
| P1b | R0 + 5 MeV / 2 hits | R0 | ACCEPTED (after D-user-16/17) | S0all +0.069 … +0.008 at every momentum, lost 0; every guard in |
| P1c | R0 + 1×1 distance (code) | R0 | REJECTED | S0n −0.08 to −0.39; G1, G2, raw sum (−57 %), clusters/neutron out |
| P1d | R1 − nlr (3 → 1) | R1 | REJECTED | all S0 up on R1, but G1–G3, S4c and raw sum (−5 %, 20/50 GeV) out |
| P1e | R1 − thresholds | R1 | REJECTED | S0γ −0.05 to −0.23; raw sum −24 … −81 % |
| P1f | R1 − distance | R1 (and R0) | REJECTED | vs R1 S0γ −0.24 … −0.34; vs R0 S0γ −0.011 / −0.009 at 225 / 275 GeV |

Gate G4 PASS for all six (static on D5; P1c also full G4 on 29 gun files: 9048 non-ZDC leaves identical).
Benchmarks: all four scripts produce PDFs on the 3×3 clusterings; P1a's π⁰ benchmark has no 2-cluster event at
130 GeV (EMPTY, not a crash); on the column clusterings (P1d, P1e) the π⁰ and/or photon benchmark crash as on
R1 (O4) — not a verdict ground.

## Calibration refit per clustering (`scripts/420_refit_calibration.py`, D2/D3 truth, peak of E_raw)

| run | γ a | γ b | γ χ²/ndf | n a | n b | n χ²/ndf |
|---|---|---|---|---|---|---|
| R0_stock | 1.758 ± 0.016 | 0.920 ± 0.002 | 65.0/6 | 2.079 | 0.911 | 2.2/4 |
| P1a_R0_nlr3 | 1.778 ± 0.016 | 0.917 ± 0.002 | 66.1/6 | 1.949 | 0.920 | 4.0/4 |
| P1b_R0_thr | 1.765 ± 0.016 | 0.919 ± 0.002 | 67.3/6 | 2.221 | 0.897 | 97.1/4 |
| P1c_R0_dist | 3.609 ± 0.125 | 0.892 ± 0.009 | 4.9/6 | 9.214 | 0.720 | 197.3/4 |
| R1_pr3064 | 4.053 ± 0.173 | 0.867 ± 0.010 | 8.8/6 | 7.974 | 0.696 | 202.3/4 |
| P1d_R1_nlr1 | 3.901 ± 0.154 | 0.876 ± 0.010 | 4.4/6 | 8.064 | 0.700 | 126.4/4 |
| P1e_R1_thr | 3.869 ± 0.158 | 0.876 ± 0.010 | 2.7/6 | 10.234 | 0.697 | 185.1/4 |
| P1f_R1_dist | 1.768 ± 0.016 | 0.918 ± 0.002 | 76.1/6 | 2.132 | 0.901 | 122.5/4 |

Stock: γ (1.1, 0.98), n (2.4, 0.89); PR 3064: γ (2.7, 1.27), n (16.65, 0.66). The proof on R0: the refit does not
reproduce stock (pulls 20–40σ) → finding F6. The two families are clean: every 3×3 clustering refits to
γ ≈ (1.76–1.78, 0.92), every 1×1 to γ ≈ (3.6–4.1, 0.87–0.89). The photon form misses on 3×3 (χ² 65–76 / 6, the
20 GeV point), the neutron form on 1×1 (χ² 126–202 / 4) and once low-energy neutrons are kept (P1b 97/4,
P1f 122/4: the 20 GeV point at 0.93). On R1's own clusters the PR's photon law is 7.4σ (a) / 40σ (b) from the
refit and its residual scale runs 1.29 → 4.44 over 20–275 GeV; its neutron law 1.54–1.92 (the Phase 0 numbers).

## Decay-position and cluster-shape views (D-user-15, `scripts/430_shape_decayz.py`)

Two views per run and D4 momentum, plots in `space/plots/phase1/<run>/shape_decayz/`, numbers in
`space/perf/shape-<run>.json`.

**Decay-position view** (`decayz_D4_<p>GeV.png`). Left axis, stacked per 1 m of true Λ decay z: both photons
separated / a photon *split* (its best cluster is pure but holds < 50 % of its clustered energy) / a photon
*merged* (its best cluster is shared, purity < 0.8) / a photon without any cluster. Right axis, its own scale:
cumulative curves normalised to the D4 events (nπ⁰ decays before the ZDC with all daughters in acceptance =
100 %, no branching ratio): all events, neutron separated, all three separated, Λ reconstructed (truth-matched).
The two axes are independent; the right one gives the feel of how much of the sample lies behind each z.

**Cluster-shape view** (`shape_D4_<p>GeV.png`, after arXiv:2412.12346 Fig. 5): z_cl − z_front against ℓ and w_T
against ℓ for every ZDC cluster, the truth-best photon and neutron clusters overlaid, with the stock box
(ℓ < 100, w_T < 12 mm), PR 3114's (110 / 22 mm), EICrecon's z cut (front + 1316 mm, F7) and the paper's (front +
300 mm). ℓ and w_T are the largest and second-largest √eigenvalue, z the proton-frame z — the quantities
`FarForwardNeutralsReconstruction::isGamma` cuts on, with its exact logic for the pass fractions.

| run | γγ at 100 GeV: sep / split / merged / miss | 175 GeV | 275 GeV | D4 175 GeV γ pass stock / PR 3114 | D4 175 GeV n pass stock / PR 3114 / paper-z | D2 γ pass stock / PR 3114 (20–275 GeV) |
|---|---|---|---|---|---|---|
| R0_stock | 0.01 / 0.00 / 0.87 / 0.12 | 0.02 / 0.00 / 0.95 / 0.03 | 0.01 / 0.00 / 0.98 / 0.01 | 0.002 / 0.080 | 0.000 / 0.003 / 0.000 | 0.00–0.09 / 0.88–0.99 |
| P1a_R0_nlr3 | 0.01 / 0.00 / 0.90 / 0.10 | 0.01 / 0.00 / 0.96 / 0.03 | 0.01 / 0.00 / 0.98 / 0.01 | 0.001 / 0.044 | 0.000 / 0.002 / 0.000 | 0.00–0.09 / 0.88–0.99 |
| P1b_R0_thr | 0.08 / 0.00 / 0.89 / 0.03 | 0.05 / 0.00 / 0.93 / 0.02 | 0.02 / 0.00 / 0.97 / 0.01 | 0.001 / 0.095 | 0.000 / 0.003 / 0.000 | 0.00–0.09 / 0.88–0.99 |
| P1f_R1_dist | 0.05 / 0.00 / 0.92 / 0.03 | 0.03 / 0.00 / 0.96 / 0.01 | 0.01 / 0.00 / 0.98 / 0.01 | 0.001 / 0.055 | 0.000 / 0.002 / 0.000 | 0.00–0.09 / 0.87–0.99 |
| P1c_R0_dist | 0.01 / 0.00 / 0.52 / 0.47 | 0.06 / 0.00 / 0.71 / 0.22 | 0.11 / 0.01 / 0.79 / 0.09 | 0.382 / 0.448 | 0.123 / 0.206 / 0.086 | 0.44–0.94 / 0.72–0.98 |
| P1e_R1_thr | 0.01 / 0.00 / 0.55 / 0.44 | 0.08 / 0.00 / 0.72 / 0.20 | 0.10 / 0.01 / 0.81 / 0.08 | 0.340 / 0.400 | 0.100 / 0.169 / 0.071 | 0.44–0.94 / 0.72–0.98 |
| R1_pr3064 | 0.16 / 0.01 / 0.64 / 0.19 | 0.21 / 0.06 / 0.66 / 0.07 | 0.15 / 0.08 / 0.74 / 0.03 | 0.494 / 0.546 | 0.098 / 0.167 / 0.069 | 0.44–0.95 / 0.72–0.98 |
| P1d_R1_nlr1 | 0.16 / 0.02 / 0.62 / 0.20 | 0.24 / 0.06 / 0.62 / 0.07 | 0.19 / 0.09 / 0.68 / 0.04 | 0.590 / 0.638 | 0.123 / 0.205 / 0.086 | 0.44–0.96 / 0.72–0.99 |

What the views say:
- **Merging, not splitting, is what keeps the Λ photons from being separated.** "Split" is ≤ 0.09 on every
  clustering; "merged" is 0.87–0.98 on the 3×3 clusterings and 0.62–0.81 even on the 1×1 columns. On columns
  the photons separate for early decays (R1, 175 GeV: 50–65 % at z < 15 m) and merge behind ~20 m, where the
  opening angle has closed — the decay position, not only the geometry and parameters, limits the clustering.
  Splitting algorithms (B8) and the chaining threshold (B3) are the levers; the cut box is not.
- **The stock photon box rejects every photon on 3×3 clusters** (D2 0–9 %, D4 ≤ 0.2 %); PR 3114's box passes
  88–99 % of single photons on 3×3 but only 3–14 % of the truth-best photon clusters in Λ events, because those
  are merged (F8: necessary, not sufficient).
- **On column clusterings any box is leaky**: PR 3114's passes 17–41 % of the truth-best neutron clusters
  (R1 at 175 GeV 17 %); the paper's z cut (front + 300 mm) removes about 30 % of those fakes at almost no photon
  cost (R1 175 GeV: n pass 0.098 → 0.069 stock box, γ 0.494 → 0.493). F7 matters as soon as photons are tagged.
- **Missing photons** (no cluster at all) are 10–47 % at 100 GeV on the clusterings with R0's 25 MeV / 10-hit
  cut (R0, P1a, P1c, P1e) and 3 % with the low thresholds (P1b, P1f): the soft-photon loss that P1b recovers.

Example plots: [R0 175 GeV decay z](../plots/phase1/R0_stock/shape_decayz/decayz_D4_175GeV.png),
[R1 175 GeV decay z](../plots/phase1/R1_pr3064/shape_decayz/decayz_D4_175GeV.png),
[P1b 100 GeV decay z](../plots/phase1/P1b_R0_thr/shape_decayz/decayz_D4_100GeV.png),
[R0 175 GeV shapes](../plots/phase1/R0_stock/shape_decayz/shape_D4_175GeV.png),
[R1 175 GeV shapes](../plots/phase1/R1_pr3064/shape_decayz/shape_D4_175GeV.png).

## R2 — PR eic/EICrecon#3114 on stock clustering

R2's reconstruction (all datasets incl. D6a) was still running when Phase 1 closed (2026-11-05 15:35 UTC). Its hypothesis is in the ledger (written before any R2 output was read); its analysis — S2 tag efficiency, mistag, S4a, S5 — is Phase 2 step 0, in `space/reports/phase2_parameters.md` and the R2 ledger entry.

## S5 quick (D6a, background-free, D-default-21)

| run | sample | events | Λ candidates / 1000 | in window / 1000 | truth Λ in acceptance | eff given acceptance |
|---|---|---|---|---|---|---|
| R0 | D6a_local (9x130) | 2000 | 0 | 0 | 0 | — |
| R0 | D6a_9x275 | 5000 | 0 | 0 | 23 | 0 |
| R1 | D6a_local (9x130) | 2000 | 3.5 | 1.5 | 0 | — |
| R1 | D6a_9x275 | 5000 | 21.2 | 9.8 | 23 | 1/23 = 0.04 ± 0.04 |

R1's in-window Λ mass: μ = 1.149 GeV, σ = 0.045 GeV (Λ: 1.1157). EICrecon's `ReconstructedLambdas` at the pin already
combines the ZDC, B0 ECal, EEMC-P and LFHCAL neutrals (`reco.cc:266-270`), so these are the all-calorimeter numbers;
the ZDC-only split (candidates whose three daughters are ZDC neutrals) is not measured — `402_lambda_msf_metrics.py`
does not trace a candidate's daughters to their collection yet (a Phase 2 step-0 item).

## Ruler notes

- Q9 → D-user-16: containment is measured against the particle's energy in surviving clusters, so discarding
  shards inflates it (P1e S0n +0.20 to +0.57 with the raw neutron sum −24 to −81 %). The one-sided S3 guard catches
  it on neutrons; the new photon raw-sum guard (D2, drop ≤ 5 %) on photons. Photon raw sum vs R0: R1 −6 to −29 %
  (D2), −26 to −41 % (Λ photons); P1c −12 to −61 %; P1b +0 to +3 % (Λ photons +1 to +14 %). Gains from lowering
  thresholds (P1b) are conservative under this containment.
- Q10 → D-user-17: S2 at 20 GeV sits at the limit for every 3×3 clustering after its own refit (R0 0.9526 ±
  0.0099, P1b 0.9488 ± 0.0092); with 2σ every Phase 1 row passes S2.
- D-user-12's σ/mean check for raw-sum increases is computed by hand here (`metrics-<exp>.json`); 400 is frozen and
  has no paired test for it yet.

## Backlog for Phase 2/3

B1–B10 in `space/EXPERIMENTS.md`: seed and size thresholds at 3×3 (B1, B2), the chaining threshold against the
γγ / γn merging (B3), nlr 2 (B4), HEXPLIT sharing (B5), sectorDist (B6), the distance as code incl. split
same-/diff-layer reach (B7), Island + splitCluster (B8), the Λ family — cut box, z cut, calibration form, the
IP-pointing preselection (B9), the truth-cluster chain (B10).

## Proposed start of Phase 2 (for the user's review)

E01 = adopt P1b: its held-out D1h / D4h reconstruction (rule 8) and the paired S0 there against R0's; P1b's
refit coefficients (γ 1.765 / 0.919, n 2.221 / 0.897) become part of the current best (rule 6). If accepted, B1–B3 scan from P1b; R2's cut box (B9a) is applied on top as soon as a 3×3
clustering separates enough photon pairs for it to matter.

## Reference rows

| cell | R0_stock | R1_pr3064 | Rt_truthchain |
|---|---|---|---|
| S0γ mean (D4) | 0.057 | 0.368 | 0.057 |
| S0n mean (D4) | 0.654 | 0.044 | 0.654 |
| S0all mean (D4) | 0.017 | 0.013 | 0.017 |
| S0γ 175 GeV | 0.065 | 0.399 | 0.065 |
| S0n 175 GeV | 0.648 | 0.042 | 0.648 |
| S0all 175 GeV | 0.023 | 0.015 | 0.023 |
| S1a_truth both γ separated, mean (D1) | 0.186 | 0.600 | — |
| S1a_raw exactly 2 clusters, mean (D1) | 0.186 | 0.010 | — |
| S2 γ-tag efficiency, mean (D2) | 0.031 | 0.947 | — |
| S2 corrected scale median, mean (D2) | 1.186 | 2.887 | — |
| S3 raw Σ E / E, mean (D3) | 0.564 | 0.381 | — |
| S3 clusters per neutron (D3) | 0.817 | 7.518 | — |
| S3 corrected scale median (D3) | 1.050 | 1.121 | — |
| S4a_tm mean (D4) | 0.000 | 0.018 | 0.000 |
| S4a_any mean (D4) | 0.000 | 0.029 | 0.000 |
| S4a_Rt (as-built truth chain) | 0.000 | 0.000 | 0.000 |
| S4b Λ mass σ [GeV] | — | 0.027 | — |
| G1 φ@180, NC / SIDIS | 0.068 / 0.074 | 1.000 / 1.000 | — / — |
| G1 single-column, NC / SIDIS | 0.000 / 0.000 | 1.000 / 1.000 | — / — |
| G2 E > 50 GeV fraction, NC / SIDIS | 0.612 / 0.864 | 0.006 / 0.016 | — / — |
| G3 clusters < 5 GeV per event, NC / SIDIS | 0.006 / 0.010 | 2.126 / 5.441 | — / — |
| clusters per event, NC / SIDIS | 0.555 / 0.984 | 3.640 / 10.160 | — / — |

Rt is the truth chain as built (D4 only): its S4a is 0 because EICrecon's HCal ZDC truth clusters
are no perfect-clustering input (Phase 0 observation O2); the S4a ceiling with ideal inputs is
0 / 0 / 0.007 / 0.025 / 0.030 / 0.050 / 0.062 / 0.068 at 100–275 GeV (`space/perf/lambda-ceiling-R0_stock.json`).
