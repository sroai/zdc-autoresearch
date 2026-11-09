#!/usr/bin/env python
"""Build phase5_msf.pptx (+ .pdf): Phase 5 of the ZDC autoresearch loop, Λ → nπ⁰ on MSF events (loop v5,
D-user-39), one slide per try (D-user-36).

Numbers load at build time; a missing file leaves "pending" in its place, so the deck always builds:
  space/perf/msf-regimes-<row>-<dataset>.json    N_found, N_window, yield, purity and the regime groups (210)
  space/perf/msf-select-<cand>-vs-<best>-D6s.json the paired selector of a try or a control (463)
  space/perf/fair-play-<row>-msf.json            F1–F3 on the MSF outputs (460)
The try texts (change, prediction) are the TRIES list below, written before each launch; the prediction is the
hypothesis line of the try's config and ledger entry.

Rebuild:  uv run --no-project --with python-pptx python slides/phase5/build_phase5_slides.py [--no-pdf]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from slide_kit import *  # noqa: E402,F401,F403

# ---- palette B, as slides/phase4/build_phase4_slides.py ---------------------------------------------------------
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
OUT = os.path.join(HERE, "phase5_msf.pptx")
PENDING = "pending"
REACH = {"9x275": 43.6, "9x130": 8.0}   # source: msf-regimes-MSF11_X9-D6c_*.json, groups n ZDC with both γ read
VERDICT_COLOR = {"ACCEPTED": (GREEN, GREEN_FILL), "INCONCLUSIVE": (ORANGE, ORANGE_FILL),
                 "REJECTED": (MUTED, GREY_FILL), "REJECTED (purity)": (ORANGE, ORANGE_FILL),
                 "FOUL": (ORANGE, ORANGE_FILL), PENDING: (MUTED, GREY_FILL)}


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
    {"id": "Y1", "row": "Y1_b0_split", "best": "MSF5_X9",
     "title": "Y1 — B0 ECal clusters split at local maxima",
     "change": ["B0 island clustering keeps one cluster per island today (splitCluster false)",
                "with both photons in B0 (4.0 % of expected at 9x275) the pair is merged for 93 % of the Λ",
                "split at every hit above 30 MeV that exceeds its 8 neighbours",
                "shared hits weighted by exp(−d / 1 crystal) × peak energy (stock: η-φ distance, scale 1)",
                "three parameters on the X9 install; no code change"],
     "prediction": "N_found on the search halves: 9x275 ≈ 920 → 960, 9x130 ≈ 65 → 95; purity flat or down < 1 point"},
    {"id": "Y2", "row": "Y2_vertex_lever_arm", "best": "MSF5_X9",
     "title": "Y2 — the Λ vertex with each daughter's lever arm",
     "change": ["the Λ line through the IP had slope Σ pᵢxᵢ / Σ pᵢzᵢ: right when n, γ, γ hit one depth",
                "a B0 photon (z ≈ 7 m) beside ZDC daughters (z ≈ 35 m) was weighted down by ~7/35",
                "now, for a vertex at depth z: s⊥ = Σ wᵢxᵢ⊥ / (P + z Σ wᵢ), wᵢ = pᵢ / (zᵢ − z), at every bisection step",
                "the depth search ends short of the nearest impact point (it ran on to the ZDC)",
                "33 lines in LambdaReconstruction.cc; all-ZDC events keep the stock result"],
     "prediction": "9x275 920 → ~990, 9x130 ~65 → ~80; all-ZDC unchanged within ±10; purity up slightly"},
    {"id": "Y4", "row": "Y4_b0_split_on_y2", "best": "Y2_vertex_lever_arm",
     "title": "Y4 — B0 splitting retried on top of Y2",
     "change": ["Y1 resolved both B0 photons for ~50 more Λ (9x275) and ~65 (9x130), but their mass failed",
                "Y2 made the γγ-in-B0 regime count: 0 → 5 found at 9x275, 1 → 15 at 9x130",
                "Y1's three B0 island parameters on the Y2 install"],
     "prediction": "γγ in B0 found 5 → ~20 and 15 → ~35; N_found 953 → ~968, 83 → ~103; purity flat"},
    {"id": "Y5", "row": "Y5_mixed_pairing", "best": "Y4_b0_split_on_y2",
     "title": "Y5 — the ZDC pairing with a photon in B0",
     "change": ["the ZDC pairing assumed both photons in the ZDC: with one photon in B0 it still wrote two ZDC photons",
                "now each tagged ZDC cluster with each B0 photon candidate is a hypothesis too (Y2's vertex)",
                "a winning mixed hypothesis writes one ZDC photon; the rest of the ZDC is the neutron",
                "LambdaReconstruction pairs that photon with the B0 photon",
                "switch lambdaPairingMixed, off by default; off reproduces Y4 exactly"],
     "prediction": "emulated mixed regime 195 → 383 (9x275), 32 → 55 (9x130); N_found 975 → ~1150, 123 → ~145; purity up"},
    {"id": "Y6", "row": "Y6_b0_profile", "best": "Y5_mixed_pairing",
     "title": "Y6 — sharper energy sharing between split B0 clusters",
     "change": ["with both photons in B0, Y5 still misses a photon for 198 of 264 Λ (9x275) and 151 of 264 (9x130)",
                "the photon's best B0 cluster is shared below purity 0.8 (~50 %) or merged with the other photon (~45 %)",
                "split hits are shared by exp(−d / s) × peak energy; s = 1.0 → 0.5 crystal",
                "one parameter on the Y5 install"],
     "prediction": "γγ-in-B0 found 33 → ~50 (9x275), 57 → ~80 (9x130); N_found 1164 → ~1180, 147 → ~170; purity flat"},
    {"id": "Y7", "row": "Y7_b0_photon_law", "best": "Y6_b0_profile",
     "title": "Y7 — the B0 photon energy law fitted on a B0 photon gun",
     "change": ["stock law 0.99·E^1.14 reads gun photons 11–48 % high at 5–40 GeV",
                "refit on D2b_photon_B0 (2–40 GeV, 7–20 mrad) with Y6's B0 clustering: 1.0888·E^1.0058",
                "every gun energy within 0.2 % of true; one parameter on Y6"],
     "prediction": "γγ in B0 up, γ B0 + γ ZDC down (the stock overestimate cancelled the ZDC photon's 0.78); net small, sign uncertain"},
    {"id": "Y8", "row": "Y8_b0_profile_03", "best": "Y7_b0_photon_law",
     "title": "Y8 — B0 split sharing narrowed again, 0.5 → 0.3 crystal",
     "change": ["Y6 (1.0 → 0.5 crystal) gained +80, z +8.1",
                "both photons in B0 is still the regime with the most B0 losses: 87 and 97 of 264 found",
                "one parameter on Y7"],
     "prediction": "N_found 1238 → ~1250, 190 → ~200; the gain may stop or turn (tail energy to the wrong maximum)"},
    {"id": "Y9", "row": "Y9_external_pair", "best": "Y8_b0_profile_03",
     "title": "Y9 — the ZDC pairing with both photons in B0",
     "change": ["with both photons in B0 another triplet wins for 46 (9x275) and 53 (9x130) of 264 Λ",
                "Y5's pairing still writes ZDC fragments as photons there and takes their energy from the neutron",
                "third hypothesis: every pair of B0 photon candidates, the whole ZDC as the neutron",
                "if it wins, no ZDC photon is written; switch lambdaPairingExternalPair, off reproduces Y8"],
     "prediction": "emulated net +21 / +28 in γγ-in-B0, −4 / −3 in γ B0 + γ ZDC; N_found 1252 → ~1268, 194 → ~219"},
    {"id": "Y10", "row": "Y10_lambda_mass_rank", "best": "Y9_external_pair",
     "title": "Y10 — the Λ-mass term of the final choice, 112 → 40 MeV",
     "change": ["LambdaReconstruction ranks triplets across ZDC, B0 and EEMC-P by π⁰ and Λ mass χ²",
                "its Λ term had the width 0.1 m_Λ = 112 MeV; now 40 MeV, as the ZDC pairing",
                "after Y5 and Y9 another triplet wins for only 22 Λ on both search halves"],
     "prediction": "N_found 1267 → ~1272, 219 → ~222; N_window up, purity down < 1 point"},
]


# ---- helpers (as the Phase 4 deck) -------------------------------------------------------------------------------
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
    set_run(tf.paragraphs[0].add_run(), "ZDC autoresearch, Phase 5: Λ → nπ⁰ on MSF events", Pt(34), INK, bold=True)
    box, tf = txbox(s, 0.8, 3.75, 11.7, 0.9)
    set_run(tf.paragraphs[0].add_run(), "Find more Λ → nπ⁰ in EICrecon on meson-structure events without a dirtier Λ sample",
            Pt(18), MUTED)
    box, tf = txbox(s, 0.8, 5.3, 11.7, 1.2)
    set_run(tf.paragraphs[0].add_run(), "Started 2026-11-08 · one slide per try · rebuilt from the run's result files",
            Pt(14), MUTED)


def s01b_waterfall(prs):
    """The score step by step: every try's paired result against the best of its time (463 files)."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Phase 5 tries — Λ found on the search halves, step by step")
    rows = [["try", "change", "9x275", "9x130", "score", "purity", "z", "verdict"]]
    for t in TRIES:
        sel = load_json(f"msf-select-{t['row']}-vs-{t['best']}-D6s.json")
        if not sel:
            rows.append([t["id"], t["title"].split("—", 1)[1].strip(), PENDING, PENDING, PENDING, PENDING, PENDING, PENDING])
            continue
        b = sel["beams"]
        rows.append([t["id"], t["title"].split("—", 1)[1].strip(),
                     f"{b['9x275']['best']['N_found']} → {b['9x275']['candidate']['N_found']}",
                     f"{b['9x130']['best']['N_found']} → {b['9x130']['candidate']['N_found']}",
                     f"{sel['N_found']['best']} → {sel['N_found']['candidate']}",
                     f"{100 * sel['purity']['best']:.1f} → {100 * sel['purity']['candidate']:.1f} %",
                     f"{sel['z']:+.1f}", sel["verdict"].replace("REJECTED", "REJECTED (no effect)") if sel["z"] == 0 else sel["verdict"]])
    add_table(s, rows, 0.55, 1.3, 12.23, PURPLE, PURPLE_FILL, INK, col_widths=[0.05, 0.37, 0.1, 0.09, 0.11, 0.12, 0.05, 0.11],
              size=Pt(11), row_h=Inches(0.42))
    first = load_json(f"msf-select-{TRIES[0]['row']}-vs-{TRIES[0]['best']}-D6s.json") or {}
    accepted = [t for t in TRIES if (load_json(f"msf-select-{t['row']}-vs-{t['best']}-D6s.json") or {}).get("verdict") == "ACCEPTED"]
    last = load_json(f"msf-select-{accepted[-1]['row']}-vs-{accepted[-1]['best']}-D6s.json") if accepted else None
    if first and last:
        a, c = first["N_found"]["best"], last["N_found"]["candidate"]
        takeaway(s, f"Score {a} → {c} (+{100 * (c - a) / a:.0f} %), purity {100 * first['purity']['best']:.1f} → "
                    f"{100 * last['purity']['candidate']:.1f} %; each row is paired against the best of its time.")


