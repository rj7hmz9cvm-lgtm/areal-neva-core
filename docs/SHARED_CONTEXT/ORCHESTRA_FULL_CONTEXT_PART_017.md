# ORCHESTRA_FULL_CONTEXT_PART_017
generated_at_utc: 2026-07-07T14:53:44.038424+00:00
git_sha_before_commit: 0b8459136a6a71207c4423ae32667c252376df29
part: 17/21


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

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/NORMATIVE_ENGINE_SHARED_CONTEXT.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 9011f21b0b01ee1ac4003c659691ab5e1f7cae2cdde825f9eb706352568f28a0
====================================================================================================
{
  "version": "NORMATIVE_ENGINE_SHARED_CONTEXT_V2",
  "updated_at": "2026-05-05",
  "status": "VERIFIED_FROM_CODE",
  "git_head": "73b4946",
  "sources": {
    "normative_engine": "core/normative_engine.py",
    "norms_map": "core/project_engine.py NORMS_MAP lines 39-45"
  },

  "normative_engine_committed": {
    "total_entries": 59,
    "blocks": {
      "NORMATIVE_ENGINE_SAFE_V1": 8,
      "P6H_NORMATIVE_INDEX_EXTRA_V1": 10,
      "P6H5_NORMATIVE_FULL_EXPAND_V1": 36,
      "P6H6_LOADS_V1": 5
    },
    "smoke_test": "11/11 PASS at commit 73b4946",
    "shared_topic5_topic210": [
      "СП 70.13330.2012",
      "СП 63.13330.2018",
      "СП 20.13330.2016/2017",
      "СП 16.13330.2017",
      "СП 17.13330.2017"
    ],
    "primarily_topic5": [
      "СП 28.13330.2017",
      "ГОСТ 23118-2019",
      "СП 48.13330.2019",
      "СП 13-102-2003",
      "ГОСТ 31937-2024",
      "ГОСТ Р ИСО 17637-2014",
      "СП 22.13330.2016"
    ],
    "primarily_topic210": [
      "ГОСТ 21.101-2020",
      "ГОСТ 21.501-2018",
      "СП 71.13330.2017"
    ],
    "p6h5_topic210_ov_vk_eom": [
      "СП 60.13330.2020", "СП 73.13330.2016", "СП 61.13330.2012",
      "СП 30.13330.2020", "СП 31.13330.2021", "СП 32.13330.2018",
      "ПУЭ (7-е изд.)", "СП 256.1325800.2016", "ГОСТ Р 50571-4-41-2022"
    ],
    "p6h6_loads_sp20": [
      "снеговые нагрузки",
      "ветровые нагрузки",
      "постоянные нагрузки",
      "временные нагрузки",
      "сочетания нагрузок"
    ]
  },

  "norms_map_committed": {
    "кж": ["СП 63.13330.2018", "ГОСТ 34028-2016", "СП 20.13330.2017"],
    "км": ["СП 16.13330.2017", "ГОСТ 27772-2015", "СП 20.13330.2017"],
    "ар": ["СП 118.13330.2022", "ГОСТ 21.501-2018"],
    "ов": ["СП 60.13330.2020", "ГОСТ 30494-2011"],
    "вк": ["СП 30.13330.2020", "СП 31.13330.2021"],
    "эом": ["СП 256.1325800.2016", "ПУЭ-7"],
    "overlap_with_normative_engine": ["СП 63.13330.2018", "СП 20.13330.2017", "СП 16.13330.2017", "ГОСТ 21.501-2018"],
    "only_in_norms_map": ["ГОСТ 34028-2016", "ГОСТ 30494-2011", "СП 118.13330.2022", "ПУЭ-7", "ГОСТ 27772-2015"]
  },

  "loads_calculation": {
    "normative_binding_status": "CLOSED",
    "normative_binding_note": "P6H6 committed — все виды нагрузок покрыты ключевыми словами СП 20",
    "calc_logic_status": "PARTIAL_CALC",
    "calc_logic_note": "calc_loads() покрывает только снег/ветер по районам",
    "committed": {
      "calc_loads_fn": "core/project_engine.py:68",
      "covers": ["snow_kPa by region (1-8)", "wind_kPa by region (1-8)"],
      "norm_reference": "СП 20.13330.2017"
    },
    "not_implemented": [
      "постоянные нагрузки (собственный вес)",
      "временные нагрузки (полезная нагрузка по назначению помещения)",
      "сочетания нагрузок",
      "проверка предельных состояний"
    ]
  },

  "open_items": {
    "calc_logic": "PARTIAL_CALC — автоматический расчёт постоянных/временных/сочетаний не реализован",
    "topic5_live_test": "NOT_DONE — фото/буфер/разбор через реальный Telegram не пройден",
    "document_output_live": "NOT_DONE — PDF/DOCX/Drive link/fallback не подтверждены живым тестом",
    "topic210_live": "NOT_DONE — ОВ/ВК/ЭОМ/КЖ/КМ через реальные файлы не прогнаны",
    "vision": "BLOCKED — EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False, owner decision required",
    "missing_in_norms_map": ["сс", "гп", "пз", "см", "тх"]
  }
}

====================================================================================================
END_FILE: docs/TECHNADZOR/NORMATIVE_ENGINE_SHARED_CONTEXT.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/NORMATIVE_ENGINE_SHARED_CONTEXT.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: fbe4915ea50f48d499b50d5e242969fe82790379f9887fbfe5a08c6aff1cb1cd
====================================================================================================
# NORMATIVE ENGINE — SHARED CONTEXT (topic_5 + topic_210)

version: NORMATIVE_ENGINE_SHARED_CONTEXT_V2
updated_at: 2026-05-05
status: VERIFIED_FROM_CODE
source_1: core/normative_engine.py — git HEAD 73b4946 (P6H5+P6H6 committed)
source_2: core/project_engine.py NORMS_MAP — git HEAD 73b4946
note: Только нормы из committed кода. Не изобретать новые нормы. Не добавлять пункты.

---

## 1. Два нормативных контура

```
normative_engine.py — SHARED
  keyword-based search_norms_sync(text)
  Используется: topic_5 (технадзор) + topic_210 (проектирование)
  Committed: 59 записей (HEAD 73b4946)
    — base 8 (NORMATIVE_ENGINE_SAFE_V1)
    — P6H extension 10 (P6H_NORMATIVE_INDEX_EXTRA_V1)
    — P6H5 expansion 36 (P6H5_NORMATIVE_FULL_EXPAND_V1) ← теперь COMMITTED
    — P6H6 loads 5 (P6H6_LOADS_V1) ← теперь COMMITTED

project_engine.py NORMS_MAP — topic_210 ONLY
  section-based NORMS_MAP[section] → list of norm_ids
  Используется: topic_210 — АР / КЖ / КМ / ОВ / ВК / ЭОМ
  Committed: 6 разделов (HEAD 2deb7c8)
```

---

## 2. normative_engine.py — committed 18 записей

### 2.1 Общие (topic_5 + topic_210)

| norm_id | Раздел | topic_5 | topic_210 |
|---|---|---|---|
| СП 70.13330.2012 | Несущие и ограждающие конструкции | акты: бетон, трещины | КЖ: несущая способность |
| СП 63.13330.2018 | Бетонные и железобетонные конструкции | акты: ЖБ дефекты | КЖ: армирование, защитный слой |
| СП 20.13330.2016/2017 | Нагрузки и воздействия | акты: основания, перекрытия | КЖ/КМ: расчётные нагрузки |
| СП 16.13330.2017 | Стальные конструкции | акты: сварка, связи, узлы | КМ: металлокаркас |
| СП 17.13330.2017 | Кровли | акты: протечки, примыкания | АР: кровельные решения |

### 2.2 Преимущественно topic_5

| norm_id | Раздел |
|---|---|
| СП 28.13330.2017 | Защита строительных конструкций от коррозии |
| ГОСТ 23118-2019 | Конструкции стальные строительные. Общие ТУ |
| СП 48.13330.2019 | Организация строительства (стройконтроль) |
| СП 13-102-2003 | Обследование несущих строительных конструкций |
| ГОСТ 31937-2024 | Обследование и мониторинг технического состояния |
| ГОСТ Р ИСО 17637-2014 | Визуальный контроль сварных соединений |
| СП 22.13330.2016 | Основания зданий и сооружений |
| СП 70.13330.2012 *(2-я запись)* | Опорные узлы металлоконструкций |
| СП 16.13330.2017 *(2-я запись)* | Пространственные связи |
| СП 20.13330.2016 *(2-я запись)* | Нагрузки — перекрытия |

### 2.3 Преимущественно topic_210

| norm_id | Раздел |
|---|---|
| ГОСТ 21.101-2020 | Основные требования к проектной и рабочей документации |
| ГОСТ 21.501-2018 | Рабочая документация АР и КР |
| СП 71.13330.2017 | Изоляционные и отделочные покрытия |

---

## 3. project_engine.py NORMS_MAP — topic_210, 6 разделов

Источник: `core/project_engine.py`, строки 39–45, HEAD 2deb7c8.

```python
NORMS_MAP = {
    "кж":  ["СП 63.13330.2018", "ГОСТ 34028-2016", "СП 20.13330.2017"],
    "км":  ["СП 16.13330.2017", "ГОСТ 27772-2015", "СП 20.13330.2017"],
    "ар":  ["СП 118.13330.2022", "ГОСТ 21.501-2018"],
    "ов":  ["СП 60.13330.2020", "ГОСТ 30494-2011"],
    "вк":  ["СП 30.13330.2020", "СП 31.13330.2021"],
    "эом": ["СП 256.1325800.2016", "ПУЭ-7"],
}
```

NORMS_MAP частично пересекается с normative_engine.py (committed):
- СП 63.13330.2018 — в NORMS_MAP["кж"] и в normative_engine base
- СП 20.13330.2017 — в NORMS_MAP["кж","км"] и в normative_engine ("СП 20.13330.2016/2017")
- СП 16.13330.2017 — в NORMS_MAP["км"] и в normative_engine base
- ГОСТ 21.501-2018 — в NORMS_MAP["ар"] и в normative_engine base

Только в NORMS_MAP (не в normative_engine committed):
- ГОСТ 34028-2016 — прокат арматурный (КЖ)
- ГОСТ 30494-2011 — параметры микроклимата (ОВ)
- СП 118.13330.2022 — общественные здания (АР)
- ПУЭ-7 — электроустановки (ЭОМ)
- ГОСТ 27772-2015 — прокат стальной (КМ)

---

## 4. Расчёт нагрузок и несущей способности — PARTIAL

### Что есть в committed коде

`core/project_engine.py` — `calc_loads(region)`, строки 68–73:
```python
{"snow_kPa": ..., "wind_kPa": ..., "region": region, "note": "СП 20.13330.2017 — район N"}
```

Закрыто только:
- снеговая нагрузка по 8 районам (SNOW_LOADS)
- ветровая нагрузка по 8 районам (WIND_LOADS)
- нормативная привязка: СП 20.13330.2017

Нормативные документы в committed движке (оба контура):
- СП 20.13330.2016/2017 — нагрузки и воздействия (normative_engine)
- СП 16.13330.2017 — стальные конструкции (normative_engine + NORMS_MAP КМ)
- СП 63.13330.2018 — ЖБ конструкции (normative_engine + NORMS_MAP КЖ)
- СП 22.13330.2016 — основания (normative_engine)

### Что НЕ закрыто

```
FULL расчёт несущей способности: НЕ ЗАКРЫТ

Отсутствует в committed коде:
- постоянные нагрузки (собственный вес конструкций)
- временные нагрузки (полезная нагрузка на перекрытия по назначению)
- особые нагрузки (сейсмика, взрыв, обрушение)
- крановые нагрузки
- нагрузки на фундаменты от надземных конструкций
- расчёт сечений элементов по нормативным требованиям
- проверка предельных состояний (1-я группа, 2-я группа)
```

### Что необходимо добавить (в оба направления)

**topic_5 (ТЕХНАДЗОР):**
Нормы ветровых и снеговых нагрузок нужны при проверке несущих конструкций в актах осмотра:
- установить соответствие пролётов, прогонов, связей расчётным нагрузкам
- фиксировать нагрузочный класс объекта при документировании дефектов несущих элементов

**topic_210 (ПРОЕКТИРОВАНИЕ):**
Для полноценного разбора КЖ/КМ разделов проектной документации:
- нормативная привязка по видам нагрузок (не только снег/ветер)
- расчётные сочетания нагрузок
- классы ответственности и коэффициенты надёжности

Статус: `PARTIAL — базовая нормативная привязка закрыта; полный расчётный контур не реализован`

---

## 5. P6H5 + P6H6 — COMMITTED (73b4946)

`core/normative_engine.py` — оба блока зафиксированы в коммите 73b4946.
Статус: `COMMITTED`

**P6H5_NORMATIVE_FULL_EXPAND_V1** (36 норм):
- ИД / журналы: РД-11-02-2006, РД-11-05-2007, СП 11-110-99
- Бетонные смеси: ГОСТ 7473-2010, ГОСТ 18105-2018, ГОСТ 26633-2015
- Газобетон / кладка: ГОСТ 31360-2007, СП 339.1325800.2017, СП 15.13330.2020
- КМ: СП 294.1325800.2017, ГОСТ 27772-2015, СП 260.1325800.2016
- ГКЛ: СП 163.1325800.2014, ГОСТ 6266-2018
- Фасады / окна: СП 50.13330.2012, СП 293.1325800.2017, ГОСТ 30674-99
- ОВ: СП 60.13330.2020, СП 73.13330.2016, СП 61.13330.2012
- ВК: СП 30.13330.2020, СП 31.13330.2021, СП 32.13330.2018
- ЭОМ: ПУЭ (7-е изд.), СП 256.1325800.2016, ГОСТ Р 50571-4-41-2022
- Пожарная безопасность: 123-ФЗ, СП 1.13130.2020, СП 2.13130.2020
- Охрана труда: СНиП 12-03-2001, СНиП 12-04-2002, Приказ №336н/№883н, ГОСТ 12.0.004-2015, ГОСТ 12.4.011-89, СП 49.13330.2010

