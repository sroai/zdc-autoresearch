# What is missing: the fast inner loop

Written 2026-11-07 by the designer session after reading the Phase 3 run
(`space/STATUS.md`, `space/EXPERIMENTS.md` Phase 3, `space/notes/runlog.md`).
No file of the running session was changed.

## What Phase 3 has produced in eight hours

- Tools: the offline Λ chain (`415`), the headline, preflight, tally, the
  capybara views; references R3 (PR 3063 on the pin) and R1p (the author's
  package); experiments B9d (stable vertex) and B9e (the neutron at its
  leader), each a build plus about an hour of reconstruction.
- The physics result, and it is a real one: PR 3063 lifts the Λ yield from
  0 to 0.171 % per thrown Λ → nπ⁰, and the stable vertex adds 2 events in
  16 000 on top of it (B9d INCONCLUSIVE). The 14 % ceiling of `414` assumed
  perfect separation; on the real 3×3 clusters only about 1 % of Λ events
  have both photons in clusters of their own and tagged, so the whole Λ
  chain, fixed or not, is capped near 0.2 %.
- So the bottleneck is back where Phase 1 found it: 89–97 % of the photon
  pairs are merged into one cluster. Nothing run in two tries attacks that
  directly. The parameter families cannot (closed in Phase 2); the code
  candidates (B11, B8, B7) are next in the run's queue, at a build plus an
  hour of reconstruction plus a verdict each, with questions to the user
  between them.

## Why it does not feel like autoresearch

An autoresearch loop is many cheap iterations against one fixed metric,
with the agent editing one thing and reading one number. Ours is the
opposite: every hypothesis costs a full EICrecon pass (reconstruction of
46 000 gun events plus DIS, 10–60 GB, about an hour), a hypothesis table,
a verdict and often a question or a patch for the user. Two tries, two
days, 18 judged rows, one accepted parameter change. The protocol
(gates, held-out, guards) is right as the outer ruler; it is wrong as the
unit of iteration. The expensive step is spent on hypotheses that a
cheap step could have discarded in seconds.

## The fix: iterate offline on cached hits, confirm in EICrecon

Every clustering experiment starts from the same input: the HEXPLIT
subcell hits of each event (digitization and HEXPLIT do not change) and
their MC contributions. Those are in every kept reconstruction output and
are identical across rows. Cache them once; re-cluster in Python; score
with the same S0 and the offline Λ chain; keep or discard in seconds.

1. **Cache** (`scripts/450_dump_hits.py`, once): for D4 (16 000 events),
   D2 and D3, the subcell hits (x, y, z, layer, energy) and their
   per-particle contributions, from R0's outputs, to npz under
   `{data}/hits/`. Size: of the order of a gigabyte.
2. **The sandbox clusterer** (`zdc/cluster.py`): a Python re-implementation
   of `ImagingTopoCluster` (connected components with the layer range, the
   XY and Z distances, the thresholds) and the CoG energy. **Ruler**: on
   the cached hits it must reproduce R0's clusters per event (same
   members, same energies within float rounding) and P1b's with P1b's
   thresholds; that proof is the sandbox's Step 0, and the sandbox is
   frozen after it.
3. **The scorer** (`scripts/451_score_candidate.py`): truth matching from
   the contributions (the same purity and containment rule as `410`), S0
   per momentum, the offline Λ chain of `415` (vertex-fixed, tagged
   variant with a shape proxy for the tag), the column and low-energy
   diagnostics of G1 to G3 on the D5 hits, the photon and neutron raw sums
   on D2 and D3. One run: seconds to a minute on all of D4.
4. **The loop** (the autoresearch proper): the agent edits one file,
   `zdc/cluster_candidate.py` (a function hits → clusters, any algorithm:
   Island with splitting at local maxima, chain-high-collect-low, an
   EM-core split of a merged shower, two-pass coarse/fine, shape-based
   separation), runs the scorer, appends one line to
   `space/perf/candidates.tsv` (candidate id, hash of the file, the
   metrics, keep/discard), and keeps the best. Hundreds of iterations per
   day; the same paired test on identical events; no question to the user
   inside the loop.
5. **Confirmation** (the existing protocol, unchanged): a candidate that
   beats the current best by the margin on the sandbox is ported to
   EICrecon (a code experiment under loop v3: patch, build, `300`, G4,
   capybara, held-out), judged there, and becomes the current best only
   there. The sandbox predicts; EICrecon decides.

What stays: the setup file, the gates, the references, the held-out
sets, the Λ family rules. What changes: Phase 3's unit of iteration, and
the time to the first clustering that splits a merged pair.

## Risks, stated

- The sandbox could diverge from EICrecon (shape parameters, the CoG's
  weighting, the subcell geometry). The ruler in step 2 catches the
  clustering; the shape-based photon tag is a proxy and the EICrecon
  confirmation catches the rest.
- An algorithm that wins offline may be slow or unclean in C++; the port
  is the cost of a win, paid once per win.
- The tag proxy for the Λ chain: the sandbox can report the tagged and
  the truth-identified variants both, as `415` does.

## What to decide

A) Redirect the Phase 3 session now: stop before B11/B8/B7 as EICrecon
   experiments; build steps 1–3 (about a day, the ruler proof included),
   then run step 4 for the rest of Phase 3; confirm winners with the
   existing loop. Loop v3 gets a "Phase 3b: the fast loop" section, as a
   patch for you to apply.
B) Let the run continue as written (B11, B8, B7 in EICrecon, hours each),
   and build the fast loop beside it.
Recommendation: A. The run has shown that the Λ chain is not where the
yield is; the clustering is, and the clustering needs iteration speed.
