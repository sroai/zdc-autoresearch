#!/usr/bin/env python3
"""Truth matching of ZDC clusters to the generated particles: the selector S0 and the truth-matched cells.

For one experiment's reconstruction of a gun dataset, for every event: the
true particles of interest (D4: the Λ's neutron and the two photons of its π⁰;
D1: the two photons; D2/D3: the single generated particle), their best-matched
cluster through HcalFarForwardZDCClusterAssociations (largest weight × cluster
energy), that cluster's purity (its association weight for the particle) and
containment (share of the particle's associated energy held by the best
cluster), the best cluster's energy and position, and whether the best cluster
is tagged a photon in the neutrals collection. A particle is "separated" when
purity ≥ purity_min and containment ≥ containment_min (configs/metrics.yaml).

Writes {space}/perf/truth-<experiment>-<dataset>.json with per-momentum
S0γ, S0n, S0all and per-event flags (so the paired McNemar test of
400_scoreboard.py --compare can count discordant events), plus the per-particle
table as a compact npz under {data}/reco/<experiment>/<dataset>/truth/.

Usage:
  uv run scripts/410_truth_match.py R0_stock --datasets D4_lambda D1_pi0
  uv run scripts/410_truth_match.py R0_stock                # every gun dataset present

Field names of the association and relation branches come from
configs/metrics.yaml (relations) and are verified at Step 0 against a file:
podio writes a OneToOne relation `rec` of collection X as `_X_rec.index`
(and `.collectionID`), and MCParticle daughters as `_MCParticles_daughters.index`
indexed by MCParticles.daughters_begin/end.
"""
import argparse
import json
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import datasets_config, load_profile, metrics_config, repo_path  # noqa: E402
from zdc.edm import collection_ids  # noqa: E402

PERF = repo_path("space", "perf")


def momentum_of(path):
    token = [t for t in path.name.split("_") if t.endswith("GeV")]
    return int(token[0][:-3]) if token else -1


def targets_for(dataset, mc, links, tm):
    """Indices (per event) of the true particles to match: [[i_n, i_g1, i_g2], ...] or [[i_g1, i_g2]] or [[i]]."""
    pdg = mc["PDG"]
    begin, end = mc["daughters_begin"], mc["daughters_end"]
    out = []
    for ev in range(len(pdg)):
        p = ak.to_numpy(pdg[ev])
        b, e = ak.to_numpy(begin[ev]), ak.to_numpy(end[ev])
        lk = ak.to_numpy(links[ev])
        kids = lambda i: lk[b[i]:e[i]]
        if dataset.startswith("D4"):
            lam = [i for i in np.where(p == tm.lambda_pdg)[0]]
            chosen = []
            for i in lam:
                ks = kids(i)
                n = [k for k in ks if p[k] == tm.neutron_pdg]
                gammas = [k for k in ks if p[k] == tm.photon_pdg]
                for k in ks:
                    if p[k] == tm.pi0_pdg:
                        gammas += [g for g in kids(k) if p[g] == tm.photon_pdg]
                if len(n) == 1 and len(gammas) == 2:
                    chosen = [n[0], gammas[0], gammas[1]]
                    break
            out.append(chosen)
        elif dataset.startswith("D1"):
            pi0 = [i for i in np.where(p == tm.pi0_pdg)[0]]
            chosen = []
            for i in pi0:
                gammas = [g for g in kids(i) if p[g] == tm.photon_pdg]
                if len(gammas) == 2:
                    chosen = gammas
                    break
            out.append(chosen)
        else:  # single-particle guns: the first generator-status-1 particle of the gun's species
            status = ak.to_numpy(mc["generatorStatus"][ev])
            want = tm.photon_pdg if dataset.startswith("D2") else tm.neutron_pdg
            idx = [i for i in np.where((p == want) & (status == 1))[0]]
            out.append(idx[:1])
    return out


