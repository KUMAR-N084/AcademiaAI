from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import io
import re


def generate_pdf(question, answer, username="User"):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"],
        fontSize=20, textColor=colors.HexColor("#4f46e5"),
        spaceAfter=10, alignment=1
    )
    q_style = ParagraphStyle(
        "Q", parent=styles["Heading2"],
        fontSize=14, textColor=colors.HexColor("#1f2937"),
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["BodyText"],
        fontSize=11, leading=16, textColor=colors.HexColor("#111827")
    )
    meta_style = ParagraphStyle(
        "Meta", parent=styles["Normal"],
        fontSize=9, textColor=colors.grey, alignment=1
    )

    story = [
        Paragraph("AcademiaAI — Answer Report", title_style),
        Paragraph(
            f"Generated for {username} on {datetime.now().strftime('%B %d, %Y %H:%M')}",
            meta_style
        ),
        Spacer(1, 16),
        Paragraph("Question:", q_style),
        Paragraph(_escape(question), body_style),
        Spacer(1, 14),
        Paragraph("Answer:", q_style)
    ]

    # Convert markdown-ish content to paragraphs
    for line in answer.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue
        if line.startswith("### "):
            story.append(Paragraph(f"<b>{_escape(line[4:])}</b>", q_style))
        elif line.startswith("## "):
            story.append(Paragraph(f"<b>{_escape(line[3:])}</b>", q_style))
        elif line.startswith("# "):
            story.append(Paragraph(f"<b>{_escape(line[2:])}</b>", q_style))
        elif line.startswith(("- ", "* ")):
            story.append(Paragraph(f"• {_escape(line[2:])}", body_style))
        else:
            story.append(Paragraph(_escape(line), body_style))

    doc.build(story)
    buf.seek(0)
    return buf.read()


def _escape(text):
    # basic escaping for reportlab + simple bold/italic
    text = (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", text)
    return text