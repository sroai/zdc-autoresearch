#!/usr/bin/env python
"""Build phase6_crystal.pptx (+ .pdf): Phase 6 of the ZDC autoresearch loop, the crystal-seeded ZDC photon finder
(loop v6), one slide per try (D-user-36).

Numbers load at build time; a missing file leaves "pending" in its place, so the deck always builds:
  space/perf/msf-regimes-<row>-<dataset>.json      N_found, N_window, yield, purity (210)
  space/perf/msf-select-<cand>-vs-<best>-D6s.json   the paired selector of a try (463)
  space/perf/fair-play-<row>-msf.json              F1–F3 on the MSF outputs (460)
  space/perf/crystal-f3-<row>.json                 F3 for crystal clusters (468)
  space/perf/crystal-scope-<row>-<dataset>.json    the Step 0 scope study (477)
  space/perf/calib-crystal-<row>.json              the crystal photon law fitted on the guns D2 + D2c (477 --fit-guns)
  space/perf/t-resolution-<row>.json               the −t resolution of the found Λ (476)
The try texts (change, prediction) are the TRIES list below, written before each launch.

Rebuild:  uv run --no-project --with python-pptx python slides/phase6/build_phase6_slides.py [--no-pdf]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from slide_kit import *  # noqa: E402,F401,F403

# ---- palette B, as the Phase 4 and Phase 5 decks ------------------------------------------------------------------
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
OUT = os.path.join(HERE, "phase6_crystal.pptx")
PLOTS = os.path.join(HERE, "..", "..", "space", "plots", "phase6")     # scripts/702_phase_plots.py 6
PENDING = "pending"
REACH = {"9x275": 43.6, "9x130": 8.0}   # source: msf-regimes-MSF11_X9-D6c_*.json, groups n ZDC with both γ read
BASE = "MSF6_Y9"
VERDICT_COLOR = {"ACCEPTED": (GREEN, GREEN_FILL), "INCONCLUSIVE": (ORANGE, ORANGE_FILL),
                 "REJECTED": (MUTED, GREY_FILL), "REJECTED (purity)": (ORANGE, ORANGE_FILL),
                 "FOUL": (ORANGE, ORANGE_FILL), PENDING: (MUTED, GREY_FILL)}
missing = []


def load_json(name):
    try:
        with open(os.path.join(PERF, name)) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def pct(v, digits=2):
    return PENDING if v is None else f"{100 * v:.{digits}f} %"


# ---- the tries (D-user-36): one entry per try, written before its launch -------------------------------------
TRIES = [
    {"id": "Z1", "row": "Z1_crystal_photons", "best": "MSF6_Y9",
     "title": "Z1 — crystal-seeded photons in the ZDC Λ pairing",
     "change": ["crystal section clustered at the crystal scale: 8 neighbours, split at local maxima ≥ 0.1 GeV",
                "a crystal cluster ≥ 0.5 GeV with no tagged Hcal photon behind it is a photon candidate",
                "its energy 1.962·E_crys + 47.47·E_column − 0.881 (gun fit, D2 + D2c); its column leaves the neutron",
                "new hypotheses: crystal + Hcal photon, crystal + crystal, crystal + B0 photon"],
     "prediction": "477 emulation: N_found 1267 → ~1385, 219 → ~234 (+133 pooled); purity 26.7 → ~28.4 %"},
    {"id": "Z1b", "row": "Z1b_crystal_column", "best": "MSF6_Y9",
     "title": "Z1b — crystal photons with the Hcal column from the rec hits",
     "change": ["Z1 summed the Hcal column over the clusters' HEXPLIT subcells: 0.45 of the rec-hit column",
                "its crystal photons carried a median 0.56 of their energy (Z1: +12, INCONCLUSIVE)",
                "Z1b sums the column over HcalFarForwardZDCRecHits (6th input), the hits the law was fitted on"],
     "prediction": "as Z1's emulation: N_found 1267 → ~1385, 219 → ~234 (+133 pooled); purity 26.7 → ~28.4 %"},
    {"id": "Z2", "row": "Z2_crystal_params", "best": "Z1b_crystal_column",
     "title": "Z2 — crystal photon parameters: threshold, column width, neutron share",
     "change": ["crystal candidates from 0.3 GeV (0.5 GeV)",
                "Hcal column 60 mm wide (45 mm), the law refitted on the guns at that width",
                "the column leaves the neutron on the Hcal clusters' scale (× 1/0.0273): no double counting"],
     "prediction": "477: +31 emulated over Z1b; at Z1b's 45 % fidelity ~+14: 1314 → ~1328, 232 → ~232; purity flat"},
    {"id": "Z4", "row": "Z4_lambda_sigma", "best": "Z2_crystal_params",
     "title": "Z4 — the ZDC pairing's Λ-mass width 0.04 → 0.03 GeV",
     "change": ["with crystal candidates the chooser weighs more hypotheses per event",
                "679 missed Λ at 9x275 hold pure candidates for both photons",
                "a narrower Λ-mass term ranks the true triplet first more often"],
     "prediction": "477 --full: +27 found, +308 in the window: 1388 → ~1409, 230 → ~236; purity 28.0 → ~27 %"},
    {"id": "Z5", "row": "Z5_crystal_energy_alt", "best": "Z4_lambda_sigma",
     "title": "Z5 — the crystal law's energy as a competing hypothesis for Hcal photons",
     "change": ["a tagged Hcal photon with a crystal cluster in front also competes with the crystal law's energy",
                "crystal law σ 10–11 % on the guns at 5–50 GeV; the Hcal law 24–34 %",
                "the chooser keeps whichever energy fits; the winner links the crystal cluster too",
                "Z3, the outright replacement, lost 107 Λ at 9x275 in emulation"],
     "prediction": "477 --alt: +160 over Z4 at a nearly flat window: 1409 → ~1556, 237 → ~250; purity up"},
    {"id": "Z6", "row": "Z6_alt_column_out", "best": "Z5_crystal_energy_alt",
     "title": "Z6 — the crystal-law photon's Hcal column leaves the neutron",
     "change": ["Z5 measures the Λ energy high (reco / true 1.110 vs Z4's 1.073) and −t worse at 9x275",
                "a crystal-law Hcal photon's column beyond its own cluster stayed in the neutron: counted twice",
                "Z6 removes it from the neutron, as Z2 does for crystal photons"],
     "prediction": "477: Λ energy 1.122 → 1.058 for −14 found at 9x275: no gain for 463; −t below Z4's 0.122 GeV²"},
    {"id": "Z7", "row": "Z7_isolation", "best": "Z6_alt_column_out",
     "title": "Z7 — tagged photons near the neutron core pay an isolation term",
     "change": ["The photon tag lets neutron shower fragments through; the chooser then picks one as the second photon",
                "Shape and depth do not tell them apart; distance to the most energetic cluster does (fragments 35 mm, photons 88 mm)",
                "Each tagged Hcal photon adds 2 · exp(−d / 42.5 mm) to its hypothesis's score; 42.5 mm: neutron-gun fragments"],
     "prediction": "477: +88 found over Z6 (9x275 +83, 9x130 +5), N_window −42: purity up; −t unchanged"},
    {"id": "Z8", "row": "Z8_hcal_axis_law", "best": "Z7_isolation",
     "title": "Z8 — tagged Hcal photons may take the axis law's energy",
     "change": ["Right pairs out of the mass window: the photons read low (Hcal law 0.69), the neutron right (1.02)",
                "A photon's Hcal shower splits into several clusters; the law on the leading one scatters ±30 % on guns",
                "Axis law: crystal + Hcal rec hits within 45 mm of the photon's line, fitted on guns (±10 %), as a competing energy"],
     "prediction": "477: +66 found over Z7 (9x275 +59, 9x130 +7), purity ~31 %; −t at or below 0.120 GeV²"},
]


# ---- helpers (as the Phase 5 deck) -------------------------------------------------------------------------------
def title(slide, text, accent=TEAL):
    add_title(slide, text, accent, INK)


def takeaway(slide, text, y=6.72, color=INK):
    box, tf = txbox(slide, 0.55, y, 12.23, 0.4)
    set_run(tf.paragraphs[0].add_run(), text, Pt(13), color, bold=True)


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


def rows_of(row, ds):
    d = load_json(f"msf-regimes-{row}-{ds}.json") or {}
    return (d.get("rows") or {}).get(row)


# ---- slides ------------------------------------------------------------------------------------------------------
def s01_title(prs):
    s = new_slide(prs)
    band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(2.3), SLIDE_W, Inches(2.6))
    band.fill.solid(); band.fill.fore_color.rgb = TEAL_FILL; band.line.fill.background(); band.shadow.inherit = False
    box, tf = txbox(s, 0.8, 2.55, 11.7, 1.2)
    set_run(tf.paragraphs[0].add_run(), "ZDC autoresearch, Phase 6: the crystal-seeded ZDC photon finder", Pt(32), INK, bold=True)
    box, tf = txbox(s, 0.8, 3.75, 11.7, 0.9)
    set_run(tf.paragraphs[0].add_run(), "Find the ZDC photons the hadronic section loses, with the LYSO crystals in front of it",
            Pt(18), MUTED)
    box, tf = txbox(s, 0.8, 5.3, 11.7, 1.2)
    set_run(tf.paragraphs[0].add_run(), "Started and closed 2026-11-09 · one slide per try · rebuilt from the run's result files",
            Pt(14), MUTED)


def s02_start(prs):
    """The start row Y9 on the Phase 6 template: score, purity, −t resolution."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Phase 6 start row Y9 — yield, purity and −t resolution per beam")
    tr = load_json("t-resolution-Y9_external_pair.json") or {}
    rows = [["Y9 on the search halves D6s", "9x275", "9x130"]]
    r = {b: rows_of(BASE, f"D6s_{b}") or rows_of("Y9_external_pair", f"D6s_{b}") for b in ("9x275", "9x130")}
    rows.append(["N_found / N_expected", *[(f"{r[b]['N_found']} / {r[b]['N_expected']:.0f}" if r[b] else PENDING) for b in ("9x275", "9x130")]])
    rows.append(["yield (reachable)", *[(f"{100 * r[b]['yield']:.2f} % ({REACH[b]} %)" if r[b] else PENDING) for b in ("9x275", "9x130")]])
    rows.append(["purity in the ±30 MeV window", *[(pct(r[b]["purity"], 1) if r[b] else PENDING) for b in ("9x275", "9x130")]])
    rows.append(["−t resolution σ68 of found Λ", *[(f"{tr[b]['sigma68']:.2f} GeV²" if b in tr else PENDING) for b in ("9x275", "9x130")]])
    rows.append(["−t within ±0.1 GeV²", *[(pct(tr[b]["within_0.1"], 0) if b in tr else PENDING) for b in ("9x275", "9x130")]])
    add_table(s, rows, 0.55, 1.35, 7.4, TEAL, TEAL_FILL, INK, col_widths=[0.46, 0.27, 0.27], size=Pt(12.5))
    card(s, 8.2, 1.35, 4.58, 2.1, "Kept from Phase 5", [
        "score: N_found pooled over D6s 9x275 + 9x130",
        "selector 463: paired z ≥ 3, purity z_P ≥ −2",
        "held out: D6h, checkpoint every 5 tries",
        "fair play: 460 F1–F6, 465 patch scan",
        "new: 468, F3 for crystal clusters"], PURPLE, PURPLE_FILL, size=Pt(12))
    if tr:
        b = tr.get("9x275", {}).get("bins", {})
        txt = ", ".join(f"{k.replace('-', '–')}: {v['sigma68']:.2f}" for k, v in b.items())
        card(s, 0.55, 4.6, 12.23, 1.4, "−t resolution at 9x275 by true −t (GeV², σ68)", [
            txt, f"beam spread {tr['9x275']['beam_part_sigma68']:.3f} GeV², detector {tr['9x275']['detector_part_sigma68']:.3f} GeV² (476)"],
            BLUE, GREY_FILL, size=Pt(12))
    takeaway(s, "The all-ZDC regime holds 28 % of expected at 9x275; a ZDC photon without a photon neutral is its largest loss.")


