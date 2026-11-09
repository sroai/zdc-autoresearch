#!/usr/bin/env bash
# D6a: register the local MSF DD4hep files (configs/datasets.yaml, msf.D6a_local)
# as a dataset: link them under {datasets_root}/D6a_local/, verify each opens and
# holds the campaign's 1000 events (truncated campaign files look normal-sized),
# and add them to the manifest. Nothing is copied; the links point at the
# campaign copy under /data/meson-structure-2026-07.
#
# Usage: scripts/112_msf_sample.sh [--max-files N] [--skip N] [--src DIR --id DATASET_ID] [--events N]
#   default: the profile's msf_local_dd4hep as D6a_local; e.g. --src /data/zdc-autoresearch/msf-9x275/dd4hep --id D6a_9x275
#   --events: the events a complete file holds (default 1000; campaign 2026-11 files hold 500, D6c_*)
#   --skip: leave out the first N files of the sorted list (Phase 5 held-out halves: --skip 40 --max-files 40)
set -euo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROFILE=${ZDC_CONFIG:-$REPO/configs/local.yaml}
yaml_get() { sed -n "s/^$1:[[:space:]]*\([^#]*\).*/\1/p" "$PROFILE" | sed 's/[[:space:]]*$//' | head -1; }
DATA_ROOT=$(yaml_get data_root); SRC=$(yaml_get msf_local_dd4hep)
MAX=1000; SKIP=0; ID=D6a_local; EVENTS=1000
while [ $# -gt 0 ]; do case "$1" in --max-files) MAX=$2; shift 2;; --src) SRC=$2; shift 2;; --id) ID=$2; shift 2;; --events) EVENTS=$2; shift 2;; --skip) SKIP=$2; shift 2;; *) echo "unknown $1" >&2; exit 2;; esac; done
OUT=$DATA_ROOT/datasets/$ID; mkdir -p "$OUT"
[ -d "$SRC" ] || { echo "ERROR: $SRC does not exist (msf_local_dd4hep in $PROFILE)" >&2; exit 1; }
n=0; bad=0
for f in $(ls "$SRC"/*.edm4hep.root | sort | tail -n +"$((SKIP + 1))" | head -n "$MAX"); do
  name=$(basename "$f")
  events=$(uv run --project "$REPO" python -c "
import uproot
try: print(uproot.open('$f')['events'].num_entries)
except Exception as e: print('ERR', e)")
  if [ "$events" = "$EVENTS" ]; then ln -sfn "$f" "$OUT/$name"; n=$((n+1)); echo "ok   $name ($events events)"
  else echo "SKIP $name ($events) — not the campaign's $EVENTS events; a finding if it is a campaign file"; bad=$((bad+1)); fi
done
echo "$n file(s) registered, $bad skipped, in $OUT"
[ "$n" -gt 0 ] || exit 1
uv run --project "$REPO" "$REPO/scripts/121_manifest.py" write "$REPO/space/perf/manifest-datasets.json" "$OUT" --section "msf-$ID" --follow-links
echo "NOTE: confirm the campaign's detector configuration from submodules/meson-structure/simulation-pipeline/configs (datasets.yaml msf.D6a_local.detector_config)"
