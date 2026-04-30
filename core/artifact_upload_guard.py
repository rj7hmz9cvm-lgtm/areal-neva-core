# === FULLFIX_14_ARTIFACT_UPLOAD_GUARD ===
import os, logging
logger = logging.getLogger(__name__)

def upload_or_fail(path, task_id, topic_id, kind="artifact"):
    if not path or not os.path.exists(path):
        # === FULLFIX_19_RETRY_FILE_NOT_FOUND ===
        try:
            import sqlite3 as _ff19_sql
            with _ff19_sql.connect("/root/.areal-neva-core/data/core.db", timeout=10) as _ff19_c:
                _ff19_c.execute("""CREATE TABLE IF NOT EXISTS upload_retry_queue(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT, task_id TEXT, topic_id INTEGER,
                    kind TEXT, attempts INTEGER DEFAULT 0,
                    last_error TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    last_attempt TEXT
                )""")
                _ff19_c.execute(
                    "INSERT INTO upload_retry_queue(path,task_id,topic_id,kind,last_error) VALUES(?,?,?,?,?)",
                    (str(path), str(task_id), int(topic_id or 0), str(kind), "FILE_NOT_FOUND")
                )
                _ff19_c.commit()
        except Exception:
            pass
        # === END FULLFIX_19_RETRY_FILE_NOT_FOUND ===
        return {"success": False, "error": "FILE_NOT_FOUND", "path": path}
    size = os.path.getsize(path)
    if size < 10:
        return {"success": False, "error": "FILE_TOO_SMALL", "path": path, "size": size}
    tried = []
    try:
        from core.engine_base import upload_artifact_to_drive
        link = upload_artifact_to_drive(path, task_id, topic_id)
        if link and str(link).startswith("http"):
            return {"success": True, "link": str(link), "path": path}
        tried.append("engine_base:empty_link")
    except Exception as e:
        tried.append("engine_base:" + str(e))
    # === FULLFIX_19_RETRY_QUEUE_REAL ===
    try:
        import sqlite3 as _ff19_sql
        with _ff19_sql.connect("/root/.areal-neva-core/data/core.db", timeout=10) as _ff19_c:
            _ff19_c.execute("""CREATE TABLE IF NOT EXISTS upload_retry_queue(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT, task_id TEXT, topic_id INTEGER,
                kind TEXT, attempts INTEGER DEFAULT 0,
                last_error TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                last_attempt TEXT
            )""")
            _ff19_c.execute(
                "INSERT INTO upload_retry_queue(path,task_id,topic_id,kind,last_error) VALUES(?,?,?,?,?)",
                (str(path), str(task_id), int(topic_id or 0), str(kind), "UPLOAD_FAILED")
            )
            _ff19_c.commit()
    except Exception:
        pass
    # === END FULLFIX_19_RETRY_QUEUE_REAL ===
    # === TG_FALLBACK_WIRED ===
    try:
        from core.engine_base import _telegram_fallback_send
        _tg_link = _telegram_fallback_send(str(path), str(task_id), int(topic_id or 0))
        if _tg_link:
            return {"success": True, "link": _tg_link, "path": path, "drive_failed": True, "telegram_fallback": True}
    except Exception as _tge:
        tried.append("telegram_fallback:" + str(_tge))
    # === END TG_FALLBACK_WIRED ===
    return {"success": False, "error": "UPLOAD_FAILED", "path": path, "size": size, "tried": tried}

def upload_many_or_fail(files, task_id, topic_id):
    results = {}
    all_ok = True
    for f in files:
        r = upload_or_fail(f["path"], task_id, topic_id, f.get("kind", "artifact"))
        results[f["path"]] = r
        if not r["success"]:
            all_ok = False
    return {"success": all_ok, "results": results}
# === END FULLFIX_14_ARTIFACT_UPLOAD_GUARD ===
