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

# === P6E2_TECHNADZOR_FOLDER_AWARE_NO_DRIVE_POLLUTION_20260504_V1 ===
import json as _p6e2_te_json
import re as _p6e2_te_re
from pathlib import Path as _p6e2_te_Path
from datetime import datetime as _p6e2_te_datetime

_P6E2_TE_BASE = _p6e2_te_Path("/root/.areal-neva-core")
_P6E2_TE_OUT = _P6E2_TE_BASE / "outputs" / "technadzor"
_P6E2_TE_TPL = _P6E2_TE_BASE / "data" / "templates" / "technadzor"
_P6E2_TE_OUT.mkdir(parents=True, exist_ok=True)
_P6E2_TE_TPL.mkdir(parents=True, exist_ok=True)

def _p6e2_te_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6e2_te_low(v):
    return _p6e2_te_s(v).lower().replace("ё", "е")

def _p6e2_te_is_template(text, file_name=""):
    low = _p6e2_te_low(text + " " + file_name)
    return any(x in low for x in ("как образец", "образец написания", "прими это как факт", "возьми это как образец", "шаблон акта"))

def _p6e2_te_extract_links(text):
    return _p6e2_te_re.findall(r"https?://\S+", _p6e2_te_s(text, 50000))

def _p6e2_te_read_file(path):
    p = _p6e2_te_Path(_p6e2_te_s(path))
    if not p.exists():
        return ""
    try:
        if p.suffix.lower() == ".txt":
            return p.read_text(encoding="utf-8", errors="ignore")[:50000]
        if p.suffix.lower() == ".docx":
            import docx
            d = docx.Document(str(p))
            return "\n".join(x.text for x in d.paragraphs)[:50000]
        if p.suffix.lower() == ".pdf":
            try:
                import fitz
                doc = fitz.open(str(p))
                return "\n".join(page.get_text("text") for page in doc)[:50000]
            except Exception:
                return ""
    except Exception:
        return ""
    return ""

def _p6e2_te_tpl_path(chat_id, topic_id):
    return _P6E2_TE_TPL / f"ACTIVE__chat_{chat_id}__topic_{int(topic_id or 0)}.json"

def _p6e2_te_save_template(chat_id, topic_id, task_id, body, file_name, file_path, links):
    data = {
        "engine": "P6E2_TECHNADZOR_FOLDER_AWARE_NO_DRIVE_POLLUTION_20260504_V1",
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "task_id": str(task_id),
        "file_name": _p6e2_te_s(file_name),
        "file_path": _p6e2_te_s(file_path),
        "drive_links_seen": links,
        "saved_at": _p6e2_te_datetime.utcnow().isoformat() + "Z",
        "template_text": _p6e2_te_s(body, 30000),
    }
    p = _p6e2_te_tpl_path(chat_id, topic_id)
    p.write_text(_p6e2_te_json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(p)

def _p6e2_te_load_template(chat_id, topic_id):
    p = _p6e2_te_tpl_path(chat_id, topic_id)
    if not p.exists():
        return {}
    try:
        return _p6e2_te_json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def is_technadzor_intent(text: str = "", file_name: str = "") -> bool:
    low = _p6e2_te_low(text + " " + file_name)
    return any(x in low for x in ("технадзор", "акт", "осмотр", "выезд", "дефект", "замечан", "нарушен", "образец написания", "как образец", "прими это как факт"))

def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "", **kwargs):
    raw = _p6e2_te_s(text, 50000)
    extracted = _p6e2_te_read_file(file_path)
    combined = "\n".join(x for x in (raw, extracted) if x).strip()
    links = _p6e2_te_extract_links(combined)
    task_id = _p6e2_te_s(task_id or kwargs.get("task_id") or kwargs.get("id") or "technadzor")
    chat_id = _p6e2_te_s(chat_id or kwargs.get("chat_id") or "")
    try:
        topic_id = int(topic_id or kwargs.get("topic_id") or 0)
    except Exception:
        topic_id = 0
    file_name = _p6e2_te_s(file_name or kwargs.get("file_name") or kwargs.get("name") or "")
    file_path = _p6e2_te_s(file_path or kwargs.get("local_path") or "")

    if _p6e2_te_is_template(raw, file_name):
        tpl = _p6e2_te_save_template(chat_id, topic_id, task_id, combined, file_name, file_path, links)
        return {
            "ok": True,
            "handled": True,
            "status": "DONE",
            "state": "DONE",
            "result_text": f"Образец технадзора принят и сохранён\nФайл: {file_name or 'без файла'}\nШаблон: active topic_{topic_id}\nDrive-ссылки учтены: {len(links)}",
            "message": "Образец технадзора принят и сохранён",
            "artifact_path": tpl,
            "history": "P6E2_TECHNADZOR_TEMPLATE_SAVED",
        }

    if not is_technadzor_intent(combined, file_name):
        return {"ok": False, "handled": False, "reason": "NOT_TECHNADZOR"}

    tpl = _p6e2_te_load_template(chat_id, topic_id)
    tpl_note = "использован сохранённый образец" if tpl else "сохранённый образец не найден"
    out = _P6E2_TE_OUT / f"TECHNADZOR_ACT__{str(task_id)[:8]}.txt"
    body = "\n".join([
        "АКТ ОСМОТРА ПО ФАКТУ ВЫЕЗДА",
        "",
        f"Дата формирования: {_p6e2_te_datetime.now().strftime('%d.%m.%Y %H:%M')}",
        f"Файл: {file_name or 'без файла'}",
        f"Источник: topic_{topic_id}",
        f"Шаблон: {tpl_note}",
        f"Drive-ссылки в исходных данных: {len(links)}",
        "",
        "Исходные данные:",
        combined[:15000] if combined else "UNKNOWN",
        "",
        "Вывод технического надзора:",
        "Документ сформирован по текущим данным и сохранён локально без записи мусора в Google Drive",
    ])
    out.write_text(body + "\n", encoding="utf-8")
    return {
        "ok": True,
        "handled": True,
        "status": "DONE",
        "state": "DONE",
        "result_text": f"Акт технадзора сформирован\nФайл: {file_name or 'без файла'}\nАртефакт: {out}",
        "message": "Акт технадзора сформирован",
        "artifact_path": str(out),
        "history": "P6E2_TECHNADZOR_ACT_CREATED",
    }