**P6H6_LOADS_V1** (5 записей — СП 20.13330.2017):
снеговые, ветровые, постоянные, временные, сочетания нагрузок

P6H5 частично дублирует NORMS_MAP (ОВ, ВК, ЭОМ) — оба источника теперь committed.
smoke 11/11 PASS при commit.

---

## 6. Правила использования нормативного контура

```
1. topic_5 (ТЕХНАДЗОР):
   - Использовать search_norms_sync() из normative_engine.py
   - NORMS_MAP не применяется
   - Если норма не найдена → "норма не подтверждена"

2. topic_210 (ПРОЕКТИРОВАНИЕ):
   - Раздел: detect_section() → NORMS_MAP[section]
   - normative_engine дополнительно для текстового поиска
   - Нельзя смешивать нормы разных разделов

3. Общий запрет:
   - Не изобретать новые СП/ГОСТ
   - Не придумывать пункты нормативов
   - Confidence=PARTIAL у всех committed записей

4. Нагрузки:
   - Нормативная привязка по всем видам нагрузок: ЗАКРЫТА (P6H6, СП 20)
   - calc_loads() в project_engine: только снег/ветер по районам
   - Автоматический расчёт постоянных/временных/сочетаний нагрузок: НЕ РЕАЛИЗОВАН
   - Статус: PARTIAL_CALC — нормы есть, расчётная логика отсутствует
```

---

## 7. Верификация с каноном

Canon `TECHNADZOR_DOMAIN_LOGIC_CANON.md`, §22:
```
СП 16, СП 70, СП 28, ГОСТ 23118, СП 48, СП 13-102, ГОСТ 31937, СП 63, СП 22
```
Все 9 норм присутствуют в committed normative_engine.py. ✓

Canon `01_SYSTEM_LOGIC_FULL.md`:
```
topic_210: КЖ / КМ / КМД / АР / ОВ / ВК / ЭОМ / СС / ГП / ПЗ / СМ / ТХ
```
- ОВ / ВК / ЭОМ — committed нормы в project_engine.py NORMS_MAP. ✓
- СС / ГП / ПЗ / СМ / ТХ — в NORMS_MAP отсутствуют. NOT_PRESENT.

====================================================================================================
END_FILE: docs/TECHNADZOR/NORMATIVE_ENGINE_SHARED_CONTEXT.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 557b97c8c932bb7c5228ff7049330426530dca78340f4cddab5435c59e290633
====================================================================================================
{
  "version": "TOPIC5_DOCUMENT_OUTPUT_CONTRACT_V1",
  "updated_at": "2026-05-05",
  "status": "CODE_AUDIT_DRAFT_NOT_LIVE_VERIFIED",
  "source": "technadzor_engine.py audit + owner addendum 2026-05-05",

  "output_types": [
    {"type": "TEXT_REPORT", "status": "ACTIVE", "note": "рабочий путь"},
    {"type": "PDF_ACT", "status": "NOT_IMPLEMENTED", "note": "local-check 2026-05-05: ModuleNotFoundError reportlab"},
    {"type": "DOCX", "status": "NOT_IMPLEMENTED", "note": "local-check 2026-05-05: ModuleNotFoundError python-docx"},
    {"type": "XLSX", "status": "UNVERIFIED"},
    {"type": "GOOGLE_DOC", "status": "FUTURE_OPTIONAL_NOT_VERIFIED"},
    {"type": "TELEGRAM_ONLY", "status": "ACTIVE", "note": "нет файла, только текст"}
  ],

  "document_statuses": [
    "TELEGRAM_TEXT_REPORT_SENT",
    "LOCAL_DRAFT_CREATED",
    "DOCX_DRAFT_CREATED",
    "PDF_GENERATION_NOT_IMPLEMENTED",
    "DRIVE_UPLOAD_PENDING",
    "DRIVE_UPLOAD_DONE",
    "DRIVE_UPLOAD_FAILED",
    "TELEGRAM_LINK_SENT",
    "FALLBACK_SENT",
    "CLIENT_DOCUMENT_DELIVERED"
  ],

  "done_rule": {
    "done": "CLIENT_DOCUMENT_DELIVERED",
    "not_done": [
      "LOCAL_DRAFT_CREATED",
      "DOCX_DRAFT_CREATED",
      "DRIVE_UPLOAD_DONE without TELEGRAM_LINK_SENT"
    ],
    "conditions": [
      "Document exists (PDF / DOCX / TEXT)",
      "Uploaded to Drive (PDF/DOCX) OR text sent to Telegram (TEXT)",
      "Owner/client received link or text in Telegram"
    ]
  },

  "forbidden_patterns": [
    "calling LOCAL_DRAFT_CREATED done",
    "calling DOCX_DRAFT_CREATED done without Drive upload and Telegram link",
    "claiming PDF generated without reportlab local-check",
    "Drive upload without Telegram confirmation",
    "sending /root/... path to client",
    "placing DOCX in client_facing without explicit owner command"
  ],

  "delivery_chain": {
    "entry": "task_worker._handle_in_progress",
    "process": "process_technadzor (wrapper chain, 8 definitions)",
    "build": "_p6h_build_* (text / docx / pdf)",
    "drive_upload_fn": "technadzor_drive_index.upload_client_pdf_to_folder",
    "drive_upload_fn_line": 383,
    "drive_upload_fn_verified": true,
    "fallback": "FALLBACK_SENT + error status in ObjectCard"
  },

  "packages_local_check_20260505": {
    "reportlab": "NOT_INSTALLED",
    "python_docx": "NOT_INSTALLED",
    "dejavu_fonts": "PRESENT"
  },

  "file_naming": {
    "docx_draft": "Черновик_акта_<объект>_<дата>.docx",
    "pdf_final": "Акт_осмотра_<объект>_<дата>.pdf",
    "xlsx_registry": "Реестр_замечаний_<объект>_<дата>.xlsx",
    "date_format": "YYYYMMDD",
    "object_name": "Russian name from ObjectCard"
  },

  "drive_placement": {
    "client_facing_folder": "финальный PDF; DOCX только по явной команде владельца",
    "topic5_system_folder": "служебные файлы, черновики, JSON манифесты",
    "forbidden": "путь /root/... клиенту"
  }
}

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: edff2931c8896b02651a0175466d81c5659f3ebc155ccfa5f9a60b6ddc44480d
====================================================================================================
# TOPIC5 DOCUMENT OUTPUT CONTRACT

version: TOPIC5_DOCUMENT_OUTPUT_CONTRACT_V1
updated_at: 2026-05-05
status: CODE_AUDIT_DRAFT_NOT_LIVE_VERIFIED
source: technadzor_engine.py audit + owner addendum 2026-05-05

---

## 1. Типы выходных документов

| Тип | Константа | Статус |
|---|---|---|
| Текстовый разбор | TEXT_REPORT | ACTIVE — рабочий путь |
| PDF акт | PDF_ACT | NOT_IMPLEMENTED — local-check 2026-05-05: ModuleNotFoundError |
| DOCX черновик | DOCX | NOT_IMPLEMENTED — local-check 2026-05-05: ModuleNotFoundError |
| XLSX реестр | XLSX | UNVERIFIED |
| Google Doc | GOOGLE_DOC | FUTURE_OPTIONAL_NOT_VERIFIED |
| Только Telegram | TELEGRAM_ONLY | ACTIVE — нет файла, только текст |

---

## 2. Статусы документа

```
TELEGRAM_TEXT_REPORT_SENT   — текстовый разбор отправлен в Telegram
LOCAL_DRAFT_CREATED         — черновик создан локально (НЕ ДОСТАВЛЕН клиенту)
DOCX_DRAFT_CREATED          — DOCX создан локально (НЕ ДОСТАВЛЕН клиенту)
PDF_GENERATION_NOT_IMPLEMENTED — reportlab не установлен: ModuleNotFoundError
DRIVE_UPLOAD_PENDING        — ожидает загрузки на Drive
DRIVE_UPLOAD_DONE           — загружен на Drive
DRIVE_UPLOAD_FAILED         — ошибка загрузки на Drive
TELEGRAM_LINK_SENT          — ссылка на Drive отправлена в Telegram
FALLBACK_SENT               — текстовый fallback вместо файла
CLIENT_DOCUMENT_DELIVERED   — документ доставлен: Drive + Telegram ссылка получена
```

---

## 3. Правило DONE

```
CLIENT_DOCUMENT_DELIVERED = задача выполнена
LOCAL_DRAFT_CREATED        ≠ задача выполнена
DOCX_DRAFT_CREATED         ≠ задача выполнена
DRIVE_UPLOAD_DONE без Telegram ссылки ≠ задача выполнена

Закрыто только когда:
  1. Документ существует (PDF / DOCX / TEXT)
  2. Загружен на Drive (PDF/DOCX) ИЛИ текст отправлен в Telegram (TEXT)
  3. Владелец/клиент получил ссылку или текст в Telegram
```

---

## 4. Запрещённые паттерны

- Называть LOCAL_DRAFT_CREATED «готово» или «документ создан»
- Называть DOCX_DRAFT_CREATED «акт готов» без Drive-загрузки и Telegram-ссылки
- Сообщать «PDF сгенерирован» без фактической проверки reportlab
- Загружать на Drive без подтверждения ссылки в Telegram
- Отправлять клиенту путь вида /root/...
- Помещать DOCX в client_facing папку без явной команды владельца

---

## 5. Цепочка доставки

```
Telegram (владелец)
  → task_worker._handle_in_progress
  → process_technadzor (wrapper chain, 8 definitions)
  → VisitPackage собран
  → _p6h_build_* (text / docx / pdf builder)
  → technadzor_drive_index.upload_client_pdf_to_folder (line 383, verified)
  → Telegram ответ со ссылкой
```

Если любой шаг падает → FALLBACK_SENT + статус ошибки в ObjectCard.

---

## 6. Статус пакетов (local-check 2026-05-05)

```
reportlab:    ModuleNotFoundError — не установлен
python-docx:  ModuleNotFoundError — не установлен
DejaVu fonts: присутствуют (/usr/share/fonts/truetype/dejavu/)

Код _p6h_build_pdf_act / _p6h_build_docx_act существует в technadzor_engine.py
но упадёт на import при вызове.

Текущий рабочий путь: TEXT_REPORT → Telegram text
```

---

## 7. Именование файлов

```
Черновик DOCX:  Черновик_акта_<объект>_<дата>.docx
Финальный PDF:  Акт_осмотра_<объект>_<дата>.pdf
Реестр XLSX:    Реестр_замечаний_<объект>_<дата>.xlsx
```

Дата формат: YYYYMMDD.
Объект: имя из ObjectCard на русском для клиентских файлов.

---

## 8. Drive placement

```
client_facing=True папка → финальный PDF акт
                           DOCX — только по явной команде владельца
topic_5 system folder    → служебные файлы, черновики, JSON манифесты
Путь /root/...           → НИКОГДА не отправлять клиенту
```

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_RUNTIME_USAGE_RULES.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 4093ded0ac87b42cc50beb5578095a4ae85e9bc4ec5ec7f5ddb5ead599618fa3
====================================================================================================
# TOPIC5 RUNTIME USAGE RULES

version: TOPIC5_RUNTIME_USAGE_RULES_V1
updated_at: 2026-05-05
status: CODE_AUDIT_VERIFIED

---

## 1. Что можно трогать / что нельзя

### Запрещено редактировать напрямую
```
task_worker.py           — overlay chain (_handle_in_progress 14 definitions)
telegram_daemon.py       — Telegram polling loop
ai_router.py             — routing logic
reply_sender.py          — delivery chain
google_io.py             — Drive OAuth
normative_engine.py      — dirty (+283 lines P6H5 expansion), не stage, не commit
.env / credentials.json  — секреты
token.json / *.session   — OAuth токены
data/core.db             — рабочая БД
data/memory.db           — memory БД
```

### Разрешено
```
docs/**                  — документация (append или новые файлы)
core/technadzor_engine.py — только append к концу файла (monkeypatch pattern)
core/normative_engine.py  — только append к концу файла (если явно разрешено)
```

---

## 2. Append-only rule

Все изменения кода в `/root/.areal-neva-core` — только дописывание к концу файла.
Это соответствует существующему паттерну wrapper/monkeypatch-цепочек.

Нельзя: редактировать существующие функции в середине файла.
Можно: добавить новую обёртку в конец, которая вызывает предыдущую версию.

---

## 3. Перед любым патчем

1. Прочитать `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md`
2. Прочитать `HANDOFFS/LATEST_HANDOFF.md`
3. Убедиться что normative_engine.py не попадает в staged

---

## 4. Активное состояние системы (2026-05-05)

```
ActiveTechnadzorFolder:
  object: тест надзор
  folder_id: 1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG
  status: OPEN
  verified: true (task 5276 DONE)

process_technadzor wrapper chain:
  _p6h4tw_v1_wrapped = True
  P6H4FD → P6H4TW → ... (8 definitions)

Vision guard:
  EXTERNAL_PHOTO_ANALYSIS_ALLOWED = False
  OpenRouter Google: 403 при попытке включить

SearchMonolithV2:
  model: perplexity/sonar (via OpenRouter)
  OPENROUTER_API_KEY: confirmed in .env
  HTTP: real calls via urllib
```

---

## 5. Изоляция объектов

- Дефекты KIEVSKOE_95 → только KIEVSKOE_95
- Дефекты NOVICHKOVO → только NOVICHKOVO
- Дефекты SUSANINO → только SUSANINO
- Нельзя переносить замечания между объектами
- Нельзя применять металлокаркасные нормы к каркасному дому без проверки

---

## 6. Перед git push

