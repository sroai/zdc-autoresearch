#!/usr/bin/env python
"""Build autoresearch_retro_v1.pptx (+ .pdf): run 1 of the ZDC autoresearch loop
(2026-11-04/05) — what went well and what went wrong, for physicists who do not
know the ZDC, calorimeter clustering or agent-run experiment loops.

Numbers load at build time from the run's result files:
  space/perf/truth-<exp>-D4_lambda.json      separation S0 and Λ efficiency S4a per momentum
  space/perf/lambda-gun-acceptance.json      fraction of thrown Λ → nπ⁰ inside the ZDC acceptance
  space/perf/lambda-ceiling-variants-P1b_R0_thr.json   Λ ceilings with perfect separation (414)
  space/perf/heldout-P1b_R0_thr-vs-R0_stock.json        E01 held-out check (405)
  space/EXPERIMENTS.md                       verdicts and the ✓/✗ of every hypothesis check
  space/notes/runlog.md                      the timeline (literals below, with # source)
The one embedded plot is space/plots/phase1/P1b_R0_thr/shape_decayz/decayz_D4_175GeV.png.
A missing file leaves "not re-run" in its cell; the deck always builds.

Rebuild:  uv run --no-project --with python-pptx python build_autoresearch_retro_v1_slides.py [--no-pdf]
"""
import argparse
import json
import os
import re

from pptx.enum.dml import MSO_LINE_DASH_STYLE
from slide_kit import *

# ---- palette B (the autoresearch deck family) ---------------------------------
INK    = RGBColor(0x22, 0x26, 0x33);  MUTED = RGBColor(0x60, 0x66, 0x76)
TEAL   = RGBColor(0x18, 0xB8, 0xA6);  TEAL_FILL   = RGBColor(0xD9, 0xF6, 0xF2)
PURPLE = RGBColor(0x7C, 0x4D, 0xD8);  PURPLE_FILL = RGBColor(0xEF, 0xE8, 0xFB)
BLUE   = RGBColor(0x2E, 0x6B, 0xE6)
ORANGE = RGBColor(0xEE, 0x85, 0x4A);  ORANGE_FILL = RGBColor(0xFD, 0xEC, 0xDF)
GREEN  = RGBColor(0x2F, 0x9E, 0x62);  GREEN_FILL  = RGBColor(0xDF, 0xF3, 0xE8)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
GREY_BAR = RGBColor(0xB8, 0xBD, 0xC8); GREY_FILL = RGBColor(0xF1, 0xF3, 0xF6)
GRID = RGBColor(0xDD, 0xE0, 0xE6)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
PERF = os.path.join(REPO, "space", "perf")
OUT = os.path.join(HERE, "autoresearch_retro_v1.pptx")
NA = "not re-run"
missing = []

MOMENTA = ["100", "125", "150", "175", "200", "225", "250", "275"]


# ---- data ----------------------------------------------------------------------
def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def truth(exp, ds="D4_lambda"):
    d = load_json(os.path.join(PERF, f"truth-{exp}-{ds}.json"))
    return d["per_momentum"] if d else None


def cell(pm, p, key):
    try:
        return pm[p][key]
    except (TypeError, KeyError):
        return None


ACC = load_json(os.path.join(PERF, "lambda-gun-acceptance.json")) or {}
ACC_P = {p: ACC[p]["all3_inside_4mrad"] for p in MOMENTA if p in ACC}
ACC_MEAN = 100 * sum(ACC_P.values()) / len(ACC_P) if ACC_P else None
CEIL = (load_json(os.path.join(PERF, "lambda-ceiling-variants-P1b_R0_thr.json")) or {}).get("per_momentum", {})
HELD = load_json(os.path.join(PERF, "heldout-P1b_R0_thr-vs-R0_stock.json"))

EXPS = {  # label: experiment row
    "R0": "R0_stock", "R1": "R1_pr3064", "P1a": "P1a_R0_nlr3", "P1b": "P1b_R0_thr",
    "P1c": "P1c_R0_dist", "E02": "E02_chain480", "E03": "E03_clEdep20", "L01": "L01_box3114",
    "E04": "E04_chain400", "E05": "E05_seed2",
}
T4 = {k: truth(v) for k, v in EXPS.items()}


def mean_per_thrown(pm, key):
    """Mean over momenta of (per-accepted-event fraction × acceptance), in % of thrown Λ → nπ⁰."""
    vals = [cell(pm, p, key) * ACC_P[p] for p in MOMENTA if cell(pm, p, key) is not None and p in ACC_P]
    return 100 * sum(vals) / len(vals) if vals else None


def mean_ceiling(key):
    vals = [CEIL[p][key] for p in MOMENTA if p in CEIL and CEIL[p].get(key) is not None]
    return 100 * sum(vals) / len(vals) if vals else None


def pct(v, digits=2):
    return NA if v is None else f"{v:.{digits}f} %"


# the ledger: verdicts and hypothesis-check tallies, parsed so the deck cannot drift from it
def ledger_sections():
    try:
        text = open(os.path.join(REPO, "space", "EXPERIMENTS.md")).read()
    except OSError:
        return {}
    out = {}
    for m in re.finditer(r"^## (\S+) (\d{4}-\d{2}-\d{2}): (.*)$", text, re.M):
        start = m.end()
        nxt = re.search(r"^## ", text[start:], re.M)
        out[m.group(1)] = text[start:start + nxt.start()] if nxt else text[start:]
    return out


LEDGER = ledger_sections()


def verdict(name):
    """The last verdict word on a 'verdict…' or 're-judged…' line of the entry (re-judging supersedes)."""
    sec = LEDGER.get(name, "")
    m = re.search(r"^status: (STOPPED)\b", sec, re.M)      # a stopped run has no verdict, whatever its text says
    if m:
        return m.group(1)
    found = re.findall(r"^(?:verdict|re-judged)\b[^:\n]*:[^\n]*?\b(ACCEPTED|REJECTED|INCONCLUSIVE)\b", sec, re.M)
    return found[-1] if found else NA


def hypothesis_tally(name):
    sec = LEDGER.get(name, "")
    m = re.search(r"Hypothesis check:(.*?)(?:^guards:|\Z)", sec, re.S | re.M)
    if not m:
        return None, None
    return m.group(1).count("✓"), m.group(1).count("✗")


# source: space/notes/runlog.md (UTC)
TIMELINE = [
    ("01:26", "run start: Phase 0"), ("03:13", "user offline"), ("07:12", "Phase 1 hypotheses written"),
    ("08:30", "Phase 0 done"), ("12:56", "user back"), ("15:35", "Phase 1 done; Phase 2 starts"),
    ("17:37", "/data full"), ("21:10", "user: acceptance?"), ("21:55", "vertex-aware ceiling"), ("23:40", "stop"),
]
RECO_CPU_H = 141.4   # source: sum of wall_s over /data/zdc-autoresearch/reco/*/*/*.json (1333 files, 15 rows)
RECO_FILES = 1333
PEAK_DISK_GB = 865   # source: du at 17:37 UTC, notes/lesson-disk-budget.md
DECISIONS_USER, DECISIONS_AGENT, QUESTIONS, FINDINGS = 21, 25, 8, 9   # source: DECISIONS.md, QUESTIONS.md, FINDINGS.md


# ---- helpers -------------------------------------------------------------------
def ref(fn):
    """Slide number of a registered slide function, so cross-references survive reordering."""
    return str(SLIDES.index(fn) + 1)


def title(slide, text, accent=TEAL):
    add_title(slide, text, accent, INK)


def takeaway(slide, text, y=6.72, color=INK):
    box, tf = txbox(slide, 0.55, y, 12.23, 0.4)
    set_run(tf.paragraphs[0].add_run(), text, Pt(13), color, bold=True)


def caption(slide, text, y, x=0.55, w=12.23):
    box, tf = txbox(slide, x, y, w, 0.4)
    set_run(tf.paragraphs[0].add_run(), text, Pt(11), MUTED, italic=True)


def legend(slide, x, y, items, size=Pt(11), dashed=()):
    for i, (fill, line, text) in enumerate(items):
        sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y + 0.04), Inches(0.3), Inches(0.18))
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
        sh.line.color.rgb = line; sh.line.width = Pt(1.0)
        if i in dashed:
            sh.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        sh.shadow.inherit = False
        box, tf = txbox(slide, x + 0.38, y, 6, 0.3)
        set_run(tf.paragraphs[0].add_run(), text, size, MUTED)
        x += 0.45 + 0.072 * len(text) + 0.35


