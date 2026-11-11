Hi Carlos,

Thanks for the detailed note. Your agent is right on both technical points, and I checked the files myself. Some of your questions overlap with an automated study of the ZDC reconstruction I have been running; I describe it in point 5. In your order:

1. The 2026-06 save-all and reco files at 18x275 do not match

Correct, and it comes from how I ran the campaign. On ifarm (times ET):

- The reconstruction ran on June 3. Its 200 jobs were created at 4:26 PM, and the outputs were written 6:19–6:42 PM. The job cards read dd4hep-saveall/18x275/... and wrote to reco-saveall/; those files now sit in reco/18x275.
- Then all 200 dd4hep-saveall/18x275 files were simulated again in place. The jobs were created June 4 at noon, and the files were written between June 4, 11:40 PM and June 5, 6:15 AM.
- The afterburner input is the same, so the generated Λ momenta agree. It is a new Geant4 run, so the decay points differ. To your question: all 200 files were regenerated, and the files the reconstruction read were overwritten. [Dmitry: confirm no copy survives elsewhere; add the reason for the rerun if you want]

The June reconstruction also used an EICrecon from about June 1 (eicdev-eic-full-2026-06-01.sif). That build predates the ZDC photon-ID fix eic/EICrecon#3114 (merged November 5). If its photon cut was the old one, it rejected almost every ZDC photon, so even a matched June reco would contain almost no ZDC Λ → nπ⁰. I would not spend time on those files. [Dmitry: offer to rerun the 18x275 reco on the current save-all files with a current EICrecon, or leave it to Carlos's own decay-gun samples]

2. A sample without LYSO

- The MSF files I have at 9x275 do contain the LYSO, both from campaign 2026-07 and from 2026-11: EcalFarForwardZDCHits is filled in about three quarters of the events. Which 9x275 sample did you see without it?
- epic ships a full detector without the LYSO, epic_craterlake_no_zdc_lyso.xml, in every release since 26.07.0. One catch: it uses the default craterlake beamline settings. In the copy I checked (epic main in eic_xl:26.11.0-stable), that means fields/beamline_5x41.xml. For 18x275, check the field and swap in the 18x275 settings before using it.
- Whether official production adds a no-LYSO sample is a question for the ePIC production group and the ZDC group. In the MSF campaigns, which I run, a no-LYSO 18x275 flavour is cheap: the same afterburner files through npsim with the other compact file. [Dmitry: decide whether to offer this] It would not give you identical decays event by event, though, because Geant4 decays the Λ again in each run. For a paired comparison your decay gun is the better tool.

3. The ZDC Λ benchmark gives no Λ

Correct. There are three separate reasons, all checked at EICrecon 1.43 in early November.

