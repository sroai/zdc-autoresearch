# Lesson: plots lapsed from Phase 4 on (2026-11-09)

work-common says every phase writes PNG plots to space/plots/phase{#}/. Phases 0–3 got them from 401 (the benchmark
plots of each row). Phase 4 switched to the slim template and dropped the benchmark guns, so 401 had nothing to plot,
and no phase script replaced it: Phase 4 wrote no plot, Phase 5 wrote four into slides/phase5/plots/, Phase 6 none. The
user found the empty folder.

Rule: a phase's plots come from a script that writes space/plots/phase{#}/ and runs after every verdict
(scripts/702_phase_plots.py for Phases 4 and 6; slides/phase5/make_phase5_plots.py writes space/plots/phase5/). A deck
reads its plots from there. STATUS.md's RESUME block names the plot command.
