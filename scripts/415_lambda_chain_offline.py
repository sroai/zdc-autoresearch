#!/usr/bin/env python3
"""S4o: the Λ → n γ γ chain run offline on one row's real clusters, per D4 momentum.

For every D4 event, the clusters 410 best-matched to the true neutron and the two true
photons go through the Λ chain of zdc/lambda_chain.py (the code 414 uses) under two pairings,
and the final mass is scored in the fixed window |m − m_Λ| ≤ 0.03 GeV (configs/metrics.yaml).
The number ties a clustering row to a Λ yield without a new reconstruction: the per-particle
tables of 410 suffice, so rows whose ROOT files were deleted still score (truth variant).

Pairings: stock (LambdaReconstruction at the pin) and vertex_fixed (the stable vertex, B9d).

Variants:
  truth  — the three particles identified by truth, no photon tag needed. Photon energy: its
           best cluster's raw energy through the row's photon law a·E^b. Neutron energy: the
           neutron law applied to the neutron's associated energy summed over all clusters
           (`assoc_E`, the quantity 420 fits the neutron law on; the neutrals factory's SumAll
           with perfect photon identification). Positions: the best clusters'.
  tagged — what EICrecon's chain receives: both photons' best clusters must carry a PDG 22
           neutral and the event a PDG 2112 neutral; energies are those neutrals' energies;
           photon positions are their clusters'; the neutron position is its neutral's first
           cluster (`getClusters(0)`, as LambdaReconstruction reads it). The neutrals factory
           links every ZDC cluster to the neutron (associateAllClustersToNeutron), so 410's
           `tagged_gamma` column cannot see photon tags on D4; the tags are read from the ROOT
           file here and cached beside 410's tables (`<file>.tags.npz`). Rows without ROOT get
           no tagged numbers.

  tagrefit — the clustering selector (D-user-31): the tagged variant's photon tags and neutron, with the
           row's own refit calibration instead of the one it applied. Photon energy: the refit photon law
           on the tagged best cluster's raw energy. Neutron energy: the refit neutron law on the raw sum
           EICrecon fed its law (the non-photon clusters above clusterEmin), recovered by inverting the
           applied law on the neutron neutral's energy. Positions as in tagged. Needs ROOT and a refit.

Every variant requires purity ≥ purity_min (metrics.yaml) for each of the three best clusters,
as S4a_tm does, and three distinct best clusters: two particles sharing a best cluster is a miss.

The row's calibration "as applied": the experiment config's coefficients when set, else the R1
build's patched defaults for rows built on R1, else the pin's stock defaults. The keys
<pairing>_refit repeat the truth variant with the row's own refit (space/perf/calib-<row>.json):
calibration follows an accepted clustering, so that column compares clusterings on equal terms.

Validation (--validate): the tagged stock variant against the in-EICrecon S4a_tm, per momentum
and per event (410's .lambda.npz); and --check-ideal: the chain on 414's ideal inputs reproduces
414's *_ideal columns.

Writes space/perf/lambda-offline-<row>.json (per_momentum[p][<pairing>_<variant>] = fraction of
accepted D4 events, `_n` counts, `_sigma` mass widths; 441 reads it) and the per-event flags as
{data}/reco/<row>/D4_lambda/truth/<file>.offline.npz for paired tests.

Usage:
  uv run scripts/415_lambda_chain_offline.py P1b_R0_thr L01_box3114     # rows
  uv run scripts/415_lambda_chain_offline.py --all                      # every row of scoreboard.csv
  uv run scripts/415_lambda_chain_offline.py --validate L01_box3114 R1_pr3064
  uv run scripts/415_lambda_chain_offline.py --check-ideal P1b_R0_thr
  uv run scripts/415_lambda_chain_offline.py --compare P1d_R1_nlr1 P1b_R0_thr --key vertex_fixed_refit
"""
import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import uproot
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, metrics_config, repo_path  # noqa: E402
from zdc.lambda_chain import M_L, M_N, chain, to_proton  # noqa: E402

