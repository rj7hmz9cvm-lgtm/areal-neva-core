# === FULLFIX_14_ARTIFACT_UPLOAD_GUARD ===
# === UPLOAD_RETRY_QUEUE_UNIFICATION_V1 ===
# === HEAVY_FILE_STORAGE_POLICY_V1 ===
from __future__ import annotations
import logging
import os
import sqlite3
from typing import Any, Dict

logger = logging.getLogger(__name__)
_DB = "/root/.areal-neva-core/data/core.db"

def _ensure_retry_table(conn: sqlite3.Connection) -> None:
    conn.execute("""CREATE TABLE IF NOT EXISTS upload_retry_queue(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT, task_id TEXT, topic_id INTEGER, kind TEXT,
        attempts INTEGER DEFAULT 0, last_error TEXT,
        created_at TEXT DEFAULT (datetime('now')), last_attempt TEXT
    )""")

def _queue_retry(path: str, task_id: str, topic_id: int, kind: str, error: str) -> None:
    try:
        with sqlite3.connect(_DB, timeout=10) as c:
            _ensure_retry_table(c)
            c.execute(
                "INSERT INTO upload_retry_queue(path,task_id,topic_id,kind,last_error) VALUES(?,?,?,?,?)",
                (str(path), str(task_id), int(topic_id or 0), str(kind or "artifact"), str(error)),
            )
            try:
                c.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (str(task_id), f"UPLOAD_RETRY_QUEUE_UNIFICATION_V1:QUEUED:{kind}"),
                )
            except Exception:
                pass
            c.commit()
    except Exception as e:
        logger.warning("UPLOAD_RETRY_QUEUE_UNIFICATION_V1_ERR task=%s err=%s", task_id, e)

def _cleanup_heavy(path: str, link: str = "") -> bool:
    try:
        p = str(path or "")
        if not p or not os.path.exists(p):
            return False
        size = os.path.getsize(p)
        is_tmp = p.startswith("/tmp/") or p.startswith("/var/tmp/") or "/runtime/" in p
        if size >= 20 * 1024 * 1024 and is_tmp:
            os.remove(p)
            logger.info("HEAVY_FILE_STORAGE_POLICY_V1_CLEANED path=%s link=%s", p, link)
            return True
    except Exception as e:
        logger.warning("HEAVY_FILE_STORAGE_POLICY_V1_CLEAN_ERR path=%s err=%s", path, e)
    return False

def upload_or_fail(path: str, task_id: str, topic_id: int, kind: str = "artifact") -> Dict[str, Any]:
    if not path or not os.path.exists(str(path)):
        _queue_retry(path, task_id, topic_id, kind, "FILE_NOT_FOUND")
        return {"success": False, "error": "FILE_NOT_FOUND", "path": path, "queued": True}
    size = os.path.getsize(str(path))
    if size < 10:
        _queue_retry(path, task_id, topic_id, kind, "FILE_TOO_SMALL")
        return {"success": False, "error": "FILE_TOO_SMALL", "path": path, "size": size, "queued": True}
    tried = []
    try:
        from core.engine_base import upload_artifact_to_drive
        link = upload_artifact_to_drive(str(path), str(task_id), int(topic_id or 0))
        if link and str(link).startswith("http"):
            _cleanup_heavy(path, link)
            return {"success": True, "link": str(link), "drive_link": str(link),
                    "path": str(path), "kind": kind, "queued": False}
        tried.append("drive:no_link")
    except Exception as e:
        tried.append(f"drive:{e}")
    _queue_retry(path, task_id, topic_id, kind, "DRIVE_UPLOAD_FAILED")
    try:
        from core.engine_base import _telegram_fallback_send
        tg = _telegram_fallback_send(str(path), str(task_id), int(topic_id or 0))
        if tg:
            _cleanup_heavy(path, tg)
            return {"success": True, "link": str(tg), "telegram_link": str(tg),
                    "path": str(path), "kind": kind, "drive_failed": True,
                    "telegram_fallback": True, "queued": True}
    except Exception as e:
        tried.append(f"telegram:{e}")
    return {"success": False, "error": "UPLOAD_FAILED", "path": str(path),
            "size": size, "tried": tried, "queued": True}

def upload_many_or_fail(files, task_id: str, topic_id: int) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    links: Dict[str, str] = {}
    all_ok = True
    for f in files or []:
        if isinstance(f, str):
            path, kind = f, "artifact"
        elif isinstance(f, dict):
            path = f.get("path") or f.get("file") or f.get("artifact_path") or ""
            kind = f.get("kind") or "artifact"
        else:
            path, kind = str(f or ""), "artifact"
        r = upload_or_fail(str(path), str(task_id), int(topic_id or 0), str(kind))
        results[str(path)] = r
        if not (isinstance(r, dict) and r.get("success")):
            all_ok = False
        if isinstance(r, dict):
            link = str(r.get("link") or r.get("drive_link") or r.get("telegram_link") or "")
            if link:
                links[str(path)] = link
    return {"success": all_ok, "results": results, "links": links,
            "queued": any(isinstance(v, dict) and v.get("queued") for v in results.values())}
# === END_HEAVY_FILE_STORAGE_POLICY_V1 ===
# === END_UPLOAD_RETRY_QUEUE_UNIFICATION_V1 ===
# === END FULLFIX_14_ARTIFACT_UPLOAD_GUARD ===
