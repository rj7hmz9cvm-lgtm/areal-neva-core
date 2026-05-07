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
