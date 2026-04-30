
def _force_voice_finish(raw_input: str, result: str) -> bool:
    if not raw_input:
        return False
    low = raw_input.lower()
    if any(x in low for x in ["заверш", "доволен", "да", "ок", "ok"]):
        if "не доволен" in low:
            return False
        return True
    return False

import os
BASE = "/root/.areal-neva-core"

import re
import time
import json
import sqlite3
import asyncio
import hashlib
import datetime
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
    "нет данных",
    "повторите",
    "не знаю",
    "чат не содержит активной задачи",
    "привет. чат не содержит активной задачи",
    "чат создан для",
    "тест диагностика",
    "не понял запрос",
    "уточните",
    "не понимаю",
    "задайте вопрос",
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


def _send_once(conn: sqlite3.Connection, task_id: str, chat_id: str, text: str, reply_to: Optional[int], kind: str) -> bool:
    if _already_replied(conn, task_id, kind):
        return True
    ok = send_reply(chat_id=chat_id, text=text, reply_to_message_id=reply_to)
    if ok:
        _history(conn, task_id, f"reply_sent:{kind}")
    return bool(ok)


def _send_once_ex(conn: sqlite3.Connection, task_id: str, chat_id: str, text: str, reply_to: Optional[int], kind: str) -> Dict[str, Any]:
    if _already_replied(conn, task_id, kind):
        return {"ok": True, "bot_message_id": None, "skipped": True}
    res = send_reply_ex(chat_id=chat_id, text=text, reply_to_message_id=reply_to)
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
        r"^(?:\[voice\]\s*)?этот топик для\s+(.+)$",
        r"^(?:\[voice\]\s*)?этот топик про\s+(.+)$",
        r"^(?:\[voice\]\s*)?чат закрепл[её]н за\s+(.+)$",
        r"^(?:\[voice\]\s*)?этот чат исключительно для\s+(.+)$",
        r"^(?:\[voice\]\s*)?этот чат используется для\s+(.+)$",
        r"^(?:\[voice\]\s*)?закрепи чат за\s+(.+)$",
        r"^(?:\[voice\]\s*)?закрепи этот чат за\s+(.+)$",
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

        MEMORY_MUTEX_MARKERS = [
            "последние действия",
            "этот чат закреплён за: последние действия",
            "в этом чате были следующие действия",
            "текущий статус: ожидание подтверждения",
            "текущий статус:",
            "задача отменена",
            "задача завершена",
            "задача закрыта",
            "задачи завершены",
            "подтверждение принято",
            "не понимаю запрос",
            "готов к выполнению задачи",
            "без контекста",
            "задайте конкретный вопрос",
            "конкретный вопрос по",
            "нет, не помню",
        ]

        for row in rows:
            key = _s(row["key"])
            raw_value = _s(row["value"])
            if key.endswith("_user_input") or key.endswith("_role"):
                limit = 500
            elif key.endswith("_task_summary"):
                limit = 20000
            elif key.endswith("_assistant_output"):
                limit = 50000
            elif key.endswith("_directions"):
                limit = 1000
            else:
                limit = 500
            value = _clean(raw_value, limit)
            if not value:
                continue
            low = value.lower()
            if _is_memory_noise(low) or any(x in low for x in MEMORY_BAD_MARKERS):
                continue
            if any(m in low for m in MEMORY_MUTEX_MARKERS):
                continue

            if key.endswith("_role") and not topic_role:
                topic_role = value[:500]
                continue

            if not topic_role and (key.endswith("_assistant_output") or key.endswith("_task_summary")):
                m = re.search(r"чат закрепл[её]н за темами:\s*(.+?)(?:\.|$)", value, re.I)
                if not m:
                    m = re.search(r"чат закрепл[её]н за\s*(.+?)(?:\.|$)", value, re.I)
                if not m:
                    m = re.search(r"закреплено:\s*чат для\s*(.+?)(?:\.|$)", value, re.I)
                if not m:
                    m = re.search(r"этот чат используется для\s*(.+?)(?:\.|$)", value, re.I)
                if m:
                    topic_role = _clean(m.group(1), 500)

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
    STOP_WORDS = {"это","как","что","где","когда","для","почему","зачем","кто"}
    words = {w for w in re.findall(r"\w+", _clean(user_text).lower()) if len(w) > 3 and w not in STOP_WORDS}
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

    scored = [(ov, blob) for ov, blob in scored if ov > 0]
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
        raw = _clean(_s(_task_field(row, "raw_input")), 300)
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
    low = (result or "").lower()
    if any(x in low for x in [
        "без контекста","не понимаю запрос","не помню",
        "задача завершена","задача закрыта","подтверждение принято",
        "готов к выполнению задачи"
    ]):
        return

    bad = [
        "ошибка",
        "не найдено",
        "уточните",
        "traceback",
        "/root/",
        ".ogg",
        "delete from",
        "task_worker.py",
        "telegram_daemon.py",
    ]
    if not result or len(result) < MIN_RESULT_LEN:
        return
    low = result.lower()
    if any(b in low for b in bad):
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
            (str(chat_id), f"{prefix}task_summary", _clean(result, 20000) if len(result) >= MIN_RESULT_LEN else ""),
        )
        conn.execute(
            "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(chat_id), f"{prefix}user_input", _clean(raw_input, 500)),
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
    if result:
        _save_memory(chat_id, topic_id, raw_input, result)
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
        "state IN ('IN_PROGRESS','WAITING_CLARIFICATION')",
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
        _send_once(conn, task_id, tg_chat_id, "Задача не выполнена. Повтори или уточни запрос", reply_to, "stale_failed")

    done_markers = [
        "задача завершена",
        "задача закрыта",
        "задачи завершены",
        "подтверждение принято",
    ]
    junk_markers = [
        "без контекста",
        "задайте конкретный вопрос",
        "конкретный вопрос по",
        "нет, не помню",
        "не понимаю запрос",
        "готов к выполнению задачи",
    ]

    rows = conn.execute("""
        SELECT id, chat_id, COALESCE(topic_id,0) AS topic_id, reply_to_message_id, result, raw_input, input_type, updated_at, created_at
        FROM tasks
        WHERE state = 'AWAITING_CONFIRMATION'
    """).fetchall()

    now_utc = datetime.datetime.now(datetime.timezone.utc)

    for row in rows:
        updated = row["updated_at"] or row["created_at"]
        if not updated:
            continue

        result = _s(row["result"])
        low_result = result.lower()
        row_raw_input = ""
        try:
            row_raw_input = _s(row["raw_input"])
        except Exception:
            row_raw_input = ""
        if _force_voice_finish(row_raw_input, result):
            _update_task(conn, row["id"], state="DONE")
            continue  # FORCE_VOICE_FINISH_HOOK

        if any(m in low_result for m in done_markers):
            _update_task(conn, row["id"], state="DONE", error_message="")
            _close_pin(conn, row["id"])
            _history(conn, row["id"], "state:DONE")
            conn.commit()
            continue

        if any(m in low_result for m in junk_markers):
            _update_task(conn, row["id"], state="FAILED", error_message="JUNK_RESULT_CLEANUP")
            _close_pin(conn, row["id"])
            _history(conn, row["id"], "state:FAILED")
            conn.commit()
            continue

        try:
            s = str(updated).strip()
            if "T" in s:
                dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
            else:
                dt = datetime.datetime.fromisoformat(s)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
        except Exception:
            continue

        hours_old = (now_utc - dt).total_seconds() / 3600.0
        if hours_old <= 24:
            continue

        if _s(row["input_type"]).lower() == "drive_file" and hours_old > 48:
            _update_task(conn, row["id"], state="FAILED", error_message="drive_upload_stale")
            _close_pin(conn, row["id"])
            _history(conn, row["id"], "state:FAILED")
            conn.commit()
        elif hours_old > 168:
            _update_task(conn, row["id"], state="ARCHIVED")
            _close_pin(conn, row["id"])
            _history(conn, row["id"], "state:ARCHIVED")
            conn.commit()

    conn.execute("""
        UPDATE pin
        SET state='CLOSED', updated_at=datetime('now')
        WHERE state='ACTIVE'
          AND task_id IN (
              SELECT id FROM tasks
              WHERE state='FAILED'
                 OR lower(COALESCE(result,'')) LIKE '%задача закрыта%'
                 OR lower(COALESCE(result,'')) LIKE '%подтверждение принято%'
                 OR lower(COALESCE(result,'')) LIKE '%без контекста%'
                 OR lower(COALESCE(result,'')) LIKE '%конкретный вопрос%'
                 OR lower(COALESCE(result,'')) LIKE '%не помню%'
          )
    """)
    conn.commit()



# === FULLFIX_13D_TASK_WORKER_SEND_BELT ===
# reply_sender also strips MANIFEST globally
# === END FULLFIX_13D_TASK_WORKER_SEND_BELT ===

# === FULLFIX_13C_STRIP_MANIFEST_BEFORE_SEND ===
def _ff13c_strip_manifest_links(text):
    import re
    msg = str(text or "")
    msg = re.sub(r"(?im)^MANIFEST:\s*https?://\S+\s*$", "", msg)
    msg = re.sub(r"(?im)^Manifest:\s*https?://\S+\s*$", "", msg)
    msg = re.sub(r"\n{3,}", "\n\n", msg).strip()
    return msg
# === END FULLFIX_13C_STRIP_MANIFEST_BEFORE_SEND ===


async def _handle_new(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> None:
    task_id = _s(_task_field(task, "id"))
    raw_input = _clean(_s(_task_field(task, "raw_input")), 4000)
    reply_to = _task_field(task, "reply_to_message_id", None)




    
    # === FULLFIX_16_CONTEXT_QUERY ===
    try:
        _ff16_low = str(raw_input or "").strip().lower().rstrip("!?. ")
        _ff16_low = _ff16_low.replace("[voice] ", "").replace("[VOICE] ", "").strip()  # FF21_FIX_VOICE_PREFIX
        _ff16_triggers = ["nu chto", "gde rezultat", "chto tam", "gde smeta", "gde proekt"]
        _ff16_ru_triggers = [
            "ну что",
            "где результат",
            "что там",
            "где смета",
            "где проект",
            "что с задачей",
            "что там у нас",
            "ну как там",
            "где файл",
            "ну что там",
            "ну давай",
            "что по задаче",
        ]
        _ff16_is_ctx = len(_ff16_low) <= 35 and any(
            _ff16_low == t or _ff16_low.startswith(t) for t in _ff16_ru_triggers
        )
        if _ff16_is_ctx:
            _ff16_row = conn.execute(
                "SELECT id,state,result FROM tasks"
                " WHERE chat_id=? AND COALESCE(topic_id,0)=? AND id<>?"
                " AND state IN ('AWAITING_CONFIRMATION','IN_PROGRESS','WAITING_CLARIFICATION')"
                " ORDER BY updated_at DESC LIMIT 1",
                (chat_id, topic_id, task_id)
            ).fetchone()
            if _ff16_row is not None:
                _ff16_pid, _ff16_pst, _ff16_pres = _ff16_row
                _ff16_parts = ["Статус: " + str(_ff16_pst)]
                if _ff16_pres is not None:
                    import re as _re16
                    _ff16_clean = _re16.sub(
                        r"(?im)^\s*MANIFEST\s*:\s*https?://\S+\s*$",
                        "",
                        str(_ff16_pres)[:800]
                    ).strip()
                    _ff16_parts.append(_ff16_clean)
                _ff16_msg = "\n".join(_ff16_parts)
                from core.reply_sender import send_reply_ex
                send_reply_ex(chat_id=str(chat_id), text=_ff16_msg, reply_to_message_id=reply_to, message_thread_id=topic_id)  # FULLFIX_20_CONTEXT_QUERY_TOPIC
                conn.execute(
                    "UPDATE tasks SET state='DONE',result=?,updated_at=datetime('now') WHERE id=?",
                    ("Ответил по активной задаче", task_id)
                )
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, "state:DONE:context_query_ff16")
                )
                conn.commit()
                return
    except Exception as _ff16_ctx_err:
        logger.error("FULLFIX_16_CONTEXT_QUERY_ERROR task=%s err=%s", task_id, _ff16_ctx_err)
    # === END FULLFIX_16_CONTEXT_QUERY ===

    # === FULLFIX_14_UNIFIED_ROUTE ===
    try:
        from core.template_intake_engine import is_sample_intent as _ff14_is_sample, process_template_intake as _ff14_tmpl
        from core.defect_act_engine import is_defect_act_intent as _ff14_is_defect, process_defect_act as _ff14_defect
        from core.multifile_artifact_engine import is_multifile_intent as _ff14_is_multi, process_multifile as _ff14_multi
        from core.estimate_unified_engine import process_estimate_task as _ff14_estimate, parse_estimate_rows as _ff14_parse
        _ff14_raw = str(raw_input or "")
        _ff14_itype = str(_task_field(task, "input_type") or "")
        _ff14_mime = ""
        _ff14_fname = ""
        _ff14_lpath = ""
        if _ff14_itype == "drive_file":
            try:
                import json as _ff14j
                _ff14_meta = _ff14j.loads(_task_field(task, "raw_input") or "{}")
                _ff14_mime = _ff14_meta.get("mime_type", "")
                _ff14_fname = _ff14_meta.get("file_name", "")
                _ff14_lpath = _ff14_meta.get("local_path", "")
            except Exception:
                pass
        # 1. template/sample intake — highest priority
        if _ff14_is_sample(_ff14_raw):
            _ff14_done = await _ff14_tmpl(
                conn=conn, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                raw_input=_ff14_raw, local_path=_ff14_lpath,
                file_name=_ff14_fname, mime_type=_ff14_mime
            )
            if _ff14_done:
                return
        # 2. defect/photo act
        if _ff14_is_defect(_ff14_raw, _ff14_mime):
            _ff14_done = await _ff14_defect(
                conn=conn, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                raw_input=_ff14_raw, file_name=_ff14_fname, local_path=_ff14_lpath
            )
            if _ff14_done:
                return
        # 3. estimate from natural language text
        if _ff14_itype in ("text", "search") and _ff14_parse(_ff14_raw):
            # === FULLFIX_16_ESTIMATE_HARD_STOP ===
            # Estimate route: ALWAYS return, never fall through to FULLFIX_10
            conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (task_id, "FULLFIX_16_ESTIMATE_ROUTE_TAKEN"))
            conn.commit()
            _ff14_done = await _ff14_estimate(
                conn=conn, task_id=task_id, chat_id=chat_id, topic_id=topic_id, raw_input=_ff14_raw
            )
            # Whether success or failure — do not let FULLFIX_10 run on estimate input
            return
            # === END FULLFIX_16_ESTIMATE_HARD_STOP ===
        # 4. multifile aggregation
        if _ff14_is_multi(_ff14_raw):
            _ff14_done = await _ff14_multi(
                conn=conn, task_id=task_id, chat_id=chat_id, topic_id=topic_id, raw_input=_ff14_raw
            )
            if _ff14_done:
                return
    except Exception as _ff14_err:
        try:
            logger.error("FULLFIX_14_ROUTE_ERROR task=%s err=%s", task_id, str(_ff14_err))
        except Exception:
            pass
    # === END FULLFIX_14_UNIFIED_ROUTE ===

