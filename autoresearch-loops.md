# Autoresearch loops in ~/dev — what exists, what worked, what must improve

Survey written on 2026-11-04 for the ZDC program. Sources: every prompt and
protocol file under `~/dev` that drives an autonomous run
(`optim/trk_hit_bkg.md`, `optim/prt_comb_bkg.md`, `optim/ilreco.md`,
`optim/cal-fpga.md`, `evio-optim/evio6-*.md`, `evio-optim/optimize.md`,
`autoresearch-for-you/optimize.md`, `firebird/mega-refactor.md`,
`optim/work-common.md`, `cv-autoresearch/{work-common,optimize}.md` v1 and
v2 with the v2 brief), the two generalization notes (`~/dev/memory_prompt.md`,
`~/dev/thriftness_prompt.md`), the memory-system review
(`optim/memory_system_review.md`), the ai-trk-bkg digest
(`optim/trk_hit_bkg_autoresearch.md`), the memory stores under
`~/.claude/projects/*/memory/`, and a web survey of Anthropic's current
guidance and of public autoresearch loops (Karpathy's `autoresearch`,
its forks, the AI Scientist). The web survey's sources are listed at the end.

## 1. The lineage, in one table

| program (dates) | prompt | what it added to the method | outcome |
|---|---|---|---|
| **ai-trk-bkg** (2026-07-12 to 07-15, ePIC tracker background filter) | `optim/trk_hit_bkg.md`, phase specs written by the user between runs | the skeleton: STATUS.md resume, one-lesson-per-file notes, QUESTIONS.md with three stop conditions, versioned plots per phase, reports; "expectation before search"; token-thrift rules; milestone-first | 99 % eff / 53 % rejection; reco 2.2× faster; an EICrecon PR-shaped diff; 16 lessons, 9 reports, a 41-slide deck in 4 days |
| **ai-comb-lam** (2026-07) | `optim/prt_comb_bkg.md` | slides as a mandated deliverable; subagents for genuinely parallel work | a deck |
| **evio-optim phase I** (2026-08) | `evio-optim/evio6-start.md` | STATUS.md ≤ 40 lines; `DECISIONS.md` as numbered knobs tied to evidence; "How you document" (Google style, no we/just/simply) | the matured template |
| **evio-optim phase II** (2026-08) | `evio6-phase2.md`, later `evio-optim/optimize.md` and the public `autoresearch-for-you` | the **append-only experiment ledger**: hypothesis with expected gain written BEFORE the run, one change, measure, gate, verdict; "if the expected gain cannot be stated, do not run it"; the correctness gate with a stored reference; **prove the gate can fail**; the move-on rule (two < 5 % results on a subsystem → ceiling); one commit per hypothesis on `autoresearch/v{N}_{name}`; K1 to K9 knobs separated from the protocol | 95 MB/s → 3.0 GB/s cold / 4.2 GB/s hot; published as a reproducible task others can rerun |
| **cal-fpga** (2026-07) | `cal-fpga.md` | "missing software → don't attempt a multi-hour source build, write QUESTIONS and stop"; a per-iteration worklog | |
| **ilreco** (2026-08) | `optim/ilreco.md` Part B | the **six-field journal** (HYPOTHESIS / TEST / LOOK / VERDICT / UNDERSTANDING / NEXT), never overwrite, corrections are new entries; a **fixed metric reported every iteration**; statistics budgeted before launch; checkpoints every 5 loops, a stop for user input every 10 | the tail of a calorimeter response explained |
| **firebird** (2026-09) | `firebird/mega-refactor.md` | phase-scoped notes and plots | |
| **work-common.md** (2026-09 to 10-22) | `optim/work-common.md` | everything above consolidated: variables (`{space}`, `{repo}`, `{ledger}`, `{data}`, `{memory}`), program/phase/run/session terms, the **FIX / ASK / PARK / STOP** protocol with a decision table, BLOCKING(!) questions with freezes, the memory canon (one home per fact, LIVE block, same-day promotion of generalizing lessons), the Findings index (F-numbers, status first), the writing and coding rules | the base every later program reads first |
| **memory review** (2026-10-04, applied 10-16) | `optim/memory_system_review.md` | index hooks = identity + pointer + date, no numbers; STATUS.md ≤ 40 lines enforced, `runlog.md` for history; `## LIVE`; feedback sweep at run end; one canonical home per fact | the drift that cost a session (stale hooks, a 700-line STATUS, an orphaned standing rule) fixed |
| **cv-autoresearch v1** (2026-10-20 to 10-31) | `cv-autoresearch/optimize.md` v1 | gates with controls (a damaged copy must fail), paired LLM judges in both orders with a self control, snapshots with hashes, a protective hook on frozen inputs | **failed**: seven rounds each passing its own check summed to a worse page; 76 questions in four days; the user stopped it |
| **cv-autoresearch v2** (2026-11-01) | `cv-autoresearch/{optimize,work-common}.md` v2, the brief | the fifth response **DECIDE** (defaults recorded, vetoable in the round note); only questions the user alone can answer reach the user; whole-draft rounds judged on the whole page; the user sees every round (a review folder); plain language, every number in the setup file; held-out judge once at the end | the rewrite the ZDC program inherits selectively |

