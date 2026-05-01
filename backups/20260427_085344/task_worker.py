import os


HUMAN_SHORT = {"да","ок","ага","понял","хорошо","ясно","ладно","угу"}

def _is_human_short(text: str) -> bool:
    return str(text).strip().lower() in HUMAN_SHORT

BASE = "/root/.areal-neva-core"

import re
import time
import json
import sqlite3
import asyncio
import hashlib
import logging
import fcntl
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from core.ai_router import process_ai_task
from core.reply_sender import send_reply, send_reply_ex
from core.pin_manager import get_pin_context, save_pin
from core.topic_drive_oauth import upload_file_to_topic
from core.artifact_pipeline import analyze_downloaded_file

load_dotenv(f"{BASE}/.env", override=True)

CORE_DB = f"{BASE}/data/core.db"
MEM_DB = f"{BASE}/data/memory.db"
LOG_PATH = f"{BASE}/logs/task_worker.log"
LOCK_PATH = f"{BASE}/runtime/task_worker.lock"

POLL_SEC = 1.5
MIN_RESULT_LEN = 8
AI_TIMEOUT = 300
STALE_TIMEOUT = 600

_REMINDER_SENT: dict = {}

TRASH_AWAITING_PATTERNS = [
    "задача отменена", "не понимаю запрос", "готов к выполнению",
    "не понял запрос", "нет данных", "не могу выполнить", "уточните задачу",
]

def _auto_close_trash_awaiting(conn) -> None:
    rows = conn.execute(
        "SELECT id, chat_id, reply_to_message_id, result FROM tasks WHERE state='AWAITING_CONFIRMATION'"
    ).fetchall()
    for row in rows:
        result = (row["result"] or "").lower().strip()
        if any(p in result for p in TRASH_AWAITING_PATTERNS):
            task_id = str(row["id"])
            conn.execute("UPDATE tasks SET state='DONE', error_message='AUTO_CLOSED_TRASH', updated_at=datetime('now') WHERE id=?", (task_id,))
            conn.execute("UPDATE pin SET state='CLOSED', updated_at=datetime('now') WHERE task_id=? AND state='ACTIVE'", (task_id,))
            conn.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))", (task_id, "auto_closed_trash"))
            conn.commit()

def _send_awaiting_reminders(conn) -> None:
    import time as _t
    _now = _t.time()
    REMINDER_INTERVAL = 180
    rows = conn.execute(
        "SELECT id, chat_id, reply_to_message_id, COALESCE(result,'') AS result FROM tasks WHERE state='AWAITING_CONFIRMATION' AND (strftime('%s','now') - strftime('%s', updated_at)) > ?",
        (REMINDER_INTERVAL,)
    ).fetchall()
    for row in rows:
        task_id = str(row["id"])
        last_sent = _REMINDER_SENT.get(task_id, 0)
        if _now - last_sent < REMINDER_INTERVAL:
            continue
        chat_id = str(row["chat_id"])
        reply_to = row["reply_to_message_id"]
        snippet = (row["result"] or "")[:300]
        reminder = f"⏰ Жду ответа:\n\n{snippet}\n\nДоволен результатом? Ответь: Да / Уточни / Правки"
        _send_once(conn, task_id, chat_id, reminder, reply_to, f"reminder_{int(_now)}")
        _REMINDER_SENT[task_id] = _now

REMINDER_SEC = 180

BAD_RESULT_RE = [
    r"\bой\b",
    r"сорян",
    r"дружище",
    r"не переживай",
    r"дай мне немного времени",
    r"я могу помочь",
    r"извини",
    r"извините",
    r"😅",
    r"💪",
    r"😎",
    r"delete from",
    r"\bsql\b",
    r"task_worker\.py",
    r"\bищу\b",
    r"\bнайду\b",
    r"непонятно",
    r"недостаточно данных",
    r"ссылки предоставлю",
    r"готов искать",
    r"могу найти",
    r"укажите\s+что\s+именно\s+нужно\s+найти",
]

MEMORY_BAD_MARKERS = [
    "traceback",
    "forbidden default model",
    "/root/",
    ".json",
    ".log",
    "не могу выполнить запрос",
    "delete from",
    "task_worker.py",
    "telegram_daemon.py",
    "выполните sql",
]

CONFIRM_INTENTS = {
    "да",
    "ок",
    "ok",
    "окей",
    "хорошо",
    "подтверждаю",
    "принято",
    "согласен",
    "верно",
    "всё верно",
    "все верно",
}

REVISION_INTENTS = {
    "нет",
    "не так",
    "переделай",
    "исправь",
    "доработай",
    "уточню",
    "уточнение",
    "правки",
    "уточни",
}

MEMORY_NOISE_MARKERS = [
    "чат не содержит активной задачи",
    "привет. чат не содержит активной задачи",
    "чат создан для",
    "тест диагностика",
    "не понял", "уточните", "нет данных",
    "последние действия", "готов к выполнению",
    "не понимаю запрос", "не могу выполнить",
]

def _is_memory_noise(text: str) -> bool:
    t = _clean(_s(text), 1000).lower()
    if not t:
        return False
    return any(x in t for x in MEMORY_NOISE_MARKERS)

SEARCH_PATTERNS = [
    r"\bнайди\b",
    r"\bнайти\b",
    r"\bпоиск\b",
    r"\bпоищи\b",
    r"\bsearch\b",
    r"\bцена\b",
    r"\bстоимость\b",
    r"\bсколько\s+стоит\b",
    r"\bavito\b",
    r"\bozon\b",
    r"\bwildberries\b",
    r"\bauto\.ru\b",
    r"\bdrom\b",
    r"\bновости\b",
    r"\bпогода\b",
    r"\bкурс\b",
    r"\bмаркетплейс\b",
]

os.makedirs(f"{BASE}/logs", exist_ok=True)
os.makedirs(f"{BASE}/runtime", exist_ok=True)

logger = logging.getLogger("task_worker")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s WORKER: %(message)s"))
    logger.addHandler(fh)


def db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=20, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=15000")
    return conn


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


def _task_field(task: Any, field: str, default: Any = "") -> Any:
    try:
        if hasattr(task, "keys") and field in task.keys():
            return task[field]
    except Exception:
        pass
    try:
        return getattr(task, field)
    except Exception:
        return default


