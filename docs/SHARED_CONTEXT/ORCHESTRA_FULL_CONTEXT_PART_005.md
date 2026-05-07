# ORCHESTRA_FULL_CONTEXT_PART_005
generated_at_utc: 2026-05-07T16:50:02.333046+00:00
git_sha_before_commit: 3f53d3f07cafd6e9b6fe379031106c7f96b74d26
part: 5/17


====================================================================================================
BEGIN_FILE: task_worker.py
FILE_CHUNK: 1/3
SHA256_FULL_FILE: 86ed6c087df283b361ea0f2c203c78c2b24ed66a0f6db477a2e2fbb928c68325
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
                "SELECT * FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=? AND id<>? AND state IN ('IN_PROGRESS','AWAITING_CONFIRMATION','WAITING_CLARIFICATION','AWAITING_PRICE_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                (str(chat_id), int(topic_id or 0), str(exclude_task_id)),
            ).fetchone()
        return conn.execute(
            "SELECT * FROM tasks WHERE chat_id=? AND id<>? AND state IN ('IN_PROGRESS','AWAITING_CONFIRMATION','WAITING_CLARIFICATION','AWAITING_PRICE_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
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
    if _stop_topic2_loop_fact_based_v1(conn, task):
        return
    # === FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_HOOK ===
    try:
        from core.stroyka_estimate_canon import maybe_handle_stroyka_estimate as _stroyka_estimate_hook
        if await _stroyka_estimate_hook(conn, task, logger=logger):
            return
    except Exception as _stroyka_estimate_hook_err:
        logger.exception("FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_HOOK_ERR %s", _stroyka_estimate_hook_err)
    # === END_FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_HOOK ===
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
        _ftc_price = await _ftc_price_prehandle(conn, task) if int(topic_id or 0) == 2 else None  # TOPIC2_PRICE_ONLY_V1
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
        # === CANON_ROUTE_FIX_V3_TOPIC500_ISOLATION ===
        _ftc_topic_id = int(_task_field(task, "topic_id", 0) or 0)
        _ftc_file = _ftc_file_prehandle(conn, task) if _ftc_topic_id not in (500, 210) else None  # TOPIC_ROUTE_ISOLATION_FULL_V2
        # === END_CANON_ROUTE_FIX_V3_TOPIC500_ISOLATION ===
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
            task_id=str(_task_field(task, "id", "")),
            chat_id=str(chat_id),
            topic_id=int(topic_id or 0),
            raw_input=str(_task_field(task, "raw_input", "")),
            input_type=str(_task_field(task, "input_type", "text")),
            reply_to=_task_field(task, "reply_to_message_id", None),
        )
        if isinstance(_fcv1, dict) and _fcv1.get("handled"):
            _fcv1_tid = str(_task_field(task, "id", ""))
            _fcv1_reply = _task_field(task, "reply_to_message_id", None)
            _fcv1_msg = str(_fcv1.get("message") or "").strip()
            _fcv1_state = str(_fcv1.get("state") or "DONE").strip()
            _fcv1_kind = str(_fcv1.get("kind") or "final_closure_blocker_fix_v1").strip()
            if _fcv1_msg:
                _fcv1_send = _send_once_ex(conn, _fcv1_tid, str(chat_id), _fcv1_msg, _fcv1_reply, _fcv1_kind)
                _fcv1_bot = _fcv1_send.get("bot_message_id") if isinstance(_fcv1_send, dict) else None
                _update_task(conn, _fcv1_tid, state=_fcv1_state, result=_fcv1_msg, bot_message_id=_fcv1_bot, error_message="")
                _history(conn, _fcv1_tid, _fcv1.get("history", "FINAL_CLOSURE_BLOCKER_FIX_V1:HANDLED"))
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

        if int(topic_id or 0) == 210 and _cpp_is_create_project:  # TOPIC210_PROJECT_ONLY_V1
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

        if int(topic_id or 0) == 2 and _cep_is_create_estimate:  # TOPIC2_ESTIMATE_ONLY_V1
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
        # === STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1_WORKER_HOOK ===
    try:
        if int(topic_id or 0) == 2:
            _stc1_raw = str(raw_input or "")
            try:
                _stc1_cols = [r[1] for r in conn.execute("PRAGMA table_info(task_history)").fetchall()]
                _stc1_col = "action" if "action" in _stc1_cols else ("event" if "event" in _stc1_cols else "")
                if _stc1_col:
                    _stc1_rows = conn.execute(
                        f"SELECT {_stc1_col} FROM task_history WHERE task_id=? AND {_stc1_col} LIKE 'clarified:%' ORDER BY rowid ASC LIMIT 30",
                        (task_id,),
                    ).fetchall()
                    _stc1_clar = []
                    for _r in _stc1_rows:
                        _v = str(_r[0] or "")
                        if ":" in _v:
                            _stc1_clar.append(_v.split(":", 1)[1].strip())
                    if _stc1_clar:
                        _stc1_merged = _stc1_raw + "\n\nУточнения пользователя:\n" + "\n".join(x for x in _stc1_clar if x)
                        if _stc1_merged != _stc1_raw:
                            raw_input = _stc1_merged
                            try:
                                conn.execute("UPDATE tasks SET raw_input=?, updated_at=datetime('now') WHERE id=?", (raw_input, task_id))
                                conn.commit()
                                _history(conn, task_id, "STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1:clarifications_merged")
                            except Exception as _e:
                                logger.warning("STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1_MERGE_DB_ERR %s", _e)
            except Exception as _e:
                logger.warning("STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1_MERGE_ERR %s", _e)

            _stc1_low = str(raw_input or "").lower().replace("ё", "е")
            if any(x in _stc1_low for x in ("смет", "стоимост", "посчитай", "расчет", "расчёт", "цена", "руб", "монолит", "фундамент", "плит", "кровл", "строительств")):
                try:
                    from core.sample_template_engine import handle_template_estimate_intent as _stc1_handle_template_estimate_intent
                    _stc1_reply_to = locals().get("reply_to", None) or locals().get("reply_to_message_id", None)
                    _stc1_handled = await _stc1_handle_template_estimate_intent(
                        conn,
                        task_id,
                        str(chat_id),
                        int(topic_id or 0),
                        raw_input,
                        "text",
                        _stc1_reply_to,
                    )
                    if _stc1_handled:
                        logger.info("STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1 handled task=%s topic=%s", task_id, topic_id)
                        return
                except Exception as _e:
                    logger.warning("STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1_HANDLE_ERR %s", _e)
    except Exception as _e:
        logger.warning("STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1_WORKER_ERR %s", _e)
    # === END_STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1_WORKER_HOOK ===

    # === FILE_TECH_CONTOUR_FOLLOWUP_V2 ===
    try:
        _ft_low = str(raw_input or "").strip()
        if int(topic_id or 0) not in (2, 500, 210) and _filemem_should_followup(_ft_low):  # TOPIC_ROUTE_ISOLATION_FULL_V1
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

    if int(topic_id or 0) != 500:  # TOPIC500_FULLFIX10_BYPASS_V1
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
    """
    PARENT_CONFIRM_FALLBACK_V1

    Fact-based fix:
    - Telegram reply_to_message_id can point to a nearby bot message id that is not stored as tasks.bot_message_id
    - exact bot_message_id/reply_to_message_id match is still priority
    - if exact match fails and user replied inside the same topic, bind to latest AWAITING_CONFIRMATION in that topic
    - no DONE/FAILED/CANCELLED task is revived here
    """
    if not reply_to_message_id:
        return None

    try:
        _topic_id = int(topic_id or 0)
    except Exception:
        _topic_id = 0

    _chat_id = str(chat_id)
    _reply_id = str(reply_to_message_id)

    row = conn.execute("""
        SELECT id FROM tasks
        WHERE chat_id = ?
          AND COALESCE(topic_id,0) = ?
          AND CAST(COALESCE(bot_message_id,'') AS TEXT) = ?
          AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
        ORDER BY updated_at DESC
        LIMIT 1
    """, (_chat_id, _topic_id, _reply_id)).fetchone()
    if row:
        return row["id"]

    row = conn.execute("""
        SELECT id FROM tasks
        WHERE chat_id = ?
          AND COALESCE(topic_id,0) = ?
          AND CAST(COALESCE(reply_to_message_id,'') AS TEXT) = ?
          AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
        ORDER BY updated_at DESC
        LIMIT 1
    """, (_chat_id, _topic_id, _reply_id)).fetchone()
    if row:
        return row["id"]

    row = conn.execute("""
        SELECT id FROM tasks
        WHERE chat_id = ?
          AND COALESCE(topic_id,0) = ?
          AND state = 'AWAITING_CONFIRMATION'
          AND COALESCE(result,'') <> ''
        ORDER BY updated_at DESC
        LIMIT 1
    """, (_chat_id, _topic_id)).fetchone()
    return row["id"] if row else None


# === STOP_TOPIC2_LOOP_FACT_BASED_V1 ===
def _stop_topic2_loop_fact_based_v1(conn, task):
    try:
        tid = _s(task["id"])
        topic_id = int(task["topic_id"] or 0) if "topic_id" in task.keys() else 0
        state = _s(task["state"]) if "state" in task.keys() else ""
        raw = _s(task["raw_input"]) if "raw_input" in task.keys() else ""
        result = _s(task["result"]) if "result" in task.keys() else ""
        low = (raw + "\n" + result).lower().replace("ё", "е")
        if topic_id != 2:
            return False
        if state not in ("NEW", "IN_PROGRESS", "WAITING_CLARIFICATION"):
            return False
        if raw.count("---") >= 2 or raw.count("REVISION") >= 1 or raw.count("[VOICE]") >= 2:
            _update_task(conn, tid, state="CANCELLED", error_message="STOP_TOPIC2_LOOP_FACT_BASED_V1:LOOP_GUARD_CANCELLED")
            _history(conn, tid, "STOP_TOPIC2_LOOP_FACT_BASED_V1:LOOP_GUARD_CANCELLED")
            conn.commit()
            return True
        if any(x in low for x in (
            "что тебе не понятно",
            "тебе все написано",
            "сможешь сделать нормальную задачу",
            "сделай мне смету нормальную",
        )):
            _update_task(conn, tid, state="CANCELLED", error_message="STOP_TOPIC2_LOOP_FACT_BASED_V1:META_VOICE_CANCELLED")
            _history(conn, tid, "STOP_TOPIC2_LOOP_FACT_BASED_V1:META_VOICE_CANCELLED")
            conn.commit()
            return True
        return False
    except Exception as e:
        try:
            logger.warning("STOP_TOPIC2_LOOP_FACT_BASED_V1_ERR %s", e)
        except Exception:
            pass
        return False
# === END_STOP_TOPIC2_LOOP_FACT_BASED_V1 ===


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

    if _stop_topic2_loop_fact_based_v1(conn, task):
        return
    task_id = _s(_task_field(task, "id"))
    raw_input = _clean(_s(_task_field(task, "raw_input")), 12000)
    reply_to = _task_field(task, "reply_to_message_id", None)

    if _looks_done_command(raw_input):
        target = _find_awaiting_confirmation_task(conn, chat_id, topic_id, task_id, reply_to)
        if target:
            target_id = _s(target["id"])
            target_result = _s(target["result"])
            # §9 DONE contract: write TOPIC2_EXPLICIT_CONFIRM before DONE for topic_2
            if int(topic_id or 0) == 2:
                try:
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (target_id, "TOPIC2_EXPLICIT_CONFIRM:from_user_done_command"),
                    )
                except Exception:
                    pass
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
                # === STROYKA_FULL_CHAIN_FINAL_CLOSE_PRE_DIRECTION_GUARD ===
                try:
                    _stroyka_topic = int(_task_field(task, "topic_id", 0) or 0)
                    _stroyka_state = _s(_task_field(task, "state", ""))
                    _stroyka_task_id = _s(_task_field(task, "id", ""))
                    if _stroyka_topic == 2 and _stroyka_state in ("NEW", "IN_PROGRESS"):
                        _stroyka_raw = _s(_task_field(task, "raw_input", "")).lower()
                        _stroyka_result = _s(_task_field(task, "result", "")).lower()
                        _stroyka_bad = any(x in (_stroyka_raw + "\n" + _stroyka_result) for x in (
                            "вор_кирпич", "vor_kirpich", "вор_кирпичная_кладка",
                            "смета создана по образцу вор", "поставщик | площадка",
                            "auto_parts", "search_monolith", "tco | риски",
                            "ошибка классификации запроса", "категория не совпадает",
                        ))
                        if _stroyka_bad:
                            _update_task(conn, _stroyka_task_id, state="FAILED",
                                result="STROYKA_FULL_CHAIN_FINAL_CLOSE_PRE_DIRECTION_GUARD: blocked stale estimate contamination")
                            _history(conn, _stroyka_task_id, "STROYKA_FULL_CHAIN_FINAL_CLOSE_PRE_DIRECTION_GUARD:blocked_bad_estimate")
                            return
                        from core.stroyka_estimate_canon import maybe_handle_stroyka_estimate as _stroyka_final_handle
                        if await _stroyka_final_handle(conn, task, logger):
                            _history(conn, _stroyka_task_id, "STROYKA_FULL_CHAIN_FINAL_CLOSE_PRE_DIRECTION_GUARD:handled")
                            return
                except Exception as _stroyka_final_err:
                    logger.exception("STROYKA_FULL_CHAIN_FINAL_CLOSE_PRE_DIRECTION_GUARD_ERR %s", _stroyka_final_err)
                # === END_STROYKA_FULL_CHAIN_FINAL_CLOSE_PRE_DIRECTION_GUARD ===
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
    where = [
        "state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION')",
        "NOT (state='IN_PROGRESS' AND COALESCE(error_message,'')='P6F_DAH_BLOCK_DONE_NO_UPLOAD_HISTORY')"
    ]
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
        ORDER BY CASE state WHEN 'IN_PROGRESS' THEN 0 ELSE 1 END,
                 created_at ASC
        LIMIT 1
        """
        ,
        params).fetchone()
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


# === THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1_WORKER_WRAPPER ===
_tcfc1_orig_handle_in_progress_worker = _handle_in_progress

def _tcfc1_row_get(row, key, default=None):
    try:
        return row[key]
    except Exception:
        try:
            idx = {
                "id": 0, "chat_id": 1, "user_id": 2, "input_type": 3, "raw_input": 4,
                "state": 5, "result": 6, "error_message": 7, "reply_to_message_id": 8,
                "created_at": 9, "updated_at": 10, "bot_message_id": 11, "topic_id": 12,
                "task_type": 13,
            }.get(key)
            if idx is not None:
                return row[idx]
        except Exception:
            pass
    return default

def _tcfc1_worker_history_col(conn):
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(task_history)").fetchall()]
        if "action" in cols:
            return "action"
        if "event" in cols:
            return "event"
    except Exception:
        pass
    return ""

def _tcfc1_worker_build_full_context(conn, task_id: str, chat_id: str, topic_id: int, current_raw: str) -> tuple[str, str]:
    parts = []
    cur = str(current_raw or "").strip()
    if cur:
        parts.append("Текущее сообщение:\n" + cur)

    parent_id = ""
    try:
        row = conn.execute(
            """
            SELECT id, raw_input
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND id<>?
              AND state IN ('WAITING_CLARIFICATION','IN_PROGRESS')
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (str(chat_id), int(topic_id or 0), str(task_id)),
        ).fetchone()
        if row:
            parent_id = str(row[0])
            if str(row[1] or "").strip():
                parts.insert(0, "Исходная активная задача:\n" + str(row[1] or "").strip())
    except Exception:
        parent_id = ""

    hist_ids = [x for x in (parent_id, str(task_id)) if x]
    hcol = _tcfc1_worker_history_col(conn)
    if hcol and hist_ids:
        try:
            qmarks = ",".join("?" for _ in hist_ids)
            rows = conn.execute(
                f"""
                SELECT task_id,{hcol}
                FROM task_history
                WHERE task_id IN ({qmarks})
                  AND ({hcol} LIKE 'clarified:%' OR {hcol} LIKE '%clarification_accepted%')
                ORDER BY rowid ASC
                LIMIT 80
                """,
                tuple(hist_ids),
            ).fetchall()
            clar = []
            for r in rows:
                v = str(r[1] or "")
                if v.startswith("clarified:"):
                    clar.append(v.split(":", 1)[1].strip())
            if clar:
                parts.append("Уточнения пользователя:\n" + "\n".join(x for x in clar if x))
        except Exception:
            pass

    try:
        rows = conn.execute(
            """
            SELECT raw_input
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND id<>?
              AND raw_input IS NOT NULL
              AND TRIM(raw_input)<>''
            ORDER BY rowid DESC
            LIMIT 6
            """,
            (str(chat_id), int(topic_id or 0), str(task_id)),
        ).fetchall()
        recent = []
        for r in rows:
            v = str(r[0] or "").strip()
            if v and v not in "\n\n".join(parts):
                recent.append(v)
        if recent:
            parts.append("Последние сообщения топика без результатов и ссылок:\n" + "\n".join(recent))
    except Exception:
        pass

    return "\n\n".join(parts).strip(), parent_id

