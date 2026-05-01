import json
import asyncio, hashlib, json, logging, os, re, uuid, fcntl, tempfile, time
from datetime import datetime, timezone, timedelta
import aiofiles, aiohttp, aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.types import BufferedInputFile, FSInputFile
from google_io import upload_to_drive
from core.drive_folder_resolver import get_or_create_topic_folder
from core.topic_drive_oauth import upload_file_to_topic

BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
DB = "/root/.areal-neva-core/data/core.db"
VOICE_DIR = "/root/.areal-neva-core/runtime/voice_queue"
MEMORY_FILES = "/root/.areal-neva-core/data/memory_files"
CHAT_MAP_FILE = os.path.join(MEMORY_FILES, "CHAT_MAP.json")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN missing")

for d in ["GLOBAL", "CHATS", "SYSTEM", "ERRORS"]:
    os.makedirs(os.path.join(MEMORY_FILES, d), exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s DAEMON: %(message)s")
logger = logging.getLogger("telegram_daemon")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

SYSTEM_CMDS = ["память", "память оркестра", "выгрузи память", "статус", "архив", "сброс задач", "очистить задачи", "yzon", "дамп", "язон", "язон файл", "дамп файл", "память файл", "архив файл", "система", "система файл", "код файл", "файл"]
CANCEL_CMDS = ["отбой", "отмена", "не надо"]
EZONE_KEYS = ("system", "architecture", "pipeline", "memory")
EZONE_EXTS = (".json", ".jsonl", ".txt")
SEARCH_TRIGGERS = ["цена", "наличие", "где купить", "площадка", "сайт", "сравнение", "новости", "актуальная"]
SHORT_CONFIRM = ["да", "нет", "ок", "подтверждаю", "не так", "ага", "верно"]
NEGATIVE_CONFIRM = ["нет", "не так"]
FINISH_PHRASES = [
    "спасибо поиск завершен", "поиск завершен",
    "не надо", "можно завершать",
    "задача закрыта", "закрывай", "хватит"
]
CANCEL_PHRASES = [
    "все запросы отменены", "отменяю все запросы", "сброс задач",
    "очистить задачи", "отмена", "отменяю", "сброс", "отбой"
]

_RECENT_INGEST = {}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def normalize_json_text(text: str) -> str:
    if not text: return text
    replacements = {"“": '"', "”": '"', "„": '"', "«": '"', "»": '"', "‘": "'", "’": "'", "…": "..."}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()

def is_ezone_payload(text: str) -> bool:
    if not text: return False
    norm = normalize_json_text(text)
    try:
        data = json.loads(norm)
        return isinstance(data, dict) and any(k in data for k in EZONE_KEYS)
    except:
        low = norm.lower()
        return any(k in low for k in EZONE_KEYS)

def content_hash(text: str) -> str:
    return hashlib.sha256(normalize_json_text(text).encode()).hexdigest()

def build_chat_key(telegram_chat_id: int) -> str:
    return f"{telegram_chat_id}__telegram"

def update_chat_map_atomic(telegram_chat_id: int, chat_key: str):
    lock_file = CHAT_MAP_FILE + ".lock"
    try:
        with open(lock_file, "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                chat_map = json.load(open(CHAT_MAP_FILE)) if os.path.exists(CHAT_MAP_FILE) else {}
                tg_id = str(telegram_chat_id)
                if tg_id not in chat_map:
                    chat_map[tg_id] = {}
                elif isinstance(chat_map[tg_id], list):
                    chat_map[tg_id] = {k: "unknown" for k in chat_map[tg_id]}
                chat_map[tg_id] = {k: v for k, v in chat_map[tg_id].items() if "unknown" not in k}
                chat_map[tg_id][chat_key] = "telegram"
                fd, tmp = tempfile.mkstemp(dir=os.path.dirname(CHAT_MAP_FILE), prefix=".chat_map_", suffix=".tmp")
                with os.fdopen(fd, "w") as f:
                    json.dump(chat_map, f, ensure_ascii=False, indent=2)
                    f.flush(); os.fsync(f.fileno())
                os.replace(tmp, CHAT_MAP_FILE)
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)
    except Exception as e:
        logger.error("CHAT_MAP update failed: %s", e)
    finally:
        try: os.unlink(lock_file)
        except: pass

def is_duplicate_today(hash_val: str, chat_key: str) -> bool:
    dup_file = os.path.join(MEMORY_FILES, "CHATS", chat_key, ".duplicates.jsonl")
    today = today_key()
    if os.path.exists(dup_file):
        with open(dup_file) as f:
            for line in f:
                try:
                    if json.loads(line).get("hash") == hash_val and json.loads(line).get("date") == today:
                        return True
                except: pass
    os.makedirs(os.path.dirname(dup_file), exist_ok=True)
    with open(dup_file, "a") as f:
        f.write(json.dumps({"hash": hash_val, "date": today, "ts": now_iso()}) + "\n")
    return False

def save_ezone_json(text: str, telegram_chat_id: int) -> tuple:
    norm = normalize_json_text(text)
    try: data = json.loads(norm)
    except: data = {"raw_text": norm}
    if not isinstance(data, dict): data = {"raw_text": norm}
    
    chat_key = build_chat_key(telegram_chat_id)
    ts = now_iso()
    hash_val = content_hash(text)
    
    if is_duplicate_today(hash_val, chat_key):
        return False, chat_key, "duplicate"
    
    data["_meta"] = {"chat_key": chat_key, "ingested_at": ts, "source": "telegram"}
    chat_dir = os.path.join(MEMORY_FILES, "CHATS", chat_key)
    os.makedirs(chat_dir, exist_ok=True)
    
    with open(os.path.join(chat_dir, "raw.json"), "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    entry = json.dumps({"timestamp": ts, "data": data}, ensure_ascii=False)
    with open(os.path.join(chat_dir, "timeline.jsonl"), "a") as f:
        f.write(entry + "\n")
    with open(os.path.join(MEMORY_FILES, "GLOBAL", "timeline.jsonl"), "a") as f:
        f.write(json.dumps({"timestamp": ts, "chat_key": chat_key, "data": data}, ensure_ascii=False) + "\n")
    
    for key in EZONE_KEYS:
        if key in data:
            with open(os.path.join(MEMORY_FILES, "SYSTEM", f"{key}.jsonl"), "a") as f:
                f.write(json.dumps({"timestamp": ts, "chat_key": chat_key, "data": data[key]}, ensure_ascii=False) + "\n")
    
    update_chat_map_atomic(telegram_chat_id, chat_key)
    logger.info("eZone saved: chat_key=%s telegram_chat=%s", chat_key, telegram_chat_id)
    return True, chat_key, ""


def dump_yzon_state(chat_id: int) -> str:
    import sqlite3, json

    result = {
        "system": {"name": "AREAL-NEVA ORCHESTRA", "role": "task execution system"},
        "architecture": {
            "pipeline": "telegram_daemon -> task_worker -> ai_router -> reply_sender",
            "memory": "memory.db + memory_files",
            "storage": "Google Drive",
            "mode": "server-first"
        },
        "runtime": {
            "chat_id": str(chat_id),
            "has_active_task": False,
            "has_active_pin": False,
            "daemon": "running",
            "worker": "running"
        },
        "active_context": {},
        "recent_results": [],
        "recent_decisions": []
    }

    try:
        conn = sqlite3.connect("/root/.areal-neva-core/data/core.db")

        cur = conn.execute(
            "SELECT id, state, raw_input FROM tasks WHERE chat_id = ? AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION') ORDER BY created_at DESC LIMIT 1",
            (str(chat_id),)
        )
        row = cur.fetchone()
        if row:
            result["runtime"]["has_active_task"] = True
            result["active_context"]["task_id"] = row[0]
            result["active_context"]["state"] = row[1]
            result["active_context"]["input"] = row[2][:200] if row[2] else ""

        cur = conn.execute(
            "SELECT task_id FROM pin WHERE chat_id = ? AND state = 'ACTIVE' ORDER BY updated_at DESC LIMIT 1",
            (str(chat_id),)
        )
        pin_row = cur.fetchone()
        if pin_row:
            result["runtime"]["has_active_pin"] = True
            result["active_context"]["active_pin"] = pin_row[0]

        cur = conn.execute(
            "SELECT id, result FROM tasks WHERE chat_id = ? AND state = 'DONE' AND result IS NOT NULL ORDER BY updated_at DESC LIMIT 5",
            (str(chat_id),)
        )
        for row in cur.fetchall():
            result["recent_results"].append({"task_id": row[0], "summary": row[1][:200] if row[1] else ""})

        cur = conn.execute(
            "SELECT task_id, action FROM task_history WHERE task_id IN (SELECT id FROM tasks WHERE chat_id = ?) ORDER BY created_at DESC LIMIT 10",
            (str(chat_id),)
        )
        for row in cur.fetchall():
            result["recent_decisions"].append({"task_id": row[0], "action": row[1]})

        conn.close()
    except Exception as e:
        result["error"] = str(e)

    return json.dumps(result, ensure_ascii=False, indent=2)


def dump_system_state() -> str:
    import sqlite3, json, os
    from datetime import datetime, timezone

    result = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "chat_id": None,
        "active_task": None,
        "active_pin": None,
        "recent_results": [],
        "architecture": {
            "system": "AREAL-NEVA ORCHESTRA",
            "stack": "telegram_daemon + task_worker + ai_router + OpenRouter",
            "memory": "memory_files + memory.db",
            "files": "Google Drive via google_io"
        }
    }

    try:
        conn = sqlite3.connect("/root/.areal-neva-core/data/core.db")
        cur = conn.execute("SELECT id, state, raw_input FROM tasks WHERE chat_id = '-1003725299009' AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION') ORDER BY created_at DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            result["chat_id"] = "-1003725299009"
            result["active_task"] = {"id": row[0], "state": row[1], "input": row[2][:200]}
        
        cur = conn.execute("SELECT task_id FROM pin WHERE chat_id = '-1003725299009' AND state = 'ACTIVE' ORDER BY updated_at DESC LIMIT 1")
        pin_row = cur.fetchone()
        if pin_row:
            result["active_pin"] = pin_row[0]
        
        cur = conn.execute("SELECT id, result FROM tasks WHERE chat_id = '-1003725299009' AND state = 'DONE' AND result IS NOT NULL ORDER BY updated_at DESC LIMIT 20")
        for row in cur.fetchall():
            result["recent_results"].append({"task_id": row[0], "summary": row[1][:200]})
        
        conn.close()
    except Exception as e:
        result["error"] = str(e)

    return json.dumps(result, ensure_ascii=False, indent=2)

def split_message(text: str, limit: int = 4000) -> list:
    text = text or ""
    parts = []
    while text and len(parts) < 10:
        if len(text) <= limit:
            parts.append(text); break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1 or split_at < limit // 3:
            split_at = limit
        parts.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return parts or [""]

async def create_task(message: types.Message, input_type: str, raw_input: str, state: str = "NEW"):
    task_id = str(uuid.uuid4())
    now = now_iso()
    user_id = getattr(message.from_user, "id", 0) if message.from_user else 0
    topic_id = getattr(message, "message_thread_id", None) or 0
    async with aiosqlite.connect(DB) as db:
        cols = [r[1] for r in await (await db.execute("PRAGMA table_info(tasks)")).fetchall()]
        if "topic_id" in cols:
            await db.execute(
                "INSERT INTO tasks (id, chat_id, user_id, input_type, raw_input, state, reply_to_message_id, topic_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (task_id, message.chat.id, user_id, input_type, raw_input, state, message.message_id, topic_id, now, now))
        else:
            await db.execute(
                "INSERT INTO tasks (id, chat_id, user_id, input_type, raw_input, state, reply_to_message_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (task_id, message.chat.id, user_id, input_type, raw_input, state, message.message_id, now, now))
        await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (task_id, f"created:{state}", now))
        await db.commit()

    # === TELEGRAM_TIMELINE_APPEND_V1 ===
    try:
        _tl_chat_key = build_chat_key(message.chat.id)
        _tl_chat_dir = os.path.join(MEMORY_FILES, "CHATS", _tl_chat_key)
        os.makedirs(_tl_chat_dir, exist_ok=True)
        os.makedirs(os.path.join(MEMORY_FILES, "GLOBAL"), exist_ok=True)
        _tl_entry = json.dumps({
            "timestamp": now, "chat_id": str(message.chat.id),
            "topic_id": int(topic_id or 0), "task_id": task_id,
            "input_type": input_type, "state": state,
            "raw_input": str(raw_input or "")[:4000],
            "source": "telegram_daemon_create_task",
        }, ensure_ascii=False)
        for _tl_path in [
            os.path.join(_tl_chat_dir, "timeline.jsonl"),
            os.path.join(MEMORY_FILES, "GLOBAL", "timeline.jsonl"),
        ]:
            with open(_tl_path, "a", encoding="utf-8") as _f:
                _f.write(_tl_entry + "\n")
    except Exception as _tl_e:
        logger.warning("TELEGRAM_TIMELINE_APPEND_V1_ERR %s", _tl_e)
    # === END TELEGRAM_TIMELINE_APPEND_V1 ===

    logger.info("Task %s created state=%s topic_id=%s", task_id, state, topic_id)
    return task_id

async def continue_parent_task(parent_id: str, user_text: str):
    now = now_iso()
    merged_sql = "COALESCE(raw_input,'') || ?"
    suffix = "\n\nПродолжение пользователя:\n" + user_text
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            f"UPDATE tasks SET raw_input={merged_sql}, state='IN_PROGRESS', updated_at=? WHERE id=?",
            (suffix, now, parent_id)
        )
        await db.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
            (parent_id, "continuation:IN_PROGRESS", now)
        )
        await db.commit()
    logger.info("Task %s continued -> IN_PROGRESS", parent_id)

async def get_active_task(chat_id: int) -> dict:
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id, state, raw_input FROM tasks WHERE chat_id=? AND state IN ('NEW','IN_PROGRESS') ORDER BY created_at DESC LIMIT 1",
            (chat_id,))
        row = await cur.fetchone()
        if row:
            return {"id": row[0], "state": row[1], "raw_input": row[2]}
        return None

