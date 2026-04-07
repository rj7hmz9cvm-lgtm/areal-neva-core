import os, json, asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

BASE_DIR = "/root/AI_ORCHESTRA/telegram"
MAP_FILE = "/root/.areal-neva-core/data/memory/telegram_map.json"
ENV_FILE = "/root/.areal-neva-core/.env"
SESSION = "/root/.areal-neva-core/sessions/sync_bot"

load_dotenv(ENV_FILE)

API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDS = service_account.Credentials.from_service_account_file(
    "/root/.areal-neva-core/credentials.json", scopes=SCOPES
)
drive = build("drive", "v3", credentials=CREDS, cache_discovery=False)

client = TelegramClient(SESSION, API_ID, API_HASH)

def load_map():
    return json.load(open(MAP_FILE)) if os.path.exists(MAP_FILE) else {}

def save_map(m):
    json.dump(m, open(MAP_FILE, "w"), indent=2)

def ensure_drive(name):
    res = drive.files().list(
        q=f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id,name)"
    ).execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"]
    f = drive.files().create(
        body={"name": name, "mimeType": "application/vnd.google-apps.folder"},
        fields="id"
    ).execute()
    return f["id"]

def upload(file_path, name, folder):
    media = MediaFileUpload(file_path, resumable=True)
    drive.files().create(
        body={"name": name, "parents": [folder]},
        media_body=media
    ).execute()

async def sync_folders():
    m = load_map()
    os.makedirs(BASE_DIR, exist_ok=True)
    changed = False

    for name in os.listdir(BASE_DIR):
        path = os.path.join(BASE_DIR, name)
        if not os.path.isdir(path):
            continue

        # Проверяем, есть ли эта папка уже в значениях мапы
        folder_exists = any(v.get("project") == name for v in m.values())
        
        if not folder_exists and name not in m:
            drive_id = await asyncio.to_thread(ensure_drive, name)
            m[name] = {
                "project": name,
                "server_path": path,
                "drive_id": drive_id
            }
            changed = True

    if changed:
        save_map(m)

@client.on(events.NewMessage)
async def handler(event):
    if not event.media:
        return  # Жрем только файлы, текст идет через основной контур (по твоей схеме)

    m = load_map()
    chat_id = event.chat_id
    
    # Пытаемся вытащить ID топика, если это супергруппа с темами
    topic_id = event.reply_to_msg_id if getattr(event, 'is_reply', False) else None
    
    # Формируем жесткую привязку
    unique_key = f"{chat_id}_{topic_id}" if topic_id else str(chat_id)
    entry = m.get(unique_key)

    if not entry:
        name = f"chat_{chat_id}_topic_{topic_id}" if topic_id else f"chat_{chat_id}"
        path = os.path.join(BASE_DIR, name)
        os.makedirs(path, exist_ok=True)

        drive_id = await asyncio.to_thread(ensure_drive, name)

        m[unique_key] = {
            "project": name,
            "server_path": path,
            "drive_id": drive_id
        }
        save_map(m)
        entry = m[unique_key]

    # Достаем имя безопасно
    fname = "unknown_media"
    if hasattr(event, 'file') and event.file and getattr(event.file, 'name', None):
        fname = event.file.name
    else:
        fname = f"media_{event.id}"

    tmp = f"/tmp/{event.id}_{fname}"

    await event.download_media(file=tmp)

    try:
        if os.path.exists(tmp):
            await asyncio.to_thread(upload, tmp, fname, entry["drive_id"])
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

async def main():
    await client.start(bot_token=BOT_TOKEN)
    await sync_folders()
    print("SYNC_READY")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
