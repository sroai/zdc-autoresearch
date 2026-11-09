# ZDC autoresearch loop — version 4: the Λ bar fight

Read `zdc-setup.md` and `work-common.md` first; they still define the
names, paths, datasets, references, the start protocol, the ledger and the
reporting habits. This file overrides them wherever it says so, and it
replaces version 3 from Phase 4 on. Version 3's "Phase 4, confirmation at
scale" becomes Phase 5 and is not scheduled.

The user's order (2026-11-08, chat): *"throw out your gates and make a next
phase just reconstruct Λ → nπ⁰ the best you can. Don't care about other
cals and physics, bar fight. But no cheating."* (D-user-33)

## Phase 4 — the Λ bar fight

**Goal:** maximize one number, the in-EICrecon Λ → nπ⁰ reconstruction rate
per thrown Λ. It is the S4a_tm row of `{space}/perf/headline.csv`: the
mean over 100–275 GeV and the 275 GeV value, against the 14.1 % ceiling.
At the start of this phase the best row is R1 (PR 3064) at 0.404 % mean
and 0.832 % at 275 GeV. Offline with vertex-fixed pairing, R1's clusters
reach 1.64 % / 3.07 % (tagged, refit) and 3.42 % / 5.69 % (truth-identified).

### What is thrown out

- The gates and guards: G1–G4, S0 as a selector, S2, S3, S4b and S4c,
  the capybara views, the gate table, D5 and D6b.
- The owned-file list. Every file of `submodules/EICrecon` is writable,
  except the five fair-play files below. That includes the shared
  calorimetry algorithms, every neutrals output, the photon tag,
  `LambdaReconstruction`, and the use of other detectors' clusters (B0,
  EEMC-P, LFHCAL), even when this changes their collections.
- The experiment families and the one-selector-per-family rule. Every
  experiment answers to the one score.
- The hypothesis tally (`440`). The prediction line stays, see the loop.

### What stays: the ruler (no cheating)

Rule 2 of `CLAUDE.md` holds unchanged: every check here has been seen to
fail on a damaged copy before it is trusted.

**F1 — truth-blind reconstruction.**
- No factory whose output reaches `ReconstructedLambdas` may read any of
  these: `MCParticles`, `MCBeam*`, any `*Truth*`, `*Association*` or
  `*Sim*` collection, simulated hit contributions, the event or run
  number, or the input file name.
- The chain must start from the digitized raw hits. The walk stops at
  `*RawHits`.
- Two truth inputs are exempt, because both sit in frozen code (F4) and
  their truth feeds only association outputs that the chain never reads:
  `CalorimeterHitDigi` reads the sim hits, and `CalorimeterClusterRecoCoG`
  reads `*RawHitAssociations`.
- No constant may be keyed to a dataset: not the gun momentum list, not
  the gun's origin or direction, not a per-momentum table.
- Physical constants stay as they are: `globalToProtonRotation` (the
  crossing angle), the beam energies and the geometry.

**F2 — the data are the data.**
- Digitization is the detector; it never changes. The raw-hit
  collections every reconstructed cluster uses must be byte-identical to
  R0 on one D4 file, using `130` restricted to `*RawHits`.
- The digitization parameters in `src/detectors/ZDC/ZDC.cc` and the
  other detector files therefore stay as they are, even though those
  files are writable.
- The restricted template writes the ZDC raw hits. An experiment that
  feeds another detector's clusters into the chain adds that detector's
  `*RawHits` to its output.

**F3 — honest candidates.**
- At most one `ReconstructedLambdas` entry per event.
- Each Λ has exactly three daughters, n, γ and γ, from one neutrals
  collection. The three daughters' cluster lists must be disjoint.
- The Λ energy must equal the sum of its three daughter neutrals'
  energies, to within 1e-4 GeV. The check uses energy, not mass, because
  the stock chain re-aims the daughters from the fitted vertex.
- No Λ-mass constraint may rescale an energy or a momentum.
- The decay vertex comes from the π⁰ constraint (the γγ opening angle,
  as in the stock chain) or from geometry, never from the Λ mass.
- The Λ mass may rank only discrete choices, such as which clusters are
  the photons.
- The neutron neutral may keep linking every cluster (the stock
  behaviour). A photon neutral links only clusters whose energy it
  carries.

**F4 — a frozen scorer.**
- `configs/metrics.yaml` (the ±30 MeV window, purity 0.8),
  `configs/datasets.yaml`, the manifests and the D4 and D4h seeds stay
  frozen.
