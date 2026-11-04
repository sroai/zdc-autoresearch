#!/usr/bin/env python3
"""The scoreboard: every fixed metric of zdc-setup.md (section Scoreboard) for one experiment.

Reads the reconstruction outputs under {reco_root}/<experiment>/<dataset>/,
computes S1 (π⁰ gun), S2 (photon gun), S3 (neutron gun), S4 (Λ gun), G1 to G3
(DIS cluster distributions) and T (timing), writes
{space}/perf/metrics-<experiment>.json and appends one row to
{space}/perf/scoreboard.csv. With --compare REF it also prints each metric's
delta against REF's row in units of the noise band ({space}/perf/noise-band.json,
or the default relative band of configs/metrics.yaml until that file exists).

Usage:
  uv run scripts/400_scoreboard.py R0_stock
  uv run scripts/400_scoreboard.py E03_nhits5 --compare R0_stock
  uv run scripts/400_scoreboard.py R0_stock --datasets D1_pi0 D4_lambda   # partial row (marked partial)

Metric definitions follow the benchmark analysis scripts
(submodules/detector_benchmarks/benchmarks/zdc_*/analysis) so the numbers here
and the plots there agree: two-cluster selection, Gaussian fits in a ±10 % window
around the momentum, the proton-frame rotation by the crossing angle.
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
from zdc.edm import binomial_error, fit_peak, read_collection, rotate_to_proton_frame  # noqa: E402

PERF = repo_path("space", "perf")


def files_of(profile, experiment, dataset):
    d = Path(profile.reco_root) / experiment / dataset
    return sorted(d.glob("*.edm4eic.root"))


def by_momentum(files):
    """{momentum_gev: [files]} from names like D1_pi0_100GeV_seed1.edm4eic.root."""
    groups = {}
    for f in files:
        token = [t for t in f.name.split("_") if t.endswith("GeV")]
        if not token:
            continue
        groups.setdefault(int(token[0][:-3]), []).append(f)
    return dict(sorted(groups.items()))


def clusters(files, mcfg):
    c = mcfg.collections.zdc_clusters
    return read_collection(files, c, ["energy", "position.x", "position.y", "position.z", "nhits", "intrinsicPhi"])


def two_cluster_mass_and_energy(cl):
    """γγ mass and summed energy for events with exactly two clusters (massless photons from the IP)."""
    two = ak.num(cl["energy"], axis=1) == 2
    e = cl["energy"][two]
    x, y, z = cl["position.x"][two], cl["position.y"][two], cl["position.z"][two]
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    px, py, pz = ak.sum(e * x / r, axis=1), ak.sum(e * y / r, axis=1), ak.sum(e * z / r, axis=1)
    etot = ak.sum(e, axis=1)
    mass = np.sqrt(np.clip(ak.to_numpy(etot ** 2 - px ** 2 - py ** 2 - pz ** 2), 0, None))
    return float(ak.mean(two)), mass, ak.to_numpy(etot)


def s1_pi0(files, mcfg):
    out = {}
    for p, fs in by_momentum(files).items():
        cl = clusters(fs, mcfg)
        frac2, mass, etot = two_cluster_mass_and_energy(cl)
        n = len(ak.num(cl["energy"], axis=1))
        out[f"S1a_frac2_{p}"] = frac2
        out[f"S1a_frac2_err_{p}"] = binomial_error(frac2 * n, n)
        fit = fit_peak(mass, mcfg.windows.pi0_mass_gev, 0.1)
        if fit:
            mu, sigma, *_ = fit
            out[f"S1b_mass_mu_{p}"], out[f"S1b_mass_sigma_{p}"] = mu, sigma
            out[f"S1b_frac_in3sigma_{p}"] = float(np.mean(np.abs(mass - mu) < 3 * sigma)) if len(mass) else 0.0
        efit = fit_peak(etot, p, p * mcfg.fits.energy_fit_half_width_rel)
        if efit:
            mu, sigma, *_ = efit
            out[f"S1c_scale_{p}"], out[f"S1c_res_{p}"] = mu / p, sigma / mu
    frac = [v for k, v in out.items() if k.startswith("S1a_frac2_") and "err" not in k]
    out["S1a_frac2_mean"] = float(np.mean(frac)) if frac else float("nan")
    return out


def single_particle(files, mcfg, prefix):
    """Energy scale/resolution and θ resolution of the leading cluster; 1-cluster fraction; isGamma rate."""
    out = {}
    tilt = float(mcfg.crossing_angle_rad)
    for p, fs in by_momentum(files).items():
        cl = clusters(fs, mcfg)
        ncl = ak.num(cl["energy"], axis=1)
        out[f"{prefix}_frac1cluster_{p}"] = float(ak.mean(ncl == 1))
        has = ncl > 0
        lead = ak.argmax(cl["energy"][has], axis=1, keepdims=True)
        e = ak.to_numpy(ak.flatten(cl["energy"][has][lead]))
        efit = fit_peak(e, p, p * mcfg.fits.energy_fit_half_width_rel)
        if efit:
            mu, sigma, *_ = efit
            out[f"{prefix}_scale_{p}"], out[f"{prefix}_res_{p}"] = mu / p, sigma / mu
        x = ak.to_numpy(ak.flatten(cl["position.x"][has][lead]))
        y = ak.to_numpy(ak.flatten(cl["position.y"][has][lead]))
        z = ak.to_numpy(ak.flatten(cl["position.z"][has][lead]))
        px, py, pz = rotate_to_proton_frame(x, y, z, tilt)
        theta = np.arctan2(np.hypot(px, py), pz)
        tfit = fit_peak(theta * 1e3, np.median(theta * 1e3), 3.0)   # mrad, within the gun's 0 to 4 mrad
        if tfit:
            out[f"{prefix}_theta_sigma_mrad_{p}"] = tfit[1]
        neutrals = read_collection(fs, mcfg.collections.zdc_neutrals, ["PDG", "energy"])
        pdg = neutrals["PDG"]
        has_n = ak.num(pdg, axis=1) > 0
        lead_n = ak.argmax(neutrals["energy"][has_n], axis=1, keepdims=True)
        lead_pdg = ak.to_numpy(ak.flatten(pdg[has_n][lead_n]))
        out[f"{prefix}_leading_is_gamma_{p}"] = float(np.mean(lead_pdg == 22)) if len(lead_pdg) else float("nan")
        out[f"{prefix}_has_neutral_{p}"] = float(ak.mean(has_n))
    return out


def neutron_raw(files, mcfg):
    """S3 raw guard: Σ E(clusters) / E_true per momentum (no corrPower), clusters per event, γ-tagged energy fraction."""
    out = {}
    for p, fs in by_momentum(files).items():
        cl = clusters(fs, mcfg)
        esum = ak.to_numpy(ak.sum(cl["energy"], axis=1)) / p
        fit = fit_peak(esum, float(np.median(esum)) if len(esum) else 0.0, 0.5)
        out[f"S3_rawsum_mean_{p}"] = float(np.mean(esum)) if len(esum) else float("nan")
        out[f"S3_rawsum_sigma_{p}"] = fit[1] if fit else (float(np.std(esum)) if len(esum) else float("nan"))
        out[f"S3_nclusters_mean_{p}"] = float(ak.mean(ak.num(cl["energy"], axis=1)))
        try:
            neutrals = read_collection(fs, mcfg.collections.zdc_neutrals, ["PDG", "energy"])
            gamma_e = ak.sum(neutrals["energy"][neutrals["PDG"] == 22], axis=1)
            total_e = ak.sum(neutrals["energy"], axis=1)
            frac = ak.to_numpy(gamma_e) / np.maximum(ak.to_numpy(total_e), 1e-9)
            out[f"S3_gamma_tagged_efrac_{p}"] = float(np.mean(frac))
        except Exception:
            out[f"S3_gamma_tagged_efrac_{p}"] = float("nan")
    return out


def truth_cells(experiment, dataset, prefix):
    """S0 (and S1a truth) cells from scripts/410_truth_match.py output, when it exists."""
    path = PERF / f"truth-{experiment}-{dataset}.json"
    if not path.exists():
        return {}
    t = json.loads(path.read_text())
    out = {}
    alls = []
    for p, per in t["per_momentum"].items():
        for k, v in per.items():
            if k.startswith("S0_"):
                out[f"{prefix}_{k[3:]}_{p}"] = v
        alls.append(per.get("S0_all_sep", float("nan")))
    out[f"{prefix}_all_sep_mean"] = float(np.nanmean(alls)) if alls else float("nan")
    return out


def mcnemar(experiment, reference, dataset):
    """Paired test of the all-separated flag per momentum: discordant counts and the McNemar z (zdc-setup.md, Noise and significance)."""
    a = PERF / f"truth-{experiment}-{dataset}.json"
    b = PERF / f"truth-{reference}-{dataset}.json"
    if not (a.exists() and b.exists()):
        return {}
    fa, fb = json.loads(a.read_text())["event_flags"], json.loads(b.read_text())["event_flags"]
    out = {}
    for p in fa:
        if p not in fb:
            continue
        ea, eb = dict(zip(fa[p]["events"], fa[p]["all_separated"])), dict(zip(fb[p]["events"], fb[p]["all_separated"]))
        common = set(ea) & set(eb)
        gained = sum(1 for e in common if ea[e] and not eb[e])
        lost = sum(1 for e in common if eb[e] and not ea[e])
        z = (gained - lost) / np.sqrt(gained + lost) if gained + lost > 0 else 0.0
        out[p] = {"gained": gained, "lost": lost, "z": float(z), "events": len(common)}
    return out


def s4_lambda(files, mcfg, references):
    out = {}
    window = mcfg.windows.lambda_mass_gev
    half = float(mcfg.windows.lambda_mass_half_window_gev)   # fixed for the program; R0 may have no peak to fit
    effs = []
    for p, fs in by_momentum(files).items():
        lam = read_collection(fs, mcfg.collections.lambdas, ["mass", "momentum.x", "momentum.y", "momentum.z", "referencePoint.z"])
        n = len(lam["mass"])
        masses = ak.to_numpy(ak.flatten(lam["mass"]))
        in_window = ak.sum(np.abs(lam["mass"] - window) < half, axis=1) > 0
        eff = float(ak.mean(in_window))
        out[f"S4a_eff_{p}"], out[f"S4a_eff_err_{p}"] = eff, binomial_error(eff * n, n)
        effs.append(eff)
        fit = fit_peak(masses, window, 0.1)
        if fit:
            mu, sigma, *_ = fit
            out[f"S4b_mass_mu_{p}"], out[f"S4b_mass_sigma_{p}"] = mu, sigma
        out[f"S4_ncand_per_event_{p}"] = float(ak.mean(ak.num(lam["mass"], axis=1)))
        try:   # S4c: γ-tagged neutrals per event (fragment combinatorics guard)
            neutrals = read_collection(fs, mcfg.collections.zdc_neutrals, ["PDG"])
            out[f"S4c_gammas_per_event_{p}"] = float(ak.mean(ak.sum(neutrals["PDG"] == 22, axis=1)))
        except Exception:
            out[f"S4c_gammas_per_event_{p}"] = float("nan")
    out["S4a_eff_mean"] = float(np.mean(effs)) if effs else float("nan")
    return out


def guards_dis(files, mcfg):
    cl = clusters(files, mcfg)
    e = ak.to_numpy(ak.flatten(cl["energy"]))
    phi = np.degrees(ak.to_numpy(ak.flatten(cl["intrinsicPhi"])))
    nh = ak.to_numpy(ak.flatten(cl["nhits"]))
    nev = len(cl["energy"])
    edge = mcfg.windows.phi_edge_deg
    out = {
        "G1_frac_phi_at_180": float(np.mean(np.abs(np.abs(phi) - 180) < edge)) if len(phi) else float("nan"),
        "G2_frac_E_above_hi": float(np.mean(e > mcfg.windows.high_energy_cluster_gev)) if len(e) else float("nan"),
        "G3_lowE_clusters_per_event": float(np.sum(e < mcfg.windows.low_energy_cluster_gev) / max(nev, 1)),
        "G3_nhits_median": float(np.median(nh)) if len(nh) else float("nan"),
        "G_clusters_per_event": float(len(e) / max(nev, 1)),
        "G_events": nev,
    }
    hist_phi, _ = np.histogram(phi, bins=36, range=(-180, 180))
    hist_e, _ = np.histogram(np.log10(np.clip(e, 1e-3, None)), bins=40, range=(-3, 3))
    out["_hist_phi"], out["_hist_logE"] = hist_phi.tolist(), hist_e.tolist()
    return out


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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment")
    ap.add_argument("--datasets", nargs="*", help="subset (the row is then marked partial)")
    ap.add_argument("--compare", metavar="REF", help="print deltas against REF's metrics file in band units")
    args = ap.parse_args()
    profile = load_profile()
    mcfg = metrics_config()
    dcfg = datasets_config()
    PERF.mkdir(parents=True, exist_ok=True)
    references = json.loads((PERF / "references.json").read_text()) if (PERF / "references.json").exists() else {}

    row = {"experiment": args.experiment, "partial": bool(args.datasets)}
    wanted = set(args.datasets) if args.datasets else None
    def take(ds):
        return wanted is None or ds in wanted
    missing = []
    for ds, fn in [("D1_pi0", lambda f: s1_pi0(f, mcfg)), ("D2_photon", lambda f: single_particle(f, mcfg, "S2")),
                   ("D3_neutron", lambda f: {**single_particle(f, mcfg, "S3"), **neutron_raw(f, mcfg)}),
                   ("D4_lambda", lambda f: s4_lambda(f, mcfg, references))]:
        if not take(ds):
            continue
        fs = files_of(profile, args.experiment, ds)
        if not fs:
            missing.append(ds)
            continue
        row.update(fn(fs))
    # truth-matched cells (the selector S0 on D4, S1a-truth on D1) from 410_truth_match.py
    row.update(truth_cells(args.experiment, "D4_lambda", "S0"))
    row.update(truth_cells(args.experiment, "D1_pi0", "S1a_truth"))
    if "S0_all_sep_mean" not in row:
        print("NOTE: no truth-match output for D4_lambda (run scripts/410_truth_match.py first); S0 cells missing")
    for ds in dcfg.dis.samples:
        if not take(ds):
            continue
        fs = files_of(profile, args.experiment, ds)
        if not fs:
            missing.append(ds)
            continue
        row.update({f"{k}_{ds}": v for k, v in guards_dis(fs, mcfg).items()})
    row.update(timing(profile, args.experiment))
    if missing:
        row["partial"] = True
        row["missing_datasets"] = ",".join(missing)
        print(f"NOTE: no reconstruction found for {missing}; the row is partial")

    out_json = PERF / f"metrics-{args.experiment}.json"
    out_json.write_text(json.dumps(row, indent=1, sort_keys=True))
    public = {k: v for k, v in row.items() if not k.startswith("_")}
    csv_path = PERF / "scoreboard.csv"
    existing = list(csv.DictReader(open(csv_path))) if csv_path.exists() else []
    columns = sorted(set(public) | {c for r in existing for c in r})
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns)
        w.writeheader()
        for r in existing:
            w.writerow(r)
        w.writerow(public)
    print(f"row appended to {csv_path}; metrics in {out_json}")
    for k in ["S0_all_sep_mean", "S1a_frac2_mean", "S4a_eff_mean"] + [k for k in public if k.startswith("G1_") or k.startswith("G2_") or k.startswith("G3_lowE")]:
        if k in public:
            print(f"  {k:40s} {public[k]}")

    if args.compare:
        ref = json.loads((PERF / f"metrics-{args.compare}.json").read_text())
        sigma = float(mcfg.significance_sigma)
        print(f"paired test of the selector against {args.compare} (McNemar on the all-separated flag, per momentum):")
        for p, t in mcnemar(args.experiment, args.compare, "D4_lambda").items():
            verdict = "SIGNIFICANT" if abs(t["z"]) >= sigma else "not significant"
            print(f"  {p:>4s} GeV: gained {t['gained']:4d} lost {t['lost']:4d} of {t['events']} events, z = {t['z']:+5.2f}  {verdict}")
        print(f"other cells (delta, and delta over the quoted error where one exists; guards are judged against configs/metrics.yaml limits):")
        for k in sorted(public):
            if k in ref and isinstance(public[k], (int, float)) and isinstance(ref[k], (int, float)) and not k.endswith("_err"):
                d = public[k] - ref[k]
                err = public.get(k.replace("_eff_", "_eff_err_").replace("_frac2_", "_frac2_err_"), None) if "_eff_" in k or "_frac2_" in k else None
                extra = f"  {d / err:+6.2f} σ" if isinstance(err, (int, float)) and err > 0 else ""
                print(f"  {k:40s} {ref[k]:12.5g} -> {public[k]:12.5g}  Δ {d:+10.4g}{extra}")


if __name__ == "__main__":
    main()
