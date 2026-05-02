# === FINAL_CLOSURE_BLOCKER_FIX_V1_OCR_TABLE_ENGINE ===
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "outputs" / "ocr"
OUT.mkdir(parents=True, exist_ok=True)


def is_ocr_table_intent(text: str = "", file_name: str = "") -> bool:
    t = f"{text} {file_name}".lower().replace("ё", "е")
    return any(x in t for x in ["таблиц", "распознай", "ocr", "скан", "фото таблицы", "в excel", "в эксель"])


def process_ocr_table(text: str = "", task_id: str = "", file_path: str = "", file_name: str = "") -> Dict[str, Any]:
    if not is_ocr_table_intent(text, file_name):
        return {"ok": False, "handled": False, "reason": "NOT_OCR_TABLE"}

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = OUT / f"OCR_TABLE__{task_id[:8] or ts}.csv"
    rows: List[List[str]] = [["status", "message"], ["FAILED", "OCR_TABLE_REQUIRES_REAL_RECOGNITION_ENGINE"]]

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)

    return {
        "ok": True,
        "handled": True,
        "kind": "ocr_table",
        "state": "FAILED",
        "artifact_path": str(csv_path),
        "message": "OCR таблицы не выполнен: реальный OCR-движок не подключён\nСоздан диагностический CSV\nБез распознавания структура таблицы не выдумывается",
        "history": "FINAL_CLOSURE_BLOCKER_FIX_V1:OCR_REQUIRES_ENGINE",
    }


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_OCR_TABLE_ENGINE ===
