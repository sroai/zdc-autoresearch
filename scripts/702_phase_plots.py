#!/usr/bin/env python3
"""Plots of Phases 4 and 6 (PNG) into space/plots/phase<N>/ (work-common: plots live in {space}/plots/phase{#}/).
Phase 5's plots are made by slides/phase5/make_phase5_plots.py, which writes to space/plots/phase5/.

Inputs (read at run time; a missing row is left out):
  space/perf/headline.csv                        S4a_tm per thrown Λ → nπ⁰ on the D4 gun, per momentum (441)
  space/perf/msf-regimes-<row>-<dataset>.json   N_found / N_expected per beam (210)
  space/perf/msf-select-<try>-vs-<best>-D6s.json the selector's verdict of a try (463)
  space/perf/t-resolution-<row>.json             −t resolution of the found Λ (476)
  space/perf/calib-crystal-CAL6_D2_Y9-rcol60.json  the launched crystal photon law on the photon guns (477 --fit-guns)
  {reco}/<row>/D6s_9x275/*.edm4eic.root          every ReconstructedLambdas mass (Phase 6 mass plot)
Colours: the dataviz reference palette's first three slots, as Phase 5's plots.

Usage:  uv run scripts/702_phase_plots.py 4 6
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PERF = REPO / "space" / "perf"
RECO = Path("/data/zdc-autoresearch/reco")
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID, SURFACE, PALE = "#0b0b0b", "#52514e", "#dddcd8", "#ffffff", "#efeeea"
REACH = {"9x275": 43.6, "9x130": 8.0}
M_L = 1.115683
MOMENTA = [100, 125, 150, 175, 200, 225, 250, 275]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
                     "axes.axisbelow": True, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
                     "axes.spines.top": False, "axes.spines.right": False})


def out_dir(phase):
    d = REPO / "space" / "plots" / f"phase{phase}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save(fig, phase, name):
    path = out_dir(phase) / name
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print("wrote", path.relative_to(REPO))


def jload(name):
    p = PERF / name
    return json.loads(p.read_text()) if p.exists() else None


def headline():
    with open(PERF / "headline.csv") as fh:
        return {r["row"]: r for r in csv.DictReader(fh)}


def num(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(x) else x


# --- Phase 4: the Λ bar fight on the D4 gun ----------------------------------------------------------------------------

P4_STEPS = [("R1", "R1_pr3064"), ("X1", "X1_offline_chain"), ("X2", "X2_lambda_pairing"), ("X3", "X3_pairing_weights"),
            ("X4", "X4_photon_depth"), ("X5", "X5_photon_depth_face"), ("X6", "X6_zdc_face"), ("X7", "X7_core_split"),
            ("X8", "X8_core_depth_centroid"), ("X9", "X9_pairing_photon_depth")]


def phase4():
    H = headline()
    fig, ax = plt.subplots(figsize=(13, 4.8))
    for col, colour, lab in (("S4a_tm_per_thrown_mean", BLUE, "mean 100–275 GeV"), ("S4a_tm_per_thrown_275", ORANGE, "275 GeV")):
        pts = [(i, num(H[row][col])) for i, (_, row) in enumerate(P4_STEPS) if row in H and num(H[row].get(col)) is not None]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=colour, lw=2, marker="o", ms=8, label=lab, zorder=3)
        for x, y in pts[-1:]:
            ax.annotate(f"{y:.2f} %", (x, y), textcoords="offset points", xytext=(10, 6), color=INK, fontsize=11)
    for c, lab in ((14.1, "ceiling, mean"), (27.8, "ceiling, 275 GeV")):
        ax.axhline(c, color=MUTED, lw=1.2, ls=":")
        ax.text(0.1, c, f"{lab} {c} %", va="bottom", color=MUTED, fontsize=11)
    ax.set_xticks(range(len(P4_STEPS)), [s[0] for s in P4_STEPS])
    ax.set_ylim(0, 31)
    ax.set_ylabel("S4a_tm per thrown Λ → nπ⁰ (%)")
    ax.set_title("Phase 4 — truth-matched Λ per thrown on the D4 gun, try by try (X6 rejected)", color=INK, fontsize=14, loc="left")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.86), frameon=False)
    save(fig, 4, "p4_d4_progression.png")

    fig, ax = plt.subplots(figsize=(13, 4.8))
    for row, colour, lab in (("R1_pr3064", MUTED, "R1 (PR 3064), start"), ("X5_photon_depth_face", BLUE, "X5"),
                             ("X9_pairing_photon_depth", ORANGE, "X9, end of Phase 4")):
        if row not in H:
            continue
        y = [num(H[row].get(f"S4a_tm_per_thrown_{p}")) for p in MOMENTA]
        ax.plot(MOMENTA, y, color=colour, lw=2, marker="o", ms=7, label=lab, zorder=3)
    ax.set_xticks(MOMENTA)
    ax.set_xlabel("Λ momentum (GeV)")
    ax.set_ylabel("S4a_tm per thrown Λ → nπ⁰ (%)")
    ax.set_title("Phase 4 — truth-matched Λ per thrown on the D4 gun, by momentum", color=INK, fontsize=14, loc="left")
    ax.legend(loc="upper left", frameon=False)
    save(fig, 4, "p4_d4_by_momentum.png")


# --- Phase 6: the crystal-seeded ZDC photon finder ---------------------------------------------------------------------

P6_STEPS = [("Y9", "MSF6_Y9", None), ("Z1", "Z1_crystal_photons", "MSF6_Y9"), ("Z1b", "Z1b_crystal_column", "MSF6_Y9"),
            ("Z2", "Z2_crystal_params", "Z1b_crystal_column"), ("Z4", "Z4_lambda_sigma", "Z2_crystal_params"),
            ("Z5", "Z5_crystal_energy_alt", "Z4_lambda_sigma"), ("Z6", "Z6_alt_column_out", "Z5_crystal_energy_alt"),
            ("Z7", "Z7_isolation", "Z6_alt_column_out"), ("Z8", "Z8_hcal_axis_law", "Z7_isolation")]
T_ROWS = [("Y9", "Y9_external_pair", MUTED), ("Z5", "Z5_crystal_energy_alt", ORANGE), ("Z8", "Z8_hcal_axis_law", BLUE)]


def yield_of(row, ds):
    d = jload(f"msf-regimes-{row}-{ds}.json")
    return 100 * d["rows"][row]["yield"] if d and row in d.get("rows", {}) else None


def verdict(row, best):
    d = jload(f"msf-select-{row}-vs-{best}-D6s.json") if best else None
    return (d or {}).get("verdict")


def phase6():
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    for ax, beam in zip(axes, ("9x275", "9x130")):
        pts = [(i, lab, yield_of(row, f"D6s_{beam}"), verdict(row, best)) for i, (lab, row, best) in enumerate(P6_STEPS)]
        pts = [p for p in pts if p[2] is not None]
        ax.plot([p[0] for p in pts], [p[2] for p in pts], color=BLUE, lw=2, zorder=2, label="search half")
        for x, lab, y, v in pts:
            filled = v is None or str(v).startswith("ACCEPT")
            ax.plot(x, y, marker="o", ms=9, color=BLUE, mfc=BLUE if filled else SURFACE, mew=2, zorder=3)
            ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0, 10), ha="center", color=INK, fontsize=11)
        held = [(i, yield_of(row, f"D6h_{beam}")) for i, (_, row, _) in enumerate(P6_STEPS)]
        held = [h for h in held if h[1] is not None]
        if held:
            ax.plot([h[0] for h in held], [h[1] for h in held], ls="none", marker="D", ms=8, color=ORANGE, zorder=3,
                    label="held-out half")
        ax.set_xticks(range(len(P6_STEPS)), [s[0] for s in P6_STEPS])
        lo = min(p[2] for p in pts); hi = max(p[2] for p in pts)
        ax.set_ylim(lo * 0.85, hi * 1.12)
        ax.set_ylabel("Λ → nπ⁰ found / expected (%)")
        ax.set_title(f"MSF {beam} (reachable {REACH[beam]} %)", color=INK, fontsize=14, loc="left")
    axes[0].legend(loc="lower right", frameon=False, fontsize=11)
    fig.suptitle("Phase 6 — found Λ per try; open circle = not accepted by the selector (Z6 became the base by the user's choice)",
                 color=INK, fontsize=13, x=0.01, ha="left")
    save(fig, 6, "p6_found_per_try.png")

    # −t resolution per −t bin
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
    for ax, beam in zip(axes, ("9x275", "9x130")):
        width = 0.26
        for k, (lab, row, colour) in enumerate(T_ROWS):
            d = jload(f"t-resolution-{row}.json")
            if not d or beam not in d:
                continue
            bins = [b for b, v in d[beam]["bins"].items() if v.get("n", 0) >= 30]
            x = np.arange(len(bins))
            y = [d[beam]["bins"][b]["sigma68"] for b in bins]
            ax.bar(x + (k - 1) * width, y, width=width * 0.94, color=colour,
                   label=f"{lab}: all −t {d[beam]['sigma68']:.3f} GeV²", zorder=2)
            ax.set_xticks(x, [b.replace("-", "–") for b in bins])
        ax.set_xlabel("true −t bin (GeV²)")
        ax.set_title(f"MSF {beam}, found Λ", color=INK, fontsize=14, loc="left")
        ax.legend(loc="upper left", frameon=False, fontsize=11)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("σ68 of −t reco − true (GeV²)")
    fig.suptitle("Phase 6 — −t resolution of the found Λ: Y9 (start), Z5, Z8 (current best)", color=INK, fontsize=13, x=0.01, ha="left")
    save(fig, 6, "p6_t_resolution.png")

    # the crystal photon law on the photon guns
    law = jload("calib-crystal-CAL6_D2_Y9-rcol60.json")
    if law:
        pe = sorted(((float(e), v) for e, v in law["per_energy"].items()), key=lambda t: t[0])
        fig, ax = plt.subplots(figsize=(13, 4.8))
        e = [p[0] for p in pe]; r = [p[1]["ratio_median"] for p in pe]; s = [p[1]["ratio_sigma68"] for p in pe]
        ax.axhline(1.0, color=MUTED, lw=1.2, ls=":")
        ax.errorbar(e, r, yerr=s, color=BLUE, lw=2, marker="o", ms=8, capsize=4, label="median, bar = σ68")
        ax.axvspan(5, 50, color=PALE, zorder=0)
        ax.text(6, 1.27, "MSF window photons: 5–50 GeV (fit range)", color=MUTED, fontsize=11)
        ax.set_xscale("log")
        ax.set_xticks(e, [f"{x:g}" for x in e])
        ax.set_ylim(0.7, 1.32)
        ax.set_xlabel("gun photon energy (GeV)")
        ax.set_ylabel("E_law / E_true")
        ax.set_title(f"Phase 6 — crystal photon law {law['a']:.3f}·E_crys + {law['b']:.2f}·E_col {law['c']:+.3f} on the photon guns "
                     "(D2c, D2)", color=INK, fontsize=13, loc="left")
        ax.legend(loc="lower right", frameon=False)
        save(fig, 6, "p6_crystal_law.png")

    # Λ mass on 9x275: Y9 and Z6
    import awkward as ak
    import uproot
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
    bins = np.linspace(0.95, 1.30, 71)
    for ax, (row, lab) in zip(axes, (("MSF6_Y9", "Y9, start of Phase 6"), ("Z8_hcal_axis_law", "Z8, current best"))):
        files = sorted((RECO / row / "D6s_9x275").glob("*.edm4eic.root"))
        allm = np.concatenate([ak.to_numpy(ak.flatten(uproot.open(f)["events"]["ReconstructedLambdas.mass"].array())) for f in files]) \
            if files else np.array([])
        d = jload(f"msf-regimes-{row}-D6s_9x275.json")
        good = np.array([l[row]["mass"] for l in d["per_lambda"] if l[row]["matched"]]) if d else np.array([])
        ax.axvspan(M_L - 0.03, M_L + 0.03, color=PALE, zorder=0)
        ax.hist(allm, bins=bins, histtype="step", color=MUTED, lw=2, label="every candidate")
        ax.hist(good, bins=bins, color=BLUE, alpha=0.85, label="truth-matched Λ → nπ⁰")
        nw = int(np.sum(np.abs(allm - M_L) < 0.03))
        ax.text(0.98, 0.62, f"in ±30 MeV: {nw} candidates,\n{len(good)} truth-matched ({100 * len(good) / max(nw, 1):.1f} %)",
                transform=ax.transAxes, ha="right", va="top", color=INK, fontsize=12)
        ax.set_title(lab + " — MSF 9x275, search half", color=INK, fontsize=14, loc="left")
        ax.set_xlabel("reconstructed Λ mass (GeV)")
    axes[0].set_ylabel("candidates / 5 MeV")
    axes[0].legend(loc="upper left", frameon=False, fontsize=11)
    save(fig, 6, "p6_mass.png")


if __name__ == "__main__":
    for ph in sys.argv[1:] or ["4", "6"]:
        {"4": phase4, "6": phase6}[ph]()
