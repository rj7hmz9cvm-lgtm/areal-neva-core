import os
import json
import mimetypes
from pathlib import Path

SYS_PROMPT = """Return ONLY valid JSON with exact schema:
{
  "summary": "Brief overall description",
  "detected_elements": ["item1", "item2"],
  "defects": ["defect1", "defect2"],
  "recommendations": ["rec1", "rec2"]
}
No markdown
No extra text
"""

def _extract_json(raw_text: str) -> dict:
    raw = str(raw_text or "").strip()
    try:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(raw[start:end + 1])
    except Exception:
        pass
    return {
        "summary": raw[:1000],
        "detected_elements": [],
        "defects": [],
        "recommendations": [],
    }

def _detect_media_type(file_path: str) -> str:
    guessed, _ = mimetypes.guess_type(file_path)
    return guessed or "application/octet-stream"

async def _call_gemini(file_path: str, prompt: str, model_name: str) -> str:
    try:
        import google.generativeai as genai
    except Exception as e:
        return f"VISION_ERROR: GEMINI_SDK_IMPORT_FAILED: {e}"

    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        return "VISION_ERROR: GOOGLE_API_KEY_MISSING"

    try:
        genai.configure(api_key=api_key)
        uploaded = genai.upload_file(file_path)
        model = genai.GenerativeModel(model_name)
        response = await model.generate_content_async(
            [uploaded, SYS_PROMPT + "\nUser request: " + str(prompt or "")]
        )
        return json.dumps(
            {
                "status": "ok",
                "engine": model_name,
                "data": _extract_json(getattr(response, "text", "") or ""),
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return f"VISION_ERROR: GEMINI_FAILED: {e}"

async def _call_claude(file_path: str, prompt: str) -> str:
    try:
        import base64
        import anthropic
    except Exception as e:
        return f"VISION_ERROR: ANTHROPIC_SDK_IMPORT_FAILED: {e}"

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return "VISION_ERROR: ANTHROPIC_API_KEY_MISSING"

    media_type = _detect_media_type(file_path)
    model_name = os.getenv("VISION_FALLBACK", "claude-3-5-sonnet-20241022")

    try:
        client = anthropic.AsyncAnthropic(api_key=api_key)
        data_b64 = base64.b64encode(Path(file_path).read_bytes()).decode("utf-8")
        response = await client.messages.create(
            model=model_name,
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document" if media_type == "application/pdf" else "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": data_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": SYS_PROMPT + "\nUser request: " + str(prompt or ""),
                        },
                    ],
                }
            ],
        )
        text_out = "".join(
            [b.text for b in response.content if getattr(b, "type", "") == "text"]
        )
        return json.dumps(
            {
                "status": "ok",
                "engine": model_name,
                "data": _extract_json(text_out),
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return f"VISION_ERROR: CLAUDE_FAILED: {e}"

async def process_vision(file_path: str, prompt: str, complexity: str = "simple") -> str:
    if os.getenv("VISION_ENABLED", "0") != "1":
        return "SYS_SKIP: VISION_DISABLED"

    if not file_path or not os.path.exists(file_path):
        return "VISION_ERROR: FILE_NOT_FOUND"

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > float(os.getenv("MAX_VISION_MB", "15")):
        return f"SYS_SKIP: FILE_TOO_LARGE ({size_mb:.1f}MB)"

    comp = str(complexity or "simple").lower().strip()

    if comp == "simple":
        result = await _call_gemini(file_path, prompt, os.getenv("VISION_DEFAULT", "gemini-2.0-flash-lite"))
        if not str(result).startswith("VISION_ERROR:"):
            return result
        return await _call_gemini(file_path, prompt, os.getenv("VISION_UPGRADE", "gemini-2.0-flash"))

    if comp == "medium":
        result = await _call_gemini(file_path, prompt, os.getenv("VISION_UPGRADE", "gemini-2.0-flash"))
        if not str(result).startswith("VISION_ERROR:"):
            return result
        return await _call_claude(file_path, prompt)

    return await _call_claude(file_path, prompt)
