# Phase 0 findings ledger

Append-only. Full entries for defects in code the program does not own; one
line each in `FINDINGS.md`. The entries below were raised by the expert review
of loop v1 (`docs/expert-review-v1.md`) before any run and are to be verified
in Phase 0; each carries the file and line the review cites.

## F1 — detector_benchmarks ZDC scripts use pre-2026-05-29 collection names (OPEN)
- Where: `benchmarks/zdc_lambda/Snakefile`, `zdc_lambda/analysis/lambda_plots.py:61-64`, `zdc_photon/analysis/zdc_photon_plots.py:31-32`, `zdc_neutron/analysis/fwd_neutrons_recon.C:115-119` at `e72103b9`.
- Defect: they request `ReconstructedFarForwardZDCLambdas` / `ReconstructedFarForwardZDCNeutrals`; EICrecon main writes `ReconstructedLambdas` / `ReconstructedHcalFarForwardZDCNeutrals` since #2622 (a48dc937). The Python scripts exit 0 when the collection is missing, so the CI's Λ and photon plots are silently empty.
- Reproducer: run `lambda_plots.py` on an EICrecon-main output; no Λ histogram, exit 0.
- Severity: medium (benchmarks blind). Workaround here: `scripts/700_benchmarks/`. Owner: an upstream detector_benchmarks PR (Phase 4 deliverable).

## F2 — `LambdaReconstruction::init` unit fallback (OPEN, to verify)
- Where: `src/algorithms/reco/LambdaReconstruction.cc:26-29`.
- Defect: when the detector constant `HcalFarForwardZDC_SiPMonTile_r_pos` is missing, the fallback `m_zMax = 35800` is in mm while the constant is read in cm: a latent factor-10 bug. Latent only; verify by reading the code at the pin.
- Severity: low. Owner: issue to EICrecon.

## F3 — HEXPLIT gives S2 subcells hexagon dimensions (OPEN, to verify)
- Where: `src/algorithms/calorimetry/HEXPLIT.cc:212-215`.
- Defect: the subcell hits of the square-tile (S2) stagger are written with the hexagonal dimensions. Consumers that read `dimension` would be wrong; the clustering does not read it (to verify).
- Severity: low. Owner: issue to EICrecon.

## F4 — `LambdaReconstruction` IP-pointing π⁰ preselection caps the Λ efficiency (OPEN, to measure)
- Where: `src/algorithms/reco/FarForwardNeutralsReconstruction.cc:97-103` (photon momentum along the cluster position from the origin), `src/algorithms/reco/LambdaReconstruction.cc:309-322` (±10 % π⁰ window before the vertex iteration).
- Defect (physics): m_γγ computed with IP-pointing photons scales as (L − z_d)/L, so decays beyond about 3.6 m fail the window regardless of clustering; the Λ-gun acceptance at 100 GeV keeps only late decays, so the benchmark's efficiency there is structurally near zero. Rt (Phase 0 item 12) measures it.
- Severity: high for the MSF physics (not for this program's selector). Owner: an EICrecon issue with the Rt numbers (Phase 4 deliverable).
