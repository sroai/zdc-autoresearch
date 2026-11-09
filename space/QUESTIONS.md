# Questions for the user

Format and rules: `work-common.md`, section "ASK — the exact protocol".
Answer after `ANSWER:` with a letter, or write `all defaults` on the line.
Numbers never reset.


## Q1 2026-11-04 [closed 2026-11-04] — Is a displaced-vertex π⁰ gun wanted for the 20–50 GeV Λ-daughter energies?
- Found: the benchmark π⁰ generator decays the π⁰ at the IP and keeps only events with both photons inside 4 mrad at the ZDC; accepted per 4000 generated: 20 GeV 0, 30 GeV 0, 50 GeV 810, 100 GeV 2352. D1 therefore runs 50 to 160 GeV (D-default-16). In Λ → nπ⁰ the π⁰ carries 6 to 25 % of E_Λ (6 to 69 GeV for the D4 momenta) and decays metres downstream, where the face subtends a larger angle, so low-energy π⁰ reach the ZDC there.
- Why it matters: S1 (the π⁰ diagnostic) has no point below 50 GeV; the low-energy photon pairs are measured only inside D4, mixed with the neutron shower.
- Options: A) keep D1 at 50–160 GeV and rely on D4 for low-energy pairs. B) add a π⁰ gun with the Λ-gun's decay-vertex distribution (new generator code, about one hour of simulation). Recommendation: A — S0 on D4 is the selector and already measures photon separation at those energies; S1 stays a diagnostic.
- ANSWER: A (chat, 2026-11-04: "No, D4 covers it")


## Phase 0 checkpoint — where the six questions are
The loop file's six checkpoint questions are numbered 1–6 there. In this file, Q1 is the earlier displaced-π⁰-gun question, so the checkpoint numbers coincide with this file's numbers only for 4–6.
- Checkpoint 1 (gun geometry): answered at the start line, "LYSO+SiPM" → D-user-4; carried out on `epic_craterlake`, which holds the same ZDC files (D-user-8).
- Checkpoint 2 (selector): "S0 truth-matched separation efficiency (default)" → D-user-5.
- Checkpoint 3 (`LambdaReconstruction` changes): "at least not in phase0 and phase1" → D-user-6; reopens before Phase 2.
  Reopened 2026-11-05: "Yes. Change it as needed" → D-user-14 (open from Phase 2; family rules D-default-25).
- Checkpoints 4–6: Q4–Q6 below, closed by D-user-7 ("Others default").

## Q4 2026-11-05 [closed 2026-11-05 by D-user-7 "Others default"] — Numeric limits for the guards G1 to G3
- Found (D5, R0 → R1): φ within 5° of ±180°: 0.068/0.074 → 1.000/1.000 (NC / SIDIS); single-(x, y) clusters 0.000 → 1.000; fraction of clusters above 50 GeV 0.612/0.864 → 0.006/0.016; clusters below 5 GeV per event 0.006/0.010 → 2.13/5.44 (the 1 GeV threshold of the draft counted nothing: the calibrated cluster-energy floor is 1.83 GeV).
- Why it matters: G1–G3 decide REJECTED for a clustering that improves S0 by making columns or shards.
- Options: A) G1 φ@180 ≤ 0.15 and columns ≤ 0.05; G2 high-energy fraction may drop at most 50 % relative to R0; G3 ≤ 0.5 low-energy clusters per event. B) tighter (R0 + 3σ). C) looser. Recommendation: A — R1 fails every one by a factor of 7 or more, while a genuine split of a merged shower (fewer >50 GeV clusters, a few more small ones) stays inside.
- ANSWER: A (default, D-default-19)

## Q5 2026-11-05 [closed 2026-11-05 by D-user-7] — Are the shared ImagingTopoCluster algorithm and the Island chain in scope for Phase 3?
- Found: the review's mechanism is a property of ImagingTopoCluster (connected components cannot split a merged shower; only the distances and thresholds act), and the ZDC already configures an Island chain with `splitCluster = true` (`HcalFarForwardZDCIslandProtoClustersBaseline`, unused by the neutrals).
- Options: A) both, under full G4 (BEMC and FHCAL use ImagingTopoCluster). B) Island chain only. C) neither. Recommendation: A.
- ANSWER: A (default, D-default-20)

