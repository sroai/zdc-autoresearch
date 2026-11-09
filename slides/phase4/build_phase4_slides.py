#!/usr/bin/env python
"""Build phase4_bar_fight.pptx (+ .pdf): Phase 4 of the ZDC autoresearch loop, the Λ bar fight (loop v4,
D-user-33), one slide per try (D-user-36), diagrams for structural changes.

Numbers load at build time; a missing file leaves "pending" in its place, so the deck always builds:
  space/perf/headline.csv              S4a_tm and S4o per thrown Λ → nπ⁰, mean over 100–275 GeV and at 275 GeV (441)
  space/perf/verdict-<row>.json        the Phase 4 verdict of a try (461): pooled gained / lost / z, fair play
  space/perf/fair-play-<row>.json      F1–F3 of a row or control (460)
  space/perf/checkpoint-heldout-*.json the held-out D4h checkpoints (462)
  space/perf/msf-*-D6a_*.json          S5 on MSF events (402)
  space/perf/lambda-losses-X9_*.json   where the final row loses its events (470)
  space/perf/cluster-containment-phase4.json  photon / neutron best-cluster purity and containment, X5 → X9 (410 tables)
The close-out slides hardcode the diagnostics of 2026-11-08T09:50Z (runlog) and the predictions of the ledger, with
`# source:` comments.
The try texts (mechanism, prediction) are the TRIES list below, written before each launch; the prediction
line is the ledger's (space/EXPERIMENTS.md).

Rebuild:  uv run --no-project --with python-pptx python slides/phase4/build_phase4_slides.py [--no-pdf]
"""
import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from pptx.enum.dml import MSO_LINE_DASH_STYLE  # noqa: E402
from slide_kit import *  # noqa: E402,F401,F403

# ---- palette B (the autoresearch deck family, as slides/build_autoresearch_retro_v1_slides.py) ----------------
INK    = RGBColor(0x22, 0x26, 0x33);  MUTED = RGBColor(0x60, 0x66, 0x76)
TEAL   = RGBColor(0x18, 0xB8, 0xA6);  TEAL_FILL   = RGBColor(0xD9, 0xF6, 0xF2)
PURPLE = RGBColor(0x7C, 0x4D, 0xD8);  PURPLE_FILL = RGBColor(0xEF, 0xE8, 0xFB)
BLUE   = RGBColor(0x2E, 0x6B, 0xE6)
ORANGE = RGBColor(0xEE, 0x85, 0x4A);  ORANGE_FILL = RGBColor(0xFD, 0xEC, 0xDF)
GREEN  = RGBColor(0x2F, 0x9E, 0x62);  GREEN_FILL  = RGBColor(0xDF, 0xF3, 0xE8)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
GREY_BAR = RGBColor(0xB8, 0xBD, 0xC8); GREY_FILL = RGBColor(0xF1, 0xF3, 0xF6)

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PERF = os.path.join(REPO, "space", "perf")
OUT = os.path.join(HERE, "phase4_bar_fight.pptx")
PENDING = "pending"
CEILING = 14.1      # mean over 100–275 GeV (D-user-20, 414: perfect separation, P1b resolution, stable vertex)
CEILING_275 = 27.8  # at 275 GeV (same source); the acceptance is 16.9 % / 32.6 %
missing = []


def load_json(name):
    path = os.path.join(PERF, name)
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def headline():
    try:
        with open(os.path.join(PERF, "headline.csv")) as fh:
            return {r["row"]: r for r in csv.DictReader(fh)}
    except OSError:
        return {}


HEAD = headline()


def num(row, col):
    v = (HEAD.get(row) or {}).get(col)
    try:
        f = float(v)
        return None if f != f else f
    except (TypeError, ValueError):
        return None


def pct(v, digits=2):
    return PENDING if v is None else f"{v:.{digits}f} %"


VERDICT_COLOR = {"ACCEPTED": (GREEN, GREEN_FILL), "INCONCLUSIVE": (ORANGE, ORANGE_FILL),
                 "REJECTED": (MUTED, GREY_FILL), "FOUL": (ORANGE, ORANGE_FILL), PENDING: (MUTED, GREY_FILL)}

