# ORCHESTRA_FULL_CONTEXT_PART_008
generated_at_utc: 2026-05-08T07:30:01.948206+00:00
git_sha_before_commit: f5838bb21bbc9157fcf828d5efebb20ee84beb60
part: 8/17


====================================================================================================
BEGIN_FILE: core/active_dialog_state.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 35e86af58d10e00979f331b0ec69c905597f26583ae97bc756413888989df1a6
====================================================================================================
# === ACTIVE_DIALOG_STATE_V1 ===
# === UNIFIED_CONTEXT_PRIORITY_V1 ===
# === SHORT_CONTROL_SAFE_ROUTER_V1 ===
from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional

BASE = "/root/.areal-neva-core"
MEM_DB = os.path.join(BASE, "data/memory.db")

SHORT_CONTROLS = {
    "да", "ок", "окей", "+", "ага", "делай", "делаем", "дальше", "продолжай",
    "покажи", "скинь", "отбой", "закрывай", "готово", "что дальше", "ну что",
}

def _s(v: Any, limit: int = 4000) -> str:
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        try:
            v = json.dumps(v, ensure_ascii=False)
        except Exception:
            v = str(v)
    return str(v).strip()[:limit]

def clean_voice(text: str) -> str:
    return re.sub(r"^\s*\[VOICE\]\s*", "", text or "", flags=re.I).strip()

def is_short_control(text: str) -> bool:
    t = clean_voice(text).lower().strip(" .,!?:;—-")
    return t in SHORT_CONTROLS or (len(t.split()) <= 3 and any(x in t for x in SHORT_CONTROLS))

def _task_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {k: row[k] for k in row.keys()}

def last_active_task(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        SELECT * FROM tasks
        WHERE chat_id=? AND COALESCE(topic_id,0)=?
          AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id or 0)),
    ).fetchone()
    return _task_row_to_dict(row) if row else None

def last_file_task(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        SELECT * FROM tasks
        WHERE chat_id=? AND COALESCE(topic_id,0)=?
          AND (
            input_type IN ('drive_file','file','document','photo','image')
            OR raw_input LIKE '%file_id%'
            OR raw_input LIKE '%file_name%'
            OR result LIKE '%drive.google%'
            OR result LIKE '%docs.google%'
            OR result LIKE '%.xlsx%'
            OR result LIKE '%.pdf%'
            OR result LIKE '%.docx%'
          )
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id or 0)),
    ).fetchone()
    return _task_row_to_dict(row) if row else None

def _memory_lookup(chat_id: str, topic_id: int, query: str = "") -> str:
    if not os.path.exists(MEM_DB):
        return ""
    q = f"%{query[:40]}%" if query else "%"
    out = []
    try:
        con = sqlite3.connect(MEM_DB)
        rows = con.execute(
            """
            SELECT key, value, timestamp FROM memory
            WHERE chat_id=? AND key LIKE ?
              AND (
                key LIKE ? OR value LIKE ? OR key LIKE ? OR key LIKE ?
              )
            ORDER BY timestamp DESC
            LIMIT 8
            """,
            (
                str(chat_id),
                f"topic_{int(topic_id or 0)}_%",
                "%file%",
                q,
                "%artifact%",
                "%archive%",
            ),
        ).fetchall()
        con.close()
        for k, v, ts in rows:
            out.append(f"{ts} | {k} | {_s(v, 700)}")
    except Exception:
        return ""
    return "\n".join(out)

def build_active_context(conn: sqlite3.Connection, chat_id: str, topic_id: int, user_text: str = "") -> Dict[str, Any]:
    active = last_active_task(conn, chat_id, topic_id)
    last_file = last_file_task(conn, chat_id, topic_id)
    mem = _memory_lookup(chat_id, topic_id, clean_voice(user_text))
    return {
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "user_text": user_text,
        "active_task": active,
        "last_file": last_file,
        "memory": mem,
        "priority": "input -> reply parent -> active task -> last file -> pin -> short memory -> long memory -> archive",
    }

