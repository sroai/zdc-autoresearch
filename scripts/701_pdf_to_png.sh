#!/usr/bin/env bash
# Convert every PDF under a directory to PNG, one PNG per page, beside the PDF
# (D-user-22: every plot the program shows is a PNG; tools the program does
# not own keep their PDF). A PDF whose PNG is newer than itself is skipped.
#
# Usage: scripts/701_pdf_to_png.sh <dir> [--dpi 110] [--force]
#
# Output names: <stem>.png for a one-page PDF, <stem>-<page>.png for more
# (pdftoppm's own numbering, zero-padded to the page count).
set -uo pipefail
DIR=${1:?usage: $0 <dir> [--dpi N] [--force]}; shift
DPI=110; FORCE=0
while [ $# -gt 0 ]; do case "$1" in --dpi) DPI=$2; shift 2;; --force) FORCE=1; shift;; *) echo "unknown $1" >&2; exit 2;; esac; done
command -v pdftoppm >/dev/null || { echo "pdftoppm missing (poppler); see space/notes/ENVIRONMENT.md" >&2; exit 3; }
done=0; skipped=0; failed=0
while IFS= read -r -d '' pdf; do
  stem=${pdf%.pdf}
  if [ "$FORCE" -eq 0 ] && { [ -s "$stem.png" ] && [ "$stem.png" -nt "$pdf" ] || [ -s "$stem-1.png" ] && [ "$stem-1.png" -nt "$pdf" ]; }; then
    skipped=$((skipped+1)); continue
  fi
  pages=$(pdfinfo "$pdf" 2>/dev/null | sed -n 's/^Pages:[[:space:]]*//p'); pages=${pages:-1}
  if [ "$pages" -eq 1 ]; then
    pdftoppm -png -r "$DPI" -singlefile "$pdf" "$stem" 2>/dev/null && done=$((done+1)) || { failed=$((failed+1)); echo "FAIL $pdf"; }
  else
    pdftoppm -png -r "$DPI" "$pdf" "$stem" 2>/dev/null && done=$((done+1)) || { failed=$((failed+1)); echo "FAIL $pdf"; }
  fi
done < <(find "$DIR" -type f -name '*.pdf' -print0)
echo "pdf_to_png: $done converted, $skipped up to date, $failed failed under $DIR"
[ "$failed" -eq 0 ]
