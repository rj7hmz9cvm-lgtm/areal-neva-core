import logging
import httpx
from telethon.tl.types import Message

logger = logging.getLogger(__name__)

async def send_notification(phone: str, message: Message, bot_token: str, chat_id: int) -> bool:
    chat_name = getattr(message.chat, "title", None) or getattr(message.chat, "username", str(message.chat_id))
    sender = getattr(message.sender, "username", None) or getattr(message.sender, "first_name", "unknown")
    
    text = (
        f"🔔 *Новое сообщение*\n"
        f"Аккаунт: `{phone}`\n"
        f"Чат: `{chat_name}`\n"
        f"От: `{sender}`\n"
        f"─────────────────\n"
        f"{message.text[:2000]}"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Notifier failed: {e}")
        return False
