#!/usr/bin/env bash
# Fetch the DIS guard inputs D5 (configs/datasets.yaml, section dis): official
# campaign FULL (DD4hep) files from JLab XRootD, enough files to reach
# min_events per sample, into {datasets_root}/<sample>/. Lists the newest
# campaign that has the sample paths when `campaign` is empty in the config.
#
# Usage:
#   scripts/111_fetch_dis_inputs.sh --list                 # campaigns and file counts, fetch nothing
#   scripts/111_fetch_dis_inputs.sh --campaign 26.10.0     # fetch for one campaign
#   scripts/111_fetch_dis_inputs.sh                        # use `campaign` from the config
#
# Runs xrdfs/xrdcp inside the image (the host client may be too old; JLab needs
# xrootd >= 5.9). If no campaign has the paths, the fallback is npsim of the
# EVGEN files the EICrecon CI uses: the paths are in
# submodules/EICrecon/.github/workflows/linux-eic-shell.yml (jobs npsim-dis and
# npsim-dis-nc); write them into the config and run with --simulate (not
# implemented here on purpose: it is a Step 0 decision, D-default, before code).
set -euo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROFILE=${ZDC_CONFIG:-$REPO/configs/local.yaml}
yaml_get() { sed -n "s/^$1:[[:space:]]*\([^#]*\).*/\1/p" "$PROFILE" | sed 's/[[:space:]]*$//' | head -1; }
DATA_ROOT=$(yaml_get data_root); DATASETS=$DATA_ROOT/datasets; LOGS=$DATA_ROOT/logs
CFG=$REPO/configs/datasets.yaml
BASE=$(sed -n 's/^  xrootd_base:[[:space:]]*\([^#]*\).*/\1/p' "$CFG" | tr -d ' ')
CAMPAIGN=$(sed -n 's/^  campaign:[[:space:]]*"\{0,1\}\([^"#]*\)"\{0,1\}.*/\1/p' "$CFG" | tr -d ' ')
MODE=fetch
while [ $# -gt 0 ]; do case "$1" in --list) MODE=list; shift;; --campaign) CAMPAIGN=$2; shift 2;; -h|--help) sed -n '2,18p' "$0"; exit 0;; *) echo "unknown $1" >&2; exit 2;; esac; done
mkdir -p "$DATASETS" "$LOGS"
HOST=${BASE#root://}; HOST=${HOST%%/*}; ROOTDIR=/${BASE#*//}; ROOTDIR=${ROOTDIR#/}; ROOTDIR=/${ROOTDIR#*/}

# The sample paths, with {campaign} substituted; python keeps the YAML parsing honest.
samples() { uv run --project "$REPO" python -c "
import yaml,sys; c=yaml.safe_load(open('$CFG'))['dis']
for k,v in c['samples'].items(): print(k, v['path'].format(campaign='$1'), v['min_events'])"; }

if [ "$MODE" = list ]; then
  echo "campaigns under $BASE:"
  "$REPO/scripts/100_in_container.sh" xrdfs "$HOST" ls "$ROOTDIR" | sed 's|.*/||' | sort -V | tail -15
  for c in $("$REPO/scripts/100_in_container.sh" xrdfs "$HOST" ls "$ROOTDIR" | sed 's|.*/||' | sort -V | tail -6); do
    samples "$c" | while read -r id path minev; do
      n=$("$REPO/scripts/100_in_container.sh" xrdfs "$HOST" ls "$ROOTDIR/$path" 2>/dev/null | grep -c edm4hep || true)
      echo "  $c  $id  $n file(s)"
    done
  done
  exit 0
fi
[ -n "$CAMPAIGN" ] || { echo "ERROR: no campaign: run --list and pass --campaign <tag> (then write it into configs/datasets.yaml)" >&2; exit 2; }

samples "$CAMPAIGN" | while read -r id path minev; do
  out=$DATASETS/$id; mkdir -p "$out"
  echo "== $id: $ROOTDIR/$path -> $out (>= $minev events)"
  files=$("$REPO/scripts/100_in_container.sh" xrdfs "$HOST" ls "$ROOTDIR/$path" | grep edm4hep | sort | head -20)
  [ -n "$files" ] || { echo "ERROR: no files at $ROOTDIR/$path for campaign $CAMPAIGN" >&2; exit 1; }
  got=0
  for f in $files; do
    name=$(basename "$f")
    [ -s "$out/$name" ] || "$REPO/scripts/100_in_container.sh" xrdcp --silent "root://$HOST/$f" "/data/zdc-autoresearch/datasets/$id/$name" >> "$LOGS/fetch-$id.log" 2>&1 || { echo "xrdcp failed for $f (see $LOGS/fetch-$id.log)"; continue; }
    n=$(uv run --project "$REPO" python -c "import uproot;print(uproot.open('$out/$name')['events'].num_entries)")
    got=$((got+n)); echo "  $name: $n events (total $got)"
    [ "$got" -ge "$minev" ] && break
  done
  [ "$got" -ge "$minev" ] || { echo "ERROR: only $got events for $id, need $minev" >&2; exit 1; }
done
uv run --project "$REPO" "$REPO/scripts/121_manifest.py" write "$REPO/space/perf/manifest-datasets.json" $(samples "$CAMPAIGN" | awk -v d="$DATASETS" '{print d"/"$1}') --section dis
echo "done; write campaign: \"$CAMPAIGN\" into configs/datasets.yaml if it is not there yet"
