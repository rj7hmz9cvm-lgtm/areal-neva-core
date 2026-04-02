from __future__ import annotations

import asyncio
import logging
import os
import sys

sys.path.insert(0, "/root/.areal-neva-core")

# FIX: logging настраивается ДО импортов, чтобы basicConfig не был no-op.
# force=True перезаписывает любые handlers, выставленные ранее импортами.
LOGDIR = "/root/.areal-neva-core/logs"
os.makedirs(LOGDIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(f"{LOGDIR}/task_worker.log"),
        logging.StreamHandler(),
    ],
    force=True,
)

logger = logging.getLogger("task_worker")

from dotenv import load_dotenv
load_dotenv("/root/.areal-neva-core/.env")

from core.db_adapter import (
    try_init_db,
    safe_transition,
    safe_update,
    safe_get_task,
    get_next_intake,
    get_next_ready,
)
from core.ai_router import process_ai_task
from core.stt import transcribe
from core.reply_sender import send_reply

POLL = float(os.getenv("WORKER_POLL_INTERVAL", "1.5"))


async def _fail(task_id: str, reason: str) -> None:
    logger.error("FAIL task=%s reason=%s", task_id, reason)
    await safe_update(task_id, error_message=reason)
    await safe_transition(task_id, "FAILED", "task_worker")


async def _process_intake(task: dict) -> None:
    task_id = task["id"]
    input_type = (task.get("input_type") or "text").strip().lower()
    raw = (task.get("raw_input") or "").strip()

    logger.info("INTAKE task=%s input_type=%s", task_id, input_type)

    if input_type == "voice":
        if not raw or not os.path.exists(raw):
            await _fail(task_id, f"voice file missing: {raw!r}")
            return

        logger.info("STT start task=%s file=%s", task_id, raw)
        text = await transcribe(raw)
        if not text:
            await _fail(task_id, "STT returned empty")
            return

        await safe_update(task_id, raw_input=text)
        task = await safe_get_task(task_id) or {**task, "raw_input": text}
        logger.info("STT done task=%s text=%r", task_id, text[:80])

    await process_ai_task(task)


async def _process_ready(task: dict) -> None:
    task_id = task["id"]
    chat_id = int(task.get("chat_id") or 0)
    topic_id = task.get("topic_id")
    result = (task.get("result") or "").strip()

    logger.info("DELIVER task=%s chat_id=%s", task_id, chat_id)

    if not result:
        await _fail(task_id, "empty result on deliver")
        return

    ok = await send_reply(chat_id, result, topic_id)
    if not ok:
        await _fail(task_id, "send_reply failed")
        return

    await safe_transition(task_id, "AWAITING_CONFIRMATION", "task_worker")
    logger.info("DELIVERED task=%s", task_id)


async def run_task_worker() -> None:
    await try_init_db()
    logger.info("task_worker started poll=%.1fs", POLL)

    while True:
        try:
            task = await get_next_intake()
            if task:
                await _process_intake(task)
                continue

            task = await get_next_ready()
            if task:
                await _process_ready(task)
                continue

        except Exception:
            logger.exception("worker loop error")

        await asyncio.sleep(POLL)


if __name__ == "__main__":
    asyncio.run(run_task_worker())
