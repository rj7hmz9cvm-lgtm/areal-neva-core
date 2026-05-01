# === NORMATIVE_SOURCE_ENGINE_FULL_CLOSE_V1 ===
# === NORMATIVE_NO_HALLUCINATION_GUARD_V1 ===
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

BASE = Path("/root/.areal-neva-core")
NORM_INDEX = BASE / "data/norms/normative_index.json"

def _load() -> List[Dict[str, Any]]:
    if NORM_INDEX.exists():
        try:
            data = json.loads(NORM_INDEX.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []
    return []

def search_normative_sources(text: str, limit: int = 8) -> List[Dict[str, Any]]:
    hay = (text or "").lower()
    out = []
    for row in _load():
        keys = " ".join(row.get("keywords") or []).lower()
        score = sum(1 for w in re.findall(r"[а-яa-z0-9]{4,}", hay) if w in keys or w in str(row).lower())
        if score:
            r = dict(row)
            r["score"] = score
            r["confidence"] = "CONFIRMED" if r.get("source") and r.get("clause") else "PARTIAL"
            out.append(r)
    out.sort(key=lambda x: int(x.get("score") or 0), reverse=True)
    return out[:limit]

def assert_no_exact_clause_without_source(norm: Dict[str, Any]) -> bool:
    return not bool(norm.get("clause")) or bool(norm.get("source"))

def format_normative_sources(rows: List[Dict[str, Any]]) -> str:
    lines = []
    for r in rows:
        confidence = "CONFIRMED" if assert_no_exact_clause_without_source(r) and r.get("source") else "PARTIAL"
        lines.append(f"{r.get('doc','UNKNOWN')} {r.get('clause','')}: {r.get('text','')} [{confidence}] {r.get('source','')}")
    return "\n".join(lines)
# === END_NORMATIVE_NO_HALLUCINATION_GUARD_V1 ===
# === END_NORMATIVE_SOURCE_ENGINE_FULL_CLOSE_V1 ===
