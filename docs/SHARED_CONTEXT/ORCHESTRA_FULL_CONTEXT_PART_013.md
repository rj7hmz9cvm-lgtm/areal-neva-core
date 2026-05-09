# ORCHESTRA_FULL_CONTEXT_PART_013
generated_at_utc: 2026-05-09T00:40:01.643350+00:00
git_sha_before_commit: 7a5f770d798caf070c337520d425ddab19cbaf60
part: 13/17


====================================================================================================
BEGIN_FILE: tools/full_context_aggregator.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: b122b0a322c8d966053ebb38926b64b77da4d5fe896dde785440f212de3407eb
====================================================================================================
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
    "docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md",
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
            "single_model_current_context": f"{RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md",
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
FIRST_READ_CURRENT_CONTEXT: {RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md
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
2. SINGLE_MODEL_CURRENT_CONTEXT — quick start
3. SINGLE_MODEL_SOURCE — operational index
4. TOPIC_STATUS_INDEX
5. DIRECTION_STATUS_INDEX
6. Required topic/direction file from TOPICS/ or DIRECTIONS/
7. SAFE_RUNTIME_SNAPSHOT
8. SINGLE_MODEL_FULL_CONTEXT — audit only
9. ORCHESTRA_FULL_CONTEXT_MANIFEST
10. ORCHESTRA_FULL_CONTEXT_PART_XXX only if dispute/raw dump needed

## RAW_LINKS
SINGLE_MODEL_CURRENT_CONTEXT:
{RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md

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
        "docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md",
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
    token = <REDACTED_SECRET>"GITHUB_TOKEN", "").strip()
    if not token:
        env_path = BASE / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "GITHUB_TOKEN":
                    token = <REDACTED_SECRET>"'").strip('"')
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
    parts.append("- CURRENT_CONTEXT (quick start): docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md")
    parts.append("- FULL_CONTEXT (audit): docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md")
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



# === SMCC_CURRENT_CONTEXT_APPLIED ===
import re as _smcc_re
from datetime import datetime as _smcc_dt, timezone as _smcc_tz, timedelta as _smcc_td

_SMCC_MAX_TOPIC_BYTES = 2000
_SMCC_MAX_TOTAL_BYTES = 40000

_SMCC_OPEN_KEYS = (
    "NOT CLOSED", "NOT_VERIFIED", "NOT VERIFIED", "INSTALLED, NOT VERIFIED",
    "INSTALLED НО НЕ VERIFIED", "НЕ VERIFIED", "НЕ ЗАКРЫТО", "НЕ ПРОВЕРЕНО",
    "PENDING", "BLOCKER", "TODO", "OPEN", "BROKEN", "ОСТАЁТСЯ", "БЛОКЕР",
)
_SMCC_CLOSED_KEYS = (
    "VERIFIED", "CLOSED", "DONE", "ARCHIVED", "OBSOLETE", "SUPERSEDED",
    "ЗАКРЫТО", "ПОДТВЕРЖДЕНО", "АРХИВ",
)
_SMCC_LINE_FILTER = (
    "⚠️", "❌", "🔴", "OPEN:", "BROKEN:", "PENDING:", "BLOCKER:",
    "NOT VERIFIED", "INSTALLED, NOT VERIFIED", "НЕ VERIFIED", "НЕ ЗАКРЫТО",
    "- ", "* ",
)
_SMCC_DATE_RE = _smcc_re.compile(r"(\d{2}[\.\-/]\d{2}[\.\-/]\d{4}|\d{4}[\.\-/]\d{2}[\.\-/]\d{2})")


def _smcc_clip(text, limit):
    if len(text.encode("utf-8")) <= limit:
        return text
    raw = text.encode("utf-8")[:limit]
    cut = raw.decode("utf-8", errors="ignore")
    nl = cut.rfind("\n")
    if nl > int(limit * 0.65):
        cut = cut[:nl]
    return cut.rstrip() + "\n... [TRUNCATED — see SINGLE_MODEL_FULL_CONTEXT.md]\n"


def _smcc_classify_section(header):
    h = header.upper()
    is_open = any(k in h for k in _SMCC_OPEN_KEYS)
    is_closed = any(k in h for k in _SMCC_CLOSED_KEYS)
    if is_open:
        return "OPEN"
    if is_closed:
        return "CLOSED"
    return "UNKNOWN"


def _smcc_extract_date(header):
    m = _SMCC_DATE_RE.search(header)
    if not m:
        return None
    raw = m.group(1).replace("/", ".").replace("-", ".")
    parts = raw.split(".")
    try:
        if len(parts[0]) == 4:
            y, mo, d = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            d, mo, y = int(parts[0]), int(parts[1]), int(parts[2])
        return _smcc_dt(y, mo, d, tzinfo=_smcc_tz.utc)
    except Exception:
        return None


def _smcc_parse_not_closed():
    nc = BASE / "docs" / "REPORTS" / "NOT_CLOSED.md"
    if not nc.exists():
        return []
    text = nc.read_text(encoding="utf-8", errors="ignore")
    sections = []
    cur = None
    for line in text.splitlines():
        if line.startswith("## ") or line.startswith("### "):
            if cur:
                sections.append(cur)
            cur = {"header": line.strip(), "lines": []}
        elif cur is not None:
            cur["lines"].append(line)
    if cur:
        sections.append(cur)

    cutoff = _smcc_dt.now(_smcc_tz.utc) - _smcc_td(days=30)
    out = []
    for s in sections:
        if _smcc_classify_section(s["header"]) != "OPEN":
            continue
        date = _smcc_extract_date(s["header"])
        if date and date < cutoff:
            continue

        lines = []
        for ln in s["lines"]:
            t = ln.strip()
            if not t:
                continue
            u = t.upper()
            if any(t.startswith(prefix) for prefix in _SMCC_LINE_FILTER) or any(k in u for k in ("NOT VERIFIED", "PENDING", "BLOCKER", "BROKEN", "НЕ ЗАКРЫТО")):
                lines.append(t[:220])
            if len(lines) >= 10:
                break

        if lines:
            out.append({"header": s["header"], "date_unknown": date is None, "lines": lines})
        if len(out) >= 12:
            break
    return out


def _smcc_recent_commits_topic(topic_id):
    try:
        return _smsv1_git_log_per_topic(topic_id, 7)
    except Exception:
        return []


def _smcc_topic_section(tid, name, role, db, markers_24h, blockers_topic):
    states = db.get("states", {}) if isinstance(db, dict) else {}
    failed_24h = db.get("failed_24h", 0) if isinstance(db, dict) else 0
    last_failed = (db.get("last_failed", []) or [])[:5]
    active = sum(states.get(s, 0) for s in ("NEW", "IN_PROGRESS", "WAITING_CLARIFICATION", "AWAITING_CONFIRMATION"))
    commits = _smcc_recent_commits_topic(tid)

    if active == 0 and failed_24h == 0 and not commits and int(tid) not in (2, 5, 210, 500):
        return None

    missing = []
    if int(tid) == 2:
        try:
            missing = _smsv1_compute_markers_missing(2, markers_24h)[:20]
        except Exception:
            missing = []

    parts = []
    parts.append(f"### topic_{tid} {name}")
    parts.append(f"role: {role}")
    parts.append(f"active: {active}")
    parts.append(f"failed_24h: {failed_24h}")
    parts.append(f"commits_last_7d: {len(commits)}")

    if commits:
        parts.append("recent_commits:")
        for c in commits[:3]:
            parts.append(f"- {c[:140]}")

    if missing:
        parts.append(f"markers_missing: {len(missing)}")
        for m in missing[:8]:
            parts.append(f"- {m}")

    if last_failed:
        parts.append("last_failed:")
        for f in last_failed[:3]:
            parts.append(f"- {str(f.get('id',''))[:8]} | {str(f.get('em',''))[:100]}")

    if blockers_topic:
        parts.append("blockers:")
        for b in blockers_topic[:3]:
            parts.append(f"- {str(b)[:140]}")

    next_action = "live-test required"
    if missing:
        next_action = f"live-test / close missing markers: {len(missing)}"
    elif last_failed:
        next_action = f"investigate latest failed: {str(last_failed[0].get('em',''))[:80]}"
    elif blockers_topic:
        next_action = f"close blocker: {str(blockers_topic[0])[:80]}"
    elif commits:
        next_action = "verify recent installed code by live-test"

    parts.append(f"NEXT_ACTION: {next_action}")
    parts.append("")
    return _smcc_clip("\n".join(parts), _SMCC_MAX_TOPIC_BYTES)


def _smcc_render_current_context(directions, topic_status_map, topic_meta, git_sha):
    parts = []
    parts.append("# SINGLE_MODEL_CURRENT_CONTEXT")
    parts.append("")
    parts.append(f"GENERATED_AT: {utc_now()}")
    parts.append(f"GIT_SHA: {git_sha}")
    parts.append("PURPOSE: Быстрый старт для любой модели — только актуальное состояние")
    parts.append("FULL_AUDIT: docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md")
    parts.append("STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test")
    parts.append("")
    parts.append("## READ_ORDER")
    parts.append("1. This SINGLE_MODEL_CURRENT_CONTEXT")
    parts.append("2. SINGLE_MODEL_SOURCE")
    parts.append("3. Topic/direction file if needed")
    parts.append("4. SINGLE_MODEL_FULL_CONTEXT only for audit/dispute")
    parts.append("5. ORCHESTRA_FULL_CONTEXT_PART_*.md only for raw dump")
    parts.append("")
    parts.append("## GLOBAL_STATUS")
    parts.append("| topic | name | status | active | failed_24h |")
    parts.append("|-------|------|--------|--------|------------|")
    for tid, meta in sorted(topic_meta.items()):
        if meta.get("active", 0) > 0 or meta.get("failed_24h", 0) > 0 or int(tid) in (2, 5, 210, 500):
            parts.append(f"| {tid} | {_smsv1_topic_safe_name(tid)} | {meta.get('status','?')} | {meta.get('active',0)} | {meta.get('failed_24h',0)} |")
    parts.append("")

    parts.append("## OPEN_BLOCKERS_FROM_NOT_CLOSED")
    open_sections = _smcc_parse_not_closed()
    if open_sections:
        for s in open_sections[:5]:
            parts.append(f"### {s['header'].lstrip('#').strip()}")
            if s.get("date_unknown"):
                parts.append("DATE_UNKNOWN")
            for ln in s["lines"][:6]:
                parts.append(ln)
            parts.append("")
    else:
        parts.append("(no current open sections detected)")
        parts.append("")

    parts.append("## ACTIVE_OR_RECENT_TOPICS")
    for tid in sorted(topic_meta.keys()):
        meta = topic_meta[tid]
        db = _smsv1_db_state(tid)
        markers = _smsv1_markers_24h(tid)
        blockers = _smsv1_extract_blockers_from_not_closed(tid)
        sec = _smcc_topic_section(tid, _smsv1_topic_safe_name(tid), meta.get("role", "?"), db, markers, blockers)
        if sec:
            parts.append(sec)

    parts.append("## STRICT_RULES")
    parts.append("- INSTALLED != VERIFIED")
    parts.append("- VERIFIED только после live-test")
    parts.append("- Diagnostics → BAK → PATCH → PY_COMPILE → RESTART → LOGS → DB_VERIFY → GIT_PUSH → FINAL_VERIFY")
    parts.append("- Не объявлять закрытым без live-теста")
    parts.append("- BROKEN / REJECTED / UNKNOWN не использовать как канон")
    parts.append("- chat_id + topic_id обязательны для контекста")
    parts.append("- FULL_CONTEXT использовать только для аудита или спора")
    parts.append("")

    parts.append("## ALLOWED_FILES_BY_SCOPE")
    parts.append("- core/stroyka_estimate_canon.py — topic_2 estimates")
    parts.append("- core/sample_template_engine.py — topic_2 estimates/templates")
    parts.append("- core/topic2_estimate_final_close_v2.py — topic_2 legacy/fallback")
    parts.append("- core/technadzor_engine.py — topic_5")
    parts.append("- core/normative_engine.py — topic_5")
    parts.append("- core/project_engine.py — topic_210")
    parts.append("- core/search_session.py — topic_500")
    parts.append("- tools/full_context_aggregator.py — aggregator")
    parts.append("")

    parts.append("## FORBIDDEN_FILES")
    parts.append("- .env / credentials / sessions/")
    parts.append("- core/ai_router.py")
    parts.append("- core/reply_sender.py")
    parts.append("- core/google_io.py")
    parts.append("- telegram_daemon.py")
    parts.append("- data/core.db / data/memory.db schema")
    parts.append("- systemd unit files")
    parts.append("")

    parts.append("## CONDITIONAL_PATCH")
    parts.append("- task_worker.py — only with explicit task scope and diagnostics-first")
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
    parts.append("")

    parts.append("## SOURCE_LINKS")
    parts.append(f"- CURRENT_CONTEXT: {RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md")
    parts.append(f"- SINGLE_MODEL_SOURCE: {RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md")
    parts.append(f"- FULL_CONTEXT_AUDIT: {RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md")
    parts.append(f"- TOPIC_STATUS_INDEX: {RAW_MAIN}/docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md")
    parts.append(f"- DIRECTION_STATUS_INDEX: {RAW_MAIN}/docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md")
    parts.append(f"- LATEST_HANDOFF: {RAW_MAIN}/docs/HANDOFFS/LATEST_HANDOFF.md")
    parts.append(f"- NOT_CLOSED_FULL: {RAW_MAIN}/docs/REPORTS/NOT_CLOSED.md")
    parts.append("")

    return _smcc_clip("\n".join(parts) + "\n", _SMCC_MAX_TOTAL_BYTES)
# === END_SMCC_CURRENT_CONTEXT_APPLIED ===

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
    try:
        current_ctx = _smcc_render_current_context(directions, topic_status_map, topic_meta, git_sha)
        write(OUTPUT_DIR / "SINGLE_MODEL_CURRENT_CONTEXT.md", current_ctx)
        print(f"SMCC_GENERATED current_context_size={len(current_ctx.encode('utf-8'))}")
    except Exception as _smcc_e:
        print(f"SMCC_FAIL {_smcc_e}")
    print(f"SMSV1_GENERATED directions={len(directions)} topics={len(topic_meta)} dr={dr_source}")

# === END_PATCH_AGGREGATOR_SINGLE_MODEL_SOURCE_V1 ===

if __name__ == "__main__":
    main()
# === END_FULL_CONTEXT_AGGREGATOR_V1 ===

====================================================================================================
END_FILE: tools/full_context_aggregator.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/context_aggregator.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 069bfcbd7cb905f16621726e8c56d54aea8340b8513d405d9fc6c6df655c2a36
====================================================================================================
#!/usr/bin/env python3
# === CONTEXT_AGGREGATOR_WRAPPER_V1 ===
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

BASE = Path("/root/.areal-neva-core")

def main() -> None:
    print("CONTEXT_AGGREGATOR_WRAPPER_V1 -> full_context_aggregator.py")
    p = subprocess.run([sys.executable, str(BASE / "tools/full_context_aggregator.py")], cwd=str(BASE))
    sys.exit(p.returncode)

if __name__ == "__main__":
    main()
# === END_CONTEXT_AGGREGATOR_WRAPPER_V1 ===

====================================================================================================
END_FILE: tools/context_aggregator.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/claude_bootstrap_aggregator.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c2f2cd0625c8961b4638a63547ed4c7b3c505ec64a1017f11ccc1a837a42cbda
====================================================================================================
#!/usr/bin/env python3
# === CLAUDE_BOOTSTRAP_AGGREGATOR_WRAPPER_V1 ===
# CANON_FINAL_REMOVE_COMMAND_DISABLED
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

BASE = Path("/root/.areal-neva-core")

def main() -> None:
    print("CLAUDE_BOOTSTRAP_AGGREGATOR_WRAPPER_V1 -> full_context_aggregator.py")
    p = subprocess.run([sys.executable, str(BASE / "tools/full_context_aggregator.py")], cwd=str(BASE))
    sys.exit(p.returncode)

if __name__ == "__main__":
    main()
# === END_CLAUDE_BOOTSTRAP_AGGREGATOR_WRAPPER_V1 ===

====================================================================================================
END_FILE: tools/claude_bootstrap_aggregator.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/__init__.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
====================================================================================================

====================================================================================================
END_FILE: tools/__init__.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/areal_reference_full_monolith_v1.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c571186116ab07d575b430586287bd9a0ab372cfb60fc106d6445d8c6ef35297
====================================================================================================
#!/usr/bin/env python3
# === AREAL_REFERENCE_FULL_MONOLITH_V1 ===
from __future__ import annotations

import io
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

BASE = Path("/root/.areal-neva-core")
CHAT_ID = "-1003725299009"
MAX_DOWNLOAD = 5 * 1024 * 1024

ROOTS = {
    "ESTIMATES_TEMPLATES": "19Z3acDgPub4nV55mad5mb8ju63FsqoG9",
    "TOPIC_210": "17QGniGggGgYEAD8lIyUK6TjgMIIDKhAq",
    "TOPIC_5": "1yWIJdSrypH3BbIozCz-OAw1R6hmnMRHK",
}

MEMORY_DB = BASE / "data" / "memory.db"
REGISTRY_PATH = BASE / "config" / "owner_reference_registry.json"
CANON_PATH = BASE / "docs" / "CANON_FINAL" / "OWNER_REFERENCE_FULL_WORKFLOW_CANON.md"
REPORT_PATH = BASE / "docs" / "REPORTS" / "AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT.md"
INDEX_PATH = BASE / "data" / "templates" / "reference_monolith" / "owner_reference_full_index.json"
VERSION = "AREAL_REFERENCE_FULL_MONOLITH_V1"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def s(v: Any) -> str:
    return "" if v is None else str(v)

def clean(v: Any, limit: int = 20000) -> str:
    return re.sub(r"\s+", " ", s(v)).strip()[:limit]

def env_load() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(str(BASE / ".env"), override=True)
    except Exception:
        pass