def card(slide, x, y, w, h, heading, lines, accent, fill, size=Pt(12), head_size=Pt(13)):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.05
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = accent; sh.line.width = Pt(1.25); sh.shadow.inherit = False
    box, tf = txbox(slide, x + 0.15, y + 0.1, w - 0.3, 0.35)
    set_run(tf.paragraphs[0].add_run(), heading, head_size, accent, bold=True)
    add_bullets(slide, lines, x + 0.15, y + 0.48, w - 0.3, h - 0.55, INK, size=size, space=Pt(3))
    return sh


def hline(slide, x1, y1, x2, color, width=Pt(0.75), dash=False):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y1))
    ln.line.color.rgb = color; ln.line.width = width; ln.shadow.inherit = False
    if dash:
        ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return ln


def vline(slide, x, y1, y2, color, width=Pt(1.5), dash=True):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y1), Inches(x), Inches(y2))
    ln.line.color.rgb = color; ln.line.width = width; ln.shadow.inherit = False
    if dash:
        ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return ln


def grouped_bars(slide, x, y, w, h, groups, series, ymax, yticks, ylabel="", xlabel=""):
    """groups: [(label, [v per series])]; series: [(name, color)]. Native shapes, 2 px gaps."""
    axis_x, plot_y = x + 0.55, y
    axis_w, plot_h = w - 0.6, h - 0.4
    for t in yticks:
        yy = plot_y + plot_h * (1 - t / ymax)
        hline(slide, axis_x, yy, axis_x + axis_w, GRID)
        box, tf = txbox(slide, x, yy - 0.09, 0.5, 0.2)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
        set_run(p.add_run(), f"{t:g}", Pt(10), MUTED)
    hline(slide, axis_x, plot_y + plot_h, axis_x + axis_w, MUTED, Pt(1.0))
    ng, ns = len(groups), len(series)
    gw = axis_w / ng
    bar_w = gw * 0.82 / ns
    for gi, (glabel, vals) in enumerate(groups):
        gx = axis_x + gi * gw + gw * 0.09
        for si, v in enumerate(vals):
            if v is None:
                continue
            bh = plot_h * min(v, ymax) / ymax
            sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(gx + si * bar_w + 0.012),
                                        Inches(plot_y + plot_h - bh), Inches(bar_w - 0.024), Inches(bh))
            sh.fill.solid(); sh.fill.fore_color.rgb = series[si][1]
            sh.line.fill.background(); sh.shadow.inherit = False
        box, tf = txbox(slide, axis_x + gi * gw, plot_y + plot_h + 0.06, gw, 0.25)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), glabel, Pt(10.5), INK)
    if ylabel:
        box, tf = txbox(slide, x, y - 0.3, 6, 0.25)
        set_run(tf.paragraphs[0].add_run(), ylabel, Pt(10.5), MUTED, italic=True)
    if xlabel:
        box, tf = txbox(slide, axis_x, plot_y + plot_h + 0.3, axis_w, 0.25)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), xlabel, Pt(10.5), MUTED, italic=True)


def ladder(slide, rows, x, y, w, row_h, label_w, vmax, marks=(), size=Pt(12)):
    """Horizontal bars in % of thrown Λ. rows: (label, value, kind) with kind 'measured' | 'ceiling'."""
    bar_x = x + label_w + 0.15
    bar_w = w - label_w - 1.25
    for i, (label, value, kind) in enumerate(rows):
        yy = y + i * row_h
        box, tf = txbox(slide, x, yy + 0.07, label_w, row_h - 0.1)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
        set_run(p.add_run(), label, size, INK if kind == "measured" else GREEN, italic=(kind != "measured"))
        frac = 0 if value is None else max(min(value / vmax, 1.0), 0.0)
        width = max(bar_w * frac, 0.06)
        sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(bar_x), Inches(yy + 0.08),
                                    Inches(width), Inches(row_h - 0.18))
        sh.fill.solid(); sh.fill.fore_color.rgb = TEAL if kind == "measured" else GREEN_FILL
        if kind == "measured":
            sh.line.fill.background()
        else:
            sh.line.color.rgb = GREEN; sh.line.width = Pt(1.25)
            sh.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        sh.shadow.inherit = False
        box, tf = txbox(slide, bar_x + bar_w + 0.15, yy + 0.07, 1.1, row_h - 0.1)
        set_run(tf.paragraphs[0].add_run(), pct(value), size, INK if kind == "measured" else GREEN, bold=True)
    for value, label in marks:
        if value is None:
            continue
        cx = bar_x + bar_w * min(value / vmax, 1.0)
        vline(slide, cx, y - 0.05, y + len(rows) * row_h, GREEN)
        box, tf = txbox(slide, cx - 1.5, y + len(rows) * row_h + 0.02, 3.0, 0.3)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), label, Pt(10.5), GREEN, bold=True)


# ---- slides --------------------------------------------------------------------
def s01_title(prs):
    s = new_slide(prs)
    band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(2.3), SLIDE_W, Inches(2.6))
    band.fill.solid(); band.fill.fore_color.rgb = TEAL_FILL; band.line.fill.background(); band.shadow.inherit = False
    box, tf = txbox(s, 0.8, 2.55, 11.7, 1.2)
    set_run(tf.paragraphs[0].add_run(), "ZDC autoresearch, run 1: what went well and what went wrong", Pt(34), INK, bold=True)
    box, tf = txbox(s, 0.8, 3.75, 11.7, 0.9)
    set_run(tf.paragraphs[0].add_run(),
            "An agent-run experiment loop on the reconstruction of Λ → nπ⁰ in the ePIC Zero Degree Calorimeter",
            Pt(18), MUTED)
    box, tf = txbox(s, 0.8, 5.3, 11.7, 1.2)
    p = tf.paragraphs[0]
    set_run(p.add_run(), "Run of 2026-11-04/05, 22 hours · deck v1, built from the run's result files and ledger", Pt(14), MUTED)
    p2 = tf.add_paragraph()
    set_run(p2.add_run(), "For physicists outside the ZDC and outside agent-run loops: every term is defined where it is used",
            Pt(14), MUTED)
    add_notes(s, "Retrospective of the first run of the ZDC autoresearch loop. The audience is general physicists; "
                 "the ZDC, the metrics and the loop itself are explained on the first slides.")


def s02_physics(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "The task: Λ → nπ⁰ at the Zero Degree Calorimeter, 36 m from the collision")
    y0 = 2.35
    dia_box(s, 0.55, y0 - 0.3, 1.5, 0.6, "collision", TEAL_FILL, TEAL, INK, "ep, proton side")
    dia_arrow(s, 2.05, y0, 4.3, y0, MUTED)
    box, tf = txbox(s, 2.1, y0 - 0.55, 2.2, 0.3)
    set_run(tf.paragraphs[0].add_run(), "Λ flies 7–19 m on average", Pt(10.5), MUTED, italic=True)
    dec = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(4.3), Inches(y0 - 0.12), Inches(0.24), Inches(0.24))
    dec.fill.solid(); dec.fill.fore_color.rgb = PURPLE; dec.line.fill.background(); dec.shadow.inherit = False
    box, tf = txbox(s, 3.7, y0 + 0.2, 1.6, 0.5)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), "Λ → n π⁰\nπ⁰ → γ γ", Pt(10.5), PURPLE, bold=True)
    zx = 8.6
    for dy, lab, col in ((-0.55, "γ", ORANGE), (0.0, "n", BLUE), (0.55, "γ", ORANGE)):
        dia_arrow(s, 4.54, y0, zx, y0 + dy, col)
        box, tf = txbox(s, zx - 0.45, y0 + dy - 0.32, 0.3, 0.3)
        set_run(tf.paragraphs[0].add_run(), lab, Pt(12), col, bold=True)
    zdc = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(zx), Inches(y0 - 1.0), Inches(0.5), Inches(2.0))
    zdc.fill.solid(); zdc.fill.fore_color.rgb = GREY_FILL; zdc.line.color.rgb = INK; zdc.line.width = Pt(1.25)
    zdc.shadow.inherit = False
    add_bullets(s, [("ZDC: a block of absorber and scintillator tiles", 0, True),
                    ("square tiles 4.9 cm, read out as 2.4 cm subcells", 1),
                    ("records where energy was deposited, layer by layer", 1),
                    ("accepts particles within 4 mrad of the beam (±14 cm)", 1)],
                zx + 0.65, y0 - 0.95, 3.9, 2.0, INK, size=Pt(11.5), space=Pt(2))
    stat_callout(s, 0.55, 3.55, 3.0, "35.8 m", "collision point to the ZDC face", TEAL, MUTED, big_size=Pt(36), label_size=Pt(12))
    acc_lo, acc_hi = (100 * ACC_P["100"], 100 * ACC_P["275"]) if ACC_P else (None, None)
    stat_callout(s, 3.6, 3.55, 3.4, f"{acc_lo:.1f}–{acc_hi:.0f} %" if acc_lo is not None else NA,
                 "of Λ → nπ⁰ reach the ZDC with all\nthree particles (100–275 GeV)", TEAL, MUTED, big_size=Pt(36), label_size=Pt(12))
    stat_callout(s, 7.1, 3.55, 3.0, "4.5 % → ~0", "Λ reconstruction efficiency after the\n2026 change to square tiles", ORANGE, MUTED, big_size=Pt(36), label_size=Pt(12))
    add_bullets(s, [
        ("What the reconstruction has to do", 0, True),
        ("group hit subcells into clusters: one cluster per particle, then pair the two photons into a π⁰ and the π⁰ with the neutron into a Λ", 1),
        ("the three showers overlap on the ZDC face; the clusterer joins neighbouring subcells, so one chain of hits becomes one cluster", 1),
        ("the 2026 tile change widened the neighbour distance: the three showers now chain into one cluster and the Λ count fell to ~0", 1),
        ("a proposed fix (EICrecon PR 3064) shrinks the distance; the loop's job: keep n, γ, γ in separate clusters without breaking the neutron measurement", 1),
    ], 0.55, 5.0, 12.2, 1.7, INK, size=Pt(12), space=Pt(2))
    takeaway(s, "Three showers on one calorimeter face after 36 m of flight: telling them apart comes before any Λ can be counted.")
    add_notes(s, "ZDC = Zero Degree Calorimeter, on the outgoing proton side. The Meson Structure Function programme needs Λ → nπ⁰ "
                 "reconstructed there. Numbers: 35.8 m from docs/zdc-problem.md; acceptance from lambda-gun-acceptance.json "
                 "(fraction of thrown Λ → nπ⁰ with all three daughters inside 4 mrad); 4.5 % → ~0 from the MSF campaigns "
                 "26.02 (hex tiles) vs 26.07 (square tiles), EICrecon issue 2737. Tile side 48.8 mm, subcell pitch 24.4 mm.")


