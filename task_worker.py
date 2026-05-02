
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
                "SELECT * FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=? AND id<>? AND state IN ('IN_PROGRESS','AWAITING_CONFIRMATION','WAITING_CLARIFICATION','NEW') ORDER BY updated_at DESC LIMIT 1",
                (str(chat_id), int(topic_id or 0), str(exclude_task_id)),
            ).fetchone()
        return conn.execute(
            "SELECT * FROM tasks WHERE chat_id=? AND id<>? AND state IN ('IN_PROGRESS','AWAITING_CONFIRMATION','WAITING_CLARIFICATION','NEW') ORDER BY updated_at DESC LIMIT 1",
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
        _cpp_project_words = (
            "проект", "кж", "кд", "км", "кмд", "ар",
            "фундамент", "фундаментн", "плита", "плиты", "плиту",
            "армирован", "арматур", "конструктив", "чертеж", "чертёж",
            "dxf", "dwg", "узел", "узлы", "спецификац"
        )
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

        # === CEP_PROJECT_EXCLUSION_V1 ===
        _cep_project_words = (
            "проект", "кж", "кд", "км", "кмд", "ар",
            "фундамент", "фундаментн", "плита", "плиты", "плиту",
            "армирован", "арматур", "dxf", "dwg", "чертеж", "чертёж", "конструктив",
        )
        _cep_is_create_estimate = (
            any(w in _cep_low for w in _cep_create_words)
            and any(w in _cep_low for w in _cep_estimate_words)
            and not any(w in _cep_low for w in _cep_followup_words)
            and not any(w in _cep_low for w in _cep_project_words)
        )
        # === END_CEP_PROJECT_EXCLUSION_V1 ===

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
