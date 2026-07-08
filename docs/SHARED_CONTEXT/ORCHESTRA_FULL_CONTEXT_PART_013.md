# ORCHESTRA_FULL_CONTEXT_PART_013
generated_at_utc: 2026-07-08T03:00:02.609357+00:00
git_sha_before_commit: be9e5981717241bb8d81d340f82cdbbe9a79db88
part: 13/22


====================================================================================================
BEGIN_FILE: core/search_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: cd8e56b848f77750e2934e99e4e8eff0c1b0d1d908d27a1939cce5e28348ba56
====================================================================================================
# === FULLFIX_SEARCH_ENGINE_STAGE_5 ===
from __future__ import annotations
from typing import Any, Dict, List, Optional

SEARCH_ENGINE_VERSION = "SEARCH_ENGINE_V1"

DIRECTION_SEARCH_PROFILES = {
    "product_search":      {"sources": ["avito", "ozon", "wildberries"], "strategy": "price_compare"},
    "auto_parts_search":   {"sources": ["drom", "exist", "emex", "zzap"], "strategy": "compatibility"},
    "construction_search": {"sources": ["petrovitch", "lerua", "grand_line"], "strategy": "price_delivery"},
    "internet_search":     {"sources": ["web"], "strategy": "general"},
}

DEFAULT_PROFILE = {"sources": ["web"], "strategy": "general"}


class SearchEngine:
    def plan(self, work_item, payload: Dict[str, Any]) -> Dict[str, Any]:
        direction = getattr(work_item, "direction", None) or payload.get("direction") or "internet_search"
        raw_text = (getattr(work_item, "raw_text", "") or payload.get("raw_input") or "")[:500]
        profile = DIRECTION_SEARCH_PROFILES.get(direction, DEFAULT_PROFILE)

        plan = {
            "query": raw_text,
            "direction": direction,
            "sources": profile["sources"],
            "strategy": profile["strategy"],
            "engine_version": SEARCH_ENGINE_VERSION,
            "shadow_mode": True,
            "status": "planned",
        }
        return plan

    def apply_to_payload(self, work_item, payload: Dict[str, Any]) -> Dict[str, Any]:
        requires_search = bool((payload.get("direction_profile") or {}).get("requires_search"))
        if not requires_search:
            return {}
        plan = self.plan(work_item, payload)
        payload["search_plan"] = plan
        try:
            import logging
            logging.getLogger("task_worker").info(
                "FULLFIX_SEARCH_ENGINE_STAGE_5 dir=%s sources=%s strategy=%s",
                plan["direction"], plan["sources"], plan["strategy"]
            )
        except Exception:
            pass
        return plan


def plan_search(work_item, payload):
    return SearchEngine().apply_to_payload(work_item, payload)
# === END FULLFIX_SEARCH_ENGINE_STAGE_5 ===


# === P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1 ===
# Scope:
# - SearchEngine is no longer decorative shadow-only metadata
# - it produces normalized active search plan for product, auto parts, construction and general web search
# - no network call here; execution is handled by SearchMonolithV2 / ai_router online model

import re as _p6se_re

_P6SE_AUTO_WORDS = (
    "сайлентблок", "саленблок", "сальник", "пыльник", "ваз", "2110", "2114",
    "жигули", "лада", "приора", "гранта", "калина", "нива", "drom", "exist", "emex", "zzap",
    "автозапчаст", "запчаст", "oem", "артикул"
)

_P6SE_ELECTRONICS_WORDS = (
    "iphone", "айфон", "pixel", "google pixel", "телефон", "смартфон", "samsung", "galaxy",
    "xiaomi", "redmi", "honor", "huawei", "pro max", "xl"
)

_P6SE_BUILD_WORDS = (
    "утепл", "каменная вата", "rockwool", "бетон", "арматур", "профлист", "металлочереп",
    "фальц", "клик-фальц", "кирпич", "газобетон", "доска", "брус", "стройматериал"
)

