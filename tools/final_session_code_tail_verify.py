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
