from __future__ import annotations
import json, os, sqlite3, threading
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "orchestra.db")
_LOCK = threading.Lock()

def _utc_now(): return datetime.now(timezone.utc).isoformat()
def _json_dumps(v): return json.dumps(v, ensure_ascii=False)
def _json_loads(v):
    if v is None: return None
    try: return json.loads(v)
    except: return v

@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        yield conn
    finally: conn.close()

def init_db():
    with _LOCK:
        with _conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT, route TEXT, status TEXT DEFAULT 'pending',
                    payload TEXT, result TEXT, error TEXT,
                    chat_id TEXT, msg_id TEXT, created_at TEXT, updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT, role TEXT, content TEXT, created_at TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mem_chat ON memory(chat_id)")

def create_task(payload, source="api", chat_id=None, msg_id=None):
    init_db()
    now = _utc_now()
    p_text = payload if isinstance(payload, str) else _json_dumps(payload)
    with _LOCK:
        with _conn() as conn:
            cur = conn.execute(
                "INSERT INTO tasks (source, status, payload, chat_id, msg_id, created_at, updated_at) VALUES (?, 'pending', ?, ?, ?, ?, ?)",
                (source, p_text, chat_id, msg_id, now, now)
            )
            return cur.lastrowid

def claim_pending_task():
    init_db()
    with _LOCK:
        with _conn() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE status = 'pending' ORDER BY id ASC LIMIT 1").fetchone()
            if not row: return None
            conn.execute("UPDATE tasks SET status = 'processing', updated_at = ? WHERE id = ?", (_utc_now(), row['id']))
            d = dict(row)
            d['payload'] = _json_loads(d['payload'])
            return d

def update_task_done(tid, res, route=None):
    now = _utc_now()
    r_text = res if isinstance(res, str) else _json_dumps(res)
    with _LOCK:
        with _conn() as conn:
            conn.execute("UPDATE tasks SET status = 'done', result = ?, route = ?, updated_at = ? WHERE id = ?", (r_text, route, now, tid))

def update_task_failed(tid, err, route=None):
    now = _utc_now()
    e_text = err if isinstance(err, str) else _json_dumps(err)
    with _LOCK:
        with _conn() as conn:
            conn.execute("UPDATE tasks SET status = 'failed', error = ?, route = ?, updated_at = ? WHERE id = ?", (e_text, route, now, tid))

def save_memory(chat_id, role, content):
    if not chat_id: return
    now = _utc_now()
    with _LOCK:
        with _conn() as conn:
            conn.execute("INSERT INTO memory (chat_id, role, content, created_at) VALUES (?, ?, ?, ?)", (str(chat_id), role, content, now))

def get_task(tid):
    with _conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (tid,)).fetchone()
        if not row: return None
        d = dict(row); d['payload'] = _json_loads(d['payload']); d['result'] = _json_loads(d['result'])
        return d
