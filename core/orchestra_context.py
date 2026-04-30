# === ORCHESTRA_SHARED_CONTEXT_V1 ===
# Каждая модель получает единый контекст: ONE_SHARED_CONTEXT + memory + task + pin + topic_role
import os, logging
logger = logging.getLogger(__name__)

def build_shared_context(
    raw_input: str = "",
    topic_id: int = 0,
    chat_id: str = "",
    active_task: dict = None,
    pin_text: str = "",
    short_memory: str = "",
    long_memory: str = "",
    search_result: str = "",
    topic_role: str = "",
    files: list = None,
) -> str:
    """
    Собирает ORCHESTRA_SHARED_CONTEXT для передачи в любую модель.
    Порядок приоритета из канона §5.1:
    user_input → active_task → pin → short_memory → long_memory → search
    """
    parts = []

    if topic_role:
        parts.append(f"[ROLE] {topic_role}")

    if active_task:
        state = active_task.get("state", "")
        raw = str(active_task.get("raw_input", ""))[:200]
        parts.append(f"[ACTIVE_TASK] state={state} input={raw}")

    if pin_text:
        parts.append(f"[PIN] {pin_text[:300]}")

    if short_memory:
        parts.append(f"[SHORT_MEMORY] {short_memory[:400]}")

    if long_memory:
        parts.append(f"[LONG_MEMORY] {long_memory[:400]}")

    if search_result:
        parts.append(f"[SEARCH] {search_result[:500]}")

    if files:
        parts.append(f"[FILES] {', '.join(str(f) for f in files[:5])}")

    if raw_input:
        parts.append(f"[USER] {raw_input[:500]}")

    return "\n".join(parts)

def user_mode_switch(text: str) -> str:
    """
    USER_MODE_SWITCH: TECH / HUMAN (default)
    """
    low = text.lower()
    if any(w in low for w in ["технический", "детально", "подробно", "tech mode", "полный разбор"]):
        return "TECH"
    return "HUMAN"

def mode_switch(task: dict) -> str:
    """
    MODE_SWITCH: LIGHT / FULL
    """
    intent = str(task.get("intent", "")).lower()
    input_type = str(task.get("input_type", "")).lower()
    if input_type == "drive_file" or intent in ("estimate", "project", "template", "technadzor", "dwg"):
        return "FULL"
    return "LIGHT"
# === END ORCHESTRA_SHARED_CONTEXT_V1 ===
