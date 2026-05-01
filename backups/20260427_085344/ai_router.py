import os
import re
import json
import hashlib
import logging
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
ENV_PATH = f"{BASE}/.env"
LOG_PATH = f"{BASE}/logs/ai_router.log"

load_dotenv(ENV_PATH, override=True)
os.makedirs(f"{BASE}/logs", exist_ok=True)

logger = logging.getLogger("ai_router")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip().rstrip("/")

DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat").strip() or "deepseek/deepseek-chat"
ONLINE_MODEL = os.getenv("OPENROUTER_MODEL_ONLINE", "google/gemini-2.5-flash:online").strip() or "google/gemini-2.5-flash:online"

SEARCH_RE = [
    r"\bнайди\b", r"\bнайти\b", r"\bпоиск\b", r"\bпоищи\b", r"\bsearch\b",
    r"\bцена\b", r"\bстоимость\b", r"\bсколько стоит\b",
    r"\bavito\b", r"\bozon\b", r"\bwildberries\b", r"\bauto\.ru\b", r"\bdrom\b",
    r"\bновости\b", r"\bпогода\b", r"\bкурс\b", r"\bмаркетплейс\b", r"\bссылк", r"\bкупить\b", r"\bзаказать\b", r"\bтовар\b",
    r"озон", r"валбер", r"вайлдбер", r"площадк"
]

BAD_CONTEXT_RE = [
    r"forbidden default model",
    r"traceback",
    r"telegramconflicterror",
    r"voice unavailable",
    r"stt failed",
    r"/root/",
    r"\.log",
    r"\.json"
]

BAD_RESULT_RE = [
    r"\bой\b",
    r"сорян",
    r"дружище",
    r"не переживай",
    r"дай мне немного времени",
    r"я могу помочь",
    r"извини",
    r"извините",
    r"я тут",
    r"уведомлятор",
    r"перегрелся",
    r"😅",
    r"💪",
    r"😎",
    r"непонятно",
    r"уточните",
    r"недостаточно данных",
    r"\bищу\b",
    r"\bнайду\b",
    r"ожидаю уточнения",
    r"ссылк[аи]\s+предоставлю",
    r"готов искать",
    r"могу найти",
    r"укажите,?\s+что именно нужно найти"
]

ROUTER_STOPWORDS = {
    "что","это","как","для","про","или","если","чтобы","только","нужно","надо","где","когда",
    "который","которая","которые","были","было","есть","ещё","уже","всё","тут","там","этот",
    "эта","эти","мой","моя","мои","твои","ваши","наши","их","его","ее","её",
    "and","the","for","with","from","this","that","into","your","you","are"
}

MEMORY_NOISE_MARKERS = [
    "не понял",
    "уточните",
    "не знаю",
    "повторите",
    "нет данных",
]

SYSTEM_PROMPT = """Ты AI-роутер системы AREAL-NEVA ORCHESTRA

Роль:
- выполнять задачу строго по запросу пользователя
- отвечать коротко, делово, по сути
- без болтовни, без эмодзи, без извинений
- без служебных фраз и внутренних технических деталей

Правила:
- главный приоритет: текущий запрос пользователя
- если в контексте есть блок [TYPE:SEARCH_RESULT] — это реальные данные из интернета, используй ТОЛЬКО их, не выдумывай товары, цены, ссылки и названия от себя
- никогда не пиши "ищу", "найду", "продолжаю поиск", "ссылки предоставлю" — если данные есть, сразу давай их
- если есть активная незавершённая задача, используй её как ближайший контекст
- pin использовать только если он релевантен текущему запросу — если запрос новый или не связан с pin, полностью игнорируй pin
- краткосрочную память использовать только как последние 2-3 релевантных шага
- долгосрочную память использовать только как факты и результаты
- не тащи в ответ ошибки, логи, пути, json-обрывки, мусор
- если запрос это обычный разговор ("как дела", "привет", "ты тут", "ты живой", "как ты") — отвечай коротко как на разговор, не пересказывай задачи из памяти и не тащи контекст

Требования к ответу:
- только ответ по сути задачи
- если запрос неясен — задай один короткий уточняющий вопрос по сути задачи
- не писать пользователю служебные сообщения
""".strip()

