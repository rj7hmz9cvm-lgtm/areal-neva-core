# ORCHESTRA_FULL_CONTEXT_PART_011
generated_at_utc: 2026-05-03T09:17:45.729872+00:00
git_sha_before_commit: 6d24f1ed47e4dea5d37798cee290f261ef205620
part: 11/11


====================================================================================================
BEGIN_FILE: core/universal_file_handler.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 10f50019c01f6a903296f3616568273fe69b0910481c12cc1105b19fec8ee2a7
====================================================================================================
# === UNIVERSAL_FILE_HANDLER_V1 ===
import os, logging, tempfile, subprocess, csv, zipfile, json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# --- Magic bytes detection ---
_MAGIC = {
    b"%PDF": "pdf",
    b"PK\x03\x04": "xlsx_or_zip",
    b"\xd0\xcf\x11\xe0": "doc_or_xls",
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG": "png",
    b"GIF8": "gif",
    b"BM": "bmp",
    b"II\x2a\x00": "tiff",
    b"MM\x00\x2a": "tiff",
    b"RIFF": "webp_or_avi",
    b"ftyp": "mp4",
    b"ID3": "mp3",
    b"AC10": "dwg",
    b"AC12": "dwg",
    b"AC14": "dwg",
    b"AC15": "dwg",
    b"AC18": "dwg",
    b"AC21": "dwg",
    b"AC24": "dwg",
    b"AC27": "dwg",
    b"  0\r\nSECTION": "dxf",
}

EXT_MAP = {
    ".pdf": "pdf", ".docx": "docx", ".doc": "doc_old",
    ".xlsx": "xlsx", ".xls": "xls_old", ".csv": "csv",
    ".txt": "text", ".md": "text", ".json": "json", ".xml": "xml",
    ".jpg": "image", ".jpeg": "image", ".png": "image",
    ".heic": "image", ".webp": "image", ".bmp": "image", ".tiff": "image",
    ".dwg": "dwg", ".dxf": "dxf", ".dgn": "dgn",
    ".zip": "zip", ".rar": "rar", ".7z": "7z",
    ".mp4": "video", ".avi": "video", ".mov": "video",
    ".mp3": "audio", ".ogg": "audio", ".wav": "audio",
    ".odt": "odt", ".ods": "ods", ".rtf": "rtf",
}

def detect_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    try:
        with open(file_path, "rb") as f:
            header = f.read(16)
        for magic, ftype in _MAGIC.items():
            if header[:len(magic)] == magic:
                # PK magic = ZIP or XLSX — уточняем по расширению
                if ftype == "xlsx_or_zip":
                    return "xlsx" if ext in (".xlsx", ".xlsm", ".xltx") else "zip"
                # RIFF = webp or avi — уточняем по расширению
                if ftype == "webp_or_avi":
                    return "image" if ext == ".webp" else "video"
                return ftype
    except Exception:
        pass
    return EXT_MAP.get(ext, "unknown")


def extract_text_from_file(file_path: str, task_id: str = "", topic_id: int = 0) -> Dict[str, Any]:
    """
    Универсальный экстрактор текста/данных из любого файла.
    Маркер: UNIVERSAL_FILE_HANDLER_V1
    Возвращает: {"success": bool, "type": str, "text": str, "rows": list, "error": str}
    """
    result = {"success": False, "type": "unknown", "text": "", "rows": [], "error": ""}
    ftype = detect_type(file_path)
    result["type"] = ftype
    logger.info("UNIVERSAL_FILE_HANDLER type=%s file=%s", ftype, os.path.basename(file_path))

    try:
        # --- PDF ---
        if ftype == "pdf":
            import pdfplumber, re
            with pdfplumber.open(file_path) as pdf:
                parts = []
                rows = []
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    t = re.sub(r'\(cid:\d+\)', '', t)
                    if t.strip():
                        parts.append(t)
                    for tbl in (page.extract_tables() or []):
                        rows.extend(tbl)
                result["text"] = "\n".join(parts)
                result["rows"] = rows
                result["success"] = True

        # --- DOCX / ODT ---
        elif ftype in ("docx", "odt"):
            import docx as _docx
            doc = _docx.Document(file_path)
            result["text"] = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            result["rows"] = [[c.text for c in row.cells] for tbl in doc.tables for row in tbl.rows]
            result["success"] = True

        # --- XLSX / ODS ---
        elif ftype in ("xlsx_or_zip", "xlsx"):
            from openpyxl import load_workbook
            wb = load_workbook(file_path, data_only=True)
            rows = []
            for ws in wb.worksheets:
                for row in ws.iter_rows(values_only=True):
                    if any(c is not None for c in row):
                        rows.append([str(c) if c is not None else "" for c in row])
            result["rows"] = rows
            result["text"] = "\n".join("\t".join(r) for r in rows[:50])
            result["success"] = True

        # --- CSV ---
        elif ftype == "csv":
            rows = []
            enc = "utf-8"
            try:
                import chardet
                with open(file_path, "rb") as f:
                    enc = chardet.detect(f.read(4096)).get("encoding", "utf-8") or "utf-8"
            except Exception:
                pass
            with open(file_path, encoding=enc, errors="replace") as f:
                for row in csv.reader(f):
                    rows.append(row)
            result["rows"] = rows
            result["text"] = "\n".join("\t".join(r) for r in rows[:50])
            result["success"] = True

        # --- TEXT / JSON / XML / MD ---
        elif ftype in ("text", "json", "xml", "rtf"):
            enc = "utf-8"
            try:
                import chardet
                with open(file_path, "rb") as f:
                    enc = chardet.detect(f.read(4096)).get("encoding", "utf-8") or "utf-8"
            except Exception:
                pass
            with open(file_path, encoding=enc, errors="replace") as f:
                result["text"] = f.read(50000)
            result["success"] = True

        # --- ИЗОБРАЖЕНИЯ (JPG/PNG/HEIC/BMP/TIFF/WEBP/GIF) ---
        elif ftype in ("jpg", "png", "image", "gif", "bmp", "tiff", "webp_or_avi"):
            import pytesseract
            from PIL import Image
            try:
                from pillow_heif import register_heif_opener
                register_heif_opener()
            except Exception:
                pass
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang="rus+eng")
            result["text"] = text.strip()
            result["success"] = True
            result["type"] = "image"

        # --- DWG → конвертация в DXF → ezdxf ---
        elif ftype == "dwg":
            result = _handle_dwg(file_path, result)

        # --- DXF ---
        elif ftype == "dxf":
            result = _handle_dxf(file_path, result)

        # --- ZIP ---
        elif ftype == "zip":
            result = _handle_zip(file_path, task_id, topic_id, result)

        # --- RAR ---
        elif ftype == "rar":
            try:
                import rarfile
                tmp = tempfile.mkdtemp()
                with rarfile.RarFile(file_path) as rf:
                    rf.extractall(tmp)
                texts = []
                for fn in os.listdir(tmp)[:5]:
                    sub = extract_text_from_file(os.path.join(tmp, fn), task_id, topic_id)
                    if sub["success"]:
                        texts.append(f"[{fn}]\n{sub['text']}")
                result["text"] = "\n\n".join(texts)
                result["success"] = True
                result["type"] = "rar"
            except Exception as e:
                result["error"] = f"RAR: {e}"

        # --- 7Z ---
        elif ftype == "7z":
            try:
                import py7zr
                tmp = tempfile.mkdtemp()
                with py7zr.SevenZipFile(file_path) as sz:
                    sz.extractall(tmp)
                texts = []
                for fn in os.listdir(tmp)[:5]:
                    sub = extract_text_from_file(os.path.join(tmp, fn), task_id, topic_id)
                    if sub["success"]:
                        texts.append(f"[{fn}]\n{sub['text']}")
                result["text"] = "\n\n".join(texts)
                result["success"] = True
                result["type"] = "7z"
            except Exception as e:
                result["error"] = f"7Z: {e}"

        # --- ВИДЕО/АУДИО — метаданные через ffmpeg ---
        elif ftype in ("mp4", "video", "mp3", "audio"):
            try:
                out = subprocess.check_output(
                    ["ffmpeg", "-i", file_path],
                    stderr=subprocess.STDOUT, timeout=10
                ).decode(errors="replace")
            except subprocess.CalledProcessError as e:
                out = e.output.decode(errors="replace")
            result["text"] = out[:2000]
            result["success"] = True

        # --- UNKNOWN — попытка открыть как текст ---
        else:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    txt = f.read(10000)
                if len(txt.strip()) > 20:
                    result["text"] = txt
                    result["success"] = True
                    result["type"] = "text_fallback"
                else:
                    result["error"] = f"Формат не поддерживается: {os.path.splitext(file_path)[1]}"
            except Exception as e:
                result["error"] = f"Неизвестный формат: {e}"

    except Exception as e:
        logger.error("UNIVERSAL_FILE_HANDLER_ERROR type=%s err=%s", ftype, e)
        result["error"] = str(e)

    return result


def _handle_dwg(file_path: str, result: dict) -> dict:
    """DWG: конвертация через dwg2dxf (libredwg), fallback через imagemagick preview"""
    dxf_path = file_path.replace(".dwg", ".dxf").replace(".DWG", ".dxf")
    if not dxf_path.endswith(".dxf"):
        dxf_path = file_path + ".dxf"

    # Попытка 1: dwg2dxf
    try:
        subprocess.run(["dwg2dxf", file_path, "-o", dxf_path],
                       timeout=30, capture_output=True, check=True)
        if os.path.exists(dxf_path):
            logger.info("DWG→DXF conversion OK: %s", dxf_path)
            return _handle_dxf(dxf_path, result)
    except Exception as e:
        logger.warning("dwg2dxf failed: %s", e)

    # Попытка 2: imagemagick — превью в PNG + OCR
    try:
        png_path = file_path + "_preview.png"
        subprocess.run(
            ["convert", "-density", "150", file_path + "[0]", png_path],
            timeout=30, capture_output=True, check=True
        )
        if os.path.exists(png_path):
            import pytesseract
            from PIL import Image
            text = pytesseract.image_to_string(Image.open(png_path), lang="rus+eng")
            result["text"] = f"[DWG файл — превью через OCR]\n{text.strip()}"
            result["success"] = True
            result["type"] = "dwg_ocr_preview"
            return result
    except Exception as e:
        logger.warning("DWG imagemagick fallback failed: %s", e)

    result["error"] = "DWG: конвертация не удалась. Пришли файл в формате .dxf"
    result["text"] = "Файл формата DWG получен. Для полной обработки конвертируй в DXF."
    result["success"] = False
    return result


def _handle_dxf(file_path: str, result: dict) -> dict:
    """DXF через ezdxf"""
    try:
        import ezdxf
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()
        counts = {}
        texts = []
        for e in msp:
            t = e.dxftype()
            counts[t] = counts.get(t, 0) + 1
            if t in ("TEXT", "MTEXT") and hasattr(e.dxf, "text"):
                txt = str(e.dxf.text or "").strip()
                if txt:
                    texts.append(txt)
        summary = "DXF элементы:\n"
        for k, v in sorted(counts.items(), key=lambda x: -x[1])[:15]:
            summary += f"  {k}: {v}\n"
        if texts:
            summary += "\nТексты в чертеже:\n" + "\n".join(texts[:30])
        result["text"] = summary
        result["rows"] = [[k, str(v)] for k, v in counts.items()]
        result["success"] = True
        result["type"] = "dxf"
    except Exception as e:
        result["error"] = f"DXF: {e}"
    return result


def _handle_zip(file_path: str, task_id: str, topic_id: int, result: dict) -> dict:
    """ZIP — распаковка и рекурсивная обработка"""
    try:
        tmp = tempfile.mkdtemp()
        with zipfile.ZipFile(file_path) as zf:
            names = zf.namelist()[:20]
            zf.extractall(tmp)
        texts = []
        all_rows = []
        for fn in names:
            fp = os.path.join(tmp, fn)
            if not os.path.isfile(fp):
                continue
            sub = extract_text_from_file(fp, task_id, topic_id)
            if sub["success"]:
                texts.append(f"[{fn}]\n{sub['text'][:1000]}")
                all_rows.extend(sub.get("rows", []))
        result["text"] = f"ZIP архив ({len(names)} файлов):\n\n" + "\n\n".join(texts)
        result["rows"] = all_rows
        result["success"] = True
        result["type"] = "zip"
    except Exception as e:
        result["error"] = f"ZIP: {e}"
    return result
# === END UNIVERSAL_FILE_HANDLER_V1 ===

====================================================================================================
END_FILE: core/universal_file_handler.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/upload_retry_queue.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c84118ed90d2faa43ddc5a8f1c63e8767639e25641c2b6ebc4c1ca38570171c2
====================================================================================================
"""
Upload retry queue.
Finds tasks where artifact was sent to Telegram (Drive failed),
checks if Drive is now available, re-uploads to Drive.
Notifies user in Telegram with new Drive link.
"""
import os
import sqlite3
import logging
import json
import tempfile
import requests
from dotenv import load_dotenv

load_dotenv("/root/.areal-neva-core/.env", override=True)

logging.basicConfig(
    filename="/root/.areal-neva-core/logs/upload_retry_queue.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

DB_PATH = "/root/.areal-neva-core/data/core.db"
BOT_TOKEN = <REDACTED_SECRET>"BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")


def check_drive_alive() -> bool:
    # === ROOT_TMP_UPLOAD_GUARD_V1 ===
    # Healthcheck MUST NOT upload tmp*.txt into AI_ORCHESTRA root.
    # It only lists the configured Drive root via OAuth.
    try:
        from core.topic_drive_oauth import _oauth_service, _root_folder_id
        service = _oauth_service()
        root_id = _root_folder_id()
        service.files().list(
            q=f"'{root_id}' in parents and trashed = false",
            spaces="drive",
            pageSize=1,
            fields="files(id,name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        logger.info("ROOT_TMP_UPLOAD_GUARD_V1: DRIVE_HEALTH_CHECK_LIST_OK root=%s", root_id)
        return True
    except Exception as e:
        logger.warning("ROOT_TMP_UPLOAD_GUARD_V1: DRIVE_HEALTH_CHECK_FAILED err=%s", e)
        return False
    # === END_ROOT_TMP_UPLOAD_GUARD_V1 ===


def get_pending_retry_tasks(conn: sqlite3.Connection):
    return conn.execute(
        """
        SELECT t.id, t.chat_id, t.topic_id, t.result,
               th_tg.action as tg_action
        FROM tasks t
        JOIN task_history th_tg ON th_tg.task_id = t.id
            AND th_tg.action LIKE 'TELEGRAM_ARTIFACT_FALLBACK_SENT:%'
        WHERE t.state IN ('AWAITING_CONFIRMATION','DONE')
          AND NOT EXISTS (
              SELECT 1 FROM task_history th2
              WHERE th2.task_id = t.id
                AND th2.action LIKE 'DRIVE_RETRY_UPLOAD_OK:%'
          )
        ORDER BY t.updated_at DESC
        LIMIT 20
        """,
    ).fetchall()


def parse_tg_action(action: str) -> dict:
    result = {}
    for part in action.split(":"):
        if "=" in part:
            k, v = part.split("=", 1)
            result[k] = v
    return result


def download_from_telegram(file_id: str, dest_path: str) -> bool:
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
            params={"file_id": file_id},
            timeout=15,
        )
        if not r.ok:
            return False
        file_path = r.json().get("result", {}).get("file_path")
        if not file_path:
            return False
        dl = requests.get(
            f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}",
            timeout=30,
        )
        if not dl.ok:
            return False
        with open(dest_path, "wb") as f:
            f.write(dl.content)
        return True
    except Exception as e:
        logger.error("TG_DOWNLOAD_FAILED file_id=%s err=%s", file_id, e)
        return False


def notify_telegram(chat_id, topic_id, message: str):
    if not BOT_TOKEN:
        return
    try:
        data = {"chat_id": str(chat_id), "text": message, "parse_mode": "HTML"}
        if topic_id and int(topic_id) > 0:
            data["message_thread_id"] = str(topic_id)
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json=data, timeout=10,
        )
    except Exception as e:
        logger.warning("NOTIFY_FAILED err=%s", e)


def run():
    logger.info("RETRY_QUEUE_START")

    if not check_drive_alive():
        logger.info("DRIVE_UNAVAILABLE — skip retry")
        return

    logger.info("DRIVE_ALIVE — checking pending tasks")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        pending = get_pending_retry_tasks(conn)
        logger.info("PENDING_RETRY_COUNT=%d", len(pending))

        for row in pending:
            task_id = row["id"]
            chat_id = row["chat_id"]
            topic_id = row["topic_id"]
            tg_info = parse_tg_action(row["tg_action"])
            file_id = tg_info.get("file_id")

            if not file_id:
                logger.warning("RETRY_SKIP task=%s no file_id", task_id)
                continue

            logger.info("RETRY_ATTEMPT task=%s file_id=%s", task_id, file_id)

            with tempfile.NamedTemporaryFile(
                suffix=".bin", delete=False,
                dir="/root/.areal-neva-core/runtime"
            ) as tmp:
                tmp_path = tmp.name

            ok = download_from_telegram(file_id, tmp_path)
            if not ok:
                logger.error("RETRY_TG_DOWNLOAD_FAILED task=%s", task_id)
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                continue

            # PATCH_RETRY_TOPIC_FOLDER_V1: upload to topic folder, not INGEST root
            try:
                import mimetypes as _mt
                from core.topic_drive_oauth import _upload_file_sync
                # Get original file name from task raw_input
                try:
                    _raw = conn.execute("SELECT raw_input FROM tasks WHERE id=?", (task_id,)).fetchone()
                    _orig_name = json.loads(_raw["raw_input"] or "{}").get("file_name", f"artifact_{task_id[:8]}")
                except Exception:
                    _orig_name = f"artifact_{task_id[:8]}"
                _mime = _mt.guess_type(_orig_name)[0] or "application/octet-stream"
                _up = _upload_file_sync(
                    tmp_path, _orig_name,
                    str(row["chat_id"]), int(topic_id or 0), _mime
                )
                _fid = _up.get("drive_file_id") if isinstance(_up, dict) else None
                drive_link = f"https://drive.google.com/file/d/{_fid}/view" if _fid else None
            except Exception as e:
                logger.error("RETRY_DRIVE_UPLOAD_FAILED task=%s err=%s", task_id, e)
                drive_link = None
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

            if not drive_link or "drive.google.com" not in str(drive_link):
                logger.error("RETRY_NO_LINK task=%s", task_id)
                continue

            old_result = row["result"] or ""
            new_result = old_result.replace(
                "Файл отправлен в Telegram. Внешнее хранилище временно недоступно.",
                f"Файл доступен на Drive: {drive_link}"
            )
            if new_result == old_result:
                new_result = old_result + f"\n\nФайл теперь на Drive: {drive_link}"

            conn.execute(
                "UPDATE tasks SET result=?, updated_at=datetime('now') WHERE id=?",
                (new_result, task_id),
            )
            conn.execute(
                "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                (task_id, f"DRIVE_RETRY_UPLOAD_OK:{drive_link}"),
            )
            conn.commit()

            notify_telegram(
                chat_id, topic_id,
                f"✅ Файл теперь доступен на Google Drive:\n{drive_link}"
            )
            logger.info("RETRY_UPLOAD_OK task=%s link=%s", task_id, drive_link)

    finally:
        conn.close()

    logger.info("RETRY_QUEUE_DONE")


if __name__ == "__main__":
    # === FULLFIX_20_RETRY_LOOP ===
    import time as _ff20_time
    logger.info("UPLOAD_RETRY_SERVICE_START")
    while True:
        try:
            run()
        except Exception as _ff20_re:
            logger.exception("UPLOAD_RETRY_LOOP_ERR=%s", _ff20_re)
        _ff20_time.sleep(300)
    # === END FULLFIX_20_RETRY_LOOP ===

====================================================================================================
END_FILE: core/upload_retry_queue.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/web_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 60ae8879713e63665e3b98acb78976ad8f6522694bb018b072daed8bd67c8912
====================================================================================================
import logging

logger = logging.getLogger("web_engine")

async def web_search(query: str) -> str:
    # Search handled by ONLINE_MODEL (perplexity/sonar) in ai_router.py
    logger.warning("web_search_stub called query=%s", (query or "")[:100])
    return ""

====================================================================================================
END_FILE: core/web_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/work_item.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ec6ecd21b8594924d8b0bdd0bde9e53d00e69485f45b88db8f7aedb11624f2f3
====================================================================================================
# === FULLFIX_DIRECTION_KERNEL_STAGE_1_WORKITEM ===
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


def _get(row, key, default=None):
    if row is None: return default
    if isinstance(row, dict): return row.get(key, default)
    try: return row[key]
    except Exception: return getattr(row, key, default)

def _int(v, d=0):
    try:
        if v is None or v == "": return d
        return int(v)
    except Exception: return d

def _str(v, d=""):
    if v is None: return d
    return str(v)


@dataclass
class WorkItem:
    work_id: str
    chat_id: str
    topic_id: int
    user_id: Optional[str] = None
    message_id: Optional[int] = None
    reply_to_message_id: Optional[int] = None
    bot_message_id: Optional[int] = None
    source_type: str = "telegram"
    input_type: str = "unknown"
    raw_text: str = ""
    state: str = "NEW"
    intent: str = "UNKNOWN"
    direction: Optional[str] = None
    direction_profile: Dict[str, Any] = field(default_factory=dict)
    formats_in: List[str] = field(default_factory=list)
    formats_out: List[str] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    context_refs: Dict[str, Any] = field(default_factory=dict)
    execution_plan: List[Dict[str, Any]] = field(default_factory=list)
    quality_gates: List[str] = field(default_factory=list)
    result: Dict[str, Any] = field(default_factory=dict)
    audit: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_task_row(cls, row, extra=None):
        extra = extra or {}
        raw_text = _str(extra.get("raw_text") or extra.get("raw_input") or _get(row, "raw_input", ""))
        input_type = _str(extra.get("input_type") or _get(row, "input_type", "unknown"), "unknown")
        topic_id = _int(extra.get("topic_id") if extra.get("topic_id") is not None else _get(row, "topic_id", 0), 0)
        wi = cls(
            work_id=_str(extra.get("work_id") or extra.get("task_id") or _get(row, "id", "")),
            chat_id=_str(extra.get("chat_id") or _get(row, "chat_id", "")),
            topic_id=topic_id,
            user_id=_str(extra.get("user_id") or _get(row, "user_id", "")) or None,
            message_id=_int(extra.get("message_id") or _get(row, "message_id", None), 0) or None,
            reply_to_message_id=_int(extra.get("reply_to_message_id") if extra.get("reply_to_message_id") is not None else _get(row, "reply_to_message_id", None), 0) or None,
            bot_message_id=_int(extra.get("bot_message_id") if extra.get("bot_message_id") is not None else _get(row, "bot_message_id", None), 0) or None,
            source_type=_str(extra.get("source_type") or "telegram"),
            input_type=input_type,
            raw_text=raw_text,
            state=_str(extra.get("state") or _get(row, "state", "NEW"), "NEW"),
            created_at=_str(extra.get("created_at") or _get(row, "created_at", "")) or None,
            updated_at=_str(extra.get("updated_at") or _get(row, "updated_at", "")) or None,
        )
        wi.formats_in = wi._detect_formats_in()
        wi.result = {"text": _str(_get(row, "result", ""))}
        err = _str(_get(row, "error_message", ""))
        if err:
            wi.errors.append({"code": "TASK_ERROR", "message": err, "fatal": False})
        wi.audit["created_by"] = "FULLFIX_DIRECTION_KERNEL_STAGE_1"
        return wi

    def _detect_formats_in(self):
        t = (self.input_type or "").lower()
        raw = (self.raw_text or "").lower()
        out = []
        if t in ("text","voice","photo","file","drive_file","url","mixed"): out.append(t)
        if ".pdf" in raw or "pdf" in t: out.append("pdf")
        if ".xlsx" in raw or ".xls" in raw: out.append("xlsx")
        if ".dwg" in raw: out.append("dwg")
        if t in ("photo","image"): out.append("photo")
        if not out: out.append("text")
        return list(dict.fromkeys(out))

    def set_direction(self, direction, profile=None):
        self.direction = direction
        self.direction_profile = profile or {}
        self.audit["direction"] = direction
        self.audit["direction_profile_id"] = self.direction_profile.get("id", direction)

    def set_intent(self, intent):
        self.intent = intent or "UNKNOWN"
        self.audit["intent"] = self.intent

    def add_audit(self, key, value):
        self.audit[str(key)] = value

    def add_error(self, code, message, fatal=False):
        self.errors.append({"code": str(code), "message": str(message), "fatal": bool(fatal)})

    def to_dict(self): return asdict(self)

    def to_payload(self):
        return {
            "id": self.work_id, "task_id": self.work_id,
            "chat_id": self.chat_id, "topic_id": self.topic_id,
            "user_id": self.user_id, "message_id": self.message_id,
            "reply_to_message_id": self.reply_to_message_id,
            "bot_message_id": self.bot_message_id,
            "source_type": self.source_type, "input_type": self.input_type,
            "raw_input": self.raw_text, "raw_text": self.raw_text,
            "state": self.state, "intent": self.intent,
            "direction": self.direction, "direction_profile": self.direction_profile,
            "formats_in": self.formats_in, "formats_out": self.formats_out,
            "attachments": self.attachments, "parsed_data": self.parsed_data,
            "context_refs": self.context_refs, "execution_plan": self.execution_plan,
            "quality_gates": self.quality_gates, "result": self.result,
            "audit": self.audit, "direction_audit": self.audit,
            "errors": self.errors, "metadata": self.metadata,
            "work_item": self.to_dict(),
        }
# === END FULLFIX_DIRECTION_KERNEL_STAGE_1_WORKITEM ===

====================================================================================================
END_FILE: core/work_item.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/full_context_aggregator.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 362029375c3a7d1a17f5e6998413963a28cb01a293fbcee90485d4b03a2f240d
====================================================================================================
#!/usr/bin/env python3
# === FULL_CONTEXT_AGGREGATOR_V1 ===
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
OUTPUT_DIR = BASE / "docs/SHARED_CONTEXT"
REPO = "rj7hmz9cvm-lgtm/areal-neva-core"
RAW_MAIN = f"https://raw.githubusercontent.com/{REPO}/main"
LOCK_PATH = Path("/tmp/areal_full_context_aggregator.lock")
PART_MAX_BYTES = 400_000
CONTENT_CHUNK_BYTES = 340_000

TEXT_SUFFIXES = {
    ".py", ".md", ".json", ".yaml", ".yml", ".sh", ".txt", ".service", ".timer",
    ".conf", ".ini", ".toml", ".sql", ".csv", ".gitignore", ".dockerignore",
}
TEXT_NAMES = {".gitignore", ".dockerignore", "Dockerfile", "Makefile"}

SECRET_PATH_PARTS = {
    ".env", ".secret_patterns", "token.json", "credentials.json", "client_secret.json",
}
SECRET_PATH_FRAGMENTS = (
    "service_account",
    "client_secret",
    "private_key",
    "credentials",
    "/sessions/",
    "/keys/",
)
BINARY_SUFFIXES = {
    ".session", ".db", ".sqlite", ".sqlite3", ".pdf", ".dwg", ".dxf", ".jpg", ".jpeg",
    ".png", ".mp4", ".mov", ".webp", ".gif", ".ico", ".pyc", ".pyo", ".so", ".o",
    ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar", ".xlsx", ".xls", ".docx", ".doc",
}
SKIP_DIR_PARTS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".mypy_cache", ".pytest_cache"}

GENERATED_EXACT = {
    "docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md",
    "docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md",
    "docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md",
    "docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md",
    "docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json",
}
GENERATED_PREFIXES = (
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_",
)

PRIORITY_PREFIXES = [
    "docs/HANDOFFS/LATEST_HANDOFF",
    "docs/REPORTS/NOT_CLOSED",
    "docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL",
    "docs/CANON_FINAL/",
    "docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK",
    "docs/ARCHITECTURE/SEARCH_MONOLITH",
    "docs/ARCHITECTURE/",
    "docs/HANDOFFS/",
    "docs/REPORTS/",
    "chat_exports/",
    "config/",
    "task_worker.py",
    "telegram_daemon.py",
    "core/project_route_guard.py",
    "core/final_closure_engine.py",
    "core/file_context_intake.py",
    "core/reply_repeat_parent.py",
    "core/estimate_engine.py",
    "core/project_engine.py",
    "core/file_intake_router.py",
    "core/ai_router.py",
    "core/",
    "tools/full_context_aggregator.py",
    "tools/context_aggregator.py",
    "tools/claude_bootstrap_aggregator.py",
    "tools/",
]