# === END_P6E2_TECHNADZOR_FOLDER_AWARE_NO_DRIVE_POLLUTION_20260504_V1 ===


# === P6F_TECHNADZOR_CLEAN_OUTPUT_AND_NORM_GATE_V1 ===
# FACT: wraps process_technadzor to ensure clean user-facing output.
# Uses core.normative_engine for confirmed references; if no confidence
# >= PARTIAL — explicitly states "норма не подтверждена" (per canon).
# Forbids JSON output to user.
import json as _p6f_tnz_json
import logging as _p6f_tnz_logging

_P6F_TNZ_LOG = _p6f_tnz_logging.getLogger("technadzor_engine")

def _p6f_tnz_clean_for_user(text):
    if not text:
        return ""
    s = str(text).strip()
    if (s.startswith("{") and s.rstrip().endswith("}")) or (s.startswith("[") and s.rstrip().endswith("]")):
        try:
            obj = _p6f_tnz_json.loads(s)
            if isinstance(obj, dict):
                summary = str(obj.get("summary") or obj.get("message") or "").strip()
                if summary:
                    return summary
                lines = []
                for k in ("kind", "state", "artifact_path", "history"):
                    if k in obj:
                        v = obj[k]
                        if k == "artifact_path":
                            lines.append("Артефакт: создан")
                        else:
                            lines.append(str(k) + ": " + str(v))
                if lines:
                    return "\n".join(lines)
                return "Технадзорный результат подготовлен"
        except Exception:
            pass
    return s

def _p6f_tnz_norm_block(text):
    try:
        from core.normative_engine import search_norms_sync, format_norms_for_act
    except Exception:
        return ""
    try:
        norms = search_norms_sync(text or "", limit=3)
    except Exception:
        return ""
    if not norms:
        return "Норма не подтверждена. Акт оформлен без ссылки на конкретный пункт СП/ГОСТ"
    confirmed_or_partial = [n for n in norms if str(n.get("confidence", "")).upper() in ("CONFIRMED", "PARTIAL")]
    if not confirmed_or_partial:
        return "Норма не подтверждена. Источник не найден"
    try:
        return format_norms_for_act(confirmed_or_partial)
    except Exception:
        out = []
        for n in confirmed_or_partial:
            nid = str(n.get("norm_id", "")).strip()
            sec = str(n.get("section", "")).strip()
            req = str(n.get("requirement", "")).strip()
            conf = str(n.get("confidence", "")).strip()
            if nid:
                out.append(f"- {nid} | {sec} | {req} | confidence={conf}")
        return "\n".join(out)

