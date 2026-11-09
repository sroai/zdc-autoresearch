#!/usr/bin/env python3
"""Cluster-shape and decay-position views of the Λ → n π⁰ → n γ γ events, as plots and as metrics.

Two views, requested by the user on 2026-11-05 (D-user-15):

1. Decay-position view (after the toy model of the 2026-11 MSF talk, built here from
   full simulation): for each D4 momentum, the Λ decay position z (true vertex of the
   daughters, global z) in 1 m bins. Left axis, stacked, the fraction of events at that z
   in which both photons are separated (S0 for both γ) / both have a pure best cluster but one
   holds < 50 % of its photon's clustered energy ("split") / a photon's best cluster is shared,
   purity < 0.8 ("merged") / at least one photon has no cluster holding its energy. Right axis, an independent scale: cumulative curves normalised to the D4
   events (Λ → n π⁰ decays before the ZDC with all daughters in the generator's acceptance
   = 100 % at the ZDC face; no branching ratio): all events, neutron separated, all three
   separated (S0all), Λ reconstructed and truth-matched (S4a_tm).

2. Cluster-shape view (Fig. 5 of S. J. Paul et al., arXiv:2412.12346): for each D4
   momentum, every ZDC cluster's z_cl − z_front against its length ℓ, and its width w_T
   against ℓ, with the marginals. ℓ = the largest √eigenvalue of the shape (shapeParameters
   4–6), w_T = the second largest, z_cl the cluster z in the proton frame (the rotation of
   FarForwardNeutralsReconstruction::isGamma). The photon cut boxes are drawn: stock
   (ℓ < 100, w_T < 12 mm), PR eic/EICrecon#3114 (ℓ < 110, w_T < 22 mm); the z cut of
   EICrecon (gammaZMaxOffset 400 mm past `HcalFarForwardZDC_SiPMonTile_r_pos`, which is
   the ZDC centre, 36716.4 mm: 1316 mm past the front face) and the paper's 300 mm.
   Metrics: the fraction of truth-best photon clusters (D4, D2) and of truth-best neutron
   clusters (D4, D3) that pass isGamma under each cut set (exact EICrecon logic: any
   √eigenvalue > maxLength fails; two or more > maxWidth fail; z above the z cut fails).

Reads the reco files and the truth tables of scripts/410_truth_match.py.
Writes {space}/perf/shape-<experiment>.json and plots into
{space}/plots/<phase>/<experiment>/shape_decayz/.

Usage:
  uv run scripts/430_shape_decayz.py R0_stock --phase phase1
"""
import argparse
import json
import re
import sys
from pathlib import Path

import awkward as ak
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, metrics_config, reco_dir, repo_path  # noqa: E402
from zdc.edm import read_collection, read_vector_member  # noqa: E402

PERF = repo_path("space", "perf")
ROT = -0.025                     # globalToProtonRotation (frozen)
Z_FRONT = 35800.0                # HcalFarForwardZDC_SiPMonTile_r_pos_front_face [mm], epic_craterlake 26.11
Z_CENTRE = 36716.368             # HcalFarForwardZDC_SiPMonTile_r_pos = front + length/2 (length 1832.736 mm)
CUTS = {                         # name: (maxLength, maxWidth, z cut in proton-frame z)
    "stock": (100.0, 12.0, Z_CENTRE + 400.0),
    "pr3114": (110.0, 22.0, Z_CENTRE + 400.0),
    "paper_z300": (100.0, 12.0, Z_FRONT + 300.0),
}
# reference palette (dataviz skill, validated: aqua / violet / orange)
C_SEP, C_SPLIT, C_MERGED, C_MISS = "#1baf7a", "#eda100", "#6250d6", "#eb6834"   # stacked in this order
INK, INK2, BLUE, RED = "#0b0b0b", "#52514e", "#2a78d6", "#e34948"


def momentum_of(path):
    m = re.search(r"_(\d+)GeV", Path(path).name)
    return int(m.group(1)) if m else None


