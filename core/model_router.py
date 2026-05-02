# === FINAL_CLOSURE_BLOCKER_FIX_V1_MODEL_ROUTER ===
from __future__ import annotations

import re
from typing import Any, Dict


def _norm(text: str) -> str:
    return (text or "").lower().replace("ё", "е").strip()


def _has(pattern: str, text: str) -> bool:
    return bool(re.search(pattern, text, flags=re.I | re.U))


def detect_domain(text: str = "", file_name: str = "", input_type: str = "text") -> Dict[str, Any]:
    t = _norm(f"{text}\n{file_name}")

    if input_type in ("drive_file", "file") and not t:
        return {"domain": "file", "intent": "needs_context", "confidence": 0.50}

    if _has(r"(смет\w*|кс[- ]?2|кс[- ]?3|вор\b|ведомост\w*\s+об[ъь]ем\w*|расцен\w*|стоимост\w*|цен\w*\s+материал\w*|материал\w*)", t):
        return {"domain": "estimate", "intent": "estimate", "confidence": 0.88}

    if _has(r"(акт\w*|технадзор\w*|техническ\w*\s+надзор\w*|дефект\w*|замечан\w*|нарушен\w*|освидетельств\w*|стройконтрол\w*|сп\s*\d+|гост\s*\d+|снип\w*)", t):
        return {"domain": "technadzor", "intent": "technadzor_act", "confidence": 0.86}

    if _has(r"(кж\b|кд\b|кр\b|ар\b|проект\w*|чертеж\w*|чертёж\w*|dxf\b|dwg\b|плит\w*|фундамент\w*|разрез\w*|узел\w*|спецификац\w*)", t):
        return {"domain": "project", "intent": "project", "confidence": 0.78}

    if _has(r"(что\s+скидывал\w*|какие\s+файл\w*|какой\s+файл\w*|покажи\s+файл\w*|последн\w*\s+файл\w*|документ\w*\s+в\s+чат\w*|памят\w*|напомни\w*)", t):
        return {"domain": "memory", "intent": "memory_query", "confidence": 0.82}

    if _has(r"(найди\w*|поищи\w*|поиск\w*|интернет\w*|авито|ozon|wildberries|яндекс|google|сколько\s+сто\w*)", t):
        return {"domain": "search", "intent": "search", "confidence": 0.72}

    return {"domain": "chat", "intent": "chat", "confidence": 0.30}


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_MODEL_ROUTER ===
