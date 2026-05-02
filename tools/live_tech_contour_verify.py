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
