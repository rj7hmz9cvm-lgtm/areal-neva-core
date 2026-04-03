import os
import sys
import requests
import logging
import time
from pathlib import Path
from dotenv import load_dotenv

# Гарантируем видимость локальных модулей
sys.path.append("/root/.areal-neva-core")
import storage_layer

# Явно указываем путь к env
load_dotenv("/root/.areal-neva-core/.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing in .env")

API = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("/root/.areal-neva-core/logs/telegram_ingress.log"),
        logging.StreamHandler()
    ]
)

BASE_DIR = Path("/root/AI_ORCHESTRA/telegram")
BASE_DIR.mkdir(parents=True, exist_ok=True)

def get_updates(offset=None):
    try:
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
        return requests.get(f"{API}/getUpdates", params=params, timeout=35).json()
    except Exception as e:
        logging.error(f"get_updates error: {e}")
        return {}

def get_file(file_id):
    r = requests.get(f"{API}/getFile", params={"file_id": file_id}).json()
    return r["result"]["file_path"]

def download(file_path, dst):
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    r = requests.get(url, timeout=60)
    with open(dst, "wb") as f:
        f.write(r.content)

def create_task(payload, chat_id, msg_id):
    storage_layer.create_task(
        payload,
        source="telegram",
        chat_id=str(chat_id),
        msg_id=str(msg_id),
    )

def handle(msg):
    chat_id = msg["chat"]["id"]
    msg_id = msg["message_id"]

    # TEXT
    if msg.get("text"):
        create_task(
            {"text": msg["text"], "source": "telegram"},
            chat_id, msg_id
        )
        logging.info("TEXT task created")
        return

    # VOICE
    if msg.get("voice"):
        file_id = msg["voice"]["file_id"]
        path = get_file(file_id)
        dst = BASE_DIR / f"{msg_id}.ogg"
        download(path, dst)

        create_task(
            {
                "text": "voice message",
                "path": str(dst),
                "type": "voice",
                "source": "telegram"
            },
            chat_id, msg_id
        )
        logging.info("VOICE task created")
        return

    # PHOTO
    if msg.get("photo"):
        file_id = msg["photo"][-1]["file_id"]
        path = get_file(file_id)
        dst = BASE_DIR / f"{msg_id}.jpg"
        download(path, dst)

        create_task(
            {
                "text": "image",
                "path": str(dst),
                "source": "telegram"
            },
            chat_id, msg_id
        )
        logging.info("PHOTO task created")
        return

def main():
    offset = None
    storage_layer.init_db()
    logging.info("telegram_ingress start | db_ready")

    while True:
        data = get_updates(offset)
        for upd in data.get("result", []):
            offset = upd["update_id"] + 1
            msg = upd.get("message")
            if msg:
                handle(msg)
        time.sleep(1)

if __name__ == "__main__":
    main()
