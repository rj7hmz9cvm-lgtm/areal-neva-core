import os
import logging
import asyncio
from typing import Optional

from dotenv import load_dotenv
from telethon import TelegramClient, events

from lib.orchestra_runtime import (
    build_prompt,
    build_task_key,
    call_orchestrator,
    extract_answer,
    mark_and_check_duplicate,
    should_skip_answer,
)

BASE_DIR = "/root/.areal-neva-core"
load_dotenv(f"{BASE_DIR}/.env")
load_dotenv(f"{BASE_DIR}/secrets.env", override=False)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("group_bot")

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "").strip()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
SESSION_NAME = os.path.expanduser(os.getenv("GROUP_BOT_SESSION", f"{BASE_DIR}/sessions/group_bot")).strip()
ALLOWED_CHATS = {int(x.strip()) for x in os.getenv("GROUP_BOT_CHAT_IDS", "").split(",") if x.strip()}

GROUP_SKIP_KEYWORDS = {
    "ок", "ага", "спс", "ясно", "понял", "привет", "+", "++", "окей"
}

if not API_ID or not API_HASH or not BOT_TOKEN or not ALLOWED_CHATS:
    raise RuntimeError("Missing required env vars for group_bot")

os.makedirs(os.path.dirname(SESSION_NAME), exist_ok=True)

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

def _get_thread_id(event) -> Optional[int]:
    try:
        return getattr(event.message, "reply_to_top_id", None) or getattr(event.message, "forum_topic_id", None)
    except Exception:
        return None

def quick_prefilter(text: str) -> bool:
    raw = (text or "").strip()
    if len(raw) < 3:
        return False
    if raw.lower() in GROUP_SKIP_KEYWORDS:
        return False
    return True

@client.on(events.NewMessage(chats=list(ALLOWED_CHATS)))
async def handle_text(event):
    try:
        if event.out:
            return
        if not event.message or not event.message.message:
            return

        raw_text = event.message.message.strip()
        if not quick_prefilter(raw_text):
            return

        sender = await event.get_sender()
        chat = await event.get_chat()

        user_id = getattr(sender, "id", 0) if sender else 0
        user_name = (
            " ".join(filter(None, [
                getattr(sender, "first_name", None) if sender else None,
                getattr(sender, "last_name", None) if sender else None,
            ])).strip()
            or (getattr(sender, "username", None) if sender else None)
            or "unknown"
        )

        dedup_key = build_task_key(event.chat_id, user_id, event.message.id, raw_text)
        if mark_and_check_duplicate(dedup_key):
            return

        prompt = build_prompt(
            chat_title=(getattr(chat, "title", None) if chat else None) or (getattr(chat, "username", None) if chat else None) or str(event.chat_id),
            chat_id=event.chat_id,
            thread_id=_get_thread_id(event),
            user_name=user_name,
            user_id=user_id,
            source="telegram",
            content_type="text",
            text=raw_text,
        )

        ans = extract_answer(await call_orchestrator(prompt))
        if should_skip_answer(ans):
            return

        await event.reply(ans[:4000])
        logger.info("reply sent | chat=%s | msg=%s", event.chat_id, event.message.id)

    except Exception:
        logger.exception("Handler error")

async def main():
    await client.start(bot_token=BOT_TOKEN)
    logger.info("group_bot ready")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
