import os
import re
import csv
import json
import base64
import tempfile
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=True)

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()

def _clean(text: str, limit: int = 12000) -> str:
    text = (text or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]

def _kind(file_name: str, mime_type: str = "") -> str:
    ext = os.path.splitext((file_name or "").lower())[1]
    mime = (mime_type or "").lower()
    if ext in (".jpg", ".jpeg", ".png", ".heic", ".webp") or mime.startswith("image/"):
        return "image"
    if ext in (".xlsx", ".xlsm", ".csv") or "spreadsheet" in mime or mime == "text/csv":
        return "table"
    if ext in (".pdf", ".docx", ".doc", ".txt") or mime in ("application/pdf", "text/plain"):
        return "document"
    if ext in (".dwg", ".dxf") or "dxf" in mime or "dwg" in mime:
        return "drawing"
    return "binary"

def _build_word(title: str, summary: str, defects: List[Dict[str, Any]], recommendations: List[str], sources: List[str]) -> str:
    from docx import Document

    fd, out = tempfile.mkstemp(prefix="artifact_", suffix=".docx", dir="/tmp")
    os.close(fd)

    doc = Document()
    doc.add_heading(title or "Результат обработки", level=1)

    if summary:
        doc.add_paragraph(_clean(summary, 12000))

    if sources:
        doc.add_heading("Источники", level=2)
        for s in sources:
            doc.add_paragraph(_s(s))

    doc.add_heading("Замечания", level=2)
    if defects:
        for idx, item in enumerate(defects, 1):
            p = doc.add_paragraph()
            p.add_run(f"{idx}. ").bold = True
            p.add_run(_s(item.get("title")) or "Замечание")
            sev = _s(item.get("severity"))
            if sev:
                p.add_run(f" [{sev}]")
            desc = _s(item.get("description"))
            if desc:
                doc.add_paragraph(desc)
    else:
        doc.add_paragraph("Замечания не выделены")

    doc.add_heading("Рекомендации", level=2)
    if recommendations:
        for r in recommendations:
            doc.add_paragraph(_s(r))
    else:
        doc.add_paragraph("Рекомендации не сформированы")

    doc.save(out)
    return out

def _build_excel(title: str, items: List[Dict[str, str]], summary: str, sources: List[str]) -> str:
    from openpyxl import Workbook

    fd, out = tempfile.mkstemp(prefix="artifact_", suffix=".xlsx", dir="/tmp")
    os.close(fd)

    wb = Workbook()
    ws = wb.active
    ws.title = "Результат"
    ws["A1"] = title or "Табличный результат"
    ws["A2"] = _clean(summary, 1000)

    row = 4
    headers = ["№", "Наименование", "Ед", "Кол-во", "Примечание"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=row, column=col, value=h)
    row += 1

    for idx, item in enumerate(items, 1):
        ws.cell(row=row, column=1, value=idx)
        ws.cell(row=row, column=2, value=_s(item.get("name")))
        ws.cell(row=row, column=3, value=_s(item.get("unit")))
        ws.cell(row=row, column=4, value=_s(item.get("qty")))
        ws.cell(row=row, column=5, value=_s(item.get("note")))
        row += 1

    src = wb.create_sheet("Источники")
    for idx, s in enumerate(sources, 1):
        src.cell(row=idx, column=1, value=_s(s))

    wb.save(out)
    return out

