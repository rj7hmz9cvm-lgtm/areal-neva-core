import os; os.environ["CUDA_VISIBLE_DEVICES"] = ""
from __future__ import annotations

import asyncio
import logging
import os

import aiohttp

logger = logging.getLogger("core.stt")

STT_BACKEND = os.getenv("STT_BACKEND", "groq").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")


def _transcribe_whisper_sync(file_path: str) -> str:
    import whisper
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(file_path, language="ru")
    return (result.get("text") or "").strip()


async def _transcribe_groq(file_path: str) -> str | None:
    if not GROQ_API_KEY:
        return None
    try:
        with open(file_path, "rb") as f:
            data = aiohttp.FormData()
            data.add_field("file", f, filename=os.path.basename(file_path))
            data.add_field("model", "whisper-large-v3")
            data.add_field("language", "ru")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        raise RuntimeError(f"groq http {resp.status}: {text[:300]}")
                    payload = await resp.json()
                    return (payload.get("text") or "").strip()
    except Exception:
        logger.exception("stt groq error file=%s", file_path)
        return None


async def transcribe(file_path: str) -> str | None:
    if not file_path or not os.path.exists(file_path):
        logger.error("stt file not found: %s", file_path)
        return None

    if STT_BACKEND == "groq":
        text = await _transcribe_groq(file_path)
        if text:
            logger.info("stt groq ok len=%s file=%s", len(text), file_path)
            return text

    try:
        loop = asyncio.get_running_loop()
        text = await loop.run_in_executor(None, _transcribe_whisper_sync, file_path)
        if text:
            logger.info("stt whisper ok len=%s file=%s", len(text), file_path)
            return text
        return None
    except Exception:
        logger.exception("stt whisper error file=%s", file_path)
        return None
