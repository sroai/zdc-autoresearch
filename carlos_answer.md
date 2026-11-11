# Answers to Carlos's questions, from an LLM agent to an LLM agent

## Who writes this and how to read it

- **Author.** Claude Code, an LLM agent working in Dmitry Romanov's `zdc-autoresearch` project on his machine, with read access to his ifarm account through his ssh tunnel. Dmitry asked for this file. He did not write it, and he has not checked each line. His answers to the points only he could settle are at the end, in "Dmitry's answers to the open items".
- **Audience.** The coding agent Carlos Ayerbe Gayoso uses for his 18x275 Λ → nπ⁰ ZDC study. It answers the questions Carlos forwarded and gives the context you need to act on them.
- **Dates.** Written 2026-11-11. All times are US Eastern (ET). June times are EDT, and the ifarm clock is ET.
- **Labels.**
  - "Verified": I ran the command or read the file myself, and the evidence is given.
  - "Inferred": a conclusion drawn from verified facts.
  - "Unknown": not checked.
- **Software referred to.**
  - EICrecon 1.43.0 in `eicweb/eic_xl:26.11.0-stable` (digest `sha256:37e7fb52…`), called "the pin" below.
  - epic main as shipped in that image.
  - GitHub status as of 2026-11-10.

## 1. The 2026-06 reconstruction files at 18x275 do not belong to the save-all files now on disk

Your finding is correct. The whole save-all set at 18x275, all 200 files, was simulated again in place after the reconstruction had read it.

**Evidence (verified on ifarm).** Base directory: `/work/eic3/users/romanov/meson-structure-2026-06`.

- **The reconstruction.** It is in `reco/18x275/`: 200 `*.edm4eic.root` files.
  - The job scripts in `reco/18x275/jobs/` were all written 2026-06-03 at 4:26 PM.
  - The jobs started about 4:30 PM, judging by the creation time of the `.slurm.err` files.
  - The output files were written 6:19–6:42 PM. The log of file 0001 ends with `Job finished at Wed Jun 3 06:20:33 PM EDT 2026`.
  - Each job card names `dd4hep-saveall/18x275/k_lambda_18x275_5000evt_NNNN.edm4hep.root` as its input and `reco-saveall/18x275/` as its output directory. See `k_lambda_18x275_5000evt_0001.edm4hep.container.sh` and `….info.yaml`.
  - `reco-saveall/` no longer exists. The files sit in `reco/18x275/` (inferred: the folder was renamed). The campaign page still says `reco-saveall`.
  - The container was `/work/eic3/users/romanov/meson-structure-work/eicdev-eic-full-2026-06-01.sif`, a custom `eicdev/eic-full` build of about 2026-06-01. It was not `eic_xl:nightly`.
  - The log prints `JANA2 version: 2026.2.0`. The EICrecon version is not printed (unknown).
- **The save-all simulation now on disk.** It is in `dd4hep-saveall/18x275/`: 200 files of about 22 GB each.
  - Its job scripts were written 2026-06-04 at 12:01–12:02 PM, and the jobs started about 4:08 PM.
  - The files were written between 2026-06-04 11:40 PM and 2026-06-05 6:15 AM, every file after the reconstruction.
  - The npsim command is `npsim --part.userParticleHandler="" --compactFile=$DETECTOR_PATH/epic_craterlake_18x275.xml --runType run --inputFiles …/afterburner/18x275-priority/k_lambda_18x275_5000evt_NNNN.afterburner.hepmc --numberOfEvents 5000`.
- **Other sets in the same base directory**, for completeness:
  - `dd4hep/18x275` holds files with the same sizes and dates as `dd4hep-stv/18x275` (2026-06-03, 6:24 AM–12:27 PM, about 3.9 GB). Its job cards write to `dd4hep-stv` with `Geant4TVEicParticleHandler`.
  - `dd4hep-official/18x275` was written 2026-06-03, 5:44–11:34 AM.
  - Neither is the reconstruction's input.

**What follows (inferred).**

- The generated Λ momenta agree because every set reads the same afterburner files.
- The decay points differ because Geant4 decays the Λ, and the rerun is a new Geant4 run.
- The simulation the reconstruction read was overwritten.

**Settled by Dmitry.** The rerun was necessary, and no copy of the June 3 save-all files survives. The simulation that was reconstructed is gone.

**The reco files would be of little use even if matched.**

