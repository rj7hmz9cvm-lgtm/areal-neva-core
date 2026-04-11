import asyncio, logging, os
from aiogram import Bot, Dispatcher, types
import aiosqlite, uuid
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN: raise RuntimeError("TELEGRAM_BOT_TOKEN missing")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
DB = "/root/.areal-neva-core/data/core.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("""CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, chat_id INTEGER, user_id INTEGER, input_type TEXT, raw_input TEXT, state TEXT DEFAULT "NEW", result TEXT, error_message TEXT, reply_to_message_id INTEGER, created_at TEXT, updated_at TEXT)""")
        await db.commit()

@dp.message()
async def handle_message(message: types.Message):
    async with aiosqlite.connect(DB) as db:
        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        await db.execute("INSERT INTO tasks (id, chat_id, user_id, input_type, raw_input, state, reply_to_message_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)", (task_id, message.chat.id, message.from_user.id, "text", message.text or "", "NEW", message.message_id, now, now))
        await db.commit()
    logger.info(f"Task {task_id} created")

async def main():
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    logger.info(f"BOT STARTED id={me.id} username={me.username}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
