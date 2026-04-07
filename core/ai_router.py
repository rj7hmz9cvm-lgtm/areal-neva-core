from __future__ import annotations

import asyncio
import inspect
import logging
import os
import re
import aiohttp

from core.assistant_core import get_history, save_memory, search_memory, search_memory_global
from core.db import transition_task, update_task_fields

try:
    from core.project_memory import search_project_files
except Exception:
    def search_project_files(*args, **kwargs):
        return []

try:
    from core.task_status import get_open_tasks_block
except Exception:
    def get_open_tasks_block(*args, **kwargs):
        return ""

try:
    from core.document_context import format_document_context
except Exception:
    def format_document_context(*args, **kwargs):
        return ""

logger = logging.getLogger("core.ai_router")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_OPENROUTER = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")
MODEL_ANTHROPIC = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "180"))

# HUMAN_STYLE_PATCH_V1
SYSTEM_PROMPT = (
    "Ты старший инженер AREAL NEVA. "
    "Отвечай сухо, точно и без лишнего текста. "
    "ЗАПРЕЩЕНО: приветствия, извинения, 'как ИИ', 'чем могу помочь', 'конечно', 'пожалуйста'. "
    "Сразу давай результат."
)


SEARCH_SYSTEM_PROMPT = (
    "Режим УМНЫЙ ПОИСК. "
    "Нужен готовый практический результат по ценам, поставщикам, артикулам, аналогам, наличию и позициям. "
    "Запрещено задавать лишние вопросы, писать что данных недостаточно, откладывать поиск или отправлять пользователя искать самому. "
    "Если точной цены нет, дай ориентир, диапазон или лучший найденный аналог. "
    "Формат ответа: ПОЗИЦИЯ, АНАЛОГИ, ЦЕНА ИЛИ ОРИЕНТИР, ОСНОВАНИЕ, СЛЕДУЮЩИЙ ШАГ"
)


BUILD_SYSTEM_PROMPT = (
    "Режим СТРОИТЕЛЬСТВО. "
    "Если смета или расчет — СТРОГО таблица Markdown. "
    "Формат: Наименование | Ед.изм | Кол-во | Примечание. "
    "Без текста до и после. "
    "Если нормы — СП/СНиП/ГОСТ с пунктами."
)



EMAIL_SYSTEM_PROMPT = (
    "Режим ПОЧТА. Напиши профессиональное письмо или ответ. "
    "Строгий корпоративный стиль, без воды и нейросетевых маркеров."
)

SOCIAL_SYSTEM_PROMPT = (
    "Режим СОЦСЕТИ. "
    "Сгенерируй пост, описание для Авито, VK, Telegram или YouTube. "
    "Пиши живо, продающе, без банальностей."
)

VIDEO_SYSTEM_PROMPT = (
    "Режим ВИДЕОКОНТЕНТ. "
    "Помогай с пайплайном Pika, FFmpeg, HeyGen, ElevenLabs. "
    "Выдавай точные промпты или технические команды."
)

TASK_SYSTEM_PROMPT = (
    "Режим ЗАДАЧИ "
    "Если спрашивают что сделано, что в работе или что не сделано — отвечай по статусам"
)

MEMORY_SYSTEM_PROMPT = (
    "Режим ПАМЯТЬ "
    "Твоя задача — восстановить контекст по прошлым обсуждениям "
    "Используй историю, локальную память, глобальную память проекта, найденные ссылки, артикулы, модели, прошлые решения и выводы "
    "Если есть несколько следов — собери их в один понятный ответ без повторов"
)

