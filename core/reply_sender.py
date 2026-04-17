import os
import logging
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=False)

LOG_PATH = f"{BASE}/logs/reply_sender.log"
os.makedirs(f"{BASE}/logs", exist_ok=True)

logger = logging.getLogger("reply_sender")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

def _clean(text: str) -> str:
    text = (text or "").replace("\r", "\n").strip()
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text[:12000]

def send_reply(chat_id: str, text: str, reply_to_message_id: Optional[int] = None) -> bool:
    return send_reply_ex(chat_id=chat_id, text=text, reply_to_message_id=reply_to_message_id)["ok"]

def send_reply_ex(chat_id: str, text: str, reply_to_message_id: Optional[int] = None) -> Dict[str, Any]:
    text = _clean(text)
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return {"ok": False, "bot_message_id": None}
    if not chat_id:
        logger.error("chat_id missing")
        return {"ok": False, "bot_message_id": None}
    if not text:
        logger.error("text empty")
        return {"ok": False, "bot_message_id": None}
    payload = {"chat_id": str(chat_id), "text": text, "disable_web_page_preview": True}
    if reply_to_message_id:
        payload["reply_to_message_id"] = int(reply_to_message_id)
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload, timeout=30)
        if r.status_code == 200 and r.json().get("ok") is True:
            bot_message_id = r.json().get("result", {}).get("message_id")
            logger.info("reply_ok chat_id=%s reply_to=%s chars=%s bot_message_id=%s", chat_id, reply_to_message_id, len(text), bot_message_id)
            return {"ok": True, "bot_message_id": bot_message_id}
        logger.error("reply_fail code=%s body=%s", r.status_code, r.text[:500])
        return {"ok": False, "bot_message_id": None}
    except Exception as e:
        logger.exception("reply_exception %s", e)
        return {"ok": False, "bot_message_id": None}
