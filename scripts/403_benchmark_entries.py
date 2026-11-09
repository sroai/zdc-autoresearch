#!/usr/bin/env python3
"""Check that a benchmark plot run filled its histograms (Phase 0 item 14).

For one benchmark of scripts/401_benchmark_plots.sh, read the linked
reconstruction files (one per momentum) and count, per momentum, the entries
that fill the benchmark script's histograms: the same collections and
selections the copy in scripts/700_benchmarks/ uses. A momentum passes when at
least one of its histograms has entries; the PDFs must exist. Every count is
printed, so a histogram that is empty at one momentum (e.g. no Λ at 100 GeV)
is visible as a number, not hidden by the pass.

Usage: uv run scripts/403_benchmark_entries.py <benchmark> <sim_output/benchmark dir> <plots dir>
"""
import re
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

bench, sim_dir, plots_dir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
Z = "HcalFarForwardZDCClusters.energy"
N = "ReconstructedHcalFarForwardZDCNeutrals.PDG"


def counts(f):
    t = uproot.open(f)["events"]
    # uproot names podio leaves "Coll/Coll.field"; map the dotted leaf name to the full key
    full = {k.split("/")[-1]: k for k in t.keys()}
    have = set(full)
    def arr(b):
        return t[full[b]].array() if b in have else None
    c = {}
    nclu = ak.num(arr(Z)) if Z in have else None
    if bench == "zdc_pi0":
        c["events with 2 ZDC clusters"] = int(np.sum(nclu == 2))
    elif bench == "zdc_lambda":
        c["ZDC cluster multiplicity (events)"] = int(len(nclu))
        lam = arr("ReconstructedLambdas.mass")
        c["ReconstructedLambdas"] = int(ak.sum(ak.num(lam))) if lam is not None else -1
        cm = arr("ReconstructedLambdaDecayProductsCM.PDG")
        c["CM neutrons"] = int(ak.sum(cm == 2112)) if cm is not None else -1
    elif bench in ("zdc_photon", "zdc_neutron"):
        pdg = arr(N)
        want = 22 if bench == "zdc_photon" else 2112
        c[f"ZDC neutrals PDG {want}"] = int(ak.sum(pdg == want)) if pdg is not None else -1
        c["ZDC clusters"] = int(ak.sum(nclu)) if nclu is not None else -1
    return c


bad = 0
for f in sorted(sim_dir.glob("*.edm4eic.root"), key=lambda p: int(re.search(r"_(\d+)GeV_", p.name).group(1))):
    p = re.search(r"_(\d+)GeV_", f.name).group(1)
    c = counts(f)
    ok = any(v > 0 for v in c.values())
    bad += not ok
    print(f"{'ok  ' if ok else 'EMPTY'} {bench:12s} {p:>4} GeV  " + "  ".join(f"{k}={v}" for k, v in c.items()))
pdfs = sorted(plots_dir.glob("*.pdf"))
print(f"{len(pdfs)} PDF(s) in {plots_dir}")
if not pdfs:
    bad += 1
sys.exit(1 if bad else 0)
