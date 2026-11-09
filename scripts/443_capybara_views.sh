#!/usr/bin/env bash
# The capybara views of one experiment against a reference (D-user-22: the
# comparison the EICrecon reviewers know, made visible per checkpoint):
#   nonowned  every collection outside the ZDC-owned list, relation branches
#             included (podio names them _<collection>_<relation>); capybara
#             prints a leaf only when the two inputs differ, so the view must
#             print none: the proof that no other calorimeter moved;
#   zdc       the owned collections only: what the experiment changed.
# Runs capybara bara (submodules/epic-capybara through uvx, as 130 does) on one
# chunk per D5 sample. Reports (Bokeh HTML + one json.gz per leaf) go under
# {data}/capybara/<exp>-vs-<ref>/<dataset>/<view>/; the summary (leaves reported,
# leaves differing, leaves below p = 1, the collections they belong to) goes to
# space/perf/capybara-<exp>-vs-<ref>.json. The non-owned view fails when any leaf
# differs or when no leaf was reported (a broken run is not a clean gate).
#
# Usage: scripts/443_capybara_views.sh <experiment> [--reference R0_stock] [--chunk chunk000]
#        [--datasets D5_dis_minq2_100,D5_dis_minq2_0]
set -uo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROFILE=${ZDC_CONFIG:-$REPO/configs/local.yaml}
yaml_get() { sed -n "s/^$1:[[:space:]]*\([^#]*\).*/\1/p" "$PROFILE" | sed 's/[[:space:]]*$//' | head -1; }
DATA_ROOT=$(yaml_get data_root); RECO=$DATA_ROOT/reco
EXP=${1:?usage: $0 <experiment> [--reference R] [--chunk C] [--datasets a,b]}; shift
REF=R0_stock; CHUNK=chunk000; DS="D5_dis_minq2_100,D5_dis_minq2_0"
while [ $# -gt 0 ]; do case "$1" in --reference) REF=$2; shift 2;; --chunk) CHUNK=$2; shift 2;; --datasets) DS=$2; shift 2;; *) echo "unknown $1" >&2; exit 2;; esac; done
# The owned prefixes of configs/metrics.yaml as one regex (capybara matches collection names).
OWNED=$(sed -n '/^zdc_owned_prefixes:/,/^[^ -]/p' "$REPO/configs/metrics.yaml" | sed -n 's/^  - \([A-Za-z0-9]*\).*/\1/p' | paste -sd'|')
[ -n "$OWNED" ] || { echo "no zdc_owned_prefixes in configs/metrics.yaml" >&2; exit 3; }
OUT=$DATA_ROOT/capybara/$EXP-vs-$REF; mkdir -p "$OUT"
SUMMARY=$REPO/space/perf/capybara-$EXP-vs-$REF.json
CAPY=(uvx --python 3.12 --from "$REPO/submodules/epic-capybara" capybara bara)
IFS=, read -ra WANT <<< "$DS"
echo "{" > "$SUMMARY.tmp"; first=1; fails=0
for ds in "${WANT[@]}"; do
  ref=$RECO/$REF/$ds/${ds}_$CHUNK.edm4eic.root; new=$RECO/$EXP/$ds/${ds}_$CHUNK.edm4eic.root
  [ -s "$ref" ] && [ -s "$new" ] || { echo "missing $ref or $new" >&2; fails=$((fails+1)); continue; }
  for view in nonowned zdc; do
    dir=$OUT/$ds/$view; rm -rf "$dir"; mkdir -p "$dir"
    if [ "$view" = nonowned ]; then flag=(-M "^_?($OWNED)"); else flag=(-m "^_?($OWNED)"); fi
    ( cd "$dir" && "${CAPY[@]}" "${flag[@]}" "$ref" "$new" > capybara.log 2>&1 ); rc=$?
    # capybara writes one json.gz per leaf it compared and prints "<leaf>\np_KS = x p_AD = y" only for a
    # leaf whose two inputs differ (bara.py: shape, per-event counts or any value).
    reported=$(ls "$dir/capybara-reports" 2>/dev/null | grep -c '\.json\.gz$')
    differing=$(grep -c "^p_KS" "$dir/capybara.log"); below=$(awk '/^p_KS/ && $3+0 < 0.9995' "$dir/capybara.log" | wc -l)
    moved=$(awk '/^p_KS/ {print prev} !/^p_KS/ && !/^\[/ && !/^(failed to validate|String value|Bool value|Skipping|Installed)/ {prev=$0}' "$dir/capybara.log" \
            | sed 's/\..*$//; s/_[^_]*$//; s/^_//' | sort | uniq -c | sort -rn | head -20 | awk '{printf "%s\"%s\": %d", (n++?", ":""), $2, $1}')
    [ $first -eq 1 ] || echo "," >> "$SUMMARY.tmp"; first=0
    printf '"%s/%s": {"rc": %d, "leaves_reported": %d, "leaves_differing": %d, "leaves_below_p1": %d, "collections_differing": {%s}, "report": "%s"}' \
      "$ds" "$view" "$rc" "$reported" "$differing" "$below" "$moved" "$dir" >> "$SUMMARY.tmp"
    echo "$ds $view: $reported leaves reported, $differing differing, $below below p=1 (rc $rc) -> $dir"
    if [ "$view" = nonowned ] && { [ "$differing" -ne 0 ] || [ "$reported" -eq 0 ]; }; then fails=$((fails+1)); fi
  done
done
echo "}" >> "$SUMMARY.tmp"; mv "$SUMMARY.tmp" "$SUMMARY"
echo "summary $SUMMARY; $fails failure(s)"
[ "$fails" -eq 0 ]
