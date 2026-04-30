import asyncio, logging, os, re
from typing import Optional
logger = logging.getLogger(__name__)

TOPIC_3008 = 3008
TIMEOUT = 90

_WRITE_CODE = ["напиши код", "написать код"]
_VERIFY_CODE = ["проверь код", "проверить код", "верификация"]
_CODE_BLOCK = re.compile(r"```[\w]*\n.*?```", re.DOTALL)

def is_topic_3008(topic_id):
    return int(topic_id or 0) == TOPIC_3008

def detect_command(text):
    low = text.lower()
    if any(t in low for t in _WRITE_CODE):
        return "write"
    if any(t in low for t in _VERIFY_CODE):
        return "verify"
    if _CODE_BLOCK.search(text):
        return "verify"
    return "none"

def extract_code(text):
    m = _CODE_BLOCK.search(text)
    if m:
        raw = m.group(0)
        lines = raw.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines)
    return text

MODEL_REGISTRY = {
    "deepseek": {"name":"DeepSeek","emoji":"🧠","role":"архитектура","api":"openrouter","model":"deepseek/deepseek-chat","env_key":"OPENROUTER_API_KEY","available":True},
    "claude":   {"name":"Claude",  "emoji":"👤","role":"логика ТЗ", "api":"anthropic","model":"claude-opus-4-6","env_key":"ANTHROPIC_API_KEY","available":True},
    "gpt":      {"name":"ChatGPT", "emoji":"🤖","role":"патчи",    "api":"openai",  "model":"gpt-4o","env_key":"OPENAI_API_KEY","available":True},
    "gemini":   {"name":"Gemini",  "emoji":"🔒","role":"безопасность","api":"gemini","model":"gemini-2.0-flash","env_key":"GOOGLE_API_KEY","available":False},
    "grok":     {"name":"Grok",    "emoji":"⚡","role":"архитектура","api":"xai",   "model":"grok-3","env_key":"XAI_API_KEY","available":False},
}

async def _call_openrouter(model_id, prompt, api_key, base_url):
    import aiohttp
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model_id, "messages": [{"role":"user","content":prompt}], "max_tokens":1000}
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            d = await r.json()
            return d["choices"][0]["message"]["content"]

async def _call_anthropic(model_id, prompt, api_key):
    import aiohttp
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    payload = {"model": model_id, "max_tokens":1000, "messages":[{"role":"user","content":prompt}]}
    async with aiohttp.ClientSession() as s:
        async with s.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            d = await r.json()
            return d["content"][0]["text"]

async def _call_openai(model_id, prompt, api_key):
    import aiohttp
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model_id, "messages":[{"role":"user","content":prompt}], "max_tokens":1000}
    async with aiohttp.ClientSession() as s:
        async with s.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            d = await r.json()
            return d["choices"][0]["message"]["content"]

async def _verify_one(key, meta, prompt):
    api_key = os.getenv(meta["env_key"], "")
    if not api_key or not meta["available"]:
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":"недоступна","ok":None}
    try:
        base_url = os.getenv("OPENROUTER_BASE_URL","https://openrouter.ai/api/v1")
        if meta["api"] == "openrouter":
            text = await _call_openrouter(meta["model"], prompt, api_key, base_url)
        elif meta["api"] == "anthropic":
            text = await _call_anthropic(meta["model"], prompt, api_key)
        elif meta["api"] == "openai":
            text = await _call_openai(meta["model"], prompt, api_key)
        else:
            return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":"API не реализован","ok":None}
        text_clean = text.strip()[:800]
        low = text_clean.lower()
        ok = not any(w in low for w in ["ошибк","проблем","уязвимост","небезопасн","запрещ"])
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"✅" if ok else "❌","text":text_clean,"ok":ok}
    except asyncio.TimeoutError:
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":"таймаут 90с","ok":None}
    except Exception as e:
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":str(e)[:200],"ok":None}

async def verify_code(code, context=""):
    prompt = f"Проверь код на логику, архитектуру, безопасность.\n\nКонтекст: AREAL-NEVA ORCHESTRA\n{context[:300]}\n\nКод:\n```\n{code[:3000]}\n```\n\nДай краткий вердикт (2-3 предложения)."
    available = {k:v for k,v in MODEL_REGISTRY.items()}
    tasks = [_verify_one(k,v,prompt) for k,v in available.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    lines = ["=== ВЕРИФИКАЦИЯ КОДА ===\n"]
    approved = 0
    critical = False
    for r in results:
        if isinstance(r, Exception):
            continue
        lines.append(f"{r['emoji']} {r['name'].upper()} ({r['role']}): {r['result']}")
        lines.append(r['text'])
        lines.append("")
        if r['ok'] is True:
            approved += 1
        if r['key'] == 'gemini' and r['result'] == '❌':
            critical = True
    total = sum(1 for v in available.values() if v["available"] and os.getenv(v["env_key"]))
    lines.append("=== ОБЩАЯ КАРТИНА ===")
    lines.append(f"Одобрено {approved} из {max(total,1)} доступных моделей.")
    if critical:
        lines.append("КРИТИЧЕСКОЕ ЗАМЕЧАНИЕ: Gemini выявил проблемы безопасности!")
    lines.append("\nРешение принимает пользователь.")
    return "\n".join(lines)

async def generate_code(description, context=""):
    api_key = os.getenv("OPENROUTER_API_KEY","")
    base_url = os.getenv("OPENROUTER_BASE_URL","https://openrouter.ai/api/v1")
    prompt = f"Напиши код. Только код без лишних объяснений.\n\nСистема: AREAL-NEVA ORCHESTRA (Python 3.12)\n{('Контекст: ' + context[:300]) if context else ''}\n\nЗадача: {description}"
    try:
        return (await _call_openrouter("deepseek/deepseek-chat", prompt, api_key, base_url)).strip()
    except Exception as e:
        return f"Ошибка генерации: {e}"
