# === FINAL_CLOSURE_BLOCKER_FIX_V1_TECHNADZOR_ENGINE ===
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "outputs" / "technadzor"
OUT.mkdir(parents=True, exist_ok=True)


def is_technadzor_intent(text: str = "", file_name: str = "") -> bool:
    t = f"{text} {file_name}".lower().replace("ё", "е")
    return bool(re.search(r"\b(акт|технадзор|техническ.*надзор|дефект|замечан|нарушен|освидетельств|стройконтроль|сп|гост|снип)\b", t))


def _norm_refs(text: str) -> str:
    refs = []
    for m in re.findall(r"\b(сп\s*\d+[.\d]*|гост\s*\d+[.\d-]*|снип\s*[\w.\-]+)\b", text or "", flags=re.I):
        refs.append(m.upper().replace("  ", " "))
    return ", ".join(sorted(set(refs))) if refs else "Норма не подтверждена"


def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "") -> Dict[str, Any]:
    if not is_technadzor_intent(text, file_name):
        return {"ok": False, "handled": False, "reason": "NOT_TECHNADZOR"}

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"TECHNADZOR_ACT__{task_id[:8] or ts}"
    txt_path = OUT / f"{stem}.txt"

    body = [
        "АКТ ТЕХНИЧЕСКОГО НАДЗОРА",
        "",
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Задача: {task_id}",
        f"Топик: {topic_id}",
    ]

    if file_name:
        body.append(f"Файл: {file_name}")

    body.extend(
        [
            "",
            "Исходное описание:",
            (text or "").strip() or "UNKNOWN",
            "",
            "Нормативная база:",
            _norm_refs(text),
            "",
            "Вывод:",
            "Черновик акта создан. Если норматив не подтверждён источником, в акте указано: Норма не подтверждена",
        ]
    )

    txt_path.write_text("\n".join(body) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "handled": True,
        "kind": "technadzor_act",
        "state": "DONE",
        "artifact_path": str(txt_path),
        "message": "Технадзорный акт подготовлен",  # TECHNADZOR_PUBLIC_MESSAGE_NO_LOCAL_PATH_V1
        "history": "FINAL_CLOSURE_BLOCKER_FIX_V1:TECHNADZOR_ACT_CREATED",
    }


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_TECHNADZOR_ENGINE ===


# === P6_TECHNADZOR_TEMPLATE_AND_ARTIFACT_CLOSE_20260504_V1 ===
# Scope:
# - technadzor sample/template files can be saved as active reference per chat/topic
# - future technadzor acts use active reference metadata
# - produces TXT and DOCX when python-docx exists; no DB schema changes

import json as _p6tz_json
import re as _p6tz_re
from datetime import datetime as _p6tz_datetime
from pathlib import Path as _p6tz_Path

_P6TZ_BASE = _p6tz_Path("/root/.areal-neva-core")
_P6TZ_TEMPLATE_DIR = _P6TZ_BASE / "data/templates/technadzor"
_P6TZ_OUT = _P6TZ_BASE / "outputs/technadzor"
_P6TZ_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
_P6TZ_OUT.mkdir(parents=True, exist_ok=True)

