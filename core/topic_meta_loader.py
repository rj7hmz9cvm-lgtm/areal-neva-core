"""TOPIC_META_LOADER_V1 — читает data/topics/{tid}/meta.json при INTAKE."""
import json
from pathlib import Path
from typing import Optional, Dict, Any

DATA_TOPICS = Path("data/topics")

# Триггеры "что это за чат" — отвечаем из meta.json напрямую
WHAT_IS_THIS_TRIGGERS = [
    "что мы здесь делаем", "что мы тут делаем", "для чего ты",
    "для чего этот чат", "для чего этот топик", "для чего у нас",
    "что мы делаем в данном чате", "что мы делаем тут",
    "скажи для чего", "зачем этот чат", "зачем этот топик",
    "про что чат", "про что топик", "что за чат", "что за топик",
]

def load_topic_meta(topic_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает meta.json топика или None."""
    if topic_id is None:
        return None
    folder = DATA_TOPICS / str(topic_id)
    meta_path = folder / "meta.json"
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None

def is_what_is_this_question(text: str) -> bool:
    """True если текст — вопрос о назначении чата."""
    if not text:
        return False
    t = text.lower().replace("[voice]", "").replace("🎤", "").strip()
    return any(trigger in t for trigger in WHAT_IS_THIS_TRIGGERS)

def build_topic_self_answer(meta: Dict[str, Any]) -> str:
    """Формирует ответ от имени топика на вопрос 'что мы тут делаем'."""
    name = meta.get("name", "Без имени")
    direction = meta.get("direction", "general_chat")
    
    DIRECTION_DESCRIPTIONS = {
        "general_chat": "общий чат для произвольных задач",
        "crm_leads": "лиды, реклама, AmoCRM, лидогенерация",
        "estimates": "сметы, расчёт стоимости строительства",
        "technical_supervision": "технадзор, акты осмотра, дефекты, СП/ГОСТ",
        "structural_design": "проектирование КЖ/КМ/КМД/АР/ОВ/ВК/ЭОМ/СС/ГП/ПЗ/СМ/ТХ",
        "internet_search": "интернет-поиск товаров и информации",
        "auto_parts_search": "поиск автозапчастей, артикулы, аналоги, цены",
        "orchestration_core": "коды оркестра, AI-роутер, архитектура системы",
        "video_production": "генерация и производство видеоконтента",
        "devops_server": "VPN, VPS, конфигурации серверов, настройки",
        "job_search": "поиск работы и интеграция с биржами труда",
    }
    
    desc = DIRECTION_DESCRIPTIONS.get(direction, direction)
    return f"Этот чат — {name}. Направление: {desc}."
