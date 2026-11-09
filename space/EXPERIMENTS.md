# Experiment ledger

Append-only, one entry per experiment, written in two steps: the hypothesis
block BEFORE the run, the verdict block after. Entry shape:
`zdc-autoresearch-loop-v2.md`, section "The experiment loop". Rejected
entries stay; corrections are new entries. The backlog of not-yet-run
hypotheses sits at the bottom, ordered.

## Phase 1 — dissection of PR 3064 (hypotheses written 2026-11-05 02:12, before any Phase 1 run)

Reference numbers (Phase 0, D4 175 GeV): R0 S0γ 0.065, S0n 0.648, S0all 0.023; R1 S0γ 0.399,
S0n 0.042, S0all 0.015. D5 minQ2=0: R0 φ@180 0.069, single-column 0.00, 0.98 clusters/event;
R1 φ@180 1.000, single-column 1.00, 10.1 clusters/event. Calibration: R0* runs keep the stock
coefficients, R1* runs keep R1's (clustering is what is dissected; S0 does not depend on calibration).

H1 (mechanism): the XY distance below the 24.4 mm subcell pitch alone produces G1 (φ at ±180°,
single-column clusters) and most of G2/G3 and of R1's S0γ gain and S0n loss; the threshold pair
only decides which shards survive.

Verdict blocks: `300_run_experiment.py` appends its stub at the end of the file; the filled blocks were moved
under their entries (2026-11-05, no hypothesis text edited). Every Phase 1 verdict reads the Phase 2–3 acceptance
rule against the run's own reference; Phase 1 changes no current best. H1's outcome and the PR's S0 balance:
`space/reports/phase1_dissection.md`.

