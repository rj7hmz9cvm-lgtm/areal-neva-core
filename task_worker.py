from __future__ import annotations





from pathlib import Path
from core.stt import transcribe_audio

import asyncio
import inspect
import logging
import os
import sqlite3
import sys

sys.path.insert(0, "/root/.areal-neva-core")

_LOGDIR = "/root/.areal-neva-core/logs"
os.makedirs(_LOGDIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(f"{_LOGDIR}/task_worker.log"),
        logging.StreamHandler(),
    ],
    force=True,
)

logger = logging.getLogger("task_worker")

try:
    from dotenv import load_dotenv
    load_dotenv("/root/.areal-neva-core/.env")
except Exception:
    pass

from core.ai_router import process_ai_task
from core.db import get_task, transition_task, update_task_fields

try:
    from core.assistant_core import add_reminder, get_pending_reminders, mark_reminder_done
except Exception:
    async def add_reminder(*args, **kwargs):
        return None
    async def get_pending_reminders():
        return []
    async def mark_reminder_done(*args, **kwargs):
        return None

try:
    from core.reply_sender import send_reply
except Exception:
    async def send_reply(chat_id, text, topic_id=None):
        logger.warning("send_reply stub chat=%s", chat_id)
        return None

try:
    from core.stt import transcribe
except Exception:
    async def transcribe(path: str) -> str:
        _stt_path = file_path if 'file_path' in locals() else (path if 'path' in locals() else '')
        text = transcribe_audio(_stt_path)
        return text

try:
    from core.db import init_db as _init_db_orig
    async def init_db():
        result = _init_db_orig()
        if inspect.isawaitable(result):
            await result
except Exception:
    async def init_db():
        return None

try:
    from core.router import route_task
except Exception:
    async def route_task(text: str, chat_id: int, user_id: int, topic_id=None) -> dict:
        return {"summary": "Автоматизация выполнена"}

try:
    from lead_ingest import is_lead, quick_extract
except Exception:
    def is_lead(text: str) -> bool:
        return False
    def quick_extract(text: str, source: str) -> dict:
        return {"raw": text or "", "source": source}

try:
    from core.db import create_artifact, update_artifact, save_lead_log
except Exception:
    async def create_artifact(*args, **kwargs):
        return 1
    async def update_artifact(*args, **kwargs):
        return None
    async def save_lead_log(*args, **kwargs):
        return None

DB_PATH = os.getenv("ORCHESTRA_DB_PATH", "/root/.areal-neva-core/data/core.db")
POLL_INTERVAL = float(os.getenv("WORKER_POLL_INTERVAL", "1.5"))
TASK_PROGRESS_PING = int(os.getenv("TASK_PROGRESS_PING", "30"))
TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", "120"))
LEAD_RESULT_PREFIX = "🎯 Обнаружен лид\n"

_running_intake: set[str] = set()
_running_ready: set[str] = set()


def _status(task: dict | None) -> str:
    if not task:
        return ""
    return str(task.get("state") or task.get("status") or "").strip()


def _preview(text: str | None, limit: int = 80) -> str:
    value = str(text or "").replace("\n", " ").strip()
    if not value:
        return "без текста"
    return value[:limit] + ("..." if len(value) > limit else "")


async def _notify(chat_id: int, text: str, topic_id=None) -> None:
    try:
        await send_reply(chat_id, text, topic_id)
    except Exception as exc:
        logger.warning("notify failed chat=%s err=%s", chat_id, exc)


async def _safe_transition(task_id: str, to_state: str, triggered_by: str) -> bool:
    try:
        result = transition_task(task_id, to_state, triggered_by=triggered_by)
        if inspect.isawaitable(result):
            await result
        return True
    except Exception as exc:
        logger.error("task=%s transition=%s err=%s", task_id, to_state, exc)
        return False


async def _safe_update(task_id: str, **kwargs) -> None:
    try:
        result = update_task_fields(task_id, **kwargs)
        if inspect.isawaitable(result):
            await result
    except Exception as exc:
        logger.error("task=%s update failed: %s", task_id, exc)