SEARCH_SYSTEM_PROMPT = """Ты выполняешь реальный поиск в интернете.
Найди реальные результаты по запросу — с настоящими названиями, ценами и источниками.
Не выдумывай названия, артикулы, цены, ссылки и площадки.
Если не знаешь точную цену — не пиши её.
Если запрос НЕ про Avito, Ozon, Wildberries, auto.ru, drom:
- если в результате поиска есть реальная ссылка, обязательно выводи полный URL
- запрещено писать слово "Ссылка" без самого URL
- запрещено писать "ищу", "продолжаю поиск", "ссылки предоставлю"
Формат ответа: Название, Цена если известна, Ссылка: https://... если есть, Источник.
Для Avito, Ozon, Wildberries, auto.ru, drom допускается ответ без URL.
Ссылки давай только если они реальные — не выдумывай URL.
""".strip()

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()


def _dedup_text(text: str) -> str:
    seen = set()
    out = []
    for line in text.split("\n"):
        key = line.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(line)
    return "\n".join(out)

def _clean(text: str, limit: int = 12000) -> str:
    text = (text or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]

def _match_any(patterns: List[str], text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t, re.I) for p in patterns)

def _keywords(text: str) -> set[str]:
    t = _clean(text, 4000).lower()
    words = re.findall(r"[a-zA-Zа-яА-Я0-9_./:-]+", t)
    out = set()
    for w in words:
        if len(w) <= 3:
            continue
        if w in ROUTER_STOPWORDS:
            continue
        out.add(w)
    return out

def _has_overlap(a: str, b: str) -> bool:
    ka = _keywords(a)
    kb = _keywords(b)
    if not ka or not kb:
        return False
    return len(ka & kb) > 0

def _is_noise_text(text: str) -> bool:
    low = _clean(text, 4000).lower()
    return any(m in low for m in MEMORY_NOISE_MARKERS)

def _search_intent(text: str, input_type: str) -> bool:
    t = _clean(text, 500).lower()
    if re.fullmatch(r"статус", t):
        return False
    if re.search(r"(что мы здесь делаем|для чего этот чат|что это за чат|назначение чата|о ч[её]м этот чат|напомни.*чат|чем занимается чат)", t):
        return False
    if (input_type or "").lower() == "search":
        return True
    return _match_any(SEARCH_RE, text)

def _sanitize_block(label: str, value: Any) -> str:
    text = _clean(_s(value), 4000)
    if not text:
        return ""
    if _match_any(BAD_CONTEXT_RE, text):
        return ""
    if _is_noise_text(text):
        return ""
    return f"[TYPE:{label}]\n{text}"

def _dedup_blocks(blocks: List[str]) -> List[str]:
    out = []
    seen = set()
    for block in blocks:
        b = _clean(block, 4000)
        if not b:
            continue
        key = hashlib.sha1(re.sub(r"\s+", " ", b.lower()).encode("utf-8")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        out.append(b)
    return out

def _extract_user_text(payload: Dict[str, Any]) -> str:
    for key in ("normalized_input", "raw_input", "input", "text", "prompt", "message", "transcript"):
        text = _clean(_s(payload.get(key)))
        if text:
            return text
    return ""


def _build_messages(payload: Dict[str, Any], user_text: str) -> List[Dict[str, str]]:
    user_text = _dedup_text(user_text)
    if not user_text.strip():
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "REQUEST:\nпустой запрос"}
        ]

    input_type = _s(payload.get("input_type")).lower() or "text"
    state = _s(payload.get("state")).upper() or "IN_PROGRESS"

    topic_role = _clean(_s(payload.get("topic_role")), 500)
    topic_directions = _clean(_s(payload.get("topic_directions")), 1000)
    system_content = SYSTEM_PROMPT
    if topic_role:
        system_content = f"Роль этого чата: {topic_role}\n\n" + system_content
    if topic_directions:
        system_content = system_content + f"\n\nТиповые задачи этого чата: {topic_directions}"


    blocks_src = []

    active_block = _sanitize_block("ACTIVE_TASK", payload.get("active_task_context"))
    if active_block:
        blocks_src.append(active_block)

    pin_raw = _clean(_s(payload.get("pin_context")), 4000)
    if pin_raw and _has_overlap(user_text, pin_raw):
        pin_block = _sanitize_block("PIN", pin_raw)
        if pin_block:
            blocks_src.append(pin_block)

    short_block = _sanitize_block("SHORT_MEMORY", payload.get("short_memory_context"))
    if short_block:
        blocks_src.append(short_block)

    long_block = _sanitize_block("LONG_MEMORY", payload.get("long_memory_context"))
    if long_block:
        blocks_src.append(long_block)

    archive_raw = _clean(_s(payload.get("archive_context")), 4000)
    if archive_raw and _has_overlap(user_text, archive_raw):
        archive_lines = [ln for ln in archive_raw.split("\n") if ln.strip() and _has_overlap(user_text, ln)]
        archive_block = _sanitize_block("ARCHIVE", "\n".join(archive_lines[:3]))
        if archive_block:
            blocks_src.append(archive_block)

    search_raw = _clean(_s(payload.get("search_context")), 4000)
    if search_raw and _has_overlap(user_text, search_raw):
        search_block = _sanitize_block("SEARCH_RESULT", search_raw)
        if search_block:
            blocks_src.append(search_block)

    blocks = _dedup_blocks(blocks_src)

    user_parts = [
        f"STATE: {state}",
        f"INPUT_TYPE: {input_type}",
    ]
    if blocks:
        user_parts.append("CONTEXT:\n" + "\n\n".join(blocks))
    user_parts.append("REQUEST:\n" + user_text)

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": "\n\n".join(user_parts)},
    ]

