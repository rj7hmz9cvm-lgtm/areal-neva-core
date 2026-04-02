# AREAL_PAYLOAD_MARK_GLOBAL
import sys
sys.path.insert(0, "/root/.areal-neva-core")

import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient, events
from core import db as core_db

BASE = "/root/.areal-neva-core"
LOG_PATH = f"{BASE}/logs/telegram_daemon.log"
MEDIA_DIR = f"{BASE}/data/telegram_media"
SESSION_BOT = f"{BASE}/sessions/bot.session"

Path(MEDIA_DIR).mkdir(parents=True, exist_ok=True)
Path(f"{BASE}/sessions").mkdir(parents=True, exist_ok=True)

load_dotenv(f"{BASE}/.env")

logger = logging.getLogger("telegram_daemon")
logger.setLevel(logging.INFO)
logger.handlers.clear()

fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

fh = logging.FileHandler(LOG_PATH)
fh.setFormatter(fmt)
logger.addHandler(fh)

sh = logging.StreamHandler()
sh.setFormatter(fmt)
logger.addHandler(sh)

logger.propagate = False

API_ID_RAW = (os.getenv("TG_API_ID", "") or "").strip()
API_ID = int(API_ID_RAW) if API_ID_RAW.isdigit() else 0
API_HASH = (os.getenv("TG_API_HASH", "") or "").strip()
BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN", "") or os.getenv("TG_BOT_TOKEN", "") or "").strip()

INIT_DB = getattr(core_db, "init_db", None)
CREATE_TASK = getattr(core_db, "create_task", None)
TRANSITION_TASK = getattr(core_db, "transition_task", None)
GET_OR_CREATE_CONTEXT = getattr(core_db, "get_or_create_context", None)

def _extract_topic_id(event):
    try:
        msg = getattr(event, "message", None)
        reply_to = getattr(msg, "reply_to", None)
        if reply_to is None:
            return None
        top_id = getattr(reply_to, "reply_to_top_id", None)
        if top_id is not None:
            return top_id
        msg_id = getattr(reply_to, "reply_to_msg_id", None)
        return msg_id
    except Exception:
        return None

async def _save_task(chat_id, user_id, topic_id, input_type, raw_input):
    if not CREATE_TASK:
        logger.error("CREATE_TASK NOT FOUND")
        return

    try:
        if GET_OR_CREATE_CONTEXT:
            try:
                await GET_OR_CREATE_CONTEXT(chat_id=chat_id, user_id=user_id, topic_id=topic_id)
            except Exception as e:
                logger.exception("CONTEXT ERROR %s", e)

        result = await CREATE_TASK(
            chat_id=chat_id,
            user_id=user_id,
            topic_id=topic_id,
            input_type=input_type,
            source="telegram",
            raw_input=raw_input,
        )

        task_id = result.get("id") if isinstance(result, dict) else str(result)

        if task_id and TRANSITION_TASK:
            try:
                await TRANSITION_TASK(task_id, "INTAKE", triggered_by="telegram_daemon")
                logger.info("TASK CREATED AND TRANSITIONED task_id=%s input_type=%s", task_id, input_type)
            except Exception as e:
                logger.exception("TRANSITION INTAKE ERROR task_id=%s error=%s", task_id, e)
        else:
            logger.info("TASK CREATED task_id=%s input_type=%s", task_id, input_type)

    except Exception as e:
        logger.exception("CREATE_TASK ERROR input_type=%s error=%s", input_type, e)

async def _handle_voice(event):
    try:
        chat_id = event.chat_id
        user_id = event.sender_id or 0
        topic_id = _extract_topic_id(event)

        file_path = f"{MEDIA_DIR}/{event.id}.ogg"
        await event.download_media(file=file_path)

        logger.info("VOICE SAVED chat_id=%s user_id=%s topic_id=%s path=%s", chat_id, user_id, topic_id, file_path)

        await _save_task(
            chat_id=chat_id,
            user_id=user_id,
            topic_id=topic_id,
            input_type="voice",
            raw_input=file_path,
        )
    except Exception as e:
        logger.exception("VOICE ERROR %s", e)

async def _handle_text(event):
    try:
        text = (event.raw_text or "").strip()
        if not text:
            return

        chat_id = event.chat_id
        user_id = event.sender_id or 0
        topic_id = _extract_topic_id(event)

        logger.info("TEXT OK chat_id=%s user_id=%s topic_id=%s text=%r", chat_id, user_id, topic_id, text[:120])

        await _save_task(
            chat_id=chat_id,
            user_id=user_id,
            topic_id=topic_id,
            input_type="text",
            raw_input=text,
        )
    except Exception as e:
        logger.exception("TEXT ERROR %s", e)

async def main():
    if INIT_DB:
        try:
            await INIT_DB()
            logger.info("DB INIT OK")
        except Exception as e:
            logger.exception("DB INIT ERROR %s", e)

    if not API_ID or not API_HASH or not BOT_TOKEN:
        logger.error("MISSING CREDENTIALS")
        raise RuntimeError("missing telegram credentials")

    client = TelegramClient(SESSION_BOT, API_ID, API_HASH)

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        try:
            if event.voice:
                await _handle_voice(event)
                return
            await _handle_text(event)
        except Exception as e:
            logger.exception("HANDLER ERROR %s", e)

    await client.start(bot_token=BOT_TOKEN)
    me = await client.get_me()
    logger.info("BOT STARTED id=%s username=%s", getattr(me, "id", ""), getattr(me, "username", ""))

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
