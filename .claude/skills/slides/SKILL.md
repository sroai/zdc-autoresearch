---
name: slides
description: >
  Build or update PowerPoint decks as rerunnable python-pptx scripts —
  progress decks, design/architecture decks, conference talks. Use whenever
  the deliverable is a deck someone will present: "slides", "deck",
  "presentation", "talk", or implicit asks like "put together something I can
  show Thursday" — even when python-pptx is never mentioned, because decks in
  these projects are generated code. Also use it
  to extend, review, QA, or polish an existing generated deck
  (build_*_slides.py, make_*_slides.py, slide_kit.py). Do NOT use for Google
  Slides, reveal.js/Markdown/HTML slides, standalone figures merely destined
  for a presentation, written reports, or reading/extracting content from a
  .pptx someone sent — the generic pptx skill handles those.
---

# Decks as python-pptx programs

A deck is a program; the `.pptx` is a build artifact: regenerated from
scratch on every run, numbers loaded from result files at build time, plots
referenced from the project's figures tree — so a rerun can never disagree
with the report it was built from. Never hand-edit the `.pptx`; edit the
script and rerun. Anyone must be able to run `python build_X_slides.py`
with no context and get the `.pptx` (and, when a converter exists, the
`.pdf`).

## Route by request

- **New deck** → follow the workflow top to bottom.
- **Extend / update an existing deck** → step 1 (find the script, match its
  helpers and palette exactly — decks in one project must look like one
  family), then steps 4—6. Do not port an old deck to this skill's kit; its
  own conventions win.
- **QA / polish an existing deck** → step 6 (visual QA), and step 7 if it
  will be presented. Fix in the script, never in the `.pptx`.

## Scale the discipline to the deck

Always, for any deck: the registry architecture, a palette from step 3, the
line-edit pass (step 4b), one render-and-look QA pass.

Scale with size and stakes:

- **Numbers from disk** — only when the project has a rerunnable pipeline
  producing result files; then `json.load` them at build time with a
  fallback string ("not re-run yet"). For invented or one-off content
  (a design deck, a tutorial), hardcode the literal with a `# source:`
  comment; label illustrative numbers as illustrative on the slide.
- **Speaker notes** — for decks that will be presented or handed over; skip
  for a quick internal 4-slider.
- **Version log + kept renders** — for decks that go through review rounds.
- **Judge loop (step 7)** — conference/seminar talks only; it is expensive.

## Workflow

### 1 — orient

Search the project for an existing deck script (`slides/build_*.py`,
`make_*_slides.py`, `slide_kit.py`). Found one → extend mode (see routing).
Nothing found (or no project at all) → copy the kit from the appendix and
pick a palette (step 3).

### 2 — architecture

One function per slide, collected in a registry, built by `main()`:

```python
def s01_title(prs): ...
def s02_overview(prs): ...

SLIDES = [s01_title, s02_overview]          # reorder/insert = one-line edit

def main():
    prs = new_deck()
    for build in SLIDES:
        build(prs)
    prs.save(OUT)
```

Module-level deck building (slides created at import time) makes every
helper un-importable; without a registry, reordering slides means
renumbering everything by hand.

### 3 — style

Canvas, all decks: **13.333 × 7.5 in (16:9)**, blank layout
(`prs.slide_layouts[6]`), coordinates in inches, 0.55 in margins,
body 13—15 pt, captions 10 pt.

Two house palettes exist — reuse one:

**A — single formal accent** (institutional; conservative audiences;
progress decks for collaborations). Calibri body, Consolas code 11—13 pt,
titles 28 pt. Includes the status pair mixed live/planned decks need
(step 4):

