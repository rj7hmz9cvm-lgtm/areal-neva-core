import os
import json
import aiohttp
import logging
from core.stt_engine import transcribe_voice
from core.web_engine import need_web_search, web_search

logger = logging.getLogger(__name__)

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat").strip()
MEMORY_URL = "http://127.0.0.1:8091/memory"
MEMORY_TOKEN = os.getenv("MEMORY_API_TOKEN", "").strip()
SNAPSHOT_CHAT_ID = os.getenv("ORCHESTRA_SNAPSHOT_CHAT_ID", "AREAL_NEVA_ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026_04_11").strip()

if not OPENROUTER_KEY:
    raise RuntimeError("OPENROUTER_API_KEY missing")

async def save_memory(chat_id: str, key: str, value: str) -> bool:
    try:
        async with aiohttp.ClientSession() as s:
            r = await s.post(
                MEMORY_URL,
                headers={"Authorization": f"Bearer {MEMORY_TOKEN}"},
                json={"chat_id": str(chat_id), "key": str(key), "value": str(value)},
                timeout=aiohttp.ClientTimeout(total=20),
            )
            return r.status in (200, 201)
    except Exception as e:
        logger.error("memory_save failed chat_id=%s key=%s err=%s", chat_id, key, e)
        return False

async def get_memory(chat_id: str, limit: int = 12) -> list:
    try:
        async with aiohttp.ClientSession() as s:
            r = await s.get(
                f"{MEMORY_URL}?chat_id={chat_id}&limit={limit}",
                headers={"Authorization": f"Bearer {MEMORY_TOKEN}"},
                timeout=aiohttp.ClientTimeout(total=20),
            )
            if r.status == 200:
                return await r.json()
    except Exception as e:
        logger.error("memory_get failed chat_id=%s err=%s", chat_id, e)
    return []

def _pick_short_memory(rows: list) -> str:
    out = []
    for row in rows:
        key = str(row.get("key", "")).strip()
        val = str(row.get("value", "")).strip()
        if not val:
            continue
        if key in {"user_input", "assistant_output", "task_summary", "fact", "decision", "project_context", "transcript"}:
            out.append(f"[{key}] {val[:1500]}")
    return "\n".join(out[:16])

def _pick_long_memory(rows: list) -> str:
    for row in rows:
        if str(row.get("key", "")).strip() == "full_export":
            return str(row.get("value", "")).strip()[:14000]
    return ""

async def _call_llm(user_text: str, short_mem: str, long_mem: str, web_data: str) -> str:
    system = (
        "Ты — рабочий оркестр для Ильи\n"
        "Отвечай только по-русски\n"
        "Без приветствий, без бытовой болтовни, без встречных вопросов ради вежливости\n"
        "Нужен результат по делу\n"
        "Если запрос технический — отвечай как инженер и оператор системы\n"
        "Используй память только как контекст\n"
        "Если данных не хватает — прямо скажи, чего не хватает\n"
    )

    payload = {
        "model": OPENROUTER_MODEL,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content":
                f"ДОЛГОСРОЧНЫЙ КОНТЕКСТ\n{long_mem}\n\n"
                f"КРАТКОСРОЧНЫЙ КОНТЕКСТ\n{short_mem}\n\n"
                f"ИНТЕРНЕТ-ПОИСК\n{web_data}\n\n"
                f"ЗАПРОС\n{user_text}"
            },
        ],
    }

    async with aiohttp.ClientSession() as s:
        r = await s.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=aiohttp.ClientTimeout(total=300),
        )
        body = await r.text()
        if r.status != 200:
            raise RuntimeError(f"LLM HTTP {r.status}: {body[:500]}")
        try:
            js = json.loads(body)
        except Exception:
            raise RuntimeError(f"LLM bad json: {body[:500]}")
        if js.get("error"):
            raise RuntimeError(f"LLM ERROR: {js['error']}")
        result = ((js.get("choices") or [{}])[0].get("message") or {}).get("content", "")
        result = (result or "").strip()
        if not result:
            raise RuntimeError("LLM returned empty content")
        return result

async def process_ai_task(task: dict) -> str:
    chat_id = str(task.get("chat_id"))
    input_type = str(task.get("input_type", "text"))
    raw_input = str(task.get("raw_input", "") or "").strip()

    if input_type == "voice":
        transcript = await transcribe_voice(raw_input)
        await save_memory(chat_id, "transcript", transcript)
        user_text = transcript
    else:
        user_text = raw_input

    if not user_text:
        return "Ошибка: пустой input"

    short_rows = await get_memory(chat_id, limit=12)
    long_rows = await get_memory(SNAPSHOT_CHAT_ID, limit=4)

    short_mem = _pick_short_memory(short_rows)
    long_mem = _pick_long_memory(long_rows)

    web_data = web_search(user_text, limit=5) if need_web_search(user_text) else ""

    await save_memory(chat_id, "user_input", user_text[:4000])

    result = await _call_llm(user_text[:12000], short_mem, long_mem, web_data[:6000])

    await save_memory(chat_id, "assistant_output", result[:4000])
    await save_memory(chat_id, "task_summary", f"{input_type}: {user_text[:400]} => {result[:700]}")

    return result