def cluster_table(path, mcfg):
    """Per cluster of one file: event, index in event, E, proton-frame z, ℓ, w_T, and the three √eigenvalues."""
    c = mcfg.collections.zdc_clusters
    f = read_collection(path, c, ["energy", "position.x", "position.z"])
    n = ak.num(f["energy"])
    ev = np.repeat(np.arange(len(n)), ak.to_numpy(n))
    idx = ak.to_numpy(ak.flatten(ak.local_index(f["energy"])))
    x, z = ak.to_numpy(ak.flatten(f["position.x"])), ak.to_numpy(ak.flatten(f["position.z"]))
    zp = z * np.cos(ROT) + x * np.sin(ROT)
    lam = np.stack([read_vector_member(path, c, "shapeParameters", k) for k in (4, 5, 6)], axis=1)
    s = np.sqrt(np.clip(lam, 0, None))
    srt = np.sort(s, axis=1)                       # ascending; NaN sorts last
    return {"event": ev, "idx": idx, "E": ak.to_numpy(ak.flatten(f["energy"])), "zp": zp,
            "l": srt[:, 2], "w": srt[:, 1], "s": s}


def is_gamma(s, zp, cut):
    L, W, zmax = cut
    long_ = (s > L).any(axis=1)
    wide = (s > W).sum(axis=1) >= 2
    return ~(long_ | wide | (zp > zmax))


def truth_table(exp, ds, stem, profile):
    p = reco_dir(profile, exp, ds) / "truth" / f"{stem}.npz"
    return np.load(p)["table"] if p.exists() else None


def best_cluster_rows(cl, tt, roles):
    """Row indices into the cluster table for the truth-best clusters of the given roles."""
    key = {(int(e), int(i)): k for k, (e, i) in enumerate(zip(cl["event"], cl["idx"]))}
    sel = tt[np.isin(tt["role"], roles) & (tt["cluster"] >= 0)]
    rows = [key.get((int(r["event"]), int(r["cluster"]))) for r in sel]
    return np.array([r for r in rows if r is not None], dtype=int)


def gamma_rawsum(tt, roles):
    """Mean over the photons of (their energy in all surviving clusters) / E_true: the photon raw sum
    (D-user-16, Q9 A; a photon without any cluster counts 0). assoc_E is 410's containment denominator."""
    t = tt[np.isin(tt["role"], roles)]
    if not len(t):
        return None
    e_true = np.sqrt(t["true_px"].astype(float) ** 2 + t["true_py"] ** 2 + t["true_pz"] ** 2)
    return float(np.mean(t["assoc_E"] / e_true))


def rawsum_table(profile, exp):
    out = {}
    for ds, roles in (("D2_photon", ["p"]), ("D4_lambda", ["g1", "g2"])):
        d = reco_dir(profile, exp, ds) / "truth"
        for f in sorted(d.glob("*.edm4eic.npz")):
            v = gamma_rawsum(np.load(f)["table"], roles)
            if v is not None:
                out.setdefault(ds.split("_")[0], {})[str(momentum_of(f))] = v
    return out