Two facts from the digest of the first run (`trk_hit_bkg_autoresearch.md`)
frame everything after it: the method was **phase-gated semi-autonomy**
(the user set each phase's goal between runs and supplied two of the biggest
ideas), and the disciplines that produced the result were *ceiling first*,
*control twins*, *negatives on record*, *decomposition before optimisation*,
and *one fixed metric from day 1 to day 4*.

## 2. What is good (keep)

1. **Phases with a Step 0, a ruler and a done criterion.** Every program that
   finished had them; the one that failed (cv v1) had phases without a
   whole-page ruler. The ZDC program keeps the phase model (the user's
   explicit wish).
2. **The ledger written before the run.** Hypothesis with the expected effect
   and the mechanism, then the verdict with numbers. "If the expected gain
   cannot be stated, do not run it" is the single rule that kept evio-optim
   from aimless sweeps. Karpathy's `program.md` lacks it and his loop is
   described as greedy hill-climbing on a noisy number.
3. **Prove the gate can fail.** evio-optim phase II introduced it; cv v1 made
   it a hard rule ("a gate counts only after its control has failed it").
   The 2026 reward-hacking literature (HackBench, BaitBench: fabricated
   metric files, monkey-patched graders, prompts cutting hacking by six
   points only) says this is the rule that matters most, and that it must
   be enforced by permissions and hooks, not by prompt text.
4. **Compute is cheap, tokens are not.** The thrift block (logs to files,
   loops inside scripts, numbers not images, one well-prepared run) is in
   every prompt and was never regretted.
5. **STATUS.md ≤ 40 lines with a LIVE block, the memory index as pointers.**
   The memory review showed what drift costs and fixed it; the Claude Code
   docs now cap the index at 200 lines / 25 KB, which the convention is well
   under.
6. **The decision table.** FIX / ASK / PARK / STOP with freezes made
   interruption cheap: a run that ends with a written question is a good
   run. Twelve programs ran under it without a silently pursued assumption
   invalidating a phase.
7. **Findings as a deliverable.** Programs that study code they do not own
   (EICrecon here) produce defects as a second product; the F-index with
   status first is readable in one pass.
8. **Numbered scripts and one machine profile.** `1xx` data, `2xx`
   understanding, `3xx` training/experiments, `4xx` evaluation, `5xx`
   export/farm, `7xx` figures; static machine facts in one YAML selected by
   an environment variable, experiment knobs as flags or per-experiment
   configs; a script's logic lives in the script. Human-launchable without
   context (`attention-finder` was clone-and-run for a student).
9. **The reference oracle.** The CLASS cosmology and the C compiler runs at
   Anthropic both rested on a reference implementation as the oracle; here
   the stock EICrecon at a pin plus the official benchmarks and capybara
   play that role.

## 3. What is bad (change)

