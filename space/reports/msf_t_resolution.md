# −t resolution of the reconstructed Λ → nπ⁰ on MSF events

Measured 2026-11-09 on the Phase 5 rows, MSF search halves D6s (files 0001–0040), truth-matched Λ → nπ⁰ only (`210`'s
match: n, γ, γ neutrals each with a cluster of purity ≥ 0.8, mass within ±30 MeV).

- −t = −(P_beam − P_Λ)². Reconstructed: the matched `ReconstructedLambdas` entry with the nominal beam (E_p, crossing
  −25 mrad in xz, as `meson-structure/analysis/kaon-lambda`). True: the generator Λ with the event's own beam proton.
- σ68 = half the 16–84 % range of Δ(−t) = reco − true. The RMS (≈ 0.34 GeV² at 9x275) is dominated by a tail.

## Y9 (Phase 5 final)

| beam | Λ | true −t median | σ68 | bias | \|Δ\| < 0.1 GeV² | \|Δ\| < 0.05 GeV² |
|---|---|---|---|---|---|---|
| 9x275 | 1267 | ≈ 0.8 GeV² | 0.124 GeV² | −0.028 | 56 % | 34 % |
| 9x130 | 219 | 0.44 GeV² | 0.133 GeV² | −0.014 | 58 % | 37 % |

σ68 per true −t bin (GeV²; relative to the bin's median −t in brackets):

| true −t (GeV²) | 9x275 | 9x130 |
|---|---|---|
| 0–0.2 | 0.050 (0.34) | 0.063 (0.51) |
| 0.2–0.5 | 0.076 (0.22) | 0.125 (0.41) |
| 0.5–1.0 | 0.106 (0.14) | 0.162 (0.23) |
| 1.0–3.0 | 0.177 (0.14) | — |

- Beam part (truth Λ, nominal vs event beam): 0.045 GeV² at 9x275, 0.016 at 9x130. Detector part: 0.110 and 0.133.
- By regime at 9x275: all three daughters in the ZDC 0.116 GeV² (749 Λ); one or both photons in B0 0.133 (518).
- Λ energy: E_reco / E_true median 1.074 (σ68 0.116) at 9x275, 1.060 (0.163) at 9x130; it drives the −0.03 bias.

## X9 (Phase 4 final), for comparison

| beam | Λ | σ68 | bias | \|Δ\| < 0.1 GeV² |
|---|---|---|---|---|
| 9x275 | 943 | 0.122 GeV² | −0.021 | 58 % |
| 9x130 | 66 | 0.097 GeV² | −0.015 | 70 % |

Phase 5 added 47 % more found Λ at the same −t resolution.

Script: `scripts/476_msf_t_resolution.py` (rows as arguments).
