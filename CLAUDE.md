# zdc-autoresearch

Autonomous optimization of the ePIC ZDC reconstruction in EICrecon, run as
a phase-gated autoresearch loop. The physics: `Λ → n π⁰ → n γ γ` in the
Meson Structure Function program; the trigger: EICrecon issue #2737 and
PR #3064 (`docs/zdc-problem.md`).

## Start line

One chat line starts a run: `Read zdc-setup.md, work-common.md and
zdc-autoresearch-loop-v6.md. Run.` (v2 holds the finished Phases 0 and 1;
v3 the Phase 2 close-out and Phase 3, halted 2026-11-07; v4 Phase 4, the Λ
bar fight, closed 2026-11-08; v5 Phase 5, Λ → nπ⁰ on MSF events, closed
2026-11-09, D-user-41; v6 Phase 6, the crystal-seeded ZDC photon finder,
prepared, starts on that line.) Add `online` if you will answer in chat
during the run; add `please-git` if commits are allowed this run.

## Three hard rules

**Phase 6 (loop v6, prepared) keeps Phase 5's ruler and adds the crystal
section's raw hits to F2 and a crystal F3 check. Phase 5 (loop v5, D-user-39,
closed) kept Phase 4's suspension and fair play
below; its one selector is N_found, the truth-matched Λ → nπ⁰ on the MSF
search halves D6s (paired test), with a purity guard and D6h held out.**

**Phase 4 (loop v4, the Λ bar fight, D-user-33) suspends rules 1 and 3:**
EICrecon is open except the fair-play files, there are no gates or guards,
and the one selector is the in-EICrecon Λ → nπ⁰ rate per thrown Λ
(pooled paired test). Rule 2 holds, and the fair-play rules F1–F6 of
`zdc-autoresearch-loop-v4.md` replace the gates: truth-blind
reconstruction, raw hits identical to R0, honest candidates, a frozen
scorer, held-out D4h. A FAIL voids the result. No cheating.

1. **Only the ZDC changes.** After Phase 0 the hook `.claude/hooks/protect.py`
   refuses writes to everything `space/FROZEN` lists: every submodule except
   the ZDC-owned files of EICrecon, the dataset and metric configs, the
   gates, the manifests. A needed change there is a question in
   `space/QUESTIONS.md`, never an edit.
2. **The ruler is proven before it is trusted.** Every gate has been seen to
   fail on a damaged copy; every parameter switch has been seen to change an
   output; the reference R0 reproduces at every run start. A check that has
   only ever printed PASS proves nothing.
3. **One fixed scoreboard, one selector per family, held-out confirmation.**
   Every experiment reports the whole scoreboard row (`zdc-setup.md`,
   Scoreboard) and the headline per thrown Λ → nπ⁰ (`space/perf/headline.csv`).
   Clustering experiments select on S0, the truth-matched separation
   efficiency on the Λ gun, by a paired test on identical events, with the
   offline Λ chain on real clusters reported beside; the Λ family
   (`LambdaReconstruction`, the neutrals cut box) selects on S4a_tm, the
   truth-matched Λ yield under the fixed scoring window, which no experiment
   changes; once the stable vertex-aware pairing is accepted, S4a_tm
   co-selects clustering changes (loop v3, selector rules; a default the
   user may veto). S2 photon scale, S3 raw neutron energy, S4b, S4c and G1
   to G3 (within the limits the user set) guard; G4 (non-ZDC collections
   identical, published as the gate table and the capybara views) gates.
   D1h and D4h (fresh seeds) are checked at checkpoints and revert an
   overfit; D6b (MSF at scale) confirms and never selects. The baseline of
   every Λ comparison is R2 (stock + the merged PR 3114).

## Where to look

- Where to resume: `space/STATUS.md`. Questions for the user: `space/QUESTIONS.md`.
- The phase ledger: `space/LEDGER.md`. The experiment ledger: `space/EXPERIMENTS.md`.
- Every command: `scripts/` (numbered: 1xx foundation, 2xx understanding,
  3xx experiments, 4xx evaluation, 5xx farm, 7xx figures); `README.md`.
- Farm: `.claude/skills/ifarm-tunnel`, `.claude/skills/ifarm-slurm`,
  `docs/ifarm-tunnel.md`. Decks: `.claude/skills/slides`. EICrecon style:
  `submodules/skill-eicrecon/plugins/eicrecon-pr/skills/eicrecon-pr/SKILL.md`.
- How the loop was designed and reviewed: `autoresearch-loops.md`,
  `docs/expert-review-v1.md`; try 1 and what v3 changed: `try1-expert.md`
  (the run's self-review), `try1-assessment.md`.
- Plots are PNG (`scripts/701_pdf_to_png.sh` converts what EIC tools write as PDF).

## Git

No commits, pushes or branch changes unless the user's chat message contains
`please-git`. The uncommitted working tree is the user's review queue.
From Phase 4 on (D-user-34), with `please-git` in the start line, EICrecon
tries are commits on `zdc-autoresearch/phase4` in the submodule, with a revert
commit for every try that is not accepted. The superproject is not committed.
**Pushes are strictly prohibited**: never `git push`, never a PR, in any repository.
