#!/usr/bin/env python3
# === UPLOAD_RETRY_QUEUE_UNIFICATION_V1_WORKER ===
from __future__ import annotations
import json, os, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
DB = BASE / "data/core.db"

def main():
    if not DB.exists():
        print(json.dumps({"ok": False, "error": "DB_NOT_FOUND"}))
        return
    conn = sqlite3.connect(DB, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS upload_retry_queue(
        id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, task_id TEXT,
        topic_id INTEGER, kind TEXT, attempts INTEGER DEFAULT 0,
        last_error TEXT, created_at TEXT DEFAULT (datetime('now')), last_attempt TEXT)""")
    conn.commit()
    rows = conn.execute(
        "SELECT * FROM upload_retry_queue WHERE COALESCE(attempts,0)<5 ORDER BY id ASC LIMIT 25"
    ).fetchall()
    done = failed = 0
    for r in rows:
        rid = r["id"]
        path = str(r["path"] or "")
        task_id = str(r["task_id"] or "")
        topic_id = int(r["topic_id"] or 0)
        kind = str(r["kind"] or "artifact")
        link = ""
        try:
            if not path or not os.path.exists(path):
                raise RuntimeError("FILE_NOT_FOUND")
            from core.engine_base import upload_artifact_to_drive
            link = upload_artifact_to_drive(path, task_id, topic_id) or ""
            if not link:
                from core.engine_base import _telegram_fallback_send
                link = _telegram_fallback_send(path, task_id, topic_id) or ""
            if not link:
                raise RuntimeError("NO_LINK")
            row = conn.execute("SELECT result FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row:
                old = row[0] or ""
                new_line = f"{kind} retry OK: {link}"
                if new_line not in old:
                    conn.execute("UPDATE tasks SET result=?,updated_at=datetime('now') WHERE id=?",
                                 ((old+"\n"+new_line).strip(), task_id))
            conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                         (task_id, f"UPLOAD_RETRY_QUEUE_UNIFICATION_V1:OK:{link}"))
            conn.execute("DELETE FROM upload_retry_queue WHERE id=?", (rid,))
            done += 1
        except Exception as e:
            conn.execute(
                "UPDATE upload_retry_queue SET attempts=COALESCE(attempts,0)+1,last_error=?,last_attempt=? WHERE id=?",
                (str(e), datetime.now(timezone.utc).isoformat(), rid),
            )
            failed += 1
        conn.commit()
    conn.close()
    print(json.dumps({"ok": True, "processed": len(rows), "done": done, "failed": failed}))

if __name__ == "__main__":
    main()
# === END_UPLOAD_RETRY_QUEUE_UNIFICATION_V1_WORKER ===
