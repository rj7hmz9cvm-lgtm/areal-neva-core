# === STARTUP_RECOVERY_V1 ===
from __future__ import annotations

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger("startup_recovery")

def _utc_cutoff(minutes: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(minutes=int(minutes))).replace(tzinfo=None).isoformat(sep=" ")

def _cols(conn: sqlite3.Connection, table: str) -> list[str]:
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except Exception:
        return []

async def run_startup_recovery(db_path: str, stale_minutes: int = 5) -> int:
    await asyncio.sleep(0)
    conn = sqlite3.connect(str(db_path), timeout=20)
    conn.row_factory = sqlite3.Row
    reset_count = 0

    try:
        cols = _cols(conn, "tasks")
        if "state" not in cols or "id" not in cols:
            logger.warning("STARTUP_RECOVERY_V1_NO_TASK_SCHEMA")
            return 0

        time_col = "updated_at" if "updated_at" in cols else ("created_at" if "created_at" in cols else "")
        if not time_col:
            logger.warning("STARTUP_RECOVERY_V1_NO_TIME_COLUMN")
            return 0

        cutoff = _utc_cutoff(stale_minutes)
        rows = conn.execute(
            f"SELECT id FROM tasks WHERE state='IN_PROGRESS' AND COALESCE({time_col}, '') < ?",
            (cutoff,),
        ).fetchall()

        for row in rows:
            task_id = str(row["id"])
            if "error_message" in cols:
                conn.execute(
                    "UPDATE tasks SET state='NEW', error_message=NULL, updated_at=datetime('now') WHERE id=?",
                    (task_id,),
                )
            else:
                conn.execute(
                    "UPDATE tasks SET state='NEW', updated_at=datetime('now') WHERE id=?",
                    (task_id,),
                )

            try:
                conn.execute(
                    "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                    (task_id, "STARTUP_RECOVERY_RESET"),
                )
            except Exception:
                pass

            logger.info("STARTUP_RECOVERY_RESET task_id=%s", task_id)
            reset_count += 1

        conn.commit()
        logger.info("STARTUP_RECOVERY_V1_DONE reset_count=%s", reset_count)
        return reset_count
    finally:
        conn.close()

# === END_STARTUP_RECOVERY_V1 ===

# === RUNTIME_PATCHES_V1 ===
# Patches task_worker module-level functions that must be fixed but can't be
# reached by appending to task_worker.py (which blocks at asyncio.run()).
# run_startup_recovery is called from inside main() after full module load.
import sys as _rp_sys
import re as _rp_re
import logging as _rp_logging

_rp_log = _rp_logging.getLogger("startup_recovery")


def _rp_get_tw():
    return _rp_sys.modules.get("__main__") or _rp_sys.modules.get("task_worker")


def _install_runtime_patches():
    tw = _rp_get_tw()
    if tw is None:
        _rp_log.warning("RUNTIME_PATCHES_V1: task_worker not in sys.modules")
        return

    # --- Patch A: _p6e2_tw_estimate_like ---
    # Original only checks "смет/расчет/посчитай/стоимость/полная смета".
    # Fix: also detect construction photos by params (dims + material/object).
    if hasattr(tw, "_p6e2_tw_estimate_like"):
        def _new_p6e2_tw_estimate_like(text):
            low = str(text or "").lower().replace("ё", "е")
            if any(x in low for x in (
                "смет", "расчет", "расчёт", "посчитай", "стоимость", "полная смета",
                "посчитать", "рассчитать", "стоить", "стоит", "нужна смета",
                "сколько будет", "цена", "нужен расчет",
            )):
                return True
            has_dims = bool(_rp_re.search(
                r"\d+[.,]?\d*\s*(?:x|х|×|\*|на)\s*\d+|\d+[.,]?\d*\s*м\b|\bвысот",
                low,
            ))
            has_material = any(x in low for x in (
                "каркас", "газобетон", "кирпич", "монолит", "арболит",
                "фундамент", "кровл", "фальц", "клик", "металлочереп",
            ))
            has_object = any(x in low for x in (
                "дом", "ангар", "склад", "баня", "гараж", "здани", "объект",
            ))
            has_construction = any(x in low for x in (
                "высота", "этаж", "площадь", "стен", "плита", "подушк", "технологи",
            ))
            if (has_dims or has_material) and (has_object or has_construction):
                return True
            return False
        tw._p6e2_tw_estimate_like = _new_p6e2_tw_estimate_like
        _rp_log.info("RUNTIME_PATCHES_V1: _p6e2_tw_estimate_like patched OK")
    else:
        _rp_log.warning("RUNTIME_PATCHES_V1: _p6e2_tw_estimate_like not found")

    # --- Patch B: _p6_bad_search_result_20260504 ---
    # Original blocks results without URLs/prices — but "Нет подходящих..." is valid.
    if hasattr(tw, "_p6_bad_search_result_20260504"):
        _rp_orig_bad = tw._p6_bad_search_result_20260504

        def _new_bad_search(result, raw_input):
            low = str(result or "").lower().replace("ё", "е")
            if any(x in low for x in (
                "нет подход", "не найден", "не нашел", "не нашёл",
                "ничего не", "нет предложен", "нет вариант",
                "нет информации", "нет данных", "не удалось найти",
            )):
                return False
            return _rp_orig_bad(result, raw_input)

        tw._p6_bad_search_result_20260504 = _new_bad_search
        _rp_log.info("RUNTIME_PATCHES_V1: _p6_bad_search_result_20260504 patched OK")
    else:
        _rp_log.warning("RUNTIME_PATCHES_V1: _p6_bad_search_result_20260504 not found")


_rp_orig_run_startup_recovery = run_startup_recovery


async def run_startup_recovery(db_path: str, stale_minutes: int = 5) -> int:
    result = await _rp_orig_run_startup_recovery(db_path, stale_minutes)
    try:
        _install_runtime_patches()
    except Exception as _rp_e:
        _rp_log.warning("RUNTIME_PATCHES_V1_ERR: %s", _rp_e)
    return result
# === END_RUNTIME_PATCHES_V1 ===
