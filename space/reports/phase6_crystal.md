# Phase 6 — the crystal-seeded ZDC photon finder

Loop: `zdc-autoresearch-loop-v6.md` (prepared under D-user-41, started 2026-11-09T04:27Z on the user's start line, no
`please-git`: tries are patches under `space/notes/patches/`). Deck: `slides/phase6/` (Step 0 item 5).

## Summary

**Phase 6 CLOSED 2026-11-09T19:40Z at the user's order (D-user-45). Final row Z8_hcal_axis_law: 1946 Λ → nπ⁰ found on
the search halves (start Y9 1486, +31 %), 1865 on the held-out halves (Y9 1411, +32 %), purity 30.9 % / 30.1 %, −t σ68
0.114 / 0.118 GeV². Next: Phase 7, the accumulated changes as EICrecon pull requests (`zdc-autoresearch-loop-v7.md`,
prepared). Section Final state lists the code and parameters.**

**Run 2 (2026-11-09T13:13Z–15:21Z) ended for review: the backlog of tries with an emulated gain ≥ +30 is empty. Current best Z8_hcal_axis_law (ACCEPTED 14:37Z: 1946 found on the search halves, z +4.88 over Z7; Z7 ACCEPTED 13:50Z, z +7.72 over Z6); checkpoint 2 REPRODUCES on the held-out halves (1865 found vs Y9 1411, z +18.03; vs Z6 1703, z +10.37).** Run 1 (ended 08:19Z) had six tries since Step 0: Z1b, Z2, Z4, Z5 ACCEPTED, Z1
INCONCLUSIVE, Z6 REJECTED by the selector. The user answered both open questions: F1d of uncommitted code tries is read
from `478` on the as-built tree (Q21 A, D-user-43), so none of the tries is foul; and **Z6 is the base** (Q22 D,
D-user-44): it keeps 1797 of Z5's 1826 found Λ and measures −t better than at the start of the phase. Checkpoint 1
REPRODUCES on the held-out halves, and so does Z6. Z6 adds crystal-seeded photons to the ZDC Λ pairing (the LYSO crystal
section clustered at the crystal scale; the photon's energy from the crystal energy and the Hcal column behind it, a law
fitted on photon guns), offers that energy to tagged Hcal photons as a competing hypothesis (Z5), and takes such a
photon's Hcal column out of the neutron (Z6), and charges a tagged Hcal photon close to the neutron core an isolation
term, which keeps neutron shower fragments from being picked as the second photon (Z7), and lets a tagged Hcal photon
take the axis law's energy (crystal and Hcal rec hits around its own line, fitted on photon guns), which repairs photon
energies that a split Hcal shower reads low (Z8). Plots: `space/plots/phase6/` (`scripts/702_phase_plots.py 6`).

| Λ → nπ⁰ found, per expected (yield) | Y9 (start) | Z5 | Z6 (base, D-user-44) | Z7 | **Z8 (current best)** | reachable |
|---|---|---|---|---|---|---|
| 9x275, search half | 1267 (17.70 %) | 1574 (21.98 %) | 1547 (21.61 %) | 1628 (22.74 %) | **1688 (23.58 %)** | 43.6 % |
| 9x275, held-out half | 1206 (16.84 %) | 1520 (21.23 %) | 1473 (20.57 %) | — | **1621 (22.64 %)** | 43.6 % |
| 9x130, search half | 219 (3.06 %) | 252 (3.52 %) | 250 (3.49 %) | 255 (3.56 %) | **258 (3.60 %)** | 8.0 % |
| 9x130, held-out half | 205 (2.86 %) | 235 (3.28 %) | 230 (3.21 %) | — | **244 (3.41 %)** | 8.0 % |
| purity (pooled): search / held out | 26.7 % / 25.8 % | 29.5 % / 28.8 % | 29.1 % / 28.0 % | 30.4 % / — | 30.9 % / 30.1 % | |
| −t σ68 at 9x275 / 9x130 (476) | 0.124 / 0.133 GeV² | 0.147 / 0.128 GeV² | 0.121 / 0.120 GeV² | 0.120 / 0.118 GeV² | 0.114 / 0.118 GeV² | |