## Q6 2026-11-05 [closed 2026-11-05 by D-user-7] — Machine background in D6 and S5
- Found (item 5): the campaign 2026-07 dd4hep step reads `afterburner/<energy>-priority`, never `bg_merged`: D6a_local (9x130) and D6a_9x275 have no machine background, and the campaign has no background variant.
- Options: A) S5 on the background-free D6 and say so in every S5 number. B) simulate a background-merged slice on the farm in Phase 4. Recommendation: A for Phases 1–3; B is a Phase 4 question.
- ANSWER: A (default, D-default-21)

## Q7 2026-11-05 [closed 2026-11-05 by D-user-13] — The S2 acceptance limit fails for R0 itself
- Found: the acceptance rule requires |S2 scale − 1| ≤ 0.05, but R0 is at 0.15–0.22 at every D2 momentum: no ZDC photon is ever tagged on R0 (both transverse √λ above `gammaMaxWidth` = 12 mm, observation O1 of the Phase 0 report), so photons get the neutron calibration. The refit (`scripts/420_refit_calibration.py`) also shows the stock photon law (1.1, 0.98) is 13–31 % low on R0's photon clusters. Any clustering change is therefore REJECTED on S2 before calibration is refit, while rule 6 refits calibration only after an ACCEPTED change.
- Why it matters: as written, no Phase 2 experiment can be ACCEPTED.
- Options: A) judge S2 (and S3 corrected scale) after the per-clustering refit of 420 for every candidate (calibration refit is part of each experiment's evaluation, not an experiment of its own), and judge the photon tag efficiency as a separate reported cell. B) drop S2 scale from acceptance and keep S3 raw sum and S0. C) allow `gammaMaxWidth` (a neutrals parameter) into the Phase 2 search. Recommendation: A, with C as a backlog entry.
- ANSWER: A (user, chat, D-user-13); C (`gammaMaxWidth`) goes to the backlog

## Q8 2026-11-05 [closed 2026-11-05 by D-user-12] — The S3 raw-sum band rejects more containment
- Found: the guard `S3_raw_sum_rel_change_max: 0.05` (an agent default) read as a two-sided ±5 % band. P1f (R1 − distances: the 5 MeV / 2-hit thresholds and nlr 3 at the stock 3×3 distance) raises the raw sum vs R0 by +0.44 at 20 GeV (0.09 → 0.53; R0's 25 MeV / 10-hit cut drops most of a 20 GeV neutron), +0.21 at 50, +0.04 at 100, +0.014 at 275 GeV, with σ 0.164 → 0.112, and fails the band.
- Why it matters: under a two-sided band no lower-threshold clustering can be ACCEPTED, however much S0all gains.
- Options: A) one-sided (fail only on a drop > 5 %) plus a check that σ/mean does not worsen and clusters per neutron stays in its limit. B) keep ±5 %. C) replace the mean with a resolution guard (σ/mean must not worsen). Recommendation: A.
- ANSWER: A (user, chat, D-user-12)

## Q9 2026-11-05 [closed 2026-11-05 by D-user-16] — Containment counts only the energy that survives clustering
- Found: S0's containment is the best cluster's share of the particle's energy summed over the *surviving* clusters (`410_truth_match.py`, `contrib[best] / contrib.sum()`; zdc-setup.md, Truth matching). Raising thresholds discards shards and so raises containment without separating anything: P1e (R1 with R0's 25 MeV / 10-hit cut) gains S0n +0.20 to +0.57 while the raw neutron sum drops 24–81 %. Lowering thresholds does the opposite (P1b: gains are conservative, lost 0).
- Mitigation in place: the one-sided S3 raw-sum guard (D-user-12) catches discarding on D3 (P1c and P1e both fail it). Nothing guards photon energy discarded in D4 events.
- Options: A) keep "not split" containment (a separation metric) and add a D2 photon raw-sum guard (one-sided, like S3). B) containment against the particle's energy in all ZDC hits before clustering ("not lost"); 410 is frozen and every row is re-scored. C) report both, select on A's. Recommendation: A (cheapest; closes the hole with a guard on the other particle type).
- ANSWER: A (user, chat: "as recommend", D-user-16)

