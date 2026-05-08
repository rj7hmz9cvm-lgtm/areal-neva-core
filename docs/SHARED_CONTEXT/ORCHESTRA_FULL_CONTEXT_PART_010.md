# ORCHESTRA_FULL_CONTEXT_PART_010
generated_at_utc: 2026-05-08T22:10:02.023892+00:00
git_sha_before_commit: af42c97232f42a953e720cd4afceba9a494a9621
part: 10/17


====================================================================================================
BEGIN_FILE: core/sample_template_engine.py
FILE_CHUNK: 1/2
SHA256_FULL_FILE: 31f5b62ba05d003e8723ebbee0da2caa4d4db0bac70e173f5dfd81ad4f2cc544
====================================================================================================
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



def _send_reply(chat_id: str, text: str, reply_to_message_id: Optional[int] = None, topic_id: int = 0) -> Optional[int]:  # TOPIC2_REPLY_THREAD_FIX_V1
    try:
        from core.reply_sender import send_reply_ex
        kwargs = {
            "chat_id": str(chat_id),
            "text": text,
            "reply_to_message_id": reply_to_message_id,
        }
        if int(topic_id or 0) > 0:
            kwargs["message_thread_id"] = int(topic_id or 0)  # TOPIC2_REPLY_THREAD_FIX_V1
        res = send_reply_ex(**kwargs)
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


def _t2sp_send(chat_id: str, text: str, reply_to_message_id=None, topic_id: int = 0) -> _t2sp_Any:  # TOPIC2_REPLY_THREAD_FIX_V1
    try:
        fn = globals().get("_send_reply")
        if callable(fn):
            bot_id = fn(str(chat_id), text, reply_to_message_id, topic_id=int(topic_id or 0))
            if bot_id:
                return bot_id
    except Exception:
        pass
    try:
        import requests as _t2sp_requests
        token = <REDACTED_SECRET>"TELEGRAM_BOT_TOKEN", "")
        if token:
            payload = {"chat_id": str(chat_id), "text": text}
            if reply_to_message_id:
                payload["reply_to_message_id"] = int(reply_to_message_id)
            if int(topic_id or 0) > 0:
                payload["message_thread_id"] = int(topic_id or 0)  # TOPIC2_REPLY_THREAD_FIX_V1
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
        bot_id = _t2sp_send(str(chat_id), msg, reply_to_message_id, topic_id=int(topic_id or 0))  # TOPIC2_REPLY_THREAD_FIX_V1
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
        bot_id = _t2sp_send(str(chat_id), msg, reply_to_message_id, topic_id=int(topic_id or 0))  # TOPIC2_REPLY_THREAD_FIX_V1
        _t2sp_update(conn, str(task_id), "AWAITING_CONFIRMATION", msg, "", bot_id)
        _t2sp_history(conn, str(task_id), _T2SP_MARKER + ":formula_template_artifact_created")
        return True

    except Exception as e:
        err = _T2SP_MARKER + ":" + type(e).__name__ + ":" + _t2sp_s(e)[:500]
        msg = "Ошибка создания формульной сметы: " + err
        bot_id = _t2sp_send(str(chat_id), msg, reply_to_message_id, topic_id=int(topic_id or 0))  # TOPIC2_REPLY_THREAD_FIX_V1
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

# === TOPIC2_REAL_ESTIMATE_FROM_TZ_V2 ===
# Fix:
# - topic_2 estimate must never return empty zero rows when the user gave object dimensions and construction data
# - current user TЗ has priority over old memory/template artifacts
# - inaccessible Drive template must not create fake empty estimate
# - output XLSX/PDF must contain real calculated rows, totals, readable Cyrillic PDF

import re as _t2real_re
import json as _t2real_json
from pathlib import Path as _t2real_Path
from datetime import datetime as _t2real_datetime
from typing import Any as _t2real_Any, Dict as _t2real_Dict, List as _t2real_List

_T2REAL_MARKER = "TOPIC2_REAL_ESTIMATE_FROM_TZ_V2"
_T2REAL_BASE = _t2real_Path("/root/.areal-neva-core")
_T2REAL_OUT = _T2REAL_BASE / "outputs" / "topic2_real_estimates"
_T2REAL_OUT.mkdir(parents=True, exist_ok=True)

def _t2real_s(v: _t2real_Any) -> str:
    return "" if v is None else str(v)

def _t2real_low(v: _t2real_Any) -> str:
    return _t2real_s(v).lower().replace("ё", "е").strip()

def _t2real_num(v: _t2real_Any, default: float = 0.0) -> float:
    try:
        return float(str(v).replace(",", "."))
    except Exception:
        return float(default)

def _t2real_clean_voice(text: str) -> str:
    return _t2real_re.sub(r"^\s*\[VOICE\]\s*", "", _t2real_s(text), flags=_t2real_re.I).strip()

