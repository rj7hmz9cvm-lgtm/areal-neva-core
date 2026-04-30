import os, json, base64, mimetypes, urllib.request, urllib.error
from pathlib import Path
from typing import Optional

GEMINI_MODEL = os.getenv("GOOGLE_GEMINI_VISION_MODEL", "gemini-2.0-flash")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp", ".gif", ".tif", ".tiff"}

def is_image_path(path: str) -> bool:
    return Path(str(path)).suffix.lower() in IMAGE_SUFFIXES

def _get_key() -> str:
    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if key:
        return key
    env = Path("/root/.areal-neva-core/.env")
    if env.exists():
        for line in env.read_text(errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip().replace("export ", "") == "GOOGLE_API_KEY":
                v = v.strip().strip("'\"")
                if v:
                    return v
    raise RuntimeError("GOOGLE_API_KEY_MISSING")

def _mime(p: Path) -> str:
    mt, _ = mimetypes.guess_type(str(p))
    if mt:
        return mt
    s = p.suffix.lower().lstrip(".")
    return {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(s, "image/jpeg")

async def analyze_image_file(path: str, prompt: Optional[str] = None, timeout: int = 60) -> str:
    p = Path(str(path))
    if not p.exists():
        raise RuntimeError(f"FILE_NOT_FOUND:{p}")
    key = _get_key()
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    text = (prompt or "").strip() or (
        "Проанализируй изображение для строительной или проектной задачи. "
        "Опиши что видно, извлеки размеры, таблицы, обозначения если есть. "
        "Укажи риски и следующий практический шаг. Кратко, технически, по фактам."
    )
    payload = {
        "contents": [{"role": "user", "parts": [
            {"text": text},
            {"inline_data": {"mime_type": _mime(p), "data": data}},
        ]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048},
    }
    url = GEMINI_URL.format(model=GEMINI_MODEL) + "?key=" + key
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            obj = json.loads(r.read().decode("utf-8", errors="ignore"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GEMINI_HTTP_{e.code}:{e.read().decode()[:500]}")
    parts = obj.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    result = "\n".join(x.get("text", "") for x in parts if x.get("text")).strip()
    if not result:
        raise RuntimeError("GEMINI_EMPTY_RESULT")
    return result
