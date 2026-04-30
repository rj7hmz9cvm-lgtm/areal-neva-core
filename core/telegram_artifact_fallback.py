import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

def send_artifact_to_telegram(
    chat_id,
    topic_id,
    reply_to_message_id,
    artifact_path: str,
    caption: str = "",
) -> dict:
    bot_token = os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return {"ok": False, "error": "BOT_TOKEN_NOT_SET"}
    if not artifact_path or not os.path.exists(artifact_path):
        return {"ok": False, "error": "ARTIFACT_NOT_FOUND"}
    try:
        data = {
            "chat_id": str(chat_id),
            "caption": caption or "Готово. Файл отправлен в Telegram.",
        }
        if topic_id and int(topic_id) > 0:
            data["message_thread_id"] = str(topic_id)
        if reply_to_message_id:
            data["reply_to_message_id"] = str(reply_to_message_id)
        with open(artifact_path, "rb") as f:
            res = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendDocument",
                data=data,
                files={"document": (os.path.basename(artifact_path), f)},
                timeout=30,
            )
        if res.ok:
            resp = res.json()
            msg = resp.get("result", {})
            doc = msg.get("document", {})
            return {
                "ok": True,
                "message_id": msg.get("message_id"),
                "file_id": doc.get("file_id"),
                "file_name": doc.get("file_name"),
            }
        return {"ok": False, "error": f"TG_STATUS_{res.status_code}"}
    except Exception as e:
        logger.error("send_artifact_to_telegram failed: %s", e)
        return {"ok": False, "error": str(e)}
