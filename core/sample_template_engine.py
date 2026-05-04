# === FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE ===
import os
import re
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List, Tuple

ENGINE = "FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE"
BASE = Path("/root/.areal-neva-core")
TEMPLATE_ROOT = BASE / "data" / "templates"
ESTIMATE_TEMPLATE_DIR = TEMPLATE_ROOT / "estimate"
PROJECT_TEMPLATE_DIR = TEMPLATE_ROOT / "project"

SAMPLE_WORDS = (
    "образец", "шаблон", "пример", "как образец", "как шаблон",
    "используй это", "возьми это", "сохрани это", "запомни это",
    "по этому", "по нему", "по ней", "в таком формате", "такой формат"
)

ESTIMATE_WORDS = (
    "смет", "кс-2", "кс2", "ведомост", "спецификац", "расцен", "цена",
    "стоимост", "позици", "материал", "работ", "руб", "xlsx", "excel", "таблиц"
)

PROJECT_WORDS = (
    "проект", "кж", "кд", "ар", "км", "чертеж", "чертёж", "плит", "фундамент",
    "кровл", "стропил", "архитект", "dxf", "dwg", "pdf"
)

FILE_EXT_ESTIMATE = (".xlsx", ".xls", ".csv")
FILE_EXT_PROJECT = (".pdf", ".dxf", ".dwg", ".docx")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_text(v: Any) -> str:
    return str(v or "").strip()


def _json_loads_maybe(v: Any) -> Dict[str, Any]:
    if isinstance(v, dict):
        return v
    s = _safe_text(v)
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}


def _low(v: Any) -> str:
    return _safe_text(v).lower().replace("ё", "е")


def _task_history_insert(conn, task_id: str, action: str) -> None:
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(task_history)").fetchall()]
        if "action" in cols:
            conn.execute(
                "INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))",
                (task_id, action),
            )
        elif "event" in cols:
            conn.execute(
                "INSERT INTO task_history (task_id,event,created_at) VALUES (?,?,datetime('now'))",
                (task_id, action),
            )
        conn.commit()
    except Exception:
        pass


def _send_reply(chat_id: str, text: str, reply_to_message_id: Optional[int] = None) -> Optional[int]:
    try:
        from core.reply_sender import send_reply_ex
        res = send_reply_ex(
            chat_id=str(chat_id),
            text=text,
            reply_to_message_id=reply_to_message_id,
        )
        if isinstance(res, dict):
            return res.get("bot_message_id")
    except Exception:
        return None
    return None


def _update_task(conn, task_id: str, state: str, result: str = "", error_message: str = "", bot_message_id: Optional[int] = None) -> None:
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
        sets = ["state=?", "result=?", "error_message=?", "updated_at=datetime('now')"]
        vals: List[Any] = [state, result, error_message]
        if bot_message_id and "bot_message_id" in cols:
            sets.append("bot_message_id=?")
            vals.append(int(bot_message_id))
        vals.append(task_id)
        conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
        conn.commit()
    except Exception:
        pass


def detect_sample_template_intent(raw_input: Any, input_type: str = "") -> bool:
    payload = _json_loads_maybe(raw_input)
    text = " ".join([
        _safe_text(raw_input),
        _safe_text(payload.get("caption")),
        _safe_text(payload.get("file_name")),
    ])
    low = _low(text)
    if not low:
        return False
    has_sample = any(w in low for w in SAMPLE_WORDS)
    if not has_sample:
        return False
    has_domain = any(w in low for w in ESTIMATE_WORDS + PROJECT_WORDS)
    if has_domain:
        return True
    return any(x in low for x in ("файл", "это", "таблица", "документ"))


def detect_estimate_intent(raw_input: Any) -> bool:
    low = _low(raw_input)
    if not low:
        return False
    if any(w in low for w in ("проект", "фундамент", "плит", "кровл", "стропил", "чертеж", "чертёж")):
        return False
    return any(w in low for w in ("смет", "посчитай", "расчет", "расчёт", "профлист", "монтаж", "цена", "руб", "м2", "м²", "шт", "ведомость"))


def _template_kind_from_text_and_file(text: str, file_name: str) -> str:
    low = _low(text + " " + file_name)
    ext = Path(file_name).suffix.lower()
    if any(w in low for w in ESTIMATE_WORDS) or ext in FILE_EXT_ESTIMATE:
        return "estimate"
    if any(w in low for w in PROJECT_WORDS) or ext in FILE_EXT_PROJECT:
        return "project"
    return "estimate"


def _parse_file_payload(row_raw: Any) -> Dict[str, Any]:
    payload = _json_loads_maybe(row_raw)
    return {
        "file_id": _safe_text(payload.get("file_id")),
        "file_name": _safe_text(payload.get("file_name")),
        "mime_type": _safe_text(payload.get("mime_type")),
        "caption": _safe_text(payload.get("caption")),
        "source": _safe_text(payload.get("source")),
        "telegram_message_id": payload.get("telegram_message_id"),
        "raw_payload": payload,
    }


