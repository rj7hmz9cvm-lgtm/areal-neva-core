# === NORMATIVE_DB_V1 ===
import os, logging, asyncio, aiohttp, json
logger = logging.getLogger(__name__)
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

async def get_norm(norm_id: str, context: str = "") -> dict:
    result = {"norm_id": norm_id, "title": "", "requirement": "норма не подтверждена",
              "source": "perplexity", "verified": False}
    if not OPENROUTER_KEY:
        result["error"] = "NO_API_KEY"; return result
    try:
        prompt = (f"Найди требование нормы {norm_id} применительно к: {context}. "
                  f"Только точная цитата и номер пункта. Без интерпретаций.")
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}",
                         "Content-Type": "application/json"},
                json={"model": "perplexity/sonar",
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                data = await r.json()
                text = data["choices"][0]["message"]["content"].strip()
                if text and len(text) > 10 and "не найд" not in text.lower():
                    result["requirement"] = text
                    result["verified"] = True
    except Exception as e:
        logger.warning("NORMATIVE_DB_V1 err=%s", e)
        result["error"] = str(e)
    return result

async def search_norms(defect_description: str, section: str = "") -> list:
    # === NORMATIVE_SEARCH_V1 ===
    norms_map = {
        "кровля": ["СП 17.13330.2017", "СНиП II-26-76"],
        "фасад": ["СП 293.1325800.2017", "ГОСТ 31251-2008"],
        "фундамент": ["СП 22.13330.2016", "СП 50-101-2004"],
        "несущие": ["СП 20.13330.2017", "ГОСТ 5781-82"],
        "перекрытие": ["СП 20.13330.2017", "СП 63.13330.2018"],
    }
    sec = section.lower() if section else defect_description.lower()
    candidates = []
    for key, norms in norms_map.items():
        if key in sec:
            candidates = norms[:2]; break
    if not candidates:
        candidates = ["СП 20.13330.2017"]
    results = []
    for n in candidates[:3]:
        r = await get_norm(n, defect_description)
        results.append(r)
    return results
# === END NORMATIVE_DB_V1 ===