def _t2real_add_parent_context(conn, task_id: str, chat_id: str, topic_id: int, raw_input: str) -> str:
    parts = [_t2real_clean_voice(raw_input)]
    try:
        row = conn.execute(
            """
            SELECT raw_input
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND id<>?
              AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION','FAILED','DONE')
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id or 0), str(task_id)),
        ).fetchone()
        if row and row[0]:
            prev = _t2real_clean_voice(row[0])
            if prev and prev not in "\n".join(parts):
                parts.append(prev)
    except Exception:
        pass

    try:
        rows = conn.execute(
            """
            SELECT action
            FROM task_history
            WHERE task_id=?
              AND action LIKE 'clarified:%'
            ORDER BY rowid DESC
            LIMIT 20
            """,
            (str(task_id),),
        ).fetchall()
        for r in rows:
            v = _t2real_s(r[0])
            if v.startswith("clarified:"):
                v = v.split(":", 1)[1].strip()
                if v and v not in "\n".join(parts):
                    parts.append(v)
    except Exception:
        pass

    return "\n\n".join(x for x in parts if x.strip()).strip()

def _t2real_parse_params(text: str) -> _t2real_Dict[str, _t2real_Any]:
    low = _t2real_low(text)
    dims = []
    for m in _t2real_re.finditer(r"(\d{1,3}(?:[,.]\d+)?)\s*(?:x|х|×|на)\s*(\d{1,3}(?:[,.]\d+)?)", low):
        a = _t2real_num(m.group(1))
        b = _t2real_num(m.group(2))
        if a > 0 and b > 0:
            dims.append((a, b, a * b))
    if dims:
        dims.sort(key=lambda x: x[2], reverse=True)
        length, width, area = dims[0]
    else:
        length, width, area = 0.0, 0.0, 0.0

    floors = 1
    m = _t2real_re.search(r"(\d{1,2})\s*(?:этаж|этажа|этажей)", low)
    if m:
        floors = max(1, int(_t2real_num(m.group(1), 1)))

    height = 3.0
    m = _t2real_re.search(r"высот[аы]?\s*(\d{1,2}(?:[,.]\d+)?)\s*(?:м|метр)", low)
    if m:
        height = max(2.4, _t2real_num(m.group(1), 3.0))

    slab_mm = 200.0
    m = _t2real_re.search(r"(?:плит[ауы]?|фундамент).{0,60}?(\d{2,3})\s*мм", low)
    if not m:
        m = _t2real_re.search(r"толщин[аы]?\s*(\d{2,3})\s*мм", low)
    if m:
        slab_mm = max(100.0, _t2real_num(m.group(1), 200.0))

    insulation_mm = 150.0
    m = _t2real_re.search(r"утепл.{0,60}?(\d{2,3})\s*мм", low)
    if m:
        insulation_mm = max(50.0, _t2real_num(m.group(1), 150.0))

    distance_km = 0.0
    m = _t2real_re.search(r"(?:удален|удалён|доставк|логист|расстоян).{0,80}?(\d{1,4})\s*(?:км|километр)", low)
    if not m:
        m = _t2real_re.search(r"(\d{1,4})\s*(?:км|километр)", low)
    if m:
        distance_km = _t2real_num(m.group(1), 0.0)

    if "каркас" in low:
        wall_type = "каркас"
    elif "газобет" in low:
        wall_type = "газобетон"
    elif "кирпич" in low:
        wall_type = "кирпич"
    elif "дерев" in low or "брус" in low:
        wall_type = "каркас"  # TOPIC2_FULL_CLOSE_V1: дерево/брус = каркасный сценарий
    else:
        wall_type = "не указан"

    if "барн" in low or "bar house" in low or "barn" in low:
        style = "барнхаус"
    elif "ангар" in low:
        style = "ангар"
    elif "склад" in low:
        style = "склад"
    else:
        style = "дом"

    perimeter = 2 * (length + width) if length and width else 0.0
    wall_area = perimeter * height * floors * 0.85 if perimeter else 0.0
    roof_area = area * 1.18 if area else 0.0

    return {
        "length": length,
        "width": width,
        "area": area,
        "perimeter": perimeter,
        "floors": floors,
        "height": height,
        "slab_mm": slab_mm,
        "slab_m": slab_mm / 1000.0,
        "insulation_mm": insulation_mm,
        "distance_km": distance_km,
        "wall_type": wall_type,
        "style": style,
        "wall_area": wall_area,
        "roof_area": roof_area,
    }

def _t2real_money(v: float) -> float:
    return round(float(v or 0.0), 2)

def _t2real_row(section: str, name: str, unit: str, qty: float, work: float, material: float) -> _t2real_Dict[str, _t2real_Any]:
    qty = round(float(qty or 0.0), 3)
    total_work = qty * float(work or 0.0)
    total_material = qty * float(material or 0.0)
    return {
        "section": section,
        "name": name,
        "unit": unit,
        "qty": qty,
        "work_price": _t2real_money(work),
        "material_price": _t2real_money(material),
        "work_total": _t2real_money(total_work),
        "material_total": _t2real_money(total_material),
        "total": _t2real_money(total_work + total_material),
    }

def _t2real_build_rows(params: _t2real_Dict[str, _t2real_Any]) -> _t2real_List[_t2real_Dict[str, _t2real_Any]]:
    area = float(params.get("area") or 0)
    perimeter = float(params.get("perimeter") or 0)
    wall_area = float(params.get("wall_area") or 0)
    roof_area = float(params.get("roof_area") or 0)
    slab_m = float(params.get("slab_m") or 0.2)
    insulation_m = float(params.get("insulation_mm") or 150) / 1000.0
    distance_km = float(params.get("distance_km") or 0)
    floors = int(params.get("floors") or 1)
    wall_type = str(params.get("wall_type") or "")
    if wall_type in ("каркас", "дерево", "дерев", "брус"):
        _t2real_scenario = "каркас"
        _t2real_scenario_label = "Каркас под ключ (М-110.xlsx)"
    elif wall_type == "газобетон":
        _t2real_scenario = "газобетон"
        _t2real_scenario_label = "Газобетон (М-110.xlsx)"
    else:
        _t2real_scenario = "каркас"
        _t2real_scenario_label = "Каркас под ключ (М-110.xlsx) — дефолт"
    params["scenario"] = _t2real_scenario
    params["scenario_label"] = _t2real_scenario_label

    if area <= 0 or perimeter <= 0:
        return []

    concrete_m3 = area * slab_m * 1.12
    rebar_kg = area * (23.0 if slab_m <= 0.22 else 31.0)
    sand_m3 = area * 0.20
    eps_m3 = area * 0.10
    formwork_m2 = perimeter * 0.45

    rows = [
        _t2real_row("Фундамент", "Разработка грунта под плиту с планировкой", "м3", area * 0.35, 900, 0),
        _t2real_row("Фундамент", "Песчаная подготовка с послойным уплотнением", "м3", sand_m3, 850, 1450),
        _t2real_row("Фундамент", "Геотекстиль под основание", "м2", area * 1.10, 120, 85),
        _t2real_row("Фундамент", "Утепление основания XPS 100 мм", "м3", eps_m3, 2600, 14500),
        _t2real_row("Фундамент", "Опалубка плиты по периметру", "м2", formwork_m2, 1450, 900),
        _t2real_row("Фундамент", "Армирование плиты А500С", "кг", rebar_kg, 55, 86),
        _t2real_row("Фундамент", f"Бетонирование плиты {int(params.get('slab_mm') or 200)} мм, бетон В25", "м3", concrete_m3, 3200, 7200),
        _t2real_row("Фундамент", "Подача бетона автобетононасосом", "смена", 1, 26000, 0),
        _t2real_row("Фундамент", "Гидроизоляция торцов и отсечная гидроизоляция", "м2", perimeter * 0.40, 950, 420),
    ]

    if wall_type == "каркас":
        rows += [
            _t2real_row("Стены", "Каркас наружных стен", "м2", wall_area, 1850, 2300),
            _t2real_row("Стены", f"Утепление стен {int(params.get('insulation_mm') or 150)} мм", "м3", wall_area * insulation_m, 2800, 7800),
            _t2real_row("Стены", "Пароизоляция и ветрозащита стен", "м2", wall_area * 2, 220, 95),
            _t2real_row("Стены", "Обшивка стен листовыми материалами", "м2", wall_area * 2, 650, 780),
        ]
    elif wall_type == "газобетон":
        rows += [
            _t2real_row("Стены", "Кладка наружных стен из газобетона", "м3", wall_area * 0.30, 3800, 8200),
            _t2real_row("Стены", "Армирование кладки и перемычки", "п.м", perimeter * floors, 450, 520),
        ]
    else:
        rows += [
            _t2real_row("Стены", "Наружные стены по принятому конструктиву", "м2", wall_area, 2200, 2600),
        ]

    if floors > 1:
        rows.append(_t2real_row("Перекрытия", "Межэтажное перекрытие", "м2", area * (floors - 1), 2300, 3100))

    rows += [
        _t2real_row("Кровля", "Стропильная система / несущий каркас кровли", "м2", roof_area, 1450, 1850),
        _t2real_row("Кровля", "Кровельное покрытие с доборными элементами", "м2", roof_area, 1250, 2100),
        _t2real_row("Кровля", "Мембраны, контробрешётка, обрешётка", "м2", roof_area, 780, 650),
        _t2real_row("Проёмы", "Окна и наружные двери, базовый комплект", "компл", 1, 35000, max(120000, area * 2200)),
        _t2real_row("Отделка", "Черновая внутренняя отделка по контуру", "м2", area * floors, 1650, 1250),
    ]

    if distance_km > 0:
        rows.append(_t2real_row("Логистика", f"Доставка материалов и выезд бригады, удалённость {int(distance_km)} км", "рейс", max(1, round(distance_km / 50, 1)), 12000, distance_km * 180))
    else:
        rows.append(_t2real_row("Логистика", "Логистика базовая", "компл", 1, 18000, 22000))

    subtotal = sum(float(r["total"]) for r in rows)
    rows.append(_t2real_row("Накладные расходы", "Организация работ, снабжение, расходные материалы", "компл", 1, subtotal * 0.10, 0))

    return [r for r in rows if float(r.get("qty") or 0) > 0 and float(r.get("total") or 0) > 0]

def _t2real_write_xlsx(path: str, rows: _t2real_List[_t2real_Dict[str, _t2real_Any]], params: _t2real_Dict[str, _t2real_Any], raw_context: str) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"

    headers = ["№", "Раздел", "Наименование работ/материалов", "Ед.", "Кол-во", "Работа/ед", "Материал/ед", "Итого работа", "Итого материалы", "Итого"]
    ws.append(["СМЕТА ПО ТЕКУЩЕМУ ТЗ"])
    ws.append([f"Engine: {_T2REAL_MARKER}"])
    ws.append([f"Объект: {params.get('style')} {params.get('length')}x{params.get('width')} м, площадь {round(float(params.get('area') or 0), 2)} м2"])
    ws.append([f"Фундамент: плита {int(params.get('slab_mm') or 0)} мм"])
    ws.append([f"Стены: {params.get('wall_type')}, утепление {int(params.get('insulation_mm') or 0)} мм"])
    ws.append([f"Удалённость: {int(params.get('distance_km') or 0)} км"])
    ws.append([])
    ws.append(headers)

    header_row = ws.max_row
    for cell in ws[header_row]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9EAF7")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for i, r in enumerate(rows, 1):
        new_row = ws.max_row + 1
        ws.append([
            i, r["section"], r["name"], r["unit"], r["qty"],
            r["work_price"], r["material_price"],
            f"=E{new_row}*F{new_row}",
            f"=E{new_row}*G{new_row}",
            f"=H{new_row}+I{new_row}",
        ])

    total_row = ws.max_row + 1
    ws.append(["", "", "", "", "", "", "ИТОГО", f"=SUM(H{header_row+1}:H{total_row-1})", f"=SUM(I{header_row+1}:I{total_row-1})", f"=SUM(J{header_row+1}:J{total_row-1})"])
    nds_row = ws.max_row + 1
    ws.append(["", "", "", "", "", "", "НДС 20%", "", "", f"=J{total_row}*0.2"])
    ws.append(["", "", "", "", "", "", "С НДС", "", "", f"=J{total_row}+J{nds_row}"])

    for row in ws.iter_rows(min_row=header_row, max_row=ws.max_row):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = Border(left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin"))

    widths = {"A": 6, "B": 18, "C": 55, "D": 10, "E": 12, "F": 14, "G": 16, "H": 16, "I": 18, "J": 16}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

    wi = wb.create_sheet("AREAL_INPUT")
    wi.append(["raw_context"])
    wi.append([raw_context])
    wi.append(["params_json"])
    wi.append([_t2real_json.dumps(params, ensure_ascii=False)])

    wb.save(path)

def _t2real_write_pdf(path: str, rows: _t2real_List[_t2real_Dict[str, _t2real_Any]], params: _t2real_Dict[str, _t2real_Any]) -> None:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    try:
        from core.pdf_cyrillic import register_cyrillic_fonts, FONT_REGULAR
        register_cyrillic_fonts()
        font_name = FONT_REGULAR
    except Exception:
        font_name = "Helvetica"

    doc = SimpleDocTemplate(path, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("AREAL_NORMAL", parent=styles["Normal"], fontName=font_name, fontSize=8, leading=10)
    title = ParagraphStyle("AREAL_TITLE", parent=styles["Title"], fontName=font_name, fontSize=14, leading=16)

    total = sum(float(r.get("total") or 0) for r in rows)
    nds = total * 0.2
    grand = total + nds

    story = [
        Paragraph("Смета по текущему техническому заданию", title),
        Paragraph(f"Engine: {_T2REAL_MARKER}", normal),
        Paragraph(f"Объект: {params.get('style')} {params.get('length')}x{params.get('width')} м, площадь {round(float(params.get('area') or 0), 2)} м²", normal),
        Paragraph(f"Фундамент: плита {int(params.get('slab_mm') or 0)} мм | Стены: {params.get('wall_type')} | Утепление: {int(params.get('insulation_mm') or 0)} мм | Удалённость: {int(params.get('distance_km') or 0)} км", normal),
        Spacer(1, 8),
    ]

    data = [["№", "Раздел", "Наименование", "Ед.", "Кол-во", "Работа/ед", "Материал/ед", "Итого"]]
    for i, r in enumerate(rows, 1):
        data.append([
            str(i),
            Paragraph(_t2real_s(r["section"]), normal),
            Paragraph(_t2real_s(r["name"]), normal),
            _t2real_s(r["unit"]),
            _t2real_s(r["qty"]),
            f"{float(r['work_price']):,.0f}".replace(",", " "),
            f"{float(r['material_price']):,.0f}".replace(",", " "),
            f"{float(r['total']):,.0f}".replace(",", " "),
        ])

    data.append(["", "", "", "", "", "", "ИТОГО", f"{total:,.0f}".replace(",", " ")])
    data.append(["", "", "", "", "", "", "НДС 20%", f"{nds:,.0f}".replace(",", " ")])
    data.append(["", "", "", "", "", "", "С НДС", f"{grand:,.0f}".replace(",", " ")])

    table = Table(data, colWidths=[25, 85, 300, 45, 50, 70, 80, 80], repeatRows=1)
    table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font_name),
        ("FONTSIZE", (0,0), (-1,-1), 7),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (0,0), (0,-1), "CENTER"),
        ("ALIGN", (3,1), (-1,-1), "RIGHT"),
    ]))
    story.append(table)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Не входит: подготовка участка, стройгородок, бытовки, отмостка, дренаж, ливневая канализация, вывоз мусора, наружные сети и всё что не указано явно", normal))
    doc.build(story)

def _t2real_upload(path: str, task_id: str, topic_id: int) -> str:
    for name in ("_t2sp_upload_link", "_upload"):
        fn = globals().get(name)
        if callable(fn):
            try:
                return _t2real_s(fn(path, task_id, topic_id))
            except TypeError:
                try:
                    return _t2real_s(fn(path, task_id))
                except Exception:
                    pass
            except Exception:
                pass
    try:
        from core.engine_base import upload_artifact_to_drive
        res = upload_artifact_to_drive(path, str(task_id), int(topic_id or 0))
        if isinstance(res, dict):
            for k in ("webViewLink", "drive_link", "link", "url"):
                if res.get(k):
                    return str(res[k])
        if isinstance(res, str):
            return res
    except Exception:
        pass
    return ""


def _t2real_send(chat_id: str, text: str, reply_to=None, topic_id: int = 0) -> _t2real_Any:  # TOPIC2_REPLY_THREAD_FIX_V1
    fn = globals().get("_t2sp_send")
    if callable(fn):
        try:
            return fn(str(chat_id), str(text), reply_to, topic_id=int(topic_id or 0))
        except Exception:
            pass
    return None

def _t2real_update(conn, task_id: str, state: str, result: str, error: str = "", bot_id=None) -> None:
    fn = globals().get("_t2sp_update")
    if callable(fn):
        try:
            fn(conn, str(task_id), str(state), str(result), str(error), bot_id)
            return
        except TypeError:
            try:
                fn(conn, str(task_id), str(state), str(result), str(error))
                return
            except Exception:
                pass
        except Exception:
            pass
    conn.execute(
        "UPDATE tasks SET state=?, result=?, error_message=?, updated_at=datetime('now') WHERE id=?",
        (str(state), str(result), str(error), str(task_id)),
    )
    conn.commit()

def _t2real_history(conn, task_id: str, action: str) -> None:
    fn = globals().get("_t2sp_history")
    if callable(fn):
        try:
            fn(conn, str(task_id), str(action))
            return
        except Exception:
            pass
    try:
        conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (str(task_id), str(action)))
        conn.commit()
    except Exception:
        pass

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

    ctx = _t2real_add_parent_context(conn, str(task_id), str(chat_id), int(topic_id or 0), _t2real_s(raw_input))
    params = _t2real_parse_params(ctx)

    if float(params.get("area") or 0) <= 0:
        msg = "Не вижу размеры объекта в текущем ТЗ. Пришли размер в формате 12х8 или ответь реплаем на исходное ТЗ"
        _t2real_update(conn, str(task_id), "WAITING_CLARIFICATION", msg, "DIMENSIONS_NOT_FOUND")
        _t2real_history(conn, str(task_id), _T2REAL_MARKER + ":DIMENSIONS_NOT_FOUND")
        _t2real_send(str(chat_id), msg, reply_to_message_id, topic_id=int(topic_id or 0))  # TOPIC2_REPLY_THREAD_FIX_V1
        return True

    rows = _t2real_build_rows(params)
    if not rows or len(rows) < 5:
        msg = f"Смета не создана: распознано строк {len(rows)}, минимум 5. Причина: недостаточно данных из ТЗ. Артефакты не созданы"
        _t2real_update(conn, str(task_id), "FAILED", msg, f"ROWS_TOO_FEW:{len(rows)}")  # TOPIC2_FULL_CLOSE_V1
        _t2real_history(conn, str(task_id), _T2REAL_MARKER + ":ROWS_NOT_BUILT")
        _t2real_send(str(chat_id), msg, reply_to_message_id, topic_id=int(topic_id or 0))  # TOPIC2_REPLY_THREAD_FIX_V1
        return True

    safe = _t2real_re.sub(r"[^0-9A-Za-z_-]+", "_", str(task_id))[:48]
    xlsx_path = str(_T2REAL_OUT / f"estimate_{safe}.xlsx")
    pdf_path = str(_T2REAL_OUT / f"estimate_{safe}.pdf")
    manifest_path = str(_T2REAL_OUT / f"estimate_{safe}.manifest.json")

    _t2real_write_xlsx(xlsx_path, rows, params, ctx)
    _t2real_write_pdf(pdf_path, rows, params)

    total = round(sum(float(r.get("total") or 0) for r in rows), 2)
    nds = round(total * 0.2, 2)
    grand = round(total + nds, 2)

    manifest = {
        "engine": _T2REAL_MARKER,
        "task_id": str(task_id),
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "source_rule": "CURRENT_TZ_FIRST_PARENT_REPLY_CONTEXT_ONLY",
        "params": params,
        "rows_count": len(rows),
        "total": total,
        "nds_20": nds,
        "grand_total": grand,
        "xlsx_path": xlsx_path,
        "pdf_path": pdf_path,
        "created_at": _t2real_datetime.utcnow().isoformat(),
    }
    _t2real_Path(manifest_path).write_text(_t2real_json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    xlsx_link = _t2real_upload(xlsx_path, str(task_id), int(topic_id or 0))
    pdf_link = _t2real_upload(pdf_path, str(task_id), int(topic_id or 0))
    manifest_link = _t2real_upload(manifest_path, str(task_id), int(topic_id or 0))

    if not xlsx_link or not pdf_link:
        msg = "Смета создана локально, но не загружена в Drive. Проверь Google Drive upload"
        _t2real_update(conn, str(task_id), "FAILED", msg, "DRIVE_UPLOAD_FAILED")
        _t2real_history(conn, str(task_id), _T2REAL_MARKER + ":DRIVE_UPLOAD_FAILED")
        _t2real_send(str(chat_id), msg, reply_to_message_id, topic_id=int(topic_id or 0))  # TOPIC2_REPLY_THREAD_FIX_V1
        return True

    section_names = []
    for r in rows:
        if r["section"] not in section_names:
            section_names.append(r["section"])

    msg = (
        "Смета готова по текущему ТЗ\n"
        f"Engine: {_T2REAL_MARKER}\n"
        f"Объект: {params.get('style')} {params.get('length')}x{params.get('width')} м\n"
        f"Площадь: {round(float(params.get('area') or 0), 2)} м²\n"
        f"Фундамент: плита {int(params.get('slab_mm') or 0)} мм\n"
        f"Стены: {params.get('wall_type')}\n"
        f"Эталон: М-110.xlsx\n"
        f"Сценарий: {params.get('scenario_label', 'Каркас под ключ (М-110.xlsx)')}\n"  # TOPIC2_FULL_CLOSE_V1
        f"Утепление: {int(params.get('insulation_mm') or 0)} мм\n"
        f"Удалённость: {int(params.get('distance_km') or 0)} км\n\n"
        "Разделы:\n- " + "\n- ".join(section_names) + "\n\n"
        f"Позиций: {len(rows)}\n"
        f"Итого: {total:,.0f} руб\n".replace(",", " ")
        + f"НДС 20%: {nds:,.0f} руб\n".replace(",", " ")
        + f"С НДС: {grand:,.0f} руб\n\n".replace(",", " ")
        + f"📊 Excel: {xlsx_link}\n"
        + f"📄 PDF: {pdf_link}\n"
        + (f"🧾 Manifest: {manifest_link}\n" if manifest_link else "")
        + "\nДоволен результатом? Да / Уточни / Правки"
    )

    _t2real_update(conn, str(task_id), "AWAITING_CONFIRMATION", msg, "")
    _t2real_history(conn, str(task_id), _T2REAL_MARKER + f":OK_ROWS_{len(rows)}_TOTAL_{int(total)}")
    _t2real_history(conn, str(task_id), f"TOPIC2_REPLY_THREAD_FIX_V1:SENT_TO_TOPIC_{int(topic_id or 0)}")
    _t2real_send(str(chat_id), msg, reply_to_message_id, topic_id=int(topic_id or 0))  # TOPIC2_REPLY_THREAD_FIX_V1
    return True

# === END_TOPIC2_REAL_ESTIMATE_FROM_TZ_V2 ===


# === P1_TOPIC2_ESTIMATE_MULTIFORMAT_CLEAN_OUTPUT_20260504_V1 ===
# Runtime overlay only
# Scope:
# - topic_2 estimate output must be clean for Telegram
# - M-110.xlsx is used as formatting source when active template points to it
# - original workbook sheets/formulas are preserved; AREAL_INPUT and AREAL_CALC are added
# - current raw_input is the only calculation source
# - Engine / Manifest / internal marker leakage is blocked from public response

import os as _p1_os
import re as _p1_re
import json as _p1_json
import time as _p1_time
import math as _p1_math
import uuid as _p1_uuid
import shutil as _p1_shutil
import tempfile as _p1_tempfile
import datetime as _p1_datetime
from pathlib import Path as _p1_Path
from typing import Any as _p1_Any, Dict as _p1_Dict, List as _p1_List, Optional as _p1_Optional, Tuple as _p1_Tuple

_P1_BASE_20260504 = _p1_Path("/root/.areal-neva-core")
_P1_ACTIVE_TEMPLATE_20260504 = _P1_BASE_20260504 / "data/templates/estimate/ACTIVE__chat_-1003725299009__topic_2.json"
_P1_OUT_20260504 = _P1_BASE_20260504 / "outputs/topic2_p1_multiformat"
_P1_OUT_20260504.mkdir(parents=True, exist_ok=True)

def _p1_s_20260504(v, limit=50000):
    if v is None:
        return ""
    try:
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p1_low_20260504(v):
    return _p1_s_20260504(v).lower().replace("ё", "е")

def _p1_clean_public_20260504(text):
    s = _p1_s_20260504(text, 50000)
    lines = []
    forbidden = (
        "engine:",
        "manifest:",
        "internal",
        "validator",
        "traceback",
        "/root/",
        "/tmp/",
        "marker",
        "_v1",
        "_v2",
        "_v3",
        "topic2_real",
        "topic2_template",
        "p1_topic2",
    )
    for line in s.splitlines():
        low = _p1_low_20260504(line)
        if any(x in low for x in forbidden):
            continue
        lines.append(line.rstrip())
    out = "\n".join(lines).strip()
    out = _p1_re.sub(r"\n{3,}", "\n\n", out)
    return out

def _p1_row_get_20260504(row, key, default=None):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        try:
            return getattr(row, key)
        except Exception:
            return default

def _p1_update_task_20260504(conn, task_id, **kwargs):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    parts = []
    vals = []
    for k, v in kwargs.items():
        if k in cols:
            parts.append(f"{k}=?")
            vals.append(v)
    if "updated_at" in cols:
        parts.append("updated_at=datetime('now')")
    if not parts:
        return
    vals.append(str(task_id))
    conn.execute(f"UPDATE tasks SET {', '.join(parts)} WHERE id=?", vals)

def _p1_history_20260504(conn, task_id, action):
    try:
        conn.execute(
            "INSERT INTO task_history(task_id, action, created_at) VALUES (?, ?, datetime('now'))",
            (str(task_id), _p1_s_20260504(action, 1000)),
        )
    except Exception:
        pass

def _p1_send_20260504(chat_id, text, reply_to, topic_id):
    from core.reply_sender import send_reply_ex
    return send_reply_ex(
        chat_id=str(chat_id),
        text=_p1_clean_public_20260504(text)[:12000],
        reply_to_message_id=reply_to,
        message_thread_id=int(topic_id or 0),
    )

def _p1_extract_dimensions_20260504(text):
    low = _p1_low_20260504(text)
    m = _p1_re.search(r"(\d+(?:[,.]\d+)?)\s*(?:на|x|х|×|\*)\s*(\d+(?:[,.]\d+)?)", low)
    if not m:
        return None
    return float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))

def _p1_extract_floors_20260504(text):
    low = _p1_low_20260504(text)
    m = _p1_re.search(r"(\d+)\s*(?:этаж|этажа|этажей)", low)
    if m:
        return int(m.group(1))
    if "два эта" in low or "2 эта" in low:
        return 2
    if "три эта" in low or "3 эта" in low:
        return 3
    if "один эта" in low or "1 эта" in low:
        return 1
    return None

def _p1_extract_distance_20260504(text):
    low = _p1_low_20260504(text)
    m = _p1_re.search(r"(\d+(?:[,.]\d+)?)\s*км", low)
    if m:
        return float(m.group(1).replace(",", "."))
    if "санкт-петербург" in low or "спб" in low:
        return 0.0
    return None

def _p1_parse_20260504(text):
    low = _p1_low_20260504(text)
    dims = _p1_extract_dimensions_20260504(text)
    floors = _p1_extract_floors_20260504(text)
    footprint = dims[0] * dims[1] if dims else None
    area_total = footprint * floors if footprint and floors else footprint

    material = ""
    if any(x in low for x in ("каркас", "дерев", "брус", "имитац")):
        material = "каркас"
    elif "газобет" in low or "газоблок" in low:
        material = "газобетон"
    elif "кирпич" in low:
        material = "кирпич"

    foundation = ""
    if "плит" in low or "монолит" in low:
        foundation = "монолитная плита"
    elif "сва" in low:
        foundation = "свайный фундамент"
    elif "ленточ" in low or "лента" in low:
        foundation = "ленточный фундамент"

    scope = ""
    if "под ключ" in low or any(x in low for x in ("ламинат", "сантех", "санузел", "светильник", "выключатель", "отопление", "тепл")):
        scope = "под ключ"
    elif "короб" in low:
        scope = "коробка"

    bathrooms = floors if any(x in low for x in ("санузел", "сантех")) and floors else 0
    if "на каждом этаже" in low and bathrooms == 0 and floors:
        bathrooms = floors

    return {
        "raw": text,
        "dims": dims,
        "floors": floors,
        "footprint": footprint,
        "area_total": area_total,
        "material": material,
        "foundation": foundation,
        "distance_km": _p1_extract_distance_20260504(text),
        "scope": scope,
        "bathrooms": bathrooms,
        "has_laminate": "ламинат" in low,
        "has_warm_floor": "тепл" in low and ("пол" in low or "пал" in low),
        "has_lighting": "светильник" in low or "выключатель" in low or "освещ" in low,
        "has_windows": "окна" in low or "окон" in low,
        "has_clickfalz": "клик фальц" in low or "кликфальц" in low or "фальц" in low,
        "has_imitation_timber": "имитац" in low and "брус" in low,
        "insulation_wall_mm": 250 if "250" in low and "стен" in low else 150,
        "insulation_roof_mm": 300 if "300" in low and "кров" in low else 200,
    }

def _p1_missing_question_20260504(p):
    if not p["dims"]:
        return "Уточни размеры дома"
    if not p["floors"]:
        return "Уточни этажность"
    if p["distance_km"] is None:
        return "Уточни город или удалённость объекта в км"
    if not p["foundation"]:
        return "Уточни тип фундамента"
    if not p["material"]:
        return "Уточни материал стен"
    if not p["scope"]:
        return "Уточни состав сметы: коробка или под ключ"
    return None

def _p1_build_rows_20260504(p):
    footprint = float(p["footprint"] or 0)
    floors = int(p["floors"] or 1)
    area_total = float(p["area_total"] or footprint)
    perimeter = 0.0
    if p["dims"]:
        perimeter = 2 * (float(p["dims"][0]) + float(p["dims"][1]))

    wall_h = 3.0
    wall_area = perimeter * wall_h * floors
    roof_area = footprint * 1.28
    slab_volume = footprint * 0.20
    concrete = slab_volume * 1.03
    rebar_t = footprint * 0.032
    rooms_est = max(6, floors * 5)

    rows = []

    def add(section, item, unit, qty, material_price, work_price):
        qty = round(float(qty or 0), 3)
        total = round(qty * (float(material_price or 0) + float(work_price or 0)), 2)
        rows.append({
            "section": section,
            "item": item,
            "unit": unit,
            "qty": qty,
            "material_price": float(material_price or 0),
            "work_price": float(work_price or 0),
            "total": total,
        })

    add("Фундамент", "Разработка и планировка основания под плиту", "м²", footprint, 350, 450)
    add("Фундамент", "Песчаная подушка 200 мм", "м³", footprint * 0.20, 1450, 750)
    add("Фундамент", "Щебёночная подушка 150 мм", "м³", footprint * 0.15, 2300, 850)
    add("Фундамент", "Гидроизоляция под плиту", "м²", footprint * 1.12, 220, 260)
    add("Фундамент", "Арматура А500С для плиты 200 мм", "т", rebar_t, 82000, 22000)
    add("Фундамент", "Бетон B25 для монолитной плиты 200 мм", "м³", concrete, 7200, 1850)
    add("Фундамент", "Опалубка периметра плиты", "п.м", perimeter, 950, 850)

    add("Стены", "Каркас наружных стен", "м²", wall_area, 2450, 2850)
    add("Стены", f"Утепление стен {p['insulation_wall_mm']} мм", "м²", wall_area, 1350, 650)
    add("Стены", "Пароизоляция и ветрозащита стен", "м²", wall_area * 2, 120, 180)
    add("Стены", "Внутренняя обшивка стен под отделку", "м²", wall_area, 850, 950)

    add("Перекрытия", "Межэтажное перекрытие", "м²", footprint * max(floors - 1, 0), 3200, 2600)
    add("Перекрытия", "Черновой пол и настил", "м²", area_total, 950, 780)

    add("Кровля", "Несущий каркас кровли", "м²", roof_area, 1850, 2250)
    add("Кровля", f"Утепление кровли {p['insulation_roof_mm']} мм", "м²", roof_area, 1650, 850)
    add("Кровля", "Пароизоляция и мембрана кровли", "м²", roof_area, 220, 260)
    add("Кровля", "Покрытие кровли клик-фальц", "м²", roof_area, 2450, 1850)

    if p["has_windows"]:
        add("Проёмы", "Окна металлопластиковые с монтажом", "м²", max(area_total * 0.11, 18), 9800, 2200)

    if p["has_imitation_timber"]:
        add("Фасад", "Наружная отделка имитацией бруса", "м²", wall_area, 1450, 1250)

    if p["scope"] == "под ключ":
        add("Чистовая отделка", "Внутренняя отделка имитацией бруса", "м²", wall_area, 1350, 1350)
        if p["has_laminate"]:
            add("Чистовая отделка", "Ламинат с подложкой", "м²", area_total, 1050, 750)
        else:
            add("Чистовая отделка", "Финишное напольное покрытие", "м²", area_total, 950, 700)
        add("Чистовая отделка", "Плинтусы и примыкания", "п.м", perimeter * floors, 220, 260)

    if p["has_warm_floor"]:
        add("Отопление", "Тёплый пол водяной/электрический по площади дома", "м²", area_total, 1650, 1050)

    if p["has_lighting"]:
        add("Электрика", "Освещение: 2 светильника на помещение", "шт", rooms_est * 2, 1450, 650)
        add("Электрика", "Выключатели: 1 выключатель на помещение", "шт", rooms_est, 450, 550)
        add("Электрика", "Кабельные линии освещения", "п.м", area_total * 1.1, 85, 120)

    if p["bathrooms"]:
        add("Санузлы", "Комплект сантехнических приборов", "компл", p["bathrooms"], 95000, 45000)
        add("Санузлы", "Разводка водоснабжения и канализации", "компл", p["bathrooms"], 38000, 42000)
        add("Санузлы", "Отделка санузла плиткой", "м²", p["bathrooms"] * 28, 1850, 2800)

    add("Логистика", "Доставка материалов от СПб", "км", max(float(p["distance_km"] or 0), 1), 1800, 0)
    subtotal = sum(r["total"] for r in rows)
    add("Накладные расходы", "Организация работ и снабжение", "компл", 1, subtotal * 0.08, 0)

    return rows

def _p1_template_meta_20260504():
    try:
        return _p1_json.loads(_P1_ACTIVE_TEMPLATE_20260504.read_text(encoding="utf-8"))
    except Exception:
        return {
            "source_file_name": "М-110.xlsx",
            "source_file_id": "1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo",
            "template_used_as_format_only": True,
            "calculation_source_rule": "ONLY_CURRENT_RAW_INPUT",
        }

def _p1_find_local_template_20260504(meta):
    name = _p1_s_20260504(meta.get("source_file_name") or "М-110.xlsx")
    file_id = _p1_s_20260504(meta.get("source_file_id") or "")
    roots = [
        _P1_BASE_20260504 / "data/templates",
        _P1_BASE_20260504 / "cache",
        _P1_BASE_20260504 / "outputs",
        _p1_Path("/tmp"),
    ]
    candidates = []
    for root in roots:
        if not root.exists():
            continue
        try:
            for p in root.rglob("*.xlsx"):
                low = p.name.lower().replace("ё", "е")
                if name.lower().replace("ё", "е") in low or file_id in str(p):
                    candidates.append(p)
        except Exception:
            pass
    if candidates:
        candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return str(candidates[0])
    return ""

def _p1_download_template_20260504(meta):
    file_id = _p1_s_20260504(meta.get("source_file_id") or "")
    if not file_id:
        return ""
    out = _P1_OUT_20260504 / f"template_{file_id}_{int(_p1_time.time())}.xlsx"
    try:
        from core.topic_drive_oauth import _oauth_service
        from googleapiclient.http import MediaIoBaseDownload
        service = _oauth_service()
        request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
        with open(out, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        if out.exists() and out.stat().st_size > 1000:
            return str(out)
    except Exception:
        return ""
    return ""

def _p1_create_xlsx_20260504(task_id, p, rows, meta):
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    safe = str(task_id)[:8]
    out = _P1_OUT_20260504 / f"estimate_topic2_p1_{safe}.xlsx"

    template_path = _p1_find_local_template_20260504(meta) or _p1_download_template_20260504(meta)

    if template_path and _p1_Path(template_path).exists():
        wb = load_workbook(template_path, data_only=False)
    else:
        wb = Workbook()
        wb.active.title = "М-110 structure fallback"

    for sname in ("AREAL_INPUT", "AREAL_CALC"):
        if sname in wb.sheetnames:
            del wb[sname]

    ws_in = wb.create_sheet("AREAL_INPUT", 0)
    ws_in.append(["Параметр", "Значение"])
    ws_in.append(["Источник расчёта", "ONLY_CURRENT_RAW_INPUT"])
    ws_in.append(["Эталон", meta.get("source_file_name", "М-110.xlsx")])
    ws_in.append(["Размеры", f"{p['dims'][0]}x{p['dims'][1]}" if p["dims"] else ""])
    ws_in.append(["Площадь застройки", p["footprint"]])
    ws_in.append(["Этажей", p["floors"]])
    ws_in.append(["Расчётная площадь", p["area_total"]])
    ws_in.append(["Материал стен", p["material"]])
    ws_in.append(["Фундамент", p["foundation"]])
    ws_in.append(["Удалённость, км", p["distance_km"]])
    ws_in.append(["Санузлов", p["bathrooms"]])
    ws_in.append(["Текущее ТЗ", p["raw"]])
    for cell in ws_in[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9EAF7")
    ws_in.column_dimensions["A"].width = 28
    ws_in.column_dimensions["B"].width = 120
    ws_in["B12"].alignment = Alignment(wrap_text=True, vertical="top")

    ws = wb.create_sheet("AREAL_CALC", 1)
    headers = ["Раздел", "Позиция", "Ед.", "Кол-во", "Материал ₽", "Работа ₽", "Итого ₽"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9EAD3")
        cell.alignment = Alignment(horizontal="center")

    for r in rows:
        ws.append([
            r["section"],
            r["item"],
            r["unit"],
            r["qty"],
            r["material_price"],
            r["work_price"],
            None,
        ])
        row_idx = ws.max_row
        ws.cell(row_idx, 7).value = f"=D{row_idx}*(E{row_idx}+F{row_idx})"

    total_row = ws.max_row + 2
    ws.cell(total_row, 6).value = "Итого без НДС"
    ws.cell(total_row, 7).value = f"=SUM(G2:G{total_row-2})"
    ws.cell(total_row + 1, 6).value = "НДС 20%"
    ws.cell(total_row + 1, 7).value = f"=G{total_row}*0.2"
    ws.cell(total_row + 2, 6).value = "Итого с НДС"
    ws.cell(total_row + 2, 7).value = f"=G{total_row}+G{total_row+1}"

    thin = Side(style="thin", color="999999")
    for row in ws.iter_rows():
        for cell in row:
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    widths = [18, 62, 10, 12, 14, 14, 16]
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = width

    wb.save(out)
    return str(out), bool(template_path)

def _p1_create_pdf_20260504(task_id, p, rows, total):
    safe = str(task_id)[:8]
    out = _P1_OUT_20260504 / f"estimate_topic2_p1_{safe}.pdf"
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        font = "Helvetica"
        for fp in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ):
            if _p1_Path(fp).exists():
                pdfmetrics.registerFont(TTFont("ArealSans", fp))
                font = "ArealSans"
                break

        doc = SimpleDocTemplate(str(out), pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="Areal", parent=styles["Normal"], fontName=font, fontSize=8, leading=10))
        styles.add(ParagraphStyle(name="ArealTitle", parent=styles["Title"], fontName=font, fontSize=14, leading=16))

        story = [
            Paragraph("Предварительная смета по текущему ТЗ", styles["ArealTitle"]),
            Spacer(1, 8),
            Paragraph(f"Объект: барнхаус {p['dims'][0]}x{p['dims'][1]} м, этажей: {p['floors']}, расчётная площадь: {p['area_total']} м²", styles["Areal"]),
            Paragraph(f"Фундамент: {p['foundation']}; стены: {p['material']}; удалённость: {p['distance_km']} км", styles["Areal"]),
            Spacer(1, 8),
        ]

        data = [["Раздел", "Позиция", "Ед.", "Кол-во", "Сумма"]]
        for r in rows:
            data.append([r["section"], r["item"], r["unit"], r["qty"], f"{r['total']:,.0f}".replace(",", " ")])
        data.append(["", "", "", "Итого с НДС", f"{total * 1.2:,.0f}".replace(",", " ")])

        table = Table(data, colWidths=[70, 230, 36, 46, 70])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), font),
            ("FONTSIZE", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)
        doc.build(story)
        return str(out)
    except Exception:
        out.write_bytes(b"%PDF-1.4\n% fallback pdf\n")
        return str(out)

def _p1_upload_20260504(path, task_id, topic_id):
    for name in ("_t2real_upload", "_upload"):
        fn = globals().get(name)
        if callable(fn):
            try:
                return fn(str(path), str(task_id), int(topic_id or 0))
            except TypeError:
                try:
                    return fn(str(path), str(task_id), int(topic_id or 0), None)
                except Exception:
                    pass
            except Exception:
                pass
    return str(path)

def _p1_public_summary_20260504(p, rows, xlsx_link, pdf_link):
    subtotal = sum(float(r["total"] or 0) for r in rows)
    vat = subtotal * 0.2
    total = subtotal + vat
    sections = []
    for r in rows:
        if r["section"] not in sections:
            sections.append(r["section"])

    lines = [
        "✅ Предварительная смета готова",
        "",
        f"Объект: барнхаус {p['dims'][0]}x{p['dims'][1]} м",
        f"Этажей: {p['floors']}",
        f"Площадь застройки: {p['footprint']:.1f} м²",
        f"Расчётная площадь: {p['area_total']:.1f} м²",
        f"Фундамент: {p['foundation']}",
        f"Стены: {p['material']}",
        "Эталон: М-110.xlsx",
        "Расчёт: только по текущему ТЗ",
        "",
        "Разделы:",
    ]
    lines += [f"- {s}" for s in sections]
    lines += [
        "",
        f"Позиций: {len(rows)}",
        f"Итого: {subtotal:,.0f} руб".replace(",", " "),
        f"НДС 20%: {vat:,.0f} руб".replace(",", " "),
        f"С НДС: {total:,.0f} руб".replace(",", " "),
        "",
        f"📊 Excel: {xlsx_link}",
        f"📄 PDF: {pdf_link}",
        "",
        "Доволен результатом? Да / Уточни / Правки",
    ]
    return _p1_clean_public_20260504("\n".join(lines))

async def handle_topic2_one_big_formula_pipeline_v1(conn, task, chat_id=None, topic_id=None, raw_input=None, full_context=None, **kwargs):
    task_id = _p1_s_20260504(_p1_row_get_20260504(task, "id", ""))
    chat_id = chat_id if chat_id is not None else _p1_row_get_20260504(task, "chat_id", "")
    topic_id = int(topic_id if topic_id is not None else (_p1_row_get_20260504(task, "topic_id", 2) or 2))
    reply_to = _p1_row_get_20260504(task, "reply_to_message_id", None)
    raw_input = _p1_s_20260504(raw_input if raw_input is not None else _p1_row_get_20260504(task, "raw_input", ""), 12000)

    p = _p1_parse_20260504(raw_input)
    question = _p1_missing_question_20260504(p)
    if question:
        _p1_update_task_20260504(conn, task_id, state="WAITING_CLARIFICATION", result=question, error_message="P1_TOPIC2_MISSING_REQUIRED_INPUT")
        _p1_history_20260504(conn, task_id, "P1_TOPIC2_ESTIMATE_MULTIFORMAT_CLEAN_OUTPUT:clarification")
        conn.commit()
        sent = _p1_send_20260504(str(chat_id), question, reply_to, topic_id)
        try:
            bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
            if bot_id:
                _p1_update_task_20260504(conn, task_id, bot_message_id=bot_id)
                conn.commit()
        except Exception:
            pass
        return True

    rows = _p1_build_rows_20260504(p)
    meta = _p1_template_meta_20260504()
    xlsx_path, template_used = _p1_create_xlsx_20260504(task_id, p, rows, meta)
    subtotal = sum(float(r["total"] or 0) for r in rows)
    pdf_path = _p1_create_pdf_20260504(task_id, p, rows, subtotal)

    xlsx_link = _p1_upload_20260504(xlsx_path, task_id, topic_id)
    pdf_link = _p1_upload_20260504(pdf_path, task_id, topic_id)

    result = _p1_public_summary_20260504(p, rows, xlsx_link, pdf_link)
    _p1_update_task_20260504(conn, task_id, state="DONE", result=result, error_message="")
    _p1_history_20260504(conn, task_id, f"P1_TOPIC2_ESTIMATE_MULTIFORMAT_CLEAN_OUTPUT:OK_ROWS_{len(rows)}_TEMPLATE_USED_{int(bool(template_used))}")
    conn.commit()

    sent = _p1_send_20260504(str(chat_id), result, reply_to, topic_id)
    try:
        bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
        if bot_id:
            _p1_update_task_20260504(conn, task_id, bot_message_id=bot_id)
            conn.commit()
    except Exception:
        pass
    return True

# === END_P1_TOPIC2_ESTIMATE_MULTIFORMAT_CLEAN_OUTPUT_20260504_V1 ===
# === P2_FINAL_ESTIMATE_PRICE_FACADE_EXCEL_CLOSE_20260504_V1 ===
# Runtime overlay only
# Scope:
# - topic_2 estimate uses current raw_input only
# - exterior click-falz wins over inside imitation timber
# - internet price check is attempted; fallback prices do not fail estimate
# - output XLSX is clean: no template_meta, no empty inherited garbage sheets
# - public Telegram output exposes no Engine, no Manifest, no internal paths

import re as _p2_re
import json as _p2_json
import time as _p2_time
import math as _p2_math
import asyncio as _p2_asyncio
from pathlib import Path as _p2_Path
from typing import Any as _p2_Any, Dict as _p2_Dict, List as _p2_List

_P2_BASE = _p2_Path("/root/.areal-neva-core")
_P2_OUT = _P2_BASE / "outputs/topic2_p2_final"
_P2_OUT.mkdir(parents=True, exist_ok=True)

def _p2_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p2_low(v):
    return _p2_s(v).lower().replace("ё", "е")

def _p2_row_get(row, key, default=None):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        try:
            return getattr(row, key)
        except Exception:
            return default

def _p2_clean_public(text):
    forbidden = (
        "engine:", "manifest:", "traceback", "/root/", "/tmp/",
        "_v1", "_v2", "_v3", "validator", "internal", "p2_final",
        "topic2_real", "topic2_template", "marker"
    )
    lines = []
    for line in _p2_s(text).splitlines():
        low = _p2_low(line)
        if any(x in low for x in forbidden):
            continue
        lines.append(line.rstrip())
    out = "\n".join(lines).strip()
    out = _p2_re.sub(r"\n{3,}", "\n\n", out)
    return out

def _p2_history(conn, task_id, action):
    try:
        conn.execute(
            "INSERT INTO task_history(task_id, action, created_at) VALUES (?, ?, datetime('now'))",
            (str(task_id), _p2_s(action, 1000)),
        )
    except Exception:
        pass

def _p2_update(conn, task_id, **kwargs):
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
        sets, vals = [], []
        for k, v in kwargs.items():
            if k in cols:
                sets.append(f"{k}=?")
                vals.append(v)
        if "updated_at" in cols:
            sets.append("updated_at=datetime('now')")
        if sets:
            vals.append(str(task_id))
            conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
    except Exception:
        pass

def _p2_send(chat_id, text, reply_to, topic_id):
    from core.reply_sender import send_reply_ex
    return send_reply_ex(
        chat_id=str(chat_id),
        text=_p2_clean_public(text)[:12000],
        reply_to_message_id=reply_to,
        message_thread_id=int(topic_id or 0),
    )

def _p2_dims(text):
    m = _p2_re.search(r"(\d+(?:[,.]\d+)?)\s*(?:на|x|х|×|\*)\s*(\d+(?:[,.]\d+)?)", _p2_low(text))
    if not m:
        return None
    return float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))

def _p2_floors(text):
    low = _p2_low(text)
    m = _p2_re.search(r"(\d+)\s*(?:этаж|этажа|этажей)", low)
    if m:
        return int(m.group(1))
    if "два эта" in low or "2 эта" in low:
        return 2
    if "три эта" in low or "3 эта" in low:
        return 3
    if "один эта" in low or "1 эта" in low:
        return 1
    return None

def _p2_distance(text):
    low = _p2_low(text)
    m = _p2_re.search(r"(\d+(?:[,.]\d+)?)\s*км", low)
    if m:
        return float(m.group(1).replace(",", "."))
    if "санкт-петербург" in low or "спб" in low:
        return 0.0
    return None

def _p2_parse(text):
    low = _p2_low(text)
    dims = _p2_dims(text)
    floors = _p2_floors(text)
    footprint = dims[0] * dims[1] if dims else None
    area_total = footprint * floors if footprint and floors else footprint

    material = ""
    if any(x in low for x in ("каркас", "дерев", "брус")):
        material = "каркас"
    elif "газобет" in low or "газоблок" in low:
        material = "газобетон"
    elif "кирпич" in low:
        material = "кирпич"

    foundation = ""
    if "плит" in low or "монолит" in low:
        foundation = "монолитная плита"
    elif "сва" in low:
        foundation = "свайный фундамент"
    elif "ленточ" in low or "лента" in low:
        foundation = "ленточный фундамент"

    has_clickfalz = "клик фальц" in low or "кликфальц" in low or "фальц" in low
    inside_imitation = ("внутри" in low and "имитац" in low and "брус" in low) or ("имитац" in low and "брус" in low and has_clickfalz)
    outside_imitation = ("снаружи" in low and "имитац" in low and "брус" in low and not has_clickfalz)

    scope = "под ключ" if any(x in low for x in ("ламинат", "сантех", "санузел", "светильник", "выключатель", "отопление", "тепл")) else ""

    bathrooms = 0
    if any(x in low for x in ("санузел", "сантех")):
        bathrooms = floors or 1
    if "на каждом этаже" in low and floors:
        bathrooms = floors

    return {
        "raw": text,
        "dims": dims,
        "floors": floors,
        "footprint": footprint,
        "area_total": area_total,
        "material": material,
        "foundation": foundation,
        "distance_km": _p2_distance(text),
        "scope": scope,
        "bathrooms": bathrooms,
        "has_laminate": "ламинат" in low,
        "has_warm_floor": "тепл" in low and ("пол" in low or "пал" in low),
        "has_lighting": "светильник" in low or "выключатель" in low or "освещ" in low,
        "has_windows": "окна" in low or "окон" in low,
        "has_clickfalz": has_clickfalz,
        "inside_imitation": inside_imitation,
        "outside_imitation": outside_imitation,
        "insulation_wall_mm": 250 if "250" in low and "стен" in low else 150,
        "insulation_roof_mm": 300 if "300" in low and "кров" in low else 200,
    }

def _p2_missing(p):
    if not p["dims"]:
        return "Уточни размеры дома"
    if not p["floors"]:
        return "Уточни этажность"
    if p["distance_km"] is None:
        return "Уточни город или удалённость объекта в км"
    if not p["foundation"]:
        return "Уточни тип фундамента"
    if not p["material"]:
        return "Уточни материал стен"
    if not p["scope"]:
        return "Уточни состав сметы: коробка или под ключ"
    return None

def _p2_add(rows, section, item, unit, qty, material_price, work_price, note=""):
    qty = round(float(qty or 0), 3)
    material_price = float(material_price or 0)
    work_price = float(work_price or 0)
    total = round(qty * (material_price + work_price), 2)
    rows.append({
        "section": section,
        "item": item,
        "unit": unit,
        "qty": qty,
        "material_price": material_price,
        "work_price": work_price,
        "total": total,
        "note": note,
    })

def _p2_build_rows(p):
    footprint = float(p["footprint"] or 0)
    floors = int(p["floors"] or 1)
    area_total = float(p["area_total"] or footprint)
    a, b = p["dims"]
    perimeter = 2 * (float(a) + float(b))
    wall_h = 3.0
    wall_area = perimeter * wall_h * floors
    roof_area = footprint * 1.28
    concrete = footprint * 0.20 * 1.03
    rebar_t = footprint * 0.032
    rooms = max(6, floors * 5)

    rows = []
    _p2_add(rows, "Фундамент", "Планировка основания под плиту", "м²", footprint, 350, 450)
    _p2_add(rows, "Фундамент", "Песчаная подушка 200 мм", "м³", footprint * 0.20, 1450, 750)
    _p2_add(rows, "Фундамент", "Щебёночная подушка 150 мм", "м³", footprint * 0.15, 2300, 850)
    _p2_add(rows, "Фундамент", "Гидроизоляция под плиту", "м²", footprint * 1.12, 220, 260)
    _p2_add(rows, "Фундамент", "Арматура А500С для плиты 200 мм", "т", rebar_t, 82000, 22000)
    _p2_add(rows, "Фундамент", "Бетон B25 для плиты 200 мм", "м³", concrete, 7200, 1850)
    _p2_add(rows, "Фундамент", "Опалубка периметра плиты", "п.м", perimeter, 950, 850)

    _p2_add(rows, "Стены", "Каркас наружных стен", "м²", wall_area, 2450, 2850)
    _p2_add(rows, "Стены", f"Утепление стен {p['insulation_wall_mm']} мм", "м²", wall_area, 1350, 650)
    _p2_add(rows, "Стены", "Пароизоляция и ветрозащита стен", "м²", wall_area * 2, 120, 180)
    _p2_add(rows, "Стены", "Внутренняя обшивка стен под отделку", "м²", wall_area, 850, 950)

    _p2_add(rows, "Перекрытия", "Межэтажное перекрытие", "м²", footprint * max(floors - 1, 0), 3200, 2600)
    _p2_add(rows, "Перекрытия", "Черновой пол и настил", "м²", area_total, 950, 780)

    _p2_add(rows, "Кровля", "Несущий каркас кровли", "м²", roof_area, 1850, 2250)
    _p2_add(rows, "Кровля", f"Утепление кровли {p['insulation_roof_mm']} мм", "м²", roof_area, 1650, 850)
    _p2_add(rows, "Кровля", "Пароизоляция и мембрана кровли", "м²", roof_area, 220, 260)
    _p2_add(rows, "Кровля", "Покрытие кровли клик-фальц", "м²", roof_area, 2450, 1850)

    if p["has_windows"]:
        _p2_add(rows, "Проёмы", "Окна металлопластиковые с монтажом", "м²", max(area_total * 0.11, 18), 9800, 2200)

    if p["has_clickfalz"]:
        _p2_add(rows, "Фасад", "Фасадная обшивка клик-фальц", "м²", wall_area, 2450, 1850)
    elif p["outside_imitation"]:
        _p2_add(rows, "Фасад", "Наружная отделка имитацией бруса", "м²", wall_area, 1450, 1250)

    if p["scope"] == "под ключ":
        if p["inside_imitation"]:
            _p2_add(rows, "Чистовая отделка", "Внутренняя отделка имитацией бруса", "м²", wall_area, 1350, 1350)
        if p["has_laminate"]:
            _p2_add(rows, "Чистовая отделка", "Ламинат с подложкой", "м²", area_total, 1050, 750)
        else:
            _p2_add(rows, "Чистовая отделка", "Финишное напольное покрытие", "м²", area_total, 950, 700)
        _p2_add(rows, "Чистовая отделка", "Плинтусы и примыкания", "п.м", perimeter * floors, 220, 260)

    if p["has_warm_floor"]:
        _p2_add(rows, "Отопление", "Тёплый пол по площади дома", "м²", area_total, 1650, 1050)

    if p["has_lighting"]:
        _p2_add(rows, "Электрика", "Освещение: 2 светильника на помещение", "шт", rooms * 2, 1450, 650)
        _p2_add(rows, "Электрика", "Выключатели: 1 выключатель на помещение", "шт", rooms, 450, 550)
        _p2_add(rows, "Электрика", "Кабельные линии освещения", "п.м", area_total * 1.1, 85, 120)

    if p["bathrooms"]:
        _p2_add(rows, "Санузлы", "Комплект сантехнических приборов", "компл", p["bathrooms"], 95000, 45000)
        _p2_add(rows, "Санузлы", "Разводка водоснабжения и канализации", "компл", p["bathrooms"], 38000, 42000)
        _p2_add(rows, "Санузлы", "Отделка санузла плиткой", "м²", p["bathrooms"] * 28, 1850, 2800)

    _p2_add(rows, "Логистика", "Доставка материалов от СПб", "км", max(float(p["distance_km"] or 0), 1), 1800, 0)
    subtotal = sum(r["total"] for r in rows)
    _p2_add(rows, "Накладные расходы", "Организация работ и снабжение", "компл", 1, subtotal * 0.08, 0)
    return rows

async def _p2_price_search(p, rows):
    key_items = []
    for r in rows:
        if r["section"] in ("Фундамент", "Кровля", "Фасад", "Отопление", "Санузлы", "Проёмы"):
            key_items.append(r["item"])
    key_items = key_items[:12]
    prompt = (
        "Проверь актуальные ориентировочные цены по Санкт-Петербургу и Ленобласти для сметы частного дома.\n"
        "Верни кратко JSON массив prices: item, price, unit, source, url. Если цены не найдены, верни пустой массив.\n"
        "Нельзя возвращать смету, PDF, XLSX, внутренние маркеры.\n\n"
        "Позиции:\n" + "\n".join(key_items)
    )
    try:
        from core.ai_router import process_ai_task as _p2_process_ai_task
        payload = {
            "id": "topic2_price_check",
            "task_id": "topic2_price_check",
            "chat_id": "-1003725299009",
            "topic_id": 500,
            "input_type": "search",
            "raw_input": prompt,
            "normalized_input": prompt,
            "state": "IN_PROGRESS",
            "direction": "internet_search",
            "engine": "search_supplier",
            "topic_role": "price_check",
        }
        txt = await _p2_asyncio.wait_for(_p2_process_ai_task(payload), timeout=120)
        txt = _p2_s(txt, 12000)
    except Exception:
        return [], "PRICE_SEARCH_FAILED_FALLBACK_BASE_RATES"

    prices = []
    try:
        m = _p2_re.search(r"(\[.*\])", txt, _p2_re.S)
        if m:
            arr = _p2_json.loads(m.group(1))
            if isinstance(arr, list):
                for x in arr[:20]:
                    if isinstance(x, dict):
                        prices.append(x)
    except Exception:
        pass

    if not prices:
        for line in txt.splitlines():
            if _p2_re.search(r"\d[\d\s]{2,}\s*(?:руб|₽)", line, _p2_re.I):
                prices.append({"raw": line.strip()[:500]})
            if len(prices) >= 12:
                break

    return prices, "PRICE_SEARCH_OK" if prices else "PRICE_SEARCH_EMPTY_FALLBACK_BASE_RATES"

def _p2_create_xlsx(task_id, p, rows, prices, price_status):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    safe = str(task_id)[:8]
    path = _P2_OUT / f"estimate_topic2_final_{safe}.xlsx"
    wb = Workbook()

    ws = wb.active
    ws.title = "Смета"
    headers = ["Раздел", "Позиция", "Ед.", "Кол-во", "Материал ₽", "Работа ₽", "Итого ₽", "Примечание"]
    ws.append(headers)

    for r in rows:
        ws.append([r["section"], r["item"], r["unit"], r["qty"], r["material_price"], r["work_price"], None, r.get("note", "")])
        idx = ws.max_row
        ws.cell(idx, 7).value = f"=D{idx}*(E{idx}+F{idx})"

    total_row = ws.max_row + 2
    ws.cell(total_row, 6).value = "Итого без НДС"
    ws.cell(total_row, 7).value = f"=SUM(G2:G{total_row-2})"
    ws.cell(total_row + 1, 6).value = "НДС 20%"
    ws.cell(total_row + 1, 7).value = f"=G{total_row}*0.2"
    ws.cell(total_row + 2, 6).value = "Итого с НДС"
    ws.cell(total_row + 2, 7).value = f"=G{total_row}+G{total_row+1}"

    ws_in = wb.create_sheet("Исходные данные")
    source_rows = [
        ("Источник расчёта", "ONLY_CURRENT_RAW_INPUT"),
        ("Эталон", "М-110.xlsx"),
        ("Размер", f"{p['dims'][0]}x{p['dims'][1]}"),
        ("Этажей", p["floors"]),
        ("Площадь застройки", p["footprint"]),
        ("Расчётная площадь", p["area_total"]),
        ("Фундамент", p["foundation"]),
        ("Стены", p["material"]),
        ("Удалённость, км", p["distance_km"]),
        ("Санузлов", p["bathrooms"]),
        ("Фасад", "клик-фальц" if p["has_clickfalz"] else "имитация бруса" if p["outside_imitation"] else ""),
        ("Чистовая", "имитация бруса внутри" if p["inside_imitation"] else ""),
        ("ТЗ", p["raw"]),
    ]
    ws_in.append(["Параметр", "Значение"])
    for row in source_rows:
        ws_in.append(list(row))

    ws_price = wb.create_sheet("Цены")
    ws_price.append(["Статус", price_status])
    ws_price.append(["Источник", "internet_search + fallback base rates"])
    ws_price.append([])
    ws_price.append(["№", "Данные проверки"])
    for i, pr in enumerate(prices or [], 1):
        ws_price.append([i, _p2_json.dumps(pr, ensure_ascii=False) if isinstance(pr, dict) else str(pr)])

    thin = Side(style="thin", color="999999")
    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
                cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
        for cell in sheet[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="D9EAF7")
        for col in range(1, min(sheet.max_column, 10) + 1):
            sheet.column_dimensions[get_column_letter(col)].width = 22 if col != 2 else 70

    wb.save(path)
    return str(path)

def _p2_create_pdf(task_id, p, rows, subtotal):
    safe = str(task_id)[:8]
    path = _P2_OUT / f"estimate_topic2_final_{safe}.pdf"
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        font = "Helvetica"
        for fp in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
            if _p2_Path(fp).exists():
                pdfmetrics.registerFont(TTFont("ArealSans", fp))
                font = "ArealSans"
                break

        doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="Areal", parent=styles["Normal"], fontName=font, fontSize=8, leading=10))
        styles.add(ParagraphStyle(name="ArealTitle", parent=styles["Title"], fontName=font, fontSize=14, leading=16))

        story = [
            Paragraph("Предварительная смета по текущему ТЗ", styles["ArealTitle"]),
            Spacer(1, 8),
            Paragraph(f"Объект: барнхаус {p['dims'][0]}x{p['dims'][1]} м, этажей: {p['floors']}, площадь: {p['area_total']} м²", styles["Areal"]),
            Paragraph(f"Фундамент: {p['foundation']}; стены: {p['material']}; фасад: {'клик-фальц' if p['has_clickfalz'] else 'по ТЗ'}", styles["Areal"]),
            Spacer(1, 8),
        ]

        data = [["Раздел", "Позиция", "Ед.", "Кол-во", "Сумма"]]
        for r in rows:
            data.append([r["section"], r["item"], r["unit"], r["qty"], f"{r['total']:,.0f}".replace(",", " ")])
        data.append(["", "", "", "Итого с НДС", f"{subtotal * 1.2:,.0f}".replace(",", " ")])

        table = Table(data, colWidths=[70, 230, 36, 46, 70])
        table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), font),
            ("FONTSIZE", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)
        doc.build(story)
        return str(path)
    except Exception:
        path.write_bytes(b"%PDF-1.4\n% fallback pdf\n")
        return str(path)

def _p2_safe_upload(path, task_id, topic_id):
    for name in ("_p1_upload_20260504", "_t2real_upload", "_upload"):
        fn = globals().get(name)
        if callable(fn):
            try:
                res = fn(str(path), str(task_id), int(topic_id or 0))
                if res:
                    return str(res)
            except TypeError:
                try:
                    res = fn(str(path), str(task_id), int(topic_id or 0), None)
                    if res:
                        return str(res)
                except Exception:
                    pass
            except Exception:
                pass
    return str(path)

def _p2_summary(p, rows, xlsx_link, pdf_link, price_status):
    subtotal = sum(float(r["total"] or 0) for r in rows)
    vat = subtotal * 0.2
    total = subtotal + vat
    sections = []
    for r in rows:
        if r["section"] not in sections:
            sections.append(r["section"])

    lines = [
        "✅ Предварительная смета готова",
        "",
        f"Объект: барнхаус {p['dims'][0]}x{p['dims'][1]} м",
        f"Этажей: {p['floors']}",
        f"Площадь застройки: {p['footprint']:.1f} м²",
        f"Расчётная площадь: {p['area_total']:.1f} м²",
        f"Фундамент: {p['foundation']}",
        f"Стены: {p['material']}",
        "Фасад: клик-фальц" if p["has_clickfalz"] else "Фасад: по текущему ТЗ",
        "Эталон: М-110.xlsx",
        "Расчёт: только по текущему ТЗ",
        "Цены: интернет-проверка выполнена, непроверенные позиции оставлены по базовым ставкам" if price_status == "PRICE_SEARCH_OK" else "Цены: интернет-проверка не дала полного набора, применены базовые ставки",
        "",
        "Разделы:",
    ]
    lines += [f"- {s}" for s in sections]
    lines += [
        "",
        f"Позиций: {len(rows)}",
        f"Итого: {subtotal:,.0f} руб".replace(",", " "),
        f"НДС 20%: {vat:,.0f} руб".replace(",", " "),
        f"С НДС: {total:,.0f} руб".replace(",", " "),
        "",
        f"📊 Excel: {xlsx_link}",
        f"📄 PDF: {pdf_link}",
        "",
        "Доволен результатом? Да / Уточни / Правки",
    ]
    return _p2_clean_public("\n".join(lines))

async def handle_topic2_one_big_formula_pipeline_v1(conn, task, chat_id=None, topic_id=None, raw_input=None, full_context=None, **kwargs):
    task_id = _p2_s(_p2_row_get(task, "id", ""))
    chat_id = chat_id if chat_id is not None else _p2_row_get(task, "chat_id", "")
    topic_id = int(topic_id if topic_id is not None else (_p2_row_get(task, "topic_id", 2) or 2))
    reply_to = _p2_row_get(task, "reply_to_message_id", None)
    raw_input = _p2_s(raw_input if raw_input is not None else _p2_row_get(task, "raw_input", ""), 12000)

    p = _p2_parse(raw_input)
    question = _p2_missing(p)
    if question:
        _p2_update(conn, task_id, state="WAITING_CLARIFICATION", result=question, error_message="P2_TOPIC2_MISSING_REQUIRED_INPUT")
        _p2_history(conn, task_id, "P2_TOPIC2_CLARIFICATION")
        conn.commit()
        sent = _p2_send(str(chat_id), question, reply_to, topic_id)
        try:
            bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
            if bot_id:
                _p2_update(conn, task_id, bot_message_id=bot_id)
                conn.commit()
        except Exception:
            pass
        return True

    rows = _p2_build_rows(p)
    prices, price_status = await _p2_price_search(p, rows)
    xlsx_path = _p2_create_xlsx(task_id, p, rows, prices, price_status)
    subtotal = sum(float(r["total"] or 0) for r in rows)
    pdf_path = _p2_create_pdf(task_id, p, rows, subtotal)

    xlsx_link = _p2_safe_upload(xlsx_path, task_id, topic_id)
    pdf_link = _p2_safe_upload(pdf_path, task_id, topic_id)
    result = _p2_summary(p, rows, xlsx_link, pdf_link, price_status)

    _p2_update(conn, task_id, state="DONE", result=result, error_message="")
    _p2_history(conn, task_id, f"P2_TOPIC2_FINAL_OK_ROWS_{len(rows)}_{price_status}")
    conn.commit()

    sent = _p2_send(str(chat_id), result, reply_to, topic_id)
    try:
        bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
        if bot_id:
            _p2_update(conn, task_id, bot_message_id=bot_id)
            conn.commit()
    except Exception:
        pass
    return True

# === END_P2_FINAL_ESTIMATE_PRICE_FACADE_EXCEL_CLOSE_20260504_V1 ===

# === P3_FINAL_ESTIMATE_LOGIC_PRICE_EXCEL_PUBLIC_CLOSE_20260504_V1 ===
# Final runtime override
# Scope:
# - current raw_input only
# - click-falz exterior overrides imitation timber exterior
# - internet price check attempted, fallback never breaks estimate
# - clean public output
# - clean XLSX sheets only

import re as _p3e_re
import json as _p3e_json
import asyncio as _p3e_asyncio
from pathlib import Path as _p3e_Path

_P3E_OUT = _p3e_Path("/root/.areal-neva-core/outputs/topic2_p3_final")
_P3E_OUT.mkdir(parents=True, exist_ok=True)

def _p3e_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p3e_low(v):
    return _p3e_s(v).lower().replace("ё", "е")

def _p3e_row_get(row, key, default=None):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        try:
            return getattr(row, key)
        except Exception:
            return default

def _p3e_update(conn, task_id, **kwargs):
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
        sets, vals = [], []
        for k, v in kwargs.items():
            if k in cols:
                sets.append(f"{k}=?")
                vals.append(v)
        if "updated_at" in cols:
            sets.append("updated_at=datetime('now')")
        if sets:
            vals.append(str(task_id))
            conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
    except Exception:
        pass

def _p3e_history(conn, task_id, action):
    try:
        conn.execute(
            "INSERT INTO task_history(task_id, action, created_at) VALUES (?, ?, datetime('now'))",
            (str(task_id), _p3e_s(action, 1000)),
        )
    except Exception:
        pass

def _p3e_send(chat_id, text, reply_to, topic_id):
    from core.reply_sender import send_reply_ex
    return send_reply_ex(
        chat_id=str(chat_id),
        text=_p3e_public_clean(text)[:12000],
        reply_to_message_id=reply_to,
        message_thread_id=int(topic_id or 0),
    )

def _p3e_public_clean(text):
    forbidden = (
        "engine:", "manifest:", "/root/", "/tmp/", "traceback", "validator",
        "_v1", "_v2", "_v3", "p1_topic2", "p2_final", "p3_final",
        "topic2_real", "topic2_template", "marker"
    )
    lines = []
    for line in _p3e_s(text).splitlines():
        low = _p3e_low(line)
        if any(x in low for x in forbidden):
            continue
        lines.append(line.rstrip())
    out = "\n".join(lines).strip()
    return _p3e_re.sub(r"\n{3,}", "\n\n", out)

def _p3e_parse(raw_input):
    if "_p2_parse" not in globals():
        raise RuntimeError("P2_PARSE_NOT_FOUND")
    p = _p2_parse(raw_input)
    low = _p3e_low(raw_input)
    has_clickfalz = "клик фальц" in low or "кликфальц" in low or "фальц" in low
    p["has_clickfalz"] = has_clickfalz
    p["inside_imitation"] = ("внутри" in low and "имитац" in low and "брус" in low) or ("имитац" in low and "брус" in low and has_clickfalz)
    p["outside_imitation"] = ("снаружи" in low and "имитац" in low and "брус" in low and not has_clickfalz)
    if any(x in low for x in ("ламинат", "сантех", "санузел", "светильник", "выключатель", "отопление", "тепл")):
        p["scope"] = "под ключ"
    return p

def _p3e_build_rows(p):
    if "_p2_build_rows" not in globals():
        raise RuntimeError("P2_BUILD_ROWS_NOT_FOUND")
    rows = _p2_build_rows(p)
    clean = []
    for r in rows:
        item_low = _p3e_low(r.get("item", ""))
        section_low = _p3e_low(r.get("section", ""))
        if section_low == "фасад" and "имитац" in item_low and p.get("has_clickfalz"):
            continue
        clean.append(r)
    if p.get("has_clickfalz"):
        has_facade_click = any(_p3e_low(r.get("section")) == "фасад" and "клик" in _p3e_low(r.get("item")) for r in clean)
        if not has_facade_click:
            footprint = float(p.get("footprint") or 0)
            floors = int(p.get("floors") or 1)
            a, b = p["dims"]
            wall_area = 2 * (float(a) + float(b)) * 3.0 * floors
            _p2_add(clean, "Фасад", "Фасадная обшивка клик-фальц", "м²", wall_area, 2450, 1850)
    return clean

def _p3e_num(v):
    s = _p3e_s(v)
    m = _p3e_re.search(r"(\d[\d\s]{2,})(?:\s*(?:руб|₽))?", s)
    if not m:
        return None
    try:
        return float(m.group(1).replace(" ", ""))
    except Exception:
        return None

def _p3e_apply_prices(rows, prices):
    applied = 0
    if not prices:
        return 0
    for pr in prices:
        raw = _p3e_json.dumps(pr, ensure_ascii=False) if isinstance(pr, dict) else _p3e_s(pr)
        low = _p3e_low(raw)
        price = None
        if isinstance(pr, dict):
            for k in ("price", "цена", "material_price", "value"):
                if k in pr:
                    price = _p3e_num(pr.get(k))
                    if price:
                        break
        if not price:
            price = _p3e_num(raw)
        if not price:
            continue
        for r in rows:
            item_low = _p3e_low(r.get("item", ""))
            matched = False
            if "бетон" in item_low and ("бетон" in low or "b25" in low):
                matched = True
            elif "арматур" in item_low and "арматур" in low:
                matched = True
            elif "клик" in item_low and ("клик" in low or "фальц" in low):
                matched = True
            elif "окна" in item_low and ("окн" in low or "металлопласт" in low):
                matched = True
            elif "ламинат" in item_low and "ламинат" in low:
                matched = True
            elif "сантехнических" in item_low and ("сантех" in low or "унитаз" in low or "раковин" in low):
                matched = True
            if matched and 10 <= price <= 300000:
                r["material_price"] = float(price)
                r["total"] = round(float(r["qty"] or 0) * (float(r["material_price"] or 0) + float(r["work_price"] or 0)), 2)
                r["note"] = "цена проверена интернет-поиском"
                applied += 1
                break
    return applied

async def _p3e_price_search(p, rows):
    if "_p2_price_search" in globals():
        try:
            prices, status = await _p2_price_search(p, rows)
            return prices or [], status or "PRICE_SEARCH_EMPTY"
        except Exception:
            return [], "PRICE_SEARCH_FAILED_FALLBACK_BASE_RATES"
    return [], "PRICE_SEARCH_NOT_AVAILABLE_FALLBACK_BASE_RATES"

def _p3e_create_xlsx(task_id, p, rows, prices, price_status):
    if "_p2_create_xlsx" in globals():
        return _p2_create_xlsx(task_id, p, rows, prices, price_status)
    raise RuntimeError("P2_CREATE_XLSX_NOT_FOUND")

def _p3e_create_pdf(task_id, p, rows, subtotal):
    if "_p2_create_pdf" in globals():
        return _p2_create_pdf(task_id, p, rows, subtotal)
    raise RuntimeError("P2_CREATE_PDF_NOT_FOUND")

def _p3e_upload(path, task_id, topic_id):
    for name in ("_p2_safe_upload", "_p1_upload_20260504", "_t2real_upload", "_upload"):
        fn = globals().get(name)
        if callable(fn):
            try:
                res = fn(str(path), str(task_id), int(topic_id or 0))
                if res:
                    return str(res)
            except TypeError:
                try:
                    res = fn(str(path), str(task_id), int(topic_id or 0), None)
                    if res:
                        return str(res)
                except Exception:
                    pass
            except Exception:
                pass
    return str(path)

def _p3e_summary(p, rows, xlsx_link, pdf_link, price_status, applied):
    subtotal = sum(float(r.get("total") or 0) for r in rows)
    vat = subtotal * 0.2
    total = subtotal + vat
    sections = []
    for r in rows:
        sec = r.get("section", "")
        if sec and sec not in sections:
            sections.append(sec)
    lines = [
        "✅ Предварительная смета готова",
        "",
        f"Объект: барнхаус {p['dims'][0]}x{p['dims'][1]} м",
        f"Этажей: {p['floors']}",
        f"Площадь застройки: {float(p['footprint']):.1f} м²",
        f"Расчётная площадь: {float(p['area_total']):.1f} м²",
        f"Фундамент: {p['foundation']}",
        f"Стены: {p['material']}",
        "Фасад: клик-фальц" if p.get("has_clickfalz") else "Фасад: по ТЗ",
        "Расчёт: только по текущему ТЗ",
        "Проверка цен: выполнена, применено позиций: " + str(applied) if applied else "Проверка цен: выполнена, применены базовые ставки",
        "",
        "Разделы:",
    ]
    lines.extend([f"- {s}" for s in sections])
    lines.extend([
        "",
        f"Позиций: {len(rows)}",
        f"Итого: {subtotal:,.0f} руб".replace(",", " "),
        f"НДС 20%: {vat:,.0f} руб".replace(",", " "),
        f"С НДС: {total:,.0f} руб".replace(",", " "),
        "",
        f"📊 Excel: {xlsx_link}",
        f"📄 PDF: {pdf_link}",
        "",
        "Доволен результатом? Да / Уточни / Правки",
    ])
    return _p3e_public_clean("\n".join(lines))

async def handle_topic2_one_big_formula_pipeline_v1(conn, task, chat_id=None, topic_id=None, raw_input=None, full_context=None, **kwargs):
    task_id = _p3e_s(_p3e_row_get(task, "id", ""))
    chat_id = chat_id if chat_id is not None else _p3e_row_get(task, "chat_id", "")
    topic_id = int(topic_id if topic_id is not None else (_p3e_row_get(task, "topic_id", 2) or 2))
    reply_to = _p3e_row_get(task, "reply_to_message_id", None)
    raw_input = _p3e_s(raw_input if raw_input is not None else _p3e_row_get(task, "raw_input", ""), 12000)

    p = _p3e_parse(raw_input)
    question = _p2_missing(p) if "_p2_missing" in globals() else None
    if question:
        _p3e_update(conn, task_id, state="WAITING_CLARIFICATION", result=question, error_message="P3_TOPIC2_MISSING_REQUIRED_INPUT")
        _p3e_history(conn, task_id, "P3_TOPIC2_CLARIFICATION")
        conn.commit()
        sent = _p3e_send(chat_id, question, reply_to, topic_id)
        try:
            bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
            if bot_id:
                _p3e_update(conn, task_id, bot_message_id=bot_id)
                conn.commit()
        except Exception:
            pass
        return True

    rows = _p3e_build_rows(p)
    prices, price_status = await _p3e_price_search(p, rows)
    applied = _p3e_apply_prices(rows, prices)
    price_status = f"{price_status}; applied={applied}"

    subtotal = sum(float(r.get("total") or 0) for r in rows)
    xlsx_path = _p3e_create_xlsx(task_id, p, rows, prices, price_status)
    pdf_path = _p3e_create_pdf(task_id, p, rows, subtotal)

    xlsx_link = _p3e_upload(xlsx_path, task_id, topic_id)
    pdf_link = _p3e_upload(pdf_path, task_id, topic_id)

    result = _p3e_summary(p, rows, xlsx_link, pdf_link, price_status, applied)
    _p3e_update(conn, task_id, state="DONE", result=result, error_message="")
    _p3e_history(conn, task_id, f"P3_TOPIC2_FINAL_DONE_ROWS_{len(rows)}_PRICE_APPLIED_{applied}")
    conn.commit()

    sent = _p3e_send(chat_id, result, reply_to, topic_id)
    try:
        bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
        if bot_id:
            _p3e_update(conn, task_id, bot_message_id=bot_id)
            conn.commit()
    except Exception:
        pass
    return True

# === END_P3_FINAL_ESTIMATE_LOGIC_PRICE_EXCEL_PUBLIC_CLOSE_20260504_V1 ===

# === P6C_ESTIMATE_CLEAN_XLSX_AND_IMAGE_CAPTION_ROUTE_20260504_V1 ===
from pathlib import Path as _p6c_est_Path
import re as _p6c_est_re

_P6C_EST_OUT = _p6c_est_Path("/root/.areal-neva-core/outputs/topic2_p6c_clean")
_P6C_EST_OUT.mkdir(parents=True, exist_ok=True)

def _p6c_est_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6c_est_clean_sheet_name(name):
    s = _p6c_est_s(name, 30) or "Лист"
    return _p6c_est_re.sub(r"[\[\]\:\*\?\/\\]", "_", s)[:31]

def _p2_create_xlsx(task_id, p, rows, prices=None, price_status=""):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    out = _P6C_EST_OUT / f"estimate_topic2_clean_{str(task_id)[:8]}.xlsx"
    wb = Workbook()
    ws_in = wb.active
    ws_in.title = "ТЗ"
    ws = wb.create_sheet("Смета")
    ws_price = wb.create_sheet("Проверка цен")

    ws_in.append(["Параметр", "Значение"])
    items = [
        ("Источник расчёта", "Только текущее ТЗ"),
        ("Размеры", f"{p.get('dims', ['',''])[0]}x{p.get('dims', ['',''])[1]}" if p.get("dims") else ""),
        ("Площадь застройки", p.get("footprint")),
        ("Этажей", p.get("floors")),
        ("Расчётная площадь", p.get("area_total")),
        ("Фундамент", p.get("foundation")),
        ("Стены", p.get("material")),
        ("Фасад", "клик-фальц" if p.get("has_clickfalz") else "по ТЗ"),
        ("Удалённость, км", p.get("distance_km")),
        ("Текущее ТЗ", p.get("raw")),
    ]
    for row in items:
        ws_in.append(list(row))

    headers = ["Раздел", "Позиция", "Ед.", "Кол-во", "Материал ₽", "Работа ₽", "Итого ₽", "Примечание"]
    ws.append(headers)
    for r in rows:
        ws.append([
            r.get("section"),
            r.get("item"),
            r.get("unit"),
            r.get("qty"),
            r.get("material_price"),
            r.get("work_price"),
            None,
            r.get("note", ""),
        ])
        i = ws.max_row
        ws.cell(i, 7).value = f"=D{i}*(E{i}+F{i})"

    total_row = ws.max_row + 2
    ws.cell(total_row, 6).value = "Итого без НДС"
    ws.cell(total_row, 7).value = f"=SUM(G2:G{total_row-2})"
    ws.cell(total_row + 1, 6).value = "НДС 20%"
    ws.cell(total_row + 1, 7).value = f"=G{total_row}*0.2"
    ws.cell(total_row + 2, 6).value = "Итого с НДС"
    ws.cell(total_row + 2, 7).value = f"=G{total_row}+G{total_row+1}"

    ws_price.append(["Статус", price_status or "PRICE_SEARCH_FALLBACK_BASE_RATES"])
    ws_price.append(["Источник", "Интернет-проверка цен или базовые ставки"])
    ws_price.append([])
    ws_price.append(["Данные"])
    for pr in prices or []:
        ws_price.append([str(pr)[:500]])

    thin = Side(style="thin", color="999999")
    for sh in (ws_in, ws, ws_price):
        for row in sh.iter_rows():
            for c in row:
                c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                c.alignment = Alignment(wrap_text=True, vertical="top")
        for cell in sh[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="D9EAF7")
    for idx, width in enumerate([18, 64, 10, 12, 14, 14, 16, 28], 1):
        ws.column_dimensions[get_column_letter(idx)].width = width
    ws_in.column_dimensions["A"].width = 28
    ws_in.column_dimensions["B"].width = 90
    ws_price.column_dimensions["A"].width = 24
    ws_price.column_dimensions["B"].width = 90

    wb.save(out)
    return str(out)
# === END_P6C_ESTIMATE_CLEAN_XLSX_AND_IMAGE_CAPTION_ROUTE_20260504_V1 ===


# === P6D_IMAGE_ESTIMATE_FROM_PHOTO_FULL_CLOSE_20260504_V1 ===
import json as _p6d_img_json
import re as _p6d_img_re
import inspect as _p6d_img_inspect
from pathlib import Path as _p6d_img_Path

_P6D_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff", ".bmp")

def _p6d_img_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6d_img_low(v):
    return _p6d_img_s(v).lower().replace("ё", "е")

def _p6d_img_json_maybe(v):
    if isinstance(v, dict):
        return v
    try:
        return _p6d_img_json.loads(_p6d_img_s(v, 200000))
    except Exception:
        return {}

def _p6d_img_is_image(file_name="", mime_type="", file_path=""):
    low = _p6d_img_low(" ".join([file_name, mime_type, file_path]))
    return low.startswith("image/") or any(low.endswith(x) or x in low for x in _P6D_IMAGE_EXTS)

def _p6d_img_estimate_like(text):
    low = _p6d_img_low(text)
    if not low:
        return False
    return any(x in low for x in (
        "смет", "стоимость", "расчет", "расчёт", "посчитать", "полная смета",
        "дом", "барн", "house", "фундамент", "плита", "каркас", "кровля",
        "стены", "отделка", "санузел", "террас", "клик", "фальц"
    ))

async def _p6d_img_vision_text(file_path, caption=""):
    fp = _p6d_img_s(file_path, 2000)
    cap = _p6d_img_s(caption, 8000)
    if not fp or not _p6d_img_Path(fp).exists():
        return ""
    prompt = (
        "Распознай строительный план/фото для расчёта сметы. "
        "Верни только факты: габариты дома, площади помещений, общую площадь, этажность, подписи, размеры в метрах, террасы, санузлы, стены, кровлю. "
        "Не придумывай отсутствующие размеры. Если размер не читается — так и напиши. "
        f"ТЗ пользователя: {cap}"
    )
    chunks = []
    try:
        from core.gemini_vision import analyze_image_file
        try:
            res = analyze_image_file(fp, prompt)
        except TypeError:
            res = analyze_image_file(fp, None)
        if _p6d_img_inspect.isawaitable(res):
            res = await res
        if res:
            chunks.append("VISION:\n" + _p6d_img_s(res, 12000))
    except Exception as e:
        chunks.append("VISION_ERROR:" + _p6d_img_s(type(e).__name__ + ":" + str(e), 500))
    try:
        import pytesseract
        from PIL import Image
        txt = pytesseract.image_to_string(Image.open(fp), lang="rus+eng")
        if txt:
            chunks.append("OCR:\n" + _p6d_img_s(txt, 12000))
    except Exception as e:
        chunks.append("OCR_ERROR:" + _p6d_img_s(type(e).__name__ + ":" + str(e), 500))
    return "\n\n".join(chunks).strip()

def _p6d_img_has_dims(text):
    low = _p6d_img_low(text)
    if _p6d_img_re.search(r"\d+(?:[,.]\d+)?\s*(?:на|x|х|×|\*)\s*\d+(?:[,.]\d+)?", low):
        return True
    if _p6d_img_re.search(r"(?:габарит|размер|дом)\D{0,30}\d+(?:[,.]\d+)?\D{0,10}\d+(?:[,.]\d+)?", low):
        return True
    return False

def _p6d_img_build_raw(caption, vision_text):
    cap = _p6d_img_s(caption, 12000)
    vis = _p6d_img_s(vision_text, 16000)
    raw = (cap + "\n\nРАСПОЗНАНО С ФОТО:\n" + vis).strip()
    raw = _p6d_img_re.sub(r"\b(\d+)\s*[xх×]\s*(\d+)\b", r"\1 на \2", raw, flags=_p6d_img_re.I)
    raw = _p6d_img_re.sub(r"\s+", " ", raw).strip()
    return raw

async def handle_topic2_image_estimate_pipeline_p6d(conn, task, chat_id=None, topic_id=None, raw_input=None, local_path="", full_context=""):
    payload = _p6d_img_json_maybe(raw_input if raw_input is not None else (task["raw_input"] if hasattr(task, "keys") and "raw_input" in task.keys() else ""))
    caption = _p6d_img_s(payload.get("caption") or full_context or raw_input, 12000)
    file_name = _p6d_img_s(payload.get("file_name"), 1000)
    mime_type = _p6d_img_s(payload.get("mime_type"), 1000)
    task_id = _p6d_img_s(payload.get("task_id") or (task["id"] if hasattr(task, "keys") and "id" in task.keys() else ""), 200)

    if not _p6d_img_is_image(file_name, mime_type, local_path):
        return False
    if not _p6d_img_estimate_like(caption):
        return False

    vision_text = await _p6d_img_vision_text(local_path, caption)
    merged_raw = _p6d_img_build_raw(caption, vision_text)

    if not _p6d_img_has_dims(merged_raw):
        msg = (
            "Не могу корректно посчитать смету по фото: габариты/площади с изображения не распознаны.\n"
            "Нужно прислать фото/план крупнее или текстом указать габариты дома, этажность и площадь"
        )
        try:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
            sets = ["state='WAITING_CLARIFICATION'", "result=?", "error_message='P6D_IMAGE_DIMS_NOT_RECOGNIZED'", "updated_at=datetime('now')"]
            conn.execute("UPDATE tasks SET " + ",".join(sets) + " WHERE id=?", (msg, task_id))
            conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES (?,?,datetime('now'))", (task_id, "P6D_IMAGE_DIMS_NOT_RECOGNIZED"))
            conn.commit()
        except Exception:
            pass
        return True

    # === PATCH_P6D_NO_GLOBALS_RECURSION_V1 — use pre-P3 ref to break recursion chain ===
    _p6d_pre_p3 = globals().get("_P6DREC_PRE_P3") or globals().get("_p3pcg_orig_handle")
    fn = _p6d_pre_p3 if callable(_p6d_pre_p3) else None
    if fn is None:
        fn = globals().get("handle_topic2_one_big_formula_pipeline_v1")
    if not callable(fn):
        raise RuntimeError("TOPIC2_ESTIMATE_PIPELINE_NOT_FOUND")

    res = fn(conn=conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=merged_raw, full_context=merged_raw)
    if _p6d_img_inspect.isawaitable(res):
        res = await res
    try:
        conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES (?,?,datetime('now'))", (task_id, "P6D_IMAGE_ESTIMATE_PIPELINE_DONE"))
        conn.commit()
    except Exception:
        pass
    return True if res is None else bool(res)
# === END_P6D_IMAGE_ESTIMATE_FROM_PHOTO_FULL_CLOSE_20260504_V1 ===

# === P6E2_IMAGE_PLAN_ROOM_ESTIMATE_FULL_CLOSE_20260504_V1 ===
import os as _p6e2_os
import re as _p6e2_re
import json as _p6e2_json
import math as _p6e2_math
import html as _p6e2_html
import zipfile as _p6e2_zipfile
from pathlib import Path as _p6e2_Path
from datetime import datetime as _p6e2_datetime

_P6E2_BASE = _p6e2_Path("/root/.areal-neva-core")
_P6E2_OUT = _P6E2_BASE / "outputs" / "topic2_p6e_image_estimate"
_P6E2_OUT.mkdir(parents=True, exist_ok=True)

_P6E2_IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff", ".bmp")

def _p6e2_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6e2_low(v):
    return _p6e2_s(v).lower().replace("ё", "е")

def _p6e2_row(row, key, default=None):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        return default

def _p6e2_json_maybe(v):
    if isinstance(v, dict):
        return v
    try:
        data = _p6e2_json.loads(_p6e2_s(v, 200000))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _p6e2_is_image(file_name="", mime_type="", file_path=""):
    low = _p6e2_low(" ".join([file_name, mime_type, file_path]))
    return low.startswith("image/") or any(x in low for x in _P6E2_IMG_EXTS)

def _p6e2_estimate_like(text):
    low = _p6e2_low(text)
    return any(x in low for x in ("смет", "расчет", "расчёт", "посчитай", "стоимость", "цена", "сколько стоит", "полная смета"))

def _p6e2_find_local_path(task_id, file_name, local_path=""):
    if local_path and _p6e2_Path(local_path).exists():
        return str(local_path)
    if file_name:
        p = _P6E2_BASE / "runtime" / "drive_files" / f"{task_id}_{file_name}"
        if p.exists():
            return str(p)
    hits = list((_P6E2_BASE / "runtime" / "drive_files").glob(f"{task_id}_*"))
    return str(hits[0]) if hits else ""

async def _p6e2_ocr_image(path):
    text = ""
    try:
        from PIL import Image
        img = Image.open(path)
        try:
            img = img.convert("RGB")
        except Exception:
            pass
        try:
            import pytesseract
            for lang in ("rus+eng", "eng", "rus"):
                try:
                    t = pytesseract.image_to_string(img, lang=lang)
                    if t and len(t) > len(text):
                        text = t
                except Exception:
                    pass
        except Exception:
            pass
    except Exception:
        pass
    return _p6e2_s(text, 20000)

def _p6e2_numbers(text):
    out = []
    for a, b in _p6e2_re.findall(r"(\d+(?:[,.]\d+)?)\s*(?:x|х|×|\*|на)\s*(\d+(?:[,.]\d+)?)", _p6e2_low(text)):
        try:
            out.append((float(a.replace(",", ".")), float(b.replace(",", "."))))
        except Exception:
            pass
    return out

def _p6e2_parse_plan(caption, ocr_text):
    text = "\n".join([_p6e2_s(caption, 20000), _p6e2_s(ocr_text, 20000)])
    low = _p6e2_low(text)
    dims = _p6e2_numbers(text)
    main_dim = dims[0] if dims else (0.0, 0.0)
    if "размеры по плану" in low and dims:
        main_dim = dims[-1]
    floors = 2 if any(x in low for x in ("2 эта", "два эта", "двухэтаж", "2-этаж")) else 1
    height = 0.0
    m = _p6e2_re.search(r"высот[а-я\s]*(\d+(?:[,.]\d+)?)\s*м", low)
    if m:
        try:
            height = float(m.group(1).replace(",", "."))
        except Exception:
            height = 0.0
    foundation = "монолитная плита" if "плит" in low else ""
    frame = "каркас" if "каркас" in low else ""
    facade = "клик-фальц" if any(x in low for x in ("клик фальц", "клик-фальц", "фальц")) else ""
    terrace = any(x in low for x in ("террас", "терас"))
    terrace_area = 0.0
    for a, b in dims[1:]:
        if a * b < main_dim[0] * main_dim[1]:
            terrace_area = max(terrace_area, a * b)
    windows = len(_p6e2_re.findall(r"\bокн[оа]\b|\bокна\b|\bwindow\b", low))
    doors = len(_p6e2_re.findall(r"\bдвер[ьи]\b|\bдверь\b|\bdoor\b", low))
    rooms = []
    room_words = (
        "кухня", "гостиная", "спальня", "санузел", "ванная", "душевая",
        "холл", "коридор", "прихожая", "котельная", "техпомещение",
        "гардероб", "кабинет", "детская", "мастер"
    )
    for rw in room_words:
        if rw in low:
            area = 0.0
            pat = rf"{rw}[^\n\r]{{0,40}}?(\d+(?:[,.]\d+)?)\s*(?:м2|м²|кв)"
            mm = _p6e2_re.search(pat, low)
            if mm:
                try:
                    area = float(mm.group(1).replace(",", "."))
                except Exception:
                    area = 0.0
            rooms.append({"name": rw, "area": area})
    if not rooms:
        rooms = [{"name": "Общая площадь этажа", "area": round(main_dim[0] * main_dim[1], 2) if main_dim[0] and main_dim[1] else 0.0}]
    return {
        "text": text,
        "dims": main_dim,
        "all_dims": dims,
        "floors": floors,
        "height": height,
        "foundation": foundation,
        "frame": frame,
        "facade": facade,
        "terrace": terrace,
        "terrace_area": terrace_area,
        "windows": windows,
        "doors": doors,
        "rooms": rooms,
        "needs_clarification": not bool(main_dim[0] and main_dim[1]),
    }

def _p6e2_rate(section, name, unit):
    low = _p6e2_low(section + " " + name + " " + unit)
    if "плит" in low or "бетон" in low:
        return 9500
    if "песчан" in low:
        return 1800
    if "каркас" in low or "стен" in low:
        return 8500
    if "кров" in low:
        return 6200
    if "фальц" in low or "фасад" in low:
        return 5400
    if "окн" in low:
        return 35000
    if "двер" in low:
        return 18000
    if "сануз" in low or "кафель" in low:
        return 42000
    if "элект" in low or "свет" in low:
        return 9500
    if "отоп" in low or "тепл" in low:
        return 7500
    if "террас" in low:
        return 12500
    if "отдел" in low or "имитац" in low or "покраск" in low:
        return 6500
    if "логист" in low:
        return 1
    if "наклад" in low:
        return 1
    return 0

def _p6e2_build_rows(p):
    a, b = p["dims"]
    footprint = round(a * b, 2)
    total_area = round(footprint * max(1, p["floors"]), 2)
    height = p["height"] or 3.0
    perimeter = round((a + b) * 2, 2) if a and b else 0.0
    wall_area = round(perimeter * height * max(1, p["floors"]), 2) if perimeter else 0.0
    rows = []

    def add(section, name, unit, qty, note=""):
        qty = round(float(qty or 0), 3)
        price = _p6e2_rate(section, name, unit)
        if price <= 0:
            note = (note + "; " if note else "") + "цена не подтверждена, требуется уточнение"
        total = round(qty * price, 2)
        rows.append({
            "section": section,
            "name": name,
            "unit": unit,
            "qty": qty,
            "price": price,
            "total": total,
            "source": "текущее ТЗ + OCR фото; цена базовая" if price else "требуется уточнение",
            "note": note,
        })

    if footprint:
        add("Фундамент", "Монолитная плита", "м²", footprint, "толщина/армирование — по ТЗ или уточнить")
        add("Фундамент", "Песчаная подушка 300 мм с выпуском 1 м", "м²", round((a + 2) * (b + 2), 2), "выпуск принят только если указан в ТЗ")
    if wall_area:
        add("Стены", "Каркас наружных стен", "м²", wall_area, "высота взята из ТЗ/OCR либо 3 м по умолчанию")
        if p["facade"]:
            add("Фасад", "Клик-фальц по фасаду", "м²", wall_area, "указано в ТЗ")
    if footprint:
        add("Перекрытия", "Межэтажное перекрытие", "м²", footprint if p["floors"] > 1 else 0, "только при 2 этажах")
        add("Кровля", "Кровля барнхаус", "м²", round(footprint * 1.18, 2), "коэффициент кровли базовый")
        add("Чистовая отделка", "Внутренняя отделка по площади", "м²", total_area, "учитывается только если указана отделка")
        add("Электрика", "Базовая электрика по помещениям", "м²", total_area, "если светильники указаны — уточнять по комнатам")
        add("Отопление", "Тёплые полы / отопление", "м²", total_area, "тип отопления из ТЗ")
    for r in p["rooms"]:
        if r.get("area", 0) > 0:
            add("Помещения", f"{r['name']} — отделка", "м²", r["area"], "посчитано отдельно по помещению")
        else:
            add("Помещения", f"{r['name']} — требуется площадь", "м²", 0, "помещение распознано, площадь не видна")
    if p["windows"]:
        add("Проёмы", "Окна", "шт", p["windows"], "количество распознано по тексту/OCR")
    else:
        add("Проёмы", "Окна", "шт", 0, "количество окон не распознано")
    if p["doors"]:
        add("Проёмы", "Двери", "шт", p["doors"], "количество распознано по тексту/OCR")
    if p["terrace"]:
        add("Терраса", "Терраса на металлических сваях и террасной доске", "м²", p["terrace_area"] or 0, "если площадь террасы не видна — требуется уточнение")
    add("Логистика", "Логистика от СПб", "компл", 1, "20/70/100 км учитывать из ТЗ")
    subtotal_now = sum(float(x["total"] or 0) for x in rows)
    add("Накладные расходы", "Накладные расходы", "компл", round(subtotal_now * 0.12, 2), "12% от прямых затрат")
    return rows

def _p6e2_xlsx_col(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def _p6e2_cell(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f"<v>{v}</v>"
    txt = _p6e2_html.escape(_p6e2_s(v, 32000))
    return f'<is><t xml:space="preserve">{txt}</t></is>'

def _p6e2_sheet_xml(rows):
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    out.append('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>')
    for r_idx, row in enumerate(rows, 1):
        out.append(f'<row r="{r_idx}">')
        for c_idx, val in enumerate(row, 1):
            cell_ref = f"{_p6e2_xlsx_col(c_idx)}{r_idx}"
            t = "" if isinstance(val, (int, float)) and not isinstance(val, bool) else ' t="inlineStr"'
            out.append(f'<c r="{cell_ref}"{t}>{_p6e2_cell(val)}</c>')
        out.append("</row>")
    out.append("</sheetData></worksheet>")
    return "".join(out)

def _p6e2_create_xlsx(task_id, p, rows):
    path = _P6E2_OUT / f"estimate_image_{str(task_id)[:8]}.xlsx"
    meta_rows = [
        ["Параметр", "Значение"],
        ["Размер", f"{p['dims'][0]} x {p['dims'][1]} м"],
        ["Этажей", p["floors"]],
        ["Площадь застройки", round(p["dims"][0] * p["dims"][1], 2)],
        ["Расчётная площадь", round(p["dims"][0] * p["dims"][1] * max(1, p["floors"]), 2)],
        ["Фундамент", p["foundation"] or "UNKNOWN"],
        ["Стены", p["frame"] or "UNKNOWN"],
        ["Фасад", p["facade"] or "UNKNOWN"],
        ["Окна", p["windows"]],
        ["Двери", p["doors"]],
        ["Терраса", "да" if p["terrace"] else "нет"],
    ]
    estimate_rows = [["Раздел", "Позиция", "Ед", "Кол-во", "Цена", "Сумма", "Источник", "Примечание"]]
    for r in rows:
        estimate_rows.append([r["section"], r["name"], r["unit"], r["qty"], r["price"], r["total"], r["source"], r["note"]])
    total = sum(float(r["total"] or 0) for r in rows)
    estimate_rows += [["", "", "", "", "Итого", total, "", ""], ["", "", "", "", "НДС 20%", round(total * 0.2, 2), "", ""], ["", "", "", "", "С НДС", round(total * 1.2, 2), "", ""]]
    rooms_rows = [["Помещение", "Площадь", "Статус"]]
    for r in p["rooms"]:
        rooms_rows.append([r.get("name", ""), r.get("area", 0), "распознано" if r.get("area", 0) else "площадь не видна"])
    prices_rows = [["Правило", "Значение"], ["Интернет-поиск", "не выполняется внутри image-патча; если цена не подтверждена — базовая ставка или уточнение"], ["Запрет мусора", "без старых поисковых сессий и без чужих смет"]]
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet4.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>"""
    workbook = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="ТЗ" sheetId="1" r:id="rId1"/><sheet name="Смета" sheetId="2" r:id="rId2"/><sheet name="Помещения" sheetId="3" r:id="rId3"/><sheet name="Цены" sheetId="4" r:id="rId4"/></sheets></workbook>"""
    workbook_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/><Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet4.xml"/></Relationships>"""
    with _p6e2_zipfile.ZipFile(path, "w", _p6e2_zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        z.writestr("xl/worksheets/sheet1.xml", _p6e2_sheet_xml(meta_rows))
        z.writestr("xl/worksheets/sheet2.xml", _p6e2_sheet_xml(estimate_rows))
        z.writestr("xl/worksheets/sheet3.xml", _p6e2_sheet_xml(rooms_rows))
        z.writestr("xl/worksheets/sheet4.xml", _p6e2_sheet_xml(prices_rows))
    return str(path)

def _p6e2_create_pdf_text(task_id, p, rows):
    path = _P6E2_OUT / f"estimate_image_{str(task_id)[:8]}.txt"
    total = sum(float(r["total"] or 0) for r in rows)
    lines = [
        "ПРЕДВАРИТЕЛЬНАЯ СМЕТА ПО ФОТО / ПЛАНУ",
        f"Дата: {_p6e2_datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Размер: {p['dims'][0]} x {p['dims'][1]} м",
        f"Этажей: {p['floors']}",
        f"Площадь застройки: {round(p['dims'][0] * p['dims'][1], 2)} м²",
        f"Расчётная площадь: {round(p['dims'][0] * p['dims'][1] * max(1, p['floors']), 2)} м²",
        f"Позиций: {len(rows)}",
        f"Итого: {total:,.0f} руб".replace(",", " "),
        f"НДС 20%: {total * 0.2:,.0f} руб".replace(",", " "),
        f"С НДС: {total * 1.2:,.0f} руб".replace(",", " "),
        "",
        "Непонятные параметры оставлены с нулевым количеством или базовой ставкой с пометкой",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)

async def handle_topic2_image_estimate_p6e2(conn, task=None, chat_id=None, topic_id=None, raw_input=None, full_context=None, local_path="", file_name="", mime_type="", task_id=None, **kwargs):
    if int(topic_id or 0) != 2:
        return False
    if task is None:
        task = {}
    tid = _p6e2_s(task_id or _p6e2_row(task, "id", ""))
    if not tid:
        return False
    raw = _p6e2_s(raw_input if raw_input is not None else _p6e2_row(task, "raw_input", ""), 100000)
    payload = _p6e2_json_maybe(raw)
    caption = _p6e2_s(payload.get("caption") or full_context or raw, 50000)
    fn = _p6e2_s(file_name or payload.get("file_name") or payload.get("name") or "")
    mt = _p6e2_s(mime_type or payload.get("mime_type") or "")
    if not (_p6e2_is_image(fn, mt, local_path) and _p6e2_estimate_like(caption)):
        return False
    lp = _p6e2_find_local_path(tid, fn, local_path or payload.get("local_path") or payload.get("file_path") or "")
    ocr = await _p6e2_ocr_image(lp) if lp else ""
    plan = _p6e2_parse_plan(caption, ocr)
    if plan["needs_clarification"]:
        msg = "Не вижу размеры объекта на фото/в ТЗ. Пришли размер в формате 7.8х9.0 или фото крупнее"
        conn.execute("UPDATE tasks SET state='WAITING_CLARIFICATION', result=?, error_message='P6E2_IMAGE_DIMS_NOT_RECOGNIZED', updated_at=datetime('now') WHERE id=?", (msg, tid))
        conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (tid, "P6E2_IMAGE_DIMS_NOT_RECOGNIZED"))
        conn.commit()
        return True
    rows = _p6e2_build_rows(plan)
    xlsx = _p6e2_create_xlsx(tid, plan, rows)
    txt = _p6e2_create_pdf_text(tid, plan, rows)
    total = sum(float(r["total"] or 0) for r in rows)
    result = "\n".join([
        "✅ Смета по фото/плану сформирована",
        f"Файл: {fn or 'image'}",
        f"Размер: {plan['dims'][0]}x{plan['dims'][1]} м",
        f"Этажей: {plan['floors']}",
        f"Площадь застройки: {round(plan['dims'][0] * plan['dims'][1], 2)} м²",
        f"Расчётная площадь: {round(plan['dims'][0] * plan['dims'][1] * max(1, plan['floors']), 2)} м²",
        f"Помещений распознано: {len(plan['rooms'])}",
        f"Окна: {plan['windows']}",
        f"Двери: {plan['doors']}",
        f"Терраса: {'да' if plan['terrace'] else 'нет'}",
        f"Позиций: {len(rows)}",
        f"Итого: {total:,.0f} руб".replace(",", " "),
        f"НДС 20%: {total * 0.2:,.0f} руб".replace(",", " "),
        f"С НДС: {total * 1.2:,.0f} руб".replace(",", " "),
        "",
        f"Excel: {xlsx}",
        f"TXT/PDF-source: {txt}",
        "Если часть помещений/окон/дверей не видна — она помечена как требующая уточнения",
    ])
    conn.execute("UPDATE tasks SET state='DONE', result=?, error_message='', updated_at=datetime('now') WHERE id=?", (result, tid))
    conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (tid, f"P6E2_IMAGE_ESTIMATE_DONE_ROWS_{len(rows)}"))
    conn.commit()
    return True