```bash
mv core/context_aggregator.py /tmp/context_aggregator_backup.py
# ... push ...
mv /tmp/context_aggregator_backup.py core/context_aggregator.py
```

Это обязательный шаг перед каждым push.

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_RUNTIME_USAGE_RULES.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e3bf441983629d033eb5d781360ea364c905fd229134d0ec3f2ed943a9080fa4
====================================================================================================
{
  "version": "TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL_V1",
  "updated_at": "2026-05-05",
  "status": "FINAL_DOCUMENTED",
  "topic": "topic_5",
  "topic_name": "ТЕХНАДЗОР",
  "main_principle": "Drive folder = work container. Telegram = owner explanation + control. Files = materials (not tasks). 61 photos = one visit = one act.",
  "task_components": [
    "OwnerInstruction",
    "InputFiles",
    "ActiveFolder",
    "ObjectContext",
    "PreviousActs"
  ],
  "material_paths": {
    "PATH_A": "Drive folder → owner Telegram explanation → ActiveTechnadzorFolder → VisitPackage → one result",
    "PATH_B": "Telegram files + voice → VisitBuffer → owner explanation → VisitPackage → one result"
  },
  "task_lifecycle": [
    "owner creates/selects Drive folder",
    "Оркестр opens ActiveTechnadzorFolder",
    "owner uploads materials + explains via voice/text",
    "Оркестр collects VisitMaterials (COLLECTING_VISIT_MATERIALS)",
    "owner commands 'сделай разбор/акт/документ'",
    "Оркестр assembles VisitPackage",
    "ObjectContext loaded (history, previous acts)",
    "Norms matched via normative_engine",
    "One result output: text report / PDF / DOCX / XLSX",
    "ObjectCard updated",
    "Drive upload: final document only to topic folder"
  ],
  "drive_facts": {
    "технадзор_root_id": "1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD",
    "технадзор_root_url": "https://drive.google.com/drive/folders/1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD",
    "topic_5_folder_id": "1yWIJdSrypH3BbIozCz-OAw1R6hmnMRHK",
    "technadzor_system_id": "1vKQM0Z2qBmiKtgeyx95JaNEQAp5mJLOm",
    "known_user_folders": [
      "Сусанино. Технадзор",
      "КП _Новичково_ Александр",
      "Выезд ангар Киевское ш",
      "Документы личные работа НЕ ОРКЕСТР",
      "тест надзор"
    ]
  },
  "system_folder_blacklist": [
    "TECHNADZOR",
    "ТЕХНАДЗОР",
    "topic_5",
    "_system",
    "_tmp",
    "_archive",
    "_drafts",
    "_templates",
    "_manifests"
  ],
  "active_folder_state_file": "data/technadzor/active_folder_{chat_id}_{topic_id}.json",
  "visit_buffer_file": "data/technadzor/buf_{chat_id}_{topic_id}.json",
  "current_active_folder": {
    "folder_id": "1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG",
    "folder_name": "тест надзор",
    "status": "TEST_ACTIVE_FOLDER",
    "verified_task": "rowid_5276_DONE"
  },
  "remark_statuses": [
    "новое замечание",
    "подтверждено по фото",
    "частично видно по фото",
    "устранено",
    "устранено частично",
    "не устранено",
    "требует доведения",
    "не проверялось на текущем выезде",
    "требует уточнения"
  ],
  "base_sections": [
    "опорные узлы",
    "сварные соединения",
    "антикоррозионная защита",
    "основание и водоотведение",
    "крепления и узлы покрытия",
    "связи / укосины / элементы жёсткости",
    "бетонные и железобетонные конструкции",
    "кровля / фасад / ограждающие конструкции",
    "прочие замечания"
  ],
  "output_formats": ["PDF", "DOCX", "GoogleDocs", "TelegramText", "XLSX", "Appendix"],
  "language_rules": {
    "client_and_owner_output": "Russian only",
    "code_internal": "English"
  },
  "vision_status": {
    "EXTERNAL_PHOTO_ANALYSIS_ALLOWED": false,
    "status": "VISION_BLOCKED_OWNER_DECISION_REQUIRED",
    "reason": "OpenRouter Google 403 + no other Vision model authorized",
    "fallback": "owner voice/text + previous acts + filenames/metadata"
  },
  "code_status": {
    "visit_buffer": "VERIFIED",
    "active_folder": "VERIFIED",
    "folder_discovery": "LIVE_CLOSED_task5276",
    "drive_batch_trigger": "INSTALLED_P6H4TW_BATCH_TRIGGER_V1",
    "stt_hallucination_guard": "INSTALLED",
    "vision_guard": "INSTALLED_EXTERNAL_PHOTO_ANALYSIS_ALLOWED_FALSE"
  }
}

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 59b575c0ccca40bac5fb41a2907fc7d2801f4032826805668f594db34284d49c
====================================================================================================
# TOPIC5 TECHNADZOR — SYSTEM LOGIC FINAL

version: TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL_V1
updated_at: 2026-05-05
status: FINAL_DOCUMENTED
topic: topic_5 / ТЕХНАДЗОР
references:
  canon: docs/CANON_FINAL/TECHNADZOR_DOMAIN_LOGIC_CANON.md
  unified_context: docs/TECHNADZOR/unified_context/TOPIC5_UNIFIED_TECHNADZOR_CONTEXT.md

---

## 1. Главный принцип

```
Google Drive папка = контейнер работы
Telegram topic_5   = пояснение владельца и управление задачей
Файлы              = материалы (не задачи)
Голос/текст владельца = техническое ТЗ + привязка замечаний
Оркестр            = связывает файлы, пояснения, объект, нормы, историю
Финал              = один разбор или один документ по всей задаче
```

Файл сам по себе — не задача.
61 фото = один выезд = один акт.
Никаких задач на каждое фото.

---

## 2. Составные части TechnadzorTask

```
TechnadzorTask =
  OwnerInstruction (голос или текст владельца)
  + InputFiles     (фото / PDF / DOCX из Drive или Telegram)
  + ActiveFolder   (текущая рабочая Drive-папка)
  + ObjectContext  (ObjectCard — история объекта)
  + PreviousActs   (предыдущие акты если есть)
```

---

## 3. Два пути передачи материалов

### Путь A — Drive (предпочтительный)
1. Владелец создаёт папку на Drive в ТЕХНАДЗОР root
2. Загружает фото, документы
3. В Telegram topic_5 поясняет: объект, задача, что проверить
4. Оркестр принимает папку как ActiveTechnadzorFolder
5. По команде "сделай разбор/акт" — формирует один результат

### Путь B — Telegram
1. Владелец присылает фото/файлы напрямую в topic_5
2. Комментирует голосом или текстом
3. Оркестр копит в VisitBuffer
4. По команде — flush → VisitPackage → один результат

**Смешивание путей допустимо:** файлы из Drive + голос из Telegram = норма.

---

## 4. Жизненный цикл задачи topic_5

```
Владелец → папка / фото / объяснение
→ Оркестр: ActiveTechnadzorFolder открыта?
     НЕТ → "К какой папке отнести материалы?"
     ДА  → принять, связать с объектом
→ VisitMaterial создаётся (COLLECTING_VISIT_MATERIALS)
→ По команде "сделай разбор/акт/документ":
     → VisitPackage собирается
     → ObjectContext загружается (история, предыдущие акты)
     → Нормы подбираются через normative_engine
     → Один результат: текстовый разбор / PDF акт / DOCX / XLSX
→ ObjectCard обновляется
→ Drive upload (только PDF/DOCX итогового документа в topic-папку)
```

---

## 5. ActiveTechnadzorFolder

```python
ActiveTechnadzorFolder:
  chat_id:           str
  topic_id:          int = 5
  object_name:       str        # название объекта
  visit_date:        str        # дата выезда
  drive_folder_url:  str        # ссылка на Drive папку
  drive_folder_id:   str        # id папки
  folder_name:       str        # название папки как на Drive
  client_facing:     bool       # true = клиентская папка
  mode_hint:         str        # INITIAL_INSPECTION / FOLLOWUP / NEXT_INSPECTION / ...
  active_since:      str        # timestamp открытия
  last_update:       str        # timestamp последнего изменения
  owner_instructions: list[str] # инструкции владельца
  status:            str        # OPEN / FLUSHED / CLOSED
```

**Файл состояния:** `data/technadzor/active_folder_{chat_id}_{topic_id}.json`

**Системные папки — НИКОГДА не становятся ActiveTechnadzorFolder:**
- TECHNADZOR
- ТЕХНАДЗОР
- topic_5
- _system / _tmp / _archive / _drafts / _templates / _manifests

**Верифицированное Drive дерево:**
- ТЕХНАДЗОР root: `1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD`
- topic_5 system folder: `1yWIJdSrypH3BbIozCz-OAw1R6hmnMRHK`
- TECHNADZOR system: `1vKQM0Z2qBmiKtgeyx95JaNEQAp5mJLOm`

---

## 6. VisitMaterial

```python
VisitMaterial:
  material_id:          str         # uuid
  source:               str         # TELEGRAM / DRIVE
  file_type:            str         # PHOTO / VIDEO / PDF / DOCX / XLSX / TEXT / VOICE / OTHER
  file_name:            str
  drive_url:            str | None
  telegram_message_id:  int | None
  added_at:             str         # iso timestamp
  owner_comment:        str | None  # пояснение владельца
  group_label:          str | None  # "опорные узлы" / "сварные соединения" / ...
  include_in_report:    bool = True
  include_in_act:       bool = True
  defect_hint:          str | None  # краткое описание дефекта из голоса владельца
  section_hint:         str | None  # к какому разделу отнести
  status:               str         # PENDING / LINKED / EXCLUDED
```

**Буфер:** `data/technadzor/buf_{chat_id}_{topic_id}.json`

---

## 7. VisitPackage

```python
VisitPackage:
  active_folder:        ActiveTechnadzorFolder
  object_name:          str
  visit_date:           str
  previous_acts:        list[str]   # ссылки на Drive или file_id предыдущих актов
  photos:               list[VisitMaterial]
  videos:               list[VisitMaterial]
  documents:            list[VisitMaterial]
  owner_instructions:   list[str]
  client_comments:      list[str]
  contractor_comments:  list[str]
  material_groups:      dict[str, list[VisitMaterial]]  # group_label → materials
  excluded_materials:   list[VisitMaterial]
  requested_output:     str    # TEXT_REPORT / PDF_ACT / DOCX / XLSX / TELEGRAM
```

---

## 8. ObservationCard

```python
ObservationCard:
  source:             str   # OWNER_VOICE / OWNER_TEXT / PHOTO_EVIDENCE /
                            # PREVIOUS_ACT / CLIENT_TEXT / CONTRACTOR_TEXT /
                            # PROJECT_DOCUMENT / EXECUTIVE_DOCUMENT
  author:             str
  author_role:        str   # owner / client / contractor
  material_type:      str   # photo / voice / text / document
  object:             str
  date:               str
  claim:              str   # суть наблюдения
  linked_files:       list[str]
  confirmed:          str   # yes / no / partial
  contradiction:      bool
  needs_owner_question: bool
```

---

## 9. DefectCard

```python
DefectCard:
  photo_no:             int | None    # номер фото в разборе
  file_name:            str
  source:               str
  node_location:        str           # узел / место
  what_visible:         str           # что видно на фото/в материале
  defect_remark:        str           # дефект или замечание
  why_bad:              str           # почему плохо
  possible_consequences: str
  what_to_fix:          str
  what_to_check_on_site: str
  normative_reference:  str | None
  norm_status:          str           # CONFIRMED / PARTIAL / NOT_FOUND / SOURCE_MENTIONED_ONLY
  remark_status:        str           # см. список статусов замечаний
  confirmation_source:  str
  owner_question:       str | None    # вопрос к владельцу если нужен
```

---

## 10. Статусы замечаний

- новое замечание
- подтверждено по фото
- частично видно по фото
- устранено
- устранено частично
- не устранено
- требует доведения
- не проверялось на текущем выезде
- требует уточнения

---

## 11. Группировка замечаний

Группировка по смыслу, не по порядку фото.

Базовые секции:
- опорные узлы
- сварные соединения
- антикоррозионная защита
- основание и водоотведение
- крепления и узлы покрытия
- связи / укосины / элементы жёсткости
- бетонные и железобетонные конструкции
- кровля / фасад / ограждающие конструкции
- прочие замечания

Профили добавляют секции: металлокаркас / бетон / кровля / фасад / инженерные сети / электрика / отделка / каркасный дом / нагрузки.

---

## 12. Логика работы с предыдущими актами

Если предыдущие акты есть:
- не начинать с нуля
- добавить раздел "Связь с предыдущими актами"
- показать что было → что проверено → что устранено → что не устранено → что новое
- если акт не распарсить → "предыдущий акт найден, содержание требует ручной сверки"

---

## 13. Правила противоречий

| Ситуация | Формулировка |
|---|---|
| Владелец говорит одно, фото показывает другое | задать уточнение |
| Подрядчик говорит "устранено", фото не подтверждает | "устранение по представленным фото не подтверждено" |
| Предыдущий акт имел дефект, фото нет | "не проверялось на текущем выезде" |
| Только слова заказчика | "по информации заказчика, требуется проверка" |
| Только слова подрядчика | "по информации подрядчика, требуется фотофиксация результата и проверка на объекте" |

---

## 14. Нормы

- Если найден документ + пункт → цитировать документ + пункт
- Если найден только документ → цитировать документ
- Если ничего не найдено → "норма не подтверждена"
- Никогда не изобретать пункты нормативов
- Упоминание нормы в старом акте = SOURCE_MENTIONED_CLAUSE, не автоматически подтверждено

---

## 15. Форматы вывода

- PDF (приоритетный финальный формат)
- DOCX / Word (если владелец запросил для клиента)
- Google Docs (если владелец запросил)
- Telegram текстовый разбор (для оперативного ответа)
- XLSX (реестр замечаний)
- Приложение к акту

