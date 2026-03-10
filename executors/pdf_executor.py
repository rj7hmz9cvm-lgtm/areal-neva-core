from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
import os

def create_pdf(text, filename="outputs/result.pdf"):
    os.makedirs("outputs", exist_ok=True)
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("ArialUnicode", font_path))
        font_name = "ArialUnicode"
    else:
        font_name = "Helvetica"

    c.setFont(font_name, 11)
    y = height - 40

    for raw_line in text.split("\n"):
        line = raw_line[:140]
        c.drawString(40, y, line)
        y -= 16
        if y < 40:
            c.showPage()
            c.setFont(font_name, 11)
            y = height - 40

    c.save()
    return filename
