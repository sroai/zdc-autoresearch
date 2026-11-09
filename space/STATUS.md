PHASE6 CLOSED 2026-11-09T19:40Z at the user's order (D-user-45); PHASE7 PREPARED (zdc-autoresearch-loop-v7.md: the EICrecon changes as pull-request units, each checked so that no collection outside its declared list moves — 130 identity, capybara — and its declared collections shown on the detector benchmarks; the user opens the pull requests, nothing is pushed). Phase 6 final row Z8_hcal_axis_law: 1946 found on the search halves (Y9 1486), 1865 held out (Y9 1411), purity 30.9 / 30.1 %, −t σ68 0.114 / 0.118 GeV². Report space/reports/phase6_crystal.md (Final state); deck slides/phase6/ (28 slides); plots space/plots/phase6/.
## LIVE
- Nothing running. Nothing committed, nothing pushed.
- EICrecon working tree = a15b0db6 + Y2 + Y5 + Y9 (phase5_cumulative.patch) + Z1b_crystal_column.patch + Z5_crystal_energy_alt.patch + Z6_alt_column_out.patch + Z7_isolation.patch + Z8_hcal_axis_law.patch (uncommitted; space/notes/patches/, apply in this order). Local only. NO PUSHES.
## RESUME (Phase 7, prepared)
- Start line: `Read zdc-setup.md, work-common.md and zdc-autoresearch-loop-v7.md. Run.` (+ `online`, `please-git`, `one unit` as wanted).
- Step 0 waits on Q23 (the base: main + PRs 3064/3063 heads, or the pin) and, for P6 and P7, Q24 (zdc_lyso and far_forward_dvcs samples).
- Proposed units P1–P8 (loop v7 table): depth-limit fix, ImagingTopoCluster core split (off), Λ vertex, ZDC pairing (off), crystal photons (off), LYSO clustering, B0 ECal splitting + law, the ZDC configuration that reproduces Z8.
- Whole EICrecon diff from a15b0db6: space/notes/patches/phase6_working_tree.patch.
## Phase 6 record (closed)
- Final row Z8_hcal_axis_law (install eicrecon-Z8, configs/experiments/Z8_hcal_axis_law.yaml): Z7 + hcalAxisAlternative (crystal + Hcal rec hits within 45 mm of a tagged photon's line, law 2.5938,45.8981,-1.5994 from 481 on the photon guns) as a competing energy; new input EcalFarForwardZDCRecHits. Search halves 1688 + 258 = 1946, purity 30.9 %; held out 1621 + 244 = 1865, purity 30.1 %; −t σ68 0.114 / 0.118 GeV²; D4 S4a_tm 8.42 % mean / 15.99 % at 275 GeV.
- Z7_isolation: Z6 + lambdaPairingIsolationWeight 2, Length 42.5 mm (the neutron gun's fragment scale, CAL6_D3_Z6 / 480): 1883, purity 30.4 %, −t 0.120 / 0.118.
- Z6_alt_column_out: the base the user chose (D-user-44): 1797 search, 1703 held out; −t 0.121 / 0.120.
- Tries since checkpoint 2: none (checkpoint 2 ran after Z6, Z7, Z8, early, the backlog being empty).
- The gap to the reachable yield (report section, 482): 9x275 3124 reachable, 1686 found; no clean photon cluster 704 (photon inside the neutron's Hcal cluster 278), clean clusters but the wrong photon ~540, mass out of the window ~200.
- Next run (report, Next run recommendations): 1) an axis law for crystal candidates (crystal photons read 0.32 in the right pairs out of the window); 2) a joint photon-likeness fitted on a two-particle gun (photon + neutron at MSF separations); 3) EEMC-P photons are outside the ZDC chain (146 Λ, soft, no pure EEMC-P neutral).
- Tools: 469 scores a try (460 -msf, 468, 210, 463, 476), 478 F1 on the as-built tree (D-user-43), 479 raw-hit identity, 477 emulation (--alt --alt-col-out = Z6; --iso W:L = Z7; --axis-law R = Z8; --front, --no-crystal-alt, --why-all), 480 photon-likeness features (MSF and --guns), 481 the axis law on the photon guns, 482 why a reachable Λ's photon has no clean cluster, 702 the phase plots.
## Waiting on the user
- Q23 and Q24 (space/QUESTIONS.md); the Phase 7 start line.
- Whether to reconstruct D4 for the six Phase 6 tries without it (Z1, Z1b, Z2, Z4, Z6, Z7), to complete the deck's D4 bar slide.
- Run space/notes/cleanup-pending.sh when convenient (Phase 6: Z1–Z7 ROOT except the kept rows, CP6_1 D4, switch proofs).
- Q17, Q18 (Phase 3) are unanswered and superseded by Phase 4's rules; nothing waits on them.
## Pointers
- ledger space/LEDGER.md (PHASE6 spec); experiments space/EXPERIMENTS.md; history space/notes/runlog.md; decisions space/notes/DECISIONS.md (D-default-47..51, D-user-43..45); questions space/QUESTIONS.md (Q23, Q24 open); loop zdc-autoresearch-loop-v7.md
- −t of the Phase 5 rows: space/reports/msf_t_resolution.md (476).
## Run mode
- Phase 6 ran auto, online, no please-git (tries as patches). NO PUSHES, ever. D-user-35: ≤ 4 eicrecon jobs, 8 idle cores, /data ≥ 150 GB free.