def match_file(path, dataset, mcfg):
    c, r, tm = mcfg.collections, mcfg.relations, mcfg.truth_match
    tree = uproot.open(path)["events"]
    arrays = tree.arrays(
        [f"{c.mc_particles}.PDG", f"{c.mc_particles}.generatorStatus", f"{c.mc_particles}.daughters_begin",
         f"{c.mc_particles}.daughters_end", r.mc_daughters_index,
         f"{c.zdc_clusters}.energy", f"{c.zdc_clusters}.position.x", f"{c.zdc_clusters}.position.y", f"{c.zdc_clusters}.position.z",
         f"{c.zdc_cluster_assoc}.weight", r.assoc_rec_index, r.assoc_sim_index,
         *[f"{c.mc_particles}.{k}" for k in ("momentum.x", "momentum.y", "momentum.z", "vertex.x", "vertex.y", "vertex.z", "endpoint.z")]],
        library="ak")
    mc = {k: arrays[f"{c.mc_particles}.{k}"] for k in ["PDG", "generatorStatus", "daughters_begin", "daughters_end"]}
    links = arrays[r.mc_daughters_index]
    cl_e = arrays[f"{c.zdc_clusters}.energy"]
    cl_x, cl_y, cl_z = (arrays[f"{c.zdc_clusters}.position.{a}"] for a in "xyz")
    w, rec, sim = arrays[f"{c.zdc_cluster_assoc}.weight"], arrays[r.assoc_rec_index], arrays[r.assoc_sim_index]
    # neutrals: which clusters are tagged photons (PDG 22) — through the neutrals' cluster relation when present
    true_p = {k: arrays[f"{c.mc_particles}.{k}"] for k in ("momentum.x", "momentum.y", "momentum.z", "vertex.x", "vertex.y", "vertex.z", "endpoint.z")}
    try:
        neutral_pdg = tree[f"{c.zdc_neutrals}.PDG"].array(library="ak")
        neutral_e = tree[f"{c.zdc_neutrals}.energy"].array(library="ak")
        neutral_p = [tree[f"{c.zdc_neutrals}.momentum.{a}"].array(library="ak") for a in "xyz"]
        neutral_cl = tree[f"_{c.zdc_neutrals}_clusters.index"].array(library="ak")
        neutral_cl_begin = tree[f"{c.zdc_neutrals}.clusters_begin"].array(library="ak")
        neutral_cl_end = tree[f"{c.zdc_neutrals}.clusters_end"].array(library="ak")
        have_neutrals = True
    except Exception:
        have_neutrals = False

    # Λ candidates (D4 only): each holds three input neutrals through `particles` (index + collectionID);
    # a daughter from the ZDC neutrals can be traced to its clusters, one from another calorimeter cannot.
    lambdas = {}
    if dataset.startswith("D4"):
        ids = collection_ids(path)
        lambdas["zdc_neutrals_id"] = ids.get(c.zdc_neutrals, -1)
        for name, key in ((c.lambdas, "reco"), (c.lambdas_truthchain, "truth")):
            if name not in tree.keys(recursive=False):   # the truth-chain Λs exist only in the Rt build
                continue
            lambdas[key] = {
                "mass": tree[f"{name}.mass"].array(library="ak"),
                "vz": tree[f"{name}.referencePoint.z"].array(library="ak"),
                "begin": tree[f"{name}.particles_begin"].array(library="ak"),
                "end": tree[f"{name}.particles_end"].array(library="ak"),
                "index": tree[f"_{name}_particles.index"].array(library="ak"),
                "cid": tree[f"_{name}_particles.collectionID"].array(library="ak"),
            }
    lam_rows = []   # one per event with targets: event, any Λ in window, truth-matched Λ, its mass, its vertex z, true decay z, any truth-chain Λ in window
    win_c, win_h = float(mcfg.windows.lambda_mass_gev), float(mcfg.windows.lambda_mass_half_window_gev)

    targets = targets_for(dataset, mc, links, tm)
    rows = []   # one per target particle: event, role, purity, containment, separated, best_E, best_x, best_y, best_z, tagged_gamma
    for ev, idx in enumerate(targets):
        if not idx:
            continue
        we, re_, si = ak.to_numpy(w[ev]), ak.to_numpy(rec[ev]), ak.to_numpy(sim[ev])
        energies = ak.to_numpy(cl_e[ev])
        # cluster index -> the neutral built from it (the neutrals factory sums every hadronic cluster into one neutron).
        # The ZDC runs with associateAllClustersToNeutron: the neutron lists every cluster, photon clusters included,
        # so the photon neutrals are mapped last and a photon neutral wins its cluster (Q14, D-user-29).
        neutral_of = {}
        if have_neutrals:
            npdg = ak.to_numpy(neutral_pdg[ev]); ncl = ak.to_numpy(neutral_cl[ev])
            nb, ne = ak.to_numpy(neutral_cl_begin[ev]), ak.to_numpy(neutral_cl_end[ev])
            for j in sorted(range(len(npdg)), key=lambda j: npdg[j] == tm.photon_pdg):
                for k in ncl[nb[j]:ne[j]].tolist():
                    neutral_of[k] = j
        roles = ["n", "g1", "g2"] if len(idx) == 3 else (["g1", "g2"] if len(idx) == 2 else ["p"])
        for role, i in zip(roles, idx):
            truth = tuple(float(true_p[k][ev][i]) for k in ("momentum.x", "momentum.y", "momentum.z", "vertex.x", "vertex.y", "vertex.z", "endpoint.z"))
            mask = si == i
            if not mask.any():
                rows.append((ev, role, 0.0, 0.0, False, 0.0, 0.0, 0.0, 0.0, False, -1, 0, 0.0, 0.0, 0.0, 0.0, 0, 0.0) + truth)
                continue
            contrib = we[mask] * energies[re_[mask]]        # energy of the particle in each cluster
            best = int(np.argmax(contrib))
            cl = int(re_[mask][best])
            purity = float(we[mask][best])
            containment = float(contrib[best] / contrib.sum()) if contrib.sum() > 0 else 0.0
            separated = purity >= tm.purity_min and containment >= tm.containment_min
            j = neutral_of.get(cl, -1)
            n_pdg = int(npdg[j]) if j >= 0 else 0
            n_e = float(neutral_e[ev][j]) if j >= 0 else 0.0
            n_px, n_py, n_pz = (float(neutral_p[a][ev][j]) if j >= 0 else 0.0 for a in range(3))
            rows.append((ev, role, purity, containment, separated, float(energies[cl]),
                         float(cl_x[ev][cl]), float(cl_y[ev][cl]), float(cl_z[ev][cl]), n_pdg == tm.photon_pdg,
                         cl, int(mask.sum()), n_e, n_px, n_py, n_pz, n_pdg, float(contrib.sum())) + truth)
        if "reco" in lambdas and len(idx) == 3:
            lam_rows.append(match_lambdas(ev, idx, lambdas, we, re_, si, energies, ncl if have_neutrals else None,
                                          nb if have_neutrals else None, ne if have_neutrals else None,
                                          float(true_p["vertex.z"][ev][idx[0]]), tm, win_c, win_h))
    return len(targets), rows, lam_rows


