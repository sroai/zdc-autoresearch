# Experiment ledger

Append-only, one entry per experiment, written in two steps: the hypothesis
block BEFORE the run, the verdict block after. Entry shape:
`zdc-autoresearch-loop-v2.md`, section "The experiment loop". Rejected
entries stay; corrections are new entries. The backlog of not-yet-run
hypotheses sits at the bottom, ordered.

## Backlog

(seeded by Phase 1 from the dissection of PR 3064)
