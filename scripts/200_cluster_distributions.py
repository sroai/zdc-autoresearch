#!/usr/bin/env python3
"""The three review findings on PR 3064 as numbers and plots (guards G1 to G3).

For one or several experiments, on the DIS guard samples (D5) or any dataset:
the intrinsic-φ histogram of ZDC clusters, the cluster-energy spectrum, the
nhits-per-cluster distribution and the clusters-per-event distribution, drawn
on one figure per dataset with every experiment overlaid, plus a table of the
G1 to G3 numbers and the χ² of each histogram against the first experiment
given (the reference). Plots go to {space}/plots/<phase>/cluster_distributions/.

Usage:
  uv run scripts/200_cluster_distributions.py R0_stock R1_pr3064 --phase phase0
  uv run scripts/200_cluster_distributions.py R0_stock E03_nhits5 --datasets D1_pi0 --phase phase2
"""
import argparse
import sys
from pathlib import Path

import awkward as ak
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import datasets_config, load_profile, metrics_config, repo_path  # noqa: E402
from zdc.edm import read_collection  # noqa: E402


def column_diagnostics(files, mcfg):
    """Per cluster: the number of distinct subcell (x, y) positions it holds. A cluster with exactly
    one is a single subcell column through the layers: the signature of a neighbour distance below
    the 24.4 mm subcell pitch (docs/expert-review-v1.md, section 2.4)."""
    import uproot
    c, r = mcfg.collections, mcfg.relations
    distinct = []
    for f in files:
        tree = uproot.open(f)["events"]
        try:
            arr = tree.arrays([f"{c.zdc_clusters}.hits_begin", f"{c.zdc_clusters}.hits_end", r.cluster_hits_index,
                               f"{c.zdc_subcell_hits}.position.x", f"{c.zdc_subcell_hits}.position.y"], library="ak")
        except Exception as e:
            print(f"NOTE: column diagnostics unavailable ({e}); the cluster-hit relation or subcell positions are missing from the output")
            return np.array([])
        hb, he = arr[f"{c.zdc_clusters}.hits_begin"], arr[f"{c.zdc_clusters}.hits_end"]
        link = arr[r.cluster_hits_index]
        hx, hy = arr[f"{c.zdc_subcell_hits}.position.x"], arr[f"{c.zdc_subcell_hits}.position.y"]
        for ev in range(len(hb)):
            b, e, lk = ak.to_numpy(hb[ev]), ak.to_numpy(he[ev]), ak.to_numpy(link[ev])
            x, y = ak.to_numpy(hx[ev]), ak.to_numpy(hy[ev])
            for i in range(len(b)):
                idx = lk[b[i]:e[i]]
                xy = np.round(np.stack([x[idx], y[idx]], axis=1), 1)
                distinct.append(len(np.unique(xy, axis=0)) if len(idx) else 0)
    return np.array(distinct)


def load(profile, mcfg, experiment, dataset):
    files = sorted((Path(profile.reco_root) / experiment / dataset).glob("*.edm4eic.root"))
    if not files:
        return None
    cl = read_collection(files, mcfg.collections.zdc_clusters, ["energy", "nhits", "intrinsicPhi", "intrinsicTheta", "shapeParameters"])
    shape = cl["shapeParameters"]
    # shapeParameters: [0..2] widths, [3] ?, [4..6] the three eigenvalues (CalorimeterClusterShape); λ2 is index 5
    try:
        lam2 = np.sqrt(np.clip(ak.to_numpy(ak.flatten(shape[:, :, 5])), 0, None))
    except Exception:
        lam2 = np.array([])
    return {
        "nev": len(cl["energy"]),
        "energy": ak.to_numpy(ak.flatten(cl["energy"])),
        "nhits": ak.to_numpy(ak.flatten(cl["nhits"])),
        "phi": np.degrees(ak.to_numpy(ak.flatten(cl["intrinsicPhi"]))),
        "theta": np.degrees(ak.to_numpy(ak.flatten(cl["intrinsicTheta"]))),
        "width2": lam2,
        "ncl": ak.to_numpy(ak.num(cl["energy"], axis=1)),
        "distinct_xy": column_diagnostics(files, mcfg),
    }