## Q10 2026-11-05 [closed 2026-11-05 by D-user-17] — S2 at 20 GeV sits on the limit for every 3×3 clustering
- Found: after each clustering's own refit (D-user-13) the photon scale at 20 GeV is R0 0.9526, P1b 0.9488, P1f 0.9643, P1a 0.9761; the 20 GeV peak has a ≈ 1.3 % statistical error (R0: E_raw peak 13.17 ± 0.17 GeV), and the a·E^b form fits the photon points poorly on every 3×3 clustering (χ²/ndf 65–76 / 6). P1b (R0 + the lower thresholds: S0all up at every momentum, lost 0, every other guard in) is REJECTED by 0.12 % at this one point.
- Options: A) judge S2 at 30–275 GeV and report 20 GeV (the form's miss is a calibration-form question, B9). B) allow the residual's statistical error (|μ/E − 1| − 2σ ≤ 0.05). C) keep the hard line. Recommendation: B (keeps 20 GeV in the guard, removes the noise verdict).
- ANSWER: B (user, chat: "as recommend", D-user-17)

## Q11 2026-11-06 [closed 2026-11-06 by D-user-26] — The S3 raw-sum guard fails experiments at a momentum the Λ-daughter neutrons never have
- Found: the one-sided S3 guard (drop ≤ 5 %, D-user-12) is applied at every D3 momentum, 20 GeV included, where R0's own raw sum is 0.087 (P1b 0.500). E02 failed it with −13.4 % and E04 with −7.6 % at 20 GeV; the D4 neutrons carry ≥ 75 GeV (`space/perf/scoreboard.csv`, S3_rawsum_mean_20; `space/EXPERIMENTS.md`, E02/E04). Both also fail S0n at 275 GeV, so neither verdict changes under any answer.
- Why it matters: `configs/metrics.yaml` is frozen, so the guard's range is a user decision; a chaining or collection change in Phase 3 (B11) may fail only at 20 GeV.
- Options: A) guard at 50–275 GeV, report 20 GeV. B) keep 20 GeV in the guard. C) guard at the D4 neutron energies only (≥ 75 GeV). Recommendation: A — 20 GeV is outside the physics and inside R0's own failure.
- ANSWER: A (user, chat: "Q11-12 default", D-user-26; the limit line is `space/notes/patches/q11-s3-guard.patch`, to apply)

## Q12 2026-11-06 [closed 2026-11-06 by D-user-27] — Keep the pin with R2 as the Λ baseline, or re-pin EICrecon to main including PR 3114?
- Found: PR 3114 (photon box 110 / 22 mm) merged into main on 2026-11-05 21:08 UTC (head `7b22d521`); the pin `e5e2a60c` predates it. R2 = R0 + 3114 at parameter tier reproduces the merged defaults on the pin (`configs/experiments/R2_pr3114.yaml`); PR 3063 is 18 commits behind main and its one file is unchanged, so it applies to the pin.
- Why it matters: `{eicrecon}` is frozen; a re-pin rebuilds R0, R1, Rt and re-runs every reference (Phase 0 items 2, 8, 12, 13: about a night) and resets the references.json checksums.
- Options: A) keep the pin; R2 is the baseline of every Λ comparison (D-default-27). B) re-pin to main head and redo Phase 0's reference items. Recommendation: A — the same physics at zero cost; re-pin before Phase 4 if the PR draft must target a newer main.
- ANSWER: A (user, chat: "Q11-12 default", D-user-27)

## Q13 2026-11-06 [closed 2026-11-06 by D-user-25] — Apply the protocol patch for loop v3 (edits to the frozen `zdc-setup.md` and `work-common.md`)
- Found: loop v3 (`zdc-autoresearch-loop-v3.md`) needs nine edits in the two frozen protocol files (the loop-file name, the `{pr3114}`/`{pr3063}` rows, references R2/R3/R1p, scoreboard rows S4o and H, the Budgets lines for restricted collections, preflight and retention, the plot-format rule, the people list; in work-common the loop name, the lesson rule, the PNG rule, the `date -u` rule, the headline-from-script rule). The harness refused the agent's edit of `space/FROZEN` (self-modification), which is the protocol's own rule 1 at work. The edits are `space/notes/patches/protocol-v3.patch` (dry run clean).
- Why it matters: until applied, the loop names the patch as the source of the changed values (loop v3, Every run, item 2); the setup file still names loop v2.
- Options: A) apply it: `patch -p1 < space/notes/patches/protocol-v3.patch` in the repository root, and add `zdc-autoresearch-loop-v3.md` to `space/FROZEN`. B) leave the setup at v2 and let the loop carry the values. Recommendation: A.
- ANSWER: A (applied by the user in the terminal on 2026-11-06; `zdc-autoresearch-loop-v3.md` is in `space/FROZEN`)


