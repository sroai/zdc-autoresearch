#!/usr/bin/env python3
"""Gate G4: every non-ZDC collection of a reconstruction must be identical to the reference.

Compares two edm4eic files leaf by leaf (every branch of the `events` tree whose
collection does not start with one of the ZDC-owned prefixes in
configs/metrics.yaml). Identical means: same branch set, same entry counts, and
every value equal (exact for integers, bit-for-bit for floats; use --rtol to
allow a floating tolerance when a platform difference is proven). Prints PASS or
FAIL with the first differing leaf and the first differing event, and exits
non-zero on FAIL. With --zdc it compares the ZDC collections instead (used by the
gate proof, where the ZDC copy must differ, and by Phase 0 item 8 where two R1
reconstructions must agree). With --capybara it also runs `capybara bara` on the
two files into the given folder (the report the EICrecon CI produces).

Usage:
  uv run scripts/130_compare_collections.py ref.edm4eic.root new.edm4eic.root
  uv run scripts/130_compare_collections.py ref.root new.root --zdc
  uv run scripts/130_compare_collections.py ref.root new.root --capybara space/reports/capybara/E03

A gate that has only ever printed PASS proves nothing: scripts/131_prove_gates.sh
feeds it damaged copies and checks the verdicts.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import metrics_config, repo_path  # noqa: E402


def collection_of(branch):
    """The podio collection a branch belongs to. Relation branches are `_<collection>_<relation>`
    (e.g. `_HcalFarForwardZDCClusters_hits`): they belong to <collection>, so a ZDC relation is ZDC."""
    head = branch.split(".")[0].split("/")[0]
    if head.startswith("_") and "_" in head[1:]:
        head = head[1:].rsplit("_", 1)[0]
    return head


def is_zdc(branch, prefixes):
    return any(collection_of(branch).startswith(p) for p in prefixes)


def compare(ref_path, new_path, prefixes, zdc_side, rtol):
    ref = uproot.open(ref_path)["events"]
    new = uproot.open(new_path)["events"]
    # Leaf branches only: a record's parent branch repeats its leaves and cannot be flattened to numbers.
    ref_branches = {b for b in ref.keys() if not ref[b].branches and is_zdc(b, prefixes) == zdc_side}
    new_branches = {b for b in new.keys() if not new[b].branches and is_zdc(b, prefixes) == zdc_side}
    side = "ZDC" if zdc_side else "non-ZDC"
    if ref.num_entries != new.num_entries:
        return False, f"entry count differs: {ref.num_entries} vs {new.num_entries}"
    if ref_branches != new_branches:
        missing = sorted(ref_branches - new_branches)[:5]
        extra = sorted(new_branches - ref_branches)[:5]
        return False, f"{side} branch sets differ: missing in new {missing}, extra in new {extra}"
    checked, unreadable = 0, []
    for branch in sorted(ref_branches):
        try:
            a = ref[branch].array(library="ak")
            b = new[branch].array(library="ak")
        except Exception as e:  # a branch uproot cannot read (podio metadata vectors): compared by count only
            if ref[branch].num_entries != new[branch].num_entries:
                return False, f"{branch}: entries differ ({e})"
            unreadable.append(branch)
            continue
        if ak.num(a, axis=1).tolist() != ak.num(b, axis=1).tolist() if a.ndim > 1 else len(a) != len(b):
            counts_a, counts_b = (ak.num(a, axis=1), ak.num(b, axis=1)) if a.ndim > 1 else (len(a), len(b))
            first = int(np.argmax(np.asarray(counts_a) != np.asarray(counts_b))) if a.ndim > 1 else 0
            return False, f"{branch}: per-event counts differ, first at event {first}"
        fa, fb = ak.flatten(a, axis=None), ak.flatten(b, axis=None)
        va, vb = ak.to_numpy(fa), ak.to_numpy(fb)
        if va.dtype.kind == "f" and rtol > 0:
            same = np.allclose(va, vb, rtol=rtol, atol=0, equal_nan=True)
        else:
            same = np.array_equal(va, vb, equal_nan=(va.dtype.kind == "f"))
        if not same:
            idx = int(np.argmax(va != vb)) if len(va) == len(vb) else -1
            return False, f"{branch}: values differ, first at flat index {idx} ({va[idx] if idx >= 0 else '?'} vs {vb[idx] if idx >= 0 else '?'})"
        checked += 1
    note = f"; {len(unreadable)} unreadable leaves compared by entry count only, e.g. {unreadable[:3]}" if unreadable else ""
    return True, f"{checked} {side} leaves identical over {ref.num_entries} events{note}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ref")
    ap.add_argument("new")
    ap.add_argument("--zdc", action="store_true", help="compare the ZDC collections instead of the non-ZDC ones")
    ap.add_argument("--rtol", type=float, default=0.0, help="relative tolerance for floats (default exact)")
    ap.add_argument("--capybara", metavar="DIR", help="also write a capybara report into DIR")
    args = ap.parse_args()
    prefixes = list(metrics_config().zdc_owned_prefixes)
    ok, message = compare(args.ref, args.new, prefixes, args.zdc, args.rtol)
    print(f"{'PASS' if ok else 'FAIL'}: {message}")
    if args.capybara:
        out = Path(args.capybara)
        out.mkdir(parents=True, exist_ok=True)
        # capybara runs in an isolated uvx environment built from the submodule: `uv run --project` there fails on
        # its requires-python range and would write a lock file into the frozen submodule.
        cmd = ["uvx", "--python", "3.12", "--from", str(repo_path("submodules", "epic-capybara")), "capybara", "bara",
               str(Path(args.ref).resolve()), str(Path(args.new).resolve())]
        with open(out / "capybara.log", "w") as lf:
            rc = subprocess.call(cmd, cwd=out, stdout=lf, stderr=subprocess.STDOUT)
        print(f"capybara: rc={rc}, report under {out} (log capybara.log)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
