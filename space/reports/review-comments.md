# Review comments — drafts for the user to post

Three drafts for the open and merged PRs of the ZDC Λ package (Baptiste Fraïsse). Every number is cited
to its file in this repository; the user decides whether and where to post. Pin: EICrecon `e5e2a60c`;
single-threaded reconstructions of the same simulated events (D4: Λ → nπ⁰ gun, 100–275 GeV, 2000 events
per momentum, all three daughters inside 4 mrad; D6a: MSF 9x275 and 9x130 slices). "Per thrown" means
per thrown Λ → nπ⁰ (× the geometric acceptance of `scripts/413_lambda_gun_acceptance.py`).

---

## PR 3114 (photon box 110 / 22 mm, merged) — necessary, not sufficient

Measured on the pin with the box as a parameter change (reference R2; `configs/experiments/R2_pr3114.yaml`):

- Single photons (D2, 20–275 GeV): the γ tag goes from 0.03 to 0.87–0.98 — the stock box rejected
  almost every ZDC photon (`space/EXPERIMENTS.md`, entry R2).
- Λ → nπ⁰ on stock clustering: still 0 truth-matched Λ at every momentum (`space/perf/truth-R2_pr3114-D4_lambda.json`,
  `S4a_tm_eff`); MSF 9x275: 1.0 candidate per 1000 events, none matched to a true Λ in acceptance
  (`space/perf/msf-R2_pr3114-D6a_9x275.json`).
- Why: on the stock 3×3 clustering 87–98 % of the Λ's photon pairs end in one cluster
  (`space/reports/phase1_dissection.md`, decay-position view), and a box can tag only a photon that has a
  cluster of its own. With the box on the best 3×3 clustering found (lower seed and size thresholds, L01):
  +25 events gained, 0 lost, still 0.04 % per thrown (`space/EXPERIMENTS.md`, entry L01; `space/perf/headline.csv`).
- Even with a vertex that does not run away (see the PR 3063 comment), the stock clustering plus this box
  allows about 0.17 % per thrown (`space/perf/lambda-offline-R2_pr3114.json`, `vertex_fixed_tagged`).

Suggested text: the box fix is right and needed; the "strongly improves Λ reconstruction" claim holds
only together with a clustering that separates the photons (PR 3064 or a successor) and a Λ chain that
accepts distant decays (PR 3063 plus a stable vertex).

---

## PR 3063 (Λ mass windows removed, IDOLA on every triplet) — the first Λs on stock clustering

Measured as R3 = R2 + this PR's one-file diff on the pin (`space/notes/patches/R3_pr3063.patch`, head 364a310a;
`configs/experiments/R3_pr3063.yaml`), same D4 events as R2:

- It works: truth-matched Λ in the fixed window |m − m_Λ| ≤ 30 MeV go from 0 to 9 / 21 / 26 / 27 / 25 / 24 / 19 / 11
  of 2000 at 100–275 GeV, 0.17 % per thrown Λ → nπ⁰ (mean), with 0 events lost; paired McNemar z = 3.0–5.2 per
  momentum (`space/perf/lambda-paired-R3_pr3063-vs-R2_pr3114.json`). Untruthful candidates in the window: 4 events
  in 16000 (same file). Non-ZDC collections identical on 62 DIS files (G4, `space/perf/gate-evidence.json`).
- Why the cut had to go: the removed π⁰ window on IP-pointing momenta is the cap the program measured (finding F4):
  with ideal inputs only 0–6.9 % of accepted Λ decays pass it (0 at 100–125 GeV), because the photons of a decay
  tens of metres downstream do not point to the IP (`space/perf/lambda-ceiling-variants-P1b_R0_thr.json`, `stock_ideal`).
- The IDOLA iteration runs away transversely for distant decays (finding F9): with ideal inputs it keeps 62 / 76 / 83 /
  86 % of accepted decays at 100 / 150 / 200 / 275 GeV, where a vertex that cannot run away keeps 100 % (`414`).
  On today's clusters this costs little: a stable vertex built into the same chain (B9d: the Λ slope Σ p_i x_i /
  Σ p_i z_i from the IP, the depth by bisection on the γγ opening angle) adds 2 events over this PR in 16000
  (`space/perf/lambda-paired-B9d_stable_vertex-vs-R3_pr3063.json`). It matters once the clustering separates the photons.
