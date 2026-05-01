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

def build_file_followup_answer(chat_id: str, topic_id: int, user_text: str, limit: int = 8) -> Optional[str]:
    if not should_handle_file_followup(user_text):
        return None

    topic_id = int(topic_id or 0)
    if topic_id == 0:
        return "В общем топике файлы не смешиваю. Для поиска файла нужен конкретный рабочий топик"

    items = load_file_memory(chat_id, topic_id, user_text, limit=limit)

    if not items:
        return (
            "В этом топике файлов по запросу не найдено\n\n"
            "Могу принять файл заново и определить действие: смета, технадзор, акт, проект, OCR или проверка"
        )

    lines = [
        "Файлы в этом топике уже есть. Нашёл релевантное:",
        "",
    ]

    for i, item in enumerate(items, 1):
        fname = item.get("file_name") or "без имени"
        direction = item.get("direction") or "FILE_GENERAL"
        ts = item.get("timestamp") or ""
        task_id = str(item.get("task_id") or "")[:8]
        links = item.get("links") or []

        lines.append(f"{i}. {fname}")
        lines.append(f"   Тип: {direction}")
        if task_id:
            lines.append(f"   Задача: {task_id}")
        if ts:
            lines.append(f"   Дата: {ts}")

        if links:
            lines.append("   Ссылки:")
            for link in links[:4]:
                lines.append(f"   - {link}")
        else:
            fid = item.get("file_id") or ""
            if fid:
                lines.append(f"   Drive file_id: {fid}")

        summary = _clean(item.get("summary") or "", 260)
        if summary:
            lines.append(f"   Кратко: {summary}")
        lines.append("")

    lines.extend([
        "Что могу сделать с выбранным файлом:",
        "1. составить или пересчитать смету",
        "2. сделать акт технадзора с ГОСТ/СП/СНиП",
        "3. разобрать фото дефектов и оформить замечания",
        "4. извлечь таблицу/OCR",
        "5. использовать как шаблон",
        "6. выдать ссылки на готовые PDF/XLSX/DOCX",
        "",
        "Напиши номер действия или ответь на сообщение с файлом",
    ])

    return "\n".join(lines).strip()

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