def s03_crystal_section(prs):
    """Diagram: the crystal section, today's clustering and the crystal-seeded candidate (Z1)."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "LYSO crystal section — today's clustering and a crystal-seeded photon", PURPLE)
    dia_box(s, 0.55, 1.4, 3.0, 1.25, "LYSO crystals", GREY_FILL, GREY_BAR, INK, "20 × 20, 30.3 mm pitch, 70 mm\nreco hits clip at 2 GeV")
    dia_box(s, 0.55, 3.2, 3.0, 1.25, "SiPM-on-tile Hcal", GREY_FILL, GREY_BAR, INK, "behind the crystals\nthe clusters the pairing reads")
    dia_box(s, 4.3, 1.2, 3.7, 1.1, "today: island, 50 cm", GREY_FILL, GREY_BAR, INK, "one crystal cluster per event\nthe neutrals do not read it")
    dia_box(s, 4.3, 2.55, 3.7, 1.3, "Z1: crystal-scale islands", PURPLE_FILL, PURPLE, INK, "8 neighbours, split at local maxima,\nenergy shared by distance")
    dia_box(s, 4.3, 4.1, 3.7, 1.1, "Hcal column behind", PURPLE_FILL, PURPLE, INK, "rec-hit energy within 45 mm\nof the line from the IP")
    dia_arrow(s, 3.55, 2.0, 4.3, 1.75, MUTED); dia_arrow(s, 3.55, 2.0, 4.3, 3.2, MUTED); dia_arrow(s, 3.55, 3.8, 4.3, 4.65, MUTED)
    dia_box(s, 8.75, 2.35, 4.0, 1.7, "crystal-seeded photon", PURPLE_FILL, PURPLE, INK,
            "a crystal cluster with no tagged Hcal photon behind it;\ndirection from the crystals; energy from the gun\nlaw (crystal + column); the column leaves the neutron")
    dia_arrow(s, 8.0, 3.2, 8.75, 3.2, MUTED); dia_arrow(s, 8.0, 4.65, 8.75, 3.7, MUTED)
    card(s, 0.55, 5.45, 12.23, 1.05, "In the pairing", [
        "new hypotheses beside Y9's: crystal + tagged Hcal photon, crystal + crystal, crystal + B0 photon; the lowest score wins as before"],
        PURPLE, PURPLE_FILL, size=Pt(12))
    add_notes(s, "Geometry from the crystal rec hits (proton frame): x, y centres −287.85 … +287.85 mm in 20 steps, z 35 737 mm. "
                 "Today's crystal clustering: src/detectors/ZDC/ZDC.cc, localDistXY 50 cm, splitCluster true.")


def s04_scope(prs):
    """Step 0 item 1: the scope study (477) on the base row."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Step 0 scope study — crystal candidates for the photons Y9 misses (9x275)")
    d = load_json(f"crystal-scope-{BASE}-D6s_9x275-step0.json") or {}
    inv, em = d.get("inventory", {}), d.get("emulation", {})
    def g(k):
        return inv.get(k, PENDING) if inv else PENDING
    rows = [["ZDC photons of a Λ → nπ⁰ (search half)", "all in the ZDC", "one γ in B0"],
            ["without a matched photon neutral in Y9", g("all-ZDC ZDC photons missing"), g("B0+ZDC ZDC photons missing")],
            ["… with a pure crystal cluster ≥ 0.5 GeV", g("all-ZDC ZDC photons missing: pure crystal cluster ≥ 0.5 GeV"),
             g("B0+ZDC ZDC photons missing: pure crystal cluster ≥ 0.5 GeV")],
            ["Λ missed with both photons available (oracle)", em.get("all-ZDC: missed, both photons have a candidate (oracle)", PENDING),
             em.get("B0+ZDC: missed, both photons have a candidate (oracle)", PENDING)]]
    add_table(s, rows, 0.55, 1.35, 12.23, TEAL, TEAL_FILL, INK, col_widths=[0.5, 0.25, 0.25], size=Pt(12.5))
    nets = {k: v for k, v in em.items() if k.endswith(" net")}
    if nets:
        best = max({k.split(": ")[1].rsplit(" net", 1)[0] for k in nets}, key=lambda n: sum(em.get(f"{r}: {n} net", 0) for r in ("all-ZDC", "B0+ZDC", "B0+B0")))
        tot = sum(em.get(f"{r}: {best} net", 0) for r in ("all-ZDC", "B0+ZDC", "B0+B0"))
        card(s, 0.55, 3.7, 12.23, 1.45, f"Emulated gain, best variant ({best})", [
            f"all-ZDC {em.get(f'all-ZDC: {best} net', 0):+d}, one γ in B0 {em.get(f'B0+ZDC: {best} net', 0):+d}, both γ in B0 {em.get(f'B0+B0: {best} net', 0):+d}: net {tot:+d} found Λ",
            f"emulator check: Y9's own decision gives {em.get('all-ZDC: emulated row good', PENDING)} / {em.get('B0+ZDC: emulated row good', PENDING)} "
            f"against the row's {em.get('all-ZDC: found by the row', PENDING)} / {em.get('B0+ZDC: found by the row', PENDING)}",
            "stop rule: below +50 pooled the phase stops here"], PURPLE, PURPLE_FILL, size=Pt(12.5))
    else:
        card(s, 0.55, 3.7, 12.23, 1.2, "Emulated gain", ["pending: the photon law is fitted on the guns D2 + D2c first (F4)"], PURPLE, PURPLE_FILL)
    add_notes(s, f"477 on {BASE}, D6s_9x275; parameters {d.get('params')}; law {d.get('law')}.")


