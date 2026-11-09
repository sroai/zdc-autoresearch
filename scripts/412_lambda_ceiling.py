#!/usr/bin/env python3
"""The S4a ceiling of LambdaReconstruction with ideal ZDC inputs, against the true decay z (Phase 0 item 12).

Why offline: EICrecon's HCal ZDC truth clusters (HcalFarForwardZDCTruthClusters) are
not a perfect-clustering input to FarForwardNeutralsReconstruction. They are built
from tile RecHits with sampFrac 1.0 (energies ~1/0.0273 low against the imaging
clusters, which use 0.0273) and carry tile-level shapes that fail the photon width
cut, so the truth-chain build (Rt) gives zero Λ for reasons that are not
LambdaReconstruction's. This script asks the item's question directly: with
perfect clusters and perfect photon/neutron identification, which Λ → n π⁰ → n γγ
decays does the frozen LambdaReconstruction logic accept?

Ideal inputs per D4 event (from the 410 tables of a reconstruction, R0 by default):
true energies; positions = the true line of each daughter from its decay vertex
to the shower depth in the proton frame (z' = 35880 mm for photons, 36000 mm for
the neutron, the medians of the truth-cluster centroids); the particle is in the
ZDC when it deposited energy in any ZDC cluster (410 column n_clusters > 0).
LambdaReconstruction's logic, as in LambdaReconstruction.cc at the pin:
  step 3: γγ mass from IP-pointing photon momenta (makeGamma: p = E·x/|x|), |m − m_π0| ≤ pi0Window·m_π0
  step 4: nγγ mass from IP-pointing momenta (neutron p = √(E² − m_n²)·x/|x|), |m − m_Λ| ≤ lambdaMassWindow·m_Λ
  IDOLA:  10 halving iterations of the vertex fraction f on the γγ opening angle, then the mass window again
Defaults pi0Window = lambdaMassWindow = 0.1 (relative), iterations 10, z_max 35800 mm.

Prints per momentum: in-acceptance fraction, the fraction passing step 3, steps 3+4,
and the full chain (the ceiling), and the pass fraction in bins of true decay z;
the z where the pass fraction falls below 50 % is the cap. Writes
{space}/perf/lambda-ceiling-<experiment>.json.

Usage: uv run scripts/412_lambda_ceiling.py [R0_stock]
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, repo_path  # noqa: E402

M_PI0, M_L, M_N = 0.1349768, 1.115683, 0.93956542
ROT = -0.025
PI0_WIN, L_WIN, ITER, ZMAX = 0.1, 0.1, 10, 35800.0
DEPTH = {"g1": 35880.0, "g2": 35880.0, "n": 36000.0}
ZBINS = [0, 1000, 2000, 3000, 4000, 6000, 10000, 15000, 20000, 30000, 40000]


def to_proton(x, y, z):  # TVector3::RotateY(-ROT): rotate lab → proton frame
    a = -ROT
    return x * np.cos(a) + z * np.sin(a), y, -x * np.sin(a) + z * np.cos(a)


def to_lab(x, y, z):
    a = ROT
    return x * np.cos(a) + z * np.sin(a), y, -x * np.sin(a) + z * np.cos(a)


def impact(r):
    """Lab position of the daughter at its shower depth: its true line from the vertex to z' = depth (proton frame)."""
    vx, vy, vz = to_proton(r["true_vx"], r["true_vy"], r["true_vz"])
    px, py, pz = to_proton(r["true_px"], r["true_py"], r["true_pz"])
    t = (DEPTH[r["role"]] - vz) / pz
    return np.array(to_lab(vx + t * px, vy + t * py, vz + t * pz))


def four(E, x, m=0.0):
    p = np.sqrt(max(E * E - m * m, 0.0))
    u = x / np.linalg.norm(x)
    return np.array([E, *(p * u)])


def mass(*vs):
    s = np.sum(vs, axis=0)
    m2 = s[0] ** 2 - s[1] ** 2 - s[2] ** 2 - s[3] ** 2
    return np.sqrt(m2) if m2 > 0 else -1.0


def idola(En, E1, E2, xn, x1, x2):
    """reconstruct_from_triplet: the iterated vertex and the Λ mass (proton frame)."""
    xn, x1, x2 = (np.array(to_proton(*v)) for v in (xn, x1, x2))
    pn = np.sqrt(max(En * En - M_N * M_N, 0.0))
    vtx = np.zeros(3)
    f, df = 0.0, 0.5
    th_exp = 2 * np.arcsin(M_PI0 / (2 * np.sqrt(E1 * E2)))
    for _ in range(ITER):
        un, u1, u2 = ((v - vtx) / np.linalg.norm(v - vtx) for v in (xn, x1, x2))
        lam = np.array([En + E1 + E2, *(pn * un + E1 * u1 + E2 * u2)])
        th = np.arccos(np.clip(np.dot(u1, u2), -1, 1))
        if th > th_exp:
            f -= df
        elif th < th_exp:
            f += df
        vtx = lam[1:] * (f * ZMAX / lam[3])
        df /= 2.0
    return mass(lam), vtx[2]


