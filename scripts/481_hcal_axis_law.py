#!/usr/bin/env python3
"""The axis law of a tagged Hcal photon, fitted on the photon guns (Phase 6, loop v6, F4: calibrations on guns only).

Gun photons (D2c, D2 <= 50 GeV through Y9, row CAL6_D2_Y9): an energy law for a tagged Hcal photon from the rec hits around its own
projective line: Hcal rec hits within R of the line through the cluster (E_col) and crystal rec hits within R of it at the
crystal depth (E_crys). Forms: (h) E = b*E_col + c; (ch) E = a*E_crys + b*E_col + c. 1/E-weighted least squares.
The Hcal law on the leading cluster alone scatters ±24–36 % (a photon's Hcal shower is split into several clusters; the
leading one holds 45–60 % above 5 GeV). Writes space/perf/calib-hcal-axis-CAL6_D2_Y9.json (every R and form; 477 --axis-law
reads one).

Usage:  uv run scripts/481_hcal_axis_law.py
"""
import importlib.util, sys, json
from pathlib import Path
import numpy as np, uproot
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from zdc.config import repo_path
spec = importlib.util.spec_from_file_location("s477", repo_path("scripts", "477_crystal_scope.py")); s477 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s477)
e473, STOCK, C, HH, EH, Z_CRYS = s477.e473, s477.STOCK, s477.C, s477.HH, s477.EH, s477.Z_CRYS
np_ = s477.np_
BR = [f"{C}.energy", f"{C}.position.x", f"{C}.position.y", f"{C}.position.z", f"{C}.shapeParameters_begin", f"_{C}_shapeParameters"] + \
     [f"{HH}.{q}" for q in ("energy", "position.x", "position.y", "position.z")] + [f"{EH}.{q}" for q in ("energy", "position.x", "position.y", "position.z")]
RS = (30.0, 45.0, 60.0, 80.0)
rows = []   # (E_true, E_lead_law, {R: (E_crys, E_col)})
for ds in ("D2c_photon_low", "D2_photon"):
    for path in sorted(Path(f"/data/zdc-autoresearch/reco/CAL6_D2_Y9/{ds}").glob("*.edm4eic.root")):
        gev = float(path.name.split("_")[-2].replace("GeV", ""))
        if gev > 50: continue
        R = uproot.open(path)["events"].arrays(BR, library="ak")
        for ev in range(len(R)):
            E = np_(R, f"{C}.energy", ev).astype(float)
            if not len(E): continue
            P = e473.to_proton(*(np_(R, f"{C}.position.{q}", ev).astype(float) for q in "xyz"))
            cand = s477.tagged_candidates(E, P, np_(R, f"{C}.shapeParameters_begin", ev), np_(R, f"_{C}_shapeParameters", ev))
            lead = int(np.argmax(E))
            if lead not in cand: continue
            he = np_(R, f"{HH}.energy", ev).astype(float)
            hp = e473.to_proton(*(np_(R, f"{HH}.position.{q}", ev).astype(float) for q in "xyz")) if len(he) else np.zeros((0, 3))
            ce = np_(R, f"{EH}.energy", ev).astype(float)
            cp = e473.to_proton(*(np_(R, f"{EH}.position.{q}", ev).astype(float) for q in "xyz")) if len(ce) else np.zeros((0, 3))
            tx, ty = P[lead][0] / P[lead][2], P[lead][1] / P[lead][2]
            dh = np.hypot(hp[:, 0] - tx * hp[:, 2], hp[:, 1] - ty * hp[:, 2]) if len(he) else np.zeros(0)
            dc = np.hypot(cp[:, 0] - tx * cp[:, 2], cp[:, 1] - ty * cp[:, 2]) if len(ce) else np.zeros(0)
            rows.append((gev, STOCK["ag"] * E[lead] ** STOCK["bg"], {r: (float(ce[dc <= r].sum()), float(he[dh <= r].sum())) for r in RS}))
et = np.array([r[0] for r in rows]); el = np.array([r[1] for r in rows])
def report(name, pred):
    out = {}
    for g in sorted(set(et)):
        q = pred[et == g] / g
        out[g] = (np.median(q), 0.5 * (np.percentile(q, 84) - np.percentile(q, 16)))
    print(f"  {name:28s} " + "  ".join(f"{g:g}: {m:.2f}±{s:.2f}" for g, (m, s) in out.items()))
    return out
print(f"{len(rows)} gun photons with a tagged leading cluster")
report("Hcal law on the cluster", el)
res = {}
for r in RS:
    ec = np.array([x[2][r][0] for x in rows]); eh = np.array([x[2][r][1] for x in rows])
    w = 1.0 / et
    for form, X in (("h", np.c_[eh, np.ones_like(eh)]), ("ch", np.c_[ec, eh, np.ones_like(eh)])):
        coef, *_ = np.linalg.lstsq(X * w[:, None] ** 0.5, et * w ** 0.5, rcond=None)
        pred = X @ coef
        o = report(f"R {r:g} mm, form {form} {np.round(coef, 3).tolist()}", pred)
        res[f"{r:g}-{form}"] = {"coef": coef.tolist(), "per_energy": {str(g): list(map(float, v)) for g, v in o.items()}}
res["n"] = len(rows); res["fit_max_gev"] = 50.0; res["row"] = "CAL6_D2_Y9"
res["form"] = "h: E = b*E_col(R) + c; ch: E = a*E_crys(R) + b*E_col(R) + c (rec hits within R of the cluster's projective line)"
path = repo_path("space", "perf", "calib-hcal-axis-CAL6_D2_Y9.json")
json.dump(res, open(path, "w"), indent=1)
print("wrote", path)
