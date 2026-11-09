#!/usr/bin/env bash
# Score one Phase 5 try after its reconstruction (zdc-autoresearch-loop-v5.md, the experiment loop):
#   460 on the MSF outputs (F1-F3; F2b against the base row's raw hits), and for a code try 460 --tree and 465 on its
#   patch; then 210 on both search halves and 463 against the current best. Prints one summary line per step and the
#   verdict (FOUL when any fair-play step FAILs). Nothing is launched or deleted.
#
# Usage: scripts/466_phase5_score.sh <experiment> <current best> [<patch>]
#   scripts/466_phase5_score.sh Y1_b0_split MSF5_X9
#   scripts/466_phase5_score.sh Y2_vertex_lever_arm MSF5_X9 space/notes/patches/Y2_vertex_lever_arm.patch
set -uo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd); cd "$REPO"
EXP=$1; BEST=$2; PATCH=${3:-}
RECO=/data/zdc-autoresearch/reco; LOGS=/data/zdc-autoresearch/logs/phase5; mkdir -p "$LOGS"
foul=0
uv run scripts/460_fair_play.py "configs/experiments/$EXP.yaml" --reco-dir "$RECO/$EXP/D6s_9x275" \
  --reference-dir "$RECO/MSF5_X9/D6s_9x275" --tag "$EXP-msf" > "$LOGS/460-$EXP-msf.log" 2>&1 || foul=1
tail -1 "$LOGS/460-$EXP-msf.log"
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
[ "$foul" -eq 1 ] && echo "FAIR PLAY FAIL: the verdict is FOUL whatever 463 says"
exit 0
