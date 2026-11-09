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
| selector | S0, the truth-matched separation efficiency on the Λ gun (per true photon and neutron: best cluster purity ≥ 0.8, containment ≥ 0.5), judged by a paired test on identical events; the Λ efficiency S4a is reported against a truth-cluster ceiling and never selects, because `LambdaReconstruction`'s own π⁰ window caps it and its parameters could game it |
| guards | photon energy scale (S2), the neutron's raw cluster-energy sum and cluster count (S3), Λ width (S4b), γ-tagged neutrals per event (S4c), and the three review findings as numbers (G1 to G3, with the single-column diagnostic) inside limits the user set at the Phase 0 checkpoint; non-ZDC collections identical (G4, the gate) |
| noise | determinism check; McNemar on discordant events and an event bootstrap, validated on three independent seeds at Step 0; held-out seed sets D1h and D4h reconstructed only at checkpoints, reverting an accepted change that does not reproduce there |
| held-out | D1h, D4h at checkpoints; MSF at scale (D6b) on the farm, confirmation only, never selection |
| human cadence | report every 5 experiments, stop for review every 10; the benchmark plots the reviewers know; questions only about physics, scope, frozen items |
| record | phase ledger + experiment ledger (two-step entries) + decisions with `D-user`/`D-default` + findings index + runlog; scoreboard.csv as the one table slides and the PR draft load |
| farm | two skills with every quirk hit since 2026-07; logs in `/farm_out`, `%16`, 2 GB/CPU, `--gres=disk`, no `/tmp`, atomic deliverables |
| resumability | STATUS ≤ 40 lines with LIVE and RESUME; everything on disk; the hook and the manifests make a mid-run death cost nothing |

## 6. What the expert review changed (v1 → v2)

An independent reviewer read v1, the EICrecon sources at the pin and the
benchmarks (`docs/expert-review-v1.md`, 22 ranked changes with file and
line). The verdict on v1: it would converge on a number, not on a
reconstruction the reviewers merge. What changed:

1. **The selector.** v1 selected on the Λ-gun efficiency. The review showed
   it is capped by `LambdaReconstruction` itself (photon momenta point from
   the IP, the π⁰ pair is cut at ±10 % before any vertex fit, so only decays
   within about 3.6 m pass; near zero at 100 GeV by the gun's acceptance) and
   gameable through parameters the loop owned (the π⁰ and Λ windows, a
   calibration refit that inflates photons, fragment combinatorics). v2
   selects on truth-matched cluster separation, freezes the Λ code and its
   windows, guards the photon scale and the neutron's raw energy, and
   reports the Λ efficiency against a truth-cluster ceiling.
2. **The mechanism, written down first.** HEXPLIT S2 puts every subcell on a
   24.4 mm grid; the PR's 14.6 mm neighbour distance is below it, so every
   cluster becomes a single subcell column: intrinsic φ exactly ±180°,
   showers shattered into shards (the three review findings). v2's Phase 1 is
   a confirmation of that one hypothesis with a single-column diagnostic,
   not an eight-way dissection; the distance scan is three discrete settings.
3. **Guards judged by the user's limits**, set at a Phase 0 checkpoint, not
   by the agent's "explained by a mechanism". Six checkpoint questions with
   defaults replace the late Phase 1 question.
4. **Noise.** The single-pair band is gone: a determinism check, a paired
   test on identical events validated on three seeds, and held-out seed sets
   at checkpoints that revert an overfit.
5. **Datasets.** Guns on the geometry with the LYSO ECal in front of the
   HCal (every physics sample has it; the ZDC-only benchmark config does
   not); π⁰ momenta at the Λ-daughter energies (20 to 70 GeV) as well as the
   benchmark's; a neutron scan instead of the benchmark's single 100 GeV
   point; D5 sized in ZDC clusters, not events.
6. **Tooling facts.** R1 is the PR's three-file diff on the pin (the PR's
   base is 14 commits behind); `podio:output_collections` entries are
   regexes; gate runs are single-threaded; the benchmark plot scripts use
   stale collection names and exit quietly, so patched copies live under
   `scripts/700_benchmarks/`; four findings about upstream code are
   pre-registered for Phase 0 to verify.

## 7. What must still improve (open)

1. Whether 26.06-simulated MSF files reconstruct correctly in the 26.11
   image is unknown until Step 0 item 6 runs (hit-level comparison). The
   loop has a fallback (the Λ gun) and a question.
2. The autonomous container (`eicdev/eic-claude`) carries an EICrecon
   dependency stack that is not the official one; this program runs the
   agent on the host and every EIC command inside the official `eic_xl`
   image through a wrapper. Whether the host agent in auto mode plus a
   docker wrapper is as robust as the container runs of 2026-07 to 10 is the
   first thing Phase 0 shows.
3. A standalone skeptical evaluator (a subagent that reads a ledger entry
   and the numbers and argues against the verdict before it is accepted) is
   cheap and still not in v2; it is the one review suggestion left for the
   first checkpoint to decide on.
4. Every script was written without being executed; Phase 0 is where the
   contracts in the loop file meet the real files.

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

## 8. What try 1 changed (v2 → v3, 2026-11-06)

Try 1 (2026-11-04/05, 22.5 h, 141 CPU-h, 12 judged experiments, one
accepted) is reviewed in `try1-expert.md` (the run agent's self-review)
and `try1-assessment.md` (the designer's assessment; verdict: modify and
continue as try 2 under loop v3, not a restart). The loop worked as an
instrument (pre-registration, paired test, held-out, guards) and aimed at
the wrong family: it measured the cap of the deliverable in Phase 0 and
ran two phases inside it. v3 adds: a re-rank rule when a ceiling is
measured; the Λ family judged on the Λ yield and an offline Λ chain that
ties every clustering row to a yield; the cost per experiment cut by
restricting output collections; preflight and integrity checks in the
launcher; predictions and headline numbers as script output; PNG plots;
the G4 evidence published (gate table, capybara views). Protocol
revisions between runs are patches the user applies, since the hook
freezes the protocol files and the harness refuses the agent's edit of
the freeze list.