def match_lambdas(ev, idx, lambdas, we, re_, si, energies, ncl, nb, ne, true_decay_z, tm, win_c, win_h):
    """One Λ row for an event: any candidate in the mass window; a truth-matched candidate in the window
    (its neutron daughter holds a cluster with purity ≥ purity_min for the true neutron, and its two photon
    daughters hold clusters with purity ≥ purity_min for the two distinct true photons; every daughter must
    come from the ZDC neutrals); the first truth-matched candidate's mass and vertex z; any truth-chain Λ;
    matched_best: a truth-matched candidate whose two photon daughters each hold that photon's best-matched
    cluster (largest weight × energy), so a Λ built from a photon fragment does not count (Q15, D-user-30)."""
    def purity_of(cluster, particle):
        m = (re_ == cluster) & (si == particle)
        return float(we[m].max()) if m.any() else 0.0

    def best_cluster(particle):
        m = si == particle
        return int(re_[m][np.argmax(we[m] * energies[re_[m]])]) if m.any() else -1

    lam = lambdas["reco"]
    mass = ak.to_numpy(lam["mass"][ev])
    in_window = np.abs(mass - win_c) < win_h
    matched, m_mass, m_vz = False, np.nan, np.nan
    matched_best = False
    i_n, i_g1, i_g2 = idx
    best_g1, best_g2 = best_cluster(i_g1), best_cluster(i_g2)
    for k in np.flatnonzero(in_window):
        b, e = int(lam["begin"][ev][k]), int(lam["end"][ev][k])
        parts, cids = ak.to_numpy(lam["index"][ev][b:e]), ak.to_numpy(lam["cid"][ev][b:e])
        if len(parts) != 3 or ncl is None or not (cids == lambdas["zdc_neutrals_id"]).all():
            continue
        clusters = [ncl[nb[j]:ne[j]].tolist() for j in parts]           # daughter order: n, γ1, γ2 (LambdaReconstruction)
        n_ok = any(purity_of(cl, i_n) >= tm.purity_min for cl in clusters[0])
        g_a = [max((purity_of(cl, g) for cl in clusters[1]), default=0.0) for g in (i_g1, i_g2)]
        g_b = [max((purity_of(cl, g) for cl in clusters[2]), default=0.0) for g in (i_g1, i_g2)]
        g_ok = (g_a[0] >= tm.purity_min and g_b[1] >= tm.purity_min) or (g_a[1] >= tm.purity_min and g_b[0] >= tm.purity_min)
        if n_ok and g_ok and not matched:
            matched, m_mass, m_vz = True, float(mass[k]), float(lam["vz"][ev][k])
        if n_ok and g_ok and not matched_best:
            hold = lambda cls, g, b: b in cls and purity_of(b, g) >= tm.purity_min
            matched_best = (hold(clusters[1], i_g1, best_g1) and hold(clusters[2], i_g2, best_g2)) or \
                           (hold(clusters[1], i_g2, best_g2) and hold(clusters[2], i_g1, best_g1))
        if matched and matched_best:
            break
    any_truth = False
    if "truth" in lambdas:
        any_truth = bool((np.abs(ak.to_numpy(lambdas["truth"]["mass"][ev]) - win_c) < win_h).any())
    return (ev, bool(in_window.any()), matched, m_mass, m_vz, true_decay_z, any_truth, matched_best)


