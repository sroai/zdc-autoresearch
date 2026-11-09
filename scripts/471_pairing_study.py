#!/usr/bin/env python3
"""Which ranking picks the true γγ pair? An offline study on a row's D4 output (Phase 4 diagnostic, never a selector).

Events (eligible): some ZDC cluster is pure for the true neutron, and some pair of ZDC photon neutrals holds clusters
pure (association weight ≥ purity_min) for the two distinct true photons, as 410's S4a_tm requires. For every pair of ZDC
photon neutrals with the event's ZDC neutron, the stable-vertex fit of X1 (bisection on the γγ opening angle along the
momentum-weighted slope, `iterations` halvings of [0, z_ZDC]) gives the fitted π⁰ and Λ masses and the decay depth.
Each ranking rule picks one pair; a pick counts when it is truth-good and its fitted mass is inside ±30 MeV, i.e. when
EICrecon would score it S4a_tm. Truth only grades the pick; the rules use no truth. The x1 rule's count is checked
against the row's in-EICrecon matched count (410).

Rules (lower score wins):
  x1        (Δm_π⁰ / 0.1 m_π⁰)² + (Δm_Λ / 0.1 m_Λ)²                       X1's ranking (R3 / PR 3063)
  lam       |Δm_Λ|
  x1_e      x1 − w · ln(E1·E2)  (prefers energetic photon pairs)
  x1_z      x1 + depth term: −ln of the Λ decay-depth density exp(−z/λ)/λ, λ = (p_Λ/m_Λ)·cτ, normalised in [0, z_ZDC]
  x1_ez     both
Writes space/perf/pairing-study-<row>.json and prints the fraction of events whose pick is the true pair, per momentum.

Usage: uv run scripts/471_pairing_study.py X1_offline_chain [--iterations 10] [--w 1.0]
"""
import argparse
import json
import math
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, metrics_config, repo_path  # noqa: E402

M_PI0, M_L, M_N = 0.1349768, 1.115683, 0.93956542
CTAU = 78.9          # mm, PDG cτ of the Λ (a physical constant)
ROT = -0.025         # globalToProtonRotation
ZMAX = 35800.0       # HcalFarForwardZDC_SiPMonTile_r_pos (mm), as LambdaReconstruction reads it
NEU = "ReconstructedHcalFarForwardZDCNeutrals"
WIN = 0.03          # the scoring window of configs/metrics.yaml (GeV)
GRID_SIGMA_L = (0.03, 0.04, 0.05, 0.065)   # Λ-mass term width (GeV); X2 uses 0.1·m_Λ
GRID_WDEPTH = (1.0, 1.5, 2.0, 3.0)          # weight of the decay-depth term; X2 uses 1


def to_proton(x, y, z):
    a = -ROT
    return (x * math.cos(a) + z * math.sin(a), y, -x * math.sin(a) + z * math.cos(a))


def unit(v):
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return (v[0] / n, v[1] / n, v[2] / n)


def fit(En, E1, E2, xn, x1, x2, iters):
    pn = math.sqrt(max(En * En - M_N * M_N, 0.0))
    wz = pn * xn[2] + E1 * x1[2] + E2 * x2[2]
    t = ((pn * xn[0] + E1 * x1[0] + E2 * x2[0]) / wz, (pn * xn[1] + E1 * x1[1] + E2 * x2[1]) / wz)
    th_exp = 2 * math.asin(min(1.0, M_PI0 / (2 * math.sqrt(E1 * E2))))
    lo, hi = 0.0, ZMAX
    for _ in range(iters):
        z = 0.5 * (lo + hi)
        v = (t[0] * z, t[1] * z, z)
        u1, u2 = unit([x1[i] - v[i] for i in range(3)]), unit([x2[i] - v[i] for i in range(3)])
        th = math.acos(max(-1.0, min(1.0, sum(u1[i] * u2[i] for i in range(3)))))
        if th > th_exp:
            hi = z
        else:
            lo = z
    v = (t[0] * lo, t[1] * lo, lo)
    un, u1, u2 = (unit([x[i] - v[i] for i in range(3)]) for x in (xn, x1, x2))
    p = [pn * un[i] + E1 * u1[i] + E2 * u2[i] for i in range(3)]
    E = En + E1 + E2
    mL = math.sqrt(max(E * E - sum(c * c for c in p), 0.0))
    g = [E1 * u1[i] + E2 * u2[i] for i in range(3)]
    mpi = math.sqrt(max((E1 + E2) ** 2 - sum(c * c for c in g), 0.0))
    return mL, mpi, lo, math.sqrt(sum(c * c for c in p))


