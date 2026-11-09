#!/usr/bin/env python
"""Phase 4 / Phase 5 comparison plots for the Phase 5 deck (PNG, slides/phase5/plots/).

Inputs (read at run time; a missing row is left out of its plot):
  space/perf/msf-regimes-<row>-D6s_<beam>.json   N_found / N_expected and the regime groups (210)
  space/perf/headline.csv                        S4a_tm per thrown Λ → nπ⁰ on the D4 gun (441)
  {reco}/<row>/D6s_9x275/*.edm4eic.root          every ReconstructedLambdas mass (the spectrum)
Colours: the dataviz reference palette's first three slots (validated all-pairs, light surface); aqua carries labels.

Rebuild:  uv run python slides/phase5/make_phase5_plots.py
"""
import csv
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
PERF = REPO / "space" / "perf"
RECO = Path("/data/zdc-autoresearch/reco")
OUT = Path(__file__).resolve().parent / "plots"
OUT.mkdir(exist_ok=True)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#dddcd8", "#ffffff"
REACH = {"9x275": 43.6, "9x130": 8.0}
M_L = 1.115683
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
                     "axes.axisbelow": True, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
                     "axes.spines.top": False, "axes.spines.right": False})

MSF_STEPS = [("R0", "CTL5_R0_msf"), ("X1", "CTL5_X1_msf"), ("X9", "MSF5_X9"), ("Y2", "Y2_vertex_lever_arm"),
             ("Y4", "Y4_b0_split_on_y2"), ("Y5", "Y5_mixed_pairing"), ("Y6", "Y6_b0_profile"), ("Y7", "Y7_b0_photon_law"),
             ("Y8", "Y8_b0_profile_03"), ("Y9", "Y9_external_pair")]
D4_STEPS = [("R1", "R1_pr3064"), ("X1", "X1_offline_chain"), ("X2", "X2_lambda_pairing"), ("X3", "X3_pairing_weights"),
            ("X4", "X4_photon_depth"), ("X5", "X5_photon_depth_face"), ("X7", "X7_core_split"), ("X8", "X8_core_depth_centroid"),
            ("X9", "X9_pairing_photon_depth"), ("Y2", "D4P5_Y2"), ("Y4", "D4P5_Y4"), ("Y5", "D4P5_Y5"), ("Y6", "CP5_1_Y6_D4"),
            ("Y7", "D4P5_Y7"), ("Y8", "D4P5_Y8"), ("Y9", "CP5_2_Y9_D4")]


def regimes(row, beam):
    p = PERF / f"msf-regimes-{row}-D6s_{beam}.json"
    return json.loads(p.read_text()) if p.exists() else None


def yield_of(row, beam):
    d = regimes(row, beam)
    if not d or row not in d.get("rows", {}):
        return None
    return 100 * d["rows"][row]["yield"]


def headline():
    with open(PERF / "headline.csv") as fh:
        return {r["row"]: r for r in csv.DictReader(fh)}


def phase_divider(ax, x, top):
    ax.axvline(x, color=MUTED, lw=1.2, ls=(0, (4, 3)))
    ax.text(x - 0.15, top, "Phase 4", ha="right", va="top", color=MUTED, fontsize=12)
    ax.text(x + 0.15, top, "Phase 5", ha="left", va="top", color=MUTED, fontsize=12)


def plot_msf_progression():
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    for ax, beam in zip(axes, ("9x275", "9x130")):
        pts = [(i, lab, yield_of(row, beam)) for i, (lab, row) in enumerate(MSF_STEPS)]
        pts = [p for p in pts if p[2] is not None]
        x = [p[0] for p in pts]; y = [p[2] for p in pts]
        ax.plot(x, y, color=BLUE, lw=2, marker="o", ms=8, zorder=3)
        ax.axhline(REACH[beam], color=MUTED, lw=1.2, ls=":")
        ax.text(len(MSF_STEPS) - 0.6, REACH[beam], f"reachable {REACH[beam]} %", ha="right", va="bottom", color=MUTED, fontsize=12)
        for xi, lab, yi in pts:
            if lab in ("R0", "X1", "X9", "Y5", "Y9"):
                ax.annotate(f"{yi:.2f} %", (xi, yi), textcoords="offset points", xytext=(0, 9), ha="center", color=INK, fontsize=11)
        ax.set_xticks(range(len(MSF_STEPS)), [s[0] for s in MSF_STEPS])
        ax.set_ylim(0, REACH[beam] * 1.12)
        ax.set_title(f"MSF {beam}, search half", color=INK, fontsize=14, loc="left")
        ax.set_ylabel("Λ → nπ⁰ found / expected (%)")
        phase_divider(ax, 2.5, REACH[beam] * 1.1)
    fig.tight_layout()
    fig.savefig(OUT / "p5_msf_progression.png", dpi=150)
    plt.close(fig)