Search halves +23 %, held-out halves +24 % (z +15.23). D4 S4a_tm 7.71 % mean / 14.56 % at 275 GeV (Y9 7.44 / 14.12 %). The
gain sits in the all-ZDC regime (9x275: 750 → 1000 of 2003 Λ found) and with one photon in B0 (395 → 451 of 803). Z5 measures
−t worse at 9x275 (the Λ energy reads high); Z6 repairs −t at −29 found Λ and reproduces on the held-out halves too (1411 → 1703, z +13.70); the user chose Z6 as the base (D-user-44).

## The score

As Phase 5 (`space/reports/phase5_msf.md`, The score): N_found pooled over the search halves D6s_9x275 and D6s_9x130,
selector `463` (paired z ≥ 3, purity guard z_P ≥ −2), D6h held out, fair play `460` (F1–F6) and `465`, plus `468` (F3
for crystal clusters, below).

The −t resolution of the found Λ is reported beside the score from this phase on (`476`; Y9: σ68 0.12 GeV² at 9x275,
0.13 GeV² at 9x130; `space/reports/msf_t_resolution.md`).

## Step 0 record

| # | item | outcome |
|---|---|---|
| 1 | Scope study, offline (`477`) | 9x275 search half (inventory: `crystal-scope-MSF6_Y9-D6s_9x275-step0.json`): the emulator reproduces Y9's own decision (all-ZDC 750 vs 749 found, γ B0 + γ ZDC 395 vs 395). Of 1422 all-ZDC photons without a matched photon neutral, 637 have a pure crystal cluster ≥ 0.5 GeV (rec energy a median 0.21 of the true, clipped). Λ the row misses whose two photons both have a pure candidate only when crystal candidates count: 305 all-ZDC, 40 γ B0 + γ ZDC, 2 γγ in B0 (the ceiling of a crystal finder at 9x275, 4.8 % of expected). With the gun law (item 2), the emulated net gain on the search halves, pooled: **+127** (veto single, crystal photon-depth term −10: 9x275 all-ZDC +114, γ B0 + γ ZDC +1, γγ in B0 0; 9x130 +10, +5, −3) and **+129** (veto split: 9x275 +114, +6, −3; 9x130 +10, +6, −4); N_window at 9x275 +214 / +120, so purity rises (26.4 → 27.6 / 28.2 %). Above the +50 stop line: **the phase continues**. Rerun with the final emulator (the row hypotheses compete with crystal ones whenever crystal candidates exist; the law at least the crystal energy), the canonical record: +131 (single) and +135 (split, −10), N_window +247 / +147 (`crystal-scope-MSF6_Y9-D6s_*-step0.json`). |
| 2 | D2c_photon_low (5, 10, 15 GeV) | generated at the Phase 5 close (D-user-42). D2 + D2c through Y9 (CAL6_D2_Y9, 11 files, integrity clean); the crystal photon law fitted on 10 005 gun photons ≤ 50 GeV (`477 --fit-guns`): E = 1.962·E_crys + 47.47·E_col − 0.881, predicted / true 0.97–1.05 with σ 7–12 % from 5 to 275 GeV (`calib-crystal-CAL6_D2_Y9.json`). |
| 3 | Base row MSF6_Y9, R0 reference CTL6_R0_crys | CTL6_R0_crys on D6s_9x275 (04:30Z–04:38Z, integrity clean). MSF6_Y9 on D6s (from 04:38Z): its ZDC, B0 and crystal raw hits are identical to CTL6_R0_crys on all 40 files of D6s_9x275 (360 leaves, 0 differences); `460 --reference-dir CTL6_R0_crys` PASS (F1a–F3f, `fair-play-MSF6_Y9-msf.json`). Λ by Λ it reproduces Y9 on both search halves (9x275: 5535 Λ identical, N_found 1267, N_window 4794; 9x130: 5135 Λ, 219, 764). On the held-out halves D6h (reconstructed 04:53Z–05:08Z, integrity clean) it reproduces Y9 too (9x275: 5480 Λ identical, N_found 1206; 9x130: 5091 Λ, 205). |
| 4 | `468` written and proven | On MSF6_Y9 D6s_9x275 (40 files, 20 000 events): PASS (0 crystal links); control `share` FAIL (C1 9504), control `budget` FAIL (C2 10 871) (`crystal-f3-*.json`). On the crystal-seeded builds: PASS on Z1 (2012 + 203 crystal-linked neutrals) and Z1b (2161 + 211). |
| 5 | FROZEN, report, deck | `space/FROZEN` adds loop v6 and `468` (04:55Z); the hook refuses an edit to `468`. Report: this file. Deck builder `slides/phase6/build_phase6_slides.py`. |