PERF = repo_path("space", "perf")
PAIRINGS = ("stock", "vertex_fixed")
STOCK_COEFF = {"photon": (1.1, 0.98), "neutron": (2.4, 0.89)}           # reco.cc at the pin
COEFF_KEYS = {"photon": "reco:ReconstructedFarForwardNeutrals:gammaScaleCorrCoeffHcalZDC",
              "neutron": "reco:ReconstructedFarForwardNeutrals:neutronScaleCorrCoeffHcalZDC"}


def momentum_of(path):
    return int(path.name.split("GeV")[0].split("_")[-1])


def row_config(row):
    for f in sorted(repo_path("configs", "experiments").glob("*.yaml")):
        cfg = yaml.safe_load(f.read_text())
        if cfg and cfg.get("name") == row:
            return cfg
    raise SystemExit(f"no config with name: {row}")


def applied_calibration(row):
    """The photon and neutron laws (a, b) the row's reconstruction applied, with where they came from."""
    cfg = row_config(row)
    base = None
    if cfg.get("install_label") == "R1":                 # the R1 build carries PR 3064's defaults
        base = yaml.safe_load(repo_path("configs", "experiments", "R1param_pr3064.yaml").read_text())["parameters"]
    out = {}
    for kind, key in COEFF_KEYS.items():
        params = cfg.get("parameters") or {}
        if key in params:
            out[kind], src = tuple(float(v) for v in str(params[key]).split(",")), "config"
        elif base and key in base:
            out[kind], src = tuple(float(v) for v in str(base[key]).split(",")), "R1 build defaults"
        else:
            out[kind], src = STOCK_COEFF[kind], "stock"
        out[f"{kind}_source"] = src
    return out


def refit_calibration(row):
    path = PERF / f"calib-{row}.json"
    if not path.exists():
        return None
    c = json.loads(path.read_text())
    return {"photon": (c["photon"]["a"], c["photon"]["b"]), "neutron": (c["neutron"]["a"], c["neutron"]["b"])}


def law(coeff, e):
    return coeff[0] * np.power(max(e, 1e-9), coeff[1])


def law_inverse(coeff, e):
    return np.power(max(e, 1e-9) / coeff[0], 1.0 / coeff[1])


# ---------------------------------------------------------------- photon tags from the ROOT file

def tags_for(root_file, cache, mcfg):
    """Per event: the ZDC cluster indices carried by PDG 22 neutrals with their energies, and the
    neutron neutral's energy, first-cluster position, reference point (its leader cluster, where
    its momentum points) and first-cluster index (lab, mm). Cached as <file>.tags.npz; the cache alone serves
    once the ROOT file is deleted (D-user-32), so tagged scores survive the retention cleanup."""
    if cache.exists() and (not root_file.exists() or cache.stat().st_mtime >= root_file.stat().st_mtime):
        d = np.load(cache, allow_pickle=True)
        return d["gamma"].item(), d["neutron"].item()
    c = mcfg.collections
    nz, cl = c.zdc_neutrals, c.zdc_clusters
    with uproot.open(root_file) as f:
        t = f["events"]
        pdg = t[f"{nz}.PDG"].array(library="ak")
        energy = t[f"{nz}.energy"].array(library="ak")
        begin = t[f"{nz}.clusters_begin"].array(library="ak")
        end = t[f"{nz}.clusters_end"].array(library="ak")
        index = t[f"_{nz}_clusters.index"].array(library="ak")
        pos = [t[f"{cl}.position.{a}"].array(library="ak") for a in "xyz"]
        ref = [t[f"{nz}.referencePoint.{a}"].array(library="ak") for a in "xyz"]
    gamma, neutron = {}, {}
    for ev in range(len(pdg)):
        p, e, b, en, idx = (ak.to_numpy(a[ev]) for a in (pdg, energy, begin, end, index))
        g = {}
        for j in np.flatnonzero(p == 22):
            for k in idx[b[j]:en[j]].tolist():
                g[int(k)] = float(e[j])
        gamma[ev] = g
        jn = np.flatnonzero(p == 2112)
        if len(jn) and en[jn[0]] > b[jn[0]]:
            k0 = int(idx[b[jn[0]]])
            neutron[ev] = (float(e[jn[0]]), tuple(float(pos[a][ev][k0]) for a in range(3)), k0,
                           tuple(float(ref[a][ev][jn[0]]) for a in range(3)))
    np.savez(cache, gamma=np.array(gamma, dtype=object), neutron=np.array(neutron, dtype=object))
    return gamma, neutron


