# === SEARCH_SESSION_MANAGER_V1 ===
# SearchSessionManager — держит активный поиск в рамках topic
import logging, time
from typing import Optional
logger = logging.getLogger(__name__)

_sessions: dict = {}  # {(chat_id, topic_id): session}

import sqlite3 as _sqlite3
_MEM_DB = "/root/.areal-neva-core/data/memory.db"

def _db_save_session(chat_id: str, topic_id: int, session: dict):
    # === SEARCH_SESSION_DB_V1 ===
    try:
        import json as _json
        conn = _sqlite3.connect(_MEM_DB)
        conn.execute("CREATE TABLE IF NOT EXISTS memory (chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        key = f"topic_{int(topic_id)}_search_session"
        conn.execute("DELETE FROM memory WHERE chat_id=? AND key=?", (str(chat_id), key))
        conn.execute("INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
                     (str(chat_id), key, _json.dumps(session, ensure_ascii=False)[:5000]))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning("SEARCH_SESSION_DB_SAVE_ERR %s", e)

def _db_load_session(chat_id: str, topic_id: int) -> dict:
    try:
        import json as _json, time as _time
        conn = _sqlite3.connect(_MEM_DB)
        row = conn.execute(
            "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY timestamp DESC LIMIT 1",
            (str(chat_id), f"topic_{int(topic_id)}_search_session")
        ).fetchone()
        conn.close()
        if row:
            d = _json.loads(row[0])
            if _time.time() - d.get("ts", 0) < 3600:
                return d
    except Exception as e:
        logger.warning("SEARCH_SESSION_DB_LOAD_ERR %s", e)
    return {}

def get_session(chat_id: str, topic_id: int) -> Optional[dict]:
    key = (str(chat_id), int(topic_id or 0))
    s = _sessions.get(key)
    if s and (time.time() - s["ts"]) < 3600:
        return s
    if s:
        del _sessions[key]
    # Fallback — читаем из memory.db (персистентность между рестартами)
    db_s = _db_load_session(str(chat_id), int(topic_id or 0))
    if db_s:
        _sessions[key] = db_s
        return db_s
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
    _db_save_session(str(chat_id), int(topic_id or 0), s)
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
