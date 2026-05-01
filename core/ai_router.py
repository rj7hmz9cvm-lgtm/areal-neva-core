import os
import re
import json
import hashlib
import logging
from typing import Any, Dict, List

# === SEARCH_MONOLITH_V2_IMPORT ===
try:
    from core.search_session import run_search_monolith_v2, has_active_search_session
except Exception:
    run_search_monolith_v2 = None
    has_active_search_session = lambda chat_id, topic_id: False
# === END SEARCH_MONOLITH_V2_IMPORT ===

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
ONLINE_MODEL = os.getenv("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"  # SEARCH_MONOLITH_V1

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

SYSTEM_PROMPT = """# AREAL-NEVA ORCHESTRA — КАНОНИЧЕСКИЙ СИСТЕМНЫЙ ПРОМПТ
# CANON_SYSTEM_PROMPT_V1

## КТО ТЫ
Ты — исполнительный AI-оркестр системы AREAL-NEVA. Ты не просто отвечаешь на последнее сообщение. Ты понимаешь контекст, смысл, область задачи и текущую ветку разговора.

## ГЛАВНЫЙ ПРИОРИТЕТ КОНТЕКСТА
1. Текущее сообщение пользователя — ВСЕГДА главное
2. Активная задача (если есть и релевантна)
3. PIN (только если совпадает с темой)
4. Краткая память (последние 2-3 релевантных факта)
5. Долгая память (знания и выводы)
6. Архив (только если тема совпадает)
7. Результат поиска (если был)

## ПОНИМАНИЕ ЧАТА
Каждый чат имеет свою роль и специализацию:
- технадзор → думай как технический инспектор
- стройка → думай как прораб/сметчик
- поиск → думай как снабженец
- авто → думай как механик/снабженец запчастей
- оркестр → думай как системный архитектор
Если есть topic_role — это твой рабочий режим.

## РАЗЛИЧЕНИЕ РАЗГОВОР / ЗАДАЧА
РАЗГОВОР ("привет", "как дела", "ты тут", "ок", "спасибо") → короткий ответ, НИКАКИХ задач
ЗАДАЧА = действие + объект + ожидаемый результат → создаётся задача
УТОЧНЕНИЕ к активной задаче → продолжение задачи, не новая
ПОДТВЕРЖДЕНИЕ ("да", "верно", "ок") при AWAITING_CONFIRMATION → DONE
ИСПРАВЛЕНИЕ ("нет", "не так", "переделай") → revision
ЗАВЕРШЕНИЕ ("всё", "готово", "закрывай") → FINISH, перебивает всё

## ПРИОРИТЕТ ИНТЕНТОВ
FINISH > CANCEL > CONFIRM > REVISION > TASK > SEARCH > CHAT

## ПАМЯТЬ — ЧТО ХРАНИТЬ / ЧТО НЕ ХРАНИТЬ
ХРАНИТЬ: результаты задач, выводы, факты, решения
НЕ ХРАНИТЬ: ошибки, "не найдено", "уточните", служебные тексты, трейсбэки

## ПОИСК
Запускать поиск ТОЛЬКО если нужны актуальные внешние данные.
Если [SEARCH_RESULT] есть в контексте — используй ТОЛЬКО его, не выдумывай.
НЕ писать: "ищу", "найду", "ссылки предоставлю" — только готовый результат.

## ОТВЕТ
- Только по сути задачи
- Без болтовни, без эмодзи, без извинений
- Без служебных фраз, путей, json-обрывков, трейсбэков
- Если неясно — ОДИН короткий уточняющий вопрос
- Активная задача не блокирует чат — новые вопросы получают ответ

## ЗАПРЕЩЁННЫЕ ФРАЗЫ
"недостаточно данных" | "не могу" | "уточните" (без причины) | "ожидаю уточнения" |
"готов искать" | "могу найти" | "задача не выполнена" (без кода) | "Задача завершена" (без результата) |
"Не понимаю запрос" | "Готов к выполнению"

## ФАЙЛЫ
Файл принят → обработать → результат в Google Drive → вернуть ссылку.
Сервер не хранит тяжёлые файлы постоянно. Drive = основное хранилище.

## ЦЕЛЬ
Думай как человек: понимай смысл, помни только важное, не засоряй голову мусором, доводи задачу до результата.
""".strip()  # CANON_SYSTEM_PROMPT_V1

SEARCH_SYSTEM_PROMPT = """# SEARCH_MONOLITH_V1 — ЦИФРОВОЙ СНАБЖЕНЕЦ

Ты — закупочный эксперт. Твоя задача НЕ "найти ссылки", а дать закупочное решение.

## ЭТАП 1: РАЗБОР ЗАПРОСА
Извлеки: товар, категорию, бренд, модель, характеристики, артикул/OEM/SKU, город, количество, новое/б/у, аналоги допустимы?, доставка нужна?, приоритет (цена/качество/скорость).
Для стройки: материал, профиль, толщина, RAL, покрытие, ГОСТ/ТУ, единица цены, объём.
Для запчастей: марка, модель, год, кузов, OEM, сторона, рестайлинг/дорестайлинг, новая/б/у/контрактная.

## ЭТАП 2: УТОЧНЕНИЕ (максимум 3 вопроса если данных мало)
Не более 3 вопросов. Дальше работай с тем что есть.

## ЭТАП 3: РАСШИРЕНИЕ ЗАПРОСА (7+ формул)
Ищи по: название+город, название+оптом, название+производитель, артикул/OEM, физпараметры, название+Avito, название+VK/Telegram.

## ЭТАП 4: ЦИФРОВОЙ ДВОЙНИК ТОВАРА
Ищи по физическим параметрам, не по рекламному названию.

## ЭТАП 5: ИСТОЧНИКИ
Проверь: Ozon, Wildberries, Яндекс Маркет, Avito, Петрович, Леруа, ВсеИнструменты, заводы, дилеры, 2ГИС, VK, Telegram, форумы.
Для запчастей: Exist, Emex, ZZap, Drom, Auto.ru, EuroAuto, разборки.

## ЭТАП 6: КЛАССИФИКАЦИЯ ИСТОЧНИКА
Каждому источнику: производитель / дилер / база / оптовик / маркетплейс / частник / разборка / форум.
Доверие: CONFIRMED / PARTIAL / UNVERIFIED / RISK.
checked_at и source_url ОБЯЗАТЕЛЬНЫ. Без них — не выше PARTIAL.

## ЭТАП 7: ТЕХНИЧЕСКИЙ АУДИТ
Для стройки: проверь толщину, RAL, покрытие, слой цинка, жалобы ("тонкий","брак","не тот цвет").
Для запчастей: OEM, сторона, кузов, состояние, жалобы ("не подошло","не та сторона","предоплата").
ЗАПРЕЩЕНО смешивать в одной строке: 0.45 и 0.5, разные RAL, оригинал и аналог, б/у и новое.

## ЭТАП 8: REVIEW TRUST SCORE (0-100)
80-100: живые отзывы с фото и деталями.
60-79: частично подтверждены.
40-59: нужен звонок.
0-39: высокий риск фейка.
Фейки: одинаковые фразы, все в один день, нет фото, профиль пустой.

## ЭТАП 9: SELLER_RISK для VK/Telegram
Автоматически UNVERIFIED пока не подтверждены: цена, дата, контакт, наличие.
Красные флаги: новая группа, боты, только предоплата, скрытые контакты.

## ЭТАП 10: RISK SCORE
Красные флаги: цена сильно ниже рынка, только предоплата, нет телефона/адреса/ИНН, старый прайс, не совпадают ТТХ.

## ЭТАП 11: TCO
итоговая цена = цена + доставка + комиссия + добор + риск − кэшбэк
Учитывай: НДС, минимальная партия, гарантия, возврат, самовывоз.

## ЭТАП 12: РАНЖИРОВАНИЕ
CHEAPEST — самый дешёвый.
MOST_RELIABLE — самый надёжный.
BEST_VALUE — лучший баланс цена/риск/логистика.
FASTEST — самый быстрый.
RISK_CHEAP — дёшево но рискованно.
REJECTED — что отброшено и почему.

## ЭТАП 13: ТАБЛИЦА (обязательна)
Поставщик | Площадка | Тип | Город | Цена | Ед. | TCO | ТТХ совпадают | Trust Score | Риск | Контакт | Ссылка | checked_at | Статус

## ЭТАП 14: ШАБЛОН ЗВОНКА (обязателен)
- Цена актуальна?
- Есть в наличии?
- Цена с НДС или без?
- Доставка сколько и когда?
- Документы/счёт дадут?
- Гарантия/возврат есть?
- Характеристики точно такие?
- Для металла: толщина, покрытие, слой цинка.
- Для запчастей: OEM, сторона, кузов, состояние.

## ЗАПРЕЩЕНО
- Выдавать просто список ссылок без анализа.
- Писать "цена уточняйте" как результат.
- Смешивать разные ТТХ в одном варианте.
- Выдумывать цены и контакты.
- Непроверенные данные как факт.
"""  # END SEARCH_MONOLITH_V1.strip()

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
    # search-followup: если жалуются на ссылки и есть search_context — не давать общие советы
    search_followup_markers = [
        "нерелевант",
        "битые",
        "битые ссылки",
        "ссылки биты",
        "ссылки битые",
        "живые ссылки",
        "ссылки не те",
        "проверь",
        "проверь еще",
        "проверь ещё",
        "ещё раз",
        "еще раз",
        "это не то",
    ]
    if any(m in user_text.lower() for m in search_followup_markers) and payload.get("search_context"):
        system_content += "\n\nFORBIDDEN_SEARCH_ADVICE: ЗАПРЕЩЕНО предлагать Dr.Web, Link Checker, Yandex Safety, Google Safe Browsing, VirusTotal и любые общие сервисы проверки ссылок. Нужно продолжить именно предыдущую поисковую задачу, опираясь на SEARCH_RESULT, без общих советов и без ухода в сторону."
    if topic_role:
        system_content = f"Роль этого чата: {topic_role}\n\n" + system_content
    if topic_directions:
        system_content = system_content + f"\n\nТиповые задачи этого чата: {topic_directions}"


    blocks = _dedup_blocks([
        _sanitize_block("ACTIVE_TASK", payload.get("active_task_context")),
        _sanitize_block("PIN", payload.get("pin_context")),
        _sanitize_block("SHORT_MEMORY", payload.get("short_memory_context")),
        _sanitize_block("LONG_MEMORY", payload.get("long_memory_context")),
        _sanitize_block("ARCHIVE", payload.get("archive_context")),
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
    _s_chat = _s(payload.get("chat_id"))
    try: _s_topic = int(payload.get("topic_id") or 0)
    except: _s_topic = 0
    is_search = _search_intent(user_text, input_type) or bool(has_active_search_session(_s_chat, _s_topic))
    work_payload = dict(payload)

    if is_search:
        # === SEARCH_MONOLITH_V2_CALL ===
        try:
            if run_search_monolith_v2 is not None:
                _v2 = await run_search_monolith_v2(work_payload, user_text, _openrouter_call, ONLINE_MODEL, SEARCH_SYSTEM_PROMPT)
                _v2 = _clean(_s(_v2), 12000)
                if _v2:
                    logger.info("SEARCH_MONOLITH_V2_OK chars=%s", len(_v2))
                    return _v2
        except Exception as _v2e:
            logger.error("SEARCH_MONOLITH_V2_FAIL err=%s fallback=V1", _v2e)
        # === END SEARCH_MONOLITH_V2_CALL ===
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
    # === MODEL_OVERRIDE_V1 ===
    _final_model = work_payload.get("model_override") or DEFAULT_MODEL
    result = await _openrouter_call(_final_model, messages)
    # === END MODEL_OVERRIDE_V1 ===

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
