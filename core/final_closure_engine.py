# === FINAL_CLOSURE_BLOCKER_FIX_V1_ENGINE ===
from __future__ import annotations

import json
import re
import sqlite3
from typing import Any, Dict


def _s(v) -> str:
    return "" if v is None else str(v).strip()


def _json(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw or "{}")
    except Exception:
        return {}


def _field(task: Any, key: str, default=None):
    try:
        if hasattr(task, "keys") and key in task.keys():
            return task[key]
    except Exception:
        pass
    try:
        return getattr(task, key)
    except Exception:
        return default


def _row_get(row: Any, key: str, idx: int, default: Any = "") -> Any:
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        if isinstance(row, dict):
            return row.get(key, default)
    except Exception:
        pass
    try:
        return row[idx]
    except Exception:
        return default


def _send_payload(message: str, kind: str, state: str = "DONE", history: str = "") -> Dict[str, Any]:
    return {
        "handled": True,
        "state": state,
        "message": message,
        "kind": kind,
        "history": history or f"FINAL_CLOSURE_BLOCKER_FIX_V1:{kind}",
    }



# === FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V2 ===

# === FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3 ===


# === PROJECT_SAMPLE_SELECTION_P0_V2 ===
def _fc_norm_public(text: Any) -> str:
    s = "" if text is None else str(text)
    s = s.replace("\\\\n", "\n").replace("\\n", "\n").replace("\\\\t", " ").replace("\\t", " ")
    s = s.replace("ё", "е")
    return s.strip()


def _fc_clean_title(name: str) -> str:
    name = _fc_norm_public(name)
    name = re.sub(r"^\s*\d+\.\s*", "", name).strip().strip("\"'«»")
    return name[:180]


def _fc_is_sample_status_request(text: str) -> bool:
    low = _fc_norm_public(text).lower()
    if not any(x in low for x in ("образец", "образцов", "шаблон", "шаблона")):
        return False

    strict_status_or_selection = (
        "взял как образец",
        "взял за образец",
        "ты взял как образец",
        "уже взял как образец",
        "взял их как образец",
        "взял это как образец",
        "принял как образец",
        "принял за образец",
        "ты принял как образец",
        "уже принял как образец",
        "принял их как образец",
        "принял это как образец",
        "используешь как образец",
        "используется как образец",
        "файлы взяты как образец",
        "файлы приняты как образец",
        "взяты как образец",
        "приняты как образец",
        "закрепи как образец",
        "закрепить как образец",
        "закрепляется как",
        "закрепляй как",
        "оставь как образец",
        "сохрани как образец",
        "один из образцов",
        "как один из образцов",
    )
    if any(x in low for x in strict_status_or_selection):
        return True

    if "как образец" in low and any(x in low for x in (
        "да ",
        "да,",
        "да.",
        "цоколь",
        "кж",
        "кд",
        "км",
        "кмд",
        "ар",
        "проект",
        "смет",
        "вор",
        "акт",
        "технадзор",
    )):
        return True

    return False


def _fc_extract_titles_from_text(text: str) -> list[str]:
    src = _fc_norm_public(text)
    titles: list[str] = []

    try:
        data = json.loads(src)
        if isinstance(data, dict):
            for key in ("file_name", "name", "title"):
                val = _fc_clean_title(data.get(key) or "")
                if val:
                    titles.append(val)
    except Exception:
        pass

    for m in re.finditer(r'"file_name"\s*:\s*"([^"]+)"', src, re.I):
        val = _fc_clean_title(m.group(1))
        if val:
            titles.append(val)

    for m in re.finditer(r'([А-ЯA-Z0-9Ёё][^\n\r]{0,120}\.(?:pdf|dwg|dxf|xlsx|xls|docx|doc))', src, re.I):
        val = _fc_clean_title(m.group(1))
        if val:
            titles.append(val)

    out: list[str] = []
    seen = set()
    for title in titles:
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(title)
    return out


