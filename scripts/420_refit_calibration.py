#!/usr/bin/env python3
"""Refit the ZDC γ and neutron energy calibration a·E^b on gun truth, for one clustering (Phase 1 step 3).

FarForwardNeutralsReconstruction corrects the ZDC energies with
E = a · E_raw^b (corrPower): for a photon E_raw is the energy of its one
cluster, for the neutron (NeutronMode::SumAll) the sum of the event's
non-photon clusters. The refit uses truth, never S4a:

  γ (D2): E_raw = energy of the photon's best-matched cluster (410 table, column E);
  n (D3): E_raw = the neutron's clustered energy, Σ over clusters of weight × E
          (410 column assoc_E), which is what SumAll adds when no shard is
          tagged a photon.

Per momentum point the peak of E_raw (Gaussian fit around the median, the
benchmarks' recipe; median if the fit fails) is taken against the true energy
(from the true momentum, plus the neutron mass for D3); then
log E_true = log a + b log E_peak is fitted with the peak errors. Printed: a
and b with their errors, and the residual scale per momentum — the peak of
a·E_raw^b / E_true — both for the refit and for the coefficients given with
--compare (default: the stock and the PR coefficients).

The coefficients belong to one clustering: the PR's were fitted on R1's
single-column clusters and are garbage on any other clustering.

Usage:
  uv run scripts/420_refit_calibration.py R0_stock
  uv run scripts/420_refit_calibration.py R1_pr3064 --out space/perf/calib-R1_pr3064.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, metrics_config, repo_path  # noqa: E402
from zdc.edm import fit_peak  # noqa: E402

M_N = 0.93956542
COEFFS = {"stock": {"g": (1.1, 0.98), "n": (2.4, 0.89)}, "PR3064": {"g": (2.7, 1.27), "n": (16.65, 0.66)}}
SPEC = {"g": ("D2_photon", "photon", 0.0), "n": ("D3_neutron", "neutron", M_N)}


def peak(values):
    values = np.asarray(values, float)
    values = values[np.isfinite(values) & (values > 0)]
    if len(values) < 25:
        return None
    med = float(np.median(values))
    f = fit_peak(values, med, 0.3 * med)
    if f and f[2] > 0 and abs(f[0] - med) < 0.3 * med:
        return f[0], f[2], len(values)
    # fallback: the median and its error (1.2533 σ/√n for a Gaussian)
    return med, 1.2533 * np.std(values) / np.sqrt(len(values)), len(values)


def points(profile, experiment, kind):
    ds, _, mass = SPEC[kind]
    d = Path(profile.reco_root) / experiment / ds / "truth"
    out = []
    for f in sorted(d.glob("*.npz")):
        if f.name.endswith(".lambda.npz"):
            continue
        t = np.load(f)["table"]
        t = t[(t["role"] == "p") & (t["cluster"] >= 0)]
        if not len(t):
            continue
        ptrue = np.sqrt(t["true_px"] ** 2 + t["true_py"] ** 2 + t["true_pz"] ** 2).astype(float)
        e_true = np.sqrt(ptrue ** 2 + mass ** 2)
        e_raw = (t["E"] if kind == "g" else t["assoc_E"]).astype(float)
        pk = peak(e_raw)
        if pk is None:
            continue
        out.append({"file": f.stem, "E_true": float(np.median(e_true)), "E_raw_peak": pk[0], "E_raw_peak_err": float(pk[1]),
                    "n": pk[2], "e_raw": e_raw, "e_true": e_true})
    return sorted(out, key=lambda r: r["E_true"])


def fit(pts):
    x = np.log([p["E_raw_peak"] for p in pts])
    y = np.log([p["E_true"] for p in pts])
    sx = np.array([p["E_raw_peak_err"] / p["E_raw_peak"] for p in pts])
    # error in x propagated through the slope (b ≈ 1): fit y = log a + b x with σ_y = b σ_x, iterated once
    b = 1.0
    for _ in range(3):
        sigma = np.maximum(b * sx, 1e-4)
        (la, b), cov = curve_fit(lambda xx, la, bb: la + bb * xx, x, y, p0=[0.0, b], sigma=sigma, absolute_sigma=True)
    err = np.sqrt(np.diag(cov))
    chi2 = float(np.sum(((y - (la + b * x)) / sigma) ** 2))
    return float(np.exp(la)), float(b), float(np.exp(la) * err[0]), float(err[1]), chi2, len(x) - 2


def residuals(pts, a, b, with_err=False):
    res, err = {}, {}
    for p in pts:
        r = a * p["e_raw"] ** b / p["e_true"]
        pk = peak(r)
        res[f"{p['E_true']:.0f}"] = round(pk[0], 4) if pk else None
        err[f"{p['E_true']:.0f}"] = round(float(pk[1]), 4) if pk else None
    return (res, err) if with_err else res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment")
    ap.add_argument("--out", help="JSON output (default space/perf/calib-<experiment>.json)")
    args = ap.parse_args()
    profile = load_profile()
    result = {"experiment": args.experiment}
    for kind in ("g", "n"):
        pts = points(profile, args.experiment, kind)
        name = SPEC[kind][1]
        if len(pts) < 3:
            print(f"{name}: {len(pts)} momentum point(s), need 3 (run 410_truth_match.py on {SPEC[kind][0]})")
            result[name] = {"error": f"{len(pts)} points"}
            continue
        a, b, ea, eb, chi2, ndf = fit(pts)
        print(f"\n{name} ({SPEC[kind][0]}, {args.experiment}): refit a = {a:.4g} ± {ea:.2g}, b = {b:.4f} ± {eb:.2g}"
              f"  (chi2/ndf = {chi2:.1f}/{ndf})")
        print(f"  {'E_true':>7s} {'E_raw peak':>11s} {'raw/true':>9s}   residual scale a·E^b/E_true")
        refit_res, refit_err = residuals(pts, a, b, with_err=True)
        lim = float(metrics_config().limits.S2_scale_abs_dev_max)
        rows = {"refit": refit_res}
        for label, c in COEFFS.items():
            rows[label] = residuals(pts, *c[kind])
        print("  " + " " * 30 + "  ".join(f"{k:>8s}" for k in rows))
        for p in pts:
            k = f"{p['E_true']:.0f}"
            print(f"  {p['E_true']:7.1f} {p['E_raw_peak']:11.3f} {p['E_raw_peak'] / p['E_true']:9.3f}    "
                  + "  ".join(f"{rows[lab][k] if rows[lab][k] is not None else float('nan'):8.3f}" for lab in rows))
        for label, c in COEFFS.items():
            pulls = ((c[kind][0] - a) / ea if ea else float("nan"), (c[kind][1] - b) / eb if eb else float("nan"))
            print(f"  {label} ({c[kind][0]}, {c[kind][1]}): pull from the refit a {pulls[0]:+.1f}σ, b {pulls[1]:+.1f}σ")
        result[name] = {"a": a, "b": b, "a_err": ea, "b_err": eb, "chi2": chi2, "ndf": ndf,
                        "points": [{k: v for k, v in p.items() if k not in ("e_raw", "e_true")} for p in pts],
                        "residual_scale": rows,
                        # statistical error of the refit residual's peak; the S2 guard (D-user-17, Q10 B) is
                        # |residual − 1| − 2·error ≤ S2_scale_abs_dev_max
                        "residual_scale_err_refit": refit_err,
                        "S2_guard_refit": {k: (None if refit_res[k] is None else
                                               bool(abs(refit_res[k] - 1) - 2 * refit_err[k] <= lim)) for k in refit_res},
                        "compared": {lab: {"a": c[kind][0], "b": c[kind][1]} for lab, c in COEFFS.items()}}
    out = Path(args.out) if args.out else repo_path("space", "perf", f"calib-{args.experiment}.json")
    out.write_text(json.dumps(result, indent=1))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