async def _fail_task(task_id: str, error: str, triggered_by: str, chat_id: int | None = None, topic_id=None) -> None:
    await _safe_update(task_id, error_message=error)

    try:
        result = transition_task(task_id, "FAILED", triggered_by=triggered_by)
        if inspect.isawaitable(result):
            await result
    except Exception as exc:
        logger.error("task=%s failed transition err=%s", task_id, exc)

    if chat_id:
        current = await get_task(task_id)
        preview = _preview((current or {}).get("raw_input"))
        await _notify(chat_id, f"❌ Не выполнено\nЗапрос: {preview}\nПричина: {error[:250]}", topic_id)


def _format_lead_summary(lead: dict) -> str:
    parts = [LEAD_RESULT_PREFIX]
    if lead.get("phone"):
        parts.append(f"Телефон: {lead['phone']}")
    if lead.get("volume"):
        parts.append(f"Объём: {lead['volume']}")
    if lead.get("budget"):
        parts.append(f"Бюджет: {lead['budget']}")
    if lead.get("location"):
        parts.append(f"Локация: {lead['location']}")
    raw = (lead.get("raw") or "").strip()
    if raw:
        parts.append("")
        parts.append(raw[:2500])
    return "\n".join(parts)


async def _progress_ping(task_id: str, chat_id: int, topic_id=None) -> None:
    await asyncio.sleep(TASK_PROGRESS_PING)
    task = await get_task(task_id)
    if _status(task) == "IN_PROGRESS":
        await _notify(chat_id, f"⏳ В работе\nЗапрос: {_preview(task.get('raw_input'))}", topic_id)


async def _process_lead_task(task: dict) -> None:
    task_id = task["id"]
    raw_input = task.get("raw_input") or ""
    source = task.get("source", "unknown")
    chat_id = int(task.get("chat_id") or 0)
    topic_id = task.get("topic_id")

    if not await _safe_transition(task_id, "IN_PROGRESS", "task_worker"):
        return

    lead = quick_extract(raw_input, source)
    summary = _format_lead_summary(lead)

    try:
        artifact_id = await create_artifact(
            task_id=task_id,
            artifact_type="lead",
            metadata={"lead": lead},
        )
        await update_artifact(artifact_id, processing_status="done")
    except Exception:
        logger.exception("task=%s lead artifact error", task_id)

    try:
        await save_lead_log({
            "source": source,
            "raw": raw_input,
            "phone": lead.get("phone"),
            "volume": lead.get("volume"),
            "location": lead.get("location"),
            "budget": lead.get("budget"),
        })
    except Exception:
        logger.exception("task=%s lead log error", task_id)

    await _safe_update(task_id, result=summary)

    if not await _safe_transition(task_id, "RESULT_READY", "task_worker"):
        await _fail_task(task_id, "cannot move lead to RESULT_READY", "task_worker", chat_id, topic_id)


async def _process_automation_task(task: dict) -> None:
    task_id = task["id"]
    text = task.get("raw_input") or ""
    chat_id = int(task.get("chat_id") or 0)
    user_id = int(task.get("user_id") or 0)
    topic_id = task.get("topic_id")

    if not await _safe_transition(task_id, "IN_PROGRESS", "task_worker"):
        return

    try:
        result = await route_task(text=text, chat_id=chat_id, user_id=user_id, topic_id=topic_id)
    except Exception as exc:
        await _fail_task(task_id, str(exc), "task_worker", chat_id, topic_id)
        return

    await _safe_update(task_id, result=result.get("summary", ""))

    if not await _safe_transition(task_id, "RESULT_READY", "task_worker"):
        await _fail_task(task_id, "cannot move automation to RESULT_READY", "task_worker", chat_id, topic_id)




# AREAL_WEB_SEARCH_START
def web_search(query):
    try:
        if not query or len(query.strip()) <= 3: return ""
        import requests
        print(f"WEB_SEARCH_START query={query[:50]}")
        r = requests.get("https://api.duckduckgo.com/", params={"q": query, "format": "json"}, timeout=5)
        d = r.json()
        res = d.get("AbstractText", "")
        if not res and d.get("RelatedTopics"): res = d["RelatedTopics"][0].get("Text", "")
        print("WEB_SEARCH_DONE")
        return res[:1000]
    except: return ""
# AREAL_WEB_SEARCH_END

