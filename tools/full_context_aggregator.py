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
    "docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md",
    "docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md",
    "docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md",
    "docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md",
    "docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json",
}
GENERATED_PREFIXES = (
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
        "tools/context_aggregator.py",
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
2. SAFE_RUNTIME_SNAPSHOT
3. ORCHESTRA_FULL_CONTEXT_MANIFEST
4. Required ORCHESTRA_FULL_CONTEXT_PART_XXX files

## RAW_LINKS
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
    ] + [
        f"docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md"
        for i in range(1, parts_count + 1)
    ]
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
            raise RuntimeError("CONTEXT_AGGREGATOR_NOT_TRACKED")

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

        stage_outputs(len(parts))
        run_secret_scan()
        new_sha = commit_push_verify()
        verify_raw_exact(new_sha)

        print(f"FULL_CONTEXT_AGGREGATOR_V1_DONE {utc_now()}")
        print(f"COMMIT_SHA {new_sha}")
        print(f"PARTS {len(parts)}")
        print(f"FILES_INCLUDED {len(full_items)}")


if __name__ == "__main__":
    main()
# === END_FULL_CONTEXT_AGGREGATOR_V1 ===