## Tries

| try | change | 9x275 N_found | 9x130 N_found | b / c, z | purity | z_P | fair play | verdict |
|---|---|---|---|---|---|---|---|---|
| Z1_crystal_photons | crystal-scale clustering + crystal-seeded photons in the ZDC pairing (code) | 1267 → 1271 | 219 → 227 | 110 / 122, +0.79 | 26.7 → 26.6 % | −0.17 | PASS (478 F1, D-default-49; 468) | INCONCLUSIVE — the C++ column summed HEXPLIT subcells (0.45 of the fitted rec-hit column); superseded by Z1b |
| Z1b_crystal_column | Z1 with the Hcal column from the rec hits (code) | 1267 → 1314 | 219 → 232 | 109 / 169, +3.60 | 26.7 → 27.5 % | +0.91 | PASS (478 F1, D-default-49; 468; raw hits = base) | **ACCEPTED** |
| Z2_crystal_params | candidates from 0.3 GeV, 60 mm column with its law, column × 1/sampFrac out of the neutron (parameters) | 1314 → 1388 | 232 → 230 | 48 / 120, +5.55 | 27.5 → 28.0 % | +0.55 | PASS (478 F1; 468; raw hits = base) | **ACCEPTED** |
| Z4_lambda_sigma | the ZDC pairing's Λ-mass width 0.04 → 0.03 GeV (parameter) | 1388 → 1409 | 230 → 237 | 24 / 52, +3.21 | 28.0 → 27.1 % | −1.11 | PASS (478 F1; 468; raw hits = base) | **ACCEPTED** |
| Z5_crystal_energy_alt | the crystal law's energy as a competing hypothesis for tagged Hcal photons (code) | 1409 → 1574 | 237 → 252 | 30 / 210, +11.62 | 27.1 → 29.5 % | +3.05 | PASS (478 F1; 468; raw hits = base) | **ACCEPTED** — −t 16 % worse at 9x275 (Q22) |
| Z6_alt_column_out | the crystal-law photon's Hcal column out of the neutron (code) | 1574 → 1547 | 252 → 250 | 68 / 39, −2.80 | 29.5 → 29.1 % | −0.58 | PASS (478 F1; 468; raw hits = base) | REJECTED (463); −t σ68 0.121 / 0.120 GeV², the best of any row; **the base** by the user's choice (Q22 D, D-user-44) |
| Z7_isolation | an isolation term in the Λ pairing: a tagged Hcal photon adds 2·exp(−d / 42.5 mm), d to the most energetic Hcal cluster (code; length from the neutron gun) | 1547 → 1628 | 250 → 255 | 19 / 105, +7.72 | 29.1 → 30.4 % | +1.62 | PASS (478 F1; 468; raw hits = base) | **ACCEPTED** — −t 0.120 / 0.118 GeV² |
| Z8_hcal_axis_law | tagged Hcal photons may take the axis law's energy: crystal + Hcal rec hits within 45 mm of the photon's line, fitted on the photon guns (±10 %), as a competing energy; column out of the neutron (code; new input EcalFarForwardZDCRecHits) | 1628 → 1688 | 255 → 258 | 52 / 115, +4.88 | 30.4 → 30.9 % | +0.64 | PASS (478 F1; 468; raw hits = base) | **ACCEPTED** — current best; −t 0.114 / 0.118 GeV² |

## Checkpoints

### Checkpoint 1 (2026-11-09T07:44Z, after Z1, Z1b, Z2, Z4, Z5)

| Λ → nπ⁰ found (yield) | Y9 (MSF6_Y9), search | Z5, search | Y9, held out | Z5, held out | reachable |
|---|---|---|---|---|---|
| 9x275 | 1267 (17.70 %) | 1574 (21.98 %) | 1206 (16.84 %) | 1520 (21.23 %) | 43.6 % |
| 9x130 | 219 (3.06 %) | 252 (3.52 %) | 205 (2.86 %) | 235 (3.28 %) | 8.0 % |
| purity (pooled) | 26.7 % | 29.5 % | 25.8 % | 28.8 % | |

- Held out (`463 --split h`, `msf-select-Z5_crystal_energy_alt-vs-MSF6_Y9-D6h.json`): b 83, c 427, z +15.23; purity z_P +3.59 →
  **REPRODUCES**. Search halves +23 %, held-out halves +24 %.