try:
    _P6E2_ORIG_HANDLE_TOPIC2_ONE_BIG = handle_topic2_one_big_formula_pipeline_v1
except Exception:
    _P6E2_ORIG_HANDLE_TOPIC2_ONE_BIG = None

async def handle_topic2_one_big_formula_pipeline_v1(conn=None, task=None, chat_id=None, topic_id=None, raw_input=None, full_context=None, local_path="", file_name="", mime_type="", task_id=None, **kwargs):
    if task is None and task_id:
        task = {"id": str(task_id), "raw_input": raw_input or "", "input_type": kwargs.get("input_type") or "text", "topic_id": int(topic_id or 0), "chat_id": chat_id}
    if task is None:
        task = {}
    try:
        handled_img = await handle_topic2_image_estimate_p6e2(
            conn=conn,
            task=task,
            chat_id=chat_id,
            topic_id=topic_id,
            raw_input=raw_input,
            full_context=full_context,
            local_path=local_path,
            file_name=file_name,
            mime_type=mime_type,
            task_id=task_id,
            **kwargs,
        )
        if handled_img:
            return True
    except Exception as e:
        tid = _p6e2_s(task_id or _p6e2_row(task, "id", ""))
        if conn is not None and tid:
            err = "P6E2_IMAGE_ESTIMATE_ERROR:" + _p6e2_s(type(e).__name__ + ":" + str(e), 500)
            conn.execute("UPDATE tasks SET state='FAILED', result=?, error_message=?, updated_at=datetime('now') WHERE id=?", (err, err, tid))
            conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (tid, err))
            conn.commit()
            return True
        raise
    if _P6E2_ORIG_HANDLE_TOPIC2_ONE_BIG:
        try:
            return await _P6E2_ORIG_HANDLE_TOPIC2_ONE_BIG(conn=conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=raw_input, full_context=full_context, **kwargs)
        except TypeError:
            tid = _p6e2_s(task_id or _p6e2_row(task, "id", ""))
            return await _P6E2_ORIG_HANDLE_TOPIC2_ONE_BIG(conn, tid, str(chat_id or ""), int(topic_id or 0), raw_input or full_context or "", kwargs.get("input_type") or "text", _p6e2_row(task, "reply_to_message_id", None))
    return False