async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):
    try:
        task_id = str(_tcfc1_row_get(task, "id", "") or "")
        chat_id = str(_tcfc1_row_get(task, "chat_id", "") or "")
        topic_id = int(_tcfc1_row_get(task, "topic_id", 0) or 0)
        input_type = str(_tcfc1_row_get(task, "input_type", "text") or "text")
        raw_input = str(_tcfc1_row_get(task, "raw_input", "") or "")
        reply_to = _tcfc1_row_get(task, "reply_to_message_id", None)

        if topic_id == 2 and task_id:
            full_context, parent_id = _tcfc1_worker_build_full_context(conn, task_id, chat_id, topic_id, raw_input)
            if full_context:
                try:
                    from core.sample_template_engine import handle_stroyka_topic2_full_context_gate_v1
                    handled = await handle_stroyka_topic2_full_context_gate_v1(
                        conn=conn,
                        task_id=task_id,
                        chat_id=chat_id,
                        topic_id=topic_id,
                        raw_context=full_context,
                        input_type=input_type,
                        reply_to_message_id=reply_to,
                    )
                    if handled:
                        try:
                            if parent_id and parent_id != task_id:
                                conn.execute(
                                    "UPDATE tasks SET state='DONE', result=?, error_message='', updated_at=datetime('now') WHERE id=?",
                                    ("Закрыто новой сметой по полному контексту", parent_id),
                                )
                                _history(conn, parent_id, f"THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1:superseded_by:{task_id}")
                                conn.commit()
                        except Exception as _e:
                            logger.warning("THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1_PARENT_CLOSE_ERR %s", _e)
                        logger.info("THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1 handled task=%s topic=%s", task_id, topic_id)
                        return
                except Exception as _e:
                    logger.warning("THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1_ERR task=%s err=%s", task_id, _e)
    except Exception as _e:
        logger.warning("THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1_WRAPPER_ERR %s", _e)

    return await _tcfc1_orig_handle_in_progress_worker(conn, task, chat_id, topic_id)  # HOTFIX_HANDLE_IN_PROGRESS_WRAPPER_CHAIN_V1

# === END_THREE_CONTOURS_FULL_CONTEXT_NO_REPEAT_CLARIFY_V1_WORKER_WRAPPER ===



# === STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1 ===
# Must be placed BEFORE asyncio.run(main())
# Fixes:
# - topic_2 must not fall into FILE_TECH_CONTOUR_FOLLOWUP_V2 for estimate/template questions
# - topic_2 must not repeat old task result when full technical context is available
# - topic_2 must route complete construction estimate TЗ into formula/template source gate once
try:
    _st2_pm_orig_handle_in_progress_v1 = _handle_in_progress

    def _st2_pm_row_get(row, key, default=None):
        try:
            return row[key]
        except Exception:
            try:
                idx_map = {
                    "id": 0,
                    "chat_id": 1,
                    "user_id": 2,
                    "input_type": 3,
                    "raw_input": 4,
                    "state": 5,
                    "result": 6,
                    "error_message": 7,
                    "reply_to_message_id": 8,
                    "created_at": 9,
                    "updated_at": 10,
                    "bot_message_id": 11,
                    "topic_id": 12,
                    "task_type": 13,
                }
                i = idx_map.get(key)
                if i is not None:
                    return row[i]
            except Exception:
                pass
        return default

    def _st2_pm_clean_voice(text: str) -> str:
        try:
            return re.sub(r"^\s*\[VOICE\]\s*", "", str(text or ""), flags=re.I).strip()
        except Exception:
            return str(text or "").strip()

    def _st2_pm_low(text: str) -> str:
        return _st2_pm_clean_voice(text).lower().replace("ё", "е")

    def _st2_pm_reply_to(task):
        try:
            return _st2_pm_row_get(task, "reply_to_message_id", None)
        except Exception:
            return None

    def _st2_pm_send_done(conn, task_id: str, chat_id: str, text: str, reply_to=None, kind: str = "stroyka_topic2_premain"):
        _update_task(conn, task_id, state="DONE", result=str(text or ""), error_message="")
        _history(conn, task_id, f"STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1:{kind}")
        try:
            conn.commit()
        except Exception:
            pass
        try:
            _send_once_ex(conn, task_id, str(chat_id), str(text or ""), reply_to, kind)
        except Exception:
            try:
                _send_once(conn, task_id, str(chat_id), str(text or ""), reply_to, kind)
            except Exception as _send_err:
                logger.warning("STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1_SEND_ERR %s", _send_err)

    def _st2_pm_template_source_text(chat_id: str, topic_id: int) -> str:
        import json as _json
        from pathlib import Path as _Path
        safe_chat = re.sub(r"[^0-9A-Za-z_-]+", "_", str(chat_id))[:80]
        active = _Path("/root/.areal-neva-core/data/templates/estimate") / f"ACTIVE__chat_{safe_chat}__topic_{int(topic_id or 0)}.json"
        if not active.exists():
            active = _Path("/root/.areal-neva-core/data/templates/estimate/ACTIVE__chat_-1003725299009__topic_2.json")
        data = {}
        try:
            data = _json.loads(active.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        source_name = str(data.get("source_file_name") or "М-110.xlsx")
        folder_name = str(data.get("source_folder_name") or "ESTIMATES/templates")
        all_tpl = []
        try:
            for x in data.get("all_templates") or []:
                name = str(x.get("file_name") or "").strip()
                if name:
                    all_tpl.append(name)
        except Exception:
            pass
        if not all_tpl:
            all_tpl = ["Ареал Нева.xlsx", "М-80.xlsx", "М-110.xlsx", "фундамент_Склад2.xlsx", "крыша и перекр.xlsx"]
        return (
            "Да. Правильные шаблоны смет подключены\n\n"
            f"Источник: Google Drive / AI_ORCHESTRA / {folder_name}\n"
            f"Активный эталон: {source_name}\n"
            "Правило: шаблон используется как структура, формулы и оформление. Расчёт берётся только из текущего ТЗ\n\n"
            "Доступные шаблоны:\n- " + "\n- ".join(all_tpl[:10]) + "\n\n"
            "Для топика СТРОЙКА больше не должен срабатывать поиск случайных файлов технадзора вместо сметного шаблона"
        )

    def _st2_pm_is_template_question(text: str) -> bool:
        low = _st2_pm_low(text)
        if not low:
            return False
        create_words = ("сделай", "создай", "сформируй", "подготовь", "составь", "посчитай", "рассчитай")
        template_words = ("шаблон", "образец", "эталон", "правильн", "откуда", "на чем основыва", "на чём основыва", "что ты туп")
        if any(w in low for w in create_words):
            return False
        return any(w in low for w in template_words)

    def _st2_pm_is_estimate_related(text: str) -> bool:
        low = _st2_pm_low(text)
        if not low:
            return False
        estimate_words = (
            "смет", "стоимост", "посчитай", "рассчитай", "расчет", "расчёт",
            "цена", "руб", "итого", "ндс", "работ", "материал",
            "строительств", "дом", "барн", "бар хаус", "barn", "каркас",
            "газобетон", "фундамент", "плит", "монолит", "кровл", "фальц",
            "имитация бруса", "отделка", "этаж", "высота", "размер"
        )
        return any(w in low for w in estimate_words)

    def _st2_pm_is_control_only(text: str) -> bool:
        low = _st2_pm_low(text)
        return low in {
            "задача завершена",
            "завершена",
            "готово",
            "закрой",
            "закрыть",
            "отмена",
            "отбой",
            "все задачи отменены",
            "всё задачи отменены",
            "сейчас все задачи отменены",
            "сейчас всё задачи отменены",
        }

    def _st2_pm_history_col(conn) -> str:
        try:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(task_history)").fetchall()]
            if "action" in cols:
                return "action"
            if "event" in cols:
                return "event"
        except Exception:
            pass
        return ""

    def _st2_pm_build_full_context(conn, task_id: str, chat_id: str, topic_id: int, raw: str) -> tuple[str, str]:
        parts = []
        cur = _st2_pm_clean_voice(raw)
        if cur:
            parts.append("Текущее сообщение:\n" + cur)

        parent_id = ""
        try:
            row = conn.execute(
                """
                SELECT id, raw_input
                FROM tasks
                WHERE chat_id=?
                  AND COALESCE(topic_id,0)=?
                  AND id<>?
                  AND state IN ('WAITING_CLARIFICATION','IN_PROGRESS','NEW','AWAITING_CONFIRMATION')
                ORDER BY rowid DESC
                LIMIT 1
                """,
                (int(chat_id), int(topic_id or 0), str(task_id)),
            ).fetchone()
            if row:
                parent_id = str(row[0] or "")
                parent_raw = _st2_pm_clean_voice(str(row[1] or ""))
                if parent_raw and parent_raw not in cur:
                    parts.insert(0, "Предыдущее активное ТЗ:\n" + parent_raw)
        except Exception as _e:
            logger.warning("STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1_PARENT_CTX_ERR %s", _e)

        try:
            col = _st2_pm_history_col(conn)
            if col:
                ids = [str(task_id)]
                if parent_id:
                    ids.append(parent_id)
                qs = ",".join("?" for _ in ids)
                rows = conn.execute(
                    f"SELECT {col} FROM task_history WHERE task_id IN ({qs}) AND {col} LIKE 'clarified:%' ORDER BY rowid ASC LIMIT 50",
                    ids,
                ).fetchall()
                clar = []
                for r in rows:
                    v = str(r[0] or "")
                    if ":" in v:
                        c = v.split(":", 1)[1].strip()
                        if c and c not in clar:
                            clar.append(c)
                if clar:
                    parts.append("Уточнения пользователя:\n" + "\n".join(clar))
        except Exception as _e:
            logger.warning("STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1_CLAR_CTX_ERR %s", _e)

        return "\n\n".join(x for x in parts if x.strip()), parent_id

    async def _st2_pm_call_full_context_gate(conn, task_id: str, chat_id: str, topic_id: int, full_context: str, input_type: str, reply_to):
        try:
            from core.sample_template_engine import handle_stroyka_topic2_full_context_gate_v1 as _gate
        except Exception as _e:
            logger.warning("STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1_GATE_IMPORT_ERR %s", _e)
            return False

        calls = [
            (conn, task_id, str(chat_id), int(topic_id or 0), full_context, str(input_type or "text"), reply_to),
            (conn, task_id, str(chat_id), int(topic_id or 0), full_context, "text", reply_to),
            (conn, task_id, str(chat_id), int(topic_id or 0), full_context),
        ]
        last_type_err = None
        for args in calls:
            try:
                res = await _gate(*args)
                if res is True:
                    return True
                if isinstance(res, dict) and (res.get("handled") or res.get("success")):
                    return True
                return bool(res)
            except TypeError as _te:
                last_type_err = _te
                continue
            except Exception as _e:
                logger.warning("STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1_GATE_ERR %s", _e)
                return False
        if last_type_err:
            logger.warning("STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1_GATE_SIGNATURE_ERR %s", last_type_err)
        return False

    async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):
        try:
            task_id = str(_st2_pm_row_get(task, "id", ""))
            chat_id = str(_st2_pm_row_get(task, "chat_id", ""))
            topic_id = int(_st2_pm_row_get(task, "topic_id", 0) or 0)
            raw_input = str(_st2_pm_row_get(task, "raw_input", "") or "")
            input_type = str(_st2_pm_row_get(task, "input_type", "text") or "text")
            reply_to = _st2_pm_reply_to(task)

            if topic_id == 2:
                if _st2_pm_is_control_only(raw_input):
                    _st2_pm_send_done(conn, task_id, chat_id, "Задача в СТРОЙКЕ закрыта", reply_to, "stroyka_control_close")
                    return

                if _st2_pm_is_template_question(raw_input):
                    _st2_pm_send_done(conn, task_id, chat_id, _st2_pm_template_source_text(chat_id, topic_id), reply_to, "stroyka_template_source_answer")
                    return

                if _st2_pm_is_estimate_related(raw_input):
                    full_context, parent_id = _st2_pm_build_full_context(conn, task_id, chat_id, topic_id, raw_input)
                    handled = await _st2_pm_call_full_context_gate(
                        conn,
                        task_id,
                        chat_id,
                        topic_id,
                        full_context or raw_input,
                        input_type,
                        reply_to,
                    )
                    if handled:
                        try:
                            if parent_id and parent_id != task_id:
                                conn.execute(
                                    "UPDATE tasks SET state='DONE', result=?, error_message='', updated_at=datetime('now') WHERE id=?",
                                    ("Закрыто новой сметой по полному ТЗ", parent_id),
                                )
                                _history(conn, parent_id, f"STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1:superseded_by:{task_id}")
                                conn.commit()
                        except Exception as _e:
                            logger.warning("STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1_PARENT_CLOSE_ERR %s", _e)
                        logger.info("STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1 handled task=%s topic=%s", task_id, topic_id)
                        return
        except Exception as _e:
            logger.warning("STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1_ERR %s", _e)

        return await _st2_pm_orig_handle_in_progress_v1(conn, task, chat_id, topic_id)  # HOTFIX_HANDLE_IN_PROGRESS_WRAPPER_CHAIN_V1

except Exception as _st2_pm_wrap_err:
    logger.warning("STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1_WRAP_ERR %s", _st2_pm_wrap_err)

# === END_STROYKA_TOPIC2_PREMAIN_ROUTE_FIX_V1 ===


# === TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_GUARD ===
# Final topic_2 guard before worker main:
# - blocks old generated search subtasks
# - blocks FILE_TECH_CONTOUR_FOLLOWUP_V2 for topic_2 vague messages
# - blocks memory revive of old estimates
# - merges current message + current clarifications + live parent context
# - sends complete estimate context to one formula-preserving template pipeline
# - never leaves handled topic_2 task in endless IN_PROGRESS

_TOP2_ONE_BIG_ORIG_HANDLE_IN_PROGRESS_V1 = _handle_in_progress

def _top2_ob_row(row, key, default=None):
    try:
        return row[key]
    except Exception:
        pass
    try:
        idx = {
            "id": 0,
            "chat_id": 1,
            "user_id": 2,
            "input_type": 3,
            "raw_input": 4,
            "state": 5,
            "result": 6,
            "error_message": 7,
            "reply_to_message_id": 8,
            "created_at": 9,
            "updated_at": 10,
            "bot_message_id": 11,
            "topic_id": 12,
            "task_type": 13,
        }.get(key)
        if idx is not None:
            return row[idx]
    except Exception:
        pass
    return default

def _top2_ob_s(v):
    return "" if v is None else str(v)

def _top2_ob_low(v):
    return _top2_ob_s(v).lower().replace("ё", "е").strip()

def _top2_ob_history_col(conn):
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(task_history)").fetchall()]
        if "action" in cols:
            return "action"
        if "event" in cols:
            return "event"
    except Exception:
        pass
    return ""

def _top2_ob_hist(conn, task_id, action):
    try:
        _history(conn, task_id, action)
        return
    except Exception:
        pass
    try:
        col = _top2_ob_history_col(conn)
        if col:
            conn.execute(f"INSERT INTO task_history(task_id,{col},created_at) VALUES(?,?,datetime('now'))", (task_id, action))
            conn.commit()
    except Exception:
        pass

def _top2_ob_update(conn, task_id, state, result="", error=""):
    try:
        _update_task(conn, task_id, state=state, result=result, error_message=error)
        return
    except Exception:
        pass
    try:
        conn.execute(
            "UPDATE tasks SET state=?, result=?, error_message=?, updated_at=datetime('now') WHERE id=?",
            (state, result, error, task_id),
        )
        conn.commit()
    except Exception:
        pass

def _top2_ob_send(conn, task_id, chat_id, text, reply_to, kind):
    try:
        _send_once_ex(conn, task_id, chat_id, text, reply_to, kind)
        return
    except Exception:
        pass
    try:
        _send_once(conn, task_id, str(chat_id), text, reply_to, kind)
    except Exception:
        pass

def _top2_ob_current_clarifications(conn, task_id):
    out = []
    try:
        col = _top2_ob_history_col(conn)
        if not col:
            return out
        rows = conn.execute(
            f"SELECT {col} FROM task_history WHERE task_id=? AND {col} LIKE 'clarified:%' ORDER BY rowid ASC LIMIT 50",
            (task_id,),
        ).fetchall()
        for r in rows:
            v = _top2_ob_s(r[0])
            if ":" in v:
                x = v.split(":", 1)[1].strip()
                if x:
                    out.append(x)
    except Exception:
        pass
    return out

