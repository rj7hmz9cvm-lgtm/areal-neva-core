# === UNIFIED_ENGINE_RESULT_VALIDATOR_V1 ===
# === UNIFIED_ARTIFACT_CONTRACT_V1 ===
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

BAD_FINAL_PATTERNS = [
    r"ожида[её]т анализ",
    r"файл скачан",
    r"ожидает выбора",
    r"не удалось",
    r"ошибка",
    r"error",
    r"traceback",
    r"none$",
    r"null$",
    r"undefined",
    r"пока не могу",
    r"не могу обработать",
]

FILE_INPUT_TYPES = {"drive_file", "file", "document", "photo", "image", "drawing", "table"}

def _s(v: Any, limit: int = 20000) -> str:
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        try:
            v = json.dumps(v, ensure_ascii=False)
        except Exception:
            v = str(v)
    s = str(v)
    s = s.replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{4,}", "\n\n", s)
    return s.strip()[:limit]

def _links(text: str) -> List[str]:
    return [x.rstrip(".,;:") for x in re.findall(r"https?://[^\s\]\)\}\"']+", text or "")]

def _exists(path: str) -> bool:
    try:
        return bool(path) and os.path.exists(path)
    except Exception:
        return False

def normalize_engine_result(raw: Any, default_engine: str = "UNKNOWN_ENGINE") -> Dict[str, Any]:
    if isinstance(raw, dict):
        data = dict(raw)
    else:
        data = {"summary": _s(raw), "result": _s(raw)}

    summary = _s(data.get("summary") or data.get("result_text") or data.get("result") or data.get("message") or data.get("text"))
    artifact_path = _s(data.get("artifact_path") or data.get("path") or "")
    artifact_name = _s(data.get("artifact_name") or (Path(artifact_path).name if artifact_path else ""))
    drive_link = _s(data.get("drive_link") or data.get("link") or data.get("url") or "")

    artifact = data.get("artifact")
    if isinstance(artifact, dict):
        artifact_path = artifact_path or _s(artifact.get("path"))
        artifact_name = artifact_name or _s(artifact.get("name") or artifact.get("artifact_name"))
        drive_link = drive_link or _s(artifact.get("drive_link") or artifact.get("link") or artifact.get("url"))

    extra = data.get("extra_artifacts") or []
    if isinstance(extra, str):
        extra = [extra]
    if not isinstance(extra, list):
        extra = []

    found_links = _links("\n".join([summary, drive_link, _s(data)]))
    if not drive_link and found_links:
        drive_link = found_links[0]

    error = _s(data.get("error") or data.get("error_message") or data.get("reason") or "")
    engine = _s(data.get("engine") or default_engine or "UNKNOWN_ENGINE", 300)

    success_raw = data.get("success", data.get("ok", None))
    if success_raw is None:
        success = bool(summary or artifact_path or drive_link or extra) and not bool(error)
    else:
        success = bool(success_raw)

    return {
        "success": success,
        "engine": engine,
        "summary": summary,
        "artifact_path": artifact_path,
        "artifact_name": artifact_name,
        "drive_link": drive_link,
        "extra_artifacts": extra,
        "error": error,
        "links": found_links,
        "raw": data,
    }

def has_artifact_contract(result: Dict[str, Any]) -> bool:
    if not isinstance(result, dict):
        result = normalize_engine_result(result)
    if result.get("drive_link"):
        return True
    if result.get("artifact_path") and _exists(result.get("artifact_path")):
        return True
    for p in result.get("extra_artifacts") or []:
        if isinstance(p, str) and _exists(p):
            return True
        if isinstance(p, dict) and _exists(_s(p.get("path"))):
            return True
    if result.get("links"):
        return True
    return False

def validate_engine_result(raw: Any, input_type: str = "", user_text: str = "", topic_id: int = 0, require_artifact: Optional[bool] = None) -> Dict[str, Any]:
    result = normalize_engine_result(raw)
    text = _s(result.get("summary") or result.get("raw"))
    low = text.lower()
    inp = (input_type or "").lower()

    if not result.get("success") and result.get("error"):
        return {"ok": False, "reason": "ENGINE_ERROR", "contract": result}

    if len(text) < 8 and not has_artifact_contract(result):
        return {"ok": False, "reason": "EMPTY_OR_TOO_SHORT", "contract": result}

    for pat in BAD_FINAL_PATTERNS:
        if re.search(pat, low, re.I):
            if not has_artifact_contract(result):
                return {"ok": False, "reason": f"BAD_FINAL_TEXT:{pat}", "contract": result}

    if require_artifact is None:
        require_artifact = inp in FILE_INPUT_TYPES or any(x in (user_text or "").lower() for x in ("файл", "смет", "акт", "проект", "dwg", "dxf", "excel", "pdf", "docx"))

    if require_artifact and not has_artifact_contract(result):
        if not re.search(r"(создан|готов|сформирован|pdf|xlsx|docx|zip|drive|google|ссылка|retry|telegram)", low, re.I):
            return {"ok": False, "reason": "NO_ARTIFACT_OR_LINK_FOR_FILE_TASK", "contract": result}

    return {"ok": True, "reason": "OK", "contract": result}

def result_to_user_text(raw: Any) -> str:
    r = normalize_engine_result(raw)
    parts = []
    if r.get("summary"):
        parts.append(r["summary"])
    if r.get("drive_link"):
        parts.append(f"Ссылка: {r['drive_link']}")
    if r.get("artifact_path") and not r.get("drive_link"):
        parts.append(f"Артефакт: {r['artifact_path']}")
    links = [x for x in r.get("links") or [] if x not in "\n".join(parts)]
    if links:
        parts.append("Ссылки:\n" + "\n".join(f"- {x}" for x in links[:10]))
    if r.get("error") and not parts:
        parts.append(f"Ошибка: {r['error']}")
    return "\n\n".join(parts).strip()

def normalize_and_validate(raw: Any, input_type: str = "", user_text: str = "", topic_id: int = 0, require_artifact: Optional[bool] = None) -> Dict[str, Any]:
    v = validate_engine_result(raw, input_type=input_type, user_text=user_text, topic_id=topic_id, require_artifact=require_artifact)
    v["text"] = result_to_user_text(v.get("contract") or raw)
    return v
# === END_UNIFIED_ARTIFACT_CONTRACT_V1 ===
# === END_UNIFIED_ENGINE_RESULT_VALIDATOR_V1 ===
