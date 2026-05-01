# === ACTIVE_DIALOG_STATE_V1 ===
# === UNIFIED_CONTEXT_PRIORITY_V1 ===
# === SHORT_CONTROL_SAFE_ROUTER_V1 ===
from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional

BASE = "/root/.areal-neva-core"
MEM_DB = os.path.join(BASE, "data/memory.db")

SHORT_CONTROLS = {
    "да", "ок", "окей", "+", "ага", "делай", "делаем", "дальше", "продолжай",
    "покажи", "скинь", "отбой", "закрывай", "готово", "что дальше", "ну что",
}

def _s(v: Any, limit: int = 4000) -> str:
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        try:
            v = json.dumps(v, ensure_ascii=False)
        except Exception:
            v = str(v)
    return str(v).strip()[:limit]

def clean_voice(text: str) -> str:
    return re.sub(r"^\s*\[VOICE\]\s*", "", text or "", flags=re.I).strip()

def is_short_control(text: str) -> bool:
    t = clean_voice(text).lower().strip(" .,!?:;—-")
    return t in SHORT_CONTROLS or (len(t.split()) <= 3 and any(x in t for x in SHORT_CONTROLS))

def _task_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {k: row[k] for k in row.keys()}

def last_active_task(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        SELECT * FROM tasks
        WHERE chat_id=? AND COALESCE(topic_id,0)=?
          AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id or 0)),
    ).fetchone()
    return _task_row_to_dict(row) if row else None

def last_file_task(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        SELECT * FROM tasks
        WHERE chat_id=? AND COALESCE(topic_id,0)=?
          AND (
            input_type IN ('drive_file','file','document','photo','image')
            OR raw_input LIKE '%file_id%'
            OR raw_input LIKE '%file_name%'
            OR result LIKE '%drive.google%'
            OR result LIKE '%docs.google%'
            OR result LIKE '%.xlsx%'
            OR result LIKE '%.pdf%'
            OR result LIKE '%.docx%'
          )
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id or 0)),
    ).fetchone()
    return _task_row_to_dict(row) if row else None

def _memory_lookup(chat_id: str, topic_id: int, query: str = "") -> str:
    if not os.path.exists(MEM_DB):
        return ""
    q = f"%{query[:40]}%" if query else "%"
    out = []
    try:
        con = sqlite3.connect(MEM_DB)
        rows = con.execute(
            """
            SELECT key, value, timestamp FROM memory
            WHERE chat_id=? AND key LIKE ?
              AND (
                key LIKE ? OR value LIKE ? OR key LIKE ? OR key LIKE ?
              )
            ORDER BY timestamp DESC
            LIMIT 8
            """,
            (
                str(chat_id),
                f"topic_{int(topic_id or 0)}_%",
                "%file%",
                q,
                "%artifact%",
                "%archive%",
            ),
        ).fetchall()
        con.close()
        for k, v, ts in rows:
            out.append(f"{ts} | {k} | {_s(v, 700)}")
    except Exception:
        return ""
    return "\n".join(out)

def build_active_context(conn: sqlite3.Connection, chat_id: str, topic_id: int, user_text: str = "") -> Dict[str, Any]:
    active = last_active_task(conn, chat_id, topic_id)
    last_file = last_file_task(conn, chat_id, topic_id)
    mem = _memory_lookup(chat_id, topic_id, clean_voice(user_text))
    return {
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "user_text": user_text,
        "active_task": active,
        "last_file": last_file,
        "memory": mem,
        "priority": "input -> reply parent -> active task -> last file -> pin -> short memory -> long memory -> archive",
    }

def maybe_handle_active_dialog(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    raw = _s(task["raw_input"] if "raw_input" in task.keys() else "")
    text = clean_voice(raw)
    low = text.lower()

    if not text:
        return None

    file_followup = any(x in low for x in (
        "скидывал файл", "скидывал смету", "какой файл", "что дальше", "дальше то что",
        "покажи файл", "где файл", "где смета", "что с файлом", "по этому файлу",
    ))

    if file_followup:
        try:
            from core.file_memory_bridge import build_file_followup_answer
            ans = build_file_followup_answer(str(chat_id), int(topic_id or 0), raw, limit=8)
            if ans:
                return {
                    "handled": True,
                    "state": "DONE",
                    "result": ans,
                    "event": "ACTIVE_DIALOG_STATE_V1:FILE_FOLLOWUP_DONE",
                }
        except Exception as e:
            return {
                "handled": True,
                "state": "FAILED",
                "result": "",
                "error": f"ACTIVE_DIALOG_FILE_FOLLOWUP_ERR:{e}",
                "event": "ACTIVE_DIALOG_STATE_V1:FILE_FOLLOWUP_FAILED",
            }

    if is_short_control(text):
        ctx = build_active_context(conn, chat_id, topic_id, raw)
        active = ctx.get("active_task")
        last_file = ctx.get("last_file")
        if active:
            res = _s(active.get("result") or active.get("raw_input"), 1200)
            return {
                "handled": True,
                "state": "DONE",
                "result": f"Активный контекст найден\nЗадача: {active.get('id')}\nСтатус: {active.get('state')}\nКратко: {res}",
                "event": "ACTIVE_DIALOG_STATE_V1:SHORT_CONTROL_ACTIVE_TASK",
            }
        if last_file:
            res = _s(last_file.get("result") or last_file.get("raw_input"), 1200)
            return {
                "handled": True,
                "state": "DONE",
                "result": f"Последний файловый контекст найден\nЗадача: {last_file.get('id')}\nСтатус: {last_file.get('state')}\nКратко: {res}",
                "event": "ACTIVE_DIALOG_STATE_V1:SHORT_CONTROL_LAST_FILE",
            }

    return None

def save_dialog_event(chat_id: str, topic_id: int, key: str, value: Any) -> None:
    if not os.path.exists(MEM_DB):
        return
    try:
        con = sqlite3.connect(MEM_DB)
        con.execute(
            "INSERT INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,?)",
            (
                str(chat_id),
                f"topic_{int(topic_id or 0)}_dialog_{key}",
                json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        con.commit()
        con.close()
    except Exception:
        pass
# === END_SHORT_CONTROL_SAFE_ROUTER_V1 ===
# === END_UNIFIED_CONTEXT_PRIORITY_V1 ===
# === END_ACTIVE_DIALOG_STATE_V1 ===
