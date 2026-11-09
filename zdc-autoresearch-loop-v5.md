# ZDC autoresearch loop — version 5: Λ → nπ⁰ on MSF events

Read `zdc-setup.md` and `work-common.md` first; they still define the
names, paths, references, the start protocol, the ledger and the reporting
habits. Version 4 (`zdc-autoresearch-loop-v4.md`) still defines the fair-play
rules F1–F3 and the open EICrecon; this file overrides it wherever it says
so, and it governs Phase 5.

The user's order (2026-11-08, chat): *"Create a new phase and Continue?"*,
then the selector *"Yield, purity guard"*, then, after the definitions below
were spelled out, *"Okay, I agree with your metrics to be optimized. Let's
start the phase run."* (D-user-39)

## Phase 5 — Λ → nπ⁰ on MSF events

**Goal:** find more Λ → nπ⁰ in EICrecon on the meson-structure (MSF)
events, without making the Λ sample dirtier. Phase 4 maximized the rate on
the D4 Λ gun; on MSF events the same code finds a third of what the
detector can reach.

### The two numbers (per beam energy, `210`)

- **N_expected** = 0.358 × N_Λ, the generated Λ (one per MSF event) times the
  Λ → nπ⁰ branching fraction: 14 320 for 40 000 events, 7 160 for a half.
- **N_found**: events whose true Λ decayed to n π⁰ (π⁰ → γγ) in which a
  `ReconstructedLambdas` entry has |m − m_Λ| < 30 MeV (`configs/metrics.yaml`)
  and three daughters: a ZDC neutron neutral holding a cluster of purity
  ≥ 0.8 for the true neutron, and two photon neutrals (ZDC, B0 or EEMC-P)
  holding clusters of purity ≥ 0.8 for the two distinct true photons.
  Purity is the cluster's summed association weight over the particle and
  its descendants, as `410` computes it. Truth is used only to score.
- **N_window**: events with a `ReconstructedLambdas` entry inside the same
  ±30 MeV window, right or wrong (F3a allows one entry per event).
- **Yield** = N_found / N_expected. **Purity** = N_found / N_window.

At the start (X9, D6c, 40 000 events per beam): yield 12.85 ± 0.30 % at
9x275 and 0.90 ± 0.08 % at 9x130, against 43.6 % and 8.0 % that the
detector can reach (n in the ZDC, both γ in a calorimeter the chain reads);
purity 21.0 % and 9.2 %.

### The selector (`463`)

- **Score:** N_found(9x275) + N_found(9x130) on the search halves D6s
  (both beams have the same N_expected, so this is the mean yield).
- **Paired test** on identical Λ, current best vs candidate: b = Λ found
  only by the best, c = only by the candidate, z = (c − b) / √(b + c),
  pooled over both beams.
- **Purity guard:** z_P = (P_cand − P_best) / √(σ_cand² + σ_best²),
  σ = √(P (1 − P) / N_window), on the pooled purity Σ N_found / Σ N_window.
  The two samples share their events, so the unpaired σ is conservative.
- **Verdict:**
  - FOUL: `460` FAIL (fair play, below).
  - REJECTED (purity): z_P < −2.
  - ACCEPTED: z ≥ 3 and c > b.
  - INCONCLUSIVE: c > b but z < 3. Kept in the backlog for a combined retry.
  - REJECTED: otherwise.
- A try that raises purity at equal yield cannot be accepted under this
  selector; it is reported, and a purity-led selector is a question for the
  user.

### Data

- **D6s_9x275, D6s_9x130** (search): files 0001–0040 of D6c, 20 000
  events per beam. Every try runs on both.
- **D6h_9x275, D6h_9x130** (held out): files 0041–0080. Never read while
  tuning; reconstructed only at checkpoints.
- **D4 / D4h** (the Phase 4 Λ guns): S4a_tm reported at checkpoints, never
  selected on. A drop there is reported, not reverted.
- The links share the D6c files (`/data/zdc-autoresearch/msf-2026-11/`);
  nothing is copied.

### What carries over from version 4

- EICrecon is open except the fair-play files of `space/FROZEN`
  (`CalorimeterHitDigi`, `CalorimeterClusterRecoCoG`, `CalorimeterClusterShape`
  and their configs and factory headers). That includes the B0, EEMC-P and
  LFHCAL reconstruction, even when a try changes their collections.
- **F1 truth-blind reconstruction, F2 the data are the data, F3 honest
  candidates**, word for word. `460` checks them on the MSF outputs:
  `460 <yaml> --reco-dir {reco}/<exp>/D6s_9x275 --reference-dir
  {reco}/MSF5_X9/D6s_9x275 --tag <exp>-msf`. F2b then compares the try's
  raw hits with the base row's on file 0001; the base row shares the pin's
  digitization, and X9 passed F2b against R0 on D4.
