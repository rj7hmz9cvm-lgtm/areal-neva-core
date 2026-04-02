from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv("/root/.areal-neva-core/.env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

class VoiceEngine:
    def transcribe(self, path: str) -> Dict[str, Any]:
        p = Path(str(path or "").strip())
        if not p.is_file():
            return {
                "status": "error",
                "engine": "voice",
                "error": "file_not_found",
                "path": str(p),
                "text": "",
            }

        if not GROQ_API_KEY:
            return {
                "status": "error",
                "engine": "voice",
                "error": "GROQ_API_KEY_missing",
                "path": str(p),
                "text": "",
            }

        try:
            with p.open("rb") as f:
                r = requests.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                    },
                    data={
                        "model": "whisper-large-v3-turbo",
                        "response_format": "json",
                        "language": "ru",
                        "temperature": "0",
                    },
                    files={
                        "file": (p.name, f, "application/octet-stream"),
                    },
                    timeout=120,
                )
            r.raise_for_status()
            data = r.json()
            text = str(data.get("text") or "").strip()

            return {
                "status": "done",
                "engine": "voice",
                "path": str(p),
                "text": text,
                "raw": data,
            }
        except Exception as e:
            return {
                "status": "error",
                "engine": "voice",
                "error": str(e),
                "path": str(p),
                "text": "",
            }
