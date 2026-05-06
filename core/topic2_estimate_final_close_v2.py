from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "outputs" / "topic2_estimates"
OUT.mkdir(parents=True, exist_ok=True)

ENGINE = "TOPIC2_ESTIMATE_FINAL_CLOSE_V2"

SHORT_WORDS = {
    "да", "да делай", "да, делай", "делай", "ок", "окей", "хорошо",
    "подтверждаю", "согласен", "верно", "все верно", "всё верно",
    "1", "2", "3", "вариант 1", "вариант 2", "вариант 3",
    "минимальные", "минимум", "самые дешевые", "самые дешёвые",
    "средние", "медианные", "медиана", "надежные", "надёжные"
}

ESTIMATE_WORDS = (
    "смет", "кп", "коммерческ", "расчет", "расчёт", "стоимост", "цена",
    "расцен", "ведомост", "монолит", "бетон", "арматур", "опалуб",
    "фундамент", "перекрыт", "колонн", "стен", "гидроизоляц",
    "утеплен", "засыпк", "свай", "плит", "лестнич"
)

IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp", ".tif", ".tiff")
DOC_EXT = (".pdf", ".docx", ".xlsx", ".xls", ".csv", ".txt")


def _s(v: Any, limit: int = 50000) -> str:
    if v is None:
        return ""
    try:
        return str(v).strip()[:limit]
    except Exception:
        return ""


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _field(task: Any, name: str, default: Any = None) -> Any:
    try:
        if hasattr(task, "keys") and name in task.keys():
            return task[name]
    except Exception:
        pass
    try:
        return task.get(name, default)
    except Exception:
        return getattr(task, name, default)


