from __future__ import annotations
import asyncio, logging, os, aiohttp, json
logger = logging.getLogger(__name__)
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_KEY: raise RuntimeError("OPENROUTER_API_KEY missing")
MEMORY_URL = "http://127.0.0.1:8091/memory"
MEMORY_TOKEN = os.getenv("MEMORY_API_TOKEN", "mem-eaf522f4934508438010fb3442a9eebd")

async def save_memory(chat_id, key, value):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                MEMORY_URL,
                headers={"Authorization": f"Bearer {MEMORY_TOKEN}"},
                json={"chat_id": str(chat_id), "key": key, "value": str(value)}
            ) as r:
                return r.status in (200, 201)
    except Exception as e:
        logger.error(f"memory save failed: {e}")
        return False

async def get_memory(chat_id):
    async with aiohttp.ClientSession() as s:
        try:
            async with s.get(f"{MEMORY_URL}?chat_id={chat_id}&limit=10", headers={"Authorization": f"Bearer {MEMORY_TOKEN}"}, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200: return await r.json()
        except: pass
    return []

async def process_ai_task(task: dict) -> str:
    chat_id = str(task.get("chat_id"))
    prompt = task.get("raw_input", "")
    await save_memory(chat_id, "user_input", prompt)
    memories = await get_memory(chat_id)
    context = "\n".join([m.get("value", "") for m in memories])
    system_prompt = "Отвечай только на русском языке. Коротко, по делу, без приветствий, без английского языка."
    full_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nUser: {prompt}"
    async with aiohttp.ClientSession() as s:
        async with s.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {OPENROUTER_KEY}"}, json={"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": full_prompt}]}, timeout=aiohttp.ClientTimeout(total=300)) as r:
            resp = await r.json()
            if r.status != 200: return f"LLM ERROR HTTP {r.status}: {resp}"
            if "error" in resp: return f"LLM ERROR: {resp[error]}"
            return resp.get("choices", [{}])[0].get("message", {}).get("content", "ERROR")
