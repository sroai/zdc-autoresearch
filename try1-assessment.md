# Assessment of try 1 and of its self-review (`try1-expert.md`)

Written 2026-11-06 by the session that designed loop v2, from the record
under `space/` and the report `try1-expert.md`. Nothing was re-run. Every
number below was checked against the file it comes from.

## Verdict on the question

**Modify and continue, as try 2 under a versioned loop v3. Do not start from
scratch.**

A scratch restart is scientifically warranted only if one of three things is
wrong: the ruler, the data, or the shape of the phases. None fails:

| what a restart would redo | state in the record | wrong? |
|---|---|---|
| the ruler: references R0/R1/Rt, determinism (9048 + 960 leaves identical in three runs), noise floor (26 tests, spread/error 0.26–1.97), gates seen to fail on damaged copies | `phase0_foundation.md`, `noise-validation.json` | no |
| the data: guns on the full detector (D-user-8), D4 with the generator's 4 mrad acceptance (`413`: 1.65–32.6 % per thrown), D5 sized by clusters, held-out seeds D1h/D4h | `datasets.yaml`, `lambda-gun-acceptance.json` | no; the acceptance cut limits the per-thrown numbers but is measured and reported |
| the phases: foundation → dissection → parameter loop → code → delivery | loop v2 | the shape holds; Phase 2's aim and cost are wrong, and both are fixable |

What failed is one phase's aim (Phase 2 tuned six parameters that the run's
own Step 0 said could recover only the 1–3 % of "missing" photons while
89–97 % of pairs are merged) and the cost per experiment (63 GB, two hours).
Neither touches Phase 0's 141 CPU-h or Phase 1's pre-registered result, which
already answers the reviewers of PR 3064. Redoing them would produce the same
files.

For the autoresearch article a restart is worse, not cleaner: the most
instructive event of try 1 is a loop that measured the cap (F4, Phase 0
item 12) and then spent two phases inside it until the user pointed at it.
A fresh start erases that. A try 2 under loop v3, with the lessons written
into rules and the ruler re-proven at the run start (as the loop already
requires), gives the clean pre-registration a restart would give and keeps
the record continuous.

The three upstream PRs in flight (section 5, added after checking them on
2026-11-06) strengthen this verdict: the foundation makes each of them a
cheap new reference row, and the ceiling tools already give a pre-registered
prediction for PR 3063 that no restart could produce sooner.

One record-integrity blemish is real and a restart does not fix it: the report
admits that some early timestamps were written ahead of the wall clock. The
fix is an audit of the Phase 0/1 timestamps against the transcripts under
`/data/zdc-autoresearch/provenance/` and file mtimes, with the corrected
times written into the ledger as a dated correction. That is a try-2 task,
done before any article number is quoted.

## 1. The assessment, assessed

**It is accurate.** Every claim I checked matches the record: the verdicts of
all 12 judged experiments (`EXPERIMENTS.md`), the S0all means and the
per-thrown numbers (D-user-20), the ceilings and the acceptance
(`lambda-ceiling-variants-P1b_R0_thr.json`, `lambda-gun-acceptance.json`),
the held-out check (+0.058 / +0.031 / +0.012 at 125 / 175 / 250 GeV, lost 0),
the decisions it cites (D-user-14, -19, -20, -21, D-default-25), F9 and the
truth-chain observation O2, and the configs: all 17 experiment files write
`output_collections: [".*"]` on every dataset. I recounted the hypothesis
tally from the ledger: 45 ✓ / 20 ✗, as stated.

**It is a self-review**, by the agent that ran try 1, and says so in its
header. Its blind spots are the run's blind spots:

1. **Six MUST items, all more instrument.** The Λ chain offline, the S0
   ceiling, the cost cut, preflight, the tally script, the headline table.
   All are right, but "try 2 starts from the Λ chain" is a continuation plan.
   The report never asks whether S0 was still the right selector after
   D-user-14 opened the Λ code; it offers the Λ number only as a post-B9d
   co-selector (T2-D1). That is the central design correction and it belongs
   at the top, not in the defaults list. See section 3.
