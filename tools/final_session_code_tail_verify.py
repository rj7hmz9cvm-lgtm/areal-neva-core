#!/usr/bin/env python3
# === FINAL_SESSION_CODE_TAIL_VERIFY_V3 ===
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
    "core/price_enrichment.py": [
        "PRICE_DECISION_BEFORE_WEB_SEARCH_V1",
        "prehandle_price_task_v1",
        "_base_prehandle_price_task_v1",
    ],
    "core/file_context_intake.py": [
        "PENDING_INTENT_CLARIFICATION_V1",
        "CONTEXT_AWARE_FILE_INTAKE_V1",
        "MULTI_FILE_TEMPLATE_INTAKE_V1",
        "TELEGRAM_FILE_MEMORY_INDEX_V1",
    ],
    "core/final_closure_engine.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_ENGINE",
        "maybe_handle_final_closure",
    ],
    "core/model_router.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_MODEL_ROUTER",
        "detect_domain",
    ],
    "core/runtime_file_catalog.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG",
    ],
    "core/archive_guard.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_ARCHIVE_DUPLICATE_GUARD",
    ],
    "core/technadzor_engine.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_TECHNADZOR_ENGINE",
    ],
    "core/ocr_engine.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_OCR_TABLE_ENGINE",
    ],
    "core/estimate_engine.py": [
        "create_estimate_xlsx_from_rows",
    ],
}


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=str(BASE), text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return "ERROR: " + str(e)


def read(rel: str) -> str:
    p = BASE / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def line_no(rel: str, needle: str) -> int:
    for i, line in enumerate(read(rel).splitlines(), 1):
        if needle in line:
            return i
    return -1


def marker_check() -> dict:
    out = {}
    for rel, markers in REQUIRED_MARKERS.items():
        txt = read(rel)
        missing = [m for m in markers if m not in txt]
        out[rel] = {"exists": bool(txt), "missing": missing, "ok": bool(txt) and not missing}
    return out


def public_def_count(rel: str, prefix: str) -> int:
    return sum(1 for line in read(rel).splitlines() if line.startswith(prefix))


def exact_bad_import_present(import_line: str, files: list[str]) -> bool:
    return any(import_line in read(x) for x in files)


def smoke_check() -> dict:
    res = {}

    from core.model_router import detect_domain
    router_cases = {
        "estimate": detect_domain("сделай смету по образцу").get("domain"),
        "estimate_inflected": detect_domain("сделай смету").get("domain"),
        "technadzor": detect_domain("сделай акт технадзора").get("domain"),
        "memory": detect_domain("какие файлы я скидывал").get("domain"),
        "project": detect_domain("сделай проект КЖ плиты").get("domain"),
    }
    res["router_cases"] = router_cases
    res["router_ok"] = (
        router_cases["estimate"] == "estimate"
        and router_cases["estimate_inflected"] == "estimate"
        and router_cases["technadzor"] == "technadzor"
        and router_cases["memory"] == "memory"
        and router_cases["project"] == "project"
    )

    from core.price_enrichment import prehandle_price_task_v1
    fake_task = {
        "id": "verify_price_task",
        "chat_id": "-1003725299009",
        "topic_id": 2,
        "input_type": "text",
        "raw_input": "сделай смету по образцу",
    }
    price_res = asyncio.run(prehandle_price_task_v1(sqlite3.connect(":memory:"), fake_task))
    res["price_function_exists"] = callable(prehandle_price_task_v1)
    res["price_function_result_type_ok"] = price_res is None or isinstance(price_res, dict)

    from core.final_closure_engine import maybe_handle_final_closure
    mem_conn = sqlite3.connect(str(CORE_DB))
    mem_conn.row_factory = sqlite3.Row
    try:
        mem_res = maybe_handle_final_closure(
            mem_conn,
            {
                "id": "verify_final_closure_task",
                "chat_id": "-1003725299009",
                "topic_id": 2,
                "input_type": "text",
                "raw_input": "какие файлы я скидывал",
            },
            "verify_final_closure_task",
            "-1003725299009",
            2,
            "какие файлы я скидывал",
            "text",
            None,
        )
    finally:
        mem_conn.close()
    res["final_closure_memory_ok"] = bool(mem_res and mem_res.get("handled"))

    from core.estimate_engine import create_estimate_xlsx_from_rows
    res["estimate_xlsx_function_ok"] = callable(create_estimate_xlsx_from_rows)

    return res


def main() -> None:
    verify_files = [
        "tools/final_session_code_tail_verify.py",
        "tools/live_tech_contour_verify.py",
    ]

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
        },
        "forbidden": {
            "telegram_daemon_dirty": bool(run(["git", "status", "--short", "--", "telegram_daemon.py"])),
            "final_closure_has_voice_handler_def": (
                "def handle_voice_confirm" in read("core/final_closure_engine.py")
                or "def voice_confirm" in read("core/final_closure_engine.py")
            ),
            "wrong_route_import": exact_bad_import_present(BAD_ROUTE_IMPORT, verify_files),
            "wrong_final_closure_import": exact_bad_import_present(BAD_FINAL_IMPORT, verify_files),
            "wrong_price_symbol": any(
                BAD_PRICE_SYMBOL in read(x)
                for x in verify_files + ["core/price_enrichment.py"]
            ),
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
    )
    report["forbidden_ok"] = not any(report["forbidden"].values())
    report["smoke_ok"] = (
        report["smoke"]["router_ok"]
        and report["smoke"]["price_function_exists"]
        and report["smoke"]["price_function_result_type_ok"]
        and report["smoke"]["final_closure_memory_ok"]
        and report["smoke"]["estimate_xlsx_function_ok"]
    )
    report["status"] = "OK" if report["markers_ok"] and report["hook_order_ok"] and report["counts_ok"] and report["forbidden_ok"] and report["smoke_ok"] else "FAILED"

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# FINAL_SESSION_CODE_TAIL_VERIFY_REPORT",
        "",
        f"generated_at: {report['generated_at']}",
        f"status: {report['status']}",
        f"markers_ok: {report['markers_ok']}",
        f"hook_order_ok: {report['hook_order_ok']}",
        f"counts_ok: {report['counts_ok']}",
        f"forbidden_ok: {report['forbidden_ok']}",
        f"smoke_ok: {report['smoke_ok']}",
        "",
        "## RAW_JSON",
        "```json",
        json.dumps(report, ensure_ascii=False, indent=2),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("FINAL_SESSION_CODE_TAIL_VERIFY_REPORT", REPORT)
    print("STATUS", report["status"])

    if report["status"] != "OK":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
# === END_FINAL_SESSION_CODE_TAIL_VERIFY_V3 ===
