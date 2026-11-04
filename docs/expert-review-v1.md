# Expert review of the ZDC autoresearch loop, version 1

Reviewer: independent reviewer (calorimeter reconstruction in ePIC/EICrecon,
autonomous experiment loops). Date: 2026-11-04. Inputs read: `docs/zdc-problem.md`,
`zdc-setup.md`, `zdc-autoresearch-loop-v1.md`, `work-common.md`, `configs/*.yaml`,
EICrecon at the pin `e5e2a60c`, `detector_benchmarks` at `e72103b9`, the epic
checkout at `~/dev/eic-workbench/epic` (`f961753`, 2026-09-24; not the 26.11
install, so every epic claim below is "as of 26.09"), `gh issue view 2737` and
`gh pr view 3064`. Nothing was run. All EICrecon paths are relative to
`submodules/EICrecon/src/`, benchmark paths to `submodules/detector_benchmarks/benchmarks/`.

## 1. Verdict

1. No, not as written. The loop would converge, but on a number. It would not be a reconstruction the reviewers merge.
2. Biggest risk: the primary metric S4a is limited by `LambdaReconstruction`'s own π⁰ preselection and is gameable through calibration and window parameters the loop owns, so "S4a improves" does not mean "π⁰/neutron separation improves".
3. Second risk: the search set (D1 to D4) is simulated without the LYSO crystal ECal that sits in front of the HCal in every physics sample (D5, D6), so photon tuning does not transfer to MSF.
4. Third: Phase 0 items 6, 8, 12 cannot reach their stated decisive outcomes (R1 base mismatch, stale benchmark names, invalid output regexes); see section 3.
5. The PR's three review findings already have one mechanism you can show from the code (section 2.4), so Phase 1 can shrink to a confirmation and the budget can move to the separation problem.

## 2. Physics and metric critique

### 2.1 Do the datasets exercise the problem? (opening distances at 35.8 m)

π⁰ gun D1 decays at the IP (`zdc_pi0/analysis/gen_pi0_decay.cxx:80-92`). Minimum opening angle θ_min = 2m_π/E;
for isotropic decay the median is 1.155·θ_min (P(θ < xθ_min) = √(1−1/x²)). Distance at 35.8 m:

| E_π (GeV) | θ_min (mrad) | d_min (mm) | d_median (mm) |
|---|---|---|---|
| 60 | 4.50 | 161 | 186 |
| 80 | 3.37 | 121 | 140 |
| 100 | 2.70 | 97 | 112 |
| 130 | 2.08 | 74 | 86 |
| 160 | 1.69 | 60 | 70 |

Every pair is farther apart than the 36.6 mm neighbour distance. With S2 subcells the relevant
quantity is the subcell pitch: HEXPLIT S2 puts subcells at ±0.5·sl with sl = dimension.x/2 = 24.4 mm
(`algorithms/calorimetry/HEXPLIT.cc:88-89,121,181-183`), and the staggered layer is shifted by
(±sl, ±sl) (`HEXPLIT.cc:83-84`). Both layer types therefore share one 24.4 mm subcell grid.
The box cut `|Δx| ≤ d && |Δy| ≤ d` (`ImagingTopoCluster.cc:285-286,326-327`) is a step function of d:
- below 24.4 mm, no lateral neighbours;
- from 24.4 to 48.8 mm, a 3×3 neighbourhood (stock 36.6 mm);
- from 48.8 mm, 5×5.

So at 60 to 160 GeV the photons merge because the topological chain bridges 3 to 7 subcell pitches
through shower tails above `minClusterHitEdep` (315 keV per *subcell*, `detectors/ZDC/ZDC.cc:199`), not
because their centroids sit inside one neighbour distance. veprbl's comment on #2737 ("pions above
80 GeV are not showing up", 26.04 → 26.05) fits this: the merge scale is about 120 mm.
Consequences:
- The backlog item "a distance between 14.6 and 36.6 mm" (loop, Phase 1 step 4) has only two
  outcomes, 1×1 or 3×3. It is not a continuous scan.
- The knob that is missing from the PR and from the backlog is `minClusterHitEdep`, the chaining threshold.
  Note that a 1-MIP tile (630 keV) splits into four subcells of about 160 keV each, below the 315 keV cut.
