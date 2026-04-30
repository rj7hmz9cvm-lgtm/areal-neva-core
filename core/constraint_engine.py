# === CONSTRAINT_ENGINE_V1 ===
import re, logging
logger = logging.getLogger(__name__)

# MULTI_OFFER_CONSISTENCY — все офферы в одном формате
def normalize_offer(offer: dict) -> dict:
    return {
        "supplier":  str(offer.get("supplier") or offer.get("поставщик") or "UNKNOWN"),
        "platform":  str(offer.get("platform") or offer.get("площадка") or ""),
        "seller_type": str(offer.get("seller_type") or "UNKNOWN"),
        "city":      str(offer.get("city") or offer.get("город") or ""),
        "price":     _to_float(offer.get("price") or offer.get("цена") or 0),
        "unit":      str(offer.get("unit") or offer.get("ед") or ""),
        "stock":     str(offer.get("stock") or offer.get("наличие") or "UNKNOWN"),
        "delivery":  str(offer.get("delivery") or offer.get("доставка") or "UNKNOWN"),
        "tco":       _to_float(offer.get("tco") or 0),
        "risk":      str(offer.get("risk") or "UNVERIFIED"),
        "contact":   str(offer.get("contact") or offer.get("контакт") or ""),
        "url":       str(offer.get("url") or offer.get("ссылка") or ""),
        "verified":  bool(offer.get("verified") or False),
    }

def _to_float(v) -> float:
    try:
        return float(re.sub(r"[^\d.]", "", str(v)) or 0)
    except Exception:
        return 0.0

def validate_offer(offer: dict) -> dict:
    """Проверить оффер на минимальное качество"""
    issues = []
    if not offer.get("price") or offer["price"] <= 0:
        issues.append("NO_PRICE")
    if not offer.get("contact") and not offer.get("url"):
        issues.append("NO_CONTACT")
    if offer.get("price") and offer["price"] < 10:
        issues.append("PRICE_TOO_LOW")
    return {"ok": len(issues) == 0, "issues": issues}

def rank_offers(offers: list) -> list:
    """ResultRanker — сортировка по TCO или цене"""
    def score(o):
        tco = o.get("tco") or o.get("price") or 999999
        risk_penalty = {"CONFIRMED": 0, "PARTIAL": 5, "UNVERIFIED": 15, "RISK": 30}.get(o.get("risk","UNVERIFIED"), 15)
        return tco + risk_penalty * 100
    return sorted(offers, key=score)

# CONSTRAINT_ENGINE — ограничения на поиск
_CONSTRAINTS = {
    "price_min": 0,
    "price_max": 999_999_999,
    "region": [],
    "exclude_keywords": ["1 руб", "договорная", "под заказ в пути"],
    "require_contact": False,
    "require_stock": False,
}

def apply_constraints(offers: list, constraints: dict = None) -> list:
    c = {**_CONSTRAINTS, **(constraints or {})}
    result = []
    for o in offers:
        price = _to_float(o.get("price") or 0)
        if price and (price < c["price_min"] or price > c["price_max"]):
            continue
        text = str(o).lower()
        if any(ex.lower() in text for ex in c["exclude_keywords"]):
            continue
        if c["require_contact"] and not o.get("contact"):
            continue
        result.append(o)
    return result
# === END CONSTRAINT_ENGINE_V1 ===