# ---- the tries (D-user-36): one entry per try, written before its launch -------------------------------------
# chain: the stages of the ZDC Λ chain that the try changes (keys of CHAIN), for the highlight strip.
TRIES = [
    {"id": "X1", "row": "X1_offline_chain", "best": "R1_pr3064",
     "title": "X1 — the offline Λ chain built into EICrecon",
     "change": ["R1 clustering (PR 3064) with neighbourLayersRange 1 (P1d)",
                "P1d's calibration refit on the D2 / D3 guns: photon 3.90·E^0.876, neutron 8.06·E^0.700 "
                "(PR 3064's laws overestimate photons 4.4× and neutrons 1.7× at 275 GeV)",
                "every γγ pair with every neutron goes through the vertex fit; the best fitted π⁰ and Λ masses win",
                "stable vertex: depth by bisection along the momentum-weighted slope (B9d)",
                "neutron position at its leader cluster (B9e)"],
     "chain": ["topo", "neutrals", "lambda"],
     "prediction": "1.5 % mean, 3.0 % at 275 GeV per thrown (R1's offline tagged refit: 1.64 / 3.07 %; "
                   "in-chain pairing loses events where truth chose the triplet offline)",
     "flow": True},
    {"id": "X2", "row": "X2_lambda_pairing", "best": "X1_offline_chain",
     "title": "X2 — the photon pair chosen by the Λ hypothesis in the ZDC neutrals",
     "change": ["X1 finds the true γγ pair in about half of the events where one exists (471 on X1's events)",
                "tagged clusters the pair leaves out are mostly neutron fragments: their energy belongs to the neutron",
                "for every pair of tagged clusters: neutron = every other cluster (energy sum, leader position)",
                "rank by fitted π⁰ and Λ mass χ² plus the Λ decay-depth density (cτ = 78.9 mm)",
                "only the chosen pair is written as photons; energies are never rescaled"],
     "chain": ["neutrals"],
     "prediction": "2.84 % mean, 5.45 % at 275 GeV per thrown (offline emulation of the rule on X1's events, "
                   "which reproduces X1's own count at every momentum)",
     "flow": True},
    {"id": "X3", "row": "X3_pairing_weights", "best": "X2_lambda_pairing",
     "title": "X3 — the Λ-pairing ranking weights",
     "change": ["X2 ranks pairs by (Δm_π⁰ / 0.1 m_π⁰)² + (Δm_Λ / σ_Λ)² + w · depth term",
                "X2: σ_Λ = 111 MeV (0.1 m_Λ), w = 1; X3: σ_Λ = 40 MeV (about the mass resolution), w = 1.5",
                "chosen at the centre of a plateau in a 32-point grid on X1's events (471): +12 % at every momentum",
                "both are parameters now: lambdaPairingLambdaSigma, lambdaPairingDepthWeight",
                "D4h at checkpoint 1 tests the D4-chosen weights"],
     "chain": ["neutrals"],
     "prediction": "3.24 % mean, 5.98 % at 275 GeV per thrown (X2 scaled per momentum by the grid)"},
    {"id": "X4", "row": "X4_photon_depth", "best": "X3_pairing_weights",
     "title": "X4 — a depth limit on the photon tag (as set, 1141 mm)",
     "change": ["true-photon clusters sit at 126 mm median depth past the ZDC face, other tagged clusters at 280 mm",
                "intended: photon candidates within 225 mm of the face (gammaZMaxOffset 400 → 225)",
                "the offset is added to HcalFarForwardZDC_SiPMonTile_r_pos, the ZDC centre (face + 916 mm)",
                "so the limit landed at 1141 mm (stock: 1316 mm, no effective depth cut)",
                "the prediction failed; X5 sets the limit at the face as intended"],
     "chain": ["neutrals"],
     "prediction": "4.31 % mean, 7.96 % at 275 GeV per thrown (471 at 225 mm past the face) — failed: mechanism mis-set"},
    {"id": "X5", "row": "X5_photon_depth_face", "best": "X4_photon_depth",
     "title": "X5 — photon candidates within 225 mm of the ZDC face",
     "change": ["gammaZMaxOffset = 225 − 916.4 = −691.4 mm, so the depth limit sits 225 mm past the front face",
                "fewer neutron fragments compete as photon candidates in the Λ pairing",
                "the excluded clusters join the neutron, whose energy becomes more complete",
                "chosen at the centre of the 200–225 mm plateau of 471 on X1's events",
                "a parameter on X3's build; no new code"],
     "chain": ["neutrals"],
     "prediction": "4.31 % mean, 7.96 % at 275 GeV per thrown (471, depth 225 mm, neutron holding every non-pair cluster)"},
    {"id": "X6", "row": "X6_zdc_face", "best": "X5_photon_depth_face",
     "title": "X6 — the vertex range ending at the ZDC front face",
     "change": ["LambdaReconstruction and the pairing searched the decay vertex up to the ZDC centre (front + 916 mm)",
                "X6 ends the vertex range and the decay-depth density at the front face (35.8 m)",
                "the photon depth limit stays 225 mm past the face",
                "three parameters on X5's code; no new code"],
     "chain": ["neutrals", "lambda"],
     "prediction": "a small gain: 4.40 % mean, 8.1 % at 275 GeV per thrown"},
    {"id": "X7", "row": "X7_core_split", "best": "X5_photon_depth_face",
     "title": "X7 — photon cores split from the ZDC clusters, lower cluster floor",
     "change": ["with X5, only 28 % of D4 events have three clean clusters; photons sit inside the neutron's cluster",
                "each imaging cluster is split between its shallow cores (≥ 5 MeV, first 4 layers, 50 mm apart) and one deep region",
                "hits join the region of their most energetic neighbour; deep showers stay whole",
                "cluster floor 50 → 20 MeV recovers low-energy photons with no cluster",
                "calibration refit on D2 / D3 for this clustering (photon 4.50·E^0.848, neutron 6.21·E^0.740)"],
     "chain": ["topo", "neutrals"],
     "prediction": "6.4 % mean, 11.8 % at 275 GeV per thrown (two-file scans: +46–48 %)",
     "flow": True},
    {"id": "X8", "row": "X8_core_depth_centroid", "best": "X7_core_split",
     "title": "X8 — photon cores limited to 5 layers, neutron at its centroid",
     "change": ["X7's photon clusters stay impure in 27 % of events; a core radius moved no hit: cores are narrow columns",
                "the contamination is neutron energy deeper in the photon's column: a core keeps only its first 5 layers",
                "the ZDC neutron sits at the energy centroid of its clusters, in the neutrals and in the pairing",
                "photon calibration refit for truncated cores: 3.95·E^0.938",
                "plateau over 4–6 layers in the scans; the centroid alone matched 471's prediction"],
     "chain": ["topo", "neutrals"],
     "prediction": "7.4 % mean, 14.0 % at 275 GeV per thrown (two-file scans, X7's calibration)"},
    {"id": "X9", "row": "X9_pairing_photon_depth", "best": "X8_core_depth_centroid",
     "title": "X9 — the photons' depth as a soft term of the Λ pairing",
     "change": ["inside the 225 mm limit, true photons still shower shallower than tagged neutron fragments",
                "each pair's score gains 1.0 × (depth₁ + depth₂) / 100 mm",
                "the pairing emulation on X8's clusters reproduces X8 within 3 events and reaches 83 % of the oracle",
                "weights 0.5–2 form a plateau; an energy penalty instead loses"],
     "chain": ["neutrals"],
     "prediction": "7.42 % mean, 14.2 % at 275 GeV per thrown (471 on X8's clusters, +2 %)"},
]

CHAIN = [("raw", "Raw hits", "digitization\n(frozen)"), ("rec", "Rec hits", "+ HEXPLIT\nsubcells"),
         ("topo", "ImagingTopo", "proto-\nclusters"), ("cog", "CoG + shape", "clusters\n(frozen)"),
         ("neutrals", "Neutrals", "n / γ tag,\ncalibration"), ("lambda", "Λ reco", "pairing,\nvertex")]


# ---- helpers (as the retro deck) -----------------------------------------------------------------------------
def title(slide, text, accent=TEAL):
    add_title(slide, text, accent, INK)


def takeaway(slide, text, y=6.72, color=INK):
    box, tf = txbox(slide, 0.55, y, 12.23, 0.4)
    set_run(tf.paragraphs[0].add_run(), text, Pt(13), color, bold=True)


def caption(slide, text, y, x=0.55, w=12.23):
    box, tf = txbox(slide, x, y, w, 0.4)
    set_run(tf.paragraphs[0].add_run(), text, Pt(11), MUTED, italic=True)


def card(slide, x, y, w, h, heading, lines, accent, fill, size=Pt(12), head_size=Pt(13)):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.05
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = accent; sh.line.width = Pt(1.25); sh.shadow.inherit = False
    box, tf = txbox(slide, x + 0.15, y + 0.1, w - 0.3, 0.35)
    set_run(tf.paragraphs[0].add_run(), heading, head_size, accent, bold=True)
    add_bullets(slide, lines, x + 0.15, y + 0.48, w - 0.3, h - 0.55, INK, size=size, space=Pt(3))
    return sh


