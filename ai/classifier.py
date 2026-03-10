import logging
import httpx

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "Ты классификатор сообщений. Отвечай ТОЛЬКО одним словом: YES или NO. Никаких объяснений."

async def classify_message(text: str, provider: str = "claude", api_key: str = "") -> bool:
    if not text or not text.strip():
        return False
    # Для первого теста возвращаем True, чтобы убедиться, что цепочка работает
    return True
