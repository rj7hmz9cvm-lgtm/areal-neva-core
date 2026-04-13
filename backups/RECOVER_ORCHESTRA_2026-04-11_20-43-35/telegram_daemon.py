import os
import uuid
import logging
import aiohttp
import aiofiles
import aiosqlite
from datetime import datetime, timezone
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
DB = "/root/.areal-neva-core/data/core.db"
TEMP_DIR = "/tmp/ai_orchestra"

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN missing")

os.makedirs(TEMP_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

async def create_task(message: types.Message, input_type: str, raw_input: str) -> str:
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    user_id = getattr(message.from_user, "id", 0) if message.from_user else 0

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO tasks (id, chat_id, user_id, input_type, raw_input, state, reply_to_message_id, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                task_id,
                message.chat.id,
                user_id,
                input_type,
                raw_input,
                "NEW",
                message.message_id,
                now,
                now,
            ),
        )
        await db.commit()

    logger.info(
        "task created task_id=%s chat_id=%s message_id=%s input_type=%s raw_len=%s",
        task_id, message.chat.id, message.message_id, input_type, len(raw_input or "")
    )
    return task_id

async def download_telegram_file(file_path: str, local_name: str) -> str:
    local_path = os.path.join(TEMP_DIR, local_name)
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    async with aiohttp.ClientSession() as s:
        async with s.get(url, timeout=aiohttp.ClientTimeout(total=300)) as r:
            r.raise_for_status()
            async with aiofiles.open(local_path, "wb") as f:
                await f.write(await r.read())
    return local_path

@dp.message(CommandStart())
async def on_start(message: types.Message):
    await create_task(message, "text", message.text or "/start")

@dp.message(F.voice)
async def on_voice(message: types.Message):
    tg_file = await bot.get_file(message.voice.file_id)
    local_path = await download_telegram_file(tg_file.file_path, f"voice_{message.message_id}.ogg")
    await create_task(message, "voice", local_path)

@dp.message(F.text)
async def on_text(message: types.Message):
    text = (message.text or "").strip()
    await create_task(message, "text", text)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    logger.info("BOT STARTED id=%s username=%s", me.id, me.username)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
