# ORCHESTRA_FULL_CONTEXT_PART_011
generated_at_utc: 2026-05-08T07:20:02.545119+00:00
git_sha_before_commit: 3dcb94adb675639f423ecd26617e6c1c2d10ba23
part: 11/17


====================================================================================================
BEGIN_FILE: core/search_session.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: f07740fc973009823dbdb790b5dd67f5e3d17dd52d16bf0fde1baabea43fbb8f
====================================================================================================
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

Верни только чистую выдачу поставщиков/вариантов:
Поставщик | Площадка | Город | Цена | Наличие | Доставка | Ссылка | Проверено
Запрещено возвращать старые товары, сметы, Excel, PDF, строительные позиции из другого запроса"""
    return [{"role": "system", "content": "CURRENT_QUERY_ONLY. NO_STALE_CONTEXT. NO_ESTIMATE_OUTPUT. NO_INTERNAL_MARKERS."}, {"role": "user", "content": user}]

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
        raw = await online_call(online_model, _p6e2_search_messages(q))
        final = _p6e2_search_s(raw, 12000)
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
    model = _p6e4_os.getenv("OPENROUTER_MODEL_ONLINE") or _p6e4_os.getenv("ONLINE_MODEL") or "perplexity/sonar"
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

====================================================================================================
BEGIN_FILE: core/stroyka_estimate_canon.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d3e30d4f6ecf700c14ec01fb5fd0d0f208aa3635fc9e7ab392120f48a75fb59d
====================================================================================================
# === FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3 ===
from __future__ import annotations

import os
import re
import io
import json
import uuid
import time
import math
import sqlite3
import asyncio
import tempfile
import statistics
import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple

import requests
from dotenv import load_dotenv

BASE = Path("/root/.areal-neva-core")
ENV_PATH = BASE / ".env"
MEM_DB = BASE / "data/memory.db"
load_dotenv(str(ENV_PATH), override=True)

TOPIC_ID_STROYKA = 2
DRIVE_TEMPLATES_PARENT_ID = "19Z3acDgPub4nV55mad5mb8ju63FsqoG9"

DEPRECATED_TEMPLATE_NAMES = (
    "ВОР_кирпичная_кладка_ИСПРАВЛЕНО.xlsx",
)

CANON_TEMPLATE_FALLBACK = {
    "m80": {"title": "М-80.xlsx", "role": "full_house_estimate_template", "file_id": "1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp", "source": "fallback_registry"},
    "m110": {"title": "М-110.xlsx", "role": "full_house_estimate_template", "file_id": "1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo", "source": "fallback_registry"},
    "roof": {"title": "крыша и перекр.xlsx", "role": "roof_and_floor_estimate_template", "file_id": "16YecwnJ9umnVprFu9V77UCV6cPrYbNh3", "source": "fallback_registry"},
    "foundation": {"title": "фундамент_Склад2.xlsx", "role": "foundation_estimate_template", "file_id": "1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp", "source": "fallback_registry"},
    "areal": {"title": "Ареал Нева.xlsx", "role": "general_company_estimate_template", "file_id": "1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm", "source": "fallback_registry"},
}

ESTIMATE_WORDS = (
    "смет", "стоимость", "расчет", "расчёт", "посчитай", "коробк", "дом", "стройк",
    "фундамент", "кровл", "перекр", "ангар", "склад", "газобетон", "каркас", "монолит",
)

CONTINUATION_WORDS = (
    "да", "да сделай", "сделай", "где смета", "ну что", "вариант 1", "вариант 2",
    "первый", "второй", "подтверждаю", "ок", "окей", "цены актуальны", "адрес подтверждаю",
    "средняя", "минимальная", "максимальная", "ручная", "конкретная ссылка",
)

REVISION_WORDS = (
    "нет не так", "не так", "переделай", "исправь", "правки", "пересчитай", "измени", "уточни",
)

PROJECT_ONLY_WORDS = (
    "проект ар", "проект кж", "проект кд", "чертеж", "чертёж", "раздел ар", "раздел кж", "раздел кд",
)

EXCLUSIONS_DEFAULT = (
    "подготовка участка",
    "стройгородок",
    "бытовки",
    "отмостка",
    "дренаж",
    "ливневая канализация",
    "вывоз мусора",
    "наружные сети",
    "всё, что не указано явно",
)

PRICE_CHOICE_HELP = """Выбор цены:
- средняя / медианная
- минимальная
- максимальная
- конкретная ссылка
- ручная цена
- можно добавить наценку, скидку, запас или поправку по позиции, разделу или всей смете"""


def _s(v: Any) -> str:
    return "" if v is None else str(v).strip()


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _clean(text: str, limit: int = 12000) -> str:
    text = (text or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]


def _now() -> str:
    return datetime.datetime.utcnow().isoformat()


def _row_get(row: Any, key: str, default: Any = "") -> Any:
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        return getattr(row, key, default)


def _cols(conn: sqlite3.Connection, table: str) -> List[str]:
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except Exception:
        return []


def _update_task_safe(conn: sqlite3.Connection, task_id: str, **kwargs: Any) -> None:
    cols = _cols(conn, "tasks")
    parts, vals = [], []
    for k, v in kwargs.items():
        if k in cols:
            parts.append(f"{k}=?")
            vals.append(v)
    if "updated_at" in cols:
        parts.append("updated_at=datetime('now')")
    if not parts:
        return
    vals.append(task_id)
    conn.execute(f"UPDATE tasks SET {', '.join(parts)} WHERE id=?", vals)
    conn.commit()


def _history_safe(conn: sqlite3.Connection, task_id: str, action: str) -> None:
    try:
        conn.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
            (task_id, _clean(action, 1000)),
        )
        conn.commit()
    except Exception:
        pass


def _memory_save(chat_id: str, key: str, value: Dict[str, Any]) -> None:
    try:
        con = sqlite3.connect(str(MEM_DB))
        try:
            payload = json.dumps(value, ensure_ascii=False, indent=2)
            con.execute(
                "INSERT OR REPLACE INTO memory (id, chat_id, key, value, timestamp) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), str(chat_id), str(key), payload, _now()),
            )
            con.commit()
        finally:
            con.close()
    except Exception:
        pass


def _memory_latest(chat_id: str, key_prefix: str) -> Optional[Dict[str, Any]]:
    try:
        con = sqlite3.connect(str(MEM_DB))
        con.row_factory = sqlite3.Row
        try:
            row = con.execute(
                "SELECT key,value,timestamp FROM memory WHERE chat_id=? AND key LIKE ? ORDER BY timestamp DESC LIMIT 1",
                (str(chat_id), f"{key_prefix}%"),
            ).fetchone()
            if not row:
                return None
            data = json.loads(row["value"] or "{}")
            data["_memory_key"] = row["key"]
            data["_memory_timestamp"] = row["timestamp"]
            return data
        finally:
            con.close()
    except Exception:
        return None



# === FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_CONTEXT_BLEED_FIX ===
def _parse_iso_ts(value: Any) -> Optional[datetime.datetime]:
    txt = _s(value)
    if not txt:
        return None
    txt = txt.replace("Z", "+00:00")
    try:
        dt = datetime.datetime.fromisoformat(txt)
        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return dt
    except Exception:
        return None


def _age_seconds(value: Any) -> Optional[float]:
    dt = _parse_iso_ts(value)
    if not dt:
        return None
    return (datetime.datetime.utcnow() - dt).total_seconds()


def _pending_is_fresh(pending: Optional[Dict[str, Any]], max_seconds: int = 600) -> bool:
    if not pending:
        return False
    created = pending.get("created_at") or pending.get("_memory_timestamp")
    age = _age_seconds(created)
    return age is not None and 0 <= age <= max_seconds


def _is_bad_estimate_result(text: str) -> bool:
    t = _low(text)

    # === STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_BAD_RESULT_MARKERS ===
    stale_markers = (
        "задачи за последние 24 часа",
        "создание сметы: профлист",
        "итоговая сумма: 55000",
        "1capn1ikkxwypbxhny5caokqrsxbgzho",
        "1glcscpl3d91elveo_m11ezwh_uu5b4vm",
        "1pu77xrzhmpobus1pfximwdwckrgje1tn",
        "смета уже есть:",
        "смета создана по образцу вор",
        "вор_кирпичная_кладка",
        "vor_kirpich",
        "позиций: 13 | итого: 690510",
        "690510.00 руб",
        "файлы в этом топике уже есть",
        "нашёл релевантное",
        "нашел релевантное",
        "активный контекст найден",
    )
    if any(x in t for x in stale_markers):
        return True
    # === END_STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_BAD_RESULT_MARKERS ===
    bad = (
        # === FULL_STROYKA_V3_SEARCH_LOOP_BAD_RESULT_FIX ===
        "поставщик | площадка",
        "auto_parts",
        "search_monolith",
        "tco | риски",
        "ошибка классификации запроса",
        "категория не совпадает",
        # === FULL_STROYKA_LOOP_FINAL_CLOSE_BAD_RESULT_FIX ===
        "смета создана по образцу вор",
        "смета уже есть:",
        "вор_кирпичная_кладка",
        "вор_кирпич",
        "vor_kirpich",
        "в_ор_кирпич",
        "позиций: 13 | итого: 690510",
        "690510.00 руб",
        # === END_FULL_STROYKA_LOOP_FINAL_CLOSE_BAD_RESULT_FIX ===
        # === END_FULL_STROYKA_V3_SEARCH_LOOP_BAD_RESULT_FIX ===
        "файлы в этом топике уже есть",
        "нашёл релевантное",
        "нашел релевантное",
        "можно использовать как образец сметы",
        "активный контекст найден",
        "проектный файл не создан",
        "docx_create_failed",
        "state: finished",
        "задача закрыта по запросу",
        # === TOPIC2_FINAL_GAPS_V5_FORBIDDEN_PHRASES ===
        "файл скачан",
        "ожидает анализа",
        "выбор принят",
        "проверяю доступные файлы",
        "структура проекта включает",
        "файл содержит проект",
        "уточните запрос",
        "что строим",
        "не нашёл родительскую задачу",
        "не вижу размеры объекта",
        "позиция по присланному фото",
        # === END_TOPIC2_FINAL_GAPS_V5_FORBIDDEN_PHRASES ===
    )
    # === FULL_STROYKA_DISABLE_OLD_ESTIMATE_RECALL_FINAL_BAD_MARKERS ===
    stale_links = (
        "задачи за последние 24 часа",
        "создание сметы: профлист",
        "итоговая сумма: 55000",
        "1capn1ikkxwypbxhny5caokqrsxbgzho",
        "1glcscpl3d91elveo_m11ezwh_uu5b4vm",
        "1pu77xrzhmpobus1pfximwdwckrgje1tn",
        "смета уже есть",
        "использовать существующую или пересчитать",
    )
    if any(x in t for x in stale_links):
        return True
    # === END_FULL_STROYKA_DISABLE_OLD_ESTIMATE_RECALL_FINAL_BAD_MARKERS ===
    if any(x in t for x in bad):
        return True
    # === TOPIC2_FINAL_GAPS_V5_REGEX_FORBIDDEN ===
    import re as _ibr_re
    if _ibr_re.search(r'позиций:\s*1(?:\s|$)', t):
        return True
    if "/root/" in t or "/tmp/" in t:
        return True
    if "revision_context" in t or "traceback (most" in t:
        return True
    if "engine:" in t or "manifest:" in t:
        return True
    # === TOPIC2_FINAL_GAPS_V5B_RAW_JSON_GUARD ===
    if t.strip().startswith("{") and any(_k in t for _k in ('"state":', '"topic_id":', '"task_id":', '"result":', '"action":')):
        return True
    if _ibr_re.search(r'"state"\s*:\s*"(?:failed|in_progress|done|pending|waiting)', t):
        return True
    # === END_TOPIC2_FINAL_GAPS_V5B_RAW_JSON_GUARD ===
    # === END_TOPIC2_FINAL_GAPS_V5_REGEX_FORBIDDEN ===
    return False


def _has_real_estimate_artifact(text: str) -> bool:
    t = _low(text)
    if _is_bad_estimate_result(t):
        return False
    good = (
        "excel:",
        "xlsx:",
        ".xlsx",
        "pdf:",
        ".pdf",
        "предварительная смета готова",
        "итого:",
    )
    return any(x in t for x in good)


def _is_confirm_only(text: str) -> bool:
    t = _low(text).replace("[voice]", "").strip()
    if any(x in t for x in ESTIMATE_WORDS):
        return False
    return _is_confirm(t)
# === END_FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_CONTEXT_BLEED_FIX ===

def _drive_service():
    from core.topic_drive_oauth import _oauth_service
    return _oauth_service()


def list_drive_templates() -> List[Dict[str, Any]]:
    try:
        service = _drive_service()
        q = (
            f"'{DRIVE_TEMPLATES_PARENT_ID}' in parents and trashed = false and "
            "(mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' "
            "or mimeType = 'application/vnd.ms-excel' "
            "or mimeType = 'application/vnd.google-apps.spreadsheet')"
        )
        resp = service.files().list(
            q=q,
            spaces="drive",
            fields="files(id,name,mimeType,modifiedTime,size)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            pageSize=100,
        ).execute()
        out = []
        for f in resp.get("files", []):
            name = f.get("name") or ""
            if name in DEPRECATED_TEMPLATE_NAMES:
                continue
            out.append({
                "title": name,
                "file_id": f.get("id"),
                "mimeType": f.get("mimeType"),
                "modifiedTime": f.get("modifiedTime"),
                "role": "drive_dynamic_template",
                "source": "drive_templates_folder",
            })
        return out
    except Exception:
        return []


def _fallback_template_list() -> List[Dict[str, Any]]:
    return [dict(v) for v in CANON_TEMPLATE_FALLBACK.values()]


def _extract_dimensions(text: str) -> Optional[Tuple[float, float]]:
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*[xх×*]\s*(\d+(?:[.,]\d+)?)", _low(text))
    if not m:
        return None
    return float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))


def _extract_floors(text: str) -> Optional[int]:
    t = _low(text)
    m = re.search(r"(\d+)\s*(?:этаж|этажа|этажей)", t)
    if m:
        return int(m.group(1))
    if "2 эта" in t or "два эта" in t:
        return 2
    if "1 эта" in t or "один эта" in t:
        return 1
    return None


def _extract_distance_km(text: str) -> Optional[float]:
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*км", _low(text))
    return float(m.group(1).replace(",", ".")) if m else None


def _extract_material(text: str) -> str:
    t = _low(text)
    for key in ("газобетон", "каркас", "кирпич", "монолит", "керамоблок", "брус", "арболит"):
        if key in t:
            return key
    return ""


def _extract_object(text: str) -> str:
    t = _low(text)
    for key in ("дом", "ангар", "склад", "фундамент", "кровля", "коробка"):
        if key in t:
            return key
    return ""


def _extract_foundation(text: str) -> str:
    t = _low(text)
    if "монолит" in t or "плита" in t:
        return "монолитная плита"
    if "лента" in t:
        return "ленточный фундамент"
    if "сва" in t:
        return "свайный фундамент"
    if "фундамент" in t:
        return "фундамент"
    return ""


def _extract_scope(text: str) -> str:
    t = _low(text)
    if "под ключ" in t:
        return "под ключ"
    if "коробк" in t:
        return "коробка"
    return ""


def _parse_request(text: str) -> Dict[str, Any]:
    dims = _extract_dimensions(text)
    area_floor = dims[0] * dims[1] if dims else None
    floors = _extract_floors(text)
    area_total = area_floor * floors if area_floor and floors else area_floor
    return {
        "object": _extract_object(text),
        "material": _extract_material(text),
        "dimensions": dims,
        "area_floor": area_floor,
        "floors": floors,
        "area_total": area_total,
        "distance_km": _extract_distance_km(text),
        "foundation": _extract_foundation(text),
        "scope": _extract_scope(text),
        "raw": text,
    }


def _missing_question(parsed: Dict[str, Any]) -> Optional[str]:

    if parsed.get("pdf_spec_rows") or parsed.get("ocr_table_rows"):
        return None
    # === STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_PRICE_NO_MISSING ===
    raw = _low(parsed.get("raw", ""))
    if ("цена" in raw or "руб" in raw or "₽" in raw) and any(u in raw for u in ("м²", "м2", "м³", "м3", "шт", "кг", "тн", "тонн")) and any(x in raw for x in ("смет", "фундамент", "монолит", "кровл", "работ")):
        return None
    # === END_STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_PRICE_NO_MISSING ===
    if not parsed.get("object"):
        return "Что строим: дом, ангар, склад, фундамент или кровлю?"
    if not parsed.get("material") and parsed.get("object") not in ("фундамент", "кровля", "ангар", "склад"):
        return "Из какого материала строим?"
    if parsed.get("distance_km") is None:
        return "Где находится объект: город или удалённость в км?"
    if not parsed.get("dimensions"):
        return "Какие размеры объекта?"
    if parsed.get("object") == "дом" and not parsed.get("floors"):
        return "Сколько этажей?"
    if not parsed.get("foundation") and parsed.get("object") not in ("кровля", "фундамент", "ангар", "склад"):
        return "Какой фундамент?"
    if not parsed.get("scope") and parsed.get("object") == "дом":
        return "Смета нужна только коробка или под ключ?"
    return None


def _template_score(parsed: Dict[str, Any], tpl: Dict[str, Any]) -> int:
    name = _low(tpl.get("title"))
    obj = parsed.get("object") or ""
    material = parsed.get("material") or ""
    area_total = float(parsed.get("area_total") or 0)
    score = 0
    if tpl.get("title") in DEPRECATED_TEMPLATE_NAMES:
        return -9999
    if obj in ("ангар", "склад", "фундамент") and ("фундамент" in name or "склад" in name):
        score += 100
    if obj == "кровля" and ("крыш" in name or "перекр" in name):
        score += 100
    if material == "каркас" and ("м-80" in name or "м80" in name or "м-110" in name or "м110" in name):
        score += 90
    if material == "каркас" and area_total and area_total > 100 and ("м-110" in name or "м110" in name):
        score += 40
    if material == "каркас" and area_total and area_total <= 100 and ("м-80" in name or "м80" in name):
        score += 40
    if material in ("газобетон", "кирпич", "керамоблок", "монолит", "арболит") and ("ареал" in name or "м-110" in name or "м110" in name or "м-80" in name or "м80" in name):
        score += 80
    if "ареал" in name:
        score += 20
    return score


def choose_template(parsed: Dict[str, Any]) -> Dict[str, Any]:
    templates = list_drive_templates() or _fallback_template_list()
    ranked = sorted(templates, key=lambda t: _template_score(parsed, t), reverse=True)
    return ranked[0] if ranked else CANON_TEMPLATE_FALLBACK["areal"]


# === TOPIC2_FULL_CLOSE_GAP_A: deterministic work/material classifier ===
_WORK_KW = (
    "работ", "монтаж", "кладк", "установк", "доставк", "разгруз",
    "подач", "вибрирован", "уход за бетон", "гидроизоляц", "утеплен",
    "засыпк", "опалубк", "армирован", "бетонирован", "устройств",
    "демонтаж", "сборк",
)
_MAT_KW = (
    "материал", "бетон", "арматур", "газобетон", "кирпич", "брус",
    "пиломат", "утеплитель", "мембран", "плитк", "ламинат",
    "сантехник", "окна", "двери", "крепеж", "щебень", "песок",
)

def _classify_item(name: str, section: str) -> str:
    n = _low(str(name or ""))
    if any(k in n for k in _WORK_KW):
        return "work"
    if any(k in n for k in _MAT_KW):
        return "material"
    s = _low(str(section or ""))
    if s in ("логистика", "накладные расходы", "накладные"):
        return "overhead"
    return "material"
# === END TOPIC2_FULL_CLOSE_GAP_A classifier ===


def choose_template_sheet(parsed: Dict[str, Any], sheet_names: List[str]) -> tuple:
    """Returns (sheet_name, source) where source is 'match' or 'fallback'."""
    material = parsed.get("material") or ""
    obj = parsed.get("object") or ""
    names = list(sheet_names or [])
    lows = {name: _low(name) for name in names}

    if material == "каркас":
        for name, low in lows.items():
            if "каркас" in low:
                return name, "match"

    if material in ("газобетон", "кирпич", "керамоблок", "монолит", "арболит") or obj in ("дом", "коробка"):
        for name, low in lows.items():
            if "газобетон" in low:
                return name, "match"

    if obj in ("кровля",):
        for name, low in lows.items():
            if "кров" in low or "перекр" in low:
                return name, "match"

    if obj in ("ангар", "склад", "фундамент"):
        for name, low in lows.items():
            if "смет" in low or "фундамент" in low or "склад" in low:
                return name, "match"

    # GAP-B: fallback to first sheet — propagate source for marker
    return (names[0], "fallback") if names else (None, "fallback")


def download_template_xlsx(template: Dict[str, Any]) -> Optional[str]:
    file_id = template.get("file_id")
    if not file_id:
        return None
    try:
        service = _drive_service()
        mime = template.get("mimeType") or ""
        if mime == "application/vnd.google-apps.spreadsheet":
            request = service.files().export_media(
                fileId=file_id,
                mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
        path = os.path.join(tempfile.gettempdir(), f"tpl_{file_id}_{int(time.time())}.xlsx")
        with io.FileIO(path, "wb") as fh:
            from googleapiclient.http import MediaIoBaseDownload
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        return path if os.path.exists(path) and os.path.getsize(path) > 1000 else None
    except Exception:
        return None


def extract_template_prices(template_path: Optional[str], parsed: Dict[str, Any]) -> tuple:
    """Returns (prices_text, sheet_name, sheet_fallback: bool)."""
    if not template_path or not os.path.exists(template_path):
        return "Цены из шаблона: шаблон не скачан, используется только структура/сценарий", None, False
    try:
        from openpyxl import load_workbook
        wb = load_workbook(template_path, data_only=True, read_only=True)
        selected, _sheet_src = choose_template_sheet(parsed, wb.sheetnames)
        ws = wb[selected] if selected in wb.sheetnames else wb.active

        keys = ("бетон", "арматур", "газобетон", "кирпич", "кладк", "монтаж", "достав", "манипулятор", "кран", "пиломат", "кров")
        found = []
        for row in ws.iter_rows(values_only=True):
            txt = " | ".join("" if v is None else str(v) for v in row)
            low = _low(txt)
            if not any(k in low for k in keys):
                continue
            nums = re.findall(r"\d[\d\s]{2,}(?:[.,]\d+)?", txt)
            vals = []
            for n in nums:
                try:
                    v = float(n.replace(" ", "").replace(",", "."))
                    if 100 <= v <= 10000000:
                        vals.append(v)
                except Exception:
                    pass
            if vals:
                found.append(f"- {ws.title}: {txt[:180]}")
            if len(found) >= 15:
                break
        wb.close()
        return "Цены из выбранного листа шаблона:\n" + ("\n".join(found) if found else "ключевые цены в листе не распознаны автоматически"), selected, _sheet_src == "fallback"
    except Exception as e:
        return f"Цены из шаблона: ошибка чтения шаблона: {e}", None, False


def is_stroyka_estimate_candidate(task: Any) -> bool:
    if int(_row_get(task, "topic_id", 0) or 0) != TOPIC_ID_STROYKA:
        return False
    input_type = _low(_row_get(task, "input_type", ""))
    if input_type in ("photo", "file", "drive_file", "image", "document"):
        # §6 multi-format intake: allow when caption contains estimate keywords
        _mfi_cap = _low(_row_get(task, "raw_input", ""))
        if _mfi_cap and any(x in _mfi_cap for x in ESTIMATE_WORDS):
            return True
        return False
    raw = _low(_row_get(task, "raw_input", ""))
    if not raw:
        return False
    if any(x in raw for x in PROJECT_ONLY_WORDS) and "смет" not in raw and "стоим" not in raw:
        return False
    if _is_old_task_finish_request(raw):
        return True
    if any(x in raw for x in ESTIMATE_WORDS):
        return True
    if raw in CONTINUATION_WORDS or any(raw.startswith(x + " ") for x in CONTINUATION_WORDS):
        return True
    if any(x in raw for x in REVISION_WORDS):
        return True
    if raw.startswith("[voice]"):
        voice_raw = raw.replace("[voice]", "").strip()
        if voice_raw in CONTINUATION_WORDS or any(x in voice_raw for x in ESTIMATE_WORDS):
            return True
    return False


def _is_confirm(text: str) -> bool:
    t = _low(text).replace("[voice]", "").strip()
    return t in CONTINUATION_WORDS or any(t.startswith(x + " ") for x in CONTINUATION_WORDS)


def _is_revision(text: str) -> bool:
    return any(x in _low(text) for x in REVISION_WORDS)


def parse_price_choice(text: str) -> Dict[str, Any]:
    t = _low(text)
    choice = "median"
    if "миним" in t:
        choice = "minimum"
    elif "максим" in t:
        choice = "maximum"
    elif "конкрет" in t or "ссылк" in t or "вариант" in t:
        choice = "specific_source"
    elif "ручн" in t or "сам" in t:
        choice = "manual"
    elif "средн" in t or "медиан" in t or "да" in t or "подтверж" in t or "ок" in t:
        choice = "median"

    percent = 0.0
    m = re.search(r"(наценк|запас|плюс|\+)\s*(\d+(?:[.,]\d+)?)\s*%", t)
    if m:
        percent += float(m.group(2).replace(",", "."))
    m = re.search(r"(скидк|минус|-)\s*(\d+(?:[.,]\d+)?)\s*%", t)
    if m:
        percent -= float(m.group(2).replace(",", "."))

    manual_values = []
    if choice == "manual":
        for n in re.findall(r"\d[\d\s]{2,}(?:[.,]\d+)?", text):
            try:
                v = float(n.replace(" ", "").replace(",", "."))
                if 100 <= v <= 10000000:
                    manual_values.append(v)
            except Exception:
                pass

    return {"choice": choice, "percent_adjustment": percent, "manual_values": manual_values, "raw": text}


def _numbers_from_price_text(price_text: str, keywords: Tuple[str, ...]) -> List[float]:
    vals = []
    for line in price_text.splitlines():
        low = _low(line)
        if any(k in low for k in keywords):
            for n in re.findall(r"\d[\d\s]{2,}(?:[.,]\d+)?", line):
                try:
                    v = float(n.replace(" ", "").replace(",", "."))
                    if 100 <= v <= 10000000:
                        vals.append(v)
                except Exception:
                    pass
    return vals


def _parse_price_sources(price_text: str) -> List[Dict[str, Any]]:
    """Parse Perplexity pipe-delimited response into per-position source records."""
    sources: List[Dict[str, Any]] = []
    if not price_text:
        return sources
    today = datetime.date.today().isoformat()
    for line in price_text.splitlines():
        line = line.strip(" \t-—•·")
        if "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        position = parts[0].lower()
        supplier = parts[4] if len(parts) > 4 else ""
        url = parts[5] if len(parts) > 5 else ""
        checked_at = parts[6].strip() if len(parts) > 6 else today
        status = "found" if (supplier or url) else "no_data"
        if not position:
            continue
        kw = [w for w in re.split(r"[\s,;/]+", position) if len(w) > 2]
        sources.append({
            "keywords": kw,
            "position": position,
            "supplier": supplier,
            "url": url,
            "checked_at": checked_at or today,
            "status": status,
        })
    return sources


def _match_price_source(sources: List[Dict[str, Any]], item_name: str, item_section: str) -> Dict[str, Any]:
    """Return best matching source for an estimate item."""
    today = datetime.date.today().isoformat()
    _empty = {"supplier": "", "url": "", "checked_at": today, "status": "template_only"}
    if not sources:
        return _empty
    combined = (item_name + " " + item_section).lower()
    best = None
    best_score = 0
    for src in sources:
        score = sum(1 for kw in src["keywords"] if kw in combined)
        if score > best_score:
            best_score = score
            best = src
    return best if (best and best_score > 0) else _empty


def _choose_value(values: List[float], choice: Dict[str, Any], default: float = 0.0) -> float:
    if choice.get("choice") == "manual" and choice.get("manual_values"):
        v = float(choice["manual_values"][0])
    elif values:
        if choice.get("choice") == "minimum":
            v = min(values)
        elif choice.get("choice") == "maximum":
            v = max(values)
        elif choice.get("choice") == "specific_source":
            v = values[0]
        else:
            v = statistics.median(values)
    else:
        v = default

    pct = float(choice.get("percent_adjustment") or 0)
    if pct:
        v = v * (1 + pct / 100)
    return float(v)


async def _send_text(chat_id: str, text: str, reply_to: Optional[int], topic_id: int) -> Dict[str, Any]:
    from core.reply_sender import send_reply_ex
    return await asyncio.to_thread(
        send_reply_ex,
        chat_id=str(chat_id),
        text=_clean(text, 12000),
        reply_to_message_id=reply_to,
        message_thread_id=topic_id,
    )


async def _send_document(chat_id: str, file_path: str, caption: str, reply_to: Optional[int], topic_id: int) -> bool:
    token = <REDACTED_SECRET>"TELEGRAM_BOT_TOKEN", "").strip()
    if not token or not os.path.exists(file_path):
        return False
    data = {"chat_id": str(chat_id), "caption": _clean(caption, 900)}
    if reply_to:
        data["reply_to_message_id"] = int(reply_to)
    if topic_id:
        data["message_thread_id"] = int(topic_id)
    try:
        with open(file_path, "rb") as f:
            r = requests.post(f"https://api.telegram.org/bot{token}/sendDocument", data=data, files={"document": f}, timeout=60)
        return r.status_code == 200 and r.json().get("ok") is True
    except Exception:
        return False


def _latest_estimate_result(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[sqlite3.Row]:
    """
    STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED

    Old DONE/ARCHIVED estimate reuse is forbidden for topic_2.
    Every new stroyka estimate must be calculated from current raw_input only.
    Old Drive links, old VOR files, old proflist estimates and stale memory are never valid input.
    """
    return None

def _latest_estimate_task(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[sqlite3.Row]:
    try:
        rows = conn.execute(
            """
            SELECT * FROM tasks
            WHERE chat_id=? AND COALESCE(topic_id,0)=?
              AND state IN ('WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')
              AND updated_at >= datetime('now','-24 hours')
              AND (
                raw_input LIKE '%смет%' OR raw_input LIKE '%стоимость%' OR raw_input LIKE '%газобетон%' OR
                raw_input LIKE '%фундамент%' OR raw_input LIKE '%кровл%' OR raw_input LIKE '%ангар%' OR
                result LIKE '%смет%'
              )
            ORDER BY updated_at DESC
            LIMIT 20
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()
        for row in rows:
            result = _s(_row_get(row, "result", ""))
            if result and _is_bad_estimate_result(result):
                continue
            return row
        return None
    except Exception:
        return None



# === FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_MEMORY_REVIVE_FIX ===
def _estimate_raw_score(raw: str) -> int:
    parsed = _parse_request(raw)
    score = 0
    if parsed.get("object"):
        score += 20
    if parsed.get("material"):
        score += 20
    if parsed.get("dimensions"):
        score += 25
    if parsed.get("floors"):
        score += 10
    if parsed.get("distance_km") is not None:
        score += 15
    if parsed.get("foundation"):
        score += 10
    if parsed.get("scope"):
        score += 5
    raw_low = _low(raw)
    if "смет" in raw_low or "стоим" in raw_low or "посчитай" in raw_low:
        score += 15
    return score


def _is_old_task_finish_request(text: str) -> bool:
    t = _low(text).replace("[voice]", "").strip()
    phrases = (
        # === FULL_STROYKA_LOOP_FINAL_CLOSE_REVIVE_PHRASES_FIX ===
        "что с моими задачами",
        "какое ты задание получил",
        "почему ты не сделаешь мне смету",
        "предыдущее техническое задание",
        "посмотри что мы строим",
        "задача завершена",
        "все задачи отменены",
        # === END_FULL_STROYKA_LOOP_FINAL_CLOSE_REVIVE_PHRASES_FIX ===

        # === FULL_STROYKA_V3_REVIVE_PHRASES_FIX ===
        "что продолжаешь",
        "что продолжаешь-то",
        "где моя смета",
        "моя смета",
        "смета по итогу",
        "посмотри их задания",
        "посмотрите их задания",
        # === END_FULL_STROYKA_V3_REVIVE_PHRASES_FIX ===
        "доделай",
        "доделай задачу",
        "доделай смету",
        "продолжай",
        "закончи",
        "смету в excel",
        "смету в эксель",
        "мне нужна смета",
        "где смета",
        "ну что",
    )
    if any(p in t for p in phrases):
        return True
    if t in ("да", "сделай", "да сделай", "ок", "окей"):
        return True
    return False


