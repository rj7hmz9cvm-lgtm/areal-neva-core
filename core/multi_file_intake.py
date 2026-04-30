import json
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)
SESSION_WINDOW_SEC = 60

def init_session(data: dict) -> dict:
    base = dict(data or {})
    base["multi_file_session"] = {
        "files": [dict(data or {})],
        "count": 1,
    }
    return base

def get_active_session(conn, chat_id: str, topic_id: int) -> Optional[str]:
    row = conn.execute(
        """SELECT id
           FROM tasks
           WHERE chat_id=?
             AND COALESCE(topic_id,0)=?
             AND state='NEEDS_CONTEXT'
             AND input_type='drive_file'
             AND COALESCE(raw_input,'') LIKE '%multi_file_session%'
             AND (julianday('now') - julianday(updated_at))*86400 < ?
           ORDER BY updated_at DESC
           LIMIT 1""",
        (str(chat_id), int(topic_id or 0), SESSION_WINDOW_SEC),
    ).fetchone()
    return row["id"] if row else None

def attach_to_session(conn, session_task_id: str, new_file_data: dict) -> bool:
    try:
        row = conn.execute(
            "SELECT raw_input FROM tasks WHERE id=? AND state='NEEDS_CONTEXT'",
            (session_task_id,),
        ).fetchone()
        if not row:
            return False

        data = json.loads(row["raw_input"] or "{}")
        session = data.get("multi_file_session") or {"files": [], "count": 0}
        files = session.get("files") or []
        files.append(dict(new_file_data or {}))
        data["multi_file_session"] = {"files": files, "count": len(files)}

        conn.execute(
            "UPDATE tasks SET raw_input=?, updated_at=datetime('now') WHERE id=?",
            (json.dumps(data, ensure_ascii=False), session_task_id),
        )
        logger.info("MULTI_FILE_ATTACHED session=%s count=%d", session_task_id, len(files))
        return True
    except Exception as e:
        logger.error("MULTI_FILE_ATTACH_FAILED session=%s err=%s", session_task_id, e)
        return False

def get_session_files(conn, session_task_id: str) -> List[dict]:
    row = conn.execute("SELECT raw_input FROM tasks WHERE id=?", (session_task_id,)).fetchone()
    if not row:
        return []
    try:
        data = json.loads(row["raw_input"] or "{}")
        return data.get("multi_file_session", {}).get("files", [])
    except Exception:
        return []
