#!/usr/bin/env python3
"""What the Λ candidates in the ±30 MeV window are made of, when they are not the true Λ → nπ⁰ (the purity's other 70 %).

For one row and one MSF dataset, every event whose ReconstructedLambdas candidate lies in the scoring window is put in one
class by the event's true Λ (210's truth_event: nπ⁰, pπ⁻, interacted in material, undecayed, Dalitz) and, for nπ⁰
events, by 210's verdict (found, or the loss reason) and the Λ's regime (where its n, γ, γ deposit, 210's homes). For each
of the candidate's three neutrals (one neutron, two photons) the cluster energy is split by the MC particle that made
it (the cluster associations, weight × cluster energy), and that particle is labelled by its family:
  Λ→n, Λ→γ (π⁰ photons), Λ→p, Λ→π⁻, Λ→material (the products of a Λ that interacted), Λ (undecayed, hit the detector),
  K⁺ (the kaon of the Sullivan process and its products), e' (the scattered electron), other.
A neutral's label is the family with the largest share of its energy (with the share).

Reads the dataset's simulation files (MCParticles) and the row's reconstruction (Λ, neutrals, clusters, associations);
uses 210's own truth and matching code. Writes space/perf/window-candidates-<row>-<dataset>.json.

Usage: uv run scripts/483_window_candidates.py D6s_9x275 --row Z8_hcal_axis_law [--files msf_9x275_1000evt_0001]
"""
import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from zdc.config import dataset_dir, load_profile, metrics_config, reco_dir  # noqa: E402
from zdc.edm import collection_ids  # noqa: E402

spec = importlib.util.spec_from_file_location("m210", REPO / "scripts" / "210_msf_lambda_regimes.py")
m210 = importlib.util.module_from_spec(spec); spec.loader.exec_module(m210)

CLUSTERS = {"HcalFarForwardZDCClusters", "EcalFarForwardZDCClusters", "B0ECalClusters", "EcalEndcapPClusters"}
REACH = {"ZDC", "B0", "EEMCP"}