PATTERNS = {
    "BUILD": [
        r"\bсмет", r"\bобъем", r"\bобъём", r"\bбетон", r"\bарматур", r"\bфундамент",
        r"\bплита", r"\bмонолит", r"\bснип", r"\bгост", r"\bсп\b", r"\bсп ",
        r"\bрасчет", r"\bрасчёт", r"\bматериал", r"\bработ", r"\bтехнадзор",
        r"\bнорм", r"\bpdf\b", r"\bdwg\b", r"\bdxf\b", r"\bчертеж", r"\bчертёж",
        r"\bтаблиц", r"\bxlsx\b", r"\bcsv\b", r"\bocr\b", r"\bjpeg\b", r"\bpng\b"
    ],
    "SEARCH": [
        r"найди", r"найти", r"поиск", r"где купить",
        r"сколько стоит", r"подбери", r"артикул", r"аналог",
        r"купить", r"запчаст", r"цена", r"цены",
        r"стоимость", r"поставщик", r"поставщики",
        r"прайс", r"прайсы", r"поставка",
        r"наличие", r"материал", r"материалы"
    ],
    "TASK": [
        r"\bстатус\b", r"\bчто с задачей\b", r"\bчто по задаче\b",
        r"\bчто сделано\b", r"\bчто не сделано\b", r"\bв работе\b"
    ],
    "EMAIL": [r"\bпочт", r"\bemail", r"\bписьм", r"\bрассылк", r"\bgmail"],
    "SOCIAL": [r"\bвк\b", r"\bvk\b", r"\bтелеграм", r"\bавито", r"\bavito", r"\bпост", r"\bсоцсет", r"\byoutube"],
    "VIDEO": [r"\bpika\b", r"\bffmpeg\b", r"\bheygen\b", r"\belevenlabs\b", r"\bвидео", r"\bролик"],
    "MEMORY": [
        r"\bвспомни\b", r"\bчто обсуждали\b", r"\bнапомни\b",
        r"\bчто было\b", r"\bпомнишь\b", r"\bраньше\b",
        r"\bмесяц назад\b", r"\bдва месяца назад\b", r"\bполгода назад\b",
        r"\bпо тойоте\b", r"\bпо toyota\b", r"\bкакой артикул\b",
        r"\bкакая ссылка\b", r"\bчто считали\b", r"\bкакая была задача\b"
    ],
}

STOP_WORDS = {
    "что", "как", "для", "это", "надо", "нужно", "было", "были", "или", "еще",
    "ещё", "там", "тут", "мне", "твой", "твоя", "когда", "где", "последний",
    "последняя", "сейчас", "потом", "пожалуйста", "найди", "вспомни", "напомни",
    "обсуждали", "задача", "задачи", "сделай", "смета", "смету", "по", "мы",
    "она", "они", "его", "ее", "её"
}

def detect_intent(text: str) -> str:
    low = (text or "").lower()
    for intent, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, low):
                return intent
    return "DEFAULT"

def split_multi_intent(text: str) -> list[str]:
    parts = re.split(r"\s+(?:и|ещё|также)\s+", text or "", flags=re.IGNORECASE)
    cleaned = [p.strip() for p in parts if p.strip()]
    return cleaned[:3] if cleaned else [(text or "").strip()]

def _dedupe_keep_order(items: list[str], limit: int) -> list[str]:
    out = []
    seen = set()
    for item in items:
        key = (item or "").strip()
        if not key:
            continue
        norm = key.lower()
        if norm in seen:
            continue
        seen.add(norm)
        out.append(key)
        if len(out) >= limit:
            break
    return out

def _memory_keys(text: str, limit: int = 8) -> list[str]:
    tokens = re.findall(r"[A-Za-zА-Яа-я0-9_./\\-]+", (text or "").lower())
    keys = []
    for token in tokens:
        if len(token) < 4:
            continue
        if token in STOP_WORDS:
            continue
        keys.append(token)
    return _dedupe_keep_order(keys, limit)

async def _safe_update(task_id: str, **kwargs) -> None:
    try:
        result = update_task_fields(task_id, **kwargs)
        if inspect.isawaitable(result):
            await result
    except Exception as exc:
        logger.error("task=%s update failed: %s", task_id, exc)

async def _safe_transition(task_id: str, to_state: str) -> bool:
    try:
        result = transition_task(task_id, to_state, triggered_by="ai_router")
        if inspect.isawaitable(result):
            await result
        return True
    except Exception as exc:
        logger.error("task=%s transition→%s failed: %s", task_id, to_state, exc)
        return False

async def _call_openrouter(messages: list[dict]) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY missing")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_OPENROUTER,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 2500,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=LLM_TIMEOUT),
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"openrouter http {resp.status}: {await resp.text()}")
            data = await resp.json()
            choices = data.get("choices") or []
            if not choices:
                raise RuntimeError("openrouter empty choices")
            result = (choices[0].get("message") or {}).get("content", "").strip()
            if not result:
                raise RuntimeError("openrouter empty content")
            return result