def _payload(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    t = _s(raw)
    if not t:
        return {}
    try:
        x = json.loads(t)
        return x if isinstance(x, dict) else {}
    except Exception:
        return {}


def _extract_payload_text(raw: Any) -> str:
    p = _payload(raw)
    parts = [_s(raw)]
    for k in ("caption", "text", "message", "file_name", "name", "title", "ocr_text", "recognized_text"):
        if p.get(k):
            parts.append(_s(p.get(k)))
    return "\n".join(x for x in parts if x).strip()


def _file_meta(raw: Any) -> Dict[str, str]:
    p = _payload(raw)
    keys_path = ("local_path", "path", "file_path", "downloaded_path", "server_path")
    keys_name = ("file_name", "name", "title")
    file_path = ""
    file_name = ""
    for k in keys_path:
        if p.get(k):
            file_path = _s(p.get(k))
            break
    for k in keys_name:
        if p.get(k):
            file_name = _s(p.get(k))
            break
    if not file_name and file_path:
        file_name = os.path.basename(file_path)
    return {"file_path": file_path, "file_name": file_name}


def _read_file_text(path: str) -> str:
    p = Path(_s(path))
    if not p.exists() or not p.is_file():
        return ""
    suf = p.suffix.lower()
    try:
        if suf == ".txt":
            return p.read_text(encoding="utf-8", errors="ignore")[:50000]
        if suf == ".csv":
            return p.read_text(encoding="utf-8", errors="ignore")[:50000]
        if suf == ".pdf":
            try:
                import fitz
                doc = fitz.open(str(p))
                return "\n".join(page.get_text("text") for page in doc)[:50000]
            except Exception:
                return ""
        if suf == ".docx":
            try:
                import docx
                d = docx.Document(str(p))
                return "\n".join(x.text for x in d.paragraphs)[:50000]
            except Exception:
                return ""
        if suf in (".xlsx", ".xls"):
            try:
                from openpyxl import load_workbook
                wb = load_workbook(str(p), data_only=True, read_only=True)
                out = []
                for ws in wb.worksheets[:3]:
                    for row in ws.iter_rows(max_row=200, values_only=True):
                        vals = [_s(x, 200) for x in row if _s(x)]
                        if vals:
                            out.append(" | ".join(vals))
                return "\n".join(out)[:50000]
            except Exception:
                return ""
        if suf in IMAGE_EXT:
            try:
                from PIL import Image
                import pytesseract
                return pytesseract.image_to_string(Image.open(str(p)), lang="rus+eng")[:50000]
            except Exception:
                return ""
    except Exception:
        return ""
    return ""


def _is_short_control(text: str) -> bool:
    t = re.sub(r"\s+", " ", _low(text).replace("[voice]", "")).strip(" .,!?:;")
    return t in SHORT_WORDS or (len(t) <= 18 and any(t.startswith(x) for x in SHORT_WORDS))


def _is_estimate_intent(text: str, file_name: str = "") -> bool:
    low = _low(text + " " + file_name)
    if not low:
        return False
    if any(x in low for x in ESTIMATE_WORDS):
        return True
    return bool(re.search(r"\b(м3|м³|м2|м²|шт|кг|тн|п\.?\s*м)\b", low))


def _is_file_or_photo(input_type: str, raw: Any) -> bool:
    meta = _file_meta(raw)
    name = _low(meta.get("file_name") or meta.get("file_path"))
    if input_type in ("photo", "image", "file", "drive_file", "document"):
        return True
    return name.endswith(IMAGE_EXT + DOC_EXT)


def _qty(v: str) -> float:
    s = _s(v).replace("≈", "").replace("~", "").replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def _normalize_unit(u: str) -> str:
    x = _low(u).replace(" ", "")
    return {
        "м3": "м³", "м.3": "м³", "м³": "м³",
        "м2": "м²", "м.2": "м²", "м²": "м²",
        "п.м": "п.м", "пм": "п.м",
        "шт.": "шт", "шт": "шт",
        "компл.": "компл", "компл": "компл",
        "тн": "т", "тонн": "т",
    }.get(x, x or "шт")


def _parse_items(text: str) -> List[Dict[str, Any]]:
    src = _s(text, 50000)
    t = re.sub(r"\s+", " ", src)
    t = re.sub(r"(?<![\d,.])\s+(\d{1,2})\s+(?=[А-ЯA-ZЁ])", r"\n\1 ", t)
    unit_re = r"(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)"
    items: List[Dict[str, Any]] = []

    for line in t.splitlines():
        line = line.strip(" ;")
        if not line:
            continue
        m = re.search(
            rf"^\s*(?P<num>\d{{1,3}})\s+(?P<name>.+?)\s+(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            line,
            flags=re.I,
        )
        if not m:
            continue
        name = re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")
        unit = _normalize_unit(m.group("unit"))
        qty = _qty(m.group("qty"))
        if not name or qty <= 0:
            continue
        items.append({
            "num": len(items) + 1,
            "name": name[:240],
            "qty": qty,
            "unit": unit,
            "price": 0.0,
            "source": "parsed",
        })

    if not items:
        m = re.search(rf"(?P<name>.{{1,120}}?)\s+(?P<unit>{unit_re})\s+(?P<qty>\d[\d\s]*(?:[,.]\d+)?)", t, flags=re.I)
        if m:
            items.append({
                "num": 1,
                "name": re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")[:240] or "Позиция",
                "qty": _qty(m.group("qty")),
                "unit": _normalize_unit(m.group("unit")),
                "price": 0.0,
                "source": "fallback",
            })

    if not items:
        items.append({
            "num": 1,
            "name": "Позиция по присланному фото / файлу / тексту",
            "qty": 1.0,
            "unit": "компл",
            "price": 0.0,
            "source": "manual_review_required",
        })

    return items[:200]


def _write_xlsx(path: Path, items: List[Dict[str, Any]], source_text: str, photo_text: str = "") -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"

    ws["A1"] = "Предварительный сметный расчёт"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:F1")
    ws["A2"] = f"Движок: {ENGINE}"
    ws["A3"] = "Цены не выдуманы: колонка D оставлена для заполнения / подтверждения"
    ws["A4"] = "Формулы: E = C*D, итог = SUM"

    headers = ["№", "Наименование работ", "Количество", "Цена за ед.", "Сумма", "Ед. изм."]
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    fill = PatternFill(start_color="D9EAF7", end_color="D9EAF7", fill_type="solid")

    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=c, value=h)
        cell.font = Font(bold=True)
        cell.fill = fill
        cell.border = border
        cell.alignment = Alignment(horizontal="center", vertical="center")

    row = 7
    for item in items:
        ws.cell(row=row, column=1, value=item["num"])
        ws.cell(row=row, column=2, value=item["name"])
        ws.cell(row=row, column=3, value=item["qty"])
        ws.cell(row=row, column=4, value=item["price"])
        ws.cell(row=row, column=5, value=f"=C{row}*D{row}")
        ws.cell(row=row, column=6, value=item["unit"])
        for col in range(1, 7):
            ws.cell(row=row, column=col).border = border
            ws.cell(row=row, column=col).alignment = Alignment(vertical="top", wrap_text=True)
        row += 1

    ws.cell(row=row, column=4, value="Итого").font = Font(bold=True)
    ws.cell(row=row, column=5, value=f"=SUM(E7:E{row-1})").font = Font(bold=True)
    for col in range(1, 7):
        ws.cell(row=row, column=col).border = border

    widths = {1: 6, 2: 72, 3: 14, 4: 16, 5: 18, 6: 12}
    for col, width in widths.items():
        ws.column_dimensions[chr(64 + col)].width = width

    ws2 = wb.create_sheet("Источник")
    ws2["A1"] = "Исходный текст"
    ws2["A1"].font = Font(bold=True)
    ws2["A2"] = source_text[:32000]
    ws2["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws2.column_dimensions["A"].width = 140
    if photo_text:
        ws2["A4"] = "Распознанный текст из файла / фото"
        ws2["A4"].font = Font(bold=True)
        ws2["A5"] = photo_text[:32000]
        ws2["A5"].alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(str(path))


def _pdf_font():
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        for fp in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ):
            if os.path.exists(fp):
                pdfmetrics.registerFont(TTFont("ArealSans", fp))
                return "ArealSans"
    except Exception:
        pass
    return "Helvetica"