def _extract_pdf(path: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        parts = []
        for page in reader.pages:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                pass
        return _clean("\n".join(parts), 12000)
    except Exception as e:
        return f"PDF_PARSE_ERROR: {e}"

def _extract_docx(path: str) -> str:
    try:
        from docx import Document
        doc = Document(path)
        return _clean("\n".join(p.text for p in doc.paragraphs if p.text), 12000)
    except Exception as e:
        return f"DOCX_PARSE_ERROR: {e}"

def _extract_txt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return _clean(f.read(), 12000)
    except Exception as e:
        return f"TXT_PARSE_ERROR: {e}"

def _extract_table_items(path: str, file_name: str) -> List[Dict[str, str]]:
    rows: List[List[str]] = []
    ext = os.path.splitext((file_name or "").lower())[1]

    try:
        if ext == ".csv":
            with open(path, "r", encoding="utf-8", errors="ignore", newline="") as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    rows.append([_s(x) for x in row])
                    if idx >= 300:
                        break
        else:
            from openpyxl import load_workbook
            wb = load_workbook(path, data_only=True, read_only=True)
            for ws in wb.worksheets[:3]:
                rows.append([f"__SHEET__:{ws.title}"])
                for idx, row in enumerate(ws.iter_rows(values_only=True)):
                    rows.append([_s(x) for x in row])
                    if idx >= 300:
                        break
    except Exception as e:
        rows.append([f"TABLE_PARSE_ERROR: {e}"])

    items: List[Dict[str, str]] = []
    unit_re = re.compile(r"\b(м2|м3|м\.п\.|п\.м\.|шт|кг|тн|т|м)\b", re.I)
    qty_re = re.compile(r"^\d+[.,]?\d*$")

    for row in rows:
        if not row:
            continue
        if len(row) == 1 and _s(row[0]).startswith("__SHEET__:"):
            continue

        cleaned = [_s(x) for x in row if _s(x)]
        if not cleaned:
            continue

        name = cleaned[0]
        unit = ""
        qty = ""
        note = ""

        for cell in cleaned[1:]:
            if not unit:
                m = unit_re.search(cell)
                if m:
                    unit = m.group(1)
                    continue
            if not qty and qty_re.match(cell.replace(" ", "")):
                qty = cell.replace(" ", "")
                continue
            note = (note + " | " + cell).strip(" |") if note else cell

        if len(name) < 2:
            continue

        items.append({
            "name": name[:500],
            "unit": unit[:32],
            "qty": qty[:64],
            "note": note[:500],
        })

        if len(items) >= 500:
            break

    return items

async def _vision_image(path: str, user_text: str, topic_role: str) -> Optional[Dict[str, Any]]:
    api_key = (os.getenv("OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        return None

    base_url = (os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip().rstrip("/")
    model = (os.getenv("OPENROUTER_VISION_MODEL") or "google/gemini-2.5-flash").strip()

    ext = os.path.splitext(path)[1].lower().lstrip(".") or "jpeg"
    mime = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"

    try:
        import httpx
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        prompt = (
            "Ты анализируешь строительную фотофиксацию\n"
            f"Роль чата: {topic_role or 'технадзор'}\n"
            f"Задача пользователя: {user_text or 'проанализируй фото'}\n\n"
            "Верни только JSON вида:\n"
            "{\n"
            '  "summary": "краткое резюме",\n'
            '  "defects": [{"title":"...", "description":"...", "severity":"low|medium|high"}],\n'
            '  "recommendations": ["...", "..."]\n'
            "}"
        )

        body = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    ],
                }
            ],
            "temperature": 0.1,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=30.0)) as client:
            r = await client.post(f"{base_url}/chat/completions", headers=headers, json=body)
            r.raise_for_status()
            data = r.json()

        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in content)
        content = _clean(_s(content), 12000)

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {
                "summary": content[:3000],
                "defects": [],
                "recommendations": [],
            }

    except Exception:
        return None

    return None

async def analyze_downloaded_file(local_path: str, file_name: str, mime_type: str = "", user_text: str = "", topic_role: str = "") -> Optional[Dict[str, Any]]:
    kind = _kind(file_name, mime_type)
    sources = [file_name]

    if kind == "image":
        analysis = await _vision_image(local_path, user_text, topic_role)
        if not analysis:
            return None
        summary = _s(analysis.get("summary")) or "Фото проанализировано"
        defects = analysis.get("defects") if isinstance(analysis.get("defects"), list) else []
        recommendations = analysis.get("recommendations") if isinstance(analysis.get("recommendations"), list) else []
        artifact_path = _build_word(
            "Акт замечаний по фотофиксации",
            summary,
            defects,
            [_s(x) for x in recommendations],
            sources,
        )
        return {
            "summary": summary,
            "artifact_path": artifact_path,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_photo_report.docx",
        }

    if kind == "table":
        items = _extract_table_items(local_path, file_name)
        summary = f"Нормализовано позиций: {len(items)}"
        artifact_path = _build_excel(
            "Сметный/табличный результат",
            items,
            summary,
            sources,
        )
        return {
            "summary": summary,
            "artifact_path": artifact_path,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_estimate.xlsx",
        }

    if kind == "document":
        ext = os.path.splitext((file_name or "").lower())[1]
        if ext == ".pdf":
            text = _extract_pdf(local_path)
        elif ext == ".docx":
            text = _extract_docx(local_path)
        else:
            text = _extract_txt(local_path)

        summary = _clean(text, 3000) if text else "Документ обработан"
        artifact_path = _build_word(
            "Сводка по документу",
            summary,
            [],
            [],
            sources,
        )
        return {
            "summary": summary,
            "artifact_path": artifact_path,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_document_summary.docx",
        }

    return None