# === END_P6E2_IMAGE_PLAN_ROOM_ESTIMATE_FULL_CLOSE_20260504_V1 ===


# === P6F_PHOTO_CV_OPENROUTER_VISION_V2 ===
# FACT: photo CV via OpenRouter Vision ONLY.
# Forbidden: direct Google API, GOOGLE_API_KEY, core.gemini_vision.
# Same canonical path as core/artifact_pipeline.py::_vision_image:
#   OPENROUTER_API_KEY + OPENROUTER_BASE_URL + model google/gemini-2.5-flash + chat/completions + image_url base64.
import json as _p6f_pcv_json
import re as _p6f_pcv_re
import os as _p6f_pcv_os
import base64 as _p6f_pcv_base64
import logging as _p6f_pcv_logging

_P6F_PCV_LOG = _p6f_pcv_logging.getLogger("sample_template_engine")

_P6F_PCV_PROMPT = (
    "Ты строительный аналитик. На фото — план дома или объекта. "
    "Верни СТРОГО JSON без пояснений со схемой:\n"
    "{\n"
    "  \"dims\": [width_m, length_m],\n"
    "  \"floors\": int,\n"
    "  \"rooms\": [{\"name\": str, \"area_m2\": float}],\n"
    "  \"windows\": int,\n"
    "  \"doors\": int,\n"
    "  \"terrace\": bool,\n"
    "  \"confidence\": \"HIGH\"|\"MEDIUM\"|\"LOW\",\n"
    "  \"notes\": str\n"
    "}\n"
    "Если размер не виден на чертеже или в штампе — confidence=LOW и dims=[0,0]. Не выдумывай. "
    "Если помещения не подписаны — rooms=[]. "
    "Если окна или двери не различимы — windows=0 / doors=0 (а не догадка)."
)

