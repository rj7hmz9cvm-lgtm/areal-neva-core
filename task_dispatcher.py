#!/usr/bin/env python3
import os
import time
import sqlite3
import socket
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = "/root/.areal-neva-core"
ENV_PATH = os.path.join(BASE_DIR, ".env")
DB_PATH = os.path.join(BASE_DIR, "runtime", "tasks.db")
LOG_PATH = os.path.join(BASE_DIR, "logs", "dispatcher.log")

load_dotenv(ENV_PATH)
ORCH_URL = os.getenv("ORCH_URL") or os.getenv("ORCHESTRA_URL") or "http://89.22.227.213:8080"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN") or ""
WORKER_ID = f"{socket.gethostname()}-{os.getpid()}"

Path(os.path.dirname(LOG_PATH)).mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("dispatcher")

def now_ts():
    return int(time.time())

def db():
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            message_id TEXT,
            text TEXT,
            status TEXT DEFAULT 'PENDING',
            result TEXT,
            error TEXT,
            worker_id TEXT,
            created_at INTEGER DEFAULT (strftime('%s','now')),
            updated_at INTEGER DEFAULT (strftime('%s','now'))
        )
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status_id ON tasks(status, id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)")

        cols = {row["name"] for row in con.execute("PRAGMA table_info(tasks)")}
        needed = {
            "chat_id": "TEXT",
            "message_id": "TEXT",
            "text": "TEXT",
            "status": "TEXT DEFAULT 'PENDING'",
            "result": "TEXT",
            "error": "TEXT",
            "worker_id": "TEXT",
            "created_at": "INTEGER DEFAULT (strftime('%s','now'))",
            "updated_at": "INTEGER DEFAULT (strftime('%s','now'))",
        }
        for name, decl in needed.items():
            if name not in cols:
                con.execute(f"ALTER TABLE tasks ADD COLUMN {name} {decl}")

        cols = {row["name"] for row in con.execute("PRAGMA table_info(tasks)")}
        if "reply_to_message_id" in cols and "message_id" in cols:
            con.execute("""
            UPDATE tasks
            SET message_id = reply_to_message_id
            WHERE (message_id IS NULL OR message_id = '')
              AND reply_to_message_id IS NOT NULL
              AND reply_to_message_id != ''
            """)

        con.commit()

def clean_result_text(result: str) -> str:
    text = (result or "").strip()
    bad_phrases = [
        "если вы можете уточнить",
        "если можете уточнить",
        "я предполагаю",
        "я постараюсь",
        "повторить задачу еще раз",
        "повторить ее еще раз",
        "повторить её ещё раз",
        "чтобы я мог понять ее лучше",
        "чтобы я мог понять её лучше",
    ]
    for bp in bad_phrases:
        text = text.replace(bp, "")
    while "  " in text:
        text = text.replace("  ", " ")
    return text.strip() or "(empty result)"

def send_tg(chat_id, text, reply_to=None):
    if not BOT_TOKEN or not chat_id:
        log.warning("TG_SKIP no token or chat_id")
        return False, "no token/chat_id"

    payload = {
        "chat_id": str(chat_id),
        "text": text[:4000] if text else "(empty result)",
    }
    if reply_to:
        try:
            payload["reply_to_message_id"] = int(reply_to)
        except Exception:
            pass

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json=payload, timeout=60)
        ok = r.status_code == 200
        if not ok:
            log.error("TG_SEND_FAIL code=%s body=%s", r.status_code, r.text[:1000])
        return ok, r.text[:1000]
    except Exception as e:
        log.exception("TG_SEND_EXC %s", e)
        return False, str(e)

def claim_task():
    with db() as con:
        row = con.execute("""
            SELECT id, chat_id, message_id, text
            FROM tasks
            WHERE status='PENDING'
            ORDER BY id ASC
            LIMIT 1
        """).fetchone()
        if not row:
            return None

        con.execute("""
            UPDATE tasks
            SET status='PROCESSING', worker_id=?, updated_at=?
            WHERE id=? AND status='PENDING'
        """, (WORKER_ID, now_ts(), row["id"]))
        con.commit()

        chk = con.execute("SELECT status FROM tasks WHERE id=?", (row["id"],)).fetchone()
        if not chk or chk["status"] != "PROCESSING":
            return None
        return row

def mark_done(task_id, result):
    with db() as con:
        con.execute("""
            UPDATE tasks
            SET status='DONE', result=?, error=NULL, updated_at=?
            WHERE id=?
        """, (result, now_ts(), task_id))
        con.commit()

def mark_error(task_id, error):
    with db() as con:
        con.execute("""
            UPDATE tasks
            SET status='ERROR', error=?, updated_at=?
            WHERE id=?
        """, ((error or "")[:4000], now_ts(), task_id))
        con.commit()

def reset_stuck():
    with db() as con:
        con.execute("""
            UPDATE tasks
            SET status='PENDING', worker_id=NULL, updated_at=?
            WHERE status IN ('PROCESSING','ERROR')
        """, (now_ts(),))
        con.commit()

def process_one(row):
    task_id = row["id"]
    text = (row["text"] or "").strip()
    chat_id = row["chat_id"]
    message_id = row["message_id"]

    log.info("PROCESS id=%s text=%s", task_id, text[:200])

    try:
        r = requests.post(
            ORCH_URL,
            json={"prompt": text},
            timeout=600,
        )
        body = r.text[:12000]
        if r.status_code != 200:
            raise RuntimeError(f"ORCH_HTTP_{r.status_code}: {body[:1000]}")

        try:
            data = r.json()
        except Exception:
            data = None

        if isinstance(data, dict):
            result = (data.get("stdout") or data.get("result") or data.get("answer") or body).strip()
            stderr = (data.get("stderr") or "").strip()
            ok = data.get("ok", True)
            if stderr:
                result = f"{result}\n\n[stderr]\n{stderr}".strip()
            if not ok and not result:
                raise RuntimeError(body[:1000])
        else:
            result = body.strip()

        result = clean_result_text(result)

        tg_ok, tg_resp = send_tg(chat_id, result, message_id)
        if not tg_ok:
            raise RuntimeError(f"TG_SEND_FAIL: {tg_resp}")

        mark_done(task_id, result)
        log.info("DONE %s", task_id)

    except Exception as e:
        log.exception("ERROR %s", task_id)
        mark_error(task_id, str(e))

def main():
    init_db()
    reset_stuck()
    log.info("STARTED DB=%s ORCH=%s", DB_PATH, ORCH_URL)
    while True:
        row = claim_task()
        if not row:
            time.sleep(2)
            continue
        process_one(row)

if __name__ == "__main__":
    main()
