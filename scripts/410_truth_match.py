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
         f"{c.zdc_cluster_assoc}.weight", r.assoc_rec_index, r.assoc_sim_index],
        library="ak")
    mc = {k: arrays[f"{c.mc_particles}.{k}"] for k in ["PDG", "generatorStatus", "daughters_begin", "daughters_end"]}
    links = arrays[r.mc_daughters_index]
    cl_e = arrays[f"{c.zdc_clusters}.energy"]
    cl_x, cl_y, cl_z = (arrays[f"{c.zdc_clusters}.position.{a}"] for a in "xyz")
    w, rec, sim = arrays[f"{c.zdc_cluster_assoc}.weight"], arrays[r.assoc_rec_index], arrays[r.assoc_sim_index]
    # neutrals: which clusters are tagged photons (PDG 22) — through the neutrals' cluster relation when present
    try:
        neutral_pdg = tree[f"{c.zdc_neutrals}.PDG"].array(library="ak")
        neutral_cl = tree[f"_{c.zdc_neutrals}_clusters.index"].array(library="ak")
        neutral_cl_begin = tree[f"{c.zdc_neutrals}.clusters_begin"].array(library="ak")
        neutral_cl_end = tree[f"{c.zdc_neutrals}.clusters_end"].array(library="ak")
        have_neutrals = True
    except Exception:
        have_neutrals = False

    targets = targets_for(dataset, mc, links, tm)
    rows = []   # one per target particle: event, role, purity, containment, separated, best_E, best_x, best_y, best_z, tagged_gamma
    for ev, idx in enumerate(targets):
        if not idx:
            continue
        we, re_, si = ak.to_numpy(w[ev]), ak.to_numpy(rec[ev]), ak.to_numpy(sim[ev])
        energies = ak.to_numpy(cl_e[ev])
        gamma_clusters = set()
        if have_neutrals:
            npdg = ak.to_numpy(neutral_pdg[ev]); ncl = ak.to_numpy(neutral_cl[ev])
            nb, ne = ak.to_numpy(neutral_cl_begin[ev]), ak.to_numpy(neutral_cl_end[ev])
            for j in range(len(npdg)):
                if npdg[j] == tm.photon_pdg:
                    gamma_clusters.update(ncl[nb[j]:ne[j]].tolist())
        roles = ["n", "g1", "g2"] if len(idx) == 3 else (["g1", "g2"] if len(idx) == 2 else ["p"])
        for role, i in zip(roles, idx):
            mask = si == i
            if not mask.any():
                rows.append((ev, role, 0.0, 0.0, False, 0.0, 0.0, 0.0, 0.0, False))
                continue
            contrib = we[mask] * energies[re_[mask]]        # energy of the particle in each cluster
            best = int(np.argmax(contrib))
            cl = int(re_[mask][best])
            purity = float(we[mask][best])
            containment = float(contrib[best] / contrib.sum()) if contrib.sum() > 0 else 0.0
            separated = purity >= tm.purity_min and containment >= tm.containment_min
            rows.append((ev, role, purity, containment, separated, float(energies[cl]),
                         float(cl_x[ev][cl]), float(cl_y[ev][cl]), float(cl_z[ev][cl]), cl in gamma_clusters))
    return len(targets), rows


def main():
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
            nev, rows = match_file(f, ds, mcfg)
            if not rows:
                print(f"{ds} {p} GeV: no target particles found (check targets_for and the relation names)")
                continue
            arr = np.array([(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]) for r in rows],
                           dtype=[("event", "i4"), ("role", "U2"), ("purity", "f4"), ("containment", "f4"), ("separated", "?"),
                                  ("E", "f4"), ("x", "f4"), ("y", "f4"), ("z", "f4"), ("tagged_gamma", "?")])
            np.savez_compressed(outdir / f"{f.stem}.npz", table=arr)
            per = {}
            for role in sorted(set(arr["role"])):
                sel = arr[arr["role"] == role]
                per[f"S0_{role}_sep"] = float(sel["separated"].mean())
                per[f"S0_{role}_purity_mean"] = float(sel["purity"].mean())
                per[f"S0_{role}_tagged_gamma"] = float(sel["tagged_gamma"].mean())
            events = np.unique(arr["event"])
            all_sep = np.array([bool(arr[arr["event"] == e]["separated"].all()) for e in events])
            per["S0_all_sep"] = float(all_sep.mean())
            per["events_with_targets"] = int(len(events))
            per["events"] = int(nev)
            summary["per_momentum"][str(p)] = per
            summary["event_flags"][str(p)] = {"events": events.tolist(), "all_separated": all_sep.tolist()}
            print(f"{ds} {p:4d} GeV: " + "  ".join(f"{k}={v:.3f}" for k, v in per.items() if k.startswith("S0_") and k.endswith("_sep")))
        (PERF / f"truth-{args.experiment}-{ds}.json").write_text(json.dumps(summary))
    print("done")


if __name__ == "__main__":
    main()
