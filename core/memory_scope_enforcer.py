# === MEMORY_SCOPE_ENFORCER_V1 ===
# === ARCHIVE_RECALL_VALIDATOR_V1 ===
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

def topic_key(topic_id: int) -> str:
    return f"topic_{int(topic_id or 0)}_"

def allowed_memory_key(key: str, topic_id: int) -> bool:
    key = str(key or "")
    return key.startswith(topic_key(topic_id))

def filter_topic_memory(rows: Iterable[Any], topic_id: int) -> List[Any]:
    out = []
    for row in rows or []:
        try:
            key = row["key"] if isinstance(row, dict) else row[0]
        except Exception:
            key = ""
        if allowed_memory_key(str(key), topic_id):
            out.append(row)
    return out

def validate_archive_recall_answer(answer: str, archive_context: str) -> Dict[str, Any]:
    if not archive_context:
        return {"ok": False, "reason": "NO_ARCHIVE_CONTEXT"}
    ans = (answer or "").lower()
    ctx = (archive_context or "").lower()
    words = [w for w in re.findall(r"[a-zа-я0-9]{4,}", ans) if len(w) >= 4]
    hits = sum(1 for w in words[:80] if w in ctx)
    return {"ok": hits >= 3, "reason": "OK" if hits >= 3 else "LOW_ARCHIVE_OVERLAP", "hits": hits}
# === END_ARCHIVE_RECALL_VALIDATOR_V1 ===
# === END_MEMORY_SCOPE_ENFORCER_V1 ===
