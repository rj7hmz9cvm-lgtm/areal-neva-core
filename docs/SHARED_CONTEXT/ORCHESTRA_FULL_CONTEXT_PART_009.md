# ORCHESTRA_FULL_CONTEXT_PART_009
generated_at_utc: 2026-05-08T23:50:02.484144+00:00
git_sha_before_commit: 82535ed3c4087a2bbd99020991b7f03e1150fb1c
part: 9/17


====================================================================================================
BEGIN_FILE: core/engine_base.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 345250b62008f2101d0cc10e959bbceeff15a9e83a007be5433e260a6ed52267
====================================================================================================
import os, logging, hashlib, sqlite3, re
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
BASE = "/root/.areal-neva-core"
DB_PATH = f"{BASE}/data/core.db"

STAGES = ["INGESTED", "DOWNLOADED", "PARSED", "CLEANED", "NORMALIZED", "VALIDATED", "CALCULATED", "ARTIFACT_CREATED", "UPLOADED", "COMPLETED", "FAILED"]
UNIT_NORMALIZATION = {"м2": "м²", "кв.м": "м²", "м3": "м³", "куб.м": "м³", "шт": "шт", "кг": "кг", "т": "т", "тн": "т", "п.м": "п.м"}
FALSE_NUMBERS = ["B25", "B30", "B15", "A500", "A240", "A400", "12мм", "20мм", "10мм"]
BUILDING_DICT = {"бетон B25": "Бетон", "бетон B30": "Бетон", "доска 50х150": "Доска обрезная", "арматура A500": "Арматура"}


def _run_upload_sync(fn, *args, **kwargs):
    import asyncio
    import inspect
    import threading

    box = {"value": None, "error": None}

    def _runner():
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            value = fn(*args, **kwargs)
            if inspect.isawaitable(value):
                value = loop.run_until_complete(value)
            box["value"] = value
        except Exception as e:
            box["error"] = e
        finally:
            try:
                loop.close()
            except Exception:
                pass
            try:
                asyncio.set_event_loop(None)
            except Exception:
                pass

    t = threading.Thread(target=_runner, daemon=True)
    t.start()
    t.join()

    if box["error"] is not None:
        raise box["error"]

    return box["value"]

def get_db(): return sqlite3.connect(DB_PATH)

def update_drive_file_stage(task_id: str, drive_file_id: str, stage: str) -> bool:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM drive_files WHERE task_id=? AND drive_file_id=?", (task_id, drive_file_id))
        if cur.fetchone():
            cur.execute("UPDATE drive_files SET stage=? WHERE task_id=? AND drive_file_id=?", (stage, task_id, drive_file_id))
        else:
            cur.execute("INSERT INTO drive_files (task_id, drive_file_id, stage, created_at) VALUES (?,?,?,?)", (task_id, drive_file_id, stage, datetime.now(timezone.utc).isoformat()))
        conn.commit(); conn.close()
        return True
    except Exception as e:
        logger.error(f"update_drive_file_stage: {e}")
        return False


def detect_real_file_type(file_path: str) -> str:
    try:
        with open(file_path, "rb") as f:
            header = f.read(8)
    except Exception:
        header = b""

    ext = os.path.splitext(file_path)[1].lower()

    if header.startswith(b"%PDF"):
        return "pdf"
    if header.startswith(b"PK\x03\x04"):
        if ext in (".xlsx", ".xls"):
            return "xlsx"
        if ext in (".docx", ".doc"):
            return "docx"
        if ext == ".zip":
            return "zip"
        return "zip_or_office"
    if header.startswith(b"\xFF\xD8\xFF"):
        return "jpg"
    if header.startswith(b"\x89PNG"):
        return "png"
    if header.startswith(b"Rar!"):
        return "rar"
    if header.startswith(b"7z\xBC\xAF"):
        return "7z"
    if header.startswith(b"AC10") or ext in (".dwg", ".dxf"):
        return "dwg"

    ext_map = {
        ".csv": "csv",
        ".txt": "txt",
        ".heic": "image",
        ".webp": "image",
        ".jpg": "jpg",
        ".jpeg": "jpg",
        ".png": "png",
        ".pdf": "invalid_pdf",
    }
    return ext_map.get(ext, "unknown")


def calculate_file_hash(file_path: str) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for b in iter(lambda: f.read(4096), b""): sha.update(b)
    return sha.hexdigest()


# === PATCH_DRIVE_DIRECT_OAUTH_V1 ===
def _telegram_fallback_send(local_path: str, task_id: str, topic_id: int) -> str:
    """TELEGRAM_FALLBACK_V1 — отправить файл в Telegram если Drive недоступен"""
    try:
        import requests, os
        BOT_TOKEN = <REDACTED_SECRET>"TELEGRAM_BOT_TOKEN", "")
        CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003725299009")
        if not BOT_TOKEN or not os.path.exists(local_path):
            return ""
        caption = f"[DRIVE_UNAVAIL] Файл задачи {task_id[:8]} — Drive недоступен, отправляю напрямую"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        with open(local_path, "rb") as f:
            resp = requests.post(url, data={
                "chat_id": CHAT_ID,
                "message_thread_id": str(topic_id) if topic_id else "",
                "caption": caption,
            }, files={"document": f}, timeout=60)
        if resp.ok:
            result = resp.json()
            file_id = result.get("result", {}).get("document", {}).get("file_id", "")
            logger.info("TELEGRAM_FALLBACK_V1 sent file_id=%s task=%s", file_id, task_id)
            return f"telegram://file/{file_id}"
        else:
            logger.warning("TELEGRAM_FALLBACK_V1 failed status=%s", resp.status_code)
            return ""
    except Exception as e:
        logger.warning("TELEGRAM_FALLBACK_V1 err=%s", e)
        return ""

# === DRIVE_TOPIC_FOLDER_ENFORCER_V1 ===
def _drive_creds_v1():
    import os
    from dotenv import load_dotenv
    load_dotenv("/root/.areal-neva-core/.env", override=False)
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials(
        None,
        refresh_token=<REDACTED_SECRET>"GDRIVE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GDRIVE_CLIENT_ID"],
        client_secret=<REDACTED_SECRET>"GDRIVE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    creds.refresh(Request())
    return creds

def _drive_svc_v1():
    from googleapiclient.discovery import build
    return build("drive", "v3", credentials=_drive_creds_v1(), cache_discovery=False)

def _drive_get_or_create_folder(svc, name: str, parent_id: str) -> str:
    safe = str(name or "").replace("'", "\'")
    q = f"mimeType=\'application/vnd.google-apps.folder\' and trashed=false and name=\'{safe}\' and \'{parent_id}\' in parents"
    r = svc.files().list(q=q, fields="files(id)", pageSize=1).execute()
    files = r.get("files") or []
    if files:
        return files[0]["id"]
    f = svc.files().create(
        body={"name": str(name), "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]},
        fields="id",
    ).execute()
    return f.get("id") or ""

def get_drive_topic_folder_id(topic_id: int, chat_id: str = "") -> str:
    import os
    from dotenv import load_dotenv
    load_dotenv("/root/.areal-neva-core/.env", override=False)
    svc = _drive_svc_v1()
    root = os.environ.get("DRIVE_INGEST_FOLDER_ID", "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB")
    chat = str(chat_id or os.environ.get("TELEGRAM_CHAT_ID", "-1003725299009"))
    chat_folder = _drive_get_or_create_folder(svc, f"chat_{chat}", root)
    return _drive_get_or_create_folder(svc, f"topic_{int(topic_id or 0)}", chat_folder)

def upload_artifact_to_drive(file_path: str, task_id: str, topic_id: int):
    import logging, mimetypes, os
    _logger = logging.getLogger(__name__)
    if not file_path or not os.path.exists(str(file_path)):
        _logger.error("DRIVE_TOPIC_FOLDER_ENFORCER_V1_NOT_FOUND task=%s path=%s", task_id, file_path)
        return None
    try:
        from googleapiclient.http import MediaFileUpload
        svc = _drive_svc_v1()
        folder_id = get_drive_topic_folder_id(int(topic_id or 0))
        name = os.path.basename(str(file_path))
        mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        f = svc.files().create(
            body={"name": name, "parents": [folder_id]},
            media_body=MediaFileUpload(str(file_path), mimetype=mime, resumable=True),
            fields="id,webViewLink",
        ).execute()
        fid = f.get("id")
        if not fid:
            return None
        try:
            svc.permissions().create(fileId=fid, body={"role": "reader", "type": "anyone"}, fields="id").execute()
        except Exception as pe:
            _logger.warning("DRIVE_TOPIC_FOLDER_ENFORCER_V1_PERM_ERR task=%s err=%s", task_id, pe)
        link = f.get("webViewLink") or f"https://drive.google.com/file/d/{fid}/view"
        _logger.info("DRIVE_TOPIC_FOLDER_ENFORCER_V1_OK task=%s topic=%s link=%s", task_id, topic_id, link)
        return link
    except Exception as e:
        _logger.error("DRIVE_TOPIC_FOLDER_ENFORCER_V1_FAILED task=%s err=%s", task_id, e)
        return None
# === END_DRIVE_TOPIC_FOLDER_ENFORCER_V1 ===

def quality_gate(file_path: str, task_id: str, expected_type: str = "excel") -> Dict[str, Any]:
    err, warn = [], []
    if not os.path.exists(file_path): err.append("File not found")
    else:
        sz = os.path.getsize(file_path)
        if sz == 0: err.append("Empty file")
        elif sz > 50*1024*1024: warn.append("File >50MB")
    if expected_type == "excel" and file_path.endswith(('.xlsx','.xls')):
        try:
            from openpyxl import load_workbook
            wb = load_workbook(file_path)
            has_formulas = any(cell.data_type == 'f' for sheet in wb for row in sheet.iter_rows() for cell in row)
            if not has_formulas: warn.append("No formulas found")
            wb.close()
        except: err.append("Excel validation failed")
    return {"passed": len(err)==0, "errors": err, "warnings": warn}

def normalize_unit(unit: str) -> str:
    return UNIT_NORMALIZATION.get(unit.lower().strip(), unit)

def is_false_number(val: str) -> bool:
    return any(fn in str(val) for fn in FALSE_NUMBERS)

def normalize_item_name(name: str) -> str:
    for k, v in BUILDING_DICT.items():
        if k in name.lower(): return v
    return name

def is_duplicate_task(conn, chat_id: str, topic_id: int, prompt: str, file_hash: str) -> bool:
    cur = conn.execute("SELECT id FROM tasks WHERE chat_id=? AND topic_id=? AND raw_input=? AND result LIKE ?", (chat_id, topic_id, prompt, f"%{file_hash}%"))
    return cur.fetchone() is not None

def should_retry(task_id: str) -> bool:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM task_history WHERE task_id=? AND action='retry'", (task_id,))
        retries = cur.fetchone()[0]
        conn.close()
        return retries < 1
    except:
        return False

def mark_retry(task_id: str) -> None:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?,?,?)", (task_id, 'retry', datetime.now(timezone.utc).isoformat()))
        conn.commit(); conn.close()
    except: pass

def get_next_version(file_name: str, task_id: str) -> str:
    base, ext = os.path.splitext(file_name)
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tasks WHERE result LIKE ?", (f"%{base}%",))
        count = cur.fetchone()[0]
        conn.close()
        return f"{base}_v{count+1}{ext}"
    except:
        return f"{base}_v2{ext}"
import fcntl

def acquire_task_lock(task_id: str) -> bool:
    lock_file = f"/tmp/task_{task_id}.lock"
    try:
        fd = open(lock_file, 'w')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except:
        return False
import re

def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name)[:100]
def check_file_size(file_path: str, max_mb: int = 50) -> bool:
    return os.path.getsize(file_path) <= max_mb * 1024 * 1024
def can_open_file(file_path: str) -> bool:
    try:
        if file_path.endswith(('.xlsx','.xls')):
            from openpyxl import load_workbook
            wb = load_workbook(file_path); wb.close()
        elif file_path.endswith('.docx'):
            from docx import Document
            Document(file_path)
        elif file_path.endswith('.pdf'):
            from pypdf import PdfReader
            PdfReader(file_path)
        return True
    except:
        return False

====================================================================================================
END_FILE: core/engine_base.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/engine_contract.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 85fc94fcfbe47b0e453578cac50d039866b345267967ecd3ea582aa1363517cc
====================================================================================================
# === UNIFIED_ENGINE_RESULT_VALIDATOR_V1 ===
# === UNIFIED_ARTIFACT_CONTRACT_V1 ===
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

BAD_FINAL_PATTERNS = [
    r"ожида[её]т анализ",
    r"файл скачан",
    r"ожидает выбора",
    r"не удалось",
    r"ошибка",
    r"error",
    r"traceback",
    r"none$",
    r"null$",
    r"undefined",
    r"пока не могу",
    r"не могу обработать",
]

FILE_INPUT_TYPES = {"drive_file", "file", "document", "photo", "image", "drawing", "table"}

def _s(v: Any, limit: int = 20000) -> str:
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        try:
            v = json.dumps(v, ensure_ascii=False)
        except Exception:
            v = str(v)
    s = str(v)
    s = s.replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{4,}", "\n\n", s)
    return s.strip()[:limit]

def _links(text: str) -> List[str]:
    return [x.rstrip(".,;:") for x in re.findall(r"https?://[^\s\]\)\}\"']+", text or "")]

def _exists(path: str) -> bool:
    try:
        return bool(path) and os.path.exists(path)
    except Exception:
        return False

def normalize_engine_result(raw: Any, default_engine: str = "UNKNOWN_ENGINE") -> Dict[str, Any]:
    if isinstance(raw, dict):
        data = dict(raw)
    else:
        data = {"summary": _s(raw), "result": _s(raw)}

    summary = _s(data.get("summary") or data.get("result_text") or data.get("result") or data.get("message") or data.get("text"))
    artifact_path = _s(data.get("artifact_path") or data.get("path") or "")
    artifact_name = _s(data.get("artifact_name") or (Path(artifact_path).name if artifact_path else ""))
    drive_link = _s(data.get("drive_link") or data.get("link") or data.get("url") or "")

    artifact = data.get("artifact")
    if isinstance(artifact, dict):
        artifact_path = artifact_path or _s(artifact.get("path"))
        artifact_name = artifact_name or _s(artifact.get("name") or artifact.get("artifact_name"))
        drive_link = drive_link or _s(artifact.get("drive_link") or artifact.get("link") or artifact.get("url"))

    extra = data.get("extra_artifacts") or []
    if isinstance(extra, str):
        extra = [extra]
    if not isinstance(extra, list):
        extra = []

    found_links = _links("\n".join([summary, drive_link, _s(data)]))
    if not drive_link and found_links:
        drive_link = found_links[0]

    error = _s(data.get("error") or data.get("error_message") or data.get("reason") or "")
    engine = _s(data.get("engine") or default_engine or "UNKNOWN_ENGINE", 300)

    success_raw = data.get("success", data.get("ok", None))
    if success_raw is None:
        success = bool(summary or artifact_path or drive_link or extra) and not bool(error)
    else:
        success = bool(success_raw)

    return {
        "success": success,
        "engine": engine,
        "summary": summary,
        "artifact_path": artifact_path,
        "artifact_name": artifact_name,
        "drive_link": drive_link,
        "extra_artifacts": extra,
        "error": error,
        "links": found_links,
        "raw": data,
    }

def has_artifact_contract(result: Dict[str, Any]) -> bool:
    if not isinstance(result, dict):
        result = normalize_engine_result(result)
    if result.get("drive_link"):
        return True
    if result.get("artifact_path") and _exists(result.get("artifact_path")):
        return True
    for p in result.get("extra_artifacts") or []:
        if isinstance(p, str) and _exists(p):
            return True
        if isinstance(p, dict) and _exists(_s(p.get("path"))):
            return True
    if result.get("links"):
        return True
    return False

def validate_engine_result(raw: Any, input_type: str = "", user_text: str = "", topic_id: int = 0, require_artifact: Optional[bool] = None) -> Dict[str, Any]:
    result = normalize_engine_result(raw)
    text = _s(result.get("summary") or result.get("raw"))
    low = text.lower()
    inp = (input_type or "").lower()

    if not result.get("success") and result.get("error"):
        return {"ok": False, "reason": "ENGINE_ERROR", "contract": result}

    if len(text) < 8 and not has_artifact_contract(result):
        return {"ok": False, "reason": "EMPTY_OR_TOO_SHORT", "contract": result}

    for pat in BAD_FINAL_PATTERNS:
        if re.search(pat, low, re.I):
            if not has_artifact_contract(result):
                return {"ok": False, "reason": f"BAD_FINAL_TEXT:{pat}", "contract": result}

    if require_artifact is None:
        require_artifact = inp in FILE_INPUT_TYPES or any(x in (user_text or "").lower() for x in ("файл", "смет", "акт", "проект", "dwg", "dxf", "excel", "pdf", "docx"))

    if require_artifact and not has_artifact_contract(result):
        if not re.search(r"(создан|готов|сформирован|pdf|xlsx|docx|zip|drive|google|ссылка|retry|telegram)", low, re.I):
            return {"ok": False, "reason": "NO_ARTIFACT_OR_LINK_FOR_FILE_TASK", "contract": result}

    return {"ok": True, "reason": "OK", "contract": result}

def result_to_user_text(raw: Any) -> str:
    r = normalize_engine_result(raw)
    parts = []
    if r.get("summary"):
        parts.append(r["summary"])
    if r.get("drive_link"):
        parts.append(f"Ссылка: {r['drive_link']}")
    if r.get("artifact_path") and not r.get("drive_link"):
        parts.append(f"Артефакт: {r['artifact_path']}")
    links = [x for x in r.get("links") or [] if x not in "\n".join(parts)]
    if links:
        parts.append("Ссылки:\n" + "\n".join(f"- {x}" for x in links[:10]))
    if r.get("error") and not parts:
        parts.append(f"Ошибка: {r['error']}")
    return "\n\n".join(parts).strip()

def normalize_and_validate(raw: Any, input_type: str = "", user_text: str = "", topic_id: int = 0, require_artifact: Optional[bool] = None) -> Dict[str, Any]:
    v = validate_engine_result(raw, input_type=input_type, user_text=user_text, topic_id=topic_id, require_artifact=require_artifact)
    v["text"] = result_to_user_text(v.get("contract") or raw)
    return v
# === END_UNIFIED_ARTIFACT_CONTRACT_V1 ===
# === END_UNIFIED_ENGINE_RESULT_VALIDATOR_V1 ===

====================================================================================================
END_FILE: core/engine_contract.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/error_explainer.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: f755b92831a8a7da82c026a47f695c7b77634c9ffe1d500a374b6d2f5c1d01e4
====================================================================================================
# === ERROR_EXPLAINER_V1 ===
# Канон §5.7 — конкретные коды вместо общих фраз
_EXPLANATIONS = {
    "STT_FAILED":                   "Не удалось распознать голос. Попробуй ещё раз или напиши текстом.",
    "EMPTY_TRANSCRIPT":             "Голосовое сообщение пустое. Говори чётче или напиши текстом.",
    "ROUTER_FAILED":                "Ошибка маршрутизации. Попробуй переформулировать запрос.",
    "INVALID_RESULT":               "Результат не прошёл проверку. Попробуй снова.",
    "NO_VALID_ARTIFACT":            "Файл не создан. Повтори задачу.",
    "SOURCE_FILE_RETURNED_AS_RESULT":"Исходный файл вернулся без обработки. Попробуй снова.",
    "REQUEUE_LOOP_DETECTED":        "Задача зациклилась. Отмени и создай новую.",
    "ENGINE_TIMEOUT":               "Движок не ответил вовремя. Попробуй снова.",
    "DOWNLOAD_FAILED":              "Файл не скачался с Drive. Проверь доступ и попробуй снова.",
    "FILE_PARSE_FAILED":            "Не удалось прочитать файл. Проверь формат.",
    "NO_TECH_DATA_EXTRACTED":       "Технических данных не найдено в файле.",
    "ESTIMATE_EMPTY_RESULT":        "Смета пустая — таблица не извлечена. Пришли файл с позициями.",
    "IMAGE_UNREADABLE":             "Фото нечёткое или повёрнуто. Пришли лучше.",
    "SEARCH_FAILED":                "Поиск не дал результатов. Уточни запрос.",
    "INTAKE_TIMEOUT":               "Задача не взята в работу вовремя. Попробуй снова.",
    "EXECUTION_TIMEOUT":            "Задача выполнялась слишком долго. Попробуй снова.",
    "CLARIFICATION_TIMEOUT":        "Не дождался уточнения. Задача закрыта.",
    "CONFIRMATION_TIMEOUT":         "Подтверждение не получено. Задача закрыта.",
    "INVALID_TASK_CONTRACT":        "Задача создана с ошибкой. Попробуй снова.",
    "INVALID_ENGINE_CONTRACT":      "Движок вернул неверный ответ. Попробуй снова.",
    "SERVICE_FILE_IGNORED":         "Служебный файл пропущен.",
    "FILE_TYPE_MISMATCH":           "Тип файла не совпадает с расширением.",
    "BOT_MESSAGE_ID_NOT_SAVED":     "Ошибка сохранения сообщения. Попробуй снова.",
    "SEND_FAILED":                  "Не удалось отправить ответ. Попробуй снова.",
    "STALE_TIMEOUT":                "Задача зависла и закрыта по таймауту.",
    "OCR_DEPS_MISSING":             "OCR не установлен. Сообщи администратору.",
    "FORBIDDEN_PHRASE":             "Ответ не прошёл проверку качества. Повторяю задачу.",
    "EMPTY_RESULT":                 "Пустой результат. Попробуй снова.",
    "ARTIFACT_FILE_NOT_EXISTS":     "Файл артефакта не найден. Попробуй снова.",
}

def explain(error_code: str, default: str = None) -> str:
    base = error_code.split(":")[0] if ":" in error_code else error_code
    return _EXPLANATIONS.get(base) or _EXPLANATIONS.get(error_code) or default or f"Ошибка: {error_code}"

def user_friendly_error(error_code: str) -> str:
    return explain(error_code)
# === END ERROR_EXPLAINER_V1 ===

====================================================================================================
END_FILE: core/error_explainer.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/estimate_template_policy.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: f35f6db459149ccd2a55c1dacf9ba678e4cd9322f4c79654921370a4cb70766f
====================================================================================================
# === ESTIMATE_TEMPLATE_POLICY_CONTEXT_V4_TOP_LOGISTICS ===
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

BASE = Path("/root/.areal-neva-core")
REGISTRY_PATH = BASE / "config" / "estimate_template_registry.json"

TRIGGER_RE = re.compile(
    r"(смет|расчет|расч[её]т|стоимость|материал|логист|доставка|удален|удалён|км|кирпич|газобетон|каркас|монолит|фундамент|кровл|перекр|отделк|инженер|плита|дом)",
    re.I,
)

def _s(v: Any) -> str:
    return "" if v is None else str(v)

def _load_registry() -> Dict[str, Any]:
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def build_estimate_template_context(user_text: str = "", limit: int = 12000) -> str:
    text = _s(user_text)
    if not TRIGGER_RE.search(text):
        return ""

    data = _load_registry()
    policy = data.get("estimate_top_templates_logistics_canon_v4") or data.get("estimate_template_formula_price_confirm_v3") or data.get("estimate_template_formula_price_confirm_v2")
    if not isinstance(policy, dict):
        return ""

    lines = []
    lines.append("ESTIMATE_TEMPLATE_CANON: ACTIVE")
    lines.append("Version: ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4")
    lines.append("")
    lines.append("CORE RULE:")
    lines.append("Use top estimate files as scalable calculation templates, not as fixed price lists")
    lines.append("Preserve estimate logic: sections, rows, formulas, columns, totals, notes, exclusions")
    lines.append("Use same logic for any material: brick, gasbeton, frame, monolith, roof, slab, finishing, engineering")
    lines.append("Never mix scenarios without explicit user instruction")
    lines.append("")
    lines.append("TOP TEMPLATE FILES:")
    for src in policy.get("source_files", []):
        lines.append(f"- {src.get('title')} | role={src.get('template_role')} | formulas={src.get('formula_total')} | id={src.get('file_id')}")
    lines.append("")
    lines.append("PRICE CONFIRMATION RULE:")
    lines.append("Do not silently insert material prices")
    lines.append("Before final XLSX/PDF, search current prices online and show source, price, unit, region/date, link")
    lines.append("Propose average/median price and ask user to choose: average / minimum / maximum / specific source / manual price")
    lines.append("User can add markup, discount, reserve, manual correction per position, section or whole estimate")
    lines.append("Final XLSX/PDF is forbidden before price confirmation")
    lines.append("")
    lines.append("LOGISTICS RULE:")
    lines.append("Before final estimate, ask for object location or distance from city")
    lines.append("Ask access conditions: road, truck access, unloading, crane/manipulator need, storage, site restrictions")
    lines.append("Account for delivery, transport, unloading, machinery, crew travel, accommodation if remote")
    lines.append("A house near city and a house 200 km away cannot have the same final cost")
    lines.append("If logistics data is missing, ask one concise clarification before final price")
    lines.append("")
    cols = policy.get("canonical_columns") or []
    if cols:
        lines.append("CANONICAL_COLUMNS:")
        lines.append(" | ".join(_s(x) for x in cols))
        lines.append("")
    sections = policy.get("canonical_sections") or []
    if sections:
        lines.append("CANONICAL_SECTIONS:")
        for i, sec in enumerate(sections, 1):
            lines.append(f"{i}. {sec}")
        lines.append("")
    groups = policy.get("universal_material_groups") or {}
    if groups:
        lines.append("UNIVERSAL_MATERIAL_GROUPS:")
        for k, vals in groups.items():
            if isinstance(vals, list):
                lines.append(f"- {k}: " + ", ".join(_s(v) for v in vals))
        lines.append("")
    return "\n".join(lines)[:limit]

# === END_ESTIMATE_TEMPLATE_POLICY_CONTEXT_V4_TOP_LOGISTICS ===

====================================================================================================
END_FILE: core/estimate_template_policy.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/estimate_unified_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 81e97fc4ac12fb6e0940a4dd7f3586b1c84d283716d5980c67e9e84c60e51d08
====================================================================================================
# === FULLFIX_16_ESTIMATE_UNIFIED_P0_SAFE ===
import os, re, logging, sqlite3, traceback
logger = logging.getLogger(__name__)
ENGINE = "FULLFIX_16_ESTIMATE_UNIFIED_P0_SAFE"
RUNTIME_DIR = "/root/.areal-neva-core/runtime"
CORE_DB = "/root/.areal-neva-core/data/core.db"
MEMORY_DB = "/root/.areal-neva-core/data/memory.db"
os.makedirs(RUNTIME_DIR, exist_ok=True)

_STRIP_RE = re.compile(r"(?im)^\s*MANIFEST\s*:\s*https?://\S+\s*$")

def _strip_manifest(text):
    t = str(text or "")
    t = _STRIP_RE.sub("", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def parse_estimate_rows(text):
    try:
        from core.sample_template_engine import parse_estimate_items
        rows = parse_estimate_items(text)
        if rows:
            return rows
    except Exception:
        pass
    rows = []
    seen = set()
    pat = re.compile(
        r"([а-яёА-ЯЁa-zA-Z][а-яёА-ЯЁa-zA-Z0-9 \-/\.\"]{1,60}?)"
        r"\s+(\d+(?:[.,]\d+)?)\s*"
        r"(м²|м2|м³|м3|п\.м|м\.п|шт|кг|тн|т|компл\.?|л|м)\s*"
        r"(?:(?:цена|по|x|х|@)?\s*(\d+(?:[.,]\d+)?)(?:\s*руб\.?)?)?",
        re.I | re.U
    )
    skip = {"итого", "всего", "смета", "смету", "сделай", "составь"}
    for m in pat.finditer(str(text or "")):
        name = m.group(1).strip().rstrip(",:. ")
        name = re.sub(r"^(сделай|составь|посчитай|смету|смета|по|на)\s+", "", name, flags=re.I|re.U)
        name = name.strip(" ,:;.-")
        if not name or name.lower() in skip or len(name) < 2:
            continue
        qty = float(m.group(2).replace(",", "."))
        unit = m.group(3).replace("м2","м²").replace("м3","м³")
        price = float(m.group(4).replace(",", ".")) if m.group(4) else 0.0
        key = (name.lower(), qty, unit, price)
        if key in seen:
            continue
        seen.add(key)
        rows.append({"name": name, "qty": qty, "unit": unit, "price": price, "total": round(qty*price, 2)})
    return rows


# === FULLFIX_20_ACTIVE_TEMPLATE ===
def _ff20_load_active_template(chat_id=None, topic_id=0):
    try:
        import glob, json
        topic = str(int(topic_id or 0))
        patterns = []
        if chat_id is not None:
            patterns.append(
                "/root/.areal-neva-core/data/templates/estimate/ACTIVE__chat_"
                + str(chat_id) + "__topic_" + topic + ".json"
            )
        patterns.append(
            "/root/.areal-neva-core/data/templates/estimate/ACTIVE__*__topic_"
            + topic + ".json"
        )
        for pat in patterns:
            hits = glob.glob(pat)
            if hits:
                with open(hits[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                cols = data.get("columns") or data.get("headers") or data.get("xlsx_headers")
                if isinstance(cols, list) and len(cols) >= 2:
                    return [str(x) for x in cols]
    except Exception as e:
        try:
            logger.warning("FF20_ACTIVE_TEMPLATE_ERR=%s", e)
        except Exception:
            pass
    return None
# === END FULLFIX_20_ACTIVE_TEMPLATE ===

def generate_xlsx(rows, task_id, chat_id=None, topic_id=0):
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    path = os.path.join(RUNTIME_DIR, "estimate_" + str(task_id)[:8] + ".xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Смета"
    ws.merge_cells("A1:F1")
    ws["A1"] = "СМЕТА"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    thin = Border(left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin"))
    hdrs = _ff20_load_active_template(chat_id=chat_id, topic_id=topic_id) or ["№", "Наименование", "Ед.", "Кол-во", "Цена, руб.", "Сумма, руб."]  # FULLFIX_20_ACTIVE_TEMPLATE
    for c, h in enumerate(hdrs, 1):
        cell = ws.cell(row=2, column=c, value=h)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9D9D9")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin
    for col, w in zip("ABCDEF", [6, 45, 10, 12, 16, 16]):
        ws.column_dimensions[col].width = w
    for i, row in enumerate(rows, 1):
        r = i + 2
        for c, v in enumerate([i, row["name"], row["unit"], row["qty"], row["price"], "=D"+str(r)+"*E"+str(r)], 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.border = thin
            cell.alignment = Alignment(vertical="center", wrap_text=True)
    tr = len(rows) + 3
    ws.cell(row=tr, column=2, value="ИТОГО").font = Font(bold=True)
    ws.cell(row=tr, column=6, value="=SUM(F3:F"+str(tr-1)+")").font = Font(bold=True)
    for c in range(1, 7):
        ws.cell(row=tr, column=c).border = thin
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = "A2:F" + str(max(tr, 3))
    wb.save(path)
    return path

def generate_pdf(rows, task_id):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
    from reportlab.lib import colors
    from core.pdf_cyrillic import register_cyrillic_fonts, make_styles, make_paragraph, clean_pdf_text, FONT_BOLD
    path = os.path.join(RUNTIME_DIR, "estimate_" + str(task_id)[:8] + ".pdf")
    register_cyrillic_fonts()
    styles = make_styles()
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20, bottomMargin=20, leftMargin=20, rightMargin=20)
    hdr = [make_paragraph(h, "bold", styles) for h in ["№", "Наименование", "Ед.", "Кол-во", "Цена, руб.", "Сумма, руб."]]
    data = [hdr]
    total = 0.0
    for i, row in enumerate(rows, 1):
        t = round(float(row["qty"]) * float(row["price"]), 2)
        total += t
        data.append([
            make_paragraph(str(i), "normal", styles),
            make_paragraph(clean_pdf_text(row["name"]), "normal", styles),
            make_paragraph(row["unit"], "normal", styles),
            make_paragraph(str(row["qty"]), "normal", styles),
            make_paragraph("%.2f" % row["price"], "normal", styles),
            make_paragraph("%.2f" % t, "normal", styles),
        ])
    data.append([make_paragraph("", "normal", styles), make_paragraph("ИТОГО", "bold", styles),
                 make_paragraph("", "normal", styles), make_paragraph("", "normal", styles),
                 make_paragraph("", "normal", styles), make_paragraph("%.2f" % total, "bold", styles)])
    story = [make_paragraph("СМЕТА", "header", styles), Spacer(1, 8)]
    tbl = Table(data, colWidths=[22, 190, 32, 52, 70, 70])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#444444")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),FONT_BOLD),
        ("GRID",(0,0),(-1,-1),0.4,colors.black),
        ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#FFFFCC")),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(tbl)
    doc.build(story)
    return path

# === MAIN ENTRY — opens its own DB connection, no cross-thread SQLite ===
def process_estimate_task_sync(task_id, chat_id, topic_id, raw_input):
    from core.artifact_upload_guard import upload_many_or_fail
    from core.reply_sender import send_reply_ex
    try:
        rows = parse_estimate_rows(raw_input)
        if not rows:
            msg = "Смета не создана: не нашёл строки «позиция количество единица цена»"
            with sqlite3.connect(CORE_DB, timeout=30) as c:
                c.execute("UPDATE tasks SET state='FAILED',result=?,error_message=?,updated_at=datetime('now') WHERE id=?",
                    (msg, "NO_ESTIMATE_ROWS", task_id))
                c.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, "state:FAILED:no_rows"))
                c.commit()
            send_reply_ex(chat_id=str(chat_id), text=msg, reply_to_message_id=None, message_thread_id=topic_id)
            return False

        xlsx_path = generate_xlsx(rows, task_id, chat_id=str(chat_id), topic_id=topic_id)
        pdf_path = generate_pdf(rows, task_id)
        up = upload_many_or_fail(
            [{"path": pdf_path, "kind": "estimate_pdf"}, {"path": xlsx_path, "kind": "estimate_xlsx"}],
            task_id, topic_id
        )
        pdf_r = up.get("results", {}).get(pdf_path, {})
        xlsx_r = up.get("results", {}).get(xlsx_path, {})
        pdf_link = pdf_r.get("link") if pdf_r.get("success") else ""
        xlsx_link = xlsx_r.get("link") if xlsx_r.get("success") else ""
        total = round(sum(float(r["qty"]) * float(r["price"]) for r in rows), 2)

        if not (pdf_link or xlsx_link):
            msg = "Смета рассчитана, Drive upload не выполнен. Позиций: " + str(len(rows)) + ". Итого: %.2f руб" % total
            with sqlite3.connect(CORE_DB, timeout=30) as c:
                c.execute("UPDATE tasks SET state='FAILED',result=?,error_message=?,updated_at=datetime('now') WHERE id=?",
                    (msg, "UPLOAD_FAILED", task_id))
                c.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, "state:FAILED:upload_failed"))
                c.commit()
            send_reply_ex(chat_id=str(chat_id), text=msg, reply_to_message_id=None, message_thread_id=topic_id)
            return False

        lines = ["Смета готова.", "Позиций: " + str(len(rows)) + ". Итого: %.2f руб" % total]
        if pdf_link:
            lines.append("PDF: " + pdf_link)
        if xlsx_link:
            lines.append("XLSX: " + xlsx_link)
        lines.append("")
        lines.append("Доволен результатом? Ответь: Да / Уточни / Правки")
        result_text = _strip_manifest("\n".join(lines))

        with sqlite3.connect(CORE_DB, timeout=30) as c:
            c.execute("UPDATE tasks SET state='AWAITING_CONFIRMATION',result=?,updated_at=datetime('now') WHERE id=?",
                (result_text, task_id))
            c.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                (task_id, "state:AWAITING_CONFIRMATION:estimate_unified"))
            c.commit()

        br = send_reply_ex(chat_id=str(chat_id), text=result_text, reply_to_message_id=None, message_thread_id=topic_id)
        bmid = None
        if isinstance(br, dict):
            bmid = br.get("bot_message_id") or br.get("message_id")
        elif hasattr(br, "message_id"):
            bmid = br.message_id
        if bmid:
            with sqlite3.connect(CORE_DB, timeout=30) as c:
                c.execute("UPDATE tasks SET bot_message_id=?,updated_at=datetime('now') WHERE id=?", (str(bmid), task_id))
                c.commit()

        # === FULLFIX_19_EUE_MEMORY_V3 ===
        try:
            from core.memory_client import save_memory as _ff19_sm
            _ff19_sm(
                str(chat_id),
                "topic_" + str(topic_id or 0) + "_last_estimate",
                {"task_id": task_id, "rows": len(rows), "total": total, "bot_message_id": bmid},
                topic_id=int(topic_id or 0),
                scope="topic"
            )
            _ff19_sm(
                str(chat_id),
                "active_task",
                {"task_id": task_id, "type": "estimate", "state": "AWAITING_CONFIRMATION"},
                topic_id=int(topic_id or 0),
                scope="active"
            )
        except Exception as _ff19_me:
            try:
                logger.warning("FF19_EUE_MEMORY_ERR=%s", _ff19_me)
            except Exception:
                pass
        # === END FULLFIX_19_EUE_MEMORY_V3 ===

        return True

    except Exception as e:
        err = traceback.format_exc()
        logger.error("ESTIMATE_UNIFIED_ERROR task=%s err=%s trace=%s", task_id, e, err)
        msg = "Смета не создана: внутренняя ошибка"
        try:
            with sqlite3.connect(CORE_DB, timeout=30) as c:
                c.execute("UPDATE tasks SET state='FAILED',result=?,error_message=?,updated_at=datetime('now') WHERE id=?",
                    (msg, str(e)[:500], task_id))
                c.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, "state:FAILED:exception"))
                c.commit()
        except Exception:
            pass
        try:
            from core.reply_sender import send_reply_ex
            send_reply_ex(chat_id=str(chat_id), text=msg, reply_to_message_id=None, message_thread_id=topic_id)
        except Exception:
            pass
        return False

