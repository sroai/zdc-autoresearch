# zdc-autoresearch

Autonomous optimization of the ePIC ZDC reconstruction in EICrecon, run as
a phase-gated autoresearch loop. The physics: `Λ → n π⁰ → n γ γ` in the
Meson Structure Function program; the trigger: EICrecon issue #2737 and
PR #3064 (`docs/zdc-problem.md`).

## Start line

One chat line starts a run: `Read zdc-setup.md, work-common.md and
zdc-autoresearch-loop-v2.md. Run.` Add `online` if you will answer in chat
during the run; add `please-git` if commits are allowed this run.

## Three hard rules

1. **Only the ZDC changes.** After Phase 0 the hook `.claude/hooks/protect.py`
   refuses writes to everything `space/FROZEN` lists: every submodule except
   the ZDC-owned files of EICrecon, the dataset and metric configs, the
   gates, the manifests. A needed change there is a question in
   `space/QUESTIONS.md`, never an edit.
2. **The ruler is proven before it is trusted.** Every gate has been seen to
   fail on a damaged copy; every parameter switch has been seen to change an
   output; the reference R0 reproduces at every run start. A check that has
   only ever printed PASS proves nothing.
3. **One fixed scoreboard, one selector, held-out confirmation.** Every
   experiment reports the whole scoreboard row (`zdc-setup.md`, Scoreboard).
   S0, the truth-matched separation efficiency on the Λ gun, decides, by a
   paired test on identical events. S2 photon scale, S3 raw neutron energy,
   S4b, S4c and G1 to G3 (within the limits the user set) guard; G4
   (non-ZDC collections identical) gates. D1h and D4h (fresh seeds) are
   checked at checkpoints and revert an overfit; D6b (MSF at scale)
   confirms and never selects. S4a, the Λ efficiency, is reported against
   its truth-cluster ceiling and never selects: `LambdaReconstruction` and
   its windows are frozen while the clustering is tuned.

## Where to look

- Where to resume: `space/STATUS.md`. Questions for the user: `space/QUESTIONS.md`.
- The phase ledger: `space/LEDGER.md`. The experiment ledger: `space/EXPERIMENTS.md`.
- Every command: `scripts/` (numbered: 1xx foundation, 2xx understanding,
  3xx experiments, 4xx evaluation, 5xx farm, 7xx figures); `README.md`.
- Farm: `.claude/skills/ifarm-tunnel`, `.claude/skills/ifarm-slurm`,
  `docs/ifarm-tunnel.md`. Decks: `.claude/skills/slides`. EICrecon style:
  `submodules/skill-eicrecon/plugins/eicrecon-pr/skills/eicrecon-pr/SKILL.md`.
- How the loop was designed and reviewed: `autoresearch-loops.md`,
  `docs/expert-review-v1.md`.

## Git

No commits, pushes or branch changes unless the user's chat message contains
`please-git`. The uncommitted working tree is the user's review queue.
