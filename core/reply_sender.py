# TG_TIMEOUT_PATCH
from __future__ import annotations
import importlib
import logging
import os
import aiohttp

logger = logging.getLogger("core.reply_sender")
_send_fn = None

def _find_send():
    global _send_fn
    if _send_fn is not None:
        return _send_fn
    for mod_path in ("core.telegram_sender", "telegram_sender"):
        try:
            m = importlib.import_module(mod_path)
            for fn_name in ("send_message", "send", "send_text"):
                if hasattr(m, fn_name):
                    _send_fn = getattr(m, fn_name)
                    return _send_fn
        except Exception:
            continue
    return None

async def send_reply(chat_id: int, text: str, topic_id=None) -> bool:
    fn = _find_send()
    if fn:
        try:
            r = fn(chat_id, text[:4096], topic_id)
            if hasattr(r, "__await__"):
                await r
            return True
        except TypeError:
            try:
                r = fn(chat_id, text[:4096])
                if hasattr(r, "__await__"):
                    await r
                return True
            except Exception:
                logger.exception("reply via module failed")
        except Exception:
            logger.exception("reply via module failed")

    token = os.getenv("TELEGRAM_BOT_TOKEN", "") or os.getenv("TG_BOT_TOKEN", "")
    if not token:
        logger.error("NO BOT TOKEN")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text[:4096]}
    if topic_id:
        payload["message_thread_id"] = topic_id

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                return resp.status == 200
    except Exception:
        logger.exception("HTTP send failed chat_id=%s", chat_id)
        return False