def chip(slide, x, y, w, text, accent, fill, size=Pt(13)):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.42))
    sh.adjustments[0] = 0.3
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = accent; sh.line.width = Pt(1.25); sh.shadow.inherit = False
    tf = sh.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), text, size, accent, bold=True)


def chain_strip(slide, y, changed, label="changed by this try"):
    """The ZDC Λ chain as a row of boxes; the stages a try changes are purple."""
    n = len(CHAIN); w = 1.62; gap = (12.23 - n * w) / (n - 1)
    for i, (key, main, sub) in enumerate(CHAIN):
        x = 0.55 + i * (w + gap)
        hit = key in changed
        dia_box(slide, x, y, w, 0.95, main, PURPLE_FILL if hit else GREY_FILL, PURPLE if hit else GREY_BAR, INK, sub,
                main_size=Pt(12.5), sub_size=Pt(10))
        if i < n - 1:
            dia_arrow(slide, x + w + 0.03, y + 0.47, x + w + gap - 0.03, y + 0.47, MUTED)
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(y + 1.07), Inches(0.3), Inches(0.18))
    sh.fill.solid(); sh.fill.fore_color.rgb = PURPLE_FILL; sh.line.color.rgb = PURPLE; sh.shadow.inherit = False
    box, tf = txbox(slide, 0.95, y + 1.03, 6, 0.3)
    set_run(tf.paragraphs[0].add_run(), label, Pt(11), MUTED)


def bars(slide, rows, x, y, w, row_h, vmax, size=Pt(12)):
    """Horizontal bars: rows = [(label, value or None, color)]; value in per cent; the ceiling is the scale."""
    label_w = 2.4
    for i, (label, v, color) in enumerate(rows):
        yy = y + i * row_h
        box, tf = txbox(slide, x, yy + 0.04, label_w - 0.1, row_h)
        set_run(tf.paragraphs[0].add_run(), label, size, INK)
        if v is not None:
            bw = max(0.02, (w - label_w - 1.2) * v / vmax)
            sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x + label_w), Inches(yy + 0.06), Inches(bw),
                                        Inches(row_h - 0.16))
            sh.fill.solid(); sh.fill.fore_color.rgb = color; sh.line.fill.background(); sh.shadow.inherit = False
        box, tf = txbox(slide, x + label_w + (0 if v is None else (w - label_w - 1.2) * v / vmax) + 0.08, yy + 0.04, 1.2, row_h)
        set_run(tf.paragraphs[0].add_run(), pct(v), size, MUTED)


# ---- slides ----------------------------------------------------------------------------------------------------
def s01_title(prs):
    s = new_slide(prs)
    band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(2.3), SLIDE_W, Inches(2.6))
    band.fill.solid(); band.fill.fore_color.rgb = TEAL_FILL; band.line.fill.background(); band.shadow.inherit = False
    box, tf = txbox(s, 0.8, 2.55, 11.7, 1.2)
    set_run(tf.paragraphs[0].add_run(), "ZDC autoresearch, Phase 4: the Λ bar fight", Pt(34), INK, bold=True)
    box, tf = txbox(s, 0.8, 3.75, 11.7, 0.9)
    set_run(tf.paragraphs[0].add_run(), "Maximize Λ → nπ⁰ reconstructed in EICrecon per thrown Λ — no gates, fair-play rules",
            Pt(18), MUTED)
    box, tf = txbox(s, 0.8, 5.3, 11.7, 1.2)
    set_run(tf.paragraphs[0].add_run(), "Started and closed 2026-11-08 · one slide per try · rebuilt from the run's result files",
            Pt(14), MUTED)


