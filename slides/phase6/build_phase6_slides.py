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
PLOTS = os.path.join(HERE, "plots")
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
    set_run(tf.paragraphs[0].add_run(), "Started 2026-11-09 · one slide per try · rebuilt from the run's result files", Pt(14), MUTED)


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
    card(s, 0.55, 4.3, 12.23, 1.3, "D4 Λ gun, S4a_tm per thrown Λ → nπ⁰ (reported, never selected on; 410 credits Hcal clusters only)", [
        f"Y9: {f(hb, 'S4a_tm_per_thrown_mean')} mean, {f(hb, 'S4a_tm_per_thrown_275')} at 275 GeV;  "
        f"{best_label}: {f(hy, 'S4a_tm_per_thrown_mean')} mean, {f(hy, 'S4a_tm_per_thrown_275')} at 275 GeV"], BLUE, GREY_FILL, size=Pt(12.5))
    takeaway(s, "The held-out halves never chose anything; they confirm or revert the gain of the search halves.")


def s98_t_tradeoff(prs):
    """Q22: the Λ count against the −t resolution, Y9 → Z5 → Z6 (476 and 463 files)."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Λ count against −t resolution — Y9, Z5 and Z6 on the search halves")
    rows = [["row", "N_found (9x275 + 9x130)", "purity", "−t σ68 9x275", "−t σ68 9x130", "−t within ±0.1 GeV², 9x275"]]
    for row, lab in (("Y9_external_pair", "Y9 (start)"), ("Z5_crystal_energy_alt", "Z5 (current best)"), ("Z6_alt_column_out", "Z6 (REJECTED by 463)")):
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
    takeaway(s, "Q22 for the user: the base for the next tries — Z5 (more Λ) or Z6 (better −t).")


def s99_checkpoint1(prs):
    checkpoint_slide(prs, 1, "Z5_crystal_energy_alt", "CP6_1_Z5_D4", "Z5")


def try_slides(prs):
    for t in TRIES:
        try_slide(prs, t)


SLIDES = [s01_title, s01b_waterfall, s02_start, s03_crystal_section, s04_scope, try_slides, s98_t_tradeoff, s99_checkpoint1]


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