def main():
    sys.stdout.reconfigure(line_buffering=True)  # progress lines reach the log as they happen under nohup
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment")
    ap.add_argument("--datasets", nargs="*")
    args = ap.parse_args()
    profile, mcfg, dcfg = load_profile(), metrics_config(), datasets_config()
    datasets = args.datasets or [d for d in dcfg.guns if (Path(profile.reco_root) / args.experiment / d).exists()]
    PERF.mkdir(parents=True, exist_ok=True)
    for ds in datasets:
        files = sorted((Path(profile.reco_root) / args.experiment / ds).glob("*.edm4eic.root"))
        if not files:
            print(f"{ds}: no reconstruction")
            continue
        summary = {"experiment": args.experiment, "dataset": ds, "per_momentum": {}, "event_flags": {}}
        outdir = files[0].parent / "truth"
        outdir.mkdir(exist_ok=True)
        for f in files:
            p = momentum_of(f)
            nev, rows, lam_rows = match_file(f, ds, mcfg)
            if not rows:
                print(f"{ds} {p} GeV: no target particles found (check targets_for and the relation names)")
                continue
            # One row per target particle. E, x, y, z: the best-matched cluster; cluster: its index in the event;
            # n_clusters: clusters holding any of the particle's energy; assoc_E: the particle's energy summed over them;
            # neutral_*: the neutral (ReconstructedHcalFarForwardZDCNeutrals) built from the best cluster (PDG 0: none);
            # true_*: the MCParticle (momentum in GeV, vertex and endpoint in mm).
            arr = np.array(rows, dtype=[("event", "i4"), ("role", "U2"), ("purity", "f4"), ("containment", "f4"), ("separated", "?"),
                                        ("E", "f4"), ("x", "f4"), ("y", "f4"), ("z", "f4"), ("tagged_gamma", "?"),
                                        ("cluster", "i4"), ("n_clusters", "i4"), ("neutral_E", "f4"), ("neutral_px", "f4"),
                                        ("neutral_py", "f4"), ("neutral_pz", "f4"), ("neutral_pdg", "i4"), ("assoc_E", "f4"),
                                        ("true_px", "f4"), ("true_py", "f4"), ("true_pz", "f4"), ("true_vx", "f4"),
                                        ("true_vy", "f4"), ("true_vz", "f4"), ("true_endz", "f4")])
            np.savez_compressed(outdir / f"{f.stem}.npz", table=arr)
            per = {}
            for role in sorted(set(arr["role"])):
                sel = arr[arr["role"] == role]
                per[f"S0_{role}_sep"] = float(sel["separated"].mean())
                per[f"S0_{role}_purity_mean"] = float(sel["purity"].mean())
                per[f"S0_{role}_tagged_gamma"] = float(sel["tagged_gamma"].mean())
            if {"g1", "g2"} <= set(arr["role"]):
                per["S0_g_sep"] = float(arr[np.isin(arr["role"], ["g1", "g2"])]["separated"].mean())
            events = np.unique(arr["event"])
            all_sep = np.array([bool(arr[arr["event"] == e]["separated"].all()) for e in events])
            per["S0_all_sep"] = float(all_sep.mean())
            per["events_with_targets"] = int(len(events))
            per["events"] = int(nev)
            if lam_rows:
                lt = np.array(lam_rows, dtype=[("event", "i4"), ("any", "?"), ("matched", "?"), ("mass", "f4"),
                                               ("vz", "f4"), ("true_decay_z", "f4"), ("any_truthchain", "?"),
                                               ("matched_best", "?")])
                np.savez_compressed(outdir / f"{f.stem}.lambda.npz", table=lt)
                # denominators: generated events (every D4 event holds one accepted Λ → n π⁰ → n γ γ)
                per["S4a_tm_eff"] = float(lt["matched"].sum() / nev)
                per["S4a_any_eff"] = float(lt["any"].sum() / nev)
                per["S4a_Rt_eff"] = float(lt["any_truthchain"].sum() / nev)
                per["S4a_tm_best_eff"] = float(lt["matched_best"].sum() / nev)
                summary.setdefault("lambda_flags", {})[str(p)] = {"events": lt["event"].tolist(), "matched": lt["matched"].tolist(),
                                                                 "matched_best": lt["matched_best"].tolist()}
            summary["per_momentum"][str(p)] = per
            # per-event and per-particle flags for the paired McNemar tests of 400_scoreboard.py --compare
            summary["event_flags"][str(p)] = {"events": events.tolist(), "all_separated": all_sep.tolist(),
                                              "particles": [[int(r["event"]), str(r["role"]), bool(r["separated"])] for r in arr]}
            print(f"{ds} {p:4d} GeV: " + "  ".join(f"{k}={v:.3f}" for k, v in per.items() if k.startswith("S0_") and k.endswith("_sep")))
        (PERF / f"truth-{args.experiment}-{ds}.json").write_text(json.dumps(summary))
    print("done")


if __name__ == "__main__":
    main()
