#!/usr/bin/env bash
# Prove that the gate (scripts/130_compare_collections.py) can fail, then keep
# the damaged copies so every run start can re-check the verdicts without a
# reconstruction (loop file, Every run).
#
# Usage:
#   scripts/131_prove_gates.sh <R0 output.edm4eic.root>    # Phase 0: make the damaged copies and prove the verdicts
#   scripts/131_prove_gates.sh --check                     # every run: re-run the gate on the stored copies
#
# Damaged copies, under {data}/gate-controls/:
#   nonzdc_damaged.root  one value of a non-ZDC collection changed  -> gate must FAIL
#   zdc_damaged.root     one value of a ZDC collection changed      -> gate must PASS (ZDC may change), --zdc must FAIL
#   identical.root       a byte copy                                -> gate must PASS
# The damage is done through uproot (rewrite one branch value into a new file);
# which branch was damaged is written to controls.json, so a changed EICrecon
# output layout shows up as a broken control, not a silent PASS.
set -euo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PROFILE=${ZDC_CONFIG:-$REPO/configs/local.yaml}
yaml_get() { sed -n "s/^$1:[[:space:]]*\([^#]*\).*/\1/p" "$PROFILE" | sed 's/[[:space:]]*$//' | head -1; }
DATA_ROOT=$(yaml_get data_root); CTRL=$DATA_ROOT/gate-controls
GATE="uv run --project $REPO $REPO/scripts/130_compare_collections.py"
fails=0
expect() { # expect <PASS|FAIL> <label> <gate args...>
  local want=$1 label=$2; shift 2
  if $GATE "$@" >/tmp/gate.$$ 2>&1; then got=PASS; else got=FAIL; fi
  if [ "$got" = "$want" ]; then echo "OK   $label -> $got (expected)"; else echo "BROKEN $label -> $got, expected $want"; cat /tmp/gate.$$; fails=$((fails+1)); fi
}

if [ "${1:-}" = "--check" ]; then
  [ -f "$CTRL/controls.json" ] || { echo "no controls yet: run Phase 0 item 10 first"; exit 1; }
  REF=$(python3 -c "import json;print(json.load(open('$CTRL/controls.json'))['reference'])")
else
  REF=${1:?usage: $0 <R0 output.edm4eic.root> | --check}
  mkdir -p "$CTRL"
  uv run --project "$REPO" python - "$REF" "$CTRL" <<'PY'
import json, sys
from pathlib import Path
import awkward as ak, numpy as np, uproot, yaml
ref, ctrl = sys.argv[1], Path(sys.argv[2])
prefixes = yaml.safe_load(open("configs/metrics.yaml"))["zdc_owned_prefixes"]
tree = uproot.open(ref)["events"]
def pick(zdc):
    for b in tree.keys():
        coll = b.split(".")[0]
        if any(coll.startswith(p) for p in prefixes) != zdc: continue
        if not b.endswith((".energy", ".position.x", ".time", ".x", ".charge")): continue
        arr = tree[b].array(library="ak")
        if ak.count(arr) > 0: return b, arr
    raise SystemExit(f"no damageable branch found (zdc={zdc})")
def write(name, damaged_branch=None):
    # Rewrite every readable branch into a flat uproot file; podio metadata is not needed by the gate.
    out = uproot.recreate(ctrl / name)
    data = {}
    for b in tree.keys():
        try: data[b] = tree[b].array(library="ak")
        except Exception: continue
    if damaged_branch:
        flat = ak.to_numpy(ak.flatten(data[damaged_branch], axis=None)).copy()
        flat[0] = flat[0] + 1.0 if flat.dtype.kind == "f" else flat[0] + 1
        data[damaged_branch] = ak.unflatten(flat, ak.num(data[damaged_branch], axis=1)) if data[damaged_branch].ndim > 1 else ak.Array(flat)
    out["events"] = data
    out.close()
nz_b, _ = pick(False); z_b, _ = pick(True)
write("identical.root"); write("nonzdc_damaged.root", nz_b); write("zdc_damaged.root", z_b)
# The reference itself must be in the same flat layout for a branch-by-branch comparison.
write("reference_flat.root")
json.dump({"reference": str(ctrl / "reference_flat.root"), "source": ref, "nonzdc_branch": nz_b, "zdc_branch": z_b}, open(ctrl / "controls.json", "w"), indent=1)
print(f"controls written: non-ZDC damage on {nz_b}, ZDC damage on {z_b}")
PY
  REF=$CTRL/reference_flat.root
fi

expect PASS "identical copy"            "$REF" "$CTRL/identical.root"
expect FAIL "non-ZDC value changed"     "$REF" "$CTRL/nonzdc_damaged.root"
expect PASS "ZDC value changed (gate ignores ZDC)" "$REF" "$CTRL/zdc_damaged.root"
expect FAIL "ZDC value changed, --zdc"  "$REF" "$CTRL/zdc_damaged.root" --zdc
echo "---- $fails broken control(s)"
[ "$fails" -eq 0 ]
