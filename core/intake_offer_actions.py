# === INTAKE_OFFER_ACTIONS_V1 ===
# При файле без команды → предложить варианты действий
import logging
logger = logging.getLogger(__name__)

_OFFER_TEXT = """Что сделать с файлом?

1️⃣ Смета — извлечь позиции, посчитать объёмы, создать Excel
2️⃣ Описание — описать содержимое документа
3️⃣ Таблица — вытащить таблицы из файла в Excel
4️⃣ Шаблон — сохранить как образец для будущих задач
5️⃣ Анализ — технический анализ (для КЖ/АР/КД)

Напиши номер или опиши задачу."""

_OFFER_MAP = {
    "1": "estimate", "смета": "estimate", "посчитай": "estimate",
    "2": "description", "описание": "description", "опиши": "description",
    "3": "table", "таблица": "table", "таблицу": "table",
    "4": "template", "шаблон": "template", "образец": "template",
    "5": "project", "анализ": "project", "кж": "project", "ар": "project",
}

def needs_offer(raw_input: str, caption: str = "") -> bool:
    """Нужно ли предлагать варианты — файл без команды"""
    combined = (raw_input + " " + caption).lower()
    # если уже есть команда — не предлагать
    action_words = ["смета", "посчитай", "таблиц", "шаблон", "опиши", "анализ",
                    "кж", "акт", "дефект", "dwg", "чертёж", "estimate"]
    return not any(w in combined for w in action_words)

def get_offer_text() -> str:
    return _OFFER_TEXT

def parse_offer_reply(reply: str) -> str:
    """Распознать выбор пользователя → intent"""
    low = reply.strip().lower().rstrip(".")
    return _OFFER_MAP.get(low, "")
# === END INTAKE_OFFER_ACTIONS_V1 ===
