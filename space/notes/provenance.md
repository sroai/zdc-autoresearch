# Provenance index — for the write-up of this autoresearch run

Everything needed to reconstruct how the run went, and where it is. Times in UTC unless marked.
Nothing here is committed by the agent (the user's rule); the working tree is the record until the user commits.

## The program (what the agent was told)
- Loop spec: `zdc-autoresearch-loop-v2.md` (v2 = v1 + the 22 changes of `docs/expert-review-v1.md`); setup/ruler: `zdc-setup.md`;
  common rules: `work-common.md`; problem statement: `docs/zdc-problem.md`; farm skills: `.claude/skills/ifarm-*`.
- Frozen ruler after Phase 0: `space/FROZEN` (copy of `space/FROZEN.after-phase0` plus additions, kept by hand: the hook was not
  live in this session, which was started from `~/dev/meson-structure`).

## The human in the loop (every user decision, verbatim quote + effect)
- `space/notes/DECISIONS.md`: D-user-* (user, chat) and D-default-* (agent defaults the user could override). Phase 0–1:
  D-user-4..17. Questions with options, recommendation and answer: `space/QUESTIONS.md` (Q1, Q4–Q10, checkpoint block).
- Interventions that changed the ruler mid-run: D-user-12 (S3 raw sum one-sided), -13 (S2 after per-clustering refit),
  -16 (photon raw-sum guard), -17 (S2 with 2σ). Scope changes: -14 (LambdaReconstruction opened), -15 (PR 3114 as R2, views
  from the MSF talk and arXiv:2412.12346).

## What was run and what came out
- Experiment ledger (hypothesis written before each run, verdict after, re-judgements as added lines): `space/EXPERIMENTS.md`.
- Scoreboard rows: `space/perf/scoreboard.csv`; per-run metrics `space/perf/metrics-<exp>.json`; truth matching
  `space/perf/truth-<exp>-<dataset>.json`; calibration refits `space/perf/calib-<exp>.json`; shape/decay-z/photon raw sum
  `space/perf/shape-<exp>.json`; S5 `space/perf/msf-<exp>-<dataset>.json`; noise `space/perf/noise-validation.json`;
  dataset hashes `space/perf/manifest-datasets.json`; references `space/perf/references.json`.
- Experiment configs (every parameter of every run): `configs/experiments/*.yaml`; code-tier patches: `space/notes/patches/`;
  builds: `/data/zdc-autoresearch/install/eicrecon-*` (pin e5e2a60c, image eic_xl:26.11.0-stable).
- Reports: `space/reports/phase0_foundation.md`, `phase1_dissection.md`; findings index `space/reports/FINDINGS.md`
  (full entries `phase0_findings.md`, `phase1_findings.md`). Plots: `space/plots/phase{0,1}/...`.
- History: `space/notes/runlog.md`; live state and resume: `space/STATUS.md`; `space/LEDGER.md`.

## Raw run data (not in git)
- Reconstructions: `/data/zdc-autoresearch/reco/<exp>/<dataset>/` with one `<stem>.json` per file (the full eicrecon command
  line and wall time) and `timing.csv` per experiment (seconds per 1000 events).
- Logs: `/data/zdc-autoresearch/logs/` (reco-*, exp-* = 300 runs, shape-*, calib-*, launch-*; 2 GB).
- Launchers used overnight: `/data/zdc-autoresearch/tmp/launch_*.sh`, `g4_guns.sh`.
- Session transcripts (the agent's full conversation incl. tool calls; Claude Code deletes old transcripts after its
  retention period, so they are copied): `/data/zdc-autoresearch/provenance/transcripts-2026-11-05/`
  (`a641ffbe-…jsonl` = this session; `36d9de33-…jsonl` = the same conversation's earlier file; the directories hold subagent
  and tool-result files). Re-copy at the end of each phase.

## Numbers an article will want (where to find them)
- Wall time per stage: runlog above; reco cost T per 1000 events: `zdc-setup.md` Step 0 fills and `timing.csv`.
- What the agent got wrong and corrected (useful for the article): `phase0_foundation.md` "Scripts repaired"; Phase 1 —
  a share quoted as ~70 % that was 50 % (corrected in the P1c entry), hand-computed refit residuals replaced by the script's,
  the "merged" category split into merged/split after the user's plots (split turned out ~0 on every clustering).