def s03_loop(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Autoresearch here: an agent executes a written loop, a human answers at checkpoints")
    steps = [
        ("1  hypothesis", "written and timestamped\nbefore the run"),
        ("2  one change", "one clustering parameter\n(no code change)"),
        ("3  reconstruct", "~90 files, 2000 events per\nmomentum, ≈10 CPU-h"),
        ("4  paired test", "same events as the current\nbest; 3σ on gained − lost"),
        ("5  guards", "neutron energy, photon\nscale, cluster shapes"),
        ("6  verdict", "ACCEPTED / REJECTED /\nINCONCLUSIVE, in the ledger"),
    ]
    bw, gap, y = 1.85, 0.22, 1.35
    for i, (main, sub) in enumerate(steps):
        x = 0.55 + i * (bw + gap)
        dia_box(s, x, y, bw, 1.15, main, TEAL_FILL, TEAL, INK, sub, main_size=Pt(12.5), sub_size=Pt(10))
        if i < len(steps) - 1:
            dia_arrow(s, x + bw, y + 0.57, x + bw + gap, y + 0.57, TEAL)
    back = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0.55 + 5 * (bw + gap) + bw / 2), Inches(y + 1.15),
                                  Inches(0.55 + bw / 2), Inches(y + 1.15))
    back.line.color.rgb = TEAL; back.line.width = Pt(1.25); back.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    back.shadow.inherit = False
    box, tf = txbox(s, 4.5, y + 1.2, 4.0, 0.3)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), "next experiment starts from the current best", Pt(10.5), TEAL, italic=True)
    card(s, 0.55, 3.0, 3.95, 1.5, "Checkpoints", [
        "every 5 experiments: a held-out sample (fresh seeds, never used to choose), a report, questions to the user",
        "after 10: stop for review",
    ], TEAL, GREY_FILL)
    card(s, 4.69, 3.0, 3.95, 1.5, "Frozen rulers", [
        "the scoring scripts and the metric limits cannot change inside a phase",
        "a change to a ruler is a decision, logged with its reason",
    ], TEAL, GREY_FILL)
    card(s, 8.83, 3.0, 3.95, 1.5, "The record", [
        "ledger: hypothesis, numbers, verdict for every run, rejected ones included",
        "decision log with the user's words; questions file; findings on code outside the program",
    ], TEAL, GREY_FILL)
    phases = [("Phase 0", "foundation: references,\nnoise floor, ceilings", "done"),
              ("Phase 1", "dissect PR 3064:\n6 single-change runs", "done"),
              ("Phase 2", "parameter loop:\n6 judged, then stopped", "done"),
              ("Phase 3", "code changes to\nthe clusterer", "planned"),
              ("Phase 4", "farm confirmation,\nPR draft", "planned")]
    pw, py = 2.3, 4.95
    for i, (name, sub, st) in enumerate(phases):
        x = 0.55 + i * (pw + 0.18)
        fill, line = (TEAL_FILL, TEAL) if st == "done" else (ORANGE_FILL, ORANGE)
        b = dia_box(s, x, py, pw, 1.0, name, fill, line, INK, sub, main_size=Pt(12), sub_size=Pt(10))
        if st == "planned":
            b.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        if i < len(phases) - 1:
            dia_arrow(s, x + pw, py + 0.5, x + pw + 0.18, py + 0.5, MUTED)
    legend(s, 0.55, 6.15, [(TEAL_FILL, TEAL, "done in run 1"), (ORANGE_FILL, ORANGE, "planned")], dashed=(1,))
    takeaway(s, "The human sets the rules and the limits; the agent runs the loop and writes the record.", y=6.6)
    add_notes(s, "The loop is zdc-autoresearch-loop-v2.md, written before the run and revised once after an expert review of "
                 "version 1. A 'parameter experiment' is a JANA -P override on a pinned EICrecon build; a 'code experiment' "
                 "patches the ZDC-owned files and rebuilds. The current best is the configuration every new experiment is "
                 "compared against; it changes only when an experiment is accepted and its gain reproduces on the held-out sample.")


def s04_numbers(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    judged = ["P1a", "P1b", "P1c", "P1d", "P1e", "P1f", "E01", "E02", "E03", "L01", "E04", "E05"]
    vs = [verdict(n) for n in judged]
    n_acc, n_rej, n_inc = vs.count("ACCEPTED"), vs.count("REJECTED"), vs.count("INCONCLUSIVE")
    title(s, f"Run 1 in numbers: 22 hours, 15 reconstructions, {len(judged)} judged experiments")
    row1 = [("22 h", "wall clock, 01:26 → 23:40 UTC;\nuser offline for the first 12"),
            (f"{RECO_CPU_H:.0f} CPU-h", f"reconstruction: {RECO_FILES} files\nin 15 reconstruction rows"),
            (f"{len(judged)}", f"judged experiments: {n_acc} accepted (one\nconfiguration), {n_rej} rejected, {n_inc} inconclusive"),
            (f"{FINDINGS}", "defects found in code the\nprogram does not own")]
    row2 = [(f"{DECISIONS_USER} + {DECISIONS_AGENT}", "decisions logged:\nuser + agent defaults"),
            (f"{QUESTIONS}", "questions put to the user,\nall answered"),
            (f"{PEAK_DISK_GB} GB", "peak disk use;\n63 GB per experiment"),
            ("2", "parameter families closed by\ntheir guards (chaining, survival)")]
    for r, row in enumerate((row1, row2)):
        for i, (big, lab) in enumerate(row):
            stat_callout(s, 0.55 + i * 3.08, 1.25 + r * 1.75, 3.0, big, lab, TEAL if r == 0 else INK, MUTED,
                         big_size=Pt(34), label_size=Pt(11.5))
    ty = 5.4
    hline(s, 0.8, ty, 12.5, MUTED, Pt(1.5))
    t0, t1 = 1 + 26 / 60, 23.75
    for i, (hhmm, lab) in enumerate(TIMELINE):
        h, m = hhmm.split(":"); t = int(h) + int(m) / 60
        x = 0.8 + 11.7 * (t - t0) / (t1 - t0)
        dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x - 0.07), Inches(ty - 0.07), Inches(0.14), Inches(0.14))
        dot.fill.solid(); dot.fill.fore_color.rgb = ORANGE if lab in ("/data full", "user offline") else TEAL
        dot.line.fill.background(); dot.shadow.inherit = False
        up = i % 2 == 0
        box, tf = txbox(s, x - 0.9, ty - 0.62 if up else ty + 0.12, 1.8, 0.5)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), f"{hhmm}\n{lab}", Pt(9.5), INK)
    caption(s, "Timeline, UTC. Phases 0–1 ran unattended; Phase 2 with the user online.", 6.45)
    add_notes(s, "Sources: runlog.md for the timeline; per-file JSON records for CPU hours; EXPERIMENTS.md for the verdicts "
                 "(parsed at build time; P1b was rejected by the letter in Phase 1 and re-judged ACCEPTED after two user "
                 "decisions on the guards, then adopted as E01). DECISIONS.md (21 user, 25 agent-default entries), "
                 "QUESTIONS.md, FINDINGS.md. E04 and E05 were stopped at their plot step at 23:30 UTC and judged from the "
                 "written numbers on 'finish E4, E5 analysis'.")


