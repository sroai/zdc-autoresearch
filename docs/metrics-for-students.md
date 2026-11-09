# The metrics of the ZDC autoresearch loop, explained for a student

What each number measures, how it is computed, why it was chosen, and what was
missing. Written after run 1 (2026-11-04/05). The values quoted are run 1's;
the definitions are in `zdc-setup.md` (section Scoreboard) and
`configs/metrics.yaml`, the numbers in `space/perf/*.json` and
`space/EXPERIMENTS.md`.

## 1. The problem in one paragraph

A Λ produced at the collision point flies along the proton beam and decays,
on average after 7–19 m (100–275 GeV), into a neutron and a π⁰; the π⁰ decays
at once into two photons. All three are neutral and continue straight to the
Zero Degree Calorimeter (ZDC), 35.8 m from the collision. The ZDC is a block
of absorber and scintillator tiles (4.9 cm square, read out as 2.4 cm
subcells) that records, layer by layer, where energy was deposited. The
reconstruction software must group the hit subcells into **clusters**, ideally
one per particle, then pair the two photon clusters into a π⁰ and the π⁰
with the neutron into a Λ. After the ZDC's tiles were changed in 2026 the
three showers started to chain into one cluster, and the Λ reconstruction
efficiency of the physics analysis fell from about 4.5 % to about 0. The
loop's task is a clustering configuration that keeps the neutron and the two
photons in clusters of their own without breaking the neutron measurement.

## 2. How the numbers are measured

**Particle guns.** Most metrics are measured on simulated samples in which a
known particle is shot at the ZDC: a lone photon (D2), a lone neutron (D3), a
lone π⁰ (D1), or a Λ that decays to nπ⁰ (D4). Each sample has 1000–2000
events per momentum. The Λ sample keeps only decays whose three daughters hit
the ZDC within 4 mrad of the beam; this **acceptance** is 1.6 % of thrown Λ
at 100 GeV and 33 % at 275 GeV, so every Λ-sample number is "per accepted
event" unless it says "per thrown Λ".

**Truth matching.** The simulation records which particle deposited each
hit. For every true particle we can therefore find the cluster that holds
most of its energy and ask two questions:

- **purity** — what fraction of that cluster's energy came from this
  particle? (1.0 = the cluster is only this particle.)
- **containment** — what fraction of this particle's clustered energy sits
  in that one cluster? (1.0 = the particle was not split across clusters.)

A particle is **separated** when purity ≥ 0.8 and containment ≥ 0.5. Real
data has no truth record; truth matching is a simulation-only ruler.

