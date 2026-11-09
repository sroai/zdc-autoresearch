#!/usr/bin/env python3
"""A "both photons outside the ZDC" hypothesis for the ZDC pairing, emulated offline on a row's MSF outputs (Phase 5
diagnostic, never a selector). It extends 474 (Y5's mixed hypothesis, as Y5 runs it) with one more hypothesis class:
two B0 photon candidates as the pair and every ZDC cluster as the neutron. If it wins, no ZDC cluster is written as a ZDC
photon and LambdaReconstruction pairs the two B0 photons with the ZDC neutron.

The emulated decision mirrors the C++: the ZDC pairing runs with more than two tagged ZDC clusters, or with external
photons and two tagged clusters; the new class also lets it run with one tagged cluster when two B0 candidates exist
(that cluster as a mixed photon against the B0 pair). B0 energies use the B0 photon law of the row (Y7: 1.0888·E^1.0058).
The B0 pair has no ZDC photon, so its photon-depth term is a constant offset (a ZDC pair carries about −16, a mixed
hypothesis three times one photon's depth): scanned.

Net: on the events whose pick switches to the B0 pair, the new good count minus the row's own found count (the row finds
γγ-in-B0 Λ through LambdaReconstruction whatever the ZDC pairing writes); the other events keep the row's result.

Grading (truth only grades): all-ZDC good = a ZDC pair pure for both photons with the Λ mass within ±30 MeV; γ B0 + γ ZDC
good = a mixed pick pure on both sides in the window; γγ in B0 good = a B0 pair pick, both clusters pure for the two
photons, in the window. "base" = the row's own decision (no B0-pair class); its good counts are compared with the row's
found counts (reproduction).

Usage: uv run scripts/475_msf_external_pair.py Y8_b0_profile_03 --dataset D6s_9x275 [--files N]
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

spec = importlib.util.spec_from_file_location("e474", repo_path("scripts", "474_msf_mixed_pairing.py"))
e474 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e474)
e473, r210 = e474.e473, e474.r210
M_PI0, M_L, M_N, Z_ZDC, STOCK = e473.M_PI0, e473.M_L, e473.M_N, e473.Z_ZDC, e473.STOCK
B, BA, C, A = e474.B, e474.BA, e474.C, e474.A
B0_LAW = (1.0888, 1.0058)
MIXED_PD = 3.0


def pair_scores(E, P, Eb, Pb, p, offset):
    """Every pair of B0 candidates with the whole ZDC as the neutron: list of (score, k, l, m_Λ)."""
    out = []
    raw = E.sum()
    if raw <= 0 or len(Eb) < 2:
        return out
    cen = (E[:, None] * P).sum(axis=0) / raw
    En = p["an"] * raw ** p["bn"]
    if En <= M_N:
        return out
    pn = math.sqrt(En * En - M_N * M_N)
    for k in range(len(Eb)):
        for l in range(k + 1, len(Eb)):
            E1, E2 = B0_LAW[0] * Eb[k] ** B0_LAW[1], B0_LAW[0] * Eb[l] ** B0_LAW[1]
            x1, x2 = Pb[k], Pb[l]
            pts = [(pn, cen), (E1, x1), (E2, x2)]
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
                u, w = x1 - v, x2 - v
                ang = math.acos(max(-1.0, min(1.0, float(u @ w / np.linalg.norm(u) / np.linalg.norm(w)))))
                if ang > th:
                    hi = z
                else:
                    lo = z
            v = slope(lo) * lo
            un = (cen - v) / np.linalg.norm(cen - v); u1 = (x1 - v) / np.linalg.norm(x1 - v); u2 = (x2 - v) / np.linalg.norm(x2 - v)
            pg = E1 * u1 + E2 * u2; pl = pg + pn * un
            mpi = math.sqrt(max((E1 + E2) ** 2 - float(pg @ pg), 0)); pL = float(np.linalg.norm(pl))
            ml = math.sqrt(max((En + E1 + E2) ** 2 - pL ** 2, 0))
            L = max(pL / M_L * p["ctau"], 1.0)
            depth = lo / L + math.log(L * max(1 - math.exp(-Z_ZDC / L), 1e-12))
            s = ((mpi - M_PI0) / (p["pi0_win"] * M_PI0)) ** 2 + ((ml - M_L) / p["sigma_l"]) ** 2 + p["w_depth"] * depth + p["w_pd"] * offset
            out.append((s, k, l, ml))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("row")
    ap.add_argument("--dataset", default="D6s_9x275")
    ap.add_argument("--files", type=int, default=40)
    ap.add_argument("--mixed-pd", type=float, nargs="*", help="also scan the mixed photon-depth factor (with --offsets)")
    ap.add_argument("--offsets", type=float, nargs="*", help="B0-pair offsets to scan (default −24 … −48)")
    args = ap.parse_args()
    J = json.loads(repo_path("space", "perf", f"msf-regimes-{args.row}-{args.dataset}.json").read_text())
    per = {}
    for l in J["per_lambda"]:
        h = l["homes"]
        if h[0] == "ZDC" and sorted(h[1:]) in (["ZDC", "ZDC"], ["B0", "ZDC"], ["B0", "B0"]):
            per[(l["file"], l["event"])] = l
    offsets = [None] + (args.offsets or [-24.0, -28.0, -32.0, -36.0, -40.0, -48.0])   # None: the row's own decision (no B0-pair class)
    mpds = args.mixed_pd or [MIXED_PD]
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
            h = sorted(l["homes"][1:])
            regime = {("ZDC", "ZDC"): "all-ZDC", ("B0", "ZDC"): "B0+ZDC", ("B0", "B0"): "B0+B0"}[tuple(h)]
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
            Eb, Pb = Eb_all[keep], (Pb_all[keep] if len(keep) else np.zeros((0, 3)))
            lams, owner = r210.truth_event(a, ev); base = l["owner_base"]
            w = ak.to_numpy(R[f"{A}.weight"][ev]); rc = ak.to_numpy(R[f"_{A}_rec.index"][ev]); si = ak.to_numpy(R[f"_{A}_sim.index"][ev]).astype(int)
            own = owner[si] if len(si) else np.array([], dtype=int)
            wb = ak.to_numpy(R[f"{BA}.weight"][ev]); rb = ak.to_numpy(R[f"_{BA}_rec.index"][ev]); sb2 = ak.to_numpy(R[f"_{BA}_sim.index"][ev]).astype(int)
            ownb = owner[sb2] if len(sb2) else np.array([], dtype=int)
            pz = {r: {c for c in cand if w[(rc == c) & (own == base + r)].sum() >= 0.8} for r in (1, 2)}
            pb = {r: {j for j, k in enumerate(keep) if wb[(rb == k) & (ownb == base + r)].sum() >= 0.8} for r in (1, 2)}
            # the row's own hypotheses (Y5): ZDC pairs when ≥ 2 tagged, mixed when B0 candidates exist; the chooser runs
            # with > 2 tagged, or with external photons and 2 tagged
            zpair = e473.choose(E, P, cand, STOCK) if len(cand) >= 2 else None
            mixes = {m: (e474.mixed_scores(E, P, cand, Eb, Pb, STOCK, m, B0_LAW) if len(Eb) else []) for m in mpds}
            pairs_cache = {}
            for mpd, off in [(m, o) for m in mpds for o in offsets]:
                mix = mixes[mpd]
                hyps = []
                runs = len(cand) > 2 or (len(Eb) > 0 and len(cand) == 2) or (off is not None and len(Eb) >= 2 and len(cand) == 1)
                if runs:
                    if zpair is not None:
                        hyps.append((zpair[3], "zpair", zpair))
                    hyps += [(m[0], "mixed", m) for m in mix]
                    if off is not None:
                        if off not in pairs_cache:
                            pairs_cache[off] = pair_scores(E, P, Eb, Pb, STOCK, off)
                        hyps += [(q[0], "b0pair", q) for q in pairs_cache[off]]
                name = ("base" if off is None else f"b0pair offset {off:+.0f}") + (f" mixed×{mpd:g}" if args.mixed_pd else "")
                if not hyps:
                    # no chooser: every tagged cluster stays a photon (one tagged cluster = a mixed photon for LambdaReconstruction)
                    kind = "mixed" if len(cand) == 1 else ("zpair" if len(cand) == 2 else None)
                    if kind == "zpair":
                        i, j = cand; ml = e473.choose(E, P, cand, STOCK)
                        pick = ("zpair", (i, j, ml[2] if ml else 0.0))
                    elif kind == "mixed" and mix:
                        best = min((m for m in mix if m[1] == cand[0]), default=None)
                        pick = ("mixed", best[1:]) if best else (None, None)
                    else:
                        pick = (None, None)
                else:
                    s, kind, val = min(hyps, key=lambda t: t[0])
                    pick = (kind, val[1:] if kind != "zpair" else val)
                kind, val = pick
                good = False
                if kind == "zpair" and regime == "all-ZDC":
                    i, j, ml = val[0], val[1], val[2]
                    good = ((i in pz[1] and j in pz[2]) or (i in pz[2] and j in pz[1])) and abs(ml - M_L) < 0.03
                elif kind == "mixed" and regime == "B0+ZDC":
                    i, k, ml = val
                    rz = 1 if l["homes"][1] == "ZDC" else 2
                    good = i in pz[rz] and k in pb[3 - rz] and abs(ml - M_L) < 0.03
                elif kind == "b0pair" and regime == "B0+B0":
                    k, l2, ml = val
                    good = ((k in pb[1] and l2 in pb[2]) or (k in pb[2] and l2 in pb[1])) and abs(ml - M_L) < 0.03
                res[f"{regime}: {name} good"] += good
                if kind == "b0pair":
                    res[f"{regime}: {name} picks b0pair"] += 1
                    # net change on a switched event: the row found it (any route) → now good or not
                    res[f"{regime}: {name} net"] += int(good) - int(bool(l[args.row]["matched"]))
    path = repo_path("space", "perf", f"pairing-b0pair-{args.row}-{args.dataset}.json")
    path.write_text(json.dumps({"row": args.row, "dataset": args.dataset, "files": len(files), "b0_law": B0_LAW, "counts": dict(res)}, indent=1))
    for k in sorted(res):
        print(f"  {k:44s} {res[k]:5d}")
    print("wrote", path)


if __name__ == "__main__":
    main()