async def _call_anthropic(messages: list[dict]) -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY missing")

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": MODEL_ANTHROPIC,
        "max_tokens": 2500,
        "system": SYSTEM_PROMPT,
        "messages": messages,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=LLM_TIMEOUT),
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"anthropic http {resp.status}: {await resp.text()}")
            data = await resp.json()
            blocks = data.get("content", [])
            result = "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
            if not result:
                raise RuntimeError("anthropic empty content")
            return result

async def _call_llm(messages: list[dict]) -> str:
    if OPENROUTER_API_KEY:
        return await _call_openrouter(messages)
    if ANTHROPIC_API_KEY:
        return await _call_anthropic(messages)
    raise RuntimeError("no LLM API key configured")

async def _collect_memory(chat_id: int, topic_id, raw_input: str, text: str) -> tuple[list[str], list[str], list[str]]:
    keys = _memory_keys(raw_input)
    local_hits: list[str] = []
    global_hits: list[str] = []

    try:
        local_hits.extend(await search_memory(chat_id, text[:120], topic_id, limit=6))
    except Exception:
        pass

    try:
        rows = await search_memory_global(text[:120], limit=6)
        for item in rows:
            txt = (item.get("text") or "").strip()
            if txt:
                global_hits.append(txt)
    except Exception:
        pass

    for key in keys:
        try:
            local_hits.extend(await search_memory(chat_id, key, topic_id, limit=4))
        except Exception:
            pass
        try:
            rows = await search_memory_global(key, limit=4)
            for item in rows:
                txt = (item.get("text") or "").strip()
                if txt:
                    global_hits.append(txt)
        except Exception:
            pass

    return keys, _dedupe_keep_order(local_hits, 10), _dedupe_keep_order(global_hits, 10)


# LLM_RETRY_HELPER_V1
async def _call_llm_with_retry(messages: list[dict]) -> str:
    last_error = None
    for attempt in range(2):
        try:
            return await asyncio.wait_for(_call_llm(messages), timeout=LLM_TIMEOUT + 5)
        except Exception as exc:
            last_error = exc
            logger.warning("llm retry %s failed: %s", attempt + 1, exc)
    logger.error("llm failed after retry: %s", last_error)
    return "Ошибка обработки запроса (таймаут LLM). Повтори ещё раз."


def _clean_result_output(text: str) -> str:
    if not text:
        return ""
    lines = text.strip().splitlines()
    bad = ("конечно", "вот", "пожалуйста", "я как", "я искусственный", "чем могу помочь")
    out = []
    for line in lines:
        l = line.strip().lower()
        if any(l.startswith(x) for x in bad):
            continue
        out.append(line.rstrip())
    return "\n".join(out).strip()


# MEMORY_PATCH_SAFE_V3
def _build_memory_context(local_hits: list, global_hits: list) -> str:
    parts = []

    for item in (local_hits or [])[:5]:
        txt = ""
        if isinstance(item, str):
            txt = item.strip()
        elif isinstance(item, dict):
            txt = str(item.get("text") or "").strip()
        else:
            txt = str(item).strip()
        if txt:
            parts.append("[LOCAL] " + txt[:300])

    for item in (global_hits or [])[:5]:
        txt = ""
        if isinstance(item, str):
            txt = item.strip()
        elif isinstance(item, dict):
            txt = str(item.get("text") or "").strip()
        else:
            txt = str(item).strip()
        if txt:
            parts.append("[GLOBAL] " + txt[:300])

    return "\n".join(parts)


# MEMORY_WRITE_PATCH_V2
def _memory_should_store(intent: str, raw_input: str, result: str) -> bool:
    text = ((raw_input or "") + "\n" + (result or "")).strip().lower()
    if len(text) < 80:
        return False
    if intent in {"BUILD", "MEMORY", "SEARCH", "TASK", "EMAIL", "SOCIAL", "VIDEO"}:
        return True
    hot = ["гост", "снип", "сп ", "смет", "объем", "объём", "артикул", "toyota", "технадзор", "бетон", "документ", "реквизит", "поставщик", "цена"]
    return any(x in text for x in hot)

