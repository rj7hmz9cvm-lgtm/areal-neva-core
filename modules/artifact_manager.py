from __future__ import annotations

import datetime
import hashlib
from pathlib import Path

BASE_DIR = Path("/root/AI_ORCHESTRA/artifacts")

def save_artifact(task_id, data, ext="txt", prefix="result"):
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    h = hashlib.md5(f"{task_id}_{ts}".encode()).hexdigest()[:6]
    path = BASE_DIR / f"{prefix}_{ts}_{h}.{ext.strip('.')}"
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(str(data), encoding="utf-8")
    return str(path)