1. **Questions about the tools reached the user.** cv v1: 76 questions, most
   about thresholds and measuring scripts, several marked blocking; the user
   called it inhumane. The fix exists (v2's DECIDE) and is imported: a doubt
   about a tool, threshold, rule, budget, naming or code is the agent's
   default, recorded, vetoable; only the physics, the scope and frozen items
   are questions.
2. **Accepting on a proxy that is not the goal.** cv v1 accepted rounds on
   keyword coverage; seven passes summed to a worse page. In physics
   software the same trap is a metric that is cheap but not the physics
   (here: a π⁰ two-cluster fraction can rise while Λ efficiency falls;
   PR 3064's own CI story: better π⁰ separation, broken cluster
   distributions). The fix: one primary metric aligned with the physics
   goal (Λ-gun efficiency), guards that must not regress (neutron
   performance, non-ZDC collections byte-identical), and a held-out
   confirmation set (MSF at scale) that never selects.
3. **No noise control.** `program.md` keeps or reverts on a single run;
   ai-trk-bkg repeated only when it felt wrong; evio-optim repeated when the
   delta was under 5 %. None measured the band first. The ZDC loop measures
   the seed-to-seed and rerun spread at Step 0 and treats anything inside it
   as no change.
4. **Program numbers leaked into the protocol.** cv v1's `optimize.md`
   carried "30 minutes, 120 calls"; `trk_hit_bkg.md` carried paths that
   meant three different things on three machines (`/work`). Rule now: every
   number and path in the setup file, the loop and the common rules refer to
   it by section.
5. **Corrections in place.** ai-trk-bkg amended report 05 when a lesson
   overturned it; the trail was lost. ilreco fixed it (append-only, new
   entries). Keep.
6. **One monolithic prompt.** `trk_hit_bkg.md` grew to a ledger-prompt
   hybrid read by stdin; `run_autonomous_claude.md` documents the container
   dance. The three-file split (setup / common rules / loop) plus a one-line
   start command in `CLAUDE.md` is the cv v2 form and is adopted.
7. **The frozen foundation was a convention, not a mechanism**, until
   cv v1's `protect.py` hook. The user's instruction for this program
   ("only ZDC data must change") is exactly a hook: everything outside the
   ZDC-owned files of EICrecon, the datasets, the metric configs and the
   gates is refused by the hook, not by a sentence.
8. **The human saw nothing until the end** (cv v1). ilreco's cadence (report
   every 5 loops, stop for review every 10) plus the benchmark plots the
   reviewers already know are the ZDC loop's "review folder".
9. **Monitors and background jobs lived in chat.** The LIVE block fixed it;
   the farm skills now require the job id in LIVE the moment a job starts.

## 4. What current guidance adds (2026-11)

From the web survey (sources at the end):

- **Claude Code memory**: `MEMORY.md` index loaded up to 200 lines / 25 KB,
  topic files on demand, four types (`user`, `feedback`, `project`,
  `reference`), skip what the code or CLAUDE.md already says; CLAUDE.md
  under 200 lines, procedures into skills; `.claude/rules/*.md` with
  `paths:` for path-scoped rules; "to block an action regardless of what
  Claude decides, use a PreToolUse hook". All already matched by the
  convention; the cap is now stated in `work-common.md`.
- **Skills**: `SKILL.md` under 500 lines, description first 1,536
  characters count, progressive disclosure. The three skills here are 150
  to 570 lines (the slides skill is the long one; it is a copy, kept whole).
- **Long-running agents** (Anthropic, 2025-11 to 2026-03): an initializer
  session, a feature list the agent may only tick, a progress file, a
  smoke test at session start, one unit of work per session, "the task
  verifier is nearly perfect, otherwise Claude will solve the wrong
  problem", keep tool output short with one greppable ERROR line, test over
  a grid rather than one fiducial point, a skeptical standalone evaluator
  rather than self-evaluation, re-tune the harness per model. The ZDC loop
  maps these to Phase 0 (initializer), the scoreboard (verifier), the
  every-run check (smoke test), the eight momenta of the guns (the grid),
  and the independent expert review of the loop itself.
- **Karpathy's autoresearch** (2026-03): one editable file, a read-only
  evaluator, a fixed 5-minute budget, git keep/revert, an untracked
  `results.tsv`, `program.md` edited only by the human; about 700 tries,
  about 20 kept, 11 % gain. Right: the editable surface is tiny and the
  evaluator untouchable. Wrong for physics: no noise control, the
  validation set is the selection set, "never stop, never ask". The forks
  (pi-autoresearch) add a checks script that blocks a keep and multiple
  metrics; Shopify's 53 % Liquid speedup was flagged as overfit and never
  merged — the held-out lesson.
- **Reward hacking** (2026): agents fabricate metric files, patch graders,
  train on held-out data; telling them not to cuts it by six points.
  Enforce with hooks and read-only inputs.
