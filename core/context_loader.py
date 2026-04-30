# === FULLFIX_CONTEXT_LOADER_STAGE_3 ===
from __future__ import annotations
import asyncio
from typing import Any, Dict, Optional

CONTEXT_LOADER_VERSION = "CONTEXT_LOADER_V1"


def _safe_str(v, default=""):
    if v is None: return default
    return str(v)


class ContextLoader:
    """
    Stage 3 shadow mode: загружает контекст задачи из доступных источников.
    Пишет context_refs в WorkItem. Не блокирует выполнение при ошибках.
    """

    def load(self, work_item, db_conn=None) -> Dict[str, Any]:
        chat_id = _safe_str(getattr(work_item, "chat_id", ""))
        topic_id = int(getattr(work_item, "topic_id", 0) or 0)
        raw_text = _safe_str(getattr(work_item, "raw_text", ""))[:500]
        direction = _safe_str(getattr(work_item, "direction", "general_chat"))

        refs = {
            "chat_id": chat_id,
            "topic_id": topic_id,
            "direction": direction,
            "short_memory": None,
            "long_memory": None,
            "recent_tasks": [],
            "topic_context": None,
            "loader_version": CONTEXT_LOADER_VERSION,
            "shadow_mode": True,
        }

        # short_memory — из memory_api если доступна
        try:
            refs["short_memory"] = self._load_short_memory(chat_id, topic_id)
        except Exception as e:
            refs["short_memory_error"] = str(e)

        # topic_context — последние задачи по теме из DB
        if db_conn is not None:
            try:
                refs["topic_context"] = self._load_topic_context(db_conn, chat_id, topic_id)
            except Exception as e:
                refs["topic_context_error"] = str(e)

        work_item.context_refs = refs
        work_item.add_audit("context_loader", CONTEXT_LOADER_VERSION)
        work_item.add_audit("context_topic_id", topic_id)
        return refs

    def _load_short_memory(self, chat_id, topic_id):
        import urllib.request, json
        url = f"http://127.0.0.1:8765/memory?chat_id={chat_id}&topic_id={topic_id}&limit=5"
        try:
            req = urllib.request.urlopen(url, timeout=2)
            data = json.loads(req.read().decode())
            return data if isinstance(data, (list, dict)) else None
        except Exception:
            return None

    def _load_topic_context(self, db_conn, chat_id, topic_id):
        try:
            import sqlite3
            if hasattr(db_conn, "execute"):
                rows = db_conn.execute(
                    "SELECT id, state, created_at FROM tasks WHERE chat_id=? AND topic_id=? ORDER BY created_at DESC LIMIT 5",
                    (str(chat_id), int(topic_id))
                ).fetchall()
            else:
                rows = []
            return [{"id": r[0], "state": r[1], "created_at": r[2]} for r in rows]
        except Exception:
            return []


def load_context(work_item, db_conn=None):
    return ContextLoader().load(work_item, db_conn)
# === END FULLFIX_CONTEXT_LOADER_STAGE_3 ===