def s01b_result(prs):
    """The close-out result, first: final row, start, ceilings, and the four facts that qualify it."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Phase 4 result — X9 against the start and the ceilings")
    stat_callout(s, 0.55, 1.3, 3.9, pct(num("X9_pairing_photon_depth", "S4a_tm_per_thrown_mean"), 3),
                 "X9, mean over 100–275 GeV", PURPLE, MUTED)
    stat_callout(s, 4.72, 1.3, 3.9, pct(num("X9_pairing_photon_depth", "S4a_tm_per_thrown_275"), 3),
                 "X9, at 275 GeV", PURPLE, MUTED)
    stat_callout(s, 8.88, 1.3, 3.9, f"{CEILING} / {CEILING_275} %", "ceiling, mean / 275 GeV (414)", TEAL, MUTED,
                 big_size=Pt(40))
    rows = [["S4a_tm per thrown Λ → nπ⁰", "mean 100–275 GeV", "at 275 GeV"],
            ["R1 (PR 3064), the start", pct(num("R1_pr3064", "S4a_tm_per_thrown_mean"), 3), pct(num("R1_pr3064", "S4a_tm_per_thrown_275"), 3)],
            ["X9, the final row", pct(num("X9_pairing_photon_depth", "S4a_tm_per_thrown_mean"), 3),
             pct(num("X9_pairing_photon_depth", "S4a_tm_per_thrown_275"), 3)],
            ["ceiling (perfect separation, P1b resolution)", f"{CEILING} %", f"{CEILING_275} %"],
            ["acceptance (all three daughters reach the ZDC)", "16.91 %", "32.64 %"]]  # source: lambda-gun-acceptance.json (413)
    add_table(s, rows, 0.55, 3.15, 7.3, TEAL, GREY_FILL, INK, col_widths=[0.5, 0.25, 0.25], size=Pt(13),
              row_h=Inches(0.48))
    card(s, 8.1, 3.15, 4.68, 2.4, "How it was earned", [
        "9 tries: 8 accepted, 1 rejected (X6), 0 foul",
        "fair play PASS on every try (460)",
        "held-out D4h reproduces at both checkpoints (z +36, +31)",
        "determinism repeats identical",
        "commits local on zdc-autoresearch/phase4; never pushed"], GREEN, GREEN_FILL, size=Pt(13))
    takeaway(s, "18× the start on the mean and 17× at 275 GeV; 43 % of the Λ in the acceptance at 275 GeV are found.", y=6.0)
    add_notes(s, "S4a_tm: truth-matched Λ in ±30 MeV of m_Λ from ReconstructedLambdas, times the gun acceptance. "
                 "43 % = 14.101 / 32.64. The ceiling assumes P1b's resolution, so it does not strictly bound this chain.")


def s02_score(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Phase 4 score — S4a_tm per thrown Λ → nπ⁰ and the starting rows")
    stat_callout(s, 0.55, 1.35, 3.9, pct(num("R1_pr3064", "S4a_tm_per_thrown_mean"), 3), "R1 (PR 3064), mean 100–275 GeV",
                 TEAL, MUTED)
    stat_callout(s, 4.72, 1.35, 3.9, pct(num("R1_pr3064", "S4a_tm_per_thrown_275"), 3), "R1 (PR 3064), at 275 GeV",
                 TEAL, MUTED)
    stat_callout(s, 8.88, 1.35, 3.9, f"{CEILING} / {CEILING_275} %", "ceiling, mean / 275 GeV (414)", TEAL, MUTED)
    rows = [["row", "in EICrecon", "offline, tagged + refit", "offline, truth-identified + refit"]]
    for r in ("R1_pr3064", "P1d_R1_nlr1"):
        rows.append([r, f"{pct(num(r, 'S4a_tm_per_thrown_mean'), 3)} / {pct(num(r, 'S4a_tm_per_thrown_275'), 3)}",
                     f"{pct(num(r, 'S4o_vertex_fixed_tagrefit_per_thrown_mean'), 3)} / {pct(num(r, 'S4o_vertex_fixed_tagrefit_per_thrown_275'), 3)}",
                     f"{pct(num(r, 'S4o_vertex_fixed_refit_per_thrown_mean'), 3)} / {pct(num(r, 'S4o_vertex_fixed_refit_per_thrown_275'), 3)}"])
    add_table(s, rows, 0.55, 3.2, 12.23, TEAL, GREY_FILL, INK, col_widths=[0.2, 0.22, 0.27, 0.31], size=Pt(12.5))
    caption(s, "Each cell: mean over 100–275 GeV / value at 275 GeV, per thrown Λ → nπ⁰ (headline.csv). Offline rows run the "
               "stable-vertex chain on the row's own clusters (415); the truth-identified row picks the three clusters by truth.",
            4.5)
    card(s, 0.55, 5.25, 12.23, 1.05, "Selector (D-default-42)", [
        "ACCEPTED when the pooled McNemar z over the eight D4 momenta is at least 3 against the current best on identical events, and the mean per thrown rises"],
        TEAL, TEAL_FILL)
    add_notes(s, "S4a_tm: the truth-matched Λ from EICrecon's ReconstructedLambdas inside ±30 MeV of m_Λ, with purity ≥ 0.8 "
                 "for its three clusters, times the gun acceptance (413).")


def s03_fair_play(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Fair play — 460 checks F1–F3 and fails on every damaged control")
    rows_def = [("R0_stock", "reference"), ("R1_pr3064", "reference"), ("R2_pr3114", "reference"),
                ("R3_pr3063", "reference"), ("L01_box3114", "reference"),
                ("Rt_truthchain", "truth chain beside the scored one"), ("CTL_F1_inplace", "truth clusters feed the scored chain"),
                ("CTL_F1_rewire", "InputTags rewires Λ to truth neutrals"), ("CTL_F2_digi", "ZDC pedestal σ 2 → 8 ADC"),
                ("CTL_F3_dup", "two candidates; photon links all clusters")]
    rows = [["row", "role", "F1 truth-blind", "F2 raw hits = R0", "F3 honest candidates"]]
    for r, role in rows_def:
        fp = load_json(f"fair-play-{r}.json")
        cells = []
        for rule in ("F1", "F2", "F3"):
            if fp is None:
                cells.append(PENDING); continue
            st = [c["status"] for c in fp["checks"] if c["rule"] == rule]
            cells.append("FAIL" if "FAIL" in st else "PASS" if "PASS" in st else "—")
        rows.append([r, role] + cells)
    add_table(s, rows, 0.55, 1.3, 12.23, TEAL, GREY_FILL, INK, col_widths=[0.18, 0.34, 0.16, 0.16, 0.16], size=Pt(11.5),
              row_h=Inches(0.4))
    caption(s, "F1: static walk of the factory registrations from ReconstructedLambdas to raw hits, the patch, the parameters, "
               "and the factories that run (janadot). F2: digitization untouched, raw hits byte-identical to R0. "
               "F3: one Λ per event, n γ γ daughters, disjoint clusters, E_Λ = Σ daughters, no mass constraint.", 5.95)
    add_notes(s, "Operational wording: D-default-43. Rt as built adds a second chain writing ReconstructedLambdasTruth, so "
                 "the scored chain stays stock; its patch still names truth (F1b). The in-place control is the decisive F1a test.")


def s04_chain(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "ZDC Λ chain in EICrecon — the stages a try may change")
    chain_strip(s, 1.6, {"rec", "topo", "neutrals", "lambda"}, label="open to Phase 4 tries")
    card(s, 0.55, 3.25, 6.0, 3.1, "Frozen (fair-play files)", [
        "digitization: the raw hits are the data (F2)",
        "the CoG step and the cluster shapes: they write the cluster ↔ MC associations the scorer reads (F4)",
        "the scorer: 410 truth match, ±30 MeV window, purity 0.8, the D4 / D4h samples"], ORANGE, ORANGE_FILL)
    card(s, 6.78, 3.25, 6.0, 3.1, "Open", [
        "hit reconstruction and HEXPLIT subcells",
        "clustering (ImagingTopoCluster, Island, new algorithms that feed the CoG)",
        "the n / γ tag and the calibration (fitted on the D2 / D3 guns only)",
        "the Λ reconstruction: pairing, vertex, ranking — one candidate per event"], PURPLE, PURPLE_FILL)
    takeaway(s, "Every try below highlights its stages on this strip.")


def s05_scoreboard(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Score per try — S4a_tm per thrown Λ → nπ⁰, mean over 100–275 GeV")
    rows = [("R1 (start)", num("R1_pr3064", "S4a_tm_per_thrown_mean"), GREY_BAR)]
    for t in TRIES:
        v = load_json(f"verdict-{t['row']}.json") or {}
        col = VERDICT_COLOR.get(v.get("verdict", PENDING), (MUTED, GREY_FILL))[0]
        rows.append((t["id"], num(t["row"], "S4a_tm_per_thrown_mean"), col))
    vmax = max([CEILING / 2] + [r[1] for r in rows if r[1] is not None])
    bars(s, rows, 0.55, 1.4, 12.23, 0.5, vmax)
    caption(s, f"Bar colour = verdict (green accepted, orange inconclusive or foul, grey rejected). Ceiling of the mean {CEILING} %. "
               "Values from headline.csv.", 6.3)


def try_slide(prs, t):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, t["title"], PURPLE)
    v = load_json(f"verdict-{t['row']}.json") or {}
    verdict = v.get("verdict", PENDING)
    ch = 0.6 + 0.29 * len(t["change"]) + 0.21 * sum(len(c) > 95 for c in t["change"])
    card(s, 0.55, 1.3, 7.3, ch, "Change", t["change"], PURPLE, PURPLE_FILL, size=Pt(12))
    ph = 0.85 + 0.21 * (len(t["prediction"]) > 95)
    card(s, 0.55, 1.3 + ch + 0.2, 7.3, ph, "Prediction (written before launch)", [t["prediction"]], BLUE, GREY_FILL, size=Pt(12))
    stat_callout(s, 8.1, 1.25, 2.3, pct(num(t["row"], "S4a_tm_per_thrown_mean"), 3), "mean per thrown", PURPLE, MUTED,
                 big_size=Pt(36))
    stat_callout(s, 10.45, 1.25, 2.3, pct(num(t["row"], "S4a_tm_per_thrown_275"), 3), "at 275 GeV", PURPLE, MUTED,
                 big_size=Pt(36))
    base = t["best"]
    box, tf = txbox(s, 8.1, 2.75, 4.7, 0.9)
    set_run(tf.paragraphs[0].add_run(), f"current best {base}: {pct(num(base, 'S4a_tm_per_thrown_mean'), 3)} mean, "
            f"{pct(num(base, 'S4a_tm_per_thrown_275'), 3)} at 275 GeV · ceilings {CEILING} % mean, {CEILING_275} % at 275 GeV", Pt(12), MUTED)
    pooled = v.get("pooled")
    box, tf = txbox(s, 8.1, 3.45, 4.7, 0.6)
    set_run(tf.paragraphs[0].add_run(), "paired test: " + (f"gained {pooled['gained']}, lost {pooled['lost']}, z {pooled['z']:+.2f}"
                                                          if pooled else PENDING), Pt(13), INK, bold=True)
    acc, fill = VERDICT_COLOR.get(verdict, (MUTED, GREY_FILL))
    chip(s, 8.1, 4.05, 2.3, verdict, acc, fill)
    fp = v.get("fair_play", PENDING)
    chip(s, 10.45, 4.05, 2.3, f"fair play {fp}", GREEN if fp == "PASS" else ORANGE if fp == "FAIL" else MUTED,
         GREEN_FILL if fp == "PASS" else ORANGE_FILL if fp == "FAIL" else GREY_FILL, size=Pt(12))
    if t.get("chain"):
        chain_strip_small(s, 5.75, set(t["chain"]))
    add_notes(s, f"Row {t['row']}; branch zdc-autoresearch/phase4 in submodules/EICrecon; patch space/notes/patches/{t['id']}*.patch; "
                 "verdict from space/perf/verdict-<row>.json (461).")
    return s


def chain_strip_small(slide, y, changed):
    n = len(CHAIN); w = 1.75; gap = (12.23 - n * w) / (n - 1)
    for i, (key, main, sub) in enumerate(CHAIN):
        x = 0.55 + i * (w + gap)
        hit = key in changed
        dia_box(slide, x, y, w, 0.55, main, PURPLE_FILL if hit else GREY_FILL, PURPLE if hit else GREY_BAR, INK,
                main_size=Pt(11.5))
        if i < n - 1:
            dia_arrow(slide, x + w + 0.02, y + 0.27, x + w + gap - 0.02, y + 0.27, MUTED)
    box, tf = txbox(slide, 0.55, y + 0.62, 8, 0.3)
    set_run(tf.paragraphs[0].add_run(), "purple: stages this try changes", Pt(10.5), MUTED, italic=True)


def x1_flow(prs):
    """X1 changes the Λ reconstruction's flow: the diagram before / after."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "X1 — Λ reconstruction flow at the pin and in X1", PURPLE)
    def column(x, head, steps, accent, fill):
        box, tf = txbox(s, x, 1.3, 5.8, 0.4)
        set_run(tf.paragraphs[0].add_run(), head, Pt(15), MUTED if accent == GREY_BAR else accent, bold=True)
        y = 1.85
        for i, (main, sub) in enumerate(steps):
            dia_box(s, x, y, 5.8, 0.72, main, fill, accent, INK, sub, main_size=Pt(12.5), sub_size=Pt(10.5))
            if i < len(steps) - 1:
                dia_arrow(s, x + 2.9, y + 0.72, x + 2.9, y + 0.92, MUTED)
            y += 0.92
    column(0.55, "Pin (stock)", [
        ("γγ pairs: π⁰ mass from origin-pointing momenta", "cut at ±10 % of m_π⁰"),
        ("n γγ triplets: Λ mass from origin-pointing momenta", "cut at ±10 % of m_Λ"),
        ("rank: ZDC first, then mass χ², p_z, E", "one triplet"),
        ("vertex: iterate along the Λ direction", "neutron at its first linked cluster"),
        ("final cut ±10 % of m_Λ", "one candidate or none")], GREY_BAR, GREY_FILL)
    column(6.98, "X1", [
        ("every γγ pair with every neutron", "no cut before the vertex"),
        ("vertex: bisection on the γγ opening angle", "along the momentum-weighted slope (B9d)"),
        ("neutron at its leader cluster", "reference point (B9e)"),
        ("rank by fitted π⁰ and Λ masses", "discrete choice only; energies untouched"),
        ("one candidate per event", "the scorer applies ±30 MeV")], PURPLE, PURPLE_FILL)
    takeaway(s, "A decay 10–30 m downstream makes origin-pointing masses wrong; X1 computes every mass after the vertex fit.",
             y=6.55)