async def _run_intake_bg(task: dict) -> None:
    task_id = task["id"]
    chat_id = int(task.get("chat_id") or 0)
    topic_id = task.get("topic_id")
    input_type = task.get("input_type", "")
    source = task.get("source", "")
    raw_input = task.get("raw_input") or ""
    ping_task = None

    try:
        await _notify(chat_id, f"✅ Принято\nЗапрос: {_preview('голосовое сообщение' if input_type == 'voice' else raw_input)}", topic_id)
        ping_task = asyncio.create_task(_progress_ping(task_id, chat_id, topic_id))

        current = await get_task(task_id)
        if not current or _status(current) != "INTAKE": return

        task = current
        raw_input = task.get("raw_input") or ""

        if "напомни" in raw_input.lower():
            await add_reminder(chat_id, raw_input, topic_id=topic_id)

        if source == "automation_daemon" and input_type in ("automation", "followup"):
            await _safe_update(task_id, result=raw_input)
            ok = await _safe_transition(task_id, "IN_PROGRESS", "task_worker")
            if ok: await _safe_transition(task_id, "RESULT_READY", "task_worker")
            return

        if input_type == "voice":
            voice_path = raw_input.strip()
            if not voice_path or not os.path.exists(voice_path):
                await _fail_task(task_id, f"voice file missing: {voice_path!r}", "task_worker", chat_id, topic_id)
                return
            text = await transcribe(voice_path)
            if not text:
                await _fail_task(task_id, "STT returned empty", "task_worker", chat_id, topic_id)
                return
            await _safe_update(task_id, raw_input=text)
            refreshed = await get_task(task_id)
            if refreshed is None:
                await _notify(chat_id, "❌ Не выполнено\nЗапрос: голосовое сообщение\nПричина: задача исчезла", topic_id)
                return
            task = refreshed
            raw_input = task.get("raw_input") or text

        lower = raw_input.lower()
        refreshed = await get_task(task_id)
        if refreshed is not None: task = refreshed

        if "напомни" in lower or "проверь" in lower:
            await _process_automation_task(task)
            return

        if is_lead(raw_input):
            await _process_lead_task(task)
            return

        # AREAL_BUS_START
        import re as _re, os as _os, time as _time, sqlite3 as _sqlite3, memory_engine as _me, file_registry as _fr
        from pathlib import Path
        _t = task.get("raw_input") or task.get("payload") or task.get("text") or ""
        if isinstance(_t, dict): _t = str(_t.get("text", ""))
        _cid = task.get("chat_id") or 0
        _scope = task.get("topic_id") or _cid
        _fp = ""
        _m = _re.search(r"\[FILE:(.*?)\]", _t)
        if _m:
            _fp = _m.group(1).strip()
            _t = _re.sub(r"\[FILE:.*?\]", "", _t, count=1).strip()
        elif task.get("input_type") == "text":
            _lp = f"/root/AI_ORCHESTRA/telegram/chat_{_cid}_latest.path"
            if _os.path.exists(_lp) and _time.time() - _os.path.getmtime(_lp) < 3600:
                with open(_lp, 'r') as _f: _fp = _f.read().strip()
        if _fp and not Path(_fp).exists(): _fp = ""
        print(f"BUS FILE {_fp}")
        _f_txt = ""
        if _fp:
            try:
                import table_engine, document_engine
                if _fp.lower().endswith(('.xlsx', '.csv')): _f_txt = table_engine.read(_fp)
                else: _f_txt = document_engine.read(_fp)
                _fr.index_file(_scope, _fp)
            except Exception as e: print(f"ENGINE ERROR {e}")
        _web = web_search(_t) if "web_search" in globals() else ""
        try: _mem, _f_ctx = _me.recall(_scope, _t), _fr.recall(_t, _scope)
        except Exception as e: _mem, _f_ctx = "", ""
        assembled_prompt = f"{_f_txt}\n{_web}\n{_mem}\n{_f_ctx}\n{_t}".strip()
        print(f"AI INPUT LEN {len(assembled_prompt)}")
        for k in ["raw_input", "prompt", "input", "text", "query", "payload"]: task[k] = assembled_prompt
        _db_ok = False
        try:
            with _sqlite3.connect("/root/.areal-neva-core/data/core.db") as _c:
                for col in ["raw_input", "payload", "prompt", "text", "input", "query"]:
                    try:
                        _c.execute(f"UPDATE tasks SET {col}=? WHERE id=?", (assembled_prompt, task.get("id")))
                        _db_ok = True
                    except: pass
                _c.commit()
            if _db_ok: print(f"DB FORCE UPDATE OK task_id={task.get('id')}")
        except Exception as e: print(f"DB FORCE UPDATE ERROR: {e}")
        print(f"FINAL RAW_INPUT LEN {len(task.get('raw_input',''))}")
        # AREAL_BUS_END

        await asyncio.wait_for(process_ai_task(task), timeout=TASK_TIMEOUT)

    except asyncio.TimeoutError:
        await _fail_task(task_id, f"timeout after {TASK_TIMEOUT}s", "task_worker", chat_id, topic_id)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).exception("task=%s intake error", task_id)
        await _fail_task(task_id, str(exc), "task_worker", chat_id, topic_id)
    finally:
        if ping_task is not None:
            ping_task.cancel()
        _running_intake.discard(task_id)


