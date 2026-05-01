#!/usr/bin/env python3
# === CLAUDE_BOOTSTRAP_AGGREGATOR_CANON_LOCK_V3 ===
from __future__ import annotations

import hashlib
import os
import re
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
OUTPUT = BASE / "docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md"
SNAPSHOT = BASE / "docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md"
SESSION_START = BASE / "docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md"

RAW_URL = "https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md"

STRICT_SOURCE_FILES = [
    "docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md",
    "docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md",
    "docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md",

    "docs/CANON_FINAL/00_INDEX.md",
    "docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md",
    "docs/CANON_FINAL/09_FILE_INTAKE_DRIVE_UPLOAD_2026-04-30.md",

    "docs/HANDOFFS/LATEST_HANDOFF.md",
    "docs/HANDOFFS/CHAT_EXPORT_PROTOCOL.md",

    "docs/REPORTS/NOT_CLOSED.md",

    "docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK.md",
    "docs/ARCHITECTURE/SEARCH_MONOLITH_V1.md",
    "docs/ARCHITECTURE/SEARCH_MONOLITH_V2.md",
]

STRICT_CODE_FILES = [
    "task_worker.py",
    "telegram_daemon.py",
    "memory_api_server.py",
    "core/ai_router.py",
    "core/search_session.py",
    "core/search_engine.py",
    "core/file_intake_router.py",
    "core/archive_engine.py",
    "core/reply_sender.py",
    "core/pin_manager.py",
    "core/topic_drive_oauth.py",
    "tools/context_aggregator.py",
    "tools/claude_bootstrap_aggregator.py",
]

SECRET_PATTERNS = (
    ".env",
    "credentials",
    "token",
    "session",
    "secret",
    "private",
    "key.json",
    "service_account",
    "client_secret",
)

MARKER_RE = re.compile(
    r"(SEARCH_MONOLITH|SEARCH_SESSION|MEMORY_QUERY|IN_PROGRESS_HARD_TIMEOUT|ARCHIVE_DEDUP|"
    r"PAYLOAD_TOPIC_ID|CONFIRMATION_TIMEOUT|HEALTHCHECK|VOICE_UPLOAD_SKIP|"
    r"TELEGRAM_TIMELINE|DRIVE_FILE_MEMORY|FILE_DUPLICATE|FULLFIX|CANON|ARCHIVE_ENGINE|"
    r"STT|GROQ|PERPLEXITY|OPENROUTER|TOPIC|PIN|REPLY|WATCHDOG|LIFECYCLE|"
    r"CLAUDE_BOOTSTRAP|SAFE_RUNTIME)",
    re.I,
)


def sh(cmd: list[str], check: bool = False) -> str:
    p = subprocess.run(cmd, cwd=str(BASE), text=True, capture_output=True)
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    if check and p.returncode != 0:
        raise RuntimeError(f"CMD_FAIL: {' '.join(cmd)}\n{out}")
    return out


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def safe_read(rel: str) -> str:
    if any(s in rel.lower() for s in SECRET_PATTERNS):
        return f"FORBIDDEN_SECRET_PATH: {rel}\n"
    p = BASE / rel
    if not p.exists() or not p.is_file():
        return f"UNKNOWN: file not found: {rel}\n"
    return p.read_text(encoding="utf-8", errors="replace")


def sqlite_scalar(db_path: Path, sql: str) -> str:
    try:
        if not db_path.exists():
            return "DB_NOT_FOUND"
        con = sqlite3.connect(str(db_path))
        try:
            row = con.execute(sql).fetchone()
            if row is None:
                return "NONE"
            return "|".join(str(x) for x in row)
        finally:
            con.close()
    except Exception as e:
        return f"SQL_ERROR:{e}"


def sqlite_rows(db_path: Path, sql: str, limit: int = 50) -> list[str]:
    try:
        if not db_path.exists():
            return ["DB_NOT_FOUND"]
        con = sqlite3.connect(str(db_path))
        try:
            rows = con.execute(sql).fetchmany(limit)
            return ["|".join(str(x) for x in row) for row in rows]
        finally:
            con.close()
    except Exception as e:
        return [f"SQL_ERROR:{e}"]


