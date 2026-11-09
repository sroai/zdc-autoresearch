#!/usr/bin/env python3
"""A mixed photon hypothesis for the ZDC pairing, emulated offline on a row's MSF outputs (Phase 5 diagnostic, never a
selector): beside every tagged ZDC pair (473's emulation of chooseLambdaPhotonPair), one tagged ZDC cluster with one B0
photon candidate (the B0 neutrals' LeaderOnly set: up to 4 leading B0 clusters ≥ 1 GeV, energy 0.99·E^1.14). In a mixed
hypothesis the neutron is every ZDC cluster but the photon's, and the vertex is Y2's: the slope with each daughter's lever
arm, the depth by bisection on the γγ opening angle up to just short of the nearest impact point. Its score has the stock
terms; the photon-depth term counts the ZDC photon twice (the pair term sums two photons). If a mixed hypothesis wins,
only its ZDC cluster is written as a ZDC photon and LambdaReconstruction pairs it with the B0 photon.

Grading (truth only grades): an all-ZDC Λ is good when the pick is a ZDC pair pure (≥ 0.8) for both true photons with the
Λ mass within ±30 MeV (as 473); a γ B0 + γ ZDC Λ is good when the pick is mixed, its ZDC cluster pure for the ZDC photon,
its B0 cluster pure for the B0 photon, and the mixed mass within ±30 MeV. Compared with the row's own found counts.

Usage: uv run scripts/474_msf_mixed_pairing.py Y2_vertex_lever_arm --dataset D6s_9x275 [--files N]
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

spec = importlib.util.spec_from_file_location("e473", repo_path("scripts", "473_msf_pairing_emulation.py"))
e473 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e473)
r210 = e473.r210
M_PI0, M_L, M_N, Z_ZDC, STOCK = e473.M_PI0, e473.M_L, e473.M_N, e473.Z_ZDC, e473.STOCK
B = "B0ECalClusters"; BA = "B0ECalClusterAssociations"
C, A = e473.C, e473.A


def mixed_scores(E, P, cand, Eb, Pb, p, w_mixed_pd=2.0, b0_law=(0.99, 1.14)):
    """Every (tagged ZDC cluster, B0 candidate) hypothesis: list of (score, i, k, m_Λ)."""
    out = []
    tot = E.sum(); sx = (E[:, None] * P).sum(axis=0)
    for i in cand:
        raw = tot - E[i]
        if raw <= 0:
            continue
        cen = (sx - E[i] * P[i]) / raw
        En = p["an"] * raw ** p["bn"]
        if En <= M_N:
            continue
        pn = math.sqrt(En * En - M_N * M_N)
        E1 = p["ag"] * E[i] ** p["bg"]
        for k in range(len(Eb)):
            E2 = b0_law[0] * Eb[k] ** b0_law[1]
            pts = [(pn, cen), (E1, P[i]), (E2, Pb[k])]
            zf = 0.999 * min(q[2] for _, q in pts)
            if zf <= 0:
                continue

            def slope(z):
                sxx = syy = sw = 0.0
                for pp, q in pts:
                    wq = pp / (q[2] - z); sxx += wq * q[0]; syy += wq * q[1]; sw += wq
                den = (pn + E1 + E2) + z * sw
                return np.array([sxx / den, syy / den, 1.0])
            th = 2 * math.asin(min(1.0, M_PI0 / (2 * math.sqrt(E1 * E2))))
            lo, hi = 0.0, min(Z_ZDC, zf)
            for _ in range(p["iters"]):
                z = 0.5 * (lo + hi); v = slope(z) * z
                u, w = P[i] - v, Pb[k] - v
                ang = math.acos(max(-1.0, min(1.0, float(u @ w / np.linalg.norm(u) / np.linalg.norm(w)))))
                if ang > th:
                    hi = z
                else:
                    lo = z
            v = slope(lo) * lo
            un = (cen - v) / np.linalg.norm(cen - v); u1 = (P[i] - v) / np.linalg.norm(P[i] - v); u2 = (Pb[k] - v) / np.linalg.norm(Pb[k] - v)
            pg = E1 * u1 + E2 * u2; pl = pg + pn * un
            mpi = math.sqrt(max((E1 + E2) ** 2 - float(pg @ pg), 0)); pL = float(np.linalg.norm(pl))
            ml = math.sqrt(max((En + E1 + E2) ** 2 - pL ** 2, 0))
            L = max(pL / M_L * p["ctau"], 1.0)
            depth = lo / L + math.log(L * max(1 - math.exp(-Z_ZDC / L), 1e-12))
            pdep = w_mixed_pd * (P[i][2] - Z_ZDC) / 100.0
            s = ((mpi - M_PI0) / (p["pi0_win"] * M_PI0)) ** 2 + ((ml - M_L) / p["sigma_l"]) ** 2 + p["w_depth"] * depth + p["w_pd"] * pdep
            out.append((s, i, k, ml))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("row")
    ap.add_argument("--dataset", default="D6s_9x275")
    ap.add_argument("--files", type=int, default=40)
    args = ap.parse_args()
    J = json.loads(repo_path("space", "perf", f"msf-regimes-{args.row}-{args.dataset}.json").read_text())
    per = {}
    for l in J["per_lambda"]:
        if l["homes"][0] == "ZDC" and sorted(l["homes"][1:]) in (["ZDC", "ZDC"], ["B0", "ZDC"]):
            per[(l["file"], l["event"])] = l
    variants = {"mixed pd×3": 3.0}
    res = Counter(); files = sorted({k[0] for k in per})[: args.files]
    for fname in files:
        a = r210.mc_arrays(uproot.open(f"/data/zdc-autoresearch/datasets/{args.dataset}/{fname}")["events"])
        R = uproot.open(f"/data/zdc-autoresearch/reco/{args.row}/{args.dataset}/{fname.replace('.edm4hep', '.edm4eic')}")["events"].arrays(
            [f"{C}.energy", f"{C}.position.x", f"{C}.position.y", f"{C}.position.z", f"{C}.shapeParameters_begin", f"_{C}_shapeParameters",
             f"{A}.weight", f"_{A}_rec.index", f"_{A}_sim.index", f"{B}.energy", f"{B}.position.x", f"{B}.position.y", f"{B}.position.z",
             f"{BA}.weight", f"_{BA}_rec.index", f"_{BA}_sim.index"], library="ak")
        for ev in range(len(R)):
            l = per.get((fname, ev))
            if l is None:
                continue
            regime = "all-ZDC" if l["homes"][1:] == ["ZDC", "ZDC"] else "B0+ZDC"
            res[f"{regime}: Λ"] += 1
            res[f"{regime}: found by the row"] += bool(l[args.row]["matched"])
            E = ak.to_numpy(R[f"{C}.energy"][ev]).astype(float)
            P = e473.to_proton(*(ak.to_numpy(R[f"{C}.position.{q}"][ev]).astype(float) for q in "xyz"))
            sb = ak.to_numpy(R[f"{C}.shapeParameters_begin"][ev]); sp = ak.to_numpy(R[f"_{C}_shapeParameters"][ev])
            cand = [c for c in range(len(E)) if P[c][2] <= e473.ZMAX and all(math.sqrt(max(sp[sb[c] + q], 0)) <= e473.LMAX for q in (4, 5, 6))
                    and sum(math.sqrt(max(sp[sb[c] + q], 0)) > e473.WMAX for q in (4, 5, 6)) < 2]
            Eb_all = ak.to_numpy(R[f"{B}.energy"][ev]).astype(float)
            Pb_all = e473.to_proton(*(ak.to_numpy(R[f"{B}.position.{q}"][ev]).astype(float) for q in "xyz")) if len(Eb_all) else np.zeros((0, 3))
            keep = [k for k in np.argsort(-Eb_all) if Eb_all[k] >= 1.0][:4]
            Eb, Pb = Eb_all[keep], Pb_all[keep] if len(keep) else np.zeros((0, 3))
            lams, owner = r210.truth_event(a, ev); base = l["owner_base"]
            w = ak.to_numpy(R[f"{A}.weight"][ev]); rc = ak.to_numpy(R[f"_{A}_rec.index"][ev]); si = ak.to_numpy(R[f"_{A}_sim.index"][ev]).astype(int)
            own = owner[si] if len(si) else np.array([], dtype=int)
            wb = ak.to_numpy(R[f"{BA}.weight"][ev]); rb = ak.to_numpy(R[f"_{BA}_rec.index"][ev]); sb2 = ak.to_numpy(R[f"_{BA}_sim.index"][ev]).astype(int)
            ownb = owner[sb2] if len(sb2) else np.array([], dtype=int)
            pz = {r: {c for c in cand if w[(rc == c) & (own == base + r)].sum() >= 0.8} for r in (1, 2)}
            pb = {r: {j for j, k in enumerate(keep) if wb[(rb == k) & (ownb == base + r)].sum() >= 0.8} for r in (1, 2)}
            stock = e473.choose(E, P, cand, STOCK) if len(cand) >= 2 else None   # two tagged: the pair itself, as the C++ scores it
            for name, wpd in variants.items():
                mix = mixed_scores(E, P, cand, Eb, Pb, STOCK, wpd) if len(Eb) else []
                best_mix = min(mix) if mix else None
                if stock is not None and (best_mix is None or stock[3] <= best_mix[0]):
                    i, j, ml, _ = stock
                    good = regime == "all-ZDC" and ((i in pz[1] and j in pz[2]) or (i in pz[2] and j in pz[1])) and abs(ml - M_L) < 0.03
                elif best_mix is not None:
                    _, i, k, ml = best_mix
                    rz = 1 if l["homes"][1] == "ZDC" else 2; rb_ = 3 - rz
                    good = regime == "B0+ZDC" and i in pz[rz] and k in pb[rb_] and abs(ml - M_L) < 0.03
                    res[f"{regime}: {name} picks mixed"] += 1
                else:
                    good = False
                res[f"{regime}: {name} good"] += good
            if stock is not None:
                i, j, ml, _ = stock
                res[f"{regime}: stock ZDC pair good"] += regime == "all-ZDC" and ((i in pz[1] and j in pz[2]) or (i in pz[2] and j in pz[1])) and abs(ml - M_L) < 0.03
    path = repo_path("space", "perf", f"pairing-mixed-{args.row}-{args.dataset}.json")
    path.write_text(json.dumps({"row": args.row, "dataset": args.dataset, "files": len(files), "counts": dict(res)}, indent=1))
    for k in sorted(res):
        print(f"  {k:40s} {res[k]:5d}")
    print("wrote", path)


if __name__ == "__main__":
    main()