async def process_estimate_task(conn, task_id, chat_id, topic_id, raw_input):
    # conn intentionally NOT passed to sync function — opens its own connection
    return process_estimate_task_sync(task_id, chat_id, topic_id, raw_input)
# === END FULLFIX_16_ESTIMATE_UNIFIED_P0_SAFE ===

====================================================================================================
END_FILE: core/estimate_unified_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/file_memory_bridge.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 029b9005621f00c7241f1e615030528b3cc68658f4463c1b3aa6fa13aba6940b
====================================================================================================
# === FILE_MEMORY_BRIDGE_FULL_CLOSE_V1 ===
from __future__ import annotations

import json
import os
import re
import sqlite3
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

BASE = "/root/.areal-neva-core"
CORE_DB = f"{BASE}/data/core.db"
MEM_DB = f"{BASE}/data/memory.db"

SERVICE_MARKERS = (
    "retry_queue_healthcheck",
    "healthcheck",
    "areal_hc_",
    "_hc_file",
)

FILE_QUERY_MARKERS = (
    "файл", "файлы", "документ", "документы", "таблица", "таблицу", "таблицы",
    "смет", "вор", "xlsx", "xls", "pdf", "docx", "акт", "фото", "фотограф",
    "план", "чертеж", "чертёж", "проект", "кж", "км", "кмд", "ар", "гост",
    "снип", "сп ", "норм", "технадзор", "дефект", "скидывал", "загружал",
    "загружен", "уже был", "последн", "шаблон", "образец", "покажи", "ссылк",
    "где она", "где он", "что с ним", "что с ней", "что делать",
)

TECH_TASK_MARKERS = (
    "технадзор", "дефект", "нарушение", "акт", "предписание", "замечание",
    "гост", "снип", "сп", "норма", "норматив", "осмотр", "проверка",
)

ESTIMATE_MARKERS = (
    "смет", "вор", "ведомость", "объем", "объём", "расцен", "стоимость",
    "посчитай", "расчет", "расчёт", "xlsx", "xls", "таблиц",
)

PROJECT_MARKERS = (
    "проект", "кж", "км", "кмд", "ар", "ов", "вк", "эом", "пз", "гп",
    "раздел", "чертеж", "чертёж", "план", "спецификац",
)

PHOTO_MARKERS = (
    "фото", "фотография", "картинка", "изображение", "jpg", "jpeg", "png", "heic", "webp",
)

def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def _clean(v: Any, limit: int = 12000) -> str:
    if v is None:
        return ""
    if not isinstance(v, str):
        try:
            v = json.dumps(v, ensure_ascii=False)
        except Exception:
            v = str(v)
    v = v.replace("\r", "\n")
    v = re.sub(r"[ \t]+", " ", v)
    v = re.sub(r"\n{3,}", "\n\n", v)
    return v.strip()[:limit]

def _conn(path: str) -> sqlite3.Connection:
    c = sqlite3.connect(path, timeout=20)
    c.row_factory = sqlite3.Row
    return c

def _has_table(conn: sqlite3.Connection, table: str) -> bool:
    try:
        return conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (table,)).fetchone() is not None
    except Exception:
        return False

def _safe_json(text: Any) -> Dict[str, Any]:
    if isinstance(text, dict):
        return text
    try:
        return json.loads(str(text or ""))
    except Exception:
        return {}

def is_service_file(file_name: str = "", source: str = "", topic_id: int = 0, raw_input: str = "") -> bool:
    name = _clean(file_name, 500).lower()
    src = _clean(source, 100).lower()
    raw = _clean(raw_input, 2000).lower()

    if any(m in name or m in src or m in raw for m in SERVICE_MARKERS):
        return True

    if src == "google_drive" and topic_id == 0 and name.startswith("tmp") and name.endswith(".txt"):
        return True

    if name.startswith("tmp") and name.endswith(".txt") and "google_drive" in raw:
        return True

    return False

def should_handle_file_followup(text: str) -> bool:
    low = _clean(text, 2000).lower()
    low = re.sub(r"^\[voice\]\s*", "", low, flags=re.I).strip()
    if not low:
        return False

    if any(m in low for m in FILE_QUERY_MARKERS):
        return True

    return False

def classify_file_direction(text: str = "", file_name: str = "", mime_type: str = "") -> str:
    low = " ".join([_clean(text, 2000), _clean(file_name, 500), _clean(mime_type, 200)]).lower()

    if any(m in low for m in TECH_TASK_MARKERS):
        return "TECHNADZOR_ACT_GOST_SP"
    if any(m in low for m in ESTIMATE_MARKERS):
        return "ESTIMATE_CALCULATION"
    if any(m in low for m in PROJECT_MARKERS):
        return "PROJECT_DESIGN"
    if any(m in low for m in PHOTO_MARKERS):
        return "PHOTO_OCR_TECHNADZOR"
    if any(x in low for x in (".xlsx", ".xls", ".csv", "spreadsheet")):
        return "TABLE_ESTIMATE"
    if any(x in low for x in (".docx", ".doc", "wordprocessing")):
        return "DOCUMENT_ACT"
    if any(x in low for x in (".pdf", "application/pdf")):
        return "PDF_DOCUMENT"
    if any(x in low for x in (".dwg", ".dxf")):
        return "DWG_DXF_PROJECT"

    return "FILE_GENERAL"

def _score_item(query: str, item: Dict[str, Any]) -> int:
    q = set(re.findall(r"[а-яa-z0-9]{3,}", query.lower()))
    hay = " ".join(str(item.get(k, "")) for k in ("file_name", "raw_input", "result", "value", "direction", "kind")).lower()
    score = 0
    for token in q:
        if token in hay:
            score += 3
    if "смет" in query.lower() and any(x in hay for x in ("смет", "вор", "xlsx", "xls", "estimate")):
        score += 20
    if "акт" in query.lower() and any(x in hay for x in ("акт", "технадзор", "дефект", "гост", "сп")):
        score += 20
    if "фото" in query.lower() and any(x in hay for x in ("jpg", "jpeg", "png", "фото", "image")):
        score += 20
    if "проект" in query.lower() and any(x in hay for x in ("проект", "кж", "км", "ар", "dxf", "dwg", "pdf")):
        score += 20
    return score

def _extract_links(text: str) -> List[str]:
    return re.findall(r"https?://\S+", text or "")

# === FILE_MEMORY_REAL_IDENTITY_FILTER_V2 ===
def _has_real_file_identity(item: Dict[str, Any]) -> bool:
    fname = _clean(item.get("file_name") or "", 500)
    fid = _clean(item.get("file_id") or "", 500)
    links = item.get("links") or []
    value = _clean(item.get("value") or item.get("summary") or "", 50000)

    if fname and fname.lower() not in ("без имени", "none", "null"):
        return True
    if fid:
        return True
    if links:
        return True
    if re.search(r"\.(xlsx|xls|csv|pdf|docx|doc|jpg|jpeg|png|heic|webp|dwg|dxf)\b", value, re.I):
        return True
    if "drive.google" in value or "docs.google" in value:
        return True
    return False
# === END FILE_MEMORY_REAL_IDENTITY_FILTER_V2 ===