async def cancel_active_task(chat_id: int):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
            (chat_id,)
        )
        tasks = await cur.fetchall()
        for t in tasks:
            await db.execute("UPDATE tasks SET state='CANCELLED', updated_at=? WHERE id=?", (now_iso(), t[0]))
            await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (t[0], "cancelled", now_iso()))
        await db.commit()
async def reset_all_open_tasks(chat_id: int):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
            (chat_id,)
        )
        rows = await cur.fetchall()
        now = now_iso()
        for row in rows:
            task_id = row[0]
            await db.execute(
                "UPDATE tasks SET state='CANCELLED', updated_at=? WHERE id=?",
                (now, task_id)
            )
            await db.execute(
                "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                (task_id, "reset:CANCELLED", now)
            )
        try:
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE chat_id=? AND state='ACTIVE'",
                (now, str(chat_id))
            )
        except Exception:
            pass
        await db.commit()

def _has_any_phrase(lower_text: str, phrases: list[str]) -> bool:
    t = (lower_text or "").strip()
    return t in phrases

async def close_latest_open_task(chat_id: int, action: str = "finish:DONE") -> bool:
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC, created_at DESC LIMIT 1",
            (chat_id,)
        )
        row = await cur.fetchone()
        if not row:
            return False
        task_id = row[0]
        now = now_iso()
        await db.execute(
            "UPDATE tasks SET state='DONE', updated_at=? WHERE id=?",
            (now, task_id)
        )
        await db.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
            (task_id, action, now)
        )
        try:
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'",
                (now, task_id)
            )
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE chat_id=? AND state='ACTIVE'",
                (now, str(chat_id))
            )
        except Exception:
            pass
        await db.commit()
        return True

