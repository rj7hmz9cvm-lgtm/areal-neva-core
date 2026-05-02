# === FINAL_CLOSURE_BLOCKER_FIX_V1_TECHNADZOR_ENGINE ===
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "outputs" / "technadzor"
OUT.mkdir(parents=True, exist_ok=True)


def is_technadzor_intent(text: str = "", file_name: str = "") -> bool:
    t = f"{text} {file_name}".lower().replace("ё", "е")
    return bool(re.search(r"\b(акт|технадзор|техническ.*надзор|дефект|замечан|нарушен|освидетельств|стройконтроль|сп|гост|снип)\b", t))


def _norm_refs(text: str) -> str:
    refs = []
    for m in re.findall(r"\b(сп\s*\d+[.\d]*|гост\s*\d+[.\d-]*|снип\s*[\w.\-]+)\b", text or "", flags=re.I):
        refs.append(m.upper().replace("  ", " "))
    return ", ".join(sorted(set(refs))) if refs else "Норма не подтверждена"


def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "") -> Dict[str, Any]:
    if not is_technadzor_intent(text, file_name):
        return {"ok": False, "handled": False, "reason": "NOT_TECHNADZOR"}

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"TECHNADZOR_ACT__{task_id[:8] or ts}"
    txt_path = OUT / f"{stem}.txt"

    body = [
        "АКТ ТЕХНИЧЕСКОГО НАДЗОРА",
        "",
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Задача: {task_id}",
        f"Топик: {topic_id}",
    ]

    if file_name:
        body.append(f"Файл: {file_name}")

    body.extend(
        [
            "",
            "Исходное описание:",
            (text or "").strip() or "UNKNOWN",
            "",
            "Нормативная база:",
            _norm_refs(text),
            "",
            "Вывод:",
            "Черновик акта создан. Если норматив не подтверждён источником, в акте указано: Норма не подтверждена",
        ]
    )

    txt_path.write_text("\n".join(body) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "handled": True,
        "kind": "technadzor_act",
        "state": "DONE",
        "artifact_path": str(txt_path),
        "message": f"Технадзорный акт подготовлен\nФайл: {txt_path}",
        "history": "FINAL_CLOSURE_BLOCKER_FIX_V1:TECHNADZOR_ACT_CREATED",
    }


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_TECHNADZOR_ENGINE ===
