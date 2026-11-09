# ZDC autoresearch loop — version 6: the crystal-seeded ZDC photon finder

Read `zdc-setup.md` and `work-common.md` first; they define the names, paths, the start protocol, the ledger and the
reporting habits. `zdc-autoresearch-loop-v5.md` defines the ruler this phase keeps (the score, the selector `463`, the
fair-play rules F1–F6, the held-out halves); this file adds to it and overrides it where it says so.

Prepared at the user's order (2026-11-09, chat, D-user-41): *"Close phase 5 … Prepare phase 6 A crystal-seeded ZDC photon
finder (the biggest pool, the most uncertain)."* The phase starts on the user's start line, not before.

## Phase 6 — photons the hadronic ZDC does not resolve

**Goal:** find more Λ → nπ⁰ on the MSF events by finding the ZDC photons that the hadronic ZDC (the SiPM-on-tile Hcal)
loses, with the LYSO crystal section in front of it. Same score, selector and purity guard as Phase 5.

**The start:** Y9, the final Phase 5 row (EICrecon a15b0db6 + the Y2, Y5, Y9 patches + four run-time parameters;
`space/reports/phase5_msf.md`, Final state). On the search halves D6s it finds 1267 (9x275, 17.70 % of expected) + 219
(9x130, 3.06 %) = 1486, purity 26.7 %; reachable 43.6 % and 8.0 %.

### The target (Phase 5's measurements)

- The all-ZDC regime at 9x275 holds 2003 Λ per search half (28.0 % of expected); Y9 finds 750. A photon has no matched
  photon neutral for 1125 of them (15.7 % of expected), the largest software loss left. Of the missing photons (X9 and Y2,
  which share the ZDC clustering): 31 % sit in a cluster the neutron dominates, 26 % in no Hcal cluster at all, 27 % share
  a cluster with the other photon, 17 % have a pure cluster that the pairing passed over.
- Missed photons deposit a median 39 % of their energy (energy-equivalent) in the crystal section; found ones 21 %; the
  neutron about none. Photons in the window regime carry 5–50 GeV (median 17 GeV at 9x275).
- With one photon in B0, 303 Λ of 803 miss a photon at 9x275, mostly the ZDC one; 111 of those have no pure ZDC cluster.
- **The crystal section** (`EcalFarForwardZDC`): 20 × 20 LYSO crystals, 30 mm pitch, 70 mm deep (about 6 X0), at the Hcal
  face (z ≈ 35.72 m). Its reconstructed hits clip at 2 GeV per crystal (`dyRangeADC`, digitization: frozen by F2), so it
  locates a photon better than it measures it. Its island clustering joins hits within 50 cm (`localDistXY`, not a run-time
  parameter: a change in `src/detectors/ZDC/ZDC.cc`) and makes one cluster per event.
- Measured dead ends (do not repeat): crystal energy in front of a tagged Hcal cluster as a pairing term (good picks −14 … +1,
  Phase 5 runlog); ranking-only energy scales in the pairing (≤ +10); retuning Y5 / Y9's depth terms (optimum at the launched
  values).

### What carries over from version 5, unchanged

The score (N_found pooled over D6s_9x275 and D6s_9x130), the selector `463` with its purity guard, D6h held out with a
checkpoint every 5 tries, F1–F6 with `460` (on the MSF outputs, `-msf` and `--tree`) and `465` (each patch), the experiment
loop and reporting of version 5. `210` already credits a ZDC photon neutral through the crystal-section associations
(`EcalFarForwardZDCClusterAssociations`, matched by collection ID and index) when an output carries them.

### What changes

- **The template** adds `EcalFarForwardZDCRawHits` (F2: an experiment that reads a detector writes its raw hits),
  `EcalFarForwardZDCClusters` and `EcalFarForwardZDCClusterAssociations` (the scorer reads them).
- **F2b** compares the crystal raw hits too, so the base row and its R0 reference write them (Step 0).
- **F3 for crystal clusters.** `460`'s F3f checks that a ZDC photon neutral carries its Hcal clusters' energy; it skips the
  crystal clusters. A new `468` checks the same for the crystal clusters a photon neutral links (each linked crystal
  cluster's energy is in the photon's energy budget, two photons never share a crystal cluster), proven on a damaged control.
