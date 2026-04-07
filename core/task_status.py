from __future__ import annotations

import sqlite3
import logging

logger = logging.getLogger("core.task_status")

DB_PATH = "/root/.areal-neva-core/data/core.db"

def get_task_status_block(chat_id: int, limit: int = 10) -> str:
    try:
        con = sqlite3.connect(DB_PATH, timeout=10)
        cur = con.cursor()

        rows = cur.execute(
            """
            SELECT id, coalesce(state, ''), coalesce(input_type, ''), coalesce(raw_input, '')
            FROM tasks
            WHERE chat_id=?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (chat_id, limit),
        ).fetchall()

        con.close()

        if not rows:
            return ""

        out = ["TASK_STATUS"]
        for task_id, state, input_type, raw_input in rows:
            out.append(
                f"- id={task_id} state={state} type={input_type} text={str(raw_input)[:120]}"
            )
        return "\n".join(out)

    except Exception as e:
        logger.error("task_status error: %s", e)
        return ""