def plot_d4_progression():
    H = headline()
    fig, ax = plt.subplots(figsize=(13, 4.8))
    for col, colour, lab in (("S4a_tm_per_thrown_mean", BLUE, "mean 100–275 GeV"), ("S4a_tm_per_thrown_275", ORANGE, "275 GeV")):
        pts = [(i, float(H[row][col])) for i, (_, row) in enumerate(D4_STEPS) if row in H and H[row].get(col) not in (None, "", "nan")]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=colour, lw=2, marker="o", ms=8, label=lab, zorder=3)
        if pts:
            ax.annotate(f"{pts[-1][1]:.2f} %", pts[-1], textcoords="offset points", xytext=(8, -4), color=INK, fontsize=11)
    for c, lab in ((14.1, "ceiling, mean"), (27.8, "ceiling, 275 GeV")):
        ax.axhline(c, color=MUTED, lw=1.2, ls=":")
        ax.text(0.1, c, lab + f" {c} %", va="bottom", color=MUTED, fontsize=11)
    ax.set_xticks(range(len(D4_STEPS)), [s[0] for s in D4_STEPS])
    ax.set_ylim(0, 31)
    ax.set_ylabel("S4a_tm per thrown Λ → nπ⁰ (%)")
    ax.set_title("D4 Λ gun (Phase 4's score)", color=INK, fontsize=14, loc="left")
    phase_divider(ax, 8.5, 30.5)
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.86), frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "p5_d4_progression.png", dpi=150)
    plt.close(fig)


def plot_regimes():
    names = ["all three in the ZDC", "n ZDC, γ B0 + γ ZDC", "n ZDC, γ γ in B0"]
    short = ["all in the ZDC", "one γ in B0", "both γ in B0"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    for ax, beam in zip(axes, ("9x275", "9x130")):
        a, b = regimes("MSF5_X9", beam), regimes("Y9_external_pair", beam)
        if not (a and b):
            continue
        ga = {g["group"]: g for g in a["groups"]}; gb = {g["group"]: g for g in b["groups"]}
        x = np.arange(len(names)); w = 0.36
        share = [100 * ga[n]["share_of_expected_npi0"] for n in names]
        ax.bar(x, share, width=0.86, color="#efeeea", edgecolor=GRID, lw=1, zorder=1, label="Λ in the regime (ceiling)")
        va = [100 * ga[n]["MSF5_X9"]["per_expected_npi0"] for n in names]
        vb = [100 * gb[n]["Y9_external_pair"]["per_expected_npi0"] for n in names]
        ax.bar(x - w / 2 - 0.01, va, width=w, color=BLUE, label="X9, end of Phase 4", zorder=2)
        ax.bar(x + w / 2 + 0.01, vb, width=w, color=ORANGE, label="Y9, end of Phase 5", zorder=2)
        for xi, v in zip(x - w / 2, va):
            ax.text(xi, v, f"{v:.1f}", ha="center", va="bottom", color=INK, fontsize=11)
        for xi, v in zip(x + w / 2, vb):
            ax.text(xi, v, f"{v:.1f}", ha="center", va="bottom", color=INK, fontsize=11)
        for xi, v in zip(x, share):
            ax.text(xi, v, f"{v:.1f} %", ha="center", va="bottom", color=MUTED, fontsize=11)
        ax.set_xticks(x, short)
        ax.set_ylim(0, max(share) * 1.18)
        ax.set_ylabel("found / expected Λ → nπ⁰ (%)")
        ax.set_title(f"MSF {beam}, search half", color=INK, fontsize=14, loc="left")
        ax.grid(axis="x", visible=False)
    axes[0].legend(loc="upper right", frameon=False, fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "p5_regimes.png", dpi=150)
    plt.close(fig)


def masses(row):
    import uproot
    import awkward as ak
    out = []
    for f in sorted((RECO / row / "D6s_9x275").glob("*.edm4eic.root")):
        m = uproot.open(f)["events"]["ReconstructedLambdas.mass"].array()
        out.append(ak.to_numpy(ak.flatten(m)))
    return np.concatenate(out) if out else np.array([])


def plot_mass():
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
    bins = np.linspace(0.95, 1.30, 71)
    for ax, (row, lab) in zip(axes, (("MSF5_X9", "X9, end of Phase 4"), ("Y9_external_pair", "Y9, end of Phase 5"))):
        allm = masses(row)
        d = regimes(row, "9x275")
        good = np.array([l[row]["mass"] for l in d["per_lambda"] if l[row]["matched"]]) if d else np.array([])
        ax.axvspan(M_L - 0.03, M_L + 0.03, color="#f3f2ee", zorder=0)
        ax.hist(allm, bins=bins, histtype="step", color=MUTED, lw=2, label="every candidate")
        ax.hist(good, bins=bins, color=BLUE, alpha=0.85, label="truth-matched Λ → nπ⁰")
        nw = int(np.sum(np.abs(allm - M_L) < 0.03))
        ax.text(0.98, 0.95, f"in ±30 MeV: {nw} candidates,\n{len(good)} truth-matched ({100 * len(good) / max(nw, 1):.1f} %)",
                transform=ax.transAxes, ha="right", va="top", color=INK, fontsize=12)
        ax.set_title(lab + " — MSF 9x275, search half", color=INK, fontsize=14, loc="left")
        ax.set_xlabel("reconstructed Λ mass (GeV)")
    axes[0].set_ylabel("candidates / 5 MeV")
    axes[0].legend(loc="upper left", frameon=False, fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "p5_mass.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    plot_msf_progression(); plot_d4_progression(); plot_regimes(); plot_mass()
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))