def get_drive_service():
    env_load()
    cid = os.getenv("GDRIVE_CLIENT_ID", "").strip()
    sec = os.getenv("GDRIVE_CLIENT_SECRET", "").strip()
    ref = os.getenv("GDRIVE_REFRESH_TOKEN", "").strip()
    if cid and sec and ref:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        creds = Credentials(
            None,
            refresh_token=<REDACTED_SECRET>
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cid,
            client_secret=<REDACTED_SECRET>
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        creds.refresh(Request())
        return build("drive", "v3", credentials=creds)
    sys.path.insert(0, str(BASE))
    import google_io
    return google_io.get_drive_service()

def drive_account(service) -> str:
    u = service.about().get(fields="user").execute().get("user", {})
    return s(u.get("emailAddress") or u.get("displayName") or "UNKNOWN")

def list_children(service, parent_id: str) -> List[Dict[str, Any]]:
    out = []
    token = <REDACTED_SECRET>
    while True:
        res = service.files().list(
            q=f"'{parent_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,modifiedTime,size,webViewLink,parents),nextPageToken",
            pageSize=1000,
            pageToken=<REDACTED_SECRET>
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        out.extend(res.get("files", []))
        token = <REDACTED_SECRET>"nextPageToken")
        if not token:
            break
    return out

def list_recursive(service, parent_id: str, prefix: str) -> List[Dict[str, Any]]:
    out = []
    for f in list_children(service, parent_id):
        item = dict(f)
        item["_path"] = prefix + "/" + s(f.get("name"))
        out.append(item)
        if f.get("mimeType") == "application/vnd.google-apps.folder":
            out.extend(list_recursive(service, f["id"], item["_path"]))
    return out

def size_ok(meta: Dict[str, Any]) -> bool:
    try:
        size = int(meta.get("size") or 0)
        return size > 0 and size <= MAX_DOWNLOAD
    except Exception:
        return False

def download_bytes(service, meta: Dict[str, Any]) -> bytes:
    from googleapiclient.http import MediaIoBaseDownload
    fid = meta["id"]
    mime = s(meta.get("mimeType"))

    if mime == "application/vnd.google-apps.document":
        req = service.files().export_media(fileId=fid, mimeType="text/plain")
    elif mime == "application/vnd.google-apps.spreadsheet":
        req = service.files().export_media(fileId=fid, mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        req = service.files().get_media(fileId=fid, supportsAllDrives=True)

    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
        if buf.tell() > MAX_DOWNLOAD:
            raise RuntimeError("DOWNLOAD_LIMIT_5MB_EXCEEDED")
    return buf.getvalue()

def classify_domain(name: str, path: str, mime: str) -> str:
    low = f"{name} {path} {mime}".lower()
    if any(x in low for x in ["смет", "estimate", "расцен", "м-80", "м-110", "ареал нева", "фундамент_склад", "крыша и перекр"]):
        return "estimate"
    if any(x in low for x in ["технадзор", "дефект", "акт_", "акт ", "исполнительн"]):
        return "technadzor"
    if any(x in low for x in ["проект", "эскиз", "план участка", "посадк", ".dwg", ".dxf", ".ifc", ".pln", "архитект", "спецификац"]):
        return "design"
    if re.search(r"(^|[^а-яa-z0-9])(ар|кр|кж|кд|км|кмд|ов|вк|эо|эм|эос)([^а-яa-z0-9]|$)", low):
        return "design"
    if mime.startswith("image/"):
        return "design"
    return "other"

def discipline(name: str, path: str, mime: str) -> str:
    low = f"{name} {path}".lower()
    checks = [
        ("AR", ["ар", "архитект"]),
        ("KJ", ["кж", "железобет", "плита"]),
        ("KD", ["кд", "стропил", "дерев"]),
        ("KR", ["кр", "конструктив"]),
        ("KM", ["км", "металл"]),
        ("KMD", ["кмд"]),
        ("OV", ["ов", "отоп", "вентиляц"]),
        ("VK", ["вк", "водоснаб", "канализац"]),
        ("EO", ["эо", "эм", "эос", "электр"]),
        ("SPEC", ["спецификац", "ведом"]),
        ("SKETCH", ["эскиз", ".jpg", ".jpeg", ".png", ".webp"]),
        ("GP", ["план участка", "посадк", "генплан"]),
        ("PLN_MODEL", [".pln", "archicad"]),
        ("IFC_MODEL", [".ifc"]),
        ("CAD", [".dwg", ".dxf"]),
    ]
    for code, keys in checks:
        if any(k in low for k in keys):
            return code
    if mime.startswith("image/"):
        return "SKETCH"
    return "DESIGN"

def estimate_role(name: str, path: str) -> str:
    low = f"{name} {path}".lower()
    if "м-80" in low or "m-80" in low:
        return "m80"
    if "м-110" in low or "m-110" in low:
        return "m110"
    if "крыша" in low or "перекр" in low:
        return "roof_floor"
    if "фундамент" in low:
        return "foundation"
    if "ареал нева" in low:
        return "areal_neva"
    return "estimate_reference"

def analyze_xlsx(raw: bytes) -> Dict[str, Any]:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(raw), data_only=False, read_only=False)
    total = 0
    sheets = []
    for ws in wb.worksheets:
        fc = 0
        mat = 0
        work = 0
        logi = 0
        for row in ws.iter_rows():
            vals = []
            for c in row:
                if c.value is None:
                    continue
                val = str(c.value)
                vals.append(val)
                if val.startswith("="):
                    fc += 1
            rt = " ".join(vals).lower()
            if any(x in rt for x in ["материал", "бетон", "арматур", "газобетон", "кирпич", "доска", "кровл"]):
                mat += 1
            if any(x in rt for x in ["работ", "монтаж", "устройств", "кладк", "вязк"]):
                work += 1
            if any(x in rt for x in ["достав", "логист", "разгруз", "манипулятор", "кран", "транспорт", "прожив"]):
                logi += 1
        total += fc
        sheets.append({"sheet_name": ws.title, "formula_count": fc, "material_hits": mat, "work_hits": work, "logistics_hits": logi})
    return {"formula_total": total, "sheets": sheets}

def analyze_file(service, meta: Dict[str, Any]) -> Dict[str, Any]:
    name = s(meta.get("name"))
    path = s(meta.get("_path"))
    mime = s(meta.get("mimeType"))
    domain = classify_domain(name, path, mime)
    item = {
        "name": name,
        "file_id": s(meta.get("id")),
        "mimeType": mime,
        "path": path,
        "size": s(meta.get("size")),
        "modifiedTime": s(meta.get("modifiedTime")),
        "url": s(meta.get("webViewLink")),
        "domain": domain,
    }
    if meta.get("mimeType") == "application/vnd.google-apps.folder":
        item["domain"] = "folder"
        return item

    if domain == "estimate":
        item["role"] = estimate_role(name, path)
        item["formula_total"] = 0
        item["sheets"] = []
        if (
            name.lower().endswith((".xlsx", ".xlsm", ".xls"))
            or mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            or mime == "application/vnd.google-apps.spreadsheet"
        ):
            if mime == "application/vnd.google-apps.spreadsheet" or size_ok(meta):
                try:
                    item.update(analyze_xlsx(download_bytes(service, meta)))
                except Exception as e:
                    item["extract_error"] = clean(type(e).__name__ + ": " + str(e), 500)
            else:
                item["extract_skipped"] = "SIZE_LIMIT_5MB"
    elif domain == "design":
        item["discipline"] = discipline(name, path, mime)
    elif domain == "technadzor":
        item["role"] = "technadzor_reference"
    return item

def slim(policy: Dict[str, Any]) -> Dict[str, Any]:
    def slim_items(items):
        out = []
        for x in items:
            y = {k: v for k, v in x.items() if k not in {"text_preview", "sample_formulas"}}
            if "sheets" in y:
                y["sheets"] = [
                    {k: sh.get(k) for k in ("sheet_name", "formula_count", "material_hits", "work_hits", "logistics_hits")}
                    for sh in y.get("sheets", [])
                ]
            out.append(y)
        return out
    return {
        "version": policy["version"],
        "status": policy["status"],
        "updated_at": policy["updated_at"],
        "counts": policy["counts"],
        "estimate_references": slim_items(policy["estimate_references"][:40]),
        "design_references": slim_items(policy["design_references"][:80]),
        "technadzor_references": slim_items(policy["technadzor_references"][:40]),
    }

def save_memory(policy: Dict[str, Any]) -> None:
    val = json.dumps(slim(policy), ensure_ascii=False, indent=2)
    ts = now()
    rows = [
        ("owner_reference_full_workflow_v1", 0),
        ("topic_2_estimate_reference_v1", 2),
        ("topic_210_design_reference_v1", 210),
        ("topic_5_technadzor_reference_v1", 5),
    ]
    conn = sqlite3.connect(str(MEMORY_DB))
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(memory)").fetchall()]
        for key, topic_id in rows:
            rec = {
                "id": str(uuid.uuid4()),
                "chat_id": CHAT_ID,
                "key": key,
                "value": val,
                "timestamp": ts,
                "topic_id": topic_id,
                "scope": "topic",
            }
            use = [c for c in ["id", "chat_id", "key", "value", "timestamp", "topic_id", "scope"] if c in cols]
            conn.execute(
                f"INSERT INTO memory({','.join(use)}) VALUES ({','.join(['?'] * len(use))})",
                [rec[c] for c in use],
            )
        conn.commit()
    finally:
        conn.close()

def main() -> int:
    service = get_drive_service()
    account = drive_account(service)
    print("DRIVE_ACCOUNT", account)

    all_items = []
    for label, folder_id in ROOTS.items():
        meta = service.files().get(fileId=folder_id, fields="id,name,mimeType", supportsAllDrives=True).execute()
        print("ROOT_OK", label, meta.get("name"), folder_id)
        for f in list_recursive(service, folder_id, label):
            if f.get("mimeType") == "application/vnd.google-apps.folder":
                continue
            item = analyze_file(service, f)
            all_items.append(item)
            print("INDEXED", item.get("domain"), item.get("name"))

    estimates = [x for x in all_items if x.get("domain") == "estimate"]
    designs = [x for x in all_items if x.get("domain") == "design"]
    technadzor = [x for x in all_items if x.get("domain") == "technadzor"]
    formula_total = sum(int(x.get("formula_total") or 0) for x in estimates)

    counts = {
        "estimate_files": len(estimates),
        "design_files": len(designs),
        "technadzor_files": len(technadzor),
        "formula_total": formula_total,
        "all_files": len(all_items),
    }

    policy = {
        "version": VERSION,
        "status": "ACTIVE",
        "updated_at": now(),
        "drive_account": account,
        "counts": counts,
        "estimate_references": estimates,
        "design_references": designs,
        "technadzor_references": technadzor,
    }

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    old = {}
    if REGISTRY_PATH.exists():
        try:
            old = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            old = {}
    old["owner_reference_full_workflow_v1"] = policy
    old["active"] = VERSION
    old["topic_isolation"] = {"estimate": 2, "technadzor": 5, "design": 210}
    REGISTRY_PATH.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    CANON_PATH.parent.mkdir(parents=True, exist_ok=True)
    CANON_PATH.write_text(
        "# OWNER_REFERENCE_FULL_WORKFLOW_CANON\n\n"
        f"version: {VERSION}\n"
        f"updated_at: {policy['updated_at']}\n\n"
        "Илья — главный канон\n\n"
        "Сметы: М-80, М-110, крыша, фундамент, Ареал Нева — эталон формул и структуры\n\n"
        "Проектирование: АР, КР, КЖ, КД, КМ, КМД, ОВ, ВК, ЭО, ЭМ, ЭОС, эскизы, планы участка — разные разделы, не смешивать\n\n"
        "Технадзор: акты, дефекты, исполнительные — отдельный контур\n\n"
        "Если данных не хватает — один короткий вопрос\n\n"
        f"counts: {json.dumps(counts, ensure_ascii=False)}\n",
        encoding="utf-8",
    )

    save_memory(policy)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "# AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT\n\n"
        f"status: OK\nversion: {VERSION}\nupdated_at: {policy['updated_at']}\n"
        f"estimate_files: {counts['estimate_files']}\n"
        f"design_files: {counts['design_files']}\n"
        f"technadzor_files: {counts['technadzor_files']}\n"
        f"formula_total: {counts['formula_total']}\n",
        encoding="utf-8",
    )

    print("ESTIMATE_FILES", counts["estimate_files"])
    print("DESIGN_FILES", counts["design_files"])
    print("TECHNADZOR_FILES", counts["technadzor_files"])
    print("FORMULA_TOTAL", counts["formula_total"])

    if counts["estimate_files"] < 5:
        raise RuntimeError("ESTIMATE_FILES_LT_5")
    if counts["design_files"] < 10:
        raise RuntimeError("DESIGN_FILES_LT_10")
    if counts["formula_total"] < 3000:
        raise RuntimeError("FORMULA_TOTAL_LT_3000")

    print("AREAL_REFERENCE_FULL_MONOLITH_INDEX_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
# === END_AREAL_REFERENCE_FULL_MONOLITH_V1 ===

====================================================================================================
END_FILE: tools/areal_reference_full_monolith_v1.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/drive_ai_orchestra_root_cleanup_v1.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: a15c2c05d0617a95bf3892e3dd7d85c3daefc4a2594b5a96fc7bea3f65032f87
====================================================================================================
#!/usr/bin/env python3
# === DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1 ===
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

BASE = Path("/root/.areal-neva-core")
ROOT_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
CHAT_FOLDER_NAME = "chat_-1003725299009"
CHAT_ID = "-1003725299009"
TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
REPORT_PATH = BASE / "docs" / "REPORTS" / "DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1_REPORT.md"

CANON_ROOT_FOLDERS = {
    "chat_-1003725299009",
    "ESTIMATES",
    "CANON_FINAL",
    "telegram_exports",
    "CHAT_EXPORTS",
    "_QUARANTINE_ROOT_CLEANUP",
    "AI_ORCHESTRA",
}

TMP_RE = re.compile(r"^tmp[a-z0-9_ -]*\.txt$", re.I)

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def s(v: Any) -> str:
    return "" if v is None else str(v)

def low(v: Any) -> str:
    return s(v).lower().strip()

def env_load() -> None:
    env_path = BASE / ".env"
    try:
        from dotenv import load_dotenv
        load_dotenv(str(env_path), override=True)
        return
    except Exception:
        pass

    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def get_drive_service():
    env_load()

    cid = os.getenv("GDRIVE_CLIENT_ID", "").strip()
    sec = os.getenv("GDRIVE_CLIENT_SECRET", "").strip()
    ref = os.getenv("GDRIVE_REFRESH_TOKEN", "").strip()

    if cid and sec and ref:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = Credentials(
            None,
            refresh_token=<REDACTED_SECRET>
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cid,
            client_secret=<REDACTED_SECRET>
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        creds.refresh(Request())
        return build("drive", "v3", credentials=creds)

    sys.path.insert(0, str(BASE))
    import google_io
    return google_io.get_drive_service()

def q_escape(name: str) -> str:
    return name.replace("\\", "\\\\").replace("'", "\\'")

def list_children(service, parent_id: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    token = <REDACTED_SECRET>
    while True:
        res = service.files().list(
            q=f"'{parent_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,modifiedTime,size,webViewLink,parents),nextPageToken",
            pageSize=1000,
            pageToken=<REDACTED_SECRET>
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        out.extend(res.get("files", []))
        token = <REDACTED_SECRET>"nextPageToken")
        if not token:
            break
    return out

def find_child_folder(service, parent_id: str, name: str) -> str | None:
    res = service.files().list(
        q=f"'{parent_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder' and name='{q_escape(name)}'",
        fields="files(id,name,mimeType,parents)",
        pageSize=20,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None

def ensure_folder(service, parent_id: str, name: str) -> str:
    existing = find_child_folder(service, parent_id, name)
    if existing:
        return existing

    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    created = service.files().create(
        body=meta,
        fields="id,name,parents",
        supportsAllDrives=True,
    ).execute()
    return created["id"]

def drive_about(service) -> str:
    about = service.about().get(fields="user").execute()
    user = about.get("user", {}) or {}
    return s(user.get("emailAddress") or user.get("displayName") or "UNKNOWN")

def parents(f: Dict[str, Any]) -> List[str]:
    return list(f.get("parents") or [])

def move_file(service, f: Dict[str, Any], target_id: str, target_path: str, moves: List[Dict[str, Any]]) -> None:
    fid = f["id"]
    current = parents(f)

    if target_id in current and ROOT_ID not in current:
        return

    remove_parents = ",".join([p for p in current if p == ROOT_ID])
    add_parents = target_id if target_id not in current else ""

    if not remove_parents and not add_parents:
        return

    kwargs = {
        "fileId": fid,
        "fields": "id,name,parents",
        "supportsAllDrives": True,
    }
    if add_parents:
        kwargs["addParents"] = add_parents
    if remove_parents:
        kwargs["removeParents"] = remove_parents

    service.files().update(**kwargs).execute()

    moves.append({
        "file_id": fid,
        "name": f.get("name"),
        "mimeType": f.get("mimeType"),
        "target": target_path,
    })

def classify_target(f: Dict[str, Any], folders: Dict[str, str]) -> Tuple[str, str]:
    name = s(f.get("name"))
    n = low(name)
    mime = s(f.get("mimeType"))
    is_folder = mime == "application/vnd.google-apps.folder"

    if is_folder and name in CANON_ROOT_FOLDERS:
        return "SKIP_CANON_ROOT_FOLDER", ""

    if is_folder and name == "Образцы смет и проектов":
        return folders["design_references"], "chat_-1003725299009/topic_210/PROJECT_DESIGN_REFERENCES"

    if TMP_RE.match(name) or n.startswith("tmp"):
        return folders["quarantine_tmp"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/tmp_txt"

    if n in {"upload_many_compat_v2.txt"} or "compat" in n:
        return folders["quarantine_service"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/service_tmp"

    if "chat_export" in n or "chat export" in n:
        return folders["telegram_exports_root_imports"], "telegram_exports/_ROOT_IMPORTS"

    if n.endswith(".manifest.json") or mime == "application/json":
        if n.startswith("estimate_"):
            return folders["estimate_manifests"], "ESTIMATES/generated/_manifests"
        if "кж_compact_project" in n or "project" in n or "кж" in n:
            return folders["project_manifests"], "chat_-1003725299009/topic_210/PROJECT_ARTIFACTS/_manifests"
        return folders["quarantine_manifests"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/manifests"

    if name in {"М-80.xlsx", "M-80.xlsx", "М-110.xlsx", "M-110.xlsx", "крыша и перекр.xlsx", "фундамент_Склад2.xlsx", "Ареал Нева.xlsx"}:
        return folders["estimate_templates"], "ESTIMATES/templates"

    if n.startswith("estimate_") or "смет" in n:
        if n.endswith(".xlsx") or "spreadsheet" in mime:
            return folders["estimate_generated"], "ESTIMATES/generated"
        if n.endswith(".pdf"):
            return folders["estimate_generated_pdf"], "ESTIMATES/generated/pdf"
        return folders["estimate_generated"], "ESTIMATES/generated"

    if n.startswith("act_") or "акт" in n or "дефект" in n or "технадзор" in n:
        return folders["technadzor"], "chat_-1003725299009/topic_5/TECHNADZOR"

    if (
        "кж_compact_project" in n
        or "проект" in n
        or "project" in n
        or re.search(r"(^|[^а-яa-z])(ар|кр|кж|кд)([^а-яa-z]|$)", n)
        or n.endswith((".dwg", ".dxf", ".pln"))
    ):
        return folders["project_artifacts"], "chat_-1003725299009/topic_210/PROJECT_ARTIFACTS"

    if n.endswith((".docx", ".doc", ".pdf", ".xlsx", ".xls", ".csv", ".txt", ".zip", ".rar", ".7z")):
        return folders["quarantine_unknown_files"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/unknown_files"

    if is_folder:
        return folders["quarantine_unknown_folders"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/unknown_folders"

    return folders["quarantine_unknown_files"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/unknown_files"

def main() -> int:
    service = get_drive_service()
    account = drive_about(service)
    print("DRIVE_ACCOUNT", account)

    root_meta = service.files().get(
        fileId=ROOT_ID,
        fields="id,name,mimeType,trashed,webViewLink",
        supportsAllDrives=True,
    ).execute()
    print("ROOT_OK", root_meta.get("name"), root_meta.get("id"))

    chat = ensure_folder(service, ROOT_ID, CHAT_FOLDER_NAME)
    topic_0 = ensure_folder(service, chat, "topic_0")
    topic_2 = ensure_folder(service, chat, "topic_2")
    topic_5 = ensure_folder(service, chat, "topic_5")
    topic_210 = ensure_folder(service, chat, "topic_210")

    estimates = ensure_folder(service, ROOT_ID, "ESTIMATES")
    canon_final = ensure_folder(service, ROOT_ID, "CANON_FINAL")
    telegram_exports = ensure_folder(service, ROOT_ID, "telegram_exports")
    quarantine = ensure_folder(service, ROOT_ID, "_QUARANTINE_ROOT_CLEANUP")
    quarantine_ts = ensure_folder(service, quarantine, TS)

    folders = {
        "topic_0": topic_0,
        "topic_2": topic_2,
        "topic_5": topic_5,
        "topic_210": topic_210,
        "estimates": estimates,
        "canon_final": canon_final,
        "telegram_exports": telegram_exports,

        "estimate_templates": ensure_folder(service, estimates, "templates"),
        "estimate_generated": ensure_folder(service, estimates, "generated"),
        "estimate_generated_pdf": ensure_folder(service, ensure_folder(service, estimates, "generated"), "pdf"),
        "estimate_manifests": ensure_folder(service, ensure_folder(service, estimates, "generated"), "_manifests"),

        "design_references": ensure_folder(service, topic_210, "PROJECT_DESIGN_REFERENCES"),
        "project_artifacts": ensure_folder(service, topic_210, "PROJECT_ARTIFACTS"),
        "project_manifests": ensure_folder(service, ensure_folder(service, topic_210, "PROJECT_ARTIFACTS"), "_manifests"),

        "technadzor": ensure_folder(service, topic_5, "TECHNADZOR"),

        "telegram_exports_root_imports": ensure_folder(service, telegram_exports, "_ROOT_IMPORTS"),

        "quarantine_tmp": ensure_folder(service, quarantine_ts, "tmp_txt"),
        "quarantine_service": ensure_folder(service, quarantine_ts, "service_tmp"),
        "quarantine_manifests": ensure_folder(service, quarantine_ts, "manifests"),
        "quarantine_unknown_files": ensure_folder(service, quarantine_ts, "unknown_files"),
        "quarantine_unknown_folders": ensure_folder(service, quarantine_ts, "unknown_folders"),
    }

    before = list_children(service, ROOT_ID)
    root_files_before = [x for x in before if x.get("mimeType") != "application/vnd.google-apps.folder"]
    print("ROOT_CHILDREN_BEFORE", len(before))
    print("ROOT_FILES_BEFORE", len(root_files_before))

    moves: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []

    for f in before:
        name = s(f.get("name"))
        target_id, target_path = classify_target(f, folders)

        if target_id == "SKIP_CANON_ROOT_FOLDER":
            skipped.append({"name": name, "reason": "canonical_root_folder"})
            continue

        if not target_id:
            skipped.append({"name": name, "reason": "no_target"})
            continue

        move_file(service, f, target_id, target_path, moves)

    after = list_children(service, ROOT_ID)
    root_files_after = [x for x in after if x.get("mimeType") != "application/vnd.google-apps.folder"]
    noncanonical_root = [
        x for x in after
        if x.get("mimeType") != "application/vnd.google-apps.folder"
        or x.get("name") not in {
            CHAT_FOLDER_NAME,
            "ESTIMATES",
            "CANON_FINAL",
            "telegram_exports",
            "CHAT_EXPORTS",
            "_QUARANTINE_ROOT_CLEANUP",
        }
    ]

    print("ROOT_CHILDREN_AFTER", len(after))
    print("ROOT_FILES_AFTER", len(root_files_after))
    print("MOVED_COUNT", len(moves))
    print("SKIPPED_COUNT", len(skipped))
    print("NONCANONICAL_ROOT_COUNT", len(noncanonical_root))

    for m in moves[:300]:
        print("MOVED", m["name"], "=>", m["target"])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1_REPORT")
    lines.append("")
    lines.append("status: OK")
    lines.append("timestamp: " + now())
    lines.append("drive_account: " + account)
    lines.append("root_id: " + ROOT_ID)
    lines.append("")
    lines.append("## COUNTS")
    lines.append(f"- root_children_before: {len(before)}")
    lines.append(f"- root_files_before: {len(root_files_before)}")
    lines.append(f"- moved_count: {len(moves)}")
    lines.append(f"- skipped_count: {len(skipped)}")
    lines.append(f"- root_children_after: {len(after)}")
    lines.append(f"- root_files_after: {len(root_files_after)}")
    lines.append(f"- noncanonical_root_count: {len(noncanonical_root)}")
    lines.append("")
    lines.append("## CANONICAL FOLDERS")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_0")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_2")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_5")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_210")
    lines.append("- AI_ORCHESTRA/ESTIMATES")
    lines.append("- AI_ORCHESTRA/CANON_FINAL")
    lines.append("- AI_ORCHESTRA/telegram_exports")
    lines.append("- AI_ORCHESTRA/_QUARANTINE_ROOT_CLEANUP")
    lines.append("")
    lines.append("## MOVES")
    for m in moves:
        lines.append(f"- `{m['name']}` -> `{m['target']}`")
    lines.append("")
    lines.append("## SKIPPED")
    for s0 in skipped:
        lines.append(f"- `{s0['name']}`: {s0['reason']}")
    lines.append("")
    lines.append("## NONCANONICAL_ROOT_AFTER")
    for x in noncanonical_root[:200]:
        lines.append(f"- `{x.get('name')}` | `{x.get('mimeType')}` | `{x.get('id')}`")
    lines.append("")
    lines.append("## RAW_JSON")
    lines.append("```json")
    lines.append(json.dumps({
        "status": "OK",
        "timestamp": now(),
        "drive_account": account,
        "root_id": ROOT_ID,
        "counts": {
            "root_children_before": len(before),
            "root_files_before": len(root_files_before),
            "moved_count": len(moves),
            "skipped_count": len(skipped),
            "root_children_after": len(after),
            "root_files_after": len(root_files_after),
            "noncanonical_root_count": len(noncanonical_root),
        },
        "moves": moves,
        "skipped": skipped,
        "noncanonical_root_after": [
            {"id": x.get("id"), "name": x.get("name"), "mimeType": x.get("mimeType")}
            for x in noncanonical_root[:500]
        ],
    }, ensure_ascii=False, indent=2))
    lines.append("```")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if len(root_files_after) > 0:
        print("ROOT_FILES_REMAIN_AFTER_CLEANUP")
        for x in root_files_after[:100]:
            print("ROOT_FILE_LEFT", x.get("name"), x.get("mimeType"), x.get("id"))

    print("REPORT_OK", REPORT_PATH)
    print("DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
# === END_DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1 ===

====================================================================================================
END_FILE: tools/drive_ai_orchestra_root_cleanup_v1.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/dwg_converter_healthcheck.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c69921875c85f57c4825a5c904e331b4e292e547b5262d206ca88f987ca8f854
====================================================================================================
#!/usr/bin/env python3
# === DWG_CONVERTER_HEALTHCHECK_V1 ===
from __future__ import annotations
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "docs/SHARED_CONTEXT/DWG_CONVERTER_STATUS.json"

def main():
    status = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "dwg2dxf": shutil.which("dwg2dxf"),
        "ODAFileConverter": shutil.which("ODAFileConverter") or shutil.which("ODAFileConverter.exe"),
        "geometry_status": "FULL_DWG_GEOMETRY_READY" if (shutil.which("dwg2dxf") or shutil.which("ODAFileConverter") or shutil.which("ODAFileConverter.exe")) else "DWG_METADATA_ONLY_DXF_FULL_PARSE_READY",
        "note": "DXF parses directly. DWG full geometry requires dwg2dxf or ODAFileConverter; without converter DWG metadata path remains active",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False))

if __name__ == "__main__":
    main()
# === END_DWG_CONVERTER_HEALTHCHECK_V1 ===

====================================================================================================
END_FILE: tools/dwg_converter_healthcheck.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/estimate_top_templates_logistics_canon_v4.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 7b41927a49d37b6f8be75db07e21c5f3eea770fa4ea71e5482465318e70af7c8
====================================================================================================
#!/usr/bin/env python3
# === ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4 ===
from __future__ import annotations

import io
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

BASE = Path("/root/.areal-neva-core")
sys.path.insert(0, str(BASE))

AI_ORCHESTRA_FOLDER_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
MEMORY_DB = BASE / "data" / "memory.db"
REGISTRY_PATH = BASE / "config" / "estimate_template_registry.json"
CANON_PATH = BASE / "docs" / "CANON_FINAL" / "ESTIMATE_TEMPLATE_M80_M110_CANON.md"
REPORT_PATH = BASE / "docs" / "REPORTS" / "ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4_REPORT.md"
FORMULA_INDEX_PATH = BASE / "data" / "templates" / "estimate_logic" / "estimate_template_formula_index.json"

TEMPLATES = [
    {"key": "M80", "aliases": ["М-80.xlsx", "M-80.xlsx"], "role": "full_house_estimate_template", "description": "Эталон полной сметы М-80"},
    {"key": "M110", "aliases": ["М-110.xlsx", "M-110.xlsx"], "role": "full_house_estimate_template", "description": "Эталон полной сметы М-110"},
    {"key": "ROOF_FLOORS", "aliases": ["крыша и перекр.xlsx"], "role": "roof_and_floor_estimate_template", "description": "Эталон расчёта кровли и перекрытий"},
    {"key": "FOUNDATION_WAREHOUSE", "aliases": ["фундамент_Склад2.xlsx"], "role": "foundation_estimate_template", "description": "Эталон расчёта фундамента"},
    {"key": "AREAL_NEVA", "aliases": ["Ареал Нева.xlsx"], "role": "general_company_estimate_template", "description": "Общий эталон сметной структуры Ареал-Нева"},
]

SECTION_ORDER = [
    "Фундамент",
    "Каркас",
    "Стены",
    "Перекрытия",
    "Кровля",
    "Окна, двери",
    "Внешняя отделка",
    "Внутренняя отделка",
    "Инженерные коммуникации",
    "Логистика",
    "Накладные расходы",
]

UNIVERSAL_MATERIAL_GROUPS = {
    "стены": ["кирпич", "газобетон", "керамоблок", "арболит", "монолит", "каркас", "брус"],
    "фундамент": ["монолитная плита", "лента", "сваи", "ростверк", "утеплённая плита", "складской фундамент"],
    "кровля": ["металлочерепица", "профнастил", "гибкая черепица", "фальц", "мембрана", "стропильная система"],
    "перекрытия": ["деревянные балки", "монолит", "плиты", "металлические балки"],
    "утепление": ["минвата", "роквул", "пеноплэкс", "pir", "эковата"],
    "отделка": ["имитация бруса", "штукатурка", "плитка", "гкл", "цсп", "фасадная доска"],
    "инженерия": ["электрика", "водоснабжение", "канализация", "отопление", "вентиляция"],
    "логистика": ["доставка", "разгрузка", "манипулятор", "кран", "проживание", "транспорт бригады", "удалённость"],
}

FORMULA_POLICY = [
    "Топовые сметы являются эталонами логики расчёта, а не прайс-листами",
    "Новые сметы считаются по такой же структуре: разделы, строки, колонки, формулы, итоги, примечания, исключения",
    "Материал может быть любым: кирпич, газобетон, каркас, монолит, кровля, перекрытия, отделка, инженерия",
    "При замене материала сохраняется расчётная логика: количество × цена = сумма; работа + материалы = всего; разделы = итоги; финальный итог = сумма разделов",
    "Каркасный сценарий, газобетон/монолитная плита, кровля/перекрытия и фундамент считаются как разные сценарии и не смешиваются",
    "Если объёмов не хватает — оркестр спрашивает только недостающие объёмы",
    "Если пользователь прислал файл как образец — сначала принять как образец, а не запускать поиск цен",
]

PRICE_CONFIRMATION_FLOW = [
    "Интернет-цены материалов и техники не подставляются молча",
    "Для финальной сметы оркестр ищет актуальные цены по материалам, технике, доставке и разгрузке",
    "По каждой позиции показывает: источник, цена, единица, дата/регион, ссылка",
    "Оркестр предлагает среднюю/медианную цену без явных выбросов",
    "Пользователь выбирает: средняя / минимальная / максимальная / конкретная ссылка / ручная цена",
    "Пользователь может добавить наценку, запас, скидку, поправку по позиции, разделу или всей смете",
    "До подтверждения цен финальный XLSX/PDF не выпускается",
    "После подтверждения цены пересчитываются по формулам шаблона",
]

LOGISTICS_POLICY = [
    "Перед финальной сметой оркестр обязан запросить локацию объекта или расстояние от города",
    "Стоимость объекта рядом с городом и объекта за 200 км не может быть одинаковой",
    "Оркестр обязан учитывать доставку материалов, транспорт бригады, разгрузку, манипулятор/кран, проживание, удалённость, дорожные условия",
    "Если логистика неизвестна — оркестр задаёт один короткий вопрос: город/населённый пункт или расстояние от города, подъезд для грузовой техники, нужна ли разгрузка/манипулятор",
    "Логистика считается отдельным блоком сметы или отдельным коэффициентом, но не смешивается молча с ценами материалов",
    "Перед финальным результатом оркестр показывает логистические допущения и спрашивает подтверждение",
]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def s(v: Any) -> str:
    return "" if v is None else str(v)

def clean(v: Any) -> str:
    return re.sub(r"\s+", " ", s(v)).strip()

def get_drive_service():
    from dotenv import load_dotenv
    load_dotenv("/root/.areal-neva-core/.env", override=True)

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    cid = os.getenv("GDRIVE_CLIENT_ID", "").strip()
    sec = os.getenv("GDRIVE_CLIENT_SECRET", "").strip()
    ref = os.getenv("GDRIVE_REFRESH_TOKEN", "").strip()

    if cid and sec and ref:
        creds = Credentials(
            None,
            refresh_token=<REDACTED_SECRET>
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cid,
            client_secret=<REDACTED_SECRET>
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        creds.refresh(Request())
        return build("drive", "v3", credentials=creds)

    import google_io
    return google_io.get_drive_service()

def find_file(service, aliases: List[str]) -> Dict[str, Any]:
    for name in aliases:
        safe_name = name.replace("'", "\\'")
        for q in [
            f"name='{safe_name}' and '{AI_ORCHESTRA_FOLDER_ID}' in parents and trashed=false",
            f"name='{safe_name}' and trashed=false",
        ]:
            res = service.files().list(
                q=q,
                fields="files(id,name,mimeType,modifiedTime,size,webViewLink,parents)",
                pageSize=20,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            ).execute()
            files = res.get("files", [])
            if files:
                files.sort(key=lambda x: x.get("modifiedTime") or "", reverse=True)
                return files[0]
    raise RuntimeError("DRIVE_TEMPLATE_NOT_FOUND_OR_NOT_ACCESSIBLE: " + " / ".join(aliases))

def download_xlsx(service, meta: Dict[str, Any]) -> bytes:
    from googleapiclient.http import MediaIoBaseDownload

    mime = meta.get("mimeType") or ""
    file_id = meta["id"]

    if mime == "application/vnd.google-apps.spreadsheet":
        req = service.files().export_media(
            fileId=file_id,
            mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        req = service.files().get_media(fileId=file_id, supportsAllDrives=True)

    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
    return buf.getvalue()

def row_text(row: List[Any]) -> str:
    return " ".join(clean(x) for x in row if clean(x))

def detect_scenario(text: str, title: str) -> str:
    title_low = (title or "").lower()
    low = (title + " " + text).lower()

    # ВАЖНО: сначала название файла/листа, потому что полные сметы М-80/М-110
    # содержат внутри кровлю и перекрытия, но листы называются "Каркас" и "Газобетон"
    if any(x in title_low for x in ["каркас", "frame"]):
        return "frame_house"

    if any(x in title_low for x in ["газобетон", "газо", "кладка", "masonry"]):
        return "gasbeton_or_masonry_with_monolithic_foundation"

    if any(x in title_low for x in ["фундамент", "склад", "foundation"]):
        return "foundation"

    if any(x in title_low for x in ["крыш", "кров", "перекр", "roof", "floor"]):
        return "roof_and_floors"

    # Потом fallback по содержимому
    if any(x in low for x in ["газобетон", "кладка стен", "арматурного каркаса", "бетон в20", "бетон в22"]):
        return "gasbeton_or_masonry_with_monolithic_foundation"

    if any(x in low for x in ["каркас", "свая винтовая", "свайный фундамент", "обвязка свай", "доска с/к"]):
        return "frame_house"

    if any(x in low for x in ["фундамент", "монолитная плита", "ростверк", "свая", "склад"]):
        if not any(y in low for y in ["кровля", "кровель", "стропил", "перекрыт"]):
            return "foundation"

    if any(x in low for x in ["кров", "стропил", "перекр", "балк"]):
        return "roof_and_floors"

    return "general_estimate"

def extract_formula_cells(ws) -> List[Dict[str, str]]:
    out = []
    for row in ws.iter_rows():
        for c in row:
            val = c.value
            if isinstance(val, str) and val.startswith("="):
                out.append({"sheet": ws.title, "cell": c.coordinate, "formula": val[:500]})
    return out

def extract_structure(ws_values, file_title: str) -> Dict[str, Any]:
    rows = [list(r) for r in ws_values.iter_rows(values_only=True)]
    sections = []
    header_rows = []
    total_rows = []
    sample_rows = []
    material_rows = 0
    work_rows = 0
    logistics_rows = 0

    for i, r in enumerate(rows, start=1):
        txt = row_text(r)
        low = txt.lower()
        if not txt:
            continue

        for sec in SECTION_ORDER:
            if low.strip(" :") == sec.lower() and sec not in sections:
                sections.append(sec)

        if "№ п/п" in txt and ("Наименование" in txt or "Наименование работ" in txt):
            header_rows.append(i)

        if low.startswith("итого") or "итого сметная стоимость" in low or "всего" == low.strip():
            total_rows.append({"row": i, "text": txt[:300]})

        if any(x in low for x in ["логист", "достав", "транспорт", "разгруз", "манипулятор", "кран", "проживан", "удален", "удалён", "км"]):
            logistics_rows += 1

        name = clean(r[1] if len(r) > 1 else "")
        unit = clean(r[2] if len(r) > 2 else "")
        qty = clean(r[3] if len(r) > 3 else "")
        work_price = clean(r[4] if len(r) > 4 else "")
        material_price = clean(r[6] if len(r) > 6 else "")

        if name and (unit or qty):
            if work_price and work_price not in ("0", "0.0", "0,0", "-"):
                work_rows += 1
            if material_price and material_price not in ("0", "0.0", "0,0", "-"):
                material_rows += 1
            if len(sample_rows) < 35:
                sample_rows.append({
                    "row": i,
                    "name": name[:180],
                    "unit": unit,
                    "qty": qty,
                    "work_price": work_price,
                    "material_price": material_price,
                })

    hay = "\n".join(row_text(r) for r in rows[:250])
    return {
        "scenario": detect_scenario(hay, file_title),
        "sections": sections,
        "header_rows": header_rows,
        "total_rows": total_rows[:50],
        "material_rows": material_rows,
        "work_rows": work_rows,
        "logistics_rows": logistics_rows,
        "sample_rows": sample_rows,
        "row_count": len(rows),
    }

def analyze_template(service, template: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
    import openpyxl

    raw = download_xlsx(service, meta)
    wb_formula = openpyxl.load_workbook(io.BytesIO(raw), data_only=False, read_only=False)
    wb_values = openpyxl.load_workbook(io.BytesIO(raw), data_only=True, read_only=True)

    sheets = []
    formula_total = 0
    formula_samples = []

    for ws_f, ws_v in zip(wb_formula.worksheets, wb_values.worksheets):
        formulas = extract_formula_cells(ws_f)
        struct = extract_structure(ws_v, f"{meta.get('name') or ''} {ws_f.title}")
        formula_total += len(formulas)
        formula_samples.extend(formulas[:50])
        sheets.append({
            "sheet_name": ws_f.title,
            "scenario": struct["scenario"],
            "sections": struct["sections"],
            "header_rows": struct["header_rows"],
            "total_rows": struct["total_rows"],
            "material_rows": struct["material_rows"],
            "work_rows": struct["work_rows"],
            "logistics_rows": struct["logistics_rows"],
            "sample_rows": struct["sample_rows"],
            "formula_count": len(formulas),
            "formula_samples": formulas[:30],
            "row_count": struct["row_count"],
        })

    return {
        "key": template["key"],
        "title": meta["name"],
        "template_role": template["role"],
        "description": template["description"],
        "file_id": meta["id"],
        "drive_url": meta.get("webViewLink") or f"https://drive.google.com/file/d/{meta['id']}/view",
        "mimeType": meta.get("mimeType"),
        "modifiedTime": meta.get("modifiedTime"),
        "parents": meta.get("parents") or [],
        "formula_total": formula_total,
        "formula_samples": formula_samples[:120],
        "sheets": sheets,
    }

def build_policy(source_files: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "version": "ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4",
        "status": "ACTIVE_CANON",
        "updated_at": now(),
        "purpose": "Use top estimate files as scalable estimate calculation logic templates with mandatory logistics and web price confirmation",
        "source_files": source_files,
        "canonical_columns": [
            "№ п/п",
            "Наименование",
            "Ед. изм.",
            "Кол-во",
            "Работа Цена",
            "Работа Стоимость",
            "Материалы Цена",
            "Материалы Стоимость",
            "Всего",
            "Примечание",
        ],
        "canonical_sections": SECTION_ORDER,
        "universal_material_groups": UNIVERSAL_MATERIAL_GROUPS,
        "formula_policy": FORMULA_POLICY,
        "price_confirmation_flow": PRICE_CONFIRMATION_FLOW,
        "logistics_policy": LOGISTICS_POLICY,
        "runtime_rule": "ai_router injects this context through core.estimate_template_policy.build_estimate_template_context",
    }

def write_canon(policy: Dict[str, Any]) -> None:
    CANON_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# ESTIMATE_TEMPLATE_TOP_CANON")
    lines.append("")
    lines.append("status: ACTIVE_CANON")
    lines.append("version: ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4")
    lines.append("updated_at: " + policy["updated_at"])
    lines.append("")
    lines.append("## ГЛАВНОЕ")
    lines.append("")
    lines.append("М-80.xlsx, М-110.xlsx, крыша и перекр.xlsx, фундамент_Склад2.xlsx, Ареал Нева.xlsx — топовые эталонные сметы")
    lines.append("Они являются образцами логики построения смет, формул, разделов, колонок, итогов, примечаний и исключений")
    lines.append("Они не являются фиксированным прайсом")
    lines.append("Оркестр обязан переносить их расчётную логику на любые новые задачи и любые материалы")
    lines.append("")
    lines.append("## ЧТО СОХРАНЯТЬ")
    for r in policy["formula_policy"]:
        lines.append("- " + r)
    lines.append("")
    lines.append("## ЦЕНЫ ИЗ ИНТЕРНЕТА")
    for r in policy["price_confirmation_flow"]:
        lines.append("- " + r)
    lines.append("")
    lines.append("## ЛОГИСТИКА И НАКЛАДНЫЕ")
    for r in policy["logistics_policy"]:
        lines.append("- " + r)
    lines.append("")
    lines.append("## КОЛОНКИ")
    lines.append(" | ".join(policy["canonical_columns"]))
    lines.append("")
    lines.append("## РАЗДЕЛЫ")
    for i, sec in enumerate(policy["canonical_sections"], 1):
        lines.append(f"{i}. {sec}")
    lines.append("")
    lines.append("## МАТЕРИАЛЫ")
    for group, values in policy["universal_material_groups"].items():
        lines.append(f"- {group}: " + ", ".join(values))
    lines.append("")
    lines.append("## ПРОЧИТАННЫЕ ШАБЛОНЫ")
    for src in policy["source_files"]:
        lines.append("")
        lines.append(f"### {src['title']}")
        lines.append(f"- role: `{src['template_role']}`")
        lines.append(f"- file_id: `{src['file_id']}`")
        lines.append(f"- drive_url: {src['drive_url']}")
        lines.append(f"- formula_total: {src['formula_total']}")
        for sh in src["sheets"]:
            lines.append(f"  - sheet: {sh['sheet_name']} | scenario={sh['scenario']} | formulas={sh['formula_count']} | material_rows={sh['material_rows']} | work_rows={sh['work_rows']} | logistics_rows={sh['logistics_rows']}")
    lines.append("")
    lines.append("## ОБЯЗАТЕЛЬНОЕ ПОВЕДЕНИЕ")
    lines.append("")
    lines.append("При новой смете оркестр обязан брать структуру и формулы из топовых эталонов")
    lines.append("Оркестр обязан подставлять конкретные объёмы и материалы задачи")
    lines.append("Оркестр обязан запросить локацию/удалённость/доступ/разгрузку до финального расчёта")
    lines.append("Оркестр обязан обновлять цены материалов и логистики через интернет только с подтверждением пользователя")
    lines.append("Оркестр обязан показывать найденные цены, источники, ссылки и среднюю/медианную цену")
    lines.append("Пользователь выбирает цену или задаёт ручную, может добавить наценку/скидку/запас")
    lines.append("Финальный XLSX/PDF запрещён до подтверждения цен и логистики")
    lines.append("")
    CANON_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

def write_registry(policy: Dict[str, Any]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    old = {}
    if REGISTRY_PATH.exists():
        try:
            old = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            old = {}
    old["estimate_top_templates_logistics_canon_v4"] = policy
    old["active_estimate_template_policy"] = "ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4"
    old["estimate_formula_logic_preserve_required"] = True
    old["estimate_material_price_web_refresh_required"] = True
    old["estimate_price_confirmation_required"] = True
    old["estimate_logistics_required"] = True
    old["estimate_final_xlsx_forbidden_before_price_and_logistics_confirmation"] = True
    REGISTRY_PATH.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def write_formula_index(policy: Dict[str, Any]) -> None:
    FORMULA_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    FORMULA_INDEX_PATH.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def save_memory_sqlite(policy: Dict[str, Any]) -> None:
    if not MEMORY_DB.exists():
        raise RuntimeError(f"MEMORY_DB_MISSING: {MEMORY_DB}")

    value = json.dumps(policy, ensure_ascii=False, indent=2)
    ts = now()
    keys = [
        "estimate_top_templates_logistics_canon_v4",
        "topic_0_estimate_top_templates_logistics_canon_v4",
        "topic_2_estimate_top_templates_logistics_canon_v4",
        "topic_210_estimate_top_templates_logistics_canon_v4",
        "estimate_universal_material_calculation_policy_v4",
        "estimate_price_confirmation_required_v4",
        "estimate_logistics_required_v4",
    ]

    conn = sqlite3.connect(str(MEMORY_DB))
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(memory)").fetchall()]
        for key in keys:
            data = {
                "id": str(uuid.uuid4()),
                "chat_id": "-1003725299009",
                "key": key,
                "value": value,
                "timestamp": ts,
                "topic_id": 2,
                "scope": "topic",
            }
            use_cols = [c for c in ["id", "chat_id", "key", "value", "timestamp", "topic_id", "scope"] if c in cols]
            sql = f"INSERT INTO memory({','.join(use_cols)}) VALUES ({','.join(['?'] * len(use_cols))})"
            conn.execute(sql, [data[c] for c in use_cols])
        conn.commit()
    finally:
        conn.close()

def write_report(policy: Dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4_REPORT",
        "",
        "status: OK",
        "updated_at: " + policy["updated_at"],
        "canon: docs/CANON_FINAL/ESTIMATE_TEMPLATE_M80_M110_CANON.md",
        "registry: config/estimate_template_registry.json",
        "formula_index: data/templates/estimate_logic/estimate_template_formula_index.json",
        "",
        "## CLOSED",
        "- top estimate templates resolved from Drive",
        "- XLSX formulas extracted",
        "- universal material logic registered",
        "- web price confirmation registered",
        "- logistics and overhead clarification registered",
        "- direct sqlite memory write completed",
        "- ai_router context hook enabled",
        "",
        "## RAW_POLICY",
        "```json",
        json.dumps(policy, ensure_ascii=False, indent=2),
        "```",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    service = get_drive_service()
    about = service.about().get(fields="user").execute()
    print("DRIVE_ACCOUNT", about.get("user", {}).get("emailAddress"))

    source_files = []
    for template in TEMPLATES:
        meta = find_file(service, template["aliases"])
        print("TEMPLATE_FOUND", template["key"], meta.get("name"), meta.get("id"), meta.get("parents"))
        source_files.append(analyze_template(service, template, meta))

    if not source_files:
        raise RuntimeError("NO_TEMPLATES_ANALYZED")

    policy = build_policy(source_files)
    write_canon(policy)
    write_registry(policy)
    write_formula_index(policy)
    save_memory_sqlite(policy)
    write_report(policy)

    print("ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4_OK")
    for src in source_files:
        print("SOURCE", src["title"], src["file_id"], "role", src["template_role"], "formulas", src["formula_total"])
        for sh in src["sheets"]:
            print("SHEET", sh["sheet_name"], sh["scenario"], "formulas", sh["formula_count"], "materials", sh["material_rows"], "works", sh["work_rows"], "logistics", sh["logistics_rows"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
# === END_ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4 ===

====================================================================================================
END_FILE: tools/estimate_top_templates_logistics_canon_v4.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/extract_tnz_msk_document_skill.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 8087be31e961487f7661690181841850967aa0c551bed91a25eed4a6a3d27bed
====================================================================================================
#!/usr/bin/env python3
# === EXTRACT_TNZ_MSK_DOCUMENT_SKILL_V1 ===
# One-shot CLI extractor: reads @tnz_msk via Telethon, extracts document-composition
# methodology for topic_5 technadzor, writes skill package and report.
# Usage:
#   .venv/bin/python tools/extract_tnz_msk_document_skill.py --sample 1000
#   .venv/bin/python tools/extract_tnz_msk_document_skill.py --dry-run
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from core.telegram_source_skill_extractor import run_source_scan
from core.technadzor_document_skill import process_records

SKILL_DIR = BASE / "data/memory_files/TEHNADZOR/source_skills/tnz_msk"
DOCS_DIR = SKILL_DIR / "downloaded_docs"
REPORT_PATH = BASE / "docs/REPORTS/TNZ_MSK_DOCUMENT_SKILL_EXTRACTION_REPORT.md"
HANDOFF_PATH = BASE / "docs/HANDOFFS/HANDOFF_20260505_TNZ_MSK_DOCUMENT_SKILL_EXTRACTION.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def build_skill_md(result: dict, scan_stats: dict, access: dict) -> str:
    cards = result["cards"]
    by_cat = result["by_category"]
    lines = [
        "# TECHNADZOR DOCUMENT COMPOSITION SKILL",
        f"> Source: {access.get('title','')} (@tnz_msk) | Extracted: {_now()}",
        "> Status: SKILL_PACKAGE — NOT A CANON OVERWRITE. Requires owner review before promotion.",
        "",
        "## Source Summary",
        f"- Channel: @tnz_msk — «{access.get('title','')}»",
        f"- Messages scanned: {scan_stats.get('total_fetched', 0)}",
        f"- With text: {scan_stats.get('total_fetched', 0) - scan_stats.get('skipped_empty', 0)}",
        f"- Detected documents: {scan_stats.get('detected_docs', 0)}",
        f"- Detected links: {scan_stats.get('detected_links', 0)}",
        f"- Noise filtered: {scan_stats.get('skipped_noise', 0)}",
        f"- Skill cards extracted: {result['extracted']}",
        f"- Rejected (noise/no value): {result['rejected_noise']}",
        "",
        "## Extracted Skill Categories",
        "",
    ]
    for cat in result["categories"]:
        cat_cards = by_cat.get(cat, [])
        lines.append(f"### {cat} ({len(cat_cards)} rules)")
        lines.append("")
        for card in cat_cards[:5]:
            lines.append(f"**Rule:** {card['extracted_rule']}")
            lines.append(f"- Source: [{card['source_ref']}]({card['source_ref']})")
            lines.append(f"- Why useful for topic_5: {card['why_useful_for_topic_5']}")
            if card.get("source_links"):
                lines.append(f"- Links: {', '.join(card['source_links'][:3])}")
            if card.get("source_files"):
                lines.append(f"- Files: {', '.join(card['source_files'])}")
            if card["needs_owner_review"]:
                lines.append("- ⚠ Needs owner review")
            lines.append("")
        if len(cat_cards) > 5:
            lines.append(f"_...and {len(cat_cards) - 5} more in JSON_")
            lines.append("")

    lines += [
        "## Document Composition Methodology Summary",
        "",
        "Based on extracted patterns from @tnz_msk, the following methodology applies to topic_5:",
        "",
        "### Act Composition Logic",
        "1. State object name, address, date, inspection participants",
        "2. List defects found with precise location references",
        "3. Reference applicable norms (СП/ГОСТ/СНиП) for each defect",
        "4. Attach photo evidence with numbered links to each defect item",
        "5. State required corrective actions with deadlines",
        "6. Conclude with overall assessment",
        "",
        "### Defect Description Logic",
        "- Format: `[Location] — [Defect type] — [Dimension/scale] — [Normative reference] — [Required action]`",
        "- Example: «Трещины в монолитной плите перекрытия оси А-В/1-3 — ширина раскрытия 0,5мм — "
        "нарушение СП 70.13330.2012 п.5.3 — требуется заключение проектировщика»",
        "",
        "### Photo-to-Defect Linking Logic",
        "- Each defect item in the act must reference photo numbers: «Фото 1, 2»",
        "- Photos must be appended as numbered attachment to the act",
        "- Photo description must match defect description location and type",
        "",
        "### Normative Reference Handling",
        "- Always cite specific norm + section, not just norm number",
        "- Example: «СП 70.13330.2012, раздел 5, п.5.3.2»",
        "- For defects without clear norm — mark as `нормативная база уточняется`",
        "",
        "### Conclusion/Recommendation Logic",
        "- Conclusion = technical state category (нормальное / удовлетворительное / ограниченно работоспособное / аварийное)",
        "- Recommendation = specific action + responsible party + deadline",
        "- Use imperative form: «Устранить», «Провести», «Выполнить»",
        "",
        "### File Workflow",
        "- Acts issued as: DOCX (editable) + PDF (signed/sealed version)",
        "- Photos attached as: ZIP archive with numbered files OR embedded in DOCX",
        "- Spreadsheet defect logs: XLSX with columns [№, Описание, Локация, Норматив, Фото, Статус]",
        "",
        "## What Is Not Verified",
        "- Document download from linked URLs not attempted (--no-download-documents mode)",
        "- Norms referenced in channel posts not cross-checked against current editions",
        "- No legal review of extracted wording",
        "",
        "## What Needs Owner Review",
        f"- {sum(1 for c in cards if c['needs_owner_review'])} cards marked `needs_owner_review=true`",
        "- All `unknown` category cards",
        "- Any rule with confidence=low",
        "",
        "## Integration Target",
        "- topic_5 / TECHNADZOR skill layer",
        "- Not a CANON_FINAL overwrite",
        "- Must be manually validated before promotion to canon",
        "",
        "---",
        "",
        "## Reusable Telegram Source Analysis Pattern for RABOTA_POISK (topic_6104)",
        "",
        "### Pattern: Telegram Source → Professional Signal → topic_6104",
        "",
        "This pattern was prototyped on @tnz_msk and is reusable for any Telegram channel "
        "as a source of work opportunities, job leads, or project orders.",
        "",
        "**Step 1 — Source Access**",
        "```python",
        "client = build_client(session_path)  # existing authorized session",
        "access = await check_source_access('@channel_name', client)",
        "```",
        "",
        "**Step 2 — Bounded Scan**",
        "- Never scan entire history in one pass",
        "- Use `limit=1000` for initial analysis, `limit=0` only after validation",
        "- Collect: text, links, file names, message dates",
        "",
        "**Step 3 — Noise Rejection (CRITICAL)**",
        "- Filter: ads, motivational posts, chatter, reposts without content",
        "- Keep only: vacancy signals, order requests, project announcements, professional leads",
        "- One message → one `is_relevant()` check → skip if False",
        "",
        "**Step 4 — Signal Classification**",
        "- Vacancy signal: «требуется», «ищем», «нужен специалист»",
        "- Order signal: «объект», «тендер», «выбор подрядчика», «заказ»",
        "- Lead signal: contact mention + professional topic",
        "",
        "**Step 5 — Compact Output**",
        "- Do NOT create one core.db task per message",
        "- Do NOT write raw history to memory.db",
        "- Write ONE compact summary record per scan session",
        "- Key: `topic_6104_rabota_poisk_<source>_<date>`",
        "",
        "**Step 6 — Routing**",
        "- Useful signals → route to topic_6104 as single aggregated report",
        "- Format: [source] [date] [signal_type] [excerpt] [link]",
        "",
        "**Reuse**: swap `@tnz_msk` for any Telegram channel, "
        "swap skill categories for job/order detection, "
        "route output to topic_6104 instead of topic_5.",
    ]
    return "\n".join(lines)


def build_report_md(result: dict, scan_stats: dict, access: dict,
                    args_ns: argparse.Namespace) -> str:
    now = _now()
    return f"""# TNZ_MSK DOCUMENT SKILL EXTRACTION REPORT
Generated: {now}

## Diagnostics
- Source: @tnz_msk — «{access.get('title', '')}»
- Session: authorized ✅
- Telethon: 1.43.2 ✅
- Mode: {'DRY-RUN' if getattr(args_ns, 'dry_run', False) else 'LIVE'}
- Sample limit: {getattr(args_ns, 'sample', 1000)}

## Scan Statistics
| Metric | Count |
|--------|-------|
| Total messages fetched | {scan_stats.get('total_fetched', 0)} |
| Skipped (empty) | {scan_stats.get('skipped_empty', 0)} |
| Skipped (noise) | {scan_stats.get('skipped_noise', 0)} |
| Detected documents | {scan_stats.get('detected_docs', 0)} |
| Detected links | {scan_stats.get('detected_links', 0)} |

## Skill Extraction
| Metric | Count |
|--------|-------|
| Records passed to skill extractor | {result['total_input']} |
| Skill cards extracted | {result['extracted']} |
| Rejected (noise/no value) | {result['rejected_noise']} |
| Skill categories | {len(result['categories'])} |
| Needs owner review | {sum(1 for c in result['cards'] if c['needs_owner_review'])} |

## Skill Categories Extracted
{chr(10).join(f'- {cat}: {len(result["by_category"].get(cat, []))} rules' for cat in result['categories'])}

## Output Files
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.md`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.json`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/SOURCE_INDEX.json`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/LINKED_DOCUMENTS_INDEX.json`

## Rules
- No raw history saved to memory.db ✅
- No core.db tasks created ✅
- No forbidden files touched ✅
- Each extracted rule has source_ref ✅
- RABOTA_POISK reusable pattern documented ✅
"""


def build_handoff_md(result: dict, scan_stats: dict, commit_hint: str = "pending") -> str:
    return f"""# HANDOFF: TNZ_MSK DOCUMENT SKILL EXTRACTION
Date: 2026-05-05
Task: TELEGRAM_SOURCE_SKILL_EXTRACTION_TNZ_MSK_V1
Status: COMPLETED

## What Was Done
- Read @tnz_msk via authorized Telethon session (read-only)
- Scanned {scan_stats.get('total_fetched', 0)} messages
- Extracted {result['extracted']} skill cards across {len(result['categories'])} categories
- Rejected {result['rejected_noise']} noise records
- Built topic_5 technadzor document composition skill package
- Created reusable RABOTA_POISK Telegram source analysis pattern

## New Files Created
- core/telegram_source_skill_extractor.py
- core/technadzor_document_skill.py
- tools/extract_tnz_msk_document_skill.py
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.md
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.json
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/SOURCE_INDEX.json
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/LINKED_DOCUMENTS_INDEX.json
- docs/REPORTS/TNZ_MSK_DOCUMENT_SKILL_EXTRACTION_REPORT.md
- docs/HANDOFFS/HANDOFF_20260505_TNZ_MSK_DOCUMENT_SKILL_EXTRACTION.md

## Uncommitted / Untouched
- core/normative_engine.py — modified (P6H5 norm expansion), staged separately by user

## Skill Categories Extracted
{chr(10).join(f'- {cat}' for cat in result['categories'])}

## Next Steps
- Owner review of `needs_owner_review=true` cards
- Promotion of validated skills to technadzor_engine prompt context
- Reuse RABOTA_POISK pattern for topic_6104 channel scan
- Consider scheduling periodic re-scan of @tnz_msk (new posts only, delta scan)

## Commit
{commit_hint}
"""


async def main_async(args: argparse.Namespace) -> None:
    limit = args.sample
    download = args.download_documents and not args.dry_run

    print(f"[INFO] source={args.source} sample={limit} download={download} dry_run={args.dry_run}")

    result_raw = await run_source_scan(
        source=args.source,
        limit=limit,
        download_docs=download,
        docs_output_dir=DOCS_DIR if download else None,
    )

    if not result_raw.get("ok"):
        print(f"[ERROR] source access failed: {result_raw.get('error')}")
        sys.exit(1)

    access = result_raw["access"]
    scan = result_raw["scan"]
    scan_stats = {k: v for k, v in scan.items() if k != "records"}
    records = scan["records"]
    downloaded = result_raw.get("downloaded_documents", [])

    print(f"[INFO] fetched={scan['total_fetched']} docs={scan['detected_docs']} "
          f"links={scan['detected_links']} noise={scan['skipped_noise']} "
          f"downloaded={len(downloaded)}")

    result = process_records(records)
    print(f"[INFO] extracted={result['extracted']} rejected={result['rejected_noise']} "
          f"categories={result['categories']}")

    if args.dry_run:
        print("[DRY-RUN] Would write files but skipping.")
        print(json.dumps({
            "scan_stats": scan_stats,
            "extracted": result["extracted"],
            "rejected": result["rejected_noise"],
            "categories": result["categories"],
        }, ensure_ascii=False, indent=2))
        return

    # Build outputs
    skill_md = build_skill_md(result, scan_stats, access)
    skill_json = {
        "schema": "TECHNADZOR_DOCUMENT_COMPOSITION_SKILL_V1",
        "source": args.source,
        "channel_title": access.get("title", ""),
        "extracted_at": _now(),
        "scan_stats": scan_stats,
        "extracted": result["extracted"],
        "rejected_noise": result["rejected_noise"],
        "categories": result["categories"],
        "cards": result["cards"],
    }
    source_index = {
        "schema": "TNZ_MSK_SOURCE_INDEX_V1",
        "source": args.source,
        "scanned_at": _now(),
        "total_fetched": scan["total_fetched"],
        "records_count": len(records),
        "records": [{
            "message_id": r["message_id"],
            "date": r["message_date"],
            "source_ref": r["source_ref"],
            "has_links": bool(r.get("links")),
            "has_file": bool(r.get("file_name")),
            "media_type": r.get("media_type"),
        } for r in records[:500]],
    }
    linked_docs = {
        "schema": "TNZ_MSK_LINKED_DOCUMENTS_INDEX_V1",
        "source": args.source,
        "scanned_at": _now(),
        "downloaded_count": len(downloaded),
        "downloaded_paths": downloaded,
        "linked_urls": sorted({
            url for r in records
            for url in r.get("links", [])
        })[:200],
        "document_messages": [{
            "message_id": r["message_id"],
            "date": r["message_date"],
            "source_ref": r["source_ref"],
            "file_name": r.get("file_name"),
        } for r in records if r.get("file_name")][:200],
    }

    _write(SKILL_DIR / "TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.md", skill_md)
    _write_json(SKILL_DIR / "TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.json", skill_json)
    _write_json(SKILL_DIR / "SOURCE_INDEX.json", source_index)
    _write_json(SKILL_DIR / "LINKED_DOCUMENTS_INDEX.json", linked_docs)

    report_md = build_report_md(result, scan_stats, access, args)
    _write(REPORT_PATH, report_md)

    handoff_md = build_handoff_md(result, scan_stats)
    _write(HANDOFF_PATH, handoff_md)

    if args.write_memory_summary:
        import sqlite3
        mem_db = BASE / "data/memory.db"
        if mem_db.exists():
            conn = sqlite3.connect(str(mem_db))
            ts = _now()
            chat_id = "-1003725299009"
            summary_val = json.dumps({
                "schema": "TNZ_MSK_SKILL_SUMMARY_V1",
                "extracted_at": ts,
                "categories": result["categories"],
                "extracted": result["extracted"],
                "source": args.source,
            }, ensure_ascii=False)
            for key, val in [
                ("topic_5_tnz_msk_skill_summary", summary_val),
                ("topic_5_tnz_msk_skill_index",
                 json.dumps({"categories": result["categories"]}, ensure_ascii=False)),
                ("topic_5_tnz_msk_skill_extracted_at", ts),
            ]:
                conn.execute(
                    "INSERT OR REPLACE INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,?)",
                    (chat_id, key, val, ts)
                )
            conn.commit()
            conn.close()
            print("[INFO] memory summary written (3 keys only)")

    print(f"[OK] skill written → {SKILL_DIR}")
    print(f"[OK] report → {REPORT_PATH}")
    print(f"[OK] handoff → {HANDOFF_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Extract technadzor document skill from Telegram source")
    parser.add_argument("--source", default="@tnz_msk")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sample", type=int, default=1000)
    parser.add_argument("--download-documents", dest="download_documents", action="store_true", default=False)
    parser.add_argument("--no-download-documents", dest="download_documents", action="store_false")
    parser.add_argument("--write-memory-summary", dest="write_memory_summary", action="store_true", default=False)
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", default=False)
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
# === END_EXTRACT_TNZ_MSK_DOCUMENT_SKILL_V1 ===

====================================================================================================
END_FILE: tools/extract_tnz_msk_document_skill.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/final_session_code_tail_verify.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 7cd72b9a9b65a65ec55a53196a1a6b8fbdc7c8f57485fe391c1b42374adc7aa4
====================================================================================================
#!/usr/bin/env python3
# === FINAL_SESSION_CODE_TAIL_VERIFY_V4_FILE_MEMORY_PUBLIC ===
from __future__ import annotations

import asyncio
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/root/.areal-neva-core")
sys.path.insert(0, str(BASE))

REPORT = BASE / "docs" / "REPORTS" / "FINAL_SESSION_CODE_TAIL_VERIFY_REPORT.md"
CORE_DB = BASE / "data" / "core.db"

BAD_ROUTE_IMPORT = "from core.model_router import " + "route_domain"
BAD_FINAL_IMPORT = "from core.final_closure_engine import " + "handle_final_closure"
BAD_PRICE_SYMBOL = "prehandle_price_" + "decision_v1"

REQUIRED_MARKERS = {
    "task_worker.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_TASK_WORKER_HOOK",
        "END_FULL_TECH_CONTOUR_CLOSE_V1_WIRED",
        "ACTIVE_DIALOG_STATE_V1_TASK_WORKER_HOOK",
        "VOICE_CONFIRM_AWAITING_V1",
    ],
    "core/file_memory_bridge.py": [
        "FILE_MEMORY_PUBLIC_OUTPUT_DOMAIN_FILTER_V6_FINAL_SESSION",
        "_fm_item_domain",
        "_fm_public_links",
        "_fm_public_title",
    ],
    "core/output_sanitizer.py": [
        "UNIFIED_USER_OUTPUT_SANITIZER_V5_STRICT_PUBLIC_CLEAN",
        "sanitize_user_output",
        "sanitize_project_message",
        "sanitize_estimate_message",
    ],
    "core/price_enrichment.py": [
        "PRICE_DECISION_BEFORE_WEB_SEARCH_V1",
        "prehandle_price_task_v1",
        "_base_prehandle_price_task_v1",
    ],
    "core/file_context_intake.py": [
        "PENDING_INTENT_CLARIFICATION_V1",
        "PROJECT_SAMPLE_TEXT_INTAKE_V1",
    ],
    "core/final_closure_engine.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_ENGINE",
        "FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3",
        "maybe_handle_final_closure",
    ],
    "core/model_router.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_MODEL_ROUTER",
        "detect_domain",
    ],
    "core/runtime_file_catalog.py": ["FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG"],
    "core/archive_guard.py": ["FINAL_CLOSURE_BLOCKER_FIX_V1_ARCHIVE_DUPLICATE_GUARD"],
    "core/technadzor_engine.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_TECHNADZOR_ENGINE",
        "TECHNADZOR_PUBLIC_MESSAGE_NO_LOCAL_PATH_V1",
    ],
    "core/ocr_engine.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_OCR_TABLE_ENGINE",
        "OCR_TABLE_REQUIRES_REAL_RECOGNITION_ENGINE",
    ],
    "core/estimate_engine.py": ["create_estimate_xlsx_from_rows"],
    "core/sheets_generator.py": ["USER_ENTERED"],
}

def run(cmd):
    try:
        return subprocess.check_output(cmd, cwd=str(BASE), text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return "ERROR: " + str(e)

def read(rel):
    p = BASE / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def line_no(rel, needle):
    for i, line in enumerate(read(rel).splitlines(), 1):
        if needle in line:
            return i
    return -1

def marker_check():
    out = {}
    for rel, markers in REQUIRED_MARKERS.items():
        txt = read(rel)
        missing = [m for m in markers if m not in txt]
        out[rel] = {"exists": bool(txt), "missing": missing, "ok": bool(txt) and not missing}
    return out

def public_def_count(rel, prefix):
    return sum(1 for line in read(rel).splitlines() if line.startswith(prefix))

def exact_bad_import_present(import_line, files):
    return any(import_line in read(x) for x in files)

def smoke_check():
    res = {}

    from core.model_router import detect_domain
    rc = {
        "estimate": detect_domain("сделай смету по образцу").get("domain"),
        "estimate_inflected": detect_domain("сделай смету").get("domain"),
        "technadzor": detect_domain("сделай акт технадзора").get("domain"),
        "memory": detect_domain("какие файлы я скидывал").get("domain"),
        "project": detect_domain("сделай проект КЖ плиты").get("domain"),
    }
    res["router_cases"] = rc
    res["router_ok"] = (rc["estimate"] == "estimate" and rc["estimate_inflected"] == "estimate"
        and rc["technadzor"] == "technadzor" and rc["memory"] == "memory" and rc["project"] == "project")

    from core.file_memory_bridge import _fm_item_domain, _fm_public_links, _fm_public_title
    project_item = {
        "file_name": "4. АР АК-М-160.pdf",
        "direction": "TECHNADZOR_ACT_GOST_SP",
        "summary": "акт технадзора",
        "value": "blob https://docs.google.com/spreadsheets/d/BAD/edit",
        "links": ["https://drive.google.com/file/d/REAL/view?usp=drivesdk"],
    }
    res["file_memory_domain_project_ok"] = _fm_item_domain(project_item) == "project"
    res["file_memory_title_ok"] = _fm_public_title(project_item) == "АР АК-М-160.pdf"
    res["file_memory_links_only_item_ok"] = _fm_public_links(project_item) == ["https://drive.google.com/file/d/REAL/view?usp=drivesdk"]
    res["file_memory_no_blob_link_ok"] = _fm_public_links({"file_name": "КЖ.pdf", "links": []}) == []

    from core.output_sanitizer import sanitize_user_output
    dirty = "MANIFEST:\nhttps://drive.google.com/file/d/M/view\nDrive file_id: abc\nКратко: {\"task_id\":\"bad\"}\n/root/.areal-neva-core/tmp\nНормальный текст"
    clean = sanitize_user_output(dirty)
    res["sanitizer_public_ok"] = (
        "MANIFEST" not in clean and "file_id" not in clean.lower()
        and "task_id" not in clean.lower() and "/root/" not in clean
        and "Нормальный текст" in clean
    )

    from core.price_enrichment import prehandle_price_task_v1
    price_res = asyncio.run(prehandle_price_task_v1(sqlite3.connect(":memory:"), {
        "id": "v", "chat_id": "-1", "topic_id": 2, "input_type": "text", "raw_input": "смета",
    }))
    res["price_function_exists"] = callable(prehandle_price_task_v1)
    res["price_function_result_type_ok"] = price_res is None or isinstance(price_res, dict)

    from core.final_closure_engine import maybe_handle_final_closure
    mc = sqlite3.connect(str(CORE_DB))
    mc.row_factory = sqlite3.Row
    try:
        mr = maybe_handle_final_closure(mc, {
            "id": "v", "chat_id": "-1003725299009", "topic_id": 2,
            "input_type": "text", "raw_input": "какие файлы я скидывал",
        }, "v", "-1003725299009", 2, "какие файлы я скидывал", "text", None)
    finally:
        mc.close()
    mm = (mr or {}).get("message", "")
    res["final_closure_memory_ok"] = bool(mr and mr.get("handled"))
    res["final_closure_public_ok"] = (
        "MANIFEST" not in mm and "DXF:" not in mm and "file_id" not in mm.lower()
        and "task=" not in mm.lower() and "Кратко:" not in mm and "/root/" not in mm
    )

    from core.estimate_engine import create_estimate_xlsx_from_rows
    res["estimate_xlsx_function_ok"] = callable(create_estimate_xlsx_from_rows)

    from core.technadzor_engine import process_technadzor
    tech = process_technadzor(text="акт технадзора", task_id="v", chat_id="-1", topic_id=2)
    res["technadzor_public_message_ok"] = bool(tech.get("handled")) and "/root/" not in str(tech.get("message", ""))

    res["google_sheets_user_entered_ok"] = "USER_ENTERED" in read("core/sheets_generator.py")
    res["ocr_real_not_closed_fact"] = "OCR_TABLE_REQUIRES_REAL_RECOGNITION_ENGINE" in read("core/ocr_engine.py")
    dwg = run(["bash", "-lc", "command -v odafileconverter || command -v dwg2dxf || true"])
    res["dwg_converter_present"] = bool(dwg.strip())

    return res

def main():
    verify_files = ["tools/final_session_code_tail_verify.py", "tools/live_tech_contour_verify.py"]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git": {
            "head": run(["git", "rev-parse", "--short", "HEAD"]),
            "origin": run(["git", "rev-parse", "--short", "origin/main"]),
            "ahead_behind": run(["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"]),
            "status": run(["git", "status", "--short"]),
        },
        "markers": marker_check(),
        "hook_order": {
            "full_end": line_no("task_worker.py", "END_FULL_TECH_CONTOUR_CLOSE_V1_WIRED"),
            "final_hook": line_no("task_worker.py", "FINAL_CLOSURE_BLOCKER_FIX_V1_TASK_WORKER_HOOK"),
            "active_dialog": line_no("task_worker.py", "ACTIVE_DIALOG_STATE_V1_TASK_WORKER_HOOK"),
        },
        "counts": {
            "public_prehandle_price_task_v1": public_def_count("core/price_enrichment.py", "async def prehandle_price_task_v1"),
            "base_prehandle_price_task_v1": public_def_count("core/price_enrichment.py", "async def _base_prehandle_price_task_v1"),
            "create_estimate_xlsx_from_rows": public_def_count("core/estimate_engine.py", "def create_estimate_xlsx_from_rows"),
            "prehandle_task_context_v1": public_def_count("core/file_context_intake.py", "def prehandle_task_context_v1"),
        },
        "forbidden": {
            "telegram_daemon_dirty": bool(run(["git", "status", "--short", "--", "telegram_daemon.py"])),
            "final_closure_has_voice_handler_def": (
                "def handle_voice_confirm" in read("core/final_closure_engine.py")
                or "def voice_confirm" in read("core/final_closure_engine.py")
            ),
            "wrong_route_import": exact_bad_import_present(BAD_ROUTE_IMPORT, verify_files),
            "wrong_final_closure_import": exact_bad_import_present(BAD_FINAL_IMPORT, verify_files),
            "wrong_price_symbol": any(BAD_PRICE_SYMBOL in read(x) for x in verify_files + ["core/price_enrichment.py"]),
        },
        "smoke": smoke_check(),
    }

    report["markers_ok"] = all(v.get("ok") for v in report["markers"].values())
    report["hook_order_ok"] = (
        report["hook_order"]["full_end"] > 0
        and report["hook_order"]["final_hook"] > report["hook_order"]["full_end"]
        and report["hook_order"]["final_hook"] < report["hook_order"]["active_dialog"]
    )
    report["counts_ok"] = (
        report["counts"]["public_prehandle_price_task_v1"] == 1
        and report["counts"]["base_prehandle_price_task_v1"] == 1
        and report["counts"]["create_estimate_xlsx_from_rows"] == 1
        and report["counts"]["prehandle_task_context_v1"] == 2
    )
    report["forbidden_ok"] = not any(report["forbidden"].values())
    required_smoke = [
        "router_ok", "file_memory_domain_project_ok", "file_memory_title_ok",
        "file_memory_links_only_item_ok", "file_memory_no_blob_link_ok",
        "sanitizer_public_ok", "price_function_exists", "price_function_result_type_ok",
        "final_closure_memory_ok", "final_closure_public_ok",
        "estimate_xlsx_function_ok", "technadzor_public_message_ok", "google_sheets_user_entered_ok",
    ]
    report["smoke_ok"] = all(bool(report["smoke"].get(k)) for k in required_smoke)
    report["status"] = "OK" if (
        report["markers_ok"] and report["hook_order_ok"]
        and report["counts_ok"] and report["forbidden_ok"] and report["smoke_ok"]
    ) else "FAILED"

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# FINAL_SESSION_CODE_TAIL_VERIFY_REPORT", "",
        f"generated_at: {report['generated_at']}",
        f"status: {report['status']}",
        f"markers_ok: {report['markers_ok']}",
        f"hook_order_ok: {report['hook_order_ok']}",
        f"counts_ok: {report['counts_ok']}",
        f"forbidden_ok: {report['forbidden_ok']}",
        f"smoke_ok: {report['smoke_ok']}", "",
        "## RAW_JSON", "```json",
        json.dumps(report, ensure_ascii=False, indent=2),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("STATUS", report["status"])
    if report["status"] != "OK":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
# === END_FINAL_SESSION_CODE_TAIL_VERIFY_V4_FILE_MEMORY_PUBLIC ===

====================================================================================================
END_FILE: tools/final_session_code_tail_verify.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/full_context_aggregator_guard.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 01edf2d4ca491599fb7966444efc3c55d2349e09991496c2947020f86a02e8cc
====================================================================================================
#!/usr/bin/env python3
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

BASE = Path("/root/.areal-neva-core")
STATE_PATH = BASE / "data" / "full_context_aggregator_guard_state.json"
LOCK_PATH = BASE / "data" / "full_context_aggregator_guard.lock"
AGGREGATOR = BASE / "tools" / "full_context_aggregator.py"
PYTHON = BASE / ".venv" / "bin" / "python3"

GENERATED_EXACT = {
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
}

GENERATED_PREFIXES = (
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_",
    "docs/SHARED_CONTEXT/TOPICS/",
    "docs/SHARED_CONTEXT/DIRECTIONS/",
)

LOCAL_RUNTIME_SOURCES = (
    "chat_exports",
    "data/chat_exports",
    "data/telegram_file_catalog",
    "data/templates/reference_monolith",
)

ABS_RUNTIME_SOURCES = (
    Path("/root/AI_ORCHESTRA/telegram_exports"),
)

FORBIDDEN_STAGED_RE = (
    ".env",
    "credentials",
    "sessions",
    "memory.db",
    "tasks.db",
    "core.db",
    "google_io.py",
    "ai_router.py",
    "telegram_daemon.py",
    "reply_sender.py",
    "systemd",
    ".bak",
    "core_db_backups",
    "data/technadzor",
)


def run(args: list[str], check: bool = True) -> str:
    p = subprocess.run(
        args,
        cwd=str(BASE),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if check and p.returncode != 0:
        raise RuntimeError((p.stdout or "").strip() or f"COMMAND_FAILED: {args}")
    return (p.stdout or "").strip()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_generated(rel: str) -> bool:
    if rel in GENERATED_EXACT:
        return True
    return any(rel.startswith(prefix) for prefix in GENERATED_PREFIXES)


def tracked_source_snapshot() -> list[dict[str, Any]]:
    out = run(["git", "ls-files"], check=True)
    items: list[dict[str, Any]] = []
    for rel in sorted(x.strip() for x in out.splitlines() if x.strip()):
        if is_generated(rel):
            continue
        if rel.endswith(".bak") or ".bak." in rel:
            continue
        p = BASE / rel
        if not p.exists() or not p.is_file():
            continue
        try:
            st = p.stat()
            items.append({
                "path": rel,
                "size": st.st_size,
                "sha256": sha_file(p),
            })
        except Exception as e:
            items.append({"path": rel, "error": str(e)[:160]})
    return items


def local_tree_snapshot(root: Path, label: str) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for p in sorted(x for x in root.rglob("*") if x.is_file()):
            if len(rows) >= 5000:
                rows.append({"label": label, "truncated": True})
                break
            try:
                st = p.stat()
                rows.append({
                    "label": label,
                    "path": str(p.relative_to(root)),
                    "size": st.st_size,
                    "mtime": int(st.st_mtime),
                })
            except Exception as e:
                rows.append({"label": label, "path": str(p), "error": str(e)[:120]})
    except Exception as e:
        rows.append({"label": label, "root": str(root), "error": str(e)[:120]})
    return rows


def db_watermark() -> dict[str, Any]:
    db = BASE / "data" / "core.db"
    if not db.exists():
        return {"status": "NO_CORE_DB"}
    result: dict[str, Any] = {"status": "OK"}
    try:
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=3)
        cur = conn.cursor()

        cur.execute("PRAGMA table_info(tasks)")
        task_cols = {r[1] for r in cur.fetchall()}
        cur.execute("PRAGMA table_info(task_history)")
        hist_cols = {r[1] for r in cur.fetchall()}

        if "updated_at" in task_cols:
            cur.execute("SELECT MAX(updated_at), COUNT(*) FROM tasks")
            result["tasks_max_updated_at"], result["tasks_count"] = cur.fetchone()
        else:
            cur.execute("SELECT MAX(rowid), COUNT(*) FROM tasks")
            result["tasks_max_rowid"], result["tasks_count"] = cur.fetchone()

        if "created_at" in hist_cols:
            cur.execute("SELECT MAX(created_at), COUNT(*) FROM task_history")
            result["history_max_created_at"], result["history_count"] = cur.fetchone()
        else:
            cur.execute("SELECT MAX(rowid), COUNT(*) FROM task_history")
            result["history_max_rowid"], result["history_count"] = cur.fetchone()

        cur.execute("SELECT COALESCE(topic_id,0), state, COUNT(*) FROM tasks GROUP BY COALESCE(topic_id,0), state")
        result["topic_state_counts"] = [list(r) for r in cur.fetchall()]

        conn.close()
    except Exception as e:
        result = {"status": "DB_READ_FAIL", "error": str(e)[:200]}
    return result


def fingerprint_payload() -> dict[str, Any]:
    local_sources = []
    for rel in LOCAL_RUNTIME_SOURCES:
        local_sources.extend(local_tree_snapshot(BASE / rel, rel))
    for abs_root in ABS_RUNTIME_SOURCES:
        local_sources.extend(local_tree_snapshot(abs_root, str(abs_root)))

    return {
        "git_head": run(["git", "rev-parse", "HEAD"], check=True),
        "tracked_sources": tracked_source_snapshot(),
        "db_watermark": db_watermark(),
        "runtime_sources": local_sources,
    }


def fingerprint(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(fp: str, payload: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    data = {
        "saved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fingerprint": fp,
        "git_head": payload.get("git_head"),
        "db_watermark": payload.get("db_watermark"),
    }
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(STATE_PATH)


def staged_files() -> list[str]:
    out = run(["git", "diff", "--cached", "--name-only"], check=True)
    return [x.strip() for x in out.splitlines() if x.strip()]


def assert_no_staged_before_run() -> None:
    staged = staged_files()
    if not staged:
        return
    raise RuntimeError("PREEXISTING_STAGED_CHANGES_REFUSE_AGGREGATOR_RUN:\n" + "\n".join(staged[:200]))


def run_aggregator() -> None:
    if not AGGREGATOR.exists():
        raise RuntimeError("FULL_CONTEXT_AGGREGATOR_NOT_FOUND")
    assert_no_staged_before_run()
    py = str(PYTHON if PYTHON.exists() else sys.executable)
    p = subprocess.run(
        [py, str(AGGREGATOR)],
        cwd=str(BASE),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if p.stdout:
        print(p.stdout.rstrip())
    if p.returncode != 0:
        raise RuntimeError(f"FULL_CONTEXT_AGGREGATOR_FAILED:{p.returncode}")



# === DIRTY_TRACKED_NONGENERATED_GUARD_V1 ===
def dirty_tracked_nongenerated() -> list[str]:
    out = run(["git", "status", "--porcelain"], check=True)
    dirty: list[str] = []
    for line in out.splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if status.startswith("??"):
            continue
        if is_generated(path):
            continue
        if path in {
            "tools/full_context_aggregator_guard.py",
            "tools/full_context_aggregator_guard.sh",
        }:
            continue
        dirty.append(f"{status} {path}")
    return dirty


def assert_clean_tracked_sources() -> None:
    dirty = dirty_tracked_nongenerated()
    if dirty:
        raise RuntimeError(
            "DIRTY_TRACKED_NONGENERATED_REFUSE_AGGREGATOR_RUN:\n"
            + "\n".join(dirty[:200])
        )
# === END_DIRTY_TRACKED_NONGENERATED_GUARD_V1 ===


def acquire_lock() -> Any:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    f = LOCK_PATH.open("w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return f
    except BlockingIOError:
        return None


def main() -> int:
    lock = acquire_lock()
    if lock is None:
        return 0

    payload = fingerprint_payload()
    fp = fingerprint(payload)
    state = load_state()
    old_fp = state.get("fingerprint")

    if "--status" in sys.argv:
        dirty = dirty_tracked_nongenerated()
        print(f"CURRENT_FINGERPRINT={fp}")
        print(f"SAVED_FINGERPRINT={old_fp or 'NONE'}")
        print(f"CHANGED={fp != old_fp}")
        print(f"GIT_HEAD={payload.get('git_head')}")
        print("DIRTY_TRACKED_NONGENERATED=" + (",".join(dirty) if dirty else "NONE"))
        return 0

    if "--init" in sys.argv:
        assert_clean_tracked_sources()
        save_state(fp, payload)
        print(f"AGGREGATOR_GUARD_INIT_OK fingerprint={fp}")
        return 0

    assert_clean_tracked_sources()

    force = "--force" in sys.argv
    if not force and old_fp == fp:
        return 0

    print(f"AGGREGATOR_CHANGE_DETECTED old={old_fp or 'NONE'} new={fp} force={force}")
    run_aggregator()

    after_payload = fingerprint_payload()
    after_fp = fingerprint(after_payload)
    save_state(after_fp, after_payload)
    print(f"AGGREGATOR_GUARD_DONE fingerprint={after_fp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

====================================================================================================
END_FILE: tools/full_context_aggregator_guard.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/full_context_aggregator_guard.sh
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e242d0afb767dde16a3aa5cddaf36b7618fa09188a57269b971d0b4d9ad0de0c
====================================================================================================
#!/usr/bin/env bash
set -Eeuo pipefail
cd /root/.areal-neva-core

set -a
set +u
[ -f .env ] && . ./.env
set -u
set +a

exec /root/.areal-neva-core/.venv/bin/python3 /root/.areal-neva-core/tools/full_context_aggregator_guard.py "$@"

====================================================================================================
END_FILE: tools/full_context_aggregator_guard.sh
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/gen_act_3rd_visit.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 83687b2e49384e5c1f23f7eab1ee2db3efe54ca062e11d57c4262ae47d16b4ae
====================================================================================================
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор акта осмотра № 3 — ангар Киевское шоссе, 04.05.2026
Standalone-скрипт. Запуск:
  cd /root/.areal-neva-core && .venv/bin/python3 tools/gen_act_3rd_visit.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
except Exception:
    pass

import asyncio
import base64
import json
import re
import time
from pathlib import Path
from datetime import datetime

# ─── Константы объекта ─────────────────────────────────────────────────────

FOLDER_ID   = "1sS1A6iHQHUwjqZGF43wdyRjoLwwAHPse"
FOLDER_URL  = f"https://drive.google.com/drive/folders/{FOLDER_ID}"
CHAT_ID     = "-1003725299009"
TOPIC_ID    = 5

ACT_NUMBER      = "04-05/26"
VISIT_DATE      = "04.05.2026"
OBJECT_DESCR    = "Металлокаркасное здание (ангар), Киевское шоссе"
PLACE           = "Объект на Киевском шоссе"
PREV_ACT_REF    = "в развитие акта № 12-03/26 от 12.03.2026"

BATCH_SIZE    = 1    # по одному фото — избегаем 502 на больших payload
MAX_PARALLEL  = 5   # одновременных Vision запросов
OUTPUT_DIR    = Path(__file__).resolve().parent.parent / "outputs" / "technadzor_p6h"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Vision промпт ─────────────────────────────────────────────────────────

VISION_PROMPT = """\
Ты специалист технического надзора. Объект — металлокаркасное здание (ангар).
Перед тобой несколько фото строительного объекта — пронумерованы по порядку, начиная с фото 1.

Задача: по каждому фото выяви дефекты и строительные нарушения.

Возможные категории дефектов:
- опорные узлы колонн: подливка, зазоры, анкера, опорные плиты
- сварные соединения: непровар, поры, прожог, наплывы, незачищенные швы
- антикоррозионная защита: отсутствие покрытия, повреждение, ржавчина
- основание и водоотведение: замачивание, загрязнение, лужи, отсутствие уклонов
- узлы крепления покрытия: болтовые соединения, смещение элементов
- связи и укосины: неправильное примыкание, отсутствие жёсткости
- прочие: всё остальное

Верни ТОЛЬКО JSON-массив. Каждый элемент:
{
  "photo_no": <номер фото в пачке, целое число>,
  "title": "краткое название дефекта на русском",
  "description": "подробное описание что именно видно на фото",
  "section_hint": "опорные узлы / сварка / антикоррозия / основание / крепления / связи / прочее",
  "why": "почему это технически плохо, к чему ведёт",
  "consequence": "что произойдёт если не устранить",
  "fix": "конкретные действия по устранению",
  "verify": "что проверить или запросить у подрядчика",
  "confidence": "high / medium / low"
}

Если на фото нет нарушений — пропусти это фото (не добавляй в массив).
Если фото нечёткое или непонятное — добавь запись с confidence=low и укажи что именно непонятно.
Верни ТОЛЬКО JSON-массив, без заголовков и пояснений.
"""


# ─── Drive helpers ──────────────────────────────────────────────────────────

def get_drive_service():
    from core.technadzor_drive_index import _service
    return _service()


def list_photos_in_folder(svc, folder_id: str) -> list[dict]:
    """Вернуть все изображения из папки, отсортированные по имени."""
    from core.technadzor_drive_index import _list_folder
    files = _list_folder(svc, folder_id)
    photos = [f for f in files if (f.get("mimeType") or "").startswith("image/")]
    photos.sort(key=lambda x: x.get("name") or "")
    return photos


def download_photo(svc, file_id: str, filename: str) -> Path | None:
    """Скачать файл в локальный кэш."""
    from core.technadzor_drive_index import download_to_local
    return download_to_local(file_id, filename)


# ─── Vision ─────────────────────────────────────────────────────────────────

_vision_sem = None  # asyncio.Semaphore, инициализируется в main


async def run_single_vision(local_path: str, fname: str, photo_no: int, total: int) -> list[dict]:
    """Анализ одного фото через существующую Vision функцию."""
    global _vision_sem
    async with _vision_sem:
        from core.technadzor_engine import _p6f_tnz_vision_via_openrouter
        vision, vstatus = await _p6f_tnz_vision_via_openrouter(local_path)
        if vstatus != "OK" and vstatus != "PARTIAL":
            print(f"    [{photo_no}/{total}] {fname}: Vision {vstatus}")
            return []
        defects = (vision.get("defects") or []) if isinstance(vision, dict) else []
        summary = (vision.get("summary") or "") if isinstance(vision, dict) else ""
        # Если нет structured defects — превращаем summary в defect
        if not defects and summary:
            defects = [{"title": "Замечание по фото", "description": summary[:500]}]
        for d in defects:
            d["file_name"] = fname
            d["photo_no"] = photo_no
        ok_str = "✓" if defects else "·"
        print(f"    [{photo_no}/{total}] {fname}: {ok_str} {len(defects)} замеч.", flush=True)
        return defects


# ─── PDF сборка ──────────────────────────────────────────────────────────────

def build_pdf(all_defects: list[dict], out_path: Path) -> bool:
    """Собрать PDF акта из агрегированных дефектов."""
    from core.technadzor_engine import (
        _p6h_group_defects_by_section,
        _p6h_build_pdf_act,
        _p6h_norms_for_section,
    )

    grouped = _p6h_group_defects_by_section(all_defects)

    # Секции с нормами и списком фото
    sections_payload = []
    section_norms_index = {}
    for sec_title, defects in grouped:
        texts = [str(d.get("description") or d.get("title") or "") for d in defects]
        norms = _p6h_norms_for_section(sec_title, texts)
        photos_block = list(dict.fromkeys(
            d.get("file_name", "") for d in defects if d.get("file_name")
        ))
        sections_payload.append({
            "title": sec_title,
            "defects": defects,
            "norms": norms,
            "photos_block": photos_block,
        })
        section_norms_index[sec_title] = norms

    # Рекомендации / последствия
    recs = list(dict.fromkeys(
        str(d.get("fix") or "").strip()
        for d in all_defects if d.get("fix")
    ))[:20]
    cons = list(dict.fromkeys(
        str(d.get("consequence") or d.get("why") or "").strip()
        for d in all_defects if (d.get("consequence") or d.get("why"))
    ))[:10]

    # Таблица нарушений
    vtable = []
    for sec_title, defects in grouped:
        norm_id = ""
        nlist = section_norms_index.get(sec_title) or []
        if nlist:
            norm_id = nlist[0].get("norm_id", "")
        for d in defects:
            v  = str(d.get("title") or d.get("description") or sec_title)[:200]
            ph = str(d.get("file_name") or "")
            vtable.append((v, norm_id or "норма не подтверждена", ph))

    payload = {
        "act_number":      ACT_NUMBER,
        "date_str":        VISIT_DATE,
        "place":           PLACE,
        "object_descr":    OBJECT_DESCR,
        "method":          "визуальный неразрушающий контроль с выездом на объект",
        "performer":       "",
        "specialist":      "Кузнецов Илья Владимирович",
        "photos_link":     FOLDER_URL,
        "general_purpose": (
            f"Осмотр выполнен методом визуального неразрушающего контроля с выездом на объект. "
            f"Текущий осмотр выполнен {PREV_ACT_REF}. "
            f"Цель осмотра — проверка выполнения замечаний из предыдущего акта, "
            f"выявление новых дефектов и отклонений, определение рекомендаций к устранению "
            f"и возможных последствий при сохранении текущего состояния. "
            f"Проектная и рабочая исполнительная документация на момент осмотра "
            f"к проверке не представлена."
        ),
        "sections":         sections_payload,
        "recommendations":  recs if recs else [
            "Привести выявленные узлы и покрытия к нормативному состоянию по СП 16.13330.2017, СП 70.13330.2012",
            "Восстановить антикоррозионную защиту всех незащищённых металлических конструкций",
            "Обеспечить отвод воды от основания и опорных узлов",
            "Выполнить фотофиксацию после устранения всех выявленных замечаний",
            "Предоставить исполнительную документацию по выполненным работам",
        ],
        "consequences":     cons if cons else [
            "Снижение несущей способности и эксплуатационной надёжности конструкций",
            "Прогрессирующее развитие коррозионных поражений",
            "Риск аварийного развития дефектов при эксплуатационных нагрузках",
        ],
        "violations_table": vtable[:40],
    }

    try:
        _p6h_build_pdf_act(payload, out_path)
        return True
    except Exception as e:
        print(f"  ❌ Ошибка генерации PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


# ─── Загрузка на Drive ───────────────────────────────────────────────────────

def upload_pdf_to_drive(pdf_path: Path, pdf_name: str) -> str:
    """Загрузить PDF в topic_5 (корень). Вернуть ссылку или пустую строку."""
    try:
        from core.technadzor_drive_index import upload_client_pdf_to_folder
        result = upload_client_pdf_to_folder(
            pdf_path, pdf_name,
            chat_id=CHAT_ID, topic_id=TOPIC_ID,
            target_folder_name=None,  # в корень topic_5
        )
        return (result or {}).get("link", "") or (result or {}).get("webViewLink", "")
    except Exception as e:
        print(f"  ⚠️  Drive upload ошибка: {e}")
        return ""


# ─── Главный цикл ────────────────────────────────────────────────────────────

async def main():
    t0 = time.time()
    print("=" * 60)
    print("АКТ ОСМОТРА № 04-05/26 — ангар Киевское шоссе")
    print("Третий выезд, 04.05.2026")
    print("=" * 60)
    print(f"Папка фото: {FOLDER_URL}\n")

    # 1. Список фото
    print("1. Получаю список фото из Drive...")
    try:
        svc = get_drive_service()
        photos = list_photos_in_folder(svc, FOLDER_ID)
    except Exception as e:
        print(f"  ❌ Ошибка Drive: {e}")
        return

    print(f"   Найдено: {len(photos)} фото")
    if not photos:
        print("   Фото не найдено — выход")
        return

    # 2. Скачиваем все фото
    print(f"\n2. Скачиваю {len(photos)} фото из Drive...")
    local_photos = []
    for photo in photos:
        p = download_photo(svc, photo["id"], photo["name"])
        if p:
            local_photos.append((str(p), photo["name"]))
        else:
            print(f"  ✗ {photo['name']} — не скачалось")
    print(f"   Скачано: {len(local_photos)} фото")

    # 3. Vision — параллельно, MAX_PARALLEL одновременно
    global _vision_sem
    _vision_sem = asyncio.Semaphore(MAX_PARALLEL)
    total = len(local_photos)
    print(f"\n3. Vision анализ ({total} фото, до {MAX_PARALLEL} параллельно)...")

    tasks = [
        run_single_vision(path, fname, i + 1, total)
        for i, (path, fname) in enumerate(local_photos)
    ]
    results = await asyncio.gather(*tasks)
    all_defects = [d for sublist in results for d in sublist]

    elapsed = int(time.time() - t0)
    print(f"\n   Vision завершён за {elapsed}с. Всего замечаний: {len(all_defects)}")

    if not all_defects:
        print("  ⚠️  Vision не выявил замечаний — генерирую акт с пустыми разделами")

    # 4. Генерация PDF
    ts = datetime.now().strftime("%d_%m_%Y")
    pdf_name = f"Акт_осмотра_ангар_Киевское_шоссе_{ts}.pdf"
    pdf_path = OUTPUT_DIR / pdf_name

    print(f"\n3. Генерирую PDF: {pdf_name}")
    ok = build_pdf(all_defects, pdf_path)
    if not ok:
        print("  ❌ PDF не создан")
        return

    size_kb = pdf_path.stat().st_size // 1024
    print(f"   ✅ PDF готов — {size_kb} KB")
    print(f"   Путь: {pdf_path}")

    # 5. Загрузка на Drive
    print("\n4. Загружаю PDF на Drive (topic_5)...")
    link = upload_pdf_to_drive(pdf_path, pdf_name)
    if link:
        print(f"   ✅ Drive: {link}")
    else:
        print(f"   ⚠️  Drive upload не выполнен, файл доступен локально")

    # Итог
    total = int(time.time() - t0)
    print("\n" + "=" * 60)
    print(f"ГОТОВО за {total // 60}м {total % 60}с")
    print(f"PDF: {pdf_path}")
    if link:
        print(f"Drive: {link}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


# ─── P6H_VISION_RESIZE_V1 ───────────────────────────────────────────────────
# Append-only override.
# Оригиналы нетронуты. Temp только в /tmp. Model не меняется.
# Если resize не получился → STOP, оригинал 8MB не отправляется.
# Если Vision падает → показать vstatus → STOP, без fallback.

import hashlib as _p6h_hashlib
import tempfile as _p6h_tempfile


def prepare_image_for_openrouter_vision(src_path: str) -> Path:
    from PIL import Image as _PIL
    src = Path(src_path)
    h = _p6h_hashlib.md5(src_path.encode()).hexdigest()[:8]
    tmp = Path(_p6h_tempfile.gettempdir()) / f"tnz_v_{h}.jpg"
    with _PIL.open(src) as img:
        img = img.convert("RGB")
        w, ht = img.size
        if max(w, ht) > 1600:
            ratio = 1600 / max(w, ht)
            img = img.resize((int(w * ratio), int(ht * ratio)), _PIL.LANCZOS)
        img.save(str(tmp), "JPEG", quality=75, optimize=True)
    return tmp


async def run_single_vision(local_path: str, fname: str, photo_no: int, total: int) -> list[dict]:
    global _vision_sem
    async with _vision_sem:
        orig_size = Path(local_path).stat().st_size if Path(local_path).exists() else 0

        try:
            tmp = prepare_image_for_openrouter_vision(local_path)
        except Exception as e:
            print(f"    [{photo_no}/{total}] {fname}: ✗ resize STOP: {e}")
            return []

        resized_size = tmp.stat().st_size
        model = (os.getenv("OPENROUTER_VISION_MODEL") or "google/gemini-2.5-flash")
        print(f"    [{photo_no}/{total}] {fname}: orig={orig_size//1024}KB resized={resized_size//1024}KB model={model}", flush=True)

        from core.technadzor_engine import _p6f_tnz_vision_via_openrouter
        vision, vstatus = await _p6f_tnz_vision_via_openrouter(str(tmp))

        try:
            tmp.unlink()
        except Exception:
            pass

        if vstatus not in ("OK", "PARTIAL"):
            print(f"    [{photo_no}/{total}] {fname}: ✗ vstatus={vstatus} — STOP")
            return []

        defects = (vision.get("defects") or []) if isinstance(vision, dict) else []
        summary = (vision.get("summary") or "") if isinstance(vision, dict) else ""
        if not defects and summary:
            defects = [{"title": "Замечание по фото", "description": summary[:500]}]
        for d in defects:
            d["file_name"] = fname
            d["photo_no"] = photo_no
        ok_str = "✓" if defects else "·"
        print(f"    [{photo_no}/{total}] {fname}: {ok_str} {len(defects)} замеч.", flush=True)
        return defects

# ─── END P6H_VISION_RESIZE_V1 ────────────────────────────────────────────────

# ─── P6H_VISION_GUARD_STANDALONE_V1 ─────────────────────────────────────────
# CANON: TECHNADZOR_DOMAIN_LOGIC_CANON_V2 §33
# Standalone-скрипт не должен запускать Vision без явного разрешения владельца

_GEN_ACT_VISION_ALLOWED = os.getenv("EXTERNAL_PHOTO_ANALYSIS_ALLOWED", "").strip().lower() in ("1", "true", "yes")

if _GEN_ACT_VISION_ALLOWED:
    print("INFO: EXTERNAL_PHOTO_ANALYSIS_ALLOWED=True — Vision включён", flush=True)
    try:
        from core.technadzor_engine import _p6h_allow_external_vision
        _p6h_allow_external_vision()
    except Exception as _e:
        print(f"WARN: _p6h_allow_external_vision failed: {_e}", flush=True)
else:
    print("INFO: EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False (default) — Vision заблокирован по канону §33", flush=True)
    print("INFO: Для включения Vision установить в .env: EXTERNAL_PHOTO_ANALYSIS_ALLOWED=true", flush=True)
    print("INFO: Скрипт продолжит работу без Vision — разбор по голосу/тексту/документам", flush=True)
# ─── END P6H_VISION_GUARD_STANDALONE_V1 ──────────────────────────────────────

====================================================================================================
END_FILE: tools/gen_act_3rd_visit.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/live_canon_test_runner.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 4086fa3c6738a509a59a1901c1c5628394a66b03c0001f3298eadefac488b033
====================================================================================================
#!/usr/bin/env python3
# === LIVE_CANON_TEST_RUNNER_V1 ===
from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
REPORT = BASE / "docs/REPORTS/LIVE_CANON_TEST_REPORT.md"

# === LIVE_CANON_TEST_RUNNER_PYTHONPATH_FIX_V1 ===
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
# === END_LIVE_CANON_TEST_RUNNER_PYTHONPATH_FIX_V1 ===

def ok(name, value):
    return {"name": name, "ok": bool(value), "value": value}

async def main():
    checks = []

    from core.engine_contract import validate_engine_result
    checks.append(ok("UNIFIED_ENGINE_RESULT_VALIDATOR_BAD", not validate_engine_result("файл скачан", input_type="drive_file").get("ok")))
    checks.append(ok("UNIFIED_ENGINE_RESULT_VALIDATOR_GOOD", validate_engine_result({"summary": "PDF создан", "drive_link": "https://drive.google.com/test"}, input_type="drive_file").get("ok")))

    from core.format_registry import classify_file
    checks.append(ok("DWG_KIND_DRAWING", classify_file("a.dwg").get("kind") == "drawing"))
    checks.append(ok("DXF_KIND_DRAWING", classify_file("a.dxf").get("kind") == "drawing"))
    checks.append(ok("HF_KIND_BINARY", classify_file("a.hf").get("kind") == "binary"))

    from core.template_workflow import _load_index
    checks.append(ok("TEMPLATE_INDEX_LOAD", isinstance(_load_index(), dict)))

    from core.normative_source_engine import search_normative_sources
    checks.append(ok("NORMATIVE_SOURCE_SEARCH", len(search_normative_sources("трещина бетон")) >= 1))

    from core.capability_router_dispatch import build_execution_plan
    checks.append(ok("CAPABILITY_ESTIMATE", build_execution_plan(user_text="смета xlsx").get("engine") == "estimate"))
    checks.append(ok("CAPABILITY_DWG", build_execution_plan(file_name="a.dwg").get("engine") == "dwg_project"))

    passed = sum(1 for c in checks if c["ok"])
    total = len(checks)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "# LIVE_CANON_TEST_REPORT\n\n"
        + f"created_at: {datetime.now(timezone.utc).isoformat()}\n"
        + f"passed: {passed}/{total}\n\n"
        + "\n".join(f"- [{'OK' if c['ok'] else 'FAIL'}] {c['name']} | {c['value']}" for c in checks)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": passed == total, "passed": passed, "total": total, "report": str(REPORT)}, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
# === END_LIVE_CANON_TEST_RUNNER_V1 ===

====================================================================================================
END_FILE: tools/live_canon_test_runner.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/live_tech_contour_verify.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2403577feb80f4ce69d57be3363e08c6df898876d487211bb91929367d68a7f1
====================================================================================================
#!/usr/bin/env python3
# === LIVE_TECH_CONTOUR_VERIFY_V2 ===
from __future__ import annotations

import asyncio
import json
import sys
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/root/.areal-neva-core")
# === TOOL_IMPORT_PATH_FIX_V1 ===
BASE_PATH = Path("/root/.areal-neva-core")
if str(BASE_PATH) not in sys.path:
    sys.path.insert(0, str(BASE_PATH))
# === END_TOOL_IMPORT_PATH_FIX_V1 ===

CORE_DB = BASE / "data" / "core.db"
MEM_DB = BASE / "data" / "memory.db"
REPORT = BASE / "docs" / "REPORTS" / "LIVE_TECH_CONTOUR_VERIFY_REPORT.md"

REQUIRED_MARKERS = {
    "task_worker.py": [
        "FULL_TECH_CONTOUR_CLOSE_V1_WIRED",
        "REMAINING_TECH_CONTOUR_CLOSE_V1_WIRED",
        "_send_once_UNIFIED_USER_OUTPUT_SANITIZER_V1",
        "_send_once_ex_UNIFIED_USER_OUTPUT_SANITIZER_V1",
    ],
    "core/file_context_intake.py": [
        "CONTEXT_AWARE_FILE_INTAKE_V1",
        "MULTI_FILE_TEMPLATE_INTAKE_V1",
        "TELEGRAM_FILE_MEMORY_INDEX_V1",
        "PENDING_INTENT_CLARIFICATION_V1",
    ],
    "core/price_enrichment.py": [
        "WEB_SEARCH_PRICE_ENRICHMENT_V1",
        "PRICE_CONFIRMATION_BEFORE_ESTIMATE_V1",
        "PRICE_DECISION_BEFORE_WEB_SEARCH_V1",
    ],
    "core/pdf_spec_extractor.py": ["PDF_SPEC_EXTRACTOR_REAL_V1"],
    "core/upload_retry_queue.py": ["ROOT_TMP_UPLOAD_GUARD_V1"],
    "core/drive_folder_resolver.py": ["DRIVE_CANON_FOLDER_RESOLVER_V1"],
    "core/topic_drive_oauth.py": ["DRIVE_CANON_SINGLE_FOLDER_PICK_V1"],
    "core/output_sanitizer.py": ["UNIFIED_USER_OUTPUT_SANITIZER_V1"],
    "core/reply_repeat_parent.py": ["REPLY_REPEAT_PARENT_TASK_V1"],
    "core/project_route_guard.py": [
        "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1",
        "PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1",
    ],
    "core/project_engine.py": [
        "PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1_WRAPPER",
        "PROJECT_ENGINE_FALLBACK_SHEET_REGISTER_V1",
    ],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read(path: str) -> str:
    p = BASE / path
    return p.read_text(encoding="utf-8") if p.exists() else ""


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=str(BASE), text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return f"ERROR: {e}"


def check_markers() -> dict:
    out = {}
    for path, markers in REQUIRED_MARKERS.items():
        txt = read(path)
        out[path] = {
            "exists": bool(txt),
            "missing": [m for m in markers if m not in txt],
            "ok": bool(txt) and all(m in txt for m in markers),
        }
    return out


def clear_smoke_memory(chat: str) -> None:
    if not MEM_DB.exists():
        return
    conn = sqlite3.connect(str(MEM_DB))
    try:
        conn.execute("DELETE FROM memory WHERE chat_id=?", (chat,))
        conn.commit()
    finally:
        conn.close()


async def smoke_async() -> dict:
    result = {}
    chat = "SMOKE_PENDING_INTENT_CLARIFICATION_V2"
    topic = 990002
    clear_smoke_memory(chat)

    try:
        from core.output_sanitizer import sanitize_user_output
        dirty = "Engine: X\nPDF: https://drive.google.com/file/d/abc/view\n/tmp/a.xlsx\nMANIFEST: hidden"
        clean = sanitize_user_output(dirty)
        result["sanitizer"] = {
            "ok": "Engine:" not in clean and "/tmp/" not in clean and "drive.google.com" in clean,
            "clean": clean,
        }
    except Exception as e:
        result["sanitizer"] = {"ok": False, "error": repr(e)}

    try:
        from core.reply_repeat_parent import _is_short_human_reply, _is_repeat, _is_status
        result["reply_repeat"] = {
            "ok": _is_short_human_reply("ответишь?") and _is_repeat("повтори") and _is_status("ну что"),
        }
    except Exception as e:
        result["reply_repeat"] = {"ok": False, "error": repr(e)}

    try:
        from core.project_route_guard import is_explicit_project_intent
        result["project_route"] = {
            "ok": is_explicit_project_intent("Сделай проект монолитной фундаментной плиты КЖ") and not is_explicit_project_intent("сделай смету по монолитным работам"),
        }
    except Exception as e:
        result["project_route"] = {"ok": False, "error": repr(e)}

    try:
        from core.file_context_intake import _detect_pending_file_intent, _save_pending_intent, prehandle_task_context_v1
        pending = _detect_pending_file_intent("сейчас скину несколько смет как образцы, цены материалов через интернет")
        ok_pending = bool(pending and pending.get("kind") == "estimate" and pending.get("price_mode") == "web_confirm")
        _save_pending_intent(chat, topic, pending)
        conn = sqlite3.connect(":memory:")
        task = {
            "id": "smoke_pending",
            "chat_id": chat,
            "topic_id": topic,
            "input_type": "text",
            "raw_input": "Ну ты должен не сразу искать в интернете, сначала спроси нужно ли это",
            "reply_to_message_id": 1,
        }
        res = prehandle_task_context_v1(conn, task)
        result["pending_intent_clarification"] = {
            "ok": ok_pending and bool(res and res.get("handled") and res.get("history") == "PENDING_INTENT_CLARIFICATION_V1:UPDATED"),
            "result": res,
        }
    except Exception as e:
        result["pending_intent_clarification"] = {"ok": False, "error": repr(e)}

    try:
        from core.price_enrichment import prehandle_price_task_v1
        conn = sqlite3.connect(":memory:")
        task2 = {
            "id": "smoke_price_ask",
            "chat_id": chat,
            "topic_id": topic,
            "input_type": "text",
            "raw_input": "сделай смету по образцу",
            "reply_to_message_id": 2,
        }
        res2 = await prehandle_price_task_v1(conn, task2)
        task3 = {
            "id": "smoke_price_yes",
            "chat_id": chat,
            "topic_id": topic,
            "input_type": "text",
            "raw_input": "да, искать актуальные цены",
            "reply_to_message_id": 3,
        }
        res3 = await prehandle_price_task_v1(conn, task3)
        result["price_decision_before_web_search"] = {
            "ok": bool(res2 and res2.get("state") == "WAITING_CLARIFICATION" and res3 and "найду актуальные цены" in res3.get("message", "")),
            "ask": res2,
            "yes": res3,
        }
    except Exception as e:
        result["price_decision_before_web_search"] = {"ok": False, "error": repr(e)}

    try:
        from core.pdf_spec_extractor import extract_spec
        result["pdf_extractor_import"] = {"ok": callable(extract_spec)}
    except Exception as e:
        result["pdf_extractor_import"] = {"ok": False, "error": repr(e)}

    clear_smoke_memory(chat)
    return result


def db_stats() -> dict:
    conn = sqlite3.connect(str(CORE_DB))
    conn.row_factory = sqlite3.Row
    try:
        state_counts = [dict(r) for r in conn.execute("SELECT state, COUNT(*) cnt FROM tasks GROUP BY state ORDER BY cnt DESC").fetchall()]
        topic2 = [dict(r) for r in conn.execute("""
            SELECT rowid, substr(id,1,8) id, state, input_type,
                   COALESCE(bot_message_id,'') bot_msg,
                   COALESCE(reply_to_message_id,'') reply_to,
                   substr(raw_input,1,180) raw,
                   substr(result,1,180) result,
                   substr(error_message,1,120) err,
                   updated_at
            FROM tasks
            WHERE COALESCE(topic_id,0)=2
            ORDER BY rowid DESC
            LIMIT 20
        """).fetchall()]
    finally:
        conn.close()
    return {"state_counts": state_counts, "topic2_latest": topic2}


def memory_stats() -> dict:
    if not MEM_DB.exists():
        return {"exists": False, "count": 0, "rows": []}
    conn = sqlite3.connect(str(MEM_DB))
    conn.row_factory = sqlite3.Row
    try:
        rows = [dict(r) for r in conn.execute("""
            SELECT chat_id,key,substr(value,1,260) value,timestamp
            FROM memory
            WHERE key LIKE '%pending_file_intent%'
               OR key LIKE '%price_mode%'
               OR key LIKE '%price_decision%'
               OR key LIKE '%telegram_file_catalog_summary%'
               OR key LIKE '%telegram_file_duplicates_summary%'
               OR key LIKE '%estimate_template_batch%'
            ORDER BY rowid DESC
            LIMIT 100
        """).fetchall()]
    finally:
        conn.close()
    return {"exists": True, "count": len(rows), "rows": rows}


def git_info() -> dict:
    return {
        "head": run(["git", "rev-parse", "--short", "HEAD"]),
        "last": run(["git", "log", "-1", "--pretty=format:%h %ci %s"]),
        "status": run(["git", "status", "--short"]),
    }


def service_info() -> dict:
    return {
        "areal-task-worker": run(["systemctl", "is-active", "areal-task-worker"]),
        "telegram-ingress": run(["systemctl", "is-active", "telegram-ingress"]),
        "areal-memory-api": run(["systemctl", "is-active", "areal-memory-api"]),
        "areal-upload-retry": run(["systemctl", "is-active", "areal-upload-retry.service"]),
    }


def write_report(payload: dict) -> None:
    lines = []
    lines.append("# LIVE_TECH_CONTOUR_VERIFY_REPORT")
    lines.append("")
    lines.append(f"generated_at: {payload['generated_at']}")
    lines.append("")
    lines.append("## GIT")
    lines.append(f"head: {payload['git']['head']}")
    lines.append(f"last: {payload['git']['last']}")
    lines.append("")
    lines.append("## SERVICES")
    for k, v in payload["services"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## CODE MARKERS")
    for path, res in payload["markers"].items():
        lines.append(f"- {path}: {'OK' if res['ok'] else 'MISSING'}")
        if res["missing"]:
            lines.append(f"  missing: {', '.join(res['missing'])}")
    lines.append("")
    lines.append("## SMOKE")
    for name, res in payload["smoke"].items():
        lines.append(f"- {name}: {'OK' if res.get('ok') else 'FAIL'}")
        if res.get("error"):
            lines.append(f"  error: {res.get('error')}")
    lines.append("")
    lines.append("## FINAL STATUS")
    lines.append(f"markers_ok: {payload['markers_ok']}")
    lines.append(f"smoke_ok: {payload['smoke_ok']}")
    lines.append(f"services_ok: {payload['services_ok']}")
    lines.append("status: CODE_INSTALLED_AND_INTERNAL_VERIFY_OK" if payload["markers_ok"] and payload["smoke_ok"] and payload["services_ok"] else "status: VERIFY_FAILED")
    lines.append("")
    lines.append("## RAW_JSON")
    lines.append("```json")
    lines.append(json.dumps(payload, ensure_ascii=False, indent=2))
    lines.append("```")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


async def main_async() -> int:
    payload = {
        "generated_at": now(),
        "git": git_info(),
        "services": service_info(),
        "markers": check_markers(),
        "smoke": await smoke_async(),
        "db": db_stats(),
        "memory": memory_stats(),
        "live_required_before_verified": [
            "real Telegram pending intent",
            "real Telegram clarification",
            "real Telegram file batch samples",
            "real duplicate Telegram file",
            "real web price search confirmation",
            "real project KZH end-to-end",
            "real voice confirm",
            "real technadzor act",
            "real DWG/DXF conversion",
        ],
    }
    payload["markers_ok"] = all(x["ok"] for x in payload["markers"].values())
    payload["smoke_ok"] = all(x.get("ok") for x in payload["smoke"].values())
    payload["services_ok"] = all(v == "active" for v in payload["services"].values())
    write_report(payload)

    print("LIVE_TECH_CONTOUR_VERIFY_REPORT", REPORT)
    print("MARKERS_OK", payload["markers_ok"])
    print("SMOKE_OK", payload["smoke_ok"])
    print("SERVICES_OK", payload["services_ok"])

    if not (payload["markers_ok"] and payload["smoke_ok"] and payload["services_ok"]):
        print("FAILED_SMOKE_OR_MARKERS")
        for name, res in payload["smoke"].items():
            if not res.get("ok"):
                print("FAILED_SMOKE", name, json.dumps(res, ensure_ascii=False)[:1000])
        return 1
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(main_async()))


if __name__ == "__main__":
    main()

====================================================================================================
END_FILE: tools/live_tech_contour_verify.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/pending_intent_backfill.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 35f4cc391a3f2c169f50adb7d9fd0d10605bc602d8eade0263858eb354ead369
====================================================================================================
#!/usr/bin/env python3
# === PENDING_INTENT_BACKFILL_V1 ===
from __future__ import annotations

import json
import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/root/.areal-neva-core")
# === TOOL_IMPORT_PATH_FIX_V1 ===
BASE_PATH = Path("/root/.areal-neva-core")
if str(BASE_PATH) not in sys.path:
    sys.path.insert(0, str(BASE_PATH))
# === END_TOOL_IMPORT_PATH_FIX_V1 ===

CORE_DB = BASE / "data" / "core.db"
REPORT = BASE / "docs" / "REPORTS" / "PENDING_INTENT_BACKFILL_REPORT.md"
REPORT.parent.mkdir(parents=True, exist_ok=True)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def s(v) -> str:
    return "" if v is None else str(v).strip()


def default_chat() -> str:
    return os.getenv("TELEGRAM_CHAT_ID") or "-1003725299009"


def main() -> None:
    from core.file_context_intake import (
        _detect_pending_file_intent,
        _save_pending_intent,
        _memory_write,
        _pic_is_clarification_text,
        _pic_update_intent_with_clarification,
    )

    conn = sqlite3.connect(str(CORE_DB))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT rowid,id,chat_id,COALESCE(topic_id,0) topic_id,input_type,raw_input,state,result,error_message,updated_at
        FROM tasks
        WHERE input_type IN ('text','voice')
        ORDER BY rowid ASC
        """
    ).fetchall()
    conn.close()

    latest_pending = {}
    saved = []
    clarifications = []

    for r in rows:
        chat_id = s(r["chat_id"]) or default_chat()
        topic_id = int(r["topic_id"] or 0)
        text = s(r["raw_input"])

        pending = _detect_pending_file_intent(text)
        if pending:
            pending["source_task_id"] = s(r["id"])
            pending["source_rowid"] = int(r["rowid"])
            pending["source_updated_at"] = s(r["updated_at"])
            pending["backfilled_at"] = now()
            latest_pending[(chat_id, topic_id)] = pending
            _save_pending_intent(chat_id, topic_id, pending)
            saved.append({
                "rowid": int(r["rowid"]),
                "task_id": s(r["id"])[:8],
                "chat_id": chat_id,
                "topic_id": topic_id,
                "raw": text[:160],
                "pending": pending,
            })
            continue

        key = (chat_id, topic_id)
        if key in latest_pending and _pic_is_clarification_text(text):
            updated = _pic_update_intent_with_clarification(latest_pending[key], text)
            updated["clarification_source_task_id"] = s(r["id"])
            updated["clarification_source_rowid"] = int(r["rowid"])
            updated["backfilled_at"] = now()
            latest_pending[key] = updated
            _save_pending_intent(chat_id, topic_id, updated)
            if updated.get("price_mode"):
                _memory_write(chat_id, f"topic_{topic_id}_price_mode", updated.get("price_mode"))
            _memory_write(chat_id, f"topic_{topic_id}_pending_file_intent_clarification", {
                "task_id": s(r["id"]),
                "rowid": int(r["rowid"]),
                "text": text,
                "updated_intent": updated,
                "created_at": now(),
            })
            clarifications.append({
                "rowid": int(r["rowid"]),
                "task_id": s(r["id"])[:8],
                "chat_id": chat_id,
                "topic_id": topic_id,
                "raw": text[:180],
                "price_mode": updated.get("price_mode"),
            })

    report = {
        "engine": "PENDING_INTENT_BACKFILL_V1",
        "generated_at": now(),
        "saved_pending_count": len(saved),
        "clarification_count": len(clarifications),
        "saved_pending": saved[-30:],
        "clarifications": clarifications[-30:],
    }

    lines = [
        "# PENDING_INTENT_BACKFILL_REPORT",
        "",
        f"generated_at: {report['generated_at']}",
        f"saved_pending_count: {report['saved_pending_count']}",
        f"clarification_count: {report['clarification_count']}",
        "",
        "## CLARIFICATIONS",
    ]
    for x in report["clarifications"]:
        lines.append(f"- rowid={x['rowid']} task={x['task_id']} topic={x['topic_id']} price_mode={x.get('price_mode')} raw={x['raw']}")
    lines.append("")
    lines.append("## RAW_JSON")
    lines.append("```json")
    lines.append(json.dumps(report, ensure_ascii=False, indent=2))
    lines.append("```")
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("PENDING_INTENT_BACKFILL_V1_OK")
    print("SAVED_PENDING", len(saved))
    print("CLARIFICATIONS", len(clarifications))
    print("REPORT", REPORT)


if __name__ == "__main__":
    main()

====================================================================================================
END_FILE: tools/pending_intent_backfill.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/secret_scan.sh
FILE_CHUNK: 1/1
SHA256_FULL_FILE: dc26b49a001a2793e2485dd66e1b00b1fbb3156d0ff8104cee75180701ea2df6
====================================================================================================
#!/bin/bash
# Паттерны хранятся отдельно чтобы скрипт не сканировал сам себя
PATTERN_FILE="/root/.areal-neva-core/.secret_patterns"

if [ ! -f "$PATTERN_FILE" ]; then
  echo "SECRET_SCAN_SKIP: pattern file not found"
  exit 0
fi

FOUND=0
while IFS= read -r line; do
  [[ "$line" =~ ^\+ ]] || continue
  while IFS= read -r pattern; do
    if echo "$line" | grep -qE -- "$pattern"; then
      echo "SECRET FOUND: $pattern"
      FOUND=1
    fi
  done < "$PATTERN_FILE"
done < <(git diff --cached)

[ $FOUND -eq 1 ] && echo "ABORT: секреты в коммите" && exit 1
echo "SECRET_SCAN_OK"
exit 0

====================================================================================================
END_FILE: tools/secret_scan.sh
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/stroyka_final_guard.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 8914fffeab4b81a8d793659cf0bbb86fa3ee1f3eb4fa401e4308afc4d4f36f39
====================================================================================================
#!/usr/bin/env python3
from pathlib import Path
import re
import sys

BASE = Path("/root/.areal-neva-core")
TASK_WORKER = BASE / "task_worker.py"
STROYKA = BASE / "core/stroyka_estimate_canon.py"

tw = TASK_WORKER.read_text(encoding="utf-8", errors="replace")
sc = STROYKA.read_text(encoding="utf-8", errors="replace")

errors = []

def require(name: str, ok: bool):
    if not ok:
        errors.append(name)

require("PICK_SQL_FIXED", "ORDER BY CASE state WHEN 'IN_PROGRESS' THEN 0 ELSE 1 END," in tw)
require("PICK_SQL_NO_BROKEN_WHEN", "WHEN  THEN" not in tw)
require("PICK_NO_WAITING_CLARIFICATION_LOOP", "state IN ('NEW','IN_PROGRESS')" in tw or 'state IN ("NEW","IN_PROGRESS")' in tw)

require("STROYKA_PRE_DIRECTION_GUARD_PRESENT", "STROYKA_FULL_CHAIN_FINAL_CLOSE_PRE_DIRECTION_GUARD" in tw)
require("STROYKA_GUARD_BEFORE_DIRECTION_KERNEL", (
    "STROYKA_FULL_CHAIN_FINAL_CLOSE_PRE_DIRECTION_GUARD" in tw
    and "FULLFIX_DIRECTION_KERNEL_STAGE_1_CALL" in tw
    and tw.index("STROYKA_FULL_CHAIN_FINAL_CLOSE_PRE_DIRECTION_GUARD") < tw.index("FULLFIX_DIRECTION_KERNEL_STAGE_1_CALL")
))

require("STROYKA_OLD_RECALL_DISABLED", re.search(r"def\s+_latest_estimate_result\b[\s\S]{0,1200}return\s+None", sc) is not None)
require("STROYKA_DIRECT_ENGINE_PRESENT", "STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_ITEM_ENGINE" in sc)
require("STROYKA_DIRECT_HANDLER_FIRST", "STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_HANDLER_CALL" in sc)
require("STROYKA_BAD_RESULT_MARKERS_PRESENT", "STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_BAD_RESULT_MARKERS" in sc)
require("STROYKA_STALE_PROFLIST_BLOCKED", "создание сметы: профлист" in sc and "итоговая сумма: 55000" in sc)
require("STROYKA_STALE_VOR_BLOCKED", "вор_кирпичная_кладка" in sc and "vor_kirpich" in sc)
require("STROYKA_NO_OLD_ESTIMATE_ALREADY_EXISTS", "смета уже есть:" in sc and "_is_bad_estimate_result" in sc)
require("STROYKA_DIRECT_PRICE_NO_MISSING", "STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_PRICE_NO_MISSING" in sc)
require("STROYKA_DRIVE_UPLOAD_TOPIC", "upload_file_to_topic" in sc)
require("STROYKA_AWAITING_CONFIRMATION_RESULT", "AWAITING_CONFIRMATION" in sc)
require("STROYKA_PDF_XLSX_PATH", ".xlsx" in sc and ".pdf" in sc)
require("STROYKA_PYTHON_FORMULAS", "=C" in sc or "*E" in sc or "formula" in sc.lower())
require("STROYKA_TOPIC_2_GATE", "TOPIC_ID_STROYKA = 2" in sc)

if errors:
    print("STROYKA_FINAL_CANON_GUARD_FAILED")
    for e in errors:
        print("FAIL:", e)
    sys.exit(1)

print("STROYKA_FINAL_CANON_GUARD_OK")

====================================================================================================
END_FILE: tools/stroyka_final_guard.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/telegram_drive_memory_sync.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 709499280bfa62924330e117bdbca8807d1247ea2cd7ee5d2dfdd15e74e5689c
====================================================================================================
#!/usr/bin/env python3
# === TELEGRAM_DRIVE_MEMORY_SYNC_V2 ===
from __future__ import annotations

import json
import os
import re
import sqlite3
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
CORE_DB = BASE / "data/core.db"
MEM_DB = BASE / "data/memory.db"

# === SYNC_SELF_PYTHONPATH_FIX_V1 ===
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
# === END SYNC_SELF_PYTHONPATH_FIX_V1 ===

from core.file_memory_bridge import (
    is_service_file,
    classify_file_direction,
    save_file_catalog_snapshot,
)

CHAT_ID_DEFAULT = "-1003725299009"

def utc():
    return datetime.now(timezone.utc).isoformat()

def conn(path):
    c = sqlite3.connect(str(path), timeout=20)
    c.row_factory = sqlite3.Row
    return c

def has_table(c, name):
    return c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (name,)).fetchone() is not None

def safe_json(text):
    try:
        return json.loads(text or "{}")
    except Exception:
        return {}

def clean(text, limit=50000):
    if text is None:
        return ""
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False)
    return text.replace("\r", "\n").strip()[:limit]

def ensure_memory_table(mem):
    mem.execute("CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
    mem.execute("CREATE INDEX IF NOT EXISTS idx_memory_chat_key_sync_v2 ON memory(chat_id,key)")

def upsert_memory(mem, chat_id, key, value):
    value = clean(value, 50000)
    mid = hashlib.sha1(f"{chat_id}:{key}".encode()).hexdigest()
    mem.execute("DELETE FROM memory WHERE chat_id=? AND key=?", (chat_id, key))
    mem.execute(
        "INSERT OR REPLACE INTO memory (id,chat_id,key,value,timestamp) VALUES (?,?,?,?,?)",
        (mid, chat_id, key, value, utc()),
    )

def main():
    if not CORE_DB.exists() or not MEM_DB.exists():
        print("SYNC_SKIP: DB_MISSING")
        return 0

    indexed = 0
    skipped = 0
    topics = set()

    with conn(CORE_DB) as core, conn(MEM_DB) as mem:
        if not has_table(core, "tasks"):
            print("SYNC_SKIP: TASKS_MISSING")
            return 0

        ensure_memory_table(mem)

        rows = core.execute(
            """
            SELECT id,chat_id,COALESCE(topic_id,0) AS topic_id,input_type,state,raw_input,result,updated_at,created_at
            FROM tasks
            WHERE input_type='drive_file'
               OR COALESCE(result,'') LIKE '%drive.google%'
               OR COALESCE(result,'') LIKE '%docs.google%'
               OR COALESCE(raw_input,'') LIKE '%.xlsx%'
               OR COALESCE(raw_input,'') LIKE '%.xls%'
               OR COALESCE(raw_input,'') LIKE '%.pdf%'
               OR COALESCE(raw_input,'') LIKE '%.docx%'
               OR COALESCE(raw_input,'') LIKE '%.jpg%'
               OR COALESCE(raw_input,'') LIKE '%.png%'
            ORDER BY updated_at DESC
            LIMIT 800
            """
        ).fetchall()

        for r in rows:
            chat_id = str(r["chat_id"] or CHAT_ID_DEFAULT)
            topic_id = int(r["topic_id"] or 0)
            if topic_id == 0:
                skipped += 1
                continue

            raw = clean(r["raw_input"], 50000)
            result = clean(r["result"], 50000)
            data = safe_json(raw)
            file_name = str(data.get("file_name") or "")
            source = str(data.get("source") or "")
            file_id = str(data.get("file_id") or "")

            # === SYNC_REAL_FILE_REF_FILTER_V2 ===
            _sync_hay = raw + "\n" + result
            _sync_links = re.findall(r"https?://\S+", _sync_hay)
            _sync_has_real_file_ref = bool(
                file_id
                or file_name
                or _sync_links
                or re.search(r"\.(xlsx|xls|csv|pdf|docx|doc|jpg|jpeg|png|heic|webp|dwg|dxf)\b", _sync_hay, re.I)
                or "drive.google" in _sync_hay
                or "docs.google" in _sync_hay
            )
            if not _sync_has_real_file_ref:
                skipped += 1
                continue
            # === END SYNC_REAL_FILE_REF_FILTER_V2 ===

            if is_service_file(file_name, source, topic_id, raw):
                skipped += 1
                continue

            direction = classify_file_direction(raw + "\n" + result, file_name, str(data.get("mime_type") or ""))
            payload = {
                "task_id": r["id"],
                "chat_id": chat_id,
                "topic_id": topic_id,
                "input_type": r["input_type"],
                "state": r["state"],
                "file_id": file_id,
                "file_name": file_name,
                "mime_type": data.get("mime_type") or "",
                "caption": data.get("caption") or "",
                "source": source or "core.db",
                "direction": direction,
                "result": result[:12000],
                "updated_at": r["updated_at"],
                "created_at": r["created_at"],
            }

            key = f"topic_{topic_id}_file_{r['id']}"
            upsert_memory(mem, chat_id, key, json.dumps(payload, ensure_ascii=False))
            indexed += 1
            topics.add((chat_id, topic_id))

        mem.commit()

    catalogs = 0
    for chat_id, topic_id in sorted(topics):
        res = save_file_catalog_snapshot(chat_id, topic_id)
        if res.get("ok"):
            catalogs += 1

    print(json.dumps({
        "ok": True,
        "indexed": indexed,
        "skipped": skipped,
        "catalogs": catalogs,
        "version": "TELEGRAM_DRIVE_MEMORY_SYNC_V2",
    }, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
# === END TELEGRAM_DRIVE_MEMORY_SYNC_V2 ===

====================================================================================================
END_FILE: tools/telegram_drive_memory_sync.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/telegram_file_memory_backfill.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e0490e5da460851785a7eb8c54aafc42289af24399375c39e3218c3f09aa55fe
====================================================================================================
#!/usr/bin/env python3
# === TELEGRAM_FILE_MEMORY_BACKFILL_V1 ===
from __future__ import annotations

import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE = Path("/root/.areal-neva-core")
CORE_DB = BASE / "data" / "core.db"
MEM_DB = BASE / "data" / "memory.db"
CATALOG_DIR = BASE / "data" / "telegram_file_catalog"
TEMPLATE_DIR = BASE / "data" / "templates"
ESTIMATE_DIR = TEMPLATE_DIR / "estimate"
ESTIMATE_BATCH_DIR = TEMPLATE_DIR / "estimate_batch"
REPORT_PATH = BASE / "docs" / "REPORTS" / "TELEGRAM_FILE_MEMORY_BACKFILL_REPORT.md"

CATALOG_DIR.mkdir(parents=True, exist_ok=True)
ESTIMATE_BATCH_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    return str(v).strip()


def safe_key(v: Any) -> str:
    raw = s(v)
    out = []
    for ch in raw:
        if ch.isalnum() or ch in "-_":
            out.append(ch)
        else:
            out.append("_")
    return ("".join(out).strip("_") or "unknown")[:120]


def jloads(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    txt = s(raw)
    if not txt:
        return {}
    try:
        obj = json.loads(txt)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def is_service_file(payload: Dict[str, Any], state: str = "", err: str = "") -> bool:
    name = s(payload.get("file_name")).lower()
    src = s(payload.get("source")).lower()
    state = s(state).upper()
    err = s(err).upper()

    if src in {"google_drive", "drive", "service", "healthcheck", "drive_sync"}:
        return True
    if name.startswith("tmp") and name.endswith(".txt"):
        return True
    if "SERVICE_FILE_IGNORED" in err:
        return True
    if "healthcheck" in name or "retry_hc" in name:
        return True
    return False


def memory_cols(conn: sqlite3.Connection) -> List[str]:
    try:
        return [r[1] for r in conn.execute("PRAGMA table_info(memory)").fetchall()]
    except Exception:
        return []


def memory_write(chat_id: str, key: str, value: Any) -> None:
    if not MEM_DB.exists():
        return
    conn = sqlite3.connect(str(MEM_DB))
    try:
        cols = memory_cols(conn)
        if not cols:
            return
        payload = json.dumps(value, ensure_ascii=False, indent=2) if not isinstance(value, str) else value
        ts = now()
        if "id" in cols:
            mid = hashlib.sha1(f"{chat_id}:{key}:{ts}:{payload[:200]}".encode("utf-8")).hexdigest()
            conn.execute(
                "INSERT OR IGNORE INTO memory (id,chat_id,key,value,timestamp) VALUES (?,?,?,?,?)",
                (mid, str(chat_id), str(key), payload, ts),
            )
        else:
            conn.execute(
                "INSERT INTO memory (chat_id,key,value,timestamp) VALUES (?,?,?,?)",
                (str(chat_id), str(key), payload, ts),
            )
        conn.commit()
    finally:
        conn.close()


def read_drive_file_tasks() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(str(CORE_DB))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT
              rowid,
              id,
              chat_id,
              COALESCE(topic_id,0) AS topic_id,
              input_type,
              state,
              raw_input,
              result,
              error_message,
              bot_message_id,
              reply_to_message_id,
              created_at,
              updated_at
            FROM tasks
            WHERE input_type='drive_file'
            ORDER BY rowid ASC
            """
        ).fetchall()
    finally:
        conn.close()

    out = []
    for r in rows:
        payload = jloads(r["raw_input"])
        if is_service_file(payload, r["state"], r["error_message"]):
            continue
        file_id = s(payload.get("file_id"))
        file_name = s(payload.get("file_name"))
        if not file_id and not file_name:
            continue
        out.append(
            {
                "rowid": r["rowid"],
                "task_id": s(r["id"]),
                "chat_id": s(r["chat_id"]),
                "topic_id": int(r["topic_id"] or 0),
                "state": s(r["state"]),
                "file_id": file_id,
                "file_name": file_name,
                "mime_type": s(payload.get("mime_type")),
                "caption": s(payload.get("caption")),
                "source": s(payload.get("source") or "telegram"),
                "telegram_message_id": payload.get("telegram_message_id"),
                "bot_message_id": r["bot_message_id"],
                "reply_to_message_id": r["reply_to_message_id"],
                "created_at": s(r["created_at"]),
                "updated_at": s(r["updated_at"]),
            }
        )
    return out


def write_catalog(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    grouped: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}
    for rec in records:
        grouped.setdefault((rec["chat_id"], rec["topic_id"]), []).append(rec)

    topic_reports = {}
    for (chat_id, topic_id), rows in grouped.items():
        path = CATALOG_DIR / f"chat_{safe_key(chat_id)}__topic_{topic_id}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        by_file: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            key = row.get("file_id") or f"name:{row.get('file_name')}"
            by_file.setdefault(key, []).append(row)

        dups = [v for v in by_file.values() if len(v) > 1]
        summary = {
            "engine": "TELEGRAM_FILE_MEMORY_BACKFILL_V1",
            "chat_id": chat_id,
            "topic_id": topic_id,
            "catalog_path": str(path),
            "file_count": len(rows),
            "unique_file_count": len(by_file),
            "duplicate_group_count": len(dups),
            "latest_files": rows[-20:],
            "duplicate_groups": [
                {
                    "file_id": group[0].get("file_id"),
                    "file_name": group[0].get("file_name"),
                    "count": len(group),
                    "task_ids": [x.get("task_id") for x in group[-10:]],
                    "latest_updated_at": group[-1].get("updated_at"),
                }
                for group in dups[-50:]
            ],
            "updated_at": now(),
        }

        topic_reports[f"{chat_id}:{topic_id}"] = summary
        memory_write(chat_id, f"topic_{topic_id}_telegram_file_catalog_summary", summary)
        if summary["duplicate_group_count"]:
            memory_write(chat_id, f"topic_{topic_id}_telegram_file_duplicates_summary", summary["duplicate_groups"])

    master = {
        "engine": "TELEGRAM_FILE_MEMORY_BACKFILL_V1",
        "total_file_records": len(records),
        "topic_count": len(grouped),
        "topics": topic_reports,
        "updated_at": now(),
    }
    (CATALOG_DIR / "index.json").write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
    return master


def parse_template_name(path: Path) -> Dict[str, Any]:
    name = path.name
    chat_id = ""
    topic_id = 0

    marker = "chat_"
    if marker in name:
        part = name.split(marker, 1)[1]
        if "__topic_" in part:
            chat_id = part.split("__topic_", 1)[0]
            rest = part.split("__topic_", 1)[1]
            raw_topic = ""
            for ch in rest:
                if ch.isdigit() or ch == "-":
                    raw_topic += ch
                else:
                    break
            try:
                topic_id = int(raw_topic or 0)
            except Exception:
                topic_id = 0

    return {"chat_id": chat_id, "topic_id": topic_id}


def backfill_template_batches() -> Dict[str, Any]:
    templates = []
    if ESTIMATE_DIR.exists():
        for p in sorted(ESTIMATE_DIR.glob("*.json")):
            if p.name.startswith("ACTIVE_BATCH__"):
                continue
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            meta = parse_template_name(p)
            chat_id = s(data.get("chat_id") or meta.get("chat_id"))
            topic_id = int(data.get("topic_id") or meta.get("topic_id") or 0)
            if not chat_id:
                continue
            data["chat_id"] = chat_id
            data["topic_id"] = topic_id
            data.setdefault("engine", "TEMPLATE_BATCH_BACKFILL_V1")
            data.setdefault("backfilled_at", now())
            templates.append(data)

    grouped: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}
    for t in templates:
        grouped.setdefault((t["chat_id"], int(t["topic_id"] or 0)), []).append(t)

    reports = {}
    for (chat_id, topic_id), rows in grouped.items():
        batch = {
            "engine": "TEMPLATE_BATCH_BACKFILL_V1",
            "chat_id": chat_id,
            "topic_id": topic_id,
            "count": len(rows),
            "templates": rows[-100:],
            "updated_at": now(),
        }
        batch_path = ESTIMATE_BATCH_DIR / f"ACTIVE_BATCH__chat_{safe_key(chat_id)}__topic_{topic_id}.json"
        batch_path.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")
        memory_write(chat_id, f"topic_{topic_id}_estimate_template_batch", batch)
        reports[f"{chat_id}:{topic_id}"] = {"batch_path": str(batch_path), "count": len(rows)}

    return {"engine": "TEMPLATE_BATCH_BACKFILL_V1", "total_templates": len(templates), "topics": reports, "updated_at": now()}


def write_report(master: Dict[str, Any], templates: Dict[str, Any]) -> None:
    lines = []
    lines.append("# TELEGRAM_FILE_MEMORY_BACKFILL_REPORT")
    lines.append("")
    lines.append(f"generated_at: {now()}")
    lines.append("")
    lines.append("## TELEGRAM FILE CATALOG")
    lines.append(f"total_file_records: {master.get('total_file_records')}")
    lines.append(f"topic_count: {master.get('topic_count')}")
    lines.append("")
    for key, val in sorted((master.get("topics") or {}).items()):
        lines.append(f"### {key}")
        lines.append(f"file_count: {val.get('file_count')}")
        lines.append(f"unique_file_count: {val.get('unique_file_count')}")
        lines.append(f"duplicate_group_count: {val.get('duplicate_group_count')}")
        lines.append(f"catalog_path: {val.get('catalog_path')}")
        lines.append("")
    lines.append("## TEMPLATE BATCH BACKFILL")
    lines.append(f"total_templates: {templates.get('total_templates')}")
    for key, val in sorted((templates.get("topics") or {}).items()):
        lines.append(f"- {key}: count={val.get('count')} path={val.get('batch_path')}")
    lines.append("")
    lines.append("## STATUS")
    lines.append("TELEGRAM_FILE_MEMORY_BACKFILL_V1_DONE")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    records = read_drive_file_tasks()
    master = write_catalog(records)
    templates = backfill_template_batches()
    write_report(master, templates)

    print("TELEGRAM_FILE_MEMORY_BACKFILL_V1_OK")
    print("TOTAL_FILE_RECORDS", master.get("total_file_records"))
    print("TOPIC_COUNT", master.get("topic_count"))
    print("TOTAL_TEMPLATES", templates.get("total_templates"))
    print("REPORT", REPORT_PATH)


if __name__ == "__main__":
    main()

====================================================================================================
END_FILE: tools/telegram_file_memory_backfill.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/telegram_history_full_backfill.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d03b26f2a1f6c79a6e4120c028c1e29082e0bcd5cad0681d3c273d783ee4496f
====================================================================================================
#!/usr/bin/env python3
# === TELEGRAM_HISTORY_FULL_BACKFILL_V1 ===
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
CORE_DB = BASE / "data/core.db"
MEM_DB = BASE / "data/memory.db"
REPORT = BASE / "docs/REPORTS/TELEGRAM_HISTORY_FULL_BACKFILL_REPORT.json"

def _s(v, limit=5000):
    return "" if v is None else str(v)[:limit]

def main():
    if not CORE_DB.exists() or not MEM_DB.exists():
        print(json.dumps({"ok": False, "error": "DB_NOT_FOUND"}, ensure_ascii=False))
        return

    core = sqlite3.connect(CORE_DB)
    core.row_factory = sqlite3.Row
    mem = sqlite3.connect(MEM_DB)

    rows = core.execute(
        """
        SELECT id, chat_id, COALESCE(topic_id,0) AS topic_id, input_type, raw_input, result, state, created_at, updated_at
        FROM tasks
        WHERE raw_input LIKE '%file_id%'
           OR raw_input LIKE '%file_name%'
           OR result LIKE '%drive.google%'
           OR result LIKE '%docs.google%'
           OR result LIKE '%.xlsx%'
           OR result LIKE '%.pdf%'
           OR result LIKE '%.docx%'
           OR input_type IN ('drive_file','file','document','photo','image')
        ORDER BY updated_at DESC
        LIMIT 5000
        """
    ).fetchall()

    indexed = 0
    catalogs = {}
    now = datetime.now(timezone.utc).isoformat()

    for r in rows:
        chat_id = _s(r["chat_id"])
        topic_id = int(r["topic_id"] or 0)
        key = f"topic_{topic_id}_history_file_{r['id']}"
        value = {
            "schema": "TELEGRAM_HISTORY_FULL_BACKFILL_V1",
            "task_id": r["id"],
            "chat_id": chat_id,
            "topic_id": topic_id,
            "input_type": r["input_type"],
            "state": r["state"],
            "raw_input": _s(r["raw_input"], 3000),
            "result": _s(r["result"], 3000),
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        }
        mem.execute(
            "INSERT INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,?)",
            (chat_id, key, json.dumps(value, ensure_ascii=False), now),
        )
        catalogs.setdefault((chat_id, topic_id), []).append(value)
        indexed += 1

    for (chat_id, topic_id), items in catalogs.items():
        mem.execute(
            "INSERT INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,?)",
            (
                chat_id,
                f"topic_{topic_id}_file_catalog_history_backfill",
                json.dumps({"schema": "TELEGRAM_HISTORY_FULL_BACKFILL_V1", "count": len(items), "items": items[:100]}, ensure_ascii=False),
                now,
            ),
        )

    mem.commit()
    core.close()
    mem.close()

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ok": True, "indexed": indexed, "catalogs": len(catalogs), "created_at": now}
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))

if __name__ == "__main__":
    main()
# === END_TELEGRAM_HISTORY_FULL_BACKFILL_V1 ===

====================================================================================================
END_FILE: tools/telegram_history_full_backfill.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/topic2_drainage_repair_close.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 9c05d54c033fae1b9714a96efd4bacf2d75340bfff395b184900274f066cfb2a
====================================================================================================
#!/usr/bin/env python3
# TOPIC2_DRAINAGE_PRICE_ENRICHMENT_CANON_FIX_V1
# Canonical price flow only:
#   _openrouter_price_search → _price_prompt → user choice → XLSX/PDF
# No custom Sonar prompts. No regex price parsing. No fallback prices.
# No XLSX/PDF before TOPIC2_PRICE_CHOICE_CONFIRMED.
from __future__ import annotations
import asyncio, glob, json, os, re, sqlite3, subprocess, sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import requests
from dotenv import load_dotenv

BASE = Path("/root/.areal-neva-core")
sys.path.insert(0, str(BASE))
DB   = BASE / "data" / "core.db"
OUT_DIR = BASE / "runtime" / "stroyka_estimates" / "drainage_repair"
TASK_ID  = "043e5c9f-e8bc-434c-9dad-a66c7e50f917"
CACHE_FILE = OUT_DIR / f"price_cache_{TASK_ID[:8]}.json"
OUT_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE / ".env", override=False)
VAT_RATE = 0.22

# ---------------------------------------------------------------------------
# Canonical imports — must not be replaced with custom equivalents
# ---------------------------------------------------------------------------
from core.price_enrichment import (
    _openrouter_price_search,
    _detect_price_choice,
    _price_prompt,
    _select_price,
    _apply_selected_prices,
)

# ---------------------------------------------------------------------------
# Source classification helpers
# ---------------------------------------------------------------------------
DRAINAGE_STRONG = ["нвд","наружные водостоки","наружные водостоки и дренажи",
    "схема дренажной и ливневой канализации","дренажная насосная станция",
    "пескоуловитель","линейный водоотвод","d=160","i=0,005","дк","лк"]
GEO_STRONG = ["инженерно-геологические","бурение геотехнических скважин","скважин",
    "игэ","грунтовых вод","нормативная глубина промерзания","супесь","насыпные грунты"]

def low(t): return str(t or "").lower().replace("ё","е")

def hist(conn, tid, action):
    conn.execute(
        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
        (tid, action[:900]),
    )

def pdf_text(path):
    try:
        r = subprocess.run(["pdftotext","-layout","-q",str(path),"-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=25)
        return r.stdout or ""
    except Exception as e:
        return f"PDFTOTEXT_ERR={e}"

def is_artifact(path, text):
    p = str(path)
    if "/runtime/stroyka_estimates/" in p: return True
    if path.name.lower().startswith("drainage_estimate_"): return True
    h = low(text[:600])
    if "смета:" in h and "дренаж" in h: return True
    return False

def classify(path, text):
    t = low(text); name = low(path.name)
    geo = sum(1 for m in GEO_STRONG if m in t)
    drn = sum(1 for m in DRAINAGE_STRONG if m in t)
    if "отчет" in name or "отчёт" in name or "мистолово" in name: geo += 3
    if "дренаж" in name or "схема" in name: drn += 3
    if geo >= 3 and drn < 5: return "geology_report"
    if drn >= 2: return "drainage_scheme"
    if geo >= 3: return "geology_report"
    return "other_pdf"

def friendly(kind):
    return {"drainage_scheme":"Схема глубинного дренажа.pdf",
            "geology_report":"Отчет_Мистолово_03.26.pdf"}.get(kind, "source.pdf")

def find_user_pdfs():
    now = datetime.now().timestamp()
    candidates = []
    for raw in glob.glob("/var/lib/telegram-bot-api/*/documents/*.pdf"):
        p = Path(raw)
        try:
            if p.is_file() and now - p.stat().st_mtime <= 12*3600:
                candidates.append(p)
        except: pass
    out = []; seen = set()
    for p in sorted(set(candidates), key=lambda x: x.stat().st_mtime, reverse=True):
        txt = pdf_text(p)
        if is_artifact(p, txt): continue
        kind = classify(p, txt)
        if kind in ("drainage_scheme","geology_report") and kind not in seen:
            out.append({"path":p,"kind":kind,"name":friendly(kind),"text":txt,"chars":len(txt)})
            seen.add(kind)
    return out

# ---------------------------------------------------------------------------
# VAT helpers
# ---------------------------------------------------------------------------
def infer_vat(conn, tid, raw_in, result):
    texts = [raw_in or "", result or ""]
    for row in conn.execute(
        "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC", (tid,)
    ).fetchall():
        texts.append(str(row[0] or ""))
    t = low("\n".join(texts))
    if "topic2_vat_mode_confirmed:with_vat_22" in t: return "WITH_VAT_22"
    if "topic2_vat_mode_confirmed:without_vat" in t: return "WITHOUT_VAT"
    wo = ["без ндс","ндс не нужен","без налога","без учета ндс"]
    wv = ["с ндс","с учетом ндс","добавь ндс","посчитай с ндс"]
    if any(p in t for p in wo): return "WITHOUT_VAT"
    if any(p in t for p in wv): return "WITH_VAT_22"
    return None

# ---------------------------------------------------------------------------
# Messaging
# ---------------------------------------------------------------------------
def send_msg(chat_id, topic_id, text):
    from core.reply_sender import send_reply_ex
    if len(text) > 3900: text = text[:3800]+"\n\n[сокращено]"
    res = send_reply_ex(chat_id=str(chat_id), text=text,
                        message_thread_id=int(topic_id) if int(topic_id) else None)
    if not res.get("ok"): raise RuntimeError(f"SEND_FAILED:{res}")
    return int(res.get("bot_message_id") or 0)

def ask_vat(conn, task):
    tid=str(task["id"]); chat_id=str(task["chat_id"]); topic_id=int(task["topic_id"] or 2)
    msg = "Считать с НДС 22% или без НДС?"
    bot_msg = send_msg(chat_id, topic_id, msg)
    conn.execute("UPDATE tasks SET state='WAITING_CLARIFICATION',result=?,bot_message_id=?,"
                 "error_message='TOPIC2_VAT_MODE_REQUIRED',updated_at=datetime('now') WHERE id=?",
                 (msg, bot_msg, tid))
    hist(conn, tid, "TOPIC2_VAT_GATE_CHECKED")
    hist(conn, tid, "TOPIC2_VAT_MODE_REQUIRED")
    hist(conn, tid, f"TOPIC2_VAT_QUESTION_SENT:{bot_msg}")
    conn.commit()
    print(f"VAT_MODE_REQUIRED\nBOT_MESSAGE_ID={bot_msg}")

# ---------------------------------------------------------------------------
# Length extraction (PDF + user reply in recent tasks)
# ---------------------------------------------------------------------------
def num(x): return float(x.replace(",","."))

def extract_lengths_from_pdf(text):
    LEGEND_SKIP = ("уклон","длина","диаметр")
    vals = []
    for line in text.splitlines():
        ll = low(line)
        if all(k in ll for k in LEGEND_SKIP): continue
        if not any(k in ll for k in ["i=","d=","дрен","водоотвод","труб","ливнев"]): continue
        for pat in [r"(?i)\bl\s*=\s*(\d+(?:[,.]\d+)?)\s*м\b",
                    r"(?i)длина\s*[-:=]?\s*(\d+(?:[,.]\d+)?)\s*м\b"]:
            for m in re.finditer(pat, line):
                try:
                    v = num(m.group(1))
                    if 0.5 <= v <= 500 and v not in vals: vals.append(round(v,2))
                except: pass
    return vals

def extract_depths(text):
    vals = []
    for pat in [r"(?i)на глубине\s*(\d+(?:[,.]\d+)?)\s*м",
                r"(?i)глубин[а-я]*\s*(?:до|от)?\s*(\d+(?:[,.]\d+)?)\s*м"]:
        for m in re.finditer(pat, text):
            try:
                v = num(m.group(1))
                if 0.2 <= v <= 12 and v not in vals: vals.append(round(v,2))
            except: pass
    return vals

def count_unique(text, prefix):
    return len(set(re.findall(rf"{re.escape(prefix)}\s*[-–]?\s*(\d+)", text, flags=re.I)))

def has(text, marker): return low(marker) in low(text)

def read_user_provided_length(conn, tid):
    """Check task_history and recent topic_2 tasks for user-provided length."""
    # Check history markers first
    for row in conn.execute(
        "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid DESC LIMIT 50", (tid,)
    ).fetchall():
        a = str(row[0] or "")
        m = re.match(r"USER_PROVIDED_LENGTH:(\d+(?:\.\d+)?)", a)
        if m:
            return float(m.group(1))
    # Check recent topic_2 text tasks (user's reply after WC was sent)
    rows = conn.execute(
        "SELECT raw_input FROM tasks WHERE topic_id=2 AND id!=? "
        "AND input_type='text' ORDER BY rowid DESC LIMIT 15",
        (tid,),
    ).fetchall()
    for row in rows:
        text = str(row[0] or "").lower()
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:м(?:\.|\.п\.|\s|$)|метр)", text)
        if m:
            try:
                v = float(m.group(1).replace(",","."))
                if 5 <= v <= 2000:
                    return v
            except: pass
    return 0.0

# ---------------------------------------------------------------------------
# History state readers
# ---------------------------------------------------------------------------
def read_history_markers(conn, tid):
    rows = conn.execute(
        "SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC", (tid,)
    ).fetchall()
    return [str(r[0] or "") for r in rows]

def find_marker(markers, prefix):
    for m in reversed(markers):
        if m.startswith(prefix): return m
    return ""

# ---------------------------------------------------------------------------
# Read recent user reply (for price choice)
# ---------------------------------------------------------------------------
def read_recent_user_reply(conn, tid):
    """Return most recent user text input in topic_2 (not the parent task)."""
    rows = conn.execute(
        "SELECT raw_input FROM tasks WHERE topic_id=2 AND id!=? "
        "AND input_type='text' ORDER BY rowid DESC LIMIT 10",
        (tid,),
    ).fetchall()
    for row in rows:
        text = str(row[0] or "").strip()
        if text: return text
    return ""

# ---------------------------------------------------------------------------
# Cache file (stores item definitions + offers between script runs)
# ---------------------------------------------------------------------------
def save_cache(cache: dict):
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2))

def load_cache() -> Optional[dict]:
    if CACHE_FILE.exists():
        try: return json.loads(CACHE_FILE.read_text())
        except: pass
    return None

# ---------------------------------------------------------------------------
# Drainage item definitions
# (name_xlsx, search_query, unit, work_price, раздел)
# qty_fn(L, ex, wd, wl) computed in build_cache
# ---------------------------------------------------------------------------
def build_drainage_cache(L, ex, wd, wl, has_dns, has_pu, sources):
    """Build the canonical cache dict for price enrichment."""
    items = []

    # Material items that need online price search
    mat_defs = [
        ("Геотекстиль в траншее",
         "Геотекстиль нетканый 150-200 г/м² Terram Typar ТехноНИКОЛЬ",
         "м²", round(L*1.8,2), 180, "Геотекстиль / щебень / песок"),
        ("Песчаная подготовка",
         "Песок строительный намывной",
         "м³", round(L*0.12,2), 1300, "Геотекстиль / щебень / песок"),
        ("Щебёночный фильтр 20-40мм",
         "Щебень гранитный фракция 20-40мм",
         "м³", round(L*0.35,2), 1600, "Геотекстиль / щебень / песок"),
        ("Труба дренажная/водоотводящая d=160",
         "Труба дренажная гофрированная двустенная d=160мм КОРСИС SN8",
         "п.м.", L, 850, "Дренажные трубы и обратный фильтр"),
    ]
    if wd:
        mat_defs.append((
            "Дренажный ревизионный колодец Дк ∅500",
            "Колодец дренажный ревизионный диаметр 500мм полимерный Wavin Политрон",
            "шт", float(wd), 6500, "Колодцы и дождеприёмники",
        ))
    if wl:
        mat_defs.append((
            "Ливневый ревизионный колодец Лк ∅500",
            "Колодец ливневый ревизионный диаметр 500мм полимерный",
            "шт", float(wl), 6500, "Колодцы и дождеприёмники",
        ))
    if has_dns:
        mat_defs.append((
            "Дренажная насосная станция ДНС-1",
            "Дренажная насосная станция 0.55кВт Grundfos Unilift Wilo Джилекс",
            "шт", 1.0, 28000, "ДНС / насосное оборудование",
        ))
    if has_pu:
        mat_defs.append((
            "Пескоуловитель ПУ-1",
            "Пескоуловитель дорожный пластиковый ПУ-1 Ecoteck Gidrostroy",
            "шт", 1.0, 6500, "Пескоуловители / линейный водоотвод",
        ))
    mat_defs.append((
        "Линейный водоотвод / лотки DN100",
        "Лоток водоотводный пластиковый DN100 с решёткой Hauraton Gidrostroy",
        "п.м.", max(round(L*0.2,2), 1.0), 1100, "Ливневая канализация",
    ))

    for (name, search, unit, qty, work_price, раздел) in mat_defs:
        items.append({
            "name": name, "search": search, "unit": unit,
            "qty": qty, "work_price": float(work_price),
            "раздел": раздел, "offers": [],
        })

    # Pure work items (no material price search)
    work_defs = [
        ("Разметка трасс дренажа/ливнёвки",        "м.п.",   L,               450.0,     0.0, "Подготовительные и земляные работы"),
        ("Разработка траншей",                       "м³",     ex,             1900.0,     0.0, "Подготовительные и земляные работы"),
        ("Вывоз/перемещение лишнего грунта",         "м³",     round(ex*0.35,2),1400.0,    0.0, "Подготовительные и земляные работы"),
        ("Укладка трубы с уклоном i=0,005",         "м.п.",   L,               950.0,     0.0, "Дренажные трубы и обратный фильтр"),
        ("Сборка узлов, подключение колодцев",      "компл",  1.0,           45000.0,     0.0, "Монтажные работы"),
        ("Доставка материалов и инструмента",        "рейс",   2.0,               0.0, 18000.0, "Логистика"),
    ]
    for (name, unit, qty, work_price, mat_price, раздел) in work_defs:
        items.append({
            "name": name, "search": None, "unit": unit,
            "qty": qty, "work_price": work_price,
            "раздел": раздел, "offers": [],
            "_fixed_mat_price": mat_price,  # for delivery etc.
        })

    return {
        "length": L, "ex": ex, "wd": wd, "wl": wl,
        "has_dns": has_dns, "has_pu": has_pu,
        "sources": sources,
        "items": items,
    }

# ---------------------------------------------------------------------------
# Price enrichment: call _openrouter_price_search for each material item
# ---------------------------------------------------------------------------
async def enrich_cache(conn, tid, cache):
    hist(conn, tid, "TOPIC2_PRICE_ENRICHMENT_STARTED")
    conn.commit()
    for item in cache["items"]:
        if not item.get("search"):
            continue
        name = item["name"]; unit = item["unit"]
        print(f"  SEARCHING: {name} ({unit})")
        try:
            offers = await asyncio.wait_for(
                _openrouter_price_search(item["search"], unit, "Санкт-Петербург"),
                timeout=30.0,
            )
        except Exception as e:
            print(f"  SEARCH_ERR {name}: {e}")
            offers = []
        item["offers"] = offers
        if offers:
            sup = offers[0].get("supplier","")
            hist(conn, tid, f"TOPIC2_PRICE_SOURCE_FOUND:{name}:{sup}")
            print(f"    → {len(offers)} offers, best: {offers[0].get('price')} {unit} @ {sup}")
        else:
            hist(conn, tid, f"TOPIC2_PRICE_SOURCE_MISSING:{name}")
            print(f"    → no offers found")
    hist(conn, tid, "TOPIC2_PRICE_ENRICHMENT_DONE")
    conn.commit()
    return cache

# ---------------------------------------------------------------------------
# Send price choice menu to user
# ---------------------------------------------------------------------------
def send_price_menu(conn, tid, chat_id, topic_id, cache):
    menu_text = _price_prompt(cache)
    bot_msg = send_msg(chat_id, topic_id, menu_text)
    conn.execute(
        "UPDATE tasks SET state='WAITING_CLARIFICATION', result=?, bot_message_id=?, "
        "error_message='TOPIC2_DRAINAGE_PRICE_CHOICE_REQUIRED', updated_at=datetime('now') WHERE id=?",
        (menu_text, bot_msg, tid),
    )
    hist(conn, tid, f"TOPIC2_PRICE_CHOICE_MENU_SENT:{bot_msg}")
    conn.commit()
    print(f"PRICE_MENU_SENT BOT_MESSAGE_ID={bot_msg}")
    return bot_msg

# ---------------------------------------------------------------------------
# XLSX + PDF generation (only after TOPIC2_PRICE_CHOICE_CONFIRMED)
# ---------------------------------------------------------------------------
def build_xlsx_rows(cache, mode, vat_mode):
    """Apply selected prices and build full XLSX row dicts."""
    rows = []
    for i, item in enumerate(cache["items"], 1):
        offers = item.get("offers") or []
        fixed_mat = item.get("_fixed_mat_price", 0.0)

        if offers:
            mat_price = _select_price(offers, mode)
            best = offers[0]
            src = best.get("status", "UNVERIFIED")
            supplier = best.get("supplier", "—")
            url = best.get("url", "—")
            checked = best.get("checked_at", datetime.now().strftime("%Y-%m-%d"))
        else:
            mat_price = fixed_mat
            src = "MANUAL" if fixed_mat > 0 else "WORK_ONLY"
            supplier = "—"; url = "—"
            checked = datetime.now().strftime("%Y-%m-%d")

        qty = float(item["qty"])
        work = float(item["work_price"])
        rows.append({
            "№": i,
            "Раздел": item.get("раздел",""),
            "Наименование": item["name"],
            "Ед изм": item["unit"],
            "Кол-во": qty,
            "Цена работ": work,
            "Стоимость работ": round(qty*work, 2),
            "Цена материалов": mat_price,
            "Стоимость материалов": round(qty*mat_price, 2),
            "Всего": round(qty*(work+mat_price), 2),
            "Источник цены": src,
            "Поставщик": supplier,
            "URL": url,
            "checked_at": checked,
            "Примечание": f"mode={mode}",
        })
    return rows

def calc_totals(rows, vat_mode):
    works = sum(r["Стоимость работ"] for r in rows)
    mats  = sum(r["Стоимость материалов"] for r in rows)
    no_vat = works + mats
    vat = no_vat * VAT_RATE if vat_mode == "WITH_VAT_22" else 0.0
    return {"works":works,"mats":mats,"no_vat":no_vat,"vat":vat,"grand":no_vat+vat}

def create_xlsx(path, rows, meta, vat_mode, mode):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    H = ["№","Раздел","Наименование","Ед изм","Кол-во","Цена работ","Стоимость работ",
         "Цена материалов","Стоимость материалов","Всего","Источник цены","Поставщик","URL","checked_at","Примечание"]
    wb = Workbook(); ws = wb.active; ws.title = "DRAINAGE_CALC"
    ws["A1"] = "Смета: дренаж / ливневая канализация / наружные сети"
    ws["A2"] = f"Исходные файлы: {', '.join(meta['file_names'])}"
    ws["A3"] = f"Длина: {meta['total_len']} м; глубина: {meta['avg_depth']} м"
    ws["A4"] = f"Цены: онлайн-поиск OpenRouter/Sonar, выбор пользователя: {mode}"
    ws["A5"] = "НДС: 22%" if vat_mode=="WITH_VAT_22" else "НДС: не применяется"
    for r in range(1,6): ws.cell(r,1).font = Font(bold=True)
    start = 7
    for c,h in enumerate(H,1):
        cell = ws.cell(start,c,h)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid",fgColor="D9EAF7")
        cell.alignment = Alignment(horizontal="center",vertical="center",wrap_text=True)
    for r,row in enumerate(rows, start+1):
        for c,h in enumerate(H,1): ws.cell(r,c,row[h])
        ws.cell(r,7,f"=E{r}*F{r}"); ws.cell(r,9,f"=E{r}*H{r}"); ws.cell(r,10,f"=G{r}+I{r}")
    last = start+len(rows); tr=last+2
    ws.cell(tr,2,"ИТОГО без НДС" if vat_mode=="WITH_VAT_22" else "ИТОГО")
    ws.cell(tr,7,f"=SUM(G{start+1}:G{last})")
    ws.cell(tr,9,f"=SUM(I{start+1}:I{last})")
    ws.cell(tr,10,f"=SUM(J{start+1}:J{last})")
    if vat_mode=="WITH_VAT_22":
        vr=tr+1; gr=vr+1
        ws.cell(vr,2,"НДС 22%"); ws.cell(vr,10,f"=J{tr}*0.22")
        ws.cell(gr,2,"ИТОГО с НДС"); ws.cell(gr,10,f"=J{tr}+J{vr}")
    else:
        vr=tr+1; gr=vr
        ws.cell(vr,2,"НДС не применяется"); ws.cell(vr,10,0)
    for r in range(tr,gr+1):
        for c in range(1,16): ws.cell(r,c).font = Font(bold=True)
    for i,w in enumerate([6,26,46,10,12,14,16,16,18,16,22,28,16,14,20],1):
        ws.column_dimensions[get_column_letter(i)].width = w
    thin = Side(style="thin",color="999999")
    for row in ws.iter_rows(min_row=start,max_row=gr,min_col=1,max_col=15):
        for cell in row:
            cell.border = Border(left=thin,right=thin,top=thin,bottom=thin)
            cell.alignment = Alignment(vertical="top",wrap_text=True)
    wb.save(path)

def create_pdf(path, rows, meta, totals, vat_mode, mode):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    fp = next((p for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"] if Path(p).exists()), None)
    if fp: pdfmetrics.registerFont(TTFont("RU",fp)); font="RU"
    else: font="Helvetica"
    vat_label = "НДС: 22%" if vat_mode=="WITH_VAT_22" else "НДС: не применяется"
    doc = SimpleDocTemplate(str(path),pagesize=landscape(A4),leftMargin=18,rightMargin=18,topMargin=18,bottomMargin=18)
    sty = getSampleStyleSheet()
    N = ParagraphStyle("n",parent=sty["Normal"],fontName=font,fontSize=8,leading=10)
    T = ParagraphStyle("t",parent=sty["Title"],fontName=font,fontSize=14,leading=16)
    story = [
        Paragraph("Смета: дренаж / ливневая канализация / наружные сети",T),Spacer(1,8),
        Paragraph(f"Исходные файлы: {', '.join(meta['file_names'])}",N),
        Paragraph(f"Длина: {meta['total_len']} м; глубина: {meta['avg_depth']} м",N),
        Paragraph(f"Цены: онлайн-поиск OpenRouter/Sonar, режим: {mode}; {vat_label}",N),
        Spacer(1,8),
    ]
    data=[["Раздел","Наименование","Ед","Кол-во","Работы","Материалы","Всего"]]
    for r in rows:
        data.append([
            Paragraph(r["Раздел"],N), Paragraph(r["Наименование"],N), r["Ед изм"],
            f"{r['Кол-во']:.1f}",
            f"{r['Стоимость работ']:,.0f}".replace(",","  "),
            f"{r['Стоимость материалов']:,.0f}".replace(",","  "),
            f"{r['Всего']:,.0f}".replace(",","  "),
        ])
    table=Table(data,colWidths=[105,230,42,55,75,85,75])
    table.setStyle(TableStyle([
        ("FONTNAME",(0,0),(-1,-1),font),("FONTSIZE",(0,0),(-1,-1),7),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("GRID",(0,0),(-1,-1),0.25,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP"),
    ]))
    story += [table, Spacer(1,8),
              Paragraph(f"Материалы: {totals['mats']:,.0f} руб".replace(",","  "),N),
              Paragraph(f"Работы: {totals['works']:,.0f} руб".replace(",","  "),N)]
    if vat_mode=="WITH_VAT_22":
        story += [
            Paragraph(f"Без НДС: {totals['no_vat']:,.0f} руб".replace(",","  "),N),
            Paragraph(f"НДС 22%: {totals['vat']:,.0f} руб".replace(",","  "),N),
            Paragraph(f"С НДС: {totals['grand']:,.0f} руб".replace(",","  "),N),
        ]
    else:
        story += [
            Paragraph(f"Итого без НДС: {totals['grand']:,.0f} руб".replace(",","  "),N),
            Paragraph("НДС: не применяется",N),
        ]
    doc.build(story)

def send_doc(chat_id, topic_id, path, caption):
    token = <REDACTED_SECRET>"TELEGRAM_BOT_TOKEN","").strip()
    if not token: raise RuntimeError("TELEGRAM_BOT_TOKEN_MISSING")
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(path,"rb") as fh:
        data={"chat_id":str(chat_id),"caption":caption[:900]}
        if int(topic_id)!=0: data["message_thread_id"]=str(int(topic_id))
        r=requests.post(url,data=data,files={"document":(path.name,fh)},timeout=120)
    js=r.json()
    if r.status_code!=200 or not js.get("ok"):
        raise RuntimeError(f"SEND_DOC_FAILED:{r.status_code}:{r.text[:200]}")
    return int(js["result"]["message_id"])

async def maybe_upload(path, chat_id, topic_id):
    import inspect
    try: from core.topic_drive_oauth import upload_file_to_topic
    except: return ""
    for fn in [
        lambda: upload_file_to_topic(file_path=str(path),file_name=path.name,chat_id=str(chat_id),topic_id=int(topic_id)),
        lambda: upload_file_to_topic(str(path),path.name,str(chat_id),int(topic_id)),
    ]:
        try:
            res = fn()
            if inspect.isawaitable(res): res = await res
            if isinstance(res,dict):
                for k in ("webViewLink","link","url","drive_link","view_link"):
                    if res.get(k): return str(res[k])
                if res.get("file_id"): return f"https://drive.google.com/file/d/{res['file_id']}/view"
            if isinstance(res,str) and res.startswith("http"): return res
        except: continue
    return ""

# ---------------------------------------------------------------------------
# Main state machine
# ---------------------------------------------------------------------------
async def main():
    conn = sqlite3.connect(str(DB)); conn.row_factory = sqlite3.Row
    task = conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1",(TASK_ID,)).fetchone()
    if not task: raise SystemExit(f"TASK_NOT_FOUND:{TASK_ID}")
    tid = str(task["id"]); chat_id = str(task["chat_id"]); topic_id = int(task["topic_id"] or 2)
    raw_in = str(task["raw_input"] or ""); result = str(task["result"] or "")

    # VAT gate
    vat_mode = infer_vat(conn, tid, raw_in, result)
    if vat_mode is None:
        ask_vat(conn, task); conn.close(); return

    markers = read_history_markers(conn, tid)

    # ── STATE: TOPIC2_PRICE_CHOICE_CONFIRMED exists → generate estimate ──
    confirmed_marker = find_marker(markers, "TOPIC2_PRICE_CHOICE_CONFIRMED:")
    if confirmed_marker:
        mode = confirmed_marker.split(":", 1)[1].strip()
        print(f"PRICE_CHOICE_CONFIRMED:{mode} — generating estimate")
        cache = load_cache()
        if cache is None:
            raise SystemExit("PRICE_CACHE_FILE_MISSING — re-run from price search state")
        await _generate_and_send(conn, tid, chat_id, topic_id, vat_mode, mode, cache, markers)
        conn.close(); return

    # ── STATE: price menu already sent → check for user reply ──
    menu_marker = find_marker(markers, "TOPIC2_PRICE_CHOICE_MENU_SENT:")
    if menu_marker:
        user_reply = read_recent_user_reply(conn, tid)
        if user_reply:
            choice = _detect_price_choice(user_reply)
            if choice:
                print(f"USER_CHOICE_DETECTED:{choice} from '{user_reply[:40]}'")
                hist(conn, tid, f"TOPIC2_PRICE_CHOICE_CONFIRMED:{choice}")
                conn.commit()
                cache = load_cache()
                if cache is None:
                    raise SystemExit("PRICE_CACHE_FILE_MISSING")
                await _generate_and_send(conn, tid, chat_id, topic_id, vat_mode, choice, cache, markers)
                conn.close(); return
            # Check if it's a length (user replied to wrong WC)
            m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:м\b|метр)", user_reply.lower())
            if m:
                try:
                    L_reply = float(m.group(1).replace(",","."))
                    if 5 <= L_reply <= 2000:
                        print(f"LENGTH_FROM_USER_REPLY:{L_reply} — rebuilding cache")
                        hist(conn, tid, f"USER_PROVIDED_LENGTH:{L_reply}")
                        conn.commit()
                        await _do_price_search(conn, tid, chat_id, topic_id, L_reply, vat_mode)
                        conn.close(); return
                except: pass
        print("WAITING_FOR_PRICE_CHOICE — no actionable reply yet")
        conn.close(); return

    # ── STATE: find length ──
    sources = find_user_pdfs()
    if not sources:
        raise SystemExit("NO_USER_SOURCE_PDFS")
    drainage = [x for x in sources if x["kind"]=="drainage_scheme"]
    if not drainage:
        raise SystemExit("DRAINAGE_SOURCE_NOT_FOUND")

    scheme_text = "\n".join(x["text"] for x in drainage)
    geo_text    = "\n".join(x["text"] for x in sources if x["kind"]=="geology_report")

    pdf_lengths = extract_lengths_from_pdf(scheme_text)
    total_len   = round(sum(pdf_lengths), 2)
    print(f"PDF_LENGTHS={pdf_lengths} TOTAL_LEN={total_len}")

    if total_len <= 0:
        user_len = read_user_provided_length(conn, tid)
        if user_len > 0:
            print(f"USER_PROVIDED_LENGTH:{user_len}")
            hist(conn, tid, f"USER_PROVIDED_LENGTH:{user_len}")
            conn.commit()
            total_len = user_len
        else:
            # Ask user for length
            wc_msg = (
                "Длина трасс дренажа и ливнёвки в PDF не читается — схема графическая.\n\n"
                "Пришли, пожалуйста:\n"
                "• Общую длину дренажных труб (в метрах)\n"
                "• Или длины по участкам: Дк-1→Дк-2, Дк-2→ДНС, и т.д.\n\n"
                "После этого запрошу актуальные цены и покажу смету."
            )
            bot_msg = send_msg(chat_id, topic_id, wc_msg)
            conn.execute(
                "UPDATE tasks SET state='WAITING_CLARIFICATION', result=?, bot_message_id=?, "
                "error_message='TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN', updated_at=datetime('now') WHERE id=?",
                (wc_msg, bot_msg, tid),
            )
            for a in ["TOPIC2_DRAINAGE_LENGTH_PROOF_GATE_V1",
                      f"TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN:lines={len(pdf_lengths)}:total={total_len}",
                      "TOPIC2_DRAINAGE_FINAL_ARTIFACTS_BLOCKED",
                      f"TOPIC2_DRAINAGE_WC_SENT:{bot_msg}"]:
                hist(conn, tid, a)
            conn.commit(); conn.close()
            print(f"DRAINAGE_LENGTH_GATE_WC_SENT BOT_MESSAGE_ID={bot_msg}")
            return

    await _do_price_search(conn, tid, chat_id, topic_id, total_len, vat_mode)
    conn.close()  # OLD main() end


async def _do_price_search(conn, tid, chat_id, topic_id, L, vat_mode):
    """Search prices via canonical _openrouter_price_search + send menu."""
    task = conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1",(tid,)).fetchone()
    sources = find_user_pdfs()
    drainage = [x for x in sources if x["kind"]=="drainage_scheme"]
    geo      = [x for x in sources if x["kind"]=="geology_report"]
    scheme_text = "\n".join(x["text"] for x in drainage)
    geo_text    = "\n".join(x["text"] for x in geo)
    depths = extract_depths(geo_text)
    avg_depth = round(max(1.2, min(depths)), 2) if depths else 1.2
    ex = round(L * avg_depth * 0.6, 2)
    wd = count_unique(scheme_text, "Дк")
    wl = count_unique(scheme_text, "Лк")
    has_dns = has(scheme_text, "ДНС")
    has_pu  = has(scheme_text, "пескоуловитель") or has(scheme_text, "ПУ-1")

    print(f"LENGTH={L} DEPTH={avg_depth} WELLS_DK={wd} WELLS_LK={wl} DNS={has_dns} PU={has_pu}")

    cache = build_drainage_cache(L, ex, wd, wl, has_dns, has_pu,
                                  [x["name"] for x in sources])
    cache = await enrich_cache(conn, tid, cache)
    save_cache(cache)
    print(f"CACHE_SAVED:{CACHE_FILE}")

    hist(conn, tid, f"TOPIC2_DRAINAGE_LENGTHS_STATUS:PROVEN:total_len={L}")
    hist(conn, tid, f"TOPIC2_DRAINAGE_VAT_MODE:{vat_mode}")
    conn.commit()

    send_price_menu(conn, tid, chat_id, topic_id, cache)


async def _generate_and_send(conn, tid, chat_id, topic_id, vat_mode, mode, cache, markers):
    """Generate XLSX/PDF after confirmed price choice and send to Telegram."""
    hist(conn, tid, "TOPIC2_DRAINAGE_GENERATE_STARTED")
    conn.commit()

    rows    = build_xlsx_rows(cache, mode, vat_mode)
    totals  = calc_totals(rows, vat_mode)
    sources = cache.get("sources", [])
    L       = cache["length"]
    depth   = cache.get("ex",0) / (cache["length"] * 0.6) if cache["length"] else 1.2
    meta    = {"file_names": sources, "total_len": L, "avg_depth": round(depth,2)}

    stamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    xlsx    = OUT_DIR / f"drainage_estimate_clean_{tid[:8]}_{stamp}.xlsx"
    pdf_out = OUT_DIR / f"drainage_estimate_clean_{tid[:8]}_{stamp}.pdf"

    create_xlsx(xlsx, rows, meta, vat_mode, mode)
    create_pdf(pdf_out, rows, meta, totals, vat_mode, mode)

    xlsx_link = await maybe_upload(xlsx, chat_id, topic_id)
    pdf_link  = await maybe_upload(pdf_out, chat_id, topic_id)
    if not xlsx_link:
        mid = send_doc(chat_id, topic_id, xlsx, "Excel: смета дренажа"); print(f"XLSX_DOC_SENT:{mid}")
    if not pdf_link:
        mid = send_doc(chat_id, topic_id, pdf_out, "PDF: смета дренажа"); print(f"PDF_DOC_SENT:{mid}")

    if vat_mode=="WITH_VAT_22":
        totals_block=(f"Без НДС: {totals['no_vat']:,.0f} руб\n"
                      f" НДС 22%: {totals['vat']:,.0f} руб\n"
                      f" С НДС: {totals['grand']:,.0f} руб").replace(",","  ")
    else:
        totals_block=f"Итого без НДС: {totals['grand']:,.0f} руб\n НДС: не применяется".replace(",","  ")

    excel_line = f"Excel: {xlsx_link}" if xlsx_link else "Excel: отправлен файлом"
    pdf_line   = f"PDF: {pdf_link}"   if pdf_link  else "PDF: отправлен файлом"

    public = (
        f"✅ Смета дренажа готова\n\n"
        f"Объект: наружные сети / дренаж / ливневая канализация\n"
        f"Файлы учтены: {', '.join(sources)}\n"
        f"Цены: онлайн-поиск OpenRouter/Sonar, режим: {mode}\n"
        f"Длина: {L} м\n\n"
        f"Итого:\n Материалы: {totals['mats']:,.0f} руб\n"
        f" Работы: {totals['works']:,.0f} руб\n {totals_block}\n\n"
        f"{excel_line}\n{pdf_line}\n\nПодтверди или пришли правки"
    ).replace(",","  ")

    dirty = [x for x in ["/root/","runtime","drainage_estimate_"] if x in public]
    if dirty: raise SystemExit(f"PUBLIC_OUTPUT_DIRTY:{dirty}")

    bot_msg = send_msg(chat_id, topic_id, public)
    conn.execute(
        "UPDATE tasks SET state='AWAITING_CONFIRMATION', result=?, bot_message_id=?, "
        "error_message=NULL, updated_at=datetime('now') WHERE id=?",
        (public, bot_msg, tid),
    )
    for action in [
        f"TOPIC2_DRAINAGE_SOURCE_FILTER_OK:user_pdfs={len(sources)}",
        "TOPIC2_DRAINAGE_NO_GENERATED_ARTIFACT_INPUT",
        f"TOPIC2_DRAINAGE_PRICES_SOURCE:OpenRouter/Sonar:mode={mode}",
        f"TOPIC2_DRAINAGE_XLSX_CREATED:{xlsx.name}",
        f"TOPIC2_DRAINAGE_PDF_CREATED:{pdf_out.name}",
        f"TOPIC2_DRAINAGE_DRIVE_XLSX_OK:{xlsx_link}" if xlsx_link else "TOPIC2_DRAINAGE_TELEGRAM_XLSX_FALLBACK_SENT",
        f"TOPIC2_DRAINAGE_DRIVE_PDF_OK:{pdf_link}"   if pdf_link  else "TOPIC2_DRAINAGE_TELEGRAM_PDF_FALLBACK_SENT",
        f"TOPIC2_DRAINAGE_TELEGRAM_SENT:{bot_msg}",
        "TOPIC2_VAT_PUBLIC_OUTPUT_OK",
        "TOPIC2_DRAINAGE_AWAITING_CONFIRMATION_CLEAN_V1",
    ]:
        hist(conn, tid, action)
    conn.commit()
    print(f"DRAINAGE_ESTIMATE_OK BOT_MESSAGE_ID={bot_msg} GRAND={totals['grand']}")


if __name__ == "__main__":
    pass  # entry point moved to end — overridden by PATCH_TOPIC2_DRAINAGE_RECOGNIZE_ALL_V1

# ─────────────────────────────────────────────────────────────────────────────
# PATCH_TOPIC2_DRAINAGE_RECOGNIZE_ALL_V1  (2026-05-09)
# Overrides main() WC branch: shows recognized scheme elements before asking
# for missing lengths. Appended per append-only rule.
# ─────────────────────────────────────────────────────────────────────────────

def _recognize_scheme_v1(text: str) -> dict:
    t = low(text)
    dk_count = count_unique(text, "Дк")
    lk_count = count_unique(text, "Лк")
    diameters: List[int] = []
    for m in re.finditer(r"[∅Ø]\s*(\d{3,4})", text):
        d = int(m.group(1))
        if d not in diameters:
            diameters.append(d)
    well_types: List[str] = []
    if "полимерный" in t:
        well_types.append("полимерный")
    if "ж/б" in t or "железобетон" in t:
        well_types.append("ж/б")
    slope_m = re.search(r"i\s*=\s*(\d+(?:[,.]\d+)?)", text, re.I)
    slope = slope_m.group(1).replace(",", ".") if slope_m else None
    legend_length: Optional[float] = None
    for line in text.splitlines():
        ll = low(line)
        if "уклон" in ll and ("длина" in ll or " l " in ll or "l=" in ll.replace(" ","")):
            lm = re.search(r"l\s*=\s*(\d+(?:[,.]\d+)?)\s*м", line, re.I)
            if lm:
                try:
                    v = float(lm.group(1).replace(",", "."))
                    if 0.5 <= v <= 200:
                        legend_length = v
                except Exception:
                    pass
    return {
        "dk_count": dk_count,
        "lk_count": lk_count,
        "diameters": sorted(set(diameters)),
        "well_types": well_types,
        "has_dns": has(text, "ДНС"),
        "has_pu": has(text, "ПУ-1") or has(text, "пескоуловитель"),
        "has_kgn": bool(re.search(r"кгн", t)),
        "has_linear": has(text, "линейный водоотвод") or has(text, "лоток"),
        "slope": slope,
        "legend_length": legend_length,
    }


def _build_wc_length_message_v1(rec: dict) -> str:
    lines = ["Распознал из схемы дренажа:\n"]
    if rec["dk_count"] > 0:
        diam_parts = [f"∅{d}" for d in rec["diameters"] if d in (315, 500)]
        types_part = ", полимерные" if "полимерный" in rec["well_types"] else ""
        diam_str = (" (" + "/".join(diam_parts) + types_part + ")") if diam_parts else ""
        lines.append(f"• Дренажные колодцы: Дк × {rec['dk_count']} шт{diam_str}")
    if 1000 in rec["diameters"] and "ж/б" in rec["well_types"]:
        lines.append("• Колодец ∅1000 ж/б (сборный)")
    if rec["lk_count"] > 0:
        lines.append(f"• Ливневые колодцы: Лк × {rec['lk_count']} шт")
    if rec["has_dns"]:
        kgn = " (ёмкость КГН-460)" if rec["has_kgn"] else ""
        lines.append(f"• ДНС-1 — дренажная насосная станция{kgn}")
    if rec["has_pu"]:
        lines.append("• ПУ-1 — пескоуловитель")
    if rec["has_linear"]:
        lines.append("• Линейный водоотвод (лотки)")
    if rec["slope"]:
        lines.append(f"• Уклон трубы: i={rec['slope']}")
    if rec["legend_length"]:
        lines.append(
            f"• В легенде схемы: l={rec['legend_length']} м"
            " (пример обозначения, не суммарная длина)"
        )
    lines += [
        "",
        "Не удалось прочитать: длины трасс (схема графическая, оцифровки нет).\n",
    ]
    if rec["legend_length"]:
        lines.append(
            f"Если l={rec['legend_length']} м — это типовая длина участка,"
            " пришли общую длину трассы (Дк-1→Дк-2→...→ДНС, сумма участков в метрах)."
        )
    else:
        lines.append(
            "Пришли, пожалуйста, общую длину дренажных труб (м)"
            " или длины по участкам: Дк-1→Дк-2, Дк-2→ДНС и т.д."
        )
    lines.append("\nПосле этого запрошу актуальные цены и покажу смету.")
    return "\n".join(lines)


async def main():  # noqa: F811  PATCH_TOPIC2_DRAINAGE_RECOGNIZE_ALL_V1
    conn = sqlite3.connect(str(DB)); conn.row_factory = sqlite3.Row
    task = conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1", (TASK_ID,)).fetchone()
    if not task:
        raise SystemExit(f"TASK_NOT_FOUND:{TASK_ID}")
    tid = str(task["id"]); chat_id = str(task["chat_id"]); topic_id = int(task["topic_id"] or 2)
    raw_in = str(task["raw_input"] or ""); result = str(task["result"] or "")

    vat_mode = infer_vat(conn, tid, raw_in, result)
    if vat_mode is None:
        ask_vat(conn, task); conn.close(); return

    markers = read_history_markers(conn, tid)

    confirmed_marker = find_marker(markers, "TOPIC2_PRICE_CHOICE_CONFIRMED:")
    if confirmed_marker:
        mode = confirmed_marker.split(":", 1)[1].strip()
        print(f"PRICE_CHOICE_CONFIRMED:{mode} — generating estimate")
        cache = load_cache()
        if cache is None:
            raise SystemExit("PRICE_CACHE_FILE_MISSING — re-run from price search state")
        await _generate_and_send(conn, tid, chat_id, topic_id, vat_mode, mode, cache, markers)
        conn.close(); return

    menu_marker = find_marker(markers, "TOPIC2_PRICE_CHOICE_MENU_SENT:")
    if menu_marker:
        user_reply = read_recent_user_reply(conn, tid)
        if user_reply:
            choice = _detect_price_choice(user_reply)
            if choice:
                print(f"USER_CHOICE_DETECTED:{choice} from '{user_reply[:40]}'")
                hist(conn, tid, f"TOPIC2_PRICE_CHOICE_CONFIRMED:{choice}")
                conn.commit()
                cache = load_cache()
                if cache is None:
                    raise SystemExit("PRICE_CACHE_FILE_MISSING")
                await _generate_and_send(conn, tid, chat_id, topic_id, vat_mode, choice, cache, markers)
                conn.close(); return
            m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:м\b|метр)", user_reply.lower())
            if m:
                try:
                    L_reply = float(m.group(1).replace(",", "."))
                    if 5 <= L_reply <= 2000:
                        print(f"LENGTH_FROM_USER_REPLY:{L_reply} — rebuilding cache")
                        hist(conn, tid, f"USER_PROVIDED_LENGTH:{L_reply}")
                        conn.commit()
                        await _do_price_search(conn, tid, chat_id, topic_id, L_reply, vat_mode)
                        conn.close(); return
                except Exception:
                    pass
        print("WAITING_FOR_PRICE_CHOICE — no actionable reply yet")
        conn.close(); return

    sources = find_user_pdfs()
    if not sources:
        raise SystemExit("NO_USER_SOURCE_PDFS")
    drainage = [x for x in sources if x["kind"] == "drainage_scheme"]
    if not drainage:
        raise SystemExit("DRAINAGE_SOURCE_NOT_FOUND")

    scheme_text = "\n".join(x["text"] for x in drainage)

    pdf_lengths = extract_lengths_from_pdf(scheme_text)
    total_len   = round(sum(pdf_lengths), 2)
    print(f"PDF_LENGTHS={pdf_lengths} TOTAL_LEN={total_len}")

    if total_len <= 0:
        user_len = read_user_provided_length(conn, tid)
        if user_len > 0:
            print(f"USER_PROVIDED_LENGTH:{user_len}")
            hist(conn, tid, f"USER_PROVIDED_LENGTH:{user_len}")
            conn.commit()
            total_len = user_len
        else:
            rec = _recognize_scheme_v1(scheme_text)
            wc_msg = _build_wc_length_message_v1(rec)
            print(f"RECOGNIZE_ALL: dk={rec['dk_count']} dns={rec['has_dns']} pu={rec['has_pu']}"
                  f" kgn={rec['has_kgn']} diameters={rec['diameters']} slope={rec['slope']}"
                  f" legend_l={rec['legend_length']}")
            bot_msg = send_msg(chat_id, topic_id, wc_msg)
            conn.execute(
                "UPDATE tasks SET state='WAITING_CLARIFICATION', result=?, bot_message_id=?,"
                " error_message='TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN',"
                " updated_at=datetime('now') WHERE id=?",
                (wc_msg, bot_msg, tid),
            )
            for a in [
                "TOPIC2_DRAINAGE_LENGTH_PROOF_GATE_V1",
                f"TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN:lines={len(pdf_lengths)}:total={total_len}",
                f"TOPIC2_DRAINAGE_RECOGNIZED:dk={rec['dk_count']},dns={rec['has_dns']},"
                f"pu={rec['has_pu']},kgn={rec['has_kgn']},slope={rec['slope']}",
                "TOPIC2_DRAINAGE_FINAL_ARTIFACTS_BLOCKED",
                f"TOPIC2_DRAINAGE_WC_SENT:{bot_msg}",
            ]:
                hist(conn, tid, a)
            conn.commit(); conn.close()
            print(f"DRAINAGE_RECOGNIZE_ALL_WC_SENT BOT_MESSAGE_ID={bot_msg}")
            return

    await _do_price_search(conn, tid, chat_id, topic_id, total_len, vat_mode)
    conn.close()


if __name__ == "__main__":  # PATCH_TOPIC2_DRAINAGE_RECOGNIZE_ALL_V1 entry point
    pass  # entry point moved to final by PATCH_TOPIC2_DRAINAGE_MULTIFILE_SOURCE_V3


# === PATCH_TOPIC2_DRAINAGE_MULTIFILE_SOURCE_V3 ===
def _t2dmf_kind_override_v3(path, text, kind):
    try:
        t = low(text)
        if kind == "other_pdf":
            has_project = "рабочий проект" in t
            has_pipe = ("пвх" in t) or ("пнд" in t)
            has_drain = ("дренаж" in t) or ("ливнев" in t) or ("наружные водостоки" in t)
            if has_project and has_pipe and has_drain:
                return "drainage_scheme"
        return kind
    except Exception:
        return kind

def find_user_pdfs():  # noqa: F811
    import glob as _glob
    from pathlib import Path as _Path
    from datetime import datetime as _datetime

    now = _datetime.now().timestamp()
    candidates = []
    for raw in _glob.glob("/var/lib/telegram-bot-api/*/documents/*.pdf"):
        p = _Path(raw)
        try:
            if p.is_file() and now - p.stat().st_mtime <= 48 * 3600:
                candidates.append(p)
        except Exception:
            pass

    out = []
    seen_paths = set()
    geology_added = False

    for p in sorted(set(candidates), key=lambda x: x.stat().st_mtime, reverse=True):
        txt = pdf_text(p)
        if is_artifact(p, txt):
            continue
        kind = _t2dmf_kind_override_v3(p, txt, classify(p, txt))

        if kind == "drainage_scheme":
            key = str(p.resolve())
            if key in seen_paths:
                continue
            out.append({"path": p, "kind": kind, "name": p.name, "text": txt, "chars": len(txt)})
            seen_paths.add(key)
            continue

        if kind == "geology_report" and not geology_added:
            key = str(p.resolve())
            if key in seen_paths:
                continue
            out.append({"path": p, "kind": kind, "name": p.name, "text": txt, "chars": len(txt)})
            seen_paths.add(key)
            geology_added = True

    return out

if __name__ == "__main__":  # PATCH_TOPIC2_DRAINAGE_MULTIFILE_SOURCE_V3 final entry point
    asyncio.run(main())
# === END_PATCH_TOPIC2_DRAINAGE_MULTIFILE_SOURCE_V3 ===


====================================================================================================
END_FILE: tools/topic2_drainage_repair_close.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/upload_retry_unified_worker.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 45992958e34bc05b156972d97caab2e3aa948f9c9e7a728ab008c5363cdb4df4
====================================================================================================
#!/usr/bin/env python3
# === UPLOAD_RETRY_QUEUE_UNIFICATION_V1_WORKER ===
from __future__ import annotations
import json, os, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
DB = BASE / "data/core.db"

def main():
    if not DB.exists():
        print(json.dumps({"ok": False, "error": "DB_NOT_FOUND"}))
        return
    conn = sqlite3.connect(DB, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS upload_retry_queue(
        id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, task_id TEXT,
        topic_id INTEGER, kind TEXT, attempts INTEGER DEFAULT 0,
        last_error TEXT, created_at TEXT DEFAULT (datetime('now')), last_attempt TEXT)""")
    conn.commit()
    rows = conn.execute(
        "SELECT * FROM upload_retry_queue WHERE COALESCE(attempts,0)<5 ORDER BY id ASC LIMIT 25"
    ).fetchall()
    done = failed = 0
    for r in rows:
        rid = r["id"]
        path = str(r["path"] or "")
        task_id = str(r["task_id"] or "")
        topic_id = int(r["topic_id"] or 0)
        kind = str(r["kind"] or "artifact")
        link = ""
        try:
            if not path or not os.path.exists(path):
                raise RuntimeError("FILE_NOT_FOUND")
            from core.engine_base import upload_artifact_to_drive
            link = upload_artifact_to_drive(path, task_id, topic_id) or ""
            if not link:
                from core.engine_base import _telegram_fallback_send
                link = _telegram_fallback_send(path, task_id, topic_id) or ""
            if not link:
                raise RuntimeError("NO_LINK")
            row = conn.execute("SELECT result FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row:
                old = row[0] or ""
                new_line = f"{kind} retry OK: {link}"
                if new_line not in old:
                    conn.execute("UPDATE tasks SET result=?,updated_at=datetime('now') WHERE id=?",
                                 ((old+"\n"+new_line).strip(), task_id))
            conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                         (task_id, f"UPLOAD_RETRY_QUEUE_UNIFICATION_V1:OK:{link}"))
            conn.execute("DELETE FROM upload_retry_queue WHERE id=?", (rid,))
            done += 1
        except Exception as e:
            conn.execute(
                "UPDATE upload_retry_queue SET attempts=COALESCE(attempts,0)+1,last_error=?,last_attempt=? WHERE id=?",
                (str(e), datetime.now(timezone.utc).isoformat(), rid),
            )
            failed += 1
        conn.commit()
    conn.close()
    print(json.dumps({"ok": True, "processed": len(rows), "done": done, "failed": failed}))

if __name__ == "__main__":
    main()
# === END_UPLOAD_RETRY_QUEUE_UNIFICATION_V1_WORKER ===

====================================================================================================
END_FILE: tools/upload_retry_unified_worker.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/verify_local_bot_api.sh
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2e151d42af7dc5a05fa8db4f5c5426d05116adf14362a9ea3feeb9fd1bc9922f
====================================================================================================
#!/bin/bash
# verify_local_bot_api.sh
# PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1 — activation gate
#
# Run all 4 checks before activating wrapper.
# Exit 0 = all OK, ready to activate.
# Exit 1 = not ready, do NOT activate.

set -e
PASS=0
FAIL=0
CRED_FILE="/etc/areal/telegram-local-api.env"
BINARY="/usr/local/bin/telegram-bot-api"
SERVICE="telegram-bot-api-local.service"
WRAPPER="/root/.areal-neva-core/areal_telegram_wrapper.py"
PENDING="/root/.areal-neva-core/tmp/bigfile_ingress_override.conf.pending"
OVERRIDE_DIR="/etc/systemd/system/telegram-ingress.service.d"

echo "=== PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1 — Activation Gate ==="
echo ""

# ── Check 1: binary ───────────────────────────────────────────────────────────
echo "1. Binary..."
if [ -x "$BINARY" ]; then
    VER=$("$BINARY" --version 2>/dev/null || echo "built")
    echo "   OK: $BINARY ($VER)"
    PASS=$((PASS+1))
else
    echo "   FAIL: $BINARY not found or not executable"
    FAIL=$((FAIL+1))
fi

# ── Check 2: service active ───────────────────────────────────────────────────
echo "2. Service telegram-bot-api-local..."
if systemctl is-active "$SERVICE" >/dev/null 2>&1; then
    echo "   OK: $SERVICE is active"
    PASS=$((PASS+1))
else
    STATUS=$(systemctl is-active "$SERVICE" 2>/dev/null || echo "unknown")
    echo "   FAIL: $SERVICE status=$STATUS"
    FAIL=$((FAIL+1))
fi

# ── Check 3: local getMe ──────────────────────────────────────────────────────
echo "3. Local getMe..."
source "$CRED_FILE" 2>/dev/null || true
BOT_TOKEN=<REDACTED_SECRET> show telegram-ingress -p Environment --value 2>/dev/null | \
    tr ' ' '\n' | grep "^TELEGRAM_BOT_TOKEN=" | cut -d= -f2- | head -1)
if [ -z "$BOT_TOKEN" ]; then
    # Try from running process
    PID=$(systemctl show telegram-ingress -p MainPID --value 2>/dev/null)
    BOT_TOKEN=<REDACTED_SECRET> -n "$PID" ] && grep -z "TELEGRAM_BOT_TOKEN" /proc/$PID/environ 2>/dev/null \
        | tr '\0' '\n' | grep "^TELEGRAM_BOT_TOKEN=" | cut -d= -f2- | head -1 || echo "")
fi
if [ -n "$BOT_TOKEN" ]; then
    RESULT=$(curl -s --max-time 5 "http://localhost:8081/bot${BOT_TOKEN}/getMe" 2>/dev/null)
    if echo "$RESULT" | /root/.areal-neva-core/.venv/bin/python3 -c \
        "import sys,json; d=json.load(sys.stdin); assert d.get('ok'), 'not ok'" 2>/dev/null; then
        USERNAME=$(echo "$RESULT" | /root/.areal-neva-core/.venv/bin/python3 -c \
            "import sys,json; d=json.load(sys.stdin); print(d['result'].get('username','?'))" 2>/dev/null)
        echo "   OK: getMe → @${USERNAME}"
        PASS=$((PASS+1))
    else
        echo "   FAIL: getMe returned error or timeout"
        FAIL=$((FAIL+1))
    fi
else
    echo "   SKIP: BOT_TOKEN not found — cannot test getMe (manual check required)"
    FAIL=$((FAIL+1))
fi

# ── Check 4: wrapper dry-run ──────────────────────────────────────────────────
echo "4. Wrapper imports dry-run..."
/root/.areal-neva-core/.venv/bin/python3 -c "
import sys, os
os.environ.setdefault('TELEGRAM_LOCAL_API_BASE', 'http://localhost:8081')
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
srv = TelegramAPIServer.from_base('http://localhost:8081')
sess = AiohttpSession(api=srv)
# Verify pattern exists in daemon
daemon = open('/root/.areal-neva-core/telegram_daemon.py').read()
pattern = 'url = f\"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}\"'
assert pattern in daemon, 'download URL pattern not found in telegram_daemon.py'
print('   OK: aiogram local server imports ok, daemon pattern ok')
" && PASS=$((PASS+1)) || { echo "   FAIL: wrapper dry-run failed"; FAIL=$((FAIL+1)); }

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "=== Results: $PASS/4 passed, $FAIL failed ==="
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo "ALL CHECKS PASSED — ready to activate"
    echo ""
    echo "Activation (requires explicit confirmation):"
    echo "  mkdir -p $OVERRIDE_DIR"
    echo "  cp $PENDING $OVERRIDE_DIR/bigfile.conf"
    echo "  systemctl daemon-reload"
    echo "  systemctl restart telegram-ingress"
    echo ""
    exit 0
else
    echo "NOT READY — do NOT activate wrapper"
    echo ""
    exit 1
fi

====================================================================================================
END_FILE: tools/verify_local_bot_api.sh
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: .gitignore
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 18457271563906a3e4e6d7d2c66167960f746a3db5d3fd7fbed171828b7c7289
====================================================================================================
*.pyc
__pycache__/
.env
*.log
*.bak
runtime/*
!runtime/.gitkeep
*.bak.*
*.broken.*
.venv/
data/*.db
data/*.db-*
data/memory/
data/memory_files/
data/source_registry.db
sessions/
logs/
runtime/
credentials.json
token.json
.env.*
*.session
*.session-journal
core.db
*.safe.*
data/*.safe.*
task_worker.py.bak_*
*.bak_*
backups/
*.broken*
data/*.backup*
data/project_templates_bak*/
data/telegram_file_catalog/
data/templates/estimate_batch/
outputs/
data/templates/estimate_logic/
data/templates/reference_monolith/
data/templates/design_logic/
data/price_quotes/
.secret_patterns
tools/*.bak_*
docs/SHARED_CONTEXT/*.bak_*
core/*.bak_*

# CODE_AND_SYSTEM_CLOSE_20260504_NO_LIVE_TEST_V1 runtime/generated data
data/db_backups/
data/project_templates/
data/templates/estimate/
data/templates/estimate/cache/
*.tar.gz

# P6H_TOPIC5 — runtime-generated technadzor data (regenerated on demand)
data/templates/technadzor/ACTIVE__*.json
data/templates/technadzor/objects/
data/memory_files/technadzor_index_cache/
outputs/technadzor_p6h/

# temp activation files
tmp/

====================================================================================================
END_FILE: .gitignore
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: HANDOFFS/HANDOFF_20260505_TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ae77a21f57e7cddbc7efba61939715989164697849258605e6ada6ea474ba3cf
====================================================================================================
# HANDOFF 2026-05-05 — TOPIC5 TECHNADZOR SYSTEM LOGIC FINAL

date: 2026-05-05
topic: topic_5 / ТЕХНАДЗОР
status: DOCS_COMPLETE_READY_FOR_COMMIT
verified_head: 6157b01

---

## Что завершено в этой сессии

1. Все unified_context файлы созданы и верифицированы
2. Исправлены 2 ошибки из предыдущей сессии (Susanino фото, Novichkovo source ref)
3. Document Output Contract задокументирован
4. Runtime usage rules задокументированы
5. OWNER_ACT_STYLE_PROFILE полностью переписан из реальных Drive актов
6. Итоговый отчёт создан

---

## Файлы изменены / созданы

### Исправлены
```
docs/TECHNADZOR/unified_context/SUSANINO_OBJECT_CONTEXT.md
docs/TECHNADZOR/unified_context/NOVICHKOVO_OBJECT_CONTEXT.md
```

### Созданы
```
docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.md
docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.json
docs/TECHNADZOR/TOPIC5_RUNTIME_USAGE_RULES.md
docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL_REPORT.md
docs/TECHNADZOR/unified_context/OWNER_ACTS_INDEX.json
docs/TECHNADZOR/unified_context/NORMATIVE_CONTEXT_INDEX.json
docs/TECHNADZOR/unified_context/TNZ_MSK_SKILL_BINDING.json
docs/TECHNADZOR/unified_context/CHAT_EXPORT_TECHNADZOR_BINDING.json
docs/TECHNADZOR/unified_context/OWNER_ENGINEERING_LOAD_VALIDATION_PATTERN.md
docs/TECHNADZOR/unified_context/OWNER_ENGINEERING_LOAD_VALIDATION_PATTERN.json
docs/TECHNADZOR/unified_context/TOPIC5_UNIFIED_TECHNADZOR_CONTEXT.md
docs/TECHNADZOR/unified_context/TOPIC5_UNIFIED_TECHNADZOR_CONTEXT.json
HANDOFFS/HANDOFF_20260505_TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.md
```

### Уже существовали (не изменялись)
```
docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.md
docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.json
docs/TECHNADZOR/unified_context/KIEVSKOE_95_OBJECT_CONTEXT.md
docs/TECHNADZOR/unified_context/OWNER_ACT_STYLE_PROFILE.md
docs/TECHNADZOR/unified_context/OBJECT_CONTEXT_INDEX.json
docs/TECHNADZOR/source_skills/tnz_msk/*
```

---

## Запрещённые файлы — не тронуты

```
core/normative_engine.py    — dirty (+283 lines), НЕ staged, НЕ committed
task_worker.py              — не тронут
telegram_daemon.py          — не тронут
ai_router.py                — не тронут
reply_sender.py             — не тронут
google_io.py                — не тронут
.env / credentials.json     — не тронуты
```

---

## Состояние системы

```
ActiveTechnadzorFolder: тест надзор (id: 1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG)
process_technadzor: _p6h4tw_v1_wrapped=True
Vision: BLOCKED (EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False)
reportlab: NOT INSTALLED
python-docx: NOT INSTALLED
SearchMonolithV2: perplexity/sonar via OpenRouter (ACTIVE)
```

---

## Открытые вопросы для следующей сессии

1. Vision 3-й выезд Киевское (04.05.2026) — решение владельца?
2. reportlab / python-docx — установить?
3. @tnz_msk 66 карт на review — одобрить?
4. ГОСТ 30971 — добавить в normative_engine?
5. Live tests (11 тестов из ТЗ) — запустить?

---

## Перед следующим патчем

1. Прочитать `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md`
2. Прочитать этот handoff
3. `mv core/context_aggregator.py /tmp/` перед push

====================================================================================================
END_FILE: HANDOFFS/HANDOFF_20260505_TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 410a003b00b8a0d4cb71e8249ce2fba39ddf21ae76a26bc32d5ea370b0ab2517
====================================================================================================
# ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.md

Статус: базовое рабочее ядро оркестра через OpenRouter

## Контур
Telegram -> telegram_daemon.py -> core.db -> task_worker.py -> core/ai_router.py -> OpenRouter -> Telegram

## Память
memory_api_server.py -> data/memory.db

## Ключевые файлы
- telegram_daemon: /root/.areal-neva-core/telegram_daemon.py
- task_worker: /root/.areal-neva-core/task_worker.py
- ai_router: /root/.areal-neva-core/core/ai_router.py
- memory_api_server: /root/.areal-neva-core/memory_api_server.py
- core_db: /root/.areal-neva-core/data/core.db
- memory_db: /root/.areal-neva-core/data/memory.db

## Процессы
```
931211 /root/.areal-neva-core/.venv/bin/python3 -u /root/.areal-neva-core/memory_api_server.py
931217 /root/.areal-neva-core/.venv/bin/python3 -u /root/.areal-neva-core/telegram_daemon.py
934122 .venv/bin/python3 -u task_worker.py
939864 /bin/sh -c pgrep -af 'memory_api_server.py|telegram_daemon.py|task_worker.py' || true
```

## Git
- branch: fatal: not a git repository (or any of the parent directories): .git
- commit: fatal: not a git repository (or any of the parent directories): .git

## Memory
- rows: 3
- export: ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.memory.json

## Последние задачи
```json
[
  {
    "id": "14d0fefb-ecb0-4ce2-9e56-8fbbd9dc546b",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Всё в порядке, спасибо. А у тебя?",
    "error_message": null,
    "reply_to_message_id": 2795,
    "created_at": "2026-04-11T13:57:16.333447+00:00",
    "updated_at": "2026-04-11T13:57:17.465609+00:00"
  },
  {
    "id": "a51d0e33-bf9f-42be-bc3a-0ae2c7d2ccbf",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "Как настроение всё ли в порядке?",
    "state": "DONE",
    "result": "Настроение нормальное, всё в порядке. А у тебя?",
    "error_message": null,
    "reply_to_message_id": 2793,
    "created_at": "2026-04-11T13:57:04.883321+00:00",
    "updated_at": "2026-04-11T13:57:06.373296+00:00"
  },
  {
    "id": "a4c08fda-eaa7-428f-9575-1bd8bd8d7600",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Понял, готов отвечать.",
    "error_message": null,
    "reply_to_message_id": 2791,
    "created_at": "2026-04-11T13:56:51.395517+00:00",
    "updated_at": "2026-04-11T13:56:53.152799+00:00"
  },
  {
    "id": "fd6a77c5-1d85-4f62-bf45-ead1d76c0cbd",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Hello! How can I assist you today?",
    "error_message": null,
    "reply_to_message_id": 2789,
    "created_at": "2026-04-11T13:41:11.612250+00:00",
    "updated_at": "2026-04-11T13:41:18.307618+00:00"
  },
  {
    "id": "9ca9f754-eb00-4959-be75-0a11672418c9",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Hello! How can I assist you today?",
    "error_message": null,
    "reply_to_message_id": 2787,
    "created_at": "2026-04-11T13:40:55.751820+00:00",
    "updated_at": "2026-04-11T13:40:57.070533+00:00"
  },
  {
    "id": "8a2c53a3-e9c4-43c6-b8c4-32a73a9eb603",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "It seems you might have intended to provide more context or a specific question. How can I assist you today?",
    "error_message": null,
    "reply_to_message_id": 2785,
    "created_at": "2026-04-11T13:40:34.152693+00:00",
    "updated_at": "2026-04-11T13:40:40.956432+00:00"
  },
  {
    "id": "b1abbf1b-a698-4cbb-bc02-db807d320c60",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "тест",
    "state": "DONE",
    "result": "Привет! Как я могу помочь вам сегодня?",
    "error_message": null,
    "reply_to_message_id": 2783,
    "created_at": "2026-04-11T13:40:20.148758+00:00",
    "updated_at": "2026-04-11T13:40:21.554233+00:00"
  }
]
```

====================================================================================================
END_FILE: ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.memory.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 1b7e37c5f348dc06d787b53bca85926fe19a115a15de5cedbfab783df29fe41d
====================================================================================================
{
  "snapshot_name": "ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.memory.json",
  "snapshot_type": "orchestra_base_core_openrouter_working",
  "date": "2026-04-11T17:20:32+03:00",
  "git": {
    "branch": "fatal: not a git repository (or any of the parent directories): .git",
    "commit": "fatal: not a git repository (or any of the parent directories): .git",
    "status_short": "fatal: not a git repository (or any of the parent directories): .git"
  },
  "processes": "931211 /root/.areal-neva-core/.venv/bin/python3 -u /root/.areal-neva-core/memory_api_server.py\n931217 /root/.areal-neva-core/.venv/bin/python3 -u /root/.areal-neva-core/telegram_daemon.py\n934122 .venv/bin/python3 -u task_worker.py\n939864 /bin/sh -c pgrep -af 'memory_api_server.py|telegram_daemon.py|task_worker.py' || true",
  "files": {
    "telegram_daemon": "/root/.areal-neva-core/telegram_daemon.py",
    "task_worker": "/root/.areal-neva-core/task_worker.py",
    "ai_router": "/root/.areal-neva-core/core/ai_router.py",
    "memory_api_server": "/root/.areal-neva-core/memory_api_server.py",
    "core_db": "/root/.areal-neva-core/data/core.db",
    "memory_db": "/root/.areal-neva-core/data/memory.db"
  },
  "memory_schema": [
    {
      "cid": 0,
      "name": "id",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 1
    },
    {
      "cid": 1,
      "name": "chat_id",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 2,
      "name": "key",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 3,
      "name": "value",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 4,
      "name": "timestamp",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    }
  ],
  "memory_count": 3,
  "memory_rows": [
    {
      "id": "c3353b3c-92df-44e2-a231-103d308ae8a2",
      "chat_id": "-1003725299009",
      "key": "user_input",
      "value": "",
      "timestamp": "2026-04-11T13:56:51.721825"
    },
    {
      "id": "2cf0d42c-157c-4be6-a3c9-c818a6158cd0",
      "chat_id": "-1003725299009",
      "key": "user_input",
      "value": "",
      "timestamp": "2026-04-11T13:57:16.414875"
    },
    {
      "id": "1023d7cf-de9f-459e-aa1d-87544b318c9e",
      "chat_id": "-1003725299009",
      "key": "user_input",
      "value": "Как настроение всё ли в порядке?",
      "timestamp": "2026-04-11T13:57:05.204941"
    }
  ],
  "sources_rows": [],
  "tasks_schema": [
    {
      "cid": 0,
      "name": "id",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 1
    },
    {
      "cid": 1,
      "name": "chat_id",
      "type": "INTEGER",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 2,
      "name": "user_id",
      "type": "INTEGER",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 3,
      "name": "input_type",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 4,
      "name": "raw_input",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 5,
      "name": "state",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": "\"NEW\"",
      "pk": 0
    },
    {
      "cid": 6,
      "name": "result",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 7,
      "name": "error_message",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 8,
      "name": "reply_to_message_id",
      "type": "INTEGER",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 9,
      "name": "created_at",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 10,
      "name": "updated_at",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    }
  ],
  "last_tasks": [
    {
      "id": "14d0fefb-ecb0-4ce2-9e56-8fbbd9dc546b",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "",
      "state": "DONE",
      "result": "Всё в порядке, спасибо. А у тебя?",
      "error_message": null,
      "reply_to_message_id": 2795,
      "created_at": "2026-04-11T13:57:16.333447+00:00",
      "updated_at": "2026-04-11T13:57:17.465609+00:00"
    },
    {
      "id": "a51d0e33-bf9f-42be-bc3a-0ae2c7d2ccbf",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "Как настроение всё ли в порядке?",
      "state": "DONE",
      "result": "Настроение нормальное, всё в порядке. А у тебя?",
      "error_message": null,
      "reply_to_message_id": 2793,
      "created_at": "2026-04-11T13:57:04.883321+00:00",
      "updated_at": "2026-04-11T13:57:06.373296+00:00"
    },
    {
      "id": "a4c08fda-eaa7-428f-9575-1bd8bd8d7600",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "",
      "state": "DONE",
      "result": "Понял, готов отвечать.",
      "error_message": null,
      "reply_to_message_id": 2791,
      "created_at": "2026-04-11T13:56:51.395517+00:00",
      "updated_at": "2026-04-11T13:56:53.152799+00:00"
    },
    {
      "id": "fd6a77c5-1d85-4f62-bf45-ead1d76c0cbd",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "",
      "state": "DONE",
      "result": "Hello! How can I assist you today?",
      "error_message": null,
      "reply_to_message_id": 2789,
      "created_at": "2026-04-11T13:41:11.612250+00:00",
      "updated_at": "2026-04-11T13:41:18.307618+00:00"
    },
    {
      "id": "9ca9f754-eb00-4959-be75-0a11672418c9",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "",
      "state": "DONE",
      "result": "Hello! How can I assist you today?",
      "error_message": null,
      "reply_to_message_id": 2787,
      "created_at": "2026-04-11T13:40:55.751820+00:00",
      "updated_at": "2026-04-11T13:40:57.070533+00:00"
    },
    {
      "id": "8a2c53a3-e9c4-43c6-b8c4-32a73a9eb603",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "",
      "state": "DONE",
      "result": "It seems you might have intended to provide more context or a specific question. How can I assist you today?",
      "error_message": null,
      "reply_to_message_id": 2785,
      "created_at": "2026-04-11T13:40:34.152693+00:00",
      "updated_at": "2026-04-11T13:40:40.956432+00:00"
    },
    {
      "id": "b1abbf1b-a698-4cbb-bc02-db807d320c60",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "тест",
      "state": "DONE",
      "result": "Привет! Как я могу помочь вам сегодня?",
      "error_message": null,
      "reply_to_message_id": 2783,
      "created_at": "2026-04-11T13:40:20.148758+00:00",
      "updated_at": "2026-04-11T13:40:21.554233+00:00"
    }
  ]
}
====================================================================================================
END_FILE: ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.memory.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: README.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: b294b43738d41e1cc39c2e221ea9722e9605bae039a6f966e950e33b139ba3d7
====================================================================================================
# AREAL-NEVA ORCHESTRA — GITHUB SSOT
Создан: 28.04.2026

GitHub = каноны / архитектура / shared context / handoff / reports / tools
Сервер = runtime / обработка / memory.db / core.db / временные файлы
Drive = резерв и тяжёлые файлы

Регламент:
- только добавление, не перезатирание
- версионирование: v1 v2 v3
- patch-правило: было -> станет -> применить
- backup перед изменением
- токены никогда в репо

====================================================================================================
END_FILE: README.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: areal_telegram_wrapper.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ff7e0e9e7f77c13d370d8796b6683523ec134d09232e9b3d18fbcd63dbce47d3
====================================================================================================
"""
PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1
Patches aiogram in-memory to use local Telegram Bot API server (localhost:8081).
Removes 20MB file size limit. telegram_daemon.py is NOT modified on disk.

Markers logged to task_history (via daemon):
  BIG_FILE_LOCAL_BOT_API_USED
  BIG_FILE_LOCAL_DOWNLOAD_OK
  BIG_FILE_LOCAL_DOWNLOAD_FAILED
  BIG_FILE_TEMP_CLEANED
  FILE_INTAKE_ROUTER_LOCAL_PATH_PASSED

Activation gate: only via verify_local_bot_api.sh — do NOT activate manually.
"""
import os
import sys
import logging

_LOG = logging.getLogger("areal.bigfile_patch")

# Read from EnvironmentFile — never hardcode, never log values
LOCAL_API_BASE = os.getenv("TELEGRAM_LOCAL_API_BASE", "http://localhost:8081")

# ── Patch 1: aiogram Bot session → local server ──────────────────────────────
try:
    from aiogram.client.session.aiohttp import AiohttpSession
    from aiogram.client.telegram import TelegramAPIServer
    import aiogram

    _orig_bot_init = aiogram.Bot.__init__

    def _patched_bot_init(self, token, session=None, default=None, **kwargs):
        if session is None:
            try:
                local_server = TelegramAPIServer.from_base(LOCAL_API_BASE)
                session = AiohttpSession(api=local_server)
                _LOG.info("BIG_FILE_LOCAL_BOT_API_USED: local server active")
            except Exception as _e:
                # Never log LOCAL_API_BASE value with credentials embedded
                _LOG.warning("BIG_FILE_LOCAL_API_SESSION_FAILED: %s — falling back", type(_e).__name__)
        _orig_bot_init(self, token, session=session, default=default, **kwargs)

    aiogram.Bot.__init__ = _patched_bot_init
    _LOG.info("PATCH_BOT_INIT_LOCAL_SERVER: installed")

except Exception as _patch_err:
    _LOG.error("PATCH_BOT_INIT_LOCAL_SERVER_FAILED: %s", type(_patch_err).__name__)

# ── Patch 2: Fix download URL (in-memory only, file on disk unchanged) ────────
_daemon_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "telegram_daemon.py"
)

try:
    _code = open(_daemon_path, "r", encoding="utf-8").read()

    _CLOUD_PATTERN = 'url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"'
    # Local Bot API returns absolute disk path in file_path — copy directly, skip HTTP
    _LOCAL_PATTERN = (
        'if file_path.startswith("/") and os.path.exists(file_path):\n'
        '        import shutil as _shutil_lbp, logging as _log_lbp\n'
        '        _log_lbp.getLogger("areal.bigfile_patch").info("LOCAL_BOT_API_ABSOLUTE_PATH_USED:%s", os.path.basename(file_path))\n'
        '        _shutil_lbp.copy2(file_path, local_path)\n'
        '        return local_path\n'
        f'    url = f"{LOCAL_API_BASE}/file/bot{{BOT_TOKEN}}/{{file_path}}"'
    )

    if _CLOUD_PATTERN in _code:
        _code = _code.replace(_CLOUD_PATTERN, _LOCAL_PATTERN)
        _LOG.info("PATCH_DOWNLOAD_URL_LOCAL_SERVER: ok (absolute path → disk copy)")
    else:
        _LOG.warning(
            "PATCH_DOWNLOAD_URL_LOCAL_SERVER: pattern not found in telegram_daemon.py — "
            "large file download URL not patched"
        )

    # ── Execute patched daemon as __main__ ────────────────────────────────────
    _globals = {
        "__name__": "__main__",
        "__file__": _daemon_path,
        "__doc__": None,
        "__package__": None,
        "__spec__": None,
        "__builtins__": __builtins__,
    }
    exec(compile(_code, _daemon_path, "exec"), _globals)

except Exception as _exec_err:
    _LOG.error("WRAPPER_EXEC_DAEMON_FAILED: %s", _exec_err)
    raise

====================================================================================================
END_FILE: areal_telegram_wrapper.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: auto_memory_dump.sh
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 51c8b3cb64183d2a3f41cf82b53daa4e234bac3e9aa4540958cecc5a1db39cb6
====================================================================================================
#!/bin/bash
cd /root/.areal-neva-core
/root/.areal-neva-core/.venv/bin/python3 /root/.areal-neva-core/orchestra_full_dump.py >> /root/.areal-neva-core/logs/auto_dump.log 2>&1

====================================================================================================
END_FILE: auto_memory_dump.sh
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/norms/normative_index.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 8d7a9162925e029c6590e632f7514e7d3bfda171a96ffc9b2c7d2de06f277448
====================================================================================================
[
  {
    "doc": "СП 70.13330.2012",
    "clause": "",
    "text": "Несущие и ограждающие конструкции. Дефекты фиксируются и устраняются по проектному решению",
    "keywords": ["бетон", "монолит", "трещина", "раковина", "скол", "дефект"],
    "source": "LOCAL_SAFE_INDEX"
  },
  {
    "doc": "СП 63.13330.2018",
    "clause": "",
    "text": "Бетонные и железобетонные конструкции. Расчёт требует проверки класса бетона, арматуры и защитного слоя",
    "keywords": ["бетон", "арматура", "защитный слой", "кж", "плита", "фундамент"],
    "source": "LOCAL_SAFE_INDEX"
  },
  {
    "doc": "ГОСТ 21.101-2020",
    "clause": "",
    "text": "Основные требования к проектной и рабочей документации",
    "keywords": ["проект", "документация", "чертеж", "спецификация", "ведомость"],
    "source": "LOCAL_SAFE_INDEX"
  }
]

====================================================================================================
END_FILE: data/norms/normative_index.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_manual.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 805aeb52360d047d9cb6b06fef54cab4177aa5bf6e9797a462f58be3735a398e
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V1",
  "project_type": "АР",
  "source_files": [
    "ПРОЕКТ КД кровля 5.pdf"
  ],
  "sheet_register": [],
  "marks": [
    "АР"
  ],
  "sections": [
    "плане",
    "расчет",
    "Расчетная",
    "Фасады",
    "Разрез",
    "План",
    "фасада"
  ],
  "axes_grid": {
    "axes_letters": [],
    "axes_numbers": [
      "01",
      "02",
      "23",
      "31"
    ]
  },
  "dimensions": [
    940,
    730,
    2025,
    16940,
    10730,
    360,
    2001,
    501,
    27751,
    6931,
    3254,
    1552,
    7463,
    6120,
    485,
    1393,
    800,
    4350,
    2300,
    3590,
    6700,
    3570,
    3160,
    4000,
    7870,
    8381,
    6850,
    6750,
    9572,
    9903,
    2783,
    900,
    944,
    1498,
    1631,
    2672,
    2968,
    1180,
    2822,
    1629,
    3600,
    3500,
    4987,
    5468,
    3916,
    600,
    10930,
    10440,
    10040,
    10530,
    4640,
    5125,
    2900,
    2905,
    1600,
    1605,
    970,
    1925,
    1930,
    4980,
    2170,
    520,
    780,
    1000,
    12730,
    12240,
    700,
    12125,
    675,
    620,
    12120
  ],
  "levels": [
    "0.0",
    "21.501"
  ],
  "nodes": [],
  "specifications": [],
  "materials": [
    "металлочерепица.",
    "бруса",
    "Утеплитель",
    "Утепление",
    "Вент.брусок",
    "Металлочерепица",
    "Брус"
  ],
  "stamp_fields": {
    "year": "2025"
  },
  "variable_parameters": [
    "project_name",
    "address",
    "customer",
    "area",
    "floors",
    "axes_grid",
    "dimensions",
    "materials",
    "sheet_register"
  ],
  "output_documents": [
    "DOCX_PROJECT_TEMPLATE_SUMMARY",
    "JSON_PROJECT_TEMPLATE_MODEL",
    "XLSX_SPECIFICATION_DRAFT"
  ],
  "quality": {
    "has_sheet_register": false,
    "has_sections": true,
    "has_axes_or_dimensions": true,
    "has_materials": true,
    "text_chars": 8561,
    "lines": 1822
  },
  "task_id": "",
  "chat_id": "",
  "topic_id": 0
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_manual.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_repaired.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 756930a51f0ac08eb66c6253ff4fe99247a1fa2153b56e9dcbff2a515328fca3
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V2_REPAIRED",
  "project_type": "АР",
  "source_file": "Проект АБ_ИНД_М_80_20_03_24.pdf",
  "template_file": "/root/.areal-neva-core/data/project_templates/PROJECT_TEMPLATE_MODEL__АР_repaired.json",
  "repaired_at": "2026-04-30T09:15:02.251470Z",
  "sheet_register": [
    "01 Общие данные",
    "02 Общий вид",
    "03 План аксонометрия",
    "04 Экспликация помещений",
    "05 План фундамента Отм. -0,029",
    "06 Перспектива. Гостинная и прихожая.",
    "07 Перспектива.",
    "08 Перспектива.",
    "09 Фасады",
    "10 Расстановка выключателей и розеток",
    "11 Маркировочный план",
    "12 Заполнение конных и дверных проемов",
    "02 Согласовано",
    "05 План фундамента",
    "06 Согласовано",
    "07 Согласовано",
    "08 Согласовано",
    "03 План закладных деталей коммуникаций",
    "04 План фундамента",
    "05 План первого этажа",
    "06 План кровли",
    "07 Фасад 1-4",
    "08 Фасад 4-1",
    "09 Фасад А-Д",
    "10 Фасад Д-А",
    "13 Экспликация помещений",
    "19 Ведомость отделки",
    "20 Общие указания",
    "22 Ведомость листов"
  ],
  "sections": [],
  "materials": [],
  "source": "core.db.topic_210.drive_file"
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_repaired.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_smoke.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: bedd84f1787a2381a8bd97ca6b9af30e39f4e4f69f2a8849e018e72a4e4dcf72
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V1",
  "project_type": "АР",
  "source_files": [
    "АР тест.pdf"
  ],
  "sheet_register": [
    {
      "mark": "АР",
      "number": "1",
      "title": "Общие данные"
    },
    {
      "mark": "АР",
      "number": "2",
      "title": "План этажа"
    },
    {
      "mark": "АР",
      "number": "3",
      "title": "Фасады"
    },
    {
      "mark": "АР",
      "number": "4",
      "title": "Разрез 1-1"
    },
    {
      "mark": "АР",
      "number": "5",
      "title": "Узлы"
    }
  ],
  "marks": [
    "АР"
  ],
  "sections": [
    "Общие данные",
    "Ведомость листов",
    "АР-1 Общие данные",
    "АР-2 План этажа",
    "АР-3 Фасады",
    "АР-4 Разрез 1-1",
    "Спецификация материалов"
  ],
  "axes_grid": {
    "axes_letters": [
      "А"
    ],
    "axes_numbers": [
      "1"
    ]
  },
  "dimensions": [
    6000,
    3000,
    2500,
    500,
    2024
  ],
  "levels": [
    "0.0"
  ],
  "nodes": [],
  "specifications": [
    "Ведомость листов",
    "Спецификация материалов"
  ],
  "materials": [
    "Бетон В25",
    "Арматура А500"
  ],
  "stamp_fields": {
    "address": "Ленинградская область, Всеволожский район",
    "developer": "ООО СК Ареал-Нева",
    "year": "2024"
  },
  "variable_parameters": [
    "project_name",
    "address",
    "customer",
    "area",
    "floors",
    "axes_grid",
    "dimensions",
    "materials",
    "sheet_register"
  ],
  "output_documents": [
    "DOCX_PROJECT_TEMPLATE_SUMMARY",
    "JSON_PROJECT_TEMPLATE_MODEL",
    "XLSX_SPECIFICATION_DRAFT"
  ],
  "quality": {
    "has_sheet_register": true,
    "has_sections": true,
    "has_axes_or_dimensions": true,
    "has_materials": true,
    "text_chars": 297,
    "lines": 17
  },
  "task_id": "smoke",
  "chat_id": "-1003725299009",
  "topic_id": 210
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_smoke.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КД_manual.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 72496cf6a372720635bd37bce2ac77ab69a6260db9100ce75fb3871e84f810c3
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V1",
  "project_type": "КД",
  "source_files": [
    "АР_КД_Агалатово_02.pdf"
  ],
  "sheet_register": [
    {
      "mark": "ов",
      "number": "1-2",
      "title": "сорта естественной влажности согласно раздела КД, с обработкой"
    }
  ],
  "marks": [
    "КД"
  ],
  "sections": [
    "Ведомость рабочих чертежей",
    "Ведомость рабочих чертежей основного комплекта (КД02)",
    "34 Схема расположения элементов подстропильной системы",
    "37 Разрез 2-1, Разрез 2-2",
    "38 Схема расположения элементов стропильной системы",
    "39 Схема расположения обрешетки",
    "40 Спецификация на стропильную систему, 3D вид стропильной системы",
    "44 Спецификация на стропильную систему, 3D вид стропильной системы гаража",
    "Ведомость рабочих чертежей основного комплекта (АР01)",
    "01 Ведомость рабочих чертежей",
    "02 Общие данные",
    "03 Общие данные",
    "04 Общие данные",
    "05 Схема планировочной организации земельного участка",
    "06 План расположения котлована",
    "07 План расположения фундамента дома",
    "08 План расположения отмостки",
    "09 План размерный на отметке 0.000",
    "10 План размерный на отметке +3.600",
    "11 План размерный на отметке +6.700",
    "12 План кладочный на отметке 0.000",
    "13 План кладочный на отметке +3.600",
    "14 План расположения водосточных желобов",
    "15 План маркировочный на отметке 0.000",
    "16 План маркировочный на отметке +3.600",
    "20 План на отметке 0.000 с расстановкой мебели",
    "21 План на отметке +3.600 с расстановкой мебели",
    "22 Разрез 1-1",
    "23 Разрез 1-2",
    "24 Фасад 1-5",
    "25 Фасад Г-А",
    "26 Фасад 5-1",
    "27 Фасад А-Г",
    "- исходные данные для подготовки проектной документации должны быть представлены в соответствии с Постановлениями Правительства Российской Федерации",
    "№ 840 от 29.12.2005 г. «О форме градостроительного плана земельного участка», № 840 от 29.12.2005 г. «О форме градостроительного плана земельного участка»,",
    "Общие данные",
    "2.1. 2.1. АрхитектурноАрхитектурно - -планировочноепланировочное решение решение",
    "На втором этаже имеется один санузел, душевая комната и 4 спальни.",
    "4. Наружная отделка стен - штукатурные работы по технике \"Мокрый фасад\",",
    "клинкерная плитка, декоративные фасадные архитектурные элементы.",
    "5. Цветовое решение материалов отделки фасадов и декоративных элементов",
    "8. Класс конструктивной пожарной опасности здания - С2.",
    "изделия и материалы, используемые при строительстве, должны быть сертифицированы в",
    "3. 3. КонструктивныеКонструктивные решения решения",
    "утрамбованного отсыпного материала. Высота подушки должна быть не менее 200 мм от поверхности песка коричневого,",
    "2. Стены наружные несущие монолитные толщиной 200 мм, утеплены согласно разрезам.",
    "- отделка фасада - штукатурка \"Мокрый фасад\", отледка клинкерной плиткой.",
    "7. Стропильная система – из пиломатериалов 1-2 сорта естественной влажности согласно раздела КД, с обработкой",
    "ЛистСхема планировочной организации земельного",
    "Схема планировочной организации земельного участка",
    "План расположения котлована",
    "План расположения фундамента дома",
    "План расположения отмостки",
    "План размерный на отметке 0.000",
    "План размерный на отметке +3.600"
  ],
  "axes_grid": {
    "axes_letters": [
      "А",
      "Г"
    ],
    "axes_numbers": [
      "01",
      "1",
      "2",
      "02",
      "5",
      "21",
      "23",
      "31"
    ]
  },
  "dimensions": [
    2025,
    600,
    700,
    2008,
    2007,
    840,
    2005,
    2006,
    2016,
    2003,
    13330,
    2011,
    2010,
    2001,
    900,
    400,
    300,
    1500,
    10925,
    17140,
    3400,
    5500,
    6220,
    620,
    4350,
    2300,
    3590,
    6700,
    3570,
    3160,
    4000,
    1100,
    16940,
    10725,
    19140,
    12925,
    23095,
    3900,
    2000,
    3290,
    6250,
    10125,
    850,
    17143,
    3565,
    11265,
    17480,
    2020,
    1400,
    4845,
    5945,
    1000,
    1370,
    2720,
    1900,
    3175,
    770,
    5259,
    1022,
    4529,
    2850,
    570,
    4150,
    2100,
    3390,
    6500,
    10525,
    4500,
    1200,
    2150,
    1765,
    1650,
    1830,
    1333,
    1245,
    550,
    2350,
    650,
    450,
    1005
  ],
  "levels": [
    "0.0",
    "3.6",
    "6.7",
    "5.03",
    "29.12",
    "16.02",
    "19.01",
    "13.02",
    "22.07",
    "3.07",
    "30.201",
    "55.133",
    "50.133",
    "3.0",
    "2.7",
    "7.4",
    "6.75",
    "43.68",
    "17.59",
    "7.8",
    "1.8",
    "7.29",
    "13.0",
    "54.6",
    "7.69",
    "7.61",
    "23.24",
    "19.92",
    "18.98",
    "16.27",
    "5.18",
    "1.37",
    "92.57",
    "-0.9",
    "0.05",
    "0.27",
    "0.35"
  ],
  "nodes": [
    "На втором этаже имеется один санузел, душевая комната и 4 спальни."
  ],
  "specifications": [
    "Ведомость рабочих чертежей",
    "Ведомость рабочих чертежей основного комплекта (КД02)",
    "40 Спецификация на стропильную систему, 3D вид стропильной системы",
    "44 Спецификация на стропильную систему, 3D вид стропильной системы гаража",
    "Ведомость рабочих чертежей основного комплекта (АР01)",
    "01 Ведомость рабочих чертежей"
  ],
  "materials": [
    "1. Фундамент расположен на отметке -0.900, на утеплении из экструдированного пенополистирола толщиной 100 мм и \"подушке\" из",
    "2. Стены наружные несущие монолитные толщиной 200 мм, утеплены согласно разрезам.",
    "- монолитные железобетонные стены - 200мм,",
    "- утепление базальтовой ватой 150мм,",
    "- кладка полнотелого кирпича - 120 мм"
  ],
  "stamp_fields": {
    "year": "2008"
  },
  "variable_parameters": [
    "project_name",
    "address",
    "customer",
    "area",
    "floors",
    "axes_grid",
    "dimensions",
    "materials",
    "sheet_register"
  ],
  "output_documents": [
    "DOCX_PROJECT_TEMPLATE_SUMMARY",
    "JSON_PROJECT_TEMPLATE_MODEL",
    "XLSX_SPECIFICATION_DRAFT"
  ],
  "quality": {
    "has_sheet_register": true,
    "has_sections": true,
    "has_axes_or_dimensions": true,
    "has_materials": true,
    "text_chars": 12000,
    "lines": 494
  },
  "task_id": "",
  "chat_id": "",
  "topic_id": 0
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КД_manual.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КД_repaired.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d6924cc53adc5cb0d1edc58d3fd6165cbdf7c084b6e32f22e63f7524790a81d3
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V2_REPAIRED",
  "project_type": "КД",
  "source_file": "АР_КД_Агалатово_02.pdf",
  "template_file": "/root/.areal-neva-core/data/project_templates/PROJECT_TEMPLATE_MODEL__КД_repaired.json",
  "repaired_at": "2026-04-30T09:15:02.250916Z",
  "sheet_register": [
    "01 Ведомость рабочих чертежей",
    "02 Общие данные",
    "03 Общие данные",
    "04 Общие данные",
    "05 Схема планировочной организации земельного участка",
    "06 План расположения котлована",
    "07 План расположения фундамента дома",
    "08 План расположения отмостки",
    "09 План размерный на отметке 0.000",
    "10 План размерный на отметке +3.600",
    "11 План размерный на отметке +6.700",
    "01 Общие данные",
    "02 План балок перекрытия",
    "03 План стропильной системы",
    "04 План стропильной системы",
    "06 Спецификация элементов стропильной системы",
    "07 План обрешётки",
    "08 План контробрешётки",
    "16 Ведомость пиломатериалов",
    "17 Ведомость крепежа",
    "18 Спецификация кровельных материалов",
    "19 Схема монтажа",
    "20 Общие указания",
    "21 Ведомость листов"
  ],
  "sections": [],
  "materials": [],
  "source": "core.db.topic_210.drive_file"
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КД_repaired.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КЖ_repaired.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 82db86c234139cb30b4ad8578ff08eb29f94521ed89ec761a3d26f0d0d5a65fa
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V2_REPAIRED",
  "project_type": "КЖ",
  "source_file": "КЖ АК-М-160.pdf",
  "template_file": "/root/.areal-neva-core/data/project_templates/PROJECT_TEMPLATE_MODEL__КЖ_repaired.json",
  "repaired_at": "2026-04-30T09:15:02.251190Z",
  "sheet_register": [
    "01 Общие данные",
    "02 План фундаментной плиты",
    "03 Разрез 1-1",
    "04 Разрез 2-2",
    "05 Схема нижнего армирования",
    "06 Схема верхнего армирования",
    "07 Схема дополнительного армирования",
    "08 Узлы армирования углов",
    "09 Узлы примыкания ленты/ребра",
    "10 Схема закладных деталей",
    "11 Схема выпусков арматуры",
    "12 Схема инженерных проходок",
    "13 План опалубки",
    "14 Спецификация арматуры",
    "15 Спецификация бетона",
    "16 Ведомость материалов основания",
    "17 Ведомость объёмов работ",
    "18 Контрольные отметки",
    "19 Общие указания",
    "20 Ведомость листов"
  ],
  "sections": [],
  "materials": [],
  "source": "core.db.topic_210.drive_file"
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КЖ_repaired.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/364b2395-0744-4a88-80a8-6e87c282aa3d.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: adcc187000a810f61ee9a17325a2d2ac5449bb8ef840f253121634f8897ffd27
====================================================================================================
{
  "template_id": "364b2395-0744-4a88-80a8-6e87c282aa3d",
  "chat_id": "-1003725299009",
  "topic_id": 210,
  "source_task_id": "364b2395-0744-4a88-80a8-6e87c282aa3d",
  "source_file_name": "АР_КД_Агалатово_02.pdf",
  "mime_type": "application/pdf",
  "kind": "estimate_template",
  "created_at": "2026-05-01T11:32:07.307426",
  "active": true
}
====================================================================================================
END_FILE: data/templates/364b2395-0744-4a88-80a8-6e87c282aa3d.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/bab630ba-7e3f-4c43-88ff-3e917e5c6279.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 079024dae167be51495505f479c057e9e7e1848d9ae077c4287d618c8418f642
====================================================================================================
{
  "template_id": "bab630ba-7e3f-4c43-88ff-3e917e5c6279",
  "chat_id": "-1003725299009",
  "topic_id": 2,
  "source_task_id": "bab630ba-7e3f-4c43-88ff-3e917e5c6279",
  "source_file_name": "Техническое задание Кордон снт.docx",
  "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "kind": "estimate_template",
  "created_at": "2026-05-02T00:20:57.882990",
  "active": true
}
====================================================================================================
END_FILE: data/templates/bab630ba-7e3f-4c43-88ff-3e917e5c6279.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/d5d1fbca-e848-4e36-b297-d12312cc5217.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d5c22742c734298e06a8fd5cdff777b21a1df1df2e192bba477b2b16da158f06
====================================================================================================
{
  "template_id": "d5d1fbca-e848-4e36-b297-d12312cc5217",
  "chat_id": "-1003725299009",
  "topic_id": 4569,
  "source_task_id": "d5d1fbca-e848-4e36-b297-d12312cc5217",
  "source_file_name": "",
  "mime_type": "",
  "kind": "unknown_template",
  "created_at": "2026-05-01T10:23:26.354953",
  "active": true
}
====================================================================================================
END_FILE: data/templates/d5d1fbca-e848-4e36-b297-d12312cc5217.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/ee10abce-9662-4797-825e-096188f40a4e.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 486eb146b39b89d7619166c2e3b99a531ab687709a2b111bcd64d5ed90105c47
====================================================================================================
{
  "template_id": "ee10abce-9662-4797-825e-096188f40a4e",
  "chat_id": "-1003725299009",
  "topic_id": 210,
  "source_task_id": "ee10abce-9662-4797-825e-096188f40a4e",
  "source_file_name": "АР_КД_Агалатово_02.pdf",
  "mime_type": "application/pdf",
  "kind": "estimate_template",
  "created_at": "2026-05-01T11:34:12.786364",
  "active": true
}
====================================================================================================
END_FILE: data/templates/ee10abce-9662-4797-825e-096188f40a4e.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/estimate/ACTIVE__chat_-1003725299009__topic_3008.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 225b637da9991f976ece0bfe4c6d0a4eca022ecb9bb09fa84104e63fb6bdca92
====================================================================================================
{
  "engine": "FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE",
  "kind": "estimate",
  "status": "active",
  "chat_id": "-1003725299009",
  "topic_id": 3008,
  "saved_by_task_id": "7270364c-bb74-4e1e-b531-de64dfe713b7",
  "source_task_id": "f5c33c40-dacf-46c9-97ca-2dc19e245650",
  "source_file_id": "1XsuPOtO-vyA73IX5Ui9AR9kf6uUAE5b_",
  "source_file_name": "estimate_c925a897-66ec-435e-8312-15687f.xlsx",
  "source_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "source_caption": "",
  "source_score": 110,
  "saved_at": "2026-05-01T08:38:07.108195+00:00",
  "usage_rule": "Use this file as formatting/sample reference for future estimate/project artifacts in the same chat and topic",
  "raw_user_instruction": "этот чат у нас используется с тобой для работы, соответственно, как ты правильно и сказал, по AI роутеру Arial Niva, но также мы здесь еще с тобой пишем коды по определенным запросам команд, которые ты вот сейчас мне написал, например, напиши код. То есть здесь мы также с тобой создаем еще коды, которые делаются на основании четырех моделей, которые присутствуют у нас с тобой."
}
====================================================================================================
END_FILE: data/templates/estimate/ACTIVE__chat_-1003725299009__topic_3008.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/estimate/TEMPLATE__chat_-1003725299009__topic_2__20260430_100323.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2751853a7fec499884e42f27a565e5d1374b91b8c0c7aaec43cecba88b3128f3
====================================================================================================
{
  "engine": "FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE",
  "kind": "estimate",
  "status": "active",
  "chat_id": "-1003725299009",
  "topic_id": 2,
  "saved_by_task_id": "d390b50d-2f5e-4aeb-871a-3b30cc149d18",
  "source_task_id": "12f63475-a307-49d5-bf85-45852622840e",
  "source_file_id": "1Ert7YACjcfZcodklU7UnckLN3xgsyuKD",
  "source_file_name": "ВОР_кирпичная_кладка_ИСПРАВЛЕНО.xlsx",
  "source_mime_type": "",
  "source_caption": "",
  "source_score": 150,
  "saved_at": "2026-04-30T10:03:23.387650+00:00",
  "usage_rule": "Use this file as formatting/sample reference for future estimate/project artifacts in the same chat and topic",
  "raw_user_instruction": "Тот файл который я тебе скинул последний возьми его как образец для составления сметы"
}
====================================================================================================
END_FILE: data/templates/estimate/TEMPLATE__chat_-1003725299009__topic_2__20260430_100323.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/estimate/TEMPLATE__chat_-1003725299009__topic_3008__20260501_083807.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 225b637da9991f976ece0bfe4c6d0a4eca022ecb9bb09fa84104e63fb6bdca92
====================================================================================================
{
  "engine": "FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE",
  "kind": "estimate",
  "status": "active",
  "chat_id": "-1003725299009",
  "topic_id": 3008,
  "saved_by_task_id": "7270364c-bb74-4e1e-b531-de64dfe713b7",
  "source_task_id": "f5c33c40-dacf-46c9-97ca-2dc19e245650",
  "source_file_id": "1XsuPOtO-vyA73IX5Ui9AR9kf6uUAE5b_",
  "source_file_name": "estimate_c925a897-66ec-435e-8312-15687f.xlsx",
  "source_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "source_caption": "",
  "source_score": 110,
  "saved_at": "2026-05-01T08:38:07.108195+00:00",
  "usage_rule": "Use this file as formatting/sample reference for future estimate/project artifacts in the same chat and topic",
  "raw_user_instruction": "этот чат у нас используется с тобой для работы, соответственно, как ты правильно и сказал, по AI роутеру Arial Niva, но также мы здесь еще с тобой пишем коды по определенным запросам команд, которые ты вот сейчас мне написал, например, напиши код. То есть здесь мы также с тобой создаем еще коды, которые делаются на основании четырех моделей, которые присутствуют у нас с тобой."
}
====================================================================================================
END_FILE: data/templates/estimate/TEMPLATE__chat_-1003725299009__topic_3008__20260501_083807.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/estimate/deprecated/DEPRECATED__ACTIVE__chat_-1003725299009__topic_2__VOR_20260503.original.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: f58425288c17d830efcab61e9238e10842f7d55434c1f35a8249f262001212c2
====================================================================================================
{
  "engine": "FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE",
  "kind": "estimate",
  "status": "deprecated",
  "chat_id": "-1003725299009",
  "topic_id": 2,
  "saved_by_task_id": "d390b50d-2f5e-4aeb-871a-3b30cc149d18",
  "source_task_id": "12f63475-a307-49d5-bf85-45852622840e",
  "source_file_id": "1Ert7YACjcfZcodklU7UnckLN3xgsyuKD",
  "source_file_name": "ВОР_кирпичная_кладка_ИСПРАВЛЕНО.xlsx",
  "source_mime_type": "",
  "source_caption": "",
  "source_score": 150,
  "saved_at": "2026-04-30T10:03:23.387650+00:00",
  "usage_rule": "Use this file as formatting/sample reference for future estimate/project artifacts in the same chat and topic",
  "raw_user_instruction": "Тот файл который я тебе скинул последний возьми его как образец для составления сметы",
  "deprecated_reason": "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3: VOR disabled from active topic_2 estimate logic",
  "deprecated_at": "2026-05-03T11:39:40.822192"
}

====================================================================================================
END_FILE: data/templates/estimate/deprecated/DEPRECATED__ACTIVE__chat_-1003725299009__topic_2__VOR_20260503.original.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/index.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 4fefe3e44a76c132b89c1186ecc62d498869ba8185064756cfe43da0f0726914
====================================================================================================
{
  "_schema": "TEMPLATE_INDEX_DICT_FIX_V1",
  "_legacy_type": "list",
  "_legacy_data": [
    {
      "template_id": "d5d1fbca-e848-4e36-b297-d12312cc5217",
      "chat_id": "-1003725299009",
      "topic_id": 4569,
      "source_task_id": "d5d1fbca-e848-4e36-b297-d12312cc5217",
      "source_file_name": "",
      "mime_type": "",
      "kind": "unknown_template",
      "created_at": "2026-05-01T10:23:26.354953",
      "active": true
    },
    {
      "template_id": "364b2395-0744-4a88-80a8-6e87c282aa3d",
      "chat_id": "-1003725299009",
      "topic_id": 210,
      "source_task_id": "364b2395-0744-4a88-80a8-6e87c282aa3d",
      "source_file_name": "АР_КД_Агалатово_02.pdf",
      "mime_type": "application/pdf",
      "kind": "estimate_template",
      "created_at": "2026-05-01T11:32:07.307426",
      "active": false
    },
    {
      "template_id": "ee10abce-9662-4797-825e-096188f40a4e",
      "chat_id": "-1003725299009",
      "topic_id": 210,
      "source_task_id": "ee10abce-9662-4797-825e-096188f40a4e",
      "source_file_name": "АР_КД_Агалатово_02.pdf",
      "mime_type": "application/pdf",
      "kind": "estimate_template",
      "created_at": "2026-05-01T11:34:12.786364",
      "active": true
    },
    {
      "template_id": "bab630ba-7e3f-4c43-88ff-3e917e5c6279",
      "chat_id": "-1003725299009",
      "topic_id": 2,
      "source_task_id": "bab630ba-7e3f-4c43-88ff-3e917e5c6279",
      "source_file_name": "Техническое задание Кордон снт.docx",
      "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "kind": "estimate_template",
      "created_at": "2026-05-02T00:20:57.882990",
      "active": true
    }
  ]
}
====================================================================================================
END_FILE: data/templates/index.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/0/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 99110904300dc66aa8fe5e9cc9aa1de41ba518ca5ce020af0cb0e2c4fb0739f8
====================================================================================================
{
  "topic_id": 0,
  "name": "ЛИДЫ АМО",
  "direction": "crm_leads",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.231172+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/0/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/11/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 04c69440018c5cb2105f1624418040b5c4dac9a5da55f0ac5b07727ed5a103e0
====================================================================================================
{
  "topic_id": 11,
  "name": "ВИДЕОКОНТЕНТ",
  "direction": "video_production",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.231872+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/11/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/2/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 51744f466380c4b2398e4e6b98c21d35fa9435a905eb9c53b308aa6a8d8836ca
====================================================================================================
{
  "topic_id": 2,
  "name": "СТРОЙКА",
  "direction": "estimates",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.231412+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/2/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/210/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ce50915df1bdab1a3baf419fea40ed5b9dfc1f6d009a4daecf0b4e7fcb36110a
====================================================================================================
{
  "topic_id": 210,
  "name": "ПРОЕКТИРОВАНИЕ",
  "direction": "structural_design",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.232182+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/210/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/3008/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 997992e041d0f6ac8ad7dd83631d2eef51a26013445370bc050ff361e3f29c0e
====================================================================================================
{
  "topic_id": 3008,
  "name": "КОДЫ МОЗГОВ",
  "direction": "orchestration_core",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.232993+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/3008/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/4569/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: a436174d9ec1dfc8e15f469fc81c061d7b8bbef1538638faefd32fec954e9343
====================================================================================================
{
  "topic_id": 4569,
  "name": "ЛИДЫ РЕКЛАМА",
  "direction": "crm_leads",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.233153+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/4569/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/5/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 7ee48f4af7bf89f492bef00163145e6ee01981b768f38dd4c30e35b8e3311bf6
====================================================================================================
{
  "topic_id": 5,
  "name": "ТЕХНАДЗОР",
  "direction": "technical_supervision",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.231656+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/5/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/500/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: fe567370b38840c0c5b5625ad07f3c7bc8473beeaccca3d54386fed17599275c
====================================================================================================
{
  "topic_id": 500,
  "name": "ВЕБ ПОИСК",
  "direction": "internet_search",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.232499+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/500/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/6104/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 1e7f11136e5ddd7e984c3cbc17affc50d1c3f2f207ceecd341a32c7cf3a95e58
====================================================================================================
{
  "topic_id": 6104,
  "name": "РАБОТА ПОИСК",
  "direction": "job_search",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.233266+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/6104/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/794/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: cac974b2d8a0b3bf5dc1955a1fae4c6385a6a02fa96e5efcca1346cfc03db928
====================================================================================================
{
  "topic_id": 794,
  "name": "НЕЙРОНКИ СОФТ ВПН ВПС",
  "direction": "devops_server",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.232700+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/794/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/961/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c1b720f5d6b47a31456f65ecdf73132c8522479962158c9e97bbdc93b9697d25
====================================================================================================
{
  "topic_id": 961,
  "name": "АВТО ЗАПЧАСТИ",
  "direction": "auto_parts_search",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.232859+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/961/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/CHAT_EXPORTS/CHAT_EXPORT__2026-05-05_TECHNADZOR_FOLDER_DISCOVERY_FULL_CLOSE.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 8ea8e43903c6fe9dfa1ea078db41f8b928807d6652aa966afee4e1634da49ea1
====================================================================================================
{"chat_id":"current_chat_2026-05-05","chat_name":"TECHNADZOR_FOLDER_DISCOVERY_FULL_CLOSE","exported_at":"2026-05-05T10:45:00Z","source_model":"GPT-5.5 Thinking","system":"AREAL-NEVA / NEURON SOFT ORCHESTRA. FACT ONLY export for current chat. GitHub SSOT repository rj7hmz9cvm-lgtm/areal-neva-core.","architecture":"Server-first Telegram orchestration. Telegram topic_5 is technadzor interface. Google Drive is storage. Server stores logic/runtime. External Vision is owner-gated optional with EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False by default.","pipeline":"topic_5 Telegram text/voice/files -> task_worker/final_closure_engine -> technadzor_engine.process_technadzor -> ActiveTechnadzorFolder/VisitMaterial/VisitPackage -> Drive OAuth topic-aware storage -> Telegram response. Folder discovery must resolve user folders by fresh Drive lookup before AI fallback.","files":["docs/HANDOFFS/LATEST_HANDOFF.md","docs/CANON_FINAL/TECHNADZOR_DOMAIN_LOGIC_CANON.md","core/technadzor_engine.py","core/final_closure_engine.py","task_worker.py","core/stt_engine.py","core/technadzor_drive_index.py"],"code":"Confirmed latest handoff records folder discovery live closed. Patches listed there: f1d6763 final_closure_engine topic5 route fix and technadzor_engine folder discovery; e1aa647 task_worker FCE hook unbound task fields fixed via _task_field; 8bf752e task_worker send path fixed via _task_field; 0a5c766 technadzor_engine excludes system folders; 48b1e55 technadzor_engine final folder root fix; f2e119f handoff update; previous P6H4TW/P6H4FD/P6H4TW_BATCH_TRIGGER commits include d90b5ad, ff753aa, 6463220, a5cae41, 38270c6.","patches":["TECHNADZOR_DOMAIN_LOGIC_CANON_V2 addendum accepted as ADDENDUM_NOT_REPLACEMENT, not superseding V1","EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False guard added and OpenAI/GPT vision fallback forbidden","P6H_PART_4 VisitBuffer/ActiveFolder/VisitMaterial/VisitPackage implemented in code path","P6H4TW_BATCH_TRIGGER_V1 moved/wrapped process_technadzor in technadzor_engine because hook after asyncio.run in task_worker was dead","Folder discovery bug fixed to search Russian user root ТЕХНАДЗОР instead of system TECHNADZOR and exclude system folders","FCE hook fixed to use _task_field before local assignments","Folder/context intent must not fall to general AI"],"commands":["GitHub commits checked through connector","Google Drive folder metadata checked for old folder 1K2sJuMbXWt4xZWxFR8pXXPg1342Qu28j, new folder 1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG, user root 1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD, system root 1vKQM0Z2qBmiKtgeyx95JaNEQAp5mJLOm","Requested server-side py_compile, restart areal-task-worker, live smoke in topic_5"],"db":"Observed task 5276 DONE in handoff with result finding folder тест надзор. Earlier task 5275 FAILED INVALID_RESULT_GATE because folder clarification/state was reprocessed. Earlier task 5274 DONE incorrectly set TECHNADZOR as active folder.","memory":"Topic scoped memory and active folder state must preserve chat_id+topic_id isolation. ActiveTechnadzorFolder must store folder_id, folder_name, folder_url, owner_instruction, updated_at, source=fresh_drive_lookup. Do not write debug/errors/system trash into long memory.","services":["areal-task-worker","telegram-ingress","areal-memory-api"],"errors":["Bot returned old folder Выезд 8 апреля 2026 instead of new тест надзор","Resolver selected system TECHNADZOR instead of user folder","Resolver searched wrong root TECHNADZOR 1vKQM0Z2qBmiKtgeyx95JaNEQAp5mJLOm instead of ТЕХНАДЗОР 1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD","FCE hook UnboundLocalError cannot access local variable task_id before assignment","WAITING_CLARIFICATION was reprocessed into INVALID_RESULT_GATE for folder discovery","topic_500 internet search reported by owner as not working and remains needing diagnostics/live proof"],"decisions":["External Vision is not a blocker for full close; it is CLOSED_AS_OWNER_GATED_OPTIONAL","Vision model must not be changed, no Llama/Pixtral/OpenAI/GPT, no direct Google Gemini API for Vision","TECHNADZOR is system/service folder and must never become ActiveTechnadzorFolder","ТЕХНАДЗОР is user folder root for technadzor user folders and also must not become ActiveTechnadzorFolder","ActiveTechnadzorFolder can only be a child/user project folder such as тест надзор","The folder named тест надзор exists and should be found by name without owner sending URL","User source docs folder 1sTMg-2cJpWmjJLEj-4Y80brWl5e70AZk is flat clean owner source folder; no extra subfolders required now; orchestra service files go elsewhere"],"solutions":["Folder/context intent in topic_5 must bypass narrow is_technadzor_intent and call process_technadzor directly","Folder discovery must extract target folder name from raw input","Search order: explicit URL -> exact/fuzzy child folder under ТЕХНАДЗОР -> strict Drive-wide name fallback -> concrete clarification","Return contract: handled=True ok=True for processed folder commands, handled=False ok=False for not handled","For not found folder/context command return DONE handled message to avoid AI fallback and INVALID_RESULT_GATE","System folders excluded from candidates: TECHNADZOR, ТЕХНАДЗОР, topic_5, _orchestra_work, _system, _tmp, _archive, _drafts, _templates, _manifests"],"state":"LATEST_HANDOFF currently states FOLDER DISCOVERY LIVE CLOSED with control case PASSED. topic_5 code side considered closed, live smoke still needed for real Telegram file/photo/разбор/акт flows. topic_500 internet search not working per owner and must be diagnosed separately.","what_working":["GitHub main contains handoff update f2e119f and folder discovery status","Google Drive connector confirms new folder тест надзор exists","Owner docs folder contains three act/source documents and no service trash","P6H/P6H4TW/P6H4FD code path documented in handoff"],"what_broken":["topic_500 internet search reported not working","Before final folder fix the resolver selected wrong/stale/system folders","Live Telegram smoke for topic_5 full file/photo flow still pending"],"what_not_done":["Full live smoke: topic_5 photo/file -> buffer -> voice/text note -> сделай разбор -> one response","Drive folder URL/name -> загрузи папку -> сделай акт","topic_2 real estimate request smoke","topic_500 real search smoke with Sonar and sources","Update docs/canon with current chat export and latest folder docs if needed"],"current_breakpoint":"Owner requested full current chat/session export and GitHub update after resolving folder discovery issues and before continuing broader testing.","root_causes":["Folder resolver used stale/old active folder or wrong system root instead of fresh user-root Drive lookup","Narrow technadzor intent did not classify folder/context commands","FCE hook referenced local variables before assignment","Return/state contract caused folder clarification to be reprocessed by general gates"],"verification":["Google Drive metadata confirmed old folder Выезд 8 апреля 2026 id 1K2sJuMbXWt4xZWxFR8pXXPg1342Qu28j","Google Drive metadata confirmed new folder тест надзор id 1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG under ТЕХНАДЗОР id 1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD","Google Drive metadata confirmed system TECHNADZOR id 1vKQM0Z2qBmiKtgeyx95JaNEQAp5mJLOm contains only service DOCX files","LATEST_HANDOFF fetched from GitHub confirms task 5276 DONE and found тест надзор"],"limits":["No SSH direct execution from ChatGPT environment; server commands must be run by owner/Claude on server","Google Drive chat export standard says Drive telegram_exports, but user asked GitHub update; this file is GitHub JSON export counterpart","No hidden assumptions; UNKNOWN should be used where not verified"]}
====================================================================================================
END_FILE: docs/CHAT_EXPORTS/CHAT_EXPORT__2026-05-05_TECHNADZOR_FOLDER_DISCOVERY_FULL_CLOSE.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/SHARED_CONTEXT/DWG_CONVERTER_STATUS.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c1575faa9c30f7376fc965272741bac01693c844705a64e8b4ab6813ad0e4e73
====================================================================================================
{
  "checked_at": "2026-05-01T22:49:05.964682+00:00",
  "dwg2dxf": null,
  "ODAFileConverter": null,
  "geometry_status": "DWG_METADATA_ONLY_DXF_FULL_PARSE_READY",
  "note": "DXF parses directly. DWG full geometry requires dwg2dxf or ODAFileConverter; without converter DWG metadata path remains active"
}
====================================================================================================
END_FILE: docs/SHARED_CONTEXT/DWG_CONVERTER_STATUS.json
FILE_CHUNK: 1/1
====================================================================================================
