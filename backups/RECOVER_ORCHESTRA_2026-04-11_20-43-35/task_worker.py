import asyncio
import os
import logging
import aiosqlite
from datetime import datetime, timezone
from core.ai_router import process_ai_task
from core.reply_sender import send_reply, send_status

DB = "/root/.areal-neva-core/data/core.db"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

async def get_db():
    db = await aiosqlite.connect(DB)
    await db.execute("PRAGMA busy_timeout=30000")
    await db.execute("PRAGMA journal_mode=WAL")
    return db

async def worker():
    while True:
        db = await get_db()
        async with db.execute(
            "SELECT id, chat_id, input_type, raw_input, reply_to_message_id "
            "FROM tasks WHERE state='NEW' ORDER BY created_at ASC LIMIT 1"
        ) as c:
            task = await c.fetchone()
        await db.close()

        if not task:
            await asyncio.sleep(1)
            continue

        task_id, chat_id, input_type, raw_input, reply_to_message_id = task
        logger.info(
            "picked task_id=%s chat_id=%s input_type=%s raw_len=%s reply_to=%s",
            task_id, chat_id, input_type, len(raw_input or ""), reply_to_message_id
        )

        db = await get_db()
        await db.execute(
            "UPDATE tasks SET state='IN_PROGRESS', updated_at=? WHERE id=?",
            (datetime.now(timezone.utc).isoformat(), task_id),
        )
        await db.commit()
        await db.close()

        await send_status(BOT_TOKEN, int(chat_id), "В работе", reply_to_message_id, "work")

        result = ""
        error = None
        state = "FAILED"

        try:
            result = await process_ai_task({
                "id": task_id,
                "chat_id": chat_id,
                "input_type": input_type,
                "raw_input": raw_input,
                "reply_to_message_id": reply_to_message_id,
            })

            if not result or not str(result).strip():
                result = "Ошибка: пустой ответ LLM"

            ok = await send_reply(BOT_TOKEN, int(chat_id), result, reply_to_message_id, "ok")
            if ok:
                state = "DONE"
            else:
                state = "FAILED"
                error = "send_reply_failed"

        except Exception as e:
            error = str(e)
            logger.exception("task failed task_id=%s err=%s", task_id, e)
            fail_text = f"Ошибка: {str(e)[:1000]}"
            await send_reply(BOT_TOKEN, int(chat_id), fail_text, reply_to_message_id, "error")

        db = await get_db()
        await db.execute(
            "UPDATE tasks SET state=?, result=?, error_message=?, updated_at=? WHERE id=?",
            (state, result, error, datetime.now(timezone.utc).isoformat(), task_id),
        )
        await db.commit()
        await db.close()

async def main():
    while True:
        try:
            await worker()
        except Exception as e:
            logger.exception("worker loop crashed: %s", e)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
