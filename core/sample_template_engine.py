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

