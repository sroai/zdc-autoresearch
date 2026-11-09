# ZDC autoresearch loop — assessment on 2026-11-06 (try 2, mid-run)

Written 2026-11-07T02:40Z by the session that scaffolded `dis-autoresearch`,
from the record under `space/`, `try1-expert.md`, `try1-assessment.md` and
the three loop versions, while B9e was running. Nothing was re-run and
nothing under `space/` was touched. The loops v1–v3 and this note come from
the same model family; read the verdict with that in mind.

## Verdict

The loop is overcomplicated, and the complication has one cause: an
optimization harness (a frozen evaluator, a small editable surface,
hill-climbing on a selector) was applied to a question that was still open
research — what caps Λ → nπ⁰ reconstruction in the square-tile ZDC. The
right metric was not known at the start, so the metric changed three times
during the run (S0 → S4a_tm → S4o vertex-fixed), and because the metric
files were frozen by a hook, every change became a question to the user
instead of a decision by the agent.

## Evidence

**Instrument weight.** Five protocol files, about 20 000 words
(`zdc-setup.md` 3 900, `work-common.md` 6 500, loop v2 4 900, loop v3
3 400); three loop versions in three days; 39 scripts, 5 400 lines; a
scoreboard with 16 metric families (S0–S5, G1–G4, T, H) and tagged / truth /
vertex-fixed / refit variants of several; a FROZEN list of about 40 entries
enforced by a hook that also freezes the protocol files, so a protocol
revision is a patch the user applies by hand (Q13, the q14-q15 patch).

**Questions.** 17 in three days (`space/QUESTIONS.md`). Twelve are about
the instrument: guard limits (Q4, Q7, Q8, Q10, Q11), metric definitions
(Q9, Q14, Q15), the selector (Q16), the baseline (Q12, Q17) and the
protocol patch (Q13). Four were BLOCKING. The DECIDE rule exists so that
tool questions never reach the user; the freeze turned every tool doubt
back into a user question. Q17 asks what a measured number means (is B9d's
gain its own or PR 3063's). By Q17 the record holds 31 user decisions and
about 40 agent defaults.

**Outcome.** After Phases 0–2 (22.5 h wall, 141 CPU-h, 865 GB peak disk,
12 judged experiments, 1 accepted), the deliverable — Λ → nπ⁰ per thrown Λ
— is 0.00 % for the current best (`space/perf/headline.csv`). The accepted
change moved a proxy (S0all 0.017 → 0.048). The cap (F4) was measured at
the end of Phase 0 and two phases ran inside it. Try 2's first verdict
(B9d) is INCONCLUSIVE: its +164 events are PR 3063's +162 (R3). The only Λ
gain on the board comes from upstream.

**Design cause.** The v1 → v2 expert review demoted the deliverable (S4a)
to "reported, never selected" and froze the Λ code; the run undid both
(D-user-14; Q16 → A) once the data showed that the selector and the
deliverable rank clusterings in opposite order. A proxy selector plus a
frozen deliverable is the root; the protocol mass is the symptom.

## What is good and worth keeping

Phase 0's ruler (determinism, a measured noise floor, gates seen to fail on
damaged copies); the dissection of PR 3064 (`space/reports/phase1_dissection.md`,
usable as a review today); findings F4 and F9 and the stable-vertex pairing;
the offline Λ chain (`415`) that scores a row in minutes without
reconstruction; and the fact that no false gain was accepted. The three
review-comment drafts (`space/reports/review-comments.md`) are the
program's most useful unposted output.

## Recommendation

After B9e's verdict, collapse to one loop file of two pages:

- One selector: Λ → nπ⁰ per thrown (Λ gun D4, confirmed on MSF events D6a).
- One gate: non-ZDC collections identical, checked once per build on one
  file, never per experiment.
- Two guards: neutron raw energy (D3, ≥ 50 GeV) and photon scale (D2).
  Everything else is printed as a diagnostic and never judged.
- Datasets per experiment: D4, D3, D6a. D2 at checkpoints. D1 and D5 only
  for the final PR validation.
- No protocol hook. Frozen by statement: the input manifests and the
  reference rows. The agent may change scoring scripts and must then
  re-score every row in the same step (minutes from the npz tables).
- Backlog ranked by expected gain on the selector, which puts B8 (Island
  split) and B11 ahead of any parameter run.
- Post the three review comments now.
- Time-box: one run of at most five experiments, then stop or hand the
  clustering to upstream.

Alternative: finish Phase 3 as loop v3 writes it. It will produce more
reference rows and more selector questions before it produces a Λ.

One consideration from the dis loop: if the Λ four-vector (hence t and
x_L) can be regressed from the far-forward hit image without resolving
three showers, the ZDC clustering leaves the critical path of the AI
analysis and serves the conventional mass-peak analysis only. That lowers
this loop's priority; it does not remove the need for the review comments.