- `ImagingTopoCluster` has no local-maximum splitting at all (`ImagingTopoCluster.cc:215-235`).
  The ZDC already builds `HcalFarForwardZDCIslandProtoClusters` on the subcells (`ZDC.cc:206-226`,
  `splitCluster = false`), and nothing consumes them. Island clustering with splitting, feeding the CoG,
  is the obvious Phase 3 candidate, and it is cheaper than the two-pass idea.

Λ gun D4: in the Λ rest frame E*_π = 0.170 GeV and p* = 0.104 GeV, so the π⁰ carries 6 to 25 % of E_Λ.
The generator accepts an event only when n, γ1 and γ2 all extrapolate within 4 mrad of the beam at
z = 35.8 m (`zdc_lambda/analysis/gen_lambda_decay.cxx:226-229`), so the two photons can be at most
286 mm apart at the face. At 100 GeV the π⁰ has at most 24.6 GeV, θ_open ≥ 11 mrad, which needs
L − z_d ≤ 26 m: **only Λ decaying beyond z_d ≈ 10 m are accepted at 100 GeV** (estimate; verify with truth).
- Photons in D4 are typically 15 to 70 GeV and well separated from each other.
- The separation that fails in Λ events is γ against the neutron's hadronic halo: all three particles sit
  inside a 143 mm radius.
- D1 (60 to 160 GeV, symmetric γγ) measures neither the right photon energies nor the n–γ overlap.
  S1 is a weak proxy.

### 2.2 S4a as the primary metric: it is dominated by LambdaReconstruction, not by clustering

- **IP-pointing preselection.** `makeGamma` sets the photon momentum along the cluster position seen
  from the origin (`algorithms/reco/FarForwardNeutralsReconstruction.cc:97-103`). The π⁰ pair mass in
  Step 3 is built from those momenta and cut at ±`pi0Window` = ±10 % (`LambdaReconstruction.cc:309-322`,
  `global/reco/reco.cc:274`). For a decay at z_d the IP-pointing opening angle is smaller by
  (L−z_d)/L, so m_γγ(IP) ≈ m_π(L−z_d)/L. **Only decays with z_d ≲ 3.6 m pass**, unless the photon
  energies are overestimated. The vertex iteration (`LambdaReconstruction.cc:85-100`) runs only after this cut.
- **The ceiling that follows.** βγcτ is 7.1 m at 100 GeV and 19.4 m at 275 GeV. Given decay before
  the ZDC, the fraction with z_d < 3.6 m is about 0.40 and 0.20. At 100 GeV the acceptance cut of 2.1
  leaves essentially none. S4a has a structural ceiling of order 0.1 to 0.3 *whatever the clustering does*.
  The "ε ≈ 0.3" of the statistics budget is that ceiling, not a clustering efficiency.
- **Loophole: the calibration refit.** Inflating photon energies by about 1/(1−z_d/L) moves late
  decays into the π⁰ window. A `gammaScaleCorrCoeffHcalZDC` refit that maximises S4a will learn this bias.
  The PR's {2.7, 1.27} (super-linear, b > 1) is the signature to worry about. S2 (photon scale) is only a
  "search" metric and is not in the acceptance guards (`zdc-setup.md:119-123`), so nothing stops it.
- **Loophole: the windows.** `pi0Window`, `lambdaMassWindow` and `iterations` are JANA parameters
  (`factories/reco/LambdaReconstruction_factory.h:33-35`) on a factory the loop owns
  (`docs/zdc-problem.md:81-82`). Widening `pi0Window` raises S4a directly.
- **Loophole: fragment combinatorics.** For the ZDC, `GammaMode::AllPassing` makes every `isGamma`
  cluster a photon, and `SumAll` sums the rest into one neutron (`FarForwardNeutralsReconstruction.cc:151-163,
  216-223,268-281`). Small fragments pass `isGamma` trivially, because l2 and l3 are about 0 for a thin cluster
  (`:39-61`). `LambdaReconstruction` tries every γ pair × neutron and keeps the best χ²
  (`LambdaReconstruction.cc:309-449`), so more fragments mean more chances that one combination falls in the window.
