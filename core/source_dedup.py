# === SOURCE_DEDUPLICATION_V1 ===
import hashlib, logging
logger = logging.getLogger(__name__)

def _sig(item: dict) -> str:
    key = f"{item.get('url','')}|{item.get('supplier','')}|{item.get('price','')}"
    return hashlib.md5(key.encode()).hexdigest()

def dedup_offers(offers: list) -> list:
    seen = set()
    result = []
    for o in offers:
        s = _sig(o)
        if s not in seen:
            seen.add(s)
            result.append(o)
    return result

def dedup_search_results(results: list, key_field: str = "url") -> list:
    seen = set()
    clean = []
    for r in results:
        k = str(r.get(key_field) or r)[:200]
        if k not in seen:
            seen.add(k)
            clean.append(r)
    return clean

# TIME_RELEVANCE — фильтр по свежести
def filter_by_time_relevance(items: list, date_field: str = "date", max_days: int = 30) -> list:
    from datetime import datetime, timezone, timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
    result = []
    for item in items:
        raw_date = item.get(date_field)
        if not raw_date:
            result.append(item)
            continue
        try:
            ts = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
            if ts >= cutoff:
                result.append(item)
        except Exception:
            result.append(item)
    return result

# REGION_PRIORITY — приоритет по региону
_PRIORITY_REGIONS = ["санкт-петербург", "спб", "москва", "мск", "ленинградская"]

def sort_by_region(offers: list, preferred_regions: list = None) -> list:
    regions = [r.lower() for r in (preferred_regions or _PRIORITY_REGIONS)]
    def region_score(o):
        city = str(o.get("city", "")).lower()
        for i, r in enumerate(regions):
            if r in city:
                return i
        return len(regions)
    return sorted(offers, key=region_score)
# === END SOURCE_DEDUPLICATION_V1 ===
