import os
import requests
from pathlib import Path

def load_env():
    p = Path("/root/.areal-neva-core/.env")
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'").strip('"')

def send_telegram_reply(chat_id, reply_to_message_id, text):
    load_env()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("CRITICAL: TELEGRAM_BOT_TOKEN missing in .env")
        return None
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_to_message_id": reply_to_message_id,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"TG_SEND_ERROR: {e}")
        return None