def main():
    experiment = sys.argv[1] if len(sys.argv) > 1 else "R0_stock"
    profile = load_profile()
    d = Path(profile.reco_root) / experiment / "D4_lambda" / "truth"
    result = {"experiment": experiment, "zbins_mm": ZBINS, "per_momentum": {}}
    print(f"ideal-input LambdaReconstruction ceiling ({experiment} acceptance); fractions of generated events")
    print(f"{'p':>4s} {'events':>6s} {'in ZDC':>7s} {'pi0 win':>8s} {'+L win':>7s} {'ceiling':>8s}  cap z50 [m]  pass fraction per true decay z bin [m]")
    for f in sorted(d.glob("*.npz"), key=lambda p: int(p.name.split("GeV")[0].split("_")[-1])):
        if f.name.endswith(".lambda.npz"):
            continue
        p = int(f.name.split("GeV")[0].split("_")[-1])
        t = np.load(f)["table"]
        events = np.unique(t["event"])
        rec = []  # (decay z, in acceptance, step3, step4, full)
        for ev in events:
            rows = {r["role"]: r for r in t[t["event"] == ev]}
            if set(rows) != {"n", "g1", "g2"}:
                continue
            zd = float(rows["n"]["true_vz"])
            acc = all(rows[k]["n_clusters"] > 0 for k in rows)
            s3 = s4 = full = False
            if acc:
                E = {k: float(np.sqrt(rows[k]["true_px"] ** 2 + rows[k]["true_py"] ** 2 + rows[k]["true_pz"] ** 2 + (M_N ** 2 if k == "n" else 0)))
                     for k in rows}
                X = {k: impact(rows[k]) for k in rows}
                g1, g2 = four(E["g1"], X["g1"]), four(E["g2"], X["g2"])
                n = four(E["n"], X["n"], M_N)
                s3 = abs(mass(g1, g2) - M_PI0) <= PI0_WIN * M_PI0
                s4 = s3 and abs(mass(n, g1, g2) - M_L) <= L_WIN * M_L
                if s4:
                    mL, _ = idola(E["n"], E["g1"], E["g2"], X["n"], X["g1"], X["g2"])
                    full = abs(mL - M_L) <= L_WIN * M_L
            rec.append((zd, acc, s3, s4, full))
        r = np.array(rec, dtype=float)
        n_ev = len(events)
        zd, acc, s3, s4, full = r.T
        per_bin, cap = [], None
        for lo, hi in zip(ZBINS[:-1], ZBINS[1:]):
            m = (zd >= lo) & (zd < hi) & (acc > 0)
            frac = float(full[m].mean()) if m.sum() >= 10 else None
            per_bin.append({"z_lo_m": lo / 1000, "z_hi_m": hi / 1000, "in_acceptance": int(m.sum()), "pass": frac})
            if cap is None and frac is not None and frac < 0.5:
                cap = lo / 1000
        out = {"events": n_ev, "in_zdc": float(acc.sum() / n_ev), "pi0_window": float(s3.sum() / n_ev),
               "lambda_window": float(s4.sum() / n_ev), "ceiling": float(full.sum() / n_ev),
               "ceiling_err": float(np.sqrt(full.mean() * (1 - full.mean()) / n_ev)),
               "decay_z_median_m": float(np.median(zd) / 1000), "cap_z50_m": cap, "per_decay_z": per_bin}
        result["per_momentum"][str(p)] = out
        bins = " ".join(f"{b['pass']:.2f}" if b["pass"] is not None else "  - " for b in per_bin)
        print(f"{p:4d} {n_ev:6d} {out['in_zdc']:7.3f} {out['pi0_window']:8.3f} {out['lambda_window']:7.3f} {out['ceiling']:8.3f}  "
              f"{cap if cap is not None else '-':>10}   {bins}")
    print("z bins [m]: " + " ".join(f"{lo/1000:g}-{hi/1000:g}" for lo, hi in zip(ZBINS[:-1], ZBINS[1:])))
    out = repo_path("space", "perf", f"lambda-ceiling-{experiment}.json")
    out.write_text(json.dumps(result, indent=1))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
