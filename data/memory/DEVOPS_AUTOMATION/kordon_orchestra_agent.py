import os
import re
import asyncio
import logging
from telethon import TelegramClient, events
from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
load_dotenv(os.path.join(BASE, ".env"))

SESSION_DIR = os.path.join(BASE, "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)
SESSION = os.path.join(SESSION_DIR, "user_agent")

API_ID_STR = os.getenv("TG_API_ID")
if not API_ID_STR:
    raise ValueError("CRITICAL: TG_API_ID missing")
API_ID = int(API_ID_STR)

API_HASH = os.getenv("TG_API_HASH")
if not API_HASH:
    raise ValueError("CRITICAL: TG_API_HASH missing")

MAIN_GROUP_STR = os.getenv("TG_MAIN_GROUP_ID")
if not MAIN_GROUP_STR:
    raise ValueError("CRITICAL: TG_MAIN_GROUP_ID missing")
MAIN_GROUP = int(MAIN_GROUP_STR)

LOG_FILE = os.path.join(BASE, "logs/kordon_orchestra_agent.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# SSOT Lead Triggers merged
LEAD_KEYS = [
    "бетон", "монолит", "фундамент", "опалубка", "арматура",
    "залить", "заливка", "строительство", "бригада", "работы",
    "плита", "нужны"
]

PRICE_KEYS = [
    "цена", "стоимость", "сколько", "руб", "₽", "бюджет", "оплата"
]

def is_lead(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in LEAD_KEYS)

def is_price(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in PRICE_KEYS)

def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text or "").strip()

def format_link(chat_id, msg_id):
    c = str(chat_id)
    if c.startswith("-100"):
        c = c[4:]
    return f"https://t.me/c/{c}/{msg_id}"

def format_lead(event, text):
    return f"🎯 ЛИД\n{text[:500]}\n\n{format_link(event.chat_id, event.id)}"

def format_price(event, text):
    return f"💰 ДЕНЬГИ\n{text[:500]}\n\n{format_link(event.chat_id, event.id)}"

client = TelegramClient(SESSION, API_ID, API_HASH)

@client.on(events.NewMessage)
async def handler(event):
    try:
        if event.chat_id == MAIN_GROUP:
            return

        if not event.raw_text:
            return

        text = clean_text(event.raw_text)
        if not text:
            return

        if is_lead(text):
            await client.send_message(MAIN_GROUP, format_lead(event, text))
            logging.info(f"LEAD chat={event.chat_id}")

        elif is_price(text):
            await client.send_message(MAIN_GROUP, format_price(event, text))
            logging.info(f"PRICE chat={event.chat_id}")

    except Exception as e:
        logging.error(f"ERROR: {e}")

async def main():
    logging.info("AGENT START")
    await client.start()
    logging.info("AGENT READY")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
