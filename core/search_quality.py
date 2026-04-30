# === SEARCH_QUALITY_V1 ===
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# AVAILABILITY_CHECK — проверить что результат содержит реальные данные
def availability_check(result: str) -> bool:
    if not result or len(result.strip()) < 40:
        return False
    bad = ["не нашёл", "не удалось найти", "информация недоступна",
           "нет данных", "данные отсутствуют", "не могу найти"]
    low = result.lower()
    return not any(b in low for b in bad)

# STALE_CONTEXT_GUARD — не использовать результат поиска старше 48ч
def stale_context_guard(search_timestamp: Optional[str], max_age_hours: int = 48) -> bool:
    if not search_timestamp:
        return True
    try:
        from datetime import datetime, timezone
        ts = datetime.fromisoformat(search_timestamp.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        age_h = (now - ts).total_seconds() / 3600
        if age_h > max_age_hours:
            logger.warning("STALE_CONTEXT_GUARD age=%.1fh > %dh", age_h, max_age_hours)
            return False
    except Exception:
        pass
    return True

# NEGATIVE_SELECTION — убрать мусорные результаты
def negative_selection(items: list) -> list:
    noise = ["реклама", "спонсор", "купить сейчас", "акция", "скидка 90%",
             "бесплатно навсегда", "партнёр"]
    clean = []
    for item in items:
        text = str(item).lower()
        if not any(n in text for n in noise):
            clean.append(item)
    return clean

# SOURCE_TRACE — убедиться что есть источник
def source_trace(result: str) -> bool:
    patterns = [r"https?://\S+", r"\bру\b", r"\bwww\b", r"источник", r"по данным"]
    return any(re.search(p, result, re.I) for p in patterns)

# CACHE_LAYER_V1 — простой in-memory кэш поисковых запросов
_search_cache: dict = {}

def cache_get(query: str) -> Optional[str]:
    import time
    entry = _search_cache.get(query)
    if entry and (time.time() - entry["ts"]) < 3600:
        return entry["result"]
    return None

def cache_set(query: str, result: str):
    import time
    _search_cache[query] = {"result": result, "ts": time.time()}
    if len(_search_cache) > 200:
        oldest = sorted(_search_cache, key=lambda k: _search_cache[k]["ts"])[:50]
        for k in oldest:
            del _search_cache[k]

# CONTACT_VALIDATION — есть ли телефон/email
def contact_validation(text: str) -> bool:
    phone = re.search(r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}", text)
    email = re.search(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", text, re.I)
    return bool(phone or email)
# === END SEARCH_QUALITY_V1 ===
