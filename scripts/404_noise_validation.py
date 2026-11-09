#!/usr/bin/env python3
"""Is the quoted error honest? Three independent seeds against the analytic error (Phase 0 item 13).

For one experiment (R0), at one momentum of D1 (100 GeV) and of D4 (175 GeV),
the metrics are computed on each seed alone — seed 1 from the main dataset,
seeds 2 and 3 from the noise datasets D1n/D4n — each with the error the
scoreboard would quote for it (binomial for efficiencies, an event bootstrap
for fitted means and widths). The seed spread is then set against the quoted
error: chi2 = Σ (x_i − x̄)² / σ_i² over the three seeds, ndf 2, and the ratio
of the seed standard deviation to the mean quoted error. A metric whose ratio
sits well above 1 (p(chi2) < 0.01) has a dishonest error; the paired test of
400_scoreboard.py --compare is only as good as these errors.

Per-file inputs: the 410 truth tables {reco}/<exp>/<dataset>/truth/<file>.npz
(and .lambda.npz), which keep one file per seed (the 410 per-momentum summary
merges seeds that share a momentum).

Writes {space}/perf/noise-validation.json, one entry per experiment.

Usage: uv run scripts/404_noise_validation.py [R0_stock]
"""
import json
import sys
from pathlib import Path

import awkward as ak
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, metrics_config, repo_path  # noqa: E402
from zdc.edm import fit_peak, n_events, read_collection  # noqa: E402

RESAMPLES = 200
POINTS = [  # (label, momentum, [(dataset, seed)])
    ("D1 100 GeV", 100, [("D1_pi0", 1), ("D1n_pi0_noise", 2), ("D1n_pi0_noise", 3)]),
    ("D4 175 GeV", 175, [("D4_lambda", 1), ("D4n_lambda_noise", 2), ("D4n_lambda_noise", 3)]),
]


def binom(k, n):
    p = k / n if n else float("nan")
    return p, (np.sqrt(p * (1 - p) / n) if n else float("nan"))


def boot(values, stat, rng):
    """stat on the values and its event-bootstrap error."""
    values = np.asarray(values)
    v = stat(values)
    if v is None or not np.isfinite(v):
        return float("nan"), float("nan")
    reps = [stat(values[rng.integers(0, len(values), len(values))]) for _ in range(RESAMPLES)]
    reps = np.array([r for r in reps if r is not None and np.isfinite(r)])
    return float(v), float(np.std(reps, ddof=1)) if len(reps) > 10 else float("nan")


def fit_mu(center, half):
    def f(x):
        r = fit_peak(np.asarray(x, float), center, half)
        return r[0] if r else None
    return f


def fit_sigma(center, half):
    def f(x):
        r = fit_peak(np.asarray(x, float), center, half)
        return r[1] if r else None
    return f


def pi0_mass(t):
    """S1b: the invariant mass of the two best-matched clusters (distinct) of each event, photons from the origin."""
    g1, g2 = t[t["role"] == "g1"], t[t["role"] == "g2"]
    common = np.intersect1d(g1["event"], g2["event"])
    a, b = g1[np.isin(g1["event"], common)], g2[np.isin(g2["event"], common)]
    keep = (a["cluster"] != b["cluster"]) & (a["cluster"] >= 0) & (b["cluster"] >= 0)
    a, b = a[keep], b[keep]

    def mom(r):
        rr = np.sqrt(r["x"] ** 2 + r["y"] ** 2 + r["z"] ** 2)
        return r["E"] * r["x"] / rr, r["E"] * r["y"] / rr, r["E"] * r["z"] / rr
    ax_, ay_, az_ = mom(a)
    bx_, by_, bz_ = mom(b)
    m2 = (a["E"] + b["E"]) ** 2 - (ax_ + bx_) ** 2 - (ay_ + by_) ** 2 - (az_ + bz_) ** 2
    return np.sqrt(np.clip(m2, 0, None))


