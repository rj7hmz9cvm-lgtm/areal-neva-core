#!/usr/bin/env python3
# === FULL_CONTEXT_AGGREGATOR_V1 ===
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
OUTPUT_DIR = BASE / "docs/SHARED_CONTEXT"
REPO = "rj7hmz9cvm-lgtm/areal-neva-core"
RAW_MAIN = f"https://raw.githubusercontent.com/{REPO}/main"
LOCK_PATH = Path("/tmp/areal_full_context_aggregator.lock")
PART_MAX_BYTES = 400_000
CONTENT_CHUNK_BYTES = 340_000

TEXT_SUFFIXES = {
    ".py", ".md", ".json", ".yaml", ".yml", ".sh", ".txt", ".service", ".timer",
    ".conf", ".ini", ".toml", ".sql", ".csv", ".gitignore", ".dockerignore",
}
TEXT_NAMES = {".gitignore", ".dockerignore", "Dockerfile", "Makefile"}

SECRET_PATH_PARTS = {
    ".env", ".secret_patterns", "token.json", "credentials.json", "client_secret.json",
}
SECRET_PATH_FRAGMENTS = (
    "service_account",
    "client_secret",
    "private_key",
    "credentials",
    "/sessions/",
    "/keys/",
)
BINARY_SUFFIXES = {
    ".session", ".db", ".sqlite", ".sqlite3", ".pdf", ".dwg", ".dxf", ".jpg", ".jpeg",
    ".png", ".mp4", ".mov", ".webp", ".gif", ".ico", ".pyc", ".pyo", ".so", ".o",
    ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar", ".xlsx", ".xls", ".docx", ".doc",
}
SKIP_DIR_PARTS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".mypy_cache", ".pytest_cache"}

GENERATED_EXACT = {
    "docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md",
    "docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md",
    "docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md",
    "docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md",
    "docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md",
    "docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md",
    "docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md",
    "docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md",
    "docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json",
}

GENERATED_PREFIXES = (
    "docs/SHARED_CONTEXT/TOPICS/",
    "docs/SHARED_CONTEXT/DIRECTIONS/",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_",
)

# === FULL_CONTEXT_NOISE_EXCLUDE_V1 ===
# One-time operational logs are excluded from model context parts
# Canon, handoffs, NOT_CLOSED, code, configs and useful reports remain included fully
NOISE_PATH_FRAGMENTS = (
    "DRIVE_AI_ORCHESTRA_ROOT_CLEANUP",
    "DRIVE_AI_ORCHESTRA_ROOT_FOLDER_FINAL_CLEAN",
    "CLAUDE_BOOTSTRAP_PENDING_PUSH",
)
# === END_FULL_CONTEXT_NOISE_EXCLUDE_V1 ===

PRIORITY_PREFIXES = [
    "docs/HANDOFFS/LATEST_HANDOFF",
    "docs/REPORTS/NOT_CLOSED",
    "docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL",
    "docs/CANON_FINAL/",
    "docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK",
    "docs/ARCHITECTURE/SEARCH_MONOLITH",
    "docs/ARCHITECTURE/",
    "docs/HANDOFFS/",
    "docs/REPORTS/",
    "chat_exports/",
    "config/",
    "task_worker.py",
    "telegram_daemon.py",
    "core/project_route_guard.py",
    "core/final_closure_engine.py",
    "core/file_context_intake.py",
    "core/reply_repeat_parent.py",
    "core/estimate_engine.py",
    "core/project_engine.py",
    "core/file_intake_router.py",
    "core/ai_router.py",
    "core/",
    "tools/full_context_aggregator.py",
    "tools/context_aggregator.py",
    "tools/claude_bootstrap_aggregator.py",
    "tools/",
]

TOPIC_REGISTRY = """TOPIC_REGISTRY:
topic_0=CHAT_ZADACH: общий чат
topic_2=STROYKA: estimate_engine, Excel =C*D =SUM, Python считает, LLM не считает
topic_5=TEKHNADZOR: technadzor_engine, Gemini vision, нормы СП/ГОСТ без выдумывания
topic_11=VIDEOKONTENT
topic_210=PROEKTIROVANIE: project_engine, PROJECT_TEMPLATE_MODEL, не OCR текст
topic_500=VEB_POISK: только Perplexity, 14 этапов, file-context/file-menu запрещены
topic_794=NEJRONKI_SOFT_VPN_VPS
topic_961=AVTO_ZAPCHASTI: OEM, Exist/Drom/Emex
topic_3008=KODY_MOZGOV: верификация кода, No Auto-Patch
topic_4569=LIDY_REKLAMA_AMO
topic_6104=RABOTA_POISK"""

PROTOCOL = """OPERATING_PROTOCOL:
MODE: FACT_ONLY / ZERO_ASSUMPTIONS / GITHUB_SSOT / CANON_LOCK
ONE_LINK_GOAL: модель читает MODEL_BOOTSTRAP_CONTEXT.md и сразу получает всю картину
PATCH_ORDER: DIAGNOSTICS → BAK → PATCH → PY_COMPILE → RESTART → LOGS → DB_VERIFY → GIT_PUSH → FINAL_VERIFY
FORBIDDEN: .env, credentials, token, sessions, raw DB dumps, rm -rf project/canon dirs
CONTEXT_RULE: разрешённые текстовые файлы включаются полностью без обрезки
BIG_TEXT_RULE: большие текстовые файлы дробятся по PART-файлам, не режутся
SECRET_RULE: секретные значения редактируются как <REDACTED_SECRET>
STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test"""

SECRET_VALUE_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
    re.compile(r"github_pat_[A-Za-z0-9_]{50,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{30,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_\-]{30,}\b"),
    re.compile(r"1//[A-Za-z0-9_\-]{20,}"),
    re.compile(r'("private_key"\s*:\s*")[^"]+(")'),
    re.compile(r'((?:API_KEY|TOKEN|SECRET|PASSWORD)\s*=\s*)[^\s\'"]+', re.I),
]


def run(cmd: list[str], check: bool = False) -> str:
    p = subprocess.run(cmd, cwd=str(BASE), text=True, capture_output=True)
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    if check and p.returncode != 0:
        raise RuntimeError(f"CMD_FAIL: {' '.join(cmd)}\n{out}")
    return out


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize_text(text: str) -> str:
    out = text
    for pat in SECRET_VALUE_PATTERNS:
        if pat.pattern.startswith('("private_key"'):
            out = pat.sub(r'\1<REDACTED_SECRET>\2', out)
        elif "(?:API_KEY|TOKEN|SECRET|PASSWORD)" in pat.pattern:
            out = pat.sub(r"\1<REDACTED_SECRET>", out)
        else:
            out = pat.sub("<REDACTED_SECRET>", out)
    return out


def is_generated_output(rel: str) -> bool:
    if rel in GENERATED_EXACT:
        return True
    return any(rel.startswith(p) for p in GENERATED_PREFIXES)


def classify_path(rel: str) -> tuple[str, str]:
    low = rel.lower()
    parts = set(Path(rel).parts)
    name = Path(rel).name
    suffix = Path(rel).suffix.lower()

    if is_generated_output(rel):
        return "excluded_generated_output", "generated output avoids self-ingestion"
    if any(x in rel for x in NOISE_PATH_FRAGMENTS):
        return "excluded_noise_report", "operational one-time report excluded from model context"
    if any(x in parts for x in SKIP_DIR_PARTS):
        return "excluded_dir", "runtime/cache/git dir"
    if name in SECRET_PATH_PARTS:
        return "excluded_secret_path", "secret path"
    if any(x in low for x in SECRET_PATH_FRAGMENTS):
        return "excluded_secret_path", "secret path fragment"
    if ".bak" in low or low.endswith(".bak") or ".bak_" in low:
        return "excluded_backup", "backup file"
    if suffix in BINARY_SUFFIXES:
        return "excluded_binary", "binary/raw db/heavy media"
    if suffix in TEXT_SUFFIXES or name in TEXT_NAMES:
        return "full", "tracked text"
    return "excluded_non_text", "suffix not allowlisted"


def sort_key(rel: str) -> tuple[int, str]:
    for i, p in enumerate(PRIORITY_PREFIXES):
        if rel.startswith(p) or p in rel:
            return (i, rel)
    return (len(PRIORITY_PREFIXES), rel)