2. **The S0 ideal-partition ceiling (MUST item 2) changes no decision.** No
   parameter experiment can be judged against it (the parameter families are
   closed), and the first code experiments are in the Λ chain. It is a
   SHOULD, not a gate on starting try 2.
3. **The 20 GeV raw-sum guard.** The report flags that the S3 guard fails
   E02/E04 at a momentum the D4 neutrons never reach and asks the user (Q11).
   It also notes that both still fail S0n at 275 GeV, so the chaining family
   stays closed under either answer. That is correct and the question is
   worth answering as recommended (guard at 50–275 GeV, 20 GeV reported).
4. **It is fair about agent behaviour** (section 4.4): phase order followed
   past the bottleneck, lesson written without changing the config that
   caused it, a prediction rate reported before counting, headline numbers
   computed in chat, 24 processes on 24 cores. These are the right five.
5. **What it owns that is not the run's fault.** Loop v2 rule 4 ("static G4
   for parameter experiments") and the setup's budget line ("D5 and full G4
   at checkpoints only") contradict rule 5 (G1–G3 per verdict, which are D5
   metrics). That contradiction was written by this session, not by the run.
   The run resolved it by reconstructing everything with every collection,
   which is the expensive reading. The report's item 3 (restricted
   collections on D5, full compare at checkpoints) is the right resolution
   and the setup file must say so.

## 2. The experiment, assessed

**Phase 0 is sound and is the asset.** The gate failed when it should, the
references reproduce, the noise floor is measured, the per-particle truth
matching works. Keep every file of it.

**Phase 1 is the scientific product so far.** The dissection splits
PR 3064 into its parts with numbers: the sub-pitch XY distance alone makes
the column clusters (G1, G2 at 1.000) and gives about half of the PR's photon
gain and a third of its neutron loss; the threshold pair alone (P1b) is the
clean gain (S0all 0.017 → 0.048, every guard in, held-out confirmed). The PR
as a whole is below stock on the all-three separation (0.013). A reviewer of
PR 3064 can use `phase1_dissection.md` today. F6 (stock calibration does
not fit stock clusters) and F8 (stock photon box rejects every ZDC photon;
fixed in PR 3114) are findings the PR's authors need.

**Phase 2 was run inside a space the run had already measured as nearly
empty.** The Phase 2 Step 0 (15:38 UTC) states the merged fraction 0.89–0.97
and that B1/B2 can recover only the missing 1–3 %. Six experiments followed,
one accepted (E01, the adoption of P1b), two families closed. The expected
gain per experiment was small before the first one ran, and the loop had no
rule that says "re-rank the backlog by expected yield on the deliverable
when a cap is measured". Loop v3 needs that rule.

**The Λ yield is zero for every 3×3 clustering and cannot exceed 0.85 % per
thrown under the frozen chain** (stock pairing with perfect separation). The
same offline tool shows a stable vertex-aware pairing reaching 14.1 % mean,
27.8 % at 275 GeV: a sixteen-fold headroom in code the program is allowed to
change since D-user-14. That is the lead, and the run found it (F4, F9)
without acting on it.

**Operations cost four runs and about three hours**, all recovered, none
prevented: disk full at 865 GB, eicrecon exit 0 on failed writes, 24
processes on 24 cores. The fixes are mechanical (preflight, integrity check,
process cap in `300`) and the report lists them correctly.

**Record quality** is high: every decision has a D-number with evidence,
every hypothesis a timestamp before its run, 69 % of pre-registered cells
right with the misses on sizes, not directions. The one blemish is the
timestamp admission above.

## 3. What try 2 changes (the pivot, in order)

1. **Loop v3**, a new file beside v2, with: the Phase 2 close-out; the
   re-aim rule (when a ceiling is measured, the backlog is re-ranked by
   expected gain on the deliverable before the next experiment); the cost
   rule (restricted collections per experiment, full compare at
   checkpoints); the preflight and process cap; headline numbers from a
   script only; timestamps from `date -u`. The setup file's budget line
   corrected under a D-user decision.
