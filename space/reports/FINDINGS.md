# FINDINGS: index (F1 to F10)

Defects found in code the program does not own (EICrecon, the benchmarks,
capybara, the campaign data). Status first; full entries in
`phase<N>_findings.md` (F1–F5 phase0, F6–F8 phase1, F9 phase2, F10 phase3; status lines appended 2026-11-06 for F4, F8, F9); rules in `work-common.md`, section Findings. F1 to F4
come from the expert review of loop v1 and are verified in Phase 0.

| status | F | title | component | owner |
|---|---|---|---|---|
| OPEN | F1 | ZDC benchmark scripts use pre-#2622 collection names; Λ and photon plots silently empty | detector_benchmarks | upstream PR, Phase 4 |
| OPEN | F2 | `LambdaReconstruction::init` mm/cm fallback (verified latent) | EICrecon | issue |
| OPEN | F3 | HEXPLIT S2 subcells carry hexagon dimensions | EICrecon | issue |
| OPEN, addressed in part by PR 3063 (open) | F4 | IP-pointing π⁰ preselection caps Λ efficiency independent of clustering (measured: decays beyond 4 m never pass; ceiling 0–0.068 on D4); PR 3063 removes the window | EICrecon | review comment on #3063 (loop v3 Phase 3 Step 0 item 8); issue with F9 |
| OPEN | F5 | ZDC neutrals and Λ empty on ZDC-only geometries (neutrals factory needs B0/EEMC-P/LFHCAL clusters) | EICrecon, detector_benchmarks | issue; workaround D-user-8 |
| OPEN | F6 | Stock ZDC calibration a·E^b does not fit stock clusters (γ 13–31 % low, n 3–9 % high; γ form χ² 65/6) | EICrecon | upstream PR with per-clustering refit |
| OPEN | F7 | Photon z cut measured from the ZDC centre (`_r_pos`), 1316 mm past the front face (paper: 300 mm) | EICrecon | issue |
| FIXED | F8 | Stock photon cut box (ℓ 100, w 12 mm) rejects every ZDC photon; fixed upstream by eic/EICrecon#3114 (merged 2026-11-05, backport #3117); R2 is the equivalent at the pin. Necessary, not sufficient: 0 Λ on stock clustering, +25 gained / 0 lost on P1b (L01) | EICrecon | #3114 merged |
| OPEN, addressed in part by PR 3063 (open) | F9 | IDOLA vertex iteration runs away for decays far from the IP (latent behind F4; PR 3063 exposes it on every triplet; the stable vertex measured offline reaches the acceptance) | EICrecon | review comment on #3063 with `414`'s table; B9d patch, Phase 3 |
| OPEN | F10 | `LambdaReconstruction` places the ZDC neutron at the event's first cluster (`getClusters(0)`; every cluster is linked to the neutron), not at its leader: −17 % to −36 % of the stable-vertex Λs | EICrecon | issue with B9e, Phase 3 |

Totals: 10 findings, 9 OPEN, 1 FIXED, 0 RESOLVED, 0 WON'T FIX. OPEN blocking: none. (F8 FIXED upstream 2026-11-06; F4 and F9 addressed in part by PR 3063.)

Phase 4 status (2026-11-08, at the close): F6, F7, F9 and F10 are fixed on the local branch
`zdc-autoresearch/phase4` (F9, F10 in patch U1; F7 in U2 and U4; F6 by the refit in U4), drafted for upstream in
`space/reports/phase4_upstream.md`; nothing posted, so all four stay OPEN upstream.