def git_tracked_files() -> list[str]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=str(BASE))
    files = [x for x in raw.decode("utf-8", errors="replace").split("\0") if x]
    for extra in (
        "tools/full_context_aggregator.py",
        "tools/claude_bootstrap_aggregator.py",
    ):
        if (BASE / extra).exists() and extra not in files:
            files.append(extra)
    return sorted(set(files), key=sort_key)


def collect_files() -> tuple[list[dict], list[dict]]:
    full_items: list[dict] = []
    manifest_items: list[dict] = []

    for rel in git_tracked_files():
        mode, reason = classify_path(rel)
        p = BASE / rel
        size = p.stat().st_size if p.exists() else 0

        record = {
            "path": rel,
            "mode": mode,
            "reason": reason,
            "size_bytes": size,
            "sha256": "",
            "chars": 0,
            "chunks": 0,
        }

        if mode != "full":
            manifest_items.append(record)
            continue

        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            text = sanitize_text(text)
            record["sha256"] = sha256_text(text)
            record["chars"] = len(text)
            full_items.append({"path": rel, "content": text, "record": record})
        except Exception as e:
            record["mode"] = "read_error"
            record["reason"] = str(e)
        manifest_items.append(record)

    return full_items, manifest_items


def split_text_by_bytes(text: str, limit: int) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_size = 0

    for line in text.splitlines(True):
        b = len(line.encode("utf-8", errors="replace"))
        if current and current_size + b > limit:
            chunks.append("".join(current))
            current = []
            current_size = 0

        if b > limit:
            data = line.encode("utf-8", errors="replace")
            for i in range(0, len(data), limit):
                chunks.append(data[i:i + limit].decode("utf-8", errors="replace"))
            continue

        current.append(line)
        current_size += b

    if current:
        chunks.append("".join(current))
    return chunks or [""]


def build_file_blocks(full_items: list[dict]) -> tuple[list[str], dict[str, int]]:
    blocks: list[str] = []
    chunk_counts: dict[str, int] = {}

    for item in full_items:
        rel = item["path"]
        content = item["content"]
        chunks = split_text_by_bytes(content, CONTENT_CHUNK_BYTES)
        chunk_counts[rel] = len(chunks)
        for idx, chunk in enumerate(chunks, 1):
            header = (
                "\n" + "=" * 100 + "\n"
                f"BEGIN_FILE: {rel}\n"
                f"FILE_CHUNK: {idx}/{len(chunks)}\n"
                f"SHA256_FULL_FILE: {sha256_text(content)}\n"
                + "=" * 100 + "\n"
            )
            footer = (
                "\n" + "=" * 100 + "\n"
                f"END_FILE: {rel}\n"
                f"FILE_CHUNK: {idx}/{len(chunks)}\n"
                + "=" * 100 + "\n"
            )
            blocks.append(header + chunk + footer)
    return blocks, chunk_counts


def split_blocks_to_parts(blocks: list[str]) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    size = 0

    for block in blocks:
        bsize = len(block.encode("utf-8", errors="replace"))
        if current and size + bsize > PART_MAX_BYTES:
            parts.append("".join(current))
            current = []
            size = 0
        current.append(block)
        size += bsize

    if current:
        parts.append("".join(current))
    return parts


def sql_rows(db: Path, query: str, limit: int = 20) -> list[str]:
    try:
        if not db.exists():
            return ["DB_NOT_FOUND"]
        con = sqlite3.connect(str(db))
        rows = con.execute(query).fetchmany(limit)
        con.close()
        return ["|".join(str(x) for x in r) for r in rows]
    except Exception as e:
        return [f"SQL_ERROR:{e}"]


def build_runtime_snapshot(git_sha: str) -> str:
    core_db = BASE / "data/core.db"
    mem_db = BASE / "data/memory.db"
    lines: list[str] = []

    lines.append("# SAFE_RUNTIME_SNAPSHOT")
    lines.append(f"generated_at_utc: {utc_now()}")
    lines.append(f"git_sha_before_commit: {git_sha}")
    lines.append(f"git_branch: {run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])}")
    lines.append("")
    lines.append("## SERVICES")
    for svc in (
        "areal-task-worker",
        "telegram-ingress",
        "areal-memory-api",
        "areal-claude-bootstrap-aggregator.timer",
    ):
        lines.append(f"- {svc}: {run(['systemctl', 'is-active', svc])}")
    lines.append("")
    lines.append("## GIT_LOG_30")
    lines.append(run(["git", "log", "--oneline", "-30"]))
    lines.append("")
    lines.append("## GIT_SHOW_STAT_HEAD")
    lines.append(run(["git", "show", "--stat", "HEAD"]))
    lines.append("")
    lines.append("## GIT_CHANGED_FILES_10")
    lines.append(run(["git", "diff", "--name-only", "HEAD~10..HEAD"]))
    lines.append("")
    lines.append("## CORE_DB_STATE_COUNTS")
    lines.extend(f"- {x}" for x in sql_rows(core_db, "SELECT state,COUNT(*) FROM tasks GROUP BY state ORDER BY 2 DESC"))
    lines.append("")
    lines.append("## CORE_DB_OPEN_TASKS")
    lines.extend(f"- {x}" for x in sql_rows(core_db, "SELECT COUNT(*) FROM tasks WHERE state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')"))
    lines.append("")
    lines.append("## LATEST_TASKS_15")
    lines.extend(f"- {x}" for x in sql_rows(core_db, "SELECT id,COALESCE(topic_id,0),input_type,state,substr(raw_input,1,120),substr(result,1,160),updated_at FROM tasks ORDER BY rowid DESC LIMIT 15", 15))
    lines.append("")
    lines.append("## LATEST_FAILED_10")
    lines.extend(f"- {x}" for x in sql_rows(core_db, "SELECT id,COALESCE(topic_id,0),substr(raw_input,1,120),substr(error_message,1,160),updated_at FROM tasks WHERE state='FAILED' ORDER BY rowid DESC LIMIT 10", 10))
    lines.append("")
    lines.append("## LATEST_TASK_HISTORY_20")
    lines.extend(f"- {x}" for x in sql_rows(core_db, "SELECT task_id,substr(action,1,180),created_at FROM task_history ORDER BY id DESC LIMIT 20", 20))
    lines.append("")
    lines.append("## MEMORY_DB_COUNT")
    lines.extend(f"- {x}" for x in sql_rows(mem_db, "SELECT COUNT(*) FROM memory"))
    lines.append("")
    lines.append("## LATEST_MEMORY_20")
    lines.extend(f"- {x}" for x in sql_rows(mem_db, "SELECT key,substr(value,1,180),timestamp FROM memory ORDER BY timestamp DESC LIMIT 20", 20))
    lines.append("")
    lines.append("## JOURNAL_AREAL_TASK_WORKER_60")
    lines.append(sanitize_text(run(["journalctl", "-u", "areal-task-worker", "-n", "60", "--no-pager", "--output=cat"])))
    lines.append("")
    lines.append("## JOURNAL_TELEGRAM_INGRESS_30")
    lines.append(sanitize_text(run(["journalctl", "-u", "telegram-ingress", "-n", "30", "--no-pager", "--output=cat"])))
    return "\n".join(lines).rstrip() + "\n"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"WRITTEN {path.relative_to(BASE)} {len(content.encode('utf-8'))} bytes")


def cleanup_old_parts() -> None:
    for p in OUTPUT_DIR.glob("ORCHESTRA_FULL_CONTEXT_PART_*.md"):
        p.unlink()