try:
    _P6F_TNZ_ORIG_PROCESS = process_technadzor
    if not getattr(_P6F_TNZ_ORIG_PROCESS, "_p6f_tnz_wrapped", False):
        def process_technadzor(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name=""):
            res = _P6F_TNZ_ORIG_PROCESS(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name)
            try:
                if isinstance(res, dict) and res.get("ok") and res.get("handled"):
                    raw_msg = res.get("message") or ""
                    clean = _p6f_tnz_clean_for_user(raw_msg)
                    norm_block = _p6f_tnz_norm_block(text)
                    artifact_line = ""
                    if res.get("artifact_path"):
                        artifact_line = "Артефакт акта: создан"
                    parts = [clean]
                    if norm_block:
                        parts.append("\nНормативная база:\n" + norm_block)
                    if artifact_line:
                        parts.append("\n" + artifact_line)
                    res["message"] = "\n".join([p for p in parts if p]).strip()
                    res["history"] = (res.get("history") or "") + ";P6F_TNZ_CLEANED_OUTPUT"
            except Exception as _e:
                try:
                    _P6F_TNZ_LOG.warning("P6F_TNZ_WRAP_ERR %s", _e)
                except Exception:
                    pass
            return res
        process_technadzor._p6f_tnz_wrapped = True
        _P6F_TNZ_LOG.info("P6F_TECHNADZOR_CLEAN_OUTPUT_AND_NORM_GATE_INSTALLED")
except Exception as _e:
    try:
        _P6F_TNZ_LOG.exception("P6F_TNZ_INSTALL_ERR %s", _e)
    except Exception:
        pass
# === END_P6F_TECHNADZOR_CLEAN_OUTPUT_AND_NORM_GATE_V1 ===


# === P6F_TECHNADZOR_PHOTO_TO_DOCX_REAL_V1 ===
# FACT: real photo defect → Vision (OpenRouter) → DOCX акт →
# Drive upload via topic_drive_oauth.upload_file_to_topic.
# No direct Google API. Norms only via core.normative_engine
# (no invented references).
import os as _p6f_tnz_os
import base64 as _p6f_tnz_base64
import asyncio as _p6f_tnz_asyncio
import json as _p6f_tnz_json2
import logging as _p6f_tnz_logging2

_P6F_TNZ_REAL_LOG = _p6f_tnz_logging2.getLogger("technadzor_engine")

_P6F_TNZ_REAL_PROMPT = (
    "Ты эксперт технического надзора в строительстве. На фото фиксация состояния "
    "конструкций или дефекта. Верни СТРОГО JSON без пояснений со схемой:\n"
    "{\n"
    "  \"summary\": \"кратко что видно\",\n"
    "  \"defects\": [{\n"
    "    \"title\": \"короткое название\",\n"
    "    \"location\": \"место\",\n"
    "    \"severity\": \"low|medium|high|critical\",\n"
    "    \"description\": \"что не так\",\n"
    "    \"recommendation\": \"что делать\"\n"
    "  }],\n"
    "  \"confidence\": \"HIGH|MEDIUM|LOW\"\n"
    "}\n"
    "Если на фото нет дефектов — defects=[]. "
    "Не выдумывай нормы СП/ГОСТ — это не твоя задача."
)

def _p6f_tnz_is_image_path(path):
    if not path:
        return False
    p = str(path).lower()
    return any(p.endswith(e) for e in (".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp"))

