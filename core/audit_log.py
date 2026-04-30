# === AUDIT_LOG_V1 ===
import os, json, logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "audit.jsonl")

def audit(event: str, task_id: str = "", chat_id: str = "", details: dict = None):
    """Записать аудит-событие"""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "task_id": task_id,
        "chat_id": str(chat_id),
        "details": details or {},
    }
    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning("AUDIT_LOG_WRITE_ERR %s", e)

def tail_audit(n: int = 20) -> list:
    """Последние n записей аудита"""
    try:
        with open(_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [json.loads(l) for l in lines[-n:] if l.strip()]
    except Exception:
        return []
# === END AUDIT_LOG_V1 ===
