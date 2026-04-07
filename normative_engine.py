import os, re, requests
from duckduckgo_search import DDGS
from dotenv import load_dotenv

load_dotenv("/root/.areal-neva-core/.env")

OR_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OR_MODEL = os.getenv("MODEL_SEARCH", "deepseek/deepseek-chat").strip()

GOOD = ["сп", "снип", "гост", "норм", "бетон", "монолит", "отклон", "допуск"]

def extract_numbers(text):
    return re.findall(r'\d+[.,]?\d*\s?(?:мм|см|м|%)', text.lower())

def _llm(prompt):
    if not OR_KEY:
        return "НЕТ КЛЮЧА OPENROUTER_API_KEY"
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json"},
            json={"model": OR_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1},
            timeout=60
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"ОШИБКА LLM: {e}"

class NormativeEngine:
    def process(self, q):
        items = []

        # 1. Пытаемся дёрнуть поиск (мягкий запрос)
        try:
            with DDGS() as d:
                for r in d.text(q + " СП ГОСТ мм", max_results=5):
                    txt = (r.get("title","") + " " + r.get("body","")).lower()
                    if any(g in txt for g in GOOD):
                        items.append(r)
        except:
            pass

        prefix = "[DRAFT - Требует проверки специалистом]\n[НОРМАТИВ]\n\n"

        # 2. Формируем контекст
        if items:
            packed = "\n\n".join(f"{x.get('title')}\n{x.get('body')}" for x in items[:5])
        else:
            packed = "(Поисковик не вернул данных. Отвечай строго по своей встроенной базе знаний СП 70.13330.2012 и другим ГОСТам. Не выдумывай, если не помнишь точно - скажи нет данных.)"

        nums = extract_numbers(packed) if items else []
        unique_nums = list(set(nums))[:15]

        # 3. ВСЕГДА обращаемся к LLM
        prompt = f"""
Ты инженер технадзора.

Запрос пользователя: {q}

Дополнительные данные: 
{packed}

Задача:
Вытащи ТОЛЬКО реальные допуски и нормы с цифрами.
Обязательно укажи норматив (например, по СП 70.13330.2012).
Отвечай коротко, без воды.
Если точных цифр нигде нет — напиши НЕТ ДАННЫХ.
"""

        llm = _llm(prompt)

        # 4. Собираем ответ
        if unique_nums:
            llm += "\n\n🔍 Найденные сырые значения в поиске: " + ", ".join(unique_nums)

        return {
            "status": "done",
            "engine": "normative",
            "data": prefix + llm
        }
