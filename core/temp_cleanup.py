# === TEMP_CLEANUP_V1 ===
import os, logging, glob
from pathlib import Path
logger = logging.getLogger(__name__)

TEMP_DIRS = ["/tmp", "/root/.areal-neva-core/data/temp"]

def cleanup_file(path: str) -> bool:
    try:
        if path and os.path.exists(path):
            os.remove(path)
            logger.info("TEMP_CLEANED path=%s", path)
            return True
    except Exception as e:
        logger.warning("TEMP_CLEANUP_ERR path=%s err=%s", path, e)
    return False

def cleanup_task_temps(task_id: str) -> int:
    """Удалить все temp файлы связанные с task_id"""
    count = 0
    for d in TEMP_DIRS:
        if not os.path.exists(d):
            continue
        for f in glob.glob(f"{d}/*{task_id}*"):
            if cleanup_file(f):
                count += 1
    return count

def cleanup_after_upload(local_paths: list) -> int:
    count = 0
    for p in (local_paths or []):
        if p and isinstance(p, str) and "/tmp" in p:
            if cleanup_file(p):
                count += 1
    return count
# === END TEMP_CLEANUP_V1 ===
