# === STARTUP_RECOVERY_V1 ===
from __future__ import annotations

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger("startup_recovery")

def _utc_cutoff(minutes: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(minutes=int(minutes))).replace(tzinfo=None).isoformat(sep=" ")

def _cols(conn: sqlite3.Connection, table: str) -> list[str]:
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except Exception:
        return []

async def run_startup_recovery(db_path: str, stale_minutes: int = 5) -> int:
    await asyncio.sleep(0)
    conn = sqlite3.connect(str(db_path), timeout=20)
    conn.row_factory = sqlite3.Row
    reset_count = 0

    try:
        cols = _cols(conn, "tasks")
        if "state" not in cols or "id" not in cols:
            logger.warning("STARTUP_RECOVERY_V1_NO_TASK_SCHEMA")
            return 0

        time_col = "updated_at" if "updated_at" in cols else ("created_at" if "created_at" in cols else "")
        if not time_col:
            logger.warning("STARTUP_RECOVERY_V1_NO_TIME_COLUMN")
            return 0

        cutoff = _utc_cutoff(stale_minutes)
        rows = conn.execute(
            f"SELECT id FROM tasks WHERE state='IN_PROGRESS' AND COALESCE({time_col}, '') < ?",
            (cutoff,),
        ).fetchall()

        for row in rows:
            task_id = str(row["id"])
            if "error_message" in cols:
                conn.execute(
                    "UPDATE tasks SET state='NEW', error_message=NULL, updated_at=datetime('now') WHERE id=?",
                    (task_id,),
                )
            else:
                conn.execute(
                    "UPDATE tasks SET state='NEW', updated_at=datetime('now') WHERE id=?",
                    (task_id,),
                )

            try:
                conn.execute(
                    "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                    (task_id, "STARTUP_RECOVERY_RESET"),
                )
            except Exception:
                pass

            logger.info("STARTUP_RECOVERY_RESET task_id=%s", task_id)
            reset_count += 1

        conn.commit()
        logger.info("STARTUP_RECOVERY_V1_DONE reset_count=%s", reset_count)
        return reset_count
    finally:
        conn.close()

# === END_STARTUP_RECOVERY_V1 ===
