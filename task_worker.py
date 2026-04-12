import asyncio, os, logging, aiosqlite
from datetime import datetime, timezone
from core.ai_router import process_ai_task
from core.reply_sender import send_reply
from core.pin_manager import pin_message, is_important

DB = "/root/.areal-neva-core/data/core.db"
BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

async def get_db():
    db = await aiosqlite.connect(DB)
    await db.execute("PRAGMA busy_timeout=30000")
    await db.execute("PRAGMA journal_mode=WAL")
    return db

async def process_one_task():
    db = await get_db()
    async with db.execute("SELECT id, chat_id, input_type, raw_input, reply_to_message_id, state, result FROM tasks WHERE state IN ('NEW', 'IN_PROGRESS', 'AWAITING_CONFIRMATION') ORDER BY rowid ASC LIMIT 1") as c:
        task = await c.fetchone()
    await db.close()
    if not task: return False

    task_id, chat_id, input_type, raw_input, reply_to_message_id, state, result = task
    logger.info("PICKED task_id=%s chat_id=%s state=%s reply_to=%s", task_id, chat_id, state, reply_to_message_id)

    # --- AWAITING_CONFIRMATION → DONE / FAILED ---
    if state == "AWAITING_CONFIRMATION":
        text = (raw_input or "").strip().lower()
        if any(x in text for x in ["да", "подтверждаю", "ок", "yes", "ага", "верно"]):
            db = await get_db()
            await db.execute("UPDATE tasks SET state='DONE', updated_at=? WHERE id=?", (datetime.now(timezone.utc).isoformat(), task_id))
            await db.commit(); await db.close()
            await send_reply(BOT_TOKEN, int(chat_id), "Задача завершена", reply_to_message_id)
        else:
            db = await get_db()
            await db.execute("UPDATE tasks SET state='FAILED', updated_at=? WHERE id=?", (datetime.now(timezone.utc).isoformat(), task_id))
            await db.commit(); await db.close()
            await send_reply(BOT_TOKEN, int(chat_id), "Задача отменена", reply_to_message_id)
        await asyncio.sleep(0.5)
        return True

    # --- NEW: защита от зависших задач и реальный reply ---
    if state == "NEW":
        # Защита от зависших задач: если result уже заполнен → DONE
        if result and result.strip():
            logger.info("DONE stuck task_id=%s (already has result)", task_id)
            db = await get_db()
            await db.execute("UPDATE tasks SET state='DONE', updated_at=? WHERE id=?", (datetime.now(timezone.utc).isoformat(), task_id))
            await db.commit(); await db.close()
            await asyncio.sleep(0.5)
            return True

        # Если это reply — ищем РЕАЛЬНУЮ родительскую задачу (не текущую)
        if reply_to_message_id:
            db = await get_db()
            cur = await db.execute(
                "SELECT id FROM tasks WHERE reply_to_message_id=? AND state='NEW' AND id != ? ORDER BY created_at DESC LIMIT 1",
                (reply_to_message_id, task_id)
            )
            parent = await cur.fetchone()
            await db.close()

            if parent:
                parent_id = parent[0]
                logger.info("CONFIRM real parent task_id=%s via reply from %s", parent_id, task_id)
                db = await get_db()
                # Родитель → IN_PROGRESS
                await db.execute("UPDATE tasks SET state='IN_PROGRESS', updated_at=? WHERE id=?", (datetime.now(timezone.utc).isoformat(), parent_id))
                # Текущая reply-задача → ARCHIVED
                await db.execute("UPDATE tasks SET state='ARCHIVED', updated_at=? WHERE id=?", (datetime.now(timezone.utc).isoformat(), task_id))
                await db.commit(); await db.close()
                await asyncio.sleep(0.5)
                return True
            # Если родитель не найден — продолжаем как обычную NEW задачу

        text = (raw_input or "").strip().lower()
        is_confirm = any(x in text for x in ["да", "подтверждаю", "ок", "yes", "ага", "верно"])

        if is_confirm:
            db = await get_db()
            await db.execute("UPDATE tasks SET state='IN_PROGRESS', updated_at=? WHERE id=?", (datetime.now(timezone.utc).isoformat(), task_id))
            await db.commit(); await db.close()
            await asyncio.sleep(0.5)
            return True

        ai_result = await process_ai_task({
            "id": task_id,
            "chat_id": chat_id,
            "input_type": input_type,
            "raw_input": raw_input,
            "state": "NEW",
            "reply_to_message_id": reply_to_message_id
        })

        msg_id = await send_reply(BOT_TOKEN, int(chat_id), ai_result, reply_to_message_id)

        db = await get_db()
        if msg_id:
            await db.execute(
                "UPDATE tasks SET state='DONE', result=?, updated_at=? WHERE id=?",
                (ai_result, datetime.now(timezone.utc).isoformat(), task_id)
            )
        else:
            await db.execute(
                "UPDATE tasks SET state='FAILED', error_message='send_reply_failed', updated_at=? WHERE id=?",
                (datetime.now(timezone.utc).isoformat(), task_id)
            )
        await db.commit(); await db.close()
        await asyncio.sleep(0.5)
        return True

    # --- IN_PROGRESS → выполнение → AWAITING_CONFIRMATION ---
    if state == "IN_PROGRESS":
        ai_result = await process_ai_task({
            "id": task_id,
            "chat_id": chat_id,
            "input_type": input_type,
            "raw_input": raw_input,
            "state": "IN_PROGRESS",
            "reply_to_message_id": reply_to_message_id
        })
        msg_id = await send_reply(BOT_TOKEN, int(chat_id), ai_result + "\n\nПодтвердить выполнение?", reply_to_message_id)
        db = await get_db()
        if msg_id:
            await db.execute("UPDATE tasks SET state='AWAITING_CONFIRMATION', result=?, updated_at=? WHERE id=?", (ai_result, datetime.now(timezone.utc).isoformat(), task_id))
            # pin временно отключён до восстановления колонки pinned
        else:
            await db.execute("UPDATE tasks SET state='FAILED', error_message='send_reply_failed', updated_at=? WHERE id=?", (datetime.now(timezone.utc).isoformat(), task_id))
        await db.commit(); await db.close()
        await asyncio.sleep(0.5)
        return True

    await asyncio.sleep(0.5)
    return False

async def archive_old_done():
    while True:
        await asyncio.sleep(3600)
        db = await get_db()
        await db.execute("UPDATE tasks SET state='ARCHIVED' WHERE state='DONE' AND updated_at < datetime('now', '-7 days')")
        await db.commit(); await db.close()

async def main():
    logger.info("WORKER STARTED pid=%s", os.getpid())
    asyncio.create_task(archive_old_done())
    while True:
        try:
            if not await process_one_task(): await asyncio.sleep(1)
        except Exception as e:
            logger.exception("WORKER LOOP CRASH err=%s", e)
            await asyncio.sleep(2)

if __name__ == "__main__": asyncio.run(main())
