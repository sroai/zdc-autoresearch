# ZDC autoresearch loop — version 7: the changes as EICrecon pull requests

Read `zdc-setup.md` and `work-common.md` first; they define the names, paths, the start protocol, the ledger and the
reporting habits. `zdc-autoresearch-loop-v6.md` and `-v5.md` define the ruler of the last two phases (the MSF score `210`,
the selector `463`, fair play `460` / `465` / `468`, `476` for −t); this file reuses it to prove that nothing was lost, and
replaces the yield fight with the upstream work.

Prepared at the user's order (2026-11-09, chat, D-user-45): *"Stop the phase. Prepare the new phase. Step by step putting
changes back to EICrecon PRs checking other calorimetry is not affected via benchmarks and capibara."* The phase starts on
the user's start line, not before.

## Phase 7 — upstream, one pull-request unit at a time

**Goal:** turn the EICrecon changes of Phases 4–6 (the Phase 6 working tree, final row Z8) into a short series of
pull-request units for eic/EICrecon. Each unit is proven on four counts before the next one starts:

1. **It is the program's code.** The units, applied in order to the base, rebuild the Phase 6 tree; the code cleanup a
   review needs changes no output (the full series reproduces Z8 Λ by Λ).
2. **Other calorimetry is not affected.** Every collection the unit does not declare stays byte-identical to the previous
   unit on the DIS guard samples and the guns (`130`'s leaf compare), and the capybara view of the undeclared collections
   prints no leaf (`443`'s method). This is G4 of Phase 3, per unit.
3. **What it does change is shown on the detector benchmarks** the reviewers know: the declared collections before and
   after, with the benchmarks' own numbers.
4. **It reads like an EICrecon pull request**: the `eicrecon-pr` checklist
   (`submodules/skill-eicrecon/plugins/eicrecon-pr/skills/eicrecon-pr/SKILL.md`) and the open items of
   `space/reports/phase4_upstream.md`.

No unit may change the physics beyond what Z8 measured: this phase finds no new Λ. **The user opens every pull request.**
The agent never pushes, never opens a pull request, never comments on GitHub, in any repository (CLAUDE.md, D-user-34).
A unit's deliverable is a patch, a pull-request description draft and its evidence, and with `please-git` in the start
line, a local branch.

**The start:** Z8_hcal_axis_law (`space/reports/phase6_crystal.md`, Final state): EICrecon a15b0db6 + Phase 5 and 6
patches, whole diff `space/notes/patches/phase6_working_tree.patch`, plus 15 run-time parameters
(`configs/experiments/Z8_hcal_axis_law.yaml`). On the MSF search halves it finds 1688 + 258 = 1946 Λ → nπ⁰, purity 30.9 %;
held out 1621 + 244 = 1865; −t σ68 0.114 / 0.118 GeV²; D4 S4a_tm 8.42 % mean (CP6_2_Z8_D4).

### The base (Q23)

EICrecon main has moved since the pin e5e2a60c; PR 3064 (ZDC clustering and calibration) and PR 3063 (Λ mass windows) are
still open, and 3063 was updated on 2026-11-09. Phases 4–6 sit on both. Step 0 item 1 reads their current heads read-only
(`gh pr diff`, `gh api`) and diffs them against `R1_pr3064.patch` and `R3_pr3063.patch`. The user chooses the base (Q23):
main with the two PRs' current heads stacked under the series (recommended: reviewers and CI see the code where it will
land), the pin, or the pin first with a port to main at the end.

The base source is a tarball of its commit (`gh api repos/eic/EICrecon/tarball/<sha>`) unpacked under
`{data}/upstream/`, one source tree per unit with the patches applied by `patch -p1`. The user's submodule and its
working tree (the Phase 6 state, the user's review queue) stay untouched. `102_build_eicrecon.sh` gets `--source <dir>`
(Step 0).

### The units (proposed; Step 0 item 2 fixes the split)

| unit | content | from | files | default | declared: the collections it may change | benchmarks |
|---|---|---|---|---|---|---|
| P1 | photon depth limit measured from the ZDC face (`gammaZMaxOffset` −691.4 mm; the stock 400 mm is added to the ZDC centre, lands 1316 mm past the face and cuts nothing; finding F7) | X5 | `reco.cc` | on | `ReconstructedHcalFarForwardZDCNeutrals`, `ReconstructedLambda*` | zdc_photon, zdc_pi0, zdc_lambda |
| P2 | ImagingTopoCluster photon-core split | U3 (X7, X8) | `ImagingTopoCluster.{cc,h}`, Config, factory | **off** | none: every collection identical, BEMC and FHCAL included | barrel_ecal, lfhcal: identical outputs, said so |
| P3 | LambdaReconstruction: stable vertex with each daughter's lever arm, neutron at its reference point (findings F9, F10) | U1 + Y2 | `LambdaReconstruction.cc` | on | `ReconstructedLambda*` | zdc_lambda, zdc_sigma |
| P4 | ZDC Λ pairing in FarForwardNeutralsReconstruction: the photon pair chosen by the Λ hypothesis, with a B0 photon (Y5) and with two B0 photons (Y9), photon depth and isolation terms | U2 + Y5 + Y9 + Z7 (+ Z4's width) | neutrals `.cc`, `.h`, Config, factory | **off** | none | — |
| P5 | crystal-seeded photons and their energy laws (crystal law, crystal-law alternative, axis law); three new factory inputs | Z1b, Z5, Z6, Z8 (neutrals part) | neutrals files, `reco.cc` inputs | **off** | none | — |
| P6 | LYSO crystal section clustered at the crystal scale (3.5 cm neighbourhood, split at local maxima, Molière-radius sharing) | Z1b (`ZDC.cc` part) | `ZDC.cc` | on | `EcalFarForwardZDC*` clusters, proto-clusters and associations | zdc_lyso (it reads these clusters), zdc_photon |
| P7 | B0 ECal: islands split at local maxima, energy shared at 0.3 crystal; the B0 photon law refit on the B0 photon gun | Y4, Y6, Y8, Y7 (Phase 5 parameters) | `B0ECAL.cc`, `reco.cc` | on | `B0ECal*` clusters, proto-clusters and associations, `ReconstructedB0EcalNeutrals`, `ReconstructedLambda*` | far_forward_dvcs (it reads `B0ECalClusters`), the B0 photon gun D2b (`467`) |
| P8 | the ZDC configuration that switches P2, P4, P5 on, with the refit calibrations and Z8's 15 parameters as defaults | U4 + switches + Z8 yaml | `ZDC.cc`, `reco.cc` | on | `HcalFarForwardZDC*` clusters, `Reconstructed*Neutrals`, `ReconstructedLambda*` | zdc_pi0, zdc_photon, zdc_neutron, zdc_lambda, zdc_sigma |

P7 is the one unit that moves another calorimeter on purpose: the B0 ECal clusters change for every user of them. Its
evidence goes to the user before its draft is written (a FIX/ASK stop, not a verdict of the agent). P2, P4 and P5 are
default-off, so with them alone every collection stays identical. P8 must reproduce Z8: N_found 1946 on D6s and 1865 on
D6h, Λ by Λ (`210`), D4 8.42 % mean.

Dependencies: P3 on PR 3063; P6 and P8 on PR 3064's ZDC configuration; P5 on P4; P8 on P2, P4, P5. Step 0 may merge or
split units when the code says so (for example a shared vertex helper for P3 and P4), and records the final table in
`configs/upstream_units.yaml` (frozen after Step 0).

### The check ladder (every unit, in this order; each line is a decisive outcome)

| # | check | PASS when |
|---|---|---|
| 1 | **split** | the unit's patch applies to the previous unit's tree; after P8 the tree equals the Phase 6 tree plus the defaults (Step 0 item 2) |
| 2 | **build and style** | incremental build in the pinned image; `clang-format` (EICrecon's `.clang-format`) and `pre-commit` clean on the changed files; units on every new config value; no magic numbers; a Catch2 test for new algorithm code (core split, pairing, crystal photons) passes; `465` patch scan PASS (no truth, no dataset-keyed constant) |
| 3 | **cleanup changes nothing** | the cleaned unit with the Phase 6 run-time parameters gives the same outputs as the Phase 6 install it came from (`130` on D6s files 0001–0004, every collection) |
| 4 | **switch off** | a default-off unit (P2, P4, P5): every collection identical to the previous unit on the identity set |
| 5 | **other calorimetry** | on the identity set: every collection outside the unit's declared list identical to the previous unit (`483`, `130`'s leaf compare with the unit's list) and the capybara view of the undeclared collections prints no leaf; a FAIL stops the unit and goes to the user (ASK): a declared list never widens without the user's word |
| 6 | **benchmarks** | the declared collections on the unit's benchmarks, before and after, plots as PNG under `space/plots/phase7/<unit>/` and the benchmarks' own numbers in a table; the capybara view of the declared collections beside it |
| 7 | **physics and cost** | the unit's effect on N_found (D6s) and on D4 S4a_tm where it changes the Λ chain; wall seconds per 1000 events on D4 275 GeV and one D5 chunk; > 10 % slower goes in the draft, 2× is a question |
| 8 | **draft** | `space/reports/phase7_upstream/<unit>.md`: title, why, what changes, how to switch it on, dependencies, the evidence table, the checklist; patch `space/notes/patches/phase7/<unit>.patch` |

**The identity set** (full collections, single-threaded, `-Pjana:nthreads=1`): D5_dis_minq2_100 and D5_dis_minq2_0, chunks
000 and 001 each (the CI's DIS samples; every calorimeter of the detector); one file per gun: D1 100 GeV, D2 50 GeV, D3
100 GeV, D4 175 GeV, D2b 10 GeV, D2c 10 GeV; D6s_9x275 file 0001. Reconstructed per unit and kept until the next unit has
passed check 5 against it; then listed in `space/notes/cleanup-pending.sh`.

### Step 0 (before the first unit)

| # | item | decisive outcome |
|---|---|---|
| 1 | **The base** (Q23): heads of main, PR 3064 and PR 3063 read with `gh` (read-only); their diffs against the program's copies; the base tarball under `{data}/upstream/`; built in the pinned image (`102 --source`) | the base builds; the PR copies' differences listed in the report. A base that needs a newer image is a question, never a silent image change |
| 2 | **The split**: the Phase 6 tree cut into P1–P8 by file and by hunk | the units applied in order to a15b0db6's tree give `phase6_working_tree.patch`'s tree byte for byte (as Phase 4 proved U1–U4); then the same units applied to the base, with every conflict listed |
| 3 | **References at the base**: R0b (the base, stock) on the identity set, twice | the two runs identical (`130`, every collection): the ruler is deterministic at the base. At the pin, R0 reproduces its recorded scoreboard row on D5 (rule 2) |
| 4 | **`483` written and proven** (identity with a declared list + capybara of the undeclared and declared collections + summary JSON) | FAIL on a control that changes one BEMC parameter (it must name the `EcalBarrel*` collections), PASS on a control that changes only a declared ZDC collection, FAIL on a run with a missing file |
| 5 | **Benchmark copies** (Q24): zdc_lyso, zdc_sigma and far_forward_dvcs added to `scripts/700_benchmarks/` with main's collection names, run by `401`; their samples generated with the benchmarks' own generators | each benchmark runs on R0b and on a damaged input and its numbers move; the new datasets in the manifest |
| 6 | **FROZEN rewrite**: this file, `483`, `configs/upstream_units.yaml`, the benchmark copies | the hook refuses an edit to `483` |
| 7 | **Report and deck**: `space/reports/phase7_upstream.md`, `slides/phase7/` (a slide per unit: the stack with the unit highlighted, the ladder's results, benchmark plots; a diagram for each code change) | both build |

### Order of work

P1 (smallest, independent; its effect on the stock chain was never measured), P2 (the shared algorithm: the plainest
proof that other calorimeters do not move), P3, P4, P5, P6, P7, P8. A unit that fails a check is fixed in its own code or
stops with a question; the next unit does not start on a failed one.

### Stop rules

- P8 reproduces Z8 and every draft is written: the run ends with the report and the deck for the user.
- A check fails and the fix would widen a declared list, change a default the user did not approve, or change a frozen
  file: STOP that unit and ASK.
- `one unit` in the start line: the run stops after each unit for the user's review.
- The user stops it.

### Git

Without `please-git`: no git at all in the user's repositories. Source trees live under `{data}/upstream/` (not git
checkouts); patches and drafts are the transport. With `please-git` in the start line: one local branch per unit in the
EICrecon submodule, `zdc-upstream/<unit>`, stacked on the base (the base fetched into the submodule for it), one commit
per unit with the draft's text as its message. **Never push, never open a pull request**, in any repository.

### Resources

D-user-35 holds: ≤ 4 reconstruction jobs, 8 idle cores, `/data` ≥ 150 GB free, no GPU. A full-collection DIS chunk
takes about 2.4 s per event (NC) single-threaded; the identity set is about 4 chunks of D5, 6 gun files and one MSF file
per unit. Benchmark samples are sized in Step 0 against the same limits.

### Reporting

As version 6: numbers from result files, timestamps from `date -u`, PNG plots, plain language first in every chat line
(what changed, what it means), then the unit's ladder in one line: split, build, switch-off, other calorimetry,
benchmarks, physics, draft.