def fair_play(row):
    """PASS, FAIL or pending: 460 on the MSF outputs (its F1d replaced by 478 on the as-built tree, D-default-49) and 468
    on both search halves."""
    fp = load_json(f"fair-play-{row}-msf.json")
    if not fp:
        return PENDING
    fails = [c for c in fp["checks"] if c["status"] == "FAIL" and not (c["rule"] == "F1" and c["check"] == "d janadot")]
    f1d = next((c for c in fp["checks"] if c["rule"] == "F1" and c["check"] == "d janadot"), None)
    if f1d and f1d["status"] == "FAIL":
        built = load_json(f"f1-as-built-{row}.json")
        if not built or built["verdict"] != "PASS":
            fails.append(f1d)
    for ds in ("D6s_9x275", "D6s_9x130"):
        c = load_json(f"crystal-f3-{row}-{ds}.json")
        if c and c["verdict"] != "PASS":
            fails.append(c)
    return "FAIL" if fails else "PASS"


def try_slide(prs, t):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, t["title"], PURPLE)
    sel = load_json(f"msf-select-{t['row']}-vs-{t['best']}-D6s.json") or {}
    fp = fair_play(t["row"])
    verdict = "FOUL" if fp == "FAIL" else sel.get("verdict", PENDING)
    ch = 0.6 + 0.29 * len(t["change"]) + 0.21 * sum(len(c) > 95 for c in t["change"])
    card(s, 0.55, 1.3, 7.3, ch, "Change", t["change"], PURPLE, PURPLE_FILL, size=Pt(12))
    ph = 0.85 + 0.21 * (len(t["prediction"]) > 95)
    card(s, 0.55, 1.3 + ch + 0.2, 7.3, ph, "Prediction (written before launch)", [t["prediction"]], BLUE, GREY_FILL, size=Pt(12))
    rows = [["search half", "best", "this try"]]
    for beam in ("9x275", "9x130"):
        x = (sel.get("beams") or {}).get(beam)
        rows.append([f"{beam} N_found", str(x["best"]["N_found"]) if x else PENDING, str(x["candidate"]["N_found"]) if x else PENDING])
        rows.append([f"{beam} purity", pct(x["best"]["purity"], 1) if x else PENDING, pct(x["candidate"]["purity"], 1) if x else PENDING])
    add_table(s, rows, 8.1, 1.3, 4.68, PURPLE, PURPLE_FILL, INK, col_widths=[0.44, 0.28, 0.28], size=Pt(12))
    box, tf = txbox(s, 8.1, 3.85, 4.7, 0.9)
    set_run(tf.paragraphs[0].add_run(), (f"paired: b {sel['b']}, c {sel['c']}, z {sel['z']:+.2f}; purity z_P {sel['z_purity']:+.2f}"
                                         if sel else "paired test: " + PENDING), Pt(13), INK, bold=True)
    acc, fill = VERDICT_COLOR.get(verdict, (MUTED, GREY_FILL))
    chip(s, 8.1, 4.6, 2.3, verdict, acc, fill, size=Pt(12))
    chip(s, 10.45, 4.6, 2.3, f"fair play {fp}", GREEN if fp == "PASS" else ORANGE if fp == "FAIL" else MUTED,
         GREEN_FILL if fp == "PASS" else ORANGE_FILL if fp == "FAIL" else GREY_FILL, size=Pt(12))
    tr = (load_json(f"t-resolution-{t['row']}.json") or {}).get("9x275")
    if tr:
        box, tf = txbox(s, 8.1, 5.2, 4.7, 0.5)
        set_run(tf.paragraphs[0].add_run(), f"−t σ68 at 9x275: {tr['sigma68']:.3f} GeV² (476)", Pt(12), MUTED)
    add_notes(s, f"Row {t['row']} against {t['best']}; selector msf-select-{t['row']}-vs-{t['best']}-D6s.json (463); "
                 f"fair play: fair-play-{t['row']}-msf.json (460, its F1d from f1-as-built-{t['row']}.json, 478, D-default-49) and "
                 f"crystal-f3-{t['row']}-D6s_*.json (468).")