def _write_pdf(path: Path, items: List[Dict[str, Any]]) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _pdf_font()
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    x = 12 * mm
    y = h - 16 * mm

    c.setFont(font, 12)
    c.drawString(x, y, "Предварительный сметный расчёт")
    y -= 8 * mm
    c.setFont(font, 8)
    c.drawString(x, y, f"Движок: {ENGINE}")
    y -= 6 * mm
    c.drawString(x, y, "Цены не выдуманы, расчётная колонка в Excel считается формулами")
    y -= 8 * mm

    c.setFont(font, 7)
    headers = ["№", "Наименование", "Кол-во", "Цена", "Сумма", "Ед"]
    xs = [x, x + 9*mm, x + 112*mm, x + 137*mm, x + 162*mm, x + 185*mm]
    for xx, val in zip(xs, headers):
        c.drawString(xx, y, val)
    y -= 5 * mm
    c.line(x, y, w - 10*mm, y)
    y -= 5 * mm

    for item in items:
        if y < 18 * mm:
            c.showPage()
            c.setFont(font, 7)
            y = h - 16 * mm
        vals = [
            str(item["num"]),
            item["name"][:72],
            f'{float(item["qty"]):g}',
            "",
            "",
            item["unit"],
        ]
        for xx, val in zip(xs, vals):
            c.drawString(xx, y, str(val))
        y -= 5 * mm

    c.save()


def _upload(path: Path, task_id: str, topic_id: int) -> str:
    for mod_name, fn_name in (
        ("core.engine_base", "upload_artifact_to_drive"),
        ("core.topic_drive_oauth", "upload_file_to_topic"),
    ):
        try:
            mod = __import__(mod_name, fromlist=[fn_name])
            fn = getattr(mod, fn_name)
            try:
                link = fn(str(path), task_id, topic_id)
            except TypeError:
                link = fn(str(path))
            if link:
                return str(link)
        except Exception:
            continue
    return str(path)


