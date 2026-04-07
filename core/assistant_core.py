from __future__ import annotations

import logging
import os
import sqlite3
import time
from typing import Optional

logger = logging.getLogger("core.assistant_core")
DB_PATH = os.getenv("ORCHESTRA_DB_PATH", "/root/.areal-neva-core/data/core.db")


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ")


def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


async def save_memory(chat_id: int, text: str, role: str = "user", topic_id: Optional[int] = None) -> None:
    text = (text or "").strip()
    if not text:
        return
    try:
        con = _conn()
        con.execute(
            "INSERT INTO memory_log (chat_id, topic_id, role, text, created_at) VALUES (?,?,?,?,?)",
            (chat_id, topic_id, role, text, _now_iso())
        )
        con.commit()
        con.close()
    except Exception:
        logger.exception("save_memory error chat_id=%s", chat_id)


async def search_memory(chat_id: int, query: str, topic_id: Optional[int] = None, limit: int = 5) -> list[str]:
    query = (query or "").strip()
    if not query:
        return []
    try:
        con = _conn()
        if topic_id is not None:
            cur = con.execute(
                "SELECT text FROM memory_log WHERE chat_id=? AND topic_id=? AND text LIKE ? ORDER BY id DESC LIMIT ?",
                (chat_id, topic_id, f"%{query}%", limit)
            )
        else:
            cur = con.execute(
                "SELECT text FROM memory_log WHERE chat_id=? AND text LIKE ? ORDER BY id DESC LIMIT ?",
                (chat_id, f"%{query}%", limit)
            )
        rows = cur.fetchall()
        con.close()
        return [r["text"] for r in rows]
    except Exception:
        logger.exception("search_memory error")
        return []


async def search_memory_global(query: str, limit: int = 5) -> list[dict]:
    query = (query or "").strip()
    if not query:
        return []
    try:
        con = _conn()
        cur = con.execute(
            "SELECT chat_id, topic_id, role, text, created_at FROM memory_log WHERE text LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{query}%", limit)
        )
        rows = cur.fetchall()
        con.close()
        return [dict(r) for r in rows]
    except Exception:
        logger.exception("search_memory_global error")
        return []


async def get_history(chat_id: int, topic_id: Optional[int] = None, limit: int = 20) -> list[dict]:
    try:
        con = _conn()
        if topic_id is not None:
            cur = con.execute(
                "SELECT role, text FROM memory_log WHERE chat_id=? AND topic_id=? ORDER BY id DESC LIMIT ?",
                (chat_id, topic_id, limit)
            )
        else:
            cur = con.execute(
                "SELECT role, text FROM memory_log WHERE chat_id=? ORDER BY id DESC LIMIT ?",
                (chat_id, limit)
            )
        rows = cur.fetchall()
        con.close()
        return [{"role": r["role"], "content": r["text"]} for r in reversed(rows)]
    except Exception:
        logger.exception("get_history error chat_id=%s", chat_id)
        return []


async def add_reminder(chat_id: int, text: str, topic_id: Optional[int] = None) -> None:
    text = (text or "").strip()
    if not text:
        return
    try:
        con = _conn()
        con.execute(
            "INSERT INTO reminders (chat_id, topic_id, text, done, created_at) VALUES (?,?,?,0,?)",
            (chat_id, topic_id, text, _now_iso())
        )
        con.commit()
        con.close()
    except Exception:
        logger.exception("add_reminder error chat_id=%s", chat_id)


async def get_pending_reminders() -> list[dict]:
    try:
        con = _conn()
        cur = con.execute("SELECT * FROM reminders WHERE done=0 ORDER BY id ASC")
        rows = cur.fetchall()
        con.close()
        return [dict(r) for r in rows]
    except Exception:
        logger.exception("get_pending_reminders error")
        return []


async def mark_reminder_done(reminder_id: int) -> None:
    try:
        con = _conn()
        con.execute("UPDATE reminders SET done=1 WHERE id=?", (reminder_id,))
        con.commit()
        con.close()
    except Exception:
        logger.exception("mark_reminder_done error id=%s", reminder_id)