def s02_score(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Phase 5 score — yield and purity per beam energy")
    code_block(s, 0.55, 1.35, 6.4, 2.45, [
        "N_expected = 0.358 × generated Λ   (one Λ per event)",
        "N_found    = events whose true Λ → n pi0 is rebuilt:",
        "             candidate within ±30 MeV of m_Λ, and",
        "             n, γ, γ clusters ≥ 80 % from the true",
        "             neutron and the two true photons",
        "N_window   = events with any candidate in the window",
        "",
        "yield  = N_found / N_expected",
        "purity = N_found / N_window"], GREY_FILL, INK, size=Pt(12.5), font="Courier New")
    hdr = ["X9 on D6c (40 000 events per beam)", "9x275", "9x130"]
    r275, r130 = rows_of("MSF11_X9", "D6c_9x275"), rows_of("MSF11_X9", "D6c_9x130")
    def cell(r, key, err):
        return PENDING if not r else f"{100 * r[key]:.2f} ± {100 * r[err]:.2f} %"
    rows = [hdr,
            ["N_found / N_expected", f"{r275['N_found']} / {r275['N_expected']:.0f}" if r275 else PENDING,
             f"{r130['N_found']} / {r130['N_expected']:.0f}" if r130 else PENDING],
            ["yield", cell(r275, "yield", "yield_err"), cell(r130, "yield", "yield_err")],
            ["reachable (n in ZDC, both γ read)", f"{REACH['9x275']} %", f"{REACH['9x130']} %"],
            ["N_found / N_window", f"{r275['N_found']} / {r275['N_window']}" if r275 else PENDING,
             f"{r130['N_found']} / {r130['N_window']}" if r130 else PENDING],
            ["purity", cell(r275, "purity", "purity_err"), cell(r130, "purity", "purity_err")]]
    add_table(s, rows, 7.2, 1.35, 5.58, TEAL, TEAL_FILL, INK, col_widths=[0.46, 0.27, 0.27], size=Pt(12))
    card(s, 0.55, 4.1, 12.23, 2.0, "Selector (463): keep a change when", [
        "the score N_found(9x275) + N_found(9x130) on the search halves D6s rises: on identical Λ, b found only by the "
        "current best, c only by the change, z = (c − b) / √(b + c) ≥ 3",
        "and the pooled purity does not fall by more than 2σ: z_P = (P_new − P_best) / √(σ_new² + σ_best²) ≥ −2",
        "D6h (files 41–80) is held out: every 5 tries the current best must reproduce its gain there at > 2σ",
        "fair play F1–F3 of Phase 4 (460) on the MSF outputs; a FAIL voids the try"], PURPLE, PURPLE_FILL, size=Pt(12.5))
    takeaway(s, "Yield is pushed up; purity is a floor. A change that only cleans the sample is reported, not kept.")


def s03_regimes(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Where Λ → nπ⁰ land and what X9 finds in each regime")
    hdr = ["regime (share of N_expected; X9 found in it)", "9x275", "9x130"]
    rows = [hdr]
    d275, d130 = load_json("msf-regimes-MSF11_X9-D6c_9x275.json"), load_json("msf-regimes-MSF11_X9-D6c_9x130.json")
    if d275 and d130:
        for g1, g2 in zip(d275["groups"], d130["groups"]):
            def c(g):
                x = g["MSF11_X9"]
                eff = f"{100 * x['eff_in_group']:.1f} %" if x["eff_in_group"] is not None else "—"
                return f"{100 * g['share_of_expected_npi0']:.1f} %; {x['matched']} found ({eff})"
            rows.append([g1["group"], c(g1), c(g2)])
        lb1, lb2 = d275["lambda_lost_before_decay_share_of_all"], d130["lambda_lost_before_decay_share_of_all"]
        rows.append(["Λ interacts in material / does not decay", f"{100 * lb1['material_interaction']:.1f} % / "
                     f"{100 * lb1['undecayed']:.1f} %", f"{100 * lb2['material_interaction']:.1f} % / {100 * lb2['undecayed']:.1f} %"])
    add_table(s, rows, 0.55, 1.35, 12.23, TEAL, TEAL_FILL, INK, col_widths=[0.42, 0.29, 0.29], size=Pt(12), row_h=Inches(0.4))
    takeaway(s, "At 9x275 the software can still win in the first four rows; at 9x130 the neutron misses the ZDC for 53 %.")


def try_slide(prs, t):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, t["title"], PURPLE)
    sel = load_json(f"msf-select-{t['row']}-vs-{t['best']}-D6s.json") or {}
    fp = (load_json(f"fair-play-{t['row']}-msf.json") or {}).get("verdict", PENDING)
    verdict = "FOUL" if fp == "FAIL" else sel.get("verdict", PENDING)
    ch = 0.6 + 0.29 * len(t["change"]) + 0.21 * sum(len(c) > 95 for c in t["change"])
    card(s, 0.55, 1.3, 7.3, ch, "Change", t["change"], PURPLE, PURPLE_FILL, size=Pt(12))
    ph = 0.85 + 0.21 * (len(t["prediction"]) > 95)
    card(s, 0.55, 1.3 + ch + 0.2, 7.3, ph, "Prediction (written before launch)", [t["prediction"]], BLUE, GREY_FILL, size=Pt(12))
    hdr = ["search half", "best", "this try"]
    rows = [hdr]
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
    add_notes(s, f"Row {t['row']} against {t['best']}; selector space/perf/msf-select-{t['row']}-vs-{t['best']}-D6s.json (463); "
                 f"fair play space/perf/fair-play-{t['row']}-msf.json (460).")


def y5_flow(prs):
    """Diagram of Y5: the ZDC pairing's hypotheses with a B0 photon."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Y5 and Y9 — photon hypotheses in the ZDC pairing", PURPLE)
    # inputs
    dia_box(s, 0.55, 1.5, 2.6, 1.0, "ZDC Hcal clusters", GREY_FILL, GREY_BAR, INK, "tagged by depth, length, width")
    dia_box(s, 0.55, 3.1, 2.6, 1.0, "B0 ECal clusters", GREY_FILL, GREY_BAR, INK, "≤ 4 leading, ≥ 1 GeV")
    # hypotheses
    dia_box(s, 3.9, 1.3, 3.6, 1.2, "ZDC pair (X2–X9)", GREY_FILL, GREY_BAR, INK,
            "γ, γ = two tagged ZDC clusters\nn = every other ZDC cluster")
    dia_box(s, 3.9, 2.75, 3.6, 1.2, "ZDC + B0 (Y5)", PURPLE_FILL, PURPLE, INK,
            "γ = one tagged ZDC cluster, γ = a B0 photon\nn = every other ZDC cluster\nvertex with each lever arm (Y2)")
    dia_box(s, 3.9, 4.1, 3.6, 0.95, "B0 + B0 (Y9)", PURPLE_FILL, PURPLE, INK, "γ, γ = two B0 photons; n = the whole ZDC")
    dia_arrow(s, 3.15, 3.6, 3.9, 4.55, MUTED); dia_arrow(s, 7.5, 4.55, 8.2, 3.0, MUTED)
    dia_arrow(s, 3.15, 2.0, 3.9, 1.9, MUTED)     # ZDC clusters -> ZDC pair
    dia_arrow(s, 3.15, 2.0, 3.9, 3.5, MUTED)     # ZDC clusters -> ZDC + B0
    dia_arrow(s, 3.15, 3.6, 3.9, 3.7, MUTED)     # B0 clusters -> ZDC + B0
    dia_box(s, 8.2, 2.1, 2.1, 1.2, "lowest score", GREY_FILL, GREY_BAR, INK, "π⁰ and Λ masses,\ndecay depth, photon depth")
    dia_arrow(s, 7.5, 1.9, 8.2, 2.6, MUTED); dia_arrow(s, 7.5, 3.6, 8.2, 2.8, MUTED)
    dia_box(s, 10.75, 2.1, 2.03, 1.2, "Λ reconstruction", GREY_FILL, GREY_BAR, INK, "ZDC and B0 photons,\none candidate per event")
    dia_arrow(s, 10.3, 2.7, 10.75, 2.7, MUTED)
    card(s, 0.55, 5.25, 12.23, 1.35, "Why", [
        "with one photon in B0 the old pairing still wrote two ZDC photons: the true one with a neutron fragment, or two fragments",
        "their energy left the neutron, and the true triplet could not form: another triplet chosen (186) or the ZDC photon missing (144) of 803",
        "emulation: Y5 383 instead of 195 in γ B0 + γ ZDC (474); Y9 +49 net with both photons in B0 (475)"],
        PURPLE, PURPLE_FILL, size=Pt(12))
    add_notes(s, "Y5 patch space/notes/patches/Y5_mixed_pairing.patch; emulation scripts/473 and 474; switch lambdaPairingMixed.")


def try_slides(prs):
    for t in TRIES:
        try_slide(prs, t)
        if t["id"] == "Y5":
            y5_flow(prs)


def headline_row(row):
    import csv
    try:
        with open(os.path.join(PERF, "headline.csv")) as fh:
            return next((r for r in csv.DictReader(fh) if r["row"] == row), None)
    except OSError:
        return None


def checkpoint_slide(prs, n, prev, best, d4row, prev_label, best_label, takeaway_text):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, f"Checkpoint {n} — held-out MSF files and the D4 gun, {prev_label} → {best_label}")
    h = load_json(f"msf-select-{best}-vs-{prev}-D6h.json") or {}
    hdr = ["N_found (yield)", f"{prev_label}, search", f"{best_label}, search", f"{prev_label}, held out", f"{best_label}, held out", "reachable"]
    rows = [hdr]
    for beam, reach in (("9x275", 43.6), ("9x130", 8.0)):
        x = (h.get("beams") or {}).get(beam)
        ra, rc = rows_of(prev, f"D6s_{beam}"), rows_of(best, f"D6s_{beam}")
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
    hx, hy = headline_row("X9_pairing_photon_depth"), headline_row(d4row)
    f = lambda r, c: (f"{float(r[c]):.2f} %" if r and r.get(c) not in (None, "", "nan") else PENDING)
    card(s, 0.55, 4.3, 12.23, 1.3, "D4 Λ gun, S4a_tm per thrown Λ → nπ⁰ (reported, never selected on)", [
        f"X9 (end of Phase 4): {f(hx, 'S4a_tm_per_thrown_mean')} mean, {f(hx, 'S4a_tm_per_thrown_275')} at 275 GeV;  "
        f"{best_label}: {f(hy, 'S4a_tm_per_thrown_mean')} mean, {f(hy, 'S4a_tm_per_thrown_275')} at 275 GeV (ceilings 14.1 % / 27.8 %)"],
        BLUE, GREY_FILL, size=Pt(12.5))
    takeaway(s, takeaway_text)


def s99_checkpoint1(prs):
    checkpoint_slide(prs, 1, "MSF5_X9", "Y6_b0_profile", "CP5_1_Y6_D4", "X9", "Y6",
                     "The search halves gained 38 %, the held-out halves 37 %: the accepted steps are no overfit.")


def s99_checkpoint2(prs):
    checkpoint_slide(prs, 2, "Y6_b0_profile", "Y9_external_pair", "CP5_2_Y9_D4", "Y6", "Y9",
                     "Y7–Y9 measured again on files nothing was tuned on.")


D4_ROW = {"Y1": "D4P5_Y1", "Y2": "D4P5_Y2", "Y4": "D4P5_Y4", "Y5": "D4P5_Y5", "Y6": "CP5_1_Y6_D4", "Y7": "D4P5_Y7",
          "Y8": "D4P5_Y8", "Y9": "CP5_2_Y9_D4", "Y10": "D4P5_Y10"}
PLOTS = os.path.join(HERE, "plots")
missing = []


def d4(row, col):
    r = headline_row(row)
    v = (r or {}).get(col)
    return PENDING if v in (None, "", "nan") else f"{float(v):.3f} %"


def s01c_phase4_columns(prs):
    """Every Phase 5 try in Phase 4's columns (S4a_tm per thrown on D4), beside its MSF score."""
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Phase 5 tries in Phase 4's columns — S4a_tm per thrown Λ → nπ⁰ on the D4 gun")
    rows = [["S4a_tm per thrown Λ → nπ⁰", "mean 100–275 GeV", "at 275 GeV", "MSF found, 9x275 / 9x130", "verdict"]]
    rows.append(["R1 (PR 3064), start of Phase 4", d4("R1_pr3064", "S4a_tm_per_thrown_mean"), d4("R1_pr3064", "S4a_tm_per_thrown_275"), "—", ""])
    x9 = (rows_of("MSF5_X9", "D6s_9x275") or {}).get("N_found"), (rows_of("MSF5_X9", "D6s_9x130") or {}).get("N_found")
    rows.append(["X9, end of Phase 4 = start of Phase 5", d4("X9_pairing_photon_depth", "S4a_tm_per_thrown_mean"),
                 d4("X9_pairing_photon_depth", "S4a_tm_per_thrown_275"), f"{x9[0]} / {x9[1]}", ""])
    for t in TRIES:
        sel = load_json(f"msf-select-{t['row']}-vs-{t['best']}-D6s.json") or {}
        b = sel.get("beams") or {}
        msf = f"{b['9x275']['candidate']['N_found']} / {b['9x130']['candidate']['N_found']}" if b else PENDING
        verdict = sel.get("verdict", PENDING)
        verdict = "REJECTED (no effect)" if verdict == "REJECTED" and sel.get("z") == 0 else verdict
        rows.append([f"{t['id']}: {t['title'].split('—', 1)[1].strip()}", d4(D4_ROW[t["id"]], "S4a_tm_per_thrown_mean"),
                     d4(D4_ROW[t["id"]], "S4a_tm_per_thrown_275"), msf, verdict])
    rows.append(["ceiling (perfect separation, P1b resolution)", f"{14.1} %", f"{27.8} %", "reachable 43.6 % / 8.0 % of expected", ""])
    add_table(s, rows, 0.55, 1.25, 12.23, TEAL, GREY_FILL, INK, col_widths=[0.42, 0.13, 0.11, 0.2, 0.14], size=Pt(10.5),
              row_h=Inches(0.36))
    add_notes(s, "D4 columns from headline.csv (441): CP5_1_Y6_D4, CP5_2_Y9_D4 at the checkpoints, D4P5_<try> for the other "
                 "tries (Phase 4's slim template, reconstructed at the Phase 5 close). MSF columns: the try's N_found on the search "
                 "halves (463). Phase 5 selected on MSF; D4 was reported, never selected on.")


def plot_slide(prs, ttl, png, caption_text, takeaway_text):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, ttl)
    add_picture_fit(s, os.path.join(PLOTS, png), 0.55, 1.3, 12.23, 4.6, MUTED, caption=False, missing=missing)
    box, tf = txbox(s, 0.55, 6.0, 12.23, 0.5)
    set_run(tf.paragraphs[0].add_run(), caption_text, Pt(11), MUTED, italic=True)
    takeaway(s, takeaway_text, y=6.6)