# ---------------------------------------------------------------- the chain on one event

def proton_pos(r):
    return np.array(to_proton(float(r["x"]), float(r["y"]), float(r["z"])))


def score_event(rows, calib, purity_min, tags=None, ev=None, refit=None):
    """The final Λ mass per pairing for one event (None = miss), or None for every pairing when the
    variant's inputs are absent. tags given → the tagged variant, else the truth variant; tags and
    refit given → the tagrefit variant (calib is then the calibration the row applied)."""
    miss = {pa: None for pa in PAIRINGS}
    if set(rows) != {"n", "g1", "g2"} or any(rows[k]["n_clusters"] == 0 for k in rows):
        return miss
    clusters = [int(rows[k]["cluster"]) for k in ("n", "g1", "g2")]
    if len(set(clusters)) < 3 or any(rows[k]["purity"] < purity_min for k in rows):
        return miss
    X = {k: proton_pos(rows[k]) for k in ("g1", "g2")}
    if tags is None:
        E = {k: law(calib["photon"], float(rows[k]["E"])) for k in ("g1", "g2")}
        E["n"] = law(calib["neutron"], float(rows["n"]["assoc_E"]))   # the law gives the total energy (setEnergy)
        X["n"] = proton_pos(rows["n"])
        n_direction = None
        if E["n"] <= M_N:
            return miss
    else:
        gamma, neutron = tags
        g = gamma.get(ev, {})
        if clusters[1] not in g or clusters[2] not in g or ev not in neutron:
            return miss
        E = {"g1": g[clusters[1]], "g2": g[clusters[2]], "n": neutron[ev][0]}
        if refit:
            E = {k: law(refit["photon"], float(rows[k]["E"])) for k in ("g1", "g2")}
            E["n"] = law(refit["neutron"], law_inverse(calib["neutron"], neutron[ev][0]))
        X["n"] = np.array(to_proton(*neutron[ev][1]))           # IDOLA: getClusters(0)
        n_direction = np.array(to_proton(*neutron[ev][3]))      # preselection: the momentum, aimed at the leader
        if E["n"] <= M_N:
            return miss
    return {pa: chain(E, X, pa, n_direction) for pa in PAIRINGS}


def in_window(m, half):
    return m is not None and abs(m - M_L) <= half


# ---------------------------------------------------------------- one row

def run_row(row, profile, mcfg, write=True, quiet=False):
    truth_dir = Path(profile.reco_root) / row / "D4_lambda" / "truth"
    files = sorted((f for f in truth_dir.glob("*.edm4eic.npz")), key=momentum_of)
    if not files:
        raise SystemExit(f"{row}: no 410 tables under {truth_dir}")
    half = float(mcfg.windows.lambda_mass_half_window_gev)
    purity_min = float(mcfg.truth_match.purity_min)
    calib = applied_calibration(row)
    refit = refit_calibration(row)
    result = {"row": row, "score_half_window_gev": half, "purity_min": purity_min,
              "calibration_applied": {k: list(v) if isinstance(v, tuple) else v for k, v in calib.items()},
              "calibration_refit": {k: list(v) for k, v in refit.items()} if refit else None,
              "tagged_available": True, "per_momentum": {}}
    for f in files:
        p = momentum_of(f)
        table = np.load(f)["table"]
        events = np.unique(table["event"])
        root = truth_dir.parent / f.name.replace(".npz", ".root")
        cache = f.with_suffix(".tags.npz")
        tags = tags_for(root, cache, mcfg) if root.exists() or cache.exists() else None
        if tags is None:
            result["tagged_available"] = False
        flags = {f"{pa}_{v}": np.zeros(len(events), bool) for pa in PAIRINGS for v in ("truth", "tagged", "refit", "tagrefit")}
        masses = {k: [] for k in flags}
        for i, ev in enumerate(events):
            rows = {r["role"]: r for r in table[table["event"] == ev]}
            variants = {"truth": score_event(rows, calib, purity_min)}
            if refit:
                variants["refit"] = score_event(rows, refit, purity_min)
            if tags is not None:
                variants["tagged"] = score_event(rows, calib, purity_min, tags=tags, ev=int(ev))
                if refit:
                    variants["tagrefit"] = score_event(rows, calib, purity_min, tags=tags, ev=int(ev), refit=refit)
            for v, ms in variants.items():
                for pa, m in ms.items():
                    if in_window(m, half):
                        flags[f"{pa}_{v}"][i] = True
                        masses[f"{pa}_{v}"].append(m)
        n = len(events)
        out = {"events_n": n}
        for key, fl in flags.items():
            pa, v = key.rsplit("_", 1)
            if v in ("tagged", "tagrefit") and tags is None or v in ("refit", "tagrefit") and not refit:
                continue
            out[key] = float(fl.mean())          # <pairing>_refit: the truth variant under the row's own refit
            out[f"{key}_n"] = int(fl.sum())
            out[f"{key}_sigma"] = float(np.std(masses[key])) if len(masses[key]) > 5 else None
        result["per_momentum"][str(p)] = out
        if write:
            np.savez_compressed(f.with_suffix(".offline.npz"), events=events, **flags)
        if not quiet:
            cells = "  ".join(f"{k} {out[k]:.4f} ({out[k + '_n']})" for k in sorted(out) if not k.endswith(("_n", "_sigma")))
            print(f"{row} {p:4d} GeV  {cells}")
    if write:
        path = PERF / f"lambda-offline-{row}.json"
        path.write_text(json.dumps(result, indent=1))
        print(f"wrote {path}")
    return result


