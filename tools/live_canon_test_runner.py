#!/usr/bin/env python3
# === LIVE_CANON_TEST_RUNNER_V1 ===
from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
REPORT = BASE / "docs/REPORTS/LIVE_CANON_TEST_REPORT.md"

# === LIVE_CANON_TEST_RUNNER_PYTHONPATH_FIX_V1 ===
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
# === END_LIVE_CANON_TEST_RUNNER_PYTHONPATH_FIX_V1 ===

def ok(name, value):
    return {"name": name, "ok": bool(value), "value": value}

async def main():
    checks = []

    from core.engine_contract import validate_engine_result
    checks.append(ok("UNIFIED_ENGINE_RESULT_VALIDATOR_BAD", not validate_engine_result("файл скачан", input_type="drive_file").get("ok")))
    checks.append(ok("UNIFIED_ENGINE_RESULT_VALIDATOR_GOOD", validate_engine_result({"summary": "PDF создан", "drive_link": "https://drive.google.com/test"}, input_type="drive_file").get("ok")))

    from core.format_registry import classify_file
    checks.append(ok("DWG_KIND_DRAWING", classify_file("a.dwg").get("kind") == "drawing"))
    checks.append(ok("DXF_KIND_DRAWING", classify_file("a.dxf").get("kind") == "drawing"))
    checks.append(ok("HF_KIND_BINARY", classify_file("a.hf").get("kind") == "binary"))

    from core.template_workflow import _load_index
    checks.append(ok("TEMPLATE_INDEX_LOAD", isinstance(_load_index(), dict)))

    from core.normative_source_engine import search_normative_sources
    checks.append(ok("NORMATIVE_SOURCE_SEARCH", len(search_normative_sources("трещина бетон")) >= 1))

    from core.capability_router_dispatch import build_execution_plan
    checks.append(ok("CAPABILITY_ESTIMATE", build_execution_plan(user_text="смета xlsx").get("engine") == "estimate"))
    checks.append(ok("CAPABILITY_DWG", build_execution_plan(file_name="a.dwg").get("engine") == "dwg_project"))

    passed = sum(1 for c in checks if c["ok"])
    total = len(checks)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "# LIVE_CANON_TEST_REPORT\n\n"
        + f"created_at: {datetime.now(timezone.utc).isoformat()}\n"
        + f"passed: {passed}/{total}\n\n"
        + "\n".join(f"- [{'OK' if c['ok'] else 'FAIL'}] {c['name']} | {c['value']}" for c in checks)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": passed == total, "passed": passed, "total": total, "report": str(REPORT)}, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
# === END_LIVE_CANON_TEST_RUNNER_V1 ===
