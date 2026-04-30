# === TOPIC_AUTODISCOVERY_V1 ===
import os, yaml, logging
from pathlib import Path

logger = logging.getLogger(__name__)

BASE = "/root/.areal-neva-core"
DIRECTIONS_YAML = f"{BASE}/config/directions.yaml"
TOPICS_BASE = f"{BASE}/data/topics"

DIRECTION_MENU = {
    "estimates":             "Смета",
    "technical_supervision": "Технадзор",
    "internet_search":       "Поиск",
    "defect_acts":           "Акт дефекта",
    "documents":             "Документы",
    "spreadsheets":          "Таблицы / Excel",
    "product_search":        "Закупка товара",
    "auto_parts_search":     "Автозапчасти",
    "construction_search":   "Стройматериалы",
    "google_drive_storage":  "Drive / хранилище",
    "structural_design":     "Проектирование КЖ/КМ",
    "devops_server":         "DevOps / сервер",
    "general_chat":          "Общий чат",
}

QUESTION = (
    "🆕 Новый топик. Выбери направление:\n"
    + "\n".join(f"• {v}" for v in DIRECTION_MENU.values())
    + "\n\nОтветь одним словом."
)

def _load_yaml():
    with open(DIRECTIONS_YAML, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _save_yaml(data):
    import shutil, time
    bak = DIRECTIONS_YAML + f'.bak.{int(time.time())}'
    shutil.copy2(DIRECTIONS_YAML, bak)
    with open(DIRECTIONS_YAML, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

def is_topic_known(topic_id: int) -> bool:
    try:
        data = _load_yaml()
        for d in data.get("directions", []):
            if topic_id in (d.get("topic_ids") or []):
                return True
    except Exception as e:
        logger.error(f"AUTODISCOVERY is_topic_known: {e}")
    return False

def assign_topic(topic_id: int, direction_id: str) -> bool:
    try:
        data = _load_yaml()
        for d in data.get("directions", []):
            if d.get("id") == direction_id:
                ids = d.get("topic_ids") or []
                if topic_id not in ids:
                    ids.append(topic_id)
                    d["topic_ids"] = ids
                break
        _save_yaml(data)
        Path(TOPICS_BASE).mkdir(parents=True, exist_ok=True)
        Path(f"{TOPICS_BASE}/{topic_id}").mkdir(exist_ok=True)
        logger.info(f"AUTODISCOVERY_ASSIGNED topic={topic_id} direction={direction_id}")
        return True
    except Exception as e:
        logger.error(f"AUTODISCOVERY assign_topic: {e}")
        return False

def match_direction_from_text(text: str) -> str | None:
    t = text.strip().lower()
    mapping = {
        "смет": "estimates",
        "технадзор": "technical_supervision",
        "надзор": "technical_supervision",
        "поиск": "internet_search",
        "акт": "defect_acts",
        "дефект": "defect_acts",
        "документ": "documents",
        "таблиц": "spreadsheets",
        "excel": "spreadsheets",
        "закупк": "product_search",
        "товар": "product_search",
        "запчаст": "auto_parts_search",
        "стройматер": "construction_search",
        "drive": "google_drive_storage",
        "хранилищ": "google_drive_storage",
        "проектир": "structural_design",
        "кж": "structural_design",
        "devops": "devops_server",
        "сервер": "devops_server",
        "чат": "general_chat",
    }
    for key, direction in mapping.items():
        if key in t:
            return direction
    return None

async def create_drive_folder(topic_id: int, chat_id: int) -> str | None:
    try:
        from core.topic_drive_oauth import _ensure_folder, _get_drive_service
        service = _get_drive_service()
        folder_id = _ensure_folder(service, chat_id, topic_id)
        logger.info(f"AUTODISCOVERY_DRIVE topic={topic_id} folder={folder_id}")
        return folder_id
    except Exception as e:
        logger.error(f"AUTODISCOVERY create_drive_folder: {e}")
        return None

def get_question_text() -> str:
    return QUESTION