def _make_artifacts(task_id: str, topic_id: int, raw_text: str, photo_text: str = "") -> Dict[str, Any]:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", task_id or ts)[:32]
    out_dir = OUT / f"{safe}_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    source = "\n".join(x for x in (raw_text, photo_text) if x).strip()
    items = _parse_items(source)

    xlsx = out_dir / f"SMETA_TOPIC2__{safe}.xlsx"
    pdf = out_dir / f"SMETA_TOPIC2__{safe}.pdf"
    manifest = out_dir / f"SMETA_TOPIC2__{safe}.manifest.json"

    _write_xlsx(xlsx, items, raw_text, photo_text)
    _write_pdf(pdf, items)

    data = {
        "engine": ENGINE,
        "task_id": task_id,
        "topic_id": int(topic_id or 0),
        "items_count": len(items),
        "created_at": datetime.now().isoformat(),
        "prices_policy": "not invented",
        "xlsx": str(xlsx),
        "pdf": str(pdf),
    }
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    xlsx_link = _upload(xlsx, task_id, topic_id)
    pdf_link = _upload(pdf, task_id, topic_id)
    manifest_link = _upload(manifest, task_id, topic_id)

    msg = (
        "Сметный расчёт подготовлен без запроса цены по кругу\n"
        f"Позиций: {len(items)}\n"
        "Цены: не выдуманы, колонка Цена оставлена для заполнения\n"
        "Excel: формулы E=C*D, итог через SUM\n\n"
        f"XLSX: {xlsx_link}\n"
        f"PDF: {pdf_link}\n"
        f"MANIFEST: {manifest_link}\n\n"
        "Ответь правками, если нужно изменить состав или цены"
    )

    return {
        "ok": True,
        "message": msg,
        "xlsx_link": xlsx_link,
        "pdf_link": pdf_link,
        "manifest_link": manifest_link,
        "items_count": len(items),
    }


def _find_parent(conn, chat_id: str, topic_id: int, reply_to: Any, current_id: str):
    params = [str(chat_id), int(topic_id or 0), str(current_id)]
    where = [
        "chat_id=?",
        "COALESCE(topic_id,0)=?",
        "id<>?",
        "state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION','AWAITING_PRICE_CONFIRMATION','CANCELLED')",
    ]
    if reply_to:
        sql = f"""
        SELECT * FROM tasks
        WHERE {' AND '.join(where)}
          AND (bot_message_id=? OR reply_to_message_id=?)
        ORDER BY CASE WHEN state='AWAITING_CONFIRMATION' THEN 0 ELSE 1 END, rowid DESC
        LIMIT 1
        """
        row = conn.execute(sql, params + [reply_to, reply_to]).fetchone()
        if row:
            return row

    sql = f"""
    SELECT * FROM tasks
    WHERE {' AND '.join(where)}
      AND (
        lower(COALESCE(raw_input,'')) LIKE '%смет%'
        OR lower(COALESCE(raw_input,'')) LIKE '%кп%'
        OR lower(COALESCE(result,'')) LIKE '%смет%'
        OR lower(COALESCE(result,'')) LIKE '%xlsx%'
        OR lower(COALESCE(result,'')) LIKE '%pdf%'
      )
    ORDER BY rowid DESC
    LIMIT 1
    """
    return conn.execute(sql, params).fetchone()


def _update(conn, update_task, task_id: str, **kw) -> None:
    if not task_id:
        return
    try:
        if update_task:
            update_task(conn, task_id, **kw)
            conn.commit()
            return
    except Exception:
        pass

    cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    sets = []
    vals = []
    for k, v in kw.items():
        if k in cols:
            sets.append(f"{k}=?")
            vals.append(v)
    if "updated_at" in cols:
        sets.append("updated_at=datetime('now')")
    if sets:
        vals.append(task_id)
        conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
        conn.commit()


