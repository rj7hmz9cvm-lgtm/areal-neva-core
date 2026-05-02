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
