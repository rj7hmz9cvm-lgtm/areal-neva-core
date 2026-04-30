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
        up = upload_or_fail(manifest_path, task_id, topic_id, "multifile_index")
        if up.get("success") and up.get("link"):
            result_text = "Сводка по " + str(len(files)) + " файлам:\n" + up["link"]
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
            _br = send_reply_ex(chat_id=str(chat_id), text=result_text, reply_to_message_id=None)
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