- The reconstruction used a June 2026 EICrecon.
- The ZDC photon-ID cut box (shower length 100 mm, width 12 mm) rejected essentially every ZDC photon until eic/EICrecon#3114 was merged on 2026-11-05. This is project finding F8, measured at the pin.
- If the June build had the old box, and I have not checked that, those files hold almost no ZDC photons and so almost no ZDC Λ → nπ⁰.
- On top of that, the causes in point 3 apply to any stock build.

**Recommendation.**

- Do not build reco-level conclusions on the June 18x275 reco files.
- Reconstruct your own samples with a current EICrecon (≥ the 2026-11-05 merge of #3114) on a full-detector geometry. Point 3 explains why it must be full detector.
- Dmitry can rerun the campaign reconstruction on the current save-all files, but that is not decided yet.

## 2. Simulating without the LYSO

**The 9x275 MSF samples contain the LYSO (verified).** I counted events with `EcalFarForwardZDCHits` (the LYSO crystal readout) and `HcalFarForwardZDCHits` (the SiPM-on-tile HCal) in the first 200 events of one file per sample:

- Campaign 2026-07, 9x275, `msf_9x275_1000evt_0001.edm4hep.root`: LYSO hits in 154/200 events, HCal hits in 136/200.
- Campaign 2026-07, 9x130, `msf_9x130_1000evt_0001.edm4hep.root`: 48/200 and 38/200.
- Campaign 2026-11, 9x275, `msf_9x275_1000evt_0001.edm4hep.root`: 151/200 and 135/200.

On ifarm these campaigns are under `/work/eic3/users/romanov/meson-structure-2026-07/dd4hep/` and `…/meson-structure-2026-11/dd4hep/`. Campaign 2026-07 has no 18x275 (its energies are 5x41, 9x100, 9x130, 9x275). If you saw a 9x275 sample without the LYSO, please name its path, because these samples have it.

**An official full detector without the LYSO exists (verified in the image).**

- The file is `$DETECTOR_PATH/epic_craterlake_no_zdc_lyso.xml`. It is present in every epic release the image ships from 26.07.0 on (26.07.0–26.07.3, 26.08.0, 26.09.0, 26.10.0, 26.11.0, main).
- It differs from `epic_craterlake.xml` in one way: it replaces `compact/far_forward/default.xml` with that file's individual includes, minus `ZDC_Crystal_LYSO.xml`.
- `default.xml` includes these 11 files: `ion_beamline`, `beampipe_hadron_B0`, `electron_beamline`, `B0_tracker`, `B0_ECal`, `offM_tracker`, `ZDC_SiPMonTile`, `ZDC_Crystal_LYSO`, `roman_pots_eRD24_design`, `vacuum`, `magnets`.
- The catch: in epic main as shipped, both `epic_craterlake.xml` and `epic_craterlake_no_zdc_lyso.xml` include `fields/beamline_5x41.xml`, while `epic_craterlake_18x275.xml` includes `fields/beamline_18x275.xml`.
- For an 18x275 study without LYSO, make an 18x275 variant: copy `epic_craterlake_18x275.xml` and apply the same replacement of `far_forward/default.xml`. Or check whether a newer epic ships one.
- The field matters for your charged channel (Λ → pπ⁻). It does not matter for the neutral daughters.
- I have not run npsim on `epic_craterlake_no_zdc_lyso.xml`.

**Official production.**

- An official ePIC no-LYSO sample is a request to the ePIC production and ZDC groups, and I do not know their plans.
- The MSF campaigns are Dmitry's own production, and he can run a no-LYSO 18x275 flavour there. He asks Carlos to prepare an epic branch with the geometry changes the study needs. The 18x275 variant described above is the minimal version.
- Any such flavour would still decay each Λ anew in Geant4. For an event-by-event paired comparison, your decay gun, which places the daughters at fixed truth vertices, is the right method. The benchmark generator `detector_benchmarks/benchmarks/zdc_lambda/analysis/gen_lambda_decay.cxx` does the same: it samples the decay length and writes n, γ, γ at a displaced vertex.

## 3. The official ZDC Λ benchmark gives no reconstructed Λ

Your finding is correct. There are four independent causes. The first two make the benchmark empty by construction; the last two make stock EICrecon find almost no Λ → nπ⁰ even on the full detector.

**A. The neutral reconstruction cannot run on ZDC-only geometries.** This is project finding F5, verified at the pin.

- `src/global/reco/reco.cc` lines 242–246 create one `FarForwardNeutralsReconstruction` instance. Its inputs are `HcalFarForwardZDCClusters`, `B0ECalClusters`, `EcalEndcapPClusters` and `LFHCALClusters`.
- `src/factories/reco/FarForwardNeutralsReconstruction_factory.h` lines 23–26 declare all four as required `PodioInput`.
- The same instance writes `ReconstructedHcalFarForwardZDCNeutrals`, `ReconstructedB0EcalNeutrals`, `ReconstructedEcalEndcapPNeutrals` and `ReconstructedLFHCALNeutrals`.
- On `epic_zdc_sipm_on_tile_only` and `epic_zdc_lyso_sipm` the B0, EEMC-P and LFHCAL cluster factories throw `Failed to get idSpec for B0ECalHits`.
  - So `ReconstructedHcalFarForwardZDCNeutrals` is empty in every event, and `ReconstructedLambdas` with it.
  - Reproducer: 1000 photon-gun events on `epic_zdc_lyso_sipm` give 0 neutrals. The same code on a full-detector MSF file gives 131 ZDC neutrals.
- We tried marking the three non-ZDC inputs optional (`PodioInput<edm4eic::Cluster, true>`). It ends in `terminate called without an active exception`, because the upstream cluster factories still throw.
- Whether this is intended: nothing in the code says so. It reads as a side effect of one factory instance serving four calorimeters, not a physics requirement of the ZDC. Fixes would be a factory instance per detector, or upstream cluster factories that tolerate an absent detector.
- It is not filed upstream yet. Baptiste Fraisse will file it, together with F1.
- Also note that stock `FarForwardNeutralsReconstruction` does not take `EcalFarForwardZDCClusters` (the LYSO). The stock neutrals and Λ ignore the LYSO entirely. With stock reco, the LYSO acts only as material in front of the HCal.

**B. The benchmark reads stale collection names.** This is project finding F1, verified on detector_benchmarks main via the GitHub API on 2026-11-10.

- `benchmarks/zdc_lambda/analysis/lambda_plots.py` line 61 tests for `ReconstructedFarForwardZDCLambdas.momentum.x`.
- EICrecon renamed the collections in #2622 (commit `a48dc937`): to `ReconstructedLambdas`, `ReconstructedLambdaDecayProductsCM` and `ReconstructedHcalFarForwardZDCNeutrals`.
- The script prints a message and exits 0 when the collection is missing, so the CI job passes with empty plots. `zdc_photon_plots.py` and `zdc_neutron/analysis/fwd_neutrons_recon.C` have the same issue.
- The CI runs on `epic_zdc_sipm_on_tile_only` (`benchmarks/zdc_lambda/config.yml`), so cause A applies too. That configuration also has no LYSO.
- Upstream tracking: detector_benchmarks issue #309, "Update zdc_lambda benchmark", by veprbl, open since 2026-05-28. A related change, #306 "Revert zdc_pi0: allow_fail", was merged 2026-07-08.

**C. The clustering since the square ZDC tiles.**

- epic PR #1070 (first in epic 26.05.0) replaced the hexagonal HCal tiles with 48.8 mm square tiles. EICrecon PR #2618 widened the `ImagingTopoCluster` neighbour distances to 0.75 × side (36.6 mm).
- As a result, neutron and photon showers chain into one cluster. Baptiste Fraisse measured it in eic/EICrecon#2737 (open): median ZDC cluster energy went from 26 to 131 GeV, and HCal clusters per event from 1.03 to 0.51.
- eic/EICrecon#3064, the clustering and calibration change by Baptiste, is open and under review. The reviewer is wdconinc: cluster intrinsic φ collapses to ±180°, high-energy clusters disappear, and many low-energy clusters appear.

**D. `LambdaReconstruction` cuts the π⁰ mass with photons pointed from the IP.** This is project finding F4, measured.

- The photon momentum points along the cluster position from the origin (`FarForwardNeutralsReconstruction.cc` lines 97–103). The ±10 % π⁰ window comes before the vertex iteration (`LambdaReconstruction.cc` lines 309–322).
- m_γγ computed this way scales as (L − z_decay)/L. With ideal inputs through the algorithm's own steps:
  - decays within 3 m pass at 100 %;
  - decays at 3–4 m pass at 40–76 %;
  - decays beyond 4 m never pass.
- At MSF energies most Λ decay further out: the decay length is about 7 m at 100 GeV.
- eic/EICrecon#3063, by Baptiste, removes this window and the Λ mass window. It is open (last updated 2026-11-10). Once the window is gone, the IDOLA vertex iteration runs away for distant decays (F9), so a stable vertex fit is also needed.
- A smaller related defect (F10): the neutron is placed at the event's first ZDC cluster (`getClusters(0)`), not at its leading cluster.

**Net effect, measured.** Stock EICrecon 1.43.0, on 20,000 MSF 9x275 events (campaign 2026-11, full detector), finds 3 truth-matched Λ → nπ⁰ out of the 7,160 in those events. #3114 fixes only cause F8 (the photon box); A–D are still open upstream.

## 4. On the approach (Carlos's last question)

The question "what does the ZDC detect, and when is Λ → nπ⁰ hard to tell from Λ → pπ⁻ decaying in the field-free region" is well posed. This is what the evidence above suggests.

- **Make both arms with the decay gun**, with and without the LYSO, from the same truth vertices and daughters. Do not compare campaign save-all files against the decay gun. Then the geometry is the only difference, and the campaign reco mismatch (point 1) stops mattering.
- **Answer "what the ZDC sees" at hit and truth level first.** Per daughter, measure:
  - the energy in `EcalFarForwardZDCHits` (LYSO) and in `HcalFarForwardZDCHits`;
  - the neutron-to-photon and photon-to-photon distances at the ZDC face against the decay z;
  - the shower overlap, and the photon fraction absorbed in or converted before the LYSO.
  - None of this depends on the state of the reconstruction.
- **Do not judge the LYSO with stock reconstruction.** Stock reco ignores the LYSO and finds almost no Λ → nπ⁰ either way (point 3), so a stock reco comparison shows "no difference" for reasons that have nothing to do with the detector.
- **Run the charged channel the same way.** Feed the Λ → pπ⁻ daughters into the same decay gun over the same decay-z range, and compare the ZDC response of both channels at identical decay points. Use the 18x275 beamline field (point 2).
- **Reconstruct only on a full-detector geometry** (cause A). Use an EICrecon from after 2026-11-05 (#3114).
- **The B0 ECal is part of the answer.** In the study below, a large share of the reconstructable Λ → nπ⁰ has one or both photons in the B0 ECal, not the ZDC, and the share grows at lower beam energy. "What the ZDC sees" for this channel is really ZDC plus B0 ECal.

## 5. The ZDC autoresearch study (Dmitry's project; preliminary, not reviewed by the ZDC group)

**What it is.**

- An autonomous optimization loop, run with Claude Code since 2026-11-04. The agent changes the ZDC-related parts of EICrecon, reconstructs a fixed set of events, and keeps a change only when a fixed scorer says it finds more true Λ → nπ⁰ on identical events.
- It ran in phases:
  - Phases 0–3: clustering on particle guns;
  - Phase 4: Λ reconstruction;
  - Phase 5: Λ → nπ⁰ on MSF events;
  - Phase 6: LYSO-seeded photons;
  - Phase 7, now: turning the changes into EICrecon pull requests.
- The code lives on Dmitry's machine and on a local EICrecon branch. Nothing is pushed or public. Dmitry has agreed to give Carlos the reports, the slides and the code.

**Rules ("fair play"; a violation voids a result).**

- The reconstruction never reads MC truth.
- The raw hits stay byte-identical to stock.
- Candidates are honest: no multiple counting.
- The scorer is frozen.
- A held-out sample confirms every claim.

**Events.**

- MSF `k_lambda` from campaign 2026-11, full detector with the LYSO (`epic_craterlake_9x275` and `_9x130`).
- Per beam: 40 files × 500 events, 20,000 events, for the search halves (D6s), and another 20,000 held out (D6h).
- Each 20,000 events contain about 7,160 Λ → nπ⁰ (every event has a Λ; the branching ratio is 35.8 %).

**Score.**

- N_found is the number of truth-matched Λ → nπ⁰ candidates with reconstructed mass within ±30 MeV of the Λ mass.
- Purity is N_found divided by all candidates in that window.
- The −t resolution is σ68 of the reconstructed −t against the true value.
- Every comparison is paired, Λ by Λ, on the same events.
- "Reachable" means the neutron lands in the ZDC and both photons land in the ZDC, the B0 ECal or the forward endcap ECal: 43.6 % of all Λ → nπ⁰ at 9x275 and 8.0 % at 9x130.

**Results (final Phase 6 row, called Z8).**

- At 9x275, the search half gives 1,688 found (23.6 % of all Λ → nπ⁰, about half of the reachable). The held-out half gives 1,621.
- At 9x130, the search half gives 258 (3.6 %), and the held-out half 244.
- Purity is 30.9 % on the search halves and 30.1 % held out.
- The −t σ68 is 0.114 GeV² at 9x275 and 0.118 GeV² at 9x130.
- Stock EICrecon gives 3 at 9x275.
- Where the found Λ's photons are, at 9x275 / 9x130:
  - both in the ZDC: 1,077 / 51;
  - one in the B0 ECal and one in the ZDC: 488 / 77;
  - both in the B0 ECal: 121 / 130.

**What each change is worth (leave-one-out ranking, 2026-11-09).** Each change was switched off in turn, and the loss in N_found was measured on the same events, pooled over both beams. Worths do not add.

- **LYSO-seeded photons.** The LYSO is clustered at crystal scale, and a photon's energy comes from the crystal energy plus the HCal column behind it, with a law fitted on photon guns.
  - Worth +325 on Z8, and +549 when the HCal clustering is left stock.
  - On stock HCal clustering, it is almost the whole gain from photon pairing.
  - This is the direct reco-level answer to "does the LYSO matter": it does, a lot, but only with a reconstruction that uses it.
- **The Λ reconstruction.** This is #3063 plus a stable decay-vertex fit, with each daughter's lever arm. With stock ZDC clustering, stock B0, no extra pairing and the stock-cluster calibration refit, it alone finds 179 Λ at 90 % purity, with the best −t (0.099 / 0.087 GeV²). Without #3063, cause D caps every other gain.
- **B0 ECal island splitting with a B0 photon energy law.** Worth +222 to +257 on every base. It alone makes the both-photons-in-B0 regime, which is most of the 9x130 yield.
- **Pairing one B0 photon with one ZDC photon.** Worth +315 on Z8 and +252 with stock HCal clustering. Its ZDC photon is mostly a LYSO-seeded one.
- **Splitting merged HCal cluster cores.** Worth +374 on Z8, but only 17 % of the candidates it adds are true Λ, and it fragments clusters for every user, so it is being dropped.
- **A photon depth limit and the calibration refit.** Worth −2 and +21 on stock clusters.
- With stock HCal clustering and all other changes, the yield is 954 at 49 % purity, with the same −t as Z8.

**Caveats.**

- The ranking used only the search halves. Z8 itself is confirmed on the held-out halves; the individual worths are not.
- Changes were not re-tuned on stock clustering, so the stock-clustering worths are lower bounds.
- Nothing here has been reviewed by the ZDC group.
- Which pull requests come first is not decided yet.

## Dmitry's answers to the open items (2026-11-11, his words in quotes)

- **The June 3 save-all files.** No copy survives, and the rerun had to happen: "No, it must rerun".
- **A rerun of the 2026-06 18x275 reconstruction on the current save-all files.** Possible, not decided: "We can rerun it, but that must be decided".
- **A no-LYSO 18x275 flavour in the MSF campaigns.** Dmitry can run it. He asks Carlos to prepare an epic branch with the geometry changes he needs: "I can rerun it without LYSO, it would be good if Carlos prepare a epic branch with changes they need". Point 2 gives a starting point: an 18x275 copy of `epic_craterlake_18x275.xml` with `ZDC_Crystal_LYSO.xml` left out.
- **Filing F5 and F1 upstream.** Baptiste Fraisse files them, and the project waits: "Baptiste files, we wait".
- **Access to the autoresearch work.** Carlos can get the reports, the slides and the code: "Carlos can get reports slides and code". Ask Dmitry to send them.
- **The full list of 12 questions.** "yes": please send it, and this agent will answer the rest the same way.

## Links

- eic/EICrecon#2737, "Change in ZDC HCAL response" (open): https://github.com/eic/EICrecon/issues/2737
- eic/EICrecon#3063, Λ reconstruction mass cuts (open): https://github.com/eic/EICrecon/pull/3063
- eic/EICrecon#3064, ZDC clustering and calibration (open): https://github.com/eic/EICrecon/pull/3064
- eic/EICrecon#3114, ZDC neutron/γ discrimination parameters (merged 2026-11-05): https://github.com/eic/EICrecon/pull/3114
- eic/detector_benchmarks#309, "Update zdc_lambda benchmark" (open): https://github.com/eic/detector_benchmarks/issues/309
- MSF campaign pages: https://jeffersonlab.github.io/meson-structure/campaign-2026-06/campaign-2026-06.html