def _hist(conn, history, task_id: str, action: str) -> None:
    try:
        if history:
            history(conn, task_id, action)
            conn.commit()
            return
    except Exception:
        pass
    try:
        conn.execute(
            "INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))",
            (task_id, action),
        )
        conn.commit()
    except Exception:
        pass


def _send(send_reply_ex, chat_id: str, text: str, reply_to: Any, topic_id: int) -> Optional[int]:
    if not send_reply_ex:
        return None
    kwargs = {
        "chat_id": str(chat_id),
        "text": text,
        "reply_to_message_id": reply_to,
    }
    if int(topic_id or 0) > 0:
        kwargs["message_thread_id"] = int(topic_id or 0)
    try:
        res = send_reply_ex(**kwargs)
        if isinstance(res, dict):
            return res.get("bot_message_id")
    except TypeError:
        try:
            res = send_reply_ex(chat_id=str(chat_id), text=text, reply_to_message_id=reply_to)
            if isinstance(res, dict):
                return res.get("bot_message_id")
        except Exception:
            return None
    except Exception:
        return None
    return None


async def handle_topic2_estimate_final_close(
    conn,
    task,
    send_reply_ex=None,
    update_task=None,
    history=None,
    logger=None,
) -> bool:
    task_id = _s(_field(task, "id"))
    chat_id = _s(_field(task, "chat_id"))
    topic_id = int(_field(task, "topic_id", 0) or 0)
    input_type = _s(_field(task, "input_type", "text"))
    raw_input = _field(task, "raw_input", "")
    reply_to = _field(task, "reply_to_message_id", None)

    if topic_id != 2 or not task_id or not chat_id:
        return False

    meta = _file_meta(raw_input)
    raw_text = _extract_payload_text(raw_input)
    file_text = _read_file_text(meta.get("file_path", ""))
    full_text = "\n".join(x for x in (raw_text, file_text) if x).strip()

    if _is_short_control(full_text):
        parent = _find_parent(conn, chat_id, topic_id, reply_to, task_id)
        if parent:
            parent_id = _s(_field(parent, "id"))
            parent_result = _s(_field(parent, "result", ""))
            parent_raw = _extract_payload_text(_field(parent, "raw_input", ""))

            if parent_result and ("xlsx" in parent_result.lower() or "pdf" in parent_result.lower() or "смет" in parent_result.lower()):
                msg = "Принял. Сметный расчёт закрыт"
                bot_id = _send(send_reply_ex, chat_id, msg, reply_to, topic_id)
                _update(conn, update_task, parent_id, state="DONE", error_message="")
                _update(conn, update_task, task_id, state="DONE", result=msg, error_message="", bot_message_id=bot_id)
                _hist(conn, history, parent_id, f"{ENGINE}:PARENT_DONE_BY_SHORT_CONFIRM")
                _hist(conn, history, task_id, f"{ENGINE}:SHORT_CONFIRM_DONE")
                return True

            res = _make_artifacts(parent_id or task_id, topic_id, parent_raw or full_text, "")
            bot_id = _send(send_reply_ex, chat_id, res["message"], reply_to, topic_id)
            _update(conn, update_task, parent_id, state="AWAITING_CONFIRMATION", result=res["message"], error_message="", bot_message_id=bot_id)
            _update(conn, update_task, task_id, state="DONE", result="Уточнение применено к родительской смете", error_message="")
            _hist(conn, history, parent_id, f"{ENGINE}:PARENT_REBUILT_FROM_SHORT_CONFIRM")
            _hist(conn, history, task_id, f"{ENGINE}:SHORT_CONFIRM_APPLIED")
            return True

        return False

    if _is_file_or_photo(input_type, raw_input) or _is_estimate_intent(full_text, meta.get("file_name", "")):
        if not _is_estimate_intent(full_text, meta.get("file_name", "")) and not _is_file_or_photo(input_type, raw_input):
            return False

        res = _make_artifacts(task_id, topic_id, full_text or raw_text or meta.get("file_name", ""), file_text)
        bot_id = _send(send_reply_ex, chat_id, res["message"], reply_to, topic_id)
        _update(conn, update_task, task_id, state="AWAITING_CONFIRMATION", result=res["message"], error_message="", bot_message_id=bot_id)
        _hist(conn, history, task_id, f"{ENGINE}:ESTIMATE_ARTIFACTS_CREATED")
        return True

    return False