def depth_nll(z, p):
    lam = max(p / M_L * CTAU, 1.0)
    norm = 1.0 - math.exp(-ZMAX / lam)
    return z / lam + math.log(lam * max(norm, 1e-12))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("row")
    ap.add_argument("--iterations", type=int, default=10)
    ap.add_argument("--w", type=float, default=1.0)
    ap.add_argument("--an", type=float, default=8.064, help="the row's neutron law a (E = a·raw^b), X1's by default")
    ap.add_argument("--bn", type=float, default=0.700)
    ap.add_argument("--max-depth", type=float, default=0.0, help="photon candidates only above this depth (mm)")
    ap.add_argument("--ag", type=float, default=0.0, help="photon law a (recompute photon energies)")
    ap.add_argument("--bg", type=float, default=1.0)
    ap.add_argument("--tag", default="", help="suffix of the output JSON")
    args = ap.parse_args()
    profile = load_profile()
    pmin = float(metrics_config().truth_match.purity_min)
    reco = Path(profile.reco_root) / args.row / "D4_lambda"
    rules = ("x3C", "x9", "x9L0.5", "x9L1.0", "x9L2.0", "x9D0.5", "x9D1.0")
    out = {"row": args.row, "iterations": args.iterations, "w": args.w, "per_momentum": {}}
    print(f"{args.row}: S4a_tm-equivalent picks per momentum (eligible = a truth-good pair exists)")
    print("   p | " + " ".join(f"{r:>7s}" for r in rules + ("oracle", "oracleN")) + " | eligible  pairs/ev")
    for root in sorted(reco.glob("D4_lambda_*GeV_seed1.edm4eic.root")):
        p = root.name.split("_")[2].replace("GeV", "")
        tdir = next(d for d in (reco, reco / "truth") if (d / f"{root.name[:-5]}.npz").exists())
        parts = np.load(tdir / f"{root.name[:-5]}.npz")["table"]
        t = uproot.open(root)["events"]
        a = t.arrays([f"{NEU}.PDG", f"{NEU}.energy", f"{NEU}.referencePoint.x", f"{NEU}.referencePoint.y",
                      f"{NEU}.referencePoint.z", f"{NEU}.clusters_begin", f"{NEU}.clusters_end", f"_{NEU}_clusters.index",
                      "HcalFarForwardZDCClusters.position.x", "HcalFarForwardZDCClusters.position.y",
                      "HcalFarForwardZDCClusters.position.z", "HcalFarForwardZDCClusters.energy",
                      "HcalFarForwardZDCClusters.shapeParameters_begin", "_HcalFarForwardZDCClusters_shapeParameters"], library="ak")
        L = {k: ak.to_list(a[k]) for k in a.fields}
        good = {r: 0 for r in rules + ("oracle", "oracleN")}
        grid = {(sl, wd): 0 for sl in GRID_SIGMA_L for wd in GRID_WDEPTH}
        n_elig = n_pairs = 0
        A = t.arrays(["MCParticles.PDG", "MCParticles.generatorStatus", "HcalFarForwardZDCClusterAssociations.weight",
                      "_HcalFarForwardZDCClusterAssociations_rec.index", "_HcalFarForwardZDCClusterAssociations_sim.index"],
                     library="ak")
        M = {k: ak.to_list(A[k]) for k in A.fields}
        for ev in range(t.num_entries):
            mpdg, mst = M["MCParticles.PDG"][ev], M["MCParticles.generatorStatus"][ev]
            i_n = next((i for i in range(len(mpdg)) if mpdg[i] == 2112 and mst[i] == 1), None)
            i_g = [i for i in range(len(mpdg)) if mpdg[i] == 22 and mst[i] == 1][:2]
            if i_n is None or len(i_g) < 2:
                continue
            pur = {}
            for w, rc, sm in zip(M["HcalFarForwardZDCClusterAssociations.weight"][ev],
                                 M["_HcalFarForwardZDCClusterAssociations_rec.index"][ev],
                                 M["_HcalFarForwardZDCClusterAssociations_sim.index"][ev]):
                pur[(rc, sm)] = max(pur.get((rc, sm), 0.0), w)
            pdg, en = L[f"{NEU}.PDG"][ev], L[f"{NEU}.energy"][ev]
            if args.ag:   # photon energies recomputed from their clusters with another photon law (a refit)
                en = list(en)
                _cb, _ci, _ecl = L[f"{NEU}.clusters_begin"][ev], L[f"_{NEU}_clusters.index"][ev], L["HcalFarForwardZDCClusters.energy"][ev]
                for k in range(len(pdg)):
                    if pdg[k] == 22:
                        en[k] = args.ag * _ecl[_ci[_cb[k]]] ** args.bg
            cb, ci = L[f"{NEU}.clusters_begin"][ev], L[f"_{NEU}_clusters.index"][ev]
            gam = [k for k in range(len(pdg)) if pdg[k] == 22]
            gam_all = list(gam)   # every tagged cluster: those left out of the photon list join the neutron
            if args.max_depth:
                cz = L["HcalFarForwardZDCClusters.position.z"][ev]; cx = L["HcalFarForwardZDCClusters.position.x"][ev]
                gam = [k for k in gam
                       if -cx[ci[cb[k]]] * math.sin(-ROT) + cz[ci[cb[k]]] * math.cos(-ROT) - ZMAX < args.max_depth]
            neu = [k for k in range(len(pdg)) if pdg[k] == 2112]
            if not neu or not any(pur.get((c, i_n), 0) >= pmin for (c, _) in pur):
                continue
            good_for = {k: {g for g in i_g if pur.get((ci[cb[k]], g), 0) >= pmin} for k in gam}

            def truth_good(a, b):
                return any(x != y for x in good_for[a] for y in good_for[b])
            if not any(truth_good(gam[i], gam[j]) for i in range(len(gam)) for j in range(i + 1, len(gam))):
                continue
            n_elig += 1
            k_n = neu[0]
            xn = to_proton(L[f"{NEU}.referencePoint.x"][ev][k_n], L[f"{NEU}.referencePoint.y"][ev][k_n],
                           L[f"{NEU}.referencePoint.z"][ev][k_n])
            pos = {k: to_proton(L["HcalFarForwardZDCClusters.position.x"][ev][ci[cb[k]]],
                                L["HcalFarForwardZDCClusters.position.y"][ev][ci[cb[k]]],
                                L["HcalFarForwardZDCClusters.position.z"][ev][ci[cb[k]]]) for k in gam}
            scores = {r: [] for r in ("x1", "lam", "x1_e", "x1_z", "x1_ez", "x1N", "x1_zN", "x1_z2N", "x1_zNL", "x1_zNC", "x3C", "x3Cd0.5", "x3Cd1.0", "x3Cd2.0", "x3Cd4.0", "x3Ce1.0", "x3Ce3.0", "x9", "x9L0.5", "x9L1.0", "x9L2.0", "x9D0.5", "x9D1.0")}
            ecl = L["HcalFarForwardZDCClusters.energy"][ev]
            terms = []
            raw_n = (en[k_n] / args.an) ** (1.0 / args.bn)
            orc = orcN = False
            for i in range(len(gam)):
                for j in range(i + 1, len(gam)):
                    g1, g2 = gam[i], gam[j]
                    mL, mpi, z, pl = fit(en[k_n], en[g1], en[g2], xn, pos[g1], pos[g2], args.iterations)
                    x1 = ((mpi - M_PI0) / (0.1 * M_PI0)) ** 2 + ((mL - M_L) / (0.1 * M_L)) ** 2
                    e = -args.w * math.log(max(en[g1] * en[g2], 1e-9))
                    zt = depth_nll(z, pl)
                    ok = truth_good(g1, g2) and abs(mL - M_L) < WIN
                    # the neutron of this hypothesis also holds the photon candidates the pair leaves out
                    En2 = args.an * (raw_n + sum(ecl[ci[cb[k]]] for k in gam_all if k not in (g1, g2))) ** args.bn
                    mL2, mpi2, z2, pl2 = fit(En2, en[g1], en[g2], xn, pos[g1], pos[g2], args.iterations)
                    x1N = ((mpi2 - M_PI0) / (0.1 * M_PI0)) ** 2 + ((mL2 - M_L) / (0.1 * M_L)) ** 2
                    okN = truth_good(g1, g2) and abs(mL2 - M_L) < WIN
                    orc, orcN = orc or ok, orcN or okN
                    # neutron position of this hypothesis: the leader / the energy centroid of the clusters the pair leaves out
                    rest = [c for c in range(len(ecl)) if c not in (ci[cb[g1]], ci[cb[g2]]) and ecl[c] > 0]
                    if rest:
                        lead = max(rest, key=lambda c: ecl[c])
                        xl = to_proton(*(L[f"HcalFarForwardZDCClusters.position.{q}"][ev][lead] for q in "xyz"))
                        es = sum(ecl[c] for c in rest)
                        xc = to_proton(*(sum(ecl[c] * L[f"HcalFarForwardZDCClusters.position.{q}"][ev][c] for c in rest) / es
                                         for q in "xyz"))
                        for tag, xpos in (("L", xl), ("C", xc)):
                            m3, p3, z3, pl3 = fit(En2, en[g1], en[g2], xpos, pos[g1], pos[g2], args.iterations)
                            s3 = ((p3 - M_PI0) / (0.1 * M_PI0)) ** 2 + ((m3 - M_L) / (0.1 * M_L)) ** 2 + depth_nll(z3, pl3)
                            scores[f"x1_zN{tag}"].append((s3, truth_good(g1, g2) and abs(m3 - M_L) < WIN))
                            if tag == "C":   # X3's weights (σ_Λ 0.04 GeV, depth weight 1.5) with the neutron at the centroid
                                scores["x3C"].append((((p3 - M_PI0) / (0.1 * M_PI0)) ** 2 + ((m3 - M_L) / 0.04) ** 2
                                                      + 1.5 * depth_nll(z3, pl3), truth_good(g1, g2) and abs(m3 - M_L) < WIN))
                            if tag == "C":   # soft photon terms on top of x3C: candidate depth and energy
                                base3 = ((p3 - M_PI0) / (0.1 * M_PI0)) ** 2 + ((m3 - M_L) / 0.04) ** 2 + 1.5 * depth_nll(z3, pl3)
                                okc = truth_good(g1, g2) and abs(m3 - M_L) < WIN
                                cxv, czv = L["HcalFarForwardZDCClusters.position.x"][ev], L["HcalFarForwardZDCClusters.position.z"][ev]
                                dep = [-cxv[ci[cb[g]]] * math.sin(-ROT) + czv[ci[cb[g]]] * math.cos(-ROT) - ZMAX for g in (g1, g2)]
                                for wd in (0.5, 1.0, 2.0, 4.0):
                                    scores[f"x3Cd{wd}"].append((base3 + wd * (dep[0] + dep[1]) / 100.0, okc))
                                for we in (1.0, 3.0):
                                    scores[f"x3Ce{we}"].append((base3 + we * (5.0 / max(en[g1], 0.1) + 5.0 / max(en[g2], 0.1)), okc))
                                # X9's rule (depth term 1.0 / 100 mm) plus a shower-length or dispersion term
                                x9 = base3 + 1.0 * (dep[0] + dep[1]) / 100.0
                                scores["x9"].append((x9, okc))
                                sb, sp = L["HcalFarForwardZDCClusters.shapeParameters_begin"][ev], L["_HcalFarForwardZDCClusters_shapeParameters"][ev]
                                ln = [math.sqrt(max(sp[sb[ci[cb[g]]] + 4], 0.0)) for g in (g1, g2)]
                                ds = [sp[sb[ci[cb[g]]] + 1] for g in (g1, g2)]
                                for wl in (0.5, 1.0, 2.0):
                                    scores[f"x9L{wl}"].append((x9 + wl * (ln[0] + ln[1]) / 100.0, okc))
                                for wq in (0.5, 1.0):
                                    scores[f"x9D{wq}"].append((x9 + wq * (ds[0] + ds[1]) / 100.0, okc))
                            if tag == "L":   # the X2 rule's terms, for the weight grid
                                terms.append(((p3 - M_PI0) / (0.1 * M_PI0), m3 - M_L, depth_nll(z3, pl3),
                                              truth_good(g1, g2) and abs(m3 - M_L) < WIN))
                    for r, sc, flag in (("x1", x1, ok), ("lam", abs(mL - M_L), ok), ("x1_e", x1 + e, ok),
                                        ("x1_z", x1 + zt, ok), ("x1_ez", x1 + e + zt, ok),
                                        ("x1N", x1N, okN), ("x1_zN", x1N + depth_nll(z2, pl2), okN),
                                        ("x1_z2N", x1N + 2 * depth_nll(z2, pl2), okN)):
                        scores[r].append((sc, flag))
                    n_pairs += 1
            for sl in GRID_SIGMA_L:
                for wd in GRID_WDEPTH:
                    if terms and min(terms, key=lambda q: q[0] ** 2 + (q[1] / sl) ** 2 + wd * q[2])[3]:
                        grid[(sl, wd)] += 1
            good["oracle"] += orc
            good["oracleN"] += orcN
            for r in rules:
                if scores[r] and min(scores[r], key=lambda x: x[0])[1]:
                    good[r] += 1
        lam_tab = np.load(tdir / f"{root.name[:-5]}.lambda.npz")["table"]
        out["per_momentum"][p] = {"events": t.num_entries, "eligible": n_elig,
                                  "matched_in_eicrecon": int(lam_tab["matched"].sum()), **{r: good[r] for r in rules + ("oracle", "oracleN")}}
        out["per_momentum"][p]["grid"] = {f"{sl}_{wd}": n for (sl, wd), n in grid.items()}
        print(f"{p:>4s} | " + " ".join(f"{good[r]:7d}" for r in rules + ("oracle", "oracleN"))
              + f" | {n_elig:8d}  {n_pairs / max(n_elig, 1):7.1f}  in EICrecon {int(lam_tab['matched'].sum())}")
    path = repo_path("space", "perf", f"pairing-study-{args.row}{args.tag}.json")
    path.write_text(json.dumps(out, indent=1))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