def x2_flow(prs):
    """X2 changes the ZDC neutrals: the diagram before / after."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "X2 — photon choice in the ZDC neutrals at X1 and in X2", PURPLE)
    def column(x, head, steps, accent, fill):
        box, tf = txbox(s, x, 1.3, 5.8, 0.4)
        set_run(tf.paragraphs[0].add_run(), head, Pt(15), MUTED if accent == GREY_BAR else accent, bold=True)
        y = 1.85
        for i, (main, sub) in enumerate(steps):
            dia_box(s, x, y, 5.8, 0.72, main, fill, accent, INK, sub, main_size=Pt(12.5), sub_size=Pt(10.5))
            if i < len(steps) - 1:
                dia_arrow(s, x + 2.9, y + 0.72, x + 2.9, y + 0.92, MUTED)
            y += 0.92
    column(0.55, "X1", [
        ("ZDC clusters → shape box tags photons", "about 5–9 tagged clusters per event"),
        ("every tagged cluster becomes a photon", "neutron fragments included"),
        ("neutron = untagged clusters only", "fragment energy missing"),
        ("Λ reconstruction ranks all pairs", "fitted π⁰ and Λ masses"),
        ("one candidate per event", "")], GREY_BAR, GREY_FILL)
    column(6.98, "X2", [
        ("ZDC clusters → shape box tags candidates", "unchanged"),
        ("each pair of candidates: neutron = all other clusters", "energy sum, leader position"),
        ("stable-vertex fit per pair", "π⁰ constraint, as LambdaReconstruction"),
        ("rank: π⁰ and Λ mass χ² + Λ decay-depth density", "discrete choice; energies untouched"),
        ("only the chosen pair written as photons", "the rest stays with the neutron")], PURPLE, PURPLE_FILL)
    takeaway(s, "The neutron of each hypothesis holds every cluster the pair leaves out, so the true pair also gets the right neutron energy.",
             y=6.55)


def x7_flow(prs):
    """X7 changes the clustering: the diagram before / after."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "X7 — ZDC imaging clusters at X5 and in X7", PURPLE)
    def column(x, head, steps, accent, fill):
        box, tf = txbox(s, x, 1.3, 5.8, 0.4)
        set_run(tf.paragraphs[0].add_run(), head, Pt(15), MUTED if accent == GREY_BAR else accent, bold=True)
        y = 1.85
        for i, (main, sub) in enumerate(steps):
            dia_box(s, x, y, 5.8, 0.72, main, fill, accent, INK, sub, main_size=Pt(12.5), sub_size=Pt(10.5))
            if i < len(steps) - 1:
                dia_arrow(s, x + 2.9, y + 0.72, x + 2.9, y + 0.92, MUTED)
            y += 0.92
    column(0.55, "X5", [
        ("HEXPLIT subcells → connected groups", "neighbours in XY and ±1 layer"),
        ("a group survives at ≥ 50 MeV", "low-energy photons often lost"),
        ("one cluster per group", "a photon touching the neutron shower merges into it"),
        ("photon tag: shape box, depth ≤ 225 mm", ""),
        ("Λ pairing (X2–X5)", "")], GREY_BAR, GREY_FILL)
    column(6.98, "X7", [
        ("HEXPLIT subcells → connected groups", "unchanged"),
        ("a group survives at ≥ 20 MeV", "low-energy photons kept"),
        ("cores: maxima ≥ 5 MeV in the first 4 layers, 50 mm apart", "deeper maxima: one shared region"),
        ("hits join their most energetic neighbour's region", "photon cores separate; deep showers stay whole"),
        ("refit on D2 / D3, then the Λ pairing", "photon 4.50·E^0.848, neutron 6.21·E^0.740")], PURPLE, PURPLE_FILL)
    takeaway(s, "Photons shower early and the neutron late: splitting only at shallow cores frees the photons without breaking showers.", y=6.55)


