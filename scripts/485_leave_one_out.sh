#!/usr/bin/env bash
# Leave-one-out ranking on a reference row (after the Phase 6 close, 2026-11-09): for each config in turn, reconstruct
# the MSF search halves D6s (300 --lean, 4 jobs, D-user-35: one config at a time), score both halves (210) and pair
# the Λ against the reference (463). Each config is the reference with one change switched off, so in 463's output
# b = Λ found only WITH the change (the reference), c = Λ found only WITHOUT it; 463's verdict words do not apply.
# An integrity failure in 300 (e.g. a smaller output on stock clustering) does not stop the scoring: the outputs are
# there, and 210 reads them. The summary is 486.
#
# Usage: scripts/485_leave_one_out.sh Z8_hcal_axis_law configs/experiments/AB7_no_core_split.yaml ... > log 2>&1
set -u
REF=$1; shift
cd "$(dirname "$0")/.."
for cfg in "$@"; do
  name=$(sed -n 's/^name: *//p' "$cfg")
  echo "=== $name start $(date -u +%FT%H:%MZ)"
  uv run scripts/300_run_experiment.py "$cfg" --phase ablation --lean --reference "$REF" \
      --datasets D6s_9x275 D6s_9x130 --jobs 4 \
    || echo "=== $name: 300 exited non-zero (see its log); scoring the outputs that exist"
  for ds in D6s_9x275 D6s_9x130; do
    uv run scripts/210_msf_lambda_regimes.py "$ds" --row "$name" > /dev/null || echo "=== $name: 210 $ds failed"
  done
  uv run scripts/463_msf_select.py "$REF" "$name" || echo "=== $name: 463 failed"
  echo "=== $name done $(date -u +%FT%H:%MZ)"
done
echo "=== ALL DONE $(date -u +%FT%H:%MZ)"
