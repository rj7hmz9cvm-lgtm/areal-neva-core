# === INBOX_AGGREGATOR_V1 ===
# Канон §22 — унифицированный агрегатор входящих
import logging
logger = logging.getLogger(__name__)

def normalize_inbox_item(
    source: str,
    external_id: str,
    text: str,
    user_name: str = "",
    user_id: str = "",
    contact: str = "",
    link: str = "",
    timestamp: str = "",
    attachments: list = None,
    chat_name: str = "",
    topic_id: int = 0,
    priority: str = "NORMAL",
) -> dict:
    """
    Привести любой источник к единому формату перед create_task()
    Канон: source / external_id / text / contact / link / timestamp / attachments
    """
    return {
        "source":      source,
        "external_id": str(external_id),
        "text":        str(text)[:2000],
        "user_name":   str(user_name),
        "user_id":     str(user_id),
        "contact":     str(contact),
        "link":        str(link),
        "timestamp":   str(timestamp),
        "attachments": attachments or [],
        "chat_name":   str(chat_name),
        "topic_id":    int(topic_id or 0),
        "priority":    priority,
        "status":      "NEW",
    }

def is_spam(text: str) -> bool:
    """Фильтр спама до создания задачи"""
    spam_markers = [
        "рефинансирование", "кредит без отказа", "займ онлайн",
        "заработок от 100к", "работа в интернете", "выиграли приз",
        "перейди по ссылке", "вы выбраны", "ставки на спорт",
    ]
    low = text.lower()
    return any(m in low for m in spam_markers)

def should_create_task(item: dict) -> bool:
    """Решить — создавать задачу из inbox item или нет"""
    if is_spam(item.get("text", "")):
        logger.info("INBOX_SPAM_FILTERED source=%s", item.get("source"))
        return False
    if not item.get("text", "").strip():
        return False
    return True

# Заглушки для будущих коннекторов
def fetch_email_inbox(imap_host: str, login: str, password: str) -> list:
    """IMAP connector — заглушка"""
    return []

def fetch_telegram_chats(session_path: str, chat_ids: list) -> list:
    """Telethon connector — заглушка"""
    return []

def fetch_profi_jobs(keywords: list, region: str) -> list:
    """Profi.ru connector — заглушка"""
    return []
# === END INBOX_AGGREGATOR_V1 ===