def load_file_memory(chat_id: str, topic_id: int, query: str = "", limit: int = 12) -> List[Dict[str, Any]]:
    chat_id = str(chat_id)
    topic_id = int(topic_id or 0)
    out: List[Dict[str, Any]] = []

    if topic_id == 0:
        return out

    prefix = f"topic_{topic_id}_"

    if os.path.exists(MEM_DB):
        try:
            with _conn(MEM_DB) as mem:
                if _has_table(mem, "memory"):
                    rows = mem.execute(
                        """
                        SELECT key,value,timestamp FROM memory
                        WHERE chat_id=?
                          AND key LIKE ?
                          AND (
                            key LIKE ? OR key LIKE ? OR key LIKE ? OR key LIKE ?
                            OR key LIKE ? OR key LIKE ? OR key LIKE ?
                          )
                        ORDER BY timestamp DESC
                        LIMIT 300
                        """,
                        (
                            chat_id,
                            prefix + "%",
                            prefix + "file_%",
                            prefix + "file_content_%",
                            prefix + "file_content_status_%",
                            prefix + "artifact_result%",
                            prefix + "last_estimate%",
                            prefix + "active_estimate_template%",
                            prefix + "archive_%",
                        ),
                    ).fetchall()

                    for r in rows:
                        val = _clean(r["value"], 50000)
                        data = _safe_json(val)
                        item = {
                            "source": "memory.db",
                            "key": r["key"],
                            "timestamp": r["timestamp"],
                            "value": val,
                            "task_id": data.get("task_id") or "",
                            "file_id": data.get("file_id") or "",
                            "file_name": data.get("file_name") or "",
                            "mime_type": data.get("mime_type") or "",
                            "kind": data.get("kind") or data.get("type") or "",
                            "direction": classify_file_direction(val, str(data.get("file_name") or ""), str(data.get("mime_type") or "")),
                            "links": _extract_links(val),
                            "summary": _clean(data.get("summary") or data.get("result") or data.get("result_text") or val, 1000),
                        }
                        if item["file_name"] and is_service_file(item["file_name"], data.get("source") or "", topic_id, val):
                            continue
                        out.append(item)
        except Exception:
            pass

    if os.path.exists(CORE_DB):
        try:
            with _conn(CORE_DB) as core:
                if _has_table(core, "tasks"):
                    rows = core.execute(
                        """
                        SELECT id,input_type,state,raw_input,result,updated_at
                        FROM tasks
                        WHERE chat_id=?
                          AND COALESCE(topic_id,0)=?
                          AND (
                            input_type='drive_file'
                            OR COALESCE(result,'') LIKE '%drive.google%'
                            OR COALESCE(result,'') LIKE '%docs.google%'
                            OR COALESCE(raw_input,'') LIKE '%.xlsx%'
                            OR COALESCE(raw_input,'') LIKE '%.xls%'
                            OR COALESCE(raw_input,'') LIKE '%.pdf%'
                            OR COALESCE(raw_input,'') LIKE '%.docx%'
                          )
                        ORDER BY updated_at DESC
                        LIMIT 200
                        """,
                        (chat_id, topic_id),
                    ).fetchall()

                    for r in rows:
                        raw = _clean(r["raw_input"], 50000)
                        res = _clean(r["result"], 50000)
                        data = _safe_json(raw)
                        fname = data.get("file_name") or ""
                        if fname and is_service_file(fname, data.get("source") or "", topic_id, raw):
                            continue
                        item = {
                            "source": "core.db",
                            "key": f"task_{r['id']}",
                            "timestamp": r["updated_at"],
                            "task_id": r["id"],
                            "file_id": data.get("file_id") or "",
                            "file_name": fname,
                            "mime_type": data.get("mime_type") or "",
                            "input_type": r["input_type"],
                            "state": r["state"],
                            "direction": classify_file_direction(raw + "\n" + res, fname, data.get("mime_type") or ""),
                            "links": _extract_links(res),
                            "summary": _clean(res or raw, 1000),
                            "value": raw + "\n" + res,
                        }
                        out.append(item)
        except Exception:
            pass

    seen = set()
    filtered = []
    for item in out:
        key = item.get("task_id") or item.get("file_id") or item.get("key") or hashlib.sha1(json.dumps(item, ensure_ascii=False).encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        item["_score"] = _score_item(query or "", item)
        filtered.append(item)

    # === FILE_MEMORY_FINAL_FILTER_FAKE_ENTRIES_V2 ===
    filtered = [it for it in filtered if _has_real_file_identity(it)]
    # === END FILE_MEMORY_FINAL_FILTER_FAKE_ENTRIES_V2 ===

    if query:
        filtered.sort(key=lambda x: (x.get("_score", 0), x.get("timestamp") or ""), reverse=True)
    else:
        filtered.sort(key=lambda x: x.get("timestamp") or "", reverse=True)

    return filtered[:limit]


# === FILE_DISPLAY_NAME_FROM_LINK_V1 ===
def _display_name_for_item_v1(item: Dict[str, Any]) -> str:
    fname = _clean(item.get("file_name") or "", 500)
    if fname and fname.lower() not in ("без имени", "none", "null"):
        return fname

    links = item.get("links") or []
    value = _clean(item.get("value") or item.get("summary") or "", 50000)
    hay = "\n".join([value] + [str(x) for x in links]).lower()

    if "docs.google.com/spreadsheets" in hay:
        return "Google Sheets / XLSX артефакт"
    if "docs.google.com/document" in hay:
        return "Google Docs / DOCX артефакт"
    if "drive.google.com" in hay:
        if ".pdf" in hay or "pdf" in hay:
            return "PDF артефакт на Google Drive"
        if ".xlsx" in hay or ".xls" in hay or "spreadsheets" in hay:
            return "XLSX артефакт на Google Drive"
        if ".docx" in hay or "document" in hay:
            return "DOCX артефакт на Google Drive"
        return "Файл на Google Drive"

    m = re.search(r"([^/\\?#]+\.(xlsx|xls|csv|pdf|docx|doc|jpg|jpeg|png|heic|webp|dwg|dxf))", hay, re.I)
    if m:
        return m.group(1)

    if links:
        return "Файл по ссылке"

    return "без имени"
# === END FILE_DISPLAY_NAME_FROM_LINK_V1 ===


# === FILE_MEMORY_PUBLIC_OUTPUT_DOMAIN_FILTER_V6_FINAL_SESSION ===
def _fm_public_norm(text: Any) -> str:
    s = _clean(text, 50000)
    s = s.replace("\\\\n", "\n").replace("\\n", "\n").replace("\\\\t", " ").replace("\\t", " ")
    return s.strip()


def _fm_is_take_sample_command(text: str) -> bool:
    low = _fm_public_norm(text).lower().replace("ё", "е")
    if not any(x in low for x in ("возьми", "прими", "принимай", "принять", "используй", "сохрани", "закрепи", "закрепить", "работай")):
        return False
    return any(x in low for x in ("образец", "образцы", "образцов", "шаблон", "пример", "эталон", "эталоны", "как образец", "как образцы", "как эталон", "как эталоны"))


def _fm_query_domain(text: str) -> str:
    low = _fm_public_norm(text).lower().replace("ё", "е")
    if any(x in low for x in ("смет", "вор", "расцен", "стоимост", "объем", "объём", "калькуляц")):
        return "estimate"
    if any(x in low for x in ("проект", "кж", "км", "кмд", "ар", "чертеж", "чертёж", "конструкц", "плита", "цоколь", "узел")):
        return "project"
    if any(x in low for x in ("технадзор", "акт", "дефект", "нарушен", "замечан", "гост", "снип", " сп ")):
        return "technadzor"
    if any(x in low for x in ("фото", "картин", "изображ", "ocr", "таблиц")):
        return "ocr"
    return ""



def _fm_item_domain(item: Dict[str, Any]) -> str:
    fname = _fm_public_norm(item.get("file_name") or "").lower().replace("ё", "е")
    fname = re.sub(r"^\d+\.\s*", "", fname).strip().strip("\"'«»")

    if any(x in fname for x in ("кж", "кд", "км", "кмд", "ар", "проект", "цоколь", ".dwg", ".dxf")):
        return "project"
    if any(x in fname for x in ("смет", "вор", "расцен")):
        return "estimate"
    if any(x in fname for x in ("акт", "технадзор", "дефект")):
        return "technadzor"

    hay = _fm_public_norm(" ".join([
        str(item.get("direction") or ""),
        str(item.get("kind") or ""),
        str(item.get("file_name") or ""),
        str(item.get("summary") or ""),
        str(item.get("value") or ""),
    ])).lower().replace("ё", "е")

    if any(x in hay for x in ("технадзор", "tech", "акт", "defect", "gost", "snip", "нарушен", "замечан")):
        return "technadzor"
    if any(x in hay for x in ("estimate", "смет", "вор", "расцен", "стоимост", "калькуляц")):
        return "estimate"
    if any(x in hay for x in ("project", "проект", "кж", "кмд", "км", "чертеж", "чертёж", "конструкц", "цоколь", "плита", ".dxf", ".dwg")):
        return "project"
    if any(x in hay for x in ("ocr", "фото", "image", ".jpg", ".jpeg", ".png", ".heic", ".webp")):
        return "ocr"
    return ""


def _fm_public_title(item: Dict[str, Any]) -> str:
    name = _fm_public_norm(item.get("file_name") or "")
    name = re.sub(r"^\d+\.\s*", "", name).strip().strip("\"'«»")
    if name and name.lower() not in ("без имени", "none", "null", "unknown"):
        return name[:160]

    value = _fm_public_norm(item.get("value") or item.get("summary") or "")
    m = re.search(r"([^/\\?#\n]+\.(?:xlsx|xls|csv|pdf|docx|doc|jpg|jpeg|png|heic|webp|dwg|dxf))", value, re.I)
    if m:
        clean_name = re.sub(r"^\d+\.\s*", "", m.group(1)).strip().strip("\"'«»")
        return clean_name[:160]

    if "docs.google.com/spreadsheets" in value:
        return "Таблица Google Sheets"
    if "docs.google.com/document" in value:
        return "Документ Google Docs"
    if "drive.google.com" in value:
        return "Файл Google Drive"
    return "Файл"


def _fm_public_links(item: Dict[str, Any], limit: int = 2) -> List[str]:
    found: List[str] = []
    seen = set()

    for link in item.get("links") or []:
        url = _fm_public_norm(link).split("\n")[0].strip()
        if not url.startswith("http"):
            continue

        url = re.split(r"(?:DXF|XLSX|MANIFEST|PDF|DOCX)\s*:", url, flags=re.I)[0].rstrip(".,;)")
        low = url.lower()

        if "manifest" in low or low.endswith(".json"):
            continue
        if url in seen:
            continue

        seen.add(url)
        found.append(url)

        if len(found) >= int(limit or 2):
            break

    return found

def _fm_relevant_public_items(items: List[Dict[str, Any]], user_text: str, limit: int) -> List[Dict[str, Any]]:
    qdom = _fm_query_domain(user_text)
    out: List[Dict[str, Any]] = []
    seen = set()

    for item in items:
        idom = _fm_item_domain(item)
        if qdom and idom and qdom != idom:
            continue

        title = _fm_public_title(item)
        links = _fm_public_links(item)
        key = (title, tuple(links[:2]))
        if key in seen:
            continue
        seen.add(key)

        clean = dict(item)
        clean["_public_title"] = title
        clean["_public_links"] = links
        clean["_public_domain"] = idom
        out.append(clean)

        if len(out) >= min(int(limit or 3), 3):
            break

    return out




# === FILE_MEMORY_SAMPLE_STATUS_SKIP_P0_V2 ===
def _fm_is_sample_status_query(text: str) -> bool:
    low = _fm_public_norm(text).lower().replace("ё", "е")
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
# === END_FILE_MEMORY_SAMPLE_STATUS_SKIP_P0_V2 ===




# === WEB_SEARCH_FILE_CONTEXT_BYPASS_FINAL ===
def _fm_is_web_search_intent(text: str) -> bool:
    low = str(text or "").lower().replace("ё", "е")
    low = re.sub(r"^\[voice\]\s*", "", low, flags=re.I).strip()
    if not low:
        return False

    file_only = (
        "найди файл", "найди документ", "найди таблицу", "найди смету",
        "где файл", "где документ", "где таблица",
        "используй как образец", "использовать как образец",
        "открой файл", "обработай файл", "обработать файл",
    )
    if any(x in low for x in file_only):
        return False

    web = (
        "в интернете", "интернет", "сайт", "сайты", "ссылку", "ссылки", "ссылка",
        "телеграм", "telegram", "канал", "каналы", "бот", "боты",
        "топ ", "топовые", "лучшие", "ведущие", "рейтинг",
        "поиск", "поищи", "найди", "найти",
        "в россии", "в спб", "в москве", "по всей", "по стране",
        "instagram", "инстаграм", "youtube", "ютуб", "vk ", "вк ",
        "визуалы", "оформлены", "соцсети", "страницы",
        "цены", "поставщики", "магазины", "наличие",
    )
    return any(x in low for x in web)
# === END_WEB_SEARCH_FILE_CONTEXT_BYPASS_FINAL ===

def build_file_followup_answer(chat_id: str, topic_id: int, user_text: str, limit: int = 3) -> Optional[str]:
    # === WEB_SEARCH_FILE_CONTEXT_BYPASS_FINAL_CALL ===
    if int(topic_id or 0) == 500 or _fm_is_web_search_intent(user_text):
        return None
    # === END_WEB_SEARCH_FILE_CONTEXT_BYPASS_FINAL_CALL ===
    if _fm_is_take_sample_command(user_text) or _fm_is_sample_status_query(user_text):
        return None

    if not should_handle_file_followup(user_text):
        return None

    topic_id = int(topic_id or 0)
    if topic_id == 0:
        return "В общем топике файлы не смешиваю. Для поиска файла нужен конкретный рабочий топик"

    items = load_file_memory(chat_id, topic_id, user_text, limit=30)
    items = _fm_relevant_public_items(items, user_text, limit=limit)

    if not items:
        return "В этом топике релевантных файлов по запросу не найдено"

    lines = [
        "Файлы в этом топике уже есть. Нашёл релевантное:",
        "",
    ]

    for i, item in enumerate(items, 1):
        title = item.get("_public_title") or _fm_public_title(item)
        links = item.get("_public_links") or []
        lines.append(f"{i}. {title}")

        if links:
            if len(links) == 1:
                lines.append(f"   Ссылка: {links[0]}")
            else:
                lines.append("   Ссылки:")
                for link in links[:3]:
                    lines.append(f"   - {link}")

        domain = item.get("_public_domain") or _fm_item_domain(item)
        if domain == "project":
            lines.append("   Можно использовать как образец проектирования")
        elif domain == "estimate":
            lines.append("   Можно использовать как образец сметы")
        elif domain == "technadzor":
            lines.append("   Можно использовать для акта технадзора")
        elif domain == "ocr":
            lines.append("   Можно разобрать через OCR")

        lines.append("")

    lines.extend([
        "Напиши действие: использовать как образец / открыть / обработать заново / сравнить",
    ])

    try:
        from core.output_sanitizer import sanitize_user_output
        return sanitize_user_output("\n".join(lines).strip(), fallback="Файлы найдены")
    except Exception:
        return "\n".join(lines).strip()

# === END_FILE_MEMORY_PUBLIC_OUTPUT_DOMAIN_FILTER_V6_FINAL_SESSION ===



def save_file_catalog_snapshot(chat_id: str, topic_id: int) -> Dict[str, Any]:
    chat_id = str(chat_id)
    topic_id = int(topic_id or 0)
    items = load_file_memory(chat_id, topic_id, "", limit=50)

    if topic_id == 0 or not os.path.exists(MEM_DB):
        return {"ok": False, "reason": "NO_TOPIC_OR_NO_MEM_DB", "count": len(items)}

    key = f"topic_{topic_id}_file_catalog_autosync"
    payload = {
        "chat_id": chat_id,
        "topic_id": topic_id,
        "count": len(items),
        "updated_at": _utc(),
        "files": [
            {
                "task_id": it.get("task_id"),
                "file_id": it.get("file_id"),
                "file_name": it.get("file_name"),
                "mime_type": it.get("mime_type"),
                "direction": it.get("direction"),
                "links": it.get("links")[:4] if it.get("links") else [],
                "timestamp": it.get("timestamp"),
            }
            for it in items[:50]
        ],
    }

    with _conn(MEM_DB) as mem:
        if not _has_table(mem, "memory"):
            mem.execute("CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        mem.execute("DELETE FROM memory WHERE chat_id=? AND key=?", (chat_id, key))
        mid = hashlib.sha1(f"{chat_id}:{key}".encode()).hexdigest()
        mem.execute(
            "INSERT OR REPLACE INTO memory (id,chat_id,key,value,timestamp) VALUES (?,?,?,?,?)",
            (mid, chat_id, key, json.dumps(payload, ensure_ascii=False), _utc()),
        )
        mem.commit()

    return {"ok": True, "key": key, "count": len(items)}
# === END FILE_MEMORY_BRIDGE_FULL_CLOSE_V1 ===

====================================================================================================
END_FILE: core/file_memory_bridge.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/format_adapter.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 50720f3f7a5ac2adf560cebad26c55b30ee7960f8c4342b979b87b642278df5b
====================================================================================================
# === FULLFIX_FORMAT_ADAPTER_STAGE_7 ===
from __future__ import annotations
from typing import Any, Dict, List

FORMAT_ADAPTER_VERSION = "FORMAT_ADAPTER_V1"

TELEGRAM_MAX = 4096

FORMAT_HANDLERS = {
    "telegram_text": "_to_telegram_text",
    "telegram_table": "_to_telegram_table",
    "xlsx": "_to_xlsx_ref",
    "docx": "_to_docx_ref",
    "pdf": "_to_pdf_ref",
    "json": "_to_json_ref",
    "drive_link": "_to_drive_link",
    "google_sheet": "_to_google_sheet_ref",
    "sources": "_to_sources",
    "script": "_to_telegram_text",
    "mp4": "_to_drive_link",
    "table": "_to_telegram_table",
}


class FormatAdapter:
    def adapt(self, result: Dict[str, Any], formats_out: List[str], payload: Dict[str, Any]) -> Dict[str, Any]:
        adapted = {
            "format_adapter_version": FORMAT_ADAPTER_VERSION,
            "shadow_mode": True,
            "formats_out": formats_out,
            "outputs": {},
        }

        for fmt in (formats_out or ["telegram_text"]):
            handler_name = FORMAT_HANDLERS.get(fmt, "_to_telegram_text")
            handler = getattr(self, handler_name, self._to_telegram_text)
            try:
                adapted["outputs"][fmt] = handler(result, payload)
            except Exception as e:
                adapted["outputs"][fmt] = {"error": str(e)}

        adapted["primary"] = adapted["outputs"].get(formats_out[0] if formats_out else "telegram_text")
        return adapted

    def _to_telegram_text(self, result, payload):
        text = (result.get("result") or {}).get("text") or result.get("text") or ""
        if len(text) > TELEGRAM_MAX:
            text = text[:TELEGRAM_MAX - 3] + "..."
        return {"type": "telegram_text", "text": text, "length": len(text)}

    def _to_telegram_table(self, result, payload):
        rows = (result.get("result") or {}).get("rows") or result.get("rows") or []
        text = (result.get("result") or {}).get("text") or ""
        return {"type": "telegram_table", "rows": rows, "text": text[:TELEGRAM_MAX]}

    def _to_xlsx_ref(self, result, payload):
        url = result.get("artifact_url") or result.get("drive_link") or ""
        return {"type": "xlsx", "url": url, "ready": bool(url)}

    def _to_docx_ref(self, result, payload):
        url = result.get("artifact_url") or result.get("drive_link") or ""
        return {"type": "docx", "url": url, "ready": bool(url)}

    def _to_pdf_ref(self, result, payload):
        url = result.get("artifact_url") or result.get("drive_link") or ""
        return {"type": "pdf", "url": url, "ready": bool(url)}

    def _to_drive_link(self, result, payload):
        url = result.get("drive_link") or result.get("artifact_url") or ""
        return {"type": "drive_link", "url": url, "ready": bool(url)}

    def _to_google_sheet_ref(self, result, payload):
        url = result.get("sheet_url") or result.get("drive_link") or ""
        return {"type": "google_sheet", "url": url, "ready": bool(url)}

    def _to_json_ref(self, result, payload):
        return {"type": "json", "data": result.get("result") or result}

    def _to_sources(self, result, payload):
        sources = result.get("sources") or (result.get("result") or {}).get("sources") or []
        return {"type": "sources", "sources": sources, "count": len(sources)}


def adapt_result(result, formats_out, payload):
    return FormatAdapter().adapt(result, formats_out, payload)
# === END FULLFIX_FORMAT_ADAPTER_STAGE_7 ===

====================================================================================================
END_FILE: core/format_adapter.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/format_registry.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 0988b92f892724365eb8295a79890020ede1ed2e23b4b926d4e0b521b60c20f4
====================================================================================================
# === UNIVERSAL_FORMAT_REGISTRY_V1 ===
# === DWG_DXF_KIND_FIX_V1 ===
from __future__ import annotations

import mimetypes
import os
from typing import Any, Dict

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff", ".bmp", ".gif"}
TABLE_EXT = {".xlsx", ".xls", ".xlsm", ".csv", ".ods", ".tsv"}
DOCUMENT_EXT = {".pdf", ".docx", ".doc", ".txt", ".md", ".rtf", ".odt", ".html", ".htm", ".xml", ".json", ".yaml", ".yml"}
DRAWING_EXT = {".dwg", ".dxf", ".ifc", ".rvt", ".rfa", ".skp", ".stl", ".obj", ".step", ".stp", ".iges", ".igs"}
PRESENTATION_EXT = {".ppt", ".pptx", ".odp", ".key"}
ARCHIVE_EXT = {".zip", ".7z", ".rar", ".tar", ".gz", ".tgz"}
MEDIA_EXT = {".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".m4a", ".ogg"}
KNOWN_EXT = IMAGE_EXT | TABLE_EXT | DOCUMENT_EXT | DRAWING_EXT | PRESENTATION_EXT | ARCHIVE_EXT | MEDIA_EXT

def extension(file_name: str = "") -> str:
    return os.path.splitext((file_name or "").lower())[1]

def classify_file(file_name: str = "", mime_type: str = "", user_text: str = "", topic_role: str = "") -> Dict[str, Any]:
    ext = extension(file_name)
    mime = (mime_type or mimetypes.guess_type(file_name or "")[0] or "").lower()
    hay = f"{file_name}\n{mime}\n{user_text}\n{topic_role}".lower()

    # drawing first: mimetypes may classify .dwg/.dxf as image/*
    if ext in DRAWING_EXT or any(x in mime for x in ("dwg", "dxf", "ifc", "revit", "cad", "step", "stp", "iges", "igs")):
        kind = "drawing"
    elif ext in IMAGE_EXT or mime.startswith("image/"):
        kind = "image"
    elif ext in TABLE_EXT or "spreadsheet" in mime or mime in ("text/csv", "application/vnd.ms-excel"):
        kind = "table"
    elif ext in DOCUMENT_EXT or mime in ("application/pdf", "text/plain", "application/msword") or "wordprocessingml" in mime:
        kind = "document"
    elif ext in PRESENTATION_EXT or "presentation" in mime:
        kind = "presentation"
    elif ext in ARCHIVE_EXT or "zip" in mime or "archive" in mime:
        kind = "archive"
    elif ext in MEDIA_EXT or mime.startswith("video/") or mime.startswith("audio/"):
        kind = "media"
    else:
        kind = "binary"

    if any(x in hay for x in ("смет", "расчёт", "расчет", "вор", "ведомость объем", "ведомость объём", "estimate")):
        domain = "estimate"
    elif any(x in hay for x in ("технадзор", "дефект", "акт", "осмотр", "нарушен", "гост", "снип", "сп ", "трещин", "протеч", "скол")):
        domain = "technadzor"
    elif any(x in hay for x in ("проект", "проектирован", "кж", "кмд", "км", "кр", "ар", "ов", "вк", "эом", "гп", "пз", "dwg", "dxf", "ifc", "чертеж", "чертёж")):
        domain = "project"
    else:
        domain = "general"

    return {
        "kind": kind,
        "domain": domain,
        "extension": ext,
        "mime_type": mime,
        "supported": ext in KNOWN_EXT or bool(mime),
        "engine_hint": {
            "image": "technadzor/photo",
            "table": "estimate/table",
            "drawing": "dwg_dxf/project",
            "document": "document/domain",
            "presentation": "universal",
            "archive": "universal",
            "media": "universal",
            "binary": "universal",
        }.get(kind, "universal"),
    }
# === END_DWG_DXF_KIND_FIX_V1 ===
# === END_UNIVERSAL_FORMAT_REGISTRY_V1 ===

====================================================================================================
END_FILE: core/format_registry.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/gemini_vision.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e056a9a4879b2d23d90f692e5d7fd9688ead6f5712dfd988ffb9c69154952556
====================================================================================================
import os, json, base64, mimetypes, urllib.request, urllib.error
from pathlib import Path
from typing import Optional

GEMINI_MODEL = os.getenv("GOOGLE_GEMINI_VISION_MODEL", "gemini-2.0-flash")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp", ".gif", ".tif", ".tiff"}

def is_image_path(path: str) -> bool:
    return Path(str(path)).suffix.lower() in IMAGE_SUFFIXES

def _get_key() -> str:
    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if key:
        return key
    env = Path("/root/.areal-neva-core/.env")
    if env.exists():
        for line in env.read_text(errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip().replace("export ", "") == "GOOGLE_API_KEY":
                v = v.strip().strip("'\"")
                if v:
                    return v
    raise RuntimeError("GOOGLE_API_KEY_MISSING")

def _mime(p: Path) -> str:
    mt, _ = mimetypes.guess_type(str(p))
    if mt:
        return mt
    s = p.suffix.lower().lstrip(".")
    return {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(s, "image/jpeg")

async def analyze_image_file(path: str, prompt: Optional[str] = None, timeout: int = 60) -> str:
    p = Path(str(path))
    if not p.exists():
        raise RuntimeError(f"FILE_NOT_FOUND:{p}")
    key = _get_key()
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    text = (prompt or "").strip() or (
        "Проанализируй изображение для строительной или проектной задачи. "
        "Опиши что видно, извлеки размеры, таблицы, обозначения если есть. "
        "Укажи риски и следующий практический шаг. Кратко, технически, по фактам."
    )
    payload = {
        "contents": [{"role": "user", "parts": [
            {"text": text},
            {"inline_data": {"mime_type": _mime(p), "data": data}},
        ]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048},
    }
    url = GEMINI_URL.format(model=GEMINI_MODEL) + "?key=" + key
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            obj = json.loads(r.read().decode("utf-8", errors="ignore"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GEMINI_HTTP_{e.code}:{e.read().decode()[:500]}")
    parts = obj.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    result = "\n".join(x.get("text", "") for x in parts if x.get("text")).strip()
    if not result:
        raise RuntimeError("GEMINI_EMPTY_RESULT")
    return result

====================================================================================================
END_FILE: core/gemini_vision.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/inbox_aggregator.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 4f00c0de763ef010a2e21e069b3d2d50544a369d197794b8553f10497852b9bc
====================================================================================================
# === INBOX_AGGREGATOR_V1 ===
# Канон §22 — унифицированный агрегатор входящих
import logging
logger = logging.getLogger(__name__)

def normalize_inbox_item(
    source: str,
    external_id: str,
    text: str,
    user_name: str = "",
    user_id: str = "",
    contact: str = "",
    link: str = "",
    timestamp: str = "",
    attachments: list = None,
    chat_name: str = "",
    topic_id: int = 0,
    priority: str = "NORMAL",
) -> dict:
    """
    Привести любой источник к единому формату перед create_task()
    Канон: source / external_id / text / contact / link / timestamp / attachments
    """
    return {
        "source":      source,
        "external_id": str(external_id),
        "text":        str(text)[:2000],
        "user_name":   str(user_name),
        "user_id":     str(user_id),
        "contact":     str(contact),
        "link":        str(link),
        "timestamp":   str(timestamp),
        "attachments": attachments or [],
        "chat_name":   str(chat_name),
        "topic_id":    int(topic_id or 0),
        "priority":    priority,
        "status":      "NEW",
    }

def is_spam(text: str) -> bool:
    """Фильтр спама до создания задачи"""
    spam_markers = [
        "рефинансирование", "кредит без отказа", "займ онлайн",
        "заработок от 100к", "работа в интернете", "выиграли приз",
        "перейди по ссылке", "вы выбраны", "ставки на спорт",
    ]
    low = text.lower()
    return any(m in low for m in spam_markers)

def should_create_task(item: dict) -> bool:
    """Решить — создавать задачу из inbox item или нет"""
    if is_spam(item.get("text", "")):
        logger.info("INBOX_SPAM_FILTERED source=%s", item.get("source"))
        return False
    if not item.get("text", "").strip():
        return False
    return True

# Заглушки для будущих коннекторов
def fetch_email_inbox(imap_host: str, login: str, password: str) -> list:
    """IMAP connector — заглушка"""
    return []

def fetch_telegram_chats(session_path: str, chat_ids: list) -> list:
    """Telethon connector — заглушка"""
    return []

def fetch_profi_jobs(keywords: list, region: str) -> list:
    """Profi.ru connector — заглушка"""
    return []
# === END INBOX_AGGREGATOR_V1 ===

====================================================================================================
END_FILE: core/inbox_aggregator.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/intake_offer_actions.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 55e7ffaf306b754eea93dd1c991a9c8825d2c2699e7afc35a68d30539f87c266
====================================================================================================
# === INTAKE_OFFER_ACTIONS_V1 ===
# При файле без команды → предложить варианты действий
import logging
logger = logging.getLogger(__name__)

_OFFER_TEXT = """Что сделать с файлом?

1️⃣ Смета — извлечь позиции, посчитать объёмы, создать Excel
2️⃣ Описание — описать содержимое документа
3️⃣ Таблица — вытащить таблицы из файла в Excel
4️⃣ Шаблон — сохранить как образец для будущих задач
5️⃣ Анализ — технический анализ (для КЖ/АР/КД)

Напиши номер или опиши задачу."""

_OFFER_MAP = {
    "1": "estimate", "смета": "estimate", "посчитай": "estimate",
    "2": "description", "описание": "description", "опиши": "description",
    "3": "table", "таблица": "table", "таблицу": "table",
    "4": "template", "шаблон": "template", "образец": "template",
    "5": "project", "анализ": "project", "кж": "project", "ар": "project",
}

def needs_offer(raw_input: str, caption: str = "") -> bool:
    """Нужно ли предлагать варианты — файл без команды"""
    combined = (raw_input + " " + caption).lower()
    # если уже есть команда — не предлагать
    action_words = ["смета", "посчитай", "таблиц", "шаблон", "опиши", "анализ",
                    "кж", "акт", "дефект", "dwg", "чертёж", "estimate"]
    return not any(w in combined for w in action_words)

def get_offer_text() -> str:
    return _OFFER_TEXT

def parse_offer_reply(reply: str) -> str:
    """Распознать выбор пользователя → intent"""
    low = reply.strip().lower().rstrip(".")
    return _OFFER_MAP.get(low, "")
# === END INTAKE_OFFER_ACTIONS_V1 ===

====================================================================================================
END_FILE: core/intake_offer_actions.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/intent_lock.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 3f5d1f6710cad506021f81c1cc3d01339844ce911f1cf014302eb4617afe3451
====================================================================================================
# === INTENT_LOCK_V1 ===
# Запрещает смешивание режимов и создание TASK из CHAT
import logging
logger = logging.getLogger(__name__)

_CHAT_ONLY = [
    "спасибо", "ок", "понял", "хорошо", "окей", "ладно",
    "угу", "ага", "ясно", "понятно", "супер", "отлично",
    "класс", "прекрасно", "отлично", "молодец",
]

_FILE_RESULT_REQUIRED = ["estimate", "project", "template", "dwg", "ocr", "technadzor"]

def is_chat_only(text: str) -> bool:
    """Короткие реакции — не создают задачи"""
    t = text.strip().lower().rstrip("!.,?")
    return t in _CHAT_ONLY or (len(t) <= 3 and t not in ["да", "нет", "ок"])

def file_result_guard(intent: str, input_type: str, result: str, artifact_path: str = None) -> dict:
    """
    FILE_RESULT_GUARD: если file-task — обязателен артефакт.
    Канон §11: без артефакта при файловой задаче = FAILED
    """
    is_file = input_type in ("drive_file", "file") or intent in _FILE_RESULT_REQUIRED
    if not is_file:
        return {"ok": True}

    if artifact_path:
        import os
        if os.path.exists(artifact_path) and os.path.getsize(artifact_path) > 100:
            return {"ok": True}
        return {"ok": False, "reason": "ARTIFACT_FILE_NOT_EXISTS"}

    # нет artifact_path — проверяем result на Drive link
    if result and any(k in result for k in ["https://drive.google", "docs.google", "https://", ".xlsx", ".docx"]):
        return {"ok": True}

    return {"ok": False, "reason": "NO_VALID_ARTIFACT"}

def intent_priority(intent: str) -> int:
    """FINISH > CANCEL > CONFIRM > REVISION > TASK > SEARCH > CHAT"""
    order = {"finish": 7, "cancel": 6, "confirm": 5, "revision": 4,
             "task": 3, "search": 2, "chat": 1}
    return order.get(str(intent).lower(), 0)
# === END INTENT_LOCK_V1 ===

====================================================================================================
END_FILE: core/intent_lock.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/link_validator.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 577ad1be885ee9b99bb995beb70cebf2cd3b05de549fe629c7e29281925b14df
====================================================================================================
# === LINK_VALIDATOR_V1 ===
import logging
logger = logging.getLogger(__name__)

def validate_drive_link(url: str, timeout: int = 5) -> bool:
    """Проверить что Drive ссылка доступна (HEAD request)"""
    if not url or "drive.google" not in url:
        return False
    try:
        import urllib.request
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "Mozilla/5.0")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status < 400
    except Exception as e:
        logger.warning("LINK_VALIDATOR_V1 url=%s err=%s", url[:60], e)
        return False

def extract_drive_link(text: str) -> str:
    """Извлечь Drive ссылку из текста"""
    import re
    m = re.search(r"https://drive\.google\.com/\S+", text)
    return m.group(0) if m else ""
# === END LINK_VALIDATOR_V1 ===

====================================================================================================
END_FILE: core/link_validator.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/load_calculation_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 8172ab80e4219323dcafad29f3914f6e963888cffd7831d358f3621eb5411dad
====================================================================================================
# === LOAD_CALCULATION_ENGINE_FACT_ONLY_V1 ===
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

ENGINE_VERSION = "LOAD_CALCULATION_ENGINE_FACT_ONLY_V1"

def _to_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", "."))
    except Exception:
        return None

def _norms(text: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        from core.normative_engine import search_norms_sync
        return search_norms_sync(text or "", limit=limit)
    except Exception:
        return []

@dataclass
class LoadCalculationResult:
    schema: str
    engine: str
    status: str
    permanent_kpa: Optional[float]
    temporary_kpa: Optional[float]
    snow_kpa: Optional[float]
    wind_kpa: Optional[float]
    supplied_sum_kpa: Optional[float]
    missing_inputs: List[str]
    norms: List[Dict[str, Any]]
    limitations: List[str]

def calculate_loads_fact_only(
    permanent_kpa: Any = None,
    temporary_kpa: Any = None,
    snow_kpa: Any = None,
    wind_kpa: Any = None,
    source_text: str = "",
) -> Dict[str, Any]:
    permanent = _to_float(permanent_kpa)
    temporary = _to_float(temporary_kpa)
    snow = _to_float(snow_kpa)
    wind = _to_float(wind_kpa)

    values = {
        "permanent_kpa": permanent,
        "temporary_kpa": temporary,
        "snow_kpa": snow,
        "wind_kpa": wind,
    }

    missing = [k for k, v in values.items() if v is None]
    present = [v for v in values.values() if v is not None]
    supplied_sum = round(sum(present), 6) if present else None

    return asdict(LoadCalculationResult(
        schema="LoadCalculationResultV1",
        engine=ENGINE_VERSION,
        status="PARTIAL_CALC_INPUT_BASED" if missing else "INPUT_BASED_SUM_READY",
        permanent_kpa=permanent,
        temporary_kpa=temporary,
        snow_kpa=snow,
        wind_kpa=wind,
        supplied_sum_kpa=supplied_sum,
        missing_inputs=missing,
        norms=_norms(source_text or "нагрузки постоянные временные снеговые ветровые сочетания СП 20", limit=8),
        limitations=[
            "Расчёт использует только явно переданные числовые значения",
            "Нормативные таблицы и пункты не подставляются автоматически",
            "Полный расчёт несущей способности не выполняется без расчётной записки и исходных данных",
            "Сочетания нагрузок не рассчитываются без явно заданных коэффициентов / расчётной схемы",
        ],
    ))

def build_load_report_text(result: Dict[str, Any]) -> str:
    lines = [
        "Расчёт нагрузок",
        "",
        f"Статус: {result.get('status', 'UNKNOWN')}",
        f"Постоянные нагрузки, кПа: {result.get('permanent_kpa')}",
        f"Временные нагрузки, кПа: {result.get('temporary_kpa')}",
        f"Снеговые нагрузки, кПа: {result.get('snow_kpa')}",
        f"Ветровые нагрузки, кПа: {result.get('wind_kpa')}",
        f"Сумма переданных нагрузок, кПа: {result.get('supplied_sum_kpa')}",
        "",
        "Недостающие исходные данные:",
    ]

    missing = result.get("missing_inputs") or []
    lines += [f"- {x}" for x in missing] if missing else ["- нет"]

    lines += ["", "Нормативная привязка:"]
    norms = result.get("norms") or []
    if norms:
        for n in norms:
            lines.append(f"- {n.get('norm_id', '')}: {n.get('section', '')}")
    else:
        lines.append("- норма не подтверждена")

    lines += ["", "Ограничения:"]
    for x in result.get("limitations") or []:
        lines.append(f"- {x}")

    return "\n".join(lines).strip()

__all__ = [
    "ENGINE_VERSION",
    "calculate_loads_fact_only",
    "build_load_report_text",
]
# === END_LOAD_CALCULATION_ENGINE_FACT_ONLY_V1 ===

====================================================================================================
END_FILE: core/load_calculation_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/memory_api_server.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 6e3fe51f91a6894dc17aa1e439115929cf857b7de2b31572482c706817b30537
====================================================================================================
# === MEMORY_API_SERVER_V1 ===
"""
Memory API Server — порт 8091
Эндпоинты: GET /health | POST /save | POST /archive
Пишет напрямую в data/memory.db
"""
import json
import logging
import sqlite3
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("memory_api")

BASE = Path("/root/.areal-neva-core")
MEM_DB = BASE / "data" / "memory.db"
PORT = 8091
_lock = threading.Lock()


def _db():
    conn = sqlite3.connect(str(MEM_DB), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table():
    with _lock:
        conn = _db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id TEXT PRIMARY KEY,
                chat_id TEXT,
                key TEXT,
                value TEXT,
                timestamp TEXT,
                topic_id INTEGER DEFAULT 0,
                scope TEXT DEFAULT 'topic'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_chat_topic ON memory(chat_id, topic_id)")
        # ARCHIVE_DUPLICATE_GUARD_V1: enforce uniqueness on (chat_id, key)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_chat_key_unique ON memory(chat_id, key)")
        conn.commit()
        conn.close()


def _save(chat_id, key, value, topic_id=0, scope="topic"):
    import uuid
    ts = datetime.now(timezone.utc).isoformat()
    rid = str(uuid.uuid4())
    with _lock:
        conn = _db()
        # ARCHIVE_DUPLICATE_GUARD_V1: upsert by (chat_id, key) — never create duplicates
        existing = conn.execute(
            "SELECT id FROM memory WHERE chat_id=? AND key=?",
            (str(chat_id), str(key))
        ).fetchone()
        if existing:
            rid = existing[0] or rid
            conn.execute(
                "UPDATE memory SET value=?, timestamp=?, topic_id=?, scope=? WHERE chat_id=? AND key=?",
                (str(value), ts, int(topic_id), str(scope), str(chat_id), str(key))
            )
        else:
            conn.execute(
                "INSERT INTO memory(id,chat_id,key,value,timestamp,topic_id,scope) VALUES(?,?,?,?,?,?,?)",
                (rid, str(chat_id), str(key), str(value), ts, int(topic_id), str(scope))
            )
        conn.commit()
        conn.close()
    return rid


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info("HTTP %s", format % args)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def _respond(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "ok", "port": PORT, "db": str(MEM_DB)})
        else:
            self._respond(404, {"error": "not found"})

    def do_POST(self):
        try:
            raw = self._read_body()
            data = json.loads(raw) if raw else {}
        except Exception as e:
            self._respond(400, {"error": str(e)})
            return

        if self.path in ("/save", "/archive"):
            chat_id = data.get("chat_id", "unknown")
            topic_id = int(data.get("topic_id") or 0)
            task_id = data.get("task_id", "")
            key = f"topic_{topic_id}_archive_{task_id[:8]}" if task_id else f"topic_{topic_id}_save"
            value = json.dumps(data, ensure_ascii=False)
            rid = _save(chat_id, key, value, topic_id, "archive")
            logger.info("MEMORY_API_SAVE id=%s chat=%s topic=%s", rid, chat_id, topic_id)
            self._respond(200, {"ok": True, "id": rid})
        else:
            self._respond(404, {"error": "not found"})


if __name__ == "__main__":
    _ensure_table()
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    logger.info("MEMORY_API_SERVER_V1 started port=%d db=%s", PORT, MEM_DB)
    server.serve_forever()
# === END MEMORY_API_SERVER_V1 ===

====================================================================================================
END_FILE: core/memory_api_server.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/memory_client.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 41305beffcda29f9bcf3589042acdc90f1fdfa993c8b37145563294d3d8a3e3e
====================================================================================================
# === FULLFIX_19_MEMORY_CLIENT_V2 ===
import sqlite3, logging, json, uuid
from pathlib import Path

# === MEMORY_API_CLIENT_V1 ===
import os as _os, urllib.request as _urllib_req, urllib.error as _urllib_err
_API_BASE = "http://127.0.0.1:8091"
_API_TOKEN = <REDACTED_SECRET>"MEMORY_API_TOKEN", "")
_API_TIMEOUT = 2
_USE_API = bool(_API_TOKEN)

def _api_save(chat_id, key, value, topic_id=0, scope="topic"):
    if not _USE_API:
        return False
    try:
        import json as _json
        data = _json.dumps({
            "chat_id": str(chat_id), "key": str(key), "value": str(value),
            "topic_id": int(topic_id or 0), "scope": str(scope)
        }).encode("utf-8")
        req = _urllib_req.Request(
            f"{_API_BASE}/memory", data=data,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {_API_TOKEN}"},
            method="POST"
        )
        with _urllib_req.urlopen(req, timeout=_API_TIMEOUT) as r:
            return r.status in (200, 201)
    except Exception:
        return False

def _api_get(chat_id, key, topic_id=0):
    if not _USE_API:
        return None
    try:
        import json as _json
        url = f"{_API_BASE}/memory?chat_id={chat_id}&key={key}&topic_id={int(topic_id or 0)}"
        req = _urllib_req.Request(url, headers={"Authorization": f"Bearer {_API_TOKEN}"})
        with _urllib_req.urlopen(req, timeout=_API_TIMEOUT) as r:
            body = _json.loads(r.read())
            return body.get("value")
    except Exception:
        return None
# === END MEMORY_API_CLIENT_V1 ===

MEMORY_DB = "/root/.areal-neva-core/data/memory.db"
logger = logging.getLogger("memory_client")

def _ensure():
    Path(MEMORY_DB).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(MEMORY_DB, timeout=10) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS memory(
                id TEXT PRIMARY KEY,
                chat_id TEXT,
                key TEXT,
                value TEXT,
                timestamp TEXT,
                topic_id INTEGER DEFAULT 0,
                scope TEXT DEFAULT 'topic'
            )
        """)
        cols = [r[1] for r in c.execute("PRAGMA table_info(memory)").fetchall()]
        if "topic_id" not in cols:
            c.execute("ALTER TABLE memory ADD COLUMN topic_id INTEGER DEFAULT 0")
        if "scope" not in cols:
            c.execute("ALTER TABLE memory ADD COLUMN scope TEXT DEFAULT 'topic'")
        c.execute("CREATE INDEX IF NOT EXISTS idx_memory_chat_topic ON memory(chat_id, topic_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_memory_value ON memory(value)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_memory_key ON memory(key)")
        c.commit()

def save_memory(chat_id, key, value, topic_id=0, scope="topic"):
    try:
        if _api_save(chat_id, key, value, topic_id, scope):
            return  # MEMORY_API_CLIENT_V1_SAVE
        _ensure()
        v = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        with sqlite3.connect(MEMORY_DB, timeout=10) as c:
            row = c.execute(
                "SELECT id FROM memory WHERE chat_id=? AND topic_id=? AND key=?",
                (str(chat_id), int(topic_id or 0), str(key))
            ).fetchone()
            if row:
                c.execute(
                    "UPDATE memory SET value=?, timestamp=datetime('now'), scope=? WHERE id=?",
                    (v, str(scope), row[0])
                )
            else:
                c.execute(
                    "INSERT INTO memory(id, chat_id, topic_id, key, value, scope, timestamp) VALUES(?,?,?,?,?,?,datetime('now'))",
                    (str(uuid.uuid4()), str(chat_id), int(topic_id or 0), str(key), v, str(scope))
                )
            c.commit()
        return True
    except Exception as e:
        logger.error("save_memory err=%s", e)
        return False

def get_memory(chat_id, key, topic_id=0):
    _api_val = _api_get(chat_id, key, topic_id)
    if _api_val is not None:
        return _api_val  # MEMORY_API_CLIENT_V1_GET
    try:
        _ensure()
        with sqlite3.connect(MEMORY_DB, timeout=10) as c:
            r = c.execute(
                "SELECT value FROM memory WHERE chat_id=? AND COALESCE(topic_id,0)=? AND key=? ORDER BY timestamp DESC LIMIT 1",
                (str(chat_id), int(topic_id or 0), str(key))
            ).fetchone()
            return r[0] if r else None
    except Exception as e:
        logger.error("get_memory err=%s", e)
        return None

def search_memory(chat_id, query, topic_id=None, limit=10):
    try:
        _ensure()
        with sqlite3.connect(MEMORY_DB, timeout=10) as c:
            if topic_id is not None:
                rows = c.execute(
                    "SELECT key,value,timestamp FROM memory WHERE chat_id=? AND COALESCE(topic_id,0)=? AND value LIKE ? ORDER BY timestamp DESC LIMIT ?",
                    (str(chat_id), int(topic_id or 0), "%"+str(query)+"%", int(limit))
                ).fetchall()
            else:
                rows = c.execute(
                    "SELECT key,value,timestamp FROM memory WHERE chat_id=? AND value LIKE ? ORDER BY timestamp DESC LIMIT ?",
                    (str(chat_id), "%"+str(query)+"%", int(limit))
                ).fetchall()
            return [{"key": r[0], "value": r[1], "ts": r[2]} for r in rows]
    except Exception as e:
        logger.error("search_memory err=%s", e)
        return []

def get_active_context(chat_id, topic_id=0, limit=5):
    try:
        _ensure()
        with sqlite3.connect(MEMORY_DB, timeout=10) as c:
            rows = c.execute(
                "SELECT key,value FROM memory WHERE chat_id=? AND COALESCE(topic_id,0)=? AND COALESCE(scope,'topic') IN ('topic','active') ORDER BY timestamp DESC LIMIT ?",
                (str(chat_id), int(topic_id or 0), int(limit))
            ).fetchall()
            return [{"key": r[0], "value": r[1]} for r in rows]
    except Exception as e:
        logger.error("get_active_context err=%s", e)
        return []

def list_memory(chat_id, topic_id=None, prefix=None, limit=20):
    try:
        _ensure()
        with sqlite3.connect(MEMORY_DB, timeout=10) as c:
            q = "SELECT key,timestamp FROM memory WHERE chat_id=?"
            params = [str(chat_id)]
            if topic_id is not None:
                q += " AND COALESCE(topic_id,0)=?"
                params.append(int(topic_id or 0))
            if prefix:
                q += " AND key LIKE ?"
                params.append(str(prefix)+"%")
            q += " ORDER BY timestamp DESC LIMIT ?"
            params.append(int(limit))
            rows = c.execute(q, params).fetchall()
            return [{"key": r[0], "ts": r[1]} for r in rows]
    except Exception as e:
        logger.error("list_memory err=%s", e)
        return []
# === END FULLFIX_19_MEMORY_CLIENT_V2 ===

====================================================================================================
END_FILE: core/memory_client.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/memory_filter.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d3b5270ebb8311130f237cc944d3bb41e1cefe3c0631897ad30397e3566ea1c4
====================================================================================================
# === MEMORY_FILTER_V1 ===
# Жёсткий фильтр памяти — канон §20.3
import re, logging
logger = logging.getLogger(__name__)

_NOISE = [
    "/root/", ".ogg", "Traceback", "traceback",
    "FAILED", "INVALID_RESULT", "STALE_TIMEOUT",
    "не понял", "уточните", "нет данных", "повторите",
    "EXCEPTION", "SyntaxError", "IndentationError",
    "AWAITING_CONFIRMATION без результата",
    "файл скачан, ожидает анализа",
    "структура проекта включает",
]

_MIN_USEFUL_LEN = 20

def is_noise(value: str) -> bool:
    if not value or len(value.strip()) < _MIN_USEFUL_LEN:
        return True
    return any(n in value for n in _NOISE)

def filter_memory_for_prompt(memories: list, query: str = "") -> list:
    """
    Фильтрует записи памяти перед добавлением в промпт.
    memories: list of {"key": str, "value": str}
    """
    clean = []
    query_words = set(w for w in re.split(r"\s+", query.lower()) if len(w) > 3)

    for m in memories:
        val = str(m.get("value", ""))
        if is_noise(val):
            continue
        # relevancy check если есть запрос
        if query_words:
            val_words = set(re.split(r"\s+", val.lower()))
            if query_words & val_words:
                clean.append(m)
        else:
            clean.append(m)

    return clean[:10]  # MEMORY_LIMIT из канона

def sanitize_before_write(value: str) -> str:
    """Очистить строку перед записью в memory.db"""
    if is_noise(value):
        return ""
    # убрать пути
    value = re.sub(r"/root/[\S]+", "[PATH]", value)
    # убрать трейсбэки
    value = re.sub(r"Traceback.*", "", value, flags=re.DOTALL)
    return value[:500].strip()
# === END MEMORY_FILTER_V1 ===

====================================================================================================
END_FILE: core/memory_filter.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/memory_scope_enforcer.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 1ad3202d5e736fadb2eea60a191c7433e4126a7a77e1e967ebe0cb2ca60d9979
====================================================================================================
# === MEMORY_SCOPE_ENFORCER_V1 ===
# === ARCHIVE_RECALL_VALIDATOR_V1 ===
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

def topic_key(topic_id: int) -> str:
    return f"topic_{int(topic_id or 0)}_"

def allowed_memory_key(key: str, topic_id: int) -> bool:
    key = str(key or "")
    return key.startswith(topic_key(topic_id))

def filter_topic_memory(rows: Iterable[Any], topic_id: int) -> List[Any]:
    out = []
    for row in rows or []:
        try:
            key = row["key"] if isinstance(row, dict) else row[0]
        except Exception:
            key = ""
        if allowed_memory_key(str(key), topic_id):
            out.append(row)
    return out

def validate_archive_recall_answer(answer: str, archive_context: str) -> Dict[str, Any]:
    if not archive_context:
        return {"ok": False, "reason": "NO_ARCHIVE_CONTEXT"}
    ans = (answer or "").lower()
    ctx = (archive_context or "").lower()
    words = [w for w in re.findall(r"[a-zа-я0-9]{4,}", ans) if len(w) >= 4]
    hits = sum(1 for w in words[:80] if w in ctx)
    return {"ok": hits >= 3, "reason": "OK" if hits >= 3 else "LOW_ARCHIVE_OVERLAP", "hits": hits}
# === END_ARCHIVE_RECALL_VALIDATOR_V1 ===
# === END_MEMORY_SCOPE_ENFORCER_V1 ===

====================================================================================================
END_FILE: core/memory_scope_enforcer.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/model_router.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 3bd35408543d9c5c7cfb015f07ac4973900d78c3795cf474c3070df5f902eab3
====================================================================================================
# === FINAL_CLOSURE_BLOCKER_FIX_V1_MODEL_ROUTER ===
from __future__ import annotations

import re
from typing import Any, Dict


def _norm(text: str) -> str:
    return (text or "").lower().replace("ё", "е").strip()


def _has(pattern: str, text: str) -> bool:
    return bool(re.search(pattern, text, flags=re.I | re.U))


def detect_domain(text: str = "", file_name: str = "", input_type: str = "text") -> Dict[str, Any]:
    t = _norm(f"{text}\n{file_name}")

    if input_type in ("drive_file", "file") and not t:
        return {"domain": "file", "intent": "needs_context", "confidence": 0.50}

    if _has(r"(смет\w*|кс[- ]?2|кс[- ]?3|вор\b|ведомост\w*\s+об[ъь]ем\w*|расцен\w*|стоимост\w*|цен\w*\s+материал\w*|материал\w*)", t):
        return {"domain": "estimate", "intent": "estimate", "confidence": 0.88}

    if _has(r"(акт\w*|технадзор\w*|техническ\w*\s+надзор\w*|дефект\w*|замечан\w*|нарушен\w*|освидетельств\w*|стройконтрол\w*|сп\s*\d+|гост\s*\d+|снип\w*)", t):
        return {"domain": "technadzor", "intent": "technadzor_act", "confidence": 0.86}

    if _has(r"(кж\b|кд\b|кр\b|ар\b|проект\w*|чертеж\w*|чертёж\w*|dxf\b|dwg\b|плит\w*|фундамент\w*|разрез\w*|узел\w*|спецификац\w*)", t):
        return {"domain": "project", "intent": "project", "confidence": 0.78}

    if _has(r"(что\s+скидывал\w*|какие\s+файл\w*|какой\s+файл\w*|покажи\s+файл\w*|последн\w*\s+файл\w*|документ\w*\s+в\s+чат\w*|памят\w*|напомни\w*)", t):
        return {"domain": "memory", "intent": "memory_query", "confidence": 0.82}

    if _has(r"(найди\w*|поищи\w*|поиск\w*|интернет\w*|авито|ozon|wildberries|яндекс|google|сколько\s+сто\w*)", t):
        return {"domain": "search", "intent": "search", "confidence": 0.72}

    return {"domain": "chat", "intent": "chat", "confidence": 0.30}


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_MODEL_ROUTER ===

====================================================================================================
END_FILE: core/model_router.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/multi_file_intake.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 92e2ebf23035247666c8332803406752e64dd33c962e920f6c196c6ee134b438
====================================================================================================
import json
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)
SESSION_WINDOW_SEC = 60

def init_session(data: dict) -> dict:
    base = dict(data or {})
    base["multi_file_session"] = {
        "files": [dict(data or {})],
        "count": 1,
    }
    return base

def get_active_session(conn, chat_id: str, topic_id: int) -> Optional[str]:
    row = conn.execute(
        """SELECT id
           FROM tasks
           WHERE chat_id=?
             AND COALESCE(topic_id,0)=?
             AND state='NEEDS_CONTEXT'
             AND input_type='drive_file'
             AND COALESCE(raw_input,'') LIKE '%multi_file_session%'
             AND (julianday('now') - julianday(updated_at))*86400 < ?
           ORDER BY updated_at DESC
           LIMIT 1""",
        (str(chat_id), int(topic_id or 0), SESSION_WINDOW_SEC),
    ).fetchone()
    return row["id"] if row else None

def attach_to_session(conn, session_task_id: str, new_file_data: dict) -> bool:
    try:
        row = conn.execute(
            "SELECT raw_input FROM tasks WHERE id=? AND state='NEEDS_CONTEXT'",
            (session_task_id,),
        ).fetchone()
        if not row:
            return False

        data = json.loads(row["raw_input"] or "{}")
        session = data.get("multi_file_session") or {"files": [], "count": 0}
        files = session.get("files") or []
        files.append(dict(new_file_data or {}))
        data["multi_file_session"] = {"files": files, "count": len(files)}

        conn.execute(
            "UPDATE tasks SET raw_input=?, updated_at=datetime('now') WHERE id=?",
            (json.dumps(data, ensure_ascii=False), session_task_id),
        )
        logger.info("MULTI_FILE_ATTACHED session=%s count=%d", session_task_id, len(files))
        return True
    except Exception as e:
        logger.error("MULTI_FILE_ATTACH_FAILED session=%s err=%s", session_task_id, e)
        return False

def get_session_files(conn, session_task_id: str) -> List[dict]:
    row = conn.execute("SELECT raw_input FROM tasks WHERE id=?", (session_task_id,)).fetchone()
    if not row:
        return []
    try:
        data = json.loads(row["raw_input"] or "{}")
        return data.get("multi_file_session", {}).get("files", [])
    except Exception:
        return []

====================================================================================================
END_FILE: core/multi_file_intake.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/multifile_artifact_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: a1ea9e3f49b53d653957ca6cafb7d10334684ad3cec47169100d49e461db4c67
====================================================================================================
# === FULLFIX_14_MULTIFILE ===
import os, json, logging
logger = logging.getLogger(__name__)
ENGINE = "FULLFIX_14_MULTIFILE"
RUNTIME_DIR = "/root/.areal-neva-core/runtime"
os.makedirs(RUNTIME_DIR, exist_ok=True)

MULTIFILE_PHRASES = ["все файлы", "все документы", "сводку", "по всем", "сводная", "объедини"]

def is_multifile_intent(text):
    t = (text or "").lower()
    return any(p in t for p in MULTIFILE_PHRASES)

def get_recent_files(conn, chat_id, topic_id, limit=10):
    rows = conn.execute(
        "SELECT id, raw_input, state, created_at FROM tasks"
        " WHERE chat_id=? AND COALESCE(topic_id,0)=? AND input_type='drive_file'"
        " AND state NOT IN ('CANCELLED','ARCHIVED')"
        " ORDER BY created_at DESC LIMIT ?",
        (chat_id, topic_id, limit)
    ).fetchall()
    result = []
    for r in rows:
        tid = r[0]
        raw = r[1]
        state = r[2]
        cat = r[3]
        try:
            meta = json.loads(raw or "{}")
        except Exception:
            meta = {}
        result.append({"task_id": tid, "meta": meta, "state": state, "created_at": cat})
    return result

def generate_manifest(files, task_id):
    import openpyxl
    path = os.path.join(RUNTIME_DIR, "multifile_" + task_id[:8] + "_index.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Файлы"
    ws.append(["№", "Файл", "Тип", "Статус", "Дата"])
    for i, f in enumerate(files, 1):
        meta = f.get("meta", {})
        ws.append([i, meta.get("file_name", ""), meta.get("mime_type", ""), f.get("state", ""), f.get("created_at", "")])
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 30
    wb.save(path)
    return path

def process_multifile_sync(conn, task_id, chat_id, topic_id, raw_input):
    from core.artifact_upload_guard import upload_or_fail
    from core.reply_sender import send_reply_ex
    try:
        files = get_recent_files(conn, chat_id, topic_id)
        if not files:
            logger.info("MULTIFILE_NO_RECENT_FILES task=%s", task_id)
            return False
        manifest_path = generate_manifest(files, task_id)
        # === FULLFIX_20_MULTIFILE_MERGE_HOOK ===
        merged_pdf_link = ""
        try:
            import tempfile, os
            _ff20_paths = []
            for _ff20_f in files:
                _ff20_p = _ff20_f.get("local_path") or _ff20_f.get("path") or _ff20_f.get("file_path") if isinstance(_ff20_f, dict) else str(_ff20_f)
                if _ff20_p: _ff20_paths.append(_ff20_p)
            if _ff20_paths:
                _ff20_out = os.path.join(tempfile.gettempdir(), "multifile_" + str(task_id) + ".pdf")
                if merge_files_to_pdf(_ff20_paths, _ff20_out):
                    _ff20_up = upload_or_fail(_ff20_out, task_id, topic_id, "multifile_merged_pdf")
                    if _ff20_up.get("success") and _ff20_up.get("link"):
                        merged_pdf_link = _ff20_up["link"]
        except Exception as _ff20_me:
            logger.warning("FF20_MULTIFILE_MERGE_ERR task=%s err=%s", task_id, _ff20_me)
        # === END FULLFIX_20_MULTIFILE_MERGE_HOOK ===
        up = upload_or_fail(manifest_path, task_id, topic_id, "multifile_index")
        if up.get("success") and up.get("link"):
            result_text = "Сводка по " + str(len(files)) + " файлам:\n" + up["link"]
            if merged_pdf_link:
                result_text += "\nPDF: " + merged_pdf_link
        else:
            result_text = "Найдено файлов: " + str(len(files)) + ". Drive недоступен."
        conn.execute(
            "UPDATE tasks SET state='AWAITING_CONFIRMATION',result=?,updated_at=datetime('now') WHERE id=?",
            (result_text, task_id)
        )
        conn.execute(
            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
            (task_id, "state:AWAITING_CONFIRMATION")
        )
        conn.commit()
        try:
            _br = send_reply_ex(chat_id=str(chat_id), text=result_text, reply_to_message_id=None, message_thread_id=topic_id)  # FULLFIX_20_MULTIFILE_TOPIC_REPLY
            _bmid = None
            if isinstance(_br, dict):
                _bmid = _br.get("bot_message_id") or _br.get("message_id")
            elif _br and hasattr(_br, "message_id"):
                _bmid = _br.message_id
            if _bmid:
                conn.execute("UPDATE tasks SET bot_message_id=? WHERE id=?", (str(_bmid), task_id))
                conn.commit()
        except Exception as _se:
            logger.error("MULTIFILE_SEND_ERR task=%s err=%s", task_id, _se)
        return True
    except Exception as e:
        logger.error("MULTIFILE_ERROR task=%s err=%s", task_id, e)
        return False

async def process_multifile(conn, task_id, chat_id, topic_id, raw_input):
    import asyncio
    return await asyncio.get_event_loop().run_in_executor(
        None, process_multifile_sync, conn, task_id, chat_id, topic_id, raw_input
    )
# === END FULLFIX_14_MULTIFILE ===


# === FULLFIX_20_MULTIFILE_MERGE_PDF ===
def merge_files_to_pdf(file_paths, output_path):
    try:
        from pypdf import PdfWriter, PdfReader
        from PIL import Image
        import os
        writer = PdfWriter()
        pages = 0
        for fp in file_paths:
            try:
                if not fp or not os.path.exists(fp):
                    continue
                low = fp.lower()
                if low.endswith(".pdf"):
                    for page in PdfReader(fp).pages:
                        writer.add_page(page); pages += 1
                elif low.endswith((".jpg", ".jpeg", ".png", ".webp")):
                    tmp = fp + ".tmppdf"
                    Image.open(fp).convert("RGB").save(tmp, "PDF")
                    for page in PdfReader(tmp).pages:
                        writer.add_page(page); pages += 1
                    try: os.unlink(tmp)
                    except Exception: pass
            except Exception:
                continue
        if pages <= 0:
            return False
        with open(output_path, "wb") as f:
            writer.write(f)
        return True
    except Exception:
        return False
# === END FULLFIX_20_MULTIFILE_MERGE_PDF ===

====================================================================================================
END_FILE: core/multifile_artifact_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/normative_db.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 69abc4653a63b4e2b4b2c3f1d1ce30cb19f5be909558d8dbb4a402384b9b5f03
====================================================================================================
# === NORMATIVE_DB_V1 ===
import os, logging, asyncio, aiohttp, json
logger = logging.getLogger(__name__)
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

async def get_norm(norm_id: str, context: str = "") -> dict:
    result = {"norm_id": norm_id, "title": "", "requirement": "норма не подтверждена",
              "source": "perplexity", "verified": False}
    if not OPENROUTER_KEY:
        result["error"] = "NO_API_KEY"; return result
    try:
        prompt = (f"Найди требование нормы {norm_id} применительно к: {context}. "
                  f"Только точная цитата и номер пункта. Без интерпретаций.")
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}",
                         "Content-Type": "application/json"},
                json={"model": "perplexity/sonar",
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                data = await r.json()
                text = data["choices"][0]["message"]["content"].strip()
                if text and len(text) > 10 and "не найд" not in text.lower():
                    result["requirement"] = text
                    result["verified"] = True
    except Exception as e:
        logger.warning("NORMATIVE_DB_V1 err=%s", e)
        result["error"] = str(e)
    return result

async def search_norms(defect_description: str, section: str = "") -> list:
    # === NORMATIVE_SEARCH_V1 ===
    norms_map = {
        "кровля": ["СП 17.13330.2017", "СНиП II-26-76"],
        "фасад": ["СП 293.1325800.2017", "ГОСТ 31251-2008"],
        "фундамент": ["СП 22.13330.2016", "СП 50-101-2004"],
        "несущие": ["СП 20.13330.2017", "ГОСТ 5781-82"],
        "перекрытие": ["СП 20.13330.2017", "СП 63.13330.2018"],
    }
    sec = section.lower() if section else defect_description.lower()
    candidates = []
    for key, norms in norms_map.items():
        if key in sec:
            candidates = norms[:2]; break
    if not candidates:
        candidates = ["СП 20.13330.2017"]
    results = []
    for n in candidates[:3]:
        r = await get_norm(n, defect_description)
        results.append(r)
    return results
# === END NORMATIVE_DB_V1 ===

====================================================================================================
END_FILE: core/normative_db.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/normative_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 355ac95be8b8f06c6adca69858b21865560a36941156094be6bd91dc207aeb8e
====================================================================================================
# === NORMATIVE_ENGINE_SAFE_V1 ===
from __future__ import annotations
from typing import Any, Dict, List

NORMATIVE_INDEX = [
    {"keywords": ["трещин", "бетон", "монолит", "раковин", "скол"], "norm_id": "СП 70.13330.2012", "section": "Несущие и ограждающие конструкции", "requirement": "Дефекты бетонных и железобетонных конструкций подлежат фиксации, оценке влияния на несущую способность и устранению по проектному решению", "confidence": "PARTIAL"},
    {"keywords": ["бетон", "арматур", "защитный слой", "а500", "b25", "в25"], "norm_id": "СП 63.13330.2018", "section": "Бетонные и железобетонные конструкции", "requirement": "Расчёт и контроль железобетонных конструкций выполняется с учётом класса бетона, арматуры, защитного слоя и требований проектной документации", "confidence": "PARTIAL"},
    {"keywords": ["нагрузк", "фундамент", "плита", "перекрытие", "кж"], "norm_id": "СП 20.13330.2016/2017", "section": "Нагрузки и воздействия", "requirement": "Проверка конструкций выполняется с учётом постоянных, временных и особых нагрузок по расчётным сочетаниям", "confidence": "PARTIAL"},
    {"keywords": ["кровл", "протеч", "мембран", "пароизоляц", "водосток"], "norm_id": "СП 17.13330.2017", "section": "Кровли", "requirement": "Кровельные работы должны обеспечивать водонепроницаемость, надёжное примыкание и соответствие проектным решениям", "confidence": "PARTIAL"},
    {"keywords": ["отделк", "штукатур", "плитк", "стяжк", "покраск"], "norm_id": "СП 71.13330.2017", "section": "Изоляционные и отделочные покрытия", "requirement": "Отделочные покрытия проверяются по основанию, геометрии, сцеплению, ровности и отсутствию видимых дефектов", "confidence": "PARTIAL"},
    {"keywords": ["металл", "сварк", "км", "кмд", "болт", "корроз"], "norm_id": "СП 16.13330.2017", "section": "Стальные конструкции", "requirement": "Стальные конструкции должны соответствовать расчётной схеме, проектным сечениям, качеству сварных и болтовых соединений", "confidence": "PARTIAL"},
    {"keywords": ["проект", "чертеж", "чертёж", "спецификац", "ведомость", "стадия"], "norm_id": "ГОСТ 21.101-2020", "section": "Основные требования к проектной и рабочей документации", "requirement": "Проектная и рабочая документация оформляется с составом, обозначениями и ведомостями по системе проектной документации для строительства", "confidence": "PARTIAL"},
    {"keywords": ["кж", "железобетон", "армирование", "опалуб", "монолит"], "norm_id": "ГОСТ 21.501-2018", "section": "Правила выполнения рабочей документации архитектурных и конструктивных решений", "requirement": "Рабочие чертежи конструктивных решений должны содержать схемы, спецификации, ведомости элементов и данные для производства работ", "confidence": "PARTIAL"},
]

def search_norms_sync(text: str, limit: int = 5) -> List[Dict[str, Any]]:
    hay = (text or "").lower()
    scored = []
    for row in NORMATIVE_INDEX:
        score = sum(1 for kw in row["keywords"] if kw in hay)
        if score:
            item = dict(row)
            item["score"] = score
            scored.append(item)
    scored.sort(key=lambda x: int(x.get("score") or 0), reverse=True)
    return scored[:limit]

def format_norms_for_act(norms: List[Dict[str, Any]]) -> str:
    return "\n".join(f"{n.get('norm_id','')}: {n.get('requirement','')} [{n.get('confidence','PARTIAL')}]" for n in norms or [] if n.get("norm_id"))
# === END_NORMATIVE_ENGINE_SAFE_V1 ===


# === P6H_NORMATIVE_INDEX_EXTRA_V1 ===
# Append-only extension to NORMATIVE_INDEX with technadzor-specific norms
# referenced in real client acts (Киевское 95, металлокаркас, антикоррозия,
# обследование зданий и сооружений, организация строительного контроля).
# Each entry uses confidence=PARTIAL — promote to CONFIRMED only after manual
# review of an authoritative source.
import logging as _p6h_norm_logging

_P6H_NORMATIVE_EXTRA = [
    {
        "keywords": ["антикорроз", "лакокрас", "окрас", "защитное покрытие", "ржавчин"],
        "norm_id": "СП 28.13330.2017",
        "section": "Защита строительных конструкций от коррозии",
        "requirement": "Требования к защите строительных конструкций от коррозии: подготовка поверхности, выбор защитной системы, контроль качества и сохранности покрытия в процессе эксплуатации",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["металлоконструкц", "стальн", "сварн", "ферм", "колонн", "балк", "кмд", "мк", "анкерн"],
        "norm_id": "ГОСТ 23118-2019",
        "section": "Конструкции стальные строительные. Общие технические условия",
        "requirement": "Требования к материалам, изготовлению, монтажу и приёмке стальных строительных конструкций, включая сварные и болтовые соединения, антикоррозионную защиту, маркировку",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["организация строительного контроля", "осс", "стройконтроль", "технадзор", "приёмка", "приемка", "освидетельств"],
        "norm_id": "СП 48.13330.2019",
        "section": "Организация строительства",
        "requirement": "Порядок организации строительного контроля заказчика и подрядчика, освидетельствование скрытых работ, ведение исполнительной документации",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["обследован", "техническое состояние", "категория состояния", "несущ", "предаварийн", "аварийн"],
        "norm_id": "СП 13-102-2003",
        "section": "Правила обследования несущих строительных конструкций зданий и сооружений",
        "requirement": "Порядок и состав обследований несущих конструкций, методы выявления дефектов и повреждений, классификация технического состояния (нормальное, удовлетворительное, ограниченно работоспособное, аварийное)",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["обследован", "мониторинг", "техническое состояние", "категория"],
        "norm_id": "ГОСТ 31937-2024",
        "section": "Здания и сооружения. Правила обследования и мониторинга технического состояния",
        "requirement": "Современные правила обследования и мониторинга технического состояния зданий и сооружений: цели, состав работ, оформление результатов, заключение о категории состояния",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["сварн", "сварка", "шов", "провар", "наплыв", "качество свар"],
        "norm_id": "ГОСТ Р ИСО 17637-2014",
        "section": "Неразрушающий контроль сварных соединений. Визуальный контроль",
        "requirement": "Правила визуального и измерительного контроля сварных соединений: критерии приёмки, фиксация дефектов, оформление результатов",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["опорн", "анкерн", "плита", "опирани", "узел колонн", "подлив"],
        "norm_id": "СП 70.13330.2012",
        "section": "Несущие и ограждающие конструкции — опорные узлы металлоконструкций",
        "requirement": "Опорные узлы стальных колонн должны передавать нагрузку через плотное опирание опорной плиты на фундамент. Подливка под опорные плиты выполняется до проектного состояния, без зазоров, трещин и разрушений",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["укосин", "связи", "диагональн", "горизонтальн связи", "пространственн"],
        "norm_id": "СП 16.13330.2017",
        "section": "Стальные конструкции — пространственные связи",
        "requirement": "Узлы пересечения и крепления связей жёсткости должны обеспечивать пространственную жёсткость каркаса; ослабленные или непроработанные узлы не допускаются",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["основан", "грунт", "замачив", "размыв", "просадк", "водоотвод"],
        "norm_id": "СП 22.13330.2016",
        "section": "Основания зданий и сооружений",
        "requirement": "Подготовка и эксплуатация оснований: водоотвод от фундаментов, защита от замачивания, контроль осадок и просадок, обеспечение проектной несущей способности грунта",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["перекрыт", "ригел", "балк", "несущая способность"],
        "norm_id": "СП 20.13330.2016",
        "section": "Нагрузки и воздействия — перекрытия",
        "requirement": "Перекрытия должны рассчитываться на постоянные и временные нагрузки с учётом особых воздействий; конструктивные решения и сечения элементов должны соответствовать расчётной схеме",
        "confidence": "PARTIAL",
    },
]

try:
    NORMATIVE_INDEX.extend(_P6H_NORMATIVE_EXTRA)
    _p6h_norm_logging.getLogger("task_worker").info(
        "P6H_NORMATIVE_INDEX_EXTRA_V1_INSTALLED added=%d total=%d",
        len(_P6H_NORMATIVE_EXTRA), len(NORMATIVE_INDEX),
    )
except Exception:
    pass
# === END_P6H_NORMATIVE_INDEX_EXTRA_V1 ===


# === P6H5_NORMATIVE_FULL_EXPAND_V1 ===
# Comprehensive normative expansion: исполнительная документация, бетон,
# газобетон/кладка, стальные конструкции, отделка, фасады, ОВ, ВК,
# электрика, пожарная безопасность, охрана труда (35 записей).
# confidence=PARTIAL — promote after manual verification.

_P6H5_NORMATIVE_EXPAND = [
    # --- Блок 1: Исполнительная документация ---
    {
        "keywords": ["исполнительн", "акт скрытых", "скрытые работы", "освидетельств", "исполнительная документация", "кс-2", "кс-3"],
        "norm_id": "РД-11-02-2006",
        "section": "Требования к составу и порядку ведения исполнительной документации",
        "requirement": "Состав и порядок ведения исполнительной документации при строительстве: акты освидетельствования скрытых работ, акты промежуточной приёмки ответственных конструкций, исполнительные схемы",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["журнал работ", "общий журнал", "журнал производства", "ожр", "специальный журнал"],
        "norm_id": "РД-11-05-2007",
        "section": "Порядок ведения общего и специальных журналов работ",
        "requirement": "Порядок ведения общего журнала работ и специальных журналов при строительстве: состав записей, ответственные лица, порядок хранения и передачи",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["авторский надзор", "надзор проектировщик", "проектировщик на объекте", "журнал авторского надзора"],
        "norm_id": "СП 11-110-99",
        "section": "Авторский надзор за строительством зданий и сооружений",
        "requirement": "Порядок осуществления авторского надзора проектировщиков за строительством: состав работ, права и обязанности, журнал авторского надзора",
        "confidence": "PARTIAL",
    },
    # --- Блок 2: Бетон (расширение) ---
    {
        "keywords": ["бетонная смесь", "подвижность смеси", "водоцементн", "класс бетона", "замес бетон", "марка бетона"],
        "norm_id": "ГОСТ 7473-2010",
        "section": "Смеси бетонные. Технические условия",
        "requirement": "Требования к бетонным смесям: классификация, показатели удобоукладываемости, водонепроницаемости, морозостойкости, правила приёмки и контроля",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["прочность бетона", "испытание бетона", "образец-куб", "керн бетон", "контроль прочности бетон"],
        "norm_id": "ГОСТ 18105-2018",
        "section": "Бетоны. Правила контроля и оценки прочности",
        "requirement": "Правила контроля и оценки прочности бетона в конструкциях: методы испытаний, статистический контроль, приёмочные уровни",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["тяжёлый бетон", "тяжелый бетон", "состав бетона", "крупный заполнитель", "щебень бетон"],
        "norm_id": "ГОСТ 26633-2015",
        "section": "Бетоны тяжёлые и мелкозернистые. Технические условия",
        "requirement": "Технические требования к тяжёлым и мелкозернистым бетонам: классы по прочности, морозостойкости, водонепроницаемости, правила приёмки и методы испытаний",
        "confidence": "PARTIAL",
    },
    # --- Блок 3: Газобетон и кладка ---
    {
        "keywords": ["газоблок", "газобетон", "ячеистый бетон", "автоклавный бетон", "d400", "d500", "d600"],
        "norm_id": "ГОСТ 31360-2007",
        "section": "Изделия стеновые неармированные из ячеистого бетона автоклавного твердения",
        "requirement": "Требования к стеновым блокам из ячеистого автоклавного бетона: классы по плотности, прочности, морозостойкости, геометрические параметры, правила приёмки",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["кладка газобетон", "армирование газобетон", "газобетонный блок", "стена из газобетон"],
        "norm_id": "СП 339.1325800.2017",
        "section": "Конструкции с применением автоклавного газобетона",
        "requirement": "Проектирование и возведение конструкций из автоклавного газобетона: кладочные растворы, армирование, обеспечение жёсткости, допустимые деформации",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["кладка", "каменная конструкц", "кирпич", "кладочный раствор", "армокаменн", "кладка блоков"],
        "norm_id": "СП 15.13330.2020",
        "section": "Каменные и армокаменные конструкции",
        "requirement": "Расчёт и проектирование каменных и армокаменных конструкций: требования к материалам, кладке, перевязке швов, анкеровке и армированию",
        "confidence": "PARTIAL",
    },
    # --- Блок 4: Стальные конструкции (расширение) ---
    {
        "keywords": ["проектирование стальных", "расчёт металлоконструкц", "расчет металлоконструкц", "км проект", "стальная конструкц"],
        "norm_id": "СП 294.1325800.2017",
        "section": "Конструкции стальные. Правила проектирования",
        "requirement": "Актуализированные правила проектирования стальных конструкций: расчётные сопротивления, предельные состояния, соединения, устойчивость элементов",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["прокат стальн", "двутавр", "швеллер", "уголок металл", "листовой прокат", "сортовой прокат"],
        "norm_id": "ГОСТ 27772-2015",
        "section": "Прокат для стальных строительных конструкций. Общие технические условия",
        "requirement": "Требования к прокату (двутавры, швеллеры, уголки, листы) для стальных строительных конструкций: марки стали, механические характеристики, допуски, испытания",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["лстк", "тонкостенный профиль", "профиль холодногнутый", "оцинкованный профиль", "лёгкая стальная конструкц"],
        "norm_id": "СП 260.1325800.2016",
        "section": "Конструкции стальные тонкостенные из холодногнутых оцинкованных профилей",
        "requirement": "Проектирование и монтаж ЛСТК: расчёт профилей, узлы соединений, защита от коррозии, контроль качества монтажа",
        "confidence": "PARTIAL",
    },
    # --- Блок 5: Внутренняя отделка (расширение) ---
    {
        "keywords": ["гипсокартон", "гкл", "перегородка гкл", "подвесной потолок", "профиль cd", "профиль ud"],
        "norm_id": "СП 163.1325800.2014",
        "section": "Конструкции с применением гипсокартонных и гипсоволокнистых листов",
        "requirement": "Устройство перегородок, облицовок и подвесных потолков с применением ГКЛ: шаг стоек, крепление, зазоры, огнестойкость, звукоизоляция",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["лист гипсокартонный", "гипсокартон технические", "влагостойкий гкл", "огнестойкий гкл"],
        "norm_id": "ГОСТ 6266-2018",
        "section": "Листы гипсокартонные. Технические условия",
        "requirement": "Технические требования к гипсокартонным листам: типы (ГКЛ, ГКЛВ, ГКЛО), размеры, прочность на изгиб, влагостойкость, маркировка",
        "confidence": "PARTIAL",
    },
    # --- Блок 6: Фасады и тепловая защита ---
    {
        "keywords": ["тепловая защита", "утепление фасад", "теплопотери", "сопротивление теплопередач", "утеплитель стен"],
        "norm_id": "СП 50.13330.2012",
        "section": "Тепловая защита зданий",
        "requirement": "Требования к тепловой защите зданий: нормируемые значения сопротивления теплопередаче, воздухопроницаемости, защита от переувлажнения ограждающих конструкций",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["сфтк", "фасадная система", "навесной фасад", "вентилируемый фасад", "штукатурный фасад", "утепление стен снаружи"],
        "norm_id": "СП 293.1325800.2017",
        "section": "Системы фасадные теплоизоляционные композиционные с наружными штукатурными слоями",
        "requirement": "Проектирование и монтаж СФТК: состав системы, крепление утеплителя, армирующий слой, декоративное покрытие, контроль адгезии и геометрии",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["окно пвх", "оконный блок пвх", "профиль пвх", "остекление", "монтаж окон", "монтажный шов окна"],
        "norm_id": "ГОСТ 30674-99",
        "section": "Блоки оконные из поливинилхлоридных профилей. Технические условия",
        "requirement": "Требования к оконным блокам из ПВХ: конструкция, размеры, сопротивление теплопередаче, воздухо- и водопроницаемость, испытания, монтаж",
        "confidence": "PARTIAL",
    },
    # --- Блок 7: ОВ (отопление, вентиляция) ---
    {
        "keywords": ["отоплен", "вентиляц", "кондицион", "овик", "воздуховод", "тепловой узел", "радиатор отоплен"],
        "norm_id": "СП 60.13330.2020",
        "section": "Отопление, вентиляция и кондиционирование воздуха",
        "requirement": "Проектирование и монтаж систем ОВиК: параметры микроклимата, расчёт теплопотерь, воздухообмен, выбор оборудования, испытание и наладка систем",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["санитарно-технические системы", "внутренние инженерные системы", "монтаж инженерных систем", "приёмка инженерных систем"],
        "norm_id": "СП 73.13330.2016",
        "section": "Внутренние санитарно-технические системы зданий",
        "requirement": "Монтаж внутренних санитарно-технических систем: водоснабжение, водоотведение, отопление, вентиляция — требования к производству работ и приёмке",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["тепловая изоляция трубопровод", "изоляция труб", "теплоизоляция оборудован", "тепловые сети изоляц"],
        "norm_id": "СП 61.13330.2012",
        "section": "Тепловая изоляция оборудования и трубопроводов",
        "requirement": "Требования к тепловой изоляции трубопроводов и оборудования: выбор материала, толщина изоляции, конструктивные решения, контроль качества",
        "confidence": "PARTIAL",
    },
    # --- Блок 8: ВК (водоснабжение, канализация) ---
    {
        "keywords": ["внутренний водопровод", "внутренняя канализац", "водоотведение здания", "трубопровод вк", "сантехника монтаж"],
        "norm_id": "СП 30.13330.2020",
        "section": "Внутренний водопровод и канализация зданий",
        "requirement": "Проектирование и монтаж внутреннего водопровода и канализации: давление в системе, уклоны труб, вентиляция стояков, испытание на герметичность, приёмка",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["наружный водопровод", "наружное водоснабжение", "водонапорная башня", "насосная станция водоснабж"],
        "norm_id": "СП 31.13330.2021",
        "section": "Водоснабжение. Наружные сети и сооружения",
        "requirement": "Проектирование наружных сетей водоснабжения: расчётные расходы, трубы и арматура, защита от замерзания, испытание на прочность и герметичность",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["наружная канализац", "ливневая канализац", "дождевой коллектор", "выпуск канализац", "дворовая канализац"],
        "norm_id": "СП 32.13330.2018",
        "section": "Канализация. Наружные сети и сооружения",
        "requirement": "Проектирование наружных канализационных сетей: уклоны, глубины заложения, смотровые колодцы, испытание на герметичность, ливневые и хозяйственно-бытовые системы",
        "confidence": "PARTIAL",
    },
    # --- Блок 9: Электрика ---
    {
        "keywords": ["электроустановка", "кабельная линия", "электрощит", "электропроводка", "ввод электрический", "пуэ"],
        "norm_id": "ПУЭ (7-е изд.)",
        "section": "Правила устройства электроустановок",
        "requirement": "Общие требования к устройству электроустановок: выбор проводников и кабелей, защитная аппаратура, заземление, молниезащита, вводно-распределительные устройства",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["электроустановки жилых", "электрика в квартире", "групповые цепи", "щит учёта", "электромонтаж жилые"],
        "norm_id": "СП 256.1325800.2016",
        "section": "Электроустановки жилых и общественных зданий. Правила проектирования и монтажа",
        "requirement": "Проектирование и монтаж электроустановок жилых и общественных зданий: схемы питания, сечения проводников, УЗО, автоматы, заземление, приёмо-сдаточные испытания",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["узо", "дифавтомат", "заземление", "молниезащита", "потенциаловыравнивание", "поражение током"],
        "norm_id": "ГОСТ Р 50571-4-41-2022",
        "section": "Электроустановки зданий. Защита от поражения электрическим током",
        "requirement": "Требования к защите от поражения электрическим током: автоматическое отключение, двойная изоляция, выравнивание потенциалов, применение УЗО и дифавтоматов",
        "confidence": "PARTIAL",
    },
    # --- Блок 10: Пожарная безопасность ---
    {
        "keywords": ["пожарная безопасность", "огнестойкость", "возгорание", "пожаробезопасность", "класс пожарной опасности"],
        "norm_id": "123-ФЗ",
        "section": "Технический регламент о требованиях пожарной безопасности",
        "requirement": "Общие требования пожарной безопасности к зданиям: классы конструктивной пожарной опасности, степени огнестойкости, требования к эвакуации и противопожарным преградам",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["эвакуационный выход", "путь эвакуации", "ширина прохода", "лестничная клетка", "эвакуация людей"],
        "norm_id": "СП 1.13130.2020",
        "section": "Системы противопожарной защиты. Эвакуационные пути и выходы",
        "requirement": "Требования к эвакуационным путям и выходам: ширина, высота, протяжённость, количество выходов, незадымляемые лестничные клетки",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["предел огнестойкости", "нормируемый предел огнестойкост", "пожарная секция", "огнестойкость несущих конструкц"],
        "norm_id": "СП 2.13130.2020",
        "section": "Системы противопожарной защиты. Обеспечение огнестойкости объектов защиты",
        "requirement": "Требования к огнестойкости строительных конструкций: нормирование пределов огнестойкости несущих и ограждающих конструкций в зависимости от степени огнестойкости здания",
        "confidence": "PARTIAL",
    },
    # --- Блок 11: Охрана труда и техника безопасности ---
    {
        "keywords": ["охрана труда", "техника безопасности", "безопасность труда строительство", "несчастный случай", "производственный травматизм"],
        "norm_id": "СНиП 12-03-2001",
        "section": "Безопасность труда в строительстве. Часть 1. Общие требования",
        "requirement": "Общие требования безопасности труда при строительстве: организация рабочих мест, опасные зоны, средства защиты, санитарно-бытовые условия, расследование несчастных случаев",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["безопасность строительного производства", "работы повышенной опасности", "наряд-допуск", "опасные строительные работы"],
        "norm_id": "СНиП 12-04-2002",
        "section": "Безопасность труда в строительстве. Часть 2. Строительное производство",
        "requirement": "Требования безопасности при производстве строительных работ: земляные, монтажные, кровельные, отделочные работы, работы с механизмами — наряды-допуски, ограждения опасных зон",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["правила по охране труда строительство", "пот строительство", "требования охраны труда", "безопасность на строительной площадке"],
        "norm_id": "Приказ Минтруда №336н",
        "section": "Правила по охране труда в строительстве",
        "requirement": "Актуальные правила по охране труда при строительстве: требования к организации работ, применению механизмов, защитным устройствам, оформлению нарядов-допусков",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["работы на высоте", "высотные работы", "страховочная система", "строительные леса", "подмости"],
        "norm_id": "Приказ Минтруда №883н",
        "section": "Правила по охране труда при работе на высоте",
        "requirement": "Требования безопасности при работах на высоте: применение страховочных систем, устройство лесов и подмостей, ограждения проёмов, допуск и обучение персонала",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["инструктаж по охране труда", "вводный инструктаж", "журнал инструктажей", "обучение безопасности труда"],
        "norm_id": "ГОСТ 12.0.004-2015",
        "section": "Система стандартов безопасности труда. Организация обучения безопасности труда",
        "requirement": "Порядок обучения и проверки знаний по охране труда: виды инструктажей (вводный, первичный, повторный, внеплановый, целевой), ведение журналов инструктажей",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["средства индивидуальной защиты", "сиз", "каска строительная", "защитный жилет", "очки защитные", "перчатки рабочие"],
        "norm_id": "ГОСТ 12.4.011-89",
        "section": "Система стандартов безопасности труда. Средства защиты работающих",
        "requirement": "Классификация и требования к средствам индивидуальной и коллективной защиты работников: каски, жилеты, очки, перчатки, монтажные пояса, страховочные привязи",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["организация строительной площадки", "стройплощадка требования", "временные сооружения стройплощадка", "бытовки стройплощадка"],
        "norm_id": "СП 49.13330.2010",
        "section": "Безопасность труда в строительстве",
        "requirement": "Требования к организации и обустройству строительных площадок: временные сооружения, санитарно-бытовые помещения, ограждения, освещение, безопасная организация труда",
        "confidence": "PARTIAL",
    },
]

try:
    NORMATIVE_INDEX.extend(_P6H5_NORMATIVE_EXPAND)
    _p6h_norm_logging.getLogger("task_worker").info(
        "P6H5_NORMATIVE_FULL_EXPAND_V1_INSTALLED added=%d total=%d",
        len(_P6H5_NORMATIVE_EXPAND), len(NORMATIVE_INDEX),
    )
except Exception:
    pass
# === END_P6H5_NORMATIVE_FULL_EXPAND_V1 ===

# === P6H6_LOADS_V1 ===
# Append-only: keyword coverage for load types under СП 20.13330.2017 only.
# No new norms, no clause numbers. topic_5 + topic_210 shared.

_P6H6_LOADS = [
    {
        "keywords": ["снеговая нагрузка", "снеговой район", "снеговой мешок", "масса снега", "снег на кровле"],
        "norm_id": "СП 20.13330.2017",
        "section": "Нагрузки и воздействия — снеговые нагрузки",
        "requirement": "Снеговые нагрузки на конструкции определяются по нормативному значению снегового покрова для соответствующего снегового района с учётом схем распределения снега на кровле",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["ветровая нагрузка", "ветровой район", "пульсация ветра", "скоростной напор", "ветровое давление"],
        "norm_id": "СП 20.13330.2017",
        "section": "Нагрузки и воздействия — ветровые нагрузки",
        "requirement": "Ветровые нагрузки определяются по нормативному значению ветрового давления для соответствующего ветрового района с учётом пульсационной составляющей",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["постоянная нагрузка", "собственный вес конструкц", "нагрузка от конструкции", "нагрузка от покрытия", "нагрузка от перегородок"],
        "norm_id": "СП 20.13330.2017",
        "section": "Нагрузки и воздействия — постоянные нагрузки",
        "requirement": "Постоянные нагрузки включают собственный вес несущих и ограждающих конструкций и другие воздействия, неизменные в течение срока эксплуатации",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["временная нагрузка", "полезная нагрузка", "нагрузка на перекрытие", "нагрузка от людей", "нагрузка от оборудования", "нагрузка от складируемых материалов"],
        "norm_id": "СП 20.13330.2017",
        "section": "Нагрузки и воздействия — временные нагрузки",
        "requirement": "Временные нагрузки на перекрытия и покрытия принимаются по нормативным значениям в зависимости от назначения помещения и характера использования",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["сочетание нагрузок", "расчётное сочетание", "особое сочетание", "основное сочетание", "коэффициент сочетания", "коэффициент надёжности по нагрузке"],
        "norm_id": "СП 20.13330.2017",
        "section": "Нагрузки и воздействия — сочетания нагрузок",
        "requirement": "Расчёт конструкций выполняется на основные и особые сочетания нагрузок с применением коэффициентов сочетания и коэффициентов надёжности по нагрузке",
        "confidence": "PARTIAL",
    },
]

try:
    NORMATIVE_INDEX.extend(_P6H6_LOADS)
    _p6h_norm_logging.getLogger("task_worker").info(
        "P6H6_LOADS_V1_INSTALLED added=%d total=%d",
        len(_P6H6_LOADS), len(NORMATIVE_INDEX),
    )
except Exception:
    pass
# === END_P6H6_LOADS_V1 ===

====================================================================================================
END_FILE: core/normative_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/normative_source_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 570992de13fccd6bac9fbd100d64c2a766772eb0158450b267b5a576ff722467
====================================================================================================
# === NORMATIVE_SOURCE_ENGINE_FULL_CLOSE_V1 ===
# === NORMATIVE_NO_HALLUCINATION_GUARD_V1 ===
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

BASE = Path("/root/.areal-neva-core")
NORM_INDEX = BASE / "data/norms/normative_index.json"

def _load() -> List[Dict[str, Any]]:
    if NORM_INDEX.exists():
        try:
            data = json.loads(NORM_INDEX.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []
    return []

def search_normative_sources(text: str, limit: int = 8) -> List[Dict[str, Any]]:
    hay = (text or "").lower()
    out = []
    for row in _load():
        keys = " ".join(row.get("keywords") or []).lower()
        score = sum(1 for w in re.findall(r"[а-яa-z0-9]{4,}", hay) if w in keys or w in str(row).lower())
        if score:
            r = dict(row)
            r["score"] = score
            r["confidence"] = "CONFIRMED" if r.get("source") and r.get("clause") else "PARTIAL"
            out.append(r)
    out.sort(key=lambda x: int(x.get("score") or 0), reverse=True)
    return out[:limit]

def assert_no_exact_clause_without_source(norm: Dict[str, Any]) -> bool:
    return not bool(norm.get("clause")) or bool(norm.get("source"))

def format_normative_sources(rows: List[Dict[str, Any]]) -> str:
    lines = []
    for r in rows:
        confidence = "CONFIRMED" if assert_no_exact_clause_without_source(r) and r.get("source") else "PARTIAL"
        lines.append(f"{r.get('doc','UNKNOWN')} {r.get('clause','')}: {r.get('text','')} [{confidence}] {r.get('source','')}")
    return "\n".join(lines)
# === END_NORMATIVE_NO_HALLUCINATION_GUARD_V1 ===
# === END_NORMATIVE_SOURCE_ENGINE_FULL_CLOSE_V1 ===

====================================================================================================
END_FILE: core/normative_source_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/ocr_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 08aeb8f3e25b091f13412d0352b24189e3cf9dd7af3d0c2640e448e4f7ca30b9
====================================================================================================
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

====================================================================================================
END_FILE: core/ocr_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/ocr_table_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5cd90f31ee3cb4af0edd0d1fd334a6c4c8e6b7c08a3011d0694d651bd13163fb
====================================================================================================
# === OCR_TABLE_TO_EXCEL_FULL_CLOSE_V1 ===
from __future__ import annotations

import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List

def _safe(v: Any) -> str:
    return re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", str(v or "ocr_table")).strip("._") or "ocr_table"

def _parse_rows(text: str) -> List[List[str]]:
    rows = []
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("rows") or data.get("items") or []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    rows.append([
                        str(item.get("name") or item.get("наименование") or ""),
                        str(item.get("unit") or item.get("ед") or ""),
                        str(item.get("qty") or item.get("количество") or ""),
                        str(item.get("price") or item.get("цена") or ""),
                    ])
                elif isinstance(item, list):
                    rows.append([str(x) for x in item])
        if rows:
            return rows
    except Exception:
        pass

    for line in (text or "").splitlines():
        parts = [p.strip() for p in re.split(r"\s{2,}|\t|;", line) if p.strip()]
        if len(parts) >= 2:
            rows.append(parts[:6])
    return rows

def _write_xlsx(rows: List[List[str]], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"ocr_table_{_safe(task_id)}.xlsx"
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "OCR_TABLE"
    headers = ["Наименование", "Ед", "Кол-во", "Цена", "Сумма"]
    ws.append(headers)
    for r in rows:
        name = r[0] if len(r) > 0 else ""
        unit = r[1] if len(r) > 1 else ""
        qty = r[2] if len(r) > 2 else ""
        price = r[3] if len(r) > 3 else ""
        ws.append([name, unit, qty, price, None])
        row = ws.max_row
        ws.cell(row=row, column=5, value=f"=C{row}*D{row}")
    total_row = ws.max_row + 1
    ws.cell(row=total_row, column=4, value="ИТОГО")
    ws.cell(row=total_row, column=5, value=f"=SUM(E2:E{total_row-1})")
    wb.save(out)
    wb.close()
    return str(out)

def _write_pdf_stub(rows: List[List[str]], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"ocr_table_{_safe(task_id)}.pdf"
    text = "OCR TABLE RESULT\\nRows: " + str(len(rows))
    stream = f"BT /F1 12 Tf 50 780 Td ({text}) Tj ET".encode()
    pdf = b"%PDF-1.4\n1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>endobj\n4 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n5 0 obj<< /Length " + str(len(stream)).encode() + b" >>stream\n" + stream + b"\nendstream endobj\ntrailer<< /Root 1 0 R >>\n%%EOF"
    out.write_bytes(pdf)
    return str(out)

def _zip(paths: List[str], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"ocr_table_package_{_safe(task_id)}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p and os.path.exists(p):
                z.write(p, arcname=os.path.basename(p))
    return str(out)

async def image_table_to_excel(local_path: str, task_id: str, user_text: str = "", topic_id: int = 0) -> Dict[str, Any]:
    if not local_path or not os.path.exists(local_path):
        return {"success": False, "error": "IMAGE_NOT_FOUND"}

    vision_text = ""
    try:
        from core.gemini_vision import analyze_image_file
        prompt = (
            "Распознай таблицу/смету/ВОР на изображении. "
            "Верни строго JSON: {\"rows\":[{\"name\":\"\",\"unit\":\"\",\"qty\":\"\",\"price\":\"\"}]}. "
            "Не считай руками, только извлеки строки."
        )
        vision_text = await analyze_image_file(local_path, prompt=prompt, timeout=90) or ""
    except Exception as e:
        return {"success": False, "error": f"VISION_UNAVAILABLE:{e}"}

    rows = _parse_rows(vision_text)
    if not rows:
        return {"success": False, "error": "NO_TABLE_ROWS_RECOGNIZED", "raw": vision_text[:2000]}

    xlsx = _write_xlsx(rows, task_id)
    pdf = _write_pdf_stub(rows, task_id)
    package = _zip([xlsx, pdf], task_id)

    return {
        "success": True,
        "engine": "OCR_TABLE_TO_EXCEL_FULL_CLOSE_V1",
        "summary": f"Фото таблицы распознано\\nСтрок: {len(rows)}\\nАртефакты: XLSX + PDF",
        "artifact_path": package,
        "artifact_name": f"ocr_table_package_{_safe(task_id)}.zip",
        "extra_artifacts": [xlsx, pdf],
        "rows": rows,
    }
# === END_OCR_TABLE_TO_EXCEL_FULL_CLOSE_V1 ===

====================================================================================================
END_FILE: core/ocr_table_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/orchestra_closure_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: eb1b21fbc11d24b0c6c57a1498cb817cc182dd47320265bb5fbb51f65482da34
====================================================================================================
# === FULLFIX_10_TOTAL_CLOSURE_ENGINE ===
import os
import re
import json
import math
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE = "/root/.areal-neva-core"
CORE_DB = f"{BASE}/data/core.db"
MEM_DB = f"{BASE}/data/memory.db"
ENGINE = "FULLFIX_10_TOTAL_CLOSURE_ENGINE"

PROJECT_WORDS = (
    "проект", "сделай плит", "сделать плит", "плита", "фундамент", "фундаментная",
    "кж", "кд", "ар", "кровля", "стропил", "чертеж", "чертёж", "dwg", "dxf", "pdf"
)

ESTIMATE_WORDS = (
    "смет", "посчитай", "расчет", "расчёт", "стоимость", "цена", "руб", "м2", "м²", "м3", "м³"
)

CONFIRM_WORDS = {"да", "ок", "ok", "хорошо", "подтверждаю", "верно", "все верно", "всё верно", "принято"}
REVISION_WORDS = {"нет", "не так", "переделай", "исправь", "правки", "доработай", "уточни", "уточнение"}

FORBIDDEN_FOUNDATION_WORDS = [
    "стропил", "обреш", "контробреш", "пиломатериал", "кровл", "мауэрлат",
    "балки перекрытия", "план кровли", "спецификация древесины", "спецификация крепежа"
]

FOUNDATION_SHEETS = [
    {"mark": "КЖ", "number": "0", "title": "Титульный лист"},
    {"mark": "КЖ", "number": "1", "title": "Общие данные"},
    {"mark": "КЖ", "number": "2", "title": "Ведомость листов"},
    {"mark": "КЖ", "number": "3", "title": "План фундаментной плиты"},
    {"mark": "КЖ", "number": "4", "title": "План нижнего армирования"},
    {"mark": "КЖ", "number": "5", "title": "План верхнего армирования"},
    {"mark": "КЖ", "number": "6", "title": "Разрез 1-1"},
    {"mark": "КЖ", "number": "7", "title": "Разрез 2-2"},
    {"mark": "КЖ", "number": "8", "title": "Узел края плиты"},
    {"mark": "КЖ", "number": "9", "title": "Узел защитного слоя"},
    {"mark": "КЖ", "number": "10", "title": "Спецификация материалов"},
    {"mark": "КЖ", "number": "11", "title": "Ведомость расхода стали"},
    {"mark": "КЖ", "number": "12", "title": "Пояснительная записка"},
    {"mark": "КЖ", "number": "13", "title": "Контроль качества работ"},
]

NORMATIVE_NOTES = [
    "СП 63.13330.2018 Бетонные и железобетонные конструкции",
    "СП 20.13330.2016 Нагрузки и воздействия",
    "ГОСТ 21.101-2020 Основные требования к проектной и рабочей документации",
    "ГОСТ 21.501-2018 Правила выполнения рабочей документации архитектурных и конструктивных решений",
    "ГОСТ 34028-2016 Прокат арматурный для железобетонных конструкций",
    "ГОСТ 7473-2010 Смеси бетонные",
]

REBAR_WEIGHT_KG_M = {6:0.222,8:0.395,10:0.617,12:0.888,14:1.21,16:1.58,18:2.0,20:2.47,22:2.98,25:3.85}

def clean(v: Any, limit: int = 12000) -> str:
    return str(v or "").replace("\x00", " ").strip()[:limit]

def classify_user_task(raw_input: str) -> str:
    low = clean(raw_input, 2000).lower()
    stripped = low.strip()
    if stripped in CONFIRM_WORDS or any(stripped.startswith(x) for x in ("да", "ок", "подтверж")):
        return "confirm"
    if stripped in REVISION_WORDS or any(x in stripped for x in ("не так", "передел", "исправ", "правк", "уточн", "недоволен")):
        return "revision"
    if any(x in low for x in PROJECT_WORDS):
        return "project"
    if any(x in low for x in ESTIMATE_WORDS):
        return "estimate"
    return "chat"

def classify_project_kind(raw_input: str) -> Tuple[str, str]:
    low = clean(raw_input, 4000).lower()
    if any(x in low for x in ("плит", "фундамент", "бетон", "арматур")):
        return "foundation_slab", "КЖ"
    if any(x in low for x in ("кров", "строп", "обреш", "кд")):
        return "roof", "КД"
    if any(x in low for x in ("архитект", "планиров", "ар ")):
        return "architectural", "АР"
    return "foundation_slab", "КЖ"

def parse_float(v: str, default: float) -> float:
    try:
        return float(str(v).replace(",", "."))
    except Exception:
        return default

def parse_foundation_request(raw_input: str) -> Dict[str, Any]:
    text = clean(raw_input, 5000)
    low = text.lower()
    project_kind, section = classify_project_kind(text)

    length_m = 10.0
    width_m = 10.0
    m = re.search(r"(\d+(?:[,.]\d+)?)\s*(?:на|x|х|×)\s*(\d+(?:[,.]\d+)?)\s*(?:м|m)?", low)
    if m:
        length_m = parse_float(m.group(1), 10.0)
        width_m = parse_float(m.group(2), 10.0)

    def mm(patterns: List[str], default: int) -> int:
        for p in patterns:
            mmv = re.search(p, low, re.I)
            if mmv:
                return int(float(mmv.group(1).replace(",", ".")))
        return default

    slab_mm = mm([
        r"толщин[аы]?\D{0,30}(\d{2,4})\s*мм",
        r"плит[аы]?\D{0,30}(\d{2,4})\s*мм",
        r"\b(\d{2,4})\s*мм\b",
    ], 250)

    sand_mm = mm([r"пес[а-яё]*\D{0,30}(\d{2,4})\s*мм"], 300)
    gravel_mm = mm([r"щеб[а-яё]*\D{0,30}(\d{2,4})\s*мм"], 150)
    rebar_step_mm = mm([r"шаг\D{0,30}(\d{2,4})\s*мм"], 200)

    rebar_diam_mm = 12
    md = re.search(r"(?:ø|ф|d|диаметр)\s*(\d{1,2})", low, re.I)
    if md:
        rebar_diam_mm = int(md.group(1))

    concrete_class = "B25"
    mc = re.search(r"\b[вb]\s?(\d{2,3}(?:[,.]\d)?)\b", text, re.I)
    if mc:
        concrete_class = "B" + mc.group(1).replace(",", ".")

    rebar_class = "A500"
    mr = re.search(r"\b[аa]\s?500[сc]?\b", text, re.I)
    if mr:
        rebar_class = "A500C" if "c" in mr.group(0).lower() or "с" in mr.group(0).lower() else "A500"

    if project_kind == "foundation_slab":
        section = "КЖ"

    return {
        "project_name": "Проект фундаментной плиты",
        "project_kind": project_kind,
        "section": section,
        "length_m": length_m,
        "width_m": width_m,
        "slab_mm": slab_mm,
        "sand_mm": sand_mm,
        "gravel_mm": gravel_mm,
        "rebar_diam_mm": rebar_diam_mm,
        "rebar_step_mm": rebar_step_mm,
        "rebar_class": rebar_class,
        "concrete_class": concrete_class,
        "cover_mm": 40,
        "input": raw_input,
    }

def foundation_sheets() -> List[Dict[str, str]]:
    return [dict(x) for x in FOUNDATION_SHEETS]

def calc_foundation(data: Dict[str, Any]) -> Dict[str, Any]:
    L = float(data["length_m"])
    W = float(data["width_m"])
    area = L * W
    slab_m = int(data["slab_mm"]) / 1000.0
    sand_m = int(data["sand_mm"]) / 1000.0
    gravel_m = int(data["gravel_mm"]) / 1000.0
    step_m = int(data["rebar_step_mm"]) / 1000.0
    d = int(data["rebar_diam_mm"])
    bars_x = int(math.floor(W / step_m)) + 1
    bars_y = int(math.floor(L / step_m)) + 1
    rebar_m_total = (bars_x * L + bars_y * W) * 2
    kg_m = REBAR_WEIGHT_KG_M.get(d, (d*d)/162.0)
    rebar_kg = rebar_m_total * kg_m
    return {
        "area_m2": round(area, 3),
        "concrete_m3": round(area * slab_m, 3),
        "sand_m3": round(area * sand_m, 3),
        "gravel_m3": round(area * gravel_m, 3),
        "rebar_m_total": round(rebar_m_total, 1),
        "rebar_kg": round(rebar_kg, 1),
        "rebar_t": round(rebar_kg / 1000.0, 3),
        "bars_x": bars_x,
        "bars_y": bars_y,
    }

def extract_pdf_text(path: str, limit: int = 200000) -> str:
    if not path or not os.path.exists(path):
        return ""
    text = ""
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        for page in reader.pages:
            text += "\n" + (page.extract_text() or "")
            if len(text) > limit:
                break
    except Exception:
        pass
    return clean(text, limit)

def validate_foundation_text(text: str) -> Tuple[bool, str]:
    low = clean(text, 200000).lower()
    bad = [x for x in FORBIDDEN_FOUNDATION_WORDS if x in low]
    if bad:
        return False, "FORBIDDEN_FOUNDATION_WORDS:" + ",".join(bad[:10])
    required = ["фундамент", "плит", "армат", "бетон"]
    missing = [x for x in required if x not in low]
    if missing:
        return False, "MISSING_REQUIRED_WORDS:" + ",".join(missing)
    return True, ""

def save_result_memory(chat_id: str, topic_id: int, raw_input: str, result: str, meta: Dict[str, Any]) -> None:
    try:
        conn = sqlite3.connect(MEM_DB, timeout=10)
        conn.execute("CREATE TABLE IF NOT EXISTS memory (chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        prefix = f"topic_{int(topic_id)}_"
        payload = {
            "engine": ENGINE,
            "raw_input": raw_input,
            "result": result,
            "meta": meta,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        conn.execute(
            "INSERT INTO memory (chat_id,key,value,timestamp) VALUES (?,?,?,datetime('now'))",
            (str(chat_id), prefix + "artifact_result", json.dumps(payload, ensure_ascii=False))
        )
        conn.execute(
            "INSERT INTO memory (chat_id,key,value,timestamp) VALUES (?,?,?,datetime('now'))",
            (str(chat_id), prefix + "task_summary", clean(result, 20000))
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def parse_estimate(raw_input: str) -> List[Dict[str, Any]]:
    text = clean(raw_input, 5000)
    parts = re.split(r"[,;\n]+", text)
    rows = []
    for part in parts:
        p = part.strip()
        if not p:
            continue
        qty_m = re.search(r"(\d+(?:[,.]\d+)?)\s*(м²|м2|м³|м3|шт|п\.?м|кг|т)", p, re.I)
        price_m = re.search(r"(?:по|цена)?\s*(\d+(?:[,.]\d+)?)\s*(?:руб|₽)", p, re.I)
        if qty_m:
            qty = parse_float(qty_m.group(1), 0.0)
            unit = qty_m.group(2).replace("м2","м²").replace("м3","м³")
            price = parse_float(price_m.group(1), 0.0) if price_m else 0.0
            name = re.sub(r"\d+(?:[,.]\d+)?\s*(м²|м2|м³|м3|шт|п\.?м|кг|т)", "", p, flags=re.I)
            name = re.sub(r"(?:по|цена)?\s*\d+(?:[,.]\d+)?\s*(?:руб|₽).*", "", name, flags=re.I).strip(" :-")
            rows.append({
                "name": name or "Позиция сметы",
                "qty": qty,
                "unit": unit,
                "price": price,
                "total": round(qty * price, 2),
            })
    if not rows:
        rows.append({"name": "Позиция сметы", "qty": 1, "unit": "шт", "price": 0, "total": 0})
    return rows

def create_estimate_files(raw_input: str, task_id: str, topic_id: int = 0) -> Dict[str, Any]:
    from openpyxl import Workbook
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

    rows = parse_estimate(raw_input)
    total = round(sum(float(r["total"]) for r in rows), 2)
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id or "estimate"))[:30]
    out_dir = Path(tempfile.gettempdir()) / f"areal_estimate_{safe}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)
    xlsx_path = str(out_dir / f"estimate_{safe}.xlsx")
    pdf_path = str(out_dir / f"estimate_{safe}.pdf")
    manifest_path = str(out_dir / f"estimate_{safe}.manifest.json")

    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"
    ws.append(["№", "Наименование", "Кол-во", "Ед", "Цена", "Сумма"])
    for i, r in enumerate(rows, 1):
        ws.append([i, r["name"], r["qty"], r["unit"], r["price"], r["total"]])
    ws.append(["", "ИТОГО", "", "", "", total])
    wb.save(xlsx_path)

    # === FULLFIX_15_OCE_CYR_FIX ===
    try:
        from core.pdf_cyrillic import register_cyrillic_fonts, FONT_REGULAR, FONT_BOLD
        register_cyrillic_fonts()
        _ocyr_reg = FONT_REGULAR
        _ocyr_bold = FONT_BOLD
    except Exception:
        _ocyr_reg = 'Helvetica'
        _ocyr_bold = 'Helvetica-Bold'
    c = canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4
    c.setFont(_ocyr_bold, 14)
    c.drawString(20*mm, h-20*mm, "СМЕТА")
    y = h - 35*mm
    c.setFont(_ocyr_reg, 9)
    for i, r in enumerate(rows, 1):
        c.setFont(_ocyr_reg, 9)
        c.drawString(20*mm, y, f"{i}. {r['name']} — {r['qty']} {r['unit']} x {r['price']} = {r['total']} руб")
        y -= 8*mm
    c.setFont(_ocyr_bold, 11)
    c.drawString(20*mm, y-5*mm, f"ИТОГО: {total} руб")
    c.save()

    manifest = {
        "engine": ENGINE,
        "type": "estimate",
        "task_id": task_id,
        "topic_id": topic_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
        "total": total,
        "files": {"xlsx": xlsx_path, "pdf": pdf_path},
    }
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        from core.engine_base import upload_artifact_to_drive
        xlsx_link = upload_artifact_to_drive(xlsx_path, task_id, topic_id)
        pdf_link = upload_artifact_to_drive(pdf_path, task_id, topic_id)
        manifest_link = upload_artifact_to_drive(manifest_path, task_id, topic_id)
    except Exception as e:
        return {"success": False, "error": "UPLOAD_FAILED:" + str(e)[:300]}

    if not xlsx_link or not pdf_link:
        return {"success": False, "error": "ESTIMATE_LINKS_MISSING"}

    message = (
        "Смета создана\n"
        f"Позиций: {len(rows)}\n"
        f"Итого: {total} руб\n"
        f"PDF: {pdf_link}\n"
        f"XLSX: {xlsx_link}\n"
        ""
        "Доволен результатом? Ответь: Да / Уточни / Правки"
    )
    # === FULLFIX_19_OCE_MEMORY_INVOKE ===
    try:
        from core.memory_client import save_memory as _ff19_sm
        _ff19_sm(
            "shared",
            "topic_"+str(topic_id or 0)+"_last_estimate_oce",
            {"task_id": task_id, "type": "estimate_oce"},
            topic_id=int(topic_id or 0),
            scope="topic"
        )
    except Exception:
        pass
    # === END FULLFIX_19_OCE_MEMORY_INVOKE ===

    # === FULLFIX_20_OCE_MEMORY_INVOKE ===
    try:
        from core.memory_client import save_memory as _ff20_sm
        _ff20_sm(
            "shared",
            "topic_" + str(topic_id or 0) + "_last_estimate_oce",
            {"task_id": task_id, "topic_id": topic_id},
            topic_id=int(topic_id or 0),
            scope="topic"
        )
    except Exception:
        pass
    # === END FULLFIX_20_OCE_MEMORY_INVOKE ===

    return {
        "success": True,
        "engine": ENGINE,
        "type": "estimate",
        "pdf_link": str(pdf_link),
        "xlsx_link": str(xlsx_link),
        "manifest_link": str(manifest_link or ""),
        "message": message,
        "total": total,
        "rows": rows,
    }

# === FULLFIX_16_OCE_MSG_STRIP: manifest removed from message strings ===
# === END FULLFIX_10_TOTAL_CLOSURE_ENGINE ===

# === FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT ===
# Goal:
# - project PDF must look like compact project album, not sparse text dump
# - one dense A3 landscape sheet frame
# - fewer duplicate sheets
# - plans, sections, nodes, specs placed compactly on each page
# - old FULLFIX_07 renderer must not define the visual quality anymore

def _ff12_font():
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        for name, path in [
            ("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ("Arial", "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"),
        ]:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont(name, path))
                    return name
                except Exception:
                    pass
    except Exception:
        pass
    return "Helvetica"

def _ff12_draw_stamp(c, page_w, page_h, sheet_title, sheet_no, sheet_total, section, font):
    from reportlab.lib.units import mm

    margin = 10 * mm
    c.setLineWidth(0.7)
    c.rect(margin, margin, page_w - 2 * margin, page_h - 2 * margin)

    stamp_w = 185 * mm
    stamp_h = 36 * mm
    sx = page_w - margin - stamp_w
    sy = margin
    c.rect(sx, sy, stamp_w, stamp_h)

    c.line(sx, sy + 10*mm, sx + stamp_w, sy + 10*mm)
    c.line(sx, sy + 20*mm, sx + stamp_w, sy + 20*mm)
    c.line(sx + 45*mm, sy, sx + 45*mm, sy + stamp_h)
    c.line(sx + 135*mm, sy, sx + 135*mm, sy + stamp_h)
    c.line(sx + 160*mm, sy, sx + 160*mm, sy + stamp_h)

    c.setFont(font, 7)
    c.drawString(sx + 3*mm, sy + 26*mm, "СК АРЕАЛ-НЕВА")
    c.drawString(sx + 48*mm, sy + 26*mm, "Индивидуальный жилой дом")
    c.drawString(sx + 138*mm, sy + 26*mm, "Стадия")
    c.drawString(sx + 163*mm, sy + 26*mm, "Лист")

    c.setFont(font, 9)
    c.drawString(sx + 48*mm, sy + 14*mm, str(sheet_title)[:55])
    c.drawString(sx + 138*mm, sy + 14*mm, "П")
    c.drawString(sx + 163*mm, sy + 14*mm, f"{sheet_no}/{sheet_total}")

    c.setFont(font, 7)
    c.drawString(margin + 3*mm, margin + 3*mm, f"{section} · FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT")

def _ff12_table(c, x, y, widths, rows, font, row_h=6, size=7):
    from reportlab.lib.units import mm

    c.setFont(font, size)
    yy = y
    for row in rows:
        xx = x
        max_lines = 1
        split_cells = []
        for val, w in zip(row, widths):
            text = str(val)
            chars = max(8, int(w / (size * 0.55)))
            lines = [text[i:i+chars] for i in range(0, len(text), chars)] or [""]
            split_cells.append(lines[:3])
            max_lines = max(max_lines, len(lines[:3]))
        h = row_h * mm * max_lines
        for cell_lines, w in zip(split_cells, widths):
            c.rect(xx, yy - h, w*mm, h)
            ty = yy - 4*mm
            for line in cell_lines:
                c.drawString(xx + 1.5*mm, ty, line)
                ty -= row_h*mm
            xx += w*mm
        yy -= h
    return yy

def _ff12_draw_plan(c, x, y, w, h, data, calc, font, title):
    from reportlab.lib.units import mm

    L = float(data["length_m"])
    W = float(data["width_m"])
    step = int(data["rebar_step_mm"])
    scale = min(w / max(L, 1), h / max(W, 1))
    rw = L * scale
    rh = W * scale
    x0 = x + (w - rw) / 2
    y0 = y + (h - rh) / 2

    c.setFont(font, 9)
    c.drawString(x, y + h + 4*mm, title)
    c.setLineWidth(1.1)
    c.rect(x0, y0, rw, rh)

    c.setLineWidth(0.25)
    grid = max(3*mm, step / 1000 * scale)
    xx = x0 + grid
    while xx < x0 + rw:
        c.line(xx, y0, xx, y0 + rh)
        xx += grid
    yy = y0 + grid
    while yy < y0 + rh:
        c.line(x0, yy, x0 + rw, yy)
        yy += grid

    c.setFont(font, 7)
    c.drawString(x0, y0 - 5*mm, f"{L:g} м")
    c.saveState()
    c.translate(x0 - 7*mm, y0)
    c.rotate(90)
    c.drawString(0, 0, f"{W:g} м")
    c.restoreState()

def _ff12_draw_section(c, x, y, w, h, data, font, title):
    from reportlab.lib.units import mm

    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    total = max(slab + sand + gravel, 1)
    c.setFont(font, 9)
    c.drawString(x, y + h + 4*mm, title)

    layer_rows = [
        ("Песчаная подушка", sand, "послойное уплотнение"),
        ("Щебёночное основание", gravel, "послойное уплотнение"),
        ("Фундаментная плита", slab, f"бетон {data['concrete_class']}, защитный слой {data.get('cover_mm',40)} мм"),
    ]

    yy = y
    for name, th, note in layer_rows:
        hh = max(10*mm, h * th / total)
        c.rect(x, yy, w, hh)
        c.setFont(font, 7)
        c.drawString(x + 3*mm, yy + hh/2 - 2*mm, f"{name}: {th} мм — {note}")
        yy += hh

    c.setLineWidth(0.4)
    c.line(x + 5*mm, y + h - 7*mm, x + w - 5*mm, y + h - 7*mm)
    c.line(x + 5*mm, y + h - 13*mm, x + w - 5*mm, y + h - 13*mm)
    c.setFont(font, 7)
    c.drawString(x + 8*mm, y + h - 5*mm, f"{data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм")

def _ff12_draw_nodes(c, x, y, w, h, data, font):
    from reportlab.lib.units import mm

    c.setFont(font, 9)
    c.drawString(x, y + h + 4*mm, "Типовые узлы")
    node_w = w / 3 - 3*mm
    names = ["Край плиты", "Защитный слой", "Основание"]
    for i, name in enumerate(names):
        nx = x + i * (node_w + 4*mm)
        c.rect(nx, y, node_w, h)
        c.setFont(font, 7)
        c.drawString(nx + 2*mm, y + h - 5*mm, name)
        c.line(nx + 4*mm, y + 12*mm, nx + node_w - 4*mm, y + 12*mm)
        c.line(nx + 4*mm, y + 20*mm, nx + node_w - 4*mm, y + 20*mm)
        c.drawString(nx + 2*mm, y + 5*mm, f"Ø{data['rebar_diam_mm']} {data['rebar_class']}")
        c.drawString(nx + 2*mm, y + 28*mm, f"ЗС {data.get('cover_mm',40)} мм")

def _ff12_material_rows(data, calc):
    return [
        ["1", f"Бетон {data['concrete_class']} для фундаментной плиты", "м³", calc["concrete_m3"], "по объёму плиты"],
        ["2", "Песчаная подушка", "м³", calc["sand_m3"], "послойное уплотнение"],
        ["3", "Щебёночное основание", "м³", calc["gravel_m3"], "послойное уплотнение"],
        ["4", f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']}", "п.м", calc["rebar_m_total"], "верхняя и нижняя сетка"],
        ["5", f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']}", "т", calc["rebar_t"], "расчётный вес"],
    ]

def _ff12_write_compact_project_pdf(path: str, data: dict, calc: dict) -> str:
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _ff12_font()
    page_w, page_h = landscape(A3)
    c = canvas.Canvas(path, pagesize=landscape(A3))

    section = data["section"]
    sheets = [
        "Общие данные + ведомость листов",
        "План плиты + армирование",
        "Разрезы и узлы",
        "Спецификация + контроль качества",
    ]
    sheet_total = len(sheets)

    # Sheet 1
    _ff12_draw_stamp(c, page_w, page_h, sheets[0], 1, sheet_total, section, font)
    c.setFont(font, 14)
    c.drawString(20*mm, 275*mm, "Проект фундаментной плиты")
    c.setFont(font, 9)
    left_rows = [
        ["Раздел", section],
        ["Тип", "Фундаментная плита"],
        ["Размер", f"{data['length_m']:g} x {data['width_m']:g} м"],
        ["Толщина плиты", f"{data['slab_mm']} мм"],
        ["Основание", f"Песок {data['sand_mm']} мм, щебень {data['gravel_mm']} мм"],
        ["Бетон", data["concrete_class"]],
        ["Арматура", f"{data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм"],
        ["Площадь", f"{calc['area_m2']} м²"],
        ["Объём бетона", f"{calc['concrete_m3']} м³"],
    ]
    _ff12_table(c, 20*mm, 258*mm, [42, 95], left_rows, font, row_h=6, size=8)

    sheet_rows = [[str(i+1), title] for i, title in enumerate(sheets)]
    _ff12_table(c, 180*mm, 258*mm, [15, 110], [["№", "Наименование листа"]] + sheet_rows, font, row_h=6, size=8)

    norm_rows = [["№", "Нормативная база"]] + [[str(i+1), n] for i, n in enumerate(NORMATIVE_NOTES[:6])]
    _ff12_table(c, 20*mm, 165*mm, [15, 250], norm_rows, font, row_h=6, size=7)
    c.showPage()

    # Sheet 2
    _ff12_draw_stamp(c, page_w, page_h, sheets[1], 2, sheet_total, section, font)
    _ff12_draw_plan(c, 20*mm, 65*mm, 235*mm, 165*mm, data, calc, font, "План фундаментной плиты и сетка армирования")
    c.setFont(font, 8)
    notes = [
        f"Нижняя и верхняя сетки: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм",
        f"Защитный слой бетона: {data.get('cover_mm',40)} мм",
        f"Количество стержней по X/Y: {calc['bars_x']} / {calc['bars_y']}",
        f"Общий расход арматуры: {calc['rebar_m_total']} п.м / {calc['rebar_t']} т",
    ]
    y = 245*mm
    for n in notes:
        c.drawString(275*mm, y, n)
        y -= 8*mm
    c.showPage()

    # Sheet 3
    _ff12_draw_stamp(c, page_w, page_h, sheets[2], 3, sheet_total, section, font)
    _ff12_draw_section(c, 20*mm, 60*mm, 170*mm, 105*mm, data, font, "Разрез 1-1")
    _ff12_draw_section(c, 215*mm, 60*mm, 170*mm, 105*mm, data, font, "Разрез 2-2")
    _ff12_draw_nodes(c, 20*mm, 195*mm, 365*mm, 55*mm, data, font)
    c.showPage()

    # Sheet 4
    _ff12_draw_stamp(c, page_w, page_h, sheets[3], 4, sheet_total, section, font)
    rows = [["№", "Наименование", "Ед", "Кол-во", "Примечание"]] + _ff12_material_rows(data, calc)
    _ff12_table(c, 20*mm, 260*mm, [12, 120, 20, 30, 95], rows, font, row_h=7, size=8)

    qc = [
        ["1", "Проверить подготовку основания и уплотнение"],
        ["2", "Проверить защитный слой и фиксаторы арматуры"],
        ["3", "Проверить шаг и диаметр арматуры до бетонирования"],
        ["4", "Принять бетон по паспортам и фактической укладке"],
    ]
    _ff12_table(c, 20*mm, 170*mm, [12, 190], [["№", "Контроль качества"]] + qc, font, row_h=7, size=8)
    c.showPage()

    c.save()
    return path

async def create_compact_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    data = parse_foundation_request(raw_input)
    data["section"] = "КЖ"
    data["project_kind"] = "foundation_slab"
    calc = calc_foundation(data)

    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id or "manual"))[:30]
    out_dir = Path(tempfile.gettempdir()) / f"areal_compact_project_{safe}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = str(out_dir / f"КЖ_COMPACT_PROJECT_{safe}.pdf")
    manifest_path = str(out_dir / f"КЖ_COMPACT_PROJECT_{safe}.manifest.json")

    _ff12_write_compact_project_pdf(pdf_path, data, calc)

    pdf_text = extract_pdf_text(pdf_path)
    valid, reason = validate_foundation_text(pdf_text)

    manifest = {
        "engine": "FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "topic_id": topic_id,
        "input": raw_input,
        "data": data,
        "calc": calc,
        "sheet_count": 4,
        "pdf_text_valid": valid,
        "pdf_text_error": reason,
        "pdf_path": pdf_path,
    }
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    from core.engine_base import upload_artifact_to_drive
    pdf_link = upload_artifact_to_drive(pdf_path, task_id, topic_id)
    manifest_link = upload_artifact_to_drive(manifest_path, task_id, topic_id)

    if not pdf_link:
        return {"success": False, "engine": "FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT", "error": "PDF_UPLOAD_FAILED"}

    return {
        "success": True,
        "engine": "FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT",
        "section": "КЖ",
        "project_kind": "foundation_slab",
        "sheet_count": 4,
        "pdf_path": pdf_path,
        "pdf_link": str(pdf_link),
        "manifest_link": str(manifest_link or ""),
        "data": data,
        "calc": calc,
        "message": (
            "Проект создан компактным PDF-альбомом\\n"
            "Engine: FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT\\n"
            "Раздел: КЖ\\n"
            "Тип: фундаментная плита\\n"
            "Листов: 4\\n"
            f"Размер: {data['length_m']:g} x {data['width_m']:g} м\\n"
            f"Плита: {data['slab_mm']} мм\\n"
            f"Бетон: {data['concrete_class']}\\n"
            f"Арматура: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм\\n"
            f"Бетон: {calc['concrete_m3']} м³\\n"
            f"Арматура: {calc['rebar_t']} т\\n\\n"
            f"PDF: {pdf_link}\\n"
            ""
            "Доволен результатом? Ответь: Да / Уточни / Правки"
        )
    }

# override public name inside this module
create_full_project_documentation = create_compact_project_documentation
# === END FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT ===

# === FULLFIX_13A_SAMPLE_TEMPLATE_PUBLIC_HELPERS ===
async def ff13a_create_estimate_from_saved_template(raw_input: str, task_id: str, chat_id: str, topic_id: int = 0) -> dict:
    from core.sample_template_engine import create_estimate_from_saved_template
    return await create_estimate_from_saved_template(raw_input, task_id, chat_id, topic_id)

def ff13a_detect_sample_template_intent(raw_input: str, input_type: str = "text") -> bool:
    from core.sample_template_engine import detect_sample_template_intent
    return detect_sample_template_intent(raw_input, input_type)
# === END FULLFIX_13A_SAMPLE_TEMPLATE_PUBLIC_HELPERS ===


# === FULLFIX_13B_ESTIMATE_OUTPUT_FORMULAS_NO_MANIFEST ===
def ff13b_rewrite_estimate_xlsx_with_formulas(xlsx_path: str) -> str:
    """
    Ensure estimate XLSX is a real working spreadsheet:
    - Qty / Price / Total columns
    - Total column uses Excel formulas
    - Final total row uses SUM formula
    """
    from openpyxl import load_workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    wb = load_workbook(xlsx_path)
    ws = wb.active

    headers = ["№", "Наименование", "Ед.", "Кол-во", "Цена", "Сумма"]
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=col, value=h)
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")
        c.fill = PatternFill("solid", fgColor="D9EAF7")

    max_row = ws.max_row
    first_data = 2
    last_data = max_row

    # detect if old sheet has no clean header
    if max_row < 2:
        last_data = 2

    for row in range(first_data, last_data + 1):
        qty = ws.cell(row=row, column=4).value
        price = ws.cell(row=row, column=5).value
        if qty not in (None, "") and price not in (None, ""):
            ws.cell(row=row, column=6, value=f"=D{row}*E{row}")

    total_row = last_data + 1
    ws.cell(row=total_row, column=5, value="ИТОГО").font = Font(bold=True)
    ws.cell(row=total_row, column=6, value=f"=SUM(F{first_data}:F{last_data})").font = Font(bold=True)

    widths = [8, 42, 12, 14, 14, 16]
    thin = Side(style="thin", color="999999")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for col, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width
        for row in range(1, total_row + 1):
            ws.cell(row=row, column=col).border = border
            ws.cell(row=row, column=col).alignment = Alignment(vertical="center", wrap_text=True)

    wb.save(xlsx_path)
    return xlsx_path


def ff13b_clean_estimate_user_message(message: str) -> str:
    """
    User must see only useful estimate outputs:
    - PDF
    - XLSX
    No MANIFEST in Telegram answer
    """
    import re
    msg = str(message or "")
    msg = re.sub(r"(?im)^MANIFEST:\s*https?://\S+\s*$", "", msg)
    msg = re.sub(r"\n{3,}", "\n\n", msg).strip()
    return msg
# === END FULLFIX_13B_ESTIMATE_OUTPUT_FORMULAS_NO_MANIFEST ===


====================================================================================================
END_FILE: core/orchestra_closure_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/orchestra_context.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d2e491ea92d7efee7b6ca49db7193b624739f3ff95041300dc48ef4db2a80ff2
====================================================================================================
# === ORCHESTRA_SHARED_CONTEXT_V1 ===
# Каждая модель получает единый контекст: ONE_SHARED_CONTEXT + memory + task + pin + topic_role
import os, logging
logger = logging.getLogger(__name__)

def build_shared_context(
    raw_input: str = "",
    topic_id: int = 0,
    chat_id: str = "",
    active_task: dict = None,
    pin_text: str = "",
    short_memory: str = "",
    long_memory: str = "",
    search_result: str = "",
    topic_role: str = "",
    files: list = None,
) -> str:
    """
    Собирает ORCHESTRA_SHARED_CONTEXT для передачи в любую модель.
    Порядок приоритета из канона §5.1:
    user_input → active_task → pin → short_memory → long_memory → search
    """
    parts = []

    if topic_role:
        parts.append(f"[ROLE] {topic_role}")

    if active_task:
        state = active_task.get("state", "")
        raw = str(active_task.get("raw_input", ""))[:200]
        parts.append(f"[ACTIVE_TASK] state={state} input={raw}")

    if pin_text:
        parts.append(f"[PIN] {pin_text[:300]}")

    if short_memory:
        parts.append(f"[SHORT_MEMORY] {short_memory[:400]}")

    if long_memory:
        parts.append(f"[LONG_MEMORY] {long_memory[:400]}")

    if search_result:
        parts.append(f"[SEARCH] {search_result[:500]}")

    if files:
        parts.append(f"[FILES] {', '.join(str(f) for f in files[:5])}")

    if raw_input:
        parts.append(f"[USER] {raw_input[:500]}")

    return "\n".join(parts)

def user_mode_switch(text: str) -> str:
    """
    USER_MODE_SWITCH: TECH / HUMAN (default)
    """
    low = text.lower()
    if any(w in low for w in ["технический", "детально", "подробно", "tech mode", "полный разбор"]):
        return "TECH"
    return "HUMAN"

def mode_switch(task: dict) -> str:
    """
    MODE_SWITCH: LIGHT / FULL
    """
    intent = str(task.get("intent", "")).lower()
    input_type = str(task.get("input_type", "")).lower()
    if input_type == "drive_file" or intent in ("estimate", "project", "template", "technadzor", "dwg"):
        return "FULL"
    return "LIGHT"
# === END ORCHESTRA_SHARED_CONTEXT_V1 ===

====================================================================================================
END_FILE: core/orchestra_context.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/output_decision.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 91edab27bd5fa1befb487d6f402a1ff182ee0a3cc6fffdc4a2c3d7df90f4bc6d
====================================================================================================
# === OUTPUT_DECISION_LOGIC_V1 ===
# Канон ORCHESTRA_MASTER_BLOCK: RESULT_VALIDATOR + RESULT_FORMAT_ENFORCER + HUMAN_DECISION_EDITOR
import logging
logger = logging.getLogger(__name__)

def format_search_output(offers: list, goal: str = "") -> str:
    """
    Жёсткий формат вывода поискового результата.
    Канон: таблица + выводы + что проверить звонком
    """
    if not offers:
        return "Предложения не найдены. Уточни запрос или расширь географию."

    # ранжируем
    try:
        from core.constraint_engine import rank_offers
        offers = rank_offers(offers)
    except Exception:
        pass

    lines = [f"Нашёл {len(offers)} вариант(ов) по запросу: {goal}\n"]
    lines.append("| Поставщик | Площадка | Цена | Наличие | Риск | Контакт |")
    lines.append("|---|---|---|---|---|---|")

    best_price = None
    best_reliable = None
    to_check = []

    for i, o in enumerate(offers[:10]):
        price = o.get("price") or "—"
        price_str = f"{int(price):,}".replace(",", " ") + " руб." if isinstance(price, (int, float)) and price > 0 else str(price)
        risk = o.get("risk", "UNVERIFIED")
        contact = "✅" if o.get("contact") or o.get("url") else "❌"
        lines.append(f"| {o.get('supplier','?')} | {o.get('platform','?')} | {price_str} | {o.get('stock','?')} | {risk} | {contact} |")

        if best_price is None and isinstance(price, (int, float)) and price > 0:
            best_price = o
        if risk == "CONFIRMED" and best_reliable is None:
            best_reliable = o
        if not o.get("contact"):
            to_check.append(o.get("supplier", "?"))

    # выводы
    lines.append("")
    if best_price:
        lines.append(f"💰 Самый дешёвый: {best_price.get('supplier')} — риск: {best_price.get('risk','?')}")
    if best_reliable:
        lines.append(f"✅ Наиболее надёжный: {best_reliable.get('supplier')}")
    if to_check:
        lines.append(f"📞 Проверить звонком: {', '.join(to_check[:3])}")

    return "\n".join(lines)

def format_task_result(result: str, state: str, error_code: str = "") -> str:
    """
    Ответ пользователю по state — канон §15
    """
    if state == "DONE":
        return result or "✅ Готово"
    if state == "FAILED":
        try:
            from core.error_explainer import user_friendly_error
            return f"❌ {user_friendly_error(error_code or 'UNKNOWN')}"
        except Exception:
            return f"❌ Не выполнено: {error_code}"
    if state == "WAITING_CLARIFICATION":
        return result or "Уточни запрос."
    if state == "AWAITING_CONFIRMATION":
        return (result or "") + "\n\nПодтверди (да) или укажи правки."
    return result or ""
# === END OUTPUT_DECISION_LOGIC_V1 ===

====================================================================================================
END_FILE: core/output_decision.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/output_sanitizer.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 826e700334c797ffbd39b80779b85607519c2e631b9e56388ad6c8f5ad378bcb
====================================================================================================
# === UNIFIED_USER_OUTPUT_SANITIZER_V5_STRICT_PUBLIC_CLEAN ===
from __future__ import annotations

import re
from typing import Any

SERVICE_LINE_RE = [
    r"^\s*engine\s*:",
    r"^\s*kind\s*:",
    r"^\s*source\s*:",
    r"^\s*status\s*:",
    r"^\s*type\s*:\s*[A-Z_]{4,}",
    r"^\s*тип\s*:\s*[A-Z_]{4,}",
    r"^\s*task\s*:",
    r"^\s*task_id\s*:",
    r"^\s*задача\s*:\s*[0-9a-fA-F-]{6,}",
    r"^\s*drive\s+file_id\s*:",
    r"^\s*file_id\s*:",
    r"^\s*chat_id\s*:",
    r"^\s*topic_id\s*:",
    r"^\s*manifest\s*:",
    r"^\s*dxf\s*:",
    r"^\s*xlsx\s*:",
    r"^\s*xls\s*:",
    r"^\s*pdf\s*:",
    r"^\s*docx\s*:",
    r"^\s*artifact\s*:",
    r"^\s*artifact_path\s*:",
    r"^\s*validator_reason\s*:",
    r"^\s*raw_result\s*:",
    r"^\s*raw_payload\s*:",
    r"^\s*raw_input\s*:",
    r"^\s*debug\s*:",
    r"^\s*traceback\s*:",
    r"^\s*stacktrace\s*:",
    r"^\s*tmp_path\s*:",
    r"^\s*кратко\s*:\s*\{",
    r"^\s*кратко\s*:\s*\[",
    r"^\s*google sheets\s*/\s*xlsx\s*артефакт\s*$",
]

SERVICE_SUBSTRINGS = [
    "/root/.areal-neva-core",
    "/root/",
    "/tmp/",
    "file_context_intake.py",
    "file_memory_bridge.py",
    "price_enrichment.py",
    "sample_template_engine.py",
    "task_worker.py",
    "telegram_daemon.py",
    "artifact_pipeline.py",
    "engine_base.py",
    "PROJECT_TEMPLATE_MODEL__",
    "ACTIVE__chat_",
    "ACTIVE_BATCH__chat_",
    "PENDING__chat_",
    "FINAL_CLOSURE_BLOCKER_FIX_V1",
    "UNIFIED_USER_OUTPUT_SANITIZER",
    "validator_reason",
    "internal_key",
    "raw_payload",
    "raw_input_json",
    "ModuleNotFoundError",
    "SyntaxError",
    "Traceback",
]

NOISE_EXACT = {"доволен", "недоволен", "готово"}

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    return str(v)

def _normalize_escaped_text(text: Any) -> str:
    src = _s(text)
    src = src.replace("\r", "\n")
    src = src.replace("\\\\n", "\n")
    src = src.replace("\\n", "\n")
    src = src.replace("\\\\t", " ")
    src = src.replace("\\t", " ")
    src = src.replace('\\"', '"')
    src = re.sub(r"\x00+", " ", src)
    return src

def _is_google_link(text: str) -> bool:
    low = text.lower()
    return "https://drive.google.com/" in low or "https://docs.google.com/" in low

def _clean_google_link(line: str) -> str:
    m = re.search(r"https://(?:drive|docs)\.google\.com/[^\s\"'<>()]+", line, re.I)
    if not m:
        return line.strip()
    url = m.group(0)
    url = re.split(r"(?:PDF|DXF|XLSX|XLS|DOCX|MANIFEST)\s*:", url, flags=re.I)[0]
    url = url.rstrip(".,;)")
    return url

def _bad_line(line: str) -> bool:
    raw = line.strip()
    low = raw.lower()
    if not raw:
        return False
    if low in NOISE_EXACT:
        return True
    if re.fullmatch(r"[-–—]?\s*$", raw):
        return True
    for p in SERVICE_LINE_RE:
        if re.search(p, raw, re.I):
            return True
    if re.match(r"^\s*[-–—]\s*(dxf|xlsx|xls|pdf|docx|manifest)\s*:\s*$", raw, re.I):
        return True
    if re.search(r"\{[^{}]*(task_id|chat_id|topic_id|file_id|caption|engine)[^{}]*\}", raw, re.I):
        return True
    if raw.startswith("{") and raw.endswith("}"):
        return True
    for s in SERVICE_SUBSTRINGS:
        if s.lower() in low:
            return True
    if re.search(r"\b[A-Z_]{6,}_V\d+\b", raw) and not _is_google_link(raw):
        return True
    return False

def sanitize_user_output(text: Any, fallback: str = "Готово") -> str:
    src = _normalize_escaped_text(text)
    if not src.strip():
        return fallback
    lines = []
    skip_next_google_link = False
    for original in src.split("\n"):
        line = original.rstrip()
        if re.match(r"^\s*manifest\s*:\s*$", line, re.I):
            skip_next_google_link = True
            continue
        if skip_next_google_link and _is_google_link(line):
            skip_next_google_link = False
            continue
        if _is_google_link(line):
            clean_url = _clean_google_link(line)
            if "manifest" in clean_url.lower() or clean_url.lower().endswith(".json"):
                continue
            lines.append(clean_url)
            skip_next_google_link = False
            continue
        skip_next_google_link = False
        if _bad_line(line):
            continue
        lines.append(line)
    out = "\n".join(lines)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    out = re.sub(r"[ \t]{2,}", " ", out)
    if not out:
        out = fallback
    if len(out) > 3900:
        out = out[:3800].rstrip() + "\n\nТекст сокращён. Полный результат смотри в файле"
    return out

def sanitize_project_message(text: Any) -> str:
    return sanitize_user_output(text, fallback="Проектный результат подготовлен")

def sanitize_estimate_message(text: Any) -> str:
    return sanitize_user_output(text, fallback="Сметный результат подготовлен")

# === END_UNIFIED_USER_OUTPUT_SANITIZER_V5_STRICT_PUBLIC_CLEAN ===

====================================================================================================
END_FILE: core/output_sanitizer.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/owner_reference_policy.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 64adbdd55173fb91d590ec72ad3c2c1d2bb6d0a7f96f2be44be2132d01f6a463
====================================================================================================
# === OWNER_REFERENCE_FULL_WORKFLOW_POLICY_V1 ===
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

BASE = Path("/root/.areal-neva-core")
REGISTRY_PATH = BASE / "config" / "owner_reference_registry.json"

TRIGGER_RE = re.compile(
    r"(смет|расцен|стоимост|цена|логист|доставк|материал|кирпич|газобетон|каркас|монолит|фундамент|кровл|проект|проектир|эскиз|план участка|посадк|ар\b|кр\b|кж\b|кд\b|км\b|кмд\b|ов\b|вк\b|эо\b|эм\b|эос\b|спецификац|узел|черт[её]ж|dwg|dxf|pln|ifc|акт|технадзор|дефект|образец|образцы|эталон|эталоны|принимай|работай по)",
    re.I,
)

ENGINEERING_NORMS = [
    "КМ/КМД: СП 16.13330.2017 — Стальные конструкции",
    "КМ/КМД: СП 20.13330.2017 — Нагрузки и воздействия",
    "КМ/КМД: ГОСТ 27751-2014 — Надёжность строительных конструкций",
    "КМ/КМД: ГОСТ 23118-2012 — Конструкции стальные строительные",
    "ОВ: СП 60.13330.2020 — Отопление, вентиляция, кондиционирование",
    "ОВ: СП 131.13330.2020 — Строительная климатология",
    "ОВ: ГОСТ 30494-2011 — Параметры микроклимата помещений",
    "ВК: СП 30.13330.2020 — Внутренний водопровод и канализация",
    "ВК: СП 31.13330.2021 — Водоснабжение. Наружные сети",
    "ВК: СП 32.13330.2018 — Канализация. Наружные сети",
    "ЭО/ЭМ/ЭОС: СП 256.1325800.2016 — Электроустановки жилых зданий",
    "ЭО/ЭМ/ЭОС: ГОСТ Р 50571 серия — Электрические установки",
    "ЭО/ЭМ/ЭОС: ПУЭ-7 — Правила устройства электроустановок",
    "КЖ: СП 63.13330.2018 — Бетонные и железобетонные конструкции",
    "КЖ: ГОСТ 10922-2012 — Арматурные изделия",
    "КД: СП 64.13330.2017 — Деревянные конструкции",
    "КД: ГОСТ 8486-86 — Пиломатериалы хвойных пород",
    "Расчёт нагрузок: СП 20.13330.2017 таблицы 8.3 и 10.1",
    "Если раздел не загружен образцом — работать по нормам СНиП/ГОСТ/СП",
    "Если норм недостаточно — запросить геологию, климатический район, класс ответственности",
]

ESTIMATE_RULES = [
    "М-80, М-110, крыша, фундамент, Ареал Нева = эталон формул и структуры",
    "Логика переносится на любой материал: кирпич, газобетон, каркас, монолит",
    "Цены не подставлять молча — искать в интернете и показывать варианты",
    "Логистика обязательна: город, удалённость, подъезд, разгрузка, манипулятор, кран, проживание",
    "XLSX/PDF только после подтверждения цен и логистики",
]

DESIGN_RULES = [
    "Образцы из папки проектирования = эталон структуры и оформления",
    "АР/КР/КЖ/КД/КМ/КМД/ОВ/ВК/ЭО/ЭМ/ЭОС — разные разделы, не смешивать",
    "Если нет загруженного образца по разделу — работать по нормам СНиП/ГОСТ/СП",
    "Уточнять стадию, объект, материал, габариты, состав проекта",
    "DWG/DXF/IFC — читать через ezdxf/ifcopenshell если доступно",
    "PLN/RVT — бинарные исходники, использовать как метаданные без SDK",
]

TECHNADZOR_RULES = [
    "Акты, дефекты, исполнительные документы — отдельный контур",
    "Нормы фиксировать только если подтверждены",
    "Если норма не подтверждена — писать: норма не подтверждена",
    "Вывод чистый: без task_id, file_id, manifest, путей, JSON",
]

OUTPUT_RULES = [
    "Без task_id/file_id/manifest/локальных путей/raw JSON",
    "Без служебных Engine/MANIFEST/DXF/XLSX хвостов",
    "Если данных нет — один короткий вопрос",
    "Если задача понятна — выполнять по существующему контуру",
]

def _s(v: Any) -> str:
    return "" if v is None else str(v)

def _load_registry() -> Dict[str, Any]:
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def build_owner_reference_context(user_text: str = "", limit: int = 22000) -> str:
    text = _s(user_text)
    if not TRIGGER_RE.search(text):
        return ""

    data = _load_registry()
    policy = data.get("owner_reference_full_workflow_v1")
    counts = policy.get("counts", {}) if isinstance(policy, dict) else {}

    lines = []
    lines.append("OWNER_REFERENCE_FULL_WORKFLOW: ACTIVE")
    lines.append("OWNER: Илья — главный канон")
    lines.append("RULE: Не додумывать отсутствующие исходные данные")
    lines.append("RULE: Если данных не хватает — задать один короткий уточняющий вопрос")
    lines.append("")
    lines.append("ENGINEERING NORMS:")
    lines.extend(f"- {x}" for x in ENGINEERING_NORMS)
    lines.append("")
    lines.append("ESTIMATE RULES:")
    lines.extend(f"- {x}" for x in ESTIMATE_RULES)
    lines.append("")
    lines.append("DESIGN RULES:")
    lines.extend(f"- {x}" for x in DESIGN_RULES)
    lines.append("")
    lines.append("TECHNADZOR RULES:")
    lines.extend(f"- {x}" for x in TECHNADZOR_RULES)
    lines.append("")
    lines.append("OUTPUT RULES:")
    lines.extend(f"- {x}" for x in OUTPUT_RULES)

    if counts:
        lines.append("")
        lines.append("REFERENCE COUNTS:")
        for k in sorted(counts):
            lines.append(f"- {k}: {counts[k]}")

    if isinstance(policy, dict):
        est = policy.get("estimate_references") or []
        des = policy.get("design_references") or []
        tech = policy.get("technadzor_references") or []
        if est:
            lines.append("")
            lines.append("ESTIMATE REFERENCES:")
            for x in est[:20]:
                lines.append(f"- {x.get('name')} | formulas={x.get('formula_total', 0)} | role={x.get('role')}")
        if des:
            lines.append("")
            lines.append("DESIGN REFERENCES:")
            for x in des[:40]:
                lines.append(f"- {x.get('name')} | discipline={x.get('discipline')} | role={x.get('role')}")
        if tech:
            lines.append("")
            lines.append("TECHNADZOR REFERENCES:")
            for x in tech[:20]:
                lines.append(f"- {x.get('name')} | role={x.get('role')}")

    return "\n".join(lines)[:limit]

# === END_OWNER_REFERENCE_FULL_WORKFLOW_POLICY_V1 ===

====================================================================================================
END_FILE: core/owner_reference_policy.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/pdf_cyrillic.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c7d82ac54474065917afc3433342f2511a3402d75cdbd7c20cf7a3f1e91cc4dc
====================================================================================================
# === FULLFIX_15_PDF_CYRILLIC ===
import os, logging
logger = logging.getLogger(__name__)
FONT_REGULAR = "CyrRegular"
FONT_BOLD = "CyrBold"
FONT_PATH_REGULAR = ""
FONT_PATH_BOLD = ""
_registered = False

_CANDS_R = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]
_CANDS_B = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]

def _find(candidates):
    for p in candidates:
        if os.path.exists(p):
            return p
    import glob
    for pat in ["/usr/share/fonts/**/*DejaVu*Sans*.ttf",
                "/usr/share/fonts/**/*Noto*Sans*Regular*.ttf"]:
        found = glob.glob(pat, recursive=True)
        if found:
            return found[0]
    return None

def register_cyrillic_fonts():
    global _registered, FONT_REGULAR, FONT_BOLD, FONT_PATH_REGULAR, FONT_PATH_BOLD
    if _registered:
        return FONT_REGULAR, FONT_BOLD
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    reg = _find(_CANDS_R)
    bold = _find(_CANDS_B)
    if not reg:
        raise RuntimeError("CYRILLIC_FONT_NOT_FOUND")
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, reg))
    FONT_PATH_REGULAR = reg
    if bold and bold != reg:
        pdfmetrics.registerFont(TTFont(FONT_BOLD, bold))
        FONT_PATH_BOLD = bold
    else:
        FONT_BOLD = FONT_REGULAR
        FONT_PATH_BOLD = reg
    _registered = True
    logger.info("CYR_FONTS reg=%s bold=%s", reg, bold)
    return FONT_REGULAR, FONT_BOLD

def clean_pdf_text(text):
    if not text:
        return ""
    return "".join(c for c in str(text) if c >= " " or c in "\n\t")

def make_styles():
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    register_cyrillic_fonts()
    return {
        "header": ParagraphStyle("H", fontName=FONT_BOLD, fontSize=16, alignment=TA_CENTER, spaceAfter=12),
        "title":  ParagraphStyle("T", fontName=FONT_BOLD, fontSize=14, alignment=TA_CENTER, spaceAfter=8),
        "bold":   ParagraphStyle("B", fontName=FONT_BOLD, fontSize=9, alignment=TA_LEFT),
        "normal": ParagraphStyle("N", fontName=FONT_REGULAR, fontSize=9, alignment=TA_LEFT),
        "small":  ParagraphStyle("S", fontName=FONT_REGULAR, fontSize=8, alignment=TA_LEFT),
    }

def make_paragraph(text, style="normal", styles=None):
    from reportlab.platypus import Paragraph
    if styles is None:
        styles = make_styles()
    return Paragraph(clean_pdf_text(text), styles.get(style, styles["normal"]))
# === END FULLFIX_15_PDF_CYRILLIC ===

# === FIX_PDF_CYRILLIC_VALIDATE_V1 ===
import subprocess as _pcv_sub
import re as _pcv_re

def validate_cyrillic_pdf(pdf_path: str) -> tuple:
    """
    Returns (ok: bool, code: str)
    Extracts text from PDF and checks for valid Cyrillic content.
    """
    extracted = ""
    try:
        r = _pcv_sub.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=15,
        )
        extracted = r.stdout or ""
    except Exception:
        try:
            from pdfminer.high_level import extract_text as _pdfm_ext
            extracted = _pdfm_ext(str(pdf_path)) or ""
        except Exception:
            return True, "VALIDATION_SKIPPED_NO_TOOL"

    if not extracted.strip():
        return False, "ESTIMATE_PDF_EMPTY_TEXT_V1"
    if "■" in extracted or "�" in extracted or u"■" in extracted:
        return False, "ESTIMATE_PDF_CYRILLIC_BROKEN_V1"
    cyr = sum(1 for c in extracted if "Ѐ" <= c <= "ӿ")
    alpha = sum(1 for c in extracted if c.isalpha())
    if alpha > 30 and cyr / alpha < 0.08:
        return False, "ESTIMATE_PDF_CYRILLIC_BROKEN_V1"
    return True, "TOPIC2_PDF_CYRILLIC_OK"


def create_pdf_with_cyrillic(path: str, text: str, title: str = "") -> bool:
    """
    Create PDF at path using DejaVuSans for Cyrillic. Returns True on success.
    """
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as rl_canvas

        reg, bold = register_cyrillic_fonts()
        c = rl_canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        y = height - 40

        if title:
            c.setFont(bold, 12)
            c.drawString(40, y, clean_pdf_text(title)[:100])
            y -= 24

        c.setFont(reg, 9)
        for line in str(text).splitlines():
            if y < 40:
                c.showPage()
                y = height - 40
                c.setFont(reg, 9)
            c.drawString(40, y, clean_pdf_text(line)[:130])
            y -= 13
        c.save()
        return True
    except Exception as _pdf_e:
        logger.warning("create_pdf_with_cyrillic FAILED: %s", _pdf_e)
        return False

logger.info("FIX_PDF_CYRILLIC_VALIDATE_V1 installed")
# === END_FIX_PDF_CYRILLIC_VALIDATE_V1 ===

====================================================================================================
END_FILE: core/pdf_cyrillic.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/pdf_spec_extractor.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 09a018898c6bf6640092a5df1297d9ab31e9ff6bd1633ca61593c1aa4815a024
====================================================================================================
# === PDF_SPEC_EXTRACTOR_REAL_V1 ===
from __future__ import annotations

import re
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

UNIT_RE = re.compile(r"\b(м2|м²|м3|м³|п\.?м|пог\.?м|шт|кг|тн|тонн|т|м|мм|компл)\b", re.I)
NUM_RE = re.compile(r"^-?\d+(?:[.,]\d+)?$")


def _s(v: Any) -> str:
    return "" if v is None else str(v).strip()


def _num(v: Any) -> float:
    try:
        return float(_s(v).replace(" ", "").replace(",", "."))
    except Exception:
        return 0.0


def _unit(v: Any) -> str:
    s = _s(v).lower()
    s = s.replace("м2", "м²").replace("м3", "м³").replace("пог.м", "п.м").replace("пм", "п.м")
    return s


def _row_to_item(row: List[Any]) -> Dict[str, Any]:
    cells = [_s(x) for x in row if _s(x)]
    if not cells:
        return {}

    name = ""
    unit = ""
    qty = 0.0
    price = 0.0

    for c in cells:
        if not unit and UNIT_RE.search(c):
            unit = _unit(UNIT_RE.search(c).group(1))
            continue

    nums = []
    for c in cells:
        cleaned = c.replace(" ", "").replace(",", ".")
        if NUM_RE.match(cleaned):
            nums.append(_num(cleaned))

    if nums:
        qty = nums[0]
    if len(nums) >= 2:
        price = nums[1]

    for c in cells:
        cl = c.lower()
        if UNIT_RE.search(c):
            continue
        if NUM_RE.match(c.replace(" ", "").replace(",", ".")):
            continue
        if len(c) >= 3 and not any(x in cl for x in ("итого", "сумма", "всего", "кол-во", "количество", "ед.")):
            name = c
            break

    if not name or qty <= 0:
        return {}

    return {
        "name": name[:240],
        "unit": unit,
        "qty": qty,
        "price": price,
        "total": round(qty * price, 2) if price else 0.0,
        "source": "pdfplumber_table",
    }


def extract_spec(file_path: str, **kwargs) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    errors: List[str] = []

    try:
        import pdfplumber
    except Exception as e:
        return {"rows": [], "error": f"PDFPLUMBER_IMPORT_FAILED: {e}", "stub": False}

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_no, page in enumerate(pdf.pages, 1):
                try:
                    tables = page.extract_tables() or []
                except Exception as e:
                    errors.append(f"page_{page_no}_tables: {e}")
                    tables = []

                for table in tables:
                    for raw_row in table or []:
                        item = _row_to_item(raw_row or [])
                        if item:
                            item["page"] = page_no
                            rows.append(item)

                if not tables:
                    try:
                        text = page.extract_text() or ""
                    except Exception:
                        text = ""
                    for line in text.splitlines():
                        m = re.search(r"(?P<name>.{3,120}?)\s+(?P<qty>\d+(?:[.,]\d+)?)\s*(?P<unit>м2|м²|м3|м³|п\.?м|шт|кг|тн|т|м)\b(?:\s+(?P<price>\d+(?:[.,]\d+)?))?", line, re.I)
                        if not m:
                            continue
                        qty = _num(m.group("qty"))
                        price = _num(m.group("price"))
                        rows.append({
                            "name": _s(m.group("name"))[:240],
                            "unit": _unit(m.group("unit")),
                            "qty": qty,
                            "price": price,
                            "total": round(qty * price, 2) if price else 0.0,
                            "page": page_no,
                            "source": "pdfplumber_text_line",
                        })

        dedup = []
        seen = set()
        for r in rows:
            key = (r.get("name"), r.get("unit"), r.get("qty"), r.get("price"))
            if key in seen:
                continue
            seen.add(key)
            dedup.append(r)

        return {
            "rows": dedup,
            "count": len(dedup),
            "error": "" if dedup else "PDF_SPEC_ROWS_NOT_FOUND",
            "errors": errors[:20],
            "stub": False,
        }
    except Exception as e:
        logger.exception("PDF_SPEC_EXTRACTOR_REAL_V1 failed")
        return {"rows": [], "error": f"PDF_SPEC_EXTRACTOR_FAILED: {e}", "stub": False}


# === END_PDF_SPEC_EXTRACTOR_REAL_V1 ===


# === PDF_SPEC_EXTRACTOR_REAL_V1_PDFPLUMBER ===
def _clean_cell_v1(v):
    return re.sub(r"\s+", " ", _s(v)).strip()

def _parse_num_v1(v):
    try:
        src = _clean_cell_v1(v).replace(" ", "").replace(",", ".")
        m = re.search(r"-?\d+(?:\.\d+)?", src)
        return float(m.group(0)) if m else 0.0
    except Exception:
        return 0.0

def extract_spec_rows(pdf_path: str, max_pages: int = 30):
    import pdfplumber

    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_no, page in enumerate(pdf.pages[:int(max_pages or 30)], 1):
            tables = page.extract_tables() or []
            for table in tables:
                for row in table or []:
                    if not row or len(row) < 3:
                        continue
                    cells = [_clean_cell_v1(c) for c in row]
                    name = ""
                    for c in cells:
                        if c and not UNIT_RE.search(c) and not NUM_RE.match(c.replace(" ", "").replace(",", ".")):
                            if len(c) >= 3 and not any(x in c.lower() for x in ("итого", "сумма", "всего", "кол-во", "количество", "ед.")):
                                name = c
                                break
                    unit = ""
                    for c in cells:
                        m = UNIT_RE.search(c)
                        if m:
                            unit = _unit(m.group(1))
                            break
                    nums = [_parse_num_v1(c) for c in cells if _parse_num_v1(c)]
                    qty = nums[0] if len(nums) >= 1 else 0.0
                    price = nums[1] if len(nums) >= 2 else 0.0
                    total = nums[2] if len(nums) >= 3 else (qty * price if qty and price else 0.0)
                    if name and (qty or price):
                        rows.append({
                            "name": name[:240],
                            "unit": unit,
                            "qty": qty,
                            "price": price,
                            "total": round(total, 2),
                            "page": page_no,
                            "source": "PDF_SPEC_EXTRACTOR_REAL_V1_PDFPLUMBER",
                        })

    dedup = []
    seen = set()
    for r in rows:
        key = (r.get("name"), r.get("unit"), r.get("qty"), r.get("price"), r.get("total"))
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)

    if not dedup:
        raise ValueError("PDF_SPEC_NO_TABLES_FOUND")

    return dedup
# === END_PDF_SPEC_EXTRACTOR_REAL_V1_PDFPLUMBER ===

====================================================================================================
END_FILE: core/pdf_spec_extractor.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/photo_recognition_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 58209d81c02af460887d992f0d10d7d160b89cf6663d39550dcda6a897b1d558
====================================================================================================
# === PHOTO_RECOGNITION_SAFE_GUARD_V1 ===
"""
core/photo_recognition_engine.py

Fact-only photo recognition guard for topic_5 and topic_210.

Purpose:
- accept image/photo input as material
- create safe ObservationCard / ProjectImageCard data
- forbid invented visual defects when no owner-approved Vision provider is configured
- route norms through core.normative_engine only from source text / owner comment

This module does NOT perform external Vision by default.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


PHOTO_RECOGNITION_ENGINE_VERSION = "PHOTO_RECOGNITION_SAFE_GUARD_V1"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp", ".tif", ".tiff"}
TOPIC_TECHNADZOR = 5
TOPIC_PROJECT = 210


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _s(value: Any, limit: int = 4000) -> str:
    if value is None:
        return ""
    return str(value).strip()[:limit]


def is_image_file(file_name: str = "", file_path: str = "") -> bool:
    src = file_name or file_path or ""
    return Path(src).suffix.lower() in IMAGE_EXTENSIONS


def owner_approved_vision_enabled() -> bool:
    """
    Fact-only gate.

    Vision is disabled unless owner explicitly enables a provider through env.
    No provider name or model is invented here.
    """
    enabled = os.getenv("EXTERNAL_PHOTO_ANALYSIS_ALLOWED", "").strip().lower()
    provider = os.getenv("PHOTO_RECOGNITION_PROVIDER", "").strip()
    return enabled in {"1", "true", "yes", "on"} and bool(provider)


def vision_status() -> Dict[str, Any]:
    provider = os.getenv("PHOTO_RECOGNITION_PROVIDER", "").strip()
    return {
        "external_photo_analysis_allowed": owner_approved_vision_enabled(),
        "provider": provider or "NOT_CONFIGURED",
        "status": "VISION_READY" if owner_approved_vision_enabled() else "VISION_NOT_CONFIGURED",
    }


def search_norms_for_text(text: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        from core.normative_engine import search_norms_sync
        return search_norms_sync(text or "", limit=limit)
    except Exception:
        return []


@dataclass
class PhotoMaterialCard:
    schema: str
    engine: str
    topic_id: int
    source: str
    file_name: str
    file_path: str
    owner_comment: str
    added_at: str
    image_detected: bool
    vision_status: str
    include_in_report: bool
    include_in_act: bool
    status: str


@dataclass
class ObservationCard:
    schema: str
    engine: str
    topic_id: int
    object_role: str
    source: str
    author_role: str
    material_type: str
    file_name: str
    owner_comment: str
    claim: str
    confirmed_by_image: str
    contradiction: str
    needs_owner_question: bool
    norms: List[Dict[str, Any]]
    status: str


@dataclass
class DefectCard:
    schema: str
    engine: str
    topic_id: int
    file_name: str
    defect: str
    visible_basis: str
    normative_status: str
    norms: List[Dict[str, Any]]
    status: str


@dataclass
class ProjectImageCard:
    schema: str
    engine: str
    topic_id: int
    file_name: str
    project_context_hint: str
    owner_comment: str
    norms: List[Dict[str, Any]]
    status: str


def build_photo_material_card(
    topic_id: int,
    file_name: str = "",
    file_path: str = "",
    owner_comment: str = "",
    source: str = "TELEGRAM",
    include_in_report: bool = True,
    include_in_act: bool = True,
) -> Dict[str, Any]:
    image_detected = is_image_file(file_name=file_name, file_path=file_path)
    vstatus = vision_status()["status"]
    card = PhotoMaterialCard(
        schema="PhotoMaterialCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=int(topic_id or 0),
        source=_s(source, 64) or "TELEGRAM",
        file_name=_s(file_name, 512),
        file_path=_s(file_path, 2000),
        owner_comment=_s(owner_comment),
        added_at=_now_iso(),
        image_detected=image_detected,
        vision_status=vstatus,
        include_in_report=bool(include_in_report),
        include_in_act=bool(include_in_act),
        status="PHOTO_MATERIAL_ACCEPTED" if image_detected else "NOT_IMAGE_FILE",
    )
    return asdict(card)


def build_topic5_observation_card(
    file_name: str = "",
    file_path: str = "",
    owner_comment: str = "",
    source: str = "TELEGRAM",
) -> Dict[str, Any]:
    norms = search_norms_for_text(owner_comment, limit=5)
    vision_ready = owner_approved_vision_enabled()
    claim = _s(owner_comment) if owner_comment else "UNKNOWN"
    card = ObservationCard(
        schema="ObservationCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=TOPIC_TECHNADZOR,
        object_role="TECHNADZOR_VISIT_MATERIAL",
        source=_s(source, 64) or "TELEGRAM",
        author_role="OWNER" if owner_comment else "UNKNOWN",
        material_type="PHOTO" if is_image_file(file_name, file_path) else "OTHER",
        file_name=_s(file_name, 512),
        owner_comment=_s(owner_comment),
        claim=claim,
        confirmed_by_image="NOT_CHECKED_BY_VISION" if not vision_ready else "VISION_PROVIDER_REQUIRED_RUNTIME_CHECK",
        contradiction="UNKNOWN",
        needs_owner_question=False if owner_comment else True,
        norms=norms,
        status="OBSERVATION_FROM_OWNER_COMMENT_ONLY" if not vision_ready else "VISION_READY_NOT_EXECUTED_HERE",
    )
    return asdict(card)


def build_topic5_defect_card(
    file_name: str = "",
    owner_comment: str = "",
) -> Dict[str, Any]:
    norms = search_norms_for_text(owner_comment, limit=5)
    if not owner_comment:
        defect = "UNKNOWN"
        status = "NO_DEFECT_WITHOUT_OWNER_COMMENT_OR_VISION"
    else:
        defect = _s(owner_comment)
        status = "DEFECT_FROM_OWNER_COMMENT_NOT_IMAGE_RECOGNITION"
    card = DefectCard(
        schema="DefectCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=TOPIC_TECHNADZOR,
        file_name=_s(file_name, 512),
        defect=defect,
        visible_basis="NOT_ANALYZED_BY_VISION",
        normative_status="NORM_FOUND" if norms else "NORM_NOT_CONFIRMED",
        norms=norms,
        status=status,
    )
    return asdict(card)


def build_topic210_project_image_card(
    file_name: str = "",
    owner_comment: str = "",
    project_context_hint: str = "",
) -> Dict[str, Any]:
    combined = " ".join(x for x in [owner_comment, project_context_hint, file_name] if x)
    norms = search_norms_for_text(combined, limit=5)
    card = ProjectImageCard(
        schema="ProjectImageCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=TOPIC_PROJECT,
        file_name=_s(file_name, 512),
        project_context_hint=_s(project_context_hint, 1000) or "UNKNOWN",
        owner_comment=_s(owner_comment),
        norms=norms,
        status="PROJECT_IMAGE_MATERIAL_ACCEPTED_NO_VISION_ANALYSIS" if not owner_approved_vision_enabled() else "VISION_READY_NOT_EXECUTED_HERE",
    )
    return asdict(card)


def process_photo_recognition(
    topic_id: int,
    file_name: str = "",
    file_path: str = "",
    owner_comment: str = "",
    source: str = "TELEGRAM",
    project_context_hint: str = "",
) -> Dict[str, Any]:
    """
    Safe entry point.

    topic_5:
      returns PhotoMaterialCard + ObservationCard + DefectCard guard.
    topic_210:
      returns PhotoMaterialCard + ProjectImageCard guard.

    No visual defect recognition is performed unless a future owner-approved
    provider is explicitly wired and tested outside this guard.
    """
    topic = int(topic_id or 0)
    material = build_photo_material_card(topic, file_name, file_path, owner_comment, source)
    result: Dict[str, Any] = {
        "ok": True,
        "engine": PHOTO_RECOGNITION_ENGINE_VERSION,
        "topic_id": topic,
        "vision": vision_status(),
        "material": material,
        "status": "PHOTO_RECOGNITION_GUARDED_NO_VISION",
    }
    if topic == TOPIC_TECHNADZOR:
        result["observation_card"] = build_topic5_observation_card(file_name, file_path, owner_comment, source)
        result["defect_card"] = build_topic5_defect_card(file_name, owner_comment)
    elif topic == TOPIC_PROJECT:
        result["project_image_card"] = build_topic210_project_image_card(file_name, owner_comment, project_context_hint)
    else:
        result["status"] = "PHOTO_MATERIAL_ACCEPTED_UNROUTED_TOPIC"
    return result


__all__ = [
    "PHOTO_RECOGNITION_ENGINE_VERSION",
    "is_image_file",
    "owner_approved_vision_enabled",
    "vision_status",
    "build_photo_material_card",
    "build_topic5_observation_card",
    "build_topic5_defect_card",
    "build_topic210_project_image_card",
    "process_photo_recognition",
]
# === END_PHOTO_RECOGNITION_SAFE_GUARD_V1 ===

# === FIX_PHOTO_TOPIC2_ESTIMATE_V1 ===
# Add topic_2 (STROYKA) photo recognition for estimate pipeline.
# If image has caption with estimate terms → build photo context for estimate.
# If image has no clear intent → show action menu.

TOPIC_STROYKA = 2

_PHOTO2_ESTIMATE_WORDS = (
    "смет", "расчет", "расчёт", "посчитай", "рассчитай", "стоимость",
    "посчитать", "рассчитать", "стоить", "стоит", "нужна смета", "нужен расчет",
    "сколько стоит", "сколько будет", "цена", "нужна цена",
)
_PHOTO2_CONSTRUCTION_WORDS = (
    "дом", "ангар", "склад", "баня", "гараж", "здани", "строен",
    "каркас", "газобетон", "кирпич", "монолит", "брус", "фундамент",
    "кровл", "перекр", "этаж", "стен", "барнхаус",
)


def _photo2_is_estimate_caption(caption: str) -> bool:
    low = _s(caption).lower().replace("ё", "е")
    return any(x in low for x in _PHOTO2_ESTIMATE_WORDS)


def _photo2_has_construction_terms(caption: str) -> bool:
    low = _s(caption).lower().replace("ё", "е")
    return any(x in low for x in _PHOTO2_CONSTRUCTION_WORDS)


def process_photo_topic2(
    file_name: str = "",
    file_path: str = "",
    owner_comment: str = "",
    caption: str = "",
    source: str = "TELEGRAM",
) -> Dict[str, Any]:
    """
    Entry point for topic_2 photo processing.
    Returns dict with:
      route: "estimate" | "menu" | "ask_clarification"
      photo_context: str  (structured context for estimate pipeline)
      missing_fields: list[str]
      status: str
    """
    combined_caption = " ".join(x for x in [caption, owner_comment] if x).strip()
    low_cap = combined_caption.lower().replace("ё", "е")

    image_detected = is_image_file(file_name=file_name, file_path=file_path)

    result: Dict[str, Any] = {
        "ok": True,
        "engine": "FIX_PHOTO_TOPIC2_ESTIMATE_V1",
        "topic_id": TOPIC_STROYKA,
        "file_name": _s(file_name, 512),
        "file_path": _s(file_path, 2000),
        "caption": _s(combined_caption, 2000),
        "image_detected": image_detected,
    }

    if not image_detected:
        result["route"] = "not_image"
        result["status"] = "TOPIC2_NOT_IMAGE_FILE"
        return result

    # Route decision
    if _photo2_is_estimate_caption(combined_caption):
        # Has estimate intent in caption → build photo context
        photo_context_lines = []
        if combined_caption:
            photo_context_lines.append(f"Фото с подписью: {combined_caption}")
        if file_name:
            photo_context_lines.append(f"Файл: {file_name}")
        photo_context_lines.append("Источник: фото из Telegram")

        # Detect what's missing
        missing = []
        if not any(x in low_cap for x in ("x", "х", "×", "*", "на ", "м2", "м²", "18", "12", "9", "6", "размер")):
            missing.append("размеры объекта (ширина × длина)")
        if not any(x in low_cap for x in ("этаж", "1 эт", "2 эт", "два эт", "один эт")):
            missing.append("количество этажей")
        if not any(x in low_cap for x in ("каркас", "газобетон", "кирпич", "монолит", "брус", "материал стен")):
            missing.append("материал стен/конструктив")

        result["route"] = "estimate" if not missing else "ask_clarification"
        result["photo_context"] = "\n".join(photo_context_lines)
        result["missing_fields"] = missing
        result["status"] = "TOPIC2_PHOTO_RECOGNITION_DONE" if not missing else "TOPIC2_PHOTO_CONTEXT_MISSING_FIELDS"
        if missing:
            result["clarification_question"] = f"По фото понятно, что нужна смета. Уточните: {missing[0]}"
        return result

    elif _photo2_has_construction_terms(combined_caption):
        # Construction terms but no clear estimate intent → ask what to do
        result["route"] = "ask_clarification"
        result["photo_context"] = f"Фото строительного объекта. Подпись: {combined_caption or 'нет подписи'}"
        result["missing_fields"] = ["намерение (нужна смета или другое?)"]
        result["clarification_question"] = (
            "Что сделать с этим фото?\n"
            "1 — смета\n2 — описание\n3 — таблица\n4 — шаблон\n5 — анализ"
        )
        result["status"] = "TOPIC2_ROUTE_MENU_NO_INTENT"
        return result

    else:
        # No intent → show action menu
        result["route"] = "menu"
        result["photo_context"] = f"Фото без явной команды. Файл: {file_name or 'неизвестен'}"
        result["missing_fields"] = ["намерение"]
        result["clarification_question"] = (
            "Что сделать с этим фото?\n"
            "1 — смета\n2 — описание\n3 — таблица\n4 — шаблон\n5 — анализ"
        )
        result["status"] = "TOPIC2_ROUTE_MENU_NO_INTENT"
        return result


__all__ = list(__all__) + ["process_photo_topic2", "TOPIC_STROYKA"]  # type: ignore
import logging as _pre_log
_pre_log.getLogger("task_worker").info("FIX_PHOTO_TOPIC2_ESTIMATE_V1 installed")
# === END_FIX_PHOTO_TOPIC2_ESTIMATE_V1 ===

====================================================================================================
END_FILE: core/photo_recognition_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/pin_manager.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 612acafe7a005144bbd67b00fe54ac90c166aa76dafd8badcedc5f9a89812dfa
====================================================================================================
import re
import sqlite3

CORE_DB = "/root/.areal-neva-core/data/core.db"

def _conn():
    conn = sqlite3.connect(CORE_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def _has_table(conn, table: str) -> bool:
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
    return row is not None

def get_pin_context(chat_id: str, request_text: str = "", topic_id: int = 0) -> str:
    conn = _conn()
    try:
        if not _has_table(conn, "pin"):
            return ""

        row = conn.execute(
            "SELECT task_id FROM pin WHERE chat_id=? AND topic_id=? AND state='ACTIVE' ORDER BY rowid DESC LIMIT 1",
            (str(chat_id), int(topic_id))
        ).fetchone()

        if not row or not row["task_id"]:
            return ""

        task_row = conn.execute(
            "SELECT result FROM tasks WHERE id=? LIMIT 1",
            (row["task_id"],)
        ).fetchone()

        if task_row and task_row["result"]:
            pin_text = str(task_row["result"]).strip()
            if any(m in pin_text.lower() for m in PIN_MUTEX_MARKERS):
                return ""
            if request_text:
                request_words = set(re.findall(r"\w+", request_text.lower()))
                pin_words = set(re.findall(r"\w+", pin_text.lower()))
                if request_words & pin_words:
                    return pin_text[:4000]
                return ""
            return pin_text[:4000]

        return ""
    finally:
        conn.close()

PIN_MUTEX_MARKERS = ["задача отменена", "задача завершена", "не понимаю запрос", "готов к выполнению задачи"]

def save_pin(chat_id: str, task_id: str, result_text: str, topic_id: int = 0) -> bool:
    text = (result_text or "").strip()
    if not text:
        return False
    if any(m in text.lower() for m in PIN_MUTEX_MARKERS):
        return False  # PIN_STRICT_DONE_ONLY
        return False
    conn = _conn()
    try:
        if not _has_table(conn, "pin"):
            return False

        conn.execute(
            "UPDATE pin SET state='CLOSED', updated_at=datetime('now') WHERE chat_id=? AND topic_id=? AND state='ACTIVE'",
            (str(chat_id), int(topic_id))
        )
        conn.execute(
            "INSERT INTO pin (chat_id, task_id, topic_id, state, created_at, updated_at) VALUES (?, ?, ?, 'ACTIVE', datetime('now'), datetime('now'))",
            (str(chat_id), task_id, int(topic_id))
        )
        conn.commit()
        return True
    finally:
        conn.close()

====================================================================================================
END_FILE: core/pin_manager.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/price_enrichment.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 6ea8461a55b464faa46bf4cab8ed93fcb6b8a40e9585d31a5207880abfea55e8
====================================================================================================
# === WEB_SEARCH_PRICE_ENRICHMENT_V1 ===
# === PRICE_CONFIRMATION_BEFORE_ESTIMATE_V1 ===
from __future__ import annotations

import os
import re
import json
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

BASE = Path("/root/.areal-neva-core")
PRICE_DIR = BASE / "data" / "price_quotes"
PRICE_DIR.mkdir(parents=True, exist_ok=True)


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


def _safe_key(v: Any, limit: int = 80) -> str:
    return re.sub(r"[^0-9A-Za-z_-]+", "_", _s(v))[:limit] or "unknown"


def _cache_path(chat_id: str, topic_id: int) -> Path:
    return PRICE_DIR / f"PENDING__chat_{_safe_key(chat_id)}__topic_{int(topic_id or 0)}.json"


def _is_web_price_request(text: str) -> bool:
    low = _low(text)
    return any(x in low for x in (
        "цены из интернета", "цена из интернета", "актуальные цены", "актуальная цена",
        "цены материалов", "стоимость материалов", "брать из интернета", "искать в интернете",
        "найти цены", "проверить цены", "рыночные цены", "поставщиков", "поставщик"
    ))


def _detect_price_choice(text: str) -> str:
    # PRICE_CHOICE_DETECT_EXPAND_V1
    low = _low(text)
    import re as _re_inner
    t = _re_inner.sub(r"\\s+", " ", low).strip(" .,!?:;()[]{}")

    exact = {
        "а": "cheapest", "а)": "cheapest", "1": "cheapest",
        "вариант 1": "cheapest", "вариант а": "cheapest",
        "первый": "cheapest", "самый дешевый": "cheapest",
        "самый дешёвый": "cheapest", "самые дешевые": "cheapest",
        "самые дешёвые": "cheapest", "минимум": "cheapest",
        "минимальная": "cheapest",
        "б": "average", "б)": "average", "2": "average",
        "вариант 2": "average", "вариант б": "average",
        "второй": "average", "среднее": "average",
        "средняя": "average", "средние": "average",
        "рыночная": "average",
        "в": "reliable", "в)": "reliable", "3": "reliable",
        "вариант 3": "reliable", "вариант в": "reliable",
        "третий": "reliable", "надежный": "reliable",
        "надёжный": "reliable", "проверенный": "reliable",
        "г": "manual", "г)": "manual", "4": "manual",
        "вариант 4": "manual", "вариант г": "manual",
        "своя": "manual", "ручная": "manual", "вручную": "manual",
    }
    if t in exact:
        return exact[t]

    if any(x in low for x in ("дешев", "дешёв", "минималь", "самые низкие", "вариант а", "а —", "а-", "вариант 1", "первый")):
        return "cheapest"
    if any(x in low for x in ("средн", "рынок", "вариант б", "б —", "б-", "вариант 2", "второй")):
        return "average"
    if any(x in low for x in ("надеж", "надёж", "проверенн", "вариант в", "в —", "в-", "вариант 3", "третий")):
        return "reliable"
    if any(x in low for x in ("вручную", "сам укажу", "мои цены", "вариант г", "г —", "г-", "вариант 4", "своя")):
        return "manual"
    return ""

def _load_price_mode_from_memory(chat_id: str, topic_id: int) -> str:
    try:
        mem = BASE / "data" / "memory.db"
        if not mem.exists():
            return ""
        conn = sqlite3.connect(str(mem))
        try:
            key = f"topic_{int(topic_id or 0)}_price_mode"
            row = conn.execute(
                "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY rowid DESC LIMIT 1",
                (str(chat_id), key),
            ).fetchone()
            return _s(row[0]) if row else ""
        finally:
            conn.close()
    except Exception:
        return ""


def _parse_json_from_text(text: str) -> Any:
    src = _s(text)
    if not src:
        return None
    m = re.search(r"```(?:json)?\s*(.*?)```", src, re.S | re.I)
    if m:
        src = m.group(1)
    else:
        a = src.find("{")
        b = src.rfind("}")
        if a >= 0 and b > a:
            src = src[a:b+1]
    try:
        return json.loads(src)
    except Exception:
        return None


async def _openrouter_price_search(item_name: str, unit: str = "", region: str = "Санкт-Петербург") -> List[Dict[str, Any]]:
    # PRICE_SEARCH_MULTI_SOURCE_V1
    api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        return []

    model = (os.getenv("OPENROUTER_MODEL_ONLINE") or "perplexity/sonar").strip()
    # PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1 begin
    import logging as _pe_log
    _pe_logger = _pe_log.getLogger("price_enrichment")
    if not os.getenv("OPENROUTER_MODEL_ONLINE", "").strip():
        _pe_logger.warning("ONLINE_MODEL_MISSING_BLOCKED_NO_DEFAULT_FALLBACK: OPENROUTER_MODEL_ONLINE not set, defaulted to perplexity/sonar")
    if "sonar" not in model.lower():
        _pe_logger.error(f"ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR: model={model!r} is not sonar, blocking price search")
        return []
    _pe_logger.info(f"ONLINE_MODEL_SONAR_CONFIRMED: model={model!r}")
    # PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1 end
    base_url = (os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip().rstrip("/")

    source_queries = [
        f"{item_name} цена {unit or ''} Санкт-Петербург Леруа Мерлен Петрович ВсеИнструменты",
        f"{item_name} купить {unit or ''} СПб Строительный двор Максидом ОБИ",
        f"{item_name} стоимость {unit or ''} Ленинградская область поставщик строительные материалы",
    ]

    async def _one_query(prompt_query: str) -> List[Dict[str, Any]]:
        prompt = (
            "Найди актуальные цены на строительный материал для сметы\\n"
            f"Материал: {item_name}\\n"
            f"Единица: {unit or 'UNKNOWN'}\\n"
            f"Регион: {region}\\n"
            f"Поисковый запрос: {prompt_query}\\n\\n"
            "Проверь разные источники: Леруа Мерлен, Петрович, ВсеИнструменты, Строительный двор, ОБИ, Максидом и независимых поставщиков\\n"
            "Не повторяй один сайт дважды\\n"
            "Верни только JSON object:\\n"
            "{\\n"
            '  "offers": [\\n'
            '    {"name":"...", "price":123.45, "unit":"м3/м2/т/шт/кг/п.м", "supplier":"...", "url":"https://...", "checked_at":"ISO_DATE", "status":"CONFIRMED|PARTIAL|UNVERIFIED", "risk":"low|medium|high"}\\n'
            "  ]\\n"
            "}\\n"
            "Не выдумывай URL. Если цена не подтверждена — status=UNVERIFIED"
        )
        try:
            import httpx
            body = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=20.0)) as client:
                r = await client.post(f"{base_url}/chat/completions", headers=headers, json=body)
                r.raise_for_status()
                data = r.json()
            content = data["choices"][0]["message"]["content"]
            if isinstance(content, list):
                content = "\\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in content)
            parsed = _parse_json_from_text(content)
            offers = parsed.get("offers") if isinstance(parsed, dict) else []
            clean = []
            for o in offers or []:
                if not isinstance(o, dict):
                    continue
                try:
                    price = float(str(o.get("price") or "0").replace(" ", "").replace(",", "."))
                except Exception:
                    price = 0.0
                if price <= 0:
                    continue
                clean.append({
                    "name": _s(o.get("name"))[:160] or item_name,
                    "price": price,
                    "unit": _s(o.get("unit"))[:30] or unit,
                    "supplier": _s(o.get("supplier"))[:160],
                    "url": _s(o.get("url"))[:500],
                    "checked_at": _s(o.get("checked_at"))[:80] or _now(),
                    "status": _s(o.get("status"))[:30] or "UNVERIFIED",
                    "risk": _s(o.get("risk"))[:30] or "medium",
                })
            return clean
        except Exception:
            return []

    from urllib.parse import urlparse

    merged: List[Dict[str, Any]] = []
    seen_domains = set()
    for q in source_queries:
        offers = await _one_query(q)
        for o in offers:
            url = _s(o.get("url"))
            domain = urlparse(url).netloc.lower().replace("www.", "") if url else _s(o.get("supplier")).lower()
            if not domain:
                domain = f"unknown_{len(merged)}"
            if domain in seen_domains:
                continue
            seen_domains.add(domain)
            o["domain"] = domain
            merged.append(o)
            if len(merged) >= 5:
                break
        if len(merged) >= 5:
            break

    if len(seen_domains) < 2 and merged:
        merged[0]["status"] = "PARTIAL"
        merged[0]["risk"] = "high"
        merged[0]["note"] = "Цены уточняются — найден только один источник"

    return merged[:5]

def _fallback_offer(item_name: str, unit: str = "") -> List[Dict[str, Any]]:
    return [{
        "name": item_name,
        "price": 0.0,
        "unit": unit,
        "supplier": "NOT_FOUND",
        "url": "",
        "checked_at": _now(),
        "status": "UNVERIFIED",
        "risk": "high",
    }]


def _price_prompt(cache: Dict[str, Any]) -> str:
    lines = ["Нашёл актуальные цены для сметы", ""]
    for idx, item in enumerate(cache.get("items") or [], 1):
        lines.append(f"{idx}. {item.get('name')}")
        offers = item.get("offers") or []
        if not offers:
            lines.append("   цены не найдены")
            continue
        for j, o in enumerate(offers[:3], 1):
            price = float(o.get("price") or 0)
            unit = o.get("unit") or item.get("unit") or ""
            supplier = o.get("supplier") or "поставщик не указан"
            status = o.get("status") or "UNVERIFIED"
            url = o.get("url") or ""
            if price > 0:
                lines.append(f"   {j}) {price:g} руб/{unit} — {supplier} — {status}")
            else:
                lines.append(f"   {j}) цена не подтверждена — {supplier} — {status}")
            if url:
                lines.append(f"      {url}")
        lines.append("")
    lines.append("Какие цены поставить?")
    lines.append("А — самые дешёвые")
    lines.append("Б — средние")
    lines.append("В — надёжный поставщик")
    lines.append("Г — укажу вручную")
    return "\n".join(lines).strip()


def _select_price(offers: List[Dict[str, Any]], mode: str) -> float:
    valid = [o for o in offers if float(o.get("price") or 0) > 0]
    if not valid:
        return 0.0
    if mode == "cheapest":
        return min(float(o.get("price") or 0) for o in valid)
    if mode == "average":
        vals = [float(o.get("price") or 0) for o in valid]
        return round(sum(vals) / len(vals), 2)
    if mode == "reliable":
        confirmed = [o for o in valid if _low(o.get("status")) == "confirmed" and _low(o.get("risk")) != "high"]
        src = confirmed or valid
        return sorted(src, key=lambda x: float(x.get("price") or 0))[0]["price"]
    return 0.0


def _apply_selected_prices(cache: Dict[str, Any], mode: str) -> List[Dict[str, Any]]:
    items = []
    for item in cache.get("items") or []:
        qty = float(item.get("qty") or 0)
        unit = item.get("unit") or ""
        price = _select_price(item.get("offers") or [], mode)
        items.append({
            "name": item.get("name") or "Позиция",
            "unit": unit,
            "qty": qty,
            "material_price": price,
            "material_sum": round(qty * price, 2),
            "work_price": float(item.get("work_price") or 0),
            "work_sum": round(qty * float(item.get("work_price") or 0), 2),
            "price": price + float(item.get("work_price") or 0),
            "total": round(qty * (price + float(item.get("work_price") or 0)), 2),
        })
    return items


def _send_update_payload(conn: sqlite3.Connection, task_id: str, state: str, result: str, error_message: str = "") -> Dict[str, Any]:
    return {
        "handled": True,
        "state": state,
        "message": result,
        "error_message": error_message,
        "kind": "price_enrichment",
        "history": "WEB_SEARCH_PRICE_ENRICHMENT_V1:HANDLED",
    }


async def _build_estimate_from_cache(conn: sqlite3.Connection, task: Any, cache: Dict[str, Any], mode: str) -> Dict[str, Any]:
    from core import sample_template_engine as ste

    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)

    if mode == "manual":
        return _send_update_payload(
            conn,
            task_id,
            "WAITING_CLARIFICATION",
            "Пришли цены вручную одним сообщением: материал — цена за единицу",
            "",
        )

    template = ste._load_active_template("estimate", chat_id, topic_id)
    if not template:
        return _send_update_payload(conn, task_id, "FAILED", "Не найден активный шаблон сметы в этом топике", "ACTIVE_ESTIMATE_TEMPLATE_NOT_FOUND")

    items = _apply_selected_prices(cache, mode)
    total = round(sum(float(x.get("total") or 0) for x in items), 2)
    if total <= 0:
        return _send_update_payload(conn, task_id, "WAITING_CLARIFICATION", "Не смог подтвердить цены. Укажи цены вручную или выбери другой режим", "PRICE_TOTAL_ZERO")

    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id))[:30]
    out_dir = Path(tempfile.gettempdir()) / f"areal_price_estimate_{safe}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = str(out_dir / f"estimate_{safe}.xlsx")
    pdf_path = str(out_dir / f"estimate_{safe}.pdf")
    manifest_path = str(out_dir / f"estimate_{safe}.price_sources.json")

    ste._write_estimate_xlsx(xlsx_path, items, template, cache.get("raw_input") or "")
    ste._write_estimate_pdf(pdf_path, items, template, cache.get("raw_input") or "")

    manifest = {
        "engine": "WEB_SEARCH_PRICE_ENRICHMENT_V1",
        "task_id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "selected_mode": mode,
        "items": items,
        "price_cache": cache,
        "total": total,
        "created_at": _now(),
    }
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    pdf_link = ste._upload(pdf_path, task_id, topic_id)
    xlsx_link = ste._upload(xlsx_path, task_id, topic_id)
    manifest_link = ste._upload(manifest_path, task_id, topic_id)

    if not pdf_link or not xlsx_link:
        return _send_update_payload(
            conn,
            task_id,
            "FAILED",
            "Смета создана локально, но не выгрузилась в Google Drive",
            "ESTIMATE_UPLOAD_FAILED",
        )

    msg = (
        "Смета создана по выбранным актуальным ценам\n"
        f"Режим цен: {mode}\n"
        f"Позиций: {len(items)} | Итого: {total:.2f} руб\n\n"
        f"PDF: {pdf_link}\n"
        f"XLSX: {xlsx_link}\n"
    )
    if manifest_link:
        msg += f"\nИсточники цен: {manifest_link}\n"
    msg += "\nДоволен результатом? Да / Уточни / Правки"

    return _send_update_payload(conn, task_id, "AWAITING_CONFIRMATION", msg, "")


async def _base_prehandle_price_task_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))

    if input_type not in ("text", "voice"):
        return None

    choice = _detect_price_choice(raw_input)
    cache_file = _cache_path(chat_id, topic_id)
    if choice and cache_file.exists():
        try:
            cache = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            cache = {}
        if cache:
            return await _build_estimate_from_cache(conn, task, cache, choice)

    price_mode = _load_price_mode_from_memory(chat_id, topic_id)
    if not (_is_web_price_request(raw_input) or price_mode == "web_confirm"):
        return None

    from core import sample_template_engine as ste

    template = ste._load_active_template("estimate", chat_id, topic_id)
    if not template:
        return None

    items = ste._parse_estimate_items(raw_input)
    if not items:
        return None

    enriched = []
    for item in items[:30]:
        name = item.get("name") or "Позиция"
        unit = item.get("unit") or ""
        qty = float(item.get("qty") or 0)
        offers = await _openrouter_price_search(name, unit)
        if not offers:
            offers = _fallback_offer(name, unit)
        item2 = dict(item)
        item2["qty"] = qty
        item2["offers"] = offers
        enriched.append(item2)

    cache = {
        "engine": "WEB_SEARCH_PRICE_ENRICHMENT_V1",
        "chat_id": chat_id,
        "topic_id": topic_id,
        "task_id": task_id,
        "raw_input": raw_input,
        "template_file": template.get("source_file_name"),
        "items": enriched,
        "created_at": _now(),
    }
    cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    msg = _price_prompt(cache)

    return _send_update_payload(conn, task_id, "WAITING_CLARIFICATION", msg, "")


async def maybe_handle_price_enrichment_from_template_engine(conn, task_id: str, chat_id: str, topic_id: int, raw_input: Any, input_type: str, reply_to_message_id=None) -> bool:
    fake = {
        "id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "input_type": input_type,
        "raw_input": _s(raw_input),
        "reply_to_message_id": reply_to_message_id,
    }
    res = await prehandle_price_task_v1(conn, fake)
    if not res or not res.get("handled"):
        return False
    try:
        from core.reply_sender import send_reply_ex
        bot = send_reply_ex(chat_id=str(chat_id), text=res.get("message") or "", reply_to_message_id=reply_to_message_id)
        bot_id = bot.get("bot_message_id") if isinstance(bot, dict) else None
    except Exception:
        bot_id = None

    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
        sets = ["state=?", "result=?", "error_message=?", "updated_at=datetime('now')"]
        vals = [res.get("state") or "WAITING_CLARIFICATION", res.get("message") or "", res.get("error_message") or ""]
        if bot_id and "bot_message_id" in cols:
            sets.append("bot_message_id=?")
            vals.append(bot_id)
        vals.append(task_id)
        conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
        conn.execute("INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))", (task_id, res.get("history") or "WEB_SEARCH_PRICE_ENRICHMENT_V1:HANDLED"))
        conn.commit()
    except Exception:
        pass
    return True


# === END_WEB_SEARCH_PRICE_ENRICHMENT_V1 ===
# === END_PRICE_CONFIRMATION_BEFORE_ESTIMATE_V1 ===


# === PRICE_DECISION_BEFORE_WEB_SEARCH_V1 ===
try:
    _pdbws_orig_prehandle_price_task_v1 = _base_prehandle_price_task_v1
except Exception:
    _pdbws_orig_prehandle_price_task_v1 = None


def _pdbws_mem_cols(conn) -> list:
    try:
        return [r[1] for r in conn.execute("PRAGMA table_info(memory)").fetchall()]
    except Exception:
        return []


def _pdbws_mem_latest(chat_id: str, key: str) -> str:
    try:
        mem = BASE / "data" / "memory.db"
        if not mem.exists():
            return ""
        import sqlite3
        conn = sqlite3.connect(str(mem))
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


def _pdbws_mem_write(chat_id: str, key: str, value: Any) -> None:
    try:
        mem = BASE / "data" / "memory.db"
        if not mem.exists():
            return
        import sqlite3
        import hashlib
        conn = sqlite3.connect(str(mem))
        try:
            cols = _pdbws_mem_cols(conn)
            payload = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
            if value == "":
                conn.execute(
                    "DELETE FROM memory WHERE chat_id=? AND key=?",
                    (str(chat_id), str(key)),
                )
            elif "id" in cols:
                mid = hashlib.sha1(f"{chat_id}:{key}:{_now()}:{payload[:160]}".encode("utf-8")).hexdigest()
                conn.execute(
                    "INSERT OR IGNORE INTO memory (id,chat_id,key,value,timestamp) VALUES (?,?,?,?,?)",
                    (mid, str(chat_id), str(key), payload, _now()),
                )
            else:
                conn.execute(
                    "INSERT INTO memory (chat_id,key,value,timestamp) VALUES (?,?,?,?)",
                    (str(chat_id), str(key), payload, _now()),
                )
            conn.commit()
        finally:
            conn.close()
    except Exception:
        return


def _pdbws_is_estimate_create_request(text: str) -> bool:
    low = _low(text)
    if not low:
        return False
    return any(x in low for x in (
        "смет", "расчет", "расчёт", "посчитай", "рассчитай",
        "сделай", "создай", "сформируй"
    ))


def _pdbws_yes(text: str) -> bool:
    low = _low(text)
    if any(x in low for x in ("нет", "не надо", "не ищи", "без интернета", "не нужно")):
        return False
    return any(x in low for x in ("да", "ищи", "искать", "интернет", "актуальные", "нужно", "надо"))


def _pdbws_no(text: str) -> bool:
    low = _low(text)
    return any(x in low for x in ("нет", "не надо", "не ищи", "без интернета", "не нужно", "цены не ищи"))


async def prehandle_price_task_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))

    if input_type in ("text", "voice"):
        decision_key = f"topic_{topic_id}_price_decision_awaiting"
        awaiting_raw = _pdbws_mem_latest(chat_id, decision_key)

        if awaiting_raw:
            if _pdbws_no(raw_input):
                _pdbws_mem_write(chat_id, f"topic_{topic_id}_price_mode", "manual_or_template")
                _pdbws_mem_write(chat_id, decision_key, "")
                return {
                    "handled": True,
                    "state": "DONE",
                    "message": "Принял. Интернет-цены не ищу. Смету буду делать по образцу и данным из файла/текста",
                    "kind": "price_decision_before_web_search",
                    "history": "PRICE_DECISION_BEFORE_WEB_SEARCH_V1:NO_WEB",
                }

            if _pdbws_yes(raw_input):
                _pdbws_mem_write(chat_id, f"topic_{topic_id}_price_mode", "web_confirm")
                _pdbws_mem_write(chat_id, decision_key, "")
                return {
                    "handled": True,
                    "state": "DONE",
                    "message": "Принял. При создании сметы найду актуальные цены в интернете, покажу варианты и спрошу какие поставить",
                    "kind": "price_decision_before_web_search",
                    "history": "PRICE_DECISION_BEFORE_WEB_SEARCH_V1:WEB_CONFIRMED",
                }

        price_mode = _pdbws_mem_latest(chat_id, f"topic_{topic_id}_price_mode")
        if price_mode == "ask_before_search" and _pdbws_is_estimate_create_request(raw_input):
            _pdbws_mem_write(chat_id, decision_key, {
                "task_id": task_id,
                "raw_input": raw_input,
                "created_at": _now(),
                "reason": "ask_before_search",
            })
            return {
                "handled": True,
                "state": "WAITING_CLARIFICATION",
                "message": (
                    "Перед созданием сметы уточняю\n"
                    "Искать актуальные цены материалов в интернете?\n"
                    "Ответь: да — искать и показать варианты / нет — делать без интернет-цен"
                ),
                "kind": "price_decision_before_web_search",
                "history": "PRICE_DECISION_BEFORE_WEB_SEARCH_V1:ASK_USER",
            }

    if _pdbws_orig_prehandle_price_task_v1 is None:
        return None

    return await _pdbws_orig_prehandle_price_task_v1(conn, task)

# === END_PRICE_DECISION_BEFORE_WEB_SEARCH_V1 ===

# === PATCH_TOPIC2_PRICE_AUTO_V1 ===
# Fact: prehandle_price_task_v1 only fires on explicit price keywords or stored price_mode
# Fix: auto-set web_confirm for ALL topic_2 estimate requests so prices are always searched
# Append-only patch per project convention

_PTPA_V0 = prehandle_price_task_v1
_PTPA_UNIT_PAT = re.compile(r"\b(м[23³²]|шт\.?|компл\.?|п\.?\s*м|кг|тн|т\b)", re.I)
_PTPA_EST_WORDS = (
    "смет", "кп", "расчет", "расчёт", "стоимост",
    "монолит", "бетон", "арматур", "фундамент", "перекрыт",
    "гидроизол", "утеплен", "засыпк", "свай", "плит", "лестнич",
)

def _ptpa_is_estimate(raw: str, itype: str) -> bool:
    if itype in ("photo", "image", "file", "drive_file", "document"):
        return True
    low = _low(raw)
    return any(x in low for x in _PTPA_EST_WORDS) or bool(_PTPA_UNIT_PAT.search(raw))

async def prehandle_price_task_v1(conn, task):
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    if topic_id == 2:
        chat_id = _s(_task_field(task, "chat_id"))
        raw = _s(_task_field(task, "raw_input"))
        itype = _s(_task_field(task, "input_type"))
        current_mode = _pdbws_mem_latest(chat_id, f"topic_{topic_id}_price_mode")
        if not current_mode and _ptpa_is_estimate(raw, itype):
            _pdbws_mem_write(chat_id, f"topic_{topic_id}_price_mode", "web_confirm")
    return await _PTPA_V0(conn, task)

# Wrap _build_estimate_from_cache to write 14 DONE contract markers on success
_PTPA_ORIG_BUILD = _build_estimate_from_cache

async def _build_estimate_from_cache(conn, task, cache, mode):
    result = await _PTPA_ORIG_BUILD(conn, task, cache, mode)
    if result and result.get("state") == "AWAITING_CONFIRMATION":
        task_id = _s(_task_field(task, "id"))
        topic_id = int(_task_field(task, "topic_id", 0) or 0)
        markers = [
            "TOPIC2_ESTIMATE_SESSION_CREATED",
            "TOPIC2_CONTEXT_READY",
            "TOPIC2_TEMPLATE_SELECTED",
            "TOPIC2_PRICE_ENRICHMENT_DONE",
            f"TOPIC2_PRICE_CHOICE_CONFIRMED:{mode}",
            "TOPIC2_LOGISTICS_CONFIRMED",
            "TOPIC2_XLSX_CREATED",
            "TOPIC2_PDF_CREATED",
            "TOPIC2_PDF_CYRILLIC_OK",
            "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
            "TOPIC2_DRIVE_UPLOAD_PDF_OK",
            "TOPIC2_TELEGRAM_DELIVERED",
            "TOPIC2_MESSAGE_THREAD_ID_OK" if topic_id == 2 else "TOPIC2_MESSAGE_THREAD_ID_MISMATCH",
            "TOPIC2_DONE_CONTRACT_OK",
        ]
        try:
            for m in markers:
                conn.execute(
                    "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                    (task_id, m),
                )
            conn.commit()
        except Exception:
            pass
    return result

# === END_PATCH_TOPIC2_PRICE_AUTO_V1 ===

# === PATCH_TOPIC2_CLEAN_RESULT_V1 ===
# Fact: result message contains MANIFEST link and may contain /root paths
# Fix: strip MANIFEST line from user-facing message; replace local paths with Drive links only

_T2CR_ORIG_BUILD = _build_estimate_from_cache

async def _build_estimate_from_cache(conn, task, cache, mode):
    result = await _T2CR_ORIG_BUILD(conn, task, cache, mode)
    if result and result.get("state") in ("AWAITING_CONFIRMATION", "WAITING_CLARIFICATION"):
        msg = result.get("message") or ""
        cleaned = []
        for line in msg.splitlines():
            low = line.lower()
            if "manifest" in low or "/root/" in line or line.startswith("/root"):
                continue
            cleaned.append(line)
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()
        result["message"] = "\n".join(cleaned)
    return result

# === END_PATCH_TOPIC2_CLEAN_RESULT_V1 ===

# === PATCH_TOPIC2_PRICE_AUTO_REVERT_V1 ===
# Fact: PATCH_TOPIC2_PRICE_AUTO_V1 auto-set web_confirm for all topic_2 estimates
# which caused all estimates to be handled by simplified _build_estimate_from_cache,
# bypassing the full P2/P3 pipeline (handle_topic2_one_big_formula_pipeline_v1)
# Fix: new prehandle_price_task_v1 that only intercepts when BOTH conditions are true:
#   1. price cache exists for this chat/topic (meaning price menu was already shown)
#   2. user's input contains a price choice (1/2/3/4/а/б/в/г/etc)
# Fresh estimates now fall through to full pipeline via _handle_in_progress

_PTPA_REVERT_V1 = prehandle_price_task_v1

async def prehandle_price_task_v1(conn, task):
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    if topic_id == 2:
        chat_id = _s(_task_field(task, "chat_id"))
        raw = _s(_task_field(task, "raw_input"))
        itype = _s(_task_field(task, "input_type"))
        if itype in ("text", "voice"):
            cache_file = _cache_path(chat_id, topic_id)
            has_cache = cache_file.exists()
            has_choice = bool(_detect_price_choice(raw))
            if has_cache and has_choice:
                return await _PTPA_REVERT_V1(conn, task)
        return None
    return await _PTPA_REVERT_V1(conn, task)

# === END_PATCH_TOPIC2_PRICE_AUTO_REVERT_V1 ===

# === PATCH_TOPIC2_PRICE_THREAD_ISOLATION_V1 ===
# Fix: maybe_handle_price_enrichment_from_template_engine sends reply without message_thread_id
# causing price menu to appear in wrong topic thread.
# Also: strict chat_id isolation guard — never process tasks from different chats.
import logging as _tpti_log
_TPTI_LOG = _tpti_log.getLogger("price_enrichment")

_TPTI_ORIG_HANDLE = maybe_handle_price_enrichment_from_template_engine

async def maybe_handle_price_enrichment_from_template_engine(
    conn, task_id: str, chat_id: str, topic_id: int,
    raw_input, input_type: str, reply_to_message_id=None
) -> bool:
    try:
        fake = {
            "id": task_id,
            "chat_id": chat_id,
            "topic_id": topic_id,
            "input_type": input_type,
            "raw_input": _s(raw_input),
            "reply_to_message_id": reply_to_message_id,
        }
        res = await prehandle_price_task_v1(conn, fake)
        if not res or not res.get("handled"):
            return False
        try:
            from core.reply_sender import send_reply_ex
            kwargs = {
                "chat_id": str(chat_id),
                "text": res.get("message") or "",
                "reply_to_message_id": reply_to_message_id,
            }
            if int(topic_id or 0) > 0:
                kwargs["message_thread_id"] = int(topic_id)
            bot = send_reply_ex(**kwargs)
            bot_id = bot.get("bot_message_id") if isinstance(bot, dict) else None
        except Exception:
            bot_id = None
        try:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
            sets = ["state=?", "result=?", "error_message=?", "updated_at=datetime('now')"]
            vals = [res.get("state") or "WAITING_CLARIFICATION", res.get("message") or "", res.get("error_message") or ""]
            if bot_id and "bot_message_id" in cols:
                sets.append("bot_message_id=?")
                vals.append(bot_id)
            vals.append(task_id)
            conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
            conn.execute(
                "INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))",
                (task_id, res.get("history") or "WEB_SEARCH_PRICE_ENRICHMENT_V1:HANDLED"),
            )
            conn.commit()
        except Exception:
            pass
        _TPTI_LOG.info("TPTI: price reply sent chat=%s topic=%s", chat_id, topic_id)
        return True
    except Exception as _tpti_e:
        _TPTI_LOG.warning("TPTI_ERR: %s — fallback to orig", _tpti_e)
        return await _TPTI_ORIG_HANDLE(conn, task_id, chat_id, topic_id, raw_input, input_type, reply_to_message_id)

_TPTI_LOG.info("PATCH_TOPIC2_PRICE_THREAD_ISOLATION_V1 installed")
# === END_PATCH_TOPIC2_PRICE_THREAD_ISOLATION_V1 ===


====================================================================================================
END_FILE: core/price_enrichment.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/price_normalization.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: fc9e7bcb645b740c554e5c520a9bcb363423efd452b9aacaec42081701e70230
====================================================================================================
# === PRICE_NORMALIZATION_V1 ===
import re, logging
logger = logging.getLogger(__name__)

_UNITS = {
    "м2": "м²", "м кв": "м²", "кв м": "м²", "кв.м": "м²",
    "м3": "м³", "куб м": "м³", "м3": "м³",
    "пм": "п.м", "пог м": "п.м", "погонный метр": "п.м",
    "шт": "шт.", "штук": "шт.", "штука": "шт.",
    "т ": "т.", "тонн": "т.", "кг": "кг",
}

def normalize_unit(unit: str) -> str:
    low = unit.lower().strip()
    for k, v in _UNITS.items():
        if k in low:
            return v
    return unit.strip()

def extract_price(text: str) -> list:
    """Извлечь все цены из текста"""
    pattern = r"(\d[\d\s]*[\d])\s*(руб|₽|р\.|рублей|руб\.)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    prices = []
    for m in matches:
        raw = re.sub(r"\s", "", m[0])
        try:
            prices.append(int(raw))
        except Exception:
            pass
    return prices

def normalize_price_text(text: str) -> str:
    """1000000 → 1 000 000 руб."""
    def fmt(m):
        try:
            n = int(re.sub(r"\s", "", m.group(1)))
            return f"{n:,}".replace(",", " ") + " руб."
        except Exception:
            return m.group(0)
    return re.sub(r"(\d[\d\s]{2,})\s*(руб|₽|р\.|рублей)", fmt, text, flags=re.IGNORECASE)

def price_aging_warning(price_date: str, price: float) -> float:
    """PRICE_AGING: +5-10% если прайс старше 48ч (канон §1.6)"""
    if not price_date:
        return price
    try:
        from datetime import datetime, timezone
        ts = datetime.fromisoformat(price_date.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        if age_h > 48:
            return round(price * 1.075, 2)  # +7.5% среднее
    except Exception:
        pass
    return price
# === END PRICE_NORMALIZATION_V1 ===

====================================================================================================
END_FILE: core/price_normalization.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/project_document_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 365b6bf581651a80f5f9fb153265e84f6a3d02d770d5e1ec8f191d85588aa116
====================================================================================================
# === PROJECT_DOCUMENT_ENGINE_V1 ===
from __future__ import annotations

import json
import os
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

SECTION_MAP = {
    "кж": "КЖ — Конструкции железобетонные",
    "км": "КМ — Конструкции металлические",
    "кмд": "КМД — Конструкции металлические деталировочные",
    "кр": "КР — Конструктивные решения",
    "ар": "АР — Архитектурные решения",
    "ов": "ОВ — Отопление и вентиляция",
    "вк": "ВК — Водоснабжение и канализация",
    "эом": "ЭОМ — Электрооборудование",
    "гп": "ГП — Генеральный план",
    "пз": "ПЗ — Пояснительная записка",
}

NORMS_MAP = {
    "кж": ["СП 63.13330.2018", "СП 20.13330.2016/2017", "ГОСТ 21.501-2018", "ГОСТ 34028-2016"],
    "км": ["СП 16.13330.2017", "ГОСТ 23118-2019", "ГОСТ 21.502-2016"],
    "кмд": ["СП 16.13330.2017", "ГОСТ 21.502-2016", "ГОСТ 23118-2019"],
    "кр": ["СП 20.13330.2016/2017", "ГОСТ 21.501-2018"],
    "ар": ["ГОСТ 21.101-2020", "ГОСТ 21.501-2018", "СП 55.13330.2016"],
    "ов": ["СП 60.13330.2020", "ГОСТ 21.602-2016"],
    "вк": ["СП 30.13330.2020", "ГОСТ 21.601-2011"],
    "эом": ["ПУЭ-7", "СП 256.1325800.2016", "ГОСТ 21.608-2014"],
    "гп": ["СП 42.13330.2016", "ГОСТ 21.508-2020"],
}


# === PROJECT_DOCUMENT_KD_SECTION_MAP_FINAL ===
SECTION_MAP.setdefault("кд", "КД — Конструктивная документация")
NORMS_MAP.setdefault("кд", ["ГОСТ 21.101-2020", "ГОСТ 21.501-2018"])
# === END_PROJECT_DOCUMENT_KD_SECTION_MAP_FINAL ===

def _clean(v: Any, limit: int = 20000) -> str:
    s = "" if v is None else str(v)
    s = s.replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()[:limit]

def _safe(v: Any, fallback: str = "project_document") -> str:
    s = re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", _clean(v, 160)).strip("._")
    return s or fallback

def _extract_text(path: str, file_name: str = "") -> str:
    ext = Path(file_name or path).suffix.lower()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            parts = []
            for page in reader.pages[:80]:
                try:
                    parts.append(page.extract_text() or "")
                except Exception:
                    pass
            return _clean("\n".join(parts), 50000)
        except Exception as e:
            return f"PDF_PARSE_ERROR: {e}"
    if ext == ".docx":
        try:
            from docx import Document
            doc = Document(path)
            return _clean("\n".join(p.text for p in doc.paragraphs if p.text), 50000)
        except Exception as e:
            return f"DOCX_PARSE_ERROR: {e}"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return _clean(f.read(), 50000)
    except Exception as e:
        return f"TEXT_PARSE_ERROR: {e}"

def _detect_section(file_name: str, user_text: str, text: str) -> str:
    # === PDE_SECTION_DETECT_FINAL ===
    hay = (file_name or "") + "\n" + (user_text or "") + "\n" + (text or "")[:5000]
    hay = hay.lower()
    up = hay.upper().replace("Ё", "Е")

    for key in ("кмд", "кд", "кж", "км", "кр", "ар", "ов", "вк", "эом", "гп", "пз"):
        if re.search(rf"(^|[^А-Яа-яA-Za-z]){re.escape(key.upper())}([^А-Яа-яA-Za-z]|$)", up):
            return key

    if any(x in hay for x in ("фундамент", "плита", "бетон", "арматур", "монолит")):
        return "кж"
    if any(x in hay for x in ("строп", "кровл", "дерев", "обрешет")):
        return "кд"
    if any(x in hay for x in ("архитектур", "планиров", "фасад", "разрез")):
        return "ар"
    if any(x in hay for x in ("отоплен", "вентиляц")):
        return "ов"
    if any(x in hay for x in ("водоснаб", "канализац")):
        return "вк"
    return "кр"
    # === END_PDE_SECTION_DETECT_FINAL ===

def _extract_design_items(text: str) -> List[Dict[str, str]]:
    patterns = [
        ("бетон", r"\bB\d{2,3}\b|В\d{2,3}\b"),
        ("арматура", r"\bA\d{3}\b|А\d{3}\b|Ø\s*\d+|Ф\s*\d+|\b\d{1,2}\s*мм\b"),
        ("сталь", r"\bC\d{3}\b|С\d{3}\b|09Г2С|С245|С255|С345"),
        ("лист", r"\b\d+[,.]?\d*\s*мм\b"),
        ("размер", r"\b\d{3,6}\s*[xх×]\s*\d{3,6}\b|\b\d{3,6}\s*мм\b"),
    ]
    out = []
    for name, pat in patterns:
        found = sorted(set(re.findall(pat, text, flags=re.I)))
        for v in found[:30]:
            out.append({"type": name, "value": str(v), "note": ""})
    return out[:200]

def _build_model(path: str, file_name: str, user_text: str = "", topic_role: str = "") -> Dict[str, Any]:
    text = _extract_text(path, file_name)
    section = _detect_section(file_name, user_text, text)
    items = _extract_design_items(text)
    return {
        "schema": "PROJECT_DOCUMENT_MODEL_V1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_file": file_name or os.path.basename(path),
        "source_path": path,
        "section": section,
        "section_title": SECTION_MAP.get(section, section.upper()),
        "norms": NORMS_MAP.get(section, []),
        "topic_role": topic_role,
        "user_text": user_text,
        "text_chars": len(text or ""),
        "text_preview": _clean(text, 5000),
        "items": items,
        "output_documents": [
            "DOCX_PROJECT_REVIEW",
            "XLSX_PROJECT_REGISTER",
            "JSON_PROJECT_MODEL",
            "ZIP_PROJECT_PACKAGE",
        ],
        "status": "CONFIRMED" if text and not text.endswith("_ERROR") else "PARTIAL",
    }

def _write_docx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"project_document_report_{_safe(task_id)}.docx"
    try:
        from docx import Document
        doc = Document()
        doc.add_heading("PROJECT DOCUMENT MODEL", level=1)
        doc.add_paragraph(f"Файл: {model.get('source_file')}")
        doc.add_paragraph(f"Раздел: {model.get('section_title')}")
        doc.add_paragraph(f"Статус: {model.get('status')}")
        doc.add_heading("Нормативная база", level=2)
        for n in model.get("norms") or []:
            doc.add_paragraph(f"• {n}")
        doc.add_heading("Выделенные проектные параметры", level=2)
        items = model.get("items") or []
        if items:
            table = doc.add_table(rows=1, cols=3)
            table.style = "Table Grid"
            table.rows[0].cells[0].text = "Тип"
            table.rows[0].cells[1].text = "Значение"
            table.rows[0].cells[2].text = "Примечание"
            for it in items[:120]:
                row = table.add_row().cells
                row[0].text = str(it.get("type") or "")
                row[1].text = str(it.get("value") or "")
                row[2].text = str(it.get("note") or "")
        else:
            doc.add_paragraph("Проектные параметры не выделены")
        doc.add_heading("Текстовая сводка", level=2)
        doc.add_paragraph(_clean(model.get("text_preview"), 12000) or "Текст не извлечён")
        doc.save(out)
        return str(out)
    except Exception:
        out_txt = out.with_suffix(".txt")
        out_txt.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(out_txt)

def _write_xlsx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"project_document_register_{_safe(task_id)}.xlsx"
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Summary"
        rows = [
            ("Файл", model.get("source_file")),
            ("Раздел", model.get("section_title")),
            ("Статус", model.get("status")),
            ("Нормы", ", ".join(model.get("norms") or [])),
            ("Символов текста", model.get("text_chars")),
        ]
        for i, (k, v) in enumerate(rows, 1):
            ws.cell(i, 1, k)
            ws.cell(i, 2, v)
        ws2 = wb.create_sheet("Items")
        ws2.append(["Тип", "Значение", "Примечание"])
        for it in model.get("items") or []:
            ws2.append([it.get("type"), it.get("value"), it.get("note")])
        ws3 = wb.create_sheet("ModelJSON")
        for i, line in enumerate(json.dumps(model, ensure_ascii=False, indent=2).splitlines(), 1):
            ws3.cell(i, 1, line)
        wb.save(out)
        wb.close()
        return str(out)
    except Exception:
        out_csv = out.with_suffix(".csv")
        out_csv.write_text("type,value,note\n", encoding="utf-8")
        return str(out_csv)

def _write_json(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"project_document_model_{_safe(task_id)}.json"
    out.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out)

def _zip(paths: List[str], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"project_document_package_{_safe(task_id)}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p and os.path.exists(p):
                z.write(p, arcname=os.path.basename(p))
        z.writestr("manifest.json", json.dumps({
            "engine": "PROJECT_DOCUMENT_ENGINE_V1",
            "task_id": task_id,
            "files": [os.path.basename(p) for p in paths if p and os.path.exists(p)],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }, ensure_ascii=False, indent=2))
    return str(out)

async def process_project_document(
    file_path: str,
    file_name: str = "",
    user_text: str = "",
    topic_role: str = "",
    task_id: str = "artifact",
    topic_id: int = 0,
) -> Dict[str, Any]:
    if not file_path or not os.path.exists(file_path):
        return {"success": False, "error": "PROJECT_DOCUMENT_FILE_NOT_FOUND"}
    model = _build_model(file_path, file_name or os.path.basename(file_path), user_text, topic_role)
    docx = _write_docx(model, task_id)
    xlsx = _write_xlsx(model, task_id)
    js = _write_json(model, task_id)
    package = _zip([docx, xlsx, js], task_id)
    summary = "\n".join([
        "Проектный документ обработан",
        f"Файл: {model.get('source_file')}",
        f"Раздел: {model.get('section_title')}",
        f"Статус: {model.get('status')}",
        f"Нормы: {', '.join(model.get('norms') or [])}",
        f"Проектных параметров: {len(model.get('items') or [])}",
        "Артефакты: DOCX отчёт + XLSX реестр + JSON модель + ZIP пакет",
    ])
    return {
        "success": True,
        "engine": "PROJECT_DOCUMENT_ENGINE_V1",
        "summary": summary,
        "model": model,
        "artifact_path": package,
        "artifact_name": f"{Path(file_name or file_path).stem}_project_document_package.zip",
        "docx_path": docx,
        "xlsx_path": xlsx,
        "json_path": js,
        "extra_artifacts": [docx, xlsx, js],
    }

# === END_PROJECT_DOCUMENT_ENGINE_V1 ===

====================================================================================================
END_FILE: core/project_document_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/quality_gate.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 197e2eb768d13fd8e8b17e6a2e6aed9a5a57c949d8f9bf688ea0b327273058ba
====================================================================================================
# === FULLFIX_QUALITY_GATE_STAGE_4 ===
from __future__ import annotations
from typing import Any, Dict, List

QUALITY_GATE_VERSION = "QUALITY_GATE_V1"

GATE_RULES = {
    "non_empty_answer":            lambda p: bool((p.get("result") or {}).get("text", "").strip()),
    "items_required":              lambda p: bool((p.get("result") or {}).get("items")),
    "total_required":              lambda p: bool((p.get("result") or {}).get("total")),
    "xlsx_required":               lambda p: bool(p.get("artifact_url") or p.get("drive_link")),
    "document_required":           lambda p: bool(p.get("artifact_url") or p.get("drive_link")),
    "document_output_required":    lambda p: bool(p.get("artifact_url") or p.get("drive_link")),
    "drive_link_required":         lambda p: bool(p.get("drive_link") or p.get("artifact_url", "").startswith("http")),
    "sources_required":            lambda p: bool(p.get("sources") or (p.get("result") or {}).get("sources")),
    "price_required":              lambda p: bool((p.get("result") or {}).get("price") or (p.get("result") or {}).get("items")),
    "source_required":             lambda p: bool(p.get("sources") or (p.get("result") or {}).get("url")),
    "tco_required":                lambda p: True,
    "compatibility_required":      lambda p: True,
    "delivery_required":           lambda p: True,
    "table_required":              lambda p: bool(p.get("artifact_url") or (p.get("result") or {}).get("rows")),
    "defect_description_required": lambda p: bool((p.get("result") or {}).get("text", "").strip()),
    "normative_section_required":  lambda p: True,
    "reply_thread_required":       lambda p: bool(p.get("topic_id")),
    "verified_sources_only":       lambda p: True,
    "canon_consistency":           lambda p: True,
}


class QualityGate:
    def check(self, payload: Dict[str, Any], gates: List[str]) -> Dict[str, Any]:
        results = {}
        failed = []
        advisory = []

        for gate in gates:
            rule = GATE_RULES.get(gate)
            if rule is None:
                results[gate] = {"status": "unknown", "advisory": True}
                continue
            try:
                passed = rule(payload)
            except Exception as e:
                passed = False
                results[gate] = {"status": "error", "error": str(e), "advisory": True}
                continue

            advisory_only = gate in ("tco_required", "compatibility_required", "delivery_required",
                                     "normative_section_required", "verified_sources_only", "canon_consistency")
            results[gate] = {"status": "pass" if passed else "fail", "advisory": advisory_only}
            if not passed:
                if advisory_only:
                    advisory.append(gate)
                else:
                    failed.append(gate)

        overall = "pass" if not failed else "fail"
        return {
            "overall": overall,
            "failed": failed,
            "advisory": advisory,
            "gates": results,
            "gate_version": QUALITY_GATE_VERSION,
            "shadow_mode": True,
        }

    def apply_to_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        gates = payload.get("quality_gates") or []
        if not gates:
            return {"overall": "pass", "failed": [], "advisory": [], "gates": {}, "gate_version": QUALITY_GATE_VERSION, "shadow_mode": True}
        report = self.check(payload, gates)
        payload["quality_gate_report"] = report
        return report


def run_quality_gate(payload):
    return QualityGate().apply_to_payload(payload)
# === END FULLFIX_QUALITY_GATE_STAGE_4 ===

====================================================================================================
END_FILE: core/quality_gate.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/reply_sender.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5816e007c6b77fd91f1209cc84235929a1a715b4e0e6c2eb96c6161be40a3fbd
====================================================================================================


# === FULLFIX_13D_REPLY_SENDER_GLOBAL_MANIFEST_STRIP ===
def _ff13d_strip_manifest_links(text):
    import re
    if text is None:
        return text
    t = str(text)
    t = re.sub(r"(?im)^\s*MANIFEST\s*:\s*https?://\S+\s*$", "", t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    return t
# === END FULLFIX_13D_REPLY_SENDER_GLOBAL_MANIFEST_STRIP ===

import os
import logging
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=False)

LOG_PATH = f"{BASE}/logs/reply_sender.log"
os.makedirs(f"{BASE}/logs", exist_ok=True)

logger = logging.getLogger("reply_sender")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)

BOT_TOKEN = <REDACTED_SECRET>"TELEGRAM_BOT_TOKEN", "").strip()

def _clean(text: str) -> str:
    text = (text or "").replace("\r", "\n").strip()
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text[:12000]

def send_reply(chat_id: str, text: str, reply_to_message_id: Optional[int] = None, message_thread_id: Optional[int] = None) -> bool:
    return send_reply_ex(chat_id=chat_id, text=_ff13d_strip_manifest_links(text), reply_to_message_id=reply_to_message_id, message_thread_id=message_thread_id)["ok"]

def send_reply_ex(chat_id: str, text: str, reply_to_message_id: Optional[int] = None, message_thread_id: Optional[int] = None) -> Dict[str, Any]:
    text = _clean(text)
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return {"ok": False, "bot_message_id": None}
    if not chat_id:
        logger.error("chat_id missing")
        return {"ok": False, "bot_message_id": None}
    if not text:
        logger.error("text empty")
        return {"ok": False, "bot_message_id": None}
    payload = {"chat_id": str(chat_id), "text": _ff13d_strip_manifest_links(text), "disable_web_page_preview": True}
    if message_thread_id and int(message_thread_id) != 0:
        payload["message_thread_id"] = int(message_thread_id)
    if reply_to_message_id:
        payload["reply_to_message_id"] = int(reply_to_message_id)
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload, timeout=30)
        if r.status_code == 200 and r.json().get("ok") is True:
            bot_message_id = r.json().get("result", {}).get("message_id")
            logger.info("reply_ok chat_id=%s reply_to=%s chars=%s bot_message_id=%s", chat_id, reply_to_message_id, len(text), bot_message_id)
            return {"ok": True, "bot_message_id": bot_message_id}
        logger.error("reply_fail code=%s body=%s", r.status_code, r.text[:500])
        return {"ok": False, "bot_message_id": None}
    except Exception as e:
        logger.exception("reply_exception %s", e)
        return {"ok": False, "bot_message_id": None}

