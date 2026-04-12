import os
import aiohttp
import logging

logger = logging.getLogger(__name__)

async def transcribe_voice(path: str) -> str:
    if not os.path.exists(path):
        raise RuntimeError(f"voice file not found: {path}")

    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    if groq_key:
        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {groq_key}"}
        model = "whisper-large-v3-turbo"
    elif openai_key:
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {openai_key}"}
        model = "gpt-4o-mini-transcribe"
    else:
        raise RuntimeError("STT API key missing: set GROQ_API_KEY or OPENAI_API_KEY")

    size = os.path.getsize(path)
    logger.info("STT start file=%s size=%s", path, size)

    data = aiohttp.FormData()
    data.add_field("model", model)
    data.add_field("response_format", "json")

    with open(path, "rb") as f:
        data.add_field("file", f, filename=os.path.basename(path), content_type="audio/ogg")
        async with aiohttp.ClientSession() as s:
            r = await s.post(url, headers=headers, data=data, timeout=aiohttp.ClientTimeout(total=300))
            body = await r.text()
            logger.info("STT http_status=%s", r.status)
            if r.status != 200:
                logger.error("STT body=%s", body[:500])
                raise RuntimeError(f"STT HTTP {r.status}: {body[:300]}")
            try:
                import json
                js = json.loads(body)
            except Exception:
                raise RuntimeError(f"STT bad json: {body[:300]}")

    text = (js.get("text") or "").strip()
    if not text:
        raise RuntimeError("STT returned empty transcript")

    logger.info("STT ok transcript_len=%s", len(text))

    try:
        os.remove(path)
    except Exception:
        pass

    return text