def decayz_plot(exp, p, tt, lt, out):
    ev = np.unique(tt["event"])
    dz = {}
    cat = {}
    for e in ev:
        r = tt[tt["event"] == e]
        g = r[np.isin(r["role"], ["g1", "g2"])]
        n = r[r["role"] == "n"]
        if len(g) != 2 or len(n) != 1:
            continue
        dz[e] = float(n["true_vz"][0]) / 1000.0
        if (g["cluster"] < 0).any():
            c = "miss"
        elif g["separated"].all():
            c = "sep"
        elif (g["purity"] < 0.8).any():
            c = "merged"          # a photon's best cluster is shared with another particle
        else:
            c = "split"           # pure, but a photon's best cluster holds < 50 % of its clustered energy
        cat[e] = (c, bool(n["separated"][0]), bool(r["separated"].all()))
    evs = np.array(sorted(dz))
    z = np.array([dz[e] for e in evs])
    lam_ok = {int(e): bool(m) for e, m in zip(lt["event"], lt["matched"])} if lt is not None else {}
    bins = np.arange(0, 37, 1.0)
    frac = {k: np.zeros(len(bins) - 1) for k in ("sep", "split", "merged", "miss")}
    counts = np.histogram(z, bins)[0]
    for k in frac:
        sel = np.array([cat[e][0] == k for e in evs])
        frac[k] = np.divide(np.histogram(z[sel], bins)[0], counts, out=np.full(len(counts), np.nan), where=counts > 0)
    order = np.argsort(z)
    zs = z[order]
    N = len(zs)
    cum = lambda flags: 100.0 * np.cumsum(flags[order]) / N  # noqa: E731
    all_ = cum(np.ones(N))
    nsep = cum(np.array([cat[e][1] for e in evs], dtype=float))
    s0all = cum(np.array([cat[e][2] for e in evs], dtype=float))
    s4a = cum(np.array([lam_ok.get(int(e), False) for e in evs], dtype=float))

    fig, ax = plt.subplots(figsize=(9, 6.6))
    left = bins[:-1]
    w = np.diff(bins)
    bottom = np.zeros(len(left))
    for k, col, lab in (("sep", C_SEP, "both γ separated (S0)"),
                        ("split", C_SPLIT, "γ split: pure, but best cluster < 50 % of it"),
                        ("merged", C_MERGED, "γ merged: best cluster shared (purity < 0.8)"),
                        ("miss", C_MISS, "≥ 1 γ without a cluster")):
        b = np.nan_to_num(frac[k])
        ax.bar(left, b, w, bottom=bottom, align="edge", color=col, edgecolor="white", linewidth=0.6, label=lab)
        bottom = bottom + b
    ax.set_xlim(0, 36)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Λ decay position z (true, global) [m]")
    ax.set_ylabel("fraction of events at this z (stacked bars)")
    ax2 = ax.twinx()
    ax2.plot(zs, all_, color=INK, lw=2, label="all D4 events (n π⁰ before ZDC = 100 %)")
    ax2.plot(zs, nsep, color=BLUE, lw=2, ls="--", label="neutron separated")
    ax2.plot(zs, s0all, color=INK, lw=2, ls=(0, (5, 3)), label="n + γ + γ all separated (S0all)")
    ax2.plot(zs, s4a, color=RED, lw=2, ls=":", label="Λ reconstructed, truth-matched (S4a_tm)")
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("cumulative, % of D4 events (curves; independent scale)")
    ax.set_title(f"{exp}  D4 Λ gun {p} GeV  ({N} events)", fontsize=11)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)
    for s in ("top",):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(out / f"decayz_D4_{p}GeV.png", dpi=130)
    plt.close(fig)
    return {"events": int(N), "frac_sep_both_g": float(np.mean([cat[e][0] == "sep" for e in evs])),
            "frac_merged": float(np.mean([cat[e][0] == "merged" for e in evs])),
            "frac_split": float(np.mean([cat[e][0] == "split" for e in evs])),
            "frac_g_missing": float(np.mean([cat[e][0] == "miss" for e in evs])),
            "z_median_m": float(np.median(z))}


