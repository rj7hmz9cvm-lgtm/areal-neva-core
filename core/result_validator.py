# === RESULT_VALIDATOR_V1 ===
import re, logging
logger = logging.getLogger(__name__)

_FORBIDDEN = [
    "файл скачан, ожидает анализа",
    "структура проекта включает",
    "файл содержит проект",
    "этот чат предназначен",
    "анализирую, результат будет готов",
    "проверяю доступные файлы",
    "выбор принят",
    "какие именно файлы вас интересуют",
    "задача не выполнена. повтори",
    "готов к выполнению",
    "не понимаю запрос",
]
_REQUIRED_FOR_FILE = ["http", "drive.google", "docs.google", ".xlsx", ".docx", ".pdf"]

def validate_result(result: str, input_type: str = "text", intent: str = "") -> dict:
    if not result or len(result.strip()) < 10:
        return {"ok": False, "reason": "EMPTY_RESULT"}
    low = result.lower()
    for f in _FORBIDDEN:
        if f in low:
            return {"ok": False, "reason": f"FORBIDDEN_PHRASE:{f[:40]}"}
    is_file_task = input_type in ("drive_file", "file") or intent in ("estimate", "project", "template", "dwg")
    if is_file_task:
        if not any(k in low for k in _REQUIRED_FOR_FILE):
            return {"ok": True, "reason": "NO_ARTIFACT_LINK_WARNING"}
    return {"ok": True, "reason": "OK"}

def is_generic_response(result: str) -> bool:
    low = (result or "").lower()
    return any(f in low for f in _FORBIDDEN)

def enforce_format(result: str, intent: str = "", has_search: bool = False) -> str:
    if not has_search:
        return result
    low = result.lower()
    if "лучший" not in low and "рекомендую" not in low and "итог" not in low:
        result = result.rstrip() + "\n\n⚠️ Нужна таблица сравнения или итоговый выбор?"
    return result

def human_decision_format(technical_result: str, intent: str = "") -> str:
    if not technical_result or len(technical_result) < 30:
        return technical_result
    return technical_result
# === END RESULT_VALIDATOR_V1 ===
