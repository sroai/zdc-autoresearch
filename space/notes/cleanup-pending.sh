#!/bin/bash
# Data the program no longer needs, for the user to delete (D-user-32). Claude appends an item when a row's
# reconstruction ROOT stops being needed and says so in chat; the user runs:
#     bash space/notes/cleanup-pending.sh
# `drop` removes only reconstruction ROOT files (*.edm4eic.root); per-file JSON, the 410 truth tables
# (npz), the tag caches, timing.csv and logs stay, so every score, plot and paired test that needs no
# re-reading of ROOT still works. `purge` removes a whole directory under /data/zdc-autoresearch: only for
# aborted rows, finished proof/repeat rows and unused builds, whose JSON no score reads. Retention (D-user-19,
# D-user-32): full ROOT only for R0, R1, R2, R3, Rt, the current best clustering (P1b) and the reference of the
# clustering selector (L01), plus rows whose verdict is pending. After a run, Claude empties the item list below.
set -u
DATA=/data/zdc-autoresearch
RECO=$DATA/reco
drop() {   # drop <row> <reason>
  local n
  n=$(find "$RECO/$1" -name '*.edm4eic.root' | wc -l)
  [ "$n" -eq 0 ] && { echo "skip  $1: no ROOT left"; return; }
  echo "drop  $1: $n ROOT files ($(find "$RECO/$1" -name '*.edm4eic.root' -printf '%s\n' | awk '{s+=$1} END {printf "%.1f GB", s/1e9}')) — $2"
  find "$RECO/$1" -name '*.edm4eic.root' -delete
}
dropds() { # dropds <row> <dataset> <reason>: ROOT of one dataset of a row; JSON and npz stay
  local d=$RECO/$1/$2 n
  [ -d "$d" ] || { echo "skip  $1/$2: gone"; return; }
  n=$(find "$d" -name '*.edm4eic.root' | wc -l)
  [ "$n" -eq 0 ] && { echo "skip  $1/$2: no ROOT left"; return; }
  echo "drop  $1/$2: $n ROOT files ($(find "$d" -name '*.edm4eic.root' -printf '%s\n' | awk '{s+=$1} END {printf "%.1f GB", s/1e9}')) — $3"
  find "$d" -name '*.edm4eic.root' -delete
}
purge() {  # purge <path relative to /data/zdc-autoresearch> <reason>
  local d=$DATA/$1
  case "$1" in ""|/*|*..*) echo "refuse $1"; return;; esac
  [ -d "$d" ] || { echo "skip  $1: gone"; return; }
  echo "purge $1: $(du -sh "$d" | cut -f1) — $2"
  rm -rf -- "$d"
}

# ---- items added 2026-11-08T23:40Z (Phase 5, loop v5; the Phase 4 list above this line was run by the user on 2026-11-08 before the MSF 2026-11 copy and is emptied) ----
drop MSF11_X9 "full-template X9 on D6c (MCParticles, 58 GB): superseded by MSF5_X9 (MSF template, same per-Λ results); msf-regimes-MSF11_X9-D6c_*.json stay"
drop Y1_b0_split "Phase 5 try, INCONCLUSIVE (463); 210 / 463 / 460 JSON stay; a combined retry reconstructs again"
drop CTL5_X1_msf "Step 0 selector control (X1 vs X9 written to msf-select-*.json)"
purge reco/CTL5_swap "Step 0 control: links to MSF5_X9 outputs only (rm -rf removes the links, not their targets)"
purge reco/T5_probe_b0split "20-event parameter smoke run"
purge reco/T5_probe_lmw "20-event parameter smoke run"
purge reco/T5_y5_mixed0 "Y5 switch proof (file 0001, off = Y4 identical); result in the runlog"
purge reco/T5_y5_mixed1 "Y5 switch proof (file 0001, on changes 45 events)"
purge reco/T5_probe_b0law "20-event check of the B0 photon law parameter (1.0,1.0 → neutral E = cluster E)"
drop CAL5_D2b_Y4 "B0 gun on Y4's clustering: the law launched is CAL5_D2b_Y6's; calib-B0-CAL5_D2b_Y4.json stays"
purge reco/T5_y9_pair0 "Y9 switch proof (file 0001, off = Y8 identical)"
purge reco/T5_y9_pair1 "Y9 switch proof (file 0001, on changes 22 events)"
drop Y10_lambda_mass_rank "Phase 5 try REJECTED (no effect); 210 / 463 / 460 JSON stay"
# ---- items added 2026-11-09T03:26Z (Phase 5 closed, D-user-41: every verdict, checkpoint and plot is written; 210 / 463 / 460 / 410 JSON and npz stay. Kept: MSF5_X9 (base), Y9_external_pair (final: D6s, D6h), CP5_2_Y9_D4, CTL5_R0_msf (F2 reference), CAL5_D2b_Y6 (the B0 law launched), and the builds of Y9) ----
drop Y2_vertex_lever_arm "accepted try, superseded by Y9"
drop Y4_b0_split_on_y2 "accepted try, superseded by Y9"
drop Y5_mixed_pairing "accepted try, superseded by Y9"
drop Y6_b0_profile "accepted try and checkpoint-1 best (D6s, D6h), superseded by Y9"
drop Y7_b0_photon_law "accepted try, superseded by Y9"
drop Y8_b0_profile_03 "accepted try, superseded by Y9"
drop CP5_1_Y6_D4 "checkpoint 1 D4, headline.csv written"
drop CAL5_D2b_Y8 "B0 gun check, written to the runlog"
drop CAL5_D2b_Y11 "B0 gun check (peak threshold), written to the runlog"
drop D4P5_Y1 "D4 of a Phase 5 try for the deck's Phase 4 columns; headline.csv written"
drop D4P5_Y2 "D4 of a Phase 5 try for the deck's Phase 4 columns; headline.csv written"
drop D4P5_Y4 "D4 of a Phase 5 try for the deck's Phase 4 columns; headline.csv written"
drop D4P5_Y5 "D4 of a Phase 5 try for the deck's Phase 4 columns; headline.csv written"
drop D4P5_Y7 "D4 of a Phase 5 try for the deck's Phase 4 columns; headline.csv written"
drop D4P5_Y8 "D4 of a Phase 5 try for the deck's Phase 4 columns; headline.csv written"
drop D4P5_Y10 "D4 of a Phase 5 try for the deck's Phase 4 columns; headline.csv written"
purge build/eicrecon-Y2 "build tree of an accepted try; the patches rebuild it"
purge build/eicrecon-Y5 "build tree of an accepted try; the patches rebuild it"
# Phase 6 run 1 (2026-11-09): superseded tries (ROOT only; JSON and scores stay), test runs, the Phase 5 crystal probe.
drop Z1_crystal_photons "Phase 6 try, INCONCLUSIVE, superseded by Z1b; scores in msf-*.json"
drop Z1b_crystal_column "Phase 6 try, ACCEPTED then superseded by Z2; scores in msf-*.json"
drop Z2_crystal_params "Phase 6 try, ACCEPTED then superseded by Z4; scores in msf-*.json"
drop Z4_lambda_sigma "Phase 6 try, ACCEPTED then superseded by Z5; scores in msf-*.json"
purge reco/T6_z1_switch0 "Z1 switch proof (file 0001); result in the runlog"
purge reco/T6_z1_switch1 "Z1 switch proof (file 0001); result in the runlog"
purge reco/T6_z1b_smoke "Z1b energy smoke check (file 0001); result in the runlog"
purge reco/T6_z5_switch0 "Z5 switch proof (file 0001); result in the runlog"
purge reco/T6_z5_switch1 "Z5 switch proof (file 0001); result in the runlog"
purge reco/T6_z6_switch0 "Z6 switch proof (file 0001); result in the runlog"
purge reco/T6_z6_switch1 "Z6 switch proof (file 0001); result in the runlog"
purge reco/T5_crystal_probe "Phase 5 crystal probe; Phase 6 Step 0 read MSF6_Y9's rec hits instead"
# Phase 6 run 2 (2026-11-09): Z5 is no longer the base (D-user-44, Z6); its scores, 210 / 463 / 476 JSON stay. Switch proofs.
drop Z5_crystal_energy_alt "Phase 6 try, ACCEPTED, then the base became Z6 (D-user-44); scores in msf-*.json, t-resolution-*.json"
purge reco/T7_z7_switch0 "Z7 switch proof (file 0001, off = Z6 identical); result in the runlog"
purge reco/T7_z7_switch1 "Z7 switch proof (file 0001, on changes 35 of 500 events); result in the runlog"
# Phase 6 run 2 end (2026-11-09T15:23Z): checkpoint 2 written; superseded tries (ROOT only; JSON, npz, scores stay). Kept: Z8 (current best, D6s + D6h), MSF6_Y9 (base row / F2 reference), CTL6_R0_crys, CAL6_D2_Y9 + CAL6_D3_Z6 (gun inputs of 477 / 480 / 481).
drop Z6_alt_column_out "Phase 6 base by D-user-44, superseded by Z7 and Z8; D6s / D6h scores, t-resolution JSON stay"
drop Z7_isolation "Phase 6 try ACCEPTED, superseded by Z8; scores in msf-*.json"
drop CP6_1_Z5_D4 "checkpoint 1 D4, headline.csv written"
purge reco/T8_z8_switch0 "Z8 switch proof (file 0001, off = Z7 identical); result in the runlog"
purge reco/T8_z8_switch1 "Z8 switch proof (file 0001, on changes 66 of 500 events); result in the runlog"
# Leave-one-out ranking on Z8 (2026-11-09, D-user-46): the one-file switch proofs (results in the runlog).
purge reco/TAB_Z8 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB1 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB2 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB3 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB4 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB5 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB6 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB7 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB8 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB9 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB10 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB11 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB12 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB13 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB14 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
purge reco/TAB_AB15 "leave-one-out switch proof (file 0001, 500 events); result in the runlog"
# Leave-one-out ranking done (2026-11-09 22:02 EST): the ablation rows (ROOT only; msf-regimes, msf-select, t-resolution JSON stay; report space/reports/leave_one_out.md). Kept for follow-ups: AB9 (stock-clustering base), AB10 (cheap set), AB16 (LambdaReconstruction-only base).
drop AB1_no_depth_cut "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB2_no_pairing "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB3_no_mixed "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB4_no_b0_pair "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB5_b0_stock "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB6_no_crystal "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB7_no_core_split "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB8_no_split_no_pairing "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB11_stock_no_depth_cut "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB12_stock_no_mixed "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB13_stock_no_b0_pair "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB14_stock_b0_stock "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB15_stock_no_crystal "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
drop AB17_cheap_zdc_laws_stock "leave-one-out row, scored (space/perf/leave-one-out-*.json)"
df -h /data | tail -1