def s01b_waterfall(prs):
    """The score step by step: every try's paired result against the best of its time (463 files)."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Phase 6 tries — Λ found on the search halves, step by step")
    rows = [["try", "change", "9x275", "9x130", "score", "purity", "z", "−t σ68 9x275", "verdict"]]
    for t in TRIES:
        sel = load_json(f"msf-select-{t['row']}-vs-{t['best']}-D6s.json")
        tr = (load_json(f"t-resolution-{t['row']}.json") or {}).get("9x275")
        fp = fair_play(t["row"])
        if not sel:
            rows.append([t["id"], t["title"].split("—", 1)[1].strip(), PENDING, PENDING, PENDING, PENDING, PENDING, PENDING, PENDING])
            continue
        b = sel["beams"]
        rows.append([t["id"], t["title"].split("—", 1)[1].strip(),
                     f"{b['9x275']['best']['N_found']} → {b['9x275']['candidate']['N_found']}",
                     f"{b['9x130']['best']['N_found']} → {b['9x130']['candidate']['N_found']}",
                     f"{sel['N_found']['best']} → {sel['N_found']['candidate']}",
                     f"{100 * sel['purity']['best']:.1f} → {100 * sel['purity']['candidate']:.1f} %",
                     f"{sel['z']:+.1f}", f"{tr['sigma68']:.3f} GeV²" if tr else PENDING,
                     "FOUL" if fp == "FAIL" else sel["verdict"]])
    add_table(s, rows, 0.55, 1.3, 12.23, PURPLE, PURPLE_FILL, INK, col_widths=[0.05, 0.33, 0.09, 0.08, 0.1, 0.11, 0.05, 0.09, 0.1],
              size=Pt(10.5), row_h=Inches(0.42))
    tr0 = (load_json("t-resolution-Y9_external_pair.json") or {}).get("9x275")
    accepted = [t for t in TRIES if (load_json(f"msf-select-{t['row']}-vs-{t['best']}-D6s.json") or {}).get("verdict") == "ACCEPTED"]
    last = load_json(f"msf-select-{accepted[-1]['row']}-vs-{accepted[-1]['best']}-D6s.json") if accepted else None
    r0 = [rows_of(BASE, f"D6s_{b}") for b in ("9x275", "9x130")]
    if last and all(r0):
        a = r0[0]["N_found"] + r0[1]["N_found"]
        c = last["N_found"]["candidate"]
        tr_best = (load_json(f"t-resolution-{accepted[-1]['row']}.json") or {}).get("9x275")
        text = f"Score {a} → {c} (+{100 * (c - a) / a:.0f} %) since the start row Y9"
        if tr0 and tr_best:
            text += f"; −t σ68 at 9x275 {tr0['sigma68']:.3f} → {tr_best['sigma68']:.3f} GeV² (Q22)"
        takeaway(s, text + ".")


def checkpoint_slide(prs, n, best, d4row, best_label):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, f"Checkpoint {n} — {best_label} on the held-out MSF halves and the D4 gun")
    h = load_json(f"msf-select-{best}-vs-{BASE}-D6h.json") or {}
    rows = [["N_found (yield)", "Y9, search", f"{best_label}, search", "Y9, held out", f"{best_label}, held out", "reachable"]]
    for beam, reach in (("9x275", 43.6), ("9x130", 8.0)):
        x = (h.get("beams") or {}).get(beam)
        ra, rc = rows_of(BASE, f"D6s_{beam}"), rows_of(best, f"D6s_{beam}")
        a, c = (ra or {}).get("N_found"), (rc or {}).get("N_found")
        rows.append([beam, f"{a} ({100 * a / 7160:.2f} %)" if a else PENDING, f"{c} ({100 * c / 7160:.2f} %)" if c else PENDING,
                     f"{x['best']['N_found']} ({100 * x['best']['yield']:.2f} %)" if x else PENDING,
                     f"{x['candidate']['N_found']} ({100 * x['candidate']['yield']:.2f} %)" if x else PENDING, f"{reach} %"])
    rows.append(["purity, held out (pooled)", "", "", pct(h.get("purity", {}).get("best"), 1) if h else PENDING,
                 pct(h.get("purity", {}).get("candidate"), 1) if h else PENDING, ""])
    add_table(s, rows, 0.55, 1.35, 12.23, TEAL, TEAL_FILL, INK, col_widths=[0.2, 0.16, 0.16, 0.16, 0.16, 0.16], size=Pt(12.5))
    v = h.get("verdict", PENDING)
    chip(s, 0.55, 3.55, 3.4, f"held out: {v}", GREEN if v == "REPRODUCES" else ORANGE, GREEN_FILL if v == "REPRODUCES" else ORANGE_FILL)
    box, tf = txbox(s, 4.15, 3.6, 8.6, 0.4)
    set_run(tf.paragraphs[0].add_run(), (f"b {h['b']}, c {h['c']}, z {h['z']:+.2f}; purity z_P {h['z_purity']:+.2f}" if h else PENDING), Pt(13), INK, bold=True)
    import csv
    try:
        with open(os.path.join(PERF, "headline.csv")) as fh:
            hd = {r["row"]: r for r in csv.DictReader(fh)}
    except OSError:
        hd = {}
    f = lambda r, c: (f"{float(r[c]):.2f} %" if r and r.get(c) not in (None, "", "nan") else PENDING)
    hy, hb = hd.get(d4row), hd.get("CP5_2_Y9_D4")
    card(s, 0.55, 4.3, 12.23, 0.85, "D4 Λ gun, S4a_tm per thrown Λ → nπ⁰ (reported, never selected on; 410 credits Hcal clusters only)", [
        f"Y9: {f(hb, 'S4a_tm_per_thrown_mean')} mean, {f(hb, 'S4a_tm_per_thrown_275')} at 275 GeV;  "
        f"{best_label}: {f(hy, 'S4a_tm_per_thrown_mean')} mean, {f(hy, 'S4a_tm_per_thrown_275')} at 275 GeV"], BLUE, GREY_FILL, size=Pt(12.5))
    takeaway(s, "The held-out halves never chose anything; they confirm or revert the gain of the search halves.")


def s98_t_tradeoff(prs):
    """Q22: the Λ count against the −t resolution, Y9 → Z5 → Z6 (476 and 463 files)."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Λ count against −t resolution — Y9, Z5 and Z6 on the search halves")
    rows = [["row", "N_found (9x275 + 9x130)", "purity", "−t σ68 9x275", "−t σ68 9x130", "−t within ±0.1 GeV², 9x275"]]
    for row, lab in (("Y9_external_pair", "Y9 (start)"), ("Z5_crystal_energy_alt", "Z5 (accepted)"), ("Z6_alt_column_out", "Z6 (the base, D-user-44)")):
        r = [rows_of(row if row != "Y9_external_pair" else BASE, f"D6s_{b}") for b in ("9x275", "9x130")]
        tr = load_json(f"t-resolution-{row}.json") or {}
        nf = (r[0]["N_found"] + r[1]["N_found"]) if all(r) else None
        nw = (r[0]["N_window"] + r[1]["N_window"]) if all(r) else None
        rows.append([lab, str(nf) if nf else PENDING, f"{100 * nf / nw:.1f} %" if nf else PENDING,
                     f"{tr['9x275']['sigma68']:.3f} GeV²" if "9x275" in tr else PENDING,
                     f"{tr['9x130']['sigma68']:.3f} GeV²" if "9x130" in tr else PENDING,
                     pct(tr["9x275"]["within_0.1"], 0) if "9x275" in tr else PENDING])
    add_table(s, rows, 0.55, 1.35, 12.23, TEAL, TEAL_FILL, INK, col_widths=[0.22, 0.17, 0.11, 0.15, 0.15, 0.2], size=Pt(12.5))
    card(s, 0.55, 3.4, 12.23, 1.75, "Why Z5 measures −t worse and Z6 does not", [
        "Z5 gives tagged Hcal photons the crystal law's energy when it fits better; their Hcal column beyond the cluster stays in the neutron",
        "the Λ energy reads high: reco / true median 1.110 (Z4 1.073, same Λ); Z6 removes that column from the neutron",
        "Z6 loses 29 found Λ against Z5 (z −2.80) and measures −t better than the start row"], PURPLE, PURPLE_FILL, size=Pt(12.5))
    takeaway(s, "Q22: the user chose Z6, the better −t, as the base for Z7 and Z8 (D-user-44).")


