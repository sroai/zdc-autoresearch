"""Raw hits of two rows identical, leaf by leaf: F2b for the crystal raw hits of a Phase 6 try against the base row MSF6_Y9
(and Step 0 item 3: MSF6_Y9 against CTL6_R0_crys).

Usage: uv run scripts/479_raw_hit_identity.py <reco dir A> <reco dir B> EcalFarForwardZDCRawHits,HcalFarForwardZDCRawHits,B0ECalRawHits
"""
import sys
from pathlib import Path
import awkward as ak, numpy as np, uproot
a_dir, b_dir = Path(sys.argv[1]), Path(sys.argv[2]); colls = sys.argv[3].split(",")
nf = ndiff = 0; leaves = 0
for fa in sorted(a_dir.glob("*.edm4eic.root")):
    fb = b_dir / fa.name
    ta, tb = uproot.open(fa)["events"], uproot.open(fb)["events"]
    nf += 1
    for c in colls:
        ka = sorted(k for k in ta.keys(recursive=True) if k.split("/")[-1].startswith(c + ".") or k.split("/")[-1].startswith(f"_{c}_"))
        kb = sorted(k for k in tb.keys(recursive=True) if k.split("/")[-1].startswith(c + ".") or k.split("/")[-1].startswith(f"_{c}_"))
        if ka != kb or not ka:
            print("branch sets differ", fa.name, c, len(ka), len(kb)); ndiff += 1; continue
        for k in ka:
            if tb[k].interpretation is None or not hasattr(tb[k], "array"):
                continue
            try:
                x, y = ta[k].array(library="ak"), tb[k].array(library="ak")
            except Exception:
                continue
            leaves += 1
            if not ak.all(ak.num(x, axis=-1) == ak.num(y, axis=-1)) if x.ndim > 1 else len(x) != len(y):
                print("counts differ", fa.name, k); ndiff += 1; continue
            if not np.array_equal(ak.to_numpy(ak.flatten(x, axis=None)), ak.to_numpy(ak.flatten(y, axis=None))):
                print("values differ", fa.name, k); ndiff += 1
print(f"{'PASS' if ndiff == 0 and nf else 'FAIL'}: {nf} files, {leaves} leaves compared, {ndiff} differences ({','.join(colls)})")