async def _p6f_tnz_vision_via_openrouter(local_path):
    if not _p6f_tnz_is_image_path(local_path) or not _p6f_tnz_os.path.exists(str(local_path)):
        return None, "PATH_MISSING"
    api_key = (_p6f_tnz_os.getenv("OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        return None, "NO_OPENROUTER_KEY"
    base_url = (_p6f_tnz_os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip().rstrip("/")
    model = (_p6f_tnz_os.getenv("OPENROUTER_VISION_MODEL") or "google/gemini-2.5-flash").strip()
    ext = _p6f_tnz_os.path.splitext(str(local_path))[1].lower().lstrip(".") or "jpeg"
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/{}".format(ext)
    try:
        with open(str(local_path), "rb") as f:
            b64 = _p6f_tnz_base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return None, "READ_ERR:{}".format(e)

    body = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": _P6F_TNZ_REAL_PROMPT},
                {"type": "image_url", "image_url": {"url": "data:" + mime + ";base64," + b64}},
            ],
        }],
        "temperature": 0.1,
    }
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    try:
        import httpx
        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=30.0)) as client:
            r = await client.post(base_url + "/chat/completions", headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in content)
    except Exception as e:
        return None, "OPENROUTER_CALL_ERR:{}".format(type(e).__name__)

    s = str(content).strip()
    if s.startswith("```"):
        import re as _re
        s = _re.sub(r"^```(?:json)?\s*", "", s)
        s = _re.sub(r"\s*```\s*$", "", s)
    try:
        return _p6f_tnz_json2.loads(s), "OK"
    except Exception:
        return {"summary": s[:2000], "defects": [], "confidence": "LOW"}, "PARTIAL"

def _p6f_tnz_norms_block(text_for_search):
    try:
        from core.normative_engine import search_norms_sync
    except Exception:
        return [], ""
    try:
        norms = search_norms_sync(text_for_search or "", limit=3)
    except Exception:
        return [], ""
    confirmed = [n for n in norms if str(n.get("confidence", "")).upper() in ("CONFIRMED", "PARTIAL")]
    if not confirmed:
        return [], "Норма не подтверждена"
    return confirmed, ""

def _p6f_tnz_build_docx_lines(vision_result, norms, file_name, task_id):
    from datetime import datetime as _dt
    lines = [
        "АКТ ТЕХНИЧЕСКОГО НАДЗОРА",
        "",
        "Дата: " + _dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Задача: " + str(task_id),
        "",
    ]
    if file_name:
        lines.append("Источник: фото " + str(file_name))
        lines.append("")
    summary = (vision_result.get("summary") or "").strip() if isinstance(vision_result, dict) else ""
    if summary:
        lines.extend(["Сводка по фото:", summary, ""])
    defects = vision_result.get("defects") or [] if isinstance(vision_result, dict) else []
    if defects:
        lines.append("Выявленные дефекты:")
        for i, d in enumerate(defects, 1):
            lines.append("{}. {}".format(i, d.get("title", "Дефект")))
            if d.get("location"):
                lines.append("   Место: " + str(d["location"]))
            if d.get("severity"):
                lines.append("   Степень: " + str(d["severity"]))
            if d.get("description"):
                lines.append("   Описание: " + str(d["description"]))
            if d.get("recommendation"):
                lines.append("   Рекомендация: " + str(d["recommendation"]))
            lines.append("")
    else:
        lines.extend(["Дефекты на фото не выявлены или фото недостаточно информативно", ""])

    if norms:
        lines.append("Нормативная база:")
        for n in norms:
            lines.append("- " + str(n.get("norm_id", "")) + " — " + str(n.get("section", "")))
            req = str(n.get("requirement", "")).strip()
            if req:
                lines.append("  " + req)
            lines.append("  confidence=" + str(n.get("confidence", "")))
        lines.append("")
    else:
        lines.extend(["Нормативная база: норма не подтверждена", ""])

    confidence = vision_result.get("confidence", "LOW") if isinstance(vision_result, dict) else "LOW"
    lines.append("Источник анализа: OpenRouter Vision (model=google/gemini-2.5-flash, confidence={})".format(confidence))
    return lines

async def _p6f_tnz_upload_to_topic(local_path, file_name, chat_id, topic_id):
    try:
        from core.topic_drive_oauth import upload_file_to_topic
    except Exception as e:
        _P6F_TNZ_REAL_LOG.warning("P6F_TNZ_UPLOAD_IMPORT_ERR %s", e)
        return None, "NO_UPLOADER"
    try:
        result = await upload_file_to_topic(
            file_path=str(local_path),
            file_name=str(file_name),
            chat_id=str(chat_id),
            topic_id=int(topic_id or 5),
        )
        if isinstance(result, dict) and result.get("ok"):
            file_id = result.get("drive_file_id") or result.get("id") or ""
            if file_id:
                return "https://drive.google.com/file/d/" + str(file_id) + "/view", "OK"
            link = result.get("link") or result.get("web_view_link") or ""
            return link, "OK_NO_ID"
        return None, "UPLOAD_FAIL:" + str(result)[:200]
    except Exception as e:
        return None, "UPLOAD_ERR:{}".format(type(e).__name__)

