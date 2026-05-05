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

# === FIX_PIC_CLARIFICATION_FRESH_REQUEST_V1 ===
# _pic_is_clarification_text fires on "актуальн*" and "интернет*" — both clar_words.
# But "сколько будет стоить" / "мне надо посчитать" are fresh requests, not clarifications.
_fpcfr_orig = _pic_is_clarification_text

def _pic_is_clarification_text(text: str) -> bool:
    low = _low(text)
    if not low:
        return False
    fresh_request = any(x in low for x in (
        "сколько будет стоить", "сколько стоит", "посчитать работу",
        "мне надо посчитать", "нужно посчитать", "помоги посчитать",
        "помоги рассчитать", "нужна смета", "нужна полная смета",
        "добрый день", "привет", "здравствуй",
        "можешь ли", "сможешь ли", "сможешь или нет",
    ))
    if fresh_request:
        return False
    return _fpcfr_orig(text)
# === END_FIX_PIC_CLARIFICATION_FRESH_REQUEST_V1 ===

