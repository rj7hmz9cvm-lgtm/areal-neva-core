from __future__ import annotations

import asyncio
import inspect
import logging
import os
import sqlite3
import sys
import time
from typing import Any

logger = logging.getLogger("core.db_adapter")

DB_PATH = os.getenv("ORCHESTRA_DB_PATH", "/root/.areal-neva-core/data/core.db")

sys.path.insert(0, "/root/.areal-neva-core")

try:
    from core import db as _db
except Exception as e:
    logger.warning("core.db import failed, raw sqlite fallback only: %s", e)
    _db = None

_CREATE_TASK     = getattr(_db, "create_task",       None) if _db else None
_TRANSITION_TASK = getattr(_db, "transition_task",   None) if _db else None
_UPDATE_FIELDS   = getattr(_db, "update_task_fields",None) if _db else None
_GET_TASK        = getattr(_db, "get_task",          None) if _db else None
_INIT_DB         = getattr(_db, "init_db",           None) if _db else None


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ")


def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, timeout=15)
    con.row_factory = sqlite3.Row
    return con


async def try_init_db() -> None:
    if not _INIT_DB:
        logger.info("core.db init_db missing, raw sqlite fallback active")
        return

    attempts = [
        ((), {}),
        ((DB_PATH,), {}),
        ((), {"db_path": DB_PATH}),
        ((), {"db_path": DB_PATH, "schema_path": "/root/.areal-neva-core/schema.sql"}),
    ]
    for args, kwargs in attempts:
        try:
            result = _INIT_DB(*args, **kwargs)
            if inspect.isawaitable(result):
                await result
            logger.info("core.db init_db ok args=%s kwargs=%s", args, kwargs)
            return
        except TypeError:
            continue
        except Exception as e:
            logger.warning("core.db init_db failed args=%s kwargs=%s err=%s", args, kwargs, e)

    logger.warning("core.db init_db not usable, raw sqlite fallback active")


def _raw_update(task_id: str, **fields: Any) -> None:
    if not fields:
        return
    con = None
    try:
        con = _connect()
        now = _now()
        for k, v in fields.items():
            try:
                con.execute(
                    f"UPDATE tasks SET {k}=?, updated_at=? WHERE id=?",
                    (v, now, task_id),
                )
            except sqlite3.OperationalError:
                continue
        con.commit()
    finally:
        if con:
            con.close()


def _raw_transition(task_id: str, to_state: str) -> None:
    con = None
    try:
        con = _connect()
        now = _now()
        for col in ("state", "status"):
            try:
                con.execute(
                    f"UPDATE tasks SET {col}=?, updated_at=? WHERE id=?",
                    (to_state, now, task_id),
                )
                con.commit()
                return
            except sqlite3.OperationalError:
                continue
    finally:
        if con:
            con.close()


async def safe_update(task_id: str, **fields: Any) -> None:
    if not fields:
        return

    if _UPDATE_FIELDS:
        try:
            result = _UPDATE_FIELDS(task_id, **fields)
            if inspect.isawaitable(result):
                await result
            return
        except TypeError:
            try:
                result = _UPDATE_FIELDS(task_id=task_id, **fields)
                if inspect.isawaitable(result):
                    await result
                return
            except Exception as e:
                logger.warning("update_task_fields failed, raw fallback task=%s: %s", task_id, e)
        except Exception as e:
            logger.warning("update_task_fields failed, raw fallback task=%s: %s", task_id, e)

    await asyncio.to_thread(_raw_update, task_id, **fields)


async def safe_transition(task_id: str, to_state: str, triggered_by: str = "adapter") -> bool:
    if _TRANSITION_TASK:
        try:
            result = _TRANSITION_TASK(task_id, to_state, triggered_by)
            if inspect.isawaitable(result):
                await result
            return True
        except TypeError:
            try:
                result = _TRANSITION_TASK(task_id=task_id, to_state=to_state, triggered_by=triggered_by)
                if inspect.isawaitable(result):
                    await result
                return True
            except Exception as e:
                logger.warning("transition_task failed, raw fallback task=%s to=%s: %s", task_id, to_state, e)
        except Exception as e:
            logger.warning("transition_task failed, raw fallback task=%s to=%s: %s", task_id, to_state, e)

    await asyncio.to_thread(_raw_transition, task_id, to_state)
    return True