```python
ACCENT = RGBColor(0x2C, 0x5A, 0xA0)   # titles, rules, arrows
DARK   = RGBColor(0x22, 0x22, 0x22);  GRAY = RGBColor(0x66, 0x66, 0x66)
LIGHT  = RGBColor(0xEB, 0xF0, 0xF8)   # banding, panels
LIVE   = RGBColor(0x1B, 0x7F, 0x4B);  LIVE_FILL = RGBColor(0xE7, 0xF4, 0xEC)
PLAN   = RGBColor(0xB0, 0x64, 0x00);  PLAN_FILL = RGBColor(0xFD, 0xF2, 0xE2)
```

**B — multi-accent with semantic fills** (architecture/status decks; default
for new standalone projects). Calibri body, Courier New code, titles
30—31 pt (pass `font="Courier New"` to `code_block`; the kit default is
Consolas). Each card accent has a matching pale fill:

```python
INK    = RGBColor(0x22, 0x26, 0x33);  MUTED = RGBColor(0x60, 0x66, 0x76)
TEAL   = RGBColor(0x18, 0xB8, 0xA6);  TEAL_FILL   = RGBColor(0xD9, 0xF6, 0xF2)
PURPLE = RGBColor(0x7C, 0x4D, 0xD8);  PURPLE_FILL = RGBColor(0xEF, 0xE8, 0xFB)
BLUE   = RGBColor(0x2E, 0x6B, 0xE6)   # lines/labels only, no fill needed
ORANGE = RGBColor(0xEE, 0x85, 0x4A);  ORANGE_FILL = RGBColor(0xFD, 0xEC, 0xDF)
GREEN  = RGBColor(0x2F, 0x9E, 0x62);  GREEN_FILL  = RGBColor(0xDF, 0xF3, 0xE8)
```

Semantic color works — green = running/recommended, amber = planned/caveat —
but only with a small legend chip on the slide; unexplained emphasis reads
as noise.

(Lineage A lives in `~/dev/optim/ai-trk-bkg` and `ai-comb-lam`; B in
`~/dev/firebird/slide_kit.py` and `evio-optim` — when extending those decks
read their palette blocks directly; the autoresearch deck uses a diverged B
variant with a dark-slide family.)

### 4 — write the slides

Universal content rules (each earned in deck review):