def build_claude_session_start_prompt() -> str:
    generated_at = datetime.now(timezone.utc).isoformat()
    return f"""# CLAUDE_SESSION_START_PROMPT

GENERATED_AT_UTC: {generated_at}

MANDATORY FIRST STEP:
Read the full file below before answering any technical question:

{RAW_URL}

If the file is unavailable, answer only:
CLAUDE_BOOTSTRAP_CONTEXT_UNAVAILABLE

OPERATING MODE:
FACT_ONLY
ZERO_ASSUMPTIONS
GITHUB_SSOT_ONLY
NO_MEMORY_GUESSING
NO_SELF_INITIATED_ARCHITECTURE_CHANGES
NO_PATCH_WITHOUT_DIAGNOSTICS
NO_ENV_TOUCH
NO_SECRET_TOUCH
NO_SESSION_TOUCH
NO_CREDENTIALS_TOUCH

PRIMARY PROJECT:
AREAL-NEVA ORCHESTRA

SERVER:
89.22.225.136

BASE_PATH:
/root/.areal-neva-core

GITHUB_SSOT:
https://github.com/rj7hmz9cvm-lgtm/areal-neva-core

RAW_BOOTSTRAP:
{RAW_URL}

MANDATORY ANSWER RULES:
1. State facts only from bootstrap, logs, code, or user-provided command output
2. If a fact is missing, write UNKNOWN
3. Never invent service state, file content, DB state, Git state, or runtime result
4. For patches: diagnostics first, backup second, patch third, compile fourth, restart fifth, logs sixth
5. Every patch must be named
6. Use only allowed files from canon unless user explicitly allows more
7. Do not modify .env, tokens, credentials, sessions, Google OAuth files, or DB schema unless the task explicitly requires it
8. Do not use memory from another topic
9. Do not treat topic_id=0 as a specific topic
10. Do not call a task closed until syntax, service, log, DB, Git, and runtime checks pass

WHEN ASKED "WHAT DO YOU KNOW":
Answer using only this bootstrap file and cite the section names from it

WHEN ASKED TO PATCH:
First verify live files and logs, then produce one monolithic SSH block

WHEN ASKED TO CLOSE A CANON:
Verify:
- code markers
- syntax
- services active
- runtime smoke
- DB open task count
- memory writes
- Git commit and push
- fatal logs
- canon docs updated

END
"""


def collect_code_markers() -> str:
    lines = []
    lines.append("# CODE_MARKERS_SAFE")
    lines.append("")
    for rel in STRICT_CODE_FILES:
        p = BASE / rel
        lines.append(f"## {rel}")
        if not p.exists():
            lines.append("UNKNOWN: missing")
            lines.append("")
            continue
        data = p.read_text(encoding="utf-8", errors="replace").splitlines()
        count = 0
        for i, line in enumerate(data, 1):
            if MARKER_RE.search(line):
                stripped = line.strip()
                if any(s in stripped.lower() for s in SECRET_PATTERNS):
                    continue
                lines.append(f"{i}: {stripped[:300]}")
                count += 1
                if count >= 100:
                    lines.append("...TRUNCATED_MARKERS...")
                    break
        if count == 0:
            lines.append("NO_MARKERS_FOUND")
        lines.append("")
    return "\n".join(lines)


