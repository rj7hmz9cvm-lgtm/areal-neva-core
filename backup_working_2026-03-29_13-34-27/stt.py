from __future__ import annotations

import logging
import os
import aiohttp

logger = logging.getLogger("core.stt")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


async def transcribe(file_path: str) -> str:
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY missing")
        return ""
    if not os.path.exists(file_path):
        logger.error("voice file not found: %s", file_path)
        return ""

    try:
        with open(file_path, "rb") as f:
            data = aiohttp.FormData()
            data.add_field("file", f, filename="audio.ogg")
            data.add_field("model", "whisper-large-v3")
            data.add_field("language", "ru")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    GROQ_STT_URL,
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        logger.error("STT %s: %s", resp.status, body[:200])
                        return ""
                    result = await resp.json()
                    text = (result.get("text") or "").strip()
                    logger.info("STT OK: %r", text[:80])
                    return text
    except Exception:
        logger.exception("STT exception file=%s", file_path)
        return ""