TOPIC_REGISTRY = """TOPIC_REGISTRY:
topic_0=CHAT_ZADACH: общий чат
topic_2=STROYKA: estimate_engine, Excel =C*D =SUM, Python считает, LLM не считает
topic_5=TEKHNADZOR: technadzor_engine, Gemini vision, нормы СП/ГОСТ без выдумывания
topic_11=VIDEOKONTENT
topic_210=PROEKTIROVANIE: project_engine, PROJECT_TEMPLATE_MODEL, не OCR текст
topic_500=VEB_POISK: только Perplexity, 14 этапов, file-context/file-menu запрещены
topic_794=NEJRONKI_SOFT_VPN_VPS
topic_961=AVTO_ZAPCHASTI: OEM, Exist/Drom/Emex
topic_3008=KODY_MOZGOV: верификация кода, No Auto-Patch
topic_4569=LIDY_REKLAMA_AMO
topic_6104=RABOTA_POISK"""

PROTOCOL = """OPERATING_PROTOCOL:
MODE: FACT_ONLY / ZERO_ASSUMPTIONS / GITHUB_SSOT / CANON_LOCK
ONE_LINK_GOAL: модель читает MODEL_BOOTSTRAP_CONTEXT.md и сразу получает всю картину
PATCH_ORDER: DIAGNOSTICS → BAK → PATCH → PY_COMPILE → RESTART → LOGS → DB_VERIFY → GIT_PUSH → FINAL_VERIFY
FORBIDDEN: .env, credentials, token, sessions, raw DB dumps, rm -rf project/canon dirs
CONTEXT_RULE: разрешённые текстовые файлы включаются полностью без обрезки
BIG_TEXT_RULE: большие текстовые файлы дробятся по PART-файлам, не режутся
SECRET_RULE: секретные значения редактируются как <REDACTED_SECRET>
STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test"""

SECRET_VALUE_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
    re.compile(r"github_pat_[A-Za-z0-9_]{50,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{30,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_\-]{30,}\b"),
    re.compile(r"1//[A-Za-z0-9_\-]{20,}"),
    re.compile(r'("private_key"\s*:\s*")[^"]+(")'),
    re.compile(r'((?:API_KEY|TOKEN|SECRET|PASSWORD)\s*=\s*)[^\s\'"]+', re.I),
]


def run(cmd: list[str], check: bool = False) -> str:
    p = subprocess.run(cmd, cwd=str(BASE), text=True, capture_output=True)
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    if check and p.returncode != 0:
        raise RuntimeError(f"CMD_FAIL: {' '.join(cmd)}\n{out}")
    return out


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize_text(text: str) -> str:
    out = text
    for pat in SECRET_VALUE_PATTERNS:
        if pat.pattern.startswith('("private_key"'):
            out = pat.sub(r'\1<REDACTED_SECRET>\2', out)
        elif "(?:API_KEY|TOKEN|SECRET|PASSWORD)" in pat.pattern:
            out = pat.sub(r"\1<REDACTED_SECRET>", out)
        else:
            out = pat.sub("<REDACTED_SECRET>", out)
    return out


def is_generated_output(rel: str) -> bool:
    if rel in GENERATED_EXACT:
        return True
    return any(rel.startswith(p) for p in GENERATED_PREFIXES)


def classify_path(rel: str) -> tuple[str, str]:
    low = rel.lower()
    parts = set(Path(rel).parts)
    name = Path(rel).name
    suffix = Path(rel).suffix.lower()

    if is_generated_output(rel):
        return "excluded_generated_output", "generated output avoids self-ingestion"
    if any(x in parts for x in SKIP_DIR_PARTS):
        return "excluded_dir", "runtime/cache/git dir"
    if name in SECRET_PATH_PARTS:
        return "excluded_secret_path", "secret path"
    if any(x in low for x in SECRET_PATH_FRAGMENTS):
        return "excluded_secret_path", "secret path fragment"
    if ".bak" in low or low.endswith(".bak") or ".bak_" in low:
        return "excluded_backup", "backup file"
    if suffix in BINARY_SUFFIXES:
        return "excluded_binary", "binary/raw db/heavy media"
    if suffix in TEXT_SUFFIXES or name in TEXT_NAMES:
        return "full", "tracked text"
    return "excluded_non_text", "suffix not allowlisted"


def sort_key(rel: str) -> tuple[int, str]:
    for i, p in enumerate(PRIORITY_PREFIXES):
        if rel.startswith(p) or p in rel:
            return (i, rel)
    return (len(PRIORITY_PREFIXES), rel)


def git_tracked_files() -> list[str]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=str(BASE))
    files = [x for x in raw.decode("utf-8", errors="replace").split("\0") if x]
    for extra in (
        "tools/full_context_aggregator.py",
        "tools/context_aggregator.py",
        "tools/claude_bootstrap_aggregator.py",
    ):
        if (BASE / extra).exists() and extra not in files:
            files.append(extra)
    return sorted(set(files), key=sort_key)


def collect_files() -> tuple[list[dict], list[dict]]:
    full_items: list[dict] = []
    manifest_items: list[dict] = []

    for rel in git_tracked_files():
        mode, reason = classify_path(rel)
        p = BASE / rel
        size = p.stat().st_size if p.exists() else 0

        record = {
            "path": rel,
            "mode": mode,
            "reason": reason,
            "size_bytes": size,
            "sha256": "",
            "chars": 0,
            "chunks": 0,
        }

        if mode != "full":
            manifest_items.append(record)
            continue

        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            text = sanitize_text(text)
            record["sha256"] = sha256_text(text)
            record["chars"] = len(text)
            full_items.append({"path": rel, "content": text, "record": record})
        except Exception as e:
            record["mode"] = "read_error"
            record["reason"] = str(e)
        manifest_items.append(record)

    return full_items, manifest_items


def split_text_by_bytes(text: str, limit: int) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_size = 0

    for line in text.splitlines(True):
        b = len(line.encode("utf-8", errors="replace"))
        if current and current_size + b > limit:
            chunks.append("".join(current))
            current = []
            current_size = 0

        if b > limit:
            data = line.encode("utf-8", errors="replace")
            for i in range(0, len(data), limit):
                chunks.append(data[i:i + limit].decode("utf-8", errors="replace"))
            continue

        current.append(line)
        current_size += b

    if current:
        chunks.append("".join(current))
    return chunks or [""]


def build_file_blocks(full_items: list[dict]) -> tuple[list[str], dict[str, int]]:
    blocks: list[str] = []
    chunk_counts: dict[str, int] = {}

    for item in full_items:
        rel = item["path"]
        content = item["content"]
        chunks = split_text_by_bytes(content, CONTENT_CHUNK_BYTES)
        chunk_counts[rel] = len(chunks)
        for idx, chunk in enumerate(chunks, 1):
            header = (
                "\n" + "=" * 100 + "\n"
                f"BEGIN_FILE: {rel}\n"
                f"FILE_CHUNK: {idx}/{len(chunks)}\n"
                f"SHA256_FULL_FILE: {sha256_text(content)}\n"
                + "=" * 100 + "\n"
            )
            footer = (
                "\n" + "=" * 100 + "\n"
                f"END_FILE: {rel}\n"
                f"FILE_CHUNK: {idx}/{len(chunks)}\n"
                + "=" * 100 + "\n"
            )
            blocks.append(header + chunk + footer)
    return blocks, chunk_counts


def split_blocks_to_parts(blocks: list[str]) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    size = 0

    for block in blocks:
        bsize = len(block.encode("utf-8", errors="replace"))
        if current and size + bsize > PART_MAX_BYTES:
            parts.append("".join(current))
            current = []
            size = 0
        current.append(block)
        size += bsize

    if current:
        parts.append("".join(current))
    return parts


def sql_rows(db: Path, query: str, limit: int = 20) -> list[str]:
    try:
        if not db.exists():
            return ["DB_NOT_FOUND"]
        con = sqlite3.connect(str(db))
        rows = con.execute(query).fetchmany(limit)
        con.close()
        return ["|".join(str(x) for x in r) for r in rows]
    except Exception as e:
        return [f"SQL_ERROR:{e}"]


def build_runtime_snapshot(git_sha: str) -> str:
    core_db = BASE / "data/core.db"
    mem_db = BASE / "data/memory.db"
    lines: list[str] = []

    lines.append("# SAFE_RUNTIME_SNAPSHOT")
    lines.append(f"generated_at_utc: {utc_now()}")
    lines.append(f"git_sha_before_commit: {git_sha}")
    lines.append(f"git_branch: {run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])}")
    lines.append("")
    lines.append("## SERVICES")
    for svc in (
        "areal-task-worker",
        "telegram-ingress",
        "areal-memory-api",
        "areal-claude-bootstrap-aggregator.timer",
    ):
        lines.append(f"- {svc}: {run(['systemctl', 'is-active', svc])}")
    lines.append("")
    lines.append("## GIT_LOG_30")
    lines.append(run(["git", "log", "--oneline", "-30"]))
    lines.append("")
    lines.append("## GIT_SHOW_STAT_HEAD")
    lines.append(run(["git", "show", "--stat", "HEAD"]))
    lines.append("")
    lines.append("## GIT_CHANGED_FILES_10")
    lines.append(run(["git", "diff", "--name-only", "HEAD~10..HEAD"]))
    lines.append("")
    lines.append("## CORE_DB_STATE_COUNTS")
    lines.extend(f"- {x}" for x in sql_rows(core_db, "SELECT state,COUNT(*) FROM tasks GROUP BY state ORDER BY 2 DESC"))
    lines.append("")
    lines.append("## CORE_DB_OPEN_TASKS")
    lines.extend(f"- {x}" for x in sql_rows(core_db, "SELECT COUNT(*) FROM tasks WHERE state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')"))
    lines.append("")
    lines.append("## LATEST_TASKS_15")
    lines.extend(f"- {x}" for x in sql_rows(core_db, "SELECT id,COALESCE(topic_id,0),input_type,state,substr(raw_input,1,120),substr(result,1,160),updated_at FROM tasks ORDER BY rowid DESC LIMIT 15", 15))
    lines.append("")
    lines.append("## LATEST_FAILED_10")
    lines.extend(f"- {x}" for x in sql_rows(core_db, "SELECT id,COALESCE(topic_id,0),substr(raw_input,1,120),substr(error_message,1,160),updated_at FROM tasks WHERE state='FAILED' ORDER BY rowid DESC LIMIT 10", 10))
    lines.append("")
    lines.append("## LATEST_TASK_HISTORY_20")
    lines.extend(f"- {x}" for x in sql_rows(core_db, "SELECT task_id,substr(action,1,180),created_at FROM task_history ORDER BY id DESC LIMIT 20", 20))
    lines.append("")
    lines.append("## MEMORY_DB_COUNT")
    lines.extend(f"- {x}" for x in sql_rows(mem_db, "SELECT COUNT(*) FROM memory"))
    lines.append("")
    lines.append("## LATEST_MEMORY_20")
    lines.extend(f"- {x}" for x in sql_rows(mem_db, "SELECT key,substr(value,1,180),timestamp FROM memory ORDER BY timestamp DESC LIMIT 20", 20))
    lines.append("")
    lines.append("## JOURNAL_AREAL_TASK_WORKER_60")
    lines.append(sanitize_text(run(["journalctl", "-u", "areal-task-worker", "-n", "60", "--no-pager", "--output=cat"])))
    lines.append("")
    lines.append("## JOURNAL_TELEGRAM_INGRESS_30")
    lines.append(sanitize_text(run(["journalctl", "-u", "telegram-ingress", "-n", "30", "--no-pager", "--output=cat"])))
    return "\n".join(lines).rstrip() + "\n"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"WRITTEN {path.relative_to(BASE)} {len(content.encode('utf-8'))} bytes")


def cleanup_old_parts() -> None:
    for p in OUTPUT_DIR.glob("ORCHESTRA_FULL_CONTEXT_PART_*.md"):
        p.unlink()


def build_manifest(records: list[dict], chunk_counts: dict[str, int], git_sha: str, parts_count: int) -> str:
    out_records = []
    for r in records:
        rr = dict(r)
        rr["chunks"] = chunk_counts.get(r["path"], 0)
        out_records.append(rr)

    data = {
        "generated_at_utc": utc_now(),
        "git_sha_before_commit": git_sha,
        "part_max_bytes": PART_MAX_BYTES,
        "content_chunk_bytes": CONTENT_CHUNK_BYTES,
        "total_records": len(out_records),
        "included_full_files": sum(1 for r in out_records if r["mode"] == "full"),
        "excluded_records": sum(1 for r in out_records if r["mode"] != "full"),
        "parts_count": parts_count,
        "raw_main": RAW_MAIN,
        "outputs": {
            "model_bootstrap": f"{RAW_MAIN}/docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md",
            "claude_alias": f"{RAW_MAIN}/docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md",
            "one_shared": f"{RAW_MAIN}/docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md",
            "runtime": f"{RAW_MAIN}/docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md",
            "full_context_index": f"{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md",
            "manifest": f"{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json",
            "parts": [
                f"{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md"
                for i in range(1, parts_count + 1)
            ],
        },
        "files": out_records,
    }
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def build_context_index(git_sha: str, parts_count: int, records: list[dict]) -> str:
    parts_links = "\n".join(
        f"- PART_{i:03d}: {RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md"
        for i in range(1, parts_count + 1)
    )
    return f"""# ORCHESTRA_FULL_CONTEXT

generated_at_utc: {utc_now()}
git_sha_before_commit: {git_sha}
parts_count: {parts_count}
included_full_files: {sum(1 for r in records if r["mode"] == "full")}
excluded_records: {sum(1 for r in records if r["mode"] != "full")}

{PROTOCOL}

{TOPIC_REGISTRY}

## FULL_CONTEXT_PARTS
{parts_links}

## MANIFEST
{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json

## RUNTIME
{RAW_MAIN}/docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md
"""


def build_model_bootstrap(git_sha: str, parts_count: int, manifest_sha: str) -> str:
    parts_links = "\n".join(
        f"- PART_{i:03d}: {RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md"
        for i in range(1, parts_count + 1)
    )
    return f"""# MODEL_BOOTSTRAP_CONTEXT

SYSTEM: AREAL-NEVA ORCHESTRA
GENERATED_AT_UTC: {utc_now()}
GIT_SHA_BEFORE_COMMIT: {git_sha}
MODE: FACT_ONLY / ZERO_ASSUMPTIONS / GITHUB_SSOT / CANON_LOCK
NO_TRUNCATION: TRUE
TEXT_FILES_INCLUDED_FULLY: TRUE
BIG_FILES_SPLIT_TO_PARTS: TRUE
MANIFEST_SHA256: {manifest_sha}

RAW_THIS_FILE:
{RAW_MAIN}/docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md

CLAUDE_ALIAS:
{RAW_MAIN}/docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md

IF_UNAVAILABLE:
MODEL_BOOTSTRAP_CONTEXT_UNAVAILABLE

{PROTOCOL}

{TOPIC_REGISTRY}

## READ_ORDER
1. This MODEL_BOOTSTRAP_CONTEXT
2. SAFE_RUNTIME_SNAPSHOT
3. ORCHESTRA_FULL_CONTEXT_MANIFEST
4. Required ORCHESTRA_FULL_CONTEXT_PART_XXX files

## RAW_LINKS
SAFE_RUNTIME_SNAPSHOT:
{RAW_MAIN}/docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md

ORCHESTRA_FULL_CONTEXT_INDEX:
{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md

ORCHESTRA_FULL_CONTEXT_MANIFEST:
{RAW_MAIN}/docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json

## FULL_CONTEXT_PARTS
{parts_links}

## PRIORITY_OF_TRUTH
1. Live user output + terminal
2. SAFE_RUNTIME_SNAPSHOT
3. LATEST_HANDOFF
4. NOT_CLOSED
5. CANON_FINAL
6. ARCHITECTURE
7. FULL_CONTEXT_PARTS
8. chat_exports
9. UNKNOWN

## CURRENT_OPEN_STATUS
CANON_ROUTE_FIX_V2: INSTALLED, live-test required
FULL_CONTEXT_AGGREGATOR_V1: this file is generated by full_context_aggregator.py
"""


def build_session_start_prompt() -> str:
    return f"""# CLAUDE_SESSION_START_PROMPT

GENERATED_AT_UTC: {utc_now()}

MANDATORY FIRST STEP:
Read this file before answering any technical question:

{RAW_MAIN}/docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md

If unavailable, answer only:
MODEL_BOOTSTRAP_CONTEXT_UNAVAILABLE

This prompt is an alias. The universal source for all models is MODEL_BOOTSTRAP_CONTEXT.md
"""


def ensure_secret_patterns() -> None:
    p = BASE / ".secret_patterns"
    if p.exists():
        return
    p.write_text(
        "\n".join([
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
            r"github_pat_[A-Za-z0-9_]{50,}",
            r"ghp_[A-Za-z0-9_]{30,}",
            r"sk-[A-Za-z0-9_\-]{20,}",
            r"\b[0-9]{8,10}:[A-Za-z0-9_\-]{30,}\b",
            r"1//[A-Za-z0-9_\-]{20,}",
            r'"private_key"\s*:\s*"[^"]+',
            r"(OPENROUTER_API_KEY|TELEGRAM_BOT_TOKEN|GROQ_API_KEY|GITHUB_TOKEN)\s*=\s*[^<\s]+",
            "",
        ]),
        encoding="utf-8",
    )
    os.chmod(p, 0o600)
    print("SECRET_PATTERNS_CREATED")


def stage_outputs(parts_count: int) -> None:
    generated = [
        "tools/full_context_aggregator.py",
        "tools/context_aggregator.py",
        "tools/claude_bootstrap_aggregator.py",
        "docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md",
        "docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md",
        "docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md",
        "docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md",
        "docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md",
        "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md",
        "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json",
    ] + [
        f"docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md"
        for i in range(1, parts_count + 1)
    ]
    subprocess.run(["git", "add", "-u", "docs/SHARED_CONTEXT"], cwd=str(BASE), check=True)
    subprocess.run(["git", "add"] + generated, cwd=str(BASE), check=True)


def run_secret_scan() -> None:
    scan = BASE / "tools/secret_scan.sh"
    if not scan.exists():
        raise RuntimeError("SECRET_SCAN_NOT_FOUND")
    ensure_secret_patterns()
    p = subprocess.run(["bash", str(scan)], cwd=str(BASE), text=True, capture_output=True)
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    print(out)
    if "SECRET_SCAN_SKIP" in out:
        raise RuntimeError("SECRET_SCAN_SKIP_IS_FAIL")
    if p.returncode != 0:
        raise RuntimeError("SECRET_SCAN_FAILED")
    print("SECRET_SCAN_OK_CONFIRMED")


def commit_push_verify() -> str:
    status = run(["git", "status", "--short"])
    print("GIT_STATUS_BEFORE_COMMIT:")
    print(status if status else "clean")

    if "D tools/context_aggregator.py" in status:
        raise RuntimeError("CONTEXT_AGGREGATOR_DELETED_REFUSE_COMMIT")

    if not status.strip():
        print("NO_GIT_CHANGE")
        return run(["git", "rev-parse", "HEAD"], check=True)

    commit = subprocess.run(
        ["git", "commit", "-m", "FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context"],
        cwd=str(BASE),
        text=True,
        capture_output=True,
    )
    print(commit.stdout.strip())
    if commit.returncode != 0 and "nothing to commit" not in (commit.stdout + commit.stderr):
        print(commit.stderr.strip())
        raise RuntimeError("COMMIT_FAILED")

    # === FULL_CONTEXT_AGGREGATOR_TOKEN_PUSH_V1 ===
    token = <REDACTED_SECRET>"GITHUB_TOKEN", "").strip()
    if not token:
        env_path = BASE / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "GITHUB_TOKEN":
                    token = <REDACTED_SECRET>"'").strip('"')
                    break
    if not token:
        raise RuntimeError("GITHUB_TOKEN_MISSING_FOR_PUSH")

    import base64 as _b64_fca
    auth = _b64_fca.b64encode(("x-access-token:" + token).encode("utf-8")).decode("ascii")
    push = subprocess.run(
        ["git", "-c", "http.https://github.com/.extraheader=AUTHORIZATION: basic " + auth, "push", "origin", "main"],
        cwd=str(BASE),
        text=True,
        capture_output=True,
    )
    print(push.stdout.strip())
    print(push.stderr.strip())
    if push.returncode != 0:
        raise RuntimeError("PUSH_FAILED")
    # === END_FULL_CONTEXT_AGGREGATOR_TOKEN_PUSH_V1 ===

    new_sha = run(["git", "rev-parse", "HEAD"], check=True)
    print(f"PUSH_OK {new_sha}")
    return new_sha


def verify_raw_exact(commit_sha: str) -> None:
    local_path = OUTPUT_DIR / "MODEL_BOOTSTRAP_CONTEXT.md"
    expected = sha256_file(local_path)
    url = f"https://raw.githubusercontent.com/{REPO}/{commit_sha}/docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md"

    for i in range(1, 8):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                data = r.read()
            actual = hashlib.sha256(data).hexdigest()
            if actual == expected:
                print(f"RAW_EXACT_SHA_VERIFY_OK {commit_sha}")
                return
            print(f"RAW_HASH_MISMATCH attempt={i}")
        except Exception as e:
            print(f"RAW_VERIFY_FAIL attempt={i}: {e}")
        time.sleep(5)

    raise RuntimeError("RAW_EXACT_SHA_VERIFY_FAILED")


def main() -> None:
    with LOCK_PATH.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("FULL_CONTEXT_AGGREGATOR_ALREADY_RUNNING")
            return

        print(f"FULL_CONTEXT_AGGREGATOR_V1_START {utc_now()}")

        if not run(["git", "ls-files", "tools/context_aggregator.py"]).strip():
            raise RuntimeError("CONTEXT_AGGREGATOR_NOT_TRACKED")

        git_sha_before = run(["git", "rev-parse", "HEAD"], check=True)

        full_items, manifest_records = collect_files()
        print(f"INCLUDED_FULL_FILES {len(full_items)}")
        print(f"MANIFEST_RECORDS {len(manifest_records)}")

        blocks, chunk_counts = build_file_blocks(full_items)
        parts = split_blocks_to_parts(blocks)
        print(f"PARTS_COUNT {len(parts)}")

        cleanup_old_parts()

        runtime = build_runtime_snapshot(git_sha_before)
        write(OUTPUT_DIR / "SAFE_RUNTIME_SNAPSHOT.md", runtime)

        for i, content in enumerate(parts, 1):
            header = (
                f"# ORCHESTRA_FULL_CONTEXT_PART_{i:03d}\n"
                f"generated_at_utc: {utc_now()}\n"
                f"git_sha_before_commit: {git_sha_before}\n"
                f"part: {i}/{len(parts)}\n\n"
            )
            write(OUTPUT_DIR / f"ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md", header + content)

        manifest = build_manifest(manifest_records, chunk_counts, git_sha_before, len(parts))
        write(OUTPUT_DIR / "ORCHESTRA_FULL_CONTEXT_MANIFEST.json", manifest)

        context_index = build_context_index(git_sha_before, len(parts), manifest_records)
        write(OUTPUT_DIR / "ORCHESTRA_FULL_CONTEXT.md", context_index)

        bootstrap = build_model_bootstrap(git_sha_before, len(parts), sha256_text(manifest))
        write(OUTPUT_DIR / "MODEL_BOOTSTRAP_CONTEXT.md", bootstrap)
        write(OUTPUT_DIR / "CLAUDE_BOOTSTRAP_CONTEXT.md", bootstrap)
        write(OUTPUT_DIR / "ONE_SHARED_CONTEXT.md", bootstrap)
        write(OUTPUT_DIR / "CLAUDE_SESSION_START_PROMPT.md", build_session_start_prompt())

        stage_outputs(len(parts))
        run_secret_scan()
        new_sha = commit_push_verify()
        verify_raw_exact(new_sha)

        print(f"FULL_CONTEXT_AGGREGATOR_V1_DONE {utc_now()}")
        print(f"COMMIT_SHA {new_sha}")
        print(f"PARTS {len(parts)}")
        print(f"FILES_INCLUDED {len(full_items)}")


if __name__ == "__main__":
    main()
# === END_FULL_CONTEXT_AGGREGATOR_V1 ===

====================================================================================================
END_FILE: tools/full_context_aggregator.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/context_aggregator.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 069bfcbd7cb905f16621726e8c56d54aea8340b8513d405d9fc6c6df655c2a36
====================================================================================================
#!/usr/bin/env python3
# === CONTEXT_AGGREGATOR_WRAPPER_V1 ===
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

BASE = Path("/root/.areal-neva-core")

def main() -> None:
    print("CONTEXT_AGGREGATOR_WRAPPER_V1 -> full_context_aggregator.py")
    p = subprocess.run([sys.executable, str(BASE / "tools/full_context_aggregator.py")], cwd=str(BASE))
    sys.exit(p.returncode)

if __name__ == "__main__":
    main()
# === END_CONTEXT_AGGREGATOR_WRAPPER_V1 ===

====================================================================================================
END_FILE: tools/context_aggregator.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/claude_bootstrap_aggregator.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c2f2cd0625c8961b4638a63547ed4c7b3c505ec64a1017f11ccc1a837a42cbda
====================================================================================================
#!/usr/bin/env python3
# === CLAUDE_BOOTSTRAP_AGGREGATOR_WRAPPER_V1 ===
# CANON_FINAL_REMOVE_COMMAND_DISABLED
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

BASE = Path("/root/.areal-neva-core")

def main() -> None:
    print("CLAUDE_BOOTSTRAP_AGGREGATOR_WRAPPER_V1 -> full_context_aggregator.py")
    p = subprocess.run([sys.executable, str(BASE / "tools/full_context_aggregator.py")], cwd=str(BASE))
    sys.exit(p.returncode)

if __name__ == "__main__":
    main()
# === END_CLAUDE_BOOTSTRAP_AGGREGATOR_WRAPPER_V1 ===

====================================================================================================
END_FILE: tools/claude_bootstrap_aggregator.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/areal_reference_full_monolith_v1.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c571186116ab07d575b430586287bd9a0ab372cfb60fc106d6445d8c6ef35297
====================================================================================================
#!/usr/bin/env python3
# === AREAL_REFERENCE_FULL_MONOLITH_V1 ===
from __future__ import annotations

import io
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

BASE = Path("/root/.areal-neva-core")
CHAT_ID = "-1003725299009"
MAX_DOWNLOAD = 5 * 1024 * 1024

ROOTS = {
    "ESTIMATES_TEMPLATES": "19Z3acDgPub4nV55mad5mb8ju63FsqoG9",
    "TOPIC_210": "17QGniGggGgYEAD8lIyUK6TjgMIIDKhAq",
    "TOPIC_5": "1yWIJdSrypH3BbIozCz-OAw1R6hmnMRHK",
}

MEMORY_DB = BASE / "data" / "memory.db"
REGISTRY_PATH = BASE / "config" / "owner_reference_registry.json"
CANON_PATH = BASE / "docs" / "CANON_FINAL" / "OWNER_REFERENCE_FULL_WORKFLOW_CANON.md"
REPORT_PATH = BASE / "docs" / "REPORTS" / "AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT.md"
INDEX_PATH = BASE / "data" / "templates" / "reference_monolith" / "owner_reference_full_index.json"
VERSION = "AREAL_REFERENCE_FULL_MONOLITH_V1"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def s(v: Any) -> str:
    return "" if v is None else str(v)

def clean(v: Any, limit: int = 20000) -> str:
    return re.sub(r"\s+", " ", s(v)).strip()[:limit]

def env_load() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(str(BASE / ".env"), override=True)
    except Exception:
        pass

