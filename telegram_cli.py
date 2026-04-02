from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv("/root/.areal-neva-core/.env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
API = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""

def _api_call(method: str, payload: Optional[Dict[str, Any]] = None, timeout: int = 60) -> Dict[str, Any]:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is empty")
    url = f"{API}/{method}"
    resp = requests.post(url, json=payload or {}, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"telegram_api_error: {data}")
    return data

def send_telegram_reply(chat_id: str | int, msg_id: str | int, body: str) -> Dict[str, Any]:
    text = (body or "").strip()
    if not text:
        text = "empty result"
    payload = {
        "chat_id": chat_id,
        "text": text[:4096],
        "reply_to_message_id": int(msg_id),
        "allow_sending_without_reply": True,
    }
    return _api_call("sendMessage", payload)

def send_telegram_message(chat_id: str | int, body: str) -> Dict[str, Any]:
    text = (body or "").strip()
    if not text:
        text = "empty result"
    payload = {
        "chat_id": chat_id,
        "text": text[:4096],
    }
    return _api_call("sendMessage", payload)

def get_file(file_id: str) -> Dict[str, Any]:
    return _api_call("getFile", {"file_id": file_id})

def get_updates(offset: Optional[int] = None, timeout: int = 30) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"timeout": timeout}
    if offset is not None:
        payload["offset"] = offset
    return _api_call("getUpdates", payload, timeout=timeout + 10)