Нет жёсткой привязки к PDF-only. Нет жёсткой привязки к металлокаркасу.

---

## 16. Клиентская vs служебная папка

**Клиентская папка (client_facing=True) может содержать:**
- оригинальные фото объекта
- финальный PDF акт
- чистый акт + приложения
- материалы, одобренные владельцем для клиента

**Клиентская папка НЕ должна содержать:**
- черновики
- рабочий DOCX (если владелец не запросил явно Word для клиента)
- JSON / манифесты / логи / debug / temp / кэш
- файлы с task_id
- реестр объектов
- runtime-файлы
- smoke/test файлы
- пути /root/...

---

## 17. Vision guard

`EXTERNAL_PHOTO_ANALYSIS_ALLOWED = False` по умолчанию.

Без явного разрешения владельца — никакой отправки фото наружу.

Если Vision заблокирован:
- использовать голос/текст владельца
- использовать предыдущие акты
- использовать документы
- использовать имена/метаданные файлов
- чётко указать в результате: "Автоматический визуальный анализ фото не выполнялся, так как Vision заблокирован. Выводы основаны на предыдущих актах, пояснениях владельца и доступных именах/метаданных файлов"

---

## 18. Язык вывода

Все клиентские и владельческие тексты — только **русский**:
- Telegram ответы
- акты / разборы / документы
- имена файлов (результирующих)
- таблицы замечаний
- рекомендации / последствия / выводы

English — только внутри кода (функции, классы, enum, маркеры).

---

## 19. Правило одного вопроса

Если данных не хватает — задать один конкретный вопрос.
Никогда не спрашивать "что строим?" если объект уже был активен.
Никогда не спрашивать несколько вопросов сразу без крайней необходимости.

---

## 20. Статусы задачи

CODE_CLOSED_ITEMS (topic_5 контур, верифицировано):
- topic_5 photo/file buffer ✅
- active folder set/get ✅
- Drive folder batch trigger ✅ (P6H4TW_BATCH_TRIGGER_V1)
- flush to process_technadzor ✅
- external Vision guarded (EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False) ✅
- STT hallucination guard ✅
- folder discovery LIVE CLOSED (task 5276 DONE) ✅

VISION_BLOCKED_OWNER_DECISION_REQUIRED:
- OpenRouter Google → 403
- Ни одна Vision модель не включена без явного разрешения владельца
- Решение о включении Vision остаётся за владельцем

---

## 21. Контракт вывода документов

Полный контракт: `docs/TECHNADZOR/TOPIC5_DOCUMENT_OUTPUT_CONTRACT.md`

Ключевые правила:

```
CLIENT_DOCUMENT_DELIVERED = задача выполнена
LOCAL_DRAFT_CREATED        ≠ задача выполнена
DOCX_DRAFT_CREATED         ≠ задача выполнена

Рабочий путь (2026-05-05): TEXT_REPORT → Telegram text
PDF/DOCX: NOT_IMPLEMENTED (reportlab / python-docx не установлены, local-check подтверждён)
```

Именование файлов:
```
Черновик_акта_<объект>_<дата>.docx
Акт_осмотра_<объект>_<дата>.pdf
Реестр_замечаний_<объект>_<дата>.xlsx
```

Drive placement:
- client_facing папка → финальный PDF; DOCX только по явной команде владельца
- Путь /root/... → никогда не отправлять клиенту

---

## 22. Реестр unified_context файлов

Полный индекс: `docs/TECHNADZOR/unified_context/TOPIC5_UNIFIED_TECHNADZOR_CONTEXT.md`

Ключевые файлы:
- OBJECT_CONTEXT_INDEX.json — индекс объектов
- OWNER_ACT_STYLE_PROFILE.md — стиль актов (из 3 реальных Drive актов)
- OWNER_ACTS_INDEX.json — индекс всех актов (5 актов, все DRIVE_VERIFIED)
- NORMATIVE_CONTEXT_INDEX.json — нормативная база
- TNZ_MSK_SKILL_BINDING.json — @tnz_msk как скилл оформления (не нормативная база)

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL_REPORT.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 3fa5aa20e7d214e993ed3cdd8e92f54c81539f60605513169901b9ace0eb726f
====================================================================================================
# TOPIC5 TECHNADZOR — ИТОГОВЫЙ ОТЧЁТ

version: TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL_REPORT_V1
date: 2026-05-05
status: FINAL

---

## 1. Что сделано

### Документы контекста (unified_context/)
- KIEVSKOE_95_OBJECT_CONTEXT.md — DRIVE_VERIFIED (3 акта прочитаны с Drive)
- NOVICHKOVO_OBJECT_CONTEXT.md — DRIVE_VERIFIED (акт Щеглово прочитан, source ref добавлен)
- SUSANINO_OBJECT_CONTEXT.md — DRIVE_VERIFIED (неподтверждённое авторство фото убрано → UNKNOWN)
- OWNER_ACT_STYLE_PROFILE.md — DRIVE_VERIFIED (профиль стиля из 3 реальных актов)
- OBJECT_CONTEXT_INDEX.json — VERIFIED (все folder_id подтверждены Drive API)
- OWNER_ACTS_INDEX.json — DRIVE_VERIFIED (5 актов, все прочитаны)
- NORMATIVE_CONTEXT_INDEX.json — VERIFIED_FROM_ACTS
- TNZ_MSK_SKILL_BINDING.json — VERIFIED
- CHAT_EXPORT_TECHNADZOR_BINDING.json — VERIFIED
- OWNER_ENGINEERING_LOAD_VALIDATION_PATTERN.md/.json — SOURCE_FROM_OWNER_CONVERSATION
- TOPIC5_UNIFIED_TECHNADZOR_CONTEXT.md/.json — VERIFIED

### Системные документы
- TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.md — CODE_AUDIT_VERIFIED (20 секций)
- TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL.json — CODE_AUDIT_VERIFIED
- TOPIC5_DOCUMENT_OUTPUT_CONTRACT.md/.json — CODE_AUDIT_DRAFT_NOT_LIVE_VERIFIED
- TOPIC5_RUNTIME_USAGE_RULES.md — CODE_AUDIT_VERIFIED

---

## 2. Исправленные ошибки

| Файл | Ошибка | Исправление |
|---|---|---|
| SUSANINO_OBJECT_CONTEXT.md | Выдуманное авторство фото (Фото Илья + Фото от заказчиков) | Заменено на UNKNOWN / NOT_VERIFIED |
| NOVICHKOVO_OBJECT_CONTEXT.md | Нет ссылки на источник | Добавлен source_file (Drive id: 1mqE0G-U5mB889IQMlh5e02UFFSkoADW9) |
| OWNER_ACT_STYLE_PROFILE.md | Предыдущая версия создана до чтения Drive актов | Полностью переписан из 3 реальных актов |

---

## 3. Верифицированные факты системы

### Wrapper chains
- `process_technadzor`: 8 определений в technadzor_engine.py, `_p6h4tw_v1_wrapped=True`
- `_handle_in_progress`: 14 определений в task_worker.py
- `_handle_new`: 4 определения в task_worker.py

### Drive
- ТЕХНАДЗОР root: `1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD`
- topic_5 system: `1yWIJdSrypH3BbIozCz-OAw1R6hmnMRHK`
- Active test folder: `тест надзор` (`1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG`) — task 5276 DONE

### Пакеты (local-check 2026-05-05)
- reportlab: NOT INSTALLED (ModuleNotFoundError)
- python-docx: NOT INSTALLED (ModuleNotFoundError)
- DejaVu fonts: PRESENT

### Vision
- `EXTERNAL_PHOTO_ANALYSIS_ALLOWED = False`
- OpenRouter Google: 403

### Search
- SearchMonolithV2 → perplexity/sonar via OpenRouter
- OPENROUTER_API_KEY подтверждён в .env

---

## 4. Открытые вопросы

| Вопрос | Статус |
|---|---|
| Vision для 3-го выезда Киевское (04.05.2026) | OWNER_DECISION_REQUIRED |
| reportlab/python-docx — установить? | OWNER_DECISION_REQUIRED |
| @tnz_msk карты (66 на review) — одобрить? | OWNER_DECISION_REQUIRED |
| ГОСТ 30971 — добавить в normative_engine? | OWNER_DECISION_REQUIRED |

---

## 5. Что НЕ делалось

- Runtime patches: нет
- Drive mutations: нет
- normative_engine.py: не staged, не committed
- Запрещённые файлы: не редактировались