- Geometry. One FarForwardNeutralsReconstruction instance (in src/global/reco/reco.cc) builds the neutrals of the ZDC, the B0 ECal, the forward endcap ECal and the LFHCAL together, and it requires all four cluster inputs.
  - On the ZDC-only geometries the B0, endcap and LFHCAL cluster factories throw ("Failed to get idSpec for B0ECalHits"). Those geometries are epic_zdc_sipm_on_tile_only (the benchmark's) and epic_zdc_lyso_sipm.
  - So the ZDC neutrals, and the Λ with them, are empty in every event.
  - I don't think this is meant as a requirement. It is a side effect of one factory serving four calorimeters. Marking the three inputs optional does not help, because the upstream factories still throw.
  - It is not filed upstream yet. [Dmitry: say who files it]
  - Until it is fixed, reconstruct on a full-detector geometry.
- Collection names. The benchmark's lambda_plots.py still reads ReconstructedFarForwardZDCLambdas, which eic/EICrecon#2622 renamed to ReconstructedLambdas. The script exits 0 when the collection is missing, so the CI page shows nothing without failing. detector_benchmarks issue #309 ("Update zdc_lambda benchmark") has been open since May.
- Physics. Even on the full detector, stock EICrecon finds almost no Λ → nπ⁰. At EICrecon 1.43, before #3114, it finds 3 of the 7,160 Λ → nπ⁰ decays in 20,000 MSF 9x275 events. #3114 fixes only the photon cut. Two other causes are untouched by it and still open:
  - Since the square ZDC tiles (epic 26.05), the clustering merges the neutron and photon showers (eic/EICrecon#2737; Baptiste's #3064 is under review).
  - LambdaReconstruction cuts on the π⁰ mass computed with photons pointed from the IP. That removes most Λ decaying beyond about 3.6 m from the IP, and all beyond 4 m. Baptiste's #3063 removes the cut and is still open.

Also, the stock neutral reconstruction does not use the LYSO clusters at all. Its four inputs above are the only ones.

4. Your approach

I think it makes sense. Some suggestions:

- The decay gun built from the truth vertices and daughters is the right tool for a paired comparison. The benchmark's gen_lambda_decay.cxx does the same thing (it decays the Λ in the generator at a sampled vertex).
- I would make both arms with the decay gun, with and without the LYSO, instead of comparing the campaign save-all files against the decay gun. Then the geometry is the only difference, and you no longer depend on the campaign reco.
- The question "what does the ZDC see" is best answered at hit and truth level for now. That means the energy each daughter leaves in the LYSO and in the HCal, the neutron-to-photon distances at the ZDC face against the decay z, and how often the showers overlap. None of that depends on the state of the reconstruction.
- At reco level, stock EICrecon cannot answer the LYSO question yet. It ignores the LYSO clusters, so the LYSO only shows up as material in front of the HCal, and it finds almost no Λ → nπ⁰ either way. A reco comparison today would show no difference for the wrong reason.
- For Λ → pπ⁻ decaying in the field-free region, the same decay gun with the charged daughters gives you the ZDC response of both channels at the same decay points. That is the direct way to see when the two channels look alike.
- Use a full-detector geometry for anything that goes through the reconstruction (point 3).

5. My autoresearch study of the ZDC reconstruction (preliminary)

Since early November I have been running "autoresearch" on the ZDC reconstruction. It is an autonomous loop in which an AI agent (Claude Code) changes the ZDC part of EICrecon and reconstructs a fixed set of MSF events. It keeps a change only when the change finds more true Λ → nπ⁰ on the same events. Rules keep it honest:

- The reconstruction never reads truth, and the raw hits stay identical to stock.
- The scorer is frozen. A Λ → nπ⁰ counts when its candidate matches the true decay and its mass is within ±30 MeV.
- Every change is a paired test on identical events, and the gain is confirmed on a second, held-out set of events.

The events are MSF k_lambda at 9x275 and 9x130 (campaign 2026-11, full detector with the LYSO). There are 20,000 per beam for the search and 20,000 per beam held out, and each 20,000 contain about 7,160 Λ → nπ⁰.

What it found so far:

- Stock EICrecon finds 3 of these Λ at 9x275.
- The best version so far finds 1,688 at 9x275, 24 % of all Λ → nπ⁰ (1,621 on the held-out events). At 9x130 it finds 258, 3.6 % (244 held out).
  - Purity, the true Λ over all candidates in the mass window, is 31 %.
  - The −t resolution (σ68) is 0.11–0.12 GeV².
- Only part of the Λ → nπ⁰ can be reached at all: the neutron must land in the ZDC and both photons in the ZDC, the B0 ECal or the forward endcap ECal. That is 44 % at 9x275 and 8 % at 9x130, so the best version finds about half of what is reachable.
- Where the photons of the found Λ are seen, in the best version:
  - 9x275: both photons in the ZDC 1,077; one in the B0 ECal and one in the ZDC 488; both in the B0 ECal 121.
  - 9x130: 51, 77 and 130.
  - So for Λ → nπ⁰, "what the ZDC sees" is really the ZDC plus the B0 ECal, and the B0 ECal's share grows at lower beam energy.
- Which changes matter: I switched each change off in turn and measured the loss on the same events.
  - The LYSO as the photon detector. Photons seeded from the crystal hits are worth +325 Λ in the best version, and +549 when the HCal clustering stays stock.
  - The Λ reconstruction itself. Baptiste's #3063 plus a stable decay-vertex fit, with everything else stock, finds 179 Λ at 90 % purity, with the best −t resolution of any version.
  - The B0 ECal. Splitting its islands and recalibrating its photons is worth +222 to +257.
  - Pairing one photon from the B0 ECal with one from the ZDC is worth +315 (+252 with stock HCal clustering). The ZDC photon in these pairs is mostly a crystal photon.
  - Splitting merged HCal cluster cores is worth +374, but only 17 % of the Λ it adds are true, and it fragments the clusters for every user. I am dropping it.

For your study, this means the LYSO matters a lot at reco level, but only with a reconstruction that uses it. Stock EICrecon does not.

None of this has been reviewed by the ZDC group yet. The next step is a few EICrecon pull requests with the changes that pay off. I can send you the report and the slides.

People

- The ZDC reconstruction: Baptiste Fraisse (#2737, #3063, #3064, #3114).
- EICrecon reviews: wdconinc on GitHub.
- detector_benchmarks: veprbl on GitHub (#309).

Yes, please send the full list of 12 questions.

Cheers,
Dmitry

Links:
- https://github.com/eic/EICrecon/issues/2737
- https://github.com/eic/EICrecon/pull/3063
- https://github.com/eic/EICrecon/pull/3064
- https://github.com/eic/EICrecon/pull/3114
- https://github.com/eic/detector_benchmarks/issues/309
