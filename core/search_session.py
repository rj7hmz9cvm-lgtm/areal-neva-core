# === SEARCH_SESSION_MANAGER_V1 ===
# SearchSessionManager — держит активный поиск в рамках topic
import logging, time
from typing import Optional
logger = logging.getLogger(__name__)

_sessions: dict = {}  # {(chat_id, topic_id): session}

def get_session(chat_id: str, topic_id: int) -> Optional[dict]:
    key = (str(chat_id), int(topic_id or 0))
    s = _sessions.get(key)
    if s and (time.time() - s["ts"]) < 3600:
        return s
    if s:
        del _sessions[key]
    return None

def create_session(chat_id: str, topic_id: int, goal: str, criteria: dict = None) -> dict:
    key = (str(chat_id), int(topic_id or 0))
    s = {
        "goal": goal,
        "criteria": criteria or {},
        "clarifications": [],
        "found": [],
        "rejected": [],
        "final": None,
        "ts": time.time(),
        "status": "ACTIVE",
    }
    _sessions[key] = s
    return s

def update_session(chat_id: str, topic_id: int, **kwargs) -> Optional[dict]:
    key = (str(chat_id), int(topic_id or 0))
    s = _sessions.get(key)
    if not s:
        return None
    s.update(kwargs)
    s["ts"] = time.time()
    return s

def close_session(chat_id: str, topic_id: int):
    key = (str(chat_id), int(topic_id or 0))
    if key in _sessions:
        _sessions[key]["status"] = "CLOSED"

# CriteriaExtractor — минимальный
def extract_criteria(text: str) -> dict:
    import re
    criteria = {}
    # регион
    m = re.search(r"(спб|санкт-петербург|москва|мск|питер|лен\. обл)", text, re.I)
    if m:
        criteria["region"] = m.group(0)
    # новое/б/у
    if "б/у" in text.lower() or "бу " in text.lower():
        criteria["condition"] = "used"
    elif "новое" in text.lower() or "новый" in text.lower():
        criteria["condition"] = "new"
    # цена
    prices = re.findall(r"(\d[\d\s]+)\s*(?:руб|₽)", text)
    if prices:
        criteria["price_hint"] = prices[0]
    return criteria

# QueryExpander
def expand_query(goal: str, criteria: dict) -> list:
    queries = [goal]
    region = criteria.get("region", "")
    if region:
        queries.append(f"{goal} {region}")
        queries.append(f"{goal} купить {region}")
    queries.append(f"{goal} оптом")
    queries.append(f"{goal} производитель")
    return queries[:5]

# SEARCH_PRESETS
SEARCH_PRESETS = {
    "BUILDING_SUPPLY": ["петрович", "леруа", "лемана", "ozon", "avito", "производитель"],
    "AUTO_PARTS":      ["exist", "emex", "zzap", "drom", "avito", "разборка"],
    "CLASSIFIEDS":     ["avito", "юла", "avito.ru"],
    "SOCIAL_GROUPS":   ["vk", "telegram"],
}
# === END SEARCH_SESSION_MANAGER_V1 ===