def _extract_memory_items(raw_input: str, result: str, limit: int = 6) -> list[str]:
    src = ((raw_input or "").strip() + "\n" + (result or "").strip()).strip()
    if not src:
        return []

    lines = []
    for line in src.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        if len(line) < 12 or len(line) > 280:
            continue
        if set(line) <= {"-", "|", " ", "="}:
            continue
        low = line.lower()
        if low.startswith(("конечно", "пожалуйста", "вот ", "ошибка обработки запроса")):
            continue
        lines.append(line)

    seen = set()
    out = []

    priority_tokens = [
        "гост", "снип", "сп ", "смет", "объем", "объём", "артикул", "toyota",
        "технадзор", "бетон", "документ", "реквизит", "поставщик", "цена",
        "решение", "итог", "вывод", "память", "акт", "pdf", "xlsx", "docx"
    ]

    ordered = []
    for line in lines:
        low = line.lower()
        score = 1 + sum(1 for t in priority_tokens if t in low)
        ordered.append((score, line))

    ordered.sort(key=lambda x: (-x[0], x[1]))

    for _, line in ordered:
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(line)
        if len(out) >= limit:
            break

    return out


# DRIVE_SAVE_PATCH_V1
def _save_result_to_drive(chat_id: str, result: str):
    try:
        from pathlib import Path
        from datetime import datetime
        base = Path("/root/AI_ORCHESTRA/RESULTS")
        base.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{chat_id}_{ts}.md"
        fpath = base / fname
        fpath.write_text(result or "", encoding="utf-8")
    except Exception:
        pass


# FILE_SEND_PATCH_FINAL_V2
def _auto_generate_file(chat_id: str, result: str) -> str:
    try:
        from core.file_generator import save_docx
        from datetime import datetime
        from pathlib import Path

        base = Path("/root/AI_ORCHESTRA/RESULTS")
        base.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fpath = base / f"{chat_id}_{ts}.docx"

        save_docx(str(fpath), result)

        return str(fpath)
    except Exception:
        return ""

async def _send_file_safe(chat_id: int, file_path: str):
    try:
        from core.reply_sender import send_document
        if file_path:
            await send_document(chat_id, file_path)
    except Exception:
        pass


# SMART_SEARCH_PATCH_V7
def _text_from_item(item) -> str:
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        return str(item.get("text") or item.get("snippet") or item.get("path") or "").strip()
    return str(item).strip()

def _inject_search_context(messages: list[dict], raw_input: str, task: dict, files: list | None = None) -> list[dict]:
    parts = []
    query = (raw_input or "").strip()
    if query: parts.append("ЗАПРОС: " + query[:300])
    local_hits = task.get("local_hits", []) if isinstance(task, dict) else []
    global_hits = task.get("global_hits", []) if isinstance(task, dict) else []
    for item in (local_hits or [])[:4]:
        txt = _text_from_item(item)
        if txt: parts.append("ЛОКАЛЬНО: " + txt[:400])
    for item in (global_hits or [])[:4]:
        txt = _text_from_item(item)
        if txt: parts.append("ГЛОБАЛЬНО: " + txt[:400])
    for f in (files or [])[:5]:
        if not isinstance(f, dict): continue
        path = str(f.get("path") or "").strip()
        snippet = str(f.get("snippet") or "").strip()
        if path or snippet: parts.append("ФАЙЛ: " + path[:220] + ("\n" + snippet[:300] if snippet else ""))
    
    if parts:
        search_msg = {"role": "system", "content": "КОНТЕКСТ ДЛЯ УМНОГО ПОИСКА:\n" + "\n---\n".join(parts)}
        # Вставляем сообщение перед последним (перед user), если оно есть
        if messages and messages[-1].get("role") == "user":
            return messages[:-1] + [search_msg] + messages[-1:]
        return messages + [search_msg]
    return messages