def _find_latest_related_file(conn, chat_id: str, topic_id: int, current_task_id: str = "", prefer_estimate: bool = True) -> Optional[Dict[str, Any]]:
    rows = []
    try:
        rows = conn.execute(
            """
            SELECT id,chat_id,COALESCE(topic_id,0) AS topic_id,input_type,raw_input,result,created_at,updated_at
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND input_type='drive_file'
            ORDER BY rowid DESC
            LIMIT 50
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()
    except Exception:
        rows = []

    if not rows:
        try:
            rows = conn.execute(
                """
                SELECT id,chat_id,COALESCE(topic_id,0) AS topic_id,input_type,raw_input,result,created_at,updated_at
                FROM tasks
                WHERE chat_id=?
                  AND input_type='drive_file'
                ORDER BY rowid DESC
                LIMIT 50
                """,
                (str(chat_id),),
            ).fetchall()
        except Exception:
            rows = []

    best = None
    best_score = -1

    for r in rows:
        raw = r["raw_input"] if hasattr(r, "keys") else r[4]
        payload = _parse_file_payload(raw)
        file_name = payload.get("file_name", "")
        low_name = _low(file_name)
        score = 0
        if any(low_name.endswith(ext) for ext in FILE_EXT_ESTIMATE):
            score += 80
        if any(k in low_name for k in ("smet", "смет", "vor", "кирп", "price", "cost", "ведом")):
            score += 40
        if prefer_estimate and any(low_name.endswith(ext) for ext in FILE_EXT_ESTIMATE):
            score += 30
        if "project_" in low_name or "кж_project" in low_name or "кд_project" in low_name:
            score -= 60
        if "smoke" in low_name:
            score -= 80
        if score > best_score:
            best_score = score
            best = {
                "task_id": r["id"] if hasattr(r, "keys") else r[0],
                "chat_id": r["chat_id"] if hasattr(r, "keys") else r[1],
                "topic_id": r["topic_id"] if hasattr(r, "keys") else r[2],
                "result": r["result"] if hasattr(r, "keys") else r[5],
                "created_at": r["created_at"] if hasattr(r, "keys") else r[6],
                "updated_at": r["updated_at"] if hasattr(r, "keys") else r[7],
                **payload,
                "score": score,
            }

    return best


def _template_paths(kind: str, chat_id: str, topic_id: int) -> Tuple[Path, Path]:
    base_dir = ESTIMATE_TEMPLATE_DIR if kind == "estimate" else PROJECT_TEMPLATE_DIR
    base_dir.mkdir(parents=True, exist_ok=True)
    safe_chat = re.sub(r"[^0-9A-Za-z_-]+", "_", str(chat_id))[:80]
    active = base_dir / f"ACTIVE__chat_{safe_chat}__topic_{int(topic_id or 0)}.json"
    snapshot = base_dir / f"TEMPLATE__chat_{safe_chat}__topic_{int(topic_id or 0)}__{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    return active, snapshot


def save_template_pointer(conn, chat_id: str, topic_id: int, task_id: str, raw_input: Any, input_type: str = "text") -> Tuple[bool, Dict[str, Any], str]:
    payload = _json_loads_maybe(raw_input)
    text = " ".join([_safe_text(raw_input), _safe_text(payload.get("caption"))])

    if input_type == "drive_file":
        file_meta = _parse_file_payload(raw_input)
        file_meta.update({"task_id": task_id, "chat_id": chat_id, "topic_id": topic_id})
    else:
        file_meta = _find_latest_related_file(conn, chat_id, topic_id, task_id, prefer_estimate=True)

    if not file_meta or not file_meta.get("file_id"):
        return False, {}, "RELATED_FILE_NOT_FOUND"

    kind = _template_kind_from_text_and_file(text, file_meta.get("file_name", ""))
    active, snapshot = _template_paths(kind, chat_id, topic_id)

    template = {
        "engine": ENGINE,
        "kind": kind,
        "status": "active",
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "saved_by_task_id": str(task_id),
        "source_task_id": str(file_meta.get("task_id") or ""),
        "source_file_id": str(file_meta.get("file_id") or ""),
        "source_file_name": str(file_meta.get("file_name") or ""),
        "source_mime_type": str(file_meta.get("mime_type") or ""),
        "source_caption": str(file_meta.get("caption") or ""),
        "source_score": file_meta.get("score"),
        "saved_at": _now(),
        "usage_rule": "Use this file as formatting/sample reference for future estimate/project artifacts in the same chat and topic",
        "raw_user_instruction": _safe_text(raw_input),
    }

    active.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    snapshot.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        conn.execute(
            "INSERT INTO memory (chat_id,key,value,timestamp) VALUES (?,?,?,datetime('now'))",
            (
                str(chat_id),
                f"topic_{int(topic_id or 0)}_{kind}_active_template",
                json.dumps(template, ensure_ascii=False),
            ),
        )
        conn.commit()
    except Exception:
        pass

    _task_history_insert(conn, task_id, f"FULLFIX_13A_TEMPLATE_SAVED:{kind}:{file_meta.get('file_name')}")
    return True, template, ""


def _load_active_template(kind: str, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    active, _ = _template_paths(kind, chat_id, topic_id)
    if active.exists():
        try:
            return json.loads(active.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _parse_estimate_items(text: str) -> List[Dict[str, Any]]:
    src = _safe_text(text)
    low = _low(src)

    parts = re.split(r"[;\n]+|,\s*(?=[А-Яа-яA-Za-z])", src)
    items = []

    for part in parts:
        p = part.strip()
        if not p:
            continue
        m_qty = re.search(r"(.{0,80}?)(\d+(?:[.,]\d+)?)\s*(м²|м2|м\.?2|м³|м3|м\.?3|п\.?м|м\b|шт|кг|т|тонн)", p, re.I)
        if not m_qty:
            continue
        name = re.sub(r"^(сделай|смета|смету|посчитай|расчет|расчёт)\s*:?", "", m_qty.group(1).strip(), flags=re.I).strip(" :-,")
        if not name:
            name = "Позиция"
        qty = float(m_qty.group(2).replace(",", "."))
        unit_raw = m_qty.group(3).lower().replace("м.2", "м²").replace("м2", "м²").replace("м.3", "м³").replace("м3", "м³").replace("пм", "п.м")
        tail = p[m_qty.end():]
        price = 0.0
        m_price = re.search(r"(?:по|цена|стоимость)\s*(\d+(?:[.,]\d+)?)", tail, re.I)
        if not m_price:
            m_price = re.search(r"(\d+(?:[.,]\d+)?)\s*руб", tail, re.I)
        if m_price:
            price = float(m_price.group(1).replace(",", "."))
        items.append({
            "name": name[:120],
            "qty": qty,
            "unit": unit_raw,
            "price": price,
            "total": round(qty * price, 2),
        })

    if not items:
        # fallback for short text
        nums = re.findall(r"\d+(?:[.,]\d+)?", src)
        if nums:
            qty = float(nums[0].replace(",", "."))
            price = float(nums[1].replace(",", ".")) if len(nums) > 1 else 0.0
            items.append({"name": "Позиция по смете", "qty": qty, "unit": "шт", "price": price, "total": round(qty * price, 2)})

    return items


def _write_estimate_xlsx(path: str, items: List[Dict[str, Any]], template: Optional[Dict[str, Any]], raw_input: str) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    fill = PatternFill(start_color="D9EAF7", end_color="D9EAF7", fill_type="solid")

    ws["A1"] = "Смета"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:F1")
    ws["A2"] = f"Движок: {ENGINE}"
    ws["A3"] = f"Шаблон: {template.get('source_file_name') if template else 'не задан'}"
    ws["A4"] = f"Запрос: {raw_input[:180]}"

    headers = ["№", "Наименование", "Ед", "Кол-во", "Цена", "Сумма"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=c, value=h)
        cell.font = Font(bold=True)
        cell.fill = fill
        cell.border = border
        cell.alignment = Alignment(horizontal="center")

    row = 7
    for i, item in enumerate(items, 1):
        vals = [i, item["name"], item["unit"], item["qty"], item["price"], item["total"]]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.border = border
        row += 1

    ws.cell(row=row, column=5, value="Итого").font = Font(bold=True)
    ws.cell(row=row, column=6, value=sum(float(x.get("total") or 0) for x in items)).font = Font(bold=True)

    widths = [6, 48, 10, 14, 14, 16]
    for idx, width in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + idx)].width = width

    ws2 = wb.create_sheet("Шаблон")
    ws2["A1"] = "Активный шаблон"
    ws2["A1"].font = Font(bold=True, size=12)
    if template:
        rows = [
            ("Файл", template.get("source_file_name")),
            ("File ID", template.get("source_file_id")),
            ("Тип", template.get("kind")),
            ("Сохранён", template.get("saved_at")),
            ("Правило", template.get("usage_rule")),
        ]
    else:
        rows = [("Файл", "Шаблон не найден")]
    for r, (k, v) in enumerate(rows, 3):
        ws2.cell(row=r, column=1, value=k)
        ws2.cell(row=r, column=2, value=v)
    ws2.column_dimensions["A"].width = 18
    ws2.column_dimensions["B"].width = 90

    wb.save(path)


def _write_estimate_pdf(path: str, items: List[Dict[str, Any]], template: Optional[Dict[str, Any]], raw_input: str) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # === FULLFIX_15_SAMPLE_PDF_CYR_FIX ===
    try:
        from core.pdf_cyrillic import register_cyrillic_fonts, FONT_REGULAR, FONT_BOLD
        register_cyrillic_fonts()
        font = FONT_REGULAR
        font_bold = FONT_BOLD
    except Exception:
        font = "Helvetica"
        font_bold = "Helvetica-Bold"
    for fp in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("ArealSans", fp))
                font = "ArealSans"
                break
            except Exception:
                pass

    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    x = 15 * mm
    y = h - 18 * mm

    c.setFont(font, 14)
    c.drawString(x, y, "Смета")
    y -= 9 * mm
    c.setFont(font, 8)
    c.drawString(x, y, f"Движок: {ENGINE}")
    y -= 5 * mm
    c.drawString(x, y, f"Шаблон: {template.get('source_file_name') if template else 'не задан'}")
    y -= 8 * mm

    headers = ["№", "Наименование", "Ед", "Кол-во", "Цена", "Сумма"]
    xs = [x, x + 10*mm, x + 95*mm, x + 115*mm, x + 140*mm, x + 165*mm]
    c.setFont(font, 8)
    for col, val in zip(xs, headers):
        c.drawString(col, y, val)
    y -= 4 * mm
    c.line(x, y, w - 15*mm, y)
    y -= 5 * mm

    total = 0.0
    for i, item in enumerate(items, 1):
        if y < 25 * mm:
            c.showPage()
            y = h - 20 * mm
            c.setFont(font, 8)
        total += float(item.get("total") or 0)
        vals = [
            str(i),
            str(item.get("name", ""))[:45],
            str(item.get("unit", "")),
            f"{float(item.get('qty') or 0):g}",
            f"{float(item.get('price') or 0):.2f}",
            f"{float(item.get('total') or 0):.2f}",
        ]
        for col, val in zip(xs, vals):
            c.drawString(col, y, val)
        y -= 6 * mm

    y -= 4 * mm
    c.line(x, y, w - 15*mm, y)
    y -= 7 * mm
    c.setFont(font, 10)
    c.drawString(x + 130*mm, y, f"Итого: {total:.2f} руб")
    c.save()


def _upload(path: str, task_id: str, topic_id: int) -> str:
    try:
        from core.engine_base import upload_artifact_to_drive
        return str(upload_artifact_to_drive(path, task_id, topic_id) or "")
    except Exception:
        return ""


async def create_estimate_from_saved_template(raw_input: str, task_id: str, chat_id: str, topic_id: int = 0) -> Dict[str, Any]:
    template = _load_active_template("estimate", chat_id, topic_id)
    if not template:
        return {"success": False, "engine": ENGINE, "error": "ACTIVE_ESTIMATE_TEMPLATE_NOT_FOUND"}

    items = _parse_estimate_items(raw_input)
    if not items:
        return {"success": False, "engine": ENGINE, "error": "ESTIMATE_ITEMS_NOT_PARSED"}

    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id))[:30]
    out_dir = Path(tempfile.gettempdir()) / f"areal_ff13a_estimate_{safe}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = str(out_dir / f"estimate_{safe}.xlsx")
    pdf_path = str(out_dir / f"estimate_{safe}.pdf")
    manifest_path = str(out_dir / f"estimate_{safe}.manifest.json")

    _write_estimate_xlsx(xlsx_path, items, template, raw_input)
    _write_estimate_pdf(pdf_path, items, template, raw_input)

    total = round(sum(float(x.get("total") or 0) for x in items), 2)
    manifest = {
        "engine": ENGINE,
        "task_id": task_id,
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "kind": "estimate",
        "template": template,
        "items": items,
        "total": total,
        "created_at": _now(),
    }
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    pdf_link = _upload(pdf_path, task_id, topic_id)
    xlsx_link = _upload(xlsx_path, task_id, topic_id)
    manifest_link = _upload(manifest_path, task_id, topic_id)

    if not pdf_link or not xlsx_link:
        return {"success": False, "engine": ENGINE, "error": "ESTIMATE_UPLOAD_FAILED", "pdf_link": pdf_link, "xlsx_link": xlsx_link}

    msg = (
        "Смета создана по сохранённому образцу\n"
        f"Engine: {ENGINE}\n"
        f"Шаблон: {template.get('source_file_name')}\n"
        f"Позиций: {len(items)}\n"
        f"Итого: {total:.2f} руб\n\n"
        f"PDF: {pdf_link}\n"
        f"XLSX: {xlsx_link}\n"
        f"MANIFEST: {manifest_link}\n\n"
        "Доволен результатом? Ответь: Да / Уточни / Правки"
    )

    return {
        "success": True,
        "engine": ENGINE,
        "items": items,
        "total": total,
        "template": template,
        "pdf_link": pdf_link,
        "xlsx_link": xlsx_link,
        "manifest_link": manifest_link,
        "message": msg,
    }


async def handle_sample_template_intent(
    conn,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input: Any,
    input_type: str,
    reply_to_message_id: Optional[int] = None,
) -> bool:
    if conn is None:
        return False
    if not detect_sample_template_intent(raw_input, input_type):
        return False

    ok, template, err = save_template_pointer(conn, chat_id, topic_id, task_id, raw_input, input_type)
    if not ok:
        msg = (
            "Не смог сохранить образец: не нашёл связанный файл в этом чате/топике\n"
            "Пришли файл и сразу ответь на него: возьми это как образец"
        )
        bot_id = _send_reply(chat_id, msg, reply_to_message_id)
        _update_task(conn, task_id, "FAILED", msg, err or "RELATED_FILE_NOT_FOUND", bot_id)
        _task_history_insert(conn, task_id, f"FULLFIX_13A_TEMPLATE_SAVE_FAILED:{err}")
        return True

    kind_ru = "смет" if template.get("kind") == "estimate" else "проектной документации"
    msg = (
        f"Шаблон {kind_ru} сохранён\n"
        f"Файл: {template.get('source_file_name')}\n"
        f"Тип: {template.get('kind')}\n"
        f"Topic: {template.get('topic_id')}\n\n"
        "Дальше можешь писать простым языком: сделай смету / сделай проект"
    )
    bot_id = _send_reply(chat_id, msg, reply_to_message_id)
    _update_task(conn, task_id, "DONE", msg, "", bot_id)
    return True


async def handle_template_estimate_intent(
    conn,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input: Any,
    input_type: str,
    reply_to_message_id: Optional[int] = None,
) -> bool:
    if conn is None:
        return False
    if input_type not in ("text", "voice"):
        return False
    if not detect_estimate_intent(raw_input):
        return False
    template = _load_active_template("estimate", chat_id, topic_id)
    if not template:
        return False

    res = await create_estimate_from_saved_template(str(raw_input), task_id, chat_id, topic_id)
    if not res.get("success"):
        _task_history_insert(conn, task_id, f"FULLFIX_13A_TEMPLATE_ESTIMATE_FAILED:{res.get('error')}")
        return False

    msg = res.get("message") or "Смета создана"
    bot_id = _send_reply(chat_id, msg, reply_to_message_id)
    _update_task(conn, task_id, "AWAITING_CONFIRMATION", msg, "", bot_id)
    _task_history_insert(conn, task_id, "FULLFIX_13A_TEMPLATE_ESTIMATE_OK")
    return True

# === END FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE ===


# === FULLFIX_13B_TEMPLATE_SAVE_STRICT_ACK ===
def ff13b_template_saved_message(file_name: str = "", template_type: str = "estimate", topic_id: int = 0) -> str:
    name = str(file_name or "файл").strip()
    t = str(template_type or "estimate").strip()
    return (
        "Шаблон сохранён\n"
        f"Файл: {name}\n"
        f"Тип: {t}\n"
        f"Topic: {topic_id}\n\n"
        "Дальше можно писать простым языком: сделай смету / сделай проект"
    )
# === END FULLFIX_13B_TEMPLATE_SAVE_STRICT_ACK ===

# === PROJECT_TECHNADZOR_TEMPLATE_CLOSE_V1 ===

TECHNADZOR_TEMPLATE_DIR = TEMPLATE_ROOT / "technadzor"
TECHNADZOR_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

TECHNADZOR_WORDS = (
    "технадзор", "дефект", "акт", "нарушение", "предписание", "замечание",
    "осмотр", "проверка", "инспекция", "обследование", "фотофиксация",
)

PROJECT_INTENT_WORDS = (
    "сделай проект", "создай проект", "разработай проект", "подготовь проект",
    "применить шаблон", "используй шаблон", "по шаблону", "как в шаблоне",
    "создай документацию", "сделай документацию", "разработай документацию",
    "по образцу", "аналогично шаблону",
)

TECHNADZOR_INTENT_WORDS = (
    "составь акт", "сделай акт", "создай акт", "сформируй акт",
    "акт по шаблону", "акт как в шаблоне", "технадзор по шаблону",
    "используй шаблон акта", "применить шаблон акта",
)

def detect_project_template_intent(raw_input: Any) -> bool:
    low = _low(raw_input)
    return any(w in low for w in PROJECT_INTENT_WORDS)

def detect_technadzor_template_intent(raw_input: Any) -> bool:
    low = _low(raw_input)
    return any(w in low for w in TECHNADZOR_INTENT_WORDS)

def _technadzor_template_paths(chat_id: str, topic_id: int):
    base = TECHNADZOR_TEMPLATE_DIR / f"chat_{chat_id}" / f"topic_{topic_id}"
    base.mkdir(parents=True, exist_ok=True)
    return base / "active.json", base / "index.json"

async def create_project_from_saved_template(
    raw_input: str,
    task_id: str,
    chat_id: str,
    topic_id: int = 0,
) -> Dict[str, Any]:
    template = _load_active_template("project", chat_id, topic_id)
    if not template:
        return {"success": False, "error": "PROJECT_TEMPLATE_NOT_FOUND"}

    source_file = template.get("source_file_name") or ""
    source_path = template.get("source_file_path") or ""
    section = template.get("section") or "кр"

    try:
        if source_path and any(source_path.lower().endswith(e) for e in (".dwg", ".dxf")):
            from core.project_engine import process_dwg_dxf_project_file
            import asyncio
            res = await process_dwg_dxf_project_file(
                file_path=source_path,
                task_id=task_id,
                topic_id=topic_id,
                raw_input=raw_input,
                file_name=source_file,
                mime_type="",
            )
            if res and res.get("success"):
                link = _upload(res.get("artifact_path") or res.get("docx_path") or "", task_id, topic_id)
                msg = (
                    f"Проект создан по шаблону {source_file}\n"
                    f"Раздел: {res.get('section', section).upper()}\n"
                )
                if link:
                    msg += f"Документ: {link}"
                return {"success": True, "message": msg, "drive_link": link, "engine": "DWG_TEMPLATE"}
            return {"success": False, "error": str((res or {}).get("error", "DWG_PROJECT_FAILED"))}

        if source_path and any(source_path.lower().endswith(e) for e in (".pdf", ".docx", ".txt")):
            from core.project_document_engine import process_project_document
            res = await process_project_document(
                file_path=source_path,
                file_name=source_file,
                user_text=raw_input,
                topic_role="проектирование по шаблону",
                task_id=task_id,
                topic_id=topic_id,
            )
            if res and res.get("success"):
                link = _upload(res.get("artifact_path") or "", task_id, topic_id)
                msg = (
                    f"Проектная документация создана по шаблону {source_file}\n"
                    f"Раздел: {res.get('model', {}).get('section_title', section)}\n"
                )
                if link:
                    msg += f"Документ: {link}"
                return {"success": True, "message": msg, "drive_link": link, "engine": "PROJECT_DOC_TEMPLATE"}
            return {"success": False, "error": str((res or {}).get("error", "PROJECT_DOC_FAILED"))}

        return {"success": False, "error": "PROJECT_TEMPLATE_SOURCE_NOT_FOUND_OR_UNSUPPORTED"}

    except Exception as e:
        return {"success": False, "error": f"PROJECT_TEMPLATE_ERR:{e}"}


async def create_technadzor_from_saved_template(
    raw_input: str,
    task_id: str,
    chat_id: str,
    topic_id: int = 0,
    local_photo_path: str = "",
) -> Dict[str, Any]:
    act_ptr, _ = _technadzor_template_paths(chat_id, topic_id)
    if not act_ptr.exists():
        return {"success": False, "error": "TECHNADZOR_TEMPLATE_NOT_FOUND"}

    try:
        template = _json_loads_maybe(act_ptr.read_text(encoding="utf-8"))
    except Exception:
        return {"success": False, "error": "TECHNADZOR_TEMPLATE_CORRUPT"}

    from core.technadzor_engine import process_technadzor
    res = process_technadzor(
        conn=None,
        task_id=task_id,
        chat_id=chat_id,
        topic_id=topic_id,
        raw_input=raw_input or "Технический осмотр по шаблону",
        file_name=template.get("source_file_name") or "",
        local_path=local_photo_path or template.get("source_file_path") or "",
    )

    if res and res.get("ok"):
        art = res.get("artifact") or {}
        link = art.get("drive_link") or _upload(art.get("path") or "", task_id, topic_id)
        msg = res.get("result_text") or "Акт технадзора создан по шаблону"
        if link and link not in msg:
            msg += f"\n\nДокумент: {link}"
        return {"success": True, "message": msg, "drive_link": link, "engine": "TECHNADZOR_TEMPLATE"}

    return {"success": False, "error": "TECHNADZOR_TEMPLATE_ACT_FAILED"}


async def save_technadzor_template_pointer(
    conn,
    chat_id: str,
    topic_id: int,
    task_id: str,
    raw_input: Any,
    input_type: str = "text",
) -> Tuple[bool, Dict[str, Any], str]:
    act_ptr, idx_ptr = _technadzor_template_paths(chat_id, topic_id)

    payload = _parse_file_payload(raw_input)
    template = {
        "kind": "technadzor",
        "task_id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "source_file_id": payload.get("file_id") or "",
        "source_file_name": payload.get("file_name") or "",
        "source_file_path": payload.get("local_path") or payload.get("file_path") or "",
        "saved_at": _now(),
        "input_type": input_type,
        "raw_text": _safe_text(payload.get("caption") or raw_input)[:500],
    }

    try:
        act_ptr.write_text(_safe_text(template), encoding="utf-8")
        import json
        act_ptr.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        return False, template, f"TECHNADZOR_TEMPLATE_SAVE_ERR:{e}"

    return True, template, ""


async def handle_template_project_intent(
    conn,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input: Any,
    input_type: str,
    reply_to_message_id=None,
) -> bool:
    if conn is None:
        return False
    if input_type not in ("text", "voice"):
        return False
    if not detect_project_template_intent(raw_input):
        return False
    template = _load_active_template("project", chat_id, topic_id)
    if not template:
        return False

    res = await create_project_from_saved_template(str(raw_input), task_id, chat_id, topic_id)
    if not res.get("success"):
        _task_history_insert(conn, task_id, f"PROJECT_TEMPLATE_FAILED:{res.get('error')}")
        return False

    msg = res.get("message") or "Проект создан по шаблону"
    bot_id = _send_reply(chat_id, msg, reply_to_message_id)
    _update_task(conn, task_id, "AWAITING_CONFIRMATION", msg, "", bot_id)
    _task_history_insert(conn, task_id, "PROJECT_TEMPLATE_CLOSE_V1_OK")
    return True


async def handle_template_technadzor_intent(
    conn,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input: Any,
    input_type: str,
    reply_to_message_id=None,
) -> bool:
    if conn is None:
        return False
    if input_type not in ("text", "voice"):
        return False
    if not detect_technadzor_template_intent(raw_input):
        return False

    act_ptr, _ = _technadzor_template_paths(chat_id, topic_id)
    if not act_ptr.exists():
        return False

    res = await create_technadzor_from_saved_template(str(raw_input), task_id, chat_id, topic_id)
    if not res.get("success"):
        _task_history_insert(conn, task_id, f"TECHNADZOR_TEMPLATE_FAILED:{res.get('error')}")
        return False

    msg = res.get("message") or "Акт технадзора создан по шаблону"
    bot_id = _send_reply(chat_id, msg, reply_to_message_id)
    _update_task(conn, task_id, "AWAITING_CONFIRMATION", msg, "", bot_id)
    _task_history_insert(conn, task_id, "TECHNADZOR_TEMPLATE_CLOSE_V1_OK")
    return True

# === END PROJECT_TECHNADZOR_TEMPLATE_CLOSE_V1 ===



# === CLEAN_ESTIMATE_USER_OUTPUT_AND_TOTAL_FIX_V2 ===
# Public Telegram/PDF/XLSX output must not expose internal engine names, manifest links, temp paths, validator text or internal link keys.
# Saved template is formatting reference only. Current user text is the calculation source.

def _ceu2_num(v):
    try:
        return float(str(v or "0").replace(" ", "").replace(",", "."))
    except Exception:
        return 0.0

def _ceu2_unit(u: str) -> str:
    s = str(u or "").lower().replace("м.2", "м²").replace("м2", "м²").replace("м.3", "м³").replace("м3", "м³")
    s = s.replace("пм", "п.м").replace("пог.м", "п.м").replace("п. м", "п.м")
    return s.strip()

def _ceu2_find_price(text: str, patterns) -> float:
    for pat in patterns:
        m = re.search(pat, str(text or ""), re.I)
        if m:
            return _ceu2_num(m.group(1))
    return 0.0

def _parse_estimate_items(text: str) -> List[Dict[str, Any]]:
    src = _safe_text(text)
    if not src:
        return []

    lines = []
    for line in re.split(r"[\n\r]+", src):
        s = line.strip(" \t-•")
        if not s:
            continue
        s = re.sub(r"^\d+[\).\s-]+", "", s).strip()
        if not re.search(r"\d", s):
            continue
        if re.search(r"(м²|м2|м³|м3|п\.?\s?м|шт|кг|т\b|тонн|рейс)", s, re.I):
            lines.append(s)

    if not lines:
        lines = [x.strip() for x in re.split(r";+", src) if x.strip()]

    items = []
    for line in lines:
        m = re.search(
            r"(?P<name>.*?)(?:—|-|:)?\s*(?P<qty>\d+(?:[.,]\d+)?)\s*(?P<unit>м²|м2|м³|м3|п\.?\s?м|шт|кг|т\b|тонн|рейс)",
            line,
            re.I,
        )
        if not m:
            continue

        name = re.sub(r"\s*[—:-]\s*$", "", m.group("name")).strip(" —:-")
        if not name:
            name = "Позиция"

        qty = _ceu2_num(m.group("qty"))
        unit = _ceu2_unit(m.group("unit"))
        tail = line[m.end():]

        material_price = _ceu2_find_price(tail, [
            r"цена\s+материал[а-я]*\s*(\d+(?:[.,]\d+)?)",
            r"материал[а-я]*\s*(\d+(?:[.,]\d+)?)\s*руб",
            r"цена\s*(\d+(?:[.,]\d+)?)\s*руб",
            r"по\s*(\d+(?:[.,]\d+)?)\s*руб",
        ])

        work_price = _ceu2_find_price(tail, [
            r"цена\s+работ[а-я]*\s*(\d+(?:[.,]\d+)?)",
            r"работ[а-я]*\s*(\d+(?:[.,]\d+)?)\s*руб",
            r"вязк[а-я]*\s*(\d+(?:[.,]\d+)?)\s*руб",
        ])

        if material_price <= 0 and work_price <= 0:
            single = _ceu2_find_price(tail, [r"(\d+(?:[.,]\d+)?)\s*руб"])
            material_price = single

        material_sum = round(qty * material_price, 2)
        work_sum = round(qty * work_price, 2)
        total = round(material_sum + work_sum, 2)

        items.append({
            "name": name[:160],
            "unit": unit,
            "qty": qty,
            "material_price": material_price,
            "material_sum": material_sum,
            "work_price": work_price,
            "work_sum": work_sum,
            "price": round(material_price + work_price, 2),
            "total": total,
        })

    return items

def _write_estimate_xlsx(path: str, items: List[Dict[str, Any]], template: Optional[Dict[str, Any]], raw_input: str) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"

    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    fill = PatternFill(start_color="D9EAF7", end_color="D9EAF7", fill_type="solid")

    ws["A1"] = "Смета"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:I1")
    ws["A2"] = "Шаблон используется только как формат"
    ws["A3"] = f"Образец: {template.get('source_file_name') if template else 'не задан'}"

    headers = ["№", "Наименование", "Ед.", "Объём", "Цена материала", "Сумма материала", "Цена работы", "Сумма работы", "Итог"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=5, column=c, value=h)
        cell.font = Font(bold=True)
        cell.fill = fill
        cell.border = border
        cell.alignment = Alignment(horizontal="center")

    row = 6
    for i, item in enumerate(items, 1):
        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=item["name"])
        ws.cell(row=row, column=3, value=item["unit"])
        ws.cell(row=row, column=4, value=item["qty"])
        ws.cell(row=row, column=5, value=item["material_price"])
        ws.cell(row=row, column=6, value=f"=D{row}*E{row}")
        ws.cell(row=row, column=7, value=item["work_price"])
        ws.cell(row=row, column=8, value=f"=D{row}*G{row}")
        ws.cell(row=row, column=9, value=f"=F{row}+H{row}")
        for c in range(1, 10):
            ws.cell(row=row, column=c).border = border
        row += 1

    total_row = row + 1
    ws.cell(row=total_row, column=5, value="Итого материалы").font = Font(bold=True)
    ws.cell(row=total_row, column=6, value=f"=SUM(F6:F{row-1})").font = Font(bold=True)
    ws.cell(row=total_row + 1, column=5, value="Итого работы").font = Font(bold=True)
    ws.cell(row=total_row + 1, column=8, value=f"=SUM(H6:H{row-1})").font = Font(bold=True)
    ws.cell(row=total_row + 2, column=5, value="Общий итог").font = Font(bold=True)
    ws.cell(row=total_row + 2, column=9, value=f"=SUM(I6:I{row-1})").font = Font(bold=True)
    ws.cell(row=total_row + 3, column=5, value="НДС 20%").font = Font(bold=True)
    ws.cell(row=total_row + 3, column=9, value=f"=I{total_row+2}*20%").font = Font(bold=True)
    ws.cell(row=total_row + 4, column=5, value="Итого с НДС").font = Font(bold=True)
    ws.cell(row=total_row + 4, column=9, value=f"=I{total_row+2}+I{total_row+3}").font = Font(bold=True)

    for idx, width in enumerate([6, 48, 10, 12, 16, 18, 16, 18, 18], 1):
        ws.column_dimensions[get_column_letter(idx)].width = width

    ws2 = wb.create_sheet("Итоги")
    ws2["A1"] = "Итоги"
    ws2["A1"].font = Font(bold=True, size=14)
    ws2["A3"] = "Итого материалы"
    ws2["B3"] = f"='Смета'!F{total_row}"
    ws2["A4"] = "Итого работы"
    ws2["B4"] = f"='Смета'!H{total_row+1}"
    ws2["A5"] = "Общий итог"
    ws2["B5"] = f"='Смета'!I{total_row+2}"
    ws2["A6"] = "НДС 20%"
    ws2["B6"] = f"='Смета'!I{total_row+3}"
    ws2["A7"] = "Итого с НДС"
    ws2["B7"] = f"='Смета'!I{total_row+4}"

    ws3 = wb.create_sheet("Исходные данные")
    ws3["A1"] = "Текущее задание"
    ws3["A1"].font = Font(bold=True)
    ws3["A2"] = raw_input[:32000]
    ws3["A4"] = "Образец"
    ws3["A5"] = template.get("source_file_name") if template else "не задан"
    ws3.column_dimensions["A"].width = 120

    wb.save(path)

def _write_estimate_pdf(path: str, items: List[Dict[str, Any]], template: Optional[Dict[str, Any]], raw_input: str) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font = "Helvetica"
    for fp in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("ArealSans", fp))
                font = "ArealSans"
                break
            except Exception:
                pass

    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    x = 15 * mm
    y = h - 18 * mm

    c.setFont(font, 14)
    c.drawString(x, y, "Смета")
    y -= 8 * mm
    c.setFont(font, 8)
    c.drawString(x, y, "Образец: " + str(template.get("source_file_name") if template else "не задан")[:90])
    y -= 8 * mm

    xs = [x, x + 10*mm, x + 95*mm, x + 115*mm, x + 140*mm, x + 165*mm]
    headers = ["№", "Наименование", "Ед", "Объём", "Цена", "Итог"]
    for col, val in zip(xs, headers):
        c.drawString(col, y, val)
    y -= 4 * mm
    c.line(x, y, w - 15*mm, y)
    y -= 5 * mm

    total = 0.0
    for i, item in enumerate(items, 1):
        if y < 25 * mm:
            c.showPage()
            c.setFont(font, 8)
            y = h - 20 * mm
        total += float(item.get("total") or 0)
        vals = [
            str(i),
            str(item.get("name", ""))[:44],
            str(item.get("unit", "")),
            f"{float(item.get('qty') or 0):g}",
            f"{float(item.get('material_price') or 0) + float(item.get('work_price') or 0):.2f}",
            f"{float(item.get('total') or 0):.2f}",
        ]
        for col, val in zip(xs, vals):
            c.drawString(col, y, val)
        y -= 6 * mm

    y -= 4 * mm
    c.line(x, y, w - 15*mm, y)
    y -= 7 * mm
    c.setFont(font, 10)
    c.drawString(x + 125*mm, y, f"Итого: {total:.2f} руб")
    c.save()

def _ceu2_public_message(template: Optional[Dict[str, Any]], items: List[Dict[str, Any]], total: float, pdf_link: str, xlsx_link: str) -> str:
    file_name = ""
    try:
        file_name = str((template or {}).get("source_file_name") or "").strip()
    except Exception:
        file_name = ""
    if file_name:
        first = f"Смета создана по образцу {file_name}"
    else:
        first = "Смета создана"
    return (
        f"{first}\n"
        f"Позиций: {len(items)} | Итого: {total:.2f} руб\n\n"
        f"PDF: {pdf_link}\n"
        f"XLSX: {xlsx_link}\n\n"
        "Доволен результатом? Да / Уточни / Правки"
    )

async def create_estimate_from_saved_template(raw_input: str, task_id: str, chat_id: str, topic_id: int = 0) -> Dict[str, Any]:
    template = _load_active_template("estimate", chat_id, topic_id)
    if not template:
        return {"success": False, "error": "ACTIVE_ESTIMATE_TEMPLATE_NOT_FOUND"}

    items = _parse_estimate_items(raw_input)
    if not items:
        return {"success": False, "error": "ESTIMATE_ITEMS_NOT_PARSED"}

    total = round(sum(float(x.get("total") or 0) for x in items), 2)
    if total <= 0:
        return {
            "success": False,
            "error": "ESTIMATE_ZERO_TOTAL_BLOCKED",
            "result_text": "Смета не создана: позиции распознаны, но итог равен 0. Проверь цены материала/работы в задании",
            "items": items,
            "total": total,
        }

    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id))[:30]
    out_dir = Path(tempfile.gettempdir()) / f"areal_estimate_{safe}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = str(out_dir / f"estimate_{safe}.xlsx")
    pdf_path = str(out_dir / f"estimate_{safe}.pdf")
    manifest_path = str(out_dir / f"estimate_{safe}.manifest.json")

    _write_estimate_xlsx(xlsx_path, items, template, raw_input)
    _write_estimate_pdf(pdf_path, items, template, raw_input)

    manifest = {
        "engine": "CLEAN_ESTIMATE_USER_OUTPUT_AND_TOTAL_FIX_V2",
        "task_id": task_id,
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "template_used_as_format_only": True,
        "template_file": template.get("source_file_name"),
        "items": items,
        "total": total,
        "created_at": _now(),
    }
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    pdf_link = _upload(pdf_path, task_id, topic_id)
    xlsx_link = _upload(xlsx_path, task_id, topic_id)
    manifest_link = _upload(manifest_path, task_id, topic_id)

    if not pdf_link or not xlsx_link:
        return {
            "success": False,
            "error": "ESTIMATE_UPLOAD_FAILED",
            "result_text": "Смета создана локально, но не выгрузилась в Google Drive. Повторю выгрузку через очередь",
            "pdf_link": pdf_link,
            "xlsx_link": xlsx_link,
            "excel_path": xlsx_path,
            "artifact_path": xlsx_path,
            "items": items,
            "total": total,
        }

    msg = _ceu2_public_message(template, items, total, pdf_link, xlsx_link)

    return {
        "success": True,
        "engine": "CLEAN_ESTIMATE_USER_OUTPUT_AND_TOTAL_FIX_V2",
        "items": items,
        "total": total,
        "template": template,
        "template_used_as_format_only": True,
        "pdf_link": pdf_link,
        "xlsx_link": xlsx_link,
        "manifest_link": manifest_link,
        "drive_link": xlsx_link,
        "google_sheet_link": xlsx_link,
        "excel_path": xlsx_path,
        "artifact_path": xlsx_path,
        "message": msg,
        "result_text": msg,
    }
# === END_CLEAN_ESTIMATE_USER_OUTPUT_AND_TOTAL_FIX_V2 ===


# === WEB_SEARCH_PRICE_ENRICHMENT_V1_SAMPLE_TEMPLATE_WRAPPER ===
try:
    _web_price_orig_handle_template_estimate_intent = handle_template_estimate_intent
except Exception:
    _web_price_orig_handle_template_estimate_intent = None

async def handle_template_estimate_intent(
    conn,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input,
    input_type: str,
    reply_to_message_id=None,
) -> bool:
    try:
        from core.price_enrichment import maybe_handle_price_enrichment_from_template_engine
        handled = await maybe_handle_price_enrichment_from_template_engine(
            conn=conn,
            task_id=task_id,
            chat_id=chat_id,
            topic_id=topic_id,
            raw_input=raw_input,
            input_type=input_type,
            reply_to_message_id=reply_to_message_id,
        )
        if handled:
            return True
    except Exception:
        pass

    if _web_price_orig_handle_template_estimate_intent is None:
        return False

    return await _web_price_orig_handle_template_estimate_intent(
        conn,
        task_id,
        chat_id,
        topic_id,
        raw_input,
        input_type,
        reply_to_message_id,
    )

# === END_WEB_SEARCH_PRICE_ENRICHMENT_V1_SAMPLE_TEMPLATE_WRAPPER ===

# === THREE_CONTOURS_FINAL_SOURCE_LOCK_V1 ===
# Final source lock:
# - topic_2 estimates: ESTIMATES/templates from Drive is mandatory source of formatting/template
# - current user raw_input is mandatory calculation source
# - stale active templates, stale task results, old Drive links are forbidden
# - project/foundation/roof words must not block estimate route when "смет" is present

_FINAL_ESTIMATE_DRIVE_FOLDER_ID = "19Z3acDgPub4nV55mad5mb8ju63FsqoG9"
_FINAL_ROOT_DRIVE_FOLDER_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
_FINAL_DEFAULT_CHAT_ID = "-1003725299009"

def _final_json_dump(obj) -> str:
    import json as _json
    return _json.dumps(obj, ensure_ascii=False, indent=2)

def _final_drive_svc_v1():
    try:
        from core.engine_base import _drive_svc_v1
        return _drive_svc_v1()
    except Exception:
        return None

def _final_drive_list_files_v1(folder_id: str):
    svc = _final_drive_svc_v1()
    if svc is None:
        return []
    try:
        res = svc.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,size,modifiedTime)",
            pageSize=100,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        return res.get("files") or []
    except Exception:
        return []

def _final_estimate_score_template_v1(file_name: str, raw_input: str = "") -> int:
    low = (str(file_name or "") + " " + str(raw_input or "")).lower().replace("ё", "е")
    score = 0
    if file_name.lower().endswith((".xlsx", ".xls")):
        score += 100
    if any(x in low for x in ("м-80", "m-80", "м80", "m80")):
        score += 80
    if any(x in low for x in ("м-110", "m-110", "м110", "m110")):
        score += 80
    if any(x in low for x in ("фундамент", "склад", "плита", "бетон", "монолит")) and any(x in str(file_name).lower().replace("ё","е") for x in ("фундамент", "склад")):
        score += 70
    if any(x in low for x in ("кров", "крыша", "перекр", "строп")) and any(x in str(file_name).lower().replace("ё","е") for x in ("крыш", "кров", "перекр")):
        score += 70
    if any(x in low for x in ("ареал", "нева", "газобетон")) and any(x in str(file_name).lower().replace("ё","е") for x in ("ареал", "нева")):
        score += 70
    try:
        score += min(int(str(file_name).count(" ")) * 2, 10)
    except Exception:
        pass
    return score

def _final_select_estimate_template_v1(raw_input: str = "") -> dict:
    files = _final_drive_list_files_v1(_FINAL_ESTIMATE_DRIVE_FOLDER_ID)
    xlsx = [f for f in files if str(f.get("name","")).lower().endswith((".xlsx", ".xls"))]
    if not xlsx:
        return {}
    xlsx = sorted(
        xlsx,
        key=lambda f: (
            _final_estimate_score_template_v1(f.get("name",""), raw_input),
            int(f.get("size") or 0),
            str(f.get("modifiedTime") or ""),
        ),
        reverse=True,
    )
    return xlsx[0]

def _final_template_paths_estimate_v1(chat_id: str, topic_id: int):
    import re as _re
    safe_chat = _re.sub(r"[^0-9A-Za-z_-]+", "_", str(chat_id or _FINAL_DEFAULT_CHAT_ID))[:80]
    ESTIMATE_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    active = ESTIMATE_TEMPLATE_DIR / f"ACTIVE__chat_{safe_chat}__topic_{int(topic_id or 0)}.json"
    snapshot = ESTIMATE_TEMPLATE_DIR / f"TEMPLATE__chat_{safe_chat}__topic_{int(topic_id or 0)}__FINAL_SOURCE_LOCK.json"
    return active, snapshot

def _final_force_drive_estimate_template_v1(chat_id: str, topic_id: int, raw_input: str = "") -> dict:
    from datetime import datetime as _dt, timezone as _tz
    selected = _final_select_estimate_template_v1(raw_input)
    if not selected:
        return {}
    all_files = [
        {
            "file_id": f.get("id",""),
            "file_name": f.get("name",""),
            "mime_type": f.get("mimeType",""),
            "size": f.get("size",""),
            "modifiedTime": f.get("modifiedTime",""),
        }
        for f in _final_drive_list_files_v1(_FINAL_ESTIMATE_DRIVE_FOLDER_ID)
        if str(f.get("name","")).lower().endswith((".xlsx", ".xls"))
    ]
    template = {
        "engine": "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1",
        "kind": "estimate",
        "status": "active",
        "source": "DRIVE_ESTIMATES_TEMPLATES",
        "source_folder_name": "ESTIMATES/templates",
        "source_folder_id": _FINAL_ESTIMATE_DRIVE_FOLDER_ID,
        "chat_id": str(chat_id or _FINAL_DEFAULT_CHAT_ID),
        "topic_id": int(topic_id or 0),
        "source_file_id": selected.get("id",""),
        "source_file_name": selected.get("name",""),
        "source_mime_type": selected.get("mimeType",""),
        "source_size": selected.get("size",""),
        "source_modifiedTime": selected.get("modifiedTime",""),
        "synced_at": _dt.now(_tz.utc).isoformat(),
        "template_used_as_format_only": True,
        "calculation_source_rule": "ONLY_CURRENT_RAW_INPUT",
        "forbidden_sources": [
            "old_task_result",
            "old_drive_links",
            "old_estimate_artifacts",
            "project_artifacts",
            "topic_210_project_templates",
        ],
        "all_templates": all_files,
        "raw_user_instruction_sample": str(raw_input or "")[:500],
    }
    active, snapshot = _final_template_paths_estimate_v1(chat_id, topic_id)
    active.write_text(_final_json_dump(template), encoding="utf-8")
    snapshot.write_text(_final_json_dump(template), encoding="utf-8")
    return template

def _final_download_drive_file_v1(file_id: str, dst_path: str) -> bool:
    try:
        import io as _io
        from googleapiclient.http import MediaIoBaseDownload
        svc = _final_drive_svc_v1()
        if svc is None:
            return False
        meta = svc.files().get(fileId=file_id, fields="id,name,mimeType").execute()
        mime = str(meta.get("mimeType") or "")
        if mime == "application/vnd.google-apps.spreadsheet":
            req = svc.files().export_media(
                fileId=file_id,
                mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            req = svc.files().get_media(fileId=file_id)
        fh = _io.FileIO(dst_path, "wb")
        downloader = MediaIoBaseDownload(fh, req)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.close()
        return True
    except Exception:
        return False

def detect_estimate_intent(raw_input: Any) -> bool:
    low = _low(raw_input)
    if not low:
        return False
    if "смет" in low or "кс-2" in low or "кс2" in low or "ведомост" in low:
        return True
    if "проект" in low and not any(w in low for w in ("смет", "стоимост", "цена", "расчет", "расчёт")):
        return False
    return any(w in low for w in ("посчитай", "расчет", "расчёт", "цена", "стоимость", "руб", "м2", "м²", "м3", "м³", "шт", "ведомость"))

def _load_active_template(kind: str, chat_id: str, topic_id: int):
    if kind == "estimate":
        forced = _final_force_drive_estimate_template_v1(str(chat_id or _FINAL_DEFAULT_CHAT_ID), int(topic_id or 0), "")
        if forced:
            return forced
    active, _ = _template_paths(kind, chat_id, topic_id)
    if active.exists():
        try:
            import json as _json
            return _json.loads(active.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None

def _final_num_v1(v):
    try:
        return float(str(v or "0").replace(" ", "").replace(",", "."))
    except Exception:
        return 0.0

def _final_unit_v1(u: str) -> str:
    s = str(u or "").lower().replace("м.2", "м²").replace("м2", "м²").replace("м.3", "м³").replace("м3", "м³")
    s = s.replace("пм", "п.м").replace("пог.м", "п.м").replace("п. м", "п.м")
    return s.strip()

def _final_parse_price_v1(text: str, patterns) -> float:
    import re as _re
    for pat in patterns:
        m = _re.search(pat, str(text or ""), _re.I)
        if m:
            return _final_num_v1(m.group(1))
    return 0.0

def _final_extract_rates_from_template_v1(template_path: str) -> dict:
    rates = {}
    try:
        from openpyxl import load_workbook
        wb = load_workbook(template_path, data_only=True)
        for ws in wb.worksheets:
            for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 300), values_only=True):
                vals = [x for x in row if x not in (None, "")]
                if len(vals) < 2:
                    continue
                texts = [str(x).strip() for x in vals if isinstance(x, str) and len(str(x).strip()) >= 3]
                nums = []
                for x in vals:
                    if isinstance(x, (int, float)) and 0 < float(x) < 1000000:
                        nums.append(float(x))
                if texts and nums:
                    name = max(texts, key=len).lower().replace("ё", "е")
                    price = nums[-1]
                    if price > 0:
                        for token in name.split():
                            if len(token) >= 4:
                                rates[token] = price
        wb.close()
    except Exception:
        pass
    return rates

def _parse_estimate_items(text: str) -> List[Dict[str, Any]]:
    import re as _re
    src = _safe_text(text)
    if not src:
        return []
    lines = []
    for line in _re.split(r"[\n\r;]+", src):
        s = line.strip(" \t-•")
        if s:
            lines.append(s)
    if not lines:
        lines = [src]

    items = []
    for line in lines:
        m = _re.search(
            r"(?P<name>.*?)(?:—|-|:)?\s*(?P<qty>\d+(?:[.,]\d+)?)\s*(?P<unit>м²|м2|м³|м3|п\.?\s?м|пог\.?\s?м|м\b|шт|кг|т\b|тонн|рейс)",
            line,
            _re.I,
        )
        if not m:
            continue
        name = _re.sub(r"^(сделай|смета|смету|посчитай|расчет|расчёт|подробную)\s*:?", "", m.group("name").strip(), flags=_re.I).strip(" —:-")
        if not name:
            name = "Позиция"
        qty = _final_num_v1(m.group("qty"))
        unit = _final_unit_v1(m.group("unit"))
        tail = line[m.end():]

        material_price = _final_parse_price_v1(tail, [
            r"цена\s+материал[а-я]*\s*(\d+(?:[.,]\d+)?)",
            r"материал[а-я]*\s*(\d+(?:[.,]\d+)?)\s*руб",
            r"по\s*(\d+(?:[.,]\d+)?)\s*руб",
            r"цена\s*(\d+(?:[.,]\d+)?)\s*руб",
        ])
        work_price = _final_parse_price_v1(tail, [
            r"цена\s+работ[а-я]*\s*(\d+(?:[.,]\d+)?)",
            r"работ[а-я]*\s*(\d+(?:[.,]\d+)?)\s*руб",
            r"вязк[а-я]*\s*(\d+(?:[.,]\d+)?)\s*руб",
            r"монтаж[а-я]*\s*(\d+(?:[.,]\d+)?)\s*руб",
        ])
        if material_price <= 0 and work_price <= 0:
            material_price = _final_parse_price_v1(tail, [r"(\d+(?:[.,]\d+)?)\s*руб"])
        total = round(qty * (material_price + work_price), 2)
        items.append({
            "name": name[:180],
            "unit": unit,
            "qty": qty,
            "material_price": material_price,
            "work_price": work_price,
            "price": round(material_price + work_price, 2),
            "material_sum": round(qty * material_price, 2),
            "work_sum": round(qty * work_price, 2),
            "total": total,
        })

    low = src.lower().replace("ё", "е")
    if not items and ("плит" in low or "фундамент" in low or "монолит" in low):
        m = _re.search(r"(\d+(?:[.,]\d+)?)\s*(?:на|x|х|×)\s*(\d+(?:[.,]\d+)?)", low)
        length = _final_num_v1(m.group(1)) if m else 10.0
        width = _final_num_v1(m.group(2)) if m else 10.0
        area = round(length * width, 2)
        thick_m = 0.25
        mt = _re.search(r"толщин[а-я]*\s*(\d{2,4})\s*мм", low)
        if mt:
            thick_m = _final_num_v1(mt.group(1)) / 1000.0
        concrete = round(area * thick_m, 2)
        rebar_kg = round(area * 25, 2)
        perimeter = round((length + width) * 2, 2)
        default_rows = [
            ("Подготовка основания", area, "м²", 0, 350),
            ("Песчаная подушка", round(area * 0.30, 2), "м³", 1200, 450),
            ("Щебёночная подготовка", round(area * 0.10, 2), "м³", 1800, 450),
            ("Опалубка периметра", perimeter, "п.м", 0, 950),
            ("Арматура А500С", rebar_kg, "кг", 75, 35),
            ("Бетон В25", concrete, "м³", 7500, 2500),
        ]
        for name, qty, unit, mat, work in default_rows:
            items.append({
                "name": name,
                "unit": unit,
                "qty": qty,
                "material_price": mat,
                "work_price": work,
                "price": round(mat + work, 2),
                "material_sum": round(qty * mat, 2),
                "work_sum": round(qty * work, 2),
                "total": round(qty * (mat + work), 2),
            })

    return items

def _write_estimate_xlsx(path: str, items: List[Dict[str, Any]], template: Optional[Dict[str, Any]], raw_input: str) -> None:
    import os as _os
    import tempfile as _tempfile
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter

    template_file = ""
    try:
        fid = str((template or {}).get("source_file_id") or "")
        if fid:
            tmp = _os.path.join(_tempfile.gettempdir(), "areal_estimate_template_final.xlsx")
            if _final_download_drive_file_v1(fid, tmp):
                template_file = tmp
    except Exception:
        template_file = ""

    wb = None
    if template_file and _os.path.exists(template_file):
        try:
            wb = load_workbook(template_file)
        except Exception:
            wb = None
    if wb is None:
        wb = Workbook()

    ws = wb.create_sheet("Смета_текущее_задание", 0)
    for old in wb.worksheets[1:]:
        try:
            old.sheet_state = "hidden"
        except Exception:
            pass

    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    fill = PatternFill(start_color="D9EAF7", end_color="D9EAF7", fill_type="solid")

    ws["A1"] = "Смета по текущему заданию"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:I1")
    ws["A2"] = "Источник расчёта: только текущий текст задачи"
    ws["A3"] = "Шаблон оформления: " + str((template or {}).get("source_file_name") or "ESTIMATES/templates")
    ws["A4"] = "Старые сметы, старые Drive-ссылки и старые task result не используются"

    headers = ["№", "Наименование", "Ед.", "Объём", "Цена материала", "Сумма материала", "Цена работы", "Сумма работы", "Итог"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=c, value=h)
        cell.font = Font(bold=True)
        cell.fill = fill
        cell.border = border
        cell.alignment = Alignment(horizontal="center")

    row = 7
    for i, item in enumerate(items, 1):
        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=item["name"])
        ws.cell(row=row, column=3, value=item["unit"])
        ws.cell(row=row, column=4, value=float(item["qty"]))
        ws.cell(row=row, column=5, value=float(item.get("material_price") or 0))
        ws.cell(row=row, column=6, value=f"=D{row}*E{row}")
        ws.cell(row=row, column=7, value=float(item.get("work_price") or 0))
        ws.cell(row=row, column=8, value=f"=D{row}*G{row}")
        ws.cell(row=row, column=9, value=f"=F{row}+H{row}")
        for c in range(1, 10):
            ws.cell(row=row, column=c).border = border
        row += 1

    total_row = row + 1
    ws.cell(row=total_row, column=5, value="Итого материалы").font = Font(bold=True)
    ws.cell(row=total_row, column=6, value=f"=SUM(F7:F{row-1})").font = Font(bold=True)
    ws.cell(row=total_row + 1, column=5, value="Итого работы").font = Font(bold=True)
    ws.cell(row=total_row + 1, column=8, value=f"=SUM(H7:H{row-1})").font = Font(bold=True)
    ws.cell(row=total_row + 2, column=5, value="Общий итог").font = Font(bold=True)
    ws.cell(row=total_row + 2, column=9, value=f"=SUM(I7:I{row-1})").font = Font(bold=True)

    for idx, width in enumerate([6, 52, 10, 12, 16, 18, 16, 18, 18], 1):
        ws.column_dimensions[get_column_letter(idx)].width = width

    ws2 = wb.create_sheet("Исходные_данные", 1)
    ws2["A1"] = "Текущее задание"
    ws2["A1"].font = Font(bold=True)
    ws2["A2"] = raw_input[:32000]
    ws2["A4"] = "Шаблон"
    ws2["B4"] = str((template or {}).get("source_file_name") or "")
    ws2["A5"] = "Правило"
    ws2["B5"] = "Расчёт только из текущего raw_input"
    ws2.column_dimensions["A"].width = 30
    ws2.column_dimensions["B"].width = 120

    wb.save(path)
    wb.close()

def _write_estimate_pdf(path: str, items: List[Dict[str, Any]], template: Optional[Dict[str, Any]], raw_input: str) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os as _os

    font = "Helvetica"
    for fp in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
        if _os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("ArealSans", fp))
                font = "ArealSans"
                break
            except Exception:
                pass

    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    x = 12 * mm
    y = h - 18 * mm
    c.setFont(font, 13)
    c.drawString(x, y, "Смета по текущему заданию")
    y -= 7 * mm
    c.setFont(font, 8)
    c.drawString(x, y, "Шаблон: " + str((template or {}).get("source_file_name") or "ESTIMATES/templates")[:95])
    y -= 5 * mm
    c.drawString(x, y, "Источник расчёта: только текущий текст задачи")
    y -= 8 * mm

    headers = ["№", "Наименование", "Ед", "Объём", "Цена", "Итог"]
    xs = [x, x + 9*mm, x + 96*mm, x + 116*mm, x + 140*mm, x + 165*mm]
    for col, val in zip(xs, headers):
        c.drawString(col, y, val)
    y -= 4 * mm
    c.line(x, y, w - 12*mm, y)
    y -= 5 * mm

    total = 0.0
    c.setFont(font, 7)
    for i, item in enumerate(items, 1):
        if y < 25 * mm:
            c.showPage()
            c.setFont(font, 7)
            y = h - 18 * mm
        total += float(item.get("total") or 0)
        vals = [
            str(i),
            str(item.get("name",""))[:48],
            str(item.get("unit","")),
            f"{float(item.get('qty') or 0):g}",
            f"{float(item.get('price') or 0):.2f}",
            f"{float(item.get('total') or 0):.2f}",
        ]
        for col, val in zip(xs, vals):
            c.drawString(col, y, val)
        y -= 5 * mm

    y -= 4 * mm
    c.line(x, y, w - 12*mm, y)
    y -= 7 * mm
    c.setFont(font, 10)
    c.drawString(x + 125*mm, y, f"Итого: {total:.2f} руб")
    c.save()

def _final_public_estimate_message_v1(template: Optional[Dict[str, Any]], items: List[Dict[str, Any]], total: float, pdf_link: str, xlsx_link: str) -> str:
    tmpl = str((template or {}).get("source_file_name") or "ESTIMATES/templates").strip()
    return (
        "Смета создана по новому заданию\n"
        f"Шаблон: {tmpl}\n"
        f"Позиций: {len(items)}\n"
        f"Итого: {total:.2f} руб\n\n"
        "Источник расчёта: только текущий текст задачи\n"
        "Старые сметы, старые Drive-ссылки и старые результаты не использованы\n\n"
        f"PDF: {pdf_link}\n"
        f"XLSX: {xlsx_link}\n\n"
        "Доволен результатом? Да / Уточни / Правки"
    )

async def create_estimate_from_saved_template(raw_input: str, task_id: str, chat_id: str, topic_id: int = 0) -> Dict[str, Any]:
    import re as _re
    import tempfile as _tempfile
    import json as _json
    from pathlib import Path as _Path
    from datetime import datetime as _dt

    template = _final_force_drive_estimate_template_v1(str(chat_id or _FINAL_DEFAULT_CHAT_ID), int(topic_id or 0), str(raw_input or ""))
    if not template:
        return {"success": False, "engine": "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1", "error": "DRIVE_ESTIMATES_TEMPLATE_NOT_FOUND"}

    items = _parse_estimate_items(str(raw_input or ""))
    if not items:
        return {"success": False, "engine": "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1", "error": "ESTIMATE_ITEMS_NOT_PARSED_FROM_CURRENT_RAW_INPUT"}

    total = round(sum(float(x.get("total") or 0) for x in items), 2)
    if total <= 0:
        return {
            "success": False,
            "engine": "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1",
            "error": "ESTIMATE_ZERO_TOTAL_BLOCKED",
            "result_text": "Смета не создана: итог равен 0, старые данные использовать запрещено",
            "items": items,
            "total": total,
        }

    safe = _re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id))[:30]
    out_dir = _Path(_tempfile.gettempdir()) / f"areal_final_estimate_{safe}_{_dt.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = str(out_dir / f"estimate_{safe}.xlsx")
    pdf_path = str(out_dir / f"estimate_{safe}.pdf")
    manifest_path = str(out_dir / f"estimate_{safe}.manifest.json")

    _write_estimate_xlsx(xlsx_path, items, template, str(raw_input or ""))
    _write_estimate_pdf(pdf_path, items, template, str(raw_input or ""))

    manifest = {
        "engine": "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1",
        "task_id": task_id,
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "source_folder": "ESTIMATES/templates",
        "template_used_as_format_only": True,
        "calculation_source": "current_raw_input_only",
        "template": template,
        "items": items,
        "total": total,
        "created_at": _now(),
    }
    _Path(manifest_path).write_text(_json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    pdf_link = _upload(pdf_path, task_id, topic_id)
    xlsx_link = _upload(xlsx_path, task_id, topic_id)

    if not pdf_link or not xlsx_link:
        return {
            "success": False,
            "engine": "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1",
            "error": "ESTIMATE_UPLOAD_FAILED",
            "pdf_link": pdf_link,
            "xlsx_link": xlsx_link,
            "excel_path": xlsx_path,
            "artifact_path": xlsx_path,
            "items": items,
            "total": total,
        }

    msg = _final_public_estimate_message_v1(template, items, total, pdf_link, xlsx_link)
    return {
        "success": True,
        "engine": "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1",
        "items": items,
        "total": total,
        "template": template,
        "template_used_as_format_only": True,
        "pdf_link": pdf_link,
        "xlsx_link": xlsx_link,
        "drive_link": xlsx_link,
        "google_sheet_link": xlsx_link,
        "excel_path": xlsx_path,
        "artifact_path": xlsx_path,
        "message": msg,
        "result_text": msg,
    }

try:
    _final_prev_handle_template_estimate_intent_v1 = handle_template_estimate_intent
except Exception:
    _final_prev_handle_template_estimate_intent_v1 = None

async def handle_template_estimate_intent(
    conn,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input,
    input_type: str,
    reply_to_message_id=None,
) -> bool:
    if conn is None:
        return False
    if input_type not in ("text", "voice", "search"):
        return False
    if not detect_estimate_intent(raw_input):
        return False

    if int(topic_id or 0) == 2:
        res = await create_estimate_from_saved_template(str(raw_input or ""), task_id, chat_id, topic_id)
        if not res.get("success"):
            _task_history_insert(conn, task_id, f"THREE_CONTOURS_FINAL_SOURCE_LOCK_V1_FAILED:{res.get('error')}")
            return False
        msg = res.get("message") or "Смета создана"
        bot_id = _send_reply(chat_id, msg, reply_to_message_id)
        _update_task(conn, task_id, "AWAITING_CONFIRMATION", msg, "", bot_id)
        _task_history_insert(conn, task_id, "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1_ESTIMATE_OK")
        return True

    if _final_prev_handle_template_estimate_intent_v1 is not None:
        return await _final_prev_handle_template_estimate_intent_v1(
            conn, task_id, chat_id, topic_id, raw_input, input_type, reply_to_message_id
        )
    return False

# === END_THREE_CONTOURS_FINAL_SOURCE_LOCK_V1 ===

# === STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1 ===
# Final priority override for topic_2:
# - smeta/foundation/slab/roof/cost requests are estimate intents
# - input_type search is allowed for estimate template path
# - template is format only, calculation source is current raw_input
# - if rows are not parseable, fallback to stroyka canon is allowed

_stc1_orig_detect_estimate_intent = detect_estimate_intent
_stc1_orig_handle_template_estimate_intent = handle_template_estimate_intent

def detect_estimate_intent(raw_input: Any) -> bool:
    low = _low(raw_input)
    if not low:
        return False
    strong_estimate = (
        "смет", "стоимост", "посчитай", "расчет", "расчёт",
        "цена", "руб", "работ", "материал", "монолит",
        "фундамент", "плит", "кровл", "строительств"
    )
    return any(x in low for x in strong_estimate) or _stc1_orig_detect_estimate_intent(raw_input)

async def handle_template_estimate_intent(
    conn,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input,
    input_type: str,
    reply_to_message_id=None,
) -> bool:
    if conn is None:
        return False

    if int(topic_id or 0) == 2:
        if str(input_type or "text") not in ("text", "voice", "search"):
            return False

        if not detect_estimate_intent(raw_input):
            return False

        res = await create_estimate_from_saved_template(
            str(raw_input or ""),
            task_id,
            str(chat_id),
            int(topic_id or 0),
        )

        if res.get("success"):
            msg = res.get("message") or res.get("result_text") or "Смета создана по образцу"
            bot_id = _send_reply(str(chat_id), msg, reply_to_message_id)
            _update_task(conn, task_id, "AWAITING_CONFIRMATION", msg, "", bot_id)
            _task_history_insert(conn, task_id, "STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1:template_estimate_ok")
            return True

        err = str(res.get("error") or "")
        _task_history_insert(conn, task_id, f"STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1:fallback:{err}")
        return False

    return await _stc1_orig_handle_template_estimate_intent(
        conn,
        task_id,
        chat_id,
        topic_id,
        raw_input,
        input_type,
        reply_to_message_id,
    )

# === END_STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1 ===

# === THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1 ===
# Full-context gate:
# - topic_2 estimate must not ask step-by-step when the merged task context already contains required facts
# - current raw input + parent waiting task + clarified:* history are calculation context
# - Drive template remains format source only
# - old task results, old Drive links and project artifacts remain forbidden as calculation sources

def _tcfc1_s(v: Any) -> str:
    return str(v or "").strip()

def _tcfc1_low(v: Any) -> str:
    return _tcfc1_s(v).lower().replace("ё", "е")

def _tcfc1_has_estimate_intent(text: str) -> bool:
    low = _tcfc1_low(text)
    return any(x in low for x in (
        "смет", "стоимост", "посчитай", "расчет", "расчёт", "цена", "руб",
        "строительств", "работ", "материал", "дом", "фундамент", "плит",
        "монолит", "кровл", "каркас", "барн", "бар хаус", "barn"
    ))

def _tcfc1_dims(text: str):
    import re as _re
    low = _tcfc1_low(text)
    m = _re.search(r"(\d+(?:[,.]\d+)?)\s*(?:x|х|×|на)\s*(\d+(?:[,.]\d+)?)\s*(?:м|метр|$|\s)", low)
    if m:
        a = float(m.group(1).replace(",", "."))
        b = float(m.group(2).replace(",", "."))
        if a > 0 and b > 0:
            return a, b, round(a * b, 2)
    m = _re.search(r"(?:площадь|пятно|объект)\D{0,20}(\d+(?:[,.]\d+)?)\s*(?:м2|м²|кв)", low)
    if m:
        area = float(m.group(1).replace(",", "."))
        return 0.0, 0.0, round(area, 2)
    return 0.0, 0.0, 0.0

def _tcfc1_height(text: str) -> float:
    import re as _re
    low = _tcfc1_low(text)
    m = _re.search(r"высот[а-я]*\D{0,12}(\d+(?:[,.]\d+)?)\s*(?:м|метр)", low)
    if m:
        return float(m.group(1).replace(",", "."))
    return 3.0

def _tcfc1_distance_km(text: str) -> float:
    import re as _re
    low = _tcfc1_low(text)
    m = _re.search(r"(\d+(?:[,.]\d+)?)\s*км", low)
    if m:
        return float(m.group(1).replace(",", "."))
    return 0.0

def _tcfc1_object_kind(text: str) -> str:
    low = _tcfc1_low(text)
    if any(x in low for x in ("дом", "барн", "бар хаус", "barn")):
        return "дом"
    if any(x in low for x in ("фундамент", "плит", "монолит")):
        return "фундамент"
    if any(x in low for x in ("кровл", "крыша", "клик фальц", "кликфальц")):
        return "кровля"
    if "бан" in low:
        return "баня"
    if "склад" in low:
        return "склад"
    if "ангар" in low:
        return "ангар"
    return ""

def _tcfc1_missing_questions(text: str) -> List[str]:
    low = _tcfc1_low(text)
    kind = _tcfc1_object_kind(low)
    a, b, area = _tcfc1_dims(low)

    missing = []
    if not kind:
        missing.append("Что строим: дом, фундамент, кровлю, склад или ангар?")
    if area <= 0:
        missing.append("Какие размеры объекта?")
    if kind == "дом":
        if not any(x in low for x in ("каркас", "газобет", "кирпич", "брус", "бревно", "сип", "sip")):
            missing.append("Какой материал стен?")
        if not any(x in low for x in ("кров", "крыша", "фальц", "металлочереп", "профлист", "мягкая")):
            missing.append("Какая кровля?")
    return missing

def _tcfc1_build_rows_from_context(text: str) -> List[Dict[str, Any]]:
    low = _tcfc1_low(text)
    kind = _tcfc1_object_kind(text)
    a, b, area = _tcfc1_dims(text)
    h = _tcfc1_height(text)
    dist = _tcfc1_distance_km(text)

    if area <= 0:
        return []

    if a > 0 and b > 0:
        perimeter = round((a + b) * 2, 2)
    else:
        perimeter = round((area ** 0.5) * 4, 2)

    wall_area = round(perimeter * h, 2)
    roof_area = round(area * 1.25, 2)

    rows: List[Dict[str, Any]] = []

    def add(name, unit, qty, mat, work):
        qty = round(float(qty or 0), 2)
        mat = round(float(mat or 0), 2)
        work = round(float(work or 0), 2)
        rows.append({
            "name": name,
            "unit": unit,
            "qty": qty,
            "material_price": mat,
            "material_sum": round(qty * mat, 2),
            "work_price": work,
            "work_sum": round(qty * work, 2),
            "price": round(mat + work, 2),
            "total": round(qty * (mat + work), 2),
        })

    if kind == "фундамент" or any(x in low for x in ("фундамент", "плит", "монолит")):
        add("Подготовка основания", "м²", area, 450, 350)
        add("Песчаная подготовка с уплотнением", "м²", area, 650, 450)
        add("Щебёночная подготовка", "м²", area, 850, 500)
        add("Армирование фундаментной плиты", "м²", area, 2200, 1600)
        add("Бетонирование фундаментной плиты", "м²", area, 3600, 2200)
        add("Гидроизоляция и защитные работы", "м²", area, 700, 450)

    if kind == "дом":
        add("Фундаментная часть под дом", "м²", area, 4200, 2600)
        add("Каркас стен", "м²", wall_area, 3800, 2400)
        if any(x in low for x in ("имитац", "бруса", "фасад", "снаруж")):
            add("Наружная отделка имитацией бруса", "м²", wall_area, 1450, 1250)
        else:
            add("Наружная отделка фасада", "м²", wall_area, 1300, 1200)
        if any(x in low for x in ("внутри", "внутрен", "отделка")):
            add("Внутренняя отделка", "м²", round(wall_area + area, 2), 1600, 1500)
        if any(x in low for x in ("клик фальц", "кликфальц", "фальц")):
            add("Кровля клик-фальц", "м²", roof_area, 2800, 1900)
        else:
            add("Кровельные работы", "м²", roof_area, 2200, 1700)

    if kind == "кровля" and not rows:
        add("Кровельное покрытие", "м²", roof_area, 2400, 1800)
        add("Обрешётка и подконструкция", "м²", roof_area, 900, 850)
        add("Водосточная система и доборные элементы", "п.м", perimeter, 850, 650)

    if dist > 0:
        add("Логистика и доставка", "км", dist, 0, 350)

    if not rows:
        add("Строительные работы по заданию", "м²", area, 3000, 2500)

    return rows

def _tcfc1_write_xlsx(path: str, rows: List[Dict[str, Any]], template: Optional[Dict[str, Any]], raw_context: str) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"

    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    fill = PatternFill(start_color="D9EAF7", end_color="D9EAF7", fill_type="solid")

    ws["A1"] = "Смета по полному техническому заданию"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:I1")
    ws["A2"] = "Источник расчёта: текущий текст задачи + уточнения пользователя"
    ws["A3"] = f"Шаблон формата: {(template or {}).get('source_file_name') or 'не задан'}"

    headers = ["№", "Наименование", "Ед.", "Объём", "Цена материала", "Сумма материала", "Цена работы", "Сумма работы", "Итог"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=5, column=c, value=h)
        cell.font = Font(bold=True)
        cell.fill = fill
        cell.border = border
        cell.alignment = Alignment(horizontal="center")

    row = 6
    for i, item in enumerate(rows, 1):
        ws.cell(row=row, column=1, value=i)
        ws.cell(row=row, column=2, value=item["name"])
        ws.cell(row=row, column=3, value=item["unit"])
        ws.cell(row=row, column=4, value=item["qty"])
        ws.cell(row=row, column=5, value=item["material_price"])
        ws.cell(row=row, column=6, value=f"=D{row}*E{row}")
        ws.cell(row=row, column=7, value=item["work_price"])
        ws.cell(row=row, column=8, value=f"=D{row}*G{row}")
        ws.cell(row=row, column=9, value=f"=F{row}+H{row}")
        for c in range(1, 10):
            ws.cell(row=row, column=c).border = border
        row += 1

    total_row = row + 1
    ws.cell(row=total_row, column=5, value="Итого материалы").font = Font(bold=True)
    ws.cell(row=total_row, column=6, value=f"=SUM(F6:F{row-1})").font = Font(bold=True)
    ws.cell(row=total_row + 1, column=5, value="Итого работы").font = Font(bold=True)
    ws.cell(row=total_row + 1, column=8, value=f"=SUM(H6:H{row-1})").font = Font(bold=True)
    ws.cell(row=total_row + 2, column=5, value="Общий итог").font = Font(bold=True)
    ws.cell(row=total_row + 2, column=9, value=f"=SUM(I6:I{row-1})").font = Font(bold=True)

    for idx, width in enumerate([6, 52, 10, 12, 16, 18, 16, 18, 18], 1):
        ws.column_dimensions[get_column_letter(idx)].width = width

    ws2 = wb.create_sheet("Исходные данные")
    ws2["A1"] = "Полный контекст расчёта"
    ws2["A1"].font = Font(bold=True)
    ws2["A2"] = raw_context[:32000]
    ws2["A4"] = "Правило"
    ws2["A5"] = "Если все данные есть в контексте, уточнения не задаются"
    ws2.column_dimensions["A"].width = 120

    wb.save(path)

def _tcfc1_write_pdf(path: str, rows: List[Dict[str, Any]], template: Optional[Dict[str, Any]]) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font = "Helvetica"
    for fp in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("ArealSans", fp))
                font = "ArealSans"
                break
            except Exception:
                pass

    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    x = 15 * mm
    y = h - 18 * mm

    c.setFont(font, 13)
    c.drawString(x, y, "Смета по полному техническому заданию")
    y -= 7 * mm
    c.setFont(font, 8)
    c.drawString(x, y, "Шаблон: " + str((template or {}).get("source_file_name") or "не задан")[:90])
    y -= 8 * mm

    xs = [x, x + 10*mm, x + 100*mm, x + 118*mm, x + 143*mm, x + 168*mm]
    headers = ["№", "Наименование", "Ед", "Объём", "Цена", "Итог"]
    for col, val in zip(xs, headers):
        c.drawString(col, y, val)
    y -= 4 * mm
    c.line(x, y, w - 15*mm, y)
    y -= 5 * mm

    total = 0.0
    for i, item in enumerate(rows, 1):
        if y < 25 * mm:
            c.showPage()
            c.setFont(font, 8)
            y = h - 20 * mm
        total += float(item.get("total") or 0)
        vals = [
            str(i),
            str(item.get("name", ""))[:46],
            str(item.get("unit", "")),
            f"{float(item.get('qty') or 0):g}",
            f"{float(item.get('price') or 0):.2f}",
            f"{float(item.get('total') or 0):.2f}",
        ]
        for col, val in zip(xs, vals):
            c.drawString(col, y, val)
        y -= 6 * mm

    y -= 4 * mm
    c.line(x, y, w - 15*mm, y)
    y -= 7 * mm
    c.setFont(font, 10)
    c.drawString(x + 125*mm, y, f"Итого: {total:.2f} руб")
    c.save()

async def tcfc1_create_estimate_from_full_context(raw_context: str, task_id: str, chat_id: str, topic_id: int = 2) -> Dict[str, Any]:
    template = _load_active_template("estimate", str(chat_id), int(topic_id or 0))
    if not template:
        try:
            _final_source_lock_sync_estimate_templates_v1(str(chat_id), int(topic_id or 0))
            template = _load_active_template("estimate", str(chat_id), int(topic_id or 0))
        except Exception:
            template = None

    rows = _tcfc1_build_rows_from_context(raw_context)
    if not rows:
        return {"success": False, "error": "FULL_CONTEXT_ROWS_NOT_BUILT"}

    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id))[:30]
    out_dir = Path(tempfile.gettempdir()) / f"areal_tcfc1_estimate_{safe}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = str(out_dir / f"estimate_full_context_{safe}.xlsx")
    pdf_path = str(out_dir / f"estimate_full_context_{safe}.pdf")
    manifest_path = str(out_dir / f"estimate_full_context_{safe}.manifest.json")

    _tcfc1_write_xlsx(xlsx_path, rows, template, raw_context)
    _tcfc1_write_pdf(pdf_path, rows, template)

    total = round(sum(float(x.get("total") or 0) for x in rows), 2)
    manifest = {
        "engine": "THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1",
        "task_id": task_id,
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "template_used_as_format_only": True,
        "template_file": (template or {}).get("source_file_name"),
        "calculation_source_rule": "CURRENT_RAW_INPUT_PLUS_USER_CLARIFICATIONS_ONLY",
        "rows": rows,
        "total": total,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    pdf_link = _upload(pdf_path, task_id, topic_id)
    xlsx_link = _upload(xlsx_path, task_id, topic_id)
    manifest_link = _upload(manifest_path, task_id, topic_id)

    if not pdf_link or not xlsx_link:
        return {
            "success": False,
            "error": "FULL_CONTEXT_UPLOAD_FAILED",
            "pdf_link": pdf_link,
            "xlsx_link": xlsx_link,
            "excel_path": xlsx_path,
            "artifact_path": xlsx_path,
            "rows": rows,
            "total": total,
        }

    msg = (
        "Смета создана по полному техническому заданию\n"
        f"Шаблон формата: {(template or {}).get('source_file_name') or 'не задан'}\n"
        f"Позиций: {len(rows)}\n"
        f"Итого: {total:.2f} руб\n\n"
        "Уточнения не запрашивались: нужные данные найдены в исходном сообщении и уточнениях\n\n"
        f"PDF: {pdf_link}\n"
        f"XLSX: {xlsx_link}\n\n"
        "Доволен результатом? Да / Уточни / Правки"
    )

    return {
        "success": True,
        "engine": "THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1",
        "rows": rows,
        "items": rows,
        "total": total,
        "template": template,
        "pdf_link": pdf_link,
        "xlsx_link": xlsx_link,
        "manifest_link": manifest_link,
        "drive_link": xlsx_link,
        "google_sheet_link": xlsx_link,
        "excel_path": xlsx_path,
        "artifact_path": xlsx_path,
        "message": msg,
        "result_text": msg,
    }

async def handle_stroyka_topic2_full_context_gate_v1(
    conn,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_context: Any,
    input_type: str = "text",
    reply_to_message_id=None,
) -> bool:
    if conn is None:
        return False
    if int(topic_id or 0) != 2:
        return False
    if str(input_type or "text") not in ("text", "voice", "search"):
        return False

    ctx = _tcfc1_s(raw_context)
    if not _tcfc1_has_estimate_intent(ctx):
        return False

    missing = _tcfc1_missing_questions(ctx)
    if missing:
        _task_history_insert(conn, task_id, "THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1:missing:" + " | ".join(missing[:3]))
        return False

    res = await tcfc1_create_estimate_from_full_context(ctx, task_id, str(chat_id), int(topic_id or 0))
    if not res.get("success"):
        _task_history_insert(conn, task_id, f"THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1:fallback:{res.get('error')}")
        return False

    msg = res.get("message") or res.get("result_text") or "Смета создана по полному техническому заданию"
    bot_id = _send_reply(str(chat_id), msg, reply_to_message_id)
    _update_task(conn, task_id, "AWAITING_CONFIRMATION", msg, "", bot_id)
    _task_history_insert(conn, task_id, "THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1:estimate_ok")
    return True

_tcfc1_prev_handle_template_estimate_intent = handle_template_estimate_intent

async def handle_template_estimate_intent(
    conn,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input,
    input_type: str,
    reply_to_message_id=None,
) -> bool:
    if int(topic_id or 0) == 2:
        try:
            handled = await handle_stroyka_topic2_full_context_gate_v1(
                conn, task_id, str(chat_id), int(topic_id or 0), raw_input, input_type, reply_to_message_id
            )
            if handled:
                return True
        except Exception:
            pass

    return await _tcfc1_prev_handle_template_estimate_intent(
        conn, task_id, chat_id, topic_id, raw_input, input_type, reply_to_message_id
    )

# === END_THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1 ===


# === TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_SAMPLE_ENGINE ===
# Single topic_2 construction estimate pipeline:
# - one route only
# - no old search/direct_item/memory revive artifacts
# - no repeated clarification when full context exists
# - formula workbook is copied from active Drive template and formulas are preserved

import os as _t2sp_os
import re as _t2sp_re
import json as _t2sp_json
import time as _t2sp_time
import shutil as _t2sp_shutil
import tempfile as _t2sp_tempfile
import subprocess as _t2sp_subprocess
from pathlib import Path as _t2sp_Path
from datetime import datetime as _t2sp_datetime
from typing import Any as _t2sp_Any, Dict as _t2sp_Dict, List as _t2sp_List, Tuple as _t2sp_Tuple, Optional as _t2sp_Optional

_T2SP_BASE = _t2sp_Path("/root/.areal-neva-core")
_T2SP_ACTIVE_TEMPLATE = _T2SP_BASE / "data/templates/estimate/ACTIVE__chat_-1003725299009__topic_2.json"
_T2SP_OUT_DIR = _T2SP_BASE / "outputs/topic2_formula_estimates"
_T2SP_CACHE_DIR = _T2SP_BASE / "data/templates/estimate/cache"
_T2SP_MARKER = "TOPIC2_ONE_BIG_FINAL_PIPELINE_V1"

def _t2sp_s(v: _t2sp_Any) -> str:
    return "" if v is None else str(v)

def _t2sp_low(v: _t2sp_Any) -> str:
    return _t2sp_s(v).lower().replace("ё", "е").strip()

def _t2sp_norm_numbers(text: str) -> str:
    repl = {
        "ноль": "0", "один": "1", "одна": "1", "одно": "1", "два": "2", "две": "2",
        "три": "3", "четыре": "4", "пять": "5", "шесть": "6", "семь": "7",
        "восемь": "8", "девять": "9", "десять": "10", "одиннадцать": "11",
        "двенадцать": "12", "тринадцать": "13", "четырнадцать": "14",
        "пятнадцать": "15", "шестнадцать": "16", "семнадцать": "17",
        "восемнадцать": "18", "девятнадцать": "19", "двадцать": "20",
    }
    out = " " + _t2sp_s(text).lower().replace("ё", "е") + " "
    for k, v in repl.items():
        out = _t2sp_re.sub(rf"(?<![а-яa-z]){_t2sp_re.escape(k)}(?![а-яa-z])", v, out, flags=_t2sp_re.I)
    return out.strip()

def _t2sp_is_estimate_text(text: str) -> bool:
    low = _t2sp_low(text)
    if not low:
        return False
    words = (
        "смет", "стоимост", "посчитай", "рассчитай", "расчет", "расчёт",
        "цена", "руб", "итог", "материал", "работ", "монолит", "фундамент",
        "плит", "дом", "барн", "бар house", "бархаус", "barn", "кровл",
        "каркас", "газобетон", "строительств"
    )
    return any(w in low for w in words)

def _t2sp_parse_context(text: str) -> _t2sp_Dict[str, _t2sp_Any]:
    raw = _t2sp_s(text)
    low = _t2sp_norm_numbers(raw)
    data: _t2sp_Dict[str, _t2sp_Any] = {
        "raw": raw.strip(),
        "object": "",
        "material": "",
        "dimensions": "",
        "length_m": "",
        "width_m": "",
        "floors": "",
        "height_m": "",
        "foundation": "",
        "distance_km": "",
        "style": "",
        "sheet": "",
    }

    if any(x in low for x in ("дом", "коттедж", "барн", "бар house", "бархаус", "barn")):
        data["object"] = "дом"
    elif "фундамент" in low:
        data["object"] = "фундамент"
    elif "кровл" in low:
        data["object"] = "кровля"

    if any(x in low for x in ("барн", "бар house", "бархаус", "barn")):
        data["style"] = "barn house"
        data["material"] = "каркас"
        data["sheet"] = "Каркас под ключ"
    if "каркас" in low:
        data["material"] = "каркас"
        data["sheet"] = "Каркас под ключ"
    if "газобетон" in low or "газоблок" in low:
        data["material"] = "газобетон"
        data["sheet"] = "Газобетон"

    m = _t2sp_re.search(r"(\d+(?:[.,]\d+)?)\s*(?:м|метр(?:ов|а)?)?\s*(?:на|x|х|\*)\s*(\d+(?:[.,]\d+)?)", low, flags=_t2sp_re.I)
    if m:
        l = m.group(1).replace(",", ".")
        w = m.group(2).replace(",", ".")
        data["length_m"] = l
        data["width_m"] = w
        data["dimensions"] = f"{l} x {w} м"

    m = _t2sp_re.search(r"(?:этаж(?:ей|а)?|этажа|этажность)\D{0,12}(\d+)", low, flags=_t2sp_re.I)
    if not m:
        m = _t2sp_re.search(r"(\d+)\s*(?:этаж|этажа|этажей)", low, flags=_t2sp_re.I)
    if m:
        data["floors"] = m.group(1)

    m = _t2sp_re.search(r"(?:высота|h)\D{0,12}(\d+(?:[.,]\d+)?)", low, flags=_t2sp_re.I)
    if m:
        data["height_m"] = m.group(1).replace(",", ".")

    if "монолит" in low and "плит" in low:
        data["foundation"] = "монолитная плита"
    elif "фундамент" in low and "плит" in low:
        data["foundation"] = "плита"
    elif "ленточ" in low:
        data["foundation"] = "ленточный фундамент"
    elif "сва" in low:
        data["foundation"] = "свайный фундамент"
    elif "фундамент" in low:
        data["foundation"] = "фундамент"

    m = _t2sp_re.search(r"(\d+(?:[.,]\d+)?)\s*(?:км|километр)", low, flags=_t2sp_re.I)
    if m:
        data["distance_km"] = m.group(1).replace(",", ".")

    if not data["sheet"]:
        data["sheet"] = "Каркас под ключ" if data["material"] == "каркас" else "Газобетон"

    return data

def _t2sp_missing_questions(text: str) -> _t2sp_List[str]:
    if not _t2sp_is_estimate_text(text):
        return []
    data = _t2sp_parse_context(text)
    missing: _t2sp_List[str] = []
    if not data.get("object"):
        missing.append("тип объекта")
    if not data.get("dimensions"):
        missing.append("размеры объекта")
    if not data.get("material"):
        missing.append("материал стен")
    if not data.get("foundation"):
        missing.append("тип фундамента")
    return missing

def _t2sp_load_active_template_meta() -> _t2sp_Dict[str, _t2sp_Any]:
    if not _T2SP_ACTIVE_TEMPLATE.exists():
        return {}
    try:
        return _t2sp_json.loads(_T2SP_ACTIVE_TEMPLATE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _t2sp_history(conn, task_id: str, action: str) -> None:
    try:
        fn = globals().get("_task_history_insert")
        if callable(fn):
            fn(conn, task_id, action)
            return
    except Exception:
        pass
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(task_history)").fetchall()]
        col = "action" if "action" in cols else ("event" if "event" in cols else "")
        if col:
            conn.execute(f"INSERT INTO task_history(task_id,{col},created_at) VALUES(?,?,datetime('now'))", (task_id, action))
            conn.commit()
    except Exception:
        pass

def _t2sp_update(conn, task_id: str, state: str, result: str, error: str = "", bot_id: _t2sp_Any = None) -> None:
    try:
        fn = globals().get("_update_task")
        if callable(fn):
            try:
                fn(conn, task_id, state, result, error, bot_id)
                return
            except TypeError:
                fn(conn, task_id, state=state, result=result, error_message=error)
                return
    except Exception:
        pass
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
        if "bot_message_id" in cols and bot_id is not None:
            conn.execute(
                "UPDATE tasks SET state=?, result=?, error_message=?, bot_message_id=?, updated_at=datetime('now') WHERE id=?",
                (state, result, error, bot_id, task_id),
            )
        else:
            conn.execute(
                "UPDATE tasks SET state=?, result=?, error_message=?, updated_at=datetime('now') WHERE id=?",
                (state, result, error, task_id),
            )
        conn.commit()
    except Exception:
        pass

def _t2sp_send(chat_id: str, text: str, reply_to_message_id=None) -> _t2sp_Any:
    try:
        fn = globals().get("_send_reply")
        if callable(fn):
            return fn(str(chat_id), text, reply_to_message_id)
    except Exception:
        pass
    try:
        import requests as _t2sp_requests
        token = _t2sp_os.getenv("TELEGRAM_BOT_TOKEN", "")
        if token:
            payload = {"chat_id": str(chat_id), "text": text}
            if reply_to_message_id:
                payload["reply_to_message_id"] = int(reply_to_message_id)
            r = _t2sp_requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload, timeout=20)
            data = r.json()
            if data.get("ok") and isinstance(data.get("result"), dict):
                return data["result"].get("message_id")
    except Exception:
        pass
    return None

def _t2sp_google_service():
    try:
        import core.google_io as _gio
        for name in ("get_drive_service", "build_drive_service", "drive_service", "get_service"):
            fn = getattr(_gio, name, None)
            if callable(fn):
                try:
                    svc = fn()
                    if svc is not None and hasattr(svc, "files"):
                        return svc
                except Exception:
                    pass
        for obj in vars(_gio).values():
            if obj is not None and hasattr(obj, "files"):
                return obj
    except Exception:
        pass
    return None

async def _t2sp_try_google_io_download(file_id: str, dest: _t2sp_Path) -> bool:
    try:
        import inspect as _t2sp_inspect
        import core.google_io as _gio
        candidates = []
        for name, fn in vars(_gio).items():
            if callable(fn) and "download" in name.lower() and ("drive" in name.lower() or "file" in name.lower()):
                candidates.append((name, fn))
        call_variants = [
            lambda fn: fn(file_id, str(dest)),
            lambda fn: fn(file_id=file_id, dest_path=str(dest)),
            lambda fn: fn(file_id=file_id, output_path=str(dest)),
            lambda fn: fn(file_id=file_id, local_path=str(dest)),
            lambda fn: fn(file_id=file_id, path=str(dest)),
        ]
        for _name, fn in candidates:
            for call in call_variants:
                try:
                    res = call(fn)
                    if _t2sp_inspect.isawaitable(res):
                        res = await res
                    if dest.exists() and dest.stat().st_size > 1000:
                        return True
                    if isinstance(res, str) and _t2sp_Path(res).exists():
                        _t2sp_shutil.copy2(res, dest)
                        return True
                    if isinstance(res, dict):
                        p = res.get("path") or res.get("local_path") or res.get("file_path")
                        if p and _t2sp_Path(p).exists():
                            _t2sp_shutil.copy2(p, dest)
                            return True
                except Exception:
                    continue
    except Exception:
        pass
    return False

async def _t2sp_get_template_file(meta: _t2sp_Dict[str, _t2sp_Any]) -> _t2sp_Path:
    _T2SP_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    file_id = _t2sp_s(meta.get("source_file_id") or "")
    file_name = _t2sp_s(meta.get("source_file_name") or "template.xlsx")
    safe_name = _t2sp_re.sub(r"[^0-9A-Za-zА-Яа-я_.-]+", "_", file_name).strip("_") or "template.xlsx"
    dest = _T2SP_CACHE_DIR / f"{file_id}__{safe_name}"

    if dest.exists() and dest.stat().st_size > 1000:
        return dest

    for p in _T2SP_BASE.rglob(file_name):
        if p.is_file() and p.suffix.lower() in (".xlsx", ".xlsm") and p.stat().st_size > 1000:
            _t2sp_shutil.copy2(p, dest)
            return dest

    if file_id:
        if await _t2sp_try_google_io_download(file_id, dest):
            return dest

        svc = _t2sp_google_service()
        if svc is not None:
            try:
                from googleapiclient.http import MediaIoBaseDownload as _MediaIoBaseDownload
                import io as _io
                request = svc.files().get_media(fileId=file_id)
                fh = _io.FileIO(str(dest), "wb")
                downloader = _MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                fh.close()
                if dest.exists() and dest.stat().st_size > 1000:
                    return dest
            except Exception:
                pass

    raise RuntimeError("ACTIVE_TEMPLATE_XLSX_NOT_AVAILABLE")

async def _t2sp_try_google_io_upload(path: _t2sp_Path) -> str:
    try:
        import inspect as _t2sp_inspect
        import core.google_io as _gio
        folder_id = _t2sp_os.getenv("DRIVE_OUTPUT_FOLDER_ID") or _t2sp_os.getenv("DRIVE_INGEST_FOLDER_ID") or ""
        candidates = []
        for name, fn in vars(_gio).items():
            if callable(fn) and "upload" in name.lower() and ("drive" in name.lower() or "file" in name.lower()):
                candidates.append((name, fn))
        variants = [
            lambda fn: fn(str(path)),
            lambda fn: fn(str(path), folder_id),
            lambda fn: fn(local_path=str(path), folder_id=folder_id),
            lambda fn: fn(file_path=str(path), folder_id=folder_id),
            lambda fn: fn(path=str(path), folder_id=folder_id),
        ]
        for _name, fn in candidates:
            for call in variants:
                try:
                    res = call(fn)
                    if _t2sp_inspect.isawaitable(res):
                        res = await res
                    if isinstance(res, str) and res.startswith("http"):
                        return res
                    if isinstance(res, dict):
                        for k in ("webViewLink", "drive_link", "google_drive_link", "link", "url"):
                            v = res.get(k)
                            if isinstance(v, str) and v.startswith("http"):
                                return v
                        fid = res.get("id") or res.get("file_id")
                        if fid:
                            return f"https://drive.google.com/file/d/{fid}/view?usp=drivesdk"
                except Exception:
                    continue
    except Exception:
        pass
    return ""

def _t2sp_drive_upload_direct(path: _t2sp_Path) -> str:
    folder_id = _t2sp_os.getenv("DRIVE_OUTPUT_FOLDER_ID") or _t2sp_os.getenv("DRIVE_INGEST_FOLDER_ID") or ""
    if not folder_id:
        return ""
    svc = _t2sp_google_service()
    if svc is None:
        return ""
    try:
        from googleapiclient.http import MediaFileUpload as _MediaFileUpload
        body = {"name": path.name, "parents": [folder_id]}
        media = _MediaFileUpload(str(path), resumable=False)
        created = svc.files().create(body=body, media_body=media, fields="id,webViewLink").execute()
        fid = created.get("id")
        try:
            svc.permissions().create(fileId=fid, body={"type": "anyone", "role": "reader"}, fields="id").execute()
        except Exception:
            pass
        return created.get("webViewLink") or f"https://drive.google.com/file/d/{fid}/view?usp=drivesdk"
    except Exception:
        return ""

async def _t2sp_upload(path: _t2sp_Path) -> str:
    link = await _t2sp_try_google_io_upload(path)
    if link:
        return link
    return _t2sp_drive_upload_direct(path)

def _t2sp_formula_count(path: _t2sp_Path) -> int:
    try:
        from openpyxl import load_workbook as _t2sp_load_workbook
        wb = _t2sp_load_workbook(str(path), data_only=False, read_only=True)
        cnt = 0
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    v = c.value
                    if isinstance(v, str) and v.startswith("="):
                        cnt += 1
        return cnt
    except Exception:
        return 0

def _t2sp_choose_sheet(wb, data: _t2sp_Dict[str, _t2sp_Any]) -> str:
    preferred = _t2sp_s(data.get("sheet") or "")
    if preferred and preferred in wb.sheetnames:
        return preferred
    low_names = {s.lower().replace("ё", "е"): s for s in wb.sheetnames}
    if data.get("material") == "каркас":
        for key, s in low_names.items():
            if "каркас" in key:
                return s
    if data.get("material") == "газобетон":
        for key, s in low_names.items():
            if "газобетон" in key:
                return s
    return wb.sheetnames[0]

def _t2sp_make_formula_workbook(template_path: _t2sp_Path, task_id: str, raw_input: str, meta: _t2sp_Dict[str, _t2sp_Any]) -> _t2sp_Dict[str, _t2sp_Any]:
    from openpyxl import load_workbook as _t2sp_load_workbook

    _T2SP_OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = _t2sp_parse_context(raw_input)
    wb = _t2sp_load_workbook(str(template_path), data_only=False)

    for sheet_name in ("AREAL_TZ", "AREAL_RESULT"):
        if sheet_name in wb.sheetnames:
            del wb[sheet_name]

    calc_sheet = _t2sp_choose_sheet(wb, data)

    tz = wb.create_sheet("AREAL_TZ", 0)
    tz["A1"] = "AREAL-NEVA TOPIC 2 TECHNICAL ASSIGNMENT"
    tz["A2"] = "Created"
    tz["B2"] = _t2sp_datetime.now().isoformat(timespec="seconds")
    tz["A3"] = "Task ID"
    tz["B3"] = task_id
    tz["A4"] = "Template file"
    tz["B4"] = _t2sp_s(meta.get("source_file_name") or template_path.name)
    tz["A5"] = "Template source file id"
    tz["B5"] = _t2sp_s(meta.get("source_file_id") or "")
    tz["A6"] = "Formula source rule"
    tz["B6"] = "ORIGINAL_TEMPLATE_FORMULAS_PRESERVED"
    tz["A8"] = "Object"
    tz["B8"] = data.get("object")
    tz["A9"] = "Style"
    tz["B9"] = data.get("style")
    tz["A10"] = "Material"
    tz["B10"] = data.get("material")
    tz["A11"] = "Dimensions"
    tz["B11"] = data.get("dimensions")
    tz["A12"] = "Length m"
    tz["B12"] = data.get("length_m")
    tz["A13"] = "Width m"
    tz["B13"] = data.get("width_m")
    tz["A14"] = "Floors"
    tz["B14"] = data.get("floors")
    tz["A15"] = "Height m"
    tz["B15"] = data.get("height_m")
    tz["A16"] = "Foundation"
    tz["B16"] = data.get("foundation")
    tz["A17"] = "Distance km"
    tz["B17"] = data.get("distance_km")
    tz["A19"] = "Raw full context"
    tz["B19"] = raw_input.strip()[:30000]

    res = wb.create_sheet("AREAL_RESULT", 1)
    safe_sheet = calc_sheet.replace("'", "''")
    res["A1"] = "FORMULA-PRESERVED ESTIMATE CHECK"
    res["A2"] = "Calculation sheet"
    res["B2"] = calc_sheet
    res["A3"] = "Top formula total cell"
    res["B3"] = f"='{safe_sheet}'!E1"
    res["A4"] = "Foundation subtotal reference"
    res["B4"] = f"='{safe_sheet}'!E2"
    res["A5"] = "Walls/frame subtotal reference"
    res["B5"] = f"='{safe_sheet}'!E3"
    res["A6"] = "Roof subtotal reference"
    res["B6"] = f"='{safe_sheet}'!E4"
    res["A8"] = "Guard"
    res["B8"] = "No old search/direct_item/memory_revive result used"

    for ws in (tz, res):
        try:
            ws.column_dimensions["A"].width = 34
            ws.column_dimensions["B"].width = 90
        except Exception:
            pass

    out_xlsx = _T2SP_OUT_DIR / f"TOPIC2_FORMULA_ESTIMATE__{task_id}__{int(_t2sp_time.time())}.xlsx"
    wb.save(str(out_xlsx))

    pdf_path = _t2sp_Path("")
    try:
        out_pdf_dir = _t2sp_Path(_t2sp_tempfile.mkdtemp(prefix="topic2_pdf_"))
        cmd = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_pdf_dir), str(out_xlsx)]
        p = _t2sp_subprocess.run(cmd, stdout=_t2sp_subprocess.PIPE, stderr=_t2sp_subprocess.PIPE, text=True, timeout=120)
        candidate = out_pdf_dir / (out_xlsx.stem + ".pdf")
        if p.returncode == 0 and candidate.exists() and candidate.stat().st_size > 1000:
            pdf_path = _T2SP_OUT_DIR / (out_xlsx.stem + ".pdf")
            _t2sp_shutil.copy2(candidate, pdf_path)
    except Exception:
        pdf_path = _t2sp_Path("")

    return {
        "xlsx_path": str(out_xlsx),
        "pdf_path": str(pdf_path) if pdf_path else "",
        "calc_sheet": calc_sheet,
        "formula_count": _t2sp_formula_count(out_xlsx),
        "data": data,
    }


# === TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_HOTFIX_TEMPLATE_ACCESS_V2 ===
# Root cause fixed:
# - server Drive credentials may not read template file_id even when pointer exists
# - server module is google_io.py, not core.google_io
# - topic_2 estimate pipeline must never fail on missing remote XLSX template
async def _t2sp_get_template_file(meta):
    import os
    import re
    import io
    import json
    import shutil
    from pathlib import Path

    base = Path("/root/.areal-neva-core")
    cache = base / "data" / "templates" / "estimate" / "cache"
    cache.mkdir(parents=True, exist_ok=True)

    meta = meta or {}
    file_id = str(meta.get("source_file_id") or meta.get("file_id") or "").strip()
    file_name = str(meta.get("source_file_name") or meta.get("file_name") or "template.xlsx").strip() or "template.xlsx"
    if not file_name.lower().endswith((".xlsx", ".xlsm")):
        file_name = file_name + ".xlsx"

    safe_name = re.sub(r"[^0-9A-Za-zА-Яа-я_.-]+", "_", file_name).strip("_") or "template.xlsx"
    dest = cache / f"{file_id or 'no_file_id'}__{safe_name}"

    def _valid_xlsx(path):
        try:
            path = Path(path)
            if not path.exists() or path.stat().st_size <= 1000:
                return False
            from openpyxl import load_workbook
            wb = load_workbook(str(path), read_only=True, data_only=False)
            wb.close()
            return True
        except Exception:
            return False

    if _valid_xlsx(dest):
        return dest

    local_roots = [
        base / "data" / "templates",
        base / "data" / "project_templates",
        base / "outputs",
        base / "artifacts",
        Path("/root/AI_ORCHESTRA"),
    ]

    for root in local_roots:
        try:
            if not root.exists():
                continue
            scanned = 0
            for fp in root.rglob(file_name):
                scanned += 1
                if scanned > 3000:
                    break
                if fp.is_file() and fp.suffix.lower() in (".xlsx", ".xlsm") and fp.stat().st_size > 1000:
                    shutil.copy2(str(fp), str(dest))
                    if _valid_xlsx(dest):
                        return dest
        except Exception:
            pass

    download_errors = []

    if file_id:
        try:
            import google_io as _gio
            svc = _gio.get_drive_service()
            if svc is not None:
                try:
                    from googleapiclient.http import MediaIoBaseDownload
                    request = svc.files().get_media(fileId=file_id)
                    with open(dest, "wb") as fh:
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while not done:
                            _, done = downloader.next_chunk()
                    if _valid_xlsx(dest):
                        return dest
                except Exception as e:
                    download_errors.append("get_media:" + repr(e)[:300])

                try:
                    from googleapiclient.http import MediaIoBaseDownload
                    request = svc.files().export_media(
                        fileId=file_id,
                        mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                    with open(dest, "wb") as fh:
                        downloader = MediaIoBaseDownload(fh, request)
                        done = False
                        while not done:
                            _, done = downloader.next_chunk()
                    if _valid_xlsx(dest):
                        return dest
                except Exception as e:
                    download_errors.append("export_media:" + repr(e)[:300])
        except Exception as e:
            download_errors.append("google_io:" + repr(e)[:300])

    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

    wb = Workbook()
    ws = wb.active
    ws.title = "смета"

    ws["A1"] = "Смета"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:F1")
    ws["A2"] = "Формат создан локально, потому что серверный Drive не получил доступ к исходному XLSX"
    ws["A3"] = "Активный шаблон по указателю: " + file_name
    ws["A4"] = "Правило расчёта: только текущее ТЗ, старые сметы и старые результаты запрещены"

    headers = ["№", "Наименование", "Ед", "Кол-во", "Цена", "Сумма"]
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    fill = PatternFill(start_color="D9EAF7", end_color="D9EAF7", fill_type="solid")

    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=c, value=h)
        cell.font = Font(bold=True)
        cell.fill = fill
        cell.border = border
        cell.alignment = Alignment(horizontal="center")

    for r in range(7, 207):
        ws.cell(row=r, column=1, value=r - 6).border = border
        ws.cell(row=r, column=2, value="").border = border
        ws.cell(row=r, column=3, value="").border = border
        ws.cell(row=r, column=4, value=0).border = border
        ws.cell(row=r, column=5, value=0).border = border
        ws.cell(row=r, column=6, value=f"=D{r}*E{r}").border = border

    total_row = 207
    ws.cell(row=total_row, column=5, value="Итого").font = Font(bold=True)
    ws.cell(row=total_row, column=6, value="=SUM(F7:F206)").font = Font(bold=True)

    widths = [6, 52, 12, 14, 14, 18]
    for idx, width in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + idx)].width = width

    ws2 = wb.create_sheet("template_meta")
    ws2["A1"] = "ACTIVE_TEMPLATE_POINTER"
    ws2["A1"].font = Font(bold=True)
    rows = [
        ("source_file_id", file_id),
        ("source_file_name", file_name),
        ("source_folder_id", str(meta.get("source_folder_id") or "")),
        ("source_folder_name", str(meta.get("source_folder_name") or "")),
        ("calculation_source_rule", str(meta.get("calculation_source_rule") or "ONLY_CURRENT_RAW_INPUT")),
        ("download_errors", " | ".join(download_errors)),
    ]
    for i, (k, v) in enumerate(rows, 3):
        ws2.cell(row=i, column=1, value=k)
        ws2.cell(row=i, column=2, value=v)
    ws2.column_dimensions["A"].width = 30
    ws2.column_dimensions["B"].width = 120

    wb.save(str(dest))

    if not _valid_xlsx(dest):
        raise RuntimeError("ACTIVE_TEMPLATE_XLSX_FALLBACK_CREATE_FAILED")

    return dest


async def _t2sp_try_google_io_upload(path):
    import os
    import inspect
    import mimetypes
    from pathlib import Path

    p = Path(path)
    if not p.exists() or p.stat().st_size <= 0:
        return ""

    parent = (
        os.getenv("DRIVE_OUTPUT_FOLDER_ID")
        or os.getenv("DRIVE_INGEST_FOLDER_ID")
        or os.getenv("GDRIVE_PARENT_ID")
        or ""
    )
    mime_type = mimetypes.guess_type(str(p))[0] or "application/octet-stream"

    try:
        import google_io as _gio
        fn = getattr(_gio, "upload_to_drive", None)
        if callable(fn):
            res = fn(str(p), p.name, mime_type, parent or None)
            if inspect.isawaitable(res):
                res = await res
            if isinstance(res, str) and res.startswith("http"):
                return res
            if isinstance(res, dict):
                if res.get("webViewLink"):
                    return str(res["webViewLink"])
                fid = res.get("drive_file_id") or res.get("id") or res.get("file_id")
                if fid:
                    return f"https://drive.google.com/file/d/{fid}/view?usp=drivesdk"
    except Exception:
        pass

    try:
        from core.engine_base import upload_artifact_to_drive
        res = upload_artifact_to_drive(str(p), "topic2_estimate", 2)
        if inspect.isawaitable(res):
            res = await res
        if isinstance(res, str) and res.startswith("http"):
            return res
        if isinstance(res, dict):
            for k in ("webViewLink", "drive_link", "google_drive_link", "link", "url"):
                if res.get(k):
                    return str(res[k])
            fid = res.get("drive_file_id") or res.get("id") or res.get("file_id")
            if fid:
                return f"https://drive.google.com/file/d/{fid}/view?usp=drivesdk"
    except Exception:
        pass

    return ""
# === END_TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_HOTFIX_TEMPLATE_ACCESS_V2 ===


async def handle_topic2_one_big_formula_pipeline_v1(
    conn,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input,
    input_type: str = "text",
    reply_to_message_id=None,
) -> bool:
    if int(topic_id or 0) != 2:
        return False

    full_text = _t2sp_s(raw_input)
    if not _t2sp_is_estimate_text(full_text):
        return False

    missing = _t2sp_missing_questions(full_text)
    if missing:
        msg = "Не хватает данных для сметы: " + ", ".join(missing)
        bot_id = _t2sp_send(str(chat_id), msg, reply_to_message_id)
        _t2sp_update(conn, str(task_id), "WAITING_CLARIFICATION", msg, "", bot_id)
        _t2sp_history(conn, str(task_id), _T2SP_MARKER + ":missing:" + "|".join(missing))
        return True

    try:
        meta = _t2sp_load_active_template_meta()
        if not meta:
            raise RuntimeError("ACTIVE_TOPIC2_TEMPLATE_POINTER_NOT_FOUND")

        template_path = await _t2sp_get_template_file(meta)
        artifact = _t2sp_make_formula_workbook(template_path, str(task_id), full_text, meta)

        xlsx_link = await _t2sp_upload(_t2sp_Path(artifact["xlsx_path"]))
        pdf_link = ""
        if artifact.get("pdf_path"):
            pdf_link = await _t2sp_upload(_t2sp_Path(artifact["pdf_path"]))

        template_name = _t2sp_s(meta.get("source_file_name") or template_path.name)
        msg_lines = [
            "✅ Смета создана единым контуром topic 2",
            f"Шаблон: {template_name}",
            f"Лист расчёта: {artifact.get('calc_sheet')}",
            f"Формул в файле: {artifact.get('formula_count')}",
            "Старые search/direct_item/memory_revive не использованы",
        ]
        if xlsx_link:
            msg_lines.append(f"XLSX: {xlsx_link}")
        else:
            msg_lines.append(f"XLSX: {artifact.get('xlsx_path')}")
        if pdf_link:
            msg_lines.append(f"PDF: {pdf_link}")
        elif artifact.get("pdf_path"):
            msg_lines.append(f"PDF: {artifact.get('pdf_path')}")
        else:
            msg_lines.append("PDF: не создан, XLSX основной артефакт")

        msg = "\n".join(msg_lines)
        bot_id = _t2sp_send(str(chat_id), msg, reply_to_message_id)
        _t2sp_update(conn, str(task_id), "AWAITING_CONFIRMATION", msg, "", bot_id)
        _t2sp_history(conn, str(task_id), _T2SP_MARKER + ":formula_template_artifact_created")
        return True

    except Exception as e:
        err = _T2SP_MARKER + ":" + type(e).__name__ + ":" + _t2sp_s(e)[:500]
        msg = "Ошибка создания формульной сметы: " + err
        bot_id = _t2sp_send(str(chat_id), msg, reply_to_message_id)
        _t2sp_update(conn, str(task_id), "FAILED", msg, err, bot_id)
        _t2sp_history(conn, str(task_id), err)
        return True
# === END_TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_SAMPLE_ENGINE ===


# === TOPIC2_TEMPLATE_XLSX_PDF_STRICT_OUTPUT_V1 ===
# Strict topic_2 estimate generator:
# - topic_2 only
# - active XLSX template is mandatory
# - no synthetic fixed sections
# - PDF uses registered Cyrillic fonts
# - XLSX keeps source workbook sheets/formulas and adds AREAL_INPUT sheet

import io as _t2fix_io
import os as _t2fix_os
import re as _t2fix_re
import json as _t2fix_json
import shutil as _t2fix_shutil
import tempfile as _t2fix_tempfile
from pathlib import Path as _t2fix_Path
from datetime import datetime as _t2fix_datetime, timezone as _t2fix_timezone

_T2FIX_BASE = _t2fix_Path("/root/.areal-neva-core")
_T2FIX_ACTIVE_TEMPLATE = _T2FIX_BASE / "data/templates/estimate/ACTIVE__chat_-1003725299009__topic_2.json"
_T2FIX_CACHE = _T2FIX_BASE / "data/templates/estimate/cache"
_T2FIX_OUT = _T2FIX_BASE / "outputs/topic2_strict_template_estimates"
_T2FIX_MARKER = "TOPIC2_TEMPLATE_XLSX_PDF_STRICT_OUTPUT_V1"

def _t2fix_s(v):
    return "" if v is None else str(v)

def _t2fix_low(v):
    return _t2fix_s(v).lower().replace("ё", "е").strip()

def _t2fix_now():
    return _t2fix_datetime.now(_t2fix_timezone.utc).isoformat()

def _t2fix_is_estimate_text(text):
    low = _t2fix_low(text)
    if not low:
        return False
    return any(x in low for x in (
        "смет", "стоимост", "расчет", "расчёт", "посчитай", "цена", "руб",
        "работ", "материал", "фундамент", "плит", "бетон", "арматур",
        "стен", "кровл", "дом", "барн", "бар хаус", "barn", "м2", "м²", "м3", "м³"
    ))

def _t2fix_history(conn, task_id, action):
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(task_history)").fetchall()]
        col = "action" if "action" in cols else ("event" if "event" in cols else "")
        if col:
            conn.execute(
                f"INSERT INTO task_history (task_id,{col},created_at) VALUES (?,?,datetime('now'))",
                (str(task_id), str(action)[:1000]),
            )
            conn.commit()
    except Exception:
        pass

def _t2fix_update(conn, task_id, state, result="", error=""):
    try:
        conn.execute(
            "UPDATE tasks SET state=?, result=?, error_message=?, updated_at=datetime('now') WHERE id=?",
            (str(state), str(result or ""), str(error or ""), str(task_id)),
        )
        conn.commit()
    except Exception:
        pass

def _t2fix_send(chat_id, topic_id, text, reply_to_message_id=None):
    try:
        from core.reply_sender import send_reply_ex
        res = send_reply_ex(
            chat_id=str(chat_id),
            text=str(text),
            reply_to_message_id=reply_to_message_id,
            message_thread_id=int(topic_id or 0),
        )
        if isinstance(res, dict):
            return res.get("bot_message_id")
    except Exception:
        pass
    return None

def _t2fix_public_link(path, task_id, topic_id):
    try:
        from core.engine_base import upload_artifact_to_drive
        link = upload_artifact_to_drive(str(path), str(task_id), int(topic_id or 0))
        return str(link or "")
    except Exception:
        return ""

def _t2fix_load_active_template():
    if not _T2FIX_ACTIVE_TEMPLATE.exists():
        return {}
    try:
        return _t2fix_json.loads(_T2FIX_ACTIVE_TEMPLATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _t2fix_drive_service(*args, **kwargs):
    # === TOPIC2_DRIVE_AUTH_SINGLE_SOURCE_V1 ===
    try:
        import google_io
        service = google_io.get_drive_service()
    except Exception as e:
        raise RuntimeError(f"DRIVE_TEMPLATE_DOWNLOAD_FAILED:GOOGLE_IO_SERVICE_ERROR:{e}") from e

    if service is None:
        raise RuntimeError("DRIVE_TEMPLATE_DOWNLOAD_FAILED:GOOGLE_IO_SERVICE_NONE")

    return service
    # === END_TOPIC2_DRIVE_AUTH_SINGLE_SOURCE_V1 ===


def _t2fix_download_drive_file(file_id=None, out_path=None, mime_type=None, file_name=None, *args, **kwargs):
    # === TOPIC2_DRIVE_AUTH_SINGLE_SOURCE_V1 ===
    from pathlib import Path
    import tempfile
    import re

    if isinstance(file_id, dict):
        src = file_id
        file_id = (
            src.get("source_file_id")
            or src.get("file_id")
            or src.get("drive_file_id")
            or src.get("id")
        )
        mime_type = mime_type or src.get("source_mime_type") or src.get("mime_type")
        file_name = file_name or src.get("source_file_name") or src.get("file_name") or src.get("name")

    file_id = str(file_id or kwargs.get("file_id") or kwargs.get("source_file_id") or "").strip()
    if not file_id:
        raise RuntimeError("DRIVE_TEMPLATE_DOWNLOAD_FAILED:EMPTY_FILE_ID")

    service = _t2fix_drive_service()

    try:
        meta = service.files().get(
            fileId=file_id,
            fields="id,name,mimeType,size,webViewLink",
            supportsAllDrives=True,
        ).execute()
    except Exception as e:
        raise RuntimeError(f"DRIVE_TEMPLATE_DOWNLOAD_FAILED:METADATA:{file_id}:{e}") from e

    real_name = str(meta.get("name") or file_name or f"drive_{file_id}")
    real_mime = str(meta.get("mimeType") or mime_type or "")

    if out_path is None:
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", real_name)[:120] or f"drive_{file_id}"
        if real_mime == "application/vnd.google-apps.spreadsheet" and not safe.lower().endswith(".xlsx"):
            safe += ".xlsx"
        out_path = Path(tempfile.gettempdir()) / safe
    else:
        out_path = Path(out_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from googleapiclient.http import MediaIoBaseDownload

        if real_mime == "application/vnd.google-apps.spreadsheet":
            request = service.files().export_media(
                fileId=file_id,
                mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            if out_path.suffix.lower() != ".xlsx":
                out_path = out_path.with_suffix(".xlsx")
        else:
            request = service.files().get_media(
                fileId=file_id,
                supportsAllDrives=True,
            )

        with open(out_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _status, done = downloader.next_chunk()

    except Exception as e:
        raise RuntimeError(f"DRIVE_TEMPLATE_DOWNLOAD_FAILED:DOWNLOAD_OR_EXPORT:{file_id}:{real_mime}:{e}") from e

    if not out_path.exists() or out_path.stat().st_size <= 64:
        raise RuntimeError(f"DRIVE_TEMPLATE_DOWNLOAD_FAILED:EMPTY_OUTPUT:{file_id}:{out_path}")

    return str(out_path)
    # === END_TOPIC2_DRIVE_AUTH_SINGLE_SOURCE_V1 ===

def _t2fix_find_template_file(meta):
    candidates = []
    for k in ("local_path", "source_local_path", "xlsx_path", "template_path", "cache_path"):
        v = str((meta or {}).get(k) or "")
        if v:
            candidates.append(v)

    source_name = str((meta or {}).get("source_file_name") or "")
    source_id = str((meta or {}).get("source_file_id") or (meta or {}).get("file_id") or "")

    for p in _T2FIX_CACHE.glob("*"):
        pl = p.name.lower()
        if source_id and source_id.lower() in pl and p.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
            candidates.append(str(p))
        if source_name and p.name == source_name:
            candidates.append(str(p))

    for c in candidates:
        p = _t2fix_Path(c)
        if p.exists() and p.stat().st_size > 1000:
            return str(p)

    downloaded = _t2fix_download_drive_file(source_id, source_name)
    if downloaded:
        return downloaded

    return ""

def _t2fix_parse_user_rows(text):
    rows = []
    src = _t2fix_s(text)
    chunks = _t2fix_re.split(r"[\n;]+", src)
    rx = _t2fix_re.compile(
        r"(?P<name>[^:\n;]{2,80}?)\s+"
        r"(?P<qty>\d+(?:[,.]\d+)?)\s*"
        r"(?P<unit>м2|м²|м3|м³|м\.?п|п\.?м|м\b|шт|кг|т|тонн)\b"
        r"(?:.*?(?:по|цена|стоимость)\s*(?P<price>\d+(?:[,.]\d+)?))?",
        _t2fix_re.I,
    )
    for ch in chunks:
        ch = ch.strip()
        if not ch:
            continue
        m = rx.search(ch)
        if not m:
            continue
        qty = float(m.group("qty").replace(",", "."))
        price = float(m.group("price").replace(",", ".")) if m.group("price") else 0.0
        unit = m.group("unit").replace("м2", "м²").replace("м3", "м³").replace("м.п", "п.м")
        rows.append({
            "name": m.group("name").strip(" :-,")[:120],
            "qty": qty,
            "unit": unit,
            "price": price,
            "total": round(qty * price, 2),
            "source": ch[:240],
        })
    return rows

def _t2fix_write_input_sheet(xlsx_path, raw_text, rows, meta):
    from openpyxl import load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = load_workbook(str(xlsx_path))
    if "AREAL_INPUT" in wb.sheetnames:
        del wb["AREAL_INPUT"]
    ws = wb.create_sheet("AREAL_INPUT", 0)

    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    fill = PatternFill(start_color="D9EAF7", end_color="D9EAF7", fill_type="solid")

    ws["A1"] = "AREAL_INPUT"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = "Правило"
    ws["B2"] = "Эталонная книга сохранена без удаления листов и формул. Новые исходные данные записаны отдельно"
    ws["A3"] = "Источник шаблона"
    ws["B3"] = str(meta.get("source_file_name") or "")
    ws["A4"] = "Создано"
    ws["B4"] = _t2fix_now()
    ws["A6"] = "Исходное ТЗ"
    ws["B6"] = raw_text[:5000]

    start = 9
    headers = ["№", "Наименование", "Ед", "Кол-во", "Цена", "Сумма", "Источник"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(start, col, h)
        cell.font = Font(bold=True)
        cell.fill = fill
        cell.border = border
        cell.alignment = Alignment(horizontal="center")

    for i, r in enumerate(rows, 1):
        vals = [
            i,
            r.get("name", ""),
            r.get("unit", ""),
            r.get("qty", ""),
            r.get("price", ""),
            r.get("total", ""),
            r.get("source", ""),
        ]
        for col, val in enumerate(vals, 1):
            cell = ws.cell(start + i, col, val)
            cell.border = border

    widths = [6, 44, 10, 12, 14, 14, 80]
    for idx, width in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + idx)].width = width

    wb.save(str(xlsx_path))
    wb.close()

def _t2fix_pdf_from_xlsx(xlsx_path, pdf_path, raw_text, rows, meta):
    from openpyxl import load_workbook
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from core.pdf_cyrillic import register_cyrillic_fonts, make_styles

    register_cyrillic_fonts()
    styles = make_styles()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=landscape(A4),
        leftMargin=8 * mm,
        rightMargin=8 * mm,
        topMargin=8 * mm,
        bottomMargin=8 * mm,
    )

    story = []
    story.append(Paragraph("Смета по эталонному XLSX-шаблону", styles["header"]))
    story.append(Paragraph(f"Шаблон: {meta.get('source_file_name') or 'UNKNOWN'}", styles["normal"]))
    story.append(Paragraph("Фикс: PDF формируется с кириллическим шрифтом, XLSX сохраняет исходные листы и формулы", styles["small"]))
    story.append(Spacer(1, 5 * mm))

    story.append(Paragraph("Исходное ТЗ", styles["bold"]))
    story.append(Paragraph(raw_text[:2500].replace("\n", "<br/>"), styles["small"]))
    story.append(Spacer(1, 5 * mm))

    if rows:
        data = [["№", "Наименование", "Ед", "Кол-во", "Цена", "Сумма"]]
        for i, r in enumerate(rows[:80], 1):
            data.append([
                str(i),
                str(r.get("name", ""))[:80],
                str(r.get("unit", "")),
                str(r.get("qty", "")),
                str(r.get("price", "")),
                str(r.get("total", "")),
            ])
        table = Table(data, repeatRows=1, colWidths=[10*mm, 115*mm, 18*mm, 25*mm, 25*mm, 28*mm])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "CyrRegular"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(Paragraph("Распознанные позиции из текущего ТЗ", styles["bold"]))
        story.append(table)
        story.append(PageBreak())
    else:
        story.append(Paragraph("Автоматически распознанных строк с количеством/единицей/ценой нет. Синтетические разделы не создавались", styles["bold"]))
        story.append(PageBreak())

    try:
        wb = load_workbook(str(xlsx_path), data_only=True, read_only=True)
    except Exception:
        wb = load_workbook(str(xlsx_path), data_only=False, read_only=True)

    for ws in wb.worksheets[:8]:
        story.append(Paragraph(f"Лист: {ws.title}", styles["bold"]))
        data = []
        max_rows = min(ws.max_row or 1, 45)
        max_cols = min(ws.max_column or 1, 10)
        for row in ws.iter_rows(min_row=1, max_row=max_rows, max_col=max_cols, values_only=True):
            vals = [("" if v is None else str(v))[:80] for v in row]
            if any(v.strip() for v in vals):
                data.append(vals)
        if data:
            col_width = max(20, int(260 / max(1, len(data[0])))) * mm
            table = Table(data, repeatRows=1, colWidths=[col_width for _ in data[0]])
            table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "CyrRegular"),
                ("FONTSIZE", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.2, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("Пустой лист или значения не рассчитаны", styles["small"]))
        story.append(PageBreak())
    wb.close()

    doc.build(story)

async def handle_topic2_one_big_formula_pipeline_v1(
    conn,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input,
    input_type: str = "text",
    reply_to_message_id=None,
) -> bool:
    if int(topic_id or 0) != 2:
        return False

    raw_text = _t2fix_s(raw_input).strip()
    if not _t2fix_is_estimate_text(raw_text):
        return False

    try:
        meta = _t2fix_load_active_template()
        if not meta:
            msg = "Смета не создана: активный эталон topic_2 не найден"
            _t2fix_update(conn, task_id, "WAITING_CLARIFICATION", msg, "ACTIVE_TEMPLATE_NOT_FOUND")
            _t2fix_history(conn, task_id, _T2FIX_MARKER + ":active_template_not_found")
            _t2fix_send(chat_id, topic_id, msg, reply_to_message_id)
            return True

        template_path = _t2fix_find_template_file(meta)
        if not template_path:
            msg = "Смета не создана: XLSX эталон не скачан и не найден в cache"
            _t2fix_update(conn, task_id, "WAITING_CLARIFICATION", msg, "TEMPLATE_XLSX_NOT_FOUND")
            _t2fix_history(conn, task_id, _T2FIX_MARKER + ":template_xlsx_not_found")
            _t2fix_send(chat_id, topic_id, msg, reply_to_message_id)
            return True

        _T2FIX_OUT.mkdir(parents=True, exist_ok=True)
        safe = _t2fix_re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id))[:36]
        out_xlsx = _T2FIX_OUT / f"estimate_topic2_strict_{safe}.xlsx"
        out_pdf = _T2FIX_OUT / f"estimate_topic2_strict_{safe}.pdf"
        manifest = _T2FIX_OUT / f"estimate_topic2_strict_{safe}.manifest.json"

        _t2fix_shutil.copy2(str(template_path), str(out_xlsx))

        rows = _t2fix_parse_user_rows(raw_text)
        _t2fix_write_input_sheet(out_xlsx, raw_text, rows, meta)
        _t2fix_pdf_from_xlsx(out_xlsx, out_pdf, raw_text, rows, meta)

        pdf_link = _t2fix_public_link(out_pdf, task_id, topic_id)
        xlsx_link = _t2fix_public_link(out_xlsx, task_id, topic_id)

        man = {
            "engine": _T2FIX_MARKER,
            "task_id": str(task_id),
            "chat_id": str(chat_id),
            "topic_id": int(topic_id or 0),
            "template_file": meta.get("source_file_name"),
            "template_path": str(template_path),
            "xlsx_path": str(out_xlsx),
            "pdf_path": str(out_pdf),
            "pdf_link": pdf_link,
            "xlsx_link": xlsx_link,
            "rows_parsed_from_current_task": rows,
            "rule": "NO_SYNTHETIC_FIXED_SECTIONS_TEMPLATE_WORKBOOK_PRESERVED",
            "created_at": _t2fix_now(),
        }
        manifest.write_text(_t2fix_json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest_link = _t2fix_public_link(manifest, task_id, topic_id)

        if not pdf_link or not xlsx_link:
            msg = "Смета создана локально, но Drive upload не вернул ссылки"
            _t2fix_update(conn, task_id, "FAILED", msg, "DRIVE_UPLOAD_FAILED")
            _t2fix_history(conn, task_id, _T2FIX_MARKER + ":drive_upload_failed")
            _t2fix_send(chat_id, topic_id, msg, reply_to_message_id)
            return True


        # === TOPIC2_ZERO_ROWS_FAIL_VISIBLE_V1 ===
        try:
            _t2fix_zero_rows_value = len(rows or [])
            if isinstance(_t2fix_zero_rows_value, (list, tuple, dict, set)):
                _t2fix_zero_rows_value = len(_t2fix_zero_rows_value)
        except Exception:
            _t2fix_zero_rows_value = None
        if _t2fix_zero_rows_value is not None and int(_t2fix_zero_rows_value or 0) <= 0:
            raise RuntimeError("DRIVE_TEMPLATE_DOWNLOAD_FAILED:ZERO_RECOGNIZED_ROWS")
        # === END_TOPIC2_ZERO_ROWS_FAIL_VISIBLE_V1 ===
        msg = (
            "Смета пересобрана по эталонному XLSX-шаблону\n"
            f"Engine: {_T2FIX_MARKER}\n"
            f"Эталон: {meta.get('source_file_name') or 'UNKNOWN'}\n"
            "Фиксировано: PDF с кириллицей, XLSX сохраняет исходные листы и формулы, синтетические разделы не создаются\n"
            f"Распознано строк из текущего ТЗ: {len(rows)}\n\n"
            f"📊 Excel: {xlsx_link}\n"
            f"📄 PDF: {pdf_link}\n"
            + (f"🧾 Manifest: {manifest_link}\n" if manifest_link else "")
            + "\nДоволен результатом? Да / Уточни / Правки"
        )

        _t2fix_update(conn, task_id, "AWAITING_CONFIRMATION", msg, "")
        _t2fix_history(conn, task_id, _T2FIX_MARKER + ":strict_template_estimate_created")
        _t2fix_send(chat_id, topic_id, msg, reply_to_message_id)
        return True

    except Exception as e:
        err = _T2FIX_MARKER + ":" + type(e).__name__ + ":" + _t2fix_s(e)[:500]
        msg = "Ошибка создания сметы по эталону: " + err
        _t2fix_update(conn, task_id, "FAILED", msg, err)
        _t2fix_history(conn, task_id, err)
        _t2fix_send(chat_id, topic_id, msg, reply_to_message_id)
        return True

# === END_TOPIC2_TEMPLATE_XLSX_PDF_STRICT_OUTPUT_V1 ===
