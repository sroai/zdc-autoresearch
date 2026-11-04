#!/usr/bin/env bash
# Run one command inside the pinned eic_xl image with the repository at /work and
# the data root at /data, the EIC environment loaded, and the custom EICrecon
# install prepended when EICRECON_INSTALL names one.
#
# Usage:
#   scripts/100_in_container.sh <command> [args...]
#   EICRECON_INSTALL=/data/zdc-autoresearch/install/eicrecon-e5e2a60c60b6 scripts/100_in_container.sh eicrecon --version
#   scripts/100_in_container.sh bash            # interactive shell in the container
#
# Machine facts (image, mounts, data root) come from configs/local.yaml, or from
# the file $ZDC_CONFIG names. The container runs as the calling user so that
# every file it writes is owned by you. Paths you pass must be container paths:
# the repo is /work, the data root is /data (identical to the host path here).
set -euo pipefail

REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROFILE=${ZDC_CONFIG:-$REPO/configs/local.yaml}

# A tiny YAML reader: top-level `key: value` lines only (the profile has no nesting at top level).
yaml_get() { sed -n "s/^$1:[[:space:]]*\([^#]*\).*/\1/p" "$PROFILE" | sed 's/[[:space:]]*$//' | head -1; }

IMAGE=$(yaml_get image)
RUNTIME=$(yaml_get runtime)
DATA_ROOT=$(yaml_get data_root)
REPO_MOUNT=$(yaml_get repo_mount); REPO_MOUNT=${REPO_MOUNT:-/work}
DATA_MOUNT=$(yaml_get data_mount); DATA_MOUNT=${DATA_MOUNT:-/data}
[ -n "$IMAGE" ] || { echo "ERROR: no `image:` in $PROFILE" >&2; exit 2; }
mkdir -p "$DATA_ROOT"

# The command runs after thisepic.sh; EICRECON_INSTALL (a container path) is
# prepended so that `eicrecon` and its plugins come from the custom build.
INNER='source /opt/detector/epic-main/bin/thisepic.sh >/dev/null 2>&1 || source /opt/detector/epic-main/bin/thisepic.sh;
if [ -n "${EICRECON_INSTALL:-}" ]; then
  export PATH="$EICRECON_INSTALL/bin:$PATH"
  export LD_LIBRARY_PATH="$EICRECON_INSTALL/lib:${LD_LIBRARY_PATH:-}"
  export JANA_PLUGIN_PATH="$EICRECON_INSTALL/lib/EICrecon/plugins${JANA_PLUGIN_PATH:+:$JANA_PLUGIN_PATH}"
fi
exec "$@"'

case "$RUNTIME" in
  docker)
    TTY_FLAGS=""; [ -t 0 ] && TTY_FLAGS="-it"
    exec docker run --rm $TTY_FLAGS --init \
      --user "$(id -u):$(id -g)" \
      -e HOME=/tmp/home -e EICRECON_INSTALL="${EICRECON_INSTALL:-}" \
      -e OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}" \
      -v "$REPO:$REPO_MOUNT" -v "$DATA_ROOT:$DATA_MOUNT" \
      -w "$REPO_MOUNT" \
      "$IMAGE" bash -c "$INNER" bash "$@"
    ;;
  apptainer|singularity)
    exec "$RUNTIME" exec \
      -B "$REPO:$REPO_MOUNT" -B "$DATA_ROOT:$DATA_MOUNT" \
      --pwd "$REPO_MOUNT" \
      "$IMAGE" bash -c "$INNER" bash "$@"
    ;;
  *) echo "ERROR: unknown runtime '$RUNTIME' in $PROFILE (docker | apptainer)" >&2; exit 2;;
esac