- D4 Λ gun (CP6_1_Z5_D4, `headline.csv`, reported only; `410` credits Hcal clusters only): S4a_tm per thrown 7.71 % mean,
  14.56 % at 275 GeV (Y9 7.44 / 14.12 %).
- −t (476): Z5 σ68 0.147 / 0.128 GeV² (Y9 0.124 / 0.133); on the Λ that Z4 and Z5 both find at 9x275, 0.142 vs 0.122 (Q22).

### Checkpoint 2 (2026-11-09T15:21Z, after Z6, Z7, Z8; run early, the backlog being empty)

| held-out halves D6h | MSF6_Y9 | Z6 (the base) | Z8 | reachable |
|---|---|---|---|---|
| 9x275 N_found (yield) | 1206 (16.84 %) | 1473 (20.57 %) | **1621 (22.64 %)** | 43.6 % |
| 9x130 N_found (yield) | 205 (2.86 %) | 230 (3.21 %) | **244 (3.41 %)** | 8.0 % |
| purity (pooled) | 25.8 % | 28.0 % | **30.1 %** | |

Z8 vs MSF6_Y9: b 90, c 544, z +18.03, z_P +5.17 → **REPRODUCES**; vs Z6: b 41, c 203, z +10.37, z_P +2.57 → **REPRODUCES**
(`msf-select-Z8_hcal_axis_law-vs-*-D6h.json`). Z8 on D6h reconstructed 15:00Z–15:13Z, integrity clean. D4 Λ gun
(CP6_2_Z8_D4, 441): S4a_tm 8.42 % mean, 15.99 % at 275 GeV (Z5 7.71 / 14.56, Y9 7.44 / 14.12; reported, never selected on).

## Findings of the tries

- **Z3 in its simple form is a dead end (emulated).** Giving tagged Hcal photons the crystal law's energy (crystal cluster in
  front + column) instead of the Hcal law's: 9x130 +19, but 9x275 all-ZDC −107 against Z1's +116, the window losing 631
  all-ZDC and 1413 other candidates. On the guns the crystal law resolves photons to 10–12 % at 5–50 GeV, the Hcal law on
  the leading cluster to 24–34 % (median 0.87–1.00); the Hcal photon and neutron laws are calibrated together around m_Λ,
  so replacing one of them shifts the true Λ out of the window.
- **The Hcal clusters' hits are HEXPLIT subcells**, not rec hits, and the cluster energies carry 1 / sampFrac (0.0273).

- **Shower shape does not tell photons from neutron fragments; the distance to the neutron core does (Z7).** Of the
  clusters the photon tag passes, the shape parameters and depth separate photons from fragments at AUC 0.50–0.54 (the
  tag already cuts on them); the transverse distance to the most energetic Hcal cluster at 0.79 (within one event 0.82).
  The neutron gun puts the tagged fragments a median 34.5 mm (mean 42.5 mm) from the core, the same as on MSF, so the
  term's length comes from the gun.
- **A photon's Hcal shower splits into several clusters (Z8).** On the photon guns the leading tagged cluster holds 45–60 %
  of the Hcal energy above 5 GeV, so the Hcal law on it scatters ±24–36 %. The crystal and Hcal rec hits within 45 mm of
  the photon's line, through a gun-fitted law (481), scatter ±10–11 % at 10–50 GeV. The right pairs that fell out of the
  mass window had photons reading low (Hcal law 0.69) and a correct neutron (1.02); low photon energies give a high mass,
  since a smaller E₁E₂ widens the expected π⁰ opening angle and moves the fitted vertex deeper.
- **Tried in emulation, not built:** a crystal-energy-in-front term against the remaining wrong second photons (+15 over
  Z8 at best; photons leave a median 2.1 GeV in the crystals within 30 mm in front, fragments 0.33 GeV), the isolation
  weight 1–4 with the axis law (flat, 2 best), dropping Z5's crystal-law option now that the axis law exists (−4), the
  isolation term on crystal photons (+3 to +8).

## Remaining losses at 9x275 (Z8, emulated)

`477 --why-all` on Z8's settings, the Λ whose two photons both have a pure candidate (tagged Hcal or crystal; B0 for the
mixed regime) but that Z8 misses:

| regime | the chooser's pick | Λ |
|---|---|---|
| all three in the ZDC | one photon right, the other a neutron fragment | 110 |
| | the right pair, its mass out of the window (109 high, 4 low; Δm median +60 MeV) | 113 |
| | one photon right, the other an Hcal cluster neither a photon's nor the neutron's | 93 |
| | one photon right, the other a crystal cluster not pure for a photon | 64 |
| | both wrong, the same photon twice, a B0 hypothesis | 78 |
| γ B0 + γ ZDC | B0 photon right, ZDC photon wrong (Hcal 53, crystal 38) | 91 |
| | the right pair, its mass out of the window | 55 |
| | a B0 pair won | 27 |

In the right pairs out of the window the neutron reads 1.00 and the photons scatter: Hcal-law photons 0.70, crystal
photons 0.32 (16–84 %: 0.06–3.2), crystal-law Hcal photons 1.54. The Λ with a photon in EEMC-P (55 at 9x275, 91 at 9x130,
counted in the reachable yield and never found) have no pure EEMC-P photon neutral (1 of 146): the photon is soft (median
0.74 GeV at 9x275, half below the 1 GeV threshold of the EEMC-P neutrals).

## The gap to the reachable yield (Z8)

Reachable: the Λ → nπ⁰ whose neutron lands in the ZDC and whose photons land in the ZDC, B0 or EEMC-P (210). Per thrown
Λ → nπ⁰ (7160 per half); "clean cluster": a tagged Hcal, crystal (477) or B0 cluster of purity ≥ 0.8 for the photon.

| | 9x275 | 9x130 |
|---|---|---|
| reachable | 3124 (43.6 %) | 580 (8.1 %) |
| a photon has no clean cluster | 704 (9.8 %) | 200 (2.8 %) |
| clean clusters, the wrong second photon or hypothesis picked | ~540 (7.5 %) | ~60 (0.8 %) |
| clean clusters, the right three, mass out of the window | ~200 (2.8 %) | ~62 (0.9 %) |
| found by Z8 in the reachable regimes | 1686 (23.5 %; 1688 = 23.6 % with 2 outside them) | 258 (3.6 %) |

Why a photon has no clean cluster (`482`, Λ counted by their first such photon):

| cause | 9x275 | 9x130 |
|---|---|---|
| ZDC: the photon is inside the neutron's Hcal cluster (median 24 mm from the neutron at the Hcal face; photons with a clean cluster 100 mm) | 278 | 12 |
| ZDC: no cluster carries the photon; 85 % of them leave < 20 % of their energy in the ZDC (they clip its edge), reachable only by 210's home threshold | 118 | 18 |
| ZDC: both photons in one Hcal cluster | 89 | 1 |
| ZDC: a clean Hcal cluster the photon tag rejects | 10 | 1 |
| B0: photon below the 1 GeV of the B0 neutrals | 63 | 42 |
| B0: both photons in one B0 cluster | 48 | 36 |
| B0: the photon shares a B0 cluster with the neutron | 44 | 11 |
| EEMC-P photon (no pure EEMC-P photon neutral) | 54 | 79 |

Of the photons inside the neutron's cluster at 9x275, 53 have a clean crystal cluster (39 vetoed, 14 below 0.3 GeV); the rest
have none. Late decays cause it: all-ZDC Λ decaying 30–40 m from the IP (the ZDC at 36 m) are found at 6 %, 25–30 m at
43 %, before 20 m at 61–63 %.

## The candidates in the window that are not the true Λ (Z8, `483`, after the close)