# ---------------------------------------------------------------- validation

def fragment_built(root_file, table, events):
    """Per event: True when EICrecon's Λ (the one nearest m_Λ) takes a photon from a cluster other
    than that photon's best-matched cluster (a fragment S4a_tm credits through purity alone)."""
    nz = "ReconstructedHcalFarForwardZDCNeutrals"
    with uproot.open(root_file) as f:
        br = f["events"].arrays([f"{nz}.clusters_begin", f"_{nz}_clusters.index", "ReconstructedLambdas.mass",
                                 "ReconstructedLambdas.particles_begin", "_ReconstructedLambdas_particles.index"])
    out = {}
    for ev in events:
        b = br[int(ev)]
        mass = ak.to_numpy(b["ReconstructedLambdas.mass"])
        if not len(mass):
            continue
        rows = {r["role"]: r for r in table[table["event"] == ev]}
        best = {int(rows[k]["cluster"]) for k in ("g1", "g2") if k in rows}
        idx, cb = ak.to_numpy(b[f"_{nz}_clusters.index"]), ak.to_numpy(b[f"{nz}.clusters_begin"])
        parts, pb = ak.to_numpy(b["_ReconstructedLambdas_particles.index"]), ak.to_numpy(b["ReconstructedLambdas.particles_begin"])
        k = int(np.argmin(np.abs(mass - M_L)))
        photons = {int(idx[cb[j]]) for j in parts[pb[k] + 1:pb[k] + 3]}     # daughter order n, γ1, γ2
        out[int(ev)] = photons != best
    return out


