Lesson: a full reco is ~63 GB per experiment; /data filled (1.6 TB) after 13 reco rows and failed four runs at once.

What bit: on 2026-11-05 17:37 UTC /data reached 100 % with 865 GB of program reco outputs (R0 102 GB, R1 92, R2 87,
P1a–P1f, E02/E03 63 each, L01 partial). E02/E03 analyses (130's G4 compare), L01's reco (4 D6a_9x275 files) and
R2's S5 failed with ENOSPC; the S5 logs were empty files, so the failure was silent until the logs were read.
Why: every experiment writes all collections (`podio:output_collections=.*`); D5 (26 GB) and D6a_9x275 (17 GB) are
mostly non-ZDC collections, kept for the G4 compare. No retention rule existed.
Rule: D-user-19 — full ROOT only for R0, R1, R2 and the current best; delete a rejected experiment's
`*.edm4eic.root` right after its verdict is written. Before a launch, check `df -h /data` against ~65 GB per
experiment (plus D6a when the experiment includes it) and do not launch a pair with less than 150 GB free.
An empty log after a background chain is a failure until shown otherwise.
Second trap: eicrecon exits 0 when ROOT writes fail on a full disk, so 120's `&& mv` renamed truncated outputs as complete
(L01: 8 files at 1–34 % of R0's size, no per-file JSON) and a rerun skips them as "exists". After any ENOSPC, compare
every output's size with R0's counterpart and require its `<stem>.json` before analysing.