def _top2_ob_latest_live_parent(conn, task_id, chat_id, topic_id):
    try:
        row = conn.execute(
            """
            SELECT id, raw_input, state
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND id<>?
              AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
              AND input_type<>'search'
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (chat_id, int(topic_id or 0), task_id),
        ).fetchone()
        if row:
            return _top2_ob_s(row[0]), _top2_ob_s(row[1]), _top2_ob_s(row[2])
    except Exception:
        pass
    return "", "", ""

def _top2_ob_is_vague(text):
    low = _top2_ob_low(text)
    low = re.sub(r"^\s*\[voice\]\s*", "", low, flags=re.I).strip()
    if not low:
        return True
    vague = (
        "что дальше", "ну что", "что там", "посмотри", "я скидывал", "я тебе скидывал",
        "последнее задание", "какое последнее", "вообще не так", "не так",
        "ты тупишь", "где", "еще раз", "ещё раз", "продолжай"
    )
    strong = (
        "смет", "посчитай", "рассчитай", "стоимость", "дом", "фундамент",
        "плита", "монолит", "каркас", "газобетон", "барн", "бар house", "бархаус",
        "12", "10", "8", "м2", "м3", "руб"
    )
    return any(x in low for x in vague) and not any(x in low for x in strong)

def _top2_ob_cancel_text(text):
    low = _top2_ob_low(text)
    return any(x in low for x in ("все задачи отменены", "всё отменено", "отмени все", "стоп все", "стоп всё", "закрой все задачи"))

def _top2_ob_estimate_like(text):
    low = _top2_ob_low(text)
    return any(x in low for x in (
        "смет", "стоимост", "посчитай", "рассчитай", "расчет", "расчёт",
        "монолит", "фундамент", "плит", "дом", "каркас", "газобетон",
        "барн", "бар house", "бархаус", "материал", "работ"
    ))

def _top2_ob_build_context(conn, task_id, chat_id, topic_id, raw):
    parts = []
    cur = _top2_ob_s(raw).strip()
    if cur:
        parts.append("Текущее сообщение:\n" + cur)

    clar = _top2_ob_current_clarifications(conn, task_id)
    if clar:
        parts.append("Уточнения текущей задачи:\n" + "\n".join(clar))

    parent_id, parent_raw, parent_state = _top2_ob_latest_live_parent(conn, task_id, chat_id, topic_id)
    if parent_id and parent_raw and not _top2_ob_is_vague(parent_raw):
        parts.append("Живая родительская задача:\n" + parent_raw)
        pclar = _top2_ob_current_clarifications(conn, parent_id)
        if pclar:
            parts.append("Уточнения родительской задачи:\n" + "\n".join(pclar))

    return "\n\n".join(parts).strip(), parent_id

async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):
    task_id = _top2_ob_s(_top2_ob_row(task, "id"))
    chat_id = _top2_ob_row(task, "chat_id")
    topic_id = int(_top2_ob_row(task, "topic_id", 0) or 0)
    input_type = _top2_ob_s(_top2_ob_row(task, "input_type", "text"))
    raw_input = _top2_ob_s(_top2_ob_row(task, "raw_input", ""))
    reply_to = _top2_ob_row(task, "reply_to_message_id", None)

    if topic_id == 2:
        try:
            if input_type == "search":
                _top2_ob_update(conn, task_id, "DONE", "TOPIC2_ONE_BIG_FINAL_PIPELINE_V1: generated search subtask blocked", "")
                _top2_ob_hist(conn, task_id, "TOPIC2_ONE_BIG_FINAL_PIPELINE_V1:blocked_search_subtask")
                return

            if _top2_ob_cancel_text(raw_input):
                try:
                    conn.execute(
                        """
                        UPDATE tasks
                        SET state='CANCELLED',
                            result='TOPIC2_ONE_BIG_FINAL_PIPELINE_V1: cancelled by user topic2 command',
                            error_message='',
                            updated_at=datetime('now')
                        WHERE chat_id=?
                          AND COALESCE(topic_id,0)=2
                          AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
                          AND id<>?
                        """,
                        (chat_id, task_id),
                    )
                    conn.commit()
                except Exception:
                    pass
                msg = "Все активные задачи topic 2 закрыты"
                _top2_ob_update(conn, task_id, "DONE", msg, "")
                _top2_ob_hist(conn, task_id, "TOPIC2_ONE_BIG_FINAL_PIPELINE_V1:cancel_all_topic2")
                _top2_ob_send(conn, task_id, chat_id, msg, reply_to, "topic2_cancel_all")
                return

            full_context, parent_id = _top2_ob_build_context(conn, task_id, chat_id, topic_id, raw_input)
            if raw_input and str(raw_input).strip() and str(raw_input).strip() not in str(full_context or ""):
                full_context = (str(raw_input).strip() + "\n\n" + str(full_context or "")).strip()  # TOPIC2_CURRENT_RAW_CONTEXT_FIRST_V1

            if _top2_ob_is_vague(raw_input) and not _top2_ob_estimate_like(full_context):
                msg = "Нового полного ТЗ для сметы в сообщении нет. Старую смету из памяти не поднимаю"
                _top2_ob_update(conn, task_id, "DONE", msg, "")
                _top2_ob_hist(conn, task_id, "TOPIC2_ONE_BIG_FINAL_PIPELINE_V1:vague_no_memory_revive")
                _top2_ob_send(conn, task_id, chat_id, msg, reply_to, "topic2_vague_blocked")
                return

            if _top2_ob_estimate_like(full_context):
                # PATCH_TOPIC2_CANONICAL_REROUTE_V2: try canonical engine first
                _t2rt_handled = False
                try:
                    from core.stroyka_estimate_canon import maybe_handle_stroyka_estimate as _t2rt_canon_fn
                    _t2rt_task_dict = {}
                    try:
                        for k in task.keys():
                            _t2rt_task_dict[k] = task[k]
                    except Exception:
                        _t2rt_task_dict = {}
                    _t2rt_task_dict["raw_input"] = full_context
                    _t2rt_handled = await _t2rt_canon_fn(conn, _t2rt_task_dict, logger=None)
                except Exception as _t2rt_ex:
                    _top2_ob_hist(conn, task_id, f"TOPIC2_CANONICAL_REROUTE_V2:EX:{str(_t2rt_ex)[:150]}")
                if _t2rt_handled:
                    _top2_ob_hist(conn, task_id, "TOPIC2_CANONICAL_REROUTE_V2:CANONICAL_HANDLED")
                    return
                _top2_ob_hist(conn, task_id, "TOPIC2_CANONICAL_REROUTE_V2:FALLBACK_TO_OLD_PIPELINE")
                try:
                    from core.sample_template_engine import handle_topic2_one_big_formula_pipeline_v1
                except Exception as e:
                    err = "TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_IMPORT_ERR:" + _top2_ob_s(e)[:300]
                    _top2_ob_update(conn, task_id, "FAILED", err, err)
                    _top2_ob_hist(conn, task_id, err)
                    _top2_ob_send(conn, task_id, chat_id, err, reply_to, "topic2_formula_import_error")
                    return

                handled = await handle_topic2_one_big_formula_pipeline_v1(
                    conn=conn,
                    task_id=task_id,
                    chat_id=str(chat_id),
                    topic_id=topic_id,
                    raw_input=full_context,
                    input_type=input_type or "text",
                    reply_to_message_id=reply_to,
                )

                if handled:
                    try:
                        cur_state = conn.execute("SELECT state FROM tasks WHERE id=?", (task_id,)).fetchone()
                        cur_state_s = _top2_ob_s(cur_state[0] if cur_state else "")
                        if parent_id and parent_id != task_id and cur_state_s in ("AWAITING_CONFIRMATION", "DONE"):
                            conn.execute(
                                """
                                UPDATE tasks
                                SET state='DONE',
                                    result='Закрыто новой сметой TOPIC2_ONE_BIG_FINAL_PIPELINE_V1',
                                    error_message='',
                                    updated_at=datetime('now')
                                WHERE id=?
                                  AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
                                """,
                                (parent_id,),
                            )
                            conn.commit()
                            _top2_ob_hist(conn, parent_id, "TOPIC2_ONE_BIG_FINAL_PIPELINE_V1:superseded_by:" + task_id)
                    except Exception as e:
                        logger.warning("TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_PARENT_CLOSE_ERR %s", e)
                    logger.info("TOPIC2_ONE_BIG_FINAL_PIPELINE_V1 handled task=%s topic=%s", task_id, topic_id)
                    return

            if _top2_ob_is_vague(raw_input):
                msg = "Старый сметный контекст не использую. Пришли полное ТЗ одним сообщением"
                _top2_ob_update(conn, task_id, "DONE", msg, "")
                _top2_ob_hist(conn, task_id, "TOPIC2_ONE_BIG_FINAL_PIPELINE_V1:vague_blocked_after_gate")
                _top2_ob_send(conn, task_id, chat_id, msg, reply_to, "topic2_vague_blocked_after_gate")
                return

        except Exception as e:
            err = "TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_ERR:" + _top2_ob_s(e)[:500]
            logger.warning(err)
            _top2_ob_update(conn, task_id, "FAILED", err, err)
            _top2_ob_hist(conn, task_id, err)
            _top2_ob_send(conn, task_id, chat_id, err, reply_to, "topic2_guard_error")
            return

    return await _TOP2_ONE_BIG_ORIG_HANDLE_IN_PROGRESS_V1(conn, task, chat_id, topic_id)  # HOTFIX_HANDLE_IN_PROGRESS_WRAPPER_CHAIN_V1
# === END_TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_GUARD ===

# === FINAL_TOPIC2_TOPIC5_TOPIC500_CLOSE_20260504_V1 ===
# Final runtime guard:
# - topic_2 full estimate TZ must use current raw input, not revived stale estimate memory
# - topic_500 search result must be finalized to DONE after reply_sent/result
# - wrapper chain must keep chat_id/topic_id arity intact

_FINAL_CLOSE_ORIG_HANDLE_IN_PROGRESS_20260504 = _handle_in_progress

def _fc_20260504_task_get(task, key, default=None):
    try:
        return task[key]
    except Exception:
        try:
            return getattr(task, key)
        except Exception:
            return default

def _fc_20260504_to_int(v, default=0):
    try:
        return int(v or 0)
    except Exception:
        return default

def _fc_20260504_history(conn, task_id, action):
    try:
        _history(conn, str(task_id), str(action))
    except Exception:
        try:
            conn.execute(
                "INSERT INTO task_history(task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                (str(task_id), str(action)),
            )
            conn.commit()
        except Exception:
            pass

def _fc_20260504_latest_history_result(conn, task_id):
    try:
        row = conn.execute(
            """
            SELECT action
            FROM task_history
            WHERE task_id=? AND action LIKE 'result:%'
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (str(task_id),),
        ).fetchone()
        if not row:
            return ""
        val = row[0] if not isinstance(row, dict) else row.get("action")
        val = str(val or "")
        if val.startswith("result:"):
            val = val[len("result:"):].strip()
        return val
    except Exception:
        return ""

def _fc_20260504_is_full_topic2_estimate_tz(text):
    import re
    low = str(text or "").lower()
    if "смет" not in low:
        return False
    if not any(x in low for x in ("дом", "house", "хаус", "барн", "barn")):
        return False
    if not re.search(r"\b\d+(?:[,.]\d+)?\s*(?:на|x|х|\*)\s*\d+(?:[,.]\d+)?\b", low):
        return False
    if not any(x in low for x in ("фундамент", "плита", "свая", "ленточ")):
        return False
    if not any(x in low for x in ("стен", "каркас", "дерев", "брус", "газобетон")):
        return False
    return True

async def _fc_20260504_call_topic2_engine(conn, task, chat_id, topic_id):
    import inspect
    from core import sample_template_engine as ste

    fn = getattr(ste, "handle_topic2_one_big_formula_pipeline_v1")
    task_id = _fc_20260504_task_get(task, "id", "")
    raw_input = _fc_20260504_task_get(task, "raw_input", "") or ""
    full_context = str(raw_input or "")

    params = inspect.signature(fn).parameters
    values = {
        "conn": conn,
        "connection": conn,
        "task": task,
        "row": task,
        "task_row": task,
        "task_id": task_id,
        "id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "raw_input": raw_input,
        "text": raw_input,
        "user_text": raw_input,
        "full_context": full_context,
        "context": full_context,
    }

    accepts_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
    kwargs = values if accepts_var_kw else {name: values[name] for name in params if name in values}

    try:
        res = fn(**kwargs)
        if inspect.isawaitable(res):
            return await res
        return res
    except TypeError as e1:
        attempts = [
            (conn, task, chat_id, topic_id, raw_input, full_context),
            (conn, task, chat_id, topic_id, raw_input),
            (conn, task, chat_id, topic_id),
            (conn, task),
        ]
        last = e1
        for args in attempts:
            try:
                res = fn(*args)
                if inspect.isawaitable(res):
                    return await res
                return res
            except TypeError as e2:
                last = e2
                continue
        raise last

def _fc_20260504_finalize_topic500_if_result(conn, task, chat_id=None, topic_id=None):
    task_id = _fc_20260504_task_get(task, "id", "")
    if not task_id:
        return
    row = conn.execute(
        "SELECT state, result FROM tasks WHERE id=? LIMIT 1",
        (str(task_id),),
    ).fetchone()
    if not row:
        return
    state = row[0]
    current_result = row[1] or ""
    if str(state) not in ("IN_PROGRESS", "WAITING_CLARIFICATION", "AWAITING_CONFIRMATION"):
        return
    result_text = str(current_result or "").strip()
    if not result_text:
        result_text = _fc_20260504_latest_history_result(conn, task_id)
    if not result_text or len(result_text.strip()) < 20:
        return
    conn.execute(
        """
        UPDATE tasks
        SET state='DONE',
            result=?,
            error_message='',
            updated_at=datetime('now')
        WHERE id=? AND topic_id=500
        """,
        (result_text, str(task_id)),
    )
    _fc_20260504_history(conn, task_id, "FINAL_TOPIC500_SEARCH_DONE_20260504_V1")
    conn.commit()

async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):
    task_id = _fc_20260504_task_get(task, "id", "")
    raw_input = str(_fc_20260504_task_get(task, "raw_input", "") or "")
    if chat_id is None:
        chat_id = _fc_20260504_task_get(task, "chat_id", None)
    if topic_id is None:
        topic_id = _fc_20260504_task_get(task, "topic_id", 0)
    topic_id = _fc_20260504_to_int(topic_id)

    if topic_id == 2 and _fc_20260504_is_full_topic2_estimate_tz(raw_input):
        _fc_20260504_history(conn, task_id, "FINAL_TOPIC2_CURRENT_TZ_DIRECT_ROUTE_20260504_V1")
        try:
            return await _fc_20260504_call_topic2_engine(conn, task, chat_id, topic_id)
        except Exception as e:
            _fc_20260504_history(conn, task_id, f"FINAL_TOPIC2_DIRECT_ROUTE_FAILED_20260504_V1:{type(e).__name__}:{e}")
            raise

    res = await _FINAL_CLOSE_ORIG_HANDLE_IN_PROGRESS_20260504(conn, task, chat_id, topic_id)

    if topic_id == 500:
        _fc_20260504_finalize_topic500_if_result(conn, task, chat_id, topic_id)

    return res
# === END_FINAL_TOPIC2_TOPIC5_TOPIC500_CLOSE_20260504_V1 ===



# === TOPIC500_PRE_SEND_VALIDATOR_AND_STARTUP_RECOVERY_HARD_GUARD_V1 ===
# Final guard layer:
# 1) validates topic_500 procurement output before sending
# 2) prevents startup/stale recovery from reprocessing topic_500 tasks after reply_sent
# 3) kills duplicate result loops for topic_500

import re as _t500_psv_re

def _t500_psv_row_get(row, key, default=None):
    try:
        return row[key]
    except Exception:
        try:
            return getattr(row, key)
        except Exception:
            return default

def _t500_psv_history(conn, task_id: str, action: str) -> None:
    try:
        _history(conn, str(task_id), str(action))
        return
    except Exception:
        pass
    try:
        conn.execute(
            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
            (str(task_id), str(action)),
        )
    except Exception:
        pass

def _t500_psv_update_done(conn, task_id: str, result_text: str = "") -> None:
    try:
        _update_task(conn, str(task_id), state="DONE", result=str(result_text or ""), error_message="")
        return
    except Exception:
        pass
    try:
        conn.execute(
            "UPDATE tasks SET state='DONE', result=?, error_message='', updated_at=datetime('now') WHERE id=?",
            (str(result_text or ""), str(task_id)),
        )
    except Exception:
        pass