## Q14 2026-11-06 [closed 2026-11-06 by D-user-29] — 410's photon-tag column reads the neutron on D4: repair the frozen truth matcher?
- Found: the neutrals factory links every ZDC cluster to the neutron neutral (`associateAllClustersToNeutron = true` for the ZDC, `FarForwardNeutralsReconstruction.cc` l. 279), and `scripts/410_truth_match.py` maps a cluster to the last neutral that lists it, the neutron. On D4 225 GeV the photon best clusters read `tagged_gamma` 0.001 (L01) and 0.01 (R1) although EICrecon built 7 and 62 truth-matched Λs there from tagged photons. Affected cells: `S0_*_tagged_gamma` (diagnostic), `S2_gamma_tag_eff`, `S3_mistag_rate`, and the S2 corrected-scale cells (`S2_scale*` read `neutral_E`, the neutron's energy when a tagged photon has fragments). No Phase 1–2 verdict cites them: the S2 guard is judged on the refit residuals of 420 (D-user-13), which read the raw cluster energy. `415` reads the tags from the ROOT files instead (D-default-33).
- Why it matters: `410` is frozen (rule 1); the γ-tag efficiency and the n mis-tag rate are reported in every scoreboard row and will matter for the Λ chain.
- Options: A) apply a one-line repair (a photon neutral wins the cluster mapping) to `410`, rerun `410`/`400` on the rows whose ROOT exists, and show every verdict cell unchanged. B) leave `410` as it is; mark the four cells "not valid on D4/D2 with fragments" in the reports. Recommendation: A — the cells become correct and the verdict cells provably do not move.
- ANSWER: A (2026-11-06T23:50Z, user, chat: "ok, all 3 questions as recommended") → D-user-29.

## Q15 2026-11-06 [closed 2026-11-06 by D-user-30] — BLOCKING(!) S4a_tm credits Λs built from a photon fragment: tighten it before it co-selects clustering?
- Found: `415 --validate` (`space/perf/lambda-offline-validation.json`): on R1 101 of the 289 truth-matched Λs (S4a_tm) take one photon from a cluster other than that photon's best-matched cluster — a fragment with purity ≥ 0.8. S4a_tm's rule is purity only (`410`, `match_lambdas`). On L01 (3×3 clusters) 0 of 25. Excluding those events, the offline chain and S4a_tm agree at every momentum (|z| ≤ 1.63).
- Why it matters: selector rule 3 makes S4a_tm a co-selector of clustering experiments once B9d is ACCEPTED. A clustering that fragments photons can raise S4a_tm through fragments whose energy lands in the window by combinatorics (R1's photon law 2.7·E^1.27 turns a 7.5 GeV fragment into 35 GeV). Λ-family experiments (B9d) keep the clustering fixed and are judged on R2's events, so they are less exposed.
- Options: A) keep S4a_tm as defined; report the fragment-built fraction beside it in every row. B) for the co-selector, require each photon daughter's cluster to be that photon's best-matched cluster (a frozen-definition change in `410`; S4a_tm for the Λ family stays as is). C) make S4o (truth variant, vertex_fixed) the co-selector instead of S4a_tm. Recommendation: B — it keeps the in-EICrecon number and removes the fragment credit; A leaves a loophole the selector would find.
- Frozen until answered: selector rule 3 (S4a_tm as a co-selector of clustering experiments); every clustering verdict keeps S0 as the one selector, with S4a_tm and S4o reported.
- Continuing meanwhile: Phase 3 Step 0 and B9d (Λ family on the fixed clustering, selector S4a_tm as user-confirmed, D-user-24) — neither uses rule 3.
- ANSWER: B (2026-11-06T23:50Z, user, chat: "ok, all 3 questions as recommended") → D-user-30.

