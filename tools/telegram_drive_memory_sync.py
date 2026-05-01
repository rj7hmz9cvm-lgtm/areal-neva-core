#!/usr/bin/env python3
# === TELEGRAM_DRIVE_MEMORY_SYNC_V2 ===
from __future__ import annotations

import json
import os
import sqlite3
import hashlib
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
CORE_DB = BASE / "data/core.db"
MEM_DB = BASE / "data/memory.db"

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
                "file_id": data.get("file_id") or "",
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
