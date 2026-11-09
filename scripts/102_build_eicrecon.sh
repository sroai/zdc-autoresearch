#!/usr/bin/env bash
# Build EICrecon from submodules/EICrecon inside the pinned image into
# {install_root}/eicrecon-<sha12>, with the build tree under {build_root}.
# A clean build takes 30 to 60 minutes (EICrecon AGENTS.md); an incremental
# rebuild of a changed file takes minutes. Never cancel a build.
#
# Usage:
#   scripts/102_build_eicrecon.sh                 # the submodule's current HEAD (plus uncommitted changes)
#   scripts/102_build_eicrecon.sh --ref fdbb773d  # check that commit out in a detached worktree and build it
#   scripts/102_build_eicrecon.sh --label E12     # install under eicrecon-E12 instead of the sha (code experiments)
#   scripts/102_build_eicrecon.sh --clean         # remove the build tree first
#
# The log is {logs_root}/build-<label>.log; only its tail is printed. The
# working tree is built as it is, so a code experiment's patch applied to the
# submodule is what gets built; the label keeps the install apart from the pin's.
set -euo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROFILE=${ZDC_CONFIG:-$REPO/configs/local.yaml}
yaml_get() { sed -n "s/^$1:[[:space:]]*\([^#]*\).*/\1/p" "$PROFILE" | sed 's/[[:space:]]*$//' | head -1; }
DATA_ROOT=$(yaml_get data_root); CORES=$(yaml_get cores); CORES=${CORES:-8}
BUILD_ROOT=${DATA_ROOT}/build; INSTALL_ROOT=${DATA_ROOT}/install; LOGS=${DATA_ROOT}/logs
REF=""; LABEL=""; CLEAN=0
while [ $# -gt 0 ]; do case "$1" in
  --ref) REF=$2; shift 2;; --label) LABEL=$2; shift 2;; --clean) CLEAN=1; shift;;
  -h|--help) sed -n '2,20p' "$0"; exit 0;; *) echo "unknown option $1" >&2; exit 2;; esac; done

SRC=$REPO/submodules/EICrecon
if [ -n "$REF" ]; then
  # A detached worktree keeps the submodule's own checkout (and any experiment in it) untouched.
  SRC=$BUILD_ROOT/src-$(echo "$REF" | cut -c1-12)
  mkdir -p "$BUILD_ROOT"
  if [ ! -d "$SRC" ]; then git -C "$REPO/submodules/EICrecon" fetch origin "$REF" >/dev/null 2>&1 || true; git -C "$REPO/submodules/EICrecon" worktree add --detach "$SRC" "$REF"; fi
fi
SHA=$(git -C "$SRC" rev-parse HEAD | cut -c1-12)
LABEL=${LABEL:-$SHA}
BUILD=$BUILD_ROOT/eicrecon-$LABEL; INSTALL=$INSTALL_ROOT/eicrecon-$LABEL
mkdir -p "$BUILD_ROOT" "$INSTALL_ROOT" "$LOGS"
[ "$CLEAN" -eq 1 ] && rm -rf "$BUILD"
LOG=$LOGS/build-$LABEL.log
echo "building $SRC ($SHA) -> $INSTALL, log $LOG"

# Container paths: the repo is /work, the data root is data_mount (its host path). A source tree under
# the data root is already a container path; the submodule needs translating.
DATA_MOUNT=$(yaml_get data_mount); DATA_MOUNT=${DATA_MOUNT:-$DATA_ROOT}
to_container() { echo "$1" | sed "s|^$REPO|/work|; s|^$DATA_ROOT|$DATA_MOUNT|"; }
SRC_C=$(to_container "$SRC"); BUILD_C=$(to_container "$BUILD"); INSTALL_C=$(to_container "$INSTALL")

start=$(date +%s)
# D-user-35: dis-autoresearch has priority; a build takes at most ZDC_BUILD_JOBS cores (default 6) and 16 GB.
BJ=${ZDC_BUILD_JOBS:-6}; [ "$BJ" -gt "$CORES" ] && BJ=$CORES
ZDC_CPUS=$BJ ZDC_MEM=16g "$REPO/scripts/100_in_container.sh" bash -c "
  set -e
  cmake -S '$SRC_C' -B '$BUILD_C' -DCMAKE_INSTALL_PREFIX='$INSTALL_C' -DCMAKE_BUILD_TYPE=Release
  cmake --build '$BUILD_C' --target install -- -j$BJ
" > "$LOG" 2>&1 || { echo "BUILD FAILED; tail of $LOG:"; tail -n 40 "$LOG"; exit 1; }
end=$(date +%s)
echo "build ok in $((end-start)) s; install $INSTALL"
echo "$(date -Is) $LABEL $SHA $((end-start))s" >> "$LOGS/build-times.txt"
EICRECON_INSTALL=$INSTALL_C "$REPO/scripts/100_in_container.sh" eicrecon --version 2>&1 | tail -1
