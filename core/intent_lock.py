# === INTENT_LOCK_V1 ===
# Запрещает смешивание режимов и создание TASK из CHAT
import logging
logger = logging.getLogger(__name__)

_CHAT_ONLY = [
    "спасибо", "ок", "понял", "хорошо", "окей", "ладно",
    "угу", "ага", "ясно", "понятно", "супер", "отлично",
    "класс", "прекрасно", "отлично", "молодец",
]

_FILE_RESULT_REQUIRED = ["estimate", "project", "template", "dwg", "ocr", "technadzor"]

def is_chat_only(text: str) -> bool:
    """Короткие реакции — не создают задачи"""
    t = text.strip().lower().rstrip("!.,?")
    return t in _CHAT_ONLY or (len(t) <= 3 and t not in ["да", "нет", "ок"])

def file_result_guard(intent: str, input_type: str, result: str, artifact_path: str = None) -> dict:
    """
    FILE_RESULT_GUARD: если file-task — обязателен артефакт.
    Канон §11: без артефакта при файловой задаче = FAILED
    """
    is_file = input_type in ("drive_file", "file") or intent in _FILE_RESULT_REQUIRED
    if not is_file:
        return {"ok": True}

    if artifact_path:
        import os
        if os.path.exists(artifact_path) and os.path.getsize(artifact_path) > 100:
            return {"ok": True}
        return {"ok": False, "reason": "ARTIFACT_FILE_NOT_EXISTS"}

    # нет artifact_path — проверяем result на Drive link
    if result and any(k in result for k in ["https://drive.google", "docs.google", "https://", ".xlsx", ".docx"]):
        return {"ok": True}

    return {"ok": False, "reason": "NO_VALID_ARTIFACT"}

def intent_priority(intent: str) -> int:
    """FINISH > CANCEL > CONFIRM > REVISION > TASK > SEARCH > CHAT"""
    order = {"finish": 7, "cancel": 6, "confirm": 5, "revision": 4,
             "task": 3, "search": 2, "chat": 1}
    return order.get(str(intent).lower(), 0)
# === END INTENT_LOCK_V1 ===
