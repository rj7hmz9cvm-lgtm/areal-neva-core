# === FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG ===
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path("/root/.areal-neva-core")
CAT_DIR = BASE / "data" / "telegram_file_catalog"
CAT_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe(v) -> str:
    return "" if v is None else str(v).strip()


def _catalog_path(chat_id: str, topic_id: int) -> Path:
    safe_chat = _safe(chat_id).replace("/", "_")
    return CAT_DIR / f"chat_{safe_chat}__topic_{int(topic_id or 0)}.jsonl"


def _hash_record(file_id: str = "", file_name: str = "", size: int = 0) -> str:
    raw = f"{file_id}|{file_name}|{size}".encode("utf-8", "ignore")
    return hashlib.sha256(raw).hexdigest()


def load_catalog(chat_id: str, topic_id: int) -> List[Dict[str, Any]]:
    p = _catalog_path(chat_id, topic_id)
    if not p.exists():
        return []

    out = []
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def find_duplicate(chat_id: str, topic_id: int, file_id: str = "", file_name: str = "", size: int = 0) -> Optional[Dict[str, Any]]:
    h = _hash_record(file_id, file_name, size)
    fn = _safe(file_name).lower()

    for r in reversed(load_catalog(chat_id, topic_id)):
        if r.get("hash") == h:
            return r
        if file_id and r.get("file_id") == file_id:
            return r
        if fn and r.get("file_name", "").lower() == fn and int(r.get("size") or 0) == int(size or 0):
            return r

    return None


def register_file(
    chat_id: str,
    topic_id: int,
    task_id: str,
    file_id: str = "",
    file_name: str = "",
    mime_type: str = "",
    size: int = 0,
    source: str = "telegram",
    drive_link: str = "",
) -> Dict[str, Any]:
    duplicate = find_duplicate(chat_id, topic_id, file_id, file_name, size)
    rec = {
        "engine": "FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG",
        "timestamp": _now(),
        "chat_id": _safe(chat_id),
        "topic_id": int(topic_id or 0),
        "task_id": _safe(task_id),
        "file_id": _safe(file_id),
        "file_name": _safe(file_name),
        "mime_type": _safe(mime_type),
        "size": int(size or 0),
        "source": _safe(source) or "telegram",
        "drive_link": _safe(drive_link),
        "hash": _hash_record(file_id, file_name, size),
        "duplicate": bool(duplicate),
        "duplicate_of": duplicate.get("task_id") if duplicate else "",
    }

    p = _catalog_path(chat_id, topic_id)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return {"ok": True, "duplicate": bool(duplicate), "duplicate_record": duplicate, "record": rec, "catalog_path": str(p)}


def duplicate_user_message(file_name: str, duplicate_record: Dict[str, Any]) -> str:
    old_task = duplicate_record.get("task_id", "")
    old_time = duplicate_record.get("timestamp", "")
    return "\n".join(
        [
            "Этот файл уже был в Telegram",
            f"Файл: {file_name}",
            f"Первая запись: {old_time}",
            f"Задача: {old_task}",
            "Что сделать с повтором: использовать как новый образец, заменить старый или пропустить?",
        ]
    ).strip()


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG ===
