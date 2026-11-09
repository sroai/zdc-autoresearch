#!/usr/bin/env bash
# Score one Phase 6 try after its reconstruction (zdc-autoresearch-loop-v6.md, the experiment loop of v5 plus 468):
#   460 on the MSF outputs (F1-F3; F2b against the base row MSF6_Y9's raw hits, crystal ones included when the try reads
#   the crystal section), 468 (F3 for crystal clusters) on both search halves, and for a code try 460 --tree and 465 on
#   its patch; then 210 on both search halves, 463 against the current best, 476 (the −t resolution of the found Λ).
#   Prints one summary line per step and the verdict (FOUL when any fair-play step FAILs). Nothing is launched or deleted.
#
# Usage: scripts/469_phase6_score.sh <experiment> <current best> [<patch>]
#   scripts/469_phase6_score.sh Z1_crystal_photons MSF6_Y9 space/notes/patches/Z1_crystal_photons.patch
set -uo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd); cd "$REPO"
EXP=$1; BEST=$2; PATCH=${3:-}
RECO=/data/zdc-autoresearch/reco; LOGS=/data/zdc-autoresearch/logs/phase6; mkdir -p "$LOGS"
foul=0
uv run scripts/460_fair_play.py "configs/experiments/$EXP.yaml" --reco-dir "$RECO/$EXP/D6s_9x275" \
  --reference-dir "$RECO/MSF6_Y9/D6s_9x275" --tag "$EXP-msf" > "$LOGS/460-$EXP-msf.log" 2>&1 || foul=1
tail -1 "$LOGS/460-$EXP-msf.log"
for e in 9x275 9x130; do
  uv run scripts/468_crystal_f3.py "$RECO/$EXP/D6s_$e" --tag "$EXP-D6s_$e" > "$LOGS/468-$EXP-D6s_$e.log" 2>&1 || foul=1
  tail -1 "$LOGS/468-$EXP-D6s_$e.log"
done
if [ -n "$PATCH" ]; then
  uv run scripts/460_fair_play.py "configs/experiments/$EXP.yaml" --tree submodules/EICrecon --tag "$EXP-tree" \
    > "$LOGS/460-$EXP-tree.log" 2>&1 || foul=1
  tail -1 "$LOGS/460-$EXP-tree.log"
  uv run scripts/465_patch_scan.py "$PATCH" --tag "$EXP" || foul=1
fi
for e in 9x275 9x130; do
  uv run scripts/210_msf_lambda_regimes.py "D6s_$e" --row "$EXP" > "$LOGS/210-$EXP-D6s_$e.log" 2>&1 &
done
wait
grep -h "^$EXP: N_found\|MISMATCH\|Traceback" "$LOGS"/210-"$EXP"-D6s_*.log
uv run scripts/463_msf_select.py "$BEST" "$EXP" | tail -4
uv run scripts/476_msf_t_resolution.py "$EXP" > "$LOGS/476-$EXP.log" 2>&1
grep -A1 "^$EXP" "$LOGS/476-$EXP.log" | grep "σ68" | sed "s/^/  −t: /"
[ "$foul" -eq 1 ] && echo "FAIR PLAY FAIL: the verdict is FOUL whatever 463 says"
exit 0