## P1a 2026-11-05: R0 + neighbourLayersRange 1 → 3
tier: parameter
config: configs/experiments/P1a_R0_nlr3.yaml
hypothesis: hits up to 3 layers apart join one cluster. With the 3×3 distance R0 already merges the
Λ photons, so S0γ (D4) stays within ±0.01 of 0.06; neutron fragments separated by empty layers
rejoin, so S0n rises by ≤ +0.03 and D3 clusters per neutron fall slightly; G1 unchanged (φ@180
≤ 0.1, single-column 0). Small effect everywhere.
expected cost: R0-like T: ~280–500 s per 1000 gun events per process, ~2400 s per 1000 NC events
--- after the run (2026-11-05) ---
row: P1a_R0_nlr3 (scoreboard.csv; metrics-P1a_R0_nlr3.json); paired against R0_stock
result: D4 S0all 0.005 / 0.012 / 0.014 / 0.014 / 0.013 / 0.012 / 0.009 / 0.006 (100–275 GeV; R0 0.006 … 0.011),
Δ −0.0045 to −0.010, significant at 125–275 GeV (z −3.0 to −4.5). S0γ Δ −0.014 to −0.027, significant at every
momentum, and one-sided: gained 0 at every momentum (lost 57–109). S0n not significant anywhere (|z| ≤ 1.5).
D1 S1a_truth_all −0.012 to −0.072 at 50–80 GeV (gained 0), n.s. above. D3 S3 raw sum +0.008 to +0.025 (+1.8 % to
+9.7 %); clusters per neutron 0.817 → 0.809. D5 φ@180 0.072 (SIDIS), columns 0, G2 0.887 / 0.636, G3 0.006 / 0.004.
Hypothesis check: S0γ within ±0.01 of R0 ✗ (−0.014 to −0.027, significant); S0n up by ≤ +0.03 ✗ (unchanged);
D3 clusters per neutron down slightly ✓ (−0.008); G1 unchanged ✓.
guards (vs R0): G4 PASS (static; D5); S2 after refit (a = 1.778, b = 0.917, χ² 66/6, as R0's) residuals
0.976–1.018, in; S3 raw sum up, in (one-sided, D-user-12); clusters per neutron in; S4b n/a; S4c in; G1–G3 in.
verdict: REJECTED — S0all falls significantly at 125–275 GeV (S0γ loses only).
understanding: neighbourLayersRange only adds edges to the connectivity graph, so it can only merge clusters,
never split them: every S0γ change is a loss (gained 0). At the 3×3 distance the two Λ photons and the neutron
shower are already close; a 3-layer reach lets sparse late hits bridge them. The neutron gains nothing
because its shower is already one cluster at layer range 1.
next: layer range 1 is the better value at 3×3 (and P1d finds 1 slightly better at 1×1 too); nlr drops
to the end of the backlog (B4).
re-judged (2026-11-05, after D-user-16/17): S2 in (20 GeV 0.976 ± 0.009); photon raw sum D2 +0.2 to +0.7 %, in; verdict unchanged, REJECTED (S0all falls).

## P1b 2026-11-05: R0 + threshold pair (minClusterCenterEdep 25 → 5 MeV, minClusterNhits 10 → 2)
tier: parameter (named pair: both decide which connected groups survive)
config: configs/experiments/P1b_R0_thr.yaml
hypothesis: ImagingTopoCluster keeps a connected group when its seed and size pass; lowering both keeps
small isolated groups (halo, late neutron fragments) but cannot split a merged shower. S0γ unchanged
(|Δ| < 0.01, not significant); clusters per event up on D3/D5 (a few %); S0n slightly down
(containment shared with new fragments, ≤ −0.02). G1 unchanged. (Switch test: minClusterNhits alone
was inert on R0 D1.)
expected cost: as P1a
--- after the run (2026-11-05) ---
row: P1b_R0_thr (scoreboard.csv; metrics-P1b_R0_thr.json); paired against R0_stock
result: D4 S0all 0.075 / 0.075 / 0.057 / 0.051 / 0.042 / 0.039 / 0.032 / 0.018 (100–275 GeV; R0 0.006 / 0.019 / 0.022 /
0.023 / 0.021 / 0.022 / 0.015 / 0.011), Δ +0.069 (100 GeV) to +0.0075 (275 GeV), significant at every momentum
(z 11.7 … 3.9), gained 136 … 15, **lost 0** at every momentum. S0γ 0.056 → 0.150 at 100 GeV, Δ +0.093 to +0.010,
significant everywhere, lost 0; S0n Δ +0.023 / +0.006 at 100 / 125 GeV (significant), n.s. above, lost ≤ 2.
D1 S1a_truth_all +0.077 (50 GeV) … +0.0055 (160 GeV), significant at every momentum, lost 0. D3 S3 raw sum
+0.41 (20 GeV) … +0.002 (275 GeV), σ/mean better at every momentum (2.44 → 0.30 at 20 GeV, 0.122 → 0.118 at
275 GeV); clusters per neutron 0.817 → 1.16. S1b π⁰ mass σ 0.0117 → 0.0130 GeV. S4a 0 (no photon is tagged
on 3×3 clusters, O1). D5 clusters/event 0.555 → 0.733 (NC), 0.984 → 1.244 (SIDIS); φ@180 0.061 / 0.068;
columns 0 / 0; E > 50 GeV fraction 0.612 → 0.467, 0.864 → 0.686; clusters < 5 GeV per event 0.110 / 0.182.
Hypothesis check: S0γ unchanged, |Δ| < 0.01 ✗ (up +0.01 to +0.09, significant); "cannot split a merged shower" ✓
(the S0 gains are particles that had no surviving cluster, see understanding); clusters per event up a few % on
D3 / D5 ✗ in size (+42 % D3, +32 % / +26 % D5); S0n slightly down ✗ (unchanged or up); G1 unchanged ✓.
guards (vs R0): G4 PASS (static; D5); S2 after refit (a = 1.765, b = 0.919, χ² 67/6) residuals 0.9488 (20 GeV),
0.989–1.014 (30–275 GeV): **20 GeV out by 0.1 %** (limit 0.95; R0's own refit gives 0.9526 there, the a·E^b form's
miss, χ² 65/6 for R0 too); S3 raw sum up, in (one-sided, D-user-12; spread better); clusters per neutron +0.34, in
(limit +0.5); S4b n/a; S4c 0.008 in; G1 in; G2 in (−24 % / −21 %, limit −50 %); G3 in (0.110 / 0.182 < 0.5).
verdict (by the Phase 2–3 rule, read in Phase 1; Phase 1 changes no current best): REJECTED by the letter on one
point — S2 at 20 GeV, 0.9488 against 0.95 — with every S0 component up or unchanged and every other guard in.
Without that point it is the first ACCEPTED-grade change of the program (Q10).
understanding: the threshold pair decides only which connected groups survive; the connectivity is unchanged,
so every cluster of R0 is still there and new ones are added. A particle can gain separation only when none
of its groups survived before (no best cluster → not separated) — gained 136, lost 0 at 100 GeV — and the
containment denominator can only grow, which works against S0 (Q9 cuts the other way here; the gains are
honest). The gainers are the soft Λ photons: at 100 GeV a photon of 10–30 GeV on 3×3 clusters often has its
own small group whose seed is below 25 MeV or whose size is below 10 hits. This is the whole S0all gain of
P1f over R0, and more: P1f = P1b + nlr 3 (P1a: nlr 3 costs S0γ) + the PR's neutrals coefficients (no S0 effect).
next: the first Phase 2 experiments split the pair (seed and size separately) and scan them down, at 3×3 and
nlr 1 (B1, B2); adopting P1b as Phase 2's starting best waits for Q10 and the held-out D1h / D4h check.
re-judged (2026-11-05, after D-user-16/17): S2 20 GeV 0.9488 ± 0.0092 → |Δ| − 2σ = 0.033 ≤ 0.05, in; photon raw sum D2 +0.0 to +3.2 % (D4 photons +0.9 to +14.4 %), in. Every guard in, every S0 component up or unchanged: **ACCEPTED by the rule** (read in Phase 1: Phase 1 changes no current best; adoption as Phase 2's start waits for the held-out D1h / D4h check, rule 8).

## P1c 2026-11-05: R0 + PR XY distances (0.3 × side_length = 14.6 mm), code tier
tier: code (install eicrecon-dist0p3, space/notes/patches/dist0p3.patch)
config: configs/experiments/P1c_R0_dist.yaml
hypothesis (H1): no two subcells of one layer are neighbours, clusters grow only along z. Predicted:
D5 φ@180 > 0.9 and single-column > 0.9; D4 S0γ rises to ≥ 0.25 (most of R1's +0.33) and S0n falls
below 0.15 (most of R1's −0.61); S0all stays ≤ 0.03. With R0's stricter thresholds (25 MeV seed,
10 hits) more shards die than in R1: clusters per event below R1's, S3 raw sum lower than R1's.
expected cost: as P1a
--- after the run (2026-11-05) ---
row: P1c_R0_dist (scoreboard.csv; metrics-P1c_R0_dist.json); paired against R0_stock
result: D4 S0all 0.005 / 0.014 / 0.031 / 0.037 / 0.043 / 0.056 / 0.050 / 0.047 (100–275 GeV; R0 0.006 … 0.011):
Δ +0.023 to +0.037, significant at 200–275 GeV (z 4.4–6.9), not significant below. S0γ 0.094 → 0.282
(Δ +0.04 to +0.25, significant at every momentum); S0n 0.656 → 0.253 (Δ −0.08 to −0.39, significant
at 125–275 GeV). D1 S1a_truth_all +0.29 to +0.65 above 60 GeV, −0.29 at 50 GeV. D3 S3 raw sum −0.07 to
−0.43 (mean 0.564 → 0.243); clusters per neutron 0.82 → 2.49; mistag 0 → 0.088. D2 γ-tag 0.03 → 0.54.
D5 φ@180 1.000 / 1.000, single-column 1.000 / 1.000, clusters/event 0.555 → 1.252 (NC), 0.984 → 3.481 (SIDIS).
Hypothesis check: φ@180 and columns > 0.9 ✓; clusters/event below R1's (1.25 / 3.48 vs 3.64 / 10.16) ✓;
S3 raw sum below R1's (0.243 vs 0.381) ✓; S0γ at 175 GeV 0.233, predicted ≥ 0.25 ✗ (half of R1's gain there);
S0n at 175 GeV 0.436, predicted < 0.15 ✗; S0all at 175 GeV 0.037, predicted ≤ 0.03 ✗.
guards: G4 PASS (D5 static + full G4 on all 29 gun files: 9048 non-ZDC leaves identical); S2 scale out with
stock coefficients (median 0.44), after the 420 refit (a = 3.61, b = 0.892, χ² 4.9/6) residuals 0.957–1.064,
20 GeV out of ±5 %; S3 raw sum out (−57 % vs R0, limit 5 %); S3 clusters per neutron out (+1.67, limit +0.5);
S4b n/a (no Λ); S4c 0.93 in; G1 out (1.000 / 1.000 vs 0.15 / 0.05); G2 out (E > 50 GeV fraction −97 % / −95 %,
limit −50 %); G3 in (0.215 / 0.129 < 0.5).
verdict: REJECTED — S0all gains at ≥ 200 GeV but S0n falls significantly, and G1, G2, S3 raw sum and clusters per neutron are out.
understanding: H1 holds for G1 and G2: the sub-pitch distance alone makes every cluster a single (x,y) column
and kills the high-energy clusters on NC/SIDIS. It carries about half of R1's S0γ gain at 175 GeV (+0.168 of +0.334), strongly momentum
dependent (13 % at 100 GeV, 85 % at 275 GeV), and about a third of R1's S0n loss at 175 GeV (−0.21 of −0.61). The rest of R1's S0n loss comes from the lower thresholds/nlr keeping the
shards as separate clusters (R0's 25 MeV / 10-hit cut drops them, which is also why S3 raw sum falls to 0.24:
the energy is not in another cluster, it is discarded). With the threshold cut doing that, the neutron's
biggest column often holds ≥ 50 % of the *surviving* energy (raw sum 0.23 at 100 GeV) at low momentum (S0n 0.66
at 100 GeV) but not at high momentum (0.25 at 275 GeV), where the shower spreads over more subcells. The S0n miss
(predicted < 0.15, measured 0.44 at 175 GeV) is in part the ruler: containment is measured against the
particle's energy in surviving clusters, and R1's 0.04 is what column clustering gives when little is
discarded (Q9). S0all rises at high momentum
because the photons separate there while the neutron still keeps half of its energy in one column often enough.
next: the distance is the only knob that separates photons; the cost is the neutron. The question for
Phase 2/3 is a distance between the two extremes (2D neighbours of one subcell side, code tier), or splitting
(Island + splitCluster) instead of a shorter reach — backlog B7, B8.
re-judged (2026-11-05, after D-user-16/17): S2 in (all points within 2σ of ±5 %); photon raw sum D2 −12 to −61 %, out (new guard); verdict unchanged, REJECTED.

## P1d 2026-11-05: R1 − neighbourLayersRange (3 → 1)
tier: parameter
config: configs/experiments/P1d_R1_nlr1.yaml
hypothesis: on single-column clusters a column breaks at any layer without a hit in its subcell;
with layer range 1 each break starts a new cluster. Clusters per event up strongly (> +30 % on D5),
D4 S0γ down (containment, Δ ≤ −0.05), S0n down further toward 0. G1 stays at 1.0.
expected cost: as P1a
--- after the run (2026-11-05) ---
row: P1d_R1_nlr1 (scoreboard.csv; metrics-P1d_R1_nlr1.json); paired against R1_pr3064
result: D4 S0all 0.025 / 0.026 / 0.018 / 0.020 / 0.017 / 0.012 / 0.016 / 0.015 (R1 0.015 … 0.008), Δ +0.0015 to
+0.010, significant at 100, 200, 250, 275 GeV; S0γ Δ +0.019 to +0.044, significant at every momentum (gained
88–183, lost 4–15); S0n Δ +0.005 to +0.026, significant at 100–175, 250, 275 GeV. No S0 component falls
anywhere. D1 S1a_truth_all +0.005 at 130 GeV (significant), n.s. elsewhere. D3 S3 raw sum −3.2 % to −5.6 %
(significant); clusters per neutron 7.52 → 7.11. S4a_tm n.s. at every momentum (mean 0.018 → 0.017); S4b σ
0.027 → 0.021 GeV. D5 clusters/event 3.640 → 3.486 (NC), 10.160 → 9.622 (SIDIS); G1 1.000 / 1.000.
Hypothesis check: clusters per event up > +30 % ✗ (−4 % / −5 %); S0γ down by ≤ −0.05 ✗ (up +0.02 to +0.04);
S0n down ✗ (up); G1 stays at 1.0 ✓. Refuted.
guards (vs R1, its reference): G4 PASS (static; D5); S2 after refit (a = 3.90, b = 0.876, χ² 4.4/6; the PR's
γ coefficients 2.7, 1.27 are 7.8σ / 40σ off) residuals 0.954–1.030, in; S3 raw sum −5.0 % / −5.6 % at 20 / 50 GeV, out (limit a 5 % drop), −3.2 % to −4.2 % at
100–275 GeV, in; clusters per neutron in; S4b in; S4c 6.41 out (limit 4.0; R1 4.87 is out too); G1–G3 out
(as R1: 1.000 / 1.000, G2 −98 %, G3 5.04 / 2.02).
verdict: REJECTED — every S0 component improves on R1, but G1–G3 and S4c are out (as for R1 itself), and the raw sum
drops > 5 % at 20 / 50 GeV.
understanding: on single-column clusters the layer reach mostly decides what joins a column from
neighbouring columns' gaps, not whether a column breaks: fewer edges means fewer stray hits attached, so
purity and S0 rise slightly, and the small pieces a column now breaks into fall below the 5 MeV / 2-hit
thresholds and disappear (clusters per event down, raw sum down 3–6 %, which also lifts containment through
its denominator, see Q9). The S0 side of R1 is insensitive to nlr; the column guards come from the distance.
next: nlr is a second-order knob in both clusterings (P1a: 3 hurts at 3×3; P1d: 1 helps slightly at 1×1).
Set nlr = 1 by default in Phase 2 and scan it last (B4).
re-judged (2026-11-05, after D-user-16/17): S2 in; photon raw sum D2 −0.1 to −0.7 % vs R1, in; verdict unchanged, REJECTED (G1–G3, S4c).

## P1e 2026-11-05: R1 − threshold pair (5 → 25 MeV, 2 → 10 hits)
tier: parameter (named pair)
config: configs/experiments/P1e_R1_thr.yaml
hypothesis: the small shards of R1 die: clusters per event down (D5 −30 % or more), nhits median
up; S0γ roughly unchanged (the best cluster is the big one; Δ within ±0.03); S3 raw sum lower than
R1 (dropped shards); G1 stays near 1.0 (the distance still makes columns).
expected cost: as P1a
--- after the run (2026-11-05) ---
row: P1e_R1_thr (scoreboard.csv; metrics-P1e_R1_thr.json); paired against R1_pr3064
result: D4 S0all Δ −0.007 / −0.005 at 100 / 125 GeV (n.s.), +0.024 to +0.045 at 150–275 GeV (significant, z 4.7–8.5);
S0γ Δ −0.23 (100 GeV) to −0.05 (275 GeV), significant everywhere; S0n Δ +0.57 (100 GeV) to +0.20 (275 GeV),
significant everywhere (mean 0.044 → 0.421). D1 S1a_truth_all −0.21 / −0.12 / −0.05 at 50 / 60 / 70 GeV,
+0.06 to +0.15 at 100–160 GeV. D3 S3 raw sum −24 % (275 GeV) to −81 % (20 GeV); clusters per neutron
7.52 → 2.50. S4a_tm 0.018 → 0.005 (significant at 150–275 GeV). D5 clusters/event 3.640 → 1.279 (NC),
10.160 → 3.505 (SIDIS), nhits median 19 → 20, 25 → 27; G1 1.000 / 1.000; G3 2.13 → 0.14, 5.44 → 0.22.
Hypothesis check: clusters per event down ≥ 30 % ✓ (−65 %); nhits median up ✓ (slightly); S0γ within ±0.03 ✗
(−0.05 to −0.23); S3 raw sum below R1's ✓; G1 near 1.0 ✓.
guards (vs R1): G4 PASS (static; D5); S2 after refit (a = 3.87, b = 0.876, χ² 2.7/6) residuals 0.960–1.050, in (20 GeV at the limit);
S3 raw sum out (drops of 24–81 %); clusters per neutron in (down); S4b in (0.013 GeV); S4c 2.08 in; G1 out
(1.000 / 1.000); G2 out (0.017 / 0.046 vs R0 0.612 / 0.864); G3 in (0.138 / 0.220).
verdict: REJECTED — S0γ falls significantly at every momentum and the raw sum drops 24–81 %, though S0all gains at 150–275 GeV.
understanding: R1's thresholds are what keeps the photons. On 1×1 columns a photon's best column often has
fewer than 10 hits or a seed below 25 MeV — most at 100 GeV, where the Λ photons are softest — and dies, so
S0γ falls most at low momentum. The neutron's S0n "gain" is mostly the containment denominator: the
shards that die no longer count in the neutron's associated energy (raw sum −24 to −81 %), so its biggest
column holds ≥ 50 % of what is left (Q9). P1e ≈ P1c (R0 + distance) on every S0 cell, as it should: the two
differ only by nlr and the neutrals coefficients, neither of which moves S0 much.
next: the threshold pair does two things at once (keeps small photon columns; drops neutron shards) and the
ruler rewards the second for the wrong reason; Q9 first, then scan the seed threshold and nhits separately
(B1, B2).
re-judged (2026-11-05, after D-user-16/17): S2 in; photon raw sum D2 −6 to −39 % vs R1, out (new guard); verdict unchanged, REJECTED.

## P1f 2026-11-05: R1 − distances (= the six PR parameters on the pin)
tier: parameter
config: configs/experiments/P1f_R1_dist.yaml
hypothesis: back to 3×3 clustering with nlr 3 and low thresholds: S0 close to R0 + P1a + P1b
(S0γ ≈ 0.06, S0n ≈ 0.65), G1 back to R0's level (φ@180 < 0.1, columns 0). The PR's coefficients
on R0-like clusters are predictable garbage: S3 corrected scale ≈ 16.65·E^0.66/E, about 2.4 at
100 GeV; no photon is tagged (widths > 12 mm), so the γ coefficients do not act.
expected cost: as P1a
--- after the run (2026-11-05) ---
row: P1f_R1_dist (scoreboard.csv; metrics-P1f_R1_dist.json); paired against R1_pr3064 (its reference) and,
print-only (`400 --no-row`), against R0_stock
result vs R1: D4 S0all 0.050 / 0.046 / 0.033 / 0.028 / 0.024 / 0.022 / 0.019 / 0.011 (R1 0.015 … 0.008), Δ +0.035
to +0.003, significant at 100–200 GeV (z 3.2–6.5); S0γ 0.100 → 0.028 (Δ −0.24 to −0.34, significant everywhere);
S0n 0.687 → 0.652 (Δ +0.60 to +0.62, significant everywhere); S4a_tm 0 (Δ −0.005 to −0.031, significant at
125–275 GeV: no photon is tagged, so no π⁰ pair forms). D1 S1a_truth_all −0.30 to −0.60 (50 GeV +0.01, n.s.).
result vs R0: S0all Δ +0.044 / +0.027 / +0.012 at 100 / 125 / 150 GeV (z 9.0 / 6.0 / 3.1, gained 90 lost 3 at 100),
not significant at 175–275 GeV; S0γ +0.044 / +0.024 at 100 / 125 GeV, −0.011 / −0.0085 at 225 / 275 GeV
(z −3.7 / −3.8, significant); S0n not significant anywhere (|z| ≤ 2.7). D1 S1a_truth_all +0.015 / +0.006 / +0.026
at 100 / 130 / 80 GeV (significant). D3 S3 raw sum +0.44 (20 GeV) … +0.014 (275 GeV), all significant: the low
thresholds keep the low-energy neutrons' clusters that R0's 25 MeV / 10-hit cut drops.
D5 φ@180 0.062 / 0.067, single-column 0 / 0, clusters/event 0.686 (NC) / 1.132 (SIDIS) (R0 0.555 / 0.984).
Hypothesis check: S0γ ≈ 0.06 ✓ (0.060), S0n ≈ 0.65 ✓ (0.657), G1 at R0's level ✓; S3 corrected scale ≈ 2.4 at
100 GeV predicted, measured 2.81 at 100 GeV (direction and size right, value off by 17 %: the predicted
number used R0's raw/true 0.56, P1f collects 0.72); no photon tagged ✓ (γ-tag 0.034, as R0 0.031).
"S0 close to R0 + P1a + P1b": ✓ in direction — P1f's S0all (0.029) lies between P1b (0.048, the threshold gain) and
P1a (0.010, the nlr-3 loss), and S0n matches both (0.657 vs 0.658 / 0.654).
guards (vs R0, the program's current best): G4 PASS (static; D5); S2 scale out with the PR coefficients
(median 3.30), after the 420 refit (a = 1.768, b = 0.918, χ² 76/6 — the same as R0's refit 1.758 / 0.920)
residuals 0.964–1.015, in; S3 raw sum up +0.014 (275 GeV) to +0.44 (20 GeV): in under the one-sided guard (D-user-12), σ/mean better at every
momentum (R0 2.44 / 0.72 / 0.24 / 0.15 / 0.15 / 0.12 → 0.28 / 0.19 / 0.17 / 0.13 / 0.13 / 0.12 at 20–275 GeV); S3 clusters per neutron 0.82 → 1.08 (+0.26, in); S4b n/a; S4c in;
G1 in (0.067 / 0.062 vs 0.15; columns 0); G2 in (−12 % / −17 % vs −50 %); G3 in (0.111 / 0.079).
verdict: REJECTED vs R1 (S0γ falls significantly at every momentum); against R0 also REJECTED by the letter
of the rule (S0γ −0.011 / −0.0085 significant at 225 / 275 GeV), despite S0all +0.044 at 100 GeV; every guard is in.
understanding: removing the distance undoes all of G1–G3 and of R1's S0γ gain and S0n loss: those effects
belong to the distance (H1, the distance half). What remains — nlr 3 and the 5 MeV / 2-hit thresholds at
3×3 — is a different clustering from R0: more of the event's energy stays in clusters (S3 raw sum up,
strongly at low energy), and S0all rises at 100–150 GeV where the decay photons are far enough apart that
R0's cut was dropping one of them. The PR's coefficients are wrong for 3×3 clusters by a factor 2.1–4.1
(n) and 3.6–10.5 (γ), as predicted.
next: P1a and P1b split this gain between nlr 3 and the threshold pair. The S0all gain at 100–150 GeV with
G1–G3 at R0's level is the best lead of Phase 1 for Phase 2 (backlog B1–B3). Q8 (the raw-sum band rejected
more containment) closed by the user: one-sided (D-user-12).
re-judged (2026-11-05, after D-user-16/17): S2 in; photon raw sum D2 +0.2 to +3.9 % vs R0, in; verdict unchanged, REJECTED (S0γ −0.011 / −0.009 at 225 / 275 GeV vs R0).

## R2 2026-11-05: reference R2 = R0 + PR eic/EICrecon#3114 (gammaMaxLength 100 → 110, gammaMaxWidth 12 → 22 mm)
tier: parameter (reference row, D-user-15; not a Phase 1 dissection run)
config: configs/experiments/R2_pr3114.yaml
hypothesis (written 2026-11-05 10:10, while R2's reco ran, before any R2 output was read; informed by the cut-box pass fractions that
`430_shape_decayz.py` computes from R0's own clusters): clustering is R0's, so every S0, S1a, S3 raw-sum and
G1–G3 cell is identical to R0 (Δ = 0 exactly). The neutrals change: D2 γ-tag 0.03 → 0.88–0.99 per energy;
D3 mistag 0 → up to 0.09 at 20–50 GeV, < 0.01 above 150 GeV; S2 then runs on the stock photon law, 13–31 % low
(F6) — S2 out until a refit. D4: only 5–9 % of the truth-best photon clusters pass even the new box (87–98 % of
the pairs are merged), so S4a_tm stays ≤ 0.005 at every momentum (the F4 ceiling allows 0–0.068); S4a_any and
S4c rise (more photon candidates, combinatorics); S5 on D6a rises from 0 but stays well below R1's 21 per 1000.
The cut box is necessary for Λ on 3×3 clusters, not sufficient.
expected cost: R0's T, all datasets incl. D6a; ~1 h on 18 jobs
--- after the run (2026-11-05, analysis finished 17:43 UTC; S5 rerun after /data filled, D-user-19) ---
row: R2_pr3114 (scoreboard.csv; metrics-R2_pr3114.json, calib-, shape-R2_pr3114.json); paired against R0_stock
result: every clustering cell equals R0's exactly (D4 S0all/S0γ/S0n and D1 S1a: gained 0, lost 0 at every momentum;
D3 raw sum, D2 photon raw sum, D5 G1–G3 and clusters/event identical) ✓. D2 γ-tag 0.03 → 0.932 / 0.975 / 0.977 / 0.976
/ 0.973 / 0.960 / 0.930 / 0.871 (20–275 GeV) ✓ (predicted 0.88–0.99; 275 GeV just under). D3 mistag 0 → 0.011 / 0.059 /
0.029 / 0.009 / 0.003 / 0.000 (20–275 GeV) ✓ (peak at 50 GeV, not 20). S2 on the stock photon law: scale median
0.72–0.87 (13–28 % low) ✓; refit γ a = 1.758, b = 0.920 (χ² 65/6), residuals 0.953–1.014 (20 GeV at −4.7 %); neutron
refit a = 2.079, b = 0.911. D4: S4a_tm = S4a_any = 0 at every momentum ✓ (predicted ≤ 0.005); S4c 0.002 → 0.073–0.135
γ-tagged neutrals per Λ event ✓. S5 on D6a (msf-R2_pr3114-*.json): 9x275 0 → 1.0 candidates per 1000 (5 in 5000; 0.4 per 1000 in the mass window), 0 of the 23 truth Λ in acceptance matched; D6a_local 0 (R0 0, R1 3.5) ✓ (predicted: up from 0, well below R1's 21.2).
guards: G4 PASS (D5 static, every chunk identical outside the ZDC chain); G1–G3 as R0; S3 raw sum unchanged; S2 in only
after the refit (as predicted). A reference row has no verdict.
understanding: PR 3114's box does what it says for single photons (tag efficiency 0.87–0.98, mistag ≤ 0.06), and on
R0's clustering it yields no Λ at all: the photon pairs are merged (decay-position view: 87–98 % of pairs), so there is
nothing for the box to pass. The box is necessary, not sufficient — the clustering decides; L01 measures the same box on
the current best.

## Phase 2 — the parameter loop (started 2026-11-05 15:35 UTC, D-user-18)

Step 0 (written 2026-11-05 15:38 UTC, before any Phase 2 reconstruction):
- **Current best**: E01 = P1b (R0 + `minClusterCenterEdep` 5 MeV, `minClusterNhits` 2; ACCEPTED by the rule after
  D-user-16/17). Rule 6: P1b's refit coefficients γ (1.765, 0.919), n (2.221, 0.897) belong to it; they are recorded
  in `configs/experiments/E01_P1b_adopt.yaml` but not reconstructed (option b): every acceptance cell is a clustering
  cell or judged after a per-clustering refit, and no 3×3 photon is tagged with the stock box. Reference reco for the
  paired tests and the gate: `P1b_R0_thr`.
- **Held-out criterion for E01, pre-registered** (rule 8; D1h/D4h reconstructions of R0 and P1b running): on D4h
  (125 / 175 / 250 GeV, seed 101) the paired Δ S0all (P1b − R0) is significant and positive at ≥ 2 of the 3 momenta,
  and no S0 component falls significantly at any; on D1h (50 / 70 / 100 GeV) S1a_truth_all does not fall
  significantly at any momentum. Otherwise E01 is reverted to R0 and every experiment based on it is re-run on R0.
- **Noise floor**: `space/perf/noise-validation.json` — R0 and R1, 26 metric tests over 3 seeds, spread / quoted
  error 0.26–1.97, none below p = 0.01: the paired-test errors of 400 are honest; 3σ as the significance line.
- **Parallel runs**: two single-change experiments from the same current best may run at once. If both are ACCEPTED,
  the one with the larger S0all gain (summed over momenta) becomes the best and the other is re-run on top of it as a
  new entry (one change per experiment holds).
- **Order of the backlog, revised with the Phase 1 views** (the backlog was written before them): on P1b at 100 GeV
  the photon pairs are merged in 0.89 and missing in 0.03 of events, at 275 GeV 0.97 / 0.01. B1/B2 (seed, size)
  can only recover the missing 1–3 %; the merging is B3's (chaining threshold) and Phase 3's. A third survival
  threshold not in the backlog, `minClusterEdep` (50 MeV = 1.83 GeV calibrated), bounds any seed/size scan: a group
  with a 2 MeV seed and under 50 MeV total still dies. Order: B3 first; B1 paired with `minClusterEdep` (B1′);
  B2 after; B4–B6 as written.
- **The Λ family beside the loop** (D-default-25): current best + PR 3114's box is parameter-only, changes no
  cluster, and is judged on S4a_tm; it runs when the machine frees (L01).

## E01 2026-11-05: adopt P1b as the current best
tier: parameter (adoption of a Phase 1 result; no new reconstruction)
config: configs/experiments/E01_P1b_adopt.yaml
hypothesis: as P1b (ledger above); the held-out check reproduces the search-set gain (criterion in Step 0).
expected cost: held-out recos of R0 and P1b (D1h, D4h: 12 files, ~30 min)
--- after the run (2026-11-05 16:15 UTC) ---
row: P1b_R0_thr (search-set row, Phase 1); held-out: space/perf/heldout-P1b_R0_thr-vs-R0_stock.json
result (held-out, seed 101, paired against R0 by `scripts/405_heldout_check.py`, written for this check because
400's paired section covers only D1_pi0 / D4_lambda): D4h S0all +0.059 / +0.031 / +0.012 at 125 / 175 / 250 GeV
(z 10.8 / 7.9 / 4.8; gained 116 / 62 / 23, lost 0); S0γ +0.071 / +0.035 / +0.017 (lost 0); S0n +0.006 / 0 / +0.0005.
D1h S1a_truth_all +0.085 / +0.050 / +0.024 at 50 / 70 / 100 GeV (lost 0). Search set at the same momenta: S0all
+0.056 / +0.028 / +0.017 — the held-out gain matches within errors.
guards: as P1b (all in after D-user-16/17); G4 PASS (Phase 1).
verdict: ACCEPTED — the pre-registered held-out criterion holds (3 of 3 D4h momenta significant and positive, nothing
falls); E01 (P1b + its refit calibration, recorded) is the current best.
understanding: the lower seed / size thresholds only add clusters; the gain is the soft Λ photons that had no
surviving cluster, and it is a property of the clustering, not of the seeds.
next: E02 (chaining threshold, B3) and E03 (cluster-energy floor, B1′) from E01, running.

## E02 2026-11-05: chaining threshold minClusterHitEdep 315 → 480 keV (B3), on E01
tier: parameter
config: configs/experiments/E02_chain480.yaml
hypothesis (written 2026-11-05 15:40 UTC, before the run): subcells below 480 keV no longer join clusters. Measured on
the current best before the run: subcells in [315, 480) keV are 19–21 % of the clustered subcells and carry 1.0–2.0 %
of the photon energy (D2 100 / 20 GeV), 2.6–4.2 % of the neutron energy (D3 200 / 50 GeV), 2.7 % in Λ events (175 GeV).
These low-energy subcells are the halo that bridges the two photons and the neutron (merged in 0.89–0.97 of P1b's
Λ events). Predicted: S0γ up at 175–275 GeV by +0.01 to +0.03 (significant at ≥ 2 momenta), S0all up at ≥ 175 GeV by
+0.003 to +0.01, n.s. at 100–125 GeV; S0n within ±0.02; D2 photon raw sum −1 to −3 % (in), D3 neutron raw sum −2 to −5 %
(at the edge at 20–50 GeV); clusters per event on D5 up 5–20 %, G3 still < 0.5; G1 unchanged. Fails if the bridges are
mostly above 480 keV (S0γ n.s.).
expected cost: ~8 CPU-h (D1–D5), ~1 h wall at 9 jobs
--- after the run (2026-11-05, analysis finished 20:45 UTC after the /data fill and a chunk rerun) ---
row: E02_chain480 (scoreboard.csv; metrics-, truth-, calib-, shape-E02_chain480.json); paired against P1b_R0_thr
result: D4 S0all +0.016 / +0.016 / +0.020 / +0.015 / +0.017 / +0.017 / +0.018 / +0.012 (100–275 GeV), significant at
every momentum (z 4.8–6.1; gained 23–40, lost 0–3); S0γ +0.024 to +0.038 (z 9.8–12.1, lost 0–10); S0n −0.004 to −0.024,
significant at 275 GeV only (−0.0236, z −5.8; gained 9, lost 56). D1 S1a_truth_all +0.082 / +0.226 / +0.193 / +0.089 /
+0.030 / +0.014 / +0.006 (50–160 GeV), significant everywhere. Decay-position view: merged pairs 0.891 → 0.868 (100 GeV),
0.933 → 0.915 (175), 0.974 → 0.960 (275); photon missing 0.034 → 0.041 at 100 GeV. D5 clusters/event 0.733 → 0.816
(Q² > 100), 1.244 → 1.472 (Q² > 0).
Hypothesis check: S0γ up at 175–275 GeV by +0.01 to +0.03 ✓ (+0.024 to +0.032; also at 100–150, not predicted);
S0all at ≥ 175 GeV +0.003 to +0.01 ✗ (+0.012 to +0.017, larger); n.s. at 100–125 GeV ✗ (significant); S0n within ±0.02 ✗
at 275 GeV (−0.024); D2 photon raw sum −1 to −3 % ✓ (−0.6 to −1.8 %); D3 neutron raw sum −2 to −5 % ✗ (−13.4 / −8.3 /
−6.1 / −4.9 / −4.3 / −3.6 % at 20–275 GeV: P1b 0.500 / 0.616 / 0.680 / 0.721 / 0.737 / 0.760 → 0.433 / 0.564 / 0.639 /
0.686 / 0.705 / 0.732); D5 clusters/event +5–20 % ✓ (+11 / +18 %); G3 < 0.5 ✓; G1 unchanged ✓.
guards: G4 PASS (D5 static compare, every chunk); S2 after the refit in at every energy (γ a = 1.826, b = 0.914;
n a = 2.529, b = 0.879, χ² 61/4); D2 photon raw sum in (≤ 1.8 % drop); S3 raw sum OUT at 20 / 50 / 100 GeV (one-sided
limit 5 %, D-user-12); S3 clusters per neutron 1.162 → 1.321 in (+0.16, limit +0.5); mistag 0; G1 in (φ@180 0.056 /
0.063, columns ≤ 0.001); G2 in (E > 50 GeV fraction −15 % / −16 %, limit −50 %); G3 in (0.167 / 0.324).
verdict: REJECTED — S0all gains significantly at all 8 momenta, but the neutron raw sum drops up to 13 % (limit 5 %) and S0n falls significantly at 275 GeV.
understanding: the halo subcells in [315, 480) keV do bridge photons to each other and to the neutron — cutting them
separates 2–3 % more photons at every momentum and unmerges 1.5–2 % of the Λ pairs. The same subcells are a large part
of the low-energy neutron shower (13 % of its clustered energy at 20 GeV, more than the 4.2 % measured on P1b's subcells
before the run: losing them also breaks the neutron cluster into pieces below the survival thresholds, which are then
discarded), so the cost is the neutron energy, not the photon one. The threshold separates bridges and neutron
halo equally; it cannot select between them.
next: revive on a different premise — keep low hits out of the chaining but attach them afterwards to the cluster they
neighbour (code tier, Phase 3: "chain at 480 keV, collect at 315 keV"), which predicts E02's separation with P1b's raw
sum. A parameter step between (400 keV) predicts roughly half of both, and the raw sum at 20 GeV would still be at the
limit — lower priority.

## E03 2026-11-05: cluster-energy floor minClusterEdep 50 → 20 MeV (B1′), on E01
tier: parameter
config: configs/experiments/E03_clEdep20.yaml
hypothesis (written 2026-11-05 15:40 UTC, before the run): a connected group survives only with ≥ 50 MeV of subcell
energy (≈ 1.8 GeV of photon energy at sampling fraction 0.0273). The softest Λ-daughter photons (a few % below 2 GeV
at 100 GeV) and their isolated fragments die there; P1b leaves 3.4 % of 100 GeV events with a photon without any
cluster, 0.8 % at 275 GeV. Predicted: S0γ up by +0.002 to +0.01 at 100–125 GeV (significant at most at 100 GeV),
n.s. above; S0all n.s. or ≤ +0.005; S0n unchanged; raw sums up slightly (in); G3 (clusters < 5 GeV per event) up,
SIDIS 0.18 → 0.25–0.4, inside 0.5; the "missing" category at 100 GeV 0.034 → ≤ 0.025. A small, mostly null result:
it measures how much of B1/B2's headroom the floor holds.
expected cost: as E02
--- after the run (2026-11-05, analysis finished 19:52 UTC) ---
row: E03_clEdep20 (scoreboard.csv; metrics-, truth-, calib-, shape-E03_clEdep20.json); paired against P1b_R0_thr
result: D4 S0all +0.013 / +0.007 at 100 / 125 GeV (z 5.0 / 3.7, lost 0), +0.001 to +0.004 n.s. above; S0γ +0.017 /
+0.011 / +0.007 / +0.007 / +0.004 / +0.004 / +0.003 / +0.002 (100–275 GeV), significant everywhere, lost 0; S0n unchanged
(≤ 2 events lost). D1 S1a_truth_all +0.001 to +0.003, n.s. everywhere. Photon missing (decay-position view) 0.034 → 0.022
at 100 GeV, 0.016 → 0.011 at 175, 0.008 → 0.006 at 275. D3 raw sum up +0.016 to +0.004 (20–275 GeV). D5: clusters/event
0.733 → 1.020 (Q² > 100), 1.244 → 2.032 (Q² > 0); clusters < 5 GeV per event 0.110 → 0.398, 0.182 → 0.970.
Hypothesis check: S0γ +0.002 to +0.01 at 100–125 GeV, significant at most at 100 ✗ (+0.017 / +0.011, significant at all
momenta though small above 150); S0all ≤ +0.005 ✗ (+0.013 at 100 GeV); S0n unchanged ✓; raw sums up slightly ✓;
missing at 100 GeV ≤ 0.025 ✓ (0.022); G3 SIDIS 0.25–0.4 ✗ (0.970); "small, mostly null" ✗ for S0 at 100–125 GeV, ✓ above.
guards: G4 PASS; S2 after the refit in (photon refit unchanged, a = 1.765, b = 0.919; n a = 2.201, b = 0.898); D2 photon
raw sum unchanged; S3 raw sum rises (passes, one-sided); S3 clusters per neutron OUT (1.162 → 1.854, +0.69, limit +0.5);
G1 in (φ@180 0.091 / 0.109 ≤ 0.15, columns 0.019 / 0.029 ≤ 0.05); G2 in (−28 % / −39 %, limit −50 %); G3 OUT on Q² > 0
(0.970, limit 0.5; Q² > 100 0.398 in).
verdict: REJECTED — S0all gains significantly at 100–125 GeV, but G3 (0.97 low-energy clusters per SIDIS event, limit 0.5) and clusters per neutron (+0.69, limit +0.5) are out.
understanding: the 50 MeV floor holds most of the soft-photon headroom P1b left (missing 3.4 % → 2.2 % at 100 GeV): the
photon gain is real and costs nothing on the Λ side. What it lets through on DIS and neutron events is mostly neutron
shower fragments and low-energy debris — 0.8 extra clusters per SIDIS event, 0.7 per neutron — which the floor exists
to remove. The floor cannot tell a 1 GeV photon from a 1 GeV neutron fragment.
next: an intermediate floor (30–35 MeV) is the parameter-tier test; G3 grows faster than the photon gain (0.18 → 0.97
for 1.2 % of photons), so the expected trade is poor. Better: keep the floor and attach sub-floor groups to the nearest
surviving cluster (code tier, with E02's re-attach idea) or select sub-floor groups by their shape (a photon is compact).

## L01 2026-11-05: Λ family — current best + PR 3114's photon box (110 / 22 mm), with the current best's refit calibration
tier: parameter (Λ family, D-default-25: selector S4a_tm under the fixed scoring window; S0 unchanged by construction)
config: configs/experiments/L01_box3114.yaml
hypothesis (written 2026-11-05 15:43 UTC, before the run): clustering is P1b's, so every S0, S1a, raw-sum and G1–G3
cell equals P1b's (Δ = 0). With the box, P1b's single photons are tagged (D2 pass 0.88–0.99 from the shape view) and
with the refit law their scale is within ±5 % (S2 in). In Λ events only 5–14 % of the truth-best photon clusters pass
(the rest are merged), both photons must pass, the π⁰ window sees IP-pointing momenta (F4 ceiling 0 at 100–125 GeV,
≤ 0.068 at 275 GeV), so S4a_tm rises from 0 to ≤ 0.005 per momentum — likely significant only at 225–275 GeV if
at all. S4a_any − S4a_tm (untruthful candidates) stays ≤ 0.005; S4c (γ-tagged neutrals per Λ event) 0.008 → 0.1–0.3.
S5 on D6a: from 0 to a few candidates per 1000 at 9x275, below R1's 21. The run shows the box is necessary and the
merging (Phase 2/3 clustering) and the preselection (F4, B9d) are the limits.
expected cost: ~9 CPU-h incl. D6a; launched after the held-out recos
--- after the run (2026-11-05, analysis finished 20:45 UTC; scoreboard rerun after timing.csv lost its header in the disk-full crash, rebuilt from the per-file JSONs) ---
row: L01_box3114 (scoreboard.csv; metrics-, truth-, shape-L01_box3114.json, msf-L01_box3114-*.json); paired against P1b_R0_thr
result: S4a_tm (= S4a_any: no untruthful candidate) 0 / 0 / 0.0005 / 0 / 0.0040 / 0.0035 / 0.0025 / 0.0020 (100–275 GeV);
paired against P1b gained 1 / 0 / 8 / 7 / 5 / 4 at 150–275 GeV, lost 0, z ≤ 2.8 at every momentum (none significant;
pooled over momenta 25 vs 0, z 5.0 — not the pre-registered selector). Every S0, S1a, raw-sum, G1–G3 cell equals P1b's ✓.
D2 γ-tag 0.031 → 0.871–0.977; with P1b's refit law the photon scale median is 0.971–1.012 (S2 in); D3 mistag 0 → 0.014 /
0.047 / 0.024 / 0.007 / 0.002 / 0 (20–275 GeV). S4c 0.29 / 0.26 / 0.23 / 0.20 / 0.19 / 0.18 / 0.16 / 0.13 γ-tagged
neutrals per Λ event. In Λ events the box passes 14 / 9.5 / 5.3 % of the truth-best photon clusters at 100 / 175 / 275 GeV.
S5 (D6a): 9x275 1.2 candidates per 1000 (0.6 in the mass window), 0 of 23 truth Λ in acceptance; D6a_local 0.5 per 1000.
Hypothesis check: S0/S1a/raw-sum/G Δ = 0 ✓; D2 tagged and S2 in with the refit law ✓; S4a_tm from 0 to ≤ 0.005 per
momentum ✓ (max 0.004), "likely significant only at 225–275 GeV if at all" — not significant at any ✓; untruthful ≤ 0.005
✓ (0); S4c 0.1–0.3 ✓; S5 a few per 1000 at 9x275, below R1's 21 ✓ (1.2).
guards: G4 PASS (D5 static; only the neutrals and Λ collections move); S0 unchanged; untruthful-candidate fraction
unchanged (0); S4b n/a (≤ 8 Λ per momentum); S2 in after P1b's refit; S5 reported.
verdict: INCONCLUSIVE — S4a_tm rises in the right direction at 200–275 GeV (25 gained, 0 lost in total) but no momentum is significant at 3σ with 2000 events per point.
understanding: the box is necessary — without it no 3×3 photon is tagged and S4a is 0 — and nearly sufficient for what
the clustering allows: 0.002–0.004 Λ per event at 200–275 GeV is 6–8 % of the F4 ceiling (0.030–0.068), set by the
5–14 % of truth-best photon clusters the box can see unmerged. Statistics, not the box, decide the verdict.
next: resolve it with statistics, not by pooling after the fact — pre-register L01's test on D4h (the held-out seed,
125 / 175 / 250 GeV, 6 files) with the pooled selector over momenta ≥ 150 GeV, or keep the box as a standing part of
every later Λ-family test on a clustering that unmerges more photons (E02's re-attach variant).

## E04 2026-11-05: chaining threshold minClusterHitEdep 315 → 400 keV (chaining family, second point), on E01
tier: parameter
config: configs/experiments/E04_chain400.yaml
hypothesis (written 2026-11-05 21:30 UTC, before the run): half of E02's step. Measured on the current best before the run
(`HcalFarForwardZDCSubcellHits`, subcells ≥ 315 keV): [315, 400) keV holds 2.8 / 2.2 / 1.7 % of the neutron subcell energy
at 20 / 50 / 100 GeV (E02's [315, 480): 5.4 / 4.2 / 3.3 %), 1.1 % for 20 GeV photons (2.0 %), 1.4 % in Λ events at
175 GeV (2.7 %). In E02 the neutron raw sum fell 2.5 / 2.0 / 1.8 × the direct share (fragments that lose their chaining
subcells die at the survival thresholds). Mechanism as E02: the bridges are partly in this band. Predicted: S0all
+0.006 to +0.010 at every momentum (significant at ≥ 4 of 8), S0γ +0.012 to +0.019 (significant everywhere), S0n
−0.003 to −0.012, n.s. except possibly 275 GeV; D1 S1a_truth_all about half of E02's (+0.1 at 60–70 GeV); D3 raw sum
−7 / −4 / −3 % at 20 / 50 / 100 GeV (20 GeV at or just past the 5 % limit), D2 photon raw sum −0.3 to −1 %; G1–G3 in.
If the fragment loss is super-linear in the threshold, the 20 GeV drop is ≤ 5 % and E04 is ACCEPTED; if linear, it is
REJECTED at 20 GeV and the chaining family's parameter ceiling is recorded (rule 7) with the re-attach idea for Phase 3.
expected cost: ~8 CPU-h (D1–D5), ~1 h 20 min wall at 9 jobs; 63 GB on /data (417 GB free)
--- after the run (2026-11-05; reco finished 22:32 UTC; analysis stopped 23:30 UTC on D-user-21 at the plot step, every number below was already written; plots finished 2026-11-06 on the user's "finish E4, E5 analysis") ---
row: E04_chain400 (scoreboard.csv; metrics-, truth-, calib-, shape-E04_chain400.json); paired against P1b_R0_thr
result: D4 S0all +0.0071 / +0.0096 / +0.0101 / +0.0060 / +0.0110 / +0.0090 / +0.0075 / +0.0055 (100–275 GeV), significant
at every momentum (z 3.3–4.7; gained 11–22, lost 0–1); S0γ +0.011 to +0.020 (z 6.7–8.8); S0n −0.001 to −0.012, significant
at 275 GeV only (−0.0121, z −4.1; gained 5, lost 29). D1 S1a_truth_all +0.054 / +0.117 / +0.092 / +0.043 / +0.012 /
+0.005 / +0.003 (50–160 GeV), significant except 160 GeV. S4a_tm 0 at every momentum (as P1b). Headline per thrown
Λ → nπ⁰: separation 0.76 % (P1b 0.62 %), Λ reco 0.00 % (P1b 0.00 %).
Hypothesis check: S0all +0.006 to +0.010, significant at ≥ 4 of 8 ✓ (+0.006 to +0.011, all 8); S0γ +0.012 to +0.019,
significant everywhere ✓ (+0.011 to +0.020); S0n −0.003 to −0.012, n.s. except possibly 275 GeV ✓ (significant at 275
only); D1 about half of E02 ✓ (+0.117 vs +0.226 at 60 GeV, +0.092 vs +0.193 at 70); D3 raw sum −7 / −4 / −3 % ✓
(−7.6 / −4.6 / −3.3 / −2.6 / −2.3 / −1.9 % at 20–275 GeV); D2 photon raw sum −0.3 to −1 % ✓ (−0.4 to −1.0 %); G1–G3 in ✓.
The "linear" branch of the hypothesis held: −7.6 % at 85 keV above P1b, −13.4 % at 165 keV (E02), 0.089 and 0.081 % per keV.
guards: G4 PASS (62 of 62 D5 files, 9043 non-ZDC leaves identical); S2 after the refit in at every energy (γ a = 1.809,
b = 0.915; n a = 2.434, b = 0.883); D2 photon raw sum in; S3 raw sum OUT at 20 GeV (−7.6 %, one-sided limit 5 %), in
at 50 GeV (−4.6 %) and above; σ/mean unchanged; S3 clusters per neutron 1.162 → 1.258 in (+0.10, limit +0.5); mistag 0;
G1 in (φ@180 0.064 / 0.058, columns ≤ 0.0003); G2 in (E > 50 GeV fraction 0.612 / 0.423 vs R0 0.864 / 0.612: −29 % /
−31 %, limit −50 %); G3 in (0.270 / 0.145). D5 clusters/event 1.244 → 1.381 (Q² > 0), 0.733 → 0.785 (Q² > 100).
verdict: REJECTED — S0all gains at all 8 momenta, but the neutron raw sum drops 7.6 % at 20 GeV (limit 5 %) and S0n falls significantly at 275 GeV, as pre-registered for a linear fragment loss.
understanding: halving E02's step halves both its gain and its cost; the neutron loss is linear in the chaining
threshold over 315–480 keV, so no point in the range buys separation without the neutron energy. By linear
interpolation (not measured) the 5 % limit at 20 GeV sits near 370 keV, where S0all would gain about +0.004 per
momentum — below the per-momentum significance this sample resolves.
family ceiling (rule 7: E02 REJECTED, E04 REJECTED, consecutive): the chaining threshold minClusterHitEdep is closed at
P1b's 315 keV. The halo subcells bridge photons and also make up the low-energy neutron shower; a threshold cannot tell
them apart. Revive only on a different premise: B11 (chain high, attach the low subcells afterwards), code tier.
retention: reco ROOT deleted 2026-11-05 23:55 UTC (D-user-19); JSON, npz, timing.csv kept.

## E05 2026-11-05: seed threshold minClusterCenterEdep 5 → 2 MeV (survival-threshold family, second point after E03), on E01
tier: parameter
config: configs/experiments/E05_seed2.yaml
hypothesis (written 2026-11-05 21:30 UTC, before the run): a connected group survives with ≥ 1 subcell above the seed,
≥ 2 subcells and ≥ 50 MeV in total. E03 showed the 50 MeV floor is the binding cut for soft photons (missing 3.4 → 2.2 %
at 100 GeV). A group with ≥ 50 MeV but every subcell below 5 MeV needs ≥ 10 diffuse subcells: that is a neutron-shower
fragment, rarely a photon (a photon group that passes the floor carries ≥ 1.8 GeV, i.e. ≥ 50 MeV deposited at sampling
fraction 0.027, in a compact core of few subcells, so its highest subcell is very likely above 5 MeV). Predicted: S0γ, S0all, S1a Δ ≤ +0.003, not significant at any momentum; S0n unchanged;
clusters per neutron +0.0 to +0.1; G3 up ≤ 0.05; raw sums up ≤ 0.5 %. A null result closes the survival-threshold
family (P1b accepted, E03 rejected, E05 n.s.: rule 7) — the photon headroom below the floor (≤ 1–3 % of photons) is
not reachable by thresholds without the neutron fragments.
expected cost: as E04
--- after the run (2026-11-05; reco finished 22:32 UTC; analysis stopped 23:30 UTC on D-user-21 at the plot step, every number below was already written; plots finished 2026-11-06 on the user's "finish E4, E5 analysis") ---
row: E05_seed2 (scoreboard.csv; metrics-, truth-, calib-, shape-E05_seed2.json); paired against P1b_R0_thr
result: D4 S0all +0.0010 / 0 / +0.0005 / 0 / +0.0005 / 0 / 0 / 0 (100–275 GeV; gained 0–2, lost 0), not significant
anywhere; S0γ ≤ +0.0010 (gained ≤ 4, lost 0), n.s.; S0n no event changed at any momentum. D1 S1a_truth_all ≤ +0.0005
(≤ 1 event gained), n.s. S2 scale unchanged (|Δ| < 10⁻⁵). S4a_tm 0. Headline per thrown Λ → nπ⁰: separation 0.63 %
(P1b 0.62 %), Λ reco 0.00 %.
Hypothesis check: S0γ, S0all, S1a Δ ≤ +0.003, n.s. at every momentum ✓; S0n unchanged ✓ (identical); clusters per
neutron +0.0 to +0.1 ✓ (1.162 → 1.172); G3 up ≤ 0.05 ✓ (+0.010 / +0.006); raw sums up ≤ 0.5 % ✓ (D3 +0.4 % at 20 GeV,
≤ +0.1 % above; significant at 20, 100, 200 GeV but inside the prediction; D2 photon raw sum ≤ +0.01 %).
guards: G4 PASS (62 of 62 D5 files); S2 after the refit in at every energy (γ a = 1.762, b = 0.919; n a = 2.214,
b = 0.898); D2 photon raw sum in; S3 raw sum in (rises only, σ/mean not worse); S3 clusters per neutron in (+0.010);
mistag 0; G1 in (φ@180 0.068 / 0.061); G2 in (0.680 / 0.463, −21 % / −24 % vs R0); G3 in (0.193 / 0.116).
verdict: INCONCLUSIVE — no S0 or S1a cell moves significantly; the null result was the pre-registered prediction.
understanding: below P1b's 5 MeV the seed is no longer the cut that removes clusters; the 50 MeV cluster floor
(E03) and the 2-hit minimum are. The few groups the lower seed revives are diffuse neutron-shower fragments
(clusters per neutron +0.01, D3 raw sum +0.4 % at 20 GeV), not photons.
family ceiling (rule 7: E03 REJECTED, E05 not significant, consecutive): the survival thresholds (minClusterCenterEdep,
minClusterEdep, minClusterNhits) are closed at P1b's values (5 MeV, 50 MeV, 2). The photons below the floor
(≤ 1–3 % at 100 GeV) cannot be reached by thresholds without the neutron fragments.

## Backlog

Seeded by Phase 1 (2026-11-05), ordered. Base for B1–B6: P1b (R0 + 5 MeV seed / 2-hit size, the stock 3×3
distance, nlr 1), if Q10 lets it be adopted after the held-out check; otherwise R0. Each entry: the change, the
mechanism, the predicted S0 effect. Phase 2 (parameters) is B1–B6; Phase 3 (code) is B7–B8; B9 is the Λ
family (D-user-14, D-default-25); B10 is a ruler fix.

- **B1 — seed threshold `minClusterCenterEdep` scan at 3×3** (25 → 10 → 5 → 3 → 1 MeV; the paper uses 3 MeV).
  Mechanism: a group survives only with one hit above the seed; the soft Λ photons' own groups at 100–150 GeV
  are the ones that die (P1b: gained 136, lost 0 at 100 GeV). Prediction: S0γ and S0all up at 100–150 GeV,
  saturating below ~5 MeV; G3 (clusters < 5 GeV per event) rises toward its 0.5 limit — the limit is the stop.
- **B2 — size threshold `minClusterNhits` scan at 3×3** (10 → 5 → 2 → 1, seed at B1's best; the paper keeps 30
  subcell hits). Mechanism: as B1, for small groups whose seed passes; the switch test found it inert on R0 at
  the 25 MeV seed, so it acts only after B1. Prediction: small S0γ gain at 100 GeV (≤ +0.02), more G3.
- **B3 — chaining threshold `minClusterHitEdep` scan** (0.5 → 1 → 2 → 4 MIP-equivalent per subcell,
  80–640 keV; the paper drops subcells below 50 keV). Mechanism: low-energy halo subcells bridge the two photons
  and the neutron at 3×3 — the decay-position view shows 87–98 % of R0's photon pairs "in clusters, not both
  separated" — and a higher chaining threshold cuts the bridges without shortening the reach. Prediction:
  S0γ up at 175–275 GeV (where the merging is), S0n roughly unchanged, raw sum down a few % (the one-sided
  S3 guard is the stop).
- **B4 — `neighbourLayersRange` 2 at 3×3** (P1a: 3 costs S0γ −0.014 to −0.027 with gained 0; P1d: 1 is slightly
  better on columns). Prediction: between 1 and 3, likely worse than 1; one run to close the family.
- **B5 — HEXPLIT `Emin_in_MIPs`, `delta_in_MIPs`** (subcell energy sharing: what each subcell gets decides
  which halo subcells pass B3's threshold and the cluster widths). Prediction: second-order on S0; changes the
  w_T distribution (cluster-shape view), so it interacts with the photon cut box (B9).
- **B6 — `sectorDist`** (10 cm). Prediction: no effect inside one ZDC module; one run as a check, then closed.
- **B7 — the XY distance, code tier**: 1×1 (P1c: half of R1's S0γ gain at 175 GeV, and the column guards fail),
  3×3 (stock), 5×5 (≥ 48.8 mm), and split reaches: same-layer 3×3 with diff-layer 1×1 (photon cores are narrow
  along z, neutron showers wide). Prediction: a split reach separates the photons without the 1×1 collapse of
  S0n; full G4 on every dataset.
- **B8 — the Island chain with `splitCluster = true` feeding the CoG** (Phase 3 first candidate, D-default-20).
  Mechanism: splitting at local maxima separates merged γγ / γn showers without single-column clusters.
  Prediction: the largest S0γ gain with S0n and G1–G3 preserved; full G4.
- **B9 — the Λ family** (D-user-14, D-default-25; S4a_tm as selector, S0 unchanged): (a) the photon cut box —
  PR 3114's 110 / 22 mm (R2), then `gammaMaxWidth` / `gammaMaxLength` per clustering from the cluster-shape view
  (Q7 option C); (b) the z cut measured from the front (F7: offset −616 mm, i.e. front + 300 mm); (c) the
  calibration form (F6: a·E^b misses the photon points; refit per clustering, never on S4a); (d) the
  IP-pointing π⁰ preselection (F4): a vertex-aware pairing or widening `pi0Window` with the vertex iteration
  first, judged on S4a_tm under the fixed scoring window. Prediction: (a) is necessary for any Λ on 3×3
  clusterings; (d) lifts the ceiling of F4 (0–0.068) itself.
- **B10 — the truth-cluster chain** (Phase 0 O2): make `HcalFarForwardZDCTruthClusters` a perfect-clustering
  input (subcell hits, the real sampling fraction) so the Rt row measures S4a's ceiling inside EICrecon, beside
  the offline one of `412_lambda_ceiling.py`.
- **B11 — chain high, collect low** (from E02/E03, code tier): build connected components with a raised chaining
  threshold (480 keV) and survival floor, then attach the sub-threshold subcells and sub-floor groups to the cluster
  they neighbour. Prediction: E02's separation gain (S0all +0.012 to +0.020 at every momentum) with P1b's neutron raw
  sum (E02's −13 % at 20 GeV recovered) and no G3 growth.
- **B9d, measured (2026-11-05, `414_lambda_ceiling_variants.py`, F9)**: a vertex-aware pairing needs a stable vertex
  (the pin's IDOLA diverges for distant decays). With perfect separation and P1b's resolution it reaches 73–85 % of
  accepted D4 events (1.2–27.8 % per thrown Λ → nπ⁰, acceptance 1.6–32.6 %) against 0–6.5 % (0–2.1 %) for the stock
  pairing: the largest single lever on Λ, independent of the clustering.

## Phase 3 — the Λ chain, then the algorithm loop (started 2026-11-06 18:14 UTC, loop v3)

Ledger format of loop v3: `hypothesis:` is a table (cell | momenta | direction | size | mechanism | ✓/✗), the last
column filled after the verdict; the "after the run" block carries `tally: <✓>/<✗>` from `440`. Phase 3 Step 0
numbers: `space/reports/phase3_lambda_chain.md`.

## R3 2026-11-06: reference R3 = R2 + PR eic/EICrecon#3063 (mass windows removed, IDOLA on every triplet, χ² ranking)
tier: reference row (code: one-file patch `space/notes/patches/R3_pr3063.patch` on the pin, build label R3; R2's parameters)
config: configs/experiments/R3_pr3063.yaml
written: 2026-11-06 18:33 UTC, before the run. Inputs of the prediction: `lambda-offline-R2_pr3114.json` (415, R2's clusters through the
stable-vertex chain with EICrecon's tags: 9 / 22 / 26 / 27 / 25 / 24 / 20 / 11 events of 2000 at 100–275 GeV) and `414`
(the IDOLA-first pairing keeps 0.62–0.86 of the stable vertex's ideal yield, F9).
hypothesis:
| cell | momenta | direction | size | mechanism | ✓/✗ |
|---|---|---|---|---|---|
| S0, S1a, S2, S3, G1–G3, S4c | all | = R2 | Δ 0 | the patch touches only LambdaReconstruction | ✓ |
| S4a_tm per accepted event | 100–275 | up from 0 | 0.3–1.0 × R2's vertex_fixed_tagged count (≈ 3–27 per 2000) | the IP-pointing π⁰ window (F4) is gone; IDOLA runs away for far decays (F9) | ✓ |
| S4a_tm per thrown, mean | 100–275 | up from 0 | 0.05–0.17 % | the above × acceptance | ✓ |
| S4a_any − S4a_tm | 100–275 | up | ≥ 2 × S4a_tm | a candidate is written whenever a triplet exists; 89–97 % of photon pairs are merged | ✗ |
| S5 candidates per 1000, D6a_9x275 | — | up | ≥ 10 × R2's 1.0 | always-a-candidate | ✓ |
| G4 | D5 | identical | 0 non-owned leaves | the Λ collections are owned | ✓ |
after the run (2026-11-07 00:44 UTC; reco 77/77 integrity OK; determinism 4/4 PASS on a D5 chunk and a D4 file, Λ collections included):
S4a_tm (D4, of 2000 per momentum, 100–275 GeV) 9 / 21 / 26 / 27 / 25 / 24 / 19 / 11 against R2's 0 — gained 162, lost 0,
McNemar z 3.0 / 4.6 / 5.1 / 5.2 / 5.0 / 4.9 / 4.4 / 3.3 (`lambda-paired-R3_pr3063-vs-R2_pr3114.json`); per thrown Λ → nπ⁰
0.171 % mean, 0.180 % at 275 GeV. `S4a_tm_best` = S4a_tm (no Λ from a photon fragment on 3×3 clusters). Untruthful candidates
in the 30 MeV window: 4 events in 16000 (R2 0). S0 cells and event flags identical to R2 (410); D5 owned view: only
`ReconstructedLambdas` and `ReconstructedLambdaDecayProductsCM` differ (36 leaves each, `capybara-R3_pr3063-vs-R2_pr3114.json`),
so the cluster and neutral cells S1–S3, S4c, G1–G3 equal R2's by construction (D1–D3 not reconstructed). G4 PASS (62/62 D5
files, 9043 non-ZDC leaves; capybara non-owned 0 differing). MSF D6a_9x275: 22.0 candidates per 1000 events (R2 1.0),
4.4 per 1000 in the window, 0 of the 23 true Λ in acceptance reconstructed (`msf-R3_pr3063-D6a_9x275.json`); D6a_local
2.5 per 1000 (no true Λ in acceptance).
Hypothesis check: identical cluster cells ✓; S4a_tm 0.95–1.00 × R2's vertex_fixed_tagged count ✓ (0.3–1.0 predicted);
0.171 % per thrown ✓ (at the upper edge of 0.05–0.17 %); S4a_any − S4a_tm ≥ 2 × S4a_tm ✗ (4 against 162: inside the fixed
30 MeV window nearly every D4 candidate is the true Λ; the always-a-candidate behaviour shows up on MSF, not on the gun);
S5 ≥ 10 × R2 ✓ (22×); G4 ✓.
tally: 5/1
understanding: on the current 3×3 clustering, IDOLA's runaway (F9) costs almost nothing in EICrecon: B9d's stable vertex adds
2 events in 16000. The events IDOLA loses are those whose photons are merged anyway. On MSF the candidates are background:
none of the 23 accepted true Λ is found, and 22 candidates per 1000 events are written.
retention: full reco ROOT kept (reference row).

## R1p 2026-11-06: reference R1p = R1 + PR eic/EICrecon#3114's box as merged (110 / 22 mm; R1 alone 150 / 12)
tier: reference row (parameter tier on the R1 build, restricted output collections)
config: configs/experiments/R1p_pr3064_3114.yaml
written: 2026-11-06 18:33 UTC, before the run. Inputs: R1's S4a_tm (`truth-R1_pr3064-D4_lambda.json`, 0.40 % per thrown, mean) and its
D2 γ-tag efficiency 0.87–0.98 under 150 / 12.
hypothesis:
| cell | momenta | direction | size | mechanism | ✓/✗ |
|---|---|---|---|---|---|
| S0 (all components) | all | = R1 | Δ 0 | identical clustering | ✓ |
| S4c (γ-tagged neutrals per Λ event) | all | up | ≥ +20 % | width 12 → 22 mm tags wider clusters, neutron fragments included | ✗ |
| S4a_tm per thrown | 225–275 | down | ≥ 20 % relative | length 150 → 110 mm rejects the long column-shaped photon clusters of R1 at high energy | ✗ |
| S4a_any − S4a_tm | all | up | — | more tagged fragments, more wrong triplets in the window | ✗ |
after the run (2026-11-07 00:51 UTC; reco 15/15 integrity OK after the D6a restricted ratio was measured, 444: 0.254 / 0.261; D4 and D6a only,
G4 static — no DIS dataset):
S0 cells and event flags identical to R1 (410). S4c γ-tagged neutrals per Λ event 4.87 → 2.37 (mean; −51 %, every momentum).
S4a_tm (of 2000, 100–275 GeV) 5 / 18 / 36 / 37 / 68 / 59 / 45 / 39 against R1's 3 / 10 / 23 / 35 / 56 / 62 / 49 / 51: McNemar
z +1.4 / +2.8 / +3.2 / +0.6 / +2.1 / −0.5 / −0.8 / −2.6 (`lambda-paired-R1p_pr3064_3114-vs-R1_pr3064.json`); per thrown 0.395 %
mean (R1 0.405 %). Untruthful in the window down, per momentum 0 / 2 / 7 / 9 / 19 / 23 / 21 / 16 against R1's
0 / 4 / 10 / 17 / 23 / 32 / 41 / 56, z −5.4 at 275 GeV and −3.3 at 250. `S4a_tm_best` (photon daughters on their best
clusters) 201 against R1's 178 of S4a_tm 307 / 289. MSF D6a_9x275: 12.8 candidates per 1000 (R1 21.2), 6.2 in the window
(R1 9.8), 0 of 23 true Λ in acceptance (R1 1 of 23); D6a_local 3.0 per 1000 (R1 3.5).
Hypothesis check: S0 = R1 ✓; S4c up ≥ 20 % ✗ (−51 %: the length cut 150 → 110 mm rejects more of R1's long column clusters
than the width 12 → 22 mm admits); S4a_tm down ≥ 20 % at 225–275 ✗ (−5 / −8 / −24 %: only 275 GeV); untruthful up ✗ (down,
z −5.4 at 275 GeV — fewer tagged fragments, fewer wrong triplets).
tally: 1/3
understanding: main's box does not cost PR 3064 its Λ: the yield is flat (0.395 vs 0.405 % per thrown), the fragment-built
share falls (S4a_tm_best / S4a_tm 0.62 → 0.65) and the untruthful candidates halve at high momentum. A merge of 3064 onto
main keeps its Λ with fewer fakes.
retention: reference row; full ROOT kept for now (restricted collections, 17.9 GB).

## B9d 2026-11-06: Λ family — the stable vertex-aware pairing on top of R3 (code tier)
tier: code (Λ family, D-default-25 / selector rule 1: S4a_tm per thrown, McNemar per D4 momentum vs R2; R3 beside)
config: configs/experiments/B9d_stable_vertex.yaml; patch space/notes/patches/B9d_stable_vertex.patch
written: 2026-11-06 18:41 UTC, before the run (R3 still running, its numbers unknown). Inputs: `lambda-offline-R2_pr3114.json`
(stable vertex on R2's clusters with EICrecon's inputs, vertex_fixed_tagged: 9 / 22 / 26 / 27 / 25 / 24 / 20 / 11 of
2000 at 100–275 GeV, 0.17 % per thrown mean), `414` (IDOLA keeps 0.62–0.86 of the stable vertex's ideal yield), F10
(the neutron at getClusters(0) costs 17 % of R2's stable-vertex Λs; not fixed here — B9e).
hypothesis:
| cell | momenta | direction | size | mechanism | ✓/✗ |
|---|---|---|---|---|---|
| S0, S2, S3, G1–G3, S4c | all | = R2 | Δ 0 | only LambdaReconstruction changes | ✓ |
| S4a_tm per accepted event vs R2 | 125–250 | up, significant (z ≥ 3 at ≥ 3 momenta) | 0.6–1.5 × the vertex_fixed_tagged counts above | the stable vertex admits distant decays (F4 gone with R3, F9 fixed) | ✓ |
| S4a_tm vs R3 | 100–275 | up at every momentum | largest relative gain at 100–150 GeV | IDOLA's runaway is worst for distant decays, which dominate at low momentum (acceptance cut) | ✗ |
| S4a_tm per thrown, mean | 100–275 | — | 0.10–0.25 % | the above × acceptance | ✓ |
| S4b Λ mass σ (truth-matched) | where ≥ 10 Λ | ≤ R3's | — | the vertex no longer runs away | ✓ |
| S4a_any − S4a_tm vs R3 | all | not up significantly | — | the candidate count is R3's (one per event with a triplet) | ✓ |
| G4 | D5 | identical | 0 non-owned leaves | Λ collections are owned | ✓ |
deviation (2026-11-06 18:56 UTC): B9d was launched at 18:43 UTC while Step 0 item 7 (R1p) and item 8 (review comments) were unfinished; loop v3 lets only item 7's reference rows precede the MUST items. The run continues; no B9d verdict is written until items 7 and 8 are done. Verdict checklist: determinism of the R3 and B9d builds (one D5 chunk twice, `130` full and `--zdc`); `443` both views vs R2 for R3 and B9d; `402` on D6a_local and D6a_9x275; `417` vs R2 and vs R3; `400 --compare R3_pr3063` (S4b bootstrap); `415`/`441` for both rows; `442`. D1–D3 are not reconstructed: the S2/S3 cells are scored from the owned-collection compare (only `ReconstructedLambda*` may differ).
after the run (2026-11-07 00:55 UTC; Step 0 items 7 and 8 done first, as the deviation note required; reco 77/77 integrity OK; determinism
4/4 PASS; switch test: B9d's Λ collections differ from R3's on the same D4 events):
S4a_tm (of 2000, 100–275 GeV) 9 / 22 / 26 / 27 / 25 / 24 / 20 / 11 — exactly 415's prediction (vertex_fixed_tagged on R2's
clusters). Against R2: +164 / −0, z 3.0–5.2 at every momentum, 0.173 % per thrown mean. Against R3, the chain it modifies:
+2 / −0 (125 and 250 GeV), z ≤ 1.0 everywhere (`lambda-paired-B9d_stable_vertex-vs-R3_pr3063.json`; `400 --compare R3_pr3063`
the same). Untruthful in the window identical to R3's (4 events). S4b mass σ 0.0167 against R3's 0.0170 GeV (mean; bootstrap
z −0.3 to +0.0, n.s.). `S4a_tm_best` = S4a_tm. S0 and event flags identical to R2; D5 owned view: only the two Λ collections
differ; G4 PASS (62/62; capybara non-owned 0 differing). MSF D6a_9x275: 22.4 candidates per 1000 (R3 22.0), 4.0 in the window
(R3 4.4), 0 of 23 true Λ in acceptance. The paired tests ran before the patched 410 rewrote R3's and B9d's tables; the Λ
`matched` flags are identical under the patch (proven 2026-11-07), so they stand.
Hypothesis check: identical cluster cells ✓; vs R2 up, 1.0 × the predicted counts ✓; vs R3 up at every momentum ✗ (+2 / −0,
n.s.: the only row that isolates the stable vertex); 0.173 % per thrown ✓; S4b σ ≤ R3 ✓ (n.s.); untruthful vs R3 not up ✓; G4 ✓.
tally: 6/1
verdict: INCONCLUSIVE — no loss and no guard failure, but no significant gain over R3, the chain it modifies. Against R2 it
passes selector rule 1's letter (z ≥ 3 at all 8 momenta), and the 162 of its 164 events are PR 3063's; for R3-based Λ changes
the selector's baseline is R3, as the guard's is (D-default-37, D-default-39; the alternative is Q17).
understanding: the mechanism is untestable on this clustering, not refuted. The decays IDOLA loses (F9) are those whose photons
are merged by the 3×3 clustering anyway, so the stable vertex has nothing to recover; with ideal inputs IDOLA keeps 0.62–0.86 of
the stable vertex's yield (414), so it matters once a clustering separates the photons. The clustering selector (`tagrefit`,
D-default-38) already scores clusterings through the stable-vertex chain offline, so nothing downstream waits for this patch.
consequences: selector rule 3 does not trigger (it waits for an ACCEPTED Λ change; S4a_tm_best stays reported). The patch is
reverted (the EICrecon tree is clean; install/eicrecon-B9d kept until B9e is built); B9e builds on R3.
retention: reco ROOT to `space/notes/cleanup-pending.sh` (every step reading it is done: 402, 443, 400, 415, 417).

## B9e 2026-11-07: Λ family — the neutron at its reference point (F10), on top of R3 (code tier)
tier: code (Λ family; selector S4a_tm per thrown, McNemar per D4 momentum, against R3, the chain it modifies — D-default-39;
R2 beside for the headline)
config: configs/experiments/B9e_neutron_leader.yaml; patch space/notes/patches/B9e_neutron_leader.patch (pin → R3 + one line:
`const auto rn = n_in.getReferencePoint();` instead of `n_in.getClusters(0).getPosition()`), build label B9e (101 s)
written: 2026-11-07 00:59 UTC, before the run. Inputs: `416 --pairing vertex R3_pr3063` (`lambda-neutron-position-R3_pr3063-vertex.json`):
the IDOLA-first model of R3's chain on EICrecon's own tags reproduces R3's in-EICrecon count (163 offline, 162 in EICrecon;
9 / 21 / 26 / 27 / 25 / 24 / 20 / 11 against 9 / 21 / 26 / 27 / 25 / 24 / 19 / 11); with the neutron at its leader
6 / 22 / 28 / 36 / 35 / 29 / 21 / 18. In all 236 tagged triplets of R2's clusters cluster 0 is not the neutron's leader.
hypothesis:
| cell | momenta | direction | size | mechanism | ✓/✗ |
|---|---|---|---|---|---|
| S0, S2, S3, G1–G3, S4c | all | = R3 | Δ 0 | only LambdaReconstruction changes | ✓ |
| S4a_tm vs R3, summed over the 8 momenta | 100–275 | up | +10 to +30 % (offline +20 %, 163 → 195) | IDOLA's neutron impact point moves from the event's first cluster (often a photon's) to the neutron's leader | ✓ |
| S4a_tm vs R3 per momentum | 175, 200 | up, significant (z ≥ 3) | +9 / +10 events offline | the largest offline gains | ✗ |
| S4a_tm vs R3 | 100 | not up | 9 → 6 offline | a wrong neutron position that happened to land the mass in the window | ✓ |
| S4a_tm per thrown, mean | 100–275 | up | 0.19–0.24 % (offline 0.217 %; R3 0.171 %) | the above × acceptance | ✓ |
| S4a_any − S4a_tm vs R3 | all | not up significantly | — | one candidate per triplet, as R3 | ✓ |
| S5 candidates per 1000, D6a_9x275 | — | = R3 | within ± 15 % of 22.0 | the candidate count does not depend on the neutron position | ✓ |
| G4 | D5 | identical | 0 non-owned leaves | the Λ collections are owned | ✓ |
after the run (2026-11-07 03:00 UTC; reco 77/77 integrity OK; determinism of the B9e build 4/4 PASS, `130` full and `--zdc` on
D5_dis_minq2_100 chunk000 and D4 175 GeV against the 300 outputs):
S4a_tm (of 2000, 100–275 GeV) 6 / 21 / 27 / 35 / 35 / 30 / 22 / 19 = 195 against R3's 9 / 21 / 26 / 27 / 25 / 24 / 19 / 11 = 162; 416's
model predicted 6 / 22 / 28 / 36 / 35 / 29 / 21 / 18 = 195 (±1 per momentum). Against R3: gained / lost 0/3, 4/4, 6/5, 12/4, 11/1, 9/3,
4/1, 9/1; z −1.73 / 0.00 / +0.30 / +2.00 / +2.89 / +1.73 / +1.34 / +2.53; pooled (reported only, not a selector) 55 / 22, z +3.76
(`lambda-paired-B9e_neutron_leader-vs-R3_pr3063.json`). Per thrown mean 0.221 % (R3 0.171 %), 0.310 % at 275 GeV (R3 0.180 %); against R2
+195 / −0, z 2.45–5.92. Untruthful in the window 2 against R3's 4. S4b mass σ (mean) 0.0152 against 0.0170 GeV. S0, event flags,
S4c and the D5 cluster distributions (200) identical to R3. MSF D6a_9x275: 22.0 candidates per 1000 (R3 22.0), 6.2 in the window
(R3 4.4), 0 of 23 true Λ in acceptance; D6a_local 2.5 per 1000, 1.0 in the window. G4 PASS (static, against R3 and R0, 62/62);
capybara against R3: non-owned 0 differing on both D5; owned: only ReconstructedLambdas and ReconstructedLambdaDecayProductsCM.
Hypothesis check: identical cluster cells ✓; summed +20 % ✓ (+20.4 %, the predicted count exactly); z ≥ 3 at 175 and 200 GeV ✗ (2.00,
2.89); 100 GeV not up ✓ (9 → 6, as modelled); 0.19–0.24 % per thrown ✓ (0.221 %); untruthful not up ✓; S5 within ±15 % ✓; G4 ✓.
tally: 7/1
verdict: INCONCLUSIVE — the mechanism is confirmed in count and in per-momentum shape (the model's 195 exactly), with no loss and
no guard failure, but no momentum reaches 3σ at 2000 events (largest z 2.89); the pooled z +3.76 is reported, not used (Q18).
understanding: F10 is real and costs R3 17 % of its Λ: IDOLA's neutron impact point was the event's first cluster, which in the
tagged triplets is never the neutron's leader. The 22 losses are events where the wrong position happened to land the mass in the
window (100 GeV: 3 of 9), as the model predicted per momentum. Per-momentum McNemar at 6–35 Λ per point cannot resolve +20 %;
the Λ family is statistics-limited, not mechanism-limited, until the clustering separates more photons.
consequences: the one line goes into the PR 3063 review comment (`space/reports/review-comments.md`, already drafted as the F10
fix) with these numbers; R3 stays the Λ chain of reference; Q18 asks for the rule. install/eicrecon-B9e kept (Q18 option B reruns it).
retention: reco ROOT of B9e and of its repeat to `space/notes/cleanup-pending.sh` (402, 443, 415, 417, 130 done; Q18 B would
reconstruct D4h fresh).

## B11 2026-11-07: chain high, collect low (code tier, clustering), on L01
tier: code (clustering; selector D-user-31 / D-default-38: `415` vertex_fixed_tagrefit per D4 momentum against L01, McNemar,
3σ; S0 beside; guards G1–G3, S2 after the refit, S3 raw sum one-sided 5 %, full G4 with both capybara views)
config: configs/experiments/B11_chain_high_collect_low.yaml; patch space/notes/patches/B11_chain_high_collect_low.patch (4 files of the
shared ImagingTopoCluster, opened by D-default-41; a new field `minClusterCollectEdep`, default 0 = the stock path), build label B11 (114 s)
written: 2026-11-07 02:49 UTC, before the run. Mechanism: subcells chain only at ≥ 480 keV (E02: the [315, 480) keV halo bridges photons to
each other and to the neutron; cutting it gained S0all +0.012 to +0.020 at all 8 momenta but cost the neutron up to 13 % of its raw
sum at 20 GeV, REJECTED); afterwards the [315, 480) keV subcells, the unseeded subcells and the groups below the survival floors
join the surviving cluster that owns their most energetic neighbouring subcell, pass by pass, so surviving clusters never merge
and the halo E02 threw away comes back. Inputs: `450_b11_prediction.py` (`space/perf/b11-prediction.json`): L01's tagrefit count ×
E02/P1b's truth-identified ratio per momentum (E02 has no tag cache): 56 / 54 / 46 / 45 / 42 / 40 / 31 / 18 → 73 / 69 / 68 / 62 / 57 /
62 / 53 / 31 (sum 332 → 475, +43 %); z 3.2–4.7 per momentum if lost ≤ 10 % of gained. Proofs before launch: the B11 build with the
knob off reproduces L01 (`130` full, D4 175 GeV and a D5 chunk); knob on differs (switch test).
hypothesis:
| cell | momenta | direction | size | mechanism | ✓/✗ |
|---|---|---|---|---|---|
| S4o vertex_fixed_tagrefit vs L01 (selector) | 100–275 | up, significant (z ≥ 3) at ≥ 4 momenta | sum +20 to +60 % (predicted +43 %) | E02's separation with the photon clusters still tagged by the 110 / 22 box | |
| S4o vertex_fixed_tagrefit per thrown, mean | 100–275 | up | 0.35–0.55 % (predicted 0.446 %; L01 0.294 %) | the above × acceptance | |
| S0all vs L01 | 100–275 | up, significant at ≥ 6 momenta | +0.008 to +0.020 | the bridges are cut as in E02; collected halo seldom lands on the wrong particle | |
| S0n vs L01 | 100–275 | within ± 0.02, not down significantly at 275 GeV | — | sub-floor neutron fragments are collected back (E02 lost −0.024 at 275 GeV) | |
| S3 D3 neutron raw sum vs P1b | 20, 50, 100 | down at most 5 % (one-sided limit) | 0 to −3 % (E02: −13.4 / −8.3 / −6.1 %) | the collected halo and fragments return the energy | |
| S2 D2 photon raw sum | all | within −1 % | — | photon halo is collected into the photon | |
| D5 clusters per event vs L01 | Q² > 100, Q² > 0 | up | +3 to +15 % (E02 +11 / +18 %) | fragments above the floors stay separate clusters | |
| G1 (φ@180, columns), G3 | D5 | in band; G3 < 0.5 | — | the 3×3 reach is unchanged | |
| S4a_tm in EICrecon vs L01 | 100–275 | not down significantly | — | the pin's Λ chain (L01's) on better-separated clusters | |
| G4 | D5 | identical; capybara non-owned 0 | — | only the ZDC protoclusters change | |
proofs (2026-11-07 03:01 UTC, before launch): B11 build with the knob off (`B11_knob_off.yaml`, L01's parameters) against L01:
`130` full and `--zdc` PASS on D4 175 GeV (2000 events) and D5_dis_minq2_100 chunk000 — the stock path is unchanged. Switch test:
knob on against knob off, D4 175 GeV `--zdc` FAILS (cluster associations differ from event 2) — the knob acts. Wall time 635 s
knob on against 637 s knob off for the same file (the collection pass costs nothing measurable).
launched: 2026-11-07 03:02 UTC (log start) via `300 --phase phase3 --reference L01_box3114 --jobs 20` (preflight PASS: 278 GB free, need 185).
stopped: 2026-11-07 03:04 UTC at the user's request ("Stop phase. … The loop needs to be restarted"): 300 and 120 killed, the 20 B11
containers stopped (`docker stop`), 20 partial outputs, nothing scored. The EICrecon tree is restored to the pin (the four
ImagingTopoCluster files byte-identical to the pre-B11 copies); the patch, the config and the pre-registration stay for the restart.
verdict: none (aborted before any output).

## Phase 4 (loop v4, the Λ bar fight)

### X1_offline_chain (2026-11-08)
- hypothesis: the offline chain built in — R1 clustering with neighbourLayersRange 1 (P1d), P1d's D2/D3 refit calibration (photon 3.901·E^0.876, neutron 8.064·E^0.700; PR 3064's laws overestimate photons 4.4× and neutrons 1.7× at 275 GeV), every γγ pair with every neutron through the vertex fit ranked by fitted π⁰/Λ masses (R3), the stable vertex (B9d), the neutron at its leader (B9e). Predicted S4a_tm per thrown 1.5 % mean / 3.0 % at 275 GeV (from R1's 0.404 / 0.832; R1's offline tagrefit 1.64 / 3.07 is the ceiling of the tagged chain under truth pair choice).
- commit c2632b19 on zdc-autoresearch/phase4; patch space/notes/patches/X1_offline_chain.patch; build X1; config configs/experiments/X1_offline_chain.yaml; reference R1_pr3064.
- result (2026-11-08T06:16Z, headline.csv): S4a_tm per thrown 1.970 % mean, 4.309 % at 275 GeV (R1 0.404 / 0.832; ceiling 14.1 %). 417 vs R1: pooled gained 1325, lost 154, z +30.45; z ≥ 6.1 at every momentum. 460 PASS (F1 a–d, F2 a–b, F3 a–f: 13 130 candidates, 131 within 0.1 MeV of m_Λ). Determinism: D4 175 GeV repeat identical.
- prediction check: 1.5 / 3.0 predicted → exceeded (the stock pre-cuts lost 16–22 % of D4 events with clean, tagged photons: 470).
- caveat: the untruthful count rises (Λ in the window, not truth-matched: 1108 vs 56 at 275 GeV); no guard in Phase 4, reported.
- verdict: **ACCEPTED** (461). Accept commit 655a8a15. Mechanism: the calibration refit puts photon and neutron energies on scale, and the vertex-aware ranking keeps the events the origin-pointing π⁰ / Λ windows threw away.
- what limits next (470 on X1): clustering 66–82 % of D4 events, pairing 9–20 %, matched 2–14 %. 471: X1's ranking reproduced exactly; a neutron holding the photon candidates the pair leaves out plus the Λ decay-depth density picks +59 % (2309 vs 1451 S4a-equivalent picks, oracle 3777) → X2.

### X2_lambda_pairing (2026-11-08)
- hypothesis: X1 picks the true γγ pair in about half of the events where one exists; the photon candidates a pair leaves out are mostly neutron fragments whose energy the neutron lacks. Choosing the pair in the ZDC neutrals by the Λ hypothesis (neutron = every other cluster, leader position; rank = fitted π⁰ and Λ mass χ² + Λ decay-depth density) and writing only that pair as photons predicts S4a_tm per thrown 2.84 % mean / 5.45 % at 275 GeV (471 x1_zNL rule on X1's events, scaled per momentum; X1 1.970 / 4.309).
- commit 8d4ae1c4 on zdc-autoresearch/phase4 (on X1); patch space/notes/patches/X2_lambda_pairing.patch; build X2; config configs/experiments/X2_lambda_pairing.yaml; reference X1_offline_chain. Switch test X2_knob_off (knob false must reproduce X1 on D4 175 GeV).
- result (2026-11-08T06:50Z, headline.csv): S4a_tm per thrown 2.913 % mean, 5.500 % at 275 GeV (X1 1.970 / 4.309; ceiling 14.1 %). 417 vs X1: pooled gained 1433, lost 416, z +23.65; z 5.1–11.0 per momentum. 460 PASS (14 840 candidates, 46 within 0.1 MeV of m_Λ). Switch test: knob off = X1 (960 ZDC leaves identical, D4 175 GeV); knob on differs (ZDC neutral PDG counts from event 0).
- prediction check: 2.84 / 5.45 predicted → met within 3 % (the 471 emulation reproduces EICrecon).
- untruthful (Λ in the window, not matched) falls at high momentum: 918 vs 1108 at 275 GeV.
- verdict: **ACCEPTED** (461). Accept commit 45f47529.
- what limits next (470 on X2): clustering 66–82 %, wrong pair (now seen as photon_tag) 5–13 %, window 1.5–2.8 %, matched 10–19 %.

### X3_pairing_weights (2026-11-08)
- hypothesis: X2's Λ-mass term is 111 MeV wide (0.1 m_Λ), several times the mass resolution, so the decay-depth term and the π⁰ term under-weigh it; σ_Λ = 40 MeV and depth weight 1.5 (centre of 471's grid plateau on X1's events: 2583 vs 2309 picks, +9 to +17 % at every momentum) predict 3.24 % mean / 5.98 % at 275 GeV per thrown (X2 2.913 / 5.500).
- commit 50018ef8 on zdc-autoresearch/phase4 (on X2); patch space/notes/patches/X3_pairing_weights.patch; build X3; reference X2_lambda_pairing. The weights were chosen on D4 (16 grid points); D4h at the first checkpoint tests the overfit.
- result (2026-11-08T07:24Z, headline.csv): S4a_tm per thrown 3.236 % mean, 5.957 % at 275 GeV (X2 2.913 / 5.500; ceiling 14.1 %). 417 vs X2: pooled gained 384, lost 88, z +13.62; z 3.5–5.4 per momentum. 460 PASS (14 837 candidates, 64 within 0.1 MeV of m_Λ).
- prediction check: 3.24 / 5.98 predicted → met (3.236 / 5.957).
- caveat: untruthful in the window rises (1105 vs 918 at 275 GeV): the narrower mass term also pulls wrong pairs into the window.
- verdict: **ACCEPTED** (461). Accept commit 1a47340a. D4h at checkpoint 1 tests the D4-chosen weights.

### X4_photon_depth (2026-11-08, parameter try)
- hypothesis: the photon box accepts clusters up to 400 mm past the ZDC face; true-photon clusters sit at 126 mm median depth (p90 172 mm) and the other tagged clusters at 280 mm (p10 163 mm) (X1's events, 150 and 275 GeV). A 225 mm limit removes most fragment candidates from the pairing, and the excluded clusters join the neutron. 471 (neutron sum corrected to hold every non-pair cluster): 3439 picks vs 2583 at 400 mm, plateau 200–225 mm. Predicted S4a_tm per thrown 4.31 % mean / 7.96 % at 275 GeV (X3 3.236 / 5.957).
- parameter reco:ReconstructedFarForwardNeutrals:gammaZMaxOffset = 225 on X3's build (commit 50018ef8; no new commit — baked into code with the next code try if accepted); config configs/experiments/X4_photon_depth.yaml; slim template; reference X3_pairing_weights. Chosen on D4; checkpoint D4h tests it.
- result (2026-11-08T07:47Z): S4a_tm per thrown 3.278 % mean, 6.055 % at 275 GeV (X3 3.236 / 5.957). 417 vs X3: pooled gained 32, lost 0, z +5.66. 460 PASS.
- prediction check: 4.31 / 7.96 predicted → **failed** (3.278 / 6.055). Mechanism mis-specified: gammaZMaxOffset is added to HcalFarForwardZDC_SiPMonTile_r_pos, which is the ZDC *centre* (front face 3580.0 cm + length 183.27 cm / 2 = 3671.64 cm, read from the geometry), so 225 mm cut at 1141 mm past the face (stock 400 mm: 1316 mm, i.e. no depth cut at all). The emulation cut at 225 mm past the face. The same constant is LambdaReconstruction's and X2's zMax (vertex range up to the ZDC centre).
- verdict: **ACCEPTED** (461: z +5.66, mean up), a parameter try on X3's build (no commit; baked into code with the next code try).

### X5_photon_depth_face (2026-11-08, parameter try)
- hypothesis: X4 as intended — photon candidates must start within 225 mm of the ZDC front face: gammaZMaxOffset = 225 − 916.37 = −691.4 mm (r_pos is the ZDC centre). Predicted 4.31 % mean / 7.96 % at 275 GeV per thrown (471, depth 225 mm, neutron holding every non-pair cluster; X4 3.278 / 6.055).
- parameter on X3's build (commit 50018ef8); config configs/experiments/X5_photon_depth_face.yaml; slim template; reference X4_photon_depth.
- result (2026-11-08T07:53Z): S4a_tm per thrown 4.373 % mean, 8.030 % at 275 GeV (X4 3.278 / 6.055). 417 vs X4: pooled gained 972, lost 28, z +29.85; z 6.8–12.1 per momentum. 460 PASS (11 340 candidates, 40 within 0.1 MeV of m_Λ).
- prediction check: 4.31 / 7.96 predicted → met (4.373 / 8.030).
- untruthful in the window falls by more than half (469 vs 1079 at 275 GeV): fewer fragment candidates, purer Λ sample.
- verdict: **ACCEPTED** (461). Baked into code: commit 57b698c4 (gammaZMaxOffset −691.4 in reco.cc and the config); build X5b without parameters reproduces X5 on D4 175 GeV (305 ZDC leaves identical).

### X6_zdc_face (2026-11-08, parameter try)
- hypothesis: LambdaReconstruction's and the pairing's zMax is HcalFarForwardZDC_SiPMonTile_r_pos, the ZDC centre (front + 916 mm): the vertex bisection and the decay-depth density extend inside the detector. Ending them at the front face (…_r_pos_front_face; photon depth limit kept at 225 mm past the face) is the geometry the 471 emulation assumed; small gain predicted: 4.40 % mean / 8.1 % at 275 GeV (X5 4.373 / 8.030).
- parameters on X5b (commit 57b698c4); config configs/experiments/X6_zdc_face.yaml; slim; reference X5_photon_depth_face.
- result (2026-11-08T08:08Z): 4.386 % mean / 8.00 % at 275 GeV (417's mean; X5 4.389). 417 vs X5: pooled gained 5, lost 6, z -0.30. 460 PASS.
- prediction check: a small gain predicted → none: the vertex range end barely moves the fits (the bisection rarely reaches beyond the face).
- verdict: **REJECTED** (461). Parameter try: nothing to revert in git; the config stays as the record.

### X7_core_split (2026-11-08)
- hypothesis: only 28 % of D4 events have three clean clusters with X5; photons sit inside the neutron's cluster (21 % at 275 GeV) or have no cluster (9 % at 150 GeV). A split of each imaging group between its shallow energy cores (seeds ≥ 5 MeV in the first 4 layers, 50 mm apart) and one shared deep region frees the photon cores without fragmenting showers (the plain watershed did fragment them and lost); a 20 MeV cluster floor recovers low-energy photons. Scans on two D4 files (X5's calibration): 712 / 716 matched at 150 / 275 GeV vs 480 / 492 (core-split rounds K, L; floors T20, M3; combined M1). Refit on D2/D3 for this clustering. Predicted 6.4 % mean / 11.8 % at 275 GeV per thrown (X5 4.373 / 8.030).
- commit 448731f0 on zdc-autoresearch/phase4 (on 57b698c4); patch space/notes/patches/X7_core_split.patch; build X7; config configs/experiments/X7_core_split.yaml; reference X5_photon_depth_face.
- result (2026-11-08T08:31Z): S4a_tm per thrown 6.853 % mean, 12.942 % at 275 GeV (X5 4.373 / 8.030). 417 vs X5: pooled gained 2827, lost 308, z +44.99; z 13.9–19.1 per momentum. 460 PASS (15 525 candidates, 72 within 0.1 MeV of m_Λ).
- prediction check: 6.4 / 11.8 predicted → exceeded (6.853 / 12.942); the refit and the 4-layer seeds add to the scans' +47 %.
- caveat: untruthful in the window rises (867 vs 469 at 275 GeV).
- verdict: **ACCEPTED** (461). Accept commit on zdc-autoresearch/phase4 after 448731f0.
- units finding (08:45Z): JANA length parameters are in DD4hep base units (cm). The scans' coreSplitMinDistXY 50 / 80 / 30 meant 500 / 800 / 300 mm (one core per neighbourhood of half a metre: K1 = K4, K3 = L4); X7's code uses 50 * dd4hep::mm = 50 mm. X7 therefore differs from the scanned spacing and still beat the prediction; spacings 30 and 100 mm are rescanned. The energy parameters (GeV base) were right.

### X8_core_depth_centroid (2026-11-08)
- hypothesis: X7's photon clusters are still impure in 27 % of events; the photon core regions are narrow columns (a core radius of 25–60 mm moves no hit: scans Rc), so the contamination is the neutron's energy deeper in the same column. Keeping only a core's first 5 layers (the deeper hits join the shared deep region) and placing the ZDC neutron at its cluster centroid (471 on X7's clusters: +3.9 % / +3.3 %) predict 7.4 % mean / 14.0 % at 275 GeV per thrown (scans G: 847 / 867 matched at 150 / 275 GeV vs 790 / 793; plateau 4–6 layers; X7's calibration). Refit on D2/D3: photon 3.952·E^0.938.
- commit 26bd6925 on zdc-autoresearch/phase4 (on X7); patch space/notes/patches/X8_core_depth_centroid.patch; build X8; reference X7_core_split.
- result (2026-11-08T09:17Z): S4a_tm per thrown 7.271 % mean, 13.970 % at 275 GeV (X7 6.853 / 12.942). 417 vs X7: pooled gained 842, lost 535, z +8.27; z grows with momentum (0.9 at 125 GeV, 4.7 at 275 GeV). 460 PASS (15 413 candidates, 82 within 0.1 MeV of m_Λ).
- prediction check: 7.4 / 14.0 predicted → met (7.271 / 13.970).
- verdict: **ACCEPTED** (461). Accept commit after 26bd6925.

### X9_pairing_photon_depth (2026-11-08)
- hypothesis: inside the 225 mm limit true photons still shower shallower than the neutron fragments that pass the photon box; a soft depth term (1.0 per 100 mm, summed over the pair) in the pairing score picks the true pair more often. 471 on X8's clusters (pairing off): 844 / 866 vs 822 / 855 picks at 150 / 275 GeV; weights 0.5–2 a plateau. Predicted 7.42 % mean / 14.2 % at 275 GeV per thrown (X8 7.271 / 13.970).
- commit f822e4d0 on zdc-autoresearch/phase4 (on X8); build X9; reference X8_core_depth_centroid.
- diagnostic beside it (X8, 150 and 275 GeV): per photon, 69 % own a pure best cluster, 22 % are swallowed by a neutron-dominated cluster (median purity 0.32), 7 % by the other photon, 2 % have no cluster → the next lever is finding photon cores that X8's single-hit maxima miss.
- result (2026-11-08T09:34Z): S4a_tm per thrown 7.436 % mean, 14.101 % at 275 GeV (X8 7.271 / 13.970). 417 vs X8: pooled gained 355, lost 160, z +8.59. 460 PASS. Untruthful in the window falls at every momentum.
- prediction check: 7.42 / 14.2 predicted → met (7.436 / 14.101).
- verdict: **ACCEPTED** (461). Accept commit after f822e4d0.

### Findings between X9 and checkpoint 2 (2026-11-08T09:41Z, scans, never tries)
- Projected core seeding (scanH, J10–J40): photons inside the neutron's cluster fall (8.5 → 4.5 % at 275 GeV) but photon impurity rises (24.8 → 29 %): the summed shallow column carries neutron energy into the core; matched flat (833 / 866 vs X9 849 / 864). Dropped.
- Shower length / dispersion as soft pairing terms on top of X9 (471): no gain (844 / 866 → 839–846 / 855–859). The pairing reaches 83 % of the oracle with depth, masses and the decay-depth density.
- The ZDC crystal section (EcalFarForwardZDC, z 35719–35733 mm, in front of the Hcal) takes only 1.4–3 % of a single photon's energy (R1's D2): adding it improves the photon resolution from 24.0 to 23.4 % (20 GeV: 35 → 31 %). Not pursued. The Hcal photon resolution itself (18–35 %) is the limit behind the window and pairing losses.

### Diagnostics after checkpoint 2 (2026-11-08T09:50Z; decide X10)
- Photon resolution and X8's truncation (D2 best-cluster raw energy, robust σ / median): X7's clustering 0.349 (20 GeV) … 0.237 (275 GeV); X8's 0.332 … 0.211 — the 5-layer truncation improved the photon resolution.
- Resolution budget (X9, 2631 truth-matched Λ, 150/200/275 GeV, the stable-vertex fit recomputed): mass robust σ 14.3 MeV with reco energies; 14.1 MeV with the true neutron energy; 8.5 MeV with the true photon energies; 5.6 MeV with all true. The photon energies dominate; hadronic compensation of the neutron would not help.
- Photon energy estimators fitted on X8's D2 (7902 photons): energy only (power law) 0.242 overall; with the cluster hit count 0.231 overall but no better per energy (0.326 / 0.194 / 0.154 at 20 / 100 / 275 GeV vs 0.325 / 0.194 / 0.144). The resolution is set by the 2.7 % sampling fraction.
- Clustering headroom (X9, 150/200/275 GeV): photons swallowed by the neutron's cluster sit a median 21.5 mm from the neutron at the ZDC face (56 % within 25 mm, the subcell pitch; 81 % within 50 mm); clean photons a median 76.7 mm. The clustering is at the granularity limit.
- Backlog after these: only small items (the ZDC crystal energy for photons, ~2 % of a photon's energy; a pairing weight retune, ~1 %). The loop's stop condition "backlog empty" is effectively met for large levers.

Phase 4 closed 2026-11-08T14:09Z (D-user-37): final row X9_pairing_photon_depth; the close-out record is space/reports/phase4_bar_fight.md.

## Phase 5 — Λ → nπ⁰ on MSF events (loop v5, D-user-39)

Score: N_found(9x275) + N_found(9x130) on the search halves D6s (`210`); selector `463` (paired z ≥ 3, purity guard
z_P ≥ −2); fair play `460` on the MSF outputs, plus `460 --tree` and `465` for a code try. Base row MSF5_X9 (X9):
N_found 943 + 66 = 1009, purity 21.5 % / 9.4 %. Tries are patches or parameters on top of EICrecon a15b0db6; no commits.

### Y1_b0_split (2026-11-08, parameter try)
- hypothesis: with both photons in B0 (4.0 % of expected at 9x275, 3.5 % at 9x130) the island clustering merges the pair
  for 93 % of the Λ; splitting B0 islands at local maxima, hits shared by exp(−d / 1 crystal) × peak energy, gives
  LambdaReconstruction both photons. Predicted (config, before launch): "N_found on the search halves: 9x275 920 → ~960,
  9x130 ~65 → ~95 (+30 from γγ-in-B0 at each beam, minus a few from split mixed-regime photons); purity flat or down by
  < 1 point" — the base turned out 943 / 66, so the predicted gains are +40 / +30.
- parameters on the X9 install: B0ECAL:B0ECalIslandProtoClusters:splitCluster 1, transverseEnergyProfileMetric
  dimScaledLocalDistXY, transverseEnergyProfileScale 1.0. Reference MSF5_X9.
- result (2026-11-08T23:39Z): N_found 9x275 943 → 944, 9x130 66 → 71; pooled b 9 c 15, z +1.22; purity 19.8 → 19.0 %, z_P -1.01. 460 PASS (Y1_b0_split-msf).
- mechanism seen: with both photons in B0 the split resolves the pair (photon missing 248 → 197 at 9x275, 215 → 148 at 9x130), but those Λ then fail on mass (true triplet out of the window 4 → 28 and 14 → 47, another triplet chosen 6 → 31 and 10 → 40): the vertex and the B0 photon energy decide them. B0 photon E_reco / E_true median 1.15 → 1.08.
- prediction check: +40 / +30 predicted → +1 / +5: missed (the pair is found, the mass is not).
- verdict: **INCONCLUSIVE** (463). Backlog: retry on top of Y2 (vertex lever arm).

### Y2_vertex_lever_arm (2026-11-08, code try)
- hypothesis (config, before launch): "in γ B0 + γ ZDC (11.0 % of expected at 9x275) the true triplet's mass sits +23.6 MeV
  high (47 % above +30 MeV) and another triplet is chosen for 26 %; a correct vertex pulls the mass toward m_Λ. Predicted
  N_found on the search halves: 9x275 920 → ~990 (about +40 of the 173 out-of-window and +30 of the 200 wrong-triplet Λ in
  the regime), 9x130 ~65 → ~80; all-ZDC unchanged within ±10; purity up slightly."
- change: LambdaReconstruction's Λ slope for a vertex at depth z is Σ w_i x_i⊥ / (P + z Σ w_i), w_i = p_i / (z_i − z),
  recomputed at each bisection step (the stock Σ p_i x_i / Σ p_i z_i weights a B0 photon's angle down by ~7/35); the depth
  range ends short of the nearest impact point. Patch space/notes/patches/Y2_vertex_lever_arm.patch on a15b0db6 (33 added
  lines, 465 PASS); build Y2 (212 s). Reference MSF5_X9.
- result (2026-11-08T23:56Z): N_found 9x275 943 → 953, 9x130 66 → 83; pooled b 7 c 34, z +4.22; purity 19.8 → 20.4 %, z_P +0.71. 460 PASS (-msf and -tree), 465 PASS.
- mechanism seen: the gain is the γγ-in-B0 regime (9x275 0 → 5, 9x130 1 → 15): the depth range now ends short of B0, where the stock bisection ran on to the ZDC. γ B0 + γ ZDC moves little (193 → 198, 30 → 33) and its true-triplet mass stays high (median +20.6 → +24.5 MeV at 9x275): the B0 photon energy, not the vertex. All-ZDC unchanged (750, 35).
- prediction check: 9x275 +40 / 9x130 +15 predicted → +10 / +17: right sign and total, wrong regime (γγ in B0, not B0 + ZDC).
- verdict: **ACCEPTED** (463). Patch stays applied; current best Y2_vertex_lever_arm.

### Y4_b0_split_on_y2 (2026-11-08, parameter try on Y2)
- hypothesis (config, before launch): "Y1 resolved both B0 photons for ~50 more Λ at 9x275 and ~65 at 9x130 in the γγ-in-B0
  regime, but their mass failed; Y2 fixed the depth range for that regime (0 → 5 and 1 → 15 found). Together: γγ-in-B0 found
  9x275 5 → ~20, 9x130 15 → ~35. Predicted N_found 9x275 953 → ~968, 9x130 83 → ~103; purity flat (Y1 cost 0.8 point alone)."
- change: Y1's three B0 island parameters on the Y2 install. Reference Y2_vertex_lever_arm.
- result (2026-11-09T00:12Z): N_found 9x275 953 → 975, 9x130 83 → 123; pooled b 8 c 70, z +7.02; purity 20.4 → 20.0 %, z_P -0.50. 460 PASS.
- prediction check: +15 / +20 predicted → +22 / +40: met, larger at 9x130.
- verdict: **ACCEPTED** (463). Current best Y4_b0_split_on_y2 (Y2 install + the three B0 island parameters).

### Y5_mixed_pairing (2026-11-09, code try on Y4)
- hypothesis (config, before launch): "γ B0 + γ ZDC is 11 % of expected at 9x275; 474 on Y4's outputs emulates 195 → 383
  found there (9x130 32 → 55), all-ZDC unchanged (749 → 750). Predicted N_found 9x275 975 → ~1150, 9x130 123 → ~145 (the
  final Λ choice may lose some of the emulated gain); purity up (the true triplet replaces a fragment pair in the window)."
- change: the ZDC pairing (chooseLambdaPhotonPair) also fits every tagged ZDC cluster with each B0 photon candidate (the
  B0 neutrals' leading clusters ≥ 1 GeV, at most 4), with Y2's lever-arm vertex; a winning mixed hypothesis writes only its
  ZDC cluster as a ZDC photon. Single-photon depth term × 3 (emulation plateau 2–4). Switch lambdaPairingMixed (default
  false, true in reco.cc), proven on file 0001 (off reproduces Y4 exactly; on changes 45 events' ZDC neutrals). Patch
  space/notes/patches/Y5_mixed_pairing.patch on a15b0db6 + Y2; build Y5 (187 s, no new warnings); Y4's B0 parameters.
  Reference Y4_b0_split_on_y2.
- diagnostics that led here (473 / 474, scratchpad diag): in the mixed regime the chain picks another triplet for 186 and
  misses the ZDC photon for 144 of 803 Λ (9x275 search half); ranking-only knobs of the ZDC pairing move ≤ 10.
- result (2026-11-09T00:45Z): N_found 9x275 975 → 1164, 9x130 123 → 147; pooled b 22 c 235, z +13.29; purity 20.0 → 23.8 %, z_P +4.84. 460 PASS (-msf, -tree), 465 PASS.
- prediction check: ~1150 / ~145 predicted (474 emulation +188 / +23) → 1164 / 147: met.
- verdict: **ACCEPTED** (463). Patch stays applied; current best Y5_mixed_pairing (install Y5 + Y4's B0 parameters).

### Y6_b0_profile (2026-11-09, parameter try on Y5)
- hypothesis (config, before launch): "γγ-in-B0 found 9x275 33 → ~50, 9x130 57 → ~80; γ B0 + γ ZDC ±5 (its B0 photon is
  mostly alone); N_found 1164 → ~1180, 147 → ~170; purity flat."
- why: with both photons in B0, Y5 still misses a photon for 198 of 264 Λ (9x275) and 151 of 264 (9x130); the photon's best
  B0 cluster is shared below purity 0.8 (50 % / 55 %) or merged with the other photon (48 % / 41 %); the 1 GeV threshold
  costs 2–4 % (scratchpad diag b0_missing.py on Y5). Change: B0 island transverseEnergyProfileScale 1.0 → 0.5 (crystal
  units). Reference Y5_mixed_pairing.
- not run: Y3_lambda_mass_rank — after Y5 another triplet is chosen for only 8 + 17 Λ (9x275 mixed, γγ-in-B0) and 0 + 22
  (9x130): its premise (26 % in the mixed regime) is gone. Parked.
- result (2026-11-09T01:04Z): N_found 9x275 1164 → 1209, 9x130 147 → 182; pooled b 9 c 89, z +8.08; purity 23.8 → 24.7 %, z_P +1.17. 460 PASS.
- prediction check: +16 / +23 predicted → +45 / +35: right direction, larger than predicted.
- verdict: **ACCEPTED** (463). Current best Y6_b0_profile (install Y5, B0 profile scale 0.5).

### Y7_b0_photon_law (2026-11-09, parameter try on Y6, D-user-40)
- hypothesis (config, before launch): "on MSF the stock law reads B0 photons a median 1.06–1.08 of true; the gun law reads them
  ~12 % lower. Both photons in B0 (true-triplet mass +8.9 / +11.1 MeV on Y5): masses move into the window, found up (9x275
  ~+10, 9x130 ~+15). γ B0 + γ ZDC (mass +3.6 / −0.5 MeV, the B0 photon's overestimate cancelling the ZDC photon's 0.78): masses
  move low, found down (9x275 ~−20, 9x130 ~−3). Predicted N_found 1209 → ~1200, 182 → ~195: net small, sign uncertain; purity
  flat."
- the law: 467 on CAL5_D2b_Y4 (D2b reconstructed with Y4's B0 clustering): a = 1.0781 ± 0.0037, b = 1.0098 ± 0.0015,
  χ² 37.5 / 3; residual peaks refit 0.995 / 1.000 / 1.004 / 1.003 / 0.967 at 2 / 5 / 10 / 20 / 40 GeV, stock 0.995 / 1.121 /
  1.228 / 1.344 / 1.428; 62–86 % of the gun photons leave a B0 cluster ≥ 1 GeV. Reference Y6_b0_profile.
- refit on Y6's B0 clustering before launch (CAL5_D2b_Y6): a = 1.0888 ± 0.0031, b = 1.0058 ± 0.0011, residual peaks 0.999 / 1.002 / 1.001 / 0.998 / 1.001 at 2–40 GeV (χ² 45.8 / 3); this law is the one launched.
- result (2026-11-09T01:41Z): N_found 9x275 1209 → 1238, 9x130 182 → 190; pooled b 31 c 68, z +3.72; purity 24.7 → 25.1 %, z_P +0.38. 460 PASS.
- mechanism seen: both B0 regimes gain (9x275 γ B0 + γ ZDC 388 → 401, γγ in B0 72 → 87; 9x130 54 → 58, 93 → 97); the mixed mass stays centred (+3.3 → +0.6 MeV at 9x275). MSF B0 photons read a median 0.91 / 0.95 of true (were 1.05 / 1.07).
- prediction check: "net small, sign uncertain", mixed predicted down → +29 / +8, mixed up: the predicted loss did not happen.
- verdict: **ACCEPTED** (463). Current best Y7_b0_photon_law (install Y5, Y6's B0 parameters, the gun-fitted B0 photon law).

### Y8_b0_profile_03 (2026-11-09, parameter try on Y7)
- hypothesis (config, before launch): "γγ-in-B0 is still the regime with the most B0 losses (9x275 87 of 264 found, 9x130 97 of
  264); a sharper share keeps more of each photon in its own cluster. Predicted N_found 1238 → ~1250, 190 → ~200; but at s = 0.3
  a hit one crystal from a peak keeps only e^−3.3 of its weight there, so the energy of a photon's shower tail may go to the
  wrong maximum: the gain may stop or turn. Purity flat."
- change: B0 island transverseEnergyProfileScale 0.5 → 0.3 (crystal units); Y7's B0 law (fitted at 0.5; a single gun photon
  rarely splits). Reference Y7_b0_photon_law.
- result (2026-11-09T01:57Z): N_found 9x275 1238 → 1252, 9x130 190 → 194; pooled b 5 c 23, z +3.40; purity 25.1 → 25.3 %, z_P +0.28. 460 PASS.
- prediction check: ~+12 / ~+10 predicted → +14 / +4: met at 9x275; the sharing scale gives diminishing returns.
- verdict: **ACCEPTED** (463). Current best Y8_b0_profile_03.

### Y9_external_pair (2026-11-09, code try on Y8)
- hypothesis (config, before launch): "with both photons in B0, Y8 picks another triplet for 46 (9x275) and 53 (9x130) of 264 Λ
  — Y5's pairing still writes ZDC fragments as photons there. Emulated net: 9x275 γγ in B0 +21, γ B0 + γ ZDC −4, all-ZDC −1;
  9x130 +28, −3. Predicted N_found 1252 → ~1268, 194 → ~219; purity flat or up."
- change: the ZDC pairing's third class, both photons outside the ZDC (every pair of B0 photon candidates, the whole ZDC as
  the neutron, Y2's lever-arm vertex); if it wins, no ZDC photon is written. Constant photon-depth term −30 (475 on Y8: net
  +41 at −28, +38 at −32; the emulator reproduces Y8: all-ZDC 750 / 750, mixed 406 / 401). Switch lambdaPairingExternalPair
  (default false, true in reco.cc), proven on file 0001 (off = Y8 identical, on changes 22 events). Patch
  space/notes/patches/Y9_external_pair.patch (126 added lines, 465 PASS); build Y9 (183 s). Reference Y8_b0_profile_03.
- result (2026-11-09T02:22Z): N_found 9x275 1252 → 1267, 9x130 194 → 219; pooled b 10 c 50, z +5.16; purity 25.3 → 26.7 %, z_P +1.76. 460 PASS (-msf, -tree), 465 PASS.
- prediction check: ~1268 / ~219 predicted (475 emulation) → 1267 / 219: met.
- verdict: **ACCEPTED** (463). Patch stays applied; current best Y9_external_pair (install Y9, Y8's parameters).

### Y10_lambda_mass_rank (2026-11-09, parameter try on Y9; the parked Y3)
- hypothesis (config, before launch): "after Y5 and Y9 another triplet wins for only 4 + 11 Λ (9x275 mixed, γγ in B0) and 1 + 6
  (9x130): little left to win; a tighter Λ term also pulls fake combinations into the window. Predicted N_found 1267 → ~1272,
  219 → ~222; N_window up, purity down < 1 point."
- context (diagnostics on Y9, scratchpad): the joint scan of the mixed photon-depth factor (2–5) and the B0-pair offset (−26 to
  −34) in 475 has its best at the launched (3, −30): no retune. With both photons in B0, the pairs that lose a photon land a
  median 2.5 crystals apart (39 % under 2), found pairs 4.5–5.1: the B0 granularity, not a parameter. Mixed regime, ZDC photon
  missing: 148 have a pure tagged ZDC cluster that another hypothesis beat, 111 have no pure cluster.
- change: reco:ReconstructedLambdas:lambdaMassWindow 0.1 → 0.036. Reference Y9_external_pair.
- result (2026-11-09T02:42Z): N_found 1267 → 1267, 219 → 219; b 0, c 0, z +0.00; N_window 4794 → 4796, 764 → 765 (the parameter acts, on 2–3 events); purity 26.7 → 26.7 %. 460 PASS.
- prediction check: ~+5 / ~+3 predicted → 0 / 0: the final chooser has no choice left to make once the ZDC pairing (Y5, Y9) has chosen.
- verdict: **REJECTED** (463, no effect). Parameter dropped.

Phase 5 closed 2026-11-09T03:22Z (D-user-41): final row Y9_external_pair; see the ledger's Phase 5 outcome.
D4 of every Phase 5 try (D4P5_Y1, Y2, Y4, Y5, Y7, Y8, Y10; with CP5_1_Y6_D4 and CP5_2_Y9_D4 at the checkpoints), reconstructed at the close for the deck's Phase 4 columns, headline.csv rows written: S4a_tm 7.436–7.439 % mean, 14.101–14.117 % at 275 GeV (X9 7.436 / 14.101). Reported only.

## Phase 6 (loop v6, started 2026-11-09T04:27Z; base row MSF6_Y9 = Y9 with the Phase 6 template)

### Z1_crystal_photons (2026-11-09, code try on MSF6_Y9)
- hypothesis (config, before launch): "637 of 1422 missing all-ZDC photons at 9x275 have a pure crystal cluster; the 477
  emulation on MSF6_Y9 (veto split, depth −10) predicts net +118 (9x275: all-ZDC +114, γ B0 + γ ZDC +7, γγ B0 −3) and +15
  (9x130), N_window +122 / +18. Predicted N_found 1267 → ~1385, 219 → ~234; purity 26.7 → ~28.4 % pooled."
- change: the crystal section clustered at the crystal scale (ZDC.cc: 35 mm neighbourhood, peaks ≥ 0.1 GeV, sharing 2 cm);
  the neutrals factory's 5th input EcalFarForwardZDCClusters; crystal photon candidates (≥ 0.5 GeV, no tagged Hcal cluster
  within 60 mm behind, veto split), energy 1.962·E_crys + 47.47·E_column − 0.881 (gun fit), hypotheses crystal + Hcal,
  crystal + crystal, crystal + B0 beside Y9's. Switch lambdaPairingCrystal, proven on file 0001 (off = MSF6_Y9 identical,
  on changes 37 of 500 events, each with a crystal-linked photon). Patch space/notes/patches/Z1_crystal_photons.patch
  (431 added lines, 465 PASS); build Z1 (209 s).
- result (2026-11-09T05:30Z): N_found 9x275 1267 → 1271 (b 107, c 111), 9x130 219 → 227 (b 3, c 11); pooled z +0.79;
  purity 26.7 → 26.6 %, z_P −0.17. 468 PASS (2012 + 203 crystal-linked neutrals). 460 -msf: F2, F3 PASS, F1d FAIL against the
  base commit's cone; 478 on the working tree (D-default-49, Q21) F1a + F1d PASS. −t σ68 0.124 / 0.129 GeV² (Y9 0.124 / 0.133).
- prediction check: ~+133 predicted → +12. Cause found: the C++ column summed the Hcal clusters' hits (HEXPLIT subcells),
  a median 0.45 of the rec-hit column the law was fitted on, so crystal photons carried a median 0.56 of their energy:
  99 newly built true triplets fell out of the window (Δm median +75 MeV) and 96 found Λ lost a photon to a crystal pick.
- verdict: **INCONCLUSIVE** (463). Superseded by Z1b (the column from the Hcal rec hits).

### Z1b_crystal_column (2026-11-09, code try on MSF6_Y9)
- hypothesis (config, before launch): "the C++ now matches the 477 emulation (rec-hit column): net +118 (9x275) and +15 (9x130),
  N_window +122 / +18. Predicted N_found 1267 → ~1385, 219 → ~234; purity 26.7 → ~28.4 % pooled."
- change: Z1 with the Hcal column behind a crystal photon summed over HcalFarForwardZDCRecHits (the neutrals factory's 6th
  input), the hits the photon law was fitted on; the column leaves the neutron on the rec-hit scale (crystalColumnNeutronScale
  1). Smoke check on file 0001: pure crystal-linked photons carry a median 0.89 of the true energy (Z1 0.56). Patch
  space/notes/patches/Z1b_crystal_column.patch (457 added lines, 465 PASS); build Z1b (197 s).
- result (2026-11-09T05:59Z): N_found 9x275 1267 → 1314 (b 104, c 151), 9x130 219 → 232 (b 5, c 18); pooled b 109 c 169, z +3.60; purity
  26.7 → 27.5 %, z_P +0.91. Fair play: 478 F1a + F1d on the working tree PASS (460 -msf F1d lists exactly the 5 crystal-chain
  factories against the base commit's cone; D-default-49, Q21); 460 F2, F3 PASS; 468 PASS (2161 + 211 crystal-linked neutrals);
  ZDC, B0 and crystal raw hits identical to MSF6_Y9 on both halves. −t σ68 0.126 / 0.126 GeV² (Y9 0.124 / 0.133).
- prediction check: ~+133 predicted → +60 (45 % of the emulation).
- verdict: **ACCEPTED** (463; fair play under D-default-49). Current best Z1b_crystal_column (install Z1b, Y9's parameters).

### Z2_crystal_params (2026-11-09, parameter try on Z1b)
- hypothesis (config, before launch): "477 on MSF6_Y9 (veto split, depth −10) with these settings: net +151 (9x275) and +13
  (9x130), against +118 / +15 with Z1b's (emulated +31 over Z1b, N_window +113); Z1b reached 45 % of its emulated gain, so
  ~+14 over Z1b: N_found 1314 → ~1328, 232 → ~232; purity flat."
- change: crystal candidates from 0.3 GeV (0.5); Hcal column 60 mm (45) with the law refitted at that radius
  (1.9092·E_crys + 44.768·E_col − 0.8984); the column leaves the neutron × 36.63 (1/sampFrac, the Hcal clusters' scale).
  Install Z1b, run-time parameters only.
- result (2026-11-09T06:27Z): N_found 9x275 1314 → 1388 (b 42, c 116), 9x130 232 → 230 (b 6, c 4); pooled b 48 c 120, z +5.55; purity
  27.5 → 28.0 %, z_P +0.55. Fair play: 478 F1a + F1d PASS (460 -msf F1d lists the 5 crystal-chain factories, D-default-49);
  460 F2, F3 PASS; 468 PASS (2012 + 215); raw hits = MSF6_Y9 on both halves. −t σ68 0.122 / 0.126 GeV².
- prediction check: ~+14 predicted → +72 (the emulation said +31 over Z1b): the real chain gains more than emulated from
  removing the column from the neutron on the clusters' scale.
- verdict: **ACCEPTED** (463; fair play under D-default-49). Current best Z2_crystal_params (install Z1b + 4 parameters).

### Z4_lambda_sigma (2026-11-09, parameter try on Z2)
- hypothesis (config, before launch): "477 --full on Z2's settings: 9x275 +170 vs +149 (launched width), window +470 vs +211;
  9x130 +19 vs +13, window +90 vs +41: emulated +27 found, +308 in the window over Z2. N_found 1388 → ~1409, 230 → ~236; purity
  28.0 → ~27 % (guard z_P ≥ −2 expected to hold)."
- change: the ZDC pairing's Λ-mass width lambdaPairingLambdaSigma 0.04 → 0.03 GeV (install Z1b, Z2's parameters).
- result (2026-11-09T06:59Z): N_found 9x275 1388 → 1409 (b 24, c 45), 9x130 230 → 237 (b 0, c 7); pooled b 24 c 52, z +3.21; purity 28.0 →
  27.1 %, z_P −1.11. Fair play: 478 PASS; 460 F2, F3 PASS (F1d lists the crystal chain, D-default-49); 468 PASS (1971 + 215);
  raw hits = MSF6_Y9. −t σ68 0.122 / 0.123 GeV².
- prediction check: ~1409 / ~236 predicted → 1409 / 237: met.
- verdict: **ACCEPTED** (463; purity guard held). Current best Z4_lambda_sigma.

### Z5_crystal_energy_alt (2026-11-09, code try on Z4)
- hypothesis (config, before launch): "477 --alt on Z4's settings (σ_Λ 0.03): 9x275 +317 vs +170 (Z4's emulation), window +547
  vs +470; 9x130 +32 vs +19, window +82 vs +90: emulated +160 found over Z4 at a nearly flat window. N_found 1409 → ~1556,
  237 → ~250; purity up."
- change: a tagged Hcal photon with a crystal cluster in front competes with the crystal law's energy (the leading crystal
  cluster in front + its column); every hypothesis with it is scored with either energy; the winner links the crystal
  cluster after its Hcal cluster. Switch crystalEnergyAlternative, proven on file 0001 (off = Z4 identical, on changes 68 of
  500 events). Patch space/notes/patches/Z5_crystal_energy_alt.patch (158 added lines on Z1b, 465 PASS); build Z5.
- result (2026-11-09T07:22Z): N_found 9x275 1409 → 1574 (b 28, c 193), 9x130 237 → 252 (b 2, c 17); pooled b 30 c 210, z +11.62; purity
  27.1 → 29.5 %, z_P +3.05. Fair play: 478 PASS; 460 F2, F3 PASS (F1d the crystal chain, D-default-49); 468 PASS (4492 +
  532); raw hits = MSF6_Y9. −t σ68 0.147 / 0.128 GeV² (Z4 0.122 / 0.123); on the 1381 + 235 Λ both rows find: 0.142 vs
  0.122 (9x275), 0.126 vs 0.120 (9x130); E_Λ reco / true median 1.110 vs 1.073 at 9x275.
- prediction check: ~1556 / ~250 predicted → 1574 / 252: met.
- verdict: **ACCEPTED** (463). Current best Z5_crystal_energy_alt. The −t resolution at 9x275 is 16 % worse: Q22.

### Z6_alt_column_out (2026-11-09, code try on Z5; Q22)
- hypothesis (config, before launch): "477 --alt on Z5's settings, with and without the column out (9x275): net +303 vs +317,
  window +558 vs +547, Λ energy / true of good picks 1.058 vs 1.122 (σ68 0.113 vs 0.129); 9x130 +32 vs +32, 1.076 vs 1.126.
  Predicted N_found 1574 → ~1560, 252 → ~252 (no gain for 463); −t σ68 at 9x275 0.147 → below Z4's 0.122."
- change: when a tagged Hcal photon carries the crystal law's energy, its Hcal column beyond its own cluster (column × 36.63
  − the cluster's energy) leaves the neutron. Switch crystalAltColumnOut (default false, true in the yaml), proven on file
  0001 (off = Z5 identical, on changes 68 of 500 events). Patch space/notes/patches/Z6_alt_column_out.patch (37 added lines,
  465 PASS); build Z6.
- result (2026-11-09T08:03Z): N_found 9x275 1574 → 1547 (b 63, c 36), 9x130 252 → 250 (b 5, c 3); pooled b 68 c 39, z −2.80; purity 29.5 →
  29.1 %, z_P −0.58. Fair play PASS (478, 460 F2–F3, 468 3610 + 345, raw hits = MSF6_Y9). **−t σ68 0.121 / 0.120 GeV²**
  (Z5 0.147 / 0.128, Y9 0.124 / 0.133), median bias −0.009 (Z5 −0.037), within ±0.1 GeV² 59.5 % (Z5 50.7 %).
- prediction check: ~1560 / ~252 → 1547 / 250; −t below 0.122 → 0.121: met.
- verdict: **REJECTED** (463, N_found −29). Patch reverted from the working tree (= Z5); install eicrecon-Z6 kept. The best −t of
  any row at 1797 found (+21 % over Y9): the alternative for Q22.
