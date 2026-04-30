import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

def get_file_id(raw_input: str) -> Optional[str]:
    try:
        return json.loads(raw_input or "{}").get("file_id")
    except Exception:
        return None

def find_duplicate(conn, chat_id: str, topic_id: int, file_id: str) -> Optional[Dict]:
    if not file_id:
        return None
    row = conn.execute(
        """SELECT id, state, substr(result,1,240) result, updated_at
           FROM tasks
           WHERE chat_id=?
             AND COALESCE(topic_id,0)=?
             AND input_type='drive_file'
             AND COALESCE(raw_input,'') LIKE ?
             AND state IN ('DONE','AWAITING_CONFIRMATION')
           ORDER BY updated_at DESC
           LIMIT 1""",
        (str(chat_id), int(topic_id or 0), f'%"file_id": "{file_id}"%'),
    ).fetchone()
    return dict(row) if row else None

def duplicate_message(prev: Dict, file_name: str) -> str:
    prev_result = (prev.get("result") or "").strip()[:160]
    if prev_result:
        return (
            f"Этот файл уже был: {file_name}\n"
            f"Прошлый результат: {prev_result}\n\n"
            f"Что сделать?\n"
            f"1. Повторить обработку\n"
            f"2. Сделать другое\n"
            f"3. Отменить"
        )
    return (
        f"Этот файл уже был: {file_name}\n\n"
        f"Что сделать?\n"
        f"1. Повторить обработку\n"
        f"2. Сделать другое\n"
        f"3. Отменить"
    )