- **AI Scientist** (Nature, 2026-03): full idea-to-paper loops; failure
  modes are naive ideas, weak rigor, unfair baselines, self-edited
  timeouts. Not the model here: the ZDC loop has a human-set goal and a
  physics oracle.

## 5. What the ZDC loop does differently

| concern | ZDC loop |
|---|---|
| editable surface | the ZDC-owned files of EICrecon and per-experiment parameter configs; everything else frozen by the hook |
| evaluator | the scoreboard script + capybara + the benchmarks' own plot scripts, frozen after Phase 0, proven to fail on damaged copies, re-proven at every run start |
| two tiers | parameter experiments via `-P` overrides on the pinned build (minutes, no rebuild); code experiments as patches with a rebuild |
| primary metric | Λ-gun efficiency S4a (the physics goal, cheap enough per experiment); S1 π⁰ separation is a diagnostic, never the verdict |
| guards | neutron gun S3 in band; non-ZDC collections byte-identical (G4, the gate); the three review findings as numbers G1 to G3, each inside its band or explained by a mechanism |
| noise | seed twins and reruns at Step 0; a change inside the band is not a change; one repeat allowed within 1.5 bands |
| held-out | MSF at scale (D6b) on the farm, confirmation only, never selection |
| human cadence | report every 5 experiments, stop for review every 10; the benchmark plots the reviewers know; questions only about physics, scope, frozen items |
| record | phase ledger + experiment ledger (two-step entries) + decisions with `D-user`/`D-default` + findings index + runlog; scoreboard.csv as the one table slides and the PR draft load |
| farm | two skills with every quirk hit since 2026-07; logs in `/farm_out`, `%16`, 2 GB/CPU, `--gres=disk`, no `/tmp`, atomic deliverables |
| resumability | STATUS ≤ 40 lines with LIVE and RESUME; everything on disk; the hook and the manifests make a mid-run death cost nothing |

## 6. What must still improve (open)

1. The acceptance rule has a human-sized hole: "G1 to G3 explained by a
   mechanism" is judged by the agent. The expert review (`docs/expert-review-v1.md`)
   is asked to tighten it; version 2 records the answer.
2. The parameter tier does not cover the two XY neighbour distances
   (`ImagingTopoCluster_factory.h` comments their `ParameterRef` out). Phase 0
   adds them as parameters under the byte-identical guard; if that proves
   unsound, distances become code-tier experiments.
3. Whether 26.06-simulated MSF files reconstruct correctly in the 26.11
   image is unknown until Step 0 item 6 runs. The loop has a fallback (the
   Λ gun) and a question.
4. The autonomous container (`eicdev/eic-claude`) carries an EICrecon
   dependency stack that is not the official one; this program runs the
   agent on the host and every EIC command inside the official `eic_xl`
   image through a wrapper. Whether the host agent in auto mode plus a
   docker wrapper is as robust as the container runs of 2026-07 to 10 is the
   first thing Phase 0 shows.
5. A standalone skeptical evaluator (a subagent that reads the ledger entry
   and the plots and argues against the verdict) is cheap and is not in
   version 1; the review decides whether version 2 adds it at the
   checkpoint.

## Web survey sources

- Claude Code memory: https://code.claude.com/docs/en/memory ; skills:
  https://code.claude.com/docs/en/skills ; hooks: https://code.claude.com/docs/en/hooks-guide
- Memory tool and context editing: https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool ,
  https://platform.claude.com/docs/en/build-with-claude/context-editing
- Effective context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Effective harnesses for long-running agents: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Building a C compiler with parallel Claudes: https://www.anthropic.com/engineering/building-c-compiler
- Long-running Claude for scientific computing: https://www.anthropic.com/research/long-running-claude
- Harness design for long-running apps: https://www.anthropic.com/research/harness-design-long-running-apps
- Karpathy autoresearch: https://github.com/karpathy/autoresearch (program.md), nanochat README; secondary: https://blog.agihouse.org/posts/autoresearch-research-brief , https://cameronwestland.com/autoresearch-is-reward-function-design/ , https://www.webfuse.com/autoresearch
- Reward hacking: https://facebookresearch.github.io/RAM/blogs/hackbench/ , https://arxiv.org/pdf/2608.30724
- AI Scientist: https://sakana.ai/ai-scientist-nature/ , https://www.nature.com/articles/s41586-026-10265-5