- **No truth matching.** S4a counts any Λ inside the mass window. The cluster→MC associations exist
  (`HcalFarForwardZDCClusterAssociations`, `ZDC.cc:244-254`; provenance kept by #3061, `HEXPLIT.cc:219-224`).
  Use them.

Verdict on S4a: keep it as the *physics outcome* metric, but it must not be the selector. The selector
for clustering should be truth-based and independent of LambdaReconstruction:
- per true photon in D4, the fraction whose best-matched cluster has purity ≥ 0.8 (energy fraction from
  that MC particle) and contains ≥ 50 % of its deposited energy (the "separation efficiency");
- the same for the neutron;
- S4a reported beside these, against a **truth-cluster ceiling**: the Λ chain replayed offline on
  `HcalFarForwardZDCTruthClusters` (`ZDC.cc:256-306`).

### 2.3 Is S3 enough to protect the neutron?

No. Neutron energy is `corrPower` of the *sum of non-γ clusters* (`FarForwardNeutralsReconstruction.cc:204-229`).
Every fragment tagged γ leaves the neutron sum, and a refit `neutronScaleCorrCoeffHcalZDC` hides the loss.
The PR's {16.65, 0.66} implies that a 100 GeV neutron keeps only about 15 GeV of raw cluster energy, against
about 66 GeV with the stock {2.4, 0.89}: the refit compensates for the missing energy.
- S3 must contain the raw `Σ HcalFarForwardZDCClusters.energy / E_true` (mean and σ), with no `corrPower`.
- It must also contain the number of clusters per neutron and the energy fraction tagged γ in neutron events.
- D3 as specified does not exist. `gen_forward_neutrons.cxx:29-30` hard-codes p = 100 GeV and θ ≤ 6 mrad,
  and the Snakefile passes no momenta. The neutron benchmark also runs on `epic_craterlake`, not on
  ZDC-only (`zdc_neutron/config.yml`). "Replace the placeholder momenta with the benchmark Snakefile values"
  (loop item 3) yields one momentum.
- Use an npsim gun scan over 20 to 275 GeV, inside 4 mrad, on the same detector config as D4.

### 2.4 G1 to G3: artifact or bug? The mechanism is visible from the code

The PR sets d = 14.64 mm, which is below the 24.4 mm pitch, so it removes *all* lateral connectivity.
The same-layer cut can never pass between distinct subcells, and the different-layer cut passes only for
the same (x, y) column, up to about 0.7 mm per layer of crossing-angle shift, because the different-layer
test uses global x (`ImagingTopoCluster.cc:324-327`; layer pitch 28.3 mm from epic `ZDC_SiPMonTile.xml:15-29`).
With `neighbourLayersRange = 3` each cluster is a single 24.4 × 24.4 mm column through ±3-layer gaps.
- **G1.** The principal axis of a column is the ZDC axis, which is rotated by the crossing angle
  (`ZDC_SiPMonTile.xml:55`). The axis is flipped toward the cluster position, which is at x ≈ −0.9 m
  (`algorithms/calorimetry/CalorimeterClusterShape.cc:170-216`). So the intrinsic φ is exactly ±180°.
  Stock clusters get their φ spread from lateral shower asymmetry, which columns do not have.
- **G2 and G3.** Showers shatter into many columns, so the high-energy tail disappears and low-energy
  clusters appear. The 5 MeV seed and `minClusterNhits = 2` then keep the shards.

So G1 is neither a "two-subcell line" (loop line 128) nor a harmless geometry artifact. It is the
signature of disabled lateral clustering. The guards as defined (the fraction within 5° of ±180°, and a χ²)
cannot tell this apart from a legitimate change. Add:
- the number of distinct (local x, y) per cluster (a fraction with exactly 1 means columns);
- the intrinsic θ beside φ;
- the lateral width √λ2 against energy.

These three numbers decide artifact versus bug with no plot.

### 2.5 Missing physics

- **The LYSO ECal.** epic `configurations/zdc_sipm_on_tile_only.yml` contains only `ZDC_SiPMonTile`.
  The full detector `far_forward/default.xml:12-13` adds `ZDC_Crystal_LYSO`: 7 cm crystals, about 6 X0 and
  0.33 λ_I, ending at 35.75 m (`ZDC_Crystal_LYSO.xml:14-16,28`).
  - Photons in D5/D6 deposit a large fraction of their energy there.
  - `FarForwardNeutralsReconstruction` never reads `EcalFarForwardZDCClusters` (`reco.cc:242-246`).
  - Guns must use `epic_zdc_lyso_sipm` (`configurations/zdc_lyso_sipm.yml`), or both configurations.
    Otherwise every γ calibration and threshold is tuned on a detector that MSF does not have. This is a user decision (section 4.4).
- **The RecHit-level loss.** Issue #2737 reports that events with HCal RecHits fell from 95.0 to 68.5 %
  (26.02 → 26.07). Clustering cannot recover that. Add an acceptance row (events with ≥ 1 RecHit;
  truth daughters inside the face) so that the S5 ceiling is known before Phase 4 is judged.
- **Position resolution** of photon clusters (it feeds both the π⁰ mass and the vertex iteration).
  Opening-angle acceptance against E_π is in the table above. Neither is on the scoreboard.
- **EM/hadronic discrimination** is three cuts on shape eigenvalues plus a z cut. The z cut is
  `HcalFarForwardZDC_SiPMonTile_r_pos + 400 mm`, and `r_pos` is the *centre* of the ZDC (`ZDC_SiPMonTile.xml:59`),
  so the cut sits about 1.3 m deep and is close to inert. `zdc-problem.md:51` misstates it.
  The γ-tag efficiency and n mis-tag need truth-matched definitions.
  "Leading neutral is PDG 22" is ill-defined, because photons are created before the neutron and order is not energy.
- **Timing:** `tRes = 0` (`ZDC.cc:146`), and no clustering stage uses time. This is out of scope for v2, but say so.
- **Backgrounds:** the MSF 2026-07 tree has `bg_merged` (`meson-structure/docs/data.md:30-33`).
  Step 0 must record whether `dd4hep` was simulated from it. If so, S5 contains beam-gas clusters that no search set has.

### 2.6 Statistics budget arithmetic

- **S4a.** √(0.3·0.7/2000) = 0.0102 absolute, which is 3.4 % relative, not 3 %.
  - The mean of eight momenta gives 0.0036 (1.2 % relative), so "resolves 2 %" is 1.7σ for one sample
    and 1.2σ for an unpaired difference.
  - With ε ≈ 0 at 100 GeV (2.1) the "average" is in practice four or five points.
  - All configurations run on the *same* simulated events, so the right test is paired (McNemar on
    discordant events). That test is much tighter than the band, and it is free.
- **S1a.** ±1.1 % is correct.
- **S5.** The arithmetic is right (450 → 4.7 %; 4500 → 1.5 %), but the 4.5 % is the hex-era number.
  On square tiles R0 is close to 0, so Phase 4 compares about 0 with X. Size it on X: at X = 2 %,
  100 k events give 2000 Λ and 2.2 %.
- **D5.** 2000 *events* is not 2000 *clusters*. DIS NC minQ2 = 100 has a forward neutron in a minority of
  events, and #2737 measured 0.51 clusters/event even on MSF. 36 bins × 50 entries needs ≥ 1800 R0 clusters,
  and the R0 φ distribution is not flat, so the edge bins need more still. Size D5 by measured cluster count.
- **The noise band.** "max(seed-to-seed difference, stat error)" from *one* seed pair is a single draw.
  It can come out arbitrarily small. It also exists only at 100 GeV (D1) and 175 GeV (D4), yet it is applied
  to an 8-momentum average.
- **"Once more on the same files"** measures determinism, not noise (digitisation is seeded per event).
  Loop rule 8 ("repeat once when within 1.5 bands") is therefore vacuous: a repeat on the same files
  reproduces the same number.

## 3. Code and tooling critique

| claim in the protocol | verdict from source |
|---|---|
| "every config value above is a JANA parameter" (`zdc-problem.md:89`) | **False** for `sameLayerDistXY`/`diffLayerDistXY`: commented out at `factories/calorimetry/ImagingTopoCluster_factory.h:24-27`, type `vector<variant<string,double>>` (`algorithms/calorimetry/ImagingTopoClusterConfig.h:19,29`). The same holds for the Island `localDistXY` (`CalorimeterIslandCluster_factory.h:24`) and HEXPLIT `stag_type` (`HEXPLIT_factory.h:21-23`). The CoG sampling fraction is named `samplingFraction` (`CalorimeterClusterRecoCoG_factory.h:33`), but `sampFrac` in ClusterShape (`CalorimeterClusterShape_factory.h:36`). |
| Other PR parameters settable with -P | **True**: `neighbourLayersRange`, `minClusterCenterEdep`, `minClusterNhits` (`ImagingTopoCluster_factory.h:43-48`); the coefficients and `gammaMaxLength` (`factories/reco/FarForwardNeutralsReconstruction_factory.h:36-40,75`). Units are dd4hep (GeV, **cm**), so `0.005` = 5 MeV is right. |
| unknown parameters need a dump_flags search (item 9) | The eicrecon CLI sets `jana:parameter_strictness = 2` (`utilities/eicrecon/eicrecon_cli.cc:422-423`), so a misspelt or unregistered -P already aborts. `R1_pr3064.yaml` fails loudly until item 7 lands, which is good. Keep the switch test only for "registered but inert". |
| `sameLayerDistXYmm` addition | Sound in principle: register two `ParameterRef<std::vector<double>>` with an empty default and, in `Configure()` before `applyConfig`, overwrite `config().*DistXY` when non-empty. `init()` reads the config at `ImagingTopoCluster.cc:57-60`. **But:** (a) the "mm" units break the EICrecon convention that every parameter is in dd4hep units; upstream will ask for cm, or better for a `vector<string>` evaluated by DD4hep, which is the real fix for the commented-out lines; (b) the factory is shared by BEMC (2×) and FHCAL (`detectors/BEMC/BEMC.cc`, `detectors/FHCAL/FHCAL.cc`), so G4 must cover those; (c) the R1 YAML passes `"14.64,14.64"` while the loop text says "doubles"; fix the type to a 2-vector. Given the step function in 2.1, the parameter buys little: three settings matter, and a code-tier build of each is cheaper than an upstream API debate. |
| `ReconstructedLambdas` vs `ReconstructedFarForwardZDCLambdas` | `metrics.yaml` is **right** for main (`global/reco/reco.cc:245,267,270`; `services/io/podio/JEventProcessorPODIO.cc:476,480`; renamed in a48dc937 / #2622, 2026-05-29). The **benchmarks are stale**: `zdc_lambda/Snakefile` requests `ReconstructedFarForwardZDCLambdas`, `lambda_plots.py:61-64` exits 0 when it is missing, `zdc_photon_plots.py:31-32` likewise for `ReconstructedFarForwardZDCNeutrals`, and `zdc_neutron/analysis/fwd_neutrons_recon.C:115-119` reads the old name. Step 0 item 12 therefore produces no Λ, photon or neutron plots, *silently*, and freezing `detector_benchmarks` (`zdc-setup.md:150-155`) forbids the fix. |
| `output_collections: ["*", "*FarForwardZDC*"]` (`configs/experiments/R0_stock.yaml`) | **Invalid.** Entries are compiled as `std::regex` (`JEventProcessorPODIO.cc:628-639`). A leading `*` is a regex_error. Use `.*` and `.*FarForwardZDC.*`. |
| R1 from commit `fdbb773d` vs R0 at the pin (item 8) | The PR base `66b8cf62` is **14 commits behind the pin**, including #3061 (HEXPLIT subcell raw-hit provenance), #3051 (calorimetry attenuation) and #3031 (PF move). "R1-from-parameters ≡ R1-from-commit on every ZDC collection" fails on the association collections, and R1-from-commit fails G4 against R0. R1 must be the PR's 3-file diff applied on the pin. |
| 26.06 MSF files in the 26.11 image (item 6) | Plausible. `ZDC_SiPMonTile.xml` last changed in #1070 (2026-04-19, 26.05.0), and the LYSO file in 2024, in epic up to 26.09. 26.10/26.11 are unverified, so check `git log` on the image's epic. podio reads older edm4hep through schema evolution. The campaign `reco` partner was made by a 26.06-era EICrecon, so the decisive comparison must be **RawHits/RecHits only** (cellID decode, counts, energy sum), never clusters. `{msf}/simulation-pipeline/configs` (item 5) does not exist in the checkout. The local files are named `msf_9x130_1000evt_NNNN`, not `msf_ev1000_NNNN` as in `zdc-setup.md:47`; check the farm names. |
| `epic_zdc_sipm_on_tile_only` valid | **Yes**: `configurations/zdc_sipm_on_tile_only.yml` exists and the zdc_pi0/lambda/photon CI uses it. It has **no LYSO**, see 2.5. `epic_zdc_lyso_sipm` is the matching config with the ECal. |
| G4 "non-ZDC collections byte-identical" with `zdc_owned_prefixes` | `FarForwardNeutralsReconstruction` also writes `ReconstructedB0EcalNeutrals`, `ReconstructedEcalEndcapPNeutrals` and `ReconstructedLFHCALNeutrals` (`reco.cc:245-246`). Any code-tier edit to that algorithm (listed as ZDC-owned, `zdc-problem.md:80`) can move them, and G4 "no exceptions" then rejects it. Either own those three outputs explicitly or treat the algorithm as shared. Also, the PR's CI shows Δ 840 on MT against Δ 148 on single-thread for the same sample, and Δ 40 on `tracking_only`: run G4 with `-Pjana:nthreads=1`, and find out in Step 0 which leaves the tracking_only Δ is. |
| Minor | `LambdaReconstruction::init` falls back to `m_zMax = 35800` (mm), whereas the detector constant is in cm (`LambdaReconstruction.cc:26-29`): a latent unit bug if the constant is missing. HEXPLIT gives S2 subcells hexagon dimensions (`HEXPLIT.cc:212-215`). These are findings for the report, not loop blockers. |

## 4. Loop-design critique

### 4.1 Step 0 items without a decisive outcome (or with an unreachable one)

- **Item 3**: "replace placeholder momenta with the Snakefile values" is impossible for D3 (2.3), and the D2 list lacks 275 GeV (`zdc_photon/Snakefile`).
  The generators default to `seed = 0`, which is clock-seeded (`gen_lambda_decay.cxx:49`), so the script must pass explicit seeds. Say so.
- **Item 6**: specify the comparison level (RecHits) and the tolerance, otherwise "agree" is a judgement.
- **Item 8**: unreachable (3, R1 base).
- **Item 9**: the switch test runs the neutron and photon *coefficients* on D1 (π⁰). There the neutron coefficient acts only on residual sums. Test each parameter on the dataset where it acts (D3 for the neutron coefficient, D2 for γ).
- **Item 11**: the Λ window is "±3σ of the R0 peak", but R0 on square tiles is expected to have no Λ peak (`zdc-problem.md:33-34`). There is no fallback, so the window is undefined.
- **Item 12**: no outcome is possible without patched benchmark copies (3); its outcome "plots exist" passes on empty PDFs.
- **Item 13**: "reproduced (or not)" has no criterion. Write the expected numbers from 2.4 first (fraction of single-column clusters with R1 > 0.9; φ within 5° of ±180° > 0.9).

### 4.2 Acceptance-rule loopholes (ways to win without better physics)

1. Widen `pi0Window`/`lambdaMassWindow` (owned -P parameters). Fix: freeze all LambdaReconstruction parameters through Phases 1 to 3. Window studies become a separate, user-approved family judged on truth-matched purity.
2. Inflate photon energies through the `a·E^b` refit to beat the IP-pointing bias (2.2). Fix: make S2 photon scale (|μ/E − 1| per momentum) a guard, and allow calibration refits only against D2/D3 truth, never against S4a.
3. Fragment more, so that combinatorics find a mass match (2.2). Fix: truth-matched S4a and the separation efficiency as selector; guard on mean ZDC "photons" per D4 event.
4. Self-certified G1 to G3: "explained by a mechanism the plots show" (`zdc-setup.md:120-121`) is judged by the agent that wants the win. Fix: numeric thresholds for G1 to G3, which the user sets at the Phase 1 checkpoint. The explanation must be the *pre-registered* hypothesis, with the predicted numbers.
5. Winner's curse on fixed seeds: 20 to 50 experiments selected on one 2000-event sample per point. Fix: a held-out D4/D1 seed set (independent npsim and generator seeds), reconstructed only at checkpoints. An accepted chain that does not reproduce there is reverted.
6. Choosing the band: a single-pair band (2.6). Fix: band = analytic binomial/fit error of the *paired difference*, with ≥ 3 seeds at Step 0 used only to check that the analytic error is honest.
7. S1a rewards "exactly two clusters" regardless of what they are. Make S1a truth-matched (two clusters, each ≥ 0.8 purity to a different photon).

### 4.3 Noise control

Replace the per-metric band with three things:
- a determinism check (same files twice, identical output, at Step 0 and after each rebuild);
- a paired test on identical events (McNemar for efficiencies, bootstrap over events for σ and μ);
- the held-out seed set at checkpoints.

Drop rule 8 or make it "repeat on the held-out seed". Run single-threaded or with ordered output for G4.

### 4.4 Checkpoint cadence and what the human must decide, and when

Five and ten experiments per checkpoint is fine for parameter work. The decisions below come too late in v1;
ask them at the **end of Phase 0**, BLOCKING:
1. Gun detector config: LYSO+SiPM (recommended) or SiPM-only, or both.
2. Primary selector: truth-matched separation efficiency (recommended) or S4a.
3. May LambdaReconstruction change at all, including the IP-pointing preselection, which is a physics change in a shared reco used by MSF?
4. G1 to G3 numeric thresholds, now that 2.4 says what G1 means.
5. Whether shared `ImagingTopoCluster` (BEMC/FHCAL users) or a switch of the ZDC to the Island chain is in scope.
6. Whether D6 contains background.

Phase 1's "is a φ collapse that is a geometry artifact acceptable?" is answered by 2.4. Replace it with decision 4.

### 4.5 Token burn

- Phase 1 "eight one-at-a-time experiments" adds the PR's *calibration* coefficients to R0 clustering. They were fitted on R1's columns, so the result is predictable garbage. Dissect the clustering parameters only (four runs: R0+each, R1−each), and treat calibration as a refit per clustering.
- The XY-distance experiments collapse to two discrete settings (2.1).
- Plots: generating every experiment's benchmark plots is CPU; *reading* them is the cost. Keep the setup's "once per milestone" rule and make the G1 to G3 diagnostics numeric (2.4), so that no G-explanation needs a plot.
- G4 on full DIS reconstruction for every parameter experiment is wasted CPU and log-reading. A ZDC-scoped -P cannot leak unless a factory prefix collides, and strictness 2 plus the parameter table proves that statically. Run full G4 for code experiments and at checkpoints.

### 4.6 Farm plan

- **Arrays.** `zdc-setup.md:145` says "one array per run, ≤ 200 tasks". Loop Phase 4 step 1 says one array per configuration: 3 configs × 2 energies × 100 files = 600 tasks, so three runs or three arrays. Reconcile the two.
- **Cost.** JANA runs only the factories that the requested collections need. Request only `MCParticles`, the ZDC chain, the four `Reconstructed*Neutrals` and the Λ collections. That skips tracking and cuts per-file cost by an order of magnitude. The B0/EEEMC/LFHCAL clustering still runs, because they are inputs (`reco.cc:244`).
- **Inputs.** The DD4hep inputs are 5 GB/file (`data.md`): reconstruct on the farm and pull only S5 numbers, as planned.
- **Combinatorics.** MSF events feed B0/EEEMC photons into the Λ γ pool (`LambdaReconstruction.cc:207-250`), which the ZDC-only guns never exercise. Make S5 report the ZDC-only and the all-calorimeter Λ separately.

## 5. Ranked changes for version 2

1. **MUST** — Setup, Scoreboard: replace S4a as selector with "S0: truth-matched separation efficiency on D4 (per true γ and n: best cluster purity ≥ 0.8 and ≥ 50 % of its deposited energy), per momentum"; keep S4a as reported outcome, truth-matched (Λ built from clusters associated to the true n, γ, γ).
2. **MUST** — Phase 0: add item "truth-cluster ceiling": replay FarForwardNeutrals+LambdaReconstruction offline on `HcalFarForwardZDCTruthClusters`, S4a vs true decay z per momentum; record the IP-pointing π⁰-window cap.
3. **MUST** — Setup, Acceptance: freeze `ReconstructedLambdas:*` parameters and the LambdaReconstruction source for Phases 1–3; add S2 photon scale (|μ/E−1| per momentum) and S3 raw-energy-sum to the guards.
4. **MUST** — Datasets: guns D1–D4 on `epic_zdc_lyso_sipm` (or both configs) after a BLOCKING Phase 0 question; D3 = npsim neutron gun scan 20–275 GeV in 4 mrad; D1 momenta matched to Λ-daughter π⁰ (20–70 GeV) plus the benchmark's 60–160.
5. **MUST** — Phase 0 item 8: "R1 = the PR's three-file diff applied to the pin (`git diff 66b8cf62 fdbb773d` → patch); R1-from-parameters must equal it on every ZDC collection".
6. **MUST** — `configs/experiments/*.yaml`: output_collections as regexes (`.*`, `.*FarForwardZDC.*`); `-Pjana:nthreads=1` for G4 runs.
7. **MUST** — Phase 0 item 12: "copy the four plot scripts to `scripts/7xx_benchmarks/` with the collection names of EICrecon main; decisive outcome: each output PDF has ≥ 1 non-empty histogram per momentum"; FROZEN keeps the submodule untouched.
8. **MUST** — Setup, Noise band: "band = analytic error of the paired difference on identical events (McNemar / event bootstrap); Step 0 runs 3 independent seeds at one momentum per gun only to validate it"; delete loop rule 8.
9. **MUST** — Setup: add a held-out seed set (D1h, D4h; fresh generator and npsim seeds) reconstructed only at checkpoints; an accepted change that fails there is reverted.
10. **MUST** — Setup, Acceptance: replace "explained in the ledger by a mechanism the plots show" with "within the numeric G1–G3 limits the user set at the Phase 0 checkpoint".
11. **SHOULD** — G1: add per-cluster distinct-(x,y) count, intrinsic θ, lateral width √λ2; write the 2.4 predictions into Phase 1 as hypotheses; shrink Phase 1 to clustering-only dissection (R0+each, R1−each).
12. **SHOULD** — Phase 2 backlog: drop "distance between 14.6 and 36.6 mm"; add `minClusterHitEdep` scan (0.5–4 MIP-equivalent per subcell) and `minClusterCenterEdep`; note the 24.4/48.8 mm steps.
13. **SHOULD** — Phase 3 candidates: put "feed `HcalFarForwardZDCIslandProtoClusters` (splitCluster=true) into the CoG" first; it exists at `ZDC.cc:206-226`.
14. **SHOULD** — Phase 0 item 7: if kept, parameters in dd4hep units as `vector<double>` of length 2 (or `vector<string>` evaluated by DD4hep); otherwise drop it and run the three distance settings as code-tier builds.
15. **SHOULD** — D5: size by measured R0 ZDC cluster count (≥ 2000 clusters per sample), not events; record clusters/event at Step 0.
16. **SHOULD** — G4: list `ReconstructedB0EcalNeutrals`, `ReconstructedEcalEndcapPNeutrals`, `ReconstructedLFHCALNeutrals` as owned outputs of the neutrals factory or mark the algorithm shared; full G4 only for code experiments and checkpoints.
17. **SHOULD** — Phase 0 item 6: "compare RawHits/RecHits (cellID decode, count, energy sum per event) only; tolerance: identical"; record whether the 2026-07 dd4hep used `bg_merged`; fix the `{msf}/simulation-pipeline/configs` pointer and the farm file-name pattern.
18. **SHOULD** — Scoreboard: add acceptance row (events with ≥1 HCal RecHit; truth daughters in face) and photon position resolution at the face.
19. **SHOULD** — Phase 4: one decision on arrays (600 tasks vs ≤200/run); restrict output collections so tracking is not run; report S5 ZDC-only and all-calorimeter Λ separately.
20. **COULD** — Item 9: drop the dump_flags search (strictness 2 already aborts on unknown names); keep inert-parameter switch tests on the dataset where each parameter acts.
21. **COULD** — Fix `zdc-problem.md:51` (`gammaZMax` = ZDC *centre* + 400 mm) and `:89` (not every value is a JANA parameter).
22. **COULD** — Record as findings (not loop work): `LambdaReconstruction` mm/cm fallback (`:26-29`), HEXPLIT S2 subcell dimensions (`:212-215`), stale benchmark collection names (an upstream PR to detector_benchmarks).