def _raw_get_task(task_id: str) -> dict | None:
    con = None
    try:
        con = _connect()
        row = con.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        return dict(row) if row else None
    finally:
        if con:
            con.close()


async def safe_get_task(task_id: str) -> dict | None:
    if _GET_TASK:
        try:
            result = _GET_TASK(task_id)
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as e:
            logger.warning("get_task failed, raw fallback task=%s: %s", task_id, e)

    return await asyncio.to_thread(_raw_get_task, task_id)


def _fetch_and_lock(state_value: str, next_state: str) -> dict | None:
    con = None
    try:
        con = sqlite3.connect(DB_PATH, isolation_level=None, timeout=15)
        con.row_factory = sqlite3.Row
        con.execute("BEGIN EXCLUSIVE")
        cur = con.cursor()

        row = None
        state_col = None
        for col in ("state", "status"):
            try:
                cur.execute(
                    f"SELECT * FROM tasks WHERE {col}=? ORDER BY created_at ASC LIMIT 1",
                    (state_value,),
                )
                row = cur.fetchone()
                if row:
                    state_col = col
                    break
            except sqlite3.OperationalError:
                continue

        if not row or not state_col:
            con.execute("ROLLBACK")
            con.close()
            return None

        task = dict(row)
        now = _now()
        cur.execute(
            f"UPDATE tasks SET {state_col}=?, updated_at=? WHERE id=?",
            (next_state, now, task["id"]),
        )
        con.execute("COMMIT")
        con.close()
        task[state_col] = next_state
        return task

    except Exception:
        logger.exception("_fetch_and_lock error state=%s", state_value)
        try:
            if con:
                con.execute("ROLLBACK")
                con.close()
        except Exception:
            pass
        return None


async def get_next_intake() -> dict | None:
    return await asyncio.to_thread(_fetch_and_lock, "INTAKE", "IN_PROGRESS")


async def get_next_ready() -> dict | None:
    return await asyncio.to_thread(_fetch_and_lock, "RESULT_READY", "DELIVERING")


def _fetch_history(chat_id: int, limit: int = 8) -> list[dict]:
    # FIX: top-level try/except — если _connect() падает, возвращаем []
    # вместо того чтобы пробрасывать исключение в process_ai_task
    terminal = (
        "DONE", "done",
        "RESULT_READY",
        "AWAITING_CONFIRMATION", "awaiting_confirmation",
        "COMPLETED", "completed",
        "SENT", "sent",
    )
    placeholders = ",".join("?" * len(terminal))
    con = None
    try:
        con = _connect()
        cur = con.cursor()

        rows = None
        for col in ("state", "status"):
            try:
                cur.execute(
                    f"SELECT input_type, coalesce(raw_input,''), coalesce(result,'') "
                    f"FROM tasks WHERE chat_id=? AND {col} IN ({placeholders}) "
                    f"ORDER BY created_at DESC LIMIT ?",
                    (chat_id, *terminal, limit),
                )
                rows = cur.fetchall()
                if rows is not None:
                    break
            except sqlite3.OperationalError:
                continue

        if not rows:
            return []

        history = []
        for r in reversed(rows):
            itype, raw, result = r[0], r[1], r[2]
            if raw:
                history.append({"role": "user", "content": f"[{itype}] {raw[:300]}"})
            if result:
                history.append({"role": "assistant", "content": result[:300]})
        return history

    except Exception:
        logger.exception("_fetch_history error chat_id=%s", chat_id)
        return []
    finally:
        if con:
            con.close()


async def get_history(chat_id: int, limit: int = 8) -> list[dict]:
    return await asyncio.to_thread(_fetch_history, chat_id, limit)
