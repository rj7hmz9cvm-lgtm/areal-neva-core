import aiohttp, logging

logger = logging.getLogger("reply_sender")

async def send_reply(bot_token: str, chat_id: int, text: str, reply_to_message_id: int = None) -> int:
    if not text:
        return None
    payload = {"chat_id": chat_id, "text": text[:4000]}
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=payload, timeout=30) as r:
                data = await r.json()
                if data.get("ok"):
                    return data["result"]["message_id"]
    except Exception as e:
        logger.error("Send reply failed: %s", e)
    return None
