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
    
    context_blocks = []
    route_log = []

    SERVICE_TRASH = (
        "голосовые сообщения временно недоступны",
        "голос не обработан",
        "voice not available",
        "voice_not_transcribed",
        "stt_failed",
        "timeout",
        "llm_fail",
        "send_reply_failed",
        "error",
        "failed",
        "не удалось распознать",
        "ошибка обработки",
        "подтвердить выполнение",
    )
    PATH_TRASH = ("/root/", ".ogg", ".log", "/voice_queue/")

    def _norm(x: str) -> str:
        return " ".join(str(x).lower().split())

    def _is_service_trash(x) -> bool:
        if x is None:
            return True
        txt = str(x).strip()
        if not txt:
            return True
        low = _norm(txt)
        if any(t in low for t in SERVICE_TRASH):
            return True
        if any(p in txt for p in PATH_TRASH):
            return True
        return False

    def _mk_block(tag: str, value) -> str | None:
        if value is None:
            return None
        txt = str(value).strip()
        if not txt:
            return None
        if _is_service_trash(txt):
            return None
        return f"[TYPE:{tag}]\n{txt}"

    def _dedup(blocks):
        seen = set()
        out = []
        for item in reversed(blocks):
            key = _norm(item)
            if key and key not in seen:
                seen.add(key)
                out.append(item)
        return list(reversed(out))

    def _priority(block: str) -> int:
        if block.startswith("[TYPE:CURRENT_INPUT]"):
            return 1
        if block.startswith("[TYPE:ACTIVE_TASK]"):
            return 2
        if block.startswith("[TYPE:PIN]"):
            return 3
        if block.startswith("[TYPE:SHORT_MEMORY]"):
            return 4
        if block.startswith("[TYPE:LONG_MEMORY]"):
            return 5
        if block.startswith("[TYPE:SEARCH_RESULT]"):
            return 6
        return 99

    def _final_sanitize_response(resp: str) -> str:
        if not resp:
            return "Не найдено"
        lines = []
        for line in str(resp).splitlines():
            line = line.strip()
            if line and not _is_service_trash(line):
                lines.append(line)
        cleaned = "\n".join(lines).strip()
        return cleaned or "Не найдено"

    # 1. CURRENT_INPUT
    current_block = _mk_block("CURRENT_INPUT", raw_input)
    if current_block:
        context_blocks.append(current_block)
        route_log.append("current_input")

    # 2. ACTIVE_TASK
    try:
        conn = sqlite3.connect(CORE_DB)
        cur = conn.execute(
            "SELECT raw_input, result FROM tasks WHERE chat_id = ? AND state IN ('NEW','WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION') AND id != ? ORDER BY created_at DESC LIMIT 1",
            (chat_id, task_id)
        )
        active = cur.fetchone()
        if active:
            active_value = active[1] if active[1] else active[0]
            active_block = _mk_block("ACTIVE_TASK", active_value)
            if active_block:
                context_blocks.append(active_block)
                route_log.append("active_task")
        conn.close()
    except:
        pass

    # 3. PIN
    try:
        conn = sqlite3.connect(CORE_DB)
        cur = conn.execute("SELECT task_id FROM pin WHERE chat_id = ? AND state = 'ACTIVE'", (str(chat_id),))
        pin_row = cur.fetchone()
        if pin_row:
            cur = conn.execute("SELECT raw_input, result FROM tasks WHERE id = ?", (pin_row[0],))
            task_row = cur.fetchone()
            if task_row:
                pin_value = task_row[1] if task_row[1] else task_row[0]
                pin_block = _mk_block("PIN", pin_value)
                if pin_block:
                    context_blocks.append(pin_block)
                    route_log.append("pin")
        conn.close()
    except:
        pass

    # 4. SHORT_MEMORY
    try:
        conn = sqlite3.connect(CORE_DB)
        cur = conn.execute(
            "SELECT result FROM tasks WHERE chat_id = ? AND state = 'DONE' AND id != ? AND result IS NOT NULL AND result != '' ORDER BY updated_at DESC LIMIT 3",
            (str(chat_id), task_id)
        )
        for row in cur.fetchall():
            block = _mk_block("SHORT_MEMORY", str(row[0])[:800])
            if block:
                context_blocks.append(block)
                route_log.append("short_memory")
        conn.close()
    except:
        pass

    # 5. LONG_MEMORY from GLOBAL + SYSTEM only
    for d in ("GLOBAL", "SYSTEM"):
        path = os.path.join(MEMORY_FILES, d)
        if os.path.exists(path):
            for fname in sorted(os.listdir(path))[-3:]:
                if fname.endswith(".jsonl"):
                    try:
                        with open(os.path.join(path, fname)) as f:
                            txt = f.read()[:1000]
                            block = _mk_block("LONG_MEMORY", txt)
                            if block:
                                context_blocks.append(block)
                                route_log.append(f"{d}:{fname}")
                    except:
                        pass

    # 6. LONG_MEMORY from memory.db
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cur = conn.execute("SELECT key, value FROM memory WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 5", (str(chat_id),))
        for row in cur.fetchall():
            txt = f"{row[0]}: {row[1]}"
            block = _mk_block("LONG_MEMORY", txt[:1000])
            if block:
                context_blocks.append(block)
                route_log.append("memory.db")
        conn.close()
    except:
        pass

    # 7. SEARCH_RESULT reuse read-only layer
    try:
        conn = sqlite3.connect(CORE_DB)
        cur = conn.execute(
            "SELECT result FROM tasks WHERE chat_id = ? AND input_type = 'search' AND state = 'DONE' AND result IS NOT NULL AND result != '' ORDER BY updated_at DESC LIMIT 3",
            (str(chat_id),)
        )
        for row in cur.fetchall():
            block = _mk_block("SEARCH_RESULT", str(row[0])[:800])
            if block:
                context_blocks.append(block)
                route_log.append("search_result")
        conn.close()
    except:
        pass

    context_blocks = _dedup(context_blocks)
    context_blocks = sorted(context_blocks, key=_priority)
    context_blocks = context_blocks[:20]
    context_text = "\n\n".join(context_blocks)[:8000]
    logger.info("ROUTE: %s", "+".join(route_log) if route_log else "empty")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
                json={
                    "model": os.getenv("OPENROUTER_MODEL"),
                    "messages": [
                        {"role": "system", "content": "Контекст:\n" + (context_text or "Память пуста")},
                        {"role": "user", "content": raw_input}
                    ]
                },
                timeout=30
            ) as resp:
                data = await resp.json()
                response = data["choices"][0]["message"]["content"]
                return _final_sanitize_response(response)
    except Exception as e:
        logger.error("LLM_FAIL: %s", e)
        return "Не найдено"
