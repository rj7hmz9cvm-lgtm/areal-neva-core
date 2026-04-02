from __future__ import annotations

import logging

from core.db import create_task, get_or_create_context, transition_task, get_active_task_in_topic

logger = logging.getLogger("core.telegram_ingress")


async def ingest(chat_id: int, user_id: int, text: str, topic_id: int | None = None) -> str | None:
    try:
        await get_or_create_context(chat_id=chat_id, user_id=user_id, topic_id=topic_id)

        if topic_id is not None:
            active = await get_active_task_in_topic(chat_id, topic_id)
            if active:
                logger.info("active task %s exists in topic %s, skip", active["id"], topic_id)
                return active["id"]

        res = await create_task(
            chat_id=chat_id,
            user_id=user_id,
            input_type="text",
            source="telegram",
            raw_input=text,
            topic_id=topic_id,
        )

        if not res or "id" not in res:
            logger.error("create_task returned invalid result: %r", res)
            return None

        task_id = res["id"]

        try:
            await transition_task(task_id, "INTAKE", triggered_by="telegram_ingress")
        except RuntimeError as e:
            logger.error("task %s INTAKE transition failed: %s", task_id, e)
            return None

        return task_id

    except Exception:
        logger.exception("ingest error chat=%s topic=%s", chat_id, topic_id)
        return None