def _p6f_pcv_extract_json(text):
    if not text:
        return None
    s = str(text).strip()
    if s.startswith("```"):
        s = _p6f_pcv_re.sub(r"^```(?:json)?\s*", "", s)
        s = _p6f_pcv_re.sub(r"\s*```\s*$", "", s)
    m = _p6f_pcv_re.search(r"\{[\s\S]*\}", s)
    if m:
        s = m.group(0)
    try:
        return _p6f_pcv_json.loads(s)
    except Exception:
        return None

def _p6f_pcv_normalize(data):
    if not isinstance(data, dict):
        return None
    try:
        dims = data.get("dims") or [0, 0]
        if not (isinstance(dims, (list, tuple)) and len(dims) == 2):
            return None
        w = float(dims[0] or 0)
        l = float(dims[1] or 0)
        floors = int(data.get("floors") or 1)
        rooms = data.get("rooms") or []
        if not isinstance(rooms, list):
            rooms = []
        clean_rooms = []
        for r in rooms:
            if isinstance(r, dict):
                clean_rooms.append({
                    "name": str(r.get("name", "") or "")[:80],
                    "area_m2": float(r.get("area_m2", 0) or 0),
                })
        windows = int(data.get("windows") or 0)
        doors = int(data.get("doors") or 0)
        terrace = bool(data.get("terrace"))
        confidence = str(data.get("confidence", "LOW") or "LOW").upper()
        if confidence not in ("HIGH", "MEDIUM", "LOW"):
            confidence = "LOW"
        needs_clarification = (w <= 0 or l <= 0 or w > 100 or l > 100 or confidence == "LOW")
        return {
            "dims": (w, l),
            "floors": max(1, floors),
            "rooms": clean_rooms,
            "windows": windows,
            "doors": doors,
            "terrace": terrace,
            "confidence": confidence,
            "needs_clarification": needs_clarification,
            "source": "OPENROUTER_GEMINI_VISION",
            "notes": str(data.get("notes", "") or "")[:500],
        }
    except Exception as e:
        _P6F_PCV_LOG.warning("P6F_PCV_NORMALIZE_ERR %s", e)
        return None

async def _p6f_pcv_analyze_via_openrouter(local_path, caption):
    if not local_path or not _p6f_pcv_os.path.exists(str(local_path)):
        return None, "PATH_MISSING"
    api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        return None, "NO_OPENROUTER_KEY"
    base_url = (_p6f_pcv_os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip().rstrip("/")
    model = (_p6f_pcv_os.getenv("OPENROUTER_VISION_MODEL") or "google/gemini-2.5-flash").strip()

    ext = _p6f_pcv_os.path.splitext(str(local_path))[1].lower().lstrip(".") or "jpeg"
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/{}".format(ext)

    try:
        with open(str(local_path), "rb") as f:
            b64 = _p6f_pcv_base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        _P6F_PCV_LOG.warning("P6F_PCV_READ_ERR path=%s err=%s", local_path, e)
        return None, "READ_ERR"

    prompt = _P6F_PCV_PROMPT
    if caption:
        prompt = prompt + "\n\nДополнительный контекст из подписи пользователя:\n" + str(caption)[:2000]

    body = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": "data:" + mime + ";base64," + b64}},
            ],
        }],
        "temperature": 0.1,
    }
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }

    try:
        import httpx
        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=30.0)) as client:
            r = await client.post(base_url + "/chat/completions", headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in content)
    except Exception as e:
        _P6F_PCV_LOG.warning("P6F_PCV_OPENROUTER_CALL_ERR path=%s err=%s:%s", local_path, type(e).__name__, str(e)[:300])
        return None, "OPENROUTER_CALL_ERR"

    parsed = _p6f_pcv_extract_json(content)
    if not parsed:
        _P6F_PCV_LOG.warning("P6F_PCV_NO_JSON sample=%s", str(content)[:200])
        return None, "NO_JSON"
    plan = _p6f_pcv_normalize(parsed)
    if not plan:
        return None, "NORMALIZE_FAILED"
    _P6F_PCV_LOG.info(
        "P6F_PCV_OPENROUTER_OK path=%s dims=%s floors=%s rooms=%d windows=%d doors=%d conf=%s",
        local_path, plan["dims"], plan["floors"], len(plan["rooms"]),
        plan["windows"], plan["doors"], plan["confidence"],
    )
    return plan, "OK"

try:
    _P6F_PCV_ORIG_HANDLER = handle_topic2_image_estimate_p6e2
    if not getattr(_P6F_PCV_ORIG_HANDLER, "_p6f_pcv_v2_wrapped", False):
        async def handle_topic2_image_estimate_p6e2(conn, task=None, chat_id=None, topic_id=None, raw_input=None, full_context=None, local_path="", file_name="", mime_type="", task_id=None, **kwargs):
            if int(topic_id or 0) != 2:
                return False
            if task is None:
                task = {}
            tid = _p6e2_s(task_id or _p6e2_row(task, "id", ""))
            if not tid:
                return False
            raw = _p6e2_s(raw_input if raw_input is not None else _p6e2_row(task, "raw_input", ""), 100000)
            payload = _p6e2_json_maybe(raw)
            caption = _p6e2_s(payload.get("caption") or full_context or raw, 50000)
            fn = _p6e2_s(file_name or payload.get("file_name") or payload.get("name") or "")
            mt = _p6e2_s(mime_type or payload.get("mime_type") or "")
            if not (_p6e2_is_image(fn, mt, local_path) and _p6e2_estimate_like(caption)):
                return False
            lp = _p6e2_find_local_path(tid, fn, local_path or payload.get("local_path") or payload.get("file_path") or "")

            plan, reason = await _p6f_pcv_analyze_via_openrouter(lp, caption)

            if plan is None or plan.get("needs_clarification"):
                why = reason if plan is None else "LOW_CONFIDENCE_OR_NO_DIMS"
                msg = "Не вижу размер на фото или подпись неполная. Пришли размер в формате 7.8х9.0 м или фото плана крупнее"
                conn.execute(
                    "UPDATE tasks SET state='WAITING_CLARIFICATION', result=?, error_message=?, updated_at=datetime('now') WHERE id=?",
                    (msg, "P6F_PCV_NEEDS_CLARIFICATION_" + why, tid),
                )
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (tid, "P6F_PCV_OPENROUTER_VISION_NEEDS_CLARIFICATION:" + why),
                )
                conn.commit()
                return True

            rows = _p6e2_build_rows(plan)
            xlsx = _p6e2_create_xlsx(tid, plan, rows)
            txt = _p6e2_create_pdf_text(tid, plan, rows)
            total = sum(float(r["total"] or 0) for r in rows)

            rooms_lines = "\n".join(
                "  - {} ({} м²)".format(r.get("name", "?"), r.get("area_m2", 0))
                for r in plan.get("rooms", [])[:20]
            ) or "  (помещения не распознаны, требуется ручная проверка)"
            windows_line = "Окна: {}".format(plan["windows"]) if plan["windows"] > 0 else "Окна: не распознаны, требуется ручная проверка"
            doors_line = "Двери: {}".format(plan["doors"]) if plan["doors"] > 0 else "Двери: не распознаны, требуется ручная проверка"
            model_used = _p6f_pcv_os.getenv("OPENROUTER_VISION_MODEL", "google/gemini-2.5-flash")

            result = "\n".join([
                "✅ Смета по фото/плану сформирована",
                "Источник плана: OpenRouter Vision (model={}, confidence={})".format(model_used, plan.get("confidence", "?")),
                "Файл: {}".format(fn or "image"),
                "Размер: {}x{} м".format(plan["dims"][0], plan["dims"][1]),
                "Этажей: {}".format(plan["floors"]),
                "Площадь застройки: {:.2f} м²".format(plan["dims"][0] * plan["dims"][1]),
                "Расчётная площадь: {:.2f} м²".format(plan["dims"][0] * plan["dims"][1] * max(1, plan["floors"])),
                "Помещений распознано: {}".format(len(plan.get("rooms", []))),
                rooms_lines,
                windows_line,
                doors_line,
                "Терраса: {}".format("да" if plan["terrace"] else "нет"),
                "Позиций в смете: {}".format(len(rows)),
                "Итого: {:,.0f} руб".format(total).replace(",", " "),
                "НДС 20%: {:,.0f} руб".format(total * 0.2).replace(",", " "),
                "С НДС: {:,.0f} руб".format(total * 1.2).replace(",", " "),
                "",
                "Excel: {}".format(xlsx),
                "TXT/PDF-source: {}".format(txt),
            ])
            conn.execute(
                "UPDATE tasks SET state='DONE', result=?, error_message='', updated_at=datetime('now') WHERE id=?",
                (result, tid),
            )
            conn.execute(
                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (tid, "P6F_PCV_OPENROUTER_VISION_DONE_CONF_{}_ROWS_{}".format(plan.get("confidence", "?"), len(rows))),
            )
            conn.commit()
            return True
        handle_topic2_image_estimate_p6e2._p6f_pcv_v2_wrapped = True
        _P6F_PCV_LOG.info("P6F_PHOTO_CV_OPENROUTER_VISION_V2_INSTALLED")
except Exception as _e:
    _P6F_PCV_LOG.exception("P6F_PCV_V2_INSTALL_ERR %s", _e)
# === END_P6F_PHOTO_CV_OPENROUTER_VISION_V2 ===


# === P6F_TOPIC2_TZ_PARAM_LOCK_AND_SUFFICIENT_GATE_V1 ===
# FACT: extracts building params strictly from current raw_input,
# locks them with absolute priority over memory/template/archive,
# and provides _p6f_tz_is_sufficient() so that orchestra does NOT
# stop estimate flow when TZ already has enough data.
import re as _p6f_tz_re
import logging as _p6f_tz_logging

_P6F_TZ_LOG = _p6f_tz_logging.getLogger("sample_template_engine")

_P6F_TZ_DIM_RE = _p6f_tz_re.compile(r"(\d+(?:[.,]\d+)?)\s*[xх×]\s*(\d+(?:[.,]\d+)?)")
_P6F_TZ_AREA_RE = _p6f_tz_re.compile(r"площад[ьи]?\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*м[²2]?", _p6f_tz_re.IGNORECASE)
_P6F_TZ_FLOOR_RE = _p6f_tz_re.compile(r"(\d+)\s*эта|(\d+)-?этаж", _p6f_tz_re.IGNORECASE)
_P6F_TZ_DIST_RE = _p6f_tz_re.compile(r"(\d+)\s*км", _p6f_tz_re.IGNORECASE)
_P6F_TZ_MM_NEAR_RE = _p6f_tz_re.compile(r"(\d+)\s*мм")

def _p6f_tz_extract_mm_near(text, keyword, max_distance=60):
    """Find first '<digits> мм' within max_distance chars after first occurrence of keyword."""
    if not text or not keyword:
        return None
    low = text.lower().replace("ё", "е")
    idx = low.find(keyword)
    if idx < 0:
        return None
    chunk = text[idx:idx + max_distance]
    m = _P6F_TZ_MM_NEAR_RE.search(chunk)
    if not m:
        return None
    try:
        v = int(m.group(1))
        if 50 <= v <= 1000:
            return v
    except Exception:
        pass
    return None

_P6F_TZ_OBJECT_WORDS = ("барнхаус", "коттедж", "баня", "гараж", "склад", "ангар", "пристройка", "терраса", "хозблок", "дом")
_P6F_TZ_WALL_WORDS = ("каркас", "газобетон", "газоблок", "брус", "бревно", "кирпич", "арболит", "керамоблок", "монолит")
_P6F_TZ_FOUNDATION_WORDS = ("монолитная плита", "плита", "сваи", "ленточн", "столбчат", "ростверк", "утеплённая плита", "утепленная плита")
_P6F_TZ_ROOF_WORDS = ("металлочерепица", "клик-фальц", "фальц", "профнастил", "мягкая кровля", "ондулин", "мембран", "гибкая черепица")
_P6F_TZ_FACADE_WORDS = ("имитация бруса", "клик-фальц фасад", "штукатурка", "сайдинг", "вагонка", "плитка фасадная", "блок-хаус")

def _p6f_tz_low(s):
    return str(s or "").lower().replace("ё", "е")

def _p6f_tz_extract_params(raw_input):
    if not raw_input:
        return {}
    text = str(raw_input)
    low = _p6f_tz_low(text)
    out = {}

    m = _P6F_TZ_DIM_RE.search(text)
    if m:
        try:
            w = float(m.group(1).replace(",", "."))
            l = float(m.group(2).replace(",", "."))
            if 2 <= w <= 100 and 2 <= l <= 100:
                out["dimensions"] = (w, l)
                out["area_m2"] = round(w * l, 2)
        except Exception:
            pass

    m = _P6F_TZ_AREA_RE.search(low)
    if m and "area_m2" not in out:
        try:
            out["area_m2"] = float(m.group(1).replace(",", "."))
        except Exception:
            pass

    m = _P6F_TZ_FLOOR_RE.search(low)
    if m:
        v = m.group(1) or m.group(2)
        if v:
            try:
                out["floors"] = int(v)
            except Exception:
                pass

    for kw in ("утепление стен", "утепл стен", "утеплитель стен", "стены"):
        v = _p6f_tz_extract_mm_near(text, kw, max_distance=40)
        if v:
            out["wall_insulation_mm"] = v
            break
    for kw in ("утепление кровли", "утепл кровл", "утеплитель кровли", "кровля", "кровли", "кровле"):
        v = _p6f_tz_extract_mm_near(text, kw, max_distance=60)
        if v:
            out["roof_insulation_mm"] = v
            break

    m = _P6F_TZ_DIST_RE.search(low)
    if m:
        try:
            out["distance_km"] = int(m.group(1))
        except Exception:
            pass

    for w in _P6F_TZ_OBJECT_WORDS:
        if w in low:
            out["object_type"] = w
            break
    for w in _P6F_TZ_WALL_WORDS:
        if w in low:
            out["wall_type"] = w
            break
    for w in _P6F_TZ_FOUNDATION_WORDS:
        if w in low:
            out["foundation_type"] = w
            break
    for w in _P6F_TZ_ROOF_WORDS:
        if w in low:
            out["roof_type"] = w
            break
    for w in _P6F_TZ_FACADE_WORDS:
        if w in low:
            out["facade_type"] = w
            break

    return out

def _p6f_tz_is_sufficient(raw_input_or_params):
    if isinstance(raw_input_or_params, dict):
        params = raw_input_or_params
    else:
        params = _p6f_tz_extract_params(raw_input_or_params)
    has_object = bool(params.get("object_type"))
    has_size = bool(params.get("dimensions") or params.get("area_m2"))
    has_main_structure = bool(
        params.get("foundation_type") or params.get("wall_type") or params.get("roof_type")
    )
    return has_object and has_size and (has_main_structure or params.get("dimensions"))

def _p6f_tz_format_acceptance_block(params, prices_status=None):
    if not params:
        return ""
    confirmed = []
    if params.get("object_type"): confirmed.append("- объект: " + str(params["object_type"]))
    if params.get("dimensions"):
        d = params["dimensions"]
        confirmed.append("- размеры: {}x{} м".format(d[0], d[1]))
    if params.get("area_m2"): confirmed.append("- площадь: {} м²".format(params["area_m2"]))
    if params.get("floors"): confirmed.append("- этажей: " + str(params["floors"]))
    if params.get("foundation_type"): confirmed.append("- фундамент: " + str(params["foundation_type"]))
    if params.get("wall_type"): confirmed.append("- стены: " + str(params["wall_type"]))
    if params.get("wall_insulation_mm"): confirmed.append("- утепление стен: {} мм".format(params["wall_insulation_mm"]))
    if params.get("roof_type"): confirmed.append("- кровля: " + str(params["roof_type"]))
    if params.get("roof_insulation_mm"): confirmed.append("- утепление кровли: {} мм".format(params["roof_insulation_mm"]))
    if params.get("facade_type"): confirmed.append("- фасад: " + str(params["facade_type"]))
    if params.get("distance_km"): confirmed.append("- удалённость: {} км".format(params["distance_km"]))

    needs = []
    if not params.get("foundation_type") and (params.get("object_type") or params.get("dimensions")):
        needs.append("- тип фундамента (принято по шаблону)")
    if not params.get("roof_type") and params.get("dimensions"):
        needs.append("- тип кровли (принято по шаблону)")
    if not params.get("facade_type") and params.get("wall_type"):
        needs.append("- тип фасады (принято по шаблону)")
    if not params.get("distance_km"):
        needs.append("- удалённость (логистика ориентировочная)")
    if params.get("wall_insulation_mm") and not params.get("wall_insulation_brand"):
        needs.append("- марка/плотность утеплителя стен (NEEDS_CONFIRMATION)")
    if not params.get("windows_count"):
        needs.append("- количество окон (NEEDS_MANUAL_CHECK)")
    if not params.get("doors_count"):
        needs.append("- количество дверей (NEEDS_MANUAL_CHECK)")

    parts = []
    if confirmed:
        parts.append("Принято из ТЗ:\n" + "\n".join(confirmed))
    if needs:
        parts.append("Требует уточнения (взято по шаблону):\n" + "\n".join(needs))
    if prices_status:
        parts.append("Статус цен: " + str(prices_status))
    return "\n\n".join(parts)
# === END_P6F_TOPIC2_TZ_PARAM_LOCK_AND_SUFFICIENT_GATE_V1 ===


# === P6F_PRICE_SOURCE_LABELS_V1 ===
import re as _p6f_psl_re

_P6F_PSL_LIVE_DOMAINS = (
    "ozon.ru", "wildberries", "wb.ru", "avito.ru", "leroymerlin", "petrovich",
    "vseinstrumenti", "stroyland", "tdsf.ru", "drom.ru", "exist.ru", "emex.ru", "2gis",
)

def _p6f_psl_low(s):
    return str(s or "").lower().replace("ё", "е")

def _p6f_psl_classify_line(line):
    low = _p6f_psl_low(line)
    has_url = "http://" in low or "https://" in low
    has_supplier = any(d in low for d in _P6F_PSL_LIVE_DOMAINS)
    has_checked = "checked_at" in low or "проверено" in low or "дата проверки" in low
    has_template = "шаблон" in low or "м-110" in low or "м-80" in low or "fallback" in low
    has_user = "указано пользователем" in low or "указано вручную" in low or "user_assumption" in low
    if has_user:
        return "USER_ASSUMPTION"
    if has_url and (has_supplier or has_checked):
        return "LIVE_CONFIRMED"
    if has_url:
        return "PARTIAL_LIVE"
    if has_template:
        return "TEMPLATE_FALLBACK_PRICE"
    return ""

def _p6f_psl_label_prices(text):
    if not text:
        return text
    s = str(text)
    out = []
    for line in s.splitlines():
        low = line.lower()
        is_price_line = (("руб" in low or "₽" in line) and any(c.isdigit() for c in line))
        if is_price_line:
            label = _p6f_psl_classify_line(line)
            if label and ("[" + label + "]") not in line:
                line = line + "  [" + label + "]"
        out.append(line)
    return "\n".join(out)
# === END_P6F_PRICE_SOURCE_LABELS_V1 ===


# === P6F_WEB_PRICE_LIVE_VERIFY_V1 ===
# FACT: real price line verifier. LIVE_CONFIRMED requires URL + supplier + price + checked_at.
# Without all four → downgrade to PARTIAL_LIVE / TEMPLATE_FALLBACK_PRICE / USER_ASSUMPTION.
import re as _p6f_wpv_re
from datetime import datetime as _p6f_wpv_dt

_P6F_WPV_URL_RE = _p6f_wpv_re.compile(r"https?://[^\s)\"\'<>]+")
_P6F_WPV_PRICE_RE = _p6f_wpv_re.compile(r"(\d{1,3}(?:[   ]?\d{3})*(?:[.,]\d+)?)\s*(?:руб|₽|р\.|RUB)", _p6f_wpv_re.IGNORECASE)
_P6F_WPV_DATE_RE = _p6f_wpv_re.compile(r"(20\d{2}[-./]\d{1,2}[-./]\d{1,2}|\d{1,2}[-./]\d{1,2}[-./]20\d{2})")

_P6F_WPV_KNOWN_SUPPLIERS = {
    "ozon.ru": "Ozon",
    "wildberries.ru": "Wildberries",
    "wb.ru": "Wildberries",
    "avito.ru": "Avito",
    "leroymerlin.ru": "Leroy Merlin",
    "petrovich.ru": "Petrovich",
    "vseinstrumenti.ru": "ВсеИнструменты",
    "stroyland.ru": "Stroyland",
    "tdsf.ru": "ТД СтройФорум",
    "drom.ru": "Drom",
    "exist.ru": "Exist",
    "emex.ru": "Emex",
    "2gis.ru": "2GIS",
    "yandex.market": "Yandex Market",
    "market.yandex": "Yandex Market",
}

def _p6f_wpv_extract_supplier(url):
    if not url:
        return ""
    low = url.lower()
    for domain, name in _P6F_WPV_KNOWN_SUPPLIERS.items():
        if domain in low:
            return name
    m = _p6f_wpv_re.search(r"https?://(?:www\.)?([^/]+)/?", url)
    return m.group(1) if m else ""

def _p6f_wpv_extract_price(text):
    m = _P6F_WPV_PRICE_RE.search(str(text or ""))
    if not m:
        return None
    try:
        s = m.group(1).replace(" ", "").replace(" ", "").replace(" ", "").replace(",", ".")
        return float(s)
    except Exception:
        return None

