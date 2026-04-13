import aiohttp
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

ICONS = {
    "work": "⏳",
    "ok": "✅",
    "error": "❌",
}

async def _send(bot_token: str, payload: dict) -> Tuple[bool, str]:
    async with aiohttp.ClientSession() as s:
        r = await s.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30),
        )
        body = await r.text()
        return r.status == 200, body

async def send_status(bot_token: str, chat_id: int, text: str, reply_to_message_id: int | None = None, status: str = "work") -> bool:
    payload = {
        "chat_id": chat_id,
        "text": f"{ICONS.get(status, '⏳')} {(text or '').strip()[:4000]}",
    }
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id

    ok, body = await _send(bot_token, payload)
    logger.info("send_status chat_id=%s reply_to=%s status=%s ok=%s", chat_id, reply_to_message_id, status, ok)
    if not ok:
        logger.error("send_status telegram_error=%s", body[:500])
    return ok

async def send_reply(bot_token: str, chat_id: int, text: str, reply_to_message_id: int | None = None, status: str = "ok") -> bool:
    if not bot_token:
        logger.error("send_reply missing bot token")
        return False

    final_text = f"{ICONS.get(status, '')} {((text or '').strip() or 'Пустой ответ')}".strip()[:4096]
    payload = {
        "chat_id": chat_id,
        "text": final_text,
    }
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id

    ok, body = await _send(bot_token, payload)
    logger.info("send_reply chat_id=%s reply_to=%s status=%s ok=%s", chat_id, reply_to_message_id, status, ok)
    if not ok:
        logger.error("send_reply telegram_error=%s", body[:500])
    return ok