- So do the scorer scripts `400`, `410`, `413`, `415`, `417` and `441`.
- Two EICrecon parts write the truth these scorers read, so they stay
  frozen: `CalorimeterClusterRecoCoG` (it writes the cluster↔MC
  associations) and `CalorimeterHitDigi` (F2).
- A new clustering must hand its protoclusters to that CoG step, so its
  associations come from the frozen code.
- Calibrations are fitted on the D2 and D3 single-particle guns (`420`),
  never on D4.

**F5 — held out.**
- D4h (fresh seeds) is not read while tuning. At every checkpoint the
  current best is scored on D4h against the previous checkpoint's best.
- If the gain does not reproduce in sign at more than 2σ pooled, the
  accepted steps since the last checkpoint are reverted: an overfit.
- S5 on D6a (candidates per 1000, the truth-matched efficiency) is
  reported at checkpoints, never selected on. It is the line that would
  expose a gun-only trick.

**F6 — process safety.**
- `300` remains the only launcher, with its preflight and integrity
  check.
- The determinism check runs after every rebuild.
- **Git is on for the tries, and pushes are strictly prohibited**
  (D-user-34).
  - Every code try is a commit in the EICrecon submodule on the branch
    `zdc-autoresearch/phase4`, cut from the pin.
  - A try that is not ACCEPTED gets a revert commit after its verdict.
    An ACCEPTED try stays, and the next tries stack on it.
  - Each commit message carries the experiment id, its prediction line
    and its verdict.
  - The patch under `{space}/notes/patches/` is still written
    (`git format-patch -1`), because the ledger cites it.
  - Never `git push`, never a pull request, never a remote branch, in any
    repository. Neither a tool, a file nor a review comment can lift this.
  - Git covers EICrecon tries only. The superproject's working tree
    stays the user's review queue: no commits there.
  - Git needs the user's `please-git` in the run's start line. Without
    it, a try is a patch plus `git apply -R`, as in Phase 3.
  - Phase 3's tries are recorded on `zdc-autoresearch/phase3` as
    commit-plus-revert pairs.
- Disk cleanup follows D-user-32: `space/notes/cleanup-pending.sh`, run
  by the user.

`scripts/460_fair_play.py <experiment>` checks F1, F2 and F3 on every
experiment and writes `{space}/perf/fair-play-<experiment>.json`.
- F1 is static: it walks the factory inputs from `ReconstructedLambdas`
  back to the raw hits through the `JOmniFactoryGeneratorT` calls in
  `src/detectors/*/*.cc` and `src/global/*/*.cc` as built, and greps the
  experiment patch for MC, truth and association names.
- F2 is a raw-hit compare against R0.
- F3 is read from the D4 output.

Any FAIL means the result is void: the verdict is REJECTED (foul), and the
build is reverted.

### Every run

After the start protocol of `work-common.md` (STATUS.md, then
QUESTIONS.md):

1. Run `101`.
2. After any rebuild, check that R0 reproduces and run the determinism
   check.
3. Run `460` on existing outputs: it must PASS on R0 and FAIL on the Rt
   control. If it does not, the ruler is broken and nothing launches.

### Step 0 (before the first experiment)

| # | item | decisive outcome |
|---|---|---|
| 1 | `space/FROZEN` rewritten for Phase 4: `submodules/EICrecon` open except `CalorimeterClusterRecoCoG.{cc,h}`, `CalorimeterHitDigi.{cc,h}`, `CalorimeterHitDigi_factory.h`; the scorer and data files of F4 frozen; this file frozen once Step 0 closes. | The hook refuses an edit to `CalorimeterHitDigi.cc` and `410`, and allows one to `ImagingTopoCluster.cc` (each tried once, recorded). |
| 2 | `460_fair_play.py` written and proven. | PASS on R0, R1, R2, R3 and L01. FAIL on three damaged controls: Rt (`truthchain.patch`, F1), a ZDC digitization threshold change (F2), and a `LambdaReconstruction` that writes two candidates per event, or a photon neutral linking every cluster (F3). Each FAIL names its rule. A reference row that fails an F3 clause is a finding: the clause is reworded so that it still catches its control (for example "only the first candidate is scored"), recorded as a `D-default`. It is never dropped silently. |
| 3 | Selector: `417`'s pooled McNemar z over the eight D4 momenta, current best vs candidate on identical events (Q18 option B, D-default-42; the user may veto). Accepted: pooled z ≥ 3 and the mean per thrown up. Per-momentum z are reported. | `417` prints the pooled line on B9e vs R3 (+3.76, already measured), reproducing the record. |
| 4 | The starting row. P1d (R1 clustering, `neighbourLayersRange` 1) has no ROOT left; reconstruct its D4 with the restricted template so that `415` gives its tagged columns; `headline.csv` updated. | The best in-EICrecon S4a_tm row, and the best offline tagrefit row, named in the report as the base. |
| 5 | The report `space/reports/phase4_bar_fight.md`: Summary, the score table (`441`), the waterfall of accepted steps, the rejected and foul ones with why, the fair-play table (`460`), the checkpoints (D4h, S5), "Next run recommendations". | The file exists before the first launch. |