async def cancel_all_open_tasks(chat_id: int, topic_id: int = 0) -> int:
    async with aiosqlite.connect(DB) as db:
        if topic_id > 0:
            cur = await db.execute(
                "SELECT id FROM tasks WHERE chat_id=? AND topic_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
                (chat_id, topic_id)
            )
        else:
            cur = await db.execute(
                "SELECT id FROM tasks WHERE chat_id=? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')",
                (chat_id,)
            )
        rows = await cur.fetchall()
        now = now_iso()
        count = 0
        for row in rows:
            task_id = row[0]
            await db.execute(
                "UPDATE tasks SET state='CANCELLED', updated_at=? WHERE id=?",
                (now, task_id)
            )
            await db.execute(
                "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                (task_id, "cancelled:CANCELLED", now)
            )
            count += 1
        try:
            await db.execute(
                "UPDATE pin SET state='CLOSED', updated_at=? WHERE chat_id=? AND state='ACTIVE'",
                (now, str(chat_id))
            )
        except Exception:
            pass
        await db.commit()
        return count

async def _find_parent_task(chat_id: int, reply_to: int | None, topic_id: int = 0):
    async with aiosqlite.connect(DB) as db:
        cols = [r[1] for r in await (await db.execute("PRAGMA table_info(tasks)")).fetchall()]
        has_topic = "topic_id" in cols and topic_id > 0
        topic_filter = " AND topic_id=?" if has_topic else ""
        topic_args = (topic_id,) if has_topic else ()
        if reply_to:
            cur = await db.execute(
                f"SELECT id, state FROM tasks WHERE chat_id=? AND bot_message_id=?{topic_filter} AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                (chat_id, reply_to) + topic_args
            )
            row = await cur.fetchone()
            if row:
                return row
            cur = await db.execute(
                f"SELECT id, state FROM tasks WHERE chat_id=? AND reply_to_message_id=?{topic_filter} AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                (chat_id, reply_to) + topic_args
            )
            row = await cur.fetchone()
            if row:
                return row
        cur = await db.execute(
            f"SELECT id, state FROM tasks WHERE chat_id=?{topic_filter} AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
            (chat_id,) + topic_args
        )
        return await cur.fetchone()

