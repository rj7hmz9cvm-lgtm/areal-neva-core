try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

def need_web_search(text: str) -> bool:
    q = (text or "").lower()
    keys = [
        "цена", "стоимость", "сколько стоит", "найди", "поиск", "найти", "поищи",
        "курс", "сейчас", "последние", "свежие", "новости", "где купить", "что по"
    ]
    return any(k in q for k in keys)

def web_search(query: str, limit: int = 5) -> str:
    if not DDGS:
        return ""
    rows = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=limit):
                title = r.get("title", "").strip()
                href = r.get("href", "").strip()
                body = r.get("body", "").strip()
                if title or href:
                    rows.append(f"{title}\n{body}\n{href}")
    except Exception:
        return ""
    return "\n\n".join(rows[:limit])