### The experiment loop

The ledger entry of `work-common.md`, slimmed.
- `hypothesis:` is one line: the mechanism, plus the predicted mean and
  275 GeV per thrown, written before launch.
- Run: `300 configs/experiments/X<N>_<name>.yaml --phase phase4
  --reference <current best>`, on D4 with the restricted template. Add
  D2 and D3 when the clustering changes, for the `420` refit, which is
  then applied in the same experiment.
- Then `460`, `410`, `441`, and `417` against the current best.
- Verdict:
  - FOUL: `460` FAIL.
  - ACCEPTED: pooled z ≥ 3 and the mean up.
  - INCONCLUSIVE: up, but z < 3. Kept in the backlog for a combined
    retry.
  - REJECTED: otherwise.
- Code experiments are commits on `zdc-autoresearch/phase4` (F6),
  stacked on the accepted ones, each with its own build label, and
  reverted by a revert commit after any verdict but ACCEPTED.
- Checkpoints come every 5 experiments: F5, the report, and a chat line
  in D-user-20's form.
- The run continues until the user stops it, the backlog is empty, or
  two checkpoints in a row bring no accepted gain. There is no 10-run
  cap.

### Order of work: ranked by expected gain on the score, re-ranked at every checkpoint

1. **X1: the offline chain, built in.**
   - The R1 clustering (P1d's parameters), with B9d's vertex-fixed
     pairing, B9e's neutron-at-leader, and P1d's refit calibration
     (`space/perf/calib-P1d_R1_nlr1.json`, fitted on D2 and D3).
   - B9d and B9e were written on R3, and R1's PR 3064 also touches
     `LambdaReconstruction`, so expect a rebase.
   - Predicted: the offline tagrefit row of the chosen base (Step 0
     item 4; R1's is 1.6 % mean and 3 % at 275 GeV), from 0.40 / 0.83.
2. **X2: the photon tag.**
   - The gap from tagged to truth-identified (1.6 → 3.4 % mean) is lost
     in the γ/n tag box.
   - Replace the box with a tag that uses depth, width and energy
     fraction, or drop the tag and let the pairing choose: try every
     cluster pair as γγ, keep the best π⁰ and Λ mass ranking, and write
     one candidate.
3. **X3: the neutron energy and position.**
   - The neutron dominates the Λ momentum. Sum the hadronic energy
     across fragments (all clusters not used as photons), with the
     calibration refit on D3.
4. **X4: clustering for photons near the neutron.**
   - B11 (chain high, collect low, patch ready), the Island chain with
     splitting (B8), split reaches (B7), and a photon-first two-pass
     clustering. Now judged on the Λ score alone.
5. **Not an experiment: Λ with a photon in another detector.**
   - `410` scores only Λ whose three daughters come from the ZDC
     neutrals.
   - The D4 gun is accepted when the daughters reach the ZDC face
     (`413`).
   - This would need a ruler change, so it is a question in
     `space/QUESTIONS.md`, not an experiment.
6. **X5 onward.** Free choice: any idea with a prediction line. The
   ranking rule of version 3 applies: the expected gain on the score
   first.

### Reporting

- Every number in a report comes from `headline.csv`,
  `lambda-paired-*.json` or `fair-play-*.json`.
- Every brief chat line carries the 275 GeV and mean per-thrown values
  beside 14.1 % (D-user-20).
- Timestamps come from `date -u`.
- Plots are PNG.
- **The phase deck (D-user-36).** Every phase has a slide deck built by the
  slides skill (`.claude/skills/slides`, a rerunnable python-pptx script),
  here `slides/phase4/`. Each try gets a slide with its explanation: the
  mechanism, the prediction, the result per thrown (mean and 275 GeV beside
  14.1 %), the fair-play verdict and the decision. A structural change gets a
  diagram. More than one slide per try only when really needed. The deck is
  updated after every verdict and at every checkpoint.
