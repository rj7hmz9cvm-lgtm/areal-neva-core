#!/usr/bin/env python3
# === FULLFIX_18B_SAFE_V2_MONITOR_JOBS ===
import os
import time
import sqlite3
import logging
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
DB_PATH = BASE / "data" / "core.db"
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "monitor_jobs.log"

POLL_SEC = int(os.getenv("MONITOR_JOBS_POLL_SEC", "600"))
STALE_AWAITING_HOURS = int(os.getenv("STALE_AWAITING_HOURS", "3"))
STALE_RUNTIME_MINUTES = int(os.getenv("STALE_RUNTIME_MINUTES", "30"))
LIMIT_PER_RUN = int(os.getenv("MONITOR_JOBS_LIMIT", "100"))

logger = logging.getLogger("monitor_jobs")
logger.setLevel(logging.INFO)
logger.handlers.clear()

_fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

_fh = logging.FileHandler(str(LOG_PATH))
_fh.setFormatter(_fmt)
logger.addHandler(_fh)

_sh = logging.StreamHandler()
_sh.setFormatter(_fmt)
logger.addHandler(_sh)


def _connect():
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def _history(conn, task_id, action):
    conn.execute(
        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
        (task_id, action),
    )


def close_stale_runtime(conn, minutes=STALE_RUNTIME_MINUTES, limit=LIMIT_PER_RUN):
    """
    Preserve existing monitor_jobs responsibility:
    stale NEW / IN_PROGRESS / WAITING_CLARIFICATION must not hang forever
    """
    rows = conn.execute(
        """
        SELECT id,state
        FROM tasks
        WHERE state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION')
        AND datetime(updated_at) < datetime('now', ?)
        ORDER BY updated_at ASC
        LIMIT ?
        """,
        (f"-{int(minutes)} minutes", int(limit)),
    ).fetchall()

    closed = 0
    for row in rows:
        task_id = row["id"]
        old_state = row["state"]
        result = f"Задача закрыта монитором: зависла в статусе {old_state} дольше {minutes} минут"
        cur = conn.execute(
            """
            UPDATE tasks
            SET state='FAILED',
                result=COALESCE(NULLIF(result,''), ?),
                error_message=COALESCE(NULLIF(error_message,''), ?),
                updated_at=datetime('now')
            WHERE id=?
            AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION')
            """,
            (result, f"STALE_{old_state}_{minutes}MIN", task_id),
        )
        if cur.rowcount:
            _history(conn, task_id, f"state:FAILED:stale_runtime_cleanup_{old_state}_{minutes}min")
            closed += 1

    return closed


def close_stale_awaiting_confirmation(conn, hours=STALE_AWAITING_HOURS, limit=LIMIT_PER_RUN):
    """
    AWAITING_CONFIRMATION is not execution failure.
    If user did not confirm for hours, close as DONE to prevent stale context pollution
    """
    rows = conn.execute(
        """
        SELECT id
        FROM tasks
        WHERE state='AWAITING_CONFIRMATION'
        AND datetime(updated_at) < datetime('now', ?)
        ORDER BY updated_at ASC
        LIMIT ?
        """,
        (f"-{int(hours)} hours", int(limit)),
    ).fetchall()

    closed = 0
    for row in rows:
        task_id = row["id"]
        cur = conn.execute(
            """
            UPDATE tasks
            SET state='DONE',
                updated_at=datetime('now')
            WHERE id=?
            AND state='AWAITING_CONFIRMATION'
            """,
            (task_id,),
        )
        if cur.rowcount:
            _history(conn, task_id, f"state:DONE:stale_awaiting_cleanup_{hours}h")
            closed += 1

    return closed


def monitor_once():
    with _connect() as conn:
        runtime_closed = close_stale_runtime(conn)
        awaiting_closed = close_stale_awaiting_confirmation(conn)
        conn.commit()
        if runtime_closed or awaiting_closed:
            logger.info(
                "MONITOR_CLEANUP runtime_closed=%s awaiting_closed=%s",
                runtime_closed,
                awaiting_closed,
            )
        return runtime_closed, awaiting_closed


def main():
    logger.info(
        "MONITOR_JOBS_START db=%s poll=%s runtime_min=%s awaiting_h=%s limit=%s",
        DB_PATH,
        POLL_SEC,
        STALE_RUNTIME_MINUTES,
        STALE_AWAITING_HOURS,
        LIMIT_PER_RUN,
    )
    while True:
        try:
            monitor_once()
        except Exception as e:
            logger.exception("MONITOR_JOBS_ERROR err=%s", e)
        time.sleep(POLL_SEC)


if __name__ == "__main__":
    main()
# === END FULLFIX_18B_SAFE_V2_MONITOR_JOBS ===