async def process_ai_task(task: dict) -> None:
    task_id = task["id"]
    chat_id = int(task.get("chat_id") or 0)
    topic_id = task.get("topic_id")
    raw_input = (task.get("raw_input") or "").strip()

    if not raw_input:
        await _safe_update(task_id, error_message="empty input")
        await _safe_transition(task_id, "FAILED")
        return

    await _safe_transition(task_id, "IN_PROGRESS")

    try:
        subqueries = split_multi_intent(raw_input)
        text = subqueries[0]
        intent = detect_intent(text)

        history_limit = 40 if intent in {"MEMORY", "BUILD"} else 20
        history = await get_history(chat_id, topic_id, limit=history_limit)

        keys, local_hits, global_hits = await _collect_memory(chat_id, topic_id, raw_input, text)

        open_tasks = await asyncio.to_thread(get_open_tasks_block, chat_id)
        files = await asyncio.to_thread(search_project_files, text, 5)

        doc_context = ""
        file_paths = re.findall(r'(?:/|~/)[\w\./\-]+\.[a-zA-Z0-9]+', raw_input)
        if file_paths:
            doc_context = await asyncio.to_thread(format_document_context, file_paths[0])

        _local_hits = task.get("local_hits", [])
        _global_hits = task.get("global_hits", [])
        mem_ctx = _build_memory_context(_local_hits, _global_hits)

        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

        if mem_ctx:
            messages.append({"role": "system", "content": "ИСТОРИЯ И ПАМЯТЬ:\n" + mem_ctx})

        if intent == "BUILD":
            messages.append({"role": "system", "content": BUILD_SYSTEM_PROMPT})
        elif intent == "SEARCH":
            messages.append({"role": "system", "content": SEARCH_SYSTEM_PROMPT})
        elif intent == "EMAIL":
            messages.append({"role": "system", "content": EMAIL_SYSTEM_PROMPT})
        elif intent == "SOCIAL":
            messages.append({"role": "system", "content": SOCIAL_SYSTEM_PROMPT})
        elif intent == "VIDEO":
            messages.append({"role": "system", "content": VIDEO_SYSTEM_PROMPT})
        elif intent == "TASK":
            messages.append({"role": "system", "content": TASK_SYSTEM_PROMPT})
        elif intent == "MEMORY":
            messages.append({"role": "system", "content": MEMORY_SYSTEM_PROMPT})

        if keys:
            messages.append({"role": "system", "content": "КЛЮЧИ ПАМЯТИ: " + ", ".join(keys)})

        for item in local_hits:
            messages.append({"role": "system", "content": f"[Локальная память] {item[:700]}"})

        for item in global_hits:
            messages.append({"role": "system", "content": f"[Глобальная память] {item[:500]}"})

        if open_tasks and intent in {"TASK", "DEFAULT", "BUILD"}:
            messages.append({"role": "system", "content": open_tasks})

        if doc_context:
            messages.append({"role": "system", "content": f"ОБНАРУЖЕН ДОКУМЕНТ В ЗАПРОСЕ:\n{doc_context}"})

        if files and intent in {"SEARCH", "BUILD", "DEFAULT", "MEMORY"}:
            lines = ["ФАЙЛЫ ПРОЕКТА:"]
            for f in files:
                lines.append(f"- {f.get('path','')}")
                snippet = (f.get("snippet") or "").strip()
                if snippet:
                    lines.append(snippet[:200])
            messages.append({"role": "system", "content": "\n".join(lines)})

        if intent == "SEARCH":
            messages = _inject_search_context(messages, raw_input, task, files)

        messages.extend(history)
        messages.append({"role": "user", "content": text})

        result = await _call_llm_with_retry(messages)

        await save_memory(chat_id, raw_input, role="user", topic_id=topic_id)
        await save_memory(chat_id, result, role="assistant", topic_id=topic_id)

        # AUTO-MEMORY EXTRACTION
        _m_intent = intent if "intent" in locals() else task.get("intent", "")
        _m_raw_input = raw_input if "raw_input" in locals() else task.get("text", "")
        _m_chat_id = chat_id if "chat_id" in locals() else task.get("chat_id")
        _m_topic_id = topic_id if "topic_id" in locals() else task.get("topic_id")
        if _memory_should_store(_m_intent, _m_raw_input, result):
            for item in _extract_memory_items(_m_raw_input, result):
                await save_memory(_m_chat_id, "[MEMORY] " + item, role="system", topic_id=_m_topic_id)
        result = _clean_result_output(result)
        # GENERATE + SAVE FILE
        try:
            _cid = task.get('chat_id','unknown')
            _file = _auto_generate_file(str(_cid), result)
        except Exception:
            _file = ''

        # SAVE RESULT (DB)
        await _safe_update(task_id, result=result)

        # SEND FILE TO TELEGRAM
        try:
            if _file:
                await _send_file_safe(int(task.get('chat_id',0)), _file)
        except Exception:
            pass

        try:
            _cid = task.get('chat_id', 'unknown')
            _save_result_to_drive(str(_cid), result)
        except Exception:
            pass
        await _safe_transition(task_id, "RESULT_READY")

        logger.info("task=%s ai done intent=%s keys=%s", task_id, intent, ",".join(keys[:4]))

    except Exception as exc:
        logger.exception("AI error task=%s", task_id)
        await _safe_update(task_id, error_message=str(exc))
        await _safe_transition(task_id, "FAILED")