def maybe_handle_active_dialog(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    raw = _s(task["raw_input"] if "raw_input" in task.keys() else "")
    text = clean_voice(raw)
    low = text.lower()

    if not text:
        return None

    # === ACTIVE_DIALOG_SKIP_EXPLICIT_ESTIMATE_CREATE_V1 ===
    create_words = (
        "сделай", "создай", "сформируй", "подготовь", "составь",
        "посчитай", "рассчитай", "выгрузи", "сохрани", "оформи"
    )
    estimate_words = (
        "смет", "расчет", "расчёт", "xlsx", "excel", "эксель",
        "pdf", "ндс", "итог", "объем", "объём", "расценк", "позици"
    )
    followup_words = (
        "я тебе скидывал", "уже скидывал", "где файл", "где смета",
        "что дальше", "дальше то что", "ты сделал", "что мы делали",
        "какие последние", "покажи прошл", "найди прошл", "помнишь"
    )
    if (
        any(w in low for w in create_words)
        and any(w in low for w in estimate_words)
        and not any(w in low for w in followup_words)
    ):
        return None
    # === END_ACTIVE_DIALOG_SKIP_EXPLICIT_ESTIMATE_CREATE_V1 ===

    # === ACTIVE_DIALOG_SKIP_EXPLICIT_PROJECT_CREATE_V1 ===
    project_create_words = (
        "сделай", "делай", "создай", "сформируй", "подготовь", "разработай",
        "оформи", "выгрузи", "сохрани", "нарисуй", "собери"
    )
    project_words = (
        "проект", "кж", "кд", "км", "кмд", "ар",
        "фундамент", "фундаментн", "плита", "плиты", "плиту",
        "армирован", "арматур", "dxf", "dwg", "чертеж", "чертёж", "конструктив"
    )
    if (
        any(w in low for w in project_create_words)
        and any(w in low for w in project_words)
        and not any(w in low for w in followup_words)
    ):
        return None
    # === END_ACTIVE_DIALOG_SKIP_EXPLICIT_PROJECT_CREATE_V1 ===

    file_followup = any(x in low for x in (
        "скидывал файл", "скидывал смету", "какой файл", "что дальше", "дальше то что",
        "покажи файл", "где файл", "где смета", "что с файлом", "по этому файлу",
    ))

    if file_followup:
        try:
            from core.file_memory_bridge import build_file_followup_answer
            ans = build_file_followup_answer(str(chat_id), int(topic_id or 0), raw, limit=8)
            if ans:
                return {
                    "handled": True,
                    "state": "DONE",
                    "result": ans,
                    "event": "ACTIVE_DIALOG_STATE_V1:FILE_FOLLOWUP_DONE",
                }
        except Exception as e:
            return {
                "handled": True,
                "state": "FAILED",
                "result": "",
                "error": f"ACTIVE_DIALOG_FILE_FOLLOWUP_ERR:{e}",
                "event": "ACTIVE_DIALOG_STATE_V1:FILE_FOLLOWUP_FAILED",
            }

    if is_short_control(text):
        ctx = build_active_context(conn, chat_id, topic_id, raw)
        active = ctx.get("active_task")
        last_file = ctx.get("last_file")
        if active:
            res = _s(active.get("result") or active.get("raw_input"), 1200)
            return {
                "handled": True,
                "state": "DONE",
                "result": f"Активный контекст найден\nЗадача: {active.get('id')}\nСтатус: {active.get('state')}\nКратко: {res}",
                "event": "ACTIVE_DIALOG_STATE_V1:SHORT_CONTROL_ACTIVE_TASK",
            }
        if last_file:
            res = _s(last_file.get("result") or last_file.get("raw_input"), 1200)
            return {
                "handled": True,
                "state": "DONE",
                "result": f"Последний файловый контекст найден\nЗадача: {last_file.get('id')}\nСтатус: {last_file.get('state')}\nКратко: {res}",
                "event": "ACTIVE_DIALOG_STATE_V1:SHORT_CONTROL_LAST_FILE",
            }

    return None

def save_dialog_event(chat_id: str, topic_id: int, key: str, value: Any) -> None:
    if not os.path.exists(MEM_DB):
        return
    try:
        con = sqlite3.connect(MEM_DB)
        con.execute(
            "INSERT INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,?)",
            (
                str(chat_id),
                f"topic_{int(topic_id or 0)}_dialog_{key}",
                json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        con.commit()
        con.close()
    except Exception:
        pass
# === END_SHORT_CONTROL_SAFE_ROUTER_V1 ===
# === END_UNIFIED_CONTEXT_PRIORITY_V1 ===
# === END_ACTIVE_DIALOG_STATE_V1 ===

====================================================================================================
END_FILE: core/active_dialog_state.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/archive_distributor.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 27d2d0630d027aeeb85fccc7c64c2907e804ba96faf7eae9be72c49f32230cb8
====================================================================================================
# === ARCHIVE_DISTRIBUTOR_V1 ===
# Читает timeline.jsonl → определяет топик → раскладывает в memory.db
import json, os, re, logging, sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

BASE = Path("/root/.areal-neva-core")
MEM_DB = str(BASE / "data/memory.db")
CHAT_ID = "-1003725299009"

# Сигнатуры топиков по контенту
_TOPIC_SIGNATURES = {
    2:    ["стройк", "смет", "кровл", "фасад", "фундамент", "металлочерепиц", "профнастил",
           "ангар", "бетон", "арматур", "утеплитель", "монтаж", "кж", "ар ", "кд "],
    5:    ["технадзор", "дефект", "акт осмотр", "нарушени", "предписани", "сп ", "гост", "снип",
           "инспекц", "фото дефект"],
    500:  ["найди", "поищи", "цена", "стоимость", "avito", "ozon", "wildberries", "поставщик",
           "купить", "маркет", "ral", "профлист"],
    961:  ["toyota", "hiace", "запчаст", "brembo", "авто", "машин", "vin", "oem", "разборк",
           "двигател", "подвеск"],
    3008: ["код", "python", "патч", "функци", "верификац", "архитектур", "task_worker",
           "telegram_daemon", "оркестр"],
}

def _detect_topic(text: str) -> int:
    low = text.lower()
    scores = {}
    for topic_id, keywords in _TOPIC_SIGNATURES.items():
        scores[topic_id] = sum(1 for kw in keywords if kw in low)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 0  # 0 = общий

def _ensure_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory
        (chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)
    """)

def distribute_timeline(timeline_path: str, chat_id: str = CHAT_ID, dry_run: bool = False) -> dict:
    """
    Читает timeline.jsonl → раскладывает записи в memory.db по топикам.
    Возвращает статистику.
    """
    p = Path(timeline_path)
    if not p.exists():
        return {"ok": False, "reason": "FILE_NOT_FOUND"}

    conn = sqlite3.connect(MEM_DB)
    conn.row_factory = sqlite3.Row
    _ensure_table(conn)

    stats = {"total": 0, "distributed": 0, "skipped": 0, "by_topic": {}}
    seen_keys = set()

    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue

            stats["total"] += 1

            # Собираем текст для классификации
            text_parts = []
            # timeline.jsonl имеет структуру {"timestamp":..., "data": {...}}
            data_block = entry.get("data") or entry
            if isinstance(data_block, dict):
                for field in ["raw_text", "text", "message", "content", "result",
                              "raw_input", "value", "system", "architecture",
                              "pipeline", "memory", "pending", "decisions"]:
                    v = data_block.get(field)
                    if v and isinstance(v, str) and len(v) > 10:
                        text_parts.append(v[:800])
            # тоже проверяем корень
            for field in ["text", "message", "content"]:
                v = entry.get(field)
                if v and isinstance(v, str):
                    text_parts.append(v[:400])
            text = " ".join(text_parts)[:3000]

            if not text or len(text) < 20:
                stats["skipped"] += 1
                continue

            # Определяем топик
            topic_id = _detect_topic(text)

            # Формируем ключ
            ts = entry.get("timestamp") or entry.get("ts") or entry.get("created_at") or "2026"
            ts_short = str(ts)[:10].replace("-", "")
            dedup_key = f"topic_{topic_id}_archive_{ts_short}_{hash(text) % 100000}"

            if dedup_key in seen_keys:
                stats["skipped"] += 1
                continue
            seen_keys.add(dedup_key)

            value = text[:5000]

            if not dry_run:
                # Проверяем нет ли уже такой записи
                existing = conn.execute(
                    "SELECT 1 FROM memory WHERE chat_id=? AND key=?",
                    (chat_id, dedup_key)
                ).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, ?)",
                        (chat_id, dedup_key, value, str(ts)[:19])
                    )

            stats["distributed"] += 1
            stats["by_topic"][topic_id] = stats["by_topic"].get(topic_id, 0) + 1

    if not dry_run:
        conn.commit()
    conn.close()

    return {"ok": True, **stats}

def run_distribution(chat_id: str = CHAT_ID) -> dict:  # CHAT_EXPORTS_POLICY_V1_WIRED
    """Запустить распределение для всех timeline.jsonl чата"""
    results = {}
    chats_dir = BASE / "data/memory_files/CHATS"
    if not chats_dir.exists():
        return {"ok": False, "reason": "NO_CHATS_DIR"}

    for chat_dir in chats_dir.iterdir():
        if not chat_dir.is_dir():
            continue
        timeline = chat_dir / "timeline.jsonl"
        if timeline.exists():
            r = distribute_timeline(str(timeline), chat_id=chat_id)
            results[str(timeline)] = r
            logger.info("ARCHIVE_DISTRIBUTED file=%s stats=%s", timeline, r)

    return {"ok": True, "files": results}

def _load_archive_for_topic(chat_id: str, topic_id: int, user_text: str = "", limit: int = 5) -> str:
    """
    Загрузить архивный контекст для топика из memory.db.
    Используется в _load_archive_context.
    """
    if not os.path.exists(MEM_DB):
        return ""
    conn = sqlite3.connect(MEM_DB)
    conn.row_factory = sqlite3.Row
    try:
        _ensure_table(conn)
        key_pattern = f"topic_{topic_id}_archive_%"
        rows = conn.execute(
            """SELECT key, value FROM memory
               WHERE chat_id=? AND key GLOB ?
               ORDER BY timestamp DESC LIMIT ?""",
            (str(chat_id), key_pattern, limit * 3)
        ).fetchall()

        if not rows:
            return ""

        # Фильтрация по релевантности если есть запрос
        if user_text:
            query_words = set(w for w in user_text.lower().split() if len(w) > 3)
            scored = []
            for row in rows:
                val = str(row["value"]).lower()
                score = sum(1 for w in query_words if w in val)
                scored.append((score, str(row["value"])[:500]))
            scored.sort(reverse=True)
            relevant = [v for s, v in scored if s > 0][:limit]
        else:
            relevant = [str(r["value"])[:500] for r in rows[:limit]]

        return "\n---\n".join(relevant) if relevant else ""
    except Exception as e:
        logger.warning("ARCHIVE_LOAD_ERR topic=%s err=%s", topic_id, e)
        return ""
    finally:
        conn.close()

try:
    from core.chat_exports_policy import get_canonical_exports_dir as _ced
except Exception:
    _ced = None

if __name__ == "__main__":
    print("Running archive distribution...")
    result = run_distribution()
    print(json.dumps(result, ensure_ascii=False, indent=2))
# === END ARCHIVE_DISTRIBUTOR_V1 ===

====================================================================================================
END_FILE: core/archive_distributor.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/archive_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 04fdd1d0f6927a38b62f869f0a020b30b8cc81d798083d607f1a86d3c61c6e1e
====================================================================================================
# === FULLFIX_ARCHIVE_ENGINE_STAGE_6 ===
from __future__ import annotations
import json
import logging
from typing import Any, Dict, Optional

ARCHIVE_ENGINE_VERSION = "ARCHIVE_ENGINE_V1"
logger = logging.getLogger("task_worker")


class ArchiveEngine:
    """
    Stage 6 shadow mode: индексирует завершённую задачу в memory.db.
    Пишет short_summary, direction, engine, quality_gate_overall.
    Не блокирует доставку при ошибках.
    """

    def archive(self, payload: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "task_id":      str(payload.get("task_id") or payload.get("id") or ""),
            "chat_id":      str(payload.get("chat_id") or ""),
            "topic_id":     int(payload.get("topic_id") or 0),
            "direction":    str(payload.get("direction") or "general_chat"),
            "engine":       str(payload.get("engine") or "ai_router"),
            "input_type":   str(payload.get("input_type") or "text"),
            "raw_input":    str(payload.get("raw_input") or payload.get("raw_text") or "")[:300],
            "result_text":  str((result.get("result") or {}).get("text") or result.get("text") or "")[:500],
            "artifact_url": str(result.get("artifact_url") or result.get("drive_link") or ""),
            "qg_overall":   str((result.get("quality_gate_report") or {}).get("overall") or "unknown"),
            "qg_failed":    json.dumps((result.get("quality_gate_report") or {}).get("failed") or []),
            "search_plan":  json.dumps(payload.get("search_plan") or {}),
            "archive_version": ARCHIVE_ENGINE_VERSION,
            "shadow_mode":  True,
        }

        self._write_to_memory_api(record)
        return record

    def _write_to_memory_api(self, record: Dict[str, Any]):
        import urllib.request, urllib.error
        try:
            body = json.dumps(record).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8091/archive",  # PORT_FIX_V1,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=2)
            logger.info("FULLFIX_ARCHIVE_ENGINE_STAGE_6 archived task=%s dir=%s qg=%s",
                        record["task_id"], record["direction"], record["qg_overall"])
        except Exception as e:
            logger.warning("FULLFIX_ARCHIVE_ENGINE_STAGE_6 memory_api unavailable: %s", e)


def archive_task(payload, result):
    return ArchiveEngine().archive(payload, result)
# === END FULLFIX_ARCHIVE_ENGINE_STAGE_6 ===

====================================================================================================
END_FILE: core/archive_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/archive_guard.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 369b05cb9ddf9aaa9f7b05828f3752848557f9e062d44f74b5f5f290723dc64c
====================================================================================================
# === FINAL_CLOSURE_BLOCKER_FIX_V1_ARCHIVE_DUPLICATE_GUARD ===
from __future__ import annotations

import hashlib
import sqlite3
from typing import Any, Dict


def _clean(v) -> str:
    return "" if v is None else str(v).strip()


def content_hash(text: str) -> str:
    return hashlib.sha256(_clean(text).lower().encode("utf-8", "ignore")).hexdigest()


def ensure_archive_guard(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS archive_guard (
            id TEXT PRIMARY KEY,
            task_id TEXT,
            chat_id TEXT,
            topic_id INTEGER DEFAULT 0,
            content_hash TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_archive_guard_hash ON archive_guard(content_hash)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_archive_guard_task ON archive_guard(task_id)")


def should_archive(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, content: str) -> Dict[str, Any]:
    ensure_archive_guard(conn)
    h = content_hash(content)
    row = conn.execute("SELECT task_id, created_at FROM archive_guard WHERE content_hash=? LIMIT 1", (h,)).fetchone()

    if row:
        return {"ok": False, "duplicate": True, "duplicate_task_id": row[0], "hash": h}

    gid = hashlib.sha1(f"{task_id}:{h}".encode()).hexdigest()
    conn.execute(
        "INSERT OR IGNORE INTO archive_guard (id, task_id, chat_id, topic_id, content_hash) VALUES (?,?,?,?,?)",
        (gid, task_id, str(chat_id), int(topic_id or 0), h),
    )
    return {"ok": True, "duplicate": False, "hash": h}


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_ARCHIVE_DUPLICATE_GUARD ===

====================================================================================================
END_FILE: core/archive_guard.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/artifact_pipeline.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 102fd4ccfe0880b0a831991f3fa9b45a968bf34f21d11c04fb785a7ab5f557e3
====================================================================================================
import os
import re
import csv
import json
import base64
import tempfile
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=True)

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

def _kind(file_name: str, mime_type: str = "") -> str:
    # === UNIVERSAL_FORMAT_REGISTRY_V1_KIND ===
    # === DWG_DXF_KIND_FIX_V1_ARTIFACT_PIPELINE ===
    try:
        from core.format_registry import classify_file
        return classify_file(file_name, mime_type).get("kind") or "binary"
    except Exception:
        ext = os.path.splitext((file_name or "").lower())[1]
        mime = (mime_type or "").lower()

        # drawing first: mimetypes may classify .dwg/.dxf as image/*
        if ext in (".dwg", ".dxf", ".ifc", ".rvt", ".rfa", ".skp", ".stl", ".obj", ".step", ".stp", ".iges", ".igs") or any(x in mime for x in ("dxf", "dwg", "ifc", "cad", "step", "stp", "iges", "igs")):
            return "drawing"
        if ext in (".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff", ".bmp", ".gif") or mime.startswith("image/"):
            return "image"
        if ext in (".xlsx", ".xls", ".xlsm", ".csv", ".ods", ".tsv") or "spreadsheet" in mime or mime in ("text/csv", "application/vnd.ms-excel"):
            return "table"
        if ext in (".pdf", ".docx", ".doc", ".txt", ".md", ".rtf", ".odt", ".html", ".htm", ".xml", ".json", ".yaml", ".yml") or mime in ("application/pdf", "text/plain"):
            return "document"
        if ext in (".ppt", ".pptx", ".odp", ".key"):
            return "presentation"
        if ext in (".zip", ".7z", ".rar", ".tar", ".gz", ".tgz"):
            return "archive"
        if ext in (".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".m4a", ".ogg"):
            return "media"
        return "binary"
    # === END_DWG_DXF_KIND_FIX_V1_ARTIFACT_PIPELINE ===
    # === END_UNIVERSAL_FORMAT_REGISTRY_V1_KIND ===


# === DOMAIN_CONTOUR_ROUTER_V1 ===
def _artifact_task_id(file_name: str, engine: str = "artifact") -> str:
    base = re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", os.path.splitext(os.path.basename(file_name or engine))[0]).strip("._")
    return (base or engine)[:80]

def _domain_flags(file_name: str, mime_type: str = "", user_text: str = "", topic_role: str = "") -> Dict[str, bool]:
    hay = f"{file_name}\n{mime_type}\n{user_text}\n{topic_role}".lower()
    estimate = any(x in hay for x in ("смет", "расчёт", "расчет", "вор", "ведомость объем", "ведомость объём", "estimate", "xlsx", "xls", "csv"))
    tech = any(x in hay for x in ("технадзор", "дефект", "акт", "осмотр", "нарушен", "предписан", "гост", "снип", "сп ", "фотофиксац", "трещин", "протеч", "скол"))
    project = any(x in hay for x in ("проект", "проектирован", "кж", "кмд", "км", "кр", "ар", "ов", "вк", "эом", "гп", "пз", "чертеж", "чертёж", "dxf", "dwg"))
    return {"estimate": estimate, "tech": tech, "project": project}


# === ESTIMATE_PDF_PACKAGE_V2 ===
def _pdf_escape_v2(text: str) -> str:
    return str(text or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

def _write_simple_pdf_v2(path: str, title: str, lines: List[str]) -> str:
    out = os.path.join(tempfile.gettempdir(), os.path.splitext(os.path.basename(path))[0] + "_estimate_summary.pdf")
    safe_lines = [_pdf_escape_v2(title or "Estimate summary")]
    safe_lines += [_pdf_escape_v2(x) for x in (lines or [])[:40]]

    stream_lines = ["BT", "/F1 11 Tf", "50 790 Td"]
    first = True
    for line in safe_lines:
        if not first:
            stream_lines.append("0 -16 Td")
        first = False
        stream_lines.append(f"({line[:105]}) Tj")
    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("utf-8", errors="ignore")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{i} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)+1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode())
    pdf.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())

    with open(out, "wb") as f:
        f.write(pdf)
    return out

def _zip_files_v2(files: List[str], name: str) -> str:
    import zipfile
    out = os.path.join(tempfile.gettempdir(), re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", name or "estimate_package").strip("._") + ".zip")
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in files or []:
            if f and os.path.exists(f):
                z.write(f, arcname=os.path.basename(f))
    return out
# === END_ESTIMATE_PDF_PACKAGE_V2 ===

async def _domain_estimate_artifact(local_path: str, file_name: str, mime_type: str, user_text: str, topic_role: str) -> Optional[Dict[str, Any]]:
    # === DOMAIN_ESTIMATE_PDF_XLSX_PACKAGE_V2 ===
    try:
        from core.estimate_engine import process_estimate_to_excel
        tid = _artifact_task_id(file_name, "estimate_artifact")
        res = await process_estimate_to_excel(local_path, tid, 0)

        if res and (res.get("success") or res.get("excel_path")) and res.get("excel_path"):
            excel_path = res.get("excel_path")
            link = res.get("drive_link") or ""
            lines = [
                f"Файл: {file_name}",
                "Engine: DOMAIN_ESTIMATE_ENGINE_V1",
                f"Drive: {link or 'не подтвержден'}",
                f"Status: {'OK' if excel_path else 'PARTIAL'}",
            ]
            if res.get("error"):
                lines.append(f"Ограничение: {res.get('error')}")

            pdf_path = _write_simple_pdf_v2(excel_path or local_path, "Сметный результат", lines)
            package = _zip_files_v2([excel_path, pdf_path], os.path.splitext(os.path.basename(file_name or "estimate"))[0] + "_estimate_package")

            summary = "Сметный файл обработан\nАртефакты: XLSX + PDF"
            if link:
                summary += f"\nExcel: {link}"
            else:
                summary += "\nExcel создан локально, Drive ссылка не подтверждена"
            summary += "\nPDF включён в ZIP пакет"

            return {
                "summary": summary,
                "artifact_path": package,
                "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_estimate_package.zip",
                "engine": "DOMAIN_ESTIMATE_ENGINE_V1",
                "drive_link": link,
                "extra_artifacts": [excel_path, pdf_path],
            }

        reason = (res or {}).get("error") or "ESTIMATE_ENGINE_NO_ARTIFACT"
        pdf_path = _write_simple_pdf_v2(local_path, "Сметный файл принят без расчётного результата", [
            f"Файл: {file_name}",
            f"Причина: {reason}",
            "Расчётные строки не подтверждены",
        ])
        package = _zip_files_v2([pdf_path], os.path.splitext(os.path.basename(file_name or "estimate"))[0] + "_estimate_diagnostic_package")
        return {
            "summary": f"Сметный файл принят, но расчётные строки не подтверждены\nПричина: {reason}\nСоздан диагностический PDF пакет",
            "artifact_path": package,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_estimate_diagnostic_package.zip",
            "engine": "DOMAIN_ESTIMATE_ENGINE_V1",
            "error": str(reason)[:300],
            "extra_artifacts": [pdf_path],
        }
    except Exception as e:
        pdf_path = _write_simple_pdf_v2(local_path, "Сметный engine недоступен", [
            f"Файл: {file_name}",
            f"Ошибка: {e}",
            "Расчётные строки не подтверждены",
        ])
        package = _zip_files_v2([pdf_path], os.path.splitext(os.path.basename(file_name or "estimate"))[0] + "_estimate_error_package")
        return {
            "summary": f"Сметный engine недоступен: {e}\nСоздан диагностический PDF пакет",
            "artifact_path": package,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_estimate_error_package.zip",
            "engine": "DOMAIN_ESTIMATE_ENGINE_V1",
            "error": str(e)[:300],
            "extra_artifacts": [pdf_path],
        }
    # === END_DOMAIN_ESTIMATE_PDF_XLSX_PACKAGE_V2 ===

async def _domain_technadzor_artifact(local_path: str, file_name: str, mime_type: str, user_text: str, topic_role: str, extracted_text: str = "") -> Optional[Dict[str, Any]]:
    try:
        from core.technadzor_engine import process_technadzor
        tid = _artifact_task_id(file_name, "technadzor_artifact")
        raw = "\n".join(x for x in [user_text or "", extracted_text or "", topic_role or ""] if x).strip()
        res = process_technadzor(
            conn=None,
            task_id=tid,
            chat_id="artifact_pipeline",
            topic_id=0,
            raw_input=raw or "Технический осмотр файла",
            file_name=file_name,
            local_path=local_path,
        )
        if res and res.get("ok"):
            art = res.get("artifact") or {}
            path = art.get("path") or ""
            link = art.get("drive_link") or ""
            summary = _clean(res.get("result_text") or "Акт технического осмотра сформирован", 6000)
            if link and link not in summary:
                summary += f"\n\nДокумент: {link}"
            return {
                "summary": summary,
                "artifact_path": path,
                "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_technadzor_act.docx",
                "engine": "DOMAIN_TECHNADZOR_ENGINE_V1",
                "drive_link": link,
            }
    except Exception as e:
        return {
            "summary": f"Технадзор engine недоступен: {e}",
            "artifact_path": "",
            "artifact_name": "",
            "engine": "DOMAIN_TECHNADZOR_ENGINE_V1",
            "error": str(e)[:300],
        }
    return None

async def _domain_project_document_artifact(local_path: str, file_name: str, mime_type: str, user_text: str, topic_role: str) -> Optional[Dict[str, Any]]:
    try:
        from core.project_document_engine import process_project_document
        tid = _artifact_task_id(file_name, "project_document")
        res = await process_project_document(
            file_path=local_path,
            file_name=file_name,
            user_text=user_text,
            topic_role=topic_role,
            task_id=tid,
            topic_id=0,
        )
        if res and res.get("success"):
            return {
                "summary": _clean(res.get("summary") or "Проектный документ обработан", 6000),
                "artifact_path": res.get("artifact_path"),
                "artifact_name": res.get("artifact_name") or f"{os.path.splitext(os.path.basename(file_name))[0]}_project_document_package.zip",
                "extra_artifacts": res.get("extra_artifacts") or [],
                "engine": "PROJECT_DOCUMENT_ENGINE_V1",
                "model": res.get("model") or {},
            }
    except Exception as e:
        return {
            "summary": f"Project document engine недоступен: {e}",
            "artifact_path": "",
            "artifact_name": "",
            "engine": "PROJECT_DOCUMENT_ENGINE_V1",
            "error": str(e)[:300],
        }
    return None
# === END_DOMAIN_CONTOUR_ROUTER_V1 ===

def _build_word(title: str, summary: str, defects: List[Dict[str, Any]], recommendations: List[str], sources: List[str]) -> str:
    from docx import Document

    fd, out = tempfile.mkstemp(prefix="artifact_", suffix=".docx", dir="/tmp")
    os.close(fd)

    doc = Document()
    doc.add_heading(title or "Результат обработки", level=1)

    if summary:
        doc.add_paragraph(_clean(summary, 12000))

    if sources:
        doc.add_heading("Источники", level=2)
        for s in sources:
            doc.add_paragraph(_s(s))

    doc.add_heading("Замечания", level=2)
    if defects:
        for idx, item in enumerate(defects, 1):
            p = doc.add_paragraph()
            p.add_run(f"{idx}. ").bold = True
            p.add_run(_s(item.get("title")) or "Замечание")
            sev = _s(item.get("severity"))
            if sev:
                p.add_run(f" [{sev}]")
            desc = _s(item.get("description"))
            if desc:
                doc.add_paragraph(desc)
    else:
        doc.add_paragraph("Замечания не выделены")

    doc.add_heading("Рекомендации", level=2)
    if recommendations:
        for r in recommendations:
            doc.add_paragraph(_s(r))
    else:
        doc.add_paragraph("Рекомендации не сформированы")

    doc.save(out)
    return out

def _build_excel(title: str, items: List[Dict[str, str]], summary: str, sources: List[str]) -> str:
    from openpyxl import Workbook

    fd, out = tempfile.mkstemp(prefix="artifact_", suffix=".xlsx", dir="/tmp")
    os.close(fd)

    wb = Workbook()
    ws = wb.active
    ws.title = "Результат"
    ws["A1"] = title or "Табличный результат"
    ws["A2"] = _clean(summary, 1000)

    row = 4
    headers = ["№", "Наименование", "Ед", "Кол-во", "Примечание"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=row, column=col, value=h)
    row += 1

    for idx, item in enumerate(items, 1):
        ws.cell(row=row, column=1, value=idx)
        ws.cell(row=row, column=2, value=_s(item.get("name")))
        ws.cell(row=row, column=3, value=_s(item.get("unit")))
        ws.cell(row=row, column=4, value=_s(item.get("qty")))
        ws.cell(row=row, column=5, value=_s(item.get("note")))
        row += 1

    src = wb.create_sheet("Источники")
    for idx, s in enumerate(sources, 1):
        src.cell(row=idx, column=1, value=_s(s))

    wb.save(out)
    return out

def _extract_pdf(path: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        parts = []
        for page in reader.pages:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                pass
        return _clean("\n".join(parts), 12000)
    except Exception as e:
        return f"PDF_PARSE_ERROR: {e}"

def _extract_docx(path: str) -> str:
    try:
        from docx import Document
        doc = Document(path)
        return _clean("\n".join(p.text for p in doc.paragraphs if p.text), 12000)
    except Exception as e:
        return f"DOCX_PARSE_ERROR: {e}"

def _extract_txt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return _clean(f.read(), 12000)
    except Exception as e:
        return f"TXT_PARSE_ERROR: {e}"

def _extract_table_items(path: str, file_name: str) -> List[Dict[str, str]]:
    rows: List[List[str]] = []
    ext = os.path.splitext((file_name or "").lower())[1]

    try:
        if ext == ".csv":
            with open(path, "r", encoding="utf-8", errors="ignore", newline="") as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    rows.append([_s(x) for x in row])
                    if idx >= 300:
                        break
        else:
            from openpyxl import load_workbook
            wb = load_workbook(path, data_only=True, read_only=True)
            for ws in wb.worksheets[:3]:
                rows.append([f"__SHEET__:{ws.title}"])
                for idx, row in enumerate(ws.iter_rows(values_only=True)):
                    rows.append([_s(x) for x in row])
                    if idx >= 300:
                        break
    except Exception as e:
        rows.append([f"TABLE_PARSE_ERROR: {e}"])

    items: List[Dict[str, str]] = []
    unit_re = re.compile(r"\b(м2|м3|м\.п\.|п\.м\.|шт|кг|тн|т|м)\b", re.I)
    qty_re = re.compile(r"^\d+[.,]?\d*$")

    for row in rows:
        if not row:
            continue
        if len(row) == 1 and _s(row[0]).startswith("__SHEET__:"):
            continue

        cleaned = [_s(x) for x in row if _s(x)]
        if not cleaned:
            continue

        name = cleaned[0]
        unit = ""
        qty = ""
        note = ""

        for cell in cleaned[1:]:
            if not unit:
                m = unit_re.search(cell)
                if m:
                    unit = m.group(1)
                    continue
            if not qty and qty_re.match(cell.replace(" ", "")):
                qty = cell.replace(" ", "")
                continue
            note = (note + " | " + cell).strip(" |") if note else cell

        if len(name) < 2:
            continue

        items.append({
            "name": name[:500],
            "unit": unit[:32],
            "qty": qty[:64],
            "note": note[:500],
        })

        if len(items) >= 500:
            break

    return items

async def _vision_image(path: str, user_text: str, topic_role: str) -> Optional[Dict[str, Any]]:
    api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        return None

    base_url = (os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip().rstrip("/")
    model = (os.getenv("OPENROUTER_VISION_MODEL") or "google/gemini-2.5-flash").strip()

    ext = os.path.splitext(path)[1].lower().lstrip(".") or "jpeg"
    mime = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"

    try:
        import httpx
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        prompt = (
            "Ты анализируешь строительную фотофиксацию\n"
            f"Роль чата: {topic_role or 'технадзор'}\n"
            f"Задача пользователя: {user_text or 'проанализируй фото'}\n\n"
            "Верни только JSON вида:\n"
            "{\n"
            '  "summary": "краткое резюме",\n'
            '  "defects": [{"title":"...", "description":"...", "severity":"low|medium|high"}],\n'
            '  "recommendations": ["...", "..."]\n'
            "}"
        )

        body = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    ],
                }
            ],
            "temperature": 0.1,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=30.0)) as client:
            r = await client.post(f"{base_url}/chat/completions", headers=headers, json=body)
            r.raise_for_status()
            data = r.json()

        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in content)
        content = _clean(_s(content), 12000)

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {
                "summary": content[:3000],
                "defects": [],
                "recommendations": [],
            }

    except Exception:
        return None

    return None

async def analyze_downloaded_file(local_path: str, file_name: str, mime_type: str = "", user_text: str = "", topic_role: str = "") -> Optional[Dict[str, Any]]:
    kind = _kind(file_name, mime_type)
    sources = [file_name]

    if kind == "image":
        # === OCR_TABLE_TO_EXCEL_FULL_CLOSE_V1_ROUTE ===
        try:
            _ocr_hay = f"{file_name} {mime_type} {user_text} {topic_role}".lower()
            if any(_x in _ocr_hay for _x in ("смет", "таблиц", "вор", "excel", "xlsx", "расчет", "расчёт")):
                from core.ocr_table_engine import image_table_to_excel
                _ocr = await image_table_to_excel(local_path, _artifact_task_id(file_name, "ocr_table"), user_text, 0)
                if _ocr and _ocr.get("success"):
                    return {
                        "summary": _clean(_ocr.get("summary") or "Фото таблицы распознано", 4000),
                        "artifact_path": _ocr.get("artifact_path"),
                        "artifact_name": _ocr.get("artifact_name") or f"{os.path.splitext(os.path.basename(file_name))[0]}_ocr_table_package.zip",
                        "extra_artifacts": _ocr.get("extra_artifacts") or [],
                        "engine": "OCR_TABLE_TO_EXCEL_FULL_CLOSE_V1",
                        "model": {"rows": _ocr.get("rows") or []},
                    }
        except Exception as _ocr_e:
            import logging as _ocr_log
            _ocr_log.getLogger(__name__).warning("OCR_TABLE_TO_EXCEL_FULL_CLOSE_V1_ROUTE_ERR %s", _ocr_e)
        # === END_OCR_TABLE_TO_EXCEL_FULL_CLOSE_V1_ROUTE ===
        # === DOMAIN_TECHNADZOR_IMAGE_ASYNC_VISION_V2 ===
        flags = _domain_flags(file_name, mime_type, user_text, topic_role)
        vision_text = ""
        analysis = None

        if flags.get("tech") or not flags.get("estimate"):
            analysis = await _vision_image(local_path, user_text, topic_role)
            if isinstance(analysis, dict):
                vision_text = json.dumps(analysis, ensure_ascii=False)
            elif analysis:
                vision_text = str(analysis)

            routed = await _domain_technadzor_artifact(local_path, file_name, mime_type, user_text, topic_role, vision_text)
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                routed["engine"] = routed.get("engine") or "DOMAIN_TECHNADZOR_IMAGE_ASYNC_VISION_V2"
                return routed

        if analysis is None:
            analysis = await _vision_image(local_path, user_text, topic_role)

        if not analysis:
            routed = await _domain_technadzor_artifact(local_path, file_name, mime_type, user_text, topic_role, "Фото принято без vision-анализа")
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                return routed
            return None

        summary = _s(analysis.get("summary")) if isinstance(analysis, dict) else _s(analysis)
        summary = summary or "Фото проанализировано"
        defects = analysis.get("defects") if isinstance(analysis, dict) and isinstance(analysis.get("defects"), list) else []
        recommendations = analysis.get("recommendations") if isinstance(analysis, dict) and isinstance(analysis.get("recommendations"), list) else []
        artifact_path = _build_word("Акт замечаний по фотофиксации", summary, defects, [_s(x) for x in recommendations], sources)
        return {
            "summary": summary,
            "artifact_path": artifact_path,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_photo_report.docx",
            "engine": "DOMAIN_TECHNADZOR_IMAGE_ASYNC_VISION_V2",
        }
        # === END_DOMAIN_TECHNADZOR_IMAGE_ASYNC_VISION_V2 ===

    if kind == "table":
        flags = _domain_flags(file_name, mime_type, user_text, topic_role)
        if flags.get("estimate") or not flags.get("project"):
            routed = await _domain_estimate_artifact(local_path, file_name, mime_type, user_text, topic_role)
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                return routed

        items = _extract_table_items(local_path, file_name)
        summary = f"Нормализовано позиций: {len(items)}"
        artifact_path = _build_excel("Сметный/табличный результат", items, summary, sources)
        return {
            "summary": summary,
            "artifact_path": artifact_path,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_estimate.xlsx",
            "engine": "TABLE_FALLBACK_ENGINE",
        }

    if kind == "drawing":
        try:
            from core.dwg_engine import process_drawing_file
            data = process_drawing_file(
                local_path=local_path,
                file_name=file_name,
                mime_type=mime_type,
                user_text=user_text,
                topic_role=topic_role,
                task_id="artifact",
                topic_id=0,
            )
            if data and data.get("success"):
                return {
                    "summary": _clean(data.get("summary") or "DWG/DXF файл обработан", 4000),
                    "artifact_path": data.get("artifact_path"),
                    "artifact_name": data.get("artifact_name") or f"{os.path.splitext(os.path.basename(file_name))[0]}_dwg_dxf_project_package.zip",
                    "extra_artifacts": data.get("extra_artifacts") or [],
                    "engine": "DWG_DXF_PROJECT_CLOSE_V1",
                    "model": data.get("model") or {},
                }
            return {
                "summary": _clean((data or {}).get("summary") or (data or {}).get("error") or "DWG/DXF файл не обработан", 3000),
                "artifact_path": "",
                "artifact_name": "",
                "engine": "DWG_DXF_PROJECT_CLOSE_V1",
                "error": (data or {}).get("error") or "DRAWING_PROCESS_FAILED",
            }
        except Exception as e:
            return {
                "summary": f"DWG/DXF обработка завершилась ошибкой: {e}",
                "artifact_path": "",
                "artifact_name": "",
                "engine": "DWG_DXF_PROJECT_CLOSE_V1",
                "error": str(e)[:300],
            }

    if kind == "document":
        flags = _domain_flags(file_name, mime_type, user_text, topic_role)
        ext = os.path.splitext((file_name or "").lower())[1]
        if ext == ".pdf":
            domain_text = _extract_pdf(local_path)
        elif ext == ".docx":
            domain_text = _extract_docx(local_path)
        else:
            domain_text = _extract_txt(local_path)

        if flags.get("tech"):
            routed = await _domain_technadzor_artifact(local_path, file_name, mime_type, user_text, topic_role, domain_text)
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                return routed

        if flags.get("estimate"):
            routed = await _domain_estimate_artifact(local_path, file_name, mime_type, user_text, topic_role)
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                return routed

        if flags.get("project"):
            routed = await _domain_project_document_artifact(local_path, file_name, mime_type, user_text, topic_role)
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                return routed

        summary = _clean(domain_text, 3000) if domain_text else "Документ обработан"
        artifact_path = _build_word("Сводка по документу", summary, [], [], sources)
        return {
            "summary": summary,
            "artifact_path": artifact_path,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_document_summary.docx",
            "engine": "DOCUMENT_FALLBACK_ENGINE",
        }

    # === UNIVERSAL_FILE_ENGINE_FALLBACK_V1 ===
    try:
        from core.universal_file_engine import process_universal_file
        data = process_universal_file(
            local_path=local_path,
            file_name=file_name,
            mime_type=mime_type,
            user_text=user_text,
            topic_role=topic_role,
            task_id=_artifact_task_id(file_name, "universal_file"),
            topic_id=0,
        )
        if data and data.get("success"):
            return {
                "summary": _clean(data.get("summary") or "Файл обработан универсальным контуром", 6000),
                "artifact_path": data.get("artifact_path"),
                "artifact_name": data.get("artifact_name") or f"{os.path.splitext(os.path.basename(file_name))[0]}_universal_file_package.zip",
                "extra_artifacts": data.get("extra_artifacts") or [],
                "engine": "UNIVERSAL_FILE_ENGINE_V1",
                "model": data.get("model") or {},
            }
    except Exception as e:
        return {
            "summary": f"Универсальный файловый контур завершился ошибкой: {e}",
            "artifact_path": "",
            "artifact_name": "",
            "engine": "UNIVERSAL_FILE_ENGINE_V1",
            "error": str(e)[:300],
        }
    return None
    # === END_UNIVERSAL_FILE_ENGINE_FALLBACK_V1 ===

# === FIX_DOMAIN_FLAGS_TOPIC_ROLE_ESTIMATE_BLEED_V1 ===
# topic_role for topic_2 = "Топик: СТРОЙКА | Направление: estimates"
# The word "estimate" in topic_role made estimate=True for EVERY file in topic_2.
# Fix: classify estimate only from file_name, mime_type, user_text — not topic_role.
_fdf_orig_domain_flags = _domain_flags

def _domain_flags(file_name: str, mime_type: str = "", user_text: str = "", topic_role: str = "") -> Dict[str, bool]:
    hay_no_role = f"{file_name}\n{mime_type}\n{user_text}".lower()
    estimate = any(x in hay_no_role for x in (
        "смет", "расчёт", "расчет", "вор", "ведомость объем", "ведомость объём",
        "estimate", "xlsx", "xls", "csv"
    ))
    orig = _fdf_orig_domain_flags(file_name, mime_type, user_text, topic_role)
    return {"estimate": estimate, "tech": orig["tech"], "project": orig["project"]}
# === END_FIX_DOMAIN_FLAGS_TOPIC_ROLE_ESTIMATE_BLEED_V1 ===

====================================================================================================
END_FILE: core/artifact_pipeline.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/artifact_upload_guard.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 3cf8290fd123e4a629b65742f93811b6a157d1d05bb63ad6532d3f931bf43b48
====================================================================================================
# === FULLFIX_14_ARTIFACT_UPLOAD_GUARD ===
# === UPLOAD_RETRY_QUEUE_UNIFICATION_V1 ===
# === HEAVY_FILE_STORAGE_POLICY_V1 ===
from __future__ import annotations
import logging
import os
import sqlite3
from typing import Any, Dict

logger = logging.getLogger(__name__)
_DB = "/root/.areal-neva-core/data/core.db"

def _ensure_retry_table(conn: sqlite3.Connection) -> None:
    conn.execute("""CREATE TABLE IF NOT EXISTS upload_retry_queue(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT, task_id TEXT, topic_id INTEGER, kind TEXT,
        attempts INTEGER DEFAULT 0, last_error TEXT,
        created_at TEXT DEFAULT (datetime('now')), last_attempt TEXT
    )""")

def _queue_retry(path: str, task_id: str, topic_id: int, kind: str, error: str) -> None:
    try:
        with sqlite3.connect(_DB, timeout=10) as c:
            _ensure_retry_table(c)
            c.execute(
                "INSERT INTO upload_retry_queue(path,task_id,topic_id,kind,last_error) VALUES(?,?,?,?,?)",
                (str(path), str(task_id), int(topic_id or 0), str(kind or "artifact"), str(error)),
            )
            try:
                c.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (str(task_id), f"UPLOAD_RETRY_QUEUE_UNIFICATION_V1:QUEUED:{kind}"),
                )
            except Exception:
                pass
            c.commit()
    except Exception as e:
        logger.warning("UPLOAD_RETRY_QUEUE_UNIFICATION_V1_ERR task=%s err=%s", task_id, e)

def _cleanup_heavy(path: str, link: str = "") -> bool:
    try:
        p = str(path or "")
        if not p or not os.path.exists(p):
            return False
        size = os.path.getsize(p)
        is_tmp = p.startswith("/tmp/") or p.startswith("/var/tmp/") or "/runtime/" in p
        if size >= 20 * 1024 * 1024 and is_tmp:
            os.remove(p)
            logger.info("HEAVY_FILE_STORAGE_POLICY_V1_CLEANED path=%s link=%s", p, link)
            return True
    except Exception as e:
        logger.warning("HEAVY_FILE_STORAGE_POLICY_V1_CLEAN_ERR path=%s err=%s", path, e)
    return False

def upload_or_fail(path: str, task_id: str, topic_id: int, kind: str = "artifact") -> Dict[str, Any]:
    if not path or not os.path.exists(str(path)):
        _queue_retry(path, task_id, topic_id, kind, "FILE_NOT_FOUND")
        return {"success": False, "error": "FILE_NOT_FOUND", "path": path, "queued": True}
    size = os.path.getsize(str(path))
    if size < 10:
        _queue_retry(path, task_id, topic_id, kind, "FILE_TOO_SMALL")
        return {"success": False, "error": "FILE_TOO_SMALL", "path": path, "size": size, "queued": True}
    tried = []
    try:
        from core.engine_base import upload_artifact_to_drive
        link = upload_artifact_to_drive(str(path), str(task_id), int(topic_id or 0))
        if link and str(link).startswith("http"):
            _cleanup_heavy(path, link)
            return {"success": True, "link": str(link), "drive_link": str(link),
                    "path": str(path), "kind": kind, "queued": False}
        tried.append("drive:no_link")
    except Exception as e:
        tried.append(f"drive:{e}")
    _queue_retry(path, task_id, topic_id, kind, "DRIVE_UPLOAD_FAILED")
    try:
        from core.engine_base import _telegram_fallback_send
        tg = _telegram_fallback_send(str(path), str(task_id), int(topic_id or 0))
        if tg:
            _cleanup_heavy(path, tg)
            return {"success": True, "link": str(tg), "telegram_link": str(tg),
                    "path": str(path), "kind": kind, "drive_failed": True,
                    "telegram_fallback": True, "queued": True}
    except Exception as e:
        tried.append(f"telegram:{e}")
    return {"success": False, "error": "UPLOAD_FAILED", "path": str(path),
            "size": size, "tried": tried, "queued": True}

def upload_many_or_fail(files, task_id: str, topic_id: int) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    links: Dict[str, str] = {}
    all_ok = True
    for f in files or []:
        if isinstance(f, str):
            path, kind = f, "artifact"
        elif isinstance(f, dict):
            path = f.get("path") or f.get("file") or f.get("artifact_path") or ""
            kind = f.get("kind") or "artifact"
        else:
            path, kind = str(f or ""), "artifact"
        r = upload_or_fail(str(path), str(task_id), int(topic_id or 0), str(kind))
        results[str(path)] = r
        if not (isinstance(r, dict) and r.get("success")):
            all_ok = False
        if isinstance(r, dict):
            link = str(r.get("link") or r.get("drive_link") or r.get("telegram_link") or "")
            if link:
                links[str(path)] = link
    return {"success": all_ok, "results": results, "links": links,
            "queued": any(isinstance(v, dict) and v.get("queued") for v in results.values())}
# === END_HEAVY_FILE_STORAGE_POLICY_V1 ===
# === END_UPLOAD_RETRY_QUEUE_UNIFICATION_V1 ===
# === END FULLFIX_14_ARTIFACT_UPLOAD_GUARD ===

====================================================================================================
END_FILE: core/artifact_upload_guard.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/audit_log.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 46ff0af7219a7e5548d4d189ecadce73909cb9ff63c0e3c64ea62933fa1976b3
====================================================================================================
# === AUDIT_LOG_V1 ===
import os, json, logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "audit.jsonl")

def audit(event: str, task_id: str = "", chat_id: str = "", details: dict = None):
    """Записать аудит-событие"""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "task_id": task_id,
        "chat_id": str(chat_id),
        "details": details or {},
    }
    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning("AUDIT_LOG_WRITE_ERR %s", e)

def tail_audit(n: int = 20) -> list:
    """Последние n записей аудита"""
    try:
        with open(_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [json.loads(l) for l in lines[-n:] if l.strip()]
    except Exception:
        return []
# === END AUDIT_LOG_V1 ===

====================================================================================================
END_FILE: core/audit_log.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/cad_project_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 6024e82541f8e08b15909858aa28306a471adeffab216b8fc3b23b819b273edc
====================================================================================================
# === FULLFIX_07_CAD_PROJECT_DOCUMENTATION_CLOSURE ===
import os
import re
import json
import math
import glob
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE = "/root/.areal-neva-core"
TEMPLATE_DIR = f"{BASE}/data/project_templates"

ENGINE = "FULLFIX_07_CAD_PROJECT_DOCUMENTATION_CLOSURE"

DEFAULT_FOUNDATION_SHEETS = [
    {"mark": "КЖ", "number": "0", "title": "Титульный лист"},
    {"mark": "КЖ", "number": "1", "title": "Общие данные"},
    {"mark": "КЖ", "number": "2", "title": "Ведомость листов"},
    {"mark": "КЖ", "number": "3", "title": "План фундаментной плиты"},
    {"mark": "КЖ", "number": "4", "title": "Разрез 1-1"},
    {"mark": "КЖ", "number": "5", "title": "Схема нижнего армирования"},
    {"mark": "КЖ", "number": "6", "title": "Схема верхнего армирования"},
    {"mark": "КЖ", "number": "7", "title": "Узлы и детали"},
    {"mark": "КЖ", "number": "8", "title": "Спецификация материалов"},
    {"mark": "КЖ", "number": "9", "title": "Ведомость расхода стали"},
]

DEFAULT_ROOF_SHEETS = [
    {"mark": "КД", "number": "0", "title": "Титульный лист"},
    {"mark": "КД", "number": "1", "title": "Общие данные"},
    {"mark": "КД", "number": "2", "title": "Ведомость листов"},
    {"mark": "КД", "number": "3", "title": "План кровли"},
    {"mark": "КД", "number": "4", "title": "План стропильной системы"},
    {"mark": "КД", "number": "5", "title": "Разрезы"},
    {"mark": "КД", "number": "6", "title": "Узлы кровли"},
    {"mark": "КД", "number": "7", "title": "Спецификация древесины"},
    {"mark": "КД", "number": "8", "title": "Спецификация крепежа"},
]

NORMATIVE_NOTES = [
    "СП 63.13330.2018 Бетонные и железобетонные конструкции",
    "СП 20.13330.2016 Нагрузки и воздействия",
    "ГОСТ 21.501-2018 Правила выполнения рабочей документации архитектурных и конструктивных решений",
    "ГОСТ 21.101-2020 Основные требования к проектной и рабочей документации",
    "ГОСТ 34028-2016 Прокат арматурный для железобетонных конструкций",
]

REBAR_WEIGHT_KG_M = {
    6: 0.222,
    8: 0.395,
    10: 0.617,
    12: 0.888,
    14: 1.21,
    16: 1.58,
    18: 2.00,
    20: 2.47,
    22: 2.98,
    25: 3.85,
}

def _clean(v: Any, limit: int = 10000) -> str:
    return str(v or "").replace("\x00", " ").strip()[:limit]

def _safe_name(v: Any) -> str:
    s = re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", _clean(v, 80))
    return s.strip("_") or "project"

def _font_name() -> str:
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
        for path in candidates:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont("ArealSans", path))
                return "ArealSans"
    except Exception:
        pass
    return "Helvetica"

def _load_templates() -> List[Dict[str, Any]]:
    out = []
    for p in sorted(glob.glob(f"{TEMPLATE_DIR}/PROJECT_TEMPLATE_MODEL__*.json"), key=os.path.getmtime, reverse=True):
        try:
            data = json.loads(Path(p).read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data["template_file"] = p
                out.append(data)
        except Exception:
            pass
    return out

def _choose_template(section: str, topic_id: int = 0) -> Dict[str, Any]:
    templates = _load_templates()
    if not templates:
        return {}
    section = _clean(section).upper()
    for tpl in templates:
        if topic_id and int(tpl.get("topic_id", 0) or 0) == int(topic_id) and _clean(tpl.get("project_type")).upper() == section:
            return tpl
    for tpl in templates:
        if _clean(tpl.get("project_type")).upper() == section:
            return tpl
    return templates[0]

def _num(text: str, default: float) -> float:
    try:
        return float(str(text).replace(",", "."))
    except Exception:
        return default

def _parse_mm(text: str, patterns: List[str], default: int) -> int:
    low = text.lower()
    for pat in patterns:
        m = re.search(pat, low, re.I)
        if m:
            return int(float(m.group(1).replace(",", ".")))
    return default

def parse_project_request(raw_input: str, template_hint: str = "") -> Dict[str, Any]:
    text = _clean(raw_input + " " + template_hint, 6000)
    low = text.lower()

    section = "КЖ"
    project_kind = "foundation_slab"
    if any(x in low for x in ["кров", "строп", "кд"]):
        section = "КД"
        project_kind = "roof"
    if any(x in low for x in [" ар ", "ар.", "архитект", "планиров", "фасад"]):  # SECTION_DETECTION_FIX_V1
        section = "АР"
        project_kind = "architectural"

    length_m = 10.0
    width_m = 10.0
    m = re.search(r"(\d+(?:[,.]\d+)?)\s*[xх×]\s*(\d+(?:[,.]\d+)?)\s*(?:м|m)?", low)
    if m:
        length_m = _num(m.group(1), 10.0)
        width_m = _num(m.group(2), 10.0)

    slab_mm = _parse_mm(low, [
        r"толщин[аы]?\D{0,30}(\d{2,4})\s*мм",
        r"плит[аы]?\D{0,30}(\d{2,4})\s*мм",
        r"бетон\D{0,30}(\d{2,4})\s*мм",
    ], 250)

    sand_mm = _parse_mm(low, [
        r"песчан\D{0,30}(\d{2,4})\s*мм",
        r"песок\D{0,30}(\d{2,4})\s*мм",
    ], 300)

    gravel_mm = _parse_mm(low, [
        r"щеб[её]н\D{0,30}(\d{2,4})\s*мм",
        r"щебень\D{0,30}(\d{2,4})\s*мм",
        r"основан\D{0,30}(\d{2,4})\s*мм",
    ], 150)

    rebar_step_mm = _parse_mm(low, [
        r"шаг\D{0,30}(\d{2,4})\s*мм",
        r"арматур\D{0,40}(\d{2,4})\s*мм",
    ], 200)

    rebar_diam_mm = 12
    md = re.search(r"(?:ø|ф|d|диаметр)\s*(\d{1,2})", low, re.I)
    if md:
        rebar_diam_mm = int(md.group(1))
    else:
        md = re.search(r"арматур[аы]?\D{0,30}(\d{1,2})(?!\d)", low, re.I)
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

    return {
        "project_name": "Проект фундаментной плиты" if project_kind == "foundation_slab" else "Проект по образцу",
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

def _normalize_sheet_register(template: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, str]]:
    section = data.get("section") or "КЖ"
    raw = template.get("sheet_register") or []
    sheets: List[Dict[str, str]] = []
    seen = set()

    for i, sh in enumerate(raw, 1):
        if isinstance(sh, dict):
            title = _clean(sh.get("title") or sh.get("name") or sh.get("sheet") or "", 120)
            number = _clean(sh.get("number") or sh.get("num") or str(i), 20)
            mark = _clean(sh.get("mark") or section, 20)
        else:
            title = _clean(sh, 120)
            number = str(i)
            mark = section
        if not title:
            continue
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        sheets.append({"mark": mark, "number": number, "title": title})

    sections = template.get("sections") or []
    if len(sheets) < 6 and sections:
        keys = ["общие", "ведомость", "план", "разрез", "армир", "спецификац", "узел", "фасад", "схема"]
        for sec in sections:
            title = _clean(sec, 120)
            if not title:
                continue
            low = title.lower()
            if not any(k in low for k in keys):
                continue
            if low in seen:
                continue
            seen.add(low)
            sheets.append({"mark": section, "number": str(len(sheets) + 1), "title": title})
            if len(sheets) >= 12:
                break

    base = DEFAULT_ROOF_SHEETS if data.get("project_kind") == "roof" else DEFAULT_FOUNDATION_SHEETS
    for sh in base:
        low = sh["title"].lower()
        if low not in seen:
            sheets.append({"mark": section, "number": str(len(sheets)), "title": sh["title"]})
            seen.add(low)

    fixed = []
    for idx, sh in enumerate(sheets[:20], 1):
        title = _clean(sh.get("title"), 120)
        mark = _clean(sh.get("mark"), 20) or section
        num = _clean(sh.get("number"), 20) or str(idx)
        fixed.append({"mark": mark, "number": num, "title": title})
    return fixed

def _calc_foundation(data: Dict[str, Any]) -> Dict[str, Any]:
    L = float(data["length_m"])
    W = float(data["width_m"])
    area = L * W
    slab_m = data["slab_mm"] / 1000.0
    sand_m = data["sand_mm"] / 1000.0
    gravel_m = data["gravel_mm"] / 1000.0
    step_m = data["rebar_step_mm"] / 1000.0
    d = int(data["rebar_diam_mm"])
    bars_x = int(math.floor(W / step_m)) + 1
    bars_y = int(math.floor(L / step_m)) + 1
    rebar_m_one_layer = bars_x * L + bars_y * W
    rebar_m_total = rebar_m_one_layer * 2
    weight = REBAR_WEIGHT_KG_M.get(d, (d * d) / 162.0)
    rebar_kg = rebar_m_total * weight
    return {
        "area_m2": round(area, 3),
        "concrete_m3": round(area * slab_m, 3),
        "sand_m3": round(area * sand_m, 3),
        "gravel_m3": round(area * gravel_m, 3),
        "bars_x": bars_x,
        "bars_y": bars_y,
        "rebar_m_total": round(rebar_m_total, 1),
        "rebar_kg": round(rebar_kg, 1),
        "rebar_t": round(rebar_kg / 1000.0, 3),
    }

def _frame(c, w, h, title: str, sheet_no: int, total: int, font: str, data: Dict[str, Any]) -> None:
    from reportlab.lib.units import mm
    c.setLineWidth(0.7)
    c.rect(10*mm, 10*mm, w - 20*mm, h - 20*mm)
    c.line(10*mm, 35*mm, w - 10*mm, 35*mm)
    c.line(w - 135*mm, 10*mm, w - 135*mm, 35*mm)
    c.line(w - 80*mm, 10*mm, w - 80*mm, 35*mm)
    c.line(w - 35*mm, 10*mm, w - 35*mm, 35*mm)
    c.setFont(font, 9)
    c.drawString(14*mm, 23*mm, _clean(title, 90))
    c.drawString(w - 132*mm, 23*mm, f"Раздел {data.get('section','КЖ')}")
    c.drawString(w - 77*mm, 23*mm, f"Лист {sheet_no}")
    c.drawString(w - 32*mm, 23*mm, f"Листов {total}")
    c.setFont(font, 7)
    c.drawString(14*mm, 15*mm, f"{ENGINE} · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.setFont(font, 14)
    c.drawString(18*mm, h - 18*mm, _clean(title, 120))
    c.setFont(font, 8)
    c.drawString(18*mm, h - 25*mm, f"{data.get('project_name','Проект')} · {data.get('length_m')}x{data.get('width_m')} м")

def _draw_lines(c, lines: List[str], x_mm: float, y_mm: float, font: str, size: int = 10, step: float = 7.5) -> None:
    from reportlab.lib.units import mm
    y = y_mm
    c.setFont(font, size)
    for line in lines:
        c.drawString(x_mm*mm, y*mm, _clean(line, 150))
        y -= step

def _draw_plan(c, w, h, font: str, data: Dict[str, Any], calc: Dict[str, Any], rebar: bool = False) -> None:
    from reportlab.lib.units import mm
    L = float(data["length_m"])
    W = float(data["width_m"])
    x0 = 55*mm
    y0 = 55*mm
    scale = min((w - 115*mm) / (L * 1000), (h - 130*mm) / (W * 1000))
    rw = L * 1000 * scale
    rh = W * 1000 * scale
    c.setLineWidth(1.2)
    c.rect(x0, y0, rw, rh)
    c.setFont(font, 9)
    c.drawString(x0, y0 - 8*mm, f"{L:g} м")
    c.saveState()
    c.translate(x0 - 8*mm, y0)
    c.rotate(90)
    c.drawString(0, 0, f"{W:g} м")
    c.restoreState()
    c.setDash(5, 3)
    c.line(x0, y0 + rh / 2, x0 + rw, y0 + rh / 2)
    c.line(x0 + rw / 2, y0, x0 + rw / 2, y0 + rh)
    c.setDash()

    if rebar:
        step_px = max(1.8*mm, data["rebar_step_mm"] * scale)
        c.setLineWidth(0.25)
        x = x0 + step_px
        while x < x0 + rw:
            c.line(x, y0, x, y0 + rh)
            x += step_px
        y = y0 + step_px
        while y < y0 + rh:
            c.line(x0, y, x0 + rw, y)
            y += step_px
        txt = f"Армирование: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм, верхняя и нижняя сетка"
    else:
        txt = f"Плита {L:g}x{W:g} м, площадь {calc['area_m2']} м²"

    c.setFont(font, 10)
    c.drawString(25*mm, (h/mm - 42)*mm, txt)

def _draw_section(c, w, h, font: str, data: Dict[str, Any]) -> None:
    from reportlab.lib.units import mm
    bx = 55*mm
    by = 70*mm
    total = data["slab_mm"] + data["gravel_mm"] + data["sand_mm"]
    k = 105*mm / total
    layers = [
        ("Фундаментная плита", data["slab_mm"], f"Бетон {data['concrete_class']}, защитный слой {data['cover_mm']} мм"),
        ("Щебёночное основание", data["gravel_mm"], "Уплотнение послойно"),
        ("Песчаная подушка", data["sand_mm"], "Уплотнение послойно"),
    ]
    y = by
    c.setLineWidth(0.8)
    for name, th, note in reversed(layers):
        hh = th * k
        c.rect(bx, y, 230*mm, hh)
        c.setFont(font, 10)
        c.drawString(bx + 5*mm, y + hh/2, f"{name}: {th} мм · {note}")
        y += hh
    c.setFont(font, 10)
    c.drawString(25*mm, 235*mm, "Разрез 1-1")
    c.drawString(25*mm, 225*mm, f"Армирование: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм")

def _draw_nodes(c, w, h, font: str, data: Dict[str, Any]) -> None:
    from reportlab.lib.units import mm
    c.setFont(font, 11)
    c.drawString(25*mm, 245*mm, "Типовые узлы")
    bx, by = 45*mm, 95*mm
    for i, title in enumerate(["Узел края плиты", "Узел защитного слоя", "Узел основания"], 0):
        x = bx + i * 115*mm
        c.setLineWidth(0.8)
        c.rect(x, by, 90*mm, 75*mm)
        c.line(x, by + 22*mm, x + 90*mm, by + 22*mm)
        c.line(x + 20*mm, by, x + 20*mm, by + 75*mm)
        c.setFont(font, 8)
        c.drawString(x + 4*mm, by + 63*mm, title)
        c.drawString(x + 4*mm, by + 15*mm, f"Защитный слой {data['cover_mm']} мм")
        c.drawString(x + 4*mm, by + 7*mm, f"Ø{data['rebar_diam_mm']} {data['rebar_class']}")

def _spec_rows(data: Dict[str, Any], calc: Dict[str, Any]) -> List[Tuple[str, str, Any, str]]:
    return [
        (f"Бетон {data['concrete_class']} для фундаментной плиты", "м³", calc["concrete_m3"], "по объёму плиты"),
        ("Песчаная подушка", "м³", calc["sand_m3"], "послойное уплотнение"),
        ("Щебёночное основание", "м³", calc["gravel_m3"], "послойное уплотнение"),
        (f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']}", "п.м", calc["rebar_m_total"], "верхняя и нижняя сетка"),
        (f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']}", "т", calc["rebar_t"], "расчётный вес"),
    ]

def _draw_spec(c, w, h, font: str, rows: List[Tuple[str, str, Any, str]]) -> None:
    from reportlab.lib.units import mm
    x = 25*mm
    y = 235*mm
    c.setFont(font, 10)
    headers = ["№", "Наименование", "Ед.", "Кол-во", "Примечание"]
    widths = [12*mm, 150*mm, 22*mm, 32*mm, 110*mm]
    c.setLineWidth(0.5)
    cx = x
    for head, ww in zip(headers, widths):
        c.rect(cx, y, ww, 8*mm)
        c.drawString(cx + 2*mm, y + 2.3*mm, head)
        cx += ww
    y -= 8*mm
    for i, row in enumerate(rows, 1):
        vals = [str(i), row[0], row[1], str(row[2]), row[3]]
        cx = x
        for val, ww in zip(vals, widths):
            c.rect(cx, y, ww, 8*mm)
            c.drawString(cx + 2*mm, y + 2.3*mm, _clean(val, 55))
            cx += ww
        y -= 8*mm

def write_project_pdf(path: str, data: Dict[str, Any], template: Dict[str, Any], sheets: List[Dict[str, str]], calc: Dict[str, Any]) -> str:
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    font = _font_name()
    page_size = landscape(A3)
    w, h = page_size
    c = canvas.Canvas(path, pagesize=page_size)
    rows = _spec_rows(data, calc)
    total = len(sheets)

    for idx, sh in enumerate(sheets, 1):
        title = sh["title"]
        low = title.lower()
        _frame(c, w, h, f"{sh['mark']}-{sh['number']} {title}", idx, total, font, data)

        if "титул" in low:
            c.setFont(font, 18)
            c.drawCentredString(w/2, h - 85*mm, data["project_name"])
            c.setFont(font, 14)
            c.drawCentredString(w/2, h - 100*mm, f"Раздел {data['section']}")
            c.setFont(font, 11)
            c.drawCentredString(w/2, h - 116*mm, f"Параметры: {data['length_m']:g}x{data['width_m']:g} м, плита {data['slab_mm']} мм")
            c.drawCentredString(w/2, h - 130*mm, "Сформировано по сохранённому шаблону пользователя")
        elif "общ" in low or "данн" in low:
            lines = [
                f"Наименование: {data['project_name']}",
                f"Раздел: {data['section']}",
                f"Размер плиты: {data['length_m']:g} x {data['width_m']:g} м",
                f"Толщина плиты: {data['slab_mm']} мм",
                f"Основание: щебень {data['gravel_mm']} мм, песок {data['sand_mm']} мм",
                f"Бетон: {data['concrete_class']}",
                f"Арматура: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм",
                f"Площадь: {calc['area_m2']} м², бетон: {calc['concrete_m3']} м³",
                "",
                "Нормативная база:",
            ] + NORMATIVE_NOTES
            _draw_lines(c, lines, 25, 245, font, 10)
        elif "ведомость лист" in low or "состав" in low:
            lines = [f"{i}. {x['mark']}-{x['number']} {x['title']}" for i, x in enumerate(sheets, 1)]
            _draw_lines(c, lines, 25, 245, font, 10)
        elif "план" in low and "арм" not in low:
            _draw_plan(c, w, h, font, data, calc, rebar=False)
        elif "разрез" in low or "сечен" in low:
            _draw_section(c, w, h, font, data)
        elif "ниж" in low and "арм" in low:
            _draw_plan(c, w, h, font, data, calc, rebar=True)
            c.setFont(font, 10)
            c.drawString(25*mm, 220*mm, "Нижняя сетка армирования")
        elif "верх" in low and "арм" in low:
            _draw_plan(c, w, h, font, data, calc, rebar=True)
            c.setFont(font, 10)
            c.drawString(25*mm, 220*mm, "Верхняя сетка армирования")
        elif "арм" in low or "сетк" in low:
            _draw_plan(c, w, h, font, data, calc, rebar=True)
        elif "узел" in low or "детал" in low:
            _draw_nodes(c, w, h, font, data)
        elif "специф" in low or "материал" in low or "стали" in low:
            _draw_spec(c, w, h, font, rows)
        else:
            _draw_lines(c, [
                f"Лист: {title}",
                f"Раздел: {data['section']}",
                f"Размер: {data['length_m']:g}x{data['width_m']:g} м",
                f"Бетон: {data['concrete_class']}",
                f"Арматура: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм",
            ], 25, 245, font, 10)

        c.showPage()

    c.save()
    return path

def write_project_dxf(path: str, data: Dict[str, Any], calc: Dict[str, Any]) -> str:
    import ezdxf
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    msp = doc.modelspace()

    for name, color in [("KJ_OUTLINE", 7), ("KJ_REBAR", 1), ("KJ_AXES", 3), ("KJ_TEXT", 2), ("KJ_SECTION", 5)]:
        doc.layers.new(name=name, dxfattribs={"color": color})

    L = float(data["length_m"]) * 1000
    W = float(data["width_m"]) * 1000
    step = float(data["rebar_step_mm"])

    pts = [(0,0), (L,0), (L,W), (0,W), (0,0)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": "KJ_OUTLINE", "closed": False})
    msp.add_line((L/2, 0), (L/2, W), dxfattribs={"layer": "KJ_AXES"})
    msp.add_line((0, W/2), (L, W/2), dxfattribs={"layer": "KJ_AXES"})

    x = step
    while x < L:
        msp.add_line((x, 0), (x, W), dxfattribs={"layer": "KJ_REBAR"})
        x += step
    y = step
    while y < W:
        msp.add_line((0, y), (L, y), dxfattribs={"layer": "KJ_REBAR"})
        y += step

    msp.add_text(
        f"{data['project_name']} {data['length_m']:g}x{data['width_m']:g}m",
        dxfattribs={"layer": "KJ_TEXT", "height": 250}
    ).set_placement((0, -900))

    msp.add_text(
        f"{data['concrete_class']} · {data['rebar_class']} D{data['rebar_diam_mm']} step {data['rebar_step_mm']}mm",
        dxfattribs={"layer": "KJ_TEXT", "height": 220}
    ).set_placement((0, -1300))

    sx = L + 1500
    y0 = 0
    layers = [
        ("Sand", data["sand_mm"]),
        ("Gravel", data["gravel_mm"]),
        ("Slab", data["slab_mm"]),
    ]
    for name, th in layers:
        msp.add_lwpolyline([(sx,y0),(sx+4000,y0),(sx+4000,y0+th),(sx,y0+th),(sx,y0)], dxfattribs={"layer": "KJ_SECTION"})
        msp.add_text(f"{name} {th}mm", dxfattribs={"layer": "KJ_TEXT", "height": 160}).set_placement((sx+4200, y0 + th/2))
        y0 += th

    doc.saveas(path)
    return path

def write_project_xlsx(path: str, data: Dict[str, Any], sheets: List[Dict[str, str]], calc: Dict[str, Any], template: Dict[str, Any]) -> str:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

    wb = Workbook()
    ws = wb.active
    ws.title = "Спецификация"

    headers = ["№", "Наименование", "Ед.изм", "Кол-во", "Примечание"]
    rows = _spec_rows(data, calc)

    ws.merge_cells("A1:E1")
    ws["A1"] = f"{data['project_name']} · {data['section']}"
    ws["A1"].font = Font(bold=True, size=13)
    ws["A1"].alignment = Alignment(horizontal="center")

    for c, h in enumerate(headers, 1):
        cell = ws.cell(3, c, h)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="DDEEFF")

    for r, row in enumerate(rows, 4):
        ws.cell(r, 1, r - 3)
        ws.cell(r, 2, row[0])
        ws.cell(r, 3, row[1])
        ws.cell(r, 4, row[2])
        ws.cell(r, 5, row[3])

    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 55
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 16
    ws.column_dimensions["E"].width = 35

    ws2 = wb.create_sheet("Ведомость листов")
    ws2.append(["№", "Марка", "Номер", "Наименование"])
    for i, sh in enumerate(sheets, 1):
        ws2.append([i, sh["mark"], sh["number"], sh["title"]])
    for col in ["A", "B", "C", "D"]:
        ws2.column_dimensions[col].width = 25

    ws3 = wb.create_sheet("Расчёт")
    for k, v in [
        ("Длина, м", data["length_m"]),
        ("Ширина, м", data["width_m"]),
        ("Площадь, м2", calc["area_m2"]),
        ("Бетон, м3", calc["concrete_m3"]),
        ("Песок, м3", calc["sand_m3"]),
        ("Щебень, м3", calc["gravel_m3"]),
        ("Арматура, п.м", calc["rebar_m_total"]),
        ("Арматура, т", calc["rebar_t"]),
    ]:
        ws3.append([k, v])
    ws3.column_dimensions["A"].width = 35
    ws3.column_dimensions["B"].width = 18

    wb.save(path)
    return path

def write_project_manifest(path: str, data: Dict[str, Any], template: Dict[str, Any], sheets: List[Dict[str, str]], calc: Dict[str, Any], files: Dict[str, str], links: Dict[str, str], task_id: str, topic_id: int) -> str:
    manifest = {
        "schema": "AREAL_PROJECT_DOCUMENTATION_PACKAGE_V1",
        "engine": ENGINE,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "topic_id": topic_id,
        "input": data.get("input"),
        "section": data.get("section"),
        "project_kind": data.get("project_kind"),
        "template_file": template.get("template_file"),
        "template_project_type": template.get("project_type"),
        "sheet_count": len(sheets),
        "sheet_register": sheets,
        "parameters": data,
        "calculation": calc,
        "files": files,
        "links": links,
        "normative_notes": NORMATIVE_NOTES,
        "status": "ARTIFACTS_CREATED_AND_UPLOADED",
    }
    Path(path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def _validate_pdf(path: str, min_pages: int) -> Tuple[bool, str]:
    if not os.path.exists(path) or os.path.getsize(path) < 5000:
        return False, "PDF_FILE_TOO_SMALL"
    try:
        from pypdf import PdfReader
        pages = len(PdfReader(path).pages)
        if pages < min_pages:
            return False, f"PDF_PAGE_COUNT_TOO_LOW:{pages}"
    except Exception as e:
        return False, f"PDF_VALIDATE_ERROR:{str(e)[:100]}"
    return True, ""

def _upload(path: str, task_id: str, topic_id: int) -> str:
    from core.engine_base import upload_artifact_to_drive
    link = upload_artifact_to_drive(path, task_id, topic_id)
    return str(link or "")

def create_full_project_package(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "") -> Dict[str, Any]:
    data = parse_project_request(raw_input, template_hint)
    template = _choose_template(data["section"], topic_id)
    sheets = _normalize_sheet_register(template, data)

    if len(sheets) < 8:
        return {
            "success": False,
            "error": f"SHEET_REGISTER_TOO_SHORT:{len(sheets)}",
            "engine": ENGINE,
            "section": data["section"],
            "sheet_count": len(sheets),
        }

    calc = _calc_foundation(data)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_task = _safe_name(task_id)[:20]
    out_dir = Path(tempfile.gettempdir()) / f"areal_project_full_{safe_task}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{data['section']}_project_{safe_task}"
    pdf_path = str(out_dir / f"{base_name}.pdf")
    dxf_path = str(out_dir / f"{base_name}.dxf")
    xlsx_path = str(out_dir / f"{base_name}.xlsx")
    manifest_path = str(out_dir / f"{base_name}.manifest.json")

    res = {
        "success": False,
        "engine": ENGINE,
        "section": data["section"],
        "sheet_count": len(sheets),
        "template_file": template.get("template_file"),
        "pdf_path": pdf_path,
        "dxf_path": dxf_path,
        "xlsx_path": xlsx_path,
        "manifest_path": manifest_path,
        "pdf_link": "",
        "dxf_link": "",
        "xlsx_link": "",
        "manifest_link": "",
        "error": None,
        "data": data,
        "calculation": calc,
    }

    try:
        write_project_pdf(pdf_path, data, template, sheets, calc)
        write_project_dxf(dxf_path, data, calc)
        write_project_xlsx(xlsx_path, data, sheets, calc, template)

        ok, err = _validate_pdf(pdf_path, min_pages=8)
        if not ok:
            res["error"] = err
            return res
        if not os.path.exists(dxf_path) or os.path.getsize(dxf_path) < 1500:
            res["error"] = "DXF_FILE_TOO_SMALL"
            return res
        if not os.path.exists(xlsx_path) or os.path.getsize(xlsx_path) < 3000:
            res["error"] = "XLSX_FILE_TOO_SMALL"
            return res

        pdf_link = _upload(pdf_path, task_id, topic_id)
        dxf_link = _upload(dxf_path, task_id, topic_id)
        xlsx_link = _upload(xlsx_path, task_id, topic_id)

        links = {"pdf": pdf_link, "dxf": dxf_link, "xlsx": xlsx_link}
        files = {"pdf": pdf_path, "dxf": dxf_path, "xlsx": xlsx_path}
        write_project_manifest(manifest_path, data, template, sheets, calc, files, links, task_id, topic_id)
        manifest_link = _upload(manifest_path, task_id, topic_id)

        if not pdf_link:
            res["error"] = "PDF_UPLOAD_FAILED"
            return res
        if not dxf_link:
            res["error"] = "DXF_UPLOAD_FAILED"
            return res
        if not xlsx_link:
            res["error"] = "XLSX_UPLOAD_FAILED"
            return res

        res.update({
            "success": True,
            "pdf_link": pdf_link,
            "dxf_link": dxf_link,
            "xlsx_link": xlsx_link,
            "manifest_link": manifest_link,
        })
        return res
    except Exception as e:
        res["error"] = str(e)[:500]
        return res

def is_project_design_request(text: str) -> bool:
    low = _clean(text, 2000).lower()
    triggers = [
        "создай проект",
        "сделай проект",
        "разработай проект",
        "готовый проект",
        "проект фундамент",
        "проект фундаментной плиты",
        "проект кровли",
        "проект по образцу",
        "проект по шаблону",
        "полный проект",
        "проектная документация",
        "рабочая документация",
        "выдай проект",
        "нужен проект",
    ]
    return any(x in low for x in triggers)

def format_project_result_message(res: Dict[str, Any]) -> str:
    if not res.get("success"):
        return "Проект не создан: " + _clean(res.get("error") or "ошибка генерации", 300)
    data = res.get("data") or {}
    calc = res.get("calculation") or {}
    lines = [
        "Проектная документация создана",
        f"Движок: {res.get('engine')}",
        f"Раздел: {res.get('section')}",
        f"Листов PDF: {res.get('sheet_count')}",
        f"Размер: {data.get('length_m')} x {data.get('width_m')} м",
        f"Плита: {data.get('slab_mm')} мм",
        f"Бетон: {data.get('concrete_class')}",
        f"Арматура: {data.get('rebar_class')} Ø{data.get('rebar_diam_mm')} шаг {data.get('rebar_step_mm')} мм",
        f"Бетон: {calc.get('concrete_m3')} м³",
        f"Арматура: {calc.get('rebar_t')} т",
        "",
        f"PDF: {res.get('pdf_link')}",
        f"DXF: {res.get('dxf_link')}",
        f"XLSX: {res.get('xlsx_link')}",
    ]
    if res.get("manifest_link"):
        lines.append(f"MANIFEST: {res.get('manifest_link')}")
    lines.append("")
    lines.append("Доволен результатом? Ответь: Да / Уточни / Правки")
    return "\n".join(lines)

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "") -> Dict[str, Any]:
    return create_full_project_package(raw_input, task_id, topic_id, template_hint)

# === END FULLFIX_07_CAD_PROJECT_DOCUMENTATION_CLOSURE ===


# === FULLFIX_08_PROJECT_SIGNATURE_COMPAT ===
# Compatibility layer:
# - accepts legacy worker calls with extra positional args
# - exposes create_full_project_documentation for diagnostics and future routes
# - keeps the real FULLFIX_07 CAD generator as the single backend

_FF08_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT = globals().get("create_project_pdf_dxf_artifact")

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    if _FF08_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT is None:
        return {
            "success": False,
            "engine": "FULLFIX_08_PROJECT_SIGNATURE_COMPAT",
            "error": "ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT_NOT_FOUND",
        }

    try:
        return await _FF08_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT(
            raw_input,
            task_id,
            int(topic_id or 0),
            str(template_hint or "")
        )
    except TypeError as e:
        msg = str(e)
        if "positional arguments" not in msg and "argument" not in msg:
            raise
        return await _FF08_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT(
            raw_input,
            task_id,
            int(topic_id or 0)
        )

async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    return await create_project_pdf_dxf_artifact(
        raw_input,
        task_id,
        int(topic_id or 0),
        str(template_hint or ""),
        *args,
        **kwargs
    )

# === END FULLFIX_08_PROJECT_SIGNATURE_COMPAT ===



# === FULLFIX_09_PROJECT_TEMPLATE_REGISTER_REPAIR ===
# Purpose:
# - repaired template models from data/project_templates/*_repaired.json are authoritative
# - never generate project PDF with empty/1-sheet register
# - KЖ fallback = 20 sheets, КД fallback = 21 sheets, АР fallback = 22 sheets

def _ff09_canon_sheet_register(section: str) -> list:
    section = str(section or "").upper().strip()
    if section == "КД":
        return [
            "01 Общие данные",
            "02 План балок перекрытия",
            "03 План стропильной системы",
            "04 План стропильной системы",
            "05 Узлы крепления стропильной системы",
            "06 Спецификация элементов стропильной системы",
            "07 План обрешётки",
            "08 План контробрешётки",
            "09 Узлы кровли",
            "10 Сечения кровельного пирога",
            "11 Узлы карнизного свеса",
            "12 Узлы конька",
            "13 Узлы ендовы",
            "14 Узлы примыкания",
            "15 Узлы проходок",
            "16 Ведомость пиломатериалов",
            "17 Ведомость крепежа",
            "18 Спецификация кровельных материалов",
            "19 Схема монтажа",
            "20 Общие указания",
            "21 Ведомость листов",
        ]
    if section == "АР":
        return [
            "01 Общие данные",
            "02 Ситуационный план",
            "03 План закладных деталей коммуникаций",
            "04 План фундамента",
            "05 План первого этажа",
            "06 План кровли",
            "07 Фасад 1-4",
            "08 Фасад 4-1",
            "09 Фасад А-Д",
            "10 Фасад Д-А",
            "11 Разрез 1-1",
            "12 Разрез 2-2",
            "13 Экспликация помещений",
            "14 Спецификация окон",
            "15 Спецификация дверей",
            "16 Узлы наружных стен",
            "17 Узлы кровли",
            "18 Узлы примыканий",
            "19 Ведомость отделки",
            "20 Общие указания",
            "21 Технико-экономические показатели",
            "22 Ведомость листов",
        ]
    return [
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
        "20 Ведомость листов",
    ]

def _ff09_load_repaired_template(section: str) -> dict:
    import json as _json_ff09
    from pathlib import Path as _Path_ff09

    section = str(section or "КЖ").upper().strip()
    base = _Path_ff09("/root/.areal-neva-core/data/project_templates")

    candidates = [
        base / f"PROJECT_TEMPLATE_MODEL__{section}_repaired.json",
        base / f"PROJECT_TEMPLATE_MODEL__{section}_manual.json",
    ]

    for path in candidates:
        if not path.exists():
            continue
        try:
            model = _json_ff09.loads(path.read_text(encoding="utf-8"))
            reg = model.get("sheet_register") or []
            if isinstance(reg, list) and len(reg) >= 10:
                model["template_file"] = str(path)
                return model
        except Exception:
            pass

    return {
        "schema": "PROJECT_TEMPLATE_MODEL_V2_CANON_FALLBACK",
        "project_type": section,
        "template_file": "canonical_fallback",
        "sheet_register": _ff09_canon_sheet_register(section),
        "sections": [],
        "materials": [],
    }

_FF09_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT = globals().get("create_project_pdf_dxf_artifact")

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    raw = str(raw_input or "")
    low = raw.lower()

    section = "КЖ"
    if " кд" in low or "кд " in low or "деревян" in low or "стропил" in low or "кровл" in low:
        section = "КД"
    elif " ар" in low or "ар " in low or "архитект" in low or "фасад" in low:
        section = "АР"
    elif " кж" in low or "кж " in low or "фундамент" in low or "плит" in low or "армир" in low:
        section = "КЖ"

    repaired = _ff09_load_repaired_template(section)
    if template_hint:
        try:
            import json as _json_ff09
            hint_obj = _json_ff09.loads(str(template_hint))
            if isinstance(hint_obj, dict):
                hint_obj.update({"sheet_register": repaired.get("sheet_register") or [], "template_file": repaired.get("template_file")})
                template_hint = _json_ff09.dumps(hint_obj, ensure_ascii=False)
        except Exception:
            template_hint = str(repaired.get("template_file") or "")

    if not template_hint:
        template_hint = str(repaired.get("template_file") or "")

    if callable(_FF09_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT):
        res = await _FF09_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT(raw_input, task_id, topic_id, template_hint)
    else:
        res = {"success": False, "error": "ORIGINAL_PROJECT_ENGINE_NOT_FOUND"}

    if isinstance(res, dict):
        data = res.get("data") or {}
        tpl = data.get("template") or {}
        reg = tpl.get("sheet_register") or repaired.get("sheet_register") or _ff09_canon_sheet_register(section)

        if len(reg) < 10:
            reg = _ff09_canon_sheet_register(section)

        tpl["sheet_register"] = reg
        tpl["template_file"] = repaired.get("template_file") or tpl.get("template_file") or "canonical_fallback"
        data["template"] = tpl
        data["sheet_register"] = reg
        res["data"] = data
        res["sheet_count"] = len(reg)
        res["template_file"] = tpl["template_file"]

        msg = str(res.get("message") or "")
        if msg:
            msg = re.sub(r"Листов(?: PDF)?:\s*\d+", f"Листов PDF: {len(reg)}", msg)
            if "Шаблон:" not in msg:
                msg = msg.replace("Раздел:", f"Шаблон: {tpl['template_file']}\nРаздел:", 1)
            res["message"] = msg

    return res

async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

# === END FULLFIX_09_PROJECT_TEMPLATE_REGISTER_REPAIR ===


# === FULLFIX_10_TOTAL_CLOSURE_CAD_OVERRIDE ===
# Purpose:
# - user may write simple natural text: "сделай плиту 12 на 8..."
# - foundation slab must always be КЖ
# - foundation slab must never use КД/roof/wood sheet register
# - generated PDF must pass forbidden-word validation before returning links

from core.orchestra_closure_engine import (
    parse_foundation_request as _ff10_parse_foundation_request,
    foundation_sheets as _ff10_foundation_sheets,
    extract_pdf_text as _ff10_extract_pdf_text,
    validate_foundation_text as _ff10_validate_foundation_text,
    ENGINE as _FF10_ENGINE,
)

_FF10_ORIGINAL_PARSE_PROJECT_REQUEST = globals().get("parse_project_request")
_FF10_ORIGINAL_NORMALIZE_SHEET_REGISTER = globals().get("_normalize_sheet_register")
_FF10_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT = globals().get("create_project_pdf_dxf_artifact")

def parse_project_request(raw_input: str, template_hint: str = "") -> dict:
    data = _ff10_parse_foundation_request(str(raw_input or "") + " " + str(template_hint or ""))
    if data.get("project_kind") == "foundation_slab":
        data["section"] = "КЖ"
        data["project_name"] = "Проект фундаментной плиты"
        return data
    if callable(_FF10_ORIGINAL_PARSE_PROJECT_REQUEST):
        return _FF10_ORIGINAL_PARSE_PROJECT_REQUEST(raw_input, template_hint)
    return data

def _normalize_sheet_register(template: dict, data: dict) -> list:
    if str((data or {}).get("project_kind") or "").lower() == "foundation_slab":
        return _ff10_foundation_sheets()
    if callable(_FF10_ORIGINAL_NORMALIZE_SHEET_REGISTER):
        return _FF10_ORIGINAL_NORMALIZE_SHEET_REGISTER(template, data)
    return _ff10_foundation_sheets()

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    if not callable(_FF10_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT):
        return {"success": False, "engine": _FF10_ENGINE, "error": "ORIGINAL_PROJECT_ENGINE_NOT_FOUND"}

    res = await _FF10_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT(raw_input, task_id, topic_id, template_hint, *args, **kwargs)
    if not isinstance(res, dict):
        return {"success": False, "engine": _FF10_ENGINE, "error": "INVALID_ENGINE_RESULT"}

    data = res.get("data") or parse_project_request(raw_input, template_hint)
    if str(data.get("project_kind") or "").lower() == "foundation_slab":
        res["section"] = "КЖ"
        res["sheet_count"] = len(_ff10_foundation_sheets())
        pdf_path = str(res.get("pdf_path") or "")
        pdf_text = _ff10_extract_pdf_text(pdf_path)
        ok, err = _ff10_validate_foundation_text(pdf_text)
        if not ok:
            res["success"] = False
            res["engine"] = _FF10_ENGINE
            res["error"] = err
            res["message"] = "Проект не создан: проверка PDF не пройдена"
            return res

    res["engine"] = _FF10_ENGINE
    return res

async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

# === END FULLFIX_10_TOTAL_CLOSURE_CAD_OVERRIDE ===


# === FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT_CAD_OVERRIDE ===
try:
    from core.orchestra_closure_engine import create_compact_project_documentation as _ff12_compact_project

    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff12_compact_project(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff12_compact_project(raw_input, task_id, topic_id, template_hint, *args, **kwargs)
except Exception:
    pass
# === END FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT_CAD_OVERRIDE ===

====================================================================================================
END_FILE: core/cad_project_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/capability_router.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 1aee1e85df8d7f5455453865a1ac6b6c8e443edeb29e71de1cda0a58adfcfeec
====================================================================================================
# === FULLFIX_CAPABILITY_ROUTER_STAGE_2 ===
from __future__ import annotations
from typing import Any, Dict, List

ROUTER_VERSION = "CAPABILITY_ROUTER_V1"

ENGINE_MAP = {
    "general_chat":          "ai_router",
    "orchestration_core":    "ai_router",
    "telegram_automation":   "ai_router",
    "memory_archive":        "ai_router",
    "internet_search":       "search_supplier",
    "product_search":        "search_supplier",
    "auto_parts_search":     "search_supplier",
    "construction_search":   "search_supplier",
    "technical_supervision": "defect_act",
    "estimates":             "estimate_unified",
    "defect_acts":           "defect_act",
    "documents":             "document_engine",
    "spreadsheets":          "sheets_route",
    "google_drive_storage":  "drive_storage",
    "devops_server":         "ai_router",
    "vpn_network":           "ai_router",
    "ocr_photo":             "ocr_engine",
    "cad_dwg":               "dwg_engine",
    "structural_design":     "project_engine",
    "roofing":               "estimate_unified",
    "monolith_concrete":     "estimate_unified",
    "crm_leads":             "ai_router",
    "email_ingress":         "email_ingress",
    "social_content":        "content_engine",
    "video_production":      "video_production_agent",
    "photo_cleanup":         "photo_cleanup",
    "isolated_project_ivan": "ai_router",
}

FALLBACK_ENGINE = "ai_router"


def _step(engine, action, params=None, required=True):
    return {"engine": engine, "action": action, "params": params or {}, "required": required, "status": "pending"}


def _plan(direction, profile, work_item):
    engine = profile.get("engine") or ENGINE_MAP.get(direction, FALLBACK_ENGINE)
    formats_out = profile.get("output_formats") or ["telegram_text"]
    requires_search = bool(profile.get("requires_search"))
    quality_gates = profile.get("quality_gates") or []
    input_type = (getattr(work_item, "input_type", "") or "").lower()
    raw_text = (getattr(work_item, "raw_text", "") or "")[:300]

    steps = []
    if input_type in ("photo", "image") and direction != "photo_cleanup":
        steps.append(_step("ocr_engine", "extract_text", required=False))
    if requires_search:
        steps.append(_step("search_supplier", "search", {"query": raw_text, "direction": direction}))
    steps.append(_step(engine, "execute", {"direction": direction, "formats_out": formats_out, "quality_gates": quality_gates}))
    if "xlsx" in formats_out:
        steps.append(_step("format_adapter", "to_xlsx"))
    if "docx" in formats_out or "pdf" in formats_out:
        steps.append(_step("format_adapter", "to_document"))
    if "drive_link" in formats_out:
        steps.append(_step("drive_storage", "upload", required=False))
    return steps, engine


class CapabilityRouter:
    def apply_to_work_item(self, work_item) -> Dict[str, Any]:
        direction = getattr(work_item, "direction", None) or "general_chat"
        profile = getattr(work_item, "direction_profile", {}) or {}
        if not profile:
            profile = {"engine": ENGINE_MAP.get(direction, FALLBACK_ENGINE)}

        steps, engine = _plan(direction, profile, work_item)
        work_item.execution_plan = steps
        work_item.formats_out = profile.get("output_formats") or ["telegram_text"]
        work_item.quality_gates = profile.get("quality_gates") or []
        work_item.add_audit("capability_router", ROUTER_VERSION)
        work_item.add_audit("engine", engine)
        work_item.add_audit("execution_plan_steps", len(steps))
        return {"direction": direction, "engine": engine, "execution_plan": steps,
                "formats_out": work_item.formats_out, "quality_gates": work_item.quality_gates,
                "router_version": ROUTER_VERSION}
# === END FULLFIX_CAPABILITY_ROUTER_STAGE_2 ===

====================================================================================================
END_FILE: core/capability_router.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/capability_router_dispatch.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5289c229f54cd10f2a8a2c42c36b5ceadbaf5e717d8473c4c354d3a390b9ae49
====================================================================================================
# === CAPABILITY_ROUTER_REAL_DISPATCH_V1 ===
from __future__ import annotations

from typing import Any, Dict

def build_execution_plan(input_type: str = "", user_text: str = "", file_name: str = "", mime_type: str = "", topic_id: int = 0) -> Dict[str, Any]:
    low = f"{input_type} {user_text} {file_name} {mime_type}".lower()
    if any(x in low for x in ("dwg", "dxf", "ifc", "чертеж", "чертёж", "проект", "кж", "кмд")):
        engine = "dwg_project"
    elif any(x in low for x in ("смет", "расч", "вор", "xlsx", "xls", "csv")):
        engine = "estimate"
    elif any(x in low for x in ("технадзор", "акт", "дефект", "фото", "jpg", "png", "heic", "сп", "гост")):
        engine = "technadzor"
    elif any(x in low for x in ("найди", "поиск", "цена", "купить")):
        engine = "search"
    else:
        engine = "universal"
    return {
        "router": "CAPABILITY_ROUTER_REAL_DISPATCH_V1",
        "topic_id": int(topic_id or 0),
        "engine": engine,
        "input_type": input_type,
        "file_name": file_name,
        "mime_type": mime_type,
    }

def dispatch_hint(plan: Dict[str, Any]) -> str:
    return str((plan or {}).get("engine") or "universal")
# === END_CAPABILITY_ROUTER_REAL_DISPATCH_V1 ===

====================================================================================================
END_FILE: core/capability_router_dispatch.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/chat_exports_policy.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5dba229a50fdb45fd5e3c6537274316caad7f37759487be75e2c97cad258c4d0
====================================================================================================
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

====================================================================================================
END_FILE: core/chat_exports_policy.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/constraint_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e8ffe41c2f52aef2692c65e65c8b59713ab45ba46f13cbffee21118e00d60382
====================================================================================================
# === CONSTRAINT_ENGINE_V1 ===
import re, logging
logger = logging.getLogger(__name__)

# MULTI_OFFER_CONSISTENCY — все офферы в одном формате
def normalize_offer(offer: dict) -> dict:
    return {
        "supplier":  str(offer.get("supplier") or offer.get("поставщик") or "UNKNOWN"),
        "platform":  str(offer.get("platform") or offer.get("площадка") or ""),
        "seller_type": str(offer.get("seller_type") or "UNKNOWN"),
        "city":      str(offer.get("city") or offer.get("город") or ""),
        "price":     _to_float(offer.get("price") or offer.get("цена") or 0),
        "unit":      str(offer.get("unit") or offer.get("ед") or ""),
        "stock":     str(offer.get("stock") or offer.get("наличие") or "UNKNOWN"),
        "delivery":  str(offer.get("delivery") or offer.get("доставка") or "UNKNOWN"),
        "tco":       _to_float(offer.get("tco") or 0),
        "risk":      str(offer.get("risk") or "UNVERIFIED"),
        "contact":   str(offer.get("contact") or offer.get("контакт") or ""),
        "url":       str(offer.get("url") or offer.get("ссылка") or ""),
        "verified":  bool(offer.get("verified") or False),
    }

def _to_float(v) -> float:
    try:
        return float(re.sub(r"[^\d.]", "", str(v)) or 0)
    except Exception:
        return 0.0

def validate_offer(offer: dict) -> dict:
    """Проверить оффер на минимальное качество"""
    issues = []
    if not offer.get("price") or offer["price"] <= 0:
        issues.append("NO_PRICE")
    if not offer.get("contact") and not offer.get("url"):
        issues.append("NO_CONTACT")
    if offer.get("price") and offer["price"] < 10:
        issues.append("PRICE_TOO_LOW")
    return {"ok": len(issues) == 0, "issues": issues}

def rank_offers(offers: list) -> list:
    """ResultRanker — сортировка по TCO или цене"""
    def score(o):
        tco = o.get("tco") or o.get("price") or 999999
        risk_penalty = {"CONFIRMED": 0, "PARTIAL": 5, "UNVERIFIED": 15, "RISK": 30}.get(o.get("risk","UNVERIFIED"), 15)
        return tco + risk_penalty * 100
    return sorted(offers, key=score)

# CONSTRAINT_ENGINE — ограничения на поиск
_CONSTRAINTS = {
    "price_min": 0,
    "price_max": 999_999_999,
    "region": [],
    "exclude_keywords": ["1 руб", "договорная", "под заказ в пути"],
    "require_contact": False,
    "require_stock": False,
}

def apply_constraints(offers: list, constraints: dict = None) -> list:
    c = {**_CONSTRAINTS, **(constraints or {})}
    result = []
    for o in offers:
        price = _to_float(o.get("price") or 0)
        if price and (price < c["price_min"] or price > c["price_max"]):
            continue
        text = str(o).lower()
        if any(ex.lower() in text for ex in c["exclude_keywords"]):
            continue
        if c["require_contact"] and not o.get("contact"):
            continue
        result.append(o)
    return result
# === END CONSTRAINT_ENGINE_V1 ===

====================================================================================================
END_FILE: core/constraint_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/context_loader.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: b2e7c83efbb7cd1e9893212919ed790834ccaef025265a92c0b40faf6898e8e5
====================================================================================================
# === FULLFIX_CONTEXT_LOADER_STAGE_3 ===
from __future__ import annotations
import asyncio
from typing import Any, Dict, Optional

CONTEXT_LOADER_VERSION = "CONTEXT_LOADER_V1"


def _safe_str(v, default=""):
    if v is None: return default
    return str(v)


class ContextLoader:
    """
    Stage 3 shadow mode: загружает контекст задачи из доступных источников.
    Пишет context_refs в WorkItem. Не блокирует выполнение при ошибках.
    """

    def load(self, work_item, db_conn=None) -> Dict[str, Any]:
        chat_id = _safe_str(getattr(work_item, "chat_id", ""))
        topic_id = int(getattr(work_item, "topic_id", 0) or 0)
        raw_text = _safe_str(getattr(work_item, "raw_text", ""))[:500]
        direction = _safe_str(getattr(work_item, "direction", "general_chat"))

        refs = {
            "chat_id": chat_id,
            "topic_id": topic_id,
            "direction": direction,
            "short_memory": None,
            "long_memory": None,
            "recent_tasks": [],
            "topic_context": None,
            "loader_version": CONTEXT_LOADER_VERSION,
            "shadow_mode": True,
        }

        # short_memory — из memory_api если доступна
        try:
            refs["short_memory"] = self._load_short_memory(chat_id, topic_id)
        except Exception as e:
            refs["short_memory_error"] = str(e)

        # topic_context — последние задачи по теме из DB
        if db_conn is not None:
            try:
                refs["topic_context"] = self._load_topic_context(db_conn, chat_id, topic_id)
            except Exception as e:
                refs["topic_context_error"] = str(e)

        work_item.context_refs = refs
        work_item.add_audit("context_loader", CONTEXT_LOADER_VERSION)
        work_item.add_audit("context_topic_id", topic_id)
        return refs

    def _load_short_memory(self, chat_id, topic_id):
        import urllib.request, json
        url = f"http://127.0.0.1:8765/memory?chat_id={chat_id}&topic_id={topic_id}&limit=5"
        try:
            req = urllib.request.urlopen(url, timeout=2)
            data = json.loads(req.read().decode())
            return data if isinstance(data, (list, dict)) else None
        except Exception:
            return None

    def _load_topic_context(self, db_conn, chat_id, topic_id):
        try:
            import sqlite3
            if hasattr(db_conn, "execute"):
                rows = db_conn.execute(
                    "SELECT id, state, created_at FROM tasks WHERE chat_id=? AND topic_id=? ORDER BY created_at DESC LIMIT 5",
                    (str(chat_id), int(topic_id))
                ).fetchall()
            else:
                rows = []
            return [{"id": r[0], "state": r[1], "created_at": r[2]} for r in rows]
        except Exception:
            return []


def load_context(work_item, db_conn=None):
    return ContextLoader().load(work_item, db_conn)
# === END FULLFIX_CONTEXT_LOADER_STAGE_3 ===

====================================================================================================
END_FILE: core/context_loader.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/data_classification.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 94b1f8b88f75ccb2d032ff2f77790acb7884c5f9e6ec7e7ad0f9277824d6d4bf
====================================================================================================
# === DATA_CLASSIFICATION_V1 ===
# Канон §28.3 — File Routing Canon
import re, logging
logger = logging.getLogger(__name__)

_DOMAIN_MAP = {
    "STROYKA":     ["кровля", "фасад", "фундамент", "кирпич", "бетон", "арматура", "утеплитель",
                    "металлочерепица", "профнастил", "сайдинг", "монтаж", "строительство", "ангар"],
    "ESTIMATES":   ["смета", "ведомость", "объём работ", "вор", "ФЕР", "ТЕР", "расценка", "калькул"],
    "TEHNADZOR":   ["технадзор", "дефект", "акт осмотра", "нарушение", "предписание", "сп ", "гост", "снип"],
    "AUTO":        ["toyota", "hiace", "запчасть", "brembo", "vin", "авто", "машина"],
    "SEARCH":      ["найди", "поищи", "цена", "стоимость", "купить", "поставщик", "avito", "ozon"],
    "DOCS_PDF_DWG": ["dwg", "dxf", "чертёж", "pdf", "docx", "проект"],
    "NEURON_SOFT_VPN": ["vpn", "wireguard", "xray", "vless", "конфиг", "ключ"],
}

def classify_domain(text: str, file_name: str = "") -> str:
    combined = (text + " " + file_name).lower()
    scores = {}
    for domain, keywords in _DOMAIN_MAP.items():
        scores[domain] = sum(1 for kw in keywords if kw.lower() in combined)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "UNSORTED"

def classify_file_type(file_name: str) -> str:
    ext = file_name.lower().rsplit(".", 1)[-1] if "." in file_name else ""
    mapping = {
        "pdf": "PDF", "docx": "DOCX", "doc": "DOCX",
        "xlsx": "XLSX", "xls": "XLSX", "csv": "CSV",
        "dwg": "DWG", "dxf": "DXF",
        "jpg": "IMAGE", "jpeg": "IMAGE", "png": "IMAGE",
        "heic": "IMAGE", "webp": "IMAGE",
        "zip": "ARCHIVE", "rar": "ARCHIVE",
        "mp4": "VIDEO", "mov": "VIDEO",
        "ogg": "AUDIO", "mp3": "AUDIO",
    }
    return mapping.get(ext, "UNKNOWN")

def classify_intent(text: str) -> str:
    low = text.lower()
    if any(w in low for w in ["смета", "посчитай", "расценка", "объём"]):
        return "estimate"
    if any(w in low for w in ["шаблон", "образец", "возьми как"]):
        return "template"
    if any(w in low for w in ["дефект", "акт", "нарушение", "технадзор"]):
        return "technadzor"
    if any(w in low for w in ["проект", "кж", "ар", "кд", "км"]):
        return "project"
    if any(w in low for w in ["найди", "поищи", "цена", "купить"]):
        return "search"
    if any(w in low for w in ["dwg", "dxf", "чертёж"]):
        return "dwg"
    return "text"
# === END DATA_CLASSIFICATION_V1 ===

====================================================================================================
END_FILE: core/data_classification.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/defect_act_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ef8ae207b552886b90aed1104beb8171ccb8159e19e4d1b05796d867afbb1817
====================================================================================================
# === FULLFIX_15_DEFECT_ACT ===
import os, logging
from datetime import date
logger = logging.getLogger(__name__)
ENGINE = "FULLFIX_15_DEFECT_ACT"
RUNTIME_DIR = "/root/.areal-neva-core/runtime"
os.makedirs(RUNTIME_DIR, exist_ok=True)
ACT_PHRASES = ["акт", "дефект", "осмотр", "сделай акт", "по фото", "технадзор", "нарушение"]

def is_defect_act_intent(text, mime_type=""):
    t = (text or "").lower()
    return "image" in (mime_type or "") and any(p in t for p in ACT_PHRASES)

def generate_act_docx(task_id, caption, file_name, object_name="UNKNOWN"):
    from docx import Document
    path = os.path.join(RUNTIME_DIR, "act_" + task_id[:8] + ".docx")
    doc = Document()
    doc.add_heading("АКТ ОСМОТРА / ДЕФЕКТНАЯ ВЕДОМОСТЬ", 0)
    today = date.today().strftime("%d.%m.%Y")
    doc.add_paragraph("Дата: " + today)
    doc.add_paragraph("Объект: " + (object_name or "UNKNOWN"))
    doc.add_paragraph("Основание: фото — " + (file_name or ""))
    table = doc.add_table(rows=1, cols=6)
    table.style = "Table Grid"
    for i, h in enumerate(["№", "Фото/файл", "Описание дефекта", "Локация", "Рекомендация", "Статус"]):
        table.rows[0].cells[i].text = h
    row = table.add_row().cells
    row[0].text = "1"; row[1].text = file_name or ""; row[2].text = caption or "требует уточнения"
    row[3].text = "-"; row[4].text = "Устранить"; row[5].text = "Открыт"
    doc.add_paragraph("Заключение: зафиксированы дефекты, требующие устранения.")
    doc.add_paragraph("Составил: ________________________  Дата: " + today)
    doc.save(path)
    return path

def generate_act_pdf(task_id, caption, file_name, object_name="UNKNOWN"):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
    from reportlab.lib import colors
    from core.pdf_cyrillic import register_cyrillic_fonts, make_styles, make_paragraph, clean_pdf_text, FONT_REGULAR, FONT_BOLD
    path = os.path.join(RUNTIME_DIR, "act_" + task_id[:8] + ".pdf")
    register_cyrillic_fonts()
    styles = make_styles()
    today = date.today().strftime("%d.%m.%Y")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20, bottomMargin=20, leftMargin=20, rightMargin=20)
    story = [
        make_paragraph("АКТ ОСМОТРА / ДЕФЕКТНАЯ ВЕДОМОСТЬ", "header", styles), Spacer(1,8),
        make_paragraph("Дата: " + today, "normal", styles),
        make_paragraph("Объект: " + (object_name or "UNKNOWN"), "normal", styles),
        make_paragraph("Основание: " + (file_name or ""), "normal", styles),
        Spacer(1,10),
    ]
    data = [
        [make_paragraph(h, "bold", styles) for h in ["№", "Файл", "Описание", "Локация", "Рекомендация", "Статус"]],
        [make_paragraph(x, "normal", styles) for x in ["1", clean_pdf_text(file_name or ""), clean_pdf_text(caption or "требует уточнения"), "-", "Устранить", "Открыт"]],
    ]
    tbl = Table(data, colWidths=[22, 70, 150, 55, 80, 50])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#444444")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),FONT_BOLD),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("GRID",(0,0),(-1,-1),0.4,colors.black),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(tbl); story.append(Spacer(1,12))
    story.append(make_paragraph("Заключение: зафиксированы дефекты, требующие устранения.", "normal", styles))
    story.append(make_paragraph("Составил: ________________________  Дата: " + today, "normal", styles))
    doc.build(story)
    return path

def process_defect_act_sync(conn, task_id, chat_id, topic_id, raw_input, file_name="", local_path=""):
    from core.artifact_upload_guard import upload_many_or_fail
    from core.reply_sender import send_reply_ex
    # === FULLFIX_20_GEMINI_DEFECT_SYNC ===
    _ff20_vision_text = ""
    try:
        if local_path and any(str(local_path).lower().endswith(ext) for ext in (".jpg",".jpeg",".png",".webp",".heic")):
            import asyncio as _ff20_aio
            from core.gemini_vision import analyze_image_file as _ff20_gif
            try:
                _ff20_aio.get_running_loop()
            except RuntimeError:
                _ff20_vision_text = _ff20_aio.run(
                    _ff20_gif(local_path, prompt="\u041e\u043f\u0438\u0448\u0438 \u0434\u0435\u0444\u0435\u043a\u0442 \u0434\u043b\u044f \u0430\u043a\u0442\u0430", timeout=60)
                ) or ""
            logger.info("FF20_GEMINI_DEFECT_SYNC len=%s", len(_ff20_vision_text))
    except Exception as _ff20_ve:
        logger.warning("FF20_GEMINI_DEFECT_SYNC_ERR=%s", _ff20_ve)
    if _ff20_vision_text:
        raw_input = str(raw_input or "") + "\n\n\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0434\u0435\u0444\u0435\u043a\u0442\u0430: " + str(_ff20_vision_text)
    # === END FULLFIX_20_GEMINI_DEFECT_SYNC ===
    # === NORMATIVE_DB_V1_WIRED ===
    try:
        import asyncio as _norm_aio
        from core.normative_db import search_norms as _search_norms
        _norm_desc = str(raw_input or "") + " " + str(_ff20_vision_text or "")
        try:
            _norm_loop = _norm_aio.get_running_loop()
            _norm_results = []
        except RuntimeError:
            _norm_results = _norm_aio.run(_search_norms(_norm_desc))
        if _norm_results:
            _norm_lines = ["\n\nНормативные требования:"]
            for _n in _norm_results:
                _norm_lines.append(f"  {_n['norm_id']}: {_n['requirement'][:200]}")
            raw_input = str(raw_input or "") + "\n".join(_norm_lines)
    except Exception as _ne:
        logger.warning("NORMATIVE_DB_V1_WIRED err=%s", _ne)
    # === END NORMATIVE_DB_V1_WIRED ===


    try:
        caption = raw_input or file_name
        docx_path = generate_act_docx(task_id, caption, file_name)
        pdf_path = generate_act_pdf(task_id, caption, file_name)
        files = [{"path": pdf_path, "kind": "act_pdf"}, {"path": docx_path, "kind": "act_docx"}]
        up = upload_many_or_fail(files, task_id, topic_id)
        pdf_r = up["results"].get(pdf_path, {}); docx_r = up["results"].get(docx_path, {})
        lines = ["Акт осмотра готов."]
        if pdf_r.get("success") and pdf_r.get("link"): lines.append("PDF: " + pdf_r["link"])
        if docx_r.get("success") and docx_r.get("link"): lines.append("DOCX: " + docx_r["link"])
        if len(lines) == 1: lines.append("Drive недоступен. Файл: " + (file_name or ""))
        result_text = "\n".join(lines)
        conn.execute("UPDATE tasks SET state='AWAITING_CONFIRMATION',result=?,updated_at=datetime('now') WHERE id=?", (result_text, task_id))
        conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (task_id, "state:AWAITING_CONFIRMATION"))
        conn.commit()
        try:
            _br = send_reply_ex(chat_id=str(chat_id), text=result_text, reply_to_message_id=None)
            _bmid = None
            if isinstance(_br, dict): _bmid = _br.get("bot_message_id") or _br.get("message_id")
            elif _br and hasattr(_br, "message_id"): _bmid = _br.message_id
            if _bmid:
                conn.execute("UPDATE tasks SET bot_message_id=? WHERE id=?", (str(_bmid), task_id))
                conn.commit()
        except Exception as _se:
            logger.error("ACT_SEND_ERR task=%s err=%s", task_id, _se)
        return True
    except Exception as e:
        logger.error("DEFECT_ACT_ERROR task=%s err=%s", task_id, e)
        return False

async def process_defect_act(conn, task_id, chat_id, topic_id, raw_input, file_name="", local_path=""):
    import asyncio
    return await asyncio.get_event_loop().run_in_executor(
        None, process_defect_act_sync, conn, task_id, chat_id, topic_id, raw_input, file_name, local_path
    )
# === END FULLFIX_15_DEFECT_ACT ===

====================================================================================================
END_FILE: core/defect_act_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/direction_registry.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 9a97f853b4f786ce481776317e043e44c142dbf4ada231f8e027bc19d3c64e23
====================================================================================================
# === FULLFIX_DIRECTION_KERNEL_STAGE_1_DIRECTION_REGISTRY ===
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

BASE = Path("/root/.areal-neva-core")
CONFIG_PATH = BASE / "config" / "directions.yaml"
SEARCH_TRIGGER_TOKENS = ["найд","поиск","куп","цена","avito","ozon","wildberries","drom","auto.ru","exist","emex","zzap"]

def _s(v): return "" if v is None else str(v)
def _low(v): return _s(v).lower()


class DirectionRegistry:
    def __init__(self, path=None):
        self.path = Path(path) if path else CONFIG_PATH
        self.data = self._load()
        self.directions = self.data.get("directions", {})

    def _load(self):
        raw = self.path.read_text(encoding="utf-8")
        try: return json.loads(raw)
        except Exception:
            try:
                import yaml
                return yaml.safe_load(raw) or {}
            except Exception as e:
                raise RuntimeError(f"DIRECTION_REGISTRY_LOAD_FAIL path={self.path} err={e}")

    def _score_direction(self, direction_id, profile, work_item):
        raw = _low(getattr(work_item, "raw_text", ""))
        topic_id = int(getattr(work_item, "topic_id", 0) or 0)
        input_type = _low(getattr(work_item, "input_type", ""))
        formats_in = [str(x).lower() for x in getattr(work_item, "formats_in", []) or []]

        score = 0
        reasons = []

        strong = profile.get("strong_aliases") or []
        strong_hits = [a for a in strong if _low(a) and _low(a) in raw]
        if strong_hits:
            score += min(250, 200 + 25 * (len(strong_hits) - 1))
            reasons.append("strong:" + ",".join(strong_hits[:5]))

        topic_ids = profile.get("topic_ids") or []
        topic_match = topic_id in topic_ids
        if topic_match:
            score += 70 + max(0, 10 - len(topic_ids))
            reasons.append(f"topic_id:{topic_id}")

        aliases = profile.get("aliases") or []
        alias_hits = [a for a in aliases if _low(a) and _low(a) in raw]
        if alias_hits:
            score += min(120, 30 * len(alias_hits))
            reasons.append("aliases:" + ",".join(alias_hits[:5]))

        any_signal = bool(strong_hits or topic_match or alias_hits)

        if any_signal:
            input_types = [str(x).lower() for x in profile.get("input_types") or []]
            if input_type and input_type in input_types:
                score += 15
                reasons.append("input_type:" + input_type)
            profile_formats = [str(x).lower() for x in profile.get("input_formats") or []]
            fmt_hits = sorted(set(formats_in).intersection(set(profile_formats)))
            if fmt_hits:
                score += min(40, 10 * len(fmt_hits))
                reasons.append("formats:" + ",".join(fmt_hits))

        if any_signal and bool(profile.get("requires_search")):
            if any(t in raw for t in SEARCH_TRIGGER_TOKENS):
                score += 25
                reasons.append("search_signal")

        if not profile.get("enabled", False):
            score = max(0, score - 80)
            reasons.append("passive_penalty")

        return score, {"direction_id": direction_id, "score": score, "reasons": reasons,
                       "enabled": bool(profile.get("enabled", False)), "topic_ids_count": len(topic_ids)}

    def detect(self, work_item):
        results = []
        for direction_id, profile in self.directions.items():
            score, item = self._score_direction(direction_id, profile or {}, work_item)
            item["profile"] = dict(profile or {})
            results.append(item)

        results.sort(key=lambda r: (-r["score"], r["topic_ids_count"]))

        if not results or results[0]["score"] <= 0:
            best_profile = dict(self.directions.get("general_chat", {}))
            best_profile["id"] = "general_chat"
            best_profile["score"] = 0
            best_profile["audit"] = []
            return best_profile

        winner = results[0]
        out = dict(winner["profile"])
        out["id"] = winner["direction_id"]
        out["score"] = winner["score"]
        out["audit"] = [{k: v for k, v in r.items() if k != "profile"} for r in results[:10]]
        return out


def detect_direction(work_item):
    return DirectionRegistry().detect(work_item)
# === END FULLFIX_DIRECTION_KERNEL_STAGE_1_DIRECTION_REGISTRY ===

====================================================================================================
END_FILE: core/direction_registry.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/document_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 3ccafce81ca7ed0c744d41e2ca489c2ee4208ecbb1d17b278c03fee1a072f588
====================================================================================================
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def parse_document(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"text": "", "tables": [], "metadata": {}, "error": f"File not found: {path}"}
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            return _parse_pdf(path)
        elif ext == ".docx":
            return _parse_docx(path)
        elif ext in (".xlsx", ".xls"):
            return _parse_excel(path)
        elif ext == ".csv":
            return _parse_csv(path)
        else:
            return {"text": "", "tables": [], "metadata": {}, "error": f"Unsupported: {ext}"}
    except Exception as e:
        logger.error(f"parse_document error: {e}")
        return {"text": "", "tables": [], "metadata": {}, "error": str(e)}

def extract_text_from_document(path: str) -> str:
    return parse_document(path).get("text", "")

def extract_tables_from_document(path: str) -> list:
    return parse_document(path).get("tables", [])

def _parse_pdf(path: str) -> Dict[str, Any]:
    import pdfplumber
    text_parts = []
    tables = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: text_parts.append(t)
            for tbl in page.extract_tables():
                if tbl: tables.append(tbl)
    return {"text": "\n".join(text_parts), "tables": tables, "metadata": {"pages": len(pdf.pages)}, "error": ""}

def _parse_docx(path: str) -> Dict[str, Any]:
    from docx import Document
    doc = Document(path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text)
    tables = [[[cell.text for cell in row.cells] for row in t.rows] for t in doc.tables]
    return {"text": text, "tables": tables, "metadata": {"source": path}, "error": ""}

def _parse_excel(path: str) -> Dict[str, Any]:
    import pandas as pd
    sheets = pd.read_excel(path, sheet_name=None)
    text, tables = [], []
    for name, df in sheets.items():
        text.append(f"=== {name} ===\n{df.to_string(max_rows=50)}")
        tables.append({"sheet": name, "data": df.fillna("").to_dict(orient="records")})
    return {"text": "\n".join(text), "tables": tables, "metadata": {"sheets": list(sheets.keys())}, "error": ""}

def _parse_csv(path: str) -> Dict[str, Any]:
    import pandas as pd
    df = pd.read_csv(path)
    text = df.to_string(max_rows=50)
    tables = [{"data": df.fillna("").to_dict(orient="records")}]
    return {"text": text, "tables": tables, "metadata": {"source": path}, "error": ""}

====================================================================================================
END_FILE: core/document_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/drive_content_indexer.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 86a8da0033f275d1ba30d0be51cfc639a9dbc68b75b7e2a5ac2dbec3d0f0cd59
====================================================================================================
# === DRIVE_FILE_CONTENT_MEMORY_INDEX_V1 ===
from __future__ import annotations

import csv
import io
import json
import os
import re
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
MEM_DB = f"{BASE}/data/memory.db"
load_dotenv(f"{BASE}/.env", override=True)

MAX_TEXT = 50000
MAX_ROWS = 300


def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()


def _clean(text: str, limit: int = MAX_TEXT) -> str:
    text = (text or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]


def _kind(file_name: str, mime_type: str = "") -> str:
    ext = os.path.splitext((file_name or "").lower())[1]
    mime = (mime_type or "").lower()
    if ext in (".xlsx", ".xlsm", ".csv") or "spreadsheet" in mime or mime == "text/csv":
        return "table"
    if ext in (".pdf", ".docx", ".doc", ".txt") or mime in ("application/pdf", "text/plain"):
        return "document"
    return "skip"


def _drive_service():
    from core.topic_drive_oauth import _oauth_service
    return _oauth_service()


def download_drive_file(file_id: str, file_name: str) -> Optional[str]:
    if not file_id:
        return None
    service = _drive_service()
    suffix = os.path.splitext(file_name or "")[1] or ".bin"
    fd, out = tempfile.mkstemp(prefix="drive_content_", suffix=suffix, dir="/tmp")
    os.close(fd)

    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    from googleapiclient.http import MediaIoBaseDownload
    with io.FileIO(out, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return out


def extract_pdf(path: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        parts = []
        for page in reader.pages[:80]:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                pass
        return _clean("\n".join(parts), MAX_TEXT)
    except Exception as e:
        return f"PDF_PARSE_ERROR: {e}"


def extract_docx(path: str) -> str:
    try:
        from docx import Document
        doc = Document(path)
        return _clean("\n".join(p.text for p in doc.paragraphs if p.text), MAX_TEXT)
    except Exception as e:
        return f"DOCX_PARSE_ERROR: {e}"


def extract_txt(path: str) -> str:
    try:
        return _clean(Path(path).read_text(encoding="utf-8", errors="ignore"), MAX_TEXT)
    except Exception as e:
        return f"TXT_PARSE_ERROR: {e}"


def extract_table(path: str, file_name: str) -> str:
    rows: List[str] = []
    ext = os.path.splitext((file_name or "").lower())[1]

    try:
        if ext == ".csv":
            with open(path, "r", encoding="utf-8", errors="ignore", newline="") as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    rows.append(" | ".join(_s(x) for x in row))
                    if idx >= MAX_ROWS:
                        break
        else:
            from openpyxl import load_workbook
            wb = load_workbook(path, data_only=True, read_only=True)
            for ws in wb.worksheets[:5]:
                rows.append(f"=== SHEET: {ws.title} ===")
                for idx, row in enumerate(ws.iter_rows(values_only=True)):
                    vals = [_s(x) for x in row if _s(x)]
                    if vals:
                        rows.append(" | ".join(vals))
                    if idx >= MAX_ROWS:
                        break
    except Exception as e:
        rows.append(f"TABLE_PARSE_ERROR: {e}")

    return _clean("\n".join(rows), MAX_TEXT)


def extract_content(local_path: str, file_name: str, mime_type: str = "") -> Dict[str, Any]:
    kind = _kind(file_name, mime_type)
    ext = os.path.splitext((file_name or "").lower())[1]

    if kind == "table":
        text = extract_table(local_path, file_name)
    elif kind == "document":
        if ext == ".pdf":
            text = extract_pdf(local_path)
        elif ext == ".docx":
            text = extract_docx(local_path)
        else:
            text = extract_txt(local_path)
    else:
        text = ""

    return {
        "ok": bool(text and not text.endswith("_PARSE_ERROR")),
        "kind": kind,
        "file_name": file_name,
        "mime_type": mime_type,
        "content": _clean(text, MAX_TEXT),
        "chars": len(text or ""),
    }


def save_file_content_memory(chat_id: str, topic_id: int, task_id: str, file_id: str, file_name: str, mime_type: str, content: str) -> Dict[str, Any]:
    if not content.strip():
        return {"ok": False, "reason": "EMPTY_CONTENT"}

    key = f"topic_{int(topic_id or 0)}_file_content_{task_id}"
    value = json.dumps({
        "task_id": task_id,
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "file_id": file_id,
        "file_name": file_name,
        "mime_type": mime_type,
        "content": _clean(content, MAX_TEXT),
    }, ensure_ascii=False)

    with sqlite3.connect(MEM_DB) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        existing = conn.execute("SELECT 1 FROM memory WHERE chat_id=? AND key=? LIMIT 1", (str(chat_id), key)).fetchone()
        if existing:
            return {"ok": True, "key": key, "dedup": True}
        import hashlib
        mid = hashlib.sha1(f"{chat_id}:{key}".encode()).hexdigest()
        conn.execute(
            "INSERT OR IGNORE INTO memory (id, chat_id, key, value, timestamp) VALUES (?,?,?,?,datetime('now'))",
            (mid, str(chat_id), key, value),
        )
        conn.commit()

    return {"ok": True, "key": key, "dedup": False}


def index_drive_file_content(chat_id: str, topic_id: int, task_id: str, file_id: str, file_name: str, mime_type: str = "") -> Dict[str, Any]:
    local_path = None
    try:
        if _kind(file_name, mime_type) == "skip":
            return {"ok": False, "reason": "UNSUPPORTED_TYPE", "file_name": file_name}

        local_path = download_drive_file(file_id, file_name)
        if not local_path or not os.path.exists(local_path):
            return {"ok": False, "reason": "DOWNLOAD_FAILED", "file_name": file_name}

        extracted = extract_content(local_path, file_name, mime_type)
        if not extracted.get("content"):
            return {"ok": False, "reason": "EXTRACT_EMPTY", "file_name": file_name}

        saved = save_file_content_memory(
            chat_id=str(chat_id),
            topic_id=int(topic_id or 0),
            task_id=str(task_id),
            file_id=str(file_id),
            file_name=str(file_name),
            mime_type=str(mime_type or ""),
            content=str(extracted.get("content") or ""),
        )
        return {
            "ok": bool(saved.get("ok")),
            "reason": "INDEXED" if saved.get("ok") else saved.get("reason"),
            "key": saved.get("key"),
            "dedup": saved.get("dedup", False),
            "kind": extracted.get("kind"),
            "chars": extracted.get("chars"),
            "file_name": file_name,
        }
    except Exception as e:
        return {"ok": False, "reason": f"ERROR:{e}", "file_name": file_name}
    finally:
        if local_path:
            try:
                os.remove(local_path)
            except Exception:
                pass
# === END DRIVE_FILE_CONTENT_MEMORY_INDEX_V1 ===

====================================================================================================
END_FILE: core/drive_content_indexer.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/drive_folder_resolver.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 74da8dc00bdbf6caea745c54e55bb20c0fb180092f6feb58a2135924fbfcc21f
====================================================================================================
# === DRIVE_CANON_FOLDER_RESOLVER_V1 ===
from __future__ import annotations

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger("drive_folder_resolver")

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=True)

DEFAULT_CHAT_ID = "-1003725299009"


def get_or_create_topic_folder(topic_id: int, chat_id: str = "") -> str:
    """
    Canonical Drive layout:
    AI_ORCHESTRA / chat_<chat_id> / topic_<topic_id>

    This resolver MUST NOT use Service Account and MUST NOT create flat folders:
    chat_-1003725299009_topic_2
    """
    from core.topic_drive_oauth import _oauth_service, _root_folder_id, _ensure_folder

    service = _oauth_service()
    root_id = _root_folder_id()
    chat = str(chat_id or os.getenv("TELEGRAM_CHAT_ID") or DEFAULT_CHAT_ID)
    chat_folder = _ensure_folder(service, root_id, f"chat_{chat}")
    topic_folder = _ensure_folder(service, chat_folder, f"topic_{int(topic_id or 0)}")
    logger.info(
        "DRIVE_CANON_FOLDER_RESOLVER_V1_OK chat=%s topic=%s folder=%s",
        chat,
        int(topic_id or 0),
        topic_folder,
    )
    return topic_folder


# === END_DRIVE_CANON_FOLDER_RESOLVER_V1 ===

====================================================================================================
END_FILE: core/drive_folder_resolver.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/duplicate_guard.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 674c881d7bc3af021c821051940aebf69d78a44129626e36b5d68be8f7690403
====================================================================================================
import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

def get_file_id(raw_input: str) -> Optional[str]:
    try:
        return json.loads(raw_input or "{}").get("file_id")
    except Exception:
        return None

def find_duplicate(conn, chat_id: str, topic_id: int, file_id: str) -> Optional[Dict]:
    if not file_id:
        return None
    row = conn.execute(
        """SELECT id, state, substr(result,1,240) result, updated_at
           FROM tasks
           WHERE chat_id=?
             AND COALESCE(topic_id,0)=?
             AND input_type='drive_file'
             AND COALESCE(raw_input,'') LIKE ?
             AND state IN ('DONE','AWAITING_CONFIRMATION')
           ORDER BY updated_at DESC
           LIMIT 1""",
        (str(chat_id), int(topic_id or 0), f'%"file_id": "{file_id}"%'),
    ).fetchone()
    return dict(row) if row else None

def duplicate_message(prev: Dict, file_name: str) -> str:
    prev_result = (prev.get("result") or "").strip()[:160]
    if prev_result:
        return (
            f"Этот файл уже был: {file_name}\n"
            f"Прошлый результат: {prev_result}\n\n"
            f"Что сделать?\n"
            f"1. Повторить обработку\n"
            f"2. Сделать другое\n"
            f"3. Отменить"
        )
    return (
        f"Этот файл уже был: {file_name}\n\n"
        f"Что сделать?\n"
        f"1. Повторить обработку\n"
        f"2. Сделать другое\n"
        f"3. Отменить"
    )

====================================================================================================
END_FILE: core/duplicate_guard.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/dwg_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 52d4a88254ff45a37f7535763c22e5ca09d2bcd1490a60c7e9d770b0833b1859
====================================================================================================
# === DWG_DXF_PROJECT_CLOSE_V1 ===
from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
    "кж": ["СП 63.13330.2018", "СП 20.13330.2016/2017", "ГОСТ 34028-2016", "ГОСТ 21.501-2018"],
    "км": ["СП 16.13330.2017", "СП 20.13330.2016/2017", "ГОСТ 27772-2015", "ГОСТ 21.502-2016"],
    "кмд": ["СП 16.13330.2017", "ГОСТ 23118-2019", "ГОСТ 21.502-2016"],
    "кр": ["СП 20.13330.2016/2017", "ГОСТ 21.501-2018"],
    "ар": ["ГОСТ 21.501-2018", "ГОСТ 21.101-2020", "СП 55.13330.2016"],
    "ов": ["СП 60.13330.2020", "ГОСТ 21.602-2016"],
    "вк": ["СП 30.13330.2020", "ГОСТ 21.601-2011"],
    "эом": ["ПУЭ-7", "СП 256.1325800.2016", "ГОСТ 21.608-2014"],
    "гп": ["СП 42.13330.2016", "ГОСТ 21.508-2020"],
}

ENTITY_PROJECT_HINTS = {
    "LINE": "линейная геометрия",
    "LWPOLYLINE": "полилинии/контуры",
    "POLYLINE": "полилинии/контуры",
    "CIRCLE": "окружности/отверстия",
    "ARC": "дуги",
    "TEXT": "текстовые подписи",
    "MTEXT": "многострочные подписи",
    "DIMENSION": "размеры",
    "INSERT": "блоки/узлы",
    "HATCH": "штриховки",
}

def _clean(v: Any, limit: int = 2000) -> str:
    if v is None:
        return ""
    s = str(v).replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()[:limit]

def _safe_name(v: Any, fallback: str = "drawing") -> str:
    s = re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", _clean(v, 120)).strip("._")
    return s or fallback

def _detect_section(file_name: str = "", user_text: str = "", drawing_text: str = "") -> str:
    hay_sources = [file_name or "", user_text or "", drawing_text[:2000] if drawing_text else ""]
    priority = ("кж", "кмд", "км", "кр", "ар", "ов", "вк", "эом", "гп", "пз")
    for src in hay_sources:
        low = src.lower()
        up = src.upper()
        for key in priority:
            if re.search(rf"(^|[^А-ЯA-Z0-9]){re.escape(key.upper())}([^А-ЯA-Z0-9]|$)", up):
                return key
            if key in low:
                return key
    return "кр"

def _read_bytes_head(path: str, n: int = 64) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read(n)
    except Exception:
        return b""

def _try_read_text(path: str, limit: int = 4_000_000) -> str:
    data = b""
    try:
        with open(path, "rb") as f:
            data = f.read(limit)
    except Exception:
        return ""
    for enc in ("utf-8", "cp1251", "latin-1"):
        try:
            return data.decode(enc, errors="ignore")
        except Exception:
            pass
    return data.decode("latin-1", errors="ignore")

def _file_signature(path: str) -> str:
    head = _read_bytes_head(path, 32)
    if head.startswith(b"AC10"):
        return head[:12].decode("latin-1", errors="ignore")
    txt = head.decode("latin-1", errors="ignore")
    if "SECTION" in _try_read_text(path, 4096).upper():
        return "ASCII_DXF"
    return head[:16].hex()

def _try_convert_dwg_to_dxf(path: str) -> Optional[str]:
    src = Path(path)
    if src.suffix.lower() != ".dwg":
        return None

    tmp = Path(tempfile.mkdtemp(prefix="dwg_convert_"))
    in_dir = tmp / "in"
    out_dir = tmp / "out"
    in_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    safe = in_dir / src.name
    shutil.copy2(src, safe)

    converters = [
        shutil.which("dwg2dxf"),
        shutil.which("ODAFileConverter"),
        shutil.which("ODAFileConverter.exe"),
    ]

    for conv in [c for c in converters if c]:
        try:
            name = os.path.basename(conv).lower()
            if "dwg2dxf" in name:
                out = out_dir / (src.stem + ".dxf")
                subprocess.run([conv, str(safe), str(out)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
                if out.exists() and out.stat().st_size > 100:
                    return str(out)
            else:
                subprocess.run(
                    [conv, str(in_dir), str(out_dir), "ACAD2018", "DXF", "0", "1"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=180,
                )
                found = list(out_dir.rglob("*.dxf"))
                if found:
                    found.sort(key=lambda p: p.stat().st_size, reverse=True)
                    if found[0].stat().st_size > 100:
                        return str(found[0])
        except Exception:
            continue

    return None

def _parse_ascii_dxf(path: str) -> Dict[str, Any]:
    text = _try_read_text(path)
    lines = [x.rstrip("\n") for x in text.splitlines()]
    pairs: List[Tuple[str, str]] = []
    i = 0
    while i + 1 < len(lines):
        code = lines[i].strip()
        value = lines[i + 1].strip()
        pairs.append((code, value))
        i += 2

    entities = []
    current: Optional[Dict[str, Any]] = None
    in_entities = False

    for code, value in pairs:
        if code == "0" and value.upper() == "SECTION":
            current = None
            continue
        if code == "2" and value.upper() == "ENTITIES":
            in_entities = True
            continue
        if code == "0" and value.upper() == "ENDSEC":
            if current:
                entities.append(current)
                current = None
            in_entities = False
            continue
        if not in_entities:
            continue

        if code == "0":
            if current:
                entities.append(current)
            current = {"type": value.upper(), "layer": "", "points": [], "texts": [], "raw": {}}
            continue

        if current is None:
            continue

        current["raw"].setdefault(code, []).append(value)
        if code == "8":
            current["layer"] = value
        elif code in ("1", "2", "3"):
            if value and len(value) <= 500:
                current["texts"].append(value)
        elif code in ("10", "20", "30", "11", "21", "31", "12", "22", "32"):
            try:
                current["points"].append((code, float(str(value).replace(",", "."))))
            except Exception:
                pass

    if current:
        entities.append(current)

    entity_counts = Counter(e.get("type") or "UNKNOWN" for e in entities)
    layer_counts = Counter(e.get("layer") or "0" for e in entities)

    texts = []
    for e in entities:
        for t in e.get("texts") or []:
            if t and t not in texts:
                texts.append(t)
            if len(texts) >= 80:
                break

    x_vals, y_vals = [], []
    for e in entities:
        coords = e.get("points") or []
        for code, val in coords:
            if code in ("10", "11", "12"):
                x_vals.append(val)
            elif code in ("20", "21", "22"):
                y_vals.append(val)

    extents = {}
    if x_vals and y_vals:
        extents = {
            "min_x": min(x_vals),
            "max_x": max(x_vals),
            "min_y": min(y_vals),
            "max_y": max(y_vals),
            "width": max(x_vals) - min(x_vals),
            "height": max(y_vals) - min(y_vals),
        }

    dims = []
    for t in texts:
        for m in re.findall(r"(?<!\d)(\d{2,6})(?!\d)", t):
            try:
                v = int(m)
                if 10 <= v <= 100000:
                    dims.append(v)
            except Exception:
                pass
    dims = sorted(set(dims))[:120]

    return {
        "parse_status": "DXF_PARSED",
        "raw_text_chars": len(text),
        "entities_total": len(entities),
        "entity_counts": dict(entity_counts.most_common(60)),
        "layers": dict(layer_counts.most_common(80)),
        "texts": texts[:80],
        "dimensions_detected": dims,
        "extents": extents,
    }

def _parse_dwg_metadata(path: str) -> Dict[str, Any]:
    p = Path(path)
    sig = _file_signature(path)
    return {
        "parse_status": "DWG_BINARY_METADATA_ONLY",
        "signature": sig,
        "file_size": p.stat().st_size if p.exists() else 0,
        "note": "DWG binary parsed as metadata only. For geometry extraction install ODAFileConverter or dwg2dxf on server; DXF is parsed directly",
    }

def _build_model(local_path: str, file_name: str, mime_type: str = "", user_text: str = "", topic_role: str = "") -> Dict[str, Any]:
    p = Path(local_path)
    ext = p.suffix.lower()
    source_path = str(p)
    converted_from_dwg = False

    if ext == ".dwg":
        converted = _try_convert_dwg_to_dxf(local_path)
        if converted:
            source_path = converted
            ext = ".dxf"
            converted_from_dwg = True

    if ext == ".dxf":
        parsed = _parse_ascii_dxf(source_path)
    elif p.suffix.lower() == ".dwg":
        parsed = _parse_dwg_metadata(local_path)
    else:
        parsed = {
            "parse_status": "UNSUPPORTED_DRAWING_FORMAT",
            "signature": _file_signature(local_path),
            "file_size": p.stat().st_size if p.exists() else 0,
        }

    drawing_text = "\n".join(parsed.get("texts") or [])
    section = _detect_section(file_name, user_text, drawing_text)
    entity_counts = parsed.get("entity_counts") or {}
    layers = parsed.get("layers") or {}
    texts = parsed.get("texts") or []

    output_documents = [
        "DOCX_DWG_DXF_ANALYSIS_REPORT",
        "XLSX_DWG_DXF_ENTITY_REGISTER",
        "ZIP_PROJECT_PACKAGE",
    ]

    if section in ("кж", "км", "кмд", "кр"):
        output_documents.extend(["SPECIFICATION_DRAFT", "STRUCTURAL_DRAWING_REGISTER"])
    if section == "ар":
        output_documents.extend(["ARCHITECTURAL_SHEET_REGISTER", "ROOM_PLAN_REVIEW"])

    risk_flags = []
    if parsed.get("parse_status") == "DWG_BINARY_METADATA_ONLY":
        risk_flags.append("DWG_GEOMETRY_NOT_EXTRACTED_WITHOUT_CONVERTER")
    if not layers:
        risk_flags.append("LAYERS_NOT_FOUND")
    if not entity_counts:
        risk_flags.append("ENTITIES_NOT_FOUND")
    if not texts:
        risk_flags.append("TEXT_LABELS_NOT_FOUND")

    model = {
        "schema": "DWG_DXF_PROJECT_MODEL_V1",
        "source_file": file_name or p.name,
        "source_path": local_path,
        "mime_type": mime_type,
        "topic_role": topic_role,
        "user_text": user_text,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "section": section,
        "section_title": SECTION_MAP.get(section, section.upper()),
        "norms": NORMS_MAP.get(section, []),
        "converted_from_dwg": converted_from_dwg,
        "parse": parsed,
        "layers": layers,
        "entity_counts": entity_counts,
        "texts": texts[:80],
        "dimensions_detected": parsed.get("dimensions_detected") or [],
        "extents": parsed.get("extents") or {},
        "output_documents": output_documents,
        "risk_flags": risk_flags,
        "status": "PARTIAL" if risk_flags else "CONFIRMED",
    }
    return model

def _summary(model: Dict[str, Any]) -> str:
    parse = model.get("parse") or {}
    entity_counts = model.get("entity_counts") or {}
    layers = model.get("layers") or {}
    risk_flags = model.get("risk_flags") or []
    lines = [
        "DWG/DXF проектный контур отработал",
        f"Файл: {model.get('source_file')}",
        f"Раздел: {model.get('section_title')}",
        f"Статус: {model.get('status')}",
        f"Parse: {parse.get('parse_status')}",
        f"Слоёв: {len(layers)}",
        f"Сущностей: {sum(int(v) for v in entity_counts.values()) if entity_counts else 0}",
    ]
    if entity_counts:
        lines.append("Типы сущностей: " + ", ".join(f"{k}:{v}" for k, v in list(entity_counts.items())[:12]))
    if layers:
        lines.append("Слои: " + ", ".join(list(layers.keys())[:20]))
    if model.get("dimensions_detected"):
        lines.append("Размеры/числа из подписей: " + ", ".join(map(str, model.get("dimensions_detected")[:30])))
    if model.get("norms"):
        lines.append("Нормы: " + ", ".join(model.get("norms")))
    if risk_flags:
        lines.append("Ограничения: " + ", ".join(risk_flags))
    lines.append("Артефакты: DOCX отчёт + XLSX реестр + ZIP пакет")
    return "\n".join(lines).strip()

def _write_docx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"dwg_dxf_report_{_safe_name(task_id, 'manual')}.docx"
    try:
        from docx import Document

        doc = Document()
        doc.add_heading("DWG/DXF PROJECT MODEL", level=1)
        doc.add_paragraph(f"Файл: {model.get('source_file')}")
        doc.add_paragraph(f"Раздел: {model.get('section_title')}")
        doc.add_paragraph(f"Статус: {model.get('status')}")
        doc.add_paragraph(f"Parse: {(model.get('parse') or {}).get('parse_status')}")

        doc.add_heading("Нормативная база", level=2)
        norms = model.get("norms") or []
        if norms:
            for n in norms:
                doc.add_paragraph(f"• {n}")
        else:
            doc.add_paragraph("Норма не подтверждена")

        doc.add_heading("Слои", level=2)
        layers = model.get("layers") or {}
        if layers:
            table = doc.add_table(rows=1, cols=2)
            table.style = "Table Grid"
            table.rows[0].cells[0].text = "Слой"
            table.rows[0].cells[1].text = "Кол-во"
            for name, cnt in list(layers.items())[:80]:
                row = table.add_row().cells
                row[0].text = str(name)
                row[1].text = str(cnt)
        else:
            doc.add_paragraph("Слои не извлечены")

        doc.add_heading("Сущности", level=2)
        ents = model.get("entity_counts") or {}
        if ents:
            table = doc.add_table(rows=1, cols=3)
            table.style = "Table Grid"
            table.rows[0].cells[0].text = "Тип"
            table.rows[0].cells[1].text = "Кол-во"
            table.rows[0].cells[2].text = "Назначение"
            for name, cnt in list(ents.items())[:80]:
                row = table.add_row().cells
                row[0].text = str(name)
                row[1].text = str(cnt)
                row[2].text = ENTITY_PROJECT_HINTS.get(str(name), "")
        else:
            doc.add_paragraph("Сущности не извлечены")

        doc.add_heading("Текстовые подписи", level=2)
        texts = model.get("texts") or []
        if texts:
            for t in texts[:60]:
                doc.add_paragraph(f"• {t}")
        else:
            doc.add_paragraph("Текстовые подписи не извлечены")

        doc.add_heading("Проектные выходные документы", level=2)
        for x in model.get("output_documents") or []:
            doc.add_paragraph(f"• {x}")

        doc.add_heading("Ограничения", level=2)
        risks = model.get("risk_flags") or []
        if risks:
            for r in risks:
                doc.add_paragraph(f"• {r}")
        else:
            doc.add_paragraph("Критичных ограничений не выявлено")

        doc.save(out)
        return str(out)
    except Exception:
        txt = out.with_suffix(".txt")
        txt.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(txt)

def _write_xlsx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"dwg_dxf_register_{_safe_name(task_id, 'manual')}.xlsx"
    try:
        from openpyxl import Workbook
        wb = Workbook()

        ws = wb.active
        ws.title = "Summary"
        rows = [
            ("Файл", model.get("source_file")),
            ("Раздел", model.get("section_title")),
            ("Статус", model.get("status")),
            ("Parse", (model.get("parse") or {}).get("parse_status")),
            ("Нормы", ", ".join(model.get("norms") or [])),
            ("Ограничения", ", ".join(model.get("risk_flags") or [])),
        ]
        for i, (k, v) in enumerate(rows, 1):
            ws.cell(i, 1, k)
            ws.cell(i, 2, v)

        ws2 = wb.create_sheet("Layers")
        ws2.append(["Слой", "Кол-во"])
        for k, v in (model.get("layers") or {}).items():
            ws2.append([k, v])

        ws3 = wb.create_sheet("Entities")
        ws3.append(["Тип", "Кол-во", "Назначение"])
        for k, v in (model.get("entity_counts") or {}).items():
            ws3.append([k, v, ENTITY_PROJECT_HINTS.get(str(k), "")])

        ws4 = wb.create_sheet("Texts")
        ws4.append(["№", "Текст"])
        for i, t in enumerate(model.get("texts") or [], 1):
            ws4.append([i, t])

        ws5 = wb.create_sheet("ModelJSON")
        raw = json.dumps(model, ensure_ascii=False, indent=2)
        for i, line in enumerate(raw.splitlines(), 1):
            ws5.cell(i, 1, line)

        wb.save(out)
        wb.close()
        return str(out)
    except Exception:
        csv = out.with_suffix(".csv")
        lines = ["key,value"]
        lines.append(f"file,{model.get('source_file')}")
        lines.append(f"section,{model.get('section_title')}")
        lines.append(f"status,{model.get('status')}")
        csv.write_text("\n".join(lines), encoding="utf-8")
        return str(csv)

def _write_json(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"dwg_dxf_model_{_safe_name(task_id, 'manual')}.json"
    out.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out)

def _zip_artifacts(paths: List[str], task_id: str, source_file: str = "") -> str:
    out = Path(tempfile.gettempdir()) / f"dwg_dxf_project_package_{_safe_name(task_id, 'manual')}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p and os.path.exists(p):
                z.write(p, arcname=os.path.basename(p))
        manifest = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "task_id": task_id,
            "source_file": source_file,
            "files": [os.path.basename(p) for p in paths if p and os.path.exists(p)],
            "engine": "DWG_DXF_PROJECT_CLOSE_V1",
        }
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return str(out)

def process_drawing_file(
    local_path: str,
    file_name: str = "",
    mime_type: str = "",
    user_text: str = "",
    topic_role: str = "",
    task_id: str = "artifact",
    topic_id: int = 0,
) -> Dict[str, Any]:
    if not local_path or not os.path.exists(local_path):
        return {
            "success": False,
            "error": "DRAWING_FILE_NOT_FOUND",
            "summary": "DWG/DXF файл не найден",
        }

    model = _build_model(local_path, file_name or os.path.basename(local_path), mime_type, user_text, topic_role)
    docx = _write_docx(model, task_id)
    xlsx = _write_xlsx(model, task_id)
    js = _write_json(model, task_id)
    package = _zip_artifacts([docx, xlsx, js], task_id, model.get("source_file") or file_name)

    return {
        "success": True,
        "engine": "DWG_DXF_PROJECT_CLOSE_V1",
        "summary": _summary(model),
        "model": model,
        "docx_path": docx,
        "xlsx_path": xlsx,
        "json_path": js,
        "artifact_path": package,
        "artifact_name": f"{Path(file_name or local_path).stem}_dwg_dxf_project_package.zip",
        "extra_artifacts": [docx, xlsx, js],
        "status": model.get("status"),
    }

async def process_drawing_file_async(*args, **kwargs) -> Dict[str, Any]:
    return process_drawing_file(*args, **kwargs)

# === END_DWG_DXF_PROJECT_CLOSE_V1 ===

====================================================================================================
END_FILE: core/dwg_engine.py
FILE_CHUNK: 1/1
====================================================================================================

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
