"""Generator PDF izvještaja za dugoročne najave (docs/*.pdf).

Format prati postojeći dokument docs/14_V_MMXXVI.pdf: A4, zaglavlje sa
paginacijom, tijelo u serifnom pismu, numerisane tabele sa potpisom.
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

import matplotlib

FONT_DIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")

for name, filename in [
    ("Body", "DejaVuSerif.ttf"),
    ("Body-Bold", "DejaVuSerif-Bold.ttf"),
    ("Body-Italic", "DejaVuSerif-Italic.ttf"),
    ("Head", "DejaVuSans.ttf"),
    ("Head-Bold", "DejaVuSans-Bold.ttf"),
]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, filename)))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body-Italic")

INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5f5f5f")
RULE = colors.HexColor("#b9b9b9")
SHADE = colors.HexColor("#eeeae4")

STYLES = {
    "title": ParagraphStyle("title", fontName="Head-Bold", fontSize=17, leading=21,
                            textColor=INK, spaceAfter=4),
    "subtitle": ParagraphStyle("subtitle", fontName="Head", fontSize=11, leading=15,
                               textColor=MUTED, spaceAfter=10),
    "meta": ParagraphStyle("meta", fontName="Body", fontSize=8.4, leading=12.4,
                           textColor=MUTED, alignment=TA_JUSTIFY, spaceAfter=12),
    "h2": ParagraphStyle("h2", fontName="Head-Bold", fontSize=12.5, leading=16,
                         textColor=INK, spaceBefore=13, spaceAfter=5),
    "h3": ParagraphStyle("h3", fontName="Head-Bold", fontSize=10, leading=13,
                         textColor=INK, spaceBefore=9, spaceAfter=3),
    "p": ParagraphStyle("p", fontName="Body", fontSize=9.4, leading=13.6, textColor=INK,
                        alignment=TA_JUSTIFY, spaceAfter=6),
    "li": ParagraphStyle("li", fontName="Body", fontSize=9.4, leading=13.6, textColor=INK,
                         alignment=TA_JUSTIFY, spaceAfter=3, leftIndent=10, bulletIndent=1),
    "caption": ParagraphStyle("caption", fontName="Body-Italic", fontSize=7.8, leading=11,
                              textColor=MUTED, alignment=TA_JUSTIFY, spaceBefore=3,
                              spaceAfter=9),
    "cell": ParagraphStyle("cell", fontName="Head", fontSize=7.9, leading=10.4, textColor=INK),
    "cellhead": ParagraphStyle("cellhead", fontName="Head-Bold", fontSize=7.9, leading=10.4,
                               textColor=INK),
    "src": ParagraphStyle("src", fontName="Body", fontSize=8.2, leading=11.6, textColor=INK,
                          alignment=TA_JUSTIFY, spaceAfter=2, leftIndent=10, bulletIndent=1),
}


def H2(text):
    return ("h2", text)


def H3(text):
    return ("h3", text)


def P(text):
    return ("p", text)


def BULLETS(items):
    return ("bullets", items)


def TABLE(caption, header, rows, widths=None):
    return ("table", (caption, header, rows, widths))


def SOURCES(items):
    return ("sources", items)


class _Doc(BaseDocTemplate):
    def __init__(self, path, running_head):
        super().__init__(path, pagesize=A4, leftMargin=21 * mm, rightMargin=21 * mm,
                         topMargin=22 * mm, bottomMargin=18 * mm, title=running_head,
                         author="Matija Ivanović")
        self.running_head = running_head
        self.total_pages = 0
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates([PageTemplate(id="std", frames=[frame], onPage=self._decorate)])

    def _decorate(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Head", 7.4)
        canvas.setFillColor(MUTED)
        y = A4[1] - 15 * mm
        canvas.drawString(21 * mm, y, self.running_head)
        total = self.total_pages or "?"
        canvas.drawRightString(A4[0] - 21 * mm, y, "Strana %d od %s" % (doc.page, total))
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.4)
        canvas.line(21 * mm, y - 3, A4[0] - 21 * mm, y - 3)
        canvas.restoreState()


def _build_table(caption, header, rows, widths, avail):
    cells = [[Paragraph(c, STYLES["cellhead"]) for c in header]]
    cells += [[Paragraph(str(c), STYLES["cell"]) for c in row] for row in rows]
    if widths:
        total = float(sum(widths))
        col_widths = [avail * w / total for w in widths]
    else:
        col_widths = [avail / len(header)] * len(header)
    table = Table(cells, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SHADE),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return [table, Paragraph(caption, STYLES["caption"])]


def _story(title, subtitle, meta, blocks, avail):
    story = [
        Paragraph(title, STYLES["title"]),
        Paragraph(subtitle, STYLES["subtitle"]),
        Paragraph(meta, STYLES["meta"]),
    ]
    for kind, payload in blocks:
        if kind in ("h2", "h3", "p"):
            story.append(Paragraph(payload, STYLES[kind]))
        elif kind == "bullets":
            for item in payload:
                story.append(Paragraph(item, STYLES["li"], bulletText="—"))
            story.append(Spacer(1, 4))
        elif kind == "sources":
            for item in payload:
                story.append(Paragraph(item, STYLES["src"], bulletText="·"))
        elif kind == "table":
            caption, header, rows, widths = payload
            flow = _build_table(caption, header, rows, widths, avail)
            if len(rows) <= 6:
                story.append(KeepTogether(flow))
            else:
                story.extend(flow)
    return story


def build(path, running_head, title, subtitle, meta, blocks):
    """Gradi PDF u dva prolaza da bi „Strana X od N” imala tačan ukupan broj."""
    import io

    probe = _Doc(io.BytesIO(), running_head)
    probe.build(_story(title, subtitle, meta, blocks, probe.width))
    total = probe.page

    doc = _Doc(path, running_head)
    doc.total_pages = total
    doc.build(_story(title, subtitle, meta, blocks, doc.width))
    return path