# === FULLFIX_13A_SAMPLE_TEMPLATE_AND_TEMPLATE_ESTIMATE_ROUTE ===
    try:
        from core.sample_template_engine import (
            handle_sample_template_intent as _ff13a_handle_sample_template_intent,
            handle_template_estimate_intent as _ff13a_handle_template_estimate_intent,
        )
        # === FULLFIX_13A_ROUTE_LOCALS_FIX ===
        # _handle_new has task/raw_input/reply_to locals, not input_type/reply_to_message_id locals
        _ff13a_conn = conn
        _ff13a_task_id = str(task_id or "")
        _ff13a_chat_id = str(chat_id or "")
        _ff13a_topic_id = int(topic_id or 0)
        _ff13a_raw_input = str(raw_input or "")
        _ff13a_input_type = str(_task_field(task, "input_type", "") or "")
        _ff13a_reply_to = _task_field(task, "reply_to_message_id", None) or _task_field(task, "telegram_message_id", None)
        # === END FULLFIX_13A_ROUTE_LOCALS_FIX ===
        _ff13a_done = await _ff13a_handle_sample_template_intent(
            conn=_ff13a_conn,
            task_id=_ff13a_task_id,
            chat_id=_ff13a_chat_id,
            topic_id=_ff13a_topic_id,
            raw_input=_ff13a_raw_input,
            input_type=_ff13a_input_type,
            reply_to_message_id=_ff13a_reply_to,
        )
        # === FULLFIX_13B_SAMPLE_HARD_STOP_1 ===
        if _ff13a_done:
            try:
                conn.commit()
            except Exception:
                pass
            return
        _ff13a_done = await _ff13a_handle_template_estimate_intent(
            conn=_ff13a_conn,
            task_id=_ff13a_task_id,
            chat_id=_ff13a_chat_id,
            topic_id=_ff13a_topic_id,
            raw_input=_ff13a_raw_input,
            input_type=_ff13a_input_type,
            reply_to_message_id=_ff13a_reply_to,
        )
        # === FULLFIX_13B_SAMPLE_HARD_STOP_2 ===
        if _ff13a_done:
            try:
                conn.commit()
            except Exception:
                pass
            return
    except Exception as _ff13a_err:
        try:
            logger.error("FULLFIX_13A_SAMPLE_ROUTE_ERROR task=%s err=%s", task_id, str(_ff13a_err))
        except Exception:
            pass
    # === END FULLFIX_13A_SAMPLE_TEMPLATE_AND_TEMPLATE_ESTIMATE_ROUTE ===


    # === FULLFIX_19_PROJECT_GUARD_REAL_V2 ===
    try:
        _ff19_low = str(raw_input or "").strip().lower()
        _ff19_short_replies = {"да","нет","ок","готово","угу","так","ясно","понятно"}
        if _ff19_low in _ff19_short_replies:
            try:
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, "FULLFIX_19_PROJECT_GUARD_BLOCKED_SHORT_REPLY")
                )
                conn.execute(
                    "UPDATE tasks SET state='DONE', updated_at=datetime('now'), result=COALESCE(NULLIF(result,''),?) WHERE id=?",
                    ("Принято", task_id)
                )
                conn.commit()
            except Exception:
                pass
            logger.info("FF19_GUARD_BLOCKED_SHORT_REPLY task=%s text=%s", task_id, _ff19_low)
            return
    except Exception as _ff19_err:
        logger.error("FF19_PROJECT_GUARD_ERR task=%s err=%s", task_id, _ff19_err)
    # === END FULLFIX_19_PROJECT_GUARD_REAL_V2 ===

    # === FULLFIX_13B_FALSE_PROJECT_PHRASE_GUARD ===
    try:
        _ff13b_low = str(raw_input or "").strip().lower()
        _ff13b_false_project_phrases = {
            "это один из вариантов",
            "это как образец",
            "это пример",
            "вот образец",
            "вот пример",
            "сохрани как образец",
        }
        if _ff13b_low in _ff13b_false_project_phrases:
            _msg = "Принял как образец. Дальше можно писать простым языком: сделай смету / сделай проект"
            await safe_update(conn, task_id, state="DONE", result=_ff13c_strip_manifest_links(_msg), error_message="")
            try:
                from core.reply_sender import send_reply_ex
                send_reply_ex(chat_id=str(chat_id), text=_ff13c_strip_manifest_links(_msg), reply_to_message_id=reply_to)
            except Exception:
                pass
            try:
                conn.execute("INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))", (task_id, "FULLFIX_13B_FALSE_PROJECT_GUARDED"))
                conn.commit()
            except Exception:
                pass
            return
    except Exception as _ff13b_guard_err:
        try:
            logger.error("FULLFIX_13B_FALSE_PROJECT_GUARD_ERROR task=%s err=%s", task_id, str(_ff13b_guard_err))
        except Exception:
            pass
    # === END FULLFIX_13B_FALSE_PROJECT_PHRASE_GUARD ===

    # === FULLFIX_10_TOTAL_CLOSURE_UNIVERSAL_ROUTE ===
    try:
        from core.orchestra_closure_engine import (
            classify_user_task as _ff10_classify_user_task,
            classify_project_kind as _ff10_classify_project_kind,
            create_estimate_files as _ff10_create_estimate_files,
            save_result_memory as _ff10_save_result_memory,
            ENGINE as _FF10_ENGINE,
        )

        _ff10_intent = _ff10_classify_user_task(str(raw_input or ""))


        # === FULLFIX_13B_CLEAN_ESTIMATE_MESSAGE_BEFORE_SEND_FALLBACK ===
        def _ff13b_clean_any_estimate_text(_txt):
            try:
                from core.orchestra_closure_engine import ff13b_clean_estimate_user_message
                return ff13b_clean_estimate_user_message(_txt)
            except Exception:
                return _txt
        # === END FULLFIX_13B_CLEAN_ESTIMATE_MESSAGE_BEFORE_SEND_FALLBACK ===

        if _ff10_intent in ("confirm", "revision"):
            _ff10_parent = conn.execute(
                """
                SELECT id,state,result,reply_to_message_id,bot_message_id
                FROM tasks
                WHERE chat_id=?
                  AND COALESCE(topic_id,0)=?
                  AND state='AWAITING_CONFIRMATION'
                  AND id<>?
                ORDER BY updated_at DESC, created_at DESC
                LIMIT 1
                """,
                (str(chat_id), int(topic_id or 0), task_id),
            ).fetchone()

            if _ff10_parent and _ff10_intent == "confirm":
                _parent_id = _s(_ff10_parent["id"])
                _update_task(conn, _parent_id, state="DONE", error_message="")
                _history(conn, _parent_id, "FULLFIX_10_CONFIRM_DONE")
                _update_task(conn, task_id, state="DONE", result="Подтверждение принято. Задача закрыта", error_message="")
                _history(conn, task_id, "FULLFIX_10_CONFIRM_CHILD_DONE")
                conn.commit()
                _send_once(conn, task_id, chat_id, "Подтверждение принято. Задача закрыта", reply_to, "ff10_confirm_done")
                return

            if _ff10_parent and _ff10_intent == "revision":
                _parent_id = _s(_ff10_parent["id"])
                _merged = _clean(_s(_ff10_parent["result"]) + "\n\nПравки пользователя:\n" + str(raw_input or ""), 12000)
                _update_task(conn, _parent_id, state="IN_PROGRESS", raw_input=_merged, error_message="")
                _history(conn, _parent_id, "FULLFIX_10_REVISION_REOPEN")
                _update_task(conn, task_id, state="DONE", result="Правки приняты. Задача возвращена в работу", error_message="")
                _history(conn, task_id, "FULLFIX_10_REVISION_CHILD_DONE")
                conn.commit()
                _send_once(conn, task_id, chat_id, "Правки приняты. Задача возвращена в работу", reply_to, "ff10_revision_reopen")
                return

        if _ff10_intent == "project":
            _kind, _section = _ff10_classify_project_kind(str(raw_input or ""))
            if _kind == "foundation_slab":
                from core.project_engine import create_project_pdf_dxf_artifact
                _ff10_res = await create_project_pdf_dxf_artifact(str(raw_input or ""), task_id, int(topic_id or 0), "FULLFIX_10_SIMPLE_USER_REQUEST", True)

                if not isinstance(_ff10_res, dict) or not _ff10_res.get("success"):
                    _err = str((_ff10_res or {}).get("error", "PROJECT_FAILED"))[:400]
                    _msg = "Проект не создан: " + _err
                    _update_task(conn, task_id, state="FAILED", result=_ff13c_strip_manifest_links(_msg), error_message=_err)
                    _history(conn, task_id, "FULLFIX_10_PROJECT_FAILED:" + _err)
                    conn.commit()
                    _send_once(conn, task_id, chat_id, _msg, reply_to, "ff10_project_failed")
                    return

                _pdf = str(_ff10_res.get("pdf_link") or "")
                _dxf = str(_ff10_res.get("dxf_link") or "")
                _xlsx = str(_ff10_res.get("xlsx_link") or "")
                _manifest = str(_ff10_res.get("manifest_link") or "")
                _sheet_count = str(_ff10_res.get("sheet_count") or "")
                _engine = str(_ff10_res.get("engine") or _FF10_ENGINE)
                _msg = (
                    "Проект создан\n"
                    f"Engine: {_engine}\n"
                    "Раздел: КЖ\n"
                    f"Тип: фундаментная плита\n"
                    f"Листов: {_sheet_count}\n"
                    f"PDF: {_pdf}\n"
                    f"DXF: {_dxf}\n"
                    f"XLSX: {_xlsx}\n"
                    f"MANIFEST: {_manifest}\n\n"
                    "Доволен результатом? Ответь: Да / Уточни / Правки"
                )
                if not _pdf or not _dxf:
                    _update_task(conn, task_id, state="FAILED", result="Проект не создан: нет PDF/DXF ссылки", error_message="PROJECT_LINKS_MISSING")
                    _history(conn, task_id, "FULLFIX_10_PROJECT_LINKS_MISSING")
                    conn.commit()
                    _send_once(conn, task_id, chat_id, "Проект не создан: нет PDF/DXF ссылки", reply_to, "ff10_project_links_missing")
                    return

                _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(_msg), error_message="")
                _history(conn, task_id, "FULLFIX_10_PROJECT_OK")
                conn.commit()
                _sent = _send_once_ex(conn, task_id, str(chat_id), _msg, reply_to, "ff10_project_result")
                if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                    _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                    conn.commit()
                _ff10_save_result_memory(str(chat_id), int(topic_id or 0), str(raw_input or ""), _msg, _ff10_res)
                return

        if _ff10_intent == "estimate":
            _ff10_res = _ff10_create_estimate_files(str(raw_input or ""), task_id, int(topic_id or 0))
            if not isinstance(_ff10_res, dict) or not _ff10_res.get("success"):
                _err = str((_ff10_res or {}).get("error", "ESTIMATE_FAILED"))[:400]
                _msg = "Смета не создана: " + _err
                _update_task(conn, task_id, state="FAILED", result=_ff13c_strip_manifest_links(_msg), error_message=_err)
                _history(conn, task_id, "FULLFIX_10_ESTIMATE_FAILED:" + _err)
                conn.commit()
                _send_once(conn, task_id, chat_id, _msg, reply_to, "ff10_estimate_failed")
                return

            _msg = str(_ff10_res.get("message") or "")
            _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(_msg), error_message="")
            _history(conn, task_id, "FULLFIX_10_ESTIMATE_OK")
            conn.commit()
            _sent = _send_once_ex(conn, task_id, str(chat_id), _msg, reply_to, "ff10_estimate_result")
            if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                conn.commit()
            _ff10_save_result_memory(str(chat_id), int(topic_id or 0), str(raw_input or ""), _msg, _ff10_res)
            return

    except Exception as _ff10_e:
        _err = str(_ff10_e)[:500]
        _update_task(conn, task_id, state="FAILED", result="Ошибка FULLFIX_10: " + _err, error_message=_err)
        _history(conn, task_id, "FULLFIX_10_EXCEPTION:" + _err)
        conn.commit()
        _send_once(conn, task_id, chat_id, "Ошибка FULLFIX_10: " + _err, reply_to, "ff10_exception")
        return
    # === END FULLFIX_10_TOTAL_CLOSURE_UNIVERSAL_ROUTE ===

    # === FULLFIX_07_PROJECT_DESIGN_CLOSURE_ROUTE ===
    _ff07_low = str(raw_input or "").lower()
    _ff07_triggers = (
        "создай проект",
        "сделай проект",
        "проект фундамент",
        "проект фундаментной плиты",
        "план фундамент",
        "план фундаментной плиты",
        "фундаментной плиты",
        "проект по образцу",
        "по образцу проект",
        "проект по шаблону",
        "dxf проект",
        "dwg проект",
    )
    if any(x in _ff07_low for x in _ff07_triggers):
        try:
            from core.project_engine import create_project_pdf_dxf_artifact
            _ff07_res = await create_project_pdf_dxf_artifact(str(raw_input), task_id, int(topic_id or 0), "", True)

            if not isinstance(_ff07_res, dict) or not _ff07_res.get("success"):
                _err = str((_ff07_res or {}).get("error", "PROJECT_FAILED"))[:500]
                _update_task(
                    conn,
                    task_id,
                    state="FAILED",
                    result="Проект не создан: нет полного комплекта PDF/DXF/XLSX/MANIFEST или шаблон неполный",
                    error_message=_err,
                )
                _history(conn, task_id, "FULLFIX_07_FAILED:" + _err)
                conn.commit()
                _send_once(
                    conn,
                    task_id,
                    chat_id,
                    "Проект не создан: нет полного комплекта PDF/DXF/XLSX/MANIFEST или шаблон неполный",
                    reply_to,
                    "project_failed",
                )
                return

            _pdf = str(_ff07_res.get("pdf_link") or "")
            _dxf = str(_ff07_res.get("dxf_link") or "")
            _xlsx = str(_ff07_res.get("xlsx_link") or "")
            _manifest = str(_ff07_res.get("manifest_link") or "")
            _engine = str(_ff07_res.get("engine") or "FULLFIX_07_PROJECT_DESIGN_CLOSURE")
            _tpl = str(_ff07_res.get("template_file") or "")
            _sheet_count = str(_ff07_res.get("sheet_count") or "0")
            _sec = str(_ff07_res.get("section") or "КЖ")

            _msg = (
                "Проект создан\n"
                f"Engine: {_engine}\n"
                f"Раздел: {_sec}\n"
                f"Листов: {_sheet_count}\n"
                f"Шаблон: {_tpl}\n"
                f"PDF: {_pdf}\n"
                f"DXF: {_dxf}\n"
                f"XLSX: {_xlsx}\n"
                f"MANIFEST: {_manifest}\n\n"
                "Доволен результатом? Ответь: Да / Уточни / Правки"
            )

            _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(_msg), error_message="")
            _history(conn, task_id, "FULLFIX_07_PROJECT_OK")
            conn.commit()

            try:
                _sent = _send_once_ex(conn, task_id, str(chat_id), _msg, reply_to, "project_fullfix_07_result")
                if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                    _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                    conn.commit()
            except Exception:
                _send_once(conn, task_id, chat_id, _msg, reply_to, "project_fullfix_07_result")
            return

        except Exception as _ff07_e:
            _err = str(_ff07_e)[:700]
            _update_task(
                conn,
                task_id,
                state="FAILED",
                result="Проект не создан: ошибка генерации полного комплекта: " + _err,
                error_message=_err,
            )
            _history(conn, task_id, "FULLFIX_07_EXCEPTION:" + _err)
            conn.commit()
            _send_once(conn, task_id, chat_id, "Проект не создан: ошибка генерации полного комплекта: " + _err, reply_to, "project_exception")
            return
    # === END FULLFIX_07_PROJECT_DESIGN_CLOSURE_ROUTE ===


    # === FULLFIX_07_CAD_PROJECT_DOCUMENTATION_ROUTE ===
    try:
        from core.cad_project_engine import is_project_design_request, create_full_project_package, format_project_result_message
        if is_project_design_request(raw_input):
            _ff07_res = create_full_project_package(str(raw_input), task_id, int(topic_id or 0), "")
            _ff07_msg = format_project_result_message(_ff07_res)
            if not isinstance(_ff07_res, dict) or not _ff07_res.get("success"):
                _err = str((_ff07_res or {}).get("error") or "PROJECT_DOCUMENTATION_FAILED")[:300]
                _update_task(conn, task_id, state="FAILED", result=_ff07_msg, error_message=_err)
                _history(conn, task_id, "FULLFIX_07_PROJECT_FAILED:" + _err)
                conn.commit()
                _send_once(conn, task_id, chat_id, _ff07_msg, reply_to, "ff07_project_failed")
                return

            _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff07_msg, error_message="")
            _history(conn, task_id, "FULLFIX_07_PROJECT_OK")
            conn.commit()
            _sent = _send_once_ex(conn, task_id, str(chat_id), _ff07_msg, reply_to, "ff07_project_result")
            if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                conn.commit()
            return
    except Exception as _ff07_e:
        _err = str(_ff07_e)[:500]
        _update_task(conn, task_id, state="FAILED", result="Проект не создан: ошибка FULLFIX_07", error_message=_err)
        _history(conn, task_id, "FULLFIX_07_EXCEPTION:" + _err)
        conn.commit()
        _send_once(conn, task_id, chat_id, "Проект не создан: ошибка FULLFIX_07", reply_to, "ff07_project_exception")
        return
    # === END FULLFIX_07_CAD_PROJECT_DOCUMENTATION_ROUTE ===

    # === FULLFIX_06_FINAL_PROJECT_TEMPLATE_ROUTE ===
    _ff06_low = str(raw_input or "").lower()
    _ff06_project_triggers = (
        "создай проект",
        "сделай проект",
        "разработай проект",
        "готовый проект",
        "проект фундамент",
        "проект фундаментной плиты",
        "проект кровли",
        "проект по образцу",
        "проект по шаблону",
        "план фундаментной плиты",
        "чертеж фундаментной плиты",
        "чертёж фундаментной плиты",
    )
    if any(x in _ff06_low for x in _ff06_project_triggers):
        try:
            from core.project_engine import create_project_pdf_dxf_artifact
            _ff06_res = await create_project_pdf_dxf_artifact(str(raw_input), task_id, int(topic_id or 0), "", True)
            if not isinstance(_ff06_res, dict) or not _ff06_res.get("success"):
                _err = str((_ff06_res or {}).get("error", "PROJECT_FAILED"))[:300]
                _update_task(conn, task_id, state="FAILED", result="Проект не создан: нет сохранённого шаблона или не созданы PDF/DXF/XLSX ссылки", error_message=_err)
                _history(conn, task_id, "FULLFIX_06_PROJECT_FAILED:" + _err)
                conn.commit()
                _send_once(conn, task_id, chat_id, "Проект не создан: нет сохранённого шаблона или не созданы PDF/DXF/XLSX ссылки", reply_to, "project_failed_ff06")
                return

            _msg = (
                "Проект создан по сохранённому шаблону\n"
                f"Раздел: {_ff06_res.get('section')}\n"
                f"Листов по шаблону: {_ff06_res.get('sheet_count')}\n"
                f"Шаблон: {_ff06_res.get('template_file')}\n"
                f"PDF: {_ff06_res.get('pdf_link')}\n"
                f"DXF: {_ff06_res.get('dxf_link')}\n"
                f"XLSX: {_ff06_res.get('xlsx_link')}\n"
                f"MANIFEST: {_ff06_res.get('manifest_link')}\n\n"
                "Доволен результатом? Ответь: Да / Уточни / Правки"
            )
            _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(_msg), error_message="")
            _history(conn, task_id, "FULLFIX_06_PROJECT_OK")
            conn.commit()
            _sent = _send_once_ex(conn, task_id, str(chat_id), _msg, reply_to, "project_result_ff06")
            if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                conn.commit()
            return
        except Exception as _ff06_e:
            _err = str(_ff06_e)[:500]
            _update_task(conn, task_id, state="FAILED", result="Проект не создан: ошибка генерации PDF/DXF/XLSX", error_message=_err)
            _history(conn, task_id, "FULLFIX_06_PROJECT_EXCEPTION:" + _err)
            conn.commit()
            _send_once(conn, task_id, chat_id, "Проект не создан: ошибка генерации PDF/DXF/XLSX", reply_to, "project_exception_ff06")
            return
    # === END FULLFIX_06_FINAL_PROJECT_TEMPLATE_ROUTE ===


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

    # === FULLFIX_05_REQUIRE_REAL_PDF_DXF_PROJECT ===
    _ff05_low = str(raw_input or "").lower()
    _ff05_project_triggers = (
        "создай проект",
        "сделай проект",
        "проект фундамент",
        "проект фундаментной плиты",
        "план фундамент",
        "план фундаментной плиты",
        "фундаментной плиты",
        "проект по образцу",
        "проект по шаблону",
        "сделай по образцу",
    )
    if any(x in _ff05_low for x in _ff05_project_triggers):
        try:
            from core.project_engine import create_project_pdf_dxf_artifact
            _ff05_res = await create_project_pdf_dxf_artifact(str(raw_input), task_id, int(topic_id or 0), "")
            if not isinstance(_ff05_res, dict) or not _ff05_res.get("success"):
                _err = str((_ff05_res or {}).get("error", "PROJECT_FAILED"))[:300]
                _update_task(
                    conn,
                    task_id,
                    state="FAILED",
                    result="Проект не создан: нет PDF/DXF файла или ссылки",
                    error_message=_err,
                )
                _history(conn, task_id, "FULLFIX_05_PROJECT_FAILED:" + _err)
                conn.commit()
                _send_once(
                    conn,
                    task_id,
                    chat_id,
                    "Проект не создан: нет PDF/DXF файла или ссылки",
                    reply_to,
                    "project_failed",
                )
                return

            _pdf = str(_ff05_res.get("pdf_link") or "")
            _dxf = str(_ff05_res.get("dxf_link") or "")
            _manifest = str(_ff05_res.get("manifest_link") or "")
            _sec = str(_ff05_res.get("section") or "КЖ")
            _msg = (
                f"Проект создан как PDF/DXF комплект\n"
                f"Раздел: {_sec}\n"
                f"PDF: {_pdf}\n"
                f"DXF: {_dxf}\n"
            )
            if _manifest:
                _msg += f"MANIFEST: {_manifest}\n"
            _msg += "\nДоволен результатом? Ответь: Да / Уточни / Правки"

            _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(_msg), error_message="")
            _history(conn, task_id, "FULLFIX_05_PROJECT_PDF_DXF_OK")
            conn.commit()

            _sent = _send_once_ex(conn, task_id, str(chat_id), _msg, reply_to, "project_pdf_dxf_result")
            if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                conn.commit()
            return

        except Exception as _ff05_e:
            _err = str(_ff05_e)[:500]
            _update_task(
                conn,
                task_id,
                state="FAILED",
                result="Проект не создан: ошибка генерации PDF/DXF",
                error_message=_err,
            )
            _history(conn, task_id, "FULLFIX_05_PROJECT_EXCEPTION:" + _err)
            conn.commit()
            _send_once(conn, task_id, chat_id, "Проект не создан: ошибка генерации PDF/DXF", reply_to, "project_exception")
            return
    # === END FULLFIX_05_REQUIRE_REAL_PDF_DXF_PROJECT ===

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



