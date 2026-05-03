# === PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1 ===
# === PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1 ===
from __future__ import annotations

import json
import re
import sqlite3
from typing import Any, Dict, Optional

PROJECT_STRONG = (
    "сделай проект", "создай проект", "разработай проект", "подготовь проект",
    "проект монолит", "проект плиты", "проект фундамент", "проект кровли",
    "проект кж", "проект кд", "проект ар", "чертеж", "чертёж",
    "конструктивное решение", "проектное решение", "лист кж", "лист кд"
)

PROJECT_WEAK = (
    "кж", "кд", "ар", "км", "кмд", "плита", "фундамент", "армирование",
    "опалубка", "разрез", "узел", "схема", "спецификация арматуры"
)

ESTIMATE_ONLY = (
    "смета", "смету", "сметный", "расценка", "стоимость работ",
    "цены материалов", "кс-2", "кс2"
)

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()

def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")

def _task_field(task: Any, field: str, default: Any = "") -> Any:
    try:
        if hasattr(task, "keys") and field in task.keys():
            return task[field]
    except Exception:
        pass
    if isinstance(task, dict):
        return task.get(field, default)
    try:
        return getattr(task, field)
    except Exception:
        return default

def is_explicit_project_intent(text: Any) -> bool:
    low = _low(text)
    if not low:
        return False
    strong = any(x in low for x in PROJECT_STRONG)
    weak_project = sum(1 for x in PROJECT_WEAK if x in low) >= 2
    estimate_only = any(x in low for x in ESTIMATE_ONLY)  # ESTIMATE_PRIORITY_FIX_V1
    if estimate_only and not strong:  # ESTIMATE_PRIORITY_FIX_V1
        return False
    return bool(strong or weak_project)

def _format_links(res: Dict[str, Any]) -> str:
    lines = []
    for label, key in (
        ("DOCX", "docx_link"),
        ("XLSX", "xlsx_link"),
        ("PDF", "pdf_link"),
        ("Drive", "drive_link"),
    ):
        val = _s(res.get(key))
        if val and "drive.google.com" in val or "docs.google.com" in val:
            lines.append(f"{label}: {val}")
    return "\n".join(lines)

def format_project_result_message(res: Dict[str, Any], raw_input: str = "") -> str:
    section = _s(res.get("project_type") or res.get("section") or "КЖ")
    links = _format_links(res)
    if res.get("success") and links:
        msg = (
            "Проектный файл создан\n"
            f"Раздел: {section}\n"
            f"{links}\n\n"
            "Доволен результатом? Да / Уточни / Правки"
        )
    elif res.get("success"):
        msg = (
            "Проектный файл подготовлен локально, но ссылка Drive не подтверждена\n"
            f"Раздел: {section}\n"
            "Нужна проверка выгрузки"
        )
    else:
        err = _s(res.get("error")) or "PROJECT_RESULT_NOT_READY"
        if "PROJECT_TEMPLATE_MODEL_NOT_FOUND" in err:
            msg = (
                "Для проектного файла нужен образец проекта в этом топике\n"
                "Пришли КЖ/КД/АР файл как образец или напиши исходные данные проекта"
            )
        else:
            msg = (
                "Проектный файл не создан\n"
                f"Причина: {err}\n"
                "Уточни исходные данные или пришли образец проекта"
            )

    try:
        from core.output_sanitizer import sanitize_project_message
        return sanitize_project_message(msg)
    except Exception:
        return msg.strip()

async def prehandle_project_route_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))

    # === CANON_LIST_QUERY_GUARD_V1 ===
    if topic_id == 500:
        return None
    _list_signals = ("какие", "покажи", "перечисли", "что есть", "есть ли", "список", "что за образц", "какие образц", "покажи образц")
    _create_signals = ("сделай", "создай", "разработай", "подготовь", "оформи")
    _raw_low_guard = raw_input.lower().replace("ё", "е")
    if any(s in _raw_low_guard for s in _list_signals) and not any(s in _raw_low_guard for s in _create_signals):
        return None
    # === END_CANON_LIST_QUERY_GUARD_V1 ===
    if input_type not in ("text", "voice", "search"):
        return None
    if not is_explicit_project_intent(raw_input):
        return None

    try:
        from core.project_engine import create_project_artifact_from_latest_template
        res = create_project_artifact_from_latest_template(raw_input, task_id, topic_id)
    except Exception as e:
        res = {
            "success": False,
            "error": f"PROJECT_ENGINE_EXCEPTION: {e}",
            "project_type": "КЖ",
        }

    msg = _s(res.get("user_message")) or format_project_result_message(res, raw_input)

    if res.get("success") and ("drive.google.com" in msg or "docs.google.com" in msg):
        state = "AWAITING_CONFIRMATION"
        err = ""
        hist = "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:PROJECT_CREATED"
    elif res.get("success"):
        state = "WAITING_CLARIFICATION"
        err = "PROJECT_DRIVE_LINK_NOT_CONFIRMED"
        hist = "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:PROJECT_LOCAL_ONLY"
    else:
        state = "WAITING_CLARIFICATION"
        err = _s(res.get("error")) or "PROJECT_NOT_CREATED"
        hist = "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:PROJECT_NEEDS_CONTEXT"

    return {
        "handled": True,
        "state": state,
        "message": msg,
        "error_message": err,
        "kind": "project_route_guard",
        "history": hist,
    }

# === END_PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1 ===
# === END_PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1 ===