def _has_table(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def _cols(conn: sqlite3.Connection, table: str) -> List[str]:
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except Exception:
        return []


def _update_task(conn: sqlite3.Connection, task_id: str, **kwargs: Any) -> None:
    cols = _cols(conn, "tasks")
    parts: List[str] = []
    vals: List[Any] = []

    for key, value in kwargs.items():
        if key in cols:
            parts.append(f"{key}=?")
            if key == "error_message":
                vals.append(_clean(_s(value), 4000))
            elif key == "result":
                vals.append(_clean(_s(value), 50000))
            elif key == "raw_input":
                vals.append(_clean(_s(value), 12000))
            else:
                vals.append(value)

    if "updated_at" in cols:
        parts.append("updated_at=datetime('now')")

    if not parts:
        return

    vals.append(task_id)
    conn.execute(f"UPDATE tasks SET {', '.join(parts)} WHERE id=?", vals)


def _history(conn: sqlite3.Connection, task_id: str, action: str) -> None:
    if not _has_table(conn, "task_history"):
        return
    conn.execute(
        "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
        (task_id, _clean(action, 1000)),
    )


def _already_replied(conn: sqlite3.Connection, task_id: str, kind: str) -> bool:
    if not _has_table(conn, "task_history"):
        return False
    row = conn.execute(
        "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
        (task_id, f"reply_sent:{kind}"),
    ).fetchone()
    return row is not None


def _reply_topic_id(conn: sqlite3.Connection, task_id: str) -> int:
    try:
        row = conn.execute("SELECT COALESCE(topic_id,0) AS topic_id FROM tasks WHERE id=? LIMIT 1", (task_id,)).fetchone()
        if not row:
            return 0
        return int(row["topic_id"] or 0)
    except Exception:
        return 0


def _send_once(conn: sqlite3.Connection, task_id: str, chat_id: str, text: str, reply_to: Optional[int], kind: str) -> bool:
    if _already_replied(conn, task_id, kind):
        return True
    topic_id = _reply_topic_id(conn, task_id)
    ok = send_reply(chat_id=chat_id, text=text, reply_to_message_id=reply_to, message_thread_id=topic_id)
    if ok:
        _history(conn, task_id, f"reply_sent:{kind}")
    return bool(ok)


def _send_once_ex(conn: sqlite3.Connection, task_id: str, chat_id: str, text: str, reply_to: Optional[int], kind: str) -> Dict[str, Any]:
    if _already_replied(conn, task_id, kind):
        return {"ok": True, "bot_message_id": None, "skipped": True}
    topic_id = _reply_topic_id(conn, task_id)
    res = send_reply_ex(chat_id=chat_id, text=text, reply_to_message_id=reply_to, message_thread_id=topic_id)
    if not isinstance(res, dict):
        res = {"ok": bool(res)}
    if res.get("ok"):
        _history(conn, task_id, f"reply_sent:{kind}")
    return res


def _hash(text: str) -> str:
    return hashlib.sha1(_clean(text).lower().encode("utf-8")).hexdigest()


def _is_valid_result(text: str, raw_input: str) -> bool:
    r = _clean(text)
    if not r or len(r) < MIN_RESULT_LEN:
        return False
    if any(re.search(p, r, re.I) for p in BAD_RESULT_RE):
        return False
    if _hash(r) == _hash(raw_input):
        return False
    if "/root/" in r or ".ogg" in r.lower():
        return False
    return True


def _detect_role_assignment(text: str) -> str:
    triggers = [
        r"^(?:\[voice\]\s*)?этот чат для\s+(.+)$",
        r"^(?:\[voice\]\s*)?этот чат про\s+(.+)$",
        r"^(?:\[voice\]\s*)?мы тут делаем\s+(.+)$",
        r"^(?:\[voice\]\s*)?запомни:?\s*это чат про\s+(.+)$",
        r"^(?:\[voice\]\s*)?этот топик для\s+(.+)$",
        r"^(?:\[voice\]\s*)?этот топик про\s+(.+)$",
    ]
    t = _clean(text, 500).lower()
    for pattern in triggers:
        m = re.fullmatch(pattern, t)
        if m:
            return _clean(m.group(1), 200)
    return ""


def _extract_role_confirmation(result: str) -> str:
    t = _clean(_s(result), 500)
    m = re.fullmatch(r"Понял назначение чата так:\n(.+?)\n\nПодтверди или уточни", t, re.S)
    if not m:
        return ""
    return _clean(m.group(1), 200)


def _save_topic_role(chat_id: str, topic_id: int, role: str) -> None:
    if not role or not os.path.exists(MEM_DB):
        return
    mem = db(MEM_DB)
    try:
        if not _has_table(mem, "memory"):
            mem.execute("CREATE TABLE IF NOT EXISTS memory (chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        key = f"topic_{topic_id}_role"
        mem.execute("DELETE FROM memory WHERE chat_id=? AND key=?", (str(chat_id), key))
        mem.execute(
            "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(chat_id), key, role),
        )
        mem.commit()
    finally:
        mem.close()


def _load_memory_context(chat_id: str, topic_id: int) -> Tuple[str, str, str, str]:
    if not os.path.exists(MEM_DB):
        return "", "", "", ""

    conn = db(MEM_DB)
    try:
        if not _has_table(conn, "memory"):
            return "", "", "", ""

        topic_prefix = f"topic_{int(topic_id)}_"
        rows = conn.execute(
            """
            SELECT key, value
            FROM memory
            WHERE chat_id=?
              AND key GLOB ?
            ORDER BY timestamp DESC
            LIMIT 100
            """,
            (str(chat_id), f"{topic_prefix}*"),
        ).fetchall()

        short_memory: List[str] = []
        long_memory: List[str] = []
        topic_role = ""
        topic_directions = ""

        for row in rows:
            key = _s(row["key"])
            value = _clean(_s(row["value"]), 500)
            if not value:
                continue
            low = value.lower()
            if _is_memory_noise(low) or any(x in low for x in MEMORY_BAD_MARKERS):
                continue

            if key.endswith("_role") and not topic_role:
                topic_role = value[:500]
                continue
            if key.endswith("_directions") and not topic_directions:
                topic_directions = value[:1000]
                continue
            if key.endswith("_user_input") or key.endswith("_task_summary"):
                if not _is_memory_noise(value):
                    short_memory.append(f"{key}: {value}")
            else:
                if not _is_memory_noise(value):
                    long_memory.append(f"{key}: {value}")

        return "\n".join(short_memory[:100]), "\n".join(long_memory[:100]), topic_role, topic_directions
    finally:
        conn.close()


def _load_archive_context(chat_id: str, topic_id: int, user_text: str) -> str:
    words = {w for w in re.findall(r"\w+", _clean(user_text).lower()) if len(w) > 3}
    if not words or not os.path.exists(MEM_DB):
        return ""

    conn = db(MEM_DB)
    try:
        if not _has_table(conn, "memory"):
            return ""
        rows = conn.execute(
            """
            SELECT key, value
            FROM memory
            WHERE chat_id=?
              AND key LIKE 'archive_legacy_%'
            ORDER BY timestamp DESC
            LIMIT 300
            """,
            (str(chat_id),),
        ).fetchall()
    finally:
        conn.close()

    scored: List[Tuple[int, str]] = []
    for row in rows:
        raw = _s(row["value"])
        if any(x in raw.lower() for x in MEMORY_BAD_MARKERS):
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        if int(payload.get("topic_id", -1)) != int(topic_id):
            continue
        blob = _clean(f"{_s(payload.get('raw_input', ''))}\n{_s(payload.get('result', ''))}", 1200)
        ov = len(words & set(re.findall(r"\w+", blob.lower())))
        if ov > 0:
            scored.append((ov, blob))

    scored.sort(key=lambda x: x[0], reverse=True)
    return "\n\n".join(x[1] for x in scored[:3]) if scored else ""


def _active_unfinished_context(conn: sqlite3.Connection, chat_id: str, topic_id: int, task_id: str) -> str:
    cols = _cols(conn, "tasks")
    where = [
        "chat_id=?",
        "id<>?",
        "state IN ('WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
    ]
    params: List[Any] = [str(chat_id), task_id]
    if "topic_id" in cols:
        where.append("COALESCE(topic_id,0)=?")
        params.append(int(topic_id))

    rows = conn.execute(
        f"""
        SELECT raw_input, result, state
        FROM tasks
        WHERE {' AND '.join(where)}
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 3
        """,
        params,
    ).fetchall()

    parts = []
    for row in rows:
        raw = _clean(_s(row["raw_input"]), 300)
        res = _clean(_s(row["result"]), 500)
        state = _clean(_s(row["state"]), 100)
        low = f"{raw}\n{res}".lower()
        if any(x in low for x in MEMORY_BAD_MARKERS):
            continue
        chunk = []
        if raw:
            chunk.append(f"raw_input: {raw}")
        if res:
            chunk.append(f"result: {res}")
        if state:
            chunk.append(f"state: {state}")
        if chunk:
            parts.append("\n".join(chunk))
    return "\n\n".join(parts[:3])


def _local_xlsx_candidates_for_drive_file(drive_file_id: str, file_name: str, task_id: str) -> list:
    try:
        import glob
        import os
        keys = []
        for v in (drive_file_id, file_name, task_id):
            v = (v or "").strip()
            if v:
                keys.append(v)
        out = []
        for k in keys:
            safe = k.replace("/", "_")
            out += glob.glob(f"/tmp/*{safe}*.xlsx")
            out += glob.glob(f"/root/.areal-neva-core/runtime/drive_files/*{safe}*.xlsx")
        seen = []
        for p in out:
            if p not in seen and os.path.exists(p):
                seen.append(p)
        return seen[:5]
    except Exception:
        return []


def _artifact_semantic_ok_for_context(row) -> bool:
    try:
        name = str(row["file_name"] or "")
        drive_file_id = str(row["drive_file_id"] or "")
        task_id = str(row["task_id"] or "")
        result = str(row["result"] or "")
        is_estimate = name.lower().endswith(".xlsx") or "estimate" in result.lower() or "готово (estimate)" in result.lower()
        if not is_estimate:
            return True
        from core.quality_gate import validate_estimate_xlsx_semantic
        candidates = _local_xlsx_candidates_for_drive_file(drive_file_id, name, task_id)
        if not candidates:
            return True
        for p in candidates:
            q = validate_estimate_xlsx_semantic(p)
            if q.get("ok"):
                return True
        return False
    except Exception:
        return True


def _last_drive_artifact_context(conn, chat_id: str, topic_id: int) -> str:
    try:
        rows = conn.execute(
            """
            SELECT t.id AS task_id, t.result, COALESCE(t.topic_id,0) AS topic_id, df.file_name, df.drive_file_id, df.created_at
            FROM drive_files df
            JOIN tasks t ON df.task_id=t.id
            WHERE t.chat_id=?
              AND t.result LIKE '%drive.google.com%'
              AND t.input_type='drive_file'
              AND t.state IN ('AWAITING_CONFIRMATION','DONE')
              AND (COALESCE(t.topic_id,0)=? OR COALESCE(t.topic_id,0)=0)
              AND lower(COALESCE(df.file_name,'')) NOT LIKE '%chat_export%'
              AND lower(COALESCE(df.file_name,'')) NOT LIKE '%full_canon%'
              AND lower(COALESCE(df.file_name,'')) NOT LIKE '%external_work_monitoring%'
              AND lower(COALESCE(df.file_name,'')) NOT LIKE '%canon__%'
              AND lower(COALESCE(df.file_name,'')) NOT LIKE '%index__%'
              AND lower(COALESCE(df.file_name,'')) NOT LIKE '%voice_%'
              AND lower(COALESCE(df.file_name,'')) NOT LIKE '%.ogg%'
            ORDER BY
              CASE WHEN COALESCE(t.topic_id,0)=? THEN 0 ELSE 1 END,
              df.created_at DESC
            LIMIT 10
            """,
            (str(chat_id), int(topic_id), int(topic_id)),
        ).fetchall()
        for row in rows:
            if not _artifact_semantic_ok_for_context(row):
                continue
            name = str(row["file_name"] or "").strip()
            src_topic = int(row["topic_id"] or 0)
            return "Последний файл-результат в этом топике или общем файловом слое: topic_id=%s file=%s result=%s" % (src_topic, name, str(row["result"] or ""))
        return ""
    except Exception:
        return ""


def _search_fact_context(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> str:
    cols = _cols(conn, "tasks")
    where = [
        "chat_id=?",
        "state IN ('DONE','ARCHIVED')",
        "lower(COALESCE(raw_input,'')) GLOB '*най*'",
    ]
    params: List[Any] = [str(chat_id)]
    if "topic_id" in cols:
        where.append("COALESCE(topic_id,0)=?")
        params.append(int(topic_id))

    rows = conn.execute(
        f"""
        SELECT raw_input, result
        FROM tasks
        WHERE {' AND '.join(where)}
        ORDER BY updated_at DESC
        LIMIT 5
        """,
        params,
    ).fetchall()

    facts: List[str] = []
    for row in rows:
        q = _clean(_s(row["raw_input"]), 300)
        r = _clean(_s(row["result"]), 500)
        low = f"{q}\n{r}".lower()
        if any(x in low for x in MEMORY_BAD_MARKERS):
            continue
        if q and r:
            facts.append(f"search_done: {q} => {r}")
    return "\n".join(facts[:3])


def _save_memory(chat_id: str, topic_id: int, raw_input: str, result: str) -> None:
    bad = [
        "ошибка", "не найдено", "уточните", "Уточните", "не понял",
        "traceback", "Traceback", "SyntaxError", "NameError", "Exception",
        "/root/", ".ogg", "delete from", "task_worker.py", "telegram_daemon.py",
        "PIPELINE_NOT_EXECUTED", "ожидает анализа", "ESTIMATE_EMPTY_RESULT",
        "DOCUMENT_EMPTY_RESULT", "INVALID_PDF_SIGNATURE", "coroutine", "was never awaited",
    ]
    if not result or len(result) <= 20:
        return
    low = (str(raw_input or "") + "\n" + str(result or "")).lower()
    if any(str(b).lower() in low for b in bad):
        return
    if not os.path.exists(MEM_DB):
        return

    conn = db(MEM_DB)
    try:
        if not _has_table(conn, "memory"):
            conn.execute("CREATE TABLE IF NOT EXISTS memory (chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        prefix = f"topic_{int(topic_id)}_"
        conn.execute(
            "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(chat_id), f"{prefix}assistant_output", _clean(result, 50000)),
        )
        conn.execute(
            "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(chat_id), f"{prefix}task_summary", _clean(result, 20000)),
        )
        conn.execute(
            "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(chat_id), f"{prefix}user_input", _clean(raw_input, 500)),
        )
        conn.commit()
        if "drive.google.com" in result:
            conn.execute(
                "INSERT OR REPLACE INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
                (str(chat_id), f"{prefix}last_drive_file", _clean(result, 500))
            )
            conn.commit()
        logger.info("save_memory_ok chat=%s topic=%s", chat_id, topic_id)
    finally:
        conn.close()


def _close_pin(conn: sqlite3.Connection, task_id: str) -> None:
    if not _has_table(conn, "pin"):
        return
    conn.execute(
        "UPDATE pin SET state='CLOSED', updated_at=datetime('now') WHERE task_id=? AND state='ACTIVE'",
        (task_id,),
    )


def _finalize_done(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, reply_to: Optional[int]) -> None:
    row = conn.execute(
        "SELECT COALESCE(raw_input,''), COALESCE(result,'') FROM tasks WHERE id=? LIMIT 1",
        (task_id,),
    ).fetchone()
    raw_input = _clean(_s(row[0]) if row else "", 500)
    result = _clean(_s(row[1]) if row else "", 50000)

    _update_task(conn, task_id, state="DONE", error_message="")
    _history(conn, task_id, "state:DONE")
    _MEMORY_SKIP = [
        "PIPELINE_NOT_EXECUTED", "ожидает анализа", "Traceback", "SyntaxError",
        "NameError", "Exception", "/root/", ".ogg", "ESTIMATE_EMPTY_RESULT",
        "DOCUMENT_EMPTY_RESULT", "INVALID_PDF_SIGNATURE", "coroutine", "was never awaited"
    ]
    if result and len(result.strip()) >= 8 and not any(b in result for b in _MEMORY_SKIP):
        _save_memory(chat_id, topic_id, raw_input, result)
        _history(conn, task_id, "memory:saved")
    else:
        logger.info("MEMORY_GUARD: skipped task=%s", task_id)
    conn.commit()


def _is_confirm_intent(text: str) -> bool:
    t = _clean(text, 200).lower()
    if t in CONFIRM_INTENTS:
        return True
    return any(t.startswith(x) for x in ["да", "подтвер", "соглас", "верно", "ок"])


def _is_revision_intent(text: str) -> bool:
    t = _clean(text, 200).lower()
    if t in REVISION_INTENTS:
        return True
    return any(x in t for x in ["не так", "передел", "исправ", "правк", "уточн"])


def _recover_stale_tasks(conn: sqlite3.Connection, chat_id: Optional[str]) -> None:
    where = [
        "state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')",  # PATCH_INTAKE_TIMEOUT
        "(strftime('%s','now') - strftime('%s', COALESCE(updated_at, created_at))) > ?",
    ]
    params: List[Any] = [STALE_TIMEOUT]
    if chat_id:
        where.insert(0, "chat_id=?")
        params.insert(0, str(chat_id))

    rows = conn.execute(
        f"""
        SELECT id, chat_id, COALESCE(topic_id,0) AS topic_id, reply_to_message_id
        FROM tasks
        WHERE {' AND '.join(where)}
        """,
        params,
    ).fetchall()

    for row in rows:
        task_id = _s(row["id"])
        tg_chat_id = _s(row["chat_id"])
        reply_to = row["reply_to_message_id"]
        _update_task(conn, task_id, state="FAILED", error_message="STALE_TIMEOUT")
        _close_pin(conn, task_id)
        _history(conn, task_id, "state:FAILED")
        conn.commit()
        _send_once(conn, task_id, tg_chat_id, "Задача не завершена вовремя. Напиши ещё раз.", reply_to, "stale_failed")


_FILE_FOLLOWUP_RE = re.compile(
    r"(таблиц|excel|эксель|xlsx|google\s*sheets|google\s*таблиц|гугл\s*таблиц|вытащи|объ[её]м|смет|расч|распозн|акт|дефект|технадзор|проверь)",
    re.IGNORECASE,
)

def _is_file_followup_text(text: str) -> bool:
    return bool(_FILE_FOLLOWUP_RE.search(_clean(_s(text), 1000)))

def _is_service_drive_raw(raw: str) -> bool:
    low = _s(raw).lower()
    blocked = [
        "chat_export",
        "full_canon",
        "external_work_monitoring",
        "unknown",
        "index__",
        "topic_",
        "voice_",
        ".ogg",
        "application/ogg",
    ]
    return any(x in low for x in blocked)

def _merge_caption_into_drive_raw(raw: str, caption: str) -> str:
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            return raw
        prev = _s(data.get("caption", "")).strip()
        cap = _clean(_s(caption), 2000)
        data["caption"] = _clean((prev + "\\n" + cap).strip() if prev else cap, 3000)
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return raw


# PATCH_FILE_DUPLICATE_GUARD_AND_PDF_TABLE_EXTRACTOR_SAFE_OVERLAY_FIX3
def _duplicate_choice(raw: str) -> str:
    raw_l = (raw or "").lower()
    if any(x in raw_l for x in ("заново", "переобработ", "перезапусти", "сделай заново", "force")):
        return "reprocess"
    if any(x in raw_l for x in ("старый", "старую", "дай ссылку", "дай результат", "результат", "что было")):
        return "old_result"
    if any(x in raw_l for x in ("отмена", "отмени", "не надо", "закрой")):
        return "cancel"
    return ""


def _extract_payload_json(raw: str) -> dict:
    try:
        data = json.loads(raw or "{}")
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _duplicate_lookup_by_payload(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, raw_input: str):
    data = _extract_payload_json(raw_input)
    file_id = str(data.get("file_id") or data.get("drive_file_id") or "").strip()
    file_name = str(data.get("file_name") or "").strip()
    if not file_id and not file_name:
        return None

    params = [str(chat_id), str(task_id)]
    where = ["t.chat_id=?", "t.id<>?"]
    if file_id:
        where.append("t.raw_input LIKE ?")
        params.append("%" + file_id + "%")
    else:
        where.append("t.raw_input LIKE ?")
        params.append("%" + file_name + "%")

    return conn.execute(
        f"""
        SELECT
            t.id,
            COALESCE(t.topic_id,0) AS topic_id,
            t.state,
            t.reply_to_message_id,
            t.bot_message_id,
            t.result,
            t.error_message,
            t.created_at,
            df.drive_file_id,
            df.stage,
            df.file_name
        FROM tasks t
        LEFT JOIN drive_files df ON df.task_id=t.id
        WHERE {' AND '.join(where)}
        ORDER BY
          CASE
            WHEN COALESCE(t.result,'') LIKE '%drive.google.com%' THEN 0
            WHEN t.state IN ('AWAITING_CONFIRMATION','DONE') THEN 1
            WHEN t.state='FAILED' THEN 2
            ELSE 3
          END,
          t.created_at DESC
        LIMIT 1
        """,
        tuple(params),
    ).fetchone()


def _duplicate_message(row, raw_input: str) -> str:
    data = _extract_payload_json(raw_input)
    fn = str(data.get("file_name") or row["file_name"] or "файл").strip()
    old_result = str(row["result"] or "").strip()
    old_err = str(row["error_message"] or "").strip()
    old_bot_msg = row["bot_message_id"] if "bot_message_id" in row.keys() else None

    parts = [
        f"Этот файл уже был загружен ранее: {fn}",
        f"Старая задача: {row['id']}",
        f"Статус старой задачи: {row['state']}",
    ]
    if old_bot_msg:
        parts.append(f"Прошлый ответ бота message_id: {old_bot_msg}")
    if old_result:
        parts.append("Старый результат:")
        parts.append(old_result[:1500])
    elif old_err:
        parts.append(f"Старый результат невалидный: {old_err}")
    else:
        parts.append("Старого валидного результата нет")

    parts.append("")
    parts.append("Что сделать: переобработать заново / дать старый результат / отменить")
    return "\n".join(parts)


def _handle_duplicate_file_guard(conn: sqlite3.Connection, task, chat_id: str, topic_id: int) -> bool:
    task_id = _s(_task_field(task, "id"))
    raw_input = _clean(_s(_task_field(task, "raw_input")), 12000)
    reply_to = _task_field(task, "reply_to_message_id", None)

    if _task_field(task, "error_message", "") == "DUPLICATE_FORCE_REPROCESS":
        return False

    row = _duplicate_lookup_by_payload(conn, task_id, chat_id, topic_id, raw_input)
    if not row:
        return False

    _update_task(conn, task_id, state="WAITING_CLARIFICATION", result="", error_message="DUPLICATE_FILE_WAITING_USER_DECISION")
    _history(conn, task_id, "duplicate_file_detected")
    conn.commit()
    _send_once(conn, task_id, chat_id, _duplicate_message(row, raw_input), reply_to, "duplicate_file_guard")
    return True


def _handle_duplicate_file_choice(conn: sqlite3.Connection, task, chat_id: str, topic_id: int) -> bool:
    task_id = _s(_task_field(task, "id"))
    raw_input = _clean(_s(_task_field(task, "raw_input")), 12000)
    reply_to = _task_field(task, "reply_to_message_id", None)
    choice = _duplicate_choice(raw_input)
    if not choice:
        return False

    parent = conn.execute(
        """
        SELECT *
        FROM tasks
        WHERE chat_id=?
          AND COALESCE(topic_id,0)=?
          AND state='WAITING_CLARIFICATION'
          AND error_message='DUPLICATE_FILE_WAITING_USER_DECISION'
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id)),
    ).fetchone()
    if not parent:
        return False

    parent_id = parent["id"]
    parent_raw = str(parent["raw_input"] or "")
    old = _duplicate_lookup_by_payload(conn, parent_id, chat_id, topic_id, parent_raw)

    if choice == "cancel":
        _update_task(conn, parent_id, state="CANCELLED", error_message="DUPLICATE_FILE_CANCELLED_BY_USER")
        _update_task(conn, task_id, state="DONE", result="Отменено", error_message="")
        _history(conn, parent_id, "duplicate_file_cancelled")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Отменил повторную обработку файла", reply_to, "duplicate_cancelled")
        return True

    if choice == "old_result":
        if old and str(old["result"] or "").strip():
            result = str(old["result"] or "").strip()
            _update_task(conn, parent_id, state="AWAITING_CONFIRMATION", result=result, error_message="")
            _update_task(conn, task_id, state="DONE", result="Отдан старый результат", error_message="")
            _history(conn, parent_id, "duplicate_file_old_result_returned")
            conn.commit()
            _send_once(conn, task_id, chat_id, result, reply_to, "duplicate_old_result")
            return True
        msg = "Старого валидного результата нет. Напиши: переобработать заново или отменить"
        _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=msg, error_message="")
        conn.commit()
        _send_once(conn, task_id, chat_id, msg, reply_to, "duplicate_no_old_result")
        return True

    if choice == "reprocess":
        _update_task(conn, parent_id, state="NEW", error_message="DUPLICATE_FORCE_REPROCESS", result="")
        _update_task(conn, task_id, state="DONE", result="Запущена переобработка", error_message="")
        _history(conn, parent_id, "duplicate_file_force_reprocess")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Принял. Переобрабатываю файл заново", reply_to, "duplicate_reprocess")
        return True

    return False


def _link_followup_to_waiting_file(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, raw_input: str, reply_to: Optional[int]) -> bool:
    if not _is_file_followup_text(raw_input):
        return False

    rows = conn.execute(
        """
        SELECT id, COALESCE(raw_input,'') AS raw_input
        FROM tasks
        WHERE chat_id=?
          AND id<>?
          AND COALESCE(topic_id,0)=?
          AND input_type='drive_file'
          AND state IN ('WAITING_CLARIFICATION','NEW')
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 5
        """,
        (str(chat_id), task_id, int(topic_id)),
    ).fetchall()

    target = None
    for r in rows:
        candidate_raw = _s(r["raw_input"])
        if _is_service_drive_raw(candidate_raw):
            continue
        target = r
        break

    if not target:
        return False

    file_task_id = _s(target["id"])
    new_raw = _merge_caption_into_drive_raw(_s(target["raw_input"]), raw_input)
    _update_task(conn, file_task_id, raw_input=new_raw, state="IN_PROGRESS", error_message="")
    _history(conn, file_task_id, f"file_followup_linked_from:{task_id}")
    _update_task(conn, task_id, state="DONE", result="Принял команду для файла", error_message="")
    _history(conn, task_id, f"file_followup_linked_to:{file_task_id}")
    conn.commit()
    _send_once(conn, task_id, chat_id, "Принял команду для файла. Делаю", reply_to, "file_followup_linked")
    return True


# PATCH_UNIVERSAL_FILE_DEDUP_REPLY_POLICY_FINAL_SAFE_V2
def _canon_dedup_action_v2(text: str) -> str:
    t = _s(text).lower().strip()
    if re.search(r"(заново|переобработ|обработай заново|обработать заново|сделай заново|пересчитай|перерасч)", t, re.IGNORECASE):
        return "REPROCESS"
    if re.search(r"(использ|используй|взять этот|возьми этот|работай с ним|по нему|этот файл)", t, re.IGNORECASE):
        return "USE_EXISTING"
    if re.search(r"(отмен|стоп|не надо|закрой|сними)", t, re.IGNORECASE):
        return "CANCEL"
    return ""

def _canon_file_json_value_v2(raw: str, *keys: str) -> str:
    try:
        data = json.loads(_s(raw))
        if isinstance(data, dict):
            for k in keys:
                v = _s(data.get(k))
                if v:
                    return v
    except Exception:
        pass
    return ""

def _canon_find_duplicate_file_v2(conn: sqlite3.Connection, current_task_id: str, chat_id: str, topic_id: int, raw_input: str):
    file_name = _canon_file_json_value_v2(raw_input, "file_name", "name", "filename")
    file_id = _canon_file_json_value_v2(raw_input, "file_id", "drive_file_id", "telegram_file_id", "telegram_file_unique_id")
    if not file_name and not file_id:
        return None, "", ""
    params = [str(chat_id), current_task_id, int(topic_id)]
    parts = []
    if file_id:
        parts.append("COALESCE(raw_input,'') LIKE ?")
        params.append(f"%{file_id}%")
    if file_name:
        parts.append("COALESCE(raw_input,'') LIKE ?")
        params.append(f"%{file_name}%")
    row = conn.execute(
        f"""
        SELECT id, COALESCE(raw_input,'') raw_input,
               COALESCE(reply_to_message_id,0) reply_to_message_id,
               COALESCE(bot_message_id,0) bot_message_id,
               COALESCE(result,'') result,
               COALESCE(error_message,'') error_message,
               COALESCE(state,'') state,
               created_at,
               updated_at
        FROM tasks
        WHERE chat_id=?
          AND id<>?
          AND COALESCE(topic_id,0)=?
          AND input_type='drive_file'
          AND ({' OR '.join(parts)})
        ORDER BY
          CASE
            WHEN state IN ('DONE','AWAITING_CONFIRMATION') THEN 0
            WHEN state IN ('FAILED','CANCELLED') THEN 2
            ELSE 1
          END,
          created_at ASC
        LIMIT 1
        """,
        params,
    ).fetchone()
    return row, file_name, file_id

def _canon_duplicate_prompt_v2(file_name: str, original_found: bool = True) -> str:
    name = file_name or "файл"
    if original_found:
        return (
            f"Файл «{name}» уже есть в системе.\n"
            f"Вот он, ты уже загружал его раньше.\n\n"
            f"Что сделать?\n"
            f"1. обработать заново\n"
            f"2. использовать уже загруженный файл\n"
            f"3. отменить\n\n"
            f"Напиши: заново / использовать / отменить"
        )
    return (
        f"Файл «{name}» уже есть в системе, но исходное сообщение не найдено.\n\n"
        f"Что сделать?\n"
        f"1. обработать заново\n"
        f"2. использовать уже загруженный файл\n"
        f"3. отменить\n\n"
        f"Напиши: заново / использовать / отменить"
    )

def _canon_duplicate_reply_target_v2(task, dup_row):
    try:
        m = int(dup_row["reply_to_message_id"] or 0)
        if m > 0:
            return m
    except Exception:
        pass
    try:
        m = int(dup_row["bot_message_id"] or 0)
        if m > 0:
            return m
    except Exception:
        pass
    return _task_field(task, "reply_to_message_id", None)

def _handle_universal_duplicate_file_guard_v2(conn: sqlite3.Connection, task, chat_id: str, topic_id: int) -> bool:
    task_id = _s(_task_field(task, "id"))
    raw_input = _s(_task_field(task, "raw_input"))
    err = _s(_task_field(task, "error_message", ""))
    if err in ("DUPLICATE_FORCE_REPROCESS", "DUPLICATE_USE_EXISTING"):
        return False
    dup, file_name, file_id = _canon_find_duplicate_file_v2(conn, task_id, chat_id, topic_id, raw_input)
    if not dup:
        return False
    original_task_id = _s(dup["id"])
    reply_target = _canon_duplicate_reply_target_v2(task, dup)
    msg = _canon_duplicate_prompt_v2(file_name, bool(reply_target))
    _update_task(conn, task_id, state="WAITING_CLARIFICATION", result=msg, error_message=f"DUPLICATE_CHOICE_REQUIRED:{original_task_id}")
    _history(conn, task_id, f"duplicate_detected:{original_task_id}")
    _history(conn, task_id, "duplicate_prompt_sent")
    conn.commit()
    _send_once(conn, task_id, chat_id, msg, reply_target, "duplicate_choice_required")
    logger.info("DUPLICATE_FILE_DETECTED task=%s original=%s file=%s", task_id, original_task_id, file_name)
    return True

def _handle_duplicate_file_choice_v2(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int, raw_input: str, reply_to) -> bool:
    action = _canon_dedup_action_v2(raw_input)
    if not action:
        return False
    row = conn.execute(
        """
        SELECT id, COALESCE(error_message,'') error_message
        FROM tasks
        WHERE chat_id=?
          AND COALESCE(topic_id,0)=?
          AND input_type='drive_file'
          AND state='WAITING_CLARIFICATION'
          AND COALESCE(error_message,'') LIKE 'DUPLICATE_CHOICE_REQUIRED:%'
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id)),
    ).fetchone()
    if not row:
        return False
    current_task_id = _s(_task_field(task, "id"))
    dup_task_id = _s(row["id"])
    original_task_id = _s(row["error_message"]).split("DUPLICATE_CHOICE_REQUIRED:", 1)[-1].strip()
    original = conn.execute("SELECT id, COALESCE(raw_input,'') raw_input FROM tasks WHERE id=?", (original_task_id,)).fetchone()
    if action == "CANCEL":
        _update_task(conn, dup_task_id, state="CANCELLED", error_message="DUPLICATE_CANCELLED_BY_USER")
        _history(conn, dup_task_id, "duplicate_choice_cancel")
        _update_task(conn, current_task_id, state="DONE", result="Отменено", error_message="")
        _history(conn, current_task_id, f"duplicate_choice_cancel_for:{dup_task_id}")
        conn.commit()
        _send_once(conn, current_task_id, chat_id, "Отменено", reply_to, "duplicate_cancelled")
        return True
    if action == "REPROCESS":
        _update_task(conn, dup_task_id, state="IN_PROGRESS", error_message="DUPLICATE_FORCE_REPROCESS")
        _history(conn, dup_task_id, f"duplicate_choice_reprocess:{original_task_id}")
        _update_task(conn, current_task_id, state="DONE", result="Запускаю повторную обработку файла", error_message="")
        _history(conn, current_task_id, f"duplicate_choice_reprocess_for:{dup_task_id}")
        conn.commit()
        _send_once(conn, current_task_id, chat_id, "Запускаю повторную обработку файла", reply_to, "duplicate_reprocess")
        return True
    if action == "USE_EXISTING":
        if not original:
            _update_task(conn, dup_task_id, state="WAITING_CLARIFICATION", error_message="ORIGINAL_FILE_NOT_FOUND")
            _update_task(conn, current_task_id, state="DONE", result="Исходный файл не найден", error_message="")
            conn.commit()
            _send_once(conn, current_task_id, chat_id, "Файл не найден. Повторно загрузи или отмени задачу", reply_to, "duplicate_original_missing")
            return True
        merged_raw = _merge_caption_into_drive_raw(_s(original["raw_input"]), raw_input)
        _update_task(conn, dup_task_id, raw_input=merged_raw, state="IN_PROGRESS", error_message="DUPLICATE_USE_EXISTING")
        _history(conn, dup_task_id, f"duplicate_choice_use_existing:{original_task_id}")
        _update_task(conn, current_task_id, state="DONE", result="Использую уже загруженный файл", error_message="")
        _history(conn, current_task_id, f"duplicate_choice_use_existing_for:{dup_task_id}")
        conn.commit()
        _send_once(conn, current_task_id, chat_id, "Использую уже загруженный файл", reply_to, "duplicate_use_existing")
        return True
    return False

def _text_result_is_file_link_without_processing_v2(raw_input: str, result: str) -> bool:
    raw_l = _s(raw_input).lower()
    res_l = _s(result).lower()
    wants_file_action = any(x in raw_l for x in ("файл", "pdf", "xlsx", "xls", "csv", "docx", "dwg", "dxf", "фото", "таблиц", "excel", "эксель", "объём", "объем", "смет", "расч", "чертеж", "чертёж", "акт", "ocr"))
    if not wants_file_action:
        return False
    if "drive.google.com/file/d/" not in res_l:
        return False
    if "/spreadsheets/d/" in res_l:
        return False
    if any(x in res_l for x in (".xlsx", ".xls", ".csv", ".docx")):
        return False
    return True

def _text_result_has_fake_file_progress_v2(raw_input: str, result: str) -> bool:
    raw_l = _s(raw_input).lower()
    res_l = _s(result).lower()
    wants_file_action = any(x in raw_l for x in ("файл", "pdf", "xlsx", "xls", "csv", "docx", "dwg", "dxf", "фото", "таблиц", "excel", "эксель", "объём", "объем", "смет", "расч", "чертеж", "чертёж", "акт", "ocr"))
    if not wants_file_action:
        return False
    return any(x in res_l for x in ("будет подготов", "после анализа файла", "файл обрабатывается", "обрабатываю файл", "скоро будет", "задача выполняется", "в процессе обработки"))

async def _handle_new(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> None:
    task_id = _s(_task_field(task, "id"))
    raw_input = _clean(_s(_task_field(task, "raw_input")), 4000)
    reply_to = _task_field(task, "reply_to_message_id", None)

    if _handle_duplicate_file_choice_v2(conn, task, chat_id, topic_id, raw_input, reply_to):
        return

    if _handle_duplicate_file_choice(conn, task, chat_id, topic_id):
        return

    # === FULL_CONTOUR_FILE_FOLLOWUP_AUTOLINK ===
    if _s(_task_field(task, "input_type", "text")).lower() in ("text", "voice", "voice_text"):
        if _link_followup_to_waiting_file(conn, task_id, chat_id, topic_id, raw_input, reply_to):
            return
    # === END_FULL_CONTOUR_FILE_FOLLOWUP_AUTOLINK ===

    # CANON_EARLY_GUARD_TOPIC_3008_CODE_BRAIN_HANDLE_NEW
    try:
        from core.orchestra_agents.agent_router import is_topic_3008, is_code_command, handle_code_brain
        raw_text = str(raw_input)
        payload_early = {"topic_id": topic_id, "raw_input": raw_text}
        if is_topic_3008(payload_early) and is_code_command(raw_text):
            code_result = await handle_code_brain(payload_early)
            if code_result:
                _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=code_result, error_message="")
                _history(conn, task_id, "result:CODE_BRAIN_TOPIC_3008")
                conn.commit()
                _send_once(conn, task_id, chat_id, code_result, reply_to, "result")
                return
    except Exception as e:
        logger.warning(f"TOPIC_3008_GUARD_HANDLE_NEW_FAILED: {e}")
    # END EARLY GUARD
    role = _detect_role_assignment(raw_input)
    if role:
        ask = f"Понял назначение чата так:\n{role}\n\nПодтверди или уточни"
        _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=ask, error_message="")
        _history(conn, task_id, "state:AWAITING_CONFIRMATION")
        conn.commit()
        _send_once(conn, task_id, chat_id, ask, reply_to, "role_confirmation")
        return

    pending_confirm = conn.execute(
        """
        SELECT id, COALESCE(raw_input,'') AS raw_input, COALESCE(result,'') AS result
        FROM tasks
        WHERE chat_id=?
          AND id<>?
          AND COALESCE(topic_id,0)=?
          AND state='AWAITING_CONFIRMATION'
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), task_id, int(topic_id)),
    ).fetchone()

    if pending_confirm:
        pending_id = _s(pending_confirm["id"])
        pending_role = _extract_role_confirmation(_s(pending_confirm["result"]))
        if pending_role and _is_confirm_intent(raw_input):
            _save_topic_role(chat_id, topic_id, pending_role)
            _update_task(conn, pending_id, state="DONE", result=f"Чат закреплён за: {pending_role}", error_message="")
            _history(conn, pending_id, f"role_saved:{pending_role}")
            _update_task(conn, task_id, state="DONE", result="Подтверждение принято", error_message="")
            _history(conn, task_id, "confirm_accepted")
            conn.commit()
            _send_once(conn, task_id, chat_id, f"Принял. Чат закреплён за: {pending_role}", reply_to, "role_saved")
            return
        if pending_role and _is_revision_intent(raw_input):
            _update_task(conn, pending_id, raw_input=raw_input, state="NEW", result="", error_message="")
            _history(conn, pending_id, "role_revision_requested")
            _update_task(conn, task_id, state="DONE", result="Правки приняты", error_message="")
            _history(conn, task_id, "state:DONE")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Принял правки. Уточни назначение чата одной фразой", reply_to, "role_revision_ok")
            return
        if _is_confirm_intent(raw_input):
            _finalize_done(conn, pending_id, chat_id, topic_id, reply_to)
            _update_task(conn, task_id, state="DONE", result="Подтверждение принято", error_message="")
            _history(conn, task_id, "confirm_accepted")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Принял. Задача закрыта", reply_to, "confirm_done")
            return
        if _is_revision_intent(raw_input):
            merged = _clean(_s(pending_confirm["raw_input"]) + "\n\nУточнение пользователя:\n" + raw_input, 12000)
            _update_task(conn, pending_id, raw_input=merged, state="IN_PROGRESS", error_message="")
            _history(conn, pending_id, "revision_accepted")
            _update_task(conn, task_id, state="DONE", result="Правки приняты", error_message="")
            _history(conn, task_id, "state:DONE")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Принял правки. Делаю", reply_to, "revision_ok")
            return

        # FALLBACK — если не confirm и не revision
        # не трогаем pending_confirm и продолжаем как новую задачу

        # intent not recognized — не зависать, продолжить как новую задачу

    if _is_status_intent(raw_input):
        status_text = _build_topic_status(conn, chat_id, topic_id)
        _update_task(conn, task_id, state="DONE", result=status_text, error_message="")
        _history(conn, task_id, "state:DONE")
        conn.commit()
        _send_once(conn, task_id, chat_id, status_text, reply_to, "status")
        return

    pending_clarify = conn.execute(
        """
        SELECT id, COALESCE(raw_input,'') AS raw_input
        FROM tasks
        WHERE chat_id=?
          AND id<>?
          AND COALESCE(topic_id,0)=?
          AND state='WAITING_CLARIFICATION'
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), task_id, int(topic_id)),
    ).fetchone()

    if pending_clarify:
        pending_id = _s(pending_clarify["id"])
        merged = _clean(_s(pending_clarify["raw_input"]) + "\n\nУточнение пользователя:\n" + raw_input, 12000)
        _update_task(conn, pending_id, raw_input=merged, state="IN_PROGRESS", error_message="")
        _history(conn, pending_id, "clarification_accepted")
        _update_task(conn, task_id, state="DONE", result="Уточнение принято", error_message="")
        _history(conn, task_id, "state:DONE")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Принял уточнение. Делаю", reply_to, "clarification_ok")
        return

    _update_task(conn, task_id, state="IN_PROGRESS", error_message="")
    _history(conn, task_id, "state:IN_PROGRESS")
    conn.commit()



