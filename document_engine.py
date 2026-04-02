from pathlib import Path
import tempfile, subprocess, os, shutil
def _ocr_image(path: str) -> str:
    p = subprocess.run(["tesseract", path, "stdout", "-l", "eng+rus"], stdout=subprocess.PIPE, text=True)
    return p.stdout[:20000] if p.returncode == 0 else ""
def read(path):
    p = Path(path); suf = p.suffix.lower()
    if not p.exists() or p.name.startswith("."): return ""
    try:
        if suf == ".pdf":
            import pdfplumber
            with pdfplumber.open(p) as pdf: t = "\n".join(pg.extract_text() or "" for pg in pdf.pages[:15])
            return t[:20000]
        if suf == ".docx":
            from docx import Document
            return "\n".join(x.text for x in Document(p).paragraphs)[:20000]
        if suf in (".txt", ".md"): return p.read_text(encoding="utf-8", errors="ignore")[:20000]
        if suf in (".jpg", ".jpeg", ".png", ".webp"): return _ocr_image(str(p))
    except: pass
    return ""