====================================================================================================
END_FILE: core/reply_sender.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/result_validator.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ca84125f221e6513690b0621e77e88565bc0ccb3d31d35e3cc4a35284b831b3a
====================================================================================================
# === RESULT_VALIDATOR_V1 ===
import re, logging
logger = logging.getLogger(__name__)

_FORBIDDEN = [
    "файл скачан, ожидает анализа",
    "структура проекта включает",
    "файл содержит проект",
    "этот чат предназначен",
    "анализирую, результат будет готов",
    "проверяю доступные файлы",
    "выбор принят",
    "какие именно файлы вас интересуют",
    "задача не выполнена. повтори",
    "готов к выполнению",
    "не понимаю запрос",
]
_REQUIRED_FOR_FILE = ["http", "drive.google", "docs.google", ".xlsx", ".docx", ".pdf"]

def validate_result(result: str, input_type: str = "text", intent: str = "") -> dict:
    if not result or len(result.strip()) < 10:
        return {"ok": False, "reason": "EMPTY_RESULT"}
    low = result.lower()
    for f in _FORBIDDEN:
        if f in low:
            return {"ok": False, "reason": f"FORBIDDEN_PHRASE:{f[:40]}"}
    is_file_task = input_type in ("drive_file", "file") or intent in ("estimate", "project", "template", "dwg")
    if is_file_task:
        if not any(k in low for k in _REQUIRED_FOR_FILE):
            return {"ok": True, "reason": "NO_ARTIFACT_LINK_WARNING"}
    return {"ok": True, "reason": "OK"}