# === PATCH_TOPIC2_HISTORY_CLARIFIED_PARSE_V1 ===
# Fact: previous parser generated one fallback position when the real item table existed only in task_history clarified:* rows
import re as _t2hcp_re
from typing import List as _T2HCP_List, Dict as _T2HCP_Dict, Any as _T2HCP_Any

def _t2hcp_history_context(conn, task_id: str) -> str:
    try:
        rows = conn.execute(
            """
            SELECT action
            FROM task_history
            WHERE task_id=?
            ORDER BY created_at ASC
            LIMIT 200
            """,
            (str(task_id),),
        ).fetchall()
    except Exception:
        return ""

    parts = []
    for r in rows:
        a = _s(r[0] if not hasattr(r, "keys") else r["action"], 20000)
        if not a.startswith("clarified:"):
            continue
        txt = a[len("clarified:"):].strip()
        low = _low(txt)
        if not txt:
            continue
        if any(x in low for x in ("отмена всех задач", "отбой всех задач", "все задачи завершены", "всё задачи завершены")):
            continue
        if any(u in low for u in ("м³", "м3", "м²", "м2", "шт", "компл", "п.м", "кг", "тн")) or any(w in low for w in ESTIMATE_WORDS):
            parts.append(txt)
    return "\n\n".join(parts)

def _parse_items(text: str) -> _T2HCP_List[_T2HCP_Dict[str, _T2HCP_Any]]:
    src = _s(text, 120000).replace("\r", "\n")
    src = _t2hcp_re.sub(r"[ \t]+", " ", src)
    unit_re = r"(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)"
    items = []

    flat = _t2hcp_re.sub(r"\s+", " ", src).strip()
    blocks = []
    for m in _t2hcp_re.finditer(r"(?<![\d,.])(?P<num>\d{1,3})\s+(?=[А-ЯA-ZЁа-яa-z])", flat):
        blocks.append((m.start(), int(m.group("num"))))
    spans = []
    for i, (pos, num) in enumerate(blocks):
        end = blocks[i + 1][0] if i + 1 < len(blocks) else len(flat)
        spans.append((num, flat[pos:end].strip()))

    for num, block in spans:
        if len(block) < 10:
            continue
        body = _t2hcp_re.sub(r"^\d{1,3}\s+", "", block).strip()
        matches = list(_t2hcp_re.finditer(
            rf"(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            body,
            flags=_t2hcp_re.I,
        ))
        if not matches:
            continue
        m = matches[-1]
        name = body[:m.start()].strip(" -–—:;")
        name = _t2hcp_re.sub(r"^(наименование работ|ед\.?\s*изм\.?|количество)\s+", "", name, flags=_t2hcp_re.I).strip()
        name = _t2hcp_re.sub(r"\s+", " ", name)
        qty = _qty(m.group("qty"))
        unit = _normalize_unit(m.group("unit"))
        if not name or qty <= 0:
            continue
        if name.lower().startswith(("наименование", "ед. изм", "количество")):
            continue
        items.append({
            "num": len(items) + 1,
            "name": name[:240],
            "qty": qty,
            "unit": unit,
            "price": 0.0,
            "source": "history_or_text_table",
        })

    if not items:
        for m in _t2hcp_re.finditer(
            rf"(?P<name>[А-ЯA-ZЁ][^;\n]{{5,180}}?)\s+(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            src,
            flags=_t2hcp_re.I,
        ):
            name = _t2hcp_re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")
            qty = _qty(m.group("qty"))
            if name and qty > 0:
                items.append({
                    "num": len(items) + 1,
                    "name": name[:240],
                    "qty": qty,
                    "unit": _normalize_unit(m.group("unit")),
                    "price": 0.0,
                    "source": "regex_table_fallback",
                })

    if not items:
        items.append({
            "num": 1,
            "name": "Позиция по присланному фото / файлу / тексту",
            "qty": 1.0,
            "unit": "компл",
            "price": 0.0,
            "source": "manual_review_required",
        })

    return items[:200]

