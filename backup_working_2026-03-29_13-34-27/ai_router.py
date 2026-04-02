from __future__ import annotations

import logging
import os
import aiohttp

from core.db_adapter import safe_transition, safe_update, get_history

logger = logging.getLogger("core.ai_router")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-chat"

SYSTEM_PROMPT = (
    "Ты AI-ассистент строительного оркестра AREAL NEVA. "
    "Отвечай кратко и конкретно на русском языке. "
    "При строительных и технических вопросах давай точный ответ. "
    "Никогда не говори 'я не знаю' — всегда давай полезный ответ."
)


async def process_ai_task(task: dict) -> None:
    task_id = task["id"]
    text = (task.get("raw_input") or "").strip()
    chat_id = int(task.get("chat_id") or 0)

    if not text:
        await safe_update(task_id, error_message="empty input after STT")
        await safe_transition(task_id, "FAILED", "ai_router")
        return

    if not OPENROUTER_API_KEY:
        await safe_update(task_id, error_message="OPENROUTER_API_KEY missing")
        await safe_transition(task_id, "FAILED", "ai_router")
        return

    history = await get_history(chat_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": text})

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                BASE_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL,
                    "messages": messages,
                    "temperature": 0.4,
                    "max_tokens": 1500,
                },
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise RuntimeError(f"http {resp.status}: {body[:200]}")
                data = await resp.json()
                choices = data.get("choices")
                if not choices:
                    raise RuntimeError("empty choices in response")
                result = choices[0]["message"]["content"].strip()

    except Exception as e:
        logger.exception("LLM error task=%s", task_id)
        await safe_update(task_id, error_message=str(e))
        await safe_transition(task_id, "FAILED", "ai_router")
        return

    await safe_update(task_id, result=result)
    await safe_transition(task_id, "RESULT_READY", "ai_router")
    logger.info("RESULT_READY task=%s", task_id)
