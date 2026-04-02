from pathlib import Path
import os

_MODEL = None

def transcribe_audio(path: str) -> str:
    global _MODEL
    p = Path(path)
    if not p.exists() or p.stat().st_size <= 0:
        return ""
    try:
        import whisper
        if _MODEL is None:
            _MODEL = whisper.load_model(os.getenv("WHISPER_MODEL", "base"))
        result = _MODEL.transcribe(str(p), fp16=False)
        return (result.get("text") or "").strip()
    except Exception:
        return ""
