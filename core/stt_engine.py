import os
import aiohttp
import logging
import json

logger = logging.getLogger(__name__)

async def transcribe_voice(path: str) -> str:
    if not os.path.exists(path):
        raise RuntimeError(f"voice file not found: {path}")

    groq_key = (os.getenv("GROQ_API_KEY") or "").strip()

    logger.info("STT env check groq=%s", bool(groq_key))

    if not groq_key:
        raise RuntimeError("STT_GROQ_API_KEY_MISSING")

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {groq_key}"}
    model = "whisper-large-v3-turbo"

    size = os.path.getsize(path)
    logger.info("STT start file=%s size=%s model=%s", path, size, model)

    data = aiohttp.FormData()
    data.add_field("model", model)
    data.add_field("response_format", "json")

    with open(path, "rb") as f:
        data.add_field("file", f, filename=os.path.basename(path), content_type="audio/ogg")
        async with aiohttp.ClientSession() as s:
            r = await s.post(
                url,
                headers=headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=300)
            )
            body = await r.text()
            logger.info("STT http_status=%s", r.status)

            if r.status != 200:
                logger.error("STT body=%s", body[:500])
                raise RuntimeError(f"STT_GROQ_FAILED: {r.status} {body[:300]}")

            try:
                js = json.loads(body)
            except Exception:
                raise RuntimeError(f"STT bad json: {body[:300]}")

    text = (js.get("text") or "").strip()

    if not text:
        raise RuntimeError("STT returned empty transcript")

    # === P6H_STT_HALLUCINATION_GUARD_V1 ===
    _stt_hall_patterns = (
        "субтитры", "субтитр", "titl", "продолжение следует",
        "конец видео", "спасибо за просмотр", "подписывайтесь",
        "thank you", "amara.org", "translated by", "caption",
    )
    _stt_low = text.lower()
    if len(text) <= 6 or any(p in _stt_low for p in _stt_hall_patterns):
        logger.warning("STT_HALLUCINATION_GUARD: rejected=%r", text[:80])
        raise RuntimeError(f"STT_HALLUCINATION_REJECTED: {text[:60]!r}")
    # === END_P6H_STT_HALLUCINATION_GUARD_V1 ===

    logger.info("STT ok transcript_len=%s", len(text))

    try:
        os.remove(path)
    except Exception:
        pass

    return text
