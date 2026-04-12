import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

def need_web_search(text: str) -> bool:
    if not text:
        return False
    keywords = ["цена", "стоимость", "сколько стоит", "найди", "поиск", "погода", "курс", "новости", "купить", "продажа", "заказать"]
    return any(k in text.lower() for k in keywords)

def is_commercial_query(text: str) -> bool:
    if not text:
        return False
    commercial = [
        "купить", "цена", "стоимость", "сколько стоит", "продажа", "в наличии", "заказать",
        "авито", "озон", "вайлдберриз", "wildberries", "wb", "avito", "ozon",
        "auto.ru", "auto ru", "дром", "drom"
    ]
    return any(k in text.lower() for k in commercial)

def commercial_search(query: str) -> list:
    sites = ["site:avito.ru", "site:ozon.ru", "site:wildberries.ru", "site:auto.ru", "site:drom.ru"]
    results = []
    seen = set()
    with DDGS() as ddgs:
        for site in sites:
            try:
                for r in ddgs.text(f"{query} {site}", max_results=2):
                    href = r.get("href", "")
                    if href and href not in seen:
                        seen.add(href)
                        results.append({"title": r.get("title", ""), "body": r.get("body", ""), "href": href})
                    if len(results) >= 7:
                        break
            except:
                pass
            if len(results) >= 7:
                break
    return results[:7]

def info_search(query: str, limit: int = 5) -> list:
    results = []
    with DDGS() as ddgs:
        try:
            for r in ddgs.text(query, max_results=limit):
                results.append({"title": r.get("title", ""), "body": r.get("body", ""), "href": r.get("href", "")})
        except:
            pass
    return results

def format_results(results: list) -> str:
    if not results:
        return ""
    lines = []
    for r in results:
        title = r.get("title", "")[:100]
        body = r.get("body", "")[:200]
        href = r.get("href", "")
        if title and href:
            lines.append(f"{title} — {body}. Источник: {href}")
    return "\n\n".join(lines)[:1500]

def web_search(query: str, limit: int = 5) -> str:
    if not query:
        return ""
    try:
        if is_commercial_query(query):
            results = commercial_search(query)
            if not results:
                results = info_search(query, limit)
        else:
            results = info_search(query, limit)
        return format_results(results)
    except Exception as e:
        logger.error(f"web_search failed: {e}")
        return ""
