import os, asyncio, json
import sys
sys.path.insert(0, "/root/.areal-neva-core")
from telethon import TelegramClient, events
from dotenv import load_dotenv
from storage_layer import create_task

load_dotenv("/root/.areal-neva-core/.env")
client = TelegramClient("/tmp/tg_session", int(os.getenv("TG_API_ID")), os.getenv("TG_API_HASH"))
GROUP_ID = int(os.getenv("TELEGRAM_ALLOWED_GROUP_ID"))

@client.on(events.NewMessage)
async def handler(e):
    if e.chat_id != GROUP_ID or e.out: return
    txt = (e.raw_text or "").strip()
    if not txt and not e.file: return
    
    payload = {"text": txt, "from_id": e.sender_id}
    if e.file:
        path = await e.download_media(file="/tmp/orchestra_uploads/")
        payload["path"] = path
        
    tid = create_task(payload)
    await e.reply(f"✅ Задача принята: ID {tid}")

async def main():
    await client.start(bot_token=os.getenv("TELEGRAM_BOT_TOKEN"))
    print("TG_AGENT_READY")
    await client.run_until_disconnected()

if __name__=="__main__": asyncio.run(main())
