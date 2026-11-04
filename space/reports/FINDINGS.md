# FINDINGS: index (F1 to F4)

Defects found in code the program does not own (EICrecon, the benchmarks,
capybara, the campaign data). Status first; full entries in
`phase<N>_findings.md`; rules in `work-common.md`, section Findings. F1 to F4
come from the expert review of loop v1 and are verified in Phase 0.

| status | F | title | component | owner |
|---|---|---|---|---|
| OPEN | F1 | ZDC benchmark scripts use pre-#2622 collection names; Λ and photon plots silently empty | detector_benchmarks | upstream PR, Phase 4 |
| OPEN | F2 | `LambdaReconstruction::init` mm/cm fallback (latent) | EICrecon | issue |
| OPEN | F3 | HEXPLIT S2 subcells carry hexagon dimensions | EICrecon | issue |
| OPEN | F4 | IP-pointing π⁰ preselection caps Λ efficiency independent of clustering | EICrecon | issue with Rt numbers, Phase 4 |

Totals: 4 findings, 4 OPEN, 0 FIXED, 0 RESOLVED, 0 WON'T FIX. OPEN blocking: none.
