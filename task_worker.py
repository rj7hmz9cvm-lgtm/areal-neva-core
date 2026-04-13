import asyncio, json, logging, os, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, "/root/.areal-neva-core")
from core.ai_router import process_ai_task
from core.reply_sender import send_reply
from core.web_engine import web_search
from core.pin_manager import activate_pin

DB = "/root/.areal-neva-core/data/core.db"
BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s WORKER: %(message)s")
logger = logging.getLogger("task_worker")

TIMEOUT_MINUTES = 30

async def get_db():
    import aiosqlite
    db = await aiosqlite.connect(DB)
    await db.execute("PRAGMA busy_timeout=30000")
    await db.execute("PRAGMA journal_mode=WAL")
    return db

async def process_one_task():
    import logging
    logger = logging.getLogger("task_worker")
    db = await get_db()
    
    timeout_threshold = (datetime.now(timezone.utc) - timedelta(minutes=TIMEOUT_MINUTES)).isoformat()
    await db.execute(
        "UPDATE tasks SET state = 'FAILED', error_message = 'timeout' WHERE state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') AND updated_at < ?",
        (timeout_threshold,)
    )
    await db.commit()
    
    async with db.execute(
        "SELECT id, chat_id, input_type, raw_input, reply_to_message_id, state FROM tasks WHERE state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS') AND (result IS NULL OR result = '') ORDER BY created_at ASC LIMIT 1"
    ) as c:
        task = await c.fetchone()
    
    if not task:
        await db.close()
        return False
    
    task_id, chat_id, input_type, raw_input, reply_to, state = task
    
    if state == "NEW":
        await db.execute(
            "UPDATE tasks SET state = 'IN_PROGRESS', updated_at = ? WHERE id = ?",
            (datetime.now(timezone.utc).isoformat(), task_id)
        )
        await db.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
            (task_id, "picked:IN_PROGRESS", datetime.now(timezone.utc).isoformat())
        )
        await db.commit()
        state = "IN_PROGRESS"
    
    await db.close()
    logger.info("PICKED %s state=%s", task_id, state)
    
    if input_type == "voice":
        import inspect
        logger.info("STT start file=%s", raw_input)
        from core.stt_engine import transcribe_voice
        if inspect.iscoroutinefunction(transcribe_voice):
            transcript = await transcribe_voice(raw_input)
        else:
            transcript = transcribe_voice(raw_input)
        if not transcript or not transcript.strip():
            logger.error("STT failed for %s", raw_input)
            await send_reply(BOT_TOKEN, int(chat_id), "Не удалось распознать голос", reply_to)
            db = await get_db()
            await db.execute("UPDATE tasks SET state = 'FAILED', error_message = 'stt_failed' WHERE id = ?", (task_id,))
            await db.commit(); await db.close()
            return True
        logger.info("STT ok transcript_len=%d", len(transcript))
        db = await get_db()
        await db.execute("UPDATE tasks SET raw_input = ?, error_message = NULL WHERE id = ?", (transcript, task_id))
        await db.commit(); await db.close()
        raw_input = transcript

    if input_type == "search":
        ai_result = await web_search(raw_input)
        final_state = "DONE"
    else:
        ai_result = await process_ai_task({
            "id": task_id, "chat_id": chat_id, "input_type": input_type,
            "raw_input": raw_input, "state": state, "reply_to_message_id": reply_to
        })
        final_state = "AWAITING_CONFIRMATION"
    
    db = await get_db()
    await db.execute("UPDATE tasks SET result = ? WHERE id = ?", (ai_result, task_id))
    await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (task_id, f"result:{ai_result[:100]}", datetime.now(timezone.utc).isoformat()))
    
    if final_state == "AWAITING_CONFIRMATION":
        await db.execute("UPDATE tasks SET state = 'AWAITING_CONFIRMATION', updated_at = ? WHERE id = ?", (datetime.now(timezone.utc).isoformat(), task_id))
        await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (task_id, "state:AWAITING_CONFIRMATION", datetime.now(timezone.utc).isoformat()))
        await db.commit()
        await db.close()
        activate_pin(str(chat_id), task_id)
        msg_id = await send_reply(BOT_TOKEN, int(chat_id), ai_result + "\n\nПодтвердить выполнение?", reply_to)
        if not msg_id:
            db = await get_db()
            await db.execute("UPDATE tasks SET state = 'FAILED', error_message = 'send_reply_failed' WHERE id = ?", (task_id,))
            await db.commit()
            await db.close()
    else:
        await db.execute("UPDATE tasks SET state = 'DONE', updated_at = ? WHERE id = ?", (datetime.now(timezone.utc).isoformat(), task_id))
        await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (task_id, "state:DONE", datetime.now(timezone.utc).isoformat()))
        await db.commit()
        await db.close()
        await send_reply(BOT_TOKEN, int(chat_id), ai_result, reply_to)
    
    return True

async def archive_old_tasks():
    while True:
        await asyncio.sleep(3600)
        db = await get_db()
        await db.execute("UPDATE tasks SET state = 'ARCHIVED' WHERE state IN ('DONE','FAILED','CANCELLED') AND updated_at < datetime('now', '-7 days')")
        await db.commit()
        await db.close()

async def main():
    logger.info("WORKER STARTED pid=%s", os.getpid())
    asyncio.create_task(archive_old_tasks())
    while True:
        try:
            if not await process_one_task():
                await asyncio.sleep(1)
        except Exception as e:
            logger.exception("CRASH: %s", e)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
