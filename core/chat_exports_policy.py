# === CHAT_EXPORTS_DEDUP_POLICY_V1 ===
# Канонический источник: chat_exports/ (lowercase)
# CHAT_EXPORTS/ — legacy, не удалять, но игнорировать в агрегаторе
import os, logging
from pathlib import Path
logger = logging.getLogger(__name__)

BASE = Path("/root/.areal-neva-core")
CANONICAL_DIR = BASE / "chat_exports"
LEGACY_DIR = BASE / "CHAT_EXPORTS"

def get_canonical_exports_dir() -> Path:
    return CANONICAL_DIR

def list_canonical_exports() -> list:
    if not CANONICAL_DIR.exists():
        return []
    return sorted(CANONICAL_DIR.rglob("*.json")) + sorted(CANONICAL_DIR.rglob("*.txt"))

def is_legacy_dir(path: str) -> bool:
    return "CHAT_EXPORTS" in str(path) and "chat_exports" not in str(path).lower().replace("CHAT_EXPORTS","")

def dedup_export_files(files: list) -> list:
    """Убрать дубли — если файл есть в обоих dirs, брать из canonical"""
    seen_names = set()
    result = []
    # Сначала canonical
    canonical = [f for f in files if CANONICAL_DIR.name in str(f) and not is_legacy_dir(str(f))]
    legacy = [f for f in files if is_legacy_dir(str(f))]
    for f in canonical:
        seen_names.add(Path(f).name)
        result.append(f)
    for f in legacy:
        if Path(f).name not in seen_names:
            result.append(f)
    return result
# === END CHAT_EXPORTS_DEDUP_POLICY_V1 ===