def chi2(h_ref, h_new):
    """χ² per bin between two histograms normalized to the reference's total."""
    scale = h_ref.sum() / max(h_new.sum(), 1)
    h = h_new * scale
    denom = h_ref + h
    mask = denom > 0
    return float(np.sum((h_ref[mask] - h[mask]) ** 2 / denom[mask]) / max(mask.sum(), 1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiments", nargs="+", help="first one is the reference")
    ap.add_argument("--datasets", nargs="*", help="default: the DIS samples of configs/datasets.yaml")
    ap.add_argument("--phase", default="phase0")
    args = ap.parse_args()
    profile, mcfg, dcfg = load_profile(), metrics_config(), datasets_config()
    datasets = args.datasets or list(dcfg.dis.samples)
    outdir = repo_path("space", "plots", args.phase, "cluster_distributions")
    outdir.mkdir(parents=True, exist_ok=True)
    w = mcfg.windows

    for ds in datasets:
        data = {e: load(profile, mcfg, e, ds) for e in args.experiments}
        data = {e: d for e, d in data.items() if d}
        if not data:
            print(f"{ds}: no reconstruction found for any experiment")
            continue
        ref = next(iter(data))
        fig, axes = plt.subplots(2, 3, figsize=(17, 9))
        specs = [("phi", 36, (-180, 180), "cluster intrinsic phi [deg]", False),
                 ("energy", 50, (0, 300), "cluster energy [GeV]", True),
                 ("nhits", 50, (0, 2000), "hits per cluster", True),
                 ("ncl", 15, (-0.5, 14.5), "clusters per event", True),
                 ("distinct_xy", 30, (0.5, 30.5), "distinct subcell (x,y) per cluster (1 = column)", True),
                 ("width2", 40, (0, 80), "lateral width sqrt(lambda2) [mm]", True)]
        hists = {}
        for ax, (key, bins, rng, label, log) in zip(axes.flat, specs):
            for e, d in data.items():
                h, edges = np.histogram(d[key], bins=bins, range=rng)
                hists.setdefault(key, {})[e] = h
                ax.stairs(h / max(d["nev"], 1), edges, label=e)
            ax.set_xlabel(label)
            ax.set_ylabel("clusters / event / bin" if key != "ncl" else "events / bin (norm.)")
            if log:
                ax.set_yscale("log")
            ax.legend(fontsize=8)
        fig.suptitle(f"{ds}: ZDC cluster distributions")
        fig.tight_layout()
        png = outdir / f"{ds}.png"
        fig.savefig(png, dpi=110)
        plt.close(fig)
        print(f"\n{ds} (plot {png})")
        print(f"{'experiment':24s} {'events':>7s} {'cl/ev':>7s} {'G1 phi@180':>11s} {'G1 columns':>11s} {'G2 E>%.0f':>9s} {'G3 E<%.0f/ev':>12s} {'nhits med':>10s} {'chi2 phi':>9s} {'chi2 E':>8s} {'chi2 nhits':>10s}" % (w.high_energy_cluster_gev, w.low_energy_cluster_gev))
        for e, d in data.items():
            g1 = np.mean(np.abs(np.abs(d["phi"]) - 180) < w.phi_edge_deg) if len(d["phi"]) else float("nan")
            columns = np.mean(d["distinct_xy"] == 1) if len(d["distinct_xy"]) else float("nan")
            g2 = np.mean(d["energy"] > w.high_energy_cluster_gev) if len(d["energy"]) else float("nan")
            g3 = np.sum(d["energy"] < w.low_energy_cluster_gev) / max(d["nev"], 1)
            med = np.median(d["nhits"]) if len(d["nhits"]) else float("nan")
            c = [chi2(hists[k][ref], hists[k][e]) for k in ("phi", "energy", "nhits")]
            print(f"{e:24s} {d['nev']:7d} {len(d['energy'])/max(d['nev'],1):7.3f} {g1:11.3f} {columns:11.3f} {g2:9.3f} {g3:12.3f} {med:10.0f} {c[0]:9.2f} {c[1]:8.2f} {c[2]:10.2f}")


if __name__ == "__main__":
    main()