def _p6se_s(v, limit=4000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6se_low(v):
    return _p6se_s(v).lower().replace("ё", "е")

def _p6se_direction(raw_text, current="internet_search"):
    low = _p6se_low(raw_text)
    if any(x in low for x in _P6SE_AUTO_WORDS):
        return "auto_parts_search"
    if any(x in low for x in _P6SE_ELECTRONICS_WORDS):
        return "product_search"
    if any(x in low for x in _P6SE_BUILD_WORDS):
        return "construction_search"
    return current or "internet_search"

def _p6se_sources(direction):
    if direction == "auto_parts_search":
        return ["zzap", "exist", "emex", "drom", "auto.ru", "euroauto", "avito", "telegram"]
    if direction == "construction_search":
        return ["petrovich", "lerua", "vseinstrumenti", "ozon", "wildberries", "yandex_market", "avito", "2gis", "supplier_sites"]
    if direction == "product_search":
        return ["ozon", "wildberries", "yandex_market", "dns", "mvideo", "eldorado", "avito", "aliexpress", "official_sites"]
    return ["web", "official_sites", "marketplaces", "classifieds", "2gis"]

def _p6se_strategy(direction):
    if direction == "auto_parts_search":
        return "compatibility_price_availability"
    if direction == "construction_search":
        return "price_delivery_supplier_trust"
    if direction == "product_search":
        return "price_compare_availability"
    return "general_verified_search"

try:
    _p6se_orig_plan = SearchEngine.plan
    def _p6se_plan(self, work_item, payload):
        payload = payload or {}
        raw_text = (
            getattr(work_item, "raw_text", None)
            or payload.get("raw_input")
            or payload.get("normalized_input")
            or payload.get("query")
            or ""
        )
        current = getattr(work_item, "direction", None) or payload.get("direction") or "internet_search"
        direction = _p6se_direction(raw_text, current)
        sources = _p6se_sources(direction)
        plan = {
            "query": _p6se_s(raw_text, 1000),
            "direction": direction,
            "sources": sources,
            "strategy": _p6se_strategy(direction),
            "engine_version": "P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1",
            "shadow_mode": False,
            "status": "active",
            "requires_online": True,
            "must_use_current_query_only": True,
        }
        return plan
    SearchEngine.plan = _p6se_plan

    def _p6se_apply_to_payload(self, work_item, payload):
        payload = payload or {}
        plan = self.plan(work_item, payload)
        payload["search_plan"] = plan
        payload["direction"] = plan["direction"]
        payload["engine"] = "search_supplier"
        payload["requires_search"] = True
        payload["search_sources"] = plan["sources"]
        payload["search_strategy"] = plan["strategy"]
        try:
            import logging
            logging.getLogger("task_worker").info(
                "P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN dir=%s sources=%s strategy=%s",
                plan["direction"], plan["sources"], plan["strategy"]
            )
        except Exception:
            pass
        return plan
    SearchEngine.apply_to_payload = _p6se_apply_to_payload
except Exception:
    pass

# === END_P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1 ===

# === P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1 ===
try:
    SEARCH_ENGINE_VERSION = "P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1"
    DIRECTION_SEARCH_PROFILES.update({
        "internet_search": {"sources": ["web", "marketplaces", "direct_suppliers"], "strategy": "current_query_price_compare"},
        "product_search": {"sources": ["ozon", "wildberries", "yandex_market", "avito", "direct_suppliers"], "strategy": "current_query_price_compare"},
        "auto_parts_search": {"sources": ["drom", "exist", "emex", "zzap", "avito"], "strategy": "current_query_compatibility_price"},
        "construction_search": {"sources": ["petrovich", "lemanapro", "vseinstrumenti", "direct_suppliers"], "strategy": "current_query_price_delivery"},
    })
except Exception:
    pass

try:
    _p6c_orig_plan_20260504 = SearchEngine.plan
    def _p6c_plan_20260504(self, work_item, payload):
        plan = _p6c_orig_plan_20260504(self, work_item, payload)
        plan["shadow_mode"] = False
        plan["status"] = "active"
        plan["engine_version"] = "P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1"
        return plan
    SearchEngine.plan = _p6c_plan_20260504
except Exception:
    pass
# === END_P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1 ===

====================================================================================================
END_FILE: core/search_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/search_quality.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c182a04e79562dc61000856b85d8cd1ac774011ebfcd85972418db2b08982cae
====================================================================================================
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

====================================================================================================
END_FILE: core/search_quality.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/search_session.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: f278acd61bfd629467f60bc8863d44da0d3f64716e5a5c28c647dce8129106b4
====================================================================================================
# === SEARCH_MONOLITH_V2_FULL ===
from __future__ import annotations
import json, logging, os, re, sqlite3, time
import urllib.request, urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("search_session")
BASE = "/root/.areal-neva-core"
MEM_DB = f"{BASE}/data/memory.db"
CORE_DB = f"{BASE}/data/core.db"
SEARCH_SESSION_VERSION = "SEARCH_MONOLITH_V2_FULL"
SESSION_TTL_SEC = 7200
MAX_CLARIFICATIONS = 3
RED_FLAGS = ("цена=1","1 руб","договорная","под заказ","нет телефона","нет адреса","только предоплата","без адреса","нет даты","предоплата 100%")
SEARCH_PROFILES = {
    "BUILDING_SUPPLY": ["Ozon","Wildberries","Яндекс Маркет","Петрович","Лемана","ВсеИнструменты","заводы","Avito","VK","Telegram"],
    "AUTO_PARTS": ["OEM cross","Exist","Emex","ZZap","Drom","Auto.ru","EuroAuto","Avito","разборки","Telegram"],
    "CLASSIFIEDS": ["Avito","Юла","VK","Telegram чаты","2ГИС"],
    "GENERAL": ["официальные сайты","маркетплейсы","Avito","2ГИС"],
}
BUILDING_WORDS = ("металлочереп","монтеррей","профлист","утепл","бетон","арматур","цемент","фанер","доска","брус","кровл","кирпич","газобетон","строй","петрович","лемана","всеинструменты","материал")
AUTO_WORDS = ("oem","артикул","запчаст","суппорт","диск","колод","рычаг","стойк","двигател","коробк","бампер","фара","drom","дром","exist","emex","zzap","авто","машин","разбор")
CLASSIFIED_WORDS = ("авито","avito","юла","б/у","бу","объявлен","частник")

def _utc(): return datetime.now(timezone.utc).isoformat()
def _clean(text, limit=12000):
    if text is None: return ""
    if not isinstance(text, str):
        try: text = json.dumps(text, ensure_ascii=False)
        except: text = str(text)
    return re.sub(r"\n{3,}","\n\n",re.sub(r"[ \t]+"," ",text.replace("\r","\n"))).strip()[:limit]
def _safe_int(v, default=0):
    try: return int(v or 0)
    except: return default

def _assert_online_model_allowed(online_model=None):
    model = (online_model or os.getenv("OPENROUTER_MODEL_ONLINE") or "perplexity/sonar").strip()
    low = model.lower()
    if "deepseek" in low:
        raise RuntimeError("FORBIDDEN_SEARCH_MODEL_DEEPSEEK")
    if model != "perplexity/sonar":
        raise RuntimeError("FORBIDDEN_SEARCH_MODEL_NOT_SONAR")
    return model

@dataclass
class SearchSession:
    chat_id: str; topic_id: int; goal: str
    criteria: Dict[str,Any] = field(default_factory=dict)
    clarifications: List[str] = field(default_factory=list)
    queries: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    best_suppliers: List[Dict[str,Any]] = field(default_factory=list)
    rejected: List[Dict[str,Any]] = field(default_factory=list)
    status: str = "ACTIVE"
    created_at_ts: float = field(default_factory=time.time)
    updated_at: str = field(default_factory=_utc)
    def to_dict(self):
        d = asdict(self); d["version"] = SEARCH_SESSION_VERSION; return d
    @staticmethod
    def from_dict(data):
        return SearchSession(chat_id=str(data.get("chat_id") or ""), topic_id=_safe_int(data.get("topic_id")), goal=str(data.get("goal") or ""), criteria=dict(data.get("criteria") or {}), clarifications=list(data.get("clarifications") or []), queries=list(data.get("queries") or []), sources=list(data.get("sources") or []), best_suppliers=list(data.get("best_suppliers") or []), rejected=list(data.get("rejected") or []), status=str(data.get("status") or "ACTIVE"), created_at_ts=float(data.get("created_at_ts") or time.time()), updated_at=str(data.get("updated_at") or _utc()))

class SearchSessionManager:
    def __init__(self, db_path=MEM_DB):
        self.db_path = db_path; self._ensure()
    def _conn(self):
        c = sqlite3.connect(self.db_path, timeout=20); c.row_factory = sqlite3.Row; return c
    def _ensure(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._conn() as c:
            c.execute("CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_mem_search ON memory(chat_id,key)")
            c.commit()
    def key(self, chat_id, topic_id): return f"topic_{int(topic_id)}_search_session_{chat_id}"
    def get(self, chat_id, topic_id):
        try:
            with self._conn() as c:
                row = c.execute("SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY timestamp DESC LIMIT 1", (str(chat_id), self.key(chat_id, topic_id))).fetchone()
            if not row: return None
            s = SearchSession.from_dict(json.loads(row["value"]))
            if s.status == "CLOSED" or time.time() - float(s.created_at_ts or 0) > SESSION_TTL_SEC: return None
            return s
        except Exception as e: logger.warning("SEARCH_V2_GET_ERR %s", e); return None
    def save(self, s):
        s.updated_at = _utc()
        k = self.key(s.chat_id, s.topic_id)
        v = json.dumps(s.to_dict(), ensure_ascii=False)[:50000]
        with self._conn() as c:
            c.execute("DELETE FROM memory WHERE chat_id=? AND key=?", (s.chat_id, k))
            c.execute("INSERT OR REPLACE INTO memory (id,chat_id,key,value,timestamp) VALUES (?,?,?,?,?)", (f"{s.chat_id}:{k}", s.chat_id, k, v, _utc()))
            c.commit()
    def get_or_create(self, chat_id, topic_id, goal, criteria=None):
        s = self.get(chat_id, topic_id)
        if s:
            if goal and goal != s.goal: s.clarifications.append(goal)
            if criteria: s.criteria.update({k:v for k,v in criteria.items() if v not in ("",None,[],{})})
            self.save(s); return s
        s = SearchSession(chat_id=str(chat_id), topic_id=int(topic_id or 0), goal=goal, criteria=criteria or {})
        self.save(s); return s
    def close(self, chat_id, topic_id):
        s = self.get(chat_id, topic_id)
        if s: s.status = "CLOSED"; self.save(s)

class CriteriaExtractor:
    def extract(self, text):
        t = _clean(text, 4000); low = t.lower(); c = {}
        c["category"] = self.detect_category(low)
        c["target"] = self.extract_target(t)
        r = re.search(r"(санкт-петербург|спб|питер|ленобласть|москва|мск|казань|екатеринбург|новосибирск)", low)
        if r: c["region"] = r.group(0)
        q = re.search(r"(\d+(?:[,.]\d+)?)\s*(шт|м2|м²|м3|м³|кг|т|пог\.?\s*м|п\.м|лист|упак|м\b)", low)
        if q: c["quantity"] = q.group(0)
        p = re.search(r"(?:до|не дороже|бюджет|максимум|за)\s*(\d[\d\s]{2,})\s*(?:руб|₽)?", low)
        if p: c["budget"] = p.group(1).replace(" ","")
        if "б/у" in low or re.search(r"\bбу\b", low): c["condition"] = "used"
        elif "нов" in low: c["condition"] = "new"
        ral = re.search(r"\bral\s*[\- ]?(\d{4})\b", low)
        if ral: c["ral"] = "RAL " + ral.group(1)
        th = re.search(r"(\d[,.]\d{1,2})\s*мм", low)
        if th: c["thickness_mm"] = th.group(1).replace(",",".")
        oem = re.search(r"\b([A-ZА-Я0-9]{4,}[-/ ]?[A-ZА-Я0-9]{2,})\b", t, re.I)
        if c["category"] == "AUTO_PARTS" and oem: c["oem_or_article"] = oem.group(1)
        return {k:v for k,v in c.items() if v not in ("",None,[],{})}
    def detect_category(self, low):
        if any(w in low for w in AUTO_WORDS): return "AUTO_PARTS"
        if any(w in low for w in BUILDING_WORDS): return "BUILDING_SUPPLY"
        if any(w in low for w in CLASSIFIED_WORDS): return "CLASSIFIEDS"
        return "GENERAL"
    def extract_target(self, text):
        t = _clean(text, 500)
        t = re.sub(r"^\[voice\]\s*","",t,flags=re.I)
        t = re.sub(r"^(найди|найти|поищи|поиск|сколько стоит|цена на|стоимость|подбери)\s+","",t,flags=re.I)
        return re.sub(r"\s+"," ",t).strip()[:220]

class ClarificationEngine:
    def ask(self, session):
        c = session.criteria; q = []
        if not c.get("target") or len(str(c.get("target"))) < 4: q.append("что именно искать")
        if c.get("category") == "AUTO_PARTS":
            if not c.get("oem_or_article"): q.append("OEM/артикул или машина/год/кузов")
            if not c.get("condition"): q.append("новое, контрактное или б/у")
            if not c.get("region"): q.append("город или доставка по РФ")
        elif c.get("category") == "BUILDING_SUPPLY":
            if not c.get("region"): q.append("город/район доставки")
            if "металлочереп" in str(c.get("target","")).lower() and not (c.get("ral") and c.get("thickness_mm")): q.append("толщина, RAL и покрытие")
            if not (c.get("quantity") or c.get("budget")): q.append("объём или бюджет")
        else:
            if not c.get("region"): q.append("город или доставка")
        already = len(session.clarifications)
        if already >= MAX_CLARIFICATIONS: return None
        q = q[:max(0, MAX_CLARIFICATIONS - already)]
        if not q: return None
        return "SEARCH_CLARIFICATION_REQUIRED:\n" + "\n".join(f"{i+1}. {x}" for i,x in enumerate(q))

class QueryExpander:
    def expand(self, session):
        goal = session.goal or session.criteria.get("target","")
        cat = session.criteria.get("category","GENERAL")
        region = session.criteria.get("region","")
        sources = SEARCH_PROFILES.get(cat, SEARCH_PROFILES["GENERAL"])
        base_parts = [goal]
        for k in ("ral","thickness_mm","oem_or_article","quantity","condition","budget"):
            if session.criteria.get(k): base_parts.append(str(session.criteria[k]))
        base = " ".join(base_parts).strip()
        queries = [base, f"{base} {region}".strip(), f"{base} купить {region}".strip(), f"{base} цена наличие {region}".strip(), f"{base} доставка {region}".strip()]
        for src in sources: queries.append(f"{base} {src} {region}".strip())
        seen = set(); out = []
        for q in queries:
            q = re.sub(r"\s+"," ",q).strip()
            if q and q.lower() not in seen: seen.add(q.lower()); out.append(q)
        return out[:14]

class SourcePlanner:
    def plan(self, category): return SEARCH_PROFILES.get(category, SEARCH_PROFILES["GENERAL"])

class RiskScorer:
    def score_text(self, text):
        low = text.lower()
        flags = [f for f in RED_FLAGS if f in low]
        has_src = "http" in low or "source_url" in low
        has_date = re.search(r"\b202[4-9]\b", low)
        if has_src and has_date and not flags: status,trust = "CONFIRMED",80
        elif has_src and not flags: status,trust = "PARTIAL",60
        elif flags: status,trust = "RISK",35
        else: status,trust = "UNVERIFIED",40
        return {"status":status,"trust_score":trust,"red_flags":flags}

class TcoCalculator:
    def instruction(self): return "TCO = цена + доставка + комиссия + добор + риск; если данных нет — НЕ ПОДТВЕРЖДЕНО"

class ResultRanker:
    def instruction(self): return "Ранжирование: CHEAPEST, MOST_RELIABLE, BEST_VALUE, FASTEST, RISK_CHEAP, REJECTED"

class SearchOutputFormatter:
    TABLE_HEADER = "Поставщик | Площадка | Тип | Город | Цена | Наличие | Доставка | TCO | Trust Score | Риски | Статус | Ссылка | checked_at"
    def build_prompt(self, session, queries, sources):
        return f"""SEARCH_MONOLITH_V2_FULL
ЦЕЛЬ: {session.goal}
КРИТЕРИИ: {json.dumps(session.criteria,ensure_ascii=False)}
ПЛОЩАДКИ: {", ".join(sources)}
ФОРМУЛИРОВКИ:\n{chr(10).join("- "+q for q in queries)}
ВЫВОД: {self.TABLE_HEADER}
После таблицы: 1.Что брать и почему 2.Что проверить звонком 3.Что отброшено 4.Данные не подтверждены
ПРАВИЛА: Не выдумывать цены/телефоны/адреса. Без source_url/даты — статус не выше PARTIAL. Красные флаги: {", ".join(RED_FLAGS)}""".strip()
    def ensure(self, text, risk):
        text = _clean(text, 12000)
        if self.TABLE_HEADER not in text: text = self.TABLE_HEADER + "\n" + text
        for h in ("1. Что брать и почему","2. Что проверить звонком","3. Что отброшено","4. Данные не подтверждены"):
            if h not in text: text += f"\n\n{h}\nНЕ ПОДТВЕРЖДЕНО"
        text += f"\n\nRiskScorer: {risk.get('status')} | Trust: {risk.get('trust_score')} | flags: {', '.join(risk.get('red_flags') or []) or 'нет'}"
        return text

class SearchMonolithV2:
    def __init__(self):
        self.sessions = SearchSessionManager(); self.extractor = CriteriaExtractor()
        self.clarifier = ClarificationEngine(); self.expander = QueryExpander()
        self.planner = SourcePlanner(); self.risk = RiskScorer()
        self.tco = TcoCalculator(); self.ranker = ResultRanker(); self.formatter = SearchOutputFormatter()
    def has_active_session(self, chat_id, topic_id): return self.sessions.get(chat_id, topic_id) is not None

    # === SEARCH_SESSION_ISOLATION_FIX_V1 ===
    def _is_new_search_goal(self, user_text, existing, extracted):
        low = _clean(user_text, 1000).lower()
        new_markers = ("найди ", "найти ", "поищи ", "поиск ", "подбери ", "сколько стоит ", "цена на ", "стоимость ")
        if not any(low.startswith(m) for m in new_markers):
            return False

        old_target = str((existing.criteria or {}).get("target") or existing.goal or "").lower()
        new_target = str((extracted or {}).get("target") or user_text or "").lower()
        old_cat = str((existing.criteria or {}).get("category") or "")
        new_cat = str((extracted or {}).get("category") or "")

        if old_cat and new_cat and old_cat != new_cat:
            return True

        old_words = set(w for w in re.findall(r"[а-яa-z0-9]{4,}", old_target) if w not in ("найди","найти","поищи","поиск","купить","цена","стоимость"))
        new_words = set(w for w in re.findall(r"[а-яa-z0-9]{4,}", new_target) if w not in ("найди","найти","поищи","поиск","купить","цена","стоимость"))

        if old_words and new_words:
            overlap = len(old_words & new_words)
            if overlap == 0:
                return True
            if overlap / max(1, min(len(old_words), len(new_words))) < 0.35:
                return True

        return False

    async def run(self, payload, user_text, online_call, online_model, base_system_prompt=""):
        chat_id = str(payload.get("chat_id") or ""); topic_id = int(payload.get("topic_id") or 0)
        user_text = _clean(user_text, 4000)
        existing = self.sessions.get(chat_id, topic_id)
        extracted = self.extractor.extract(user_text)

        if existing and self._is_new_search_goal(user_text, existing, extracted):
            try:
                existing.status = "CLOSED"
                self.sessions.save(existing)
                logger.info("SEARCH_SESSION_ISOLATION_FIX_V1 closed_old_session chat=%s topic=%s old_goal=%s new_goal=%s", chat_id, topic_id, existing.goal, user_text)
            except Exception as e:
                logger.warning("SEARCH_SESSION_ISOLATION_FIX_V1_CLOSE_ERR %s", e)
            session = SearchSession(chat_id=str(chat_id), topic_id=int(topic_id or 0), goal=user_text, criteria=extracted)
            self.sessions.save(session)
        elif existing:
            # === SEARCH_SESSION_CLARIFICATION_PRESERVE_FIX_V1 ===
            existing.clarifications.append(user_text)
            _keep = dict(existing.criteria or {})
            _safe_update_keys = ("region", "quantity", "budget", "condition", "ral", "thickness_mm", "oem_or_article")
            for k, v in (extracted or {}).items():
                if v in ("", None, [], {}):
                    continue
                if k in ("category", "target"):
                    if not _keep.get(k):
                        _keep[k] = v
                    continue
                if k in _safe_update_keys:
                    _keep[k] = v
            existing.criteria = _keep
            logger.info("SEARCH_SESSION_CLARIFICATION_PRESERVE_FIX_V1 preserved category=%s target=%s", existing.criteria.get("category"), existing.criteria.get("target"))
            session = existing
            # === END SEARCH_SESSION_CLARIFICATION_PRESERVE_FIX_V1 ===
        else:
            session = self.sessions.get_or_create(chat_id, topic_id, user_text, extracted)
    # === END SEARCH_SESSION_ISOLATION_FIX_V1 ===
        ask = self.clarifier.ask(session)
        if ask: session.status = "WAITING_CLARIFICATION"; self.sessions.save(session); return ask
        session.status = "IN_PROGRESS"
        sources = self.planner.plan(str(session.criteria.get("category") or "GENERAL"))
        queries = self.expander.expand(session)
        session.sources = sources; session.queries = queries; self.sessions.save(session)
        prompt = self.formatter.build_prompt(session, queries, sources)
        system = (base_system_prompt or "") + "\nSEARCH_MONOLITH_V2_FULL_ACTIVE\n" + self.tco.instruction() + "\n" + self.ranker.instruction()
        online_model = _assert_online_model_allowed(online_model)
        raw = await online_call(online_model, [{"role":"system","content":system},{"role":"user","content":prompt}])
        risk = self.risk.score_text(raw)
        final = self.formatter.ensure(raw, risk)
        session.status = "AWAITING_CONFIRMATION"
        session.best_suppliers = [{"summary":final[:1500],"risk":risk,"checked_at":_utc()}]
        self.sessions.save(session); return final

_MONOLITH = SearchMonolithV2()
def has_active_search_session(chat_id, topic_id): return _MONOLITH.has_active_session(str(chat_id), int(topic_id or 0))
def is_search_clarification_output(text): return _clean(text, 200).startswith("SEARCH_CLARIFICATION_REQUIRED:")
async def run_search_monolith_v2(payload, user_text, online_call, online_model, base_system_prompt=""): return await _MONOLITH.run(payload, user_text, online_call, online_model, base_system_prompt)
def get_session(chat_id, topic_id): s = _MONOLITH.sessions.get(str(chat_id), int(topic_id or 0)); return s.to_dict() if s else None
def close_session(chat_id, topic_id): _MONOLITH.sessions.close(str(chat_id), int(topic_id or 0))
def extract_criteria(text): return CriteriaExtractor().extract(text)
SEARCH_PRESETS = SEARCH_PROFILES
# === END SEARCH_MONOLITH_V2_FULL ===


# === REAL_SEARCH_QUALITY_LOGIC_V1 ===
_NEGATIVE_DOMAINS_V1 = ("avito.ru", "dzen.ru", "zen.yandex.ru")

def _negative_selection_v1(results):
    # NEGATIVE_SELECTION_V1
    out = []
    for r in results or []:
        url = ""
        try:
            url = str(r.get("url") or r.get("link") or "")
        except Exception:
            url = str(r or "")
        if any(nd in url.lower() for nd in _NEGATIVE_DOMAINS_V1):
            continue
        out.append(r)
    return out

def _stale_context_guard_v1(payload):
    # STALE_CONTEXT_GUARD_V1
    try:
        ts = None
        if isinstance(payload, dict):
            ts = payload.get("search_context_timestamp") or payload.get("checked_at")
        if not ts:
            return payload
        from datetime import datetime, timezone, timedelta
        ctx_time = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if ctx_time.tzinfo is None:
            ctx_time = ctx_time.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - ctx_time > timedelta(hours=24):
            if isinstance(payload, dict):
                payload = dict(payload)
                payload["search_context"] = None
                payload["stale_context_dropped"] = True
        return payload
    except Exception:
        return payload

def _availability_check_v1(result):
    # AVAILABILITY_CHECK_V1
    try:
        url = str(result.get("url") or result.get("link") or "")
        title = str(result.get("title") or result.get("name") or "")
        return bool(url or title)
    except Exception:
        return bool(result)

try:
    _orig_run_search_monolith_v2_quality_v1 = run_search_monolith_v2
    async def run_search_monolith_v2(*args, **kwargs):
        import inspect
        if "payload" in kwargs and isinstance(kwargs["payload"], dict):
            kwargs["payload"] = _stale_context_guard_v1(kwargs["payload"])
        res = _orig_run_search_monolith_v2_quality_v1(*args, **kwargs)
        if inspect.isawaitable(res):
            res = await res
        if isinstance(res, list):
            return [r for r in _negative_selection_v1(res) if _availability_check_v1(r)]
        if isinstance(res, dict):
            for key in ("results", "items", "offers"):
                if isinstance(res.get(key), list):
                    res[key] = [r for r in _negative_selection_v1(res[key]) if _availability_check_v1(r)]
        return res
except Exception:
    pass

try:
    _orig_run_quality_v1 = run
    async def run(*args, **kwargs):
        import inspect
        if "payload" in kwargs and isinstance(kwargs["payload"], dict):
            kwargs["payload"] = _stale_context_guard_v1(kwargs["payload"])
        res = _orig_run_quality_v1(*args, **kwargs)
        if inspect.isawaitable(res):
            res = await res
        if isinstance(res, list):
            return [r for r in _negative_selection_v1(res) if _availability_check_v1(r)]
        if isinstance(res, dict):
            for key in ("results", "items", "offers"):
                if isinstance(res.get(key), list):
                    res[key] = [r for r in _negative_selection_v1(res[key]) if _availability_check_v1(r)]
        return res
except Exception:
    pass
# === END_REAL_SEARCH_QUALITY_LOGIC_V1 ===


# === PROJECT_SEARCH_FINAL_REGEX_AND_HEADER_FIX_SEARCH_FORMATTER ===
try:
    _SS_FINAL_HEADER = "Поставщик | Площадка | Тип | Город | Цена | Наличие | Доставка | TCO | Trust Score | Риски | Статус | Ссылка | checked_at"
    SearchOutputFormatter.TABLE_HEADER = _SS_FINAL_HEADER
    _ss_orig_ensure = SearchOutputFormatter.ensure

    def _ss_ensure_final(self, text, risk):
        text = _ss_orig_ensure(self, text, risk)
        lines = text.splitlines() if text else []
        first = lines[0] if lines else ""

        if "Поставщик" in first and ("Trust Score" not in first or "checked_at" not in first):
            rest = "\n".join(lines[1:]) if len(lines) > 1 else ""
            text = _SS_FINAL_HEADER + ("\n" + rest if rest else "")

        if _SS_FINAL_HEADER not in text:
            text = _SS_FINAL_HEADER + "\n" + text

        if "checked_at" not in text.lower():
            text += f"\n\nchecked_at: {_utc()}"

        if "Trust Score:" not in text:
            text += f"\n\nTrust Score: {risk.get('trust_score')}"

        return text

    SearchOutputFormatter.ensure = _ss_ensure_final
except Exception:
    pass
# === END_PROJECT_SEARCH_FINAL_REGEX_AND_HEADER_FIX_SEARCH_FORMATTER ===

# === P5_SEARCH_SESSION_VOICE_STALE_CLOSE_20260504_V1 ===
# Runtime overlay only
# Scope:
# - normalize [VOICE] search text before new-goal detection
# - close stale Rockwool/building session when new product/auto/electronics search arrives
# - prevent previous session target from contaminating online prompt
# - no DB schema changes, no forbidden files, no systemd unit changes

try:
    SEARCH_PROFILES.setdefault("ELECTRONICS", ["Ozon", "Wildberries", "Яндекс Маркет", "DNS", "М.Видео", "Эльдорадо", "Avito", "AliExpress", "официальные магазины"])
except Exception:
    pass

_P5_SEARCH_STOP_WORDS = {
    "найди", "найти", "поиск", "поищи", "подбери", "купить", "цена", "стоимость",
    "дешевле", "самый", "самая", "новый", "новое", "нужен", "нужна", "мне",
    "проведи", "соответственно", "если", "такое", "есть", "сообщи", "там",
    "самый", "крутой", "большой", "самого", "самую"
}

_P5_ELECTRONICS_WORDS = (
    "iphone", "айфон", "pixel", "google pixel", "телефон", "смартфон",
    "samsung", "galaxy", "xiaomi", "redmi", "honor", "huawei", "pro max", "xl"
)

_P5_AUTO_EXTRA_WORDS = (
    "сайлентблок", "саленблок", "сальник", "пыльник", "ваз", "2110", "2114",
    "жигули", "лада", "приора", "гранта", "калина", "нива", "автозапчаст"
)

def _p5_norm_text(text):
    s = _clean(text, 4000)
    s = re.sub(r"^\s*\[voice\]\s*", "", s, flags=re.I)
    s = re.sub(r"^\s*(voice|голос|голосовое)\s*[:\-]\s*", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _p5_low(text):
    return _p5_norm_text(text).lower().replace("ё", "е")

def _p5_words(text):
    low = _p5_low(text)
    return set(
        w for w in re.findall(r"[а-яa-z0-9]{3,}", low)
        if w not in _P5_SEARCH_STOP_WORDS
    )

def _p5_category(low):
    if any(x in low for x in _P5_AUTO_EXTRA_WORDS):
        return "AUTO_PARTS"
    if any(x in low for x in _P5_ELECTRONICS_WORDS):
        return "ELECTRONICS"
    if any(w in low for w in AUTO_WORDS):
        return "AUTO_PARTS"
    if any(w in low for w in BUILDING_WORDS):
        return "BUILDING_SUPPLY"
    if any(w in low for w in CLASSIFIED_WORDS):
        return "CLASSIFIEDS"
    return "GENERAL"

try:
    _p5_orig_detect_category = CriteriaExtractor.detect_category
    def _p5_detect_category(self, low):
        cat = _p5_category(str(low or ""))
        if cat:
            return cat
        return _p5_orig_detect_category(self, low)
    CriteriaExtractor.detect_category = _p5_detect_category
except Exception:
    pass

try:
    _p5_orig_extract_target = CriteriaExtractor.extract_target
    def _p5_extract_target(self, text):
        t = _p5_norm_text(text)
        t = re.sub(r"^(найди|найти|поищи|поиск|сколько стоит|цена на|стоимость|подбери|проведи поиск|мне нужен|мне нужна|нужен|нужна)\s+", "", t, flags=re.I)
        return re.sub(r"\s+", " ", t).strip()[:220]
    CriteriaExtractor.extract_target = _p5_extract_target
except Exception:
    pass

def _p5_is_explicit_new_search(text):
    low = _p5_low(text)
    if not low:
        return False
    markers = (
        "найди", "найти", "поищи", "поиск", "подбери", "проведи поиск",
        "мне нужен", "мне нужна", "нужен ", "нужна ", "дешевле", "купить"
    )
    if low.startswith(markers):
        return True
    if any(x in low for x in _P5_ELECTRONICS_WORDS + _P5_AUTO_EXTRA_WORDS) and any(x in low for x in ("найди", "поиск", "дешевле", "купить", "цена", "стоимость", "нужен", "нужна")):
        return True
    return False

def _p5_should_force_new_goal(user_text, existing, extracted):
    new_norm = _p5_norm_text(user_text)
    low = new_norm.lower().replace("ё", "е")
    if not _p5_is_explicit_new_search(new_norm):
        return False

    old_goal = str(getattr(existing, "goal", "") or "")
    old_target = str((getattr(existing, "criteria", {}) or {}).get("target") or old_goal)
    old_low = old_target.lower().replace("ё", "е")
    new_target = str((extracted or {}).get("target") or new_norm)
    old_cat = str((getattr(existing, "criteria", {}) or {}).get("category") or "")
    new_cat = str((extracted or {}).get("category") or _p5_category(low) or "")

    if "rockwool" in old_low or "light buds" in old_low or "light batts" in old_low or "каменная вата" in old_low:
        if any(x in low for x in _P5_AUTO_EXTRA_WORDS + _P5_ELECTRONICS_WORDS):
            return True

    if old_cat and new_cat and old_cat != new_cat:
        return True

    old_words = _p5_words(old_target)
    new_words = _p5_words(new_target)
    if old_words and new_words:
        overlap = len(old_words & new_words)
        ratio = overlap / max(1, min(len(old_words), len(new_words)))
        if overlap == 0 or ratio < 0.35:
            return True

    return False

try:
    _p5_orig_is_new_search_goal = SearchMonolithV2._is_new_search_goal
    def _p5_is_new_search_goal(self, user_text, existing, extracted):
        if _p5_should_force_new_goal(user_text, existing, extracted):
            return True
        return _p5_orig_is_new_search_goal(self, _p5_norm_text(user_text), existing, extracted)
    SearchMonolithV2._is_new_search_goal = _p5_is_new_search_goal
except Exception:
    pass

try:
    _p5_orig_run_search = SearchMonolithV2.run
    async def _p5_run_search(self, payload, user_text, online_call, online_model, base_system_prompt=""):
        payload = dict(payload or {})
        original_text = _clean(user_text, 4000)
        normalized_text = _p5_norm_text(original_text)
        chat_id = str(payload.get("chat_id") or "")
        topic_id = int(payload.get("topic_id") or 0)

        extracted = self.extractor.extract(normalized_text)
        existing = self.sessions.get(chat_id, topic_id)

        if existing and _p5_should_force_new_goal(normalized_text, existing, extracted):
            try:
                old_goal = getattr(existing, "goal", "")
                existing.status = "CLOSED"
                self.sessions.save(existing)
                logger.info(
                    "P5_SEARCH_SESSION_VOICE_STALE_CLOSE closed_old_session chat=%s topic=%s old_goal=%s new_goal=%s",
                    chat_id, topic_id, old_goal, normalized_text
                )
            except Exception as e:
                logger.warning("P5_SEARCH_SESSION_VOICE_STALE_CLOSE_ERR %s", e)

        payload["raw_input"] = normalized_text
        payload["normalized_input"] = normalized_text

        async def _p5_online_call(model, messages):
            clean_messages = []
            for m in messages or []:
                mm = dict(m or {})
                content = str(mm.get("content") or "")
                if "rockwool" in content.lower() or "light buds" in content.lower() or "light batts" in content.lower() or "каменная вата" in content.lower():
                    if any(x in normalized_text.lower().replace("ё", "е") for x in _P5_AUTO_EXTRA_WORDS + _P5_ELECTRONICS_WORDS):
                        content = re.sub(r".*(Rockwool|ROCKWOOL|Light Buds|Light Batts|каменная вата).*\n?", "", content, flags=re.I)
                        content += "\nАКТУАЛЬНЫЙ ЗАПРОС ПОЛЬЗОВАТЕЛЯ: " + normalized_text
                mm["content"] = content
                clean_messages.append(mm)
            return await online_call(model, clean_messages)

        return await _p5_orig_run_search(self, payload, normalized_text, _p5_online_call, online_model, base_system_prompt)
    SearchMonolithV2.run = _p5_run_search
except Exception:
    pass

try:
    _p5_orig_formatter_build_prompt = SearchOutputFormatter.build_prompt
    def _p5_build_prompt(self, session, queries, sources):
        if session and getattr(session, "goal", None):
            session.goal = _p5_norm_text(session.goal)
        return _p5_orig_formatter_build_prompt(self, session, queries, sources)
    SearchOutputFormatter.build_prompt = _p5_build_prompt
except Exception:
    pass

# === END_P5_SEARCH_SESSION_VOICE_STALE_CLOSE_20260504_V1 ===


# === P6_GLOBAL_SEARCH_SESSION_HARD_ISOLATION_20260504_V1 ===
# Scope:
# - every explicit new search starts a clean session
# - vague follow-up may use previous session only when it is really vague
# - stale topic_500 sessions cannot contaminate new auto/electronics/building search
# - output is supplier/result contract, not estimate, not old context
# - no DB schema changes

try:
    SEARCH_PROFILES.setdefault("ELECTRONICS", ["Ozon", "Wildberries", "Яндекс Маркет", "DNS", "М.Видео", "Эльдорадо", "Avito", "AliExpress", "официальные магазины"])
    SEARCH_PROFILES.setdefault("AUTO_PARTS", ["ZZap", "Exist", "Emex", "Drom", "Auto.ru", "EuroAuto", "Avito", "разборки", "Telegram"])
    SEARCH_PROFILES.setdefault("BUILDING_SUPPLY", ["Петрович", "Лемана", "ВсеИнструменты", "Ozon", "Wildberries", "Яндекс Маркет", "Avito", "2ГИС", "официальные поставщики"])
except Exception:
    pass

_P6_SEARCH_STOP_WORDS = {
    "найди", "найти", "поиск", "поищи", "подбери", "купить", "цена", "стоимость",
    "дешевле", "самый", "самая", "новый", "новое", "нужен", "нужна", "мне",
    "проведи", "соответственно", "если", "такое", "есть", "сообщи", "там",
    "варианты", "вариант", "хорошие", "хороший", "пожалуйста"
}

_P6_AUTO_WORDS = (
    "сайлентблок", "саленблок", "сальник", "пыльник", "ваз", "2110", "2114",
    "жигули", "лада", "приора", "гранта", "калина", "нива", "автозапчаст",
    "запчаст", "oem", "артикул", "drom", "exist", "emex", "zzap"
)

_P6_ELECTRONICS_WORDS = (
    "iphone", "айфон", "pixel", "google pixel", "телефон", "смартфон",
    "samsung", "galaxy", "xiaomi", "redmi", "honor", "huawei", "pro max", "xl"
)

_P6_BUILD_WORDS = (
    "rockwool", "роквул", "light batts", "light buds", "каменная вата", "утеплитель",
    "бетон", "арматура", "цемент", "профлист", "металлочерепица", "клик-фальц",
    "фальц", "кирпич", "газобетон", "доска", "брус", "петрович", "лемана"
)

def _p6_norm_text(text):
    s = _clean(text, 4000)
    s = re.sub(r"^\s*\[voice\]\s*", "", s, flags=re.I)
    s = re.sub(r"^\s*(voice|голос|голосовое)\s*[:\-]\s*", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _p6_low(text):
    return _p6_norm_text(text).lower().replace("ё", "е")

def _p6_words(text):
    low = _p6_low(text)
    return set(
        w for w in re.findall(r"[а-яa-z0-9]{3,}", low)
        if w not in _P6_SEARCH_STOP_WORDS
    )

def _p6_category_from_low(low):
    if any(x in low for x in _P6_AUTO_WORDS):
        return "AUTO_PARTS"
    if any(x in low for x in _P6_ELECTRONICS_WORDS):
        return "ELECTRONICS"
    if any(x in low for x in _P6_BUILD_WORDS):
        return "BUILDING_SUPPLY"
    if any(w in low for w in AUTO_WORDS):
        return "AUTO_PARTS"
    if any(w in low for w in BUILDING_WORDS):
        return "BUILDING_SUPPLY"
    if any(w in low for w in CLASSIFIED_WORDS):
        return "CLASSIFIEDS"
    return "GENERAL"

def _p6_is_explicit_new_search(text):
    low = _p6_low(text)
    if not low:
        return False
    if any(x in low for x in ("найди", "найти", "поищи", "поиск", "подбери", "купить", "дешевле", "цена", "стоимость", "мне нужен", "мне нужна", "нужен ", "нужна ")):
        return True
    return any(x in low for x in _P6_AUTO_WORDS + _P6_ELECTRONICS_WORDS + _P6_BUILD_WORDS)

def _p6_is_vague_followup(text):
    low = _p6_low(text)
    if not low:
        return False
    if _p6_is_explicit_new_search(text):
        return False
    return len(low) <= 120 and any(x in low for x in (
        "то что", "то, что", "предыдущ", "прошл", "я тебя про что", "выполни поиск",
        "продолжи", "дальше", "что там", "ну что"
    ))

def _p6_target(text):
    t = _p6_norm_text(text)
    t = re.sub(
        r"^(найди|найти|поищи|поиск|сколько стоит|цена на|стоимость|подбери|проведи поиск|мне нужен|мне нужна|нужен|нужна)\s+",
        "",
        t,
        flags=re.I,
    )
    return re.sub(r"\s+", " ", t).strip()[:260]

def _p6_same_goal(old_text, new_text):
    ow = _p6_words(old_text)
    nw = _p6_words(new_text)
    if not ow or not nw:
        return False
    overlap = len(ow & nw)
    return overlap > 0 and (overlap / max(1, min(len(ow), len(nw)))) >= 0.35

def _p6_force_new_session(user_text, existing, extracted):
    if not existing:
        return True
    if _p6_is_vague_followup(user_text):
        return False
    if _p6_is_explicit_new_search(user_text):
        old_goal = str(getattr(existing, "goal", "") or "")
        old_target = str((getattr(existing, "criteria", {}) or {}).get("target") or old_goal)
        old_cat = str((getattr(existing, "criteria", {}) or {}).get("category") or "")
        new_cat = str((extracted or {}).get("category") or _p6_category_from_low(_p6_low(user_text)) or "")
        if old_cat and new_cat and old_cat != new_cat:
            return True
        if not _p6_same_goal(old_target, user_text):
            return True
    return False

try:
    def _p6_detect_category(self, low):
        return _p6_category_from_low(str(low or ""))
    CriteriaExtractor.detect_category = _p6_detect_category

    def _p6_extract_target(self, text):
        return _p6_target(text)
    CriteriaExtractor.extract_target = _p6_extract_target
except Exception:
    pass

def _p6_patch_criteria(criteria, text):
    c = dict(criteria or {})
    low = _p6_low(text)
    c["category"] = _p6_category_from_low(low)
    c["target"] = _p6_target(text)
    if not c.get("region"):
        if any(x in low for x in ("санкт-петербург", "спб", "питер", "ленобласть")):
            c["region"] = "Санкт-Петербург / Ленобласть"
        elif c["category"] in ("AUTO_PARTS", "ELECTRONICS", "GENERAL", "CLASSIFIEDS"):
            c["region"] = "Россия / доставка"
    return {k: v for k, v in c.items() if v not in ("", None, [], {})}

try:
    _p6_orig_query_expand = QueryExpander.expand
    def _p6_expand(self, session):
        c = session.criteria or {}
        target = str(c.get("target") or session.goal or "")
        region = str(c.get("region") or "")
        category = str(c.get("category") or "GENERAL")
        sources = SEARCH_PROFILES.get(category, SEARCH_PROFILES.get("GENERAL", []))
        base = " ".join(x for x in [
            target,
            str(c.get("oem_or_article") or ""),
            str(c.get("condition") or ""),
            str(c.get("budget") or ""),
        ] if x).strip()
        q = [
            base,
            f"{base} {region}".strip(),
            f"{base} купить {region}".strip(),
            f"{base} цена наличие {region}".strip(),
            f"{base} доставка {region}".strip(),
        ]
        if category == "AUTO_PARTS":
            q += [f"{base} zzap", f"{base} exist", f"{base} emex", f"{base} drom", f"{base} avito"]
        elif category == "ELECTRONICS":
            q += [f"{base} ozon", f"{base} wildberries", f"{base} яндекс маркет", f"{base} avito", f"{base} dns"]
        elif category == "BUILDING_SUPPLY":
            q += [f"{base} петрович", f"{base} лемана", f"{base} всеинструменты", f"{base} avito", f"{base} 2гис"]
        for src in sources:
            q.append(f"{base} {src} {region}".strip())
        out, seen = [], set()
        for x in q:
            x = re.sub(r"\s+", " ", str(x)).strip()
            k = x.lower()
            if x and k not in seen:
                seen.add(k)
                out.append(x)
        return out[:16]
    QueryExpander.expand = _p6_expand
except Exception:
    pass

try:
    _p6_orig_plan_sources = SourcePlanner.plan
    def _p6_plan_sources(self, category):
        category = str(category or "GENERAL")
        return SEARCH_PROFILES.get(category, SEARCH_PROFILES.get("GENERAL", ["официальные сайты", "маркетплейсы", "Avito", "2ГИС"]))
    SourcePlanner.plan = _p6_plan_sources
except Exception:
    pass

try:
    def _p6_build_prompt(self, session, queries, sources):
        c = session.criteria or {}
        return f"""P6_GLOBAL_SEARCH_SESSION_HARD_ISOLATION_ACTIVE
АКТУАЛЬНЫЙ ЗАПРОС: {session.goal}
КАТЕГОРИЯ: {c.get('category','GENERAL')}
ЦЕЛЬ: {c.get('target', session.goal)}
РЕГИОН: {c.get('region','Россия / доставка')}
ПЛОЩАДКИ: {", ".join(sources)}
ПОИСКОВЫЕ ФОРМУЛИРОВКИ:
{chr(10).join("- " + q for q in queries)}

ЖЁСТКИЕ ПРАВИЛА:
1. Используй только АКТУАЛЬНЫЙ ЗАПРОС
2. Не используй старые цели, старые товары, Rockwool/каменная вата, если их нет в актуальном запросе
3. Не составляй смету
4. Не создавай XLSX/PDF
5. Не выдавай общие советы
6. Нужны реальные варианты покупки или честно напиши, что подтверждённых вариантов нет
7. Каждая строка должна иметь ссылку
8. Если цена/телефон/наличие не видны — так и пиши

ФОРМАТ:
Найдено: <N> вариантов

| № | Поставщик | Площадка | Товар | Город/регион | Цена | Наличие | Доставка | Телефон | Ссылка | Риск |
|---|-----------|----------|-------|--------------|------|---------|----------|---------|--------|------|

Лучший вариант:
<одна строка>

Проверить звонком:
1. актуальная цена
2. наличие
3. доставка
4. НДС/счёт
5. точная модель/артикул/совместимость

Отброшено:
- <кратко, если есть>
""".strip()
    SearchOutputFormatter.build_prompt = _p6_build_prompt
except Exception:
    pass

try:
    _p6_orig_ensure = SearchOutputFormatter.ensure
    def _p6_ensure(self, text, risk):
        t = _clean(text, 12000)
        bad = ("смета готова", "предварительная смета готова", "xlsx:", "pdf:", "engine:", "м-110.xlsx", "ареал нева.xlsx")
        if any(x in t.lower().replace("ё", "е") for x in bad):
            return "Поиск заблокирован: маршрут вернул сметный результат вместо поиска"
        if "Найдено:" not in t and "| № |" not in t:
            t = "Найдено: результат требует проверки\n\n" + t
        if "Проверить звонком:" not in t:
            t += "\n\nПроверить звонком:\n1. актуальная цена\n2. наличие\n3. доставка\n4. НДС/счёт\n5. точная модель/артикул/совместимость"
        return _clean(t, 12000)
    SearchOutputFormatter.ensure = _p6_ensure
except Exception:
    pass

try:
    async def _p6_run_search(self, payload, user_text, online_call, online_model, base_system_prompt=""):
        payload = dict(payload or {})
        chat_id = str(payload.get("chat_id") or "")
        topic_id = int(payload.get("topic_id") or 0)
        normalized = _p6_norm_text(user_text)
        existing = self.sessions.get(chat_id, topic_id)
        extracted = _p6_patch_criteria(self.extractor.extract(normalized), normalized)

        if existing and _p6_is_vague_followup(normalized):
            goal = str(getattr(existing, "goal", "") or normalized)
            merged = dict(getattr(existing, "criteria", {}) or {})
            for k, v in extracted.items():
                if k not in ("target", "category") and v not in ("", None, [], {}):
                    merged[k] = v
            session = existing
            session.clarifications.append(normalized)
            session.criteria = merged
        else:
            if existing and _p6_force_new_session(normalized, existing, extracted):
                try:
                    existing.status = "CLOSED"
                    self.sessions.save(existing)
                    logger.info("P6_GLOBAL_SEARCH_SESSION_CLOSED_OLD chat=%s topic=%s old_goal=%s new_goal=%s", chat_id, topic_id, existing.goal, normalized)
                except Exception as e:
                    logger.warning("P6_GLOBAL_SEARCH_SESSION_CLOSE_ERR %s", e)
            session = SearchSession(chat_id=str(chat_id), topic_id=int(topic_id or 0), goal=normalized, criteria=extracted)

        session.criteria = _p6_patch_criteria(session.criteria, session.goal)
        session.status = "IN_PROGRESS"
        sources = self.planner.plan(str(session.criteria.get("category") or "GENERAL"))
        queries = self.expander.expand(session)
        session.sources = sources
        session.queries = queries
        self.sessions.save(session)

        prompt = self.formatter.build_prompt(session, queries, sources)
        system = (base_system_prompt or "") + "\nP6_GLOBAL_SEARCH_SESSION_ACTIVE\nCURRENT_QUERY_ONLY\nNO_ESTIMATE_NO_XLSX_NO_PDF"
        online_model = _assert_online_model_allowed(online_model)
        raw = await online_call(online_model, [{"role": "system", "content": system}, {"role": "user", "content": prompt}])
        risk = self.risk.score_text(raw)
        final = self.formatter.ensure(raw, risk)

        qlow = _p6_low(session.goal)
        flow = final.lower().replace("ё", "е")
        stale_pairs = (
            ("rockwool", ("сальник", "сайлент", "саленблок", "iphone", "pixel", "телефон", "2110", "2114")),
            ("каменная вата", ("сальник", "сайлент", "саленблок", "iphone", "pixel", "телефон", "2110", "2114")),
            ("light batts", ("сальник", "сайлент", "саленблок", "iphone", "pixel", "телефон", "2110", "2114")),
            ("термодом", ("сальник", "сайлент", "саленблок", "iphone", "pixel", "телефон", "2110", "2114")),
        )
        for stale, actual_markers in stale_pairs:
            if stale in flow and stale not in qlow and any(x in qlow for x in actual_markers):
                final = "Поиск заблокирован: ответ содержит старый товар из другой поисковой сессии. Повтори запрос одной строкой с товаром и регионом"
                break

        session.status = "AWAITING_CONFIRMATION"
        session.best_suppliers = [{"summary": final[:1500], "risk": risk, "checked_at": _utc()}]
        self.sessions.save(session)
        logger.info("P6_GLOBAL_SEARCH_SESSION_DONE chat=%s topic=%s category=%s chars=%s", chat_id, topic_id, session.criteria.get("category"), len(final))
        return final

    SearchMonolithV2.run = _p6_run_search
except Exception:
    pass

# === END_P6_GLOBAL_SEARCH_SESSION_HARD_ISOLATION_20260504_V1 ===

# === P6B_SEARCH_SESSION_NO_STALE_CONTEXT_FINAL_20260504_V1 ===
# Runtime overlay only
# Scope:
# - final SearchMonolithV2.run override
# - current query only for explicit new product/auto/electronics searches
# - stale Rockwool/building session cannot contaminate auto/electronics prompts
# - no DB schema changes, no forbidden files, no systemd unit changes

_P6B_STALE_WORDS = (
    "rockwool", "rockwool light", "light buds", "light batts", "лайт баттс",
    "каменная вата", "минвата", "утеплитель", "термодом", "minvata",
    "www-minvata", "petrovich", "петрович", "лемана", "стройматериал"
)

_P6B_ELECTRONICS_WORDS = (
    "iphone", "айфон", "pixel", "google pixel", "телефон", "смартфон",
    "samsung", "galaxy", "xiaomi", "redmi", "honor", "huawei", "pro max", "xl"
)

_P6B_AUTO_WORDS = (
    "сайлентблок", "саленблок", "сальник", "пыльник", "ваз", "2110", "2114",
    "жигули", "лада", "приора", "гранта", "калина", "нива", "автозапчаст",
    "шрус", "рычаг", "суппорт", "колодки", "стойка", "амортизатор"
)

_P6B_SEARCH_VERBS = (
    "найди", "найти", "поищи", "поиск", "подбери", "проведи поиск",
    "мне нужен", "мне нужна", "нужен", "нужна", "дешевле", "купить",
    "цена", "стоимость", "сколько стоит"
)

_P6B_STOP_WORDS = {
    "найди", "найти", "поиск", "поищи", "подбери", "купить", "цена", "стоимость",
    "дешевле", "самый", "самая", "новый", "новое", "нужен", "нужна", "мне",
    "проведи", "соответственно", "если", "такое", "есть", "сообщи", "там",
    "самого", "самую", "большой", "крутой", "для", "всех", "интернет", "площадках"
}

def _p6b_norm(text):
    s = _clean(text, 4000)
    s = re.sub(r"^\s*\[voice\]\s*", "", s, flags=re.I)
    s = re.sub(r"^\s*(voice|голос|голосовое)\s*[:\-]\s*", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _p6b_low(text):
    return _p6b_norm(text).lower().replace("ё", "е")

def _p6b_words(text):
    low = _p6b_low(text)
    return {
        w for w in re.findall(r"[а-яa-z0-9]{3,}", low)
        if w not in _P6B_STOP_WORDS
    }

def _p6b_category(text):
    low = _p6b_low(text)
    if any(x in low for x in _P6B_AUTO_WORDS):
        return "AUTO_PARTS"
    if any(x in low for x in _P6B_ELECTRONICS_WORDS):
        return "ELECTRONICS"
    if any(x in low for x in AUTO_WORDS):
        return "AUTO_PARTS"
    if any(x in low for x in BUILDING_WORDS):
        return "BUILDING_SUPPLY"
    if any(x in low for x in CLASSIFIED_WORDS):
        return "CLASSIFIEDS"
    return "GENERAL"

def _p6b_explicit_new_search(text):
    low = _p6b_low(text)
    if not low:
        return False
    if any(low.startswith(v) for v in _P6B_SEARCH_VERBS):
        return True
    if any(x in low for x in _P6B_AUTO_WORDS + _P6B_ELECTRONICS_WORDS) and any(v in low for v in _P6B_SEARCH_VERBS):
        return True
    return False

def _p6b_force_new(existing, current_text, extracted):
    if not existing:
        return False
    if not _p6b_explicit_new_search(current_text):
        return False

    old_goal = str(getattr(existing, "goal", "") or "")
    old_criteria = getattr(existing, "criteria", {}) or {}
    old_target = str(old_criteria.get("target") or old_goal)
    old_low = old_target.lower().replace("ё", "е")

    new_cat = str((extracted or {}).get("category") or _p6b_category(current_text) or "")
    old_cat = str(old_criteria.get("category") or "")

    if any(x in old_low for x in _P6B_STALE_WORDS) and new_cat in ("AUTO_PARTS", "ELECTRONICS"):
        return True

    if old_cat and new_cat and old_cat != new_cat:
        return True

    old_words = _p6b_words(old_target)
    new_words = _p6b_words(current_text)
    if old_words and new_words:
        overlap = len(old_words & new_words)
        ratio = overlap / max(1, min(len(old_words), len(new_words)))
        if overlap == 0 or ratio < 0.30:
            return True

    return False

def _p6b_scrub_stale_from_text(content, current_text):
    s = str(content or "")
    cur_low = _p6b_low(current_text)
    current_is_building = _p6b_category(current_text) == "BUILDING_SUPPLY"
    if current_is_building:
        return s

    if not any(x in s.lower().replace("ё", "е") for x in _P6B_STALE_WORDS):
        return s

    clean_lines = []
    for line in s.splitlines():
        low = line.lower().replace("ё", "е")
        if any(x in low for x in _P6B_STALE_WORDS):
            continue
        clean_lines.append(line)

    out = "\n".join(clean_lines).strip()
    out += "\n\nАКТУАЛЬНЫЙ ЗАПРОС ПОЛЬЗОВАТЕЛЯ, ЕДИНСТВЕННЫЙ ИСТОЧНИК ПОИСКА: " + _p6b_norm(current_text)
    return out

def _p6b_target(text):
    t = _p6b_norm(text)
    t = re.sub(
        r"^(найди|найти|поищи|поиск|сколько стоит|цена на|стоимость|подбери|проведи поиск|мне нужен|мне нужна|нужен|нужна)\s+",
        "",
        t,
        flags=re.I,
    )
    return re.sub(r"\s+", " ", t).strip()[:220]

try:
    _p6b_orig_detect_category = CriteriaExtractor.detect_category
    def _p6b_detect_category(self, low):
        return _p6b_category(str(low or ""))
    CriteriaExtractor.detect_category = _p6b_detect_category
except Exception:
    pass

try:
    _p6b_orig_extract_target = CriteriaExtractor.extract_target
    def _p6b_extract_target(self, text):
        return _p6b_target(text)
    CriteriaExtractor.extract_target = _p6b_extract_target
except Exception:
    pass

async def _p6b_run_search_final(self, payload, user_text, online_call, online_model, base_system_prompt=""):
    payload = dict(payload or {})
    chat_id = str(payload.get("chat_id") or "")
    topic_id = int(payload.get("topic_id") or 0)
    normalized = _p6b_norm(user_text or payload.get("raw_input") or payload.get("normalized_input") or "")
    if not normalized:
        normalized = _p6b_norm(user_text)

    extracted = self.extractor.extract(normalized)
    extracted["category"] = _p6b_category(normalized)
    extracted["target"] = _p6b_target(normalized)

    if not extracted.get("region"):
        extracted["region"] = "Санкт-Петербург / РФ"

    existing = self.sessions.get(chat_id, topic_id)

    if existing and _p6b_force_new(existing, normalized, extracted):
        try:
            existing.status = "CLOSED"
            self.sessions.save(existing)
            logger.info(
                "P6B_SEARCH_SESSION_CLOSED_STALE chat=%s topic=%s old_goal=%s new_goal=%s",
                chat_id,
                topic_id,
                getattr(existing, "goal", ""),
                normalized,
            )
        except Exception as e:
            logger.warning("P6B_SEARCH_SESSION_CLOSE_ERR %s", e)
        existing = None

    if existing and not _p6b_explicit_new_search(normalized):
        session = existing
        session.clarifications.append(normalized)
        safe_update = dict(session.criteria or {})
        for k, v in (extracted or {}).items():
            if v in ("", None, [], {}):
                continue
            if k in ("region", "quantity", "budget", "condition", "ral", "thickness_mm", "oem_or_article"):
                safe_update[k] = v
        session.criteria = safe_update
    else:
        session = SearchSession(chat_id=str(chat_id), topic_id=int(topic_id or 0), goal=normalized, criteria=extracted)

    session.status = "IN_PROGRESS"
    sources = self.planner.plan(str(session.criteria.get("category") or "GENERAL"))
    queries = self.expander.expand(session)

    if session.criteria.get("category") == "AUTO_PARTS":
        sources = ["Exist", "Emex", "ZZap", "Drom", "Auto.ru", "EuroAuto", "Avito", "разборки", "официальные каталоги"]
    elif session.criteria.get("category") == "ELECTRONICS":
        sources = ["Ozon", "Wildberries", "Яндекс Маркет", "DNS", "М.Видео", "Эльдорадо", "Avito", "AliExpress", "официальные магазины"]

    session.sources = sources
    session.queries = queries
    self.sessions.save(session)

    prompt = self.formatter.build_prompt(session, queries, sources)
    prompt = _p6b_scrub_stale_from_text(prompt, normalized)

    system = "\n".join([
        base_system_prompt or "",
        "P6B_SEARCH_SESSION_NO_STALE_CONTEXT_FINAL_ACTIVE",
        "CURRENT_QUERY_ONLY",
        "USE ONLY CURRENT USER QUERY AND CURRENT CRITERIA",
        "IGNORE OLD SEARCH SESSIONS, OLD SUPPLIERS, OLD MEMORY, OLD BUILDING MATERIAL CONTEXT",
        "FORBIDDEN: estimate, смета, XLSX, PDF, проектные расчёты",
        self.tco.instruction(),
        self.ranker.instruction(),
    ])

    async def _p6b_online_call(model, messages):
        clean_messages = []
        for m in messages or []:
            mm = dict(m or {})
            mm["content"] = _p6b_scrub_stale_from_text(mm.get("content") or "", normalized)
            clean_messages.append(mm)
        joined = "\n".join(str(x.get("content") or "") for x in clean_messages)
        jlow = joined.lower().replace("ё", "е")
        if _p6b_category(normalized) in ("AUTO_PARTS", "ELECTRONICS"):
            if any(x in jlow for x in _P6B_STALE_WORDS):
                raise RuntimeError("P6B_STALE_CONTEXT_BLOCKED_BEFORE_ONLINE_CALL")
        return await online_call(model, clean_messages)

    raw = await _p6b_online_call(
        online_model,
        [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )

    if _p6b_category(normalized) in ("AUTO_PARTS", "ELECTRONICS"):
        rlow = str(raw or "").lower().replace("ё", "е")
        if any(x in rlow for x in _P6B_STALE_WORDS):
            raw = "Подтверждённых вариантов по актуальному запросу не получено без загрязнения старым контекстом. Повтори запрос с артикулом/OEM или точной моделью"

    risk = self.risk.score_text(str(raw or ""))
    final = self.formatter.ensure(str(raw or ""), risk)
    session.status = "AWAITING_CONFIRMATION"
    session.best_suppliers = [{"summary": final[:1500], "risk": risk, "checked_at": _utc()}]
    self.sessions.save(session)
    logger.info(
        "P6B_SEARCH_SESSION_DONE chat=%s topic=%s category=%s chars=%s",
        chat_id,
        topic_id,
        session.criteria.get("category"),
        len(final),
    )
    return final

try:
    SearchMonolithV2.run = _p6b_run_search_final
except Exception:
    pass

try:
    _p6b_orig_formatter_prompt = SearchOutputFormatter.build_prompt
    def _p6b_build_prompt(self, session, queries, sources):
        if session and getattr(session, "goal", None):
            session.goal = _p6b_norm(session.goal)
        text = _p6b_orig_formatter_prompt(self, session, queries, sources)
        return _p6b_scrub_stale_from_text(text, getattr(session, "goal", "") if session else "")
    SearchOutputFormatter.build_prompt = _p6b_build_prompt
except Exception:
    pass

# === END_P6B_SEARCH_SESSION_NO_STALE_CONTEXT_FINAL_20260504_V1 ===

# === P6C_SEARCH_CURRENT_QUERY_ONLY_NO_STALE_CONTEXT_20260504_V1 ===
import re as _p6c_re

def _p6c_clean_text_20260504(text, limit=4000):
    try:
        s = _clean(text, limit)
    except Exception:
        s = str(text or "")[:limit]
    s = _p6c_re.sub(r"^\s*\[VOICE\]\s*", "", s, flags=_p6c_re.I)
    s = _p6c_re.sub(r"^\s*(voice|голос|голосовое)\s*[:\-]\s*", "", s, flags=_p6c_re.I)
    s = _p6c_re.sub(r"\s+", " ", s).strip()
    return s[:limit]

def _p6c_low_20260504(text):
    return _p6c_clean_text_20260504(text).lower().replace("ё", "е")

def _p6c_category_20260504(text):
    low = _p6c_low_20260504(text)
    if any(x in low for x in ("сайлентблок", "саленблок", "сальник", "пыльник", "ваз", "2110", "2114", "лада", "жигули", "автозапчаст", "drom", "exist", "emex", "zzap")):
        return "AUTO_PARTS", "drom, exist, emex, zzap, avito, профильные магазины автозапчастей"
    if any(x in low for x in ("iphone", "айфон", "pixel", "google pixel", "телефон", "смартфон", "samsung", "galaxy", "xiaomi", "redmi", "honor", "huawei")):
        return "ELECTRONICS", "ozon, wildberries, яндекс маркет, dns, мвидео, эльдорадо, avito, официальные магазины"
    if any(x in low for x in ("вата", "утеплитель", "rockwool", "light batts", "light buds", "бетон", "арматур", "пиломатериал")):
        return "BUILDING_SUPPLY", "петрович, лемана про, всеинструменты, профильные поставщики, avito"
    return "GENERAL", "официальные сайты, маркетплейсы, avito, профильные магазины"

def _p6c_messages_20260504(query):
    q = _p6c_clean_text_20260504(query, 2500)
    cat, sources = _p6c_category_20260504(q)
    system = (
        "Ты выполняешь только товарный интернет-поиск по текущему запросу пользователя. "
        "Не используй старые задачи, память, архив, прошлые товары и прошлые ответы. "
        "Нужны реальные варианты покупки, цены, наличие, доставка и прямые ссылки."
    )
    user = (
        "Текущий запрос пользователя:\n"
        f"{q}\n\n"
        f"Категория: {cat}\n"
        f"Где проверять: {sources}\n\n"
        "Ответ строго таблицей:\n"
        "№ | Площадка/поставщик | Товар | Город/регион | Цена | Наличие | Доставка | Телефон | Прямая ссылка | Риск\n"
        "Минимум 3 варианта, если они реально существуют. Если подтверждённых вариантов нет, так и напиши."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]

try:
    _p6c_prev_run_20260504 = SearchMonolithV2.run

    async def _p6c_run_20260504(self, payload, user_text, online_call, online_model, base_system_prompt=""):
        payload = dict(payload or {})
        query = _p6c_clean_text_20260504(user_text or payload.get("raw_input") or payload.get("normalized_input") or "", 3000)
        chat_id = str(payload.get("chat_id") or "")
        topic_id = int(payload.get("topic_id") or 0)

        try:
            existing = self.sessions.get(chat_id, topic_id)
            if existing:
                existing.status = "CLOSED"
                self.sessions.save(existing)
        except Exception:
            pass

        payload["raw_input"] = query
        payload["normalized_input"] = query
        payload["active_task_context"] = ""
        payload["pin_context"] = ""
        payload["short_memory_context"] = ""
        payload["long_memory_context"] = ""
        payload["archive_context"] = ""
        payload["search_context"] = ""

        online_model = _assert_online_model_allowed(online_model)
        raw = await online_call(online_model, _p6c_messages_20260504(query))
        try:
            final = _clean(raw, 12000)
        except Exception:
            final = str(raw or "")[:12000]
        if not final.strip():
            final = "Подтверждённых вариантов по текущему запросу не найдено"
        try:
            logger.info("P6C_SEARCH_CURRENT_QUERY_ONLY_DONE chat=%s topic=%s chars=%s", chat_id, topic_id, len(final))
        except Exception:
            pass
        return final

    SearchMonolithV2.run = _p6c_run_20260504
except Exception:
    pass

try:
    def run_search_monolith_v2(payload, user_text, online_call, online_model, base_system_prompt=""):
        online_model = _assert_online_model_allowed(online_model)
        return _MONOLITH.run(payload, user_text, online_call, online_model, base_system_prompt)
except Exception:
    pass
# === END_P6C_SEARCH_CURRENT_QUERY_ONLY_NO_STALE_CONTEXT_20260504_V1 ===

# === P6E2_SEARCH_CURRENT_QUERY_HARD_NO_STALE_NO_ESTIMATE_POLLUTION_20260504_V1 ===
import re as _p6e2_search_re

def _p6e2_search_s(v, limit=5000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6e2_search_low(v):
    return _p6e2_search_s(v).lower().replace("ё", "е")

def _p6e2_search_category(q):
    low = _p6e2_search_low(q)
    if any(x in low for x in ("ваз", "2110", "2114", "сайлент", "саленблок", "сальник", "пыльник", "автозапчаст", "drom", "exist", "emex", "zzap")):
        return "AUTO_PARTS", "drom, exist, emex, zzap, avito, auto.ru, профильные магазины"
    if any(x in low for x in ("iphone", "айфон", "pixel", "телефон", "смартфон", "samsung", "xiaomi", "honor", "ноутбук")):
        return "ELECTRONICS", "ozon, wildberries, яндекс маркет, dns, мвидео, avito, официальные магазины"
    if any(x in low for x in ("бетон", "арматур", "пиломатериал", "утеплитель", "rockwool", "плита", "стройматериал")):
        return "BUILDING_SUPPLY", "петрович, лемана про, всеинструменты, профильные поставщики, avito"
    return "GENERAL", "официальные сайты, маркетплейсы, avito, профильные поставщики"

def _p6e2_search_messages(q):
    cat, sources = _p6e2_search_category(q)
    user = f"""АКТУАЛЬНЫЙ ЗАПРОС:
{_p6e2_search_s(q, 2500)}

Категория: {cat}
Искать только по текущему запросу
Площадки: {sources}

Сначала определи режим: procurement / service-local / factual / normative / technical / news / comparison.

Для procurement/service-local верни только чистую выдачу контактов без пояснительных комментариев:
Profile/поставщик | Сайт/ссылка | Телефон | Цена/условия | Город/регион | Доставка/выезд | Дата проверки | Статус проверки

Правила источников:
- Дата проверки обязательна для каждой строки.
- Статус проверки: подтверждено / частично проверено / не подтверждено / риск.
- Телефон обязателен. Если прямой телефон не найден, строку помечай "не подтверждено" и пиши "телефон не найден".
- Ссылка должна вести на сайт, профиль, карточку, объявление или страницу поставщика/исполнителя.
- Лишние комментарии, рекомендации, блоки "что проверить", "риски" и внутренние пояснения не выводить.
- "Подтверждено" разрешено только при прямой проверке источника, даты и ссылки.
- Если нет даты, контакта, цены или прямого подтверждения, ставь "частично проверено" или "не подтверждено".
- Не используй англоязычные статусы CONFIRMED/PARTIAL/UNVERIFIED/RISK в публичном ответе.
- Не используй колонку "Проверено" и не пиши "Да" вместо статуса проверки.
- Запрещено возвращать старые товары, сметы, Excel, PDF, строительные позиции из другого запроса.
- Запрещены fake links, invented prices, invented source names."""
    system = (
        "CURRENT_QUERY_ONLY. NO_STALE_CONTEXT. NO_ESTIMATE_OUTPUT. NO_INTERNAL_MARKERS. "
        "TOPIC_500_UNIVERSAL_SEARCH_CANON. INTERNET_SEARCH_ONLY_SONAR. "
        "NO_FAKE_LINKS. NO_INVENTED_PRICES. CHECKED_AT_AND_SOURCE_STATUS_REQUIRED."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]

def _p6e2_apply_universal_search_canon(final):
    text = _p6e2_search_s(final, 12000)
    if not text:
        return text
    checked_at = _utc()
    text = text.replace("Поставщик | Площадка | Город | Цена | Наличие | Доставка | Ссылка | Проверено",
                        "Profile/поставщик | Сайт/ссылка | Телефон | Цена/условия | Город/регион | Доставка/выезд | Дата проверки | Статус проверки")
    text = text.replace("Поставщик/исполнитель | Площадка | Город/регион | Цена | Наличие/условия | Доставка | Контакт | Ссылка | Дата проверки | Статус проверки | Риски",
                        "Profile/поставщик | Сайт/ссылка | Телефон | Цена/условия | Город/регион | Доставка/выезд | Дата проверки | Статус проверки")
    text = text.replace("checked_at", "Дата проверки").replace("source_status", "Статус проверки")
    text = re.sub(r"\s*\|\s*Проверено\s*$", " | Дата проверки | Статус проверки", text, flags=re.I | re.M)
    text = re.sub(r"\s*\|\s*Да\s*$", f" | {checked_at} | частично проверено", text, flags=re.I | re.M)
    text = re.sub(r"\s*\|\s*Нет\s*$", f" | {checked_at} | не подтверждено", text, flags=re.I | re.M)
    text = re.split(
        r"\n\s*(?:Что брать|Что проверить|Что отброшено|Данные не подтверждены|Рекомендац|Комментар|Риски)\b",
        text,
        maxsplit=1,
        flags=re.I,
    )[0].rstrip()
    replacements = {
        "CONFIRMED": "частично проверено",
        "PARTIAL": "частично проверено",
        "UNVERIFIED": "не подтверждено",
        "RISK": "риск",
    }
    for src, dst in replacements.items():
        text = re.sub(rf"\b{src}\b", dst, text, flags=re.I)
    return _p6e2_search_s(text, 12000)

def _p6e2_norm_phone(value):
    digits = re.sub(r"\D+", "", str(value or ""))
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    return digits if len(digits) >= 10 else ""

def _p6e2_is_placeholder_phone(phone):
    digits = _p6e2_norm_phone(phone)
    if not digits:
        return False
    tail = digits[-7:]
    if tail in {"1234567", "1111111", "2222222", "3333333", "4444444", "5555555", "6666666", "7777777", "8888888", "9999999", "0000000"}:
        return True
    if re.search(r"(\d)\1{5,}", tail):
        return True
    return False

def _p6e2_dedupe_contacts(text):
    lines = str(text or "").splitlines()
    seen = {}
    out = []
    phone_re = re.compile(r"(?:\+7|8)\s*[\(\- ]?\d{3}[\)\- ]?\s*\d{3}[\- ]?\d{2}[\- ]?\d{2}")
    for line in lines:
        phones = [_p6e2_norm_phone(x) for x in phone_re.findall(line)]
        phones = [x for x in phones if x]
        if not phones:
            out.append(line)
            continue
        if any(_p6e2_is_placeholder_phone(x) for x in phones):
            continue
        key = phones[0]
        if key in seen:
            seen[key]["count"] += 1
            seen[key]["sources"].append(line.strip())
            continue
        seen[key] = {"count": 1, "sources": [line.strip()]}
        out.append(line)
    duplicate_notes = []
    for phone, data in seen.items():
        if data["count"] > 1:
            duplicate_notes.append(f"DUPLICATE_CONTACT: +{phone} встречается в {data['count']} строках; оставлен один профиль, остальные объявления считаются дублями")
    if duplicate_notes:
        out.append("")
        out.extend(duplicate_notes)
    return "\n".join(out).strip()

def _p6e2_extract_urls(line):
    urls = re.findall(r"https?://[^\s\]\)>,|]+", str(line or ""))
    return [u.rstrip(".,;:") for u in urls]

def _p6e2_url_alive(url):
    try:
        req = urllib.request.Request(
            url,
            method="HEAD",
            headers={"User-Agent": "Mozilla/5.0 AREAL-NEVA source verifier"},
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            return 200 <= int(getattr(resp, "status", 0) or 0) < 400
    except Exception:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 AREAL-NEVA source verifier"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                return 200 <= int(getattr(resp, "status", 0) or 0) < 400
        except Exception:
            return False

def _p6e2_url_live_text(url):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 AREAL-NEVA source verifier"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = int(getattr(resp, "status", 0) or 0)
            if not (200 <= status < 400):
                return False, ""
            raw = resp.read(180000) or b""
            return True, raw.decode("utf-8", "ignore")
    except Exception:
        return False, ""

def _p6e2_verify_live_source_lines(text):
    lines = str(text or "").splitlines()
    out = []
    cache = {}
    text_cache = {}
    phone_re = re.compile(r"(?:\+7|8)\s*[\(\- ]?\d{3}[\)\- ]?\s*\d{3}[\- ]?\d{2}[\- ]?\d{2}")
    for line in lines:
        urls = _p6e2_extract_urls(line)
        raw_phones = phone_re.findall(line)
        phones = [_p6e2_norm_phone(x) for x in raw_phones]
        phones = [x for x in phones if x]
        has_phone = bool(phones)
        if not urls:
            if has_phone:
                continue
            out.append(line)
            continue
        alive = False
        phone_confirmed = not has_phone
        for url in urls[:2]:
            if url not in cache:
                cache[url] = _p6e2_url_alive(url)
            if cache[url]:
                alive = True
                if has_phone:
                    if url not in text_cache:
                        text_cache[url] = _p6e2_url_live_text(url)
                    _, body = text_cache[url]
                    digits = re.sub(r"\D+", "", body or "")
                    if any(phone in digits for phone in phones):
                        phone_confirmed = True
                break
        if alive and phone_confirmed:
            out.append(line)
    return "\n".join(out).strip()

def _p6e2_query_region_guard(text, query):
    qlow = str(query or "").lower().replace("ё", "е")
    if not any(x in qlow for x in ("санкт-петербург", "санкт петербург", "спб", "ленинградск")):
        return str(text or "").strip()
    forbidden = (
        "москва", "московск", "екатеринбург", "новосибирск", "казань", "краснодар",
        "ростов", "нижний новгород", "самара", "воронеж", "пермь", "уфа",
    )
    lines = []
    for line in str(text or "").splitlines():
        low = line.lower().replace("ё", "е")
        if any(x in low for x in forbidden):
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def _p6e2_seen_topic500_phones(chat_id, topic_id=500):
    phones = set()
    phone_re = re.compile(r"(?:\+7|8)\s*[\(\- ]?\d{3}[\)\- ]?\s*\d{3}[\- ]?\d{2}[\- ]?\d{2}")
    try:
        with sqlite3.connect(MEM_DB, timeout=10) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT value FROM memory
                WHERE chat_id=?
                  AND COALESCE(topic_id,0)=?
                  AND (key LIKE 'topic_500_%assistant_output'
                       OR key LIKE 'topic_500_%task_summary'
                       OR key LIKE 'topic_500_archive_%')
                ORDER BY timestamp DESC
                LIMIT 40
                """,
                (str(chat_id), int(topic_id or 500)),
            ).fetchall()
        for row in rows:
            for raw_phone in phone_re.findall(str(row["value"] or "")):
                phone = _p6e2_norm_phone(raw_phone)
                if phone and not _p6e2_is_placeholder_phone(phone):
                    phones.add(phone)
    except Exception:
        pass
    try:
        with sqlite3.connect(CORE_DB, timeout=10) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT result FROM tasks
                WHERE chat_id=?
                  AND COALESCE(topic_id,0)=?
                  AND COALESCE(result,'')<>''
                  AND state IN ('DONE','AWAITING_CONFIRMATION','FAILED')
                ORDER BY rowid DESC
                LIMIT 40
                """,
                (str(chat_id), int(topic_id or 500)),
            ).fetchall()
        for row in rows:
            for raw_phone in phone_re.findall(str(row["result"] or "")):
                phone = _p6e2_norm_phone(raw_phone)
                if phone and not _p6e2_is_placeholder_phone(phone):
                    phones.add(phone)
    except Exception:
        pass
    return phones

def _p6e2_filter_seen_contacts(text, seen_phones):
    if not seen_phones:
        return str(text or "").strip()
    lines = str(text or "").splitlines()
    out = []
    phone_re = re.compile(r"(?:\+7|8)\s*[\(\- ]?\d{3}[\)\- ]?\s*\d{3}[\- ]?\d{2}[\- ]?\d{2}")
    for line in lines:
        phones = [_p6e2_norm_phone(x) for x in phone_re.findall(line)]
        phones = [x for x in phones if x]
        if phones and any(x in seen_phones for x in phones):
            continue
        out.append(line)
    return "\n".join(out).strip()

try:
    _P6E2_ORIG_SEARCH_RUN = SearchMonolithV2.run
    async def _p6e2_search_run(self, payload, user_text, online_call, online_model, base_system_prompt=""):
        payload = dict(payload or {})
        q = _p6e2_search_s(user_text or payload.get("raw_input") or payload.get("normalized_input") or "", 5000)
        payload["raw_input"] = q
        payload["normalized_input"] = q
        payload["pin_context"] = ""
        payload["short_memory_context"] = ""
        payload["long_memory_context"] = ""
        payload["archive_context"] = ""
        payload["search_context"] = ""
        online_model = _assert_online_model_allowed(online_model)
        raw = await online_call(online_model, _p6e2_search_messages(q))
        final = _p6e2_apply_universal_search_canon(raw)
        final = _p6e2_dedupe_contacts(final)
        final = _p6e2_verify_live_source_lines(final)
        final = _p6e2_query_region_guard(final, q)
        final = _p6e2_filter_seen_contacts(final, _p6e2_seen_topic500_phones(payload.get("chat_id"), 500))
        if not re.search(r"(?:\+7|8)\s*[\(\- ]?\d{3}[\)\- ]?\s*\d{3}[\- ]?\d{2}[\- ]?\d{2}", final):
            final = "Новых подтверждённых живых контактов по текущему запросу не найдено"
        stale = ("rockwool", "каменная вата", "термодом", "утеплитель")
        qlow = _p6e2_search_low(q)
        flow = _p6e2_search_low(final)
        if any(x in flow and x not in qlow for x in stale) and any(x in qlow for x in ("ваз", "2110", "2114", "сайлент", "саленблок", "сальник", "iphone", "pixel", "телефон")):
            final = "Поиск заблокирован: ответ содержит старый товар из другой поисковой сессии. Повтори запрос одной строкой с товаром и регионом"
        if not final:
            final = "Подтверждённых вариантов по текущему запросу не найдено"
        try:
            import logging
            logging.getLogger("ai_router").info("P6E2_SEARCH_CURRENT_QUERY_DONE chars=%s", len(final))
        except Exception:
            pass
        return final
    SearchMonolithV2.run = _p6e2_search_run
except Exception:
    pass
# === END_P6E2_SEARCH_CURRENT_QUERY_HARD_NO_STALE_NO_ESTIMATE_POLLUTION_20260504_V1 ===

# === P6E4_GENERAL_SEARCH_NO_DOMAIN_CONTAMINATION_20260504_V1 ===
import os as _p6e4_os
import re as _p6e4_re
import json as _p6e4_json
import urllib.request as _p6e4_urllib_request
import inspect as _p6e4_inspect
import asyncio as _p6e4_asyncio
import logging as _p6e4_logging

_P6E4_AUTO_TERMS = ("саленблок", "сайлентблок", "сальник", "ваз", "жигули", "2110", "авто", "машин", "пыльник", "шрус", "рычаг", "стойка")
_P6E4_BUILD_TERMS = ("смет", "бетон", "арматур", "фундамент", "кровл", "технадзор", "стро", "дом", "плита", "каркас", "клик-фальц", "утепл", "rockwool", "минват")
_P6E4_BUILD_RESULT_TERMS = ("rockwool", "роквул", "минват", "утеплител", "термодом", "строймат", "базальт", "кровл", "бетон", "арматур")
_P6E4_AUTO_RESULT_TERMS = ("сайлентблок", "саленблок", "сальник", "ваз", "2110", "lada", "vaz", "автозапчаст", "шрус", "пыльник")

def _p6e4_env_load_once():
    if getattr(_p6e4_env_load_once, "_done", False):
        return
    for path in ("/root/.areal-neva-core/.env", ".env"):
        try:
            if not _p6e4_os.path.exists(path):
                continue
            for line in open(path, "r", encoding="utf-8", errors="ignore"):
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in _p6e4_os.environ:
                    _p6e4_os.environ[k] = v
        except Exception:
            pass
    _p6e4_env_load_once._done = True

def _p6e4_val(obj, key, default=None):
    try:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return obj[key]
    except Exception:
        try:
            return getattr(obj, key, default)
        except Exception:
            return default

def _p6e4_extract_query(args, kwargs):
    for k in ("query", "prompt", "raw_input", "user_input", "text"):
        if isinstance(kwargs.get(k), str) and kwargs.get(k).strip():
            return kwargs.get(k).strip()
    for obj in args:
        if isinstance(obj, str) and obj.strip():
            return obj.strip()
        raw = _p6e4_val(obj, "raw_input", None)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
        inp = _p6e4_val(obj, "input", None)
        if isinstance(inp, str) and inp.strip():
            return inp.strip()
    return ""

def _p6e4_norm(s):
    return _p6e4_re.sub(r"\s+", " ", str(s or "").lower()).strip()

def _p6e4_is_auto_query(q):
    t = _p6e4_norm(q)
    return any(x in t for x in _P6E4_AUTO_TERMS)

def _p6e4_is_build_query(q):
    t = _p6e4_norm(q)
    return any(x in t for x in _P6E4_BUILD_TERMS)

def _p6e4_is_too_vague(q):
    t = _p6e4_norm(q)
    return len(t) < 8 or t in ("я тебя про что спрашивал?", "я тебя про что спрашивал", "дальше что?", "дальше что")

def _p6e4_contaminated(q, result):
    qt = _p6e4_norm(q)
    rt = _p6e4_norm(result)
    if _p6e4_is_auto_query(qt):
        return any(x in rt for x in _P6E4_BUILD_RESULT_TERMS) and not any(x in rt for x in _P6E4_AUTO_RESULT_TERMS)
    if not _p6e4_is_build_query(qt):
        return any(x in rt for x in ("rockwool", "роквул", "термодом", "минват"))
    return False

def _p6e4_general_online_search(q):
    _p6e4_env_load_once()
    if _p6e4_is_too_vague(q):
        return "По текущему сообщению нет самостоятельного поискового запроса. Старый результат не использую"
    api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY", "")
    if not api_key:
        return ""
    base = (_p6e4_os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").rstrip("/")
    model = _assert_online_model_allowed(_p6e4_os.getenv("OPENROUTER_MODEL_ONLINE") or _p6e4_os.getenv("ONLINE_MODEL") or "perplexity/sonar")
    domain_rule = "Автозапчасти/товары/услуги/строительство определяй только по текущему запросу"
    if _p6e4_is_auto_query(q):
        domain_rule = "Это поиск автозапчастей. Ищи только автозапчасти и совместимые детали. Стройматериалы запрещены"
    elif _p6e4_is_build_query(q):
        domain_rule = "Это строительный/сметный поиск. Ищи стройматериалы, работы, поставщиков или нормы по текущему запросу"
    prompt = (
        "Ты универсальный поисковый агент. Работай по текущему запросу, без старой памяти и без доменной подмены.\n"
        f"{domain_rule}.\n"
        "Верни кратко по-русски: найдено, таблица вариантов, цена/наличие/город/ссылка, лучший вариант, что проверить.\n"
        "Если точных данных нет — так и напиши, не подменяй товар другим доменом.\n\n"
        f"Текущий запрос: {q}"
    )
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a fresh web/product search agent. Use only the current user query. Never reuse stale construction results for non-construction searches."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1800,
    }
    req = _p6e4_urllib_request.Request(
        base + "/chat/completions",
        data=_p6e4_json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/rj7hmz9cvm-lgtm/areal-neva-core",
            "X-Title": "AREAL-NEVA-ORCHESTRA",
        },
        method="POST",
    )
    try:
        with _p6e4_urllib_request.urlopen(req, timeout=90) as resp:
            data = _p6e4_json.loads(resp.read().decode("utf-8", errors="ignore"))
        return str(data["choices"][0]["message"]["content"]).strip()
    except Exception as exc:
        _p6e4_logging.getLogger("ai_router").warning("P6E4_GENERAL_SEARCH_ERR query=%r err=%s", q[:120], exc)
        return ""

def _p6e4_wrap_search_func(name):
    orig = globals().get(name)
    if not orig or getattr(orig, "_p6e4_wrapped", False):
        return
    if _p6e4_inspect.iscoroutinefunction(orig):
        async def wrapped(*args, **kwargs):
            q = _p6e4_extract_query(args, kwargs)
            if q and not _p6e4_is_build_query(q):
                fresh = await _p6e4_asyncio.to_thread(_p6e4_general_online_search, q)
                if fresh:
                    return fresh
            res = await orig(*args, **kwargs)
            if q and _p6e4_contaminated(q, res):
                fresh = await _p6e4_asyncio.to_thread(_p6e4_general_online_search, q)
                if fresh:
                    return fresh
            return res
    else:
        def wrapped(*args, **kwargs):
            q = _p6e4_extract_query(args, kwargs)
            if q and not _p6e4_is_build_query(q):
                fresh = _p6e4_general_online_search(q)
                if fresh:
                    return fresh
            res = orig(*args, **kwargs)
            if q and _p6e4_contaminated(q, res):
                fresh = _p6e4_general_online_search(q)
                if fresh:
                    return fresh
            return res
    wrapped._p6e4_wrapped = True
    globals()[name] = wrapped

for _p6e4_func_name in (
    "run_search_session",
    "search_current_query",
    "handle_search_query",
    "handle_search",
    "run_search",
    "execute_search",
    "search_session",
    "run",
):
    _p6e4_wrap_search_func(_p6e4_func_name)

_p6e4_logging.getLogger("ai_router").info("P6E4_GENERAL_SEARCH_GUARD_INSTALLED")
# === END_P6E4_GENERAL_SEARCH_NO_DOMAIN_CONTAMINATION_20260504_V1 ===

====================================================================================================
END_FILE: core/search_session.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/sheets_generator.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c81446527b4f3d281a6839303da115164fdc1d9f1ec3f0cbd58ed9f8da4a6112
====================================================================================================
# === GOOGLE_SHEETS_NATIVE_EXPORT_V1 ===
from __future__ import annotations
import logging
import os
import re
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

def _safe_title(title: str) -> str:
    t = re.sub(r"[\r\n\t]+", " ", str(title or "Estimate")).strip()
    return re.sub(r"[\\/]+", "_", t)[:90] or "Estimate"

def _creds():
    from dotenv import load_dotenv
    load_dotenv("/root/.areal-neva-core/.env", override=False)
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials(
        None,
        refresh_token=<REDACTED_SECRET>"GDRIVE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GDRIVE_CLIENT_ID"],
        client_secret=<REDACTED_SECRET>"GDRIVE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/spreadsheets"],
    )
    creds.refresh(Request())
    return creds

def create_google_sheet(title: str, rows: List[List[Any]], topic_id: int = 0, task_id: str = "") -> Optional[str]:
    try:
        from googleapiclient.discovery import build
        creds = _creds()
        drive = build("drive", "v3", credentials=creds, cache_discovery=False)
        sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
        sheet = sheets.spreadsheets().create(
            body={"properties": {"title": _safe_title(title)}, "sheets": [{"properties": {"title": "Смета"}}]},
            fields="spreadsheetId,spreadsheetUrl",
        ).execute()
        sid = sheet.get("spreadsheetId")
        if not sid:
            return None
        values = [["" if v is None else v for v in (row if isinstance(row, list) else [row])] for row in (rows or [])][:5000]
        if values:
            sheets.spreadsheets().values().update(
                spreadsheetId=sid, range="Смета!A1",
                valueInputOption="USER_ENTERED", body={"values": values},
            ).execute()
        try:
            from core.engine_base import get_drive_topic_folder_id
            folder_id = get_drive_topic_folder_id(int(topic_id or 0))
            if folder_id:
                meta = drive.files().get(fileId=sid, fields="parents").execute()
                old = ",".join(meta.get("parents") or [])
                drive.files().update(fileId=sid, addParents=folder_id, removeParents=old, fields="id").execute()
        except Exception as me:
            logger.warning("SHEETS_MOVE_ERR task=%s err=%s", task_id, me)
        try:
            drive.permissions().create(fileId=sid, body={"role": "reader", "type": "anyone"}, fields="id").execute()
        except Exception:
            pass
        link = drive.files().get(fileId=sid, fields="webViewLink").execute().get("webViewLink") \
               or f"https://docs.google.com/spreadsheets/d/{sid}/edit"
        logger.info("GOOGLE_SHEETS_NATIVE_EXPORT_V1_OK task=%s link=%s", task_id, link)
        return link
    except Exception as e:
        logger.warning("GOOGLE_SHEETS_NATIVE_EXPORT_V1_ERR task=%s err=%s", task_id, e)
        return None
# === END_GOOGLE_SHEETS_NATIVE_EXPORT_V1 ===

====================================================================================================
END_FILE: core/sheets_generator.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/sheets_route.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 6f8fdc9ca242696660b7d018166ccec46738a0ccfdf0baf929cf4d85f42d2f00
====================================================================================================
# === SHEETS_ROUTE_V1 ===
import os, logging
logger = logging.getLogger(__name__)
CREDENTIALS_PATH = "/root/.areal-neva-core/credentials.json"

def is_sheets_requested(text: str) -> bool:
    # === SHEETS_INTENT_DETECT_V1 ===
    t = (text or "").lower()
    return any(k in t for k in ["таблиц", "sheets", "гугл таблиц", "google sheets"])

async def create_estimate_sheet(rows: list, title: str, chat_id: str, topic_id: int) -> dict:
    if not os.path.exists(CREDENTIALS_PATH):
        return {"success": False, "url": "", "error": "SHEETS_CREDENTIALS_MISSING"}
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        svc = build("sheets", "v4", credentials=creds)
        sheet = svc.spreadsheets().create(body={"properties": {"title": title}}).execute()
        sid = sheet["spreadsheetId"]
        url = f"https://docs.google.com/spreadsheets/d/{sid}/edit"
        header = [["№", "Наименование", "Ед.", "Кол-во", "Цена, руб.", "Сумма, руб."]]
        data_rows = header + [[i+1, r.get("name",""), r.get("unit",""), r.get("qty",0),
                                r.get("price",0), r.get("total",0)] for i, r in enumerate(rows)]
        svc.spreadsheets().values().update(
            spreadsheetId=sid, range="A1",
            valueInputOption="RAW",
            body={"values": data_rows}
        ).execute()
        return {"success": True, "url": url, "sheet_id": sid}
    except Exception as e:
        return {"success": False, "url": "", "error": str(e)}
# === END SHEETS_ROUTE_V1 ===

====================================================================================================
END_FILE: core/sheets_route.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/source_dedup.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e5f2c40dc2ffb3c4c4fdfeaa1c27cd4622c0d33c6c10b363118cb90cb265baef
====================================================================================================
# === SOURCE_DEDUPLICATION_V1 ===
import hashlib, logging
logger = logging.getLogger(__name__)

def _sig(item: dict) -> str:
    key = f"{item.get('url','')}|{item.get('supplier','')}|{item.get('price','')}"
    return hashlib.md5(key.encode()).hexdigest()

def dedup_offers(offers: list) -> list:
    seen = set()
    result = []
    for o in offers:
        s = _sig(o)
        if s not in seen:
            seen.add(s)
            result.append(o)
    return result

def dedup_search_results(results: list, key_field: str = "url") -> list:
    seen = set()
    clean = []
    for r in results:
        k = str(r.get(key_field) or r)[:200]
        if k not in seen:
            seen.add(k)
            clean.append(r)
    return clean

# TIME_RELEVANCE — фильтр по свежести
def filter_by_time_relevance(items: list, date_field: str = "date", max_days: int = 30) -> list:
    from datetime import datetime, timezone, timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
    result = []
    for item in items:
        raw_date = item.get(date_field)
        if not raw_date:
            result.append(item)
            continue
        try:
            ts = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
            if ts >= cutoff:
                result.append(item)
        except Exception:
            result.append(item)
    return result

# REGION_PRIORITY — приоритет по региону
_PRIORITY_REGIONS = ["санкт-петербург", "спб", "москва", "мск", "ленинградская"]

def sort_by_region(offers: list, preferred_regions: list = None) -> list:
    regions = [r.lower() for r in (preferred_regions or _PRIORITY_REGIONS)]
    def region_score(o):
        city = str(o.get("city", "")).lower()
        for i, r in enumerate(regions):
            if r in city:
                return i
        return len(regions)
    return sorted(offers, key=region_score)
# === END SOURCE_DEDUPLICATION_V1 ===

====================================================================================================
END_FILE: core/source_dedup.py
FILE_CHUNK: 1/1
====================================================================================================
