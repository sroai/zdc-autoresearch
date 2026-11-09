#!/usr/bin/env python3
"""The scoreboard: every fixed metric of zdc-setup.md (section Scoreboard) for one reconstruction.

Inputs: the reconstruction outputs under {reco_root}/<experiment>/<dataset>/ and
the truth-match tables scripts/410_truth_match.py writes beside them
(truth/<file>.npz per particle, truth/<file>.lambda.npz per Λ event) and into
{space}/perf/truth-<experiment>-<dataset>.json. Run 410 first.

Outputs: {space}/perf/metrics-<experiment>.json (every cell, with errors) and one
row in {space}/perf/scoreboard.csv (replacing an older row of the same experiment).

Cells, per momentum p (suffix _<p>) and averaged over momenta (suffix _mean):
  S0  (D4)  S0_g, S0_n, S0_all: separated fraction of true photons, neutrons, events with all three; the selector
  S1  (D1)  S1a_truth (both photons separated), S1a_raw (exactly two clusters); S1b γγ mass of the two
            best-matched clusters (fit μ, σ; fraction within ±3σ); S1c π⁰ energy scale and resolution (two-cluster
            events, the benchmark's recipe); S1d photon position resolution at the cluster (robust σ of Δx, Δy)
  S2  (D2)  corrected energy of the neutral built from the best-matched cluster: scale μ/E, |μ/E − 1|, σ/μ;
            θ resolution (mrad, proton frame); γ-tag efficiency
  S3  (D3)  raw Σ E(clusters)/E (mean, σ); corrected scale of the best cluster's neutral; θ resolution;
            clusters holding neutron energy; γ-tagged energy fraction; n mis-tag rate
  S4  (D4)  S4a truth-matched Λ efficiency, the raw any-Λ fraction, the truth-chain ceiling Rt;
            S4b mass μ, σ and decay-z resolution of truth-matched Λs; S4c γ-tagged neutrals per event
  G1–G3 (D5) per DIS sample: φ at ±180°, single-column clusters, energy above 50 GeV (and χ² of the
            log-energy spectrum against R0), clusters below 1 GeV per event, nhits median, clusters per event
  T         reconstruction seconds per 1000 events per dataset (median over files)

--compare REF prints the paired test against REF on identical events (zdc-setup.md, Noise and
significance): McNemar on the discordant events for S0_g, S0_n, S0_all, S1a_truth and S4a_tm;
an event bootstrap (fixed seed, the same resamples for both) for S2 scale (the median of E/p: a
Gaussian peak does not exist for every clustering), S3 raw sum and S4b σ.

Usage:
  uv run scripts/400_scoreboard.py R0_stock
  uv run scripts/400_scoreboard.py E03_nhits5 --compare R0_stock
  uv run scripts/400_scoreboard.py R0_stock --datasets D4_lambda      # partial row (marked partial)
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import awkward as ak
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import datasets_config, load_profile, metrics_config, repo_path  # noqa: E402
from zdc.edm import binomial_error, collection_ids, fit_peak, read_collection, rotate_to_proton_frame  # noqa: E402

PERF = repo_path("space", "perf")


# ---------------------------------------------------------------- inputs

def files_of(profile, experiment, dataset):
    d = Path(profile.reco_root) / experiment / dataset
    return sorted(f for f in d.glob("*.edm4eic.root") if ".part." not in f.name)


def momentum_of(path):
    token = [t for t in Path(path).name.split("_") if t.endswith("GeV")]
    return int(token[0][:-3]) if token else -1


def by_momentum(files):
    """{momentum_gev: [files]} from names like D1_pi0_100GeV_seed1.edm4eic.root."""
    groups = {}
    for f in files:
        groups.setdefault(momentum_of(f), []).append(f)
    return dict(sorted(groups.items()))


def truth_table(files, suffix=".npz"):
    """The concatenated 410 tables of these files (per particle, or per Λ event with suffix .lambda.npz)."""
    parts = []
    for f in files:
        t = f.parent / "truth" / f"{f.stem}{suffix}"
        if t.exists():
            parts.append(np.load(t)["table"])
    return np.concatenate(parts) if parts else None


def truth_summary(experiment, dataset):
    path = PERF / f"truth-{experiment}-{dataset}.json"
    return json.loads(path.read_text()) if path.exists() else None


def robust_sigma(values):
    """Half the 16–84 % interval: a width that ignores the tails a Gaussian fit would also ignore."""
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    return float(0.5 * (np.percentile(values, 84) - np.percentile(values, 16))) if len(values) >= 10 else float("nan")


def theta_proton_frame(px, py, pz, tilt):
    qx, qy, qz = rotate_to_proton_frame(np.asarray(px, float), np.asarray(py, float), np.asarray(pz, float), tilt)
    return np.arctan2(np.hypot(qx, qy), qz)


def mean_over(out, prefix):
    vals = [v for k, v in out.items() if k.startswith(prefix + "_") and k[len(prefix) + 1:].isdigit() and np.isfinite(v)]
    return float(np.mean(vals)) if vals else float("nan")


def energy_fit(values, half_width_rel=0.2):
    """Gaussian peak of an energy (or ratio) distribution around its median; None when it fails."""
    values = np.asarray(values, float)
    values = values[np.isfinite(values) & (values > 0)]
    if len(values) < 25:
        return None
    med = float(np.median(values))
    return fit_peak(values, med, half_width_rel * med)


# ---------------------------------------------------------------- S0 and S1

def s0_cells(summary, prefix="S0"):
    """Separated fractions per momentum with their binomial errors, from the 410 summary."""
    out = {}
    for p, per in summary["per_momentum"].items():
        flags = summary["event_flags"][p]
        particles = flags.get("particles", [])
        for role, key in (("g", "S0_g_sep"), ("n", "S0_n_sep"), ("all", "S0_all_sep"), ("p", "S0_p_sep")):
            if key not in per:
                continue
            if role == "all":
                n = len(flags["events"])
            elif role == "g":
                n = sum(1 for _, r, _ in particles if r in ("g1", "g2"))
            else:
                n = sum(1 for _, r, _ in particles if r == role)
            out[f"{prefix}_{role}_{p}"] = per[key]
            out[f"{prefix}_{role}_err_{p}"] = binomial_error(per[key] * n, n)
    for role in ("g", "n", "all", "p"):
        m = mean_over(out, f"{prefix}_{role}")
        if np.isfinite(m):
            out[f"{prefix}_{role}_mean"] = m
    return out


def s1_pi0(files, mcfg):
    out = {}
    c = mcfg.collections.zdc_clusters
    for p, fs in by_momentum(files).items():
        cl = read_collection(fs, c, ["energy"])
        ncl = ak.num(cl["energy"], axis=1)
        n = len(ncl)
        frac2 = float(ak.mean(ncl == 2)) if n else float("nan")
        out[f"S1a_raw_{p}"], out[f"S1a_raw_err_{p}"] = frac2, binomial_error(frac2 * n, n)
        # S1c, the benchmark's recipe: summed energy of two-cluster events, Gaussian fit ±10 % around p
        etot = ak.to_numpy(ak.sum(cl["energy"][ncl == 2], axis=1))
        efit = fit_peak(etot, p, p * mcfg.fits.energy_fit_half_width_rel)
        if efit:
            out[f"S1c_scale_{p}"], out[f"S1c_res_{p}"] = efit[0] / p, efit[1] / efit[0]
        t = truth_table(fs)
        if t is None:
            continue
        # S1b: the two best-matched clusters of one event, photons pointing from the origin (as the neutrals factory does)
        g1, g2 = t[t["role"] == "g1"], t[t["role"] == "g2"]
        common = np.intersect1d(g1["event"], g2["event"])
        a = g1[np.isin(g1["event"], common)]
        b = g2[np.isin(g2["event"], common)]
        distinct = (a["cluster"] != b["cluster"]) & (a["cluster"] >= 0) & (b["cluster"] >= 0)
        a, b = a[distinct], b[distinct]
        if len(a):
            def mom(r):
                rr = np.sqrt(r["x"] ** 2 + r["y"] ** 2 + r["z"] ** 2)
                return r["E"] * r["x"] / rr, r["E"] * r["y"] / rr, r["E"] * r["z"] / rr
            ax_, ay_, az_ = mom(a)
            bx_, by_, bz_ = mom(b)
            m2 = (a["E"] + b["E"]) ** 2 - (ax_ + bx_) ** 2 - (ay_ + by_) ** 2 - (az_ + bz_) ** 2
            mass = np.sqrt(np.clip(m2, 0, None))
            fit = fit_peak(mass, mcfg.windows.pi0_mass_gev, 0.1)
            if fit:
                out[f"S1b_mass_mu_{p}"], out[f"S1b_mass_sigma_{p}"] = fit[0], fit[1]
                out[f"S1b_frac_in3sigma_{p}"] = float(np.mean(np.abs(mass - fit[0]) < 3 * fit[1]))
        # S1d: best cluster position against the true photon line at the cluster's z
        gam = t[np.isin(t["role"], ["g1", "g2"]) & (t["cluster"] >= 0)]
        if len(gam):
            dz = gam["z"] - gam["true_vz"]
            x_true = gam["true_vx"] + gam["true_px"] / gam["true_pz"] * dz
            y_true = gam["true_vy"] + gam["true_py"] / gam["true_pz"] * dz
            out[f"S1d_dx_sigma_mm_{p}"] = robust_sigma(gam["x"] - x_true)
            out[f"S1d_dy_sigma_mm_{p}"] = robust_sigma(gam["y"] - y_true)
    for key in ("S1a_raw", "S1c_scale", "S1c_res", "S1b_mass_sigma", "S1d_dx_sigma_mm"):
        out[f"{key}_mean"] = mean_over(out, key)
    return out


# ---------------------------------------------------------------- S2 and S3

def neutral_cells(t, p, prefix, tilt, out):
    """Corrected energy scale, resolution and θ resolution of the neutral built from the best-matched cluster."""
    has = (t["neutral_pdg"] != 0) & (t["neutral_E"] > 0)
    out[f"{prefix}_has_neutral_{p}"] = float(np.mean(has)) if len(t) else float("nan")
    ratio = t["neutral_E"][has] / p
    if len(ratio) >= 10:  # robust companions of the fitted cells: defined even where no Gaussian peak exists
        out[f"{prefix}_scale_median_{p}"] = float(np.median(ratio))
        out[f"{prefix}_res_robust_{p}"] = robust_sigma(ratio) / float(np.median(ratio)) if np.median(ratio) > 0 else float("nan")
    fit = energy_fit(ratio)
    if fit:
        out[f"{prefix}_scale_{p}"] = fit[0]
        out[f"{prefix}_scale_absdev_{p}"] = abs(fit[0] - 1.0)
        out[f"{prefix}_res_{p}"] = fit[1] / fit[0]
    sel = t[has]
    if len(sel):
        th_reco = theta_proton_frame(sel["neutral_px"], sel["neutral_py"], sel["neutral_pz"], tilt)
        th_true = theta_proton_frame(sel["true_px"], sel["true_py"], sel["true_pz"], tilt)
        out[f"{prefix}_theta_sigma_mrad_{p}"] = robust_sigma((th_reco - th_true) * 1e3)


def s2_photon(files, mcfg):
    out = {}
    tilt = float(mcfg.crossing_angle_rad)
    for p, fs in by_momentum(files).items():
        t = truth_table(fs)
        if t is None:
            continue
        t = t[t["role"] == "p"]
        neutral_cells(t, p, "S2", tilt, out)
        out[f"S2_gamma_tag_eff_{p}"] = float(np.mean(t["neutral_pdg"] == 22)) if len(t) else float("nan")
    for key in ("S2_scale_absdev", "S2_res", "S2_scale_median", "S2_res_robust", "S2_theta_sigma_mrad", "S2_gamma_tag_eff"):
        out[f"{key}_mean"] = mean_over(out, key)
    out["S2_scale_absdev_max"] = max([v for k, v in out.items() if k.startswith("S2_scale_absdev_") and k[16:].isdigit()], default=float("nan"))
    return out


def s3_neutron(files, mcfg):
    out = {}
    tilt = float(mcfg.crossing_angle_rad)
    c = mcfg.collections
    for p, fs in by_momentum(files).items():
        cl = read_collection(fs, c.zdc_clusters, ["energy"])
        esum = ak.to_numpy(ak.sum(cl["energy"], axis=1)) / p      # raw: no corrPower, every ZDC HCal cluster
        out[f"S3_rawsum_mean_{p}"] = float(np.mean(esum)) if len(esum) else float("nan")
        out[f"S3_rawsum_sigma_{p}"] = float(np.std(esum)) if len(esum) else float("nan")
        out[f"S3_clusters_per_event_{p}"] = float(ak.mean(ak.num(cl["energy"], axis=1)))
        neutrals = read_collection(fs, c.zdc_neutrals, ["PDG", "energy"])
        gamma_e = ak.to_numpy(ak.sum(neutrals["energy"][neutrals["PDG"] == 22], axis=1))
        total_e = ak.to_numpy(ak.sum(neutrals["energy"], axis=1))
        with np.errstate(invalid="ignore", divide="ignore"):
            frac = np.where(total_e > 0, gamma_e / total_e, 0.0)
        out[f"S3_gamma_tagged_efrac_{p}"] = float(np.mean(frac))
        t = truth_table(fs)
        if t is None:
            continue
        t = t[t["role"] == "p"]
        neutral_cells(t, p, "S3corr", tilt, out)
        out[f"S3_clusters_per_neutron_{p}"] = float(np.mean(t["n_clusters"])) if len(t) else float("nan")
        out[f"S3_mistag_rate_{p}"] = float(np.mean(t["neutral_pdg"] == 22)) if len(t) else float("nan")
    for key in ("S3_rawsum_mean", "S3_rawsum_sigma", "S3_clusters_per_neutron", "S3_gamma_tagged_efrac", "S3_mistag_rate", "S3corr_scale", "S3corr_res", "S3corr_scale_median", "S3corr_res_robust"):
        out[f"{key}_mean"] = mean_over(out, key)
    return out


# ---------------------------------------------------------------- S4

def s4_lambda(files, mcfg, summary):
    out = {}
    if summary:
        for p, per in summary["per_momentum"].items():
            n = per.get("events", 0)
            for key in ("S4a_tm_eff", "S4a_any_eff", "S4a_Rt_eff"):
                if key in per:
                    out[f"{key}_{p}"] = per[key]
                    out[f"{key}_err_{p}"] = binomial_error(per[key] * n, n)
    for p, fs in by_momentum(files).items():
        neutrals = read_collection(fs, mcfg.collections.zdc_neutrals, ["PDG"])
        out[f"S4c_gammas_per_event_{p}"] = float(ak.mean(ak.sum(neutrals["PDG"] == 22, axis=1)))
        lt = truth_table(fs, ".lambda.npz")
        if lt is None:
            continue
        m = lt[lt["matched"]]
        fit = fit_peak(m["mass"], mcfg.windows.lambda_mass_gev, float(mcfg.windows.lambda_mass_half_window_gev))
        if fit:
            out[f"S4b_mass_mu_{p}"], out[f"S4b_mass_sigma_{p}"] = fit[0], fit[1]
        elif len(m) >= 10:
            out[f"S4b_mass_sigma_{p}"] = robust_sigma(m["mass"])
        out[f"S4b_decayz_sigma_mm_{p}"] = robust_sigma(m["vz"] - m["true_decay_z"]) if len(m) else float("nan")
        out[f"S4b_n_matched_{p}"] = int(len(m))
    for key in ("S4a_tm_eff", "S4a_any_eff", "S4a_Rt_eff", "S4b_mass_sigma", "S4c_gammas_per_event"):
        out[f"{key}_mean"] = mean_over(out, key)
    return out


# ---------------------------------------------------------------- G1 to G3

def column_fraction(files, mcfg, max_events=None):
    """Fraction of clusters whose hits sit on exactly one distinct subcell (x, y): a column along z."""
    c, r = mcfg.collections, mcfg.relations
    single, total = 0, 0
    for f in files:
        import uproot
        ids = collection_ids(f)
        tree = uproot.open(f)["events"]
        a = tree.arrays([f"{c.zdc_clusters}.hits_begin", f"{c.zdc_clusters}.hits_end", r.cluster_hits_index,
                         r.cluster_hits_index.replace(".index", ".collectionID"),
                         f"{c.zdc_subcell_hits}.position.x", f"{c.zdc_subcell_hits}.position.y",
                         f"{c.zdc_subcell_hits}.position.z"], entry_stop=max_events)
        # proton frame (the ZDC axis): in global x a subcell column drifts ~0.6 mm per layer at −25 mrad
        ca, sa = np.cos(mcfg.crossing_angle_rad), np.sin(mcfg.crossing_angle_rad)
        sub_id = ids.get(c.zdc_subcell_hits)
        for ev in range(len(a)):
            idx = ak.to_numpy(a[r.cluster_hits_index][ev])
            cid = ak.to_numpy(a[r.cluster_hits_index.replace(".index", ".collectionID")][ev])
            hx = ak.to_numpy(a[f"{c.zdc_subcell_hits}.position.x"][ev]) * ca - ak.to_numpy(a[f"{c.zdc_subcell_hits}.position.z"][ev]) * sa
            hy = ak.to_numpy(a[f"{c.zdc_subcell_hits}.position.y"][ev])
            for b, e in zip(ak.to_numpy(a[f"{c.zdc_clusters}.hits_begin"][ev]), ak.to_numpy(a[f"{c.zdc_clusters}.hits_end"][ev])):
                sel = idx[b:e][cid[b:e] == sub_id]
                if not len(sel):
                    continue
                xy = np.unique(np.round(np.stack([hx[sel], hy[sel]], axis=1), 0), axis=0)
                single += int(len(xy) == 1)
                total += 1
    return (single / total if total else float("nan")), total


def guards_dis(files, mcfg):
    c = mcfg.collections.zdc_clusters
    cl = read_collection(files, c, ["energy", "nhits", "intrinsicPhi"])
    e = ak.to_numpy(ak.flatten(cl["energy"]))
    phi = np.degrees(ak.to_numpy(ak.flatten(cl["intrinsicPhi"])))
    nh = ak.to_numpy(ak.flatten(cl["nhits"]))
    nev = len(cl["energy"])
    edge = mcfg.windows.phi_edge_deg
    col_frac, n_col = column_fraction(files, mcfg)
    out = {
        "G1_phi_at_180_frac": float(np.mean(np.abs(np.abs(phi) - 180) < edge)) if len(phi) else float("nan"),
        "G1_column_frac": col_frac,
        "G2_highE_frac": float(np.mean(e > mcfg.windows.high_energy_cluster_gev)) if len(e) else float("nan"),
        "G3_lowE_per_event": float(np.sum(e < mcfg.windows.low_energy_cluster_gev) / max(nev, 1)),
        "G3_nhits_median": float(np.median(nh)) if len(nh) else float("nan"),
        "G3_clusters_per_event": float(len(e) / max(nev, 1)),
        "G_events": nev,
        "G_clusters": int(len(e)),
    }
    out["_hist_phi"] = np.histogram(phi, bins=36, range=(-180, 180))[0].tolist()
    out["_hist_logE"] = np.histogram(np.log10(np.clip(e, 1e-3, None)), bins=40, range=(-3, 3))[0].tolist()
    return out


def spectrum_chi2(hist, ref_hist):
    """χ²/ndf of two log-energy histograms after normalising to equal area (G2 against R0)."""
    a, b = np.asarray(hist, float), np.asarray(ref_hist, float)
    if a.sum() == 0 or b.sum() == 0:
        return float("nan")
    a_n, b_n = a / a.sum(), b / b.sum()
    var = a_n / a.sum() + b_n / b.sum()
    ok = var > 0
    return float(np.sum((a_n[ok] - b_n[ok]) ** 2 / var[ok]) / max(ok.sum() - 1, 1))


def timing(profile, experiment):
    t = Path(profile.reco_root) / experiment / "timing.csv"
    if not t.exists():
        return {}
    rows = list(csv.DictReader(open(t)))
    out = {}
    for ds in sorted({r["dataset"] for r in rows}):
        vals = [float(r["s_per_1000"]) for r in rows if r["dataset"] == ds]
        out[f"T_s_per_1000_{ds}"] = float(np.median(vals))
    return out


# ---------------------------------------------------------------- the paired test

def mcnemar_flags(fa, fb):
    """McNemar on paired booleans keyed by event (or particle): Δ = (b − c)/n, its paired error, z."""
    common = sorted(set(fa) & set(fb))
    gained = sum(1 for k in common if fa[k] and not fb[k])
    lost = sum(1 for k in common if fb[k] and not fa[k])
    n = len(common)
    if n == 0:
        return None
    delta = (gained - lost) / n
    err = np.sqrt(max(gained + lost - (gained - lost) ** 2 / n, 0)) / n
    z = (gained - lost) / np.sqrt(gained + lost) if gained + lost else 0.0
    return {"gained": gained, "lost": lost, "n": n, "delta": delta, "err": float(err), "z": float(z)}


def paired_s0(experiment, reference, dataset):
    """Per momentum, per role (g, n, all): the McNemar test of the separation flags."""
    a, b = truth_summary(experiment, dataset), truth_summary(reference, dataset)
    if not (a and b):
        return {}
    out = {}
    for p in a["event_flags"]:
        if p not in b["event_flags"]:
            continue
        fa, fb = a["event_flags"][p], b["event_flags"][p]
        res = {"all": mcnemar_flags(dict(zip(fa["events"], fa["all_separated"])), dict(zip(fb["events"], fb["all_separated"])))}
        pa = {(e, r): s for e, r, s in fa.get("particles", [])}
        pb = {(e, r): s for e, r, s in fb.get("particles", [])}
        res["g"] = mcnemar_flags({k: v for k, v in pa.items() if k[1] in ("g1", "g2")}, {k: v for k, v in pb.items() if k[1] in ("g1", "g2")})
        res["n"] = mcnemar_flags({k: v for k, v in pa.items() if k[1] == "n"}, {k: v for k, v in pb.items() if k[1] == "n"})
        if "lambda_flags" in a and "lambda_flags" in b and p in a["lambda_flags"] and p in b["lambda_flags"]:
            la, lb = a["lambda_flags"][p], b["lambda_flags"][p]
            res["S4a_tm"] = mcnemar_flags(dict(zip(la["events"], la["matched"])), dict(zip(lb["events"], lb["matched"])))
        out[p] = {k: v for k, v in res.items() if v}
    return out


def bootstrap_delta(values_a, values_b, stat, resamples, seed=12345):
    """Event bootstrap of stat(A) − stat(B) on the events both hold; the same resamples for A and B."""
    common = sorted(set(values_a) & set(values_b))
    if len(common) < 25:
        return None
    va = np.array([values_a[k] for k in common], float)
    vb = np.array([values_b[k] for k in common], float)
    rng = np.random.default_rng(seed)
    deltas = []
    for _ in range(resamples):
        i = rng.integers(0, len(common), len(common))
        sa, sb = stat(va[i]), stat(vb[i])
        if np.isfinite(sa) and np.isfinite(sb):
            deltas.append(sa - sb)
    if len(deltas) < resamples // 2:
        return None
    return {"delta": float(stat(va) - stat(vb)), "err": float(np.std(deltas)), "n": len(common)}


def per_event_values(profile, experiment, dataset, kind, mcfg):
    """{momentum: {event key: value}} for the bootstrap: S2 corrected E/p, S3 raw Σ E/p, S4b truth-matched Λ mass."""
    out = {}
    for p, fs in by_momentum(files_of(profile, experiment, dataset)).items():
        vals = {}
        if kind == "S3_rawsum":
            for f in fs:
                e = ak.to_numpy(ak.sum(read_collection([f], mcfg.collections.zdc_clusters, ["energy"])["energy"], axis=1)) / p
                vals.update({(f.name.split(".")[0], i): float(v) for i, v in enumerate(e)})
        else:
            for f in fs:
                suffix = ".lambda.npz" if kind == "S4b_mass" else ".npz"
                t = truth_table([f], suffix)
                if t is None:
                    continue
                if kind == "S2_scale":
                    t = t[(t["role"] == "p") & (t["neutral_E"] > 0)]
                    vals.update({(f.name.split(".")[0], int(r["event"])): float(r["neutral_E"]) / p for r in t})
                else:
                    t = t[t["matched"]]
                    vals.update({(f.name.split(".")[0], int(r["event"])): float(r["mass"]) for r in t})
        out[p] = vals
    return out


def fitted_mu(values):
    f = energy_fit(values)
    return f[0] if f else float("nan")


def fitted_sigma(values):
    f = energy_fit(values, 0.05)
    return f[1] if f else float("nan")


def print_compare(profile, experiment, reference, mcfg, public, ref):
    sigma = float(mcfg.significance_sigma)
    tag = lambda z: "SIGNIFICANT" if abs(z) >= sigma else "not significant"
    print(f"\npaired test against {reference} (identical events; significant at {sigma:g}σ)")
    for ds, label in (("D4_lambda", "S0"), ("D1_pi0", "S1a_truth")):
        for p, res in paired_s0(experiment, reference, ds).items():
            for role, t in res.items():
                name = role if role == "S4a_tm" else f"{label}_{role}"
                print(f"  {ds:10s} {p:>4s} GeV {name:12s} Δ {t['delta']:+.4f} ± {t['err']:.4f}  (gained {t['gained']}, lost {t['lost']} of {t['n']})  z {t['z']:+5.2f}  {tag(t['z'])}")
    resamples = int(mcfg.fits.bootstrap_resamples)
    for ds, kind, stat in (("D2_photon", "S2_scale", np.median), ("D3_neutron", "S3_rawsum", np.mean), ("D4_lambda", "S4b_mass", fitted_sigma)):
        va, vb = per_event_values(profile, experiment, ds, kind, mcfg), per_event_values(profile, reference, ds, kind, mcfg)
        for p in sorted(set(va) & set(vb)):
            res = bootstrap_delta(va[p], vb[p], stat, resamples)
            if res:
                z = res["delta"] / res["err"] if res["err"] > 0 else 0.0
                print(f"  {ds:10s} {p:>4d} GeV {kind:12s} Δ {res['delta']:+.5f} ± {res['err']:.5f}  (bootstrap, {res['n']} events)  z {z:+5.2f}  {tag(z)}")
    print("other cells (Δ against the reference; guards are judged against the limits in configs/metrics.yaml):")
    for k in sorted(public):
        if k in ref and k.endswith("_mean") and isinstance(public[k], (int, float)) and isinstance(ref[k], (int, float)):
            print(f"  {k:40s} {ref[k]:12.5g} -> {public[k]:12.5g}  Δ {public[k] - ref[k]:+10.4g}")


# ---------------------------------------------------------------- main

def main():
    sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment")
    ap.add_argument("--datasets", nargs="*", help="subset (the row is then marked partial)")
    ap.add_argument("--compare", metavar="REF", help="paired test against REF's reconstruction")
    ap.add_argument("--no-row", action="store_true", help="compute and print, do not touch scoreboard.csv")
    args = ap.parse_args()
    profile, mcfg, dcfg = load_profile(), metrics_config(), datasets_config()
    PERF.mkdir(parents=True, exist_ok=True)

    row = {"experiment": args.experiment, "partial": bool(args.datasets)}
    wanted = set(args.datasets) if args.datasets else None
    take = lambda ds: wanted is None or ds in wanted
    missing = []
    gun_cells = [("D1_pi0", lambda fs: {**s1_pi0(fs, mcfg), **s0_cells(truth_summary(args.experiment, "D1_pi0") or {"per_momentum": {}, "event_flags": {}}, "S1a_truth")}),
                 ("D2_photon", lambda fs: s2_photon(fs, mcfg)),
                 ("D3_neutron", lambda fs: s3_neutron(fs, mcfg)),
                 ("D4_lambda", lambda fs: {**s0_cells(truth_summary(args.experiment, "D4_lambda") or {"per_momentum": {}, "event_flags": {}}, "S0"),
                                           **s4_lambda(fs, mcfg, truth_summary(args.experiment, "D4_lambda"))})]
    for ds, fn in gun_cells:
        if not take(ds):
            continue
        fs = files_of(profile, args.experiment, ds)
        if not fs:
            missing.append(ds)
            continue
        if not truth_summary(args.experiment, ds):
            print(f"NOTE: no truth-match output for {ds} (run scripts/410_truth_match.py {args.experiment} first)")
        row.update(fn(fs))
    ref_metrics = PERF / "metrics-R0_stock.json"
    ref_row = json.loads(ref_metrics.read_text()) if ref_metrics.exists() else {}
    for ds in dcfg.dis.samples:
        if not take(ds):
            continue
        fs = files_of(profile, args.experiment, ds)
        if not fs:
            missing.append(ds)
            continue
        g = guards_dis(fs, mcfg)
        if f"_hist_logE_{ds}" in ref_row:
            g["G2_logE_chi2_vs_R0"] = spectrum_chi2(g["_hist_logE"], ref_row[f"_hist_logE_{ds}"])
        row.update({f"{k}_{ds}": v for k, v in g.items()})
    row.update(timing(profile, args.experiment))
    if missing:
        row["partial"] = True
        row["missing_datasets"] = ",".join(missing)
        print(f"NOTE: no reconstruction found for {missing}; the row is partial")

    out_json = PERF / f"metrics-{args.experiment}.json"
    out_json.write_text(json.dumps(row, indent=1, sort_keys=True))
    public = {k: v for k, v in row.items() if not k.startswith("_")}
    if not args.no_row:
        csv_path = PERF / "scoreboard.csv"
        existing = [r for r in (list(csv.DictReader(open(csv_path))) if csv_path.exists() else []) if r["experiment"] != args.experiment]
        columns = ["experiment", "partial"] + sorted((set(public) | {c for r in existing for c in r}) - {"experiment", "partial"})
        with open(csv_path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=columns)
            w.writeheader()
            for r in existing:
                w.writerow(r)
            w.writerow(public)
        print(f"row written to {csv_path}; metrics in {out_json}")
    for k in sorted(public):
        if k.endswith("_mean") or k.startswith("G1_") or k.startswith("G3_lowE") or k.startswith("G2_highE"):
            print(f"  {k:45s} {public[k]}")
    if args.compare:
        ref = json.loads((PERF / f"metrics-{args.compare}.json").read_text())
        print_compare(profile, args.experiment, args.compare, mcfg, public, ref)


if __name__ == "__main__":
    main()