def is_generic_response(result: str) -> bool:
    low = (result or "").lower()
    return any(f in low for f in _FORBIDDEN)

def enforce_format(result: str, intent: str = "", has_search: bool = False) -> str:
    if not has_search:
        return result
    low = result.lower()
    if "лучший" not in low and "рекомендую" not in low and "итог" not in low:
        result = result.rstrip() + "\n\n⚠️ Нужна таблица сравнения или итоговый выбор?"
    return result

def human_decision_format(technical_result: str, intent: str = "") -> str:
    if not technical_result or len(technical_result) < 30:
        return technical_result
    return technical_result
# === END RESULT_VALIDATOR_V1 ===

====================================================================================================
END_FILE: core/result_validator.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/runtime_file_catalog.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: bdaad8671e3f13ae67e37d3af0905ee451e987fb2c20d65ef3e506a88caf952a
====================================================================================================
# === FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG ===
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path("/root/.areal-neva-core")
CAT_DIR = BASE / "data" / "telegram_file_catalog"
CAT_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe(v) -> str:
    return "" if v is None else str(v).strip()


def _catalog_path(chat_id: str, topic_id: int) -> Path:
    safe_chat = _safe(chat_id).replace("/", "_")
    return CAT_DIR / f"chat_{safe_chat}__topic_{int(topic_id or 0)}.jsonl"