def build_manifest(records: list[dict], chunk_counts: dict[str, int], git_sha: str, parts_count: int) -> str:
    out_records = []
    for r in records:
        rr = dict(r)
        rr["chunks"] = chunk_counts.get(r["path"], 0)
        out_records.append(rr)

    data = {
        "generated_at_utc": utc_now(),
        "git_sha_before_commit": git_sha,
        "part_max_bytes": PART_MAX_BYTES,
        "content_chunk_bytes": CONTENT_CHUNK_BYTES,
        "total_records": len(out_records),
        "included_full_files": sum(1 for r in out_records if r["mode"] == "full"),
        "excluded_records": sum(1 for r in out_records if r["mode"] != "full"),
        "parts_count": parts_count,
        "raw_main": RAW_MAIN,
        "outputs": {
            "model_bootstrap": f"{RAW_MAIN}/docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md",
            "claude_alias": f"{RAW_MAIN}/docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md",
            "one_shared": f"{RAW_MAIN}/docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md",
            "runtime": f"{RAW_MAIN}/docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md",
            "full_context_index": f"{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md",
            "manifest": f"{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json",
            "single_model_source": f"{RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md",
            "single_model_full_context": f"{RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md",
            "topic_status_index": f"{RAW_MAIN}/docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md",
            "direction_status_index": f"{RAW_MAIN}/docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md",
            "topics_dir": f"{RAW_MAIN}/docs/SHARED_CONTEXT/TOPICS/",
            "directions_dir": f"{RAW_MAIN}/docs/SHARED_CONTEXT/DIRECTIONS/",
            "parts": [
                f"{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md"
                for i in range(1, parts_count + 1)
            ],
        },
        "files": out_records,
    }
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def build_context_index(git_sha: str, parts_count: int, records: list[dict]) -> str:
    parts_links = "\n".join(
        f"- PART_{i:03d}: {RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md"
        for i in range(1, parts_count + 1)
    )
    return f"""# ORCHESTRA_FULL_CONTEXT

generated_at_utc: {utc_now()}
git_sha_before_commit: {git_sha}
parts_count: {parts_count}
included_full_files: {sum(1 for r in records if r["mode"] == "full")}
excluded_records: {sum(1 for r in records if r["mode"] != "full")}

{PROTOCOL}

{TOPIC_REGISTRY}

## FULL_CONTEXT_PARTS
{parts_links}

## MANIFEST
{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json

## RUNTIME
{RAW_MAIN}/docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md

## STATUS_INDEX
FIRST_READ_SINGLE_MODEL_SOURCE: {RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md
FIRST_READ_TOPIC_STATUS: {RAW_MAIN}/docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md
FIRST_READ_DIRECTION_STATUS: {RAW_MAIN}/docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md
"""


def build_model_bootstrap(git_sha: str, parts_count: int, manifest_sha: str) -> str:
    parts_links = "\n".join(
        f"- PART_{i:03d}: {RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md"
        for i in range(1, parts_count + 1)
    )
    return f"""# MODEL_BOOTSTRAP_CONTEXT

SYSTEM: AREAL-NEVA ORCHESTRA
GENERATED_AT_UTC: {utc_now()}
GIT_SHA_BEFORE_COMMIT: {git_sha}
MODE: FACT_ONLY / ZERO_ASSUMPTIONS / GITHUB_SSOT / CANON_LOCK
NO_TRUNCATION: TRUE
TEXT_FILES_INCLUDED_FULLY: TRUE
BIG_FILES_SPLIT_TO_PARTS: TRUE
MANIFEST_SHA256: {manifest_sha}

RAW_THIS_FILE:
{RAW_MAIN}/docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md

CLAUDE_ALIAS:
{RAW_MAIN}/docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md

IF_UNAVAILABLE:
MODEL_BOOTSTRAP_CONTEXT_UNAVAILABLE

{PROTOCOL}

{TOPIC_REGISTRY}

## READ_ORDER
1. This MODEL_BOOTSTRAP_CONTEXT
2. SINGLE_MODEL_SOURCE
3. TOPIC_STATUS_INDEX
4. DIRECTION_STATUS_INDEX
5. Required topic/direction file from TOPICS/ or DIRECTIONS/
6. SAFE_RUNTIME_SNAPSHOT
7. ORCHESTRA_FULL_CONTEXT_MANIFEST
8. ORCHESTRA_FULL_CONTEXT_PART_XXX only if needed

## RAW_LINKS
SINGLE_MODEL_SOURCE:
{RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md

TOPIC_STATUS_INDEX:
{RAW_MAIN}/docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md

DIRECTION_STATUS_INDEX:
{RAW_MAIN}/docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md

SAFE_RUNTIME_SNAPSHOT:
{RAW_MAIN}/docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md

ORCHESTRA_FULL_CONTEXT_INDEX:
{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md

ORCHESTRA_FULL_CONTEXT_MANIFEST:
{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json

## FULL_CONTEXT_PARTS
{parts_links}

## PRIORITY_OF_TRUTH
1. Live user output + terminal
2. SAFE_RUNTIME_SNAPSHOT
3. LATEST_HANDOFF
4. NOT_CLOSED
5. CANON_FINAL
6. ARCHITECTURE
7. FULL_CONTEXT_PARTS
8. chat_exports
9. UNKNOWN

## CURRENT_OPEN_STATUS
CANON_ROUTE_FIX_V2: INSTALLED, live-test required
FULL_CONTEXT_AGGREGATOR_V1: this file is generated by full_context_aggregator.py
"""


def build_session_start_prompt() -> str:
    return f"""# CLAUDE_SESSION_START_PROMPT

GENERATED_AT_UTC: {utc_now()}

MANDATORY FIRST STEP:
Read this file before answering any technical question:

{RAW_MAIN}/docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md

If unavailable, answer only:
MODEL_BOOTSTRAP_CONTEXT_UNAVAILABLE

This prompt is an alias. The universal source for all models is MODEL_BOOTSTRAP_CONTEXT.md
"""


def ensure_secret_patterns() -> None:
    p = BASE / ".secret_patterns"
    if p.exists():
        return
    p.write_text(
        "\n".join([
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
            r"github_pat_[A-Za-z0-9_]{50,}",
            r"ghp_[A-Za-z0-9_]{30,}",
            r"sk-[A-Za-z0-9_\-]{20,}",
            r"\b[0-9]{8,10}:[A-Za-z0-9_\-]{30,}\b",
            r"1//[A-Za-z0-9_\-]{20,}",
            r'"private_key"\s*:\s*"[^"]+',
            r"(?:OPENROUTER_API_KEY|TELEGRAM_BOT_TOKEN|GROQ_API_KEY|GITHUB_TOKEN)\s*=\s*[^<\s]+",
            "",
        ]),
        encoding="utf-8",
    )
    os.chmod(p, 0o600)
    print("SECRET_PATTERNS_CREATED")


def stage_outputs(parts_count: int) -> None:
    generated = [
        "tools/full_context_aggregator.py",
        "tools/context_aggregator.py",
        "tools/claude_bootstrap_aggregator.py",
        "docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md",
        "docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md",
        "docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md",
        "docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md",
        "docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md",
        "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md",
        "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json",
        "docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md",
        "docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md",
        "docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md",
        "docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md",
    ] + [
        f"docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md"
        for i in range(1, parts_count + 1)
    ]
    topics_dir = BASE / "docs" / "SHARED_CONTEXT" / "TOPICS"
    if topics_dir.exists():
        for ff in topics_dir.glob("*.md"):
            generated.append(str(ff.relative_to(BASE)))
    directions_dir = BASE / "docs" / "SHARED_CONTEXT" / "DIRECTIONS"
    if directions_dir.exists():
        for ff in directions_dir.glob("*.md"):
            generated.append(str(ff.relative_to(BASE)))
    subprocess.run(["git", "add", "-u", "docs/SHARED_CONTEXT"], cwd=str(BASE), check=True)
    subprocess.run(["git", "add"] + generated, cwd=str(BASE), check=True)


def run_secret_scan() -> None:
    scan = BASE / "tools/secret_scan.sh"
    if not scan.exists():
        raise RuntimeError("SECRET_SCAN_NOT_FOUND")
    ensure_secret_patterns()
    p = subprocess.run(["bash", str(scan)], cwd=str(BASE), text=True, capture_output=True)
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    print(out)
    if "SECRET_SCAN_SKIP" in out:
        raise RuntimeError("SECRET_SCAN_SKIP_IS_FAIL")
    if p.returncode != 0:
        raise RuntimeError("SECRET_SCAN_FAILED")
    print("SECRET_SCAN_OK_CONFIRMED")


