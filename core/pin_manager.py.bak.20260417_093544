import sqlite3

CORE_DB = "/root/.areal-neva-core/data/core.db"

def _conn():
    conn = sqlite3.connect(CORE_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def _has_table(conn, table: str) -> bool:
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
    return row is not None

def get_pin_context(chat_id: str, request_text: str = "") -> str:
    conn = _conn()
    try:
        if not _has_table(conn, "pin"):
            return ""

        row = conn.execute(
            "SELECT task_id FROM pin WHERE chat_id=? AND state='ACTIVE' ORDER BY rowid DESC LIMIT 1",
            (str(chat_id),)
        ).fetchone()

        if not row or not row["task_id"]:
            return ""

        task_row = conn.execute(
            "SELECT result FROM tasks WHERE id=? LIMIT 1",
            (row["task_id"],)
        ).fetchone()

        if task_row and task_row["result"]:
            pin_text = str(task_row["result"]).strip()[:4000]
            if request_text:
                import re
                STOP_WORDS = {
                    "мне","нужно","ещё","еще","варианты","вариант","вариантов","вариантах",
                    "это","вот","сделай","найди","найти","покажи","дай","дать","хочу",
                    "можешь","можно","пожалуйста","давай","давайте","сюда","туда","там",
                    "тут","здесь","всё","все","тоже","также","просто","только","уже",
                    "или","что","как","где","когда","зачем","почему","есть","быть",
                    "этот","эта","эти","такой","такие","один","одна","одно","больше",
                    "лучше","другой","другие","другое","новый","новые","новая","ещe",
                    "по","на","за","из","от","до","с","к","а","и","но","не","ни",
                    "то","да","нет","же","бы","ли","ну","так"
                }
                req_words = set(re.findall(r"\w+", request_text.lower()))
                req_meaningful = {w for w in req_words if len(w) > 3 and w not in STOP_WORDS}
                if not req_meaningful:
                    return ""
                pin_words = set(re.findall(r"\w+", pin_text.lower()))
                pin_meaningful = {w for w in pin_words if len(w) > 3 and w not in STOP_WORDS}
                if not (req_meaningful & pin_meaningful):
                    return ""
            return pin_text

        return ""
    finally:
        conn.close()

def save_pin(chat_id: str, task_id: str, result_text: str) -> bool:
    text = (result_text or "").strip()
    if not text:
        return False
    conn = _conn()
    try:
        if not _has_table(conn, "pin"):
            return False

        conn.execute(
            "UPDATE pin SET state='CLOSED', updated_at=datetime('now') WHERE chat_id=? AND state='ACTIVE'",
            (str(chat_id),)
        )
        conn.execute(
            "INSERT INTO pin (chat_id, task_id, state, created_at, updated_at) VALUES (?, ?, 'ACTIVE', datetime('now'), datetime('now'))",
            (str(chat_id), task_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()
