import json, os, logging, sqlite3

logger = logging.getLogger("ai_router")

MEMORY_FILES = "/root/.areal-neva-core/data/memory_files"
CHAT_MAP_FILE = os.path.join(MEMORY_FILES, "CHAT_MAP.json")
MEMORY_DB = "/root/.areal-neva-core/data/memory.db"
CORE_DB = "/root/.areal-neva-core/data/core.db"

async def process_ai_task(task: dict) -> str:
    chat_id = task.get("chat_id")
    task_id = task.get("id")
    raw_input = task.get("raw_input", "")
    # GUARD: voice must be transcribed
    if raw_input and (".ogg" in raw_input or "/voice_queue/" in raw_input):
        import logging
        logging.getLogger("ai_router").error("VOICE NOT TRANSCRIBED: %s", raw_input)
        raise ValueError("VOICE_NOT_TRANSCRIBED")
    
    context = []
    route_log = []
    
    # 1. active pin
    try:
        conn = sqlite3.connect(CORE_DB)
        cur = conn.execute("SELECT task_id FROM pin WHERE chat_id = ? AND state = 'ACTIVE'", (str(chat_id),))
        pin_row = cur.fetchone()
        if pin_row:
            cur = conn.execute("SELECT raw_input, result FROM tasks WHERE id = ?", (pin_row[0],))
            task_row = cur.fetchone()
            if task_row:
                context.append(f"PIN: {task_row[0]}\nRESULT: {task_row[1]}")
                route_log.append("pin")
        conn.close()
    except:
        pass
    
    # 2. active task
    try:
        conn = sqlite3.connect(CORE_DB)
        cur = conn.execute(
            "SELECT raw_input, result FROM tasks WHERE chat_id = ? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') AND id != ? ORDER BY created_at DESC LIMIT 1",
            (chat_id, task_id)
        )
        active = cur.fetchone()
        if active:
            context.append(f"ACTIVE TASK: {active[0]}\nRESULT: {active[1]}")
            route_log.append("active_task")
        conn.close()
    except:
        pass
    
    # 3. file memory
    try:
        with open(CHAT_MAP_FILE) as f:
            chat_map = json.load(f)
    except:
        chat_map = {}
    
    chats = chat_map.get(str(chat_id), {})
    if isinstance(chats, dict):
        chat_keys = list(chats.keys())
    elif isinstance(chats, list):
        chat_keys = chats
    else:
        chat_keys = []
    
    for ck in chat_keys[-3:]:
        raw_file = os.path.join(MEMORY_FILES, "CHATS", ck, "raw.json")
        if os.path.exists(raw_file):
            try:
                with open(raw_file) as f:
                    context.append(f.read()[:2000])
                    route_log.append(f"file:{ck}")
            except:
                pass
    
    # 4. GLOBAL + SYSTEM
    for d, label in [("GLOBAL", "GLOBAL"), ("SYSTEM", "SYSTEM")]:
        path = os.path.join(MEMORY_FILES, d)
        if os.path.exists(path):
            for fname in sorted(os.listdir(path))[-3:]:
                if fname.endswith(".jsonl"):
                    try:
                        with open(os.path.join(path, fname)) as f:
                            context.append(f.read()[:1000])
                            route_log.append(f"{d}:{fname}")
                    except:
                        pass
    
    # 5. memory.db
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cur = conn.execute("SELECT key, value FROM memory WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 5", (str(chat_id),))
        for row in cur.fetchall():
            context.append(f"{row[0]}: {row[1]}")
            route_log.append("memory.db")
        conn.close()
    except:
        pass
    
    context_text = "\n".join(context)[:8000]
    logger.info("ROUTE: %s", "+".join(route_log) if route_log else "empty")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
                json={
                    "model": os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
                    "messages": [
                        {"role": "system", "content": "Контекст:\n" + (context_text or "Память пуста")},
                        {"role": "user", "content": raw_input}
                    ]
                },
                timeout=30
            ) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error("LLM_FAIL: %s", e)
        return "Не найдено"