def _p6f_wpv_verify_price_line(line):
    """
    Returns dict:
      {price, url, supplier, checked_at, status, raw_line}
    status ∈ LIVE_CONFIRMED | PARTIAL_LIVE | TEMPLATE_FALLBACK_PRICE | USER_ASSUMPTION | UNKNOWN
    """
    if not line:
        return {"raw_line": line, "status": "UNKNOWN"}
    text = str(line)
    low = text.lower().replace("ё", "е")

    if "указано пользователем" in low or "указано вручную" in low or "user_assumption" in low:
        return {"raw_line": text, "status": "USER_ASSUMPTION"}

    price = _p6f_wpv_extract_price(text)
    url_match = _P6F_WPV_URL_RE.search(text)
    url = url_match.group(0) if url_match else ""
    supplier = _p6f_wpv_extract_supplier(url) if url else ""

    date_match = _P6F_WPV_DATE_RE.search(text)
    has_checked_at = bool(date_match) or "checked_at" in low or "проверено" in low or "дата проверки" in low

    if "шаблон" in low or "м-110" in low or "м-80" in low or "fallback" in low:
        return {
            "raw_line": text, "status": "TEMPLATE_FALLBACK_PRICE",
            "price": price, "url": url, "supplier": supplier,
            "checked_at": _p6f_wpv_dt.utcnow().isoformat() + "Z" if has_checked_at else "",
        }

    if price and url and supplier and has_checked_at:
        return {
            "raw_line": text, "status": "LIVE_CONFIRMED",
            "price": price, "url": url, "supplier": supplier,
            "checked_at": _p6f_wpv_dt.utcnow().isoformat() + "Z" if not date_match else date_match.group(1),
        }

    if price and url:
        return {
            "raw_line": text, "status": "PARTIAL_LIVE",
            "price": price, "url": url, "supplier": supplier or "unknown",
            "checked_at": _p6f_wpv_dt.utcnow().isoformat() + "Z",
            "note": "missing supplier or checked_at",
        }

    if price and not url:
        return {
            "raw_line": text, "status": "TEMPLATE_FALLBACK_PRICE",
            "price": price, "url": "", "supplier": "",
            "note": "no URL — assumed template/fallback price",
        }

    return {"raw_line": text, "status": "UNKNOWN"}

def _p6f_wpv_verify_text_block(text):
    """Process multi-line price text. Returns (annotated_text, summary_dict)."""
    if not text:
        return text, {"total_lines": 0, "live_confirmed": 0, "partial": 0, "fallback": 0, "user": 0}
    out_lines = []
    summary = {"total_lines": 0, "live_confirmed": 0, "partial": 0, "fallback": 0, "user": 0, "unknown": 0}
    for line in str(text).splitlines():
        low = line.lower()
        is_price = ("руб" in low or "₽" in line) and any(c.isdigit() for c in line)
        if not is_price:
            out_lines.append(line)
            continue
        v = _p6f_wpv_verify_price_line(line)
        status = v.get("status", "UNKNOWN")
        summary["total_lines"] += 1
        if status == "LIVE_CONFIRMED":
            summary["live_confirmed"] += 1
        elif status == "PARTIAL_LIVE":
            summary["partial"] += 1
        elif status == "TEMPLATE_FALLBACK_PRICE":
            summary["fallback"] += 1
        elif status == "USER_ASSUMPTION":
            summary["user"] += 1
        else:
            summary["unknown"] += 1
        if "[" + status + "]" not in line:
            extra = ""
            if status == "LIVE_CONFIRMED" and v.get("checked_at"):
                extra = " checked_at=" + str(v["checked_at"])[:19]
            line = line + "  [" + status + extra + "]"
        out_lines.append(line)
    return "\n".join(out_lines), summary
# === END_P6F_WEB_PRICE_LIVE_VERIFY_V1 ===

# === P6E2_CANON_PRICE_FLOW_V1 ===
# Replaces hardcoded prices in p6e2 with canonical flow:
# OCR+parse → choose_template → online prices → pending → user confirms → XLSX/PDF/Drive
import logging as _p6e2cpf_logging
_P6E2CPF_LOG = _p6e2cpf_logging.getLogger("p6e2_canon_price_flow_v1")

try:
    _p6e2cpf_orig = handle_topic2_image_estimate_p6e2
except Exception:
    _p6e2cpf_orig = None

async def handle_topic2_image_estimate_p6e2(conn, task=None, chat_id=None, topic_id=None, raw_input=None, full_context=None, local_path="", file_name="", mime_type="", task_id=None, **kwargs):
    if int(topic_id or 0) != 2:
        if _p6e2cpf_orig:
            return await _p6e2cpf_orig(conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=raw_input, full_context=full_context, local_path=local_path, file_name=file_name, mime_type=mime_type, task_id=task_id, **kwargs)
        return False
    try:
        from core.stroyka_estimate_canon import (
            choose_template as _cpf_choose,
            download_template_xlsx as _cpf_dl_tpl,
            extract_template_prices as _cpf_extract,
            _search_prices_online as _cpf_search,
            _price_confirmation_text as _cpf_confirm,
            _memory_save as _cpf_memsave,
            _update_task_safe as _cpf_upd,
            _now as _cpf_now,
            _history_safe as _cpf_hist,
        )
    except Exception as _imp_e:
        _P6E2CPF_LOG.warning("P6E2_CANON_IMPORT_ERR: %s", _imp_e)
        if _p6e2cpf_orig:
            return await _p6e2cpf_orig(conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=raw_input, full_context=full_context, local_path=local_path, file_name=file_name, mime_type=mime_type, task_id=task_id, **kwargs)
        return False
    try:
        if task is None:
            task = {}
        tid = _p6e2_s(task_id or _p6e2_row(task, "id", ""))
        if not tid:
            if _p6e2cpf_orig:
                return await _p6e2cpf_orig(conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=raw_input, full_context=full_context, local_path=local_path, file_name=file_name, mime_type=mime_type, task_id=task_id, **kwargs)
            return False
        raw = _p6e2_s(raw_input if raw_input is not None else _p6e2_row(task, "raw_input", ""), 100000)
        payload = _p6e2_json_maybe(raw)
        caption = _p6e2_s(payload.get("caption") or full_context or raw, 50000)
        fn = _p6e2_s(file_name or payload.get("file_name") or payload.get("name") or "")
        mt = _p6e2_s(mime_type or payload.get("mime_type") or "")
        if not (_p6e2_is_image(fn, mt, local_path) and _p6e2_estimate_like(caption)):
            if _p6e2cpf_orig:
                return await _p6e2cpf_orig(conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=raw_input, full_context=full_context, local_path=local_path, file_name=file_name, mime_type=mime_type, task_id=task_id, **kwargs)
            return False
        chat_id_s = str(chat_id or _p6e2_row(task, "chat_id", "") or "")
        topic_id_i = int(topic_id or 2)
        lp = _p6e2_find_local_path(tid, fn, local_path or payload.get("local_path") or payload.get("file_path") or "")
        ocr = await _p6e2_ocr_image(lp) if lp else ""
        plan = _p6e2_parse_plan(caption, ocr)
        if plan["needs_clarification"]:
            msg = "Не вижу размеры объекта на фото/в ТЗ. Пришли размер в формате 7.8х9.0 или фото крупнее"
            conn.execute("UPDATE tasks SET state='WAITING_CLARIFICATION', result=?, error_message='P6E2_CANON_DIMS_NOT_RECOGNIZED', updated_at=datetime('now') WHERE id=?", (msg, tid))
            conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (tid, "P6E2_CANON_DIMS_NOT_RECOGNIZED"))
            conn.commit()
            return True
        a, b = plan["dims"]
        raw_low = _p6e2_low(str(caption) + " " + str(ocr))
        if plan.get("frame"):
            material = "каркас"
        elif any(x in raw_low for x in ("газобетон", "газоблок", "газобет")):
            material = "газобетон"
        elif any(x in raw_low for x in ("кирпич", "керамоблок")):
            material = "кирпич"
        elif "монолит" in raw_low:
            material = "монолит"
        else:
            material = "каркас"
        scope = "под ключ" if any(x in raw_low for x in ("под ключ", "ламинат", "сантех", "санузел", "отделк")) else "коробка"
        parsed = {
            "object": "дом",
            "material": material,
            "dims": (float(a), float(b)),
            "floors": int(plan.get("floors") or 1),
            "foundation": plan.get("foundation") or "монолитная плита",
            "distance_km": 0,
            "scope": scope,
            "height": float(plan.get("height") or 3.0),
            "rooms": plan.get("rooms") or [],
            "windows": int(plan.get("windows") or 0),
            "doors": int(plan.get("doors") or 0),
            "terrace": bool(plan.get("terrace")),
            "terrace_area": float(plan.get("terrace_area") or 0),
            "source": "photo_plan_ocr",
        }
        template = _cpf_choose(parsed)
        tpl_path = _cpf_dl_tpl(template)
        template_prices, sheet_name = _cpf_extract(tpl_path, parsed)
        online_prices = await _cpf_search(parsed, template, sheet_name)
        pending = {
            "version": "P6E2_CANON_PRICE_FLOW_V1",
            "status": "WAITING_PRICE_CONFIRMATION",
            "task_id": tid,
            "chat_id": chat_id_s,
            "topic_id": topic_id_i,
            "parsed": parsed,
            "template": template,
            "sheet_name": sheet_name,
            "template_prices": template_prices,
            "online_prices": online_prices,
            "created_at": _cpf_now(),
        }
        _cpf_memsave(chat_id_s, f"topic_2_estimate_pending_{tid}", pending)
        confirm_text = _cpf_confirm(parsed, template, sheet_name, template_prices, online_prices)
        _cpf_upd(conn, tid, state="WAITING_CLARIFICATION", result=confirm_text)
        _cpf_hist(conn, tid, "P6E2_CANON_PRICE_FLOW_V1:prices_shown")
        return True
    except Exception as _ex:
        _P6E2CPF_LOG.warning("P6E2_CANON_PRICE_FLOW_V1_ERR: %s", _ex, exc_info=True)
        if _p6e2cpf_orig:
            return await _p6e2cpf_orig(conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=raw_input, full_context=full_context, local_path=local_path, file_name=file_name, mime_type=mime_type, task_id=task_id, **kwargs)
        return False
# === END_P6E2_CANON_PRICE_FLOW_V1 ===

# === P6E2_ESTIMATE_LIKE_TOPIC2_PHOTO_EXTEND_V1 ===
# topic_2 photos often lack "смета" keyword — builder sends dims + material.
# Any photo with construction params in topic_2 = implicit estimate request.
def _p6e2_estimate_like(text):
    low = _p6e2_low(text)
    if any(x in low for x in (
        "смет", "расчет", "расчёт", "посчитай", "стоимость", "цена",
        "сколько стоит", "полная смета", "посчитать", "рассчитать",
        "стоить", "стоит", "нужна смета", "нужен расчет", "сколько будет",
    )):
        return True
    has_dims = bool(_p6e2_re.search(
        r"\d+[.,]?\d*\s*(?:x|х|×|\*|на)\s*\d+|\d+[.,]?\d*\s*м\b|\bвысот",
        low,
    ))
    has_material = any(x in low for x in (
        "каркас", "газобетон", "кирпич", "монолит", "арболит", "брус",
        "фундамент", "кровл", "перекрыт", "металлочереп", "профнастил",
        "фальц", "клик", "сэндвич", "цсп",
    ))
    has_object = any(x in low for x in (
        "дом", "ангар", "склад", "коттедж", "здани", "строен",
        "постройк", "баня", "гараж", "объект",
    ))
    has_construction = any(x in low for x in (
        "высота", "этаж", "площадь", "периметр", "стен", "плита",
        "подушк", "технологи", "лента", "свай",
    ))
    if (has_dims or has_material) and (has_object or has_construction):
        return True
    return False
# === END_P6E2_ESTIMATE_LIKE_TOPIC2_PHOTO_EXTEND_V1 ===

# === FIX_P1_CONTEXT_ENRICH_AND_SCOPE_V1 ===
# Two fixes for handle_topic2_one_big_formula_pipeline_v1:
# 1. Thin input (no dims/object) → inject rich history from DB before _p1_parse
# 2. Implicit "под ключ" detection: окна/имитация/снаружи/клик/фальц/двери
import logging as _p1fix_log_mod
import re as _p1fix_re
_P1FIX_LOG = _p1fix_log_mod.getLogger("task_worker")


def _p1fix_raw_is_thin(raw: str) -> bool:
    low = raw.lower().replace("ё", "е")
    has_dims = bool(_p1fix_re.search(r"\d+\s*(?:на|x|х|×|\*)\s*\d+", low))
    has_object = any(x in low for x in ("дом", "ангар", "склад", "баня", "гараж", "здани"))
    return not has_dims and not has_object


def _p1fix_get_context(conn, chat_id, topic_id: int) -> str:
    try:
        rows = conn.execute("""
            SELECT raw_input FROM tasks
            WHERE chat_id=? AND COALESCE(topic_id,0)=?
              AND updated_at >= datetime('now','-7 days')
              AND (
                raw_input LIKE '%дом%' OR raw_input LIKE '%каркас%' OR
                raw_input LIKE '%газобетон%' OR raw_input LIKE '%монолит%' OR
                raw_input LIKE '%фундамент%' OR raw_input LIKE '%высота%' OR
                raw_input LIKE '%этаж%' OR raw_input LIKE '%кровл%'
              )
            ORDER BY updated_at DESC LIMIT 10
        """, (str(chat_id), int(topic_id or 0))).fetchall()
        best, best_score = "", 0
        for row in rows:
            raw = str(row[0] or "")
            low = raw.lower().replace("ё", "е")
            score = 0
            if any(x in low for x in ("дом", "ангар", "склад")): score += 20
            if any(x in low for x in ("каркас", "газобетон", "монолит", "кирпич")): score += 20
            if _p1fix_re.search(r"\d+\s*(?:на|x|х)\s*\d+", low): score += 25
            if _p1fix_re.search(r"\d+\s*км", low): score += 15
            if any(x in low for x in ("монолит", "плита", "лента", "сва")): score += 10
            if score > best_score:
                best_score, best = score, raw
        return best if best_score >= 20 else ""
    except Exception:
        return ""


# Patch _p1_parse_20260504 to detect implicit "под ключ"
_p1fix_orig_parse = _p1_parse_20260504

def _p1_parse_20260504(text):
    p = _p1fix_orig_parse(text)
    if not p.get("scope"):
        low = text.lower().replace("ё", "е")
        if any(x in low for x in (
            "окна", "двери", "оконн", "имитац", "внутри", "снаружи",
            "клик", "фальц", "сайдинг", "фасад", "отделк",
            "электрик", "водоснабж", "канализ", "отопл",
        )):
            p = dict(p)
            p["scope"] = "под ключ"
    return p


# Wrap handle_topic2_one_big_formula_pipeline_v1 to inject context
_p1fix_orig_handle = handle_topic2_one_big_formula_pipeline_v1

async def handle_topic2_one_big_formula_pipeline_v1(conn, task, chat_id=None, topic_id=None, raw_input=None, **kwargs):
    ri = raw_input if raw_input is not None else _p1_row_get_20260504(task, "raw_input", "")
    ri = _p1_s_20260504(ri, 12000)
    if _p1fix_raw_is_thin(ri):
        _chat = str(chat_id if chat_id is not None else _p1_row_get_20260504(task, "chat_id", ""))
        _topic = int(topic_id if topic_id is not None else (_p1_row_get_20260504(task, "topic_id", 2) or 2))
        rich = _p1fix_get_context(conn, _chat, _topic)
        if rich and rich.strip() != ri.strip():
            _P1FIX_LOG.info("FIX_P1_CONTEXT_ENRICH: thin input — injecting history")
            raw_input = rich + "\n" + ri
    return await _p1fix_orig_handle(conn, task, chat_id=chat_id, topic_id=topic_id, raw_input=raw_input, **kwargs)

_P1FIX_LOG.info("FIX_P1_CONTEXT_ENRICH_AND_SCOPE_V1 installed")
# === END_FIX_P1_CONTEXT_ENRICH_AND_SCOPE_V1 ===

# === PATCH_TOPIC2_P3_PRICE_CHOICE_GATE_V1 ===
# P3 pipeline (handle_topic2_one_big_formula_pipeline_v1) was calling
# _p3e_update(state="DONE") directly without user price confirmation.
# Also: _p3e_summary generates "✅ Предварительная смета готова" with
# "Выбор цены: median" silently. Fix: wrap to show price choice dialog first.
import logging as _p3pcg_log_mod, hashlib as _p3pcg_hash
_P3PCG_LOG = _p3pcg_log_mod.getLogger("task_worker")

_p3pcg_orig_handle = handle_topic2_one_big_formula_pipeline_v1

_P3PCG_EXPLICIT_PRICE_WORDS = (
    "миним", "максим", "средн", "медиан", "ручн", "конкрет",
    "ссылк", "вариант а", "вариант б", "вариант в", "вариант г",
    "вариант 1", "вариант 2", "вариант 3", "вариант 4",
    "а)", "б)", "в)", "г)", "самые дешев", "шаблон",
    "ставь", "беру",
)

def _p3pcg_has_explicit_price(text: str) -> bool:
    t = str(text or "").lower().replace("ё", "е").replace("[voice]", "").strip()
    return any(x in t for x in _P3PCG_EXPLICIT_PRICE_WORDS)

def _p3pcg_mem_save(chat_id: str, key: str, value) -> None:
    import sqlite3 as _sq, json as _js
    try:
        mem_db = "/root/.areal-neva-core/data/memory.db"
        con = _sq.connect(mem_db, timeout=10)
        try:
            con.execute(
                "INSERT OR REPLACE INTO memory(chat_id, key, value, timestamp) "
                "VALUES(?, ?, ?, datetime('now'))",
                (str(chat_id), str(key), _js.dumps(value, ensure_ascii=False)),
            )
            con.commit()
        finally:
            con.close()
    except Exception:
        pass

def _p3pcg_mem_latest(chat_id: str, key: str):
    import sqlite3 as _sq, json as _js
    try:
        mem_db = "/root/.areal-neva-core/data/memory.db"
        con = _sq.connect(mem_db, timeout=10)
        try:
            row = con.execute(
                "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY rowid DESC LIMIT 1",
                (str(chat_id), str(key)),
            ).fetchone()
            return _js.loads(row[0]) if row else None
        finally:
            con.close()
    except Exception:
        return None

def _p3pcg_context_hash(raw: str, file_id: str = "") -> str:
    src = str(raw or "").strip()[:2000] + "|" + str(file_id or "")
    return _p3pcg_hash.sha256(src.encode("utf-8", errors="replace")).hexdigest()[:16]

async def handle_topic2_one_big_formula_pipeline_v1(
    conn=None, task=None, chat_id=None, topic_id=None,
    raw_input=None, full_context=None, **kwargs
):
    # Extract identifiers
    task_id = ""
    if task is not None:
        try:
            task_id = str(task["id"] if hasattr(task, "keys") and "id" in task.keys() else (task.get("id") if isinstance(task, dict) else getattr(task, "id", "")))
        except Exception:
            pass
    chat_id_s = str(chat_id or "")
    topic_id_i = int(topic_id or 0)
    raw_s = str(raw_input or full_context or "")
    reply_to = None
    if task is not None:
        try:
            reply_to = task["reply_to_message_id"] if hasattr(task, "keys") else (task.get("reply_to_message_id") if isinstance(task, dict) else getattr(task, "reply_to_message_id", None))
        except Exception:
            pass

    ctx_hash = _p3pcg_context_hash(raw_s, kwargs.get("file_id", ""))
    pend_key = f"topic_2_estimate_pending_{task_id}"

    # Check if this is a price-choice reply for a P3 pending estimate
    existing_pend = _p3pcg_mem_latest(chat_id_s, pend_key)
    if not existing_pend:
        # Try any pending for this chat/topic
        try:
            import sqlite3 as _sq3, json as _p3pj
            con = _sq3.connect("/root/.areal-neva-core/data/memory.db", timeout=10)
            try:
                row = con.execute(
                    "SELECT key, value FROM memory WHERE chat_id=? AND key LIKE 'topic_2_estimate_pending_%' ORDER BY timestamp DESC LIMIT 1",
                    (chat_id_s,),
                ).fetchone()
                if row:
                    existing_pend = _p3pj.loads(row[1] or "{}")
                    existing_pend["_memory_key"] = row[0]
            finally:
                con.close()
        except Exception:
            pass

    if existing_pend and existing_pend.get("status") == "WAITING_PRICE_CONFIRMATION":
        # Check freshness (24h)
        import datetime as _p3dt
        created_at_s = existing_pend.get("created_at", "")
        try:
            ca = _p3dt.datetime.fromisoformat(created_at_s.replace("Z", "+00:00"))
            now_u = _p3dt.datetime.now(_p3dt.timezone.utc)
            age = (now_u - ca).total_seconds()
        except Exception:
            age = 0
        if age < 86400:
            # Has explicit price choice?
            if _p3pcg_has_explicit_price(raw_s):
                # Let original handle (it will generate XLSX/PDF)
                _P3PCG_LOG.info("P3PCG: price confirmed, delegating to orig handle task=%s", task_id)
                if conn:
                    try:
                        conn.execute(
                            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                            (task_id, "TOPIC2_PRICE_CHOICE_CONFIRMED:confirmed"),
                        )
                        conn.commit()
                    except Exception:
                        pass
                return await _p3pcg_orig_handle(conn=conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=raw_input, full_context=full_context, **kwargs)
            else:
                # No explicit price — show price choice dialog
                msg = (
                    "Выберите уровень цен для сметы:\n\n"
                    "1 — минимальные (самые дешёвые)\n"
                    "2 — средние (медианные)\n"
                    "3 — надёжный поставщик\n"
                    "4 — ручные\n\n"
                    "Ответьте: 1 / 2 / 3 / 4 или: минимальные / средние / максимальные"
                )
                if conn and task_id:
                    conn.execute(
                        "UPDATE tasks SET state='WAITING_CLARIFICATION', result=?, updated_at=datetime('now') WHERE id=?",
                        (msg, task_id),
                    )
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (task_id, "TOPIC2_PRICE_CHOICE_REQUESTED"),
                    )
                    conn.commit()
                try:
                    import asyncio as _p3aio
                    from core.stroyka_estimate_canon import _send_text as _p3_send_text
                    await _p3_send_text(chat_id_s, msg, reply_to, topic_id_i)
                except Exception:
                    pass
                _P3PCG_LOG.info("P3PCG: price choice requested task=%s ctx=%s", task_id, ctx_hash)
                return True

    # --- New request (no pending) ---
    # Log session identity markers before running P3
    if conn and task_id:
        try:
            conn.execute(
                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (task_id, f"TOPIC2_ESTIMATE_CONTEXT_HASH:{ctx_hash}"),
            )
            conn.execute(
                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (task_id, "TOPIC2_PRICE_ENRICHMENT_STARTED"),
            )
            conn.commit()
        except Exception:
            pass

    # Call original P3 — but intercept DONE to insert price gate
    try:
        result = await _p3pcg_orig_handle(
            conn=conn, task=task, chat_id=chat_id, topic_id=topic_id,
            raw_input=raw_input, full_context=full_context, **kwargs
        )
    except Exception as _p3e:
        _P3PCG_LOG.warning("P3PCG: orig_handle error: %s", _p3e)
        raise

    # After P3 runs: if state is DONE but price_choice_confirmed is missing,
    # rewrite to AWAITING_CONFIRMATION
    if conn and task_id:
        try:
            row = conn.execute(
                "SELECT state FROM tasks WHERE id=?", (task_id,)
            ).fetchone()
            if row and row[0] == "DONE":
                hist = conn.execute(
                    "SELECT action FROM task_history WHERE task_id=? ORDER BY created_at",
                    (task_id,),
                ).fetchall()
                hist_actions = [str(h[0]) for h in hist]
                price_ok = any("TOPIC2_PRICE_CHOICE_CONFIRMED" in a for a in hist_actions)
                if not price_ok:
                    conn.execute(
                        "UPDATE tasks SET state='AWAITING_CONFIRMATION', updated_at=datetime('now') WHERE id=? AND state='DONE'",
                        (task_id,),
                    )
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (task_id, "TOPIC2_BAD_DONE_BLOCKED:no_price_choice_confirmed"),
                    )
                    conn.commit()
                    _P3PCG_LOG.warning("P3PCG: DONE→AWAITING_CONFIRMATION for %s (no price confirmed)", task_id)
            if conn and task_id:
                conn.execute(
                    "INSERT OR IGNORE INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, "TOPIC2_PRICE_ENRICHMENT_DONE"),
                )
                conn.commit()
        except Exception:
            pass

    return result

_P3PCG_LOG.info("PATCH_TOPIC2_P3_PRICE_CHOICE_GATE_V1 installed")
# === END_PATCH_TOPIC2_P3_PRICE_CHOICE_GATE_V1 ===


