import os, json, aiohttp, logging, sqlite3
from core.stt_engine import transcribe_voice
from core.web_engine import need_web_search, web_search

logger = logging.getLogger(__name__)

OPENROUTER_KEY = (os.getenv("OPENROUTER_API_KEY") or "").strip()
OPENROUTER_MODEL = (os.getenv("OPENROUTER_MODEL") or "deepseek/deepseek-chat").strip()
MEMORY_URL, MEMORY_TOKEN = "http://127.0.0.1:8091/memory", (os.getenv("MEMORY_API_TOKEN") or "").strip()
SNAPSHOT_CHAT_ID = (os.getenv("ORCHESTRA_SNAPSHOT_CHAT_ID") or "AREAL_NEVA_ORCHESTRA_BASE_CORE_OPENROUTER_WORKING_2026_04_11").strip()
MEMORY_FILES = "/root/.areal-neva-core/data/memory_files"

if not OPENROUTER_KEY: raise RuntimeError("OPENROUTER_API_KEY missing")

# ============================================================
# FALLBACK: поиск в файловой памяти (с сортировкой и JSON)
# ============================================================
def search_in_file_memory(query: str, chat_id: str) -> str:
    matches = []
    sd = os.path.join(MEMORY_FILES, "SYSTEM")
    if os.path.exists(sd):
        for fn in sorted(os.listdir(sd)):
            if fn.endswith(".jsonl"):
                with open(os.path.join(sd, fn), "r") as f:
                    for line in f:
                        if query.lower() in line.lower():
                            try:
                                data = json.loads(line)
                                matches.append(json.dumps(data.get("data", {}), ensure_ascii=False)[:500])
                            except: pass
    gf = os.path.join(MEMORY_FILES, "GLOBAL", "timeline.jsonl")
    if os.path.exists(gf):
        with open(gf, "r") as f:
            for line in f:
                if query.lower() in line.lower():
                    try:
                        data = json.loads(line)
                        matches.append(json.dumps(data.get("data", {}), ensure_ascii=False)[:500])
                    except: pass
    cd = os.path.join(MEMORY_FILES, "CHATS", str(chat_id))
    if os.path.exists(cd):
        tf = os.path.join(cd, "timeline.jsonl")
        if os.path.exists(tf):
            with open(tf, "r") as f:
                for line in f:
                    if query.lower() in line.lower():
                        try:
                            data = json.loads(line)
                            matches.append(json.dumps(data.get("data", {}), ensure_ascii=False)[:500])
                        except: pass
    return "\n".join(matches[:3]) if matches else ""

# ============================================================
# ФАЙЛОВАЯ ПАМЯТЬ (контекст) — исправленные форматы
# ============================================================
def read_file_memory(chat_id: str) -> str:
    parts = []
    # 1. SYSTEM
    sd = os.path.join(MEMORY_FILES, "SYSTEM")
    if os.path.exists(sd):
        for fn in sorted(os.listdir(sd)):
            if fn.endswith(".jsonl"):
                with open(os.path.join(sd, fn), "r") as f:
                    parts.append(f"=== SYSTEM: {fn} ===\n" + f.read()[-2000:])
    # 2. GLOBAL — исправлен формат
    gf = os.path.join(MEMORY_FILES, "GLOBAL", "timeline.jsonl")
    if os.path.exists(gf):
        with open(gf, "r") as f:
            parts.append("=== GLOBAL: timeline.jsonl ===\n" + f.read()[-3000:])
    # 3. CHAT — исправлен формат
    cd = os.path.join(MEMORY_FILES, "CHATS", str(chat_id))
    if os.path.exists(cd):
        tf = os.path.join(cd, "timeline.jsonl")
        if os.path.exists(tf):
            with open(tf, "r") as f:
                parts.append(f"=== CHAT: {chat_id} / timeline.jsonl ===\n" + f.read()[-2000:])
    # 4. RELATED CHATS — исправлен формат
    cr = os.path.join(MEMORY_FILES, "CHATS")
    if os.path.exists(cr):
        for cid in sorted(os.listdir(cr)):
            if cid != str(chat_id):
                rf = os.path.join(cr, cid, "raw.json")
                if os.path.exists(rf):
                    with open(rf, "r") as f:
                        data = f.read()[:1000]
                        if any(k in data.lower() for k in ["архитектура", "pipeline", "ошибки", "решения"]):
                            parts.append(f"=== CHAT: {cid} / raw.json ===\n{data}")
    return "\n\n".join(parts)

# ============================================================
# MEMORY DB FALLBACK
# ============================================================
def _fallback_memory(chat_id: str, limit: int = 20):
    try:
        conn = sqlite3.connect("/root/.areal-neva-core/data/memory.db")
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM memory WHERE chat_id=? ORDER BY timestamp DESC LIMIT ?", (chat_id, limit))
        rows = cur.fetchall(); conn.close()
        return [{"key": r[0], "value": r[1]} for r in rows]
    except: return []

async def get_memory(chat_id: str, limit: int = 20) -> list:
    try:
        async with aiohttp.ClientSession() as s:
            r = await s.get(f"{MEMORY_URL}?chat_id={chat_id}&limit={limit}", headers={"Authorization": f"Bearer {MEMORY_TOKEN}"}, timeout=aiohttp.ClientTimeout(total=20))
            return await r.json() if r.status == 200 else _fallback_memory(chat_id, limit)
    except: return _fallback_memory(chat_id, limit)

