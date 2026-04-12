import aiohttp
import logging

logger = logging.getLogger(__name__)

async def pin_message(bot_token: str, chat_id: int, message_id: int) -> bool:
    try:
        async with aiohttp.ClientSession() as s:
            r = await s.post(f"https://api.telegram.org/bot{bot_token}/pinChatMessage", json={"chat_id": chat_id, "message_id": message_id}, timeout=aiohttp.ClientTimeout(total=10))
            return (await r.json()).get("ok", False)
    except Exception as e:
        logger.error(f"pin_message error: {e}")
        return False

def is_important(text: str) -> bool:
    if not text:
        return False
    keywords = ["смета", "итог", "расчёт", "заключение", "акт", "отчёт", "результат", "ведомость", "спецификация"]
    return any(k in text.lower() for k in keywords)
