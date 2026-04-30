#!/usr/bin/env python3
# === FULLFIX_10_MONITOR_JOBS ===
import os
import time
import sqlite3
import logging
from datetime import datetime, timezone

BASE = "/root/.areal-neva-core"
DB = f"{BASE}/data/core.db"
LOG = f"{BASE}/logs/monitor_jobs.log"
STALE_SEC = 600

os.makedirs(f"{BASE}/logs", exist_ok=True)
logging.basicConfig(filename=LOG, level=logging.INFO, format="%(asctime)s MONITOR: %(message)s")

def connect():
    conn = sqlite3.connect(DB, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def main_once():
    conn = connect()
    rows = conn.execute("""
        SELECT id,state,chat_id,COALESCE(topic_id,0) topic_id,created_at,updated_at,substr(raw_input,1,160) raw_input
        FROM tasks
        WHERE state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
        ORDER BY updated_at DESC
        LIMIT 100
    """).fetchall()
    now = time.time()
    for r in rows:
        t = r["updated_at"] or r["created_at"]
        age = 0
        try:
            if "T" in str(t):
                dt = datetime.fromisoformat(str(t).replace("Z","+00:00"))
            else:
                dt = datetime.fromisoformat(str(t))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age = now - dt.timestamp()
        except Exception:
            pass
        if age > STALE_SEC and r["state"] in ("NEW","IN_PROGRESS","WAITING_CLARIFICATION"):
            conn.execute(
                "UPDATE tasks SET state='FAILED', error_message='MONITOR_STALE_TIMEOUT', updated_at=datetime('now') WHERE id=?",
                (r["id"],)
            )
            logging.warning("STALE_FAILED id=%s state=%s topic=%s age=%s raw=%s", r["id"], r["state"], r["topic_id"], int(age), r["raw_input"])
    conn.commit()
    stats = conn.execute("SELECT state,COUNT(*) c FROM tasks GROUP BY state ORDER BY state").fetchall()
    logging.info("STATS %s", " ".join([f"{x['state']}={x['c']}" for x in stats]))
    conn.close()

def main():
    logging.info("START")
    while True:
        try:
            main_once()
        except Exception as e:
            logging.exception("CRASH %s", e)
        time.sleep(60)

if __name__ == "__main__":
    main()
# === END FULLFIX_10_MONITOR_JOBS ===