def _get_parent_task_id(conn, chat_id, reply_to_message_id, topic_id):
    if not reply_to_message_id:
        return None
    row = conn.execute("""
        SELECT id FROM tasks
        WHERE chat_id = ? AND topic_id = ?
          AND (bot_message_id = ? OR reply_to_message_id = ?)
          AND state IN ('NEW', 'IN_PROGRESS', 'WAITING_CLARIFICATION', 'AWAITING_CONFIRMATION')
        ORDER BY updated_at DESC
        LIMIT 1
    """, (str(chat_id), int(topic_id), reply_to_message_id, reply_to_message_id)).fetchone()
    return row["id"] if row else None

def _normalize_voice_text(text: str) -> str:
    return _clean(_s(text).replace("[VOICE]", " "), 12000)

def _looks_done_command(text: str) -> bool:
    low = _normalize_voice_text(text).lower()
    if "не доволен" in low or "недоволен" in low:
        return False
    done_markers = [
        "да доволен",
        "доволен результатом",
        "можно завершать",
        "можно закрывать",
        "завершай задачу",
        "завершай запрос",
        "завершай поиск",
        "задача завершена",
        "задача закрыта",
        "запрос завершен",
        "поиск завершен",
        "все верно завершай",
        "всё верно завершай",
        "все верно задача завершена",
        "всё верно задача завершена",
        "да все верно",
        "да всё верно",
        "я же тебе сказал задача завершена",
        "я же тебе сказал завершай",
        "да можно",
    ]
    return any(m in low for m in done_markers)

