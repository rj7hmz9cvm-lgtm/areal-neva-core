import re
import sqlite3

CORE_DB = "/root/.areal-neva-core/data/core.db"

def _conn():
    conn = sqlite3.connect(CORE_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def _has_table(conn, table: str) -> bool:
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
    return row is not None

def get_pin_context(chat_id: str, request_text: str = "", topic_id: int = 0) -> str:
    conn = _conn()
    try:
        if not _has_table(conn, "pin"):
            return ""

        row = conn.execute(
            "SELECT task_id FROM pin WHERE chat_id=? AND topic_id=? AND state='ACTIVE' ORDER BY rowid DESC LIMIT 1",
            (str(chat_id), int(topic_id))
        ).fetchone()

        if not row or not row["task_id"]:
            return ""

        task_row = conn.execute(
            "SELECT result FROM tasks WHERE id=? LIMIT 1",
            (row["task_id"],)
        ).fetchone()

        if task_row and task_row["result"]:
            pin_text = str(task_row["result"]).strip()
            if any(m in pin_text.lower() for m in PIN_MUTEX_MARKERS):
                return ""
            if request_text:
                request_words = set(re.findall(r"\w+", request_text.lower()))
                pin_words = set(re.findall(r"\w+", pin_text.lower()))
                if request_words & pin_words:
                    return pin_text[:4000]
                return ""
            return pin_text[:4000]

        return ""
    finally:
        conn.close()

PIN_MUTEX_MARKERS = ["задача отменена", "задача завершена", "не понимаю запрос", "готов к выполнению задачи"]

def save_pin(chat_id: str, task_id: str, result_text: str, topic_id: int = 0) -> bool:
    text = (result_text or "").strip()
    if not text:
        return False
    if any(m in text.lower() for m in PIN_MUTEX_MARKERS):
        return False  # PIN_STRICT_DONE_ONLY
        return False
    conn = _conn()
    try:
        if not _has_table(conn, "pin"):
            return False

        conn.execute(
            "UPDATE pin SET state='CLOSED', updated_at=datetime('now') WHERE chat_id=? AND topic_id=? AND state='ACTIVE'",
            (str(chat_id), int(topic_id))
        )
        conn.execute(
            "INSERT INTO pin (chat_id, task_id, topic_id, state, created_at, updated_at) VALUES (?, ?, ?, 'ACTIVE', datetime('now'), datetime('now'))",
            (str(chat_id), task_id, int(topic_id))
        )
        conn.commit()
        return True
    finally:
        conn.close()
