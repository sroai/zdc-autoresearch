#!/usr/bin/env python3
"""S5: Λ → nπ⁰ reconstruction on MSF events (D6a locally, D6b on the farm).

For one experiment's reconstruction of an MSF dataset: Λ candidates per 1000
events, the mass peak and σ, and the efficiency against MC-truth Λ whose three
daughters (n, γ, γ) reach the ZDC acceptance (θ < 4 mrad around the proton axis,
the gun's acceptance, and forward of the decay). Writes
{space}/perf/msf-<experiment>-<dataset>.json and prints the numbers.

Usage:
  uv run scripts/402_lambda_msf_metrics.py R0_stock D6a_local
  uv run scripts/402_lambda_msf_metrics.py R0_stock D6b_9x275 --reco-dir /volatile/eic/romanov/zdc-autoresearch/reco/R0_stock/9x275

The MC-truth selection follows submodules/meson-structure/analysis/zdc-lambda
(mc_decay.py): the Λ is the MCParticle with PDG 3122 from the primary vertex,
daughters by the parent links. Step 0 verifies the link field names against a
file (`MCParticles.daughters_begin/end`, `_MCParticles_daughters.index`).
"""
import argparse
import json
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, metrics_config, repo_path  # noqa: E402
from zdc.edm import binomial_error, fit_peak, read_collection, rotate_to_proton_frame  # noqa: E402

LAMBDA_PDG, NEUTRON_PDG, PHOTON_PDG = 3122, 2112, 22


def truth_lambda_in_acceptance(files, mcfg, theta_max_mrad=4.0):
    """Per event: True when a primary Λ exists whose n and two γ daughters are within θ < theta_max of the proton axis."""
    mc = read_collection(files, mcfg.collections.mc_particles,
                         ["PDG", "generatorStatus", "momentum.x", "momentum.y", "momentum.z", "daughters_begin", "daughters_end"])
    links = uproot.concatenate({str(f): "events" for f in files}, expressions=["_MCParticles_daughters.index"], library="ak")["_MCParticles_daughters.index"]
    tilt = mcfg.crossing_angle_rad
    result = []
    for ev in range(len(mc["PDG"])):
        pdg = ak.to_numpy(mc["PDG"][ev])
        lam = np.where(pdg == LAMBDA_PDG)[0]
        ok = False
        for i in lam:
            d0, d1 = int(mc["daughters_begin"][ev][i]), int(mc["daughters_end"][ev][i])
            kids = ak.to_numpy(links[ev][d0:d1])
            kpdg = pdg[kids]
            if sorted(kpdg.tolist()) != [PHOTON_PDG, PHOTON_PDG, NEUTRON_PDG] and not (NEUTRON_PDG in kpdg and np.sum(kpdg == 111) == 1):
                continue
            # π⁰ daughters are two generations down when the generator wrote the π⁰; follow one level if needed
            finals = []
            for k in kids:
                if pdg[k] == 111:
                    b, e = int(mc["daughters_begin"][ev][k]), int(mc["daughters_end"][ev][k])
                    finals += ak.to_numpy(links[ev][b:e]).tolist()
                else:
                    finals.append(int(k))
            px = ak.to_numpy(mc["momentum.x"][ev])[finals]
            py = ak.to_numpy(mc["momentum.y"][ev])[finals]
            pz = ak.to_numpy(mc["momentum.z"][ev])[finals]
            qx, qy, qz = rotate_to_proton_frame(px, py, pz, tilt)
            theta = np.arctan2(np.hypot(qx, qy), qz) * 1e3
            if len(theta) == 3 and np.all(theta < theta_max_mrad) and np.all(qz > 0):
                ok = True
                break
        result.append(ok)
    return np.array(result)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment")
    ap.add_argument("dataset")
    ap.add_argument("--reco-dir", help="override {reco_root}/<experiment>/<dataset>")
    ap.add_argument("--max-files", type=int)
    args = ap.parse_args()
    profile, mcfg = load_profile(), metrics_config()
    reco_dir = Path(args.reco_dir) if args.reco_dir else Path(profile.reco_root) / args.experiment / args.dataset
    files = sorted(reco_dir.glob("*.edm4eic.root"))[: args.max_files]
    if not files:
        sys.exit(f"no reconstruction under {reco_dir}")
    lam = read_collection(files, mcfg.collections.lambdas, ["mass"])
    nev = len(lam["mass"])
    masses = ak.to_numpy(ak.flatten(lam["mass"]))
    fit = fit_peak(masses, mcfg.windows.lambda_mass_gev, 0.1)
    truth = truth_lambda_in_acceptance(files, mcfg)
    refs = json.loads((repo_path("space", "perf", "references.json")).read_text()) if repo_path("space", "perf", "references.json").exists() else {}
    half = refs.get("lambda_mass_half_window", 0.03)
    reco_in_window = ak.to_numpy(ak.sum(np.abs(lam["mass"] - mcfg.windows.lambda_mass_gev) < half, axis=1) > 0)
    n_truth = int(truth.sum())
    n_both = int((truth & reco_in_window).sum())
    out = {
        "experiment": args.experiment, "dataset": args.dataset, "files": len(files), "events": nev,
        "S5_candidates_per_1000": 1000.0 * len(masses) / max(nev, 1),
        "S5_truth_in_acceptance": n_truth,
        "S5_eff_given_acceptance": n_both / max(n_truth, 1),
        "S5_eff_err": binomial_error(n_both, max(n_truth, 1)),
        "S5_reco_in_window_per_1000": 1000.0 * reco_in_window.sum() / max(nev, 1),
    }
    if fit:
        out["S5_mass_mu"], out["S5_mass_sigma"] = fit[0], fit[1]
    perf = repo_path("space", "perf")
    perf.mkdir(parents=True, exist_ok=True)
    (perf / f"msf-{args.experiment}-{args.dataset}.json").write_text(json.dumps(out, indent=1))
    for k, v in out.items():
        print(f"  {k:32s} {v}")


if __name__ == "__main__":
    main()