async def save_memory(chat_id: str, key: str, value: str) -> bool:
    try:
        async with aiohttp.ClientSession() as s:
            r = await s.post(MEMORY_URL, headers={"Authorization": f"Bearer {MEMORY_TOKEN}"}, json={"chat_id": str(chat_id), "key": key, "value": str(value)}, timeout=aiohttp.ClientTimeout(total=20))
            return r.status in (200, 201)
    except: return False

async def get_full_export() -> str:
    for m in await get_memory(SNAPSHOT_CHAT_ID, limit=100):
        if m.get("key") == "full_export": return m.get("value", "")[:10000]
    return ""

def is_archive_request(text: str) -> bool:
    return any(k in text.lower() for k in ["искали", "было", "помнишь", "найди прошлое", "старая задача", "раньше искал"])

def search_archive(query: str) -> str:
    try:
        conn = sqlite3.connect("/root/.areal-neva-core/data/memory.db")
        cur = conn.cursor()
        cur.execute("SELECT value FROM memory WHERE key='task_summary' ORDER BY timestamp DESC LIMIT 20")
        for r in cur.fetchall():
            if query.lower() in (r[0] or "").lower(): return r[0][:1000]
        conn.close()
    except: pass
    return ""

# ============================================================
# BUILD CONTEXT — фиксированный порядок
# ============================================================
def build_context(memories: list, full_export: str, web_data: str, file_memory: str) -> str:
    parts = []
    # 1. FILE MEMORY (уже содержит SYSTEM, GLOBAL, CHAT, RELATED в правильном порядке)
    if file_memory:
        parts.append(file_memory)
    # 2. DB PROJECT
    if full_export:
        parts.append(f"ПРОЕКТ (DB):\n{full_export[:5000]}")
    # 3. DB RECENT
    recent = [f"- {m.get('value', '')[:400]}" for m in memories[-8:] if m.get('key') in ("user_input", "assistant_output", "task_summary")]
    if recent:
        parts.append("ИСТОРИЯ (DB):\n" + "\n".join(recent))
    # 4. WEB
    if web_data:
        parts.append(f"ИНТЕРНЕТ:\n{web_data}")
    return "\n\n".join(parts)

# ============================================================
# LLM CALL WITH FALLBACK
# ============================================================
async def call_llm(user_text: str, context: str, chat_id: str) -> str:
    system = ("Ты — живой ассистент. Отвечай по-русски, только по делу. "
              "Никогда не пиши: 'система выполнит', 'поиск выполняется', 'ожидайте', 'не подключено'.")
    try:
        async with aiohttp.ClientSession() as s:
            r = await s.post("https://openrouter.ai/api/v1/chat/completions",
                             headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                             json={"model": OPENROUTER_MODEL, "temperature": 0.2,
                                   "messages": [{"role": "system", "content": system},
                                                {"role": "user", "content": f"{context}\n\nЗАПРОС: {user_text}"}]},
                             timeout=aiohttp.ClientTimeout(total=300))
            if r.status != 200:
                raise Exception(f"HTTP {r.status}")
            data = await r.json()
            if data.get("error"):
                raise Exception(data["error"])
            return (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip() or "Нет ответа"
    except Exception as e:
        logger.error(f"LLM failed: {e}, using fallback")
        fallback = search_in_file_memory(user_text, chat_id)
        if fallback:
            return fallback
        return "Не нашёл в памяти, уточни запрос"

# ============================================================
# MAIN PROCESS
# ============================================================
async def process_ai_task(task: dict) -> str:
    chat_id = str(task.get("chat_id"))
    input_type = str(task.get("input_type", "text"))
    raw_input = str(task.get("raw_input", "") or "").strip()
    state = task.get("state", "")
    logger.info(f"PROCESS: chat={chat_id}, type={input_type}, state={state}")

    if input_type == "voice":
        user_text = (await transcribe_voice(raw_input)).strip()
    else:
        user_text = raw_input
    if not user_text: return "Пустой запрос"

    if state == "NEW":
        return f"Понял задачу так: {user_text[:300]}\n\nПодтверди или уточни"

    if state == "IN_PROGRESS":
        memories = await get_memory(chat_id, limit=20)
        full_export = await get_full_export()
        file_memory = read_file_memory(chat_id)

        web_data = ""
        if need_web_search(user_text):
            web_data = web_search(user_text, limit=3)
            if not web_data:
                return "Не нашёл нормальных вариантов, уточни критерии"

        await save_memory(chat_id, "user_input", user_text[:4000])
        if input_type == "voice":
            await save_memory(chat_id, "transcript", user_text)

        if is_archive_request(user_text):
            archived = search_archive(user_text)
            if archived:
                return f"Нашёл в архиве:\n{archived}"

        context = build_context(memories, full_export, web_data, file_memory)
        result = await call_llm(user_text, context, chat_id)

        await save_memory(chat_id, "assistant_output", result[:4000])
        await save_memory(chat_id, "task_summary", f"{input_type}: {user_text[:200]} => {result[:300]}")
        return result

    return "Неизвестное состояние задачи"
