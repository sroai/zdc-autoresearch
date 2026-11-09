# Phase 3 findings ledger

Append-only; numbers continue the global index `space/reports/FINDINGS.md` (F1–F9 from Phases 0–2).

## F10 — LambdaReconstruction places the ZDC neutron at the event's first cluster, not at the neutron (OPEN, measured 2026-11-06)
- Where: `src/algorithms/reco/LambdaReconstruction.cc:60` (`reconstruct_from_triplet`): `const auto rn = n_in.getClusters(0).getPosition();`,
  with `src/algorithms/reco/FarForwardNeutralsReconstruction.cc:244-246` and `:279` (`associateAllClustersToNeutron = true` for the
  ZDC): the neutron neutral lists every ZDC cluster of the event, in collection order, so `getClusters(0)` is cluster 0 of
  `HcalFarForwardZDCClusters` — often a photon's cluster. The neutron's momentum and reference point aim at its leader
  (the most energetic non-photon cluster), so the stock preselection and the IDOLA vertex read two different neutron
  positions.
- Reproducer: `uv run scripts/416_neutron_position.py R2_pr3114 L01_box3114 R1_pr3064` (EICrecon's own tags and neutron
  energy from the D4 ROOT files, the three truth-matched daughters, the stable-vertex chain of `zdc/lambda_chain.py`).
- Evidence: cluster 0 is the neutron's leader in 0 of 236 (R2), 0 of 566 (L01) and 52 of 3638 (R1) tagged triplets. With
  the neutron at its leader the stable-vertex chain keeps +20 % (R2: 164 → 197), +57 % (L01: 332 → 522) and +28 % (R1:
  1053 → 1349) more Λs in the scoring window (`space/perf/lambda-neutron-position-<row>.json`).
- Severity: medium today (the stock chain's yield is capped by F4 first), high once the vertex is stable (B9d, PR 3063):
  the neutron direction enters the Λ direction and the mass. Fix: `n_in.getReferencePoint()` (the leader's position, set by
  the neutrals factory) instead of `getClusters(0).getPosition()`, or set `associateAllClustersToNeutron = false` so that
  cluster 0 of the neutron is one of its own. Owner: EICrecon issue/PR with the Λ chain (B9e, Phase 3 Λ family).