def s99_checkpoint1(prs):
    checkpoint_slide(prs, 1, "Z5_crystal_energy_alt", "CP6_1_Z5_D4", "Z5")


def plot_slide(prs, ttl, png, caption_text, takeaway_text):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, ttl)
    add_picture_fit(s, os.path.join(PLOTS, png), 0.55, 1.3, 12.23, 4.6, MUTED, caption=False, missing=missing)
    box, tf = txbox(s, 0.55, 6.0, 12.23, 0.5)
    set_run(tf.paragraphs[0].add_run(), caption_text, Pt(11), MUTED, italic=True)
    takeaway(s, takeaway_text, y=6.6)


def s95_found_plot(prs):
    plot_slide(prs, "Phase 6 found Λ per try — MSF search and held-out halves", "p6_found_per_try.png",
               "Λ → nπ⁰ found per expected (210). Filled: accepted by the selector (463); open: not accepted. Diamonds: the "
               "held-out halves D6h. Z6 is the base by the user's choice (D-user-44).",
               "Crystal-seeded photons, the isolation term and the axis law took 9x275 from 17.7 % to 23.6 %; the held-out halves agree.")


def s96_t_plot(prs):
    plot_slide(prs, "−t resolution of the found Λ per −t bin — Y9, Z5, Z8", "p6_t_resolution.png",
               "σ68 of −t reco − true (476) on each row's found Λ, by true −t; bins with fewer than 30 Λ left out.",
               "Z8, the current best, finds the most Λ with the best −t at 9x275; Z5 had paid for its count in −t.")


def s97_mass_plot(prs):
    plot_slide(prs, "Λ mass on MSF 9x275 — Y9 and Z8", "p6_mass.png",
               "Every ReconstructedLambdas mass on the 9x275 search half and the truth-matched Λ → nπ⁰ (210); band: ±30 MeV.",
               "More truth-matched Λ in a narrower peak; the purity in the window rises from 26 % to 31 %.")


def s99b_checkpoint2(prs):
    checkpoint_slide(prs, 2, "Z8_hcal_axis_law", "CP6_2_Z8_D4", "Z8")


