from duckduckgo_search import DDGS

def search_web(query, limit=8):
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=limit):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "body": r.get("body", "")
                })
    except Exception as e:
        return [{"title": "SEARCH_ERROR", "url": "", "body": str(e)}]
    return results