- `LambdaReconstruction` reads the neutron's position from `getClusters(0)`, which for the ZDC neutral is the event's
  first cluster (every cluster is linked to it), not its leader; offline, the leader keeps 20–57 % more Λs with
  the stable vertex (finding F10, `space/perf/lambda-neutron-position-*.json`). A one-line change
  (`n_in.getReferencePoint()`, which the factory aims at the leader) is suggested. Measured in EICrecon on top of
  this PR (B9e, the same 16000 Λ-gun events): 195 truth-matched Λ against 162 (+20 %; 55 gained, 22 lost; 0.221 %
  against 0.171 % per thrown Λ → nπ⁰), mass σ 0.0152 against 0.0170 GeV, candidate rate on MSF unchanged
  (`space/perf/lambda-paired-B9e_neutron_leader-vs-R3_pr3063.json`); no single momentum reaches 3σ, pooled z +3.76.
- MSF 9x275 (5000 events): 22.0 Λ candidates per 1000 events (R2: 1.0), 4.4 per 1000 inside the 30 MeV window,
  and none of the 23 true Λ → nπ⁰ with all three daughters in the ZDC acceptance is reconstructed
  (`space/perf/msf-R3_pr3063-D6a_9x275.json`). On physics events the always-a-candidate output is background
  until the clustering separates the photons; a quality flag (the χ² the PR already computes) on the candidate
  would let analyses cut it.

Suggested text: the change is right and is what makes the ZDC Λ appear at all on the current clustering (on the gun);
please store the χ² with the candidate so MSF analyses can reject the combinatorial ones, and consider the neutron position fix (F10) in the same PR; the vertex iteration is worth hardening before the
clustering improves.

---

## PR 3064 (clustering and calibration) — the dissection, and what the Λ yield says

- The six PR parameters taken apart one at a time on the pin (`space/reports/phase1_dissection.md`): the
  XY neighbour distance below the subcell pitch makes every DIS cluster a single column (φ at ±180° and
  single-column fraction 1.000), which is the review finding of 2026-10-30; the lower seed and size
  thresholds alone give the best all-three separation of the program with no event lost.
- The calibration coefficients are off this clustering's own refit by 7σ (γ a) to 40σ (γ b) (F6).
- New since then: with a stable vertex (offline, each row's own refit calibration), the PR's clustering
  carries the most Λs: 3.4 % per thrown (R1) and 4.0 % with the layer range back at 1 (P1d), against
  0.56 % for the best 3×3 clustering and 0.27 % for stock (`space/perf/headline.csv`,
  `S4o_vertex_fixed_refit`; paired against the best 3×3 row z = 43 and 48,
  `space/perf/lambda-offline-compare-*-vs-P1b_R0_thr-vertex_fixed_refit.json`). With EICrecon's own photon tags
  and neutron (no truth help): 1.10 % per thrown against 0.17 % for stock + PR 3114.
- With main's photon box (PR 3114, 110 / 22 mm instead of this PR's 150 / 12) the in-EICrecon Λ yield stays
  0.40 % per thrown (0.395 against 0.405 %, R1p vs R1 paired on the same events), while untruthful Λ candidates
  in the 30 MeV window halve at 250–275 GeV (z −3.3, −5.4) and γ-tagged neutrals per Λ event fall from 4.9 to 2.4
  (`space/perf/lambda-paired-R1p_pr3064_3114-vs-R1_pr3064.json`, `space/EXPERIMENTS.md` entry R1p): rebasing onto
  main does not cost the PR its Λ.
- The corrected photon-tag numbers (the program's truth matcher was fixed for the neutron that lists every cluster):
  on this PR's clustering 47 % of single neutrons (D3, mean over 20–275 GeV) get a best cluster tagged as a photon
  (`space/perf/metrics-R1_pr3064.json`, `S3_mistag_rate_mean`); the stock clustering 0 %.
- So the column clusters are pure enough to make Λs once the chain handles distant decays, while they fail
  the cluster-shape expectations for hadronic showers. The program's next question is whether a clustering
  can keep the photon purity without single-column clusters (`space/QUESTIONS.md`, Q16).
