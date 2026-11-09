PHASE6 RUNNING — run 1 ended 2026-11-09 for the user's review (the backlog of tries with a predicted gain is empty); waiting on Q21 (BLOCKING: the F1d source of the crystal tries) and Q22 (the base: Z5 or Z6). Report space/reports/phase6_crystal.md; deck slides/phase6/ (13 slides).
## LIVE
- Nothing running.
- EICrecon working tree = a15b0db6 + Y2 + Y5 + Y9 (phase5_cumulative.patch) + Z1b_crystal_column.patch + Z5_crystal_energy_alt.patch (uncommitted; space/notes/patches/). Local only. NO PUSHES.
## RESUME (Phase 6)
- Current best Z5_crystal_energy_alt (install eicrecon-Z5 + Z4's parameters, configs/experiments/Z5_crystal_energy_alt.yaml): search halves 1574 + 252 = 1826 (Y9 1486), purity 29.5 %; held out 1520 + 235 (REPRODUCES, z +15.23); −t σ68 0.147 / 0.128 GeV².
- Alternative Z6_alt_column_out (install eicrecon-Z6, patch Z6_alt_column_out.patch reverted from the tree): 1547 + 250 = 1797, held out 1473 + 230 (REPRODUCES, z +13.70), −t σ68 0.121 / 0.120 GeV² (Q22).
- Next after Q22: shower shape of tagged Hcal photons as a chooser term (report, Next run recommendations); emulate with 477 first.
- Tools: 469 scores a try (460 -msf, 468, 210, 463, 476), 478 F1 on the as-built tree (D-default-49), 477 emulation (--alt for Z5's decision, --why), 479 raw-hit identity (crystal raw hits = base).
## Waiting on the user
- Q21 BLOCKING(!): the ACCEPTED verdicts of Z1b, Z2, Z4, Z5 stand only if F1d may come from the as-built tree (478, A) or tries are committed (please-git, B); under C the crystal line is FOUL.
- Q22: the base for the next tries, Z5 (1826 found, −t 0.147) or Z6 (1797, −t 0.121).
- Run space/notes/cleanup-pending.sh when convenient (Phase 6: Z1, Z1b, Z2, Z4 ROOT, test runs).
## Pointers
- ledger space/LEDGER.md (PHASE6 spec); experiments space/EXPERIMENTS.md; history space/notes/runlog.md; decisions space/notes/DECISIONS.md (D-default-47..49); questions space/QUESTIONS.md
- −t of the Phase 5 rows: space/reports/msf_t_resolution.md (476).
## Run mode
- auto, offline; no please-git (tries as patches). NO PUSHES, ever. D-user-35: ≤ 4 eicrecon jobs, 8 idle cores, /data ≥ 150 GB free.
