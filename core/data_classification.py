# === DATA_CLASSIFICATION_V1 ===
# Канон §28.3 — File Routing Canon
import re, logging
logger = logging.getLogger(__name__)

_DOMAIN_MAP = {
    "STROYKA":     ["кровля", "фасад", "фундамент", "кирпич", "бетон", "арматура", "утеплитель",
                    "металлочерепица", "профнастил", "сайдинг", "монтаж", "строительство", "ангар"],
    "ESTIMATES":   ["смета", "ведомость", "объём работ", "вор", "ФЕР", "ТЕР", "расценка", "калькул"],
    "TEHNADZOR":   ["технадзор", "дефект", "акт осмотра", "нарушение", "предписание", "сп ", "гост", "снип"],
    "AUTO":        ["toyota", "hiace", "запчасть", "brembo", "vin", "авто", "машина"],
    "SEARCH":      ["найди", "поищи", "цена", "стоимость", "купить", "поставщик", "avito", "ozon"],
    "DOCS_PDF_DWG": ["dwg", "dxf", "чертёж", "pdf", "docx", "проект"],
    "NEURON_SOFT_VPN": ["vpn", "wireguard", "xray", "vless", "конфиг", "ключ"],
}

def classify_domain(text: str, file_name: str = "") -> str:
    combined = (text + " " + file_name).lower()
    scores = {}
    for domain, keywords in _DOMAIN_MAP.items():
        scores[domain] = sum(1 for kw in keywords if kw.lower() in combined)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "UNSORTED"

def classify_file_type(file_name: str) -> str:
    ext = file_name.lower().rsplit(".", 1)[-1] if "." in file_name else ""
    mapping = {
        "pdf": "PDF", "docx": "DOCX", "doc": "DOCX",
        "xlsx": "XLSX", "xls": "XLSX", "csv": "CSV",
        "dwg": "DWG", "dxf": "DXF",
        "jpg": "IMAGE", "jpeg": "IMAGE", "png": "IMAGE",
        "heic": "IMAGE", "webp": "IMAGE",
        "zip": "ARCHIVE", "rar": "ARCHIVE",
        "mp4": "VIDEO", "mov": "VIDEO",
        "ogg": "AUDIO", "mp3": "AUDIO",
    }
    return mapping.get(ext, "UNKNOWN")

def classify_intent(text: str) -> str:
    low = text.lower()
    if any(w in low for w in ["смета", "посчитай", "расценка", "объём"]):
        return "estimate"
    if any(w in low for w in ["шаблон", "образец", "возьми как"]):
        return "template"
    if any(w in low for w in ["дефект", "акт", "нарушение", "технадзор"]):
        return "technadzor"
    if any(w in low for w in ["проект", "кж", "ар", "кд", "км"]):
        return "project"
    if any(w in low for w in ["найди", "поищи", "цена", "купить"]):
        return "search"
    if any(w in low for w in ["dwg", "dxf", "чертёж"]):
        return "dwg"
    return "text"
# === END DATA_CLASSIFICATION_V1 ===
