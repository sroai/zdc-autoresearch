#!/usr/bin/env python3
"""F3 for the crystal clusters (Phase 6, loop v6): honest photon candidates when a neutral links LYSO crystal clusters.

`460`'s F3f checks the Hcal clusters of the ZDC photon neutrals; it skips EcalFarForwardZDCClusters. `210` credits a
photon neutral through any linked cluster pure for a true photon, crystal clusters included, so a neutral that links a
crystal cluster must own it:

  C1 no two neutrals (any Reconstructed*Neutrals collection, any PDG) link the same crystal cluster;
  C2 a photon neutral's energy covers the crystal clusters it links: E_γ ≥ Σ E(linked crystal clusters) − 1e-4 GeV
     (crystal energies are electromagnetic energy, clipped at 2 GeV per crystal, so they are a lower bound of the photon's).

An output without crystal links passes with zero links counted (the base row). Any FAIL makes the try FOUL.

Controls (`--damage`, applied to the arrays after reading, to prove each clause fails): `share` links crystal cluster 0
to the first two photon neutrals of every event that has two; `budget` links every crystal cluster of the event to the
first photon neutral with its energy set below their sum.

Usage:
  uv run scripts/468_crystal_f3.py /data/zdc-autoresearch/reco/<row>/D6s_9x275 --tag <row>
  uv run scripts/468_crystal_f3.py /data/zdc-autoresearch/reco/MSF6_Y9/D6s_9x275 --tag CTL6_468_share --damage share
Writes space/perf/crystal-f3-<tag>.json; exit 1 on FAIL.
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import repo_path  # noqa: E402

spec = importlib.util.spec_from_file_location("r210", repo_path("scripts", "210_msf_lambda_regimes.py"))
r210 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r210)

CRYS = "EcalFarForwardZDCClusters"
TOL = 1e-4


def check_file(path, damage, fails, stats, max_listed=20):
    ids = r210.collection_ids(path)
    crys_id = ids.get(CRYS)
    t = uproot.open(path)["events"]
    have = {k.split("/")[-1] for k in t.keys()}
    names = sorted(n for n in ids if re.fullmatch(r"Reconstructed\w*Neutrals", n) and f"{n}.PDG" in have)
    if crys_id is None or f"{CRYS}.energy" not in have:
        stats["files_without_crystal_clusters"] += 1
        return
    ce = ak.to_list(t[f"{CRYS}.energy"].array())
    neu = {}
    for n in names:
        a = t.arrays([f"{n}.PDG", f"{n}.energy", f"{n}.clusters_begin", f"{n}.clusters_end", f"_{n}_clusters.index",
                      f"_{n}_clusters.collectionID"], library="ak")
        neu[n] = {k: ak.to_list(a[f"{n}.{k}"]) for k in ("PDG", "energy", "clusters_begin", "clusters_end")}
        neu[n]["index"] = ak.to_list(a[f"_{n}_clusters.index"]); neu[n]["cid"] = ak.to_list(a[f"_{n}_clusters.collectionID"])
    for ev in range(len(ce)):
        # per neutral: (collection, k, PDG, energy, linked crystal cluster indices)
        items = []
        for n, d in neu.items():
            for k, pdg in enumerate(d["PDG"][ev]):
                lo, hi = d["clusters_begin"][ev][k], d["clusters_end"][ev][k]
                crys = [int(d["index"][ev][j]) for j in range(lo, hi) if int(d["cid"][ev][j]) == crys_id]
                items.append([n, k, int(pdg), float(d["energy"][ev][k]), crys])
        photons = [it for it in items if it[2] == 22]
        if damage == "share" and len(photons) >= 2 and ce[ev]:
            photons[0][4] = photons[0][4] + [0]; photons[1][4] = photons[1][4] + [0]
        if damage == "budget" and photons and ce[ev]:
            photons[0][4] = list(range(len(ce[ev])))
            photons[0][3] = 0.5 * sum(ce[ev])
        stats["events"] += 1
        owner = {}
        for n, k, pdg, en, crys in items:
            stats["neutrals"] += 1
            if crys:
                stats["neutrals_with_crystal_links"] += 1
                stats["crystal_links"] += len(crys)
            for x in crys:
                if x in owner and owner[x] != (n, k):
                    stats["fail_C1"] += 1
                    if len(fails) < max_listed:
                        fails.append(f"C1 {path.name} event {ev}: crystal cluster {x} linked by {owner[x][0]}[{owner[x][1]}] and {n}[{k}]")
                owner[x] = (n, k)
            if pdg == 22 and crys:
                esum = sum(ce[ev][x] for x in set(crys) if x < len(ce[ev]))
                stats["photons_with_crystal_links"] += 1
                if en < esum - TOL:
                    stats["fail_C2"] += 1
                    if len(fails) < max_listed:
                        fails.append(f"C2 {path.name} event {ev}: photon {n}[{k}] E {en:.3f} GeV < its crystal clusters' {esum:.3f} GeV")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reco_dir")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--damage", choices=["share", "budget"], help="a control: damage the arrays after reading")
    ap.add_argument("--files", type=int, default=0, help="first N files only (0: all)")
    args = ap.parse_args()
    files = sorted(Path(args.reco_dir).glob("*.edm4eic.root"))
    if args.files:
        files = files[: args.files]
    fails, stats = [], {k: 0 for k in ("files", "files_without_crystal_clusters", "events", "neutrals", "neutrals_with_crystal_links",
                                       "crystal_links", "photons_with_crystal_links", "fail_C1", "fail_C2")}
    for f in files:
        stats["files"] += 1
        check_file(f, args.damage, fails, stats)
    ok = stats["files"] > 0 and stats["fail_C1"] == 0 and stats["fail_C2"] == 0 and stats["files_without_crystal_clusters"] == 0
    out = {"reco_dir": args.reco_dir, "damage": args.damage, "verdict": "PASS" if ok else "FAIL", "stats": stats, "failures": fails}
    path = repo_path("space", "perf", f"crystal-f3-{args.tag}.json")
    path.write_text(json.dumps(out, indent=1))
    for x in fails[:5]:
        print("  " + x)
    print(f"468 {args.tag}: {out['verdict']} — {stats['files']} files, {stats['events']} events, {stats['neutrals_with_crystal_links']} neutrals "
          f"with crystal links ({stats['crystal_links']} links), C1 fails {stats['fail_C1']}, C2 fails {stats['fail_C2']}"
          + (f", {stats['files_without_crystal_clusters']} files without crystal clusters" if stats["files_without_crystal_clusters"] else "")
          + f" → {path}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
