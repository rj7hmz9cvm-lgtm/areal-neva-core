# === MEMORY_FILTER_V1 ===
# Жёсткий фильтр памяти — канон §20.3
import re, logging
logger = logging.getLogger(__name__)

_NOISE = [
    "/root/", ".ogg", "Traceback", "traceback",
    "FAILED", "INVALID_RESULT", "STALE_TIMEOUT",
    "не понял", "уточните", "нет данных", "повторите",
    "EXCEPTION", "SyntaxError", "IndentationError",
    "AWAITING_CONFIRMATION без результата",
    "файл скачан, ожидает анализа",
    "структура проекта включает",
]

_MIN_USEFUL_LEN = 20

def is_noise(value: str) -> bool:
    if not value or len(value.strip()) < _MIN_USEFUL_LEN:
        return True
    return any(n in value for n in _NOISE)

def filter_memory_for_prompt(memories: list, query: str = "") -> list:
    """
    Фильтрует записи памяти перед добавлением в промпт.
    memories: list of {"key": str, "value": str}
    """
    clean = []
    query_words = set(w for w in re.split(r"\s+", query.lower()) if len(w) > 3)

    for m in memories:
        val = str(m.get("value", ""))
        if is_noise(val):
            continue
        # relevancy check если есть запрос
        if query_words:
            val_words = set(re.split(r"\s+", val.lower()))
            if query_words & val_words:
                clean.append(m)
        else:
            clean.append(m)

    return clean[:10]  # MEMORY_LIMIT из канона

def sanitize_before_write(value: str) -> str:
    """Очистить строку перед записью в memory.db"""
    if is_noise(value):
        return ""
    # убрать пути
    value = re.sub(r"/root/[\S]+", "[PATH]", value)
    # убрать трейсбэки
    value = re.sub(r"Traceback.*", "", value, flags=re.DOTALL)
    return value[:500].strip()
# === END MEMORY_FILTER_V1 ===
