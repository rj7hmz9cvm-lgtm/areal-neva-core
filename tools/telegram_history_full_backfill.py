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