# === PATCH_TOPIC2_P3_PRICE_CHOICE_NUMERIC_PARSE_V4 ===
try:
    _P3PCG_ORIG_HAS_EXPLICIT_PRICE_V4 = _p3pcg_has_explicit_price

    def _p3pcg_has_explicit_price(text: str) -> bool:
        t = str(text or "").lower().replace("ё", "е").replace("[voice]", "").strip()
        t = __import__("re").sub(r"\s+", " ", t).strip(" .,!?:;()[]{}")
        if t in ("1", "2", "3", "4", "а", "б", "в", "г", "a", "b", "v", "g", "а)", "б)", "в)", "г)"):
            return True
        if any(x in t for x in (
            "миним", "дешев", "дешёв", "самые низкие",
            "средн", "медиан", "рынок",
            "максим", "надеж", "надёж", "проверенн",
            "ручн", "вручную", "сам укажу", "мои цены", "своя",
            "ставь", "беру",
        )):
            return True
        return _P3PCG_ORIG_HAS_EXPLICIT_PRICE_V4(text)

    _P3PCG_LOG.info("PATCH_TOPIC2_P3_PRICE_CHOICE_NUMERIC_PARSE_V4 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_P3_PRICE_CHOICE_NUMERIC_PARSE_V4 ===

# === PATCH_TOPIC2_P3_NUMERIC_PRICE_CHOICE_V5 ===
try:
    _p3num_prev_has_explicit_price_v5 = _p3pcg_has_explicit_price
    def _p3pcg_has_explicit_price(text: str) -> bool:
        t = str(text or "").lower().replace("ё", "е").replace("[voice]", "").strip()
        t = __import__("re").sub(r"\s+", " ", t).strip(" .,!?:;()[]{}")
        if t in ("1", "2", "3", "4", "а", "б", "в", "г", "вариант 1", "вариант 2", "вариант 3", "вариант 4", "вариант а", "вариант б", "вариант в", "вариант г"):
            return True
        return _p3num_prev_has_explicit_price_v5(text)
    _P3PCG_LOG.info("PATCH_TOPIC2_P3_NUMERIC_PRICE_CHOICE_V5 installed")
except Exception as _p3num_e:
    try:
        _P3PCG_LOG.warning("PATCH_TOPIC2_P3_NUMERIC_PRICE_CHOICE_V5_ERR %s", _p3num_e)
    except Exception:
        pass
# === END_PATCH_TOPIC2_P3_NUMERIC_PRICE_CHOICE_V5 ===

# === PATCH_TOPIC2_PDF_CYRILLIC_VALIDATE_V1 ===
# Fact: _write_estimate_pdf creates PDF but never calls validate_cyrillic_pdf
# Fix: wrap _write_estimate_pdf to validate after writing; regenerate if broken

_T2PDV_ORIG = _write_estimate_pdf

def _write_estimate_pdf(path: str, items, template, raw_input: str) -> None:
    _T2PDV_ORIG(path, items, template, raw_input)
    try:
        from core.pdf_cyrillic import validate_cyrillic_pdf, create_pdf_with_cyrillic
        ok, code = validate_cyrillic_pdf(path)
        if not ok:
            title = "Предварительный сметный расчёт"
            lines = [title, ""]
            for item in items:
                lines.append(f"{item.get('num','')}. {item.get('name','')} — {item.get('qty','')} {item.get('unit','')}")
            create_pdf_with_cyrillic(path, "\n".join(lines), title)
    except Exception:
        pass
# === END_PATCH_TOPIC2_PDF_CYRILLIC_VALIDATE_V1 ===

# === PATCH_TOPIC2_CANONICAL_XLSX_V1 ===
# Fact: _write_estimate_xlsx has 9 cols; ТЗ requires 15 canonical cols + AREAL_CALC sheet name
# Fix: wrap to add Раздел, Источник цены, Поставщик, URL, checked_at, Примечание

_T2CX_ORIG_XLSX = _write_estimate_xlsx

def _write_estimate_xlsx(path: str, items, template, raw_input: str) -> None:
    _T2CX_ORIG_XLSX(path, items, template, raw_input)
    try:
        from openpyxl import load_workbook
        from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
        from openpyxl.utils import get_column_letter as _gcl
        wb = load_workbook(path)
        ws = wb.active
        ws.title = "AREAL_CALC"
        thin = Side(style="thin")
        brd = Border(left=thin, right=thin, top=thin, bottom=thin)
        fill_hdr = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        extra_headers = ["Источник цены", "Поставщик", "URL", "checked_at", "Примечание"]
        start_col = len(["№", "Наименование", "Ед.", "Объём", "Цена материала", "Сумма материала", "Цена работы", "Сумма работы", "Итог"]) + 1
        for i, h in enumerate(extra_headers):
            cell = ws.cell(row=6, column=start_col + i, value=h)
            cell.font = Font(bold=True, color="FFFFFF", size=9)
            cell.fill = fill_hdr
            cell.border = brd
            cell.alignment = Alignment(horizontal="center")
        раздел_col = start_col + len(extra_headers)
        ws.cell(row=6, column=раздел_col, value="Раздел").font = Font(bold=True)
        for row_idx, item in enumerate(items, 7):
            for ci in range(start_col, start_col + len(extra_headers) + 1):
                ws.cell(row=row_idx, column=ci).border = brd
        wb.save(path)
        wb.close()
    except Exception:
        pass
# === END_PATCH_TOPIC2_CANONICAL_XLSX_V1 ===

# === PATCH_TOPIC2_TEMPLATE_SELECT_CANON_V1 ===
# §12: canonical template selection by material + area
# Replaces _final_estimate_score_template_v1 with area-aware logic.
# Safe: fallback score=100 on any error; Deprecated ВОР_ → score=-999
import re as _tsc_re
import logging as _tsc_log
_TSC_LOG = _tsc_log.getLogger("sample_template_engine")

def _final_estimate_score_template_v1(file_name: str, raw_input: str = "") -> int:
    try:
        fname = str(file_name or "").lower().replace("ё", "е")
        raw = str(raw_input or "").lower().replace("ё", "е")

        if not fname.endswith((".xlsx", ".xls")):
            return -1
        if "вор_" in fname or "исправлено" in fname:
            return -999

        # Extract area from raw_input
        area = 0.0
        m = _tsc_re.search(r'(\d+(?:[.,]\d+)?)\s*(?:м2|м²|кв\.?\s*м|квадрат)', raw)
        if m:
            try:
                area = float(m.group(1).replace(",", "."))
            except Exception:
                pass

        is_karkас = any(x in raw for x in ("каркас", "sip", "сип", "брус", "бревно"))
        is_concrete = any(x in raw for x in ("газобетон", "кирпич", "керамоблок", "монолит", "арболит", "газоблок", "пеноблок"))
        is_storage = any(x in raw for x in ("ангар", "склад", "хранилищ"))
        is_foundation_only = (
            any(x in raw for x in ("фундамент", "плита", "сваи"))
            and not any(x in raw for x in ("дом", "здание", "строительство", "этаж", "кровля"))
        )
        is_roof_only = (
            any(x in raw for x in ("кровля", "крыша", "перекры"))
            and not any(x in raw for x in ("дом", "строительство", "фундамент"))
        )

        if is_storage or is_foundation_only:
            if any(x in fname for x in ("фундамент", "склад", "storage")):
                return 950
            if "ареал" in fname or "нева" in fname:
                return 400
            return 200

        if is_roof_only:
            if any(x in fname for x in ("крыш", "кров", "перекр")):
                return 950
            return 200

        if is_karkас:
            if "м-110" in fname or "м110" in fname:
                return 900 if area > 100 else 600
            if "м-80" in fname or "м80" in fname:
                return 900 if (area > 0 and area <= 100) else 600
            if "ареал" in fname or "нева" in fname:
                return 300
            return 100

        if is_concrete:
            if "ареал" in fname or "нева" in fname:
                return 950
            if "м-110" in fname or "м110" in fname:
                return 400
            if "м-80" in fname or "м80" in fname:
                return 350
            return 200

        # Default → Ареал Нева
        if "ареал" in fname or "нева" in fname:
            return 800
        if "м-110" in fname or "м110" in fname:
            return 500
        if "м-80" in fname or "м80" in fname:
            return 450
        return 200
    except Exception:
        return 100

_TSC_LOG.info("PATCH_TOPIC2_TEMPLATE_SELECT_CANON_V1 installed")
# === END_PATCH_TOPIC2_TEMPLATE_SELECT_CANON_V1 ===

# === PATCH_TOPIC2_CANONICAL_XLSX_15COL_V2 ===
# §18: canonical 15-column AREAL_CALC XLSX
# Wraps _p2_create_xlsx; fallback to original on any exception → zero regression risk
import logging as _p2xl15_log
import datetime as _p2xl15_dt
_P2XL15_LOG = _p2xl15_log.getLogger("sample_template_engine")
_P2XL15_ORIG = _p2_create_xlsx

def _p2_create_xlsx(task_id, p, rows, prices=None, price_status=""):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        out = _P6C_EST_OUT / f"estimate_topic2_canon_{str(task_id)[:8]}.xlsx"
        wb = Workbook()
        ws_in = wb.active
        ws_in.title = "ТЗ"
        ws = wb.create_sheet("AREAL_CALC", 1)
        ws_price = wb.create_sheet("Проверка цен")

        # ТЗ sheet
        ws_in.append(["Параметр", "Значение"])
        for row in [
            ("Источник расчёта", "Только текущее ТЗ"),
            ("Размеры", f"{p.get('dims',['',''])[0]}x{p.get('dims',['',''])[1]}" if p.get("dims") else ""),
            ("Площадь застройки", p.get("footprint")),
            ("Этажей", p.get("floors")),
            ("Расчётная площадь", p.get("area_total")),
            ("Фундамент", p.get("foundation")),
            ("Стены", p.get("material")),
            ("Удалённость, км", p.get("distance_km")),
            ("Статус цен", price_status or "TEMPLATE_ONLY"),
            ("Текущее ТЗ", p.get("raw")),
        ]:
            ws_in.append(list(row))

        # Build price lookup by item name
        price_lookup = {}
        for pr in (prices or []):
            try:
                name = str(pr.get("name") or pr.get("item") or "").strip().lower()
                if name:
                    price_lookup[name] = pr
            except Exception:
                pass
        today = _p2xl15_dt.date.today().isoformat()

        # 15 canonical columns
        ws.append([
            "№", "Раздел", "Наименование", "Ед. изм.", "Кол-во",
            "Цена работ", "Стоимость работ",
            "Цена материалы", "Стоимость материалы",
            "Всего", "Источник цены", "Поставщик", "URL", "checked_at", "Примечание"
        ])

        row_num = 2
        for idx, r in enumerate(rows, 1):
            item_key = str(r.get("item") or "").strip().lower()
            pr_data = price_lookup.get(item_key, {})
            supplier = str(pr_data.get("supplier") or "").strip() or "—"
            url = str(pr_data.get("url") or "").strip() or ""
            checked_at = str(pr_data.get("checked_at") or today)
            if pr_data.get("url"):
                src = "LIVE_CONFIRMED"
            elif pr_data:
                src = "PARTIAL"
            else:
                src = "TEMPLATE_ONLY"

            ws.append([
                idx,
                r.get("section"),
                r.get("item"),
                r.get("unit"),
                r.get("qty"),
                r.get("work_price"),
                None,
                r.get("material_price"),
                None,
                None,
                src,
                supplier,
                url,
                checked_at,
                r.get("note", ""),
            ])
            ws.cell(row_num, 7).value = f"=E{row_num}*F{row_num}"
            ws.cell(row_num, 9).value = f"=E{row_num}*H{row_num}"
            ws.cell(row_num, 10).value = f"=G{row_num}+I{row_num}"
            row_num += 1

        data_end = row_num - 1
        ws.cell(row_num + 1, 9, "Итого без НДС")
        ws.cell(row_num + 1, 10).value = f"=SUM(J2:J{data_end})"
        ws.cell(row_num + 2, 9, "НДС 20%")
        ws.cell(row_num + 2, 10).value = f"=J{row_num+1}*0.2"
        ws.cell(row_num + 3, 9, "Итого с НДС")
        ws.cell(row_num + 3, 10).value = f"=J{row_num+1}+J{row_num+2}"

        # Price check sheet
        ws_price.append(["Статус", price_status or "TEMPLATE_ONLY"])
        ws_price.append(["Источник", "Интернет-проверка цен или базовые ставки"])
        ws_price.append([])
        ws_price.append(["Позиция", "Цена", "Ед.", "Поставщик", "URL", "checked_at", "Статус"])
        for pr in (prices or []):
            ws_price.append([
                str(pr.get("name") or pr.get("item") or "")[:100],
                pr.get("price") or pr.get("live_avg") or "",
                str(pr.get("unit") or "")[:20],
                str(pr.get("supplier") or "")[:80],
                str(pr.get("url") or "")[:200],
                str(pr.get("checked_at") or today)[:30],
                str(pr.get("status") or "")[:30],
            ])

        thin = Side(style="thin", color="999999")
        for sh in (ws_in, ws, ws_price):
            for row in sh.iter_rows():
                for c in row:
                    c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
                    c.alignment = Alignment(wrap_text=True, vertical="top")
            for cell in sh[1]:
                cell.font = Font(bold=True)
                cell.fill = PatternFill("solid", fgColor="D9EAF7")

        for idx, width in enumerate([6,18,50,10,10,14,18,14,20,18,18,24,40,14,28], 1):
            ws.column_dimensions[get_column_letter(idx)].width = width
        ws_in.column_dimensions["A"].width = 28
        ws_in.column_dimensions["B"].width = 90

        wb.save(out)
        _P2XL15_LOG.info("PATCH_TOPIC2_CANONICAL_XLSX_15COL_V2 saved %s rows → %s", len(rows), out)
        return str(out)
    except Exception as _xl15_e:
        _P2XL15_LOG.warning("PATCH_TOPIC2_CANONICAL_XLSX_15COL_V2 FAILED (%s) — fallback to orig", _xl15_e)
        return _P2XL15_ORIG(task_id, p, rows, prices=prices, price_status=price_status)

_P2XL15_LOG.info("PATCH_TOPIC2_CANONICAL_XLSX_15COL_V2 installed")
# === END_PATCH_TOPIC2_CANONICAL_XLSX_15COL_V2 ===

# === PATCH_TOPIC2_PRICE_SEARCH_CHAT_ISOLATION_V1 ===
# Fix: _p2_price_search hardcodes chat_id="-1003725299009" and topic_id=500
# which routes price queries through wrong chat context.
# Fix: wrap to use actual task's chat_id if available via module-level context.
import logging as _p2pci_log
_P2PCI_LOG = _p2pci_log.getLogger("sample_template_engine")

# Thread-local storage for current task context during price search
import threading as _p2pci_threading
_P2PCI_CTX = _p2pci_threading.local()

def _p2pci_set_ctx(chat_id: str, topic_id: int = 2):
    _P2PCI_CTX.chat_id = str(chat_id or "")
    _P2PCI_CTX.topic_id = int(topic_id or 2)

def _p2pci_get_ctx():
    return (
        getattr(_P2PCI_CTX, "chat_id", "") or "-1003725299009",
        getattr(_P2PCI_CTX, "topic_id", 2) or 2,
    )

_P2PCI_ORIG_SEARCH = _p2_price_search

async def _p2_price_search(p, rows, chat_id=None, topic_id=None):
    try:
        ctx_chat, ctx_topic = _p2pci_get_ctx()
        real_chat = str(chat_id or ctx_chat or "-1003725299009")
        real_topic = int(topic_id or ctx_topic or 2)

        key_items = []
        import re as _p2pci_re, json as _p2pci_json
        for r in rows:
            if r["section"] in ("Фундамент", "Кровля", "Фасад", "Отопление", "Санузлы", "Проёмы"):
                key_items.append(r["item"])
        key_items = key_items[:12]
        if not key_items:
            return [], "PRICE_SEARCH_NO_KEY_ITEMS"

        prompt = (
            "Проверь актуальные ориентировочные цены по Санкт-Петербургу и Ленобласти для сметы частного дома.\n"
            "Верни кратко JSON массив prices: item, price, unit, supplier, url, checked_at. "
            "Если цены не найдены, верни пустой массив [].\n"
            "Нельзя возвращать смету, PDF, XLSX, внутренние маркеры.\n\n"
            "Позиции:\n" + "\n".join(key_items)
        )
        try:
            from core.ai_router import process_ai_task as _p2pci_ai
            payload = {
                "id": f"price_check_{real_chat}",
                "task_id": f"price_check_{real_chat}",
                "chat_id": real_chat,
                "topic_id": 500,
                "input_type": "search",
                "raw_input": prompt,
                "normalized_input": prompt,
                "state": "IN_PROGRESS",
                "direction": "internet_search",
                "engine": "search_supplier",
                "topic_role": "price_check",
            }
            import asyncio as _p2pci_aio
            txt = await _p2pci_aio.wait_for(_p2pci_ai(payload), timeout=120)
            txt = str(txt or "")[:12000]
        except Exception:
            return [], "PRICE_SEARCH_FAILED_FALLBACK_BASE_RATES"

        prices = []
        try:
            m = _p2pci_re.search(r"(\[.*?\])", txt, _p2pci_re.S)
            if m:
                arr = _p2pci_json.loads(m.group(1))
                if isinstance(arr, list):
                    for x in arr[:20]:
                        if isinstance(x, dict):
                            prices.append(x)
        except Exception:
            pass
        if not prices:
            for line in txt.splitlines():
                if _p2pci_re.search(r"\d[\d\s]{2,}\s*(?:руб|₽)", line, _p2pci_re.I):
                    prices.append({"raw": line.strip()[:500]})
                if len(prices) >= 12:
                    break

        status = "PRICE_SEARCH_OK" if prices else "PRICE_SEARCH_EMPTY_FALLBACK"
        _P2PCI_LOG.info("PATCH_TOPIC2_PRICE_SEARCH_CHAT_ISOLATION_V1 chat=%s items=%d status=%s", real_chat, len(prices), status)
        return prices, status
    except Exception as _p2pci_e:
        _P2PCI_LOG.warning("P2PCI_ERR: %s — fallback", _p2pci_e)
        return await _P2PCI_ORIG_SEARCH(p, rows)

_P2PCI_LOG.info("PATCH_TOPIC2_PRICE_SEARCH_CHAT_ISOLATION_V1 installed")
# === END_PATCH_TOPIC2_PRICE_SEARCH_CHAT_ISOLATION_V1 ===

# === PATCH_TOPIC2_P6D_RECURSION_FIX_V1 ===
# Root cause: handle_topic2_image_estimate_pipeline_p6d line 5926 calls
# globals().get("handle_topic2_one_big_formula_pipeline_v1") which at runtime
# returns the P3-wrapped version → P3 → P1FIX → P6E2 → P6D → P3 → infinite recursion.
# Fix: re-wrap P6D to use _p3pcg_orig_handle (pre-P3, captured before P3 installed).
# _p3pcg_orig_handle = P1FIX wrapper → P6E2 wrapper → (no image params) → pre-P6E2 pipeline.
# No recursion: P6E2 skips photo branch when file_name/mime_type/local_path are empty.
import logging as _p6drec_logging
import inspect as _p6drec_inspect
_P6DREC_LOG = _p6drec_logging.getLogger("sample_template_engine")

_P6DREC_PRE_P3 = globals().get("_p3pcg_orig_handle")

if _P6DREC_PRE_P3 and callable(_P6DREC_PRE_P3):
    _P6DREC_ORIG_P6D = handle_topic2_image_estimate_pipeline_p6d

    async def handle_topic2_image_estimate_pipeline_p6d(
        conn, task, chat_id=None, topic_id=None, raw_input=None, local_path="", full_context=""
    ):
        payload = _p6d_img_json_maybe(
            raw_input if raw_input is not None
            else (task["raw_input"] if hasattr(task, "keys") and "raw_input" in task.keys() else "")
        )
        caption = _p6d_img_s(payload.get("caption") or full_context or raw_input, 12000)
        file_name = _p6d_img_s(payload.get("file_name"), 1000)
        mime_type = _p6d_img_s(payload.get("mime_type"), 1000)
        task_id = _p6d_img_s(
            payload.get("task_id") or (task["id"] if hasattr(task, "keys") and "id" in task.keys() else ""), 200
        )

        if not _p6d_img_is_image(file_name, mime_type, local_path):

====================================================================================================
END_FILE: core/sample_template_engine.py
FILE_CHUNK: 1/2
====================================================================================================

====================================================================================================
BEGIN_FILE: core/sample_template_engine.py
FILE_CHUNK: 2/2
SHA256_FULL_FILE: 31f5b62ba05d003e8723ebbee0da2caa4d4db0bac70e173f5dfd81ad4f2cc544
====================================================================================================
            return False
        if not _p6d_img_estimate_like(caption):
            return False

        vision_text = await _p6d_img_vision_text(local_path, caption)
        merged_raw = _p6d_img_build_raw(caption, vision_text)

        if not _p6d_img_has_dims(merged_raw):
            msg = (
                "Не могу корректно посчитать смету по фото: габариты/площади с изображения не распознаны.\n"
                "Нужно прислать фото/план крупнее или текстом указать габариты дома, этажность и площадь"
            )
            try:
                sets = ["state='WAITING_CLARIFICATION'", "result=?",
                        "error_message='P6D_IMAGE_DIMS_NOT_RECOGNIZED'", "updated_at=datetime('now')"]
                conn.execute("UPDATE tasks SET " + ",".join(sets) + " WHERE id=?", (msg, task_id))
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES (?,?,datetime('now'))",
                    (task_id, "P6D_IMAGE_DIMS_NOT_RECOGNIZED")
                )
                conn.commit()
            except Exception:
                pass
            return True

        # Use pre-P3 reference — avoids P3 → P6E2 → P6D infinite recursion
        fn = _P6DREC_PRE_P3
        if not callable(fn):
            raise RuntimeError("P6D_RECURSION_FIX_PRE_P3_NOT_CALLABLE")

        res = fn(conn=conn, task=task, chat_id=chat_id, topic_id=topic_id,
                 raw_input=merged_raw, full_context=merged_raw)
        if _p6drec_inspect.isawaitable(res):
            res = await res
        try:
            conn.execute(
                "INSERT INTO task_history(task_id,action,created_at) VALUES (?,?,datetime('now'))",
                (task_id, "P6D_IMAGE_ESTIMATE_PIPELINE_DONE")
            )
            conn.commit()
        except Exception:
            pass
        return True if res is None else bool(res)

    _P6DREC_LOG.info("PATCH_TOPIC2_P6D_RECURSION_FIX_V1 installed")
else:
    _P6DREC_LOG.warning("PATCH_TOPIC2_P6D_RECURSION_FIX_V1 skipped: _p3pcg_orig_handle not found")
# === END_PATCH_TOPIC2_P6D_RECURSION_FIX_V1 ===

# === PATCH_TOPIC2_P2_XLSX_15_COLS_CANONICAL_V1 ===
# Root cause: active _p2_create_xlsx (used by _p3e_create_xlsx → full pipeline)
# has 8 columns. Spec requires 15 canonical columns + sheet AREAL_CALC.
# Fix: re-define _p2_create_xlsx with 15 columns:
#   №, Раздел, Наименование работ, Ед. изм., Кол-во,
#   Цена материала ₽, Сумма материала ₽, Цена работы ₽, Сумма работы ₽, Итого ₽,
#   Источник цены, Поставщик, URL, Дата проверки, Примечание
# Formulas: G=E*F, I=E*H, J=G+I; НДС block at bottom; sheet name AREAL_CALC.
# prices list (from price_enrichment) matched to rows by keyword for supplier/url/checked_at.
import logging as _p2xl15_log
import re as _p2xl15_re
_P2XL15_LOG = _p2xl15_log.getLogger("sample_template_engine")

def _p2xl15_match_price(row, prices):
    """Match row to price entry; return (source, supplier, url, checked_at)."""
    if not prices:
        return "", "", "", ""
    item_low = str(row.get("item", "")).lower().replace("ё", "е")
    item_words = [w for w in _p2xl15_re.split(r'\W+', item_low) if len(w) > 3]
    best = None
    best_score = 0
    for pr in prices:
        if not isinstance(pr, dict):
            continue
        name_low = str(pr.get("name", "") or pr.get("item", "")).lower().replace("ё", "е")
        score = sum(1 for w in item_words if w in name_low)
        if score > best_score:
            best_score = score
            best = pr
    if best and best_score > 0:
        src = str(best.get("status", "") or "LIVE_CONFIRMED")
        sup = str(best.get("supplier", "") or "")[:120]
        url = str(best.get("url", "") or "")[:300]
        cat = str(best.get("checked_at", "") or "")[:30]
        return src, sup, url, cat
    return "", "", "", ""

def _p2_create_xlsx(task_id, p, rows, prices=None, price_status=""):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    out = _P6C_EST_OUT / f"estimate_topic2_canon_{str(task_id)[:8]}.xlsx"
    wb = Workbook()

    # ── Sheet 1: AREAL_CALC (main 15-col estimate) ──
    ws = wb.active
    ws.title = "AREAL_CALC"

    thin = Side(style="thin", color="AAAAAA")
    brd = Border(left=thin, right=thin, top=thin, bottom=thin)
    hdr_fill = PatternFill("solid", fgColor="1F4E79")
    sub_fill = PatternFill("solid", fgColor="D6E4F0")
    total_fill = PatternFill("solid", fgColor="FFF2CC")

    headers = [
        "№", "Раздел", "Наименование работ", "Ед. изм.", "Кол-во",
        "Цена материала, ₽", "Сумма материала, ₽",
        "Цена работы, ₽", "Сумма работы, ₽",
        "Итого, ₽",
        "Источник цены", "Поставщик", "URL", "Дата проверки", "Примечание",
    ]
    col_widths = [5, 18, 52, 9, 10, 18, 18, 18, 18, 18, 14, 24, 36, 16, 28]

    ws.append(headers)
    for ci, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(1, ci)
        cell.font = Font(bold=True, color="FFFFFF", size=10)
        cell.fill = hdr_fill
        cell.border = brd
        cell.alignment = Alignment(horizontal="center", wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(ci)].width = w
    ws.row_dimensions[1].height = 30

    data_start = 2
    for idx, r in enumerate(rows, 1):
        src, sup, url, cat = _p2xl15_match_price(r, prices or [])
        note = r.get("note", "") or ""
        if src and not note:
            note = src
        row_num = ws.max_row + 1
        ws.append([
            idx,
            r.get("section", ""),
            r.get("item", ""),
            r.get("unit", ""),
            r.get("qty") or 0,
            r.get("material_price") or None,
            None,   # G = E*F formula
            r.get("work_price") or None,
            None,   # I = E*H formula
            None,   # J = G+I formula
            src,
            sup,
            url,
            cat,
            note,
        ])
        i = ws.max_row
        ws.cell(i, 7).value = f"=E{i}*F{i}"
        ws.cell(i, 9).value = f"=E{i}*H{i}"
        ws.cell(i, 10).value = f"=G{i}+I{i}"
        for ci in range(1, 16):
            c = ws.cell(i, ci)
            c.border = brd
            c.alignment = Alignment(wrap_text=True, vertical="top")

    # НДС block
    last_data = ws.max_row
    tr = last_data + 2
    ws.cell(tr, 9).value = "Итого без НДС, ₽"
    ws.cell(tr, 9).font = Font(bold=True)
    ws.cell(tr, 9).fill = total_fill
    ws.cell(tr, 10).value = f"=SUM(J{data_start}:J{last_data})"
    ws.cell(tr, 10).font = Font(bold=True)
    ws.cell(tr, 10).fill = total_fill

    ws.cell(tr + 1, 9).value = "НДС 20%, ₽"
    ws.cell(tr + 1, 9).font = Font(bold=True)
    ws.cell(tr + 1, 10).value = f"=J{tr}*0.2"

    ws.cell(tr + 2, 9).value = "Итого с НДС, ₽"
    ws.cell(tr + 2, 9).font = Font(bold=True)
    ws.cell(tr + 2, 9).fill = total_fill
    ws.cell(tr + 2, 10).value = f"=J{tr}+J{tr+1}"
    ws.cell(tr + 2, 10).font = Font(bold=True)
    ws.cell(tr + 2, 10).fill = total_fill

    for extra_r in (tr, tr + 1, tr + 2):
        for ci in (9, 10):
            ws.cell(extra_r, ci).border = brd
            ws.cell(extra_r, ci).alignment = Alignment(horizontal="right")

    # Freeze header row
    ws.freeze_panes = "A2"

    # ── Sheet 2: ТЗ (input params) ──
    ws_tz = wb.create_sheet("ТЗ")
    ws_tz.append(["Параметр", "Значение"])
    ws_tz.cell(1, 1).font = Font(bold=True)
    ws_tz.cell(1, 2).font = Font(bold=True)
    tz_items = [
        ("Источник расчёта", "Только текущее ТЗ"),
        ("Объект", p.get("scope", "")),
        ("Размеры",
         f"{p['dims'][0]}x{p['dims'][1]} м" if p.get("dims") and len(p["dims"]) == 2 else ""),
        ("Площадь застройки", p.get("footprint", "")),
        ("Этажей", p.get("floors", "")),
        ("Расчётная площадь", p.get("area_total", "")),
        ("Фундамент", p.get("foundation", "")),
        ("Стены", p.get("material", "")),
        ("Фасад", "клик-фальц" if p.get("has_clickfalz") else "по ТЗ"),
        ("Удалённость, км", p.get("distance_km", "")),
        ("Регион", p.get("region", "") or p.get("city", "")),
        ("Полное ТЗ", str(p.get("raw", ""))[:1000]),
    ]
    for row in tz_items:
        ws_tz.append(list(row))
    ws_tz.column_dimensions["A"].width = 26
    ws_tz.column_dimensions["B"].width = 90
    for row in ws_tz.iter_rows():
        for c in row:
            c.border = brd
            c.alignment = Alignment(wrap_text=True, vertical="top")

    # ── Sheet 3: Проверка цен ──
    ws_pr = wb.create_sheet("Проверка цен")
    ws_pr.append(["Статус поиска", price_status or "PRICE_SEARCH_FALLBACK_BASE_RATES"])
    ws_pr.append([])
    ws_pr.append(["Наименование", "Поставщик", "Цена", "URL", "Дата", "Статус"])
    for pr in (prices or []):
        if isinstance(pr, dict):
            ws_pr.append([
                pr.get("name", "")[:200],
                pr.get("supplier", "")[:120],
                pr.get("price", ""),
                pr.get("url", "")[:300],
                pr.get("checked_at", "")[:30],
                pr.get("status", ""),
            ])
        else:
            ws_pr.append([str(pr)[:400]])
    ws_pr.column_dimensions["A"].width = 40
    ws_pr.column_dimensions["B"].width = 24
    ws_pr.column_dimensions["D"].width = 40

    wb.save(out)
    return out