def validate(row, profile, mcfg):
    """The tagged stock variant against the in-EICrecon S4a_tm, per momentum and per event.

    The offline chain sees only best-matched clusters, so an S4a_tm Λ built from a photon fragment
    (another cluster with purity ≥ purity_min for that photon) cannot be reproduced: those events are
    counted apart, and the paired z is quoted on all events and on the events without such a Λ."""
    run_row(row, profile, mcfg, write=True, quiet=True)
    truth_dir = Path(profile.reco_root) / row / "D4_lambda" / "truth"
    report = {}
    print(f"\n{row}: tagged stock (offline) vs S4a_tm (in EICrecon), events per momentum")
    print(f"{'p':>4s} {'S4a_tm':>7s} {'offline':>7s} {'both':>5s} {'only_reco':>9s} {'(fragment)':>10s} {'only_off':>8s} {'z_all':>6s} {'z_best':>6s}")
    total = {"only_reco": 0, "fragment": 0, "only_offline": 0, "S4a_tm": 0, "offline": 0}
    for f in sorted(truth_dir.glob("*.edm4eic.offline.npz"), key=momentum_of):
        p = momentum_of(f)
        off = np.load(f)
        lam = np.load(truth_dir / f.name.replace(".offline.npz", ".lambda.npz"))["table"]
        table = np.load(truth_dir / f.name.replace(".offline.npz", ".npz"))["table"]
        reco = dict(zip(lam["event"].tolist(), lam["matched"].tolist()))
        anyc = dict(zip(lam["event"].tolist(), lam["any"].tolist()))
        a = np.array([reco.get(int(e), False) for e in off["events"]])
        b = off["stock_tagged"]
        only_reco_ev = off["events"][a & ~b]
        frag = fragment_built(truth_dir.parent / f.name.replace(".offline.npz", ".root"), table, only_reco_ev)
        n_frag = int(sum(frag.values()))
        only_reco, only_off = int((a & ~b).sum()), int((~a & b).sum())
        z_all = (only_off - only_reco) / np.sqrt(only_reco + only_off) if only_reco + only_off else 0.0
        rb = only_reco - n_frag
        z_best = (only_off - rb) / np.sqrt(rb + only_off) if rb + only_off else 0.0
        off_ev = off["events"][~a & b].tolist()
        report[str(p)] = {"S4a_tm_n": int(a.sum()), "offline_n": int(b.sum()), "both": int((a & b).sum()),
                          "only_reco": only_reco, "only_reco_fragment_built": n_frag, "only_offline": only_off,
                          "z_all": z_all, "z_best_clusters": z_best,
                          "only_offline_events_with_other_candidate": [e for e in off_ev if anyc.get(e)],
                          "only_offline_events": off_ev, "only_reco_events": only_reco_ev.tolist()}
        for k, v in (("only_reco", only_reco), ("fragment", n_frag), ("only_offline", only_off), ("S4a_tm", int(a.sum())), ("offline", int(b.sum()))):
            total[k] += v
        print(f"{p:4d} {int(a.sum()):7d} {int(b.sum()):7d} {int((a & b).sum()):5d} {only_reco:9d} {n_frag:10d} {only_off:8d} {z_all:6.2f} {z_best:6.2f}")
    rb = total["only_reco"] - total["fragment"]
    total["z_all"] = (total["only_offline"] - total["only_reco"]) / max(np.sqrt(total["only_reco"] + total["only_offline"]), 1e-9)
    total["z_best_clusters"] = (total["only_offline"] - rb) / max(np.sqrt(rb + total["only_offline"]), 1e-9)
    report["all"] = total
    print(f" all {total['S4a_tm']:7d} {total['offline']:7d}       {total['only_reco']:9d} {total['fragment']:10d} {total['only_offline']:8d} {total['z_all']:6.2f} {total['z_best_clusters']:6.2f}")
    return report


def compare(row_a, row_b, key, profile):
    """Paired test of one S4o key between two rows on the same D4 events (McNemar on the discordant ones):
    per momentum, events gained by A over B, lost, and z = (gained − lost) / √(gained + lost)."""
    out = {}
    da = Path(profile.reco_root) / row_a / "D4_lambda" / "truth"
    db = Path(profile.reco_root) / row_b / "D4_lambda" / "truth"
    print(f"{key}: {row_a} vs {row_b}")
    print(f"{'p':>4s} {'A':>5s} {'B':>5s} {'gained':>6s} {'lost':>5s} {'z':>6s}")
    tot = [0, 0]
    for fa in sorted(da.glob("*.edm4eic.offline.npz"), key=momentum_of):
        fb = db / fa.name
        if not fb.exists():
            continue
        a, b = np.load(fa), np.load(fb)
        ea = dict(zip(a["events"].tolist(), a[key].tolist()))
        eb = dict(zip(b["events"].tolist(), b[key].tolist()))
        common = sorted(set(ea) & set(eb))
        x = np.array([ea[e] for e in common]); y = np.array([eb[e] for e in common])
        g, l = int((x & ~y).sum()), int((~x & y).sum())
        z = (g - l) / np.sqrt(g + l) if g + l else 0.0
        tot[0] += g; tot[1] += l
        p = momentum_of(fa)
        out[str(p)] = {"A_n": int(x.sum()), "B_n": int(y.sum()), "gained": g, "lost": l, "z": z}
        print(f"{p:4d} {int(x.sum()):5d} {int(y.sum()):5d} {g:6d} {l:5d} {z:6.2f}")
    z = (tot[0] - tot[1]) / np.sqrt(sum(tot)) if sum(tot) else 0.0
    out["pooled"] = {"gained": tot[0], "lost": tot[1], "z": z}
    print(f" all             {tot[0]:6d} {tot[1]:5d} {z:6.2f}")
    return out