def _extract_topic_role(text: str) -> str:
    raw = _clean(_s(text), 1000)
    if not raw:
        return ""

    patterns = [
        r"чат закреплен за темами:\s*(.+?)(?:\.|$)",
        r"чат закреплён за темами:\s*(.+?)(?:\.|$)",
        r"чат закреплен за:\s*(.+?)(?:\.|$)",
        r"чат закреплён за:\s*(.+?)(?:\.|$)",
        r"закрепленные темы:\s*(.+?)(?:\.|$)",
        r"закреплённые темы:\s*(.+?)(?:\.|$)",
        r"закреплено:\s*чат для\s*(.+?)(?:\.|$)",
        r"этот чат используется для\s*(.+?)(?:\.|$)",
        r"этот чат предназначен для\s*(.+?)(?:\.|$)",
    ]

    bad_markers = [
        "без контекста",
        "не понимаю запрос",
        "не помню",
        "задача завершена",
        "задача закрыта",
        "подтверждение принято",
        "готов к выполнению задачи",
        "последние действия",
        "в этом чате были следующие действия",
        "текущий статус",
        "последний запрос",
        "какие последние",
        "чем помочь",
    ]

    for pattern in patterns:
        m = re.search(pattern, raw, re.I | re.S)
        if not m:
            continue

        role = re.sub(r"\s+", " ", m.group(1)).strip(" .:-")
        role = re.split(r"\b(чем помочь|готов к работе|готов обсудить|последний запрос)\b", role, flags=re.I)[0].strip(" .:-")
        low = role.lower()

        if not role or len(role) < 3:
            continue
        if "?" in role:
            continue
        if any(x in low for x in bad_markers):
            continue

        return role[:500]

    return ""