(written 2026-11-09 after the close, at the user's question about the unmatched candidates)

Purity 31 % means that 69 % of the events with a candidate in the ±30 MeV window hold something other than the true
Λ → nπ⁰. `483` traces every such candidate to its true event and the particles that made its three clusters
(`space/perf/window-candidates-Z8_hcal_axis_law-D6s_*.json`). At 9x275 (search half, 20 000 events): 5437 in the window,
1688 the true Λ, 3749 not. They split into two halves of about the same size.

- **No Λ → nπ⁰ in the event: 1904 (51 % of the unmatched).** A charged or interacting hadron showers in the ZDC; the
  chain calls the shower's core the neutron and two of its fragments the photons.
  - Λ → pπ⁻: 770. The proton reaches the ZDC (the "neutron" is the proton in 757).
  - The Λ interacted in material on its way: 735. Its debris showers in the ZDC and the B0.
  - The Λ reached the ZDC undecayed: 364. The Λ itself showers there.
  - Λ → nπ⁰ with a Dalitz π⁰: 35.
- **A true Λ → nπ⁰ whose photons cannot all be used: 1845 (49 %).** The chain puts a neutron-shower fragment in place of
  the missing photon.
  - A photon (or both) reaches no calorimeter: 736.
  - Both photons in the acceptance, but one has no clean cluster (inside the neutron's cluster, or shared): 866 + 18
    other-triplet choices + 10 without a neutron neutral. These are the losses of the gap section above.
  - The neutron misses the ZDC: 215. A photon's cluster plays the neutron.
- **Why they sit in the window and not around it:** the pairing picks, among all combinations of an event's clusters,
  the one closest to the π⁰ and Λ masses. With several fragments per hadron shower, a combination near m_Λ is nearly
  always there, so the background is pulled into the window: 5437 of the 8279 events with a candidate have it in the
  window.
- At 9x130 (859 in the window, 258 true): no Λ → nπ⁰ 155 (Λ → pπ⁻ 89, material 50, undecayed 11, Dalitz 5); a true
  Λ → nπ⁰ with an unusable photon 446 (photon in no calorimeter 266, neutron missed the ZDC 75, no clean photon cluster
  93 + 12).

What this means: the ZDC cannot tell a proton or a Λ shower from a neutron shower, and a photon from a hadronic fragment
only partly (the tag, Z7's isolation). Raising the purity needs variables that the mass choice does not use: the EM
character of the photons (crystal fraction, depth), a charged-hadron signature, the decay vertex. That is a phase of its
own; Phase 7 (upstream) does not change it.

## Remaining losses at 9x275 (Z5, emulated, run 1)

`477 --alt --why` on Z5's settings: among the all-ZDC Λ missed although a photon has a pure crystal cluster (≥ 0.3 GeV),
- that photon picked right, the other photon wrong: 227 (100 of them have no pure candidate for the other photon);
- both photons picked, the Λ mass out of the window: 138 (76 without a pure candidate for the other photon);
- an Hcal pair won over a pure crystal candidate: 81 (18); another crystal pairing won: 40 (11); vetoed behind an impure Hcal
  cluster: 30.

Run-time knobs on Z5's settings move the emulated net by at most +8: depth term −15 / −5 (on Z2: +112 / +137 vs +151), veto
40 / 90 mm (+140 / +140 vs +151), Λ-mass width 0.025 / 0.035 (+325 / +300 vs +317), π⁰ window 0.07 / 0.14 (+311 / +319),
crystal peak threshold 0.05 / 0.2 GeV (+312 / +313 vs +315, laws refitted). The rest needs information the chooser lacks:
which tagged Hcal cluster is the second photon, and per-photon energies without the high tail.

## Final state

(written 2026-11-09T19:40Z at the close, D-user-45)

- **Code.** EICrecon working tree = a15b0db6 (Phase 4's X9 accept commit) + `phase5_cumulative.patch` (Y2, Y5, Y9) +
  `Z1b_crystal_column.patch` + `Z5_crystal_energy_alt.patch` + `Z6_alt_column_out.patch` + `Z7_isolation.patch` +
  `Z8_hcal_axis_law.patch`, uncommitted (no `please-git` in this phase). The whole diff from a15b0db6 is
  `space/notes/patches/phase6_working_tree.patch` (1054 added lines in 7 files: FarForwardNeutralsReconstruction `.cc`,
  `.h`, Config and factory, LambdaReconstruction.cc, ZDC.cc, reco.cc). Nothing committed, nothing pushed.
- **Run-time parameters of Z8** (`configs/experiments/Z8_hcal_axis_law.yaml`): the B0 ECal island splitting
  (`splitCluster 1`, `transverseEnergyProfileMetric dimScaledLocalDistXY`, `transverseEnergyProfileScale 0.3`), the B0
  photon law `1.0888,1.0058`, `crystalClusterEmin 0.3`, `crystalColumnRadius 60`, `crystalGammaLaw 1.9092,44.768,-0.8984`,
  `crystalColumnNeutronScale 36.63`, `lambdaPairingLambdaSigma 0.03`, `crystalAltColumnOut 1`, isolation weight 2 and
  length 42.5 mm, `hcalAxisAlternative 1`, `hcalAxisRadius 45`, `hcalAxisLaw 2.5938,45.8981,-1.5994`. The defaults in
  `reco.cc` are still Z1's (for example `crystalGammaLaw {1.962, 47.47, −0.881}`): a build without these parameters is
  not Z8. Upstream code must carry them as defaults, and that build must reproduce Z8.
- **What Z8 changes outside the ZDC.** The B0 ECal clusters (`B0ECalClusters`, through the three B0 island parameters
  of Phase 5) — a calorimeter outside the ZDC's owned list. The ZDC crystal-section clusters (`EcalFarForwardZDCClusters`,
  ZDC.cc: neighbourhood 3.5 cm, split at local maxima), which the `zdc_lyso` benchmark reads. The neutrals factory gets
  three new inputs (`EcalFarForwardZDCClusters`, `HcalFarForwardZDCRecHits`, `EcalFarForwardZDCRecHits`) in `reco.cc`.
  No phase measured the effect of these on other users (Phase 4 argued from the code that the default-off core split
  leaves BEMC and FHCAL alone). Phase 7 measures it.
- **Kept on disk for Phase 7:** the ROOT of Z8 (D6s, D6h), MSF6_Y9, CTL6_R0_crys, CP6_2_Z8_D4, CAL6_D2_Y9, CAL6_D3_Z6;
  everything else of Phase 6 is in `space/notes/cleanup-pending.sh`.

## Next run recommendations

Run 1's items are done: Z6 became the base (Q22), the second-photon problem got the isolation term (Z7), the energy tail
turned out to be photon energies, not the neutron's (Z8).

1. **Crystal photon energies.** In the right pairs out of the window the crystal photons read 0.32 (0.06–3.2): a crystal
   candidate's column misses most of its Hcal shower or takes the neutron's. An axis law for crystal candidates (rec hits
   around the crystal cluster's line at several radii, fitted on the guns), offered as a competing energy as Z8 does for
   Hcal photons; emulate with `477` first.
2. **The second photon, beyond distance.** 110 + 93 + 91 misses still pick a fragment or a mixed cluster; neither the
   shape parameters nor the crystal energy in front separate them further (480, `--front` +15). A joint likelihood of
   distance, energy share and crystal fraction fitted on the D2 / D3 guns may; it needs a two-particle gun (photon +
   neutron at MSF separations) to be fitted honestly (F4).
3. **EEMC-P photons are out of reach for the ZDC chain:** 146 Λ in the reachable yield have their soft photon there and
   no pure EEMC-P photon neutral. Recovering them is an EEMC-P clustering and threshold question (the neutrals' 1 GeV),
   outside this phase; the reachable yield could count them apart.
4. **The photon inside the neutron's Hcal cluster** (278 Λ at 9x275, the largest single loss; section The gap to the
   reachable yield). 53 of them have a clean crystal cluster that the veto or the 0.3 GeV threshold drops (39 vetoed); the
   rest need sub-structure of the neutron's Hcal cluster, a clustering change that the −t guard must watch. Part of it is
   a ceiling question: Λ decaying 30–40 m from the IP are found at 6 %; 210 could report the reachable yield with a
   decay-depth cut beside the present one.
5. **Upstream:** Z1b–Z8 are self-contained in FarForwardNeutralsReconstruction (+ ZDC.cc's crystal clustering, + the
   EcalFarForwardZDCRecHits input for Z8); the patches under `space/notes/patches/` apply in order on a15b0db6 + Phase 5.

## Open questions

None. Q21 answered A (D-user-43), Q22 answered D (D-user-44), both 2026-11-09.

## Defaults you may veto

- D-default-50: a code try is built only when the emulation predicts at least +30 found Λ pooled over the current best;
  smaller ideas stay emulation records (run 2: the crystal-front term +15 and three parameter rescans were not built).
- D-default-51: a run that ends on an empty backlog runs the checkpoint (D6h + D4) on its best first (checkpoint 2 after
  three tries).

- D-default-49: confirmed by the user (Q21 A, D-user-43).
- D-default-48: the scope study's crystal clustering and candidate parameters, the linear law fitted on guns ≤ 50 GeV.
- D-default-47: one Phase 6 output template (Y9's MSF template plus the crystal raw hits, rec hits, clusters and
  associations, and the Hcal rec hits) for the base row, its R0 reference and every try; Step 0 item 3 runs before item 1.
