#!/usr/bin/env python3
"""The ZDC photon pairing of FarForwardNeutralsReconstruction (chooseLambdaPhotonPair, X9 and later), emulated offline on
a row's MSF outputs, to rank pairing variants before a try (Phase 5 diagnostic, never a selector).

Per event: the ZDC Hcal clusters (energy, position, shape eigenvalues) → the photon tag (depth ≤ gammaZMaxOffset + z_ZDC
in the proton frame, length ≤ 150, at most one width > 12) → with more than two tagged clusters, every tagged pair is a
photon hypothesis, the neutron is every other cluster (summed, at the energy-weighted centroid), the decay depth comes by
bisection on the γγ opening angle along the momentum-weighted slope, and the pair with the lowest
  ((m_γγ − m_π⁰) / (0.1 m_π⁰))² + ((m_Λ − m_Λ,PDG) / σ_Λ)² + w_depth · (−ln decay-depth density) + w_pd · photon depth
wins. Reproduction: the emulated pair must be the row's photon neutrals in (nearly) every event with > 2 tagged clusters.

Grading (truth only grades): for each Λ → nπ⁰ of the all-ZDC regime (`210` homes), the pick is good when its two
clusters are pure (association weight ≥ 0.8) for the two distinct true photons and the emulated Λ mass is within ±30 MeV;
the oracle needs some such pair among the tagged clusters. A variant changes σ_Λ, w_depth, w_pd, the photon law scale or
adds a crystal term; its good count is compared with the stock rule's on the same events.

Usage: uv run scripts/473_msf_pairing_emulation.py Y2_vertex_lever_arm --dataset D6s_9x275 [--files N]
"""
import argparse
import importlib.util
import json
import math
import sys
from collections import Counter
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import repo_path  # noqa: E402

spec = importlib.util.spec_from_file_location("r210", repo_path("scripts", "210_msf_lambda_regimes.py"))
r210 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r210)

M_PI0, M_L, M_N = 0.1349768, 1.115683, 0.93956542
ROT = -0.025
Z_ZDC = 36716.35            # HcalFarForwardZDC_SiPMonTile_r_pos in mm (the ZDC centre, Phase 4 F7)
ZMAX = Z_ZDC - 691.4        # photon tag depth limit (gammaZMaxOffset)
LMAX, WMAX = 150.0, 12.0
C = "HcalFarForwardZDCClusters"; A = "HcalFarForwardZDCClusterAssociations"; N = "ReconstructedHcalFarForwardZDCNeutrals"

STOCK = {"sigma_l": 0.04, "w_depth": 1.5, "w_pd": 1.0, "ag": 3.952, "bg": 0.938, "an": 6.214, "bn": 0.740, "iters": 10,
         "pi0_win": 0.1, "ctau": 78.9}


def to_proton(x, y, z):
    ca, sa = math.cos(-ROT), math.sin(-ROT)
    return np.stack([x * ca + z * sa, y, -x * sa + z * ca], axis=-1)