def _save_topic_role_memory(chat_id: str, topic_id: int, text: str) -> str:
    role = _extract_topic_role(text)
    if not role or not os.path.exists(MEM_DB):
        return ""
    conn_mem = db(MEM_DB)
    try:
        if not _has_table(conn_mem, "memory"):
            return ""
        key = f"topic_{int(topic_id)}_role"
        conn_mem.execute(
            "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(chat_id), key, role),
        )
        conn_mem.commit()
        return role
    except Exception:
        return ""
    finally:
        conn_mem.close()

def _find_awaiting_confirmation_task(conn: sqlite3.Connection, chat_id: str, topic_id: int, current_task_id: str, reply_to_message_id: Any) -> Optional[sqlite3.Row]:
    if reply_to_message_id:
        row = conn.execute(
            """
            SELECT id, result
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND state='AWAITING_CONFIRMATION'
              AND id<>?
              AND (bot_message_id=? OR reply_to_message_id=?)
            ORDER BY updated_at DESC, created_at DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id), str(current_task_id), reply_to_message_id, reply_to_message_id),
        ).fetchone()
        if row:
            return row

    return conn.execute(
        """
        SELECT id, result
        FROM tasks
        WHERE chat_id=?
          AND COALESCE(topic_id,0)=?
          AND state='AWAITING_CONFIRMATION'
          AND id<>?
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id), str(current_task_id)),
    ).fetchone()