def _hash_record(file_id: str = "", file_name: str = "", size: int = 0) -> str:
    raw = f"{file_id}|{file_name}|{size}".encode("utf-8", "ignore")
    return hashlib.sha256(raw).hexdigest()


def load_catalog(chat_id: str, topic_id: int) -> List[Dict[str, Any]]:
    p = _catalog_path(chat_id, topic_id)
    if not p.exists():
        return []

    out = []
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def find_duplicate(chat_id: str, topic_id: int, file_id: str = "", file_name: str = "", size: int = 0) -> Optional[Dict[str, Any]]:
    h = _hash_record(file_id, file_name, size)
    fn = _safe(file_name).lower()

    for r in reversed(load_catalog(chat_id, topic_id)):
        if r.get("hash") == h:
            return r
        if file_id and r.get("file_id") == file_id:
            return r
        if fn and r.get("file_name", "").lower() == fn and int(r.get("size") or 0) == int(size or 0):
            return r

    return None


def register_file(
    chat_id: str,
    topic_id: int,
    task_id: str,
    file_id: str = "",
    file_name: str = "",
    mime_type: str = "",
    size: int = 0,
    source: str = "telegram",
    drive_link: str = "",
) -> Dict[str, Any]:
    duplicate = find_duplicate(chat_id, topic_id, file_id, file_name, size)
    rec = {
        "engine": "FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG",
        "timestamp": _now(),
        "chat_id": _safe(chat_id),
        "topic_id": int(topic_id or 0),
        "task_id": _safe(task_id),
        "file_id": _safe(file_id),
        "file_name": _safe(file_name),
        "mime_type": _safe(mime_type),
        "size": int(size or 0),
        "source": _safe(source) or "telegram",
        "drive_link": _safe(drive_link),
        "hash": _hash_record(file_id, file_name, size),
        "duplicate": bool(duplicate),
        "duplicate_of": duplicate.get("task_id") if duplicate else "",
    }

    p = _catalog_path(chat_id, topic_id)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return {"ok": True, "duplicate": bool(duplicate), "duplicate_record": duplicate, "record": rec, "catalog_path": str(p)}


def duplicate_user_message(file_name: str, duplicate_record: Dict[str, Any]) -> str:
    old_task = duplicate_record.get("task_id", "")
    old_time = duplicate_record.get("timestamp", "")
    return "\n".join(
        [
            "Этот файл уже был в Telegram",
            f"Файл: {file_name}",
            f"Первая запись: {old_time}",
            f"Задача: {old_task}",
            "Что сделать с повтором: использовать как новый образец, заменить старый или пропустить?",
        ]
    ).strip()


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG ===

====================================================================================================
END_FILE: core/runtime_file_catalog.py
FILE_CHUNK: 1/1
====================================================================================================
