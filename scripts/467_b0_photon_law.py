#!/usr/bin/env python3
"""The B0 ECal photon energy law a·E_raw^b fitted on the B0 photon gun D2b_photon_B0 (Phase 5, D-user-40; loop v5 F4:
calibrations on guns only).

FarForwardNeutralsReconstruction gives every leading B0 cluster (≥ clusterEminB0Ecal) the photon energy
corrPower(E_raw, gammaScaleCorrCoeffB0Ecal) = a·E_raw^b; stock a = 0.99, b = 1.14. On the gun (one photon per event, so
every B0 deposit is the photon's or its secondaries') E_raw is the event's leading B0 cluster energy. Per gun energy the
peak of E_raw (a Gaussian fit around the median; the median if the fit fails) is taken against the true energy, and
log E_true = log a + b log E_peak is fitted with the peak errors — the method of 420 (whose functions are imported).
Printed: a, b with errors, and the residual peak of a·E_raw^b / E_true per energy for the refit and for the stock law.
Events without a B0 cluster ≥ the threshold (photons into the beam-pipe hole) are counted, not fitted.

Writes space/perf/calib-B0-<row>.json.
Usage: uv run scripts/467_b0_photon_law.py <row that reconstructed D2b_photon_B0> [--emin 1.0]
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import uproot

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import load_profile, repo_path  # noqa: E402

spec = importlib.util.spec_from_file_location("r420", repo_path("scripts", "420_refit_calibration.py"))
r420 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r420)
DS = "D2b_photon_B0"
STOCK = (0.99, 1.14)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("row")
    ap.add_argument("--emin", type=float, default=1.0, help="clusterEminB0Ecal (GeV)")
    args = ap.parse_args()
    prof = load_profile()
    pts, counts = [], {}
    for f in sorted((Path(prof.reco_root) / args.row / DS).glob("*.edm4eic.root")):
        sim = Path(prof.datasets_root) / DS / f.name.replace(".edm4eic.root", ".edm4hep.root")
        mc = uproot.open(sim)["events"].arrays(["MCParticles.PDG", "MCParticles.generatorStatus", "MCParticles.momentum.x",
                                                "MCParticles.momentum.y", "MCParticles.momentum.z"], library="ak")
        sel = (mc["MCParticles.PDG"] == 22) & (mc["MCParticles.generatorStatus"] == 1)
        e_true_ev = ak.to_numpy(ak.firsts(np.sqrt(mc["MCParticles.momentum.x"][sel] ** 2 + mc["MCParticles.momentum.y"][sel] ** 2
                                                  + mc["MCParticles.momentum.z"][sel] ** 2)))
        E = uproot.open(f)["events"]["B0ECalClusters.energy"].array(library="ak")
        lead = ak.to_numpy(ak.fill_none(ak.max(E, axis=1), 0.0))
        ok = lead >= args.emin
        counts[f.stem] = {"events": len(lead), "with_b0_cluster": int(ok.sum())}
        e_raw, e_true = lead[ok], e_true_ev[ok]
        pk = r420.peak(e_raw)
        if pk is None:
            continue
        pts.append({"file": f.stem, "E_true": float(np.median(e_true)), "E_raw_peak": pk[0], "E_raw_peak_err": float(pk[1]),
                    "n": pk[2], "e_raw": e_raw, "e_true": e_true})
    pts.sort(key=lambda r: r["E_true"])
    a, b, ea, eb, chi2, ndf = r420.fit(pts)
    res_fit, res_stock = r420.residuals(pts, a, b), r420.residuals(pts, *STOCK)
    out = {"row": args.row, "dataset": DS, "emin": args.emin, "a": a, "b": b, "a_err": ea, "b_err": eb, "chi2": chi2, "ndf": ndf,
           "points": [{k: v for k, v in p.items() if k not in ("e_raw", "e_true")} for p in pts], "counts": counts,
           "residual_peak_refit": res_fit, "residual_peak_stock": res_stock, "stock": STOCK}
    path = repo_path("space", "perf", f"calib-B0-{args.row}.json")
    path.write_text(json.dumps(out, indent=1))
    for p in pts:
        key = "%.0f" % p["E_true"]
        print(f"  E_true {p['E_true']:6.1f} GeV: leading B0 cluster peak {p['E_raw_peak']:.3f} ± {p['E_raw_peak_err']:.3f} GeV (n {p['n']}) "
              f"→ residual refit {res_fit[key]}, stock {res_stock[key]}")
    print(f"B0 photon law: a = {a:.4f} ± {ea:.4f}, b = {b:.4f} ± {eb:.4f}, χ² {chi2:.1f} / {ndf} (stock {STOCK}); counts {counts}")
    print("wrote", path)


if __name__ == "__main__":
    main()