async def _handle_in_progress(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> None:
    task_id = _s(_task_field(task, "id"))
    raw_input = _clean(_s(_task_field(task, "raw_input")), 12000)
    reply_to = _task_field(task, "reply_to_message_id", None)

    if _looks_done_command(raw_input):
        target = _find_awaiting_confirmation_task(conn, chat_id, topic_id, task_id, reply_to)
        if target:
            target_id = _s(target["id"])
            target_result = _s(target["result"])
            saved_role = _save_topic_role_memory(chat_id, topic_id, target_result)
            _update_task(conn, target_id, state="DONE", error_message="")
            _history(conn, target_id, "state:DONE")
            if saved_role:
                _history(conn, target_id, f"ROLE_SAVED:{_clean(saved_role, 200)}")
            _update_task(conn, task_id, state="DONE", result="Подтверждение принято", error_message="")
            _history(conn, task_id, "state:DONE")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Принял. Задача закрыта", reply_to, "confirm_done")
            return

    parent_task_id = _get_parent_task_id(conn, chat_id, task["reply_to_message_id"], topic_id)
    active_source_id = parent_task_id or task_id
    active_task_context = _active_unfinished_context(conn, chat_id, topic_id, active_source_id)
    pin_context = get_pin_context(chat_id, raw_input, topic_id)
    short_memory, long_memory, topic_role, topic_directions = _load_memory_context(chat_id, topic_id)
    archive_context = _load_archive_context(chat_id, topic_id, raw_input)
    search_context = _search_fact_context(conn, chat_id, topic_id)

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
        "search_context": search_context,
        "topic_role": topic_role,
        "topic_directions": topic_directions,
    }

    try:
        assigned_role = _detect_role_assignment(raw_input)
        if assigned_role:
            _save_topic_role(chat_id, topic_id, assigned_role)
            _history(conn, task_id, f"ROLE_SAVED:{_clean(assigned_role, 200)}")
            conn.commit()
            ai_result = f"Принято. Чат закреплен за темами: {assigned_role}. Все связанные запросы будут обрабатываться здесь."
        else:
            ROLE_Q = re.compile(r"(для чего|о чём|о чем|про что|напомни.*(чат|топик)|чем занимается|зачем этот чат)", re.IGNORECASE)
            HISTORY_Q = re.compile(r"(что мы писали|что писали раньше|о ч[её]м общались|напомни.*что.*(писали|обсуждали)|что было в этом чате|история чата)", re.IGNORECASE)
            if topic_role and (ROLE_Q.search(raw_input) or HISTORY_Q.search(raw_input)):
                ai_result = f"Этот чат закреплён за: {topic_role}"
            else:
                ai_result = await asyncio.wait_for(process_ai_task(payload), timeout=AI_TIMEOUT)
    except Exception as e:
        _update_task(conn, task_id, state="FAILED", error_message=_clean(str(e), 500))
        _close_pin(conn, task_id)
        _history(conn, task_id, "state:FAILED")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Задача не выполнена. Уточни или повтори запрос", reply_to, "router_failed")
        return

    ai_result = _clean(_s(ai_result), 50000)
    # === FOLLOWUP DETECTION (FACT-BASED) ===
    low_input = raw_input.lower()

    memory_markers = [
        "напомни","что обсуждали","что делали","какие задачи","история",
        "что было","что писали","для чего этот чат","о чем чат","о чём чат"
    ]

    search_markers = [
        "нерелевант","битые","ссылки не те","проверь","еще раз","ещё раз",
        "сделай еще","сделай ещё","найди еще","найди ещё","это не то"
    ]

    has_memory_context = any([
        short_memory,
        long_memory,
        topic_role,
        active_task_context,
        pin_context,
        archive_context,
    ])

    raw_input = _clean(_s(_task_field(task, "raw_input")), 12000)
    low_input = raw_input.lower()

    memory_markers = [
        "напомни",
        "что обсуждали",
        "что делали",
        "какие задачи",
        "история",
        "что было в этом чате",
        "что писали",
        "для чего этот чат",
        "о чем чат",
        "о чём чат",
    ]
    is_memory_followup = has_memory_context and any(m in low_input for m in memory_markers)

    search_markers = [
        "нерелевант",
        "битые ссылки",
        "живые ссылки",
        "ссылки не те",
        "проверь еще",
        "проверь ещё",
        "еще раз поиск",
        "ещё раз поиск",
        "сделай еще раз поиск",
        "сделай ещё раз поиск",
        "найди еще",
        "найди ещё",
        "это не то",
        "ссылки биты",
        "ссылки битые",
    ]
    is_search_followup = bool(search_context) and any(m in low_input for m in search_markers)

    if is_search_followup and search_context:
        forbidden_search_advice = [
            "dr.web",
            "link checker",
            "яндекс safety",
            "google safe browsing",
            "virustotal",
            "для проверки безопасности ссылок используйте",
        ]
        if any(m in ai_result.lower() for m in forbidden_search_advice):
            ai_result = _clean(f"Повторяю поиск по последнему запросу\n\n{search_context}", 50000)

    if is_memory_followup or is_search_followup:
        if not ai_result or len(ai_result) < MIN_RESULT_LEN:
            _update_task(conn, task_id, state="FAILED", error_message="INVALID_RESULT_GATE")
            _close_pin(conn, task_id)
            _history(conn, task_id, "state:FAILED")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Не понял запрос. Уточни что нужно сделать", reply_to, "invalid_result")
            return
    else:
        if not _is_valid_result(ai_result, raw_input):
            _update_task(conn, task_id, state="FAILED", error_message="INVALID_RESULT_GATE")
            _close_pin(conn, task_id)
            _history(conn, task_id, "state:FAILED")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Не понял запрос. Уточни что нужно сделать", reply_to, "invalid_result")
            return

    low_result = ai_result.lower()
    done_markers = [
        "задача завершена",
        "задача закрыта",
        "задачи завершены",
        "подтверждение принято",
        "поиск завершен",
        "поиск завершён",
    ]
    junk_markers = [
        "без контекста",
        "задайте конкретный вопрос",
        "конкретный вопрос по",
        "нет, не помню",
        "не понимаю запрос",
        "готов к выполнению задачи",
    ]
    info_markers = [
        "для чего этот чат",
        "что мы здесь обсуждаем",
        "что в данном чате",
        "какой последний запрос",
        "последний запрос",
        "какие последние запросы",
        "что мы тут делаем",
        "что мы здесь делаем",
        "о чем чат",
        "о чём чат",
    ]
    file_success_markers = [
        "документ обработан",
        "артефакт:",
        "нормализовано позиций",
        "обработаны документы",
    ]
    file_bad_markers = [
        "скачан, ожидает анализа",
        "создан локально, но загрузка в drive завершилась ошибкой",
        "ожидает анализа",
        "загрузка в drive завершилась ошибкой",
    ]

    if any(m in low_result for m in done_markers):
        _update_task(conn, task_id, state="DONE", result=ai_result, error_message="")
        _close_pin(conn, task_id)
        _history(conn, task_id, f"result:{_clean(ai_result, 400)}")
        conn.commit()
        _send_once(conn, task_id, chat_id, ai_result, reply_to, "done_terminal")
        return

    if any(m in low_result for m in junk_markers):
        _update_task(conn, task_id, state="WAITING_CLARIFICATION", result=ai_result, error_message="")
        _close_pin(conn, task_id)
        _history(conn, task_id, f"clarify:{_clean(ai_result, 400)}")
        conn.commit()
        _send_once(conn, task_id, chat_id, ai_result, reply_to, "clarify_terminal")
        return

    is_info_query = any(m in low_input for m in info_markers)
    is_file_success = any(m in low_result for m in file_success_markers) and not any(m in low_result for m in file_bad_markers)

    if is_memory_followup or is_search_followup or is_info_query or is_file_success:
        _update_task(conn, task_id, state="DONE", result=ai_result, error_message="")
        _history(conn, task_id, f"result:{_clean(ai_result, 400)}")
        conn.commit()
        try:
            save_pin(chat_id, task_id, ai_result, topic_id)
        except Exception:
            pass
        _send_once(conn, task_id, chat_id, ai_result, reply_to, "done_terminal")
        return

    should_save_role = (
        bool(re.search(
            r"(чат закреплен за темами:|чат закреплён за темами:|чат закреплен за:|чат закреплён за:|закрепленные темы:|закреплённые темы:|закреплено:\s*чат для|этот чат используется для|этот чат предназначен для)",
            ai_result,
            re.I,
        ))
        and not any(x in low_result for x in junk_markers)
        and "последние действия" not in low_result
        and "текущий статус" not in low_result
    )

    saved_role = ""
    if should_save_role:
        saved_role = _save_topic_role_memory(chat_id, topic_id, ai_result)
    _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=ai_result, error_message="")
    _history(conn, task_id, f"result:{_clean(ai_result, 400)}")
    if saved_role:
        _history(conn, task_id, f"ROLE_SAVED:{_clean(saved_role, 200)}")

    try:
        save_pin(chat_id, task_id, ai_result, topic_id)
    except Exception as e:
        logger.warning("save_pin_fail task=%s err=%s", task_id, e)

    _ai_result_clean = str(ai_result or "").replace("\n\nДоволен результатом? Ответь: Да / Уточни / Правки", "").strip()  # FF21_FIX_DOUBLE_DOVOLEN
    confirmation_text = f"{_ai_result_clean}\n\nДоволен результатом? Ответь: Да / Уточни / Правки"
    sent = _send_once_ex(conn, task_id, chat_id, confirmation_text, reply_to, "result")
    bot_message_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
    if bot_message_id is not None:
        _update_task(conn, task_id, bot_message_id=bot_message_id)
    conn.commit()