def commit_push_verify() -> str:
    status = run(["git", "status", "--short"])
    print("GIT_STATUS_BEFORE_COMMIT:")
    print(status if status else "clean")

    if "D tools/context_aggregator.py" in status:
        raise RuntimeError("CONTEXT_AGGREGATOR_DELETED_REFUSE_COMMIT")

    if not status.strip():
        print("NO_GIT_CHANGE")
        return run(["git", "rev-parse", "HEAD"], check=True)

    commit = subprocess.run(
        ["git", "commit", "-m", "FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context"],
        cwd=str(BASE),
        text=True,
        capture_output=True,
    )
    print(commit.stdout.strip())
    if commit.returncode != 0 and "nothing to commit" not in (commit.stdout + commit.stderr):
        print(commit.stderr.strip())
        raise RuntimeError("COMMIT_FAILED")

    # === FULL_CONTEXT_AGGREGATOR_TOKEN_PUSH_V1 ===
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        env_path = BASE / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "GITHUB_TOKEN":
                    token = v.strip().strip("'").strip('"')
                    break
    if not token:
        raise RuntimeError("GITHUB_TOKEN_MISSING_FOR_PUSH")

    import base64 as _b64_fca
    auth = _b64_fca.b64encode(("x-access-token:" + token).encode("utf-8")).decode("ascii")
    push = subprocess.run(
        ["git", "-c", "http.https://github.com/.extraheader=AUTHORIZATION: basic " + auth, "push", "origin", "main"],
        cwd=str(BASE),
        text=True,
        capture_output=True,
    )
    print(push.stdout.strip())
    print(push.stderr.strip())
    if push.returncode != 0:
        raise RuntimeError("PUSH_FAILED")
    # === END_FULL_CONTEXT_AGGREGATOR_TOKEN_PUSH_V1 ===

    new_sha = run(["git", "rev-parse", "HEAD"], check=True)
    print(f"PUSH_OK {new_sha}")
    return new_sha


def verify_raw_exact(commit_sha: str) -> None:
    local_path = OUTPUT_DIR / "MODEL_BOOTSTRAP_CONTEXT.md"
    expected = sha256_file(local_path)
    url = f"https://raw.githubusercontent.com/{REPO}/{commit_sha}/docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md"

    for i in range(1, 8):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                data = r.read()
            actual = hashlib.sha256(data).hexdigest()
            if actual == expected:
                print(f"RAW_EXACT_SHA_VERIFY_OK {commit_sha}")
                return
            print(f"RAW_HASH_MISMATCH attempt={i}")
        except Exception as e:
            print(f"RAW_VERIFY_FAIL attempt={i}: {e}")
        time.sleep(5)

    raise RuntimeError("RAW_EXACT_SHA_VERIFY_FAILED")


def main() -> None:
    with LOCK_PATH.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("FULL_CONTEXT_AGGREGATOR_ALREADY_RUNNING")
            return

        print(f"FULL_CONTEXT_AGGREGATOR_V1_START {utc_now()}")

        if not run(["git", "ls-files", "tools/context_aggregator.py"]).strip():
            print("CONTEXT_AGGREGATOR_GITIGNORED_OK — using tools/full_context_aggregator.py as tracked source")

        git_sha_before = run(["git", "rev-parse", "HEAD"], check=True)

        full_items, manifest_records = collect_files()
        print(f"INCLUDED_FULL_FILES {len(full_items)}")
        print(f"MANIFEST_RECORDS {len(manifest_records)}")

        blocks, chunk_counts = build_file_blocks(full_items)
        parts = split_blocks_to_parts(blocks)
        print(f"PARTS_COUNT {len(parts)}")

        cleanup_old_parts()

        runtime = build_runtime_snapshot(git_sha_before)
        write(OUTPUT_DIR / "SAFE_RUNTIME_SNAPSHOT.md", runtime)

        for i, content in enumerate(parts, 1):
            header = (
                f"# ORCHESTRA_FULL_CONTEXT_PART_{i:03d}\n"
                f"generated_at_utc: {utc_now()}\n"
                f"git_sha_before_commit: {git_sha_before}\n"
                f"part: {i}/{len(parts)}\n\n"
            )
            write(OUTPUT_DIR / f"ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md", header + content)

        manifest = build_manifest(manifest_records, chunk_counts, git_sha_before, len(parts))
        write(OUTPUT_DIR / "ORCHESTRA_FULL_CONTEXT_MANIFEST.json", manifest)

        context_index = build_context_index(git_sha_before, len(parts), manifest_records)
        write(OUTPUT_DIR / "ORCHESTRA_FULL_CONTEXT.md", context_index)

        bootstrap = build_model_bootstrap(git_sha_before, len(parts), sha256_text(manifest))
        write(OUTPUT_DIR / "MODEL_BOOTSTRAP_CONTEXT.md", bootstrap)
        write(OUTPUT_DIR / "CLAUDE_BOOTSTRAP_CONTEXT.md", bootstrap)
        write(OUTPUT_DIR / "ONE_SHARED_CONTEXT.md", bootstrap)
        write(OUTPUT_DIR / "CLAUDE_SESSION_START_PROMPT.md", build_session_start_prompt())

        smsv1_generate_all(git_sha_before)
        if "--no-auto-push" in sys.argv:
            print("NO_AUTO_PUSH_MODE — skip stage/scan/push")
            new_sha = git_sha_before
        else:
            stage_outputs(len(parts))
            run_secret_scan()
            new_sha = commit_push_verify()
            verify_raw_exact(new_sha)

        print(f"FULL_CONTEXT_AGGREGATOR_V1_DONE {utc_now()}")
        print(f"COMMIT_SHA {new_sha}")
        print(f"PARTS {len(parts)}")
        print(f"FILES_INCLUDED {len(full_items)}")



# === PATCH_AGGREGATOR_SINGLE_MODEL_SOURCE_V1 ===
import sqlite3 as _smsv1_sqlite

_SMSV1_TOPICS_DIR = OUTPUT_DIR / "TOPICS"
_SMSV1_DIRECTIONS_DIR = OUTPUT_DIR / "DIRECTIONS"

_SMSV1_FORBIDDEN_FILES = (
    ".env", "credentials", "sessions/",
    "core/ai_router.py", "core/reply_sender.py", "core/google_io.py",
    "task_worker.py", "telegram_daemon.py",
    "data/core.db", "data/memory.db",
)

_SMSV1_TOPIC_NAMES = {
    0: "COMMON",
    2: "STROYKA",
    5: "TEKHNADZOR",
    11: "VIDEO",
    210: "PROEKTIROVANIE",
    500: "VEB_POISK",
    794: "DEVOPS",
    961: "AVTOZAPCHASTI",
    3008: "KODY_MOZGOV",
    4569: "CRM_LEADS",
    6104: "JOB_SEARCH",
}

def _smsv1_load_directions():
    try:
        sys.path.insert(0, str(BASE))
        from core.direction_registry import DirectionRegistry
        reg = DirectionRegistry()
        return reg.directions, "DirectionRegistry"
    except Exception as e:
        return {}, f"FAIL:{e}"

def _smsv1_db_state(topic_id):
    db = BASE / "data" / "core.db"
    if not db.exists():
        return {}
    try:
        conn = _smsv1_sqlite.connect(str(db))
        conn.row_factory = _smsv1_sqlite.Row
        cur = conn.execute(
            "SELECT state, COUNT(*) c FROM tasks WHERE topic_id=? GROUP BY state",
            (int(topic_id),)
        )
        states = {row["state"]: row["c"] for row in cur.fetchall()}
        cur = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE topic_id=? AND state='FAILED' "
            "AND updated_at >= datetime('now','-24 hours')",
            (int(topic_id),)
        )
        failed_24h = cur.fetchone()[0]
        cur = conn.execute(
            "SELECT id, substr(coalesce(error_message,''),1,80) em "
            "FROM tasks WHERE topic_id=? AND state='FAILED' "
            "ORDER BY rowid DESC LIMIT 5",
            (int(topic_id),)
        )
        last_failed = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"states": states, "failed_24h": failed_24h, "last_failed": last_failed}
    except Exception as e:
        return {"error": str(e)}

def _smsv1_markers_24h(topic_id):
    db = BASE / "data" / "core.db"
    if not db.exists():
        return []
    try:
        conn = _smsv1_sqlite.connect(str(db))
        cur = conn.execute(
            "SELECT DISTINCT substr(action,1,80) FROM task_history "
            "WHERE task_id IN (SELECT id FROM tasks WHERE topic_id=?) "
            "AND created_at >= datetime('now','-24 hours') LIMIT 100",
            (int(topic_id),)
        )
        out = [r[0] for r in cur.fetchall()]
        conn.close()
        return out
    except Exception:
        return []

