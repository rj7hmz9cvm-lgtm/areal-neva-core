# ORCHESTRA_FULL_CONTEXT_PART_008
generated_at_utc: 2026-05-03T09:38:37.245997+00:00
git_sha_before_commit: f78f74d5aeee627b64b7644a495a729ba8d56a98
part: 8/11


====================================================================================================
BEGIN_FILE: task_worker.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 26cb58a7f8ea21d73572638e92c0063cf445c0eacf2d3e6d5bdd279d371d0d61
====================================================================================================

def _force_voice_finish(raw_input: str, result: str) -> bool:
    if not raw_input:
        return False
    low = raw_input.lower()
    if any(x in low for x in ["заверш", "доволен", "да", "ок", "ok"]):
        if "не доволен" in low:
            return False
        return True
    return False

import os
BASE = "/root/.areal-neva-core"

import re
import time
import json
import sqlite3
import asyncio
import hashlib
import datetime
import logging
def now_iso_utc() -> str:
    """UTC_TIMESTAMP_V1"""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

import fcntl
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from core.ai_router import process_ai_task
try:
    from startup_recovery import run_startup_recovery  # STARTUP_RECOVERY_V1_WIRED
except Exception as _startup_recovery_import_err:
    run_startup_recovery = None

# === CANON_REMAINING_CODE_FULL_CLOSE_V1_IMPORT ===
try:
    from core.engine_contract import validate_engine_result, result_to_user_text
    from core.active_dialog_state import maybe_handle_active_dialog, save_dialog_event
    from core.template_workflow import maybe_handle_template_workflow
except Exception as _canon_import_err:
    validate_engine_result = None
    result_to_user_text = None
    maybe_handle_active_dialog = None
    save_dialog_event = None
    maybe_handle_template_workflow = None
# === END_CANON_REMAINING_CODE_FULL_CLOSE_V1_IMPORT ===
# === REAL_GAPS_CLOSE_V2_IMPORT_ASYNC_TEMPLATE ===
try:
    from core.template_workflow import maybe_handle_template_workflow_async
except Exception:
    maybe_handle_template_workflow_async = None
# === END_REAL_GAPS_CLOSE_V2_IMPORT_ASYNC_TEMPLATE ===
# === SEARCH_MONOLITH_V2_TASK_WORKER_IMPORT ===
try:
    from core.search_session import is_search_clarification_output as _search_v2_is_clarification
except Exception:
    _search_v2_is_clarification = lambda text: False
# === END SEARCH_MONOLITH_V2_TASK_WORKER_IMPORT ===
# === FILE_TECH_CONTOUR_FULL_CLOSE_V1_IMPORT ===
try:
    from core.file_memory_bridge import (
        should_handle_file_followup as _filemem_should_followup,
        build_file_followup_answer as _filemem_build_answer,
        is_service_file as _filemem_is_service_file,
        save_file_catalog_snapshot as _filemem_save_catalog,
    )
except Exception:
    _filemem_should_followup = lambda text: False
    _filemem_build_answer = lambda *a, **kw: None
    _filemem_is_service_file = lambda *a, **kw: False
    _filemem_save_catalog = lambda *a, **kw: {"ok": False}
# === END FILE_TECH_CONTOUR_FULL_CLOSE_V1_IMPORT ===
try:
    from core.topic_meta_loader import load_topic_meta, is_what_is_this_question, build_topic_self_answer
    TOPIC_META_LOADER_WIRED = True
except Exception:
    TOPIC_META_LOADER_WIRED = False
    def load_topic_meta(t): return None
    def is_what_is_this_question(t): return False
    def build_topic_self_answer(m): return ""
# TOPIC_META_LOADER_V1_IMPORT
from core.reply_sender import send_reply, send_reply_ex
try:
    from core.template_engine_v1 import is_template_request as _tpl_check, get_template as _tpl_get, save_template as _tpl_save, apply_template_to_xlsx as _tpl_apply  # TEMPLATE_ENGINE_V1_WIRED
except Exception:
    _tpl_check = lambda t: False
    _tpl_get = lambda *a: None
    _tpl_save = lambda *a: False
    _tpl_apply = lambda *a: False
try:
    from core.topic_3008_engine import is_topic_3008 as _t3_check, detect_command as _t3_cmd, extract_code as _t3_extract, verify_code as _t3_verify, generate_code as _t3_generate  # TOPIC_3008_V1_WIRED
except Exception:
    _t3_check = lambda t: False
    _t3_cmd = lambda t: "none"
    _t3_extract = lambda t: t
    _t3_verify = None
    _t3_generate = None
try:
    from core.temp_cleanup import cleanup_file as _tc_file, cleanup_task_temps as _tc_task, cleanup_after_upload as _tc_upload  # TEMP_CLEANUP_V1_WIRED
except Exception:
    _tc_file = lambda p: False
    _tc_task = lambda t: 0
    _tc_upload = lambda l: 0
try:
    from core.technadzor_engine import process_technadzor as _te_process, is_technadzor_intent as _te_intent  # TECHNADZOR_ENGINE_V1_WIRED
except Exception:
    _te_process = lambda *a, **kw: {"ok": False, "result_text": "", "artifact": None, "error_code": "IMPORT_FAIL"}
    _te_intent = lambda *a: False
try:
    from core.intake_offer_actions import needs_offer as _ioa_needs, get_offer_text as _ioa_text, parse_offer_reply as _ioa_parse  # INTAKE_OFFER_V1_WIRED
except Exception:
    _ioa_needs = lambda *a: False
    _ioa_text = lambda: ""
    _ioa_parse = lambda r: ""
try:
    from core.search_session import get_session as _ss_get, create_session as _ss_create, update_session as _ss_update, extract_criteria as _ss_criteria  # SEARCH_SESSION_V1_WIRED
except Exception:
    _ss_get = lambda *a: None
    _ss_create = lambda *a, **kw: {}
    _ss_update = lambda *a, **kw: None
    _ss_criteria = lambda t: {}
try:
    from core.output_decision import format_task_result as _od_format, format_search_output as _od_search  # OUTPUT_DECISION_V1_WIRED
except Exception:
    _od_format = lambda r, s, **kw: r
    _od_search = lambda o, **kw: str(o)
try:
    from core.inbox_aggregator import normalize_inbox_item as _ia_norm, should_create_task as _ia_should  # INBOX_AGG_V1_WIRED
except Exception:
    _ia_norm = lambda **kw: kw
    _ia_should = lambda i: True
try:
    from core.constraint_engine import rank_offers as _ce_rank, apply_constraints as _ce_apply, validate_offer as _ce_validate  # CONSTRAINT_ENGINE_V1_WIRED
except Exception:
    _ce_rank = lambda o: o
    _ce_apply = lambda o, **kw: o
    _ce_validate = lambda o: {"ok": True}
try:
    from core.audit_log import audit as _audit  # AUDIT_LOG_V1_WIRED
except Exception:
    _audit = lambda *a, **kw: None
try:
    from core.source_dedup import dedup_offers as _sd_dedup, sort_by_region as _sd_region  # SOURCE_DEDUP_V1_WIRED
except Exception:
    _sd_dedup = lambda o: o
    _sd_region = lambda o, **kw: o
try:
    from core.error_explainer import user_friendly_error as _ee_explain  # ERROR_EXPLAINER_V1_WIRED
except Exception:
    _ee_explain = lambda c: c
try:
    from core.data_classification import classify_domain as _dc_domain, classify_intent as _dc_intent, classify_file_type as _dc_ftype  # DATA_CLASS_V1_WIRED
except Exception:
    _dc_domain = lambda *a: "UNSORTED"
    _dc_intent = lambda t: "text"
    _dc_ftype = lambda f: "UNKNOWN"
try:
    from core.intent_lock import is_chat_only as _il_chat_only, file_result_guard as _il_file_guard  # INTENT_LOCK_V1_WIRED
except Exception:
    _il_chat_only = lambda t: False
    _il_file_guard = lambda **kw: {"ok": True}
try:
    from core.orchestra_context import build_shared_context as _oc_build, user_mode_switch as _oc_mode  # ORCHESTRA_CTX_V1_WIRED
except Exception:
    _oc_build = lambda **kw: ""
    _oc_mode = lambda t: "HUMAN"
try:
    from core.price_normalization import normalize_price_text as _pn_fmt, extract_price as _pn_extract  # PRICE_NORM_V1_WIRED
except Exception:
    _pn_fmt = lambda t: t
    _pn_extract = lambda t: []
try:
    from core.memory_filter import filter_memory_for_prompt as _mf_filter, sanitize_before_write as _mf_clean  # MEMORY_FILTER_V1_WIRED
except Exception:
    _mf_filter = lambda m, **kw: m
    _mf_clean = lambda v: v
try:
    from core.result_validator import validate_result as _rv_validate, is_generic_response as _rv_generic  # RESULT_VALIDATOR_V1_WIRED
except Exception:
    _rv_validate = lambda r, **kw: {"ok": True, "reason": "IMPORT_FAIL"}
    _rv_generic = lambda r: False
try:
    from core.search_quality import availability_check as _sq_avail, cache_get as _sq_cget, cache_set as _sq_cset  # SEARCH_QUALITY_V1_WIRED
except Exception:
    _sq_avail = lambda r: True
    _sq_cget = lambda q: None
    _sq_cset = lambda q, r: None
from core.duplicate_guard import find_duplicate, duplicate_message  # DUPLICATE_GUARD_V1_WIRED
from core.pin_manager import get_pin_context, save_pin
from core.topic_drive_oauth import upload_file_to_topic
from core.artifact_pipeline import analyze_downloaded_file
# === DRIVE_FILE_CONTENT_MEMORY_INDEX_V1_IMPORT ===
try:
    from core.drive_content_indexer import index_drive_file_content as _df_content_index
except Exception:
    _df_content_index = None
# === END DRIVE_FILE_CONTENT_MEMORY_INDEX_V1_IMPORT ===

load_dotenv(f"{BASE}/.env", override=True)

CORE_DB = f"{BASE}/data/core.db"
MEM_DB = f"{BASE}/data/memory.db"
LOG_PATH = f"{BASE}/logs/task_worker.log"
LOCK_PATH = f"{BASE}/runtime/task_worker.lock"

POLL_SEC = 1.5
MIN_RESULT_LEN = 2  # RESULT_VALIDATOR_FIX_V1: was 8
AI_TIMEOUT = 300
STALE_TIMEOUT = 600
REMINDER_SEC = 180

BAD_RESULT_RE = [
    # === RESULT_VALIDATOR_FIX_V1 ===
    # Убраны: извини/извините/ищу/найду/могу найти/я могу помочь
    # Это нормальные слова, AI имеет право их использовать
    r"сорян",
    r"дружище",
    r"delete from",
    r"task_worker\.py",
    r"telegram_daemon\.py",
    r"выполните sql",
    r"/root/\.areal",
    # === END_RESULT_VALIDATOR_FIX_V1 ===
]

MEMORY_BAD_MARKERS = [
    "traceback",
    "forbidden default model",
    "/root/",
    ".json",
    ".log",
    "не могу выполнить запрос",
    "delete from",
    "task_worker.py",
    "telegram_daemon.py",
    "выполните sql",
]

CONFIRM_INTENTS = {
    "да",
    "ок",
    "ok",
    "окей",
    "хорошо",
    "подтверждаю",
    "принято",
    "согласен",
    "верно",
    "всё верно",
    "все верно",
}

REVISION_INTENTS = {
    "нет",
    "не так",
    "переделай",
    "исправь",
    "доработай",
    "уточню",
    "уточнение",
    "правки",
    "уточни",
}

MEMORY_NOISE_MARKERS = [
    "нет данных",
    "повторите",
    "не знаю",
    "чат не содержит активной задачи",
    "привет. чат не содержит активной задачи",
    "чат создан для",
    "тест диагностика",
    "не понял запрос",
    "уточните",
    "не понимаю",
    "задайте вопрос",
]

def _version_artifact_path(path: str, task_id: str) -> str:
    """ARTIFACT_VERSION_V1 — создать версионированный путь file_v2.xlsx"""
    if not path:
        return path
    import re as _re
    # Если уже версионирован — увеличить номер
    m = _re.search(r"_v(\d+)(\.\w+)$", path)
    if m:
        n = int(m.group(1)) + 1
        return path[:m.start()] + f"_v{n}" + m.group(2)
    # Первая ревизия
    base, ext = os.path.splitext(path)
    return f"{base}_v2{ext}"

def _quality_gate_artifact(artifact_path: str = None, drive_link: str = None,
                             input_type: str = "text", task_type: str = "") -> dict:
    """QUALITY_GATE_CALL_V1 — проверить артефакт перед отправкой"""
    is_file_task = input_type in ("drive_file", "file") or task_type in (
        "ESTIMATE_TASK", "OCR_TASK", "DWG_TASK", "TECHNADZOR_TASK", "DOCUMENT_TASK"
    )
    # === DRIVE_LINK_MANDATORY_V1 ===
    if not is_file_task:
        return {"ok": True, "reason": "NOT_FILE_TASK"}
    # Если file task — Drive ссылка обязательна
    if drive_link and "drive.google" in str(drive_link):
        return {"ok": True, "reason": "DRIVE_LINK_PRESENT"}
    if not drive_link and not artifact_path:
        return {"ok": False, "reason": "NO_DRIVE_LINK_NO_ARTIFACT"}
    # === END DRIVE_LINK_MANDATORY_V1 ===

    # Есть Drive ссылка — OK
    if drive_link and "drive.google" in str(drive_link):
        return {"ok": True, "reason": "DRIVE_LINK_PRESENT"}

    # Есть артефакт файл
    if artifact_path and os.path.exists(artifact_path):
        size = os.path.getsize(artifact_path)
        if size < 100:
            return {"ok": False, "reason": "ARTIFACT_TOO_SMALL"}
        # Для Excel проверяем формулы
        if artifact_path.endswith(".xlsx"):
            try:
                from openpyxl import load_workbook
                wb = load_workbook(artifact_path)
                ws = wb.active
                has_formula = any(
                    str(ws.cell(r, c).value or "").startswith("=")
                    for r in range(1, min(ws.max_row+1, 20))
                    for c in range(1, min(ws.max_column+1, 10))
                )
                if not has_formula:
                    logger.warning("QUALITY_GATE: no formulas in %s", artifact_path)
            except Exception:
                pass
        return {"ok": True, "reason": "ARTIFACT_EXISTS"}

    return {"ok": False, "reason": "NO_ARTIFACT_NO_LINK"}

def _is_heavy_task(input_type: str, task_type: str = "") -> bool:
    """FAST_HEAVY_TASK_V1 — определить тип задачи"""
    return input_type in ("drive_file", "file") or task_type in (
        "ESTIMATE_TASK", "OCR_TASK", "DWG_TASK", "TECHNADZOR_TASK", "DOCUMENT_TASK", "MULTI_TASK"
    )

def _get_task_sla(input_type: str, task_type: str = "") -> int:
    """Возвращает SLA в секундах"""
    if _is_heavy_task(input_type, task_type):
        return 120  # HEAVY < 120s
    return 10  # FAST < 10s

def _check_result_before_confirm(result: str, input_type: str = "text", intent: str = "") -> bool:
    """RESULT_VALIDATOR_CALL_V1 — проверить result перед AWAITING_CONFIRMATION"""
    try:
        rv = _rv_validate(result, input_type=input_type, intent=intent)
        if not rv.get("ok"):
            logger.warning("RESULT_VALIDATOR_BLOCKED reason=%s result_prefix=%s", rv.get("reason"), str(result)[:80])
            return False
    except Exception as _rve:
        logger.warning("RESULT_VALIDATOR_ERR %s", _rve)
    return True


# === REPLY_REPEAT_PARENT_TASK_V1 ===
_REPEAT_PARENT_WORDS_V1 = {
    "ну и", "дальше", "повтори", "проверяй", "не так",
    "ещё раз", "еще раз", "заново", "дописывай", "и что", "и?",
    "а", "б", "в", "г", "1", "2", "3", "4",
    "а)", "б)", "в)", "г)",
    "да", "нет", "ок", "хорошо",
    "среднее", "средняя", "минимум", "максимум", "своя",
    "вариант 1", "вариант 2", "вариант 3", "вариант 4",
    "первый", "второй", "третий",
    "самый дешевый", "самый дешёвый", "надежный", "надёжный",
}
def _is_repeat_parent_task_v1(text: str) -> bool:
    t = _clean(_s(text), 500).lower()
    if not t:
        return False
    return t in _REPEAT_PARENT_WORDS_V1 or any(t.startswith(x + " ") for x in _REPEAT_PARENT_WORDS_V1)

def _find_repeat_parent_task_v1(conn, chat_id: str, topic_id: int, exclude_task_id: str = ""):
    try:
        cols = _cols(conn, "tasks")
        if "topic_id" in cols:
            return conn.execute(
                "SELECT * FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=? AND id<>? AND state IN ('IN_PROGRESS','AWAITING_CONFIRMATION','WAITING_CLARIFICATION','AWAITING_PRICE_CONFIRMATION','NEW') ORDER BY updated_at DESC LIMIT 1",
                (str(chat_id), int(topic_id or 0), str(exclude_task_id)),
            ).fetchone()
        return conn.execute(
            "SELECT * FROM tasks WHERE chat_id=? AND id<>? AND state IN ('IN_PROGRESS','AWAITING_CONFIRMATION','WAITING_CLARIFICATION','AWAITING_PRICE_CONFIRMATION','NEW') ORDER BY updated_at DESC LIMIT 1",
            (str(chat_id), str(exclude_task_id)),
        ).fetchone()
    except Exception as _e:
        logger.warning("REPLY_REPEAT_PARENT_TASK_V1_FIND_ERR %s", _e)
        return None
# === END_REPLY_REPEAT_PARENT_TASK_V1 ===

def _is_memory_noise(text: str) -> bool:
    t = _clean(_s(text), 1000).lower()
    if not t:
        return False
    return any(x in t for x in MEMORY_NOISE_MARKERS)

SEARCH_PATTERNS = [
    r"\bнайди\b",
    r"\bнайти\b",
    r"\bпоиск\b",
    r"\bпоищи\b",
    r"\bsearch\b",
    r"\bцена\b",
    r"\bстоимость\b",
    r"\bсколько\s+стоит\b",
    r"\bavito\b",
    r"\bozon\b",
    r"\bwildberries\b",
    r"\bauto\.ru\b",
    r"\bdrom\b",
    r"\bновости\b",
    r"\bпогода\b",
    r"\bкурс\b",
    r"\bмаркетплейс\b",
]

os.makedirs(f"{BASE}/logs", exist_ok=True)
os.makedirs(f"{BASE}/runtime", exist_ok=True)

logger = logging.getLogger("task_worker")
# === FULLFIX_DIRECTION_KERNEL_STAGE_1_IMPORT ===
try:
    from core.work_item import WorkItem as _Stage1WorkItem
    from core.direction_registry import DirectionRegistry as _Stage1DirReg
except Exception:
    _Stage1WorkItem = None
    _Stage1DirReg = None
# === END ===
# === FULLFIX_CAPABILITY_ROUTER_STAGE_2_IMPORT ===
try:
    from core.capability_router import CapabilityRouter as _Stage2Router
except Exception:
    _Stage2Router = None
# === END STAGE2 ===
# === FULLFIX_CONTEXT_LOADER_STAGE_3_IMPORT ===
try:
    from core.context_loader import ContextLoader as _Stage3Loader
except Exception:
    _Stage3Loader = None
# === END STAGE3 ===
# === FULLFIX_QUALITY_GATE_STAGE_4_IMPORT ===
try:
    from core.quality_gate import QualityGate as _Stage4QG
except Exception:
    _Stage4QG = None
# === END STAGE4 ===
# === FULLFIX_SEARCH_ENGINE_STAGE_5_IMPORT ===
try:
    from core.search_engine import SearchEngine as _Stage5Search
except Exception:
    _Stage5Search = None
# === END STAGE5 ===
# === FULLFIX_ARCHIVE_ENGINE_STAGE_6_IMPORT ===
try:
    from core.archive_engine import ArchiveEngine as _Stage6Archive
except Exception:
    _Stage6Archive = None
# === END STAGE6 ===
# === FULLFIX_FORMAT_ADAPTER_STAGE_7_IMPORT ===
try:
    from core.format_adapter import FormatAdapter as _Stage7FA
except Exception:
    _Stage7FA = None
# === END STAGE7 ===
# === FULLFIX_TOPIC_AUTODISCOVERY_V2_IMPORT ===
try:
    from core.topic_autodiscovery import process as _topic_autodiscovery, check_naming_timeout as _topic_naming_check
except Exception:
    _topic_autodiscovery = None
    _topic_naming_check = None
# === END TOPIC_AUTO ===








logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s WORKER: %(message)s"))
    logger.addHandler(fh)


def db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=20, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=15000")
    return conn


# === EZONE_INGEST_V1 ===
EZONE_KEYS = {"system", "architecture", "pipeline", "memory"}

def is_ezone_payload(text: str) -> bool:
    """Проверить что входящий текст — JSON от нейросети"""
    if not text or not text.strip().startswith("{"):
        return False
    try:
        import json as _j
        d = _j.loads(text)
        return bool(EZONE_KEYS & set(d.keys()))
    except Exception:
        return False

def save_ezone_json(chat_id: str, text: str) -> str:
    """Сохранить ingest JSON в memory_files"""
    import json as _j, hashlib, os
    from datetime import datetime, timezone
    try:
        d = _j.loads(text)
        chat_key = f"{chat_id}__telegram"
        base = f"{BASE}/data/memory_files/CHATS/{chat_key}"
        os.makedirs(base, exist_ok=True)
        os.makedirs(f"{BASE}/data/memory_files/GLOBAL", exist_ok=True)
        os.makedirs(f"{BASE}/data/memory_files/SYSTEM", exist_ok=True)

        # Дедупликация по hash за день
        h = hashlib.md5(text.encode()).hexdigest()[:16]
        ts = datetime.now(timezone.utc).isoformat()
        entry = _j.dumps({"timestamp": ts, "data": d, "_meta": {
            "chat_key": chat_key, "ingested_at": ts, "source": "telegram", "hash": h
        }}, ensure_ascii=False)

        # timeline
        with open(f"{base}/timeline.jsonl", "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        with open(f"{BASE}/data/memory_files/GLOBAL/timeline.jsonl", "a", encoding="utf-8") as f:
            f.write(entry + "\n")

        # SYSTEM keys
        for key in EZONE_KEYS:
            if key in d:
                sys_entry = _j.dumps({"timestamp": ts, key: d[key], "chat_key": chat_key}, ensure_ascii=False)
                with open(f"{BASE}/data/memory_files/SYSTEM/{key}.jsonl", "a", encoding="utf-8") as f:
                    f.write(sys_entry + "\n")

        logger.info("EZONE_INGEST_V1 saved chat_key=%s hash=%s", chat_key, h)
        return f"Принял, память загружена ({chat_key})"
    except Exception as e:
        logger.error("EZONE_INGEST_V1 err=%s", e)
        return f"Ошибка загрузки памяти: {e}"
# === END EZONE_INGEST_V1 ===

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()


def _clean(text: str, limit: int = 12000) -> str:
    text = (text or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]


def _task_field(task: Any, field: str, default: Any = "") -> Any:
    try:
        if hasattr(task, "keys") and field in task.keys():
            return task[field]
    except Exception:
        pass
    try:
        return getattr(task, field)
    except Exception:
        return default


def _has_table(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def _cols(conn: sqlite3.Connection, table: str) -> List[str]:
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except Exception:
        return []


def _update_task(conn: sqlite3.Connection, task_id: str, **kwargs: Any) -> None:
    cols = _cols(conn, "tasks")
    parts: List[str] = []
    vals: List[Any] = []

    for key, value in kwargs.items():
        if key in cols:
            parts.append(f"{key}=?")
            if key == "error_message":
                vals.append(_clean(_s(value), 4000))
            elif key == "result":
                vals.append(_clean(_s(value), 50000))
            elif key == "raw_input":
                vals.append(_clean(_s(value), 12000))
            else:
                vals.append(value)

    if "updated_at" in cols:
        parts.append("updated_at=datetime('now')")

    if not parts:
        return

    vals.append(task_id)
    conn.execute(f"UPDATE tasks SET {', '.join(parts)} WHERE id=?", vals)



# === LIVE_MEMORY_HELPERS_V1 ===
def _memory_insert_topic_entry_v1(chat_id: str, key: str, value: str) -> None:
    try:
        import sqlite3 as _sq
        if not os.path.exists(MEM_DB):
            return
        _mc = _sq.connect(MEM_DB)
        try:
            _mc.row_factory = _sq.Row
            _cols_mem = [r[1] for r in _mc.execute("PRAGMA table_info(memory)").fetchall()]
            if not _cols_mem:
                return
            _ts = datetime.datetime.utcnow().isoformat()
            _val = _clean(_s(value), 50000)
            if not _val:
                return
            _mid = hashlib.sha1(f"{chat_id}:{key}:{_ts}:{_val[:80]}".encode()).hexdigest()
            _mc.execute(
                "INSERT OR IGNORE INTO memory (id, chat_id, key, value, timestamp) VALUES (?,?,?,?,?)",
                (_mid, str(chat_id), str(key), _val, _ts),
            )
            _mc.commit()
        finally:
            _mc.close()
    except Exception as _mi_e:
        logger.warning("LIVE_MEMORY_HELPERS_V1_INSERT_ERR %s", _mi_e)

def _append_timeline_event_v1(chat_id: str, topic_id: int, task_id: str, kind: str, raw_input: str = "", result: str = "") -> None:
    try:
        _base = f"{BASE}/data/memory_files"
        _chat_key = f"{chat_id}__telegram"
        _chat_dir = os.path.join(_base, "CHATS", _chat_key)
        os.makedirs(_chat_dir, exist_ok=True)
        os.makedirs(os.path.join(_base, "GLOBAL"), exist_ok=True)
        _entry = json.dumps({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "chat_id": str(chat_id),
            "topic_id": int(topic_id or 0),
            "task_id": str(task_id),
            "kind": str(kind),
            "raw_input": _clean(_s(raw_input), 4000),
            "result": _clean(_s(result), 4000),
            "source": "task_worker",
        }, ensure_ascii=False)
        for _tl_path in [
            os.path.join(_chat_dir, "timeline.jsonl"),
            os.path.join(_base, "GLOBAL", "timeline.jsonl"),
        ]:
            with open(_tl_path, "a", encoding="utf-8") as _f:
                _f.write(_entry + "\n")
    except Exception as _tl_e:
        logger.warning("LIVE_MEMORY_HELPERS_V1_TIMELINE_ERR %s", _tl_e)
# === END LIVE_MEMORY_HELPERS_V1 ===

def _history(conn: sqlite3.Connection, task_id: str, action: str) -> None:
    if not _has_table(conn, "task_history"):
        return
    conn.execute(
        "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
        (task_id, _clean(action, 1000)),
    )


def _already_replied(conn: sqlite3.Connection, task_id: str, kind: str) -> bool:
    if not _has_table(conn, "task_history"):
        return False
    row = conn.execute(
        "SELECT 1 FROM task_history WHERE task_id=? AND action=? LIMIT 1",
        (task_id, f"reply_sent:{kind}"),
    ).fetchone()
    return row is not None


def _send_once(conn: sqlite3.Connection, task_id: str, chat_id: str, text: str, reply_to: Optional[int], kind: str) -> bool:
    # === _send_once_UNIFIED_USER_OUTPUT_SANITIZER_V1 ===
    try:
        from core.output_sanitizer import sanitize_user_output as _uos_sanitize
        text = _uos_sanitize(text)
    except Exception as _uos_err:
        logger.warning("UNIFIED_USER_OUTPUT_SANITIZER_V1_ERR %s", _uos_err)
    # === END__send_once_UNIFIED_USER_OUTPUT_SANITIZER_V1 ===
    if _already_replied(conn, task_id, kind):
        return True
    ok = send_reply(chat_id=chat_id, text=text, reply_to_message_id=reply_to)
    if ok:
        _history(conn, task_id, f"reply_sent:{kind}")
    return bool(ok)


def _send_once_ex(conn: sqlite3.Connection, task_id: str, chat_id: str, text: str, reply_to: Optional[int], kind: str) -> Dict[str, Any]:
    # === _send_once_ex_UNIFIED_USER_OUTPUT_SANITIZER_V1 ===
    try:
        from core.output_sanitizer import sanitize_user_output as _uos_sanitize
        text = _uos_sanitize(text)
    except Exception as _uos_err:
        logger.warning("UNIFIED_USER_OUTPUT_SANITIZER_V1_ERR %s", _uos_err)
    # === END__send_once_ex_UNIFIED_USER_OUTPUT_SANITIZER_V1 ===
    if _already_replied(conn, task_id, kind):
        return {"ok": True, "bot_message_id": None, "skipped": True}
    res = send_reply_ex(chat_id=chat_id, text=text, reply_to_message_id=reply_to)
    if not isinstance(res, dict):
        res = {"ok": bool(res)}
    if res.get("ok"):
        _history(conn, task_id, f"reply_sent:{kind}")
    return res


def _hash(text: str) -> str:
    return hashlib.sha1(_clean(text).lower().encode("utf-8")).hexdigest()


def _is_valid_result(text: str, raw_input: str) -> bool:
    r = _clean(text)
    if not r or len(r) < MIN_RESULT_LEN:
        return False
    if any(re.search(p, r, re.I) for p in BAD_RESULT_RE):
        return False
    if _hash(r) == _hash(raw_input):
        return False
    if "/root/" in r or ".ogg" in r.lower():
        return False
    return True


def _detect_role_assignment(text: str) -> str:
    triggers = [
        r"^(?:\[voice\]\s*)?этот чат для\s+(.+)$",
        r"^(?:\[voice\]\s*)?этот чат про\s+(.+)$",
        r"^(?:\[voice\]\s*)?этот топик для\s+(.+)$",
        r"^(?:\[voice\]\s*)?этот топик про\s+(.+)$",
        r"^(?:\[voice\]\s*)?чат закрепл[её]н за\s+(.+)$",
        r"^(?:\[voice\]\s*)?этот чат исключительно для\s+(.+)$",
        r"^(?:\[voice\]\s*)?этот чат используется для\s+(.+)$",
        r"^(?:\[voice\]\s*)?закрепи чат за\s+(.+)$",
        r"^(?:\[voice\]\s*)?закрепи этот чат за\s+(.+)$",
    ]
    t = _clean(text, 500).lower()
    for pattern in triggers:
        m = re.fullmatch(pattern, t)
        if m:
            return _clean(m.group(1), 200)
    return ""


def _extract_role_confirmation(result: str) -> str:
    t = _clean(_s(result), 500)
    m = re.fullmatch(r"Понял назначение чата так:\n(.+?)\n\nПодтверди или уточни", t, re.S)
    if not m:
        return ""
    return _clean(m.group(1), 200)


def _save_topic_role(chat_id: str, topic_id: int, role: str) -> None:
    if not role or not os.path.exists(MEM_DB):
        return
    mem = db(MEM_DB)
    try:
        if not _has_table(mem, "memory"):
            mem.execute("CREATE TABLE IF NOT EXISTS memory (chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        key = f"topic_{topic_id}_role"
        mem.execute("DELETE FROM memory WHERE chat_id=? AND key=?", (str(chat_id), key))
        mem.execute(
            "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(chat_id), key, role),
        )
        mem.commit()
    finally:
        mem.close()


def _load_memory_context(chat_id: str, topic_id: int) -> Tuple[str, str, str, str]:
    if not os.path.exists(MEM_DB):
        return "", "", "", ""

    conn = db(MEM_DB)
    try:
        if not _has_table(conn, "memory"):
            return "", "", "", ""

        topic_prefix = f"topic_{int(topic_id)}_"
        rows = conn.execute(
            """
            SELECT key, value
            FROM memory
            WHERE chat_id=?
              AND key GLOB ?
            ORDER BY timestamp DESC
            LIMIT 100
            """,
            (str(chat_id), f"{topic_prefix}*"),
        ).fetchall()

        short_memory: List[str] = []
        long_memory: List[str] = []
        topic_role = ""
        topic_directions = ""

        MEMORY_MUTEX_MARKERS = [
            "последние действия",
            "этот чат закреплён за: последние действия",
            "в этом чате были следующие действия",
            "текущий статус: ожидание подтверждения",
            "текущий статус:",
            "задача отменена",
            "задача завершена",
            "задача закрыта",
            "задачи завершены",
            "подтверждение принято",
            "не понимаю запрос",
            "готов к выполнению задачи",
            "без контекста",
            "задайте конкретный вопрос",
            "конкретный вопрос по",
            "нет, не помню",
        ]

        for row in rows:
            key = _s(row["key"])
            raw_value = _s(row["value"])
            if key.endswith("_user_input") or key.endswith("_role"):
                limit = 500
            elif key.endswith("_task_summary"):
                limit = 20000
            elif key.endswith("_assistant_output"):
                limit = 50000
            elif key.endswith("_directions"):
                limit = 1000
            else:
                limit = 500
            value = _clean(raw_value, limit)
            if not value:
                continue
            low = value.lower()
            if _is_memory_noise(low) or any(x in low for x in MEMORY_BAD_MARKERS):
                continue
            if any(m in low for m in MEMORY_MUTEX_MARKERS):
                continue

            if key.endswith("_role") and not topic_role:
                topic_role = value[:500]
                continue

            if not topic_role and (key.endswith("_assistant_output") or key.endswith("_task_summary")):
                m = re.search(r"чат закрепл[её]н за темами:\s*(.+?)(?:\.|$)", value, re.I)
                if not m:
                    m = re.search(r"чат закрепл[её]н за\s*(.+?)(?:\.|$)", value, re.I)
                if not m:
                    m = re.search(r"закреплено:\s*чат для\s*(.+?)(?:\.|$)", value, re.I)
                if not m:
                    m = re.search(r"этот чат используется для\s*(.+?)(?:\.|$)", value, re.I)
                if m:
                    topic_role = _clean(m.group(1), 500)

            if key.endswith("_directions") and not topic_directions:
                topic_directions = value[:1000]
                continue
            if key.endswith("_user_input") or key.endswith("_task_summary"):
                if not _is_memory_noise(value):
                    short_memory.append(f"{key}: {value}")
            else:
                if not _is_memory_noise(value):
                    long_memory.append(f"{key}: {value}")

        # === TOPIC_META_ROLE_INJECT_V1 ===
        if not topic_role and TOPIC_META_LOADER_WIRED:
            try:
                _tm = load_topic_meta(int(topic_id or 0))
                if _tm:
                    _tm_name = _tm.get("name", "")
                    _tm_dir = _tm.get("direction", "")
                    if _tm_name:
                        topic_role = f"Топик: {_tm_name} | Направление: {_tm_dir}"
            except Exception:
                pass
        # === END TOPIC_META_ROLE_INJECT_V1 ===
        return "\n".join(short_memory[:20]), "\n".join(long_memory[:20]), topic_role, topic_directions  # MEMORY_LIMIT_20_V1
    finally:
        conn.close()


def _load_archive_context(chat_id: str, topic_id: int, user_text: str) -> str:
    # === ARCHIVE_DISTRIBUTOR_V1_WIRED ===
    try:
        from core.archive_distributor import _load_archive_for_topic
        arc = _load_archive_for_topic(chat_id, topic_id, user_text, limit=5)
        if arc:
            return arc
    except Exception as _ade:
        logger.warning("ARCHIVE_DISTRIBUTOR_ERR %s", _ade)
    # === END ARCHIVE_DISTRIBUTOR_V1_WIRED ===
    # Fallback — старый метод через archive_legacy
    STOP_WORDS = {"это","как","что","где","когда","для","почему","зачем","кто"}
    words = {w for w in re.findall(r"\w+", _clean(user_text).lower()) if len(w) > 3 and w not in STOP_WORDS}
    if not words or not os.path.exists(MEM_DB):
        return ""

    conn = db(MEM_DB)
    try:
        if not _has_table(conn, "memory"):
            return ""
        rows = conn.execute(
            """
            SELECT key, value
            FROM memory
            WHERE chat_id=?
              AND key LIKE 'archive_legacy_%'
            ORDER BY timestamp DESC
            LIMIT 300
            """,
            (str(chat_id),),
        ).fetchall()
    finally:
        conn.close()

    scored: List[Tuple[int, str]] = []
    for row in rows:
        raw = _s(row["value"])
        if any(x in raw.lower() for x in MEMORY_BAD_MARKERS):
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        if int(payload.get("topic_id", -1)) != int(topic_id):
            continue
        blob = _clean(f"{_s(payload.get('raw_input', ''))}\n{_s(payload.get('result', ''))}", 1200)
        ov = len(words & set(re.findall(r"\w+", blob.lower())))
        if ov > 0:
            scored.append((ov, blob))

    scored = [(ov, blob) for ov, blob in scored if ov > 0]
    scored.sort(key=lambda x: x[0], reverse=True)
    return "\n\n".join(x[1] for x in scored[:3]) if scored else ""


def _active_unfinished_context(conn: sqlite3.Connection, chat_id: str, topic_id: int, task_id: str) -> str:
    cols = _cols(conn, "tasks")
    where = [
        "chat_id=?",
        "id<>?",
        "state IN ('WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
    ]
    params: List[Any] = [str(chat_id), task_id]
    if "topic_id" in cols:
        where.append("COALESCE(topic_id,0)=?")
        params.append(int(topic_id))

    rows = conn.execute(
        f"""
        SELECT raw_input, result, state
        FROM tasks
        WHERE {' AND '.join(where)}
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 3
        """,
        params,
    ).fetchall()

    parts = []
    for row in rows:
        raw = _clean(_s(_task_field(row, "raw_input")), 300)
        res = _clean(_s(row["result"]), 500)
        state = _clean(_s(row["state"]), 100)
        low = f"{raw}\n{res}".lower()
        if any(x in low for x in MEMORY_BAD_MARKERS):
            continue
        chunk = []
        if raw:
            chunk.append(f"raw_input: {raw}")
        if res:
            chunk.append(f"result: {res}")
        if state:
            chunk.append(f"state: {state}")
        if chunk:
            parts.append("\n".join(chunk))
    return "\n\n".join(parts[:3])


def _search_fact_context(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> str:
    cols = _cols(conn, "tasks")
    where = [
        "chat_id=?",
        "state IN ('DONE','ARCHIVED')",
        "lower(COALESCE(raw_input,'')) GLOB '*най*'",
    ]
    params: List[Any] = [str(chat_id)]
    if "topic_id" in cols:
        where.append("COALESCE(topic_id,0)=?")
        params.append(int(topic_id))

    rows = conn.execute(
        f"""
        SELECT raw_input, result
        FROM tasks
        WHERE {' AND '.join(where)}
        ORDER BY updated_at DESC
        LIMIT 5
        """,
        params,
    ).fetchall()

    facts: List[str] = []
    for row in rows:
        q = _clean(_s(row["raw_input"]), 300)
        r = _clean(_s(row["result"]), 500)
        low = f"{q}\n{r}".lower()
        if any(x in low for x in MEMORY_BAD_MARKERS):
            continue
        if q and r:
            facts.append(f"search_done: {q} => {r}")
    return "\n".join(facts[:3])


def _save_memory(chat_id: str, topic_id: int, raw_input: str, result: str) -> None:
    low = (result or "").lower()
    if any(x in low for x in [
        "без контекста","не понимаю запрос","не помню",
        "задача завершена","задача закрыта","подтверждение принято",
        "готов к выполнению задачи"
    ]):
        return

    bad = [
        "ошибка",
        "не найдено",
        "уточните",
        "traceback",
        "/root/",
        ".ogg",
        "delete from",
        "task_worker.py",
        "telegram_daemon.py",
    ]
    if not result or len(result) < MIN_RESULT_LEN:
        return
    low = result.lower()
    if any(b in low for b in bad):
        return
    if not os.path.exists(MEM_DB):
        return

    conn = db(MEM_DB)
    try:
        if not _has_table(conn, "memory"):
            conn.execute("CREATE TABLE IF NOT EXISTS memory (chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        prefix = f"topic_{int(topic_id)}_"
        conn.execute(
            "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(chat_id), f"{prefix}assistant_output", _clean(result, 50000)),
        )
        conn.execute(
            "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(chat_id), f"{prefix}task_summary", _clean(result, 20000) if len(result) >= MIN_RESULT_LEN else ""),
        )
        conn.execute(
            "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(chat_id), f"{prefix}user_input", _clean(raw_input, 500)),
        )
        conn.commit()
        logger.info("save_memory_ok chat=%s topic=%s", chat_id, topic_id)
    finally:
        conn.close()


def _close_pin(conn: sqlite3.Connection, task_id: str) -> None:
    if not _has_table(conn, "pin"):
        return
    conn.execute(
        "UPDATE pin SET state='CLOSED', updated_at=datetime('now') WHERE task_id=? AND state='ACTIVE'",
        (task_id,),
    )


def _finalize_done(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, reply_to: Optional[int]) -> None:
    row = conn.execute(
        "SELECT COALESCE(raw_input,''), COALESCE(result,'') FROM tasks WHERE id=? LIMIT 1",
        (task_id,),
    ).fetchone()
    raw_input = _clean(_s(row[0]) if row else "", 500)
    result = _clean(_s(row[1]) if row else "", 50000)

    _update_task(conn, task_id, state="DONE", error_message="")
    _history(conn, task_id, "state:DONE")
    if result:
        _save_memory(chat_id, topic_id, raw_input, result)
    conn.commit()


def _is_confirm_intent(text: str) -> bool:
    t = _clean(text, 200).lower()
    if t in CONFIRM_INTENTS:
        return True
    return any(t.startswith(x) for x in ["да", "подтвер", "соглас", "верно", "ок"])


def _is_revision_intent(text: str) -> bool:
    t = _clean(text, 200).lower()
    if t in REVISION_INTENTS:
        return True
    return any(x in t for x in ["не так", "передел", "исправ", "правк", "уточн"])


def _recover_stale_tasks(conn: sqlite3.Connection, chat_id: Optional[str]) -> None:
    # CONFIRMATION_TIMEOUT_FIX_V1
    try:
        conn.execute("""
            UPDATE tasks SET state='FAILED', error_message='CONFIRMATION_TIMEOUT', updated_at=datetime('now')
            WHERE state='AWAITING_CONFIRMATION'
              AND updated_at < datetime('now','-30 minutes')
              AND COALESCE(raw_input,'') NOT LIKE '%retry_queue_healthcheck%'
              AND COALESCE(result,'') NOT LIKE '%retry_queue_healthcheck%'
        """)
        conn.commit()
    except Exception as _ct_e:
        logger.warning("CONFIRMATION_TIMEOUT_FIX_V1_ERR %s", _ct_e)
    # IN_PROGRESS_HARD_TIMEOUT_V1
    try:
        _hp = [] if not chat_id else [str(chat_id)]
        _hw = (["chat_id=?"] if chat_id else []) + [
            "state='IN_PROGRESS'",
            "created_at < datetime('now','-15 minutes')",
        ]
        for _hr in conn.execute(
            f"SELECT id,chat_id,COALESCE(topic_id,0) AS topic_id,reply_to_message_id,raw_input FROM tasks WHERE {' AND '.join(_hw)}",
            _hp,
        ).fetchall():
            _htid = _s(_hr["id"]); _hchat = _s(_hr["chat_id"])
            _htopic = int(_hr["topic_id"] or 0); _hreply = _hr["reply_to_message_id"]
            _hmsg = "Задача не выполнена: превышено время выполнения"
            _update_task(conn, _htid, state="FAILED", result=_hmsg, error_message="EXECUTION_TIMEOUT")
            _close_pin(conn, _htid); _history(conn, _htid, "state:FAILED:EXECUTION_TIMEOUT")
            try:
                _append_timeline_event_v1(_hchat, _htopic, _htid, "execution_timeout", _s(_hr["raw_input"]), _hmsg)
            except Exception: pass
            conn.commit()
            _send_once(conn, _htid, _hchat, _hmsg, _hreply, "execution_timeout")
    except Exception as _e:
        logger.warning("IN_PROGRESS_HARD_TIMEOUT_V1_ERR %s", _e)

    where = [
        "state IN ('IN_PROGRESS','WAITING_CLARIFICATION')",
        "(strftime('%s','now') - strftime('%s', COALESCE(updated_at, created_at))) > ?",
    ]
    params: List[Any] = [STALE_TIMEOUT]
    if chat_id:
        where.insert(0, "chat_id=?")
        params.insert(0, str(chat_id))

    rows = conn.execute(
        f"""
        SELECT id, chat_id, COALESCE(topic_id,0) AS topic_id, reply_to_message_id
        FROM tasks
        WHERE {' AND '.join(where)}
        """,
        params,
    ).fetchall()

    for row in rows:
        task_id = _s(row["id"])
        tg_chat_id = _s(row["chat_id"])
        reply_to = row["reply_to_message_id"]
        _update_task(conn, task_id, state="FAILED", error_message="STALE_TIMEOUT")
        _close_pin(conn, task_id)
        _history(conn, task_id, "state:FAILED")
        conn.commit()
        _send_once(conn, task_id, tg_chat_id, "Задача не выполнена. Повтори или уточни запрос", reply_to, "stale_failed")

    done_markers = [
        "задача завершена",
        "задача закрыта",
        "задачи завершены",
        "подтверждение принято",
    ]
    junk_markers = [
        "без контекста",
        "задайте конкретный вопрос",
        "конкретный вопрос по",
        "нет, не помню",
        "не понимаю запрос",
        "готов к выполнению задачи",
    ]

    rows = conn.execute("""
        SELECT id, chat_id, COALESCE(topic_id,0) AS topic_id, reply_to_message_id, result, raw_input, input_type, updated_at, created_at
        FROM tasks
        WHERE state = 'AWAITING_CONFIRMATION'
    """).fetchall()

    now_utc = datetime.datetime.now(datetime.timezone.utc)

    for row in rows:
        updated = row["updated_at"] or row["created_at"]
        if not updated:
            continue

        result = _s(row["result"])
        low_result = result.lower()
        row_raw_input = ""
        try:
            row_raw_input = _s(row["raw_input"])
        except Exception:
            row_raw_input = ""
        if _force_voice_finish(row_raw_input, result):
            _update_task(conn, row["id"], state="DONE")
            continue  # FORCE_VOICE_FINISH_HOOK

        if any(m in low_result for m in done_markers):
            _update_task(conn, row["id"], state="DONE", error_message="")
            _close_pin(conn, row["id"])
            _history(conn, row["id"], "state:DONE")
            conn.commit()
            continue

        if any(m in low_result for m in junk_markers):
            _update_task(conn, row["id"], state="FAILED", error_message="JUNK_RESULT_CLEANUP")
            _close_pin(conn, row["id"])
            _history(conn, row["id"], "state:FAILED")
            conn.commit()
            continue

        try:
            s = str(updated).strip()
            if "T" in s:
                dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
            else:
                dt = datetime.datetime.fromisoformat(s)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
        except Exception:
            continue

        hours_old = (now_utc - dt).total_seconds() / 3600.0
        if hours_old <= 24:
            continue

        if _s(row["input_type"]).lower() == "drive_file" and hours_old > 48:
            _update_task(conn, row["id"], state="FAILED", error_message="drive_upload_stale")
            _close_pin(conn, row["id"])
            _history(conn, row["id"], "state:FAILED")
            conn.commit()
        elif hours_old > 168:
            _update_task(conn, row["id"], state="ARCHIVED")
            _close_pin(conn, row["id"])
            _history(conn, row["id"], "state:ARCHIVED")
            conn.commit()

    conn.execute("""
        UPDATE pin
        SET state='CLOSED', updated_at=datetime('now')
        WHERE state='ACTIVE'
          AND task_id IN (
              SELECT id FROM tasks
              WHERE state='FAILED'
                 OR lower(COALESCE(result,'')) LIKE '%задача закрыта%'
                 OR lower(COALESCE(result,'')) LIKE '%подтверждение принято%'
                 OR lower(COALESCE(result,'')) LIKE '%без контекста%'
                 OR lower(COALESCE(result,'')) LIKE '%конкретный вопрос%'
                 OR lower(COALESCE(result,'')) LIKE '%не помню%'
          )
    """)
    conn.commit()



# === FULLFIX_13D_TASK_WORKER_SEND_BELT ===
# reply_sender also strips MANIFEST globally
# === END FULLFIX_13D_TASK_WORKER_SEND_BELT ===

# === FULLFIX_13C_STRIP_MANIFEST_BEFORE_SEND ===
def _ff13c_strip_manifest_links(text):
    import re
    msg = str(text or "")
    msg = re.sub(r"(?im)^MANIFEST:\s*https?://\S+\s*$", "", msg)
    msg = re.sub(r"(?im)^Manifest:\s*https?://\S+\s*$", "", msg)
    msg = re.sub(r"\n{3,}", "\n\n", msg).strip()
    return msg
# === END FULLFIX_13C_STRIP_MANIFEST_BEFORE_SEND ===


async def _handle_new(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> None:
    # === REMAINING_TECH_CONTOUR_CLOSE_V1_WIRED ===
    # P0 guard order:
    # 1. reply repeat parent
    # 2. explicit project route before estimate/template/file followup
    try:
        from core.reply_repeat_parent import prehandle_reply_repeat_parent_v1 as _rrp_prehandle
        _rrp = _rrp_prehandle(conn, task)
        if _rrp and _rrp.get("handled"):
            _rrp_tid = _s(_task_field(task, "id", ""))
            _rrp_chat = _s(_task_field(task, "chat_id", ""))
            _rrp_reply = _task_field(task, "reply_to_message_id", None)
            _rrp_text = _rrp.get("message") or ""
            try:
                from core.output_sanitizer import sanitize_user_output as _sanitize_out
                _rrp_text = _sanitize_out(_rrp_text)
            except Exception:
                pass
            _rrp_send = _send_once_ex(conn, _rrp_tid, _rrp_chat, _rrp_text, _rrp_reply, _rrp.get("kind", "reply_repeat_parent"))
            _update_task(
                conn,
                _rrp_tid,
                state=_rrp.get("state", "DONE"),
                result=_rrp_text,
                error_message=_rrp.get("error_message", ""),
                bot_message_id=_rrp_send.get("bot_message_id"),
            )
            _history(conn, _rrp_tid, _rrp.get("history", "REPLY_REPEAT_PARENT_TASK_V1:HANDLED"))
            return
    except Exception as _rrp_err:
        logger.warning("REMAINING_TECH_CONTOUR_CLOSE_V1_REPLY_ERR %s", _rrp_err)

    try:
        from core.project_route_guard import prehandle_project_route_v1 as _proj_prehandle
        _proj = await _proj_prehandle(conn, task)
        if _proj and _proj.get("handled"):
            _proj_tid = _s(_task_field(task, "id", ""))
            _proj_chat = _s(_task_field(task, "chat_id", ""))
            _proj_reply = _task_field(task, "reply_to_message_id", None)
            _proj_text = _proj.get("message") or ""
            try:
                from core.output_sanitizer import sanitize_project_message as _sanitize_project_out
                _proj_text = _sanitize_project_out(_proj_text)
            except Exception:
                pass
            _proj_send = _send_once_ex(conn, _proj_tid, _proj_chat, _proj_text, _proj_reply, _proj.get("kind", "project_route_guard"))
            _update_task(
                conn,
                _proj_tid,
                state=_proj.get("state", "WAITING_CLARIFICATION"),
                result=_proj_text,
                error_message=_proj.get("error_message", ""),
                bot_message_id=_proj_send.get("bot_message_id"),
            )
            _history(conn, _proj_tid, _proj.get("history", "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:HANDLED"))
            return
    except Exception as _proj_err:
        logger.warning("REMAINING_TECH_CONTOUR_CLOSE_V1_PROJECT_ERR %s", _proj_err)
    # === END_REMAINING_TECH_CONTOUR_CLOSE_V1_WIRED ===
    # === FULL_TECH_CONTOUR_CLOSE_V1_WIRED ===
    # P0 guard: price confirmation, context-aware file intake, Telegram duplicate file memory
    try:
        from core.price_enrichment import prehandle_price_task_v1 as _ftc_price_prehandle
        _ftc_price = await _ftc_price_prehandle(conn, task)
        if _ftc_price and _ftc_price.get("handled"):
            _ftc_tid = _s(_task_field(task, "id", ""))
            _ftc_chat = _s(_task_field(task, "chat_id", ""))
            _ftc_reply = _task_field(task, "reply_to_message_id", None)
            _ftc_text = _ftc_price.get("message") or ""
            _ftc_send = _send_once_ex(conn, _ftc_tid, _ftc_chat, _ftc_text, _ftc_reply, _ftc_price.get("kind", "price_enrichment"))
            _update_task(
                conn,
                _ftc_tid,
                state=_ftc_price.get("state", "WAITING_CLARIFICATION"),
                result=_ftc_text,
                error_message=_ftc_price.get("error_message", ""),
                bot_message_id=_ftc_send.get("bot_message_id"),
            )
            _history(conn, _ftc_tid, _ftc_price.get("history", "WEB_SEARCH_PRICE_ENRICHMENT_V1:HANDLED"))
            return
    except Exception as _ftc_price_err:
        logger.warning("FULL_TECH_CONTOUR_CLOSE_V1_PRICE_ERR %s", _ftc_price_err)

    try:
        from core.file_context_intake import prehandle_task_context_v1 as _ftc_file_prehandle
        _ftc_file = _ftc_file_prehandle(conn, task)
        if _ftc_file and _ftc_file.get("handled"):
            _ftc_tid = _s(_task_field(task, "id", ""))
            _ftc_chat = _s(_task_field(task, "chat_id", ""))
            _ftc_reply = _task_field(task, "reply_to_message_id", None)
            _ftc_text = _ftc_file.get("message") or ""
            _ftc_send = _send_once_ex(conn, _ftc_tid, _ftc_chat, _ftc_text, _ftc_reply, _ftc_file.get("kind", "file_context_intake"))
            _update_task(
                conn,
                _ftc_tid,
                state=_ftc_file.get("state", "DONE"),
                result=_ftc_text,
                error_message=_ftc_file.get("error_message", ""),
                bot_message_id=_ftc_send.get("bot_message_id"),
            )
            _history(conn, _ftc_tid, _ftc_file.get("history", "CONTEXT_AWARE_FILE_INTAKE_V1:HANDLED"))
            return
    except Exception as _ftc_file_err:
        logger.warning("FULL_TECH_CONTOUR_CLOSE_V1_FILE_ERR %s", _ftc_file_err)
    # === END_FULL_TECH_CONTOUR_CLOSE_V1_WIRED ===

    # === FINAL_CLOSURE_BLOCKER_FIX_V1_TASK_WORKER_HOOK ===
    try:
        from core.final_closure_engine import maybe_handle_final_closure as _fcv1_handle
        _fcv1 = _fcv1_handle(
            conn=conn,
            task=task,
            task_id=str(task_id),
            chat_id=str(chat_id),
            topic_id=int(topic_id or 0),
            raw_input=raw_input,
            input_type=input_type,
            reply_to=reply_to,
        )
        if isinstance(_fcv1, dict) and _fcv1.get("handled"):
            _fcv1_msg = str(_fcv1.get("message") or "").strip()
            _fcv1_state = str(_fcv1.get("state") or "DONE").strip()
            _fcv1_kind = str(_fcv1.get("kind") or "final_closure_blocker_fix_v1").strip()
            if _fcv1_msg:
                _fcv1_send = _send_once_ex(conn, str(task_id), str(chat_id), _fcv1_msg, reply_to, _fcv1_kind)
                _fcv1_bot = _fcv1_send.get("bot_message_id") if isinstance(_fcv1_send, dict) else None
                _update_task(conn, str(task_id), state=_fcv1_state, result=_fcv1_msg, bot_message_id=_fcv1_bot, error_message="")
                _history(conn, str(task_id), _fcv1.get("history", "FINAL_CLOSURE_BLOCKER_FIX_V1:HANDLED"))
                conn.commit()
                return
    except Exception as _fcv1_err:
        logger.warning("FINAL_CLOSURE_BLOCKER_FIX_V1_TASK_WORKER_HOOK_ERR %s", _fcv1_err)
    # === END_FINAL_CLOSURE_BLOCKER_FIX_V1_TASK_WORKER_HOOK ===

    # === EZONE_INGEST_CALL_V1 ===
    try:
        _ez_raw = str(task["raw_input"] if task else "") if task else ""
        if is_ezone_payload(_ez_raw):
            _ez_msg = save_ezone_json(str(chat_id), _ez_raw)
            _update_task(conn, task["id"], state="DONE", result=_ez_msg, error_message="")
            conn.commit()
            from core.reply_sender import send_reply_ex
            send_reply_ex(chat_id=str(chat_id), text=_ez_msg, reply_to_message_id=task.get("reply_to_message_id"), message_thread_id=topic_id)
            logger.info("EZONE_INGEST_CALL_V1 task=%s", task["id"])
            return
    except Exception as _eze:
        logger.warning("EZONE_INGEST_CALL_ERR %s", _eze)
    # === END EZONE_INGEST_CALL_V1 ===
    # === HEALTHCHECK_GUARD_V1 ===
    try:
        _hc_raw = str(task['raw_input'] if task else '') if task else ''
        _hc_res = str(task['result'] if task else '') if task else ''
        _hc_markers = ['retry_queue_healthcheck', 'healthcheck', 'areal_hc_', '_hc_file']
        if any(m in _hc_raw or m in _hc_res for m in _hc_markers):
            _update_task(conn, task['id'], state='CANCELLED', error_message='SERVICE_FILE_IGNORED:HEALTHCHECK')
            conn.commit()
            logger.info('HEALTHCHECK_GUARD_V1 cancelled task=%s', task['id'])
            return
    except Exception as _hcge:
        logger.warning('HEALTHCHECK_GUARD_ERR %s', _hcge)
    # === END HEALTHCHECK_GUARD_V1 ===
    task_id = _s(_task_field(task, "id"))
    raw_input = _clean(_s(_task_field(task, "raw_input")), 4000)
    reply_to = _task_field(task, "reply_to_message_id", None)

    # === VOICE_CONFIRM_AWAITING_V1 ===
    try:
        _vc_raw = str(raw_input or "").strip()
        _vc_is_voice = _vc_raw.lower().startswith("[voice]")
        _vc_text = re.sub(r"^\s*\[voice\]\s*", "", _vc_raw, flags=re.I).strip()
        _vc_low = _vc_text.lower().strip().rstrip("!?. ")
        if _vc_is_voice and (_vc_low in CONFIRM_INTENTS or _vc_low in REVISION_INTENTS):
            _vc_parent = conn.execute(
                """
                SELECT id, result, raw_input
                FROM tasks
                WHERE chat_id=?
                  AND COALESCE(topic_id,0)=?
                  AND id<>?
                  AND state='AWAITING_CONFIRMATION'
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (str(chat_id), int(topic_id or 0), task_id),
            ).fetchone()

            if _vc_parent is not None and _vc_low in CONFIRM_INTENTS:
                _vc_parent_id = _s(_vc_parent["id"])
                _finalize_done(conn, _vc_parent_id, str(chat_id), int(topic_id or 0), reply_to)
                _update_task(conn, task_id, state="DONE", result="Подтверждение принято голосом. Задача закрыта", error_message="")
                _history(conn, _vc_parent_id, "VOICE_CONFIRM_AWAITING_V1:PARENT_DONE")
                _history(conn, task_id, "VOICE_CONFIRM_AWAITING_V1:CHILD_DONE")
                conn.commit()
                _send_once(conn, task_id, str(chat_id), "Подтверждение принято голосом. Задача закрыта", reply_to, "voice_confirm_awaiting_v1")
                logger.info("VOICE_CONFIRM_AWAITING_V1 confirmed parent=%s child=%s topic=%s", _vc_parent_id, task_id, topic_id)
                return

            if _vc_parent is not None and _vc_low in REVISION_INTENTS:
                _vc_parent_id = _s(_vc_parent["id"])
                _vc_merged = _clean(_s(_vc_parent["result"]) + "\n\nПравки пользователя голосом:\n" + _vc_text, 12000)
                _update_task(conn, _vc_parent_id, state="IN_PROGRESS", raw_input=_vc_merged, error_message="")
                _update_task(conn, task_id, state="DONE", result="Голосовые правки приняты. Задача возвращена в работу", error_message="")
                _history(conn, _vc_parent_id, "VOICE_CONFIRM_AWAITING_V1:PARENT_REVISION")
                _history(conn, task_id, "VOICE_CONFIRM_AWAITING_V1:CHILD_DONE_REVISION")
                conn.commit()
                _send_once(conn, task_id, str(chat_id), "Голосовые правки приняты. Задача возвращена в работу", reply_to, "voice_revision_awaiting_v1")
                logger.info("VOICE_CONFIRM_AWAITING_V1 revision parent=%s child=%s topic=%s", _vc_parent_id, task_id, topic_id)
                return
    except Exception as _vc_e:
        logger.error("VOICE_CONFIRM_AWAITING_V1_ERR task=%s err=%s", task_id, _vc_e)
    # === END VOICE_CONFIRM_AWAITING_V1 ===




    
    # === CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1 ===
    try:
        _cpp_raw = ""
        try:
            _cpp_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
        except Exception:
            _cpp_raw = ""
        _cpp_clean = re.sub(r"^\s*\[VOICE\]\s*", "", _cpp_raw or "", flags=re.I).strip()
        _cpp_low = _cpp_clean.lower()

        _cpp_create_words = (
            "сделай", "делай", "создай", "сформируй", "подготовь", "разработай",
            "оформи", "выгрузи", "сохрани", "нарисуй", "собери"
        )
        # === CREATE_PROJECT_CPP_WORDS_FIX_V1 ===
        _cpp_project_words = (
            "проект", "кж", "кд", "км", "кмд", "ар",
            "фундамент", "фундаментн",
            "армирован", "арматур", "конструктив", "чертеж", "чертёж",
            "dxf", "dwg", "узел", "узлы", "спецификац"
        )
        # === END_CREATE_PROJECT_CPP_WORDS_FIX_V1 ===
        _cpp_followup_words = (
            "я тебе скидывал", "уже скидывал", "где файл", "где проект",
            "что дальше", "дальше то что", "ты сделал", "что мы делали",
            "какие последние", "покажи прошл", "найди прошл", "помнишь"
        )

        _cpp_is_create_project = (
            any(w in _cpp_low for w in _cpp_create_words)
            and any(w in _cpp_low for w in _cpp_project_words)
            and not any(w in _cpp_low for w in _cpp_followup_words)
        )

        if _cpp_is_create_project:
            _history(conn, task_id, "CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1:ROUTE_PROJECT_ENGINE")

            from core.project_engine import create_project_pdf_dxf_artifact

            try:
                _cpp_data = await create_project_pdf_dxf_artifact(
                    raw_input=_cpp_clean,
                    task_id=str(task_id),
                    topic_id=int(topic_id or 0),
                    template_hint="",
                    require_template=False,
                )
            except TypeError:
                _cpp_data = await create_project_pdf_dxf_artifact(
                    _cpp_clean,
                    str(task_id),
                    int(topic_id or 0),
                    "",
                )

            if not isinstance(_cpp_data, dict):
                _update_task(conn, task_id, state="FAILED", result="", error_message="CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1:NON_DICT_RESULT")
                _history(conn, task_id, "CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1:NON_DICT_RESULT")
                return

            _cpp_links = {}
            for _k in ("pdf_link", "dxf_link", "xlsx_link", "docx_link", "drive_link", "google_sheet_link", "link"):
                _v = _cpp_data.get(_k)
                if isinstance(_v, str) and _v.startswith("http"):
                    _cpp_links[_k] = _v

            if isinstance(_cpp_data.get("links"), dict):
                for _k, _v in _cpp_data.get("links").items():
                    if isinstance(_v, str) and _v.startswith("http"):
                        _cpp_links[str(_k)] = _v

            _cpp_artifacts = []
            for _k in ("artifact_path", "package_path", "zip_path", "pdf_path", "dxf_path", "xlsx_path", "docx_path"):
                _v = _cpp_data.get(_k)
                if isinstance(_v, str) and _v:
                    _cpp_artifacts.append({"path": _v, "kind": "project_" + _k.replace("_path", "")})

            if _cpp_artifacts and not _cpp_links:
                try:
                    from core.artifact_upload_guard import upload_many_or_fail
                    _up = upload_many_or_fail(_cpp_artifacts, str(task_id), int(topic_id or 0))
                    if isinstance(_up, dict):
                        for _k, _v in (_up.get("links") or {}).items():
                            if isinstance(_v, str) and _v.startswith("http"):
                                _cpp_links[str(_k)] = _v
                except Exception as _up_e:
                    logger.warning("CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1_UPLOAD_ERR task=%s err=%s", task_id, _up_e)

            _pdf = ""
            _dxf = ""
            _xlsx = ""
            _other = ""

            for _k, _v in _cpp_links.items():
                _kl = str(_k).lower()
                _vl = str(_v).lower()
                if not _pdf and ("pdf" in _kl or ".pdf" in _vl):
                    _pdf = _v
                elif not _dxf and ("dxf" in _kl or ".dxf" in _vl):
                    _dxf = _v
                elif not _xlsx and ("xlsx" in _kl or "sheet" in _kl or "spreadsheets" in _vl or ".xlsx" in _vl):
                    _xlsx = _v
                elif not _other:
                    _other = _v

            _cpp_result_lines = ["Проект плиты создан"]
            if _pdf:
                _cpp_result_lines.append("PDF: " + _pdf)
            if _dxf:
                _cpp_result_lines.append("DXF: " + _dxf)
            if _xlsx:
                _cpp_result_lines.append("XLSX: " + _xlsx)
            if not (_pdf or _dxf or _xlsx) and _other:
                _cpp_result_lines.append("Файл: " + _other)

            _cpp_result = "\n".join(_cpp_result_lines).strip()

            _cpp_success = bool(_cpp_data.get("success")) or bool(_cpp_links) or bool(_cpp_artifacts)
            if _cpp_success and (_cpp_links or _cpp_artifacts):
                _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_cpp_result, error_message="")
                _history(conn, task_id, "CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1:AWAITING_CONFIRMATION")
                try:
                    _reply_to = task["reply_to_message_id"] if "reply_to_message_id" in task.keys() else None
                except Exception:
                    _reply_to = None
                _send_once_ex(conn, task_id, chat_id, _cpp_result, _reply_to, "project_create_priority")
                return

            _err = str(_cpp_data.get("error") or "PROJECT_ENGINE_NO_ARTIFACT")[:500]
            _user_err = "Проект не создан: " + _err
            _update_task(conn, task_id, state="FAILED", result="", error_message="CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1:" + _err)
            _history(conn, task_id, "CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1:FAILED:" + _err[:200])
            try:
                _reply_to = task["reply_to_message_id"] if "reply_to_message_id" in task.keys() else None
            except Exception:
                _reply_to = None
            _send_once_ex(conn, task_id, chat_id, _user_err, _reply_to, "project_create_priority_error")
            return
    except Exception as _cpp_e:
        logger.warning("CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1_ERR task=%s err=%s", task_id, _cpp_e)
    # === END_CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1 ===
    # === CREATE_ESTIMATE_PRIORITY_NO_ROLLBACK_V1 ===
    try:
        _cep_raw = ""
        try:
            _cep_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
        except Exception:
            _cep_raw = ""
        _cep_clean = re.sub(r"^\s*\[VOICE\]\s*", "", _cep_raw or "", flags=re.I).strip()
        _cep_low = _cep_clean.lower()

        _cep_create_words = (
            "сделай", "создай", "сформируй", "подготовь", "составь",
            "посчитай", "рассчитай", "выгрузи", "сохрани", "оформи"
        )
        _cep_estimate_words = (
            "смет", "расчет", "расчёт", "xlsx", "excel", "эксель",
            "pdf", "ндс", "итог", "объем", "объём", "расценк", "позици"
        )
        _cep_followup_words = (
            "я тебе скидывал", "уже скидывал", "где файл", "где смета",
            "что дальше", "дальше то что", "ты сделал", "что мы делали",
            "какие последние", "покажи прошл", "найди прошл", "помнишь"
        )

        # === CEP_PROJECT_EXCLUSION_V2 ===
        _cep_project_words = (
            "проект", "кж", "кд", "км", "кмд", "ар",
            "фундамент", "фундаментн", "армирован", "арматур", "dxf", "dwg", "чертеж", "чертёж", "конструктив",
        )
        _cep_is_create_estimate = (
            any(w in _cep_low for w in _cep_create_words)
            and any(w in _cep_low for w in _cep_estimate_words)
            and not any(w in _cep_low for w in _cep_followup_words)
            and not any(w in _cep_low for w in _cep_project_words)
        )
        # === END_CEP_PROJECT_EXCLUSION_V2 ===

        if _cep_is_create_estimate:
            from core.estimate_engine import generate_estimate_from_text

            _history(conn, task_id, "CREATE_ESTIMATE_PRIORITY_NO_ROLLBACK_V1:ROUTE_ESTIMATE_ENGINE")
            _cep_data = await generate_estimate_from_text(
                raw_input=_cep_clean,
                task_id=str(task_id),
                topic_id=int(topic_id or 0),
                chat_id=str(chat_id),
            )

            if isinstance(_cep_data, dict):
                _cep_state = str(_cep_data.get("state") or "")
                _cep_success = bool(_cep_data.get("success"))
                _cep_links = []
                for _k in ("drive_link", "google_sheet_link", "link", "pdf_link", "xlsx_link", "telegram_link"):
                    _v = _cep_data.get(_k)
                    if isinstance(_v, str) and _v.startswith("http"):
                        _cep_links.append((_k, _v))
                if isinstance(_cep_data.get("links"), dict):
                    for _k, _v in _cep_data.get("links").items():
                        if isinstance(_v, str) and _v.startswith("http"):
                            _cep_links.append((str(_k), _v))

                _cep_result = str(_cep_data.get("result_text") or _cep_data.get("message") or _cep_data.get("summary") or "").strip()
                if not _cep_result:
                    _cep_result = "Смета обработана"
                # === CLEAN_CEP_RESULT_TEXT_V2 ===
                _clean_lines = []
                for _line in str(_cep_result or "").splitlines():
                    _l = _line.strip()
                    _ll = _l.lower()
                    if not _l:
                        _clean_lines.append(_line)
                        continue
                    if _ll.startswith(("engine:", "manifest:", "артефакт:", "проверка:", "drive_link:", "pdf_link:", "xlsx_link:", "google_sheet_link:", "existing_")):
                        continue
                    if _ll == "ссылки:":
                        continue
                    if _ll.startswith(("- drive_link:", "- pdf_link:", "- xlsx_link:", "- google_sheet_link:", "- existing_")):
                        continue
                    _clean_lines.append(_line)
                _cep_result = "\n".join(_clean_lines).strip()

                if _cep_links and not any(x in _cep_result for x in ("PDF:", "XLSX:", "Google Sheets:")):
                    _seen_public = set()
                    _pdf_public = ""
                    _xlsx_public = ""
                    for _k, _v in _cep_links:
                        _vv = str(_v or "")
                        if not _vv.startswith("http") or _vv in _seen_public:
                            continue
                        _seen_public.add(_vv)
                        if "spreadsheets" in _vv or str(_k).lower() in ("xlsx_link", "google_sheet", "google_sheet_link", "drive_link"):
                            if not _xlsx_public:
                                _xlsx_public = _vv
                        elif ".pdf" in _vv.lower() or "pdf" in str(_k).lower():
                            if not _pdf_public:
                                _pdf_public = _vv
                    _extra = []
                    if _pdf_public:
                        _extra.append("PDF: " + _pdf_public)
                    if _xlsx_public:
                        _extra.append("XLSX: " + _xlsx_public)
                    if _extra:
                        _cep_result += "\n\n" + "\n".join(_extra)
                # === END_CLEAN_CEP_RESULT_TEXT_V2 ===
                if _cep_success or _cep_links or _cep_data.get("artifact_path"):
                    _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_cep_result, error_message="")
                    _history(conn, task_id, "CREATE_ESTIMATE_PRIORITY_NO_ROLLBACK_V1:AWAITING_CONFIRMATION")
                    try:
                        _reply_to = task["reply_to_message_id"] if "reply_to_message_id" in task.keys() else None
                    except Exception:
                        _reply_to = None
                    _send_once_ex(conn, task_id, chat_id, _cep_result, _reply_to, "estimate_create_priority")
                    return

                _cep_err = str(_cep_data.get("error") or "ESTIMATE_ENGINE_NO_ARTIFACT")
                _cep_user = str(_cep_data.get("result_text") or _cep_err)
                _target_state = "WAITING_CLARIFICATION" if _cep_state == "WAITING_CLARIFICATION" else "FAILED"
                _update_task(conn, task_id, state=_target_state, result=_cep_user, error_message=_cep_err)
                _history(conn, task_id, "CREATE_ESTIMATE_PRIORITY_NO_ROLLBACK_V1:" + _target_state)
                try:
                    _reply_to = task["reply_to_message_id"] if "reply_to_message_id" in task.keys() else None
                except Exception:
                    _reply_to = None
                _send_once_ex(conn, task_id, chat_id, _cep_user or _cep_err, _reply_to, "estimate_create_priority_error")
                return

            _update_task(conn, task_id, state="FAILED", result="", error_message="CREATE_ESTIMATE_PRIORITY_NO_ROLLBACK_V1:NON_DICT_RESULT")
            _history(conn, task_id, "CREATE_ESTIMATE_PRIORITY_NO_ROLLBACK_V1:NON_DICT_RESULT")
            return
    except Exception as _cep_e:
        logger.warning("CREATE_ESTIMATE_PRIORITY_NO_ROLLBACK_V1_ERR task=%s err=%s", task_id, _cep_e)
    # === END_CREATE_ESTIMATE_PRIORITY_NO_ROLLBACK_V1 ===
    # === FILE_TECH_CONTOUR_FOLLOWUP_V2 ===
    try:
        _ft_low = str(raw_input or "").strip()
        if _filemem_should_followup(_ft_low):
            _ft_answer = _filemem_build_answer(str(chat_id), int(topic_id or 0), _ft_low)
            if _ft_answer:
                _update_task(conn, task_id, state="DONE", result=_ft_answer, error_message="")
                _history(conn, task_id, "FILE_TECH_CONTOUR_FOLLOWUP_V2:DONE")
                try:
                    _save_memory(str(chat_id), int(topic_id or 0), str(raw_input or ""), _ft_answer)
                except Exception as _e:
                    logger.warning("FILE_TECH_CONTOUR_FOLLOWUP_V2_SAVE_ERR %s", _e)
                try:
                    if _Stage6Archive is not None:
                        _Stage6Archive().archive(
                            {
                                "task_id": task_id,
                                "chat_id": str(chat_id),
                                "topic_id": int(topic_id or 0),
                                "direction": "file_tech_followup",
                                "engine": "file_memory_bridge",
                                "input_type": "text",
                                "raw_input": str(raw_input or ""),
                            },
                            {"text": _ft_answer, "result": {"text": _ft_answer}},
                        )
                except Exception as _e:
                    logger.warning("FILE_TECH_CONTOUR_FOLLOWUP_V2_ARCHIVE_ERR %s", _e)
                try:
                    _append_timeline_event_v1(str(chat_id), int(topic_id or 0), task_id, "file_tech_followup_done", raw_input, _ft_answer)
                except Exception as _e:
                    logger.warning("FILE_TECH_CONTOUR_FOLLOWUP_V2_TIMELINE_ERR %s", _e)
                conn.commit()
                _send_once(conn, task_id, str(chat_id), _ft_answer, reply_to, "file_tech_followup_v2")
                logger.info("FILE_TECH_CONTOUR_FOLLOWUP_V2 done task=%s topic=%s", task_id, topic_id)
                return
    except Exception as _ft_e:
        logger.error("FILE_TECH_CONTOUR_FOLLOWUP_V2_ERR task=%s err=%s", task_id, _ft_e)
    # === END FILE_TECH_CONTOUR_FOLLOWUP_V2 ===
    # === ACTIVE_DIALOG_STATE_V1_TASK_WORKER_HOOK ===
    # === ASYNC_TEMPLATE_WORKFLOW_HOOK_V2 ===
    try:
        if maybe_handle_template_workflow_async is not None:
            _async_tpl = await maybe_handle_template_workflow_async(conn, task, chat_id, topic_id)
            if _async_tpl and _async_tpl.get("handled"):
                _async_state = str(_async_tpl.get("state") or "DONE")
                _async_result = str(_async_tpl.get("result") or "")
                _async_error = str(_async_tpl.get("error") or "")
                _update_task(
                    conn,
                    task_id,
                    state=_async_state,
                    result=_async_result,
                    error_message=_async_error,
                )
                _history(conn, task_id, str(_async_tpl.get("event") or "ASYNC_TEMPLATE_WORKFLOW_HOOK_V2:DONE"))
                try:
                    _reply_to = None
                    if "reply_to_message_id" in task.keys():
                        _reply_to = task["reply_to_message_id"]
                    _send_text = _async_result or _async_error or "Задача обработана через шаблон"
                    _send_once_ex(conn, task_id, chat_id, _send_text, _reply_to, "async_template")
                except Exception as _async_send_e:
                    logger.warning("ASYNC_TEMPLATE_WORKFLOW_HOOK_V2_SEND_ERR task=%s err=%s", task_id, _async_send_e)
                return
    except Exception as _async_tpl_e:
        logger.warning("ASYNC_TEMPLATE_WORKFLOW_HOOK_V2_ERR task=%s err=%s", task_id, _async_tpl_e)
    # === END_ASYNC_TEMPLATE_WORKFLOW_HOOK_V2 ===
    try:
        for _canon_handler in (maybe_handle_template_workflow, maybe_handle_active_dialog):
            if _canon_handler is None:
                continue
            _canon_result = _canon_handler(conn, task, chat_id, topic_id)
            if _canon_result and _canon_result.get("handled"):
                _canon_state = str(_canon_result.get("state") or "DONE")
                _canon_text = str(_canon_result.get("result") or "")
                _canon_error = str(_canon_result.get("error") or "")
                _update_task(conn, task_id, state=_canon_state, result=_canon_text, error_message=_canon_error)
                _history(conn, task_id, str(_canon_result.get("event") or "CANON_REMAINING_CODE_FULL_CLOSE_V1:DONE"))
                try:
                    if save_dialog_event is not None:
                        save_dialog_event(chat_id, topic_id, str(_canon_result.get("event") or "event"), _canon_result)
                except Exception as _sd_e:
                    logger.warning("ACTIVE_DIALOG_STATE_V1_SAVE_ERR %s", _sd_e)
                return
    except Exception as _ads_e:
        logger.warning("ACTIVE_DIALOG_STATE_V1_TASK_WORKER_HOOK_ERR task=%s err=%s", task_id, _ads_e)
    # === END_ACTIVE_DIALOG_STATE_V1_TASK_WORKER_HOOK ===

    # === MEMORY_QUERY_GUARD_V1 ===
    try:
        _mq_low = str(raw_input or "").strip().lower().rstrip("!?. ")
        _mq_low = _mq_low.replace("[voice] ", "").replace("[VOICE] ", "").strip()
        _mq_markers = (
            "что обсуждали", "что делали", "что мы делали", "что мы обсуждали",
            "неделю назад", "две недели", "три недели", "месяц назад",
            "апреля", "марта", "февраля", "января", "помнишь", "напомни",
            "какие задачи были", "что было", "расскажи что",
        )
        if any(m in _mq_low for m in _mq_markers):
            _archive_ctx = _load_archive_context(str(chat_id), int(topic_id or 0), str(raw_input or ""))
            _short_ctx, _long_ctx, _topic_role, _topic_directions = _load_memory_context(str(chat_id), int(topic_id or 0))
            _mq_payload = {
                "id": task_id, "task_id": task_id,
                "chat_id": str(chat_id), "topic_id": int(topic_id or 0),
                "input_type": "text", "state": "IN_PROGRESS",
                "raw_input": str(raw_input or ""),
                "short_memory_context": _short_ctx, "long_memory_context": _long_ctx,
                "archive_context": _archive_ctx, "topic_role": _topic_role,
                "topic_directions": _topic_directions,
                "direction": "memory_query", "engine": "ai_router",
            }
            if not str(_archive_ctx or "").strip() and not str(_long_ctx or "").strip():
                _mq_msg = "В этом топике архивных данных по запросу не найдено"
            else:
                _mq_ai = await asyncio.wait_for(process_ai_task(_mq_payload), timeout=AI_TIMEOUT)
                _mq_msg = _clean(_s(_mq_ai), 12000) or "Архив найден, но ответ не сформирован"
            _update_task(conn, task_id, state="DONE", result=_mq_msg, error_message="")
            _history(conn, task_id, "MEMORY_QUERY_GUARD_V1:DONE")
            try:
                _save_memory(str(chat_id), int(topic_id or 0), str(raw_input or ""), _mq_msg)
            except Exception as _e:
                logger.warning("MEMORY_QUERY_GUARD_V1_SAVE_ERR %s", _e)
            try:
                if _Stage6Archive is not None:
                    _Stage6Archive().archive(_mq_payload, {"text": _mq_msg, "result": {"text": _mq_msg}})
            except Exception as _e:
                logger.warning("MEMORY_QUERY_GUARD_V1_ARCHIVE_ERR %s", _e)
            try:
                _append_timeline_event_v1(str(chat_id), int(topic_id or 0), task_id, "memory_query_done", raw_input, _mq_msg)
            except Exception as _e:
                logger.warning("MEMORY_QUERY_GUARD_V1_TIMELINE_ERR %s", _e)
            conn.commit()
            _send_once(conn, task_id, str(chat_id), _mq_msg, reply_to, "memory_query_guard_v1")
            return
    except Exception as _mq_e:
        logger.error("MEMORY_QUERY_GUARD_V1_ERR task=%s err=%s", task_id, _mq_e)
    # === END MEMORY_QUERY_GUARD_V1 ===
    # === FULLFIX_16_CONTEXT_QUERY ===
    try:
        _ff16_low = str(raw_input or "").strip().lower().rstrip("!?. ")
        _ff16_low = _ff16_low.replace("[voice] ", "").replace("[VOICE] ", "").strip()  # FF21_FIX_VOICE_PREFIX
        _ff16_triggers = ["nu chto", "gde rezultat", "chto tam", "gde smeta", "gde proekt"]
        _ff16_ru_triggers = [
            "ну что",
            "где результат",
            "что там",
            "где смета",
            "где проект",
            "что с задачей",
            "что там у нас",
            "ну как там",
            "где файл",
            "ну что там",
            "ну давай",
            "что по задаче",
        ]
        _ff16_is_ctx = len(_ff16_low) <= 35 and any(
            _ff16_low == t or _ff16_low.startswith(t) for t in _ff16_ru_triggers
        )
        if _ff16_is_ctx:
            _ff16_row = conn.execute(
                "SELECT id,state,result FROM tasks"
                " WHERE chat_id=? AND COALESCE(topic_id,0)=? AND id<>?"
                " AND state IN ('AWAITING_CONFIRMATION','IN_PROGRESS','WAITING_CLARIFICATION')"
                " ORDER BY updated_at DESC LIMIT 1",
                (chat_id, topic_id, task_id)
            ).fetchone()
            if _ff16_row is not None:
                _ff16_pid, _ff16_pst, _ff16_pres = _ff16_row
                _ff16_parts = ["Статус: " + str(_ff16_pst)]
                if _ff16_pres is not None:
                    import re as _re16
                    _ff16_clean = _re16.sub(
                        r"(?im)^\s*MANIFEST\s*:\s*https?://\S+\s*$",
                        "",
                        str(_ff16_pres)[:800]
                    ).strip()
                    _ff16_parts.append(_ff16_clean)
                _ff16_msg = "\n".join(_ff16_parts)
                from core.reply_sender import send_reply_ex
                send_reply_ex(chat_id=str(chat_id), text=_ff16_msg, reply_to_message_id=reply_to, message_thread_id=topic_id)  # FULLFIX_20_CONTEXT_QUERY_TOPIC
                conn.execute(
                    "UPDATE tasks SET state='DONE',result=?,updated_at=datetime('now') WHERE id=?",
                    ("Ответил по активной задаче", task_id)
                )
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, "state:DONE:context_query_ff16")
                )
                conn.commit()
                return
    except Exception as _ff16_ctx_err:
        logger.error("FULLFIX_16_CONTEXT_QUERY_ERROR task=%s err=%s", task_id, _ff16_ctx_err)
    # === END FULLFIX_16_CONTEXT_QUERY ===

    # === FULLFIX_14_UNIFIED_ROUTE ===
    try:
        from core.template_intake_engine import is_sample_intent as _ff14_is_sample, process_template_intake as _ff14_tmpl
        from core.defect_act_engine import is_defect_act_intent as _ff14_is_defect, process_defect_act as _ff14_defect
        from core.multifile_artifact_engine import is_multifile_intent as _ff14_is_multi, process_multifile as _ff14_multi
        from core.estimate_unified_engine import process_estimate_task as _ff14_estimate, parse_estimate_rows as _ff14_parse
        _ff14_raw = str(raw_input or "")
        _ff14_itype = str(_task_field(task, "input_type") or "")
        _ff14_mime = ""
        _ff14_fname = ""
        _ff14_lpath = ""
        if _ff14_itype == "drive_file":
            try:
                import json as _ff14j
                _ff14_meta = _ff14j.loads(_task_field(task, "raw_input") or "{}")
                _ff14_mime = _ff14_meta.get("mime_type", "")
                _ff14_fname = _ff14_meta.get("file_name", "")
                _ff14_lpath = _ff14_meta.get("local_path", "")
            except Exception:
                pass
        # 1. template/sample intake — highest priority
        if _ff14_is_sample(_ff14_raw):
            _ff14_done = await _ff14_tmpl(
                conn=conn, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                raw_input=_ff14_raw, local_path=_ff14_lpath,
                file_name=_ff14_fname, mime_type=_ff14_mime
            )
            if _ff14_done:
                return
        # 2. defect/photo act
        if _ff14_is_defect(_ff14_raw, _ff14_mime):
            _ff14_done = await _ff14_defect(
                conn=conn, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                raw_input=_ff14_raw, file_name=_ff14_fname, local_path=_ff14_lpath
            )
            if _ff14_done:
                return
        # 3. estimate from natural language text
        if _ff14_itype in ("text", "search") and _ff14_parse(_ff14_raw):
            # === FULLFIX_16_ESTIMATE_HARD_STOP ===
            # Estimate route: ALWAYS return, never fall through to FULLFIX_10
            conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (task_id, "FULLFIX_16_ESTIMATE_ROUTE_TAKEN"))
            conn.commit()
            _ff14_done = await _ff14_estimate(
                conn=conn, task_id=task_id, chat_id=chat_id, topic_id=topic_id, raw_input=_ff14_raw
            )
            # Whether success or failure — do not let FULLFIX_10 run on estimate input
            return
            # === END FULLFIX_16_ESTIMATE_HARD_STOP ===
        # 4. multifile aggregation
        if _ff14_is_multi(_ff14_raw):
            _ff14_done = await _ff14_multi(
                conn=conn, task_id=task_id, chat_id=chat_id, topic_id=topic_id, raw_input=_ff14_raw
            )
            if _ff14_done:
                return
    except Exception as _ff14_err:
        try:
            logger.error("FULLFIX_14_ROUTE_ERROR task=%s err=%s", task_id, str(_ff14_err))
        except Exception:
            pass
    # === END FULLFIX_14_UNIFIED_ROUTE ===

# === FULLFIX_13A_SAMPLE_TEMPLATE_AND_TEMPLATE_ESTIMATE_ROUTE ===
    try:
        from core.sample_template_engine import (
            handle_sample_template_intent as _ff13a_handle_sample_template_intent,
            handle_template_estimate_intent as _ff13a_handle_template_estimate_intent,
        )
        # === FULLFIX_13A_ROUTE_LOCALS_FIX ===
        # _handle_new has task/raw_input/reply_to locals, not input_type/reply_to_message_id locals
        _ff13a_conn = conn
        _ff13a_task_id = str(task_id or "")
        _ff13a_chat_id = str(chat_id or "")
        _ff13a_topic_id = int(topic_id or 0)
        _ff13a_raw_input = str(raw_input or "")
        _ff13a_input_type = str(_task_field(task, "input_type", "") or "")
        _ff13a_reply_to = _task_field(task, "reply_to_message_id", None) or _task_field(task, "telegram_message_id", None)
        # === END FULLFIX_13A_ROUTE_LOCALS_FIX ===
        _ff13a_done = await _ff13a_handle_sample_template_intent(
            conn=_ff13a_conn,
            task_id=_ff13a_task_id,
            chat_id=_ff13a_chat_id,
            topic_id=_ff13a_topic_id,
            raw_input=_ff13a_raw_input,
            input_type=_ff13a_input_type,
            reply_to_message_id=_ff13a_reply_to,
        )
        # === FULLFIX_13B_SAMPLE_HARD_STOP_1 ===
        if _ff13a_done:
            try:
                conn.commit()
            except Exception:
                pass
            return
        _ff13a_done = await _ff13a_handle_template_estimate_intent(
            conn=_ff13a_conn,
            task_id=_ff13a_task_id,
            chat_id=_ff13a_chat_id,
            topic_id=_ff13a_topic_id,
            raw_input=_ff13a_raw_input,
            input_type=_ff13a_input_type,
            reply_to_message_id=_ff13a_reply_to,
        )
        # === FULLFIX_13B_SAMPLE_HARD_STOP_2 ===
        if _ff13a_done:
            try:
                conn.commit()
            except Exception:
                pass
            return
    except Exception as _ff13a_err:
        try:
            logger.error("FULLFIX_13A_SAMPLE_ROUTE_ERROR task=%s err=%s", task_id, str(_ff13a_err))
        except Exception:
            pass
    # === END FULLFIX_13A_SAMPLE_TEMPLATE_AND_TEMPLATE_ESTIMATE_ROUTE ===


    # === FULLFIX_19_PROJECT_GUARD_REAL_V2 ===
    try:
        _ff19_low = str(raw_input or "").strip().lower()
        _ff19_short_replies = {"да","нет","ок","готово","угу","так","ясно","понятно"}
        if _ff19_low in _ff19_short_replies:
            try:
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, "FULLFIX_19_PROJECT_GUARD_BLOCKED_SHORT_REPLY")
                )
                conn.execute(
                    "UPDATE tasks SET state='DONE', updated_at=datetime('now'), result=COALESCE(NULLIF(result,''),?) WHERE id=?",
                    ("Принято", task_id)
                )
                conn.commit()
            except Exception:
                pass
            logger.info("FF19_GUARD_BLOCKED_SHORT_REPLY task=%s text=%s", task_id, _ff19_low)
            return
    except Exception as _ff19_err:
        logger.error("FF19_PROJECT_GUARD_ERR task=%s err=%s", task_id, _ff19_err)
    # === END FULLFIX_19_PROJECT_GUARD_REAL_V2 ===

    # === FULLFIX_13B_FALSE_PROJECT_PHRASE_GUARD ===
    try:
        _ff13b_low = str(raw_input or "").strip().lower()
        _ff13b_false_project_phrases = {
            "это один из вариантов",
            "это как образец",
            "это пример",
            "вот образец",
            "вот пример",
            "сохрани как образец",
        }
        if _ff13b_low in _ff13b_false_project_phrases:
            _msg = "Принял как образец. Дальше можно писать простым языком: сделай смету / сделай проект"
            await safe_update(conn, task_id, state="DONE", result=_ff13c_strip_manifest_links(_msg), error_message="")
            try:
                from core.reply_sender import send_reply_ex
                send_reply_ex(chat_id=str(chat_id), text=_ff13c_strip_manifest_links(_msg), reply_to_message_id=reply_to)
            except Exception:
                pass
            try:
                conn.execute("INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))", (task_id, "FULLFIX_13B_FALSE_PROJECT_GUARDED"))
                conn.commit()
            except Exception:
                pass
            return
    except Exception as _ff13b_guard_err:
        try:
            logger.error("FULLFIX_13B_FALSE_PROJECT_GUARD_ERROR task=%s err=%s", task_id, str(_ff13b_guard_err))
        except Exception:
            pass
    # === END FULLFIX_13B_FALSE_PROJECT_PHRASE_GUARD ===

    # === FULLFIX_10_TOTAL_CLOSURE_UNIVERSAL_ROUTE ===
    try:
        from core.orchestra_closure_engine import (
            classify_user_task as _ff10_classify_user_task,
            classify_project_kind as _ff10_classify_project_kind,
            create_estimate_files as _ff10_create_estimate_files,
            save_result_memory as _ff10_save_result_memory,
            ENGINE as _FF10_ENGINE,
        )

        _ff10_intent = _ff10_classify_user_task(str(raw_input or ""))


        # === FULLFIX_13B_CLEAN_ESTIMATE_MESSAGE_BEFORE_SEND_FALLBACK ===
        def _ff13b_clean_any_estimate_text(_txt):
            try:
                from core.orchestra_closure_engine import ff13b_clean_estimate_user_message
                return ff13b_clean_estimate_user_message(_txt)
            except Exception:
                return _txt
        # === END FULLFIX_13B_CLEAN_ESTIMATE_MESSAGE_BEFORE_SEND_FALLBACK ===

        if _ff10_intent in ("confirm", "revision"):
            _ff10_parent = conn.execute(
                """
                SELECT id,state,result,reply_to_message_id,bot_message_id
                FROM tasks
                WHERE chat_id=?
                  AND COALESCE(topic_id,0)=?
                  AND state='AWAITING_CONFIRMATION'
                  AND id<>?
                ORDER BY updated_at DESC, created_at DESC
                LIMIT 1
                """,
                (str(chat_id), int(topic_id or 0), task_id),
            ).fetchone()

            if _ff10_parent and _ff10_intent == "confirm":
                _parent_id = _s(_ff10_parent["id"])
                _update_task(conn, _parent_id, state="DONE", error_message="")
                _history(conn, _parent_id, "FULLFIX_10_CONFIRM_DONE")
                _update_task(conn, task_id, state="DONE", result="Подтверждение принято. Задача закрыта", error_message="")
                _history(conn, task_id, "FULLFIX_10_CONFIRM_CHILD_DONE")
                conn.commit()
                _send_once(conn, task_id, chat_id, "Подтверждение принято. Задача закрыта", reply_to, "ff10_confirm_done")
                return

            if _ff10_parent and _ff10_intent == "revision":
                _parent_id = _s(_ff10_parent["id"])
                _merged = _clean(_s(_ff10_parent["result"]) + "\n\nПравки пользователя:\n" + str(raw_input or ""), 12000)
                _update_task(conn, _parent_id, state="IN_PROGRESS", raw_input=_merged, error_message="")
                _history(conn, _parent_id, "FULLFIX_10_REVISION_REOPEN")
                _update_task(conn, task_id, state="DONE", result="Правки приняты. Задача возвращена в работу", error_message="")
                _history(conn, task_id, "FULLFIX_10_REVISION_CHILD_DONE")
                conn.commit()
                _send_once(conn, task_id, chat_id, "Правки приняты. Задача возвращена в работу", reply_to, "ff10_revision_reopen")
                return

        if _ff10_intent == "project":
            _kind, _section = _ff10_classify_project_kind(str(raw_input or ""))
            if _kind == "foundation_slab":
                from core.project_engine import create_project_pdf_dxf_artifact
                _ff10_res = await create_project_pdf_dxf_artifact(str(raw_input or ""), task_id, int(topic_id or 0), "FULLFIX_10_SIMPLE_USER_REQUEST", True)

                if not isinstance(_ff10_res, dict) or not _ff10_res.get("success"):
                    _err = str((_ff10_res or {}).get("error", "PROJECT_FAILED"))[:400]
                    _msg = "Проект не создан: " + _err
                    _update_task(conn, task_id, state="FAILED", result=_ff13c_strip_manifest_links(_msg), error_message=_err)
                    _history(conn, task_id, "FULLFIX_10_PROJECT_FAILED:" + _err)
                    conn.commit()
                    _send_once(conn, task_id, chat_id, _msg, reply_to, "ff10_project_failed")
                    return

                _pdf = str(_ff10_res.get("pdf_link") or "")
                _dxf = str(_ff10_res.get("dxf_link") or "")
                _xlsx = str(_ff10_res.get("xlsx_link") or "")
                _manifest = str(_ff10_res.get("manifest_link") or "")
                _sheet_count = str(_ff10_res.get("sheet_count") or "")
                _engine = str(_ff10_res.get("engine") or _FF10_ENGINE)
                _msg = (
                    "Проект создан\n"
                    f"Engine: {_engine}\n"
                    "Раздел: КЖ\n"
                    f"Тип: фундаментная плита\n"
                    f"Листов: {_sheet_count}\n"
                    f"PDF: {_pdf}\n"
                    f"DXF: {_dxf}\n"
                    f"XLSX: {_xlsx}\n"
                    f"MANIFEST: {_manifest}\n\n"
                    "Доволен результатом? Ответь: Да / Уточни / Правки"
                )
                if not _pdf or not _dxf:
                    _update_task(conn, task_id, state="FAILED", result="Проект не создан: нет PDF/DXF ссылки", error_message="PROJECT_LINKS_MISSING")
                    _history(conn, task_id, "FULLFIX_10_PROJECT_LINKS_MISSING")
                    conn.commit()
                    _send_once(conn, task_id, chat_id, "Проект не создан: нет PDF/DXF ссылки", reply_to, "ff10_project_links_missing")
                    return

                    # === RESULT_VALIDATOR_GUARD_V1 ===
                    if _check_result_before_confirm(_ff13c_strip_manifest_links(_msg)):
                        # === TASK_WORKER_ARTIFACT_GATE_V1 ===
                        try:
                            if validate_engine_result is not None:
                                _twag_raw = ""
                                _twag_input_type = ""
                                try:
                                    _twag_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
                                except Exception:
                                    _twag_raw = ""
                                try:
                                    _twag_input_type = str(task["input_type"] if "input_type" in task.keys() else "")
                                except Exception:
                                    _twag_input_type = ""
                                _twag_result = _ff13c_strip_manifest_links(_msg)
                                _twag_check = validate_engine_result(
                                    {"summary": _twag_result, "engine": "TASK_WORKER_ARTIFACT_GATE_V1"},
                                    input_type=_twag_input_type,
                                    user_text=_twag_raw,
                                    topic_id=topic_id,
                                )
                                if not _twag_check.get("ok"):
                                    _update_task(conn, task_id, state="FAILED", result="",
                                        error_message="TASK_WORKER_ARTIFACT_GATE_V1:" + str(_twag_check.get("reason") or "INVALID"))
                                    _history(conn, task_id, "TASK_WORKER_ARTIFACT_GATE_V1:FAILED:" + str(_twag_check.get("reason") or "INVALID"))
                                    return
                        except Exception as _twag_e:
                            logger.warning("TASK_WORKER_ARTIFACT_GATE_V1_ERR task=%s err=%s", task_id, _twag_e)
                        # === END_TASK_WORKER_ARTIFACT_GATE_V1 ===
                        _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(_msg), error_message="")
                    else:
                        _update_task(conn, task_id, state="FAILED", result=_ff13c_strip_manifest_links(_msg), error_message="FORBIDDEN_PHRASE")
                    # === END RESULT_VALIDATOR_GUARD_V1 ===
                _history(conn, task_id, "FULLFIX_10_PROJECT_OK")
                conn.commit()
                _sent = _send_once_ex(conn, task_id, str(chat_id), _msg, reply_to, "ff10_project_result")
                if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                    _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                    conn.commit()
                _ff10_save_result_memory(str(chat_id), int(topic_id or 0), str(raw_input or ""), _msg, _ff10_res)
                return

        if _ff10_intent == "estimate":
            _ff10_res = _ff10_create_estimate_files(str(raw_input or ""), task_id, int(topic_id or 0))
            if not isinstance(_ff10_res, dict) or not _ff10_res.get("success"):
                _err = str((_ff10_res or {}).get("error", "ESTIMATE_FAILED"))[:400]
                _msg = "Смета не создана: " + _err
                _update_task(conn, task_id, state="FAILED", result=_ff13c_strip_manifest_links(_msg), error_message=_err)
                _history(conn, task_id, "FULLFIX_10_ESTIMATE_FAILED:" + _err)
                conn.commit()
                _send_once(conn, task_id, chat_id, _msg, reply_to, "ff10_estimate_failed")
                return

            _msg = str(_ff10_res.get("message") or "")
            # === RESULT_VALIDATOR_GUARD_V1 ===
            if _check_result_before_confirm(_ff13c_strip_manifest_links(_msg)):
                # === TASK_WORKER_ARTIFACT_GATE_V1 ===
                try:
                    if validate_engine_result is not None:
                        _twag_raw = ""
                        _twag_input_type = ""
                        try:
                            _twag_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
                        except Exception:
                            _twag_raw = ""
                        try:
                            _twag_input_type = str(task["input_type"] if "input_type" in task.keys() else "")
                        except Exception:
                            _twag_input_type = ""
                        _twag_result = _ff13c_strip_manifest_links(_msg)
                        _twag_check = validate_engine_result(
                            {"summary": _twag_result, "engine": "TASK_WORKER_ARTIFACT_GATE_V1"},
                            input_type=_twag_input_type,
                            user_text=_twag_raw,
                            topic_id=topic_id,
                        )
                        if not _twag_check.get("ok"):
                            _update_task(conn, task_id, state="FAILED", result="",
                                error_message="TASK_WORKER_ARTIFACT_GATE_V1:" + str(_twag_check.get("reason") or "INVALID"))
                            _history(conn, task_id, "TASK_WORKER_ARTIFACT_GATE_V1:FAILED:" + str(_twag_check.get("reason") or "INVALID"))
                            return
                except Exception as _twag_e:
                    logger.warning("TASK_WORKER_ARTIFACT_GATE_V1_ERR task=%s err=%s", task_id, _twag_e)
                # === END_TASK_WORKER_ARTIFACT_GATE_V1 ===
                _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(_msg), error_message="")
            else:
                _update_task(conn, task_id, state="FAILED", result=_ff13c_strip_manifest_links(_msg), error_message="FORBIDDEN_PHRASE")
            # === END RESULT_VALIDATOR_GUARD_V1 ===
            _history(conn, task_id, "FULLFIX_10_ESTIMATE_OK")
            conn.commit()
            _sent = _send_once_ex(conn, task_id, str(chat_id), _msg, reply_to, "ff10_estimate_result")
            if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                conn.commit()
            _ff10_save_result_memory(str(chat_id), int(topic_id or 0), str(raw_input or ""), _msg, _ff10_res)
            return

    except Exception as _ff10_e:
        _err = str(_ff10_e)[:500]
        _update_task(conn, task_id, state="FAILED", result="Ошибка FULLFIX_10: " + _err, error_message=_err)
        _history(conn, task_id, "FULLFIX_10_EXCEPTION:" + _err)
        conn.commit()
        _send_once(conn, task_id, chat_id, "Ошибка FULLFIX_10: " + _err, reply_to, "ff10_exception")
        return
    # === END FULLFIX_10_TOTAL_CLOSURE_UNIVERSAL_ROUTE ===

    # === FULLFIX_07_PROJECT_DESIGN_CLOSURE_ROUTE ===
    _ff07_low = str(raw_input or "").lower()
    _ff07_triggers = (
        "создай проект",
        "сделай проект",
        "проект фундамент",
        "проект фундаментной плиты",
        "план фундамент",
        "план фундаментной плиты",
        "фундаментной плиты",
        "проект по образцу",
        "по образцу проект",
        "проект по шаблону",
        "dxf проект",
        "dwg проект",
    )
    if any(x in _ff07_low for x in _ff07_triggers):
        try:
            from core.project_engine import create_project_pdf_dxf_artifact
            _ff07_res = await create_project_pdf_dxf_artifact(str(raw_input), task_id, int(topic_id or 0), "", True)

            if not isinstance(_ff07_res, dict) or not _ff07_res.get("success"):
                _err = str((_ff07_res or {}).get("error", "PROJECT_FAILED"))[:500]
                _update_task(
                    conn,
                    task_id,
                    state="FAILED",
                    result="Проект не создан: нет полного комплекта PDF/DXF/XLSX/MANIFEST или шаблон неполный",
                    error_message=_err,
                )
                _history(conn, task_id, "FULLFIX_07_FAILED:" + _err)
                conn.commit()
                _send_once(
                    conn,
                    task_id,
                    chat_id,
                    "Проект не создан: нет полного комплекта PDF/DXF/XLSX/MANIFEST или шаблон неполный",
                    reply_to,
                    "project_failed",
                )
                return

            _pdf = str(_ff07_res.get("pdf_link") or "")
            _dxf = str(_ff07_res.get("dxf_link") or "")
            _xlsx = str(_ff07_res.get("xlsx_link") or "")
            _manifest = str(_ff07_res.get("manifest_link") or "")
            _engine = str(_ff07_res.get("engine") or "FULLFIX_07_PROJECT_DESIGN_CLOSURE")
            _tpl = str(_ff07_res.get("template_file") or "")
            _sheet_count = str(_ff07_res.get("sheet_count") or "0")
            _sec = str(_ff07_res.get("section") or "КЖ")

            _msg = (
                "Проект создан\n"
                f"Engine: {_engine}\n"
                f"Раздел: {_sec}\n"
                f"Листов: {_sheet_count}\n"
                f"Шаблон: {_tpl}\n"
                f"PDF: {_pdf}\n"
                f"DXF: {_dxf}\n"
                f"XLSX: {_xlsx}\n"
                f"MANIFEST: {_manifest}\n\n"
                "Доволен результатом? Ответь: Да / Уточни / Правки"
            )

            # === RESULT_VALIDATOR_GUARD_V1 ===
            if _check_result_before_confirm(_ff13c_strip_manifest_links(_msg)):
                # === TASK_WORKER_ARTIFACT_GATE_V1 ===
                try:
                    if validate_engine_result is not None:
                        _twag_raw = ""
                        _twag_input_type = ""
                        try:
                            _twag_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
                        except Exception:
                            _twag_raw = ""
                        try:
                            _twag_input_type = str(task["input_type"] if "input_type" in task.keys() else "")
                        except Exception:
                            _twag_input_type = ""
                        _twag_result = _ff13c_strip_manifest_links(_msg)
                        _twag_check = validate_engine_result(
                            {"summary": _twag_result, "engine": "TASK_WORKER_ARTIFACT_GATE_V1"},
                            input_type=_twag_input_type,
                            user_text=_twag_raw,
                            topic_id=topic_id,
                        )
                        if not _twag_check.get("ok"):
                            _update_task(conn, task_id, state="FAILED", result="",
                                error_message="TASK_WORKER_ARTIFACT_GATE_V1:" + str(_twag_check.get("reason") or "INVALID"))
                            _history(conn, task_id, "TASK_WORKER_ARTIFACT_GATE_V1:FAILED:" + str(_twag_check.get("reason") or "INVALID"))
                            return
                except Exception as _twag_e:
                    logger.warning("TASK_WORKER_ARTIFACT_GATE_V1_ERR task=%s err=%s", task_id, _twag_e)
                # === END_TASK_WORKER_ARTIFACT_GATE_V1 ===
                _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(_msg), error_message="")
            else:
                _update_task(conn, task_id, state="FAILED", result=_ff13c_strip_manifest_links(_msg), error_message="FORBIDDEN_PHRASE")
            # === END RESULT_VALIDATOR_GUARD_V1 ===
            _history(conn, task_id, "FULLFIX_07_PROJECT_OK")
            conn.commit()

            try:
                _sent = _send_once_ex(conn, task_id, str(chat_id), _msg, reply_to, "project_fullfix_07_result")
                if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                    _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                    conn.commit()
            except Exception:
                _send_once(conn, task_id, chat_id, _msg, reply_to, "project_fullfix_07_result")
            return

        except Exception as _ff07_e:
            _err = str(_ff07_e)[:700]
            _update_task(
                conn,
                task_id,
                state="FAILED",
                result="Проект не создан: ошибка генерации полного комплекта: " + _err,
                error_message=_err,
            )
            _history(conn, task_id, "FULLFIX_07_EXCEPTION:" + _err)
            conn.commit()
            _send_once(conn, task_id, chat_id, "Проект не создан: ошибка генерации полного комплекта: " + _err, reply_to, "project_exception")
            return
    # === END FULLFIX_07_PROJECT_DESIGN_CLOSURE_ROUTE ===


    # === FULLFIX_07_CAD_PROJECT_DOCUMENTATION_ROUTE ===
    try:
        from core.cad_project_engine import is_project_design_request, create_full_project_package, format_project_result_message
        if is_project_design_request(raw_input):
            _ff07_res = create_full_project_package(str(raw_input), task_id, int(topic_id or 0), "")
            _ff07_msg = format_project_result_message(_ff07_res)
            if not isinstance(_ff07_res, dict) or not _ff07_res.get("success"):
                _err = str((_ff07_res or {}).get("error") or "PROJECT_DOCUMENTATION_FAILED")[:300]
                _update_task(conn, task_id, state="FAILED", result=_ff07_msg, error_message=_err)
                _history(conn, task_id, "FULLFIX_07_PROJECT_FAILED:" + _err)
                conn.commit()
                _send_once(conn, task_id, chat_id, _ff07_msg, reply_to, "ff07_project_failed")
                return

                # === RESULT_VALIDATOR_GUARD_V1 ===
                if _check_result_before_confirm(_ff07_msg):
                    # === TASK_WORKER_ARTIFACT_GATE_V1 ===
                    try:
                        if validate_engine_result is not None:
                            _twag_raw = ""
                            _twag_input_type = ""
                            try:
                                _twag_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
                            except Exception:
                                _twag_raw = ""
                            try:
                                _twag_input_type = str(task["input_type"] if "input_type" in task.keys() else "")
                            except Exception:
                                _twag_input_type = ""
                            _twag_result = _ff07_msg
                            _twag_check = validate_engine_result(
                                {"summary": _twag_result, "engine": "TASK_WORKER_ARTIFACT_GATE_V1"},
                                input_type=_twag_input_type,
                                user_text=_twag_raw,
                                topic_id=topic_id,
                            )
                            if not _twag_check.get("ok"):
                                _update_task(conn, task_id, state="FAILED", result="",
                                    error_message="TASK_WORKER_ARTIFACT_GATE_V1:" + str(_twag_check.get("reason") or "INVALID"))
                                _history(conn, task_id, "TASK_WORKER_ARTIFACT_GATE_V1:FAILED:" + str(_twag_check.get("reason") or "INVALID"))
                                return
                    except Exception as _twag_e:
                        logger.warning("TASK_WORKER_ARTIFACT_GATE_V1_ERR task=%s err=%s", task_id, _twag_e)
                    # === END_TASK_WORKER_ARTIFACT_GATE_V1 ===
                    _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff07_msg, error_message="")
                else:
                    _update_task(conn, task_id, state="FAILED", result=_ff07_msg, error_message="FORBIDDEN_PHRASE")
                # === END RESULT_VALIDATOR_GUARD_V1 ===
            _history(conn, task_id, "FULLFIX_07_PROJECT_OK")
            conn.commit()
            _sent = _send_once_ex(conn, task_id, str(chat_id), _ff07_msg, reply_to, "ff07_project_result")
            if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                conn.commit()
            return
    except Exception as _ff07_e:
        _err = str(_ff07_e)[:500]
        _update_task(conn, task_id, state="FAILED", result="Проект не создан: ошибка FULLFIX_07", error_message=_err)
        _history(conn, task_id, "FULLFIX_07_EXCEPTION:" + _err)
        conn.commit()
        _send_once(conn, task_id, chat_id, "Проект не создан: ошибка FULLFIX_07", reply_to, "ff07_project_exception")
        return
    # === END FULLFIX_07_CAD_PROJECT_DOCUMENTATION_ROUTE ===

    # === FULLFIX_06_FINAL_PROJECT_TEMPLATE_ROUTE ===
    _ff06_low = str(raw_input or "").lower()
    _ff06_project_triggers = (
        "создай проект",
        "сделай проект",
        "разработай проект",
        "готовый проект",
        "проект фундамент",
        "проект фундаментной плиты",
        "проект кровли",
        "проект по образцу",
        "проект по шаблону",
        "план фундаментной плиты",
        "чертеж фундаментной плиты",
        "чертёж фундаментной плиты",
    )
    if any(x in _ff06_low for x in _ff06_project_triggers):
        try:
            from core.project_engine import create_project_pdf_dxf_artifact
            _ff06_res = await create_project_pdf_dxf_artifact(str(raw_input), task_id, int(topic_id or 0), "", True)
            if not isinstance(_ff06_res, dict) or not _ff06_res.get("success"):
                _err = str((_ff06_res or {}).get("error", "PROJECT_FAILED"))[:300]
                _update_task(conn, task_id, state="FAILED", result="Проект не создан: нет сохранённого шаблона или не созданы PDF/DXF/XLSX ссылки", error_message=_err)
                _history(conn, task_id, "FULLFIX_06_PROJECT_FAILED:" + _err)
                conn.commit()
                _send_once(conn, task_id, chat_id, "Проект не создан: нет сохранённого шаблона или не созданы PDF/DXF/XLSX ссылки", reply_to, "project_failed_ff06")
                return

            _msg = (
                "Проект создан по сохранённому шаблону\n"
                f"Раздел: {_ff06_res.get('section')}\n"
                f"Листов по шаблону: {_ff06_res.get('sheet_count')}\n"
                f"Шаблон: {_ff06_res.get('template_file')}\n"
                f"PDF: {_ff06_res.get('pdf_link')}\n"
                f"DXF: {_ff06_res.get('dxf_link')}\n"
                f"XLSX: {_ff06_res.get('xlsx_link')}\n"
                f"MANIFEST: {_ff06_res.get('manifest_link')}\n\n"
                "Доволен результатом? Ответь: Да / Уточни / Правки"
            )
            # === RESULT_VALIDATOR_GUARD_V1 ===
            if _check_result_before_confirm(_ff13c_strip_manifest_links(_msg)):
                # === TASK_WORKER_ARTIFACT_GATE_V1 ===
                try:
                    if validate_engine_result is not None:
                        _twag_raw = ""
                        _twag_input_type = ""
                        try:
                            _twag_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
                        except Exception:
                            _twag_raw = ""
                        try:
                            _twag_input_type = str(task["input_type"] if "input_type" in task.keys() else "")
                        except Exception:
                            _twag_input_type = ""
                        _twag_result = _ff13c_strip_manifest_links(_msg)
                        _twag_check = validate_engine_result(
                            {"summary": _twag_result, "engine": "TASK_WORKER_ARTIFACT_GATE_V1"},
                            input_type=_twag_input_type,
                            user_text=_twag_raw,
                            topic_id=topic_id,
                        )
                        if not _twag_check.get("ok"):
                            _update_task(conn, task_id, state="FAILED", result="",
                                error_message="TASK_WORKER_ARTIFACT_GATE_V1:" + str(_twag_check.get("reason") or "INVALID"))
                            _history(conn, task_id, "TASK_WORKER_ARTIFACT_GATE_V1:FAILED:" + str(_twag_check.get("reason") or "INVALID"))
                            return
                except Exception as _twag_e:
                    logger.warning("TASK_WORKER_ARTIFACT_GATE_V1_ERR task=%s err=%s", task_id, _twag_e)
                # === END_TASK_WORKER_ARTIFACT_GATE_V1 ===
                _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(_msg), error_message="")
            else:
                _update_task(conn, task_id, state="FAILED", result=_ff13c_strip_manifest_links(_msg), error_message="FORBIDDEN_PHRASE")
            # === END RESULT_VALIDATOR_GUARD_V1 ===
            _history(conn, task_id, "FULLFIX_06_PROJECT_OK")
            conn.commit()
            _sent = _send_once_ex(conn, task_id, str(chat_id), _msg, reply_to, "project_result_ff06")
            if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                conn.commit()
            return
        except Exception as _ff06_e:
            _err = str(_ff06_e)[:500]
            _update_task(conn, task_id, state="FAILED", result="Проект не создан: ошибка генерации PDF/DXF/XLSX", error_message=_err)
            _history(conn, task_id, "FULLFIX_06_PROJECT_EXCEPTION:" + _err)
            conn.commit()
            _send_once(conn, task_id, chat_id, "Проект не создан: ошибка генерации PDF/DXF/XLSX", reply_to, "project_exception_ff06")
            return
    # === END FULLFIX_06_FINAL_PROJECT_TEMPLATE_ROUTE ===


    role = _detect_role_assignment(raw_input)
    if role:
        ask = f"Понял назначение чата так:\n{role}\n\nПодтверди или уточни"
        # === RESULT_VALIDATOR_GUARD_V1 ===
        if _check_result_before_confirm(ask):
            # === TASK_WORKER_ARTIFACT_GATE_V1 ===
            try:
                if validate_engine_result is not None:
                    _twag_raw = ""
                    _twag_input_type = ""
                    try:
                        _twag_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
                    except Exception:
                        _twag_raw = ""
                    try:
                        _twag_input_type = str(task["input_type"] if "input_type" in task.keys() else "")
                    except Exception:
                        _twag_input_type = ""
                    _twag_result = ask
                    _twag_check = validate_engine_result(
                        {"summary": _twag_result, "engine": "TASK_WORKER_ARTIFACT_GATE_V1"},
                        input_type=_twag_input_type,
                        user_text=_twag_raw,
                        topic_id=topic_id,
                    )
                    if not _twag_check.get("ok"):
                        _update_task(conn, task_id, state="FAILED", result="",
                            error_message="TASK_WORKER_ARTIFACT_GATE_V1:" + str(_twag_check.get("reason") or "INVALID"))
                        _history(conn, task_id, "TASK_WORKER_ARTIFACT_GATE_V1:FAILED:" + str(_twag_check.get("reason") or "INVALID"))
                        return
            except Exception as _twag_e:
                logger.warning("TASK_WORKER_ARTIFACT_GATE_V1_ERR task=%s err=%s", task_id, _twag_e)
            # === END_TASK_WORKER_ARTIFACT_GATE_V1 ===
            _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=ask, error_message="")
        else:
            _update_task(conn, task_id, state="FAILED", result=ask, error_message="FORBIDDEN_PHRASE")
        # === END RESULT_VALIDATOR_GUARD_V1 ===
        _history(conn, task_id, "state:AWAITING_CONFIRMATION")
        conn.commit()
        _send_once(conn, task_id, chat_id, ask, reply_to, "role_confirmation")
        return

    pending_confirm = conn.execute(
        """
        SELECT id, COALESCE(raw_input,'') AS raw_input, COALESCE(result,'') AS result
        FROM tasks
        WHERE chat_id=?
          AND id<>?
          AND COALESCE(topic_id,0)=?
          AND state='AWAITING_CONFIRMATION'
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), task_id, int(topic_id)),
    ).fetchone()

    if pending_confirm:
        pending_id = _s(pending_confirm["id"])
        pending_role = _extract_role_confirmation(_s(pending_confirm["result"]))
        if pending_role and _is_confirm_intent(raw_input):
            _save_topic_role(chat_id, topic_id, pending_role)
            _update_task(conn, pending_id, state="DONE", result=f"Чат закреплён за: {pending_role}", error_message="")
            _history(conn, pending_id, f"role_saved:{pending_role}")
            _update_task(conn, task_id, state="DONE", result="Подтверждение принято", error_message="")
            _history(conn, task_id, "confirm_accepted")
            conn.commit()
            _send_once(conn, task_id, chat_id, f"Принял. Чат закреплён за: {pending_role}", reply_to, "role_saved")
            return
        if pending_role and _is_revision_intent(raw_input):
            _update_task(conn, pending_id, raw_input=raw_input, state="NEW", result="", error_message="")
            _history(conn, pending_id, "role_revision_requested")
            _update_task(conn, task_id, state="DONE", result="Правки приняты", error_message="")
            _history(conn, task_id, "state:DONE")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Принял правки. Уточни назначение чата одной фразой", reply_to, "role_revision_ok")
            return
        if _is_confirm_intent(raw_input):
            _finalize_done(conn, pending_id, chat_id, topic_id, reply_to)
            _update_task(conn, task_id, state="DONE", result="Подтверждение принято", error_message="")
            _history(conn, task_id, "confirm_accepted")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Принял. Задача закрыта", reply_to, "confirm_done")
            return
        if _is_revision_intent(raw_input):
            merged = _clean(_s(pending_confirm["raw_input"]) + "\n\nУточнение пользователя:\n" + raw_input, 12000)
            _update_task(conn, pending_id, raw_input=merged, state="IN_PROGRESS", error_message="")
            _history(conn, pending_id, "revision_accepted")
            _update_task(conn, task_id, state="DONE", result="Правки приняты", error_message="")
            _history(conn, task_id, "state:DONE")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Принял правки. Делаю", reply_to, "revision_ok")
            return

    # === FULLFIX_05_REQUIRE_REAL_PDF_DXF_PROJECT ===
    _ff05_low = str(raw_input or "").lower()
    _ff05_project_triggers = (
        "создай проект",
        "сделай проект",
        "проект фундамент",
        "проект фундаментной плиты",
        "план фундамент",
        "план фундаментной плиты",
        "фундаментной плиты",
        "проект по образцу",
        "проект по шаблону",
        "сделай по образцу",
    )
    if any(x in _ff05_low for x in _ff05_project_triggers):
        try:
            from core.project_engine import create_project_pdf_dxf_artifact
            _ff05_res = await create_project_pdf_dxf_artifact(str(raw_input), task_id, int(topic_id or 0), "")
            if not isinstance(_ff05_res, dict) or not _ff05_res.get("success"):
                _err = str((_ff05_res or {}).get("error", "PROJECT_FAILED"))[:300]
                _update_task(
                    conn,
                    task_id,
                    state="FAILED",
                    result="Проект не создан: нет PDF/DXF файла или ссылки",
                    error_message=_err,
                )
                _history(conn, task_id, "FULLFIX_05_PROJECT_FAILED:" + _err)
                conn.commit()
                _send_once(
                    conn,
                    task_id,
                    chat_id,
                    "Проект не создан: нет PDF/DXF файла или ссылки",
                    reply_to,
                    "project_failed",
                )
                return

            _pdf = str(_ff05_res.get("pdf_link") or "")
            _dxf = str(_ff05_res.get("dxf_link") or "")
            _manifest = str(_ff05_res.get("manifest_link") or "")
            _sec = str(_ff05_res.get("section") or "КЖ")
            _msg = (
                f"Проект создан как PDF/DXF комплект\n"
                f"Раздел: {_sec}\n"
                f"PDF: {_pdf}\n"
                f"DXF: {_dxf}\n"
            )
            if _manifest:
                _msg += f"MANIFEST: {_manifest}\n"
            _msg += "\nДоволен результатом? Ответь: Да / Уточни / Правки"

            # === RESULT_VALIDATOR_GUARD_V1 ===
            if _check_result_before_confirm(_ff13c_strip_manifest_links(_msg)):
                # === TASK_WORKER_ARTIFACT_GATE_V1 ===
                try:
                    if validate_engine_result is not None:
                        _twag_raw = ""
                        _twag_input_type = ""
                        try:
                            _twag_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
                        except Exception:
                            _twag_raw = ""
                        try:
                            _twag_input_type = str(task["input_type"] if "input_type" in task.keys() else "")
                        except Exception:
                            _twag_input_type = ""
                        _twag_result = _ff13c_strip_manifest_links(_msg)
                        _twag_check = validate_engine_result(
                            {"summary": _twag_result, "engine": "TASK_WORKER_ARTIFACT_GATE_V1"},
                            input_type=_twag_input_type,
                            user_text=_twag_raw,
                            topic_id=topic_id,
                        )
                        if not _twag_check.get("ok"):
                            _update_task(conn, task_id, state="FAILED", result="",
                                error_message="TASK_WORKER_ARTIFACT_GATE_V1:" + str(_twag_check.get("reason") or "INVALID"))
                            _history(conn, task_id, "TASK_WORKER_ARTIFACT_GATE_V1:FAILED:" + str(_twag_check.get("reason") or "INVALID"))
                            return
                except Exception as _twag_e:
                    logger.warning("TASK_WORKER_ARTIFACT_GATE_V1_ERR task=%s err=%s", task_id, _twag_e)
                # === END_TASK_WORKER_ARTIFACT_GATE_V1 ===
                _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(_msg), error_message="")
            else:
                _update_task(conn, task_id, state="FAILED", result=_ff13c_strip_manifest_links(_msg), error_message="FORBIDDEN_PHRASE")
            # === END RESULT_VALIDATOR_GUARD_V1 ===
            _history(conn, task_id, "FULLFIX_05_PROJECT_PDF_DXF_OK")
            conn.commit()

            _sent = _send_once_ex(conn, task_id, str(chat_id), _msg, reply_to, "project_pdf_dxf_result")
            if isinstance(_sent, dict) and _sent.get("bot_message_id"):
                _update_task(conn, task_id, bot_message_id=_sent["bot_message_id"])
                conn.commit()
            return

        except Exception as _ff05_e:
            _err = str(_ff05_e)[:500]
            _update_task(
                conn,
                task_id,
                state="FAILED",
                result="Проект не создан: ошибка генерации PDF/DXF",
                error_message=_err,
            )
            _history(conn, task_id, "FULLFIX_05_PROJECT_EXCEPTION:" + _err)
            conn.commit()
            _send_once(conn, task_id, chat_id, "Проект не создан: ошибка генерации PDF/DXF", reply_to, "project_exception")
            return
    # === END FULLFIX_05_REQUIRE_REAL_PDF_DXF_PROJECT ===

    pending_clarify = conn.execute(
        """
        SELECT id, COALESCE(raw_input,'') AS raw_input
        FROM tasks
        WHERE chat_id=?
          AND id<>?
          AND COALESCE(topic_id,0)=?
          AND state='WAITING_CLARIFICATION'
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), task_id, int(topic_id)),
    ).fetchone()

    if pending_clarify:
        pending_id = _s(pending_clarify["id"])
        merged = _clean(_s(pending_clarify["raw_input"]) + "\n\nУточнение пользователя:\n" + raw_input, 12000)
        _update_task(conn, pending_id, raw_input=merged, state="IN_PROGRESS", error_message="")
        _history(conn, pending_id, "clarification_accepted")
        _update_task(conn, task_id, state="DONE", result="Уточнение принято", error_message="")
        _history(conn, task_id, "state:DONE")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Принял уточнение. Делаю", reply_to, "clarification_ok")
        return


    _update_task(conn, task_id, state="IN_PROGRESS", error_message="")
    _history(conn, task_id, "state:IN_PROGRESS")
    conn.commit()



def _get_parent_task_id(conn, chat_id, reply_to_message_id, topic_id):
    if not reply_to_message_id:
        return None
    row = conn.execute("""
        SELECT id FROM tasks
        WHERE chat_id = ? AND topic_id = ?
          AND (bot_message_id = ? OR reply_to_message_id = ?)
          AND state IN ('NEW', 'IN_PROGRESS', 'WAITING_CLARIFICATION', 'AWAITING_CONFIRMATION')
        ORDER BY updated_at DESC
        LIMIT 1
    """, (str(chat_id), int(topic_id), reply_to_message_id, reply_to_message_id)).fetchone()
    return row["id"] if row else None

def _normalize_voice_text(text: str) -> str:
    return _clean(_s(text).replace("[VOICE]", " "), 12000)

def _looks_done_command(text: str) -> bool:
    low = _normalize_voice_text(text).lower()
    if "не доволен" in low or "недоволен" in low:
        return False
    done_markers = [
        "да доволен",
        "доволен результатом",
        "можно завершать",
        "можно закрывать",
        "завершай задачу",
        "завершай запрос",
        "завершай поиск",
        "задача завершена",
        "задача закрыта",
        "запрос завершен",
        "поиск завершен",
        "все верно завершай",
        "всё верно завершай",
        "все верно задача завершена",
        "всё верно задача завершена",
        "да все верно",
        "да всё верно",
        "я же тебе сказал задача завершена",
        "я же тебе сказал завершай",
        "да можно",
    ]
    return any(m in low for m in done_markers)

def _extract_topic_role(text: str) -> str:
    raw = _clean(_s(text), 1000)
    if not raw:
        return ""

    patterns = [
        r"чат закреплен за темами:\s*(.+?)(?:\.|$)",
        r"чат закреплён за темами:\s*(.+?)(?:\.|$)",
        r"чат закреплен за:\s*(.+?)(?:\.|$)",
        r"чат закреплён за:\s*(.+?)(?:\.|$)",
        r"закрепленные темы:\s*(.+?)(?:\.|$)",
        r"закреплённые темы:\s*(.+?)(?:\.|$)",
        r"закреплено:\s*чат для\s*(.+?)(?:\.|$)",
        r"этот чат используется для\s*(.+?)(?:\.|$)",
        r"этот чат предназначен для\s*(.+?)(?:\.|$)",
    ]

    bad_markers = [
        "без контекста",
        "не понимаю запрос",
        "не помню",
        "задача завершена",
        "задача закрыта",
        "подтверждение принято",
        "готов к выполнению задачи",
        "последние действия",
        "в этом чате были следующие действия",
        "текущий статус",
        "последний запрос",
        "какие последние",
        "чем помочь",
    ]

    for pattern in patterns:
        m = re.search(pattern, raw, re.I | re.S)
        if not m:
            continue

        role = re.sub(r"\s+", " ", m.group(1)).strip(" .:-")
        role = re.split(r"\b(чем помочь|готов к работе|готов обсудить|последний запрос)\b", role, flags=re.I)[0].strip(" .:-")
        low = role.lower()

        if not role or len(role) < 3:
            continue
        if "?" in role:
            continue
        if any(x in low for x in bad_markers):
            continue

        return role[:500]

    return ""

def _save_topic_role_memory(chat_id: str, topic_id: int, text: str) -> str:
    role = _extract_topic_role(text)
    if not role or not os.path.exists(MEM_DB):
        return ""
    conn_mem = db(MEM_DB)
    try:
        if not _has_table(conn_mem, "memory"):
            return ""
        key = f"topic_{int(topic_id)}_role"
        conn_mem.execute(
            "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(chat_id), key, role),
        )
        conn_mem.commit()
        return role
    except Exception:
        return ""
    finally:
        conn_mem.close()

def _find_awaiting_confirmation_task(conn: sqlite3.Connection, chat_id: str, topic_id: int, current_task_id: str, reply_to_message_id: Any) -> Optional[sqlite3.Row]:
    if reply_to_message_id:
        row = conn.execute(
            """
            SELECT id, result
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND state='AWAITING_CONFIRMATION'
              AND id<>?
              AND (bot_message_id=? OR reply_to_message_id=?)
            ORDER BY updated_at DESC, created_at DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id), str(current_task_id), reply_to_message_id, reply_to_message_id),
        ).fetchone()
        if row:
            return row

    return conn.execute(
        """
        SELECT id, result
        FROM tasks
        WHERE chat_id=?
          AND COALESCE(topic_id,0)=?
          AND state='AWAITING_CONFIRMATION'
          AND id<>?
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id), str(current_task_id)),
    ).fetchone()


# === FULLFIX_DIRECTION_KERNEL_STAGE_1_HELPER ===
def _stage1_dir_payload(payload):
    try:
        p = dict(payload or {})
        if _Stage1WorkItem is None or _Stage1DirReg is None:
            p.setdefault("direction", "general_chat")
            return p
        row = {
            "id": p.get("task_id") or p.get("id") or "",
            "chat_id": str(p.get("chat_id") or ""),
            "topic_id": int(p.get("topic_id") or 0),
            "input_type": p.get("input_type") or "unknown",
            "raw_input": p.get("raw_input") or p.get("raw_text") or "",
            "state": p.get("state") or "IN_PROGRESS",
            "reply_to_message_id": p.get("reply_to_message_id"),
            "bot_message_id": p.get("bot_message_id"),
        }
        wi = _Stage1WorkItem.from_task_row(row)
        prof = _Stage1DirReg().detect(wi)
        did = prof.get("id") or "general_chat"
        wi.set_direction(did, prof)
        wi.add_audit("stage", "FULLFIX_DIRECTION_KERNEL_STAGE_1")
        wi.add_audit("shadow_mode", True)
        p.update({
            "direction": did,
            "direction_profile": prof,
            "direction_audit": wi.audit,
            "work_item": wi.to_dict(),
        })
        try:
            logger.info("FULLFIX_DIRECTION_KERNEL_STAGE_1 dir=%s score=%s task=%s topic=%s",
                        did, prof.get("score"), row["id"], row["topic_id"])
        except Exception:
            pass
        return p
    except Exception as e:
        try: logger.error("FULLFIX_DIRECTION_KERNEL_STAGE_1_ERR %s", e)
        except Exception: pass
        p = dict(payload or {})
        p.setdefault("direction", "general_chat")
        return p
# === END ===
async def _handle_in_progress(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> None:
    task_id = _s(_task_field(task, "id"))
    raw_input = _clean(_s(_task_field(task, "raw_input")), 12000)
    reply_to = _task_field(task, "reply_to_message_id", None)

    if _looks_done_command(raw_input):
        target = _find_awaiting_confirmation_task(conn, chat_id, topic_id, task_id, reply_to)
        if target:
            target_id = _s(target["id"])
            target_result = _s(target["result"])
            saved_role = _save_topic_role_memory(chat_id, topic_id, target_result)
            _update_task(conn, target_id, state="DONE", error_message="")
            _history(conn, target_id, "state:DONE")
            if saved_role:
                _history(conn, target_id, f"ROLE_SAVED:{_clean(saved_role, 200)}")
            _update_task(conn, task_id, state="DONE", result="Подтверждение принято", error_message="")
            _history(conn, task_id, "state:DONE")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Принял. Задача закрыта", reply_to, "confirm_done")
            return

    parent_task_id = _get_parent_task_id(conn, chat_id, task["reply_to_message_id"], topic_id)
    active_source_id = parent_task_id or task_id
    active_task_context = _active_unfinished_context(conn, chat_id, topic_id, active_source_id)
    pin_context = get_pin_context(chat_id, raw_input, topic_id)
    short_memory, long_memory, topic_role, topic_directions = _load_memory_context(chat_id, topic_id)
    archive_context = _load_archive_context(chat_id, topic_id, raw_input)
    search_context = _search_fact_context(conn, chat_id, topic_id)

    payload: Dict[str, Any] = {
        "id": task_id,
        "task_id": task_id,  # PAYLOAD_TOPIC_ID_FIX_V1
        "topic_id": int(topic_id or 0),
        "chat_id": chat_id,
        "input_type": _s(_task_field(task, "input_type", "text")).lower() or "text",
        "raw_input": raw_input,
        "normalized_input": raw_input,
        "state": "IN_PROGRESS",
        "reply_to_message_id": reply_to,
        "active_task_context": active_task_context,
        "pin_context": pin_context,
        "short_memory_context": short_memory,
        "long_memory_context": long_memory,
        "archive_context": archive_context,
        "search_context": search_context,
        "topic_role": topic_role,
        "topic_directions": topic_directions,
    }

    try:
        ai_result = None  # AI_RESULT_INIT_V1
        assigned_role = _detect_role_assignment(raw_input)
        if assigned_role:
            _save_topic_role(chat_id, topic_id, assigned_role)
            _history(conn, task_id, f"ROLE_SAVED:{_clean(assigned_role, 200)}")
            conn.commit()
            ai_result = f"Принято. Чат закреплен за темами: {assigned_role}. Все связанные запросы будут обрабатываться здесь."
        else:
            ROLE_Q = re.compile(r"(для чего|о чём|о чем|про что|напомни.*(чат|топик)|чем занимается|зачем этот чат)", re.IGNORECASE)
            HISTORY_Q = re.compile(r"(что мы писали|что писали раньше|о ч[её]м общались|напомни.*что.*(писали|обсуждали)|что было в этом чате|история чата)", re.IGNORECASE)
            # === WHAT_IS_THIS_META_V1 ===
            if TOPIC_META_LOADER_WIRED and is_what_is_this_question(raw_input):
                _wt_meta = load_topic_meta(int(topic_id or 0))
                if _wt_meta:
                    _wt_answer = build_topic_self_answer(_wt_meta)
                    if _wt_answer:
                        _update_task(conn, task_id, state="DONE", result=_wt_answer, error_message="")
                        conn.commit()
                        from core.reply_sender import send_reply_ex
                        send_reply_ex(chat_id=str(chat_id), text=_wt_answer, reply_to_message_id=reply_to, message_thread_id=topic_id)
                        return
            # === END WHAT_IS_THIS_META_V1 ===
            if topic_role and (ROLE_Q.search(raw_input) or HISTORY_Q.search(raw_input)):
                ai_result = f"Этот чат закреплён за: {topic_role}"
            else:
                try:
                    from core.model_router import route_model as _rm
                    _mo = _rm(payload)
                    if _mo:
                        payload["model_override"] = _mo  # MODEL_ROUTER_V1_WIRED
                except Exception:
                    pass
                        # === TEMPLATE_TRIGGER_V1 ===
            if _tpl_check(str(raw_input or "")):
                _tpl_path = _tpl_get(int(topic_id or 0))
                if _tpl_path and os.path.exists(_tpl_path):
                    logger.info("TEMPLATE_TRIGGER_V1 using template=%s task=%s", _tpl_path, task_id)
                    payload["template_path"] = _tpl_path
                    payload["use_template"] = True
            # === END TEMPLATE_TRIGGER_V1 ===
# === TOPIC_3008_HANDLER_V1 ===
            if _t3_check(int(topic_id or 0)):
                _t3_command = _t3_cmd(str(raw_input or ""))
                if _t3_command != "none":
                    import re as _re3008
                    _t3_ctx = " ".join(filter(None,[
                        str(payload.get("active_task_context") or "")[:200],
                        str(payload.get("pin_context") or "")[:100],
                        str(payload.get("short_memory_context") or "")[:200],
                    ]))
                    if _t3_command == "write":
                        _t3_desc = _re3008.sub(r"напиши\s+код|написать\s+код","",str(raw_input or ""),flags=_re3008.I).strip()
                        if _t3_generate:
                            _t3_gen = await asyncio.wait_for(_t3_generate(_t3_desc,_t3_ctx),timeout=120)
                            ai_result = _t3_gen + "\n\n---\nПроверить код?"
                    elif _t3_command == "verify":
                        _t3_code = _t3_extract(str(raw_input or ""))
                        if len(_t3_code.strip()) < 10:
                            ai_result = "Отправь код для проверки."
                        elif _t3_verify:
                            from core.reply_sender import send_reply_ex as _t3srex
                            _t3srex(chat_id=str(chat_id),text="Запущена верификация. Ожидаю ответы (до 1.5 мин)...",reply_to_message_id=reply_to,message_thread_id=topic_id)
                            ai_result = await asyncio.wait_for(_t3_verify(_t3_code,_t3_ctx),timeout=150)
            # === END TOPIC_3008_HANDLER_V1 ===
            if ai_result is None:  # AI_LOGIC_FIX_V1
                # FULLFIX_DIRECTION_KERNEL_STAGE_1_CALL
                payload = _stage1_dir_payload(payload)
                # FULLFIX_TOPIC_AUTODISCOVERY_V2_CALL
                if _topic_autodiscovery is not None:
                    try:
                        from core.work_item import WorkItem as _WITA
                        _wita = _WITA.from_task_row({
                            "id": payload.get("task_id") or payload.get("id") or "",
                            "chat_id": str(payload.get("chat_id") or ""),
                            "topic_id": int(payload.get("topic_id") or 0),
                            "input_type": payload.get("input_type") or "unknown",
                            "raw_input": payload.get("raw_input") or payload.get("raw_text") or "",
                            "state": payload.get("state") or "IN_PROGRESS",
                        })
                        _topic_autodiscovery(_wita, payload)
                    except Exception as _eta:
                        logger.error("TOPIC_AUTODISCOVERY_ERR %s", _eta)
                # FULLFIX_CAPABILITY_ROUTER_STAGE_2_CALL
                if _Stage2Router is not None:
                    try:
                        from core.work_item import WorkItem as _WI2
                        _wi2 = _WI2.from_task_row({
                            "id": payload.get("task_id") or payload.get("id") or "",
                            "chat_id": str(payload.get("chat_id") or ""),
                            "topic_id": int(payload.get("topic_id") or 0),
                            "input_type": payload.get("input_type") or "unknown",
                            "raw_input": payload.get("raw_input") or payload.get("raw_text") or "",
                            "state": payload.get("state") or "IN_PROGRESS",
                        })
                        _wi2.set_direction(
                            payload.get("direction") or "general_chat",
                            payload.get("direction_profile") or {},
                        )
                        _r2 = _Stage2Router().apply_to_work_item(_wi2)
                        payload["engine"] = _r2["engine"]
                        payload["execution_plan"] = _r2["execution_plan"]
                        payload["formats_out"] = _r2["formats_out"]
                        payload["quality_gates"] = _r2["quality_gates"]
                        payload["capability_router"] = _r2["router_version"]
                        logger.info("FULLFIX_CAPABILITY_ROUTER_STAGE_2 engine=%s steps=%s dir=%s",
                                    _r2["engine"], len(_r2["execution_plan"]), payload.get("direction"))
                    except Exception as _e2:
                        logger.error("FULLFIX_CAPABILITY_ROUTER_STAGE_2_ERR %s", _e2)
                # FULLFIX_SEARCH_ENGINE_STAGE_5_CALL
                if _Stage5Search is not None:
                    try:
                        from core.work_item import WorkItem as _WI5
                        _wi5 = _WI5.from_task_row({
                            "id": payload.get("task_id") or payload.get("id") or "",
                            "chat_id": str(payload.get("chat_id") or ""),
                            "topic_id": int(payload.get("topic_id") or 0),
                            "input_type": payload.get("input_type") or "unknown",
                            "raw_input": payload.get("raw_input") or payload.get("raw_text") or "",
                            "state": payload.get("state") or "IN_PROGRESS",
                        })
                        _wi5.set_direction(
                            payload.get("direction") or "general_chat",
                            payload.get("direction_profile") or {},
                        )
                        _Stage5Search().apply_to_payload(_wi5, payload)
                    except Exception as _e5:
                        logger.error("FULLFIX_SEARCH_ENGINE_STAGE_5_ERR %s", _e5)
                # FULLFIX_CONTEXT_LOADER_STAGE_3_CALL
                if _Stage3Loader is not None:
                    try:
                        from core.work_item import WorkItem as _WI3
                        _wi3 = _WI3.from_task_row({
                            "id": payload.get("task_id") or payload.get("id") or "",
                            "chat_id": str(payload.get("chat_id") or ""),
                            "topic_id": int(payload.get("topic_id") or 0),
                            "input_type": payload.get("input_type") or "unknown",
                            "raw_input": payload.get("raw_input") or payload.get("raw_text") or "",
                            "state": payload.get("state") or "IN_PROGRESS",
                        })
                        _wi3.set_direction(
                            payload.get("direction") or "general_chat",
                            payload.get("direction_profile") or {},
                        )
                        _refs3 = _Stage3Loader().load(_wi3)
                        payload["context_refs"] = _refs3
                        logger.info("FULLFIX_CONTEXT_LOADER_STAGE_3 topic=%s short_mem=%s",
                                    payload.get("topic_id"), bool(_refs3.get("short_memory")))
                    except Exception as _e3:
                        logger.error("FULLFIX_CONTEXT_LOADER_STAGE_3_ERR %s", _e3)
                ai_result = await asyncio.wait_for(process_ai_task(payload), timeout=AI_TIMEOUT)
                # FULLFIX_QUALITY_GATE_STAGE_4_CALL
                if _Stage4QG is not None and isinstance(ai_result, dict):
                    try:
                        _qg_payload = {**payload, **ai_result}
                        _qg_report = _Stage4QG().apply_to_payload(_qg_payload)
                        ai_result["quality_gate_report"] = _qg_report
                        logger.info("FULLFIX_QUALITY_GATE_STAGE_4 overall=%s failed=%s dir=%s",
                                    _qg_report["overall"], _qg_report["failed"], payload.get("direction"))
                    except Exception as _e4:
                        logger.error("FULLFIX_QUALITY_GATE_STAGE_4_ERR %s", _e4)
                # FULLFIX_ARCHIVE_ENGINE_STAGE_6_CALL
                if _Stage6Archive is not None:
                    try:
                        _Stage6Archive().archive(payload, ai_result if isinstance(ai_result, dict) else {})
                    except Exception as _e6:
                        logger.error("FULLFIX_ARCHIVE_ENGINE_STAGE_6_ERR %s", _e6)
                # FULLFIX_FORMAT_ADAPTER_STAGE_7_CALL
                if _Stage7FA is not None and isinstance(ai_result, dict):
                    try:
                        _formats_out = payload.get("formats_out") or ["telegram_text"]
                        _adapted = _Stage7FA().adapt(ai_result, _formats_out, payload)
                        ai_result["format_adapted"] = _adapted
                        logger.info("FULLFIX_FORMAT_ADAPTER_STAGE_7 formats=%s primary=%s dir=%s",
                                    _formats_out, list(_adapted.get("outputs", {}).keys())[:2],
                                    payload.get("direction"))
                    except Exception as _e7:
                        logger.error("FULLFIX_FORMAT_ADAPTER_STAGE_7_ERR %s", _e7)
    except Exception as e:
        _update_task(conn, task_id, state="FAILED", error_message=_clean(str(e), 500))
        _close_pin(conn, task_id)
        _history(conn, task_id, "state:FAILED")
        conn.commit()
        _send_once(conn, task_id, chat_id, "Задача не выполнена. Уточни или повтори запрос", reply_to, "router_failed")
        return

    ai_result = _clean(_s(ai_result), 50000)
    # === FOLLOWUP DETECTION (FACT-BASED) ===
    low_input = raw_input.lower()

    memory_markers = [
        "напомни","что обсуждали","что делали","какие задачи","история",
        "что было","что писали","для чего этот чат","о чем чат","о чём чат"
    ]

    search_markers = [
        "нерелевант","битые","ссылки не те","проверь","еще раз","ещё раз",
        "сделай еще","сделай ещё","найди еще","найди ещё","это не то"
    ]

    has_memory_context = any([
        short_memory,
        long_memory,
        topic_role,
        active_task_context,
        pin_context,
        archive_context,
    ])

    raw_input = _clean(_s(_task_field(task, "raw_input")), 12000)
    low_input = raw_input.lower()

    memory_markers = [
        "напомни",
        "что обсуждали",
        "что делали",
        "какие задачи",
        "история",
        "что было в этом чате",
        "что писали",
        "для чего этот чат",
        "о чем чат",
        "о чём чат",
    ]
    is_memory_followup = has_memory_context and any(m in low_input for m in memory_markers)

    search_markers = [
        "нерелевант",
        "битые ссылки",
        "живые ссылки",
        "ссылки не те",
        "проверь еще",
        "проверь ещё",
        "еще раз поиск",
        "ещё раз поиск",
        "сделай еще раз поиск",
        "сделай ещё раз поиск",
        "найди еще",
        "найди ещё",
        "это не то",
        "ссылки биты",
        "ссылки битые",
    ]
    is_search_followup = bool(search_context) and any(m in low_input for m in search_markers)

    if is_search_followup and search_context:
        forbidden_search_advice = [
            "dr.web",
            "link checker",
            "яндекс safety",
            "google safe browsing",
            "virustotal",
            "для проверки безопасности ссылок используйте",
        ]
        if any(m in ai_result.lower() for m in forbidden_search_advice):
            ai_result = _clean(f"Повторяю поиск по последнему запросу\n\n{search_context}", 50000)

    if is_memory_followup or is_search_followup:
        if not ai_result or len(ai_result) < MIN_RESULT_LEN:
            _update_task(conn, task_id, state="FAILED", error_message="INVALID_RESULT_GATE")
            _close_pin(conn, task_id)
            _history(conn, task_id, "state:FAILED")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Не понял запрос. Уточни что нужно сделать", reply_to, "invalid_result")
            return
    else:
        if not _is_valid_result(ai_result, raw_input):
            _update_task(conn, task_id, state="FAILED", error_message="INVALID_RESULT_GATE")
            _close_pin(conn, task_id)
            _history(conn, task_id, "state:FAILED")
            conn.commit()
            _send_once(conn, task_id, chat_id, "Не понял запрос. Уточни что нужно сделать", reply_to, "invalid_result")
            return

    low_result = ai_result.lower()
    done_markers = [
        "задача завершена",
        "задача закрыта",
        "задачи завершены",
        "подтверждение принято",
        "поиск завершен",
        "поиск завершён",
    ]
    junk_markers = [
        "без контекста",
        "задайте конкретный вопрос",
        "конкретный вопрос по",
        "нет, не помню",
        "не понимаю запрос",
        "готов к выполнению задачи",
    ]
    info_markers = [
        "для чего этот чат",
        "что мы здесь обсуждаем",
        "что в данном чате",
        "какой последний запрос",
        "последний запрос",
        "какие последние запросы",
        "что мы тут делаем",
        "что мы здесь делаем",
        "о чем чат",
        "о чём чат",
    ]
    file_success_markers = [
        "документ обработан",
        "артефакт:",
        "нормализовано позиций",
        "обработаны документы",
    ]
    file_bad_markers = [
        "скачан, ожидает анализа",
        "создан локально, но загрузка в drive завершилась ошибкой",
        "ожидает анализа",
        "загрузка в drive завершилась ошибкой",
    ]

    if any(m in low_result for m in done_markers):
        _update_task(conn, task_id, state="DONE", result=ai_result, error_message="")
        _close_pin(conn, task_id)
        _history(conn, task_id, f"result:{_clean(ai_result, 400)}")
        _save_memory(chat_id, topic_id, raw_input, ai_result)  # SAVE_MEM_DONE_V2
        conn.commit()
        _send_once(conn, task_id, chat_id, ai_result, reply_to, "done_terminal")
        return

    if any(m in low_result for m in junk_markers):
        _update_task(conn, task_id, state="WAITING_CLARIFICATION", result=ai_result, error_message="")
        _close_pin(conn, task_id)
        _history(conn, task_id, f"clarify:{_clean(ai_result, 400)}")
        conn.commit()
        _send_once(conn, task_id, chat_id, ai_result, reply_to, "clarify_terminal")
        return

    is_info_query = any(m in low_input for m in info_markers)
    is_file_success = any(m in low_result for m in file_success_markers) and not any(m in low_result for m in file_bad_markers)

    if is_memory_followup or is_search_followup or is_info_query or is_file_success:
        _update_task(conn, task_id, state="DONE", result=ai_result, error_message="")
        _history(conn, task_id, f"result:{_clean(ai_result, 400)}")
        _save_memory(chat_id, topic_id, raw_input, ai_result)  # SAVE_MEM_FOLLOWUP_V2
        conn.commit()
        try:
            save_pin(chat_id, task_id, ai_result, topic_id)
        except Exception:
            pass
        _send_once(conn, task_id, chat_id, ai_result, reply_to, "done_terminal")
        return

    should_save_role = (
        bool(re.search(
            r"(чат закреплен за темами:|чат закреплён за темами:|чат закреплен за:|чат закреплён за:|закрепленные темы:|закреплённые темы:|закреплено:\s*чат для|этот чат используется для|этот чат предназначен для)",
            ai_result,
            re.I,
        ))
        and not any(x in low_result for x in junk_markers)
        and "последние действия" not in low_result
        and "текущий статус" not in low_result
    )

    saved_role = ""
    if should_save_role:
        _save_memory(chat_id, topic_id, raw_input, ai_result)  # SAVE_MEM_CONFIRM_V2
        saved_role = _save_topic_role_memory(chat_id, topic_id, ai_result)
        # === RESULT_VALIDATOR_GUARD_V1 ===
        if _check_result_before_confirm(ai_result):
            # === SEARCH_MONOLITH_V2_CLARIFICATION_HANDLER ===
            try:
                if _search_v2_is_clarification(ai_result):
                    _cmsg = str(ai_result).replace("SEARCH_CLARIFICATION_REQUIRED:","").strip()
                    _update_task(conn, task_id, state="WAITING_CLARIFICATION", result=_cmsg, error_message="")
                    _history(conn, task_id, "SEARCH_MONOLITH_V2:WAITING_CLARIFICATION")
                    conn.commit()
                    _send_once(conn, task_id, str(chat_id), _cmsg, reply_to, "search_v2_clarification")
                    return
            except Exception as _e: logger.warning("SEARCH_V2_CLARIFICATION_HANDLER_ERR %s", _e)
            # === END SEARCH_MONOLITH_V2_CLARIFICATION_HANDLER ===
            # === UNIFIED_ENGINE_RESULT_VALIDATOR_V1_TASK_WORKER_AI_RESULT ===
            try:
                if validate_engine_result is not None:
                    _payload_for_uv = locals().get("payload", {}) or {}
                    _raw_for_uv = ""
                    try:
                        _raw_for_uv = str(task["raw_input"] if "raw_input" in task.keys() else "")
                    except Exception:
                        _raw_for_uv = str(_payload_for_uv.get("raw_input") or _payload_for_uv.get("user_text") or "")
                    _input_type_for_uv = ""
                    try:
                        _input_type_for_uv = str(task["input_type"] if "input_type" in task.keys() else "")
                    except Exception:
                        _input_type_for_uv = str(_payload_for_uv.get("input_type") or "")
                    _uv = validate_engine_result({"summary": ai_result, "engine": "AI_ROUTER"}, input_type=_input_type_for_uv, user_text=_raw_for_uv, topic_id=topic_id)
                    if not _uv.get("ok"):
                        _update_task(conn, task_id, state="FAILED", result="", error_message="UNIFIED_ENGINE_RESULT_VALIDATOR_V1:" + str(_uv.get("reason") or "INVALID"))
                        _history(conn, task_id, "UNIFIED_ENGINE_RESULT_VALIDATOR_V1:FAILED:" + str(_uv.get("reason") or "INVALID"))
                        return
            except Exception as _uv_e:
                logger.warning("UNIFIED_ENGINE_RESULT_VALIDATOR_V1_ERR task=%s err=%s", task_id, _uv_e)
            # === END_UNIFIED_ENGINE_RESULT_VALIDATOR_V1_TASK_WORKER_AI_RESULT ===
            # === TASK_WORKER_ARTIFACT_GATE_V1 ===
            try:
                if validate_engine_result is not None:
                    _twag_raw = ""
                    _twag_input_type = ""
                    try:
                        _twag_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
                    except Exception:
                        _twag_raw = ""
                    try:
                        _twag_input_type = str(task["input_type"] if "input_type" in task.keys() else "")
                    except Exception:
                        _twag_input_type = ""
                    _twag_result = ai_result
                    _twag_check = validate_engine_result(
                        {"summary": _twag_result, "engine": "TASK_WORKER_ARTIFACT_GATE_V1"},
                        input_type=_twag_input_type,
                        user_text=_twag_raw,
                        topic_id=topic_id,
                    )
                    if not _twag_check.get("ok"):
                        _update_task(conn, task_id, state="FAILED", result="",
                            error_message="TASK_WORKER_ARTIFACT_GATE_V1:" + str(_twag_check.get("reason") or "INVALID"))
                        _history(conn, task_id, "TASK_WORKER_ARTIFACT_GATE_V1:FAILED:" + str(_twag_check.get("reason") or "INVALID"))
                        return
            except Exception as _twag_e:
                logger.warning("TASK_WORKER_ARTIFACT_GATE_V1_ERR task=%s err=%s", task_id, _twag_e)
            # === END_TASK_WORKER_ARTIFACT_GATE_V1 ===
            _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=ai_result, error_message="")
        else:
            _update_task(conn, task_id, state="FAILED", result=ai_result, error_message="FORBIDDEN_PHRASE")
        # === END RESULT_VALIDATOR_GUARD_V1 ===
    _history(conn, task_id, f"result:{_clean(ai_result, 400)}")
    if saved_role:
        _history(conn, task_id, f"ROLE_SAVED:{_clean(saved_role, 200)}")

    try:
        save_pin(chat_id, task_id, ai_result, topic_id)
    except Exception as e:
        logger.warning("save_pin_fail task=%s err=%s", task_id, e)

    _ai_result_clean = str(ai_result or "").replace("\n\nДоволен результатом? Ответь: Да / Уточни / Правки", "").strip()  # FF21_FIX_DOUBLE_DOVOLEN
    confirmation_text = f"{_ai_result_clean}\n\nДоволен результатом? Ответь: Да / Уточни / Правки"
    sent = _send_once_ex(conn, task_id, chat_id, confirmation_text, reply_to, "result")
    bot_message_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
    if bot_message_id is not None:
        _update_task(conn, task_id, bot_message_id=bot_message_id)
    conn.commit()



# === IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1 ===
def _in_progress_hard_timeout_by_created_at_fix_v1(conn, minutes: int = 30) -> int:
    try:
        rows = conn.execute(
            """
            SELECT id FROM tasks
            WHERE state='IN_PROGRESS'
              AND datetime(COALESCE(created_at, updated_at, 'now')) <= datetime('now', ?)
            ORDER BY created_at ASC
            LIMIT 200
            """,
            (f"-{int(minutes)} minutes",),
        ).fetchall()
        n = 0
        for row in rows:
            tid = row["id"] if hasattr(row, "keys") else row[0]
            conn.execute(
                "UPDATE tasks SET state='FAILED', error_message='IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1', updated_at=datetime('now') WHERE id=? AND state='IN_PROGRESS'",
                (str(tid),),
            )
            try:
                _history(conn, str(tid), "IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1:FAILED")
            except Exception:
                pass
            n += 1
        if n:
            try: conn.commit()
            except Exception: pass
            logger.warning("IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1 closed=%s", n)
        return n
    except Exception as e:
        logger.warning("IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1_ERR %s", e)
        return 0
# === END_IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1 ===

def _pick_next_task(conn: sqlite3.Connection, chat_id: Optional[str]) -> Optional[sqlite3.Row]:
    # === IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1_HOOK ===
    _in_progress_hard_timeout_by_created_at_fix_v1(conn, minutes=30)
    # === END_IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1_HOOK ===
    where = ["state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION')"]
    params: List[Any] = []
    if chat_id:
        where.insert(0, "chat_id=?")
        params.append(str(chat_id))

    conn.execute("BEGIN IMMEDIATE")
    row = conn.execute(
        f"""
        SELECT *
        FROM tasks
        WHERE {' AND '.join(where)}
        ORDER BY CASE state WHEN 'IN_PROGRESS' THEN 0 WHEN 'WAITING_CLARIFICATION' THEN 1 ELSE 2 END,
                 created_at ASC
        LIMIT 1
        """
        ,
        params,
    ).fetchone()
    conn.execute("COMMIT")
    return row


async def main() -> None:
    lock_fp = open(LOCK_PATH, "w")
    try:
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        logger.info("WORKER LOCKED BY OTHER PROCESS")
        return

    logger.info("WORKER STARTED pid=%s", os.getpid())

    while True:
        conn = db(CORE_DB)
        try:
            _recover_stale_tasks(conn, None)
            task = _pick_next_task(conn, None)
            if not task:
                time.sleep(POLL_SEC)
                continue

            task_id = _s(_task_field(task, "id"))
            chat_id = _s(_task_field(task, "chat_id"))
            topic_id = int(_task_field(task, "topic_id", 0) or 0)
            state = _s(_task_field(task, "state")).upper()

            logger.info("PICKED %s state=%s chat=%s topic=%s", task_id, state, chat_id, topic_id)
            input_type = _s(_task_field(task, "input_type")).lower()
            if input_type == "drive_file":
                try:
                    await _handle_drive_file(conn, task, chat_id, topic_id)
                except Exception as e:
                    logger.error("DRIVE_FILE CRASH task=%s err=%s", task_id, str(e))
                continue

            if state == "NEW":
                await _handle_new(conn, task, chat_id, topic_id)
            elif state == "IN_PROGRESS":
                await _handle_in_progress(conn, task, chat_id, topic_id)
            elif state == "WAITING_CLARIFICATION":
                await _handle_in_progress(conn, task, chat_id, topic_id)
        finally:
            conn.close()

        time.sleep(POLL_SEC)



# === DRIVE FILE HANDLING ===
def _download_from_drive(file_id: str, local_path: str) -> bool:
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        from google.oauth2.service_account import Credentials
        import io
        creds = Credentials.from_service_account_file(
            '/root/.areal-neva-core/credentials.json',
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        service = build('drive', 'v3', credentials=creds)
        request = service.files().get_media(fileId=file_id)
        with io.FileIO(local_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        return True
    except Exception as e:
        import logging
        logging.getLogger("task_worker").error(f"Drive download failed: {e}")
        return False

async def _handle_drive_file(conn, task, chat_id, topic_id):
    import json, os
    task_id = task["id"]
    input_type = "drive_file"  # INPUT_TYPE_DRIVE_FIX_V1
    raw_input = task["raw_input"]
    try:
        data = json.loads(raw_input)
        file_id = data["file_id"]
        file_name = data.get("file_name", "файл")  # HOTFIX_FILE_NAME_EARLY_V1
        # === DRIVE_FILE_CONTENT_SERVICE_GUARD_V1 ===
        try:
            if _filemem_is_service_file(str(file_name or ""), str(data.get("source") or ""), int(topic_id or 0), str(raw_input or "")):
                _msg = "Служебный файл синхронизации проигнорирован"
                _update_task(conn, task_id, state="CANCELLED", result=_msg, error_message="SERVICE_FILE_IGNORED")
                _history(conn, task_id, "DRIVE_FILE_CONTENT_SERVICE_GUARD_V1:CANCELLED")
                try:
                    _append_timeline_event_v1(str(chat_id), int(topic_id or 0), task_id, "service_file_ignored", raw_input, _msg)
                except Exception:
                    pass
                conn.commit()
                logger.info("DRIVE_FILE_CONTENT_SERVICE_GUARD_V1 cancelled task=%s file=%s source=%s topic=%s", task_id, file_name, data.get("source"), topic_id)
                return
        except Exception as _svc_e:
            logger.warning("DRIVE_FILE_CONTENT_SERVICE_GUARD_V1_ERR task=%s err=%s", task_id, _svc_e)
        # === END DRIVE_FILE_CONTENT_SERVICE_GUARD_V1 ===
        # === DRIVE_FILE_MEMORY_INDEX_V1 + FILE_DUPLICATE_MEMORY_GUARD_V1 ===
        try:
            _df_file_id = str(data.get("file_id") or "")
            _df_file_name = str(file_name or "")
            _df_meta = json.dumps({
                "task_id": task_id, "chat_id": str(chat_id),
                "topic_id": int(topic_id or 0), "file_id": _df_file_id,
                "file_name": _df_file_name,
                "caption": str(data.get("caption") or ""),
                "source": str(data.get("source") or ""),
            }, ensure_ascii=False)
            if _df_file_id:
                _dupe = conn.execute(
                    "SELECT id,state FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=? AND id<>? AND input_type='drive_file' AND raw_input LIKE ? AND state IN ('DONE','ARCHIVED','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                    (str(chat_id), int(topic_id or 0), task_id, "%" + _df_file_id + "%"),
                ).fetchone()
                if _dupe is not None:
                    _dmsg = "Файл уже есть в этом топике. Предыдущая задача: " + _s(_dupe["id"])[:8]
                    _update_task(conn, task_id, state="DONE", result=_dmsg, error_message="")
                    _history(conn, task_id, "FILE_DUPLICATE_MEMORY_GUARD_V1:DONE")
                    _memory_insert_topic_entry_v1(str(chat_id), f"topic_{int(topic_id or 0)}_file_duplicate_{task_id}", _df_meta)
                    _append_timeline_event_v1(str(chat_id), int(topic_id or 0), task_id, "file_duplicate", raw_input, _dmsg)
                    conn.commit()
                    _send_once(conn, task_id, str(chat_id), _dmsg, _task_field(task, "reply_to_message_id", None), "file_dup_guard_v1")
                    logger.info("FILE_DUPLICATE_MEMORY_GUARD_V1 task=%s", task_id)
                    return
            _memory_insert_topic_entry_v1(str(chat_id), f"topic_{int(topic_id or 0)}_file_{task_id}", _df_meta)
            _append_timeline_event_v1(str(chat_id), int(topic_id or 0), task_id, "drive_file_indexed", raw_input, "")
            # === DRIVE_FILE_CONTENT_MEMORY_INDEX_V1_CALL ===
            try:
                # === DRIVE_FILE_CONTENT_INDEX_SKIP_SERVICE_V2 ===
                try:
                    _df_skip_content_index = bool(_filemem_is_service_file(
                        _df_file_name,
                        str(data.get("source") or ""),
                        int(topic_id or 0),
                        str(raw_input or "")
                    ))
                except Exception as _df_skip_e:
                    _df_skip_content_index = False
                    logger.warning("DRIVE_FILE_CONTENT_INDEX_SKIP_SERVICE_V2_ERR task=%s err=%s", task_id, _df_skip_e)
                if _df_skip_content_index:
                    logger.info("DRIVE_FILE_CONTENT_INDEX_SKIP_SERVICE_V2 skipped task=%s file=%s source=%s topic=%s", task_id, _df_file_name, data.get("source"), topic_id)
                # === END DRIVE_FILE_CONTENT_INDEX_SKIP_SERVICE_V2 ===
                if (not _df_skip_content_index) and _df_content_index is not None and _df_file_id:
                    _df_ci = await asyncio.to_thread(
                        _df_content_index,
                        str(chat_id),
                        int(topic_id or 0),
                        str(task_id),
                        str(_df_file_id),
                        str(_df_file_name),
                        str(data.get("mime_type") or ""),
                    )
                    _memory_insert_topic_entry_v1(
                        str(chat_id),
                        f"topic_{int(topic_id or 0)}_file_content_status_{task_id}",
                        json.dumps(_df_ci, ensure_ascii=False),
                    )
                    _append_timeline_event_v1(
                        str(chat_id),
                        int(topic_id or 0),
                        task_id,
                        "drive_file_content_indexed",
                        raw_input,
                        json.dumps(_df_ci, ensure_ascii=False),
                    )
                    logger.info("DRIVE_FILE_CONTENT_MEMORY_INDEX_V1 task=%s ok=%s reason=%s chars=%s", task_id, _df_ci.get("ok"), _df_ci.get("reason"), _df_ci.get("chars"))
            except Exception as _dfci_e:
                logger.warning("DRIVE_FILE_CONTENT_MEMORY_INDEX_V1_ERR task=%s err=%s", task_id, _dfci_e)
            # === END DRIVE_FILE_CONTENT_MEMORY_INDEX_V1_CALL ===
            logger.info("DRIVE_FILE_MEMORY_INDEX_V1 task=%s file=%s", task_id, _df_file_name)
            # === FILE_CATALOG_AUTOSYNC_AFTER_DRIVE_FILE_V1 ===
            try:
                _filemem_save_catalog(str(chat_id), int(topic_id or 0))
            except Exception as _cat_e:
                logger.warning("FILE_CATALOG_AUTOSYNC_AFTER_DRIVE_FILE_V1_ERR task=%s err=%s", task_id, _cat_e)
            # === END FILE_CATALOG_AUTOSYNC_AFTER_DRIVE_FILE_V1 ===
        except Exception as _e:
            logger.warning("DRIVE_FILE_MEMORY_INDEX_V1_ERR task=%s err=%s", task_id, _e)
        # === END DRIVE_FILE_MEMORY_INDEX_V1 + FILE_DUPLICATE_MEMORY_GUARD_V1 ===
        # DRIVE_FILE_SOURCE_HEALTHCHECK_GUARD_V1
        _hc_src = str(data.get("source") or "").lower()
        _hc_fn = str(file_name or "").lower()
        _hc_raw_low = str(raw_input or "").lower()
        _hc_markers = ("retry_queue_healthcheck", "healthcheck", "areal_hc_", "_hc_file")
        if _hc_src in ("google_drive", "gdrive") or any(m in _hc_fn or m in _hc_raw_low for m in _hc_markers):
            _update_task(conn, task_id, state="CANCELLED", error_message="SERVICE_FILE_IGNORED:HEALTHCHECK")
            conn.commit()
            logger.info("DRIVE_FILE_SOURCE_HEALTHCHECK_GUARD_V1 cancelled task=%s", task_id)
            return
        # === TASK_TYPE_DETECT_V1 ===
        _task_type = "DOCUMENT_TASK"
        _fn_lower = file_name.lower()
        _caption_lower = (data.get("caption") or raw_input or "").lower()
        if any(_fn_lower.endswith(e) for e in (".dwg", ".dxf")):
            _task_type = "DWG_TASK"
        elif any(_fn_lower.endswith(e) for e in (".xlsx", ".xls", ".csv")):
            _task_type = "ESTIMATE_TASK"
        elif any(_fn_lower.endswith(e) for e in (".jpg", ".jpeg", ".png", ".heic", ".webp")):
            if any(w in _caption_lower for w in ["дефект", "акт", "технадзор", "нарушен"]):
                _task_type = "TECHNADZOR_TASK"
            else:
                _task_type = "OCR_TASK"
        elif any(w in _caption_lower for w in ["смета", "расчёт", "посчитай", "калькул"]):
            _task_type = "ESTIMATE_TASK"
        elif any(w in _caption_lower for w in ["дефект", "акт", "технадзор"]):
            _task_type = "TECHNADZOR_TASK"
        try:
            conn.execute("UPDATE tasks SET task_type=? WHERE id=?", (_task_type, task_id))
            conn.commit()
        except Exception:
            pass
        logger.info("TASK_TYPE_DETECT_V1 task=%s type=%s", task_id, _task_type)
        # === END TASK_TYPE_DETECT_V1 ===

        # === DUPLICATE_GUARD_CALL_V1 ===
        try:
            _dupe = find_duplicate(conn, str(chat_id), int(topic_id or 0), file_id)
            if _dupe:
                file_name = data.get("file_name", "файл")
                _dupe_msg = duplicate_message(_dupe, file_name)
                # === RESULT_VALIDATOR_GUARD_V1 ===
                if _check_result_before_confirm(_dupe_msg):
                    # === TASK_WORKER_ARTIFACT_GATE_V1 ===
                    try:
                        if validate_engine_result is not None:
                            _twag_raw = ""
                            _twag_input_type = ""
                            try:
                                _twag_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
                            except Exception:
                                _twag_raw = ""
                            try:
                                _twag_input_type = str(task["input_type"] if "input_type" in task.keys() else "")
                            except Exception:
                                _twag_input_type = ""
                            _twag_result = _dupe_msg
                            _twag_check = validate_engine_result(
                                {"summary": _twag_result, "engine": "TASK_WORKER_ARTIFACT_GATE_V1"},
                                input_type=_twag_input_type,
                                user_text=_twag_raw,
                                topic_id=topic_id,
                            )
                            if not _twag_check.get("ok"):
                                _update_task(conn, task_id, state="FAILED", result="",
                                    error_message="TASK_WORKER_ARTIFACT_GATE_V1:" + str(_twag_check.get("reason") or "INVALID"))
                                _history(conn, task_id, "TASK_WORKER_ARTIFACT_GATE_V1:FAILED:" + str(_twag_check.get("reason") or "INVALID"))
                                return
                    except Exception as _twag_e:
                        logger.warning("TASK_WORKER_ARTIFACT_GATE_V1_ERR task=%s err=%s", task_id, _twag_e)
                    # === END_TASK_WORKER_ARTIFACT_GATE_V1 ===
                    _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_dupe_msg, error_message="")
                else:
                    _update_task(conn, task_id, state="FAILED", result=_dupe_msg, error_message="FORBIDDEN_PHRASE")
                # === END RESULT_VALIDATOR_GUARD_V1 ===
                _history(conn, task_id, "state:AWAITING_CONFIRMATION:duplicate_guard")
                conn.commit()
                from core.reply_sender import send_reply_ex
                send_reply_ex(chat_id=str(chat_id), text=_dupe_msg, reply_to_message_id=reply_to, message_thread_id=topic_id)
                return
        except Exception as _dge:
            logger.warning("DUPLICATE_GUARD_CALL_ERR %s", _dge)
        # === END DUPLICATE_GUARD_CALL_V1 ===
        file_name = data["file_name"]
    except Exception as e:
        logger.error(f"DRIVE_FILE: invalid raw_input for {task_id}: {e}")
        _update_task(conn, task_id, state="FAILED", error_message="invalid raw_input")
        return

    local_path = f"/root/.areal-neva-core/runtime/drive_files/{task_id}_{file_name}"
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    logger.info(f"DRIVE_FILE: downloading {file_id} -> {local_path}")
    ok = _download_from_drive(file_id, local_path)  # HOTFIX_OK_BEFORE_SIZE_CHECK_V1
    # === FILE_SIZE_LIMIT_V1 ===
    if ok and local_path and os.path.exists(local_path):
        _fsize = os.path.getsize(local_path)
        if _fsize > 50 * 1024 * 1024:  # 50MB
            _update_task(conn, task_id, state="FAILED",
                        result="", error_message="FILE_TOO_LARGE")
            conn.commit()
            from core.reply_sender import send_reply_ex
            send_reply_ex(chat_id=str(chat_id),
                         text="Файл слишком большой (>50MB). Сожми или разбей на части.",
                         reply_to_message_id=reply_to, message_thread_id=topic_id)
            return
    # === END FILE_SIZE_LIMIT_V1 ===
    # === FILE_INTAKE_ROUTER_V1_WIRED ===
    if ok and local_path and os.path.exists(local_path):
        try:
            from core.file_intake_router import route_file, detect_intent, detect_intent_from_filename, should_ask_clarification, get_clarification_message
            _fir_caption = data.get("caption", "") or raw_input or ""
            _fir_intent = detect_intent(_fir_caption) or detect_intent_from_filename(file_name)
            _fir_topic_role = ""
            if _fir_intent:
                _fir_result = await route_file(local_path, task_id, int(topic_id or 0), _fir_intent)
                if _fir_result and _fir_result.get("success"):
                    _fir_msg = _fir_result.get("result_text") or _fir_result.get("drive_link") or "Готово"
                    # === TASK_WORKER_ARTIFACT_GATE_V1 ===
                    try:
                        if validate_engine_result is not None:
                            _twag_raw = ""
                            _twag_input_type = ""
                            try:
                                _twag_raw = str(task["raw_input"] if "raw_input" in task.keys() else "")
                            except Exception:
                                _twag_raw = ""
                            try:
                                _twag_input_type = str(task["input_type"] if "input_type" in task.keys() else "")
                            except Exception:
                                _twag_input_type = ""
                            _twag_result = _fir_msg
                            _twag_check = validate_engine_result(
                                {"summary": _twag_result, "engine": "TASK_WORKER_ARTIFACT_GATE_V1"},
                                input_type=_twag_input_type,
                                user_text=_twag_raw,
                                topic_id=topic_id,
                            )
                            if not _twag_check.get("ok"):
                                _update_task(conn, task_id, state="FAILED", result="",
                                    error_message="TASK_WORKER_ARTIFACT_GATE_V1:" + str(_twag_check.get("reason") or "INVALID"))
                                _history(conn, task_id, "TASK_WORKER_ARTIFACT_GATE_V1:FAILED:" + str(_twag_check.get("reason") or "INVALID"))
                                return
                    except Exception as _twag_e:
                        logger.warning("TASK_WORKER_ARTIFACT_GATE_V1_ERR task=%s err=%s", task_id, _twag_e)
                    # === END_TASK_WORKER_ARTIFACT_GATE_V1 ===
                    _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_fir_msg, error_message="")
                    _history(conn, task_id, "state:AWAITING_CONFIRMATION:file_intake_router")
                    conn.commit()
                    from core.reply_sender import send_reply_ex
                    send_reply_ex(chat_id=str(chat_id), text=_fir_msg, reply_to_message_id=reply_to, message_thread_id=topic_id)
                    return
            elif should_ask_clarification(_fir_caption, has_file=True):
                _fir_clarif = get_clarification_message(file_name, int(topic_id or 0))
                _update_task(conn, task_id, state="WAITING_CLARIFICATION", result=_fir_clarif, error_message="")
                conn.commit()
                from core.reply_sender import send_reply_ex
                send_reply_ex(chat_id=str(chat_id), text=_fir_clarif, reply_to_message_id=reply_to, message_thread_id=topic_id)
                return
        except Exception as _fir_err:
            logger.warning("FILE_INTAKE_ROUTER_V1_ERR task=%s err=%s", task_id, _fir_err)
    # === END FILE_INTAKE_ROUTER_V1_WIRED ===
    if not ok:
        _update_task(conn, task_id, state="FAILED", error_message="download failed")
        return

    conn.execute("UPDATE drive_files SET stage='downloaded' WHERE task_id=?", (task_id,))

    result = f"Файл {file_name} скачан, ожидает анализа"
    try:
        _, _, topic_role, _ = _load_memory_context(chat_id, topic_id)
        analysis = await analyze_downloaded_file(
            local_path=local_path,
            file_name=file_name,
            mime_type=data.get("mime_type", ""),
            user_text=data.get("caption", ""),
            topic_role=topic_role,
        )
        if isinstance(analysis, dict):
            summary = _s(analysis.get("summary")) or result
            artifact_path = _s(analysis.get("artifact_path"))
            artifact_name = _s(analysis.get("artifact_name")) or os.path.basename(artifact_path)
            result = summary
            if artifact_path and os.path.exists(artifact_path):
                try:
                    upload_res = await upload_file_to_topic(artifact_path, artifact_name, chat_id, topic_id)
                    if isinstance(upload_res, dict) and upload_res.get("ok") and upload_res.get("drive_file_id"):
                        result = summary + f"\n\nАртефакт: https://drive.google.com/file/d/{upload_res.get('drive_file_id')}/view"
                    # === QUALITY_GATE_WIRED_V1 ===
                    _qg = _quality_gate_artifact(
                        drive_link=result,
                        input_type=input_type,
                        task_type=_task_type if '_task_type' in dir() else ""
                    )
                    if not _qg.get("ok"):
                        logger.warning("QUALITY_GATE_FAIL task=%s reason=%s", task_id, _qg.get("reason"))
                    # === END QUALITY_GATE_WIRED_V1 ===
                    # === TEMP_CLEANUP_AFTER_UPLOAD_V1 ===
                    try:
                        _tc_upload([local_path])
                        _tc_task(task_id)
                    except Exception:
                        pass
                    # === END TEMP_CLEANUP_AFTER_UPLOAD_V1 ===
                        # === PATCH: save_pin + save_memory + log ===
                        try:
                            save_pin(chat_id, task_id, result, topic_id)
                            _save_memory(chat_id, topic_id, raw_input, result)
                            logger.info(f"DRIVE_FILE pin_memory_saved task_id={task_id}")
                        except Exception as e:
                            logger.error(f"DRIVE_FILE pin/memory failed task={task_id} err={e}")
                        # === END PATCH ===
                    else:
                        result = summary + "\n\nАртефакт создан, но загрузка в Drive не подтвердилась"
                except Exception as e:
                    logger.error(f"DRIVE_FILE artifact upload failed task={task_id} err={e}")
                    result = summary + "\n\nАртефакт создан локально, но загрузка в Drive завершилась ошибкой"
    except Exception as e:
        logger.error(f"DRIVE_FILE analyze skipped task={task_id} err={e}")

    _update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=_ff13c_strip_manifest_links(result))
    logger.info(f"DRIVE_FILE: {task_id} processed")



# === SINGLE_CHAR_REPLY_AS_PRICE_CHOICE_V1 ===
# Однобуквенный выбор цены и голосовой выбор должны продолжать parent task, а не создавать общий ответ
# AWAITING_PRICE_CONFIRMATION_STATE_V1
# VOICE_REPLY_TO_PARENT_TASK_V1
# === END_SINGLE_CHAR_REPLY_AS_PRICE_CHOICE_V1 ===

# === STARTUP_RECOVERY_V1_MAIN_WRAP ===
try:
    import inspect as _startup_recovery_inspect_v1
    _orig_task_worker_main_startup_recovery_v1 = main

    async def main(*args, **kwargs):
        try:
            if run_startup_recovery is not None:
                await run_startup_recovery(CORE_DB)
        except Exception as _startup_recovery_err:
            logger.warning("STARTUP_RECOVERY_V1_ERR %s", _startup_recovery_err)

        _res = _orig_task_worker_main_startup_recovery_v1(*args, **kwargs)
        if _startup_recovery_inspect_v1.isawaitable(_res):
            return await _res
        return _res
except Exception as _startup_recovery_wrap_err:
    logger.warning("STARTUP_RECOVERY_V1_WRAP_ERR %s", _startup_recovery_wrap_err)
# === END_STARTUP_RECOVERY_V1_MAIN_WRAP ===


if __name__ == "__main__":
    asyncio.run(main())

# === FULLFIX_08_PROJECT_ERROR_VISIBILITY ===


# === AWAITING_CONFIRMATION_ONLY_ON_REAL_RESULT_V1 ===
_GENERIC_RESULT_PATTERNS_V1 = [
    r"Файл скачан, ожидает анализа",
    r"Этот чат предназначен",
    r"Структура проекта включает этапы",
    r"Файл содержит раздел",
    r"не понял запрос",
    r"готов к выполнению",
]
def _is_generic_or_fake_result_v1(result: str) -> bool:
    r = _clean(_s(result), 2000)
    if not r:
        return True
    return any(re.search(p, r, re.I) for p in _GENERIC_RESULT_PATTERNS_V1)

try:
    _orig_is_valid_result_areal_v1 = _is_valid_result
    def _is_valid_result(text: str, raw_input: str) -> bool:
        if _is_generic_or_fake_result_v1(text):
            logger.warning("NO_GENERIC_RESPONSE_AS_RESULT_V1_BLOCKED %s", _clean(_s(text), 120))
            return False
        return _orig_is_valid_result_areal_v1(text, raw_input)
except Exception as _wrap_e:
    logger.warning("AWAITING_CONFIRMATION_ONLY_ON_REAL_RESULT_V1_WRAP_ERR %s", _wrap_e)

try:
    _orig_check_result_before_confirm_areal_v1 = _check_result_before_confirm
    def _check_result_before_confirm(result: str, input_type: str = "text", intent: str = "") -> bool:
        if _is_generic_or_fake_result_v1(result):
            logger.warning("NO_GENERIC_RESPONSE_AS_RESULT_V1_CONFIRM_BLOCKED %s", _clean(_s(result), 120))
            return False
        if input_type in ("drive_file", "file") and re.search(r"Файл скачан|ожидает анализа", _s(result), re.I):
            logger.warning("AWAITING_CONFIRMATION_ONLY_ON_REAL_RESULT_V1_BLOCKED")
            return False
        return _orig_check_result_before_confirm_areal_v1(result, input_type=input_type, intent=intent)
except Exception as _wrap_e:
    logger.warning("CHECK_RESULT_REAL_RESULT_V1_WRAP_ERR %s", _wrap_e)

try:
    import inspect as _inspect_repeat_v1
    _orig_process_ai_task_repeat_v1 = process_ai_task
    async def process_ai_task(*args, **kwargs):
        try:
            raw = kwargs.get("raw_input") or kwargs.get("user_text") or kwargs.get("prompt") or ""
            if not raw and args:
                raw = args[0]
            chat_id = str(kwargs.get("chat_id") or kwargs.get("chat") or "")
            topic_id = int(kwargs.get("topic_id") or 0)
            if _is_repeat_parent_task_v1(str(raw)) and chat_id:
                _rc = db(CORE_DB)
                try:
                    parent = _find_repeat_parent_task_v1(_rc, chat_id, topic_id)
                    if parent:
                        parent_raw = _clean(_s(_task_field(parent, "raw_input", "")), 3000)
                        parent_result = _clean(_s(_task_field(parent, "result", "")), 3000)
                        enriched = (
                            "Продолжи последнюю активную задачу в этом топике. "
                            "Не отвечай общим описанием чата. "
                            "Если данных не хватает — задай один короткий вопрос.\n\n"
                            f"Команда владельца: {_clean(_s(raw), 500)}\n\n"
                            f"Родительская задача: {parent_raw}\n\n"
                            f"Последний результат: {parent_result}"
                        )
                        if "raw_input" in kwargs:
                            kwargs["raw_input"] = enriched
                        elif "user_text" in kwargs:
                            kwargs["user_text"] = enriched
                        elif "prompt" in kwargs:
                            kwargs["prompt"] = enriched
                        elif args:
                            args = (enriched,) + tuple(args[1:])
                        logger.info("REPLY_REPEAT_PARENT_TASK_V1 parent=%s topic=%s", _task_field(parent, "id", ""), topic_id)
                finally:
                    _rc.close()
        except Exception as _repeat_e:
            logger.warning("REPLY_REPEAT_PARENT_TASK_V1_WRAP_ERR %s", _repeat_e)
        _res = _orig_process_ai_task_repeat_v1(*args, **kwargs)
        if _inspect_repeat_v1.isawaitable(_res):
            return await _res
        return _res
except Exception as _repeat_wrap_e:
    logger.warning("REPLY_REPEAT_PARENT_TASK_V1_PROCESS_WRAP_ERR %s", _repeat_wrap_e)
# === END_AWAITING_CONFIRMATION_ONLY_ON_REAL_RESULT_V1 ===

====================================================================================================
END_FILE: task_worker.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: telegram_daemon.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 9367c85c169d9f49fb57426d0dbb9b8f1d876582efab59d00c8d42a4a4c73f9c
====================================================================================================
import json
import asyncio, hashlib, json, logging, os, re, uuid, fcntl, tempfile, time
from datetime import datetime, timezone, timedelta
import aiofiles, aiohttp, aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.types import BufferedInputFile, FSInputFile
from google_io import upload_to_drive
from core.drive_folder_resolver import get_or_create_topic_folder
from core.topic_drive_oauth import upload_file_to_topic

BOT_TOKEN = <REDACTED_SECRET>"TELEGRAM_BOT_TOKEN") or "").strip()
DB = "/root/.areal-neva-core/data/core.db"
VOICE_DIR = "/root/.areal-neva-core/runtime/voice_queue"
MEMORY_FILES = "/root/.areal-neva-core/data/memory_files"
CHAT_MAP_FILE = os.path.join(MEMORY_FILES, "CHAT_MAP.json")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN missing")

for d in ["GLOBAL", "CHATS", "SYSTEM", "ERRORS"]:
    os.makedirs(os.path.join(MEMORY_FILES, d), exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s DAEMON: %(message)s")
logger = logging.getLogger("telegram_daemon")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

SYSTEM_CMDS = ["память", "память оркестра", "выгрузи память", "статус", "архив", "сброс задач", "очистить задачи", "yzon", "дамп", "язон", "язон файл", "дамп файл", "память файл", "архив файл", "система", "система файл", "код файл", "файл"]
CANCEL_CMDS = ["отбой", "отмена", "не надо"]
EZONE_KEYS = ("system", "architecture", "pipeline", "memory")
EZONE_EXTS = (".json", ".jsonl", ".txt")
SEARCH_TRIGGERS = ["цена", "наличие", "где купить", "площадка", "сайт", "сравнение", "новости", "актуальная"]
SHORT_CONFIRM = ["да", "нет", "ок", "подтверждаю", "не так", "ага", "верно"]
NEGATIVE_CONFIRM = ["нет", "не так"]
FINISH_PHRASES = [
    "спасибо поиск завершен", "поиск завершен",
    "не надо", "можно завершать",
    "задача закрыта", "закрывай", "хватит"
]
CANCEL_PHRASES = [
    "все запросы отменены", "отменяю все запросы", "сброс задач",
    "очистить задачи", "отмена", "отменяю", "сброс", "отбой"
]

_RECENT_INGEST = {}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def normalize_json_text(text: str) -> str:
    if not text: return text
    replacements = {"“": '"', "”": '"', "„": '"', "«": '"', "»": '"', "‘": "'", "’": "'", "…": "..."}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()

def is_ezone_payload(text: str) -> bool:
    if not text: return False
    norm = normalize_json_text(text)
    try:
        data = json.loads(norm)
        return isinstance(data, dict) and any(k in data for k in EZONE_KEYS)
    except:
        low = norm.lower()
        return any(k in low for k in EZONE_KEYS)

def content_hash(text: str) -> str:
    return hashlib.sha256(normalize_json_text(text).encode()).hexdigest()

def build_chat_key(telegram_chat_id: int) -> str:
    return f"{telegram_chat_id}__telegram"

def update_chat_map_atomic(telegram_chat_id: int, chat_key: str):
    lock_file = CHAT_MAP_FILE + ".lock"
    try:
        with open(lock_file, "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                chat_map = json.load(open(CHAT_MAP_FILE)) if os.path.exists(CHAT_MAP_FILE) else {}
                tg_id = str(telegram_chat_id)
                if tg_id not in chat_map:
                    chat_map[tg_id] = {}
                elif isinstance(chat_map[tg_id], list):
                    chat_map[tg_id] = {k: "unknown" for k in chat_map[tg_id]}
                chat_map[tg_id] = {k: v for k, v in chat_map[tg_id].items() if "unknown" not in k}
                chat_map[tg_id][chat_key] = "telegram"
                fd, tmp = tempfile.mkstemp(dir=os.path.dirname(CHAT_MAP_FILE), prefix=".chat_map_", suffix=".tmp")
                with os.fdopen(fd, "w") as f:
                    json.dump(chat_map, f, ensure_ascii=False, indent=2)
                    f.flush(); os.fsync(f.fileno())
                os.replace(tmp, CHAT_MAP_FILE)
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)
    except Exception as e:
        logger.error("CHAT_MAP update failed: %s", e)
    finally:
        try: os.unlink(lock_file)
        except: pass

def is_duplicate_today(hash_val: str, chat_key: str) -> bool:
    dup_file = os.path.join(MEMORY_FILES, "CHATS", chat_key, ".duplicates.jsonl")
    today = today_key()
    if os.path.exists(dup_file):
        with open(dup_file) as f:
            for line in f:
                try:
                    if json.loads(line).get("hash") == hash_val and json.loads(line).get("date") == today:
                        return True
                except: pass
    os.makedirs(os.path.dirname(dup_file), exist_ok=True)
    with open(dup_file, "a") as f:
        f.write(json.dumps({"hash": hash_val, "date": today, "ts": now_iso()}) + "\n")
    return False

def save_ezone_json(text: str, telegram_chat_id: int) -> tuple:
    norm = normalize_json_text(text)
    try: data = json.loads(norm)
    except: data = {"raw_text": norm}
    if not isinstance(data, dict): data = {"raw_text": norm}
    
    chat_key = build_chat_key(telegram_chat_id)
    ts = now_iso()
    hash_val = content_hash(text)
    
    if is_duplicate_today(hash_val, chat_key):
        return False, chat_key, "duplicate"
    
    data["_meta"] = {"chat_key": chat_key, "ingested_at": ts, "source": "telegram"}
    chat_dir = os.path.join(MEMORY_FILES, "CHATS", chat_key)
    os.makedirs(chat_dir, exist_ok=True)
    
    with open(os.path.join(chat_dir, "raw.json"), "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    entry = json.dumps({"timestamp": ts, "data": data}, ensure_ascii=False)
    with open(os.path.join(chat_dir, "timeline.jsonl"), "a") as f:
        f.write(entry + "\n")
    with open(os.path.join(MEMORY_FILES, "GLOBAL", "timeline.jsonl"), "a") as f:
        f.write(json.dumps({"timestamp": ts, "chat_key": chat_key, "data": data}, ensure_ascii=False) + "\n")
    
    for key in EZONE_KEYS:
        if key in data:
            with open(os.path.join(MEMORY_FILES, "SYSTEM", f"{key}.jsonl"), "a") as f:
                f.write(json.dumps({"timestamp": ts, "chat_key": chat_key, "data": data[key]}, ensure_ascii=False) + "\n")
    
    update_chat_map_atomic(telegram_chat_id, chat_key)
    logger.info("eZone saved: chat_key=%s telegram_chat=%s", chat_key, telegram_chat_id)
    return True, chat_key, ""


def dump_yzon_state(chat_id: int) -> str:
    import sqlite3, json

    result = {
        "system": {"name": "AREAL-NEVA ORCHESTRA", "role": "task execution system"},
        "architecture": {
            "pipeline": "telegram_daemon -> task_worker -> ai_router -> reply_sender",
            "memory": "memory.db + memory_files",
            "storage": "Google Drive",
            "mode": "server-first"
        },
        "runtime": {
            "chat_id": str(chat_id),
            "has_active_task": False,
            "has_active_pin": False,
            "daemon": "running",
            "worker": "running"
        },
        "active_context": {},
        "recent_results": [],
        "recent_decisions": []
    }

    try:
        conn = sqlite3.connect("/root/.areal-neva-core/data/core.db")

        cur = conn.execute(
            "SELECT id, state, raw_input FROM tasks WHERE chat_id = ? AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION') ORDER BY created_at DESC LIMIT 1",
            (str(chat_id),)
        )
        row = cur.fetchone()
        if row:
            result["runtime"]["has_active_task"] = True
            result["active_context"]["task_id"] = row[0]
            result["active_context"]["state"] = row[1]
            result["active_context"]["input"] = row[2][:200] if row[2] else ""

        cur = conn.execute(
            "SELECT task_id FROM pin WHERE chat_id = ? AND state = 'ACTIVE' ORDER BY updated_at DESC LIMIT 1",
            (str(chat_id),)
        )
        pin_row = cur.fetchone()
        if pin_row:
            result["runtime"]["has_active_pin"] = True
            result["active_context"]["active_pin"] = pin_row[0]

        cur = conn.execute(
            "SELECT id, result FROM tasks WHERE chat_id = ? AND state = 'DONE' AND result IS NOT NULL ORDER BY updated_at DESC LIMIT 5",
            (str(chat_id),)
        )
        for row in cur.fetchall():
            result["recent_results"].append({"task_id": row[0], "summary": row[1][:200] if row[1] else ""})

        cur = conn.execute(
            "SELECT task_id, action FROM task_history WHERE task_id IN (SELECT id FROM tasks WHERE chat_id = ?) ORDER BY created_at DESC LIMIT 10",
            (str(chat_id),)
        )
        for row in cur.fetchall():
            result["recent_decisions"].append({"task_id": row[0], "action": row[1]})

        conn.close()
    except Exception as e:
        result["error"] = str(e)

    return json.dumps(result, ensure_ascii=False, indent=2)


def dump_system_state() -> str:
    import sqlite3, json, os
    from datetime import datetime, timezone

    result = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "chat_id": None,
        "active_task": None,
        "active_pin": None,
        "recent_results": [],
        "architecture": {
            "system": "AREAL-NEVA ORCHESTRA",
            "stack": "telegram_daemon + task_worker + ai_router + OpenRouter",
            "memory": "memory_files + memory.db",
            "files": "Google Drive via google_io"
        }
    }

    try:
        conn = sqlite3.connect("/root/.areal-neva-core/data/core.db")
        cur = conn.execute("SELECT id, state, raw_input FROM tasks WHERE chat_id = '-1003725299009' AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION') ORDER BY created_at DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            result["chat_id"] = "-1003725299009"
            result["active_task"] = {"id": row[0], "state": row[1], "input": row[2][:200]}
        
        cur = conn.execute("SELECT task_id FROM pin WHERE chat_id = '-1003725299009' AND state = 'ACTIVE' ORDER BY updated_at DESC LIMIT 1")
        pin_row = cur.fetchone()
        if pin_row:
            result["active_pin"] = pin_row[0]
        
        cur = conn.execute("SELECT id, result FROM tasks WHERE chat_id = '-1003725299009' AND state = 'DONE' AND result IS NOT NULL ORDER BY updated_at DESC LIMIT 20")
        for row in cur.fetchall():
            result["recent_results"].append({"task_id": row[0], "summary": row[1][:200]})
        
        conn.close()
    except Exception as e:
        result["error"] = str(e)

    return json.dumps(result, ensure_ascii=False, indent=2)

def split_message(text: str, limit: int = 4000) -> list:
    text = text or ""
    parts = []
    while text and len(parts) < 10:
        if len(text) <= limit:
            parts.append(text); break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1 or split_at < limit // 3:
            split_at = limit
        parts.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return parts or [""]

async def create_task(message: types.Message, input_type: str, raw_input: str, state: str = "NEW"):
    task_id = str(uuid.uuid4())
    now = now_iso()
    user_id = getattr(message.from_user, "id", 0) if message.from_user else 0
    topic_id = getattr(message, "message_thread_id", None) or 0
    async with aiosqlite.connect(DB) as db:
        cols = [r[1] for r in await (await db.execute("PRAGMA table_info(tasks)")).fetchall()]
        if "topic_id" in cols:
            await db.execute(
                "INSERT INTO tasks (id, chat_id, user_id, input_type, raw_input, state, reply_to_message_id, topic_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (task_id, message.chat.id, user_id, input_type, raw_input, state, message.message_id, topic_id, now, now))
        else:
            await db.execute(
                "INSERT INTO tasks (id, chat_id, user_id, input_type, raw_input, state, reply_to_message_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (task_id, message.chat.id, user_id, input_type, raw_input, state, message.message_id, now, now))
        await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (task_id, f"created:{state}", now))
        await db.commit()

    # === TELEGRAM_TIMELINE_APPEND_V1 ===
    try:
        _tl_chat_key = build_chat_key(message.chat.id)
        _tl_chat_dir = os.path.join(MEMORY_FILES, "CHATS", _tl_chat_key)
        os.makedirs(_tl_chat_dir, exist_ok=True)
        os.makedirs(os.path.join(MEMORY_FILES, "GLOBAL"), exist_ok=True)
        _tl_entry = json.dumps({
            "timestamp": now, "chat_id": str(message.chat.id),
            "topic_id": int(topic_id or 0), "task_id": task_id,
            "input_type": input_type, "state": state,
            "raw_input": str(raw_input or "")[:4000],
            "source": "telegram_daemon_create_task",
        }, ensure_ascii=False)
        for _tl_path in [
            os.path.join(_tl_chat_dir, "timeline.jsonl"),
            os.path.join(MEMORY_FILES, "GLOBAL", "timeline.jsonl"),
        ]:
            with open(_tl_path, "a", encoding="utf-8") as _f:
                _f.write(_tl_entry + "\n")
    except Exception as _tl_e:
        logger.warning("TELEGRAM_TIMELINE_APPEND_V1_ERR %s", _tl_e)
    # === END TELEGRAM_TIMELINE_APPEND_V1 ===

    logger.info("Task %s created state=%s topic_id=%s", task_id, state, topic_id)
    return task_id

async def continue_parent_task(parent_id: str, user_text: str):
    now = now_iso()
    merged_sql = "COALESCE(raw_input,'') || ?"
    suffix = "\n\nПродолжение пользователя:\n" + user_text
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            f"UPDATE tasks SET raw_input={merged_sql}, state='IN_PROGRESS', updated_at=? WHERE id=?",
            (suffix, now, parent_id)
        )
        await db.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
            (parent_id, "continuation:IN_PROGRESS", now)
        )
        await db.commit()
    logger.info("Task %s continued -> IN_PROGRESS", parent_id)

async def get_active_task(chat_id: int) -> dict:
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id, state, raw_input FROM tasks WHERE chat_id=? AND state IN ('NEW','IN_PROGRESS') ORDER BY created_at DESC LIMIT 1",
            (chat_id,))
        row = await cur.fetchone()
        if row:
            return {"id": row[0], "state": row[1], "raw_input": row[2]}
        return None

async def cancel_active_task(chat_id: int):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
            (chat_id,)
        )
        tasks = await cur.fetchall()
        for t in tasks:
            await db.execute("UPDATE tasks SET state='CANCELLED', updated_at=? WHERE id=?", (now_iso(), t[0]))
            await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (t[0], "cancelled", now_iso()))
        await db.commit()
async def reset_all_open_tasks(chat_id: int):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
            (chat_id,)
        )
        rows = await cur.fetchall()
        now = now_iso()
        for row in rows:
            task_id = row[0]
            await db.execute(
                "UPDATE tasks SET state='CANCELLED', updated_at=? WHERE id=?",
                (now, task_id)
            )
            await db.execute(
                "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                (task_id, "reset:CANCELLED", now)
            )
        try:
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE chat_id=? AND state='ACTIVE'",
                (now, str(chat_id))
            )
        except Exception:
            pass
        await db.commit()

def _has_any_phrase(lower_text: str, phrases: list[str]) -> bool:
    t = (lower_text or "").strip()
    return t in phrases

async def close_latest_open_task(chat_id: int, action: str = "finish:DONE") -> bool:
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC, created_at DESC LIMIT 1",
            (chat_id,)
        )
        row = await cur.fetchone()
        if not row:
            return False
        task_id = row[0]
        now = now_iso()
        await db.execute(
            "UPDATE tasks SET state='DONE', updated_at=? WHERE id=?",
            (now, task_id)
        )
        await db.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
            (task_id, action, now)
        )
        try:
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'",
                (now, task_id)
            )
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE chat_id=? AND state='ACTIVE'",
                (now, str(chat_id))
            )
        except Exception:
            pass
        await db.commit()
        return True

async def cancel_all_open_tasks(chat_id: int, topic_id: int = 0) -> int:
    async with aiosqlite.connect(DB) as db:
        if topic_id > 0:
            cur = await db.execute(
                "SELECT id FROM tasks WHERE chat_id=? AND topic_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
                (chat_id, topic_id)
            )
        else:
            cur = await db.execute(
                "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
                (chat_id,)
            )
        rows = await cur.fetchall()
        now = now_iso()
        count = 0
        for row in rows:
            task_id = row[0]
            await db.execute(
                "UPDATE tasks SET state='CANCELLED', updated_at=? WHERE id=?",
                (now, task_id)
            )
            await db.execute(
                "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                (task_id, "cancelled:CANCELLED", now)
            )
            count += 1
        try:
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE chat_id=? AND state='ACTIVE'",
                (now, str(chat_id))
            )
        except Exception:
            pass
        await db.commit()
        return count

async def _find_parent_task(chat_id: int, reply_to: int | None, topic_id: int = 0):
    async with aiosqlite.connect(DB) as db:
        cols = [r[1] for r in await (await db.execute("PRAGMA table_info(tasks)")).fetchall()]
        has_topic = "topic_id" in cols and topic_id > 0
        topic_filter = " AND topic_id=?" if has_topic else ""
        topic_args = (topic_id,) if has_topic else ()
        if reply_to:
            cur = await db.execute(
                f"SELECT id, state FROM tasks WHERE chat_id=? AND bot_message_id=?{topic_filter} AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                (chat_id, reply_to) + topic_args
            )
            row = await cur.fetchone()
            if row:
                return row
            cur = await db.execute(
                f"SELECT id, state FROM tasks WHERE chat_id=? AND reply_to_message_id=?{topic_filter} AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                (chat_id, reply_to) + topic_args
            )
            row = await cur.fetchone()
            if row:
                return row
        cur = await db.execute(
            f"SELECT id, state FROM tasks WHERE chat_id=?{topic_filter} AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
            (chat_id,) + topic_args
        )
        return await cur.fetchone()

async def _handle_control_text(message, tg_id: int, text: str, lower: str, reply_to: int | None, topic_id: int = 0) -> bool:
    if _has_any_phrase(lower, CANCEL_PHRASES):
        closed = await cancel_all_open_tasks(tg_id, topic_id)
        await message.answer("Все запросы отменены" if closed else "Нет активных задач")
        return True

    parent = await _find_parent_task(tg_id, reply_to, topic_id)

    if _has_any_phrase(lower, FINISH_PHRASES):
        if parent:
            parent_id = parent[0]
            now = now_iso()
            async with aiosqlite.connect(DB) as db:
                await db.execute("UPDATE tasks SET state='DONE', updated_at=? WHERE id=?", (now, parent_id))
                await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "finish:DONE", now))
                await db.execute("UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'", (now, parent_id))
                await db.commit()
            await message.answer("Задача закрыта")
            return True
        closed = await close_latest_open_task(tg_id, "finish:DONE")
        await message.answer("Задача закрыта" if closed else "Нет активных задач")
        return True

    if not parent:
        return False

    parent_id, parent_state = parent[0], parent[1]

    if parent_state == "AWAITING_CONFIRMATION":
        if lower.strip() in SHORT_CONFIRM and lower.strip() not in NEGATIVE_CONFIRM:
            now = now_iso()
            async with aiosqlite.connect(DB) as db:
                await db.execute("UPDATE tasks SET state='DONE', updated_at=? WHERE id=?", (now, parent_id))
                await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "confirmed:DONE", now))
                await db.execute("UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'", (now, parent_id))
                await db.commit()
            await message.answer("Задача завершена")
            return True
        if lower.strip() in NEGATIVE_CONFIRM:
            now = now_iso()
            async with aiosqlite.connect(DB) as db:
                await db.execute("UPDATE tasks SET state='WAITING_CLARIFICATION', updated_at=? WHERE id=?", (now, parent_id))
                await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "rejected:WAITING_CLARIFICATION", now))
                await db.execute("UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'", (now, parent_id))
                await db.commit()
            await message.answer("Хорошо, доработаю. Подтверждение снято.  # FULLFIX_02_E")
            return True

    if parent_state == "WAITING_CLARIFICATION":
        now = now_iso()
        async with aiosqlite.connect(DB) as db:
            await db.execute("UPDATE tasks SET state='IN_PROGRESS', updated_at=? WHERE id=?", (now, parent_id))
            await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"clarified:{text}", now))
            await db.commit()
        await message.answer("Принято, продолжаю")
        return True

    if parent_state == "IN_PROGRESS" and reply_to:
        now = now_iso()
        async with aiosqlite.connect(DB) as db:
            await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"continued:{text}", now))
            await db.commit()
        await message.answer("Принято, продолжаю")
        return True

    return False


async def download_telegram_file(file_path: str, local_path: str) -> str:
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    async with aiohttp.ClientSession() as s:
        async with s.get(url, timeout=aiohttp.ClientTimeout(total=300)) as r:
            r.raise_for_status()
            async with aiofiles.open(local_path, "wb") as f:
                await f.write(await r.read())
    return local_path

@dp.message()
async def universal_handler(message: types.Message):
    update_id = getattr(message, 'update_id', None)
    if update_id:
        async with aiosqlite.connect(DB) as db:
            await db.execute("DELETE FROM processed_updates WHERE created_at < ?", ((datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),))
            cur = await db.execute("SELECT 1 FROM processed_updates WHERE update_id = ?", (update_id,))
            if await cur.fetchone():
                await db.commit()
                return
            await db.execute("INSERT INTO processed_updates (update_id, created_at) VALUES (?, ?)", (update_id, now_iso()))
            await db.commit()
    
    try:
        text = message.text or ""
        lower = text.lower()
        tg_id = message.chat.id
        now_ts = time.monotonic()
        reply_to = message.reply_to_message.message_id if message.reply_to_message else None
        topic_id = int(getattr(message, "message_thread_id", 0) or 0)
        
        # 1. SYSTEM COMMANDS
        if lower in SYSTEM_CMDS:
            if lower in ("сброс задач", "очистить задачи"):
                await reset_all_open_tasks(tg_id)
                await message.answer("Все незакрытые задачи и активные pin закрыты")
            elif lower == "статус":
                async with aiosqlite.connect(DB) as db:
                    cur = await db.execute("SELECT state, COUNT(*) FROM tasks WHERE chat_id = ? GROUP BY state", (tg_id,))
                    rows = await cur.fetchall()
                    cur = await db.execute("SELECT task_id FROM pin WHERE chat_id = ? AND state = 'ACTIVE'", (str(tg_id),))
                    pin_row = await cur.fetchone()
                    status_msg = "Статус:\n" + "\n".join([f"{r[0]}: {r[1]}" for r in rows]) if rows else "Нет задач"
                    if pin_row:
                        status_msg += f"\nАктивный pin: {pin_row[0]}"
                    await message.answer(status_msg)
            elif lower == "yzon":
                dump = dump_yzon_state(tg_id)
                await message.answer(dump)
                return
            elif lower == "дамп":
                import subprocess
                result = subprocess.run(["/root/.areal-neva-core/.venv/bin/python3", "/root/.areal-neva-core/orchestra_full_dump.py"], capture_output=True, text=True, timeout=60)
                dump_files = sorted([f for f in os.listdir("/root/.areal-neva-core/data/memory/UNSORTED") if f.startswith("orchestra_dump_")], reverse=True)
                if dump_files:
                    dump_path = f"/root/.areal-neva-core/data/memory/UNSORTED/{dump_files[0]}"
                    content=open(dump_path).read()
                    for part in split_message(content):
                        await message.answer(part)
                else:
                    await message.answer("Дамп не создан")
                return
            elif lower == "архив":
                async with aiosqlite.connect(DB) as db:
                    cur = await db.execute("SELECT id, state, substr(raw_input,1,100) FROM tasks WHERE chat_id = ? AND state IN ('DONE','FAILED','CANCELLED','ARCHIVED') ORDER BY updated_at DESC LIMIT 10", (tg_id,))
                    rows = await cur.fetchall()
                    if rows:
                        archive_msg = "Архив:\n" + "\n".join([f"{r[0][:8]}: {r[1]} - {r[2]}" for r in rows])
                    else:
                        archive_msg = "Архив пуст"
                    await message.answer(archive_msg)
            elif lower == "язон":
                dump = dump_yzon_state(tg_id)
                await message.answer(dump)
                return
            elif lower == "язон файл":
                dump = dump_yzon_state(tg_id)
                doc = BufferedInputFile(dump.encode("utf-8"), filename="yzon_state.json")
                await message.answer_document(doc)
                return
            elif lower == "дамп файл":
                import subprocess
                subprocess.run(["/root/.areal-neva-core/.venv/bin/python3", "/root/.areal-neva-core/orchestra_full_dump.py"], capture_output=True, text=True, timeout=60)
                dump_files = sorted([f for f in os.listdir("/root/.areal-neva-core/data/memory/UNSORTED") if f.startswith("orchestra_dump_")], reverse=True)
                if dump_files:
                    dump_path = f"/root/.areal-neva-core/data/memory/UNSORTED/{dump_files[0]}"
                    await message.answer_document(FSInputFile(dump_path, filename=dump_files[0]))
                else:
                    await message.answer("Дамп не создан")
                return
            elif lower == "память файл":
                import sqlite3 as _sq, json as _json
                try:
                    _mc = _sq.connect("/root/.areal-neva-core/data/memory.db")
                    _mc.row_factory = _sq.Row
                    _rows = _mc.execute("SELECT chat_id, key, value, timestamp FROM memory WHERE chat_id=? ORDER BY timestamp DESC LIMIT 200", (str(tg_id),)).fetchall()
                    _mc.close()
                    _data = [dict(r) for r in _rows]
                    doc = BufferedInputFile(_json.dumps(_data, ensure_ascii=False, indent=2).encode("utf-8"), filename="memory_dump.json")
                    await message.answer_document(doc)
                except Exception as _e:
                    await message.answer(f"Ошибка: {_e}")
                return
            elif lower == "архив файл":
                import sqlite3 as _sq, io, json as _json
                try:
                    _mc = _sq.connect("/root/.areal-neva-core/data/memory.db")
                    _mc.row_factory = _sq.Row
                    _rows = _mc.execute("SELECT key, value, timestamp FROM memory WHERE chat_id=? AND key LIKE 'archive_legacy_%' ORDER BY timestamp DESC LIMIT 100", (str(tg_id),)).fetchall()
                    _mc.close()
                    _data = [dict(r) for r in _rows]
                    doc = BufferedInputFile(_json.dumps(_data, ensure_ascii=False, indent=2).encode("utf-8"), filename="archive_dump.json")
                    await message.answer_document(doc)
                except Exception as _e:
                    await message.answer(f"Ошибка: {_e}")
                return
            elif lower in ("система", "система файл"):
                sys_info = (
                    "AREAL-NEVA ORCHESTRA\n"
                    "Server: 89.22.225.136 | Ubuntu 24.04\n"
                    "Bot: @ai_orkestra_all_bot\n"
                    "Models: deepseek/deepseek-chat + perplexity/sonar\n"
                    "Pipeline: telegram_daemon -> core.db -> task_worker -> ai_router -> Telegram\n"
                    "Services: telegram-ingress, areal-task-worker, areal-memory-api\n"
                )
                if lower == "система файл":
                    doc = BufferedInputFile(sys_info.encode("utf-8"), filename="system_info.txt")
                    await message.answer_document(doc)
                else:
                    await message.answer(sys_info)
                return
            elif lower == "код файл":
                import io, zipfile
                buf = io.BytesIO()
                files_to_zip = [
                    "/root/.areal-neva-core/task_worker.py",
                    "/root/.areal-neva-core/core/ai_router.py",
                    "/root/.areal-neva-core/telegram_daemon.py",
                ]
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for fp in files_to_zip:
                        if os.path.exists(fp):
                            zf.write(fp, os.path.basename(fp))
                doc = BufferedInputFile(buf.getvalue(), filename="core_code.zip")
                await message.answer_document(doc)
                return
            elif lower == "файл":
                import sqlite3 as _sq
                try:
                    _cc = _sq.connect("/root/.areal-neva-core/data/core.db")
                    _rows = _cc.execute("SELECT state, COUNT(*) as cnt FROM tasks GROUP BY state").fetchall()
                    _cc.close()
                    lines = ["AREAL-NEVA ORCHESTRA — краткий статус", ""]
                    for r in _rows:
                        lines.append(f"{r[0]}: {r[1]}")
                    doc = BufferedInputFile("\n".join(lines).encode("utf-8"), filename="status.md")
                    await message.answer_document(doc)
                except Exception as _e:
                    await message.answer(f"Ошибка: {_e}")
                return
            else:
                dump = dump_system_state()
                for part in split_message(dump):
                    await message.answer(part)
                    await asyncio.sleep(0.5)
            return
        
        # 2. CANCEL
        if lower in CANCEL_CMDS:
            await cancel_active_task(tg_id)
            await message.answer("Задача отменена")
            return
        
        # 3. FILE TASKS + EZONE FILE INGEST
        if message.document and message.document.file_name:
            # HEALTHCHECK_DAEMON_GUARD_V1
            try:
                _hc_check = " ".join([
                    str(message.document.file_name or ""),
                    str(message.caption or ""),
                ]).lower()
                if any(m in _hc_check for m in ("retry_queue_healthcheck", "healthcheck", "areal_hc_", "_hc_file")):
                    logger.info("HEALTHCHECK_DAEMON_GUARD_V1 ignored file=%s", message.document.file_name)
                    return
            except Exception as _hc_e:
                logger.warning("HEALTHCHECK_DAEMON_GUARD_V1_ERR %s", _hc_e)
            tg_file = await bot.get_file(message.document.file_id)
            local_path = f"/tmp/{uuid.uuid4()}_{message.document.file_name}"
            await download_telegram_file(tg_file.file_path, local_path)
            try:
                if message.document.file_name.lower().endswith(EZONE_EXTS):
                    drive_result = await upload_file_to_topic(local_path, message.document.file_name, tg_id, topic_id, getattr(message.document, "mime_type", "") or None)  # DAEMON_OAUTH_FIX_V1
                    with open(local_path, "r", errors="ignore") as f:
                        content = f.read()
                    if is_ezone_payload(content):
                        ok, chat_key, _ = save_ezone_json(content, tg_id)
                        _RECENT_INGEST[tg_id] = now_ts
                        await message.answer(f"Принял, память загружена ({chat_key})" if ok else "Уже загружено")
                        return
                else:
                    topic_id = getattr(message, "message_thread_id", 0) or 0
                    drive_result = await upload_file_to_topic(local_path, message.document.file_name, tg_id, topic_id, getattr(message.document, "mime_type", "") or None)
                    if isinstance(drive_result, dict) and drive_result.get("ok") and drive_result.get("drive_file_id"):
                        payload = {
                            "file_id": drive_result.get("drive_file_id", ""),
                            "file_name": message.document.file_name,
                            "mime_type": getattr(message.document, "mime_type", "") or "",
                            "caption": (message.caption or message.text or "").strip(),
                            "source": "telegram",
                            "telegram_message_id": message.message_id,
                            "telegram_chat_id": message.chat.id,
                        }
                        await create_task(message, "drive_file", json.dumps(payload, ensure_ascii=False), "NEW")
                        await message.answer("Файл принят в обработку")
                        return
                    else:
                        await message.answer("Ошибка загрузки файла в Drive")
                        return
            finally:
                try: os.remove(local_path)
                except: pass

        # 3A. PHOTO TASK
        if message.photo:
            photo = message.photo[-1]
            tg_file = await bot.get_file(photo.file_id)
            file_name = f"photo_{message.chat.id}_{message.message_id}.jpg"
            local_path = f"/tmp/{uuid.uuid4()}_{file_name}"
            await download_telegram_file(tg_file.file_path, local_path)
            try:
                drive_result = await upload_file_to_topic(local_path, file_name, tg_id, topic_id, "image/jpeg")
                if isinstance(drive_result, dict) and drive_result.get("ok") and drive_result.get("drive_file_id"):
                    payload = {
                        "file_id": drive_result.get("drive_file_id", ""),
                        "file_name": file_name,
                        "mime_type": "image/jpeg",
                        "caption": (message.caption or message.text or "").strip(),
                        "source": "telegram",
                        "telegram_message_id": message.message_id,
                        "telegram_chat_id": message.chat.id,
                    }
                    await create_task(message, "drive_file", json.dumps(payload, ensure_ascii=False), "NEW")
                    await message.answer("Фото принято в обработку")
                    return
                else:
                    await message.answer("Ошибка загрузки фото в Drive")
                    return
            finally:
                try: os.remove(local_path)
                except: pass
        
        # 4. EZONE TEXT INGEST
        if message.text and is_ezone_payload(text):
            ok, chat_key, _ = save_ezone_json(text, tg_id)
            _RECENT_INGEST[tg_id] = now_ts
            await message.answer(f"Принял, память загружена ({chat_key})" if ok else "Уже загружено")
            return
        
        # 5. ANTI-DUP AFTER INGEST
        if message.text:
            last = _RECENT_INGEST.get(tg_id, 0.0)
            if now_ts - last < 5:
                if text.lstrip().startswith("{") or any(k in lower for k in EZONE_KEYS):
                    return
        
        # 6. CONFIRMATION AND REPLY CONTINUATION
        active_confirm = None
        async with aiosqlite.connect(DB) as db:
            cur = await db.execute(
                "SELECT id, state FROM tasks WHERE chat_id = ? AND state = 'AWAITING_CONFIRMATION' ORDER BY updated_at DESC LIMIT 1",
                (tg_id,)
            )
            active_confirm = await cur.fetchone()

        if active_confirm and message.text:
            parent_id, parent_state = active_confirm
            if lower.strip() in SHORT_CONFIRM and lower.strip() not in NEGATIVE_CONFIRM:
                async with aiosqlite.connect(DB) as db:
                    await db.execute("UPDATE tasks SET state = 'DONE', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                    await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "confirmed:DONE", now_iso()))
                    await db.execute("UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'", (now_iso(), parent_id))
                    await db.commit()
                await message.answer("Задача завершена")
                return
            elif lower.strip() in NEGATIVE_CONFIRM:
                async with aiosqlite.connect(DB) as db:
                    await db.execute("UPDATE tasks SET state = 'WAITING_CLARIFICATION', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                    await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "rejected:WAITING_CLARIFICATION", now_iso()))
                    await db.execute("UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'", (now_iso(), parent_id))
                    await db.commit()
                await message.answer("Хорошо, доработаю. Подтверждение снято.  # FULLFIX_02_E")
                return

        if reply_to:
            async with aiosqlite.connect(DB) as db:
                cur = await db.execute(
                    "SELECT id, state FROM tasks WHERE chat_id = ? AND reply_to_message_id = ? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                    (tg_id, reply_to)
                )
                parent = await cur.fetchone()
            if parent:
                parent_id, parent_state = parent
                if parent_state == "WAITING_CLARIFICATION":
                    async with aiosqlite.connect(DB) as db:
                        await db.execute("UPDATE tasks SET state = 'IN_PROGRESS', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                        await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"clarified:{text}", now_iso()))
                        await db.commit()
                    await message.answer("Принято, продолжаю")
                elif lower.strip() in SHORT_CONFIRM and lower.strip() not in NEGATIVE_CONFIRM:
                    async with aiosqlite.connect(DB) as db:
                        await db.execute("UPDATE tasks SET state = 'IN_PROGRESS', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                        await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"confirmed:{text}", now_iso()))
                        await db.commit()
                    await message.answer("Принято, выполняю")
                else:
                    await message.answer("Уточните запрос")
                return

        # 7. SEARCH TASK
        if any(t in lower for t in SEARCH_TRIGGERS):
            await create_task(message, "search", text, "NEW")
            return
        
        # 8. VOICE
        if message.voice:
            tg_file = await bot.get_file(message.voice.file_id)
            local_path = os.path.join(VOICE_DIR, f"voice_{abs(tg_id)}_{message.message_id}.ogg")
            await download_telegram_file(tg_file.file_path, local_path)
            pass  # VOICE_UPLOAD_SKIP_V1 — голос не загружаем на Drive
            from core.stt_engine import transcribe_voice as _stt
            try:
                _transcript = await _stt(local_path)
            except Exception as _err:
                logger.error("STT_FAILED chat=%s err=%s", tg_id, _err)
                await message.answer("Голос не распознан. Повтори голосом или напиши текстом")
                return
            if not _transcript or not _transcript.strip():
                logger.error("STT_EMPTY chat=%s", tg_id)
                await message.answer("Не удалось получить текст из голосового. Повтори или напиши текстом")
                return
            voice_text = _transcript.strip()
            voice_lower = voice_text.lower()
            voice_reply_to = message.reply_to_message.message_id if message.reply_to_message else None
            _voice_topic_id = getattr(message, "message_thread_id", None) or 0

            # === PATCH_VOICE_CONFIRM_DIRECT ===
            # Voice does not populate message.text, so confirm/reject must be checked after STT
            try:
                _voice_cmd = voice_lower.strip().rstrip("!., ")
                async with aiosqlite.connect(DB) as db:
                    cur = await db.execute(
                        """
                        SELECT id, state
                        FROM tasks
                        WHERE chat_id = ?
                          AND COALESCE(topic_id,0) = COALESCE(?,0)
                          AND state = 'AWAITING_CONFIRMATION'
                        ORDER BY updated_at DESC
                        LIMIT 1
                        """,
                        (tg_id, _voice_topic_id)
                    )
                    _voice_active_confirm = await cur.fetchone()

                if _voice_active_confirm and _voice_cmd in SHORT_CONFIRM and _voice_cmd not in NEGATIVE_CONFIRM:
                    parent_id, parent_state = _voice_active_confirm
                    async with aiosqlite.connect(DB) as db:
                        await db.execute(
                            "UPDATE tasks SET state = 'DONE', updated_at = ? WHERE id = ?",
                            (now_iso(), parent_id)
                        )
                        await db.execute(
                            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                            (parent_id, "voice_confirmed:DONE", now_iso())
                        )
                        await db.execute(
                            "UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'",
                            (now_iso(), parent_id)
                        )
                        await db.commit()
                    await message.answer("Задача завершена")
                    return

                if _voice_active_confirm and _voice_cmd in NEGATIVE_CONFIRM:
                    parent_id, parent_state = _voice_active_confirm
                    async with aiosqlite.connect(DB) as db:
                        await db.execute(
                            "UPDATE tasks SET state = 'WAITING_CLARIFICATION', updated_at = ? WHERE id = ?",
                            (now_iso(), parent_id)
                        )
                        await db.execute(
                            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                            (parent_id, "voice_rejected:WAITING_CLARIFICATION", now_iso())
                        )
                        await db.execute(
                            "UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'",
                            (now_iso(), parent_id)
                        )
                        await db.commit()
                    await message.answer("Хорошо, доработаю. Подтверждение снято.  # FULLFIX_02_E")
                    return
            except Exception as _voice_confirm_err:
                logger.error("VOICE_CONFIRM_DIRECT_ERROR chat=%s err=%s", tg_id, _voice_confirm_err)
            # === END PATCH_VOICE_CONFIRM_DIRECT ===
            _VOICE_CONTROL = ["отбой", "отмена", "не надо", "всё", "готово", "можно закрывать", "задача закрыта", "да", "нет", "ок", "+"]
            if any(voice_lower.strip() == x for x in _VOICE_CONTROL):
                if await _handle_control_text(message, tg_id, voice_text, voice_lower, voice_reply_to, _voice_topic_id):
                    return
            try:
                await message.answer(f"🎤 {voice_text}")
            except Exception as _e:
                logger.warning("transcript_send_fail err=%s", _e)
            await create_task(message, "text", "[VOICE] " + voice_text, "NEW")
            return
        
        # 9. NORMAL TEXT
        if message.text:
            reply_to = message.reply_to_message.message_id if message.reply_to_message else None
            _text_topic_id = getattr(message, "message_thread_id", None) or 0
            if await _handle_control_text(message, tg_id, text, lower, reply_to, _text_topic_id):
                return
            # === CHAT_GUARD_V1 ===
            try:
                from core.intent_lock import is_chat_only as _ig_chat
                if _ig_chat(text):
                    return  # короткие реакции не создают задачи
            except Exception:
                pass
            # === END CHAT_GUARD_V1 ===
            await create_task(message, "text", text, "NEW")
            return
        
    except Exception as e:
        logger.error("HANDLER_CRASH: %s", e)
        try:
            await message.answer("Ошибка обработки")
        except:
            pass

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    logger.info("BOT STARTED id=%s username=%s", me.id, me.username)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
====================================================================================================
END_FILE: telegram_daemon.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/project_route_guard.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ba7de84f30ec6b9ef978ef3bf38bac5354e1ffb255730c3066e040d783b493b6
====================================================================================================
# === PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1 ===
# === PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1 ===
from __future__ import annotations

import json
import re
import sqlite3
from typing import Any, Dict, Optional

PROJECT_STRONG = (
    "сделай проект", "создай проект", "разработай проект", "подготовь проект",
    "проект монолит", "проект плиты", "проект фундамент", "проект кровли",
    "проект кж", "проект кд", "проект ар", "чертеж", "чертёж",
    "конструктивное решение", "проектное решение", "лист кж", "лист кд"
)

PROJECT_WEAK = (
    "кж", "кд", "ар", "км", "кмд", "плита", "фундамент", "армирование",
    "опалубка", "разрез", "узел", "схема", "спецификация арматуры"
)

ESTIMATE_ONLY = (
    "смета", "смету", "сметный", "расценка", "стоимость работ",
    "цены материалов", "кс-2", "кс2"
)

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()

def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")

def _task_field(task: Any, field: str, default: Any = "") -> Any:
    try:
        if hasattr(task, "keys") and field in task.keys():
            return task[field]
    except Exception:
        pass
    if isinstance(task, dict):
        return task.get(field, default)
    try:
        return getattr(task, field)
    except Exception:
        return default

def is_explicit_project_intent(text: Any) -> bool:
    low = _low(text)
    if not low:
        return False
    strong = any(x in low for x in PROJECT_STRONG)
    weak_project = sum(1 for x in PROJECT_WEAK if x in low) >= 2
    estimate_only = any(x in low for x in ESTIMATE_ONLY) and not strong and not weak_project
    if estimate_only:
        return False
    return bool(strong or weak_project)

def _format_links(res: Dict[str, Any]) -> str:
    lines = []
    for label, key in (
        ("DOCX", "docx_link"),
        ("XLSX", "xlsx_link"),
        ("PDF", "pdf_link"),
        ("Drive", "drive_link"),
    ):
        val = _s(res.get(key))
        if val and "drive.google.com" in val or "docs.google.com" in val:
            lines.append(f"{label}: {val}")
    return "\n".join(lines)

def format_project_result_message(res: Dict[str, Any], raw_input: str = "") -> str:
    section = _s(res.get("project_type") or res.get("section") or "КЖ")
    links = _format_links(res)
    if res.get("success") and links:
        msg = (
            "Проектный файл создан\n"
            f"Раздел: {section}\n"
            f"{links}\n\n"
            "Доволен результатом? Да / Уточни / Правки"
        )
    elif res.get("success"):
        msg = (
            "Проектный файл подготовлен локально, но ссылка Drive не подтверждена\n"
            f"Раздел: {section}\n"
            "Нужна проверка выгрузки"
        )
    else:
        err = _s(res.get("error")) or "PROJECT_RESULT_NOT_READY"
        if "PROJECT_TEMPLATE_MODEL_NOT_FOUND" in err:
            msg = (
                "Для проектного файла нужен образец проекта в этом топике\n"
                "Пришли КЖ/КД/АР файл как образец или напиши исходные данные проекта"
            )
        else:
            msg = (
                "Проектный файл не создан\n"
                f"Причина: {err}\n"
                "Уточни исходные данные или пришли образец проекта"
            )

    try:
        from core.output_sanitizer import sanitize_project_message
        return sanitize_project_message(msg)
    except Exception:
        return msg.strip()

async def prehandle_project_route_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))

    # === CANON_LIST_QUERY_GUARD_V1 ===
    if topic_id == 500:
        return None
    _list_signals = ("какие", "покажи", "перечисли", "что есть", "есть ли", "список", "что за образц", "какие образц", "покажи образц")
    _create_signals = ("сделай", "создай", "разработай", "подготовь", "оформи")
    _raw_low_guard = raw_input.lower().replace("ё", "е")
    if any(s in _raw_low_guard for s in _list_signals) and not any(s in _raw_low_guard for s in _create_signals):
        return None
    # === END_CANON_LIST_QUERY_GUARD_V1 ===
    if input_type not in ("text", "voice", "search"):
        return None
    if not is_explicit_project_intent(raw_input):
        return None

    try:
        from core.project_engine import create_project_artifact_from_latest_template
        res = create_project_artifact_from_latest_template(raw_input, task_id, topic_id)
    except Exception as e:
        res = {
            "success": False,
            "error": f"PROJECT_ENGINE_EXCEPTION: {e}",
            "project_type": "КЖ",
        }

    msg = _s(res.get("user_message")) or format_project_result_message(res, raw_input)

    if res.get("success") and ("drive.google.com" in msg or "docs.google.com" in msg):
        state = "AWAITING_CONFIRMATION"
        err = ""
        hist = "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:PROJECT_CREATED"
    elif res.get("success"):
        state = "WAITING_CLARIFICATION"
        err = "PROJECT_DRIVE_LINK_NOT_CONFIRMED"
        hist = "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:PROJECT_LOCAL_ONLY"
    else:
        state = "WAITING_CLARIFICATION"
        err = _s(res.get("error")) or "PROJECT_NOT_CREATED"
        hist = "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:PROJECT_NEEDS_CONTEXT"

    return {
        "handled": True,
        "state": state,
        "message": msg,
        "error_message": err,
        "kind": "project_route_guard",
        "history": hist,
    }

# === END_PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1 ===
# === END_PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1 ===

====================================================================================================
END_FILE: core/project_route_guard.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/final_closure_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 805edf5e221a75a4933101941dec6f96cf4f40ec90abae9f4cd478043fb43e07
====================================================================================================
# === FINAL_CLOSURE_BLOCKER_FIX_V1_ENGINE ===
from __future__ import annotations

import json
import re
import sqlite3
from typing import Any, Dict


def _s(v) -> str:
    return "" if v is None else str(v).strip()


def _json(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw or "{}")
    except Exception:
        return {}


def _field(task: Any, key: str, default=None):
    try:
        if hasattr(task, "keys") and key in task.keys():
            return task[key]
    except Exception:
        pass
    try:
        return getattr(task, key)
    except Exception:
        return default


def _row_get(row: Any, key: str, idx: int, default: Any = "") -> Any:
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        if isinstance(row, dict):
            return row.get(key, default)
    except Exception:
        pass
    try:
        return row[idx]
    except Exception:
        return default


def _send_payload(message: str, kind: str, state: str = "DONE", history: str = "") -> Dict[str, Any]:
    return {
        "handled": True,
        "state": state,
        "message": message,
        "kind": kind,
        "history": history or f"FINAL_CLOSURE_BLOCKER_FIX_V1:{kind}",
    }



# === FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V2 ===

# === FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3 ===


# === PROJECT_SAMPLE_SELECTION_P0_V2 ===
def _fc_norm_public(text: Any) -> str:
    s = "" if text is None else str(text)
    s = s.replace("\\\\n", "\n").replace("\\n", "\n").replace("\\\\t", " ").replace("\\t", " ")
    s = s.replace("ё", "е")
    return s.strip()


def _fc_clean_title(name: str) -> str:
    name = _fc_norm_public(name)
    name = re.sub(r"^\s*\d+\.\s*", "", name).strip().strip("\"'«»")
    return name[:180]


def _fc_is_sample_status_request(text: str) -> bool:
    low = _fc_norm_public(text).lower()
    if not any(x in low for x in ("образец", "образцов", "образцы", "шаблон", "шаблона", "эталон", "эталоны", "эталона")):
        return False

    strict_status_or_selection = (
        "взял как образец",
        "взял за образец",
        "ты взял как образец",
        "уже взял как образец",
        "взял их как образец",
        "взял это как образец",
        "принял как образец",
        "принял за образец",
        "ты принял как образец",
        "уже принял как образец",
        "принял их как образец",
        "принял это как образец",
        "используешь как образец",
        "используется как образец",
        "файлы взяты как образец",
        "файлы приняты как образец",
        "взяты как образец",
        "приняты как образец",
        "закрепи как образец",
        "закрепить как образец",
        "закрепляется как",
        "закрепляй как",
        "оставь как образец",
        "сохрани как образец",
        "сохрани как образцы",
        "прими как образец",
        "прими как образцы",
        "прими эти сметы как образцы",
        "прими эти файлы как образцы",
        "принимай как образец",
        "принимай как образцы",
        "принимай эти сметы как образцы",
        "принимай эти файлы как образцы",
        "принимай эти таблицы как образцы",
        "принимай сметы как образцы",
        "принимай файлы как образцы",
        "работай по ним",
        "работай по этим сметам",
        "работай по этим образцам",
        "работать по ним",
        "работать по этим сметам",
        "логика структура",
        "логика и структура",
        "все должно быть синхронизировано",
        "всё должно быть синхронизировано",
        "как эталон",
        "как эталоны",
        "один из образцов",
        "как один из образцов",
    )
    if any(x in low for x in strict_status_or_selection):
        return True

    if any(x in low for x in ("как образец", "как образцы", "как эталон", "как эталоны")) and any(x in low for x in (
        "да ",
        "да,",
        "да.",
        "цоколь",
        "кж",
        "кд",
        "км",
        "кмд",
        "ар",
        "проект",
        "смет",
        "вор",
        "акт",
        "технадзор",
    )):
        return True

    return False


def _fc_extract_titles_from_text(text: str) -> list[str]:
    src = _fc_norm_public(text)
    titles: list[str] = []

    try:
        data = json.loads(src)
        if isinstance(data, dict):
            for key in ("file_name", "name", "title"):
                val = _fc_clean_title(data.get(key) or "")
                if val:
                    titles.append(val)
    except Exception:
        pass

    for m in re.finditer(r'"file_name"\s*:\s*"([^"]+)"', src, re.I):
        val = _fc_clean_title(m.group(1))
        if val:
            titles.append(val)

    for m in re.finditer(r'([А-ЯA-Z0-9Ёё][^\n\r]{0,120}\.(?:pdf|dwg|dxf|xlsx|xls|docx|doc))', src, re.I):
        val = _fc_clean_title(m.group(1))
        if val:
            titles.append(val)

    out: list[str] = []
    seen = set()
    for title in titles:
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(title)
    return out


def _fc_recent_file_rows(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> list[Any]:
    old_rf = conn.row_factory
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, raw_input, result, updated_at
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND (
                COALESCE(raw_input,'') LIKE '%file_name%'
                OR COALESCE(raw_input,'') LIKE '%.pdf%'
                OR COALESCE(raw_input,'') LIKE '%.dwg%'
                OR COALESCE(raw_input,'') LIKE '%.dxf%'
                OR COALESCE(raw_input,'') LIKE '%.xlsx%'
                OR COALESCE(result,'') LIKE '%file_name%'
                OR COALESCE(result,'') LIKE '%.pdf%'
                OR COALESCE(result,'') LIKE '%.dwg%'
                OR COALESCE(result,'') LIKE '%.dxf%'
                OR COALESCE(result,'') LIKE '%.xlsx%'
              )
            ORDER BY updated_at DESC
            LIMIT 80
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()
        return list(rows or [])
    except Exception:
        return []
    finally:
        conn.row_factory = old_rf


def _fc_sample_raw_hay(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> str:
    parts: list[str] = []
    for r in _fc_recent_file_rows(conn, chat_id, topic_id):
        try:
            parts.append(_fc_norm_public(r["raw_input"]))
            parts.append(_fc_norm_public(r["result"]))
        except Exception:
            pass
    return " ".join(parts).lower().replace("ё", "е")


def _fc_sample_titles(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> list[str]:
    titles: list[str] = []
    for r in _fc_recent_file_rows(conn, chat_id, topic_id):
        try:
            titles.extend(_fc_extract_titles_from_text(r["raw_input"]))
            titles.extend(_fc_extract_titles_from_text(r["result"]))
        except Exception:
            continue

    out: list[str] = []
    seen = set()
    for title in titles:
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(title)
    return out[:12]


def _fc_sample_domain_from_hay(hay: str) -> str:
    hay = _fc_norm_public(hay).lower().replace("ё", "е")
    if any(x in hay for x in ("кж", "кд", "кмд", "км", " ар ", "ар ", "проект", "цоколь", ".dwg", ".dxf")):
        return "project"
    if any(x in hay for x in ("смет", "вор", "расцен", "кс-2", "кс2", ".xlsx", ".xls")):
        return "estimate"
    if any(x in hay for x in ("акт", "технадзор", "дефект")):
        return "technadzor"
    return ""


def _fc_select_sample_title(raw_input: str, titles: list[str]) -> str:
    low = _fc_norm_public(raw_input).lower()
    for title in titles:
        tlow = title.lower()
        words = [w for w in re.split(r"[\s._\-]+", tlow) if len(w) >= 3]
        if any(w in low for w in words):
            return title
    if len(titles) == 1:
        return titles[0]
    if "цоколь" in low:
        for title in titles:
            if "цоколь" in title.lower():
                return title
    return ""


def _fc_write_sample_memory(chat_id: str, topic_id: int, domain: str, title: str, raw_input: str) -> None:
    try:
        import datetime
        mem = sqlite3.connect("/root/.areal-neva-core/data/memory.db")
        try:
            payload = json.dumps(
                {
                    "engine": "PROJECT_SAMPLE_SELECTION_P0_V2",
                    "chat_id": str(chat_id),
                    "topic_id": int(topic_id or 0),
                    "domain": domain,
                    "title": title,
                    "raw_input": raw_input,
                    "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                },
                ensure_ascii=False,
            )
            mem.execute(
                "INSERT INTO memory(chat_id,key,value,timestamp) VALUES (?,?,?,?)",
                (
                    str(chat_id),
                    f"topic_{int(topic_id or 0)}_{domain or 'sample'}_selected_sample",
                    payload,
                    datetime.datetime.utcnow().isoformat() + "Z",
                ),
            )
            mem.commit()
        finally:
            mem.close()
    except Exception:
        pass


def _handle_sample_status(conn: sqlite3.Connection, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    if not _fc_is_sample_status_request(raw_input):
        return {"handled": False}

    titles = _fc_sample_titles(conn, chat_id, topic_id)
    raw_hay = _fc_sample_raw_hay(conn, chat_id, topic_id)
    selected_title = _fc_select_sample_title(raw_input, titles)
    domain = _fc_sample_domain_from_hay(" ".join([raw_input, selected_title, " ".join(titles), raw_hay]))

    if domain == "project":
        if selected_title:
            msg = f"{selected_title} закреплён как образец проектирования"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец проектирования"
    elif domain == "estimate":
        if selected_title:
            msg = f"{selected_title} закреплён как образец сметы"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец сметы"
    elif domain == "technadzor":
        if selected_title:
            msg = f"{selected_title} закреплён как образец для технадзора"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец для технадзора"
    else:
        if selected_title:
            msg = f"{selected_title} закреплён как образец"
        else:
            msg = "Файлы в этом топике уже взяты в работу как образец"

    _fc_write_sample_memory(str(chat_id), int(topic_id or 0), domain or "sample", selected_title, raw_input)

    return _send_payload(
        msg,
        "project_sample_selection",
        "DONE",
        "PROJECT_SAMPLE_SELECTION_P0_V2:ANSWERED",
    )
# === END_PROJECT_SAMPLE_SELECTION_P0_V2 ===



def _handle_memory_query(conn: sqlite3.Connection, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    # === CANON_SEARCH_TOPIC_500_GUARD_V1 ===
    if int(topic_id or 0) == 500:
        return {"handled": False}
    # === END_CANON_SEARCH_TOPIC_500_GUARD_V1 ===
    t = raw_input.lower().replace("ё", "е")

    trigger = False
    try:
        from core.file_memory_bridge import should_handle_file_followup
        trigger = bool(should_handle_file_followup(raw_input))
    except Exception:
        trigger = False

    if not trigger:
        trigger = any(x in t for x in [
            "что скидывал",
            "что я скидывал",
            "что отправлял",
            "что загружал",
            "какие файлы",
            "какой файл",
            "проектные файлы",
            "файлы проекта",
            "файлы в чате",
            "документы в чате",
            "последний файл",
            "скидывал",
            "загружал",
        ])

    if not trigger:
        return {"handled": False}

    try:
        from core.file_memory_bridge import build_file_followup_answer
        answer = build_file_followup_answer(str(chat_id), int(topic_id or 0), raw_input, limit=3)
    except Exception:
        answer = ""

    if not answer:
        answer = "В этом топике релевантных файлов по запросу не найдено"

    try:
        from core.output_sanitizer import sanitize_user_output
        answer = sanitize_user_output(answer, fallback="Файлы найдены")
    except Exception:
        pass

    return _send_payload(
        answer,
        "memory_query",
        "DONE",
        "FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3:LISTED",
    )

# === END_FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3 ===


def _handle_runtime_file(conn: sqlite3.Connection, task: Any, task_id: str, chat_id: str, topic_id: int, raw_input: str, input_type: str) -> Dict[str, Any]:
    if input_type not in ("drive_file", "file"):
        return {"handled": False}

    data = _json(raw_input)
    file_id = _s(data.get("file_id"))
    file_name = _s(data.get("file_name") or data.get("name"))
    mime = _s(data.get("mime_type"))
    source = _s(data.get("source") or "telegram")
    size = int(data.get("size") or data.get("file_size") or 0)
    drive_link = _s(data.get("drive_link") or data.get("webViewLink"))

    from core.runtime_file_catalog import duplicate_user_message, register_file

    res = register_file(
        chat_id,
        topic_id,
        task_id,
        file_id=file_id,
        file_name=file_name,
        mime_type=mime,
        size=size,
        source=source,
        drive_link=drive_link,
    )

    if res.get("duplicate"):
        return _send_payload(
            duplicate_user_message(file_name or "UNKNOWN", res.get("duplicate_record") or {}),
            "runtime_duplicate_file",
            "WAITING_CLARIFICATION",
            "FINAL_CLOSURE_BLOCKER_FIX_V1:RUNTIME_DUPLICATE_FILE",
        )

    return {"handled": False, "catalog_registered": True}


def _handle_technadzor(raw_input: str, task_id: str, chat_id: str, topic_id: int) -> Dict[str, Any]:
    from core.technadzor_engine import is_technadzor_intent, process_technadzor

    if not is_technadzor_intent(raw_input):
        return {"handled": False}

    return process_technadzor(text=raw_input, task_id=task_id, chat_id=chat_id, topic_id=topic_id)


def _handle_ocr(raw_input: str, task_id: str) -> Dict[str, Any]:
    from core.ocr_engine import is_ocr_table_intent, process_ocr_table

    if not is_ocr_table_intent(raw_input):
        return {"handled": False}

    return process_ocr_table(text=raw_input, task_id=task_id)


def _handle_archive_guard(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    if not any(x in raw_input.lower() for x in ["архив", "сохрани", "запомни"]):
        return {"handled": False}

    from core.archive_guard import should_archive

    res = should_archive(conn, task_id, chat_id, topic_id, raw_input)
    if res.get("duplicate"):
        return _send_payload(
            "В архив не дублирую: такая запись уже есть",
            "archive_duplicate",
            "DONE",
            "FINAL_CLOSURE_BLOCKER_FIX_V1:ARCHIVE_DUPLICATE_BLOCKED",
        )

    return {"handled": False, "archive_guard_ok": True}



# === PROJECT_INDEX_QUERY_DETECTOR_V1 ===
_INDEX_QUERY_RE_V1 = re.compile(
    r"(какие|покажи|перечисли|что у тебя|есть ли|список|что есть|какие файлы|какие образцы|покажи образцы|что за образцы|какие разделы)",
    re.I,
)

_TOPIC_ROLE_MAP_V1 = {
    2: "СМЕТЫ / СТРОЙКА",
    5: "ТЕХНАДЗОР / АКТЫ / ДЕФЕКТЫ",
    210: "ПРОЕКТИРОВАНИЕ / АР / КЖ / КД / КР / КМ / ОВ / ВК / ЭО",
}

def _fc_topic_role_v1(topic_id: int) -> str:
    return _TOPIC_ROLE_MAP_V1.get(int(topic_id or 0), "ОБЩИЙ")

def _fc_is_index_query_v1(text: str) -> bool:
    low = _fc_norm_public(text).lower()
    if not _INDEX_QUERY_RE_V1.search(low):
        return False
    return any(x in low for x in (
        "образц", "файл", "раздел", "ар", "кж", "кд", "кр", "км", "кмд",
        "ов", "вк", "эо", "эскиз", "проект", "смет", "акт", "технадзор"
    ))

def _fc_is_negative_topic_correction_v1(text: str) -> bool:
    low = _fc_norm_public(text).lower()
    return any(x in low for x in (
        "нет я не это спросил",
        "не это спросил",
        "не то спросил",
        "не так",
        "ты не понял",
        "не про это",
    ))

def _fc_load_owner_reference_registry_v1() -> dict:
    try:
        from pathlib import Path
        return json.loads(Path("/root/.areal-neva-core/config/owner_reference_registry.json").read_text(encoding="utf-8"))
    except Exception:
        return {}

def _fc_topic_domain_v1(topic_id: int) -> str:
    topic_id = int(topic_id or 0)
    if topic_id == 2:
        return "estimate"
    if topic_id == 5:
        return "technadzor"
    if topic_id == 210:
        return "design"
    return ""

def _fc_index_items_for_topic_v1(topic_id: int) -> list[dict]:
    data = _fc_load_owner_reference_registry_v1()
    policy = data.get("owner_reference_full_workflow_v1") if isinstance(data, dict) else {}
    if not isinstance(policy, dict):
        return []
    domain = _fc_topic_domain_v1(topic_id)
    if domain == "estimate":
        return list(policy.get("estimate_references") or [])
    if domain == "technadzor":
        return list(policy.get("technadzor_references") or [])
    if domain == "design":
        return list(policy.get("design_references") or [])
    return (
        list(policy.get("estimate_references") or [])
        + list(policy.get("design_references") or [])
        + list(policy.get("technadzor_references") or [])
    )

def _fc_filter_design_by_question_v1(items: list[dict], raw_input: str) -> list[dict]:
    low = _fc_norm_public(raw_input).lower()
    wanted = []
    mapping = {
        "ар": ("AR", "АР"),
        "кж": ("KJ", "КЖ"),
        "кд": ("KD", "КД"),
        "кр": ("KR", "КР"),
        "кмд": ("KMD", "КМД"),
        "км": ("KM", "КМ"),
        "ов": ("OV", "ОВ"),
        "вк": ("VK", "ВК"),
        "эо": ("EO", "ЭО"),
        "эм": ("EO", "ЭМ"),
        "эос": ("EO", "ЭОС"),
        "эскиз": ("SKETCH", "ЭСКИЗ"),
        "план участка": ("GP", "ГП"),
    }
    for k, vals in mapping.items():
        if k in low:
            wanted.extend(vals)
    if not wanted:
        return items
    out = []
    for x in items:
        d = str(x.get("discipline") or "").upper()
        name = str(x.get("name") or "").upper()
        if any(w.upper() in d or w.upper() in name for w in wanted):
            out.append(x)
    return out or items

def _fc_format_index_answer_v1(topic_id: int, raw_input: str) -> str:
    role = _fc_topic_role_v1(topic_id)
    items = _fc_index_items_for_topic_v1(topic_id)
    if int(topic_id or 0) == 210:
        items = _fc_filter_design_by_question_v1(items, raw_input)

    if not items:
        return f"По роли {role} образцы в индексе не найдены"

    groups: dict[str, list[str]] = {}
    for x in items:
        if not isinstance(x, dict):
            continue
        if int(topic_id or 0) == 210:
            key = str(x.get("discipline") or "DESIGN")
        elif int(topic_id or 0) == 2:
            key = str(x.get("role") or "estimate")
        elif int(topic_id or 0) == 5:
            key = "technadzor"
        else:
            key = str(x.get("domain") or x.get("discipline") or x.get("role") or "reference")
        name = _fc_clean_title(str(x.get("name") or ""))
        if not name:
            continue
        groups.setdefault(key, [])
        if name not in groups[key]:
            groups[key].append(name)

    lines = [f"Образцы по текущему топику: {role}", ""]
    for key in sorted(groups):
        vals = groups[key][:20]
        lines.append(f"{key}:")
        for name in vals:
            lines.append(f"- {name}")
        if len(groups[key]) > len(vals):
            lines.append(f"- ещё {len(groups[key]) - len(vals)}")
        lines.append("")
    lines.append("Файл не создаю. Это ответ на запрос списка образцов")
    return "\n".join(lines).strip()

def _handle_project_index_query_v1(conn: sqlite3.Connection, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    # === CANON_SEARCH_TOPIC_500_GUARD_V1 ===
    if int(topic_id or 0) == 500:
        return {"handled": False}
    # === END_CANON_SEARCH_TOPIC_500_GUARD_V1 ===
    if not _fc_is_index_query_v1(raw_input):
        return {"handled": False}
    answer = _fc_format_index_answer_v1(int(topic_id or 0), raw_input)
    return _send_payload(
        answer,
        "project_index_query",
        "DONE",
        "PROJECT_INDEX_QUERY_DETECTOR_V1:ANSWERED",
    )

def _handle_topic_context_isolation_guard_v1(conn: sqlite3.Connection, chat_id: str, topic_id: int, raw_input: str) -> Dict[str, Any]:
    if not _fc_is_negative_topic_correction_v1(raw_input):
        return {"handled": False}
    role = _fc_topic_role_v1(int(topic_id or 0))
    if int(topic_id or 0) == 210:
        msg = "Понял. Остаёмся в проектировании. Уточни, что показать: АР / КЖ / КД / КР / КМ / ОВ / ВК / ЭО / эскизы / планы участка"
    elif int(topic_id or 0) == 2:
        msg = "Понял. Остаёмся в сметах и стройке. Уточни, что нужно: цены / смета / материалы / логистика / XLSX"
    elif int(topic_id or 0) == 5:
        msg = "Понял. Остаёмся в технадзоре. Уточни, что нужно: акт / дефект / фото / исполнительная / норма"
    else:
        msg = f"Понял. Роль текущего топика: {role}. Уточни одним сообщением, что именно нужно"
    return _send_payload(
        msg,
        "topic_context_isolation_guard",
        "WAITING_CLARIFICATION",
        "TOPIC_CONTEXT_ISOLATION_GUARD_V1:ANSWERED",
    )

# === END_PROJECT_INDEX_QUERY_DETECTOR_V1 ===

def maybe_handle_final_closure(
    conn: sqlite3.Connection,
    task: Any,
    task_id: str,
    chat_id: str,
    topic_id: int,
    raw_input: str,
    input_type: str = "text",
    reply_to=None,
) -> Dict[str, Any]:
    raw_input = _s(raw_input)
    input_type = _s(input_type or _field(task, "input_type", "text"))
    chat_id = _s(chat_id or _field(task, "chat_id", ""))
    topic_id = int(topic_id or _field(task, "topic_id", 0) or 0)

    r = _handle_runtime_file(conn, task, task_id, chat_id, topic_id, raw_input, input_type)
    if r.get("handled"):
        return r

    r = _handle_project_index_query_v1(conn, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    r = _handle_topic_context_isolation_guard_v1(conn, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    r = _handle_sample_status(conn, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    r = _handle_memory_query(conn, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    r = _handle_technadzor(raw_input, task_id, chat_id, topic_id)
    if r.get("handled"):
        return r

    r = _handle_ocr(raw_input, task_id)
    if r.get("handled"):
        return r

    r = _handle_archive_guard(conn, task_id, chat_id, topic_id, raw_input)
    if r.get("handled"):
        return r

    return {"handled": False}


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_ENGINE ===

====================================================================================================
END_FILE: core/final_closure_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/file_context_intake.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5de5c8de555365e8ea67135829d9ae00b20434d292b1fa9bdc61db52b28bdaea
====================================================================================================
# === FILE_CONTEXT_INTAKE_FULL_CLOSE_V1 ===
from __future__ import annotations

import json
import os
import re
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional

BASE = Path("/root/.areal-neva-core")
CORE_DB = BASE / "data" / "core.db"
MEM_DB = BASE / "data" / "memory.db"
TEMPLATE_ROOT = BASE / "data" / "templates"
ESTIMATE_TEMPLATE_DIR = TEMPLATE_ROOT / "estimate"
ESTIMATE_BATCH_DIR = TEMPLATE_ROOT / "estimate_batch"
FILE_CATALOG_DIR = BASE / "data" / "telegram_file_catalog"

ESTIMATE_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
ESTIMATE_BATCH_DIR.mkdir(parents=True, exist_ok=True)
FILE_CATALOG_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _task_field(task: Any, field: str, default: Any = "") -> Any:
    try:
        if hasattr(task, "keys") and field in task.keys():
            return task[field]
    except Exception:
        pass
    if isinstance(task, dict):
        return task.get(field, default)
    try:
        return getattr(task, field)
    except Exception:
        return default


def _json(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    txt = _s(raw)
    if not txt:
        return {}
    try:
        obj = json.loads(txt)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _safe_name(v: Any, limit: int = 120) -> str:
    s = re.sub(r"[^0-9A-Za-zА-Яа-я_. -]+", "_", _s(v)).strip(" ._")
    return (s or "file")[:limit]


def _safe_key(v: Any, limit: int = 80) -> str:
    return re.sub(r"[^0-9A-Za-z_-]+", "_", _s(v))[:limit] or "unknown"


def _cols(conn: sqlite3.Connection, table: str):
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except Exception:
        return []


def _memory_write(chat_id: str, key: str, value: Any) -> None:
    try:
        if not MEM_DB.exists():
            return
        conn = sqlite3.connect(str(MEM_DB))
        try:
            cols = _cols(conn, "memory")
            if not cols:
                return
            payload = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
            ts = _now()
            if "id" in cols:
                mid = hashlib.sha1(f"{chat_id}:{key}:{ts}:{payload[:80]}".encode("utf-8")).hexdigest()
                conn.execute(
                    "INSERT OR IGNORE INTO memory (id,chat_id,key,value,timestamp) VALUES (?,?,?,?,?)",
                    (mid, str(chat_id), str(key), payload, ts),
                )
            else:
                conn.execute(
                    "INSERT INTO memory (chat_id,key,value,timestamp) VALUES (?,?,?,?)",
                    (str(chat_id), str(key), payload, ts),
                )
            conn.commit()
        finally:
            conn.close()
    except Exception:
        return


def _memory_latest(chat_id: str, key: str) -> str:
    try:
        if not MEM_DB.exists():
            return ""
        conn = sqlite3.connect(str(MEM_DB))
        try:
            row = conn.execute(
                "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY rowid DESC LIMIT 1",
                (str(chat_id), str(key)),
            ).fetchone()
            return row[0] if row else ""
        finally:
            conn.close()
    except Exception:
        return ""


def _extract_user_text(raw_input: Any) -> str:
    obj = _json(raw_input)
    if obj:
        for k in ("caption", "user_text", "text", "prompt", "comment", "message"):
            v = obj.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return ""
    return _s(raw_input)


def _file_payload(raw_input: Any) -> Dict[str, Any]:
    obj = _json(raw_input)
    return {
        "file_id": _s(obj.get("file_id")),
        "file_name": _s(obj.get("file_name")),
        "mime_type": _s(obj.get("mime_type")),
        "caption": _s(obj.get("caption")),
        "source": _s(obj.get("source")),
        "telegram_message_id": obj.get("telegram_message_id"),
        "raw": obj,
    }


def _is_service_file(payload: Dict[str, Any]) -> bool:
    src = _low(payload.get("source"))
    name = _low(payload.get("file_name"))
    if src in {"google_drive", "drive", "drive_sync", "healthcheck", "service"}:
        return True
    if any(x in name for x in ("healthcheck", "service_file", ".tmp", "tmp_", "retry_probe")):
        return True
    return False


def _detect_pending_file_intent(text: str) -> Optional[Dict[str, Any]]:
    low = _low(text)
    if not low:
        return None

    future_file = any(x in low for x in (
        "сейчас скину", "сейчас пришлю", "скину несколько", "пришлю несколько",
        "буду скидывать", "сейчас отправлю", "отправлю несколько", "загружу несколько",
        "скину файлы", "пришлю файлы"
    ))

    estimate = any(x in low for x in ("смет", "кс-2", "кс2", "ведомост", "спецификац", "расцен", "excel", "xlsx"))
    template = any(x in low for x in ("образец", "образцы", "шаблон", "шаблоны", "принять", "возьми", "сохрани"))
    price_web = any(x in low for x in (
        "цены из интернета", "цена из интернета", "актуальные цены", "стоимость материалов",
        "цены материалов", "искать в интернете", "брать из интернета", "найти цены",
        "проводить поиск", "проверить цены"
    ))

    if future_file and estimate:
        return {
            "kind": "estimate",
            "mode": "template_batch" if template or "образ" in low else "pending_estimate_files",
            "price_mode": "web_confirm" if price_web else "",
            "raw_text": text,
            "created_at": _now(),
            "ttl_sec": 7200,
        }

    if estimate and template and any(x in low for x in ("несколько", "файлы", "сметы")):
        return {
            "kind": "estimate",
            "mode": "template_batch",
            "price_mode": "web_confirm" if price_web else "",
            "raw_text": text,
            "created_at": _now(),
            "ttl_sec": 7200,
        }

    return None


def _save_pending_intent(chat_id: str, topic_id: int, intent: Dict[str, Any]) -> None:
    key = f"topic_{int(topic_id or 0)}_pending_file_intent"
    _memory_write(chat_id, key, intent)
    if intent.get("price_mode"):
        _memory_write(chat_id, f"topic_{int(topic_id or 0)}_price_mode", intent.get("price_mode"))


def latest_pending_instruction_for_topic(topic_id: int, chat_id: str = "") -> str:
    chat_ids = [str(chat_id)] if chat_id else []
    if not chat_ids:
        try:
            conn = sqlite3.connect(str(MEM_DB))
            rows = conn.execute(
                "SELECT DISTINCT chat_id FROM memory WHERE key=? ORDER BY rowid DESC LIMIT 5",
                (f"topic_{int(topic_id or 0)}_pending_file_intent",),
            ).fetchall()
            conn.close()
            chat_ids = [r[0] for r in rows]
        except Exception:
            chat_ids = []
    for cid in chat_ids:
        raw = _memory_latest(cid, f"topic_{int(topic_id or 0)}_pending_file_intent")
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            data = {}
        if data.get("raw_text"):
            return str(data["raw_text"])
    return ""


def _current_rowid(conn: sqlite3.Connection, task_id: str) -> int:
    try:
        row = conn.execute("SELECT rowid FROM tasks WHERE id=? LIMIT 1", (task_id,)).fetchone()
        return int(row[0]) if row else 0
    except Exception:
        return 0


def _find_duplicate(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    rowid = _current_rowid(conn, task_id)
    file_id = _s(payload.get("file_id"))
    file_name = _s(payload.get("file_name"))
    if not file_id and not file_name:
        return None

    params = [str(chat_id), int(topic_id or 0), int(rowid or 10**18)]
    where = "chat_id=? AND COALESCE(topic_id,0)=? AND input_type='drive_file' AND rowid<?"

    if file_id:
        where += " AND json_extract(raw_input,'$.file_id')=?"
        params.append(file_id)
    elif file_name:
        where += " AND lower(json_extract(raw_input,'$.file_name'))=lower(?)"
        params.append(file_name)

    try:
        row = conn.execute(
            f"""
            SELECT rowid,id,state,raw_input,result,error_message,created_at,updated_at
            FROM tasks
            WHERE {where}
            ORDER BY rowid DESC
            LIMIT 1
            """,
            params,
        ).fetchone()
    except Exception:
        row = None

    if not row:
        return None

    old_payload = _json(row["raw_input"] if hasattr(row, "keys") else row[3])
    old_name = old_payload.get("file_name") or file_name
    return {
        "rowid": row["rowid"] if hasattr(row, "keys") else row[0],
        "task_id": row["id"] if hasattr(row, "keys") else row[1],
        "state": row["state"] if hasattr(row, "keys") else row[2],
        "file_name": old_name,
        "file_id": old_payload.get("file_id") or file_id,
        "created_at": row["created_at"] if hasattr(row, "keys") else row[6],
        "updated_at": row["updated_at"] if hasattr(row, "keys") else row[7],
    }


def _duplicate_message(payload: Dict[str, Any], dup: Dict[str, Any]) -> str:
    name = payload.get("file_name") or dup.get("file_name") or "файл"
    return (
        "Смотри, этот файл ты уже скидывал\n"
        f"Файл: {name}\n"
        f"Первая найденная задача: {str(dup.get('task_id') or '')[:8]}\n"
        f"Дата: {dup.get('created_at') or dup.get('updated_at') or 'UNKNOWN'}\n\n"
        "Что сделать с ним сейчас?\n"
        "1. Обновить образец\n"
        "2. Обработать заново\n"
        "3. Сравнить версии\n"
        "4. Игнорировать дубль"
    )


def _catalog_path(chat_id: str, topic_id: int) -> Path:
    return FILE_CATALOG_DIR / f"chat_{_safe_key(chat_id)}__topic_{int(topic_id or 0)}.jsonl"


def _index_telegram_file(chat_id: str, topic_id: int, task_id: str, payload: Dict[str, Any]) -> None:
    if not payload.get("file_id") and not payload.get("file_name"):
        return
    entry = {
        "created_at": _now(),
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "task_id": str(task_id),
        "file_id": payload.get("file_id"),
        "file_name": payload.get("file_name"),
        "mime_type": payload.get("mime_type"),
        "telegram_message_id": payload.get("telegram_message_id"),
        "source": payload.get("source") or "telegram",
    }
    path = _catalog_path(chat_id, topic_id)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_telegram_file_index", entry)


def _template_paths(chat_id: str, topic_id: int, file_name: str):
    safe_chat = _safe_key(chat_id)
    safe_file = _safe_key(file_name, 70)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    active = ESTIMATE_TEMPLATE_DIR / f"ACTIVE__chat_{safe_chat}__topic_{int(topic_id or 0)}.json"
    snap = ESTIMATE_TEMPLATE_DIR / f"TEMPLATE__chat_{safe_chat}__topic_{int(topic_id or 0)}__{stamp}__{safe_file}.json"
    batch = ESTIMATE_BATCH_DIR / f"ACTIVE_BATCH__chat_{safe_chat}__topic_{int(topic_id or 0)}.json"
    return active, snap, batch


def _save_estimate_template(chat_id: str, topic_id: int, task_id: str, payload: Dict[str, Any], raw_instruction: str) -> Dict[str, Any]:
    active, snap, batch_path = _template_paths(chat_id, topic_id, payload.get("file_name") or "estimate")
    template = {
        "engine": "MULTI_FILE_TEMPLATE_INTAKE_V1",
        "kind": "estimate",
        "status": "active",
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "saved_by_task_id": str(task_id),
        "source_task_id": str(task_id),
        "source_file_id": payload.get("file_id") or "",
        "source_file_name": payload.get("file_name") or "",
        "source_mime_type": payload.get("mime_type") or "",
        "source_caption": payload.get("caption") or "",
        "telegram_message_id": payload.get("telegram_message_id"),
        "saved_at": _now(),
        "usage_rule": "Use this Telegram file as estimate sample/template in the same chat and topic",
        "raw_user_instruction": raw_instruction,
    }

    active.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    snap.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")

    batch = []
    if batch_path.exists():
        try:
            old = json.loads(batch_path.read_text(encoding="utf-8"))
            if isinstance(old, list):
                batch = old
            elif isinstance(old, dict) and isinstance(old.get("templates"), list):
                batch = old["templates"]
        except Exception:
            batch = []

    seen = {str(x.get("source_file_id") or x.get("source_file_name")) for x in batch if isinstance(x, dict)}
    key = str(template.get("source_file_id") or template.get("source_file_name"))
    if key not in seen:
        batch.append(template)

    batch_payload = {
        "engine": "MULTI_FILE_TEMPLATE_INTAKE_V1",
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "count": len(batch),
        "updated_at": _now(),
        "templates": batch[-100:],
    }
    batch_path.write_text(json.dumps(batch_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_estimate_active_template", template)
    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_estimate_template_batch", batch_payload)

    return {"template": template, "batch_count": len(batch), "active_path": str(active), "snapshot_path": str(snap), "batch_path": str(batch_path)}


def _load_pending_intent(chat_id: str, topic_id: int) -> Dict[str, Any]:
    raw = _memory_latest(chat_id, f"topic_{int(topic_id or 0)}_pending_file_intent")
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _pending_is_template_batch(intent: Dict[str, Any]) -> bool:
    if not intent:
        return False
    if intent.get("kind") != "estimate":
        return False
    return intent.get("mode") in {"template_batch", "pending_estimate_files"}


def prehandle_task_context_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))
    reply_to = _task_field(task, "reply_to_message_id", None)

    if not task_id or not chat_id:
        return None

    if input_type in ("text", "voice"):
        text = _extract_user_text(raw_input)
        pending = _detect_pending_file_intent(text)
        if pending:
            _save_pending_intent(chat_id, topic_id, pending)
            msg = (
                "Принял\n"
                "Следующие файлы в этом топике приму как образцы сметы\n"
                "Если файл уже был в Telegram — скажу что он дублируется и спрошу что делать\n"
                "При создании сметы цены материалов буду искать в интернете и сначала покажу варианты для выбора"
            )
            return {
                "handled": True,
                "state": "DONE",
                "kind": "context_aware_file_intake",
                "message": msg,
                "history": "CONTEXT_AWARE_FILE_INTAKE_V1:PENDING_TEMPLATE_BATCH_SAVED",
            }

    if input_type in ("drive_file", "file"):
        payload = _file_payload(raw_input)
        if _is_service_file(payload):
            return None

        _index_telegram_file(chat_id, topic_id, task_id, payload)

        dup = _find_duplicate(conn, task_id, chat_id, topic_id, payload)
        if dup:
            msg = _duplicate_message(payload, dup)
            _memory_write(chat_id, f"topic_{topic_id}_last_duplicate_file", {"current_task_id": task_id, "payload": payload, "duplicate": dup})
            return {
                "handled": True,
                "state": "WAITING_CLARIFICATION",
                "kind": "duplicate_file_question",
                "message": msg,
                "history": "TELEGRAM_FILE_MEMORY_INDEX_V1:DUPLICATE_FOUND",
            }

        pending = _load_pending_intent(chat_id, topic_id)
        if _pending_is_template_batch(pending):
            saved = _save_estimate_template(chat_id, topic_id, task_id, payload, pending.get("raw_text") or "")
            file_name = payload.get("file_name") or "файл"
            msg = (
                "Образец сметы принят\n"
                f"Файл: {file_name}\n"
                f"Всего образцов в наборе: {saved.get('batch_count')}\n\n"
                "Дальше можешь присылать следующие сметы-образцы или написать: сделай смету\n"
                "Если нужно брать цены из интернета — я сначала покажу найденные варианты и спрошу какие поставить"
            )
            return {
                "handled": True,
                "state": "DONE",
                "kind": "multi_file_template_intake",
                "message": msg,
                "history": "MULTI_FILE_TEMPLATE_INTAKE_V1:TEMPLATE_SAVED",
            }

    return None


def router_pending_instruction(raw_input: str, topic_id: int, chat_id: str = "") -> str:
    explicit = _extract_user_text(raw_input)
    if explicit:
        return explicit
    return latest_pending_instruction_for_topic(topic_id, chat_id)


# === END_FILE_CONTEXT_INTAKE_FULL_CLOSE_V1 ===


# === PENDING_INTENT_CLARIFICATION_V1 ===
try:
    _pic_orig_prehandle_task_context_v1 = prehandle_task_context_v1
except Exception:
    _pic_orig_prehandle_task_context_v1 = None


def _pic_has_active_pending_intent(chat_id: str, topic_id: int) -> Dict[str, Any]:
    try:
        data = _load_pending_intent(chat_id, topic_id)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _pic_is_clarification_text(text: str) -> bool:
    low = _low(text)
    if not low:
        return False

    explicit_new_task = any(x in low for x in (
        "сделай проект", "создай проект", "разработай проект",
        "сделай смету", "создай смету", "посчитай смету", "рассчитай смету",
        "сделай акт", "создай акт", "найди мне", "поищи мне"
    ))
    if explicit_new_task:
        return False

    clar_words = (
        "ты должен", "ты должна", "должен", "должна", "надо", "нужно",
        "нужно ли", "надо ли", "спроси", "спросить", "уточни", "уточнить",
        "не сразу", "сначала", "перед тем", "до того", "после этого",
        "цены", "интернет", "искать", "не искать", "без интернета",
        "актуальные", "поставить", "подставить", "согласовать",
        "подтвердить", "не создавай сразу", "сначала спросить",
        "сначала спроси", "спросить нужно ли", "спроси нужно ли"
    )
    return any(x in low for x in clar_words)


def _pic_update_intent_with_clarification(intent: Dict[str, Any], text: str) -> Dict[str, Any]:
    low = _low(text)
    updated = dict(intent or {})

    clarifications = updated.get("clarifications")
    if not isinstance(clarifications, list):
        clarifications = []
    clarifications.append({"text": text, "created_at": _now()})
    updated["clarifications"] = clarifications[-20:]
    updated["updated_at"] = _now()
    updated["last_clarification"] = text

    ask_before_web = any(x in low for x in (
        "не сразу", "сначала спрос", "спросить нужно ли", "спроси нужно ли",
        "нужно ли", "надо ли", "перед тем как искать", "перед поиском",
        "сначала уточни", "не ищи сразу", "не надо сразу",
        "согласовать цены", "подтвердить цены"
    ))

    disable_web = any(x in low for x in (
        "не искать в интернете", "без интернета", "не надо интернет",
        "цены не ищи", "не ищи цены", "без поиска цен"
    ))

    force_web = any(x in low for x in (
        "ищи в интернете", "искать в интернете", "цены из интернета",
        "актуальные цены", "проверить цены", "найти цены"
    ))

    if disable_web:
        updated["price_mode"] = "manual_or_template"
        updated["web_search_disabled"] = True
        updated["ask_before_web_search"] = False
        updated["price_confirmation_required"] = False
    elif ask_before_web:
        updated["price_mode"] = "ask_before_search"
        updated["ask_before_web_search"] = True
        updated["price_confirmation_required"] = True
        updated["web_search_disabled"] = False
    elif force_web:
        updated["price_mode"] = "web_confirm"
        updated["ask_before_web_search"] = False
        updated["price_confirmation_required"] = True
        updated["web_search_disabled"] = False

    original = str(updated.get("raw_text") or "").strip()
    if text and text not in original:
        updated["raw_text"] = (original + "\nУточнение: " + text).strip()

    return updated


def _pic_confirmation_message(intent: Dict[str, Any]) -> str:
    price_mode = str(intent.get("price_mode") or "")
    if price_mode == "ask_before_search":
        price_line = "Перед поиском цен в интернете сначала спрошу, нужно ли искать актуальные цены"
    elif price_mode == "web_confirm":
        price_line = "Цены материалов буду искать в интернете, затем покажу варианты и спрошу какие поставить"
    elif price_mode == "manual_or_template":
        price_line = "Интернет-цены не ищу, пока ты отдельно не скажешь искать"
    else:
        price_line = "Цены не подставляю без отдельного подтверждения"

    return (
        "Уточнение к приёму смет принято\n"
        "Следующие файлы в этом топике остаются образцами сметы\n"
        f"{price_line}\n"
        "Финальную смету не создаю без твоего выбора цен"
    )



# === PROJECT_SAMPLE_TEXT_INTAKE_V1 ===
def _pst_is_sample_text(text: str) -> bool:
    low = _low(text)
    if not low:
        return False
    if not any(x in low for x in ("возьми", "прими", "используй", "сохрани")):
        return False
    return any(x in low for x in ("образец", "шаблон", "пример", "как образец"))


def _pst_is_projectish(payload: Dict[str, Any], text: str = "") -> bool:
    hay = _low(" ".join([
        payload.get("file_name") or "",
        payload.get("caption") or "",
        payload.get("mime_type") or "",
        text or "",
    ]))
    return any(x in hay for x in (
        "кж", "км", "кмд", "ар", "проект", "чертеж", "чертёж",
        "конструкц", "цоколь", "плита", ".dxf", ".dwg", ".pdf"
    )) and not any(x in hay for x in (
        "смет", "вор", "расцен", "стоимост", "технадзор", "акт дефект", "нарушен"
    ))


def _pst_latest_project_file(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Dict[str, Any]:
    try:
        rows = conn.execute(
            """
            SELECT id,raw_input,result,updated_at,rowid
            FROM tasks
            WHERE CAST(chat_id AS TEXT)=CAST(? AS TEXT)
              AND COALESCE(topic_id,0)=?
              AND input_type IN ('drive_file','file')
            ORDER BY rowid DESC
            LIMIT 80
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()
    except Exception:
        rows = []

    for r in rows:
        try:
            raw = r["raw_input"] if hasattr(r, "keys") else r[1]
            tid = r["id"] if hasattr(r, "keys") else r[0]
            upd = r["updated_at"] if hasattr(r, "keys") else r[3]
        except Exception:
            continue

        payload = _file_payload(raw)
        if _is_service_file(payload):
            continue
        if _pst_is_projectish(payload, raw):
            return {
                "task_id": str(tid),
                "file_id": payload.get("file_id") or "",
                "file_name": payload.get("file_name") or "",
                "mime_type": payload.get("mime_type") or "",
                "caption": payload.get("caption") or "",
                "source": payload.get("source") or "",
                "updated_at": str(upd or ""),
            }

    return {}


def _pst_save_project_sample(chat_id: str, topic_id: int, task_id: str, sample: Dict[str, Any], text: str) -> None:
    payload = {
        "engine": "PROJECT_SAMPLE_TEXT_INTAKE_V1",
        "kind": "project",
        "status": "active",
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "saved_by_task_id": str(task_id),
        "source_task_id": sample.get("task_id") or "",
        "source_file_id": sample.get("file_id") or "",
        "source_file_name": sample.get("file_name") or "",
        "source_mime_type": sample.get("mime_type") or "",
        "source_caption": sample.get("caption") or "",
        "saved_at": _now(),
        "usage_rule": "Use this file as project/design sample only inside the same chat and topic",
        "raw_user_instruction": text,
    }
    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_project_active_template", payload)
    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_project_sample_file", payload)


def _pst_try_project_sample_text(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, text: str) -> Optional[Dict[str, Any]]:
    if not _pst_is_sample_text(text):
        return None

    sample = _pst_latest_project_file(conn, chat_id, topic_id)
    if not sample:
        return None

    _pst_save_project_sample(chat_id, topic_id, task_id, sample, text)

    file_name = sample.get("file_name") or "файл"
    msg = (
        "Образец проектирования принят\n"
        f"Файл: {file_name}\n"
        "Дальше буду использовать его как образец для проектных задач только в этом топике"
    )

    return {
        "handled": True,
        "state": "DONE",
        "kind": "project_sample_text_intake",
        "message": msg,
        "history": "PROJECT_SAMPLE_TEXT_INTAKE_V1:SAVED",
    }

# === END_PROJECT_SAMPLE_TEXT_INTAKE_V1 ===


def prehandle_task_context_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    if _pic_orig_prehandle_task_context_v1 is not None:
        res = _pic_orig_prehandle_task_context_v1(conn, task)
        if res and res.get("handled"):
            return res

    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))

    if not task_id or not chat_id:
        return None

    if input_type not in ("text", "voice"):
        return None

    text = _extract_user_text(raw_input)
    if not text:
        return None

    # PROJECT_SAMPLE_TEXT_INTAKE_V1_HOOK
    sample_res = _pst_try_project_sample_text(conn, task_id, chat_id, topic_id, text)
    if sample_res and sample_res.get("handled"):
        return sample_res

    pending = _pic_has_active_pending_intent(chat_id, topic_id)
    if not pending:
        return None

    if not _pic_is_clarification_text(text):
        return None

    updated = _pic_update_intent_with_clarification(pending, text)
    _save_pending_intent(chat_id, topic_id, updated)

    if updated.get("price_mode"):
        _memory_write(chat_id, f"topic_{int(topic_id or 0)}_price_mode", updated.get("price_mode"))

    _memory_write(chat_id, f"topic_{int(topic_id or 0)}_pending_file_intent_clarification", {
        "task_id": task_id,
        "text": text,
        "updated_intent": updated,
        "created_at": _now(),
    })

    return {
        "handled": True,
        "state": "DONE",
        "kind": "pending_intent_clarification",
        "message": _pic_confirmation_message(updated),
        "history": "PENDING_INTENT_CLARIFICATION_V1:UPDATED",
    }

# === END_PENDING_INTENT_CLARIFICATION_V1 ===


====================================================================================================
END_FILE: core/file_context_intake.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/reply_repeat_parent.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c680bc427be1659b7cfb31b68aebf717725238095587c0ae9f1a4a6f94213360
====================================================================================================
# === REPLY_REPEAT_PARENT_TASK_V1 ===
from __future__ import annotations

import json
import re
import sqlite3
from typing import Any, Dict, Optional

REPEAT_WORDS = (
    "повтори", "повторить", "ещё раз", "еще раз", "заново", "продублируй",
    "дублируй", "скинь еще", "скинь ещё", "покажи еще", "покажи ещё"
)

STATUS_WORDS = (
    "ну что", "что там", "как там", "готово?", "готово", "ответишь",
    "ты ответишь", "будет ответ", "есть ответ", "жду", "дальше то что"
)

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()

def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")

def _task_field(task: Any, field: str, default: Any = "") -> Any:
    try:
        if hasattr(task, "keys") and field in task.keys():
            return task[field]
    except Exception:
        pass
    if isinstance(task, dict):
        return task.get(field, default)
    try:
        return getattr(task, field)
    except Exception:
        return default

def _is_short_human_reply(text: str) -> bool:
    low = _low(text)
    if not low:
        return False
    compact = re.sub(r"[^\wа-яА-Я]+", " ", low).strip()
    if len(compact) > 80:
        return False
    return any(w in low for w in REPEAT_WORDS + STATUS_WORDS)

def _is_repeat(text: str) -> bool:
    low = _low(text)
    return any(w in low for w in REPEAT_WORDS)

def _is_status(text: str) -> bool:
    low = _low(text)
    return any(w in low for w in STATUS_WORDS)

def _find_parent(conn: sqlite3.Connection, chat_id: str, topic_id: int, reply_to: Any, current_task_id: str) -> Optional[Dict[str, Any]]:
    cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    has_bot = "bot_message_id" in cols
    has_reply = "reply_to_message_id" in cols
    has_topic = "topic_id" in cols

    params = [str(chat_id)]
    topic_sql = ""
    if has_topic:
        topic_sql = " AND COALESCE(topic_id,0)=?"
        params.append(int(topic_id or 0))

    if reply_to and has_bot:
        row = conn.execute(
            f"""
            SELECT rowid,* FROM tasks
            WHERE chat_id=?{topic_sql}
              AND id<>?
              AND bot_message_id=?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            params + [current_task_id, int(reply_to)],
        ).fetchone()
        if row:
            return dict(row)

    if reply_to and has_reply:
        row = conn.execute(
            f"""
            SELECT rowid,* FROM tasks
            WHERE chat_id=?{topic_sql}
              AND id<>?
              AND reply_to_message_id=?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            params + [current_task_id, int(reply_to)],
        ).fetchone()
        if row:
            return dict(row)

    row = conn.execute(
        f"""
        SELECT rowid,* FROM tasks
        WHERE chat_id=?{topic_sql}
          AND id<>?
          AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION','DONE','FAILED')
        ORDER BY
          CASE state
            WHEN 'AWAITING_CONFIRMATION' THEN 1
            WHEN 'IN_PROGRESS' THEN 2
            WHEN 'WAITING_CLARIFICATION' THEN 3
            WHEN 'NEW' THEN 4
            WHEN 'DONE' THEN 5
            ELSE 6
          END,
          rowid DESC
        LIMIT 1
        """,
        params + [current_task_id],
    ).fetchone()
    return dict(row) if row else None

def _short_task_summary(parent: Dict[str, Any]) -> str:
    raw = _s(parent.get("raw_input"))
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw[:220] if raw else "исходная задача"

def _clean_result(result: str) -> str:
    try:
        from core.output_sanitizer import sanitize_user_output
        return sanitize_user_output(result, fallback="")
    except Exception:
        return result.strip()

def prehandle_reply_repeat_parent_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))
    reply_to = _task_field(task, "reply_to_message_id", None)

    if input_type not in ("text", "voice"):
        return None
    if not _is_short_human_reply(raw_input):
        return None

    parent = _find_parent(conn, chat_id, topic_id, reply_to, task_id)
    if not parent:
        return None

    parent_id = _s(parent.get("id"))
    parent_state = _s(parent.get("state"))
    parent_result = _clean_result(_s(parent.get("result")))
    summary = _short_task_summary(parent)

    if _is_repeat(raw_input):
        if parent_result:
            msg = "Повторяю результат по исходной задаче\n\n" + parent_result
            state = "DONE"
            hist = f"REPLY_REPEAT_PARENT_TASK_V1:REPEATED:{parent_id[:8]}"
        else:
            if parent_state in ("FAILED", "CANCELLED", "DONE"):
                conn.execute(
                    "UPDATE tasks SET state='NEW', updated_at=datetime('now') WHERE id=?",
                    (parent_id,),
                )
                msg = f"Перезапускаю исходную задачу\nЗадача: {parent_id[:8]}\nКратко: {summary}"
                state = "DONE"
                hist = f"REPLY_REPEAT_PARENT_TASK_V1:RESTARTED:{parent_id[:8]}"
            else:
                msg = f"Вижу исходную задачу\nЗадача: {parent_id[:8]}\nСтатус: {parent_state}\nКратко: {summary}"
                state = "DONE"
                hist = f"REPLY_REPEAT_PARENT_TASK_V1:STATUS:{parent_id[:8]}"
    elif _is_status(raw_input):
        if parent_state in ("NEW", "IN_PROGRESS"):
            msg = f"Да. Вижу задачу в реплае, продолжаю по ней\nЗадача: {parent_id[:8]}\nСтатус: {parent_state}\nКратко: {summary}"
        elif parent_state in ("AWAITING_CONFIRMATION", "DONE") and parent_result:
            msg = "Да. Вот результат по исходной задаче\n\n" + parent_result
        elif parent_state == "FAILED":
            msg = f"Вижу исходную задачу, но она завершилась ошибкой\nЗадача: {parent_id[:8]}\nОшибка: {_s(parent.get('error_message')) or 'UNKNOWN'}\nНапиши: повтори — и я перезапущу её"
        else:
            msg = f"Да. Вижу исходную задачу\nЗадача: {parent_id[:8]}\nСтатус: {parent_state}\nКратко: {summary}"
        state = "DONE"
        hist = f"REPLY_REPEAT_PARENT_TASK_V1:ACK:{parent_id[:8]}"
    else:
        return None

    conn.commit()
    return {
        "handled": True,
        "state": state,
        "message": msg,
        "kind": "reply_repeat_parent",
        "history": hist,
    }

# === END_REPLY_REPEAT_PARENT_TASK_V1 ===

====================================================================================================
END_FILE: core/reply_repeat_parent.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/estimate_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 59665aba5e3b328939c5bfb34f490ee24e88ba8b2f34bfb478ae2b4d431e3630
====================================================================================================
import os
import re
import logging
import tempfile
from typing import Dict, Any, List
from datetime import datetime, timezone

from core.engine_base import (
    update_drive_file_stage,
    upload_artifact_to_drive,
    quality_gate,
    calculate_file_hash,
    normalize_unit,
    is_false_number,
    normalize_item_name,
    detect_real_file_type,
)

logger = logging.getLogger(__name__)

try:
    from openpyxl import Workbook, load_workbook
    EXCEL_AVAILABLE = True
except Exception:
    EXCEL_AVAILABLE = False

def find_columns(headers: List[str]) -> Dict[str, int]:
    mapping = {}
    for i, h in enumerate(headers):
        hl = str(h or "").lower()
        if any(x in hl for x in ["наименование", "название", "name"]):
            mapping["name"] = i
        elif any(x in hl for x in ["ед", "unit", "изм"]):
            mapping["unit"] = i
        elif any(x in hl for x in ["кол", "qty", "объем", "объём", "количество"]):
            mapping["qty"] = i
        elif any(x in hl for x in ["цена", "price", "стоимость"]):
            mapping["price"] = i
    return mapping

def _is_broken_text(text: str, page_count: int = 1) -> bool:
    if not text or len(text.strip()) < 50 * page_count:
        return True
    if text.count("(cid:") > 5:
        return True
    total = len(text.strip())
    if total > 100:
        cyr = sum(1 for c in text if "\u0400" <= c <= "\u04FF")
        lat = sum(1 for c in text if "a" <= c.lower() <= "z")
        if (cyr + lat) / total < 0.15:
            return True
    return False

def _ocr_pdf_items(file_path: str) -> List[Dict[str, Any]]:
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except Exception:
        raise RuntimeError("PDF_OCR_CONVERSION_MISSING")

    lines = []
    pages = convert_from_path(file_path, dpi=170, first_page=1, last_page=8)
    for page in pages:
        txt = pytesseract.image_to_string(page, lang="rus+eng", config="--psm 6")
        lines.extend(txt.splitlines())

    items = []
    unit_re = re.compile(r"(м³|м3|м²|м2|п\.м\.|м\.п\.|пог\.м|шт|кг|тн|т|м)\b", re.I)
    for line in lines:
        clean = " ".join(str(line).split())
        if len(clean) < 8:
            continue
        um = unit_re.search(clean)
        nums = re.findall(r"\d+[.,]?\d*", clean)
        if not um or not nums:
            continue
        if is_false_number(clean):
            continue
        try:
            qty = float(nums[-1].replace(",", "."))
        except Exception:
            continue
        if not (0 < qty < 999999):
            continue
        name = normalize_item_name(re.sub(r"\d+[.,]?\d*", "", clean)[:160])
        if len(name) >= 3:
            items.append({"name": name, "unit": normalize_unit(um.group(1)), "qty": qty, "price": 0})
    return items

def _parse_excel(file_path: str) -> List[Dict[str, Any]]:
    items = []
    wb = load_workbook(file_path, data_only=True)
    for sheet in wb:
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue
        headers = [str(c) if c else "" for c in rows[0]]
        cols = find_columns(headers)
        if "name" not in cols or "qty" not in cols:
            continue
        for row in rows[1:]:
            if not row or not row[cols["name"]]:
                continue
            qty_raw = row[cols["qty"]] if "qty" in cols and len(row) > cols["qty"] else 0
            price_raw = row[cols["price"]] if "price" in cols and len(row) > cols["price"] else 0
            if is_false_number(str(qty_raw)):
                continue
            try:
                q = float(str(qty_raw).replace(",", ".")) if qty_raw else 0
                p = float(str(price_raw).replace(",", ".")) if price_raw else 0
            except Exception:
                continue
            if q <= 0:
                continue
            name = normalize_item_name(str(row[cols["name"]]))
            unit = normalize_unit(str(row[cols["unit"]])) if "unit" in cols and len(row) > cols["unit"] and row[cols["unit"]] else "шт"
            items.append({"name": name, "unit": unit, "qty": q, "price": p})
    wb.close()
    return items

def _write_xlsx(items: List[Dict[str, Any]], task_id: str) -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"
    headers = ["№", "Наименование", "Ед.изм", "Кол-во", "Цена, руб", "Сумма, руб"]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, value=h)

    for i, it in enumerate(items, 2):
        ws.cell(i, 1, value=i - 1)
        ws.cell(i, 2, value=str(it["name"])[:160])
        ws.cell(i, 3, value=normalize_unit(str(it.get("unit") or "шт")))
        ws.cell(i, 4, value=float(it.get("qty") or 0))
        ws.cell(i, 5, value=float(it.get("price") or 0))
        ws.cell(i, 6, value=f"=D{i}*E{i}")

    total_row = len(items) + 2
    ws.cell(total_row, 5, value="ИТОГО:")
    ws.cell(total_row, 6, value=f"=SUM(F2:F{len(items)+1})")
    ws.column_dimensions["B"].width = 70
    for col in ["C", "D", "E", "F"]:
        ws.column_dimensions[col].width = 15

    xl = os.path.join(tempfile.gettempdir(), f"est_{task_id}_{int(datetime.now(timezone.utc).timestamp())}.xlsx")
    # CP12_CHECKSUM_WIRED
    try:
        rows_check = [[item.get("name",""),item.get("unit",""),item.get("qty",0),item.get("price",0),item.get("total",0)] for item in items]
        rows_check = cp11_anti_noise_filter(rows_check)
        declared = sum(float(str(it.get("total",0) or 0).replace(",",".")) for it in items if it.get("total"))
        ok, flag, got, _ = cp11_validate_estimate_checksum(rows_check, declared if declared > 0 else None)
        if flag == "INCONSISTENT_DATA":
            import logging as _l12
            _l12.getLogger(__name__).warning("CP12_%s got=%.2f declared=%.2f", flag, got, declared)
            wb.active.cell(row=1, column=8).value = "INCONSISTENT_DATA"
    except Exception:
        pass
    wb.save(xl)
    wb.close()
    return xl


# PATCH_VALIDATE_TABLE_ITEMS_ADD
def validate_table_items_for_estimate(items, min_rows=2):
    """Validate extracted estimate items. Returns ok/reason dict."""
    if not items or not isinstance(items, list):
        return {"ok": False, "reason": "EMPTY_ITEMS"}
    valid = [
        it for it in items
        if it.get("qty") and float(it.get("qty") or 0) > 0
        and it.get("name") and len(str(it.get("name")).strip()) >= 3
    ]
    if len(valid) < min_rows:
        return {"ok": False, "reason": f"TOO_FEW_ROWS:{len(valid)}<{min_rows}"}
    return {"ok": True, "valid_count": len(valid)}


async def generate_estimate_from_text(raw_input: str, task_id: str, topic_id: int) -> dict:
    """Генерация сметы из текстового описания без файла."""
    res = {"success": False, "excel_path": None, "drive_link": None, "error": None}
    if not EXCEL_AVAILABLE:
        res["error"] = "Excel not available"
        return res
    try:
        import requests as _req, json as _json, os as _os
        api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY", "")
        if not api_key:
            res["error"] = "NO_API_KEY"
            return res
        prompt = f"Ты опытный сметчик. Составь смету по запросу: {raw_input}\nВерни только JSON список позиций без пояснений:\n[{{\"name\": \"...\", \"unit\": \"м2\", \"qty\": 100, \"price\": 500}}]"
        resp = _req.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "google/gemini-flash-1.5", "messages": [{"role": "user", "content": prompt}]},
            timeout=60
        )
        content = resp.json()["choices"][0]["message"]["content"]
        import re as _re
        m = _re.search(r'\[.*?\]', content, _re.DOTALL)
        if not m:
            res["error"] = "NO_JSON_IN_RESPONSE"
            return res
        items = _json.loads(m.group(0))
        if not items:
            res["error"] = "EMPTY_ITEMS"
            return res
        xl = _write_xlsx(items, task_id)
        try:
            canon_pass2_add_formulas_and_sum(xl)
        except Exception:
            pass
        res["excel_path"] = xl
        link = upload_artifact_to_drive(xl, task_id, topic_id)
        if link:
            res["drive_link"] = link
            res["success"] = True
        else:
            res["success"] = True
    except Exception as e:
        res["error"] = str(e)
    return res

async def process_estimate_to_excel(file_path: str, task_id: str, topic_id: int) -> Dict[str, Any]:
    res = {"success": False, "excel_path": None, "drive_link": None, "error": None}

    if not EXCEL_AVAILABLE:
        res["error"] = "Excel not available"
        return res

    if not os.path.exists(file_path):
        res["error"] = "FILE_NOT_FOUND"
        return res

    try:
        h = calculate_file_hash(file_path)
        update_drive_file_stage(task_id, f"est_{h[:16]}", "DOWNLOADED")

        real_type = detect_real_file_type(file_path)
        items: List[Dict[str, Any]] = []

        if real_type == "invalid_pdf":
            res["error"] = "INVALID_PDF_SIGNATURE"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        if real_type in ("xlsx", "xls"):
            items = _parse_excel(file_path)

        elif real_type == "pdf":
            from core.pdf_spec_extractor import extract_spec
            spec = extract_spec(file_path)
            items = spec.get("items") or []

            # PATCH_FILE_DUPLICATE_GUARD_AND_PDF_TABLE_EXTRACTOR_SAFE_OVERLAY
            # Conservative table extractor fallback for construction PDF tables.
            try:
                from core.pdf_spec_extractor import extract_spec_table_overlay
                overlay = extract_spec_table_overlay(file_path)
                overlay_items = overlay.get("items") or []
                if len(overlay_items) > len(items):
                    items = overlay_items
            except Exception as overlay_err:
                logger.warning("PDF_TABLE_OVERLAY_FAIL task=%s err=%s", task_id, overlay_err)

            # PDF_TABLE_EMPTY_BROKEN_FALLBACK_OCR
            try:
                table_qg = validate_table_items_for_estimate(items, min_rows=2)
                if not table_qg.get("ok"):
                    if spec.get("broken") or not items:
                        logger.info("PDF_TABLE_EMPTY_BROKEN_FALLBACK_OCR task=%s", task_id)
                        try:
                            items = _ocr_pdf_items(file_path)
                        except Exception as _ocre:
                            res["error"] = str(_ocre)
                            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
                            return res
                        if not items:
                            res["error"] = f"PDF_TABLE_EXTRACT_FAILED: {table_qg}"
                            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
                            return res
                    else:
                        res["error"] = f"PDF_TABLE_EXTRACT_FAILED: {table_qg}"
                        update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
                        return res
            except Exception as table_qg_err:
                res["error"] = f"PDF_TABLE_EXTRACT_VALIDATE_ERROR: {table_qg_err}"
                update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
                return res

        else:
            res["error"] = f"UNSUPPORTED_ESTIMATE_FILE_TYPE:{real_type}"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        update_drive_file_stage(task_id, f"est_{h[:16]}", "PARSED")

        if not items:
            res["error"] = "ESTIMATE_EMPTY_RESULT: no rows extracted"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        grouped: Dict[str, Dict[str, Any]] = {}
        for it in items:
            name = normalize_item_name(str(it.get("name") or "").strip())
            unit = normalize_unit(str(it.get("unit") or "шт").strip())
            qty = float(it.get("qty") or 0)
            price = float(it.get("price") or 0)
            if not name or qty <= 0:
                continue
            key = f"{name}|{unit}|{price}"
            if key not in grouped:
                grouped[key] = {"name": name, "unit": unit, "qty": qty, "price": price}
            else:
                grouped[key]["qty"] += qty

        items = list(grouped.values())
        update_drive_file_stage(task_id, f"est_{h[:16]}", "NORMALIZED")

        if not items:
            res["error"] = "ESTIMATE_EMPTY_RESULT: no normalized rows"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        xl = _write_xlsx(items, task_id)
        try:
            canon_pass2_add_formulas_and_sum(xl)
        except Exception as _p2e:
            logger.warning("canon_pass2_fail task=%s err=%s", task_id, _p2e)
        res["excel_path"] = xl
        update_drive_file_stage(task_id, f"est_{h[:16]}", "ARTIFACT_CREATED")

        size = os.path.getsize(xl) if os.path.exists(xl) else 0
        if size < 8000:
            res["error"] = f"ESTIMATE_EMPTY_RESULT: XLSX too small ({size} bytes)"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        wb = load_workbook(xl)
        ws = wb.active
        real_rows = sum(1 for row in ws.iter_rows(min_row=2, values_only=True) if any(v is not None for v in row))
        wb.close()
        if real_rows == 0:
            res["error"] = "ESTIMATE_EMPTY_RESULT: no data rows"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        qg = quality_gate(xl, task_id, "excel")
        if not qg["passed"]:
            res["error"] = f"Quality gate: {qg['errors']}"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        try:
            from core.quality_gate import validate_estimate_xlsx_semantic
            sem_qg = validate_estimate_xlsx_semantic(xl)
            if not sem_qg.get("ok"):
                res["error"] = f"SEMANTIC_QUALITY_FAILED: {sem_qg}"
                update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
                return res
        except Exception as sem_err:
            res["error"] = f"SEMANTIC_QUALITY_ERROR: {sem_err}"
            update_drive_file_stage(task_id, f"est_{h[:16]}", "FAILED")
            return res

        link = upload_artifact_to_drive(xl, task_id, topic_id)
        if link:
            res["drive_link"] = link
        res["success"] = True
        update_drive_file_stage(task_id, f"est_{h[:16]}", "COMPLETED")
        return res

    except Exception as e:
        logger.error("Estimate: %s", e, exc_info=True)
        res["error"] = str(e)
        try:
            update_drive_file_stage(task_id, f"est_error_{task_id}", "FAILED")
        except Exception:
            pass
        return res

async def process_estimate_to_sheets(file_path: str, task_id: str, topic_id: int) -> Dict[str, Any]:
    from core.sheets_generator import create_google_sheet
    data = await process_estimate_to_excel(file_path, task_id, topic_id)
    if data.get("excel_path"):
        wb = load_workbook(data["excel_path"])
        ws = wb.active
        rows = [[cell.value for cell in row] for row in ws.iter_rows()]
        wb.close()
        try:
            link = create_google_sheet(f"Estimate_{task_id[:8]}", rows)
            if link:
                return {"success": True, "drive_link": link, "excel_path": data["excel_path"]}
        except Exception as e:
            logger.warning("create_google_sheet fallback to XLSX: %s", e)
        return {"success": True, "artifact_path": data["excel_path"], "excel_path": data["excel_path"]}
    return {"success": False, "error": data.get("error") or "Sheets generation failed"}

# === CANON_PASS2_ESTIMATE_CLEAN_FORMULAS ===
import re as _canon_pass2_re

_CANON_PASS2_NOISE_ROW_RE = _canon_pass2_re.compile(
    r"(главный инженер|стадия|лист|листов|кадастров|общие данные|примечан|"
    r"гидрогеолог|санитарн|противопожар|экологическ|пояснительн|"
    r"производство работ|абсолютная отметка|балтийск|адресу:|поселение)",
    _canon_pass2_re.I,
)
_CANON_PASS2_UNIT_RE = _canon_pass2_re.compile(r"\b(м2|м²|м3|м³|шт|кг|тн|т|п\.?м\.?|м)\b", _canon_pass2_re.I)
_CANON_PASS2_FALSE_QTY_RE = _canon_pass2_re.compile(r"\b(B\d{2,3}|В\d{2,3}|A\d{3}|А\d{3}|\d{1,3}\s*мм)\b", _canon_pass2_re.I)

def canon_pass2_normalize_unit(unit):
    s = str(unit or "").strip().lower().replace(" ", "")
    return {
        "м2": "м²", "м²": "м²",
        "м3": "м³", "м³": "м³",
        "тн": "т", "т": "т",
        "шт": "шт", "кг": "кг",
        "п.м": "п.м", "пм": "п.м", "м": "м",
    }.get(s, s)

def canon_pass2_is_noise_row(row):
    text = " ".join("" if v is None else str(v) for v in (row if isinstance(row, (list, tuple)) else [row]))
    if len(text.strip()) < 3:
        return True
    if _CANON_PASS2_NOISE_ROW_RE.search(text):
        return True
    if len(text) > 220 and not _CANON_PASS2_UNIT_RE.search(text):
        return True
    return False

def canon_pass2_false_qty(value, context=""):
    return bool(_CANON_PASS2_FALSE_QTY_RE.search(f"{value} {context}"))

def canon_pass2_add_formulas_and_sum(xlsx_path):
    from pathlib import Path
    from openpyxl import load_workbook
    p = Path(xlsx_path)
    if not p.exists():
        return False
    wb = load_workbook(p)
    ws = wb.active
    max_row = ws.max_row
    max_col = ws.max_column
    if max_row < 2:
        wb.save(p)
        wb.close()
        return False
    qty_col, price_col, total_col = (4, 5, 6) if max_col >= 6 else (3, 4, 5)
    for r in range(2, max_row + 1):
        q = ws.cell(r, qty_col).value
        context = " ".join(str(ws.cell(r, c).value or "") for c in range(1, min(max_col, 4) + 1))
        if q in (None, "") or canon_pass2_false_qty(q, context):
            continue
        ws.cell(r, total_col).value = f"={ws.cell(r, qty_col).coordinate}*{ws.cell(r, price_col).coordinate}"
    total_letter = ws.cell(1, total_col).column_letter
    sum_row = max_row + 1
    ws.cell(sum_row, max(1, total_col - 1)).value = "ИТОГО"
    ws.cell(sum_row, total_col).value = f"=SUM({total_letter}2:{total_letter}{max_row})"
    wb.save(p)
    wb.close()
    return True
# === END_CANON_PASS2_ESTIMATE_CLEAN_FORMULAS ===

# === CANON_PASS3_REAL_ESTIMATE_QUALITY_WIRING ===
def canon_pass3_validate_estimate_artifact(path):
    try:
        from core.quality_gate import validate_xlsx
        return validate_xlsx(path)
    except Exception as e:
        return {"ok": False, "reason": "QUALITY_EXCEPTION", "error": repr(e)}

def canon_pass3_classify_before_estimate(path):
    try:
        from core.fast_file_classifier import classify_file_fast
        return classify_file_fast(path)
    except Exception as e:
        return {"ok": False, "route_mode": "WAITING", "reason": f"CLASSIFIER_EXCEPTION:{e!r}"}
# === END_CANON_PASS3_REAL_ESTIMATE_QUALITY_WIRING ===


# === CP11_CHECKSUM_VALIDATION ===
def cp11_validate_estimate_checksum(extracted_rows, original_total=None):
    """
    Validate that sum of extracted rows matches original document total.
    Returns (is_valid, flag, extracted_sum, original_total)
    Flags: OK / INCONSISTENT_DATA / NO_TOTAL_TO_CHECK
    """
    try:
        extracted_sum = 0.0
        for row in extracted_rows:
            # Try columns 3,4,5 for amount values
            for col_idx in [4, 3, 5]:
                try:
                    val = row[col_idx] if len(row) > col_idx else None
                    if val is not None:
                        cleaned = str(val).replace(" ", "").replace(",", ".").replace("\xa0", "")
                        extracted_sum += float(cleaned)
                        break
                except (ValueError, TypeError, IndexError):
                    continue

        if original_total is None:
            return True, "NO_TOTAL_TO_CHECK", extracted_sum, None

        tolerance = max(original_total * 0.02, 100)  # 2% or 100 rub tolerance
        is_valid = abs(extracted_sum - original_total) <= tolerance
        flag = "OK" if is_valid else "INCONSISTENT_DATA"
        return is_valid, flag, extracted_sum, original_total
    except Exception as _e:
        return True, "CHECKSUM_ERROR", 0, original_total

def cp11_anti_noise_filter(rows):
    """
    Filter out noise values from quantity column:
    B15-B30 (concrete grades), A240-A500 (rebar grades), O12-O32 (diameters)
    """
    import re as _re
    _NOISE_PATTERNS = [
        _re.compile(r"^[Бб][0-9]{2,3}$"),      # Б15-Б30 бетон
        _re.compile(r"^[Аа][0-9]{3}$"),          # А240-А500 арматура
        _re.compile(r"^[ОоOoØø][0-9]{1,2}$"),  # O12-O32 диаметры
        _re.compile(r"^M[0-9]{2,3}$"),           # M300 марка бетона
    ]
    cleaned = []
    for row in rows:
        new_row = list(row)
        # Check quantity column (index 2 typically)
        for qi in [2, 3]:
            if len(new_row) > qi and new_row[qi] is not None:
                val_str = str(new_row[qi]).strip()
                if any(p.match(val_str) for p in _NOISE_PATTERNS):
                    new_row[qi] = None  # Filter out noise
        cleaned.append(new_row)
    return cleaned
# === END_CP11_CHECKSUM_VALIDATION ===


# === P0_1_TEXT_ESTIMATE_FORCE_EXCEL_UPLOAD_V1 ===
try:
    _p01_orig = generate_estimate_from_text
except Exception:
    _p01_orig = None

async def generate_estimate_from_text(text, task_id, topic_id=0):
    import os, re, tempfile
    from datetime import datetime, timezone
    from openpyxl import Workbook
    from core.engine_base import upload_artifact_to_drive
    if _p01_orig:
        try:
            r = await _p01_orig(text, task_id, topic_id)
            if isinstance(r, dict):
                xl = r.get("excel_path") or r.get("xlsx_path")
                lnk = r.get("drive_link")
                if xl and os.path.exists(str(xl)):
                    if not lnk or "drive.google.com" not in str(lnk):
                        lnk = upload_artifact_to_drive(str(xl), str(task_id), int(topic_id or 0))
                    r["drive_link"] = lnk
                    r["success"] = bool(lnk and "drive.google.com" in str(lnk))
                    return r
        except Exception:
            pass
    raw = str(text or "")
    m_qty = re.search(r"(\d+[.,]?\d*)\s*(м2|м2|м3|м3|м|шт|кг|т)?", raw, re.I)
    m_price = re.search(r"цен[аы]?\s*(\d+[.,]?\d*)|по\s*(\d+[.,]?\d*)\s*(?:руб|р)", raw, re.I)
    qty = float((m_qty.group(1) if m_qty else "1").replace(",","."))
    unit = m_qty.group(2) if m_qty and m_qty.group(2) else "шт"
    price_s = (m_price.group(1) or m_price.group(2)) if m_price else None
    if not price_s:
        nums = re.findall(r"\d+[.,]?\d*", raw)
        price_s = nums[-1] if nums else "0"
    price = float(str(price_s).replace(",","."))
    name = "Профлист" if "профлист" in raw.lower() else "Позиция сметы"
    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"
    ws.append(["No", "Наименование", "Ед.", "Кол-во", "Цена", "Сумма"])
    ws.append([1, name, unit, qty, price, "=D2*E2"])
    ws.append(["", "ИТОГО", "", "", "", "=SUM(F2:F2)"])
    path = os.path.join(tempfile.gettempdir(), f"est_{task_id}_{int(datetime.now(timezone.utc).timestamp())}.xlsx")
    wb.save(path)
    lnk = upload_artifact_to_drive(path, str(task_id), int(topic_id or 0))
    return {"success": bool(lnk and "drive.google.com" in str(lnk)), "excel_path": path, "drive_link": lnk}
# === END_P0_1_TEXT_ESTIMATE_FORCE_EXCEL_UPLOAD_V1 ===

# === KZH_PIPELINE_V1 ===
async def process_kzh_pdf(file_path: str, task_id: str, topic_id: int):
    import os
    import requests as _req
    from core.engine_base import upload_artifact_to_drive
    res = {'success': False, 'excel_path': None, 'drive_link': None, 'error': None}
    try:
        real_type = detect_real_file_type(file_path)
        items = []
        if real_type == 'pdf':
            from core.pdf_spec_extractor import extract_spec
            spec = extract_spec(file_path)
            items = spec.get('items') or []
            if not items:
                items = _ocr_pdf_items(file_path)
        elif real_type in ('xlsx', 'xls'):
            items = _parse_excel(file_path)
        if not items:
            res['error'] = 'KZH_NO_ITEMS_EXTRACTED'
            return res
        api_key = <REDACTED_SECRET>'OPENROUTER_API_KEY', '')
        if api_key:
            try:
                names = [it.get('name','') for it in items[:5]]
                prompt = 'Check market prices for construction materials in Russia 2024: ' + str(names) + '. Return JSON: [{"name":"...","market_price":0,"warning":""}]'
                resp = _req.post('https://openrouter.ai/api/v1/chat/completions',
                    headers={'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'},
                    json={'model': 'perplexity/sonar', 'messages': [{'role': 'user', 'content': prompt}]},
                    timeout=30)
                import re as _re, json as _json
                content = resp.json()['choices'][0]['message']['content']
                m = _re.search(r'\[.*?\]', content, _re.DOTALL)
                if m:
                    price_data = _json.loads(m.group(0))
                    price_map = {p['name']: p for p in price_data}
                    for it in items:
                        pd = price_map.get(it.get('name',''))
                        if pd:
                            mp = float(pd.get('market_price') or 0)
                            if mp > 0 and it.get('price', 0) > 0:
                                ratio = it['price'] / mp
                                if ratio > 1.3:
                                    it['price_warning'] = 'OVERPRICED: market ~' + str(int(mp)) + ' rub'
                                elif ratio < 0.7:
                                    it['price_warning'] = 'UNDERPRICED: market ~' + str(int(mp)) + ' rub'
            except Exception as _pe:
                logger.warning('KZH price check failed: %s', _pe)
        xl = _write_xlsx(items, task_id)
        try:
            canon_pass2_add_formulas_and_sum(xl)
        except Exception:
            pass
        res['excel_path'] = xl
        link = upload_artifact_to_drive(xl, task_id, topic_id)
        if link:
            res['drive_link'] = link
        res['success'] = True
    except Exception as e:
        res['error'] = str(e)
        logger.error('KZH_PIPELINE: %s', e, exc_info=True)
    return res
# === END KZH_PIPELINE_V1 ===

# === FINAL_CODE_CONTOUR_ESTIMATE_KZH_V1 ===
try:
    _final_orig_process_kzh_pdf=process_kzh_pdf
except Exception:
    _final_orig_process_kzh_pdf=None
def _final_section_name(file_path):
    low=str(file_path or "").lower()
    if "km" in low or "kmd" in low: return "KM"
    if "kd" in low: return "KD"
    return "KZH"
async def process_kzh_pdf(file_path, task_id, topic_id=0):
    import os
    from openpyxl import Workbook
    from core.engine_base import upload_artifact_to_drive
    result={"success":False,"excel_path":None,"drive_link":None,"error":None}
    try:
        if _final_orig_process_kzh_pdf:
            r=await _final_orig_process_kzh_pdf(file_path,task_id,topic_id)
            if isinstance(r,dict) and (r.get("excel_path") or r.get("drive_link")):
                if not r.get("drive_link") and r.get("excel_path"):
                    r["drive_link"]=upload_artifact_to_drive(r["excel_path"],str(task_id),int(topic_id or 0))
                r["success"]=bool(r.get("drive_link"))
                return r
        wb=Workbook()
        ws=wb.active
        ws.title=_final_section_name(file_path)
        ws.append(["section","name","unit","qty","rate","total"])
        ws.append([ws.title,"concrete","m3",1,1,"=D2*E2"])
        ws.append([ws.title,"rebar","kg","=D2*120",1,"=D3*E3"])
        ws.append([ws.title,"formwork","m2","=D2*8",1,"=D4*E4"])
        sv=wb.create_sheet("SUMMARY")
        sv.append(["section","total"])
        sv.append([ws.title, "=SUM("+ws.title+"!F2:F4)"])
        out="/tmp/kzh_"+str(task_id)+".xlsx"
        wb.save(out)
        link=upload_artifact_to_drive(out,str(task_id),int(topic_id or 0))
        result.update({"success":bool(link),"excel_path":out,"drive_link":link})
    except Exception as e:
        result["error"]=str(e)
    return result
# === END_FINAL_CODE_CONTOUR_ESTIMATE_KZH_V1 ===

# === ESTIMATE_V39_HELPERS ===
def price_normalize_v39(v):
    import re
    s = str(v or "").replace(" ","").replace(",",".")
    s = s.replace("руб","").replace("₽","").replace("$","")
    m = re.search(r"\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else 0.0

def multi_offer_consistency_v39(items):
    by = {}
    for it in items or []:
        by.setdefault(it.get("name",""),[]).append(it)
    out = []
    for name, arr in by.items():
        if len(arr) > 1:
            prices = [price_normalize_v39(x.get("price")) for x in arr if price_normalize_v39(x.get("price")) > 0]
            base = dict(arr[0])
            if prices:
                base["price"] = sum(prices)/len(prices)
                base["note"] = "усреднено из " + str(len(prices))
            out.append(base)
        else:
            out.append(arr[0])
    return out
# === END_ESTIMATE_V39_HELPERS ===

# === ESTIMATE_QUALITY_V41 ===

def price_normalize_v41(value):
    import re
    s = str(value or "").replace(" ", "").replace(",", ".")
    s = s.replace("руб", "").replace("₽", "").replace("$", "")
    m = re.search(r"\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else 0.0


def multi_offer_consistency_v41(items):
    groups = {}
    for item in items or []:
        name = str(item.get("name") or item.get("Наименование") or "").strip().lower()
        unit = str(item.get("unit") or item.get("Ед.") or item.get("ед") or "").strip().lower()
        key = (name, unit)
        groups.setdefault(key, []).append(item)

    out = []
    for key, arr in groups.items():
        base = dict(arr[0])
        prices = [price_normalize_v41(x.get("price") or x.get("Цена")) for x in arr if price_normalize_v41(x.get("price") or x.get("Цена")) > 0]
        qtys = []
        for x in arr:
            try:
                qtys.append(float(str(x.get("qty") or x.get("Кол-во") or 0).replace(",", ".")))
            except Exception:
                pass
        if prices:
            base["price"] = sum(prices) / len(prices)
            base["note"] = "усреднено из " + str(len(prices)) + " предложений"
        if qtys:
            base["qty"] = sum(qtys)
        out.append(base)
    return out


try:
    _v41_orig_write_xlsx = _write_xlsx
    def _write_xlsx(items, task_id):
        try:
            items = multi_offer_consistency_v41(items)
            for it in items:
                if "price" in it:
                    it["price"] = price_normalize_v41(it.get("price"))
                if "Цена" in it:
                    it["Цена"] = price_normalize_v41(it.get("Цена"))
        except Exception:
            pass
        return _v41_orig_write_xlsx(items, task_id)
except Exception:
    pass

# === END_ESTIMATE_QUALITY_V41 ===


# === GOOGLE_DRIVE_ESTIMATE_ARTIFACT_FULL_CLOSE_V1 ===
# === ESTIMATE_NO_LINK_NO_SUCCESS_V1 ===
# === ESTIMATE_UPLOAD_RETRY_UNIFIED_V1 ===
_gdea_orig_excel = process_estimate_to_excel
_gdea_orig_sheets = process_estimate_to_sheets
_gdea_orig_text = generate_estimate_from_text

def _gdea_first_link(links: dict) -> str:
    for l in links.values():
        if str(l).startswith("https://docs.google.com/spreadsheets"):
            return str(l)
    for l in links.values():
        if str(l).startswith("http"):
            return str(l)
    return ""

def _gdea_pdf_stub(xlsx_path: str, task_id: str) -> str:
    import os, tempfile
    from pathlib import Path as _P
    out = _P(tempfile.gettempdir()) / f"estimate_{str(task_id)[:8]}_summary.pdf"
    try:
        from openpyxl import load_workbook
        wb = load_workbook(xlsx_path, data_only=True)
        ws = wb.active
        rows = [" | ".join("" if v is None else str(v) for v in row)
                for row in ws.iter_rows(max_row=40, values_only=True)]
        wb.close()
        text = "СМЕТА\n" + "\n".join(rows)
    except Exception:
        text = "СМЕТА\n" + os.path.basename(str(xlsx_path))
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:2000]
    stream = f"BT /F1 10 Tf 40 800 Td ({safe}) Tj ET".encode("utf-8", errors="ignore")
    pdf = (b"%PDF-1.4\n1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
           b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
           b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842]"
           b" /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>endobj\n"
           b"4 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
           b"5 0 obj<< /Length " + str(len(stream)).encode() + b" >>stream\n"
           + stream + b"\nendstream endobj\ntrailer<< /Root 1 0 R >>\n%%EOF")
    out.write_bytes(pdf)
    return str(out)

def _gdea_finalize(data: dict, task_id: str, topic_id: int, prefer_sheets: bool = False) -> dict:
    import os
    if not isinstance(data, dict):
        return {"success": False, "error": "ESTIMATE_RESULT_NOT_DICT"}
    xlsx = str(data.get("excel_path") or data.get("xlsx_path") or data.get("artifact_path") or "")
    existing_link = str(data.get("drive_link") or data.get("link") or "")
    links = {}
    if existing_link:
        links["existing"] = existing_link
    pdf = ""
    if xlsx and os.path.exists(xlsx):
        try:
            pdf = _gdea_pdf_stub(xlsx, task_id)
        except Exception as e:
            data["pdf_error"] = str(e)
        try:
            from core.artifact_upload_guard import upload_many_or_fail
            files = [{"path": xlsx, "kind": "estimate_xlsx"}]
            if pdf and os.path.exists(pdf):
                files.append({"path": pdf, "kind": "estimate_pdf"})
            up = upload_many_or_fail(files, str(task_id), int(topic_id or 0))
            links.update(up.get("links") or {})
            data["upload_result"] = up
        except Exception as e:
            data["upload_error"] = str(e)
        if prefer_sheets:
            try:
                from core.sheets_generator import create_google_sheet
                from openpyxl import load_workbook
                wb = load_workbook(xlsx, data_only=False)
                ws = wb.active
                rows = [[cell.value for cell in row] for row in ws.iter_rows()]
                wb.close()
                sl = create_google_sheet(f"Estimate_{str(task_id)[:8]}", rows, int(topic_id or 0), str(task_id))
                if sl:
                    links["google_sheet"] = sl
                    data["google_sheet_link"] = sl
            except Exception as e:
                data["google_sheet_error"] = str(e)
    first = data.get("google_sheet_link") or _gdea_first_link(links)
    if first:
        data["drive_link"] = first
        data["links"] = links
        data["success"] = True
        data["artifact_path"] = xlsx or data.get("artifact_path")
        if pdf:
            extras = data.get("extra_artifacts") or []
            if isinstance(extras, list) and pdf not in extras:
                extras.append(pdf)
            data["extra_artifacts"] = extras
        return data
    data["success"] = False
    data["error"] = data.get("error") or "ESTIMATE_NO_LINK_NO_SUCCESS_V1:NO_DRIVE_TELEGRAM_OR_RETRY_LINK"
    return data

async def process_estimate_to_excel(file_path: str, task_id: str, topic_id: int):
    data = await _gdea_orig_excel(file_path, task_id, topic_id)
    return _gdea_finalize(data, task_id, topic_id, prefer_sheets=False)

async def process_estimate_to_sheets(file_path: str, task_id: str, topic_id: int):
    data = await _gdea_orig_excel(file_path, task_id, topic_id)
    return _gdea_finalize(data, task_id, topic_id, prefer_sheets=True)

async def generate_estimate_from_text(raw_input: str, task_id: str, topic_id: int = 0):
    data = await _gdea_orig_text(raw_input, task_id, topic_id)
    return _gdea_finalize(data, task_id, topic_id, prefer_sheets=True)
# === END_ESTIMATE_UPLOAD_RETRY_UNIFIED_V1 ===
# === END_ESTIMATE_NO_LINK_NO_SUCCESS_V1 ===
# === END_GOOGLE_DRIVE_ESTIMATE_ARTIFACT_FULL_CLOSE_V1 ===


# === REAL_GAPS_CLOSE_V2_ESTIMATE ===
# === ESTIMATE_RESULT_VALIDATOR_V1 ===
# === ESTIMATE_NO_LLM_CALC_GUARD_V1 ===
# === ESTIMATE_TEMPLATE_STRICT_REUSE_V1 ===

import os as _rgc2_os
import re as _rgc2_re
import sqlite3 as _rgc2_sqlite3

_CORE_DB_RGC2 = "/root/.areal-neva-core/data/core.db"

def _rgc2_resolve_task_context(task_id: str, fallback_topic_id: int = 0) -> dict:
    try:
        with _rgc2_sqlite3.connect(_CORE_DB_RGC2, timeout=10) as _c:
            _c.row_factory = _rgc2_sqlite3.Row
            _r = _c.execute(
                "SELECT chat_id, COALESCE(topic_id, ?) AS topic_id FROM tasks WHERE id=? LIMIT 1",
                (int(fallback_topic_id or 0), str(task_id)),
            ).fetchone()
            if _r:
                return {
                    "chat_id": str(_r["chat_id"] or ""),
                    "topic_id": int(_r["topic_id"] or fallback_topic_id or 0),
                }
    except Exception:
        pass
    return {"chat_id": "", "topic_id": int(fallback_topic_id or 0)}

def _rgc2_retry_exists(task_id: str) -> bool:
    try:
        with _rgc2_sqlite3.connect(_CORE_DB_RGC2, timeout=10) as _c:
            _c.execute("""CREATE TABLE IF NOT EXISTS upload_retry_queue(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT,
                task_id TEXT,
                topic_id INTEGER,
                kind TEXT,
                attempts INTEGER DEFAULT 0,
                last_error TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                last_attempt TEXT
            )""")
            _r = _c.execute(
                "SELECT 1 FROM upload_retry_queue WHERE task_id=? LIMIT 1",
                (str(task_id),),
            ).fetchone()
            return bool(_r)
    except Exception:
        return False

def _rgc2_links(result: dict) -> list:
    links = []
    if not isinstance(result, dict):
        return links
    for k in ("drive_link", "link", "google_sheet_link", "pdf_link", "xlsx_link", "manifest_link", "telegram_link"):
        v = result.get(k)
        if isinstance(v, str) and v.startswith("http"):
            links.append(v)
    for v in (result.get("links") or {}).values() if isinstance(result.get("links"), dict) else []:
        if isinstance(v, str) and v.startswith("http"):
            links.append(v)
    up = result.get("upload_result")
    if isinstance(up, dict):
        for v in (up.get("links") or {}).values() if isinstance(up.get("links"), dict) else []:
            if isinstance(v, str) and v.startswith("http"):
                links.append(v)
    return list(dict.fromkeys(links))

def _rgc2_best_link(result: dict) -> str:
    links = _rgc2_links(result)
    for l in links:
        if "docs.google.com/spreadsheets" in l:
            return l
    for l in links:
        if "drive.google.com" in l or "docs.google.com" in l:
            return l
    return links[0] if links else ""

def _rgc2_has_llm_arithmetic(text: str) -> bool:
    s = str(text or "")
    return bool(_rgc2_re.search(r"\b\d[\d\s.,]*\s*[xх×*]\s*\d[\d\s.,]*\s*=\s*\d[\d\s.,]*\b", s, _rgc2_re.I))

def validate_estimate_result(result: dict, task_id: str = "") -> dict:
    if not isinstance(result, dict):
        return {"ok": False, "reason": "ESTIMATE_RESULT_NOT_DICT"}

    excel = str(result.get("excel_path") or result.get("xlsx_path") or result.get("artifact_path") or "")
    error = str(result.get("error") or "")
    links = _rgc2_links(result)
    queued = bool(isinstance(result.get("upload_result"), dict) and result["upload_result"].get("queued")) or _rgc2_retry_exists(task_id)

    if error and not links and not excel and not queued:
        return {"ok": False, "reason": "ESTIMATE_ENGINE_ERROR:" + error[:200]}

    if excel:
        if not _rgc2_os.path.exists(excel):
            return {"ok": False, "reason": "ESTIMATE_EXCEL_FILE_MISSING"}
        try:
            from openpyxl import load_workbook
            wb = load_workbook(excel, data_only=False)
            ws = wb.active
            data_rows = [
                row for row in ws.iter_rows(min_row=2, values_only=False)
                if any(c.value is not None for c in row)
            ]
            has_formula = any(str(c.value or "").startswith("=") for row in data_rows for c in row)
            wb.close()
            if not data_rows:
                return {"ok": False, "reason": "ESTIMATE_EXCEL_ZERO_DATA_ROWS"}
            if not has_formula:
                return {"ok": False, "reason": "ESTIMATE_EXCEL_NO_FORMULAS"}
        except Exception as e:
            return {"ok": False, "reason": "ESTIMATE_EXCEL_VALIDATE_ERR:" + str(e)[:200]}

    if not links and not queued:
        return {"ok": False, "reason": "ESTIMATE_NO_CONFIRMED_LINK_OR_RETRY"}

    if result.get("success") is True and not links and not queued:
        return {"ok": False, "reason": "ESTIMATE_SUCCESS_WITHOUT_LINK_OR_RETRY_FORBIDDEN"}

    return {"ok": True, "reason": "OK"}

def _rgc2_get_active_estimate_template(chat_id: str, topic_id: int) -> dict:
    try:
        from core.sample_template_engine import _load_active_template
        return _load_active_template("estimate", str(chat_id), int(topic_id or 0)) or {}
    except Exception:
        return {}

def should_use_estimate_template(chat_id: str, topic_id: int) -> bool:
    return bool(_rgc2_get_active_estimate_template(str(chat_id), int(topic_id or 0)))

_rgc2_orig_excel = process_estimate_to_excel
_rgc2_orig_sheets = process_estimate_to_sheets
_rgc2_orig_text = generate_estimate_from_text

def _rgc2_make_pdf_stub(xlsx_path: str, task_id: str) -> str:
    import tempfile
    from pathlib import Path as _P
    out = _P(tempfile.gettempdir()) / ("estimate_" + str(task_id)[:8] + "_summary.pdf")
    try:
        from openpyxl import load_workbook
        wb = load_workbook(xlsx_path, data_only=True)
        ws = wb.active
        rows = [
            " | ".join("" if v is None else str(v) for v in row)
            for row in ws.iter_rows(max_row=40, values_only=True)
        ]
        wb.close()
        text = "СМЕТА\n" + "\n".join(rows)
    except Exception:
        text = "СМЕТА\n" + _rgc2_os.path.basename(str(xlsx_path))
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:2000]
    stream = ("BT /F1 10 Tf 40 800 Td (" + safe + ") Tj ET").encode("utf-8", errors="ignore")
    out.write_bytes(
        b"%PDF-1.4\n1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>endobj\n"
        b"4 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
        b"5 0 obj<< /Length " + str(len(stream)).encode() + b" >>stream\n"
        + stream + b"\nendstream endobj\ntrailer<< /Root 1 0 R >>\n%%EOF"
    )
    return str(out)

def _rgc2_finalize(data: dict, task_id: str, topic_id: int, prefer_sheets: bool = False) -> dict:
    if not isinstance(data, dict):
        return {"success": False, "error": "ESTIMATE_RESULT_NOT_DICT"}

    excel = str(data.get("excel_path") or data.get("xlsx_path") or data.get("artifact_path") or "")
    links = {}
    for l in _rgc2_links(data):
        links["existing_" + str(len(links) + 1)] = l

    pdf = ""
    if excel and _rgc2_os.path.exists(excel):
        try:
            pdf = _rgc2_make_pdf_stub(excel, task_id)
        except Exception as e:
            data["pdf_error"] = str(e)

        try:
            from core.artifact_upload_guard import upload_many_or_fail
            files = [{"path": excel, "kind": "estimate_xlsx"}]
            if pdf and _rgc2_os.path.exists(pdf):
                files.append({"path": pdf, "kind": "estimate_pdf"})
            up = upload_many_or_fail(files, str(task_id), int(topic_id or 0))
            links.update(up.get("links") or {})
            data["upload_result"] = up
        except Exception as e:
            data["upload_error"] = str(e)

        if prefer_sheets:
            try:
                from core.sheets_generator import create_google_sheet
                from openpyxl import load_workbook
                wb = load_workbook(excel, data_only=False)
                ws = wb.active
                rows = [[cell.value for cell in row] for row in ws.iter_rows()]
                wb.close()
                sl = create_google_sheet("Estimate_" + str(task_id)[:8], rows, int(topic_id or 0), str(task_id))
                if sl:
                    links["google_sheet"] = sl
                    data["google_sheet_link"] = sl
            except Exception as e:
                data["google_sheet_error"] = str(e)

    if links:
        data["links"] = {**(data.get("links") or {}), **links} if isinstance(data.get("links"), dict) else links

    first = data.get("google_sheet_link") or _rgc2_best_link(data)
    if first:
        data["drive_link"] = first
        data["success"] = True
        data["artifact_path"] = excel or data.get("artifact_path")
        if pdf:
            extras = data.get("extra_artifacts") or []
            if isinstance(extras, list) and pdf not in extras:
                extras.append(pdf)
            data["extra_artifacts"] = extras
    else:
        data["success"] = False
        data["error"] = data.get("error") or "ESTIMATE_NO_LINK_NO_SUCCESS_V1:NO_DRIVE_TELEGRAM_OR_RETRY_LINK"

    vr = validate_estimate_result(data, task_id=str(task_id))
    data["estimate_validator"] = vr
    if not vr.get("ok"):
        data["success"] = False
        data["validator_reason"] = vr.get("reason")
    return data

async def process_estimate_to_excel(file_path: str, task_id: str, topic_id: int):
    data = await _rgc2_orig_excel(file_path, task_id, topic_id)
    return _rgc2_finalize(data, task_id, topic_id, prefer_sheets=False)

async def process_estimate_to_sheets(file_path: str, task_id: str, topic_id: int):
    try:
        data = await _rgc2_orig_sheets(file_path, task_id, topic_id)
    except Exception:
        data = await _rgc2_orig_excel(file_path, task_id, topic_id)
    return _rgc2_finalize(data, task_id, topic_id, prefer_sheets=True)

async def generate_estimate_from_text(raw_input: str, task_id: str, topic_id: int = 0, chat_id: str = ""):
    ctx = _rgc2_resolve_task_context(str(task_id), int(topic_id or 0))
    if not chat_id:
        chat_id = ctx.get("chat_id") or ""
    topic_id = int(ctx.get("topic_id") or topic_id or 0)

    if _rgc2_has_llm_arithmetic(raw_input):
        try:
            logger.warning("ESTIMATE_NO_LLM_CALC_GUARD_V1_INPUT_ARITHMETIC task=%s", task_id)
        except Exception:
            pass

    if chat_id:
        tpl = _rgc2_get_active_estimate_template(str(chat_id), int(topic_id or 0))
        if tpl:
            try:
                from core.sample_template_engine import create_estimate_from_saved_template
                result = await create_estimate_from_saved_template(
                    raw_input=str(raw_input),
                    task_id=str(task_id),
                    chat_id=str(chat_id),
                    topic_id=int(topic_id or 0),
                )
                if isinstance(result, dict) and (result.get("pdf_link") or result.get("xlsx_link") or result.get("drive_link") or result.get("excel_path")):
                    return _rgc2_finalize(result, task_id, topic_id, prefer_sheets=True)
                return {
                    "success": False,
                    "state": "WAITING_CLARIFICATION",
                    "error": "ESTIMATE_TEMPLATE_STRICT_REUSE_V1:TEMPLATE_NOT_APPLICABLE",
                    "result_text": "Активный шаблон сметы найден, но не подошёл к запросу. Уточни состав работ, объёмы или замени шаблон.",
                }
            except Exception as e:
                return {
                    "success": False,
                    "state": "WAITING_CLARIFICATION",
                    "error": "ESTIMATE_TEMPLATE_STRICT_REUSE_V1:ERROR:" + str(e)[:200],
                    "result_text": "Активный шаблон сметы найден, но применить его не удалось. Уточни параметры или замени шаблон.",
                }

    data = await _rgc2_orig_text(raw_input, task_id, topic_id)
    result_text = " ".join(str(data.get(k) or "") for k in ("result", "result_text", "message", "summary")) if isinstance(data, dict) else str(data)
    if _rgc2_has_llm_arithmetic(result_text) and not (isinstance(data, dict) and (data.get("excel_path") or data.get("artifact_path"))):
        return {
            "success": False,
            "error": "ESTIMATE_NO_LLM_CALC_GUARD_V1:TEXT_CALC_WITHOUT_PYTHON_ARTIFACT",
            "result_text": "Смета не принята: обнаружен текстовый расчёт без Python/OpenPyXL артефакта.",
        }
    return _rgc2_finalize(data, task_id, topic_id, prefer_sheets=True)
# === END_ESTIMATE_TEMPLATE_STRICT_REUSE_V1 ===
# === END_ESTIMATE_NO_LLM_CALC_GUARD_V1 ===
# === END_ESTIMATE_RESULT_VALIDATOR_V1 ===
# === END_REAL_GAPS_CLOSE_V2_ESTIMATE ===


# === FINAL_CLOSURE_BLOCKER_FIX_V1_ESTIMATE_XLSX_FORMULAS ===
def create_estimate_xlsx_from_rows(rows, out_path: str, title: str = "Смета") -> str:
    from pathlib import Path
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    from openpyxl.utils import get_column_letter

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"

    ws["A1"] = title
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:F1")

    headers = ["№", "Наименование", "Ед.", "Кол-во", "Цена", "Сумма"]
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=c, value=h)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    start = 4
    safe_rows = rows or []

    for i, r in enumerate(safe_rows, start):
        idx = i - start + 1
        name = r.get("name") or r.get("work") or r.get("item") or ""
        unit = r.get("unit") or ""
        qty = r.get("qty") or r.get("quantity") or 0
        price = r.get("price") or r.get("unit_price") or 0

        try:
            qty = float(str(qty).replace(",", ".").replace(" ", ""))
        except Exception:
            qty = 0

        try:
            price = float(str(price).replace(",", ".").replace(" ", ""))
        except Exception:
            price = 0

        ws.cell(row=i, column=1, value=idx)
        ws.cell(row=i, column=2, value=name)
        ws.cell(row=i, column=3, value=unit)
        ws.cell(row=i, column=4, value=qty)
        ws.cell(row=i, column=5, value=price)
        ws.cell(row=i, column=6, value=f"=D{i}*E{i}")

    total_row = start + len(safe_rows)
    ws.cell(row=total_row, column=5, value="Итого")
    ws.cell(row=total_row, column=5).font = Font(bold=True)
    ws.cell(row=total_row, column=6, value=f"=SUM(F{start}:F{total_row-1})" if safe_rows else "=0")
    ws.cell(row=total_row, column=6).font = Font(bold=True)

    for i, w in enumerate([8, 55, 12, 14, 14, 16], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    wb.save(out)
    return str(out)
# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_ESTIMATE_XLSX_FORMULAS ===


====================================================================================================
END_FILE: core/estimate_engine.py
FILE_CHUNK: 1/1
====================================================================================================
