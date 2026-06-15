import io
import os
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, PageBreak, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Korean font candidates (Windows → macOS → Linux)
_FONT_CANDIDATES = [
    "C:/Windows/Fonts/malgun.ttf",
    "C:/Windows/Fonts/gulim.ttc",
    "/Library/Fonts/AppleGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
]

_FONT: str | None = None


def _init_font() -> str:
    global _FONT
    if _FONT:
        return _FONT
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("KFont", path))
                _FONT = "KFont"
                return _FONT
            except Exception:
                continue
    _FONT = "Helvetica"
    return _FONT


def _ps(name: str, size=11, leading=17, align=TA_LEFT,
        sb=0, sa=4, indent=0) -> ParagraphStyle:
    font = _init_font()
    return ParagraphStyle(
        name, fontName=font, fontSize=size, leading=leading,
        alignment=align, spaceBefore=sb, spaceAfter=sa, leftIndent=indent,
    )


def build_pdf(pages: list[dict]) -> bytes:
    """
    Build a clean exam PDF from a list of page dicts returned by extractor.extract_page().
    Each dict becomes one page in the output PDF.
    """
    _init_font()

    S_TITLE   = _ps("title",   18, 24, TA_CENTER, sb=2, sa=3)
    S_SUBJECT = _ps("subject", 13, 18, TA_CENTER, sa=2)
    S_INFO    = _ps("info",    10, 14, TA_CENTER,  sa=8)
    S_INSTR   = _ps("instr",   10, 15, sa=8)
    S_QBODY   = _ps("qbody",   11, 17, sb=10, sa=3)
    S_SUBCONT = _ps("subcont", 10, 15, sa=3, indent=10)
    S_OPTION  = _ps("option",  10, 15, sa=2,  indent=14)
    S_PASSAGE = _ps("passage", 10, 15, sa=5,  indent=8)
    S_SECTION = _ps("section", 11, 16, sb=8,  sa=4)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=22 * mm, rightMargin=22 * mm,
        topMargin=20 * mm, bottomMargin=22 * mm,
    )

    story = []

    for pi, page in enumerate(pages):
        if pi > 0:
            story.append(PageBreak())

        hdr = page.get("header") or {}
        if hdr.get("title"):
            story.append(Paragraph(escape(hdr["title"]), S_TITLE))
        if hdr.get("subject"):
            story.append(Paragraph(escape(hdr["subject"]), S_SUBJECT))
        if hdr.get("info_line"):
            story.append(Paragraph(escape(hdr["info_line"]), S_INFO))

        story.append(HRFlowable(
            width="100%", thickness=1.2, color="black", spaceAfter=6,
        ))

        if page.get("instructions"):
            story.append(Paragraph(
                "※ " + escape(page["instructions"]), S_INSTR,
            ))

        for item in page.get("items") or []:
            t = item.get("type", "question")

            if t == "section_header":
                story.append(Paragraph(
                    f"<b>{escape(item.get('content', ''))}</b>", S_SECTION,
                ))

            elif t == "passage":
                label = item.get("label") or ""
                content = item.get("content") or ""
                label_part = f"<b>{escape(label)}</b>  " if label else ""
                story.append(Paragraph(label_part + escape(content), S_PASSAGE))

            elif t == "question":
                num = item.get("number", "")
                pts = item.get("points")
                pts_tag = (
                    f"  <font size='9'>[{pts}점]</font>" if pts else ""
                )
                body = escape(item.get("content") or "")
                block = [Paragraph(f"<b>{num}.</b>{pts_tag}  {body}", S_QBODY)]

                if item.get("sub_content"):
                    block.append(Paragraph(
                        escape(item["sub_content"]), S_SUBCONT,
                    ))

                for opt in item.get("options") or []:
                    block.append(Paragraph(escape(opt), S_OPTION))

                for _ in range(item.get("answer_lines") or 0):
                    block.append(Spacer(1, 7 * mm))
                    block.append(HRFlowable(
                        width="88%", thickness=0.5, color="#aaaaaa",
                    ))

                story.append(KeepTogether(block))

    doc.build(story)
    return buf.getvalue()
