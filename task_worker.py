import asyncio, logging, os, aiosqlite, sys
from datetime import datetime, timezone
import aiohttp

sys.path.insert(0, "/root/.areal-neva-core")
from core.ai_router import process_ai_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB = "/root/.areal-neva-core/data/core.db"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN: logger.error("TELEGRAM_BOT_TOKEN missing")

async def get_db():
    db = await aiosqlite.connect(DB)
    await db.execute("PRAGMA busy_timeout=30000")
    await db.execute("PRAGMA journal_mode=WAL")
    return db

async def send_reply(chat_id, text, reply_to=None):
    if not BOT_TOKEN: return
    async with aiohttp.ClientSession() as s:
        r = await s.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text[:4096], "reply_to_message_id": reply_to}, timeout=aiohttp.ClientTimeout(total=30))
        if r.status != 200: logger.error(f"TELEGRAM ERROR: {r.status} {await r.text()}")

async def worker():
    while True:
        db = await get_db()
        async with db.execute("SELECT id, chat_id, raw_input, reply_to_message_id FROM tasks WHERE state='NEW' ORDER BY created_at ASC LIMIT 1") as c:
            task = await c.fetchone()
        if not task:
            await db.close()
            await asyncio.sleep(1)
            continue
        task_id, chat_id, prompt, reply_id = task
        await db.execute("UPDATE tasks SET state='IN_PROGRESS', updated_at=? WHERE id=?", (datetime.now(timezone.utc).isoformat(), task_id))
        await db.commit()
        await db.close()
        try:
            result = await process_ai_task({"id": task_id, "chat_id": chat_id, "raw_input": prompt})
            if not result or str(result).strip() == "": result = "Ошибка: пустой ответ LLM"
            await send_reply(chat_id, result, reply_id)
            state, error = "DONE", None
        except Exception as e:
            result, state, error = None, "FAILED", str(e)
            logger.error(f"Task {task_id} failed: {e}")
        db = await get_db()
        await db.execute("UPDATE tasks SET state=?, result=?, error_message=?, updated_at=? WHERE id=?", (state, result, error, datetime.now(timezone.utc).isoformat(), task_id))
        await db.commit()
        await db.close()

if __name__ == "__main__":
    asyncio.run(worker())
