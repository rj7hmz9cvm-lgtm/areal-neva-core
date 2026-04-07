from __future__ import annotations

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import aiosqlite

logger = logging.getLogger("core.db")

DB_PATH = "/root/.areal-neva-core/data/core.db"

_pool: Optional[aiosqlite.Connection] = None
_write_lock = asyncio.Lock()

VALID_TRANSITIONS: dict[str, set[str]] = {
    "NEW": {"INTAKE", "FAILED", "CANCELLED"},
    "INTAKE": {"NEEDS_CONTEXT", "IN_PROGRESS", "FAILED", "CANCELLED"},
    "NEEDS_CONTEXT": {"INTAKE", "IN_PROGRESS", "FAILED", "CANCELLED"},
    "IN_PROGRESS": {"RESULT_READY", "FAILED", "CANCELLED", "TIMEOUT"},
    "RESULT_READY": {"AWAITING_CONFIRMATION", "DONE", "FAILED"},
    "AWAITING_CONFIRMATION": {"DONE", "REVISION_REQUESTED", "FAILED", "CANCELLED", "TIMEOUT"},
    "REVISION_REQUESTED": {"IN_PROGRESS", "REVISION_PENDING", "FAILED", "CANCELLED"},
    "REVISION_PENDING": {"IN_PROGRESS", "FAILED", "CANCELLED"},
    "DONE": set(),
    "FAILED": set(),
    "CANCELLED": set(),
    "TIMEOUT": set(),
}

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def _new_id() -> str:
    return str(uuid.uuid4())

def _row_to_dict(row: Optional[aiosqlite.Row]) -> Optional[dict]:
    return dict(row) if row is not None else None

async def init_db() -> None:
    global _pool
    if _pool is not None:
        return
    _pool = await aiosqlite.connect(DB_PATH, isolation_level=None)
    _pool.row_factory = aiosqlite.Row
    await _pool.execute("PRAGMA journal_mode=WAL")
    await _pool.execute("PRAGMA foreign_keys=ON")
    await _pool.execute("PRAGMA synchronous=NORMAL")

def _get_conn() -> aiosqlite.Connection:
    if _pool is None:
        raise RuntimeError("DB not initialized")
    return _pool

@asynccontextmanager
async def transaction():
    if _pool is None:
        await init_db()
    async with _write_lock:
        conn = _get_conn()
        await conn.execute("BEGIN IMMEDIATE")
        try:
            yield conn
            await conn.execute("COMMIT")
        except Exception:
            await conn.execute("ROLLBACK")
            raise