def write_safe_runtime_snapshot() -> None:
    git_head = sh(["git", "rev-parse", "--short", "HEAD"])
    git_full = sh(["git", "rev-parse", "HEAD"])
    git_branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    git_status = sh(["git", "status", "--short"])

    services = []
    for svc in (
        "areal-task-worker",
        "telegram-ingress",
        "areal-memory-api",
        "areal-claude-bootstrap-aggregator.timer",
    ):
        services.append(f"{svc}: {sh(['systemctl', 'is-active', svc]) or 'UNKNOWN'}")

    core_db = BASE / "data/core.db"
    memory_db = BASE / "data/memory.db"

    db_state = sqlite_rows(
        core_db,
        "SELECT state, COUNT(*) FROM tasks GROUP BY state ORDER BY 2 DESC",
        20,
    )
    open_tasks = sqlite_scalar(
        core_db,
        "SELECT 'OPEN_TASKS', COUNT(*) FROM tasks WHERE state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')",
    )
    latest_tasks = sqlite_rows(
        core_db,
        "SELECT id, COALESCE(topic_id,0), input_type, state, substr(raw_input,1,80), substr(result,1,80), updated_at FROM tasks ORDER BY updated_at DESC LIMIT 12",
        12,
    )

    memory_rows = sqlite_scalar(memory_db, "SELECT 'MEMORY_ROWS', COUNT(*) FROM memory")
    memory_latest = sqlite_rows(
        memory_db,
        "SELECT key, substr(value,1,120), timestamp FROM memory ORDER BY timestamp DESC LIMIT 12",
        12,
    )
    search_sessions = sqlite_rows(
        memory_db,
        "SELECT key, substr(value,1,180), timestamp FROM memory WHERE key LIKE 'topic_500_search_session%' ORDER BY timestamp DESC LIMIT 5",
        5,
    )

    timeline_info = []
    tl = BASE / "data/memory_files/CHATS/-1003725299009__telegram/timeline.jsonl"
    if tl.exists():
        timeline_info.append(f"path={tl}")
        timeline_info.append(f"bytes={tl.stat().st_size}")
        timeline_info.append(f"mtime_utc={datetime.fromtimestamp(tl.stat().st_mtime, timezone.utc).isoformat()}")
    else:
        timeline_info.append("timeline=NOT_FOUND")

    files_manifest = []
    for rel in STRICT_SOURCE_FILES + STRICT_CODE_FILES:
        p = BASE / rel
        if p.exists() and p.is_file():
            try:
                data = p.read_text(encoding="utf-8", errors="replace")
                files_manifest.append(f"{rel}|bytes={p.stat().st_size}|sha256={sha256_text(data)}")
            except Exception as e:
                files_manifest.append(f"{rel}|READ_ERROR:{e}")
        else:
            files_manifest.append(f"{rel}|UNKNOWN")

    content = []
    content.append("# SAFE_RUNTIME_SNAPSHOT")
    content.append(f"generated_at_utc: {datetime.now(timezone.utc).isoformat()}")
    content.append(f"git_branch: {git_branch}")
    content.append(f"git_head_short: {git_head}")
    content.append(f"git_head_full: {git_full}")
    content.append("")
    content.append("## SERVICES")
    content.extend(f"- {x}" for x in services)
    content.append("")
    content.append("## CORE_DB_STATE_COUNTS")
    content.extend(f"- {x}" for x in db_state)
    content.append(f"- {open_tasks}")
    content.append("")
    content.append("## LATEST_TASKS_SAFE")
    content.extend(f"- {x}" for x in latest_tasks)
    content.append("")
    content.append("## MEMORY_DB_COUNTS")
    content.append(f"- {memory_rows}")
    content.append("")
    content.append("## LATEST_MEMORY_SAFE")
    content.extend(f"- {x}" for x in memory_latest)
    content.append("")
    content.append("## SEARCH_SESSIONS")
    content.extend(f"- {x}" for x in search_sessions)
    content.append("")
    content.append("## TIMELINE_INFO")
    content.extend(f"- {x}" for x in timeline_info)
    content.append("")
    content.append("## GIT_STATUS_SAFE")
    content.append(git_status if git_status else "clean")
    content.append("")
    content.append("## FILES_MANIFEST_SAFE")
    content.extend(f"- {x}" for x in files_manifest)
    content.append("")
    content.append(collect_code_markers())

    SNAPSHOT.write_text("\n".join(content).rstrip() + "\n", encoding="utf-8")


def build_protocol_block() -> str:
    return f"""# CLAUDE_OPERATING_PROTOCOL_CANON_LOCK_V3

CRITICAL:
This file is the mandatory single bootstrap context for Claude / external LLM work on AREAL-NEVA ORCHESTRA

RAW_URL:
{RAW_URL}

IF THIS FILE IS NOT READ:
Answer only:
CLAUDE_BOOTSTRAP_CONTEXT_UNAVAILABLE

FACT SOURCE ORDER:
1. Current user message and provided terminal output
2. This CLAUDE_BOOTSTRAP_CONTEXT
3. GitHub SSOT files listed in SOURCE_INDEX
4. Live diagnostics/logs/code snippets explicitly provided by user
5. UNKNOWN

FORBIDDEN:
- inventing facts
- relying on old chat memory if bootstrap contradicts it
- answering from general memory when GitHub SSOT is required
- changing architecture without explicit user command
- touching secrets, .env, credentials, token files, sessions
- modifying files outside allowed task scope
- declaring DONE without verification
- mixing topic memory
- treating topic_0 as a project topic
- creating broad rewrites when a surgical patch is required

MANDATORY PATCH ORDER:
1. DIAGNOSTICS
2. BACKUP
3. PATCH
4. PY_COMPILE
5. RESTART
6. LOGS
7. DB VERIFY
8. GIT STATUS
9. COMMIT/PUSH
10. FINAL VERIFY

MANDATORY FINAL VERIFY FOR SYSTEM CHANGES:
- syntax OK
- services active
- no fatal logs
- DB open task count checked
- memory write checked if memory was touched
- Git push OK
- context_aggregator.py still tracked
- no secrets committed

CANON LOCK:
Claude must treat this file as session memory, project memory, and operational contract
Claude must not say it cannot remember if this file is available
Claude must reload this file at start of each new session
"""


