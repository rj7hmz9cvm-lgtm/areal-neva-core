# === UNIFIED_USER_OUTPUT_SANITIZER_V1 ===
from __future__ import annotations

import re
from typing import Any

FORBIDDEN_LINE_PATTERNS = [
    r"^\s*Engine\s*:",
    r"^\s*MANIFEST\s*:",
    r"^\s*manifest\s*:",
    r"^\s*Artifact\s*:",
    r"^\s*artifact_path\s*:",
    r"^\s*validator_reason\s*:",
    r"^\s*internal[_ -]?keys?\s*:",
    r"^\s*raw_result\s*:",
    r"^\s*debug\s*:",
    r"^\s*traceback\s*:",
    r"^\s*stacktrace\s*:",
    r"^\s*tmp_path\s*:",
]

FORBIDDEN_SUBSTRINGS = [
    "/root/.areal-neva-core",
    "/root/",
    "/tmp/",
    "file_context_intake.py",
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
    "validator_reason",
    "internal_key",
    "raw_payload",
    "raw_input_json",
    "traceback",
    "ModuleNotFoundError",
    "SyntaxError",
]

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    return str(v)

def _is_drive_line(line: str) -> bool:
    low = line.lower()
    return "https://drive.google.com/" in low or "https://docs.google.com/" in low

def _bad_line(line: str) -> bool:
    if _is_drive_line(line):
        return False
    for p in FORBIDDEN_LINE_PATTERNS:
        if re.search(p, line, re.I):
            return True
    low = line.lower()
    for s in FORBIDDEN_SUBSTRINGS:
        if s.lower() in low:
            return True
    if re.search(r"\b[A-Z_]{6,}_V\d+\b", line) and not _is_drive_line(line):
        return True
    if re.search(r"\{[^{}]*\"engine\"[^{}]*\}", line, re.I):
        return True
    return False

def sanitize_user_output(text: Any, fallback: str = "Готово") -> str:
    src = _s(text).replace("\r", "\n")
    if not src.strip():
        return fallback

    src = re.sub(r"\x00+", " ", src)
    lines = []
    for line in src.split("\n"):
        clean = line.rstrip()
        if _bad_line(clean):
            continue
        lines.append(clean)

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

# === END_UNIFIED_USER_OUTPUT_SANITIZER_V1 ===
