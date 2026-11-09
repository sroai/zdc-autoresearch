# Phase 2 findings ledger

Append-only. Full entries; one line each in `FINDINGS.md`.

## F9 — the IDOLA vertex iteration runs away for decays far from the IP (OPEN, measured 2026-11-05)
- Where: `src/algorithms/reco/LambdaReconstruction.cc:74-99` (`reconstruct_from_triplet`): each iteration sets
  `vtx = lambda.Vect() * (f * m_zMax / lambda.Z())`, with `lambda` summed from directions `(x_i − vtx).Unit()` of the
  *current* vertex.
- Defect: the vertex is placed along a Λ direction that itself depends on the vertex. For decays near the ZDC the
  feedback diverges transversely: with ideal inputs (true energies, true impact points) on D4 at 100 GeV the fitted
  vertex z is within ±25 mm of the truth in 68 % of events, but 34 % of events end with the vertex metres off in x/y
  (e.g. true (51, −27, 34143) mm, fitted (21184, −12102, 34227) mm) and a γγ mass of 1–100 MeV instead of 135 MeV.
- Why it is latent today: the step-3 π⁰ window on IP-pointing photons (F4) admits only decays within ~3–4 m of the IP,
  where the iteration converges; F4 hides F9. Any vertex-aware pairing that lets distant decays reach the iteration
  (backlog B9d) exposes it: running the pin's iteration first gives 0.62–0.86 of accepted D4 events with ideal inputs,
  where 1.00 is possible.
- Fix measured offline (`scripts/414_lambda_ceiling_variants.py`, pairing `vertex_fixed`): the Λ comes from the IP, so
  its direction is the momentum-weighted centroid of the impact points (Σ p_i x_i / Σ p_i L_i), independent of the
  vertex; only the depth is unknown and θ_γγ grows monotonically with it → bisection. Ideal inputs: 1.000 of accepted
  D4 events at every momentum (= the geometric acceptance per thrown Λ, 1.6–32.6 %). With the current best's measured
  single-particle resolution and perfect separation: 0.73 / 0.74 / 0.79 / 0.83 / 0.82 / 0.84 / 0.85 / 0.85 of accepted
  events (100–275 GeV), i.e. 1.2 / 3.4 / 7.1 / 11.8 / 16.1 / 20.7 / 24.5 / 27.8 % per thrown Λ → nπ⁰; with 5× the
  measured position errors 0.55 / 0.63 / 0.63 at 100 / 175 / 275 GeV (20.7 % per thrown at 275).
- Evidence: `space/perf/lambda-ceiling-variants-P1b_R0_thr.json`, `space/perf/lambda-gun-acceptance.json`.
- Severity: high for any Λ improvement beyond F4's cap (it is the next wall after the preselection). Owner: EICrecon
  issue/PR together with F4 (vertex-aware pairing with the stable vertex), Phase 3 Λ family.

- Status 2026-11-06: OPEN, addressed in part by eic/EICrecon#3063 (open; removes the mass windows and runs the IDOLA iteration on every triplet, so F9 is no longer latent). `414`'s `vertex` pairing is the pre-registered prediction for the PR: 0.50–0.78 of accepted D4 events with P1b's resolution against 0.73–0.85 with the stable vertex (`try1-assessment.md`, section 5). B9d is the fix on top of the PR.