async def _handle_control_text(message, tg_id: int, text: str, lower: str, reply_to: int | None, topic_id: int = 0) -> bool:
    if _has_any_phrase(lower, CANCEL_PHRASES):
        closed = await cancel_all_open_tasks(tg_id, topic_id)
        await message.answer("Все запросы отменены" if closed else "Нет активных задач")
        return True

    parent = await _find_parent_task(tg_id, reply_to, topic_id)

    if _has_any_phrase(lower, FINISH_PHRASES):
        if parent:
            parent_id = parent[0]
            now = now_iso()
            async with aiosqlite.connect(DB) as db:
                await db.execute("UPDATE tasks SET state='DONE', updated_at=? WHERE id=?", (now, parent_id))
                await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "finish:DONE", now))
                await db.execute("UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'", (now, parent_id))
                await db.commit()
            await message.answer("Задача закрыта")
            return True
        closed = await close_latest_open_task(tg_id, "finish:DONE")
        await message.answer("Задача закрыта" if closed else "Нет активных задач")
        return True

    if not parent:
        return False

    parent_id, parent_state = parent[0], parent[1]

    if parent_state == "AWAITING_CONFIRMATION":
        if lower.strip() in SHORT_CONFIRM and lower.strip() not in NEGATIVE_CONFIRM:
            now = now_iso()
            async with aiosqlite.connect(DB) as db:
                await db.execute("UPDATE tasks SET state='DONE', updated_at=? WHERE id=?", (now, parent_id))
                await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "confirmed:DONE", now))
                await db.execute("UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'", (now, parent_id))
                await db.commit()
            await message.answer("Задача завершена")
            return True
        if lower.strip() in NEGATIVE_CONFIRM:
            now = now_iso()
            async with aiosqlite.connect(DB) as db:
                await db.execute("UPDATE tasks SET state='WAITING_CLARIFICATION', updated_at=? WHERE id=?", (now, parent_id))
                await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "rejected:WAITING_CLARIFICATION", now))
                await db.execute("UPDATE pin SET state='CLOSED', updated_at=? WHERE task_id=? AND state='ACTIVE'", (now, parent_id))
                await db.commit()
            await message.answer("Хорошо, доработаю. Подтверждение снято.  # FULLFIX_02_E")
            return True

    if parent_state == "WAITING_CLARIFICATION":
        now = now_iso()
        async with aiosqlite.connect(DB) as db:
            await db.execute("UPDATE tasks SET state='IN_PROGRESS', updated_at=? WHERE id=?", (now, parent_id))
            await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"clarified:{text}", now))
            await db.commit()
        await message.answer("Принято, продолжаю")
        return True

    if parent_state == "IN_PROGRESS" and reply_to:
        now = now_iso()
        async with aiosqlite.connect(DB) as db:
            await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"continued:{text}", now))
            await db.commit()
        await message.answer("Принято, продолжаю")
        return True

    return False


