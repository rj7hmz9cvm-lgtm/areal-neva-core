# === FULLFIX_14_TEMPLATE_INTAKE ===
import os, json, logging
from datetime import datetime
logger = logging.getLogger(__name__)
ENGINE = "FULLFIX_14_TEMPLATE_INTAKE"
TEMPLATES_DIR = "/root/.areal-neva-core/data/templates"
TEMPLATES_INDEX = os.path.join(TEMPLATES_DIR, "index.json")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

SAMPLE_PHRASES = [
    "как образец", "как шаблон", "образец", "шаблон", "как пример",
    "по образцу", "возьми", "используй этот", "используй как",
    "сделай по", "сохрани", "запомни"
]

def is_sample_intent(text):
    t = (text or "").lower()
    return any(p in t for p in SAMPLE_PHRASES)

def _load_index():
    if os.path.exists(TEMPLATES_INDEX):
        try:
            with open(TEMPLATES_INDEX, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def _save_index(idx):
    with open(TEMPLATES_INDEX, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)

def _detect_kind(file_name, mime_type, text=""):
    name = (file_name or "").lower()
    t = (text or "").lower()
    if "смет" in name or "смет" in t or "estimate" in name:
        return "estimate_template"
    if any(x in name for x in ["ар", "кж", "кд", "км", "проект"]):
        return "project_template"
    if any(x in t for x in ["акт", "дефект", "технадзор"]):
        return "act_template"
    if mime_type and "spreadsheet" in mime_type:
        return "estimate_template"
    if mime_type and "pdf" in mime_type:
        return "project_template"
    return "unknown_template"

def _save_memory_pointer(chat_id, topic_id, kind, template_id):
    try:
        import sqlite3
        mem_db = "/root/.areal-neva-core/data/memory.db"
        key = "topic_" + str(topic_id) + "_active_" + kind
        val = json.dumps({"template_id": template_id, "kind": kind})
        con = sqlite3.connect(mem_db)
        con.execute(
            "INSERT OR REPLACE INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,datetime('now'))",
            (chat_id, key, val)
        )
        con.commit()
        con.close()
    except Exception as e:
        logger.error("TEMPLATE_MEMORY_SAVE err=%s", e)

def save_template(task_id, chat_id, topic_id, file_name, mime_type, local_path="", caption=""):
    kind = _detect_kind(file_name, mime_type, caption)
    tmpl = {
        "template_id": task_id, "chat_id": chat_id, "topic_id": topic_id,
        "source_task_id": task_id, "source_file_name": file_name,
        "mime_type": mime_type, "kind": kind,
        "created_at": datetime.now().isoformat(), "active": True,
    }
    idx = _load_index()
    for t in idx:
        if t.get("chat_id") == chat_id and t.get("topic_id") == topic_id and t.get("kind") == kind:
            t["active"] = False
    idx.append(tmpl)
    _save_index(idx)
    with open(os.path.join(TEMPLATES_DIR, task_id + ".json"), "w", encoding="utf-8") as f:
        json.dump(tmpl, f, ensure_ascii=False, indent=2)
    _save_memory_pointer(chat_id, topic_id, kind, task_id)
    return tmpl

def get_active_template(chat_id, topic_id, kind="estimate_template"):
    idx = _load_index()
    for t in reversed(idx):
        if t.get("chat_id") == chat_id and t.get("topic_id") == topic_id and t.get("kind") == kind and t.get("active"):
            p = os.path.join(TEMPLATES_DIR, t["template_id"] + ".json")
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
    return {}

def process_template_intake_sync(conn, task_id, chat_id, topic_id, raw_input, local_path="", file_name="", mime_type=""):
    from core.reply_sender import send_reply_ex
    try:
        if not is_sample_intent(raw_input) and not file_name:
            return False
        if not file_name:
            row = conn.execute(
                "SELECT raw_input FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=? AND input_type='drive_file' AND state!='CANCELLED' ORDER BY created_at DESC LIMIT 1",
                (chat_id, topic_id)
            ).fetchone()
            if row:
                try:
                    meta = json.loads(row[0] or "{}")
                    file_name = meta.get("file_name", "")
                    mime_type = meta.get("mime_type", "")
                except Exception:
                    pass
        save_template(task_id, chat_id, topic_id, file_name, mime_type, local_path, raw_input)
        kind = _detect_kind(file_name, mime_type, raw_input)
        kind_label = {"estimate_template": "смета", "project_template": "проект", "act_template": "акт"}.get(kind, "файл")
        result_text = "Образец принят. Тип: " + kind_label + ". Файл: " + file_name + ". Шаблон сохранён."
        conn.execute(
            "UPDATE tasks SET state='DONE',result=?,updated_at=datetime('now') WHERE id=?",
            (result_text, task_id)
        )
        conn.execute(
            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
            (task_id, "state:DONE")
        )
        conn.commit()
        try:
            send_reply_ex(chat_id=str(chat_id), text=result_text, reply_to_message_id=None)
        except Exception as _se:
            logger.error("TEMPLATE_SEND_ERR task=%s err=%s", task_id, _se)
        return True
    except Exception as e:
        logger.error("TEMPLATE_INTAKE_ERROR task=%s err=%s", task_id, e)
        return False

async def process_template_intake(conn, task_id, chat_id, topic_id, raw_input, local_path="", file_name="", mime_type=""):
    import asyncio
    return await asyncio.get_event_loop().run_in_executor(
        None, process_template_intake_sync, conn, task_id, chat_id, topic_id, raw_input, local_path, file_name, mime_type
    )
# === END FULLFIX_14_TEMPLATE_INTAKE ===