- **The title states the slide's content, never a comment on it.** The
  failure mode: writing the slide's moral, metaphor, or verdict as its
  title ("a ruler the loop cannot bend", "instrument first, optimize
  last") — punchy prose that only decodes after reading the body, which
  is backwards: titles are read alone (scanning, outlines, memory).
  Write the concrete subject plus what the slide says about it
  ("PHASE 2 — benchmark and analysis framework"). Three tests, applied
  to every title: (a) with the body covered, the title alone tells what
  the slide contains; (b) the titles read in order reconstruct the
  talk's outline; (c) a title that could sit on three different slides
  fails. A slide about a named thing (a phase, a milestone, a tool)
  leads with the name, then what it is or does. Rhetorical punch goes
  in a takeaway line at the bottom of the slide — never in the title.
- **One idea per slide**; a slide needing three paragraphs is two slides or
  a speaker note.
- **Load-bearing numbers become stat callouts** (40—76 pt with a small
  label). Callouts in one row share one color.
- **Anchor every headline number to a baseline the audience owns** (their
  current tool, their farm, people they respect) rather than a benchmark
  name or a bare dollar figure.
- **Never screenshot matplotlib tables or multi-panel figures** —
  unreadable at slide scale. One plot per slide region at adequate size, or
  redraw the comparison as native shapes (proportional bars, a gauge).
- **Fit cards/panels to their content.** Fixed-height cards with a dead
  interior are the most common visual defect.
- **Balance the whole slide.** A top-heavy slide over an empty bottom third
  is the card defect at slide level — spread content through the
  title-to-footer band, or drop a slide.
- **Caveats go to speaker notes** unless they change how a number must be
  read.
- **Color-code mixed live/planned content** (status pair + legend) so the
  deck cannot oversell what exists. A legend is required when color encodes
  a claim the reader must decode (live vs planned); decorative accents
  need none.
- **URLs**: a visible monospace line with `run.hyperlink.address` set —
  bare blue text only works as a click.

Idioms worth reusing:

- **Running scoreboard** (long-running progress decks): one metrics table
  redrawn on many slides via `scoreboard(slide, upto=N)` — earned rows
  filled, future rows greyed em-dashes, the target row always visible. The
  audience can never be told two different numbers.
- **Plot resolver with a missing-list**: `plot(rel)` records absent files
  in `missing = []`; `main()` prints the list. The deck builds before every
  figure exists.
- **Fallback strings for in-flight results** (`"in training"`) so a rebuild
  mid-campaign stays truthful.

### 4b — line-edit pass (mandatory)

Draft first, then strip. Before any build or visual QA, run this pass over
every string in the deck — titles, bullets, captions, table cells, notes.
Slides amplify wordiness: a sentence that reads fine in prose is a wall of
text at 13 pt. The Zinsser rules, applied literally:

- **Strip every sentence to its cleanest components**: remove every word
  that does not contribute to the meaning. For each line ask what could be
  removed without significant loss — then remove it.
- **Eliminate clutter**: no redundancies ("completely finished" →
  "finished", "end-to-end proof that … are consistent" → "proves …
  consistent").
- **No qualifiers**: cut hedge words — very, little, pretty, rather,
  basically, actually. They weaken the prose.
- **No jargon**: simple, direct language a general reader understands
  without a dictionary (the audience's own domain terms are fine).


House rules on top of Zinsser (each from review of a real deck):

- **Never the rhetorical "X, not Y" construction** ("what makes it science,
  not vibes"; "the window must follow t0, not t = 0"). State X; the reader
  infers not-Y. "X, not Y" might be used in other contexts. 
- **No slang** ("vibes") and **no editorializing epithets** ("nominal",
  "finally", "honest caveat", "melting"). Decks go to collaborators; keep a
  neutral, factual register.
- **Em dash (—) for every dash in slide text**, ranges included — never a
  hyphen or en dash as punctuation.
- A slide that is only text is a candidate for a diagram, a plot, or
  deletion.
- **Titles and headings** A title is a label for the content under it, not a hook for the reader. 
  In the fewest words, state what the reader finds there. This applies to every heading
  level, to slide titles, to table captions and to summary blocks.

### 5 — build + PDF

Build: `uv run --with python-pptx python build_my_slides.py`
(no uv → `pip install python-pptx` in any venv; python-pptx ≥ 1.0 is fine).

PDF conversion is a **probe chain** (the appendix `convert_to_pdf`
implements it):

1. ONLYOFFICE `x2t` (`/opt/onlyoffice/desktopeditors/converter/x2t`) —
   needs its fonts dir with `AllFonts.js` to exist;
2. else `soffice`/`libreoffice` `--headless --convert-to pdf`;
3. else build the `.pptx` only, print that PDF conversion was unavailable,
   and continue — the build must never fail because a converter is missing.

Provide `--no-pdf` for fast iteration.

### 6 — visual QA (never skip)

A deck nobody looked at is not done. Static checks cannot see what matters:
textboxes clip (overflow lands on the element below), and table rows grow
when cells wrap.

1. `mkdir -p qa && pdftoppm -png -r 90 deck.pdf qa/s`
   (no pdftoppm → read the PDF pages with the Read tool; every page must
   get looked at).
2. **Read every page image.** Look for: collisions, overflow past edges,
   dead space in cards, unreadable embedded plots, orphaned labels, a
   legend whose colors don't match the boxes, silent font substitution.
3. Fix in the script, rebuild, re-render the affected pages.
4. Never claim the deck was inspected if no render could be produced — say
   so instead.

The `qa/` renders are disposable; keep them only for decks with a version
log (`render/v0…vN/`), and there record the defect each render caught.

### 7 — judge loop (presented talks only)

Cheap review iterations:

1. Render all slides to PNG; judges review the rendered images.
2. **Rotate the judge persona per loop**: design/typography → skeptical
   senior domain expert → practitioner → first-time listener → talk-flow /
   line editor. Different personas find disjoint defect classes.
3. Apply **exactly one drastic change per loop** (add/remove/rebuild one
   slide) plus a list of minors — more thrashes the deck.
4. Keep every version and its renders (`render/v0…vN/`); append each
   loop's verdicts, the drastic change, and declined judge picks (with the
   reason) to a `REVIEW_LOG.md` next to the script.
5. Finish with a number-consistency pass and a 4b line-edit pass — one real
   contradiction and a dozen wording drifts is the typical yield.

## python-pptx and rendering traps

- **Arrowheads need raw oxml** (no API):
  `ln = conn.line._get_or_add_ln();`
  `ln.append(ln.makeelement(qn('a:tailEnd'), {'type':'triangle','w':'med','len':'med'}))`
- Set `shape.shadow.inherit = False` on every shape — and still check the
  rendered PDF: some converters (x2t) draw faint shadows anyway.
- Tables: `first_row = False`, `horz_banding = False`, style cells manually
  — the default table style fights any palette. `row_h` is a minimum.
- `add_bullets` has no hanging indent: a wrapped sub-bullet line lands
  flush left. Keep sub-bullets short enough not to wrap, or accept it.
- Box-drawing characters (`┌─┬`) render as broken half-lines through
  x2t + Consolas — use plain ASCII (`+--`) for fake terminal output.
- Titles that would overflow the title box must shrink (~46 chars at 28 pt
  Calibri inside 0.55 in margins; scale as 46 × 28 / title-pt).
- Fonts substitute **silently** at conversion; verify text in the rendered
  PNGs.

## Deliverables checklist

- [ ] one rerunnable script; header comment says how to rebuild and where
      numbers/plots come from
- [ ] `.pptx` (+ `.pdf` when a converter exists) left next to the script
- [ ] pipeline numbers loaded from the project's result files where they
      exist; invented numbers labeled illustrative
- [ ] every title passes the nutshell tests (content, outline, uniqueness)
- [ ] slide text passed the 4b line-edit
- [ ] rendered pages visually inspected; defects fixed and re-rendered
- [ ] mixed live/planned content carries the status legend
- [ ] presented decks: speaker notes on content slides

## Appendix — the kit (self-contained, copy into new projects)

The canonical implementation, verified end-to-end (build → x2t PDF →
rendered pages inspected). For an existing deck family, its local helpers
win over this kit.

```python
"""slide_kit.py — shared python-pptx helpers. Palette/type constants are
defined by the deck script that imports this (see §Style)."""
import os, shutil, subprocess, sys, tempfile

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.parts.image import Image as PptxImage
from pptx.util import Inches, Pt, Emu

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.55)
CONTENT_W = Emu(int(SLIDE_W) - 2 * int(MARGIN))


def new_deck():
    prs = Presentation()
    prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H
    return prs


def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])   # blank


def txbox(slide, x, y, w, h):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return box, tf


def set_run(run, text, size, color, bold=False, italic=False, font="Calibri"):
    run.text = text
    f = run.font
    f.size, f.bold, f.italic, f.name = size, bold, italic, font
    f.color.rgb = color


def add_title(slide, text, accent, txt=None, size=Pt(28)):
    """Title + thin accent rule. `txt` is the title color (defaults to
    accent; lineage B uses ink text over a colored rule — pass INK). Long
    titles shrink instead of wrapping into the rule; the ~46-char threshold
    (28 pt Calibri) scales with the requested size."""
    box, tf = txbox(slide, 0.55, 0.28, 12.23, 0.75)
    limit = max(1, int(46 * 28 / size.pt))
    if len(text) > limit:
        size = Pt(max(20, int(size.pt * limit / len(text))))
    set_run(tf.paragraphs[0].add_run(), text, size, txt or accent, bold=True)
    rule = slide.shapes.add_shape(1, MARGIN, Inches(1.02), CONTENT_W, Pt(2.2))
    rule.fill.solid(); rule.fill.fore_color.rgb = accent
    rule.line.fill.background(); rule.shadow.inherit = False


def add_bullets(slide, items, x, y, w, h, color, size=Pt(14), space=Pt(6)):
    """items: str or (text, level) or (text, level, bold). Sub-bullets that
    wrap have no hanging indent — keep them short."""
    box, tf = txbox(slide, x, y, w, h)
    for i, item in enumerate(items):
        text, level, bold = (item, 0, False) if isinstance(item, str) else \
            (item[0], item[1], item[2] if len(item) > 2 else False)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = space
        set_run(p.add_run(), ("• " if level == 0 else "    – ") + text,
                size, color, bold=bold)
    return box


def add_table(slide, rows, x, y, w, header_fill, band_fill, dark,
              col_widths=None, size=Pt(13), row_h=Inches(0.38)):
    """rows[0] = header. col_widths: fractions summing to 1. Rows grow if a
    cell wraps — row_h is a minimum."""
    white = RGBColor(0xFF, 0xFF, 0xFF)
    gf = slide.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y),
                                Inches(w), Emu(int(row_h) * len(rows)))
    tbl = gf.table
    tbl.first_row = False; tbl.horz_banding = False   # style manually
    if col_widths:
        for j, frac in enumerate(col_widths):
            tbl.columns[j].width = Emu(int(Inches(w)) * frac // 1)
    for i, row in enumerate(rows):
        tbl.rows[i].height = row_h
        for j, val in enumerate(row):
            c = tbl.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.08)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid()
            c.fill.fore_color.rgb = (header_fill if i == 0 else
                                     band_fill if i % 2 == 0 else white)
            p = c.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            set_run(p.add_run(), str(val), size,
                    white if i == 0 else dark, bold=(i == 0))
    return gf


def add_picture_fit(slide, path, x, y, max_w, max_h, gray,
                    caption=True, missing=None):
    """Aspect-fit into (max_w, max_h) inches, centered; basename caption.
    Absent file -> recorded in `missing`, not a crash."""
    if not os.path.isfile(path):
        if missing is not None:
            missing.append(path)
        return None
    nw, nh = PptxImage.from_file(path).size
    w = Inches(max_w); h = Emu(int(int(w) * nh / nw))
    if int(h) > int(Inches(max_h)):
        h = Inches(max_h); w = Emu(int(int(h) * nw / nh))
    px = Inches(x) + Emu((int(Inches(max_w)) - int(w)) // 2)
    pic = slide.shapes.add_picture(path, px, Inches(y), width=w, height=h)
    if caption:
        box, tf = txbox(slide, x, y + h / 914400 + 0.05, max_w, 0.25)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        set_run(p.add_run(), os.path.basename(path), Pt(10), gray,
                italic=True, font="Consolas")
    return pic


def dia_box(slide, x, y, w, h, main, fill, line, txt, sub=None,
            main_size=Pt(13), sub_size=Pt(10.5)):
    """Rounded-rect node; `sub` may contain \\n for extra lines."""
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x),
                                Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.14
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = line; sh.line.width = Pt(1.25)
    sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), main, main_size, txt, bold=True)
    if sub:
        p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
        set_run(p2.add_run(), sub, sub_size, txt)
    return sh


def dia_arrow(slide, x1, y1, x2, y2, color):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1),
                                      Inches(y1), Inches(x2), Inches(y2))
    conn.line.color.rgb = color; conn.line.width = Pt(1.75)
    conn.shadow.inherit = False
    ln = conn.line._get_or_add_ln()          # arrowhead: oxml only
    ln.append(ln.makeelement(qn('a:tailEnd'),
              {'type': 'triangle', 'w': 'med', 'len': 'med'}))
    return conn


def code_block(slide, x, y, w, h, lines, fill, color, size=Pt(12),
               font="Consolas"):
    """Tinted monospace panel; lines may be str or (text, color).
    ASCII only for pseudo-terminal art — box-drawing glyphs break in x2t."""
    panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x),
                                   Inches(y), Inches(w), Inches(h))
    panel.adjustments[0] = 0.06
    panel.fill.solid(); panel.fill.fore_color.rgb = fill
    panel.line.fill.background(); panel.shadow.inherit = False
    box, tf = txbox(slide, x + 0.14, y + 0.10, w - 0.28, h - 0.20)
    for i, item in enumerate(lines):
        text, col = item if isinstance(item, tuple) else (item, color)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(3)
        set_run(p.add_run(), text, size, col, font=font)
    return panel


def stat_callout(slide, x, y, w, big, label, color, muted,
                 big_size=Pt(54), label_size=Pt(13)):
    """One huge number + small label — how load-bearing numbers are shown."""
    box, tf = txbox(slide, x, y, w, 1.5)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), big, big_size, color, bold=True)
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
    set_run(p2.add_run(), label, label_size, muted)


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def add_slide_number(prs, slide, gray):
    """Call right after creating the slide: len(prs.slides) IS its number,
    so inserting slides later keeps every number correct."""
    box, tf = txbox(slide, 12.43, 7.12, 0.6, 0.3)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
    set_run(p.add_run(), str(len(prs.slides)), Pt(11), gray)


# ---- PDF probe chain: x2t -> soffice -> continue without a PDF -----------
X2T = "/opt/onlyoffice/desktopeditors/converter/x2t"
X2T_FONTS = os.path.expanduser(
    "~/.local/share/onlyoffice/desktopeditors/data/fonts")


def convert_to_pdf(pptx_path, pdf_path):
    """x2t -> soffice -> give up gracefully. Returns True if pdf exists."""
    if os.path.exists(X2T) and os.path.exists(
            os.path.join(X2T_FONTS, "AllFonts.js")):
        with tempfile.TemporaryDirectory() as tmp:
            params = os.path.join(tmp, "conv.xml")
            with open(params, "w") as f:
                f.write(f"""<?xml version="1.0" encoding="utf-8"?>
<TaskQueueDataConvert xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <m_sFileFrom>{pptx_path}</m_sFileFrom>
  <m_sFileTo>{pdf_path}</m_sFileTo>
  <m_sTempDir>{tmp}</m_sTempDir>
  <m_nFormatTo>513</m_nFormatTo>
  <m_sFontDir>{X2T_FONTS}</m_sFontDir>
  <m_sAllFontsPath>{X2T_FONTS}/AllFonts.js</m_sAllFontsPath>
</TaskQueueDataConvert>
""")
            r = subprocess.run([X2T, params], capture_output=True, text=True)
            if r.returncode == 0 and os.path.exists(pdf_path):
                return True
            print(f"x2t failed: {r.stderr[-500:]}", file=sys.stderr)
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                        "--outdir", os.path.dirname(pdf_path) or ".",
                        pptx_path], capture_output=True)
        if os.path.exists(pdf_path):
            return True
    print("no PDF converter available — built .pptx only", file=sys.stderr)
    return False
```

Deck-script skeleton using the kit:

```python
#!/usr/bin/env python
"""Build <what>: reads <numbers source>, writes <name>.pptx (+ .pdf).
Rebuild: uv run --with python-pptx python build_my_slides.py [--no-pdf]"""
import argparse, os
from slide_kit import *          # or paste the kit above this line

ACCENT = RGBColor(0x2C, 0x5A, 0xA0)  # ... palette block from step 3
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "my_deck.pptx")
missing = []                      # add_picture_fit records absent plots here

def s01_title(prs):
    s = new_slide(prs)
    ...

SLIDES = [s01_title]

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
```