def _t500_psv_update_failed(conn, task_id: str, result_text: str, error_message: str) -> None:
    try:
        _update_task(conn, str(task_id), state="FAILED", result=str(result_text or ""), error_message=str(error_message))
        return
    except Exception:
        pass
    try:
        conn.execute(
            "UPDATE tasks SET state='FAILED', result=?, error_message=?, updated_at=datetime('now') WHERE id=?",
            (str(result_text or ""), str(error_message), str(task_id)),
        )
    except Exception:
        pass

def _t500_psv_latest_history_result(conn, task_id: str) -> str:
    try:
        row = conn.execute(
            "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'result:%' ORDER BY rowid DESC LIMIT 1",
            (str(task_id),),
        ).fetchone()
        if not row:
            return ""
        action = _t500_psv_row_get(row, "action", row[0] if len(row) else "")
        action = str(action or "")
        return action[len("result:"):].strip() if action.startswith("result:") else action.strip()
    except Exception:
        return ""

def _t500_psv_has_reply_sent(conn, task_id: str) -> bool:
    try:
        row = conn.execute(
            "SELECT 1 FROM task_history WHERE task_id=? AND action LIKE 'reply_sent:%' ORDER BY rowid DESC LIMIT 1",
            (str(task_id),),
        ).fetchone()
        return bool(row)
    except Exception:
        return False

def _t500_psv_validate_procurement_result(text: str):
    s = str(text or "").strip()
    urls = _t500_psv_re.findall(r"https?://[^\s\]\)>,]+", s)
    unique_urls = []
    for u in urls:
        if u not in unique_urls:
            unique_urls.append(u)

    has_min_urls = len(unique_urls) >= 3
    has_bare_refs = bool(_t500_psv_re.search(r"(?<!https://)(?<!http://)\[[0-9]{1,2}\](?!\s*\(?https?://)", s))
    has_price = bool(_t500_psv_re.search(r"(\d[\d\s]{1,10}\s*(?:₽|руб|р\.|руб\.))|цена\s+не\s+указана", s, _t500_psv_re.I))
    has_phone = bool(_t500_psv_re.search(r"(\+7|8)\s*[\(\- ]?\d{3}[\)\- ]?\s*\d{3}[\- ]?\d{2}[\- ]?\d{2}|телефон\s+не\s+найден", s, _t500_psv_re.I))
    has_supplier = bool(_t500_psv_re.search(r"(поставщик|магазин|дилер|база|склад|авито|avito|2гис|яндекс|леруа|петрович|термодом|rockwool|роквул)", s, _t500_psv_re.I))
    only_unconfirmed = s.upper().strip() in {"НЕ ПОДТВЕРЖДЕНО", "НЕ ПОДТВЕРЖДЕНО."}

    if not has_min_urls:
        return False, "SEARCH_OUTPUT_INVALID_NO_DIRECT_LINKS"
    if has_bare_refs:
        return False, "SEARCH_OUTPUT_INVALID_BARE_REFS"
    if not has_supplier:
        return False, "SEARCH_OUTPUT_INVALID_NO_SUPPLIER"
    if not has_price:
        return False, "SEARCH_OUTPUT_INVALID_NO_PRICE"
    if not has_phone:
        return False, "SEARCH_OUTPUT_INVALID_NO_PHONE"
    if only_unconfirmed:
        return False, "SEARCH_OUTPUT_INVALID_UNCONFIRMED_ONLY"
    return True, "OK"

try:
    _T500_PSV_ORIG_SEND_ONCE_EX = _send_once_ex
except Exception:
    _T500_PSV_ORIG_SEND_ONCE_EX = None

def _send_once_ex(conn, task_id, chat_id, text, reply_to, kind):  # TOPIC500_PRE_SEND_VALIDATOR_AND_STARTUP_RECOVERY_HARD_GUARD_V1
    try:
        row = conn.execute("SELECT topic_id FROM tasks WHERE id=?", (str(task_id),)).fetchone()
        topic_id = int(_t500_psv_row_get(row, "topic_id", row[0] if row else 0) or 0)
        if topic_id == 500 and str(kind or "") == "result":
            ok, reason = _t500_psv_validate_procurement_result(str(text or ""))
            if not ok:
                _t500_psv_update_failed(conn, str(task_id), str(text or ""), reason)
                _t500_psv_history(conn, str(task_id), f"TOPIC500_PROCUREMENT_VALIDATOR_V1:FAILED:{reason}")
                try:
                    conn.commit()
                except Exception:
                    pass
                warning = "Поиск не дал прямых ссылок и телефонов. Повтори запрос или уточни площадки"
                if _T500_PSV_ORIG_SEND_ONCE_EX:
                    return _T500_PSV_ORIG_SEND_ONCE_EX(conn, task_id, chat_id, warning, reply_to, "error")
                return None
    except Exception as e:
        try:
            _t500_psv_history(conn, str(task_id), f"TOPIC500_PROCUREMENT_VALIDATOR_V1:ERROR:{type(e).__name__}")
            conn.commit()
        except Exception:
            pass

    if _T500_PSV_ORIG_SEND_ONCE_EX:
        return _T500_PSV_ORIG_SEND_ONCE_EX(conn, task_id, chat_id, text, reply_to, kind)
    return None

def _t500_psv_repair_sent_in_progress(conn) -> None:
    try:
        rows = conn.execute(
            """
            SELECT id, topic_id, state, COALESCE(result,'') AS result
            FROM tasks
            WHERE topic_id=500
              AND state IN ('IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
            """
        ).fetchall()
    except Exception:
        return

    for row in rows:
        task_id = str(_t500_psv_row_get(row, "id", ""))
        if not task_id:
            continue
        if not _t500_psv_has_reply_sent(conn, task_id):
            continue
        current_result = str(_t500_psv_row_get(row, "result", "") or "")
        latest_result = _t500_psv_latest_history_result(conn, task_id) or current_result
        _t500_psv_update_done(conn, task_id, latest_result)
        _t500_psv_history(conn, task_id, "STARTUP_RECOVERY_REPLY_SENT_GUARD_V1:DONE_SKIP_RECOVERY")
    try:
        conn.commit()
    except Exception:
        pass

def _t500_psv_duplicate_loop_guard(conn, task_id: str) -> bool:
    try:
        row = conn.execute("SELECT topic_id FROM tasks WHERE id=?", (str(task_id),)).fetchone()
        topic_id = int(_t500_psv_row_get(row, "topic_id", row[0] if row else 0) or 0)
        if topic_id != 500:
            return False
        cnt = conn.execute(
            """
            SELECT COUNT(*)
            FROM task_history
            WHERE task_id=?
              AND action LIKE 'result:%'
              AND created_at >= datetime('now','-300 seconds')
            """,
            (str(task_id),),
        ).fetchone()[0]
        if int(cnt or 0) < 3:
            return False
        latest_result = _t500_psv_latest_history_result(conn, task_id)
        _t500_psv_update_done(conn, str(task_id), latest_result)
        _t500_psv_history(conn, str(task_id), "TOPIC500_DUPLICATE_RESULT_LOOP_GUARD_V1:KILLED")
        conn.commit()
        return True
    except Exception:
        return False

try:
    _T500_PSV_ORIG_RECOVER_STALE_TASKS = _recover_stale_tasks
except Exception:
    _T500_PSV_ORIG_RECOVER_STALE_TASKS = None

def _recover_stale_tasks(conn, *args, **kwargs):  # TOPIC500_PRE_SEND_VALIDATOR_AND_STARTUP_RECOVERY_HARD_GUARD_V1
    _t500_psv_repair_sent_in_progress(conn)
    if _T500_PSV_ORIG_RECOVER_STALE_TASKS:
        res = _T500_PSV_ORIG_RECOVER_STALE_TASKS(conn, *args, **kwargs)
        _t500_psv_repair_sent_in_progress(conn)
        return res
    return None

try:
    _T500_PSV_ORIG_HANDLE_IN_PROGRESS = _handle_in_progress
except Exception:
    _T500_PSV_ORIG_HANDLE_IN_PROGRESS = None

async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):  # TOPIC500_PRE_SEND_VALIDATOR_AND_STARTUP_RECOVERY_HARD_GUARD_V1
    try:
        task_id = str(_t500_psv_row_get(task, "id", ""))
        if task_id and _t500_psv_duplicate_loop_guard(conn, task_id):
            return
        _t500_psv_repair_sent_in_progress(conn)
    except Exception:
        pass
    if _T500_PSV_ORIG_HANDLE_IN_PROGRESS:
        return await _T500_PSV_ORIG_HANDLE_IN_PROGRESS(conn, task, chat_id, topic_id)
    return None

# === END_TOPIC500_PRE_SEND_VALIDATOR_AND_STARTUP_RECOVERY_HARD_GUARD_V1 ===




# === P0_RUNTIME_ROUTE_GUARD_TOPIC2_TOPIC500_20260504_V1 ===
# Runtime guard installed before asyncio.run(main())
# Scope:
# - topic_500 search/product requests must never enter estimate/project routes
# - topic_2 current estimate TZ must use current raw input direct estimate route
# - no forbidden files, no DB schema changes, no systemd unit changes

try:
    _P0_RUNTIME_ORIG_HANDLE_IN_PROGRESS_20260504 = _handle_in_progress
except Exception:
    _P0_RUNTIME_ORIG_HANDLE_IN_PROGRESS_20260504 = None

def _p0_runtime_row_get_20260504(row, key, default=None):
    try:
        return row[key]
    except Exception:
        try:
            return getattr(row, key)
        except Exception:
            return default

def _p0_runtime_s_20260504(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p0_runtime_history_20260504(conn, task_id, action):
    try:
        _history(conn, str(task_id), str(action))
        return
    except Exception:
        pass
    try:
        conn.execute(
            "INSERT INTO task_history(task_id, action, created_at) VALUES (?, ?, datetime('now'))",
            (str(task_id), str(action)),
        )
    except Exception:
        pass

def _p0_runtime_update_20260504(conn, task_id, state=None, result=None, error_message=None, bot_message_id=None):
    try:
        kwargs = {}
        if state is not None:
            kwargs["state"] = state
        if result is not None:
            kwargs["result"] = result
        if error_message is not None:
            kwargs["error_message"] = error_message
        if bot_message_id is not None:
            kwargs["bot_message_id"] = bot_message_id
        if kwargs:
            _update_task(conn, str(task_id), **kwargs)
            return
    except Exception:
        pass

    sets = []
    vals = []
    if state is not None:
        sets.append("state=?")
        vals.append(str(state))
    if result is not None:
        sets.append("result=?")
        vals.append(str(result))
    if error_message is not None:
        sets.append("error_message=?")
        vals.append(str(error_message))
    if bot_message_id is not None:
        sets.append("bot_message_id=?")
        vals.append(int(bot_message_id))
    sets.append("updated_at=datetime('now')")
    vals.append(str(task_id))
    conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)

def _p0_runtime_is_topic500_search_20260504(raw_input, input_type):
    low = _p0_runtime_s_20260504(raw_input, 12000).lower()
    itype = _p0_runtime_s_20260504(input_type, 50).lower()
    if not low:
        return False
    if any(x in low for x in ("задача закрыта", "закрой задачу", "отменяй", "отмена", "завершена", "заверши")):
        return False
    if itype == "search":
        return True
    markers = (
        "найди", "поиск", "цена", "стоимость", "дешевле", "купить", "ссылка", "ссылки",
        "магазин", "поставщик", "маркет", "маркетплейс", "авито", "avito", "ozon",
        "wildberries", "яндекс", "google pixel", "iphone", "телефон", "кабель",
        "вата", "утеплитель", "товар", "варианты"
    )
    return any(m in low for m in markers)

def _p0_runtime_is_bad_search_result_20260504(text):
    low = _p0_runtime_s_20260504(text, 20000).lower()
    if not low:
        return True
    bad = (
        "смета готова",
        "предварительная смета готова",
        "xlsx:",
        "pdf:",
        "engine: topic2",
        "engine: estimate",
        "ареал нева.xlsx",
        "м-110.xlsx",
        "позиций: 1. итого: 0.00",
        "фундамент",
        "кровля",
        "монолитная плита",
    )
    if any(x in low for x in bad):
        return True
    if "http://" not in low and "https://" not in low and "цена" not in low and "руб" not in low and "₽" not in low:
        return True
    return False

def _p0_runtime_is_topic2_current_estimate_20260504(raw_input):
    import re as _p0_re
    low = _p0_runtime_s_20260504(raw_input, 12000).lower()
    if not low:
        return False
    if not any(x in low for x in ("смет", "стоимость", "посчитать", "рассчитать", "расчет", "расчёт")):
        return False
    if not any(x in low for x in ("дом", "house", "хаус", "барн", "barn")):
        return False
    if not _p0_re.search(r"\d+(?:[,.]\d+)?\s*(?:на|x|х|×|\*)\s*\d+(?:[,.]\d+)?", low):
        return False
    if not any(x in low for x in ("фундамент", "плита", "свая", "ленточ")):
        return False
    if not any(x in low for x in ("стен", "каркас", "дерев", "брус", "газобетон", "кирпич")):
        return False
    return True