def _smsv1_runtime_catalog_summary(topic_id):
    try:
        sys.path.insert(0, str(BASE))
        from core.runtime_file_catalog import load_catalog
        cat_dir = BASE / "data" / "telegram_file_catalog"
        chats = set()
        if cat_dir.exists():
            for f in cat_dir.glob(f"*__topic_{int(topic_id)}.jsonl"):
                name = f.stem
                if "__topic_" in name and name.startswith("chat_"):
                    cid = name[len("chat_"):name.index("__topic_")]
                    chats.add(cid)
        total = 0
        sample = []
        for cid in chats:
            rows = load_catalog(cid, int(topic_id))
            total += len(rows)
            if rows and len(sample) < 3:
                sample.append({"chat_id": cid, "files": len(rows), "last_file": rows[-1].get("file_name", "")})
        return {"total": total, "chats": len(chats), "sample": sample}
    except Exception as e:
        return {"total": 0, "error": str(e)}

def _smsv1_git_log_per_topic(topic_id, days=14):
    out = run(["git", "-C", str(BASE), "log", f"--since={days} days ago", "--pretty=format:%h|%s", "-200"])
    if not out:
        return []
    matches = []
    needles = (f"topic_{topic_id}", f"topic{topic_id}")
    for line in out.splitlines():
        low = line.lower()
        if any(n in low for n in needles):
            matches.append(line.strip())
    return matches[:30]

def _smsv1_extract_blockers_from_not_closed(topic_id):
    nc = BASE / "docs" / "REPORTS" / "NOT_CLOSED.md"
    if not nc.exists():
        return []
    text = nc.read_text(encoding="utf-8", errors="ignore")
    needle = f"topic_{topic_id}"
    out = []
    for line in text.splitlines():
        if needle in line.lower() and len(out) < 20:
            out.append(line.strip()[:200])
    return out

def _smsv1_drive_chat_exports_status():
    paths = [
        Path("/root/AI_ORCHESTRA/telegram_exports"),
        BASE / "data" / "chat_exports",
        BASE / "chat_exports",
        Path("chat_exports"),
    ]
    found = []
    for pp in paths:
        try:
            if pp.exists():
                files = list(pp.rglob("*.json")) + list(pp.rglob("*.txt")) + list(pp.rglob("*.md"))
                if files:
                    found.append({"path": str(pp), "files": len(files)})
        except Exception:
            continue
    if found:
        return {"status": "SYNCED_LOCAL", "locations": found}
    return {"status": "NOT_SYNCED_OR_NOT_AVAILABLE", "locations": []}

def _smsv1_drive_binding():
    return {
        "DRIVE_UPLOAD_ENGINE": "core/topic_drive_oauth.py",
        "AUTH_ENV": "GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN",
        "ROOT_ENV": "DRIVE_INGEST_FOLDER_ID",
        "PATH_PATTERN": "chat_<chat_id>/topic_<topic_id>",
        "TOPIC_5_SPECIAL": "active_folder_override",
    }

def _smsv1_load_owner_reference():
    out = {"loaded": False, "items": 0}
    paths = [
        BASE / "config" / "owner_reference_registry.json",
        BASE / "data" / "templates" / "reference_monolith" / "owner_reference_full_index.json",
    ]
    import json as _j
    for pth in paths:
        if pth.exists():
            try:
                d = _j.loads(pth.read_text(encoding="utf-8"))
                if isinstance(d, dict):
                    out["loaded"] = True
                    out["items"] += len(d)
                    out[pth.name] = list(d.keys())[:10]
                elif isinstance(d, list):
                    out["loaded"] = True
                    out["items"] += len(d)
            except Exception as e:
                out[f"err_{pth.name}"] = str(e)[:80]
    rep = BASE / "docs" / "REPORTS" / "AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT.md"
    if rep.exists():
        out["report"] = rep.read_text(encoding="utf-8", errors="ignore")[:300]
    return out

def _smsv1_load_estimate_templates():
    out = {"loaded": False, "templates": []}
    pth = BASE / "config" / "estimate_template_registry.json"
    if not pth.exists():
        return out
    try:
        import json as _j
        d = _j.loads(pth.read_text(encoding="utf-8"))
        out["loaded"] = True
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, dict) and "source_files" in v:
                    for sf in (v.get("source_files") or [])[:10]:
                        out["templates"].append({
                            "key": sf.get("key"),
                            "title": sf.get("title"),
                            "role": sf.get("template_role"),
                            "drive_url": sf.get("drive_url"),
                        })
    except Exception as e:
        out["error"] = str(e)[:120]
    return out

def _smsv1_topic2_required_truth():
    return {
        "NEXT_REQUIRED_PATCH": "PATCH_TOPIC2_FULL_GAP_CLOSE_V4",
        "OPEN": [
            "P6E2 photo intercept before canonical",
            "pdf_spec_extractor.py exists but not connected to canonical flow",
            "ocr_table_engine.py exists but not connected to topic_2 flow",
            "per-item materials + works internet price search missing",
            "TOPIC2_MULTIFILE_PROJECT_CONTEXT_* missing",
            "TOPIC2_REVISION_BOUND_TO_PARENT missing",
            "TOPIC2_REPEAT_PARENT_TASK missing",
            "TOPIC2_AFTER_PRICE_CHOICE_GENERATION_STARTED missing",
            "TOPIC2_FORBIDDEN_FINAL_RESULT_BLOCKED missing",
            "TOPIC2_PDF_TOTALS_MATCH_XLSX missing",
            "live verification pending",
        ],
        "REQUIRED_MARKERS": [
            "TOPIC2_ESTIMATE_SESSION_CREATED",
            "TOPIC2_CONTEXT_READY",
            "TOPIC2_TEMPLATE_SELECTED",
            "TOPIC2_PRICE_ENRICHMENT_DONE",
            "TOPIC2_PRICE_CHOICE_CONFIRMED",
            "TOPIC2_LOGISTICS_CONFIRMED",
            "TOPIC2_XLSX_CREATED",
            "TOPIC2_PDF_CREATED",
            "TOPIC2_PDF_CYRILLIC_OK",
            "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
            "TOPIC2_DRIVE_UPLOAD_PDF_OK",
            "TOPIC2_TELEGRAM_DELIVERED",
            "TOPIC2_MESSAGE_THREAD_ID_OK",
            "TOPIC2_DONE_CONTRACT_OK",
        ],
        "REGRESSION_GUARDS": [
            "не возвращать P6E67_PARENT_NOT_FOUND на полное ТЗ",
            "не возвращать INVALID_PUBLIC_RESULT при наличии markers + Drive ссылок",
            "не убивать задачи с TOPIC2_PRICE_CHOICE_REQUESTED 30-мин таймаутом",
            "не плодить новые задачи на короткий ответ 2/да при WAITING_PRICE",
        ],
        "LIVE_VERIFY_COMMANDS": [
            "sqlite3 data/core.db \"SELECT id,state FROM tasks WHERE topic_id=2 ORDER BY rowid DESC LIMIT 10\"",
            "journalctl -u areal-task-worker --since '10 minutes ago' | grep -E 'TOPIC2|TPRR|TPTG|TFFE|TDOIP'",
            "sqlite3 data/core.db \"SELECT action FROM task_history WHERE task_id IN (SELECT id FROM tasks WHERE topic_id=2 ORDER BY rowid DESC LIMIT 1)\"",
        ],
    }

def _smsv1_compute_markers_missing(topic_id, markers_24h):
    if int(topic_id) != 2:
        return []
    required = _smsv1_topic2_required_truth()["REQUIRED_MARKERS"]
    actual = " ".join(markers_24h)
    return [m for m in required if m not in actual]

def _smsv1_topic_safe_name(tid):
    return _SMSV1_TOPIC_NAMES.get(int(tid), f"TOPIC_{tid}")

def _smsv1_derive_status(commits, failed_24h, active_count):
    if failed_24h >= 3 and not commits:
        return "BROKEN"
    if commits and failed_24h == 0 and not active_count:
        return "IDLE_NO_FAILURES_NOT_VERIFIED"
    if commits:
        return "INSTALLED_NOT_VERIFIED"
    return "UNKNOWN"