def _extract_content(data: Dict[str, Any]) -> str:
    try:
        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
                else:
                    parts.append(_s(item))
            return _clean("\n".join(parts))
        return _clean(_s(content))
    except Exception:
        return _clean(json.dumps(data, ensure_ascii=False)[:2000])

async def _openrouter_call(model: str, messages: List[Dict[str, str]]) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0)) as client:
        r = await client.post(f"{OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=body)
    if r.status_code != 200:
        msg = f"OPENROUTER_HTTP_{r.status_code}: {r.text[:500]}"
        logger.error(msg)
        raise RuntimeError(msg)
    return _extract_content(r.json())

async def process_ai_task(payload: Dict[str, Any]) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    user_text = _dedup_text(_extract_user_text(payload))
    if not user_text:
        return ""

    input_type = _s(payload.get("input_type")).lower()
    is_search = _search_intent(user_text, input_type)
    work_payload = dict(payload)

    if is_search:
        logger.info(
            "router_search_call model=%s input_type=%s state=%s chars=%s",
            ONLINE_MODEL,
            input_type or "text",
            _s(payload.get("state")).upper() or "IN_PROGRESS",
            len(user_text),
        )
        try:
            search_result = await _openrouter_call(
                ONLINE_MODEL,
                [
                    {"role": "system", "content": SEARCH_SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
            )
        except Exception as e:
            logger.error("search_model_fail err=%s — fallback to DEFAULT_MODEL without search", e)
            search_result = ""

        search_result = _clean(_s(search_result), 4000)
        if not search_result:
            logger.warning("web_search_empty query=%s", user_text[:200])
        else:
            existing = _clean(_s(work_payload.get("search_context")), 4000)
            work_payload["search_context"] = search_result + ("\n\n" + existing if existing else "")
            logger.info("web_search_ok chars=%s", len(search_result))

    logger.info(
        "router_call model=%s input_type=%s state=%s chars=%s is_search=%s",
        DEFAULT_MODEL,
        input_type or "text",
        _s(payload.get("state")).upper() or "IN_PROGRESS",
        len(user_text),
        is_search,
    )

    messages = _build_messages(work_payload, user_text)
    ctx_str = _clean_context("\n\n".join(m.get("content", "") for m in messages))
    if _context_has_answer(ctx_str):
        for m in messages:
            if m.get("role") == "system":
                m["content"] += "\nFORBIDDEN: do not ask clarifying questions. Answer directly."
                break
    result = await _openrouter_call(DEFAULT_MODEL, messages)

    if _match_any(BAD_RESULT_RE, result):
        logger.warning("router_result_filtered result=%s", result[:120])
        return ""

    logger.info("router_ok chars=%s", len(result))
    return result



def _clean_context(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r", "\n")
    text = text.replace("\t", " ")
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()[:12000]

def _context_has_answer(text: str) -> bool:
    if not text:
        return False
    return len(text.strip()) > 50

# FORCE CLEAN CONTEXT

# === CANON_PASS2_CONTEXT_CLEANUP ===
def canon_pass2_clean_context_block(text, limit=12000):
    try:
        from core.quality_gate import clean_text
        return clean_text(text, limit)
    except Exception:
        return ("" if text is None else str(text))[:limit]

def canon_pass2_filter_context_items(items, user_text="", topic_id=0, limit=20):
    out = []
    words = {w.lower() for w in str(user_text or "").split() if len(w) > 3}
    for item in items or []:
        s = canon_pass2_clean_context_block(item, 2000)
        if not s:
            continue
        if words:
            low = s.lower()
            if not any(w in low for w in words):
                continue
        out.append(s)
        if len(out) >= limit:
            break
    return out
# === END_CANON_PASS2_CONTEXT_CLEANUP ===

# === CANON_PASS3_REAL_SEARCH_AND_CONTEXT_WIRING ===
import contextvars as _canon_pass3_contextvars

_canon_pass3_payload_ctx = _canon_pass3_contextvars.ContextVar("canon_pass3_payload_ctx", default={})

def _canon_pass3_payload_topic(payload):
    try:
        return int(payload.get("topic_id") or payload.get("topic") or 0)
    except Exception:
        return 0

def _canon_pass3_payload_chat(payload):
    return payload.get("chat_id") or payload.get("chat") or "-1003725299009"

def _canon_pass3_payload_role(payload):
    return payload.get("topic_role") or payload.get("role") or ""

if "process_ai_task" in globals():
    _canon_pass3_orig_process_ai_task = process_ai_task

    async def process_ai_task(*args, **kwargs):
        payload = {}
        if args and isinstance(args[0], dict):
            payload = dict(args[0])
        if isinstance(kwargs.get("payload"), dict):
            payload = dict(kwargs["payload"])
        token = _canon_pass3_payload_ctx.set(payload)
        try:
            return await _canon_pass3_orig_process_ai_task(*args, **kwargs)
        finally:
            _canon_pass3_payload_ctx.reset(token)

if "_openrouter_call" in globals():
    _canon_pass3_orig_openrouter_call = _openrouter_call

    async def _openrouter_call(model, messages, *args, **kwargs):
        payload = _canon_pass3_payload_ctx.get({}) or {}
        try:
            online_model = globals().get("ONLINE_MODEL", "")
            is_online = bool(online_model and str(model).strip() == str(online_model).strip())
            if is_online:
                from core.search_guard import get_search_cache, save_search_cache, normalize_search_query
                chat_id = _canon_pass3_payload_chat(payload)
                topic_id = _canon_pass3_payload_topic(payload)
                role = _canon_pass3_payload_role(payload)
                user_text = ""
                for m in messages or []:
                    if isinstance(m, dict) and m.get("role") == "user":
                        user_text = str(m.get("content") or "")[-1000:]
                query = normalize_search_query(user_text, role)
                cached = get_search_cache(chat_id, topic_id, query)
                if cached:
                    try:
                        logger.info("SEARCH_CACHE_HIT topic_id=%s chars=%s", topic_id, len(cached))
                    except Exception:
                        pass
                    return cached
                try:
                    logger.info("SEARCH_CACHE_MISS topic_id=%s", topic_id)
                    logger.info("ONLINE_MODEL_CALLED model=%s topic_id=%s", model, topic_id)
                except Exception:
                    pass
                result = await _canon_pass3_orig_openrouter_call(model, messages, *args, **kwargs)
                save_search_cache(chat_id, topic_id, query, result)
                try:
                    logger.info("SEARCH_RESULT_NORMALIZED topic_id=%s chars=%s", topic_id, len(str(result or "")))
                except Exception:
                    pass
                return result
        except Exception:
            pass
        return await _canon_pass3_orig_openrouter_call(model, messages, *args, **kwargs)

if "_build_messages" in globals():
    _canon_pass3_orig_build_messages = _build_messages

    def _build_messages(*args, **kwargs):
        msgs = _canon_pass3_orig_build_messages(*args, **kwargs)
        try:
            from core.topic_context_guard import clean_context_text
            cleaned = []
            for m in msgs or []:
                if isinstance(m, dict) and "content" in m:
                    mm = dict(m)
                    mm["content"] = clean_context_text(mm.get("content"), 12000)
                    cleaned.append(mm)
                else:
                    cleaned.append(m)
            return cleaned
        except Exception:
            return msgs
# === END_CANON_PASS3_REAL_SEARCH_AND_CONTEXT_WIRING ===
