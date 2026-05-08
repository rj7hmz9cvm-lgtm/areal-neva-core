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
        raw, res,
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

    # For direct file tasks with no local path: use bot-api fallback scoped to recent
    if input_type in ("drive_file", "file", "photo", "document") and not paths:
        for p in _recent_bot_api_pdfs(limit=3) + _recent_runtime_pdfs(limit=3):
            if p.exists():
                paths.append(p)

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