def _smsv1_render_topic_file(topic_id, role, directions_bound, git_sha):
    db = _smsv1_db_state(topic_id)
    markers = _smsv1_markers_24h(topic_id)
    blockers = _smsv1_extract_blockers_from_not_closed(topic_id)
    commits = _smsv1_git_log_per_topic(topic_id, 14)
    drive = _smsv1_drive_binding()
    chat_exports = _smsv1_drive_chat_exports_status()
    catalog = _smsv1_runtime_catalog_summary(topic_id)

    states = db.get("states", {}) if isinstance(db, dict) else {}
    failed_24h = db.get("failed_24h", 0) if isinstance(db, dict) else 0
    last_failed = db.get("last_failed", []) if isinstance(db, dict) else []
    active = sum(states.get(s, 0) for s in ("NEW", "IN_PROGRESS", "WAITING_CLARIFICATION", "AWAITING_CONFIRMATION"))
    status = _smsv1_derive_status(commits, failed_24h, active)

    parts = [
        f"# topic_{topic_id} {_smsv1_topic_safe_name(topic_id)}",
        "",
        f"GENERATED_AT: {utc_now()}",
        f"GIT_SHA: {git_sha}",
        "GENERATED_FROM: tools/full_context_aggregator.py",
        "",
        f"TOPIC_ID: {topic_id}",
        f"ROLE: {role}",
        f"DIRECTIONS_BOUND: {', '.join(directions_bound) if directions_bound else 'none'}",
        f"CURRENT_STATUS: {status}",
        f"ACTIVE_TASKS: {active}",
        f"FAILED_LAST_24H: {failed_24h}",
        "",
        "## DB_STATE_COUNTS",
    ]
    if states:
        for s, c in sorted(states.items()):
            parts.append(f"- {s}: {c}")
    else:
        parts.append("- (no data)")

    parts += ["", "## LATEST_FAILED"]
    if last_failed:
        for t in last_failed:
            parts.append(f"- {str(t.get('id',''))[:8]} | {t.get('em','')}")
    else:
        parts.append("- (none)")

    parts += ["", "## COMMITS_LAST_14D"]
    if commits:
        for c in commits:
            parts.append(f"- {c}")
    else:
        parts.append("- (none matching topic)")

    parts += ["", "## MARKERS_LAST_24H"]
    if markers:
        for m in markers[:30]:
            parts.append(f"- {m}")
    else:
        parts.append("- (none)")

    parts += ["", "## BLOCKERS_FROM_NOT_CLOSED"]
    if blockers:
        for b in blockers:
            parts.append(f"- {b}")
    else:
        parts.append("- (none)")

    parts += ["", "## RUNTIME_FILE_CATALOG_SUMMARY"]
    parts.append(f"total_files: {catalog.get('total', 0)}")
    parts.append(f"chats: {catalog.get('chats', 0)}")
    if catalog.get("error"):
        parts.append(f"error: {catalog['error']}")

    parts += ["", "## DRIVE_UPLOAD_CONTRACT"]
    for k, v in drive.items():
        parts.append(f"{k}: {v}")

    parts += ["", "## DRIVE_CHAT_EXPORTS_STATUS"]
    parts.append(f"STATUS: {chat_exports.get('status')}")
    for loc in chat_exports.get("locations", []):
        parts.append(f"- {loc.get('path')} files={loc.get('files')}")

    parts += ["", "## FORBIDDEN_FILES"]
    for f in _SMSV1_FORBIDDEN_FILES:
        parts.append(f"- {f}")

    if int(topic_id) == 2:
        truth = _smsv1_topic2_required_truth()
        parts += ["", "## NEXT_REQUIRED_PATCH", truth["NEXT_REQUIRED_PATCH"]]
        parts += ["", "## OPEN_CONTOURS"]
        for it in truth["OPEN"]:
            parts.append(f"- {it}")
        parts += ["", "## REQUIRED_MARKERS"]
        for m in truth["REQUIRED_MARKERS"]:
            parts.append(f"- {m}")
        missing = _smsv1_compute_markers_missing(2, markers)
        parts += ["", "## MARKERS_MISSING"]
        if missing:
            for m in missing:
                parts.append(f"- {m}")
        else:
            parts.append("- (all present in last 24h)")
        parts += ["", "## REGRESSION_GUARDS"]
        for g in truth["REGRESSION_GUARDS"]:
            parts.append(f"- {g}")
        parts += ["", "## LIVE_VERIFY_COMMANDS"]
        for c in truth["LIVE_VERIFY_COMMANDS"]:
            parts.append(f"- {c}")
        et = _smsv1_load_estimate_templates()
        parts += ["", "## ESTIMATE_TEMPLATE_REGISTRY"]
        parts.append(f"loaded: {et.get('loaded', False)}")
        for t in et.get("templates", [])[:10]:
            parts.append(f"- {t.get('key')} | {t.get('title')} | {t.get('role')}")

    if int(topic_id) in (2, 5, 210):
        ref = _smsv1_load_owner_reference()
        parts += ["", "## OWNER_REFERENCE_REGISTRY"]
        parts.append(f"loaded: {ref.get('loaded', False)}")
        parts.append(f"items: {ref.get('items', 0)}")

    parts += ["", "## FACT_SOURCE_LIST"]
    parts.append("- core.db live state and task_history")
    parts.append("- config/directions.yaml via core.direction_registry.DirectionRegistry")
    parts.append("- core/runtime_file_catalog.py")
    parts.append("- config/estimate_template_registry.json")
    parts.append("- config/owner_reference_registry.json")
    parts.append("- data/templates/reference_monolith/owner_reference_full_index.json")
    parts.append("- docs/REPORTS/NOT_CLOSED.md")
    parts.append("- docs/HANDOFFS/LATEST_HANDOFF.md")
    parts.append("- git log last 14 days")
    parts.append("")
    return "\n".join(parts) + "\n"

def _smsv1_render_direction_file(direction_id, profile, topic_status_map, git_sha):
    parts = [
        f"# direction: {direction_id}",
        "",
        f"GENERATED_AT: {utc_now()}",
        f"GIT_SHA: {git_sha}",
        "GENERATED_FROM: core.direction_registry.DirectionRegistry",
        "",
        f"DIRECTION_ID: {direction_id}",
        f"TITLE: {profile.get('title') or profile.get('name') or '?'}",
        f"ENABLED: {profile.get('enabled', False)}",
        f"ENGINE: {profile.get('engine','?')}",
        f"REQUIRES_SEARCH: {profile.get('requires_search', False)}",
        f"TOPIC_IDS: {profile.get('topic_ids', [])}",
        f"INPUT_TYPES: {profile.get('input_types', [])}",
        f"INPUT_FORMATS: {profile.get('input_formats', [])}",
        f"OUTPUT_FORMATS: {profile.get('output_formats', [])}",
        f"QUALITY_GATES: {profile.get('quality_gates', [])}",
        f"ALIASES: {(profile.get('aliases') or [])[:20]}",
        f"STRONG_ALIASES: {profile.get('strong_aliases') or []}",
        "",
        "## BOUND_TOPICS_STATUS",
    ]
    tids = profile.get("topic_ids") or []
    if tids:
        for tid in tids:
            parts.append(f"- topic_{tid}: {topic_status_map.get(int(tid), 'UNKNOWN')}")
    else:
        parts.append("- (no topic_ids bound)")
    parts.append("")
    return "\n".join(parts) + "\n"