def metrics_of(reco_file, mcfg, p, rng):
    t = np.load(reco_file.parent / "truth" / f"{reco_file.stem}.npz")["table"]
    out = {}
    g = t[np.isin(t["role"], ["g1", "g2"])]
    out["S0_g"] = binom(int(g["separated"].sum()), len(g))
    n = t[t["role"] == "n"]
    if len(n):
        out["S0_n"] = binom(int(n["separated"].sum()), len(n))
    ev = np.unique(t["event"])
    all_sep = np.array([t[t["event"] == e]["separated"].all() for e in ev])
    out["S0_all"] = binom(int(all_sep.sum()), len(all_sep))
    out["S0_g_purity_mean"] = boot(g["purity"], np.mean, rng)
    nev = int(n_events(reco_file))
    cl = read_collection([reco_file], mcfg.collections.zdc_clusters, ["energy"])
    ncl = ak.to_numpy(ak.num(cl["energy"], axis=1))
    out["S1a_raw"] = binom(int(np.sum(ncl == 2)), len(ncl))
    out["clusters_per_event"] = boot(ncl.astype(float), np.mean, rng)
    m = pi0_mass(t)
    if len(m) >= 25:
        out["S1b_mass_mu"] = boot(m, fit_mu(mcfg.windows.pi0_mass_gev, 0.1), rng)
        out["S1b_mass_sigma"] = boot(m, fit_sigma(mcfg.windows.pi0_mass_gev, 0.1), rng)
    if not len(n):  # D1: S1c, the benchmark's summed energy of two-cluster events
        etot = ak.to_numpy(ak.sum(cl["energy"][ncl == 2], axis=1))
        half = p * mcfg.fits.energy_fit_half_width_rel
        out["S1c_scale"] = tuple(x / p for x in boot(etot, fit_mu(p, half), rng))
        out["S1c_sigma_gev"] = boot(etot, fit_sigma(p, half), rng)
    lam = reco_file.parent / "truth" / f"{reco_file.stem}.lambda.npz"
    if lam.exists():
        lt = np.load(lam)["table"]
        out["S4a_tm"] = binom(int(lt["matched"].sum()), nev)
        out["S4a_any"] = binom(int(lt["any"].sum()), nev)
        if lt["any"].sum() >= 25:
            out["S4b_mass_sigma"] = boot(lt["mass"][lt["any"]], fit_sigma(mcfg.windows.lambda_mass_gev, 0.03), rng)
    out["events"] = (nev, 0.0)
    return out


def main():
    experiment = sys.argv[1] if len(sys.argv) > 1 else "R0_stock"
    profile, mcfg = load_profile(), metrics_config()
    rng = np.random.default_rng(12345)
    result = {"experiment": experiment, "resamples": RESAMPLES, "points": {}}
    for label, p, seeds in POINTS:
        per_seed = {}
        for ds, s in seeds:
            f = Path(profile.reco_root) / experiment / ds / f"{ds}_{p}GeV_seed{s}.edm4eic.root"
            if not f.exists() or not (f.parent / "truth" / f"{f.stem}.npz").exists():
                print(f"{label}: missing {f} or its truth table (run 410_truth_match.py)")
                continue
            per_seed[s] = metrics_of(f, mcfg, p, rng)
        if len(per_seed) < 3:
            result["points"][label] = {"error": f"only {len(per_seed)} seed(s)"}
            continue
        rows = {}
        print(f"\n{label} ({experiment}): value ± quoted error per seed; spread/err = seed std / mean quoted error")
        for key in per_seed[1]:
            if key == "events" or not all(key in v for v in per_seed.values()):
                continue
            x = np.array([v[key][0] for v in per_seed.values()], float)
            e = np.array([v[key][1] for v in per_seed.values()], float)
            if not (np.all(np.isfinite(x)) and np.all(np.isfinite(e)) and np.all(e > 0)):
                rows[key] = {"values": x.tolist(), "errors": e.tolist(), "note": "not computable on every seed"}
                continue
            chi2 = float(np.sum((x - x.mean()) ** 2 / e ** 2))
            pval = float(stats.chi2.sf(chi2, len(x) - 1))
            ratio = float(np.std(x, ddof=1) / np.mean(e))
            rows[key] = {"values": x.tolist(), "errors": e.tolist(), "seed_std": float(np.std(x, ddof=1)),
                         "mean_error": float(np.mean(e)), "spread_over_error": ratio, "chi2": chi2, "ndf": len(x) - 1,
                         "p_value": pval, "honest": bool(pval >= 0.01)}
            print(f"  {key:20s} " + "  ".join(f"{a:.4g}±{b:.2g}" for a, b in zip(x, e))
                  + f"   spread/err={ratio:.2f}  chi2/2={chi2:.2f}  p={pval:.3f} {'ok' if pval >= 0.01 else 'DISHONEST?'}")
        result["points"][label] = {"seeds": [s for _, s in seeds], "metrics": rows}
    # With 3 seeds the chi2 has 2 degrees of freedom: about 1 metric in 100 fails at p < 0.01 by chance alone.
    out = repo_path("space", "perf", "noise-validation.json")
    allres = json.loads(out.read_text()) if out.exists() else {}
    if "experiment" in allres:  # the first version held one experiment at the top level
        allres = {allres["experiment"]: allres}
    allres[experiment] = result
    out.write_text(json.dumps(allres, indent=1))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
