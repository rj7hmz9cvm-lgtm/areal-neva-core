# === FINAL_CLOSURE_BLOCKER_FIX_V1_ARCHIVE_DUPLICATE_GUARD ===
from __future__ import annotations

import hashlib
import sqlite3
from typing import Any, Dict


def _clean(v) -> str:
    return "" if v is None else str(v).strip()


def content_hash(text: str) -> str:
    return hashlib.sha256(_clean(text).lower().encode("utf-8", "ignore")).hexdigest()


def ensure_archive_guard(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS archive_guard (
            id TEXT PRIMARY KEY,
            task_id TEXT,
            chat_id TEXT,
            topic_id INTEGER DEFAULT 0,
            content_hash TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_archive_guard_hash ON archive_guard(content_hash)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_archive_guard_task ON archive_guard(task_id)")


def should_archive(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, content: str) -> Dict[str, Any]:
    ensure_archive_guard(conn)
    h = content_hash(content)
    row = conn.execute("SELECT task_id, created_at FROM archive_guard WHERE content_hash=? LIMIT 1", (h,)).fetchone()

    if row:
        return {"ok": False, "duplicate": True, "duplicate_task_id": row[0], "hash": h}

    gid = hashlib.sha1(f"{task_id}:{h}".encode()).hexdigest()
    conn.execute(
        "INSERT OR IGNORE INTO archive_guard (id, task_id, chat_id, topic_id, content_hash) VALUES (?,?,?,?,?)",
        (gid, task_id, str(chat_id), int(topic_id or 0), h),
    )
    return {"ok": True, "duplicate": False, "hash": h}


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_ARCHIVE_DUPLICATE_GUARD ===
