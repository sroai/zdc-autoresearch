"""slide_kit.py — shared python-pptx helpers (the slides skill's kit, verbatim).
Palette/type constants are defined by the deck script that imports this."""
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
    """Title + thin accent rule. Long titles shrink instead of wrapping into the rule."""
    box, tf = txbox(slide, 0.55, 0.28, 12.23, 0.75)
    limit = max(1, int(46 * 28 / size.pt))
    if len(text) > limit:
        size = Pt(max(20, int(size.pt * limit / len(text))))
    set_run(tf.paragraphs[0].add_run(), text, size, txt or accent, bold=True)
    rule = slide.shapes.add_shape(1, MARGIN, Inches(1.02), CONTENT_W, Pt(2.2))
    rule.fill.solid(); rule.fill.fore_color.rgb = accent
    rule.line.fill.background(); rule.shadow.inherit = False


def add_bullets(slide, items, x, y, w, h, color, size=Pt(14), space=Pt(6)):
    """items: str or (text, level) or (text, level, bold)."""
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
    """rows[0] = header. col_widths: fractions summing to 1. row_h is a minimum."""
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
    """Aspect-fit into (max_w, max_h) inches, centered; basename caption."""
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
    """Tinted monospace panel; lines may be str or (text, color)."""
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
    """One huge number + small label."""
    box, tf = txbox(slide, x, y, w, 1.5)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    set_run(p.add_run(), big, big_size, color, bold=True)
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
    set_run(p2.add_run(), label, label_size, muted)


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def add_slide_number(prs, slide, gray):
    """Call right after creating the slide: len(prs.slides) IS its number."""
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


def hbars(slide, rows, x, y, scale_w, row_h, vmax, ink, muted, label_w=2.2, size=Pt(12), text_w=4.6, mark=None):
    """Horizontal bars, one row each: rows = [(label, value or None, color, text)]. A bar of length scale_w × value / vmax
    starts at x + label_w; its text sits right after it (pass the text width the longest label needs). mark = (value,
    label) draws a thin vertical rule at that value through every row, its label above the first row (a ceiling, a
    reachable yield). A None value prints the text where the bar would start."""
    x0 = x + label_w
    for i, (label, v, color, text) in enumerate(rows):
        yy = y + i * row_h
        box, tf = txbox(slide, x, yy + 0.06, label_w - 0.1, row_h)
        set_run(tf.paragraphs[0].add_run(), label, size, ink)
        end = x0
        if v is not None:
            bw = max(0.02, scale_w * v / vmax)
            sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x0), Inches(yy + 0.06), Inches(bw),
                                        Inches(row_h - 0.16))
            sh.fill.solid(); sh.fill.fore_color.rgb = color; sh.line.fill.background(); sh.shadow.inherit = False
            end = x0 + bw
        box, tf = txbox(slide, end + 0.1, yy + 0.06, text_w, row_h)
        set_run(tf.paragraphs[0].add_run(), text, size, muted)
    if mark:
        mx = x0 + scale_w * mark[0] / vmax
        rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(mx - 0.01), Inches(y - 0.05), Inches(0.02),
                                      Inches(len(rows) * row_h))
        rule.fill.solid(); rule.fill.fore_color.rgb = muted; rule.line.fill.background(); rule.shadow.inherit = False
        box, tf = txbox(slide, mx - 2.6, y - 0.38, 2.55, 0.3)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
        set_run(p.add_run(), mark[1], Pt(11), muted, italic=True)
