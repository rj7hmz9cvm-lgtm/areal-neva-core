import asyncio, hashlib, json, logging, os, re, time, uuid, fcntl, tempfile
import time
from datetime import datetime, timezone
import aiofiles, aiohttp, aiosqlite
from aiogram import Bot, Dispatcher, types

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

DUMP_TRIGGERS = (
    "память оркестра", "оркестровая память", "выгрузи память", "дай память", "общая память",
    "покажи память", "вся память", "экспорт памяти", "дамп", "память"
)
EZONE_KEYS = ("system", "architecture", "pipeline", "memory")
EZONE_EXTS = (".json", ".jsonl", ".txt")

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def normalize_chat_id(raw: str) -> str:
    if not raw:
        return ""
    raw = raw.lower().strip()
    raw = re.sub(r"[^a-z0-9_-]", "", raw)
    return raw

def normalize_json_text(text: str) -> str:
    if not text:
        return text
    replacements = {"“": '"', "”": '"', "„": '"', "«": '"', "»": '"', "‘": "'", "’": "'", "…": "..."}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()

def extract_raw_chat_id(text: str, data: dict = None) -> str:
    if data and isinstance(data, dict) and "chat_id" in data:
        return str(data["chat_id"])
    match = re.search(r'"chat_id"\s*:\s*"([^"]+)"', text)
    if match:
        return match.group(1)
    match = re.search(r'chat_id[:\s]+([^\s,}]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip('"')
    return ""

def extract_source_model(data: dict) -> str:
    if isinstance(data, dict):
        for key in ("source_model", "model"):
            if key in data:
                return str(data[key])
    return "unknown_model"

def build_chat_key(text: str, data: dict) -> str:
    raw_chat = extract_raw_chat_id(text, data)
    chat_id = normalize_chat_id(raw_chat) if raw_chat else f"unknown_{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%S')}"
    model = extract_source_model(data)
    return f"{chat_id}__{model}"

def update_chat_map_atomic(telegram_chat_id: int, chat_key: str):
    lock_file = CHAT_MAP_FILE + ".lock"
    try:
        with open(lock_file, "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                if os.path.exists(CHAT_MAP_FILE):
                    with open(CHAT_MAP_FILE, "r") as f:
                        chat_map = json.load(f)
                else:
                    chat_map = {}
                tg_id = str(telegram_chat_id)
                if tg_id not in chat_map:
                    chat_map[tg_id] = []
                if chat_key not in chat_map[tg_id]:
                    chat_map[tg_id].append(chat_key)
                fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(CHAT_MAP_FILE), prefix=".chat_map_", suffix=".tmp")
                try:
                    with os.fdopen(fd, "w") as tmp:
                        json.dump(chat_map, tmp, ensure_ascii=False, indent=2)
                        tmp.flush()
                        os.fsync(tmp.fileno())
                    os.replace(tmp_path, CHAT_MAP_FILE)
                except:
                    os.unlink(tmp_path)
                    raise
                logger.info("CHAT_MAP updated: %s -> %s", tg_id, chat_key)
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)
    except Exception as e:
        logger.error("CHAT_MAP update failed: %s", e)
    finally:
        try:
            os.unlink(lock_file)
        except:
            pass

def is_ezone_payload(text: str) -> bool:
    norm = normalize_json_text(text)
    try:
        data = json.loads(norm)
        return isinstance(data, dict) and any(k in data for k in EZONE_KEYS)
    except:
        low = norm.lower()
        return all(k in low for k in EZONE_KEYS)

def content_hash(text: str) -> str:
    return hashlib.sha256(normalize_json_text(text).encode()).hexdigest()

def is_duplicate_today(hash_val: str, chat_key: str) -> bool:
    dup_file = os.path.join(MEMORY_FILES, "CHATS", chat_key, ".duplicates.jsonl")
    today = today_key()
    if os.path.exists(dup_file):
        with open(dup_file, "r") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec.get("hash") == hash_val and rec.get("date") == today:
                        return True
                except:
                    pass
    os.makedirs(os.path.dirname(dup_file), exist_ok=True)
    with open(dup_file, "a") as f:
        f.write(json.dumps({"hash": hash_val, "date": today, "ts": now_iso()}) + "\n")
    return False

def save_ezone_json(text: str, telegram_chat_id: int) -> tuple[bool, str, str]:
    try:
        norm = normalize_json_text(text)
        try:
            data = json.loads(norm)
        except:
            data = {"raw_text": norm}
        if not isinstance(data, dict):
            data = {"raw_text": norm}

        chat_key = build_chat_key(text, data)
        ts = now_iso()
        hash_val = content_hash(text)

        if is_duplicate_today(hash_val, chat_key):
            return False, "duplicate", chat_key

        meta = {"chat_key": chat_key, "ingested_at": ts}
        data["_meta"] = meta

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
                fname = os.path.join(MEMORY_FILES, "SYSTEM", f"{key}.jsonl")
                with open(fname, "a") as f:
                    f.write(json.dumps({"timestamp": ts, "data": data[key]}, ensure_ascii=False) + "\n")

        update_chat_map_atomic(telegram_chat_id, chat_key)
        logger.info("eZone saved: chat_key=%s telegram_chat=%s", chat_key, telegram_chat_id)
        return True, chat_key, ""
    except Exception as e:
        with open(os.path.join(MEMORY_FILES, "ERRORS", "errors.log"), "a") as f:
            f.write(f"{now_iso()} | source=telegram | error={str(e)}\n")
        return False, "", str(e)

def save_system_note(key: str, content: str):
    fname = os.path.join(MEMORY_FILES, "SYSTEM", f"{key}.jsonl")
    with open(fname, "a") as f:
        f.write(json.dumps({"timestamp": now_iso(), "note": content}, ensure_ascii=False) + "\n")

