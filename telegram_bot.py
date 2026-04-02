import os, requests
from dotenv import load_dotenv

load_dotenv("/root/.areal-neva-core/.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if TOKEN:
    API = f"https://api.telegram.org/bot{TOKEN}"
else:
    API = None

def send_telegram_reply(chat_id, text):
    if not API or not chat_id or not text:
        return
    try:
        requests.post(f"{API}/sendMessage", json={
            "chat_id": chat_id,
            "text": str(text)[:4000]
        }, timeout=20)
    except Exception:
        pass
