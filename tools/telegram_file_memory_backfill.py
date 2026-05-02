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