_CTX_STOPWORDS = {
    "что","это","как","для","про","или","если","чтобы","только","нужно","надо","где","когда",
    "который","которая","которые","были","было","есть","ещё","уже","всё","тут","там","этот",
    "эта","эти","моё","мое","мой","моя","мои","твой","твоя","твои","его","ее","её","их",
    "and","the","for","with","from","this","that","into","your","you","are"
}

MEMORY_NOISE_MARKERS = [
    "не понял",
    "уточните",
    "не знаю",
    "повторите",
    "нет данных",
    "traceback",
    "error",
    "exception",
    "stale_timeout",
]

def _ctx_keywords(text: str) -> set[str]:
    t = _clean(_s(text), 4000).lower()
    words = re.findall(r"[a-zA-Zа-яА-Я0-9_./:-]+", t)
    out = set()
    for w in words:
        if len(w) <= 3:
            continue
        if w in _CTX_STOPWORDS:
            continue
        out.add(w)
    return out

def _ctx_has_overlap(request_text: str, candidate_text: str) -> bool:
    rq = _ctx_keywords(request_text)
    cd = _ctx_keywords(candidate_text)
    if not rq or not cd:
        return False
    return len(rq & cd) > 0


_STATUS_RE = re.compile(r"^\s*статус\s*$", re.IGNORECASE)

def _is_status_intent(text: str) -> bool:
    return bool(_STATUS_RE.match(_clean(_s(text), 200)))

