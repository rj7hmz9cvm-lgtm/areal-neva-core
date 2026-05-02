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



def build_file_followup_answer(chat_id: str, topic_id: int, user_text: str, limit: int = 3) -> Optional[str]:
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
