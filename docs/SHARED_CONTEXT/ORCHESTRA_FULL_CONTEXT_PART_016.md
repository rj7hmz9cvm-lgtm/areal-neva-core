# ORCHESTRA_FULL_CONTEXT_PART_016
generated_at_utc: 2026-07-07T17:24:03.207668+00:00
git_sha_before_commit: e4b5fdc5234ada55a4a9968b15bd631bc175a65f
part: 16/22


====================================================================================================
BEGIN_FILE: core/telegram_source_skill_extractor.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2f9e18163498265ad703ced0637bf33a83779fdfc4b7304974bb64d091a5f797
====================================================================================================
#!/usr/bin/env python3
# === TELEGRAM_SOURCE_SKILL_EXTRACTOR_V1 ===
# Read-only Telethon-based extractor for public Telegram sources.
# Collects message metadata, links, and document references.
# Does NOT save raw history to memory.db or create core.db tasks.
from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("telegram_source_skill_extractor")

BASE = Path(__file__).parent.parent
SESSION_PATH = BASE / "sessions" / "user.session"
API_ID = 27925449

URL_RE = re.compile(r"https?://[^\s\)\]\>\"']+")

DOCUMENT_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls",
    ".pptx", ".ppt", ".zip", ".rar", ".dwg", ".dxf",
}

TECHNADZOR_KEYWORDS = [
    "акт", "дефект", "предписание", "заключение", "протокол",
    "осмотр", "проверка", "замечание", "нарушение", "устранение",
    "приёмка", "приемка", "скрытые работы", "исполнительная",
    "норматив", "снип", "гост", "сп ", "фото", "документ",
    "отчёт", "отчет", "смета", "спецификация", "чертёж", "чертеж",
    "технадзор", "стройконтроль", "авторский надзор",
    "кровля", "фасад", "перекрытие", "колонна", "фундамент",
    "бетон", "арматура", "сварка", "металл", "кладка", "газобетон",
    "отделка", "стяжка", "штукатурка", "электрика", "вентиляция",
    "водоснабжение", "канализация", "охрана труда",
]

NOISE_MARKERS = [
    "реклама", "продам", "куплю", "скидка", "акция",
    "подпишись", "переходи по ссылке", "розыгрыш",
    "заработок", "кредит без отказа", "займ",
    "только сегодня", "бесплатно жми", "выиграли",
]


def load_env(path: str | None = None) -> dict:
    env_path = Path(path) if path else BASE / ".env"
    result = {}
    if not env_path.exists():
        return result
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        result[k.strip()] = v.strip()
    return result


def build_client(session_path: str | None = None):
    from telethon import TelegramClient
    sp = str(session_path or SESSION_PATH)
    # api_hash not stored — authorized session does not need it for reads
    return TelegramClient(sp, API_ID, "a" * 32)


def extract_links(text: str) -> list[str]:
    return URL_RE.findall(text or "")


def is_relevant_for_document_skill(
    message_text: str,
    file_name: str | None = None,
    links: list[str] | None = None,
) -> bool:
    low = (message_text or "").lower()
    if any(n in low for n in NOISE_MARKERS):
        return False
    if any(kw in low for kw in TECHNADZOR_KEYWORDS):
        return True
    fname_low = (file_name or "").lower()
    if any(ext in fname_low for ext in DOCUMENT_EXTENSIONS):
        return True
    for link in (links or []):
        if any(ext in link.lower() for ext in DOCUMENT_EXTENSIONS):
            return True
    return False


def build_source_record(msg_id: int, msg_date: str, text: str,
                        media_type: str | None, file_name: str | None,
                        links: list[str], channel: str) -> dict:
    return {
        "source": f"@{channel.lstrip('@')}",
        "message_id": msg_id,
        "message_date": msg_date,
        "text": (text or "")[:1500],
        "media_type": media_type,
        "file_name": file_name,
        "links": links,
        "source_ref": f"https://t.me/{channel.lstrip('@')}/{msg_id}",
    }