**Physics events.** Two samples have no gun: deep-inelastic scattering events
(D5, the same files EICrecon's continuous integration uses) and the Meson
Structure Function Λ sample (D6a, the campaign files the physics analysis
runs on). They show what a setting does to ordinary events.

**Identical events.** Every setting reconstructs the same simulated events.
That is what makes the comparison sensitive (section 5).

| sample | what is shot | used for |
|---|---|---|
| D1 | π⁰ → γγ, 50–160 GeV, 7 momenta | S1 |
| D2 | photon, 20–275 GeV, 8 energies | S2 |
| D3 | neutron, 20–275 GeV, 6 energies | S3 |
| D4 | Λ → nπ⁰, 100–275 GeV, 8 momenta | S0, S4 |
| D1h, D4h | the same with fresh random seeds | held-out checks only |
| D5 | deep-inelastic events | G1–G3 |
| D6a | MSF Λ physics events | S5 |
| every sample | — | G4, T |

## 3. The metrics, one by one

Each metric has a **role**: the *selector* decides whether an experiment is
accepted; a *guard* can reject it; an *outcome* is reported beside it but
never decides; the *gate* rejects without appeal; a *diagnostic* explains.

### S0 — separation efficiency (selector)

*Question:* is each of the three particles of a Λ → nπ⁰ event in a cluster of
its own?

*How:* on the Λ sample, per momentum, the fraction of photons that are
separated (**S0γ**, two per event), of neutrons (**S0n**), and of events in
which all three are separated (**S0all**).

*Run 1 values (S0all):* stock 0.006–0.023; PR 3064 0.008–0.022; the accepted
setting P1b 0.018–0.075; the best rejected setting 0.030–0.091. Photons:
stock 0.04–0.07, PR 3064 0.33–0.40, P1b 0.05–0.15. Neutron: stock and P1b
0.64–0.70, PR 3064 0.03–0.07.

*Why this is the selector:* it measures exactly what the clusterer controls;
it counts events, so settings can be compared event by event; and it uses
truth, so "two clusters" cannot be one photon split in two.

### S1 — the lone π⁰ (diagnostic)

- **S1a** — are the two photons of a lone π⁰ in two clusters? The simplest
  separation case, with no neutron shower in the way. Run 1: stock 0.74 at
  50 GeV falling to 0.005 at 100 GeV; PR 3064 0.74 → 0.62; P1b 0.82 → 0.026.
- **S1b** — do the two clusters give the π⁰ mass back (peak and width)?
- **S1c** — is the π⁰ energy right (scale and resolution)? Not filled in run 1.
- **S1d** — how precisely is a photon's impact point measured (mm)?

### S2 — the lone photon (guard on the energy scale)

*Question:* is a photon's energy measured right, how wide is the spread, and
is the cluster recognised as a photon?

*How:* on the photon sample, the best-matched cluster's calibrated energy
divided by the true energy: the median is the **scale**, the width the
**resolution**; the **γ-tag efficiency** is the fraction of those clusters
the neutrals code labels as photons.

*Guard:* the scale must be within 5 % of 1 after the calibration is refit
for the setting (every clustering changes how much energy a cluster
collects, so the stock calibration cannot be reused — finding F6).

*Run 1:* with the stock calibration photons read 13–31 % low on every
setting; after a refit every setting is within 5 %. γ-tag: stock 0.03
(finding F8: the shape cuts reject every ZDC photon), PR 3114's cuts
0.87–0.98.

### S3 — the lone neutron (guard on the neutron measurement)

*Question:* how much of the neutron's energy ends up in clusters, in how many
clusters, and is it ever mistaken for a photon?

*How:* on the neutron sample, the **raw sum** = total cluster energy before
any calibration, divided by the true energy (so a calibration change cannot
hide a lost shower); **clusters per neutron**; the **mistag rate** = fraction
of best clusters labelled photon.

*Guard:* the raw sum must not drop by more than 5 % against the current
best (one-sided: more energy in clusters is fine); clusters per neutron
must not rise by more than 0.5; the mistag is reported.

*Run 1:* stock raw sum 0.50 (20 GeV) to 0.76 (275 GeV); PR 3064 0.24–0.38
(the shower is cut into columns and most pieces are discarded); E02's
chaining threshold cost 13 % at 20 GeV and E04, half the step, 7.6 %; both
were rejected on this guard, which closed the chaining-threshold family.

### S4 — the Λ outcome (reported, never the selector)

- **S4a** — in what fraction of Λ events does the code output a Λ built from
  the right three clusters (each daughter cluster has purity ≥ 0.8 for the
  true n, γ, γ) with a mass inside a fixed ±0.03 GeV window? Beside it, the
  fraction with any Λ at all. Run 1: 0 for stock and for every setting that
  keeps the stock neighbour distance; PR 3064 0.002–0.031; P1b with PR
  3114's photon cuts 0–0.004.
- **S4b** — how sharp is the Λ mass peak? (guard; needs ≥ 50 Λ, so it was
  never computable in run 1.)
- **S4c** — how many photon-labelled objects per Λ event? (guard: fragments
  make fake pairs.)

*Why never the selector:* it is 0 for most settings, and a zero cannot rank
candidates; and it depends on the pairing code downstream of the clustering
(section 4).

### S5 — Λ candidates in physics events (the goal; confirmation only)

*Question:* how many Λ candidates per 1000 real-looking events, and how many
of the true Λ are found?

*Run 1 (9x275 MSF sample, 5000 events, 23 true Λ in acceptance):* stock 0;
PR 3064 21 candidates per 1000, 1 of 23 true Λ found; PR 3114's cuts on stock
1.0 per 1000, 0 of 23. With 23 true Λ this number cannot rank anything; it
needs the farm-scale sample (100 000 events per energy) planned for Phase 4.

### G1, G2, G3 — shower shapes on physics events (guards)

The reviewers of PR 3064 saw three defects on deep-inelastic events:
clusters collapsed to a single column of subcells, a spike in a shape
angle, and the high-energy clusters gone. The guards make those measurable:

- **G1** — fraction of clusters that are one (x, y) column; fraction with
  an intrinsic angle within 5° of ±180°. Limits 0.05 and 0.15.
- **G2** — fraction of cluster energy above 50 GeV; must not drop more than
  50 %.
- **G3** — low-energy clusters per event ("debris"); limit 0.5.

*Run 1:* PR 3064 and the distance-only setting fail G1 and G2 (every cluster
a column); E03's lower cluster floor failed G3 (0.97 debris clusters per
event).

### G4 — nothing outside the ZDC changed (gate)

Every collection that is not ZDC-owned is compared to the reference file by
file, event by event. A ZDC change that touched anything else is rejected
without appeal. Every run-1 experiment passed.

### T — speed (report line)

Reconstruction seconds per 1000 events. A 2× slowdown is a question for the
user, not a rejection.

## 4. Why these metrics

**One decides.** A selector has to be *sensitive* (a small real change must
be resolvable), *on target* (it must measure the thing being changed) and
*hard to game* (there must be no way to raise it without better physics).
S0all is all three: event-by-event comparison resolves +0.01 with 2000
events; separation is what the clusterer controls; truth matching closes the
"split one photon in two" loophole.

**Several protect.** Every guard is something the current reconstruction
does well that a photon-friendly setting could silently break: the
neutron's energy (S3), the photon energy scale (S2), shower shapes on real
events (G1–G3), everything else in the event (G4). The limits were set by
the user before the loop ran; a loop that sets its own limits can always
pass.