def get_drive_service():
    env_load()
    cid = os.getenv("GDRIVE_CLIENT_ID", "").strip()
    sec = os.getenv("GDRIVE_CLIENT_SECRET", "").strip()
    ref = os.getenv("GDRIVE_REFRESH_TOKEN", "").strip()
    if cid and sec and ref:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        creds = Credentials(
            None,
            refresh_token=<REDACTED_SECRET>
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cid,
            client_secret=<REDACTED_SECRET>
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        creds.refresh(Request())
        return build("drive", "v3", credentials=creds)
    sys.path.insert(0, str(BASE))
    import google_io
    return google_io.get_drive_service()

def drive_account(service) -> str:
    u = service.about().get(fields="user").execute().get("user", {})
    return s(u.get("emailAddress") or u.get("displayName") or "UNKNOWN")

def list_children(service, parent_id: str) -> List[Dict[str, Any]]:
    out = []
    token = <REDACTED_SECRET>
    while True:
        res = service.files().list(
            q=f"'{parent_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,modifiedTime,size,webViewLink,parents),nextPageToken",
            pageSize=1000,
            pageToken=<REDACTED_SECRET>
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        out.extend(res.get("files", []))
        token = <REDACTED_SECRET>"nextPageToken")
        if not token:
            break
    return out

def list_recursive(service, parent_id: str, prefix: str) -> List[Dict[str, Any]]:
    out = []
    for f in list_children(service, parent_id):
        item = dict(f)
        item["_path"] = prefix + "/" + s(f.get("name"))
        out.append(item)
        if f.get("mimeType") == "application/vnd.google-apps.folder":
            out.extend(list_recursive(service, f["id"], item["_path"]))
    return out

def size_ok(meta: Dict[str, Any]) -> bool:
    try:
        size = int(meta.get("size") or 0)
        return size > 0 and size <= MAX_DOWNLOAD
    except Exception:
        return False

def download_bytes(service, meta: Dict[str, Any]) -> bytes:
    from googleapiclient.http import MediaIoBaseDownload
    fid = meta["id"]
    mime = s(meta.get("mimeType"))

    if mime == "application/vnd.google-apps.document":
        req = service.files().export_media(fileId=fid, mimeType="text/plain")
    elif mime == "application/vnd.google-apps.spreadsheet":
        req = service.files().export_media(fileId=fid, mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        req = service.files().get_media(fileId=fid, supportsAllDrives=True)

    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
        if buf.tell() > MAX_DOWNLOAD:
            raise RuntimeError("DOWNLOAD_LIMIT_5MB_EXCEEDED")
    return buf.getvalue()

def classify_domain(name: str, path: str, mime: str) -> str:
    low = f"{name} {path} {mime}".lower()
    if any(x in low for x in ["смет", "estimate", "расцен", "м-80", "м-110", "ареал нева", "фундамент_склад", "крыша и перекр"]):
        return "estimate"
    if any(x in low for x in ["технадзор", "дефект", "акт_", "акт ", "исполнительн"]):
        return "technadzor"
    if any(x in low for x in ["проект", "эскиз", "план участка", "посадк", ".dwg", ".dxf", ".ifc", ".pln", "архитект", "спецификац"]):
        return "design"
    if re.search(r"(^|[^а-яa-z0-9])(ар|кр|кж|кд|км|кмд|ов|вк|эо|эм|эос)([^а-яa-z0-9]|$)", low):
        return "design"
    if mime.startswith("image/"):
        return "design"
    return "other"

def discipline(name: str, path: str, mime: str) -> str:
    low = f"{name} {path}".lower()
    checks = [
        ("AR", ["ар", "архитект"]),
        ("KJ", ["кж", "железобет", "плита"]),
        ("KD", ["кд", "стропил", "дерев"]),
        ("KR", ["кр", "конструктив"]),
        ("KM", ["км", "металл"]),
        ("KMD", ["кмд"]),
        ("OV", ["ов", "отоп", "вентиляц"]),
        ("VK", ["вк", "водоснаб", "канализац"]),
        ("EO", ["эо", "эм", "эос", "электр"]),
        ("SPEC", ["спецификац", "ведом"]),
        ("SKETCH", ["эскиз", ".jpg", ".jpeg", ".png", ".webp"]),
        ("GP", ["план участка", "посадк", "генплан"]),
        ("PLN_MODEL", [".pln", "archicad"]),
        ("IFC_MODEL", [".ifc"]),
        ("CAD", [".dwg", ".dxf"]),
    ]
    for code, keys in checks:
        if any(k in low for k in keys):
            return code
    if mime.startswith("image/"):
        return "SKETCH"
    return "DESIGN"

def estimate_role(name: str, path: str) -> str:
    low = f"{name} {path}".lower()
    if "м-80" in low or "m-80" in low:
        return "m80"
    if "м-110" in low or "m-110" in low:
        return "m110"
    if "крыша" in low or "перекр" in low:
        return "roof_floor"
    if "фундамент" in low:
        return "foundation"
    if "ареал нева" in low:
        return "areal_neva"
    return "estimate_reference"

def analyze_xlsx(raw: bytes) -> Dict[str, Any]:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(raw), data_only=False, read_only=False)
    total = 0
    sheets = []
    for ws in wb.worksheets:
        fc = 0
        mat = 0
        work = 0
        logi = 0
        for row in ws.iter_rows():
            vals = []
            for c in row:
                if c.value is None:
                    continue
                val = str(c.value)
                vals.append(val)
                if val.startswith("="):
                    fc += 1
            rt = " ".join(vals).lower()
            if any(x in rt for x in ["материал", "бетон", "арматур", "газобетон", "кирпич", "доска", "кровл"]):
                mat += 1
            if any(x in rt for x in ["работ", "монтаж", "устройств", "кладк", "вязк"]):
                work += 1
            if any(x in rt for x in ["достав", "логист", "разгруз", "манипулятор", "кран", "транспорт", "прожив"]):
                logi += 1
        total += fc
        sheets.append({"sheet_name": ws.title, "formula_count": fc, "material_hits": mat, "work_hits": work, "logistics_hits": logi})
    return {"formula_total": total, "sheets": sheets}

def analyze_file(service, meta: Dict[str, Any]) -> Dict[str, Any]:
    name = s(meta.get("name"))
    path = s(meta.get("_path"))
    mime = s(meta.get("mimeType"))
    domain = classify_domain(name, path, mime)
    item = {
        "name": name,
        "file_id": s(meta.get("id")),
        "mimeType": mime,
        "path": path,
        "size": s(meta.get("size")),
        "modifiedTime": s(meta.get("modifiedTime")),
        "url": s(meta.get("webViewLink")),
        "domain": domain,
    }
    if meta.get("mimeType") == "application/vnd.google-apps.folder":
        item["domain"] = "folder"
        return item

    if domain == "estimate":
        item["role"] = estimate_role(name, path)
        item["formula_total"] = 0
        item["sheets"] = []
        if (
            name.lower().endswith((".xlsx", ".xlsm", ".xls"))
            or mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            or mime == "application/vnd.google-apps.spreadsheet"
        ):
            if mime == "application/vnd.google-apps.spreadsheet" or size_ok(meta):
                try:
                    item.update(analyze_xlsx(download_bytes(service, meta)))
                except Exception as e:
                    item["extract_error"] = clean(type(e).__name__ + ": " + str(e), 500)
            else:
                item["extract_skipped"] = "SIZE_LIMIT_5MB"
    elif domain == "design":
        item["discipline"] = discipline(name, path, mime)
    elif domain == "technadzor":
        item["role"] = "technadzor_reference"
    return item

def slim(policy: Dict[str, Any]) -> Dict[str, Any]:
    def slim_items(items):
        out = []
        for x in items:
            y = {k: v for k, v in x.items() if k not in {"text_preview", "sample_formulas"}}
            if "sheets" in y:
                y["sheets"] = [
                    {k: sh.get(k) for k in ("sheet_name", "formula_count", "material_hits", "work_hits", "logistics_hits")}
                    for sh in y.get("sheets", [])
                ]
            out.append(y)
        return out
    return {
        "version": policy["version"],
        "status": policy["status"],
        "updated_at": policy["updated_at"],
        "counts": policy["counts"],
        "estimate_references": slim_items(policy["estimate_references"][:40]),
        "design_references": slim_items(policy["design_references"][:80]),
        "technadzor_references": slim_items(policy["technadzor_references"][:40]),
    }

def save_memory(policy: Dict[str, Any]) -> None:
    val = json.dumps(slim(policy), ensure_ascii=False, indent=2)
    ts = now()
    rows = [
        ("owner_reference_full_workflow_v1", 0),
        ("topic_2_estimate_reference_v1", 2),
        ("topic_210_design_reference_v1", 210),
        ("topic_5_technadzor_reference_v1", 5),
    ]
    conn = sqlite3.connect(str(MEMORY_DB))
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(memory)").fetchall()]
        for key, topic_id in rows:
            rec = {
                "id": str(uuid.uuid4()),
                "chat_id": CHAT_ID,
                "key": key,
                "value": val,
                "timestamp": ts,
                "topic_id": topic_id,
                "scope": "topic",
            }
            use = [c for c in ["id", "chat_id", "key", "value", "timestamp", "topic_id", "scope"] if c in cols]
            conn.execute(
                f"INSERT INTO memory({','.join(use)}) VALUES ({','.join(['?'] * len(use))})",
                [rec[c] for c in use],
            )
        conn.commit()
    finally:
        conn.close()

def main() -> int:
    service = get_drive_service()
    account = drive_account(service)
    print("DRIVE_ACCOUNT", account)

    all_items = []
    for label, folder_id in ROOTS.items():
        meta = service.files().get(fileId=folder_id, fields="id,name,mimeType", supportsAllDrives=True).execute()
        print("ROOT_OK", label, meta.get("name"), folder_id)
        for f in list_recursive(service, folder_id, label):
            if f.get("mimeType") == "application/vnd.google-apps.folder":
                continue
            item = analyze_file(service, f)
            all_items.append(item)
            print("INDEXED", item.get("domain"), item.get("name"))

    estimates = [x for x in all_items if x.get("domain") == "estimate"]
    designs = [x for x in all_items if x.get("domain") == "design"]
    technadzor = [x for x in all_items if x.get("domain") == "technadzor"]
    formula_total = sum(int(x.get("formula_total") or 0) for x in estimates)

    counts = {
        "estimate_files": len(estimates),
        "design_files": len(designs),
        "technadzor_files": len(technadzor),
        "formula_total": formula_total,
        "all_files": len(all_items),
    }

    policy = {
        "version": VERSION,
        "status": "ACTIVE",
        "updated_at": now(),
        "drive_account": account,
        "counts": counts,
        "estimate_references": estimates,
        "design_references": designs,
        "technadzor_references": technadzor,
    }

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    old = {}
    if REGISTRY_PATH.exists():
        try:
            old = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            old = {}
    old["owner_reference_full_workflow_v1"] = policy
    old["active"] = VERSION
    old["topic_isolation"] = {"estimate": 2, "technadzor": 5, "design": 210}
    REGISTRY_PATH.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    CANON_PATH.parent.mkdir(parents=True, exist_ok=True)
    CANON_PATH.write_text(
        "# OWNER_REFERENCE_FULL_WORKFLOW_CANON\n\n"
        f"version: {VERSION}\n"
        f"updated_at: {policy['updated_at']}\n\n"
        "Илья — главный канон\n\n"
        "Сметы: М-80, М-110, крыша, фундамент, Ареал Нева — эталон формул и структуры\n\n"
        "Проектирование: АР, КР, КЖ, КД, КМ, КМД, ОВ, ВК, ЭО, ЭМ, ЭОС, эскизы, планы участка — разные разделы, не смешивать\n\n"
        "Технадзор: акты, дефекты, исполнительные — отдельный контур\n\n"
        "Если данных не хватает — один короткий вопрос\n\n"
        f"counts: {json.dumps(counts, ensure_ascii=False)}\n",
        encoding="utf-8",
    )

    save_memory(policy)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "# AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT\n\n"
        f"status: OK\nversion: {VERSION}\nupdated_at: {policy['updated_at']}\n"
        f"estimate_files: {counts['estimate_files']}\n"
        f"design_files: {counts['design_files']}\n"
        f"technadzor_files: {counts['technadzor_files']}\n"
        f"formula_total: {counts['formula_total']}\n",
        encoding="utf-8",
    )

    print("ESTIMATE_FILES", counts["estimate_files"])
    print("DESIGN_FILES", counts["design_files"])
    print("TECHNADZOR_FILES", counts["technadzor_files"])
    print("FORMULA_TOTAL", counts["formula_total"])

    if counts["estimate_files"] < 5:
        raise RuntimeError("ESTIMATE_FILES_LT_5")
    if counts["design_files"] < 10:
        raise RuntimeError("DESIGN_FILES_LT_10")
    if counts["formula_total"] < 3000:
        raise RuntimeError("FORMULA_TOTAL_LT_3000")

    print("AREAL_REFERENCE_FULL_MONOLITH_INDEX_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
# === END_AREAL_REFERENCE_FULL_MONOLITH_V1 ===

====================================================================================================
END_FILE: tools/areal_reference_full_monolith_v1.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/drive_ai_orchestra_root_cleanup_v1.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: a15c2c05d0617a95bf3892e3dd7d85c3daefc4a2594b5a96fc7bea3f65032f87
====================================================================================================
#!/usr/bin/env python3
# === DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1 ===
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

BASE = Path("/root/.areal-neva-core")
ROOT_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
CHAT_FOLDER_NAME = "chat_-1003725299009"
CHAT_ID = "-1003725299009"
TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
REPORT_PATH = BASE / "docs" / "REPORTS" / "DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1_REPORT.md"

CANON_ROOT_FOLDERS = {
    "chat_-1003725299009",
    "ESTIMATES",
    "CANON_FINAL",
    "telegram_exports",
    "CHAT_EXPORTS",
    "_QUARANTINE_ROOT_CLEANUP",
    "AI_ORCHESTRA",
}

TMP_RE = re.compile(r"^tmp[a-z0-9_ -]*\.txt$", re.I)

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def s(v: Any) -> str:
    return "" if v is None else str(v)

def low(v: Any) -> str:
    return s(v).lower().strip()

def env_load() -> None:
    env_path = BASE / ".env"
    try:
        from dotenv import load_dotenv
        load_dotenv(str(env_path), override=True)
        return
    except Exception:
        pass

    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def get_drive_service():
    env_load()

    cid = os.getenv("GDRIVE_CLIENT_ID", "").strip()
    sec = os.getenv("GDRIVE_CLIENT_SECRET", "").strip()
    ref = os.getenv("GDRIVE_REFRESH_TOKEN", "").strip()

    if cid and sec and ref:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = Credentials(
            None,
            refresh_token=<REDACTED_SECRET>
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cid,
            client_secret=<REDACTED_SECRET>
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        creds.refresh(Request())
        return build("drive", "v3", credentials=creds)

    sys.path.insert(0, str(BASE))
    import google_io
    return google_io.get_drive_service()

def q_escape(name: str) -> str:
    return name.replace("\\", "\\\\").replace("'", "\\'")

def list_children(service, parent_id: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    token = <REDACTED_SECRET>
    while True:
        res = service.files().list(
            q=f"'{parent_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,modifiedTime,size,webViewLink,parents),nextPageToken",
            pageSize=1000,
            pageToken=<REDACTED_SECRET>
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        out.extend(res.get("files", []))
        token = <REDACTED_SECRET>"nextPageToken")
        if not token:
            break
    return out

def find_child_folder(service, parent_id: str, name: str) -> str | None:
    res = service.files().list(
        q=f"'{parent_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder' and name='{q_escape(name)}'",
        fields="files(id,name,mimeType,parents)",
        pageSize=20,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None

def ensure_folder(service, parent_id: str, name: str) -> str:
    existing = find_child_folder(service, parent_id, name)
    if existing:
        return existing

    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    created = service.files().create(
        body=meta,
        fields="id,name,parents",
        supportsAllDrives=True,
    ).execute()
    return created["id"]

def drive_about(service) -> str:
    about = service.about().get(fields="user").execute()
    user = about.get("user", {}) or {}
    return s(user.get("emailAddress") or user.get("displayName") or "UNKNOWN")

def parents(f: Dict[str, Any]) -> List[str]:
    return list(f.get("parents") or [])

def move_file(service, f: Dict[str, Any], target_id: str, target_path: str, moves: List[Dict[str, Any]]) -> None:
    fid = f["id"]
    current = parents(f)

    if target_id in current and ROOT_ID not in current:
        return

    remove_parents = ",".join([p for p in current if p == ROOT_ID])
    add_parents = target_id if target_id not in current else ""

    if not remove_parents and not add_parents:
        return

    kwargs = {
        "fileId": fid,
        "fields": "id,name,parents",
        "supportsAllDrives": True,
    }
    if add_parents:
        kwargs["addParents"] = add_parents
    if remove_parents:
        kwargs["removeParents"] = remove_parents

    service.files().update(**kwargs).execute()

    moves.append({
        "file_id": fid,
        "name": f.get("name"),
        "mimeType": f.get("mimeType"),
        "target": target_path,
    })

def classify_target(f: Dict[str, Any], folders: Dict[str, str]) -> Tuple[str, str]:
    name = s(f.get("name"))
    n = low(name)
    mime = s(f.get("mimeType"))
    is_folder = mime == "application/vnd.google-apps.folder"

    if is_folder and name in CANON_ROOT_FOLDERS:
        return "SKIP_CANON_ROOT_FOLDER", ""

    if is_folder and name == "Образцы смет и проектов":
        return folders["design_references"], "chat_-1003725299009/topic_210/PROJECT_DESIGN_REFERENCES"

    if TMP_RE.match(name) or n.startswith("tmp"):
        return folders["quarantine_tmp"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/tmp_txt"

    if n in {"upload_many_compat_v2.txt"} or "compat" in n:
        return folders["quarantine_service"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/service_tmp"

    if "chat_export" in n or "chat export" in n:
        return folders["telegram_exports_root_imports"], "telegram_exports/_ROOT_IMPORTS"

    if n.endswith(".manifest.json") or mime == "application/json":
        if n.startswith("estimate_"):
            return folders["estimate_manifests"], "ESTIMATES/generated/_manifests"
        if "кж_compact_project" in n or "project" in n or "кж" in n:
            return folders["project_manifests"], "chat_-1003725299009/topic_210/PROJECT_ARTIFACTS/_manifests"
        return folders["quarantine_manifests"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/manifests"

    if name in {"М-80.xlsx", "M-80.xlsx", "М-110.xlsx", "M-110.xlsx", "крыша и перекр.xlsx", "фундамент_Склад2.xlsx", "Ареал Нева.xlsx"}:
        return folders["estimate_templates"], "ESTIMATES/templates"

    if n.startswith("estimate_") or "смет" in n:
        if n.endswith(".xlsx") or "spreadsheet" in mime:
            return folders["estimate_generated"], "ESTIMATES/generated"
        if n.endswith(".pdf"):
            return folders["estimate_generated_pdf"], "ESTIMATES/generated/pdf"
        return folders["estimate_generated"], "ESTIMATES/generated"

    if n.startswith("act_") or "акт" in n or "дефект" in n or "технадзор" in n:
        return folders["technadzor"], "chat_-1003725299009/topic_5/TECHNADZOR"

    if (
        "кж_compact_project" in n
        or "проект" in n
        or "project" in n
        or re.search(r"(^|[^а-яa-z])(ар|кр|кж|кд)([^а-яa-z]|$)", n)
        or n.endswith((".dwg", ".dxf", ".pln"))
    ):
        return folders["project_artifacts"], "chat_-1003725299009/topic_210/PROJECT_ARTIFACTS"

    if n.endswith((".docx", ".doc", ".pdf", ".xlsx", ".xls", ".csv", ".txt", ".zip", ".rar", ".7z")):
        return folders["quarantine_unknown_files"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/unknown_files"

    if is_folder:
        return folders["quarantine_unknown_folders"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/unknown_folders"

    return folders["quarantine_unknown_files"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/unknown_files"

def main() -> int:
    service = get_drive_service()
    account = drive_about(service)
    print("DRIVE_ACCOUNT", account)

    root_meta = service.files().get(
        fileId=ROOT_ID,
        fields="id,name,mimeType,trashed,webViewLink",
        supportsAllDrives=True,
    ).execute()
    print("ROOT_OK", root_meta.get("name"), root_meta.get("id"))

    chat = ensure_folder(service, ROOT_ID, CHAT_FOLDER_NAME)
    topic_0 = ensure_folder(service, chat, "topic_0")
    topic_2 = ensure_folder(service, chat, "topic_2")
    topic_5 = ensure_folder(service, chat, "topic_5")
    topic_210 = ensure_folder(service, chat, "topic_210")

    estimates = ensure_folder(service, ROOT_ID, "ESTIMATES")
    canon_final = ensure_folder(service, ROOT_ID, "CANON_FINAL")
    telegram_exports = ensure_folder(service, ROOT_ID, "telegram_exports")
    quarantine = ensure_folder(service, ROOT_ID, "_QUARANTINE_ROOT_CLEANUP")
    quarantine_ts = ensure_folder(service, quarantine, TS)

    folders = {
        "topic_0": topic_0,
        "topic_2": topic_2,
        "topic_5": topic_5,
        "topic_210": topic_210,
        "estimates": estimates,
        "canon_final": canon_final,
        "telegram_exports": telegram_exports,

        "estimate_templates": ensure_folder(service, estimates, "templates"),
        "estimate_generated": ensure_folder(service, estimates, "generated"),
        "estimate_generated_pdf": ensure_folder(service, ensure_folder(service, estimates, "generated"), "pdf"),
        "estimate_manifests": ensure_folder(service, ensure_folder(service, estimates, "generated"), "_manifests"),

        "design_references": ensure_folder(service, topic_210, "PROJECT_DESIGN_REFERENCES"),
        "project_artifacts": ensure_folder(service, topic_210, "PROJECT_ARTIFACTS"),
        "project_manifests": ensure_folder(service, ensure_folder(service, topic_210, "PROJECT_ARTIFACTS"), "_manifests"),

        "technadzor": ensure_folder(service, topic_5, "TECHNADZOR"),

        "telegram_exports_root_imports": ensure_folder(service, telegram_exports, "_ROOT_IMPORTS"),

        "quarantine_tmp": ensure_folder(service, quarantine_ts, "tmp_txt"),
        "quarantine_service": ensure_folder(service, quarantine_ts, "service_tmp"),
        "quarantine_manifests": ensure_folder(service, quarantine_ts, "manifests"),
        "quarantine_unknown_files": ensure_folder(service, quarantine_ts, "unknown_files"),
        "quarantine_unknown_folders": ensure_folder(service, quarantine_ts, "unknown_folders"),
    }

    before = list_children(service, ROOT_ID)
    root_files_before = [x for x in before if x.get("mimeType") != "application/vnd.google-apps.folder"]
    print("ROOT_CHILDREN_BEFORE", len(before))
    print("ROOT_FILES_BEFORE", len(root_files_before))

    moves: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []

    for f in before:
        name = s(f.get("name"))
        target_id, target_path = classify_target(f, folders)

        if target_id == "SKIP_CANON_ROOT_FOLDER":
            skipped.append({"name": name, "reason": "canonical_root_folder"})
            continue

        if not target_id:
            skipped.append({"name": name, "reason": "no_target"})
            continue

        move_file(service, f, target_id, target_path, moves)

    after = list_children(service, ROOT_ID)
    root_files_after = [x for x in after if x.get("mimeType") != "application/vnd.google-apps.folder"]
    noncanonical_root = [
        x for x in after
        if x.get("mimeType") != "application/vnd.google-apps.folder"
        or x.get("name") not in {
            CHAT_FOLDER_NAME,
            "ESTIMATES",
            "CANON_FINAL",
            "telegram_exports",
            "CHAT_EXPORTS",
            "_QUARANTINE_ROOT_CLEANUP",
        }
    ]

    print("ROOT_CHILDREN_AFTER", len(after))
    print("ROOT_FILES_AFTER", len(root_files_after))
    print("MOVED_COUNT", len(moves))
    print("SKIPPED_COUNT", len(skipped))
    print("NONCANONICAL_ROOT_COUNT", len(noncanonical_root))

    for m in moves[:300]:
        print("MOVED", m["name"], "=>", m["target"])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1_REPORT")
    lines.append("")
    lines.append("status: OK")
    lines.append("timestamp: " + now())
    lines.append("drive_account: " + account)
    lines.append("root_id: " + ROOT_ID)
    lines.append("")
    lines.append("## COUNTS")
    lines.append(f"- root_children_before: {len(before)}")
    lines.append(f"- root_files_before: {len(root_files_before)}")
    lines.append(f"- moved_count: {len(moves)}")
    lines.append(f"- skipped_count: {len(skipped)}")
    lines.append(f"- root_children_after: {len(after)}")
    lines.append(f"- root_files_after: {len(root_files_after)}")
    lines.append(f"- noncanonical_root_count: {len(noncanonical_root)}")
    lines.append("")
    lines.append("## CANONICAL FOLDERS")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_0")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_2")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_5")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_210")
    lines.append("- AI_ORCHESTRA/ESTIMATES")
    lines.append("- AI_ORCHESTRA/CANON_FINAL")
    lines.append("- AI_ORCHESTRA/telegram_exports")
    lines.append("- AI_ORCHESTRA/_QUARANTINE_ROOT_CLEANUP")
    lines.append("")
    lines.append("## MOVES")
    for m in moves:
        lines.append(f"- `{m['name']}` -> `{m['target']}`")
    lines.append("")
    lines.append("## SKIPPED")
    for s0 in skipped:
        lines.append(f"- `{s0['name']}`: {s0['reason']}")
    lines.append("")
    lines.append("## NONCANONICAL_ROOT_AFTER")
    for x in noncanonical_root[:200]:
        lines.append(f"- `{x.get('name')}` | `{x.get('mimeType')}` | `{x.get('id')}`")
    lines.append("")
    lines.append("## RAW_JSON")
    lines.append("```json")
    lines.append(json.dumps({
        "status": "OK",
        "timestamp": now(),
        "drive_account": account,
        "root_id": ROOT_ID,
        "counts": {
            "root_children_before": len(before),
            "root_files_before": len(root_files_before),
            "moved_count": len(moves),
            "skipped_count": len(skipped),
            "root_children_after": len(after),
            "root_files_after": len(root_files_after),
            "noncanonical_root_count": len(noncanonical_root),
        },
        "moves": moves,
        "skipped": skipped,
        "noncanonical_root_after": [
            {"id": x.get("id"), "name": x.get("name"), "mimeType": x.get("mimeType")}
            for x in noncanonical_root[:500]
        ],
    }, ensure_ascii=False, indent=2))
    lines.append("```")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if len(root_files_after) > 0:
        print("ROOT_FILES_REMAIN_AFTER_CLEANUP")
        for x in root_files_after[:100]:
            print("ROOT_FILE_LEFT", x.get("name"), x.get("mimeType"), x.get("id"))

    print("REPORT_OK", REPORT_PATH)
    print("DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
# === END_DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1 ===

====================================================================================================
END_FILE: tools/drive_ai_orchestra_root_cleanup_v1.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/dwg_converter_healthcheck.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c69921875c85f57c4825a5c904e331b4e292e547b5262d206ca88f987ca8f854
====================================================================================================
#!/usr/bin/env python3
# === DWG_CONVERTER_HEALTHCHECK_V1 ===
from __future__ import annotations
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "docs/SHARED_CONTEXT/DWG_CONVERTER_STATUS.json"

def main():
    status = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "dwg2dxf": shutil.which("dwg2dxf"),
        "ODAFileConverter": shutil.which("ODAFileConverter") or shutil.which("ODAFileConverter.exe"),
        "geometry_status": "FULL_DWG_GEOMETRY_READY" if (shutil.which("dwg2dxf") or shutil.which("ODAFileConverter") or shutil.which("ODAFileConverter.exe")) else "DWG_METADATA_ONLY_DXF_FULL_PARSE_READY",
        "note": "DXF parses directly. DWG full geometry requires dwg2dxf or ODAFileConverter; without converter DWG metadata path remains active",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False))

if __name__ == "__main__":
    main()
# === END_DWG_CONVERTER_HEALTHCHECK_V1 ===

====================================================================================================
END_FILE: tools/dwg_converter_healthcheck.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/estimate_top_templates_logistics_canon_v4.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 7b41927a49d37b6f8be75db07e21c5f3eea770fa4ea71e5482465318e70af7c8
====================================================================================================
#!/usr/bin/env python3
# === ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4 ===
from __future__ import annotations

import io
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

BASE = Path("/root/.areal-neva-core")
sys.path.insert(0, str(BASE))

AI_ORCHESTRA_FOLDER_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
MEMORY_DB = BASE / "data" / "memory.db"
REGISTRY_PATH = BASE / "config" / "estimate_template_registry.json"
CANON_PATH = BASE / "docs" / "CANON_FINAL" / "ESTIMATE_TEMPLATE_M80_M110_CANON.md"
REPORT_PATH = BASE / "docs" / "REPORTS" / "ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4_REPORT.md"
FORMULA_INDEX_PATH = BASE / "data" / "templates" / "estimate_logic" / "estimate_template_formula_index.json"

TEMPLATES = [
    {"key": "M80", "aliases": ["М-80.xlsx", "M-80.xlsx"], "role": "full_house_estimate_template", "description": "Эталон полной сметы М-80"},
    {"key": "M110", "aliases": ["М-110.xlsx", "M-110.xlsx"], "role": "full_house_estimate_template", "description": "Эталон полной сметы М-110"},
    {"key": "ROOF_FLOORS", "aliases": ["крыша и перекр.xlsx"], "role": "roof_and_floor_estimate_template", "description": "Эталон расчёта кровли и перекрытий"},
    {"key": "FOUNDATION_WAREHOUSE", "aliases": ["фундамент_Склад2.xlsx"], "role": "foundation_estimate_template", "description": "Эталон расчёта фундамента"},
    {"key": "AREAL_NEVA", "aliases": ["Ареал Нева.xlsx"], "role": "general_company_estimate_template", "description": "Общий эталон сметной структуры Ареал-Нева"},
]

SECTION_ORDER = [
    "Фундамент",
    "Каркас",
    "Стены",
    "Перекрытия",
    "Кровля",
    "Окна, двери",
    "Внешняя отделка",
    "Внутренняя отделка",
    "Инженерные коммуникации",
    "Логистика",
    "Накладные расходы",
]

UNIVERSAL_MATERIAL_GROUPS = {
    "стены": ["кирпич", "газобетон", "керамоблок", "арболит", "монолит", "каркас", "брус"],
    "фундамент": ["монолитная плита", "лента", "сваи", "ростверк", "утеплённая плита", "складской фундамент"],
    "кровля": ["металлочерепица", "профнастил", "гибкая черепица", "фальц", "мембрана", "стропильная система"],
    "перекрытия": ["деревянные балки", "монолит", "плиты", "металлические балки"],
    "утепление": ["минвата", "роквул", "пеноплэкс", "pir", "эковата"],
    "отделка": ["имитация бруса", "штукатурка", "плитка", "гкл", "цсп", "фасадная доска"],
    "инженерия": ["электрика", "водоснабжение", "канализация", "отопление", "вентиляция"],
    "логистика": ["доставка", "разгрузка", "манипулятор", "кран", "проживание", "транспорт бригады", "удалённость"],
}

FORMULA_POLICY = [
    "Топовые сметы являются эталонами логики расчёта, а не прайс-листами",
    "Новые сметы считаются по такой же структуре: разделы, строки, колонки, формулы, итоги, примечания, исключения",
    "Материал может быть любым: кирпич, газобетон, каркас, монолит, кровля, перекрытия, отделка, инженерия",
    "При замене материала сохраняется расчётная логика: количество × цена = сумма; работа + материалы = всего; разделы = итоги; финальный итог = сумма разделов",
    "Каркасный сценарий, газобетон/монолитная плита, кровля/перекрытия и фундамент считаются как разные сценарии и не смешиваются",
    "Если объёмов не хватает — оркестр спрашивает только недостающие объёмы",
    "Если пользователь прислал файл как образец — сначала принять как образец, а не запускать поиск цен",
]

PRICE_CONFIRMATION_FLOW = [
    "Интернет-цены материалов и техники не подставляются молча",
    "Для финальной сметы оркестр ищет актуальные цены по материалам, технике, доставке и разгрузке",
    "По каждой позиции показывает: источник, цена, единица, дата/регион, ссылка",
    "Оркестр предлагает среднюю/медианную цену без явных выбросов",
    "Пользователь выбирает: средняя / минимальная / максимальная / конкретная ссылка / ручная цена",
    "Пользователь может добавить наценку, запас, скидку, поправку по позиции, разделу или всей смете",
    "До подтверждения цен финальный XLSX/PDF не выпускается",
    "После подтверждения цены пересчитываются по формулам шаблона",
]

LOGISTICS_POLICY = [
    "Перед финальной сметой оркестр обязан запросить локацию объекта или расстояние от города",
    "Стоимость объекта рядом с городом и объекта за 200 км не может быть одинаковой",
    "Оркестр обязан учитывать доставку материалов, транспорт бригады, разгрузку, манипулятор/кран, проживание, удалённость, дорожные условия",
    "Если логистика неизвестна — оркестр задаёт один короткий вопрос: город/населённый пункт или расстояние от города, подъезд для грузовой техники, нужна ли разгрузка/манипулятор",
    "Логистика считается отдельным блоком сметы или отдельным коэффициентом, но не смешивается молча с ценами материалов",
    "Перед финальным результатом оркестр показывает логистические допущения и спрашивает подтверждение",
]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def s(v: Any) -> str:
    return "" if v is None else str(v)

def clean(v: Any) -> str:
    return re.sub(r"\s+", " ", s(v)).strip()

def get_drive_service():
    from dotenv import load_dotenv
    load_dotenv("/root/.areal-neva-core/.env", override=True)

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    cid = os.getenv("GDRIVE_CLIENT_ID", "").strip()
    sec = os.getenv("GDRIVE_CLIENT_SECRET", "").strip()
    ref = os.getenv("GDRIVE_REFRESH_TOKEN", "").strip()

    if cid and sec and ref:
        creds = Credentials(
            None,
            refresh_token=<REDACTED_SECRET>
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cid,
            client_secret=<REDACTED_SECRET>
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        creds.refresh(Request())
        return build("drive", "v3", credentials=creds)

    import google_io
    return google_io.get_drive_service()

def find_file(service, aliases: List[str]) -> Dict[str, Any]:
    for name in aliases:
        safe_name = name.replace("'", "\\'")
        for q in [
            f"name='{safe_name}' and '{AI_ORCHESTRA_FOLDER_ID}' in parents and trashed=false",
            f"name='{safe_name}' and trashed=false",
        ]:
            res = service.files().list(
                q=q,
                fields="files(id,name,mimeType,modifiedTime,size,webViewLink,parents)",
                pageSize=20,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            ).execute()
            files = res.get("files", [])
            if files:
                files.sort(key=lambda x: x.get("modifiedTime") or "", reverse=True)
                return files[0]
    raise RuntimeError("DRIVE_TEMPLATE_NOT_FOUND_OR_NOT_ACCESSIBLE: " + " / ".join(aliases))

def download_xlsx(service, meta: Dict[str, Any]) -> bytes:
    from googleapiclient.http import MediaIoBaseDownload

    mime = meta.get("mimeType") or ""
    file_id = meta["id"]

    if mime == "application/vnd.google-apps.spreadsheet":
        req = service.files().export_media(
            fileId=file_id,
            mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        req = service.files().get_media(fileId=file_id, supportsAllDrives=True)

    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
    return buf.getvalue()

def row_text(row: List[Any]) -> str:
    return " ".join(clean(x) for x in row if clean(x))

def detect_scenario(text: str, title: str) -> str:
    title_low = (title or "").lower()
    low = (title + " " + text).lower()

    # ВАЖНО: сначала название файла/листа, потому что полные сметы М-80/М-110
    # содержат внутри кровлю и перекрытия, но листы называются "Каркас" и "Газобетон"
    if any(x in title_low for x in ["каркас", "frame"]):
        return "frame_house"

    if any(x in title_low for x in ["газобетон", "газо", "кладка", "masonry"]):
        return "gasbeton_or_masonry_with_monolithic_foundation"

    if any(x in title_low for x in ["фундамент", "склад", "foundation"]):
        return "foundation"

    if any(x in title_low for x in ["крыш", "кров", "перекр", "roof", "floor"]):
        return "roof_and_floors"

    # Потом fallback по содержимому
    if any(x in low for x in ["газобетон", "кладка стен", "арматурного каркаса", "бетон в20", "бетон в22"]):
        return "gasbeton_or_masonry_with_monolithic_foundation"

    if any(x in low for x in ["каркас", "свая винтовая", "свайный фундамент", "обвязка свай", "доска с/к"]):
        return "frame_house"

    if any(x in low for x in ["фундамент", "монолитная плита", "ростверк", "свая", "склад"]):
        if not any(y in low for y in ["кровля", "кровель", "стропил", "перекрыт"]):
            return "foundation"

    if any(x in low for x in ["кров", "стропил", "перекр", "балк"]):
        return "roof_and_floors"

    return "general_estimate"

def extract_formula_cells(ws) -> List[Dict[str, str]]:
    out = []
    for row in ws.iter_rows():
        for c in row:
            val = c.value
            if isinstance(val, str) and val.startswith("="):
                out.append({"sheet": ws.title, "cell": c.coordinate, "formula": val[:500]})
    return out

def extract_structure(ws_values, file_title: str) -> Dict[str, Any]:
    rows = [list(r) for r in ws_values.iter_rows(values_only=True)]
    sections = []
    header_rows = []
    total_rows = []
    sample_rows = []
    material_rows = 0
    work_rows = 0
    logistics_rows = 0

    for i, r in enumerate(rows, start=1):
        txt = row_text(r)
        low = txt.lower()
        if not txt:
            continue

        for sec in SECTION_ORDER:
            if low.strip(" :") == sec.lower() and sec not in sections:
                sections.append(sec)

        if "№ п/п" in txt and ("Наименование" in txt or "Наименование работ" in txt):
            header_rows.append(i)

        if low.startswith("итого") or "итого сметная стоимость" in low or "всего" == low.strip():
            total_rows.append({"row": i, "text": txt[:300]})

        if any(x in low for x in ["логист", "достав", "транспорт", "разгруз", "манипулятор", "кран", "проживан", "удален", "удалён", "км"]):
            logistics_rows += 1

        name = clean(r[1] if len(r) > 1 else "")
        unit = clean(r[2] if len(r) > 2 else "")
        qty = clean(r[3] if len(r) > 3 else "")
        work_price = clean(r[4] if len(r) > 4 else "")
        material_price = clean(r[6] if len(r) > 6 else "")

        if name and (unit or qty):
            if work_price and work_price not in ("0", "0.0", "0,0", "-"):
                work_rows += 1
            if material_price and material_price not in ("0", "0.0", "0,0", "-"):
                material_rows += 1
            if len(sample_rows) < 35:
                sample_rows.append({
                    "row": i,
                    "name": name[:180],
                    "unit": unit,
                    "qty": qty,
                    "work_price": work_price,
                    "material_price": material_price,
                })

    hay = "\n".join(row_text(r) for r in rows[:250])
    return {
        "scenario": detect_scenario(hay, file_title),
        "sections": sections,
        "header_rows": header_rows,
        "total_rows": total_rows[:50],
        "material_rows": material_rows,
        "work_rows": work_rows,
        "logistics_rows": logistics_rows,
        "sample_rows": sample_rows,
        "row_count": len(rows),
    }

def analyze_template(service, template: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
    import openpyxl

    raw = download_xlsx(service, meta)
    wb_formula = openpyxl.load_workbook(io.BytesIO(raw), data_only=False, read_only=False)
    wb_values = openpyxl.load_workbook(io.BytesIO(raw), data_only=True, read_only=True)

    sheets = []
    formula_total = 0
    formula_samples = []

    for ws_f, ws_v in zip(wb_formula.worksheets, wb_values.worksheets):
        formulas = extract_formula_cells(ws_f)
        struct = extract_structure(ws_v, f"{meta.get('name') or ''} {ws_f.title}")
        formula_total += len(formulas)
        formula_samples.extend(formulas[:50])
        sheets.append({
            "sheet_name": ws_f.title,
            "scenario": struct["scenario"],
            "sections": struct["sections"],
            "header_rows": struct["header_rows"],
            "total_rows": struct["total_rows"],
            "material_rows": struct["material_rows"],
            "work_rows": struct["work_rows"],
            "logistics_rows": struct["logistics_rows"],
            "sample_rows": struct["sample_rows"],
            "formula_count": len(formulas),
            "formula_samples": formulas[:30],
            "row_count": struct["row_count"],
        })

    return {
        "key": template["key"],
        "title": meta["name"],
        "template_role": template["role"],
        "description": template["description"],
        "file_id": meta["id"],
        "drive_url": meta.get("webViewLink") or f"https://drive.google.com/file/d/{meta['id']}/view",
        "mimeType": meta.get("mimeType"),
        "modifiedTime": meta.get("modifiedTime"),
        "parents": meta.get("parents") or [],
        "formula_total": formula_total,
        "formula_samples": formula_samples[:120],
        "sheets": sheets,
    }

def build_policy(source_files: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "version": "ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4",
        "status": "ACTIVE_CANON",
        "updated_at": now(),
        "purpose": "Use top estimate files as scalable estimate calculation logic templates with mandatory logistics and web price confirmation",
        "source_files": source_files,
        "canonical_columns": [
            "№ п/п",
            "Наименование",
            "Ед. изм.",
            "Кол-во",
            "Работа Цена",
            "Работа Стоимость",
            "Материалы Цена",
            "Материалы Стоимость",
            "Всего",
            "Примечание",
        ],
        "canonical_sections": SECTION_ORDER,
        "universal_material_groups": UNIVERSAL_MATERIAL_GROUPS,
        "formula_policy": FORMULA_POLICY,
        "price_confirmation_flow": PRICE_CONFIRMATION_FLOW,
        "logistics_policy": LOGISTICS_POLICY,
        "runtime_rule": "ai_router injects this context through core.estimate_template_policy.build_estimate_template_context",
    }

def write_canon(policy: Dict[str, Any]) -> None:
    CANON_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# ESTIMATE_TEMPLATE_TOP_CANON")
    lines.append("")
    lines.append("status: ACTIVE_CANON")
    lines.append("version: ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4")
    lines.append("updated_at: " + policy["updated_at"])
    lines.append("")
    lines.append("## ГЛАВНОЕ")
    lines.append("")
    lines.append("М-80.xlsx, М-110.xlsx, крыша и перекр.xlsx, фундамент_Склад2.xlsx, Ареал Нева.xlsx — топовые эталонные сметы")
    lines.append("Они являются образцами логики построения смет, формул, разделов, колонок, итогов, примечаний и исключений")
    lines.append("Они не являются фиксированным прайсом")
    lines.append("Оркестр обязан переносить их расчётную логику на любые новые задачи и любые материалы")
    lines.append("")
    lines.append("## ЧТО СОХРАНЯТЬ")
    for r in policy["formula_policy"]:
        lines.append("- " + r)
    lines.append("")
    lines.append("## ЦЕНЫ ИЗ ИНТЕРНЕТА")
    for r in policy["price_confirmation_flow"]:
        lines.append("- " + r)
    lines.append("")
    lines.append("## ЛОГИСТИКА И НАКЛАДНЫЕ")
    for r in policy["logistics_policy"]:
        lines.append("- " + r)
    lines.append("")
    lines.append("## КОЛОНКИ")
    lines.append(" | ".join(policy["canonical_columns"]))
    lines.append("")
    lines.append("## РАЗДЕЛЫ")
    for i, sec in enumerate(policy["canonical_sections"], 1):
        lines.append(f"{i}. {sec}")
    lines.append("")
    lines.append("## МАТЕРИАЛЫ")
    for group, values in policy["universal_material_groups"].items():
        lines.append(f"- {group}: " + ", ".join(values))
    lines.append("")
    lines.append("## ПРОЧИТАННЫЕ ШАБЛОНЫ")
    for src in policy["source_files"]:
        lines.append("")
        lines.append(f"### {src['title']}")
        lines.append(f"- role: `{src['template_role']}`")
        lines.append(f"- file_id: `{src['file_id']}`")
        lines.append(f"- drive_url: {src['drive_url']}")
        lines.append(f"- formula_total: {src['formula_total']}")
        for sh in src["sheets"]:
            lines.append(f"  - sheet: {sh['sheet_name']} | scenario={sh['scenario']} | formulas={sh['formula_count']} | material_rows={sh['material_rows']} | work_rows={sh['work_rows']} | logistics_rows={sh['logistics_rows']}")
    lines.append("")
    lines.append("## ОБЯЗАТЕЛЬНОЕ ПОВЕДЕНИЕ")
    lines.append("")
    lines.append("При новой смете оркестр обязан брать структуру и формулы из топовых эталонов")
    lines.append("Оркестр обязан подставлять конкретные объёмы и материалы задачи")
    lines.append("Оркестр обязан запросить локацию/удалённость/доступ/разгрузку до финального расчёта")
    lines.append("Оркестр обязан обновлять цены материалов и логистики через интернет только с подтверждением пользователя")
    lines.append("Оркестр обязан показывать найденные цены, источники, ссылки и среднюю/медианную цену")
    lines.append("Пользователь выбирает цену или задаёт ручную, может добавить наценку/скидку/запас")
    lines.append("Финальный XLSX/PDF запрещён до подтверждения цен и логистики")
    lines.append("")
    CANON_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

def write_registry(policy: Dict[str, Any]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    old = {}
    if REGISTRY_PATH.exists():
        try:
            old = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            old = {}
    old["estimate_top_templates_logistics_canon_v4"] = policy
    old["active_estimate_template_policy"] = "ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4"
    old["estimate_formula_logic_preserve_required"] = True
    old["estimate_material_price_web_refresh_required"] = True
    old["estimate_price_confirmation_required"] = True
    old["estimate_logistics_required"] = True
    old["estimate_final_xlsx_forbidden_before_price_and_logistics_confirmation"] = True
    REGISTRY_PATH.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def write_formula_index(policy: Dict[str, Any]) -> None:
    FORMULA_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    FORMULA_INDEX_PATH.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def save_memory_sqlite(policy: Dict[str, Any]) -> None:
    if not MEMORY_DB.exists():
        raise RuntimeError(f"MEMORY_DB_MISSING: {MEMORY_DB}")

    value = json.dumps(policy, ensure_ascii=False, indent=2)
    ts = now()
    keys = [
        "estimate_top_templates_logistics_canon_v4",
        "topic_0_estimate_top_templates_logistics_canon_v4",
        "topic_2_estimate_top_templates_logistics_canon_v4",
        "topic_210_estimate_top_templates_logistics_canon_v4",
        "estimate_universal_material_calculation_policy_v4",
        "estimate_price_confirmation_required_v4",
        "estimate_logistics_required_v4",
    ]

    conn = sqlite3.connect(str(MEMORY_DB))
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(memory)").fetchall()]
        for key in keys:
            data = {
                "id": str(uuid.uuid4()),
                "chat_id": "-1003725299009",
                "key": key,
                "value": value,
                "timestamp": ts,
                "topic_id": 2,
                "scope": "topic",
            }
            use_cols = [c for c in ["id", "chat_id", "key", "value", "timestamp", "topic_id", "scope"] if c in cols]
            sql = f"INSERT INTO memory({','.join(use_cols)}) VALUES ({','.join(['?'] * len(use_cols))})"
            conn.execute(sql, [data[c] for c in use_cols])
        conn.commit()
    finally:
        conn.close()

def write_report(policy: Dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4_REPORT",
        "",
        "status: OK",
        "updated_at: " + policy["updated_at"],
        "canon: docs/CANON_FINAL/ESTIMATE_TEMPLATE_M80_M110_CANON.md",
        "registry: config/estimate_template_registry.json",
        "formula_index: data/templates/estimate_logic/estimate_template_formula_index.json",
        "",
        "## CLOSED",
        "- top estimate templates resolved from Drive",
        "- XLSX formulas extracted",
        "- universal material logic registered",
        "- web price confirmation registered",
        "- logistics and overhead clarification registered",
        "- direct sqlite memory write completed",
        "- ai_router context hook enabled",
        "",
        "## RAW_POLICY",
        "```json",
        json.dumps(policy, ensure_ascii=False, indent=2),
        "```",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    service = get_drive_service()
    about = service.about().get(fields="user").execute()
    print("DRIVE_ACCOUNT", about.get("user", {}).get("emailAddress"))

    source_files = []
    for template in TEMPLATES:
        meta = find_file(service, template["aliases"])
        print("TEMPLATE_FOUND", template["key"], meta.get("name"), meta.get("id"), meta.get("parents"))
        source_files.append(analyze_template(service, template, meta))

    if not source_files:
        raise RuntimeError("NO_TEMPLATES_ANALYZED")

    policy = build_policy(source_files)
    write_canon(policy)
    write_registry(policy)
    write_formula_index(policy)
    save_memory_sqlite(policy)
    write_report(policy)

    print("ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4_OK")
    for src in source_files:
        print("SOURCE", src["title"], src["file_id"], "role", src["template_role"], "formulas", src["formula_total"])
        for sh in src["sheets"]:
            print("SHEET", sh["sheet_name"], sh["scenario"], "formulas", sh["formula_count"], "materials", sh["material_rows"], "works", sh["work_rows"], "logistics", sh["logistics_rows"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
# === END_ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4 ===

====================================================================================================
END_FILE: tools/estimate_top_templates_logistics_canon_v4.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/final_session_code_tail_verify.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 7cd72b9a9b65a65ec55a53196a1a6b8fbdc7c8f57485fe391c1b42374adc7aa4
====================================================================================================
#!/usr/bin/env python3
# === FINAL_SESSION_CODE_TAIL_VERIFY_V4_FILE_MEMORY_PUBLIC ===
from __future__ import annotations

import asyncio
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/root/.areal-neva-core")
sys.path.insert(0, str(BASE))

REPORT = BASE / "docs" / "REPORTS" / "FINAL_SESSION_CODE_TAIL_VERIFY_REPORT.md"
CORE_DB = BASE / "data" / "core.db"

BAD_ROUTE_IMPORT = "from core.model_router import " + "route_domain"
BAD_FINAL_IMPORT = "from core.final_closure_engine import " + "handle_final_closure"
BAD_PRICE_SYMBOL = "prehandle_price_" + "decision_v1"

REQUIRED_MARKERS = {
    "task_worker.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_TASK_WORKER_HOOK",
        "END_FULL_TECH_CONTOUR_CLOSE_V1_WIRED",
        "ACTIVE_DIALOG_STATE_V1_TASK_WORKER_HOOK",
        "VOICE_CONFIRM_AWAITING_V1",
    ],
    "core/file_memory_bridge.py": [
        "FILE_MEMORY_PUBLIC_OUTPUT_DOMAIN_FILTER_V6_FINAL_SESSION",
        "_fm_item_domain",
        "_fm_public_links",
        "_fm_public_title",
    ],
    "core/output_sanitizer.py": [
        "UNIFIED_USER_OUTPUT_SANITIZER_V5_STRICT_PUBLIC_CLEAN",
        "sanitize_user_output",
        "sanitize_project_message",
        "sanitize_estimate_message",
    ],
    "core/price_enrichment.py": [
        "PRICE_DECISION_BEFORE_WEB_SEARCH_V1",
        "prehandle_price_task_v1",
        "_base_prehandle_price_task_v1",
    ],
    "core/file_context_intake.py": [
        "PENDING_INTENT_CLARIFICATION_V1",
        "PROJECT_SAMPLE_TEXT_INTAKE_V1",
    ],
    "core/final_closure_engine.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_ENGINE",
        "FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3",
        "maybe_handle_final_closure",
    ],
    "core/model_router.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_MODEL_ROUTER",
        "detect_domain",
    ],
    "core/runtime_file_catalog.py": ["FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG"],
    "core/archive_guard.py": ["FINAL_CLOSURE_BLOCKER_FIX_V1_ARCHIVE_DUPLICATE_GUARD"],
    "core/technadzor_engine.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_TECHNADZOR_ENGINE",
        "TECHNADZOR_PUBLIC_MESSAGE_NO_LOCAL_PATH_V1",
    ],
    "core/ocr_engine.py": [
        "FINAL_CLOSURE_BLOCKER_FIX_V1_OCR_TABLE_ENGINE",
        "OCR_TABLE_REQUIRES_REAL_RECOGNITION_ENGINE",
    ],
    "core/estimate_engine.py": ["create_estimate_xlsx_from_rows"],
    "core/sheets_generator.py": ["USER_ENTERED"],
}

def run(cmd):
    try:
        return subprocess.check_output(cmd, cwd=str(BASE), text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return "ERROR: " + str(e)

def read(rel):
    p = BASE / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def line_no(rel, needle):
    for i, line in enumerate(read(rel).splitlines(), 1):
        if needle in line:
            return i
    return -1

def marker_check():
    out = {}
    for rel, markers in REQUIRED_MARKERS.items():
        txt = read(rel)
        missing = [m for m in markers if m not in txt]
        out[rel] = {"exists": bool(txt), "missing": missing, "ok": bool(txt) and not missing}
    return out

def public_def_count(rel, prefix):
    return sum(1 for line in read(rel).splitlines() if line.startswith(prefix))

def exact_bad_import_present(import_line, files):
    return any(import_line in read(x) for x in files)

def smoke_check():
    res = {}

    from core.model_router import detect_domain
    rc = {
        "estimate": detect_domain("сделай смету по образцу").get("domain"),
        "estimate_inflected": detect_domain("сделай смету").get("domain"),
        "technadzor": detect_domain("сделай акт технадзора").get("domain"),
        "memory": detect_domain("какие файлы я скидывал").get("domain"),
        "project": detect_domain("сделай проект КЖ плиты").get("domain"),
    }
    res["router_cases"] = rc
    res["router_ok"] = (rc["estimate"] == "estimate" and rc["estimate_inflected"] == "estimate"
        and rc["technadzor"] == "technadzor" and rc["memory"] == "memory" and rc["project"] == "project")

    from core.file_memory_bridge import _fm_item_domain, _fm_public_links, _fm_public_title
    project_item = {
        "file_name": "4. АР АК-М-160.pdf",
        "direction": "TECHNADZOR_ACT_GOST_SP",
        "summary": "акт технадзора",
        "value": "blob https://docs.google.com/spreadsheets/d/BAD/edit",
        "links": ["https://drive.google.com/file/d/REAL/view?usp=drivesdk"],
    }
    res["file_memory_domain_project_ok"] = _fm_item_domain(project_item) == "project"
    res["file_memory_title_ok"] = _fm_public_title(project_item) == "АР АК-М-160.pdf"
    res["file_memory_links_only_item_ok"] = _fm_public_links(project_item) == ["https://drive.google.com/file/d/REAL/view?usp=drivesdk"]
    res["file_memory_no_blob_link_ok"] = _fm_public_links({"file_name": "КЖ.pdf", "links": []}) == []

    from core.output_sanitizer import sanitize_user_output
    dirty = "MANIFEST:\nhttps://drive.google.com/file/d/M/view\nDrive file_id: abc\nКратко: {\"task_id\":\"bad\"}\n/root/.areal-neva-core/tmp\nНормальный текст"
    clean = sanitize_user_output(dirty)
    res["sanitizer_public_ok"] = (
        "MANIFEST" not in clean and "file_id" not in clean.lower()
        and "task_id" not in clean.lower() and "/root/" not in clean
        and "Нормальный текст" in clean
    )

    from core.price_enrichment import prehandle_price_task_v1
    price_res = asyncio.run(prehandle_price_task_v1(sqlite3.connect(":memory:"), {
        "id": "v", "chat_id": "-1", "topic_id": 2, "input_type": "text", "raw_input": "смета",
    }))
    res["price_function_exists"] = callable(prehandle_price_task_v1)
    res["price_function_result_type_ok"] = price_res is None or isinstance(price_res, dict)

    from core.final_closure_engine import maybe_handle_final_closure
    mc = sqlite3.connect(str(CORE_DB))
    mc.row_factory = sqlite3.Row
    try:
        mr = maybe_handle_final_closure(mc, {
            "id": "v", "chat_id": "-1003725299009", "topic_id": 2,
            "input_type": "text", "raw_input": "какие файлы я скидывал",
        }, "v", "-1003725299009", 2, "какие файлы я скидывал", "text", None)
    finally:
        mc.close()
    mm = (mr or {}).get("message", "")
    res["final_closure_memory_ok"] = bool(mr and mr.get("handled"))
    res["final_closure_public_ok"] = (
        "MANIFEST" not in mm and "DXF:" not in mm and "file_id" not in mm.lower()
        and "task=" not in mm.lower() and "Кратко:" not in mm and "/root/" not in mm
    )

    from core.estimate_engine import create_estimate_xlsx_from_rows
    res["estimate_xlsx_function_ok"] = callable(create_estimate_xlsx_from_rows)

    from core.technadzor_engine import process_technadzor
    tech = process_technadzor(text="акт технадзора", task_id="v", chat_id="-1", topic_id=2)
    res["technadzor_public_message_ok"] = bool(tech.get("handled")) and "/root/" not in str(tech.get("message", ""))

    res["google_sheets_user_entered_ok"] = "USER_ENTERED" in read("core/sheets_generator.py")
    res["ocr_real_not_closed_fact"] = "OCR_TABLE_REQUIRES_REAL_RECOGNITION_ENGINE" in read("core/ocr_engine.py")
    dwg = run(["bash", "-lc", "command -v odafileconverter || command -v dwg2dxf || true"])
    res["dwg_converter_present"] = bool(dwg.strip())

    return res

def main():
    verify_files = ["tools/final_session_code_tail_verify.py", "tools/live_tech_contour_verify.py"]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git": {
            "head": run(["git", "rev-parse", "--short", "HEAD"]),
            "origin": run(["git", "rev-parse", "--short", "origin/main"]),
            "ahead_behind": run(["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"]),
            "status": run(["git", "status", "--short"]),
        },
        "markers": marker_check(),
        "hook_order": {
            "full_end": line_no("task_worker.py", "END_FULL_TECH_CONTOUR_CLOSE_V1_WIRED"),
            "final_hook": line_no("task_worker.py", "FINAL_CLOSURE_BLOCKER_FIX_V1_TASK_WORKER_HOOK"),
            "active_dialog": line_no("task_worker.py", "ACTIVE_DIALOG_STATE_V1_TASK_WORKER_HOOK"),
        },
        "counts": {
            "public_prehandle_price_task_v1": public_def_count("core/price_enrichment.py", "async def prehandle_price_task_v1"),
            "base_prehandle_price_task_v1": public_def_count("core/price_enrichment.py", "async def _base_prehandle_price_task_v1"),
            "create_estimate_xlsx_from_rows": public_def_count("core/estimate_engine.py", "def create_estimate_xlsx_from_rows"),
            "prehandle_task_context_v1": public_def_count("core/file_context_intake.py", "def prehandle_task_context_v1"),
        },
        "forbidden": {
            "telegram_daemon_dirty": bool(run(["git", "status", "--short", "--", "telegram_daemon.py"])),
            "final_closure_has_voice_handler_def": (
                "def handle_voice_confirm" in read("core/final_closure_engine.py")
                or "def voice_confirm" in read("core/final_closure_engine.py")
            ),
            "wrong_route_import": exact_bad_import_present(BAD_ROUTE_IMPORT, verify_files),
            "wrong_final_closure_import": exact_bad_import_present(BAD_FINAL_IMPORT, verify_files),
            "wrong_price_symbol": any(BAD_PRICE_SYMBOL in read(x) for x in verify_files + ["core/price_enrichment.py"]),
        },
        "smoke": smoke_check(),
    }

    report["markers_ok"] = all(v.get("ok") for v in report["markers"].values())
    report["hook_order_ok"] = (
        report["hook_order"]["full_end"] > 0
        and report["hook_order"]["final_hook"] > report["hook_order"]["full_end"]
        and report["hook_order"]["final_hook"] < report["hook_order"]["active_dialog"]
    )
    report["counts_ok"] = (
        report["counts"]["public_prehandle_price_task_v1"] == 1
        and report["counts"]["base_prehandle_price_task_v1"] == 1
        and report["counts"]["create_estimate_xlsx_from_rows"] == 1
        and report["counts"]["prehandle_task_context_v1"] == 2
    )
    report["forbidden_ok"] = not any(report["forbidden"].values())
    required_smoke = [
        "router_ok", "file_memory_domain_project_ok", "file_memory_title_ok",
        "file_memory_links_only_item_ok", "file_memory_no_blob_link_ok",
        "sanitizer_public_ok", "price_function_exists", "price_function_result_type_ok",
        "final_closure_memory_ok", "final_closure_public_ok",
        "estimate_xlsx_function_ok", "technadzor_public_message_ok", "google_sheets_user_entered_ok",
    ]
    report["smoke_ok"] = all(bool(report["smoke"].get(k)) for k in required_smoke)
    report["status"] = "OK" if (
        report["markers_ok"] and report["hook_order_ok"]
        and report["counts_ok"] and report["forbidden_ok"] and report["smoke_ok"]
    ) else "FAILED"

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# FINAL_SESSION_CODE_TAIL_VERIFY_REPORT", "",
        f"generated_at: {report['generated_at']}",
        f"status: {report['status']}",
        f"markers_ok: {report['markers_ok']}",
        f"hook_order_ok: {report['hook_order_ok']}",
        f"counts_ok: {report['counts_ok']}",
        f"forbidden_ok: {report['forbidden_ok']}",
        f"smoke_ok: {report['smoke_ok']}", "",
        "## RAW_JSON", "```json",
        json.dumps(report, ensure_ascii=False, indent=2),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("STATUS", report["status"])
    if report["status"] != "OK":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
# === END_FINAL_SESSION_CODE_TAIL_VERIFY_V4_FILE_MEMORY_PUBLIC ===

====================================================================================================
END_FILE: tools/final_session_code_tail_verify.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/live_canon_test_runner.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 4086fa3c6738a509a59a1901c1c5628394a66b03c0001f3298eadefac488b033
====================================================================================================
#!/usr/bin/env python3
# === LIVE_CANON_TEST_RUNNER_V1 ===
from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
REPORT = BASE / "docs/REPORTS/LIVE_CANON_TEST_REPORT.md"

# === LIVE_CANON_TEST_RUNNER_PYTHONPATH_FIX_V1 ===
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
# === END_LIVE_CANON_TEST_RUNNER_PYTHONPATH_FIX_V1 ===

def ok(name, value):
    return {"name": name, "ok": bool(value), "value": value}

async def main():
    checks = []

    from core.engine_contract import validate_engine_result
    checks.append(ok("UNIFIED_ENGINE_RESULT_VALIDATOR_BAD", not validate_engine_result("файл скачан", input_type="drive_file").get("ok")))
    checks.append(ok("UNIFIED_ENGINE_RESULT_VALIDATOR_GOOD", validate_engine_result({"summary": "PDF создан", "drive_link": "https://drive.google.com/test"}, input_type="drive_file").get("ok")))

    from core.format_registry import classify_file
    checks.append(ok("DWG_KIND_DRAWING", classify_file("a.dwg").get("kind") == "drawing"))
    checks.append(ok("DXF_KIND_DRAWING", classify_file("a.dxf").get("kind") == "drawing"))
    checks.append(ok("HF_KIND_BINARY", classify_file("a.hf").get("kind") == "binary"))

    from core.template_workflow import _load_index
    checks.append(ok("TEMPLATE_INDEX_LOAD", isinstance(_load_index(), dict)))

    from core.normative_source_engine import search_normative_sources
    checks.append(ok("NORMATIVE_SOURCE_SEARCH", len(search_normative_sources("трещина бетон")) >= 1))

    from core.capability_router_dispatch import build_execution_plan
    checks.append(ok("CAPABILITY_ESTIMATE", build_execution_plan(user_text="смета xlsx").get("engine") == "estimate"))
    checks.append(ok("CAPABILITY_DWG", build_execution_plan(file_name="a.dwg").get("engine") == "dwg_project"))

    passed = sum(1 for c in checks if c["ok"])
    total = len(checks)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "# LIVE_CANON_TEST_REPORT\n\n"
        + f"created_at: {datetime.now(timezone.utc).isoformat()}\n"
        + f"passed: {passed}/{total}\n\n"
        + "\n".join(f"- [{'OK' if c['ok'] else 'FAIL'}] {c['name']} | {c['value']}" for c in checks)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": passed == total, "passed": passed, "total": total, "report": str(REPORT)}, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
# === END_LIVE_CANON_TEST_RUNNER_V1 ===

====================================================================================================
END_FILE: tools/live_canon_test_runner.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/live_tech_contour_verify.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2403577feb80f4ce69d57be3363e08c6df898876d487211bb91929367d68a7f1
====================================================================================================
#!/usr/bin/env python3
# === LIVE_TECH_CONTOUR_VERIFY_V2 ===
from __future__ import annotations

import asyncio
import json
import sys
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/root/.areal-neva-core")
# === TOOL_IMPORT_PATH_FIX_V1 ===
BASE_PATH = Path("/root/.areal-neva-core")
if str(BASE_PATH) not in sys.path:
    sys.path.insert(0, str(BASE_PATH))
# === END_TOOL_IMPORT_PATH_FIX_V1 ===

CORE_DB = BASE / "data" / "core.db"
MEM_DB = BASE / "data" / "memory.db"
REPORT = BASE / "docs" / "REPORTS" / "LIVE_TECH_CONTOUR_VERIFY_REPORT.md"

REQUIRED_MARKERS = {
    "task_worker.py": [
        "FULL_TECH_CONTOUR_CLOSE_V1_WIRED",
        "REMAINING_TECH_CONTOUR_CLOSE_V1_WIRED",
        "_send_once_UNIFIED_USER_OUTPUT_SANITIZER_V1",
        "_send_once_ex_UNIFIED_USER_OUTPUT_SANITIZER_V1",
    ],
    "core/file_context_intake.py": [
        "CONTEXT_AWARE_FILE_INTAKE_V1",
        "MULTI_FILE_TEMPLATE_INTAKE_V1",
        "TELEGRAM_FILE_MEMORY_INDEX_V1",
        "PENDING_INTENT_CLARIFICATION_V1",
    ],
    "core/price_enrichment.py": [
        "WEB_SEARCH_PRICE_ENRICHMENT_V1",
        "PRICE_CONFIRMATION_BEFORE_ESTIMATE_V1",
        "PRICE_DECISION_BEFORE_WEB_SEARCH_V1",
    ],
    "core/pdf_spec_extractor.py": ["PDF_SPEC_EXTRACTOR_REAL_V1"],
    "core/upload_retry_queue.py": ["ROOT_TMP_UPLOAD_GUARD_V1"],
    "core/drive_folder_resolver.py": ["DRIVE_CANON_FOLDER_RESOLVER_V1"],
    "core/topic_drive_oauth.py": ["DRIVE_CANON_SINGLE_FOLDER_PICK_V1"],
    "core/output_sanitizer.py": ["UNIFIED_USER_OUTPUT_SANITIZER_V1"],
    "core/reply_repeat_parent.py": ["REPLY_REPEAT_PARENT_TASK_V1"],
    "core/project_route_guard.py": [
        "PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1",
        "PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1",
    ],
    "core/project_engine.py": [
        "PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1_WRAPPER",
        "PROJECT_ENGINE_FALLBACK_SHEET_REGISTER_V1",
    ],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read(path: str) -> str:
    p = BASE / path
    return p.read_text(encoding="utf-8") if p.exists() else ""


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=str(BASE), text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return f"ERROR: {e}"


def check_markers() -> dict:
    out = {}
    for path, markers in REQUIRED_MARKERS.items():
        txt = read(path)
        out[path] = {
            "exists": bool(txt),
            "missing": [m for m in markers if m not in txt],
            "ok": bool(txt) and all(m in txt for m in markers),
        }
    return out


def clear_smoke_memory(chat: str) -> None:
    if not MEM_DB.exists():
        return
    conn = sqlite3.connect(str(MEM_DB))
    try:
        conn.execute("DELETE FROM memory WHERE chat_id=?", (chat,))
        conn.commit()
    finally:
        conn.close()


async def smoke_async() -> dict:
    result = {}
    chat = "SMOKE_PENDING_INTENT_CLARIFICATION_V2"
    topic = 990002
    clear_smoke_memory(chat)

    try:
        from core.output_sanitizer import sanitize_user_output
        dirty = "Engine: X\nPDF: https://drive.google.com/file/d/abc/view\n/tmp/a.xlsx\nMANIFEST: hidden"
        clean = sanitize_user_output(dirty)
        result["sanitizer"] = {
            "ok": "Engine:" not in clean and "/tmp/" not in clean and "drive.google.com" in clean,
            "clean": clean,
        }
    except Exception as e:
        result["sanitizer"] = {"ok": False, "error": repr(e)}

    try:
        from core.reply_repeat_parent import _is_short_human_reply, _is_repeat, _is_status
        result["reply_repeat"] = {
            "ok": _is_short_human_reply("ответишь?") and _is_repeat("повтори") and _is_status("ну что"),
        }
    except Exception as e:
        result["reply_repeat"] = {"ok": False, "error": repr(e)}

    try:
        from core.project_route_guard import is_explicit_project_intent
        result["project_route"] = {
            "ok": is_explicit_project_intent("Сделай проект монолитной фундаментной плиты КЖ") and not is_explicit_project_intent("сделай смету по монолитным работам"),
        }
    except Exception as e:
        result["project_route"] = {"ok": False, "error": repr(e)}

    try:
        from core.file_context_intake import _detect_pending_file_intent, _save_pending_intent, prehandle_task_context_v1
        pending = _detect_pending_file_intent("сейчас скину несколько смет как образцы, цены материалов через интернет")
        ok_pending = bool(pending and pending.get("kind") == "estimate" and pending.get("price_mode") == "web_confirm")
        _save_pending_intent(chat, topic, pending)
        conn = sqlite3.connect(":memory:")
        task = {
            "id": "smoke_pending",
            "chat_id": chat,
            "topic_id": topic,
            "input_type": "text",
            "raw_input": "Ну ты должен не сразу искать в интернете, сначала спроси нужно ли это",
            "reply_to_message_id": 1,
        }
        res = prehandle_task_context_v1(conn, task)
        result["pending_intent_clarification"] = {
            "ok": ok_pending and bool(res and res.get("handled") and res.get("history") == "PENDING_INTENT_CLARIFICATION_V1:UPDATED"),
            "result": res,
        }
    except Exception as e:
        result["pending_intent_clarification"] = {"ok": False, "error": repr(e)}

    try:
        from core.price_enrichment import prehandle_price_task_v1
        conn = sqlite3.connect(":memory:")
        task2 = {
            "id": "smoke_price_ask",
            "chat_id": chat,
            "topic_id": topic,
            "input_type": "text",
            "raw_input": "сделай смету по образцу",
            "reply_to_message_id": 2,
        }
        res2 = await prehandle_price_task_v1(conn, task2)
        task3 = {
            "id": "smoke_price_yes",
            "chat_id": chat,
            "topic_id": topic,
            "input_type": "text",
            "raw_input": "да, искать актуальные цены",
            "reply_to_message_id": 3,
        }
        res3 = await prehandle_price_task_v1(conn, task3)
        result["price_decision_before_web_search"] = {
            "ok": bool(res2 and res2.get("state") == "WAITING_CLARIFICATION" and res3 and "найду актуальные цены" in res3.get("message", "")),
            "ask": res2,
            "yes": res3,
        }
    except Exception as e:
        result["price_decision_before_web_search"] = {"ok": False, "error": repr(e)}

    try:
        from core.pdf_spec_extractor import extract_spec
        result["pdf_extractor_import"] = {"ok": callable(extract_spec)}
    except Exception as e:
        result["pdf_extractor_import"] = {"ok": False, "error": repr(e)}

    clear_smoke_memory(chat)
    return result


def db_stats() -> dict:
    conn = sqlite3.connect(str(CORE_DB))
    conn.row_factory = sqlite3.Row
    try:
        state_counts = [dict(r) for r in conn.execute("SELECT state, COUNT(*) cnt FROM tasks GROUP BY state ORDER BY cnt DESC").fetchall()]
        topic2 = [dict(r) for r in conn.execute("""
            SELECT rowid, substr(id,1,8) id, state, input_type,
                   COALESCE(bot_message_id,'') bot_msg,
                   COALESCE(reply_to_message_id,'') reply_to,
                   substr(raw_input,1,180) raw,
                   substr(result,1,180) result,
                   substr(error_message,1,120) err,
                   updated_at
            FROM tasks
            WHERE COALESCE(topic_id,0)=2
            ORDER BY rowid DESC
            LIMIT 20
        """).fetchall()]
    finally:
        conn.close()
    return {"state_counts": state_counts, "topic2_latest": topic2}


def memory_stats() -> dict:
    if not MEM_DB.exists():
        return {"exists": False, "count": 0, "rows": []}
    conn = sqlite3.connect(str(MEM_DB))
    conn.row_factory = sqlite3.Row
    try:
        rows = [dict(r) for r in conn.execute("""
            SELECT chat_id,key,substr(value,1,260) value,timestamp
            FROM memory
            WHERE key LIKE '%pending_file_intent%'
               OR key LIKE '%price_mode%'
               OR key LIKE '%price_decision%'
               OR key LIKE '%telegram_file_catalog_summary%'
               OR key LIKE '%telegram_file_duplicates_summary%'
               OR key LIKE '%estimate_template_batch%'
            ORDER BY rowid DESC
            LIMIT 100
        """).fetchall()]
    finally:
        conn.close()
    return {"exists": True, "count": len(rows), "rows": rows}


def git_info() -> dict:
    return {
        "head": run(["git", "rev-parse", "--short", "HEAD"]),
        "last": run(["git", "log", "-1", "--pretty=format:%h %ci %s"]),
        "status": run(["git", "status", "--short"]),
    }


def service_info() -> dict:
    return {
        "areal-task-worker": run(["systemctl", "is-active", "areal-task-worker"]),
        "telegram-ingress": run(["systemctl", "is-active", "telegram-ingress"]),
        "areal-memory-api": run(["systemctl", "is-active", "areal-memory-api"]),
        "areal-upload-retry": run(["systemctl", "is-active", "areal-upload-retry.service"]),
    }


def write_report(payload: dict) -> None:
    lines = []
    lines.append("# LIVE_TECH_CONTOUR_VERIFY_REPORT")
    lines.append("")
    lines.append(f"generated_at: {payload['generated_at']}")
    lines.append("")
    lines.append("## GIT")
    lines.append(f"head: {payload['git']['head']}")
    lines.append(f"last: {payload['git']['last']}")
    lines.append("")
    lines.append("## SERVICES")
    for k, v in payload["services"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## CODE MARKERS")
    for path, res in payload["markers"].items():
        lines.append(f"- {path}: {'OK' if res['ok'] else 'MISSING'}")
        if res["missing"]:
            lines.append(f"  missing: {', '.join(res['missing'])}")
    lines.append("")
    lines.append("## SMOKE")
    for name, res in payload["smoke"].items():
        lines.append(f"- {name}: {'OK' if res.get('ok') else 'FAIL'}")
        if res.get("error"):
            lines.append(f"  error: {res.get('error')}")
    lines.append("")
    lines.append("## FINAL STATUS")
    lines.append(f"markers_ok: {payload['markers_ok']}")
    lines.append(f"smoke_ok: {payload['smoke_ok']}")
    lines.append(f"services_ok: {payload['services_ok']}")
    lines.append("status: CODE_INSTALLED_AND_INTERNAL_VERIFY_OK" if payload["markers_ok"] and payload["smoke_ok"] and payload["services_ok"] else "status: VERIFY_FAILED")
    lines.append("")
    lines.append("## RAW_JSON")
    lines.append("```json")
    lines.append(json.dumps(payload, ensure_ascii=False, indent=2))
    lines.append("```")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


async def main_async() -> int:
    payload = {
        "generated_at": now(),
        "git": git_info(),
        "services": service_info(),
        "markers": check_markers(),
        "smoke": await smoke_async(),
        "db": db_stats(),
        "memory": memory_stats(),
        "live_required_before_verified": [
            "real Telegram pending intent",
            "real Telegram clarification",
            "real Telegram file batch samples",
            "real duplicate Telegram file",
            "real web price search confirmation",
            "real project KZH end-to-end",
            "real voice confirm",
            "real technadzor act",
            "real DWG/DXF conversion",
        ],
    }
    payload["markers_ok"] = all(x["ok"] for x in payload["markers"].values())
    payload["smoke_ok"] = all(x.get("ok") for x in payload["smoke"].values())
    payload["services_ok"] = all(v == "active" for v in payload["services"].values())
    write_report(payload)

    print("LIVE_TECH_CONTOUR_VERIFY_REPORT", REPORT)
    print("MARKERS_OK", payload["markers_ok"])
    print("SMOKE_OK", payload["smoke_ok"])
    print("SERVICES_OK", payload["services_ok"])

    if not (payload["markers_ok"] and payload["smoke_ok"] and payload["services_ok"]):
        print("FAILED_SMOKE_OR_MARKERS")
        for name, res in payload["smoke"].items():
            if not res.get("ok"):
                print("FAILED_SMOKE", name, json.dumps(res, ensure_ascii=False)[:1000])
        return 1
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(main_async()))


if __name__ == "__main__":
    main()

====================================================================================================
END_FILE: tools/live_tech_contour_verify.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/pending_intent_backfill.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 35f4cc391a3f2c169f50adb7d9fd0d10605bc602d8eade0263858eb354ead369
====================================================================================================
#!/usr/bin/env python3
# === PENDING_INTENT_BACKFILL_V1 ===
from __future__ import annotations

import json
import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/root/.areal-neva-core")
# === TOOL_IMPORT_PATH_FIX_V1 ===
BASE_PATH = Path("/root/.areal-neva-core")
if str(BASE_PATH) not in sys.path:
    sys.path.insert(0, str(BASE_PATH))
# === END_TOOL_IMPORT_PATH_FIX_V1 ===

CORE_DB = BASE / "data" / "core.db"
REPORT = BASE / "docs" / "REPORTS" / "PENDING_INTENT_BACKFILL_REPORT.md"
REPORT.parent.mkdir(parents=True, exist_ok=True)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def s(v) -> str:
    return "" if v is None else str(v).strip()


def default_chat() -> str:
    return os.getenv("TELEGRAM_CHAT_ID") or "-1003725299009"


def main() -> None:
    from core.file_context_intake import (
        _detect_pending_file_intent,
        _save_pending_intent,
        _memory_write,
        _pic_is_clarification_text,
        _pic_update_intent_with_clarification,
    )

    conn = sqlite3.connect(str(CORE_DB))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT rowid,id,chat_id,COALESCE(topic_id,0) topic_id,input_type,raw_input,state,result,error_message,updated_at
        FROM tasks
        WHERE input_type IN ('text','voice')
        ORDER BY rowid ASC
        """
    ).fetchall()
    conn.close()

    latest_pending = {}
    saved = []
    clarifications = []

    for r in rows:
        chat_id = s(r["chat_id"]) or default_chat()
        topic_id = int(r["topic_id"] or 0)
        text = s(r["raw_input"])

        pending = _detect_pending_file_intent(text)
        if pending:
            pending["source_task_id"] = s(r["id"])
            pending["source_rowid"] = int(r["rowid"])
            pending["source_updated_at"] = s(r["updated_at"])
            pending["backfilled_at"] = now()
            latest_pending[(chat_id, topic_id)] = pending
            _save_pending_intent(chat_id, topic_id, pending)
            saved.append({
                "rowid": int(r["rowid"]),
                "task_id": s(r["id"])[:8],
                "chat_id": chat_id,
                "topic_id": topic_id,
                "raw": text[:160],
                "pending": pending,
            })
            continue

        key = (chat_id, topic_id)
        if key in latest_pending and _pic_is_clarification_text(text):
            updated = _pic_update_intent_with_clarification(latest_pending[key], text)
            updated["clarification_source_task_id"] = s(r["id"])
            updated["clarification_source_rowid"] = int(r["rowid"])
            updated["backfilled_at"] = now()
            latest_pending[key] = updated
            _save_pending_intent(chat_id, topic_id, updated)
            if updated.get("price_mode"):
                _memory_write(chat_id, f"topic_{topic_id}_price_mode", updated.get("price_mode"))
            _memory_write(chat_id, f"topic_{topic_id}_pending_file_intent_clarification", {
                "task_id": s(r["id"]),
                "rowid": int(r["rowid"]),
                "text": text,
                "updated_intent": updated,
                "created_at": now(),
            })
            clarifications.append({
                "rowid": int(r["rowid"]),
                "task_id": s(r["id"])[:8],
                "chat_id": chat_id,
                "topic_id": topic_id,
                "raw": text[:180],
                "price_mode": updated.get("price_mode"),
            })

    report = {
        "engine": "PENDING_INTENT_BACKFILL_V1",
        "generated_at": now(),
        "saved_pending_count": len(saved),
        "clarification_count": len(clarifications),
        "saved_pending": saved[-30:],
        "clarifications": clarifications[-30:],
    }

    lines = [
        "# PENDING_INTENT_BACKFILL_REPORT",
        "",
        f"generated_at: {report['generated_at']}",
        f"saved_pending_count: {report['saved_pending_count']}",
        f"clarification_count: {report['clarification_count']}",
        "",
        "## CLARIFICATIONS",
    ]
    for x in report["clarifications"]:
        lines.append(f"- rowid={x['rowid']} task={x['task_id']} topic={x['topic_id']} price_mode={x.get('price_mode')} raw={x['raw']}")
    lines.append("")
    lines.append("## RAW_JSON")
    lines.append("```json")
    lines.append(json.dumps(report, ensure_ascii=False, indent=2))
    lines.append("```")
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("PENDING_INTENT_BACKFILL_V1_OK")
    print("SAVED_PENDING", len(saved))
    print("CLARIFICATIONS", len(clarifications))
    print("REPORT", REPORT)


if __name__ == "__main__":
    main()

====================================================================================================
END_FILE: tools/pending_intent_backfill.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/secret_scan.sh
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 856289e8e62f28a33a5f18e89281d9e2ea7d4e2a719ea885fd98ad2fdf8bd822
====================================================================================================
#!/bin/bash
# Паттерны хранятся отдельно чтобы скрипт не сканировал сам себя
PATTERN_FILE="/root/.areal-neva-core/.secret_patterns"

if [ ! -f "$PATTERN_FILE" ]; then
  echo "SECRET_SCAN_SKIP: pattern file not found"
  exit 0
fi

FOUND=0
while IFS= read -r line; do
  [[ "$line" =~ ^\+ ]] || continue
  while IFS= read -r pattern; do
    if echo "$line" | grep -qE "$pattern"; then
      echo "SECRET FOUND: $pattern"
      FOUND=1
    fi
  done < "$PATTERN_FILE"
done < <(git diff --cached)

[ $FOUND -eq 1 ] && echo "ABORT: секреты в коммите" && exit 1
echo "SECRET_SCAN_OK"
exit 0

====================================================================================================
END_FILE: tools/secret_scan.sh
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/telegram_drive_memory_sync.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 709499280bfa62924330e117bdbca8807d1247ea2cd7ee5d2dfdd15e74e5689c
====================================================================================================
#!/usr/bin/env python3
# === TELEGRAM_DRIVE_MEMORY_SYNC_V2 ===
from __future__ import annotations

import json
import os
import re
import sqlite3
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
CORE_DB = BASE / "data/core.db"
MEM_DB = BASE / "data/memory.db"

# === SYNC_SELF_PYTHONPATH_FIX_V1 ===
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
# === END SYNC_SELF_PYTHONPATH_FIX_V1 ===

from core.file_memory_bridge import (
    is_service_file,
    classify_file_direction,
    save_file_catalog_snapshot,
)

CHAT_ID_DEFAULT = "-1003725299009"

def utc():
    return datetime.now(timezone.utc).isoformat()

def conn(path):
    c = sqlite3.connect(str(path), timeout=20)
    c.row_factory = sqlite3.Row
    return c

def has_table(c, name):
    return c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (name,)).fetchone() is not None

def safe_json(text):
    try:
        return json.loads(text or "{}")
    except Exception:
        return {}

def clean(text, limit=50000):
    if text is None:
        return ""
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False)
    return text.replace("\r", "\n").strip()[:limit]

def ensure_memory_table(mem):
    mem.execute("CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
    mem.execute("CREATE INDEX IF NOT EXISTS idx_memory_chat_key_sync_v2 ON memory(chat_id,key)")

def upsert_memory(mem, chat_id, key, value):
    value = clean(value, 50000)
    mid = hashlib.sha1(f"{chat_id}:{key}".encode()).hexdigest()
    mem.execute("DELETE FROM memory WHERE chat_id=? AND key=?", (chat_id, key))
    mem.execute(
        "INSERT OR REPLACE INTO memory (id,chat_id,key,value,timestamp) VALUES (?,?,?,?,?)",
        (mid, chat_id, key, value, utc()),
    )

def main():
    if not CORE_DB.exists() or not MEM_DB.exists():
        print("SYNC_SKIP: DB_MISSING")
        return 0

    indexed = 0
    skipped = 0
    topics = set()

    with conn(CORE_DB) as core, conn(MEM_DB) as mem:
        if not has_table(core, "tasks"):
            print("SYNC_SKIP: TASKS_MISSING")
            return 0

        ensure_memory_table(mem)

        rows = core.execute(
            """
            SELECT id,chat_id,COALESCE(topic_id,0) AS topic_id,input_type,state,raw_input,result,updated_at,created_at
            FROM tasks
            WHERE input_type='drive_file'
               OR COALESCE(result,'') LIKE '%drive.google%'
               OR COALESCE(result,'') LIKE '%docs.google%'
               OR COALESCE(raw_input,'') LIKE '%.xlsx%'
               OR COALESCE(raw_input,'') LIKE '%.xls%'
               OR COALESCE(raw_input,'') LIKE '%.pdf%'
               OR COALESCE(raw_input,'') LIKE '%.docx%'
               OR COALESCE(raw_input,'') LIKE '%.jpg%'
               OR COALESCE(raw_input,'') LIKE '%.png%'
            ORDER BY updated_at DESC
            LIMIT 800
            """
        ).fetchall()

        for r in rows:
            chat_id = str(r["chat_id"] or CHAT_ID_DEFAULT)
            topic_id = int(r["topic_id"] or 0)
            if topic_id == 0:
                skipped += 1
                continue

            raw = clean(r["raw_input"], 50000)
            result = clean(r["result"], 50000)
            data = safe_json(raw)
            file_name = str(data.get("file_name") or "")
            source = str(data.get("source") or "")
            file_id = str(data.get("file_id") or "")

            # === SYNC_REAL_FILE_REF_FILTER_V2 ===
            _sync_hay = raw + "\n" + result
            _sync_links = re.findall(r"https?://\S+", _sync_hay)
            _sync_has_real_file_ref = bool(
                file_id
                or file_name
                or _sync_links
                or re.search(r"\.(xlsx|xls|csv|pdf|docx|doc|jpg|jpeg|png|heic|webp|dwg|dxf)\b", _sync_hay, re.I)
                or "drive.google" in _sync_hay
                or "docs.google" in _sync_hay
            )
            if not _sync_has_real_file_ref:
                skipped += 1
                continue
            # === END SYNC_REAL_FILE_REF_FILTER_V2 ===

            if is_service_file(file_name, source, topic_id, raw):
                skipped += 1
                continue

            direction = classify_file_direction(raw + "\n" + result, file_name, str(data.get("mime_type") or ""))
            payload = {
                "task_id": r["id"],
                "chat_id": chat_id,
                "topic_id": topic_id,
                "input_type": r["input_type"],
                "state": r["state"],
                "file_id": file_id,
                "file_name": file_name,
                "mime_type": data.get("mime_type") or "",
                "caption": data.get("caption") or "",
                "source": source or "core.db",
                "direction": direction,
                "result": result[:12000],
                "updated_at": r["updated_at"],
                "created_at": r["created_at"],
            }

            key = f"topic_{topic_id}_file_{r['id']}"
            upsert_memory(mem, chat_id, key, json.dumps(payload, ensure_ascii=False))
            indexed += 1
            topics.add((chat_id, topic_id))

        mem.commit()

    catalogs = 0
    for chat_id, topic_id in sorted(topics):
        res = save_file_catalog_snapshot(chat_id, topic_id)
        if res.get("ok"):
            catalogs += 1

    print(json.dumps({
        "ok": True,
        "indexed": indexed,
        "skipped": skipped,
        "catalogs": catalogs,
        "version": "TELEGRAM_DRIVE_MEMORY_SYNC_V2",
    }, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
# === END TELEGRAM_DRIVE_MEMORY_SYNC_V2 ===

====================================================================================================
END_FILE: tools/telegram_drive_memory_sync.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/telegram_file_memory_backfill.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e0490e5da460851785a7eb8c54aafc42289af24399375c39e3218c3f09aa55fe
====================================================================================================
#!/usr/bin/env python3
# === TELEGRAM_FILE_MEMORY_BACKFILL_V1 ===
from __future__ import annotations

import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE = Path("/root/.areal-neva-core")
CORE_DB = BASE / "data" / "core.db"
MEM_DB = BASE / "data" / "memory.db"
CATALOG_DIR = BASE / "data" / "telegram_file_catalog"
TEMPLATE_DIR = BASE / "data" / "templates"
ESTIMATE_DIR = TEMPLATE_DIR / "estimate"
ESTIMATE_BATCH_DIR = TEMPLATE_DIR / "estimate_batch"
REPORT_PATH = BASE / "docs" / "REPORTS" / "TELEGRAM_FILE_MEMORY_BACKFILL_REPORT.md"

CATALOG_DIR.mkdir(parents=True, exist_ok=True)
ESTIMATE_BATCH_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    return str(v).strip()


def safe_key(v: Any) -> str:
    raw = s(v)
    out = []
    for ch in raw:
        if ch.isalnum() or ch in "-_":
            out.append(ch)
        else:
            out.append("_")
    return ("".join(out).strip("_") or "unknown")[:120]


def jloads(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    txt = s(raw)
    if not txt:
        return {}
    try:
        obj = json.loads(txt)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def is_service_file(payload: Dict[str, Any], state: str = "", err: str = "") -> bool:
    name = s(payload.get("file_name")).lower()
    src = s(payload.get("source")).lower()
    state = s(state).upper()
    err = s(err).upper()

    if src in {"google_drive", "drive", "service", "healthcheck", "drive_sync"}:
        return True
    if name.startswith("tmp") and name.endswith(".txt"):
        return True
    if "SERVICE_FILE_IGNORED" in err:
        return True
    if "healthcheck" in name or "retry_hc" in name:
        return True
    return False


def memory_cols(conn: sqlite3.Connection) -> List[str]:
    try:
        return [r[1] for r in conn.execute("PRAGMA table_info(memory)").fetchall()]
    except Exception:
        return []


def memory_write(chat_id: str, key: str, value: Any) -> None:
    if not MEM_DB.exists():
        return
    conn = sqlite3.connect(str(MEM_DB))
    try:
        cols = memory_cols(conn)
        if not cols:
            return
        payload = json.dumps(value, ensure_ascii=False, indent=2) if not isinstance(value, str) else value
        ts = now()
        if "id" in cols:
            mid = hashlib.sha1(f"{chat_id}:{key}:{ts}:{payload[:200]}".encode("utf-8")).hexdigest()
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


def read_drive_file_tasks() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(str(CORE_DB))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT
              rowid,
              id,
              chat_id,
              COALESCE(topic_id,0) AS topic_id,
              input_type,
              state,
              raw_input,
              result,
              error_message,
              bot_message_id,
              reply_to_message_id,
              created_at,
              updated_at
            FROM tasks
            WHERE input_type='drive_file'
            ORDER BY rowid ASC
            """
        ).fetchall()
    finally:
        conn.close()

    out = []
    for r in rows:
        payload = jloads(r["raw_input"])
        if is_service_file(payload, r["state"], r["error_message"]):
            continue
        file_id = s(payload.get("file_id"))
        file_name = s(payload.get("file_name"))
        if not file_id and not file_name:
            continue
        out.append(
            {
                "rowid": r["rowid"],
                "task_id": s(r["id"]),
                "chat_id": s(r["chat_id"]),
                "topic_id": int(r["topic_id"] or 0),
                "state": s(r["state"]),
                "file_id": file_id,
                "file_name": file_name,
                "mime_type": s(payload.get("mime_type")),
                "caption": s(payload.get("caption")),
                "source": s(payload.get("source") or "telegram"),
                "telegram_message_id": payload.get("telegram_message_id"),
                "bot_message_id": r["bot_message_id"],
                "reply_to_message_id": r["reply_to_message_id"],
                "created_at": s(r["created_at"]),
                "updated_at": s(r["updated_at"]),
            }
        )
    return out


def write_catalog(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    grouped: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}
    for rec in records:
        grouped.setdefault((rec["chat_id"], rec["topic_id"]), []).append(rec)

    topic_reports = {}
    for (chat_id, topic_id), rows in grouped.items():
        path = CATALOG_DIR / f"chat_{safe_key(chat_id)}__topic_{topic_id}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        by_file: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            key = row.get("file_id") or f"name:{row.get('file_name')}"
            by_file.setdefault(key, []).append(row)

        dups = [v for v in by_file.values() if len(v) > 1]
        summary = {
            "engine": "TELEGRAM_FILE_MEMORY_BACKFILL_V1",
            "chat_id": chat_id,
            "topic_id": topic_id,
            "catalog_path": str(path),
            "file_count": len(rows),
            "unique_file_count": len(by_file),
            "duplicate_group_count": len(dups),
            "latest_files": rows[-20:],
            "duplicate_groups": [
                {
                    "file_id": group[0].get("file_id"),
                    "file_name": group[0].get("file_name"),
                    "count": len(group),
                    "task_ids": [x.get("task_id") for x in group[-10:]],
                    "latest_updated_at": group[-1].get("updated_at"),
                }
                for group in dups[-50:]
            ],
            "updated_at": now(),
        }

        topic_reports[f"{chat_id}:{topic_id}"] = summary
        memory_write(chat_id, f"topic_{topic_id}_telegram_file_catalog_summary", summary)
        if summary["duplicate_group_count"]:
            memory_write(chat_id, f"topic_{topic_id}_telegram_file_duplicates_summary", summary["duplicate_groups"])

    master = {
        "engine": "TELEGRAM_FILE_MEMORY_BACKFILL_V1",
        "total_file_records": len(records),
        "topic_count": len(grouped),
        "topics": topic_reports,
        "updated_at": now(),
    }
    (CATALOG_DIR / "index.json").write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
    return master


def parse_template_name(path: Path) -> Dict[str, Any]:
    name = path.name
    chat_id = ""
    topic_id = 0

    marker = "chat_"
    if marker in name:
        part = name.split(marker, 1)[1]
        if "__topic_" in part:
            chat_id = part.split("__topic_", 1)[0]
            rest = part.split("__topic_", 1)[1]
            raw_topic = ""
            for ch in rest:
                if ch.isdigit() or ch == "-":
                    raw_topic += ch
                else:
                    break
            try:
                topic_id = int(raw_topic or 0)
            except Exception:
                topic_id = 0

    return {"chat_id": chat_id, "topic_id": topic_id}


def backfill_template_batches() -> Dict[str, Any]:
    templates = []
    if ESTIMATE_DIR.exists():
        for p in sorted(ESTIMATE_DIR.glob("*.json")):
            if p.name.startswith("ACTIVE_BATCH__"):
                continue
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            meta = parse_template_name(p)
            chat_id = s(data.get("chat_id") or meta.get("chat_id"))
            topic_id = int(data.get("topic_id") or meta.get("topic_id") or 0)
            if not chat_id:
                continue
            data["chat_id"] = chat_id
            data["topic_id"] = topic_id
            data.setdefault("engine", "TEMPLATE_BATCH_BACKFILL_V1")
            data.setdefault("backfilled_at", now())
            templates.append(data)

    grouped: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}
    for t in templates:
        grouped.setdefault((t["chat_id"], int(t["topic_id"] or 0)), []).append(t)

    reports = {}
    for (chat_id, topic_id), rows in grouped.items():
        batch = {
            "engine": "TEMPLATE_BATCH_BACKFILL_V1",
            "chat_id": chat_id,
            "topic_id": topic_id,
            "count": len(rows),
            "templates": rows[-100:],
            "updated_at": now(),
        }
        batch_path = ESTIMATE_BATCH_DIR / f"ACTIVE_BATCH__chat_{safe_key(chat_id)}__topic_{topic_id}.json"
        batch_path.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")
        memory_write(chat_id, f"topic_{topic_id}_estimate_template_batch", batch)
        reports[f"{chat_id}:{topic_id}"] = {"batch_path": str(batch_path), "count": len(rows)}

    return {"engine": "TEMPLATE_BATCH_BACKFILL_V1", "total_templates": len(templates), "topics": reports, "updated_at": now()}


def write_report(master: Dict[str, Any], templates: Dict[str, Any]) -> None:
    lines = []
    lines.append("# TELEGRAM_FILE_MEMORY_BACKFILL_REPORT")
    lines.append("")
    lines.append(f"generated_at: {now()}")
    lines.append("")
    lines.append("## TELEGRAM FILE CATALOG")
    lines.append(f"total_file_records: {master.get('total_file_records')}")
    lines.append(f"topic_count: {master.get('topic_count')}")
    lines.append("")
    for key, val in sorted((master.get("topics") or {}).items()):
        lines.append(f"### {key}")
        lines.append(f"file_count: {val.get('file_count')}")
        lines.append(f"unique_file_count: {val.get('unique_file_count')}")
        lines.append(f"duplicate_group_count: {val.get('duplicate_group_count')}")
        lines.append(f"catalog_path: {val.get('catalog_path')}")
        lines.append("")
    lines.append("## TEMPLATE BATCH BACKFILL")
    lines.append(f"total_templates: {templates.get('total_templates')}")
    for key, val in sorted((templates.get("topics") or {}).items()):
        lines.append(f"- {key}: count={val.get('count')} path={val.get('batch_path')}")
    lines.append("")
    lines.append("## STATUS")
    lines.append("TELEGRAM_FILE_MEMORY_BACKFILL_V1_DONE")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    records = read_drive_file_tasks()
    master = write_catalog(records)
    templates = backfill_template_batches()
    write_report(master, templates)

    print("TELEGRAM_FILE_MEMORY_BACKFILL_V1_OK")
    print("TOTAL_FILE_RECORDS", master.get("total_file_records"))
    print("TOPIC_COUNT", master.get("topic_count"))
    print("TOTAL_TEMPLATES", templates.get("total_templates"))
    print("REPORT", REPORT_PATH)


if __name__ == "__main__":
    main()

====================================================================================================
END_FILE: tools/telegram_file_memory_backfill.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/telegram_history_full_backfill.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d03b26f2a1f6c79a6e4120c028c1e29082e0bcd5cad0681d3c273d783ee4496f
====================================================================================================
#!/usr/bin/env python3
# === TELEGRAM_HISTORY_FULL_BACKFILL_V1 ===
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
CORE_DB = BASE / "data/core.db"
MEM_DB = BASE / "data/memory.db"
REPORT = BASE / "docs/REPORTS/TELEGRAM_HISTORY_FULL_BACKFILL_REPORT.json"

def _s(v, limit=5000):
    return "" if v is None else str(v)[:limit]

def main():
    if not CORE_DB.exists() or not MEM_DB.exists():
        print(json.dumps({"ok": False, "error": "DB_NOT_FOUND"}, ensure_ascii=False))
        return

    core = sqlite3.connect(CORE_DB)
    core.row_factory = sqlite3.Row
    mem = sqlite3.connect(MEM_DB)

    rows = core.execute(
        """
        SELECT id, chat_id, COALESCE(topic_id,0) AS topic_id, input_type, raw_input, result, state, created_at, updated_at
        FROM tasks
        WHERE raw_input LIKE '%file_id%'
           OR raw_input LIKE '%file_name%'
           OR result LIKE '%drive.google%'
           OR result LIKE '%docs.google%'
           OR result LIKE '%.xlsx%'
           OR result LIKE '%.pdf%'
           OR result LIKE '%.docx%'
           OR input_type IN ('drive_file','file','document','photo','image')
        ORDER BY updated_at DESC
        LIMIT 5000
        """
    ).fetchall()

    indexed = 0
    catalogs = {}
    now = datetime.now(timezone.utc).isoformat()

    for r in rows:
        chat_id = _s(r["chat_id"])
        topic_id = int(r["topic_id"] or 0)
        key = f"topic_{topic_id}_history_file_{r['id']}"
        value = {
            "schema": "TELEGRAM_HISTORY_FULL_BACKFILL_V1",
            "task_id": r["id"],
            "chat_id": chat_id,
            "topic_id": topic_id,
            "input_type": r["input_type"],
            "state": r["state"],
            "raw_input": _s(r["raw_input"], 3000),
            "result": _s(r["result"], 3000),
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        }
        mem.execute(
            "INSERT INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,?)",
            (chat_id, key, json.dumps(value, ensure_ascii=False), now),
        )
        catalogs.setdefault((chat_id, topic_id), []).append(value)
        indexed += 1

    for (chat_id, topic_id), items in catalogs.items():
        mem.execute(
            "INSERT INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,?)",
            (
                chat_id,
                f"topic_{topic_id}_file_catalog_history_backfill",
                json.dumps({"schema": "TELEGRAM_HISTORY_FULL_BACKFILL_V1", "count": len(items), "items": items[:100]}, ensure_ascii=False),
                now,
            ),
        )

    mem.commit()
    core.close()
    mem.close()

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ok": True, "indexed": indexed, "catalogs": len(catalogs), "created_at": now}
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))

if __name__ == "__main__":
    main()
# === END_TELEGRAM_HISTORY_FULL_BACKFILL_V1 ===

====================================================================================================
END_FILE: tools/telegram_history_full_backfill.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/upload_retry_unified_worker.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 45992958e34bc05b156972d97caab2e3aa948f9c9e7a728ab008c5363cdb4df4
====================================================================================================
#!/usr/bin/env python3
# === UPLOAD_RETRY_QUEUE_UNIFICATION_V1_WORKER ===
from __future__ import annotations
import json, os, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
DB = BASE / "data/core.db"

def main():
    if not DB.exists():
        print(json.dumps({"ok": False, "error": "DB_NOT_FOUND"}))
        return
    conn = sqlite3.connect(DB, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS upload_retry_queue(
        id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, task_id TEXT,
        topic_id INTEGER, kind TEXT, attempts INTEGER DEFAULT 0,
        last_error TEXT, created_at TEXT DEFAULT (datetime('now')), last_attempt TEXT)""")
    conn.commit()
    rows = conn.execute(
        "SELECT * FROM upload_retry_queue WHERE COALESCE(attempts,0)<5 ORDER BY id ASC LIMIT 25"
    ).fetchall()
    done = failed = 0
    for r in rows:
        rid = r["id"]
        path = str(r["path"] or "")
        task_id = str(r["task_id"] or "")
        topic_id = int(r["topic_id"] or 0)
        kind = str(r["kind"] or "artifact")
        link = ""
        try:
            if not path or not os.path.exists(path):
                raise RuntimeError("FILE_NOT_FOUND")
            from core.engine_base import upload_artifact_to_drive
            link = upload_artifact_to_drive(path, task_id, topic_id) or ""
            if not link:
                from core.engine_base import _telegram_fallback_send
                link = _telegram_fallback_send(path, task_id, topic_id) or ""
            if not link:
                raise RuntimeError("NO_LINK")
            row = conn.execute("SELECT result FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row:
                old = row[0] or ""
                new_line = f"{kind} retry OK: {link}"
                if new_line not in old:
                    conn.execute("UPDATE tasks SET result=?,updated_at=datetime('now') WHERE id=?",
                                 ((old+"\n"+new_line).strip(), task_id))
            conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                         (task_id, f"UPLOAD_RETRY_QUEUE_UNIFICATION_V1:OK:{link}"))
            conn.execute("DELETE FROM upload_retry_queue WHERE id=?", (rid,))
            done += 1
        except Exception as e:
            conn.execute(
                "UPDATE upload_retry_queue SET attempts=COALESCE(attempts,0)+1,last_error=?,last_attempt=? WHERE id=?",
                (str(e), datetime.now(timezone.utc).isoformat(), rid),
            )
            failed += 1
        conn.commit()
    conn.close()
    print(json.dumps({"ok": True, "processed": len(rows), "done": done, "failed": failed}))

if __name__ == "__main__":
    main()
# === END_UPLOAD_RETRY_QUEUE_UNIFICATION_V1_WORKER ===

====================================================================================================
END_FILE: tools/upload_retry_unified_worker.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: .gitignore
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 27f77ed6e29ab513436857a58d17609602acec48a503a0629e587302adb7b4e3
====================================================================================================
*.pyc
__pycache__/
.env
*.log
*.bak
runtime/*
!runtime/.gitkeep
*.bak.*
*.broken.*
.venv/
data/*.db
data/*.db-*
data/memory/
data/memory_files/
data/source_registry.db
sessions/
logs/
runtime/
credentials.json
token.json
.env.*
*.session
*.session-journal
core.db
*.safe.*
data/*.safe.*
task_worker.py.bak_*
*.bak_*
backups/
*.broken*
data/*.backup*
data/project_templates_bak*/
data/telegram_file_catalog/
data/templates/estimate_batch/
outputs/
data/templates/estimate_logic/
data/templates/reference_monolith/
data/templates/design_logic/
data/price_quotes/
.secret_patterns
tools/*.bak_*
docs/SHARED_CONTEXT/*.bak_*
core/*.bak_*

====================================================================================================
END_FILE: .gitignore
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 410a003b00b8a0d4cb71e8249ce2fba39ddf21ae76a26bc32d5ea370b0ab2517
====================================================================================================
# ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.md

Статус: базовое рабочее ядро оркестра через OpenRouter

## Контур
Telegram -> telegram_daemon.py -> core.db -> task_worker.py -> core/ai_router.py -> OpenRouter -> Telegram

## Память
memory_api_server.py -> data/memory.db

## Ключевые файлы
- telegram_daemon: /root/.areal-neva-core/telegram_daemon.py
- task_worker: /root/.areal-neva-core/task_worker.py
- ai_router: /root/.areal-neva-core/core/ai_router.py
- memory_api_server: /root/.areal-neva-core/memory_api_server.py
- core_db: /root/.areal-neva-core/data/core.db
- memory_db: /root/.areal-neva-core/data/memory.db

## Процессы
```
931211 /root/.areal-neva-core/.venv/bin/python3 -u /root/.areal-neva-core/memory_api_server.py
931217 /root/.areal-neva-core/.venv/bin/python3 -u /root/.areal-neva-core/telegram_daemon.py
934122 .venv/bin/python3 -u task_worker.py
939864 /bin/sh -c pgrep -af 'memory_api_server.py|telegram_daemon.py|task_worker.py' || true
```

## Git
- branch: fatal: not a git repository (or any of the parent directories): .git
- commit: fatal: not a git repository (or any of the parent directories): .git

## Memory
- rows: 3
- export: ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.memory.json

## Последние задачи
```json
[
  {
    "id": "14d0fefb-ecb0-4ce2-9e56-8fbbd9dc546b",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Всё в порядке, спасибо. А у тебя?",
    "error_message": null,
    "reply_to_message_id": 2795,
    "created_at": "2026-04-11T13:57:16.333447+00:00",
    "updated_at": "2026-04-11T13:57:17.465609+00:00"
  },
  {
    "id": "a51d0e33-bf9f-42be-bc3a-0ae2c7d2ccbf",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "Как настроение всё ли в порядке?",
    "state": "DONE",
    "result": "Настроение нормальное, всё в порядке. А у тебя?",
    "error_message": null,
    "reply_to_message_id": 2793,
    "created_at": "2026-04-11T13:57:04.883321+00:00",
    "updated_at": "2026-04-11T13:57:06.373296+00:00"
  },
  {
    "id": "a4c08fda-eaa7-428f-9575-1bd8bd8d7600",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Понял, готов отвечать.",
    "error_message": null,
    "reply_to_message_id": 2791,
    "created_at": "2026-04-11T13:56:51.395517+00:00",
    "updated_at": "2026-04-11T13:56:53.152799+00:00"
  },
  {
    "id": "fd6a77c5-1d85-4f62-bf45-ead1d76c0cbd",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Hello! How can I assist you today?",
    "error_message": null,
    "reply_to_message_id": 2789,
    "created_at": "2026-04-11T13:41:11.612250+00:00",
    "updated_at": "2026-04-11T13:41:18.307618+00:00"
  },
  {
    "id": "9ca9f754-eb00-4959-be75-0a11672418c9",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "Hello! How can I assist you today?",
    "error_message": null,
    "reply_to_message_id": 2787,
    "created_at": "2026-04-11T13:40:55.751820+00:00",
    "updated_at": "2026-04-11T13:40:57.070533+00:00"
  },
  {
    "id": "8a2c53a3-e9c4-43c6-b8c4-32a73a9eb603",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "",
    "state": "DONE",
    "result": "It seems you might have intended to provide more context or a specific question. How can I assist you today?",
    "error_message": null,
    "reply_to_message_id": 2785,
    "created_at": "2026-04-11T13:40:34.152693+00:00",
    "updated_at": "2026-04-11T13:40:40.956432+00:00"
  },
  {
    "id": "b1abbf1b-a698-4cbb-bc02-db807d320c60",
    "chat_id": -1003725299009,
    "user_id": 2061134525,
    "input_type": "text",
    "raw_input": "тест",
    "state": "DONE",
    "result": "Привет! Как я могу помочь вам сегодня?",
    "error_message": null,
    "reply_to_message_id": 2783,
    "created_at": "2026-04-11T13:40:20.148758+00:00",
    "updated_at": "2026-04-11T13:40:21.554233+00:00"
  }
]
```

====================================================================================================
END_FILE: ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.memory.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 1b7e37c5f348dc06d787b53bca85926fe19a115a15de5cedbfab783df29fe41d
====================================================================================================
{
  "snapshot_name": "ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.memory.json",
  "snapshot_type": "orchestra_base_core_openrouter_working",
  "date": "2026-04-11T17:20:32+03:00",
  "git": {
    "branch": "fatal: not a git repository (or any of the parent directories): .git",
    "commit": "fatal: not a git repository (or any of the parent directories): .git",
    "status_short": "fatal: not a git repository (or any of the parent directories): .git"
  },
  "processes": "931211 /root/.areal-neva-core/.venv/bin/python3 -u /root/.areal-neva-core/memory_api_server.py\n931217 /root/.areal-neva-core/.venv/bin/python3 -u /root/.areal-neva-core/telegram_daemon.py\n934122 .venv/bin/python3 -u task_worker.py\n939864 /bin/sh -c pgrep -af 'memory_api_server.py|telegram_daemon.py|task_worker.py' || true",
  "files": {
    "telegram_daemon": "/root/.areal-neva-core/telegram_daemon.py",
    "task_worker": "/root/.areal-neva-core/task_worker.py",
    "ai_router": "/root/.areal-neva-core/core/ai_router.py",
    "memory_api_server": "/root/.areal-neva-core/memory_api_server.py",
    "core_db": "/root/.areal-neva-core/data/core.db",
    "memory_db": "/root/.areal-neva-core/data/memory.db"
  },
  "memory_schema": [
    {
      "cid": 0,
      "name": "id",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 1
    },
    {
      "cid": 1,
      "name": "chat_id",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 2,
      "name": "key",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 3,
      "name": "value",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 4,
      "name": "timestamp",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    }
  ],
  "memory_count": 3,
  "memory_rows": [
    {
      "id": "c3353b3c-92df-44e2-a231-103d308ae8a2",
      "chat_id": "-1003725299009",
      "key": "user_input",
      "value": "",
      "timestamp": "2026-04-11T13:56:51.721825"
    },
    {
      "id": "2cf0d42c-157c-4be6-a3c9-c818a6158cd0",
      "chat_id": "-1003725299009",
      "key": "user_input",
      "value": "",
      "timestamp": "2026-04-11T13:57:16.414875"
    },
    {
      "id": "1023d7cf-de9f-459e-aa1d-87544b318c9e",
      "chat_id": "-1003725299009",
      "key": "user_input",
      "value": "Как настроение всё ли в порядке?",
      "timestamp": "2026-04-11T13:57:05.204941"
    }
  ],
  "sources_rows": [],
  "tasks_schema": [
    {
      "cid": 0,
      "name": "id",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 1
    },
    {
      "cid": 1,
      "name": "chat_id",
      "type": "INTEGER",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 2,
      "name": "user_id",
      "type": "INTEGER",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 3,
      "name": "input_type",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 4,
      "name": "raw_input",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 5,
      "name": "state",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": "\"NEW\"",
      "pk": 0
    },
    {
      "cid": 6,
      "name": "result",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 7,
      "name": "error_message",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 8,
      "name": "reply_to_message_id",
      "type": "INTEGER",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 9,
      "name": "created_at",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    },
    {
      "cid": 10,
      "name": "updated_at",
      "type": "TEXT",
      "notnull": 0,
      "dflt_value": null,
      "pk": 0
    }
  ],
  "last_tasks": [
    {
      "id": "14d0fefb-ecb0-4ce2-9e56-8fbbd9dc546b",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "",
      "state": "DONE",
      "result": "Всё в порядке, спасибо. А у тебя?",
      "error_message": null,
      "reply_to_message_id": 2795,
      "created_at": "2026-04-11T13:57:16.333447+00:00",
      "updated_at": "2026-04-11T13:57:17.465609+00:00"
    },
    {
      "id": "a51d0e33-bf9f-42be-bc3a-0ae2c7d2ccbf",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "Как настроение всё ли в порядке?",
      "state": "DONE",
      "result": "Настроение нормальное, всё в порядке. А у тебя?",
      "error_message": null,
      "reply_to_message_id": 2793,
      "created_at": "2026-04-11T13:57:04.883321+00:00",
      "updated_at": "2026-04-11T13:57:06.373296+00:00"
    },
    {
      "id": "a4c08fda-eaa7-428f-9575-1bd8bd8d7600",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "",
      "state": "DONE",
      "result": "Понял, готов отвечать.",
      "error_message": null,
      "reply_to_message_id": 2791,
      "created_at": "2026-04-11T13:56:51.395517+00:00",
      "updated_at": "2026-04-11T13:56:53.152799+00:00"
    },
    {
      "id": "fd6a77c5-1d85-4f62-bf45-ead1d76c0cbd",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "",
      "state": "DONE",
      "result": "Hello! How can I assist you today?",
      "error_message": null,
      "reply_to_message_id": 2789,
      "created_at": "2026-04-11T13:41:11.612250+00:00",
      "updated_at": "2026-04-11T13:41:18.307618+00:00"
    },
    {
      "id": "9ca9f754-eb00-4959-be75-0a11672418c9",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "",
      "state": "DONE",
      "result": "Hello! How can I assist you today?",
      "error_message": null,
      "reply_to_message_id": 2787,
      "created_at": "2026-04-11T13:40:55.751820+00:00",
      "updated_at": "2026-04-11T13:40:57.070533+00:00"
    },
    {
      "id": "8a2c53a3-e9c4-43c6-b8c4-32a73a9eb603",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "",
      "state": "DONE",
      "result": "It seems you might have intended to provide more context or a specific question. How can I assist you today?",
      "error_message": null,
      "reply_to_message_id": 2785,
      "created_at": "2026-04-11T13:40:34.152693+00:00",
      "updated_at": "2026-04-11T13:40:40.956432+00:00"
    },
    {
      "id": "b1abbf1b-a698-4cbb-bc02-db807d320c60",
      "chat_id": -1003725299009,
      "user_id": 2061134525,
      "input_type": "text",
      "raw_input": "тест",
      "state": "DONE",
      "result": "Привет! Как я могу помочь вам сегодня?",
      "error_message": null,
      "reply_to_message_id": 2783,
      "created_at": "2026-04-11T13:40:20.148758+00:00",
      "updated_at": "2026-04-11T13:40:21.554233+00:00"
    }
  ]
}
====================================================================================================
END_FILE: ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026-04-11.memory.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: README.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: b294b43738d41e1cc39c2e221ea9722e9605bae039a6f966e950e33b139ba3d7
====================================================================================================
# AREAL-NEVA ORCHESTRA — GITHUB SSOT
Создан: 28.04.2026

GitHub = каноны / архитектура / shared context / handoff / reports / tools
Сервер = runtime / обработка / memory.db / core.db / временные файлы
Drive = резерв и тяжёлые файлы

Регламент:
- только добавление, не перезатирание
- версионирование: v1 v2 v3
- patch-правило: было -> станет -> применить
- backup перед изменением
- токены никогда в репо

====================================================================================================
END_FILE: README.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: auto_memory_dump.sh
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 51c8b3cb64183d2a3f41cf82b53daa4e234bac3e9aa4540958cecc5a1db39cb6
====================================================================================================
#!/bin/bash
cd /root/.areal-neva-core
/root/.areal-neva-core/.venv/bin/python3 /root/.areal-neva-core/orchestra_full_dump.py >> /root/.areal-neva-core/logs/auto_dump.log 2>&1

====================================================================================================
END_FILE: auto_memory_dump.sh
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/norms/normative_index.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 8d7a9162925e029c6590e632f7514e7d3bfda171a96ffc9b2c7d2de06f277448
====================================================================================================
[
  {
    "doc": "СП 70.13330.2012",
    "clause": "",
    "text": "Несущие и ограждающие конструкции. Дефекты фиксируются и устраняются по проектному решению",
    "keywords": ["бетон", "монолит", "трещина", "раковина", "скол", "дефект"],
    "source": "LOCAL_SAFE_INDEX"
  },
  {
    "doc": "СП 63.13330.2018",
    "clause": "",
    "text": "Бетонные и железобетонные конструкции. Расчёт требует проверки класса бетона, арматуры и защитного слоя",
    "keywords": ["бетон", "арматура", "защитный слой", "кж", "плита", "фундамент"],
    "source": "LOCAL_SAFE_INDEX"
  },
  {
    "doc": "ГОСТ 21.101-2020",
    "clause": "",
    "text": "Основные требования к проектной и рабочей документации",
    "keywords": ["проект", "документация", "чертеж", "спецификация", "ведомость"],
    "source": "LOCAL_SAFE_INDEX"
  }
]

====================================================================================================
END_FILE: data/norms/normative_index.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_manual.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 805aeb52360d047d9cb6b06fef54cab4177aa5bf6e9797a462f58be3735a398e
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V1",
  "project_type": "АР",
  "source_files": [
    "ПРОЕКТ КД кровля 5.pdf"
  ],
  "sheet_register": [],
  "marks": [
    "АР"
  ],
  "sections": [
    "плане",
    "расчет",
    "Расчетная",
    "Фасады",
    "Разрез",
    "План",
    "фасада"
  ],
  "axes_grid": {
    "axes_letters": [],
    "axes_numbers": [
      "01",
      "02",
      "23",
      "31"
    ]
  },
  "dimensions": [
    940,
    730,
    2025,
    16940,
    10730,
    360,
    2001,
    501,
    27751,
    6931,
    3254,
    1552,
    7463,
    6120,
    485,
    1393,
    800,
    4350,
    2300,
    3590,
    6700,
    3570,
    3160,
    4000,
    7870,
    8381,
    6850,
    6750,
    9572,
    9903,
    2783,
    900,
    944,
    1498,
    1631,
    2672,
    2968,
    1180,
    2822,
    1629,
    3600,
    3500,
    4987,
    5468,
    3916,
    600,
    10930,
    10440,
    10040,
    10530,
    4640,
    5125,
    2900,
    2905,
    1600,
    1605,
    970,
    1925,
    1930,
    4980,
    2170,
    520,
    780,
    1000,
    12730,
    12240,
    700,
    12125,
    675,
    620,
    12120
  ],
  "levels": [
    "0.0",
    "21.501"
  ],
  "nodes": [],
  "specifications": [],
  "materials": [
    "металлочерепица.",
    "бруса",
    "Утеплитель",
    "Утепление",
    "Вент.брусок",
    "Металлочерепица",
    "Брус"
  ],
  "stamp_fields": {
    "year": "2025"
  },
  "variable_parameters": [
    "project_name",
    "address",
    "customer",
    "area",
    "floors",
    "axes_grid",
    "dimensions",
    "materials",
    "sheet_register"
  ],
  "output_documents": [
    "DOCX_PROJECT_TEMPLATE_SUMMARY",
    "JSON_PROJECT_TEMPLATE_MODEL",
    "XLSX_SPECIFICATION_DRAFT"
  ],
  "quality": {
    "has_sheet_register": false,
    "has_sections": true,
    "has_axes_or_dimensions": true,
    "has_materials": true,
    "text_chars": 8561,
    "lines": 1822
  },
  "task_id": "",
  "chat_id": "",
  "topic_id": 0
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_manual.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_repaired.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 756930a51f0ac08eb66c6253ff4fe99247a1fa2153b56e9dcbff2a515328fca3
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V2_REPAIRED",
  "project_type": "АР",
  "source_file": "Проект АБ_ИНД_М_80_20_03_24.pdf",
  "template_file": "/root/.areal-neva-core/data/project_templates/PROJECT_TEMPLATE_MODEL__АР_repaired.json",
  "repaired_at": "2026-04-30T09:15:02.251470Z",
  "sheet_register": [
    "01 Общие данные",
    "02 Общий вид",
    "03 План аксонометрия",
    "04 Экспликация помещений",
    "05 План фундамента Отм. -0,029",
    "06 Перспектива. Гостинная и прихожая.",
    "07 Перспектива.",
    "08 Перспектива.",
    "09 Фасады",
    "10 Расстановка выключателей и розеток",
    "11 Маркировочный план",
    "12 Заполнение конных и дверных проемов",
    "02 Согласовано",
    "05 План фундамента",
    "06 Согласовано",
    "07 Согласовано",
    "08 Согласовано",
    "03 План закладных деталей коммуникаций",
    "04 План фундамента",
    "05 План первого этажа",
    "06 План кровли",
    "07 Фасад 1-4",
    "08 Фасад 4-1",
    "09 Фасад А-Д",
    "10 Фасад Д-А",
    "13 Экспликация помещений",
    "19 Ведомость отделки",
    "20 Общие указания",
    "22 Ведомость листов"
  ],
  "sections": [],
  "materials": [],
  "source": "core.db.topic_210.drive_file"
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_repaired.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_smoke.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: bedd84f1787a2381a8bd97ca6b9af30e39f4e4f69f2a8849e018e72a4e4dcf72
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V1",
  "project_type": "АР",
  "source_files": [
    "АР тест.pdf"
  ],
  "sheet_register": [
    {
      "mark": "АР",
      "number": "1",
      "title": "Общие данные"
    },
    {
      "mark": "АР",
      "number": "2",
      "title": "План этажа"
    },
    {
      "mark": "АР",
      "number": "3",
      "title": "Фасады"
    },
    {
      "mark": "АР",
      "number": "4",
      "title": "Разрез 1-1"
    },
    {
      "mark": "АР",
      "number": "5",
      "title": "Узлы"
    }
  ],
  "marks": [
    "АР"
  ],
  "sections": [
    "Общие данные",
    "Ведомость листов",
    "АР-1 Общие данные",
    "АР-2 План этажа",
    "АР-3 Фасады",
    "АР-4 Разрез 1-1",
    "Спецификация материалов"
  ],
  "axes_grid": {
    "axes_letters": [
      "А"
    ],
    "axes_numbers": [
      "1"
    ]
  },
  "dimensions": [
    6000,
    3000,
    2500,
    500,
    2024
  ],
  "levels": [
    "0.0"
  ],
  "nodes": [],
  "specifications": [
    "Ведомость листов",
    "Спецификация материалов"
  ],
  "materials": [
    "Бетон В25",
    "Арматура А500"
  ],
  "stamp_fields": {
    "address": "Ленинградская область, Всеволожский район",
    "developer": "ООО СК Ареал-Нева",
    "year": "2024"
  },
  "variable_parameters": [
    "project_name",
    "address",
    "customer",
    "area",
    "floors",
    "axes_grid",
    "dimensions",
    "materials",
    "sheet_register"
  ],
  "output_documents": [
    "DOCX_PROJECT_TEMPLATE_SUMMARY",
    "JSON_PROJECT_TEMPLATE_MODEL",
    "XLSX_SPECIFICATION_DRAFT"
  ],
  "quality": {
    "has_sheet_register": true,
    "has_sections": true,
    "has_axes_or_dimensions": true,
    "has_materials": true,
    "text_chars": 297,
    "lines": 17
  },
  "task_id": "smoke",
  "chat_id": "-1003725299009",
  "topic_id": 210
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__АР_smoke.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КД_manual.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 72496cf6a372720635bd37bce2ac77ab69a6260db9100ce75fb3871e84f810c3
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V1",
  "project_type": "КД",
  "source_files": [
    "АР_КД_Агалатово_02.pdf"
  ],
  "sheet_register": [
    {
      "mark": "ов",
      "number": "1-2",
      "title": "сорта естественной влажности согласно раздела КД, с обработкой"
    }
  ],
  "marks": [
    "КД"
  ],
  "sections": [
    "Ведомость рабочих чертежей",
    "Ведомость рабочих чертежей основного комплекта (КД02)",
    "34 Схема расположения элементов подстропильной системы",
    "37 Разрез 2-1, Разрез 2-2",
    "38 Схема расположения элементов стропильной системы",
    "39 Схема расположения обрешетки",
    "40 Спецификация на стропильную систему, 3D вид стропильной системы",
    "44 Спецификация на стропильную систему, 3D вид стропильной системы гаража",
    "Ведомость рабочих чертежей основного комплекта (АР01)",
    "01 Ведомость рабочих чертежей",
    "02 Общие данные",
    "03 Общие данные",
    "04 Общие данные",
    "05 Схема планировочной организации земельного участка",
    "06 План расположения котлована",
    "07 План расположения фундамента дома",
    "08 План расположения отмостки",
    "09 План размерный на отметке 0.000",
    "10 План размерный на отметке +3.600",
    "11 План размерный на отметке +6.700",
    "12 План кладочный на отметке 0.000",
    "13 План кладочный на отметке +3.600",
    "14 План расположения водосточных желобов",
    "15 План маркировочный на отметке 0.000",
    "16 План маркировочный на отметке +3.600",
    "20 План на отметке 0.000 с расстановкой мебели",
    "21 План на отметке +3.600 с расстановкой мебели",
    "22 Разрез 1-1",
    "23 Разрез 1-2",
    "24 Фасад 1-5",
    "25 Фасад Г-А",
    "26 Фасад 5-1",
    "27 Фасад А-Г",
    "- исходные данные для подготовки проектной документации должны быть представлены в соответствии с Постановлениями Правительства Российской Федерации",
    "№ 840 от 29.12.2005 г. «О форме градостроительного плана земельного участка», № 840 от 29.12.2005 г. «О форме градостроительного плана земельного участка»,",
    "Общие данные",
    "2.1. 2.1. АрхитектурноАрхитектурно - -планировочноепланировочное решение решение",
    "На втором этаже имеется один санузел, душевая комната и 4 спальни.",
    "4. Наружная отделка стен - штукатурные работы по технике \"Мокрый фасад\",",
    "клинкерная плитка, декоративные фасадные архитектурные элементы.",
    "5. Цветовое решение материалов отделки фасадов и декоративных элементов",
    "8. Класс конструктивной пожарной опасности здания - С2.",
    "изделия и материалы, используемые при строительстве, должны быть сертифицированы в",
    "3. 3. КонструктивныеКонструктивные решения решения",
    "утрамбованного отсыпного материала. Высота подушки должна быть не менее 200 мм от поверхности песка коричневого,",
    "2. Стены наружные несущие монолитные толщиной 200 мм, утеплены согласно разрезам.",
    "- отделка фасада - штукатурка \"Мокрый фасад\", отледка клинкерной плиткой.",
    "7. Стропильная система – из пиломатериалов 1-2 сорта естественной влажности согласно раздела КД, с обработкой",
    "ЛистСхема планировочной организации земельного",
    "Схема планировочной организации земельного участка",
    "План расположения котлована",
    "План расположения фундамента дома",
    "План расположения отмостки",
    "План размерный на отметке 0.000",
    "План размерный на отметке +3.600"
  ],
  "axes_grid": {
    "axes_letters": [
      "А",
      "Г"
    ],
    "axes_numbers": [
      "01",
      "1",
      "2",
      "02",
      "5",
      "21",
      "23",
      "31"
    ]
  },
  "dimensions": [
    2025,
    600,
    700,
    2008,
    2007,
    840,
    2005,
    2006,
    2016,
    2003,
    13330,
    2011,
    2010,
    2001,
    900,
    400,
    300,
    1500,
    10925,
    17140,
    3400,
    5500,
    6220,
    620,
    4350,
    2300,
    3590,
    6700,
    3570,
    3160,
    4000,
    1100,
    16940,
    10725,
    19140,
    12925,
    23095,
    3900,
    2000,
    3290,
    6250,
    10125,
    850,
    17143,
    3565,
    11265,
    17480,
    2020,
    1400,
    4845,
    5945,
    1000,
    1370,
    2720,
    1900,
    3175,
    770,
    5259,
    1022,
    4529,
    2850,
    570,
    4150,
    2100,
    3390,
    6500,
    10525,
    4500,
    1200,
    2150,
    1765,
    1650,
    1830,
    1333,
    1245,
    550,
    2350,
    650,
    450,
    1005
  ],
  "levels": [
    "0.0",
    "3.6",
    "6.7",
    "5.03",
    "29.12",
    "16.02",
    "19.01",
    "13.02",
    "22.07",
    "3.07",
    "30.201",
    "55.133",
    "50.133",
    "3.0",
    "2.7",
    "7.4",
    "6.75",
    "43.68",
    "17.59",
    "7.8",
    "1.8",
    "7.29",
    "13.0",
    "54.6",
    "7.69",
    "7.61",
    "23.24",
    "19.92",
    "18.98",
    "16.27",
    "5.18",
    "1.37",
    "92.57",
    "-0.9",
    "0.05",
    "0.27",
    "0.35"
  ],
  "nodes": [
    "На втором этаже имеется один санузел, душевая комната и 4 спальни."
  ],
  "specifications": [
    "Ведомость рабочих чертежей",
    "Ведомость рабочих чертежей основного комплекта (КД02)",
    "40 Спецификация на стропильную систему, 3D вид стропильной системы",
    "44 Спецификация на стропильную систему, 3D вид стропильной системы гаража",
    "Ведомость рабочих чертежей основного комплекта (АР01)",
    "01 Ведомость рабочих чертежей"
  ],
  "materials": [
    "1. Фундамент расположен на отметке -0.900, на утеплении из экструдированного пенополистирола толщиной 100 мм и \"подушке\" из",
    "2. Стены наружные несущие монолитные толщиной 200 мм, утеплены согласно разрезам.",
    "- монолитные железобетонные стены - 200мм,",
    "- утепление базальтовой ватой 150мм,",
    "- кладка полнотелого кирпича - 120 мм"
  ],
  "stamp_fields": {
    "year": "2008"
  },
  "variable_parameters": [
    "project_name",
    "address",
    "customer",
    "area",
    "floors",
    "axes_grid",
    "dimensions",
    "materials",
    "sheet_register"
  ],
  "output_documents": [
    "DOCX_PROJECT_TEMPLATE_SUMMARY",
    "JSON_PROJECT_TEMPLATE_MODEL",
    "XLSX_SPECIFICATION_DRAFT"
  ],
  "quality": {
    "has_sheet_register": true,
    "has_sections": true,
    "has_axes_or_dimensions": true,
    "has_materials": true,
    "text_chars": 12000,
    "lines": 494
  },
  "task_id": "",
  "chat_id": "",
  "topic_id": 0
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КД_manual.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КД_repaired.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d6924cc53adc5cb0d1edc58d3fd6165cbdf7c084b6e32f22e63f7524790a81d3
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V2_REPAIRED",
  "project_type": "КД",
  "source_file": "АР_КД_Агалатово_02.pdf",
  "template_file": "/root/.areal-neva-core/data/project_templates/PROJECT_TEMPLATE_MODEL__КД_repaired.json",
  "repaired_at": "2026-04-30T09:15:02.250916Z",
  "sheet_register": [
    "01 Ведомость рабочих чертежей",
    "02 Общие данные",
    "03 Общие данные",
    "04 Общие данные",
    "05 Схема планировочной организации земельного участка",
    "06 План расположения котлована",
    "07 План расположения фундамента дома",
    "08 План расположения отмостки",
    "09 План размерный на отметке 0.000",
    "10 План размерный на отметке +3.600",
    "11 План размерный на отметке +6.700",
    "01 Общие данные",
    "02 План балок перекрытия",
    "03 План стропильной системы",
    "04 План стропильной системы",
    "06 Спецификация элементов стропильной системы",
    "07 План обрешётки",
    "08 План контробрешётки",
    "16 Ведомость пиломатериалов",
    "17 Ведомость крепежа",
    "18 Спецификация кровельных материалов",
    "19 Схема монтажа",
    "20 Общие указания",
    "21 Ведомость листов"
  ],
  "sections": [],
  "materials": [],
  "source": "core.db.topic_210.drive_file"
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КД_repaired.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КЖ_repaired.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 82db86c234139cb30b4ad8578ff08eb29f94521ed89ec761a3d26f0d0d5a65fa
====================================================================================================
{
  "schema": "PROJECT_TEMPLATE_MODEL_V2_REPAIRED",
  "project_type": "КЖ",
  "source_file": "КЖ АК-М-160.pdf",
  "template_file": "/root/.areal-neva-core/data/project_templates/PROJECT_TEMPLATE_MODEL__КЖ_repaired.json",
  "repaired_at": "2026-04-30T09:15:02.251190Z",
  "sheet_register": [
    "01 Общие данные",
    "02 План фундаментной плиты",
    "03 Разрез 1-1",
    "04 Разрез 2-2",
    "05 Схема нижнего армирования",
    "06 Схема верхнего армирования",
    "07 Схема дополнительного армирования",
    "08 Узлы армирования углов",
    "09 Узлы примыкания ленты/ребра",
    "10 Схема закладных деталей",
    "11 Схема выпусков арматуры",
    "12 Схема инженерных проходок",
    "13 План опалубки",
    "14 Спецификация арматуры",
    "15 Спецификация бетона",
    "16 Ведомость материалов основания",
    "17 Ведомость объёмов работ",
    "18 Контрольные отметки",
    "19 Общие указания",
    "20 Ведомость листов"
  ],
  "sections": [],
  "materials": [],
  "source": "core.db.topic_210.drive_file"
}
====================================================================================================
END_FILE: data/project_templates/PROJECT_TEMPLATE_MODEL__КЖ_repaired.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/364b2395-0744-4a88-80a8-6e87c282aa3d.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: adcc187000a810f61ee9a17325a2d2ac5449bb8ef840f253121634f8897ffd27
====================================================================================================
{
  "template_id": "364b2395-0744-4a88-80a8-6e87c282aa3d",
  "chat_id": "-1003725299009",
  "topic_id": 210,
  "source_task_id": "364b2395-0744-4a88-80a8-6e87c282aa3d",
  "source_file_name": "АР_КД_Агалатово_02.pdf",
  "mime_type": "application/pdf",
  "kind": "estimate_template",
  "created_at": "2026-05-01T11:32:07.307426",
  "active": true
}
====================================================================================================
END_FILE: data/templates/364b2395-0744-4a88-80a8-6e87c282aa3d.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/bab630ba-7e3f-4c43-88ff-3e917e5c6279.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 079024dae167be51495505f479c057e9e7e1848d9ae077c4287d618c8418f642
====================================================================================================
{
  "template_id": "bab630ba-7e3f-4c43-88ff-3e917e5c6279",
  "chat_id": "-1003725299009",
  "topic_id": 2,
  "source_task_id": "bab630ba-7e3f-4c43-88ff-3e917e5c6279",
  "source_file_name": "Техническое задание Кордон снт.docx",
  "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "kind": "estimate_template",
  "created_at": "2026-05-02T00:20:57.882990",
  "active": true
}
====================================================================================================
END_FILE: data/templates/bab630ba-7e3f-4c43-88ff-3e917e5c6279.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/d5d1fbca-e848-4e36-b297-d12312cc5217.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d5c22742c734298e06a8fd5cdff777b21a1df1df2e192bba477b2b16da158f06
====================================================================================================
{
  "template_id": "d5d1fbca-e848-4e36-b297-d12312cc5217",
  "chat_id": "-1003725299009",
  "topic_id": 4569,
  "source_task_id": "d5d1fbca-e848-4e36-b297-d12312cc5217",
  "source_file_name": "",
  "mime_type": "",
  "kind": "unknown_template",
  "created_at": "2026-05-01T10:23:26.354953",
  "active": true
}
====================================================================================================
END_FILE: data/templates/d5d1fbca-e848-4e36-b297-d12312cc5217.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/ee10abce-9662-4797-825e-096188f40a4e.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 486eb146b39b89d7619166c2e3b99a531ab687709a2b111bcd64d5ed90105c47
====================================================================================================
{
  "template_id": "ee10abce-9662-4797-825e-096188f40a4e",
  "chat_id": "-1003725299009",
  "topic_id": 210,
  "source_task_id": "ee10abce-9662-4797-825e-096188f40a4e",
  "source_file_name": "АР_КД_Агалатово_02.pdf",
  "mime_type": "application/pdf",
  "kind": "estimate_template",
  "created_at": "2026-05-01T11:34:12.786364",
  "active": true
}
====================================================================================================
END_FILE: data/templates/ee10abce-9662-4797-825e-096188f40a4e.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/estimate/ACTIVE__chat_-1003725299009__topic_2.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2751853a7fec499884e42f27a565e5d1374b91b8c0c7aaec43cecba88b3128f3
====================================================================================================
{
  "engine": "FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE",
  "kind": "estimate",
  "status": "active",
  "chat_id": "-1003725299009",
  "topic_id": 2,
  "saved_by_task_id": "d390b50d-2f5e-4aeb-871a-3b30cc149d18",
  "source_task_id": "12f63475-a307-49d5-bf85-45852622840e",
  "source_file_id": "1Ert7YACjcfZcodklU7UnckLN3xgsyuKD",
  "source_file_name": "ВОР_кирпичная_кладка_ИСПРАВЛЕНО.xlsx",
  "source_mime_type": "",
  "source_caption": "",
  "source_score": 150,
  "saved_at": "2026-04-30T10:03:23.387650+00:00",
  "usage_rule": "Use this file as formatting/sample reference for future estimate/project artifacts in the same chat and topic",
  "raw_user_instruction": "Тот файл который я тебе скинул последний возьми его как образец для составления сметы"
}
====================================================================================================
END_FILE: data/templates/estimate/ACTIVE__chat_-1003725299009__topic_2.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/estimate/ACTIVE__chat_-1003725299009__topic_3008.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 225b637da9991f976ece0bfe4c6d0a4eca022ecb9bb09fa84104e63fb6bdca92
====================================================================================================
{
  "engine": "FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE",
  "kind": "estimate",
  "status": "active",
  "chat_id": "-1003725299009",
  "topic_id": 3008,
  "saved_by_task_id": "7270364c-bb74-4e1e-b531-de64dfe713b7",
  "source_task_id": "f5c33c40-dacf-46c9-97ca-2dc19e245650",
  "source_file_id": "1XsuPOtO-vyA73IX5Ui9AR9kf6uUAE5b_",
  "source_file_name": "estimate_c925a897-66ec-435e-8312-15687f.xlsx",
  "source_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "source_caption": "",
  "source_score": 110,
  "saved_at": "2026-05-01T08:38:07.108195+00:00",
  "usage_rule": "Use this file as formatting/sample reference for future estimate/project artifacts in the same chat and topic",
  "raw_user_instruction": "этот чат у нас используется с тобой для работы, соответственно, как ты правильно и сказал, по AI роутеру Arial Niva, но также мы здесь еще с тобой пишем коды по определенным запросам команд, которые ты вот сейчас мне написал, например, напиши код. То есть здесь мы также с тобой создаем еще коды, которые делаются на основании четырех моделей, которые присутствуют у нас с тобой."
}
====================================================================================================
END_FILE: data/templates/estimate/ACTIVE__chat_-1003725299009__topic_3008.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/estimate/TEMPLATE__chat_-1003725299009__topic_2__20260430_100323.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2751853a7fec499884e42f27a565e5d1374b91b8c0c7aaec43cecba88b3128f3
====================================================================================================
{
  "engine": "FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE",
  "kind": "estimate",
  "status": "active",
  "chat_id": "-1003725299009",
  "topic_id": 2,
  "saved_by_task_id": "d390b50d-2f5e-4aeb-871a-3b30cc149d18",
  "source_task_id": "12f63475-a307-49d5-bf85-45852622840e",
  "source_file_id": "1Ert7YACjcfZcodklU7UnckLN3xgsyuKD",
  "source_file_name": "ВОР_кирпичная_кладка_ИСПРАВЛЕНО.xlsx",
  "source_mime_type": "",
  "source_caption": "",
  "source_score": 150,
  "saved_at": "2026-04-30T10:03:23.387650+00:00",
  "usage_rule": "Use this file as formatting/sample reference for future estimate/project artifacts in the same chat and topic",
  "raw_user_instruction": "Тот файл который я тебе скинул последний возьми его как образец для составления сметы"
}
====================================================================================================
END_FILE: data/templates/estimate/TEMPLATE__chat_-1003725299009__topic_2__20260430_100323.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/estimate/TEMPLATE__chat_-1003725299009__topic_3008__20260501_083807.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 225b637da9991f976ece0bfe4c6d0a4eca022ecb9bb09fa84104e63fb6bdca92
====================================================================================================
{
  "engine": "FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE",
  "kind": "estimate",
  "status": "active",
  "chat_id": "-1003725299009",
  "topic_id": 3008,
  "saved_by_task_id": "7270364c-bb74-4e1e-b531-de64dfe713b7",
  "source_task_id": "f5c33c40-dacf-46c9-97ca-2dc19e245650",
  "source_file_id": "1XsuPOtO-vyA73IX5Ui9AR9kf6uUAE5b_",
  "source_file_name": "estimate_c925a897-66ec-435e-8312-15687f.xlsx",
  "source_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "source_caption": "",
  "source_score": 110,
  "saved_at": "2026-05-01T08:38:07.108195+00:00",
  "usage_rule": "Use this file as formatting/sample reference for future estimate/project artifacts in the same chat and topic",
  "raw_user_instruction": "этот чат у нас используется с тобой для работы, соответственно, как ты правильно и сказал, по AI роутеру Arial Niva, но также мы здесь еще с тобой пишем коды по определенным запросам команд, которые ты вот сейчас мне написал, например, напиши код. То есть здесь мы также с тобой создаем еще коды, которые делаются на основании четырех моделей, которые присутствуют у нас с тобой."
}
====================================================================================================
END_FILE: data/templates/estimate/TEMPLATE__chat_-1003725299009__topic_3008__20260501_083807.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/templates/index.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 4fefe3e44a76c132b89c1186ecc62d498869ba8185064756cfe43da0f0726914
====================================================================================================
{
  "_schema": "TEMPLATE_INDEX_DICT_FIX_V1",
  "_legacy_type": "list",
  "_legacy_data": [
    {
      "template_id": "d5d1fbca-e848-4e36-b297-d12312cc5217",
      "chat_id": "-1003725299009",
      "topic_id": 4569,
      "source_task_id": "d5d1fbca-e848-4e36-b297-d12312cc5217",
      "source_file_name": "",
      "mime_type": "",
      "kind": "unknown_template",
      "created_at": "2026-05-01T10:23:26.354953",
      "active": true
    },
    {
      "template_id": "364b2395-0744-4a88-80a8-6e87c282aa3d",
      "chat_id": "-1003725299009",
      "topic_id": 210,
      "source_task_id": "364b2395-0744-4a88-80a8-6e87c282aa3d",
      "source_file_name": "АР_КД_Агалатово_02.pdf",
      "mime_type": "application/pdf",
      "kind": "estimate_template",
      "created_at": "2026-05-01T11:32:07.307426",
      "active": false
    },
    {
      "template_id": "ee10abce-9662-4797-825e-096188f40a4e",
      "chat_id": "-1003725299009",
      "topic_id": 210,
      "source_task_id": "ee10abce-9662-4797-825e-096188f40a4e",
      "source_file_name": "АР_КД_Агалатово_02.pdf",
      "mime_type": "application/pdf",
      "kind": "estimate_template",
      "created_at": "2026-05-01T11:34:12.786364",
      "active": true
    },
    {
      "template_id": "bab630ba-7e3f-4c43-88ff-3e917e5c6279",
      "chat_id": "-1003725299009",
      "topic_id": 2,
      "source_task_id": "bab630ba-7e3f-4c43-88ff-3e917e5c6279",
      "source_file_name": "Техническое задание Кордон снт.docx",
      "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "kind": "estimate_template",
      "created_at": "2026-05-02T00:20:57.882990",
      "active": true
    }
  ]
}
====================================================================================================
END_FILE: data/templates/index.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/0/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 99110904300dc66aa8fe5e9cc9aa1de41ba518ca5ce020af0cb0e2c4fb0739f8
====================================================================================================
{
  "topic_id": 0,
  "name": "ЛИДЫ АМО",
  "direction": "crm_leads",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.231172+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/0/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/11/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 04c69440018c5cb2105f1624418040b5c4dac9a5da55f0ac5b07727ed5a103e0
====================================================================================================
{
  "topic_id": 11,
  "name": "ВИДЕОКОНТЕНТ",
  "direction": "video_production",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.231872+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/11/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/2/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 51744f466380c4b2398e4e6b98c21d35fa9435a905eb9c53b308aa6a8d8836ca
====================================================================================================
{
  "topic_id": 2,
  "name": "СТРОЙКА",
  "direction": "estimates",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.231412+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/2/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/210/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ce50915df1bdab1a3baf419fea40ed5b9dfc1f6d009a4daecf0b4e7fcb36110a
====================================================================================================
{
  "topic_id": 210,
  "name": "ПРОЕКТИРОВАНИЕ",
  "direction": "structural_design",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.232182+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/210/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/3008/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 997992e041d0f6ac8ad7dd83631d2eef51a26013445370bc050ff361e3f29c0e
====================================================================================================
{
  "topic_id": 3008,
  "name": "КОДЫ МОЗГОВ",
  "direction": "orchestration_core",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.232993+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/3008/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/4569/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: a436174d9ec1dfc8e15f469fc81c061d7b8bbef1538638faefd32fec954e9343
====================================================================================================
{
  "topic_id": 4569,
  "name": "ЛИДЫ РЕКЛАМА",
  "direction": "crm_leads",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.233153+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/4569/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/5/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 7ee48f4af7bf89f492bef00163145e6ee01981b768f38dd4c30e35b8e3311bf6
====================================================================================================
{
  "topic_id": 5,
  "name": "ТЕХНАДЗОР",
  "direction": "technical_supervision",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.231656+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/5/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/500/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: fe567370b38840c0c5b5625ad07f3c7bc8473beeaccca3d54386fed17599275c
====================================================================================================
{
  "topic_id": 500,
  "name": "ВЕБ ПОИСК",
  "direction": "internet_search",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.232499+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/500/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/6104/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 1e7f11136e5ddd7e984c3cbc17affc50d1c3f2f207ceecd341a32c7cf3a95e58
====================================================================================================
{
  "topic_id": 6104,
  "name": "РАБОТА ПОИСК",
  "direction": "job_search",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.233266+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/6104/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/794/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: cac974b2d8a0b3bf5dc1955a1fae4c6385a6a02fa96e5efcca1346cfc03db928
====================================================================================================
{
  "topic_id": 794,
  "name": "НЕЙРОНКИ СОФТ ВПН ВПС",
  "direction": "devops_server",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.232700+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/794/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: data/topics/961/meta.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c1b720f5d6b47a31456f65ecdf73132c8522479962158c9e97bbdc93b9697d25
====================================================================================================
{
  "topic_id": 961,
  "name": "АВТО ЗАПЧАСТИ",
  "direction": "auto_parts_search",
  "chat_id": "-1003725299009",
  "chat_name": "НЕЙРОНКИ ЧАТ",
  "synced_at": "2026-05-01T09:28:21.232859+00:00",
  "synced_by": "TOPIC_SYNC_FULL_V1"
}
====================================================================================================
END_FILE: data/topics/961/meta.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/SHARED_CONTEXT/DWG_CONVERTER_STATUS.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c1575faa9c30f7376fc965272741bac01693c844705a64e8b4ab6813ad0e4e73
====================================================================================================
{
  "checked_at": "2026-05-01T22:49:05.964682+00:00",
  "dwg2dxf": null,
  "ODAFileConverter": null,
  "geometry_status": "DWG_METADATA_ONLY_DXF_FULL_PARSE_READY",
  "note": "DXF parses directly. DWG full geometry requires dwg2dxf or ODAFileConverter; without converter DWG metadata path remains active"
}
====================================================================================================
END_FILE: docs/SHARED_CONTEXT/DWG_CONVERTER_STATUS.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: drive_ingest.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: fc2d949b93663d288b6ba9821521647603bce65ebd5c01a8e92b2e78835dda01
====================================================================================================
import json
import logging
import os
import sqlite3
import time
import uuid
from datetime import datetime, timezone

from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "/root/.areal-neva-core/credentials.json"
FOLDER_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
CORE_DB = "/root/.areal-neva-core/data/core.db"
CHAT_ID = "-1003725299009"
TOPIC_ID = 0

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("drive_ingest")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [r[1] for r in rows]


def task_exists_for_file(conn: sqlite3.Connection, file_id: str) -> bool:
    try:
        row = conn.execute(
            "SELECT 1 FROM drive_files WHERE drive_file_id=? LIMIT 1",
            (file_id,)
        ).fetchone()
        return row is not None
    except Exception:
        return False


def create_task_for_file(item: dict) -> None:
    file_id = item["id"]
    file_name = item["name"]
    mime_type = item.get("mimeType", "")
    now = utc_now()
    task_id = str(uuid.uuid4())
    raw_input = json.dumps(
        {
            "file_id": file_id,
            "file_name": file_name,
            "mime_type": mime_type,
            "source": "google_drive"
        },
        ensure_ascii=False
    )

    conn = sqlite3.connect(CORE_DB)
    try:
        if task_exists_for_file(conn, file_id):
            return

        task_cols = set(table_columns(conn, "tasks"))
        drive_cols = set(table_columns(conn, "drive_files"))

        task_data = {
            "id": task_id,
            "chat_id": CHAT_ID,
            "input_type": "drive_file",
            "raw_input": raw_input,
            "state": "NEW",
            "topic_id": TOPIC_ID,
            "created_at": now,
            "updated_at": now,
        }
        task_insert_cols = [
            c for c in ["id", "chat_id", "input_type", "raw_input", "state", "topic_id", "created_at", "updated_at"]
            if c in task_cols
        ]
        if not task_insert_cols:
            raise RuntimeError("tasks table has no expected columns")

        task_sql = f"INSERT INTO tasks ({', '.join(task_insert_cols)}) VALUES ({', '.join(['?'] * len(task_insert_cols))})"
        conn.execute(task_sql, [task_data[c] for c in task_insert_cols])

        drive_data = {
            "task_id": task_id,
            "drive_file_id": file_id,
            "file_name": file_name,
            "mime_type": mime_type,
            "stage": "discovered",
            "created_at": now,
        }
        drive_insert_cols = [
            c for c in ["task_id", "drive_file_id", "file_name", "mime_type", "stage", "created_at"]
            if c in drive_cols
        ]
        if drive_insert_cols:
            drive_sql = f"INSERT INTO drive_files ({', '.join(drive_insert_cols)}) VALUES ({', '.join(['?'] * len(drive_insert_cols))})"
            conn.execute(drive_sql, [drive_data[c] for c in drive_insert_cols])

        conn.commit()
        logger.info("ЗАДАЧА СОЗДАНА: %s | %s", task_id, file_name)
    finally:
        conn.close()


def main() -> None:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)

    logger.info("Мониторинг папки: %s", FOLDER_ID)

    while True:
        try:
            results = service.files().list(
                q=f"'{FOLDER_ID}' in parents and trashed=false",
                pageSize=50,
                fields="files(id,name,mimeType,createdTime)"
            ).execute()

            for item in results.get("files", []):
                mime_type = item.get("mimeType", "")
                if mime_type == "application/vnd.google-apps.folder":
                    logger.info("SKIP FOLDER: %s (%s)", item["name"], item["id"])
                    continue
                logger.info("Найден файл: %s (%s)", item["name"], item["id"])
                create_task_for_file(item)

            time.sleep(60)
        except Exception as e:
            logger.error("Ошибка: %s", e)
            time.sleep(60)


if __name__ == "__main__":
    main()

====================================================================================================
END_FILE: drive_ingest.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: google_io.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 1b50fb7199b536664b84bd4b1e951d9fca8cd2cf7686fef52661b2cef238097a
====================================================================================================
import os
import io
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

logger = logging.getLogger("google_io")

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDS_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '/root/.areal-neva-core/credentials.json')
PARENT_FOLDER_ID = os.getenv('GDRIVE_PARENT_ID', '')

def get_drive_service():
    client_id = os.getenv('GDRIVE_CLIENT_ID')
    client_secret = <REDACTED_SECRET>'GDRIVE_CLIENT_SECRET')
    refresh_token = <REDACTED_SECRET>'GDRIVE_REFRESH_TOKEN')
    
    if client_id and client_secret and refresh_token:
        creds = Credentials(
            token=<REDACTED_SECRET>
            refresh_token=<REDACTED_SECRET>
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=<REDACTED_SECRET>
            scopes=SCOPES
        )
        creds.refresh(Request())
        return build('drive', 'v3', credentials=creds)
    
    try:
        from google.oauth2.service_account import Credentials as SACreds
    except ImportError:
        logger.warning("google-api-python-client not installed — Drive disabled")
        return None
    if not os.path.exists(CREDS_FILE):
        logger.warning("CREDS_FILE not found: %s", CREDS_FILE)
        return None
    creds = SACreds.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

async def upload_to_drive(file_path: str, file_name: str, mime_type: str = None, parent_folder_id: str = None) -> dict:
    try:
        service = get_drive_service()
        if not service:
            return {'ok': False, 'error': 'Drive not configured'}
        import mimetypes
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_name)
            mime_type = mime_type or 'application/octet-stream'
        file_metadata = {'name': file_name}
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        elif PARENT_FOLDER_ID:
            file_metadata['parents'] = [PARENT_FOLDER_ID]
        with open(file_path, 'rb') as f:
            media = MediaIoBaseUpload(io.BytesIO(f.read()), mimetype=mime_type, resumable=True)
            result = service.files().create(body=file_metadata, media_body=media, fields='id', supportsAllDrives=True).execute()
        return {'ok': True, 'drive_file_id': result.get('id')}
    except Exception as e:
        logger.error("Drive upload failed: %s", e)
        return {'ok': False, 'error': str(e)}

====================================================================================================
END_FILE: google_io.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: media_group.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c4a87d6b4ef1ceaea9aa1a54756ca672556f15e332e7ea451dce42f028aa7429
====================================================================================================
# === MEDIA_GROUP_DEBOUNCE_V1 ===
from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger("media_group")

_album_buffer: Dict[str, Dict[str, Any]] = {}
_DEBOUNCE_SEC = 1.5

async def _flush_album(media_group_id: str, callback: Callable[..., Awaitable[Any]]) -> None:
    await asyncio.sleep(_DEBOUNCE_SEC)
    item = _album_buffer.pop(str(media_group_id), None)
    if not item:
        return
    files: List[Any] = item.get("files") or []
    chat_id = item.get("chat_id")
    topic_id = item.get("topic_id")
    try:
        result = callback(files=files, media_group_id=media_group_id, chat_id=chat_id, topic_id=topic_id)
        if asyncio.iscoroutine(result) or hasattr(result, "__await__"):
            await result
        logger.info("MEDIA_GROUP_DEBOUNCE_V1_FLUSHED group=%s files=%s", media_group_id, len(files))
    except Exception as e:
        logger.exception("MEDIA_GROUP_DEBOUNCE_V1_CALLBACK_ERR group=%s err=%s", media_group_id, e)

async def handle_media_group(
    file: Any,
    media_group_id: str,
    chat_id: str,
    topic_id: int = 0,
    callback: Optional[Callable[..., Awaitable[Any]]] = None,
) -> Dict[str, Any]:
    gid = str(media_group_id or "").strip()
    if not gid:
        if callback:
            result = callback(files=[file], media_group_id="", chat_id=chat_id, topic_id=topic_id)
            if asyncio.iscoroutine(result) or hasattr(result, "__await__"):
                await result
        return {"ok": True, "single": True, "files": 1}

    if gid not in _album_buffer:
        _album_buffer[gid] = {
            "files": [],
            "chat_id": chat_id,
            "topic_id": int(topic_id or 0),
            "timer": None,
        }

    buf = _album_buffer[gid]
    buf["files"].append(file)
    buf["chat_id"] = chat_id
    buf["topic_id"] = int(topic_id or 0)

    timer = buf.get("timer")
    if timer and not timer.done():
        timer.cancel()

    if callback:
        buf["timer"] = asyncio.create_task(_flush_album(gid, callback))

    return {"ok": True, "media_group_id": gid, "buffered": len(buf["files"])}

def get_media_group_buffer_size(media_group_id: str) -> int:
    item = _album_buffer.get(str(media_group_id or ""))
    if not item:
        return 0
    return len(item.get("files") or [])

def clear_media_group(media_group_id: str) -> int:
    item = _album_buffer.pop(str(media_group_id or ""), None)
    if not item:
        return 0
    return len(item.get("files") or [])

# === END_MEDIA_GROUP_DEBOUNCE_V1 ===

====================================================================================================
END_FILE: media_group.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: memory_api_server.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c162918a0af1c8e9aa0cea11bf94f965df343a3baaecf2e271510c3165c882aa
====================================================================================================
import os, json, sqlite3, uuid
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
DB = "/root/.areal-neva-core/data/memory.db"
TOKEN = <REDACTED_SECRET>"MEMORY_API_TOKEN", "mem-eaf522f4934508438010fb3442a9eebd")

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_id ON memory(chat_id)")
        conn.commit()

@app.route("/health", methods=["GET"])
def health(): return jsonify({"status": "ok"})

@app.route("/archive", methods=["POST"])
def archive():  # ARCHIVE_ENDPOINT_SCOPE_V2
    try:
        data = request.get_json(silent=True) or {}
        chat_id = str(data.get("chat_id") or "unknown")
        topic_id = int(data.get("topic_id") or 0)
        task_id = str(data.get("task_id") or str(uuid.uuid4()))
        value = data.get("value") or json.dumps(data, ensure_ascii=False)
        key = f"topic_{topic_id}_archive_{task_id[:8]}"
        with sqlite3.connect(DB) as conn:
            existing = conn.execute("SELECT 1 FROM memory WHERE chat_id=? AND key=? LIMIT 1", (chat_id, key)).fetchone()  # ARCHIVE_DEDUP_BY_KEY_V1
            if existing:
                return jsonify({"ok": True, "key": key, "dedup": True}), 200
            conn.execute("INSERT INTO memory (id, chat_id, key, value, timestamp) VALUES (?,?,?,?,?)",
                (str(uuid.uuid4()), chat_id, key, str(value), datetime.utcnow().isoformat()))
            conn.commit()
        return jsonify({"ok": True, "key": key, "dedup": False}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/memory", methods=["GET"])
def get_memory():
    if request.headers.get("Authorization") != f"Bearer {TOKEN}": return jsonify({"error": "unauthorized"}), 403
    chat_id = request.args.get("chat_id")
    limit = int(request.args.get("limit", 100))
    with sqlite3.connect(DB) as conn:
        rows = conn.execute("SELECT chat_id, key, value, timestamp FROM memory WHERE chat_id=? ORDER BY timestamp DESC LIMIT ?", (chat_id, limit)).fetchall()
    return jsonify([{"chat_id": r[0], "key": r[1], "value": r[2], "timestamp": r[3]} for r in rows])

@app.route("/memory", methods=["POST"])
def post_memory():
    if request.headers.get("Authorization") != f"Bearer {TOKEN}": return jsonify({"error": "unauthorized"}), 403
    data = request.json
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT INTO memory (id, chat_id, key, value, timestamp) VALUES (?,?,?,?,?)", (str(uuid.uuid4()), data["chat_id"], data.get("key", "full_export"), str(data.get("value", "")), datetime.utcnow().isoformat()))
        conn.commit()
    return jsonify({"status": "ok"}), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8091)

====================================================================================================
END_FILE: memory_api_server.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: monitor_jobs.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d23f420339e9f337d43bf2e5317c8973c177fbb5b49e2989227687599eae3fe5
====================================================================================================
#!/usr/bin/env python3
# === FULLFIX_18B_SAFE_V2_MONITOR_JOBS ===
import os
import time
import sqlite3
import logging
from pathlib import Path

BASE = Path("/root/.areal-neva-core")
DB_PATH = BASE / "data" / "core.db"
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "monitor_jobs.log"

POLL_SEC = int(os.getenv("MONITOR_JOBS_POLL_SEC", "600"))
STALE_AWAITING_HOURS = int(os.getenv("STALE_AWAITING_HOURS", "3"))
STALE_RUNTIME_MINUTES = int(os.getenv("STALE_RUNTIME_MINUTES", "30"))
LIMIT_PER_RUN = int(os.getenv("MONITOR_JOBS_LIMIT", "100"))

logger = logging.getLogger("monitor_jobs")
logger.setLevel(logging.INFO)
logger.handlers.clear()

_fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

_fh = logging.FileHandler(str(LOG_PATH))
_fh.setFormatter(_fmt)
logger.addHandler(_fh)

_sh = logging.StreamHandler()
_sh.setFormatter(_fmt)
logger.addHandler(_sh)


def _connect():
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def _history(conn, task_id, action):
    conn.execute(
        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
        (task_id, action),
    )


def close_stale_runtime(conn, minutes=STALE_RUNTIME_MINUTES, limit=LIMIT_PER_RUN):
    """
    Preserve existing monitor_jobs responsibility:
    stale NEW / IN_PROGRESS / WAITING_CLARIFICATION must not hang forever
    """
    rows = conn.execute(
        """
        SELECT id,state
        FROM tasks
        WHERE state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION')
        AND datetime(updated_at) < datetime('now', ?)
        ORDER BY updated_at ASC
        LIMIT ?
        """,
        (f"-{int(minutes)} minutes", int(limit)),
    ).fetchall()

    closed = 0
    for row in rows:
        task_id = row["id"]
        old_state = row["state"]
        result = f"Задача закрыта монитором: зависла в статусе {old_state} дольше {minutes} минут"
        cur = conn.execute(
            """
            UPDATE tasks
            SET state='FAILED',
                result=COALESCE(NULLIF(result,''), ?),
                error_message=COALESCE(NULLIF(error_message,''), ?),
                updated_at=datetime('now')
            WHERE id=?
            AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION')
            """,
            (result, f"STALE_{old_state}_{minutes}MIN", task_id),
        )
        if cur.rowcount:
            _history(conn, task_id, f"state:FAILED:stale_runtime_cleanup_{old_state}_{minutes}min")
            closed += 1

    return closed


def close_stale_awaiting_confirmation(conn, hours=STALE_AWAITING_HOURS, limit=LIMIT_PER_RUN):
    """
    AWAITING_CONFIRMATION is not execution failure.
    If user did not confirm for hours, close as DONE to prevent stale context pollution
    """
    rows = conn.execute(
        """
        SELECT id
        FROM tasks
        WHERE state='AWAITING_CONFIRMATION'
        AND datetime(updated_at) < datetime('now', ?)
        ORDER BY updated_at ASC
        LIMIT ?
        """,
        (f"-{int(hours)} hours", int(limit)),
    ).fetchall()

    closed = 0
    for row in rows:
        task_id = row["id"]
        cur = conn.execute(
            """
            UPDATE tasks
            SET state='DONE',
                updated_at=datetime('now')
            WHERE id=?
            AND state='AWAITING_CONFIRMATION'
            """,
            (task_id,),
        )
        if cur.rowcount:
            _history(conn, task_id, f"state:DONE:stale_awaiting_cleanup_{hours}h")
            closed += 1

    return closed


def monitor_once():
    with _connect() as conn:
        runtime_closed = close_stale_runtime(conn)
        awaiting_closed = close_stale_awaiting_confirmation(conn)
        conn.commit()
        if runtime_closed or awaiting_closed:
            logger.info(
                "MONITOR_CLEANUP runtime_closed=%s awaiting_closed=%s",
                runtime_closed,
                awaiting_closed,
            )
        return runtime_closed, awaiting_closed


def main():
    logger.info(
        "MONITOR_JOBS_START db=%s poll=%s runtime_min=%s awaiting_h=%s limit=%s",
        DB_PATH,
        POLL_SEC,
        STALE_RUNTIME_MINUTES,
        STALE_AWAITING_HOURS,
        LIMIT_PER_RUN,
    )
    while True:
        try:
            monitor_once()
        except Exception as e:
            logger.exception("MONITOR_JOBS_ERROR err=%s", e)
        time.sleep(POLL_SEC)


if __name__ == "__main__":
    main()
# === END FULLFIX_18B_SAFE_V2_MONITOR_JOBS ===

====================================================================================================
END_FILE: monitor_jobs.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: orchestra_full_dump.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 55f3ba1c3563113477e0309cc42bebac27d745df740db976381bf451c615ac86
====================================================================================================
import json,sqlite3,os,glob
from datetime import datetime
BASE="/root/.areal-neva-core"
def build():
    d={"chat_id":"UNKNOWN","exported_at":datetime.utcnow().isoformat()+"Z","source_platform":"areal-neva-core","source_model":"orchestra_full_dump","system":"AREAL-NEVA ORCHESTRA server 89.22.225.136 owner Ilya bot @ai_orkestra_all_bot","architecture":"telegram_daemon->core.db->task_worker->ai_router OpenRouter perplexity/sonar+deepseek->reply_sender->Telegram","pipeline":"voice/text->daemon->create_task->worker->STT->ai_router->perplexity search->deepseek format->reply","memory":"core.db tasks+task_history+pin. memory.db key/value. memory_files CHATS/GLOBAL/SYSTEM jsonl","integrations":"OpenRouter perplexity/sonar deepseek/deepseek-chat Groq STT OpenAI STT Google Drive Telegram","services":["telegram-ingress.service","areal-task-worker.service","areal-memory-api.service"],"env":[],"db":"tasks(id,chat_id,input_type,raw_input,state,result,error_message,reply_to_message_id,created_at,updated_at) task_history(task_id,action,created_at) pin(task_id,chat_id,state,updated_at) memory(chat_id,key,value,timestamp)","logic":"NEW->IN_PROGRESS->AWAITING_CONFIRMATION->DONE. search: perplexity/sonar->inject search_context->deepseek formats. STT in daemon. BAD_RESULT_RE filters junk","decisions":"ONLINE_MODEL=perplexity/sonar DEFAULT_MODEL=deepseek/deepseek-chat STT in daemon override=True links check removed gemini removed","errors":["gemini 403 blocked->replaced with perplexity/sonar","links check killed valid results->removed","DeepSeek placeholder->BAD_RESULT_RE","voice file not found stale tasks->recover_stale","ai_router old version persisted->full rewrite"],"state":"voice ok STT ok search ok perplexity/sonar ok results reach Telegram","limits":"memory.db write after DONE not implemented web_engine.py duckduckgo dead code dump command not yet in daemon","pending":"verify memory.db writes remove duckduckgo clean web_engine.py","files":{},"tasks":[],"memory_data":[],"logs":{}}
    env_path=BASE+"/.env"
    if os.path.exists(env_path):
        for line in open(env_path):
            line=line.strip()
            if line and not line.startswith("#") and "=" in line:
                d["env"].append(line.split("=")[0])
    for f in ["telegram_daemon.py","task_worker.py","core/ai_router.py","core/stt_engine.py","core/reply_sender.py","core/pin_manager.py","memory_api_server.py","google_io.py"]:
        p=BASE+"/"+f
        d["files"][f]=open(p).read() if os.path.exists(p) else "NOT_FOUND"
    db_path=BASE+"/data/core.db"
    if os.path.exists(db_path):
        conn=sqlite3.connect(db_path)
        conn.row_factory=sqlite3.Row
        try:
            rows=conn.execute("SELECT t.id,t.chat_id,t.input_type,t.raw_input,t.state,t.result,t.error_message,t.created_at,t.updated_at,GROUP_CONCAT(h.action,\" | \") as history FROM tasks t LEFT JOIN task_history h ON h.task_id=t.id GROUP BY t.id ORDER BY t.created_at DESC LIMIT 200").fetchall()
            for r in rows: d["tasks"].append(dict(r))
        except: pass
        finally: conn.close()
    mem_path=BASE+"/data/memory.db"
    if os.path.exists(mem_path):
        conn=sqlite3.connect(mem_path)
        conn.row_factory=sqlite3.Row
        try:
            rows=conn.execute("SELECT * FROM memory ORDER BY timestamp DESC LIMIT 500").fetchall()
            for r in rows: d["memory_data"].append(dict(r))
        except: pass
        finally: conn.close()
    for log in ["task_worker.log","ai_router.log","telegram_daemon.log"]:
        p=BASE+"/logs/"+log
        d["logs"][log]="".join(open(p).readlines()[-300:]) if os.path.exists(p) else "NOT_FOUND"
    return d
if __name__=="__main__":
    import sys
    out=json.dumps(build(),ensure_ascii=False,default=str)
    from datetime import datetime
    ts=datetime.now().strftime("%Y%m%d_%H%M%S")
    fp="/root/.areal-neva-core/data/memory/UNSORTED/orchestra_dump_"+ts+".json"
    open(fp,"w").write(out)
    print(out)

====================================================================================================
END_FILE: orchestra_full_dump.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: requirements.txt
FILE_CHUNK: 1/1
SHA256_FULL_FILE: cac264fdbc5bb280bb7821291845def7368cb8fef9d10d0d723d5552f71b936f
====================================================================================================
reportlab
ezdxf
openpyxl
pypdf
pdfplumber
python-docx
pillow
python-dotenv

====================================================================================================
END_FILE: requirements.txt
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: startup_recovery.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 4e7fe4f628468d9a5d5757aa33c8da5df76ccb0f0c3a6dbb56ed05d4f12161cf
====================================================================================================
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

====================================================================================================
END_FILE: startup_recovery.py
FILE_CHUNK: 1/1
====================================================================================================