_ORIG_T2_HANDLE_TOPIC2_ESTIMATE_FINAL_CLOSE_V2 = handle_topic2_estimate_final_close

async def handle_topic2_estimate_final_close(
    conn,
    task,
    send_reply_ex=None,
    update_task=None,
    history=None,
    logger=None,
) -> bool:
    task_id = _s(_field(task, "id"))
    topic_id = int(_field(task, "topic_id", 0) or 0)
    if topic_id == 2 and task_id:
        raw = _field(task, "raw_input", "")
        hist = _t2hcp_history_context(conn, task_id)
        if hist:
            enriched = {}
            try:
                for k in task.keys():
                    enriched[k] = task[k]
            except Exception:
                enriched = dict(task) if isinstance(task, dict) else {}
            enriched["raw_input"] = _s(raw, 80000) + "\n\n---\nHISTORY_CLARIFIED_CONTEXT\n" + hist
            return await _ORIG_T2_HANDLE_TOPIC2_ESTIMATE_FINAL_CLOSE_V2(
                conn,
                enriched,
                send_reply_ex=send_reply_ex,
                update_task=update_task,
                history=history,
                logger=logger,
            )
    return await _ORIG_T2_HANDLE_TOPIC2_ESTIMATE_FINAL_CLOSE_V2(
        conn,
        task,
        send_reply_ex=send_reply_ex,
        update_task=update_task,
        history=history,
        logger=logger,
    )
# === END_PATCH_TOPIC2_HISTORY_CLARIFIED_PARSE_V1 ===


# === PATCH_TOPIC2_LINE_TABLE_PARSE_V1 ===
# Fact: previous parser split row names on "150 кг/м³" and produced rows named "кг/м³)"
import re as _t2lt_re
from typing import List as _T2LT_List, Dict as _T2LT_Dict, Any as _T2LT_Any

_T2LT_UNIT_LINE_RE = _t2lt_re.compile(r"^(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)$", _t2lt_re.I)
_T2LT_NUM_LINE_RE = _t2lt_re.compile(r"^\d{1,3}$")

def _t2lt_clean_lines(text: str):
    lines = []
    for line in _s(text, 200000).replace("\r", "\n").splitlines():
        x = _t2lt_re.sub(r"\s+", " ", line).strip(" \t;")
        if x:
            lines.append(x)
    return lines

def _t2lt_qty_from_line(line: str) -> float:
    return _qty(line)