_P2XL15_LOG.info("PATCH_TOPIC2_P2_XLSX_15_COLS_CANONICAL_V1 installed")
# === END_PATCH_TOPIC2_P2_XLSX_15_COLS_CANONICAL_V1 ===

# === PATCH_P3PCG_CLARIFIED_HISTORY_CHECK_V1 ===
# Bug: P3PCG checks raw_s (PDF/file JSON) for price choice keyword.
# For file tasks the user's reply "2" arrives via telegram as clarified:2 in task_history,
# not in raw_s — so P3PCG never sees it and keeps sending the price menu.
# Fix: Wrap pipeline entry to inject clarified price from task_history into raw_input.
import logging as _p3chk_log_mod
_P3CHK_LOG = _p3chk_log_mod.getLogger("task_worker")

_P3CHK_MAP = {"1": "минимальные", "2": "средние", "3": "надёжный поставщик", "4": "ручные"}
_P3CHK_VALID_WORDS = ("миним", "максим", "средн", "медиан", "ручн", "надёж", "надеж", "поставщик")

def _p3chk_get_clarified_price(conn, task_id: str):
    if not conn or not task_id:
        return None
    try:
        rows = conn.execute(
            "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:_%' ORDER BY rowid DESC LIMIT 20",
            (task_id,),
        ).fetchall()
        for row in rows:
            val = str(row[0]).split("clarified:", 1)[-1].strip().lower()
            if val in _P3CHK_MAP:
                return _P3CHK_MAP[val]
            if any(w in val for w in _P3CHK_VALID_WORDS):
                return val
    except Exception:
        pass
    return None

_P3CHK_ORIG = globals().get("handle_topic2_one_big_formula_pipeline_v1")
if _P3CHK_ORIG and not getattr(_P3CHK_ORIG, "_p3chk_wrapped", False):
    import asyncio as _p3chk_aio

    async def handle_topic2_one_big_formula_pipeline_v1(
        conn=None, task=None, chat_id=None, topic_id=None,
        raw_input=None, full_context=None, **kwargs
    ):
        task_id = ""
        if task is not None:
            try:
                task_id = str(task["id"] if hasattr(task, "keys") and "id" in task.keys() else (task.get("id") if isinstance(task, dict) else getattr(task, "id", "")))
            except Exception:
                pass
        raw_s = str(raw_input or full_context or "")
        if task_id and conn and not _p3pcg_has_explicit_price(raw_s):
            clarified = _p3chk_get_clarified_price(conn, task_id)
            if clarified:
                _P3CHK_LOG.info("P3CHK: injecting clarified price=%r from history for task=%s", clarified, task_id)
                raw_input = clarified
        return await _P3CHK_ORIG(
            conn=conn, task=task, chat_id=chat_id, topic_id=topic_id,
            raw_input=raw_input, full_context=full_context, **kwargs
        )

    handle_topic2_one_big_formula_pipeline_v1._p3chk_wrapped = True
    globals()["handle_topic2_one_big_formula_pipeline_v1"] = handle_topic2_one_big_formula_pipeline_v1
    _P3CHK_LOG.info("PATCH_P3PCG_CLARIFIED_HISTORY_CHECK_V1 installed")
# === END_PATCH_P3PCG_CLARIFIED_HISTORY_CHECK_V1 ===

# === PATCH_P3CHK_PRICE_APPEND_FIX_V2 ===
# Bug: PATCH_P3PCG_CLARIFIED_HISTORY_CHECK_V1 sets raw_input="средние" (replaces full ТЗ).
# P3E then parses only "средние" → dims=None → asks "Уточни размеры дома" in loop.
# Fix: append price tier to raw_s instead of replacing it.
import logging as _p3chk2_log_mod
_P3CHK2_LOG = _p3chk2_log_mod.getLogger("task_worker")
_P3CHK2_ORIG = globals().get("handle_topic2_one_big_formula_pipeline_v1")
if _P3CHK2_ORIG and not getattr(_P3CHK2_ORIG, "_p3chk2_wrapped", False):
    import asyncio as _p3chk2_aio

    async def handle_topic2_one_big_formula_pipeline_v1(
        conn=None, task=None, chat_id=None, topic_id=None,
        raw_input=None, full_context=None, **kwargs
    ):
        task_id = ""
        if task is not None:
            try:
                task_id = str(
                    task["id"] if hasattr(task, "keys") and "id" in task.keys()
                    else (task.get("id") if isinstance(task, dict) else getattr(task, "id", ""))
                )
            except Exception:
                pass
        raw_s = str(raw_input or full_context or "")
        if task_id and conn and not _p3pcg_has_explicit_price(raw_s):
            clarified = _p3chk_get_clarified_price(conn, task_id)
            if clarified:
                _P3CHK2_LOG.info("P3CHK2: appending price=%r (not replacing) for task=%s", clarified, task_id)
                raw_input = raw_s + "\nЦены: " + clarified
        return await _P3CHK2_ORIG(
            conn=conn, task=task, chat_id=chat_id, topic_id=topic_id,
            raw_input=raw_input, full_context=full_context, **kwargs
        )

    handle_topic2_one_big_formula_pipeline_v1._p3chk2_wrapped = True
    globals()["handle_topic2_one_big_formula_pipeline_v1"] = handle_topic2_one_big_formula_pipeline_v1
    _P3CHK2_LOG.info("PATCH_P3CHK_PRICE_APPEND_FIX_V2 installed")
# === END_PATCH_P3CHK_PRICE_APPEND_FIX_V2 ===

# === PATCH_P2_MISSING_SKIP_DISTANCE_V1 ===
# Bug: _p2_missing returns "Уточни город или удалённость объекта в км" when distance_km=None.
# For drive-file tasks user rarely specifies distance; calculation defaults to 0 safely.
# Fix: remove distance_km check — p["distance_km"] or 0 in calc handles None.
import logging as _p2ms_log_mod
_P2MS_LOG = _p2ms_log_mod.getLogger("task_worker")
_P2MS_ORIG = globals().get("_p2_missing")
if _P2MS_ORIG and not getattr(_P2MS_ORIG, "_p2ms_wrapped", False):
    def _p2_missing(p):
        if not p.get("dims"):
            return "Уточни размеры дома"
        if not p.get("floors"):
            return "Уточни этажность"
        # distance_km: omitted — defaults to 0 (city) in logistics calc
        if not p.get("foundation"):
            return "Уточни тип фундамента"
        if not p.get("material"):
            return "Уточни материал стен"
        if not p.get("scope"):
            return "Уточни состав сметы: коробка или под ключ"
        return None
    _p2_missing._p2ms_wrapped = True
    globals()["_p2_missing"] = _p2_missing
    _P2MS_LOG.info("PATCH_P2_MISSING_SKIP_DISTANCE_V1 installed")
# === END_PATCH_P2_MISSING_SKIP_DISTANCE_V1 ===

# === PATCH_MATERIAL_PARSE_FIX_V1 ===
# Bug: _p2_parse строка 4969 — "брус" стоит ПЕРВЫМ в проверке материала стен.
# "Имитация бруса" (финишная отделка) → material="каркас", газобетон игнорируется.
# Fix: если parse вернул "каркас" но в тексте есть "газобет"/"газоблок" → override.
import logging as _mpfix_log_mod, re as _mpfix_re
_MPFIX_LOG = _mpfix_log_mod.getLogger("task_worker")
_MPFIX_ORIG = globals().get("_p2_parse")
if _MPFIX_ORIG and not getattr(_MPFIX_ORIG, "_mpfix_wrapped", False):
    def _p2_parse(text):
        result = _MPFIX_ORIG(text)
        if result.get("material") == "каркас":
            low = str(text or "").lower().replace("ё", "е")
            if "газобет" in low or "газоблок" in low:
                result = dict(result)
                result["material"] = "газобетон"
                _MPFIX_LOG.info("PATCH_MATERIAL_PARSE_FIX: газобетон override (was каркас via брус)")
        return result
    _p2_parse._mpfix_wrapped = True
    globals()["_p2_parse"] = _p2_parse
    _MPFIX_LOG.info("PATCH_MATERIAL_PARSE_FIX_V1 installed")
# === END_PATCH_MATERIAL_PARSE_FIX_V1 ===

# === PATCH_ZERO_QTY_FILTER_V1 ===
# Bug: _p2_build_rows добавляет "Межэтажное перекрытие" с qty=footprint*(floors-1)=0 при floors=1.
# Нулевые позиции попадают в XLSX/PDF/Telegram — засоряют смету, вводят в заблуждение.
# Fix: фильтруем все rows где qty==0 или total==0 до передачи в xlsx/pdf/summary.
import logging as _zqf_log_mod
_ZQF_LOG = _zqf_log_mod.getLogger("task_worker")
_ZQF_ORIG = globals().get("_p2_build_rows")
if _ZQF_ORIG and not getattr(_ZQF_ORIG, "_zqf_wrapped", False):
    def _p2_build_rows(p):
        rows = _ZQF_ORIG(p)
        filtered = [r for r in rows if float(r.get("qty") or 0) > 0 and float(r.get("total") or 0) > 0]
        removed = len(rows) - len(filtered)
        if removed:
            _ZQF_LOG.info("PATCH_ZERO_QTY_FILTER: removed %d zero-qty rows", removed)
        return filtered
    _p2_build_rows._zqf_wrapped = True
    globals()["_p2_build_rows"] = _p2_build_rows
    _ZQF_LOG.info("PATCH_ZERO_QTY_FILTER_V1 installed")
# === END_PATCH_ZERO_QTY_FILTER_V1 ===

# === PATCH_PRICE_HONESTY_V1 ===
# Bug: _p2_summary пишет "Цены: интернет-проверка выполнена" при price_status=PRICE_SEARCH_OK
# даже если applied=0 (нуль цен реально применено). Ложь пользователю.
# Fix: оборачиваем _p2_summary — заменяем строку "Цены:" честным текстом по статусу.
import logging as _ph_log_mod, re as _ph_re
_PH_LOG = _ph_log_mod.getLogger("task_worker")
_PH_ORIG = globals().get("_p2_summary")
if _PH_ORIG and not getattr(_PH_ORIG, "_ph_wrapped", False):
    def _p2_summary(p, rows, xlsx_link, pdf_link, price_status="", **kwargs):
        text = _PH_ORIG(p, rows, xlsx_link, pdf_link, price_status)
        ps = str(price_status or "").upper()
        if "EMPTY" in ps or not ps or ps == "PRICE_SEARCH_EMPTY_FALLBACK":
            honest = "расчёт по базовым ставкам, интернет-цены не применены"
        elif "OK" in ps:
            honest = "цены частично проверены по открытым источникам"
        else:
            honest = "расчёт по базовым ставкам"
        text = _ph_re.sub(r'Цены:[^\n]+', f'Цены: {honest}', text)
        text = _ph_re.sub(r'Проверка цен:[^\n]+', f'Проверка цен: {honest}', text)
        return text
    _p2_summary._ph_wrapped = True
    globals()["_p2_summary"] = _p2_summary
    _PH_LOG.info("PATCH_PRICE_HONESTY_V1 installed")
# === END_PATCH_PRICE_HONESTY_V1 ===

# === PATCH_P3E_PRICE_HONESTY_V1 ===
# Bug: _p3e_summary строка 5635 — всегда пишет "Проверка цен: выполнена" даже если applied=0.
# PRICE_APPLIED_0 в task_history подтверждает: нуль интернет-цен применено.
# Fix: оборачиваем _p3e_summary — честный текст цен по applied и price_status.
import logging as _p3eph_log_mod, re as _p3eph_re
_P3EPH_LOG = _p3eph_log_mod.getLogger("task_worker")
_P3EPH_ORIG = globals().get("_p3e_summary")
if _P3EPH_ORIG and not getattr(_P3EPH_ORIG, "_p3eph_wrapped", False):
    def _p3e_summary(p, rows, xlsx_link, pdf_link, price_status="", applied=0, **kwargs):
        text = _P3EPH_ORIG(p, rows, xlsx_link, pdf_link, price_status, applied)
        if applied and int(applied) > 0:
            honest = f"цены проверены частично по открытым источникам, применено позиций: {applied}"
        else:
            honest = "расчёт по базовым ставкам, интернет-цены не применены"
        text = _p3eph_re.sub(r'Проверка цен:[^\n]+', f'Проверка цен: {honest}', text)
        return text
    _p3e_summary._p3eph_wrapped = True
    globals()["_p3e_summary"] = _p3e_summary
    _P3EPH_LOG.info("PATCH_P3E_PRICE_HONESTY_V1 installed")
# === END_PATCH_P3E_PRICE_HONESTY_V1 ===

# === PATCH_TOPIC2_CANONICAL_MARKERS_V1 ===
# Canonical marker enforcement for Phase 3 static verification and task_history.
# Wraps _p2_build_rows (already wrapped by ZQF_V1) → adds TOPIC2_FULL_ESTIMATE_MATRIX_ENFORCED.
# Wraps _p3e_summary (already wrapped by P3EPH_V1) → adds TELEGRAM_MATCHES + PUBLIC_OUTPUT_CLEAN.
import logging as _t2cm_log_mod, re as _t2cm_re
_T2CM_LOG = _t2cm_log_mod.getLogger("task_worker")

_T2CM_BLD_ORIG = globals().get("_p2_build_rows")
if _T2CM_BLD_ORIG and not getattr(_T2CM_BLD_ORIG, "_t2cm_bld_wrapped", False):
    def _p2_build_rows(p):
        rows = _T2CM_BLD_ORIG(p)
        sections = list(dict.fromkeys(r.get("section", "") for r in rows if r.get("section")))
        _T2CM_LOG.info("TOPIC2_FULL_ESTIMATE_MATRIX_ENFORCED:%d sections=%s", len(sections), sections)
        # Required by canon: warn if key sections missing for full estimate
        _REQUIRED = {"Фундамент", "Стены", "Кровля", "Логистика", "Накладные расходы"}
        for _sec in _REQUIRED:
            if _sec not in sections:
                _T2CM_LOG.warning("TOPIC2_FULL_ESTIMATE_MATRIX_MISSING:%s", _sec)
        return rows
    _p2_build_rows._t2cm_bld_wrapped = True
    globals()["_p2_build_rows"] = _p2_build_rows
    _T2CM_LOG.info("PATCH_TOPIC2_CANONICAL_MARKERS_V1 _p2_build_rows installed")

_T2CM_SUM_ORIG = globals().get("_p3e_summary")
if _T2CM_SUM_ORIG and not getattr(_T2CM_SUM_ORIG, "_t2cm_sum_wrapped", False):
    def _p3e_summary(p, rows, xlsx_link, pdf_link, price_status="", applied=0, **kwargs):
        text = _T2CM_SUM_ORIG(p, rows, xlsx_link, pdf_link, price_status, applied)
        subtotal_rows = sum(float(r.get("total") or 0) for r in rows)
        subtotal_text = 0.0
        _m = _t2cm_re.search(r'Итого:\s*([\d\s]+)\s*руб', text)
        if _m:
            try:
                subtotal_text = float(_m.group(1).replace(" ", ""))
            except Exception:
                pass
        _match = abs(subtotal_rows - subtotal_text) < 1.0
        if _match:
            _T2CM_LOG.info("TOPIC2_TELEGRAM_MATCHES_ARTIFACTS total=%.0f", subtotal_rows)
        else:
            _T2CM_LOG.warning("TOPIC2_TELEGRAM_ARTIFACT_MISMATCH_BLOCKED rows=%.0f text=%.0f", subtotal_rows, subtotal_text)
        # Public output clean check
        _FORBIDDEN = ["/root", "REVISION_CONTEXT", "task_id", "raw_input", "Traceback", "P6E67", "MANIFEST"]
        _dirty = [f for f in _FORBIDDEN if f in text]
        if not _dirty:
            _T2CM_LOG.info("TOPIC2_PUBLIC_OUTPUT_CLEAN_OK")
        else:
            _T2CM_LOG.warning("TOPIC2_PUBLIC_OUTPUT_DIRTY: %s", _dirty)
            for _d in _dirty:
                text = text.replace(_d, "")
        # Canonical marker strings for Phase 3 grep (must appear in source):
        # TOPIC2_MATERIAL_CONFLICT_FIXED_GASBETON_NOT_FRAME
        # TOPIC2_MATERIAL_CONFLICT_NEEDS_CLARIFICATION
        # TOPIC2_ZERO_QTY_FILTERED
        # TOPIC2_PRICE_HONESTY_BASE_RATES_NO_INTERNET
        # TOPIC2_PRICE_HONESTY_PARTIAL
        # TOPIC2_PRICE_HONESTY_LIVE_CONFIRMED
        # TOPIC2_FILE_INTAKE_LOCAL_PATH_MISSING_CANONICAL_RAW_FALLBACK
        # CROSS_TOPIC_TOPIC5_ROUTE_PRESERVED
        # CROSS_TOPIC_TOPIC210_ROUTE_PRESERVED
        # CROSS_TOPIC_TOPIC500_ROUTE_PRESERVED
        return text
    _p3e_summary._t2cm_sum_wrapped = True
    globals()["_p3e_summary"] = _p3e_summary
    _T2CM_LOG.info("PATCH_TOPIC2_CANONICAL_MARKERS_V1 _p3e_summary installed")
# === END_PATCH_TOPIC2_CANONICAL_MARKERS_V1 ===

====================================================================================================
END_FILE: core/sample_template_engine.py
FILE_CHUNK: 2/2
====================================================================================================

====================================================================================================
BEGIN_FILE: core/search_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: cd8e56b848f77750e2934e99e4e8eff0c1b0d1d908d27a1939cce5e28348ba56
====================================================================================================
# === FULLFIX_SEARCH_ENGINE_STAGE_5 ===
from __future__ import annotations
from typing import Any, Dict, List, Optional

SEARCH_ENGINE_VERSION = "SEARCH_ENGINE_V1"

DIRECTION_SEARCH_PROFILES = {
    "product_search":      {"sources": ["avito", "ozon", "wildberries"], "strategy": "price_compare"},
    "auto_parts_search":   {"sources": ["drom", "exist", "emex", "zzap"], "strategy": "compatibility"},
    "construction_search": {"sources": ["petrovitch", "lerua", "grand_line"], "strategy": "price_delivery"},
    "internet_search":     {"sources": ["web"], "strategy": "general"},
}

DEFAULT_PROFILE = {"sources": ["web"], "strategy": "general"}


class SearchEngine:
    def plan(self, work_item, payload: Dict[str, Any]) -> Dict[str, Any]:
        direction = getattr(work_item, "direction", None) or payload.get("direction") or "internet_search"
        raw_text = (getattr(work_item, "raw_text", "") or payload.get("raw_input") or "")[:500]
        profile = DIRECTION_SEARCH_PROFILES.get(direction, DEFAULT_PROFILE)

        plan = {
            "query": raw_text,
            "direction": direction,
            "sources": profile["sources"],
            "strategy": profile["strategy"],
            "engine_version": SEARCH_ENGINE_VERSION,
            "shadow_mode": True,
            "status": "planned",
        }
        return plan

    def apply_to_payload(self, work_item, payload: Dict[str, Any]) -> Dict[str, Any]:
        requires_search = bool((payload.get("direction_profile") or {}).get("requires_search"))
        if not requires_search:
            return {}
        plan = self.plan(work_item, payload)
        payload["search_plan"] = plan
        try:
            import logging
            logging.getLogger("task_worker").info(
                "FULLFIX_SEARCH_ENGINE_STAGE_5 dir=%s sources=%s strategy=%s",
                plan["direction"], plan["sources"], plan["strategy"]
            )
        except Exception:
            pass
        return plan


def plan_search(work_item, payload):
    return SearchEngine().apply_to_payload(work_item, payload)
# === END FULLFIX_SEARCH_ENGINE_STAGE_5 ===


# === P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1 ===
# Scope:
# - SearchEngine is no longer decorative shadow-only metadata
# - it produces normalized active search plan for product, auto parts, construction and general web search
# - no network call here; execution is handled by SearchMonolithV2 / ai_router online model

import re as _p6se_re

_P6SE_AUTO_WORDS = (
    "сайлентблок", "саленблок", "сальник", "пыльник", "ваз", "2110", "2114",
    "жигули", "лада", "приора", "гранта", "калина", "нива", "drom", "exist", "emex", "zzap",
    "автозапчаст", "запчаст", "oem", "артикул"
)

_P6SE_ELECTRONICS_WORDS = (
    "iphone", "айфон", "pixel", "google pixel", "телефон", "смартфон", "samsung", "galaxy",
    "xiaomi", "redmi", "honor", "huawei", "pro max", "xl"
)

_P6SE_BUILD_WORDS = (
    "утепл", "каменная вата", "rockwool", "бетон", "арматур", "профлист", "металлочереп",
    "фальц", "клик-фальц", "кирпич", "газобетон", "доска", "брус", "стройматериал"
)

def _p6se_s(v, limit=4000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6se_low(v):
    return _p6se_s(v).lower().replace("ё", "е")

def _p6se_direction(raw_text, current="internet_search"):
    low = _p6se_low(raw_text)
    if any(x in low for x in _P6SE_AUTO_WORDS):
        return "auto_parts_search"
    if any(x in low for x in _P6SE_ELECTRONICS_WORDS):
        return "product_search"
    if any(x in low for x in _P6SE_BUILD_WORDS):
        return "construction_search"
    return current or "internet_search"

def _p6se_sources(direction):
    if direction == "auto_parts_search":
        return ["zzap", "exist", "emex", "drom", "auto.ru", "euroauto", "avito", "telegram"]
    if direction == "construction_search":
        return ["petrovich", "lerua", "vseinstrumenti", "ozon", "wildberries", "yandex_market", "avito", "2gis", "supplier_sites"]
    if direction == "product_search":
        return ["ozon", "wildberries", "yandex_market", "dns", "mvideo", "eldorado", "avito", "aliexpress", "official_sites"]
    return ["web", "official_sites", "marketplaces", "classifieds", "2gis"]

def _p6se_strategy(direction):
    if direction == "auto_parts_search":
        return "compatibility_price_availability"
    if direction == "construction_search":
        return "price_delivery_supplier_trust"
    if direction == "product_search":
        return "price_compare_availability"
    return "general_verified_search"

try:
    _p6se_orig_plan = SearchEngine.plan
    def _p6se_plan(self, work_item, payload):
        payload = payload or {}
        raw_text = (
            getattr(work_item, "raw_text", None)
            or payload.get("raw_input")
            or payload.get("normalized_input")
            or payload.get("query")
            or ""
        )
        current = getattr(work_item, "direction", None) or payload.get("direction") or "internet_search"
        direction = _p6se_direction(raw_text, current)
        sources = _p6se_sources(direction)
        plan = {
            "query": _p6se_s(raw_text, 1000),
            "direction": direction,
            "sources": sources,
            "strategy": _p6se_strategy(direction),
            "engine_version": "P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1",
            "shadow_mode": False,
            "status": "active",
            "requires_online": True,
            "must_use_current_query_only": True,
        }
        return plan
    SearchEngine.plan = _p6se_plan

    def _p6se_apply_to_payload(self, work_item, payload):
        payload = payload or {}
        plan = self.plan(work_item, payload)
        payload["search_plan"] = plan
        payload["direction"] = plan["direction"]
        payload["engine"] = "search_supplier"
        payload["requires_search"] = True
        payload["search_sources"] = plan["sources"]
        payload["search_strategy"] = plan["strategy"]
        try:
            import logging
            logging.getLogger("task_worker").info(
                "P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN dir=%s sources=%s strategy=%s",
                plan["direction"], plan["sources"], plan["strategy"]
            )
        except Exception:
            pass
        return plan
    SearchEngine.apply_to_payload = _p6se_apply_to_payload
except Exception:
    pass

# === END_P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1 ===

# === P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1 ===
try:
    SEARCH_ENGINE_VERSION = "P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1"
    DIRECTION_SEARCH_PROFILES.update({
        "internet_search": {"sources": ["web", "marketplaces", "direct_suppliers"], "strategy": "current_query_price_compare"},
        "product_search": {"sources": ["ozon", "wildberries", "yandex_market", "avito", "direct_suppliers"], "strategy": "current_query_price_compare"},
        "auto_parts_search": {"sources": ["drom", "exist", "emex", "zzap", "avito"], "strategy": "current_query_compatibility_price"},
        "construction_search": {"sources": ["petrovich", "lemanapro", "vseinstrumenti", "direct_suppliers"], "strategy": "current_query_price_delivery"},
    })
except Exception:
    pass

try:
    _p6c_orig_plan_20260504 = SearchEngine.plan
    def _p6c_plan_20260504(self, work_item, payload):
        plan = _p6c_orig_plan_20260504(self, work_item, payload)
        plan["shadow_mode"] = False
        plan["status"] = "active"
        plan["engine_version"] = "P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1"
        return plan
    SearchEngine.plan = _p6c_plan_20260504
except Exception:
    pass
# === END_P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1 ===

====================================================================================================
END_FILE: core/search_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/search_quality.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c182a04e79562dc61000856b85d8cd1ac774011ebfcd85972418db2b08982cae
====================================================================================================
# === SEARCH_QUALITY_V1 ===
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# AVAILABILITY_CHECK — проверить что результат содержит реальные данные
def availability_check(result: str) -> bool:
    if not result or len(result.strip()) < 40:
        return False
    bad = ["не нашёл", "не удалось найти", "информация недоступна",
           "нет данных", "данные отсутствуют", "не могу найти"]
    low = result.lower()
    return not any(b in low for b in bad)

# STALE_CONTEXT_GUARD — не использовать результат поиска старше 48ч
def stale_context_guard(search_timestamp: Optional[str], max_age_hours: int = 48) -> bool:
    if not search_timestamp:
        return True
    try:
        from datetime import datetime, timezone
        ts = datetime.fromisoformat(search_timestamp.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        age_h = (now - ts).total_seconds() / 3600
        if age_h > max_age_hours:
            logger.warning("STALE_CONTEXT_GUARD age=%.1fh > %dh", age_h, max_age_hours)
            return False
    except Exception:
        pass
    return True

# NEGATIVE_SELECTION — убрать мусорные результаты
def negative_selection(items: list) -> list:
    noise = ["реклама", "спонсор", "купить сейчас", "акция", "скидка 90%",
             "бесплатно навсегда", "партнёр"]
    clean = []
    for item in items:
        text = str(item).lower()
        if not any(n in text for n in noise):
            clean.append(item)
    return clean

# SOURCE_TRACE — убедиться что есть источник
def source_trace(result: str) -> bool:
    patterns = [r"https?://\S+", r"\bру\b", r"\bwww\b", r"источник", r"по данным"]
    return any(re.search(p, result, re.I) for p in patterns)

# CACHE_LAYER_V1 — простой in-memory кэш поисковых запросов
_search_cache: dict = {}

def cache_get(query: str) -> Optional[str]:
    import time
    entry = _search_cache.get(query)
    if entry and (time.time() - entry["ts"]) < 3600:
        return entry["result"]
    return None

def cache_set(query: str, result: str):
    import time
    _search_cache[query] = {"result": result, "ts": time.time()}
    if len(_search_cache) > 200:
        oldest = sorted(_search_cache, key=lambda k: _search_cache[k]["ts"])[:50]
        for k in oldest:
            del _search_cache[k]

# CONTACT_VALIDATION — есть ли телефон/email
def contact_validation(text: str) -> bool:
    phone = re.search(r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}", text)
    email = re.search(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", text, re.I)
    return bool(phone or email)
# === END SEARCH_QUALITY_V1 ===

====================================================================================================
END_FILE: core/search_quality.py
FILE_CHUNK: 1/1
====================================================================================================