def _fc_recent_file_rows(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> list[Any]:
    old_rf = conn.row_factory
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, raw_input, result, updated_at
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND (
                COALESCE(raw_input,'') LIKE '%file_name%'
                OR COALESCE(raw_input,'') LIKE '%.pdf%'
                OR COALESCE(raw_input,'') LIKE '%.dwg%'
                OR COALESCE(raw_input,'') LIKE '%.dxf%'
                OR COALESCE(raw_input,'') LIKE '%.xlsx%'
                OR COALESCE(result,'') LIKE '%file_name%'
                OR COALESCE(result,'') LIKE '%.pdf%'
                OR COALESCE(result,'') LIKE '%.dwg%'
                OR COALESCE(result,'') LIKE '%.dxf%'
                OR COALESCE(result,'') LIKE '%.xlsx%'
              )
            ORDER BY updated_at DESC
            LIMIT 80
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()
        return list(rows or [])
    except Exception:
        return []
    finally:
        conn.row_factory = old_rf


def _fc_sample_raw_hay(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> str:
    parts: list[str] = []
    for r in _fc_recent_file_rows(conn, chat_id, topic_id):
        try:
            parts.append(_fc_norm_public(r["raw_input"]))
            parts.append(_fc_norm_public(r["result"]))
        except Exception:
            pass
    return " ".join(parts).lower().replace("ё", "е")


def _fc_sample_titles(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> list[str]:
    titles: list[str] = []
    for r in _fc_recent_file_rows(conn, chat_id, topic_id):
        try:
            titles.extend(_fc_extract_titles_from_text(r["raw_input"]))
            titles.extend(_fc_extract_titles_from_text(r["result"]))
        except Exception:
            continue

    out: list[str] = []
    seen = set()
    for title in titles:
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(title)
    return out[:12]


def _fc_sample_domain_from_hay(hay: str) -> str:
    hay = _fc_norm_public(hay).lower().replace("ё", "е")
    if any(x in hay for x in ("кж", "кд", "кмд", "км", " ар ", "ар ", "проект", "цоколь", ".dwg", ".dxf")):
        return "project"
    if any(x in hay for x in ("смет", "вор", "расцен", "кс-2", "кс2", ".xlsx", ".xls")):
        return "estimate"
    if any(x in hay for x in ("акт", "технадзор", "дефект")):
        return "technadzor"
    return ""


def _fc_select_sample_title(raw_input: str, titles: list[str]) -> str:
    low = _fc_norm_public(raw_input).lower()
    for title in titles:
        tlow = title.lower()
        words = [w for w in re.split(r"[\s._\-]+", tlow) if len(w) >= 3]
        if any(w in low for w in words):
            return title
    if len(titles) == 1:
        return titles[0]
    if "цоколь" in low:
        for title in titles:
            if "цоколь" in title.lower():
                return title
    return ""


def _fc_write_sample_memory(chat_id: str, topic_id: int, domain: str, title: str, raw_input: str) -> None:
    try:
        import datetime
        mem = sqlite3.connect("/root/.areal-neva-core/data/memory.db")
        try:
            payload = json.dumps(
                {
                    "engine": "PROJECT_SAMPLE_SELECTION_P0_V2",
                    "chat_id": str(chat_id),
                    "topic_id": int(topic_id or 0),
                    "domain": domain,
                    "title": title,
                    "raw_input": raw_input,
                    "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                },
                ensure_ascii=False,
            )
            mem.execute(
                "INSERT INTO memory(chat_id,key,value,timestamp) VALUES (?,?,?,?)",
                (
                    str(chat_id),
                    f"topic_{int(topic_id or 0)}_{domain or 'sample'}_selected_sample",
                    payload,
                    datetime.datetime.utcnow().isoformat() + "Z",
                ),
            )
            mem.commit()
        finally:
            mem.close()
    except Exception:
        pass


def _handle_sample_status(conn: sqlite3.Connection, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    if not _fc_is_sample_status_request(raw_input):
        return {"handled": False}

    titles = _fc_sample_titles(conn, chat_id, topic_id)
    raw_hay = _fc_sample_raw_hay(conn, chat_id, topic_id)
    selected_title = _fc_select_sample_title(raw_input, titles)
    domain = _fc_sample_domain_from_hay(" ".join([raw_input, selected_title, " ".join(titles), raw_hay]))

    if domain == "project":
        if selected_title:
            msg = f"{selected_title} закреплён как образец проектирования"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец проектирования"
    elif domain == "estimate":
        if selected_title:
            msg = f"{selected_title} закреплён как образец сметы"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец сметы"
    elif domain == "technadzor":
        if selected_title:
            msg = f"{selected_title} закреплён как образец для технадзора"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец для технадзора"
    else:
        if selected_title:
            msg = f"{selected_title} закреплён как образец"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец"

    _fc_write_sample_memory(str(chat_id), int(topic_id or 0), domain or "sample", selected_title, raw_input)

    return _send_payload(
        msg,
        "project_sample_selection",
        "DONE",
        "PROJECT_SAMPLE_SELECTION_P0_V2:ANSWERED",
    )
# === END_PROJECT_SAMPLE_SELECTION_P0_V2 ===



def _handle_memory_query(conn: sqlite3.Connection, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    t = raw_input.lower().replace("ё", "е")

    trigger = False
    try:
        from core.file_memory_bridge import should_handle_file_followup
        trigger = bool(should_handle_file_followup(raw_input))
    except Exception:
        trigger = False

    if not trigger:
        trigger = any(x in t for x in [
            "что скидывал",
            "что я скидывал",
            "что отправлял",
            "что загружал",
            "какие файлы",
            "какой файл",
            "проектные файлы",
            "файлы проекта",
            "файлы в чате",
            "документы в чате",
            "последний файл",
            "скидывал",
            "загружал",
        ])

    if not trigger:
        return {"handled": False}

    try:
        from core.file_memory_bridge import build_file_followup_answer
        answer = build_file_followup_answer(str(chat_id), int(topic_id or 0), raw_input, limit=3)
    except Exception:
        answer = ""

    if not answer:
        answer = "В этом топике релевантных файлов по запросу не найдено"

    try:
        from core.output_sanitizer import sanitize_user_output
        answer = sanitize_user_output(answer, fallback="Файлы найдены")
    except Exception:
        pass

    return _send_payload(
        answer,
        "memory_query",
        "DONE",
        "FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3:LISTED",
    )

# === END_FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3 ===


def _handle_runtime_file(conn: sqlite3.Connection, task: Any, task_id: str, chat_id: str, topic_id: int, raw_input: str, input_type: str) -> Dict[str, Any]:
    if input_type not in ("drive_file", "file"):
        return {"handled": False}

    data = _json(raw_input)
    file_id = _s(data.get("file_id"))
    file_name = _s(data.get("file_name") or data.get("name"))
    mime = _s(data.get("mime_type"))
    source = _s(data.get("source") or "telegram")
    size = int(data.get("size") or data.get("file_size") or 0)
    drive_link = _s(data.get("drive_link") or data.get("webViewLink"))

    from core.runtime_file_catalog import duplicate_user_message, register_file

    res = register_file(
        chat_id,
        topic_id,
        task_id,
        file_id=file_id,
        file_name=file_name,
        mime_type=mime,
        size=size,
        source=source,
        drive_link=drive_link,
    )

    if res.get("duplicate"):
        return _send_payload(
            duplicate_user_message(file_name or "UNKNOWN", res.get("duplicate_record") or {}),
            "runtime_duplicate_file",
            "WAITING_CLARIFICATION",
            "FINAL_CLOSURE_BLOCKER_FIX_V1:RUNTIME_DUPLICATE_FILE",
        )

    return {"handled": False, "catalog_registered": True}


def _handle_technadzor(raw_input: str, task_id: str, chat_id: str, topic_id: int) -> Dict[str, Any]:
    from core.technadzor_engine import is_technadzor_intent, process_technadzor

    if not is_technadzor_intent(raw_input):
        return {"handled": False}

    return process_technadzor(text=raw_input, task_id=task_id, chat_id=chat_id, topic_id=topic_id)


def _handle_ocr(raw_input: str, task_id: str) -> Dict[str, Any]:
    from core.ocr_engine import is_ocr_table_intent, process_ocr_table

    if not is_ocr_table_intent(raw_input):
        return {"handled": False}

    return process_ocr_table(text=raw_input, task_id=task_id)


def _handle_archive_guard(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    if not any(x in raw_input.lower() for x in ["архив", "сохрани", "запомни"]):
        return {"handled": False}

    from core.archive_guard import should_archive

    res = should_archive(conn, task_id, chat_id, topic_id, raw_input)
    if res.get("duplicate"):
        return _send_payload(
            "В архив не дублирую: такая запись уже есть",
            "archive_duplicate",
            "DONE",
            "FINAL_CLOSURE_BLOCKER_FIX_V1:ARCHIVE_DUPLICATE_BLOCKED",
        )

    return {"handled": False, "archive_guard_ok": True}


def maybe_handle_final_closure(
    conn: sqlite3.Connection,
    task: Any,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input: str,
    input_type: str = "text",
    reply_to=None,
) -> Dict[str, Any]:
    raw_input = _s(raw_input)
    input_type = _s(input_type or _field(task, "input_type", "text"))
    chat_id = _s(chat_id or _field(task, "chat_id", ""))
    topic_id = int(topic_id or _field(task, "topic_id", 0) or 0)

    r = _handle_runtime_file(conn, task, task_id, chat_id, topic_id, raw_input, input_type)
    if r.get("handled"):
        return r

    r = _handle_sample_status(conn, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    r = _handle_memory_query(conn, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    r = _handle_technadzor(raw_input, task_id, chat_id, topic_id)
    if r.get("handled"):
        return r

    r = _handle_ocr(raw_input, task_id)
    if r.get("handled"):
        return r

    r = _handle_archive_guard(conn, task_id, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    return {"handled": False}


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_ENGINE ===