- **Calibration** of any crystal-seeded photon energy is fitted on guns only (F4): D2 (20–275 GeV) and, below 20 GeV, a
  ZDC photon gun D2c_photon_low (5, 10, 15 GeV; Q20 answered, D-user-42).
- **Git.** Phase 5's accepted patches are uncommitted. With `please-git` in Phase 6's start line, they are committed first as
  three commits (Y2, Y5, Y9, with their ledger lines) on `zdc-autoresearch/phase5` cut from a15b0db6, and the Phase 6 tries
  are commits on `zdc-autoresearch/phase6` cut from there, each with a revert commit when not accepted. Without `please-git`,
  tries are patches as in Phase 5. **Never push**, in any repository.

### Step 0 (before the first try)

| # | item | decisive outcome |
|---|---|---|
| 1 | **Scope study, offline.** Re-cluster the crystal rec hits at the crystal scale (an island clustering with an 8-neighbourhood, split at local maxima) on a probe of D6s_9x275 (X9's ZDC clustering is Y9's) and, per missing all-ZDC photon: a crystal cluster pure (≥ 0.8) for it? its crystal energy? the Hcal energy behind it in a narrow column (Hcal rec hits)? Then emulate a crystal-seeded photon hypothesis in the pairing (`473` / `475`'s method) with the energy from crystal + Hcal column. | A predicted gain in found Λ on the 9x275 search half, with the all-ZDC and mixed regimes' losses. **Below +50 pooled, the phase stops here** and the report says why (the user decides what next). |
| 2 | The low-energy ZDC photon gun D2c_photon_low (5, 10, 15 GeV, θ < 4 mrad, 1000 events each; Q20 answered A, D-user-42; generated at the Phase 5 close). | Its manifest entries in place; the crystal-seeded photon law is fitted on D2 and D2c together. |
| 3 | The base row MSF6_Y9 (Y9 with the Phase 6 template) on D6s and D6h; an R0 run with the Phase 6 template on D6s_9x275, CTL6_R0_crys, as F2b's reference (CTL5_R0_msf lacks the crystal raw hits, and `130` fails on differing branch sets). | MSF6_Y9 reproduces Y9 Λ by Λ (the template adds collections only); `460 --reference-dir {reco}/CTL6_R0_crys/D6s_9x275` PASS with F2b over the ZDC, B0 and crystal raw hits; every Phase 6 try's F2b then runs against MSF6_Y9. |
| 4 | `468` written and proven. | PASS on MSF6_Y9 (no crystal links) and on a crystal-seeded smoke build; FAIL on a control whose photon links a crystal cluster it does not carry, and on one where two photons share a crystal cluster. |
| 5 | `space/FROZEN` rewritten (this file, `468` and any new scorer frozen); the report `space/reports/phase6_crystal.md` and the deck `slides/phase6/`. | The hook refuses an edit to `468`. |

### Order of work (re-ranked after Step 0 item 1)

1. **Z1: crystal clustering at the crystal scale** (`ZDC.cc`: neighbourhood in crystal units, split at local maxima, energy
   shared by distance) **with crystal-seeded photon candidates** in the ZDC pairing: a crystal cluster with no tagged Hcal
   photon behind it becomes a photon hypothesis, its direction from the crystal cluster, its energy from the crystal energy
   plus the Hcal energy in a narrow column behind it (a gun-fitted law). Z1 alone changes no score (the neutrals do not read
   crystal clusters), so it is tried together with the candidates.
2. **Z2: crystal-seeded split of a neutron-led Hcal cluster** — where a crystal photon sits in front of a cluster the neutron
   dominates, the shallow Hcal energy in its column becomes the photon's.
3. **Z3: crystal-assisted energy for tagged Hcal photons** — the crystal energy in front added, with the gun-fitted law.
4. **Z4 onward:** free choice, each with a prediction line, ranked by the expected gain.

### Stop rules

As version 5 (the user stops it, the backlog is empty, or two checkpoints in a row bring no accepted gain), and Step 0's
own: no try runs if the scope study predicts less than +50 pooled.

### Reporting

As version 5: numbers from result files, timestamps from `date -u`, PNG plots, a deck `slides/phase6/` with a slide per
try and a diagram for each structural change; every chat line gives yield and purity per beam beside the reachable
43.6 % / 8.0 %.
