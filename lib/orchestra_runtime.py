import os
import time
import json
import hashlib
from typing import Any, Dict, Optional
import httpx

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://127.0.0.1:8080")
ORCHESTRATOR_TIMEOUT_CONNECT = float(os.getenv("ORCHESTRATOR_TIMEOUT_CONNECT", "10"))
ORCHESTRATOR_TIMEOUT_READ = float(os.getenv("ORCHESTRATOR_TIMEOUT_READ", "120"))
DEDUP_TTL_SEC = int(os.getenv("DEDUP_TTL_SEC", "30"))

_SEEN: Dict[str, float] = {}

def sanitize_text(text: Any) -> str:
    if text is None:
        return ""
    return str(text).strip()

def build_task_key(user_id=None, message_id=None, text="", **kwargs) -> str:
    raw = f"{user_id}:{message_id}:{sanitize_text(text)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def mark_and_check_duplicate(key: str) -> bool:
    now = time.time()
    ts = _SEEN.get(key)
    if ts is not None and now - ts < DEDUP_TTL_SEC:
        return True
    _SEEN[key] = now
    return False

def should_skip_answer(*args, **kwargs) -> bool:
    key = kwargs.get("task_key") or kwargs.get("key")
    if key:
        return mark_and_check_duplicate(str(key))
    return False

def build_prompt(*, chat_title: str = "", chat_id: int = 0, thread_id: Optional[int] = None,
                 user_name: str = "unknown", user_id: Optional[int] = None, text: str = "",
                 source: str = "telegram", content_type: str = "text", **kwargs) -> str:
    text = sanitize_text(text)
    parts = []
    if chat_title:
        parts.append(f"CHAT: {chat_title}")
    if chat_id:
        parts.append(f"CHAT_ID: {chat_id}")
    if thread_id is not None:
        parts.append(f"THREAD_ID: {thread_id}")
    if user_name:
        parts.append(f"USER: {user_name}")
    if user_id is not None:
        parts.append(f"USER_ID: {user_id}")
    if source:
        parts.append(f"SOURCE: {source}")
    if content_type:
        parts.append(f"TYPE: {content_type}")
    parts.append("")
    parts.append(text)
    return "\n".join(parts).strip()

def extract_answer(payload: Any) -> str:
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload.strip()
    if isinstance(payload, dict):
        for key in ("answer", "result", "output", "text", "stdout"):
            val = payload.get(key)
            if val:
                return str(val).strip()
        try:
            return json.dumps(payload, ensure_ascii=False)
        except Exception:
            return str(payload).strip()
    return str(payload).strip()

def call_orchestrator(prompt: str) -> str:
    try:
        timeout = httpx.Timeout(ORCHESTRATOR_TIMEOUT_READ, connect=ORCHESTRATOR_TIMEOUT_CONNECT)
        r = httpx.post(ORCHESTRATOR_URL, json={"prompt": prompt}, timeout=timeout)
        r.raise_for_status()
        content_type = r.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                return extract_answer(r.json())
            except Exception:
                return r.text.strip()
        return r.text.strip()
    except Exception as e:
        return f"ERROR: {e}"

def execute(prompt: str) -> str:
    return call_orchestrator(sanitize_text(prompt))
