import os
import requests

async def process_audio(file_path: str, use_diarization: bool = False):
    if os.getenv("AUDIO_ENABLED", "0") != "1":
        return {"status": "skip", "error": "SYS_SKIP: AUDIO_DISABLED"}

    if not file_path or not os.path.exists(file_path):
        return {"status": "error", "error": "AUDIO_ERROR: FILE_NOT_FOUND"}

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > float(os.getenv("MAX_AUDIO_MB", "25")):
        return {"status": "skip", "error": f"SYS_SKIP: AUDIO_TOO_LARGE ({size_mb:.1f}MB)"}

    base_url = os.getenv("AUDIO_API_BASE_URL", "https://api.groq.com/openai/v1/audio/transcriptions").strip()
    if "groq.com" in base_url:
        api_key = os.getenv("GROQ_API_KEY", "").strip()
    elif "openai.com" in base_url:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
    else:
        api_key = os.getenv("AUDIO_API_KEY", "").strip() or os.getenv("OPENAI_API_KEY", "").strip()

    model = os.getenv("AUDIO_API_MODEL", "whisper-large-v3-turbo").strip()

    if not api_key:
        result = {"status": "error", "mode": "api", "error": "AUDIO_API_KEY_MISSING"}
    else:
        try:
            with open(file_path, "rb") as fh:
                r = requests.post(
                    base_url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    data={"model": model},
                    files={"file": fh},
                    timeout=120,
                )
                r.raise_for_status()
                payload = r.json()
                result = {
                    "status": "ok",
                    "mode": "api",
                    "transcription": payload.get("text", "") if isinstance(payload, dict) else str(payload),
                }
        except Exception as e:
            result = {"status": "error", "mode": "api", "error": f"AUDIO_API_ERROR: {e}"}

    if use_diarization and os.getenv("PYANNOTE_ENABLED", "0") == "1" and os.getenv("HUGGINGFACE_TOKEN", "").strip():
        result["diarization"] = "TODO_PYANNOTE_RESULT"
    elif use_diarization:
        result["diarization_skip"] = "SYS_SKIP: PYANNOTE_DISABLED_OR_TOKEN_MISSING"

    return result