def family_labels(a, ev, lams):
    """Label every MCParticle of the event by its family (see the module docstring)."""
    pdg = ak.to_numpy(a["MCParticles.PDG"][ev]); st = ak.to_numpy(a["MCParticles.generatorStatus"][ev])
    db = ak.to_numpy(a["MCParticles.daughters_begin"][ev]); de = ak.to_numpy(a["MCParticles.daughters_end"][ev])
    dl = ak.to_numpy(a["_MCParticles_daughters.index"][ev])
    kids = lambda i: dl[db[i]:de[i]].tolist()
    lab = np.array(["other"] * len(pdg), dtype=object)

    def paint(root, name):
        stack = [root]
        while stack:
            j = stack.pop()
            if lab[j] == "other":
                lab[j] = name
                stack.extend(kids(j))
    for i in np.flatnonzero(((st == 1) | (st == 2)) & (pdg == 3122)):
        mode = next((l["mode"] for l in lams), "other")
        d = kids(i)
        for k in d:
            p = int(pdg[k])
            if mode in ("npi0", "npi0_dalitz"):
                paint(k, "Λ→n" if p == 2112 else "Λ→γ")
            elif mode == "ppi":
                paint(k, "Λ→p" if p == 2212 else "Λ→π⁻")
            else:
                paint(k, "Λ→material")
        lab[i] = "Λ"
    for i in np.flatnonzero(st == 1):
        if lab[i] == "other" and int(pdg[i]) in (321, 11):
            paint(i, "K⁺" if pdg[i] == 321 else "e'")
    return lab


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--row", required=True)
    ap.add_argument("--files", nargs="*")
    args = ap.parse_args()
    prof = load_profile(); mcfg = metrics_config()
    win_c, win_h = float(mcfg.windows.lambda_mass_gev), float(mcfg.windows.lambda_mass_half_window_gev)
    purity_min = float(mcfg.truth_match.purity_min)
    files = sorted(dataset_dir(prof, args.dataset).glob("*.edm4hep.root"))
    if args.files:
        files = [f for f in files if f.name.split(".")[0] in args.files]
    classes, neutron_by_class, photon_by_class, examples = Counter(), defaultdict(Counter), defaultdict(Counter), defaultdict(list)
    n_window, n_events = 0, 0
    for f in files:
        t = uproot.open(f)["events"]
        a = m210.mc_arrays(t)
        sa = t.arrays(m210.sim_branches(t), library="ak")
        rp = reco_dir(prof, args.row, args.dataset) / f.name.replace(".edm4hep.root", ".edm4eic.root")
        ra, cid, ne, _ = m210.reco_arrays(rp, ["ZDC", "B0", "EEMCP"])
        assert ne == t.num_entries
        ids = collection_ids(rp)
        rt = uproot.open(rp)["events"]
        have = m210.leaf_names(rt)
        cl_e = {ids[c]: rt[f"{c}/{c}.energy"].array(library="ak") for c in CLUSTERS if c in ids and f"{c}.energy" in have}
        gid = {v: k for k, v in cid.items()}
        for ev in range(t.num_entries):
            m = ak.to_numpy(ra["ReconstructedLambdas.mass"][ev])
            inw = np.flatnonzero(np.abs(m - win_c) < win_h)
            if not len(inw):
                continue
            n_window += 1
            lams, owner = m210.truth_event(a, ev)
            res = m210.reco_event(ra, ra, cid, ev, lams, owner, purity_min, win_c, win_h,
                                  {"photon_ratio": {"ZDC": [], "B0": [], "EEMCP": []}})
            mode = lams[0]["mode"] if lams else "no Λ"
            if mode == "npi0":
                if res[0]["matched"]:
                    classes["Λ → nπ⁰, found"] += 1
                    continue
                dep = m210.deposits_event(sa, ev, owner)
                homes = []
                for r in range(3):
                    eq = {g: dep[g].get(lams[0]["owner_base"] + r, 0.0) for g in m210.GROUPS}
                    b = max(eq, key=eq.get)
                    homes.append(b if eq[b] >= 0.5 else "none")
                if homes[0] != "ZDC":
                    reg = "neutron not in the ZDC"
                elif "none" in homes[1:]:
                    reg = f"{homes[1:].count('none')} photon(s) in no calorimeter"
                elif all(h in REACH for h in homes[1:]):
                    reg = "reachable"
                else:
                    reg = "a photon in the LFHCAL"
                cls = f"Λ → nπ⁰, not found: {reg} ({res[0]['reason']})"
            else:
                cls = {"ppi": "Λ → pπ⁻", "other": "Λ interacted in material", "undecayed": "Λ undecayed",
                       "npi0_dalitz": "Λ → nπ⁰, π⁰ Dalitz"}.get(mode, mode)
            classes[cls] += 1
            lab = family_labels(a, ev, lams)
            j = int(inw[0])
            lb, le = int(ra["ReconstructedLambdas.particles_begin"][ev][j]), int(ra["ReconstructedLambdas.particles_end"][ev][j])
            li = ak.to_numpy(ra["_ReconstructedLambdas_particles.index"][ev]); lc = ak.to_numpy(ra["_ReconstructedLambdas_particles.collectionID"][ev])
            desc = []
            for x in range(lb, le):
                grp = gid.get(int(lc[x])); k = int(li[x])
                col = m210.NEUTRALS[grp]
                pdg = int(ra[f"{col}.PDG"][ev][k])
                cb, ce = int(ra[f"{col}.clusters_begin"][ev][k]), int(ra[f"{col}.clusters_end"][ev][k])
                ci = ak.to_numpy(ra[f"_{col}_clusters.index"][ev]); cc = ak.to_numpy(ra[f"_{col}_clusters.collectionID"][ev])
                comp = Counter()
                for an in (m210.assoc_names(grp) if grp in m210.ASSOC else []):   # LFHCAL: no associations written
                    if f"{an}.weight" not in ra.fields:
                        continue
                    w = ak.to_numpy(ra[f"{an}.weight"][ev]); rc = ak.to_numpy(ra[f"_{an}_rec.index"][ev])
                    rcid = ak.to_numpy(ra[f"_{an}_rec.collectionID"][ev]); si = ak.to_numpy(ra[f"_{an}_sim.index"][ev])
                    for y in range(cb, ce):
                        e_cl = float(cl_e[int(cc[y])][ev][int(ci[y])]) if int(cc[y]) in cl_e else 1.0
                        sel = (rcid == int(cc[y])) & (rc == int(ci[y]))
                        for ww, s in zip(w[sel], si[sel]):
                            comp[lab[int(s)]] += float(ww) * e_cl
                tot = sum(comp.values())
                top = comp.most_common(1)[0] if tot > 0 else ("no association", 0.0)
                desc.append({"pdg": pdg, "group": grp, "label": top[0], "share": round(top[1] / tot, 2) if tot > 0 else 0.0})
            n_d = [d for d in desc if d["pdg"] == 2112]
            g_d = [d for d in desc if d["pdg"] == 22]
            if n_d:
                neutron_by_class[cls][n_d[0]["label"]] += 1
            for d in g_d:
                photon_by_class[cls][f"{d['group']}: {d['label']}"] += 1
            if len(examples[cls]) < 5:
                examples[cls].append({"file": f.name, "event": ev, "mass": round(float(m[j]), 4), "daughters": desc})
        n_events += t.num_entries
    out = {"dataset": args.dataset, "row": args.row, "events": n_events, "events_in_window": n_window,
           "classes": dict(classes.most_common()),
           "neutron_family": {k: dict(v.most_common()) for k, v in neutron_by_class.items()},
           "photon_family": {k: dict(v.most_common()) for k, v in photon_by_class.items()},
           "examples": examples}
    p = REPO / "space" / "perf" / f"window-candidates-{args.row}-{args.dataset}.json"
    p.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(json.dumps({k: out[k] for k in ("events", "events_in_window", "classes")}, indent=1, ensure_ascii=False))
    print("wrote", p)


if __name__ == "__main__":
    main()