def choose(E, P, cand, p):
    """E: raw cluster energies; P: proton-frame positions (n, 3); cand: tagged indices. Returns (i, j, m_Λ, score) or None."""
    if len(cand) < 2:
        return None
    ii, jj = np.triu_indices(len(cand), 1)
    a, b = np.asarray(cand)[ii], np.asarray(cand)[jj]
    E1, E2 = p["ag"] * E[a] ** p["bg"], p["ag"] * E[b] ** p["bg"]
    tot = E.sum(); raw = tot - E[a] - E[b]
    sx = (E[:, None] * P).sum(axis=0)
    cen = (sx[None, :] - E[a, None] * P[a] - E[b, None] * P[b]) / np.where(raw > 0, raw, 1)[:, None]
    En = p["an"] * np.where(raw > 0, raw, 1e-9) ** p["bn"]
    ok = (raw > 0) & (En > M_N) & (len(E) > 2)
    pn = np.sqrt(np.maximum(En ** 2 - M_N ** 2, 0))
    x1, x2 = P[a], P[b]
    wz = pn * cen[:, 2] + E1 * x1[:, 2] + E2 * x2[:, 2]
    tx = (pn * cen[:, 0] + E1 * x1[:, 0] + E2 * x2[:, 0]) / wz
    ty = (pn * cen[:, 1] + E1 * x1[:, 1] + E2 * x2[:, 1]) / wz
    th = 2 * np.arcsin(np.minimum(1.0, M_PI0 / (2 * np.sqrt(E1 * E2))))
    lo, hi = np.zeros_like(E1), np.full_like(E1, Z_ZDC)

    def angle(z):
        v = np.stack([tx * z, ty * z, z], axis=-1)
        u, w = x1 - v, x2 - v
        c = (u * w).sum(-1) / np.linalg.norm(u, axis=-1) / np.linalg.norm(w, axis=-1)
        return np.arccos(np.clip(c, -1, 1))
    for _ in range(p["iters"]):
        z = 0.5 * (lo + hi)
        far = angle(z) > th
        hi = np.where(far, z, hi); lo = np.where(far, lo, z)
    v = np.stack([tx * lo, ty * lo, lo], axis=-1)
    un = (cen - v) / np.linalg.norm(cen - v, axis=-1)[:, None]
    u1 = (x1 - v) / np.linalg.norm(x1 - v, axis=-1)[:, None]
    u2 = (x2 - v) / np.linalg.norm(x2 - v, axis=-1)[:, None]
    pg = E1[:, None] * u1 + E2[:, None] * u2; pl = pg + pn[:, None] * un
    Eg, El = E1 + E2, En + E1 + E2
    mpi = np.sqrt(np.maximum(Eg ** 2 - (pg ** 2).sum(-1), 0))
    pL = np.linalg.norm(pl, axis=-1); ml = np.sqrt(np.maximum(El ** 2 - pL ** 2, 0))
    L = np.maximum(pL / M_L * p["ctau"], 1.0)
    depth = lo / L + np.log(L * np.maximum(1 - np.exp(-Z_ZDC / L), 1e-12))
    pdep = (x1[:, 2] + x2[:, 2] - 2 * Z_ZDC) / 100.0
    score = ((mpi - M_PI0) / (p["pi0_win"] * M_PI0)) ** 2 + ((ml - M_L) / p["sigma_l"]) ** 2 + p["w_depth"] * depth \
        + p["w_pd"] * pdep + p.get("crys_w", 0.0) * p.get("crys_pen", np.zeros(len(E)))[a] + p.get("crys_w", 0.0) * p.get("crys_pen", np.zeros(len(E)))[b]
    score = np.where(ok, score, np.inf)
    k = int(np.argmin(score))
    if not np.isfinite(score[k]):
        return None
    return int(a[k]), int(b[k]), float(ml[k]), float(score[k])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("row")
    ap.add_argument("--dataset", default="D6s_9x275")
    ap.add_argument("--files", type=int, default=40)
    ap.add_argument("--grid", choices=["knobs", "scales"], default="scales")
    args = ap.parse_args()
    J = json.loads(repo_path("space", "perf", f"msf-regimes-{args.row}-{args.dataset}.json").read_text())
    per = {(l["file"], l["event"]): l for l in J["per_lambda"] if l["homes"] == ["ZDC", "ZDC", "ZDC"]}
    variants = {"stock": dict(STOCK)}
    if args.grid == "knobs":
        for s in (0.03, 0.05, 0.065):
            variants[f"sigma_l={s}"] = {**STOCK, "sigma_l": s}
        for w in (0.75, 2.25, 3.0):
            variants[f"w_depth={w}"] = {**STOCK, "w_depth": w}
        for w in (0.0, 0.5, 2.0):
            variants[f"w_pd={w}"] = {**STOCK, "w_pd": w}
    else:   # ranking-only energy scales: the pick uses scaled energies, the graded mass the stock ones
        for fg in (1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3):
            for fn in (0.8, 0.85, 0.9, 0.95, 1.0):
                if fg == 1.0 and fn == 1.0:
                    continue
                variants[f"g{fg:.2f}_n{fn:.2f}"] = {**STOCK, "ag": STOCK["ag"] * fg, "an": STOCK["an"] * fn}
    good = Counter(); oracle = 0; repro = Counter(); n_lam = 0; found = 0
    files = sorted({k[0] for k in per})[: args.files]
    for fname in files:
        a = r210.mc_arrays(uproot.open(f"/data/zdc-autoresearch/datasets/{args.dataset}/{fname}")["events"])
        R = uproot.open(f"/data/zdc-autoresearch/reco/{args.row}/{args.dataset}/{fname.replace('.edm4hep', '.edm4eic')}")["events"].arrays(
            [f"{C}.energy", f"{C}.position.x", f"{C}.position.y", f"{C}.position.z", f"{C}.shapeParameters_begin", f"_{C}_shapeParameters",
             f"{A}.weight", f"_{A}_rec.index", f"_{A}_sim.index", f"{N}.PDG", f"{N}.clusters_begin", f"{N}.clusters_end",
             f"_{N}_clusters.index"], library="ak")
        for ev in range(len(R)):
            l = per.get((fname, ev))
            if l is None:
                continue
            n_lam += 1
            found += bool(l[args.row]["matched"])
            E = ak.to_numpy(R[f"{C}.energy"][ev]).astype(float)
            P = to_proton(*(ak.to_numpy(R[f"{C}.position.{q}"][ev]).astype(float) for q in "xyz"))
            sb = ak.to_numpy(R[f"{C}.shapeParameters_begin"][ev]); sp = ak.to_numpy(R[f"_{C}_shapeParameters"][ev])
            zl = P[:, 2] if len(E) else np.array([])
            cand = []
            for c in range(len(E)):
                lam = [math.sqrt(max(sp[sb[c] + k], 0)) for k in (4, 5, 6)]
                if zl[c] <= ZMAX and all(v <= LMAX for v in lam) and sum(v > WMAX for v in lam) < 2:
                    cand.append(c)
            pdg = ak.to_numpy(R[f"{N}.PDG"][ev]); cb = ak.to_numpy(R[f"{N}.clusters_begin"][ev]); ce = ak.to_numpy(R[f"{N}.clusters_end"][ev])
            ci = ak.to_numpy(R[f"_{N}_clusters.index"][ev])
            actual = sorted(int(ci[cb[k]]) for k in range(len(pdg)) if pdg[k] == 22)
            lams, owner = r210.truth_event(a, ev); base = l["owner_base"]
            w = ak.to_numpy(R[f"{A}.weight"][ev]); rc = ak.to_numpy(R[f"_{A}_rec.index"][ev]); si = ak.to_numpy(R[f"_{A}_sim.index"][ev]).astype(int)
            own = owner[si] if len(si) else np.array([], dtype=int)
            pur = {r: np.array([w[(rc == c) & (own == base + r)].sum() for c in range(len(E))]) for r in (1, 2)}
            g1 = {c for c in cand if pur[1][c] >= 0.8}; g2 = {c for c in cand if pur[2][c] >= 0.8}
            has_oracle = bool(g1 and g2)
            oracle += has_oracle
            for name, p in variants.items():
                pick = choose(E, P, cand, p) if len(cand) > 2 else None
                if name == "stock" and len(cand) > 2:
                    repro["match" if pick and sorted(pick[:2]) == actual else "differ"] += 1
                if pick is None:
                    continue
                i, j, ml, _ = pick
                ml = choose(E, P, [i, j], STOCK)[2]   # the output energies are the stock ones
                if ((i in g1 and j in g2) or (i in g2 and j in g1)) and abs(ml - M_L) < 0.03:
                    good[name] += 1
    out = {"row": args.row, "dataset": args.dataset, "files": len(files), "all_zdc_lambda": n_lam, "oracle_available": oracle,
           "reproduction": dict(repro), "found_in_row": found, "good": dict(good), "variants": {k: v for k, v in variants.items()}}
    path = repo_path("space", "perf", f"pairing-msf-{args.row}-{args.dataset}-{args.grid}.json")
    path.write_text(json.dumps(out, indent=1))
    print(f"{args.row} {args.dataset} ({len(files)} files): all-ZDC Λ {n_lam}, found by the row {found}, oracle pair available {oracle}; reproduction {dict(repro)}")
    for k in variants:
        print(f"  {k:22s} good {good[k]:5d}  ({good[k] - good['stock']:+d})")
    print("wrote", path)


if __name__ == "__main__":
    main()