def check_ideal(row, profile):
    """414's *_ideal columns from the shared chain on ideal inputs, through this script's loop."""
    spec = importlib.util.spec_from_file_location("ceiling414", repo_path("scripts", "414_lambda_ceiling_variants.py"))
    m414 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m414)
    ref = json.loads((PERF / f"lambda-ceiling-variants-{row}.json").read_text())["per_momentum"]
    truth_dir = Path(profile.reco_root) / row / "D4_lambda" / "truth"
    worst = 0.0
    for f in sorted(truth_dir.glob("*.edm4eic.npz"), key=momentum_of):
        p = momentum_of(f)
        t = np.load(f)["table"]
        events = np.unique(t["event"])
        cnt = {pa: 0 for pa in ("stock", "vertex", "vertex_fixed")}
        for ev in events:
            rows = {r["role"]: r for r in t[t["event"] == ev]}
            if set(rows) != {"n", "g1", "g2"}:
                continue
            Et = {k: float(np.sqrt(rows[k]["true_px"] ** 2 + rows[k]["true_py"] ** 2 + rows[k]["true_pz"] ** 2
                                   + (M_N ** 2 if k == "n" else 0))) for k in rows}
            Xt = {k: m414.line_at(rows[k], m414.DEPTH[k]) for k in rows}
            for pa in cnt:
                cnt[pa] += in_window(chain(Et, Xt, pa), m414.SCORE_HALF)
        cells = []
        for pa, c in cnt.items():
            mine, theirs = c / len(events), ref[str(p)][f"{pa}_ideal"]
            worst = max(worst, abs(mine - theirs))
            cells.append(f"{pa} {mine:.4f}/{theirs:.4f}")
        print(f"{p:4d} GeV  415/414: " + "  ".join(cells))
    print(f"largest difference {worst:.2e}: " + ("REPRODUCED" if worst == 0 else "DIFFERS"))
    return worst


def main():
    sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rows", nargs="*")
    ap.add_argument("--all", action="store_true", help="every row of space/perf/scoreboard.csv with 410 tables")
    ap.add_argument("--validate", action="store_true", help="compare the tagged stock variant with S4a_tm")
    ap.add_argument("--check-ideal", action="store_true", help="reproduce 414's ideal-input columns")
    ap.add_argument("--compare", nargs=2, metavar=("A", "B"), help="paired test of --key between two rows")
    ap.add_argument("--key", default="vertex_fixed_refit", help="S4o key for --compare (default vertex_fixed_refit)")
    args = ap.parse_args()
    profile, mcfg = load_profile(), metrics_config()
    rows = args.rows
    if args.all:
        with open(PERF / "scoreboard.csv") as fh:
            rows = [r["experiment"] for r in csv.DictReader(fh)
                    if (Path(profile.reco_root) / r["experiment"] / "D4_lambda" / "truth").exists()]
    if args.compare:
        a_row, b_row = args.compare
        res = compare(a_row, b_row, args.key, profile)
        path = PERF / f"lambda-offline-compare-{a_row}-vs-{b_row}-{args.key}.json"
        path.write_text(json.dumps(res, indent=1))
        print(f"wrote {path}")
        return
    if args.check_ideal:
        for row in rows:
            check_ideal(row, profile)
        return
    if args.validate:
        out = {row: validate(row, profile, mcfg) for row in rows}
        path = PERF / "lambda-offline-validation.json"
        path.write_text(json.dumps(out, indent=1))
        print(f"wrote {path}")
        return
    for row in rows:
        run_row(row, profile, mcfg)


if __name__ == "__main__":
    main()