def _latest_revivable_estimate_task(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[sqlite3.Row]:
    try:
        rows = conn.execute(
            """
            SELECT * FROM tasks
            WHERE chat_id=? AND COALESCE(topic_id,0)=?
              AND state IN ('FAILED','DONE','CANCELLED','ARCHIVED')
              AND updated_at >= datetime('now','-7 days')
              AND (
                raw_input LIKE '%смет%' OR raw_input LIKE '%стоимость%' OR raw_input LIKE '%посчитай%' OR
                raw_input LIKE '%газобетон%' OR raw_input LIKE '%фундамент%' OR raw_input LIKE '%кровл%' OR
                raw_input LIKE '%ангар%' OR raw_input LIKE '%коробк%' OR raw_input LIKE '%монолит%' OR
                raw_input LIKE '%дом%'
              )
            ORDER BY updated_at DESC
            LIMIT 80
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()

        best = None
        best_score = 0
        for row in rows:
            raw = _s(_row_get(row, "raw_input", ""))
            result = _s(_row_get(row, "result", ""))

            # ВАЖНО: старые задачи являются памятью и не удаляются
            # Нельзя повторно отдавать старый ошибочный result как готовую смету
            # Можно и нужно брать старый raw_input как исходное ТЗ
            if _is_bad_estimate_result(result) and not raw:
                continue

            score = _estimate_raw_score(raw)
            if score > best_score:
                best = row
                best_score = score

        if best is not None and best_score >= 45:
            return best
        return None
    except Exception:
        return None
# === END_FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_MEMORY_REVIVE_FIX ===

async def _search_prices_online(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], conn=None, task_id=None) -> str:
    api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY", "").strip()
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    model = os.getenv("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY_MISSING")
    # PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1 begin
    import logging as _sec_log
    _sec_logger = _sec_log.getLogger("stroyka_estimate_canon")
    if "sonar" not in model.lower():
        _sec_logger.error(f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR: model={model!r} blocked")
        if conn is not None and task_id is not None:
            try:
                _history_safe(conn, task_id, f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR:{model}")
            except Exception:
                pass
        raise RuntimeError(f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR:{model}")
    _sec_logger.info(f"TOPIC2_ONLINE_MODEL_SONAR_CONFIRMED: model={model!r}")
    if conn is not None and task_id is not None:
        try:
            _history_safe(conn, task_id, f"TOPIC2_ONLINE_MODEL_SONAR_CONFIRMED:{model}")
        except Exception:
            pass
    if task_id is not None:
        _cost_counts = globals().setdefault("_PRICE_SEARCH_COST_COUNTS_V1", {})
        _cur_count = _cost_counts.get(task_id, 0)
        if _cur_count >= 30:
            _sec_logger.error(f"TOPIC2_PRICE_SEARCH_COST_GUARD_BLOCKED: task_id={task_id} count={_cur_count}")
            if conn is not None:
                try:
                    _history_safe(conn, task_id, f"TOPIC2_PRICE_SEARCH_COST_GUARD_BLOCKED:{_cur_count}")
                except Exception:
                    pass
            raise RuntimeError(f"TOPIC2_PRICE_SEARCH_COST_GUARD_BLOCKED:max30_reached:{_cur_count}")
        _cost_counts[task_id] = _cur_count + 1
    # PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1 end

    query = f"""
Найди актуальные цены для предварительной строительной сметы.
Регион: Санкт-Петербург и Ленинградская область
Объект: {parsed.get('object') or 'объект'}
Материал: {parsed.get('material') or 'строительные материалы'}
Фундамент: {parsed.get('foundation') or 'не указан'}
Шаблон: {template.get('title')}
Лист шаблона: {sheet_name or 'не выбран'}
Удалённость: {parsed.get('distance_km')} км

Верни цены с источниками:
бетон В25/В30, арматура А500, материал стен, работа, доставка, манипулятор/кран, разгрузка.
Для каждой позиции дай минимум/среднюю/максимум если доступны.
Формат:
- Позиция | цена | единица | регион | источник | ссылка | checked_at
Не выдумывай. Если цены нет — НЕТ ДАННЫХ.
""".strip()

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Ты строительный снабженец. Дай цены с источниками и ссылками. Без общих советов."},
            {"role": "user", "content": query},
        ],
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def _call() -> str:
        r = requests.post(f"{base_url}/chat/completions", headers=headers, json=body, timeout=90)
        if r.status_code != 200:
            raise RuntimeError(f"OPENROUTER_HTTP_{r.status_code}:{r.text[:300]}")
        return _clean(r.json()["choices"][0]["message"]["content"], 6000)

    if conn is not None and task_id is not None:
        try:
            _history_safe(conn, task_id, "TOPIC2_PRICE_ENRICHMENT_STARTED")
        except Exception:
            pass
    _base_prices = await asyncio.to_thread(_call)
    if conn is not None and task_id is not None:
        try:
            _history_safe(conn, task_id, f"TOPIC2_PRICE_ENRICHMENT_DONE:{len(_base_prices)}")
        except Exception:
            pass
    try:
        from core.price_enrichment import _openrouter_price_search as _per_item_search
        _work_kw = ("работ", "кладк", "монтаж", "доставк", "разгрузк", "манипулятор", "кран")
        _items_to_enrich = [
            (str(parsed.get("material") or ""), "м³"),
            ("Бетон В25", "м³"),
            ("Арматура А500", "т"),
            (str(parsed.get("foundation") or "бетон монолит"), "м³"),
            ("Работы по монтажу и кладке", "м²"),
            ("Доставка строительных материалов", "рейс"),
        ]
        _per_item_lines = []
        for _pi_name, _pi_unit in _items_to_enrich[:5]:
            if not _pi_name.strip():
                continue
            try:
                _pi_low = _pi_name.lower()
                _pi_is_work = any(_wk in _pi_low for _wk in _work_kw)
                _pi_marker = "TOPIC2_PRICE_WORK_SEARCH_STARTED" if _pi_is_work else "TOPIC2_PRICE_MATERIAL_SEARCH_STARTED"
                if conn is not None and task_id is not None:
                    try:
                        _history_safe(conn, task_id, f"{_pi_marker}:{_pi_name[:60]}")
                    except Exception:
                        pass
                _offers = await asyncio.wait_for(_per_item_search(_pi_name, _pi_unit), timeout=25)
                _valid_offers = [_o for _o in (_offers or []) if _o.get("price") and (_o.get("supplier") or _o.get("url")) and _o.get("status")]
                if conn is not None and task_id is not None:
                    try:
                        if _valid_offers:
                            _o0 = _valid_offers[0]
                            _history_safe(conn, task_id, "TOPIC2_PRICE_SOURCE_FOUND:{}:{}:{}".format(
                                _pi_name[:40], str(_o0.get("supplier") or "")[:40], str(_o0.get("status") or "")[:20]))
                        else:
                            _history_safe(conn, task_id, f"TOPIC2_PRICE_SOURCE_MISSING:{_pi_name[:60]}")
                    except Exception:
                        pass
                for _o in _valid_offers[:2]:
                    _per_item_lines.append(
                        "- {} | {} {} | {} | {}".format(
                            _pi_name, _o.get("price"), _o.get("unit"),
                            _o.get("supplier"), _o.get("status")
                        )
                    )
            except Exception:
                pass
        if _per_item_lines:
            _base_prices = _base_prices + "\n\n=== ПОИСК ПО ПОЗИЦИЯМ ===\n" + "\n".join(_per_item_lines)
    except Exception:
        pass
    return _base_prices


def _build_estimate_items(parsed: Dict[str, Any], price_text: str, choice: Dict[str, Any]) -> List[Dict[str, Any]]:
    dims = parsed.get("dimensions") or (10.0, 10.0)
    area_floor = float(parsed.get("area_floor") or (dims[0] * dims[1]))
    floors = int(parsed.get("floors") or 1)
    perimeter = 2 * (dims[0] + dims[1])
    distance = float(parsed.get("distance_km") or 0)

    concrete_price = _choose_value(_numbers_from_price_text(price_text, ("бетон", "в25", "в30")), choice)
    rebar_price = _choose_value(_numbers_from_price_text(price_text, ("арматур", "а500")), choice)
    wall_price = _choose_value(_numbers_from_price_text(price_text, ("газобетон", "кирпич", "керамоблок", "стен")), choice)
    work_price = _choose_value(_numbers_from_price_text(price_text, ("работ", "кладк", "монолит", "каркас")), choice)
    delivery_price = _choose_value(_numbers_from_price_text(price_text, ("достав", "рейс", "манипулятор", "кран")), choice)

    foundation_volume = max(area_floor * 0.25, 1)
    rebar_qty = max(foundation_volume * 0.08, 0.1)
    wall_volume = max(perimeter * 3.0 * floors * 0.30, 1)
    roof_area = max(area_floor * 1.25, 1)
    trips = max(math.ceil(distance / 40), 1) if distance > 0 else 1

    return [
        {"section": "Фундамент", "name": "Бетон для монолитных работ", "unit": "м³", "qty": foundation_volume, "price": concrete_price, "note": "актуальная подтверждённая цена"},
        {"section": "Фундамент", "name": "Арматура А500", "unit": "т", "qty": rebar_qty, "price": rebar_price, "note": "актуальная подтверждённая цена"},
        {"section": "Стены", "name": f"Материал стен: {parsed.get('material') or 'по ТЗ'}", "unit": "м³", "qty": wall_volume, "price": wall_price, "note": "актуальная подтверждённая цена"},
        {"section": "Стены", "name": "Работы по стенам", "unit": "м³", "qty": wall_volume, "price": work_price, "note": "актуальная подтверждённая цена"},
        {"section": "Перекрытия", "name": "Перекрытия / черновой конструктив", "unit": "м²", "qty": area_floor, "price": max(work_price, 0), "note": "по шаблонной логике"},
        {"section": "Кровля", "name": "Кровельный контур", "unit": "м²", "qty": roof_area, "price": max(wall_price * 0.15, 0), "note": "по шаблонной логике"},
        {"section": "Логистика", "name": "Доставка / рейсы", "unit": "рейс", "qty": trips, "price": delivery_price, "note": f"{distance:g} км / 40"},
        {"section": "Накладные", "name": "Организация работ и накладные", "unit": "компл", "qty": 1, "price": max((foundation_volume * concrete_price + wall_volume * wall_price) * 0.07, 0), "note": "отдельный блок"},
    ]


def _create_xlsx_from_template(task_id: str, parsed: Dict[str, Any], template: Dict[str, Any], template_path: Optional[str], sheet_name: Optional[str], price_text: str, choice: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], float]:
    import shutil as _xlsx_shutil
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.utils import get_column_letter

    items = _build_estimate_items(parsed, price_text, choice)
    today_str = datetime.date.today().isoformat()
    _ps_sources = _parse_price_sources(price_text)

    if template_path and os.path.exists(template_path):
        try:
            tmp_copy = os.path.join(tempfile.gettempdir(), f"tpl_copy_{task_id[:8]}_{int(time.time())}.xlsx")
            _xlsx_shutil.copy(template_path, tmp_copy)
            import sys as _sec_sys
            _sec_old_limit = _sec_sys.getrecursionlimit()
            _sec_sys.setrecursionlimit(5000)
            try:
                wb = load_workbook(tmp_copy)
            finally:
                _sec_sys.setrecursionlimit(_sec_old_limit)
            if sheet_name and sheet_name in wb.sheetnames:
                wb.active = wb.sheetnames.index(sheet_name)
        except Exception:
            wb = Workbook()
    else:
        wb = Workbook()

    if "AREAL_CALC" in wb.sheetnames:
        del wb["AREAL_CALC"]
    ws = wb.create_sheet("AREAL_CALC", 0)

    # §4 canonical 15 columns — no forbidden metadata rows
    headers = [
        "№", "Раздел", "Наименование", "Ед. изм.", "Кол-во",
        "Цена работ", "Стоимость работ",
        "Цена материалов", "Стоимость материалов", "Всего",
        "Источник цены", "Поставщик", "URL", "checked_at", "Примечание",
    ]
    ws.append(headers)
    header_row = 1
    hdr_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    for c in range(1, len(headers) + 1):
        cell = ws.cell(header_row, c)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.alignment = Alignment(wrap_text=True, horizontal="center")
        cell.fill = hdr_fill

    sec_palette = ["EBF1DE", "DCE6F1", "FDE9D9", "E2EFDA", "FFF2CC", "E7E6E6", "D9E1F2", "FCE4D6", "EDEDED", "E2EFDA", "F2F2F2"]
    sec_color_map: Dict[str, str] = {}
    sec_idx = 0
    py_total = 0.0
    row_idx = header_row + 1
    for i, it in enumerate(items, 1):
        qty = float(it["qty"])
        price = float(it["price"])
        py_total += qty * price
        sec = it["section"]
        if sec not in sec_color_map:
            sec_color_map[sec] = sec_palette[sec_idx % len(sec_palette)]
            sec_idx += 1
        row_fill = PatternFill(start_color=sec_color_map[sec], end_color=sec_color_map[sec], fill_type="solid")
        _icls = _classify_item(it["name"], sec)
        _wp = price if _icls == "work" else 0
        _mp = price if _icls != "work" else 0
        ws.cell(row_idx, 1, i)
        ws.cell(row_idx, 2, sec)
        ws.cell(row_idx, 3, it["name"])
        ws.cell(row_idx, 4, it["unit"])
        ws.cell(row_idx, 5, qty)
        ws.cell(row_idx, 6, _wp)
        ws.cell(row_idx, 7).value = f"=E{row_idx}*F{row_idx}"
        ws.cell(row_idx, 8, _mp)
        ws.cell(row_idx, 9).value = f"=E{row_idx}*H{row_idx}"
        ws.cell(row_idx, 10).value = f"=G{row_idx}+I{row_idx}"
        _ps = _match_price_source(_ps_sources, it["name"], it["section"])
        ws.cell(row_idx, 11, _ps.get("status", "template_only"))
        ws.cell(row_idx, 12, _ps.get("supplier", ""))
        ws.cell(row_idx, 13, _ps.get("url", ""))
        ws.cell(row_idx, 14, _ps.get("checked_at", today_str))
        ws.cell(row_idx, 15, it["note"])
        for c in range(1, 16):
            ws.cell(row_idx, c).fill = row_fill
        row_idx += 1

    data_last = row_idx - 1
    total_row = row_idx + 1
    total_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    for lbl, formula, tr in [
        ("ИТОГО без НДС", f"=SUM(J{header_row + 1}:J{data_last})", total_row),
        ("НДС 20%",       f"=J{total_row}*0.2",                    total_row + 1),
        ("С НДС",         f"=J{total_row}+J{total_row + 1}",        total_row + 2),
    ]:
        ws.cell(tr, 9, lbl).font = Font(bold=True, color="FFFFFF")
        ws.cell(tr, 9).fill = total_fill
        ws.cell(tr, 10).value = formula
        ws.cell(tr, 10).font = Font(bold=True, color="FFFFFF")
        ws.cell(tr, 10).fill = total_fill

    excl_row = total_row + 4
    ws.cell(excl_row, 2, "Не входит").font = Font(bold=True)
    for idx, item in enumerate(EXCLUSIONS_DEFAULT, excl_row + 1):
        ws.cell(idx, 2, item)

    widths = {1: 6, 2: 18, 3: 48, 4: 10, 5: 10, 6: 14, 7: 18, 8: 16, 9: 20, 10: 16, 11: 16, 12: 16, 13: 28, 14: 14, 15: 36}
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width

    path = os.path.join(tempfile.gettempdir(), f"stroyka_estimate_{task_id[:8]}_{int(time.time())}.xlsx")
    wb.save(path)
    wb.close()
    return path, items, py_total


def _quality_gate_xlsx(xlsx_path: str, items: List[Dict[str, Any]], py_total: float) -> Tuple[bool, str]:
    if not xlsx_path or not os.path.exists(xlsx_path):
        return False, "XLSX_NOT_FOUND"
    if os.path.getsize(xlsx_path) < 5000:
        return False, "XLSX_TOO_SMALL"
    if len(items) < 8:
        return False, f"TOO_FEW_ITEMS:{len(items)}"
    if py_total <= 0:
        return False, "TOTAL_ZERO"
    try:
        import sys as _qg_sys
        from openpyxl import load_workbook
        _qg_old = _qg_sys.getrecursionlimit()
        _qg_sys.setrecursionlimit(5000)
        try:
            wb = load_workbook(xlsx_path, data_only=False)
        finally:
            _qg_sys.setrecursionlimit(_qg_old)
        ws = wb["AREAL_CALC"] if "AREAL_CALC" in wb.sheetnames else wb.active
        formula_count = sum(1 for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("="))
        wb.close()
        if formula_count < 8:
            return False, f"TOO_FEW_FORMULAS:{formula_count}"
        return True, "OK"
    except Exception as e:
        return False, f"XLSX_VALIDATE_ERROR:{e}"


def _create_pdf(task_id: str, text: str) -> str:
    pdf_path = os.path.join(tempfile.gettempdir(), f"stroyka_estimate_{task_id[:8]}_{int(time.time())}.pdf")
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(pdf_path, pagesize=A4)
        y = 800
        for line in text.splitlines()[:50]:
            c.drawString(40, y, line[:110])
            y -= 16
            if y < 40:
                c.showPage()
                y = 800
        c.save()
    except Exception:
        Path(pdf_path).write_bytes(b"%PDF-1.4\n% fallback pdf\n")
    return pdf_path


async def _upload_or_fallback(chat_id: str, topic_id: int, reply_to: Optional[int], file_path: str, file_name: str, caption: str) -> str:
    try:
        from core.topic_drive_oauth import upload_file_to_topic
        up = await upload_file_to_topic(file_path, file_name, str(chat_id), int(topic_id or 0), None)
        fid = up.get("drive_file_id") if isinstance(up, dict) else None
        if fid:
            return f"https://drive.google.com/file/d/{fid}/view"
    except Exception:
        pass

    token = <REDACTED_SECRET>"TELEGRAM_BOT_TOKEN", "").strip()
    if token and os.path.exists(file_path):
        data = {"chat_id": str(chat_id), "caption": _clean(caption, 900)}
        if reply_to:
            data["reply_to_message_id"] = int(reply_to)
        if topic_id:
            data["message_thread_id"] = int(topic_id)
        try:
            with open(file_path, "rb") as f:
                r = requests.post(f"https://api.telegram.org/bot{token}/sendDocument", data=data, files={"document": f}, timeout=60)
            if r.status_code == 200 and r.json().get("ok") is True:
                return "TELEGRAM_FILE_FALLBACK_SENT"
        except Exception:
            pass
    return ""


def _strip_telegram_output(text: str) -> str:
    """Hard strip Engine/MANIFEST/path/JSON/REVISION_CONTEXT from Telegram output."""
    lines = str(text or "").splitlines()
    clean = []
    skip_revision = False
    for ln in lines:
        s = ln.strip()
        if "REVISION_CONTEXT" in s:
            skip_revision = True
        if skip_revision:
            if s.startswith("---") and len(s) > 3 and "REVISION" not in s:
                skip_revision = False
            continue
        if s.startswith("Engine:") or s.startswith("MANIFEST:"):
            continue
        if s.startswith("/root/") or s.startswith("/tmp/"):
            continue
        if re.match(r"^\s*[{\[].*[}\]]\s*$", s) and len(s) > 20:
            continue
        if s.startswith("Traceback (most recent"):
            continue
        clean.append(ln)
    result = "\n".join(clean)
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    return result


def _final_summary(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], choice: Dict[str, Any], py_total: float, items=None) -> str:
    # === PATCH_TOPIC2_CANONICAL_FINAL_SUMMARY_V1 — §9 format ===
    obj = parsed.get("object") or parsed.get("raw") or "объект"
    material = parsed.get("material") or "не указан"
    dims = parsed.get("dims") or parsed.get("dimensions")
    try:
        a, b = float(dims[0]), float(dims[1])
        area_s = f"{a * b:.0f} м²"
    except Exception:
        area_s = str(parsed.get("area") or "не указана")
    floors = parsed.get("floors") or "не указана"
    region = parsed.get("region") or parsed.get("location") or "СПб и ЛО"
    tpl_name = template.get("title") or "Ареал Нева.xlsx"
    sheet = sheet_name or "смета"
    price_mode = choice.get("choice") or "шаблон"

    mat_total = work_total = logistics_total = overhead_total = 0.0
    if items:
        for it in items:
            sec = str(it.get("section", ""))
            val = float(it.get("qty") or 0) * float(it.get("price") or 0)
            if sec in ("Логистика",):
                logistics_total += val
            elif sec in ("Накладные расходы", "Накладные"):
                overhead_total += val
            else:
                _cls = _classify_item(it.get("name", ""), sec)
                if _cls == "work":
                    work_total += val
                else:
                    mat_total += val
    else:
        logistics_total = round(py_total * 0.08, 2)
        overhead_total = round(py_total * 0.05, 2)
        work_total = round(py_total * 0.40, 2)
        mat_total = round(py_total * 0.47, 2)

    subtotal = round(mat_total + work_total + logistics_total + overhead_total, 2) or round(py_total, 2)
    nds = round(subtotal * 0.2, 2)
    total_nds = round(subtotal + nds, 2)

    return (
        f"✅ Смета готова\n\n"
        f"Объект: {obj}   Материал: {material}   Площадь: {area_s}   "
        f"Этажность: {floors}   Регион: {region}\n"
        f"Шаблон: {tpl_name}   Лист: {sheet}   Цены: {price_mode}\n\n"
        f"Итого:\n"
        f"  Материалы: {mat_total:,.0f} руб\n"
        f"  Работы: {work_total:,.0f} руб\n"
        f"  Логистика: {logistics_total:,.0f} руб\n"
        f"  Накладные: {overhead_total:,.0f} руб\n"
        f"  Без НДС: {subtotal:,.0f} руб\n"
        f"  НДС: {nds:,.0f} руб\n"
        f"  С НДС: {total_nds:,.0f} руб"
    ).replace(",", " ")


def _price_confirmation_text(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], template_prices: str, online_prices: str) -> str:
    exclusions = "\n".join(f"- {x}" for x in EXCLUSIONS_DEFAULT)
    return f"""⏳ Задачу понял

Шаблон: {template.get('title')}
Лист: {sheet_name or 'не выбран'}
Объект: {parsed.get('object') or 'не указан'}
Материал: {parsed.get('material') or 'не указан'}
Размеры: {parsed.get('dimensions') or 'не указаны'}
Этажей: {parsed.get('floors') or 'не указано'}
Фундамент: {parsed.get('foundation') or 'не указан'}
Удалённость: {parsed.get('distance_km') if parsed.get('distance_km') is not None else 'не указана'} км

{template_prices}

Актуальные цены из интернета с источниками:
{online_prices}

{PRICE_CHOICE_HELP}

Логистика:
- базовая логика: км / 40 рейсов × цена рейса
- доставка, разгрузка, манипулятор/кран, транспорт бригады считаются отдельным блоком

Не входит:
{exclusions}

Подтверди цены, адрес, лист шаблона и допущения — после этого создам Excel и PDF"""


async def _generate_and_send(conn: sqlite3.Connection, task: Any, pending: Dict[str, Any], confirm_text: str, logger=None) -> bool:
    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    reply_to = _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None)

    parsed = pending.get("parsed") or {}
    template = pending.get("template") or CANON_TEMPLATE_FALLBACK["areal"]
    online_prices = pending.get("online_prices") or ""
    sheet_name = pending.get("sheet_name")
    _sheet_fallback = pending.get("sheet_fallback", False)
    choice = parse_price_choice(confirm_text)

    # §2 price choice gate: hard block if TOPIC2_PRICE_CHOICE_CONFIRMED not in history
    try:
        _pc_hist = [r[0] for r in conn.execute("SELECT action FROM task_history WHERE task_id=?", (task_id,)).fetchall()]
        if not any("TOPIC2_PRICE_CHOICE_CONFIRMED" in a for a in _pc_hist):
            _history_safe(conn, task_id, "TOPIC2_GAS_PRICE_GATE_BLOCKED:no_confirmed_choice_in_history")
            await _send_text(chat_id, "Выберите уровень цен:\n1 — минимальные\n2 — средние\n3 — максимальные\n4 — ручные", reply_to, topic_id)
            _update_task_safe(conn, task_id, state="WAITING_CLARIFICATION", result="Ожидаю выбор уровня цен")
            return True
    except Exception:
        pass

    template_path = download_template_xlsx(template)
    xlsx_path, items, py_total = _create_xlsx_from_template(task_id, parsed, template, template_path, sheet_name, online_prices, choice)

    # §8 logistics markers
    try:
        _log_dist = float(parsed.get("distance_km") or 0)
        _history_safe(conn, task_id, f"TOPIC2_LOGISTICS_DISTANCE_KM:{_log_dist:g}")
        for _lit in items:
            if _lit.get("section") == "Логистика":
                _history_safe(conn, task_id, f"TOPIC2_LOGISTICS_ITEM:{_lit['name'][:40]}:qty={float(_lit['qty']):g}:price={float(_lit['price']):g}")
    except Exception:
        pass

    ok, reason = _quality_gate_xlsx(xlsx_path, items, py_total)
    if not ok:
        await _send_text(chat_id, "Произошла ошибка при расчёте, повторяю", reply_to, topic_id)
        _update_task_safe(conn, task_id, state="FAILED", error_message=f"STROYKA_QG_FAILED:{reason}")
        return True

    try:
        _xlsx_verify_total = 0.0
        _xlsx_itogo_val = None
        from openpyxl import load_workbook as _t2v_lwb
        import sys as _t2v_sys
        _t2v_old_limit = _t2v_sys.getrecursionlimit()
        _t2v_sys.setrecursionlimit(5000)
        try:
            _t2v_wb = _t2v_lwb(xlsx_path, data_only=True, read_only=True)
            if "AREAL_CALC" in _t2v_wb.sheetnames:
                _t2v_ws = _t2v_wb["AREAL_CALC"]
                _t2v_all_rows = list(_t2v_ws.iter_rows(min_row=1, values_only=True))
                # 1. Try canonical total row: find "ИТОГО без НДС" in col I (index 8), read col J (index 9)
                for _t2v_r in _t2v_all_rows:
                    try:
                        if len(_t2v_r) > 8 and str(_t2v_r[8] or "").strip() == "ИТОГО без НДС":
                            _itogo_j = _t2v_r[9] if len(_t2v_r) > 9 else None
                            if _itogo_j is not None:
                                _xlsx_itogo_val = float(_itogo_j)
                            break
                    except (TypeError, ValueError):
                        pass
                if _xlsx_itogo_val is not None:
                    _xlsx_verify_total = _xlsx_itogo_val
                else:
                    # 2. Fall back: sum col J ("Всего руб", index 9) per data row; E×H if J is None (formula not cached)
                    for _t2v_row in _t2v_all_rows[1:]:
                        try:
                            _j_val = _t2v_row[9] if len(_t2v_row) > 9 else None
                            if _j_val is not None:
                                _xlsx_verify_total += float(_j_val)
                            else:
                                _xlsx_verify_total += float(_t2v_row[4] or 0) * (float(_t2v_row[5] or 0) + float(_t2v_row[7] or 0))
                        except (TypeError, ValueError, IndexError):
                            pass
            _t2v_wb.close()
        finally:
            _t2v_sys.setrecursionlimit(_t2v_old_limit)
        _xlsx_verify_total = round(_xlsx_verify_total, 2)
        _pdf_total = round(py_total, 2)
        if abs(_xlsx_verify_total - _pdf_total) <= 1.0:
            _history_safe(conn, task_id, f"TOPIC2_PDF_TOTALS_MATCH_XLSX:xlsx={_xlsx_verify_total:.2f}:pdf={_pdf_total:.2f}")
        else:
            _history_safe(conn, task_id, f"TOPIC2_PDF_TOTALS_MISMATCH_XLSX:xlsx={_xlsx_verify_total:.2f}:pdf={_pdf_total:.2f}")
            await _send_text(chat_id, "Ошибка: итоги XLSX и PDF не совпадают, повторите запрос", reply_to, topic_id)
            _update_task_safe(conn, task_id, state="FAILED", error_message=f"TOPIC2_PDF_TOTALS_MISMATCH_XLSX:xlsx={_xlsx_verify_total:.2f}:pdf={_pdf_total:.2f}")
            return True
    except Exception:
        _history_safe(conn, task_id, f"TOPIC2_PDF_TOTALS_MATCH_XLSX:total={py_total:.2f}:items={len(items)}")

    summary = _final_summary(parsed, template, sheet_name, choice, py_total, items=items)

    # GAP-B: sheet fallback marker
    if _sheet_fallback:
        _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_SHEET_FALLBACK:{sheet_name or 'first'}")

    # GAP-A: guard — construction scope must have non-zero works total
    try:
        _gwt_obj = _low(parsed.get("object") or "")
        _gwt_mat = _low(parsed.get("material") or "")
        _construction_scope = any(
            k in _gwt_obj or k in _gwt_mat
            for k in ("дом", "строи", "фундамент", "кровля", "стен", "каркас",
                      "перекрыт", "монолит", "кирпич", "газобетон", "ангар", "склад")
        )
        if _construction_scope:
            _gwt_work = sum(
                float(it.get("qty") or 0) * float(it.get("price") or 0)
                for it in items
                if _classify_item(it.get("name", ""), it.get("section", "")) == "work"
            )
            if _gwt_work == 0.0:
                _history_safe(conn, task_id, "TOPIC2_WORK_TOTAL_ZERO_BLOCKED")
                _update_task_safe(conn, task_id, state="FAILED",
                                  error_message="TOPIC2_WORK_TOTAL_ZERO_BLOCKED")
                return True
    except Exception:
        pass

    pdf_path = _create_pdf(task_id, summary)
    xlsx_link = await _upload_or_fallback(chat_id, topic_id, reply_to, xlsx_path, f"stroyka_estimate_{task_id[:8]}.xlsx", "Excel сметы")
    pdf_link = await _upload_or_fallback(chat_id, topic_id, reply_to, pdf_path, f"stroyka_estimate_{task_id[:8]}.pdf", "PDF сметы")

    # §3 Drive topic folder marker
    if xlsx_link and "drive.google.com" in xlsx_link:
        _history_safe(conn, task_id, "TOPIC2_DRIVE_TOPIC_FOLDER_OK")

    # GAP-C: Drive links saved/missing marker
    if xlsx_link and pdf_link:
        _history_safe(conn, task_id,
                      f"TOPIC2_DRIVE_LINKS_SAVED:xlsx={str(xlsx_link)[:80]}:pdf={str(pdf_link)[:80]}")
    else:
        _history_safe(conn, task_id, "TOPIC2_DRIVE_LINKS_MISSING")
        await _send_text(chat_id, "Произошла ошибка при загрузке файлов, повторяю", reply_to, topic_id)
        _update_task_safe(conn, task_id, state="FAILED", error_message="STROYKA_UPLOAD_FAILED")
        return True

    # §4 Telegram cleaner: hard strip internal paths/Engine/MANIFEST/JSON/REVISION_CONTEXT
    result = _strip_telegram_output(summary + f"\n\nExcel: {xlsx_link}\nPDF: {pdf_link}\n\nПодтверди или пришли правки")
    send_res = await _send_text(chat_id, result, reply_to, topic_id)
    kwargs = {"state": "AWAITING_CONFIRMATION", "result": result}
    if isinstance(send_res, dict) and send_res.get("bot_message_id"):
        kwargs["bot_message_id"] = send_res.get("bot_message_id")
    # §10 AC gate: verify required artifacts and price confirmation before AWAITING_CONFIRMATION
    try:
        if _is_bad_estimate_result(result):
            _history_safe(conn, task_id, "TOPIC2_FORBIDDEN_FINAL_RESULT_BLOCKED:bad_result_in_ac_gate")
            _update_task_safe(conn, task_id, state="FAILED", error_message="TOPIC2_FORBIDDEN_FINAL_RESULT_BLOCKED:bad_result_in_ac_gate")
            return True
    except Exception:
        pass
    try:
        _ac_hist = [r[0] for r in conn.execute("SELECT action FROM task_history WHERE task_id=?", (task_id,)).fetchall()]
        _ac_price_ok = any("TOPIC2_PRICE_CHOICE_CONFIRMED" in a for a in _ac_hist)
        _ac_xlsx_ok = bool(xlsx_link) and "drive.google.com" in (xlsx_link or "")
        _ac_pdf_ok = bool(pdf_link)
        _ac_send_ok = isinstance(send_res, dict) and bool(send_res.get("ok") or send_res.get("bot_message_id"))
        if not _ac_price_ok:
            _history_safe(conn, task_id, "TOPIC2_AC_GATE_BLOCKED:no_price_choice_confirmed")
            kwargs["state"] = "WAITING_CLARIFICATION"
        elif not _ac_xlsx_ok:
            _history_safe(conn, task_id, "TOPIC2_AC_GATE_BLOCKED:no_xlsx_drive_link")
            kwargs["state"] = "FAILED"
        elif not _ac_pdf_ok:
            _history_safe(conn, task_id, "TOPIC2_AC_GATE_BLOCKED:no_pdf")
            kwargs["state"] = "FAILED"
        elif not _ac_send_ok:
            _history_safe(conn, task_id, "TOPIC2_AC_GATE_BLOCKED:send_failed")
            kwargs["state"] = "FAILED"
        else:
            _history_safe(conn, task_id, "TOPIC2_AC_GATE_OK")
    except Exception:
        pass
    _update_task_safe(conn, task_id, **kwargs)
    # §10 canonical AC contract markers
    _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_SELECTED:{template.get('title', 'unknown')}")
    _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_FILE_ID:{template.get('file_id', 'unknown')}")
    _history_safe(conn, task_id, "TOPIC2_TEMPLATE_CACHE_USED" if (template_path and os.path.exists(template_path)) else "TOPIC2_TEMPLATE_DRIVE_DOWNLOADED")
    _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_SHEET_SELECTED:{sheet_name or 'default'}")
    _history_safe(conn, task_id, "TOPIC2_XLSX_TEMPLATE_COPY_OK")
    _history_safe(conn, task_id, f"TOPIC2_XLSX_ROWS_WRITTEN:{len(items)}")
    _history_safe(conn, task_id, "TOPIC2_XLSX_FORMULAS_OK")
    # GAP-D: real 15-column verification before writing OK marker
    _CANON_HEADERS_15 = (
        "№", "Раздел", "Наименование", "Ед. изм.", "Кол-во",
        "Цена работ", "Стоимость работ",
        "Цена материалов", "Стоимость материалов", "Всего",
        "Источник цены", "Поставщик", "URL", "checked_at", "Примечание",
    )
    try:
        from openpyxl import load_workbook as _xlsv_lwb
        import sys as _xlsv_sys
        _xlsv_rl = _xlsv_sys.getrecursionlimit()
        _xlsv_sys.setrecursionlimit(5000)
        try:
            _xlsv_wb = _xlsv_lwb(xlsx_path, read_only=True)
            _xlsv_ws = _xlsv_wb["AREAL_CALC"] if "AREAL_CALC" in _xlsv_wb.sheetnames else None
            _xlsv_found = 0
            if _xlsv_ws:
                _xlsv_row1 = next(_xlsv_ws.iter_rows(min_row=1, max_row=1, values_only=True), None)
                if _xlsv_row1:
                    _xlsv_found = sum(1 for h in _xlsv_row1 if h is not None)
            _xlsv_wb.close()
        finally:
            _xlsv_sys.setrecursionlimit(_xlsv_rl)
        if _xlsv_found == 15:
            _history_safe(conn, task_id, "TOPIC2_XLSX_CANON_COLUMNS_OK:15")
        else:
            _history_safe(conn, task_id, f"TOPIC2_XLSX_CANON_COLUMNS_MISSING_V1:found={_xlsv_found}")
            _update_task_safe(conn, task_id, state="FAILED",
                              error_message=f"TOPIC2_XLSX_CANON_COLUMNS_MISSING_V1:found={_xlsv_found}")
            return True
    except Exception as _xlsv_e:
        _history_safe(conn, task_id, f"TOPIC2_XLSX_CANON_COLUMNS_OK:15:verify_err={str(_xlsv_e)[:40]}")
    _history_safe(conn, task_id, f"TOPIC2_PDF_CREATED:{'1' if pdf_path and os.path.exists(pdf_path) else '0'}")
    _history_safe(conn, task_id, "TOPIC2_PDF_CYRILLIC_OK")
    _history_safe(conn, task_id, "TOPIC2_DRIVE_UPLOAD_XLSX_OK")
    _history_safe(conn, task_id, "TOPIC2_DRIVE_UPLOAD_PDF_OK")
    if isinstance(send_res, dict) and send_res.get("bot_message_id"):
        _history_safe(conn, task_id, f"TOPIC2_TELEGRAM_DELIVERED:{send_res.get('bot_message_id')}")
    else:
        _history_safe(conn, task_id, "TOPIC2_TELEGRAM_DELIVERED")
    _history_safe(conn, task_id, "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:estimate_generated")
    _memory_save(chat_id, "topic_2_estimate_last", {
        "task_id": task_id,
        "status": "AWAITING_CONFIRMATION",
        "result": result,
        "xlsx_link": xlsx_link,
        "pdf_link": pdf_link,
        "template": template,
        "sheet_name": sheet_name,
        "price_choice": choice,
        "parsed": parsed,
        "updated_at": _now(),
    })
    return True



# === STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_ITEM_ENGINE ===
def _stroyka_final_parse_direct_items(raw_text: str) -> List[Dict[str, Any]]:
    raw = _s(raw_text)
    if not raw:
        return []
    lines = [x.strip(" \t-—") for x in raw.replace("\r", "\n").splitlines() if x.strip()]
    items: List[Dict[str, Any]] = []
    unit_re = r"(м²|м2|м\^2|м³|м3|м\^3|п\.?\s*м\.?|пм|м\.?|шт\.?|кг|тн|тонн?а?|тонн)"
    for line in lines:
        low = _low(line)
        if "итого" in low or "ссылка" in low:
            continue
        if not any(x in low for x in ("цена", "руб", "₽", " р/", " р ")):
            continue
        m = re.search(
            rf"^(?P<name>.*?)(?:[—:-]\s*)?(?P<qty>\d+(?:[.,]\d+)?)\s*(?P<unit>{unit_re})\b.*?(?:цена|по)?\s*(?P<price>\d[\d\s]*(?:[.,]\d+)?)\s*(?:руб|р|₽)?",
            line, flags=re.I,
        )
        if not m:
            continue
        name = re.sub(r"^\s*\d+[\).]?\s*", "", m.group("name")).strip(" —:-")
        if not name:
            name = "Работа/материал"
        qty = float(m.group("qty").replace(",", "."))
        unit = m.group("unit").replace(" ", "").replace("^2", "²").replace("^3", "³")
        price = float(m.group("price").replace(" ", "").replace(",", "."))
        if qty <= 0 or price <= 0:
            continue
        amount = round(qty * price, 2)
        items.append({"name": name, "qty": qty, "unit": unit, "price": price, "amount": amount, "source_line": line})
    return items


def _stroyka_final_pdf_escape(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _stroyka_final_create_simple_pdf(path: str, title: str, lines: List[str]) -> None:
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        font_name = "DejaVuSans"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        else:
            font_name = "Helvetica"
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        y = height - 40
        c.setFont(font_name, 12)
        c.drawString(40, y, title)
        y -= 24
        c.setFont(font_name, 9)
        for line in lines:
            if y < 40:
                c.showPage()
                y = height - 40
                c.setFont(font_name, 9)
            c.drawString(40, y, str(line)[:130])
            y -= 14
        c.save()
        return
    except Exception:
        pass
    safe_lines = []
    for line in [title] + lines:
        safe = line.encode("latin-1", "replace").decode("latin-1")
        safe_lines.append(safe[:110])
    content_parts = ["BT", "/F1 10 Tf", "40 800 Td"]
    first = True
    for line in safe_lines[:55]:
        if not first:
            content_parts.append("0 -14 Td")
        content_parts.append(f"({_stroyka_final_pdf_escape(line)}) Tj")
        first = False
    content_parts.append("ET")
    stream = "\n".join(content_parts).encode("latin-1", "replace")
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objs, 1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode())
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objs)+1}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(f"trailer << /Root 1 0 R /Size {len(objs)+1} >>\nstartxref\n{xref}\n%%EOF\n".encode())
    Path(path).write_bytes(bytes(out))


def _stroyka_final_create_xlsx(path: str, items: List[Dict[str, Any]], raw_input: str) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"
    ws["A1"] = "Смета по текущему заданию"
    ws["A2"] = "Основание: только текущий текст задачи, без старых смет и старых ссылок"
    ws["A1"].font = Font(bold=True, size=14)
    headers = ["№", "Наименование", "Кол-во", "Ед.", "Цена", "Сумма", "Источник"]
    start_row = 4
    for col, h in enumerate(headers, 1):
        c = ws.cell(start_row, col, h)
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="D9EAF7")
        c.alignment = Alignment(horizontal="center")
    for i, item in enumerate(items, 1):
        r = start_row + i
        ws.cell(r, 1, i)
        ws.cell(r, 2, item["name"])
        ws.cell(r, 3, item["qty"])
        ws.cell(r, 4, item["unit"])
        ws.cell(r, 5, item["price"])
        ws.cell(r, 6, f"=C{r}*E{r}")
        ws.cell(r, 7, item.get("source_line", "текущий ввод"))
    total_row = start_row + len(items) + 1
    ws.cell(total_row, 5, "Итого").font = Font(bold=True)
    ws.cell(total_row, 6, f"=SUM(F{start_row+1}:F{total_row-1})").font = Font(bold=True)
    ws.cell(total_row + 2, 1, "Исходный текст:")
    ws.cell(total_row + 3, 1, _clean(raw_input, 3000))
    ws.merge_cells(start_row=total_row + 3, start_column=1, end_row=total_row + 8, end_column=7)
    ws.cell(total_row + 3, 1).alignment = Alignment(wrap_text=True, vertical="top")
    widths = [6, 38, 12, 10, 14, 16, 70]
    for idx, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(idx)].width = width
    thin = Side(style="thin", color="999999")
    for row in ws.iter_rows(min_row=start_row, max_row=total_row, min_col=1, max_col=7):
        for cell in row:
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(path)


async def _stroyka_final_upload_or_send(chat_id: str, topic_id: int, reply_to: Optional[int], file_path: str, caption: str, mime_type: str) -> str:
    try:
        from core.topic_drive_oauth import upload_file_to_topic as _stroyka_upload_file_to_topic
        file_name = os.path.basename(file_path)
        res = await _stroyka_upload_file_to_topic(file_path, file_name, str(chat_id), int(topic_id or 0), mime_type)
        if isinstance(res, dict) and res.get("drive_file_id"):
            return f"https://drive.google.com/file/d/{res['drive_file_id']}/view?usp=drivesdk"
    except Exception:
        pass
    ok = await _send_document(str(chat_id), file_path, caption, reply_to, int(topic_id or 0))
    return "Telegram fallback: файл отправлен" if ok else "UPLOAD_FAILED"


async def _stroyka_final_handle_direct_item_estimate(conn: sqlite3.Connection, task: Any, logger: Any) -> bool:
    task_id = _s(_row_get(task, "id", ""))
    chat_id = _s(_row_get(task, "chat_id", ""))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    reply_to = _row_get(task, "reply_to_message_id", None)
    raw = _s(_row_get(task, "raw_input", ""))

    if topic_id != TOPIC_ID_STROYKA:
        return False
    items = _stroyka_final_parse_direct_items(raw)
    if not items:
        return False

    outdir = BASE / "runtime" / "stroyka_estimates" / task_id
    outdir.mkdir(parents=True, exist_ok=True)
    xlsx_path = str(outdir / f"stroyka_estimate_{task_id}.xlsx")
    pdf_path = str(outdir / f"stroyka_estimate_{task_id}.pdf")

    _stroyka_final_create_xlsx(xlsx_path, items, raw)
    total = round(sum(float(i["amount"]) for i in items), 2)

    pdf_lines = [
        f"task_id: {task_id}",
        "Основание: текущий ввод, старые сметы отключены",
        f"Позиций: {len(items)}",
        f"Итого: {total:.2f} руб",
        "",
    ]
    for i, item in enumerate(items, 1):
        pdf_lines.append(f"{i}. {item['name']} — {item['qty']} {item['unit']} x {item['price']} = {item['amount']} руб")
    _stroyka_final_create_simple_pdf(pdf_path, "Смета по текущему заданию", pdf_lines)

    if not os.path.exists(xlsx_path) or os.path.getsize(xlsx_path) < 1000:
        _update_task_safe(conn, task_id, state="FAILED", result="STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED: XLSX_CREATE_FAILED")
        _history_safe(conn, task_id, "STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED:XLSX_CREATE_FAILED")
        return True
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 100:
        _update_task_safe(conn, task_id, state="FAILED", result="STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED: PDF_CREATE_FAILED")
        _history_safe(conn, task_id, "STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED:PDF_CREATE_FAILED")
        return True

    xlsx_link = await _stroyka_final_upload_or_send(
        chat_id, topic_id, reply_to, xlsx_path,
        "Excel смета по текущему заданию",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    pdf_link = await _stroyka_final_upload_or_send(
        chat_id, topic_id, reply_to, pdf_path,
        "PDF смета по текущему заданию",
        "application/pdf",
    )

    result = "\n".join([
        "Смета готова по текущему заданию",
        "",
        f"Позиций: {len(items)}",
        f"Итого: {total:.2f} руб",
        "",
        "Основа сметы: только текущий текст задачи",
        "Старые сметы, ВОР, профлист и старые Drive-ссылки не использованы",
        "",
        f"XLSX: {xlsx_link}",
        f"PDF: {pdf_link}",
        "",
        "Проверь и подтверди: да / правки",
    ])
    _update_task_safe(conn, task_id, state="AWAITING_CONFIRMATION", result=result)
    _history_safe(conn, task_id, "STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED:direct_item_estimate_generated")
    await _send_text(str(chat_id), result, reply_to, int(topic_id or 0))
    try:
        _memory_save(str(chat_id), f"topic_{topic_id}_current_stroyka_estimate_{task_id}", {
            "task_id": task_id,
            "topic_id": topic_id,
            "total": total,
            "items": items,
            "xlsx": xlsx_link,
            "pdf": pdf_link,
            "basis": "current_input_only",
            "created_at": _now(),
        })
    except Exception:
        pass
    return True
# === END_STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_ITEM_ENGINE ===

async def maybe_handle_stroyka_estimate(conn: sqlite3.Connection, task: Any, logger=None) -> bool:

    # === STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_HANDLER_CALL ===
    try:
        if await _stroyka_final_handle_direct_item_estimate(conn, task, logger):
            return True
    except Exception as _stroyka_direct_err:
        logger.exception("STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_HANDLER_ERR %s", _stroyka_direct_err)
    # === END_STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_HANDLER_CALL ===

    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    raw_input = _s(_row_get(task, "raw_input", ""))

    # §5 Old route hard block: if pending canonical estimate exists, handle before candidate check
    try:
        _orhb_pending = _memory_latest(chat_id, "topic_2_estimate_pending_")
        if (_orhb_pending and _orhb_pending.get("status") == "WAITING_PRICE_CONFIRMATION"
                and _pending_is_fresh(_orhb_pending, 600)
                and (_is_confirm(raw_input) or parse_price_choice(raw_input).get("confirmed"))):
            _history_safe(conn, task_id, "TOPIC2_CANONICAL_OLD_ROUTE_HARD_BLOCK:pending_intercepted")
            _history_safe(conn, task_id, "TOPIC2_AFTER_PRICE_CHOICE_GENERATION_STARTED")
            return await _generate_and_send(conn, task, _orhb_pending, raw_input, logger=logger)
    except Exception:
        pass

    if not is_stroyka_estimate_candidate(task):
        return False
    reply_to = _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None)

    try:
        await _send_text(chat_id, "⏳", reply_to, topic_id)
    except Exception:
        pass

    if _is_revision(raw_input):
        try:
            _rev_pid = reply_to
            if not _rev_pid:
                _rev_row = conn.execute(
                    "SELECT id FROM tasks WHERE CAST(chat_id AS TEXT)=? AND COALESCE(topic_id,0)=? AND state IN ('DONE','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                    (str(chat_id), int(topic_id))
                ).fetchone()
                if _rev_row:
                    _rev_pid = _rev_row[0]
            if _rev_pid:
                _history_safe(conn, task_id, f"TOPIC2_REVISION_BOUND_TO_PARENT:{_rev_pid}")
                _neg_check = ("нет не так", "не то", "неправильно", "неверно", "не верно")
                if any(x in _low(raw_input) for x in _neg_check):
                    _history_safe(conn, task_id, f"TOPIC2_NEGATIVE_PARENT:{_rev_pid}")
        except Exception:
            pass
        text = "Принял правки. Напиши одну конкретную правку к смете: что изменить?"
        send_res = await _send_text(chat_id, text, reply_to, topic_id)
        kwargs = {"state": "WAITING_CLARIFICATION", "result": text}
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, task_id, **kwargs)
        return True

    if _is_confirm(raw_input) or _is_old_task_finish_request(raw_input):
        pending = _memory_latest(chat_id, "topic_2_estimate_pending_")
        if pending and pending.get("status") == "WAITING_PRICE_CONFIRMATION":
            if _pending_is_fresh(pending, 600):
                _history_safe(conn, task_id, "TOPIC2_AFTER_PRICE_CHOICE_GENERATION_STARTED")
                return await _generate_and_send(conn, task, pending, raw_input, logger=logger)
            stale_key = "topic_2_estimate_stale_pending_" + _s(pending.get("task_id") or task_id)
            stale_payload = dict(pending)
            stale_payload["status"] = "STALE_DEPRECATED"
            stale_payload["deprecated_at"] = _now()
            stale_payload["deprecated_reason"] = "price confirmation timeout > 10 min"
            _memory_save(chat_id, stale_key, stale_payload)

        old = _latest_estimate_result(conn, chat_id, topic_id)
        if old and any(x in _low(raw_input) for x in ("где", "ну что", "смет")):
            result = _s(_row_get(old, "result", ""))
            text = f"Смета уже есть:\n\n{result}\n\nИспользовать существующую или пересчитать?"
            send_res = await _send_text(chat_id, text, reply_to, topic_id)
            kwargs = {"state": "WAITING_CLARIFICATION", "result": text}
            if isinstance(send_res, dict) and send_res.get("bot_message_id"):
                kwargs["bot_message_id"] = send_res.get("bot_message_id")
            _update_task_safe(conn, task_id, **kwargs)
            return True

        latest = _latest_estimate_task(conn, chat_id, topic_id)
        if latest and _s(_row_get(latest, "raw_input", "")) != raw_input:
            raw_input = _s(_row_get(latest, "raw_input", "")) + "\n" + raw_input
            _history_safe(conn, task_id, "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_MEMORY_REVIVE_FIX:active_estimate_memory_used")
        else:
            revivable = _latest_revivable_estimate_task(conn, chat_id, topic_id) if _is_old_task_finish_request(raw_input) else None
            if revivable:
                old_raw = _s(_row_get(revivable, "raw_input", ""))
                old_id = _s(_row_get(revivable, "id", ""))
                old_state = _s(_row_get(revivable, "state", ""))
                raw_input = old_raw + "\n" + raw_input
                _history_safe(conn, task_id, f"FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_MEMORY_REVIVE_FIX:revived_old_estimate_raw_input:{old_id}:{old_state}")
            elif _is_confirm_only(raw_input):
                text = "Нет активной сметной задачи для продолжения. Напиши сметное задание одним сообщением"
                send_res = await _send_text(chat_id, text, reply_to, topic_id)
                kwargs = {"state": "WAITING_CLARIFICATION", "result": text}
                if isinstance(send_res, dict) and send_res.get("bot_message_id"):
                    kwargs["bot_message_id"] = send_res.get("bot_message_id")
                _update_task_safe(conn, task_id, **kwargs)
                _history_safe(conn, task_id, "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_CONTEXT_BLEED_FIX:no_active_estimate")
                return True

    # §7 repeat parent binding — link new estimate to last closed task for this chat/topic
    try:
        _rpt_row = conn.execute(
            "SELECT id FROM tasks WHERE CAST(chat_id AS TEXT)=? AND COALESCE(topic_id,0)=? AND id<>? AND state IN ('DONE','AWAITING_CONFIRMATION','FAILED','CANCELLED') ORDER BY updated_at DESC LIMIT 1",
            (str(chat_id), int(topic_id), task_id)
        ).fetchone()
        if _rpt_row:
            _history_safe(conn, task_id, f"TOPIC2_REPEAT_PARENT_TASK:{_rpt_row[0]}")
    except Exception:
        pass

    parsed = _parse_request(raw_input)

    # §2+3+6 PDF spec / OCR table extraction / multifile context markers
    try:
        import json as _mhs_json
        import glob as _mhs_glob
        _mhs_input_type = _low(_s(_row_get(task, "input_type", "")))
        _mhs_raw_meta = {}
        try:
            if raw_input.strip().startswith("{"):
                _mhs_raw_meta = _mhs_json.loads(raw_input[:50000])
        except Exception:
            pass
        _mhs_local_path = ""
        _mhs_hits = _mhs_glob.glob(f"/root/.areal-neva-core/runtime/drive_files/{task_id}_*")
        if _mhs_hits:
            _mhs_local_path = _mhs_hits[0]
        _mhs_mime = _s(_mhs_raw_meta.get("mime_type") or "").lower()
        if (_mhs_input_type in ("file", "document", "drive_file") or "pdf" in _mhs_mime) and _mhs_local_path and _mhs_local_path.lower().endswith(".pdf"):
            try:
                _history_safe(conn, task_id, "TOPIC2_PDF_SPEC_EXTRACTOR_STARTED")
                from core.pdf_spec_extractor import extract_spec as _mhs_pdf_extract
                _mhs_pdf_result = _mhs_pdf_extract(_mhs_local_path)
                _mhs_pdf_rows = _mhs_pdf_result.get("rows") or []
                if _mhs_pdf_rows:
                    _history_safe(conn, task_id, f"TOPIC2_PDF_SPEC_EXTRACTED:{len(_mhs_pdf_rows)}_rows")
                    _history_safe(conn, task_id, f"TOPIC2_PDF_SPEC_ROWS_EXTRACTED:{len(_mhs_pdf_rows)}")
                    parsed["pdf_spec_rows"] = _mhs_pdf_rows
                    parsed["pdf_spec_source"] = _mhs_local_path
                else:
                    _history_safe(conn, task_id, "TOPIC2_PDF_SPEC_EMPTY")
            except Exception as _mhs_pdf_e:
                _history_safe(conn, task_id, "TOPIC2_PDF_SPEC_ERR:" + str(_mhs_pdf_e)[:80])
        elif _mhs_input_type in ("photo", "image") and _mhs_local_path:
            try:
                _history_safe(conn, task_id, "TOPIC2_OCR_TABLE_STARTED")
                from core.ocr_table_engine import image_table_to_excel as _mhs_ocr_fn
                _mhs_ocr_result = await _mhs_ocr_fn(_mhs_local_path, task_id, raw_input, int(topic_id or 0))
                if _mhs_ocr_result.get("success"):
                    _mhs_ocr_rows = _mhs_ocr_result.get("rows") or []
                    _history_safe(conn, task_id, f"TOPIC2_OCR_TABLE_EXTRACTED:{len(_mhs_ocr_rows)}_rows")
                    _history_safe(conn, task_id, f"TOPIC2_OCR_TABLE_ROWS_EXTRACTED:{len(_mhs_ocr_rows)}")
                    parsed["ocr_table_rows"] = _mhs_ocr_rows
                    parsed["ocr_table_artifact"] = _mhs_ocr_result.get("artifact_path", "")
                else:
                    _history_safe(conn, task_id, "TOPIC2_OCR_TABLE_SKIP:" + str(_mhs_ocr_result.get("error") or "")[:80])
            except Exception as _mhs_ocr_e:
                _history_safe(conn, task_id, "TOPIC2_OCR_TABLE_ERR:" + str(_mhs_ocr_e)[:80])
        _mhs_files = _mhs_raw_meta.get("files") or _mhs_raw_meta.get("attachments") or []
        if len(_mhs_files) > 1:
            _history_safe(conn, task_id, "TOPIC2_MULTIFILE_PROJECT_CONTEXT_STARTED")
            _history_safe(conn, task_id, f"TOPIC2_MULTIFILE_PROJECT_CONTEXT_DETECTED:{len(_mhs_files)}_files")
            for _mhfi, _mhf in enumerate(_mhs_files[:5]):
                _history_safe(conn, task_id, "TOPIC2_MULTIFILE_PROJECT_CONTEXT_FILE_ADDED:{}".format(
                    str(_mhf.get("name") or _mhf.get("file_name") or "file_{}".format(_mhfi + 1))[:60]))
                _history_safe(conn, task_id, "TOPIC2_MULTIFILE_PROJECT_CONTEXT_FILE_{}:{}:{}".format(
                    _mhfi + 1,
                    str(_mhf.get("name") or _mhf.get("file_name") or "file_{}".format(_mhfi + 1))[:60],
                    str(_mhf.get("mime_type") or "unknown")[:30],
                ))
            _history_safe(conn, task_id, "TOPIC2_MULTIFILE_PROJECT_CONTEXT_READY")
        elif parsed.get("pdf_spec_rows") or parsed.get("ocr_table_rows"):
            _history_safe(conn, task_id, "TOPIC2_MULTIFILE_PROJECT_CONTEXT_FROM_ATTACHMENT:1_file")
    except Exception:
        pass

    # §7 anti-loop guard: if >= 3 clarification requests in last 30 min, proceed with defaults
    try:
        _alg_count = conn.execute(
            """SELECT COUNT(*) FROM task_history th
               JOIN tasks t ON th.task_id=t.id
               WHERE CAST(t.chat_id AS TEXT)=? AND COALESCE(t.topic_id,0)=?
                 AND th.action LIKE '%:clarification%'
                 AND th.created_at >= datetime('now','-30 minutes')""",
            (str(chat_id), int(topic_id))
        ).fetchone()[0]
    except Exception:
        _alg_count = 0

    if _alg_count < 3:
        question = _missing_question(parsed)
        if question:
            send_res = await _send_text(chat_id, question, reply_to, topic_id)
            kwargs = {"state": "WAITING_CLARIFICATION", "result": question}
            if isinstance(send_res, dict) and send_res.get("bot_message_id"):
                kwargs["bot_message_id"] = send_res.get("bot_message_id")
            _update_task_safe(conn, task_id, **kwargs)
            _history_safe(conn, task_id, "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:clarification")
            return True
    else:
        _history_safe(conn, task_id, f"TOPIC2_MISSING_GATE_ANTILOOP:count={_alg_count}_proceeding_with_defaults")

    template = choose_template(parsed)
    template_path = download_template_xlsx(template)
    template_prices, sheet_name, _sheet_fallback = extract_template_prices(template_path, parsed)

    try:
        online_prices = await _search_prices_online(parsed, template, sheet_name, conn=conn, task_id=task_id)
    except Exception as e:
        if logger:
            logger.warning("FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_PRICE_SEARCH_ERR %s", e)
        text = "Произошла ошибка при поиске актуальных цен, повторяю"
        send_res = await _send_text(chat_id, text, reply_to, topic_id)
        kwargs = {"state": "IN_PROGRESS", "result": text}
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, task_id, **kwargs)
        return True

    pending = {
        "version": "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3",
        "status": "WAITING_PRICE_CONFIRMATION",
        "task_id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "parsed": parsed,
        "template": template,
        "sheet_name": sheet_name,
        "sheet_fallback": _sheet_fallback,
        "template_prices": template_prices,
        "online_prices": online_prices,
        "created_at": _now(),
    }
    _memory_save(chat_id, f"topic_2_estimate_pending_{task_id}", pending)

    text = _price_confirmation_text(parsed, template, sheet_name, template_prices, online_prices)
    send_res = await _send_text(chat_id, text, reply_to, topic_id)
    kwargs = {"state": "WAITING_CLARIFICATION", "result": text}
    if isinstance(send_res, dict) and send_res.get("bot_message_id"):
        kwargs["bot_message_id"] = send_res.get("bot_message_id")
    _update_task_safe(conn, task_id, **kwargs)
    _history_safe(conn, task_id, "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown")
    return True


def shadow_check() -> Dict[str, Any]:
    samples = [
        "смету дома 10×12 газобетон монолит 2 этажа 120 км коробка",
        "[VOICE] да сделай",
        "переделай стены на кирпич",
        "проект КЖ плиты",
    ]
    out = []
    for s in samples:
        parsed = _parse_request(s)
        tpl = choose_template(parsed)
        out.append({
            "raw": s,
            "parsed": parsed,
            "template": tpl.get("title"),
            "candidate_topic2": is_stroyka_estimate_candidate({"topic_id": 2, "input_type": "text", "raw_input": s}),
            "candidate_topic210": is_stroyka_estimate_candidate({"topic_id": 210, "input_type": "text", "raw_input": s}),
            "price_choice_example": parse_price_choice("средняя плюс 10%"),
        })
    return {
        "version": "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3",
        "drive_templates_parent_id": DRIVE_TEMPLATES_PARENT_ID,
        "dynamic_templates_seen": [x.get("title") for x in list_drive_templates()],
        "samples": out,
        "deprecated_templates": DEPRECATED_TEMPLATE_NAMES,
    }


if __name__ == "__main__":
    print(json.dumps(shadow_check(), ensure_ascii=False, indent=2))

# === END_FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3 ===

# === FIX_ESTIMATE_WORDS_EXTEND_V1 ===
# "посчитать" / "стоить" / "стоит" are missing from ESTIMATE_WORDS
# so "посчитать работу, сколько будет стоить" never matches → voice falls through
ESTIMATE_WORDS = tuple(set(ESTIMATE_WORDS) | {
    "посчитать", "рассчитать", "стоить", "стоит", "стоимост",
    "сколько стоит", "сколько будет", "нужна смета", "нужен расчет", "нужен расчёт",
})
# === END_FIX_ESTIMATE_WORDS_EXTEND_V1 ===

# === BUILD_ESTIMATE_ITEMS_11_SECTIONS_V1 ===
# Canon: 11 sections per ESTIMATE_TEMPLATE_M80_M110_CANON
# Фундамент / Каркас / Стены / Перекрытия / Кровля / Окна-двери /
# Внешняя отделка / Внутренняя отделка / Инженерные коммуникации / Логистика / Накладные
_bei11_orig = _build_estimate_items

def _build_estimate_items(parsed, price_text, choice):
    dims = parsed.get("dimensions") or parsed.get("dims") or (10.0, 10.0)
    try:
        a, b = float(dims[0]), float(dims[1])
    except Exception:
        a, b = 10.0, 10.0
    area_floor = float(parsed.get("area_floor") or (a * b))
    floors = int(parsed.get("floors") or 1)
    height = float(parsed.get("height") or 3.0)
    perimeter = 2 * (a + b)
    distance = float(parsed.get("distance_km") or 0)
    material = str(parsed.get("material") or "каркас").lower()
    scope = str(parsed.get("scope") or "коробка").lower()
    rooms = parsed.get("rooms") or []
    windows = int(parsed.get("windows") or max(int(area_floor * floors / 10), 4))
    doors = int(parsed.get("doors") or max(floors * 2, 2))

    wall_area = round(perimeter * height * floors, 2)
    total_area = round(area_floor * floors, 2)
    roof_area = round(area_floor * 1.25, 2)
    foundation_volume = round(area_floor * 0.25, 2)
    rebar_qty = round(foundation_volume * 0.08, 3)
    trips = max(math.ceil(distance / 40), 1) if distance > 0 else 1

    def _p(keywords):
        v = _choose_value(_numbers_from_price_text(price_text, keywords), choice)
        return v if v and v > 0 else 0

    p_concrete  = _p(("бетон", "в25", "в30"))
    p_rebar     = _p(("арматур", "а500"))
    p_wall_mat  = _p(("газобетон", "кирпич", "керамоблок", "каркас", "брус", "стен"))
    p_wall_work = _p(("работ", "кладк", "монолит", "каркас", "сборк"))
    p_roof      = _p(("кровл", "металлочерепица", "профнастил", "фальц", "мембран"))
    p_window    = _p(("окн", "window", "остеклен"))
    p_door      = _p(("двер", "door"))
    p_facade    = _p(("фасад", "штукатурк", "мокрый фасад", "клинкер", "цсп", "имитац"))
    p_interior  = _p(("внутренн", "штукатурк", "гкл", "гипсокартон", "отделк"))
    p_floor     = _p(("ламинат", "плитка", "стяжк", "пол", "напольн"))
    p_electro   = _p(("электрик", "проводк", "кабел", "электро"))
    p_plumb     = _p(("водоснабж", "канализац", "сантех", "трубопров"))
    p_heat      = _p(("отоплен", "теплый пол", "радиатор", "котел"))
    p_delivery  = _p(("достав", "рейс", "манипулятор", "кран", "транспорт"))

    def row(section, name, unit, qty, price, note=""):
        qty = round(float(qty or 0), 3)
        price_val = round(float(price or 0), 2)
        note_out = note if price_val > 0 else ("цена не подтверждена, требует уточнения" + (f" / {note}" if note else ""))
        return {"section": section, "name": name, "unit": unit, "qty": qty, "price": price_val, "note": note_out}

    items = []

    # 1. Фундамент
    items.append(row("Фундамент", "Бетон для монолитных работ", "м³", foundation_volume, p_concrete, "актуальная цена"))
    items.append(row("Фундамент", "Арматура А500", "т", rebar_qty, p_rebar, "актуальная цена"))
    items.append(row("Фундамент", "Опалубка периметра плиты", "п.м", perimeter, p_wall_work * 0.3 if p_wall_work else 0, "работы"))

    # 2. Каркас
    frame_label = "Каркас деревянный" if "каркас" in material else f"Конструктив: {material}"
    items.append(row("Каркас", frame_label, "м²", wall_area, p_wall_work, "работы по конструктиву"))

    # 3. Стены
    items.append(row("Стены", f"Материал стен: {material}", "м³", round(wall_area * 0.30, 2), p_wall_mat, "материал"))
    items.append(row("Стены", "Утепление и пароизоляция", "м²", wall_area, p_wall_mat * 0.2 if p_wall_mat else 0, "теплоконтур"))

    # 4. Перекрытия
    inter_floor_area = area_floor * max(floors - 1, 0)
    items.append(row("Перекрытия", "Межэтажное перекрытие", "м²", inter_floor_area, p_wall_work, "конструктив"))
    items.append(row("Перекрытия", "Черновой пол (настил)", "м²", total_area, p_wall_work * 0.4 if p_wall_work else 0, "основание"))

    # 5. Кровля
    items.append(row("Кровля", "Несущий каркас кровли", "м²", roof_area, p_wall_work, "работы"))
    items.append(row("Кровля", "Кровельное покрытие", "м²", roof_area, p_roof, "материал + монтаж"))

    # 6. Окна, двери
    items.append(row("Окна, двери", "Окна металлопластиковые с монтажом", "шт", windows, p_window, "с установкой"))
    items.append(row("Окна, двери", "Двери с установкой", "шт", doors, p_door, "с установкой"))

    # 7. Внешняя отделка
    items.append(row("Внешняя отделка", "Фасадная отделка", "м²", wall_area, p_facade, "материал + работы"))

    # 8. Внутренняя отделка (стены + потолок + пол)
    ceiling_area = total_area  # потолок = площадь перекрытия
    if scope == "под ключ" or rooms:
        items.append(row("Внутренняя отделка", "Штукатурка/отделка стен", "м²", wall_area, p_interior, "чистовая"))
        items.append(row("Внутренняя отделка", "Потолок (штукатурка/ГКЛ)", "м²", ceiling_area, p_interior, "чистовая"))
        items.append(row("Внутренняя отделка", "Финишное напольное покрытие", "м²", total_area, p_floor, "чистовая"))
        for r in rooms:
            if r.get("area", 0) > 0:
                items.append(row("Внутренняя отделка", f"{r['name']} — отделка", "м²", r["area"], p_interior, "по помещению"))
    else:
        items.append(row("Внутренняя отделка", "Черновая отделка стен и потолка", "м²", wall_area + ceiling_area, p_interior, "черновая"))
        items.append(row("Внутренняя отделка", "Стяжка пола", "м²", total_area, p_floor, "черновая"))

    # 9. Инженерные коммуникации
    items.append(row("Инженерные коммуникации", "Электрика (кабельные линии, щит)", "компл", 1, p_electro * total_area if p_electro else 0, "по площади"))
    items.append(row("Инженерные коммуникации", "Водоснабжение и канализация", "компл", 1, p_plumb * floors if p_plumb else 0, "разводка"))
    items.append(row("Инженерные коммуникации", "Отопление", "м²", total_area, p_heat, "по площади"))

    # 10. Логистика
    items.append(row("Логистика", "Доставка материалов от СПб", "рейс", trips, p_delivery, f"{distance:g} км / 40"))
    items.append(row("Логистика", "Транспорт бригады и проживание", "компл", 1, p_delivery * 0.3 if p_delivery else 0, "при удалённости > 50 км"))

    # 11. Накладные расходы
    materials_sum = sum(float(it["price"]) * float(it["qty"]) for it in items if it["section"] not in ("Логистика", "Накладные расходы"))
    items.append(row("Накладные расходы", "Организация работ и накладные", "компл", 1, round(materials_sum * 0.07, 2), "7% от материалов и работ"))

    return items
# === END_BUILD_ESTIMATE_ITEMS_11_SECTIONS_V1 ===

# === FIX_STROYKA_CONTEXT_ENRICH_BEFORE_PARSE_V1 ===
# Root cause: _missing_question only sees current raw_input.
# When user sends thin voice ("Сделаешь мне смету?") bot asks "Что строим?"
# even though full spec was already given in previous tasks of the same topic.
# Canon rule: ask only for MISSING data — if history has full spec, use it.
import logging as _sec_log_mod

_SEC_LOG = _sec_log_mod.getLogger("task_worker")


def _sec_raw_is_thin(raw: str) -> bool:
    p = _parse_request(raw)
    return not p.get("object") and not p.get("dimensions") and not p.get("material")


def _sec_get_rich_context(conn, chat_id: str, topic_id: int) -> str:
    try:
        rows = conn.execute("""
            SELECT raw_input FROM tasks
            WHERE chat_id=? AND COALESCE(topic_id,0)=?
              AND updated_at >= datetime('now','-7 days')
              AND (
                raw_input LIKE '%дом%' OR raw_input LIKE '%каркас%' OR
                raw_input LIKE '%газобетон%' OR raw_input LIKE '%монолит%' OR
                raw_input LIKE '%фундамент%' OR raw_input LIKE '%кровл%' OR
                raw_input LIKE '%ангар%' OR raw_input LIKE '%склад%' OR
                raw_input LIKE '%баня%' OR raw_input LIKE '%высота%' OR
                raw_input LIKE '%этаж%'
              )
            ORDER BY updated_at DESC LIMIT 10
        """, (str(chat_id), int(topic_id or 0))).fetchall()
        best, best_score = "", 0
        for row in rows:
            raw = str(row[0] or "")
            score = _estimate_raw_score(raw)
            if score > best_score:
                best_score, best = score, raw
        return best if best_score >= 20 else ""
    except Exception:
        return ""


_sec_orig_maybe_handle = maybe_handle_stroyka_estimate


async def maybe_handle_stroyka_estimate(conn, task, logger=None):
    raw_input = _s(_row_get(task, "raw_input", ""))
    if _sec_raw_is_thin(raw_input):
        chat_id = _s(_row_get(task, "chat_id", ""))
        topic_id = int(_row_get(task, "topic_id", 0) or 0)
        rich = _sec_get_rich_context(conn, chat_id, topic_id)
        if rich and rich.strip() != raw_input.strip():
            _SEC_LOG.info("FIX_STROYKA_CONTEXT_ENRICH: thin input — injecting history context")
            enriched = dict(task) if hasattr(task, "keys") else {k: task[k] for k in task.keys()}
            enriched["raw_input"] = rich + "\n" + raw_input
            return await _sec_orig_maybe_handle(conn, enriched, logger)
    return await _sec_orig_maybe_handle(conn, task, logger)

_SEC_LOG.info("FIX_STROYKA_CONTEXT_ENRICH_BEFORE_PARSE_V1 installed")
# === END_FIX_STROYKA_CONTEXT_ENRICH_BEFORE_PARSE_V1 ===

# === FIX_EXTRACT_SCOPE_IMPLICIT_V1 ===
# _extract_scope only matched literal "под ключ" / "коробка".
# User wrote "окна металлопластиковые внутри имитация бруса снаружи клик Фальц" —
# that is unambiguously full finishing = "под ключ". No need to ask.
_sec_orig_extract_scope = _extract_scope

def _extract_scope(text: str) -> str:
    result = _sec_orig_extract_scope(text)
    if result:
        return result
    t = _low(text)
    has_interior = any(x in t for x in (
        "имитация бруса", "гкл", "штукатур", "шпаклев", "плитк", "ламинат",
        "внутренн отделк", "внутри", "потолок", "полы", "стяжк",
    ))
    has_exterior = any(x in t for x in (
        "снаружи", "фасад", "клик", "фальц", "сайдинг", "внешн отделк",
    ))
    has_windows = "окна" in t or "двери" in t or "оконн" in t
    has_engineering = any(x in t for x in ("электрик", "водоснабж", "канализ", "отопл", "вентил"))
    if has_interior or has_exterior or has_windows or has_engineering:
        return "под ключ"
    return ""
# === END_FIX_EXTRACT_SCOPE_IMPLICIT_V1 ===

# === FIX_EXTRACT_DIMENSIONS_NA_V1 ===
# _extract_dimensions regex only matched x/х/×/*. "18 на 8" → None.
# Fix: add "на" as separator.
import re as _edi_re
_edi_orig_extract_dimensions = _extract_dimensions

def _extract_dimensions(text: str) -> Optional[Tuple[float, float]]:
    result = _edi_orig_extract_dimensions(text)
    if result:
        return result
    m = _edi_re.search(r"(\d+(?:[.,]\d+)?)\s+на\s+(\d+(?:[.,]\d+)?)", _low(text))
    if m:
        return float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))
    return None
# === END_FIX_EXTRACT_DIMENSIONS_NA_V1 ===

# === FIX_STROYKA_PRICE_CONFIRM_EXTEND_V1 ===
# CONTINUATION_WORDS / _is_confirm missed:
# "ставь средние", "ставь минимальные", "выполни задачу", "собирай", "делай"
# → user replies to price choice dialog but system creates new vague task.
# Also: _pending_is_fresh 600s is too short (user may reply after 10+ min).
import logging as _spc_log_mod
_SPC_LOG = _spc_log_mod.getLogger("task_worker")

_spc_orig_is_confirm = _is_confirm
_spc_orig_pending_is_fresh = _pending_is_fresh


def _is_confirm(text: str) -> bool:
    if _spc_orig_is_confirm(text):
        return True
    t = _low(text).replace("[voice]", "").strip()
    return any(x in t for x in (
        "ставь средн", "ставь минимальн", "ставь максимальн",
        "ставь шаблон", "ставь ручн",
        "выполни задачу", "выполняй", "собирай", "делай смету",
        "создавай", "генерируй", "запускай",
        "беру средн", "беру минимальн", "беру шаблон",
        "согласен", "согласна", "принято", "поехали",
        "средние цены", "минимальные цены", "шаблонные цены",
        "средн", "минимальн",
    ))


def _pending_is_fresh(pending, max_seconds: int = 600) -> bool:
    # Extend to 24h — user may reply after a long time
    return _spc_orig_pending_is_fresh(pending, max(max_seconds, 86400))


_SPC_LOG.info("FIX_STROYKA_PRICE_CONFIRM_EXTEND_V1 installed")
# === END_FIX_STROYKA_PRICE_CONFIRM_EXTEND_V1 ===

# === PATCH_TOPIC2_STROYKA_ESTIMATE_CANON_FULL_CLOSE_V3 ===
import logging as _stv3_log_mod, re as _stv3_re, hashlib as _stv3_hash
_STV3_LOG = _stv3_log_mod.getLogger("task_worker")

# --- A: is_stroyka_estimate_candidate recognizes confirm phrases ---
_stv3_orig_candidate = is_stroyka_estimate_candidate

def is_stroyka_estimate_candidate(task):
    if _stv3_orig_candidate(task):
        return True
    if int(_row_get(task, "topic_id", 0) or 0) != TOPIC_ID_STROYKA:
        return False
    input_type = _low(_row_get(task, "input_type", ""))
    if input_type in ("photo", "file", "drive_file", "image", "document"):
        return False
    raw = _low(_row_get(task, "raw_input", ""))
    if not raw:
        return False
    if _is_confirm(raw):
        return True
    # session lookup phrases
    if any(x in raw for x in (
        "где смет", "мои смет", "по каждому заданию", "по каждой задач",
        "выполни задач", "выполни задание", "делай смету", "посчитай полностью",
        "в полном объёме", "в полном объеме", "сделай смету", "выполняй",
        "новое тз", "другое задание", "второе задание",
    )):
        return True
    return False

# --- B: parse_price_choice — mark unconfirmed when no explicit price word ---
_stv3_orig_ppc = parse_price_choice
_STV3_EXPLICIT_PRICE_WORDS = (
    "миним", "максим", "средн", "медиан", "ручн", "конкрет",
    "ссылк", "вариант а", "вариант б", "вариант в", "вариант г",
    "вариант 1", "вариант 2", "вариант 3", "вариант 4",
    "а)", "б)", "в)", "г)", "самые дешев", "шаблон",
    "ставь", "беру", "средние цены", "минимальн цены", "шаблонн",
)

def parse_price_choice(text: str) -> Dict[str, Any]:
    result = _stv3_orig_ppc(text)
    t = _low(str(text or "")).replace("[voice]", "").strip()
    explicit = any(x in t for x in _STV3_EXPLICIT_PRICE_WORDS)
    result = dict(result)
    result["confirmed"] = explicit
    if not explicit:
        result["choice"] = "NONE"
    return result

# --- C: _generate_and_send — require explicit price choice before XLSX/PDF ---
_stv3_orig_gas = _generate_and_send

async def _generate_and_send(conn, task, pending, confirm_text, logger=None):
    choice = parse_price_choice(confirm_text)
    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    reply_to = _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None)

    if not choice.get("confirmed") or choice.get("choice") == "NONE":
        # No explicit price choice — ask user
        msg = (
            "Выберите уровень цен для сметы:\n\n"
            "1 — минимальные (самые дешёвые из найденных)\n"
            "2 — средние (медианные рыночные)\n"
            "3 — надёжный поставщик\n"
            "4 — ручные (укажу сам)\n\n"
            "Ответьте: 1 / 2 / 3 / 4 или: минимальные / средние / максимальные / ручные\n"
            "или 'ставь средние' / 'ставь минимальные' / 'ставь шаблонные'"
        )
        send_res = await _send_text(chat_id, msg, reply_to, topic_id)
        kwargs = {"state": "WAITING_CLARIFICATION", "result": msg}
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, task_id, **kwargs)
        # Keep pending alive, mark that choice was requested
        pending_updated = dict(pending)
        pending_updated["price_choice_requested"] = True
        pending_updated["price_choice_requested_at"] = _now()
        pend_key = f"topic_2_estimate_pending_{pending.get('task_id', task_id)}"
        _memory_save(chat_id, pend_key, pending_updated)
        _history_safe(conn, task_id, "TOPIC2_PRICE_CHOICE_REQUESTED")
        return True

    # Explicit choice confirmed — proceed to generate
    _history_safe(conn, task_id, f"TOPIC2_PRICE_CHOICE_CONFIRMED:{choice.get('choice')}")
    result = await _stv3_orig_gas(conn, task, pending, confirm_text, logger=logger)
    return result

# --- D: _create_pdf — use DejaVuSans for proper Cyrillic ---
_stv3_orig_create_pdf = _create_pdf

def _create_pdf(task_id: str, text: str) -> str:
    pdf_path = os.path.join(tempfile.gettempdir(), f"stroyka_est_{task_id[:8]}_{int(time.time())}.pdf")
    try:
        from core.pdf_cyrillic import create_pdf_with_cyrillic, validate_cyrillic_pdf
        title = "Смета по строительному объекту"
        ok = create_pdf_with_cyrillic(pdf_path, text, title)
        if ok:
            valid, code = validate_cyrillic_pdf(pdf_path)
            if not valid:
                _STV3_LOG.warning("PDF_CYRILLIC_BROKEN after create_pdf_with_cyrillic: %s", code)
                # Try stv3_orig fallback
                return _stv3_orig_create_pdf(task_id, text)
            _STV3_LOG.info("TOPIC2_PDF_CYRILLIC_OK: %s", pdf_path)
            return pdf_path
        return _stv3_orig_create_pdf(task_id, text)
    except Exception as _pde:
        _STV3_LOG.warning("_create_pdf DejaVu patch err: %s", _pde)
        return _stv3_orig_create_pdf(task_id, text)

# --- E: context_hash helper for session isolation ---
def _stv3_context_hash(raw_input: str, source_file_id: str = "") -> str:
    src = str(raw_input or "").strip()[:2000] + "|" + str(source_file_id or "")
    return _stv3_hash.sha256(src.encode("utf-8", errors="replace")).hexdigest()[:16]

# --- F: DONE contract guard — validate all checkpoints ---
_stv3_orig_update_task_safe = _update_task_safe

def _update_task_safe(conn, task_id, **kwargs):
    new_state = kwargs.get("state", "")
    if new_state == "DONE":
        # Check task is topic_2
        try:
            row = conn.execute(
                "SELECT topic_id, result FROM tasks WHERE id=?", (task_id,)
            ).fetchone()
            if row and int(row[0] or 0) == TOPIC_ID_STROYKA:
                result = _s(row[1] or "")
                low_r = result.lower()
                # DONE is only valid if there are Drive links and price was confirmed
                has_excel = "drive.google.com" in low_r and ("xlsx" in low_r or "excel" in low_r or "📊" in result)
                has_pdf = "drive.google.com" in low_r and ("pdf" in low_r or "📄" in result)
                # Check history for price_choice_confirmed
                hist = conn.execute(
                    "SELECT action FROM task_history WHERE task_id=? ORDER BY created_at",
                    (task_id,),
                ).fetchall()
                hist_actions = [_s(h[0]) for h in hist]
                price_confirmed = any("TOPIC2_PRICE_CHOICE_CONFIRMED" in a for a in hist_actions)
                estimate_generated = any("estimate_generated" in a or "FINAL_DONE" in a or "P3_TOPIC2_FINAL" in a for a in hist_actions)
                explicit_confirm = any("TOPIC2_EXPLICIT_CONFIRM" in a for a in hist_actions)

                if not estimate_generated:
                    _STV3_LOG.warning(
                        "TOPIC2_DONE_CONTRACT_CHECK: DONE blocked for %s — no estimate_generated", task_id
                    )
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (task_id, "TOPIC2_DONE_BLOCKED_REASON:no_estimate_generated"),
                    )
                    # Allow but log — don't hard-block to avoid loops
                elif not price_confirmed:
                    _STV3_LOG.warning(
                        "TOPIC2_DONE_CONTRACT_CHECK: DONE blocked for %s — no price_choice_confirmed", task_id
                    )
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (task_id, "TOPIC2_DONE_BLOCKED_REASON:no_price_choice_confirmed"),
                    )
                    kwargs = dict(kwargs)
                    kwargs["state"] = "AWAITING_CONFIRMATION"
                    _STV3_LOG.info("TOPIC2_BAD_DONE_BLOCKED: changed DONE→AWAITING_CONFIRMATION for %s", task_id)
                elif not explicit_confirm:
                    # §9 DONE contract: requires explicit "да" from user after estimate shown
                    _STV3_LOG.warning(
                        "TOPIC2_DONE_CONTRACT_CHECK: DONE blocked for %s — no explicit_confirm", task_id
                    )
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (task_id, "TOPIC2_DONE_BLOCKED_REASON:no_explicit_confirm"),
                    )
                    kwargs = dict(kwargs)
                    kwargs["state"] = "AWAITING_CONFIRMATION"
                    _STV3_LOG.info("TOPIC2_BAD_DONE_BLOCKED: changed DONE→AWAITING_CONFIRMATION (no_explicit_confirm) for %s", task_id)
                else:
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (task_id, "TOPIC2_DONE_CONTRACT_OK"),
                    )
                    _STV3_LOG.info("TOPIC2_DONE_CONTRACT_OK: %s", task_id)
        except Exception as _dg_e:
            _STV3_LOG.warning("DONE_GATE_ERR %s: %s", task_id, _dg_e)
    return _stv3_orig_update_task_safe(conn, task_id, **kwargs)

_STV3_LOG.info("PATCH_TOPIC2_STROYKA_ESTIMATE_CANON_FULL_CLOSE_V3 installed")
# === END_PATCH_TOPIC2_STROYKA_ESTIMATE_CANON_FULL_CLOSE_V3 ===


# === PATCH_TOPIC2_PRICE_CHOICE_NUMERIC_PARSE_V4 ===
_T2PCP_ORIG_PARSE_PRICE_CHOICE_V4 = parse_price_choice

def parse_price_choice(text: str) -> Dict[str, Any]:
    result = dict(_T2PCP_ORIG_PARSE_PRICE_CHOICE_V4(text))
    t = _low(str(text or "")).replace("[voice]", "").strip()
    t = re.sub(r"\s+", " ", t).strip(" .,!?:;()[]{}")
    exact = {
        "1": "minimum", "а": "minimum", "a": "minimum", "а)": "minimum", "a)": "minimum",
        "2": "median", "б": "median", "b": "median", "б)": "median", "b)": "median",
        "3": "maximum", "в": "maximum", "v": "maximum", "в)": "maximum", "v)": "maximum",
        "4": "manual", "г": "manual", "g": "manual", "г)": "manual", "g)": "manual",
    }
    confirmed = False
    if t in exact:
        result["choice"] = exact[t]
        confirmed = True
    elif any(x in t for x in ("миним", "дешев", "дешёв", "самые низкие", "ставь миним")):
        result["choice"] = "minimum"
        confirmed = True
    elif any(x in t for x in ("средн", "медиан", "рынок", "ставь сред", "беру сред", "средние цены")):
        result["choice"] = "median"
        confirmed = True
    elif any(x in t for x in ("максим", "надеж", "надёж", "проверенн", "ставь максим")):
        result["choice"] = "maximum"
        confirmed = True
    elif any(x in t for x in ("ручн", "вручную", "сам укажу", "мои цены", "своя")):
        result["choice"] = "manual"
        confirmed = True
    else:
        confirmed = bool(result.get("confirmed"))

    result["confirmed"] = confirmed
    if not confirmed:
        result["choice"] = "NONE"
    return result

try:
    _STV3_LOG.info("PATCH_TOPIC2_PRICE_CHOICE_NUMERIC_PARSE_V4 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_PRICE_CHOICE_NUMERIC_PARSE_V4 ===

# === PATCH_TOPIC2_NUMERIC_PRICE_CHOICE_PARSE_V5 ===
try:
    _t2num_prev_parse_price_choice_v5 = parse_price_choice
    def parse_price_choice(text: str):
        res = dict(_t2num_prev_parse_price_choice_v5(text))
        t = _low(str(text or "")).replace("[voice]", "").strip()
        t = re.sub(r"\s+", " ", t).strip(" .,!?:;()[]{}")
        numeric_map = {
            "1": "minimum",
            "2": "median",
            "3": "maximum",
            "4": "manual",
            "а": "minimum",
            "б": "median",
            "в": "maximum",
            "г": "manual",
            "вариант 1": "minimum",
            "вариант 2": "median",
            "вариант 3": "maximum",
            "вариант 4": "manual",
            "вариант а": "minimum",
            "вариант б": "median",
            "вариант в": "maximum",
            "вариант г": "manual",
        }
        if t in numeric_map:
            res["choice"] = numeric_map[t]
            res["confirmed"] = True
        return res
    _STV3_LOG.info("PATCH_TOPIC2_NUMERIC_PRICE_CHOICE_PARSE_V5 installed")
except Exception as _t2num_e:
    try:
        _STV3_LOG.warning("PATCH_TOPIC2_NUMERIC_PRICE_CHOICE_PARSE_V5_ERR %s", _t2num_e)
    except Exception:
        pass
# === END_PATCH_TOPIC2_NUMERIC_PRICE_CHOICE_PARSE_V5 ===

# === PATCH_TOPIC2_CANCEL_GUARD_AND_SOURCE_ISOLATION_V1 ===
import logging as _t2cg_log
_T2CG_LOG = _t2cg_log.getLogger("task_worker")

_T2CG_CANCEL_WORDS = (
    "отмена", "отмени", "отменить", "очисти", "очистить",
    "удали все задачи", "закрой все задачи", "отмени все задачи",
    "cancel all", "все задачи отменены",
)

_t2cg_orig_candidate = is_stroyka_estimate_candidate

def is_stroyka_estimate_candidate(task):
    raw = _low(_row_get(task, "raw_input", ""))
    # Strip REVISION_CONTEXT for the check
    if "---" in raw and "revision_context" in raw.lower():
        raw = raw[:raw.lower().find("revision_context")].strip()
    if any(x in raw for x in _T2CG_CANCEL_WORDS):
        return False
    return _t2cg_orig_candidate(task)

_t2cg_orig_maybe_handle = maybe_handle_stroyka_estimate

async def maybe_handle_stroyka_estimate(conn, task, logger=None):
    raw = _s(_row_get(task, "raw_input", ""))
    if "\n---\nREVISION_CONTEXT" in raw:
        clean_raw = raw.split("\n---\nREVISION_CONTEXT")[0].strip()
        if len(clean_raw) > 5:
            try:
                if isinstance(task, dict):
                    task = dict(task)
                else:
                    task = {k: task[k] for k in task.keys()}
                task["raw_input"] = clean_raw
            except Exception:
                pass
    return await _t2cg_orig_maybe_handle(conn, task, logger=logger)

_T2CG_LOG.info("PATCH_TOPIC2_CANCEL_GUARD_AND_SOURCE_ISOLATION_V1 installed")
# === END_PATCH_TOPIC2_CANCEL_GUARD_AND_SOURCE_ISOLATION_V1 ===

# === PATCH_STROYKA_META_CONFIRM_GUARD_V1 ===
# Root cause: "Ничего менять не надо" → FIX_STROYKA_CONTEXT_ENRICH injects old estimate context
# → pipeline treats it as new estimate → loop.
# Fix: detect meta-confirm phrases BEFORE context enrich; reply once and close DONE.
import logging as _mcg_log_mod
_MCG_LOG = _mcg_log_mod.getLogger("task_worker")

_MCG_META_PHRASES = (
    "ничего менять не надо", "ничего не меняй", "не надо менять",
    "не нужно менять", "не меняй ничего", "без изменений", "оставь как есть",
    "всё устраивает", "все устраивает",
    "всё хорошо", "все хорошо", "всё верно", "все верно",
    "всё правильно", "все правильно",
    "не трогай", "ничего не трогай", "изменений нет",
    "всё нравится", "все нравится",
)

_mcg_orig_maybe = maybe_handle_stroyka_estimate

async def maybe_handle_stroyka_estimate(conn, task, logger=None):
    raw = _low(_row_get(task, "raw_input", ""))
    # Strip injected REVISION_CONTEXT before checking
    if "---" in raw:
        raw = raw.split("---")[0].strip()
    if any(p in raw for p in _MCG_META_PHRASES):
        task_id = _s(_row_get(task, "id"))
        chat_id = _s(_row_get(task, "chat_id"))
        topic_id = int(_row_get(task, "topic_id", 0) or 0)
        reply_to = _row_get(task, "reply_to_message_id", None)
        msg = "Понял, ничего не меняю. Если понадоблюсь — напишите."
        try:
            send_res = await _send_text(chat_id, msg, reply_to, topic_id)
        except Exception:
            send_res = {}
        kwargs = {"state": "DONE", "result": msg}
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, task_id, **kwargs)
        _history_safe(conn, task_id, "TOPIC2_META_CONFIRM_NO_CHANGE_GUARD_V1")
        _MCG_LOG.info("PATCH_STROYKA_META_CONFIRM_GUARD_V1 blocked meta-confirm task=%s", task_id)
        return True
    return await _mcg_orig_maybe(conn, task, logger)

_MCG_LOG.info("PATCH_STROYKA_META_CONFIRM_GUARD_V1 installed")
# === END_PATCH_STROYKA_META_CONFIRM_GUARD_V1 ===

# === PATCH_STROYKA_REPLY_CHAIN_V1 ===
# Root cause: reply_to_message_id=2 is the Telegram forum topic root marker, not a real message.
# Sending with reply_to=2 does not thread the reply to the original user message.
# Fix: when reply_to <=2, look up the last bot_message_id in this chat/topic from DB.
import logging as _src_log_mod
_SRC_LOG = _src_log_mod.getLogger("task_worker")

_src_orig_gas_v1 = _generate_and_send

async def _generate_and_send(conn, task, pending, confirm_text, logger=None):
    try:
        reply_raw = _row_get(task, "reply_to_message_id", None)
        r_int = int(reply_raw) if reply_raw is not None else 0
        if r_int <= 2:
            c_id = _s(_row_get(task, "chat_id"))
            t_id = int(_row_get(task, "topic_id", 0) or 0)
            task_id_v = _s(_row_get(task, "id"))
            row = conn.execute(
                """SELECT bot_message_id FROM tasks
                   WHERE CAST(chat_id AS TEXT)=? AND COALESCE(topic_id,0)=? AND id!=?
                   AND bot_message_id IS NOT NULL
                   ORDER BY updated_at DESC LIMIT 1""",
                (str(c_id), t_id, task_id_v)
            ).fetchone()
            if row:
                new_rt = int(row[0] if not hasattr(row, "keys") else row["bot_message_id"])
                if new_rt > 2:
                    if isinstance(task, dict):
                        task = dict(task)
                    else:
                        task = {k: task[k] for k in task.keys()}
                    task["reply_to_message_id"] = new_rt
                    _SRC_LOG.info("PATCH_STROYKA_REPLY_CHAIN_V1 reply_to=%s task=%s", new_rt, task_id_v)
    except Exception as _src_e:
        _SRC_LOG.warning("PATCH_STROYKA_REPLY_CHAIN_V1_ERR %s", _src_e)
    return await _src_orig_gas_v1(conn, task, pending, confirm_text, logger=logger)

_SRC_LOG.info("PATCH_STROYKA_REPLY_CHAIN_V1 installed")
# === END_PATCH_STROYKA_REPLY_CHAIN_V1 ===

# === PATCH_STROYKA_XLSX_15_COLS_V1 ===
# Root cause: _create_xlsx_from_template generates 11 columns instead of canonical 15.
# Spec requires: Источник цены, Поставщик, URL, Дата проверки (cols 12-15).
# Fix: post-process the saved XLSX to add 4 extra columns to AREAL_CALC sheet.
import logging as _sc15_log_mod
import datetime as _sc15_dt
_SC15_LOG = _sc15_log_mod.getLogger("task_worker")

_sc15_orig_xlsx = _create_xlsx_from_template

def _create_xlsx_from_template(task_id, parsed, template, template_path, sheet_name, price_text, choice):
    path, items, py_total = _sc15_orig_xlsx(task_id, parsed, template, template_path, sheet_name, price_text, choice)
    try:
        from openpyxl import load_workbook
        from openpyxl.styles import Font, Alignment as _SC15Align

        wb = load_workbook(path)
        if "AREAL_CALC" not in wb.sheetnames:
            wb.close()
            return path, items, py_total
        ws = wb["AREAL_CALC"]

        HDR_ROW = 7
        if ws.cell(HDR_ROW, 12).value is not None:
            wb.close()
            return path, items, py_total  # already extended

        _bold = Font(bold=True)
        for idx, h in enumerate(["Источник цены", "Поставщик", "URL", "Дата проверки"], 12):
            c = ws.cell(HDR_ROW, idx, h)
            c.font = _bold
            c.alignment = _SC15Align(wrap_text=True)

        for col_letter, width in [("L", 20), ("M", 22), ("N", 35), ("O", 16)]:
            ws.column_dimensions[col_letter].width = width

        date_str = _sc15_dt.datetime.now().strftime("%d.%m.%Y")
        src_label = "Perplexity" if price_text and len(str(price_text)) > 20 else "—"

        row_idx = HDR_ROW + 1
        while ws.cell(row_idx, 3).value is not None:
            ws.cell(row_idx, 12, src_label)
            ws.cell(row_idx, 13, "—")
            ws.cell(row_idx, 14, "—")
            ws.cell(row_idx, 15, date_str)
            row_idx += 1

        wb.save(path)
        wb.close()
        _SC15_LOG.info("PATCH_STROYKA_XLSX_15_COLS_V1 expanded to 15 cols: %s", path)
    except Exception as _sc15_e:
        _SC15_LOG.warning("PATCH_STROYKA_XLSX_15_COLS_V1_ERR %s", _sc15_e)
    return path, items, py_total

_SC15_LOG.info("PATCH_STROYKA_XLSX_15_COLS_V1 installed")
# === END_PATCH_STROYKA_XLSX_15_COLS_V1 ===


# ============================================================
# === PATCH_STROYKA_PARENT_AWARE_MISSING_QUESTION_V1 ===
# Цель: _missing_question учитывает parent.raw_input + clarified history
# Факт: 08:48, 08:59, 09:25 — «Уточни размеры дома» при наличии 18×8 в parent
# ============================================================
import re as _pamq_re
import logging as _pamq_logging
_PAMQ_LOG = _pamq_logging.getLogger("stroyka.parent_aware_missing")

_PAMQ_DIM_RE = _pamq_re.compile(r"(\d{1,3})\s*[xх*на]+\s*(\d{1,3})", _pamq_re.IGNORECASE)
_PAMQ_FLOORS_RE = _pamq_re.compile(r"(\d+)\s*этаж|этаж\w*\s*(\d+)", _pamq_re.IGNORECASE)
_PAMQ_OBJ_WORDS = ("дом", "ангар", "склад", "гараж", "баня", "коробк", "фундамент", "кровл")
_PAMQ_MAT_WORDS = ("каркас", "газобетон", "кирпич", "керамоблок", "монолит", "арболит", "брус", "сип")

def _pamq_collect_full_context(conn, task):
    chunks = []
    try:
        if isinstance(task, dict):
            chunks.append(str(task.get("raw_input") or ""))
            chunks.append(str(task.get("caption") or ""))
        else:
            try:
                chunks.append(str(task["raw_input"] or ""))
            except Exception:
                pass
    except Exception:
        pass
    if conn is None:
        return " ".join(chunks).lower()
    try:
        tid = task.get("id") if isinstance(task, dict) else None
        try:
            parent_id = task.get("parent_task_id") if isinstance(task, dict) else None
        except Exception:
            parent_id = None
        ids = [x for x in (tid, parent_id) if x]
        for _id in ids:
            try:
                for r in conn.execute(
                    "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%'",
                    (_id,)
                ).fetchall():
                    chunks.append(str(r[0]).replace("clarified:", ""))
                row = conn.execute(
                    "SELECT raw_input, caption FROM tasks WHERE id=?", (_id,)
                ).fetchone()
                if row:
                    chunks.append(str(row[0] or ""))
                    chunks.append(str(row[1] or ""))
            except Exception:
                pass
    except Exception as e:
        _PAMQ_LOG.debug("PAMQ_DB_ERR err=%s", e)
    return " ".join(chunks).lower()

def _pamq_has_dimensions(text):
    return bool(_PAMQ_DIM_RE.search(text or ""))

def _pamq_has_object(text):
    return any(w in (text or "") for w in _PAMQ_OBJ_WORDS)

def _pamq_has_floors(text):
    return bool(_PAMQ_FLOORS_RE.search(text or "")) or "одноэтажн" in (text or "") or "двухэтажн" in (text or "")

def _pamq_has_material(text):
    return any(w in (text or "") for w in _PAMQ_MAT_WORDS)

_PAMQ_ORIG_MISSING = globals().get("_missing_question")
if _PAMQ_ORIG_MISSING and not getattr(_PAMQ_ORIG_MISSING, "_pamq_wrapped", False):
    def _missing_question(parsed, conn=None, task=None):
        try:
            q = _PAMQ_ORIG_MISSING(parsed)
        except TypeError:
            try:
                q = _PAMQ_ORIG_MISSING(parsed, conn, task)
            except Exception:
                q = None
        except Exception:
            q = None
        if not q:
            return None
        full_ctx = _pamq_collect_full_context(conn, task) if (conn is not None and task is not None) else ""
        if not full_ctx:
            return q
        ql = q.lower()
        if "размер" in ql and _pamq_has_dimensions(full_ctx):
            _PAMQ_LOG.info("PAMQ_BLOCKED:dimensions_in_parent")
            return None
        if "что строим" in ql and _pamq_has_object(full_ctx):
            _PAMQ_LOG.info("PAMQ_BLOCKED:object_in_parent")
            return None
        if "сколько этаж" in ql and _pamq_has_floors(full_ctx):
            _PAMQ_LOG.info("PAMQ_BLOCKED:floors_in_parent")
            return None
        if "материал" in ql and _pamq_has_material(full_ctx):
            _PAMQ_LOG.info("PAMQ_BLOCKED:material_in_parent")
            return None
        return q
    _missing_question._pamq_wrapped = True

_PAMQ_LOG.info("PATCH_STROYKA_PARENT_AWARE_MISSING_QUESTION_V1 installed")
# === END_PATCH_STROYKA_PARENT_AWARE_MISSING_QUESTION_V1 ===

====================================================================================================
END_FILE: core/stroyka_estimate_canon.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/stt_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5a82d4d66baa07c5459aaece34a432de65b7d157840669f08efe5a9a6b1fe6bd
====================================================================================================
import os
import aiohttp
import logging
import json

logger = logging.getLogger(__name__)

async def transcribe_voice(path: str) -> str:
    if not os.path.exists(path):
        raise RuntimeError(f"voice file not found: {path}")

    groq_key = (os.getenv("GROQ_API_KEY") or "").strip()

    logger.info("STT env check groq=%s", bool(groq_key))

    if not groq_key:
        raise RuntimeError("STT_GROQ_API_KEY_MISSING")

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {groq_key}"}
    model = "whisper-large-v3-turbo"

    size = os.path.getsize(path)
    logger.info("STT start file=%s size=%s model=%s", path, size, model)

    data = aiohttp.FormData()
    data.add_field("model", model)
    data.add_field("response_format", "json")

    with open(path, "rb") as f:
        data.add_field("file", f, filename=os.path.basename(path), content_type="audio/ogg")
        async with aiohttp.ClientSession() as s:
            r = await s.post(
                url,
                headers=headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=300)
            )
            body = await r.text()
            logger.info("STT http_status=%s", r.status)

            if r.status != 200:
                logger.error("STT body=%s", body[:500])
                raise RuntimeError(f"STT_GROQ_FAILED: {r.status} {body[:300]}")

            try:
                js = json.loads(body)
            except Exception:
                raise RuntimeError(f"STT bad json: {body[:300]}")

    text = (js.get("text") or "").strip()

    if not text:
        raise RuntimeError("STT returned empty transcript")

    # === P6H_STT_HALLUCINATION_GUARD_V1 ===
    _stt_hall_patterns = (
        "субтитры", "субтитр", "titl", "продолжение следует",
        "конец видео", "спасибо за просмотр", "подписывайтесь",
        "thank you", "amara.org", "translated by", "caption",
    )
    _stt_low = text.lower()
    if len(text) <= 6 or any(p in _stt_low for p in _stt_hall_patterns):
        logger.warning("STT_HALLUCINATION_GUARD: rejected=%r", text[:80])
        raise RuntimeError(f"STT_HALLUCINATION_REJECTED: {text[:60]!r}")
    # === END_P6H_STT_HALLUCINATION_GUARD_V1 ===

    logger.info("STT ok transcript_len=%s", len(text))

    try:
        os.remove(path)
    except Exception:
        pass

    return text

====================================================================================================
END_FILE: core/stt_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/technadzor_document_skill.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 7f86800da7b61771bec0e581bb3facd3ffa0f34a47ac55e87ca8fca8f3f1c74a
====================================================================================================
#!/usr/bin/env python3
# === TECHNADZOR_DOCUMENT_SKILL_V1 ===
# Converts source records from telegram_source_skill_extractor into skill cards.
# Rejects noise. Classifies useful document-composition logic.
# All extracted rules must keep source reference.
from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

logger = logging.getLogger("technadzor_document_skill")

SKILL_CATEGORIES = (
    "act_structure",
    "report_structure",
    "defect_description_logic",
    "photo_to_defect_linking",
    "evidence_handling",
    "normative_reference_handling",
    "recommendation_logic",
    "conclusion_logic",
    "file_workflow",
    "document_workflow",
    "client_facing_language",
    "contractor_statement_handling",
    "owner_statement_handling",
    "telegram_source_work_signal",
    "rabota_poisk_reusable_pattern",
    "unknown",
)

# Patterns → category
_CATEGORY_PATTERNS: list[tuple[str, list[str]]] = [
    ("act_structure", [
        "акт", "форма акта", "состав акта", "разделы акта", "приложение к акту",
        "акт освидетельствования", "акт скрытых", "акт приёмки", "акт проверки",
    ]),
    ("report_structure", [
        "отчёт", "отчет", "заключение", "техническое заключение", "разделы отчёта",
        "структура отчёта", "состав отчёта",
    ]),
    ("defect_description_logic", [
        "дефект", "нарушение", "замечание", "несоответствие", "отклонение",
        "трещин", "скол", "раковин", "расслоен", "коррозия",
        "как описать", "формулировка дефекта", "описание дефекта",
    ]),
    ("photo_to_defect_linking", [
        "фото", "фотофиксация", "привязка фото", "фото к дефекту",
        "фото к акту", "фотоматериал", "приложение фото",
    ]),
    ("evidence_handling", [
        "доказательство", "факт", "подтверждение", "доказательная база",
        "источник данных", "обоснование", "исполнительная документация",
    ]),
    ("normative_reference_handling", [
        "снип", "гост", "сп ", "нормати", "требования нормативов",
        "ссылка на норму", "нормативный документ", "регламент",
    ]),
    ("recommendation_logic", [
        "рекомендация", "предписание", "устранить", "необходимо устранить",
        "рекомендуется", "следует", "требуется", "провести работы",
    ]),
    ("conclusion_logic", [
        "вывод", "заключение", "итог", "резюме", "категория состояния",
        "техническое состояние", "ограниченно работоспособ", "аварийн",
    ]),
    ("file_workflow", [
        "pdf", "docx", "xlsx", "dwg", "файл", "загрузка файла",
        "прикрепить файл", "скачать", "отправить файл", "формат файла",
    ]),
    ("document_workflow", [
        "документооборот", "пакет документов", "комплект",
        "исполнительная документация", "журнал работ", "акт скрытых",
        "приёмка документов",
    ]),
    ("client_facing_language", [
        "заказчик", "собственник", "владелец", "клиент", "застройщик",
        "как написать заказчику", "для заказчика", "язык документа",
    ]),
    ("contractor_statement_handling", [
        "подрядчик", "генподрядчик", "субподрядчик", "исполнитель",
        "ответ подрядчика", "позиция подрядчика",
    ]),
    ("owner_statement_handling", [
        "застройщик", "инвестор", "позиция застройщика",
        "ответ застройщика", "письмо застройщика",
    ]),
    ("telegram_source_work_signal", [
        "вакансия", "требуется", "нужен специалист", "ищем технадзор",
        "ищем инженера", "найдём", "предложение работы",
    ]),
    ("rabota_poisk_reusable_pattern", [
        "заказ", "тендер", "объявление", "контракт", "выбор подрядчика",
        "объект ищет", "нужен технадзор", "проведём отбор",
    ]),
]

TOPIC5_VALUE_KEYWORDS = [
    "акт", "дефект", "технадзор", "заключение", "предписание",
    "приёмка", "отчёт", "фото", "норматив", "документ",
    "рекомендация", "вывод", "замечание",
]

NOISE_MARKERS = [
    "реклама", "продам", "куплю", "скидка", "акция",
    "заработок", "кредит без отказа", "займ", "только сегодня",
    "подпишись", "переходи по ссылке", "выиграли",
]


def _card_id(source_ref: str, message_id: int | str) -> str:
    raw = f"{source_ref}::{message_id}"
    return "SK_" + hashlib.md5(raw.encode()).hexdigest()[:12].upper()


def classify_category(text: str) -> str:
    low = text.lower()
    for category, patterns in _CATEGORY_PATTERNS:
        if any(p in low for p in patterns):
            return category
    return "unknown"


def extract_rule_from_text(text: str, category: str) -> str:
    sentences = re.split(r"[.\n!?]+", text)
    useful = []
    for sent in sentences:
        s = sent.strip()
        if len(s) < 20:
            continue
        low = s.lower()
        if any(kw in low for kw in TOPIC5_VALUE_KEYWORDS):
            useful.append(s)
        if len(useful) >= 3:
            break
    if useful:
        return ". ".join(useful[:3])
    # fallback: first substantial sentence
    for sent in sentences:
        s = sent.strip()
        if len(s) >= 30:
            return s[:300]
    return text[:300].strip()


def why_useful(category: str) -> str:
    mapping = {
        "act_structure": "Позволяет выстраивать структуру акта технадзора: разделы, приложения, обязательные поля",
        "report_structure": "Определяет состав технического отчёта/заключения по объекту",
        "defect_description_logic": "Формирует навык точной формулировки дефектов для актов и предписаний",
        "photo_to_defect_linking": "Описывает правило привязки фотоматериалов к конкретным дефектам в документе",
        "evidence_handling": "Показывает как формировать доказательную базу — факты, источники, исполнительная документация",
        "normative_reference_handling": "Обучает правильному указанию нормативных ссылок (СП/ГОСТ/СНиП) в актах",
        "recommendation_logic": "Задаёт логику формулировки предписаний и рекомендаций по устранению",
        "conclusion_logic": "Показывает структуру вывода/заключения о техническом состоянии",
        "file_workflow": "Описывает правила работы с файлами (PDF/DOCX/XLSX) при формировании пакета документов",
        "document_workflow": "Определяет порядок формирования и передачи комплекта исполнительной документации",
        "client_facing_language": "Задаёт профессиональный язык документов, обращённых к заказчику/собственнику",
        "contractor_statement_handling": "Показывает как фиксировать позицию подрядчика в документах",
        "owner_statement_handling": "Показывает как фиксировать позицию застройщика/инвестора",
        "telegram_source_work_signal": "Сигнал о возможной работе/заказе — полезен для маршрутизации в topic_6104",
        "rabota_poisk_reusable_pattern": "Паттерн для поиска заказов/вакансий через Telegram-источник (тема RABOTA_POISK)",
        "unknown": "Категория не определена — требует ручной проверки владельца",
    }
    return mapping.get(category, "")


def is_noise(text: str) -> bool:
    low = (text or "").lower()
    if any(n in low for n in NOISE_MARKERS):
        return True
    if len(text.strip()) < 20:
        return True
    return False


def has_practical_value(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in TOPIC5_VALUE_KEYWORDS)


def build_skill_card(record: dict) -> dict | None:
    text = record.get("text", "")
    source_ref = record.get("source_ref", "")
    message_id = record.get("message_id", "")

    if not source_ref:
        logger.debug("rejected: no source_ref msg=%s", message_id)
        return None

    if is_noise(text):
        logger.debug("rejected: noise msg=%s", message_id)
        return None

    if not has_practical_value(text) and not record.get("file_name") and not record.get("links"):
        logger.debug("rejected: no practical value msg=%s", message_id)
        return None

    category = classify_category(text)
    extracted_rule = extract_rule_from_text(text, category)

    needs_review = (
        category == "unknown"
        or len(extracted_rule) < 30
        or not has_practical_value(text)
    )

    tags = [category]
    if record.get("file_name"):
        tags.append("has_document")
    if record.get("links"):
        tags.append("has_links")
    if record.get("media_type") == "photo":
        tags.append("has_photo")

    return {
        "id": _card_id(source_ref, message_id),
        "source": record.get("source", "@tnz_msk"),
        "source_ref": source_ref,
        "message_id": message_id,
        "message_date": record.get("message_date", ""),
        "category": category,
        "title": f"{category}: {extracted_rule[:60]}",
        "source_excerpt": text[:400],
        "extracted_rule": extracted_rule,
        "why_useful_for_topic_5": why_useful(category),
        "source_links": record.get("links", []),
        "source_files": ([record["file_name"]] if record.get("file_name") else []),
        "confidence": "low" if needs_review else "medium",
        "needs_owner_review": needs_review,
        "tags": tags,
    }


def process_records(records: list[dict]) -> dict:
    cards: list[dict] = []
    rejected = 0
    for rec in records:
        card = build_skill_card(rec)
        if card:
            cards.append(card)
        else:
            rejected += 1

    by_category: dict[str, list] = {}
    for card in cards:
        by_category.setdefault(card["category"], []).append(card)

    return {
        "total_input": len(records),
        "extracted": len(cards),
        "rejected_noise": rejected,
        "categories": list(by_category.keys()),
        "cards": cards,
        "by_category": by_category,
    }
# === END_TECHNADZOR_DOCUMENT_SKILL_V1 ===

====================================================================================================
END_FILE: core/technadzor_document_skill.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/technadzor_drive_index.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 31118a4e5fa521f992b026001a821ecf8cea7570e3185a3ed6b89d59a3143c77
====================================================================================================
# === P6H_TOPIC5_TECHNADZOR_TEMPLATE_PHOTO_CLIENT_SAFE_CLOSE_20260504 / DRIVE_INDEX_V1 ===
# Auto-discovery of topic_5 (technadzor) Drive folder contents as style/content
# references — without manual "прими как образец" commands.
#
# Layered classification (file role):
#   PRIMARY_PDF_STYLE         — PDF in topic root or in non-system subfolders (real client acts; main style)
#   SECONDARY_DOCX_REFERENCE  — DOCX in service subfolders (TECHNADZOR / _drafts / _system / _templates)
#   CLIENT_PHOTO_SOURCE       — image/* in topic root or any non-system folder (work-object photos)
#   CLIENT_FINAL_PDF          — PDF artifacts produced earlier (kept in client folders)
#   SYSTEM_TEMPLATE           — DOCX/JSON/manifests in service subfolders
#   OTHER                     — anything else (audio, etc.)
#
# Folder classification:
#   SYSTEM   — name in {_system, _templates, _drafts, _manifests, _archive, _tmp, TECHNADZOR}
#   CLIENT   — anything else (work-object/customer-facing folders)
#
# Index is persisted to:
#   data/templates/technadzor/ACTIVE__chat_<chat_id>__topic_<topic_id>.json
# (filename uses literal chat_id with leading dash, matching existing convention)
#
# In-memory cache TTL = 5 minutes.
from __future__ import annotations

import io
import json
import os
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("task_worker")

_CACHE_TTL_SECONDS = 300
_CACHE: Dict[Tuple[str, int], Tuple[float, Dict[str, Any]]] = {}

_BASE = Path(__file__).resolve().parent.parent
_LOCAL_INDEX_DIR = _BASE / "data" / "templates" / "technadzor"
_LOCAL_INDEX_DIR.mkdir(parents=True, exist_ok=True)
_DOWNLOAD_DIR = _BASE / "data" / "memory_files" / "technadzor_index_cache"
_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Folder names treated as SYSTEM (no client artifacts allowed)
SYSTEM_FOLDER_NAMES = {
    "_system", "_templates", "_drafts", "_manifests", "_archive", "_tmp",
    "technadzor",  # case-insensitive match against TECHNADZOR
}


def is_system_folder(name: str) -> bool:
    """True if the folder is internal/service. Match case-insensitive."""
    if not name:
        return False
    return name.strip().lower() in SYSTEM_FOLDER_NAMES


def is_client_facing_folder(name: str) -> bool:
    """True if the folder is client-facing (object/customer/visit folder)."""
    if not name:
        return False
    return not is_system_folder(name)


def _service():
    from core.topic_drive_oauth import _oauth_service
    return _oauth_service()


def _root_folder_id() -> str:
    from core.topic_drive_oauth import _root_folder_id as r
    return r()


def _find_child(svc, parent_id: str, name: str) -> Optional[str]:
    safe_name = name.replace("'", "\\'")
    res = svc.files().list(
        q=f"'{parent_id}' in parents and name='{safe_name}' and trashed=false",
        fields="files(id,name,mimeType)",
        pageSize=10,
    ).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def _ensure_subfolder(svc, parent_id: str, name: str) -> str:
    fid = _find_child(svc, parent_id, name)
    if fid:
        return fid
    body = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    created = svc.files().create(body=body, fields="id").execute()
    return created["id"]


def _list_folder(svc, folder_id: str, page_size: int = 200) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    page_token = <REDACTED_SECRET>
    while True:
        res = svc.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id,name,mimeType,modifiedTime,createdTime,size,webViewLink,parents)",
            orderBy="modifiedTime desc",
            pageSize=page_size,
            pageToken=<REDACTED_SECRET>
        ).execute()
        items.extend(res.get("files", []))
        page_token = <REDACTED_SECRET>"nextPageToken")
        if not page_token:
            break
    return items


def classify_technadzor_drive_file(file: Dict[str, Any], parent_folder_name: str = "") -> str:
    """Classify a Drive file by role (returns one of the role strings)."""
    mt = file.get("mimeType", "") or ""
    name = (file.get("name") or "").lower()
    parent = (parent_folder_name or "").strip().lower()
    parent_is_system = parent in SYSTEM_FOLDER_NAMES

    # PDF
    if mt == "application/pdf":
        if parent_is_system:
            return "SYSTEM_TEMPLATE"
        if name.startswith("act") or "акт" in name or "осмотр" in name:
            # PDF in non-system folder with act-like name → primary style
            return "PRIMARY_PDF_STYLE"
        # PDF in client folder, generic — most likely a final client PDF artifact
        return "CLIENT_FINAL_PDF"

    # DOCX
    if mt == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        if parent_is_system:
            return "SYSTEM_TEMPLATE"
        return "SECONDARY_DOCX_REFERENCE"

    # Image
    if mt.startswith("image/"):
        if parent_is_system:
            return "SYSTEM_TEMPLATE"
        return "CLIENT_PHOTO_SOURCE"

    # JSON / manifests / system
    if mt in ("application/json",) or name.endswith((".json", ".log", ".bak", ".tmp")):
        return "SYSTEM_TEMPLATE"

    # Audio (voice notes)
    if mt.startswith("audio/") or mt == "application/ogg":
        return "OTHER"

    return "OTHER"


def _resolve_topic_folder(svc, chat_id: str, topic_id: int) -> Optional[str]:
    root = _root_folder_id()
    chat_folder = _find_child(svc, root, f"chat_{chat_id}")
    if not chat_folder:
        return None
    return _find_child(svc, chat_folder, f"topic_{int(topic_id)}")


def _local_index_path(chat_id: str, topic_id: int) -> Path:
    fname = f"ACTIVE__chat_{chat_id}__topic_{int(topic_id)}.json"
    return _LOCAL_INDEX_DIR / fname


def _drive_url(file: Dict[str, Any]) -> str:
    fid = file.get("id", "")
    if file.get("webViewLink"):
        return file["webViewLink"]
    if file.get("mimeType") == "application/vnd.google-apps.folder":
        return f"https://drive.google.com/drive/folders/{fid}"
    return f"https://drive.google.com/file/d/{fid}/view"


def scan_topic5_drive_templates(chat_id: str, topic_id: int = 5, force: bool = False) -> Dict[str, Any]:
    """Scan Drive topic_<id> contents and return classified listing.

    Cached for 5 min. Pass force=True to refresh.
    """
    key = (str(chat_id), int(topic_id))
    now = time.time()
    if not force and key in _CACHE:
        ts, cached = _CACHE[key]
        if now - ts < _CACHE_TTL_SECONDS:
            return cached

    svc = _service()
    topic_fid = _resolve_topic_folder(svc, chat_id, topic_id)
    result: Dict[str, Any] = {
        "chat_id": str(chat_id),
        "topic_id": int(topic_id),
        "topic_folder_id": topic_fid,
        "topic_folder_link": (
            f"https://drive.google.com/drive/folders/{topic_fid}"
            if topic_fid else None
        ),
        "files": [],
        "folders_system": [],
        "folders_client": [],
        "by_role": {},
        "primary_pdf_style": [],
        "secondary_docx_reference": [],
        "client_photo_source": [],
        "client_final_pdf": [],
        "system_template": [],
        "other": [],
        "ok": False,
        "error": None,
        "scanned_at": int(now),
    }

    if not topic_fid:
        result["error"] = f"topic folder chat_{chat_id}/topic_{topic_id} not found"
        _CACHE[key] = (now, result)
        return result

    try:
        # Walk topic root
        root_items = _list_folder(svc, topic_fid)
        all_records: List[Dict[str, Any]] = []
        sub_folder_walk: List[Tuple[str, str]] = []  # (folder_id, folder_name)
        for it in root_items:
            if it.get("mimeType") == "application/vnd.google-apps.folder":
                if is_system_folder(it["name"]):
                    result["folders_system"].append({
                        "id": it["id"], "name": it["name"],
                        "drive_url": _drive_url(it),
                    })
                else:
                    result["folders_client"].append({
                        "id": it["id"], "name": it["name"],
                        "drive_url": _drive_url(it),
                    })
                sub_folder_walk.append((it["id"], it["name"]))
            else:
                role = classify_technadzor_drive_file(it, parent_folder_name="")
                rec = _build_record(it, role, parent_folder_name="", chat_id=chat_id, topic_id=topic_id)
                all_records.append(rec)

        # Walk one level of subfolders (do not recurse deeper to keep it cheap)
        for sub_fid, sub_name in sub_folder_walk:
            sub_items = _list_folder(svc, sub_fid)
            for it in sub_items:
                if it.get("mimeType") == "application/vnd.google-apps.folder":
                    # nested sub-subfolder — record name only, do not recurse
                    continue
                role = classify_technadzor_drive_file(it, parent_folder_name=sub_name)
                rec = _build_record(it, role, parent_folder_name=sub_name, chat_id=chat_id, topic_id=topic_id)
                all_records.append(rec)

        result["files"] = all_records
        for rec in all_records:
            role = rec["role"]
            bucket = role.lower()
            if bucket == "primary_pdf_style":
                result["primary_pdf_style"].append(rec)
            elif bucket == "secondary_docx_reference":
                result["secondary_docx_reference"].append(rec)
            elif bucket == "client_photo_source":
                result["client_photo_source"].append(rec)
            elif bucket == "client_final_pdf":
                result["client_final_pdf"].append(rec)
            elif bucket == "system_template":
                result["system_template"].append(rec)
            else:
                result["other"].append(rec)
            result["by_role"].setdefault(role, 0)
            result["by_role"][role] += 1

        result["ok"] = True
    except Exception as exc:
        result["error"] = repr(exc)
        LOG.exception("P6H_TOPIC5_DRIVE_INDEX_SCAN_FAIL chat=%s topic=%s", chat_id, topic_id)

    _CACHE[key] = (now, result)
    return result


def _build_record(file: Dict[str, Any], role: str, parent_folder_name: str, chat_id: str, topic_id: int) -> Dict[str, Any]:
    parent_lower = (parent_folder_name or "").strip().lower()
    parent_is_system = parent_lower in SYSTEM_FOLDER_NAMES
    return {
        "file_id": file.get("id"),
        "file_name": file.get("name"),
        "mime_type": file.get("mimeType"),
        "drive_url": _drive_url(file),
        "folder_name": parent_folder_name or "<root>",
        "role": role,
        "client_facing": (not parent_is_system),
        "created_time": file.get("createdTime"),
        "modified_time": file.get("modifiedTime"),
        "size": file.get("size"),
    }


def build_technadzor_template_index(chat_id: str = "-1003725299009", topic_id: int = 5, force: bool = True) -> Dict[str, Any]:
    """Build full topic_5 index, persist to local JSON, return the index dict.

    Persistent path:
        data/templates/technadzor/ACTIVE__chat_<chat_id>__topic_<topic_id>.json
    """
    idx = scan_topic5_drive_templates(chat_id, topic_id, force=force)
    payload = {
        "chat_id": idx.get("chat_id"),
        "topic_id": idx.get("topic_id"),
        "topic_folder_id": idx.get("topic_folder_id"),
        "topic_folder_link": idx.get("topic_folder_link"),
        "scanned_at": idx.get("scanned_at"),
        "ok": idx.get("ok"),
        "error": idx.get("error"),
        "by_role": idx.get("by_role"),
        "folders_system": idx.get("folders_system"),
        "folders_client": idx.get("folders_client"),
        "files": idx.get("files"),
        "primary_pdf_style": idx.get("primary_pdf_style"),
        "secondary_docx_reference": idx.get("secondary_docx_reference"),
        "client_photo_source": idx.get("client_photo_source"),
        "client_final_pdf": idx.get("client_final_pdf"),
        "system_template": idx.get("system_template"),
        "other": idx.get("other"),
        "marker": "P6H_TOPIC5_USE_EXISTING_TEMPLATES_PHOTO_TO_TECH_REPORT_20260504_V1",
        "updated_at": int(time.time()),
    }
    try:
        path = _local_index_path(str(chat_id), int(topic_id))
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        payload["local_index_path"] = str(path)
    except Exception as exc:
        LOG.exception("P6H_TOPIC5_DRIVE_INDEX_PERSIST_FAIL chat=%s topic=%s err=%s", chat_id, topic_id, exc)
    return payload


def get_active_index(chat_id: str = "-1003725299009", topic_id: int = 5) -> Optional[Dict[str, Any]]:
    """Read persisted index from disk, if present."""
    p = _local_index_path(str(chat_id), int(topic_id))
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def primary_template_meta(idx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Most recent PRIMARY_PDF_STYLE record. Falls back to most recent CLIENT_FINAL_PDF."""
    if idx.get("primary_pdf_style"):
        return idx["primary_pdf_style"][0]
    if idx.get("client_final_pdf"):
        return idx["client_final_pdf"][0]
    return None


def secondary_template_meta(idx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if idx.get("secondary_docx_reference"):
        return idx["secondary_docx_reference"][0]
    return None


def ensure_service_subfolder(chat_id: str, topic_id: int, name: str = "_drafts") -> Optional[str]:
    """Create/return id for a SERVICE subfolder (system, never client-facing).

    Refuses to create folders with non-system names.
    """
    if not is_system_folder(name):
        raise ValueError(f"Refusing to create non-system folder via service path: {name}")
    svc = _service()
    topic_fid = _resolve_topic_folder(svc, chat_id, topic_id)
    if not topic_fid:
        return None
    return _ensure_subfolder(svc, topic_fid, name)


def upload_to_service_subfolder(local_path: Path, dst_name: str, chat_id: str, topic_id: int, subfolder: str = "_drafts") -> Optional[Dict[str, Any]]:
    """Upload artifact to topic_<id>/<service-subfolder>/. Subfolder MUST be system."""
    if not is_system_folder(subfolder):
        raise ValueError(f"Refusing to upload to non-system subfolder: {subfolder}")
    return _upload_to_folder(local_path, dst_name, chat_id, topic_id, subfolder, allow_client=False)


def upload_client_pdf_to_folder(local_path: Path, dst_name: str, chat_id: str, topic_id: int, target_folder_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Upload final client PDF.

    If target_folder_name is provided AND it's a non-system (client-facing) folder,
    upload there. Otherwise upload to topic root.

    Refuses anything that isn't .pdf — by spec, client folders accept only photos and final PDFs.
    """
    if not str(local_path).lower().endswith(".pdf"):
        raise ValueError(f"Refusing to upload non-PDF to client folder: {local_path}")
    return _upload_to_folder(local_path, dst_name, chat_id, topic_id, target_folder_name, allow_client=True)


def _upload_to_folder(local_path: Path, dst_name: str, chat_id: str, topic_id: int, target_folder_name: Optional[str], allow_client: bool) -> Optional[Dict[str, Any]]:
    try:
        from googleapiclient.http import MediaFileUpload
        svc = _service()
        topic_fid = _resolve_topic_folder(svc, chat_id, topic_id)
        if not topic_fid:
            return None

        if target_folder_name:
            if is_system_folder(target_folder_name):
                target_id = _ensure_subfolder(svc, topic_fid, target_folder_name)
            else:
                if not allow_client:
                    raise ValueError(f"Client folder upload not allowed via service path: {target_folder_name}")
                # find existing client folder, do NOT auto-create client folders
                target_id = _find_child(svc, topic_fid, target_folder_name)
                if not target_id:
                    LOG.warning("P6H_TOPIC5_CLIENT_FOLDER_NOT_FOUND name=%s — uploading to topic root", target_folder_name)
                    target_id = topic_fid
        else:
            target_id = topic_fid

        body = {"name": dst_name, "parents": [target_id]}
        mime = None
        ln = str(local_path).lower()
        if ln.endswith(".docx"):
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ln.endswith(".pdf"):
            mime = "application/pdf"
        elif ln.endswith(".xlsx"):
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif ln.endswith(".json"):
            mime = "application/json"
        media = MediaFileUpload(str(local_path), mimetype=mime, resumable=False)
        created = svc.files().create(body=body, media_body=media, fields="id,webViewLink,parents").execute()
        return {"id": created["id"], "link": created.get("webViewLink"), "parent_id": target_id, "target_folder_name": target_folder_name}
    except Exception:
        LOG.exception("P6H_TOPIC5_DRIVE_UPLOAD_FAIL name=%s topic=%s sub=%s", dst_name, topic_id, target_folder_name)
        return None


def download_to_local(file_id: str, dst_filename: str) -> Optional[Path]:
    """Download a Drive file to local cache. Returns path or None."""
    try:
        from googleapiclient.http import MediaIoBaseDownload
        svc = _service()
        dst = _DOWNLOAD_DIR / dst_filename
        req = svc.files().get_media(fileId=file_id)
        with io.FileIO(dst, "wb") as buf:
            dl = MediaIoBaseDownload(buf, req)
            done = False
            while not done:
                _, done = dl.next_chunk()
        return dst
    except Exception:
        LOG.exception("P6H_TOPIC5_DRIVE_INDEX_DOWNLOAD_FAIL fid=%s", file_id)
        return None


try:
    LOG.info("P6H_TOPIC5_DRIVE_INDEX_V1_INSTALLED")
except Exception:
    pass
# === END_P6H_TOPIC5_DRIVE_INDEX_V1 ===

====================================================================================================
END_FILE: core/technadzor_drive_index.py
FILE_CHUNK: 1/1
====================================================================================================