def try_slides(prs):
    for t in TRIES:
        try_slide(prs, t)
        if t.get("flow") and t["id"] == "X1":
            x1_flow(prs)
        if t.get("flow") and t["id"] == "X2":
            x2_flow(prs)
        if t.get("flow") and t["id"] == "X7":
            x7_flow(prs)


def s99_checkpoint1(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Checkpoint 1 — held-out D4h and MSF events after X1–X5")
    cp = load_json("checkpoint-heldout-CP1_X5_D4h-vs-CP1_R1_D4h.json") or {}
    rows = [["D4h momentum", "X5 matched", "R1 matched", "gained / lost", "z", "X5 % per thrown", "R1 % per thrown"]]
    for m in cp.get("per_momentum", []):
        rows.append([f"{m['p']} GeV", m["tm_A"], m["tm_B"], f"{m['gained']} / {m['lost']}", f"{m['z']:+.1f}",
                     pct(m["A_per_thrown_pct"], 2), pct(m["B_per_thrown_pct"], 2)])
    add_table(s, rows, 0.55, 1.3, 12.23, TEAL, GREY_FILL, INK, col_widths=[0.16, 0.12, 0.12, 0.15, 0.1, 0.18, 0.17], size=Pt(12.5))
    pz = cp.get("pooled", {})
    caption(s, f"Pooled over the three held-out momenta: gained {pz.get('gained', PENDING)}, lost {pz.get('lost', PENDING)}, "
               f"z {pz.get('z', 0):+.1f}. X5's per-thrown values on D4h match D4 (175 GeV 3.77 vs 3.79 %; 250 GeV 7.76 vs 7.73 %).", 3.05)
    s9 = load_json("msf-CP1_X5_S5-D6a_9x275.json") or {}; r9 = load_json("msf-R1_pr3064-D6a_9x275.json") or {}
    card(s, 0.55, 3.75, 6.0, 1.75, "MSF events, 9x275 (S5, reported only)", [
        f"Λ in the acceptance found: {100 * s9.get('S5_eff_given_acceptance', 0):.0f} ± {100 * s9.get('S5_eff_err', 0):.0f} % (R1 {100 * r9.get('S5_eff_given_acceptance', 0):.0f} %), 23 Λ in 5000 events",
        f"mass peak {s9.get('S5_mass_mu', 0):.3f} GeV, σ {1000 * s9.get('S5_mass_sigma', 0):.0f} MeV (R1 {r9.get('S5_mass_mu', 0):.3f} GeV, σ {1000 * r9.get('S5_mass_sigma', 0):.0f} MeV)",
        f"candidates {s9.get('S5_candidates_per_1000', 0):.0f} per 1000 events, {s9.get('S5_reco_in_window_per_1000', 0):.0f} in the window: mostly not Λ"],
        TEAL, TEAL_FILL, size=Pt(12))
    card(s, 6.78, 3.75, 6.0, 1.75, "What limits next (X5, D4)", [
        "matched 14–28 % of D4 events; wrong pair 2–4 %; mass window 2–3 %",
        "three clean clusters in only 28–29 % of events; ~87 % of those now convert",
        "photon clusters impure 32–35 %, inside the neutron's 18–21 %, merged 12 %",
        "next: photon-core split (X7); vertex range at the ZDC face (X6)"], ORANGE, ORANGE_FILL, size=Pt(12))
    takeaway(s, "The gain holds on held-out events (pooled z +36); the clustering is the remaining lever.", y=5.85)


def s99_checkpoint2(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Checkpoint 2 — held-out D4h and MSF events after X6–X9")
    cp = load_json("checkpoint-heldout-CP2_X9_D4h-vs-CP1_X5_D4h.json") or {}
    rows = [["D4h momentum", "X9 matched", "X5 matched", "gained / lost", "z", "X9 % per thrown", "X5 % per thrown"]]
    for m in cp.get("per_momentum", []):
        rows.append([f"{m['p']} GeV", m["tm_A"], m["tm_B"], f"{m['gained']} / {m['lost']}", f"{m['z']:+.1f}",
                     pct(m["A_per_thrown_pct"], 2), pct(m["B_per_thrown_pct"], 2)])
    add_table(s, rows, 0.55, 1.3, 12.23, TEAL, GREY_FILL, INK, col_widths=[0.16, 0.12, 0.12, 0.15, 0.1, 0.18, 0.17], size=Pt(12.5))
    pz = cp.get("pooled", {})
    caption(s, f"Pooled: gained {pz.get('gained', PENDING)}, lost {pz.get('lost', PENDING)}, z {pz.get('z', 0):+.1f}. "
               "X9's held-out values match D4 (250 GeV 13.26 vs 13.00 %; 175 GeV 6.42 vs 6.30 %).", 3.05)
    s9 = load_json("msf-CP2_X9_S5-D6a_9x275.json") or {}; x5 = load_json("msf-CP1_X5_S5-D6a_9x275.json") or {}
    card(s, 0.55, 3.75, 6.0, 1.75, "MSF events, 9x275 (S5, reported only)", [
        f"Λ in the acceptance found: {100 * s9.get('S5_eff_given_acceptance', 0):.0f} ± {100 * s9.get('S5_eff_err', 0):.0f} % (X5 {100 * x5.get('S5_eff_given_acceptance', 0):.0f} %)",
        f"mass peak {s9.get('S5_mass_mu', 0):.3f} GeV, σ {1000 * s9.get('S5_mass_sigma', 0):.0f} MeV",
        f"candidates {s9.get('S5_candidates_per_1000', 0):.0f} per 1000 events, {s9.get('S5_reco_in_window_per_1000', 0):.0f} in the window: mostly not Λ"],
        TEAL, TEAL_FILL, size=Pt(12))
    card(s, 6.78, 3.75, 6.0, 1.75, "What limits next (X9, D4)", [
        "per photon: 22 % swallowed by the neutron's cluster, 7 % by the other photon",
        "pairing at 83 % of the oracle; shape terms add nothing",
        "photon energy resolution 18–35 %: next, hit-level weights fitted on D2 / D3"], ORANGE, ORANGE_FILL, size=Pt(12))
    takeaway(s, "X6–X9 hold on held-out events (pooled z +31 against X5); the MSF candidate rate is the physics caveat.", y=5.85)


# ---- close-out (D-user-37, 2026-11-08T14:09Z) -------------------------------------------------------------------
PREDICTIONS = [  # source: the hypothesis lines of space/EXPERIMENTS.md, written before each launch (mean %, 275 GeV %)
    ("X1", "1.5 / 3.0", "beat"), ("X2", "2.84 / 5.45", "met"), ("X3", "3.24 / 5.98", "met"),
    ("X4", "4.31 / 7.96", "failed: limit set from the ZDC centre"), ("X5", "4.31 / 7.96", "met"),
    ("X6", "4.40 / 8.1", "no effect"), ("X7", "6.4 / 11.8", "beat"), ("X8", "7.4 / 14.0", "close"),
    ("X9", "7.42 / 14.2", "met")]


def s100_predictions(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Predictions against results — the nine tries")
    rows = [["try", "predicted, mean / 275 GeV", "measured, mean / 275 GeV", "verdict", "reading"]]
    for (tid, pred, reading), t in zip(PREDICTIONS, TRIES):
        v = load_json(f"verdict-{t['row']}.json") or {}
        meas = f"{pct(num(t['row'], 'S4a_tm_per_thrown_mean'), 3)} / {pct(num(t['row'], 'S4a_tm_per_thrown_275'), 3)}"
        rows.append([tid, pred + " %", meas, v.get("verdict", PENDING), reading])
    add_table(s, rows, 0.55, 1.3, 12.23, TEAL, GREY_FILL, INK, col_widths=[0.07, 0.2, 0.25, 0.14, 0.34], size=Pt(12),
              row_h=Inches(0.42))
    takeaway(s, "Pairing predictions from the 471 emulation held within 3 %; two-file clustering scans underestimated.", y=6.0)
    add_notes(s, "X4 was accepted (z +5.66) although its prediction failed: gammaZMaxOffset is added to the ZDC centre "
                 "(face + 916 mm), so the intended 225 mm limit landed at 1141 mm. X5 set it as intended.")


def s101_limits(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "X9 losses per D4 event and the detector limits")
    ls = (load_json("lambda-losses-X9_pairing_photon_depth.json") or {}).get("per_momentum", {})
    rows = [["D4 momentum", "matched", "clustering", "wrong pair", "window"]]
    for p in ("100", "150", "200", "250", "275"):
        m = ls.get(p)
        rows.append([f"{p} GeV"] + ([f"{m[k]:.2f}" for k in ("matched", "clustering", "photon_tag", "window")] if m else [PENDING] * 4))
    add_table(s, rows, 0.55, 1.3, 6.2, TEAL, GREY_FILL, INK, col_widths=[0.28, 0.18, 0.2, 0.18, 0.16], size=Pt(13),
              row_h=Inches(0.5))
    caption(s, "Fractions of D4 events, first category that applies (470). Clustering: a daughter's best cluster below "
               "purity 0.8, or two daughters sharing one.", 4.45, w=6.2)
    # source: diagnostics on X9 and the D2 gun, 2026-11-08T09:50Z (runlog; scratch budget.py)
    card(s, 7.0, 1.3, 5.78, 3.0, "What sets the limit", [
        "Λ mass width 14.3 MeV; 8.5 MeV with true photon energies, 14.1 MeV with the true neutron energy",
        "photon resolution 21–33 %, set by the 2.7 % sampling fraction",
        "swallowed photons sit a median 21.5 mm from the neutron, under one 24.4 mm subcell",
        "pairing at 83 % of its oracle",
        "left: crystal-section photon energy (~ +2 %), pairing retune (~ +1 %)"], ORANGE, ORANGE_FILL, size=Pt(13))
    takeaway(s, "A larger gain needs a finer or deeper EM measurement than the Hcal sampling.", y=5.4)


def s102_clusters(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "ZDC clusters after the core split — purer photons, fragmented showers")
    cc = (load_json("cluster-containment-phase4.json") or {}).get("rows", {})
    def cell(row, key, fmt="{:.2f}"):
        v = cc.get(row, {}).get("275", {}).get(key)
        return PENDING if v is None else fmt.format(v)
    rows = [["at 275 GeV (D4, 410 tables)", "X5 (before)", "X9 (final)"],
            ["photons with best-cluster purity ≥ 0.8", cell("X5_photon_depth_face", "photon_purity_ge_0p8"),
             cell("X9_pairing_photon_depth", "photon_purity_ge_0p8")],
            ["photons with containment ≥ 0.5", cell("X5_photon_depth_face", "photon_containment_ge_0p5"),
             cell("X9_pairing_photon_depth", "photon_containment_ge_0p5")],
            ["neutron best-cluster containment, median", cell("X5_photon_depth_face", "neutron_containment_median"),
             cell("X9_pairing_photon_depth", "neutron_containment_median")],
            ["S0all per thrown, mean (headline.csv)", pct(num("X5_photon_depth_face", "S0all_per_thrown_mean"), 3),
             pct(num("X9_pairing_photon_depth", "S0all_per_thrown_mean"), 3)]]
    add_table(s, rows, 0.55, 1.3, 7.3, TEAL, GREY_FILL, INK, col_widths=[0.56, 0.22, 0.22], size=Pt(13),
              row_h=Inches(0.46))
    card(s, 8.1, 1.3, 4.68, 2.3, "MSF 9x275 candidates per 1000 events", [
        "R1 21 · X5 206 · X9 360 (213 in the window)",
        "X9 finds 96 ± 4 % of the 23 Λ in the acceptance",
        "most candidates are not Λ"], ORANGE, ORANGE_FILL, size=Pt(13))  # source: msf-*-D6a_9x275.json
    card(s, 0.55, 4.0, 12.23, 1.55, "What this means for other users", [
        "a ZDC cluster is no longer one shower: S0 (purity and containment) falls while the Λ chain rises",
        "the neutrals factory re-sums the neutron; the photon law is refit for 5-layer cores",
        "the core split is off by default, so BEMC and FHCAL clustering is unchanged — argued from the code, not measured"],
        PURPLE, PURPLE_FILL, size=Pt(13))
    takeaway(s, "The gun score was the only selector; cluster quality and the MSF candidate rate need their own ruler.", y=5.9)


def s103_upstream(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Upstream pieces — four patches beyond PRs 3064 and 3063")
    stack = [("pin e5e2a60c", "EICrecon at the program's pin", GREY_FILL, GREY_BAR),
             ("PR 3064 (open)", "ZDC clustering, calibration, n/γ box", GREY_FILL, GREY_BAR),
             ("PR 3063 (open)", "Λ mass windows removed, every triplet fitted", GREY_FILL, GREY_BAR),
             ("U1 LambdaReconstruction", "stable vertex, neutron at its reference point", PURPLE_FILL, PURPLE),
             ("U2 ZDC neutrals", "Λ-hypothesis photon pair, depth limit at the face, centroid", PURPLE_FILL, PURPLE),
             ("U3 ImagingTopoCluster", "photon-core split, default off", PURPLE_FILL, PURPLE),
             ("U4 ZDC configuration", "switches U2 and U3 on; refit calibration", PURPLE_FILL, PURPLE)]
    y = 1.3
    for i, (main, sub, fill, line) in enumerate(stack):
        dia_box(s, 0.55, y, 6.1, 0.6, main, fill, line, INK, sub, main_size=Pt(12), sub_size=Pt(10))
        if i < len(stack) - 1:
            dia_arrow(s, 3.6, y + 0.6, 3.6, y + 0.72, MUTED)
        y += 0.72
    card(s, 6.95, 1.3, 5.83, 2.75, "Open before any pull request", [
        "clang-format: 40 lines over 100 columns",
        "one shared vertex helper; edm4hep::utils for vectors",
        "units on every length and energy; no magic numbers",
        "pairing default off in the Config struct",
        "Catch2 tests for the split and the pairing",
        "measure the cost; check the other detectors"], ORANGE, ORANGE_FILL, size=Pt(13))
    caption(s, "Applying 3064, 3063, U1–U4 to the pin reproduces the branch tip a15b0db6 byte for byte. Patches: "
               "space/notes/patches/upstream/; drafts: space/reports/phase4_upstream.md. Nothing posted or pushed.", 4.25, x=6.95, w=5.83)
    takeaway(s, "U1 fits as a review comment on PR 3063; the depth-limit convention is a one-line bug report.", y=6.55)


def s104_next(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Next phase — Λ purity on MSF events, then upstream")
    card(s, 0.55, 1.3, 6.0, 2.15, "Ruler", [
        "score Λ purity × efficiency on MSF events beside S4a_tm",
        "a larger MSF sample from the farm (23 Λ in 5000 events now)",
        "a guard on the other detectors' collections before upstream",
        "keep the slim template and the fair-play checker"], TEAL, TEAL_FILL, size=Pt(13))
    card(s, 6.78, 1.3, 6.0, 2.15, "Work", [
        "a candidate-quality cut: fitted π⁰ and Λ masses, decay depth, photon depth",
        "the upstream checklist on U1–U4",
        "small gun items: crystal-section photon energy, pairing retune",
        "software compensation fitted on D2 / D3"], PURPLE, PURPLE_FILL, size=Pt(13))
    card(s, 0.55, 3.75, 12.23, 1.3, "Process lessons", [
        "JANA lengths are in cm: write them so in every config",
        "check where a geometry constant sits (here the ZDC centre) before using it as an offset"],
        ORANGE, ORANGE_FILL, size=Pt(13))
    takeaway(s, "The gun score is near what these hits allow; the physics question now is the fake-Λ rate.", y=5.45)


SLIDES = [s01_title, s01b_result, s02_score, s03_fair_play, s04_chain, s05_scoreboard, try_slides, s99_checkpoint1,
          s99_checkpoint2, s100_predictions, s101_limits, s102_clusters, s103_upstream, s104_next]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()
    prs = new_deck()
    for build in SLIDES:
        build(prs)
    prs.save(OUT)
    print(f"wrote {OUT} ({len(prs.slides)} slides)")
    if missing:
        print("missing plots:", *missing, sep="\n  ")
    if not args.no_pdf:
        convert_to_pdf(OUT, OUT[:-5] + ".pdf")


if __name__ == "__main__":
    main()
