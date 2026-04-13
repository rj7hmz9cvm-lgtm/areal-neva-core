import sqlite3, os
from datetime import datetime, timezone

DB = "/root/.areal-neva-core/data/core.db"

def activate_pin(chat_id: str, task_id: str):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE pin SET state = 'CLOSED' WHERE chat_id = ?", (chat_id,))
    conn.execute(
        "INSERT INTO pin (chat_id, task_id, state, created_at, updated_at) VALUES (?, ?, 'ACTIVE', ?, ?)",
        (chat_id, task_id, datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()

def close_pin(chat_id: str):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE chat_id = ? AND state = 'ACTIVE'",
                 (datetime.now(timezone.utc).isoformat(), chat_id))
    conn.commit()
    conn.close()

def get_active_pin(chat_id: str) -> str:
    conn = sqlite3.connect(DB)
    cur = conn.execute("SELECT task_id FROM pin WHERE chat_id = ? AND state = 'ACTIVE'", (chat_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None
