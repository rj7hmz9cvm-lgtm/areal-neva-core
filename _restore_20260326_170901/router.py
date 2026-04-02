import os

def route_and_execute(task):
    try:
        payload = task.get("payload", {}) or {}
        text = payload.get("text", "") or ""
        file_id = payload.get("file_id")
        file_name = payload.get("file_name")

        # 1. ЕСЛИ ЕСТЬ ФАЙЛ → ДОКУМЕНТ
        if file_id or file_name:
            return "done", f"[DOC_TASK]\nfile={file_name}\nstatus=queued_for_analysis"

        # 2. ЕСЛИ ТЕКСТ → НЕ ДАЕМ ЧАТ-БОТ ОТВЕТ
        if text:
            return "done", f"[TASK]\n{text}\nstatus=accepted"

        return "failed", "EMPTY_TASK"

    except Exception as e:
        return "failed", f"ROUTER_ERROR: {e}"
