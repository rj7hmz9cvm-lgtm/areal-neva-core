import os,sys,json,asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv("/root/.areal-neva-core/.env")

API_ID=int(os.getenv("TG_API_ID"))
API_HASH=os.getenv("TG_API_HASH")
BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
GROUP=int(os.getenv("TG_TARGET_GROUP_ID","-1002220455500"))

MAP="/root/.areal-neva-core/data/memory/projects_map.json"

def load():
    if not os.path.exists(MAP): return {}
    try: return json.load(open(MAP))
    except: return {}

def save(d):
    json.dump(d,open(MAP,"w"),indent=2)

async def main(name):
    d=load()
    if name in d:
        print("EXISTS",name)
        return

    client=TelegramClient("/tmp/tg_sessions/sync",API_ID,API_HASH)
    await client.start(bot_token=BOT_TOKEN)

    # КРИТИЧЕСКИЙ ФИКС — получаем entity правильно
    dialogs = await client.get_dialogs()

    target = None
    for dlg in dialogs:
        if dlg.id == GROUP:
            target = dlg.entity
            break

    if not target:
        raise RuntimeError("GROUP_NOT_FOUND_BY_BOT")

    msg = await client.send_message(target, f"📁 {name}")
    topic_id = msg.id

    d[name]={"topic_id":topic_id}
    save(d)

    print("CREATED",name,topic_id)

if __name__=="__main__":
    asyncio.run(main(sys.argv[1]))
