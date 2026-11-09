#!/usr/bin/env bash
# Phase 0 item 9 (switch tests) and the item 8 R1 equivalence, on the first N events of
# one gun file per dataset, all single-threaded.
#
# Switch tests: each PR 3064 parameter alone on the R0 install, at its PR value, against an R0
# baseline of the same events; the ZDC output must differ (130_compare_collections.py --zdc
# must FAIL). eicrecon aborts on an unregistered name (strictness 2), so this catches the
# registered-but-inert ones.
#
# Equivalence: the R1 build (the PR's three-file diff) against the dist0p3 build (only the
# PR's XY distances, space/notes/patches/dist0p3.patch) plus the six PR parameters: every ZDC
# collection must be identical (--zdc PASS). This is "R1 from the patched build and R1 from
# the parameter config agree", with the distances supplied by the only build that can.
#
# Outputs: {data}/switch-tests/<name>.edm4eic.root, logs under {data}/logs/switch-tests/,
# verdicts in space/perf/switch-tests.json.
#
# Usage: scripts/133_switch_tests.sh [--events N] [--jobs J]
set -uo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROFILE=${ZDC_CONFIG:-$REPO/configs/local.yaml}
yaml_get() { sed -n "s/^$1:[[:space:]]*\([^#]*\).*/\1/p" "$PROFILE" | sed 's/[[:space:]]*$//' | head -1; }
DATA_ROOT=$(yaml_get data_root); OUT=$DATA_ROOT/switch-tests; LOGS=$DATA_ROOT/logs/switch-tests
DS=$DATA_ROOT/datasets; INST=$DATA_ROOT/install
EVENTS=300; JOBS=2
while [ $# -gt 0 ]; do case "$1" in --events) EVENTS=$2; shift 2;; --jobs) JOBS=$2; shift 2;;
  -h|--help) sed -n '2,18p' "$0"; exit 0;; *) echo "unknown option $1" >&2; exit 2;; esac; done
mkdir -p "$OUT" "$LOGS"
GATE="uv run --project $REPO $REPO/scripts/130_compare_collections.py"

D1=$DS/D1_pi0/D1_pi0_100GeV_seed1.edm4hep.root
D2=$DS/D2_photon/D2_photon_100GeV_seed1.edm4hep.root
D3=$DS/D3_neutron/D3_neutron_100GeV_seed1.edm4hep.root
D4=$DS/D4_lambda/D4_lambda_175GeV_seed1.edm4hep.root
P_NLR="-PZDC:HcalFarForwardZDCImagingProtoClusters:neighbourLayersRange=3"
P_MCE="-PZDC:HcalFarForwardZDCImagingProtoClusters:minClusterCenterEdep=0.005"
P_MNH="-PZDC:HcalFarForwardZDCImagingProtoClusters:minClusterNhits=2"
P_NSC="-Preco:ReconstructedFarForwardNeutrals:neutronScaleCorrCoeffHcalZDC=16.65,0.66"
P_GSC="-Preco:ReconstructedFarForwardNeutrals:gammaScaleCorrCoeffHcalZDC=2.7,1.27"
P_GML="-Preco:ReconstructedFarForwardNeutrals:gammaMaxLength=150"
ALL6="$P_NLR $P_MCE $P_MNH $P_NSC $P_GSC $P_GML"

reco() { # reco <name> <install label> <input> [extra -P flags]
  local name=$1 inst=$2 input=$3; shift 3
  [ -s "$OUT/$name.edm4eic.root" ] && return 0
  rm -f "$OUT/$name.part.edm4eic.root"
  EICRECON_INSTALL=$INST/eicrecon-$inst "$REPO/scripts/100_in_container.sh" bash -c \
    "export DETECTOR_CONFIG=epic_craterlake; eicrecon -Pnthreads=1 -Pjana:nevents=$EVENTS -Ppodio:output_collections=.* $* -Ppodio:output_file=$OUT/$name.part.edm4eic.root $input && mv $OUT/$name.part.edm4eic.root $OUT/$name.edm4eic.root" \
    > "$LOGS/$name.log" 2>&1 || { echo "reconstruction $name failed (log $LOGS/$name.log)"; rm -f "$OUT/$name.part.edm4eic.root"; return 1; }
}

