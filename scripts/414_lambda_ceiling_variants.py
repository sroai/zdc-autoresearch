#!/usr/bin/env python3
"""The Λ → nπ⁰ reconstruction ceiling under two pairings and two input qualities (user request 2026-11-05, Phase 2).

412_lambda_ceiling.py measured the ceiling of LambdaReconstruction's logic with ideal inputs (F4: ≤ 0.068 of D4,
0 at 100–125 GeV), capped by the IP-pointing π⁰ preselection. This script asks what a decay-position-aware pairing
would reach, and what either reaches with the ZDC's measured single-particle resolution instead of ideal inputs:

  pairing  stock  — as 412: π⁰ window and Λ window on IP-pointing momenta, then the IDOLA vertex iteration and the
                    Λ window again (LambdaReconstruction.cc at the pin; windows 10 % relative).
           vertex — IDOLA first (the pin's iteration: the vertex placed along the Λ momentum recomputed from the
                    current vertex), then the π⁰ window and the Λ window on momenta pointing from that vertex.
                    Measured here: for decays far from the IP this iteration runs away transversely (fitted vertex
                    z right, x/y off by metres), so it is reported as found, not as the fix.
           vertex_fixed — the Λ comes from the IP, so its direction is the momentum-weighted centroid of the impact
                    points (Σ p_i x_i / Σ p_i L_i, exact for straight lines at small angles, independent of the
                    vertex); only the decay depth is unknown, and the γγ opening angle grows monotonically with it:
                    bisection (20 steps) for θ_γγ = θ_expected(E1, E2), then the π⁰ and Λ windows. The code change
                    B9d would make (the vertex-aware pairing with a stable vertex).
  inputs   ideal  — true energies; positions on each daughter's true line at shower depth (412's convention).
           real   — energies and positions drawn from the response of single photons (D2) and neutrons (D3)
                    reconstructed with <experiment> (default the current best P1b_R0_thr): calibrated energy
                    E = a·E_cl^b with <experiment>'s refit coefficients (420), the measured ratio E/E_true
                    distribution at the nearest gun energy rescaled to the daughter's energy by σ(E) ∝ 1/√E
                    (tails kept), and the measured transverse position residual (best cluster vs the true line).
                    Detection: a daughter is seen when <experiment> gave it any cluster (410 n_clusters > 0).
                    This is perfect *separation* with real *measurement*: the clustering ideal, not the clustering.

Score: a Λ counts when the chain accepts it and its final mass is inside the fixed scoring window
|m − m_Λ| ≤ 0.03 GeV (configs/metrics.yaml windows.lambda_mass_half_window_gev; the S4a_tm convention).
Fractions are per accepted D4 event (the generator's acceptance) and per thrown Λ → nπ⁰ (× the acceptance of
413_lambda_gun_acceptance.py). Writes {space}/perf/lambda-ceiling-variants-<experiment>.json.

Usage: uv run scripts/414_lambda_ceiling_variants.py [P1b_R0_thr]
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, repo_path  # noqa: E402
from zdc.lambda_chain import M_N, M_L, PAIRINGS, chain, to_proton  # noqa: E402

SCORE_HALF = 0.03
DEPTH = {"g1": 35880.0, "g2": 35880.0, "n": 36000.0, "p": None}
RNG = np.random.default_rng(20261105)


def line_at(r, zprime):
    vx, vy, vz = to_proton(r["true_vx"], r["true_vy"], r["true_vz"])
    px, py, pz = to_proton(r["true_px"], r["true_py"], r["true_pz"])
    t = (zprime - vz) / pz
    return np.array([vx + t * px, vy + t * py, zprime])  # proton frame


class Response:
    """Measured single-particle response of one experiment: calibrated E/E_true samples and transverse residuals."""

    def __init__(self, reco, dataset, coeff, depth):
        self.pts = {}
        for f in sorted((reco / dataset / "truth").glob("*.npz")):
            if f.name.endswith(".lambda.npz"):
                continue
            e_true = int(f.name.split("GeV")[0].split("_")[-1])
            t = np.load(f)["table"]
            t = t[t["n_clusters"] > 0]
            ecal = coeff[0] * np.power(np.maximum(t["E"], 1e-6), coeff[1])
            ptrue = np.sqrt(t["true_px"] ** 2 + t["true_py"] ** 2 + t["true_pz"] ** 2)
            ratio = ecal / ptrue
            res = []
            for r in t:
                cx, cy, cz = to_proton(r["x"], r["y"], r["z"])
                L = line_at(r, cz)
                res.append((cx - L[0], cy - L[1]))
            res = np.array(res)
            med = np.median(ratio)
            sig = (np.quantile(ratio, 0.84) - np.quantile(ratio, 0.16)) / 2
            self.pts[e_true] = {"ratio": ratio, "median": float(med), "sigma": float(sig), "dxy": res,
                                "sx": float((np.quantile(res[:, 0], .84) - np.quantile(res[:, 0], .16)) / 2),
                                "sy": float((np.quantile(res[:, 1], .84) - np.quantile(res[:, 1], .16)) / 2)}
        self.energies = np.array(sorted(self.pts))

    def draw(self, e):
        k = int(self.energies[np.argmin(np.abs(np.log(self.energies) - np.log(max(e, 0.5))))])
        p = self.pts[k]
        r = RNG.choice(p["ratio"])
        scale = np.sqrt(k / max(e, 0.5))  # stochastic term: σ/E ∝ 1/√E around the measured point
        ratio = 1.0 + (r / p["median"] - 1.0) * scale  # residual bias removed: the refit calibration is the ideal one
        d = p["dxy"][RNG.integers(len(p["dxy"]))]
        return max(ratio, 0.0) * e, d

    def summary(self):
        return {str(k): {"median_ratio": v["median"], "sigma_over_E": v["sigma"], "sx_mm": v["sx"], "sy_mm": v["sy"],
                         "n": int(len(v["ratio"]))} for k, v in self.pts.items()}


def main():
    experiment = sys.argv[1] if len(sys.argv) > 1 else "P1b_R0_thr"
    profile = load_profile()
    reco = Path(profile.reco_root) / experiment
    calib = json.loads(repo_path("space", "perf", f"calib-{experiment}.json").read_text())
    gam = Response(reco, "D2_photon", (calib["photon"]["a"], calib["photon"]["b"]), DEPTH["g1"])
    neu = Response(reco, "D3_neutron", (calib["neutron"]["a"], calib["neutron"]["b"]), DEPTH["n"])
    acc = json.loads(repo_path("space", "perf", "lambda-gun-acceptance.json").read_text())
    result = {"experiment": experiment, "score_half_window_gev": SCORE_HALF,
              "photon_response": gam.summary(), "neutron_response": neu.summary(), "per_momentum": {}}
    print(f"photon response ({experiment}, D2):  " + "  ".join(f"{k}: σ/E {v['sigma_over_E']:.3f} sx {v['sx_mm']:.1f} mm" for k, v in gam.summary().items()))
    print(f"neutron response ({experiment}, D3): " + "  ".join(f"{k}: σ/E {v['sigma_over_E']:.3f} sx {v['sx_mm']:.1f} mm" for k, v in neu.summary().items()))
    head = "  ".join(f"{p}/{i:5s}" for p in PAIRINGS for i in ("ideal", "real"))
    print(f"\nΛ in the ±{SCORE_HALF} GeV scoring window, per accepted D4 event | per thrown Λ → nπ⁰ [%]")
    print(f"{'p':>4s} {'seen':>6s}  {head}")
    d4 = reco / "D4_lambda" / "truth"
    for f in sorted(d4.glob("*.npz"), key=lambda p: int(p.name.split("GeV")[0].split("_")[-1])):
        if f.name.endswith(".lambda.npz"):
            continue
        p = int(f.name.split("GeV")[0].split("_")[-1])
        t = np.load(f)["table"]
        events = np.unique(t["event"])
        cnt = {(pa, i): 0 for pa in PAIRINGS for i in ("ideal", "real")}
        masses = {k: [] for k in cnt}
        seen = 0
        for ev in events:
            rows = {r["role"]: r for r in t[t["event"] == ev]}
            if set(rows) != {"n", "g1", "g2"}:
                continue
            Et = {k: float(np.sqrt(rows[k]["true_px"] ** 2 + rows[k]["true_py"] ** 2 + rows[k]["true_pz"] ** 2
                                   + (M_N ** 2 if k == "n" else 0))) for k in rows}
            Xt = {k: line_at(rows[k], DEPTH[k]) for k in rows}
            vis = all(rows[k]["n_clusters"] > 0 for k in rows)
            seen += vis
            for pa in PAIRINGS:
                m = chain(Et, Xt, pa)
                if m is not None and abs(m - M_L) <= SCORE_HALF:
                    cnt[(pa, "ideal")] += 1
                    masses[(pa, "ideal")].append(m)
            if not vis:
                continue
            Er, Xr = {}, {}
            for k in rows:
                resp = neu if k == "n" else gam
                e, d = resp.draw(Et[k] if k != "n" else np.sqrt(max(Et[k] ** 2 - M_N ** 2, 0)))
                Er[k] = np.sqrt(e * e + M_N * M_N) if k == "n" else e
                Xr[k] = Xt[k] + np.array([d[0], d[1], 0.0])
            for pa in PAIRINGS:
                m = chain(Er, Xr, pa)
                if m is not None and abs(m - M_L) <= SCORE_HALF:
                    cnt[(pa, "real")] += 1
                    masses[(pa, "real")].append(m)
        n = len(events)
        a = acc[str(p)]["all3_inside_4mrad"]
        out = {"events": n, "seen_by_clustering": seen / n, "acceptance_per_thrown": a}
        for (pa, i), c in cnt.items():
            out[f"{pa}_{i}"] = c / n
            out[f"{pa}_{i}_per_thrown"] = c / n * a
            out[f"{pa}_{i}_mass_sigma"] = float(np.std(masses[(pa, i)])) if len(masses[(pa, i)]) > 5 else None
        result["per_momentum"][str(p)] = out
        cells = "  ".join(f"{out[f'{pa}_{i}']:.3f}|{out[f'{pa}_{i}_per_thrown']*100:5.2f}" for pa in PAIRINGS for i in ("ideal", "real"))
        print(f"{p:4d} {seen / n:6.3f}  {cells}")
    path = repo_path("space", "perf", f"lambda-ceiling-variants-{experiment}.json")
    path.write_text(json.dumps(result, indent=1))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
