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

load_dotenv(ENV_PATH, override=False)
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

SEARCH_SYSTEM_PROMPT = """Ты выполняешь реальный поиск товаров в интернете.
Найди реальные товары по запросу — с настоящими названиями и реальными ценами.
Не выдумывай названия, артикулы, цены и ссылки.
Если не знаешь точную цену — не пиши её.
Площадки: Ozon, Wildberries, Avito, Яндекс.Маркет, DNS, Citilink и другие.
Формат: название товара, цена если известна, рейтинг если известен, площадка.
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

def _clean(text: str, limit: int = 12000) -> str:
    text = (text or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]

def _match_any(patterns: List[str], text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t, re.I) for p in patterns)

def _search_intent(text: str, input_type: str) -> bool:
    if (input_type or "").lower() == "search":
        return True
    return _match_any(SEARCH_RE, text)

def _sanitize_block(label: str, value: Any) -> str:
    text = _clean(_s(value), 4000)
    if not text:
        return ""
    if _match_any(BAD_CONTEXT_RE, text):
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
    input_type = _s(payload.get("input_type")).lower() or "text"
    state = _s(payload.get("state")).upper() or "IN_PROGRESS"

    blocks = _dedup_blocks([
        _sanitize_block("ACTIVE_TASK", payload.get("active_task_context")),
        _sanitize_block("PIN", payload.get("pin_context")),
        _sanitize_block("SHORT_MEMORY", payload.get("short_memory_context")),
        _sanitize_block("LONG_MEMORY", payload.get("long_memory_context")),
        _sanitize_block("SEARCH_RESULT", payload.get("search_context")),
    ])

    user_parts = [
        f"STATE: {state}",
        f"INPUT_TYPE: {input_type}",
    ]
    if blocks:
        user_parts.append("CONTEXT:\n" + "\n\n".join(blocks))
    user_parts.append("REQUEST:\n" + user_text)

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
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
    async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=30.0)) as client:
        r = await client.post(f"{OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=body)
    if r.status_code != 200:
        msg = f"OPENROUTER_HTTP_{r.status_code}: {r.text[:500]}"
        logger.error(msg)
        raise RuntimeError(msg)
    return _extract_content(r.json())

async def process_ai_task(payload: Dict[str, Any]) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    user_text = _extract_user_text(payload)
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

    result = await _openrouter_call(DEFAULT_MODEL, _build_messages(work_payload, user_text))

    if _match_any(BAD_RESULT_RE, result):
        logger.warning("router_result_filtered result=%s", result[:120])
        return ""

    logger.info("router_ok chars=%s", len(result))
    return result

# FORCE CLEAN CONTEXT