def build_bootstrap() -> str:
    SESSION_START.write_text(build_claude_session_start_prompt(), encoding="utf-8")
    write_safe_runtime_snapshot()

    generated_at = datetime.now(timezone.utc).isoformat()
    git_sha = sh(["git", "rev-parse", "HEAD"])
    git_branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])

    source_files = []
    for rel in STRICT_SOURCE_FILES:
        if rel not in source_files:
            source_files.append(rel)

    lines = []
    lines.append("# CLAUDE_BOOTSTRAP_CONTEXT")
    lines.append("")
    lines.append("SYSTEM: AREAL-NEVA ORCHESTRA")
    lines.append("MODE: FACT_ONLY / ZERO_ASSUMPTIONS / GITHUB_SSOT / CANON_LOCK")
    lines.append("PURPOSE: one-file bootstrap for Claude and external LLMs")
    lines.append(f"GENERATED_AT_UTC: {generated_at}")
    lines.append(f"GIT_BRANCH: {git_branch}")
    lines.append(f"GIT_SHA: {git_sha}")
    lines.append(f"RAW_URL: {RAW_URL}")
    lines.append("")
    lines.append(build_protocol_block().rstrip())
    lines.append("")
    lines.append("SOURCE_INDEX:")
    for rel in source_files:
        data = safe_read(rel)
        lines.append(f"- {rel} | bytes={len(data.encode('utf-8'))} | sha256={sha256_text(data)}")
    lines.append("")

    for rel in source_files:
        data = safe_read(rel)
        lines.append("")
        lines.append("=" * 120)
        lines.append(f"BEGIN_FILE: {rel}")
        lines.append("=" * 120)
        lines.append(data.rstrip())
        lines.append("=" * 120)
        lines.append(f"END_FILE: {rel}")
        lines.append("=" * 120)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_if_changed(path: Path, content: str) -> bool:
    old = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    if old == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def protect_context_aggregator() -> None:
    tracked = sh(["git", "ls-files", "tools/context_aggregator.py"])
    if not tracked.strip():
        raise RuntimeError("CONTEXT_AGGREGATOR_NOT_TRACKED")
    if not (BASE / "tools/context_aggregator.py").exists():
        sh(["git", "restore", "tools/context_aggregator.py"], check=True)
    if not (BASE / "tools/context_aggregator.py").exists():
        raise RuntimeError("CONTEXT_AGGREGATOR_RESTORE_FAILED")


def git_commit_push(changed: bool) -> None:
    protect_context_aggregator()

    if not changed:
        print("NO_CHANGE")
        return

    sh([
        "git",
        "add",
        "docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md",
        "docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md",
        "docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md",
        "tools/claude_bootstrap_aggregator.py",
    ])

    protect_context_aggregator()

    status = sh(["git", "status", "--short"])
    print(status)

    if "D tools/context_aggregator.py" in status:
        raise RuntimeError("REFUSE_COMMIT_CONTEXT_AGGREGATOR_DELETED")

    if not status.strip():
        print("NO_GIT_CHANGE")
        return

    commit = subprocess.run(
        ["git", "commit", "-m", "CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh"],
        cwd=str(BASE),
        text=True,
        capture_output=True,
    )
    print(commit.stdout.strip())
    if commit.returncode != 0 and "nothing to commit" not in (commit.stdout + commit.stderr):
        raise RuntimeError(commit.stderr)

    protect_context_aggregator()

    push = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE), text=True, capture_output=True)
    print(push.stdout.strip())
    print(push.stderr.strip())
    if push.returncode != 0:
        raise RuntimeError(push.stderr)

    print("GIT_PUSH_OK")


def main() -> None:
    print("CLAUDE_BOOTSTRAP_AGGREGATOR_CANON_LOCK_V3_START")
    protect_context_aggregator()
    subprocess.run(["rm", "-rf", "CANON_FINAL"], cwd=str(BASE))

    content = build_bootstrap()
    changed = write_if_changed(OUTPUT, content)

    print(f"OUTPUT={OUTPUT}")
    print(f"SIZE_BYTES={len(content.encode('utf-8'))}")
    print(f"SHA256={sha256_text(content)}")

    git_commit_push(changed)

    print(f"RAW_URL={RAW_URL}")
    print("CLAUDE_BOOTSTRAP_AGGREGATOR_CANON_LOCK_V3_DONE")


if __name__ == "__main__":
    main()
# === END CLAUDE_BOOTSTRAP_AGGREGATOR_CANON_LOCK_V3 ===
