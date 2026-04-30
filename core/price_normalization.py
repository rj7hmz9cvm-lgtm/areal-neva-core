# === PRICE_NORMALIZATION_V1 ===
import re, logging
logger = logging.getLogger(__name__)

_UNITS = {
    "м2": "м²", "м кв": "м²", "кв м": "м²", "кв.м": "м²",
    "м3": "м³", "куб м": "м³", "м3": "м³",
    "пм": "п.м", "пог м": "п.м", "погонный метр": "п.м",
    "шт": "шт.", "штук": "шт.", "штука": "шт.",
    "т ": "т.", "тонн": "т.", "кг": "кг",
}

def normalize_unit(unit: str) -> str:
    low = unit.lower().strip()
    for k, v in _UNITS.items():
        if k in low:
            return v
    return unit.strip()

def extract_price(text: str) -> list:
    """Извлечь все цены из текста"""
    pattern = r"(\d[\d\s]*[\d])\s*(руб|₽|р\.|рублей|руб\.)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    prices = []
    for m in matches:
        raw = re.sub(r"\s", "", m[0])
        try:
            prices.append(int(raw))
        except Exception:
            pass
    return prices

def normalize_price_text(text: str) -> str:
    """1000000 → 1 000 000 руб."""
    def fmt(m):
        try:
            n = int(re.sub(r"\s", "", m.group(1)))
            return f"{n:,}".replace(",", " ") + " руб."
        except Exception:
            return m.group(0)
    return re.sub(r"(\d[\d\s]{2,})\s*(руб|₽|р\.|рублей)", fmt, text, flags=re.IGNORECASE)

def price_aging_warning(price_date: str, price: float) -> float:
    """PRICE_AGING: +5-10% если прайс старше 48ч (канон §1.6)"""
    if not price_date:
        return price
    try:
        from datetime import datetime, timezone
        ts = datetime.fromisoformat(price_date.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        if age_h > 48:
            return round(price * 1.075, 2)  # +7.5% среднее
    except Exception:
        pass
    return price
# === END PRICE_NORMALIZATION_V1 ===