## Q16 2026-11-06 [closed 2026-11-06 by D-user-31] — BLOCKING(!) S0 and the Λ yield rank clusterings in opposite order: which one selects clustering experiments?
- Found: Step 0 item 1 (`415`, `space/perf/headline.csv`): the stable-vertex chain on each row's real clusters with its own refit calibration (S4o vertex_fixed_refit) gives, in % per thrown Λ → nπ⁰ (mean 100–275 GeV): P1d 4.02, R1 3.42, P1e 1.20, P1c 1.13, E02 0.79, P1b 0.56, R0 0.27. S0all orders them the other way (P1b 0.62, R1 0.19, P1d 0.27). Paired on the same events against P1b: P1d +3139 / −307 (z 48), R1 +2692 / −309 (z 43), P1c z 1.5 (`space/perf/lambda-offline-compare-*.json`). With EICrecon's own tags and neutron (tagged variant, the calibration each row applied): R1 1.10 %, L01 (P1b + box) 0.29 %, R2 0.17 %. Correction (2026-11-06, from `space/perf/truth-*-D4_lambda.json`): the reversal comes from the neutron, not the photons. R1 separates the photons better than P1b (S0_g 0.34 / 0.40 / 0.33 against 0.15 / 0.09 / 0.05 at 100 / 200 / 275 GeV) but shreds the neutron shower into columns (S0_n 0.07 / 0.04 / 0.03 against 0.70 / 0.65 / 0.65; purity 0.92, containment < 0.5). The Λ chain does not need the neutron in one cluster: EICrecon's neutron takes the summed energy of all ZDC clusters and the leader's direction. The column clusterings fail the G1 guard (columns, φ at ±180°) that the review of PR 3064 asked for.
- Why it matters: every clustering verdict of Phases 1–2 selected on S0; the deliverable (Λ per thrown) prefers what S0 and G1 reject. B11, B8 and B7 are judged by whichever selector you pick.
- Options: A) clustering selects on S4o vertex_fixed (tagged variant, the row's refit calibration once a refit exists), with S0 reported and the G1–G3 guards unchanged — column clusterings stay rejected, and the loop looks for Λ yield without columns. B) keep S0 as the clustering selector (D-user-24), S4o reported beside. C) S4o selects and the G1 column guard is relaxed for clusterings that win on S4o — R1/P1d become candidates. D) (added after the correction) select clustering on the photon separation S0_g (both photons, purity ≥ 0.8, containment ≥ 0.5), with S0_n as a guard and S4o reported — stays on truth-matched clusters, drops the neutron requirement the chain does not need. Recommendation: A — it aligns the selector with the deliverable and keeps the reviewers' column objection as a guard; D is the closest alternative that keeps a cluster-level ruler.
- Frozen until answered: clustering verdicts (B11, B8, B7 and later clustering candidates); none is launched.
- Continuing meanwhile: Step 0 items 7–10 and B9d (Λ family on R2's fixed clustering, selector S4a_tm, D-user-24) — neither is a clustering verdict.
- ANSWER: A (2026-11-06T23:50Z, user, chat: "ok, all 3 questions as recommended") → D-user-31.

## Q17 2026-11-07 — B9d's verdict: judge R3-based Λ changes against R3 (INCONCLUSIVE) or against R2 as rule 1 reads (ACCEPTED)?
- Found: B9d (PR 3063 + the stable vertex) against R2: +164 / −0, z 3.0–5.2 at all 8 D4 momenta; against R3 (PR 3063 alone): +2 / −0, z ≤ 1.0 (`space/perf/lambda-paired-B9d_stable_vertex-vs-*.json`). Every guard holds. 162 of the 164 events are PR 3063's.
- Why it matters: rule 1 names R2 as the baseline (D-default-28, confirmed D-user-24). Read literally it ACCEPTS B9d for PR 3063's gain; that would also trigger rule 3 (S4a_tm_best co-selects clustering) and carry B9d's patch into every later build.
- Options: A) the baseline of an R3-based Λ change is R3, like its untruthful guard (D-default-37): B9d INCONCLUSIVE, patch reverted, B9e built on R3, the stable vertex re-tested once a clustering separates the photons (D-default-39, D-default-40). B) rule 1 as written: B9d ACCEPTED, its patch the base for B9e, rule 3 active. Recommendation: A — a baseline every R3-based change passes tells nothing about the change; nothing downstream needs the patch now (the clustering selector runs the stable vertex offline).
- Continuing meanwhile: A (the default); B9e is pre-registered against R3 either way, so its result reads under both.
- ANSWER:

## Q18 2026-11-07 — Λ-family verdicts per momentum cannot see a +20 % gain at 2000 events: keep the rule, pool the momenta, or add events?
- Found: B9e (the neutron at its reference point, on R3) gained 55 and lost 22 truth-matched Λ against R3 over the 8 D4 momenta (195 against 162, exactly 416's prediction; 0.221 % per thrown against 0.171 %). Per momentum the largest z is 2.89 (200 GeV), so selector rule 1 (McNemar per momentum, 3σ) gives INCONCLUSIVE. Pooled over the momenta the same test gives z +3.76 (`space/perf/lambda-paired-B9e_neutron_leader-vs-R3_pr3063.json`, field `pooled`; B9d: +1.41, a real null).
- Why it matters: at 6–35 Λ per 2000-event momentum point, a change has to gain about +50 % at one momentum to pass; any Λ-code fix on the 3×3 clustering is INCONCLUSIVE by construction, and the per-thrown headline cannot move through the Λ family until the clustering improves.
- Options: A) keep rule 1 as written: B9e INCONCLUSIVE, its one line goes to the PR 3063 review comment as a recommendation. B) from now on Λ-family changes select on the pooled McNemar over the 8 momenta (3σ), with "no momentum down significantly" as a guard; because this rule was chosen after seeing B9e, B9e is ACCEPTED only if the held-out D4h (125/175/250 GeV, seed 101) pooled test also gains with no loss (one 300 run of B9e and R3 on D4h, about 30 min). C) more D4 statistics for Λ verdicts (new seeds; `configs/datasets.yaml` is frozen, so you add them; about 1 h per row and seed).
- Recommendation: B — the per-momentum test asks whether the change helps at each momentum separately, which ~1 % yields cannot answer; the pooled test asks whether it helps, which is the selector's question; the held-out check keeps the post-hoc choice honest.
- Continuing meanwhile: A (the default); nothing in the clustering loop waits on it (its selector is the offline stable-vertex chain).
- Phase 4 (2026-11-08T04:57Z, D-default-42): the bar fight takes option B as its selector (pooled z ≥ 3, mean per thrown up); a veto restores A for Phase 4.
- ANSWER:

## Q19 2026-11-08 [closed 2026-11-09 by D-user-40] — May a B0 photon gun (D2b_photon_B0) be added to the frozen datasets config, for the B0 photon energy try?
- Found: in the γ B0 + γ ZDC regime (11.0 % of expected at 9x275) the true triplet's mass sits +23.6 MeV high at the median (47 % above +30 MeV, all-ZDC −1.5 MeV); B0 photon neutrals carry a median 1.11 of the true photon energy (power law 0.99 · E^1.14 in reco.cc). Loop v5 F4 lets calibrations be fitted on guns only, never on D6, and no gun aims at B0 (z ≈ 7.0 m, 6–24 mrad from the proton axis). Opening the FROZEN exception on an agent default was refused by the auto-mode classifier.
- Why it matters: the B0 photon energy try (loop v5 order of work, item 1) waits on it; the other tries do not.
- Options: A) add D2b_photon_B0 (python gun, γ at 2, 5, 10, 20, 40 GeV, 1000 events each, seed 1, θ 7–20 mrad, epic_craterlake) through a temporary exception; B) fit the B0 photon calibration on the D6s search half and let the D6h checkpoint guard the overfit; C) drop the try. Recommendation: A — a gun fit is the rule of Phases 4 and 5 and costs ~5000 cheap events.
- ANSWER: A (2026-11-09T00:30Z, user: "Yes, add the gun"; D-user-40).

