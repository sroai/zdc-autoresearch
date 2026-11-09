# Phase 6 — the crystal-seeded ZDC photon finder

Loop: `zdc-autoresearch-loop-v6.md` (prepared under D-user-41, started 2026-11-09T04:27Z on the user's start line, no
`please-git`: tries are patches under `space/notes/patches/`). Deck: `slides/phase6/` (Step 0 item 5).

## Summary

**Run 1 ended 2026-11-09T08:19Z for the user's review** (the backlog of tries with a predicted gain is empty; Q21, Q22 open). Six tries
since Step 0: Z1b, Z2, Z4, Z5 ACCEPTED, Z1 INCONCLUSIVE, Z6 REJECTED. None is foul if F1d may be read from `478` on the as-built tree (D-default-49) — Q21, BLOCKING: under its option C the crystal line is FOUL and the base returns to MSF6_Y9.
Checkpoint 1 REPRODUCES on the held-out halves. The current best Z5 adds crystal-seeded photons to the ZDC Λ pairing (the LYSO
crystal section clustered at the crystal scale; the photon's energy from the crystal energy and the Hcal column behind it, a
law fitted on photon guns) and offers that energy to tagged Hcal photons as a competing hypothesis.

| Λ → nπ⁰ found, per expected (yield) | Y9 (start) | Z5 (current best) | Z6 (Q22) | reachable |
|---|---|---|---|---|
| 9x275, search half | 1267 (17.70 %) | 1574 (21.98 %) | 1547 (21.61 %) | 43.6 % |
| 9x275, held-out half | 1206 (16.84 %) | 1520 (21.23 %) | 1473 (20.57 %) | 43.6 % |
| 9x130, search half | 219 (3.06 %) | 252 (3.52 %) | 250 (3.49 %) | 8.0 % |
| 9x130, held-out half | 205 (2.86 %) | 235 (3.28 %) | 230 (3.21 %) | 8.0 % |
| purity (pooled): search / held out | 26.7 % / 25.8 % | 29.5 % / 28.8 % | 29.1 % / 28.0 % | |
| −t σ68 at 9x275 / 9x130 (476) | 0.124 / 0.133 GeV² | 0.147 / 0.128 GeV² | 0.121 / 0.120 GeV² | |

Search halves +23 %, held-out halves +24 % (z +15.23). D4 S4a_tm 7.71 % mean / 14.56 % at 275 GeV (Y9 7.44 / 14.12 %). The
gain sits in the all-ZDC regime (9x275: 750 → 1000 of 2003 Λ found) and with one photon in B0 (395 → 451 of 803). Z5 measures
−t worse at 9x275 (the Λ energy reads high); Z6 repairs −t at −29 found Λ and reproduces on the held-out halves too (1411 → 1703, z +13.70) (Q22).

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
| Z5_crystal_energy_alt | the crystal law's energy as a competing hypothesis for tagged Hcal photons (code) | 1409 → 1574 | 237 → 252 | 30 / 210, +11.62 | 27.1 → 29.5 % | +3.05 | PASS (478 F1; 468; raw hits = base) | **ACCEPTED** — current best; −t 16 % worse at 9x275 (Q22) |
| Z6_alt_column_out | the crystal-law photon's Hcal column out of the neutron (code) | 1574 → 1547 | 252 → 250 | 68 / 39, −2.80 | 29.5 → 29.1 % | −0.58 | PASS (478 F1; 468; raw hits = base) | REJECTED (463); −t σ68 0.121 / 0.120 GeV², the best of any row (Q22) |

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

## Findings of the tries

- **Z3 in its simple form is a dead end (emulated).** Giving tagged Hcal photons the crystal law's energy (crystal cluster in
  front + column) instead of the Hcal law's: 9x130 +19, but 9x275 all-ZDC −107 against Z1's +116, the window losing 631
  all-ZDC and 1413 other candidates. On the guns the crystal law resolves photons to 10–12 % at 5–50 GeV, the Hcal law on
  the leading cluster to 24–34 % (median 0.87–1.00); the Hcal photon and neutron laws are calibrated together around m_Λ,
  so replacing one of them shifts the true Λ out of the window.
- **The Hcal clusters' hits are HEXPLIT subcells**, not rec hits, and the cluster energies carry 1 / sampFrac (0.0273).

## Remaining losses at 9x275 (Z5, emulated)

`477 --alt --why` on Z5's settings: among the all-ZDC Λ missed although a photon has a pure crystal cluster (≥ 0.3 GeV),
- that photon picked right, the other photon wrong: 227 (100 of them have no pure candidate for the other photon);
- both photons picked, the Λ mass out of the window: 138 (76 without a pure candidate for the other photon);
- an Hcal pair won over a pure crystal candidate: 81 (18); another crystal pairing won: 40 (11); vetoed behind an impure Hcal
  cluster: 30.

Run-time knobs on Z5's settings move the emulated net by at most +8: depth term −15 / −5 (on Z2: +112 / +137 vs +151), veto
40 / 90 mm (+140 / +140 vs +151), Λ-mass width 0.025 / 0.035 (+325 / +300 vs +317), π⁰ window 0.07 / 0.14 (+311 / +319),
crystal peak threshold 0.05 / 0.2 GeV (+312 / +313 vs +315, laws refitted). The rest needs information the chooser lacks:
which tagged Hcal cluster is the second photon, and per-photon energies without the high tail.

## Next run recommendations

1. Q22 first: the base (Z5 more Λ, Z6 better −t).
2. Shower shape for the tagged Hcal photons (the second photon is wrong for 227 of the missed Λ above): a photon/neutron
   fragment discriminant from the Hcal cluster's longitudinal and lateral profile, fitted on D2 / D3 guns (F4), as a term of
   the chooser; emulate with `477` before code.
3. The energy tail (138 Λ out of the window with both photons right): the neutron energy in events with photons (reco / true
   1.07 on Y9, guns ≈ 1.0) — a photon-aware neutron sum.
4. Upstream: Z1b–Z5 are self-contained in FarForwardNeutralsReconstruction (+ ZDC.cc's crystal clustering); the patches under
   `space/notes/patches/` apply on a15b0db6 + Phase 5.

## Open questions

- Q21 (BLOCKING): F1d of uncommitted code tries from `478` on the working tree (D-default-49) — or commits with `please-git`. The acceptances of Z1b, Z2, Z4 and Z5 depend on it.
- Q22: the base for the next tries, Z5 or Z6.

## Defaults you may veto

- D-default-49: F1a + F1d of uncommitted code tries from `478` on the working tree (460's own checks on the source the install
  was built from); 460's MSF run walks the base commit and fails F1d whenever a try adds a factory input (Q21).
- D-default-48: the scope study's crystal clustering and candidate parameters, the linear law fitted on guns ≤ 50 GeV.
- D-default-47: one Phase 6 output template (Y9's MSF template plus the crystal raw hits, rec hits, clusters and
  associations, and the Hcal rec hits) for the base row, its R0 reference and every try; Step 0 item 3 runs before item 1.