def s05_metrics_1(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Metrics, part 1: what the clustering does to each particle (S0–S3)")
    rows = [["metric", "measured on", "the question it answers", "role"],
            ["S0γ, S0n, S0all", "Λ → nπ⁰ events, 8 momenta", "is each photon, the neutron, all three, in a cluster of its own? (separated: the cluster is ≥ 80 % that particle and holds ≥ 50 % of its clustered energy)", "selector: S0all decides"],
            ["S1a", "lone π⁰ → γγ, 7 momenta", "are the two photons of a π⁰ in two clusters? — the simplest separation, no neutron in the way", "diagnostic"],
            ["S1b, S1c, S1d", "lone π⁰", "do the two clusters give back the π⁰ mass and energy? how precisely is a photon's impact point measured?", "diagnostic"],
            ["S2", "lone photon, 8 energies", "is the photon's energy right (scale), how wide is the spread (resolution), is it recognised as a photon (γ-tag)?", "guard on the scale: within 5 % after a refit"],
            ["S3", "lone neutron, 6 energies", "how much of the neutron's energy ends up in clusters (raw sum), in how many clusters, and is it ever mistaken for a photon?", "guard: raw sum drop ≤ 5 %, clusters per neutron ≤ +0.5, mistag"]]
    add_table(s, rows, 0.55, 1.3, 12.2, TEAL, GREY_FILL, INK, col_widths=[0.12, 0.17, 0.5, 0.21], size=Pt(11.5), row_h=Inches(0.62))
    add_bullets(s, [
        ("Reading the rows", 0, True),
        ("every number is a fraction of events (or of particles) at one momentum; 1000–2000 events per point, so ±0.01 is resolvable", 1),
        ("'truth-matched' means the simulation's record of which particle made each hit is used to judge a cluster; a reconstruction on real data has no such record", 1),
        ("'raw' energy is the summed cluster energy before any calibration, so a calibration change cannot hide a lost shower", 1),
    ], 0.55, 5.25, 12.2, 1.4, INK, size=Pt(12), space=Pt(2))
    takeaway(s, "S0 asks the one question the clusterer controls; S2 and S3 ask whether the single particles are still measured right.")
    add_notes(s, "Definitions from zdc-setup.md (Scoreboard) and configs/metrics.yaml. Datasets: D4 (Λ gun), D1 (π⁰ gun), "
                 "D2 (photon gun), D3 (neutron gun). S1c was not filled in this run (its fit is the benchmark's and returned nan).")


def s06_metrics_2(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Metrics, part 2: the Λ outcome, physics-event guards and bookkeeping (S4, S5, G, T)")
    rows = [["metric", "measured on", "the question it answers", "role"],
            ["S4a", "Λ → nπ⁰ events", "in what fraction of events does the code output a Λ built from the right three clusters, with the right mass? (beside it: any Λ at all)", "outcome: reported, never decides"],
            ["S4b, S4c", "Λ → nπ⁰ events", "how sharp is the Λ mass peak? how many photon-like objects per event (fragments make fake pairs)?", "guards"],
            ["S5", "simulated physics events (MSF Λ sample)", "Λ candidates per 1000 real-looking events, and how many of the true Λ are found", "the physics goal; confirmation only"],
            ["G1, G2, G3", "deep-inelastic events (the CI's samples)", "do clusters still look like showers (not single columns or odd shapes)? are the high-energy clusters still there? how much low-energy debris per event?", "guards: limits set by the user"],
            ["G4", "every dataset", "did anything outside the ZDC change? (every other collection compared file by file)", "gate: a difference rejects"],
            ["T", "every dataset", "reconstruction seconds per 1000 events", "report line; 2× slower is a question"]]
    add_table(s, rows, 0.55, 1.3, 12.2, TEAL, GREY_FILL, INK, col_widths=[0.12, 0.17, 0.5, 0.21], size=Pt(11.5), row_h=Inches(0.58))
    add_bullets(s, [
        ("Reading the rows", 0, True),
        ("G1–G3 exist because the reviewers of PR 3064 saw three defects on physics events: single-column clusters, a spike in a shape angle, missing high-energy clusters; the guards make those measurable", 1),
        (f"S5 is the number the physics programme cares about; with 23 true Λ in 5000 events it cannot rank settings (slide {ref(s10_headline)})", 1),
    ], 0.55, 5.5, 12.2, 1.1, INK, size=Pt(12), space=Pt(2))
    takeaway(s, "The Λ numbers are the goal; they are reported beside every experiment but never allowed to decide it.")
    add_notes(s, "S4a 'truth-matched': each daughter cluster has purity ≥ 0.8 for the true n, γ, γ and the mass is inside a fixed "
                 "±0.03 GeV scoring window. S5 is from scripts/402_lambda_msf_metrics.py on the MSF campaign files (D6a).")


def s07_why_metrics(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Why these metrics: one decides, several protect, the rest report")
    card(s, 0.55, 1.3, 3.95, 2.5, "One decides: S0all", [
        "it measures exactly what the clusterer controls: whether showers end up in separate clusters",
        "it counts events, so the same events can be compared setting against setting (gained − lost), which is far more sensitive than comparing two averages",
        "it is truth-matched: 'two clusters' alone could be one photon split in two",
    ], TEAL, TEAL_FILL, size=Pt(11.5))
    card(s, 4.69, 1.3, 3.95, 2.5, "Several protect: S2, S3, S4b–c, G1–G4", [
        "each guard is something the current reconstruction does well that a photon-friendly setting could silently break: the neutron's energy, the photon scale, shower shapes on physics events, everything else in the event",
        "the limits were set by the user before the loop ran; a loop that sets its own limits can always pass",
    ], ORANGE, ORANGE_FILL, size=Pt(11.5))
    card(s, 8.83, 1.3, 3.95, 2.5, "The rest report: S4a, S5, S1, T", [
        "S4a and S5 are the goal, and cannot decide: they are 0 for most settings, and they depend on the pairing code downstream of the clustering",
        "S1 isolates the photon–photon case; T flags a slowdown",
        "units added mid-run: per thrown Λ → nπ⁰, so the 1.6–33 % acceptance is folded in",
    ], GREEN, GREEN_FILL, size=Pt(11.5))
    add_bullets(s, [
        ("What a student should take from this", 0, True),
        ("a selector must be sensitive, must measure the thing being changed, and must be hard to game; the guards cover what the selector ignores", 1),
        ("a proxy selector is a bet: that improving it improves the goal; the bet has to be checked with a number tied to the goal (next slide)", 1),
        ("the limits are as much a physics statement as the selector: 'the neutron may lose 5 %' is a decision the physicist owns", 1),
    ], 0.55, 4.1, 12.2, 1.6, INK, size=Pt(12), space=Pt(2))
    takeaway(s, "S0all is sensitive, on target and hard to game; the tie to the goal is what it lacks.")
    add_notes(s, "Selector and guard roles from zdc-setup.md and the v1 expert review (§2.2: S4a is dominated by "
                 "LambdaReconstruction, not by the clustering). Limits: D-user-7 (G1–G3), D-user-12 (raw sum one-sided), "
                 "D-user-13 (S2 after refit). Per-thrown units: D-user-20.")


def s08_missing_metrics(prs):
    s = new_slide(prs); add_slide_number(prs, s, ORANGE)
    title(s, "Metrics that were missing, for the loop and for reporting", ORANGE)
    rows = [["missing", "what it would have told us", "status"],
            ["a ceiling for separation (give each subcell to the particle that put most energy in it; score with the same rule)", "how far each setting is from the best any clustering could do", "never computed"],
            ["a Λ number that moves while S4a is 0 (a vertex-aware pairing run offline on real clusters)", "whether a separation gain changes the Λ yield at all", "computed once, at the end, for perfect clusters only"],
            ["who merges with whom: photon with photon, or photon with neutron", "which code change would help: splitting showers or shortening the reach", "the views say 'merged', not with what"],
            ["separation by decay position, as a number", "where the loss is geometry and where it is the clusterer", "a plot per setting, no scoreboard cell"],
            ["per-thrown-Λ units (acceptance folded in)", "numbers comparable across momenta and with the physics analysis", "added mid-run (user)"],
            ["a prediction hit rate per checkpoint", "whether the loop understands the detector or only screens", "computed for this deck"],
            ["cost per experiment: CPU-h, GB, wall time", "the budget spent per answer; the disk would not have filled", "T per 1000 events only"],
            ["enough Λ for S5 and the mass peak (S4b)", "23 true Λ in 5000 events cannot rank anything", "farm-scale sample planned"],
            ["a one-line report per experiment", "a result readable without the ledger", "added mid-run (user)"]]
    add_table(s, rows, 0.55, 1.3, 12.2, ORANGE, GREY_FILL, INK, col_widths=[0.42, 0.36, 0.22], size=Pt(11), row_h=Inches(0.46))
    takeaway(s, "The first two rows are the gap that let the loop optimise a proxy for a day; both are afternoon-sized scripts.", y=6.55)
    add_notes(s, "'Added mid-run (user)' rows: D-user-15 (decay-position and cluster-shape views) and D-user-20 (per-thrown "
                 "headline and one-line reports). The vertex-aware pairing ceiling is 414_lambda_ceiling_variants.py; running it "
                 "on real clusters instead of perfect ones is run-2 item 1.")


def s09_scoreboard(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "S0all by Λ momentum: stock, PR 3064 and the three Phase 2 settings")
    series = [("R0 stock", GREY_BAR), ("R1 = PR 3064", PURPLE), ("P1b (accepted)", TEAL),
              ("E02 chaining 480 keV (rejected)", ORANGE), ("E03 floor 20 MeV (rejected)", BLUE)]
    labels = ["R0", "R1", "P1b", "E02", "E03"]
    groups = [(f"{p} GeV", [cell(T4[l], p, "S0_all_sep") for l in labels]) for p in MOMENTA]
    grouped_bars(s, 0.55, 1.55, 12.2, 4.6, groups, series, ymax=0.10, yticks=[0, 0.02, 0.04, 0.06, 0.08, 0.10],
                 ylabel="fraction of Λ events with n, γ, γ each in a cluster of its own (S0all)", xlabel="Λ momentum")
    legend(s, 0.55, 6.3, [(c, c, n) for n, c in series], size=Pt(10.5))
    takeaway(s, "Every 3×3 setting beats stock by 2–5× and stays below 0.1; PR 3064 is below stock above 125 GeV.", y=6.75)
    add_notes(s, "Values from truth-<exp>-D4_lambda.json, S0_all_sep per momentum. E02 and E03 are rejected on guards "
                 f"(slide {ref(s16_knobs)}), so the current best is P1b. R1 separates photons well but breaks the neutron "
                 f"(slide {ref(s11_dissection)}). Errors: with 2000 events, ±0.005 at 0.05.")


def s10_headline(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Per thrown Λ → nπ⁰: separation 0.3 → 0.6 %, Λ reconstructed 0 %, ceiling 14 %")
    vmax = 18.0
    box, tf = txbox(s, 0.55, 1.2, 6.0, 0.3)
    set_run(tf.paragraphs[0].add_run(), "All three particles separated, mean over 100–275 GeV", Pt(13), INK, bold=True)
    rows = [(f"{n} {d}", mean_per_thrown(T4[n], "S0_all_sep"), "measured") for n, d in
            (("R0", "stock"), ("R1", "PR 3064"), ("P1b", "accepted"), ("E02", "rejected"), ("E03", "rejected"),
             ("E04", "rejected"), ("E05", "inconclusive"))]
    rows.append(("ceiling: acceptance", ACC_MEAN, "ceiling"))
    ladder(s, rows, 0.55, 1.55, 6.1, 0.37, 2.6, vmax)
    box, tf = txbox(s, 6.78, 1.2, 6.0, 0.3)
    set_run(tf.paragraphs[0].add_run(), "Λ reconstructed, mean over 100–275 GeV", Pt(13), INK, bold=True)
    rows2 = [("R0 stock", mean_per_thrown(T4["R0"], "S4a_tm_eff"), "measured"),
             ("P1b accepted", mean_per_thrown(T4["P1b"], "S4a_tm_eff"), "measured"),
             ("L01 = P1b + photon cuts", mean_per_thrown(T4["L01"], "S4a_tm_eff"), "measured"),
             ("R1 PR 3064", mean_per_thrown(T4["R1"], "S4a_tm_eff"), "measured"),
             ("stock pairing, perfect separation", mean_ceiling("stock_real_per_thrown"), "ceiling"),
             ("vertex-aware pairing, perfect separation", mean_ceiling("vertex_fixed_real_per_thrown"), "ceiling"),
             ("ceiling: acceptance", ACC_MEAN, "ceiling")]
    ladder(s, rows2, 6.78, 1.55, 6.0, 0.37, 2.9, vmax)
    legend(s, 0.55, 4.75, [(TEAL, TEAL, "measured on the reconstruction"),
                           (GREEN_FILL, GREEN, "ceiling: computed offline with perfect separation and the measured resolution")],
           dashed=(1,))
    add_bullets(s, [
        "units: per cent of all thrown Λ → nπ⁰ at that momentum, so the geometric acceptance (1.6–33 %) is the ceiling of every bar",
        f"left: the clustering moved separation from 0.3 to 0.6 of 17 points; the ceiling of this bar is not known (slide {ref(s08_missing_metrics)}, first row)",
        "right: no 3×3 setting reconstructs a Λ; with the pairing as coded even perfect clusters give 0.9 %; a vertex-aware pairing gives 14 %",
        "at 275 GeV alone (the headline momentum): Λ ceiling " + pct(100 * CEIL.get("275", {}).get("vertex_fixed_real_per_thrown", 0) or None, 1)
        + " of thrown Λ, acceptance " + pct(100 * ACC_P.get("275", 0) or None, 1) + "; the current best reconstructs 0.00 %",
    ], 0.55, 5.2, 12.2, 1.5, INK, size=Pt(12), space=Pt(2))
    takeaway(s, "Of the 17 points available, the clustering knobs moved 0.3; the pairing code holds 13.")
    add_notes(s, "Per-thrown = per-accepted-event fraction × acceptance at that momentum (lambda-gun-acceptance.json), averaged "
                 "over the 8 momenta — the headline the user asked for (D-user-20). Ceilings from 414_lambda_ceiling_variants.py: "
                 "'stock pairing' is LambdaReconstruction's own steps fed with perfectly separated clusters at P1b's measured "
                 "energy and position resolution; 'vertex-aware' replaces the IP-pointing π⁰ pairing with a stable vertex "
                 "search (finding F9). R1 reconstructs some Λ because its photon clusters pass the shape cuts; L01 adds PR 3114's "
                 "wider cuts to P1b and gains 25 Λ in 16 000 events.")


def s11_dissection(prs):
    s = new_slide(prs); add_slide_number(prs, s, GREEN)
    title(s, "What went well: PR 3064 split into its three changes, each measured alone", GREEN)
    series = [("R0 stock", GREY_BAR), ("R1: all three changes", PURPLE), ("P1c: distance only", ORANGE),
              ("P1b: thresholds only", TEAL), ("P1a: layer range only", BLUE)]
    labels = ["R0", "R1", "P1c", "P1b", "P1a"]
    groups = [("photons separated (S0γ)", [cell(T4[l], "175", "S0_g_sep") for l in labels]),
              ("neutron separated (S0n)", [cell(T4[l], "175", "S0_n_sep") for l in labels]),
              ("all three (S0all)", [cell(T4[l], "175", "S0_all_sep") for l in labels])]
    grouped_bars(s, 0.55, 1.55, 6.3, 3.6, groups, series, ymax=0.8, yticks=[0, 0.2, 0.4, 0.6, 0.8],
                 ylabel="fraction of Λ events at 175 GeV")
    legend(s, 0.55, 5.3, [(c, c, n) for n, c in series[:3]], size=Pt(10))
    legend(s, 0.55, 5.6, [(c, c, n) for n, c in series[3:]], size=Pt(10))
    rows = [["change in PR 3064", "photons", "neutron", "verdict"],
            ["neighbour distance 36.6 → 14.6 mm", "+0.17", "−0.21, clusters collapse to columns", "rejected"],
            ["seed 25 → 5 MeV, size 10 → 2 hits", "+0.03", "unchanged", "accepted"],
            ["layer range 1 → 3", "−0.02", "unchanged", "rejected"]]
    add_table(s, rows, 7.1, 1.55, 5.7, TEAL, GREY_FILL, INK, col_widths=[0.42, 0.14, 0.3, 0.14], size=Pt(11), row_h=Inches(0.5))
    add_bullets(s, [
        "the PR's photon gain comes from the shorter distance; its neutron cost comes from the same distance",
        "the thresholds alone give a smaller gain and cost nothing: the keepable part of the PR",
        "the layer range makes it worse; one run closed that question",
    ], 7.1, 3.9, 5.7, 1.6, INK, size=Pt(12), space=Pt(3))
    takeaway(s, "A reviewer of PR 3064 can now say which line to merge and which to drop, with numbers.")
    add_notes(s, "Phase 1: six single-change runs between R0 (stock) and R1 (the PR), three adding one change to R0 and three "
                 "removing one from R1. Numbers at 175 GeV from truth-*-D4_lambda.json; deltas in the table are S0γ and S0n "
                 "at 175 GeV against R0. P1c also fails the cluster-shape guards on deep-inelastic events (single-column clusters).")


def s12_method(prs):
    s = new_slide(prs); add_slide_number(prs, s, GREEN)
    title(s, "What went well: predictions before each run, paired tests, a held-out set that reproduced", GREEN)
    card(s, 0.55, 1.3, 5.6, 2.4, "Pre-registration and statistics", [
        "every hypothesis timestamped in the ledger before its reconstruction started; verdicts of rejected runs kept",
        "noise floor measured first: 26 metric tests over 3 seeds; the quoted errors are honest, 3σ is the line",
        "paired test on identical events: gained − lost, so a +0.01 change is resolvable with 2000 events",
        f"the ledger scores each prediction ✓ / ✗ against the result (slide {ref(s15_predictions)})",
    ], GREEN, GREEN_FILL, size=Pt(12))
    search = {p: (cell(T4["P1b"], p, "S0_all_sep") or 0) - (cell(T4["R0"], p, "S0_all_sep") or 0) for p in ("125", "175", "250")}
    held = {}
    if HELD:
        for c in HELD["cells"]:
            if c["dataset"].startswith("D4h") and c["cell"] == "S0_all":
                held[str(c["momentum"])] = c
    rows = [["momentum", "search set Δ S0all", "held-out Δ S0all", "held-out gained / lost", "z"]]
    for p in ("125", "175", "250"):
        h = held.get(p)
        rows.append([f"{p} GeV", f"{search[p]:+.3f}", f"{h['delta']:+.3f}" if h else NA,
                     f"{h['gained']} / {h['lost']}" if h else NA, f"{h['z']:.1f}" if h else NA])
    box, tf = txbox(s, 6.4, 1.3, 6.4, 0.3)
    set_run(tf.paragraphs[0].add_run(), "E01: P1b against stock on the held-out sample (seed never used to choose)",
            Pt(12.5), INK, bold=True)
    add_table(s, rows, 6.4, 1.7, 6.4, GREEN, GREY_FILL, INK, col_widths=[0.16, 0.22, 0.22, 0.24, 0.16], size=Pt(11.5), row_h=Inches(0.42))
    add_bullets(s, [
        "criterion written before the numbers existed: significant and positive at ≥ 2 of 3 momenta, nothing falls",
        "result: 3 of 3, zero events lost; the search-set gain repeats within errors",
    ], 6.4, 3.5, 6.4, 1.0, INK, size=Pt(12), space=Pt(3))
    add_bullets(s, [
        ("Also kept honest by construction", 0, True),
        ("a gate compares every non-ZDC collection to the reference file by file: a ZDC change that touched anything else would be rejected without appeal", 1),
        ("rulers frozen per phase; the two ruler changes of the run (containment definition, raw-sum guard) are logged decisions with the user's words", 1),
    ], 0.55, 4.6, 12.2, 1.7, INK, size=Pt(12), space=Pt(2))
    takeaway(s, "The accepted gain is real: it repeated on events that played no part in choosing it.")
    add_notes(s, "Held-out numbers from heldout-P1b_R0_thr-vs-R0_stock.json (405_heldout_check.py); search-set deltas from the "
                 "truth JSON. The held-out D4h sample has seed 101 at 125/175/250 GeV. The noise validation is "
                 "space/perf/noise-validation.json (Phase 0).")


def s13_findings(prs):
    s = new_slide(prs); add_slide_number(prs, s, GREEN)
    title(s, "What went well: nine defects found in code the program does not own", GREEN)
    rows = [["finding", "what it is, in plain words", "effect"],
            ["F4", "the Λ finder pairs photons as if they came from the collision point; only decays within ~3.6 m pass its π⁰ mass window",
             "caps the Λ yield at 0–7 % of accepted events, whatever the clustering does"],
            ["F9", "the decay-vertex iteration diverges for decays far from the collision point (hidden behind F4)",
             "any fix of F4 exposes it; a stable vertex search measured offline reaches the acceptance"],
            ["F6", "the energy calibration does not fit the clusters it is applied to", "photons read 13–31 % low"],
            ["F7", "a photon depth cut is measured from the ZDC centre, 1.3 m behind the front face the paper uses", "removes real photons"],
            ["F8", "the photon shape cuts reject every ZDC photon on the new tiles", "fix proposed in PR 3114 (reference R2 here)"],
            ["F1, F2, F3, F5", "stale collection names in the benchmarks; a unit fallback; subcell dimensions; no Λ on ZDC-only geometries",
             "silent empty plots; workarounds in place"]]
    add_table(s, rows, 0.55, 1.3, 12.2, GREEN, GREY_FILL, INK, col_widths=[0.11, 0.57, 0.32], size=Pt(11.5), row_h=Inches(0.56))
    add_bullets(s, [
        "all nine are open issues for EICrecon or the benchmarks, each with the file and line, a measurement and a proposed fix",
        "F4 came from the expert review of the loop's first version; the loop measured its size in Phase 0 on its own",
        f"F9 was found only after the user asked for the acceptance (slide {ref(s14_proxy)})",
    ], 0.55, 5.55, 12.2, 1.1, INK, size=Pt(12), space=Pt(2))
    takeaway(s, "Two of the nine (F4, F9) bound the Λ yield more than any clustering setting in the loop's search space.")
    add_notes(s, "Full entries in space/reports/phase0_findings.md, phase1_findings.md, phase2_findings.md; index in FINDINGS.md. "
                 "F4: LambdaReconstruction builds the γγ mass from IP-pointing momenta and cuts at ±10 % of the π⁰ mass; the "
                 "IP-pointing opening angle is smaller by (L − z_decay)/L, so only z_decay ≲ 0.1 L ≈ 3.6 m passes.")


def s14_proxy(prs):
    s = new_slide(prs); add_slide_number(prs, s, ORANGE)
    title(s, "What went wrong: the loop tuned the clustering while the Λ ceiling sat in the pairing code", ORANGE)
    card(s, 0.55, 1.3, 7.4, 2.95, "What the loop knew, and when", [
        "Phase 0, night: measured the cap — with perfect inputs the pairing as coded passes 0–6.8 % of accepted Λ events (F4); filed as a finding, loop continued with its phase order",
        "Phases 1–2: 11 reconstructions on clustering knobs; separation ×3, Λ reconstructed 0 → 0",
        "21:10 UTC, user asks about the acceptance; 21:55: an offline check with a vertex-aware pairing passes 73–85 % of accepted events (F9) — 10× the cap, independent of the clustering",
        "the loop's own backlog had that pairing as a Phase 3 experiment, not as a ceiling to measure first",
    ], ORANGE, ORANGE_FILL, size=Pt(12))
    stat_callout(s, 8.2, 1.35, 4.5, pct(mean_ceiling("stock_real_per_thrown"), 1),
                 "Λ per thrown Λ → nπ⁰ with perfect clusters\nand the pairing as coded (mean, 100–275 GeV)", ORANGE, MUTED,
                 big_size=Pt(40), label_size=Pt(11.5))
    stat_callout(s, 8.2, 3.0, 4.5, pct(mean_ceiling("vertex_fixed_real_per_thrown"), 1),
                 "same clusters, vertex-aware pairing\n(acceptance " + pct(ACC_MEAN, 1) + ")",
                 GREEN, MUTED, big_size=Pt(40), label_size=Pt(11.5))
    add_bullets(s, [
        ("Why it happened", 0, True),
        ("the selector (S0) was chosen because the Λ count could not rank settings; that choice also disconnected the loop from the deliverable", 1),
        ("the program's phase order (parameters, then code) was followed after the cap was known; no rule said 'measure every ceiling before tuning under it'", 1),
        ("the expert review had estimated the cap at 10–30 %; the loop measured 0–7 % and did not re-plan on the difference", 1),
    ], 0.55, 4.5, 12.2, 1.6, INK, size=Pt(12), space=Pt(2))
    takeaway(s, "The cap was known on day one; the lever was measured only when the user pointed. Rule for run 2: ceilings first.")
    add_notes(s, "F4 ceiling: lambda-ceiling-R0_stock.json (412, Phase 0 item 12). Vertex-aware ceiling: "
                 "lambda-ceiling-variants-P1b_R0_thr.json (414, after the user's 21:10 UTC question and 'Yes. And continue'). "
                 "The 'stock pairing' number here uses P1b's measured energy and position resolution; with ideal inputs it is "
                 "0–6.9 % of accepted events. Both are means over 8 momenta in per cent of thrown Λ → nπ⁰.")


def s15_predictions(prs):
    s = new_slide(prs); add_slide_number(prs, s, ORANGE)
    rows = [["experiment", "change", "right / wrong", "the miss"]]
    desc = {"P1a": ("layer range 1 → 3", "photon loss not predicted"),
            "P1b": ("seed 5 MeV, size 2 hits", "photon gain 3–9× larger than predicted"),
            "P1c": ("distance 14.6 mm", "half the photon gain; neutron did not collapse fully"),
            "P1d": ("R1 with layer range 1", "cluster count went down, predicted up"),
            "P1e": ("R1 with stock thresholds", "one magnitude miss"),
            "P1f": ("R1 with stock distance", "—"),
            "E02": ("chaining 315 → 480 keV", "neutron energy −13 % (predicted −5 %); low-momentum gain not predicted"),
            "E03": ("cluster floor 50 → 20 MeV", "debris clusters on DIS events 5× the prediction"),
            "L01": ("P1b + PR 3114 photon cuts", "—"),
            "E04": ("chaining 315 → 400 keV", "— (the 'linear cost' branch, pre-registered, held)"),
            "E05": ("seed 5 → 2 MeV", "— (the predicted null)")}
    tot_ok = tot_miss = 0
    for n, (chg, miss) in desc.items():
        ok, bad = hypothesis_tally(n)
        if ok is None:
            rows.append([n, chg, NA, miss]); continue
        tot_ok += ok; tot_miss += bad
        rows.append([n, chg, f"{ok} / {bad}", miss])
    rate = 100 * tot_ok / (tot_ok + tot_miss) if tot_ok + tot_miss else None
    title(s, f"What went wrong: pre-registered predictions were right {rate:.0f} % of the time" if rate else
          "What went wrong: pre-registered predictions were right only part of the time", ORANGE)
    rows.append(["total", "", f"{tot_ok} / {tot_miss}", f"{rate:.0f} % of predicted cells right" if rate else NA])
    add_table(s, rows, 0.55, 1.3, 12.2, ORANGE, GREY_FILL, INK, col_widths=[0.1, 0.22, 0.12, 0.56], size=Pt(10.5), row_h=Inches(0.32))
    add_bullets(s, [
        "directions were mostly right; the misses are magnitudes, and most say the same thing: the cost was larger than the share measured on the clusters beforehand",
        "the hit rate rose through the run: Phase 1 17 / 12, Phase 2 28 / 8 — the later hypotheses were written with the earlier misses in hand",
        "a loop that mispredicts a third of its cells is screening the space, not yet modelling the detector; the tally belongs in every checkpoint report",
    ], 0.55, 5.6, 12.2, 1.1, INK, size=Pt(12), space=Pt(2))
    takeaway(s, "Pre-registration made the miss rate measurable. Without it this slide could not exist.")
    add_notes(s, "Counts parsed at build time from the 'Hypothesis check' line of each ledger entry (✓ and ✗ per predicted cell). "
                 "E01 and R2 have no prediction line of that form. The title's percentage is the total row.")


def s16_knobs(prs):
    s = new_slide(prs); add_slide_number(prs, s, ORANGE)
    title(s, "What went wrong: the parameter knobs cannot separate what the showers merge", ORANGE)
    e02_all = cell(T4["E02"], "175", "S0_all_sep"); p1b_all = cell(T4["P1b"], "175", "S0_all_sep")
    d_e02 = f"{e02_all - p1b_all:+.3f}" if e02_all is not None and p1b_all is not None else NA
    e03_100 = cell(T4["E03"], "100", "S0_all_sep"); p1b_100 = cell(T4["P1b"], "100", "S0_all_sep")
    d_e03 = f"{e03_100 - p1b_100:+.3f}" if e03_100 is not None and p1b_100 is not None else NA
    card(s, 0.55, 1.3, 3.95, 2.3, "Reach — R1, P1c", [
        "a shorter neighbour distance stops the chaining: photons separated 0.40 instead of 0.06",
        "the same distance cuts the neutron shower into single-column pieces: neutron separated 0.04 instead of 0.65",
        "cluster shapes on physics events fail the guards",
    ], ORANGE, ORANGE_FILL, size=Pt(11.5))
    card(s, 4.69, 1.3, 3.95, 2.5, "Chaining threshold — E02, E04", [
        "hits below 480 keV no longer join a cluster: the low-energy bridges between photon and neutron are cut",
        f"S0all {d_e02} at 175 GeV, significant at all 8 momenta",
        "the same hits are the neutron's own halo: its summed energy drops 13 % at 20 GeV (limit 5 %) → rejected",
        "E04, half the step (400 keV): half the gain, half the cost (−7.6 %) → rejected; family closed",
    ], ORANGE, ORANGE_FILL, size=Pt(11.5))
    card(s, 8.83, 1.3, 3.95, 2.5, "Survival thresholds — E03, E05", [
        "clusters below 20 MeV deposited (≈ 0.7 GeV) now survive: the softest Λ photons get a cluster",
        f"S0all {d_e03} at 100 GeV; nothing above 150 GeV",
        "a 1 GeV photon and a 1 GeV neutron fragment look alike to a threshold: 0.97 debris clusters per DIS event (limit 0.5) → rejected",
        "E05, seed 5 → 2 MeV: no event changes → family closed",
    ], ORANGE, ORANGE_FILL, size=Pt(11.5))
    add_bullets(s, [
        ("Where the remaining gain is", 0, True),
        ("a connected-component clusterer joins or cuts; it cannot split a dense photon core out of the neutron's halo", 1),
        ("code changes, planned for Phase 3: split clusters at local maxima (the Island algorithm with splitting); chain hits at a high threshold, then collect the low ones onto the nearest cluster", 1),
        ("the loop's parameter phase had a low ceiling by construction; ten of its twelve judged runs were threshold or distance steps, and two families are now closed by their guards", 1),
    ], 0.55, 4.0, 12.2, 1.9, INK, size=Pt(12), space=Pt(2))
    legend(s, 0.55, 5.9, [(ORANGE_FILL, ORANGE, "the code changes are planned, not run")], dashed=(0,))
    takeaway(s, "After six Phase 2 runs both threshold families are closed by their guards; the next step is a code change.")
    add_notes(s, "Numbers from the ledger entries of P1c, E02, E03 and from truth-*-D4_lambda.json. The '20 MeV ≈ 0.7 GeV' uses "
                 "the sampling fraction 0.0273. Backlog items B8 (Island + splitCluster) and B11 (chain high, collect low).")


def s17_decayz(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Where the photons go: merged with the neutron shower at every decay position")
    plot = os.path.join(REPO, "space", "plots", "phase1", "P1b_R0_thr", "shape_decayz", "decayz_D4_175GeV.png")
    add_picture_fit(s, plot, 0.55, 1.2, 7.7, 5.4, MUTED, caption=False, missing=missing)
    add_bullets(s, [
        ("How to read it (P1b, Λ at 175 GeV, 1993 events)", 0, True),
        ("bars, left axis: at each true decay position, the share of events where both photons are separated (green), share one cluster with something else (purple), or one photon has no cluster at all (orange)", 1),
        ("curves, right axis, independent scale: cumulative share of events decaying before that z — all events reach 100 %; the neutron is separated in 65 %; all three in 5 %; Λ reconstructed: 0, on the axis", 1),
        ("87–97 % of photon pairs share a cluster at every z; early decays do slightly better", 1),
        ("Why", 0, True),
        ("the π⁰ carries ~15 % of the Λ energy; its photons land within the neutron's shower, and the clusterer joins any chain of neighbouring hits", 1),
    ], 8.45, 1.25, 4.35, 5.4, INK, size=Pt(11.5), space=Pt(3))
    takeaway(s, "The loss is one mechanism: photon showers chained to the neutron shower. Thresholds trim it; they cannot cut it.", y=6.8)
    add_notes(s, "Plot: space/plots/phase1/P1b_R0_thr/shape_decayz/decayz_D4_175GeV.png from scripts/430_shape_decayz.py, requested "
                 "by the user mid-run in the format of the toy-model plots (two independent axes; right axis 100 % for every nπ⁰ "
                 "decay before the ZDC). The same plot exists for every setting and momentum.")


def s18_operations(prs):
    s = new_slide(prs); add_slide_number(prs, s, ORANGE)
    title(s, "What went wrong: operations — a full disk, silent truncation, a crash under load", ORANGE)
    rows = [["time (UTC)", "what happened", "consequence"],
            ["17:37", f"/data reached 100 % ({PEAK_DISK_GB} GB of outputs, 63 GB per experiment)", "two analyses, one reconstruction and one Λ count failed"],
            ["18:50", "failure noticed, by reading the logs 73 minutes later", "no watchdog; empty log files looked like 'not started'"],
            ["18:57", "user decision: delete the rejected runs' output (315 GB); retention rule from now on", "run resumes"],
            ["19:05", "8 output files cut short had been renamed as complete (the reconstruction exits 0 when writes fail)", "a rerun would have skipped them and scored truncated data"],
            ["11:53", "one chunk crashed in a different detector's code while 24 jobs shared the machine", "rerun alone, fine"],
            ["earlier", "ledger timestamps written ahead of the clock", "corrected by hand"]]
    add_table(s, rows, 0.55, 1.3, 12.2, ORANGE, GREY_FILL, INK, col_widths=[0.1, 0.52, 0.38], size=Pt(11), row_h=Inches(0.46))
    card(s, 0.55, 4.7, 6.0, 1.55, "Root cause", [
        "every experiment writes every collection — full tracking on deep-inelastic events — for a gate that a ZDC parameter cannot fail",
        "no preflight check of free space; no integrity check of outputs",
    ], ORANGE, ORANGE_FILL, size=Pt(11.5))
    card(s, 6.78, 4.7, 6.0, 1.55, "Fixed during the run / still open", [
        "an output now needs its per-file record or it is redone; rejected runs deleted after the verdict; ≥ 150 GB before a launch",
        "open: restrict the collections written (63 GB → ~5 GB per experiment)",
    ], GREEN, GREEN_FILL, size=Pt(11.5))
    takeaway(s, "Unattended loops fail on plumbing; run 1's plumbing had no checks at all.", y=6.55)
    add_notes(s, "Sources: notes/lesson-disk-budget.md, runlog.md, DECISIONS.md D-user-19. The crash was in the pfRICH IRT code "
                 "after a JANA worker timeout, unrelated to the ZDC.")


def s19_changes(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Changes for run 2, ranked by leverage")
    rows = [["#", "change", "expected effect"],
            ["1", "a selector tied to the Λ chain: run the vertex-aware pairing offline on each setting's real clusters", "a number that moves with the Λ yield, minutes per experiment, no EICrecon change"],
            ["2", "an ideal-partition ceiling for separation: give each subcell to the particle that put most energy in it, score with the same rule", "a denominator for every separation table"],
            ["3", "write only the ZDC collections for parameter runs; run the full gate once per code build", "63 GB → ~5 GB, 2.5 h → ~40 min per experiment; scans instead of single steps"],
            ["4", "code tier as soon as a parameter family is closed by its guards", "the remaining separation gain (split at local maxima; chain high, collect low)"],
            ["5", "preflight and integrity checks in the launcher: free space, output records, non-empty logs, error scan", "failures found in minutes, by the loop"],
            ["6", "a prediction tally and the cost per experiment in every checkpoint report", "the loop reports its own hit rate and its budget"],
            ["7", "loop rule: measure every ceiling before tuning under it; re-plan when a measured ceiling contradicts the plan", "no proxy optimisation while the cap is elsewhere"]]
    add_table(s, rows, 0.55, 1.3, 12.2, TEAL, GREY_FILL, INK, col_widths=[0.04, 0.5, 0.46], size=Pt(11.5), row_h=Inches(0.56))
    legend(s, 0.55, 6.2, [(ORANGE_FILL, ORANGE, "all seven are proposals, none implemented yet")], dashed=(0,))
    takeaway(s, "Items 1, 2 and 7 would have re-aimed run 1 by its second hour.", y=6.6)
    add_notes(s, "Items 1–2 are offline scripts over existing reconstructions (an afternoon). Item 3 is a config change in "
                 "120_reconstruct.py. Item 4 is backlog B8/B11. Item 7 is a change to the loop file itself.")


def s20_status(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Status at the stop: one accepted, three rejected, two inconclusive, two families closed")
    rows = [["experiment", "change", "verdict", "reason"],
            ["E01 = P1b", "seed 5 MeV, size 2 hits", verdict("E01"), "held-out check reproduced; current best"],
            ["E02", "chaining threshold 480 keV", verdict("E02"), "neutron energy −13 % at 20 GeV (limit 5 %)"],
            ["E03", "cluster floor 20 MeV", verdict("E03"), "0.97 debris clusters per DIS event (limit 0.5)"],
            ["L01", "P1b + PR 3114 photon cuts", verdict("L01"), "25 Λ gained, 0 lost in 16 000 events; no momentum at 3σ"],
            ["E04", "chaining threshold 400 keV", verdict("E04"), "neutron energy −7.6 % at 20 GeV (limit 5 %); chaining family closed"],
            ["E05", "seed 2 MeV", verdict("E05"), "no event changes, as predicted; survival-threshold family closed"]]
    add_table(s, rows, 0.55, 1.3, 12.2, TEAL, GREY_FILL, INK, col_widths=[0.12, 0.26, 0.16, 0.46], size=Pt(11.5), row_h=Inches(0.42))
    card(s, 0.55, 4.5, 6.0, 1.8, "Decisions pending, for the user", [
        "E04 / E05 output (126 GB) falls under the retention rule once the user confirms",
        "adopt the run-2 changes, in particular the Λ-chain selector before any further clustering run",
        "Phase 3 code tier next (split at local maxima; chain high, collect low), or a re-planned Phase 2",
    ], TEAL, TEAL_FILL, size=Pt(12))
    card(s, 6.78, 4.5, 6.0, 1.8, "What exists, reproducibly", [
        "every number on these slides rebuilds from space/perf/*.json and the ledger (slides/build_autoresearch_retro_v1_slides.py)",
        "every experiment is regenerable from its config at the pinned EICrecon build",
        "transcripts, decisions and questions are kept for the write-up",
    ], TEAL, GREY_FILL, size=Pt(12))
    takeaway(s, "Run 1 produced a clear negative result on the clustering knobs, nine findings, and the measured location of the real lever.", y=6.6)
    add_notes(s, "Verdicts are parsed from EXPERIMENTS.md at build time. The run stopped at 23:30 UTC on 'Dont continue after "
                 "E02/E03/L01' (D-user-21); E04 and E05 were judged from their written numbers at 23:40 on 'finish E4, E5 "
                 "analysis'. Rule 7 closed both threshold families. Nothing is committed; the working tree holds the run.")


SLIDES = [s01_title, s02_physics, s03_loop, s04_numbers,
          s05_metrics_1, s06_metrics_2, s07_why_metrics, s08_missing_metrics,
          s09_scoreboard, s10_headline,
          s11_dissection, s12_method, s13_findings,
          s14_proxy, s15_predictions, s16_knobs, s17_decayz, s18_operations,
          s19_changes, s20_status]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()
    prs = new_deck()
    for build in SLIDES:
        build(prs)
    prs.save(OUT)
    print(f"wrote {OUT} ({len(SLIDES)} slides)")
    if missing:
        print("missing plots:", *missing, sep="\n  ")
    if not args.no_pdf:
        convert_to_pdf(OUT, OUT[:-5] + ".pdf")


if __name__ == "__main__":
    main()
