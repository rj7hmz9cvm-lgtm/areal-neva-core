import logging

logger = logging.getLogger("web_engine")

async def web_search(query: str) -> str:
    # Search handled by ONLINE_MODEL (perplexity/sonar) in ai_router.py
    logger.warning("web_search_stub called query=%s", (query or "")[:100])
    return ""