async def create_task(
    chat_id: int,
    user_id: int,
    input_type: str,
    source: str,
    raw_input: str | None = None,
    topic_id: int | None = None,
    priority: int = 5,
    cancellable: bool = True,
    agent_type: str | None = None,
    parent_task_id: str | None = None,
    media_group_id: str | None = None,
    timeout_seconds: int | None = None,
) -> dict:
    task_id = _new_id()
    now = _now_iso()
    timeout_at = None
    if timeout_seconds is not None:
        timeout_at = (datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    async with transaction() as conn:
        await conn.execute(
            """
            INSERT INTO tasks (
                id, parent_task_id, media_group_id,
                chat_id, topic_id, user_id,
                source, input_type, raw_input, agent_type,
                state, priority, cancellable, created_at, updated_at, timeout_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NEW', ?, ?, ?, ?, ?)
            """,
            (
                task_id, parent_task_id, media_group_id,
                chat_id, topic_id, user_id,
                source, input_type, raw_input, agent_type,
                priority, int(cancellable), now, now, timeout_at
            )
        )
    return {"id": task_id}

async def get_task(task_id: str) -> Optional[dict]:
    conn = _get_conn()
    async with conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cur:
        row = await cur.fetchone()
    return _row_to_dict(row)

async def get_tasks_by_state(state: str) -> list[dict]:
    conn = _get_conn()
    async with conn.execute(
        "SELECT * FROM tasks WHERE state = ? ORDER BY priority ASC, created_at ASC",
        (state,)
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]

async def get_active_task_in_topic(chat_id: int, topic_id: int | None = None) -> Optional[dict]:
    conn = _get_conn()
    active_states = (
        "NEW", "INTAKE", "NEEDS_CONTEXT", "IN_PROGRESS",
        "RESULT_READY", "AWAITING_CONFIRMATION",
        "REVISION_REQUESTED", "REVISION_PENDING"
    )
    placeholders = ",".join("?" * len(active_states))
    if topic_id is not None:
        sql = f"""
        SELECT * FROM tasks
        WHERE chat_id = ? AND topic_id = ? AND state IN ({placeholders})
        ORDER BY created_at DESC
        LIMIT 1
        """
        params = (chat_id, topic_id, *active_states)
    else:
        sql = f"""
        SELECT * FROM tasks
        WHERE chat_id = ? AND topic_id IS NULL AND state IN ({placeholders})
        ORDER BY created_at DESC
        LIMIT 1
        """
        params = (chat_id, *active_states)

    async with conn.execute(sql, params) as cur:
        row = await cur.fetchone()
    return _row_to_dict(row)

async def transition_task(task_id: str, to_state: str, triggered_by: str = "system", note: str | None = None) -> None:
    now = _now_iso()
    async with transaction() as conn:
        async with conn.execute("SELECT state FROM tasks WHERE id = ?", (task_id,)) as cur:
            row = await cur.fetchone()
        if row is None:
            raise RuntimeError(f"task not found: {task_id}")

        from_state = row["state"]
        allowed = VALID_TRANSITIONS.get(from_state, set())
        if to_state not in allowed:
            raise RuntimeError(f"invalid transition {from_state} -> {to_state}")

        await conn.execute(
            "UPDATE tasks SET state = ?, updated_at = ? WHERE id = ?",
            (to_state, now, task_id)
        )
        await conn.execute(
            """
            INSERT INTO state_transitions (
                task_id, from_state, to_state, triggered_by, note, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (task_id, from_state, to_state, triggered_by, note, now)
        )

async def update_task_fields(task_id: str, **fields: Any) -> None:
    if not fields:
        return
    now = _now_iso()
    sets = [f"{k} = ?" for k in fields]
    values = list(fields.values()) + [now, task_id]
    async with transaction() as conn:
        await conn.execute(
            f"UPDATE tasks SET {', '.join(sets)}, updated_at = ? WHERE id = ?",
            values
        )

async def get_or_create_context(chat_id: int, user_id: int, topic_id: int | None = None) -> dict:
    conn = _get_conn()
    if topic_id is not None:
        async with conn.execute(
            "SELECT * FROM context_sessions WHERE chat_id = ? AND topic_id = ?",
            (chat_id, topic_id)
        ) as cur:
            row = await cur.fetchone()
    else:
        async with conn.execute(
            "SELECT * FROM context_sessions WHERE chat_id = ? AND topic_id IS NULL",
            (chat_id,)
        ) as cur:
            row = await cur.fetchone()

    if row is not None:
        data = dict(row)
        data["history"] = json.loads(data["history"]) if data.get("history") else []
        data["pinned_data"] = json.loads(data["pinned_data"]) if data.get("pinned_data") else {}
        return data

    ctx_id = _new_id()
    now = _now_iso()
    async with transaction() as conn:
        await conn.execute(
            """
            INSERT OR IGNORE INTO context_sessions (
                id, chat_id, topic_id, user_id, last_task_id,
                history, pinned_data, active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, NULL, '[]', '{}', 1, ?, ?)
            """,
            (ctx_id, chat_id, topic_id, user_id, now, now)
        )

    return await get_or_create_context(chat_id, user_id, topic_id)

async def update_context_last_task(chat_id: int, task_id: str, topic_id: int | None = None) -> None:
    now = _now_iso()
    async with transaction() as conn:
        if topic_id is not None:
            await conn.execute(
                "UPDATE context_sessions SET last_task_id = ?, updated_at = ? WHERE chat_id = ? AND topic_id = ?",
                (task_id, now, chat_id, topic_id)
            )
        else:
            await conn.execute(
                "UPDATE context_sessions SET last_task_id = ?, updated_at = ? WHERE chat_id = ? AND topic_id IS NULL",
                (task_id, now, chat_id)
            )

async def create_artifact(
    task_id: str,
    artifact_type: str,
    file_path: str | None = None,
    file_url: str | None = None,
    storage_url: str | None = None,
    source_message_id: int | None = None,
    metadata: dict | None = None,
) -> str:
    artifact_id = _new_id()
    now = _now_iso()
    async with transaction() as conn:
        await conn.execute(
            """
            INSERT INTO artifacts (
                id, task_id, source_message_id, type,
                file_path, file_url, drive_url, storage_url,
                metadata, processing_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, 'pending', ?, ?)
            """,
            (
                artifact_id, task_id, source_message_id, artifact_type,
                file_path, file_url, storage_url,
                json.dumps(metadata or {}), now, now
            )
        )
    return artifact_id

async def get_artifact(artifact_id: str) -> Optional[dict]:
    conn = _get_conn()
    async with conn.execute("SELECT * FROM artifacts WHERE id = ?", (artifact_id,)) as cur:
        row = await cur.fetchone()
    if row is None:
        return None
    data = dict(row)
    data["metadata"] = json.loads(data["metadata"]) if data.get("metadata") else {}
    return data

async def update_artifact(artifact_id: str, **fields: Any) -> None:
    if not fields:
        return
    now = _now_iso()
    if "metadata" in fields and isinstance(fields["metadata"], dict):
        fields["metadata"] = json.dumps(fields["metadata"])
    sets = [f"{k} = ?" for k in fields]
    values = list(fields.values()) + [now, artifact_id]
    async with transaction() as conn:
        await conn.execute(
            f"UPDATE artifacts SET {', '.join(sets)}, updated_at = ? WHERE id = ?",
            values
        )

async def save_lead_log(data: dict) -> None:
    async with transaction() as conn:
        await conn.execute(
            """
            INSERT INTO leads_log (
                source, raw_text, volume, location, phone, budget, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("source"),
                data.get("raw"),
                data.get("volume"),
                data.get("location"),
                data.get("phone"),
                data.get("budget"),
                _now_iso(),
            )
        )

async def get_due_schedule_rules() -> list[dict]:
    now = _now_iso()
    conn = _get_conn()
    async with conn.execute(
        """
        SELECT * FROM automation_rules
        WHERE type = 'schedule'
          AND is_active = 1
          AND next_run_at IS NOT NULL
          AND next_run_at <= ?
        ORDER BY next_run_at ASC
        """,
        (now,)
    ) as cur:
        rows = await cur.fetchall()
    out = []
    for row in rows:
        r = dict(row)
        r["schedule"] = json.loads(r["schedule_json"]) if r.get("schedule_json") else {}
        r["condition"] = json.loads(r["condition_json"]) if r.get("condition_json") else {}
        out.append(r)
    return out

async def log_automation_event(rule_id: str, event_type: str, payload: dict, status: str = "done") -> None:
    async with transaction() as conn:
        await conn.execute(
            """
            INSERT INTO automation_events (
                id, rule_id, event_type, payload_json, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (_new_id(), rule_id, event_type, json.dumps(payload), status, _now_iso())
        )

async def upsert_followup(
    source: str,
    external_id: str,
    chat_id: int,
    user_id: int,
    followup_deadline: str,
    topic_id: int | None = None,
) -> None:
    now = _now_iso()
    async with transaction() as conn:
        await conn.execute(
            """
            INSERT INTO followup_state (
                id, source, external_id, chat_id, topic_id, user_id,
                last_seen_at, last_replied_at, followup_required, followup_deadline, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 1, ?, 'open')
            ON CONFLICT(source, external_id) DO UPDATE SET
                last_seen_at = excluded.last_seen_at,
                followup_deadline = excluded.followup_deadline,
                followup_required = 1,
                status = 'open'
            """,
            (_new_id(), source, external_id, chat_id, topic_id, user_id, now, followup_deadline)
        )

async def get_due_followups() -> list[dict]:
    now = _now_iso()
    conn = _get_conn()
    async with conn.execute(
        """
        SELECT * FROM followup_state
        WHERE followup_required = 1
          AND status = 'open'
          AND followup_deadline <= ?
        ORDER BY followup_deadline ASC
        """,
        (now,)
    ) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]

async def mark_followup_notified(followup_id: str) -> None:
    async with transaction() as conn:
        await conn.execute(
            """
            UPDATE followup_state
            SET status = 'notified', followup_required = 0
            WHERE id = ?
            """,
            (followup_id,)
        )
