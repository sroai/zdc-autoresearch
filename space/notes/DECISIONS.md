# Decisions

One entry per decision that constrains later work. `D-user-<n>` quotes the
user; `D-default-<n>` records a default the agent took (DECIDE in
`work-common.md`) and is listed in the phase report under "Defaults you may
veto". Edit an entry when the decision changes; never add a second one for
the same decision. Numbers stay in the reports.

- D-user-1 (2026-11-04, user, chat): "When we'll work on autoresearch only ZDC data must change." → the frozen list in `zdc-setup.md` and the ZDC-owned file list in `docs/zdc-problem.md`.
- D-user-2 (2026-11-04, user, chat): "I certainly want to stick to phases and our model" → the phase-gated protocol of `work-common.md`, not a flat keep/revert loop.
- D-user-3 (2026-11-04, user, chat): "start our work with building a dataset … something like machine gun with pions to zdc … All gates such as copybara, benchmarks etc setup as phase0." → Phase 0 of the loop file; the π⁰ gun D1 is the "pions" default (charged pions are not a Λ daughter; a π± gun is an optional dataset the user may add).
- D-default-1 (2026-11-04, agent, scaffold): the pinned image is `eicweb/eic_xl:26.11.0-stable` (newest stable on 2026-11-04; the local `25.10.4` predates the square-tile ZDC). Digest recorded at Step 0.
- D-default-2 (2026-11-04, agent, scaffold): the primary metric is S4a (Λ-gun efficiency), with S3 (neutron gun) and G4 (non-ZDC byte-identical) as guards and S1 as the diagnostic; D6b confirms and never selects. Evidence: the physics goal is Λ → nπ⁰; the gun is cheap enough for every experiment; MSF at scale is not.
- D-default-3 (2026-11-04, agent, scaffold): parameter experiments run as `-P` overrides on the pinned build (no rebuild); code experiments as patches under `space/notes/patches/` with `{git}` off.
- D-default-4 (2026-11-04, agent, scaffold, from the expert review): the selector is S0, truth-matched separation efficiency (purity ≥ 0.8, containment ≥ 0.5) on the Λ gun; S4a is reported against the truth-cluster ceiling Rt and never selects. Evidence: `docs/expert-review-v1.md` §2.2 (S4a is capped by LambdaReconstruction's IP-pointing π⁰ window and gameable through calibration and window parameters). Replaces D-default-2.
- D-default-5 (2026-11-04, agent, scaffold): the guns run on `epic_zdc_lyso_sipm` (LYSO ECal + SiPM HCal, as in every physics sample), the SiPM-only configuration being a cross-check; Phase 0 checkpoint question 1 lets the user veto. Evidence: review §2.5.
- D-default-6 (2026-11-04, agent, scaffold): `LambdaReconstruction` source and its four parameters are frozen through Phase 3; checkpoint question 3 may open them. Evidence: review §4.2 loopholes 1 and 3.
- D-default-7 (2026-11-04, agent, scaffold): R1 is the PR's three-file diff applied to the pin, never the PR commit (base 14 commits behind). Evidence: review §3.
- D-default-8 (2026-11-04, agent, scaffold): the noise band is replaced by a paired test on identical events (McNemar / event bootstrap) validated on three seeds at Step 0, plus the held-out D1h/D4h at checkpoints. Evidence: review §2.6, §4.3.
- D-default-9 (2026-11-04, agent, scaffold): the benchmark plot scripts run from patched copies under `scripts/700_benchmarks/` (EICrecon main collection names); the submodule stays frozen; the rename is a finding for upstream. Evidence: review §3.
- D-default-10 (2026-11-04, agent, scaffold): G1 to G3 are judged against numeric limits the user sets at the Phase 0 checkpoint, not against the agent's own "explained by a mechanism". Evidence: review §4.2 loophole 4.
- D-default-11 (2026-11-04, agent, scaffold): the XY neighbour distances are run as code-tier builds at the three settings that matter (below the 24.4 mm subcell pitch, 3×3, 5×5); exposing them as a parameter is optional (Step 0 item 7). Evidence: review §2.1 (step function), §3 (units convention).