def s200_msf_steps(prs):
    plot_slide(prs, "Phase 4 and Phase 5 on the MSF score — yield step by step", "p5_msf_progression.png",
               "Λ → nπ⁰ found per expected on the MSF search halves (210). R0 the pin; X1, X9 Phase 4 rows (tuned on the D4 gun); "
               "Y2–Y9 the accepted Phase 5 tries (tuned on MSF). R0 was not run at 9x130.",
               "Phase 4 took MSF 9x275 from 0.04 % to 13.2 % without seeing MSF; Phase 5 added 4.5 points there and tripled 9x130.")


def s201_d4_steps(prs):
    plot_slide(prs, "Phase 4 and Phase 5 on the D4 gun score — S4a_tm step by step", "p5_d4_progression.png",
               "S4a_tm per thrown Λ → nπ⁰ on the D4 Λ gun (headline.csv): Phase 4 tries R1 → X9, then every accepted Phase 5 try "
               "(D4P5_*, CP5_1_Y6_D4, CP5_2_Y9_D4).",
               "Phase 5 leaves the gun where Phase 4 left it: its gains are in B0 regimes the gun barely reaches.")


def s202_regimes(prs):
    plot_slide(prs, "Phase 5's gain by regime — X9 and Y9 on MSF", "p5_regimes.png",
               "Found per expected Λ → nπ⁰ in each regime (210 groups, search halves); grey: the regime's share of expected, "
               "the most any reconstruction could find there.",
               "All-ZDC unchanged; one photon in B0 doubled; both photons in B0 from zero to 1.7 % (9x275) and 1.8 % (9x130).")