async def download_telegram_file(file_path: str, local_path: str) -> str:
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    async with aiohttp.ClientSession() as s:
        async with s.get(url, timeout=aiohttp.ClientTimeout(total=300)) as r:
            r.raise_for_status()
            async with aiofiles.open(local_path, "wb") as f:
                await f.write(await r.read())
    return local_path

@dp.message()
async def universal_handler(message: types.Message):
    update_id = getattr(message, 'update_id', None)
    if update_id:
        async with aiosqlite.connect(DB) as db:
            await db.execute("DELETE FROM processed_updates WHERE created_at < ?", ((datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),))
            cur = await db.execute("SELECT 1 FROM processed_updates WHERE update_id = ?", (update_id,))
            if await cur.fetchone():
                await db.commit()
                return
            await db.execute("INSERT INTO processed_updates (update_id, created_at) VALUES (?, ?)", (update_id, now_iso()))
            await db.commit()
    
    try:
        text = message.text or ""
        lower = text.lower()
        tg_id = message.chat.id
        now_ts = time.monotonic()
        reply_to = message.reply_to_message.message_id if message.reply_to_message else None
        topic_id = int(getattr(message, "message_thread_id", 0) or 0)
        
        # 1. SYSTEM COMMANDS
        if lower in SYSTEM_CMDS:
            if lower in ("сброс задач", "очистить задачи"):
                await reset_all_open_tasks(tg_id)
                await message.answer("Все незакрытые задачи и активные pin закрыты")
            elif lower == "статус":
                async with aiosqlite.connect(DB) as db:
                    cur = await db.execute("SELECT state, COUNT(*) FROM tasks WHERE chat_id = ? GROUP BY state", (tg_id,))
                    rows = await cur.fetchall()
                    cur = await db.execute("SELECT task_id FROM pin WHERE chat_id = ? AND state = 'ACTIVE'", (str(tg_id),))
                    pin_row = await cur.fetchone()
                    status_msg = "Статус:\n" + "\n".join([f"{r[0]}: {r[1]}" for r in rows]) if rows else "Нет задач"
                    if pin_row:
                        status_msg += f"\nАктивный pin: {pin_row[0]}"
                    await message.answer(status_msg)
            elif lower == "yzon":
                dump = dump_yzon_state(tg_id)
                await message.answer(dump)
                return
            elif lower == "дамп":
                import subprocess
                result = subprocess.run(["/root/.areal-neva-core/.venv/bin/python3", "/root/.areal-neva-core/orchestra_full_dump.py"], capture_output=True, text=True, timeout=60)
                dump_files = sorted([f for f in os.listdir("/root/.areal-neva-core/data/memory/UNSORTED") if f.startswith("orchestra_dump_")], reverse=True)
                if dump_files:
                    dump_path = f"/root/.areal-neva-core/data/memory/UNSORTED/{dump_files[0]}"
                    content=open(dump_path).read()
                    for part in split_message(content):
                        await message.answer(part)
                else:
                    await message.answer("Дамп не создан")
                return
            elif lower == "архив":
                async with aiosqlite.connect(DB) as db:
                    cur = await db.execute("SELECT id, state, substr(raw_input,1,100) FROM tasks WHERE chat_id = ? AND state IN ('DONE','FAILED','CANCELLED','ARCHIVED') ORDER BY updated_at DESC LIMIT 10", (tg_id,))
                    rows = await cur.fetchall()
                    if rows:
                        archive_msg = "Архив:\n" + "\n".join([f"{r[0][:8]}: {r[1]} - {r[2]}" for r in rows])
                    else:
                        archive_msg = "Архив пуст"
                    await message.answer(archive_msg)
            elif lower == "язон":
                dump = dump_yzon_state(tg_id)
                await message.answer(dump)
                return
            elif lower == "язон файл":
                dump = dump_yzon_state(tg_id)
                doc = BufferedInputFile(dump.encode("utf-8"), filename="yzon_state.json")
                await message.answer_document(doc)
                return
            elif lower == "дамп файл":
                import subprocess
                subprocess.run(["/root/.areal-neva-core/.venv/bin/python3", "/root/.areal-neva-core/orchestra_full_dump.py"], capture_output=True, text=True, timeout=60)
                dump_files = sorted([f for f in os.listdir("/root/.areal-neva-core/data/memory/UNSORTED") if f.startswith("orchestra_dump_")], reverse=True)
                if dump_files:
                    dump_path = f"/root/.areal-neva-core/data/memory/UNSORTED/{dump_files[0]}"
                    await message.answer_document(FSInputFile(dump_path, filename=dump_files[0]))
                else:
                    await message.answer("Дамп не создан")
                return
            elif lower == "память файл":
                import sqlite3 as _sq, json as _json
                try:
                    _mc = _sq.connect("/root/.areal-neva-core/data/memory.db")
                    _mc.row_factory = _sq.Row
                    _rows = _mc.execute("SELECT chat_id, key, value, timestamp FROM memory WHERE chat_id=? ORDER BY timestamp DESC LIMIT 200", (str(tg_id),)).fetchall()
                    _mc.close()
                    _data = [dict(r) for r in _rows]
                    doc = BufferedInputFile(_json.dumps(_data, ensure_ascii=False, indent=2).encode("utf-8"), filename="memory_dump.json")
                    await message.answer_document(doc)
                except Exception as _e:
                    await message.answer(f"Ошибка: {_e}")
                return
            elif lower == "архив файл":
                import sqlite3 as _sq, io, json as _json
                try:
                    _mc = _sq.connect("/root/.areal-neva-core/data/memory.db")
                    _mc.row_factory = _sq.Row
                    _rows = _mc.execute("SELECT key, value, timestamp FROM memory WHERE chat_id=? AND key LIKE 'archive_legacy_%' ORDER BY timestamp DESC LIMIT 100", (str(tg_id),)).fetchall()
                    _mc.close()
                    _data = [dict(r) for r in _rows]
                    doc = BufferedInputFile(_json.dumps(_data, ensure_ascii=False, indent=2).encode("utf-8"), filename="archive_dump.json")
                    await message.answer_document(doc)
                except Exception as _e:
                    await message.answer(f"Ошибка: {_e}")
                return
            elif lower in ("система", "система файл"):
                sys_info = (
                    "AREAL-NEVA ORCHESTRA\n"
                    "Server: 89.22.225.136 | Ubuntu 24.04\n"
                    "Bot: @ai_orkestra_all_bot\n"
                    "Models: deepseek/deepseek-chat + perplexity/sonar\n"
                    "Pipeline: telegram_daemon -> core.db -> task_worker -> ai_router -> Telegram\n"
                    "Services: telegram-ingress, areal-task-worker, areal-memory-api\n"
                )
                if lower == "система файл":
                    doc = BufferedInputFile(sys_info.encode("utf-8"), filename="system_info.txt")
                    await message.answer_document(doc)
                else:
                    await message.answer(sys_info)
                return
            elif lower == "код файл":
                import io, zipfile
                buf = io.BytesIO()
                files_to_zip = [
                    "/root/.areal-neva-core/task_worker.py",
                    "/root/.areal-neva-core/core/ai_router.py",
                    "/root/.areal-neva-core/telegram_daemon.py",
                ]
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for fp in files_to_zip:
                        if os.path.exists(fp):
                            zf.write(fp, os.path.basename(fp))
                doc = BufferedInputFile(buf.getvalue(), filename="core_code.zip")
                await message.answer_document(doc)
                return
            elif lower == "файл":
                import sqlite3 as _sq
                try:
                    _cc = _sq.connect("/root/.areal-neva-core/data/core.db")
                    _rows = _cc.execute("SELECT state, COUNT(*) as cnt FROM tasks GROUP BY state").fetchall()
                    _cc.close()
                    lines = ["AREAL-NEVA ORCHESTRA — краткий статус", ""]
                    for r in _rows:
                        lines.append(f"{r[0]}: {r[1]}")
                    doc = BufferedInputFile("\n".join(lines).encode("utf-8"), filename="status.md")
                    await message.answer_document(doc)
                except Exception as _e:
                    await message.answer(f"Ошибка: {_e}")
                return
            else:
                dump = dump_system_state()
                for part in split_message(dump):
                    await message.answer(part)
                    await asyncio.sleep(0.5)
            return
        
        # 2. CANCEL
        if lower in CANCEL_CMDS:
            await cancel_active_task(tg_id)
            await message.answer("Задача отменена")
            return
        
        # 3. FILE TASKS + EZONE FILE INGEST
        if message.document and message.document.file_name:
            # HEALTHCHECK_DAEMON_GUARD_V1
            try:
                _hc_check = " ".join([
                    str(message.document.file_name or ""),
                    str(message.caption or ""),
                ]).lower()
                if any(m in _hc_check for m in ("retry_queue_healthcheck", "healthcheck", "areal_hc_", "_hc_file")):
                    logger.info("HEALTHCHECK_DAEMON_GUARD_V1 ignored file=%s", message.document.file_name)
                    return
            except Exception as _hc_e:
                logger.warning("HEALTHCHECK_DAEMON_GUARD_V1_ERR %s", _hc_e)
            tg_file = await bot.get_file(message.document.file_id)
            local_path = f"/tmp/{uuid.uuid4()}_{message.document.file_name}"
            await download_telegram_file(tg_file.file_path, local_path)
            try:
                if message.document.file_name.lower().endswith(EZONE_EXTS):
                    drive_result = await upload_file_to_topic(local_path, message.document.file_name, tg_id, topic_id, getattr(message.document, "mime_type", "") or None)  # DAEMON_OAUTH_FIX_V1
                    with open(local_path, "r", errors="ignore") as f:
                        content = f.read()
                    if is_ezone_payload(content):
                        ok, chat_key, _ = save_ezone_json(content, tg_id)
                        _RECENT_INGEST[tg_id] = now_ts
                        await message.answer(f"Принял, память загружена ({chat_key})" if ok else "Уже загружено")
                        return
                else:
                    topic_id = getattr(message, "message_thread_id", 0) or 0
                    drive_result = await upload_file_to_topic(local_path, message.document.file_name, tg_id, topic_id, getattr(message.document, "mime_type", "") or None)
                    if isinstance(drive_result, dict) and drive_result.get("ok") and drive_result.get("drive_file_id"):
                        payload = {
                            "file_id": drive_result.get("drive_file_id", ""),
                            "file_name": message.document.file_name,
                            "mime_type": getattr(message.document, "mime_type", "") or "",
                            "caption": (message.caption or message.text or "").strip(),
                            "source": "telegram",
                            "telegram_message_id": message.message_id,
                            "telegram_chat_id": message.chat.id,
                        }
                        await create_task(message, "drive_file", json.dumps(payload, ensure_ascii=False), "NEW")
                        await message.answer("Файл принят в обработку")
                        return
                    else:
                        await message.answer("Ошибка загрузки файла в Drive")
                        return
            finally:
                try: os.remove(local_path)
                except: pass

        # 3A. PHOTO TASK
        if message.photo:
            photo = message.photo[-1]
            tg_file = await bot.get_file(photo.file_id)
            file_name = f"photo_{message.chat.id}_{message.message_id}.jpg"
            local_path = f"/tmp/{uuid.uuid4()}_{file_name}"
            await download_telegram_file(tg_file.file_path, local_path)
            try:
                drive_result = await upload_file_to_topic(local_path, file_name, tg_id, topic_id, "image/jpeg")
                if isinstance(drive_result, dict) and drive_result.get("ok") and drive_result.get("drive_file_id"):
                    payload = {
                        "file_id": drive_result.get("drive_file_id", ""),
                        "file_name": file_name,
                        "mime_type": "image/jpeg",
                        "caption": (message.caption or message.text or "").strip(),
                        "source": "telegram",
                        "telegram_message_id": message.message_id,
                        "telegram_chat_id": message.chat.id,
                    }
                    await create_task(message, "drive_file", json.dumps(payload, ensure_ascii=False), "NEW")
                    await message.answer("Фото принято в обработку")
                    return
                else:
                    await message.answer("Ошибка загрузки фото в Drive")
                    return
            finally:
                try: os.remove(local_path)
                except: pass
        
        # 4. EZONE TEXT INGEST
        if message.text and is_ezone_payload(text):
            ok, chat_key, _ = save_ezone_json(text, tg_id)
            _RECENT_INGEST[tg_id] = now_ts
            await message.answer(f"Принял, память загружена ({chat_key})" if ok else "Уже загружено")
            return
        
        # 5. ANTI-DUP AFTER INGEST
        if message.text:
            last = _RECENT_INGEST.get(tg_id, 0.0)
            if now_ts - last < 5:
                if text.lstrip().startswith("{") or any(k in lower for k in EZONE_KEYS):
                    return
        
        # 6. CONFIRMATION AND REPLY CONTINUATION
        active_confirm = None
        async with aiosqlite.connect(DB) as db:
            cur = await db.execute(
                "SELECT id, state FROM tasks WHERE chat_id = ? AND state = 'AWAITING_CONFIRMATION' ORDER BY updated_at DESC LIMIT 1",
                (tg_id,)
            )
            active_confirm = await cur.fetchone()

        if active_confirm and message.text:
            parent_id, parent_state = active_confirm
            if lower.strip() in SHORT_CONFIRM and lower.strip() not in NEGATIVE_CONFIRM:
                async with aiosqlite.connect(DB) as db:
                    await db.execute("UPDATE tasks SET state = 'DONE', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                    await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "confirmed:DONE", now_iso()))
                    await db.execute("UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'", (now_iso(), parent_id))
                    await db.commit()
                await message.answer("Задача завершена")
                return
            elif lower.strip() in NEGATIVE_CONFIRM:
                async with aiosqlite.connect(DB) as db:
                    await db.execute("UPDATE tasks SET state = 'WAITING_CLARIFICATION', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                    await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, "rejected:WAITING_CLARIFICATION", now_iso()))
                    await db.execute("UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'", (now_iso(), parent_id))
                    await db.commit()
                await message.answer("Хорошо, доработаю. Подтверждение снято.  # FULLFIX_02_E")
                return

        if reply_to:
            async with aiosqlite.connect(DB) as db:
                cur = await db.execute(
                    "SELECT id, state FROM tasks WHERE chat_id = ? AND reply_to_message_id = ? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                    (tg_id, reply_to)
                )
                parent = await cur.fetchone()
            if parent:
                parent_id, parent_state = parent
                if parent_state == "WAITING_CLARIFICATION":
                    async with aiosqlite.connect(DB) as db:
                        await db.execute("UPDATE tasks SET state = 'IN_PROGRESS', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                        await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"clarified:{text}", now_iso()))
                        await db.commit()
                    await message.answer("Принято, продолжаю")
                elif lower.strip() in SHORT_CONFIRM and lower.strip() not in NEGATIVE_CONFIRM:
                    async with aiosqlite.connect(DB) as db:
                        await db.execute("UPDATE tasks SET state = 'IN_PROGRESS', updated_at = ? WHERE id = ?", (now_iso(), parent_id))
                        await db.execute("INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)", (parent_id, f"confirmed:{text}", now_iso()))
                        await db.commit()
                    await message.answer("Принято, выполняю")
                else:
                    await message.answer("Уточните запрос")
                return

        # 7. SEARCH TASK
        if any(t in lower for t in SEARCH_TRIGGERS):
            await create_task(message, "search", text, "NEW")
            return
        
        # 8. VOICE
        if message.voice:
            tg_file = await bot.get_file(message.voice.file_id)
            local_path = os.path.join(VOICE_DIR, f"voice_{abs(tg_id)}_{message.message_id}.ogg")
            await download_telegram_file(tg_file.file_path, local_path)
            pass  # VOICE_UPLOAD_SKIP_V1 — голос не загружаем на Drive
            from core.stt_engine import transcribe_voice as _stt
            try:
                _transcript = await _stt(local_path)
            except Exception as _err:
                logger.error("STT_FAILED chat=%s err=%s", tg_id, _err)
                await message.answer("Голос не распознан. Повтори голосом или напиши текстом")
                return
            if not _transcript or not _transcript.strip():
                logger.error("STT_EMPTY chat=%s", tg_id)
                await message.answer("Не удалось получить текст из голосового. Повтори или напиши текстом")
                return
            voice_text = _transcript.strip()
            voice_lower = voice_text.lower()
            voice_reply_to = message.reply_to_message.message_id if message.reply_to_message else None
            _voice_topic_id = getattr(message, "message_thread_id", None) or 0

            # === PATCH_VOICE_CONFIRM_DIRECT ===
            # Voice does not populate message.text, so confirm/reject must be checked after STT
            try:
                _voice_cmd = voice_lower.strip().rstrip("!., ")
                async with aiosqlite.connect(DB) as db:
                    cur = await db.execute(
                        """
                        SELECT id, state
                        FROM tasks
                        WHERE chat_id = ?
                          AND COALESCE(topic_id,0) = COALESCE(?,0)
                          AND state = 'AWAITING_CONFIRMATION'
                        ORDER BY updated_at DESC
                        LIMIT 1
                        """,
                        (tg_id, _voice_topic_id)
                    )
                    _voice_active_confirm = await cur.fetchone()

                if _voice_active_confirm and _voice_cmd in SHORT_CONFIRM and _voice_cmd not in NEGATIVE_CONFIRM:
                    parent_id, parent_state = _voice_active_confirm
                    async with aiosqlite.connect(DB) as db:
                        await db.execute(
                            "UPDATE tasks SET state = 'DONE', updated_at = ? WHERE id = ?",
                            (now_iso(), parent_id)
                        )
                        await db.execute(
                            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                            (parent_id, "voice_confirmed:DONE", now_iso())
                        )
                        await db.execute(
                            "UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'",
                            (now_iso(), parent_id)
                        )
                        await db.commit()
                    await message.answer("Задача завершена")
                    return

                if _voice_active_confirm and _voice_cmd in NEGATIVE_CONFIRM:
                    parent_id, parent_state = _voice_active_confirm
                    async with aiosqlite.connect(DB) as db:
                        await db.execute(
                            "UPDATE tasks SET state = 'WAITING_CLARIFICATION', updated_at = ? WHERE id = ?",
                            (now_iso(), parent_id)
                        )
                        await db.execute(
                            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, ?)",
                            (parent_id, "voice_rejected:WAITING_CLARIFICATION", now_iso())
                        )
                        await db.execute(
                            "UPDATE pin SET state = 'CLOSED', updated_at = ? WHERE task_id = ? AND state = 'ACTIVE'",
                            (now_iso(), parent_id)
                        )
                        await db.commit()
                    await message.answer("Хорошо, доработаю. Подтверждение снято.  # FULLFIX_02_E")
                    return
            except Exception as _voice_confirm_err:
                logger.error("VOICE_CONFIRM_DIRECT_ERROR chat=%s err=%s", tg_id, _voice_confirm_err)
            # === END PATCH_VOICE_CONFIRM_DIRECT ===
            _VOICE_CONTROL = ["отбой", "отмена", "не надо", "всё", "готово", "можно закрывать", "задача закрыта", "да", "нет", "ок", "+"]
            if any(voice_lower.strip() == x for x in _VOICE_CONTROL):
                if await _handle_control_text(message, tg_id, voice_text, voice_lower, voice_reply_to, _voice_topic_id):
                    return
            try:
                await message.answer(f"🎤 {voice_text}")
            except Exception as _e:
                logger.warning("transcript_send_fail err=%s", _e)
            await create_task(message, "text", "[VOICE] " + voice_text, "NEW")
            return
        
        # 9. NORMAL TEXT
        if message.text:
            reply_to = message.reply_to_message.message_id if message.reply_to_message else None
            _text_topic_id = getattr(message, "message_thread_id", None) or 0
            if await _handle_control_text(message, tg_id, text, lower, reply_to, _text_topic_id):
                return
            # === CHAT_GUARD_V1 ===
            try:
                from core.intent_lock import is_chat_only as _ig_chat
                if _ig_chat(text):
                    return  # короткие реакции не создают задачи
            except Exception:
                pass
            # === END CHAT_GUARD_V1 ===
            await create_task(message, "text", text, "NEW")
            return
        
    except Exception as e:
        logger.error("HANDLER_CRASH: %s", e)
        try:
            await message.answer("Ошибка обработки")
        except:
            pass

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    logger.info("BOT STARTED id=%s username=%s", me.id, me.username)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())