- A try is an uncommitted patch, and `460` reads committed sources (F1a, F1b)
  and, for a source tree, only the registration files. So a code try also
  runs `460 <yaml> --tree submodules/EICrecon --tag <exp>-tree` (F1a–F1c on
  the working tree's registrations) and `465 <patch>`, which scans every
  added line of the patch with `460`'s own truth and dataset patterns. F1d
  (janadot) runs on the try's install in the `-msf` run. A FAIL of any of
  the three is FOUL.
- No constant may be keyed to a dataset, a beam energy or a file (F1).
  Beam energies and the geometry come from the detector configuration, as
  in the stock code.

### F4 — a frozen scorer (replaces version 4's F4)

- `configs/metrics.yaml`, `configs/datasets.yaml` (after the D6s / D6h
  entries), the manifests, the scripts `210`, `460`, `463` and the scorers
  frozen in Phase 4.
- Calibrations are fitted on single-particle guns (D2, D3, or a gun
  dataset added for a try under a `D-default`), never on D6.

### F5 — held out (replaces version 4's F5)

- At every checkpoint the current best is reconstructed on D6h and
  compared with the previous checkpoint's best by `463 --split h`.
- If the gain does not reproduce in sign at more than 2σ pooled, the
  accepted steps since the last checkpoint are reverted: an overfit.

### F6 — process safety (replaces version 4's F6)

- `300` is the only launcher, with its preflight and integrity check.
- **No commits this phase.** The start line had no `please-git`, so a try is
  a patch: `git diff > {space}/notes/patches/Y<N>_<name>.patch` in the
  EICrecon working tree on top of a15b0db6 (`zdc-autoresearch/phase4`), and
  `git apply -R` after any verdict but ACCEPTED. Accepted patches stay
  applied and the next try stacks on them. No branch change. If a later
  start line carries `please-git`, the tries become commits on
  `zdc-autoresearch/phase5`, cut from a15b0db6.
- **Never `git push`, never a pull request, never a remote branch**, in any
  repository.
- **The MSF template** writes `EventHeader`, the ZDC and B0 raw hits, the ZDC
  and B0 clusters, the ZDC, B0 and EEMC-P cluster associations, every
  `Reconstructed*Neutrals` and `ReconstructedLambda*`: about 1 GB per try on
  both search halves. `MCParticles` (97 % of a full output) is left out;
  `210` reads truth from the simulation files.
- A try whose verdict is not ACCEPTED goes into
  `space/notes/cleanup-pending.sh` at its verdict (D-user-32: the user
  deletes). The disk floor of `300` (150 GB) stands.
- D-user-35 stands: dis-autoresearch has priority; 4 jobs, 8 idle cores.

### Step 0 (before the first try)

| # | item | decisive outcome |
|---|---|---|
| 1 | D6s / D6h registered: four `configs/datasets.yaml` entries and manifest sections (`112 --skip`), through temporary FROZEN exceptions. | 40 files of 500 events in each of the four. |
| 2 | `210` writes N_window and purity per row; `463` written. | `210` on MSF11_X9 / D6c_9x275 reproduces N_found 1840 and gives N_window 8749. |
| 3 | The base row MSF5_X9: X9 on D6s and D6h with the MSF template. | Its N_found per Λ equals MSF11_X9's on the same files: the template and the rerun change nothing. |
| 4 | The ruler seen to fail. | `463` ACCEPTS X9 over an earlier Phase 4 row on D6s and REJECTS the reverse; a control with truth misaligned by one file is REJECTED by `463` and FAILS `460` F2b; the purity guard REJECTS a copy of the base row's `210` output whose N_window is inflated. `460` PASSES on MSF5_X9. |
| 5 | `space/FROZEN` rewritten: this file, `210`, `463` and `configs/datasets.yaml` frozen. | The hook refuses an edit to `210`. |
| 6 | The report `space/reports/phase5_msf.md` and the deck `slides/phase5/`. | Both exist before the first try. |

### The experiment loop

- Ids `Y<N>_<name>`; configs `configs/experiments/Y<N>_<name>.yaml`
  (`install_label`, `source_commit` = a15b0db6 plus the patch named in
  `notes`), datasets [D6s_9x275, D6s_9x130], the MSF template.
- `hypothesis:` one line, written before launch: the mechanism and the
  predicted N_found per beam and purity direction.
- Build: `102 --label Y<N>`; then `300 <yaml> --phase phase5 --lean`; `460`
  on the MSF outputs; `210` on both D6s; `463 <best> <candidate>`.
- The verdict, the ledger entry (`space/EXPERIMENTS.md`), a slide.
- **Checkpoint every 5 tries:** F5 on D6h, S4a_tm on D4 (reported), the
  report, the deck, and a chat line with yield and purity per beam beside
  the reachable 43.6 % / 8.0 %.
- The run continues until the user stops it, the backlog is empty, or two
  checkpoints in a row bring no accepted gain.

### Order of work: by the Λ at stake at 9x275 (share of N_expected)

1. **Y1: the B0 photon energy.** B0 photon neutrals carry a median 1.11 of
   the true photon energy (9x130: 1.15). In the γ B0 + γ ZDC regime (11.0 %
   of expected) the true triplet falls outside the window for 22 % of the
   Λ. A photon calibration of the B0 ECal fitted on a B0 photon gun.
2. **Y2: the pairing with a B0 photon.** In the same regime the chain picks
   another triplet for 26 % of the Λ (2.8 % of expected).
3. **Y3: two photons in B0.** 4.0 % of expected; the island clustering
   merges the pair for 93 % of them (`splitCluster` false). Splitting the
   B0 clusters at local maxima.
4. **Y4: ZDC photon clustering.** The all-ZDC regime is 27.9 % of expected
   and X9 finds 36.8 % of it; a photon without a photon neutral loses 56 %
   (15.7 % of expected). ZDC photon neutrals carry a median 0.56 of their
   photon's energy, fragments included. Photon fragments merged into one
   neutral; the swallowed photons Phase 4 left (`470`).
5. **Y5 onward:** free choice, each with a prediction line, ranked by the
   expected gain on the score.

### Reporting

- Every number comes from `msf-regimes-*.json`, `msf-select-*.json`,
  `fair-play-*.json` or `headline.csv`.
- Timestamps come from `date -u` (two hand-typed times were wrong on
  2026-11-08).
- Plots are PNG.
- The phase deck (D-user-36): `slides/phase5/`, a slide per try (the
  mechanism, the prediction, yield and purity per beam, the fair-play
  verdict, the decision), a diagram for a structural change, updated after
  every verdict and checkpoint.