def s203_mass(prs):
    plot_slide(prs, "Λ mass on MSF 9x275 — every candidate and the truth-matched ones, X9 and Y9", "p5_mass.png",
               "ReconstructedLambdas mass, at most one candidate per event (F3a), MSF 9x275 search half; shaded: the ±30 MeV "
               "scoring window; blue: candidates 210 truth-matches to the true n, γ, γ.",
               "The wrong candidates peak at m_Λ too (both pairings rank by Λ mass): purity needs other variables — a phase of its own.")


def s204_compare(prs):
    s = new_slide(prs); add_slide_number(prs, s, MUTED)
    title(s, "Phase 4 and Phase 5 side by side")
    def y(row, beam, half="s"):
        if half == "h":
            sel = load_json(f"msf-select-Y9_external_pair-vs-MSF5_X9-D6h.json") or {}
            x = (sel.get("beams") or {}).get(beam)
            return None if not x else (100 * x["best"]["yield"], 100 * x["candidate"]["yield"])
        r = rows_of(row, f"D6s_{beam}")
        return None if not r else 100 * r["yield"]
    def f(v, d=1):
        return PENDING if v is None else f"{v:.{d}f} %"
    r0, x1, x9, y9 = (y(r, "9x275") for r in ("CTL5_R0_msf", "CTL5_X1_msf", "MSF5_X9", "Y9_external_pair"))
    x9b, y9b = y("MSF5_X9", "9x130"), y("Y9_external_pair", "9x130")
    h275, h130 = y(None, "9x275", "h"), y(None, "9x130", "h")
    p_x9 = [(rows_of("MSF5_X9", f"D6s_{b}") or {}).get("purity") for b in ("9x275", "9x130")]
    p_y9 = [(rows_of("Y9_external_pair", f"D6s_{b}") or {}).get("purity") for b in ("9x275", "9x130")]
    pp = lambda v: PENDING if None in v else f"{100 * v[0]:.0f} % / {100 * v[1]:.0f} %"
    rows = [["", "Phase 4 — the Λ bar fight", "Phase 5 — Λ → nπ⁰ on MSF events"],
            ["data it tuned on", "D4 Λ gun (8 momenta × 2000)", "MSF 2026-11 search halves (2 × 20 000 events)"],
            ["score", "S4a_tm per thrown Λ → nπ⁰ (D4)", "N_found on MSF, purity as a floor"],
            ["held out", "D4h (fresh seeds)", "D6h (MSF files 41–80)"],
            ["tries", "9: 8 accepted, 1 rejected", "9: 7 accepted, 1 inconclusive, 1 rejected"],
            ["D4 S4a_tm, mean / 275 GeV",
             f"{d4('R1_pr3064', 'S4a_tm_per_thrown_mean')} / {d4('R1_pr3064', 'S4a_tm_per_thrown_275')} → "
             f"{d4('X9_pairing_photon_depth', 'S4a_tm_per_thrown_mean')} / {d4('X9_pairing_photon_depth', 'S4a_tm_per_thrown_275')}",
             f"X9 → Y9: {d4('CP5_2_Y9_D4', 'S4a_tm_per_thrown_mean')} / {d4('CP5_2_Y9_D4', 'S4a_tm_per_thrown_275')} (reported, not selected on)"],
            ["MSF 9x275 found / expected (search)", f"R0 {f(r0, 2)} → X1 {f(x1)} → X9 {f(x9)}",
             f"X9 {f(x9)} → Y9 {f(y9)} (held out {f(h275[0]) if h275 else PENDING} → {f(h275[1]) if h275 else PENDING})"],
            ["MSF 9x130 found / expected (search)", f"X9 {f(x9b, 2)}",
             f"X9 {f(x9b, 2)} → Y9 {f(y9b, 2)} (held out {f(h130[0], 2) if h130 else PENDING} → {f(h130[1], 2) if h130 else PENDING})"],
            ["purity in the window, 9x275 / 9x130", f"X9 {pp(p_x9)}", f"Y9 {pp(p_y9)}"],
            ["what changed", "ZDC clustering, photon tag, Λ pairing", "vertex lever arm, pairing with B0 photons, B0 splitting and law"]]
    add_table(s, rows, 0.55, 1.25, 12.23, TEAL, GREY_FILL, INK, col_widths=[0.26, 0.34, 0.4], size=Pt(11.5), row_h=Inches(0.42))
    card(s, 0.55, 5.85, 12.23, 0.75, "Next: Phase 6, the crystal-seeded ZDC photon finder (prepared, loop v6)", [
        "the all-ZDC regime loses a photon for 1125 of 2003 Λ (9x275 half); a scope study decides first (stop below +50 emulated)"],
        PURPLE, PURPLE_FILL, size=Pt(11.5))


SLIDES = [s01_title, s01b_waterfall, s01c_phase4_columns, s02_score, s03_regimes, try_slides, s99_checkpoint1,
          s99_checkpoint2, s200_msf_steps, s201_d4_steps, s202_regimes, s203_mass, s204_compare]


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
