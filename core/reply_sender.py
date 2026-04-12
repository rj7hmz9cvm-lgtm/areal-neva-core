import aiohttp
import logging

logger = logging.getLogger(__name__)

async def send_reply(bot_token: str, chat_id: int, text: str, reply_to_message_id: int = None):
    if not bot_token or not text:
        return None
    payload = {"chat_id": chat_id, "text": text[:4096]}
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id
    try:
        async with aiohttp.ClientSession() as s:
            r = await s.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=payload, timeout=aiohttp.ClientTimeout(total=30))
            if r.status != 200:
                body = await r.text()
                logger.error(f"Telegram error {r.status}: {body[:200]}")
                return None
            data = await r.json()
            if data.get("ok"):
                return data["result"]["message_id"]
            return None
    except Exception as e:
        logger.error(f"send_reply exception: {e}")
        return None
