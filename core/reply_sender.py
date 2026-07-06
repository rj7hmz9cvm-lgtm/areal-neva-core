

# === FULLFIX_13D_REPLY_SENDER_GLOBAL_MANIFEST_STRIP ===
def _ff13d_strip_manifest_links(text):
    import re
    if text is None:
        return text
    t = str(text)
    t = re.sub(r"(?im)^\s*MANIFEST\s*:\s*https?://\S+\s*$", "", t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    return t
# === END FULLFIX_13D_REPLY_SENDER_GLOBAL_MANIFEST_STRIP ===

import os
import logging
import re
import uuid
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=False)

LOG_PATH = f"{BASE}/logs/reply_sender.log"
os.makedirs(f"{BASE}/logs", exist_ok=True)
os.makedirs(f"{BASE}/data/telegram_artifacts", exist_ok=True)

logger = logging.getLogger("reply_sender")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_TEXT_LIMIT = 3900

def _clean(text: str) -> str:
    text = (text or "").replace("\r", "\n").strip()
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text[:12000]

def _humanize_internal_markers(text: str) -> str:
    out = str(text or "")
    replacements = {
        "checked_at": "Дата проверки",
        "source_status": "Статус проверки",
        "CONFIRMED": "подтверждено",
        "PARTIAL": "частично проверено",
        "UNVERIFIED": "не подтверждено",
        "RISK": "риск",
    }
    for src, dst in replacements.items():
        out = re.sub(rf"\b{src}\b", dst, out, flags=re.I)
    return out

def _safe_artifact_name() -> str:
    return "full_search_result_" + uuid.uuid4().hex[:12] + ".txt"

def _write_full_result_artifact(text: str) -> tuple[str, str]:
    file_name = _safe_artifact_name()
    path = os.path.join(BASE, "data", "telegram_artifacts", file_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text or "")
    return path, file_name

def _upload_full_result_to_drive(chat_id: str, topic_id: Optional[int], text: str) -> Dict[str, Any]:
    try:
        from core.topic_drive_oauth import _upload_file_sync
        path, file_name = _write_full_result_artifact(text)
        res = _upload_file_sync(path, file_name, str(chat_id), int(topic_id or 0), "text/plain")
        file_id = (res or {}).get("drive_file_id") or ""
        link = (res or {}).get("webViewLink") or (f"https://drive.google.com/file/d/{file_id}/view" if file_id else "")
        logger.info("long_text_drive_upload ok=%s file_id=%s link=%s", bool(file_id), file_id, link)
        return {"ok": bool(file_id), "path": path, "file_name": file_name, "drive_file_id": file_id, "link": link}
    except Exception as e:
        logger.exception("long_text_drive_upload_exception %s", e)
        return {"ok": False, "error": str(e)}

def _build_public_text(full_text: str, drive_link: str = "") -> str:
    if len(full_text or "") <= TELEGRAM_TEXT_LIMIT:
        return full_text
    suffix = "\n\nПолный результат сохранён на Google Drive:\n" + drive_link if drive_link else "\n\nТекст сокращён из-за лимита Telegram. Если нужно, попроси показать оставшиеся строки."
    budget = max(0, TELEGRAM_TEXT_LIMIT - len(suffix))
    return (full_text or "")[:budget].rstrip() + suffix

def send_reply(chat_id: str, text: str, reply_to_message_id: Optional[int] = None, message_thread_id: Optional[int] = None) -> bool:
    return send_reply_ex(chat_id=chat_id, text=_ff13d_strip_manifest_links(text), reply_to_message_id=reply_to_message_id, message_thread_id=message_thread_id)["ok"]

def send_reply_ex(chat_id: str, text: str, reply_to_message_id: Optional[int] = None, message_thread_id: Optional[int] = None) -> Dict[str, Any]:
    text = _humanize_internal_markers(_clean(text))
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return {"ok": False, "bot_message_id": None}
    if not chat_id:
        logger.error("chat_id missing")
        return {"ok": False, "bot_message_id": None}
    if not text:
        logger.error("text empty")
        return {"ok": False, "bot_message_id": None}
    full_text = _ff13d_strip_manifest_links(text)
    drive_res = None
    if len(full_text) > TELEGRAM_TEXT_LIMIT:
        drive_res = _upload_full_result_to_drive(str(chat_id), message_thread_id, full_text)
    public_text = _build_public_text(full_text, (drive_res or {}).get("link") or "")
    payload = {"chat_id": str(chat_id), "text": public_text, "disable_web_page_preview": True}
    if message_thread_id and int(message_thread_id) != 0:
        payload["message_thread_id"] = int(message_thread_id)
    if reply_to_message_id:
        payload["reply_to_message_id"] = int(reply_to_message_id)
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload, timeout=30)
        if r.status_code == 200 and r.json().get("ok") is True:
            bot_message_id = r.json().get("result", {}).get("message_id")
            logger.info("reply_ok chat_id=%s reply_to=%s chars=%s bot_message_id=%s", chat_id, reply_to_message_id, len(text), bot_message_id)
            return {"ok": True, "bot_message_id": bot_message_id, "drive_artifact": drive_res}
        logger.error("reply_fail code=%s body=%s", r.status_code, r.text[:500])
        return {"ok": False, "bot_message_id": None}
    except Exception as e:
        logger.exception("reply_exception %s", e)
        return {"ok": False, "bot_message_id": None}