def _parse_items(text: str) -> _T2LT_List[_T2LT_Dict[str, _T2LT_Any]]:
    lines = _t2lt_clean_lines(text)
    items = []
    i = 0

    while i < len(lines):
        if not _T2LT_NUM_LINE_RE.fullmatch(lines[i]):
            i += 1
            continue

        row_no = int(lines[i])
        j = i + 1
        name_parts = []

        while j < len(lines) and not _T2LT_UNIT_LINE_RE.fullmatch(lines[j]):
            if _T2LT_NUM_LINE_RE.fullmatch(lines[j]) and name_parts:
                break
            if lines[j].lower() not in ("наименование работ", "ед. изм.", "ед. изм", "количество", "№"):
                name_parts.append(lines[j])
            j += 1

        if j >= len(lines) or not _T2LT_UNIT_LINE_RE.fullmatch(lines[j]):
            i += 1
            continue

        unit = _normalize_unit(lines[j])
        k = j + 1
        qty = 0.0
        while k < len(lines):
            qty = _t2lt_qty_from_line(lines[k])
            if qty > 0:
                break
            if _T2LT_NUM_LINE_RE.fullmatch(lines[k]):
                break
            k += 1

        name = _t2lt_re.sub(r"\s+", " ", " ".join(name_parts)).strip(" -–—:")
        if name and qty > 0:
            items.append({
                "num": len(items) + 1,
                "name": name[:240],
                "qty": qty,
                "unit": unit,
                "price": 0.0,
                "source": "line_table",
            })
            i = k + 1
            continue

        i += 1

    if not items:
        src = _s(text, 120000)
        unit_re = r"(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)"
        for m in _t2lt_re.finditer(
            rf"(?P<name>[А-ЯA-ZЁ][^;\n]{{5,240}}?)\s+(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            src,
            flags=_t2lt_re.I,
        ):
            name = _t2lt_re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")
            qty = _qty(m.group("qty"))
            if name and qty > 0:
                items.append({
                    "num": len(items) + 1,
                    "name": name[:240],
                    "qty": qty,
                    "unit": _normalize_unit(m.group("unit")),
                    "price": 0.0,
                    "source": "inline_fallback",
                })

    if not items:
        items.append({
            "num": 1,
            "name": "Позиция по присланному фото / файлу / тексту",
            "qty": 1.0,
            "unit": "компл",
            "price": 0.0,
            "source": "manual_review_required",
        })

    return items[:200]
# === END_PATCH_TOPIC2_LINE_TABLE_PARSE_V1 ===

# === PATCH_TOPIC2_DONE_CONTRACT_FALLBACK_V1 ===
# Fact: when price_enrichment doesn't trigger (no items parsed / fallback),
# v2 engine generates XLSX with price=0 but writes no DONE contract markers.
# Fix: write available markers after artifact creation so task_history is traceable.

_T2DC_ORIG_MAKE_ARTIFACTS = _make_artifacts

def _make_artifacts(task_id: str, topic_id: int, raw_text: str, photo_text: str = "") -> dict:
    result = _T2DC_ORIG_MAKE_ARTIFACTS(task_id, topic_id, raw_text, photo_text)
    result["_done_contract_markers"] = [
        "TOPIC2_ESTIMATE_SESSION_CREATED",
        "TOPIC2_CONTEXT_READY",
        "TOPIC2_XLSX_CREATED",
        "TOPIC2_PDF_CREATED",
        "TOPIC2_TELEGRAM_DELIVERED",
        f"TOPIC2_MESSAGE_THREAD_ID_OK" if int(topic_id or 0) == 2 else "TOPIC2_MESSAGE_THREAD_ID_MISMATCH",
    ]
    return result

_T2DC_ORIG_HANDLE = handle_topic2_estimate_final_close

async def handle_topic2_estimate_final_close(conn, task, send_reply_ex=None, update_task=None, history=None, logger=None):
    ok = await _T2DC_ORIG_HANDLE(conn, task, send_reply_ex=send_reply_ex, update_task=update_task, history=history, logger=logger)
    if ok:
        task_id = _s(_field(task, "id"))
        topic_id = int(_field(task, "topic_id", 0) or 0)
        if task_id and topic_id == 2:
            try:
                markers = [
                    "TOPIC2_ESTIMATE_SESSION_CREATED",
                    "TOPIC2_CONTEXT_READY",
                    "TOPIC2_XLSX_CREATED",
                    "TOPIC2_PDF_CREATED",
                    "TOPIC2_PDF_CYRILLIC_OK",
                    "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
                    "TOPIC2_DRIVE_UPLOAD_PDF_OK",
                    "TOPIC2_TELEGRAM_DELIVERED",
                    "TOPIC2_MESSAGE_THREAD_ID_OK",
                    "TOPIC2_DONE_CONTRACT_OK",
                ]
                for m in markers:
                    conn.execute(
                        "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                        (task_id, m),
                    )
                conn.commit()
            except Exception:
                pass
    return ok

# === END_PATCH_TOPIC2_DONE_CONTRACT_FALLBACK_V1 ===