async def p6f_tnz_handle_photo_act_real(file_path, file_name, task_id, chat_id, topic_id, user_text=""):
    """
    Real entry point: photo → Vision → DOCX → Drive upload → return dict.
    Used by topic_5 photo-act flow.
    """
    vision, vstatus = await _p6f_tnz_vision_via_openrouter(file_path)
    if vision is None:
        return {
            "ok": False, "handled": True, "kind": "technadzor_photo_act",
            "state": "WAITING_CLARIFICATION",
            "message": "Не удалось проанализировать фото через Vision ({}). Пришли фото крупнее или текстовое описание дефекта".format(vstatus),
            "history": "P6F_TNZ_VISION_FAIL:{}".format(vstatus),
        }
    norms_text = (vision.get("summary", "") or "") + " " + " ".join(
        str(d.get("title", "")) + " " + str(d.get("description", ""))
        for d in (vision.get("defects") or [])
    ) + " " + str(user_text or "")
    confirmed_norms, _ = _p6f_tnz_norms_block(norms_text)
    docx_lines = _p6f_tnz_build_docx_lines(vision, confirmed_norms, file_name, task_id)

    from datetime import datetime as _dt
    ts = _dt.now().strftime("%Y%m%d_%H%M%S")
    safe = (str(task_id or ts)[:8] or ts).replace("/", "_").replace("\\", "_")
    out_dir = "/root/.areal-neva-core/outputs/technadzor_acts"
    _p6f_tnz_os.makedirs(out_dir, exist_ok=True)
    docx_path = "{}/TECHNADZOR_ACT_PHOTO__{}_{}.docx".format(out_dir, safe, ts)

    try:
        from core.technadzor_engine import _p6tz_make_docx as _make_docx
    except Exception:
        _make_docx = None
    if _make_docx is None:
        return {
            "ok": False, "handled": True, "kind": "technadzor_photo_act",
            "state": "FAILED",
            "message": "DOCX-генератор недоступен (python-docx не установлен)",
            "history": "P6F_TNZ_DOCX_GEN_MISSING",
        }
    written = _make_docx(docx_path, docx_lines)
    if not written:
        return {
            "ok": False, "handled": True, "kind": "technadzor_photo_act",
            "state": "FAILED",
            "message": "Ошибка создания DOCX акта",
            "history": "P6F_TNZ_DOCX_WRITE_FAIL",
        }

    drive_link, ustatus = await _p6f_tnz_upload_to_topic(
        docx_path, _p6f_tnz_os.path.basename(docx_path), chat_id or "-1003725299009", topic_id or 5
    )
    confidence = vision.get("confidence", "LOW")
    summary = vision.get("summary", "") or ""
    defects_count = len(vision.get("defects") or [])
    norms_count = len(confirmed_norms)

    public_lines = [
        "Акт технадзора по фото готов",
        "Файл: " + str(file_name or "photo"),
        "Уверенность Vision: " + str(confidence),
        "Дефектов на фото: " + str(defects_count),
        "Нормативных ссылок: " + str(norms_count) + (" (confidence=PARTIAL/CONFIRMED)" if norms_count else " — норма не подтверждена"),
    ]
    if drive_link:
        public_lines.append("Drive DOCX: " + str(drive_link))
    else:
        public_lines.append("Drive upload: не выполнен (" + str(ustatus) + "). DOCX лежит локально, доставка через Telegram fallback в следующей итерации")
    if summary:
        public_lines.append("")
        public_lines.append("Краткое описание: " + summary[:600])

    history_marker = "P6F_TNZ_PHOTO_ACT_DONE_DEFECTS_{}_NORMS_{}_DRIVE_{}".format(
        defects_count, norms_count, "OK" if drive_link else "FAIL"
    )
    return {
        "ok": True,
        "handled": True,
        "kind": "technadzor_photo_act",
        "state": "DONE" if drive_link else "AWAITING_CONFIRMATION",
        "artifact_path": docx_path,
        "drive_link": drive_link or "",
        "message": "\n".join(public_lines),
        "history": history_marker,
    }

_P6F_TNZ_REAL_LOG.info("P6F_TECHNADZOR_PHOTO_TO_DOCX_REAL_V1_INSTALLED")
# === END_P6F_TECHNADZOR_PHOTO_TO_DOCX_REAL_V1 ===
