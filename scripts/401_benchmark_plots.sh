#!/usr/bin/env bash
# Run the detector_benchmarks ZDC plot scripts (the plots the reviewers know) on
# one experiment's reconstruction outputs.
#
# The benchmark scripts read fixed paths
# (sim_output/zdc_<x>/<config>_rec_<x>_<p>GeV_<i>.edm4eic.root) and write into a
# results dir, so this script builds that layout from symlinks under
# {data}/benchmark-layout/<experiment>/ and runs each script inside the pinned
# image (they need uproot/mplhep/ROOT from the image). Plots end up under
# {space}/plots/<phase>/<experiment>/benchmarks/<benchmark>/.
#
# Usage: scripts/401_benchmark_plots.sh <experiment> --phase <phaseN> [--only zdc_pi0,zdc_lambda]
#
# Mapping dataset -> benchmark: D1_pi0 -> zdc_pi0, D4_lambda -> zdc_lambda,
# D2_photon -> zdc_photon, D3_neutron -> zdc_neutron (ROOT macro). The benchmark
# scripts expect 5 index files per momentum; ours are one file per momentum and
# seed, linked as index 0 (and the seed-2 twin as index 1); the scripts
# concatenate whatever exists. Momenta that the benchmark hardcodes but the
# dataset lacks make the script skip them (they check for < 25 entries).
set -uo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROFILE=${ZDC_CONFIG:-$REPO/configs/local.yaml}
yaml_get() { sed -n "s/^$1:[[:space:]]*\([^#]*\).*/\1/p" "$PROFILE" | sed 's/[[:space:]]*$//' | head -1; }
DATA_ROOT=$(yaml_get data_root); RECO=$DATA_ROOT/reco
EXP=${1:?usage: $0 <experiment> --phase <phase> [--only a,b]}; shift
PHASE=""; ONLY="zdc_pi0,zdc_lambda,zdc_photon,zdc_neutron"
while [ $# -gt 0 ]; do case "$1" in --phase) PHASE=$2; shift 2;; --only) ONLY=$2; shift 2;; *) echo "unknown $1" >&2; exit 2;; esac; done
[ -n "$PHASE" ] || { echo "--phase required" >&2; exit 2; }
CONFIG=$(sed -n "s/^detector_config_guns:[[:space:]]*\([^#]*\).*/\1/p" "$REPO/configs/datasets.yaml" | tr -d " ")   # a label in the layout path only
LAYOUT=$DATA_ROOT/benchmark-layout/$EXP; rm -rf "$LAYOUT"; mkdir -p "$LAYOUT"
PLOTS=$REPO/space/plots/$PHASE/$EXP/benchmarks; mkdir -p "$PLOTS"
BENCH=$REPO/scripts/700_benchmarks   # copies with EICrecon main collection names (README there)

link_dataset() { # link_dataset <dataset> <benchmark> <stem>   e.g. D1_pi0 zdc_pi0 zdc_pi0 ; D4_lambda zdc_lambda lambda_dec
  local ds=$1 bench=$2 stem=$3 dir="$LAYOUT/sim_output/$2"; mkdir -p "$dir"
  for f in "$RECO/$EXP/$ds"/*.edm4eic.root; do
    [ -e "$f" ] || continue
    p=$(basename "$f" | sed -n 's/.*_\([0-9]*\)GeV_seed\([0-9]*\).*/\1/p'); s=$(basename "$f" | sed -n 's/.*GeV_seed\([0-9]*\).*/\1/p')
    ln -sfn "$f" "$dir/${CONFIG}_rec_${stem}_${p}GeV_$((s-1)).edm4eic.root"
  done
}
IFS=, read -ra WANT <<< "$ONLY"
for b in "${WANT[@]}"; do
  case "$b" in
    zdc_pi0)     link_dataset D1_pi0 zdc_pi0 zdc_pi0;       script="python $BENCH/zdc_pi0_plots.py";;
    zdc_lambda)  link_dataset D4_lambda zdc_lambda lambda_dec; script="python $BENCH/lambda_plots.py";;
    zdc_photon)  link_dataset D2_photon zdc_photon zdc_photon; script="python $BENCH/zdc_photon_plots.py";;
    zdc_neutron) link_dataset D3_neutron zdc_neutron zdc_neutron; script="root -l -b -q '$BENCH/fwd_neutrons_recon.C'";;
    *) echo "unknown benchmark $b"; continue;;
  esac
  out="$LAYOUT/results/$CONFIG/$b"; mkdir -p "$out"
  # The plot scripts derive the detector config from the results path (outdir.split("/")[1]) and read
  # sim_output/ relative to the cwd, so run them from the layout dir, with repo paths translated.
  script_c=$(echo "$script" | sed "s|$REPO|/work|g")
  ( cd "$LAYOUT" && "$REPO/scripts/100_in_container.sh" bash -c "cd $(echo "$LAYOUT" | sed "s|$DATA_ROOT|/data|") && $script_c results/$CONFIG/$b" ) > "$PLOTS/$b.log" 2>&1 \
    && { mkdir -p "$PLOTS/$b"; cp "$out"/* "$PLOTS/$b/" 2>/dev/null; echo "ok   $b -> $PLOTS/$b ($(ls "$PLOTS/$b" | wc -l) files)"; } \
    || echo "FAIL $b (log $PLOTS/$b.log)"
done
