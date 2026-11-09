#!/usr/bin/env python3
"""The scope of a crystal-seeded ZDC photon finder, emulated offline on a row's MSF outputs (Phase 6 Step 0 item 1,
loop v6; a diagnostic, never a selector).

The LYSO crystal section (EcalFarForwardZDC: 20 × 20 crystals, 30.3 mm pitch, 70 mm deep) sits in front of the Hcal.
EICrecon makes one crystal cluster per event (island clustering with a 50 cm neighbourhood) and the neutrals factory does
not read it. This script asks what a crystal-scale clustering would give the Λ → nπ⁰ pairing:

1. Re-clustering. The crystal rec hits (the row's EcalFarForwardZDCRecHits, clipped at 2 GeV per crystal) form islands of
   8-connected crystals above HIT_MIN; an island splits at its local maxima (a crystal ≥ PEAK_MIN and above its 8
   neighbours); each crystal's energy is shared among its island's peaks in proportion to E_peak · exp(−d / R_SHARE);
   the position is the log-weighted centroid (w0 = 4). A cluster's purity for a true particle is that particle's share of
   the cluster's simulated deposit (EcalFarForwardZDCHits contributions, matched by cellID, weighted by the shares).
2. Inventory. Per true photon of the all-ZDC and γ B0 + γ ZDC regimes (210's homes) that has no matched photon neutral
   in the row: the crystal cluster holding most of its deposit, that cluster's purity and rec energy, and the Hcal
   rec-hit energy in a column of radius R_COL behind it (projective from the IP).
3. Emulation. The row's decision as 475 emulates Y9 (ZDC pairs [473], mixed ZDC + B0 pairs [474], B0 pairs at the
   offset −30) plus crystal-seeded photon hypotheses: a crystal cluster ≥ CRYS_MIN with no tagged Hcal cluster within
   R_VETO behind it is a photon at the crystal-cluster position, energy law(E_crystal, E_column); its column energy
   leaves the neutron sum. Crystal hypotheses: crystal + tagged Hcal photon, crystal + crystal, crystal + B0 photon. A
   crystal photon's photon-depth term is the constant `crys_pd` (an Hcal photon carries (z − z_ZDC) / 100), scanned.
   Grading (truth only grades): a pick is good when both photons are pure (≥ 0.8) for the two distinct true photons and
   the emulated Λ mass is within ±30 MeV. Net = good − found by the row, on the events whose pick switches to a crystal
   hypothesis; the other events keep the row's result.

The photon law comes from the gun fit (`--law`, written by `--fit-guns`, F4: never fitted on D6); without it the script
reports the inventory only.

Usage:
  uv run scripts/477_crystal_scope.py --fit-guns CAL6_D2_Y9                      # the law, from D2 + D2c
  uv run scripts/477_crystal_scope.py MSF6_Y9 --dataset D6s_9x275 [--files N] --law space/perf/calib-crystal-CAL6_D2_Y9.json
"""
import argparse
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import repo_path  # noqa: E402

spec = importlib.util.spec_from_file_location("e475", repo_path("scripts", "475_msf_external_pair.py"))
e475 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e475)
e474, e473, r210 = e475.e474, e475.e473, e475.r210
M_PI0, M_L, M_N, Z_ZDC, STOCK = e473.M_PI0, e473.M_L, e473.M_N, e473.Z_ZDC, e473.STOCK
B, BA, C, A = e474.B, e474.BA, e474.C, e474.A
EH, HH = "EcalFarForwardZDCRecHits", "HcalFarForwardZDCRecHits"
SIM = "EcalFarForwardZDCHits"
B0_OFFSET, MIXED_PD = -30.0, e475.MIXED_PD     # Y9's launched values

PITCH, X0_GRID = 30.3, -287.85                 # crystal pitch and the first column's centre (proton frame, mm)
HIT_MIN, PEAK_MIN, R_SHARE = 0.005, 0.10, 20.0  # GeV, GeV, mm (LYSO Molière radius ≈ 20.7 mm)
CRYS_MIN, R_VETO = 0.5, 60.0                   # GeV, mm
R_COL, Z_HCAL = 45.0, 35800.0                  # column radius (mm); the Hcal front face (mm, proton frame ≈ lab z)


# --- crystal re-clustering -------------------------------------------------------------------------------------------

def recluster(e, x, y):
    """Crystal-scale island clustering with splitting at local maxima. e, x, y: one event's crystal rec hits (proton
    frame). Returns a list of clusters {E, x, y, hits, shares}."""
    ix = np.rint((x - X0_GRID) / PITCH).astype(int); iy = np.rint((y - X0_GRID) / PITCH).astype(int)
    cell = {(ix[h], iy[h]): h for h in range(len(e)) if e[h] >= HIT_MIN}

    def neighbours(h):
        return [cell[(ix[h] + a, iy[h] + b)] for a in (-1, 0, 1) for b in (-1, 0, 1)
                if (a or b) and (ix[h] + a, iy[h] + b) in cell]
    seen, clusters = set(), []
    for h0 in cell.values():
        if h0 in seen:
            continue
        island, stack = [], [h0]
        seen.add(h0)
        while stack:
            h = stack.pop(); island.append(h)
            for q in neighbours(h):
                if q not in seen:
                    seen.add(q); stack.append(q)
        peaks = [h for h in island if e[h] >= PEAK_MIN and all(e[h] > e[q] or (e[h] == e[q] and h < q) for q in neighbours(h))]
        if not peaks:
            peaks = [max(island, key=lambda h: e[h])]
        hits = np.array(island)
        d = np.hypot(x[hits][:, None] - x[peaks][None, :], y[hits][:, None] - y[peaks][None, :])
        w = e[peaks][None, :] * np.exp(-d / R_SHARE)
        w /= w.sum(axis=1, keepdims=True)
        for k in range(len(peaks)):
            share = w[:, k]
            ek = share * e[hits]
            Ek = ek.sum()
            if Ek <= 0:
                continue
            lw = np.maximum(0.0, 4.0 + np.log(np.maximum(ek, 1e-12) / Ek))
            if lw.sum() <= 0:
                lw = ek
            clusters.append({"E": float(Ek), "x": float((lw * x[hits]).sum() / lw.sum()), "y": float((lw * y[hits]).sum() / lw.sum()),
                             "hits": hits, "shares": share})
    return clusters


def cell_truth(sa, ev, owner):
    """Simulated crystal deposit per cellID: {cellID: (total, {owner: energy})}."""
    cid = ak.to_numpy(sa[f"{SIM}.cellID"][ev]); cb = ak.to_numpy(sa[f"{SIM}.contributions_begin"][ev])
    ce = ak.to_numpy(sa[f"{SIM}.contributions_end"][ev]); ci = ak.to_numpy(sa[f"_{SIM}_contributions.index"][ev])
    ce_e = ak.to_numpy(sa[f"{SIM}Contributions.energy"][ev]); cp = ak.to_numpy(sa[f"_{SIM}Contributions_particle.index"][ev])
    out = {}
    for h in range(len(cid)):
        idx = ci[cb[h]:ce[h]]
        own = defaultdict(float)
        for q in idx:
            o = owner[cp[q]] if cp[q] < len(owner) else -1
            if o >= 0:
                own[int(o)] += float(ce_e[q])
        out[int(cid[h])] = (float(ce_e[idx].sum()), own)
    return out