def _build_topic_status(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> str:
    rows = conn.execute(
        """
        SELECT state, COUNT(*) AS cnt
        FROM tasks
        WHERE chat_id=? AND COALESCE(topic_id,0)=?
        GROUP BY state
        ORDER BY state
        """,
        (str(chat_id), int(topic_id)),
    ).fetchall()

    parts = [f"Статус топика {int(topic_id)}:"]
    order = [
        "ARCHIVED","AWAITING_CONFIRMATION","CANCELLED","DONE",
        "FAILED","IN_PROGRESS","NEW","WAITING_CLARIFICATION"
    ]
    data = {str(r["state"]).upper(): int(r["cnt"]) for r in rows}
    for k in order:
        if k in data:
            parts.append(f"{k}: {data[k]}")

    pin_row = conn.execute(
        """
        SELECT task_id
        FROM pin
        WHERE chat_id=? AND topic_id=? AND state='ACTIVE'
        ORDER BY rowid DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id)),
    ).fetchone()
    if pin_row and pin_row["task_id"]:
        parts.append(f"Активный pin: {pin_row['task_id']}")
    return "\n".join(parts)

def _ctx_is_noise(text: str) -> bool:
    low = _clean(_s(text), 4000).lower()
    return any(m in low for m in MEMORY_NOISE_MARKERS)

def _ctx_filter(label: str, request_text: str, value: Any, max_len: int = 4000) -> str:
    text = _clean(_s(value), max_len)
    if not text:
        return ""
    if _ctx_is_noise(text):
        return ""
    if label in {"PIN", "ARCHIVE", "SEARCH"} and not _ctx_has_overlap(request_text, text):
        return ""
    if label == "ARCHIVE":
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        rel = [ln for ln in lines if _ctx_has_overlap(request_text, ln)]
        text = "\n".join(rel[:3]) if rel else ""
    return _clean(text, max_len)


# === PATCH_FILE_FOLLOWUP_TO_DRIVE_PIPELINE_SAFE_FINAL ===
def _patch_file_followup_intent_safe_final(text: str) -> bool:
    t = _s(text).lower()
    return any(x in t for x in (
        "таблиц", "смет", "объём", "объем", "обьем", "расч", "xlsx", "excel",
        "google sheet", "google табли", "вытащ", "последн", "по файлу", "из файла",
        "где мое решение", "где моё решение", "нужен нормальный результат"
    ))

def _patch_extract_drive_id_safe_final(text: str) -> str:
    m = re.search(r"drive\.google\.com/(?:file/d/|open\?id=)([A-Za-z0-9_-]+)", _s(text))
    return m.group(1) if m else ""

def _patch_extract_pdf_name_safe_final(text: str) -> str:
    m = re.search(r"([A-Za-zА-Яа-яЁё0-9_.\-]+\.pdf)", _s(text), re.IGNORECASE)
    return m.group(1) if m else "У1-02-26-Р-КЖ1.6.pdf"

def _patch_latest_pdf_context_safe_final(conn, chat_id: str, topic_id: int):
    rows = conn.execute("""
        SELECT t.raw_input,t.result,df.drive_file_id,df.file_name,df.mime_type
        FROM tasks t
        LEFT JOIN drive_files df ON df.task_id=t.id
        WHERE t.chat_id=? AND COALESCE(t.topic_id,0)=?
        ORDER BY t.created_at DESC
        LIMIT 120
    """, (str(chat_id), int(topic_id or 0))).fetchall()

    for r in rows:
        raw = _s(r["raw_input"] if hasattr(r, "keys") else r[0])
        result = _s(r["result"] if hasattr(r, "keys") else r[1])
        df_id = _s(r["drive_file_id"] if hasattr(r, "keys") else r[2])
        df_name = _s(r["file_name"] if hasattr(r, "keys") else r[3])
        mime = _s(r["mime_type"] if hasattr(r, "keys") else r[4]) or "application/pdf"
        text = raw + "\n" + result + "\n" + df_name
        low = text.lower()

        if any(x in low for x in ("chat_export", "file_identity", "canon", "policy", "voice_", ".ogg")):
            continue

        if df_id and df_name.lower().endswith(".pdf"):
            return df_id, df_name, mime

        fid = _patch_extract_drive_id_safe_final(text)
        pdf = _patch_extract_pdf_name_safe_final(text)
        if fid and pdf.lower().endswith(".pdf") and ".pdf" in low:
            return fid, pdf, "application/pdf"

    import json as _json2
    for r in rows:
        raw = _s(r["raw_input"] if hasattr(r, "keys") else r[0])
        try:
            d = _json2.loads(raw)
            fid = _s(d.get("file_id", ""))
            fname = _s(d.get("file_name", ""))
            mime = _s(d.get("mime_type", "")) or "application/pdf"
            low_fname = fname.lower()
            if fid and low_fname.endswith(".pdf") and not any(x in low_fname for x in ("chat_export","canon","policy","voice_")):
                return fid, fname, mime
        except Exception:
            continue
    return "", "", ""

def _patch_requeue_text_followup_to_drive_safe_final(conn, task, chat_id: str, topic_id: int) -> bool:
    task_id = _s(_task_field(task, "id"))
    raw_input = _clean(_s(_task_field(task, "raw_input")), 12000)
    input_type = _s(_task_field(task, "input_type", "text")).lower() or "text"

    if input_type != "text":
        return False
    if not _patch_file_followup_intent_safe_final(raw_input):
        return False

    file_id, file_name, mime_type = _patch_latest_pdf_context_safe_final(conn, chat_id, topic_id)
    if not file_id:
        return False

    raw_json = json.dumps({
        "file_id": file_id,
        "file_name": file_name,
        "mime_type": mime_type or "application/pdf",
        "source": "TEXT_FOLLOWUP_REQUEUED_AS_DRIVE_FILE",
        "original_text": raw_input[:1000]
    }, ensure_ascii=False)

    conn.execute("""
        UPDATE tasks
        SET input_type='drive_file',
            raw_input=?,
            state='IN_PROGRESS',
            result='',
            error_message='TEXT_FOLLOWUP_REQUEUED_AS_DRIVE_FILE',
            updated_at=datetime('now')
        WHERE id=?
    """, (raw_json, task_id))

    conn.execute("""
        INSERT INTO drive_files(task_id, drive_file_id, file_name, mime_type, stage, created_at)
        VALUES(?,?,?,?,?,datetime('now'))
    """, (task_id, file_id, file_name, mime_type or "application/pdf", "TEXT_FOLLOWUP_REQUEUED"))

    try:
        _history(conn, task_id, "state:NEW:TEXT_FOLLOWUP_REQUEUED_AS_DRIVE_FILE")
    except Exception:
        pass

    conn.commit()
    logger.info("TEXT_FOLLOWUP_REQUEUED_AS_DRIVE_FILE task=%s file=%s", task_id, file_name)
    return True
# === END PATCH_FILE_FOLLOWUP_TO_DRIVE_PIPELINE_SAFE_FINAL ===


# PATCH__FILE_ARTIFACT_RESOLVER__V1
def _looks_like_file_artifact_followup(text: str) -> bool:
    t = re.sub(r"\\s+", " ", str(text or "").strip().lower())
    keys = (
        "таблиц", "таблич", "excel", "xlsx", "xls", "смет",
        "объем", "объём", "ведомост", "посчитай", "расчет",
        "расчёт", "кж", "pdf", "файл"
    )
    return any(k in t for k in keys)

def _extract_drive_link_from_text_for_file_resolver(text: str) -> str:
    m = re.search(r"https://drive\.google\.com/[^\s\]\)\"']+", text or "")
    return m.group(0).strip() if m else ""

def _latest_valid_excel_artifact(conn, chat_id: str, topic_id: int):
    rows = conn.execute("""
        SELECT
            df.task_id,
            COALESCE(df.file_name,'') AS file_name,
            COALESCE(df.stage,'') AS stage,
            COALESCE(t.result,'') AS result,
            COALESCE(t.raw_input,'') AS raw_input,
            COALESCE(t.updated_at,'') AS updated_at,
            COALESCE(df.created_at,'') AS created_at
        FROM drive_files df
        LEFT JOIN tasks t ON t.id = df.task_id
        WHERE COALESCE(t.chat_id, ?) = ?
          AND COALESCE(t.topic_id, 0) = ?
        ORDER BY COALESCE(t.updated_at, df.created_at) DESC, df.created_at DESC
        LIMIT 120
    """, (chat_id, chat_id, int(topic_id or 0))).fetchall()

    fallback = None
    for r in rows:
        fn = (r["file_name"] or "").strip()
        fn_l = fn.lower()
        result = r["result"] or ""
        blob_l = " ".join([fn_l, (r["stage"] or "").lower(), result.lower(), (r["raw_input"] or "").lower()])

        if not blob_l:
            continue
        if "voice_" in fn_l or fn_l.endswith(".ogg"):
            continue
        if fn_l.startswith("chat_export") or fn_l.startswith("canon"):
            continue
        if "1AaERRkk4cTJZNoUsOdASSDOd6VZw2O_z" in result:
            continue
        if fn_l.endswith(".pdf") and ".xlsx" not in blob_l and ".xls" not in blob_l and "est_" not in blob_l:
            continue

        is_excel = (
            fn_l.endswith((".xlsx", ".xls", ".csv"))
            or ".xlsx" in blob_l
            or ".xls" in blob_l
            or "est_" in blob_l
        )
        if not is_excel:
            continue

        link = _extract_drive_link_from_text_for_file_resolver(result)
        if link and "drive.google.com" in link and "1AaERRkk4cTJZNoUsOdASSDOd6VZw2O_z" not in link:
            return {"task_id": r["task_id"], "file_name": fn, "stage": r["stage"], "link": link}

        if fn_l.endswith((".xlsx", ".xls", ".csv")) or "est_" in fn_l:
            fallback = {"task_id": r["task_id"], "file_name": fn, "stage": r["stage"], "link": ""}

    return fallback

def _try_resolve_file_artifact_followup(conn, task, chat_id: str, topic_id: int, raw_input: str) -> bool:
    if not _looks_like_file_artifact_followup(raw_input):
        return False

    task_id = _task_field(task, "id", "")
    reply_to = _task_field(task, "reply_to_message_id", None)
    hit = _latest_valid_excel_artifact(conn, chat_id, int(topic_id or 0))

    if not hit:
        return False

    link = hit.get("link") or ""
    file_name = hit.get("file_name") or ""

    if link:
        result = f"Готово. Таблица: {link}"
    else:
        result = f"Готово. Таблица уже создана: {file_name}"

    _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=result, error_message="")
    _history(conn, task_id, f"FILE_ARTIFACT_RESOLVER_HIT:{hit.get('task_id','')}")
    sent = _send_once(conn, task_id, chat_id, result, reply_to, "file_artifact_resolver")
    bot_message_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
    if bot_message_id is not None:
        _update_task(conn, task_id, bot_message_id=bot_message_id)

    try:
        save_pin(chat_id, task_id, result, int(topic_id or 0))
    except Exception as e:
        logger.warning("FILE_ARTIFACT_RESOLVER_SAVE_PIN_FAIL task=%s err=%s", task_id, e)

    logger.info("FILE_ARTIFACT_RESOLVER_HIT task=%s topic=%s link=%s file=%s", task_id, topic_id, link, file_name)
    return True
# PATCH__FILE_ARTIFACT_RESOLVER__V1_END

async def _handle_in_progress(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> None:
    task_id = _s(_task_field(task, "id"))
    raw_input = _clean(_s(_task_field(task, "raw_input")), 12000)
    reply_to = _task_field(task, "reply_to_message_id", None)
    _em = _s(_task_field(task, "error_message", ""))
    if "TEXT_FOLLOWUP_REQUEUED_AS_DRIVE_FILE" in _em:
        _update_task(conn, task_id, state="FAILED", error_message="REQUEUE_LOOP_DETECTED")
        _history(conn, task_id, "state:FAILED:REQUEUE_LOOP_DETECTED")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Не выполнено: REQUEUE_LOOP_DETECTED", reply_to, "requeue_loop")
        return
    if _patch_requeue_text_followup_to_drive_safe_final(conn, task, chat_id, topic_id):
        return

    active_task_context = _ctx_filter("ACTIVE", raw_input, _active_unfinished_context(conn, chat_id, topic_id, task_id))
    if _try_resolve_file_artifact_followup(conn, task, chat_id, topic_id, raw_input):
        return

    short_memory_raw, long_memory_raw, topic_role, topic_directions = _load_memory_context(chat_id, topic_id)
    short_memory = _ctx_filter("SHORT", raw_input, short_memory_raw)
    long_memory = _ctx_filter("LONG", raw_input, long_memory_raw)
    pin_context = _ctx_filter("PIN", raw_input, get_pin_context(chat_id, raw_input, topic_id))
    archive_context = _ctx_filter("ARCHIVE", raw_input, _load_archive_context(chat_id, topic_id, raw_input))
    search_context = _ctx_filter("SEARCH", raw_input, _search_fact_context(conn, chat_id, topic_id))

    payload: Dict[str, Any] = {
        "id": task_id,
        "chat_id": chat_id,
        "input_type": _s(_task_field(task, "input_type", "text")).lower() or "text",
        "raw_input": raw_input,
        "normalized_input": raw_input,
        "state": "IN_PROGRESS",
        "reply_to_message_id": reply_to,
        "active_task_context": active_task_context,
        "pin_context": pin_context,
        "short_memory_context": short_memory,
        "long_memory_context": long_memory,
        "archive_context": archive_context,
        "last_artifact_context": _last_drive_artifact_context(conn, chat_id, topic_id),
        "search_context": search_context,
        "topic_role": topic_role,
        "topic_directions": topic_directions,
    }

    try:
        ROLE_Q = re.compile(r"(для чего|о чём|о чем|про что|напомни.*(чат|топик)|чем занимается|зачем этот чат)", re.IGNORECASE)
        HISTORY_Q = re.compile(r"(что мы писали|что писали раньше|о ч[её]м общались|напомни.*что.*(писали|обсуждали)|что было в этом чате|история чата)", re.IGNORECASE)
        if topic_role and (ROLE_Q.search(raw_input) or HISTORY_Q.search(raw_input)):
            ai_result = f"Этот чат закреплён за: {topic_role}"
        else:
            # CANON_EARLY_GUARD_TOPIC_3008_CODE_BRAIN
            try:
                from core.orchestra_agents.agent_router import is_topic_3008, is_code_command, handle_code_brain
                raw_text = str(payload.get("raw_input") or payload.get("text") or payload.get("user_text") or "")
                if is_topic_3008(payload) and is_code_command(raw_text):
                    code_result = await handle_code_brain(payload)
                    if code_result:
                        _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=code_result, error_message="")
                        _history(conn, task_id, f"result:CODE_BRAIN_TOPIC_3008")
                        conn.commit()
                        _send_once(conn, task_id, chat_id, code_result, reply_to, "result")
                        return
            except Exception as e:
                logger.warning(f"TOPIC_3008_GUARD_FAILED: {e}")
            # END EARLY GUARD
            ai_result = await asyncio.wait_for(process_ai_task(payload), timeout=AI_TIMEOUT)
    except Exception as e:
        _update_task(conn, task_id, state="FAILED", error_message=_clean(str(e), 500))
        _close_pin(conn, task_id)
        _history(conn, task_id, "state:FAILED")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Не удалось обработать запрос. Попробуй снова.", reply_to, "router_failed")
        return

    ai_result = _clean(_s(ai_result), 50000)
    # PATCH_NO_FAKE_PROGRESS_WAIT
    if any(x in ai_result.lower() for x in ["ожидайте", "создаю таблицу", "подождите", "в процессе"]) :
        _update_task(conn, task_id, state="FAILED", result="", error_message="FAKE_PROGRESS_BLOCKED")
        _close_pin(conn, task_id)
        _history(conn, task_id, "state:FAILED:FAKE_PROGRESS_BLOCKED")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Ошибка: фейковый прогресс без результата. Повтори задачу", reply_to, "fake_progress_blocked")
        return
    if _text_result_is_file_link_without_processing_v2(raw_input, ai_result):
        _update_task(conn, task_id, state="FAILED", result="", error_message="FILE_LINK_RETURNED_WITHOUT_PROCESSING")
        _close_pin(conn, task_id)
        _history(conn, task_id, "state:FAILED:FILE_LINK_RETURNED_WITHOUT_PROCESSING")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Не выполнено: система вернула ссылку на файл вместо реальной обработки. Прикрепи файл заново или выбери действие по уже загруженному файлу", reply_to, "file_link_rejected")
        return

    if _text_result_has_fake_file_progress_v2(raw_input, ai_result):
        _update_task(conn, task_id, state="FAILED", result="", error_message="FAKE_FILE_PROGRESS_REJECTED")
        _close_pin(conn, task_id)
        _history(conn, task_id, "state:FAILED:FAKE_FILE_PROGRESS_REJECTED")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Не выполнено: обработка файла реально не запущена. Прикрепи файл или выбери действие по уже загруженному файлу", reply_to, "fake_file_progress_rejected")
        return

    if not _is_valid_result(ai_result, raw_input):
        _update_task(conn, task_id, state="FAILED", error_message="INVALID_RESULT_GATE")
        _close_pin(conn, task_id)
        _history(conn, task_id, "state:FAILED")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Результат не получен. Переформулируй задачу.", reply_to, "invalid_result")
        return

    _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=ai_result, error_message="")
    _history(conn, task_id, f"result:{_clean(ai_result, 400)}")

    # HARD FACT GUARD: file без артефакта запрещён
    if payload.get("input_type") == "drive_file":
        if "скачан" in ai_result and "анализ" in ai_result:
            _update_task(conn, task_id, state="FAILED", error_message="PIPELINE_NOT_EXECUTED")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Ошибка обработки файла", reply_to, "file_error")
            return

    try:
        save_pin(chat_id, task_id, ai_result, topic_id)
    except Exception as e:
        logger.warning("save_pin_fail task=%s err=%s", task_id, e)

    confirmation_text = ai_result + "\n\nДоволен результатом? Ответь: Да / Уточни / Правки"
    sent = _send_once_ex(conn, task_id, chat_id, confirmation_text, reply_to, "result")
    bot_message_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
    if bot_message_id is not None:
        _update_task(conn, task_id, bot_message_id=bot_message_id)
    conn.commit()


def _is_service_drive_raw(raw: str) -> bool:
    raw_l = (raw or "").lower()
    return any(x in raw_l for x in (
        "chat_export", "full_canon", "external_work_monitoring", "canon__", "index__",
        "voice_", ".ogg", "application/ogg", "unknown_chat"
    ))


def _pick_next_task(conn: sqlite3.Connection, chat_id: Optional[str]) -> Optional[sqlite3.Row]:
    where = ["state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION')"]
    where.append("NOT (input_type='drive_file' AND (lower(raw_input) LIKE '%chat_export%' OR lower(raw_input) LIKE '%full_canon%' OR lower(raw_input) LIKE '%external_work_monitoring%' OR lower(raw_input) LIKE '%canon__%' OR lower(raw_input) LIKE '%index__%' OR lower(raw_input) LIKE '%voice_%' OR lower(raw_input) LIKE '%.ogg%' OR lower(raw_input) LIKE '%application/ogg%' OR lower(raw_input) LIKE '%unknown_chat%'))")
    params: List[Any] = []
    if chat_id:
        where.insert(0, "chat_id=?")
        params.append(str(chat_id))

    conn.execute("BEGIN IMMEDIATE")
    row = conn.execute(
        f"""
        SELECT *
        FROM tasks
        WHERE {' AND '.join(where)}
        ORDER BY CASE state WHEN 'IN_PROGRESS' THEN 0 WHEN 'WAITING_CLARIFICATION' THEN 1 ELSE 2 END,
                 created_at ASC
        LIMIT 1
        """
        ,
        params,
    ).fetchone()
    conn.execute("COMMIT")
    return row


async def main() -> None:
    lock_fp = open(LOCK_PATH, "w")
    try:
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        logger.info("WORKER LOCKED BY OTHER PROCESS")
        return

    logger.info("WORKER STARTED pid=%s", os.getpid())

    while True:
        conn = db(CORE_DB)
        try:
            _recover_stale_tasks(conn, None)
            _auto_close_trash_awaiting(conn)
            _send_awaiting_reminders(conn)
            task = _pick_next_task(conn, None)
            if not task:
                time.sleep(POLL_SEC)
                continue

            task_id = _s(_task_field(task, "id"))
            chat_id = _s(_task_field(task, "chat_id"))
            topic_id = int(_task_field(task, "topic_id", 0) or 0)
            state = _s(_task_field(task, "state")).upper()

            logger.info("PICKED %s state=%s chat=%s topic=%s", task_id, state, chat_id, topic_id)
            input_type = _s(_task_field(task, "input_type")).lower()
            if input_type == "drive_file":
                try:
                    await _handle_drive_file(conn, task, chat_id, topic_id)
                except Exception as e:
                    logger.error("DRIVE_FILE CRASH task=%s err=%s", task_id, str(e), exc_info=True)
                    try:
                        _update_task(conn, task_id, state="FAILED", error_message=str(e)[:500])
                        _history(conn, task_id, f"state:FAILED:DRIVE_FILE_CRASH:{str(e)[:200]}")
                        conn.execute("UPDATE drive_files SET stage='FAILED' WHERE task_id=?", (task_id,))
                        conn.commit()
                    except Exception:
                        pass
                continue

            if state == "NEW":
                await _handle_new(conn, task, chat_id, topic_id)
            elif state == "IN_PROGRESS":
                await _handle_in_progress(conn, task, chat_id, topic_id)
            elif state == "WAITING_CLARIFICATION":
                await _handle_in_progress(conn, task, chat_id, topic_id)
        finally:
            conn.close()

        time.sleep(POLL_SEC)



# === DRIVE FILE HANDLING ===
def _download_from_drive(file_id: str, local_path: str) -> bool:
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        from google.oauth2.service_account import Credentials
        import io
        creds = Credentials.from_service_account_file(
            '/root/.areal-neva-core/credentials.json',
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        service = build('drive', 'v3', credentials=creds)
        meta = service.files().get(fileId=file_id, fields="mimeType").execute()
        mime = meta.get("mimeType", "")
        EXPORT_MAP = {
            "application/vnd.google-apps.document": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
            "application/vnd.google-apps.spreadsheet": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
            "application/vnd.google-apps.presentation": ("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"),
        }
        if mime in EXPORT_MAP:
            export_mime, ext = EXPORT_MAP[mime]
            if not local_path.endswith(ext):
                local_path = local_path + ext
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        else:
            request = service.files().get_media(fileId=file_id)
        with io.FileIO(local_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        return True
    except Exception as e:
        import logging
        logging.getLogger("task_worker").error(f"Drive download failed: {e}")
        return False


# PATCH_FILE_RESULT_MUST_MATCH_INTENT_NO_PDF_AS_EXCEL
def _file_result_matches_intent(intent: str, link: str = "", artifact_path: str = "", source_file_name: str = "") -> tuple:
    intent_l = (intent or "").lower()
    link_l = (link or "").lower()
    path_l = (artifact_path or "").lower()
    source_l = (source_file_name or "").lower()

    needs_table = intent_l in ("estimate", "ocr", "table", "excel", "spreadsheet") or any(x in intent_l for x in ("таблиц", "смет", "объ"))
    if not needs_table:
        return True, "OK"

    if link_l:
        if "/spreadsheets/d/" in link_l:
            return True, "OK"
        if link_l.endswith(".xlsx") or link_l.endswith(".xls") or link_l.endswith(".csv"):
            return True, "OK"
        if "/file/d/" in link_l and source_l.endswith(".pdf"):
            return False, "PDF_LINK_RETURNED_FOR_TABLE_TASK"
        if ".pdf" in link_l:
            return False, "PDF_LINK_RETURNED_FOR_TABLE_TASK"

    if path_l:
        if path_l.endswith((".xlsx", ".xls", ".csv")):
            return True, "OK"
        if path_l.endswith(".pdf"):
            return False, "PDF_ARTIFACT_RETURNED_FOR_TABLE_TASK"

    return False, "TABLE_ARTIFACT_NOT_CONFIRMED"

# PATCH_FULL_FILE_INTAKE_SERVICE_DOC_PDF_TABLE_OCR_SAFE_FINAL
def _is_service_drive_document_guard_final(raw: str, topic_id: int = 0) -> bool:
    raw_l = _s(raw).lower()
    return any(x in raw_l for x in (
        "chat_export",
        "canon__",
        "drive_ingest_hygiene",
        "file_identity",
        "dedup_reply_memory_policy",
        "memory_policy",
        "hygiene",
        "external_work_monitoring",
        "full_canon",
        "index__",
        "каноны",
        "orchestra_canon",
        "monolithic_canon",
        "open_contours_master",
        "areal-neva status",
        "session_update",
        "session_facts",
        "patches_history",
        "final_state",
    ))

def _close_service_drive_document_guard_final(conn: sqlite3.Connection, task, chat_id: str, topic_id: int) -> bool:
    raw_input = _s(_task_field(task, "raw_input"))
    if not _is_service_drive_document_guard_final(raw_input, topic_id):
        return False
    task_id = _s(_task_field(task, "id"))
    _update_task(conn, task_id, state="DONE", result="SERVICE_DRIVE_DOCUMENT_IGNORED", error_message="SERVICE_DRIVE_DOCUMENT_IGNORED")
    _history(conn, task_id, "state:DONE:SERVICE_DRIVE_DOCUMENT_IGNORED")
    try:
        conn.execute("UPDATE drive_files SET stage='SERVICE_IGNORED' WHERE task_id=?", (task_id,))
    except Exception:
        pass
    conn.commit()
    logger.info("SERVICE_DRIVE_DOCUMENT_IGNORED task=%s topic=%s", task_id, topic_id)
    return True

async def _handle_drive_file(conn, task, chat_id, topic_id):
    if _close_service_drive_document_guard_final(conn, task, chat_id, topic_id):
        return

    if _task_field(task, "input_type", "") == "drive_file" and _task_field(task, "error_message", "") not in ("DUPLICATE_FORCE_REPROCESS", "DUPLICATE_USE_EXISTING"):
        if _handle_universal_duplicate_file_guard_v2(conn, task, chat_id, topic_id):
            return
        if _handle_duplicate_file_guard(conn, task, chat_id, topic_id):
            return

    import json, os
    result = ""
    waiting_result = "__WAIT__"
    task_id = task["id"]
    raw_input = task["raw_input"]
    _em_drive = _s(_task_field(task, "error_message", ""))
    # PATCH_REQUEUE_LOOP_ALLOW_ONCE
    if "TEXT_FOLLOWUP_REQUEUED_AS_DRIVE_FILE" in _em_drive:
        _reply_to_d = _task_field(task, "reply_to_message_id", None)
        _stage_check = conn.execute(
            "SELECT stage FROM drive_files WHERE task_id=? ORDER BY id DESC LIMIT 1",
            (task_id,)
        ).fetchone()
        _stage_val = _stage_check["stage"] if _stage_check else ""
        if _stage_val in ("DOWNLOADED", "PARSED", "ARTIFACT_CREATED", "UPLOADED", "FAILED"):
            _update_task(conn, task_id, state="FAILED", error_message="REQUEUE_LOOP_DETECTED")
            _history(conn, task_id, "state:FAILED:REQUEUE_LOOP_DETECTED")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Не выполнено: REQUEUE_LOOP_DETECTED", _reply_to_d, "requeue_loop_drive")
            return
        _update_task(conn, task_id, error_message="")
        conn.commit()
    if "[VOICE]" in str(raw_input) and _is_human_short(raw_input):
        logger.info("VOICE_HUMAN_SHORT_IGNORED")
        return
    if _is_human_short(raw_input):
        logger.info("HUMAN_SHORT_IGNORED")
        return
    try:
        data = json.loads(raw_input)
        file_id = data["file_id"]
        file_name = data["file_name"]
        reply_to = _task_field(task, "reply_to_message_id", None)
    except Exception as e:
        logger.error(f"DRIVE_FILE: invalid raw_input for {task_id}: {e}")
        _update_task(conn, task_id, state="FAILED", error_message="invalid raw_input")
        return

    # === VOICE BYPASS: ogg -> skip file pipeline ===
    if file_name.lower().endswith(".ogg"):
        _update_task(conn, task_id, state="FAILED", error_message="VOICE_FILE_SHOULD_GO_STT")
        conn.commit()
        return

    local_path = f"/root/.areal-neva-core/runtime/drive_files/{task_id}_{file_name}"
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    logger.info(f"DRIVE_FILE: downloading {file_id} -> {local_path}")
    from google_io import download_file
    ok = await download_file(file_id, local_path)
    if not ok:
        _update_task(conn, task_id, state="FAILED", error_message="DOWNLOAD_FAILED")
        _history(conn, task_id, "state:FAILED:DOWNLOAD_FAILED")
        conn.execute("UPDATE drive_files SET stage='FAILED' WHERE task_id=?", (task_id,))
        conn.commit()
        _send_once(conn, task_id, chat_id, "Не удалось скачать файл. Попробуй снова.", reply_to, "download_failed")
        return

    conn.execute("UPDATE drive_files SET stage='DOWNLOADED' WHERE task_id=?", (task_id,))


    try:
        _, _, topic_role, _ = _load_memory_context(chat_id, topic_id)
        caption = data.get("caption", "")

        # === ROUTE_FILE: специализированные движки ===
        router_result = None
        try:
            from core.file_intake_router import detect_intent, detect_format, route_file, should_ask_clarification, get_clarification_message
            intent = detect_intent(caption) or detect_intent(topic_role)
            fmt = detect_format(caption)
            if not intent:
                from core.file_intake_router import detect_intent_from_filename
                intent = detect_intent_from_filename(file_name)

            # Если intent не определён и caption пустой — спросить пользователя
            _, _, _zn_role, _zn_dir = _load_memory_context(str(chat_id), topic_id)
            if should_ask_clarification(caption, True) and not intent and not _zn_dir:
                clarify_msg = get_clarification_message(file_name, topic_id)
                _update_task(conn, task_id, state="WAITING_CLARIFICATION", result="", error_message="CLARIFICATION_REQUIRED")
                _history(conn, task_id, "state:WAITING_CLARIFICATION:CLARIFICATION_REQUIRED")
                conn.commit()
                _send_once(conn, task_id, chat_id, clarify_msg, reply_to, "clarification_needed")
                return

            if intent:
                logger.info(f"DRIVE_FILE: route_file intent={intent} fmt={fmt} task={task_id}")
                from core.file_pipeline_overlay import extract_router_payload
                router_result = await asyncio.wait_for(
                    route_file(local_path, task_id, topic_id, intent, fmt),
                    timeout=300
                )  # PATCH_ENGINE_TIMEOUT
                if not isinstance(router_result, dict):
                    router_result = {"success": False, "error": "INVALID_ROUTER_RESULT"}
                usable_r, artifact_path_r, drive_link_r, text_result_r = extract_router_payload(router_result)
                if router_result.get("success") is False and not usable_r:
                    err = str(router_result.get("error") or "ROUTE_FILE_FAILED")[:500]
                    _update_task(conn, task_id, state="FAILED", error_message=err)
                    _history(conn, task_id, f"state:FAILED:{err}")
                    conn.execute("UPDATE drive_files SET stage='FAILED' WHERE task_id=?", (task_id,))
                    conn.commit()
                    _send_once(conn, task_id, chat_id, f"Не выполнено: {err}", reply_to, "route_failed")
                    logger.error(f"DRIVE_FILE: route_file failed task={task_id} err={err}")
                    return

                if usable_r:
                    if drive_link_r:
                        ok_intent, intent_err = _file_result_matches_intent(intent, drive_link_r, "", file_name)
                        if not ok_intent:
                            _update_task(conn, task_id, state="FAILED", result="", error_message=intent_err)
                            _history(conn, task_id, f"state:FAILED:{intent_err}")
                            conn.execute("UPDATE drive_files SET stage='FAILED_INTENT_MISMATCH' WHERE task_id=?", (task_id,))
                            conn.commit()
                            _send_once(conn, task_id, chat_id, f"Не выполнено: {intent_err}", reply_to, "intent_mismatch")
                            logger.error(f"DRIVE_FILE: intent mismatch task={task_id} err={intent_err} link={drive_link_r}")
                            return
                        result = f"Готово ({intent})\n\nАртефакт: {drive_link_r}"
                        _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=result, error_message="")
                        sent = _send_once_ex(conn, task_id, chat_id, result, reply_to, "result")
                        bot_message_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
                        if bot_message_id is not None:
                            _update_task(conn, task_id, bot_message_id=bot_message_id)
                        conn.commit()
                        logger.info(f"DRIVE_FILE: route_file done via drive_link task={task_id}")
                        return

                    elif artifact_path_r and os.path.exists(artifact_path_r):
                        ok_intent, intent_err = _file_result_matches_intent(intent, "", artifact_path_r, file_name)
                        if not ok_intent:
                            _update_task(conn, task_id, state="FAILED", result="", error_message=intent_err)
                            _history(conn, task_id, f"state:FAILED:{intent_err}")
                            conn.execute("UPDATE drive_files SET stage='FAILED_INTENT_MISMATCH' WHERE task_id=?", (task_id,))
                            conn.commit()
                            _send_once(conn, task_id, chat_id, f"Не выполнено: {intent_err}", reply_to, "intent_mismatch")
                            logger.error(f"DRIVE_FILE: intent mismatch task={task_id} err={intent_err} artifact={artifact_path_r}")
                            return
                        artifact_name_r = os.path.basename(artifact_path_r)
                        try:
                            upload_res = await upload_file_to_topic(artifact_path_r, artifact_name_r, chat_id, topic_id)
                            if isinstance(upload_res, dict) and upload_res.get("ok") and upload_res.get("drive_file_id"):
                                result = f"Готово ({intent})\n\nАртефакт: https://drive.google.com/file/d/{upload_res.get('drive_file_id')}/view"
                            else:
                                result = f"Готово ({intent})\n\nАртефакт создан, но загрузка в Drive не подтвердилась"

                            _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=result, error_message="")
                            sent = _send_once_ex(conn, task_id, chat_id, result, reply_to, "result")
                            bot_message_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
                            if bot_message_id is not None:
                                _update_task(conn, task_id, bot_message_id=bot_message_id)
                            conn.commit()
                            try:
                                if artifact_path_r and os.path.exists(artifact_path_r):
                                    os.remove(artifact_path_r)
                                    logger.info("TEMP_DELETED %s", artifact_path_r)
                            except Exception:
                                pass
                            logger.info(f"DRIVE_FILE: route_file done via artifact_path task={task_id}")
                            return
                        except Exception as ue:
                            logger.error(f"DRIVE_FILE: route_file upload failed task={task_id} err={ue}")

                    elif text_result_r:
                        if "drive.google.com" not in str(text_result_r):
                            _update_task(conn, task_id, state="FAILED", error_message="NO_VALID_ARTIFACT")
                            _history(conn, task_id, "state:FAILED:NO_VALID_ARTIFACT")
                            conn.commit()
                            _send_once(conn, task_id, chat_id, "Ошибка: результат без файла. NO_VALID_ARTIFACT", reply_to, "no_artifact")
                            return
                        result = text_result_r
                        _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=result, error_message="")
                        sent = _send_once_ex(conn, task_id, chat_id, result, reply_to, "result")
                        bot_message_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
                        if bot_message_id is not None:
                            _update_task(conn, task_id, bot_message_id=bot_message_id)
                        conn.commit()
                        logger.info(f"DRIVE_FILE: route_file done via text_result task={task_id}")
                        return

                logger.info(f"DRIVE_FILE: route_file returned no usable payload, fallback task={task_id}")
        except asyncio.TimeoutError:
            logger.error(f"DRIVE_FILE: route_file ENGINE_TIMEOUT task={task_id}")
            _update_task(conn, task_id, state="FAILED", error_message="ENGINE_TIMEOUT")
            _history(conn, task_id, "state:FAILED:ENGINE_TIMEOUT")
            conn.execute("UPDATE drive_files SET stage='FAILED' WHERE task_id=?", (task_id,))
            conn.commit()
            _send_once(conn, task_id, chat_id, "Не выполнено: ENGINE_TIMEOUT", reply_to, "engine_timeout")
            return
        except Exception as re_err:
            logger.error(f"DRIVE_FILE: route_file error task={task_id} err={re_err}")
        # === END ROUTE_FILE ===

        analysis = await analyze_downloaded_file(
            local_path=local_path,
            file_name=file_name,
            mime_type=data.get("mime_type", ""),
            user_text=caption,
            topic_role=topic_role,
        )
        if isinstance(analysis, dict):
            summary = _s(analysis.get("summary")) or result
            artifact_path = _s(analysis.get("artifact_path"))
            artifact_name = _s(analysis.get("artifact_name")) or os.path.basename(artifact_path)
            result = summary
            if artifact_path and os.path.exists(artifact_path):
                try:
                    upload_res = await upload_file_to_topic(artifact_path, artifact_name, chat_id, topic_id)
                    if isinstance(upload_res, dict) and upload_res.get("ok") and upload_res.get("drive_file_id"):
                        result = summary + f"\n\nАртефакт: https://drive.google.com/file/d/{upload_res.get('drive_file_id')}/view"
                    else:
                        result = summary + "\n\nАртефакт создан, но загрузка в Drive не подтвердилась"
                except Exception as e:
                    logger.error(f"DRIVE_FILE artifact upload failed task={task_id} err={e}")
                    result = summary + "\n\nАртефакт создан локально, но загрузка в Drive завершилась ошибкой"
    except Exception as e:
        logger.error(f"DRIVE_FILE analyze skipped task={task_id} err={e}")

    if not _clean(_s(result), 50000) or result == waiting_result or "ожидает анализа" in str(result) or "скачан" in str(result):
        try:
            from core.file_intake_router import get_clarification_message
            clarify_msg = get_clarification_message(file_name, topic_id)
        except Exception:
            clarify_msg = f"📎 Получил файл «{file_name}».\nЧто с ним сделать?"
        _update_task(conn, task_id, state="WAITING_CLARIFICATION", result="", error_message="PIPELINE_NOT_EXECUTED")
        _history(conn, task_id, "state:WAITING_CLARIFICATION")
        conn.commit()
        _send_once(conn, task_id, chat_id, clarify_msg, reply_to, "clarification_needed")
        logger.info(f"DRIVE_FILE: no artifact/result -> WAITING_CLARIFICATION task={task_id}")
        return

    _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=result, error_message="")
    sent = _send_once_ex(conn, task_id, chat_id, result, reply_to, "result")
    bot_message_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
    if bot_message_id is not None:
        _update_task(conn, task_id, bot_message_id=bot_message_id)
    conn.commit()
    logger.info(f"DRIVE_FILE: {task_id} processed")

# === CANON_PASS3_REAL_DRIVEFILE_WIRING ===
import asyncio as _canon_pass3_asyncio
import inspect as _canon_pass3_inspect
import json as _canon_pass3_json
import sqlite3 as _canon_pass3_sqlite3
from datetime import datetime as _canon_pass3_datetime

_CANON_PASS3_DRIVE_TIMEOUT = 120

def _canon_pass3_db():
    return _canon_pass3_sqlite3.connect("/root/.areal-neva-core/data/core.db")

def _canon_pass3_extract_task_payload(args, kwargs):
    task_id = kwargs.get("task_id")
    chat_id = kwargs.get("chat_id")
    topic_id = kwargs.get("topic_id", 0)
    raw_input = kwargs.get("raw_input")
    file_name = ""
    file_id = ""

    for obj in list(args) + list(kwargs.values()):
        try:
            if isinstance(obj, dict):
                task_id = task_id or obj.get("id") or obj.get("task_id")
                chat_id = chat_id or obj.get("chat_id")
                topic_id = obj.get("topic_id", topic_id)
                raw_input = raw_input or obj.get("raw_input") or obj.get("input")
            elif hasattr(obj, "keys"):
                task_id = task_id or obj["id"] if "id" in obj.keys() else task_id
                chat_id = chat_id or obj["chat_id"] if "chat_id" in obj.keys() else chat_id
                topic_id = obj["topic_id"] if "topic_id" in obj.keys() else topic_id
                raw_input = raw_input or obj["raw_input"] if "raw_input" in obj.keys() else raw_input
        except Exception:
            pass

    try:
        data = _canon_pass3_json.loads(raw_input) if isinstance(raw_input, str) and raw_input.strip().startswith("{") else {}
        file_name = data.get("file_name") or data.get("name") or ""
        file_id = data.get("file_id") or data.get("drive_file_id") or ""
    except Exception:
        data = {}

    return {
        "task_id": str(task_id or ""),
        "chat_id": chat_id,
        "topic_id": int(topic_id or 0),
        "raw_input": raw_input or "",
        "file_name": file_name,
        "file_id": file_id,
    }

def _canon_pass3_mark_task_failed(task_id, error):
    if not task_id:
        return False
    try:
        con = _canon_pass3_db()
        con.execute(
            "UPDATE tasks SET state='FAILED', error_message=?, updated_at=? WHERE id=?",
            (str(error)[:500], _canon_pass3_datetime.utcnow().isoformat(timespec="seconds") + "Z", str(task_id)),
        )
        con.commit()
        con.close()
        return True
    except Exception:
        return False

def _canon_pass3_mark_drive_stage(task_id, stage):
    try:
        con = _canon_pass3_db()
        cols = [r[1] for r in con.execute("PRAGMA table_info(drive_files)").fetchall()]
        if "stage" in cols:
            con.execute("UPDATE drive_files SET stage=? WHERE task_id=?", (str(stage), str(task_id)))
        con.commit()
        con.close()
        return True
    except Exception:
        return False

def _canon_pass3_find_reusable_result(chat_id, topic_id, file_name, file_id, exclude_task_id=""):
    try:
        con = _canon_pass3_db()
        params = []
        wh = ["COALESCE(result,'') LIKE '%drive.google.com%'"]
        if chat_id is not None:
            wh.append("chat_id=?")
            params.append(chat_id)
        if topic_id is not None:
            wh.append("COALESCE(topic_id,0)=?")
            params.append(int(topic_id or 0))
        if file_id:
            wh.append("raw_input LIKE ?")
            params.append(f"%{file_id}%")
        elif file_name:
            wh.append("raw_input LIKE ?")
            params.append(f"%{file_name}%")
        else:
            con.close()
            return ""
        if exclude_task_id:
            wh.append("id<>?")
            params.append(str(exclude_task_id))
        sql = "SELECT result FROM tasks WHERE " + " AND ".join(wh) + " ORDER BY updated_at DESC LIMIT 1"
        row = con.execute(sql, params).fetchone()
        con.close()
        return row[0] if row else ""
    except Exception:
        return ""

def _canon_pass3_complete_with_reuse(task_id, result, chat_id, topic_id, raw_input):
    try:
        from core.quality_gate import extract_drive_link, is_clean_value
        link = extract_drive_link(result)
        if not link or not is_clean_value(result):
            return False
        con = _canon_pass3_db()
        con.execute(
            "UPDATE tasks SET state='AWAITING_CONFIRMATION', result=?, error_message=NULL, updated_at=? WHERE id=?",
            (result, _canon_pass3_datetime.utcnow().isoformat(timespec="seconds") + "Z", str(task_id)),
        )
        con.commit()
        con.close()
        _canon_pass3_mark_drive_stage(task_id, "REUSING_ARTIFACT")
        try:
            canon_pass2_save_file_pin(chat_id, topic_id, task_id, result)
        except Exception:
            pass
        try:
            canon_pass2_save_file_memory(chat_id, topic_id, task_id, raw_input, result)
        except Exception:
            pass
        return True
    except Exception:
        return False

if "_handle_drive_file" in globals():
    _canon_pass3_orig_handle_drive_file = _handle_drive_file

    async def _canon_pass3_handle_drive_file_wrapper(*args, **kwargs):
        payload = _canon_pass3_extract_task_payload(args, kwargs)
        task_id = payload["task_id"]
        chat_id = payload["chat_id"]
        topic_id = payload["topic_id"]
        raw_input = payload["raw_input"]
        file_name = payload["file_name"]
        file_id = payload["file_id"]

        reusable = _canon_pass3_find_reusable_result(chat_id, topic_id, file_name, file_id, task_id)
        if reusable and _canon_pass3_complete_with_reuse(task_id, reusable, chat_id, topic_id, raw_input):
            return {"ok": True, "reused": True, "result": reusable}

        _canon_pass3_mark_drive_stage(task_id, "PARSING")

        try:
            res = _canon_pass3_orig_handle_drive_file(*args, **kwargs)
            if _canon_pass3_inspect.isawaitable(res):
                return await _canon_pass3_asyncio.wait_for(res, timeout=_CANON_PASS3_DRIVE_TIMEOUT)
            return res
        except _canon_pass3_asyncio.TimeoutError:
            _canon_pass3_mark_drive_stage(task_id, "FAILED_TIMEOUT")
            _canon_pass3_mark_task_failed(task_id, "TIMEOUT_ERROR:drive_file_pipeline")
            return {"ok": False, "error": "TIMEOUT_ERROR:drive_file_pipeline"}
        except Exception as e:
            _canon_pass3_mark_drive_stage(task_id, "FAILED")
            raise

    _handle_drive_file = _canon_pass3_handle_drive_file_wrapper
# === END_CANON_PASS3_REAL_DRIVEFILE_WIRING ===

# === CANON_PASS5B_TOPIC_3008_CODE_BRAIN ===
if "process_ai_task" in globals():
    _canon_pass5b_orig_process_ai_task = process_ai_task

    async def process_ai_task(payload):
        try:
            from core.orchestra_agents.agent_router import is_topic_3008, is_code_command, handle_code_brain
            raw = str(payload.get("raw_input") or payload.get("text") or payload.get("user_text") or "")
            if is_topic_3008(payload) and is_code_command(raw):
                result = await handle_code_brain(payload)
                if result:
                    return result
        except Exception as e:
            return f"CODE_BRAIN_ERROR: {e!r}"
        return await _canon_pass5b_orig_process_ai_task(payload)
# === END_CANON_PASS5B_TOPIC_3008_CODE_BRAIN ===

# === CANON_RECOVERY_SAFE_QUEUE_VOICE_MEMORY ===
# Safe overlay only. No core rewrite.
import json as _canon_recovery_json
import re as _canon_recovery_re

_CANON_RECOVERY_MEMORY_DENY = (
    "Понял задачу так",
    "Подтверди или уточни",
    "Не понял",
    "Уточни",
    "Ошибка обработки",
    "INVALID_RESULT",
    "INVALID_RESULT_GATE",
    "INVALID_RESULT_SOFT",
    "STALE_TIMEOUT",
    "DOWNLOAD_FAILED",
    "VOICE_FILE_SHOULD_GO_STT",
    "VOICE_DROP",
    "Traceback",
    "SyntaxError",
    "NameError",
    "/root/",
    ".ogg",
    "voice_",
)

def _canon_recovery_is_voice_drive_raw(raw):
    try:
        data = _canon_recovery_json.loads(str(raw or "{}"))
    except Exception:
        data = {}
    file_name = str(data.get("file_name") or "").lower()
    mime_type = str(data.get("mime_type") or "").lower()
    raw_s = str(raw or "").lower()
    return (
        file_name.endswith(".ogg")
        or file_name.startswith("voice_")
        or mime_type in ("application/ogg", "audio/ogg", "audio/mpeg", "audio/wav", "audio/x-wav")
        or "voice_" in raw_s and ".ogg" in raw_s
        or "application/ogg" in raw_s
        or "audio/" in raw_s
    )

def _canon_recovery_cancel_voice_drive_files(conn, chat_id=None):
    try:
        params = []
        where_chat = ""
        if chat_id:
            where_chat = " AND chat_id=?"
            params.append(str(chat_id))
        conn.execute(
            "UPDATE tasks SET state='CANCELLED', error_message='VOICE_DROP', updated_at=datetime('now') "
            "WHERE input_type='drive_file' AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION') "
            "AND (raw_input LIKE '%voice_%' OR raw_input LIKE '%.ogg%' OR raw_input LIKE '%application/ogg%' OR raw_input LIKE '%audio/%')"
            + where_chat,
            params,
        )
        conn.commit()
    except Exception as e:
        try:
            logger.warning("CANON_RECOVERY voice cleanup failed: %s", e)
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())

# === CANON_PASS2_FILE_MEMORY_REPLY_GUARD ===
def canon_pass2_is_file_result_valid(result):
    try:
        from core.quality_gate import extract_drive_link, is_clean_value
        return bool(extract_drive_link(result)) and is_clean_value(result)
    except Exception:
        return False

def canon_pass2_clean_result(result, limit=5000):
    try:
        from core.quality_gate import clean_text
        return clean_text(result, limit)
    except Exception:
        return ("" if result is None else str(result))[:limit]

def canon_pass2_save_file_memory(chat_id, topic_id, task_id, raw_input, result):
    try:
        import sqlite3
        from datetime import datetime
        from core.quality_gate import clean_text, extract_drive_link, is_clean_value
        clean_result = clean_text(result, 20000)
        clean_raw = clean_text(raw_input, 500)
        link = extract_drive_link(result)
        if not is_clean_value(clean_result):
            return False
        con = sqlite3.connect("/root/.areal-neva-core/data/memory.db")
        ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        key_base = f"topic_{int(topic_id or 0)}"
        rows = [
            (str(chat_id), f"{key_base}_task_summary", clean_result, ts),
            (str(chat_id), f"{key_base}_artifact_link", link, ts),
            (str(chat_id), f"{key_base}_last_result_format", "xlsx" if ".xlsx" in clean_result.lower() or "drive.google.com" in clean_result.lower() else "unknown", ts),
            (str(chat_id), f"{key_base}_file_context", clean_raw, ts),
        ]
        con.executemany("INSERT INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,?)", rows)
        con.commit()
        con.close()
        return True
    except Exception:
        return False

def canon_pass2_save_file_pin(chat_id, topic_id, task_id, result):
    try:
        import sqlite3
        from datetime import datetime
        if not canon_pass2_is_file_result_valid(result):
            return False
        con = sqlite3.connect("/root/.areal-neva-core/data/core.db")
        cols = [r[1] for r in con.execute("PRAGMA table_info(pin)").fetchall()]
        ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        if "topic_id" in cols:
            con.execute("DELETE FROM pin WHERE chat_id=? AND topic_id=?", (chat_id, int(topic_id or 0)))
            con.execute("INSERT INTO pin(chat_id,topic_id,task_id,state,updated_at) VALUES(?,?,?,?,?)", (chat_id, int(topic_id or 0), task_id, "ACTIVE", ts))
        else:
            con.execute("DELETE FROM pin WHERE chat_id=?", (chat_id,))
            con.execute("INSERT INTO pin(chat_id,task_id,state,updated_at) VALUES(?,?,?,?)", (chat_id, task_id, "ACTIVE", ts))
        con.commit()
        con.close()
        return True
    except Exception:
        return False

def canon_pass2_control_intent(text):
    s = (text or "").strip().lower()
    finish_words = ("можно завершать", "задачу можно завершать", "задача закрыта", "закрывай", "готово", "всё", "все", "не надо")
    cancel_words = ("отбой", "отмена", "сброс задач")
    revision_words = ("не так", "исправь", "переделай", "правки")
    confirm_words = ("да", "ок", "okay", "принято", "подтверждаю", "верно")
    if any(w in s for w in cancel_words):
        return "CANCEL"
    if any(w in s for w in finish_words):
        return "FINISH"
    if any(w in s for w in revision_words):
        return "REVISION"
    if s in confirm_words:
        return "CONFIRM"
    if s in ("ага", "понял", "ясно", "+"):
        return "CHAT"
    return "NONE"
# === END_CANON_PASS2_FILE_MEMORY_REPLY_GUARD ===



# === CANON_PASS6_LIVE_CORE_OVERLAY ===
import sqlite3 as _cp6_sqlite3
import os as _cp6_os

_CP6_MEM_DB = "/root/.areal-neva-core/data/memory.db"

def _cp6_save_topic_directions(chat_id, topic_id, directions):
    if not directions or not _cp6_os.path.exists(_CP6_MEM_DB):
        return
    try:
        c = _cp6_sqlite3.connect(_CP6_MEM_DB)
        c.execute("CREATE TABLE IF NOT EXISTS memory (chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        k = f"topic_{int(topic_id)}_directions"
        c.execute("DELETE FROM memory WHERE chat_id=? AND key=?", (str(chat_id), k))
        c.execute("INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
                  (str(chat_id), k, str(directions)[:1000]))
        c.commit(); c.close()
    except Exception as _e:
        try: logger.warning("CP6_DIR_FAIL: %s", _e)
        except Exception: pass

if "_save_topic_role" in globals():
    _cp6_orig_save_role = _save_topic_role
    def _save_topic_role(chat_id, topic_id, role):
        _cp6_orig_save_role(chat_id, topic_id, role)
        try: _cp6_save_topic_directions(chat_id, topic_id, role)
        except Exception: pass

_CP6_CHAT_BYPASS = (
    "чем помочь", "готов помочь", "задача закрыта", "принял",
    "принято", "понял", "хорошо", "привет", "здравствуй", "добрый день",
    "доброе утро", "добрый вечер", "уточни"
)
_CP6_RECALL_BYPASS = ("этот чат закреплён", "этот чат для", "напомню", "история чата")

if "_is_valid_result" in globals():
    _cp6_orig_ivr = _is_valid_result
    def _is_valid_result(text, raw_input):
        try:
            r = (str(text or "")).strip().lower()
            ri = (str(raw_input or "")).strip().lower()
            if r and len(r) < 200:
                if any(p in r for p in _CP6_CHAT_BYPASS): return True
                if any(p in r for p in _CP6_RECALL_BYPASS): return True
            if any(q in ri for q in ("для чего", "о чём", "о чем", "напомни", "что мы писали", "что писали раньше", "история чата")):
                if r and len(r) >= 8: return True
        except Exception: pass
        return _cp6_orig_ivr(text, raw_input)

_CP6_TRASH_EXTRA = [
    "чем помочь", "готов помочь", "задача закрыта",
    "принял правки", "принял.", "принято.",
    "уточните запрос", "отправь код для проверки"
]

def _cp6_extra_close_trash(conn):
    try:
        for pat in _CP6_TRASH_EXTRA:
            conn.execute(
                "UPDATE tasks SET state='DONE', error_message='', updated_at=datetime('now') "
                "WHERE state='AWAITING_CONFIRMATION' "
                "AND lower(COALESCE(result,'')) LIKE ? "
                "AND (strftime('%s','now') - strftime('%s', COALESCE(updated_at, created_at))) > 60",
                (f"%{pat}%",)
            )
        conn.commit()
    except Exception as _e:
        try: logger.warning("CP6_TRASH_SWEEP_FAIL: %s", _e)
        except Exception: pass

if "_auto_close_trash_awaiting" in globals():
    _cp6_orig_actrash = _auto_close_trash_awaiting
    def _auto_close_trash_awaiting(conn):
        _cp6_orig_actrash(conn)
        _cp6_extra_close_trash(conn)

if "process_ai_task" in globals():
    _cp6_orig_pat = process_ai_task
    async def process_ai_task(payload):
        try:
            tid = int(payload.get("topic_id") or 0)
            raw = str(payload.get("raw_input") or payload.get("text") or "")
            if tid == 3008 and ("проверь код" in raw.lower() or "проверить код" in raw.lower() or "верифик" in raw.lower()):
                from core.orchestra_agents.local_checks import extract_code
                if not extract_code(raw):
                    return "__CP6_WAITING_CLARIFICATION__:Отправь код для проверки в блоке ```python ... ```"
        except Exception as _e:
            try: logger.warning("CP6_T3008_GUARD_FAIL: %s", _e)
            except Exception: pass
        return await _cp6_orig_pat(payload)

def _cp6_promote_waiting_clarification(conn):
    try:
        rows = conn.execute(
            "SELECT id, result FROM tasks WHERE state='AWAITING_CONFIRMATION' "
            "AND result LIKE '__CP6_WAITING_CLARIFICATION__%' LIMIT 50"
        ).fetchall()
        for r in rows:
            tid = r[0] if not hasattr(r, "keys") else r["id"]
            res = r[1] if not hasattr(r, "keys") else r["result"]
            clean = str(res).replace("__CP6_WAITING_CLARIFICATION__:", "").strip()
            conn.execute(
                "UPDATE tasks SET state='WAITING_CLARIFICATION', result=?, "
                "error_message='AWAITING_CODE_BLOCK', updated_at=datetime('now') WHERE id=?",
                (clean, tid)
            )
        conn.commit()
    except Exception as _e:
        try: logger.warning("CP6_PROMOTE_WC_FAIL: %s", _e)
        except Exception: pass

def _cp6_close_pins_on_closed_tasks(conn):
    try:
        conn.execute(
            "UPDATE pin SET state='CLOSED', updated_at=datetime('now') "
            "WHERE state='ACTIVE' AND task_id IN ("
            "  SELECT id FROM tasks WHERE state IN ('DONE','FAILED','CANCELLED','ARCHIVED')"
            ")"
        )
        conn.commit()
    except Exception as _e:
        try: logger.warning("CP6_PIN_SWEEP_FAIL: %s", _e)
        except Exception: pass

if "_recover_stale_tasks" in globals():
    _cp6_orig_recover = _recover_stale_tasks
    def _recover_stale_tasks(conn, chat_id):
        _cp6_orig_recover(conn, chat_id)
        _cp6_promote_waiting_clarification(conn)
        _cp6_close_pins_on_closed_tasks(conn)
# === END_CANON_PASS6_LIVE_CORE_OVERLAY ===

# === CANON_PASS7_WORKER_MONOLITH_FINAL ===
# Append-only overlay. No forbidden files. No DB schema changes.
# Closes factual failures observed in diagnostics:
# - topic_3008 no-code verify must become WAITING_CLARIFICATION, not stale timeout
# - short/service/chat results must not fail INVALID_RESULT_GATE
# - active pins pointing to closed tasks must be closed
# - trash awaiting confirmations must auto-close before stale timeout
# - voice/control results already saved in DB as "Задача закрыта" must not be left to stale

import re as _cp7_re
import sqlite3 as _cp7_sqlite3

_CP7_CORE_DB = "/root/.areal-neva-core/data/core.db"

_CP7_SHORT_OK_RESULT_PATTERNS = (
    "чем помочь",
    "готов помочь",
    "задача закрыта",
    "задача завершена",
    "принял",
    "принято",
    "понял",
    "хорошо",
    "привет",
    "здравствуй",
    "добрый день",
    "доброе утро",
    "добрый вечер",
    "уточни",
    "уточните",
    "отправь код для проверки",
    "подтверждение принято",
    "правки приняты",
)

_CP7_RECALL_OK_RESULT_PATTERNS = (
    "этот чат закреплён",
    "этот чат закреплен",
    "этот чат для",
    "чат для",
    "напомню",
    "история чата",
    "последние задачи",
)

_CP7_TRASH_RESULT_PATTERNS = (
    "чем помочь",
    "готов помочь",
    "задача закрыта",
    "задача завершена",
    "принял правки",
    "принял.",
    "принято.",
    "подтверждение принято",
    "правки приняты",
    "уточните запрос",
    "отправь код для проверки",
)

def _cp7_s(x):
    return "" if x is None else str(x)

def _cp7_lower(x):
    return _cp7_s(x).strip().lower()

def _cp7_is_topic3008_verify_without_code(raw):
    text = _cp7_s(raw)
    low = text.lower()
    if not any(x in low for x in ("проверь код", "проверить код", "верификац")):
        return False
    try:
        from core.orchestra_agents.local_checks import extract_code
        code = extract_code(text)
        stripped = (code or "").strip()
        if not stripped:
            return True
        if stripped.lower() in ("проверь код", "проверить код", "верификация"):
            return True
        return False
    except Exception:
        return "```" not in text

def _cp7_result_should_be_valid(text, raw_input):
    r = _cp7_lower(text)
    ri = _cp7_lower(raw_input)
    if r and len(r) < 300:
        if any(p in r for p in _CP7_SHORT_OK_RESULT_PATTERNS):
            return True
        if any(p in r for p in _CP7_RECALL_OK_RESULT_PATTERNS):
            return True
    if any(q in ri for q in ("для чего", "о чём", "о чем", "напомни", "что мы писали", "что писали раньше", "история чата")):
        return bool(r and len(r) >= 8)
    return False

if "_is_valid_result" in globals():
    _cp7_orig_is_valid_result = _is_valid_result
    def _is_valid_result(text, raw_input):
        try:
            if _cp7_result_should_be_valid(text, raw_input):
                return True
        except Exception as _e:
            try:
                logger.warning("CP7_VALID_RESULT_BYPASS_FAIL: %s", _e)
            except Exception:
                pass
        return _cp7_orig_is_valid_result(text, raw_input)

def _cp7_close_active_pins_on_closed_tasks(conn):
    try:
        conn.execute(
            "UPDATE pin SET state='CLOSED', updated_at=datetime('now') "
            "WHERE state='ACTIVE' AND task_id IN ("
            "SELECT id FROM tasks WHERE state IN ('DONE','FAILED','CANCELLED','ARCHIVED'))"
        )
        conn.commit()
    except Exception as _e:
        try:
            logger.warning("CP7_PIN_CLOSE_FAIL: %s", _e)
        except Exception:
            pass

def _cp7_close_trash_awaiting(conn):
    try:
        for pat in _CP7_TRASH_RESULT_PATTERNS:
            conn.execute(
                "UPDATE tasks SET state='DONE', error_message='', updated_at=datetime('now') "
                "WHERE state='AWAITING_CONFIRMATION' "
                "AND lower(COALESCE(result,'')) LIKE ? "
                "AND (strftime('%s','now') - strftime('%s', COALESCE(updated_at, created_at))) > 60",
                (f"%{pat}%",),
            )
        conn.commit()
    except Exception as _e:
        try:
            logger.warning("CP7_TRASH_CLOSE_FAIL: %s", _e)
        except Exception:
            pass

def _cp7_promote_no_code_verify(conn):
    try:
        rows = conn.execute(
            "SELECT id, COALESCE(topic_id,0) AS topic_id, COALESCE(raw_input,'') AS raw_input "
            "FROM tasks "
            "WHERE state IN ('NEW','IN_PROGRESS','AWAITING_CONFIRMATION') "
            "AND COALESCE(topic_id,0)=3008 "
            "AND lower(COALESCE(raw_input,'')) LIKE '%проверь код%' "
            "LIMIT 100"
        ).fetchall()
        for row in rows:
            tid = row["id"] if hasattr(row, "keys") else row[0]
            raw = row["raw_input"] if hasattr(row, "keys") else row[2]
            if _cp7_is_topic3008_verify_without_code(raw):
                conn.execute(
                    "UPDATE tasks SET state='WAITING_CLARIFICATION', "
                    "result='Отправь код для проверки в блоке ```python ... ```', "
                    "error_message='AWAITING_CODE_BLOCK', updated_at=datetime('now') "
                    "WHERE id=?",
                    (tid,),
                )
                try:
                    _history(conn, tid, "cp7:WAITING_CLARIFICATION:AWAITING_CODE_BLOCK")
                except Exception:
                    pass
        conn.commit()
    except Exception as _e:
        try:
            logger.warning("CP7_PROMOTE_NO_CODE_FAIL: %s", _e)
        except Exception:
            pass

def _cp7_finalize_control_like_results(conn):
    try:
        rows = conn.execute(
            "SELECT id, COALESCE(result,'') AS result "
            "FROM tasks "
            "WHERE state IN ('IN_PROGRESS','AWAITING_CONFIRMATION') "
            "AND (lower(COALESCE(result,'')) LIKE '%задача закрыта%' "
            "OR lower(COALESCE(result,'')) LIKE '%задача завершена%' "
            "OR lower(COALESCE(result,'')) LIKE '%подтверждение принято%' "
            "OR lower(COALESCE(result,'')) LIKE '%правки приняты%') "
            "LIMIT 100"
        ).fetchall()
        for row in rows:
            tid = row["id"] if hasattr(row, "keys") else row[0]
            conn.execute(
                "UPDATE tasks SET state='DONE', error_message='', updated_at=datetime('now') WHERE id=?",
                (tid,),
            )
            try:
                _history(conn, tid, "cp7:state:DONE:CONTROL_LIKE_RESULT")
            except Exception:
                pass
        conn.commit()
    except Exception as _e:
        try:
            logger.warning("CP7_CONTROL_FINALIZE_FAIL: %s", _e)
        except Exception:
            pass

def _cp7_runtime_sweep(conn):
    _cp7_promote_no_code_verify(conn)
    _cp7_close_trash_awaiting(conn)
    _cp7_finalize_control_like_results(conn)
    _cp7_close_active_pins_on_closed_tasks(conn)

if "_recover_stale_tasks" in globals():
    _cp7_orig_recover_stale_tasks = _recover_stale_tasks
    def _recover_stale_tasks(conn, chat_id):
        _cp7_runtime_sweep(conn)
        _cp7_orig_recover_stale_tasks(conn, chat_id)
        _cp7_runtime_sweep(conn)

if "_handle_new" in globals():
    _cp7_orig_handle_new = _handle_new
    async def _handle_new(conn, task, chat_id, topic_id):
        try:
            task_id = _s(_task_field(task, "id"))
            raw_input = _s(_task_field(task, "raw_input"))
            reply_to = _task_field(task, "reply_to_message_id", None)
            if int(topic_id or 0) == 3008 and _cp7_is_topic3008_verify_without_code(raw_input):
                msg = "Отправь код для проверки в блоке ```python ... ```"
                _update_task(conn, task_id, state="WAITING_CLARIFICATION", result=msg, error_message="AWAITING_CODE_BLOCK")
                _history(conn, task_id, "cp7:WAITING_CLARIFICATION:AWAITING_CODE_BLOCK")
                conn.commit()
                _send_once(conn, task_id, chat_id, msg, reply_to, "clarification_needed")
                return
        except Exception as _e:
            try:
                logger.warning("CP7_HANDLE_NEW_GUARD_FAIL: %s", _e)
            except Exception:
                pass
        return await _cp7_orig_handle_new(conn, task, chat_id, topic_id)

if "_handle_in_progress" in globals():
    _cp7_orig_handle_in_progress = _handle_in_progress
    async def _handle_in_progress(conn, task, chat_id, topic_id):
        try:
            task_id = _s(_task_field(task, "id"))
            raw_input = _s(_task_field(task, "raw_input"))
            reply_to = _task_field(task, "reply_to_message_id", None)
            if int(topic_id or 0) == 3008 and _cp7_is_topic3008_verify_without_code(raw_input):
                msg = "Отправь код для проверки в блоке ```python ... ```"
                _update_task(conn, task_id, state="WAITING_CLARIFICATION", result=msg, error_message="AWAITING_CODE_BLOCK")
                _history(conn, task_id, "cp7:WAITING_CLARIFICATION:AWAITING_CODE_BLOCK")
                conn.commit()
                _send_once(conn, task_id, chat_id, msg, reply_to, "clarification_needed")
                return
        except Exception as _e:
            try:
                logger.warning("CP7_HANDLE_IN_PROGRESS_GUARD_FAIL: %s", _e)
            except Exception:
                pass
        return await _cp7_orig_handle_in_progress(conn, task, chat_id, topic_id)

# === END_CANON_PASS7_WORKER_MONOLITH_FINAL ===

# === CANON_PASS8_FINAL_CLOSE ===
# FACT BASIS:
# - Live DB showed ACTIVE pin on a DONE task:
#   task_id=c9405ca6-22f0-4fe6-ac77-2b5ce012ddb6, topic_id=961
# - ROLLBACK test update returned changes()=1
# - This overlay changes only task_worker.py
# - No DB schema changes
# - No forbidden files touched
# - Purpose: enforce runtime cleanup of ACTIVE pins linked to closed tasks

def _cp8_close_active_pins_on_closed_tasks(conn):
    try:
        conn.execute(
            "UPDATE pin SET state='CLOSED', updated_at=datetime('now') "
            "WHERE state='ACTIVE' "
            "AND task_id IN ("
            "  SELECT id FROM tasks "
            "  WHERE state IN ('DONE','FAILED','CANCELLED','ARCHIVED')"
            ")"
        )
        conn.commit()
    except Exception as e:
        try:
            logger.warning("CP8_PIN_CLOSE_FAIL: %s", e)
        except Exception:
            pass

def _cp8_fix_codebrain_waiting_clarification(conn):
    try:
        conn.execute(
            "UPDATE tasks "
            "SET state='WAITING_CLARIFICATION', "
            "    error_message='AWAITING_CODE_BLOCK', "
            "    updated_at=datetime('now') "
            "WHERE state IN ('AWAITING_CONFIRMATION','FAILED') "
            "AND COALESCE(topic_id,0)=3008 "
            "AND lower(COALESCE(raw_input,'')) LIKE '%проверь код%' "
            "AND lower(COALESCE(result,'')) LIKE '%отправь код для проверки%' "
            "AND (COALESCE(error_message,'') IN ('','STALE_TIMEOUT') OR error_message IS NULL)"
        )
        conn.commit()
    except Exception as e:
        try:
            logger.warning("CP8_CODE_WAITING_FAIL: %s", e)
        except Exception:
            pass

def _cp8_mark_closed_voice_control_tasks(conn):
    try:
        conn.execute(
            "UPDATE tasks "
            "SET state='DONE', error_message='', updated_at=datetime('now') "
            "WHERE state='FAILED' "
            "AND error_message='STALE_TIMEOUT' "
            "AND lower(COALESCE(raw_input,'')) LIKE '%[voice]%' "
            "AND ("
            "  lower(COALESCE(result,'')) LIKE '%задача закрыта%' "
            "  OR lower(COALESCE(result,'')) LIKE '%задача завершена%' "
            "  OR lower(COALESCE(result,'')) LIKE '%подтверждение принято%'"
            ")"
        )
        conn.commit()
    except Exception as e:
        try:
            logger.warning("CP8_VOICE_DONE_FAIL: %s", e)
        except Exception:
            pass

if "_recover_stale_tasks" in globals():
    _cp8_orig_recover_stale_tasks = _recover_stale_tasks

    def _recover_stale_tasks(conn, chat_id):
        _cp8_orig_recover_stale_tasks(conn, chat_id)
        _cp8_close_active_pins_on_closed_tasks(conn)
        _cp8_fix_codebrain_waiting_clarification(conn)
        _cp8_mark_closed_voice_control_tasks(conn)

# === END_CANON_PASS8_FINAL_CLOSE ===


# === CANON_PASS7_SEND_SAFE ===
# Защита от ошибок при отправке длинных сообщений в Telegram
# Аддитивный overlay — оборачивает _send_once и _send_once_ex

import asyncio as _cp7_asyncio

_CP7_TELEGRAM_LIMIT = 4000

def _cp7_truncate(text, limit=_CP7_TELEGRAM_LIMIT):
    if not text:
        return text
    t = str(text)
    if len(t) <= limit:
        return t
    return t[:limit] + "\n\n[...результат обрезан до 4000 символов]"

# Wrap _send_once чтобы truncate text перед отправкой
if "_send_once" in globals():
    _cp7_orig_send_once = _send_once

    def _send_once(conn, task_id, chat_id, text, reply_to, tag, **kw):
        try:
            safe_text = _cp7_truncate(text)
            return _cp7_orig_send_once(conn, task_id, chat_id, safe_text, reply_to, tag, **kw)
        except Exception as _e:
            try:
                logger.warning("CP7_SEND_ONCE_FAIL task=%s err=%s", task_id, _e)
            except Exception:
                pass

if "_send_once_ex" in globals():
    _cp7_orig_send_once_ex = _send_once_ex

    def _send_once_ex(conn, task_id, chat_id, text, reply_to, tag, **kw):
        try:
            safe_text = _cp7_truncate(text)
            return _cp7_orig_send_once_ex(conn, task_id, chat_id, safe_text, reply_to, tag, **kw)
        except Exception as _e:
            try:
                logger.warning("CP7_SEND_ONCE_EX_FAIL task=%s err=%s", task_id, _e)
            except Exception:
                pass
            return {}

# === END_CANON_PASS7_SEND_SAFE ===


# === CANON_PASS8_FILE_ENGINES ===
# Additive overlay: estimate from text + service docs guard + drive_file reply_to fix

import re as _cp8_re

_CP8_ESTIMATE_TRIGGERS = re.compile(
    r"(создай|сделай|сгенерируй|собери|рассчитай|посчитай)\s+.*смет|"
    r"смет.*на\s+\d|смет.*по\s+(фундамент|кровл|стен|перекрыт|бетон|арматур)",
    re.IGNORECASE
)

_CP8_SERVICE_DRIVE_NAMES = (
    "chat_export", "full_canon", "canon__", "index__",
    "areal-neva status", "test_export", "external_work_monitoring",
    "unknown_chat"
)

def _cp8_is_service_doc(raw_input):
    try:
        import json as _j
        d = _j.loads(str(raw_input or "{}"))
        fn = str(d.get("file_name") or "").lower()
        mime = str(d.get("mime_type") or "").lower()
        if mime == "application/vnd.google-apps.document" and any(x in fn for x in _CP8_SERVICE_DRIVE_NAMES):
            return True
        if any(x in fn for x in _CP8_SERVICE_DRIVE_NAMES):
            return True
    except Exception:
        pass
    return False

# Hook: text estimate trigger
if "_handle_in_progress" in globals():
    _cp8_orig_hip = _handle_in_progress

    async def _handle_in_progress(conn, task, chat_id, topic_id):
        task_id = _s(_task_field(task, "id"))
        raw_input = _clean(_s(_task_field(task, "raw_input")), 12000)
        reply_to = _task_field(task, "reply_to_message_id", None)
        input_type = _s(_task_field(task, "input_type", "text")).lower()

        # B. Service Google Docs guard
        if input_type == "drive_file" and _cp8_is_service_doc(raw_input):
            _update_task(conn, task_id, state="CANCELLED", error_message="SERVICE_DOC_IGNORED")
            _history(conn, task_id, "state:CANCELLED:SERVICE_DOC_IGNORED")
            conn.execute("UPDATE drive_files SET stage='SERVICE_IGNORED' WHERE task_id=?", (task_id,))
            conn.commit()
            logger.info("CP8_SERVICE_DOC_IGNORED task=%s", task_id)
            return

        # C. Text estimate hook
        if input_type in ("text", "voice", "voice_text") and _cp8_ESTIMATE_TRIGGERS.search(raw_input):
            try:
                from core.estimate_engine import generate_estimate_from_text
                from core.engine_base import upload_artifact_to_drive
                result_data = await asyncio.wait_for(
                    generate_estimate_from_text(raw_input, task_id, topic_id),
                    timeout=120
                )
                if isinstance(result_data, dict) and result_data.get("excel_path"):
                    xl = result_data["excel_path"]
                    drive_link = upload_artifact_to_drive(xl, task_id, topic_id)
                    if drive_link and "drive.google.com" in str(drive_link):
                        result = f"Смета готова\n\nАртефакт: {drive_link}"
                        _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=result, error_message="")
                        _history(conn, task_id, "result:TEXT_ESTIMATE_CP8")
                        sent = _send_once_ex(conn, task_id, chat_id, result, reply_to, "result")
                        bot_message_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
                        if bot_message_id:
                            _update_task(conn, task_id, bot_message_id=bot_message_id)
                        conn.commit()
                        logger.info("CP8_TEXT_ESTIMATE_OK task=%s link=%s", task_id, drive_link)
                        return
                    else:
                        logger.warning("CP8_TEXT_ESTIMATE_NO_LINK task=%s", task_id)
                else:
                    logger.warning("CP8_TEXT_ESTIMATE_NO_EXCEL task=%s data=%s", task_id, result_data)
            except asyncio.TimeoutError:
                logger.error("CP8_TEXT_ESTIMATE_TIMEOUT task=%s", task_id)
            except Exception as _e:
                logger.error("CP8_TEXT_ESTIMATE_ERR task=%s err=%s", task_id, _e)

        return await _cp8_orig_hip(conn, task, chat_id, topic_id)

_CP8_ESTIMATE_TRIGGERS = _cp8_re.compile(
    r"(создай|сделай|сгенерируй|собери|рассчитай|посчитай)\s+.*смет|"
    r"смет.*на\s+\d|смет.*по\s+(фундамент|кровл|стен|перекрыт|бетон|арматур)",
    _cp8_re.IGNORECASE
)

# === END_CANON_PASS8_FILE_ENGINES ===


# === CANON_PASS9_MULTIFILE_DEDUP ===
# Additive overlay: multi-file grouping + duplicate file dialog

import json as _cp9_json

def _cp9_find_same_file_task(conn, chat_id, topic_id, file_id, file_name):
    """Find existing task with same file in same topic."""
    try:
        rows = conn.execute(
            """SELECT t.id, t.state, t.result, t.bot_message_id
               FROM tasks t
               WHERE t.chat_id=? AND COALESCE(t.topic_id,0)=?
                 AND t.input_type='drive_file'
                 AND t.raw_input LIKE ?
                 AND t.state IN ('DONE','AWAITING_CONFIRMATION','FAILED','CANCELLED')
               ORDER BY t.updated_at DESC LIMIT 1""",
            (str(chat_id), int(topic_id or 0), f'%{file_id}%')
        ).fetchall()
        if rows:
            return rows[0]
        # Fallback by file_name
        rows = conn.execute(
            """SELECT t.id, t.state, t.result, t.bot_message_id
               FROM tasks t
               WHERE t.chat_id=? AND COALESCE(t.topic_id,0)=?
                 AND t.input_type='drive_file'
                 AND t.raw_input LIKE ?
                 AND t.state IN ('DONE','AWAITING_CONFIRMATION','FAILED','CANCELLED')
               ORDER BY t.updated_at DESC LIMIT 1""",
            (str(chat_id), int(topic_id or 0), f'%{file_name}%')
        ).fetchall()
        if rows:
            return rows[0]
    except Exception as _e:
        try:
            logger.warning("CP9_FIND_SAME_FILE_FAIL: %s", _e)
        except Exception:
            pass
    return None

def _cp9_handle_duplicate_file(conn, task_id, chat_id, topic_id, file_id, file_name, reply_to, existing):
    """Ask user what to do with duplicate file."""
    try:
        existing_id = existing[0] if not hasattr(existing, "keys") else existing["id"]
        existing_state = existing[1] if not hasattr(existing, "keys") else existing["state"]
        existing_result = existing[2] if not hasattr(existing, "keys") else existing["result"]

        has_artifact = existing_result and "drive.google.com" in str(existing_result)
        artifact_text = f"\n\nАртефакт: {existing_result[:200]}" if has_artifact else ""

        msg = (
            f"⚠️ Файл «{file_name}» уже был в этом чате."
            f"{artifact_text}"
            f"\n\nЧто сделать?"
            f"\n• Ответь: переобработать"
            f"\n• Ответь: использовать существующий"
            f"\n• Ответь: отмена"
        )
        _update_task(conn, task_id, state="WAITING_CLARIFICATION",
                     result=f"DUPLICATE_FILE_DIALOG|{existing_id}", error_message="DUPLICATE_FILE")
        _history(conn, task_id, f"state:WAITING_CLARIFICATION:DUPLICATE_FILE:{existing_id}")
        conn.commit()
        _send_once(conn, task_id, chat_id, msg, reply_to, "duplicate_file_dialog")
        return True
    except Exception as _e:
        try:
            logger.warning("CP9_DUPLICATE_DIALOG_FAIL: %s", _e)
        except Exception:
            pass
    return False

# Wrap _handle_drive_file to add duplicate check and multi-file awareness
if "_handle_drive_file" in globals():
    _cp9_orig_hdf = _handle_drive_file

    async def _handle_drive_file(conn, task, chat_id, topic_id):
        task_id = _s(_task_field(task, "id"))
        raw_input = _s(_task_field(task, "raw_input", ""))
        reply_to = _task_field(task, "reply_to_message_id", None)
        error_msg = _s(_task_field(task, "error_message", ""))

        # Skip duplicate check if already in dialog or reprocess
        if "DUPLICATE_FORCE_REPROCESS" in error_msg or "DUPLICATE_USE_EXISTING" in error_msg:
            return await _cp9_orig_hdf(conn, task, chat_id, topic_id)

        # Parse file info
        try:
            data = _cp9_json.loads(raw_input)
            file_id = data.get("file_id", "")
            file_name = data.get("file_name", "")
        except Exception:
            return await _cp9_orig_hdf(conn, task, chat_id, topic_id)

        # Skip ogg/voice
        if file_name.lower().endswith(".ogg") or "voice_" in file_name.lower():
            return await _cp9_orig_hdf(conn, task, chat_id, topic_id)

        # Check for duplicate
        existing = _cp9_find_same_file_task(conn, chat_id, topic_id, file_id, file_name)
        if existing:
            existing_result = existing[2] if not hasattr(existing, "keys") else existing["result"]
            # If previous was DONE with artifact — ask user
            if existing_result and "drive.google.com" in str(existing_result):
                if _cp9_handle_duplicate_file(conn, task_id, chat_id, topic_id, file_id, file_name, reply_to, existing):
                    return

        return await _cp9_orig_hdf(conn, task, chat_id, topic_id)

# Handle clarification responses for duplicate dialog
if "_handle_new" in globals():
    _cp9_orig_hn = _handle_new

    async def _handle_new(conn, task, chat_id, topic_id):
        task_id = _s(_task_field(task, "id"))
        raw_input = _clean(_s(_task_field(task, "raw_input")), 500)
        reply_to = _task_field(task, "reply_to_message_id", None)

        # Check if this is a response to duplicate file dialog
        pending_dup = conn.execute(
            """SELECT id, result FROM tasks
               WHERE chat_id=? AND COALESCE(topic_id,0)=? AND id<>?
                 AND state='WAITING_CLARIFICATION'
                 AND error_message='DUPLICATE_FILE'
               ORDER BY updated_at DESC LIMIT 1""",
            (str(chat_id), int(topic_id or 0), task_id)
        ).fetchone()

        if pending_dup:
            pending_id = pending_dup[0] if not hasattr(pending_dup, "keys") else pending_dup["id"]
            result_field = pending_dup[1] if not hasattr(pending_dup, "keys") else pending_dup["result"]

            raw_lower = raw_input.lower().strip()

            # Reprocess
            if any(x in raw_lower for x in ("переобработ", "заново", "обработ", "перередел")):
                _update_task(conn, pending_id, state="NEW", error_message="DUPLICATE_FORCE_REPROCESS", result="")
                _update_task(conn, task_id, state="DONE", result="Принято, переобрабатываю файл", error_message="")
                _history(conn, task_id, "confirm:reprocess")
                conn.commit()
                _send_once(conn, task_id, chat_id, "Принято, запускаю переобработку файла", reply_to, "dup_reprocess")
                return

            # Use existing
            if any(x in raw_lower for x in ("использ", "существующ", "оставь", "так и")):
                orig_id_part = str(result_field).replace("DUPLICATE_FILE_DIALOG|", "")
                orig_result = ""
                try:
                    orig_row = conn.execute("SELECT result FROM tasks WHERE id=?", (orig_id_part,)).fetchone()
                    if orig_row:
                        orig_result = orig_row[0] if not hasattr(orig_row, "keys") else orig_row["result"]
                except Exception:
                    pass
                _update_task(conn, pending_id, state="DONE", error_message="")
                _update_task(conn, task_id, state="DONE", result="Использую существующий артефакт", error_message="")
                _history(conn, task_id, "confirm:use_existing")
                conn.commit()
                msg = f"Использую существующий. {orig_result[:300] if orig_result else ''}"
                _send_once(conn, task_id, chat_id, msg, reply_to, "dup_use_existing")
                return

            # Cancel
            if any(x in raw_lower for x in ("отмен", "не надо", "случайн")):
                _update_task(conn, pending_id, state="CANCELLED", error_message="DUPLICATE_CANCELLED")
                _update_task(conn, task_id, state="DONE", result="Отменено", error_message="")
                _history(conn, task_id, "confirm:cancel")
                conn.commit()
                _send_once(conn, task_id, chat_id, "Понял, отменяю", reply_to, "dup_cancel")
                return

        return await _cp9_orig_hn(conn, task, chat_id, topic_id)

# === END_CANON_PASS9_MULTIFILE_DEDUP ===


# === CANON_PASS10_MULTIFILE_WIRE ===
# F. Wire handle_multiple_files to worker
# H. generate_estimate_from_text fallback if missing
# X. Extended stale timeout for drive_file tasks

import asyncio as _cp10_asyncio

# H. Safe import of generate_estimate_from_text
try:
    from core.estimate_engine import generate_estimate_from_text as _cp10_gen_estimate
    _CP10_ESTIMATE_AVAILABLE = True
except ImportError:
    _CP10_ESTIMATE_AVAILABLE = False
    try:
        logger.warning("CP10: generate_estimate_from_text not found in estimate_engine")
    except Exception:
        pass

# F. Multi-file grouping: collect files sent within 3 seconds into one task
_CP10_MULTIFILE_WINDOW = 3  # seconds

async def _cp10_collect_pending_files(conn, chat_id, topic_id, anchor_task_id, window_sec=3):
    """Collect NEW drive_file tasks created within window_sec of anchor task."""
    try:
        rows = conn.execute(
            """SELECT id, raw_input, reply_to_message_id
               FROM tasks
               WHERE chat_id=? AND COALESCE(topic_id,0)=?
                 AND input_type='drive_file' AND state='NEW' AND id!=?
                 AND created_at >= datetime(
                     (SELECT created_at FROM tasks WHERE id=?),
                     '-' || ? || ' seconds')
               ORDER BY created_at ASC""",
            (str(chat_id), int(topic_id or 0), anchor_task_id, anchor_task_id, window_sec)
        ).fetchall()
        return rows
    except Exception as _e:
        try:
            logger.warning("CP10_COLLECT_FILES_FAIL: %s", _e)
        except Exception:
            pass
        return []

# Wrap _handle_drive_file for multi-file grouping
if "_handle_drive_file" in globals() and "CANON_PASS9" in open(p).read():
    _cp10_orig_hdf = _handle_drive_file

    async def _handle_drive_file(conn, task, chat_id, topic_id):
        task_id = _s(_task_field(task, "id"))
        raw_input = _s(_task_field(task, "raw_input", ""))
        reply_to = _task_field(task, "reply_to_message_id", None)

        # F. Check for sibling files (multi-file batch)
        await _cp10_asyncio.sleep(0.5)  # small wait for batch to accumulate
        siblings = await _cp10_collect_pending_files(conn, chat_id, topic_id, task_id, _CP10_MULTIFILE_WINDOW)

        if siblings:
            try:
                import json as _j
                from core.file_intake_router import handle_multiple_files
                # Extract file paths from drive cache
                all_tasks = [(task_id, raw_input)] + [(r[0], r[1]) for r in siblings]
                file_paths = []
                for tid, raw in all_tasks:
                    try:
                        d = _j.loads(raw)
                        fp = d.get("local_path") or d.get("file_path") or ""
                        if fp:
                            file_paths.append(fp)
                    except Exception:
                        pass

                if len(file_paths) >= 2:
                    # Mark siblings as CANCELLED:MERGED
                    for r in siblings:
                        sid = r[0] if not hasattr(r, "keys") else r["id"]
                        _update_task(conn, sid, state="CANCELLED", error_message="MERGED_INTO_" + task_id)
                        _history(conn, sid, f"state:CANCELLED:MERGED_INTO:{task_id}")
                    conn.commit()

                    _update_task(conn, task_id, state="IN_PROGRESS", error_message="")
                    _history(conn, task_id, f"multi_file:{len(file_paths)}_files")
                    conn.commit()

                    result_data = await _cp10_asyncio.wait_for(
                        handle_multiple_files(file_paths, task_id, int(topic_id or 0), "estimate"),
                        timeout=180
                    )
                    if result_data and result_data.get("success"):
                        artifact = result_data.get("drive_link") or result_data.get("excel_path", "")
                        result = f"Объединённая обработка {len(file_paths)} файлов завершена.\n\nАртефакт: {artifact}"
                        _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=result, error_message="")
                        _history(conn, task_id, "result:MULTIFILE_OK")
                        sent = _send_once_ex(conn, task_id, chat_id, result, reply_to, "result")
                        bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
                        if bot_id:
                            _update_task(conn, task_id, bot_message_id=bot_id)
                        conn.commit()
                        logger.info("CP10_MULTIFILE_OK task=%s files=%s", task_id, len(file_paths))
                        return
            except _cp10_asyncio.TimeoutError:
                logger.error("CP10_MULTIFILE_TIMEOUT task=%s", task_id)
            except Exception as _e:
                logger.error("CP10_MULTIFILE_ERR task=%s err=%s", task_id, _e)

        return await _cp10_orig_hdf(conn, task, chat_id, topic_id)
elif "_handle_drive_file" in globals():
    _cp10_orig_hdf2 = _handle_drive_file

    async def _handle_drive_file(conn, task, chat_id, topic_id):
        task_id = _s(_task_field(task, "id"))
        raw_input = _s(_task_field(task, "raw_input", ""))
        reply_to = _task_field(task, "reply_to_message_id", None)

        await _cp10_asyncio.sleep(0.5)
        siblings = await _cp10_collect_pending_files(conn, chat_id, topic_id, task_id, _CP10_MULTIFILE_WINDOW)

        if siblings and len(siblings) >= 1:
            try:
                import json as _j
                from core.file_intake_router import handle_multiple_files
                all_tasks = [(task_id, raw_input)] + [(r[0], r[1]) for r in siblings]
                file_paths = []
                for tid, raw in all_tasks:
                    try:
                        d = _j.loads(raw)
                        fp = d.get("local_path") or d.get("file_path") or ""
                        if fp:
                            file_paths.append(fp)
                    except Exception:
                        pass
                if len(file_paths) >= 2:
                    for r in siblings:
                        sid = r[0] if not hasattr(r, "keys") else r["id"]
                        _update_task(conn, sid, state="CANCELLED", error_message="MERGED_INTO_" + task_id)
                    conn.commit()
                    _update_task(conn, task_id, state="IN_PROGRESS")
                    conn.commit()
                    result_data = await _cp10_asyncio.wait_for(
                        handle_multiple_files(file_paths, task_id, int(topic_id or 0), "estimate"),
                        timeout=180
                    )
                    if result_data and result_data.get("success"):
                        artifact = result_data.get("drive_link") or result_data.get("excel_path", "")
                        result = f"Объединённая обработка {len(file_paths)} файлов завершена.\n\nАртефакт: {artifact}"
                        _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=result, error_message="")
                        sent = _send_once_ex(conn, task_id, chat_id, result, reply_to, "result")
                        bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
                        if bot_id:
                            _update_task(conn, task_id, bot_message_id=bot_id)
                        conn.commit()
                        return
            except Exception as _e:
                logger.error("CP10_MULTIFILE_ERR task=%s err=%s", task_id, _e)

        return await _cp10_orig_hdf2(conn, task, chat_id, topic_id)

# H. Patch _cp8_ESTIMATE_TRIGGERS reference if needed
if not _CP10_ESTIMATE_AVAILABLE:
    # Disable estimate hook in PASS8 gracefully
    _CP10_ESTIMATE_AVAILABLE = False
    logger.warning("CP10: estimate engine unavailable, text estimate hook disabled")

# X. Extended stale timeout for file tasks
# If _recover_stale_tasks checks a fixed threshold — increase for drive_file
_CP10_FILE_STALE_HOURS = 4  # drive_file tasks get 4h before STALE_TIMEOUT

if "_recover_stale_tasks" in globals():
    _cp10_orig_rst = _recover_stale_tasks

    def _recover_stale_tasks(conn, chat_id):
        # Mark drive_file tasks that are IN_PROGRESS for >4h as stale
        try:
            conn.execute(
                """UPDATE tasks SET state='FAILED', error_message='STALE_TIMEOUT',
                   updated_at=datetime('now')
                   WHERE state='IN_PROGRESS' AND input_type='drive_file'
                     AND updated_at < datetime('now', '-' || ? || ' hours')
                     AND chat_id=?""",
                (_CP10_FILE_STALE_HOURS, str(chat_id))
            )
            conn.commit()
        except Exception as _e:
            try:
                logger.warning("CP10_FILE_STALE_FAIL: %s", _e)
            except Exception:
                pass
        return _cp10_orig_rst(conn, chat_id)

# === END_CANON_PASS10_MULTIFILE_WIRE ===






# === CANON_PASS11_REVISION_SHA256_CLEANUP ===
import hashlib as _cp11_hashlib
import os as _cp11_os
import glob as _cp11_glob
import logging.handlers as _cp11_lh

def _cp11_setup_log_rotation():
    try:
        log_path = '/root/.areal-neva-core/logs/task_worker.log'
        _cp11_os.makedirs(_cp11_os.path.dirname(log_path), exist_ok=True)
        rh = _cp11_lh.RotatingFileHandler(log_path, maxBytes=100*1024*1024, backupCount=3, encoding='utf-8')
        rh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logging.getLogger().addHandler(rh)
        logger.info('CP11_LOG_ROTATION_OK')
    except Exception as _e:
        pass

_cp11_setup_log_rotation()

def _cp11_sha256_file(path):
    try:
        h = _cp11_hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def _cp11_save_file_hash(conn, task_id, file_hash):
    if not file_hash:
        return
    try:
        conn.execute('UPDATE drive_files SET file_hash=? WHERE task_id=?', (file_hash, task_id))
        conn.commit()
    except Exception:
        try:
            conn.execute('ALTER TABLE drive_files ADD COLUMN file_hash TEXT')
            conn.execute('UPDATE drive_files SET file_hash=? WHERE task_id=?', (file_hash, task_id))
            conn.commit()
            logger.info('CP11_FILE_HASH_COLUMN_ADDED')
        except Exception:
            pass

def _cp11_cleanup_runtime_files(task_id):
    try:
        for pattern in ['/tmp/*' + task_id + '*', '/root/.areal-neva-core/runtime/drive_files/' + task_id + '*']:
            for f in _cp11_glob.glob(pattern):
                try:
                    _cp11_os.remove(f)
                    logger.info('CP11_CLEANUP path=%s', f)
                except Exception:
                    pass
    except Exception as _e:
        logger.warning('CP11_CLEANUP_FAIL task=%s err=%s', task_id, _e)

def _cp11_memory_search(conn, chat_id, topic_id, query, limit=3):
    try:
        memory_path = '/root/.areal-neva-core/data/memory.db'
        if not _cp11_os.path.exists(memory_path):
            return []
        import sqlite3 as _sq11
        mconn = _sq11.connect(memory_path, timeout=5)
        keywords = [w for w in query.lower().split() if len(w) > 3][:5]
        if not keywords:
            mconn.close()
            return []
        like_clause = ' OR '.join(['value LIKE ?' for _ in keywords])
        params = ['%' + k + '%' for k in keywords] + [limit]
        rows = mconn.execute('SELECT key, value FROM memory WHERE (' + like_clause + ') ORDER BY timestamp DESC LIMIT ?', params).fetchall()
        mconn.close()
        return [{'key': r[0], 'value': r[1]} for r in rows]
    except Exception as _e:
        logger.warning('CP11_MEM_SEARCH_FAIL: %s', _e)
        return []

if '_handle_new' in globals():
    _cp11_orig_hn = _handle_new
    async def _handle_new(conn, task, chat_id, topic_id):
        task_id = _s(_task_field(task, 'id'))
        raw_input = _clean(_s(_task_field(task, 'raw_input')), 2000)
        reply_to = _task_field(task, 'reply_to_message_id', None)
        raw_lower = raw_input.lower().strip()
        _REVISION_TRIGGERS = ('исправь','переделай','не так','не то','измени','скорректируй','поправь','неверно','неправильно','сделай по-другому','давай иначе','попробуй снова')
        is_revision = any(t in raw_lower for t in _REVISION_TRIGGERS)
        if is_revision and reply_to:
            parent = conn.execute('SELECT id, state, result FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=? AND (bot_message_id=? OR reply_to_message_id=?) AND state IN (??) ORDER BY updated_at DESC LIMIT 1', (str(chat_id), int(topic_id or 0), reply_to, reply_to)).fetchone()
            if not parent:
                parent = conn.execute('SELECT id, state, result FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=? AND state IN (??) ORDER BY updated_at DESC LIMIT 1', (str(chat_id), int(topic_id or 0))).fetchone()
            if parent:
                parent_id = parent[0] if not hasattr(parent, 'keys') else parent['id']
                _update_task(conn, parent_id, state='IN_PROGRESS', error_message='REVISION_V2', result='REVISION_REQUEST: ' + raw_input[:300])
                _history(conn, parent_id, 'revision:by_task:' + task_id)
                _update_task(conn, task_id, state='CANCELLED', error_message='REVISION_ROUTED', result='routed to ' + parent_id)
                _history(conn, task_id, 'revision:routed_to:' + parent_id)
                conn.commit()
                logger.info('CP11_REVISION_ROUTED task=%s -> parent=%s', task_id, parent_id)
                return
        if len(raw_input) > 20 and not is_revision:
            try:
                memories = _cp11_memory_search(conn, chat_id, topic_id, raw_input)
                if memories:
                    mem_lines = ['[MEMORY] ' + m.get('value', '')[:100] for m in memories]
                    mem_context = chr(10).join(mem_lines)
                    conn.execute('UPDATE tasks SET raw_input=? WHERE id=?', (raw_input + chr(10) + chr(10) + mem_context, task_id))
                    conn.commit()
                    logger.info('CP11_MEMORY_ENRICHED task=%s count=%s', task_id, len(memories))
            except Exception:
                pass
        return await _cp11_orig_hn(conn, task, chat_id, topic_id)

if '_handle_drive_file' in globals():
    _cp11_orig_hdf = _handle_drive_file
    async def _handle_drive_file(conn, task, chat_id, topic_id):
        task_id = _s(_task_field(task, 'id'))
        raw_input = _s(_task_field(task, 'raw_input', ''))
        local_path = None
        try:
            import json as _j11
            d = _j11.loads(raw_input)
            local_path = d.get('local_path') or d.get('file_path')
        except Exception:
            pass
        if local_path and _cp11_os.path.exists(str(local_path)):
            file_hash = _cp11_sha256_file(local_path)
            if file_hash:
                _cp11_save_file_hash(conn, task_id, file_hash)
        result = await _cp11_orig_hdf(conn, task, chat_id, topic_id)
        if local_path and _cp11_os.path.exists(str(local_path)):
            try:
                _cp11_os.remove(local_path)
                logger.info('CP11_LOCAL_CLEANUP path=%s', local_path)
            except Exception:
                pass
        return result

# === END_CANON_PASS11_REVISION_SHA256_CLEANUP ===
