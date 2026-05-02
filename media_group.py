# === MEDIA_GROUP_DEBOUNCE_V1 ===
from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger("media_group")

_album_buffer: Dict[str, Dict[str, Any]] = {}
_DEBOUNCE_SEC = 1.5

async def _flush_album(media_group_id: str, callback: Callable[..., Awaitable[Any]]) -> None:
    await asyncio.sleep(_DEBOUNCE_SEC)
    item = _album_buffer.pop(str(media_group_id), None)
    if not item:
        return
    files: List[Any] = item.get("files") or []
    chat_id = item.get("chat_id")
    topic_id = item.get("topic_id")
    try:
        result = callback(files=files, media_group_id=media_group_id, chat_id=chat_id, topic_id=topic_id)
        if asyncio.iscoroutine(result) or hasattr(result, "__await__"):
            await result
        logger.info("MEDIA_GROUP_DEBOUNCE_V1_FLUSHED group=%s files=%s", media_group_id, len(files))
    except Exception as e:
        logger.exception("MEDIA_GROUP_DEBOUNCE_V1_CALLBACK_ERR group=%s err=%s", media_group_id, e)

async def handle_media_group(
    file: Any,
    media_group_id: str,
    chat_id: str,
    topic_id: int = 0,
    callback: Optional[Callable[..., Awaitable[Any]]] = None,
) -> Dict[str, Any]:
    gid = str(media_group_id or "").strip()
    if not gid:
        if callback:
            result = callback(files=[file], media_group_id="", chat_id=chat_id, topic_id=topic_id)
            if asyncio.iscoroutine(result) or hasattr(result, "__await__"):
                await result
        return {"ok": True, "single": True, "files": 1}

    if gid not in _album_buffer:
        _album_buffer[gid] = {
            "files": [],
            "chat_id": chat_id,
            "topic_id": int(topic_id or 0),
            "timer": None,
        }

    buf = _album_buffer[gid]
    buf["files"].append(file)
    buf["chat_id"] = chat_id
    buf["topic_id"] = int(topic_id or 0)

    timer = buf.get("timer")
    if timer and not timer.done():
        timer.cancel()

    if callback:
        buf["timer"] = asyncio.create_task(_flush_album(gid, callback))

    return {"ok": True, "media_group_id": gid, "buffered": len(buf["files"])}

def get_media_group_buffer_size(media_group_id: str) -> int:
    item = _album_buffer.get(str(media_group_id or ""))
    if not item:
        return 0
    return len(item.get("files") or [])

def clear_media_group(media_group_id: str) -> int:
    item = _album_buffer.pop(str(media_group_id or ""), None)
    if not item:
        return 0
    return len(item.get("files") or [])

# === END_MEDIA_GROUP_DEBOUNCE_V1 ===
