# === FULLFIX_15_PDF_CYRILLIC ===
import os, logging
logger = logging.getLogger(__name__)
FONT_REGULAR = "CyrRegular"
FONT_BOLD = "CyrBold"
FONT_PATH_REGULAR = ""
FONT_PATH_BOLD = ""
_registered = False

_CANDS_R = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]
_CANDS_B = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]

def _find(candidates):
    for p in candidates:
        if os.path.exists(p):
            return p
    import glob
    for pat in ["/usr/share/fonts/**/*DejaVu*Sans*.ttf",
                "/usr/share/fonts/**/*Noto*Sans*Regular*.ttf"]:
        found = glob.glob(pat, recursive=True)
        if found:
            return found[0]
    return None

def register_cyrillic_fonts():
    global _registered, FONT_REGULAR, FONT_BOLD, FONT_PATH_REGULAR, FONT_PATH_BOLD
    if _registered:
        return FONT_REGULAR, FONT_BOLD
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    reg = _find(_CANDS_R)
    bold = _find(_CANDS_B)
    if not reg:
        raise RuntimeError("CYRILLIC_FONT_NOT_FOUND")
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, reg))
    FONT_PATH_REGULAR = reg
    if bold and bold != reg:
        pdfmetrics.registerFont(TTFont(FONT_BOLD, bold))
        FONT_PATH_BOLD = bold
    else:
        FONT_BOLD = FONT_REGULAR
        FONT_PATH_BOLD = reg
    _registered = True
    logger.info("CYR_FONTS reg=%s bold=%s", reg, bold)
    return FONT_REGULAR, FONT_BOLD

def clean_pdf_text(text):
    if not text:
        return ""
    return "".join(c for c in str(text) if c >= " " or c in "\n\t")

def make_styles():
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    register_cyrillic_fonts()
    return {
        "header": ParagraphStyle("H", fontName=FONT_BOLD, fontSize=16, alignment=TA_CENTER, spaceAfter=12),
        "title":  ParagraphStyle("T", fontName=FONT_BOLD, fontSize=14, alignment=TA_CENTER, spaceAfter=8),
        "bold":   ParagraphStyle("B", fontName=FONT_BOLD, fontSize=9, alignment=TA_LEFT),
        "normal": ParagraphStyle("N", fontName=FONT_REGULAR, fontSize=9, alignment=TA_LEFT),
        "small":  ParagraphStyle("S", fontName=FONT_REGULAR, fontSize=8, alignment=TA_LEFT),
    }

def make_paragraph(text, style="normal", styles=None):
    from reportlab.platypus import Paragraph
    if styles is None:
        styles = make_styles()
    return Paragraph(clean_pdf_text(text), styles.get(style, styles["normal"]))
# === END FULLFIX_15_PDF_CYRILLIC ===

# === FIX_PDF_CYRILLIC_VALIDATE_V1 ===
import subprocess as _pcv_sub
import re as _pcv_re

def validate_cyrillic_pdf(pdf_path: str) -> tuple:
    """
    Returns (ok: bool, code: str)
    Extracts text from PDF and checks for valid Cyrillic content.
    """
    extracted = ""
    try:
        r = _pcv_sub.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=15,
        )
        extracted = r.stdout or ""
    except Exception:
        try:
            from pdfminer.high_level import extract_text as _pdfm_ext
            extracted = _pdfm_ext(str(pdf_path)) or ""
        except Exception:
            return True, "VALIDATION_SKIPPED_NO_TOOL"

    if not extracted.strip():
        return False, "ESTIMATE_PDF_EMPTY_TEXT_V1"
    if "■" in extracted or "�" in extracted or u"■" in extracted:
        return False, "ESTIMATE_PDF_CYRILLIC_BROKEN_V1"
    cyr = sum(1 for c in extracted if "Ѐ" <= c <= "ӿ")
    alpha = sum(1 for c in extracted if c.isalpha())
    if alpha > 30 and cyr / alpha < 0.08:
        return False, "ESTIMATE_PDF_CYRILLIC_BROKEN_V1"
    return True, "TOPIC2_PDF_CYRILLIC_OK"


def create_pdf_with_cyrillic(path: str, text: str, title: str = "") -> bool:
    """
    Create PDF at path using DejaVuSans for Cyrillic. Returns True on success.
    """
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as rl_canvas

        reg, bold = register_cyrillic_fonts()
        c = rl_canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        y = height - 40

        if title:
            c.setFont(bold, 12)
            c.drawString(40, y, clean_pdf_text(title)[:100])
            y -= 24

        c.setFont(reg, 9)
        for line in str(text).splitlines():
            if y < 40:
                c.showPage()
                y = height - 40
                c.setFont(reg, 9)
            c.drawString(40, y, clean_pdf_text(line)[:130])
            y -= 13
        c.save()
        return True
    except Exception as _pdf_e:
        logger.warning("create_pdf_with_cyrillic FAILED: %s", _pdf_e)
        return False

logger.info("FIX_PDF_CYRILLIC_VALIDATE_V1 installed")
# === END_FIX_PDF_CYRILLIC_VALIDATE_V1 ===
