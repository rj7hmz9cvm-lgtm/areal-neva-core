from pathlib import Path

from docx import Document


class WriterEngine:
    @staticmethod
    def generate_docx(text: str, path: str) -> str:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        doc = Document()
        for block in str(text).split("\n\n"):
            doc.add_paragraph(block)
        doc.save(str(p))
        return str(p)
