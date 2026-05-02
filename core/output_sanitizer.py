# === UNIFIED_USER_OUTPUT_SANITIZER_V4_NO_SERVICE_JUNK ===
from __future__ import annotations

import re
from typing import Any

SERVICE_LINE_RE = [
    r"^\s*engine\s*:",
    r"^\s*kind\s*:",
    r"^\s*source\s*:",
    r"^\s*status\s*:",
    r"^\s*type\s*:\s*[A-Z_]{4,}",
    r"^\s*тип\s*:\s*[A-Z_]{4,}",
    r"^\s*task\s*:",
    r"^\s*task_id\s*:",
    r"^\s*задача\s*:\s*[0-9a-fA-F-]{6,}",
    r"^\s*drive\s+file_id\s*:",
    r"^\s*file_id\s*:",
    r"^\s*chat_id\s*:",
    r"^\s*topic_id\s*:",
    r"^\s*manifest\s*:",
    r"^\s*dxf\s*:",
    r"^\s*xlsx\s*:",
    r"^\s*xls\s*:",
    r"^\s*pdf\s*:",
    r"^\s*docx\s*:",
    r"^\s*artifact\s*:",
    r"^\s*artifact_path\s*:",
    r"^\s*validator_reason\s*:",
    r"^\s*raw_result\s*:",
    r"^\s*raw_payload\s*:",
    r"^\s*raw_input\s*:",
    r"^\s*debug\s*:",
    r"^\s*traceback\s*:",
    r"^\s*stacktrace\s*:",
    r"^\s*tmp_path\s*:",
    r"^\s*кратко\s*:\s*\{",
    r"^\s*кратко\s*:\s*\[",
    r"^\s*google sheets\s*/\s*xlsx\s*артефакт\s*$",
]

SERVICE_SUBSTRINGS = [
    "/root/.areal-neva-core",
    "/root/",
    "/tmp/",
    "file_context_intake.py",
    "file_memory_bridge.py",
    "price_enrichment.py",
    "sample_template_engine.py",
    "task_worker.py",
    "telegram_daemon.py",
    "artifact_pipeline.py",
    "engine_base.py",
    "PROJECT_TEMPLATE_MODEL__",
    "ACTIVE__chat_",
    "ACTIVE_BATCH__chat_",
    "PENDING__chat_",
    "FINAL_CLOSURE_BLOCKER_FIX_V1",
    "UNIFIED_USER_OUTPUT_SANITIZER",
    "validator_reason",
    "internal_key",
    "raw_payload",
    "raw_input_json",
    "ModuleNotFoundError",
    "SyntaxError",
    "Traceback",
]

NOISE_EXACT = {
    "доволен",
    "недоволен",
    "готово",
}

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    return str(v)

def _normalize_escaped_text(text: Any) -> str:
    src = _s(text)
    src = src.replace("\r", "\n")
    src = src.replace("\\\\n", "\n")
    src = src.replace("\\n", "\n")
    src = src.replace("\\\\t", " ")
    src = src.replace("\\t", " ")
    src = src.replace('\\"', '"')
    src = re.sub(r"\x00+", " ", src)
    return src

def _is_google_link(text: str) -> bool:
    low = text.lower()
    return "https://drive.google.com/" in low or "https://docs.google.com/" in low

def _clean_google_link(line: str) -> str:
    m = re.search(r"https://(?:drive|docs)\.google\.com/[^\s\"'<>()]+", line, re.I)
    if not m:
        return line.strip()
    url = m.group(0)
    url = re.split(r"(?:PDF|DXF|XLSX|XLS|DOCX|MANIFEST)\s*:", url, flags=re.I)[0]
    url = url.rstrip(".,;)")
    return url

def _bad_line(line: str) -> bool:
    raw = line.strip()
    low = raw.lower()

    if not raw:
        return False

    if low in NOISE_EXACT:
        return True

    if re.fullmatch(r"[-–—]?\s*$", raw):
        return True

    for p in SERVICE_LINE_RE:
        if re.search(p, raw, re.I):
            return True

    if re.match(r"^\s*[-–—]\s*(dxf|xlsx|xls|pdf|docx|manifest)\s*:\s*$", raw, re.I):
        return True

    if re.search(r"\{[^{}]*(task_id|chat_id|topic_id|file_id|caption|engine)[^{}]*\}", raw, re.I):
        return True

    if raw.startswith("{") and raw.endswith("}"):
        return True

    for s in SERVICE_SUBSTRINGS:
        if s.lower() in low:
            return True

    if re.search(r"\b[A-Z_]{6,}_V\d+\b", raw) and not _is_google_link(raw):
        return True

    return False

def sanitize_user_output(text: Any, fallback: str = "Готово") -> str:
    src = _normalize_escaped_text(text)
    if not src.strip():
        return fallback

    lines = []
    skip_next_google_link = False

    for original in src.split("\n"):
        line = original.rstrip()

        if re.match(r"^\s*manifest\s*:\s*$", line, re.I):
            skip_next_google_link = True
            continue

        if skip_next_google_link and _is_google_link(line):
            skip_next_google_link = False
            continue

        if _is_google_link(line):
            clean_url = _clean_google_link(line)
            if "manifest" in clean_url.lower() or clean_url.lower().endswith(".json"):
                continue
            lines.append(clean_url)
            skip_next_google_link = False
            continue

        skip_next_google_link = False

        if _bad_line(line):
            continue

        lines.append(line)

    out = "\n".join(lines)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    out = re.sub(r"[ \t]{2,}", " ", out)

    if not out:
        out = fallback

    if len(out) > 3900:
        out = out[:3800].rstrip() + "\n\nТекст сокращён. Полный результат смотри в файле"

    return out

def sanitize_project_message(text: Any) -> str:
    return sanitize_user_output(text, fallback="Проектный результат подготовлен")

def sanitize_estimate_message(text: Any) -> str:
    return sanitize_user_output(text, fallback="Сметный результат подготовлен")

# === END_UNIFIED_USER_OUTPUT_SANITIZER_V4_NO_SERVICE_JUNK ===
