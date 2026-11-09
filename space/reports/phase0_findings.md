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

## F2 — `LambdaReconstruction::init` unit fallback (OPEN, verified latent 2026-11-05)
- Where: `src/algorithms/reco/LambdaReconstruction.cc:26-29`.
- Defect: when the detector constant `HcalFarForwardZDC_SiPMonTile_r_pos` is missing, the fallback `m_zMax = 35800` is in mm while the constant is read in cm: a latent factor-10 bug. Latent only; verify by reading the code at the pin.
- Verified: the main path reads the constant in dd4hep units (cm) and the cluster positions are converted with `* dd4hep::mm`, so the vertex scale `m_zMax / λ.Z()` is consistent; only the catch branch (`m_zMax = 35800`) is a mm number in a cm context. Every gun and MSF geometry here defines the constant, so the branch never runs.
- Severity: low. Owner: issue to EICrecon.

## F3 — HEXPLIT gives S2 subcells hexagon dimensions (OPEN, to verify)
- Where: `src/algorithms/calorimetry/HEXPLIT.cc:212-215`.
- Defect: the subcell hits of the square-tile (S2) stagger are written with the hexagonal dimensions. Consumers that read `dimension` would be wrong; the clustering does not read it (to verify).
- Severity: low. Owner: issue to EICrecon.

## F4 — `LambdaReconstruction` IP-pointing π⁰ preselection caps the Λ efficiency (OPEN, measured 2026-11-05)
- Where: `src/algorithms/reco/FarForwardNeutralsReconstruction.cc:97-103` (photon momentum along the cluster position from the origin), `src/algorithms/reco/LambdaReconstruction.cc:309-322` (±10 % π⁰ window before the vertex iteration).
- Defect (physics): m_γγ computed with IP-pointing photons scales as (L − z_d)/L, so decays beyond about 3.6 m fail the window regardless of clustering; the Λ-gun acceptance at 100 GeV keeps only late decays, so the benchmark's efficiency there is structurally near zero. Rt (Phase 0 item 12) measures it.
- Measured (Phase 0 item 12, `scripts/412_lambda_ceiling.py`, `space/perf/lambda-ceiling-R0_stock.json`): with ideal inputs (true energies, true daughter lines at shower depth) through the algorithm's own steps, decays within 3 m pass at 100 %, 3–4 m at 40–76 %, beyond 4 m none. The ceiling of S4a on D4 is 0 at 100 and 125 GeV, 0.007 at 150, 0.025 at 175, 0.030 at 200, 0.050 at 225, 0.062 at 250, 0.068 at 275 GeV. The review's 3.6 m estimate holds. R1's measured S4a_tm (0.028–0.031 at 200–225 GeV) is already 50–90 % of the ceiling. The Rt build itself gives 0 for a different, owned reason (the HCal ZDC truth clusters, report item 12).
- Severity: high for the MSF physics (not for this program's selector). Owner: an EICrecon issue with these numbers (Phase 4 deliverable).

## F5 — ZDC neutrals and Λ are empty on ZDC-only geometries at the pin (OPEN)
- Where: `src/global/reco/reco.cc:242-246` (one `FarForwardNeutralsReconstruction` instance with inputs `HcalFarForwardZDCClusters`, `B0ECalClusters`, `EcalEndcapPClusters`, `LFHCALClusters`); `src/factories/reco/FarForwardNeutralsReconstruction_factory.h:23-26` (all four `PodioInput` required).
- Defect: on `epic_zdc_lyso_sipm` or `epic_zdc_sipm_on_tile_only` the B0 ECal, EEMC-P and LFHCAL cluster factories throw (no readout: `Failed to get idSpec for B0ECalHits`), so `ReconstructedHcalFarForwardZDCNeutrals` is written empty in every event and `ReconstructedLambdas` with it. The detector_benchmarks ZDC jobs run on `epic_zdc_sipm_on_tile_only`, so their Λ and photon-neutral plots are empty for this reason as well as F1's names.
- Reproducer: R0 reco of `D2_photon_50GeV_seed1` simulated on `epic_zdc_lyso_sipm`: 1000 events, 0 neutrals; same algorithm on the full-geometry MSF campaign file `msf_9x130_1000evt_0001`: 131 ZDC neutrals.
- Tried: marking the three non-ZDC inputs optional (`PodioInput<edm4eic::Cluster, true>`, `space/notes/patches/harness_neutrals_optional_inputs.patch`) ends in `terminate called without an active exception`: the upstream cluster factories still throw.
- Workaround here: the guns are simulated on `epic_craterlake` (D-user-8).
- Severity: medium (benchmarks blind, any ZDC-only study of the neutrals impossible). Owner: EICrecon issue (separate factory instance per detector, or upstream factories that tolerate an absent detector).

## Status lines appended 2026-11-06
- F4 — OPEN, addressed in part by eic/EICrecon#3063 (open): the PR removes the IP-pointing π⁰ window and the Λ window; the IDOLA iteration then runs on every triplet (F9). Review comment with the numbers: loop v3, Phase 3 Step 0 item 8.
