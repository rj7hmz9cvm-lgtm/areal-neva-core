from __future__ import annotations

import logging
import os
import aiohttp

from core.db import get_task, transition_task, update_task_fields

logger = logging.getLogger("delivery")


def _get_token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "")


async def _send(chat_id: str, text: str, topic_id: int | None = None) -> bool:
    token = _get_token()
    if not token:
        logger.error("telegram token missing")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text[:4096]}
    if topic_id is not None:
        payload["message_thread_id"] = topic_id

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    return True
                body = await resp.text()
                logger.error("telegram send http=%s body=%s", resp.status, body[:300])
                return False
    except Exception:
        logger.exception("telegram send error")
        return False


async def deliver_task_by_id(task_id: str) -> bool:
    task = await get_task(task_id)
    if task is None:
        logger.error("task not found task=%s", task_id)
        return False

    state = task.get("state")
    if state != "RESULT_READY":
        logger.warning("task=%s state=%s not RESULT_READY", task_id, state)
        return False

    chat_id = str(task.get("chat_id") or "")
    topic_id = task.get("topic_id")
    result_text = (task.get("result") or "").strip()

    if not chat_id:
        logger.error("task=%s no chat_id", task_id)
        await update_task_fields(task_id, error_message="no chat_id for delivery")
        try:
            await transition_task(task_id, "FAILED", triggered_by="delivery")
        except RuntimeError:
            pass
        return False

    if not result_text:
        logger.error("task=%s empty result", task_id)
        await update_task_fields(task_id, error_message="empty result")
        try:
            await transition_task(task_id, "FAILED", triggered_by="delivery")
        except RuntimeError:
            pass
        return False

    ok = await _send(chat_id, result_text, topic_id)
    if not ok:
        return False

    try:
        await transition_task(task_id, "AWAITING_CONFIRMATION", triggered_by="delivery")
    except RuntimeError as exc:
        logger.error("task=%s AWAITING_CONFIRMATION failed: %s", task_id, exc)
        return False

    return True