R0=e5e2a60c60b6
# name | install | input | flags
RUNS=(
  "base_D1|$R0|$D1|"  "base_D2|$R0|$D2|"  "base_D3|$R0|$D3|"
  "nlr_D1|$R0|$D1|$P_NLR"  "mce_D1|$R0|$D1|$P_MCE"  "mnh_D1|$R0|$D1|$P_MNH"
  "gsc_D2|$R0|$D2|$P_GSC"  "gml_D2|$R0|$D2|$P_GML"  "gml_D3|$R0|$D3|$P_GML"  "nsc_D3|$R0|$D3|$P_NSC"
  "R1_D1|R1|$D1|"  "dist6_D1|dist0p3|$D1|$ALL6"
  "R1_D4|R1|$D4|"  "dist6_D4|dist0p3|$D4|$ALL6"
  # On R0 clustering no photon is ever tagged (both transverse widths above gammaMaxWidth = 12 mm), so the
  # γ parameters cannot act there; R1's clustering tags photons, so they are switched back to stock on R1.
  "R1_D2|R1|$D2|"  "r1gsc_D2|R1|$D2|-Preco:ReconstructedFarForwardNeutrals:gammaScaleCorrCoeffHcalZDC=1.1,0.98"
  "r1gml_D2|R1|$D2|-Preco:ReconstructedFarForwardNeutrals:gammaMaxLength=100"
  "r1mnh_D1|R1|$D1|-PZDC:HcalFarForwardZDCImagingProtoClusters:minClusterNhits=10"
)
echo "$(date -Is) ${#RUNS[@]} reconstructions of $EVENTS events, $JOBS parallel, into $OUT"
running=0
for r in "${RUNS[@]}"; do
  IFS='|' read -r name inst input flags <<< "$r"
  reco "$name" "$inst" "$input" $flags &
  running=$((running+1)); if [ "$running" -ge "$JOBS" ]; then wait -n; running=$((running-1)); fi
done
wait

results=()
verdict() { # verdict <want PASS|FAIL> <label> <a> <b>   (--zdc comparison)
  local want=$1 label=$2 a=$OUT/$3.edm4eic.root b=$OUT/$4.edm4eic.root got out
  if [ ! -s "$a" ] || [ ! -s "$b" ]; then got=MISSING; out="output missing"
  elif out=$($GATE "$a" "$b" --zdc 2>&1); then got=PASS; else got=FAIL; fi
  local ok=BROKEN; [ "$got" = "$want" ] && ok=OK
  echo "$ok $label: --zdc $got (want $want) — $(echo "$out" | tail -1)"
  results+=("{\"test\": \"$label\", \"want\": \"$want\", \"got\": \"$got\", \"ok\": $([ $ok = OK ] && echo true || echo false), \"last_line\": $(echo "$out" | tail -1 | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}")
}
verdict FAIL "neighbourLayersRange 1->3 on D1"           base_D1 nlr_D1
verdict FAIL "minClusterCenterEdep 25->5 MeV on D1"      base_D1 mce_D1
verdict FAIL "minClusterNhits 10->2 on D1"               base_D1 mnh_D1
verdict FAIL "gammaScaleCorrCoeffHcalZDC on D2"          base_D2 gsc_D2
verdict FAIL "gammaMaxLength 100->150 on D2"             base_D2 gml_D2
verdict FAIL "gammaMaxLength 100->150 on D3"             base_D3 gml_D3
verdict FAIL "neutronScaleCorrCoeffHcalZDC on D3"        base_D3 nsc_D3
verdict FAIL "gammaScaleCorrCoeffHcalZDC PR->stock on R1, D2" R1_D2 r1gsc_D2
verdict FAIL "gammaMaxLength 150->100 on R1, D2"         R1_D2 r1gml_D2
verdict FAIL "minClusterNhits 2->10 on R1, D1"           R1_D1 r1mnh_D1
verdict PASS "R1 build == dist0p3 build + six PR parameters, D1" R1_D1 dist6_D1
verdict PASS "R1 build == dist0p3 build + six PR parameters, D4" R1_D4 dist6_D4
{ echo "{\"events\": $EVENTS, \"written\": \"$(date -Is)\", \"results\": ["; (IFS=,; echo "${results[*]}"); echo "]}"; } \
  | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin), indent=1))' > "$REPO/space/perf/switch-tests.json"
echo "verdicts in $REPO/space/perf/switch-tests.json"