def _smsv1_render_single_model_source(directions, topic_status_map, topic_meta, git_sha):
    parts = [
        "# SINGLE_MODEL_SOURCE",
        "",
        f"GENERATED_AT: {utc_now()}",
        f"GIT_SHA: {git_sha}",
        "STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test",
        "",
        "## PRIORITY_OF_TRUTH",
        "1. SAFE_RUNTIME_SNAPSHOT / live core.db",
        "2. docs/HANDOFFS/LATEST_HANDOFF.md",
        "3. docs/REPORTS/NOT_CLOSED.md",
        "4. newest docs/HANDOFFS/*",
        "5. newest chat_exports/*",
        "6. locally synced Google Drive telegram_exports",
        "7. docs/CANON_FINAL/*",
        "8. git log last 14 days",
        "9. code grep",
        "10. UNKNOWN",
        "",
        "## READ_ORDER",
        "1. THIS FILE",
        "2. TOPIC_STATUS_INDEX.md",
        "3. DIRECTION_STATUS_INDEX.md",
        "4. required TOPICS/topic_<id>_*.md or DIRECTIONS/<id>.md",
        "5. SAFE_RUNTIME_SNAPSHOT.md",
        "6. ORCHESTRA_FULL_CONTEXT_MANIFEST.json",
        "7. PART files only if needed",
        "",
        "## DRIVE_BINDING",
    ]
    for k, v in _smsv1_drive_binding().items():
        parts.append(f"{k}: {v}")

    ref = _smsv1_load_owner_reference()
    et = _smsv1_load_estimate_templates()
    parts += ["", "## REFERENCE_REGISTRIES"]
    parts.append(f"estimate_template_registry: loaded={et.get('loaded', False)} templates_count={len(et.get('templates', []))}")
    parts.append(f"owner_reference_registry: loaded={ref.get('loaded', False)} items={ref.get('items', 0)}")
    if ref.get("report"):
        parts.append(f"AREAL_REFERENCE_REPORT_SUMMARY: {ref['report'][:200]}")
    if et.get("templates"):
        parts.append("estimate_templates_top5:")
        for t in et["templates"][:5]:
            parts.append(f"- {t.get('key')} | {t.get('title')} | {t.get('role')}")

    chat_exports = _smsv1_drive_chat_exports_status()
    parts += ["", "## DRIVE_CHAT_EXPORTS_STATUS"]
    parts.append(f"STATUS: {chat_exports.get('status')}")
    for loc in chat_exports.get("locations", []):
        parts.append(f"- {loc.get('path')} files={loc.get('files')}")

    parts += ["", "## GLOBAL_TOPIC_TABLE"]
    parts.append("| topic_id | name | status | active | failed_24h |")
    parts.append("|----------|------|--------|--------|------------|")
    for tid, meta in sorted(topic_meta.items()):
        parts.append(f"| {tid} | {_smsv1_topic_safe_name(tid)} | {meta.get('status','?')} | {meta.get('active',0)} | {meta.get('failed_24h',0)} |")

    parts += ["", "## DIRECTION_TABLE"]
    parts.append("| direction_id | engine | enabled | topic_ids | quality_gates |")
    parts.append("|--------------|--------|---------|-----------|---------------|")
    for did, prof in directions.items():
        prof = prof or {}
        parts.append(f"| {did} | {prof.get('engine','?')} | {prof.get('enabled', False)} | {prof.get('topic_ids', [])} | {prof.get('quality_gates', [])} |")

    parts += ["", "## SOURCE_LINKS"]
    parts.append("- TOPIC_STATUS_INDEX: docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md")
    parts.append("- DIRECTION_STATUS_INDEX: docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md")
    parts.append("- LATEST_HANDOFF: docs/HANDOFFS/LATEST_HANDOFF.md")
    parts.append("- NOT_CLOSED: docs/REPORTS/NOT_CLOSED.md")
    parts.append("- SAFE_RUNTIME_SNAPSHOT: docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md")
    parts.append("- MANIFEST: docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json")
    parts.append("- DirectionRegistry: core/direction_registry.py")
    parts.append("")
    return "\n".join(parts) + "\n"

def _smsv1_render_topic_status_index(topic_meta, git_sha):
    parts = [
        "# TOPIC_STATUS_INDEX",
        "",
        f"GENERATED_AT: {utc_now()}",
        f"GIT_SHA: {git_sha}",
        "",
        "| topic_id | name | role | status | active | failed_24h | source |",
        "|----------|------|------|--------|--------|------------|--------|",
    ]
    for tid, meta in sorted(topic_meta.items()):
        parts.append(f"| {tid} | {_smsv1_topic_safe_name(tid)} | {meta.get('role','?')} | {meta.get('status','?')} | {meta.get('active',0)} | {meta.get('failed_24h',0)} | TOPICS/topic_{tid}_{_smsv1_topic_safe_name(tid)}.md |")
    parts.append("")
    return "\n".join(parts) + "\n"

def _smsv1_render_direction_status_index(directions, topic_status_map, git_sha):
    parts = [
        "# DIRECTION_STATUS_INDEX",
        "",
        f"GENERATED_AT: {utc_now()}",
        f"GIT_SHA: {git_sha}",
        "Source: core/direction_registry.DirectionRegistry from config/directions.yaml",
        "",
        "| direction | enabled | engine | topic_ids | bound_status |",
        "|-----------|---------|--------|-----------|--------------|",
    ]
    for did, prof in directions.items():
        prof = prof or {}
        tids = prof.get("topic_ids") or []
        bound = ",".join(f"{tid}:{topic_status_map.get(int(tid), '?')}" for tid in tids) or "-"
        parts.append(f"| {did} | {prof.get('enabled', False)} | {prof.get('engine','?')} | {tids} | {bound} |")
    parts.append("")
    return "\n".join(parts) + "\n"



# === SMSV1_FULL_CONTEXT_APPLIED ===
def _smfc_read_file(path, max_chars=None):
    p = BASE / path
    if not p.exists():
        return f"# (file missing: {path})\n"
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
        if max_chars and len(text) > max_chars:
            text = text[:max_chars] + f"\n\n... [TRUNCATED at {max_chars} chars from {len(text)} total — see source file] ..."
        return text
    except Exception as e:
        return f"# (read error {path}: {e})\n"

def _smfc_last_failed_per_topic(topic_id, limit=5):
    try:
        conn = _smsv1_sqlite.connect(str(BASE / "data" / "core.db"))
        conn.row_factory = _smsv1_sqlite.Row
        cur = conn.execute(
            "SELECT id, datetime(updated_at,'localtime') t, "
            "substr(coalesce(error_message,''),1,200) em, "
            "substr(raw_input,1,150) ri "
            "FROM tasks WHERE topic_id=? AND state='FAILED' "
            "ORDER BY rowid DESC LIMIT ?",
            (int(topic_id), limit)
        )
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            hist_cur = conn.execute(
                "SELECT substr(action,1,100) FROM task_history "
                "WHERE task_id=? ORDER BY rowid DESC LIMIT 5",
                (d["id"],)
            )
            d["history"] = [h[0] for h in hist_cur.fetchall()]
            rows.append(d)
        conn.close()
        return rows
    except Exception as e:
        return [{"error": str(e)}]