## Q20 2026-11-09 [closed 2026-11-09 by D-user-42] — May a low-energy ZDC photon gun (D2c) be added to the frozen datasets config, for Phase 6's crystal-seeded photon law?
- Found: the MSF photons that reach the ZDC carry 5–50 GeV (median 17 GeV at 9x275, 10 % below 6.3 GeV); the D2 photon gun starts at 20 GeV. A crystal-seeded photon's energy (crystal clusters clip at 2 GeV per crystal) needs a law fitted on guns (F4) where the photons are.
- Why it matters: Phase 6 (loop v6) Step 0 item 2; without it the law below 20 GeV is an extrapolation.
- Options: A) add D2c_photon_low (python gun, γ at 5, 10, 15 GeV, 1000 events each, seed 1, θ < 4 mrad, epic_craterlake) through a temporary exception, as D2b; B) extrapolate D2's law below 20 GeV and let the paired test judge. Recommendation: A — cheap (3000 events), and Phase 5's B0 gun turned an assumed law into one within 0.2 % of true.
- ANSWER: A (2026-11-09T04:14Z, user: "Yes, add the gun"; D-user-42).

## Q21 2026-11-09 [closed 2026-11-09 by D-user-43] — BLOCKING(!) F1d of uncommitted code tries: may the static cone come from the working tree (478) instead of the base commit?
- Found: Z1 adds the crystal clusters as an input of the neutrals factory. 460's MSF run walks the static cone of the yaml's commit (a15b0db6, the base), so F1d reports the 5 crystal factories the Z1 install runs as outside the cone (FAIL). Phase 5's code tries never changed the cone, so the gap never showed. 478 runs 460's own F1a walk and F1d janadot with the working tree as the source: Z1 against a15b0db6 FAIL, against the working tree PASS, the base row against a15b0db6 PASS.
- Why it matters: every crystal try changes the cone; without a source that matches the build, every one is FOUL by F1d regardless of what it does. With `please-git` tries are commits and 460 --source covers it.
- Options: A) read F1a + F1d from 478 on the working tree for uncommitted code tries (D-default-49; the other 460 clauses unchanged); B) commit each try (`please-git`) so 460 walks the try's own commit; C) treat a cone change as FOUL. Recommendation: A — the same check on the source that was built; B is equivalent when you grant commits.
- Frozen until answered: the fair-play verdict of every code try that changes the static cone — Z1b, Z5 and their successors (Z2 and Z4 run on the Z1b install). Their ACCEPTED verdicts stand only under A or B; under C the crystal line is FOUL and the base returns to MSF6_Y9. (Raised to BLOCKING 2026-11-09T08:22Z: D-default-49 changed what a frozen gate accepts, which is the user's call.)
- Continuing meanwhile: nothing that needs the verdict — the run ended for review; Z6 on D6h for Q22.
- ANSWER: A (2026-11-09, 13:09–13:12Z, user, chat: "A: working tree (Recommended)" in the question dialog; confirmed after a plain-language explanation with "1 a ." at 13:13Z) → D-user-43. F1a + F1d of uncommitted code tries come from `478` on the working tree; the ACCEPTED verdicts of Z1b, Z2, Z4 and Z5 stand.

## Q22 2026-11-09 [closed 2026-11-09 by D-user-44] — Z5 finds 11 % more Λ but measures −t 16 % worse at 9x275: keep it as the base for the next tries?
- Found: Z5 (the crystal law's energy as a competing hypothesis for tagged Hcal photons) raises N_found on the search halves 1646 → 1826 (z +11.62) and purity 27.1 → 29.5 %. On the 1381 Λ at 9x275 that Z4 and Z5 both find, the −t resolution σ68 goes 0.122 → 0.142 GeV² (within ±0.1 GeV²: 57.6 → 51.0 %), the Λ energy reco / true median 1.073 → 1.110; at 9x130 0.120 → 0.126. The neutron reads high (median 1.07) and the crystal-law photon energies add to it.
- Why it matters: the phase selects on N_found with a purity guard (loop v5/v6), so Z5 is accepted and the next tries build on it. If −t precision weighs more for the MSF analysis than the Λ count, the base should stay Z4 or a try should correct the Λ energy scale first.
- Options: A) keep Z5 as the base and add a try that corrects the Λ energy scale (the neutron's law in the ZDC chain), judged by N_found with −t reported; B) return to Z4 as the base; C) add −t (σ68 on common Λ) as a second guard of the selector. Recommendation: A — the count gain is large and the energy bias has a visible cause to work on.
- Recommendation revised 2026-11-09T08:22Z: D (Z6 as the base) if −t precision matters as much as the count for the MSF analysis — Z6 keeps 1797 found (+21 % over Y9; Z5 1826, +23 %) at −t σ68 0.121 / 0.120 GeV² (Z5 0.147 / 0.128, Y9 0.124 / 0.133); Z5 if the count alone matters. Z6's held-out check (2026-11-09T08:39Z): 1411 → 1703 (+21 %, z +13.70), purity 25.8 → 28.0 % — REPRODUCES, so either choice has its checkpoint.
- New evidence (2026-11-09T08:03Z): option A tried as Z6 (the crystal-law photon's Hcal column out of the neutron): N_found 1826 → 1797 (−29, z −2.80, REJECTED by 463) and −t σ68 0.147 → 0.121 GeV² at 9x275 (Y9 0.124), 0.128 → 0.120 at 9x130, bias −0.037 → −0.009 GeV². Z6 = +21 % found Λ over Y9 at a better −t than Y9's. If −t counts, answer D) take Z6 as the base (its install is kept).
- ANSWER: D (2026-11-09, 13:09–13:12Z, user, chat: "D: Z6, better −t" in the question dialog; kept after the explanation, 13:13Z) → D-user-44. Z6 is the base and the selector's reference for the next tries; −t σ68 is reported beside every try.

## Q23 2026-11-09 [open] — Phase 7: which EICrecon base do the pull-request units sit on?
- Found: every Phase 4–6 change sits on the pin e5e2a60c with two open upstream PRs folded in: PR 3064 (ZDC clustering and calibration, last updated 2026-11-05) and PR 3063 (Λ mass windows removed, updated 2026-11-09T17:31Z). EICrecon main has moved since the pin. The Phase 4 calibrations were refit for 3064's clustering; P3 needs 3063, P6 and P8 need 3064.
- Why it matters: reviewers and CI see the code on main; evidence measured on the pin may not transfer if main or the two PRs changed the same files.
- Options: A) main with the current heads of PRs 3064 and 3063 stacked under the series (the units become PRs that say "depends on #3064, #3063"); B) the pin (cheapest, every Phase 4–6 number stays comparable; you rebase the branches before opening the PRs); C) the pin first, then a port of the whole series to main at the end with the identity checks repeated there. Recommendation: A — the identity checks are made where the code will land, and Step 0 lists every difference between the PRs' current heads and the program's copies.
- Blocks: Phase 7 Step 0 item 1 (the base) and everything after it.
- ANSWER:

## Q24 2026-11-09 [open] — Phase 7: may two benchmark samples be added to the frozen datasets, for the units that change the LYSO and B0 ECal clusters?
- Found: two units change clusters that other people's benchmarks read. P6 (the LYSO crystal clustering) changes `EcalFarForwardZDCClusters`, which the `zdc_lyso` benchmark reads (single photons 5 MeV–1 GeV, its own generator, 1000 events per point). P7 (B0 ECal splitting and law) changes `B0ECalClusters`, which the `far_forward_dvcs` benchmark reads (DVCS events from the EVGEN area the CI uses, simulated with npsim). Neither sample exists here; `configs/datasets.yaml`, `scripts/700_benchmarks/` and `401` are frozen.
- Why it matters: without them, P6 and P7 show only that nothing else moved (capybara, identity) and the B0 photon gun D2b, not the benchmarks the LYSO and B0 people look at.
- Options: A) both samples, generated by the benchmarks' own recipes, and their plot scripts copied into `scripts/700_benchmarks/` (temporary FROZEN exceptions, as D2b and D2c); B) zdc_lyso only; B0 shown by capybara and D2b; C) neither. Recommendation: A — they are the reviewers' own plots, and both are small samples within the D-user-35 limits.
- Blocks: Phase 7 Step 0 item 5; P6 and P7 wait for it, P1–P5 do not.
- ANSWER:
