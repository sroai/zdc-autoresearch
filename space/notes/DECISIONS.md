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