def s99c_losses(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Remaining losses after Z8 — what the chooser picks instead (9x275)")
    # source: space/perf/crystal-scope-MSF6_Y9-D6s_9x275-z9front.json and -z8whyb0.json (477 --why-all on Z8's settings)
    rows = [["regime", "the chooser's pick for a missed Λ whose photons both have a candidate", "Λ"],
            ["all in the ZDC", "one photon right, the other a neutron fragment", "110"],
            ["", "the right pair, mass out of the window (109 high)", "113"],
            ["", "one photon right, the other a mixed Hcal cluster", "93"],
            ["", "one photon right, the other a crystal cluster not a photon's", "64"],
            ["γ B0 + γ ZDC", "B0 photon right, ZDC photon wrong", "91"],
            ["", "the right pair, mass out of the window", "55"],
            ["", "a B0 pair won", "27"]]
    add_table(s, rows, 0.55, 1.35, 12.23, TEAL, TEAL_FILL, INK, col_widths=[0.18, 0.72, 0.10], size=Pt(12.5))
    card(s, 0.55, 4.85, 12.23, 1.3, "Tried in emulation, not built (gain under +30)", [
        "crystal energy in front as a second term +15; isolation weight 1–4 flat; Z5's crystal-law option dropped −4",
        "EEMC-P photons (146 Λ in the reachable yield): soft, no pure EEMC-P photon neutral — outside the ZDC chain"], ORANGE, ORANGE_FILL, size=Pt(12))
    takeaway(s, "No single cause above ~110 Λ remains among Λ whose photons both have a clean candidate.")


def try_slides(prs):
    for t in TRIES:
        try_slide(prs, t)


# ---- closing slides (the user's close, D-user-45) ----------------------------------------------------------------
VERDICT_BAR = {"ACCEPTED": GREEN, "INCONCLUSIVE": ORANGE, "FOUL": ORANGE, "REJECTED": MUTED}
N_EXP = 7160                                   # source: msf-regimes-*-D6s_*.json, N_expected per search half (210)
REACH_POOLED = sum(REACH.values()) / 100 * N_EXP
CEILING, CEILING_275 = 14.1, 27.8              # source: Phase 4 deck, the D4 ceilings (perfect separation, P1b resolution)
D4_ROW = {"Z5": "CP6_1_Z5_D4", "Z8": "CP6_2_Z8_D4"}   # D4 reconstructed only at the checkpoints


def sel_of(t, half="D6s"):
    return load_json(f"msf-select-{t['row']}-vs-{t['best']}-{half}.json")


def headline_row(row):
    import csv
    try:
        with open(os.path.join(PERF, "headline.csv")) as fh:
            return next((r for r in csv.DictReader(fh) if r["row"] == row), None)
    except OSError:
        return None


def d4_value(row, col):
    v = (headline_row(row) or {}).get(col)
    return None if v in (None, "", "nan") else float(v)


def verdict_of(t):
    sel = sel_of(t)
    if not sel:
        return PENDING
    return "FOUL" if fair_play(t["row"]) == "FAIL" else sel["verdict"]


def s01a_outcome(prs):
    """The phase in four numbers: start row Y9 against the final row Z8."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Phase 6 outcome — Y9 → Z8 on the MSF search and held-out halves")
    a = [rows_of(BASE, f"D6s_{b}") for b in ("9x275", "9x130")]
    c = [rows_of("Z8_hcal_axis_law", f"D6s_{b}") for b in ("9x275", "9x130")]
    h = load_json("msf-select-Z8_hcal_axis_law-vs-MSF6_Y9-D6h.json") or {}
    t0 = (load_json("t-resolution-Y9_external_pair.json") or {}).get("9x275")
    t1 = (load_json("t-resolution-Z8_hcal_axis_law.json") or {}).get("9x275")
    if all(a) and all(c):
        na, nc = a[0]["N_found"] + a[1]["N_found"], c[0]["N_found"] + c[1]["N_found"]
        pa = na / (a[0]["N_window"] + a[1]["N_window"]); pc = nc / (c[0]["N_window"] + c[1]["N_window"])
        stats = [(f"{na} → {nc}", f"Λ found, search halves (+{100 * (nc - na) / na:.0f} %)"),
                 (f"{h['N_found']['best']} → {h['N_found']['candidate']}" if h else PENDING,
                  f"held-out halves (z {h['z']:+.1f})" if h else "held-out halves"),
                 (f"{100 * pa:.1f} → {100 * pc:.1f} %", "purity in the ±30 MeV window"),
                 (f"{t0['sigma68']:.3f} → {t1['sigma68']:.3f}" if t0 and t1 else PENDING, "−t σ68 at 9x275, GeV²")]
        for i, (big, lab) in enumerate(stats):
            stat_callout(s, 0.55 + i * 3.08, 1.5, 2.95, big, lab, TEAL, MUTED, big_size=Pt(32), label_size=Pt(13))
        rows = [["yield (found / expected)", "Y9, start", "Z8, final", "reachable"],
                ["9x275", f"{100 * a[0]['yield']:.2f} %", f"{100 * c[0]['yield']:.2f} %", f"{REACH['9x275']} %"],
                ["9x130", f"{100 * a[1]['yield']:.2f} %", f"{100 * c[1]['yield']:.2f} %", f"{REACH['9x130']} %"]]
        add_table(s, rows, 0.55, 3.45, 6.2, TEAL, TEAL_FILL, INK, col_widths=[0.37, 0.21, 0.21, 0.21], size=Pt(12.5))
    card(s, 7.0, 3.45, 5.78, 2.05, "What Z8 adds to Y9", [
        "crystal-seeded photon candidates in the ZDC pairing (Z1b, Z2)",
        "a narrower Λ-mass term in the pairing (Z4)",
        "the crystal law's energy offered to Hcal photons (Z5), its column out of the neutron (Z6)",
        "an isolation term against neutron fragments (Z7)",
        "the axis-law energy for Hcal photons (Z8)"], PURPLE, PURPLE_FILL, size=Pt(12))
    if all(a) and all(c):
        takeaway(s, f"Z8 finds {100 * c[0]['yield']:.1f} % of expected at 9x275, "
                    f"{100 * c[0]['yield'] / REACH['9x275'] * 100:.0f} % of the reachable yield; closed 2026-11-09 (D-user-45).")


def s01c_score_bars(prs):
    """Score per try, as the Phase 4 deck's bar slide: N_found pooled over the search halves, colour = verdict."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Score per try — Λ → nπ⁰ found on the MSF search halves, 9x275 + 9x130")
    r0 = [rows_of(BASE, f"D6s_{b}") for b in ("9x275", "9x130")]
    tr0 = (load_json("t-resolution-Y9_external_pair.json") or {}).get("9x275")
    rows = []
    if all(r0):
        n = r0[0]["N_found"] + r0[1]["N_found"]
        rows.append(("Y9 (start)", n, GREY_BAR, f"{n}  ({100 * r0[0]['yield']:.1f} % · {100 * r0[1]['yield']:.2f} %)  "
                     f"purity {100 * n / (r0[0]['N_window'] + r0[1]['N_window']):.1f} %" + (f"  −t {tr0['sigma68']:.3f}" if tr0 else "")))
    for t in TRIES:
        sel = sel_of(t)
        label = t["id"] + (" (base)" if t["id"] == "Z6" else "")
        if not sel:
            rows.append((label, None, MUTED, PENDING))
            continue
        b = sel["beams"]
        tr = (load_json(f"t-resolution-{t['row']}.json") or {}).get("9x275")
        n = sel["N_found"]["candidate"]
        rows.append((label, n, VERDICT_BAR.get(verdict_of(t), MUTED),
                     f"{n}  ({100 * b['9x275']['candidate']['yield']:.1f} % · {100 * b['9x130']['candidate']['yield']:.2f} %)  "
                     f"purity {100 * sel['purity']['candidate']:.1f} %" + (f"  −t {tr['sigma68']:.3f}" if tr else "")))
    hbars(s, rows, 0.55, 1.6, 10.4, 0.5, REACH_POOLED, INK, MUTED, label_w=1.6, size=Pt(12), text_w=4.6,
          mark=(REACH_POOLED, f"reachable {REACH_POOLED:.0f}"))
    box, tf = txbox(s, 0.55, 6.15, 12.23, 0.5)
    set_run(tf.paragraphs[0].add_run(), "Bar: found Λ pooled over the search halves (463). Text: found (yield 9x275 · 9x130), purity, "
            "−t σ68 at 9x275 in GeV² (476). Colour = verdict: green accepted, orange inconclusive, grey rejected. Z6 was rejected "
            "by the selector and made the base by the user for its −t (D-user-44). Rule: the reachable yield, pooled.",
            Pt(10.5), MUTED, italic=True)
    if all(r0) and rows[-1][1]:
        takeaway(s, f"Y9 {rows[0][1]} → Z8 {rows[-1][1]} found (+{100 * (rows[-1][1] - rows[0][1]) / rows[0][1]:.0f} %): "
                    f"{100 * rows[-1][1] / REACH_POOLED:.0f} % of the reachable yield.")


def s01d_d4_bars(prs):
    """Phase 4's own chart continued: S4a_tm per thrown Λ → nπ⁰ on the D4 gun, where Phase 6 reconstructed D4."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "D4 gun score per try — S4a_tm per thrown Λ → nπ⁰, mean over 100–275 GeV")
    rows = []
    for lab, row in (("R1 (Phase 4 start)", "R1_pr3064"), ("X9 (Phase 4 end)", "X9_pairing_photon_depth"), ("Y9 (Phase 5 end)", "CP5_2_Y9_D4")):
        v, v275 = d4_value(row, "S4a_tm_per_thrown_mean"), d4_value(row, "S4a_tm_per_thrown_275")
        rows.append((lab, v, GREY_BAR, PENDING if v is None else f"{v:.2f} %  (275 GeV: {v275:.2f} %)"))
    for t in TRIES:
        row = D4_ROW.get(t["id"])
        v = d4_value(row, "S4a_tm_per_thrown_mean") if row else None
        v275 = d4_value(row, "S4a_tm_per_thrown_275") if row else None
        rows.append((t["id"], v, VERDICT_BAR.get(verdict_of(t), MUTED),
                     f"{v:.2f} %  (275 GeV: {v275:.2f} %)" if v is not None else "not reconstructed on D4"))
    hbars(s, rows, 0.55, 1.6, 7.6, 0.4, CEILING, INK, MUTED, label_w=2.3, size=Pt(11.5), text_w=3.0,
          mark=(CEILING, f"ceiling {CEILING} %"))
    box, tf = txbox(s, 0.55, 6.15, 12.23, 0.5)
    set_run(tf.paragraphs[0].add_run(), "headline.csv (441). Phase 6 reconstructed the D4 gun at its two checkpoints only (Z5, Z8); "
            "D4 is reported, never selected on, and 410 credits Hcal clusters only (a crystal-seeded photon counts as missed).",
            Pt(10.5), MUTED, italic=True)
    takeaway(s, "On the gun, Z8 stands at 8.4 % of thrown (ceiling 14.1 %), above every Phase 4 and Phase 5 row.")


# source: the tries' prediction lines (TRIES) and space/EXPERIMENTS.md, pooled over the search halves
PREDICTED = {"Z1": (133, "the C++ column summed HEXPLIT subcells: 0.45 of the fitted column"),
             "Z1b": (133, "45 % of the emulated gain"),
             "Z2": (14, "the emulation said +31; the real chain gained more"),
             "Z4": (27, "held"),
             "Z5": (160, "held within 13 %"),
             "Z6": (-14, "predicted at 9x275 only; −t repaired as predicted"),
             "Z7": (88, "held within 2"),
             "Z8": (66, "held within 3")}


def s100_predictions(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Predictions against results — the eight Phase 6 tries")
    rows = [["try", "predicted gain (477)", "measured gain (463)", "verdict", "reading"]]
    for t in TRIES:
        sel = sel_of(t)
        p, reading = PREDICTED[t["id"]]
        meas = f"{sel['N_found']['candidate'] - sel['N_found']['best']:+d}".replace("-", "−") if sel else PENDING
        rows.append([t["id"], f"{p:+d}".replace("-", "−"), meas, verdict_of(t), reading])
    add_table(s, rows, 0.55, 1.3, 12.23, TEAL, GREY_FILL, INK, col_widths=[0.07, 0.17, 0.17, 0.14, 0.45], size=Pt(12),
              row_h=Inches(0.42))
    takeaway(s, "The emulator ranks ideas; it predicts counts once its decision code mirrors the C++ (Z4 on).", y=5.6)
    add_notes(s, "Predicted gains are pooled N_found over the current best, written before launch (TRIES). Z2's line used Z1b's "
                 "45 % fidelity on an emulated +31.")


def s101_gap(prs):
    """The gap to the reachable yield (482, 210, 477's oracle)."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Gap to the reachable yield after Z8 — where reachable Λ are lost")
    # source: space/reports/phase6_crystal.md, The gap to the reachable yield (482 no-candidate-causes-Z8_*.json, 210, 477)
    rows = [["per expected Λ → nπ⁰ (7160 per half)", "9x275", "9x130"],
            ["reachable: n in the ZDC, γγ in ZDC / B0 / EEMC-P", "3124 (43.6 %)", "580 (8.1 %)"],
            ["a photon has no clean cluster", "704 (9.8 %)", "200 (2.8 %)"],
            ["clean clusters, another photon picked", "~540 (7.5 %)", "~60 (0.8 %)"],
            ["the right three, mass out of the window", "~200 (2.8 %)", "~62 (0.9 %)"],
            ["found by Z8", "1686 (23.5 %)", "258 (3.6 %)"]]
    add_table(s, rows, 0.55, 1.3, 6.4, TEAL, TEAL_FILL, INK, col_widths=[0.56, 0.22, 0.22], size=Pt(12))
    card(s, 7.2, 1.3, 5.58, 2.55, "No clean cluster, by cause (9x275 / 9x130)", [
        "inside the neutron's Hcal cluster: 278 / 12",
        "no cluster carries it (edge clippers): 118 / 18",
        "both photons in one Hcal cluster: 89 / 1",
        "a clean cluster the photon tag rejects: 10 / 1",
        "B0: below 1 GeV 63 / 42; two photons in one 48 / 36; with the neutron 44 / 11",
        "EEMC-P photon, no pure EEMC-P neutral: 54 / 79"], ORANGE, ORANGE_FILL, size=Pt(12))
    card(s, 0.55, 4.2, 12.23, 1.35, "The largest single loss", [
        "late decays put the photon a median 24 mm from the neutron at the Hcal face; one Hcal cluster holds both",
        "all-ZDC Λ decaying 30–40 m from the IP are found at 6 %, before 20 m at 61–63 %",
        "53 of the 278 have a clean crystal cluster that the veto (39) or the 0.3 GeV floor (14) drops"],
        PURPLE, PURPLE_FILL, size=Pt(11.5))
    takeaway(s, "Z8 finds 54 % of the reachable Λ at 9x275; no single remaining cause is above 6 % of the reachable yield.")


def s102_compare(prs):
    """Phase 5 and Phase 6 side by side (as the Phase 5 deck's Phase 4 / Phase 5 slide)."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Phase 5 and Phase 6 side by side")
    def yv(row, beam):
        r = rows_of(row, f"D6s_{beam}")
        return None if not r else 100 * r["yield"]
    f = lambda v, d=1: PENDING if v is None else f"{v:.{d}f} %"
    h5 = load_json("msf-select-Y9_external_pair-vs-MSF5_X9-D6h.json") or {}
    h6 = load_json("msf-select-Z8_hcal_axis_law-vs-MSF6_Y9-D6h.json") or {}
    pur = lambda row: (lambda r: PENDING if not all(r) else f"{100 * (r[0]['N_found'] + r[1]['N_found']) / (r[0]['N_window'] + r[1]['N_window']):.1f} %")(
        [rows_of(row, f"D6s_{b}") for b in ("9x275", "9x130")])
    tr = lambda row: (load_json(f"t-resolution-{row}.json") or {}).get("9x275")
    t5, t6 = tr("Y9_external_pair"), tr("Z8_hcal_axis_law")
    d4m = lambda row: PENDING if d4_value(row, "S4a_tm_per_thrown_mean") is None else f"{d4_value(row, 'S4a_tm_per_thrown_mean'):.2f} %"
    rows = [["", "Phase 5 — Λ → nπ⁰ on MSF events", "Phase 6 — the crystal-seeded photon finder"],
            ["start → final row", "X9 → Y9", "Y9 → Z8"],
            ["tries", "9: 7 accepted, 1 inconclusive, 1 rejected", "8: 6 accepted, 1 inconclusive, 1 rejected (made the base)"],
            ["MSF 9x275 found / expected, search", f"{f(yv('MSF5_X9', '9x275'))} → {f(yv('Y9_external_pair', '9x275'))}",
             f"{f(yv(BASE, '9x275'))} → {f(yv('Z8_hcal_axis_law', '9x275'))}"],
            ["MSF 9x130 found / expected, search", f"{f(yv('MSF5_X9', '9x130'), 2)} → {f(yv('Y9_external_pair', '9x130'), 2)}",
             f"{f(yv(BASE, '9x130'), 2)} → {f(yv('Z8_hcal_axis_law', '9x130'), 2)}"],
            ["found, held-out halves", f"{h5['N_found']['best']} → {h5['N_found']['candidate']}" if h5 else PENDING,
             f"{h6['N_found']['best']} → {h6['N_found']['candidate']}" if h6 else PENDING],
            ["purity in the window, search (pooled)", f"{pur('MSF5_X9')} → {pur('Y9_external_pair')}", f"{pur(BASE)} → {pur('Z8_hcal_axis_law')}"],
            ["−t σ68 at 9x275", f"Y9 {t5['sigma68']:.3f} GeV² (X9 not measured)" if t5 else PENDING, f"{t5['sigma68']:.3f} → {t6['sigma68']:.3f} GeV²" if t5 and t6 else PENDING],
            ["D4 S4a_tm per thrown, mean", f"{d4m('X9_pairing_photon_depth')} → {d4m('CP5_2_Y9_D4')}", f"{d4m('CP5_2_Y9_D4')} → {d4m('CP6_2_Z8_D4')}"],
            ["what changed", "vertex lever arm, pairing with B0 photons, B0 splitting and law",
             "crystal-seeded photons, crystal and axis energy laws, isolation term"]]
    add_table(s, rows, 0.55, 1.25, 12.23, TEAL, GREY_FILL, INK, col_widths=[0.28, 0.34, 0.38], size=Pt(11.5), row_h=Inches(0.42))
    takeaway(s, "Phase 5 won in the B0 regimes, Phase 6 in the all-ZDC regime; both gains hold on the held-out halves.", y=6.0)


def s103_upstream(prs):
    """What the program has changed in EICrecon since the pin, and what of it moves collections outside the ZDC."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "EICrecon changes since the pin — the stack Phase 7 takes upstream")
    stack = [("pin e5e2a60c", "EICrecon at the program's pin", GREY_FILL, GREY_BAR),
             ("PR 3064 + PR 3063 (open upstream)", "ZDC clustering and calibration; Λ mass windows removed", GREY_FILL, GREY_BAR),
             ("Phase 4: U1–U4", "stable vertex, Λ-hypothesis pairing, core split, ZDC configuration", PURPLE_FILL, PURPLE),
             ("Phase 5: Y2, Y5, Y9 + B0 parameters", "lever-arm vertex, pairing with B0 photons, B0 splitting and law", PURPLE_FILL, PURPLE),
             ("Phase 6: Z1b–Z8 + crystal clustering", "crystal-seeded photons, energy laws, isolation term", PURPLE_FILL, PURPLE)]
    y = 1.35
    for i, (main, sub, fill, line) in enumerate(stack):
        dia_box(s, 0.55, y, 6.1, 0.78, main, fill, line, INK, sub, main_size=Pt(12.5), sub_size=Pt(10.5))
        if i < len(stack) - 1:
            dia_arrow(s, 3.6, y + 0.78, 3.6, y + 0.93, MUTED)
        y += 0.93
    card(s, 6.95, 1.35, 5.83, 1.85, "Moves collections outside the ZDC", [
        "B0ECalClusters: island splitting at local maxima (Phase 5)",
        "EcalFarForwardZDCClusters at the crystal scale: zdc_lyso reads them",
        "three new inputs of the neutrals factory in reco.cc",
        "ImagingTopoCluster is shared with other calorimeters: core split off by default, never measured"],
        ORANGE, ORANGE_FILL, size=Pt(12))
    card(s, 6.95, 3.45, 5.83, 1.15, "Not yet code", [
        "Z8's 15 run-time parameters are not code defaults",
        "clang-format, units, Catch2 tests, defaults off in the Config structs"], BLUE, GREY_FILL, size=Pt(12))
    caption_box, tf = txbox(s, 0.55, 6.1, 12.23, 0.4)
    set_run(tf.paragraphs[0].add_run(), "Whole diff from a15b0db6: space/notes/patches/phase6_working_tree.patch (1054 added lines, "
            "7 files). Uncommitted; nothing pushed.", Pt(10.5), MUTED, italic=True)
    takeaway(s, "Phase 7 splits this stack into pull requests and measures what Phase 4 only argued.", y=6.55)


def s104_next(prs):
    """Phase 7, prepared: the check every pull-request unit passes (loop v7)."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Phase 7 (prepared) — the changes as EICrecon pull requests, one unit at a time")
    steps = [("split", "units in order rebuild\nthe Phase 6 tree"),
             ("build", "clang-format, units,\ntests, defaults off"),
             ("switch off", "every collection\nidentical to the base"),
             ("other calorimetry", "D5 DIS + guns: 130\nidentity, capybara 0"),
             ("benchmarks", "declared collections:\nzdc_*, zdc_lyso, B0"),
             ("PR draft", "evidence + text;\nthe user opens it")]
    w, gap = 1.88, 0.19
    for i, (main, sub) in enumerate(steps):
        x = 0.55 + i * (w + gap)
        dia_box(s, x, 1.45, w, 1.2, main, PURPLE_FILL if i not in (3, 4) else ORANGE_FILL, PURPLE if i not in (3, 4) else ORANGE,
                INK, sub, main_size=Pt(12.5), sub_size=Pt(10.5))
        if i < len(steps) - 1:
            dia_arrow(s, x + w + 0.02, 2.05, x + w + gap - 0.02, 2.05, MUTED)
    card(s, 0.55, 3.0, 6.0, 2.2, "Units proposed (Step 0 confirms the split)", [
        "photon depth limit measured from the ZDC face (a bug fix)",
        "ImagingTopoCluster core split, off by default",
        "LambdaReconstruction vertex with lever arms",
        "ZDC Λ pairing; crystal-seeded photons (both off by default)",
        "LYSO clustering at the crystal scale; B0 ECal splitting and law",
        "the ZDC configuration that switches it on: reproduces Z8"], PURPLE, PURPLE_FILL, size=Pt(12))
    card(s, 6.78, 3.0, 6.0, 2.2, "Rules", [
        "each unit declares the collections it may move; every other one stays byte-identical",
        "orange steps: the user's 'other calorimetry not affected'",
        "the cleaned-up full stack reproduces Z8 Λ by Λ",
        "the user opens every pull request; nothing is pushed",
        "start: the loop v7 line in CLAUDE.md"], TEAL, TEAL_FILL, size=Pt(12))
    takeaway(s, "Open before the start: the base (EICrecon main with the open PRs 3064 and 3063, or the pin) and two benchmark samples.")


SLIDES = [s01_title, s01a_outcome, s01c_score_bars, s01d_d4_bars, s01b_waterfall, s02_start, s03_crystal_section, s04_scope,
          try_slides, s98_t_tradeoff, s99_checkpoint1, s99b_checkpoint2, s100_predictions, s95_found_plot, s96_t_plot,
          s97_mass_plot, s99c_losses, s101_gap, s102_compare, s103_upstream, s104_next]


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
