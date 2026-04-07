from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient, events

sys.path.insert(0, "/root/.areal-neva-core")
from core import db as core_db

BASE = "/root/.areal-neva-core"
MEDIA_DIR = "/root/AI_ORCHESTRA/telegram"
LOG_FILE = f"{BASE}/logs/telegram_daemon.log"

Path(MEDIA_DIR).mkdir(parents=True, exist_ok=True)
Path(f"{BASE}/logs").mkdir(parents=True, exist_ok=True)

load_dotenv(f"{BASE}/.env")

logger = logging.getLogger("telegram_daemon")
logger.setLevel(logging.INFO)
logger.handlers.clear()
fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(fh)

API_ID = int(os.getenv("TG_API_ID") or os.getenv("TELEGRAM_API_ID") or "0")
API_HASH = os.getenv("TG_API_HASH") or os.getenv("TELEGRAM_API_HASH") or ""
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or ""

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise RuntimeError("telegram_daemon env error: TG_API_ID/TG_API_HASH/TELEGRAM_BOT_TOKEN required")

client = TelegramClient(f"{BASE}/sessions/bot.session", API_ID, API_HASH)

def _extract_topic_id(event) -> int | None:
    try:
        msg = getattr(event, "message", None)
        reply_to = getattr(msg, "reply_to", None)
        if not reply_to:
            return None
        return getattr(reply_to, "reply_to_top_id", None) or getattr(reply_to, "reply_to_msg_id", None)
    except Exception:
        return None

async def _create_task(chat_id: int, user_id: int, topic_id: int | None, input_type: str, raw_input: str, triggered_by: str = "telegram_daemon") -> None:
    res = await core_db.create_task(
        chat_id=chat_id,
        user_id=user_id,
        topic_id=topic_id,
        input_type=input_type,
        source="telegram",
        raw_input=raw_input,
    )
    task_id = res.get("id") if isinstance(res, dict) else str(res)
    await core_db.transition_task(task_id, "INTAKE", triggered_by=triggered_by)
    logger.info("TASK CREATED id=%s type=%s chat_id=%s topic_id=%s", task_id, input_type, chat_id, topic_id)

async def _handle_text(event) -> None:
    chat_id = int(event.chat_id)
    user_id = int(getattr(event, "sender_id", 0) or 0)
    topic_id = _extract_topic_id(event)
    text = (event.raw_text or "").strip()
    if not text:
        return
    await _create_task(chat_id, user_id, topic_id, "text", text)

@client.on(events.NewMessage(incoming=True))
async def handler(event) -> None:
    try:
        chat_id = int(event.chat_id)
        user_id = int(getattr(event, "sender_id", 0) or 0)
        topic_id = _extract_topic_id(event)
        text = (event.raw_text or "").strip()

        media = getattr(event, "document", None) or getattr(event, "voice", None) or getattr(event, "photo", None) or getattr(event, "video", None)

        if media:
            if isinstance(media, list):
                media = media[-1]

            ext = ".bin"
            if getattr(event, "voice", None):
                ext = ".ogg"
            elif getattr(event, "photo", None):
                ext = ".jpg"
            elif getattr(event, "video", None):
                ext = ".mp4"
            elif getattr(event, "document", None):
                for a in getattr(media, "attributes", []):
                    if hasattr(a, "file_name") and "." in a.file_name:
                        ext = "." + a.file_name.split(".")[-1].lower()
                        break

            path = f"{MEDIA_DIR}/{event.id}{ext}"
            await event.download_media(file=path)
            logger.info("FILE SAVED %s", path)

            with open(f"{MEDIA_DIR}/chat_{chat_id}_latest.path", "w", encoding="utf-8") as f:
                f.write(path)

            if getattr(event, "voice", None):
                raw_input = path
                input_type = "voice"
            else:
                raw_input = f"[FILE:{path}] {text}".strip()
                input_type = "file"

            logger.info("RAW_INPUT READY chat_id=%s type=%s raw_input=%s", chat_id, input_type, raw_input[:200])
            await _create_task(chat_id, user_id, topic_id, input_type, raw_input)
            return

        if text:
            try:
                await _handle_text(event)
            except Exception as e:
                logger.info("FALLBACK TEXT TASK chat_id=%s err=%s", chat_id, e)
                await _create_task(chat_id, user_id, topic_id, "text", text, triggered_by="telegram_daemon_fallback")

    except Exception as e:
        logger.exception("HANDLER ERROR %s", e)

async def main() -> None:
    if getattr(core_db, "init_db", None):
        maybe = core_db.init_db()
        if asyncio.iscoroutine(maybe):
            await maybe
    await client.start(bot_token=BOT_TOKEN)
    me = await client.get_me()
    logger.info("BOT STARTED id=%s username=%s", getattr(me, "id", None), getattr(me, "username", None))
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
