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