2. **Close Phase 2 formally**: the Phase 2 report with the waterfall, the
   family ceilings, the remaining checkpoint parts (question sweep), and
   "Next run recommendations". No B4 run; B2/B5/B6 dropped with the report's
   reasons.
3. **The Λ chain on real clusters** (report item 1) on all 15 rows, from the
   `410` npz tables, validated on L01 and R1 against the in-EICrecon
   `S4a_tm`. This is the number that ties any clustering row to a Λ yield;
   it costs minutes per row and no reconstruction.
4. **Phase 3 starts with B9d**, the vertex-aware pairing with the stable
   vertex, pre-registered against 14.1 % / 27.8 % and against item 3's number
   for P1b. **The selector for the Λ family is the Λ yield per thrown**
   (`S4a_tm`, truth-matched, fixed 0.03 GeV scoring window, windows frozen),
   with S0 as a guard (identical clustering, so it cannot move). Once B9d is
   accepted the same number becomes the selector for clustering experiments
   too, with S0 and the raw-sum guards as guards. The expert review demoted
   S4a because it was capped and its windows were tunable; with the Λ code
   open, the cap is the thing being removed, and with the windows frozen it
   is no longer gameable.
5. Then the clustering code tier: "chain at 480 keV, collect at 315 keV"
   (E02's premise without its neutron cost) and the Island chain with
   splitting (B8), judged on the Λ number with the raw-sum guards.
6. Q11 (raw-sum guard momenta) answered by the user at the start; the
   timestamp audit done before any article number is quoted; the findings
   F4+F9, F1, F6–F8 drafted for upstream (Phase 4).

## 4. Why not from scratch, in one paragraph

Everything that would be rebuilt is correct; what is wrong is where the loop
aimed after it measured the cap, and how much each shot cost. Both are rules,
and rules are versioned, not re-run. A scratch restart would spend a night
reproducing Phase 0 and Phase 1 to the byte, discard the one record that
shows a pre-registered loop failing in the informative way, and leave the
same Phase 2 question open. Try 2 under loop v3 is the restart that keeps
the evidence.

## 5. The upstream PRs in flight (checked 2026-11-06)

All three are by the same author (Baptiste Fraïsse) and form one package:
clustering and calibration (3064), the photon box (3114), the Λ chain
(3063). The program measured them one at a time, never together, and never
3063 at all.

### PR 3114, photon box 100/12 → 110/22 mm: MERGED

Merged 2026-11-05 21:08 UTC (approved by veprbl), backported to v1.43 as
PR 3117. The program already carries it as reference R2 (D-user-15) and as
L01 = P1b + 3114. Consequences:

- **The baseline moved.** Main now has the box fix; R0's "no Λ at all" is
  no longer the state of upstream. Every Λ comparison for the article and
  for PR reviews is against R2 (stock + 3114), not R0. The program's pin
  (e5e2a60c, 2026-11-03) predates the merge; keeping the pin and treating R2
  as the baseline costs nothing, since 3114 is parameter-tier on the pin.
  Finding F8 is RESOLVED upstream and the index should say so.
- **The program's measurement contradicts the PR's claim in part.** The PR
  body says the new box "strongly improves the Λ reconstruction". On stock
  clustering it gives zero Λ at every momentum (R2: 0.00 % per thrown, S5
  1.0 per 1000 at 9x275), and on P1b +25 gained / 0 lost, below 3σ (L01).
  The reason is in the record: on 3×3 clustering 87–98 % of the photon
  pairs are merged into one cluster, and a box can only tag photons that
  have a cluster of their own. The box fix is necessary and not sufficient;
  the author's gain presumably comes from the package (column clusters from
  3064 plus the wider box). That is a review comment worth posting, with the
  R2 and L01 numbers.

### PR 3063, relax the Λ mass cuts: OPEN, not in the program's record

Open since 2026-10-28, review required, CI building again after fixes on
2026-11-05/06, 18 commits behind main, mergeable. One file:
`LambdaReconstruction.cc`. What it does:

- removes the step-3 π⁰ mass window (the IP-pointing preselection) and the
  Λ mass window in `reconstruct_from_triplet`;
- runs the full vertex reconstruction (the IDOLA iteration) on every
  (n, γ1, γ2) triplet and ranks candidates by a χ² of the two masses
  computed after the vertex, with `pi0Window` and `lambdaMassWindow` kept
  only as the χ² scales;
- always writes the best candidate; mass selection is left to the analysis.

This is the program's finding F4 as a PR, and it walks straight into F9:

- **F4.** The IP-pointing π⁰ window is exactly the cap the program measured
  (decays beyond about 4 m never pass; 0–0.068 of accepted D4 events). PR
  3063 removes it.
- **F9.** With the window gone, every triplet goes through the pin's IDOLA
  iteration, which the program measured to diverge transversely for decays
  far from the IP. `414`'s `vertex` pairing is this algorithm (IDOLA first,
  then the masses). Its numbers, per accepted D4 event, are a pre-registered
  prediction for PR 3063 made before the program knew of it:

| momentum (GeV) | 3063-like (IDOLA, ideal inputs) | stable vertex (B9d, ideal) | 3063-like, P1b resolution | B9d, P1b resolution |
|---|---|---|---|---|
| 100 | 0.62 | 1.00 | 0.50 | 0.73 |
| 150 | 0.76 | 1.00 | 0.65 | 0.79 |
| 200 | 0.83 | 1.00 | 0.73 | 0.82 |
| 275 | 0.86 | 1.00 | 0.78 | 0.85 |

  Per thrown Λ → nπ⁰ with the measured resolution and perfect separation:
  3063-like 0.8–25.6 %, B9d 1.2–27.8 %, stock 0–2.1 %. So PR 3063 is
  predicted to take most of the sixteen-fold headroom, and the stable vertex
  adds about half again at 100 GeV and a tenth at 275 GeV. The right shape
  for B9d is therefore a small follow-up on top of 3063, not a competing
  chain: a review comment with these numbers now, a patch after.
- **Two caveats the review needs.** First, 3063 outputs a candidate
  whenever a triplet exists; on real clusters, where 89–97 % of pairs are
  merged, the best-χ² triplet will often be a wrong combination, so the
  untruthful-candidate fraction (S4a_any − S4a_tm, the guard of
  D-default-25) and the candidates-per-event rate on D5/D6a (S5) are the
  numbers that decide whether MSF can use the collection. Second, the
  prediction above assumes perfect separation; the Λ chain on real clusters
  (section 3, item 3) gives the actual number per clustering row.

### PR 3064, clustering and calibration: OPEN, now CONFLICTING

Head 92288da4 (2026-11-05) only merges main; the three files the program
patched are unchanged, so R1 still represents the PR. It conflicts because
3114 changed the same two box lines it changes (to 150 mm length). The
reviewer's comment of 2026-10-30 (columns, no high-energy clusters, many
low-energy ones) is unanswered upstream; `phase1_dissection.md` answers it.

### What this adds to try 2

1. **Two reference rows**, both cheap: R3 = R2 + PR 3063 (one-file patch on
   the pin; the file is unchanged on main since before the PR's base, so it
   applies cleanly) and the author's package R1 + 3114 (parameter-tier on
   the existing R1 build; one D4 reconstruction). The package row is owed to
   a fair review of 3064: the program never measured the PR with the box it
   was tuned with.
2. **B9d is re-scoped** as "R3 + stable vertex", pre-registered against the
   table above: R3 on P1b clusters at or below the 3063-like column times
   the separated fraction; B9d above R3 at every momentum, by the most at
   100–150 GeV.
3. **Three review comments** can be drafted from the record now, before any
   new run: 3114 (necessary, not sufficient; R2 and L01 numbers), 3063 (F9
   with the table; the stable-vertex fix), 3064 (the dissection). The user
   posts.
4. **Record updates**: F8 RESOLVED; F4 and F9 "addressed in part by PR
   3063"; the headline baseline R2.