def cluster_purity(cl, cellid, truth, o):
    tot = num = 0.0
    for h, s in zip(cl["hits"], cl["shares"]):
        t = truth.get(int(cellid[h]))
        if t is None:
            continue
        tot += s * t[0]; num += s * t[1].get(o, 0.0)
    return num / tot if tot > 0 else 0.0


def column_energy(cl, he, hp, r_col=None):
    """Hcal rec-hit energy within r_col of the projective line from the IP through the crystal cluster."""
    r_col = R_COL if r_col is None else r_col
    if not len(he):
        return 0.0
    s = hp[:, 2] / Z_CRYS
    return float(he[np.hypot(hp[:, 0] - cl["x"] * s, hp[:, 1] - cl["y"] * s) <= r_col].sum())


Z_CRYS = 35737.0   # crystal rec-hit depth, proton frame (mm)


# --- hypothesis scoring (473 for ZDC pairs, 474 / 475 for pairs with a B0 photon) -------------------------------------

def score_zdc_pair(g1, g2, En, cen, pd_sum, p):
    """473's ZDC-pair score for two photons g = (E, position) and a neutron (En, centroid); pd_sum: Σ photon-depth terms."""
    E1, x1 = g1; E2, x2 = g2
    if En <= M_N or E1 <= 0 or E2 <= 0:
        return math.inf, 0.0
    pn = math.sqrt(En * En - M_N * M_N)
    wz = pn * cen[2] + E1 * x1[2] + E2 * x2[2]
    tx = (pn * cen[0] + E1 * x1[0] + E2 * x2[0]) / wz; ty = (pn * cen[1] + E1 * x1[1] + E2 * x2[1]) / wz
    th = 2 * math.asin(min(1.0, M_PI0 / (2 * math.sqrt(E1 * E2))))
    lo, hi = 0.0, Z_ZDC
    for _ in range(p["iters"]):
        z = 0.5 * (lo + hi); v = np.array([tx * z, ty * z, z])
        u, w = x1 - v, x2 - v
        ang = math.acos(max(-1.0, min(1.0, float(u @ w / np.linalg.norm(u) / np.linalg.norm(w)))))
        hi, lo = (z, lo) if ang > th else (hi, z)
    v = np.array([tx * lo, ty * lo, lo])
    un = (cen - v) / np.linalg.norm(cen - v); u1 = (x1 - v) / np.linalg.norm(x1 - v); u2 = (x2 - v) / np.linalg.norm(x2 - v)
    pg = E1 * u1 + E2 * u2; pl = pg + pn * un
    mpi = math.sqrt(max((E1 + E2) ** 2 - float(pg @ pg), 0)); pL = float(np.linalg.norm(pl))
    ml = math.sqrt(max((En + E1 + E2) ** 2 - pL ** 2, 0))
    L = max(pL / M_L * p["ctau"], 1.0)
    depth = lo / L + math.log(L * max(1 - math.exp(-Z_ZDC / L), 1e-12))
    s = ((mpi - M_PI0) / (p["pi0_win"] * M_PI0)) ** 2 + ((ml - M_L) / p["sigma_l"]) ** 2 + p["w_depth"] * depth + p["w_pd"] * pd_sum
    return s, ml


def score_mixed(gz, gb, En, cen, pd_term, p):
    """474's mixed score (lever-arm slope) for a ZDC-side photon gz and a B0 photon gb (energies already calibrated)."""
    E1, x1 = gz; E2, x2 = gb
    if En <= M_N or E1 <= 0 or E2 <= 0:
        return math.inf, 0.0
    pn = math.sqrt(En * En - M_N * M_N)
    pts = [(pn, cen), (E1, x1), (E2, x2)]
    zf = 0.999 * min(q[2] for _, q in pts)
    if zf <= 0:
        return math.inf, 0.0

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
        hi, lo = (z, lo) if ang > th else (hi, z)
    v = slope(lo) * lo
    un = (cen - v) / np.linalg.norm(cen - v); u1 = (x1 - v) / np.linalg.norm(x1 - v); u2 = (x2 - v) / np.linalg.norm(x2 - v)
    pg = E1 * u1 + E2 * u2; pl = pg + pn * un
    mpi = math.sqrt(max((E1 + E2) ** 2 - float(pg @ pg), 0)); pL = float(np.linalg.norm(pl))
    ml = math.sqrt(max((En + E1 + E2) ** 2 - pL ** 2, 0))
    L = max(pL / M_L * p["ctau"], 1.0)
    depth = lo / L + math.log(L * max(1 - math.exp(-Z_ZDC / L), 1e-12))
    s = ((mpi - M_PI0) / (p["pi0_win"] * M_PI0)) ** 2 + ((ml - M_L) / p["sigma_l"]) ** 2 + p["w_depth"] * depth + p["w_pd"] * pd_term
    return s, ml


def crystal_law(law, e_crys, e_col):
    """The crystal photon energy; at least the crystal energy (the hits clip at 2 GeV, so it is a lower bound)."""
    return max(e_crys, law["a"] * e_crys + law["b"] * e_col + law.get("c", 0.0))


# --- per-event inputs --------------------------------------------------------------------------------------------------

def tagged_candidates(E, P, sb, sp):
    return [c for c in range(len(E)) if P[c][2] <= e473.ZMAX and all(math.sqrt(max(sp[sb[c] + q], 0)) <= e473.LMAX for q in (4, 5, 6))
            and sum(math.sqrt(max(sp[sb[c] + q], 0)) > e473.WMAX for q in (4, 5, 6)) < 2]


def reco_branches():
    return ([f"{C}.energy", f"{C}.position.x", f"{C}.position.y", f"{C}.position.z", f"{C}.shapeParameters_begin", f"_{C}_shapeParameters",
             f"{A}.weight", f"_{A}_rec.index", f"_{A}_sim.index", f"{B}.energy", f"{B}.position.x", f"{B}.position.y", f"{B}.position.z",
             f"{BA}.weight", f"_{BA}_rec.index", f"_{BA}_sim.index"]
            + [f"{EH}.{q}" for q in ("energy", "cellID", "position.x", "position.y", "position.z")]
            + [f"{HH}.{q}" for q in ("energy", "position.x", "position.y", "position.z")] + ["ReconstructedLambdas.mass"])


def sim_branches():
    return [f"{SIM}.cellID", f"{SIM}.contributions_begin", f"{SIM}.contributions_end", f"_{SIM}_contributions.index",
            f"{SIM}Contributions.energy", f"_{SIM}Contributions_particle.index"]


def np_(arr, key, ev):
    return ak.to_numpy(arr[key][ev])


# --- the gun fit (F4) ---------------------------------------------------------------------------------------------------

def fit_guns(row, e_max=50.0, tag=""):
    """Per gun photon whose leading re-clustered crystal cluster holds ≥ 0.5 GeV: E_true against (E_crystal, E_column)
    with a linear least-squares fit E = a·E_crys + b·E_col + c, weighted 1 / E_true (relative residuals)."""
    rows = []
    for ds in ("D2c_photon_low", "D2_photon"):
        for f in sorted((Path("/data/zdc-autoresearch/reco") / row / ds).glob("*.edm4eic.root")):
            R = uproot.open(f)["events"].arrays([f"{EH}.{q}" for q in ("energy", "position.x", "position.y", "position.z")]
                                                + [f"{HH}.{q}" for q in ("energy", "position.x", "position.y", "position.z")], library="ak")
            S = uproot.open(Path("/data/zdc-autoresearch/datasets") / ds / f.name.replace(".edm4eic", ".edm4hep"))["events"].arrays(
                ["MCParticles.PDG", "MCParticles.generatorStatus", "MCParticles.momentum.x", "MCParticles.momentum.y", "MCParticles.momentum.z"], library="ak")
            for ev in range(len(R)):
                st = np_(S, "MCParticles.generatorStatus", ev); pdg = np_(S, "MCParticles.PDG", ev)
                g = np.flatnonzero((st == 1) & (pdg == 22))
                if len(g) != 1:
                    continue
                k = g[0]
                etrue = float(np.sqrt(sum(np_(S, f"MCParticles.momentum.{q}", ev)[k] ** 2 for q in "xyz")))
                ce = np_(R, f"{EH}.energy", ev)
                if not len(ce):
                    continue
                cp = e473.to_proton(*(np_(R, f"{EH}.position.{q}", ev).astype(float) for q in "xyz"))
                cls = recluster(ce.astype(float), cp[:, 0], cp[:, 1])
                if not cls:
                    continue
                cl = max(cls, key=lambda c: c["E"])
                if cl["E"] < CRYS_MIN:
                    continue
                he = np_(R, f"{HH}.energy", ev).astype(float)
                hp = e473.to_proton(*(np_(R, f"{HH}.position.{q}", ev).astype(float) for q in "xyz")) if len(he) else np.zeros((0, 3))
                rows.append((etrue, cl["E"], column_energy(cl, he, hp), len(cls)))
    a_all = np.array(rows)
    a = a_all[a_all[:, 0] <= e_max * 1.001]     # the MSF window photons carry 5–50 GeV
    X = np.stack([a[:, 1], a[:, 2], np.ones(len(a))], axis=1); w = 1.0 / a[:, 0]
    coef, *_ = np.linalg.lstsq(X * w[:, None], a[:, 0] * w, rcond=None)
    law = {"form": "E = a·E_crys + b·E_col + c", "a": float(coef[0]), "b": float(coef[1]), "c": float(coef[2]),
           "r_col_mm": R_COL, "crys_min_gev": CRYS_MIN, "n": len(a), "fit_max_gev": e_max}
    per_e = {}
    a = a_all
    pred = np.stack([a[:, 1], a[:, 2], np.ones(len(a))], axis=1) @ coef
    for e in sorted(set(np.round(a[:, 0]).astype(int))):
        s = np.abs(np.round(a[:, 0]) - e) < 0.5
        r = pred[s] / a[s, 0]
        per_e[str(e)] = {"n": int(s.sum()), "ratio_median": float(np.median(r)), "ratio_sigma68": float(0.5 * (np.percentile(r, 84) - np.percentile(r, 16))),
                         "crys_median": float(np.median(a[s, 1])), "col_median": float(np.median(a[s, 2])), "clusters_median": float(np.median(a[s, 3]))}
    law["per_energy"] = per_e
    path = repo_path("space", "perf", f"calib-crystal-{row}{tag}.json")
    path.write_text(json.dumps(law, indent=1))
    print(f"law on {len(a)} gun photons: E = {coef[0]:.3f}·E_crys + {coef[1]:.3f}·E_col + {coef[2]:.3f}")
    for e, v in per_e.items():
        print(f"  {e:>4s} GeV: n {v['n']:4d}  pred/true {v['ratio_median']:.3f} ± {v['ratio_sigma68']:.3f}  E_crys {v['crys_median']:.2f}  E_col {v['col_median']:.2f}  clusters {v['clusters_median']:.0f}")
    print("wrote", path)


# --- the scope study ------------------------------------------------------------------------------------------------------

def main():
    global CRYS_MIN, R_VETO, R_COL, PEAK_MIN, R_SHARE
    ap = argparse.ArgumentParser()
    ap.add_argument("row", nargs="?")
    ap.add_argument("--dataset", default="D6s_9x275")
    ap.add_argument("--files", type=int, default=40)
    ap.add_argument("--json-row", help="the row whose 210 per-Λ record grades (default: the row)")
    ap.add_argument("--law", help="the crystal photon law (JSON from --fit-guns); without it: inventory only")
    ap.add_argument("--crys-pd", type=float, nargs="*", default=[-10.0, -5.0, 0.0, 5.0], help="crystal photon-depth terms to scan")
    ap.add_argument("--peak-min", type=float, help=f"crystal clustering: local-maximum threshold, GeV (default {PEAK_MIN})")
    ap.add_argument("--r-share", type=float, help=f"crystal clustering: sharing profile scale, mm (default {R_SHARE})")
    ap.add_argument("--crys-min", type=float, help=f"crystal candidate threshold, GeV (default {CRYS_MIN})")
    ap.add_argument("--r-veto", type=float, help=f"veto radius, mm (default {R_VETO})")
    ap.add_argument("--r-col", type=float, help=f"Hcal column radius, mm (default {R_COL}; the law was fitted at 45)")
    ap.add_argument("--col-scale", type=float, default=1.0, help="the column leaves the neutron × this (1: rec-hit scale, as Z1; "
                    "1 / 0.0273 = 36.6: the Hcal clusters' scale)")
    ap.add_argument("--tag", default="", help="suffix of the output JSON")
    ap.add_argument("--full", action="store_true", help="also run the crystal decision with every Λ re-graded (for chooser-weight scans)")
    ap.add_argument("--sigma-l", type=float, help="chooser Λ-mass width for --full (launched 0.04 GeV)")
    ap.add_argument("--pi0-win", type=float, help="chooser π⁰-mass window, relative, for --full / --alt (launched 0.1)")
    ap.add_argument("--w-depth", type=float, help="chooser decay-depth weight for --full (launched 1.5)")
    ap.add_argument("--why", action="store_true", help="with --alt: why the all-ZDC Λ with a pure crystal cluster are missed "
                    "(under the first --iso setting when given)")
    ap.add_argument("--why-all", action="store_true", help="with --alt: what the chooser picks for every missed all-ZDC Λ whose "
                    "photons both have a pure candidate (under the first --iso setting when given)")
    ap.add_argument("--no-crystal-alt", action="store_true", help="with --alt: drop the crystal law's energy as an option for "
                    "tagged Hcal photons (Z5), keeping --axis-law's")
    ap.add_argument("--axis-law", type=float, help="with --alt: tagged Hcal photons also offer the axis law's energy at this "
                    "radius (mm; calib-hcal-axis-CAL6_D2_Y9.json, form ch, written by 481)")
    ap.add_argument("--alt-col-out", action="store_true", help="with --alt: a crystal-law Hcal photon's column beyond its own cluster leaves the neutron")
    ap.add_argument("--iso", nargs="*", default=[], type=lambda v: tuple(float(q) for q in v.split(":")),
                    help="with --alt / --full: isolation terms W:L (mm) to scan, w·exp(−d_lead / l) per Hcal photon")
    ap.add_argument("--front", nargs="*", default=[], type=lambda v: tuple(float(q) for q in v.split(":")),
                    help="with --alt: crystal-front terms W:E0 (GeV) to scan on top of the first --iso setting, w·exp(−E_front30 / e0) "
                    "per tagged Hcal photon")
    ap.add_argument("--iso-crys", action="store_true", help="--iso also on crystal photons (their projected position)")
    ap.add_argument("--alt", action="store_true", help="as --full, with a tagged Hcal photon's crystal-law energy as a competing hypothesis")
    ap.add_argument("--z3", action="store_true", help="also emulate Z3: tagged Hcal photons with a crystal cluster in front take the crystal law's energy")
    ap.add_argument("--veto", nargs="*", default=["single", "split"], choices=["single", "split"], help="crystal veto variants to scan")
    ap.add_argument("--purity", action="store_true", help="also run the decision on every other event: crystal picks in the window there (no target Λ) estimate the change of N_window")
    ap.add_argument("--fit-guns", metavar="ROW", help="fit the crystal photon law on the row's D2 + D2c outputs and stop")
    ap.add_argument("--fit-max-gev", type=float, default=50.0, help="fit on gun photons up to this energy (MSF window photons: 5–50 GeV)")
    args = ap.parse_args()
    CRYS_MIN = args.crys_min if args.crys_min is not None else CRYS_MIN
    R_VETO = args.r_veto if args.r_veto is not None else R_VETO
    R_COL = args.r_col if args.r_col is not None else R_COL
    PEAK_MIN = args.peak_min if args.peak_min is not None else PEAK_MIN
    R_SHARE = args.r_share if args.r_share is not None else R_SHARE
    if args.fit_guns:
        fit_guns(args.fit_guns, args.fit_max_gev, args.tag)
        return
    jrow = args.json_row or args.row
    J = json.loads(repo_path("space", "perf", f"msf-regimes-{jrow}-{args.dataset}.json").read_text())
    per = {}
    for l in J["per_lambda"]:
        h = l["homes"]
        if h[0] == "ZDC" and sorted(h[1:]) in (["ZDC", "ZDC"], ["B0", "ZDC"], ["B0", "B0"]):
            per[(l["file"], l["event"])] = l
    law = json.loads(Path(args.law).read_text()) if args.law else None
    axis = None
    if args.axis_law:
        aj = json.loads(repo_path("space", "perf", "calib-hcal-axis-CAL6_D2_Y9.json").read_text())[f"{args.axis_law:g}-ch"]["coef"]
        axis = {"r": args.axis_law, "a": aj[0], "b": aj[1], "c": aj[2]}
    inv = Counter(); inv_e = defaultdict(list); res = Counter(); e_ratio = defaultdict(list); why_dm = []; why_e = defaultdict(list)
    files = sorted({k[0] for k in per})[: args.files]
    for fname in files:
        sim = uproot.open(f"/data/zdc-autoresearch/datasets/{args.dataset}/{fname}")["events"]
        a = r210.mc_arrays(sim); sa = sim.arrays(sim_branches(), library="ak")
        R = uproot.open(f"/data/zdc-autoresearch/reco/{args.row}/{args.dataset}/{fname.replace('.edm4hep', '.edm4eic')}")["events"].arrays(reco_branches(), library="ak")
        for ev in range(len(R)):
            l = per.get((fname, ev))
            lm = np_(R, "ReconstructedLambdas.mass", ev)
            row_in_window = bool(len(lm) and (np.abs(lm - M_L) < 0.03).any())
            if l is None:
                if not (args.purity and law):
                    continue
                # an event without a target Λ in the three regimes: only the decision is run (no truth grading)
                regime, found = "other", False
                l = {"homes": ["none", "none", "none"], "owner_base": -100, jrow: {"photon_groups": [None, None]}}
                res["other: events"] += 1; res["other: row in window"] += row_in_window
            else:
                regime = {("ZDC", "ZDC"): "all-ZDC", ("B0", "ZDC"): "B0+ZDC", ("B0", "B0"): "B0+B0"}[tuple(sorted(l["homes"][1:]))]
                found = bool(l[jrow]["matched"])
                res[f"{regime}: Λ"] += 1; res[f"{regime}: found by the row"] += found
            lams, owner = r210.truth_event(a, ev); base = l["owner_base"]
            # Hcal clusters, B0 candidates, purities (as 475)
            E = np_(R, f"{C}.energy", ev).astype(float)
            P = e473.to_proton(*(np_(R, f"{C}.position.{q}", ev).astype(float) for q in "xyz"))
            cand = tagged_candidates(E, P, np_(R, f"{C}.shapeParameters_begin", ev), np_(R, f"_{C}_shapeParameters", ev))
            Eb_all = np_(R, f"{B}.energy", ev).astype(float)
            Pb_all = e473.to_proton(*(np_(R, f"{B}.position.{q}", ev).astype(float) for q in "xyz")) if len(Eb_all) else np.zeros((0, 3))
            keep = [k for k in np.argsort(-Eb_all) if Eb_all[k] >= 1.0][:4]
            Eb, Pb = Eb_all[keep], (Pb_all[keep] if len(keep) else np.zeros((0, 3)))
            w = np_(R, f"{A}.weight", ev); rc = np_(R, f"_{A}_rec.index", ev); si = np_(R, f"_{A}_sim.index", ev).astype(int)
            own = owner[si] if len(si) else np.array([], dtype=int)
            wb = np_(R, f"{BA}.weight", ev); rb = np_(R, f"_{BA}_rec.index", ev); sb2 = np_(R, f"_{BA}_sim.index", ev).astype(int)
            ownb = owner[sb2] if len(sb2) else np.array([], dtype=int)
            pz = {r: {c for c in cand if w[(rc == c) & (own == base + r)].sum() >= 0.8} for r in (1, 2)}
            pb = {r: {j for j, k in enumerate(keep) if wb[(rb == k) & (ownb == base + r)].sum() >= 0.8} for r in (1, 2)}
            # crystal clusters at the crystal scale, their truth, their Hcal columns
            ce = np_(R, f"{EH}.energy", ev).astype(float); cid = np_(R, f"{EH}.cellID", ev)
            cp = e473.to_proton(*(np_(R, f"{EH}.position.{q}", ev).astype(float) for q in "xyz")) if len(ce) else np.zeros((0, 3))
            cls = recluster(ce, cp[:, 0], cp[:, 1]) if len(ce) else []
            truth = cell_truth(sa, ev, owner)
            he = np_(R, f"{HH}.energy", ev).astype(float)
            hp = e473.to_proton(*(np_(R, f"{HH}.position.{q}", ev).astype(float) for q in "xyz")) if len(he) else np.zeros((0, 3))
            for cl in cls:
                cl["pur"] = {r: cluster_purity(cl, cid, truth, base + r) for r in (1, 2)}
                cl["col"] = column_energy(cl, he, hp)
            # inventory: ZDC-home photons without a matched photon neutral in the row
            for r in (1, 2):
                if l["homes"][r] != "ZDC":
                    continue
                miss = l[jrow]["photon_groups"][r - 1] is None
                tag = "missing" if miss else "found"
                inv[f"{regime} ZDC photons {tag}"] += 1
                best = max(cls, key=lambda c: c["pur"][r] * c["E"], default=None)
                if best is not None and best["pur"][r] >= 0.8 and best["E"] >= CRYS_MIN:
                    inv[f"{regime} ZDC photons {tag}: pure crystal cluster ≥ {CRYS_MIN} GeV"] += 1
                    if miss:
                        etrue = l["E"][r]
                        inv_e[f"{regime} missing: E_crys / E_true"].append(best["E"] / etrue)
                        inv_e[f"{regime} missing: E_col (GeV, Hcal rec)"].append(best["col"])
                        inv_e[f"{regime} missing: E_true (GeV)"].append(etrue)
            # crystal photon candidates: no tagged Hcal cluster within R_VETO behind
            # behind[k]: the tagged Hcal clusters within R_VETO behind crystal cluster k. Veto "single": a crystal cluster with
            # a tagged cluster behind it is that photon already. Veto "split": it stays a candidate when two or more crystal
            # clusters sit in front of the same tagged cluster (two photons sharing one Hcal cluster).
            xc_all = []
            for k, cl in enumerate(cls):
                if cl["E"] < CRYS_MIN:
                    continue
                behind = [c for c in cand if math.hypot(P[c][0] * Z_CRYS / P[c][2] - cl["x"], P[c][1] * Z_CRYS / P[c][2] - cl["y"]) <= R_VETO]
                xc_all.append({"k": k, "E": crystal_law(law, cl["E"], cl["col"]) if law else 0.0, "x": np.array([cl["x"], cl["y"], Z_CRYS]),
                               "col": cl["col"], "pur": cl["pur"], "behind": behind})
            front = Counter(c for x in xc_all for c in x["behind"])
            xcs = {"single": [x for x in xc_all if not x["behind"]],
                   "split": [x for x in xc_all if not x["behind"] or any(front[c] >= 2 for c in x["behind"])]}
            xc = xcs["single"]
            # oracle: a Λ the row misses whose two photons each have a pure photon candidate (tagged Hcal, crystal or B0)
            if not found and regime != "other":
                avail = []
                for r in (1, 2):
                    avail.append(("hcal" if pz[r] else "") + ("crys" if any(c["pur"][r] >= 0.8 for c in xcs["split"]) else "") + ("b0" if pb[r] else ""))
                if all(avail):
                    res[f"{regime}: missed, both photons have a candidate (oracle)"] += 1
                    if any("crys" in v and "hcal" not in v and "b0" not in v for v in avail):
                        res[f"{regime}: missed, oracle needs a crystal candidate"] += 1
            # the row's decision (475's base with the B0 pair at Y9's offset)
            zpair = e473.choose(E, P, cand, STOCK) if len(cand) >= 2 else None
            mix = e474.mixed_scores(E, P, cand, Eb, Pb, STOCK, MIXED_PD, e475.B0_LAW) if len(Eb) else []
            bpair = e475.pair_scores(E, P, Eb, Pb, STOCK, B0_OFFSET) if len(Eb) >= 2 else []
            runs = len(cand) > 2 or (len(Eb) > 0 and len(cand) == 2) or (len(Eb) >= 2 and len(cand) == 1)
            row_hyps = []
            if runs:
                if zpair is not None:
                    row_hyps.append((zpair[3], "zpair", (zpair[0], zpair[1], zpair[2])))
                row_hyps += [(m[0], "mixed", m[1:]) for m in mix]
                row_hyps += [(q[0], "b0pair", q[1:]) for q in bpair]
            # the row's own pick, graded: its good count must reproduce the row's found count (475's fallbacks when the
            # chooser does not run)
            if row_hyps:
                _, rkind, rval = min(row_hyps, key=lambda t: t[0])
            elif len(cand) == 2:
                m2 = e473.choose(E, P, cand, STOCK)
                rkind, rval = "zpair", (cand[0], cand[1], m2[2] if m2 else 0.0)
            elif len(cand) == 1 and mix:
                best = min((m for m in mix if m[1] == cand[0]), default=None)
                rkind, rval = ("mixed", best[1:]) if best else (None, None)
            else:
                rkind, rval = None, None
            rgood = False
            if rkind == "zpair" and regime == "all-ZDC":
                i, j, m2 = rval
                rgood = ((i in pz[1] and j in pz[2]) or (i in pz[2] and j in pz[1])) and abs(m2 - M_L) < 0.03
            elif rkind == "mixed" and regime == "B0+ZDC":
                i, kb, m2 = rval
                rz = 1 if l["homes"][1] == "ZDC" else 2
                rgood = i in pz[rz] and kb in pb[3 - rz] and abs(m2 - M_L) < 0.03
            elif rkind == "b0pair" and regime == "B0+B0":
                kb, lb, m2 = rval
                rgood = ((kb in pb[1] and lb in pb[2]) or (kb in pb[2] and lb in pb[1])) and abs(m2 - M_L) < 0.03
            res[f"{regime}: emulated row good"] += rgood
            if law is None:
                continue
            # With crystal candidates the chooser always runs, so every row hypothesis competes with them, whether or not
            # the row's own chooser ran (with two tagged clusters and no B0 photon the row keeps that pair unscored).
            row_hyps_all = []
            if zpair is not None:
                row_hyps_all.append((zpair[3], "zpair", (zpair[0], zpair[1], zpair[2])))
            row_hyps_all += [(m[0], "mixed", m[1:]) for m in mix]
            row_hyps_all += [(q[0], "b0pair", q[1:]) for q in bpair]
            # crystal hypotheses (independent of crys_pd except for the depth term: computed once per pd value)
            tot = E.sum(); sx = (E[:, None] * P).sum(axis=0) if len(E) else np.zeros(3)

            def neutron(minus_clusters, minus_cols):
                # the column is rec-hit energy; the Hcal clusters carry 1 / sampFrac on top (--col-scale)
                raw = tot - sum(E[i] for i in minus_clusters) - args.col_scale * sum(c["col"] for c in minus_cols)
                if raw <= 0:
                    return 0.0, np.array([0.0, 0.0, Z_ZDC])
                cen = (sx - sum(E[i] * P[i] for i in minus_clusters)
                       - args.col_scale * sum(c["col"] * np.array([c["x"][0] * Z_ZDC / Z_CRYS, c["x"][1] * Z_ZDC / Z_CRYS, Z_ZDC]) for c in minus_cols)) / raw
                return STOCK["an"] * raw ** STOCK["bn"], cen
            for veto, pd in [(v, q) for v in args.veto for q in args.crys_pd]:
                xc = xcs[veto]
                hyps = list(row_hyps_all)
                for ci_, c in enumerate(xc):
                    for i in cand:     # crystal + tagged Hcal photon (never the cluster behind the crystal: the same photon)
                        if i in c["behind"]:
                            continue
                        En, cen = neutron([i], [c])
                        Eg = STOCK["ag"] * E[i] ** STOCK["bg"]
                        s, ml = score_zdc_pair((Eg, P[i]), (c["E"], c["x"]), En, cen, (P[i][2] - Z_ZDC) / 100.0 + pd, STOCK)
                        hyps.append((s, "crys+hcal", (ci_, i, ml)))
                    for cj_ in range(ci_ + 1, len(xc)):     # crystal + crystal
                        d = xc[cj_]
                        En, cen = neutron([], [c, d])
                        s, ml = score_zdc_pair((c["E"], c["x"]), (d["E"], d["x"]), En, cen, 2 * pd, STOCK)
                        hyps.append((s, "crys+crys", (ci_, cj_, ml)))
                    for kb in range(len(Eb)):     # crystal + B0 photon
                        En, cen = neutron([], [c])
                        Ebc = e475.B0_LAW[0] * Eb[kb] ** e475.B0_LAW[1]
                        s, ml = score_mixed((c["E"], c["x"]), (Ebc, Pb[kb]), En, cen, MIXED_PD * pd, STOCK)
                        hyps.append((s, "crys+b0", (ci_, kb, ml)))
                if not hyps:
                    continue
                s, kind, val = min(hyps, key=lambda t: t[0])
                if not kind.startswith("crys"):
                    continue
                good = False
                ml = val[2]
                inwin = abs(ml - M_L) < 0.03
                if kind == "crys+hcal" and regime == "all-ZDC":
                    c, i = xc[val[0]], val[1]
                    good = inwin and ((c["pur"][1] >= 0.8 and i in pz[2]) or (c["pur"][2] >= 0.8 and i in pz[1]))
                elif kind == "crys+crys" and regime == "all-ZDC":
                    c, d = xc[val[0]], xc[val[1]]
                    good = inwin and ((c["pur"][1] >= 0.8 and d["pur"][2] >= 0.8) or (c["pur"][2] >= 0.8 and d["pur"][1] >= 0.8))
                elif kind == "crys+b0" and regime == "B0+ZDC":
                    c, kb = xc[val[0]], val[1]
                    rz = 1 if l["homes"][1] == "ZDC" else 2
                    good = inwin and c["pur"][rz] >= 0.8 and kb in pb[3 - rz]
                name = f"veto {veto} crys_pd {pd:+.0f}"
                res[f"{regime}: {name} picks crystal"] += 1
                res[f"{regime}: {name} picks crystal, in window"] += inwin
                res[f"{regime}: {name} window change"] += int(inwin) - int(row_in_window)
                res[f"{regime}: {name} good"] += good
                res[f"{regime}: {name} net"] += int(good) - int(found)
            if not (args.z3 or args.full or args.alt):
                continue
            # Z3: a tagged Hcal photon with a crystal cluster ≥ CRYS_MIN in front of it takes the crystal law's energy (the
            # leading such cluster and its column) instead of the Hcal law's. The row hypotheses are recomputed with 477's
            # scorers ("recomputed": Hcal law everywhere, the reproduction check; "z3": crystal energies), and every Λ is
            # graded (the energies change the mass of an unchanged pick too); net = good − the emulated row's good.
            eg_hcal = {c: STOCK["ag"] * E[c] ** STOCK["bg"] for c in cand}
            eg_z3 = dict(eg_hcal)
            alt_out = {}     # --alt-col-out: the column of a crystal-law Hcal photon beyond its own cluster leaves the neutron
            for c in cand:
                front = [x for x in xc_all if c in x["behind"]]
                if front:
                    f = max(front, key=lambda x: cls[x["k"]]["E"])
                    eg_z3[c] = max(cls[f["k"]]["E"], crystal_law(law, cls[f["k"]]["E"], f["col"]))
                    extra = max(0.0, args.col_scale * f["col"] - E[c])
                    if args.alt_col_out and extra > 0:
                        alt_out[c] = [{"col": extra / args.col_scale, "x": f["x"]}]
            # --axis-law: every tagged Hcal photon also offers the axis law's energy (481: crystal and Hcal rec hits within R of
            # its own projective line, fitted on the photon guns); with --alt-col-out its column beyond its cluster leaves the neutron
            ax_opt = {}
            if axis is not None:
                for c in cand:
                    tx, ty = P[c][0] / P[c][2], P[c][1] / P[c][2]
                    ecr = float(ce[np.hypot(cp[:, 0] - tx * cp[:, 2], cp[:, 1] - ty * cp[:, 2]) <= axis["r"]].sum()) if len(ce) else 0.0
                    ecl = float(he[np.hypot(hp[:, 0] - tx * hp[:, 2], hp[:, 1] - ty * hp[:, 2]) <= axis["r"]].sum()) if len(he) else 0.0
                    e_ax = axis["a"] * ecr + axis["b"] * ecl + axis["c"]
                    if e_ax <= 0:
                        continue
                    extra = max(0.0, args.col_scale * ecl - E[c])
                    out_cols = [{"col": extra / args.col_scale, "x": np.array([tx * Z_CRYS, ty * Z_CRYS, Z_CRYS])}] if (args.alt_col_out and extra > 0) else []
                    ax_opt[c] = (e_ax, out_cols)
            b0e = [e475.B0_LAW[0] * Eb[kb] ** e475.B0_LAW[1] for kb in range(len(Eb))]
            lead = int(np.argmax(E)) if len(E) else -1
            # --front: the crystal rec-hit energy within 30 mm in front of each tagged Hcal photon (its projective line)
            e_front = {}
            for c in cand:
                tx, ty = P[c][0] / P[c][2], P[c][1] / P[c][2]
                e_front[c] = float(ce[np.hypot(cp[:, 0] - tx * cp[:, 2], cp[:, 1] - ty * cp[:, 2]) <= 30.0].sum()) if len(ce) else 0.0

            def front_term(t, w, e0):
                """--front: w·exp(−E_front / e0) per tagged Hcal photon of hypothesis t (no crystal energy in front: fragment-like)."""
                kind, val = t[1], t[2]
                hc = {"zpair": (val[0], val[1]), "mixed": (val[0],), "crys+hcal": (val[1],)}.get(kind, ())
                return sum(w * math.exp(-e_front[i] / e0) for i in hc)

            def iso_term(t, xc, w, lscale):
                """--iso: w·exp(−d / l) per Hcal photon of hypothesis t (and per crystal photon with --iso-crys)."""
                kind, val = t[1], t[2]
                if lead < 0:     # no Hcal cluster: no neutron core to be close to
                    return 0.0
                hc = {"zpair": (val[0], val[1]), "mixed": (val[0],), "crys+hcal": (val[1],)}.get(kind, ())
                cr = {"crys+hcal": (val[0],), "crys+crys": (val[0], val[1]), "crys+b0": (val[0],)}.get(kind, ()) if args.iso_crys else ()
                tot = sum(w * math.exp(-math.hypot(P[i][0] - P[lead][0], P[i][1] - P[lead][1]) / lscale) for i in hc)
                for k in cr:
                    x = xc[k]["x"]; f = P[lead][2] / Z_CRYS
                    tot += w * math.exp(-math.hypot(x[0] * f - P[lead][0], x[1] * f - P[lead][1]) / lscale)
                return tot
            rinwin = rkind is not None and abs(rval[2] - M_L) < 0.03
            # --full: the crystal decision with every hypothesis rescored under the chooser weights of --sigma-l / --w-depth
            # (the row's reference decision keeps the launched weights), every Λ graded against the emulated row
            pv = dict(STOCK, **{k: v for k, v in (("sigma_l", args.sigma_l), ("w_depth", args.w_depth), ("pi0_win", args.pi0_win)) if v is not None})
            bpair_v = e475.pair_scores(E, P, Eb, Pb, pv, B0_OFFSET) if len(Eb) >= 2 else []
            modes = [("recomputed", eg_hcal, STOCK, bpair)] + ([("z3", eg_z3, STOCK, bpair)] if args.z3 else []) \
                + ([("full", eg_hcal, pv, bpair_v)] if args.full else []) + ([("alt", eg_hcal, pv, bpair_v)] if args.alt else [])
            for mode, eg, ps, bp in modes:
                for veto, pd in [(v, q) for v in args.veto for q in args.crys_pd]:
                    xc = xcs[veto] if mode != "recomputed" else []
                    hyps = []
                    # energy options per tagged cluster: (energy, columns that leave the neutron with it)
                    egv = {c: ([(eg[c], [])] + ([(eg_z3[c], alt_out.get(c, []))] if mode == "alt" and eg_z3[c] != eg[c] and not args.no_crystal_alt else [])
                               + ([ax_opt[c]] if mode == "alt" and c in ax_opt else [])) for c in cand}
                    for ia in range(len(cand)):
                        for ib in range(ia + 1, len(cand)):
                            i, j = cand[ia], cand[ib]
                            for e1, o1 in egv[i]:
                                for e2, o2 in egv[j]:
                                    En, cen = neutron([i, j], o1 + o2)
                                    s, ml = score_zdc_pair((e1, P[i]), (e2, P[j]), En, cen, (P[i][2] + P[j][2] - 2 * Z_ZDC) / 100.0, ps)
                                    hyps.append((s, "zpair", (i, j, ml, En + e1 + e2, e1, e2, En)))
                        for kb in range(len(Eb)):
                            for e1, o1 in egv[cand[ia]]:
                                En, cen = neutron([cand[ia]], o1)
                                s, ml = score_mixed((e1, P[cand[ia]]), (b0e[kb], Pb[kb]), En, cen, MIXED_PD * (P[cand[ia]][2] - Z_ZDC) / 100.0, ps)
                                hyps.append((s, "mixed", (cand[ia], kb, ml, En + e1 + b0e[kb])))
                    hyps += [(q[0], "b0pair", q[1:]) for q in bp]
                    for ci_, c in enumerate(xc):
                        for i in cand:
                            if i in c["behind"]:
                                continue
                            for e1, o1 in egv[i]:
                                En, cen = neutron([i], [c] + o1)
                                s, ml = score_zdc_pair((e1, P[i]), (c["E"], c["x"]), En, cen, (P[i][2] - Z_ZDC) / 100.0 + pd, ps)
                                hyps.append((s, "crys+hcal", (ci_, i, ml, En + e1 + c["E"], c["E"], e1, En)))
                        for cj_ in range(ci_ + 1, len(xc)):
                            d = xc[cj_]
                            En, cen = neutron([], [c, d])
                            s, ml = score_zdc_pair((c["E"], c["x"]), (d["E"], d["x"]), En, cen, 2 * pd, ps)
                            hyps.append((s, "crys+crys", (ci_, cj_, ml, En + c["E"] + d["E"], c["E"], d["E"], En)))
                        for kb in range(len(Eb)):
                            En, cen = neutron([], [c])
                            s, ml = score_mixed((c["E"], c["x"]), (b0e[kb], Pb[kb]), En, cen, MIXED_PD * pd, ps)
                            hyps.append((s, "crys+b0", (ci_, kb, ml)))
                    # --iso: an isolation term w·exp(−d / l) per Hcal photon (d: transverse distance to the most energetic Hcal
                    # cluster, the neutron core) and, with --iso-crys, per crystal photon; (0, 1) is the launched chooser
                    iso0 = tuple(args.iso[0]) if args.iso else (0.0, 1.0)
                    settings = [(0.0, 1.0, 0.0, 1.0)] + ([(w_, l_, 0.0, 1.0) for w_, l_ in args.iso] if mode in ("alt", "full") else []) \
                        + ([(iso0[0], iso0[1], fw, fe) for fw, fe in args.front] if mode in ("alt", "full") else [])
                    for iso_w, iso_l, fr_w, fr_e in settings:
                        def key(t, iso_w=iso_w, iso_l=iso_l, fr_w=fr_w, fr_e=fr_e):
                            return (t[0] + (iso_term(t, xc, iso_w, iso_l) if iso_w else 0.0)
                                    + (front_term(t, fr_w, fr_e) if fr_w else 0.0))
                        # the chooser runs as the row's (runs) or whenever crystal candidates exist; otherwise the fallbacks
                        if runs or xc:
                            pick = min(hyps, key=key) if hyps else None
                        elif len(cand) == 2:
                            pick = next((h for h in hyps if h[1] == "zpair"), None)
                        elif len(cand) == 1:
                            pick = min((h for h in hyps if h[1] == "mixed"), key=key, default=None)
                        else:
                            pick = None
                        good, inwin = False, False
                        if pick is not None:
                            _, kind, val = pick
                            inwin = abs(val[2] - M_L) < 0.03
                            rz = 1 if l["homes"][1] == "ZDC" else 2
                            if kind == "zpair" and regime == "all-ZDC":
                                good = inwin and ((val[0] in pz[1] and val[1] in pz[2]) or (val[0] in pz[2] and val[1] in pz[1]))
                            elif kind == "mixed" and regime == "B0+ZDC":
                                good = inwin and val[0] in pz[rz] and val[1] in pb[3 - rz]
                            elif kind == "b0pair" and regime == "B0+B0":
                                good = inwin and ((val[0] in pb[1] and val[1] in pb[2]) or (val[0] in pb[2] and val[1] in pb[1]))
                            elif kind == "crys+hcal" and regime == "all-ZDC":
                                c, i = xc[val[0]], val[1]
                                good = inwin and ((c["pur"][1] >= 0.8 and i in pz[2]) or (c["pur"][2] >= 0.8 and i in pz[1]))
                            elif kind == "crys+crys" and regime == "all-ZDC":
                                c, d = xc[val[0]], xc[val[1]]
                                good = inwin and ((c["pur"][1] >= 0.8 and d["pur"][2] >= 0.8) or (c["pur"][2] >= 0.8 and d["pur"][1] >= 0.8))
                            elif kind == "crys+b0" and regime == "B0+ZDC":
                                good = inwin and xc[val[0]]["pur"][rz] >= 0.8 and val[1] in pb[3 - rz]
                        name = ((mode if mode == "recomputed" else f"{mode} veto {veto} crys_pd {pd:+.0f}") + (f" iso {iso_w:g}/{iso_l:g}" if iso_w else "")
                                + (f" front {fr_w:g}/{fr_e:g}" if fr_w else ""))
                        res[f"{regime}: {name} good"] += good
                        # --why: an all-ZDC Λ the alt decision misses although a photon has a pure crystal cluster ≥ CRYS_MIN
                        if args.why and mode == "alt" and not fr_w and (iso_w, iso_l) == iso0 and regime == "all-ZDC" and not good:
                            for r in (1, 2):
                                pure_cand = [k for k, c in enumerate(xc) if c["pur"][r] >= 0.8]
                                pure_veto = [x for x in xc_all if x["pur"][r] >= 0.8 and x not in xc]
                                if not (pure_cand or pure_veto):
                                    continue
                                other = 3 - r
                                other_ok = bool(pz[other]) or any(c["pur"][other] >= 0.8 for c in xc_all)
                                if pure_cand:
                                    if pick is None:
                                        why = "candidate, no pick"
                                    elif pick[1].startswith("crys") and any(pick[2][q] in pure_cand for q in ((0, 1) if pick[1] == "crys+crys" else (0,))):
                                        why = "candidate picked, " + ("out of window" if not inwin else "other photon wrong")
                                    else:
                                        why = f"candidate, {pick[1]} won"
                                else:
                                    behind = {c for x in pure_veto for c in x["behind"]}
                                    why = "vetoed, Hcal cluster behind " + ("pure" if behind & pz[r] else "impure")
                                    if pick is not None and pick[1] in ("zpair", "mixed", "crys+hcal") and (set(pick[2][:2]) & behind):
                                        why += ", picked" + (" out of window" if not inwin else "")
                                res[f"why: {why}" + ("" if other_ok else " (other photon without a pure candidate)")] += 1
                                break
                        # --why-all: every all-ZDC Λ the decision misses although both photons have a pure candidate
                        # (tagged Hcal or crystal): what the chooser picked instead
                        if (args.why_all and mode == "alt" and regime == "all-ZDC" and not good and not fr_w
                                and (iso_w, iso_l) == iso0
                                and all(pz[r] or any(c["pur"][r] >= 0.8 for c in xc) for r in (1, 2))):
                            def who(m, is_crys):
                                if is_crys:
                                    c = xc[m]
                                    return next((r for r in (1, 2) if c["pur"][r] >= 0.8), 0), "crystal"
                                r = next((r for r in (1, 2) if m in pz[r]), 0)
                                if r:
                                    return r, "hcal"
                                wn = w[(rc == m) & (own == base)].sum()
                                return 0, "hcal neutron fragment" if wn >= 0.5 else "hcal other"
                            if pick is None:
                                cat = "no pick"
                            elif pick[1] in ("mixed", "b0pair", "crys+b0"):
                                cat = f"a B0 hypothesis ({pick[1]}) won"
                            else:
                                k, v = pick[1], pick[2]
                                mem = {"zpair": [(v[0], False), (v[1], False)], "crys+hcal": [(v[0], True), (v[1], False)],
                                       "crys+crys": [(v[0], True), (v[1], True)]}[k]
                                ids = [who(m, c) for m, c in mem]
                                right = [t for t in ids if t[0]]
                                if len(right) == 2 and right[0][0] != right[1][0]:
                                    dm = v[2] - M_L
                                    cat = "right pair, mass " + ("high" if dm > 0 else "low")
                                    why_dm.append(dm)
                                    if len(v) >= 7:     # energies / true: the members' photons in order, the neutron
                                        why_e["photon"] += [v[4] / l["E"][ids[0][0]], v[5] / l["E"][ids[1][0]]]
                                        for q, (m, isc) in enumerate(mem):
                                            typ = "crystal" if isc else ("hcal, crystal-law energy" if (k == "zpair" and abs(v[4 + q] - eg_hcal.get(m, -1)) > 1e-9) or (k == "crys+hcal" and abs(v[5] - eg_hcal.get(m, -1)) > 1e-9) else "hcal, Hcal-law energy")
                                            why_e[f"photon ({typ})"].append(v[4 + q] / l["E"][ids[q][0]])
                                        why_e["neutron"].append(v[6] / l["E"][0])
                                        why_e["kind " + k].append(1.0)
                                elif len(right) == 2:
                                    cat = "both pure for the same photon"
                                elif len(right) == 1:
                                    cat = "one right, other: " + next(t[1] for t in ids if not t[0])
                                else:
                                    cat = "both wrong: " + " + ".join(sorted(t[1] for t in ids))
                            res[f"why-all: {cat}"] += 1
                        # --why-all, B0 + ZDC: the misses whose ZDC photon has a pure candidate (tagged Hcal or crystal) and whose
                        # B0 photon a pure B0 cluster
                        if (args.why_all and mode == "alt" and regime == "B0+ZDC" and not good and not fr_w
                                and (iso_w, iso_l) == iso0):
                            rzz = 1 if l["homes"][1] == "ZDC" else 2
                            zok = bool(pz[rzz]) or any(c["pur"][rzz] >= 0.8 for c in xc)
                            bok = bool(pb[3 - rzz])
                            if zok and bok:
                                if pick is None:
                                    cat = "no pick"
                                elif pick[1] in ("zpair", "crys+hcal", "crys+crys"):
                                    cat = f"a ZDC pair ({pick[1]}) won"
                                elif pick[1] == "b0pair":
                                    cat = "a B0 pair won"
                                else:
                                    v = pick[2]
                                    zright = (v[0] in pz[rzz]) if pick[1] == "mixed" else (xc[v[0]]["pur"][rzz] >= 0.8)
                                    bright = v[1] in pb[3 - rzz]
                                    if zright and bright:
                                        cat = "right pair, mass " + ("high" if v[2] > M_L else "low")
                                    elif bright:
                                        cat = f"B0 right, ZDC photon wrong ({'Hcal' if pick[1] == 'mixed' else 'crystal'})"
                                    elif zright:
                                        cat = "ZDC right, B0 photon wrong"
                                    else:
                                        cat = "both wrong"
                                res[f"why-all B0+ZDC: {cat}"] += 1
                        if good and pick is not None and len(pick[2]) > 3:
                            e_ratio[name].append(pick[2][3] / math.sqrt(l["p"] ** 2 + M_L ** 2))
                        if regime == "B0+B0":     # the row finds these through LambdaReconstruction too: count switches only
                            kind_new = pick[1] if pick is not None else None
                            if kind_new != rkind:
                                res[f"{regime}: {name} net"] += int(good) - int(found)
                        else:
                            res[f"{regime}: {name} net"] += int(good) - int(rgood)
                        res[f"{regime}: {name} window change"] += int(inwin) - int(rinwin)
                    if mode == "recomputed":
                        break
    out = {"row": args.row, "json_row": jrow, "dataset": args.dataset, "files": len(files), "law": law,
           "params": {"HIT_MIN": HIT_MIN, "PEAK_MIN": PEAK_MIN, "R_SHARE": R_SHARE, "CRYS_MIN": CRYS_MIN, "R_VETO": R_VETO, "R_COL": R_COL},
           "inventory": dict(inv), "inventory_medians": {k: float(np.median(v)) for k, v in inv_e.items()},
           "inventory_quantiles": {k: [float(q) for q in np.percentile(v, [16, 50, 84])] for k, v in inv_e.items()},
           "emulation": dict(res)}
    for k in sorted(inv):
        print(f"  {k:62s} {inv[k]:5d}")
    for k, v in inv_e.items():
        print(f"  {k:62s} 16/50/84 % {np.percentile(v, 16):.2f} / {np.median(v):.2f} / {np.percentile(v, 84):.2f}")
    for k in sorted(res):
        print(f"  {k:62s} {int(res[k]):5d}")
    if why_dm:
        print(f"  why-all right pairs out of the window: Δm 16/50/84 % {np.percentile(why_dm, 16):+.3f} / {np.median(why_dm):+.3f} / "
              f"{np.percentile(why_dm, 84):+.3f} GeV")
        out["why_all_dm_quantiles"] = [float(q) for q in np.percentile(why_dm, [16, 50, 84])]
        for k, v in why_e.items():
            q = np.percentile(v, [16, 50, 84]) if not k.startswith("kind") else [len(v)] * 3
            print(f"  why-all right pairs out of the window, {k}: " + (f"E reco / true 16/50/84 % {q[0]:.3f} / {q[1]:.3f} / {q[2]:.3f} ({len(v)})"
                                                                     if not k.startswith("kind") else f"{len(v)}"))
            out[f"why_all_{k}"] = [float(x) for x in q]
    for k, v in e_ratio.items():
        print(f"  Λ energy / true of good picks, {k}: median {np.median(v):.3f}, σ68 {0.5 * (np.percentile(v, 84) - np.percentile(v, 16)):.3f} ({len(v)})")
    path = repo_path("space", "perf", f"crystal-scope-{args.row}-{args.dataset}{args.tag}.json")
    path.write_text(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print("wrote", path)


if __name__ == "__main__":
    main()