_RECENT_INGEST = {}

def dump_file_memory() -> str:
    parts = []
    for d in ["GLOBAL", "CHATS", "SYSTEM"]:
        path = os.path.join(MEMORY_FILES, d)
        if os.path.exists(path):
            for root, _, files in sorted(os.walk(path)):
                for fname in sorted(files):
                    if d == "SYSTEM" and not fname.endswith(".jsonl"):
                        continue
                    if not (fname.endswith(".json") or fname.endswith(".jsonl")):
                        continue
                    with open(os.path.join(root, fname), "r") as fp:
                        content = fp.read()
                    if d == "CHATS":
                        chat_key = os.path.basename(root)
                        parts.append(f"=== CHAT: {chat_key} / {fname} ===\n{content}")
                    else:
                        parts.append(f"=== {d}: {fname} ===\n{content}")
    return "\n\n".join(parts)

def split_message(text: str, limit: int = 3000) -> list:
    text = text or ""
    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1 or split_at < limit // 3:
            split_at = limit
        parts.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return parts or [""]
async def create_task(message: types.Message, input_type: str, raw_input: str):
    task_id = str(uuid.uuid4())
    now = now_iso()
    user_id = getattr(message.from_user, "id", 0) if message.from_user else 0
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT INTO tasks (id, chat_id, user_id, input_type, raw_input, state, reply_to_message_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (task_id, message.chat.id, user_id, input_type, raw_input, "NEW", message.message_id, now, now))
        await db.commit()
    logger.info("Task %s created", task_id)

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
    try:
        text = message.text or ""
        lower = text.strip().lower()
        telegram_chat_id = message.chat.id
        now_ts = time.monotonic()

        # memory dump commands: one route, no task creation
        if lower in ["память", "память оркестра", "выгрузи память"]:
            try:
                dump = dump_file_memory() or "Память пуста"
                for part in split_message(dump):
                    await message.answer(part or " ")
                    await asyncio.sleep(0.15)
            except Exception as e:
                logger.error("MEMORY_DUMP_FAIL: %s", e)
                try:
                    await message.answer("Ошибка памяти")
                except Exception:
                    pass
            return

        # document ingest: one route, no task creation
        if message.document:
            doc = message.document
            file_name = (doc.file_name or "").lower()

            if file_name.endswith(EZONE_EXTS):
                tg_file = await bot.get_file(doc.file_id)
                local_path = f"/tmp/{uuid.uuid4()}_{os.path.basename(file_name) or 'ezone.txt'}"
                await download_telegram_file(tg_file.file_path, local_path)

                try:
                    with open(local_path, "r", errors="ignore") as f:
                        content = f.read()

                    if is_ezone_payload(content):
                        ok, chat_key, err = save_ezone_json(content, telegram_chat_id)
                        _RECENT_INGEST[telegram_chat_id] = now_ts

                        if ok:
                            await message.reply(f"Принял, память загружена ({chat_key})")
                            try:
                                save_system_note("ingest", f"file ingested: {chat_key}")
                            except Exception:
                                pass
                        elif chat_key:
                            await message.reply("Уже загружено")
                        else:
                            await message.reply("НЕТ")
                        return

                except Exception as e:
                    logger.error("FILE_INGEST_FAIL: %s", e)
                    try:
                        with open(os.path.join(MEMORY_FILES, "ERRORS", "errors.log"), "a") as f:
                            f.write(f"{now_iso()} | source=telegram | error={str(e)}\n")
                    except Exception:
                        pass
                    await message.reply("НЕТ")
                    return

                finally:
                    try:
                        os.remove(local_path)
                    except Exception:
                        pass

        # text ingest: one route, no task creation
        if message.text and is_ezone_payload(text):
            try:
                ok, chat_key, err = save_ezone_json(text, telegram_chat_id)
                _RECENT_INGEST[telegram_chat_id] = now_ts

                if ok:
                    await message.reply(f"Принял, память загружена ({chat_key})")
                    try:
                        save_system_note("ingest", f"text ingested: {chat_key}")
                    except Exception:
                        pass
                elif chat_key:
                    await message.reply("Уже загружено")
                else:
                    await message.reply("НЕТ")
            except Exception as e:
                logger.error("TEXT_INGEST_FAIL: %s", e)
                try:
                    with open(os.path.join(MEMORY_FILES, "ERRORS", "errors.log"), "a") as f:
                        f.write(f"{now_iso()} | source=telegram | error={str(e)}\n")
                except Exception:
                    pass
                await message.reply("НЕТ")
            return

        # anti-double-processing window after successful ingest
        if message.text:
            last_ingest = _RECENT_INGEST.get(telegram_chat_id, 0.0)
            if now_ts - last_ingest < 2.5:
                suspect = text.lstrip().startswith("{") or "chat_id" in lower or "architecture" in lower or "pipeline" in lower or "memory" in lower
                if suspect:
                    logger.info("SKIP_DUP_AFTER_INGEST chat=%s", telegram_chat_id)
                    return

        # voice -> task
        if message.voice:
            tg_file = await bot.get_file(message.voice.file_id)
            local_path = os.path.join(VOICE_DIR, f"voice_{abs(message.chat.id)}_{message.message_id}.ogg")
            await download_telegram_file(tg_file.file_path, local_path)
            await create_task(message, "voice", local_path)
            return

        # normal text -> task
        if message.text:
            await create_task(message, "text", text)
            return

    except Exception as e:
        logger.error("HANDLER_CRASH: %s", e)
        try:
            await message.answer("Ошибка обработки")
        except Exception:
            pass

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    logger.info("BOT STARTED id=%s username=%s", me.id, me.username)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

