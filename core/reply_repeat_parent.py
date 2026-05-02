# === REPLY_REPEAT_PARENT_TASK_V1 ===
from __future__ import annotations

import json
import re
import sqlite3
from typing import Any, Dict, Optional

REPEAT_WORDS = (
    "повтори", "повторить", "ещё раз", "еще раз", "заново", "продублируй",
    "дублируй", "скинь еще", "скинь ещё", "покажи еще", "покажи ещё"
)

STATUS_WORDS = (
    "ну что", "что там", "как там", "готово?", "готово", "ответишь",
    "ты ответишь", "будет ответ", "есть ответ", "жду", "дальше то что"
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

def _is_short_human_reply(text: str) -> bool:
    low = _low(text)
    if not low:
        return False
    compact = re.sub(r"[^\wа-яА-Я]+", " ", low).strip()
    if len(compact) > 80:
        return False
    return any(w in low for w in REPEAT_WORDS + STATUS_WORDS)

def _is_repeat(text: str) -> bool:
    low = _low(text)
    return any(w in low for w in REPEAT_WORDS)

def _is_status(text: str) -> bool:
    low = _low(text)
    return any(w in low for w in STATUS_WORDS)

def _find_parent(conn: sqlite3.Connection, chat_id: str, topic_id: int, reply_to: Any, current_task_id: str) -> Optional[Dict[str, Any]]:
    cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    has_bot = "bot_message_id" in cols
    has_reply = "reply_to_message_id" in cols
    has_topic = "topic_id" in cols

    params = [str(chat_id)]
    topic_sql = ""
    if has_topic:
        topic_sql = " AND COALESCE(topic_id,0)=?"
        params.append(int(topic_id or 0))

    if reply_to and has_bot:
        row = conn.execute(
            f"""
            SELECT rowid,* FROM tasks
            WHERE chat_id=?{topic_sql}
              AND id<>?
              AND bot_message_id=?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            params + [current_task_id, int(reply_to)],
        ).fetchone()
        if row:
            return dict(row)

    if reply_to and has_reply:
        row = conn.execute(
            f"""
            SELECT rowid,* FROM tasks
            WHERE chat_id=?{topic_sql}
              AND id<>?
              AND reply_to_message_id=?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            params + [current_task_id, int(reply_to)],
        ).fetchone()
        if row:
            return dict(row)

    row = conn.execute(
        f"""
        SELECT rowid,* FROM tasks
        WHERE chat_id=?{topic_sql}
          AND id<>?
          AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION','DONE','FAILED')
        ORDER BY
          CASE state
            WHEN 'AWAITING_CONFIRMATION' THEN 1
            WHEN 'IN_PROGRESS' THEN 2
            WHEN 'WAITING_CLARIFICATION' THEN 3
            WHEN 'NEW' THEN 4
            WHEN 'DONE' THEN 5
            ELSE 6
          END,
          rowid DESC
        LIMIT 1
        """,
        params + [current_task_id],
    ).fetchone()
    return dict(row) if row else None

def _short_task_summary(parent: Dict[str, Any]) -> str:
    raw = _s(parent.get("raw_input"))
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw[:220] if raw else "исходная задача"

def _clean_result(result: str) -> str:
    try:
        from core.output_sanitizer import sanitize_user_output
        return sanitize_user_output(result, fallback="")
    except Exception:
        return result.strip()

def prehandle_reply_repeat_parent_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))
    reply_to = _task_field(task, "reply_to_message_id", None)

    if input_type not in ("text", "voice"):
        return None
    if not _is_short_human_reply(raw_input):
        return None

    parent = _find_parent(conn, chat_id, topic_id, reply_to, task_id)
    if not parent:
        return None

    parent_id = _s(parent.get("id"))
    parent_state = _s(parent.get("state"))
    parent_result = _clean_result(_s(parent.get("result")))
    summary = _short_task_summary(parent)

    if _is_repeat(raw_input):
        if parent_result:
            msg = "Повторяю результат по исходной задаче\n\n" + parent_result
            state = "DONE"
            hist = f"REPLY_REPEAT_PARENT_TASK_V1:REPEATED:{parent_id[:8]}"
        else:
            if parent_state in ("FAILED", "CANCELLED", "DONE"):
                conn.execute(
                    "UPDATE tasks SET state='NEW', updated_at=datetime('now') WHERE id=?",
                    (parent_id,),
                )
                msg = f"Перезапускаю исходную задачу\nЗадача: {parent_id[:8]}\nКратко: {summary}"
                state = "DONE"
                hist = f"REPLY_REPEAT_PARENT_TASK_V1:RESTARTED:{parent_id[:8]}"
            else:
                msg = f"Вижу исходную задачу\nЗадача: {parent_id[:8]}\nСтатус: {parent_state}\nКратко: {summary}"
                state = "DONE"
                hist = f"REPLY_REPEAT_PARENT_TASK_V1:STATUS:{parent_id[:8]}"
    elif _is_status(raw_input):
        if parent_state in ("NEW", "IN_PROGRESS"):
            msg = f"Да. Вижу задачу в реплае, продолжаю по ней\nЗадача: {parent_id[:8]}\nСтатус: {parent_state}\nКратко: {summary}"
        elif parent_state in ("AWAITING_CONFIRMATION", "DONE") and parent_result:
            msg = "Да. Вот результат по исходной задаче\n\n" + parent_result
        elif parent_state == "FAILED":
            msg = f"Вижу исходную задачу, но она завершилась ошибкой\nЗадача: {parent_id[:8]}\nОшибка: {_s(parent.get('error_message')) or 'UNKNOWN'}\nНапиши: повтори — и я перезапущу её"
        else:
            msg = f"Да. Вижу исходную задачу\nЗадача: {parent_id[:8]}\nСтатус: {parent_state}\nКратко: {summary}"
        state = "DONE"
        hist = f"REPLY_REPEAT_PARENT_TASK_V1:ACK:{parent_id[:8]}"
    else:
        return None

    conn.commit()
    return {
        "handled": True,
        "state": state,
        "message": msg,
        "kind": "reply_repeat_parent",
        "history": hist,
    }

# === END_REPLY_REPEAT_PARENT_TASK_V1 ===
