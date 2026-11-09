#!/usr/bin/env bash
# Prove that the G4 gate (scripts/130_compare_collections.py) can fail, and keep
# the control outputs so every run start can re-check the verdicts without a
# reconstruction (loop file, Every run).
#
# The controls are real single-threaded reconstructions of the first N events of
# one full-detector input (default: the first D6a file), all with the R0 install:
#   reference.edm4eic.root   R0, stock parameters
#   repeat.edm4eic.root      R0 again                                   -> G4 PASS and --zdc PASS (determinism)
#   nonzdc.edm4eic.root      a non-ZDC parameter changed (EEMC-N hit threshold)  -> G4 must FAIL
#   zdc.edm4eic.root         a ZDC parameter changed (ZDC minClusterNhits)       -> G4 must PASS, --zdc must FAIL
# capybara (epic-capybara) runs on reference vs nonzdc and must name a non-ZDC collection.
# A gate that has only ever printed PASS proves nothing; this script is how it is seen to fail.
#
# Usage:
#   scripts/131_prove_gates.sh [--input FILE] [--events N]   # Phase 0 item 10: make the controls and prove the verdicts
#   scripts/131_prove_gates.sh --check                       # every run: re-run the gate on the stored controls
set -euo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROFILE=${ZDC_CONFIG:-$REPO/configs/local.yaml}
yaml_get() { sed -n "s/^$1:[[:space:]]*\([^#]*\).*/\1/p" "$PROFILE" | sed 's/[[:space:]]*$//' | head -1; }
DATA_ROOT=$(yaml_get data_root); CTRL=$DATA_ROOT/gate-controls; LOGS=$DATA_ROOT/logs/gate-controls
INSTALL=$DATA_ROOT/install/eicrecon-e5e2a60c60b6
INPUT=$(ls "$DATA_ROOT"/datasets/D6a_local/*.edm4hep.root 2>/dev/null | head -1 || true)
DETECTOR_CONFIG=epic_craterlake_9x130
EVENTS=300
NONZDC_PARAM="-PEEMC:EcalEndcapNRecHits:thresholdValue=40.0"                 # stock 4.0 ADC counts
ZDC_PARAM="-PZDC:HcalFarForwardZDCImagingProtoClusters:minClusterHitEdep=0.003"   # GeV; stock 315 keV: changes which hits join every cluster
# (minClusterNhits=40 changed nothing: the MSF ZDC clusters have a median of 488 hits)
GATE="uv run --project $REPO $REPO/scripts/130_compare_collections.py"
MODE=make
while [ $# -gt 0 ]; do case "$1" in
  --check) MODE=check; shift;; --input) INPUT=$2; shift 2;; --events) EVENTS=$2; shift 2;;
  -h|--help) sed -n '2,19p' "$0"; exit 0;; *) echo "unknown option $1" >&2; exit 2;; esac; done

fails=0
expect() { # expect <PASS|FAIL> <label> <gate args...>
  local want=$1 label=$2; shift 2
  local out; if out=$($GATE "$@" 2>&1); then got=PASS; else got=FAIL; fi
  if [ "$got" = "$want" ]; then echo "OK     $label -> $got (expected): $(echo "$out" | tail -1)"
  else echo "BROKEN $label -> $got, expected $want: $(echo "$out" | tail -3)"; fails=$((fails+1)); fi
}

reco() { # reco <name> [extra -P flags]
  local name=$1; shift
  [ -s "$CTRL/$name.edm4eic.root" ] && return 0
  EICRECON_INSTALL=$INSTALL "$REPO/scripts/100_in_container.sh" bash -c \
    "export DETECTOR_CONFIG=$DETECTOR_CONFIG; eicrecon -Pnthreads=1 -Pjana:nevents=$EVENTS -Ppodio:output_collections=.* $* -Ppodio:output_file=$CTRL/$name.part.edm4eic.root $INPUT && mv $CTRL/$name.part.edm4eic.root $CTRL/$name.edm4eic.root" \
    > "$LOGS/$name.log" 2>&1 || { echo "reconstruction $name failed (log $LOGS/$name.log)"; exit 1; }
}

if [ "$MODE" = make ]; then
  [ -n "$INPUT" ] && [ -f "$INPUT" ] || { echo "no input file (pass --input)"; exit 1; }
  mkdir -p "$CTRL" "$LOGS"
  echo "controls from $INPUT, first $EVENTS events, under $CTRL"
  reco reference & reco repeat & reco nonzdc "$NONZDC_PARAM" & reco zdc "$ZDC_PARAM" & wait
  printf '{"input": "%s", "events": %s, "detector_config": "%s", "install": "%s", "nonzdc_param": "%s", "zdc_param": "%s"}\n' \
    "$INPUT" "$EVENTS" "$DETECTOR_CONFIG" "$INSTALL" "$NONZDC_PARAM" "$ZDC_PARAM" > "$CTRL/controls.json"
else
  [ -f "$CTRL/controls.json" ] || { echo "no controls yet: run Phase 0 item 10 first"; exit 1; }
fi

R=$CTRL/reference.edm4eic.root
expect PASS "R0 twice (determinism), non-ZDC"   "$R" "$CTRL/repeat.edm4eic.root"
expect PASS "R0 twice (determinism), ZDC"       "$R" "$CTRL/repeat.edm4eic.root" --zdc
expect FAIL "non-ZDC parameter changed"         "$R" "$CTRL/nonzdc.edm4eic.root"
expect PASS "ZDC parameter changed (G4 ignores ZDC)" "$R" "$CTRL/zdc.edm4eic.root"
expect FAIL "ZDC parameter changed, --zdc"      "$R" "$CTRL/zdc.edm4eic.root" --zdc
if [ "$MODE" = make ]; then
  # capybara must see the non-ZDC damage too: the CI's own comparison tool on the same pair
  $GATE "$R" "$CTRL/nonzdc.edm4eic.root" --capybara "$CTRL/capybara-nonzdc" >/dev/null 2>&1 || true
  if grep -rqE "EcalEndcapN" "$CTRL/capybara-nonzdc" 2>/dev/null; then echo "OK     capybara names EcalEndcapN collections in reference vs nonzdc"
  else echo "BROKEN capybara report does not name EcalEndcapN (see $CTRL/capybara-nonzdc/capybara.log)"; fails=$((fails+1)); fi
fi
echo "---- $fails broken control(s)"
[ "$fails" -eq 0 ]
