import os, logging

logger = logging.getLogger("web_engine")

async def web_search(query: str) -> str:
    try:
        import aiohttp
        async with aiohttp.ClientSession() as s:
            async with s.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                timeout=15
            ) as resp:
                data = await resp.json()
                if data.get("AbstractText"):
                    return data["AbstractText"][:2000]
                elif data.get("RelatedTopics"):
                    results = []
                    for t in data["RelatedTopics"][:3]:
                        if isinstance(t, dict) and t.get("Text"):
                            results.append(t["Text"])
                    if results:
                        return "\n".join(results)[:2000]
    except Exception as e:
        logger.error("WEB_SEARCH_FAIL: %s", e)
    return "Не найдено"
