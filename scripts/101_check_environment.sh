#!/usr/bin/env bash
# The every-run check (loop file, section Every run): image present and its
# digest recorded, submodules at their pins, the ZDC-only detector configuration
# inside the image, the dataset manifest and the reference checksums intact.
# Prints one line per check with OK / FAIL / SKIP and exits non-zero on any FAIL.
#
# Usage: scripts/101_check_environment.sh [--record-digest]
#   --record-digest   write the image digest into zdc-setup.md (Phase 0, Step 0 item 1)
set -uo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROFILE=${ZDC_CONFIG:-$REPO/configs/local.yaml}
yaml_get() { sed -n "s/^$1:[[:space:]]*\([^#]*\).*/\1/p" "$PROFILE" | sed 's/[[:space:]]*$//' | head -1; }
IMAGE=$(yaml_get image); DATA_ROOT=$(yaml_get data_root)
fails=0
ok()   { echo "OK   $*"; }
fail() { echo "FAIL $*"; fails=$((fails+1)); }
skip() { echo "SKIP $*"; }

# 1. tools on the host
for tool in docker uv gh git; do command -v $tool >/dev/null && ok "$tool present" || fail "$tool missing"; done

# 2. the image and its digest
if docker image inspect "$IMAGE" >/dev/null 2>&1; then
  DIGEST=$(docker image inspect "$IMAGE" --format '{{index .RepoDigests 0}}' 2>/dev/null)
  ok "image $IMAGE ($DIGEST)"
  if [ "${1:-}" = "--record-digest" ]; then
    sed -i "s|(digest: \*Step 0 fills\*)|(digest: \`$DIGEST\`)|" "$REPO/zdc-setup.md" && ok "digest recorded in zdc-setup.md"
  fi
  if grep -q "digest: \*Step 0 fills\*" "$REPO/zdc-setup.md"; then
    skip "digest not yet recorded in zdc-setup.md (run with --record-digest in Phase 0)"
  elif grep -q "$DIGEST" "$REPO/zdc-setup.md"; then ok "digest matches zdc-setup.md"
  else fail "image digest differs from the one recorded in zdc-setup.md"; fi
else
  fail "image $IMAGE not pulled (docker pull $IMAGE)"
fi

# 3. submodule pins against zdc-setup.md
for sub in EICrecon detector_benchmarks epic-capybara meson-structure; do
  sha=$(git -C "$REPO/submodules/$sub" rev-parse HEAD 2>/dev/null | cut -c1-8)
  if [ -z "$sha" ]; then fail "submodule $sub not initialized (git submodule update --init)"
  elif grep -q "$sha" "$REPO/zdc-setup.md"; then ok "submodule $sub at $sha (pin)"
  elif [ "$sub" = EICrecon ] && br=$(git -C "$REPO/submodules/$sub" branch --show-current) && [[ "$br" == zdc-autoresearch/* ]] \
       && pin=$(git -C "$REPO/submodules/$sub" rev-list --max-count=500 HEAD | cut -c1-8 | while read -r c; do
                  grep -q "$c" "$REPO/zdc-setup.md" && { echo "$c"; break; }; done) \
       && [ -n "$pin" ]; then
    # Phase 4 (D-user-34): tries are commits on a zdc-autoresearch/* branch cut from the pin
    ok "submodule $sub at $sha on $br, $(git -C "$REPO/submodules/$sub" rev-list --count "$pin"..HEAD) commits above the pin $pin"
  else fail "submodule $sub at $sha, which zdc-setup.md does not name"; fi
done
dirty=$(git -C "$REPO/submodules/EICrecon" status --porcelain | wc -l)
[ "$dirty" -eq 0 ] && ok "EICrecon working tree clean" || echo "NOTE EICrecon working tree has $dirty changed paths (a code experiment in progress?)"

# 4. inside the image: EIC environment, detector configurations, tool versions
if docker image inspect "$IMAGE" >/dev/null 2>&1; then
  "$REPO/scripts/100_in_container.sh" bash -c '
    ok(){ echo "OK   $*"; }; fail(){ echo "FAIL $*"; exit 1; }
    [ -n "${DETECTOR_PATH:-}" ] && ok "DETECTOR_PATH=$DETECTOR_PATH" || fail "thisepic.sh did not set DETECTOR_PATH"
    for cfg in epic_zdc_lyso_sipm epic_zdc_sipm_on_tile_only epic_craterlake epic_craterlake_9x130 epic_craterlake_9x275; do
      [ -f "$DETECTOR_PATH/$cfg.xml" ] && ok "detector config $cfg.xml" || fail "detector config $cfg.xml missing in the image"
    done
    ok "eicrecon $(eicrecon --version 2>&1 | head -1)"; ok "npsim $(python -c "import DDSim; print(DDSim.__file__)" 2>&1 | tail -1)"; ok "root $(root-config --version)"
    ok "epic $(cat $DETECTOR_PATH/../../share/epic/version 2>/dev/null || echo unknown)"
  ' || fail "container checks (see above)"
fi

# 5. data root, manifests, references
[ -d "$DATA_ROOT" ] && ok "data root $DATA_ROOT" || skip "data root $DATA_ROOT does not exist yet (Phase 0 creates it)"
if [ -f "$REPO/space/perf/manifest-datasets.json" ]; then
  uv run --project "$REPO" "$REPO/scripts/121_manifest.py" verify "$REPO/space/perf/manifest-datasets.json" && ok "dataset manifest verifies" || fail "dataset manifest does NOT verify (the ruler is broken: work-common.md, the missing/mismatching artifact rows)"
else skip "no dataset manifest yet"; fi
if [ -f "$REPO/space/perf/references.json" ]; then
  uv run --project "$REPO" "$REPO/scripts/121_manifest.py" verify "$REPO/space/perf/references.json" && ok "reference outputs verify" || fail "reference outputs do NOT verify"
else skip "no references.json yet"; fi
[ -f "$REPO/space/FROZEN" ] && ok "space/FROZEN in place ($(grep -vc '^#' "$REPO/space/FROZEN") lines)" || skip "space/FROZEN absent (Phase 0 not done)"

echo "---- $fails failure(s)"
[ "$fails" -eq 0 ]
