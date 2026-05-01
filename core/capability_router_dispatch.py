# === CAPABILITY_ROUTER_REAL_DISPATCH_V1 ===
from __future__ import annotations

from typing import Any, Dict

def build_execution_plan(input_type: str = "", user_text: str = "", file_name: str = "", mime_type: str = "", topic_id: int = 0) -> Dict[str, Any]:
    low = f"{input_type} {user_text} {file_name} {mime_type}".lower()
    if any(x in low for x in ("dwg", "dxf", "ifc", "чертеж", "чертёж", "проект", "кж", "кмд")):
        engine = "dwg_project"
    elif any(x in low for x in ("смет", "расч", "вор", "xlsx", "xls", "csv")):
        engine = "estimate"
    elif any(x in low for x in ("технадзор", "акт", "дефект", "фото", "jpg", "png", "heic", "сп", "гост")):
        engine = "technadzor"
    elif any(x in low for x in ("найди", "поиск", "цена", "купить")):
        engine = "search"
    else:
        engine = "universal"
    return {
        "router": "CAPABILITY_ROUTER_REAL_DISPATCH_V1",
        "topic_id": int(topic_id or 0),
        "engine": engine,
        "input_type": input_type,
        "file_name": file_name,
        "mime_type": mime_type,
    }

def dispatch_hint(plan: Dict[str, Any]) -> str:
    return str((plan or {}).get("engine") or "universal")
# === END_CAPABILITY_ROUTER_REAL_DISPATCH_V1 ===
