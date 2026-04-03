import os, requests, time
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from cachetools import TTLCache

load_dotenv("/root/.areal-neva-core/.env")

OR_KEY = os.getenv("OPENROUTER_API_KEY","").strip()
MODEL = os.getenv("MODEL_SEARCH", "deepseek/deepseek-chat").strip()

# КЭШ: 100 запросов, 10 минут
CACHE = TTLCache(maxsize=100, ttl=600)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9"
}

def _llm(prompt):
    if not OR_KEY:
        return "[DRAFT - Требует проверки специалистом]\nНет ключа"

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OR_KEY}", "Content-Type":"application/json"},
            json={"model": MODEL, "messages":[{"role":"user","content":prompt}], "temperature":0.1},
            timeout=40
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[DRAFT - Требует проверки специалистом]\nОшибка LLM: {e}"

def search_ddg(q):
    out = []
    try:
        with DDGS() as d:
            for r in d.text(q, max_results=5):
                out.append(r.get("title","") + " " + r.get("body",""))
    except:
        pass
    return out

def search_avito(q):
    out = []
    try:
        html = requests.get(f"https://www.avito.ru/all?q={q}", headers=HEADERS, timeout=8).text
        soup = BeautifulSoup(html, "lxml")
        for item in soup.select("div[data-marker=item]")[:5]:
            out.append(item.get_text(" ", strip=True))
    except:
        pass
    return out

def search_ozon(q):
    out = []
    try:
        html = requests.get(f"https://www.ozon.ru/search/?text={q}", headers=HEADERS, timeout=8).text
        soup = BeautifulSoup(html, "lxml")
        for item in soup.select("div")[:10]:
            t = item.get_text(" ", strip=True)
            if "₽" in t:
                out.append(t)
    except:
        pass
    return out[:5]

class WebEngine:

    def search(self, q):
        q = q.strip().lower()

        # ===== CACHE HIT =====
        if q in CACHE:
            return {
                "status": "done",
                "engine": "web",
                "data": CACHE[q] + "\n\n⚡ CACHE"
            }

        ddg = search_ddg(q)
        avito = search_avito(q)
        ozon = search_ozon(q)

        packed = "\n\n".join([
            "DDG:\n" + "\n".join(ddg),
            "AVITO:\n" + "\n".join(avito),
            "OZON:\n" + "\n".join(ozon),
        ])[:3000]

        prompt = f"""
Ты технадзор.

Запрос: {q}

Данные:
{packed}

Дай:
- реальные цены
- диапазон
- кратко

Ответ начинай строго с:
[DRAFT - Требует проверки специалистом]
"""

        result = _llm(prompt)

        # ===== SAVE CACHE =====
        CACHE[q] = result

        return {
            "status": "done",
            "engine": "web",
            "data": result
        }
