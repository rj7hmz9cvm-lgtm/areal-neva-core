# === SEARCH_MONOLITH_V2_FULL ===
from __future__ import annotations
import json, logging, os, re, sqlite3, time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("search_session")
BASE = "/root/.areal-neva-core"
MEM_DB = f"{BASE}/data/memory.db"
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