====================================================================================================
END_FILE: docs/TECHNADZOR/TOPIC5_TECHNADZOR_SYSTEM_LOGIC_FINAL_REPORT.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/source_skills/tnz_msk/LINKED_DOCUMENTS_INDEX.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5f685fff1da97501adca5e14d8c99bddcd01f846778f99d1485eae20baaaa6e4
====================================================================================================
{
  "schema": "TNZ_MSK_LINKED_DOCUMENTS_INDEX_V1",
  "source": "@tnz_msk",
  "scanned_at": "2026-05-05T07:49:28.093641+00:00",
  "downloaded_count": 6,
  "downloaded_paths": [
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/ГОСТ Р 72509-2026.pdf",
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/0001202512310019.pdf",
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/Чек-лист по окнам.pdf",
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/checklist_priemka_white_box.pdf",
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/cheklist_priemka_kvartiry_v_betone_kirillitsa.pdf",
    "/root/.areal-neva-core/data/memory_files/TEHNADZOR/source_skills/tnz_msk/downloaded_docs/ВСН 53-86 Утратил силу.pdf"
  ],
  "linked_urls": [
    "https://donstroy.moscow/owners/keys/",
    "https://ds-fest.ru/",
    "https://framerfest.ru/",
    "https://markets.house/",
    "https://max.ru/tnz_msk",
    "https://poly.cam/",
    "https://t.me/+26x9OiOEawphMDdi",
    "https://t.me/KarabanovPV",
    "https://t.me/developers_policy/8029",
    "https://t.me/glebgrinfeld/668",
    "https://t.me/neural_ntw",
    "https://t.me/neural_ntw/175",
    "https://t.me/parket_expert",
    "https://t.me/tnz_msk",
    "https://t.me/tnz_msk/116",
    "https://t.me/tnz_msk/2899",
    "https://t.me/tnz_msk/3290",
    "https://t.me/tnz_msk/3391",
    "https://t.me/tnz_msk/3436",
    "https://t.me/tnz_msk/3606",
    "https://t.me/tnz_msk/3635",
    "https://t.me/tnz_msk/3654",
    "https://t.me/tnz_msk/3785",
    "https://t.me/tnz_msk/4",
    "https://t.me/tnz_msk?livestream",
    "https://telegra.ph/Svetlyachkam-na-zavist-06-14",
    "https://telegra.ph/Svetlyachkam-na-zavist-part-2-08-05",
    "https://telegra.ph/U-nas-promerzanie--D-12-19",
    "https://vk.com/clip-216130923_456240215",
    "https://www.gosuslugi.ru/snet/6895ec2c06836073af0da543",
    "https://www.youtube.com/watch?v=7kZHpvqMqRM",
    "https://www.youtube.com/watch?v=A4sMjYyN7FM",
    "https://www.youtube.com/watch?v=HGQU1ZdylT0",
    "https://www.youtube.com/watch?v=LWE3TCS8njs",
    "https://www.youtube.com/watch?v=Vt7w9kjG460",
    "https://www.youtube.com/watch?v=i4yUN8YANJs",
    "https://www.youtube.com/watch?v=vhXxJp1MS6E",
    "https://yandex.ru/adv/edu/materials/registraciya-blogerov-ot-10000-podpischikov?ysclid=mdfrqderhy804916339",
    "https://yandex.ru/maps/?um=constructor%3Af35f7f3f5f880a78b46c473eca916075f563f6eaf036006f7519a3f3f3751e89&source=constructorLink",
    "https://yandex.ru/video/touch/preview/17284700974743076036"
  ],
  "document_messages": [
    {
      "message_id": 4059,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4059",
      "file_name": "IMG_5198.MOV"
    },
    {
      "message_id": 4058,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4058",
      "file_name": "IMG_5200.MOV"
    },
    {
      "message_id": 4036,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4036",
      "file_name": "IMG_4848.MOV"
    },
    {
      "message_id": 4023,
      "date": "2026-04-20T09:48:36+00:00",
      "source_ref": "https://t.me/tnz_msk/4023",
      "file_name": "IMG_4666.MOV"
    },
    {
      "message_id": 4021,
      "date": "2026-04-16T10:53:00+00:00",
      "source_ref": "https://t.me/tnz_msk/4021",
      "file_name": "IMG_4381.MOV"
    },
    {
      "message_id": 4005,
      "date": "2026-04-11T23:16:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4005",
      "file_name": "IMG_5079.MP4"
    },
    {
      "message_id": 4004,
      "date": "2026-04-11T23:16:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4004",
      "file_name": "IMG_5078.MOV"
    },
    {
      "message_id": 3998,
      "date": "2026-04-09T08:40:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3998",
      "file_name": "IMG_4172.MP4"
    },
    {
      "message_id": 3992,
      "date": "2026-04-05T10:04:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3992",
      "file_name": "IMG_1448.mp4"
    },
    {
      "message_id": 3988,
      "date": "2026-04-02T20:51:08+00:00",
      "source_ref": "https://t.me/tnz_msk/3988",
      "file_name": "IMG_1642.MP4"
    },
    {
      "message_id": 3978,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3978",
      "file_name": "IMG_3415.MOV"
    },
    {
      "message_id": 3977,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3977",
      "file_name": "IMG_3421.MOV"
    },
    {
      "message_id": 3971,
      "date": "2026-04-01T07:36:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3971",
      "file_name": "IMG_3860.MP4"
    },
    {
      "message_id": 3965,
      "date": "2026-03-31T21:05:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3965",
      "file_name": "IMG_1570.MP4"
    },
    {
      "message_id": 3943,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3943",
      "file_name": "IMG_3518.MOV"
    },
    {
      "message_id": 3929,
      "date": "2026-03-10T19:44:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3929",
      "file_name": "video_2026-03-10_22-40-41.mp4"
    },
    {
      "message_id": 3903,
      "date": "2026-02-21T10:11:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3903",
      "file_name": "IMG_2455.MP4"
    },
    {
      "message_id": 3901,
      "date": "2026-02-20T16:46:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3901",
      "file_name": "ГОСТ Р 72509-2026.pdf"
    },
    {
      "message_id": 3895,
      "date": "2026-02-18T04:05:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3895",
      "file_name": "IMG_2370.MP4"
    },
    {
      "message_id": 3893,
      "date": "2026-02-17T15:11:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3893",
      "file_name": "IMG_2365.MP4"
    },
    {
      "message_id": 3892,
      "date": "2026-02-17T12:38:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3892",
      "file_name": "IMG_2355.MOV"
    },
    {
      "message_id": 3891,
      "date": "2026-02-17T04:57:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3891",
      "file_name": "Бот.mp4"
    },
    {
      "message_id": 3890,
      "date": "2026-02-13T13:26:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3890",
      "file_name": "IMG_2239.MP4"
    },
    {
      "message_id": 3883,
      "date": "2026-02-08T15:44:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3883",
      "file_name": "IMG_2135.MP4"
    },
    {
      "message_id": 3865,
      "date": "2026-02-05T14:25:43+00:00",
      "source_ref": "https://t.me/tnz_msk/3865",
      "file_name": "IMG_2034.MP4"
    },
    {
      "message_id": 3864,
      "date": "2026-02-05T14:25:43+00:00",
      "source_ref": "https://t.me/tnz_msk/3864",
      "file_name": "IMG_2035.MP4"
    },
    {
      "message_id": 3844,
      "date": "2026-01-23T15:48:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3844",
      "file_name": "IMG_1542.MP4"
    },
    {
      "message_id": 3840,
      "date": "2026-01-22T12:52:31+00:00",
      "source_ref": "https://t.me/tnz_msk/3840",
      "file_name": "IMG_1471.MP4"
    },
    {
      "message_id": 3836,
      "date": "2026-01-22T09:56:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3836",
      "file_name": "IMG_1454.MP4"
    },
    {
      "message_id": 3833,
      "date": "2026-01-20T07:49:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3833",
      "file_name": "1113 (1)(1).mp4"
    },
    {
      "message_id": 3817,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3817",
      "file_name": "IMG_1195.MOV"
    },
    {
      "message_id": 3807,
      "date": "2026-01-05T09:30:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3807",
      "file_name": "0001202512310019.pdf"
    },
    {
      "message_id": 3784,
      "date": "2025-12-23T15:12:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3784",
      "file_name": "IMG_0527.MP4"
    },
    {
      "message_id": 3751,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3751",
      "file_name": "IMG_9952.MP4"
    },
    {
      "message_id": 3749,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3749",
      "file_name": "IMG_9949.MP4"
    },
    {
      "message_id": 3748,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3748",
      "file_name": "IMG_9948.MP4"
    },
    {
      "message_id": 3747,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3747",
      "file_name": "IMG_9944.MP4"
    },
    {
      "message_id": 3746,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3746",
      "file_name": "IMG_9947.MP4"
    },
    {
      "message_id": 3743,
      "date": "2025-12-07T08:10:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3743",
      "file_name": "IMG_9831.MP4"
    },
    {
      "message_id": 3740,
      "date": "2025-12-06T11:16:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3740",
      "file_name": "IMG_9862.MP4"
    },
    {
      "message_id": 3735,
      "date": "2025-12-04T08:41:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3735",
      "file_name": "IMG_9750.MP4"
    },
    {
      "message_id": 3730,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3730",
      "file_name": "IMG_9618.MOV"
    },
    {
      "message_id": 3729,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3729",
      "file_name": "IMG_9617.MOV"
    },
    {
      "message_id": 3728,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3728",
      "file_name": "IMG_9615.MOV"
    },
    {
      "message_id": 3714,
      "date": "2025-11-28T12:14:17+00:00",
      "source_ref": "https://t.me/tnz_msk/3714",
      "file_name": "IMG_9573.MP4"
    },
    {
      "message_id": 3710,
      "date": "2025-11-26T12:22:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3710",
      "file_name": "Чек-лист по окнам.pdf"
    },
    {
      "message_id": 3694,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3694",
      "file_name": "IMG_9373.MP4"
    },
    {
      "message_id": 3693,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3693",
      "file_name": "IMG_9374.MP4"
    },
    {
      "message_id": 3691,
      "date": "2025-11-24T16:58:33+00:00",
      "source_ref": "https://t.me/tnz_msk/3691",
      "file_name": "record.ogg"
    },
    {
      "message_id": 3690,
      "date": "2025-11-24T16:58:33+00:00",
      "source_ref": "https://t.me/tnz_msk/3690",
      "file_name": "record.mp4"
    },
    {
      "message_id": 3675,
      "date": "2025-11-20T16:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3675",
      "file_name": "IMG_9159.MP4"
    },
    {
      "message_id": 3657,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3657",
      "file_name": "IMG_8898.MOV"
    },
    {
      "message_id": 3656,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3656",
      "file_name": "IMG_8899.MOV"
    },
    {
      "message_id": 3630,
      "date": "2025-11-07T14:37:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3630",
      "file_name": "19700121_1234_690d225fb42481919d3aa09139f5e817.mp4"
    },
    {
      "message_id": 3629,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3629",
      "file_name": "IMG_8340.MOV"
    },
    {
      "message_id": 3628,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3628",
      "file_name": "IMG_8360.MOV"
    },
    {
      "message_id": 3625,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3625",
      "file_name": "IMG_8351.MOV"
    },
    {
      "message_id": 3623,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3623",
      "file_name": "IMG_8329.MOV"
    },
    {
      "message_id": 3622,
      "date": "2025-11-06T08:10:44+00:00",
      "source_ref": "https://t.me/tnz_msk/3622",
      "file_name": "IMG_8345.MOV"
    },
    {
      "message_id": 3621,
      "date": "2025-11-05T18:41:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3621",
      "file_name": "video_2025-11-05_21-40-44.mp4"
    },
    {
      "message_id": 3604,
      "date": "2025-11-03T09:45:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3604",
      "file_name": "IMG_8161.MP4"
    },
    {
      "message_id": 3589,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3589",
      "file_name": "IMG_8035.MOV"
    },
    {
      "message_id": 3588,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3588",
      "file_name": "IMG_8010.MOV"
    },
    {
      "message_id": 3587,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3587",
      "file_name": "IMG_8037.MP4"
    },
    {
      "message_id": 3586,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3586",
      "file_name": "IMG_8038.MP4"
    },
    {
      "message_id": 3585,
      "date": "2025-10-27T16:28:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3585",
      "file_name": "IMG_7990.MOV"
    },
    {
      "message_id": 3581,
      "date": "2025-10-26T04:45:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3581",
      "file_name": "sora_video_1761427768738.mp4"
    },
    {
      "message_id": 3580,
      "date": "2025-10-25T04:16:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3580",
      "file_name": "ScreenRecorderProject96.mp4"
    },
    {
      "message_id": 3579,
      "date": "2025-10-24T16:00:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3579",
      "file_name": "IMG_7820.MP4"
    },
    {
      "message_id": 3576,
      "date": "2025-10-24T15:58:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3576",
      "file_name": "IMG_7820.MP4"
    },
    {
      "message_id": 3571,
      "date": "2025-10-24T03:39:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3571",
      "file_name": "checklist_priemka_white_box.pdf"
    },
    {
      "message_id": 3563,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3563",
      "file_name": "IMG_7621.MOV"
    },
    {
      "message_id": 3562,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3562",
      "file_name": "IMG_7620.MOV"
    },
    {
      "message_id": 3561,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3561",
      "file_name": "IMG_7646.MP4"
    },
    {
      "message_id": 3559,
      "date": "2025-10-22T04:06:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3559",
      "file_name": "cheklist_priemka_kvartiry_v_betone_kirillitsa.pdf"
    },
    {
      "message_id": 3547,
      "date": "2025-10-20T16:58:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3547",
      "file_name": "IMG_7494.MP4"
    },
    {
      "message_id": 3539,
      "date": "2025-10-20T10:15:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3539",
      "file_name": "IMG_7437.MOV"
    },
    {
      "message_id": 3537,
      "date": "2025-10-18T09:48:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3537",
      "file_name": "IMG_7318.MP4"
    },
    {
      "message_id": 3536,
      "date": "2025-10-17T14:52:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3536",
      "file_name": "IMG_7341.MP4"
    },
    {
      "message_id": 3521,
      "date": "2025-10-15T14:50:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3521",
      "file_name": "IMG_7247.MOV"
    },
    {
      "message_id": 3520,
      "date": "2025-10-15T14:50:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3520",
      "file_name": "IMG_7248.MOV"
    },
    {
      "message_id": 3519,
      "date": "2025-10-15T14:50:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3519",
      "file_name": "IMG_7246.MP4"
    },
    {
      "message_id": 3492,
      "date": "2025-10-08T13:35:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3492",
      "file_name": "IMG_4490.MOV"
    },
    {
      "message_id": 3491,
      "date": "2025-10-08T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3491",
      "file_name": "watermark-removed-20251008_0035_01k709amyafkka83bp7j708xxn.mp4"
    },
    {
      "message_id": 3487,
      "date": "2025-10-06T04:28:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3487",
      "file_name": "video_2025-10-06_00-15-54.mp4"
    },
    {
      "message_id": 3486,
      "date": "2025-10-05T17:29:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3486",
      "file_name": "IMG_6893.MP4"
    },
    {
      "message_id": 3485,
      "date": "2025-10-05T14:08:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3485",
      "file_name": "IMG_6882.MP4"
    },
    {
      "message_id": 3484,
      "date": "2025-10-05T09:13:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3484",
      "file_name": "20251005_1211_01k6st6fgee749rtfghjefsra1.mp4"
    },
    {
      "message_id": 3483,
      "date": "2025-10-03T14:20:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3483",
      "file_name": "IMG_6817.MP4"
    },
    {
      "message_id": 3482,
      "date": "2025-10-01T20:27:52+00:00",
      "source_ref": "https://t.me/tnz_msk/3482",
      "file_name": "20251001_2327_01k6gq89y0fpkamh6ycr0txqhs.mp4"
    },
    {
      "message_id": 3481,
      "date": "2025-10-01T19:47:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3481",
      "file_name": "20251001_2246_01k6gmxkw2f4fvn46zhbm80y56.mp4"
    },
    {
      "message_id": 3479,
      "date": "2025-09-30T21:58:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3479",
      "file_name": "IMG_7556.MP4"
    },
    {
      "message_id": 3475,
      "date": "2025-09-29T04:33:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3475",
      "file_name": "Новый проект.mp4"
    },
    {
      "message_id": 3471,
      "date": "2025-09-24T16:24:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3471",
      "file_name": "IMG_6579.MP4"
    },
    {
      "message_id": 3466,
      "date": "2025-09-19T09:23:17+00:00",
      "source_ref": "https://t.me/tnz_msk/3466",
      "file_name": "IMG_6370.MP4"
    },
    {
      "message_id": 3442,
      "date": "2025-09-13T08:53:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3442",
      "file_name": "IMG_6006.MP4"
    },
    {
      "message_id": 3441,
      "date": "2025-09-13T08:53:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3441",
      "file_name": "IMG_6005.MP4"
    },
    {
      "message_id": 3425,
      "date": "2025-08-29T09:02:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3425",
      "file_name": "IMG_5435.MOV"
    },
    {
      "message_id": 3424,
      "date": "2025-08-28T10:14:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3424",
      "file_name": "IMG_5368.MP4"
    },
    {
      "message_id": 3422,
      "date": "2025-08-27T13:19:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3422",
      "file_name": "IMG_5337.MP4"
    },
    {
      "message_id": 3417,
      "date": "2025-08-27T13:19:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3417",
      "file_name": "IMG_5329.MOV"
    },
    {
      "message_id": 3416,
      "date": "2025-08-27T09:01:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3416",
      "file_name": "IMG_5302.MP4"
    },
    {
      "message_id": 3401,
      "date": "2025-08-22T18:56:35+00:00",
      "source_ref": "https://t.me/tnz_msk/3401",
      "file_name": "IMG_5811.MP4"
    },
    {
      "message_id": 3398,
      "date": "2025-08-21T11:51:07+00:00",
      "source_ref": "https://t.me/tnz_msk/3398",
      "file_name": "IMG_4981.MOV"
    },
    {
      "message_id": 3387,
      "date": "2025-08-14T15:59:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3387",
      "file_name": "IMG_4764.MP4"
    },
    {
      "message_id": 3377,
      "date": "2025-08-13T07:50:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3377",
      "file_name": "IMG_4715.MOV"
    },
    {
      "message_id": 3375,
      "date": "2025-08-12T20:21:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3375",
      "file_name": "IMG_6243.MOV"
    },
    {
      "message_id": 3367,
      "date": "2025-08-10T20:18:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3367",
      "file_name": "IMG_4661.MP4"
    },
    {
      "message_id": 3356,
      "date": "2025-08-08T12:49:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3356",
      "file_name": "IMG_4469.MOV"
    },
    {
      "message_id": 3353,
      "date": "2025-08-07T20:00:39+00:00",
      "source_ref": "https://t.me/tnz_msk/3353",
      "file_name": "video_2025-08-07_21-50-56.mp4"
    },
    {
      "message_id": 3352,
      "date": "2025-08-07T17:35:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3352",
      "file_name": "IMG_4386.MP4"
    },
    {
      "message_id": 3344,
      "date": "2025-08-07T17:35:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3344",
      "file_name": "IMG_4365.MOV"
    },
    {
      "message_id": 3334,
      "date": "2025-08-07T06:49:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3334",
      "file_name": "IMG_4386.MP4"
    },
    {
      "message_id": 3316,
      "date": "2025-08-03T12:35:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3316",
      "file_name": "IMG_0125.MP4"
    },
    {
      "message_id": 3315,
      "date": "2025-08-02T12:55:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3315",
      "file_name": "IMG_4218.MOV"
    },
    {
      "message_id": 3313,
      "date": "2025-08-02T12:55:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3313",
      "file_name": "IMG_4213.MOV"
    },
    {
      "message_id": 3312,
      "date": "2025-08-02T12:55:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3312",
      "file_name": "IMG_4210.MOV"
    },
    {
      "message_id": 3311,
      "date": "2025-08-02T12:55:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3311",
      "file_name": "IMG_4209.MOV"
    },
    {
      "message_id": 3310,
      "date": "2025-08-02T12:55:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3310",
      "file_name": "IMG_4205.MOV"
    },
    {
      "message_id": 3309,
      "date": "2025-08-01T19:48:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3309",
      "file_name": "video_2025-08-01_22-47-43.mp4"
    },
    {
      "message_id": 3302,
      "date": "2025-08-01T08:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3302",
      "file_name": "polycam.mp4"
    },
    {
      "message_id": 3291,
      "date": "2025-07-26T21:10:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3291",
      "file_name": "IMG_2715.MP4"
    },
    {
      "message_id": 3282,
      "date": "2025-07-25T10:53:59+00:00",
      "source_ref": "https://t.me/tnz_msk/3282",
      "file_name": "IMG_3851.MP4"
    },
    {
      "message_id": 3271,
      "date": "2025-07-24T09:23:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3271",
      "file_name": "IMG_3811.MOV"
    },
    {
      "message_id": 3258,
      "date": "2025-07-18T08:25:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3258",
      "file_name": "IMG_3419.MOV"
    },
    {
      "message_id": 3242,
      "date": "2025-07-15T07:43:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3242",
      "file_name": "IMG_3158.MP4"
    },
    {
      "message_id": 3231,
      "date": "2025-07-11T14:20:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3231",
      "file_name": "IMG_2811.MP4"
    },
    {
      "message_id": 3227,
      "date": "2025-07-10T11:31:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3227",
      "file_name": "IMG_2695.MOV"
    },
    {
      "message_id": 3202,
      "date": "2025-07-05T15:56:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3202",
      "file_name": "IMG_2463.MP4"
    },
    {
      "message_id": 3201,
      "date": "2025-07-05T15:56:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3201",
      "file_name": "IMG_2465.MP4"
    },
    {
      "message_id": 3200,
      "date": "2025-07-05T15:56:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3200",
      "file_name": "IMG_2464.MP4"
    },
    {
      "message_id": 3199,
      "date": "2025-07-04T18:24:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3199",
      "file_name": "IMG_2400.MP4"
    },
    {
      "message_id": 3198,
      "date": "2025-07-04T14:26:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3198",
      "file_name": "IMG_2406.MOV"
    },
    {
      "message_id": 3186,
      "date": "2025-07-02T15:22:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3186",
      "file_name": "IMG_2264.MOV"
    },
    {
      "message_id": 3184,
      "date": "2025-07-01T20:39:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3184",
      "file_name": "Видео WhatsApp 2025-06-30 в 15.51.31_6dd6737c.mp4"
    },
    {
      "message_id": 3183,
      "date": "2025-06-30T10:53:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3183",
      "file_name": "IMG_9935.MOV"
    },
    {
      "message_id": 3182,
      "date": "2025-06-30T10:00:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3182",
      "file_name": "IMG_1576.MP4"
    },
    {
      "message_id": 3180,
      "date": "2025-06-30T08:13:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3180",
      "file_name": "IMG_2110.MP4"
    },
    {
      "message_id": 3179,
      "date": "2025-06-30T07:16:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3179",
      "file_name": "IMG_2107.MP4"
    },
    {
      "message_id": 3166,
      "date": "2025-06-27T14:03:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3166",
      "file_name": "IMG_2048.MP4"
    },
    {
      "message_id": 3136,
      "date": "2025-06-19T14:31:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3136",
      "file_name": "IMG_1460.MOV"
    },
    {
      "message_id": 3134,
      "date": "2025-06-19T10:15:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3134",
      "file_name": "IMG_1598.MP4"
    },
    {
      "message_id": 3130,
      "date": "2025-06-19T10:15:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3130",
      "file_name": "IMG_1440.MOV"
    },
    {
      "message_id": 3128,
      "date": "2025-06-18T08:03:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3128",
      "file_name": "IMG_1565.MP4"
    },
    {
      "message_id": 3117,
      "date": "2025-06-14T15:35:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3117",
      "file_name": "IMG_1406.MP4"
    },
    {
      "message_id": 3112,
      "date": "2025-06-10T08:20:34+00:00",
      "source_ref": "https://t.me/tnz_msk/3112",
      "file_name": "IMG_1191.MP4"
    },
    {
      "message_id": 3111,
      "date": "2025-06-08T07:42:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3111",
      "file_name": "IMG_1130.MP4"
    },
    {
      "message_id": 3086,
      "date": "2025-05-30T11:10:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3086",
      "file_name": "AIIN.mp4"
    },
    {
      "message_id": 3084,
      "date": "2025-05-29T20:46:59+00:00",
      "source_ref": "https://t.me/tnz_msk/3084",
      "file_name": "record.ogg"
    },
    {
      "message_id": 3083,
      "date": "2025-05-29T16:17:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3083",
      "file_name": "record.mp4"
    },
    {
      "message_id": 3077,
      "date": "2025-05-28T04:09:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3077",
      "file_name": "ВСН 53-86 Утратил силу.pdf"
    },
    {
      "message_id": 3072,
      "date": "2025-05-25T12:09:34+00:00",
      "source_ref": "https://t.me/tnz_msk/3072",
      "file_name": "IMG_0537.MOV"
    },
    {
      "message_id": 3070,
      "date": "2025-05-25T12:09:34+00:00",
      "source_ref": "https://t.me/tnz_msk/3070",
      "file_name": "IMG_0547.MOV"
    },
    {
      "message_id": 3067,
      "date": "2025-05-25T12:09:34+00:00",
      "source_ref": "https://t.me/tnz_msk/3067",
      "file_name": "IMG_0546.MOV"
    },
    {
      "message_id": 3063,
      "date": "2025-05-24T05:31:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3063",
      "file_name": "IMG_0477.MP4"
    },
    {
      "message_id": 3062,
      "date": "2025-05-24T05:31:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3062",
      "file_name": "IMG_0476.MP4"
    },
    {
      "message_id": 3050,
      "date": "2025-05-21T16:29:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3050",
      "file_name": "IMG_3938.MOV"
    },
    {
      "message_id": 3037,
      "date": "2025-05-19T08:44:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3037",
      "file_name": "IMG_0223.MP4"
    },
    {
      "message_id": 3034,
      "date": "2025-05-14T17:17:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3034",
      "file_name": "video_2025-05-15_00-14-14.mp4"
    },
    {
      "message_id": 3033,
      "date": "2025-05-14T10:51:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3033",
      "file_name": "IMG_9931.MOV"
    },
    {
      "message_id": 3031,
      "date": "2025-05-13T07:07:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3031",
      "file_name": "IMG_9914.MOV"
    }
  ]
}
====================================================================================================
END_FILE: docs/TECHNADZOR/source_skills/tnz_msk/LINKED_DOCUMENTS_INDEX.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/TECHNADZOR/source_skills/tnz_msk/SOURCE_INDEX.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 64adb6f42d95261884ffea8950affac4b4b134750a417e397449e804b004ca28
====================================================================================================
{
  "schema": "TNZ_MSK_SOURCE_INDEX_V1",
  "source": "@tnz_msk",
  "scanned_at": "2026-05-05T07:49:28.093445+00:00",
  "total_fetched": 1000,
  "records_count": 971,
  "records": [
    {
      "message_id": 4068,
      "date": "2026-05-04T11:17:38+00:00",
      "source_ref": "https://t.me/tnz_msk/4068",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4067,
      "date": "2026-05-04T04:50:05+00:00",
      "source_ref": "https://t.me/tnz_msk/4067",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4066,
      "date": "2026-05-02T13:49:44+00:00",
      "source_ref": "https://t.me/tnz_msk/4066",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4065,
      "date": "2026-05-02T13:49:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4065",
      "has_links": true,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4064,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4064",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4063,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4063",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4062,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4062",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4061,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4061",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4060,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4060",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4059,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4059",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4058,
      "date": "2026-05-01T09:44:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4058",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4057,
      "date": "2026-04-30T05:34:01+00:00",
      "source_ref": "https://t.me/tnz_msk/4057",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4056,
      "date": "2026-04-27T07:26:47+00:00",
      "source_ref": "https://t.me/tnz_msk/4056",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 4055,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4055",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4054,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4054",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4053,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4053",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4052,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4052",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4051,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4051",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4050,
      "date": "2026-04-25T13:20:45+00:00",
      "source_ref": "https://t.me/tnz_msk/4050",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4049,
      "date": "2026-04-25T13:20:44+00:00",
      "source_ref": "https://t.me/tnz_msk/4049",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4048,
      "date": "2026-04-25T13:20:44+00:00",
      "source_ref": "https://t.me/tnz_msk/4048",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4047,
      "date": "2026-04-25T11:57:46+00:00",
      "source_ref": "https://t.me/tnz_msk/4047",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4046,
      "date": "2026-04-25T11:57:46+00:00",
      "source_ref": "https://t.me/tnz_msk/4046",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4045,
      "date": "2026-04-25T11:57:46+00:00",
      "source_ref": "https://t.me/tnz_msk/4045",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4044,
      "date": "2026-04-25T11:57:46+00:00",
      "source_ref": "https://t.me/tnz_msk/4044",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4043,
      "date": "2026-04-25T11:57:46+00:00",
      "source_ref": "https://t.me/tnz_msk/4043",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4042,
      "date": "2026-04-24T17:53:44+00:00",
      "source_ref": "https://t.me/tnz_msk/4042",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4041,
      "date": "2026-04-24T17:53:44+00:00",
      "source_ref": "https://t.me/tnz_msk/4041",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4040,
      "date": "2026-04-24T16:17:01+00:00",
      "source_ref": "https://t.me/tnz_msk/4040",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4039,
      "date": "2026-04-24T16:17:01+00:00",
      "source_ref": "https://t.me/tnz_msk/4039",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4038,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4038",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4037,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4037",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4036,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4036",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4035,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4035",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4034,
      "date": "2026-04-24T12:33:58+00:00",
      "source_ref": "https://t.me/tnz_msk/4034",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4033,
      "date": "2026-04-23T17:28:13+00:00",
      "source_ref": "https://t.me/tnz_msk/4033",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4032,
      "date": "2026-04-23T16:07:07+00:00",
      "source_ref": "https://t.me/tnz_msk/4032",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4030,
      "date": "2026-04-23T05:47:53+00:00",
      "source_ref": "https://t.me/tnz_msk/4030",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4029,
      "date": "2026-04-23T05:47:53+00:00",
      "source_ref": "https://t.me/tnz_msk/4029",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4028,
      "date": "2026-04-23T05:47:53+00:00",
      "source_ref": "https://t.me/tnz_msk/4028",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4027,
      "date": "2026-04-21T15:15:31+00:00",
      "source_ref": "https://t.me/tnz_msk/4027",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4026,
      "date": "2026-04-21T15:15:31+00:00",
      "source_ref": "https://t.me/tnz_msk/4026",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4025,
      "date": "2026-04-21T15:15:31+00:00",
      "source_ref": "https://t.me/tnz_msk/4025",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4024,
      "date": "2026-04-21T15:15:31+00:00",
      "source_ref": "https://t.me/tnz_msk/4024",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4023,
      "date": "2026-04-20T09:48:36+00:00",
      "source_ref": "https://t.me/tnz_msk/4023",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4022,
      "date": "2026-04-16T13:39:50+00:00",
      "source_ref": "https://t.me/tnz_msk/4022",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4021,
      "date": "2026-04-16T10:53:00+00:00",
      "source_ref": "https://t.me/tnz_msk/4021",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4020,
      "date": "2026-04-16T10:53:00+00:00",
      "source_ref": "https://t.me/tnz_msk/4020",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4019,
      "date": "2026-04-16T10:53:00+00:00",
      "source_ref": "https://t.me/tnz_msk/4019",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4018,
      "date": "2026-04-15T16:44:14+00:00",
      "source_ref": "https://t.me/tnz_msk/4018",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4017,
      "date": "2026-04-15T16:44:14+00:00",
      "source_ref": "https://t.me/tnz_msk/4017",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4016,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4016",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4015,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4015",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4014,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4014",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4013,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4013",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4012,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4012",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4011,
      "date": "2026-04-14T17:08:33+00:00",
      "source_ref": "https://t.me/tnz_msk/4011",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4010,
      "date": "2026-04-14T16:59:12+00:00",
      "source_ref": "https://t.me/tnz_msk/4010",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 4009,
      "date": "2026-04-13T14:38:49+00:00",
      "source_ref": "https://t.me/tnz_msk/4009",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4008,
      "date": "2026-04-13T14:38:49+00:00",
      "source_ref": "https://t.me/tnz_msk/4008",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4007,
      "date": "2026-04-13T14:38:49+00:00",
      "source_ref": "https://t.me/tnz_msk/4007",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4006,
      "date": "2026-04-13T14:38:49+00:00",
      "source_ref": "https://t.me/tnz_msk/4006",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4005,
      "date": "2026-04-11T23:16:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4005",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4004,
      "date": "2026-04-11T23:16:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4004",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 4003,
      "date": "2026-04-11T23:16:43+00:00",
      "source_ref": "https://t.me/tnz_msk/4003",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 4002,
      "date": "2026-04-10T16:32:18+00:00",
      "source_ref": "https://t.me/tnz_msk/4002",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 4001,
      "date": "2026-04-10T12:44:04+00:00",
      "source_ref": "https://t.me/tnz_msk/4001",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 4000,
      "date": "2026-04-10T11:25:38+00:00",
      "source_ref": "https://t.me/tnz_msk/4000",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3999,
      "date": "2026-04-10T08:36:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3999",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3998,
      "date": "2026-04-09T08:40:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3998",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3997,
      "date": "2026-04-08T15:16:14+00:00",
      "source_ref": "https://t.me/tnz_msk/3997",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3996,
      "date": "2026-04-08T11:57:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3996",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3995,
      "date": "2026-04-08T11:57:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3995",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3994,
      "date": "2026-04-05T10:44:16+00:00",
      "source_ref": "https://t.me/tnz_msk/3994",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3993,
      "date": "2026-04-05T10:16:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3993",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3992,
      "date": "2026-04-05T10:04:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3992",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3991,
      "date": "2026-04-05T10:04:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3991",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3990,
      "date": "2026-04-05T09:09:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3990",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3989,
      "date": "2026-04-03T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3989",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3988,
      "date": "2026-04-02T20:51:08+00:00",
      "source_ref": "https://t.me/tnz_msk/3988",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3987,
      "date": "2026-04-02T14:42:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3987",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3986,
      "date": "2026-04-02T09:30:57+00:00",
      "source_ref": "https://t.me/tnz_msk/3986",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3985,
      "date": "2026-04-01T09:31:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3985",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3984,
      "date": "2026-04-01T09:25:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3984",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3983,
      "date": "2026-04-01T09:25:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3983",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3982,
      "date": "2026-04-01T09:25:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3982",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3981,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3981",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3980,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3980",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3979,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3979",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3978,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3978",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3977,
      "date": "2026-04-01T09:16:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3977",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3976,
      "date": "2026-04-01T08:39:57+00:00",
      "source_ref": "https://t.me/tnz_msk/3976",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3975,
      "date": "2026-04-01T08:39:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3975",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3974,
      "date": "2026-04-01T08:39:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3974",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3973,
      "date": "2026-04-01T07:36:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3973",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3972,
      "date": "2026-04-01T07:36:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3972",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3971,
      "date": "2026-04-01T07:36:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3971",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3970,
      "date": "2026-04-01T06:06:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3970",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3969,
      "date": "2026-04-01T05:56:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3969",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3968,
      "date": "2026-04-01T05:42:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3968",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3967,
      "date": "2026-04-01T05:42:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3967",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3965,
      "date": "2026-03-31T21:05:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3965",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3964,
      "date": "2026-03-31T21:01:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3964",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3963,
      "date": "2026-03-30T10:05:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3963",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3962,
      "date": "2026-03-28T19:23:33+00:00",
      "source_ref": "https://t.me/tnz_msk/3962",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3960,
      "date": "2026-03-27T11:18:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3960",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3959,
      "date": "2026-03-27T11:01:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3959",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3958,
      "date": "2026-03-27T10:13:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3958",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3957,
      "date": "2026-03-27T07:18:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3957",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3956,
      "date": "2026-03-27T04:03:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3956",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3955,
      "date": "2026-03-26T19:36:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3955",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3954,
      "date": "2026-03-26T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3954",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3953,
      "date": "2026-03-26T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3953",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3952,
      "date": "2026-03-26T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3952",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3951,
      "date": "2026-03-26T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3951",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3950,
      "date": "2026-03-26T04:23:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3950",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3949,
      "date": "2026-03-25T03:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3949",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3948,
      "date": "2026-03-24T08:04:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3948",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3947,
      "date": "2026-03-24T08:04:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3947",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3945,
      "date": "2026-03-21T20:35:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3945",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3944,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3944",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3943,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3943",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3942,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3942",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3941,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3941",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3940,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3940",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3939,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3939",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3938,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3938",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3937,
      "date": "2026-03-20T15:06:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3937",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3936,
      "date": "2026-03-18T16:20:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3936",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3935,
      "date": "2026-03-17T09:22:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3935",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3934,
      "date": "2026-03-17T09:22:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3934",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3933,
      "date": "2026-03-17T09:22:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3933",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3932,
      "date": "2026-03-12T21:51:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3932",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3931,
      "date": "2026-03-11T20:06:18+00:00",
      "source_ref": "https://t.me/tnz_msk/3931",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3929,
      "date": "2026-03-10T19:44:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3929",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3928,
      "date": "2026-03-09T20:52:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3928",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3927,
      "date": "2026-03-09T11:05:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3927",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3926,
      "date": "2026-03-09T11:05:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3926",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3924,
      "date": "2026-03-08T08:03:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3924",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3923,
      "date": "2026-03-06T10:01:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3923",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3922,
      "date": "2026-03-06T06:58:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3922",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3921,
      "date": "2026-03-06T03:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3921",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3920,
      "date": "2026-03-05T17:31:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3920",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3918,
      "date": "2026-03-04T08:34:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3918",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3917,
      "date": "2026-03-04T07:04:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3917",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3916,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3916",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3915,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3915",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3914,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3914",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3913,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3913",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3912,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3912",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3911,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3911",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3910,
      "date": "2026-03-03T12:43:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3910",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3909,
      "date": "2026-03-03T10:33:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3909",
      "has_links": true,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3908,
      "date": "2026-03-03T07:24:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3908",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3907,
      "date": "2026-03-03T03:13:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3907",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3906,
      "date": "2026-02-26T10:37:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3906",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3905,
      "date": "2026-02-26T10:37:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3905",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3903,
      "date": "2026-02-21T10:11:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3903",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3902,
      "date": "2026-02-21T10:01:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3902",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3901,
      "date": "2026-02-20T16:46:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3901",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3900,
      "date": "2026-02-18T04:05:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3900",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3899,
      "date": "2026-02-18T04:05:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3899",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3898,
      "date": "2026-02-18T04:05:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3898",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3897,
      "date": "2026-02-18T04:05:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3897",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3896,
      "date": "2026-02-18T04:05:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3896",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3895,
      "date": "2026-02-18T04:05:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3895",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3894,
      "date": "2026-02-17T16:23:02+00:00",
      "source_ref": "https://t.me/tnz_msk/3894",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3893,
      "date": "2026-02-17T15:11:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3893",
      "has_links": true,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3892,
      "date": "2026-02-17T12:38:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3892",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3891,
      "date": "2026-02-17T04:57:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3891",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3890,
      "date": "2026-02-13T13:26:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3890",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3889,
      "date": "2026-02-13T10:33:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3889",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3888,
      "date": "2026-02-13T10:33:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3888",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3886,
      "date": "2026-02-10T10:38:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3886",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3885,
      "date": "2026-02-10T04:24:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3885",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3884,
      "date": "2026-02-09T20:31:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3884",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3883,
      "date": "2026-02-08T15:44:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3883",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3882,
      "date": "2026-02-06T23:27:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3882",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3881,
      "date": "2026-02-06T21:34:59+00:00",
      "source_ref": "https://t.me/tnz_msk/3881",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3880,
      "date": "2026-02-06T21:34:59+00:00",
      "source_ref": "https://t.me/tnz_msk/3880",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3879,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3879",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3878,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3878",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3877,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3877",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3876,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3876",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3875,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3875",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3874,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3874",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3873,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3873",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3872,
      "date": "2026-02-06T13:21:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3872",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3871,
      "date": "2026-02-06T07:32:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3871",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3870,
      "date": "2026-02-06T07:32:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3870",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3869,
      "date": "2026-02-06T07:32:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3869",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3868,
      "date": "2026-02-06T07:32:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3868",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3867,
      "date": "2026-02-06T03:02:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3867",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3866,
      "date": "2026-02-05T14:25:43+00:00",
      "source_ref": "https://t.me/tnz_msk/3866",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3865,
      "date": "2026-02-05T14:25:43+00:00",
      "source_ref": "https://t.me/tnz_msk/3865",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3864,
      "date": "2026-02-05T14:25:43+00:00",
      "source_ref": "https://t.me/tnz_msk/3864",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3863,
      "date": "2026-02-03T17:59:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3863",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3862,
      "date": "2026-02-03T06:54:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3862",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3861,
      "date": "2026-02-02T19:45:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3861",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3860,
      "date": "2026-02-02T19:45:56+00:00",
      "source_ref": "https://t.me/tnz_msk/3860",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3859,
      "date": "2026-01-30T08:32:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3859",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3857,
      "date": "2026-01-29T08:43:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3857",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3856,
      "date": "2026-01-29T08:43:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3856",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3855,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3855",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3854,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3854",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3853,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3853",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3852,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3852",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3851,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3851",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3850,
      "date": "2026-01-29T05:10:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3850",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3849,
      "date": "2026-01-28T15:06:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3849",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3847,
      "date": "2026-01-24T09:29:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3847",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3846,
      "date": "2026-01-24T09:29:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3846",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3845,
      "date": "2026-01-24T07:33:31+00:00",
      "source_ref": "https://t.me/tnz_msk/3845",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3844,
      "date": "2026-01-23T15:48:47+00:00",
      "source_ref": "https://t.me/tnz_msk/3844",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3843,
      "date": "2026-01-23T14:48:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3843",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3842,
      "date": "2026-01-23T14:48:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3842",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3841,
      "date": "2026-01-23T14:48:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3841",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3840,
      "date": "2026-01-22T12:52:31+00:00",
      "source_ref": "https://t.me/tnz_msk/3840",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3839,
      "date": "2026-01-22T12:32:08+00:00",
      "source_ref": "https://t.me/tnz_msk/3839",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3838,
      "date": "2026-01-22T12:32:08+00:00",
      "source_ref": "https://t.me/tnz_msk/3838",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3837,
      "date": "2026-01-22T09:56:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3837",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3836,
      "date": "2026-01-22T09:56:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3836",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3834,
      "date": "2026-01-21T16:47:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3834",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3833,
      "date": "2026-01-20T07:49:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3833",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3832,
      "date": "2026-01-19T18:20:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3832",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3831,
      "date": "2026-01-17T06:41:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3831",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3830,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3830",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3829,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3829",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3828,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3828",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3827,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3827",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3826,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3826",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3825,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3825",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3824,
      "date": "2026-01-16T10:35:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3824",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3823,
      "date": "2026-01-14T21:06:51+00:00",
      "source_ref": "https://t.me/tnz_msk/3823",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3822,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3822",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3821,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3821",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3820,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3820",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3819,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3819",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3818,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3818",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3817,
      "date": "2026-01-14T10:10:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3817",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3816,
      "date": "2026-01-07T12:59:31+00:00",
      "source_ref": "https://t.me/tnz_msk/3816",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3815,
      "date": "2026-01-06T20:23:07+00:00",
      "source_ref": "https://t.me/tnz_msk/3815",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3814,
      "date": "2026-01-06T13:50:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3814",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3813,
      "date": "2026-01-06T13:38:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3813",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3812,
      "date": "2026-01-06T12:46:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3812",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3811,
      "date": "2026-01-06T12:46:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3811",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3810,
      "date": "2026-01-06T08:23:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3810",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3809,
      "date": "2026-01-05T19:08:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3809",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3808,
      "date": "2026-01-05T17:40:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3808",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3807,
      "date": "2026-01-05T09:30:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3807",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3806,
      "date": "2026-01-05T09:30:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3806",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3805,
      "date": "2026-01-02T11:01:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3805",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3804,
      "date": "2026-01-01T21:42:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3804",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3803,
      "date": "2025-12-31T21:18:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3803",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3802,
      "date": "2025-12-31T12:52:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3802",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3800,
      "date": "2025-12-30T14:59:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3800",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3799,
      "date": "2025-12-30T07:40:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3799",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3798,
      "date": "2025-12-29T22:11:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3798",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3797,
      "date": "2025-12-29T18:21:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3797",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3796,
      "date": "2025-12-29T17:00:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3796",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3795,
      "date": "2025-12-29T12:43:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3795",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3794,
      "date": "2025-12-26T06:34:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3794",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3793,
      "date": "2025-12-24T13:03:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3793",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3792,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3792",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3791,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3791",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3790,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3790",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3789,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3789",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3788,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3788",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3787,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3787",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3786,
      "date": "2025-12-24T13:03:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3786",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3784,
      "date": "2025-12-23T15:12:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3784",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3783,
      "date": "2025-12-19T21:37:15+00:00",
      "source_ref": "https://t.me/tnz_msk/3783",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3782,
      "date": "2025-12-18T03:20:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3782",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3781,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3781",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3780,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3780",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3779,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3779",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3778,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3778",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3777,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3777",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3776,
      "date": "2025-12-17T11:57:13+00:00",
      "source_ref": "https://t.me/tnz_msk/3776",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3775,
      "date": "2025-12-16T14:25:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3775",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3774,
      "date": "2025-12-16T14:25:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3774",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3773,
      "date": "2025-12-16T14:25:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3773",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3772,
      "date": "2025-12-16T14:25:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3772",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3771,
      "date": "2025-12-16T08:59:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3771",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3770,
      "date": "2025-12-16T08:59:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3770",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3769,
      "date": "2025-12-16T08:59:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3769",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3768,
      "date": "2025-12-16T07:22:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3768",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3767,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3767",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3766,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3766",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3765,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3765",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3764,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3764",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3763,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3763",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3762,
      "date": "2025-12-15T11:28:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3762",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3761,
      "date": "2025-12-15T05:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3761",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3760,
      "date": "2025-12-13T06:14:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3760",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3759,
      "date": "2025-12-12T05:03:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3759",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3758,
      "date": "2025-12-11T09:11:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3758",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3757,
      "date": "2025-12-11T09:11:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3757",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3756,
      "date": "2025-12-11T09:11:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3756",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3755,
      "date": "2025-12-10T15:43:52+00:00",
      "source_ref": "https://t.me/tnz_msk/3755",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3754,
      "date": "2025-12-10T15:19:53+00:00",
      "source_ref": "https://t.me/tnz_msk/3754",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3753,
      "date": "2025-12-10T15:19:53+00:00",
      "source_ref": "https://t.me/tnz_msk/3753",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3752,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3752",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3751,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3751",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3750,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3750",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3749,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3749",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3748,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3748",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3747,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3747",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3746,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3746",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3745,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3745",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3744,
      "date": "2025-12-08T15:32:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3744",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3743,
      "date": "2025-12-07T08:10:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3743",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3742,
      "date": "2025-12-07T06:32:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3742",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3741,
      "date": "2025-12-06T11:16:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3741",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3740,
      "date": "2025-12-06T11:16:23+00:00",
      "source_ref": "https://t.me/tnz_msk/3740",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3739,
      "date": "2025-12-06T07:22:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3739",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3738,
      "date": "2025-12-06T07:22:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3738",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3737,
      "date": "2025-12-06T07:22:25+00:00",
      "source_ref": "https://t.me/tnz_msk/3737",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3736,
      "date": "2025-12-04T12:57:11+00:00",
      "source_ref": "https://t.me/tnz_msk/3736",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3735,
      "date": "2025-12-04T08:41:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3735",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3734,
      "date": "2025-12-03T13:38:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3734",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3733,
      "date": "2025-12-03T13:38:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3733",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3732,
      "date": "2025-12-03T13:38:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3732",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3731,
      "date": "2025-12-02T04:11:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3731",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3730,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3730",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3729,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3729",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3728,
      "date": "2025-11-29T15:29:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3728",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3727,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3727",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3726,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3726",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3725,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3725",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3724,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3724",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3723,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3723",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3722,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3722",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3721,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3721",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3720,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3720",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3719,
      "date": "2025-11-29T04:59:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3719",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3717,
      "date": "2025-11-28T14:15:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3717",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3716,
      "date": "2025-11-28T14:03:07+00:00",
      "source_ref": "https://t.me/tnz_msk/3716",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3715,
      "date": "2025-11-28T14:03:07+00:00",
      "source_ref": "https://t.me/tnz_msk/3715",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3714,
      "date": "2025-11-28T12:14:17+00:00",
      "source_ref": "https://t.me/tnz_msk/3714",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3713,
      "date": "2025-11-28T04:45:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3713",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3711,
      "date": "2025-11-27T08:33:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3711",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3710,
      "date": "2025-11-26T12:22:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3710",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3709,
      "date": "2025-11-25T18:19:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3709",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3708,
      "date": "2025-11-25T18:19:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3708",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3707,
      "date": "2025-11-25T18:19:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3707",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3706,
      "date": "2025-11-25T18:19:57+00:00",
      "source_ref": "https://t.me/tnz_msk/3706",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3701,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3701",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3700,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3700",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3699,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3699",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3698,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3698",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3697,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3697",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3696,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3696",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3695,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3695",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3694,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3694",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3693,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3693",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3692,
      "date": "2025-11-24T18:30:19+00:00",
      "source_ref": "https://t.me/tnz_msk/3692",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3691,
      "date": "2025-11-24T16:58:33+00:00",
      "source_ref": "https://t.me/tnz_msk/3691",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3690,
      "date": "2025-11-24T16:58:33+00:00",
      "source_ref": "https://t.me/tnz_msk/3690",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3681,
      "date": "2025-11-24T09:35:24+00:00",
      "source_ref": "https://t.me/tnz_msk/3681",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3680,
      "date": "2025-11-23T06:59:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3680",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3679,
      "date": "2025-11-23T06:59:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3679",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3678,
      "date": "2025-11-21T09:54:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3678",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3677,
      "date": "2025-11-21T09:54:00+00:00",
      "source_ref": "https://t.me/tnz_msk/3677",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3675,
      "date": "2025-11-20T16:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3675",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3674,
      "date": "2025-11-20T16:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3674",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3673,
      "date": "2025-11-20T16:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3673",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3672,
      "date": "2025-11-20T16:47:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3672",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3671,
      "date": "2025-11-20T16:29:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3671",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3670,
      "date": "2025-11-20T16:29:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3670",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3669,
      "date": "2025-11-20T08:24:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3669",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3668,
      "date": "2025-11-20T08:23:53+00:00",
      "source_ref": "https://t.me/tnz_msk/3668",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3667,
      "date": "2025-11-18T14:50:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3667",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3666,
      "date": "2025-11-18T14:50:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3666",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3665,
      "date": "2025-11-18T14:50:10+00:00",
      "source_ref": "https://t.me/tnz_msk/3665",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3664,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3664",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3663,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3663",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3662,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3662",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3661,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3661",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3660,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3660",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3659,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3659",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3658,
      "date": "2025-11-18T14:50:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3658",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3657,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3657",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3656,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3656",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3655,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3655",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3654,
      "date": "2025-11-17T15:33:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3654",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3653,
      "date": "2025-11-17T07:48:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3653",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3652,
      "date": "2025-11-17T07:48:28+00:00",
      "source_ref": "https://t.me/tnz_msk/3652",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3651,
      "date": "2025-11-13T16:14:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3651",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3650,
      "date": "2025-11-13T16:14:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3650",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3649,
      "date": "2025-11-12T18:37:09+00:00",
      "source_ref": "https://t.me/tnz_msk/3649",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3648,
      "date": "2025-11-12T16:22:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3648",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3647,
      "date": "2025-11-11T07:19:54+00:00",
      "source_ref": "https://t.me/tnz_msk/3647",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3646,
      "date": "2025-11-11T06:38:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3646",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3645,
      "date": "2025-11-11T04:11:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3645",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3644,
      "date": "2025-11-10T16:11:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3644",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3643,
      "date": "2025-11-10T16:11:50+00:00",
      "source_ref": "https://t.me/tnz_msk/3643",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3642,
      "date": "2025-11-10T13:38:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3642",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3641,
      "date": "2025-11-10T13:38:27+00:00",
      "source_ref": "https://t.me/tnz_msk/3641",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3640,
      "date": "2025-11-10T13:38:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3640",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3639,
      "date": "2025-11-10T13:38:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3639",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3638,
      "date": "2025-11-10T13:38:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3638",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3637,
      "date": "2025-11-10T13:38:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3637",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3635,
      "date": "2025-11-09T04:38:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3635",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3634,
      "date": "2025-11-08T06:53:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3634",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3633,
      "date": "2025-11-08T06:53:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3633",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3632,
      "date": "2025-11-08T06:53:11+00:00",
      "source_ref": "https://t.me/tnz_msk/3632",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3631,
      "date": "2025-11-08T04:06:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3631",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3630,
      "date": "2025-11-07T14:37:49+00:00",
      "source_ref": "https://t.me/tnz_msk/3630",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3629,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3629",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3628,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3628",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3627,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3627",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3626,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3626",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3625,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3625",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3624,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3624",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3623,
      "date": "2025-11-06T09:58:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3623",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3622,
      "date": "2025-11-06T08:10:44+00:00",
      "source_ref": "https://t.me/tnz_msk/3622",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3621,
      "date": "2025-11-05T18:41:26+00:00",
      "source_ref": "https://t.me/tnz_msk/3621",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3620,
      "date": "2025-11-05T17:40:07+00:00",
      "source_ref": "https://t.me/tnz_msk/3620",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3619,
      "date": "2025-11-05T14:24:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3619",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3618,
      "date": "2025-11-05T14:24:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3618",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3617,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3617",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3616,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3616",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3615,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3615",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3614,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3614",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3613,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3613",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3612,
      "date": "2025-11-05T12:27:55+00:00",
      "source_ref": "https://t.me/tnz_msk/3612",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3611,
      "date": "2025-11-05T10:44:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3611",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3610,
      "date": "2025-11-05T10:44:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3610",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3609,
      "date": "2025-11-05T10:44:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3609",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3608,
      "date": "2025-11-05T10:44:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3608",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3607,
      "date": "2025-11-05T10:44:20+00:00",
      "source_ref": "https://t.me/tnz_msk/3607",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3606,
      "date": "2025-11-04T10:20:21+00:00",
      "source_ref": "https://t.me/tnz_msk/3606",
      "has_links": false,
      "has_file": false,
      "media_type": null
    },
    {
      "message_id": 3605,
      "date": "2025-11-04T09:39:08+00:00",
      "source_ref": "https://t.me/tnz_msk/3605",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3604,
      "date": "2025-11-03T09:45:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3604",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3602,
      "date": "2025-11-02T09:08:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3602",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3601,
      "date": "2025-11-02T09:08:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3601",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3600,
      "date": "2025-11-02T09:08:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3600",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3599,
      "date": "2025-11-02T09:08:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3599",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3598,
      "date": "2025-11-02T09:08:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3598",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3597,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3597",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3596,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3596",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3595,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3595",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3594,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3594",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3593,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3593",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3592,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3592",
      "has_links": false,
      "has_file": false,
      "media_type": "document"
    },
    {
      "message_id": 3591,
      "date": "2025-10-31T06:12:32+00:00",
      "source_ref": "https://t.me/tnz_msk/3591",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3590,
      "date": "2025-10-30T19:29:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3590",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3589,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3589",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3588,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3588",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3587,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3587",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3586,
      "date": "2025-10-28T11:59:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3586",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3585,
      "date": "2025-10-27T16:28:38+00:00",
      "source_ref": "https://t.me/tnz_msk/3585",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3584,
      "date": "2025-10-27T11:40:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3584",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3583,
      "date": "2025-10-26T04:45:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3583",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3582,
      "date": "2025-10-26T04:45:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3582",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3581,
      "date": "2025-10-26T04:45:04+00:00",
      "source_ref": "https://t.me/tnz_msk/3581",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3580,
      "date": "2025-10-25T04:16:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3580",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3579,
      "date": "2025-10-24T16:00:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3579",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3578,
      "date": "2025-10-24T16:00:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3578",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3577,
      "date": "2025-10-24T16:00:05+00:00",
      "source_ref": "https://t.me/tnz_msk/3577",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3576,
      "date": "2025-10-24T15:58:30+00:00",
      "source_ref": "https://t.me/tnz_msk/3576",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3573,
      "date": "2025-10-24T12:58:37+00:00",
      "source_ref": "https://t.me/tnz_msk/3573",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3572,
      "date": "2025-10-24T09:16:06+00:00",
      "source_ref": "https://t.me/tnz_msk/3572",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3571,
      "date": "2025-10-24T03:39:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3571",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3569,
      "date": "2025-10-23T04:06:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3569",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3568,
      "date": "2025-10-22T16:59:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3568",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3567,
      "date": "2025-10-22T16:59:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3567",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3566,
      "date": "2025-10-22T16:59:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3566",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3565,
      "date": "2025-10-22T16:59:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3565",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3564,
      "date": "2025-10-22T16:59:48+00:00",
      "source_ref": "https://t.me/tnz_msk/3564",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3563,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3563",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3562,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3562",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3561,
      "date": "2025-10-22T13:51:42+00:00",
      "source_ref": "https://t.me/tnz_msk/3561",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3560,
      "date": "2025-10-22T07:18:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3560",
      "has_links": true,
      "has_file": false,
      "media_type": "webpage"
    },
    {
      "message_id": 3559,
      "date": "2025-10-22T04:06:58+00:00",
      "source_ref": "https://t.me/tnz_msk/3559",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3558,
      "date": "2025-10-21T12:40:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3558",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3557,
      "date": "2025-10-21T12:40:46+00:00",
      "source_ref": "https://t.me/tnz_msk/3557",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3556,
      "date": "2025-10-21T12:40:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3556",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3555,
      "date": "2025-10-21T12:40:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3555",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3554,
      "date": "2025-10-21T12:40:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3554",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3553,
      "date": "2025-10-21T12:40:45+00:00",
      "source_ref": "https://t.me/tnz_msk/3553",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3551,
      "date": "2025-10-21T08:47:52+00:00",
      "source_ref": "https://t.me/tnz_msk/3551",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3550,
      "date": "2025-10-20T20:02:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3550",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3549,
      "date": "2025-10-20T20:02:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3549",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3548,
      "date": "2025-10-20T20:02:12+00:00",
      "source_ref": "https://t.me/tnz_msk/3548",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3547,
      "date": "2025-10-20T16:58:36+00:00",
      "source_ref": "https://t.me/tnz_msk/3547",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3546,
      "date": "2025-10-20T13:39:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3546",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3545,
      "date": "2025-10-20T13:39:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3545",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3544,
      "date": "2025-10-20T13:39:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3544",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3543,
      "date": "2025-10-20T13:39:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3543",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3542,
      "date": "2025-10-20T13:39:22+00:00",
      "source_ref": "https://t.me/tnz_msk/3542",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3541,
      "date": "2025-10-20T10:15:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3541",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3540,
      "date": "2025-10-20T10:15:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3540",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3539,
      "date": "2025-10-20T10:15:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3539",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3538,
      "date": "2025-10-20T10:15:40+00:00",
      "source_ref": "https://t.me/tnz_msk/3538",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3537,
      "date": "2025-10-18T09:48:03+00:00",
      "source_ref": "https://t.me/tnz_msk/3537",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3536,
      "date": "2025-10-17T14:52:29+00:00",
      "source_ref": "https://t.me/tnz_msk/3536",
      "has_links": false,
      "has_file": true,
      "media_type": "document"
    },
    {
      "message_id": 3535,
      "date": "2025-10-17T09:09:01+00:00",
      "source_ref": "https://t.me/tnz_msk/3535",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    },
    {
      "message_id": 3534,
      "date": "2025-10-17T07:08:28+00:00",
      "source_ref": "https://t.me/tnz_msk/3534",
      "has_links": false,
      "has_file": false,
      "media_type": "photo"
    }
  ]
}
====================================================================================================
END_FILE: docs/TECHNADZOR/source_skills/tnz_msk/SOURCE_INDEX.json
FILE_CHUNK: 1/1
====================================================================================================