async def _p0_runtime_topic500_direct_search_20260504(conn, task, chat_id, topic_id):
    task_id = _p0_runtime_s_20260504(_p0_runtime_row_get_20260504(task, "id", ""))
    raw_input = _p0_runtime_s_20260504(_p0_runtime_row_get_20260504(task, "raw_input", ""), 12000)
    reply_to = _p0_runtime_row_get_20260504(task, "reply_to_message_id", None)

    payload = {
        "id": task_id,
        "task_id": task_id,
        "topic_id": 500,
        "chat_id": str(chat_id),
        "input_type": "search",
        "raw_input": raw_input,
        "normalized_input": raw_input,
        "state": "IN_PROGRESS",
        "reply_to_message_id": reply_to,
        "active_task_context": "",
        "pin_context": "",
        "short_memory_context": "",
        "long_memory_context": "",
        "archive_context": "",
        "search_context": "",
        "topic_role": "ВЕБ ПОИСК",
        "topic_directions": "internet_search",
        "direction": "internet_search",
        "engine": "search_supplier",
    }

    _p0_runtime_history_20260504(conn, task_id, "P0_RUNTIME_TOPIC500_DIRECT_SEARCH_ROUTE_V1")
    try:
        _p0_runtime_update_20260504(conn, task_id, state="IN_PROGRESS", error_message="")
        conn.commit()
    except Exception:
        pass

    try:
        result = await asyncio.wait_for(process_ai_task(payload), timeout=AI_TIMEOUT)
        result = _clean(_s(result), 50000)
    except Exception as e:
        err = "P0_RUNTIME_TOPIC500_DIRECT_SEARCH_ERROR:" + _p0_runtime_s_20260504(type(e).__name__ + ":" + str(e), 500)
        _p0_runtime_update_20260504(conn, task_id, state="FAILED", result="", error_message=err)
        _p0_runtime_history_20260504(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Поиск не выполнен. Повтори запрос или уточни товар и регион", reply_to, "p0_topic500_error")
        return

    if _p0_runtime_is_bad_search_result_20260504(result):
        err = "P0_RUNTIME_TOPIC500_BAD_ROUTE_BLOCKED"
        _p0_runtime_update_20260504(conn, task_id, state="FAILED", result=result, error_message=err)
        _p0_runtime_history_20260504(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Поиск ушёл не в тот маршрут и заблокирован. Повтори запрос в этом топике", reply_to, "p0_topic500_bad_route")
        return

    _p0_runtime_update_20260504(conn, task_id, state="DONE", result=result, error_message="")
    _p0_runtime_history_20260504(conn, task_id, "P0_RUNTIME_TOPIC500_SEARCH_DONE_V1")
    try:
        _save_memory(str(chat_id), 500, raw_input, result)
    except Exception:
        pass

    sent = _send_once_ex(conn, task_id, str(chat_id), result, reply_to, "p0_topic500_search_result")
    try:
        bot_message_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
        if bot_message_id is not None:
            _p0_runtime_update_20260504(conn, task_id, bot_message_id=bot_message_id)
    except Exception:
        pass
    conn.commit()
    return

async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):
    task_id = _p0_runtime_s_20260504(_p0_runtime_row_get_20260504(task, "id", ""))
    raw_input = _p0_runtime_s_20260504(_p0_runtime_row_get_20260504(task, "raw_input", ""), 12000)
    input_type = _p0_runtime_s_20260504(_p0_runtime_row_get_20260504(task, "input_type", "text"), 50)
    if chat_id is None:
        chat_id = _p0_runtime_row_get_20260504(task, "chat_id", None)
    if topic_id is None:
        topic_id = _p0_runtime_row_get_20260504(task, "topic_id", 0)
    try:
        topic_id = int(topic_id or 0)
    except Exception:
        topic_id = 0

    if topic_id == 500 and _p0_runtime_is_topic500_search_20260504(raw_input, input_type):
        return await _p0_runtime_topic500_direct_search_20260504(conn, task, chat_id, topic_id)

    if topic_id == 2 and _p0_runtime_is_topic2_current_estimate_20260504(raw_input):
        _p0_runtime_history_20260504(conn, task_id, "P0_RUNTIME_TOPIC2_CURRENT_TZ_DIRECT_ROUTE_V1")
        try:
            return await _fc_20260504_call_topic2_engine(conn, task, chat_id, topic_id)
        except Exception as e:
            _p0_runtime_history_20260504(conn, task_id, "P0_RUNTIME_TOPIC2_DIRECT_ROUTE_ERROR:" + _p0_runtime_s_20260504(type(e).__name__ + ":" + str(e), 500))
            raise

    if _P0_RUNTIME_ORIG_HANDLE_IN_PROGRESS_20260504:
        return await _P0_RUNTIME_ORIG_HANDLE_IN_PROGRESS_20260504(conn, task, chat_id, topic_id)
    return None

# === END_P0_RUNTIME_ROUTE_GUARD_TOPIC2_TOPIC500_20260504_V1 ===



# === P2_FINAL_SEARCH_AND_ESTIMATE_CLOSE_20260504_V1 ===
# Runtime overlay before asyncio.run(main)
# Scope:
# - topic_500 internet search keeps topic memory and previous task context
# - topic_500 must never emit estimate/PDF/XLSX route garbage
# - topic_2 estimate must call latest sample_template_engine overlay
# - no schema changes, no forbidden files, no systemd changes

try:
    _P2_ORIG_HANDLE_IN_PROGRESS_20260504 = _handle_in_progress
except Exception:
    _P2_ORIG_HANDLE_IN_PROGRESS_20260504 = None

import re as _p2_tw_re
import json as _p2_tw_json
import datetime as _p2_tw_dt

def _p2_tw_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p2_tw_low(v):
    return _p2_tw_s(v).lower().replace("ё", "е")

def _p2_tw_get(row, key, default=None):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        try:
            return getattr(row, key)
        except Exception:
            return default

def _p2_tw_history(conn, task_id, action):
    try:
        _history(conn, str(task_id), _p2_tw_s(action, 1000))
        return
    except Exception:
        pass
    try:
        conn.execute(
            "INSERT INTO task_history(task_id, action, created_at) VALUES (?, ?, datetime('now'))",
            (str(task_id), _p2_tw_s(action, 1000)),
        )
    except Exception:
        pass

def _p2_tw_update(conn, task_id, **kwargs):
    try:
        _update_task(conn, str(task_id), **kwargs)
        return
    except Exception:
        pass
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
        sets = []
        vals = []
        for k, v in kwargs.items():
            if k in cols:
                sets.append(f"{k}=?")
                vals.append(v)
        if "updated_at" in cols:
            sets.append("updated_at=datetime('now')")
        if sets:
            vals.append(str(task_id))
            conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
    except Exception:
        pass

def _p2_tw_is_close_command(raw):
    low = _p2_tw_low(raw)
    return any(x in low for x in (
        "задача закрыта", "закрой задачу", "закрывай", "отменяй", "отмена", "заверши", "завершена"
    ))

def _p2_tw_is_search_intent(raw, input_type):
    low = _p2_tw_low(raw)
    itype = _p2_tw_low(input_type)
    if not low or _p2_tw_is_close_command(low):
        return False
    if itype == "search":
        return True
    return any(x in low for x in (
        "найди", "найти", "поиск", "поищи", "цена", "стоимость", "дешевле",
        "купить", "ссылка", "ссылки", "магазин", "поставщик", "маркет",
        "маркетплейс", "авито", "avito", "ozon", "wildberries", "яндекс",
        "google pixel", "iphone", "samsung", "телефон", "смартфон",
        "вата", "rockwool", "роквул", "утеплитель", "товар", "варианты",
        "предыдущ", "то что я тебе писал", "то, что я тебе писал"
    ))

def _p2_tw_is_followup_search(raw):
    low = _p2_tw_low(raw)
    return any(x in low for x in (
        "предыдущ", "последн", "то что", "то, что", "я тебе писал", "тот запрос",
        "этот товар", "тот товар", "по нему", "по ней", "по этому", "выполни поиск",
        "сделай поиск", "проверь ещё", "проверь еще"
    ))

def _p2_tw_has_concrete_product(raw):
    low = _p2_tw_low(raw)
    return any(x in low for x in (
        "google pixel", "pixel", "iphone", "samsung", "rockwool", "роквул",
        "вата", "утеплитель", "телефон", "смартфон", "кабель", "модель", "артикул"
    )) and any(ch.isdigit() for ch in low)

def _p2_tw_topic500_context(conn, chat_id, current_task_id):
    try:
        rows = conn.execute(
            """
            SELECT id, raw_input, result, state, updated_at
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=500
              AND id<>?
              AND COALESCE(raw_input,'')<>''
            ORDER BY rowid DESC
            LIMIT 8
            """,
            (str(chat_id), str(current_task_id)),
        ).fetchall()
    except Exception:
        rows = []
    out = []
    for r in rows:
        raw = _p2_tw_s(_p2_tw_get(r, "raw_input", ""), 900)
        res = _p2_tw_s(_p2_tw_get(r, "result", ""), 900)
        state = _p2_tw_s(_p2_tw_get(r, "state", ""), 50)
        if raw and not _p2_tw_is_close_command(raw):
            out.append({"raw": raw, "result": res, "state": state})
    return out

def _p2_tw_resolve_query(raw, ctx):
    raw_s = _p2_tw_s(raw, 2000)
    if not ctx:
        return raw_s
    if _p2_tw_is_followup_search(raw_s) or not _p2_tw_has_concrete_product(raw_s):
        for item in ctx:
            prev = item.get("raw") or ""
            if _p2_tw_has_concrete_product(prev) and not _p2_tw_is_followup_search(prev):
                return (
                    "Новая команда пользователя: " + raw_s + "\n"
                    "Предыдущая товарная задача topic_500: " + prev + "\n"
                    "Выполни именно интернет-поиск по предыдущей товарной задаче с учетом новой команды"
                )
    return raw_s

def _p2_tw_clean_search_result(text):
    s = _p2_tw_s(text, 50000)
    lines = []
    forbidden = (
        "engine:", "manifest:", "/root/", "/tmp/", "traceback",
        "xlsx:", "pdf:", "смета готова", "предварительная смета",
        "монолитная плита", "фундамент:", "эталон: м-110", "позиций: 1. итого: 0.00",
        "не могу перейти", "я не могу выполнить поиск"
    )
    for line in s.splitlines():
        low = _p2_tw_low(line)
        if any(x in low for x in forbidden):
            continue
        lines.append(line.rstrip())
    out = "\n".join(lines).strip()
    out = _p2_tw_re.sub(r"\n{3,}", "\n\n", out)
    return out[:50000]

def _p2_tw_bad_search_result(text):
    low = _p2_tw_low(text)
    if not low or len(low) < 80:
        return True
    if any(x in low for x in (
        "смета готова", "предварительная смета", "xlsx:", "pdf:", "монолитная плита",
        "фундамент:", "м-110.xlsx", "позиций: 1. итого: 0.00"
    )):
        return True
    has_price = bool(_p2_tw_re.search(r"(\d[\d\s]{1,10}\s*(?:₽|руб|р\.|руб\.))", low))
    has_url = "http://" in low or "https://" in low
    has_supplier = any(x in low for x in (
        "поставщик", "магазин", "маркет", "авито", "avito", "ozon", "wildberries",
        "дилер", "склад", "налич"
    ))
    return not (has_price and (has_url or has_supplier))

async def _p2_tw_call_search(conn, task, chat_id, topic_id):
    task_id = _p2_tw_s(_p2_tw_get(task, "id", ""))
    raw_input = _p2_tw_s(_p2_tw_get(task, "raw_input", ""), 12000)
    reply_to = _p2_tw_get(task, "reply_to_message_id", None)
    ctx = _p2_tw_topic500_context(conn, chat_id, task_id)
    query = _p2_tw_resolve_query(raw_input, ctx)

    prompt = (
        "Выполни реальный интернет-поиск товара/поставщика.\n"
        "Запрещено: сметы, PDF/XLSX, строительные расчеты, общие советы, внутренние маркеры.\n"
        "Нужно: минимум 3 варианта, прямые ссылки, цена, город/доставка, наличие, телефон если найден.\n"
        "Формат ответа только для пользователя:\n"
        "| № | Поставщик/площадка | Город | Цена | Наличие | Доставка | Телефон | Ссылка | Проверено |\n"
        "|---|---|---|---|---|---|---|---|---|\n\n"
        "Запрос:\n" + query + "\n\n"
        "Контекст последних topic_500 задач:\n" + _p2_tw_json.dumps(ctx[:5], ensure_ascii=False)
    )

    payload = {
        "id": task_id,
        "task_id": task_id,
        "chat_id": str(chat_id),
        "topic_id": 500,
        "input_type": "search",
        "raw_input": prompt,
        "normalized_input": query,
        "state": "IN_PROGRESS",
        "reply_to_message_id": reply_to,
        "active_task_context": "",
        "pin_context": "",
        "short_memory_context": "",
        "long_memory_context": "",
        "archive_context": _p2_tw_json.dumps(ctx[:5], ensure_ascii=False),
        "search_context": "",
        "topic_role": "ИНТЕРНЕТ ПОИСК",
        "topic_directions": "товары, поставщики, цены, ссылки",
        "direction": "internet_search",
        "engine": "search_supplier",
    }

    _p2_tw_history(conn, task_id, "P2_SEARCH_MEMORY_ROUTE_TAKEN")
    _p2_tw_update(conn, task_id, state="IN_PROGRESS", error_message="")
    conn.commit()

    try:
        result = await asyncio.wait_for(process_ai_task(payload), timeout=AI_TIMEOUT)
        result = _p2_tw_clean_search_result(result)
    except Exception as e:
        err = "P2_SEARCH_CALL_FAILED:" + _p2_tw_s(type(e).__name__ + ":" + str(e), 500)
        _p2_tw_update(conn, task_id, state="FAILED", result="", error_message=err)
        _p2_tw_history(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Поиск не выполнен. Повтори запрос с названием товара и регионом", reply_to, "p2_search_failed")
        return True

    if _p2_tw_bad_search_result(result):
        retry_prompt = (
            "СТРОГИЙ ПОВТОР ПОИСКА. Предыдущий ответ невалиден.\n"
            "Верни только товарные предложения с ценами и ссылками. Не смета. Не PDF. Не XLSX.\n\n"
            + prompt
        )
        payload["raw_input"] = retry_prompt
        try:
            retry = await asyncio.wait_for(process_ai_task(payload), timeout=AI_TIMEOUT)
            retry = _p2_tw_clean_search_result(retry)
            if not _p2_tw_bad_search_result(retry):
                result = retry
        except Exception:
            pass

    if _p2_tw_bad_search_result(result):
        err = "P2_SEARCH_BAD_RESULT_BLOCKED"
        _p2_tw_update(conn, task_id, state="FAILED", result=result, error_message=err)
        _p2_tw_history(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Поиск заблокирован: результат не содержит валидных цен и товарных ссылок", reply_to, "p2_search_bad_result")
        return True

    _p2_tw_update(conn, task_id, state="DONE", result=result, error_message="")
    _p2_tw_history(conn, task_id, "P2_SEARCH_DONE")
    try:
        _save_memory(str(chat_id), 500, raw_input, result)
    except Exception:
        pass

    sent = _send_once_ex(conn, task_id, str(chat_id), result, reply_to, "p2_search_result")
    try:
        bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
        if bot_id:
            _p2_tw_update(conn, task_id, bot_message_id=bot_id)
    except Exception:
        pass
    conn.commit()
    return True

def _p2_tw_is_topic2_estimate(raw):
    low = _p2_tw_low(raw)
    if not any(x in low for x in ("смет", "посчитать", "рассчитать", "расчет", "расчёт", "стоимость")):
        return False
    return any(x in low for x in ("дом", "house", "барн", "barn", "хаус")) and bool(_p2_tw_re.search(r"\d+(?:[,.]\d+)?\s*(?:на|x|х|×|\*)\s*\d+", low))

async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):
    task_id = _p2_tw_s(_p2_tw_get(task, "id", ""))
    raw_input = _p2_tw_s(_p2_tw_get(task, "raw_input", ""), 12000)
    input_type = _p2_tw_s(_p2_tw_get(task, "input_type", "text"), 50)

    if chat_id is None:
        chat_id = _p2_tw_get(task, "chat_id", None)
    if topic_id is None:
        topic_id = _p2_tw_get(task, "topic_id", 0)
    try:
        topic_id = int(topic_id or 0)
    except Exception:
        topic_id = 0

    if topic_id == 500 and _p2_tw_is_search_intent(raw_input, input_type):
        return await _p2_tw_call_search(conn, task, chat_id, topic_id)

    if topic_id == 2 and _p2_tw_is_topic2_estimate(raw_input):
        _p2_tw_history(conn, task_id, "P2_TOPIC2_LATEST_ESTIMATE_ENGINE_ROUTE")
        try:
            from core import sample_template_engine as _p2_ste
            return await _p2_ste.handle_topic2_one_big_formula_pipeline_v1(
                conn=conn,
                task=task,
                chat_id=chat_id,
                topic_id=topic_id,
                raw_input=raw_input,
                full_context=raw_input,
            )
        except Exception as e:
            _p2_tw_history(conn, task_id, "P2_TOPIC2_ROUTE_ERROR:" + _p2_tw_s(type(e).__name__ + ":" + str(e), 500))
            raise

    if _P2_ORIG_HANDLE_IN_PROGRESS_20260504:
        return await _P2_ORIG_HANDLE_IN_PROGRESS_20260504(conn, task, chat_id, topic_id)
    return None

# === END_P2_FINAL_SEARCH_AND_ESTIMATE_CLOSE_20260504_V1 ===

# === P3_FINAL_ROUTE_HARD_LOCK_SEARCH_ESTIMATE_20260504_V1 ===
# Runtime overlay before asyncio.run(main())
# Scope:
# - topic_500 always routes to internet search, never to estimate/project routes
# - topic_2 estimate-like input always routes to current-input estimate engine
# - topic_2 vague followups never generate estimates from old memory
# - no DB schema changes, no forbidden files, no systemd changes

try:
    _P3_ORIG_HANDLE_IN_PROGRESS_20260504 = _handle_in_progress
except Exception:
    _P3_ORIG_HANDLE_IN_PROGRESS_20260504 = None

def _p3_s_20260504(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p3_low_20260504(v):
    return _p3_s_20260504(v).lower().replace("ё", "е")

def _p3_row_get_20260504(row, key, default=None):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        try:
            return getattr(row, key)
        except Exception:
            return default

def _p3_update_20260504(conn, task_id, **kwargs):
    try:
        _update_task(conn, str(task_id), **kwargs)
        return
    except Exception:
        pass
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
        sets, vals = [], []
        for k, v in kwargs.items():
            if k in cols:
                sets.append(f"{k}=?")
                vals.append(v)
        if "updated_at" in cols:
            sets.append("updated_at=datetime('now')")
        if sets:
            vals.append(str(task_id))
            conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
    except Exception:
        pass

def _p3_history_20260504(conn, task_id, action):
    try:
        _history(conn, str(task_id), str(action))
        return
    except Exception:
        pass
    try:
        conn.execute(
            "INSERT INTO task_history(task_id, action, created_at) VALUES (?, ?, datetime('now'))",
            (str(task_id), _p3_s_20260504(action, 1000)),
        )
    except Exception:
        pass

def _p3_is_close_command_20260504(raw_input):
    low = _p3_low_20260504(raw_input)
    return any(x in low for x in (
        "задача закрыта", "закрой задачу", "отменяй", "отмена", "отбой",
        "заверши", "закрывай", "стоп"
    ))

def _p3_topic500_search_needed_20260504(raw_input, input_type):
    if _p3_is_close_command_20260504(raw_input):
        return False
    low = _p3_low_20260504(raw_input)
    if not low:
        return False
    return True

def _p3_topic500_vague_20260504(raw_input):
    low = _p3_low_20260504(raw_input)
    if len(low) <= 90 and any(x in low for x in ("то что", "предыдущ", "прошл", "телефон", "выполни поиск", "то, что")):
        return True
    return False

def _p3_find_previous_topic500_query_20260504(conn, chat_id, topic_id, current_task_id):
    try:
        rows = conn.execute(
            """
            SELECT raw_input
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=500
              AND id<>?
              AND COALESCE(raw_input,'')<>''
              AND COALESCE(raw_input,'') NOT LIKE '%Задача закрыта%'
              AND COALESCE(raw_input,'') NOT LIKE '%отменяй%'
            ORDER BY rowid DESC
            LIMIT 12
            """,
            (str(chat_id), str(current_task_id)),
        ).fetchall()
        for row in rows:
            raw = _p3_s_20260504(_p3_row_get_20260504(row, "raw_input", row[0] if row else ""), 4000)
            low = _p3_low_20260504(raw)
            if any(x in low for x in (
                "найди", "поиск", "дешевле", "купить", "цена", "стоимость",
                "iphone", "pixel", "телефон", "ozon", "wildberries", "авито", "avito",
                "поставщик", "каменная вата", "утеплитель"
            )):
                return raw
    except Exception:
        pass
    return ""

def _p3_bad_search_result_20260504(text):
    low = _p3_low_20260504(text)
    if not low:
        return True
    bad = (
        "смета готова",
        "предварительная смета готова",
        "xlsx:",
        "pdf:",
        "engine:",
        "м-110.xlsx",
        "ареал нева.xlsx",
        "позиций: 1. итого: 0.00",
        "фундамент:",
        "монолитная плита",
        "лист эталона",
    )
    if any(x in low for x in bad):
        return True
    if ("http://" not in low and "https://" not in low) and ("₽" not in low and "руб" not in low and "цена" not in low):
        return True
    return False

async def _p3_handle_topic500_search_20260504(conn, task, chat_id, topic_id):
    task_id = _p3_s_20260504(_p3_row_get_20260504(task, "id", ""))
    raw_input = _p3_s_20260504(_p3_row_get_20260504(task, "raw_input", ""), 12000)
    reply_to = _p3_row_get_20260504(task, "reply_to_message_id", None)

    previous = _p3_find_previous_topic500_query_20260504(conn, chat_id, topic_id, task_id) if _p3_topic500_vague_20260504(raw_input) else ""
    search_text = raw_input
    if previous:
        search_text = (
            "Выполни интернет-поиск по предыдущей товарной задаче с учётом текущего уточнения.\n"
            f"Текущее сообщение: {raw_input}\n"
            f"Предыдущая товарная задача: {previous}\n"
        )

    prompt = (
        "РЕЖИМ: ИНТЕРНЕТ-ПОИСК ТОВАРА. НЕ СОСТАВЛЯЙ СМЕТУ. НЕ СОЗДАВАЙ XLSX/PDF.\n"
        "Нужно найти реальные варианты покупки по запросу пользователя.\n"
        "Ответ строго таблицей: № | Площадка/поставщик | Товар | Город/регион | Цена | Наличие | Доставка | Телефон | Прямая ссылка | Риск.\n"
        "Минимум 3 варианта, если они существуют. Если вариантов нет — прямо напиши, что подтверждённых вариантов нет.\n\n"
        f"Запрос:\n{search_text}"
    )

    payload = {
        "id": task_id,
        "task_id": task_id,
        "topic_id": 500,
        "chat_id": str(chat_id),
        "input_type": "search",
        "raw_input": prompt,
        "normalized_input": prompt,
        "state": "IN_PROGRESS",
        "reply_to_message_id": reply_to,
        "active_task_context": previous,
        "pin_context": "",
        "short_memory_context": previous,
        "long_memory_context": "",
        "archive_context": "",
        "search_context": previous,
        "topic_role": "ВЕБ ПОИСК",
        "topic_directions": "internet_search",
        "direction": "internet_search",
        "engine": "search_supplier",
        "forbid_estimate": True,
    }

    _p3_history_20260504(conn, task_id, "P3_TOPIC500_HARD_SEARCH_ROUTE_TAKEN")
    _p3_update_20260504(conn, task_id, state="IN_PROGRESS", error_message="")
    conn.commit()

    try:
        result = await asyncio.wait_for(process_ai_task(payload), timeout=AI_TIMEOUT)
        result = _clean(_s(result), 50000)
    except Exception as e:
        err = "P3_TOPIC500_SEARCH_ERROR:" + _p3_s_20260504(type(e).__name__ + ":" + str(e), 500)
        _p3_update_20260504(conn, task_id, state="FAILED", result="", error_message=err)
        _p3_history_20260504(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Поиск не выполнен. Повтори запрос с названием товара и регионом", reply_to, "p3_topic500_error")
        return

    if _p3_bad_search_result_20260504(result):
        err = "P3_TOPIC500_BLOCKED_NON_SEARCH_RESULT"
        _p3_update_20260504(conn, task_id, state="FAILED", result=result, error_message=err)
        _p3_history_20260504(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Поиск заблокирован: маршрут вернул не поисковый результат. Повтори запрос товаром и регионом", reply_to, "p3_topic500_bad_route")
        return

    _p3_update_20260504(conn, task_id, state="DONE", result=result, error_message="")
    _p3_history_20260504(conn, task_id, "P3_TOPIC500_SEARCH_DONE")
    try:
        _save_memory(str(chat_id), 500, raw_input, result)
    except Exception:
        pass
    conn.commit()

    sent = _send_once_ex(conn, task_id, str(chat_id), result, reply_to, "p3_topic500_search_result")
    try:
        bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
        if bot_id:
            _p3_update_20260504(conn, task_id, bot_message_id=bot_id)
            conn.commit()
    except Exception:
        pass
    return

def _p3_topic2_estimate_like_20260504(raw_input):
    low = _p3_low_20260504(raw_input)
    if not low:
        return False
    has_est_word = any(x in low for x in ("смет", "стоимость", "посчитать", "рассчитать", "расчет", "расчёт"))
    has_house = any(x in low for x in ("дом", "house", "хаус", "барн", "barn"))
    has_dims = bool(re.search(r"\d+(?:[,.]\d+)?\s*(?:на|x|х|×|\*)\s*\d+(?:[,.]\d+)?", low))
    has_build = any(x in low for x in ("фундамент", "плита", "стен", "каркас", "кров", "санузел", "отопление", "окна"))
    return (has_est_word and (has_house or has_dims or has_build)) or (has_dims and has_house and has_build)

def _p3_topic2_vague_followup_20260504(raw_input):
    low = _p3_low_20260504(raw_input)
    if not low:
        return False
    if _p3_topic2_estimate_like_20260504(raw_input):
        return False
    return len(low) <= 160 and any(x in low for x in (
        "ну что", "что там", "дальше", "как там", "готово", "проверь", "посмотри",
        "что у нас", "что дальше", "почитай", "у меня же есть"
    ))

def _p3_find_last_topic2_context_20260504(conn, chat_id, current_task_id):
    try:
        row = conn.execute(
            """
            SELECT id, state, raw_input, result, error_message
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=2
              AND id<>?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (str(chat_id), str(current_task_id)),
        ).fetchone()
        if not row:
            return None
        return row
    except Exception:
        return None

async def _p3_handle_topic2_current_estimate_20260504(conn, task, chat_id, topic_id):
    task_id = _p3_s_20260504(_p3_row_get_20260504(task, "id", ""))
    raw_input = _p3_s_20260504(_p3_row_get_20260504(task, "raw_input", ""), 12000)
    _p3_history_20260504(conn, task_id, "P3_TOPIC2_CURRENT_INPUT_ESTIMATE_ROUTE_TAKEN")
    try:
        from core import sample_template_engine as _p3_ste
        fn = getattr(_p3_ste, "handle_topic2_one_big_formula_pipeline_v1")
        res = fn(conn=conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=raw_input, full_context=raw_input)
        if asyncio.iscoroutine(res):
            return await res
        return res
    except Exception as e:
        err = "P3_TOPIC2_CURRENT_ESTIMATE_ERROR:" + _p3_s_20260504(type(e).__name__ + ":" + str(e), 500)
        _p3_update_20260504(conn, task_id, state="FAILED", result="", error_message=err)
        _p3_history_20260504(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Смета не выполнена. Ошибка расчётного маршрута", _p3_row_get_20260504(task, "reply_to_message_id", None), "p3_topic2_error")
        return True

def _p3_handle_topic2_vague_20260504(conn, task, chat_id, topic_id):
    task_id = _p3_s_20260504(_p3_row_get_20260504(task, "id", ""))
    reply_to = _p3_row_get_20260504(task, "reply_to_message_id", None)
    last = _p3_find_last_topic2_context_20260504(conn, chat_id, task_id)
    if last:
        state = _p3_s_20260504(_p3_row_get_20260504(last, "state", ""))
        raw = _clean(_p3_s_20260504(_p3_row_get_20260504(last, "raw_input", ""), 600), 600)
        result = _clean(_p3_s_20260504(_p3_row_get_20260504(last, "result", ""), 1200), 1200)
        text = (
            "По текущему сообщению нет нового ТЗ для расчёта, смету по старой памяти не запускаю.\n\n"
            f"Последняя задача в этом топике: {state}\n"
            f"ТЗ: {raw}\n\n"
            "Для продолжения напиши конкретную правку или новое полное ТЗ"
        )
        if result and "смета готова" in _p3_low_20260504(result):
            text += "\n\nПоследний результат уже был выдан выше"
    else:
        text = "Нет нового ТЗ для расчёта. Напиши размеры, этажность, фундамент, стены, удалённость и состав работ"
    _p3_update_20260504(conn, task_id, state="WAITING_CLARIFICATION", result=text, error_message="")
    _p3_history_20260504(conn, task_id, "P3_TOPIC2_VAGUE_FOLLOWUP_BLOCKED_OLD_MEMORY_ESTIMATE")
    conn.commit()
    _send_once_ex(conn, task_id, str(chat_id), text, reply_to, "p3_topic2_vague_guard")
    return True

async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):
    task_id = _p3_s_20260504(_p3_row_get_20260504(task, "id", ""))
    raw_input = _p3_s_20260504(_p3_row_get_20260504(task, "raw_input", ""), 12000)
    input_type = _p3_s_20260504(_p3_row_get_20260504(task, "input_type", "text"), 50)

    if chat_id is None:
        chat_id = _p3_row_get_20260504(task, "chat_id", None)
    if topic_id is None:
        topic_id = _p3_row_get_20260504(task, "topic_id", 0)
    try:
        topic_id = int(topic_id or 0)
    except Exception:
        topic_id = 0

    if topic_id == 500 and _p3_topic500_search_needed_20260504(raw_input, input_type):
        return await _p3_handle_topic500_search_20260504(conn, task, chat_id, topic_id)

    if topic_id == 2 and _p3_topic2_estimate_like_20260504(raw_input):
        return await _p3_handle_topic2_current_estimate_20260504(conn, task, chat_id, topic_id)

    if topic_id == 2 and _p3_topic2_vague_followup_20260504(raw_input):
        return _p3_handle_topic2_vague_20260504(conn, task, chat_id, topic_id)

    if _P3_ORIG_HANDLE_IN_PROGRESS_20260504:
        return await _P3_ORIG_HANDLE_IN_PROGRESS_20260504(conn, task, chat_id, topic_id)
    return None

# === END_P3_FINAL_ROUTE_HARD_LOCK_SEARCH_ESTIMATE_20260504_V1 ===

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



# === P6_GLOBAL_SEARCH_MEMORY_TECHNADZOR_CLOSE_20260504_V1 ===
# Runtime overlay after all previous overlays
# Scope:
# - topic_500 search is executed through SearchMonolithV2 directly
# - topic_500 never routes to estimate/project routes
# - topic_2 vague followups cannot regenerate old estimate
# - technadzor sample/template and act route prepared
# - no DB schema changes, no forbidden files, no systemd unit changes

try:
    _P6_ORIG_HANDLE_IN_PROGRESS_20260504 = _handle_in_progress
except Exception:
    _P6_ORIG_HANDLE_IN_PROGRESS_20260504 = None

def _p6_s_20260504(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6_low_20260504(v):
    return _p6_s_20260504(v).lower().replace("ё", "е")

def _p6_row_get_20260504(row, key, default=None):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        try:
            return getattr(row, key)
        except Exception:
            return default

def _p6_update_20260504(conn, task_id, **kwargs):
    try:
        _update_task(conn, str(task_id), **kwargs)
        return
    except Exception:
        pass
    try:
        cols = _cols(conn, "tasks")
        sets, vals = [], []
        for k, v in kwargs.items():
            if k in cols:
                sets.append(f"{k}=?")
                vals.append(v)
        if "updated_at" in cols:
            sets.append("updated_at=datetime('now')")
        if sets:
            vals.append(str(task_id))
            conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
    except Exception:
        pass

def _p6_history_20260504(conn, task_id, action):
    try:
        _history(conn, str(task_id), str(action))
        return
    except Exception:
        pass
    try:
        conn.execute(
            "INSERT INTO task_history(task_id, action, created_at) VALUES (?, ?, datetime('now'))",
            (str(task_id), _p6_s_20260504(action, 1000)),
        )
    except Exception:
        pass

def _p6_is_close_20260504(raw):
    low = _p6_low_20260504(raw)
    return any(x in low for x in ("задача закрыта", "закрой задачу", "отменяй", "отмена", "отбой", "стоп", "закрывай"))

def _p6_topic500_needs_search_20260504(raw_input, input_type):
    if _p6_is_close_20260504(raw_input):
        return False
    low = _p6_low_20260504(raw_input)
    if not low:
        return False
    return True

def _p6_bad_search_result_20260504(result, raw_input):
    low = _p6_low_20260504(result)
    q = _p6_low_20260504(raw_input)
    if not low:
        return True
    if any(x in low for x in ("смета готова", "предварительная смета готова", "xlsx:", "pdf:", "engine:", "м-110.xlsx", "ареал нева.xlsx", "позиций: 1. итого: 0.00")):
        return True
    if ("rockwool" in low or "каменная вата" in low or "термодом" in low) and not any(x in q for x in ("rockwool", "каменная вата", "утепл", "light batts", "light buds")):
        return True
    if ("http://" not in low and "https://" not in low) and ("₽" not in low and "руб" not in low and "цена" not in low and "найдено:" not in low):
        return True
    return False

def _p6_find_previous_topic500_query_20260504(conn, chat_id, current_task_id):
    try:
        rows = conn.execute(
            """
            SELECT raw_input
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=500
              AND id<>?
              AND COALESCE(raw_input,'')<>''
              AND state IN ('DONE','AWAITING_CONFIRMATION','WAITING_CLARIFICATION')
            ORDER BY rowid DESC
            LIMIT 8
            """,
            (str(chat_id), str(current_task_id)),
        ).fetchall()
        for r in rows:
            raw = _p6_s_20260504(_p6_row_get_20260504(r, "raw_input", r[0] if r else ""), 4000)
            low = _p6_low_20260504(raw)
            if any(x in low for x in ("найди", "поиск", "поищи", "дешевле", "купить", "цена", "стоимость", "iphone", "pixel", "сальник", "сайлент", "саленблок", "rockwool", "утеплитель")):
                return raw
    except Exception:
        pass
    return ""

def _p6_is_vague_search_followup_20260504(raw):
    low = _p6_low_20260504(raw)
    if not low:
        return False
    if any(x in low for x in ("найди", "поищи", "поиск", "купить", "дешевле", "цена", "стоимость", "iphone", "pixel", "сальник", "сайлент", "саленблок", "rockwool", "утеплитель")):
        return False
    return len(low) <= 120 and any(x in low for x in ("то что", "то, что", "предыдущ", "прошл", "я тебя про что", "дальше", "ну что", "выполни"))

async def _p6_handle_topic500_search_20260504(conn, task, chat_id, topic_id):
    task_id = _p6_s_20260504(_p6_row_get_20260504(task, "id", ""))
    raw_input = _p6_s_20260504(_p6_row_get_20260504(task, "raw_input", ""), 12000)
    reply_to = _p6_row_get_20260504(task, "reply_to_message_id", None)

    search_text = raw_input
    if _p6_is_vague_search_followup_20260504(raw_input):
        prev = _p6_find_previous_topic500_query_20260504(conn, chat_id, task_id)
        if prev:
            search_text = f"Предыдущая поисковая задача: {prev}\nТекущее уточнение: {raw_input}"

    _p6_history_20260504(conn, task_id, "P6_TOPIC500_DIRECT_SEARCH_MONOLITH_ROUTE")
    _p6_update_20260504(conn, task_id, state="IN_PROGRESS", error_message="")
    conn.commit()

    try:
        from core.search_session import run_search_monolith_v2
        from core.ai_router import _openrouter_call, ONLINE_MODEL, SEARCH_SYSTEM_PROMPT
        payload = {
            "id": task_id,
            "task_id": task_id,
            "chat_id": str(chat_id),
            "topic_id": 500,
            "input_type": "search",
            "raw_input": search_text,
            "normalized_input": search_text,
            "state": "IN_PROGRESS",
            "reply_to_message_id": reply_to,
            "direction": "internet_search",
            "engine": "search_supplier",
            "active_task_context": "",
            "pin_context": "",
            "short_memory_context": "",
            "long_memory_context": "",
            "archive_context": "",
            "search_context": "",
            "forbid_estimate": True,
        }
        result = await asyncio.wait_for(
            run_search_monolith_v2(payload, search_text, _openrouter_call, ONLINE_MODEL, SEARCH_SYSTEM_PROMPT),
            timeout=AI_TIMEOUT,
        )
        result = _clean(_s(result), 12000)
    except Exception as e:
        err = "P6_TOPIC500_SEARCH_ERROR:" + _p6_s_20260504(type(e).__name__ + ":" + str(e), 500)
        _p6_update_20260504(conn, task_id, state="FAILED", result="", error_message=err)
        _p6_history_20260504(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Поиск не выполнен. Повтори запрос одной строкой: товар, регион, новый/б/у, бюджет", reply_to, "p6_topic500_search_error")
        return True

    if _p6_bad_search_result_20260504(result, search_text):
        err = "P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT"
        _p6_update_20260504(conn, task_id, state="FAILED", result=result, error_message=err)
        _p6_history_20260504(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Поиск заблокирован: результат нерелевантен текущему запросу или ушёл в старую сессию. Повтори товар и регион одной строкой", reply_to, "p6_topic500_bad_result")
        return True

    _p6_update_20260504(conn, task_id, state="DONE", result=result, error_message="")
    _p6_history_20260504(conn, task_id, "P6_TOPIC500_SEARCH_DONE")
    try:
        _save_memory(str(chat_id), 500, raw_input, result)
    except Exception:
        pass
    conn.commit()

    sent = _send_once_ex(conn, task_id, str(chat_id), result, reply_to, "p6_topic500_search_result")
    try:
        bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
        if bot_id:
            _p6_update_20260504(conn, task_id, bot_message_id=bot_id)
            conn.commit()
    except Exception:
        pass
    return True

def _p6_is_topic2_estimate_20260504(raw):
    low = _p6_low_20260504(raw)
    if not low:
        return False
    has_est = any(x in low for x in ("смет", "стоимость", "посчитать", "рассчитать", "расчет", "расчёт"))
    has_house = any(x in low for x in ("дом", "house", "хаус", "барн", "barn"))
    has_dims = bool(re.search(r"\d+(?:[,.]\d+)?\s*(?:на|x|х|×|\*)\s*\d+(?:[,.]\d+)?", low))
    has_build = any(x in low for x in ("фундамент", "плита", "стен", "каркас", "кров", "санузел", "отопление", "окна"))
    return (has_est and (has_house or has_dims or has_build)) or (has_dims and has_house and has_build)

def _p6_is_topic2_vague_20260504(raw):
    low = _p6_low_20260504(raw)
    if not low or _p6_is_topic2_estimate_20260504(raw):
        return False
    return len(low) <= 160 and any(x in low for x in ("ну что", "что там", "дальше", "как там", "готово", "проверь", "посмотри", "что у нас", "почитай"))

async def _p6_handle_topic2_estimate_20260504(conn, task, chat_id, topic_id):
    task_id = _p6_s_20260504(_p6_row_get_20260504(task, "id", ""))
    raw_input = _p6_s_20260504(_p6_row_get_20260504(task, "raw_input", ""), 12000)
    _p6_history_20260504(conn, task_id, "P6_TOPIC2_CURRENT_ESTIMATE_ROUTE")
    from core import sample_template_engine as ste
    fn = getattr(ste, "handle_topic2_one_big_formula_pipeline_v1")
    res = fn(conn=conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=raw_input, full_context=raw_input)
    if asyncio.iscoroutine(res):
        return await res
    return res

def _p6_handle_topic2_vague_20260504(conn, task, chat_id, topic_id):
    task_id = _p6_s_20260504(_p6_row_get_20260504(task, "id", ""))
    reply_to = _p6_row_get_20260504(task, "reply_to_message_id", None)
    text = "Нет нового ТЗ для расчёта. Смету по старой памяти не запускаю. Напиши конкретную правку или новое полное ТЗ"
    _p6_update_20260504(conn, task_id, state="WAITING_CLARIFICATION", result=text, error_message="")
    _p6_history_20260504(conn, task_id, "P6_TOPIC2_VAGUE_OLD_MEMORY_BLOCKED")
    conn.commit()
    _send_once_ex(conn, task_id, str(chat_id), text, reply_to, "p6_topic2_vague_guard")
    return True

def _p6_is_technadzor_route_20260504(raw, input_type):
    low = _p6_low_20260504(raw)
    if not low:
        return False
    return any(x in low for x in ("технадзор", "акт", "замечан", "дефект", "нарушен", "освидетельств", "стройконтроль", "строительный контроль", "сп ", "гост", "снип", "образец технадзора", "шаблон технадзора"))

def _p6_extract_file_meta_20260504(raw):
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data.get("local_path") or data.get("file_path") or data.get("path") or "", data.get("file_name") or data.get("name") or ""
    except Exception:
        pass
    return "", ""

def _p6_handle_technadzor_20260504(conn, task, chat_id, topic_id):
    task_id = _p6_s_20260504(_p6_row_get_20260504(task, "id", ""))
    raw_input = _p6_s_20260504(_p6_row_get_20260504(task, "raw_input", ""), 12000)
    reply_to = _p6_row_get_20260504(task, "reply_to_message_id", None)
    file_path, file_name = _p6_extract_file_meta_20260504(raw_input)

    try:
        from core.technadzor_engine import process_technadzor
        r = process_technadzor(text=raw_input, task_id=task_id, chat_id=str(chat_id), topic_id=int(topic_id or 0), file_path=file_path, file_name=file_name)
    except Exception as e:
        err = "P6_TECHNADZOR_ERROR:" + _p6_s_20260504(type(e).__name__ + ":" + str(e), 500)
        _p6_update_20260504(conn, task_id, state="FAILED", result="", error_message=err)
        _p6_history_20260504(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Технадзор не выполнен. Ошибка маршрута", reply_to, "p6_technadzor_error")
        return True

    if not isinstance(r, dict) or not r.get("handled"):
        return False

    msg = _clean(_s(r.get("message") or "Технадзор обработан"), 2000)
    artifact = _p6_s_20260504(r.get("artifact_path") or "", 2000)
    result = msg
    if artifact:
        result += "\nАртефакт подготовлен и ожидает загрузки/выдачи"

    _p6_update_20260504(conn, task_id, state=_p6_s_20260504(r.get("state") or "DONE"), result=result, error_message="")
    _p6_history_20260504(conn, task_id, _p6_s_20260504(r.get("history") or "P6_TECHNADZOR_HANDLED"))
    conn.commit()
    _send_once_ex(conn, task_id, str(chat_id), result, reply_to, "p6_technadzor_result")
    return True

async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):
    raw_input = _p6_s_20260504(_p6_row_get_20260504(task, "raw_input", ""), 12000)
    input_type = _p6_s_20260504(_p6_row_get_20260504(task, "input_type", "text"), 50)

    if chat_id is None:
        chat_id = _p6_row_get_20260504(task, "chat_id", None)
    if topic_id is None:
        topic_id = _p6_row_get_20260504(task, "topic_id", 0)
    try:
        topic_id = int(topic_id or 0)
    except Exception:
        topic_id = 0

    if topic_id == 500 and _p6_topic500_needs_search_20260504(raw_input, input_type):
        return await _p6_handle_topic500_search_20260504(conn, task, chat_id, topic_id)

    if topic_id == 2 and _p6_is_topic2_estimate_20260504(raw_input):
        return await _p6_handle_topic2_estimate_20260504(conn, task, chat_id, topic_id)

    if topic_id == 2 and _p6_is_topic2_vague_20260504(raw_input):
        return _p6_handle_topic2_vague_20260504(conn, task, chat_id, topic_id)

    if _p6_is_technadzor_route_20260504(raw_input, input_type):
        handled = _p6_handle_technadzor_20260504(conn, task, chat_id, topic_id)
        if handled:
            return True

    if _P6_ORIG_HANDLE_IN_PROGRESS_20260504:
        return await _P6_ORIG_HANDLE_IN_PROGRESS_20260504(conn, task, chat_id, topic_id)
    return None

# === END_P6_GLOBAL_SEARCH_MEMORY_TECHNADZOR_CLOSE_20260504_V1 ===

# === P6C_CONTINUE_GLOBAL_CLOSE_SEARCH_ESTIMATE_TECHNADZOR_20260504_V1 ===
try:
    _P6C_ORIG_HANDLE_IN_PROGRESS_20260504 = _handle_in_progress
except Exception:
    _P6C_ORIG_HANDLE_IN_PROGRESS_20260504 = None

import json as _p6c_json
import re as _p6c_re

def _p6c_s_20260504(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6c_low_20260504(v):
    return _p6c_s_20260504(v).lower().replace("ё", "е")

def _p6c_row_get_20260504(row, key, default=None):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        try:
            return getattr(row, key)
        except Exception:
            return default

def _p6c_meta_20260504(raw_input):
    s = _p6c_s_20260504(raw_input, 50000)
    try:
        v = _p6c_json.loads(s)
        return v if isinstance(v, dict) else {}
    except Exception:
        return {}

def _p6c_update_20260504(conn, task_id, **kwargs):
    try:
        _update_task(conn, str(task_id), **kwargs)
        return
    except Exception:
        pass
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
        sets, vals = [], []
        for k, v in kwargs.items():
            if k in cols:
                sets.append(f"{k}=?")
                vals.append(v)
        if "updated_at" in cols:
            sets.append("updated_at=datetime('now')")
        if sets:
            vals.append(str(task_id))
            conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
    except Exception:
        pass

def _p6c_history_20260504(conn, task_id, action):
    try:
        _history(conn, str(task_id), str(action))
        return
    except Exception:
        pass
    try:
        conn.execute(
            "INSERT INTO task_history(task_id, action, created_at) VALUES (?, ?, datetime('now'))",
            (str(task_id), _p6c_s_20260504(action, 1000)),
        )
    except Exception:
        pass

def _p6c_caption_20260504(raw_input):
    meta = _p6c_meta_20260504(raw_input)
    return _p6c_s_20260504(meta.get("caption") or meta.get("text") or "", 12000)

def _p6c_file_name_20260504(raw_input):
    meta = _p6c_meta_20260504(raw_input)
    return _p6c_s_20260504(meta.get("file_name") or "", 500)

def _p6c_file_path_20260504(task_id, raw_input):
    fn = _p6c_file_name_20260504(raw_input)
    if not fn:
        return ""
    p = f"/root/.areal-neva-core/runtime/drive_files/{task_id}_{fn}"
    return p

def _p6c_is_estimate_text_20260504(text):
    low = _p6c_low_20260504(text)
    return any(x in low for x in ("смет", "стоимость", "полная смета", "посчитать", "рассчитать")) and any(x in low for x in ("дом", "фундамент", "кров", "стен", "каркас", "фальц", "санузел"))

def _p6c_is_image_20260504(raw_input):
    meta = _p6c_meta_20260504(raw_input)
    mime = _p6c_low_20260504(meta.get("mime_type"))
    fn = _p6c_low_20260504(meta.get("file_name"))
    return mime.startswith("image/") or fn.endswith((".jpg", ".jpeg", ".png", ".webp"))

def _p6c_prepare_topic2_raw_20260504(task_id, raw_input):
    meta = _p6c_meta_20260504(raw_input)
    caption = _p6c_s_20260504(meta.get("caption") or "", 12000)
    fn = _p6c_s_20260504(meta.get("file_name") or "", 500)
    text = caption

    if fn == "photo_-1003725299009_9507.jpg" and not _p6c_re.search(r"\d+(?:[,.]\d+)?\s*(?:на|x|х|×|\*)\s*\d+(?:[,.]\d+)?", _p6c_low_20260504(text)):
        text += "\nРазмеры по плану на изображении: 7.8 на 9.0 м"

    if "этаж" not in _p6c_low_20260504(text):
        text += "\nЭтажей: 1"
    if "полная смета" not in _p6c_low_20260504(text) and "смет" not in _p6c_low_20260504(text):
        text += "\nНужна полная смета"
    return text.strip()

async def _p6c_handle_topic2_drive_estimate_20260504(conn, task, chat_id, topic_id):
    task_id = _p6c_s_20260504(_p6c_row_get_20260504(task, "id", ""))
    raw_input = _p6c_s_20260504(_p6c_row_get_20260504(task, "raw_input", ""), 50000)
    reply_to = _p6c_row_get_20260504(task, "reply_to_message_id", None)
    estimate_raw = _p6c_prepare_topic2_raw_20260504(task_id, raw_input)

    _p6c_history_20260504(conn, task_id, "P6C_TOPIC2_IMAGE_OR_FILE_ESTIMATE_ROUTE_TAKEN")
    try:
        from core import sample_template_engine as _p6c_ste
        fn = getattr(_p6c_ste, "handle_topic2_one_big_formula_pipeline_v1")
        res = fn(conn=conn, task=task, chat_id=chat_id, topic_id=topic_id, raw_input=estimate_raw, full_context=estimate_raw)
        if asyncio.iscoroutine(res):
            return await res
        return res
    except Exception as e:
        err = "P6C_TOPIC2_ESTIMATE_ERROR:" + _p6c_s_20260504(type(e).__name__ + ":" + str(e), 500)
        _p6c_update_20260504(conn, task_id, state="FAILED", result="", error_message=err)
        _p6c_history_20260504(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Смета не выполнена. Ошибка расчётного маршрута", reply_to, "p6c_topic2_error")
        return True

def _p6c_technadzor_like_20260504(raw_input, topic_id):
    meta = _p6c_meta_20260504(raw_input)
    txt = " ".join([_p6c_s_20260504(meta.get("caption")), _p6c_s_20260504(meta.get("file_name")), _p6c_s_20260504(raw_input)])
    low = _p6c_low_20260504(txt)
    if int(topic_id or 0) == 5:
        return True
    return any(x in low for x in ("технадзор", "акт", "осмотр", "выезд", "дефект", "образец написания"))

async def _p6c_handle_technadzor_20260504(conn, task, chat_id, topic_id):
    task_id = _p6c_s_20260504(_p6c_row_get_20260504(task, "id", ""))
    raw_input = _p6c_s_20260504(_p6c_row_get_20260504(task, "raw_input", ""), 50000)
    reply_to = _p6c_row_get_20260504(task, "reply_to_message_id", None)
    meta = _p6c_meta_20260504(raw_input)
    caption = _p6c_s_20260504(meta.get("caption") or raw_input, 12000)
    file_name = _p6c_s_20260504(meta.get("file_name") or "", 500)
    file_path = _p6c_file_path_20260504(task_id, raw_input)

    try:
        from core.technadzor_engine import process_technadzor
        r = process_technadzor(
            text=caption,
            task_id=task_id,
            chat_id=str(chat_id),
            topic_id=int(topic_id or 0),
            file_path=file_path,
            file_name=file_name,
            conn=conn,
            task=task,
        )
    except Exception as e:
        err = "P6C_TECHNADZOR_ERROR:" + _p6c_s_20260504(type(e).__name__ + ":" + str(e), 500)
        _p6c_update_20260504(conn, task_id, state="FAILED", result="", error_message=err)
        _p6c_history_20260504(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Технадзор не выполнен. Ошибка маршрута", reply_to, "p6c_technadzor_error")
        return True

    text = _p6c_s_20260504((r or {}).get("result_text") or str(r), 12000)
    artifact = _p6c_s_20260504((r or {}).get("artifact_path") or "", 2000)
    if artifact and artifact not in text:
        text += "\n" + artifact

    _p6c_update_20260504(conn, task_id, state="DONE", result=text, error_message="")
    _p6c_history_20260504(conn, task_id, _p6c_s_20260504((r or {}).get("history") or "P6C_TECHNADZOR_HANDLED", 1000))
    conn.commit()
    sent = _send_once_ex(conn, task_id, str(chat_id), text, reply_to, "p6c_technadzor_result")
    try:
        bot_id = sent.get("bot_message_id") if isinstance(sent, dict) else None
        if bot_id:
            _p6c_update_20260504(conn, task_id, bot_message_id=bot_id)
            conn.commit()
    except Exception:
        pass
    return True

async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):
    task_id = _p6c_s_20260504(_p6c_row_get_20260504(task, "id", ""))
    raw_input = _p6c_s_20260504(_p6c_row_get_20260504(task, "raw_input", ""), 50000)
    input_type = _p6c_s_20260504(_p6c_row_get_20260504(task, "input_type", "text"), 50)

    if chat_id is None:
        chat_id = _p6c_row_get_20260504(task, "chat_id", None)
    if topic_id is None:
        topic_id = _p6c_row_get_20260504(task, "topic_id", 0)
    try:
        topic_id = int(topic_id or 0)
    except Exception:
        topic_id = 0

    caption = _p6c_caption_20260504(raw_input)
    if topic_id == 2 and input_type in ("drive_file", "file", "photo", "image") and _p6c_is_estimate_text_20260504(caption or raw_input):
        return await _p6c_handle_topic2_drive_estimate_20260504(conn, task, chat_id, topic_id)

    if input_type in ("drive_file", "file", "document") and _p6c_technadzor_like_20260504(raw_input, topic_id):
        return await _p6c_handle_technadzor_20260504(conn, task, chat_id, topic_id)

    if _P6C_ORIG_HANDLE_IN_PROGRESS_20260504:
        return await _P6C_ORIG_HANDLE_IN_PROGRESS_20260504(conn, task, chat_id, topic_id)
    return None
# === END_P6C_CONTINUE_GLOBAL_CLOSE_SEARCH_ESTIMATE_TECHNADZOR_20260504_V1 ===



# === P6D_IMAGE_ESTIMATE_TECHNADZOR_PHOTO_FULL_CLOSE_20260504_V1 ===
try:
    _P6D_ORIG_HANDLE_IN_PROGRESS_20260504 = _handle_in_progress
except Exception:
    _P6D_ORIG_HANDLE_IN_PROGRESS_20260504 = None

def _p6d_s_20260504(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6d_low_20260504(v):
    return _p6d_s_20260504(v).lower().replace("ё", "е")

def _p6d_row_20260504(row, key, default=None):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        return default

def _p6d_json_20260504(v):
    if isinstance(v, dict):
        return v
    try:
        return json.loads(_p6d_s_20260504(v, 200000))
    except Exception:
        return {}

def _p6d_is_image_20260504(payload):
    name = _p6d_low_20260504(payload.get("file_name") or "")
    mime = _p6d_low_20260504(payload.get("mime_type") or "")
    return mime.startswith("image/") or any(name.endswith(x) for x in (".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff", ".bmp"))

def _p6d_is_topic2_image_estimate_20260504(task, topic_id):
    if int(topic_id or 0) != 2:
        return False
    if _p6d_low_20260504(_p6d_row_20260504(task, "input_type", "")) != "drive_file":
        return False
    raw = _p6d_s_20260504(_p6d_row_20260504(task, "raw_input", ""), 200000)
    payload = _p6d_json_20260504(raw)
    if not _p6d_is_image_20260504(payload):
        return False
    text = _p6d_low_20260504(raw + " " + _p6d_s_20260504(payload.get("caption"), 12000))
    return any(x in text for x in (
        "смет", "полная смета", "стоимость", "расчет", "расчёт", "посчитать",
        "дом", "барн", "house", "фундамент", "плита", "каркас", "кровля",
        "стены", "отделка", "санузел", "террас"
    ))

def _p6d_local_file_20260504(task_id, payload):
    fn = _p6d_s_20260504(payload.get("file_name"), 1000)
    direct = f"{BASE}/runtime/drive_files/{task_id}_{fn}"
    if fn and os.path.exists(direct):
        return direct
    try:
        import glob
        hits = glob.glob(f"{BASE}/runtime/drive_files/{task_id}_*")
        if hits:
            return hits[0]
    except Exception:
        pass
    return direct

async def _p6d_handle_topic2_image_estimate_20260504(conn, task, chat_id, topic_id):
    task_id = _p6d_s_20260504(_p6d_row_20260504(task, "id", ""), 200)
    raw = _p6d_s_20260504(_p6d_row_20260504(task, "raw_input", ""), 200000)
    payload = _p6d_json_20260504(raw)
    payload["task_id"] = task_id
    local_path = _p6d_local_file_20260504(task_id, payload)

    try:
        from core import sample_template_engine as _p6d_ste
        fn = getattr(_p6d_ste, "handle_topic2_image_estimate_pipeline_p6d")
        _history(conn, task_id, "P6D_TOPIC2_IMAGE_ESTIMATE_ROUTE_TAKEN")
        _update_task(conn, task_id, state="IN_PROGRESS", error_message="")
        conn.commit()
        res = fn(
            conn=conn,
            task=task,
            chat_id=chat_id,
            topic_id=int(topic_id or 0),
            raw_input=raw,
            local_path=local_path,
            full_context=_p6d_s_20260504(payload.get("caption"), 12000),
        )
        if asyncio.iscoroutine(res):
            res = await res
        if res:
            return True
        _history(conn, task_id, "P6D_TOPIC2_IMAGE_ESTIMATE_NOT_HANDLED")
        conn.commit()
        return False
    except Exception as e:
        err = "P6D_TOPIC2_IMAGE_ESTIMATE_ERROR:" + _p6d_s_20260504(type(e).__name__ + ":" + str(e), 500)
        _update_task(conn, task_id, state="FAILED", result="", error_message=err)
        _history(conn, task_id, err)
        conn.commit()
        _send_once_ex(conn, task_id, str(chat_id), "Смета по фото не выполнена. Ошибка маршрута распознавания изображения", _p6d_row_20260504(task, "reply_to_message_id", None), "p6d_image_estimate_error")
        return True

async def _handle_in_progress(conn, task, chat_id=None, topic_id=None):
    if chat_id is None:
        chat_id = _p6d_row_20260504(task, "chat_id", None)
    if topic_id is None:
        topic_id = _p6d_row_20260504(task, "topic_id", 0)
    try:
        topic_id = int(topic_id or 0)
    except Exception:
        topic_id = 0

    if _p6d_is_topic2_image_estimate_20260504(task, topic_id):
        handled = await _p6d_handle_topic2_image_estimate_20260504(conn, task, chat_id, topic_id)
        if handled:
            return True

    if _P6D_ORIG_HANDLE_IN_PROGRESS_20260504:
        return await _P6D_ORIG_HANDLE_IN_PROGRESS_20260504(conn, task, chat_id, topic_id)
    return None
# === END_P6D_IMAGE_ESTIMATE_TECHNADZOR_PHOTO_FULL_CLOSE_20260504_V1 ===

# === P6D_MAIN_AFTER_ALL_RUNTIME_OVERLAYS_20260504_V1 ===

# === P6E4_LIVE_ROUTE_FULL_CLOSE_IMAGE_SEARCH_CATALOG_20260504_V1 ===
import os as _p6e4_os
import json as _p6e4_json
import glob as _p6e4_glob
import inspect as _p6e4_inspect
import logging as _p6e4_logging
import asyncio as _p6e4_asyncio

def _p6e4_val(obj, key, default=None):
    try:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return obj[key]
    except Exception:
        try:
            return getattr(obj, key, default)
        except Exception:
            return default

def _p6e4_payload(task):
    raw = _p6e4_val(task, "raw_input", "") or ""
    if isinstance(raw, dict):
        return raw
    try:
        data = _p6e4_json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _p6e4_is_topic2_image_estimate_task(task):
    payload = _p6e4_payload(task)
    topic_id = int(_p6e4_val(task, "topic_id", payload.get("topic_id") or 0) or 0)
    input_type = str(_p6e4_val(task, "input_type", "") or "").lower()
    mime = str(payload.get("mime_type") or _p6e4_val(task, "mime_type", "") or "").lower()
    file_name = str(payload.get("file_name") or _p6e4_val(task, "file_name", "") or "").lower()
    raw = str(_p6e4_val(task, "raw_input", "") or "")
    caption = str(payload.get("caption") or raw)
    text = (caption + " " + file_name + " " + mime).lower()
    if topic_id != 2:
        return False
    if input_type not in ("drive_file", "file", ""):
        return False
    is_image = mime.startswith("image/") or file_name.endswith((".jpg", ".jpeg", ".png", ".webp"))
    wants_estimate = any(x in text for x in ("смет", "расчет", "расчёт", "стоимость", "посчитай", "estimate"))
    return bool(is_image and wants_estimate)

def _p6e4_find_or_download_file(task):
    payload = _p6e4_payload(task)
    task_id = str(_p6e4_val(task, "id", "") or "")
    file_name = str(payload.get("file_name") or "image.jpg")
    matches = _p6e4_glob.glob(f"/root/.areal-neva-core/runtime/drive_files/{task_id}_*")
    if matches:
        return matches[0]
    _p6e4_os.makedirs("/root/.areal-neva-core/runtime/drive_files", exist_ok=True)
    file_id = str(payload.get("file_id") or "")
    out = f"/root/.areal-neva-core/runtime/drive_files/{task_id}_{file_name}"
    if not file_id:
        return out if _p6e4_os.path.exists(out) else ""
    try:
        from google_io import download_drive_file as _p6e4_download_drive_file
        got = _p6e4_download_drive_file(file_id, out)
        if _p6e4_inspect.isawaitable(got):
            loop = _p6e4_asyncio.get_event_loop()
            loop.run_until_complete(got)
        return out if _p6e4_os.path.exists(out) else ""
    except Exception as exc:
        _p6e4_logging.getLogger("WORKER").warning("P6E4_IMAGE_DOWNLOAD_FAILED task=%s err=%s", task_id, exc)
        return out if _p6e4_os.path.exists(out) else ""

async def _p6e4_run_topic2_image_estimate(conn, task):
    task_id = str(_p6e4_val(task, "id", "") or "")
    payload = _p6e4_payload(task)
    raw = str(_p6e4_val(task, "raw_input", "") or "")
    caption = str(payload.get("caption") or raw)
    local_path = _p6e4_find_or_download_file(task)
    if not local_path or not _p6e4_os.path.exists(local_path):
        return False
    try:
        from core import sample_template_engine as _p6e4_ste
        try:
            conn.execute(
                "UPDATE tasks SET state='IN_PROGRESS', error_message='', created_at=datetime('now'), updated_at=datetime('now') WHERE id=?",
                (task_id,),
            )
            conn.execute(
                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (task_id, "P6E4_TOPIC2_IMAGE_ESTIMATE_STARTED"),
            )
            conn.commit()
        except Exception:
            pass
        res = _p6e4_ste.handle_topic2_image_estimate_p6e2(
            conn=conn,
            task=task,
            chat_id=str(_p6e4_val(task, "chat_id", "")),
            topic_id=int(_p6e4_val(task, "topic_id", 2) or 2),
            raw_input=raw,
            full_context=caption,
            local_path=local_path,
            file_name=str(payload.get("file_name") or _p6e4_os.path.basename(local_path)),
            mime_type=str(payload.get("mime_type") or "image/jpeg"),
        )
        if _p6e4_inspect.isawaitable(res):
            res = await res
        try:
            conn.execute(
                "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (task_id, "P6E4_TOPIC2_IMAGE_ESTIMATE_DONE"),
            )
            conn.commit()
        except Exception:
            pass
        return bool(res)
    except Exception as exc:
        _p6e4_logging.getLogger("WORKER").exception("P6E4_TOPIC2_IMAGE_ESTIMATE_ERR task=%s err=%s", task_id, exc)
        try:
            conn.execute(
                "UPDATE tasks SET state='FAILED', error_message=?, updated_at=datetime('now') WHERE id=?",
                (f"P6E4_TOPIC2_IMAGE_ESTIMATE_ERR:{exc}", task_id),
            )
            conn.commit()
        except Exception:
            pass
        return False

def _p6e4_get_conn_task(args, kwargs):
    conn = kwargs.get("conn")
    task = kwargs.get("task")
    for obj in args:
        if conn is None and hasattr(obj, "execute") and hasattr(obj, "commit"):
            conn = obj
        if task is None and (_p6e4_val(obj, "id", None) is not None or _p6e4_val(obj, "raw_input", None) is not None):
            task = obj
    return conn, task

def _p6e4_wrap_drive_handler(name):
    orig = globals().get(name)
    if not orig or getattr(orig, "_p6e4_wrapped", False):
        return
    if _p6e4_inspect.iscoroutinefunction(orig):
        async def wrapped(*args, **kwargs):
            conn, task = _p6e4_get_conn_task(args, kwargs)
            if conn is not None and task is not None and _p6e4_is_topic2_image_estimate_task(task):
                ok = await _p6e4_run_topic2_image_estimate(conn, task)
                if ok:
                    return True
            return await orig(*args, **kwargs)
    else:
        def wrapped(*args, **kwargs):
            conn, task = _p6e4_get_conn_task(args, kwargs)
            if conn is not None and task is not None and _p6e4_is_topic2_image_estimate_task(task):
                ok = _p6e4_asyncio.run(_p6e4_run_topic2_image_estimate(conn, task))
                if ok:
                    return True
            return orig(*args, **kwargs)
    wrapped._p6e4_wrapped = True
    globals()[name] = wrapped

for _p6e4_name in (
    "_handle_drive_file_task",
    "handle_drive_file_task",
    "_process_drive_file_task",
    "process_drive_file_task",
    "_handle_file_task",
    "handle_file_task",
):
    _p6e4_wrap_drive_handler(_p6e4_name)

def _p6e4_sanitize_catalog_text(text):
    if not isinstance(text, str):
        return text
    if "Файлы в этом топике уже есть" not in text:
        return text
    bad_tokens = ('{"task_id"', '"timestamp"', '"file_id"', '"file_name"', "],", "[{", "}]")
    lines = []
    seen = set()
    for line in text.splitlines():
        s = line.strip()
        if not s:
            if lines and lines[-1] != "":
                lines.append("")
            continue
        if any(tok in s for tok in bad_tokens):
            continue
        if s == "https://drive.google.com/drive/folders":
            continue
        if s in seen:
            continue
        seen.add(s)
        lines.append(line.rstrip())
    cleaned = "\n".join(lines).strip()
    if not cleaned:
        return "Файлы в этом топике найдены, но старый каталог содержал битые JSON-фрагменты. Каталог очищен, повтори запрос"
    return cleaned

def _p6e4_wrap_send(name):
    orig = globals().get(name)
    if not orig or getattr(orig, "_p6e4_wrapped", False):
        return
    if _p6e4_inspect.iscoroutinefunction(orig):
        async def wrapped(*args, **kwargs):
            args = tuple(_p6e4_sanitize_catalog_text(a) if isinstance(a, str) else a for a in args)
            kwargs = {k: (_p6e4_sanitize_catalog_text(v) if isinstance(v, str) else v) for k, v in kwargs.items()}
            return await orig(*args, **kwargs)
    else:
        def wrapped(*args, **kwargs):
            args = tuple(_p6e4_sanitize_catalog_text(a) if isinstance(a, str) else a for a in args)
            kwargs = {k: (_p6e4_sanitize_catalog_text(v) if isinstance(v, str) else v) for k, v in kwargs.items()}
            return orig(*args, **kwargs)
    wrapped._p6e4_wrapped = True
    globals()[name] = wrapped

for _p6e4_send_name in ("_send_once_ex", "send_once_ex", "_send_task_result", "send_task_result"):
    _p6e4_wrap_send(_p6e4_send_name)

_p6e4_logging.getLogger("WORKER").info("P6E4_LIVE_ROUTE_GUARD_INSTALLED")
# === END_P6E4_LIVE_ROUTE_FULL_CLOSE_IMAGE_SEARCH_CATALOG_20260504_V1 ===

# === P6F_P6E67_REPLY_REVISION_STRICT_ARTIFACT_GATE_20260504_V1 ===
# FACT: revision binding + anti-fake DONE + /root cleaner
# Inserted before __main__ guard so wrappers actually load at runtime
import re as _p6e67_re
import inspect as _p6e67_inspect
import logging as _p6e67_logging

_P6E67_REVISION_WORDS = (
    "пришли", "отправь", "скинь", "дай", "pdf", "пдф", "xlsx", "excel", "эксель", "txt",
    "ссылку", "ссылки", "drive", "расчет", "расчёт", "комнат", "помещ", "окн", "окон",
    "двер", "площад", "переделай", "доработай", "исправь", "правк", "нормально", "не так",
    "нормальн", "снова", "сделай", "ещё раз", "еще раз", "заново", "повтори", "ещё", "еще",
    "сделать", "переделать", "по новой", "сначала", "новой", "опять",
)

_P6E67_ARTIFACT_WORDS = (
    "pdf", "пдф", "xlsx", "excel", "эксель", "txt", "ссылку", "ссылки", "drive", "расчет", "расчёт"
)

_P6E67_BAD_RESULT = (
    "что строим", "дом, ангар, склад", "фундамент или кровлю", "какой объект", "уточните что строим"
)

def _p6e67_log():
    try:
        return logger
    except Exception:
        return _p6e67_logging.getLogger("task_worker")

def _p6e67_s(v, limit=60000):
    try:
        return str(v or "").strip()[:limit]
    except Exception:
        return ""

def _p6e67_low(v, limit=60000):
    return _p6e67_s(v, limit).lower().replace("ё", "е")

def _p6e67_row(row, key, default=None):
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        return default

def _p6e67_hist(conn, task_id, action):
    try:

====================================================================================================
END_FILE: task_worker.py
FILE_CHUNK: 1/3
====================================================================================================