def _p6tz_s(v, limit=12000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6tz_low(v):
    return _p6tz_s(v).lower().replace("ё", "е")

def _p6tz_template_path(chat_id, topic_id):
    safe_chat = _p6tz_re.sub(r"[^0-9a-zA-Z_-]+", "_", str(chat_id or "unknown"))
    return _P6TZ_TEMPLATE_DIR / f"ACTIVE__chat_{safe_chat}__topic_{int(topic_id or 0)}.json"

def _p6tz_is_template_intent(text="", file_name=""):
    low = _p6tz_low(str(text) + " " + str(file_name))
    return any(x in low for x in ("образец", "шаблон", "пример", "как образец", "как шаблон", "возьми его как образец", "сохрани как образец")) and any(x in low for x in ("технадзор", "акт", "замечан", "дефект", "строительный контроль", "стройконтроль"))

def _p6tz_save_template(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name=""):
    meta = {
        "engine": "P6_TECHNADZOR_TEMPLATE_AND_ARTIFACT_CLOSE_20260504_V1",
        "kind": "technadzor_template",
        "status": "active",
        "chat_id": str(chat_id or ""),
        "topic_id": int(topic_id or 0),
        "source_task_id": str(task_id or ""),
        "source_file_path": str(file_path or ""),
        "source_file_name": str(file_name or ""),
        "raw_user_instruction": _p6tz_s(text, 4000),
        "usage_rule": "Use this file as formatting/sample reference for future technadzor acts in same chat/topic",
        "saved_at": _p6tz_datetime.now().isoformat(),
    }
    path = _p6tz_template_path(chat_id, topic_id)
    path.write_text(_p6tz_json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def _p6tz_load_template(chat_id, topic_id):
    path = _p6tz_template_path(chat_id, topic_id)
    if not path.exists():
        return {}
    try:
        return _p6tz_json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _p6tz_refs(text):
    refs = []
    for m in _p6tz_re.findall(r"\b(сп\s*\d+[.\d]*|гост\s*\d+[.\d-]*|снип\s*[\w.\-]+)\b", text or "", flags=_p6tz_re.I):
        refs.append(m.upper().replace("  ", " "))
    return ", ".join(sorted(set(refs))) if refs else "Норма не подтверждена"

def _p6tz_make_docx(path, lines):
    try:
        from docx import Document
        doc = Document()
        for i, line in enumerate(lines):
            if i == 0:
                doc.add_heading(line, level=1)
            elif line == "":
                doc.add_paragraph("")
            else:
                doc.add_paragraph(line)
        doc.save(str(path))
        return str(path)
    except Exception:
        return ""

try:
    _p6tz_orig_is_intent = is_technadzor_intent
    def is_technadzor_intent(text: str = "", file_name: str = "") -> bool:
        low = _p6tz_low(str(text) + " " + str(file_name))
        if _p6tz_is_template_intent(text, file_name):
            return True
        if any(x in low for x in ("технадзор", "акт", "замечан", "дефект", "нарушен", "освидетельств", "стройконтроль", "строительный контроль", "сп ", "гост", "снип")):
            return True
        return _p6tz_orig_is_intent(text, file_name)
except Exception:
    pass

try:
    _p6tz_orig_process = process_technadzor
    def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = ""):
        if _p6tz_is_template_intent(text, file_name):
            meta_path = _p6tz_save_template(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name)
            return {
                "ok": True,
                "handled": True,
                "kind": "technadzor_template_saved",
                "state": "DONE",
                "artifact_path": str(meta_path),
                "message": "Образец технадзора сохранён для этого топика",
                "history": "P6_TECHNADZOR_TEMPLATE_SAVED",
            }

        if not is_technadzor_intent(text, file_name):
            return {"ok": False, "handled": False, "reason": "NOT_TECHNADZOR"}

        tpl = _p6tz_load_template(chat_id, topic_id)
        ts = _p6tz_datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = str(task_id or ts)[:8] or ts
        stem = f"TECHNADZOR_ACT__{safe}"
        txt_path = _P6TZ_OUT / f"{stem}.txt"
        docx_path = _P6TZ_OUT / f"{stem}.docx"

        lines = [
            "АКТ ТЕХНИЧЕСКОГО НАДЗОРА",
            "",
            f"Дата: {_p6tz_datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Задача: {task_id}",
            f"Топик: {topic_id}",
        ]
        if file_name:
            lines.append(f"Файл: {file_name}")
        if tpl:
            lines.append(f"Образец: {tpl.get('source_file_name') or tpl.get('source_file_path') or 'активный шаблон топика'}")
        lines += [
            "",
            "Исходное описание:",
            _p6tz_s(text, 6000) or "UNKNOWN",
            "",
            "Нормативная база:",
            _p6tz_refs(text),
            "",
            "Выявленные замечания:",
            "1. Требуется заполнение по присланным фото/файлам и описанию",
            "",
            "Требуемые действия:",
            "1. Устранить замечания",
            "2. Предоставить фотофиксацию устранения",
            "3. Повторно предъявить участок работ техническому надзору",
            "",
            "Статус:",
            "Черновик подготовлен по текущим данным",
        ]

        txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        docx_created = _p6tz_make_docx(docx_path, lines)
        return {
            "ok": True,
            "handled": True,
            "kind": "technadzor_act",
            "state": "DONE",
            "artifact_path": docx_created or str(txt_path),
            "extra_artifact_path": str(txt_path),
            "message": "Технадзорный акт подготовлен",
            "history": "P6_TECHNADZOR_ACT_CREATED",
        }
except Exception:
    pass

# === END_P6_TECHNADZOR_TEMPLATE_AND_ARTIFACT_CLOSE_20260504_V1 ===

# === P6C_TECHNADZOR_CONN_COMPAT_TEMPLATE_ACT_CLOSE_20260504_V1 ===
import json as _p6c_te_json
import re as _p6c_te_re
from pathlib import Path as _p6c_te_Path
from datetime import datetime as _p6c_te_datetime

_P6C_TE_BASE = _p6c_te_Path("/root/.areal-neva-core")
_P6C_TE_OUT = _P6C_TE_BASE / "outputs" / "technadzor"
_P6C_TE_TPL = _P6C_TE_BASE / "data" / "templates" / "technadzor"
_P6C_TE_OUT.mkdir(parents=True, exist_ok=True)
_P6C_TE_TPL.mkdir(parents=True, exist_ok=True)

def _p6c_te_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6c_te_low(v):
    return _p6c_te_s(v).lower().replace("ё", "е")

def is_technadzor_intent(text: str = "", file_name: str = "") -> bool:
    low = _p6c_te_low(f"{text} {file_name}")
    return any(x in low for x in (
        "технадзор", "акт", "осмотр", "выезд", "дефект", "замечан",
        "образец написания", "образец акта", "как образец"
    ))

def _p6c_te_is_template(text, file_name):
    low = _p6c_te_low(f"{text} {file_name}")
    return any(x in low for x in (
        "образец", "как образец", "прими это как факт", "образец написания",
        "возьми это как образец", "шаблон"
    ))

def _p6c_te_read_text(file_path):
    fp = _p6c_te_Path(_p6c_te_s(file_path))
    if not fp.exists():
        return ""
    suf = fp.suffix.lower()
    try:
        if suf == ".txt":
            return fp.read_text(encoding="utf-8", errors="ignore")[:30000]
        if suf == ".pdf":
            try:
                import fitz
                doc = fitz.open(str(fp))
                return "\n".join(page.get_text("text") for page in doc)[:30000]
            except Exception:
                return ""
        if suf == ".docx":
            try:
                import docx
                d = docx.Document(str(fp))
                return "\n".join(p.text for p in d.paragraphs)[:30000]
            except Exception:
                return ""
    except Exception:
        return ""
    return ""

def _p6c_te_save_template(chat_id, topic_id, task_id, text, file_name, file_path):
    data = {
        "engine": "P6C_TECHNADZOR_CONN_COMPAT_TEMPLATE_ACT_CLOSE_20260504_V1",
        "chat_id": str(chat_id or ""),
        "topic_id": int(topic_id or 0),
        "task_id": str(task_id or ""),
        "file_name": _p6c_te_s(file_name),
        "file_path": _p6c_te_s(file_path),
        "saved_at": _p6c_te_datetime.utcnow().isoformat() + "Z",
        "template_text": _p6c_te_s(text, 25000),
    }
    out = _P6C_TE_TPL / f"ACTIVE__chat_{chat_id}__topic_{int(topic_id or 0)}.json"
    out.write_text(_p6c_te_json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out)

def _p6c_te_load_template(chat_id, topic_id):
    p = _P6C_TE_TPL / f"ACTIVE__chat_{chat_id}__topic_{int(topic_id or 0)}.json"
    if not p.exists():
        return {}
    try:
        return _p6c_te_json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _p6c_te_write_act(task_id, chat_id, topic_id, body):
    out = _P6C_TE_OUT / f"TECHNADZOR_ACT__{str(task_id)[:8]}.txt"
    out.write_text(body, encoding="utf-8")
    return str(out)

def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "", **kwargs):
    conn = kwargs.get("conn")
    raw_text = _p6c_te_s(text, 50000)
    file_name = _p6c_te_s(file_name or kwargs.get("name") or "")
    file_path = _p6c_te_s(file_path or kwargs.get("local_path") or "")
    task_id = _p6c_te_s(task_id or kwargs.get("id") or kwargs.get("task_id") or "technadzor")
    chat_id = _p6c_te_s(chat_id or kwargs.get("chat_id") or "")
    try:
        topic_id = int(topic_id or kwargs.get("topic_id") or 0)
    except Exception:
        topic_id = 0

    extracted = _p6c_te_read_text(file_path)
    combined = "\n".join(x for x in [raw_text, extracted] if x).strip()

    if _p6c_te_is_template(raw_text, file_name):
        tpl_path = _p6c_te_save_template(chat_id, topic_id, task_id, combined, file_name, file_path)
        return {
            "ok": True,
            "status": "DONE",
            "result_text": f"Образец технадзора принят и сохранён\nФайл: {file_name}\nШаблон: активен для topic_{topic_id}",
            "artifact_path": tpl_path,
            "history": "P6C_TECHNADZOR_TEMPLATE_SAVED",
        }

    tpl = _p6c_te_load_template(chat_id, topic_id)
    tpl_note = "Использован сохранённый образец" if tpl else "Сохранённый образец не найден"

    body = "\n".join([
        "АКТ ОСМОТРА ПО ФАКТУ ВЫЕЗДА",
        "",
        f"Дата формирования: {_p6c_te_datetime.now().strftime('%d.%m.%Y %H:%M')}",
        f"Файл: {file_name or 'без файла'}",
        f"Источник: topic_{topic_id}",
        f"Шаблон: {tpl_note}",
        "",
        "Исходные данные:",
        combined[:12000] if combined else "Данные из файла не извлечены автоматически",
        "",
        "Вывод технического надзора:",
        "Документ сформирован как рабочий черновик акта. Требуется проверка владельцем перед выдачей заказчику.",
    ])
    artifact = _p6c_te_write_act(task_id, chat_id, topic_id, body)

    return {
        "ok": True,
        "status": "DONE",
        "result_text": f"Акт технадзора сформирован\nФайл: {file_name or 'без файла'}\nАртефакт: {artifact}",
        "artifact_path": artifact,
        "history": "P6C_TECHNADZOR_ACT_CREATED",
    }
# === END_P6C_TECHNADZOR_CONN_COMPAT_TEMPLATE_ACT_CLOSE_20260504_V1 ===