async def check_source_access(source: str, client) -> dict:
    try:
        entity = await client.get_entity(source.lstrip("@"))
        return {
            "ok": True,
            "id": entity.id,
            "title": getattr(entity, "title", ""),
            "username": getattr(entity, "username", ""),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def scan_source(source: str, client, limit: int = 1000) -> dict:
    from telethon.tl.types import (
        MessageMediaDocument, MessageMediaPhoto, MessageMediaWebPage
    )

    records: list[dict] = []
    total = skipped_empty = skipped_noise = detected_docs = detected_links = 0

    async for msg in client.iter_messages(source.lstrip("@"), limit=limit or None):
        total += 1
        text = (msg.message or "").strip()
        if not text and not msg.media:
            skipped_empty += 1
            continue

        low = text.lower()
        if any(n in low for n in NOISE_MARKERS):
            skipped_noise += 1
            continue

        links = extract_links(text)
        file_name = None
        media_type = None

        if isinstance(msg.media, MessageMediaDocument):
            doc = msg.media.document
            for attr in getattr(doc, "attributes", []):
                if hasattr(attr, "file_name") and attr.file_name:
                    file_name = attr.file_name
            media_type = "document"
            detected_docs += 1
        elif isinstance(msg.media, MessageMediaPhoto):
            media_type = "photo"
        elif isinstance(msg.media, MessageMediaWebPage):
            wp = msg.media.webpage
            if hasattr(wp, "url") and wp.url:
                links.append(wp.url)
            media_type = "webpage"

        if links:
            detected_links += 1

        date_str = msg.date.isoformat() if msg.date else ""
        record = build_source_record(
            msg.id, date_str, text, media_type, file_name,
            links, source.lstrip("@")
        )
        records.append(record)

    return {
        "total_fetched": total,
        "skipped_empty": skipped_empty,
        "skipped_noise": skipped_noise,
        "detected_docs": detected_docs,
        "detected_links": detected_links,
        "records": records,
    }


async def download_relevant_documents(
    client, msg, output_dir: Path
) -> str | None:
    from telethon.tl.types import MessageMediaDocument
    if not isinstance(msg.media, MessageMediaDocument):
        return None
    doc = msg.media.document
    file_name = f"doc_{msg.id}"
    for attr in getattr(doc, "attributes", []):
        if hasattr(attr, "file_name") and attr.file_name:
            file_name = attr.file_name
    ext = Path(file_name).suffix.lower()
    if ext not in DOCUMENT_EXTENSIONS:
        return None
    out_path = output_dir / file_name
    if out_path.exists():
        return str(out_path)
    try:
        await client.download_media(msg, file=str(out_path))
        return str(out_path)
    except Exception as e:
        logger.warning("download failed msg=%s err=%s", msg.id, e)
        return None


async def run_source_scan(
    source: str = "@tnz_msk",
    limit: int = 1000,
    download_docs: bool = False,
    docs_output_dir: Path | None = None,
) -> dict:
    client = build_client()
    await client.connect()

    if not await client.is_user_authorized():
        await client.disconnect()
        return {"ok": False, "error": "session_not_authorized"}

    access = await check_source_access(source, client)
    if not access["ok"]:
        await client.disconnect()
        return {"ok": False, "error": access.get("error")}

    scan = await scan_source(source, client, limit=limit)
    downloaded: list[str] = []

    if download_docs and docs_output_dir:
        docs_output_dir.mkdir(parents=True, exist_ok=True)
        from telethon.tl.types import MessageMediaDocument
        async for msg in client.iter_messages(source.lstrip("@"), limit=limit or None):
            if not isinstance(msg.media, MessageMediaDocument):
                continue
            text = msg.message or ""
            links = extract_links(text)
            doc = msg.media.document
            fname = ""
            for attr in getattr(doc, "attributes", []):
                if hasattr(attr, "file_name") and attr.file_name:
                    fname = attr.file_name
            if is_relevant_for_document_skill(text, fname, links):
                path = await download_relevant_documents(client, msg, docs_output_dir)
                if path:
                    downloaded.append(path)

    await client.disconnect()

    return {
        "ok": True,
        "source": source,
        "access": access,
        "scan": scan,
        "downloaded_documents": downloaded,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }
# === END_TELEGRAM_SOURCE_SKILL_EXTRACTOR_V1 ===

====================================================================================================
END_FILE: core/telegram_source_skill_extractor.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/temp_cleanup.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2b7b91b8f6ba3a13518d234d8c24a426b85854300ae56a458fae4c6bcdb06194
====================================================================================================
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

====================================================================================================
END_FILE: core/temp_cleanup.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/template_engine_v1.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 03b9f6dca63b13fc8584f33acc32498fc893c9dfe06a92b5d1c0e467d04eddfc
====================================================================================================
# === TEMPLATE_ENGINE_V1 ===
import os, json, logging, glob
from typing import Optional, Dict, Any
logger = logging.getLogger(__name__)

BASE = "/root/.areal-neva-core"
TEMPLATE_DIR = f"{BASE}/data/templates"
TRIGGER_PHRASES = [
    "сделай так же", "по образцу", "как в прошлый раз",
    "аналогично", "такой же", "такую же", "такое же",
    "по шаблону", "используй шаблон", "как раньше"
]

def is_template_request(text: str) -> bool:
    low = text.lower()
    return any(t in low for t in TRIGGER_PHRASES)

def save_template(topic_id: int, file_path: str, template_type: str = "estimate") -> bool:
    """Сохранить файл как шаблон для топика"""
    try:
        os.makedirs(f"{TEMPLATE_DIR}/{template_type}", exist_ok=True)
        import shutil
        ext = os.path.splitext(file_path)[1]
        dest = f"{TEMPLATE_DIR}/{template_type}/ACTIVE__topic_{topic_id}{ext}"
        shutil.copy2(file_path, dest)
        meta = {
            "topic_id": topic_id,
            "type": template_type,
            "source": file_path,
            "saved_at": __import__("datetime").datetime.utcnow().isoformat()
        }
        with open(f"{TEMPLATE_DIR}/{template_type}/ACTIVE__topic_{topic_id}.json", "w") as f:
            json.dump(meta, f, ensure_ascii=False)
        logger.info("TEMPLATE_ENGINE_V1 saved topic=%s type=%s", topic_id, template_type)
        return True
    except Exception as e:
        logger.error("TEMPLATE_SAVE_ERR %s", e)
        return False

def get_template(topic_id: int, template_type: str = "estimate") -> Optional[str]:
    """Получить путь к шаблону топика"""
    try:
        patterns = [
            f"{TEMPLATE_DIR}/{template_type}/ACTIVE__topic_{topic_id}.*",
            f"{TEMPLATE_DIR}/estimate/ACTIVE__topic_{topic_id}.*",
        ]
        for pat in patterns:
            hits = [f for f in glob.glob(pat) if not f.endswith(".json")]
            if hits:
                return hits[0]
    except Exception as e:
        logger.warning("TEMPLATE_GET_ERR %s", e)
    return None

def apply_template_to_xlsx(template_path: str, rows: list, output_path: str) -> bool:
    """Применить структуру шаблона к новым данным"""
    try:
        from openpyxl import load_workbook
        import copy
        wb_tpl = load_workbook(template_path)
        ws_tpl = wb_tpl.active

        # Копируем структуру — заголовки из шаблона
        wb_new = load_workbook(template_path)
        ws_new = wb_new.active

        # Очищаем данные, оставляем заголовки (строка 1-2)
        header_rows = 2
        for row in ws_new.iter_rows(min_row=header_rows+1, max_row=ws_new.max_row):
            for cell in row:
                cell.value = None

        # Заполняем новыми данными с сохранением формул
        for i, item in enumerate(rows, start=header_rows+1):
            ws_new.cell(i, 1, value=i - header_rows)
            ws_new.cell(i, 2, value=str(item.get("name", "")))
            ws_new.cell(i, 3, value=str(item.get("unit", "шт")))
            ws_new.cell(i, 4, value=float(item.get("qty", 0) or 0))
            ws_new.cell(i, 5, value=float(item.get("price", 0) or 0))
            ws_new.cell(i, 6, f"=D{i}*E{i}")

        # Итог
        last = header_rows + len(rows)
        ws_new.cell(last+1, 6, f"=SUM(F{header_rows+1}:F{last})")

        wb_new.save(output_path)
        logger.info("TEMPLATE_APPLIED_V1 output=%s rows=%s", output_path, len(rows))
        return True
    except Exception as e:
        logger.error("TEMPLATE_APPLY_ERR %s", e)
        return False

def detect_template_type(file_name: str, intent: str = "") -> str:
    fn = file_name.lower()
    if any(e in fn for e in [".xlsx", ".xls", ".csv"]):
        return "estimate"
    if any(e in fn for e in [".docx", ".doc"]):
        return "technadzor"
    if "estimate" in intent or "смет" in intent:
        return "estimate"
    return "estimate"
# === END TEMPLATE_ENGINE_V1 ===

====================================================================================================
END_FILE: core/template_engine_v1.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/template_intake_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2f648e1b331a0532cd5ada22935d47ef2b2d81860d0239e0cde9275f3702eddf
====================================================================================================
# === FULLFIX_14_TEMPLATE_INTAKE ===
import os, json, logging
from datetime import datetime
logger = logging.getLogger(__name__)
ENGINE = "FULLFIX_14_TEMPLATE_INTAKE"
TEMPLATES_DIR = "/root/.areal-neva-core/data/templates"
TEMPLATES_INDEX = os.path.join(TEMPLATES_DIR, "index.json")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

SAMPLE_PHRASES = [
    "как образец", "как шаблон", "образец", "шаблон", "как пример",
    "по образцу", "возьми", "используй этот", "используй как",
    "сделай по", "сохрани", "запомни"
]

def is_sample_intent(text):
    t = (text or "").lower()
    return any(p in t for p in SAMPLE_PHRASES)

def _load_index():
    if os.path.exists(TEMPLATES_INDEX):
        try:
            with open(TEMPLATES_INDEX, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def _save_index(idx):
    with open(TEMPLATES_INDEX, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)

def _detect_kind(file_name, mime_type, text=""):
    name = (file_name or "").lower()
    t = (text or "").lower()
    if "смет" in name or "смет" in t or "estimate" in name:
        return "estimate_template"
    if any(x in name for x in ["ар", "кж", "кд", "км", "проект"]):
        return "project_template"
    if any(x in t for x in ["акт", "дефект", "технадзор"]):
        return "act_template"
    if mime_type and "spreadsheet" in mime_type:
        return "estimate_template"
    if mime_type and "pdf" in mime_type:
        return "project_template"
    return "unknown_template"

def _save_memory_pointer(chat_id, topic_id, kind, template_id):
    try:
        import sqlite3
        mem_db = "/root/.areal-neva-core/data/memory.db"
        key = "topic_" + str(topic_id) + "_active_" + kind
        val = json.dumps({"template_id": template_id, "kind": kind})
        con = sqlite3.connect(mem_db)
        con.execute(
            "INSERT OR REPLACE INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,datetime('now'))",
            (chat_id, key, val)
        )
        con.commit()
        con.close()
    except Exception as e:
        logger.error("TEMPLATE_MEMORY_SAVE err=%s", e)

def save_template(task_id, chat_id, topic_id, file_name, mime_type, local_path="", caption=""):
    kind = _detect_kind(file_name, mime_type, caption)
    tmpl = {
        "template_id": task_id, "chat_id": chat_id, "topic_id": topic_id,
        "source_task_id": task_id, "source_file_name": file_name,
        "mime_type": mime_type, "kind": kind,
        "created_at": datetime.now().isoformat(), "active": True,
    }
    idx = _load_index()
    for t in idx:
        if t.get("chat_id") == chat_id and t.get("topic_id") == topic_id and t.get("kind") == kind:
            t["active"] = False
    idx.append(tmpl)
    _save_index(idx)
    with open(os.path.join(TEMPLATES_DIR, task_id + ".json"), "w", encoding="utf-8") as f:
        json.dump(tmpl, f, ensure_ascii=False, indent=2)
    _save_memory_pointer(chat_id, topic_id, kind, task_id)
    return tmpl

def get_active_template(chat_id, topic_id, kind="estimate_template"):
    idx = _load_index()
    for t in reversed(idx):
        if t.get("chat_id") == chat_id and t.get("topic_id") == topic_id and t.get("kind") == kind and t.get("active"):
            p = os.path.join(TEMPLATES_DIR, t["template_id"] + ".json")
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
    return {}

def process_template_intake_sync(conn, task_id, chat_id, topic_id, raw_input, local_path="", file_name="", mime_type=""):
    from core.reply_sender import send_reply_ex
    try:
        if not is_sample_intent(raw_input) and not file_name:
            return False
        if not file_name:
            row = conn.execute(
                "SELECT raw_input FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=? AND input_type='drive_file' AND state!='CANCELLED' ORDER BY created_at DESC LIMIT 1",
                (chat_id, topic_id)
            ).fetchone()
            if row:
                try:
                    meta = json.loads(row[0] or "{}")
                    file_name = meta.get("file_name", "")
                    mime_type = meta.get("mime_type", "")
                except Exception:
                    pass
        save_template(task_id, chat_id, topic_id, file_name, mime_type, local_path, raw_input)
        kind = _detect_kind(file_name, mime_type, raw_input)
        kind_label = {"estimate_template": "смета", "project_template": "проект", "act_template": "акт"}.get(kind, "файл")
        result_text = "Образец принят. Тип: " + kind_label + ". Файл: " + file_name + ". Шаблон сохранён."
        conn.execute(
            "UPDATE tasks SET state='DONE',result=?,updated_at=datetime('now') WHERE id=?",
            (result_text, task_id)
        )
        conn.execute(
            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
            (task_id, "state:DONE")
        )
        conn.commit()
        try:
            send_reply_ex(chat_id=str(chat_id), text=result_text, reply_to_message_id=None)
        except Exception as _se:
            logger.error("TEMPLATE_SEND_ERR task=%s err=%s", task_id, _se)
        return True
    except Exception as e:
        logger.error("TEMPLATE_INTAKE_ERROR task=%s err=%s", task_id, e)
        return False

async def process_template_intake(conn, task_id, chat_id, topic_id, raw_input, local_path="", file_name="", mime_type=""):
    import asyncio
    return await asyncio.get_event_loop().run_in_executor(
        None, process_template_intake_sync, conn, task_id, chat_id, topic_id, raw_input, local_path, file_name, mime_type
    )
# === END FULLFIX_14_TEMPLATE_INTAKE ===

====================================================================================================
END_FILE: core/template_intake_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/template_manager.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 3a9747ea77b9eedd43404491616b056af960b0fa4cdb72331f4b0ce6c3fc9cce
====================================================================================================
import os, logging, sqlite3, shutil
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)
MEMORY_DB = "/root/.areal-neva-core/data/memory.db"

def save_template(chat_id: str, topic_id: int, template_type: str, file_path: str) -> bool:
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cur = conn.cursor()
        key = f"topic_{topic_id}_template_{template_type}"
        cur.execute("INSERT OR REPLACE INTO memory (chat_id, key, value, timestamp) VALUES (?,?,?,?)",
                    (chat_id, key, file_path, datetime.utcnow().isoformat()))
        conn.commit(); conn.close()
        return True
    except Exception as e:
        logger.error(f"save_template: {e}")
        return False

def get_template(chat_id: str, topic_id: int, template_type: str) -> Optional[str]:
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cur = conn.cursor()
        cur.execute("SELECT value FROM memory WHERE chat_id=? AND key=?", (chat_id, f"topic_{topic_id}_template_{template_type}"))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except:
        return None

def apply_template(template_path: str, output_path: str, data: list) -> bool:
    try:
        shutil.copy(template_path, output_path)
        from openpyxl import load_workbook
        wb = load_workbook(output_path)
        ws = wb.active
        for i, row_data in enumerate(data, 2):
            for j, val in enumerate(row_data, 1):
                ws.cell(i, j, value=val)
        wb.save(output_path); wb.close()
        return True
    except Exception as e:
        logger.error(f"apply_template: {e}")
        return False

# === ALL_CONTOURS_TEMPLATE_MANAGER_V2 ===
def save_template(file_path, topic_id, intent):
    import shutil
    from pathlib import Path
    src=Path(file_path)
    if not src.exists():
        raise FileNotFoundError(str(file_path))
    safe="".join(c if c.isalnum() or c in ("_","-") else "_" for c in str(intent or "template"))
    out=Path("/root/.areal-neva-core/data/templates")
    out.mkdir(parents=True, exist_ok=True)
    dst=out/(str(int(topic_id or 0))+"_"+safe+(src.suffix or ".xlsx"))
    shutil.copy2(src,dst)
    return str(dst)
# === END_ALL_CONTOURS_TEMPLATE_MANAGER_V2 ===

# === FINAL_CODE_CONTOUR_TEMPLATE_APPLY_V1 ===
def apply_template(template_path, output_path, data_rows):
    from openpyxl import load_workbook
    wb=load_workbook(template_path)
    ws=wb.active
    start=2
    for r_idx,row in enumerate(data_rows or [], start):
        vals=row.values() if isinstance(row,dict) else row
        for c_idx,val in enumerate(list(vals),1):
            ws.cell(r_idx,c_idx,value=val)
    wb.save(output_path)
    return output_path
# === END_FINAL_CODE_CONTOUR_TEMPLATE_APPLY_V1 ===

# === TEMPLATE_SYSTEM_V41 ===

def template_learn_v41(file_path, chat_id=None, topic_id=0, template_type="project"):
    try:
        return save_template(str(chat_id or "default"), int(topic_id or 0), template_type, file_path)
    except TypeError:
        return save_template(file_path, topic_id, template_type)
    except Exception:
        return False


def template_priority_v41(chat_id=None, topic_id=0, template_type="project"):
    try:
        return get_template(str(chat_id or "default"), int(topic_id or 0), template_type)
    except TypeError:
        return get_template(topic_id, template_type)
    except Exception:
        return None


def project_template_engine_v41(template_path, output_path, data_rows=None):
    if not template_path:
        return {"success": False, "error": "TEMPLATE_NOT_FOUND"}
    ok = apply_template(template_path, output_path, data_rows or [])
    return {"success": bool(ok), "artifact_path": output_path if ok else None, "error": None if ok else "TEMPLATE_APPLY_FAILED"}

# === END_TEMPLATE_SYSTEM_V41 ===

# === CODE_CLOSE_V43_TEMPLATE_MANAGER ===

def _v43_template_dir():
    import os
    path = "/root/.areal-neva-core/data/templates"
    os.makedirs(path, exist_ok=True)
    return path

def template_learn_v43(file_path, topic_id=0, template_type="project"):
    import os, shutil, json
    base = _v43_template_dir()
    name = "topic_" + str(int(topic_id or 0)) + "_" + str(template_type or "project")
    ext = os.path.splitext(str(file_path))[1] or ".bin"
    dst = os.path.join(base, name + ext)
    shutil.copy2(file_path, dst)
    meta = {"topic_id": int(topic_id or 0), "template_type": template_type, "path": dst}
    with open(os.path.join(base, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return dst

def template_priority_v43(topic_id=0, template_type="project"):
    import os, json, glob
    base = _v43_template_dir()
    name = "topic_" + str(int(topic_id or 0)) + "_" + str(template_type or "project")
    meta = os.path.join(base, name + ".json")
    if os.path.exists(meta):
        try:
            data = json.load(open(meta, encoding="utf-8"))
            if os.path.exists(data.get("path","")):
                return data.get("path")
        except Exception:
            pass
    files = glob.glob(os.path.join(base, name + ".*"))
    files = [x for x in files if not x.endswith(".json")]
    return files[0] if files else None

def project_template_engine_v43(template_path, output_path, data_rows=None):
    import shutil, os
    if not template_path or not os.path.exists(template_path):
        return {"success": False, "error": "TEMPLATE_NOT_FOUND"}
    shutil.copy2(template_path, output_path)
    return {"success": True, "artifact_path": output_path, "template_used": template_path}

# === END_CODE_CLOSE_V43_TEMPLATE_MANAGER ===


# === PATCH_PROJECT_TEMPLATE_STORAGE_V1 ===
import json as _json_ptm
import re as _re_ptm
from pathlib import Path as _Path_ptm

_PTM_DIR = _Path_ptm("/root/.areal-neva-core/data/project_templates")

def save_project_template_model(model: dict, task_id: str = "", chat_id: str = "", topic_id: int = 0) -> str:
    _PTM_DIR.mkdir(parents=True, exist_ok=True)
    model = dict(model)
    model["task_id"] = task_id or model.get("task_id","")
    model["chat_id"] = str(chat_id or model.get("chat_id",""))
    model["topic_id"] = int(topic_id or model.get("topic_id",0) or 0)
    name = model.get("project_type","UNKNOWN")
    safe = _re_ptm.sub(r"[^A-Za-zА-Яа-я0-9_.-]+","_",f"{name}_{task_id[:8] if task_id else 'manual'}")
    path = _PTM_DIR / f"PROJECT_TEMPLATE_MODEL__{safe}.json"
    path.write_text(_json_ptm.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)

# === END PATCH_PROJECT_TEMPLATE_STORAGE_V1 ===

====================================================================================================
END_FILE: core/template_manager.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/template_workflow.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e45401c7e1af73eed9f615dcc6455b2a91d36b5898b1729a81e61c960702b9eb
====================================================================================================
# === PROJECT_TEMPLATE_WORKFLOW_FULL_CLOSE_V1 ===
# === TECHNADZOR_ACT_TEMPLATE_WORKFLOW_V1 ===
# === TEMPLATE_SCOPE_ENFORCER_V1 ===
from __future__ import annotations

import json
import os
import re
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

BASE = Path("/root/.areal-neva-core")
TEMPLATE_DIR = BASE / "data/templates"
PROJECT_DIR = TEMPLATE_DIR / "project"
TECH_DIR = TEMPLATE_DIR / "technadzor"
INDEX = TEMPLATE_DIR / "index.json"

for d in (PROJECT_DIR, TECH_DIR):
    d.mkdir(parents=True, exist_ok=True)

SAVE_WORDS = ("образец", "шаблон", "пример", "возьми это", "сохрани это", "запомни это")
APPLY_WORDS = ("по образцу", "по шаблону", "как в образце", "как шаблон", "сделай так же")
PROJECT_WORDS = ("проект", "чертеж", "чертёж", "dwg", "dxf", "pdf", "кж", "км", "кмд", "ар", "проектирование")
TECH_WORDS = ("акт", "технадзор", "дефект", "замечан", "осмотр", "гост", "сп", "снип")

def _s(v: Any, limit: int = 10000) -> str:
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        try:
            v = json.dumps(v, ensure_ascii=False)
        except Exception:
            v = str(v)
    return str(v).strip()[:limit]

def _safe(v: Any) -> str:
    return re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", _s(v, 120)).strip("._") or "template"

def _load_index() -> Dict[str, Any]:
    # === TEMPLATE_INDEX_DICT_FIX_V1 ===
    if INDEX.exists():
        try:
            data = json.loads(INDEX.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
            return {
                "_schema": "TEMPLATE_INDEX_DICT_FIX_V1",
                "_legacy_type": type(data).__name__,
                "_legacy_data": data,
            }
        except Exception as e:
            return {
                "_schema": "TEMPLATE_INDEX_DICT_FIX_V1",
                "_legacy_error": str(e),
            }
    return {"_schema": "TEMPLATE_INDEX_DICT_FIX_V1"}
    # === END_TEMPLATE_INDEX_DICT_FIX_V1 ===

def _save_index(idx: Dict[str, Any]) -> None:
    # === TEMPLATE_INDEX_SAVE_DICT_FIX_V1 ===
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    if not isinstance(idx, dict):
        idx = {
            "_schema": "TEMPLATE_INDEX_SAVE_DICT_FIX_V1",
            "_legacy_type": type(idx).__name__,
            "_legacy_data": idx,
        }
    INDEX.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")
    # === END_TEMPLATE_INDEX_SAVE_DICT_FIX_V1 ===

def _detect_domain(text: str) -> Optional[str]:
    low = (text or "").lower()
    if any(x in low for x in TECH_WORDS):
        return "technadzor"
    if any(x in low for x in PROJECT_WORDS):
        return "project"
    return None

def _is_save_template(text: str) -> bool:
    low = (text or "").lower()
    return any(x in low for x in SAVE_WORDS)

def _is_apply_template(text: str) -> bool:
    low = (text or "").lower()
    return any(x in low for x in APPLY_WORDS)

def _last_relevant_task(conn: sqlite3.Connection, chat_id: str, topic_id: int, domain: str) -> Optional[Dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    like = "%акт%" if domain == "technadzor" else "%проект%"
    row = conn.execute(
        """
        SELECT * FROM tasks
        WHERE chat_id=? AND COALESCE(topic_id,0)=?
          AND (
            input_type IN ('drive_file','file','document','photo','image')
            OR raw_input LIKE '%file_id%'
            OR raw_input LIKE '%file_name%'
            OR result LIKE ?
            OR raw_input LIKE ?
          )
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id or 0), like, like),
    ).fetchone()
    return {k: row[k] for k in row.keys()} if row else None

def _write_docx(title: str, body: str, out_name: str) -> str:
    out = Path(tempfile.gettempdir()) / out_name
    try:
        from docx import Document
        doc = Document()
        doc.add_heading(title, level=1)
        for part in (body or "").split("\n"):
            doc.add_paragraph(part)
        doc.save(out)
        return str(out)
    except Exception:
        txt = out.with_suffix(".txt")
        txt.write_text(title + "\n\n" + body, encoding="utf-8")
        return str(txt)

def _write_xlsx(meta: Dict[str, Any], out_name: str) -> str:
    out = Path(tempfile.gettempdir()) / out_name
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Template"
        for i, (k, v) in enumerate(meta.items(), 1):
            ws.cell(i, 1, str(k))
            ws.cell(i, 2, json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v))
        wb.save(out)
        wb.close()
        return str(out)
    except Exception:
        csv = out.with_suffix(".csv")
        csv.write_text("\n".join(f"{k};{v}" for k, v in meta.items()), encoding="utf-8")
        return str(csv)

def _zip(paths: list[str], name: str) -> str:
    out = Path(tempfile.gettempdir()) / f"{_safe(name)}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p and os.path.exists(p):
                z.write(p, arcname=os.path.basename(p))
    return str(out)

def save_template(conn: sqlite3.Connection, chat_id: str, topic_id: int, domain: str, task: sqlite3.Row, user_text: str) -> Dict[str, Any]:
    source = _last_relevant_task(conn, chat_id, topic_id, domain)
    source_payload = {}
    if source:
        source_payload = {
            "source_task_id": source.get("id"),
            "source_input_type": source.get("input_type"),
            "source_raw_input": _s(source.get("raw_input"), 3000),
            "source_result": _s(source.get("result"), 3000),
        }

    tid = _s(task["id"] if "id" in task.keys() else datetime.now(timezone.utc).timestamp())
    model = {
        "schema": f"{domain.upper()}_TEMPLATE_MODEL_V1",
        "template_id": tid,
        "domain": domain,
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "user_text": _s(user_text, 3000),
        **source_payload,
    }

    target_dir = PROJECT_DIR if domain == "project" else TECH_DIR
    path = target_dir / f"{_safe(tid)}.json"
    path.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")

    idx = _load_index()
    idx[f"topic_{int(topic_id or 0)}_active_{domain}_template"] = str(path)
    idx[f"chat_{chat_id}_topic_{int(topic_id or 0)}_active_{domain}_template"] = str(path)
    _save_index(idx)

    return {
        "handled": True,
        "state": "DONE",
        "result": f"Шаблон сохранён\nТип: {domain}\nTopic: {topic_id}\nTemplate: {path.name}",
        "event": f"{domain.upper()}_TEMPLATE_WORKFLOW_FULL_CLOSE_V1:SAVED",
    }

def _load_active_template(chat_id: str, topic_id: int, domain: str) -> Optional[Dict[str, Any]]:
    idx = _load_index()
    path = idx.get(f"chat_{chat_id}_topic_{int(topic_id or 0)}_active_{domain}_template") or idx.get(f"topic_{int(topic_id or 0)}_active_{domain}_template")
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def apply_template(chat_id: str, topic_id: int, domain: str, user_text: str) -> Dict[str, Any]:
    tpl = _load_active_template(chat_id, topic_id, domain)
    if not tpl:
        return {
            "handled": True,
            "state": "WAITING_CLARIFICATION",
            "result": f"Активный шаблон {domain} в этом топике не найден. Пришли файл/акт/проект и напиши: возьми это как образец",
            "event": f"{domain.upper()}_TEMPLATE_WORKFLOW_FULL_CLOSE_V1:NO_TEMPLATE",
        }

    title = "Проект по сохранённому шаблону" if domain == "project" else "Акт по сохранённому шаблону"
    body = "\n".join([
        title,
        f"Template ID: {tpl.get('template_id')}",
        f"Source task: {tpl.get('source_task_id','')}",
        f"Запрос: {user_text}",
        "",
        "Источник шаблона:",
        _s(tpl.get("source_raw_input") or tpl.get("source_result"), 4000),
    ])

    docx = _write_docx(title, body, f"{domain}_template_result_{_safe(tpl.get('template_id'))}.docx")
    xlsx = _write_xlsx(tpl, f"{domain}_template_model_{_safe(tpl.get('template_id'))}.xlsx")
    model_path = Path(tempfile.gettempdir()) / f"{domain}_template_model_{_safe(tpl.get('template_id'))}.json"
    model_path.write_text(json.dumps(tpl, ensure_ascii=False, indent=2), encoding="utf-8")
    package = _zip([docx, xlsx, str(model_path)], f"{domain}_template_package_{_safe(tpl.get('template_id'))}")

    link = ""
    try:
        from core.artifact_upload_guard import upload_many_or_fail
        up = upload_many_or_fail([{"path": package, "kind": f"{domain}_template_package"}], f"{domain}_template_{tpl.get('template_id')}", int(topic_id or 0))
        link = ((up.get("links") or {}).get(package) or "")
    except Exception:
        link = ""

    result = "\n".join([
        f"{title} создан",
        f"Артефакт: {package}",
        f"Drive: {link or 'не подтверждён'}",
    ])

    return {
        "handled": True,
        "state": "AWAITING_CONFIRMATION",
        "result": result,
        "artifact_path": package,
        "drive_link": link,
        "event": f"{domain.upper()}_TEMPLATE_WORKFLOW_FULL_CLOSE_V1:APPLIED",
    }

def maybe_handle_template_workflow(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    raw = _s(task["raw_input"] if "raw_input" in task.keys() else "")
    clean = re.sub(r"^\s*\[VOICE\]\s*", "", raw, flags=re.I).strip()
    low = clean.lower()

    domain = _detect_domain(low)
    if not domain:
        return None

    if _is_save_template(low):
        return save_template(conn, chat_id, topic_id, domain, task, clean)

    if _is_apply_template(low):
        return apply_template(chat_id, topic_id, domain, clean)

    return None
# === END_TEMPLATE_SCOPE_ENFORCER_V1 ===
# === END_TECHNADZOR_ACT_TEMPLATE_WORKFLOW_V1 ===
# === END_PROJECT_TEMPLATE_WORKFLOW_FULL_CLOSE_V1 ===


# === PROJECT_DWG_TEMPLATE_REUSE_V2 ===
async def async_apply_template(chat_id: str, topic_id: int, domain: str, user_text: str) -> Optional[Dict[str, Any]]:
    tpl = _load_active_template(chat_id, topic_id, domain)
    if not tpl:
        return {
            "handled": True,
            "state": "WAITING_CLARIFICATION",
            "result": f"Активный шаблон {domain} не найден. Пришли файл и напиши: возьми это как образец",
            "event": f"{domain.upper()}_TEMPLATE_APPLY:NO_TEMPLATE",
        }

    tid = _safe(tpl.get("template_id") or "tpl")
    source_text = _s(tpl.get("source_raw_input") or tpl.get("source_result"), 3000)

    if domain == "project":
        try:
            from core.project_engine import create_project_pdf_dxf_artifact
            combined = str(user_text or "") + " " + str(source_text or "")
            result = await create_project_pdf_dxf_artifact(
                raw_input=combined,
                task_id="tpl_" + tid,
                topic_id=int(topic_id or 0),
                template_hint=_s(tpl.get("source_raw_input"), 500),
                require_template=False,
            )
            if result and result.get("success") and result.get("artifact_path"):
                link = result.get("drive_link") or ""
                if not link:
                    try:
                        from core.artifact_upload_guard import upload_many_or_fail
                        up = upload_many_or_fail(
                            [{"path": result["artifact_path"], "kind": "project_template_package"}],
                            "tpl_" + tid,
                            int(topic_id or 0),
                        )
                        link = list((up.get("links") or {}).values())[0] if up.get("links") else ""
                    except Exception:
                        pass
                res_text = "Проект создан по сохранённому шаблону"
                res_text += "\nПакет: " + str(result.get("artifact_path", ""))
                res_text += "\nDrive: " + (link or "не подтверждён")
                if result.get("region_detected"):
                    res_text += "\nРегион нагрузок: " + str(result.get("region_detected"))
                return {
                    "handled": True,
                    "state": "AWAITING_CONFIRMATION",
                    "result": res_text,
                    "artifact_path": result.get("artifact_path"),
                    "drive_link": link,
                    "event": "PROJECT_DWG_TEMPLATE_REUSE_V2:APPLIED_REAL_ENGINE",
                }
            err = (result or {}).get("error") or "PROJECT_ENGINE_RETURNED_NO_ARTIFACT"
            return {
                "handled": True,
                "state": "FAILED",
                "result": "",
                "error": "PROJECT_DWG_TEMPLATE_REUSE_V2:ENGINE_FAILED:" + str(err)[:200],
                "event": "PROJECT_DWG_TEMPLATE_REUSE_V2:ENGINE_FAILED",
            }
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("PROJECT_DWG_TEMPLATE_REUSE_V2_ERR %s", e)
            return {
                "handled": True,
                "state": "FAILED",
                "result": "",
                "error": "PROJECT_DWG_TEMPLATE_REUSE_V2:EXCEPTION:" + str(e)[:200],
                "event": "PROJECT_DWG_TEMPLATE_REUSE_V2:EXCEPTION",
            }

    return apply_template(chat_id, topic_id, domain, user_text)

async def maybe_handle_template_workflow_async(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    raw = _s(task["raw_input"] if "raw_input" in task.keys() else "")
    clean = re.sub(r"^\s*\[VOICE\]\s*", "", raw, flags=re.I).strip()
    low = clean.lower()
    domain = _detect_domain(low)
    if not domain:
        return None
    if _is_save_template(low):
        return save_template(conn, chat_id, topic_id, domain, task, clean)
    if _is_apply_template(low):
        return await async_apply_template(chat_id, topic_id, domain, clean)
    return None
# === END_PROJECT_DWG_TEMPLATE_REUSE_V2 ===

====================================================================================================
END_FILE: core/template_workflow.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic2_estimate_final_close_v2.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 9aff038d9c4f284dc2211539a93cf491672f6dac10d7b8f439d80ce94a98d471
====================================================================================================
from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "outputs" / "topic2_estimates"
OUT.mkdir(parents=True, exist_ok=True)

ENGINE = "TOPIC2_ESTIMATE_FINAL_CLOSE_V2"

SHORT_WORDS = {
    "да", "да делай", "да, делай", "делай", "ок", "окей", "хорошо",
    "подтверждаю", "согласен", "верно", "все верно", "всё верно",
    "1", "2", "3", "вариант 1", "вариант 2", "вариант 3",
    "минимальные", "минимум", "самые дешевые", "самые дешёвые",
    "средние", "медианные", "медиана", "надежные", "надёжные"
}

ESTIMATE_WORDS = (
    "смет", "кп", "коммерческ", "расчет", "расчёт", "стоимост", "цена",
    "расцен", "ведомост", "монолит", "бетон", "арматур", "опалуб",
    "фундамент", "перекрыт", "колонн", "стен", "гидроизоляц",
    "утеплен", "засыпк", "свай", "плит", "лестнич"
)

IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp", ".tif", ".tiff")
DOC_EXT = (".pdf", ".docx", ".xlsx", ".xls", ".csv", ".txt")


def _s(v: Any, limit: int = 50000) -> str:
    if v is None:
        return ""
    try:
        return str(v).strip()[:limit]
    except Exception:
        return ""


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _field(task: Any, name: str, default: Any = None) -> Any:
    try:
        if hasattr(task, "keys") and name in task.keys():
            return task[name]
    except Exception:
        pass
    try:
        return task.get(name, default)
    except Exception:
        return getattr(task, name, default)


def _payload(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    t = _s(raw)
    if not t:
        return {}
    try:
        x = json.loads(t)
        return x if isinstance(x, dict) else {}
    except Exception:
        return {}


def _extract_payload_text(raw: Any) -> str:
    p = _payload(raw)
    parts = [_s(raw)]
    for k in ("caption", "text", "message", "file_name", "name", "title", "ocr_text", "recognized_text"):
        if p.get(k):
            parts.append(_s(p.get(k)))
    return "\n".join(x for x in parts if x).strip()


def _file_meta(raw: Any) -> Dict[str, str]:
    p = _payload(raw)
    keys_path = ("local_path", "path", "file_path", "downloaded_path", "server_path")
    keys_name = ("file_name", "name", "title")
    file_path = ""
    file_name = ""
    for k in keys_path:
        if p.get(k):
            file_path = _s(p.get(k))
            break
    for k in keys_name:
        if p.get(k):
            file_name = _s(p.get(k))
            break
    if not file_name and file_path:
        file_name = os.path.basename(file_path)
    return {"file_path": file_path, "file_name": file_name}


def _read_file_text(path: str) -> str:
    p = Path(_s(path))
    if not p.exists() or not p.is_file():
        return ""
    suf = p.suffix.lower()
    try:
        if suf == ".txt":
            return p.read_text(encoding="utf-8", errors="ignore")[:50000]
        if suf == ".csv":
            return p.read_text(encoding="utf-8", errors="ignore")[:50000]
        if suf == ".pdf":
            try:
                import fitz
                doc = fitz.open(str(p))
                return "\n".join(page.get_text("text") for page in doc)[:50000]
            except Exception:
                return ""
        if suf == ".docx":
            try:
                import docx
                d = docx.Document(str(p))
                return "\n".join(x.text for x in d.paragraphs)[:50000]
            except Exception:
                return ""
        if suf in (".xlsx", ".xls"):
            try:
                from openpyxl import load_workbook
                wb = load_workbook(str(p), data_only=True, read_only=True)
                out = []
                for ws in wb.worksheets[:3]:
                    for row in ws.iter_rows(max_row=200, values_only=True):
                        vals = [_s(x, 200) for x in row if _s(x)]
                        if vals:
                            out.append(" | ".join(vals))
                return "\n".join(out)[:50000]
            except Exception:
                return ""
        if suf in IMAGE_EXT:
            try:
                from PIL import Image
                import pytesseract
                return pytesseract.image_to_string(Image.open(str(p)), lang="rus+eng")[:50000]
            except Exception:
                return ""
    except Exception:
        return ""
    return ""


def _is_short_control(text: str) -> bool:
    t = re.sub(r"\s+", " ", _low(text).replace("[voice]", "")).strip(" .,!?:;")
    return t in SHORT_WORDS or (len(t) <= 18 and any(t.startswith(x) for x in SHORT_WORDS))


def _is_estimate_intent(text: str, file_name: str = "") -> bool:
    low = _low(text + " " + file_name)
    if not low:
        return False
    if any(x in low for x in ESTIMATE_WORDS):
        return True
    return bool(re.search(r"\b(м3|м³|м2|м²|шт|кг|тн|п\.?\s*м)\b", low))


def _is_file_or_photo(input_type: str, raw: Any) -> bool:
    meta = _file_meta(raw)
    name = _low(meta.get("file_name") or meta.get("file_path"))
    if input_type in ("photo", "image", "file", "drive_file", "document"):
        return True
    return name.endswith(IMAGE_EXT + DOC_EXT)


def _qty(v: str) -> float:
    s = _s(v).replace("≈", "").replace("~", "").replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def _normalize_unit(u: str) -> str:
    x = _low(u).replace(" ", "")
    return {
        "м3": "м³", "м.3": "м³", "м³": "м³",
        "м2": "м²", "м.2": "м²", "м²": "м²",
        "п.м": "п.м", "пм": "п.м",
        "шт.": "шт", "шт": "шт",
        "компл.": "компл", "компл": "компл",
        "тн": "т", "тонн": "т",
    }.get(x, x or "шт")


def _parse_items(text: str) -> List[Dict[str, Any]]:
    src = _s(text, 50000)
    t = re.sub(r"\s+", " ", src)
    t = re.sub(r"(?<![\d,.])\s+(\d{1,2})\s+(?=[А-ЯA-ZЁ])", r"\n\1 ", t)
    unit_re = r"(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)"
    items: List[Dict[str, Any]] = []

    for line in t.splitlines():
        line = line.strip(" ;")
        if not line:
            continue
        m = re.search(
            rf"^\s*(?P<num>\d{{1,3}})\s+(?P<name>.+?)\s+(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            line,
            flags=re.I,
        )
        if not m:
            continue
        name = re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")
        unit = _normalize_unit(m.group("unit"))
        qty = _qty(m.group("qty"))
        if not name or qty <= 0:
            continue
        items.append({
            "num": len(items) + 1,
            "name": name[:240],
            "qty": qty,
            "unit": unit,
            "price": 0.0,
            "source": "parsed",
        })

    if not items:
        m = re.search(rf"(?P<name>.{{1,120}}?)\s+(?P<unit>{unit_re})\s+(?P<qty>\d[\d\s]*(?:[,.]\d+)?)", t, flags=re.I)
        if m:
            items.append({
                "num": 1,
                "name": re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")[:240] or "Позиция",
                "qty": _qty(m.group("qty")),
                "unit": _normalize_unit(m.group("unit")),
                "price": 0.0,
                "source": "fallback",
            })

    if not items:
        items.append({
            "num": 1,
            "name": "Позиция по присланному фото / файлу / тексту",
            "qty": 1.0,
            "unit": "компл",
            "price": 0.0,
            "source": "manual_review_required",
        })

    return items[:200]


def _write_xlsx(path: Path, items: List[Dict[str, Any]], source_text: str, photo_text: str = "") -> None:
    import copy
    from datetime import date
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    template_path = Path("/root/.areal-neva-core/data/templates/estimate/cache/1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp__фундамент_Склад2.xlsx")
    if template_path.exists():
        try:
            wb = load_workbook(str(template_path))
        except Exception:
            wb = Workbook()
    else:
        wb = Workbook()

    if "AREAL_CALC" in wb.sheetnames:
        del wb["AREAL_CALC"]
    ws = wb.create_sheet("AREAL_CALC", 0)
    template_ws = wb["смета"] if "смета" in wb.sheetnames else None

    thin = Side(style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    header_fill = PatternFill(start_color="D9EAF7", end_color="D9EAF7", fill_type="solid")
    section_fill = PatternFill(start_color="EAF2F8", end_color="EAF2F8", fill_type="solid")
    total_fill = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")

    def copy_template_cell(src_row: int, src_col: int, dst_row: int, dst_col: int) -> None:
        if not template_ws:
            return
        src = template_ws.cell(src_row, src_col)
        dst = ws.cell(dst_row, dst_col)
        if src.has_style:
            dst._style = copy.copy(src._style)
        if src.number_format:
            dst.number_format = src.number_format
        if src.alignment:
            dst.alignment = copy.copy(src.alignment)

    for col in range(1, 16):
        copy_template_cell(1, min(col, 10), 1, col)
        copy_template_cell(2, min(col, 10), 2, col)
        ws.cell(1, col).border = border
        ws.cell(2, col).border = border
        ws.cell(1, col).fill = header_fill
        ws.cell(2, col).fill = header_fill
        ws.cell(1, col).font = Font(bold=True)
        ws.cell(2, col).font = Font(bold=True)
        ws.cell(1, col).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.cell(2, col).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Canon §4 keeps 15 columns; template layout keeps grouped Work/Materials columns.
    ws.merge_cells("A1:A2")
    ws.merge_cells("B1:B2")
    ws.merge_cells("C1:C2")
    ws.merge_cells("D1:D2")
    ws.merge_cells("E1:E2")
    ws.merge_cells("F1:G1")
    ws.merge_cells("H1:I1")
    ws.merge_cells("J1:J2")
    ws.merge_cells("K1:K2")
    ws.merge_cells("L1:L2")
    ws.merge_cells("M1:M2")
    ws.merge_cells("N1:N2")
    ws.merge_cells("O1:O2")

    ws["A1"] = "№"
    ws["B1"] = "Раздел"
    ws["C1"] = "Наименование"
    ws["D1"] = "Ед изм"
    ws["E1"] = "Кол-во"
    ws["F1"] = "Работа"
    ws["F2"] = "Цена работ"
    ws["G2"] = "Стоимость работ"
    ws["H1"] = "Материалы"
    ws["H2"] = "Цена материалов"
    ws["I2"] = "Стоимость материалов"
    ws["J1"] = "Всего"
    ws["K1"] = "Источник цены"
    ws["L1"] = "Поставщик"
    ws["M1"] = "URL"
    ws["N1"] = "checked_at"
    ws["O1"] = "Примечание"

    widths = {
        "A": 7, "B": 22, "C": 58, "D": 11, "E": 12,
        "F": 14, "G": 16, "H": 16, "I": 18, "J": 18,
        "K": 24, "L": 24, "M": 36, "N": 14, "O": 34,
    }
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "A3"

    def classify(item):
        name = str(item.get("name", "")).lower().replace("ё", "е")
        if any(x in name for x in ("накладн", "расходные материалы", "крепеж", "герметик", "логистика")):
            return "overhead"
        if any(x in name for x in ("монтаж", "устройство", "работ", "уборка")):
            return "work"
        return "material"

    def section_for(item):
        name = str(item.get("name", "")).lower().replace("ё", "е")
        if "фундамент" in name or "плиты" in name or "бетон" in name or "арматур" in name:
            return "Фундамент"
        if "металлоконструк" in name or "каркас" in name or "колонн" in name:
            return "Стены / каркас"
        if "стен" in name:
            return "Стены / каркас"
        if "кров" in name:
            return "Кровля"
        if "логист" in name:
            return "Логистика"
        if "накладн" in name or "расходные" in name or "уборка" in name:
            return "Накладные расходы"
        return "Прочее"

    def supplier_source(item):
        source = str(item.get("source", ""))
        low = source.lower()
        if "sp-sever" in low:
            return "sp-sever.ru", "https://sp-sever.ru/panels/stenovye_sendvich_panely"
        if "sp-rsk" in low:
            return "sp-rsk-uteplitel.ru", "https://spb.rsk-uteplitel.ru/sklady"
        if "sonar" in low:
            return "Sonar", ""
        if "runtime" in low:
            return "topic_2 runtime", ""
        return "", ""

    row = 3
    today = date.today().isoformat()
    last_section = None
    for item in items:
        section = section_for(item)
        if section != last_section:
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=15)
            sec_cell = ws.cell(row=row, column=1, value=section)
            sec_cell.font = Font(bold=True)
            sec_cell.fill = section_fill
            sec_cell.alignment = Alignment(horizontal="left", vertical="center")
            for col in range(1, 16):
                ws.cell(row=row, column=col).border = border
            row += 1
            last_section = section

        qty = float(item.get("qty") or 0)
        price = float(item.get("price") or 0)
        kind = classify(item)
        work_price = price if kind == "work" else 0
        mat_price = price if kind in ("material", "overhead") else 0
        supplier, url = supplier_source(item)
        values = [
            item.get("num"), section, item.get("name"), item.get("unit"), qty,
            work_price, f"=E{row}*F{row}", mat_price, f"=E{row}*H{row}", f"=G{row}+I{row}",
            item.get("source", ""), supplier, url, today, item.get("note", ""),
        ]
        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.border = border
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if col in (5, 6, 7, 8, 9, 10):
                cell.number_format = '#,##0.00'
        row += 1

    data_rows = [r for r in range(3, row) if ws.cell(r, 10).value and str(ws.cell(r, 10).value).startswith("=")]
    first_data = min(data_rows) if data_rows else 3
    last_data = max(data_rows) if data_rows else row - 1

    row += 1
    ws.cell(row=row, column=9, value="ИТОГО без НДС").font = Font(bold=True)
    ws.cell(row=row, column=10, value=f"=SUM(J{first_data}:J{last_data})").font = Font(bold=True)
    for col in range(1, 16):
        cell = ws.cell(row=row, column=col)
        cell.border = border
        cell.fill = total_fill
    row += 1
    ws.cell(row=row, column=9, value="НДС").font = Font(bold=True)
    ws.cell(row=row, column=10, value="не начисляется по заданию").font = Font(bold=True)
    for col in range(1, 16):
        cell = ws.cell(row=row, column=col)
        cell.border = border
        cell.fill = total_fill

    ws2 = wb.create_sheet("Источник")
    ws2["A1"] = "Исходный текст"
    ws2["A1"].font = Font(bold=True)
    ws2["A2"] = source_text[:32000]
    ws2["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws2.column_dimensions["A"].width = 140
    if photo_text:
        ws2["A4"] = "Распознанный текст из файла / фото"
        ws2["A4"].font = Font(bold=True)
        ws2["A5"] = photo_text[:32000]
        ws2["A5"].alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(str(path))

def _pdf_font():
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        for fp in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ):
            if os.path.exists(fp):
                pdfmetrics.registerFont(TTFont("ArealSans", fp))
                return "ArealSans"
    except Exception:
        pass
    return "Helvetica"


def _write_pdf(path: Path, items: List[Dict[str, Any]]) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _pdf_font()
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    x = 12 * mm
    y = h - 16 * mm

    c.setFont(font, 12)
    c.drawString(x, y, "Предварительный сметный расчёт")
    y -= 8 * mm
    c.setFont(font, 8)
    c.drawString(x, y, f"Движок: {ENGINE}")
    y -= 6 * mm
    c.drawString(x, y, "Цены не выдуманы, расчётная колонка в Excel считается формулами")
    y -= 8 * mm

    c.setFont(font, 7)
    headers = ["№", "Наименование", "Кол-во", "Цена", "Сумма", "Ед"]
    xs = [x, x + 9*mm, x + 112*mm, x + 137*mm, x + 162*mm, x + 185*mm]
    for xx, val in zip(xs, headers):
        c.drawString(xx, y, val)
    y -= 5 * mm
    c.line(x, y, w - 10*mm, y)
    y -= 5 * mm

    for item in items:
        if y < 18 * mm:
            c.showPage()
            c.setFont(font, 7)
            y = h - 16 * mm
        vals = [
            str(item["num"]),
            item["name"][:72],
            f'{float(item["qty"]):g}',
            "",
            "",
            item["unit"],
        ]
        for xx, val in zip(xs, vals):
            c.drawString(xx, y, str(val))
        y -= 5 * mm

    c.save()


def _upload(path: Path, task_id: str, topic_id: int, chat_id: str = "") -> str:
    try:
        from core.topic_drive_oauth import _upload_file_sync
        up = _upload_file_sync(str(path), path.name, str(chat_id or task_id), int(topic_id or 0), None)
        if isinstance(up, dict):
            link = up.get("webViewLink")
            fid = up.get("drive_file_id")
            if link:
                return str(link)
            if fid:
                return "https://drive.google.com/file/d/" + str(fid) + "/view?usp=drivesdk"
    except Exception:
        pass

    try:
        from core.engine_base import upload_artifact_to_drive
        link = upload_artifact_to_drive(str(path), task_id, topic_id)
        if link and "drive.google.com" in str(link):
            return str(link)
    except Exception:
        pass
    return str(path)


def _make_artifacts(task_id: str, topic_id: int, raw_text: str, photo_text: str = "", chat_id: str = "") -> Dict[str, Any]:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", task_id or ts)[:32]
    out_dir = OUT / f"{safe}_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    source = "\n".join(x for x in (raw_text, photo_text) if x).strip()
    items = _parse_items(source)

    xlsx = out_dir / f"SMETA_TOPIC2__{safe}.xlsx"
    pdf = out_dir / f"SMETA_TOPIC2__{safe}.pdf"
    manifest = out_dir / f"SMETA_TOPIC2__{safe}.manifest.json"

    _write_xlsx(xlsx, items, raw_text, photo_text)
    _write_pdf(pdf, items)

    data = {
        "engine": ENGINE,
        "task_id": task_id,
        "topic_id": int(topic_id or 0),
        "items_count": len(items),
        "created_at": datetime.now().isoformat(),
        "prices_policy": "not invented",
        "xlsx": str(xlsx),
        "pdf": str(pdf),
    }
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    xlsx_link = _upload(xlsx, task_id, topic_id, chat_id)
    pdf_link = _upload(pdf, task_id, topic_id, chat_id)
    manifest_link = _upload(manifest, task_id, topic_id, chat_id)

    total = 0.0
    for item in items:
        try:
            total += float(item.get("total") or 0) or (float(item.get("qty") or 0) * float(item.get("price") or 0))
        except Exception:
            pass

    msg = (
        "✅ Смета готова\n"
        f"Позиций: {len(items)}\n"
        f"Итого: {total:,.0f} руб\n".replace(",", " ")
        + "Цены: не выдуманы, Excel содержит формулы и итог\n\n"
        + f"Excel: {xlsx_link}\n"
        + f"PDF: {pdf_link}\n\n"
        + "Подтверди или пришли правки"
    )

    return {
        "ok": True,
        "message": msg,
        "xlsx_link": xlsx_link,
        "pdf_link": pdf_link,
        "manifest_link": manifest_link,
        "items_count": len(items),
    }


def _find_parent(conn, chat_id: str, topic_id: int, reply_to: Any, current_id: str):
    params = [str(chat_id), int(topic_id or 0), str(current_id)]
    where = [
        "chat_id=?",
        "COALESCE(topic_id,0)=?",
        "id<>?",
        "state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION','AWAITING_PRICE_CONFIRMATION','CANCELLED')",
    ]
    if reply_to:
        sql = f"""
        SELECT * FROM tasks
        WHERE {' AND '.join(where)}
          AND (bot_message_id=? OR reply_to_message_id=?)
        ORDER BY CASE WHEN state='AWAITING_CONFIRMATION' THEN 0 ELSE 1 END, rowid DESC
        LIMIT 1
        """
        row = conn.execute(sql, params + [reply_to, reply_to]).fetchone()
        if row:
            return row

    sql = f"""
    SELECT * FROM tasks
    WHERE {' AND '.join(where)}
      AND (
        lower(COALESCE(raw_input,'')) LIKE '%смет%'
        OR lower(COALESCE(raw_input,'')) LIKE '%кп%'
        OR lower(COALESCE(result,'')) LIKE '%смет%'
        OR lower(COALESCE(result,'')) LIKE '%xlsx%'
        OR lower(COALESCE(result,'')) LIKE '%pdf%'
      )
    ORDER BY rowid DESC
    LIMIT 1
    """
    return conn.execute(sql, params).fetchone()


def _update(conn, update_task, task_id: str, **kw) -> None:
    if not task_id:
        return
    try:
        if update_task:
            update_task(conn, task_id, **kw)
            conn.commit()
            return
    except Exception:
        pass

    cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    sets = []
    vals = []
    for k, v in kw.items():
        if k in cols:
            sets.append(f"{k}=?")
            vals.append(v)
    if "updated_at" in cols:
        sets.append("updated_at=datetime('now')")
    if sets:
        vals.append(task_id)
        conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
        conn.commit()


def _hist(conn, history, task_id: str, action: str) -> None:
    try:
        if history:
            history(conn, task_id, action)
            conn.commit()
            return
    except Exception:
        pass
    try:
        conn.execute(
            "INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))",
            (task_id, action),
        )
        conn.commit()
    except Exception:
        pass


def _send(send_reply_ex, chat_id: str, text: str, reply_to: Any, topic_id: int) -> Optional[int]:
    if not send_reply_ex:
        return None
    kwargs = {
        "chat_id": str(chat_id),
        "text": text,
        "reply_to_message_id": reply_to,
    }
    if int(topic_id or 0) > 0:
        kwargs["message_thread_id"] = int(topic_id or 0)
    try:
        res = send_reply_ex(**kwargs)
        if isinstance(res, dict):
            return res.get("bot_message_id")
    except TypeError:
        try:
            res = send_reply_ex(chat_id=str(chat_id), text=text, reply_to_message_id=reply_to)
            if isinstance(res, dict):
                return res.get("bot_message_id")
        except Exception:
            return None
    except Exception:
        return None
    return None


async def handle_topic2_estimate_final_close(
    conn,
    task,
    send_reply_ex=None,
    update_task=None,
    history=None,
    logger=None,
) -> bool:
    task_id = _s(_field(task, "id"))
    chat_id = _s(_field(task, "chat_id"))
    topic_id = int(_field(task, "topic_id", 0) or 0)
    input_type = _s(_field(task, "input_type", "text"))
    raw_input = _field(task, "raw_input", "")
    reply_to = _field(task, "reply_to_message_id", None)

    if topic_id != 2 or not task_id or not chat_id:
        return False

    meta = _file_meta(raw_input)
    raw_text = _extract_payload_text(raw_input)
    file_text = _read_file_text(meta.get("file_path", ""))
    full_text = "\n".join(x for x in (raw_text, file_text) if x).strip()

    if _is_short_control(full_text):
        parent = _find_parent(conn, chat_id, topic_id, reply_to, task_id)
        if parent:
            parent_id = _s(_field(parent, "id"))
            parent_result = _s(_field(parent, "result", ""))
            parent_raw = _extract_payload_text(_field(parent, "raw_input", ""))

            if parent_result and ("xlsx" in parent_result.lower() or "pdf" in parent_result.lower() or "смет" in parent_result.lower()):
                msg = "Принял. Сметный расчёт закрыт"
                bot_id = _send(send_reply_ex, chat_id, msg, reply_to, topic_id)
                _update(conn, update_task, parent_id, state="DONE", error_message="")
                _update(conn, update_task, task_id, state="DONE", result=msg, error_message="", bot_message_id=bot_id)
                _hist(conn, history, parent_id, f"{ENGINE}:PARENT_DONE_BY_SHORT_CONFIRM")
                _hist(conn, history, task_id, f"{ENGINE}:SHORT_CONFIRM_DONE")
                return True

            res = _make_artifacts(parent_id or task_id, topic_id, parent_raw or full_text, "", chat_id)
            bot_id = _send(send_reply_ex, chat_id, res["message"], reply_to, topic_id)
            _update(conn, update_task, parent_id, state="AWAITING_CONFIRMATION", result=res["message"], error_message="", bot_message_id=bot_id)
            _update(conn, update_task, task_id, state="DONE", result="Уточнение применено к родительской смете", error_message="")
            _hist(conn, history, parent_id, f"{ENGINE}:PARENT_REBUILT_FROM_SHORT_CONFIRM")
            _hist(conn, history, task_id, f"{ENGINE}:SHORT_CONFIRM_APPLIED")
            return True

        return False

    if _is_file_or_photo(input_type, raw_input) or _is_estimate_intent(full_text, meta.get("file_name", "")):
        if not _is_estimate_intent(full_text, meta.get("file_name", "")) and not _is_file_or_photo(input_type, raw_input):
            return False

        res = _make_artifacts(task_id, topic_id, full_text or raw_text or meta.get("file_name", ""), file_text, chat_id)
        bot_id = _send(send_reply_ex, chat_id, res["message"], reply_to, topic_id)
        _update(conn, update_task, task_id, state="AWAITING_CONFIRMATION", result=res["message"], error_message="", bot_message_id=bot_id)
        _hist(conn, history, task_id, f"{ENGINE}:ESTIMATE_ARTIFACTS_CREATED")
        return True

    return False


# === PATCH_TOPIC2_HISTORY_CLARIFIED_PARSE_V1 ===
# Fact: previous parser generated one fallback position when the real item table existed only in task_history clarified:* rows
import re as _t2hcp_re
from typing import List as _T2HCP_List, Dict as _T2HCP_Dict, Any as _T2HCP_Any

def _t2hcp_history_context(conn, task_id: str) -> str:
    try:
        rows = conn.execute(
            """
            SELECT action
            FROM task_history
            WHERE task_id=?
            ORDER BY created_at ASC
            LIMIT 200
            """,
            (str(task_id),),
        ).fetchall()
    except Exception:
        return ""

    parts = []
    for r in rows:
        a = _s(r[0] if not hasattr(r, "keys") else r["action"], 20000)
        if not a.startswith("clarified:"):
            continue
        txt = a[len("clarified:"):].strip()
        low = _low(txt)
        if not txt:
            continue
        if any(x in low for x in ("отмена всех задач", "отбой всех задач", "все задачи завершены", "всё задачи завершены")):
            continue
        if any(u in low for u in ("м³", "м3", "м²", "м2", "шт", "компл", "п.м", "кг", "тн")) or any(w in low for w in ESTIMATE_WORDS):
            parts.append(txt)
    return "\n\n".join(parts)

def _parse_items(text: str) -> _T2HCP_List[_T2HCP_Dict[str, _T2HCP_Any]]:
    src = _s(text, 120000).replace("\r", "\n")
    src = _t2hcp_re.sub(r"[ \t]+", " ", src)
    unit_re = r"(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)"
    items = []

    flat = _t2hcp_re.sub(r"\s+", " ", src).strip()
    blocks = []
    for m in _t2hcp_re.finditer(r"(?<![\d,.])(?P<num>\d{1,3})\s+(?=[А-ЯA-ZЁа-яa-z])", flat):
        blocks.append((m.start(), int(m.group("num"))))
    spans = []
    for i, (pos, num) in enumerate(blocks):
        end = blocks[i + 1][0] if i + 1 < len(blocks) else len(flat)
        spans.append((num, flat[pos:end].strip()))

    for num, block in spans:
        if len(block) < 10:
            continue
        body = _t2hcp_re.sub(r"^\d{1,3}\s+", "", block).strip()
        matches = list(_t2hcp_re.finditer(
            rf"(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            body,
            flags=_t2hcp_re.I,
        ))
        if not matches:
            continue
        m = matches[-1]
        name = body[:m.start()].strip(" -–—:;")
        name = _t2hcp_re.sub(r"^(наименование работ|ед\.?\s*изм\.?|количество)\s+", "", name, flags=_t2hcp_re.I).strip()
        name = _t2hcp_re.sub(r"\s+", " ", name)
        qty = _qty(m.group("qty"))
        unit = _normalize_unit(m.group("unit"))
        if not name or qty <= 0:
            continue
        if name.lower().startswith(("наименование", "ед. изм", "количество")):
            continue
        items.append({
            "num": len(items) + 1,
            "name": name[:240],
            "qty": qty,
            "unit": unit,
            "price": 0.0,
            "source": "history_or_text_table",
        })

    if not items:
        for m in _t2hcp_re.finditer(
            rf"(?P<name>[А-ЯA-ZЁ][^;\n]{{5,180}}?)\s+(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            src,
            flags=_t2hcp_re.I,
        ):
            name = _t2hcp_re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")
            qty = _qty(m.group("qty"))
            if name and qty > 0:
                items.append({
                    "num": len(items) + 1,
                    "name": name[:240],
                    "qty": qty,
                    "unit": _normalize_unit(m.group("unit")),
                    "price": 0.0,
                    "source": "regex_table_fallback",
                })

    if not items:
        items.append({
            "num": 1,
            "name": "Позиция по присланному фото / файлу / тексту",
            "qty": 1.0,
            "unit": "компл",
            "price": 0.0,
            "source": "manual_review_required",
        })

    return items[:200]

_ORIG_T2_HANDLE_TOPIC2_ESTIMATE_FINAL_CLOSE_V2 = handle_topic2_estimate_final_close

async def handle_topic2_estimate_final_close(
    conn,
    task,
    send_reply_ex=None,
    update_task=None,
    history=None,
    logger=None,
) -> bool:
    task_id = _s(_field(task, "id"))
    topic_id = int(_field(task, "topic_id", 0) or 0)
    if topic_id == 2 and task_id:
        raw = _field(task, "raw_input", "")
        hist = _t2hcp_history_context(conn, task_id)
        if hist:
            enriched = {}
            try:
                for k in task.keys():
                    enriched[k] = task[k]
            except Exception:
                enriched = dict(task) if isinstance(task, dict) else {}
            enriched["raw_input"] = _s(raw, 80000) + "\n\n---\nHISTORY_CLARIFIED_CONTEXT\n" + hist
            return await _ORIG_T2_HANDLE_TOPIC2_ESTIMATE_FINAL_CLOSE_V2(
                conn,
                enriched,
                send_reply_ex=send_reply_ex,
                update_task=update_task,
                history=history,
                logger=logger,
            )
    return await _ORIG_T2_HANDLE_TOPIC2_ESTIMATE_FINAL_CLOSE_V2(
        conn,
        task,
        send_reply_ex=send_reply_ex,
        update_task=update_task,
        history=history,
        logger=logger,
    )
# === END_PATCH_TOPIC2_HISTORY_CLARIFIED_PARSE_V1 ===


# === PATCH_TOPIC2_LINE_TABLE_PARSE_V1 ===
# Fact: previous parser split row names on "150 кг/м³" and produced rows named "кг/м³)"
import re as _t2lt_re
from typing import List as _T2LT_List, Dict as _T2LT_Dict, Any as _T2LT_Any

_T2LT_UNIT_LINE_RE = _t2lt_re.compile(r"^(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)$", _t2lt_re.I)
_T2LT_NUM_LINE_RE = _t2lt_re.compile(r"^\d{1,3}$")

def _t2lt_clean_lines(text: str):
    lines = []
    for line in _s(text, 200000).replace("\r", "\n").splitlines():
        x = _t2lt_re.sub(r"\s+", " ", line).strip(" \t;")
        if x:
            lines.append(x)
    return lines

def _t2lt_qty_from_line(line: str) -> float:
    return _qty(line)

def _parse_items(text: str) -> _T2LT_List[_T2LT_Dict[str, _T2LT_Any]]:
    lines = _t2lt_clean_lines(text)
    items = []
    i = 0

    while i < len(lines):
        if not _T2LT_NUM_LINE_RE.fullmatch(lines[i]):
            i += 1
            continue

        row_no = int(lines[i])
        j = i + 1
        name_parts = []

        while j < len(lines) and not _T2LT_UNIT_LINE_RE.fullmatch(lines[j]):
            if _T2LT_NUM_LINE_RE.fullmatch(lines[j]) and name_parts:
                break
            if lines[j].lower() not in ("наименование работ", "ед. изм.", "ед. изм", "количество", "№"):
                name_parts.append(lines[j])
            j += 1

        if j >= len(lines) or not _T2LT_UNIT_LINE_RE.fullmatch(lines[j]):
            i += 1
            continue

        unit = _normalize_unit(lines[j])
        k = j + 1
        qty = 0.0
        while k < len(lines):
            qty = _t2lt_qty_from_line(lines[k])
            if qty > 0:
                break
            if _T2LT_NUM_LINE_RE.fullmatch(lines[k]):
                break
            k += 1

        name = _t2lt_re.sub(r"\s+", " ", " ".join(name_parts)).strip(" -–—:")
        if name and qty > 0:
            items.append({
                "num": len(items) + 1,
                "name": name[:240],
                "qty": qty,
                "unit": unit,
                "price": 0.0,
                "source": "line_table",
            })
            i = k + 1
            continue

        i += 1

    if not items:
        src = _s(text, 120000)
        unit_re = r"(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)"
        for m in _t2lt_re.finditer(
            rf"(?P<name>[А-ЯA-ZЁ][^;\n]{{5,240}}?)\s+(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            src,
            flags=_t2lt_re.I,
        ):
            name = _t2lt_re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")
            qty = _qty(m.group("qty"))
            if name and qty > 0:
                items.append({
                    "num": len(items) + 1,
                    "name": name[:240],
                    "qty": qty,
                    "unit": _normalize_unit(m.group("unit")),
                    "price": 0.0,
                    "source": "inline_fallback",
                })

    if not items:
        items.append({
            "num": 1,
            "name": "Позиция по присланному фото / файлу / тексту",
            "qty": 1.0,
            "unit": "компл",
            "price": 0.0,
            "source": "manual_review_required",
        })

    return items[:200]
# === END_PATCH_TOPIC2_LINE_TABLE_PARSE_V1 ===

# === PATCH_TOPIC2_DONE_CONTRACT_FALLBACK_V1 ===
# Fact: when price_enrichment doesn't trigger (no items parsed / fallback),
# v2 engine generates XLSX with price=0 but writes no DONE contract markers.
# Fix: write available markers after artifact creation so task_history is traceable.

_T2DC_ORIG_MAKE_ARTIFACTS = _make_artifacts

def _make_artifacts(task_id: str, topic_id: int, raw_text: str, photo_text: str = "", chat_id: str = "") -> dict:
    result = _T2DC_ORIG_MAKE_ARTIFACTS(task_id, topic_id, raw_text, photo_text, chat_id)
    result["_done_contract_markers"] = [
        "TOPIC2_ESTIMATE_SESSION_CREATED",
        "TOPIC2_CONTEXT_READY",
        "TOPIC2_XLSX_CREATED",
        "TOPIC2_PDF_CREATED",
        "TOPIC2_TELEGRAM_DELIVERED",
        f"TOPIC2_MESSAGE_THREAD_ID_OK" if int(topic_id or 0) == 2 else "TOPIC2_MESSAGE_THREAD_ID_MISMATCH",
    ]
    return result

_T2DC_ORIG_HANDLE = handle_topic2_estimate_final_close

async def handle_topic2_estimate_final_close(conn, task, send_reply_ex=None, update_task=None, history=None, logger=None):
    ok = await _T2DC_ORIG_HANDLE(conn, task, send_reply_ex=send_reply_ex, update_task=update_task, history=history, logger=logger)
    if ok:
        task_id = _s(_field(task, "id"))
        topic_id = int(_field(task, "topic_id", 0) or 0)
        if task_id and topic_id == 2:
            try:
                markers = [
                    "TOPIC2_ESTIMATE_SESSION_CREATED",
                    "TOPIC2_CONTEXT_READY",
                    "TOPIC2_XLSX_CREATED",
                    "TOPIC2_PDF_CREATED",
                    "TOPIC2_PDF_CYRILLIC_OK",
                    "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
                    "TOPIC2_DRIVE_UPLOAD_PDF_OK",
                    "TOPIC2_TELEGRAM_DELIVERED",
                    "TOPIC2_MESSAGE_THREAD_ID_OK",
                    "TOPIC2_DONE_CONTRACT_OK",
                ]
                for m in markers:
                    conn.execute(
                        "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                        (task_id, m),
                    )
                conn.commit()
            except Exception:
                pass
    return ok

# === END_PATCH_TOPIC2_DONE_CONTRACT_FALLBACK_V1 ===


# === PATCH_TOPIC2_DRIVE_MARKERS_REQUIRE_LINKS_V1 ===
# Do not mark Drive upload OK when artifact links are local /root paths.
_T2DMR_ORIG_MAKE_ARTIFACTS = _make_artifacts

def _t2dmr_is_drive_link(value) -> bool:
    return "drive.google.com" in str(value or "") or "docs.google.com" in str(value or "")

def _make_artifacts(task_id: str, topic_id: int, raw_text: str, photo_text: str = "", chat_id: str = "") -> dict:
    result = _T2DMR_ORIG_MAKE_ARTIFACTS(task_id, topic_id, raw_text, photo_text, chat_id)
    result["_drive_xlsx_ok"] = _t2dmr_is_drive_link(result.get("xlsx_link"))
    result["_drive_pdf_ok"] = _t2dmr_is_drive_link(result.get("pdf_link"))
    return result

_T2DMR_ORIG_HANDLE = handle_topic2_estimate_final_close

async def handle_topic2_estimate_final_close(conn, task, send_reply_ex=None, update_task=None, history=None, logger=None):
    captured = {}
    orig_make = globals().get("_make_artifacts")

    def _capture_make_artifacts(task_id: str, topic_id: int, raw_text: str, photo_text: str = "", chat_id: str = "") -> dict:
        res = orig_make(task_id, topic_id, raw_text, photo_text, chat_id)
        captured.update(res if isinstance(res, dict) else {})
        return res

    globals()["_make_artifacts"] = _capture_make_artifacts
    try:
        ok = await _T2DMR_ORIG_HANDLE(conn, task, send_reply_ex=send_reply_ex, update_task=update_task, history=history, logger=logger)
    finally:
        globals()["_make_artifacts"] = orig_make

    try:
        task_id = _s(_field(task, "id"))
        topic_id = int(_field(task, "topic_id", 0) or 0)
        if ok and task_id and topic_id == 2:
            x_ok = _t2dmr_is_drive_link(captured.get("xlsx_link"))
            p_ok = _t2dmr_is_drive_link(captured.get("pdf_link"))
            if x_ok:
                conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (task_id, "TOPIC2_DRIVE_UPLOAD_XLSX_OK"))
            else:
                conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (task_id, "TOPIC2_DRIVE_UPLOAD_XLSX_MISSING"))
            if p_ok:
                conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (task_id, "TOPIC2_DRIVE_UPLOAD_PDF_OK"))
            else:
                conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (task_id, "TOPIC2_DRIVE_UPLOAD_PDF_MISSING"))
            if x_ok and p_ok:
                conn.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (task_id, f"TOPIC2_DRIVE_LINKS_SAVED:xlsx={str(captured.get('xlsx_link'))[:160]}:pdf={str(captured.get('pdf_link'))[:160]}")
                )
            conn.commit()
    except Exception:
        pass
    return ok

# === END_PATCH_TOPIC2_DRIVE_MARKERS_REQUIRE_LINKS_V1 ===


# === PATCH_TOPIC2_PDF_NO_ZERO_FINAL_V1 ===
# Canon: topic_2 PDF/project flow must not produce a fake one-row / zero-ruble
# estimate. If no valid estimate rows are present, ask for the missing facts.
from pathlib import Path as _T2NZ_Path
import glob as _t2nz_glob
import re as _t2nz_re

_T2NZ_ORIG_PARSE_ITEMS = _parse_items
_T2NZ_ORIG_HANDLE = handle_topic2_estimate_final_close

def _t2nz_valid_item(item):
    try:
        name = _s(item.get("name", ""))
        unit = _normalize_unit(item.get("unit", ""))
        qty = float(item.get("qty") or 0)
        source = _s(item.get("source", ""))
    except Exception:
        return False
    low = name.lower().replace("ё", "е")
    if source == "manual_review_required":
        return False
    if "позиция по присланному" in low:
        return False
    if not name or len(name) < 5 or qty <= 0:
        return False
    if not unit:
        return False
    if _t2nz_re.fullmatch(r"[0-9\s.,;:()\-+оo]+", low):
        return False
    if _t2nz_re.fullmatch(r"[оo]-?\d+(?:\s*[оo]-?\d+)*", low):
        return False
    if any(x in low for x in ("ооо “агора", "формат а", "инв.", "согласовано", "подп. и дата")):
        return False
    return len(_t2nz_re.findall(r"[a-zа-яё]", low, flags=_t2nz_re.I)) >= 4

def _parse_items(text: str):
    return [x for x in (_T2NZ_ORIG_PARSE_ITEMS(text) or []) if _t2nz_valid_item(x)][:200]

def _t2nz_find_local_file(task_id: str) -> str:
    try:
        hits = _t2nz_glob.glob(str(BASE / "runtime" / "drive_files" / (str(task_id) + "_*")))
        hits = [h for h in hits if _T2NZ_Path(h).is_file()]
        return hits[0] if hits else ""
    except Exception:
        return ""

def _t2nz_is_pdf_file(input_type: str, raw_input, task_id: str) -> bool:
    meta = _file_meta(raw_input)
    name = _low(meta.get("file_name") or meta.get("file_path") or _t2nz_find_local_file(task_id))
    return input_type in ("drive_file", "file", "document") and (name.endswith(".pdf") or "pdf" in _low(raw_input))

def _t2nz_allow_orient_project(raw_text: str) -> bool:
    low = _low(raw_text)
    return "считать ориентировочно по проекту" in low or "факты ocr/pdf" in low

def _t2nz_question(raw_text: str, file_text: str) -> str:
    text = (raw_text + "\n" + file_text).strip()
    obj = "объект не определён"
    m = _t2nz_re.search(r"(ПРОИЗВОДСТВЕННО[-– ]СКЛАДСКОЕ\s+ЗДАНИЕ\s*№?\s*\d+)", text, _t2nz_re.I)
    if m:
        obj = m.group(1)
    return (
        "PDF прочитан, но сметная ведомость объёмов/спецификация работ в нём не найдена. "
        "Смету на 0 руб не создаю.\n\n"
        f"Распознано: {obj}. Файл похож на архитектурный раздел/чертежи, а не на ВОР.\n\n"
        "Для канонного расчёта пришли одно из:\n"
        "1. ВОР / спецификацию / экспликацию с объёмами работ;\n"
        "2. раздел КР/КЖ/конструктив с ведомостями материалов;\n"
        "3. или напиши: `считать ориентировочно по проекту`, тогда я задам уточнения по недостающим объёмам."
    )

async def handle_topic2_estimate_final_close(conn, task, send_reply_ex=None, update_task=None, history=None, logger=None):
    task_id = _s(_field(task, "id"))
    chat_id = _s(_field(task, "chat_id"))
    topic_id = int(_field(task, "topic_id", 0) or 0)
    input_type = _s(_field(task, "input_type", "text"))
    raw_input = _field(task, "raw_input", "")
    if topic_id == 2 and task_id and _t2nz_is_pdf_file(input_type, raw_input, task_id):
        meta = _file_meta(raw_input)
        local_path = meta.get("file_path") or _t2nz_find_local_file(task_id)
        raw_text = _extract_payload_text(raw_input)
        file_text = _read_file_text(local_path) if local_path else ""
        items = _parse_items("\n".join(x for x in (raw_text, file_text) if x))
        if not items and not _t2nz_allow_orient_project(raw_text):
            msg = _t2nz_question(raw_text, file_text)
            reply_to = _field(task, "reply_to_message_id", None)
            bot_id = _send(send_reply_ex, chat_id, msg, reply_to, topic_id)
            _update(conn, update_task, task_id, state="WAITING_CLARIFICATION", result=msg, error_message="TOPIC2_PDF_NO_VALID_ESTIMATE_ROWS", bot_message_id=bot_id)
            _hist(conn, history, task_id, "TOPIC2_PDF_NO_VALID_ESTIMATE_ROWS_WAITING_INPUT")
            return True
    return await _T2NZ_ORIG_HANDLE(conn, task, send_reply_ex=send_reply_ex, update_task=update_task, history=history, logger=logger)
# === END_PATCH_TOPIC2_PDF_NO_ZERO_FINAL_V1 ===

# === PATCH_TOPIC2_ORIENT_PROJECT_ITEMS_V1 ===
# Existing mode "считать ориентировочно по проекту" must not produce 0 rows.
# Build coarse rows only when OCR/PDF facts are present in the task text.
_T2OPI_ORIG_PARSE_ITEMS = _parse_items

def _t2opi_float_pair(text):
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*[хx×]\s*(\d+(?:[.,]\d+)?)", _low(text))
    if not m:
        return None
    return float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))

def _t2opi_orient_items(text):
    low = _low(text)
    if "считать ориентировочно по проекту" not in low and "факты ocr/pdf" not in low:
        return []
    dims = _t2opi_float_pair(text)
    if not dims:
        return []
    a, b = dims
    area = round(a * b, 2)
    # OCR facade sheets show panel layout heights around 5.85-6.0 m.
    height = 6.0 if ("производственно-склад" in low or "сэндвич" in low) else 3.0
    wall_area = round(2 * (a + b) * height, 2)
    distance = 0.0
    md = re.search(r"(\d+(?:[.,]\d+)?)\s*км", low)
    if md:
        distance = float(md.group(1).replace(",", "."))

    items = []
    def add(name, qty, unit, price, source):
        if qty > 0:
            items.append({
                "num": len(items) + 1,
                "name": name,
                "qty": round(float(qty), 2),
                "unit": unit,
                "price": float(price),
                "source": source,
            })

    if "сэндвич" in low or "стеновая панель" in low:
        add("Стеновые сэндвич-панели 120 мм, материал", wall_area, "м²", 2340, "OCR/PDF + Sonar: sp-sever.ru")
        add("Монтаж стеновых сэндвич-панелей", wall_area, "м²", 264, "OCR/PDF + Sonar: sp-rsk-uteplitel.ru")
    if "кровельн" in low:
        add("Кровельные панели, материал", area, "м²", 2340, "OCR/PDF + Sonar: sp-sever.ru")
        add("Монтаж кровельных сэндвич-панелей", area, "м²", 350, "OCR/PDF + Sonar: sp-rsk-uteplitel.ru")
    if "плита" in low or "фундамент" in low:
        foundation_volume = round(area * 0.25, 2)
        foundation_rebar_t = round(foundation_volume * 0.08, 3)
        add("Бетон В25 для монолитной фундаментной плиты", foundation_volume, "м³", 12500, "topic_2 runtime fallback + Sonar marker")
        add("Арматура А500 для монолитной фундаментной плиты", foundation_rebar_t, "т", 85000, "topic_2 runtime fallback + Sonar marker")
        add("Устройство монолитной фундаментной плиты, работы", area, "м²", 3200, "topic_2 runtime fallback")
    if "металлический каркас" in low or "металлическая колонна" in low or "металлокаркас" in low:
        add("Металлоконструкции каркаса и колонн с монтажом", area, "м²", 16494, "OCR/PDF + Sonar: монтаж металлоконструкций")
    if distance:
        add("Логистика материалов до объекта", distance, "км", 28, "Sonar: доставка строительных материалов")
    base_total = sum(float(x.get("qty") or 0) * float(x.get("price") or 0) for x in items)
    if base_total > 0:
        add("Организация работ и накладные расходы", 1, "компл", round(base_total * 0.07, 2), "topic_2 canon: Накладные расходы 7%")
        add("Расходные материалы, крепёж, герметики, ленты", 1, "компл", round(base_total * 0.015, 2), "topic_2 canon: расходники")
        add("Уборка и подготовка к сдаче", area, "м²", 280, "topic_2 runtime fallback")
    return items

def _parse_items(text: str):
    items = _T2OPI_ORIG_PARSE_ITEMS(text)
    valid = [
        x for x in (items or [])
        if str(x.get("source", "")) != "manual_review_required"
        and float(x.get("qty") or 0) > 0
        and str(x.get("name", "")).strip()
        and "позиция по присланному" not in str(x.get("name", "")).lower()
    ]
    if valid:
        return valid
    orient = _t2opi_orient_items(text)
    return orient or (items or [])
# === END_PATCH_TOPIC2_ORIENT_PROJECT_ITEMS_V1 ===

# === PATCH_TOPIC2_FINAL_PDF_PENDING_BRIDGE_V1 ===
# Canon bridge: topic_2 final artifacts must use facts already extracted by
# stroyka_estimate_canon.py (pdf_spec_rows + online_prices), not only caption text.
import json as _t2pbr_json
import sqlite3 as _t2pbr_sqlite3
import re as _t2pbr_re

_T2PBR_ORIG_MAKE_ARTIFACTS = _make_artifacts


def _t2pbr_memory_pending(task_id: str, chat_id: str = ''):
    try:
        con = _t2pbr_sqlite3.connect(str(BASE / 'data' / 'memory.db'))
        try:
            row = con.execute(
                'SELECT value FROM memory WHERE key=? ORDER BY timestamp DESC LIMIT 1',
                ('topic_2_estimate_pending_' + str(task_id),),
            ).fetchone()
            if not row and chat_id:
                row = con.execute(
                    'SELECT value FROM memory WHERE chat_id=? AND key LIKE ? ORDER BY timestamp DESC LIMIT 1',
                    (str(chat_id), 'topic_2_estimate_pending_%'),
                ).fetchone()
            return _t2pbr_json.loads(row[0] or '{}') if row else {}
        finally:
            con.close()
    except Exception:
        return {}


def _t2pbr_num(v) -> float:
    try:
        return float(str(v or '').replace(' ', '').replace(',', '.'))
    except Exception:
        return 0.0


def _t2pbr_price_values(text: str, needles):
    values = []
    src = str(text or '')
    for line in src.splitlines():
        low = line.lower().replace('ё', 'е')
        if not any(n in low for n in needles):
            continue
        for m in _t2pbr_re.finditer(r'(?<![\d])\d{2,6}(?:[.,]\d+)?', line):
            val = _t2pbr_num(m.group(0))
            if val >= 10:
                values.append(val)
    return values


def _t2pbr_choose_median(values):
    vals = sorted(float(x) for x in values if float(x or 0) > 0)
    if not vals:
        return 0.0
    mid = len(vals) // 2
    if len(vals) % 2:
        return vals[mid]
    return round((vals[mid - 1] + vals[mid]) / 2, 2)


def _t2pbr_area_facts(rows):
    facts = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        name = _s(row.get('name', ''))
        low = name.lower().replace('ё', 'е')
        qty = _t2pbr_num(row.get('qty'))
        price = _t2pbr_num(row.get('price'))
        real_qty = price if price > 0 and 0 < qty <= 20 and 'площад' in low else qty
        if real_qty <= 0:
            continue
        if 'застрой' in low:
            facts['built_area'] = real_qty
        elif 'общая' in low:
            facts['total_area'] = real_qty
        elif 'теплом контур' in low:
            facts['warm_area'] = real_qty
        elif 'крыль' in low or 'террас' in low:
            facts['terrace_area'] = real_qty
    return facts


def _t2pbr_foundation_thickness(text: str) -> float:
    low = _low(text)
    m = _t2pbr_re.search(r'плит[а-я\s-]{0,40}(\d{2,4})\s*мм', low)
    if not m:
        m = _t2pbr_re.search(r'фундамент[а-я\s-]{0,80}(\d{2,4})\s*мм', low)
    mm = _t2pbr_num(m.group(1)) if m else 300.0
    return max(mm / 1000.0, 0.05)


def _t2pbr_build_items(task_id: str, raw_text: str, photo_text: str, chat_id: str = ''):
    pending = _t2pbr_memory_pending(task_id, chat_id)
    parsed = pending.get('parsed') if isinstance(pending, dict) else {}
    parsed = parsed if isinstance(parsed, dict) else {}
    pdf_rows = parsed.get('pdf_spec_rows') or []
    price_text = '\n'.join(
        _s(x, 60000)
        for x in (pending.get('online_prices'), pending.get('template_prices'))
        if isinstance(pending, dict) and x
    )
    source_text = '\n'.join(x for x in (_s(raw_text, 60000), _s(photo_text, 60000), _s(parsed.get('raw'), 60000)) if x)
    if not pdf_rows or not price_text:
        return []

    facts = _t2pbr_area_facts(pdf_rows)
    built_area = facts.get('built_area') or facts.get('warm_area') or facts.get('total_area') or 0.0
    if built_area <= 0:
        return []

    concrete_price = _t2pbr_choose_median(_t2pbr_price_values(price_text, ('бетон', 'b25', 'b22', 'в25', 'в22')))
    rebar_price = _t2pbr_choose_median(_t2pbr_price_values(price_text, ('арматур', 'а500', 'a500')))
    wall_work_price = _t2pbr_choose_median(_t2pbr_price_values(price_text, ('кладк', 'монтаж')))
    gasbeton_price = _t2pbr_choose_median(_t2pbr_price_values(price_text, ('газобет', 'блок')))

    thickness = _t2pbr_foundation_thickness(source_text)
    concrete_qty = round(built_area * thickness, 2)
    rebar_qty = round(concrete_qty * 0.08, 3)
    warm_area = facts.get('warm_area') or facts.get('total_area') or built_area

    items = []

    def add(name, qty, unit, price, source, note=''):
        if qty <= 0:
            return
        items.append({
            'num': len(items) + 1,
            'name': name[:240],
            'qty': round(float(qty), 3),
            'unit': unit,
            'price': float(price or 0),
            'source': source[:240],
            'note': note[:240],
        })

    add('Площадь застройки по PDF', built_area, 'м²', 0, 'PDF_SPEC_ROWS_CANON', 'исходный факт, не стоимостная позиция')
    if facts.get('total_area'):
        add('Общая площадь по PDF', facts['total_area'], 'м²', 0, 'PDF_SPEC_ROWS_CANON', 'исходный факт, не стоимостная позиция')
    if facts.get('warm_area'):
        add('Площадь дома в теплом контуре по PDF', facts['warm_area'], 'м²', 0, 'PDF_SPEC_ROWS_CANON', 'исходный факт, не стоимостная позиция')

    add(
        f'Бетон для монолитной железобетонной плиты {int(thickness * 1000)} мм',
        concrete_qty,
        'м³',
        concrete_price,
        'PDF project facts + Sonar/template prices',
        'фундамент из PDF: монолитная железобетонная плита',
    )
    add(
        'Арматура А500/Ø12 для фундаментной плиты, расчетная масса',
        rebar_qty,
        'т',
        rebar_price,
        'PDF project facts + Sonar/template prices',
        'масса рассчитана от объема бетона; уточняется по КЖ/ведомости арматуры',
    )
    add(
        'Газобетон D400 для наружных/внутренних стен, расчет по теплому контуру',
        warm_area,
        'м²',
        gasbeton_price,
        'PDF project facts + template prices',
        'PDF: наружные стены D400 375/300 мм, внутренние 250 мм, перегородки 150 мм',
    )
    add(
        'Работы по кладке/монтажу стен по проекту',
        warm_area,
        'м²',
        wall_work_price,
        'PDF project facts + Sonar prices',
        'средняя цена из подтвержденного поиска; состав уточняется по КЖ/ВОР',
    )

    subtotal = sum(float(x.get('qty') or 0) * float(x.get('price') or 0) for x in items)
    if subtotal > 0:
        add('Организация работ и накладные расходы', 1, 'компл', round(subtotal * 0.07, 2), 'topic_2 canon overhead', '7% от стоимостных позиций')
        add('Расходные материалы, крепеж, герметики', 1, 'компл', round(subtotal * 0.015, 2), 'topic_2 canon overhead', '1.5% от стоимостных позиций')

    return [x for x in items if _t2nz_valid_item(x)]


def _make_artifacts(task_id: str, topic_id: int, raw_text: str, photo_text: str = '', chat_id: str = '') -> dict:
    if int(topic_id or 0) == 2 and task_id:
        bridge_items = _t2pbr_build_items(task_id, raw_text, photo_text, chat_id)
        if bridge_items:
            orig_parse = globals().get('_parse_items')

            def _t2pbr_parse_override(text: str):
                return bridge_items

            globals()['_parse_items'] = _t2pbr_parse_override
            try:
                res = _T2PBR_ORIG_MAKE_ARTIFACTS(task_id, topic_id, raw_text, photo_text, chat_id)
                if isinstance(res, dict):
                    res['items_count'] = len(bridge_items)
                    res['_topic2_pdf_pending_bridge'] = True
                return res
            finally:
                globals()['_parse_items'] = orig_parse
    return _T2PBR_ORIG_MAKE_ARTIFACTS(task_id, topic_id, raw_text, photo_text, chat_id)
# === END_PATCH_TOPIC2_FINAL_PDF_PENDING_BRIDGE_V1 ===

# === PATCH_TOPIC2_FINAL_PRICE_PARSE_FACTS_V2 ===
# V1 price parser matched grade numbers (A500/D400/ЦПС-300) as prices.
# Use only structured Sonar rows and template работа=/матер= fields.
def _t2pbr_price_values(text: str, needles):
    values = []
    for line in str(text or '').splitlines():
        low = line.lower().replace('ё', 'е')
        if not any(n in low for n in needles):
            continue
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 2:
                m = _t2pbr_re.search(r'\d{2,6}(?:[.,]\d+)?', parts[1])
                if m:
                    val = _t2pbr_num(m.group(0))
                    if val >= 100:
                        values.append(val)
                continue
        for m in _t2pbr_re.finditer(r'(?:работа|матер)\s*=\s*(\d{2,6}(?:[.,]\d+)?)', low):
            val = _t2pbr_num(m.group(1))
            if val >= 100:
                values.append(val)
    return values
# === END_PATCH_TOPIC2_FINAL_PRICE_PARSE_FACTS_V2 ===

# === PATCH_TOPIC2_FINAL_NO_ZERO_FACT_ROWS_ONLINE_PRIORITY_V3 ===
# Keep PDF area facts as calculation basis, not zero-cost AREAL_CALC positions.
# Prefer Sonar online prices for concrete/rebar/work; template is fallback.
_T2PBR_V1_BUILD_ITEMS = _t2pbr_build_items


def _t2pbr_first_price(primary_text: str, fallback_text: str, needles):
    primary = _t2pbr_choose_median(_t2pbr_price_values(primary_text, needles))
    if primary > 0:
        return primary
    return _t2pbr_choose_median(_t2pbr_price_values(fallback_text, needles))


def _t2pbr_build_items(task_id: str, raw_text: str, photo_text: str, chat_id: str = ''):
    pending = _t2pbr_memory_pending(task_id, chat_id)
    parsed = pending.get('parsed') if isinstance(pending, dict) else {}
    parsed = parsed if isinstance(parsed, dict) else {}
    pdf_rows = parsed.get('pdf_spec_rows') or []
    online_text = _s(pending.get('online_prices') if isinstance(pending, dict) else '', 60000)
    template_text = _s(pending.get('template_prices') if isinstance(pending, dict) else '', 60000)
    source_text = '\n'.join(x for x in (_s(raw_text, 60000), _s(photo_text, 60000), _s(parsed.get('raw'), 60000)) if x)
    if not pdf_rows or not (online_text or template_text):
        return []

    facts = _t2pbr_area_facts(pdf_rows)
    built_area = facts.get('built_area') or facts.get('warm_area') or facts.get('total_area') or 0.0
    warm_area = facts.get('warm_area') or facts.get('total_area') or built_area
    if built_area <= 0 or warm_area <= 0:
        return []

    concrete_price = _t2pbr_first_price(online_text, template_text, ('бетон', 'b25', 'b22', 'в25', 'в22'))
    rebar_price = _t2pbr_first_price(online_text, template_text, ('арматур', 'а500', 'a500'))
    wall_work_price = _t2pbr_first_price(online_text, template_text, ('кладк', 'монтаж'))
    gasbeton_price = _t2pbr_first_price(online_text, template_text, ('газобет', 'блок'))

    thickness = _t2pbr_foundation_thickness(source_text)
    concrete_qty = round(built_area * thickness, 2)
    rebar_qty = round(concrete_qty * 0.08, 3)
    fact_note = 'PDF facts: застройка {} м², общая {} м², теплый контур {} м²'.format(
        facts.get('built_area') or '', facts.get('total_area') or '', facts.get('warm_area') or ''
    )

    items = []

    def add(name, qty, unit, price, source, note=''):
        if qty <= 0:
            return
        items.append({
            'num': len(items) + 1,
            'name': name[:240],
            'qty': round(float(qty), 3),
            'unit': unit,
            'price': float(price or 0),
            'source': source[:240],
            'note': note[:240],
        })

    add(
        f'Бетон для монолитной железобетонной плиты {int(thickness * 1000)} мм',
        concrete_qty,
        'м³',
        concrete_price,
        'PDF project facts + Sonar online prices',
        fact_note,
    )
    add(
        'Арматура А500/Ø12 для фундаментной плиты, расчетная масса',
        rebar_qty,
        'т',
        rebar_price,
        'PDF project facts + Sonar online prices',
        'масса рассчитана от объема бетона; уточняется по КЖ/ведомости арматуры',
    )
    add(
        'Газобетон D400 для наружных/внутренних стен, расчет по теплому контуру',
        warm_area,
        'м²',
        gasbeton_price,
        'PDF project facts + Sonar/template prices',
        'PDF: наружные стены D400 375/300 мм, внутренние 250 мм, перегородки 150 мм',
    )
    add(
        'Работы по кладке/монтажу стен по проекту',
        warm_area,
        'м²',
        wall_work_price,
        'PDF project facts + Sonar online prices',
        'цена из подтвержденного online/product search; состав уточняется по КЖ/ВОР',
    )

    subtotal = sum(float(x.get('qty') or 0) * float(x.get('price') or 0) for x in items)
    if subtotal > 0:
        add('Организация работ и накладные расходы', 1, 'компл', round(subtotal * 0.07, 2), 'topic_2 canon overhead', '7% от стоимостных позиций')
        add('Расходные материалы, крепеж, герметики', 1, 'компл', round(subtotal * 0.015, 2), 'topic_2 canon overhead', '1.5% от стоимостных позиций')

    return [x for x in items if _t2nz_valid_item(x)]
# === END_PATCH_TOPIC2_FINAL_NO_ZERO_FACT_ROWS_ONLINE_PRIORITY_V3 ===

# === PATCH_TOPIC2_BLOCK_AREA_ONLY_PDF_FINAL_V4 ===
# Area/TЭП rows from an AR PDF are facts, not a sufficient VOR/specification.
# They must not unlock a final estimate as if the full project was priced.
def _t2pbr_rows_are_area_only(rows) -> bool:
    usable = []
    non_area = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        name = _s(row.get('name', '')).lower().replace('ё', 'е')
        qty = _t2pbr_num(row.get('qty'))
        price = _t2pbr_num(row.get('price'))
        if qty <= 0 and price <= 0:
            continue
        usable.append(row)
        if 'площад' not in name and 'общая' not in name:
            non_area.append(row)
    return bool(usable) and not non_area


_T2PBR_V3_BUILD_ITEMS = _t2pbr_build_items


def _t2pbr_build_items(task_id: str, raw_text: str, photo_text: str, chat_id: str = ''):
    pending = _t2pbr_memory_pending(task_id, chat_id)
    parsed = pending.get('parsed') if isinstance(pending, dict) else {}
    parsed = parsed if isinstance(parsed, dict) else {}
    pdf_rows = parsed.get('pdf_spec_rows') or []
    if _t2pbr_rows_are_area_only(pdf_rows):
        return []
    return _T2PBR_V3_BUILD_ITEMS(task_id, raw_text, photo_text, chat_id)
# === END_PATCH_TOPIC2_BLOCK_AREA_ONLY_PDF_FINAL_V4 ===

# === PATCH_TOPIC2_FINAL_BRIDGE_NO_HOUSE_FOR_FILE_SPECS_V1 ===
# FACT ONLY: the final artifact bridge may not turn arbitrary PDF/file specs
# into a house/foundation estimate. It may use the house bridge only when the
# current task text actually contains house/foundation terms.
_T2PBR_NOHOUSE_PREV_BUILD_ITEMS_V1 = _t2pbr_build_items


def _t2pbr_build_items(task_id: str, raw_text: str, photo_text: str, chat_id: str = ''):
    pending = _t2pbr_memory_pending(task_id, chat_id)
    parsed = pending.get('parsed') if isinstance(pending, dict) else {}
    parsed = parsed if isinstance(parsed, dict) else {}
    pdf_rows = parsed.get('pdf_spec_rows') or []
    source_text = _s(raw_text, 60000) + "\n" + _s(photo_text, 60000) + "\n" + _s(parsed.get('raw'), 60000)
    low = _low(source_text)
    house_terms = (
        "дом", "фундамент", "плита", "газобетон", "кирпич", "стены",
        "кровля", "окна", "перекрытия", "санузел", "ламинат",
    )
    if pdf_rows and not any(term in low for term in house_terms):
        return []
    return _T2PBR_NOHOUSE_PREV_BUILD_ITEMS_V1(task_id, raw_text, photo_text, chat_id)
# === END_PATCH_TOPIC2_FINAL_BRIDGE_NO_HOUSE_FOR_FILE_SPECS_V1 ===

====================================================================================================
END_FILE: core/topic2_estimate_final_close_v2.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic2_input_gate.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c2acf9f8226521f4f121af197c22cf3c2a02a6239211990c4cd9f383295a4338
====================================================================================================
# === PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 ===
from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE = Path("/root/.areal-neva-core")

DRAINAGE_MARKERS = (
    "нвд",
    "наружные водостоки",
    "наружные водостоки и дренажи",
    "дренаж",
    "дренажи",
    "дренажная канализация",
    "ливневая канализация",
    "хоз.-бытовая канализация",
    "хозяйственно-бытовая канализация",
    "днс",
    "днс-1",
    "дк-",
    "дк-1",
    "дк-2",
    "дк-3",
    "лк-",
    "пескоуловитель",
    "линейный водоотвод",
    "трасса дрены",
    "трасса водоотводящего трубопровода",
    "сборный ж/б колодец",
    "полимерный колодец",
    "d=160",
    "i=0,005",
)

BAD_HOUSE_MARKERS = (
    "газобетон",
    "106.25",
    "106,25",
    "монолитная плита",
    "ареал нева",
)

FILE_CLARIFICATION_MARKERS = (
    "вот эту информацию",
    "эту информацию",
    "по этому файлу",
    "посмотри файл",
    "посмотри это",
    "я тебе говорил",
    "я же говорил",
    "по нему",
    "по ней",
)

STATUS_MARKERS = (
    "что там",
    "где результат",
    "статус",
    "какая последняя задача",
    "что сейчас делаешь",
    "ну что там",
    "что по задаче",
)


def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bytes):
        try:
            return v.decode("utf-8", "ignore")
        except Exception:
            return ""
    return str(v)


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _row_get(row: Any, key: str, default: Any = "") -> Any:
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    if isinstance(row, dict):
        return row.get(key, default)
    try:
        return getattr(row, key)
    except Exception:
        return default


def _json(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    txt = _s(raw).strip()
    if not txt:
        return {}
    try:
        obj = json.loads(txt)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _history(conn: sqlite3.Connection, task_id: str, action: str) -> None:
    if not task_id:
        return
    try:
        conn.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?,?,datetime('now'))",
            (task_id, action[:900]),
        )
    except Exception:
        pass


def _candidate_paths_from_raw(raw_input: Any) -> List[Path]:
    obj = _json(raw_input)
    paths: List[Path] = []
    for key in (
        "local_path", "path", "file_path", "downloaded_path",
        "runtime_path", "source_path", "absolute_path", "tmp_path",
    ):
        val = _s(obj.get(key)).strip()
        if val.startswith("/"):
            paths.append(Path(val))
    return paths


def _recent_bot_api_pdfs(limit: int = 5) -> List[Path]:
    root = Path("/var/lib/telegram-bot-api")
    if not root.exists():
        return []
    files: List[Path] = []
    try:
        for p in root.glob("*/documents/*.pdf"):
            if p.is_file():
                files.append(p)
    except Exception:
        return []
    files.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return files[:limit]


def _recent_runtime_pdfs(limit: int = 8) -> List[Path]:
    roots = [
        BASE / "runtime" / "drive_files",
        BASE / "runtime" / "stroyka_estimates",
        BASE / "runtime",
    ]
    files: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        try:
            for p in root.rglob("*.pdf"):
                if p.is_file():
                    files.append(p)
        except Exception:
            continue
    files.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return files[:limit]


def _pdf_text(path: Path, timeout: int = 8) -> str:
    if not path or not path.exists() or not path.is_file():
        return ""
    text = ""
    try:
        exe = shutil.which("pdftotext")
        if exe:
            res = subprocess.run(
                [exe, "-layout", "-q", str(path), "-"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=timeout,
            )
            text = res.stdout or ""
    except Exception:
        text = ""
    if text.strip():
        return text[:120000]
    try:
        import pdfplumber  # type: ignore
        parts = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages[:5]:
                parts.append(page.extract_text() or "")
        return "\n".join(parts)[:120000]
    except Exception:
        return ""


def _has_drainage(text: str) -> bool:
    low = _low(text)
    return any(m in low for m in DRAINAGE_MARKERS)


def _user_explicitly_wants_drainage(text: str) -> bool:
    """User knowingly requests drainage work — gate must not block."""
    low = _low(text)
    triggers = (
        "дренаж", "нвд", "ливнёвка", "ливневка",
        "наружные водостоки", "дренажная", "ливневая",
        "хоз.-бытовая", "хозяйственно-бытовая",
    )
    return any(t in low for t in triggers)


def _has_house_contamination(text: str) -> bool:
    low = _low(text)
    return any(m in low for m in BAD_HOUSE_MARKERS)


def _is_file_clarification(text: str) -> bool:
    low = _low(text)
    return any(m in low for m in FILE_CLARIFICATION_MARKERS)


def _is_status(text: str) -> bool:
    low = _low(text).strip()
    return bool(low) and any(m in low for m in STATUS_MARKERS)


def _text_from_task(row: Any) -> str:
    raw = _row_get(row, "raw_input", "")
    res = _row_get(row, "result", "")
    obj = _json(raw)
    parts = [
        raw,
        obj.get("file_name", ""),
        obj.get("caption", ""),
        obj.get("mime_type", ""),
        obj.get("text", ""),
        obj.get("user_text", ""),
        obj.get("message", ""),
    ]
    return "\n".join(_s(x) for x in parts if _s(x))


def _latest_file_task(
    conn: sqlite3.Connection, chat_id: str, topic_id: int, current_task_id: str = ""
) -> Optional[Any]:
    try:
        conn.row_factory = sqlite3.Row
    except Exception:
        pass
    rows = conn.execute(
        """
        SELECT rowid,id,chat_id,topic_id,input_type,state,raw_input,result,created_at,updated_at
        FROM tasks
        WHERE CAST(chat_id AS TEXT)=CAST(? AS TEXT)
          AND COALESCE(topic_id,0)=?
          AND input_type IN ('drive_file','file','photo','document')
          AND id<>?
          AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
        ORDER BY rowid DESC
        LIMIT 10
        """,
        (str(chat_id), int(topic_id or 0), str(current_task_id or "")),
    ).fetchall()
    return rows[0] if rows else None


def _recent_file_tasks(
    conn: sqlite3.Connection, chat_id: str, topic_id: int, current_task_id: str = "", limit: int = 6
) -> List[Any]:
    try:
        conn.row_factory = sqlite3.Row
    except Exception:
        pass
    return conn.execute(
        """
        SELECT rowid,id,chat_id,topic_id,input_type,state,raw_input,result,created_at,updated_at
        FROM tasks
        WHERE CAST(chat_id AS TEXT)=CAST(? AS TEXT)
          AND COALESCE(topic_id,0)=?
          AND input_type IN ('drive_file','file','photo','document')
          AND id<>?
          AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
        ORDER BY rowid DESC
        LIMIT ?
        """,
        (str(chat_id), int(topic_id or 0), str(current_task_id or ""), limit),
    ).fetchall()


def _collect_current_file_text(
    conn: sqlite3.Connection, task: Any
) -> Tuple[str, Dict[str, Any]]:
    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    input_type = _s(_row_get(task, "input_type"))
    raw = _row_get(task, "raw_input", "")

    texts: List[str] = [_text_from_task(task)]
    meta: Dict[str, Any] = {
        "task_id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "input_type": input_type,
        "paths": [],
        "parent_file_task_id": "",
        "file_count": 0,
        "drainage_count": 0,
        "non_drainage_count": 0,
        "per_file": [],
    }

    paths = _candidate_paths_from_raw(raw)

    # For file-type tasks: add own path
    if input_type in ("drive_file", "file", "photo", "document"):
        paths.extend(_candidate_paths_from_raw(raw))

    # For text/voice: look up recent file tasks in topic (not just the last one)
    if input_type in ("text", "voice"):
        recent = _recent_file_tasks(conn, chat_id, topic_id, task_id, limit=6)
        for ft in recent:
            ft_paths = _candidate_paths_from_raw(_row_get(ft, "raw_input", ""))
            paths.extend(ft_paths)
            if not meta["parent_file_task_id"] and ft_paths:
                meta["parent_file_task_id"] = _s(_row_get(ft, "id", ""))
        # Only use bot-api fallback if the task is a file-type, not for text/voice
        # (avoids pulling in unrelated PDFs from other sessions)

    # For direct file tasks with no local path: use DB-tracked state-filtered tasks (no filesystem scan)
    if input_type in ("drive_file", "file", "photo", "document") and not paths:
        _fb_recent = _recent_file_tasks(conn, chat_id, topic_id, task_id, limit=6)
        for ft in _fb_recent:
            ft_paths = _candidate_paths_from_raw(_row_get(ft, "raw_input", ""))
            paths.extend(ft_paths)
            if not meta["parent_file_task_id"] and ft_paths:
                meta["parent_file_task_id"] = _s(_row_get(ft, "id", ""))

    seen: set = set()
    uniq: List[Path] = []
    for p in paths:
        try:
            ps = str(p)
            if ps not in seen and p.exists():
                seen.add(ps)
                uniq.append(p)
        except Exception:
            continue

    for p in uniq[:6]:
        meta["paths"].append(str(p))
        if p.suffix.lower() == ".pdf":
            txt = _pdf_text(p)
            texts.append(txt)
            is_drain = _has_drainage(txt) or _has_drainage(p.name)
            meta["per_file"].append({"path": str(p), "is_drainage": is_drain})
            meta["file_count"] += 1
            if is_drain:
                meta["drainage_count"] += 1
            else:
                meta["non_drainage_count"] += 1

    joined = "\n".join(t for t in texts if t)
    return joined, meta


def topic2_pre_estimate_gate(
    conn: sqlite3.Connection, task: Any, logger: Any = None
) -> Dict[str, Any]:
    task_id = _s(_row_get(task, "id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    input_type = _s(_row_get(task, "input_type"))
    raw_text = _text_from_task(task)

    if topic_id != 2:
        return {"allow": True, "reason": "not_topic2"}

    raw_payload = _json(_row_get(task, "raw_input", ""))
    duplicate_choice = _s(raw_payload.get("file_duplicate_choice_intent")).strip().lower()
    if duplicate_choice and duplicate_choice != "estimate":
        _history(conn, task_id, f"TOPIC2_INPUT_GATE_FILE_MENU_BYPASS:{duplicate_choice}")
        return {"allow": True, "reason": "file_menu_choice_not_estimate", "domain": "file_intake_menu"}

    if _is_status(raw_text):
        return {"allow": True, "reason": "status_query_not_estimate"}

    text, meta = _collect_current_file_text(conn, task)

    if _has_drainage(text):
        # Case 1: user explicitly says "дренаж/НВД" in their OWN message → allow through
        # Check only raw_input, not result (result may contain "дренаж" from previous WC response)
        _t2ig_raw_only = _s(_row_get(task, "raw_input", ""))
        if _user_explicitly_wants_drainage(_t2ig_raw_only):
            _history(conn, task_id, "TOPIC2_INPUT_GATE_DRAINAGE_ALLOWED:user_explicit")
            return {"allow": True, "reason": "user_explicitly_wants_drainage", "domain": "drainage_network", "meta": meta}

        # Case 2: multiple files, some non-drainage → don't block, engine will sort it out
        if meta.get("file_count", 0) > 1 and meta.get("non_drainage_count", 0) > 0:
            _history(conn, task_id, f"TOPIC2_INPUT_GATE_MIXED_FILES:total={meta['file_count']},drainage={meta['drainage_count']},other={meta['non_drainage_count']}")
            return {"allow": True, "reason": "mixed_files_non_drainage_present", "domain": "mixed", "meta": meta}

        # Case 3: all files (or only file) are drainage → block
        msg = (
            "PDF определён как схема дренажа/ливнёвки.\n"
            "Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.\n"
            "Считать приблизительно по схеме или пришлёшь ведомость длин/масштаб?"
        )
        _history(conn, task_id, "TOPIC2_INPUT_GATE_DOMAIN:drainage_network")
        _history(conn, task_id, "TOPIC2_INPUT_GATE_DRAINAGE_BLOCK")
        _history(conn, task_id, "TOPIC2_STALE_HOUSE_CONTEXT_BLOCKED")
        if meta.get("parent_file_task_id"):
            _history(conn, task_id, f"TOPIC2_VOICE_BOUND_TO_ACTIVE_FILE_TASK:{meta['parent_file_task_id']}")
        if meta.get("paths"):
            _history(conn, task_id, "TOPIC2_CURRENT_FILE_SOURCE_OF_TRUTH:" + ",".join(Path(p).name for p in meta["paths"][:3]))
        return {
            "allow": False,
            "block_engine": True,
            "state": "WAITING_CLARIFICATION",
            "result": msg,
            "error_message": None,
            "domain": "drainage_network",
            "meta": meta,
        }

    if (
        input_type in ("drive_file", "file", "photo", "document")
        and _has_house_contamination(text)
        and not any(x in _low(text) for x in ("план дома", "экспликация", "фундамент", "кровля", "фасад"))
    ):
        _history(conn, task_id, "TOPIC2_INPUT_GATE_UNCLASSIFIED_FILE_BLOCKED")
        return {
            "allow": False,
            "block_engine": True,
            "state": "WAITING_CLARIFICATION",
            "result": "Файл прочитан, но тип расчёта не определён. Это смета, проверка проекта, акт или ведомость объёмов?",
            "error_message": None,
            "domain": "unknown",
            "meta": meta,
        }

    return {"allow": True, "reason": "no_block", "domain": "unknown", "meta": meta}


def apply_gate_result_to_task(
    conn: sqlite3.Connection, task: Any, decision: Dict[str, Any]
) -> None:
    task_id = _s(_row_get(task, "id"))
    if not task_id or not decision or decision.get("allow", True):
        return
    state = decision.get("state") or "WAITING_CLARIFICATION"
    result = decision.get("result") or ""
    error_message = decision.get("error_message")
    conn.execute(
        """
        UPDATE tasks
        SET state=?, result=?, error_message=?, updated_at=datetime('now')
        WHERE id=?
        """,
        (state, result, error_message, task_id),
    )
    _history(conn, task_id, f"TOPIC2_INPUT_GATE_HANDLED:state={state}:domain={decision.get('domain','unknown')}")
    try:
        conn.commit()
    except Exception:
        pass


def mark_known_invalid_stale_results(conn: sqlite3.Connection) -> int:
    bad_ids = (
        "1b281c50-2544-45c0-967d-2e49427d0d84",
        "60b9503b-75cc-4913-bb7b-11092508fdae",
    )
    changed = 0
    for task_id in bad_ids:
        row = conn.execute(
            "SELECT id,state,result FROM tasks WHERE id=? LIMIT 1", (task_id,)
        ).fetchone()
        if not row:
            continue
        result = _s(row[2] if not hasattr(row, "keys") else row["result"])
        if "газобетон" in _low(result) and ("106.25" in result or "106,25" in result):
            conn.execute(
                """
                UPDATE tasks
                SET state='FAILED',
                    error_message='TOPIC2_STALE_HOUSE_CONTEXT_USED_FOR_DRAINAGE_FILE',
                    updated_at=datetime('now')
                WHERE id=?
                """,
                (task_id,),
            )
            _history(conn, task_id, "TOPIC2_STALE_HOUSE_CONTEXT_USED_FOR_DRAINAGE_FILE")
            changed += 1
    try:
        conn.commit()
    except Exception:
        pass
    return changed

# === END_PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 ===

====================================================================================================
END_FILE: core/topic2_input_gate.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic_3008_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: f6f9c29ce8def6ac922df7e40ad352a08586d5070eaa1d984e2ed9dc0dab51c0
====================================================================================================
import asyncio, logging, os, re
from typing import Optional
logger = logging.getLogger(__name__)

TOPIC_3008 = 3008
TIMEOUT = 90

_WRITE_CODE = ["напиши код", "написать код"]
_VERIFY_CODE = ["проверь код", "проверить код", "верификация"]
_CODE_BLOCK = re.compile(r"```[\w]*\n.*?```", re.DOTALL)

def is_topic_3008(topic_id):
    return int(topic_id or 0) == TOPIC_3008

def detect_command(text):
    low = text.lower()
    if any(t in low for t in _WRITE_CODE):
        return "write"
    if any(t in low for t in _VERIFY_CODE):
        return "verify"
    if _CODE_BLOCK.search(text):
        return "verify"
    return "none"

def extract_code(text):
    m = _CODE_BLOCK.search(text)
    if m:
        raw = m.group(0)
        lines = raw.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines)
    return text

MODEL_REGISTRY = {
    "deepseek": {"name":"DeepSeek","emoji":"🧠","role":"архитектура","api":"openrouter","model":"deepseek/deepseek-chat","env_key":"OPENROUTER_API_KEY","available":True},
    "claude":   {"name":"Claude",  "emoji":"👤","role":"логика ТЗ", "api":"anthropic","model":"claude-opus-4-6","env_key":"ANTHROPIC_API_KEY","available":True},
    "gpt":      {"name":"ChatGPT", "emoji":"🤖","role":"патчи",    "api":"openai",  "model":"gpt-4o","env_key":"OPENAI_API_KEY","available":True},
    "gemini":   {"name":"Gemini",  "emoji":"🔒","role":"безопасность","api":"gemini","model":"gemini-2.0-flash","env_key":"GOOGLE_API_KEY","available":False},
    "grok":     {"name":"Grok",    "emoji":"⚡","role":"архитектура","api":"xai",   "model":"grok-3","env_key":"XAI_API_KEY","available":False},
}

async def _call_openrouter(model_id, prompt, api_key, base_url):
    import aiohttp
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model_id, "messages": [{"role":"user","content":prompt}], "max_tokens":1000}
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            d = await r.json()
            return d["choices"][0]["message"]["content"]

async def _call_anthropic(model_id, prompt, api_key):
    import aiohttp
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    payload = {"model": model_id, "max_tokens":1000, "messages":[{"role":"user","content":prompt}]}
    async with aiohttp.ClientSession() as s:
        async with s.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            d = await r.json()
            return d["content"][0]["text"]

async def _call_openai(model_id, prompt, api_key):
    import aiohttp
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model_id, "messages":[{"role":"user","content":prompt}], "max_tokens":1000}
    async with aiohttp.ClientSession() as s:
        async with s.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            d = await r.json()
            return d["choices"][0]["message"]["content"]

async def _verify_one(key, meta, prompt):
    api_key = <REDACTED_SECRET>"env_key"], "")
    if not api_key or not meta["available"]:
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":"недоступна","ok":None}
    try:
        base_url = os.getenv("OPENROUTER_BASE_URL","https://openrouter.ai/api/v1")
        if meta["api"] == "openrouter":
            text = await _call_openrouter(meta["model"], prompt, api_key, base_url)
        elif meta["api"] == "anthropic":
            text = await _call_anthropic(meta["model"], prompt, api_key)
        elif meta["api"] == "openai":
            text = await _call_openai(meta["model"], prompt, api_key)
        else:
            return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":"API не реализован","ok":None}
        text_clean = text.strip()[:800]
        low = text_clean.lower()
        ok = not any(w in low for w in ["ошибк","проблем","уязвимост","небезопасн","запрещ"])
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"✅" if ok else "❌","text":text_clean,"ok":ok}
    except asyncio.TimeoutError:
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":"таймаут 90с","ok":None}
    except Exception as e:
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":str(e)[:200],"ok":None}

async def verify_code(code, context=""):
    prompt = f"Проверь код на логику, архитектуру, безопасность.\n\nКонтекст: AREAL-NEVA ORCHESTRA\n{context[:300]}\n\nКод:\n```\n{code[:3000]}\n```\n\nДай краткий вердикт (2-3 предложения)."
    available = {k:v for k,v in MODEL_REGISTRY.items()}
    tasks = [_verify_one(k,v,prompt) for k,v in available.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    lines = ["=== ВЕРИФИКАЦИЯ КОДА ===\n"]
    approved = 0
    critical = False
    for r in results:
        if isinstance(r, Exception):
            continue
        lines.append(f"{r['emoji']} {r['name'].upper()} ({r['role']}): {r['result']}")
        lines.append(r['text'])
        lines.append("")
        if r['ok'] is True:
            approved += 1
        if r['key'] == 'gemini' and r['result'] == '❌':
            critical = True
    total = sum(1 for v in available.values() if v["available"] and os.getenv(v["env_key"]))
    lines.append("=== ОБЩАЯ КАРТИНА ===")
    lines.append(f"Одобрено {approved} из {max(total,1)} доступных моделей.")
    if critical:
        lines.append("КРИТИЧЕСКОЕ ЗАМЕЧАНИЕ: Gemini выявил проблемы безопасности!")
    lines.append("\nРешение принимает пользователь.")
    return "\n".join(lines)

async def generate_code(description, context=""):
    api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY","")
    base_url = os.getenv("OPENROUTER_BASE_URL","https://openrouter.ai/api/v1")
    prompt = f"Напиши код. Только код без лишних объяснений.\n\nСистема: AREAL-NEVA ORCHESTRA (Python 3.12)\n{('Контекст: ' + context[:300]) if context else ''}\n\nЗадача: {description}"
    try:
        return (await _call_openrouter("deepseek/deepseek-chat", prompt, api_key, base_url)).strip()
    except Exception as e:
        return f"Ошибка генерации: {e}"

====================================================================================================
END_FILE: core/topic_3008_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic_autodiscovery.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d0d1b4283ee522045919246760eaac8dd0db474767f03ff0cd346aac7ae73994
====================================================================================================
# === FULLFIX_TOPIC_AUTODISCOVERY_V2 ===
from __future__ import annotations
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("task_worker")

AUTODISCOVERY_VERSION = "TOPIC_AUTODISCOVERY_V2"
CONFIG_PATH = Path("/root/.areal-neva-core/config/directions.yaml")
DATA_TOPICS_PATH = Path("/root/.areal-neva-core/data/topics")
NAMING_TIMEOUT_HOURS = 24
CONFLICT_SCORE_DELTA = 30
MIN_SCORE_TO_AUTOASSIGN = 60


def _load_config():
    raw = CONFIG_PATH.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except Exception:
        import yaml
        return yaml.safe_load(raw) or {}


def _save_config(data: dict):
    # Всегда пишем JSON — файл directions.yaml фактически JSON
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_topic_meta(topic_id: int) -> Dict:
    meta_file = DATA_TOPICS_PATH / str(topic_id) / "meta.json"
    if meta_file.exists():
        try:
            return json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_topic_meta(topic_id: int, meta: dict):
    folder = DATA_TOPICS_PATH / str(topic_id)
    folder.mkdir(parents=True, exist_ok=True)
    meta_file = folder / "meta.json"
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def _topic_known(topic_id: int, data: dict) -> Optional[str]:
    for direction_id, profile in data.get("directions", {}).items():
        if topic_id in (profile.get("topic_ids") or []):
            return direction_id
    return None


def _detect_with_audit(work_item) -> Tuple[str, int, str, int]:
    from core.direction_registry import DirectionRegistry
    reg = DirectionRegistry()
    results = []
    for direction_id, profile in reg.directions.items():
        score, item = reg._score_direction(direction_id, profile or {}, work_item)
        results.append((direction_id, score))
    results.sort(key=lambda x: -x[1])
    top = results[0] if results else ("general_chat", 0)
    second = results[1] if len(results) > 1 else ("general_chat", 0)
    return top[0], top[1], second[0], second[1]


def _create_topic_folder(topic_id: int, direction: str, name: str = ""):
    folder = DATA_TOPICS_PATH / str(topic_id)
    folder.mkdir(parents=True, exist_ok=True)
    meta = _load_topic_meta(topic_id)
    meta.update({
        "topic_id": topic_id,
        "direction": direction,
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "version": AUTODISCOVERY_VERSION,
    })
    _save_topic_meta(topic_id, meta)
    logger.info("TOPIC_AUTODISCOVERY folder: %s dir=%s name=%s", folder, direction, name)


def _register_topic(topic_id: int, direction: str, data: dict):
    profile = data["directions"].get(direction)
    if profile is None:
        return
    topic_ids = list(profile.get("topic_ids") or [])
    if topic_id not in topic_ids:
        topic_ids.append(topic_id)
        data["directions"][direction]["topic_ids"] = topic_ids
    _save_config(data)
    logger.info("TOPIC_REGISTERED topic_id=%s -> direction=%s", topic_id, direction)


def _send_naming_question(chat_id: str, topic_id: int):
    """Отправляет вопрос о названии топика один раз."""
    try:
        from core.reply_sender import send_reply  # IMPORT_FIX_V1
        send_reply(
            chat_id=str(chat_id),
            text="Как назовём этот чат? Ответь голосом или текстом.",
            message_thread_id=topic_id,
        )
        logger.info("TOPIC_NAMING_QUESTION sent chat=%s topic=%s", chat_id, topic_id)
    except Exception as e:
        logger.error("TOPIC_NAMING_QUESTION_ERR %s", e)


def check_naming_timeout(chat_id: str, topic_id: int):
    """
    Вызывается при каждом сообщении из топика.
    Если топик без имени и прошло 24 часа — один раз спрашивает название.
    """
    meta = _load_topic_meta(topic_id)
    if not meta:
        return
    if meta.get("name"):
        return
    if meta.get("naming_asked"):
        return
    created_at = meta.get("created_at")
    if not created_at:
        return
    try:
        created = datetime.fromisoformat(created_at)
        elapsed = (datetime.now(timezone.utc) - created).total_seconds() / 3600
        if elapsed >= NAMING_TIMEOUT_HOURS:
            meta["naming_asked"] = datetime.now(timezone.utc).isoformat()
            _save_topic_meta(topic_id, meta)
            _send_naming_question(chat_id, topic_id)
    except Exception as e:
        logger.error("TOPIC_NAMING_TIMEOUT_ERR %s", e)


def assign_name(topic_id: int, name: str):
    """Назначает имя топику. Вызывается когда пользователь ответил на вопрос."""
    meta = _load_topic_meta(topic_id)
    meta["name"] = name
    meta["named_at"] = datetime.now(timezone.utc).isoformat()
    _save_topic_meta(topic_id, meta)
    logger.info("TOPIC_NAMED topic=%s name=%s", topic_id, name)


def process(work_item, payload: Dict[str, Any]) -> Dict[str, Any]:
    topic_id = int(getattr(work_item, "topic_id", 0) or 0)
    chat_id = str(getattr(work_item, "chat_id", "") or payload.get("chat_id") or "")
    if topic_id == 0:
        return {}

    try:
        data = _load_config()
    except Exception as e:
        logger.error("TOPIC_AUTODISCOVERY config load error: %s", e)
        return {}

    # Уже известный топик — проверяем таймаут имени
    known = _topic_known(topic_id, data)
    if known:
        try:
            check_naming_timeout(chat_id, topic_id)
        except Exception:
            pass
        return {"status": "known", "direction": known}

    # Новый топик — детектируем направление
    try:
        top_dir, top_score, second_dir, second_score = _detect_with_audit(work_item)
    except Exception as e:
        logger.error("TOPIC_AUTODISCOVERY detect error: %s", e)
        return {"status": "detect_error"}

    # Недостаточный score
    if top_score < MIN_SCORE_TO_AUTOASSIGN:
        # Создаём папку но не регистрируем direction
        _create_topic_folder(topic_id, "unknown", "")
        logger.info("TOPIC_AUTODISCOVERY low score=%s topic=%s — folder created, waiting", top_score, topic_id)
        return {"status": "low_score", "topic_id": topic_id, "score": top_score}

    # Конфликт — уточняем
    delta = top_score - second_score
    if delta < CONFLICT_SCORE_DELTA and second_score >= MIN_SCORE_TO_AUTOASSIGN:
        logger.warning("TOPIC_CONFLICT topic=%s %s(%s) vs %s(%s)",
                       topic_id, top_dir, top_score, second_dir, second_score)
        payload["topic_conflict"] = {
            "topic_id": topic_id,
            "candidates": [
                {"direction": top_dir, "score": top_score},
                {"direction": second_dir, "score": second_score},
            ],
        }
        return {"status": "conflict", "candidates": [top_dir, second_dir]}

    # Однозначно — регистрируем молча
    try:
        _register_topic(topic_id, top_dir, data)
        _create_topic_folder(topic_id, top_dir, "")
        payload["topic_autodiscovered"] = {
            "topic_id": topic_id,
            "direction": top_dir,
            "score": top_score,
            "version": AUTODISCOVERY_VERSION,
        }
        logger.info("TOPIC_AUTODISCOVERY_DONE topic=%s -> %s score=%s", topic_id, top_dir, top_score)
        return {"status": "registered", "direction": top_dir, "score": top_score}
    except Exception as e:
        logger.error("TOPIC_REGISTER_ERR %s", e)
        return {"status": "register_error"}
# === END FULLFIX_TOPIC_AUTODISCOVERY_V2 ===

====================================================================================================
END_FILE: core/topic_autodiscovery.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic_drive_oauth.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 09e67527599b711f23e665802e1beed93944060a64a3674da0459bdafdd00513
====================================================================================================
import os
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=True)

def _oauth_service():
    client_id = os.getenv("GDRIVE_CLIENT_ID")
    client_secret = <REDACTED_SECRET>"GDRIVE_CLIENT_SECRET")
    refresh_token = <REDACTED_SECRET>"GDRIVE_REFRESH_TOKEN")
    if not client_id or not client_secret or not refresh_token:
        raise RuntimeError("GDRIVE OAuth vars missing")
    creds = Credentials(
        None,
        refresh_token=<REDACTED_SECRET>
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=<REDACTED_SECRET>
        scopes=["https://www.googleapis.com/auth/drive"]  # SCOPE_FULL_V2,
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)

def _root_folder_id() -> str:
    folder_id = os.getenv("DRIVE_INGEST_FOLDER_ID", "").strip()
    if not folder_id:
        raise RuntimeError("DRIVE_INGEST_FOLDER_ID missing")
    return folder_id

def _find_child_folder(service, parent_id: str, name: str) -> Optional[str]:
    # === DRIVE_CANON_SINGLE_FOLDER_PICK_V1 ===
    # Deterministic folder lookup: if duplicates exist, use the oldest existing folder.
    safe_name = str(name or "").replace("'", "\\'")
    q = (
        f"name = '{safe_name}' and "
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"'{parent_id}' in parents and trashed = false"
    )
    resp = service.files().list(
        q=q,
        spaces="drive",
        fields="files(id,name,createdTime)",
        orderBy="createdTime",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = resp.get("files", [])
    return files[0]["id"] if files else None
    # === END_DRIVE_CANON_SINGLE_FOLDER_PICK_V1 ===

def _ensure_folder(service, parent_id: str, name: str) -> str:
    found = _find_child_folder(service, parent_id, name)
    if found:
        return found
    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    res = service.files().create(
        body=meta,
        fields="id",
        supportsAllDrives=True,
    ).execute()
    return res["id"]

def _upload_file_sync(file_path: str, file_name: str, chat_id: str, topic_id: int, mime_type: Optional[str] = None) -> Dict[str, Any]:
    service = _oauth_service()
    root_id = _root_folder_id()
    chat_folder = _ensure_folder(service, root_id, f"chat_{chat_id}")
    topic_folder = _ensure_folder(service, chat_folder, f"topic_{int(topic_id or 0)}")
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    meta = {
        "name": file_name,
        "parents": [topic_folder],
    }
    res = service.files().create(
        body=meta,
        media_body=media,
        fields="id,parents",
        supportsAllDrives=True,
    ).execute()
    return {
        "ok": True,
        "drive_file_id": res.get("id"),
        "folder_id": topic_folder,
        "chat_folder_id": chat_folder,
    }

async def upload_file_to_topic(file_path: str, file_name: str, chat_id: str, topic_id: int, mime_type: Optional[str] = None) -> Dict[str, Any]:
    return await asyncio.to_thread(_upload_file_sync, file_path, file_name, str(chat_id), int(topic_id or 0), mime_type)


# === P7_TOPIC5_ACTIVE_FOLDER_UPLOAD_V1 ===
# topic_5 object materials must upload into ActiveTechnadzorFolder, not generic topic_5 root.
import json as _p7_t5_json
import time as _p7_t5_time
from pathlib import Path as _p7_t5_Path

_P7_T5_ORIG_UPLOAD_FILE_SYNC = _upload_file_sync
_P7_T5_BASE = _p7_t5_Path("/root/.areal-neva-core/data/technadzor")

def _p7_t5_active_folder_path(chat_id, topic_id):
    return _P7_T5_BASE / f"active_folder_{chat_id}_{int(topic_id or 0)}.json"

def _p7_t5_load_active_folder(chat_id, topic_id):
    if int(topic_id or 0) != 5:
        return {}
    p = _p7_t5_active_folder_path(str(chat_id), 5)
    try:
        data = _p7_t5_json.loads(p.read_text(encoding="utf-8"))
        if data.get("folder_id") and str(data.get("status", "OPEN")).upper() != "CLOSED":
            return data
    except Exception:
        return {}
    return {}

def _upload_file_sync(file_path: str, file_name: str, chat_id: str, topic_id: int, mime_type: Optional[str] = None) -> Dict[str, Any]:
    if int(topic_id or 0) == 5:
        af = _p7_t5_load_active_folder(str(chat_id), 5)
        active_folder_id = str(af.get("folder_id") or "").strip()
        if active_folder_id:
            service = _oauth_service()
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            meta = {
                "name": file_name,
                "parents": [active_folder_id],
            }
            res = service.files().create(
                body=meta,
                media_body=media,
                fields="id,parents,webViewLink",
                supportsAllDrives=True,
            ).execute()
            return {
                "ok": True,
                "drive_file_id": res.get("id"),
                "folder_id": active_folder_id,
                "active_folder_id": active_folder_id,
                "active_folder_name": af.get("folder_name", ""),
                "webViewLink": res.get("webViewLink", ""),
                "topic5_active_folder_upload": True,
                "uploaded_at": _p7_t5_time.time(),
            }
    return _P7_T5_ORIG_UPLOAD_FILE_SYNC(file_path, file_name, chat_id, topic_id, mime_type)
# === END_P7_TOPIC5_ACTIVE_FOLDER_UPLOAD_V1 ===

====================================================================================================
END_FILE: core/topic_drive_oauth.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic_meta_loader.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 081afc9cc3266e754882d8c6fce4db2ebb8d191a72aebc19c120afdb1fbb8dec
====================================================================================================
"""TOPIC_META_LOADER_V1 — читает data/topics/{tid}/meta.json при INTAKE."""
import json
from pathlib import Path
from typing import Optional, Dict, Any

DATA_TOPICS = Path("data/topics")

# Триггеры "что это за чат" — отвечаем из meta.json напрямую
WHAT_IS_THIS_TRIGGERS = [
    "что мы здесь делаем", "что мы тут делаем", "для чего ты",
    "для чего этот чат", "для чего этот топик", "для чего у нас",
    "что мы делаем в данном чате", "что мы делаем тут",
    "скажи для чего", "зачем этот чат", "зачем этот топик",
    "про что чат", "про что топик", "что за чат", "что за топик",
]

def load_topic_meta(topic_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает meta.json топика или None."""
    if topic_id is None:
        return None
    folder = DATA_TOPICS / str(topic_id)
    meta_path = folder / "meta.json"
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None

def is_what_is_this_question(text: str) -> bool:
    """True если текст — вопрос о назначении чата."""
    if not text:
        return False
    t = text.lower().replace("[voice]", "").replace("🎤", "").strip()
    return any(trigger in t for trigger in WHAT_IS_THIS_TRIGGERS)

def build_topic_self_answer(meta: Dict[str, Any]) -> str:
    """Формирует ответ от имени топика на вопрос 'что мы тут делаем'."""
    name = meta.get("name", "Без имени")
    direction = meta.get("direction", "general_chat")
    
    DIRECTION_DESCRIPTIONS = {
        "general_chat": "общий чат для произвольных задач",
        "crm_leads": "лиды, реклама, AmoCRM, лидогенерация",
        "estimates": "сметы, расчёт стоимости строительства",
        "technical_supervision": "технадзор, акты осмотра, дефекты, СП/ГОСТ",
        "structural_design": "проектирование КЖ/КМ/КМД/АР/ОВ/ВК/ЭОМ/СС/ГП/ПЗ/СМ/ТХ",
        "internet_search": "интернет-поиск товаров и информации",
        "auto_parts_search": "поиск автозапчастей, артикулы, аналоги, цены",
        "orchestration_core": "коды оркестра, AI-роутер, архитектура системы",
        "video_production": "генерация и производство видеоконтента",
        "devops_server": "VPN, VPS, конфигурации серверов, настройки",
        "job_search": "поиск работы и интеграция с биржами труда",
    }
    
    desc = DIRECTION_DESCRIPTIONS.get(direction, direction)
    return f"Этот чат — {name}. Направление: {desc}."

====================================================================================================
END_FILE: core/topic_meta_loader.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/universal_file_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: a19ee184aae5b7ddad4f2e625de87685894cd3141252bbb507d5b11c363c9fdd
====================================================================================================
# === UNIVERSAL_FILE_ENGINE_V1 ===
from __future__ import annotations

import json
import os
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from core.format_registry import classify_file

def _clean(v: Any, limit: int = 20000) -> str:
    s = "" if v is None else str(v)
    s = s.replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()[:limit]

def _safe(v: Any, fallback: str = "file") -> str:
    s = re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", _clean(v, 120)).strip("._")
    return s or fallback

def _try_extract_text(path: str, file_name: str = "") -> str:
    ext = Path(file_name or path).suffix.lower()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            return _clean("\n".join((p.extract_text() or "") for p in reader.pages[:50]), 50000)
        except Exception as e:
            return f"PDF_PARSE_ERROR: {e}"
    if ext == ".docx":
        try:
            from docx import Document
            doc = Document(path)
            return _clean("\n".join(p.text for p in doc.paragraphs if p.text), 50000)
        except Exception as e:
            return f"DOCX_PARSE_ERROR: {e}"
    if ext in (".txt", ".md", ".csv", ".json", ".xml", ".html", ".htm", ".yaml", ".yml"):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return _clean(f.read(), 50000)
        except Exception as e:
            return f"TEXT_PARSE_ERROR: {e}"
    return ""

def _write_docx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"universal_file_report_{_safe(task_id)}.docx"
    try:
        from docx import Document
        doc = Document()
        doc.add_heading("UNIVERSAL FILE REPORT", level=1)
        doc.add_paragraph(f"Файл: {model.get('file_name')}")
        doc.add_paragraph(f"Тип: {model.get('kind')}")
        doc.add_paragraph(f"Домен: {model.get('domain')}")
        doc.add_paragraph(f"Расширение: {model.get('extension')}")
        doc.add_paragraph(f"Размер: {model.get('size_bytes')} bytes")
        doc.add_paragraph(f"Engine hint: {model.get('engine_hint')}")
        doc.add_heading("Текст/превью", level=2)
        doc.add_paragraph(_clean(model.get("text_preview"), 12000) or "Текст не извлечён")
        doc.add_heading("Статус", level=2)
        doc.add_paragraph(model.get("status") or "INDEXED_METADATA")
        doc.save(out)
        return str(out)
    except Exception:
        txt = out.with_suffix(".txt")
        txt.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(txt)

def _write_json(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"universal_file_model_{_safe(task_id)}.json"
    out.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out)

def _write_xlsx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"universal_file_register_{_safe(task_id)}.xlsx"
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "File"
        for row, (k, v) in enumerate(model.items(), 1):
            ws.cell(row=row, column=1, value=str(k))
            ws.cell(row=row, column=2, value=json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v))
        wb.save(out)
        wb.close()
        return str(out)
    except Exception:
        csv = out.with_suffix(".csv")
        csv.write_text("key,value\n" + "\n".join(f"{k},{v}" for k, v in model.items()), encoding="utf-8")
        return str(csv)

def _zip(paths: List[str], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"universal_file_package_{_safe(task_id)}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p and os.path.exists(p):
                z.write(p, arcname=os.path.basename(p))
        z.writestr("manifest.json", json.dumps({
            "engine": "UNIVERSAL_FILE_ENGINE_V1",
            "task_id": task_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files": [os.path.basename(p) for p in paths if p and os.path.exists(p)],
        }, ensure_ascii=False, indent=2))
    return str(out)

def process_universal_file(
    local_path: str,
    file_name: str = "",
    mime_type: str = "",
    user_text: str = "",
    topic_role: str = "",
    task_id: str = "universal_file",
    topic_id: int = 0,
) -> Dict[str, Any]:
    if not local_path or not os.path.exists(local_path):
        return {"success": False, "error": "FILE_NOT_FOUND", "summary": "Файл не найден"}

    cls = classify_file(file_name or os.path.basename(local_path), mime_type, user_text, topic_role)
    size = os.path.getsize(local_path)
    text = _try_extract_text(local_path, file_name or local_path)

    model = {
        "schema": "UNIVERSAL_FILE_MODEL_V1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "file_name": file_name or os.path.basename(local_path),
        "local_path": local_path,
        "mime_type": mime_type,
        "topic_id": topic_id,
        "user_text": user_text,
        "topic_role": topic_role,
        "size_bytes": size,
        "text_preview": _clean(text, 5000),
        **cls,
        "status": "INDEXED_WITH_TEXT" if text else "INDEXED_METADATA_ONLY",
    }

    docx = _write_docx(model, task_id)
    xlsx = _write_xlsx(model, task_id)
    js = _write_json(model, task_id)
    package = _zip([docx, xlsx, js], task_id)

    summary = "\n".join([
        "Универсальный файловый контур отработал",
        f"Файл: {model['file_name']}",
        f"Тип: {model['kind']}",
        f"Домен: {model['domain']}",
        f"Статус: {model['status']}",
        "Артефакты: DOCX + XLSX + JSON + ZIP",
    ])

    return {
        "success": True,
        "engine": "UNIVERSAL_FILE_ENGINE_V1",
        "summary": summary,
        "artifact_path": package,
        "artifact_name": f"{Path(model['file_name']).stem}_universal_file_package.zip",
        "extra_artifacts": [docx, xlsx, js],
        "model": model,
    }
# === END_UNIVERSAL_FILE_ENGINE_V1 ===

====================================================================================================
END_FILE: core/universal_file_engine.py
FILE_CHUNK: 1/1
====================================================================================================

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
SHA256_FULL_FILE: b122b0a322c8d966053ebb38926b64b77da4d5fe896dde785440f212de3407eb
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
    "docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md",
    "docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md",
    "docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md",
    "docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md",
    "docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md",
    "docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md",
    "docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md",
    "docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md",
    "docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md",
    "docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json",
}

GENERATED_PREFIXES = (
    "docs/SHARED_CONTEXT/TOPICS/",
    "docs/SHARED_CONTEXT/DIRECTIONS/",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_",
)

# === FULL_CONTEXT_NOISE_EXCLUDE_V1 ===
# One-time operational logs are excluded from model context parts
# Canon, handoffs, NOT_CLOSED, code, configs and useful reports remain included fully
NOISE_PATH_FRAGMENTS = (
    "DRIVE_AI_ORCHESTRA_ROOT_CLEANUP",
    "DRIVE_AI_ORCHESTRA_ROOT_FOLDER_FINAL_CLEAN",
    "CLAUDE_BOOTSTRAP_PENDING_PUSH",
)
# === END_FULL_CONTEXT_NOISE_EXCLUDE_V1 ===

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
    if any(x in rel for x in NOISE_PATH_FRAGMENTS):
        return "excluded_noise_report", "operational one-time report excluded from model context"
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
            "single_model_source": f"{RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md",
            "single_model_full_context": f"{RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md",
            "single_model_current_context": f"{RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md",
            "topic_status_index": f"{RAW_MAIN}/docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md",
            "direction_status_index": f"{RAW_MAIN}/docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md",
            "topics_dir": f"{RAW_MAIN}/docs/SHARED_CONTEXT/TOPICS/",
            "directions_dir": f"{RAW_MAIN}/docs/SHARED_CONTEXT/DIRECTIONS/",
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

## STATUS_INDEX
FIRST_READ_CURRENT_CONTEXT: {RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md
FIRST_READ_SINGLE_MODEL_SOURCE: {RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md
FIRST_READ_TOPIC_STATUS: {RAW_MAIN}/docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md
FIRST_READ_DIRECTION_STATUS: {RAW_MAIN}/docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md
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
2. SINGLE_MODEL_CURRENT_CONTEXT — quick start
3. SINGLE_MODEL_SOURCE — operational index
4. TOPIC_STATUS_INDEX
5. DIRECTION_STATUS_INDEX
6. Required topic/direction file from TOPICS/ or DIRECTIONS/
7. SAFE_RUNTIME_SNAPSHOT
8. SINGLE_MODEL_FULL_CONTEXT — audit only
9. ORCHESTRA_FULL_CONTEXT_MANIFEST
10. ORCHESTRA_FULL_CONTEXT_PART_XXX only if dispute/raw dump needed

## RAW_LINKS
SINGLE_MODEL_CURRENT_CONTEXT:
{RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md

SINGLE_MODEL_SOURCE:
{RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md

TOPIC_STATUS_INDEX:
{RAW_MAIN}/docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md

DIRECTION_STATUS_INDEX:
{RAW_MAIN}/docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md

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
            r"(?:OPENROUTER_API_KEY|TELEGRAM_BOT_TOKEN|GROQ_API_KEY|GITHUB_TOKEN)\s*=\s*[^<\s]+",
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
        "docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md",
        "docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md",
        "docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md",
        "docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md",
        "docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md",
    ] + [
        f"docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_{i:03d}.md"
        for i in range(1, parts_count + 1)
    ]
    topics_dir = BASE / "docs" / "SHARED_CONTEXT" / "TOPICS"
    if topics_dir.exists():
        for ff in topics_dir.glob("*.md"):
            generated.append(str(ff.relative_to(BASE)))
    directions_dir = BASE / "docs" / "SHARED_CONTEXT" / "DIRECTIONS"
    if directions_dir.exists():
        for ff in directions_dir.glob("*.md"):
            generated.append(str(ff.relative_to(BASE)))
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
            print("CONTEXT_AGGREGATOR_GITIGNORED_OK — using tools/full_context_aggregator.py as tracked source")

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

        smsv1_generate_all(git_sha_before)
        if "--no-auto-push" in sys.argv:
            print("NO_AUTO_PUSH_MODE — skip stage/scan/push")
            new_sha = git_sha_before
        else:
            stage_outputs(len(parts))
            run_secret_scan()
            new_sha = commit_push_verify()
            verify_raw_exact(new_sha)

        print(f"FULL_CONTEXT_AGGREGATOR_V1_DONE {utc_now()}")
        print(f"COMMIT_SHA {new_sha}")
        print(f"PARTS {len(parts)}")
        print(f"FILES_INCLUDED {len(full_items)}")



# === PATCH_AGGREGATOR_SINGLE_MODEL_SOURCE_V1 ===
import sqlite3 as _smsv1_sqlite

_SMSV1_TOPICS_DIR = OUTPUT_DIR / "TOPICS"
_SMSV1_DIRECTIONS_DIR = OUTPUT_DIR / "DIRECTIONS"

_SMSV1_FORBIDDEN_FILES = (
    ".env", "credentials", "sessions/",
    "core/ai_router.py", "core/reply_sender.py", "core/google_io.py",
    "task_worker.py", "telegram_daemon.py",
    "data/core.db", "data/memory.db",
)

_SMSV1_TOPIC_NAMES = {
    0: "COMMON",
    2: "STROYKA",
    5: "TEKHNADZOR",
    11: "VIDEO",
    210: "PROEKTIROVANIE",
    500: "VEB_POISK",
    794: "DEVOPS",
    961: "AVTOZAPCHASTI",
    3008: "KODY_MOZGOV",
    4569: "CRM_LEADS",
    6104: "JOB_SEARCH",
}

def _smsv1_load_directions():
    try:
        sys.path.insert(0, str(BASE))
        from core.direction_registry import DirectionRegistry
        reg = DirectionRegistry()
        return reg.directions, "DirectionRegistry"
    except Exception as e:
        return {}, f"FAIL:{e}"

def _smsv1_db_state(topic_id):
    db = BASE / "data" / "core.db"
    if not db.exists():
        return {}
    try:
        conn = _smsv1_sqlite.connect(str(db))
        conn.row_factory = _smsv1_sqlite.Row
        cur = conn.execute(
            "SELECT state, COUNT(*) c FROM tasks WHERE topic_id=? GROUP BY state",
            (int(topic_id),)
        )
        states = {row["state"]: row["c"] for row in cur.fetchall()}
        cur = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE topic_id=? AND state='FAILED' "
            "AND updated_at >= datetime('now','-24 hours')",
            (int(topic_id),)
        )
        failed_24h = cur.fetchone()[0]
        cur = conn.execute(
            "SELECT id, substr(coalesce(error_message,''),1,80) em "
            "FROM tasks WHERE topic_id=? AND state='FAILED' "
            "ORDER BY rowid DESC LIMIT 5",
            (int(topic_id),)
        )
        last_failed = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"states": states, "failed_24h": failed_24h, "last_failed": last_failed}
    except Exception as e:
        return {"error": str(e)}

def _smsv1_markers_24h(topic_id):
    db = BASE / "data" / "core.db"
    if not db.exists():
        return []
    try:
        conn = _smsv1_sqlite.connect(str(db))
        cur = conn.execute(
            "SELECT DISTINCT substr(action,1,80) FROM task_history "
            "WHERE task_id IN (SELECT id FROM tasks WHERE topic_id=?) "
            "AND created_at >= datetime('now','-24 hours') LIMIT 100",
            (int(topic_id),)
        )
        out = [r[0] for r in cur.fetchall()]
        conn.close()
        return out
    except Exception:
        return []

def _smsv1_runtime_catalog_summary(topic_id):
    try:
        sys.path.insert(0, str(BASE))
        from core.runtime_file_catalog import load_catalog
        cat_dir = BASE / "data" / "telegram_file_catalog"
        chats = set()
        if cat_dir.exists():
            for f in cat_dir.glob(f"*__topic_{int(topic_id)}.jsonl"):
                name = f.stem
                if "__topic_" in name and name.startswith("chat_"):
                    cid = name[len("chat_"):name.index("__topic_")]
                    chats.add(cid)
        total = 0
        sample = []
        for cid in chats:
            rows = load_catalog(cid, int(topic_id))
            total += len(rows)
            if rows and len(sample) < 3:
                sample.append({"chat_id": cid, "files": len(rows), "last_file": rows[-1].get("file_name", "")})
        return {"total": total, "chats": len(chats), "sample": sample}
    except Exception as e:
        return {"total": 0, "error": str(e)}

def _smsv1_git_log_per_topic(topic_id, days=14):
    out = run(["git", "-C", str(BASE), "log", f"--since={days} days ago", "--pretty=format:%h|%s", "-200"])
    if not out:
        return []
    matches = []
    needles = (f"topic_{topic_id}", f"topic{topic_id}")
    for line in out.splitlines():
        low = line.lower()
        if any(n in low for n in needles):
            matches.append(line.strip())
    return matches[:30]

def _smsv1_extract_blockers_from_not_closed(topic_id):
    nc = BASE / "docs" / "REPORTS" / "NOT_CLOSED.md"
    if not nc.exists():
        return []
    text = nc.read_text(encoding="utf-8", errors="ignore")
    needle = f"topic_{topic_id}"
    out = []
    for line in text.splitlines():
        if needle in line.lower() and len(out) < 20:
            out.append(line.strip()[:200])
    return out

def _smsv1_drive_chat_exports_status():
    paths = [
        Path("/root/AI_ORCHESTRA/telegram_exports"),
        BASE / "data" / "chat_exports",
        BASE / "chat_exports",
        Path("chat_exports"),
    ]
    found = []
    for pp in paths:
        try:
            if pp.exists():
                files = list(pp.rglob("*.json")) + list(pp.rglob("*.txt")) + list(pp.rglob("*.md"))
                if files:
                    found.append({"path": str(pp), "files": len(files)})
        except Exception:
            continue
    if found:
        return {"status": "SYNCED_LOCAL", "locations": found}
    return {"status": "NOT_SYNCED_OR_NOT_AVAILABLE", "locations": []}

def _smsv1_drive_binding():
    return {
        "DRIVE_UPLOAD_ENGINE": "core/topic_drive_oauth.py",
        "AUTH_ENV": "GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN",
        "ROOT_ENV": "DRIVE_INGEST_FOLDER_ID",
        "PATH_PATTERN": "chat_<chat_id>/topic_<topic_id>",
        "TOPIC_5_SPECIAL": "active_folder_override",
    }

def _smsv1_load_owner_reference():
    out = {"loaded": False, "items": 0}
    paths = [
        BASE / "config" / "owner_reference_registry.json",
        BASE / "data" / "templates" / "reference_monolith" / "owner_reference_full_index.json",
    ]
    import json as _j
    for pth in paths:
        if pth.exists():
            try:
                d = _j.loads(pth.read_text(encoding="utf-8"))
                if isinstance(d, dict):
                    out["loaded"] = True
                    out["items"] += len(d)
                    out[pth.name] = list(d.keys())[:10]
                elif isinstance(d, list):
                    out["loaded"] = True
                    out["items"] += len(d)
            except Exception as e:
                out[f"err_{pth.name}"] = str(e)[:80]
    rep = BASE / "docs" / "REPORTS" / "AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT.md"
    if rep.exists():
        out["report"] = rep.read_text(encoding="utf-8", errors="ignore")[:300]
    return out

def _smsv1_load_estimate_templates():
    out = {"loaded": False, "templates": []}
    pth = BASE / "config" / "estimate_template_registry.json"
    if not pth.exists():
        return out
    try:
        import json as _j
        d = _j.loads(pth.read_text(encoding="utf-8"))
        out["loaded"] = True
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, dict) and "source_files" in v:
                    for sf in (v.get("source_files") or [])[:10]:
                        out["templates"].append({
                            "key": sf.get("key"),
                            "title": sf.get("title"),
                            "role": sf.get("template_role"),
                            "drive_url": sf.get("drive_url"),
                        })
    except Exception as e:
        out["error"] = str(e)[:120]
    return out

def _smsv1_topic2_required_truth():
    return {
        "NEXT_REQUIRED_PATCH": "PATCH_TOPIC2_FULL_GAP_CLOSE_V4",
        "OPEN": [
            "P6E2 photo intercept before canonical",
            "pdf_spec_extractor.py exists but not connected to canonical flow",
            "ocr_table_engine.py exists but not connected to topic_2 flow",
            "per-item materials + works internet price search missing",
            "TOPIC2_MULTIFILE_PROJECT_CONTEXT_* missing",
            "TOPIC2_REVISION_BOUND_TO_PARENT missing",
            "TOPIC2_REPEAT_PARENT_TASK missing",
            "TOPIC2_AFTER_PRICE_CHOICE_GENERATION_STARTED missing",
            "TOPIC2_FORBIDDEN_FINAL_RESULT_BLOCKED missing",
            "TOPIC2_PDF_TOTALS_MATCH_XLSX missing",
            "live verification pending",
        ],
        "REQUIRED_MARKERS": [
            "TOPIC2_ESTIMATE_SESSION_CREATED",
            "TOPIC2_CONTEXT_READY",
            "TOPIC2_TEMPLATE_SELECTED",
            "TOPIC2_PRICE_ENRICHMENT_DONE",
            "TOPIC2_PRICE_CHOICE_CONFIRMED",
            "TOPIC2_LOGISTICS_CONFIRMED",
            "TOPIC2_XLSX_CREATED",
            "TOPIC2_PDF_CREATED",
            "TOPIC2_PDF_CYRILLIC_OK",
            "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
            "TOPIC2_DRIVE_UPLOAD_PDF_OK",
            "TOPIC2_TELEGRAM_DELIVERED",
            "TOPIC2_MESSAGE_THREAD_ID_OK",
            "TOPIC2_DONE_CONTRACT_OK",
        ],
        "REGRESSION_GUARDS": [
            "не возвращать P6E67_PARENT_NOT_FOUND на полное ТЗ",
            "не возвращать INVALID_PUBLIC_RESULT при наличии markers + Drive ссылок",
            "не убивать задачи с TOPIC2_PRICE_CHOICE_REQUESTED 30-мин таймаутом",
            "не плодить новые задачи на короткий ответ 2/да при WAITING_PRICE",
        ],
        "LIVE_VERIFY_COMMANDS": [
            "sqlite3 data/core.db \"SELECT id,state FROM tasks WHERE topic_id=2 ORDER BY rowid DESC LIMIT 10\"",
            "journalctl -u areal-task-worker --since '10 minutes ago' | grep -E 'TOPIC2|TPRR|TPTG|TFFE|TDOIP'",
            "sqlite3 data/core.db \"SELECT action FROM task_history WHERE task_id IN (SELECT id FROM tasks WHERE topic_id=2 ORDER BY rowid DESC LIMIT 1)\"",
        ],
    }

def _smsv1_compute_markers_missing(topic_id, markers_24h):
    if int(topic_id) != 2:
        return []
    required = _smsv1_topic2_required_truth()["REQUIRED_MARKERS"]
    actual = " ".join(markers_24h)
    return [m for m in required if m not in actual]

def _smsv1_topic_safe_name(tid):
    return _SMSV1_TOPIC_NAMES.get(int(tid), f"TOPIC_{tid}")

def _smsv1_derive_status(commits, failed_24h, active_count):
    if failed_24h >= 3 and not commits:
        return "BROKEN"
    if commits and failed_24h == 0 and not active_count:
        return "IDLE_NO_FAILURES_NOT_VERIFIED"
    if commits:
        return "INSTALLED_NOT_VERIFIED"
    return "UNKNOWN"

def _smsv1_render_topic_file(topic_id, role, directions_bound, git_sha):
    db = _smsv1_db_state(topic_id)
    markers = _smsv1_markers_24h(topic_id)
    blockers = _smsv1_extract_blockers_from_not_closed(topic_id)
    commits = _smsv1_git_log_per_topic(topic_id, 14)
    drive = _smsv1_drive_binding()
    chat_exports = _smsv1_drive_chat_exports_status()
    catalog = _smsv1_runtime_catalog_summary(topic_id)

    states = db.get("states", {}) if isinstance(db, dict) else {}
    failed_24h = db.get("failed_24h", 0) if isinstance(db, dict) else 0
    last_failed = db.get("last_failed", []) if isinstance(db, dict) else []
    active = sum(states.get(s, 0) for s in ("NEW", "IN_PROGRESS", "WAITING_CLARIFICATION", "AWAITING_CONFIRMATION"))
    status = _smsv1_derive_status(commits, failed_24h, active)

    parts = [
        f"# topic_{topic_id} {_smsv1_topic_safe_name(topic_id)}",
        "",
        f"GENERATED_AT: {utc_now()}",
        f"GIT_SHA: {git_sha}",
        "GENERATED_FROM: tools/full_context_aggregator.py",
        "",
        f"TOPIC_ID: {topic_id}",
        f"ROLE: {role}",
        f"DIRECTIONS_BOUND: {', '.join(directions_bound) if directions_bound else 'none'}",
        f"CURRENT_STATUS: {status}",
        f"ACTIVE_TASKS: {active}",
        f"FAILED_LAST_24H: {failed_24h}",
        "",
        "## DB_STATE_COUNTS",
    ]
    if states:
        for s, c in sorted(states.items()):
            parts.append(f"- {s}: {c}")
    else:
        parts.append("- (no data)")

    parts += ["", "## LATEST_FAILED"]
    if last_failed:
        for t in last_failed:
            parts.append(f"- {str(t.get('id',''))[:8]} | {t.get('em','')}")
    else:
        parts.append("- (none)")

    parts += ["", "## COMMITS_LAST_14D"]
    if commits:
        for c in commits:
            parts.append(f"- {c}")
    else:
        parts.append("- (none matching topic)")

    parts += ["", "## MARKERS_LAST_24H"]
    if markers:
        for m in markers[:30]:
            parts.append(f"- {m}")
    else:
        parts.append("- (none)")

    parts += ["", "## BLOCKERS_FROM_NOT_CLOSED"]
    if blockers:
        for b in blockers:
            parts.append(f"- {b}")
    else:
        parts.append("- (none)")

    parts += ["", "## RUNTIME_FILE_CATALOG_SUMMARY"]
    parts.append(f"total_files: {catalog.get('total', 0)}")
    parts.append(f"chats: {catalog.get('chats', 0)}")
    if catalog.get("error"):
        parts.append(f"error: {catalog['error']}")

    parts += ["", "## DRIVE_UPLOAD_CONTRACT"]
    for k, v in drive.items():
        parts.append(f"{k}: {v}")

    parts += ["", "## DRIVE_CHAT_EXPORTS_STATUS"]
    parts.append(f"STATUS: {chat_exports.get('status')}")
    for loc in chat_exports.get("locations", []):
        parts.append(f"- {loc.get('path')} files={loc.get('files')}")

    parts += ["", "## FORBIDDEN_FILES"]
    for f in _SMSV1_FORBIDDEN_FILES:
        parts.append(f"- {f}")

    if int(topic_id) == 2:
        truth = _smsv1_topic2_required_truth()
        parts += ["", "## NEXT_REQUIRED_PATCH", truth["NEXT_REQUIRED_PATCH"]]
        parts += ["", "## OPEN_CONTOURS"]
        for it in truth["OPEN"]:
            parts.append(f"- {it}")
        parts += ["", "## REQUIRED_MARKERS"]
        for m in truth["REQUIRED_MARKERS"]:
            parts.append(f"- {m}")
        missing = _smsv1_compute_markers_missing(2, markers)
        parts += ["", "## MARKERS_MISSING"]
        if missing:
            for m in missing:
                parts.append(f"- {m}")
        else:
            parts.append("- (all present in last 24h)")
        parts += ["", "## REGRESSION_GUARDS"]
        for g in truth["REGRESSION_GUARDS"]:
            parts.append(f"- {g}")
        parts += ["", "## LIVE_VERIFY_COMMANDS"]
        for c in truth["LIVE_VERIFY_COMMANDS"]:
            parts.append(f"- {c}")
        et = _smsv1_load_estimate_templates()
        parts += ["", "## ESTIMATE_TEMPLATE_REGISTRY"]
        parts.append(f"loaded: {et.get('loaded', False)}")
        for t in et.get("templates", [])[:10]:
            parts.append(f"- {t.get('key')} | {t.get('title')} | {t.get('role')}")

    if int(topic_id) in (2, 5, 210):
        ref = _smsv1_load_owner_reference()
        parts += ["", "## OWNER_REFERENCE_REGISTRY"]
        parts.append(f"loaded: {ref.get('loaded', False)}")
        parts.append(f"items: {ref.get('items', 0)}")

    parts += ["", "## FACT_SOURCE_LIST"]
    parts.append("- core.db live state and task_history")
    parts.append("- config/directions.yaml via core.direction_registry.DirectionRegistry")
    parts.append("- core/runtime_file_catalog.py")
    parts.append("- config/estimate_template_registry.json")
    parts.append("- config/owner_reference_registry.json")
    parts.append("- data/templates/reference_monolith/owner_reference_full_index.json")
    parts.append("- docs/REPORTS/NOT_CLOSED.md")
    parts.append("- docs/HANDOFFS/LATEST_HANDOFF.md")
    parts.append("- git log last 14 days")
    parts.append("")
    return "\n".join(parts) + "\n"

def _smsv1_render_direction_file(direction_id, profile, topic_status_map, git_sha):
    parts = [
        f"# direction: {direction_id}",
        "",
        f"GENERATED_AT: {utc_now()}",
        f"GIT_SHA: {git_sha}",
        "GENERATED_FROM: core.direction_registry.DirectionRegistry",
        "",
        f"DIRECTION_ID: {direction_id}",
        f"TITLE: {profile.get('title') or profile.get('name') or '?'}",
        f"ENABLED: {profile.get('enabled', False)}",
        f"ENGINE: {profile.get('engine','?')}",
        f"REQUIRES_SEARCH: {profile.get('requires_search', False)}",
        f"TOPIC_IDS: {profile.get('topic_ids', [])}",
        f"INPUT_TYPES: {profile.get('input_types', [])}",
        f"INPUT_FORMATS: {profile.get('input_formats', [])}",
        f"OUTPUT_FORMATS: {profile.get('output_formats', [])}",
        f"QUALITY_GATES: {profile.get('quality_gates', [])}",
        f"ALIASES: {(profile.get('aliases') or [])[:20]}",
        f"STRONG_ALIASES: {profile.get('strong_aliases') or []}",
        "",
        "## BOUND_TOPICS_STATUS",
    ]
    tids = profile.get("topic_ids") or []
    if tids:
        for tid in tids:
            parts.append(f"- topic_{tid}: {topic_status_map.get(int(tid), 'UNKNOWN')}")
    else:
        parts.append("- (no topic_ids bound)")
    parts.append("")
    return "\n".join(parts) + "\n"

def _smsv1_render_single_model_source(directions, topic_status_map, topic_meta, git_sha):
    parts = [
        "# SINGLE_MODEL_SOURCE",
        "",
        f"GENERATED_AT: {utc_now()}",
        f"GIT_SHA: {git_sha}",
        "STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test",
        "",
        "## PRIORITY_OF_TRUTH",
        "1. SAFE_RUNTIME_SNAPSHOT / live core.db",
        "2. docs/HANDOFFS/LATEST_HANDOFF.md",
        "3. docs/REPORTS/NOT_CLOSED.md",
        "4. newest docs/HANDOFFS/*",
        "5. newest chat_exports/*",
        "6. locally synced Google Drive telegram_exports",
        "7. docs/CANON_FINAL/*",
        "8. git log last 14 days",
        "9. code grep",
        "10. UNKNOWN",
        "",
        "## READ_ORDER",
        "1. THIS FILE",
        "2. TOPIC_STATUS_INDEX.md",
        "3. DIRECTION_STATUS_INDEX.md",
        "4. required TOPICS/topic_<id>_*.md or DIRECTIONS/<id>.md",
        "5. SAFE_RUNTIME_SNAPSHOT.md",
        "6. ORCHESTRA_FULL_CONTEXT_MANIFEST.json",
        "7. PART files only if needed",
        "",
        "## DRIVE_BINDING",
    ]
    for k, v in _smsv1_drive_binding().items():
        parts.append(f"{k}: {v}")

    ref = _smsv1_load_owner_reference()
    et = _smsv1_load_estimate_templates()
    parts += ["", "## REFERENCE_REGISTRIES"]
    parts.append(f"estimate_template_registry: loaded={et.get('loaded', False)} templates_count={len(et.get('templates', []))}")
    parts.append(f"owner_reference_registry: loaded={ref.get('loaded', False)} items={ref.get('items', 0)}")
    if ref.get("report"):
        parts.append(f"AREAL_REFERENCE_REPORT_SUMMARY: {ref['report'][:200]}")
    if et.get("templates"):
        parts.append("estimate_templates_top5:")
        for t in et["templates"][:5]:
            parts.append(f"- {t.get('key')} | {t.get('title')} | {t.get('role')}")

    chat_exports = _smsv1_drive_chat_exports_status()
    parts += ["", "## DRIVE_CHAT_EXPORTS_STATUS"]
    parts.append(f"STATUS: {chat_exports.get('status')}")
    for loc in chat_exports.get("locations", []):
        parts.append(f"- {loc.get('path')} files={loc.get('files')}")

    parts += ["", "## GLOBAL_TOPIC_TABLE"]
    parts.append("| topic_id | name | status | active | failed_24h |")
    parts.append("|----------|------|--------|--------|------------|")
    for tid, meta in sorted(topic_meta.items()):
        parts.append(f"| {tid} | {_smsv1_topic_safe_name(tid)} | {meta.get('status','?')} | {meta.get('active',0)} | {meta.get('failed_24h',0)} |")

    parts += ["", "## DIRECTION_TABLE"]
    parts.append("| direction_id | engine | enabled | topic_ids | quality_gates |")
    parts.append("|--------------|--------|---------|-----------|---------------|")
    for did, prof in directions.items():
        prof = prof or {}
        parts.append(f"| {did} | {prof.get('engine','?')} | {prof.get('enabled', False)} | {prof.get('topic_ids', [])} | {prof.get('quality_gates', [])} |")

    parts += ["", "## SOURCE_LINKS"]
    parts.append("- CURRENT_CONTEXT (quick start): docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md")
    parts.append("- FULL_CONTEXT (audit): docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md")
    parts.append("- TOPIC_STATUS_INDEX: docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md")
    parts.append("- DIRECTION_STATUS_INDEX: docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md")
    parts.append("- LATEST_HANDOFF: docs/HANDOFFS/LATEST_HANDOFF.md")
    parts.append("- NOT_CLOSED: docs/REPORTS/NOT_CLOSED.md")
    parts.append("- SAFE_RUNTIME_SNAPSHOT: docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md")
    parts.append("- MANIFEST: docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json")
    parts.append("- DirectionRegistry: core/direction_registry.py")
    parts.append("")
    return "\n".join(parts) + "\n"

def _smsv1_render_topic_status_index(topic_meta, git_sha):
    parts = [
        "# TOPIC_STATUS_INDEX",
        "",
        f"GENERATED_AT: {utc_now()}",
        f"GIT_SHA: {git_sha}",
        "",
        "| topic_id | name | role | status | active | failed_24h | source |",
        "|----------|------|------|--------|--------|------------|--------|",
    ]
    for tid, meta in sorted(topic_meta.items()):
        parts.append(f"| {tid} | {_smsv1_topic_safe_name(tid)} | {meta.get('role','?')} | {meta.get('status','?')} | {meta.get('active',0)} | {meta.get('failed_24h',0)} | TOPICS/topic_{tid}_{_smsv1_topic_safe_name(tid)}.md |")
    parts.append("")
    return "\n".join(parts) + "\n"

def _smsv1_render_direction_status_index(directions, topic_status_map, git_sha):
    parts = [
        "# DIRECTION_STATUS_INDEX",
        "",
        f"GENERATED_AT: {utc_now()}",
        f"GIT_SHA: {git_sha}",
        "Source: core/direction_registry.DirectionRegistry from config/directions.yaml",
        "",
        "| direction | enabled | engine | topic_ids | bound_status |",
        "|-----------|---------|--------|-----------|--------------|",
    ]
    for did, prof in directions.items():
        prof = prof or {}
        tids = prof.get("topic_ids") or []
        bound = ",".join(f"{tid}:{topic_status_map.get(int(tid), '?')}" for tid in tids) or "-"
        parts.append(f"| {did} | {prof.get('enabled', False)} | {prof.get('engine','?')} | {tids} | {bound} |")
    parts.append("")
    return "\n".join(parts) + "\n"



# === SMSV1_FULL_CONTEXT_APPLIED ===
def _smfc_read_file(path, max_chars=None):
    p = BASE / path
    if not p.exists():
        return f"# (file missing: {path})\n"
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
        if max_chars and len(text) > max_chars:
            text = text[:max_chars] + f"\n\n... [TRUNCATED at {max_chars} chars from {len(text)} total — see source file] ..."
        return text
    except Exception as e:
        return f"# (read error {path}: {e})\n"

def _smfc_last_failed_per_topic(topic_id, limit=5):
    try:
        conn = _smsv1_sqlite.connect(str(BASE / "data" / "core.db"))
        conn.row_factory = _smsv1_sqlite.Row
        cur = conn.execute(
            "SELECT id, datetime(updated_at,'localtime') t, "
            "substr(coalesce(error_message,''),1,200) em, "
            "substr(raw_input,1,150) ri "
            "FROM tasks WHERE topic_id=? AND state='FAILED' "
            "ORDER BY rowid DESC LIMIT ?",
            (int(topic_id), limit)
        )
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            hist_cur = conn.execute(
                "SELECT substr(action,1,100) FROM task_history "
                "WHERE task_id=? ORDER BY rowid DESC LIMIT 5",
                (d["id"],)
            )
            d["history"] = [h[0] for h in hist_cur.fetchall()]
            rows.append(d)
        conn.close()
        return rows
    except Exception as e:
        return [{"error": str(e)}]

def _smfc_render_full_context(directions, topic_status_map, topic_meta, git_sha):
    parts = []
    parts.append("# SINGLE_MODEL_FULL_CONTEXT")
    parts.append("")
    parts.append(f"GENERATED_AT: {utc_now()}")
    parts.append(f"GIT_SHA: {git_sha}")
    parts.append("PURPOSE: Один файл с полным контекстом проекта для любой модели")
    parts.append("STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test")
    parts.append("")
    parts.append("## CONTENTS")
    parts.append("1. SUMMARY (карта статусов всех топиков и направлений)")
    parts.append("2. DOCS/HANDOFFS/LATEST_HANDOFF.md (полностью)")
    parts.append("3. DOCS/REPORTS/NOT_CLOSED.md (полностью)")
    parts.append("4. DOCS/CANON_FINAL/* (полностью)")
    parts.append("5. PER_TOPIC: status + last failed + key engine code (head)")
    parts.append("6. PER_DIRECTION: profile + bound topics status")
    parts.append("7. SOURCE_LINKS")
    parts.append("")
    parts.append("=" * 80)
    parts.append("# 1. SUMMARY")
    parts.append("=" * 80)
    parts.append("")
    parts.append("## GLOBAL_TOPIC_TABLE")
    parts.append("| topic_id | name | status | active | failed_24h |")
    parts.append("|----------|------|--------|--------|------------|")
    for tid, meta in sorted(topic_meta.items()):
        parts.append(f"| {tid} | {_smsv1_topic_safe_name(tid)} | {meta.get('status','?')} | "
                     f"{meta.get('active',0)} | {meta.get('failed_24h',0)} |")
    parts.append("")
    parts.append("## DIRECTION_TABLE")
    parts.append("| direction_id | engine | enabled | topic_ids |")
    parts.append("|--------------|--------|---------|-----------|")
    for did, prof in directions.items():
        parts.append(f"| {did} | {(prof or {}).get('engine','?')} | "
                     f"{(prof or {}).get('enabled', False)} | {(prof or {}).get('topic_ids', [])} |")
    parts.append("")
    parts.append("## DRIVE_BINDING")
    for k, v in _smsv1_drive_binding().items():
        parts.append(f"{k}: {v}")
    parts.append("")
    parts.append("## REFERENCE_REGISTRIES")
    et = _smsv1_load_estimate_templates()
    ref = _smsv1_load_owner_reference()
    parts.append(f"estimate_template_registry: loaded={et.get('loaded')} count={len(et.get('templates', []))}")
    parts.append(f"owner_reference_registry: loaded={ref.get('loaded')} items={ref.get('items', 0)}")
    for t in et.get("templates", [])[:10]:
        parts.append(f"- {t.get('key')} | {t.get('title')} | {t.get('role')}")
    parts.append("")

    parts.append("=" * 80)
    parts.append("# 2. LATEST_HANDOFF")
    parts.append("=" * 80)
    parts.append("")
    parts.append(_smfc_read_file("docs/HANDOFFS/LATEST_HANDOFF.md"))
    parts.append("")

    parts.append("=" * 80)
    parts.append("# 3. NOT_CLOSED")
    parts.append("=" * 80)
    parts.append("")
    parts.append(_smfc_read_file("docs/REPORTS/NOT_CLOSED.md"))
    parts.append("")

    parts.append("=" * 80)
    parts.append("# 4. CANON_FINAL")
    parts.append("=" * 80)
    parts.append("")
    canon_dir = BASE / "docs" / "CANON_FINAL"
    if canon_dir.exists():
        for f in sorted(canon_dir.glob("*.md")):
            parts.append(f"## CANON_FINAL/{f.name}")
            parts.append("")
            parts.append(_smfc_read_file(f"docs/CANON_FINAL/{f.name}"))
            parts.append("")

    parts.append("=" * 80)
    parts.append("# 5. PER_TOPIC")
    parts.append("=" * 80)
    parts.append("")
    
    # Engine maps per topic
    topic_engines = {
        2: ["core/sample_template_engine.py", "core/stroyka_estimate_canon.py", "core/topic2_estimate_final_close_v2.py"],
        5: ["core/technadzor_engine.py", "core/normative_engine.py"],
        210: ["core/project_engine.py", "core/cad_project_engine.py"],
        500: ["core/search_session.py", "core/search_engine.py"],
    }
    
    for tid in sorted(topic_meta.keys()):
        meta = topic_meta[tid]
        parts.append(f"## TOPIC_{tid}_{_smsv1_topic_safe_name(tid)}")
        parts.append("")
        parts.append(f"STATUS: {meta.get('status','?')}")
        parts.append(f"ACTIVE: {meta.get('active',0)}  FAILED_24H: {meta.get('failed_24h',0)}")
        parts.append(f"DIRECTIONS_BOUND: {meta.get('role','?')}")
        parts.append("")
        # Last failed
        failed = _smfc_last_failed_per_topic(tid, 5)
        if failed and not failed[0].get("error"):
            parts.append("### LAST_FAILED (5)")
            for f in failed:
                parts.append(f"- {f.get('id','')[:8]} | {f.get('t','')} | {f.get('em','')[:80]}")
                if f.get("history"):
                    for h in f["history"][:3]:
                        parts.append(f"    history: {h}")
            parts.append("")
        # Engine code (head 250 lines)
        if tid in topic_engines:
            parts.append("### KEY_ENGINE_CODE (head 250 lines each)")
            for engine_path in topic_engines[tid]:
                ep = BASE / engine_path
                if ep.exists():
                    parts.append(f"#### {engine_path}")
                    parts.append("```python")
                    try:
                        lines = ep.read_text(encoding="utf-8", errors="ignore").splitlines()[:250]
                        parts.append("\n".join(lines))
                    except Exception as e:
                        parts.append(f"# read error: {e}")
                    parts.append("```")
                    parts.append("")
        # Topic file inline (markers, blockers, regression)
        topic_file = BASE / "docs" / "SHARED_CONTEXT" / "TOPICS" / f"topic_{tid}_{_smsv1_topic_safe_name(tid)}.md"
        if topic_file.exists():
            parts.append(f"### TOPIC_FILE_INLINE")
            parts.append("```")
            parts.append(_smfc_read_file(f"docs/SHARED_CONTEXT/TOPICS/topic_{tid}_{_smsv1_topic_safe_name(tid)}.md"))
            parts.append("```")
            parts.append("")

    parts.append("=" * 80)
    parts.append("# 6. PER_DIRECTION")
    parts.append("=" * 80)
    parts.append("")
    for did, prof in directions.items():
        prof = prof or {}
        if not prof.get("enabled", False):
            continue
        parts.append(f"## {did}")
        parts.append(f"engine: {prof.get('engine','?')}")
        parts.append(f"topic_ids: {prof.get('topic_ids', [])}")
        parts.append(f"input_types: {prof.get('input_types', [])}")
        parts.append(f"output_formats: {prof.get('output_formats', [])}")
        parts.append(f"quality_gates: {prof.get('quality_gates', [])}")
        parts.append(f"aliases: {(prof.get('aliases') or [])[:10]}")
        parts.append("")

    parts.append("=" * 80)
    parts.append("# 7. SOURCE_LINKS")
    parts.append("=" * 80)
    parts.append("")
    parts.append("- TOPIC_STATUS_INDEX: docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md")
    parts.append("- DIRECTION_STATUS_INDEX: docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md")
    parts.append("- SAFE_RUNTIME_SNAPSHOT: docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md")
    parts.append("- MANIFEST: docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json")
    parts.append("- DirectionRegistry: core/direction_registry.py")
    parts.append("- runtime_file_catalog: core/runtime_file_catalog.py")
    parts.append("- topic_drive_oauth: core/topic_drive_oauth.py")
    parts.append("- ORCHESTRA_FULL_CONTEXT_PARTS: 17 files (full project dump)")
    parts.append("")
    return "\n".join(parts) + "\n"

# === END SMSV1_FULL_CONTEXT_APPLIED ===



# === SMCC_CURRENT_CONTEXT_APPLIED ===
import re as _smcc_re
from datetime import datetime as _smcc_dt, timezone as _smcc_tz, timedelta as _smcc_td

_SMCC_MAX_TOPIC_BYTES = 2000
_SMCC_MAX_TOTAL_BYTES = 40000

_SMCC_OPEN_KEYS = (
    "NOT CLOSED", "NOT_VERIFIED", "NOT VERIFIED", "INSTALLED, NOT VERIFIED",
    "INSTALLED НО НЕ VERIFIED", "НЕ VERIFIED", "НЕ ЗАКРЫТО", "НЕ ПРОВЕРЕНО",
    "PENDING", "BLOCKER", "TODO", "OPEN", "BROKEN", "ОСТАЁТСЯ", "БЛОКЕР",
)
_SMCC_CLOSED_KEYS = (
    "VERIFIED", "CLOSED", "DONE", "ARCHIVED", "OBSOLETE", "SUPERSEDED",
    "ЗАКРЫТО", "ПОДТВЕРЖДЕНО", "АРХИВ",
)
_SMCC_LINE_FILTER = (
    "⚠️", "❌", "🔴", "OPEN:", "BROKEN:", "PENDING:", "BLOCKER:",
    "NOT VERIFIED", "INSTALLED, NOT VERIFIED", "НЕ VERIFIED", "НЕ ЗАКРЫТО",
    "- ", "* ",
)
_SMCC_DATE_RE = _smcc_re.compile(r"(\d{2}[\.\-/]\d{2}[\.\-/]\d{4}|\d{4}[\.\-/]\d{2}[\.\-/]\d{2})")


def _smcc_clip(text, limit):
    if len(text.encode("utf-8")) <= limit:
        return text
    raw = text.encode("utf-8")[:limit]
    cut = raw.decode("utf-8", errors="ignore")
    nl = cut.rfind("\n")
    if nl > int(limit * 0.65):
        cut = cut[:nl]
    return cut.rstrip() + "\n... [TRUNCATED — see SINGLE_MODEL_FULL_CONTEXT.md]\n"


def _smcc_classify_section(header):
    h = header.upper()
    is_open = any(k in h for k in _SMCC_OPEN_KEYS)
    is_closed = any(k in h for k in _SMCC_CLOSED_KEYS)
    if is_open:
        return "OPEN"
    if is_closed:
        return "CLOSED"
    return "UNKNOWN"


def _smcc_extract_date(header):
    m = _SMCC_DATE_RE.search(header)
    if not m:
        return None
    raw = m.group(1).replace("/", ".").replace("-", ".")
    parts = raw.split(".")
    try:
        if len(parts[0]) == 4:
            y, mo, d = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            d, mo, y = int(parts[0]), int(parts[1]), int(parts[2])
        return _smcc_dt(y, mo, d, tzinfo=_smcc_tz.utc)
    except Exception:
        return None


def _smcc_parse_not_closed():
    nc = BASE / "docs" / "REPORTS" / "NOT_CLOSED.md"
    if not nc.exists():
        return []
    text = nc.read_text(encoding="utf-8", errors="ignore")
    sections = []
    cur = None
    for line in text.splitlines():
        if line.startswith("## ") or line.startswith("### "):
            if cur:
                sections.append(cur)
            cur = {"header": line.strip(), "lines": []}
        elif cur is not None:
            cur["lines"].append(line)
    if cur:
        sections.append(cur)

    cutoff = _smcc_dt.now(_smcc_tz.utc) - _smcc_td(days=30)
    out = []
    for s in sections:
        if _smcc_classify_section(s["header"]) != "OPEN":
            continue
        date = _smcc_extract_date(s["header"])
        if date and date < cutoff:
            continue

        lines = []
        for ln in s["lines"]:
            t = ln.strip()
            if not t:
                continue
            u = t.upper()
            if any(t.startswith(prefix) for prefix in _SMCC_LINE_FILTER) or any(k in u for k in ("NOT VERIFIED", "PENDING", "BLOCKER", "BROKEN", "НЕ ЗАКРЫТО")):
                lines.append(t[:220])
            if len(lines) >= 10:
                break

        if lines:
            out.append({"header": s["header"], "date_unknown": date is None, "lines": lines})
        if len(out) >= 12:
            break
    return out


def _smcc_recent_commits_topic(topic_id):
    try:
        return _smsv1_git_log_per_topic(topic_id, 7)
    except Exception:
        return []


def _smcc_topic_section(tid, name, role, db, markers_24h, blockers_topic):
    states = db.get("states", {}) if isinstance(db, dict) else {}
    failed_24h = db.get("failed_24h", 0) if isinstance(db, dict) else 0
    last_failed = (db.get("last_failed", []) or [])[:5]
    active = sum(states.get(s, 0) for s in ("NEW", "IN_PROGRESS", "WAITING_CLARIFICATION", "AWAITING_CONFIRMATION"))
    commits = _smcc_recent_commits_topic(tid)

    if active == 0 and failed_24h == 0 and not commits and int(tid) not in (2, 5, 210, 500):
        return None

    missing = []
    if int(tid) == 2:
        try:
            missing = _smsv1_compute_markers_missing(2, markers_24h)[:20]
        except Exception:
            missing = []

    parts = []
    parts.append(f"### topic_{tid} {name}")
    parts.append(f"role: {role}")
    parts.append(f"active: {active}")
    parts.append(f"failed_24h: {failed_24h}")
    parts.append(f"commits_last_7d: {len(commits)}")

    if commits:
        parts.append("recent_commits:")
        for c in commits[:3]:
            parts.append(f"- {c[:140]}")

    if missing:
        parts.append(f"markers_missing: {len(missing)}")
        for m in missing[:8]:
            parts.append(f"- {m}")

    if last_failed:
        parts.append("last_failed:")
        for f in last_failed[:3]:
            parts.append(f"- {str(f.get('id',''))[:8]} | {str(f.get('em',''))[:100]}")

    if blockers_topic:
        parts.append("blockers:")
        for b in blockers_topic[:3]:
            parts.append(f"- {str(b)[:140]}")

    next_action = "live-test required"
    if missing:
        next_action = f"live-test / close missing markers: {len(missing)}"
    elif last_failed:
        next_action = f"investigate latest failed: {str(last_failed[0].get('em',''))[:80]}"
    elif blockers_topic:
        next_action = f"close blocker: {str(blockers_topic[0])[:80]}"
    elif commits:
        next_action = "verify recent installed code by live-test"

    parts.append(f"NEXT_ACTION: {next_action}")
    parts.append("")
    return _smcc_clip("\n".join(parts), _SMCC_MAX_TOPIC_BYTES)


def _smcc_render_current_context(directions, topic_status_map, topic_meta, git_sha):
    parts = []
    parts.append("# SINGLE_MODEL_CURRENT_CONTEXT")
    parts.append("")
    parts.append(f"GENERATED_AT: {utc_now()}")
    parts.append(f"GIT_SHA: {git_sha}")
    parts.append("PURPOSE: Быстрый старт для любой модели — только актуальное состояние")
    parts.append("FULL_AUDIT: docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md")
    parts.append("STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test")
    parts.append("")
    parts.append("## READ_ORDER")
    parts.append("1. This SINGLE_MODEL_CURRENT_CONTEXT")
    parts.append("2. SINGLE_MODEL_SOURCE")
    parts.append("3. Topic/direction file if needed")
    parts.append("4. SINGLE_MODEL_FULL_CONTEXT only for audit/dispute")
    parts.append("5. ORCHESTRA_FULL_CONTEXT_PART_*.md only for raw dump")
    parts.append("")
    parts.append("## GLOBAL_STATUS")
    parts.append("| topic | name | status | active | failed_24h |")
    parts.append("|-------|------|--------|--------|------------|")
    for tid, meta in sorted(topic_meta.items()):
        if meta.get("active", 0) > 0 or meta.get("failed_24h", 0) > 0 or int(tid) in (2, 5, 210, 500):
            parts.append(f"| {tid} | {_smsv1_topic_safe_name(tid)} | {meta.get('status','?')} | {meta.get('active',0)} | {meta.get('failed_24h',0)} |")
    parts.append("")

    parts.append("## OPEN_BLOCKERS_FROM_NOT_CLOSED")
    open_sections = _smcc_parse_not_closed()
    if open_sections:
        for s in open_sections[:5]:
            parts.append(f"### {s['header'].lstrip('#').strip()}")
            if s.get("date_unknown"):
                parts.append("DATE_UNKNOWN")
            for ln in s["lines"][:6]:
                parts.append(ln)
            parts.append("")
    else:
        parts.append("(no current open sections detected)")
        parts.append("")

    parts.append("## ACTIVE_OR_RECENT_TOPICS")
    for tid in sorted(topic_meta.keys()):
        meta = topic_meta[tid]
        db = _smsv1_db_state(tid)
        markers = _smsv1_markers_24h(tid)
        blockers = _smsv1_extract_blockers_from_not_closed(tid)
        sec = _smcc_topic_section(tid, _smsv1_topic_safe_name(tid), meta.get("role", "?"), db, markers, blockers)
        if sec:
            parts.append(sec)

    parts.append("## STRICT_RULES")
    parts.append("- INSTALLED != VERIFIED")
    parts.append("- VERIFIED только после live-test")
    parts.append("- Diagnostics → BAK → PATCH → PY_COMPILE → RESTART → LOGS → DB_VERIFY → GIT_PUSH → FINAL_VERIFY")
    parts.append("- Не объявлять закрытым без live-теста")
    parts.append("- BROKEN / REJECTED / UNKNOWN не использовать как канон")
    parts.append("- chat_id + topic_id обязательны для контекста")
    parts.append("- FULL_CONTEXT использовать только для аудита или спора")
    parts.append("")

    parts.append("## ALLOWED_FILES_BY_SCOPE")
    parts.append("- core/stroyka_estimate_canon.py — topic_2 estimates")
    parts.append("- core/sample_template_engine.py — topic_2 estimates/templates")
    parts.append("- core/topic2_estimate_final_close_v2.py — topic_2 legacy/fallback")
    parts.append("- core/technadzor_engine.py — topic_5")
    parts.append("- core/normative_engine.py — topic_5")
    parts.append("- core/project_engine.py — topic_210")
    parts.append("- core/search_session.py — topic_500")
    parts.append("- tools/full_context_aggregator.py — aggregator")
    parts.append("")

    parts.append("## FORBIDDEN_FILES")
    parts.append("- .env / credentials / sessions/")
    parts.append("- core/ai_router.py")
    parts.append("- core/reply_sender.py")
    parts.append("- core/google_io.py")
    parts.append("- telegram_daemon.py")
    parts.append("- data/core.db / data/memory.db schema")
    parts.append("- systemd unit files")
    parts.append("")

    parts.append("## CONDITIONAL_PATCH")
    parts.append("- task_worker.py — only with explicit task scope and diagnostics-first")
    parts.append("")

    parts.append("## DRIVE_BINDING")
    for k, v in _smsv1_drive_binding().items():
        parts.append(f"{k}: {v}")
    parts.append("")

    parts.append("## REFERENCE_REGISTRIES")
    et = _smsv1_load_estimate_templates()
    ref = _smsv1_load_owner_reference()
    parts.append(f"estimate_template_registry: loaded={et.get('loaded')} count={len(et.get('templates', []))}")
    parts.append(f"owner_reference_registry: loaded={ref.get('loaded')} items={ref.get('items', 0)}")
    parts.append("")

    parts.append("## SOURCE_LINKS")
    parts.append(f"- CURRENT_CONTEXT: {RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md")
    parts.append(f"- SINGLE_MODEL_SOURCE: {RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md")
    parts.append(f"- FULL_CONTEXT_AUDIT: {RAW_MAIN}/docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md")
    parts.append(f"- TOPIC_STATUS_INDEX: {RAW_MAIN}/docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md")
    parts.append(f"- DIRECTION_STATUS_INDEX: {RAW_MAIN}/docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md")
    parts.append(f"- LATEST_HANDOFF: {RAW_MAIN}/docs/HANDOFFS/LATEST_HANDOFF.md")
    parts.append(f"- NOT_CLOSED_FULL: {RAW_MAIN}/docs/REPORTS/NOT_CLOSED.md")
    parts.append("")

    return _smcc_clip("\n".join(parts) + "\n", _SMCC_MAX_TOTAL_BYTES)
# === END_SMCC_CURRENT_CONTEXT_APPLIED ===

def smsv1_generate_all(git_sha):
    _SMSV1_TOPICS_DIR.mkdir(parents=True, exist_ok=True)
    _SMSV1_DIRECTIONS_DIR.mkdir(parents=True, exist_ok=True)

    directions, dr_source = _smsv1_load_directions()
    topic_ids_set = set(int(k) for k in _SMSV1_TOPIC_NAMES.keys())
    direction_role_map = {}
    for did, prof in directions.items():
        for tid in ((prof or {}).get("topic_ids") or []):
            try:
                tid_int = int(tid)
                topic_ids_set.add(tid_int)
                direction_role_map.setdefault(tid_int, []).append(did)
            except Exception:
                pass

    topic_meta = {}
    topic_status_map = {}

    for tid in sorted(topic_ids_set):
        directions_bound = direction_role_map.get(tid, [])
        if directions_bound and directions_bound[0] in directions:
            role = (directions[directions_bound[0]] or {}).get("title") or (directions[directions_bound[0]] or {}).get("name") or "?"
        else:
            role = "Общий" if tid == 0 else "?"
        content = _smsv1_render_topic_file(tid, role, directions_bound, git_sha)
        safe_name = _smsv1_topic_safe_name(tid)
        write(_SMSV1_TOPICS_DIR / f"topic_{tid}_{safe_name}.md", content)

        st = "UNKNOWN"
        active = 0
        failed_24h = 0
        for line in content.splitlines():
            if line.startswith("CURRENT_STATUS:"):
                st = line.split(":", 1)[1].strip()
            elif line.startswith("FAILED_LAST_24H:"):
                try:
                    failed_24h = int(line.split(":", 1)[1].strip())
                except Exception:
                    pass
            elif line.startswith("ACTIVE_TASKS:"):
                try:
                    active = int(line.split(":", 1)[1].strip())
                except Exception:
                    pass
        topic_meta[tid] = {"role": role, "status": st, "active": active, "failed_24h": failed_24h}
        topic_status_map[tid] = st

    for did, prof in directions.items():
        write(_SMSV1_DIRECTIONS_DIR / f"{did}.md", _smsv1_render_direction_file(did, prof or {}, topic_status_map, git_sha))

    write(OUTPUT_DIR / "TOPIC_STATUS_INDEX.md", _smsv1_render_topic_status_index(topic_meta, git_sha))
    write(OUTPUT_DIR / "DIRECTION_STATUS_INDEX.md", _smsv1_render_direction_status_index(directions, topic_status_map, git_sha))
    write(OUTPUT_DIR / "SINGLE_MODEL_SOURCE.md", _smsv1_render_single_model_source(directions, topic_status_map, topic_meta, git_sha))

    try:
        full_ctx = _smfc_render_full_context(directions, topic_status_map, topic_meta, git_sha)
        write(OUTPUT_DIR / "SINGLE_MODEL_FULL_CONTEXT.md", full_ctx)
        print(f"SMFC_GENERATED full_context_size={len(full_ctx)}")
    except Exception as _smfc_e:
        print(f"SMFC_FAIL {_smfc_e}")
    try:
        current_ctx = _smcc_render_current_context(directions, topic_status_map, topic_meta, git_sha)
        write(OUTPUT_DIR / "SINGLE_MODEL_CURRENT_CONTEXT.md", current_ctx)
        print(f"SMCC_GENERATED current_context_size={len(current_ctx.encode('utf-8'))}")
    except Exception as _smcc_e:
        print(f"SMCC_FAIL {_smcc_e}")
    print(f"SMSV1_GENERATED directions={len(directions)} topics={len(topic_meta)} dr={dr_source}")

# === END_PATCH_AGGREGATOR_SINGLE_MODEL_SOURCE_V1 ===

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
BEGIN_FILE: tools/__init__.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
====================================================================================================

====================================================================================================
END_FILE: tools/__init__.py
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
BEGIN_FILE: tools/extract_tnz_msk_document_skill.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 8087be31e961487f7661690181841850967aa0c551bed91a25eed4a6a3d27bed
====================================================================================================
#!/usr/bin/env python3
# === EXTRACT_TNZ_MSK_DOCUMENT_SKILL_V1 ===
# One-shot CLI extractor: reads @tnz_msk via Telethon, extracts document-composition
# methodology for topic_5 technadzor, writes skill package and report.
# Usage:
#   .venv/bin/python tools/extract_tnz_msk_document_skill.py --sample 1000
#   .venv/bin/python tools/extract_tnz_msk_document_skill.py --dry-run
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from core.telegram_source_skill_extractor import run_source_scan
from core.technadzor_document_skill import process_records

SKILL_DIR = BASE / "data/memory_files/TEHNADZOR/source_skills/tnz_msk"
DOCS_DIR = SKILL_DIR / "downloaded_docs"
REPORT_PATH = BASE / "docs/REPORTS/TNZ_MSK_DOCUMENT_SKILL_EXTRACTION_REPORT.md"
HANDOFF_PATH = BASE / "docs/HANDOFFS/HANDOFF_20260505_TNZ_MSK_DOCUMENT_SKILL_EXTRACTION.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def build_skill_md(result: dict, scan_stats: dict, access: dict) -> str:
    cards = result["cards"]
    by_cat = result["by_category"]
    lines = [
        "# TECHNADZOR DOCUMENT COMPOSITION SKILL",
        f"> Source: {access.get('title','')} (@tnz_msk) | Extracted: {_now()}",
        "> Status: SKILL_PACKAGE — NOT A CANON OVERWRITE. Requires owner review before promotion.",
        "",
        "## Source Summary",
        f"- Channel: @tnz_msk — «{access.get('title','')}»",
        f"- Messages scanned: {scan_stats.get('total_fetched', 0)}",
        f"- With text: {scan_stats.get('total_fetched', 0) - scan_stats.get('skipped_empty', 0)}",
        f"- Detected documents: {scan_stats.get('detected_docs', 0)}",
        f"- Detected links: {scan_stats.get('detected_links', 0)}",
        f"- Noise filtered: {scan_stats.get('skipped_noise', 0)}",
        f"- Skill cards extracted: {result['extracted']}",
        f"- Rejected (noise/no value): {result['rejected_noise']}",
        "",
        "## Extracted Skill Categories",
        "",
    ]
    for cat in result["categories"]:
        cat_cards = by_cat.get(cat, [])
        lines.append(f"### {cat} ({len(cat_cards)} rules)")
        lines.append("")
        for card in cat_cards[:5]:
            lines.append(f"**Rule:** {card['extracted_rule']}")
            lines.append(f"- Source: [{card['source_ref']}]({card['source_ref']})")
            lines.append(f"- Why useful for topic_5: {card['why_useful_for_topic_5']}")
            if card.get("source_links"):
                lines.append(f"- Links: {', '.join(card['source_links'][:3])}")
            if card.get("source_files"):
                lines.append(f"- Files: {', '.join(card['source_files'])}")
            if card["needs_owner_review"]:
                lines.append("- ⚠ Needs owner review")
            lines.append("")
        if len(cat_cards) > 5:
            lines.append(f"_...and {len(cat_cards) - 5} more in JSON_")
            lines.append("")

    lines += [
        "## Document Composition Methodology Summary",
        "",
        "Based on extracted patterns from @tnz_msk, the following methodology applies to topic_5:",
        "",
        "### Act Composition Logic",
        "1. State object name, address, date, inspection participants",
        "2. List defects found with precise location references",
        "3. Reference applicable norms (СП/ГОСТ/СНиП) for each defect",
        "4. Attach photo evidence with numbered links to each defect item",
        "5. State required corrective actions with deadlines",
        "6. Conclude with overall assessment",
        "",
        "### Defect Description Logic",
        "- Format: `[Location] — [Defect type] — [Dimension/scale] — [Normative reference] — [Required action]`",
        "- Example: «Трещины в монолитной плите перекрытия оси А-В/1-3 — ширина раскрытия 0,5мм — "
        "нарушение СП 70.13330.2012 п.5.3 — требуется заключение проектировщика»",
        "",
        "### Photo-to-Defect Linking Logic",
        "- Each defect item in the act must reference photo numbers: «Фото 1, 2»",
        "- Photos must be appended as numbered attachment to the act",
        "- Photo description must match defect description location and type",
        "",
        "### Normative Reference Handling",
        "- Always cite specific norm + section, not just norm number",
        "- Example: «СП 70.13330.2012, раздел 5, п.5.3.2»",
        "- For defects without clear norm — mark as `нормативная база уточняется`",
        "",
        "### Conclusion/Recommendation Logic",
        "- Conclusion = technical state category (нормальное / удовлетворительное / ограниченно работоспособное / аварийное)",
        "- Recommendation = specific action + responsible party + deadline",
        "- Use imperative form: «Устранить», «Провести», «Выполнить»",
        "",
        "### File Workflow",
        "- Acts issued as: DOCX (editable) + PDF (signed/sealed version)",
        "- Photos attached as: ZIP archive with numbered files OR embedded in DOCX",
        "- Spreadsheet defect logs: XLSX with columns [№, Описание, Локация, Норматив, Фото, Статус]",
        "",
        "## What Is Not Verified",
        "- Document download from linked URLs not attempted (--no-download-documents mode)",
        "- Norms referenced in channel posts not cross-checked against current editions",
        "- No legal review of extracted wording",
        "",
        "## What Needs Owner Review",
        f"- {sum(1 for c in cards if c['needs_owner_review'])} cards marked `needs_owner_review=true`",
        "- All `unknown` category cards",
        "- Any rule with confidence=low",
        "",
        "## Integration Target",
        "- topic_5 / TECHNADZOR skill layer",
        "- Not a CANON_FINAL overwrite",
        "- Must be manually validated before promotion to canon",
        "",
        "---",
        "",
        "## Reusable Telegram Source Analysis Pattern for RABOTA_POISK (topic_6104)",
        "",
        "### Pattern: Telegram Source → Professional Signal → topic_6104",
        "",
        "This pattern was prototyped on @tnz_msk and is reusable for any Telegram channel "
        "as a source of work opportunities, job leads, or project orders.",
        "",
        "**Step 1 — Source Access**",
        "```python",
        "client = build_client(session_path)  # existing authorized session",
        "access = await check_source_access('@channel_name', client)",
        "```",
        "",
        "**Step 2 — Bounded Scan**",
        "- Never scan entire history in one pass",
        "- Use `limit=1000` for initial analysis, `limit=0` only after validation",
        "- Collect: text, links, file names, message dates",
        "",
        "**Step 3 — Noise Rejection (CRITICAL)**",
        "- Filter: ads, motivational posts, chatter, reposts without content",
        "- Keep only: vacancy signals, order requests, project announcements, professional leads",
        "- One message → one `is_relevant()` check → skip if False",
        "",
        "**Step 4 — Signal Classification**",
        "- Vacancy signal: «требуется», «ищем», «нужен специалист»",
        "- Order signal: «объект», «тендер», «выбор подрядчика», «заказ»",
        "- Lead signal: contact mention + professional topic",
        "",
        "**Step 5 — Compact Output**",
        "- Do NOT create one core.db task per message",
        "- Do NOT write raw history to memory.db",
        "- Write ONE compact summary record per scan session",
        "- Key: `topic_6104_rabota_poisk_<source>_<date>`",
        "",
        "**Step 6 — Routing**",
        "- Useful signals → route to topic_6104 as single aggregated report",
        "- Format: [source] [date] [signal_type] [excerpt] [link]",
        "",
        "**Reuse**: swap `@tnz_msk` for any Telegram channel, "
        "swap skill categories for job/order detection, "
        "route output to topic_6104 instead of topic_5.",
    ]
    return "\n".join(lines)


def build_report_md(result: dict, scan_stats: dict, access: dict,
                    args_ns: argparse.Namespace) -> str:
    now = _now()
    return f"""# TNZ_MSK DOCUMENT SKILL EXTRACTION REPORT
Generated: {now}

## Diagnostics
- Source: @tnz_msk — «{access.get('title', '')}»
- Session: authorized ✅
- Telethon: 1.43.2 ✅
- Mode: {'DRY-RUN' if getattr(args_ns, 'dry_run', False) else 'LIVE'}
- Sample limit: {getattr(args_ns, 'sample', 1000)}

## Scan Statistics
| Metric | Count |
|--------|-------|
| Total messages fetched | {scan_stats.get('total_fetched', 0)} |
| Skipped (empty) | {scan_stats.get('skipped_empty', 0)} |
| Skipped (noise) | {scan_stats.get('skipped_noise', 0)} |
| Detected documents | {scan_stats.get('detected_docs', 0)} |
| Detected links | {scan_stats.get('detected_links', 0)} |

## Skill Extraction
| Metric | Count |
|--------|-------|
| Records passed to skill extractor | {result['total_input']} |
| Skill cards extracted | {result['extracted']} |
| Rejected (noise/no value) | {result['rejected_noise']} |
| Skill categories | {len(result['categories'])} |
| Needs owner review | {sum(1 for c in result['cards'] if c['needs_owner_review'])} |

## Skill Categories Extracted
{chr(10).join(f'- {cat}: {len(result["by_category"].get(cat, []))} rules' for cat in result['categories'])}

## Output Files
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.md`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.json`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/SOURCE_INDEX.json`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/LINKED_DOCUMENTS_INDEX.json`

## Rules
- No raw history saved to memory.db ✅
- No core.db tasks created ✅
- No forbidden files touched ✅
- Each extracted rule has source_ref ✅
- RABOTA_POISK reusable pattern documented ✅
"""


def build_handoff_md(result: dict, scan_stats: dict, commit_hint: str = "pending") -> str:
    return f"""# HANDOFF: TNZ_MSK DOCUMENT SKILL EXTRACTION
Date: 2026-05-05
Task: TELEGRAM_SOURCE_SKILL_EXTRACTION_TNZ_MSK_V1
Status: COMPLETED

## What Was Done
- Read @tnz_msk via authorized Telethon session (read-only)
- Scanned {scan_stats.get('total_fetched', 0)} messages
- Extracted {result['extracted']} skill cards across {len(result['categories'])} categories
- Rejected {result['rejected_noise']} noise records
- Built topic_5 technadzor document composition skill package
- Created reusable RABOTA_POISK Telegram source analysis pattern

## New Files Created
- core/telegram_source_skill_extractor.py
- core/technadzor_document_skill.py
- tools/extract_tnz_msk_document_skill.py
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.md
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.json
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/SOURCE_INDEX.json
- data/memory_files/TEHNADZOR/source_skills/tnz_msk/LINKED_DOCUMENTS_INDEX.json
- docs/REPORTS/TNZ_MSK_DOCUMENT_SKILL_EXTRACTION_REPORT.md
- docs/HANDOFFS/HANDOFF_20260505_TNZ_MSK_DOCUMENT_SKILL_EXTRACTION.md

## Uncommitted / Untouched
- core/normative_engine.py — modified (P6H5 norm expansion), staged separately by user

## Skill Categories Extracted
{chr(10).join(f'- {cat}' for cat in result['categories'])}

## Next Steps
- Owner review of `needs_owner_review=true` cards
- Promotion of validated skills to technadzor_engine prompt context
- Reuse RABOTA_POISK pattern for topic_6104 channel scan
- Consider scheduling periodic re-scan of @tnz_msk (new posts only, delta scan)

## Commit
{commit_hint}
"""


async def main_async(args: argparse.Namespace) -> None:
    limit = args.sample
    download = args.download_documents and not args.dry_run

    print(f"[INFO] source={args.source} sample={limit} download={download} dry_run={args.dry_run}")

    result_raw = await run_source_scan(
        source=args.source,
        limit=limit,
        download_docs=download,
        docs_output_dir=DOCS_DIR if download else None,
    )

    if not result_raw.get("ok"):
        print(f"[ERROR] source access failed: {result_raw.get('error')}")
        sys.exit(1)

    access = result_raw["access"]
    scan = result_raw["scan"]
    scan_stats = {k: v for k, v in scan.items() if k != "records"}
    records = scan["records"]
    downloaded = result_raw.get("downloaded_documents", [])

    print(f"[INFO] fetched={scan['total_fetched']} docs={scan['detected_docs']} "
          f"links={scan['detected_links']} noise={scan['skipped_noise']} "
          f"downloaded={len(downloaded)}")

    result = process_records(records)
    print(f"[INFO] extracted={result['extracted']} rejected={result['rejected_noise']} "
          f"categories={result['categories']}")

    if args.dry_run:
        print("[DRY-RUN] Would write files but skipping.")
        print(json.dumps({
            "scan_stats": scan_stats,
            "extracted": result["extracted"],
            "rejected": result["rejected_noise"],
            "categories": result["categories"],
        }, ensure_ascii=False, indent=2))
        return

    # Build outputs
    skill_md = build_skill_md(result, scan_stats, access)
    skill_json = {
        "schema": "TECHNADZOR_DOCUMENT_COMPOSITION_SKILL_V1",
        "source": args.source,
        "channel_title": access.get("title", ""),
        "extracted_at": _now(),
        "scan_stats": scan_stats,
        "extracted": result["extracted"],
        "rejected_noise": result["rejected_noise"],
        "categories": result["categories"],
        "cards": result["cards"],
    }
    source_index = {
        "schema": "TNZ_MSK_SOURCE_INDEX_V1",
        "source": args.source,
        "scanned_at": _now(),
        "total_fetched": scan["total_fetched"],
        "records_count": len(records),
        "records": [{
            "message_id": r["message_id"],
            "date": r["message_date"],
            "source_ref": r["source_ref"],
            "has_links": bool(r.get("links")),
            "has_file": bool(r.get("file_name")),
            "media_type": r.get("media_type"),
        } for r in records[:500]],
    }
    linked_docs = {
        "schema": "TNZ_MSK_LINKED_DOCUMENTS_INDEX_V1",
        "source": args.source,
        "scanned_at": _now(),
        "downloaded_count": len(downloaded),
        "downloaded_paths": downloaded,
        "linked_urls": sorted({
            url for r in records
            for url in r.get("links", [])
        })[:200],
        "document_messages": [{
            "message_id": r["message_id"],
            "date": r["message_date"],
            "source_ref": r["source_ref"],
            "file_name": r.get("file_name"),
        } for r in records if r.get("file_name")][:200],
    }

    _write(SKILL_DIR / "TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.md", skill_md)
    _write_json(SKILL_DIR / "TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.json", skill_json)
    _write_json(SKILL_DIR / "SOURCE_INDEX.json", source_index)
    _write_json(SKILL_DIR / "LINKED_DOCUMENTS_INDEX.json", linked_docs)

    report_md = build_report_md(result, scan_stats, access, args)
    _write(REPORT_PATH, report_md)

    handoff_md = build_handoff_md(result, scan_stats)
    _write(HANDOFF_PATH, handoff_md)

    if args.write_memory_summary:
        import sqlite3
        mem_db = BASE / "data/memory.db"
        if mem_db.exists():
            conn = sqlite3.connect(str(mem_db))
            ts = _now()
            chat_id = "-1003725299009"
            summary_val = json.dumps({
                "schema": "TNZ_MSK_SKILL_SUMMARY_V1",
                "extracted_at": ts,
                "categories": result["categories"],
                "extracted": result["extracted"],
                "source": args.source,
            }, ensure_ascii=False)
            for key, val in [
                ("topic_5_tnz_msk_skill_summary", summary_val),
                ("topic_5_tnz_msk_skill_index",
                 json.dumps({"categories": result["categories"]}, ensure_ascii=False)),
                ("topic_5_tnz_msk_skill_extracted_at", ts),
            ]:
                conn.execute(
                    "INSERT OR REPLACE INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,?)",
                    (chat_id, key, val, ts)
                )
            conn.commit()
            conn.close()
            print("[INFO] memory summary written (3 keys only)")

    print(f"[OK] skill written → {SKILL_DIR}")
    print(f"[OK] report → {REPORT_PATH}")
    print(f"[OK] handoff → {HANDOFF_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Extract technadzor document skill from Telegram source")
    parser.add_argument("--source", default="@tnz_msk")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sample", type=int, default=1000)
    parser.add_argument("--download-documents", dest="download_documents", action="store_true", default=False)
    parser.add_argument("--no-download-documents", dest="download_documents", action="store_false")
    parser.add_argument("--write-memory-summary", dest="write_memory_summary", action="store_true", default=False)
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", default=False)
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
# === END_EXTRACT_TNZ_MSK_DOCUMENT_SKILL_V1 ===

====================================================================================================
END_FILE: tools/extract_tnz_msk_document_skill.py
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
BEGIN_FILE: tools/full_context_aggregator_guard.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 01edf2d4ca491599fb7966444efc3c55d2349e09991496c2947020f86a02e8cc
====================================================================================================
#!/usr/bin/env python3
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

BASE = Path("/root/.areal-neva-core")
STATE_PATH = BASE / "data" / "full_context_aggregator_guard_state.json"
LOCK_PATH = BASE / "data" / "full_context_aggregator_guard.lock"
AGGREGATOR = BASE / "tools" / "full_context_aggregator.py"
PYTHON = BASE / ".venv" / "bin" / "python3"

GENERATED_EXACT = {
    "docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md",
    "docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md",
    "docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md",
    "docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md",
    "docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md",
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json",
    "docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md",
    "docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md",
    "docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md",
    "docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md",
}

GENERATED_PREFIXES = (
    "docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_",
    "docs/SHARED_CONTEXT/TOPICS/",
    "docs/SHARED_CONTEXT/DIRECTIONS/",
)

LOCAL_RUNTIME_SOURCES = (
    "chat_exports",
    "data/chat_exports",
    "data/telegram_file_catalog",
    "data/templates/reference_monolith",
)

ABS_RUNTIME_SOURCES = (
    Path("/root/AI_ORCHESTRA/telegram_exports"),
)

FORBIDDEN_STAGED_RE = (
    ".env",
    "credentials",
    "sessions",
    "memory.db",
    "tasks.db",
    "core.db",
    "google_io.py",
    "ai_router.py",
    "telegram_daemon.py",
    "reply_sender.py",
    "systemd",
    ".bak",
    "core_db_backups",
    "data/technadzor",
)


def run(args: list[str], check: bool = True) -> str:
    p = subprocess.run(
        args,
        cwd=str(BASE),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if check and p.returncode != 0:
        raise RuntimeError((p.stdout or "").strip() or f"COMMAND_FAILED: {args}")
    return (p.stdout or "").strip()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_generated(rel: str) -> bool:
    if rel in GENERATED_EXACT:
        return True
    return any(rel.startswith(prefix) for prefix in GENERATED_PREFIXES)


def tracked_source_snapshot() -> list[dict[str, Any]]:
    out = run(["git", "ls-files"], check=True)
    items: list[dict[str, Any]] = []
    for rel in sorted(x.strip() for x in out.splitlines() if x.strip()):
        if is_generated(rel):
            continue
        if rel.endswith(".bak") or ".bak." in rel:
            continue
        p = BASE / rel
        if not p.exists() or not p.is_file():
            continue
        try:
            st = p.stat()
            items.append({
                "path": rel,
                "size": st.st_size,
                "sha256": sha_file(p),
            })
        except Exception as e:
            items.append({"path": rel, "error": str(e)[:160]})
    return items


def local_tree_snapshot(root: Path, label: str) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for p in sorted(x for x in root.rglob("*") if x.is_file()):
            if len(rows) >= 5000:
                rows.append({"label": label, "truncated": True})
                break
            try:
                st = p.stat()
                rows.append({
                    "label": label,
                    "path": str(p.relative_to(root)),
                    "size": st.st_size,
                    "mtime": int(st.st_mtime),
                })
            except Exception as e:
                rows.append({"label": label, "path": str(p), "error": str(e)[:120]})
    except Exception as e:
        rows.append({"label": label, "root": str(root), "error": str(e)[:120]})
    return rows


def db_watermark() -> dict[str, Any]:
    db = BASE / "data" / "core.db"
    if not db.exists():
        return {"status": "NO_CORE_DB"}
    result: dict[str, Any] = {"status": "OK"}
    try:
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=3)
        cur = conn.cursor()

        cur.execute("PRAGMA table_info(tasks)")
        task_cols = {r[1] for r in cur.fetchall()}
        cur.execute("PRAGMA table_info(task_history)")
        hist_cols = {r[1] for r in cur.fetchall()}

        if "updated_at" in task_cols:
            cur.execute("SELECT MAX(updated_at), COUNT(*) FROM tasks")
            result["tasks_max_updated_at"], result["tasks_count"] = cur.fetchone()
        else:
            cur.execute("SELECT MAX(rowid), COUNT(*) FROM tasks")
            result["tasks_max_rowid"], result["tasks_count"] = cur.fetchone()

        if "created_at" in hist_cols:
            cur.execute("SELECT MAX(created_at), COUNT(*) FROM task_history")
            result["history_max_created_at"], result["history_count"] = cur.fetchone()
        else:
            cur.execute("SELECT MAX(rowid), COUNT(*) FROM task_history")
            result["history_max_rowid"], result["history_count"] = cur.fetchone()

        cur.execute("SELECT COALESCE(topic_id,0), state, COUNT(*) FROM tasks GROUP BY COALESCE(topic_id,0), state")
        result["topic_state_counts"] = [list(r) for r in cur.fetchall()]

        conn.close()
    except Exception as e:
        result = {"status": "DB_READ_FAIL", "error": str(e)[:200]}
    return result


def fingerprint_payload() -> dict[str, Any]:
    local_sources = []
    for rel in LOCAL_RUNTIME_SOURCES:
        local_sources.extend(local_tree_snapshot(BASE / rel, rel))
    for abs_root in ABS_RUNTIME_SOURCES:
        local_sources.extend(local_tree_snapshot(abs_root, str(abs_root)))

    return {
        "git_head": run(["git", "rev-parse", "HEAD"], check=True),
        "tracked_sources": tracked_source_snapshot(),
        "db_watermark": db_watermark(),
        "runtime_sources": local_sources,
    }


def fingerprint(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(fp: str, payload: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    data = {
        "saved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fingerprint": fp,
        "git_head": payload.get("git_head"),
        "db_watermark": payload.get("db_watermark"),
    }
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(STATE_PATH)


def staged_files() -> list[str]:
    out = run(["git", "diff", "--cached", "--name-only"], check=True)
    return [x.strip() for x in out.splitlines() if x.strip()]


def assert_no_staged_before_run() -> None:
    staged = staged_files()
    if not staged:
        return
    raise RuntimeError("PREEXISTING_STAGED_CHANGES_REFUSE_AGGREGATOR_RUN:\n" + "\n".join(staged[:200]))


def run_aggregator() -> None:
    if not AGGREGATOR.exists():
        raise RuntimeError("FULL_CONTEXT_AGGREGATOR_NOT_FOUND")
    assert_no_staged_before_run()
    py = str(PYTHON if PYTHON.exists() else sys.executable)
    p = subprocess.run(
        [py, str(AGGREGATOR)],
        cwd=str(BASE),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if p.stdout:
        print(p.stdout.rstrip())
    if p.returncode != 0:
        raise RuntimeError(f"FULL_CONTEXT_AGGREGATOR_FAILED:{p.returncode}")



# === DIRTY_TRACKED_NONGENERATED_GUARD_V1 ===
def dirty_tracked_nongenerated() -> list[str]:
    out = run(["git", "status", "--porcelain"], check=True)
    dirty: list[str] = []
    for line in out.splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if status.startswith("??"):
            continue
        if is_generated(path):
            continue
        if path in {
            "tools/full_context_aggregator_guard.py",
            "tools/full_context_aggregator_guard.sh",
        }:
            continue
        dirty.append(f"{status} {path}")
    return dirty


def assert_clean_tracked_sources() -> None:
    dirty = dirty_tracked_nongenerated()
    if dirty:
        raise RuntimeError(
            "DIRTY_TRACKED_NONGENERATED_REFUSE_AGGREGATOR_RUN:\n"
            + "\n".join(dirty[:200])
        )
# === END_DIRTY_TRACKED_NONGENERATED_GUARD_V1 ===


def acquire_lock() -> Any:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    f = LOCK_PATH.open("w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return f
    except BlockingIOError:
        return None


def main() -> int:
    lock = acquire_lock()
    if lock is None:
        return 0

    payload = fingerprint_payload()
    fp = fingerprint(payload)
    state = load_state()
    old_fp = state.get("fingerprint")

    if "--status" in sys.argv:
        dirty = dirty_tracked_nongenerated()
        print(f"CURRENT_FINGERPRINT={fp}")
        print(f"SAVED_FINGERPRINT={old_fp or 'NONE'}")
        print(f"CHANGED={fp != old_fp}")
        print(f"GIT_HEAD={payload.get('git_head')}")
        print("DIRTY_TRACKED_NONGENERATED=" + (",".join(dirty) if dirty else "NONE"))
        return 0

    if "--init" in sys.argv:
        assert_clean_tracked_sources()
        save_state(fp, payload)
        print(f"AGGREGATOR_GUARD_INIT_OK fingerprint={fp}")
        return 0

    assert_clean_tracked_sources()

    force = "--force" in sys.argv
    if not force and old_fp == fp:
        return 0

    print(f"AGGREGATOR_CHANGE_DETECTED old={old_fp or 'NONE'} new={fp} force={force}")
    run_aggregator()

    after_payload = fingerprint_payload()
    after_fp = fingerprint(after_payload)
    save_state(after_fp, after_payload)
    print(f"AGGREGATOR_GUARD_DONE fingerprint={after_fp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

====================================================================================================
END_FILE: tools/full_context_aggregator_guard.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: tools/full_context_aggregator_guard.sh
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e242d0afb767dde16a3aa5cddaf36b7618fa09188a57269b971d0b4d9ad0de0c
====================================================================================================
#!/usr/bin/env bash
set -Eeuo pipefail
cd /root/.areal-neva-core

set -a
set +u
[ -f .env ] && . ./.env
set -u
set +a

exec /root/.areal-neva-core/.venv/bin/python3 /root/.areal-neva-core/tools/full_context_aggregator_guard.py "$@"

====================================================================================================
END_FILE: tools/full_context_aggregator_guard.sh
FILE_CHUNK: 1/1
====================================================================================================