def _smfc_render_full_context(directions, topic_status_map, topic_meta, git_sha):
    parts = []
    parts.append("# SINGLE_MODEL_FULL_CONTEXT")
    parts.append("")
    parts.append(f"GENERATED_AT: {utc_now()}")
    parts.append(f"GIT_SHA: {git_sha}")
    parts.append("PURPOSE: Один файл с полным контекстом проекта для любой модели")
    parts.append("STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test")
    parts.append("")
    parts.append("## CONTENTS")
    parts.append("1. SUMMARY (карта статусов всех топиков и направлений)")
    parts.append("2. DOCS/HANDOFFS/LATEST_HANDOFF.md (полностью)")
    parts.append("3. DOCS/REPORTS/NOT_CLOSED.md (полностью)")
    parts.append("4. DOCS/CANON_FINAL/* (полностью)")
    parts.append("5. PER_TOPIC: status + last failed + key engine code (head)")
    parts.append("6. PER_DIRECTION: profile + bound topics status")
    parts.append("7. SOURCE_LINKS")
    parts.append("")
    parts.append("=" * 80)
    parts.append("# 1. SUMMARY")
    parts.append("=" * 80)
    parts.append("")
    parts.append("## GLOBAL_TOPIC_TABLE")
    parts.append("| topic_id | name | status | active | failed_24h |")
    parts.append("|----------|------|--------|--------|------------|")
    for tid, meta in sorted(topic_meta.items()):
        parts.append(f"| {tid} | {_smsv1_topic_safe_name(tid)} | {meta.get('status','?')} | "
                     f"{meta.get('active',0)} | {meta.get('failed_24h',0)} |")
    parts.append("")
    parts.append("## DIRECTION_TABLE")
    parts.append("| direction_id | engine | enabled | topic_ids |")
    parts.append("|--------------|--------|---------|-----------|")
    for did, prof in directions.items():
        parts.append(f"| {did} | {(prof or {}).get('engine','?')} | "
                     f"{(prof or {}).get('enabled', False)} | {(prof or {}).get('topic_ids', [])} |")
    parts.append("")
    parts.append("## DRIVE_BINDING")
    for k, v in _smsv1_drive_binding().items():
        parts.append(f"{k}: {v}")
    parts.append("")
    parts.append("## REFERENCE_REGISTRIES")
    et = _smsv1_load_estimate_templates()
    ref = _smsv1_load_owner_reference()
    parts.append(f"estimate_template_registry: loaded={et.get('loaded')} count={len(et.get('templates', []))}")
    parts.append(f"owner_reference_registry: loaded={ref.get('loaded')} items={ref.get('items', 0)}")
    for t in et.get("templates", [])[:10]:
        parts.append(f"- {t.get('key')} | {t.get('title')} | {t.get('role')}")
    parts.append("")

    parts.append("=" * 80)
    parts.append("# 2. LATEST_HANDOFF")
    parts.append("=" * 80)
    parts.append("")
    parts.append(_smfc_read_file("docs/HANDOFFS/LATEST_HANDOFF.md"))
    parts.append("")

    parts.append("=" * 80)
    parts.append("# 3. NOT_CLOSED")
    parts.append("=" * 80)
    parts.append("")
    parts.append(_smfc_read_file("docs/REPORTS/NOT_CLOSED.md"))
    parts.append("")

    parts.append("=" * 80)
    parts.append("# 4. CANON_FINAL")
    parts.append("=" * 80)
    parts.append("")
    canon_dir = BASE / "docs" / "CANON_FINAL"
    if canon_dir.exists():
        for f in sorted(canon_dir.glob("*.md")):
            parts.append(f"## CANON_FINAL/{f.name}")
            parts.append("")
            parts.append(_smfc_read_file(f"docs/CANON_FINAL/{f.name}"))
            parts.append("")

    parts.append("=" * 80)
    parts.append("# 5. PER_TOPIC")
    parts.append("=" * 80)
    parts.append("")
    
    # Engine maps per topic
    topic_engines = {
        2: ["core/sample_template_engine.py", "core/stroyka_estimate_canon.py", "core/topic2_estimate_final_close_v2.py"],
        5: ["core/technadzor_engine.py", "core/normative_engine.py"],
        210: ["core/project_engine.py", "core/cad_project_engine.py"],
        500: ["core/search_session.py", "core/search_engine.py"],
    }
    
    for tid in sorted(topic_meta.keys()):
        meta = topic_meta[tid]
        parts.append(f"## TOPIC_{tid}_{_smsv1_topic_safe_name(tid)}")
        parts.append("")
        parts.append(f"STATUS: {meta.get('status','?')}")
        parts.append(f"ACTIVE: {meta.get('active',0)}  FAILED_24H: {meta.get('failed_24h',0)}")
        parts.append(f"DIRECTIONS_BOUND: {meta.get('role','?')}")
        parts.append("")
        # Last failed
        failed = _smfc_last_failed_per_topic(tid, 5)
        if failed and not failed[0].get("error"):
            parts.append("### LAST_FAILED (5)")
            for f in failed:
                parts.append(f"- {f.get('id','')[:8]} | {f.get('t','')} | {f.get('em','')[:80]}")
                if f.get("history"):
                    for h in f["history"][:3]:
                        parts.append(f"    history: {h}")
            parts.append("")
        # Engine code (head 250 lines)
        if tid in topic_engines:
            parts.append("### KEY_ENGINE_CODE (head 250 lines each)")
            for engine_path in topic_engines[tid]:
                ep = BASE / engine_path
                if ep.exists():
                    parts.append(f"#### {engine_path}")
                    parts.append("```python")
                    try:
                        lines = ep.read_text(encoding="utf-8", errors="ignore").splitlines()[:250]
                        parts.append("\n".join(lines))
                    except Exception as e:
                        parts.append(f"# read error: {e}")
                    parts.append("```")
                    parts.append("")
        # Topic file inline (markers, blockers, regression)
        topic_file = BASE / "docs" / "SHARED_CONTEXT" / "TOPICS" / f"topic_{tid}_{_smsv1_topic_safe_name(tid)}.md"
        if topic_file.exists():
            parts.append(f"### TOPIC_FILE_INLINE")
            parts.append("```")
            parts.append(_smfc_read_file(f"docs/SHARED_CONTEXT/TOPICS/topic_{tid}_{_smsv1_topic_safe_name(tid)}.md"))
            parts.append("```")
            parts.append("")

    parts.append("=" * 80)
    parts.append("# 6. PER_DIRECTION")
    parts.append("=" * 80)
    parts.append("")
    for did, prof in directions.items():
        prof = prof or {}
        if not prof.get("enabled", False):
            continue
        parts.append(f"## {did}")
        parts.append(f"engine: {prof.get('engine','?')}")
        parts.append(f"topic_ids: {prof.get('topic_ids', [])}")
        parts.append(f"input_types: {prof.get('input_types', [])}")
        parts.append(f"output_formats: {prof.get('output_formats', [])}")
        parts.append(f"quality_gates: {prof.get('quality_gates', [])}")
        parts.append(f"aliases: {(prof.get('aliases') or [])[:10]}")
        parts.append("")

    parts.append("=" * 80)
    parts.append("# 7. SOURCE_LINKS")
    parts.append("=" * 80)
    parts.append("")
    parts.append("- TOPIC_STATUS_INDEX: docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md")
    parts.append("- DIRECTION_STATUS_INDEX: docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md")
    parts.append("- SAFE_RUNTIME_SNAPSHOT: docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md")
    parts.append("- MANIFEST: docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json")
    parts.append("- DirectionRegistry: core/direction_registry.py")
    parts.append("- runtime_file_catalog: core/runtime_file_catalog.py")
    parts.append("- topic_drive_oauth: core/topic_drive_oauth.py")
    parts.append("- ORCHESTRA_FULL_CONTEXT_PARTS: 17 files (full project dump)")
    parts.append("")
    return "\n".join(parts) + "\n"

# === END SMSV1_FULL_CONTEXT_APPLIED ===

def smsv1_generate_all(git_sha):
    _SMSV1_TOPICS_DIR.mkdir(parents=True, exist_ok=True)
    _SMSV1_DIRECTIONS_DIR.mkdir(parents=True, exist_ok=True)

    directions, dr_source = _smsv1_load_directions()
    topic_ids_set = set(int(k) for k in _SMSV1_TOPIC_NAMES.keys())
    direction_role_map = {}
    for did, prof in directions.items():
        for tid in ((prof or {}).get("topic_ids") or []):
            try:
                tid_int = int(tid)
                topic_ids_set.add(tid_int)
                direction_role_map.setdefault(tid_int, []).append(did)
            except Exception:
                pass

    topic_meta = {}
    topic_status_map = {}

    for tid in sorted(topic_ids_set):
        directions_bound = direction_role_map.get(tid, [])
        if directions_bound and directions_bound[0] in directions:
            role = (directions[directions_bound[0]] or {}).get("title") or (directions[directions_bound[0]] or {}).get("name") or "?"
        else:
            role = "Общий" if tid == 0 else "?"
        content = _smsv1_render_topic_file(tid, role, directions_bound, git_sha)
        safe_name = _smsv1_topic_safe_name(tid)
        write(_SMSV1_TOPICS_DIR / f"topic_{tid}_{safe_name}.md", content)

        st = "UNKNOWN"
        active = 0
        failed_24h = 0
        for line in content.splitlines():
            if line.startswith("CURRENT_STATUS:"):
                st = line.split(":", 1)[1].strip()
            elif line.startswith("FAILED_LAST_24H:"):
                try:
                    failed_24h = int(line.split(":", 1)[1].strip())
                except Exception:
                    pass
            elif line.startswith("ACTIVE_TASKS:"):
                try:
                    active = int(line.split(":", 1)[1].strip())
                except Exception:
                    pass
        topic_meta[tid] = {"role": role, "status": st, "active": active, "failed_24h": failed_24h}
        topic_status_map[tid] = st

    for did, prof in directions.items():
        write(_SMSV1_DIRECTIONS_DIR / f"{did}.md", _smsv1_render_direction_file(did, prof or {}, topic_status_map, git_sha))

    write(OUTPUT_DIR / "TOPIC_STATUS_INDEX.md", _smsv1_render_topic_status_index(topic_meta, git_sha))
    write(OUTPUT_DIR / "DIRECTION_STATUS_INDEX.md", _smsv1_render_direction_status_index(directions, topic_status_map, git_sha))
    write(OUTPUT_DIR / "SINGLE_MODEL_SOURCE.md", _smsv1_render_single_model_source(directions, topic_status_map, topic_meta, git_sha))

    try:
        full_ctx = _smfc_render_full_context(directions, topic_status_map, topic_meta, git_sha)
        write(OUTPUT_DIR / "SINGLE_MODEL_FULL_CONTEXT.md", full_ctx)
        print(f"SMFC_GENERATED full_context_size={len(full_ctx)}")
    except Exception as _smfc_e:
        print(f"SMFC_FAIL {_smfc_e}")
    print(f"SMSV1_GENERATED directions={len(directions)} topics={len(topic_meta)} dr={dr_source}")

# === END_PATCH_AGGREGATOR_SINGLE_MODEL_SOURCE_V1 ===

if __name__ == "__main__":
    main()
# === END_FULL_CONTEXT_AGGREGATOR_V1 ===