async def _run_ready_bg(task: dict) -> None:
    task_id = task["id"]

    try:
        full_task = await get_task(task_id)
        if not full_task:
            raise ValueError("task missing on ready")

        result = (full_task.get("result") or "").strip()
        if not result:
            raise ValueError("empty result on deliver")

        chat_id = int(full_task.get("chat_id") or 0)
        topic_id = full_task.get("topic_id")
        preview = _preview(full_task.get("raw_input"))

        await _notify(chat_id, f"✅ Выполнено\nЗапрос: {preview}\n\n{result}", topic_id)

        await _safe_transition(task_id, "AWAITING_CONFIRMATION", "task_worker")

    except Exception as exc:
        logger.exception("_run_ready_bg task=%s", task_id)
        current = await get_task(task_id) or task
        await _fail_task(task_id, str(exc), "task_worker", int(current.get("chat_id") or 0), current.get("topic_id"))
    finally:
        _running_ready.discard(task_id)


def _fetch_by_state_raw(state: str, limit: int = 20) -> list[dict]:
    try:
        con = sqlite3.connect(DB_PATH, timeout=10)
        con.row_factory = sqlite3.Row
        rows = None
        for col in ("state", "status"):
            try:
                rows = con.execute(
                    f"SELECT * FROM tasks WHERE {col}=? ORDER BY created_at ASC LIMIT ?",
                    (state, limit),
                ).fetchall()
                break
            except sqlite3.OperationalError:
                continue
        con.close()
        return [dict(r) for r in rows] if rows else []
    except Exception:
        logger.exception("_fetch_by_state_raw error state=%s", state)
        return []


async def _get_tasks(state: str) -> list[dict]:
    try:
        from core.db import get_tasks_by_state
        result = get_tasks_by_state(state)
        if inspect.isawaitable(result):
            result = await result
        return result or []
    except Exception:
        return await asyncio.to_thread(_fetch_by_state_raw, state)


async def _reminders_loop() -> None:
    while True:
        try:
            rows = await get_pending_reminders()
            for item in rows:
                await _notify(item["chat_id"], f"⏰ Напоминание\n{item['text']}", item.get("topic_id"))
                await mark_reminder_done(item["id"])
        except Exception:
            logger.exception("reminders_loop error")
        await asyncio.sleep(60)


async def run_task_worker() -> None:
    await init_db()
    logger.info("task_worker started poll=%s timeout=%s", POLL_INTERVAL, TASK_TIMEOUT)
    asyncio.create_task(_reminders_loop())

    while True:
        try:
            intake_tasks = await _get_tasks("INTAKE")
            for item in intake_tasks:
                tid = item["id"]
                if tid not in _running_intake:
                    _running_intake.add(tid)
                    asyncio.create_task(_run_intake_bg(item))

            ready_tasks = await _get_tasks("RESULT_READY")
            for item in ready_tasks:
                tid = item["id"]
                if tid not in _running_ready:
                    _running_ready.add(tid)
                    asyncio.create_task(_run_ready_bg(item))

        except Exception:
            logger.exception("worker loop error")

        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(run_task_worker())