**The rest report.** S4a and S5 are the goal and cannot decide: they are 0
for most settings, and the Λ finder's own steps (its π⁰ mass window assumes
the photons point back to the collision; finding F4) cap them at 0–7 % of
accepted events whatever the clustering does. They are shown beside every
experiment so that the proxy's bet — better separation gives more Λ — stays
visible.

**A proxy is a bet.** It has to be checked with a number tied to the goal.
Run 1 did not have one until its last hours (section 7).

## 5. How a verdict is reached

1. The hypothesis is written and timestamped before the run: which cells
   move, by how much, and what would refute it.
2. The setting reconstructs the same events as the current best.
3. **Paired test.** For S0all, count the events the new setting separates
   and the current best does not (*gained*) and the reverse (*lost*). The
   change is (gained − lost)/N and its significance z = (gained − lost) /
   √(gained + lost). The line is 3σ. This is far more sensitive than
   comparing two averages, because events that behave the same under both
   settings add no noise. Example: P1b against stock at 125 GeV gained 116,
   lost 0, z = 10.8.
4. Every guard is checked against its limit; the gate runs.
5. Verdict: ACCEPTED (selector up significantly, every guard in), REJECTED
   (a guard or the gate out, or the selector down), INCONCLUSIVE (nothing
   significant).
6. An accepted setting becomes the current best only after its gain
   reproduces on the held-out samples (D1h, D4h: fresh seeds, never used
   to choose).

**Noise floor.** Before 3σ was used, 26 metric tests were repeated over
three independent seeds to check that the quoted errors are honest.

## 6. The headline units: per thrown Λ

Every Λ-sample number is conditional on the acceptance (1.6–33 %). The
headline the user asked for folds it in: *per thrown Λ → nπ⁰* = (fraction
per accepted event) × acceptance, averaged over the eight momenta. Run 1:

| quantity, mean over 100–275 GeV | per thrown Λ → nπ⁰ |
|---|---|
| all three separated, stock | 0.29 % |
| all three separated, PR 3064 | 0.19 % |
| all three separated, P1b (accepted) | 0.62 % |
| Λ reconstructed, stock and P1b | 0 |
| Λ reconstructed, PR 3064 | 0.40 % |
| ceiling: pairing as coded, perfect clusters | 0.9 % |
| ceiling: vertex-aware pairing, perfect clusters | 14.1 % |
| ceiling of everything: the acceptance | 16.9 % |

The same quantities at 275 GeV alone, the headline momentum of the brief
reports: separation (P1b) 0.59 %, Λ reconstructed 0.00 %, Λ ceiling with the
vertex-aware pairing 27.8 %, acceptance 32.6 %.

Of the 17 points available, run 1's clustering changes moved 0.3; the
pairing code holds 13.

## 7. What was missing

| missing | what it would have told us | status after run 1 |
|---|---|---|
| a ceiling for separation: give each subcell to the particle that put most energy in it, score with the same rule | how far each setting is from the best any clustering could do | never computed |
| a Λ number that moves while S4a is 0: the vertex-aware pairing run offline on each setting's real clusters | whether a separation gain changes the Λ yield at all | computed once, at the end, for perfect clusters only |
| who merges with whom: photon with photon, or photon with neutron | which code change would help (splitting showers, or a shorter reach) | the decay-position view says "merged", not with what |
| separation by decay position, as a number | where the loss is geometry and where it is the clusterer | a plot per setting, no scoreboard cell |
| per-thrown-Λ units | numbers comparable across momenta and with the physics analysis | added mid-run, on the user's request |
| a prediction hit rate per checkpoint | whether the loop understands the detector or only screens it | computed for the retrospective: 45 cells right, 20 wrong (Phase 1 17/12, Phase 2 28/8) |
| cost per experiment: CPU-hours, gigabytes, wall time | the budget spent per answer | T per 1000 events only; the disk filled |
| enough Λ for S5 and S4b | 23 true Λ in 5000 events cannot rank anything | farm-scale sample planned |
| a one-line report per experiment | a result readable without the ledger | added mid-run, on the user's request |

The first two rows are the gap that let the loop optimise a proxy for a
day. Both are afternoon-sized scripts over reconstructions that already
exist.

## 8. Where the numbers live

- `space/perf/scoreboard.csv` — one row per reconstruction, every metric.
- `space/perf/truth-<experiment>-<sample>.json` — S0, S1a, S4a per momentum,
  with per-event flags for the paired test.
- `space/perf/metrics-<experiment>.json` — S2, S3, G1–G3, T.
- `space/perf/calib-<experiment>.json` — the refit calibration and S2 after it.
- `space/perf/shape-<experiment>.json`, `space/plots/<phase>/<experiment>/shape_decayz/`
  — the decay-position and cluster-shape views.
- `space/perf/msf-<experiment>-<sample>.json` — S5.
- `space/perf/lambda-gun-acceptance.json`, `lambda-ceiling-variants-P1b_R0_thr.json`
  — the acceptance and the Λ ceilings.
- `space/EXPERIMENTS.md` — hypothesis, numbers, guards and verdict of every
  experiment; `space/notes/DECISIONS.md` — every limit and ruler change, with
  the user's words.