def shape_plot(exp, p, cl, gam_rows, n_rows, out):
    fig = plt.figure(figsize=(6.4, 8.6))
    gs = fig.add_gridspec(3, 2, width_ratios=[1, 4], height_ratios=[4, 4, 1], hspace=0.05, wspace=0.05)
    a_top, a_bot = fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1])
    m_top, m_bot, m_x = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[2, 1])
    ok = np.isfinite(cl["l"]) & np.isfinite(cl["w"])
    l, w, dz = cl["l"][ok], cl["w"][ok], (cl["zp"] - Z_FRONT)[ok]
    lb, wb, zb = np.linspace(0, 400, 81), np.linspace(0, 40, 81), np.linspace(0, 2000, 81)
    h1 = a_top.hist2d(l, dz, [lb, zb], norm=LogNorm(), cmap="viridis")
    a_bot.hist2d(l, w, [lb, wb], norm=LogNorm(), cmap="viridis")
    m_top.hist(dz, zb, orientation="horizontal", color=BLUE)
    m_bot.hist(w, wb, orientation="horizontal", color=BLUE)
    m_x.hist(l, lb, color=BLUE)
    for m in (m_top, m_bot):
        m.invert_xaxis()
        m.set_xticks([])
    for a in (a_top, a_bot):
        a.set_yticklabels([])
    a_top.set_xticklabels([])
    a_bot.set_xticklabels([])
    m_top.set_ylabel("z_cl − z_front [mm]")
    m_bot.set_ylabel("width w_T [mm]")
    m_x.set_xlabel("length ℓ [mm]")
    m_x.set_yticks([])
    for name, (L, W, zc), col in (("stock", CUTS["stock"], RED), ("PR 3114", CUTS["pr3114"], "#eda100")):
        a_bot.plot([0, L, L], [W, W, 0], color=col, lw=1.6, label=f"{name}: ℓ<{L:.0f}, w<{W:.0f}")
        a_top.plot([L, L], [0, 2000], color=col, lw=1.2)
    a_top.axhline(CUTS["stock"][2] - Z_FRONT, color=RED, lw=1.2, ls="--")
    a_top.axhline(300, color=INK2, lw=1.2, ls=":")
    a_top.text(395, CUTS["stock"][2] - Z_FRONT + 25, "EICrecon z cut (centre + 400)", ha="right", fontsize=7, color=RED)
    a_top.text(395, 325, "paper z cut (front + 300)", ha="right", fontsize=7, color=INK2)
    a_bot.scatter(cl["l"][n_rows], cl["w"][n_rows], s=1.2, color=INK2, alpha=0.35, label="truth-best n clusters")
    a_bot.scatter(cl["l"][gam_rows], cl["w"][gam_rows], s=1.5, color=C_MISS, alpha=0.6, label="truth-best γ clusters")
    a_bot.legend(fontsize=7, loc="upper right", markerscale=5)
    for a in (a_top, a_bot, m_x):
        a.set_xlim(0, 400)
    a_top.set_ylim(0, 2000)
    m_top.set_ylim(0, 2000)
    a_bot.set_ylim(0, 40)
    m_bot.set_ylim(0, 40)
    fig.colorbar(h1[3], ax=[a_top, a_bot], fraction=0.04, pad=0.02, label="clusters")
    fig.suptitle(f"{exp}  D4 Λ {p} GeV: ZDC cluster shapes (cf. arXiv:2412.12346 Fig. 5)", fontsize=10)
    fig.savefig(out / f"shape_D4_{p}GeV.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def pass_fractions(cl, rows):
    if len(rows) == 0:
        return {k: None for k in CUTS}
    return {k: float(is_gamma(cl["s"][rows], cl["zp"][rows], c).mean()) for k, c in CUTS.items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment")
    ap.add_argument("--phase", default="phase1")
    ap.add_argument("--compare", metavar="REF", help="judge the photon raw-sum guard against REF (D-user-16)")
    ap.add_argument("--decayz-only", action="store_true", help="only the decay-position plots (fast; truth tables)")
    ap.add_argument("--rawsum-only", action="store_true", help="only the photon raw sum (fast; reads the truth tables)")
    args = ap.parse_args()
    profile, mcfg = load_profile(), metrics_config()
    rs = rawsum_table(profile, args.experiment)
    lim = float(mcfg.limits.gamma_raw_sum_rel_drop_max)
    guard = None
    if args.compare:
        ref = rawsum_table(profile, args.compare)
        guard = {}
        for ds in rs:
            for p, v in sorted(rs[ds].items(), key=lambda kv: int(kv[0])):
                r = ref.get(ds, {}).get(p)
                if r:
                    rel = v / r - 1
                    ok = rel >= -lim if ds == "D2" else None      # D4 photons: reported, not a guard
                    guard.setdefault(ds, {})[p] = {"rel_change": rel, "pass": ok}
                    print(f"photon raw sum {ds} {p:>4s} GeV  {r:.4f} -> {v:.4f}  ({rel:+.1%})"
                          + ("" if ok is None else ("  in" if ok else "  OUT (drop > 5 %)")))
    if args.decayz_only:
        out = repo_path("space", "plots", args.phase, args.experiment, "shape_decayz")
        out.mkdir(parents=True, exist_ok=True)
        path = PERF / f"shape-{args.experiment}.json"
        res = json.loads(path.read_text()) if path.exists() else {"experiment": args.experiment, "D4": {}}
        d = reco_dir(profile, args.experiment, "D4_lambda") / "truth"
        for f in sorted(d.glob("*.edm4eic.npz")):
            p = momentum_of(f)
            lp = f.with_name(f.name.replace(".npz", ".lambda.npz"))
            lt = np.load(lp)["table"] if lp.exists() else None
            res.setdefault("D4", {}).setdefault(str(p), {})["decayz"] = decayz_plot(args.experiment, p, np.load(f)["table"], lt, out)
        path.write_text(json.dumps(res, indent=1))
        print(f"decay-z plots redrawn in {out}")
        return
    if args.rawsum_only:
        path = PERF / f"shape-{args.experiment}.json"
        res = json.loads(path.read_text()) if path.exists() else {"experiment": args.experiment}
        res["gamma_rawsum"] = rs
        if guard is not None:
            res["gamma_rawsum_guard_vs"] = {"reference": args.compare, **guard}
        path.write_text(json.dumps(res, indent=1))
        print(f"updated {path}")
        return
    out = repo_path("space", "plots", args.phase, args.experiment, "shape_decayz")
    out.mkdir(parents=True, exist_ok=True)
    res = {"experiment": args.experiment, "cuts": {k: list(v) for k, v in CUTS.items()},
           "z_front_mm": Z_FRONT, "z_centre_mm": Z_CENTRE, "D4": {}, "D2": {}, "D3": {}}
    for ds, roles_g, roles_n in (("D4_lambda", ["g1", "g2"], ["n"]), ("D2_photon", ["p"], []), ("D3_neutron", [], ["p"])):
        d = reco_dir(profile, args.experiment, ds)
        files = sorted(d.glob("*.edm4eic.root"))
        if not files:
            print(f"{ds}: no reco files under {d}")
            continue
        for f in files:
            p = momentum_of(f)
            stem = f.name.replace(".root", "")
            tt = truth_table(args.experiment, ds, stem, profile)
            if tt is None:
                print(f"{ds} {p}: no truth table (run 410 first)")
                continue
            cl = cluster_table(f, mcfg)
            g_rows = best_cluster_rows(cl, tt, roles_g) if roles_g else np.array([], int)
            n_rows = best_cluster_rows(cl, tt, roles_n) if roles_n else np.array([], int)
            entry = {"gamma_pass": pass_fractions(cl, g_rows), "neutron_pass": pass_fractions(cl, n_rows),
                     "n_gamma_clusters": int(len(g_rows)), "n_neutron_clusters": int(len(n_rows))}
            if ds == "D4_lambda":
                lp = reco_dir(profile, args.experiment, ds) / "truth" / f"{stem}.lambda.npz"
                lt = np.load(lp)["table"] if lp.exists() else None
                entry["decayz"] = decayz_plot(args.experiment, p, tt, lt, out)
                shape_plot(args.experiment, p, cl, g_rows, n_rows, out)
            res[ds.split("_")[0]][str(p)] = entry
            gp, npass = entry["gamma_pass"], entry["neutron_pass"]
            fmt = lambda x: "  —  " if x is None else f"{x:.3f}"  # noqa: E731
            print(f"{ds:11s} {p:4d} GeV  γ pass stock/pr3114/paper {fmt(gp['stock'])} {fmt(gp['pr3114'])} {fmt(gp['paper_z300'])}"
                  f"   n pass {fmt(npass['stock'])} {fmt(npass['pr3114'])} {fmt(npass['paper_z300'])}"
                  + (f"   γγ sep/split/merged/miss {entry['decayz']['frac_sep_both_g']:.3f}/{entry['decayz']['frac_split']:.3f}/{entry['decayz']['frac_merged']:.3f}/"
                     f"{entry['decayz']['frac_g_missing']:.3f}" if "decayz" in entry else ""))
    res["gamma_rawsum"] = rs
    if guard is not None:
        res["gamma_rawsum_guard_vs"] = {"reference": args.compare, **guard}
    (PERF / f"shape-{args.experiment}.json").write_text(json.dumps(res, indent=1))
    print(f"wrote {PERF / f'shape-{args.experiment}.json'}; plots in {out}")


if __name__ == "__main__":
    main()