def _pick_next_task(conn: sqlite3.Connection, chat_id: Optional[str]) -> Optional[sqlite3.Row]:
    where = ["state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION')"]
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
                    logger.error("DRIVE_FILE CRASH task=%s err=%s", task_id, str(e))
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

async def _handle_drive_file(conn, task, chat_id, topic_id):
    import json, os
    task_id = task["id"]
    raw_input = task["raw_input"]
    try:
        data = json.loads(raw_input)
        file_id = data["file_id"]
        file_name = data["file_name"]
    except Exception as e:
        logger.error(f"DRIVE_FILE: invalid raw_input for {task_id}: {e}")
        _update_task(conn, task_id, state="FAILED", error_message="invalid raw_input")
        return

    local_path = f"/root/.areal-neva-core/runtime/drive_files/{task_id}_{file_name}"
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    logger.info(f"DRIVE_FILE: downloading {file_id} -> {local_path}")
    ok = _download_from_drive(file_id, local_path)
    if not ok:
        _update_task(conn, task_id, state="FAILED", error_message="download failed")
        return

    conn.execute("UPDATE drive_files SET stage='downloaded' WHERE task_id=?", (task_id,))

    result = f"Файл {file_name} скачан, ожидает анализа"
    try:
        _, _, topic_role, _ = _load_memory_context(chat_id, topic_id)
        analysis = await analyze_downloaded_file(
            local_path=local_path,
            file_name=file_name,
            mime_type=data.get("mime_type", ""),
            user_text=data.get("caption", ""),
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
                        # === PATCH: save_pin + save_memory + log ===
                        try:
                            save_pin(chat_id, task_id, result, topic_id)
                            _save_memory(chat_id, topic_id, raw_input, result)
                            logger.info(f"DRIVE_FILE pin_memory_saved task_id={task_id}")
                        except Exception as e:
                            logger.error(f"DRIVE_FILE pin/memory failed task={task_id} err={e}")
                        # === END PATCH ===
                    else:
                        result = summary + "\n\nАртефакт создан, но загрузка в Drive не подтвердилась"
                except Exception as e:
                    logger.error(f"DRIVE_FILE artifact upload failed task={task_id} err={e}")
                    result = summary + "\n\nАртефакт создан локально, но загрузка в Drive завершилась ошибкой"
    except Exception as e:
        logger.error(f"DRIVE_FILE analyze skipped task={task_id} err={e}")

    _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(result))
    logger.info(f"DRIVE_FILE: {task_id} processed")

if __name__ == "__main__":
    asyncio.run(main())

# === FULLFIX_08_PROJECT_ERROR_VISIBILITY ===
