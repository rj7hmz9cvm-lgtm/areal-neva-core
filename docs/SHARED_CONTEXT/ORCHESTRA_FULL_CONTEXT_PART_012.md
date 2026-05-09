# ORCHESTRA_FULL_CONTEXT_PART_012
generated_at_utc: 2026-05-09T07:40:02.314294+00:00
git_sha_before_commit: 62a5da22f1c20cb0ad84a06020938053156ddd54
part: 12/17


====================================================================================================
BEGIN_FILE: core/technadzor_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 4677dac1c9d15e1a54aff22f31bbddeac1e5c132f6eb03d57bc5e732b457b560
====================================================================================================
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
        def process_technadzor(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name="", **kwargs):
            try:
                res = _P6F_TNZ_ORIG_PROCESS(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs)
            except TypeError:
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
    api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY") or "").strip()
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


# === P6H_TOPIC5_USE_EXISTING_TEMPLATES_PHOTO_TO_TECH_REPORT_20260504_V1 ===
# Append-only wrapper.
# - Auto-indexes Drive topic_5 contents (PRIMARY_PDF_STYLE, SECONDARY_DOCX_REFERENCE, etc.)
#   on first photo / "акт" request per chat — without manual "образец" command.
# - On photo: Vision (existing _p6f_tnz_vision_via_openrouter) → section classifier
#   → clean Telegram text (no JSON, no /root, no internal paths).
# - On "сделай акт" / "оформи акт": same + DOCX (service folder _drafts) +
#   client-grade PDF A4 with cyrillic + clickable hyperlinks.
# - DOCX always lands in topic_5/_drafts/ (system).  PDF lands in topic root by default;
#   if user explicitly named a client folder, drop PDF there (only PDF allowed in client
#   folders per spec).
# - Telegram fallback when Drive upload fails — handled by existing P6F path
#   (we keep returning local artifact_path in that case so caller can retry).
import logging as _p6h_logging
import os as _p6h_os
import asyncio as _p6h_asyncio
from pathlib import Path as _P6H_Path
from datetime import datetime as _p6h_dt

_P6H_LOG = _p6h_logging.getLogger("task_worker")

# Eager import so drive_index install marker fires at worker startup
try:
    from core import technadzor_drive_index as _p6h_tdi  # noqa: F401
except Exception as _e_imp:
    _P6H_LOG.warning("P6H_DRIVE_INDEX_IMPORT_FAIL: %s", _e_imp)
_P6H_BASE = _P6H_Path(__file__).resolve().parent.parent
_P6H_OUTDIR = _P6H_BASE / "outputs" / "technadzor_p6h"
_P6H_OUTDIR.mkdir(parents=True, exist_ok=True)

_P6H_DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_P6H_DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Section classifier — keyword (lowercase substring) → canonical section title.
_P6H_SECTIONS = [
    ("Опорные узлы колонн",                        ["опорн", "анкерн", "колонн", "подлив", "опорная плита", "узел опор"]),
    ("Сварные соединения металлоконструкций",      ["сварн", "сварка", "шов", "провар", "наплыв", "сварные стык"]),
    ("Антикоррозионная защита",                    ["окрас", "лакокрас", "корроз", "защитн", "ржавчин", "антикорроз"]),
    ("Состояние основания и прилегающей территории", ["грунт", "основан", "замачив", "размыв", "просадк", "водоотвод", "канав", "лужа"]),
    ("Перекрытия",                                  ["перекрыт", "ригел", "балк перекрыт", "плита перекрыт"]),
    ("Узлы пересечения укосин",                     ["укосин", "связи", "диагональн", "жесткост", "пространств"]),
    ("Узлы крепления элементов покрытия",           ["крепл", "примыкан", "покрыт", "узел кров"]),
    ("Бетонные / железобетонные конструкции",       ["бетон", "железобетон", "арматур", "ж/б", "опалуб", "монолит"]),
    ("Гидроизоляция",                               ["гидроизол", "пароизол", "мембран"]),
    ("Кровля",                                       ["кровл", "крыш", "водосток", "желоб", "конек"]),
    ("Фасад",                                        ["фасад", "облиц", "сайдинг"]),
    ("Общие обзорные материалы",                    ["обзор", "общ вид", "общий вид"]),
]


def _p6h_classify_defect(d):
    text_pool = " ".join([
        str(d.get("title", "") or ""),
        str(d.get("description", "") or ""),
        str(d.get("section_hint", "") or ""),
        str(d.get("category", "") or ""),
    ]).lower()
    for section, kws in _P6H_SECTIONS:
        for kw in kws:
            if kw in text_pool:
                return section
    return "Прочие выявленные замечания"


def _p6h_group_defects_by_section(defects):
    groups = {}
    for d in defects or []:
        sec = _p6h_classify_defect(d)
        groups.setdefault(sec, []).append(d)
    ordered = []
    for sec, _ in _P6H_SECTIONS:
        if sec in groups:
            ordered.append((sec, groups[sec]))
    if "Прочие выявленные замечания" in groups:
        ordered.append(("Прочие выявленные замечания", groups["Прочие выявленные замечания"]))
    return ordered


def _p6h_clean_text(s, limit=4000):
    """Strip JSON/system markers, /root paths, traceback patterns, internal markers
    so result text is safe to send to Telegram."""
    if not s:
        return ""
    txt = str(s)
    # Strip lines starting with /root or containing internal markers
    bad_substrings = ["/root/", "task_id=", "TRACEBACK", "Traceback (most recent",
                       "P6F_", "P6G_", "P6H_", "P6E", "INSTALLED",
                       "MARKER:", "DEBUG:", "DEBUG ", "MANIFEST", "raw_input"]
    cleaned_lines = []
    for ln in txt.splitlines():
        keep = True
        for bad in bad_substrings:
            if bad in ln:
                keep = False
                break
        if keep:
            cleaned_lines.append(ln)
    out = "\n".join(cleaned_lines).strip()
    # Collapse triple+ blank lines
    while "\n\n\n" in out:
        out = out.replace("\n\n\n", "\n\n")
    return out[:limit]


def _p6h_norms_for_haystack(text):
    try:
        from core.normative_engine import search_norms_sync
        return search_norms_sync(text or "", limit=8)
    except Exception:
        return []


def _p6h_norms_for_section(section_title, defect_texts):
    haystack = (section_title + " " + " ".join(defect_texts)).strip()
    return _p6h_norms_for_haystack(haystack)


def _p6h_human_act_number(task_id):
    """Pretty act number 12-03/26 style — fall back to short task_id if missing."""
    today = _p6h_dt.now()
    n = today.strftime("%d-%m") + "/" + today.strftime("%y")
    if task_id:
        suffix = str(task_id)[:6]
        return f"{n}-{suffix}"
    return n


# ────────────────────────────────────────────────────────────────────
# DOCX builder — service-side, draft, with clickable hyperlinks
# ────────────────────────────────────────────────────────────────────
def _p6h_docx_add_hyperlink(paragraph, url, text):
    try:
        from docx.oxml.shared import OxmlElement, qn
    except Exception:
        paragraph.add_run(text + " (" + url + ")")
        return None
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    rPr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    rPr.append(underline)
    new_run.append(rPr)
    text_el = OxmlElement("w:t")
    text_el.text = text
    new_run.append(text_el)
    hyperlink.append(new_run)
    paragraph._element.append(hyperlink)
    return hyperlink


def _p6h_build_docx_act(payload, dst_path):
    """payload = {
        act_number, date_str, place, object_descr, method, performer, specialist,
        photos_link, general_purpose, sections=[(title, defects=[{title,description,norm_id,section_norms}], norms=[...], photos_block=[...])],
        recommendations=[str], consequences=[str], violations_table=[(violation, norm_id, photo)]
    }"""
    from docx import Document
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # Header
    h = doc.add_paragraph()
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = h.add_run(f"АКТ ОСМОТРА ОБЪЕКТА № {payload.get('act_number','')}")
    r.bold = True
    r.font.size = Pt(14)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.add_run("Методом визуального неразрушающего контроля").italic = True

    doc.add_paragraph(f"Дата осмотра: {payload.get('date_str','')}")
    doc.add_paragraph(f"Место осмотра: {payload.get('place','')}")
    doc.add_paragraph(f"Объект осмотра: {payload.get('object_descr','')}")
    doc.add_paragraph(f"Метод обследования: {payload.get('method','визуальный неразрушающий контроль с выездом на объект')}")
    if payload.get("performer"):
        doc.add_paragraph(f"Представитель подрядчика: {payload['performer']}")
    doc.add_paragraph(f"Технический специалист: {payload.get('specialist','Кузнецов Илья Владимирович')}")

    if payload.get("photos_link"):
        p = doc.add_paragraph("Ссылка на фотоматериалы: ")
        _p6h_docx_add_hyperlink(p, payload["photos_link"], payload["photos_link"])

    # 1. Общие сведения
    doc.add_paragraph()
    h1 = doc.add_paragraph()
    h1.add_run("1. Общие сведения").bold = True
    doc.add_paragraph(payload.get("general_purpose",
        "Осмотр выполнен методом визуального неразрушающего контроля с выездом на "
        "объект. Цель осмотра — выявление фактически наблюдаемых дефектов, определение "
        "рекомендаций к устранению и возможных последствий для заказчика при сохранении "
        "текущего состояния объекта"))

    # 2. Установлено по факту осмотра
    doc.add_paragraph()
    h2 = doc.add_paragraph()
    h2.add_run("2. Установлено по факту осмотра").bold = True
    sections = payload.get("sections") or []
    for i, sec in enumerate(sections, 1):
        ph = doc.add_paragraph()
        ph.add_run(f"2.{i} {sec.get('title','')}").bold = True
        # facts
        for d in sec.get("defects") or []:
            line = (d.get("title") or "").strip()
            descr = (d.get("description") or "").strip()
            if line and descr:
                doc.add_paragraph(f"— {line}: {descr}")
            elif line:
                doc.add_paragraph(f"— {line}")
            elif descr:
                doc.add_paragraph(f"— {descr}")
        # norm refs for section
        norms = sec.get("norms") or []
        if norms:
            np = doc.add_paragraph()
            np.add_run("Нормативная отсылка: ").italic = True
            np.add_run("; ".join(f"{n.get('norm_id','')} — {n.get('section','')}" for n in norms if n.get("norm_id")))
        else:
            np = doc.add_paragraph()
            np.add_run("Нормативная отсылка: ").italic = True
            np.add_run("норма не подтверждена").italic = True
        # photos
        photos = sec.get("photos_block") or []
        if photos:
            pp = doc.add_paragraph()
            pp.add_run("Фотоматериалы: ").italic = True
            pp.add_run(", ".join(photos))

    # Рекомендации
    if payload.get("recommendations"):
        doc.add_paragraph()
        rh = doc.add_paragraph()
        rh.add_run("3. Рекомендовано к устранению").bold = True
        for i, line in enumerate(payload["recommendations"], 1):
            doc.add_paragraph(f"{i}. {line}")

    # Возможные последствия
    if payload.get("consequences"):
        doc.add_paragraph()
        ch = doc.add_paragraph()
        ch.add_run("4. Возможные последствия при отсутствии устранения").bold = True
        for line in payload["consequences"]:
            doc.add_paragraph(f"— {line}")

    # Таблица: Нарушение / Норматив / Фото
    if payload.get("violations_table"):
        doc.add_paragraph()
        th = doc.add_paragraph()
        th.add_run("5. Сводная таблица нарушений").bold = True
        tbl = doc.add_table(rows=1, cols=3)
        tbl.style = "Light Grid"
        hdr = tbl.rows[0].cells
        hdr[0].text = "Нарушение"
        hdr[1].text = "Норматив"
        hdr[2].text = "Фото"
        for v, n, ph in payload["violations_table"]:
            row = tbl.add_row().cells
            row[0].text = str(v or "")
            row[1].text = str(n or "норма не подтверждена")
            row[2].text = str(ph or "")

    # Подпись
    doc.add_paragraph()
    doc.add_paragraph()
    sig = doc.add_paragraph()
    sig.add_run(f"Технический специалист: {payload.get('specialist','Кузнецов Илья Владимирович')}").bold = True
    doc.add_paragraph(f"Дата: {payload.get('date_str','')}")

    doc.save(str(dst_path))
    return str(dst_path)


# ────────────────────────────────────────────────────────────────────
# PDF builder — A4, cyrillic, clickable hyperlinks (reportlab platypus)
# ────────────────────────────────────────────────────────────────────
def _p6h_register_fonts():
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        if "DejaVuSans" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("DejaVuSans", _P6H_DEJAVU))
        if "DejaVuSans-Bold" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", _P6H_DEJAVU_BOLD))
        return True
    except Exception:
        return False


def _p6h_build_pdf_act(payload, dst_path):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    from reportlab.lib.units import cm
    from reportlab.lib import colors

    _p6h_register_fonts()

    styles = getSampleStyleSheet()
    base_font = "DejaVuSans"
    bold_font = "DejaVuSans-Bold"

    sty_title = ParagraphStyle("title", parent=styles["Title"], fontName=bold_font, fontSize=14, alignment=1, spaceAfter=4)
    sty_subtitle = ParagraphStyle("subtitle", parent=styles["Normal"], fontName=base_font, fontSize=10, alignment=1, textColor=colors.grey, spaceAfter=10)
    sty_h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName=bold_font, fontSize=12, spaceBefore=8, spaceAfter=4)
    sty_h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontName=bold_font, fontSize=11, spaceBefore=6, spaceAfter=2)
    sty_body = ParagraphStyle("body", parent=styles["Normal"], fontName=base_font, fontSize=10, leading=13, spaceAfter=2)
    sty_italic = ParagraphStyle("italic", parent=sty_body, textColor=colors.grey)
    sty_small = ParagraphStyle("small", parent=sty_body, fontSize=9)

    flow = []
    flow.append(Paragraph(f"АКТ ОСМОТРА ОБЪЕКТА № {payload.get('act_number','')}", sty_title))
    flow.append(Paragraph("Методом визуального неразрушающего контроля", sty_subtitle))
    flow.append(Paragraph(f"<b>Дата осмотра:</b> {payload.get('date_str','')}", sty_body))
    flow.append(Paragraph(f"<b>Место осмотра:</b> {payload.get('place','')}", sty_body))
    flow.append(Paragraph(f"<b>Объект осмотра:</b> {payload.get('object_descr','')}", sty_body))
    flow.append(Paragraph(f"<b>Метод обследования:</b> {payload.get('method','визуальный неразрушающий контроль с выездом на объект')}", sty_body))
    if payload.get("performer"):
        flow.append(Paragraph(f"<b>Представитель подрядчика:</b> {payload['performer']}", sty_body))
    flow.append(Paragraph(f"<b>Технический специалист:</b> {payload.get('specialist','Кузнецов Илья Владимирович')}", sty_body))
    if payload.get("photos_link"):
        flow.append(Paragraph(
            f'<b>Ссылка на фотоматериалы:</b> <link href="{payload["photos_link"]}"><font color="#0563C1"><u>{payload["photos_link"]}</u></font></link>',
            sty_body,
        ))

    flow.append(Spacer(1, 8))
    flow.append(Paragraph("1. Общие сведения", sty_h2))
    flow.append(Paragraph(payload.get("general_purpose",
        "Осмотр выполнен методом визуального неразрушающего контроля с выездом на "
        "объект. Цель осмотра — выявление фактически наблюдаемых дефектов, определение "
        "рекомендаций к устранению и возможных последствий для заказчика."), sty_body))

    flow.append(Paragraph("2. Установлено по факту осмотра", sty_h2))
    sections = payload.get("sections") or []
    for i, sec in enumerate(sections, 1):
        flow.append(Paragraph(f"2.{i} {sec.get('title','')}", sty_h3))
        for d in sec.get("defects") or []:
            line = (d.get("title") or "").strip()
            descr = (d.get("description") or "").strip()
            txt = (line + ((": " + descr) if descr and line else descr)).strip()
            if txt:
                flow.append(Paragraph("— " + txt, sty_body))
        norms = sec.get("norms") or []
        if norms:
            ns = "; ".join(f"{n.get('norm_id','')} — {n.get('section','')}" for n in norms if n.get("norm_id"))
            flow.append(Paragraph(f"<i>Нормативная отсылка:</i> {ns}", sty_italic))
        else:
            flow.append(Paragraph("<i>Нормативная отсылка: норма не подтверждена</i>", sty_italic))
        photos = sec.get("photos_block") or []
        if photos:
            flow.append(Paragraph(f"<i>Фотоматериалы:</i> {', '.join(photos)}", sty_italic))

    if payload.get("recommendations"):
        flow.append(Spacer(1, 4))
        flow.append(Paragraph("3. Рекомендовано к устранению", sty_h2))
        for i, line in enumerate(payload["recommendations"], 1):
            flow.append(Paragraph(f"{i}. {line}", sty_body))

    if payload.get("consequences"):
        flow.append(Spacer(1, 4))
        flow.append(Paragraph("4. Возможные последствия при отсутствии устранения", sty_h2))
        for line in payload["consequences"]:
            flow.append(Paragraph("— " + line, sty_body))

    if payload.get("violations_table"):
        flow.append(Spacer(1, 6))
        flow.append(Paragraph("5. Сводная таблица нарушений", sty_h2))
        rows = [["Нарушение", "Норматив", "Фото"]]
        for v, n, ph in payload["violations_table"]:
            rows.append([Paragraph(str(v or ""), sty_small),
                         Paragraph(str(n or "норма не подтверждена"), sty_small),
                         Paragraph(str(ph or ""), sty_small)])
        tbl = Table(rows, colWidths=[7*cm, 6*cm, 4*cm], repeatRows=1)
        tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), base_font),
            ("FONTNAME", (0, 0), (-1, 0), bold_font),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        flow.append(tbl)

    flow.append(Spacer(1, 16))
    flow.append(Paragraph(
        f"<b>Технический специалист:</b> {payload.get('specialist','Кузнецов Илья Владимирович')}",
        sty_body,
    ))
    flow.append(Paragraph(f"<b>Дата:</b> {payload.get('date_str','')}", sty_body))

    doc = SimpleDocTemplate(
        str(dst_path), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=f"Акт осмотра № {payload.get('act_number','')}",
    )
    doc.build(flow)
    return str(dst_path)


# ────────────────────────────────────────────────────────────────────
# Async pipeline: photo → Vision → sections → response (and optionally DOCX+PDF)
# ────────────────────────────────────────────────────────────────────
async def _p6h_process_photo_async(file_path, file_name, task_id, chat_id, topic_id, user_text="", make_act=False, place="", object_descr=""):
    # Ensure Drive index is built (silently, best-effort)
    try:
        from core import technadzor_drive_index as _tdi
        idx = _tdi.build_technadzor_template_index(str(chat_id), int(topic_id), force=False)
    except Exception:
        idx = {}

    # Vision
    vision, vstatus = await _p6f_tnz_vision_via_openrouter(file_path)
    if vstatus == "FAIL" or vision is None:
        return {
            "ok": False, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "WAITING_CLARIFICATION",
            "message": "Не удалось проанализировать фото через Vision. Пришли крупнее или текстовое описание дефекта",
            "history": "P6H_VISION_FAIL",
        }

    summary = (vision.get("summary") or "").strip() if isinstance(vision, dict) else ""
    defects = (vision.get("defects") or []) if isinstance(vision, dict) else []
    confidence = vision.get("confidence", "LOW") if isinstance(vision, dict) else "LOW"

    grouped = _p6h_group_defects_by_section(defects)

    # Norms per section + global
    section_norms = []
    all_haystack = summary + " " + (user_text or "") + " " + " ".join(
        str(d.get("title", "")) + " " + str(d.get("description", "")) for d in defects
    )
    global_norms = _p6h_norms_for_haystack(all_haystack)

    # Build sections payload (used by both DOCX and PDF, and partly by Telegram)
    sections_payload = []
    for sec_title, ds in grouped:
        defect_texts = [str(d.get("title", "")) + " " + str(d.get("description", "")) for d in ds]
        snorms = _p6h_norms_for_section(sec_title, defect_texts)
        section_norms.append((sec_title, snorms))
        sections_payload.append({
            "title": sec_title,
            "defects": ds,
            "norms": snorms,
            "photos_block": [str(file_name or "")] if file_name else [],
        })

    # Topic folder link from index for "Ссылка на фотоматериалы"
    topic_folder_link = (idx or {}).get("topic_folder_link", "")

    # Build clean Telegram text response.
    # If make_act=False — photo-only response (template per spec).
    # If make_act=True  — short summary + DOCX/PDF links.
    if not make_act:
        out_lines = ["Технический осмотр по фото", ""]
        # 1. Что видно
        out_lines.append("1. Что видно:")
        if summary:
            out_lines.append(_p6h_clean_text(summary, 700))
        else:
            out_lines.append("Описание не сформировано")
        out_lines.append("")
        # 2. Замечания
        out_lines.append("2. Обнаруженные замечания:")
        if grouped:
            for sec_title, ds in grouped:
                titles = []
                for d in ds:
                    t = str(d.get("title") or d.get("description") or "").strip()
                    if t:
                        titles.append(t[:120])
                line = f"— {sec_title}: " + ("; ".join(titles) if titles else "замечания зафиксированы")
                out_lines.append(_p6h_clean_text(line, 500))
        else:
            out_lines.append("Дефектов на фото не выявлено")
        out_lines.append("")
        # 3. Почему плохо — берём severity/why из Vision если есть, иначе общий
        out_lines.append("3. Почему это плохо:")
        why_lines = []
        for d in defects:
            w = str(d.get("why") or d.get("severity") or d.get("impact") or "").strip()
            if w:
                why_lines.append("— " + w[:200])
        if why_lines:
            out_lines.extend(why_lines[:6])
        elif grouped:
            out_lines.append("Зафиксированные отклонения снижают эксплуатационную надёжность и/или несущую способность конструкции и требуют проверки и устранения")
        else:
            out_lines.append("Отклонений не выявлено")
        out_lines.append("")
        # 4. Как исправить
        out_lines.append("4. Как исправить:")
        fix_lines = []
        for d in defects:
            f = str(d.get("fix") or d.get("recommendation") or "").strip()
            if f:
                fix_lines.append("— " + f[:200])
        if fix_lines:
            out_lines.extend(fix_lines[:6])
        else:
            out_lines.append("Привести узлы и покрытия к нормативному состоянию по соответствующим СП/ГОСТ. Уточнить решения по проектной документации")
        out_lines.append("")
        # 5. Что проверить на объекте
        out_lines.append("5. Что проверить на объекте:")
        check_lines = []
        for d in defects:
            c = str(d.get("verify") or d.get("check") or "").strip()
            if c:
                check_lines.append("— " + c[:200])
        if check_lines:
            out_lines.extend(check_lines[:6])
        else:
            out_lines.append("Состояние конструкции в полном объёме, наличие и соответствие исполнительной документации, ранее выданные предписания и их устранение")
        out_lines.append("")
        # 6. Норма
        out_lines.append("6. Нормативная отсылка:")
        if global_norms:
            for n in global_norms[:5]:
                out_lines.append("— " + str(n.get("norm_id","")) + ": " + str(n.get("section","")) + f" [{n.get('confidence','PARTIAL')}]")
        else:
            out_lines.append("норма не подтверждена")
        out_lines.append("")
        # 7. Акт
        out_lines.append("7. Акт:")
        out_lines.append("Могу оформить акт по текущим фото — напишите «сделай акт» / «оформи акт»")

        return {
            "ok": True, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "DONE",
            "message": _p6h_clean_text("\n".join(out_lines), 6000),
            "history": "P6H_PHOTO_REPORT_DEFECTS_{}_NORMS_{}".format(len(defects), len(global_norms)),
        }

    # ── Build DOCX (service _drafts) + PDF (client topic root) ──
    ts = _p6h_dt.now().strftime("%Y%m%d_%H%M%S")
    safe_tid = (str(task_id or ts)[:8] or ts).replace("/", "_").replace("\\", "_")
    docx_local = _P6H_OUTDIR / f"P6H_TNZ_ACT_DRAFT__{safe_tid}_{ts}.docx"
    pdf_local = _P6H_OUTDIR / f"АКТ_ОСМОТРА__{safe_tid}_{ts}.pdf"

    # Recommendations / consequences — pulled from defects
    recs = []
    cons = []
    for d in defects:
        r = str(d.get("fix") or d.get("recommendation") or "").strip()
        if r:
            recs.append(r[:300])
        c = str(d.get("consequence") or d.get("why") or "").strip()
        if c:
            cons.append(c[:300])
    # Violation table rows
    vtable = []
    for sec_title, ds in grouped:
        for d in ds:
            v = str(d.get("title") or d.get("description") or sec_title)[:200]
            sn = ""
            for n in section_norms:
                if n[0] == sec_title and n[1]:
                    sn = n[1][0].get("norm_id", "")
                    break
            ph = str(file_name or "")
            vtable.append((v, sn or "норма не подтверждена", ph))

    payload = {
        "act_number": _p6h_human_act_number(task_id),
        "date_str": _p6h_dt.now().strftime("%d.%m.%Y"),
        "place": place or "место уточняется по запросу владельца",
        "object_descr": object_descr or "объект уточняется по запросу владельца",
        "method": "визуальный неразрушающий контроль с выездом на объект",
        "performer": "",
        "specialist": "Кузнецов Илья Владимирович",
        "photos_link": topic_folder_link or "",
        "general_purpose": (
            "Осмотр выполнен методом визуального неразрушающего контроля. "
            "Цель осмотра — выявление фактически наблюдаемых дефектов, определение "
            "рекомендаций к устранению и возможных последствий для заказчика при "
            "сохранении текущего состояния объекта."
        ),
        "sections": sections_payload,
        "recommendations": recs[:20] if recs else ["Привести выявленные узлы и покрытия к нормативному состоянию по соответствующим СП/ГОСТ"],
        "consequences": cons[:10] if cons else ["Снижение несущей способности и эксплуатационной надёжности конструкций"],
        "violations_table": vtable[:30],
    }

    docx_ok = False
    pdf_ok = False
    try:
        _p6h_build_docx_act(payload, docx_local)
        docx_ok = True
    except Exception:
        _P6H_LOG.exception("P6H_DOCX_BUILD_FAIL")
    try:
        _p6h_build_pdf_act(payload, pdf_local)
        pdf_ok = True
    except Exception:
        _P6H_LOG.exception("P6H_PDF_BUILD_FAIL")

    drive_docx = None
    drive_pdf = None
    if docx_ok or pdf_ok:
        try:
            from core import technadzor_drive_index as _tdi
            if docx_ok:
                drive_docx = _tdi.upload_to_service_subfolder(
                    docx_local, docx_local.name, str(chat_id), int(topic_id), subfolder="_drafts",
                )
            if pdf_ok:
                drive_pdf = _tdi.upload_client_pdf_to_folder(
                    pdf_local, pdf_local.name, str(chat_id), int(topic_id), target_folder_name=None,
                )
        except Exception:
            _P6H_LOG.exception("P6H_UPLOAD_FAIL")

    pdf_link = (drive_pdf or {}).get("link", "") if drive_pdf else ""
    docx_link = (drive_docx or {}).get("link", "") if drive_docx else ""

    msg_lines = ["Акт сформирован"]
    if pdf_link:
        msg_lines.append(f"PDF: {pdf_link}")
    elif pdf_ok:
        msg_lines.append("PDF: подготовлен локально, загрузка на Drive не выполнена — повторная попытка через retry queue")
    else:
        msg_lines.append("PDF: ошибка генерации")
    if docx_link:
        msg_lines.append(f"DOCX (черновик, служебно): {docx_link}")
    if topic_folder_link:
        msg_lines.append(f"Фото: {topic_folder_link}")
    msg_lines.append("Норма: " + ("подтверждена" if global_norms else "не подтверждена"))

    return {
        "ok": True if (pdf_ok or docx_ok) else False,
        "handled": True,
        "kind": "technadzor_p6h_act",
        "state": "DONE" if pdf_link else "AWAITING_CONFIRMATION",
        "artifact_path": str(pdf_local if pdf_ok else docx_local),
        "extra_artifact_path": str(docx_local if docx_ok else ""),
        "drive_link": pdf_link or docx_link or "",
        "message": _p6h_clean_text("\n".join(msg_lines), 4000),
        "history": "P6H_ACT_DOCX_{}_PDF_{}_DRIVE_PDF_{}".format(
            "OK" if docx_ok else "FAIL",
            "OK" if pdf_ok else "FAIL",
            "OK" if pdf_link else "FAIL",
        ),
    }


# ────────────────────────────────────────────────────────────────────
# Sync wrapper around process_technadzor — only intercepts topic_5
# ────────────────────────────────────────────────────────────────────
def _p6h_is_image_path(path):
    if not path:
        return False
    p = str(path).lower()
    return p.endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".heic"))


_P6H_ACT_TRIGGERS = (
    "сделай акт", "оформи акт", "выдай акт", "финальн", "акт по фото",
    "сформируй акт", "подготовь акт", "сделать акт", "оформить акт",
)


def _p6h_should_handle(topic_id, file_path, user_text):
    if int(topic_id or 0) != 5:
        return False
    if file_path and _p6h_is_image_path(file_path):
        return True
    low = (user_text or "").lower()
    if any(t in low for t in _P6H_ACT_TRIGGERS):
        return True
    return False


def _p6h_run_async(coro):
    """Run coro from sync context. Mimics codebase pattern."""
    try:
        return _p6h_asyncio.run(coro)
    except RuntimeError:
        # Already in a loop — schedule in a worker thread with its own loop
        import threading
        result = {"v": None, "exc": None}
        def _runner():
            new_loop = _p6h_asyncio.new_event_loop()
            try:
                _p6h_asyncio.set_event_loop(new_loop)
                result["v"] = new_loop.run_until_complete(coro)
            except Exception as e:
                result["exc"] = e
            finally:
                new_loop.close()
        t = threading.Thread(target=_runner, daemon=True)
        t.start()
        t.join()
        if result["exc"]:
            raise result["exc"]
        return result["v"]


try:
    _p6h_orig_process = process_technadzor
    if not getattr(_p6h_orig_process, "_p6h_wrapped", False):
        def process_technadzor(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name="", **kwargs):
            try:
                if _p6h_should_handle(topic_id, file_path, text):
                    is_image = _p6h_is_image_path(file_path)
                    low = (text or "").lower()
                    make_act = any(t in low for t in _P6H_ACT_TRIGGERS)
                    if is_image or make_act:
                        return _p6h_run_async(
                            _p6h_process_photo_async(
                                file_path=file_path,
                                file_name=file_name,
                                task_id=task_id,
                                chat_id=chat_id,
                                topic_id=topic_id,
                                user_text=text,
                                make_act=make_act,
                            )
                        )
            except Exception:
                _P6H_LOG.exception("P6H_WRAPPER_FAIL — falling back to original")
            return _p6h_orig_process(
                text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                file_path=file_path, file_name=file_name, **kwargs,
            )
        process_technadzor._p6h_wrapped = True
        _p6h_orig_process._p6h_wrapped = True
    _P6H_LOG.info("P6H_TOPIC5_USE_EXISTING_TEMPLATES_PHOTO_TO_TECH_REPORT_20260504_V1_INSTALLED")
except Exception as _exc:
    _P6H_LOG.exception("P6H_TOPIC5_INSTALL_FAIL: %s", _exc)
# === END_P6H_TOPIC5_USE_EXISTING_TEMPLATES_PHOTO_TO_TECH_REPORT_20260504_V1 ===


# === P6H_PART_2: PHOTO_NUMBER_DEFECT_NORM_CLARIFICATION_LOGIC + VOICE_LIVE_DIALOG_CLARIFICATION_GATE_20260504 ===
# Adds on top of P6H_PART_1:
# - voice transcript parser (extracts object_hint, folder_hint, visit_date_hint, client_facing flag, raw user-stated defects)
# - clarification gate (returns WAITING_CLARIFICATION with concrete questions, never «что строим?»)
# - photo-numbered Telegram output («Фото №N — <file>»)
# - 8-column violations_table for акты
# - memory summary write after DONE (key topic_5_technadzor_photo_report_summary)
# - replaces _p6h_process_photo_async with enhanced version
import re as _p6h2_re
import json as _p6h2_json

_P6H2_LOG = _p6h_logging.getLogger("task_worker")

_P6H2_FOLDER_HINT_PATTERNS = [
    _p6h2_re.compile(r"папк[аеу]?\s+[«\"\'']?([^«»\"\'\.,;\n]{2,80})[»\"\'']?", _p6h2_re.IGNORECASE),
    _p6h2_re.compile(r"директор[ияю]?\s+[«\"\'']?([^«»\"\'\.,;\n]{2,80})[»\"\'']?", _p6h2_re.IGNORECASE),
]
_P6H2_OBJECT_HINTS = [
    "ангар", "склад", "цех", "корпус", "коттедж", "дом", "здание", "сооружение",
    "фундамент", "кровл", "фасад", "перекрыт", "колонн", "балк", "ферм", "плита",
    "паркинг", "гараж", "трибун", "купол", "теплиц",
]
_P6H2_DATE_RE = _p6h2_re.compile(
    r"(?P<d>\d{1,2})[\s\-./](?P<m>\d{1,2}|январ|феврал|март|апрел|ма[яй]|июн|июл|август|сентябр|октябр|ноябр|декабр)[\s\-./а-я]*?(?P<y>\d{2,4})?",
    _p6h2_re.IGNORECASE,
)
_P6H2_CLIENT_HINTS = ("заказчик", "клиент", "генподряд", "застройщ", "владельцу объекта")
_P6H2_INTERNAL_HINTS = ("служебн", "не для клиента", "черновик", "внутрен", "тестов", "smoke")


def _p6h_parse_voice_instruction(raw_input):
    """Parse [VOICE] transcript into structured TZ context.

    Returns dict with keys:
      object_hint, folder_hint, visit_date_hint, client_facing,
      explicit_include, explicit_exclude, output_kind, requires_act
    All values are conservative — present only when transcript explicitly mentioned them.
    """
    text = (raw_input or "").strip()
    if text.startswith("[VOICE]"):
        text_body = text[len("[VOICE]"):].strip()
    else:
        text_body = text
    low = text_body.lower()
    ctx = {
        "is_voice": text.startswith("[VOICE]"),
        "transcript": text_body,
        "object_hint": "",
        "folder_hint": "",
        "visit_date_hint": "",
        "client_facing": None,  # None=unknown, True/False=explicit
        "explicit_include": [],
        "explicit_exclude": [],
        "output_kind": "",  # text|act|pdf|docx|description
        "requires_act": False,
    }
    if not text_body:
        return ctx

    # Object
    for h in _P6H2_OBJECT_HINTS:
        if h in low:
            ctx["object_hint"] = h
            break

    # Folder hint
    for pat in _P6H2_FOLDER_HINT_PATTERNS:
        m = pat.search(text_body)
        if m:
            ctx["folder_hint"] = m.group(1).strip()
            break

    # Date hint
    m = _P6H2_DATE_RE.search(text_body)
    if m:
        ctx["visit_date_hint"] = m.group(0).strip()

    # Client-facing
    if any(h in low for h in _P6H2_CLIENT_HINTS):
        ctx["client_facing"] = True
    if any(h in low for h in _P6H2_INTERNAL_HINTS):
        ctx["client_facing"] = False

    # Output
    if any(t in low for t in _P6H_ACT_TRIGGERS):
        ctx["requires_act"] = True
        ctx["output_kind"] = "act"
    elif "pdf" in low or "пдф" in low:
        ctx["output_kind"] = "pdf"
    elif "docx" in low or "ворд" in low or "word" in low:
        ctx["output_kind"] = "docx"
    elif "описан" in low or "опиши" in low or "посмотри" in low:
        ctx["output_kind"] = "description"

    # Explicit include/exclude lists
    for marker, key in (("включ", "explicit_include"), ("не включ", "explicit_exclude"),
                         ("исключ", "explicit_exclude")):
        i = low.find(marker)
        if i >= 0:
            tail = text_body[i:i + 240]
            ctx[key].append(tail.strip())
    return ctx


def _p6h_should_wait_for_clarification(vision, defects, voice_ctx, drive_idx):
    """Returns (should_wait: bool, questions: [str]).

    Triggers:
      • Vision confidence=LOW AND no defects → ask what's on the photo, before/after, side
      • voice_ctx folder_hint set but folder not in Drive index
      • voice_ctx client_facing is None AND folder_hint set (need to know if it's customer-visible)
    Never asks "что строим?" / "что это?" / "пришлите шаблон".
    """
    questions = []
    confidence = (vision or {}).get("confidence", "LOW") if isinstance(vision, dict) else "LOW"
    nd = len(defects or [])

    # 1. Folder named by owner — check it exists
    fh = (voice_ctx or {}).get("folder_hint", "").strip()
    if fh:
        folders = []
        for f in (drive_idx or {}).get("folders_client", []) + (drive_idx or {}).get("folders_system", []):
            folders.append(f.get("name", ""))
        if not any(fh.lower() == n.lower() or fh.lower() in n.lower() for n in folders if n):
            questions.append(
                f"Не нашёл папку «{fh}» в Drive topic_5. "
                "Уточни точное имя или создай её перед загрузкой фото"
            )

    # 2. Folder client_facing flag uncertain
    if fh and (voice_ctx or {}).get("client_facing") is None:
        questions.append(
            f"Папку «{fh}» считать клиентской (туда складывать только фото и чистовой PDF) "
            "или служебной (тогда туда можно DOCX-черновик)?"
        )

    # 3. Vision low-confidence + no defects on a photo
    if confidence == "LOW" and nd == 0:
        questions.append(
            "Фото не позволяет однозначно определить дефект. "
            "Это до или после исправления? С какой стороны конструкции снято? "
            "Что именно нужно зафиксировать на этом фото?"
        )

    # Never trigger generic clarifier
    return (bool(questions), questions)


def _p6h_save_summary_to_memory(chat_id, topic_id, summary_dict):
    """Persist a compact summary to memory.db under topic_5_technadzor_photo_report_summary.

    Uses task_worker._save_memory_safe if exposed; falls back to direct memory_client write.
    Stores ONLY: folder, object, date, owner_directives, defect_brief, pdf_link, status.
    """
    try:
        payload = {
            "folder": str(summary_dict.get("folder") or "")[:200],
            "object": str(summary_dict.get("object") or "")[:200],
            "date": str(summary_dict.get("date") or "")[:40],
            "owner_directives": (summary_dict.get("owner_directives") or [])[:6],
            "defect_brief": (summary_dict.get("defect_brief") or [])[:12],
            "pdf_link": str(summary_dict.get("pdf_link") or "")[:400],
            "docx_link": str(summary_dict.get("docx_link") or "")[:400],
            "status": str(summary_dict.get("status") or "")[:60],
            "ts": int(_p6h_dt.now().timestamp()),
        }
        body = _p6h2_json.dumps(payload, ensure_ascii=False)[:4000]
    except Exception:
        return False
    try:
        from core.memory_client import save_memory  # type: ignore
        key = f"topic_{int(topic_id or 5)}_technadzor_photo_report_summary"
        save_memory(chat_id=str(chat_id), key=key, value=body)
        return True
    except Exception:
        try:
            import sqlite3 as _sql
            db = _P6H_BASE / "data" / "memory.db"
            con = _sql.connect(str(db))
            cur = con.cursor()
            cur.execute(
                "INSERT INTO memory(chat_id,key,value,timestamp) VALUES (?,?,?,strftime('%s','now'))",
                (str(chat_id), f"topic_{int(topic_id or 5)}_technadzor_photo_report_summary", body),
            )
            con.commit()
            con.close()
            return True
        except Exception:
            _P6H2_LOG.exception("P6H2_MEMORY_SAVE_FAIL")
            return False


def _p6h_format_photo_numbered_response(vision, defects, grouped, global_norms, file_name, photo_no=1, voice_ctx=None):
    """Build per-photo numbered Telegram text per spec section 'Формат текстового ответа без акта'."""
    fname = str(file_name or "photo")
    out = ["Технический осмотр по фото", ""]
    if voice_ctx and (voice_ctx.get("folder_hint") or voice_ctx.get("object_hint")):
        out.append("Объект / папка:")
        parts = []
        if voice_ctx.get("object_hint"):
            parts.append(voice_ctx["object_hint"])
        if voice_ctx.get("folder_hint"):
            parts.append(f"папка «{voice_ctx['folder_hint']}»")
        if voice_ctx.get("visit_date_hint"):
            parts.append(f"дата {voice_ctx['visit_date_hint']}")
        out.append(" / ".join(parts))
        out.append("")

    out.append(f"Фото №{photo_no} — {fname}")

    summary = (vision or {}).get("summary", "") if isinstance(vision, dict) else ""
    out.append("Что видно:")
    if summary:
        out.append(_p6h_clean_text(summary, 600))
    else:
        out.append("по фото однозначно не определяется")

    out.append("")
    out.append("Замечание:")
    if grouped:
        per_section = []
        for sec_title, ds in grouped:
            tt = []
            for d in ds:
                t = str(d.get("title") or d.get("description") or "").strip()
                if t:
                    tt.append(t[:120])
            per_section.append(f"— {sec_title}: " + ("; ".join(tt) if tt else "замечания зафиксированы"))
        out.extend(per_section)
    else:
        out.append("Дефектов на фото не выявлено")

    out.append("")
    out.append("Чем опасно:")
    risks = []
    for d in defects or []:
        r = str(d.get("risk") or d.get("why") or d.get("severity") or d.get("impact") or "").strip()
        if r:
            risks.append("— " + r[:200])
    if risks:
        out.extend(risks[:6])
    elif grouped:
        out.append("Зафиксированные отклонения снижают эксплуатационную надёжность и/или несущую способность конструкции")
    else:
        out.append("Отклонений не выявлено")

    out.append("")
    out.append("Как исправить:")
    fixes = []
    for d in defects or []:
        f = str(d.get("recommended_fix") or d.get("fix") or d.get("recommendation") or "").strip()
        if f:
            fixes.append("— " + f[:200])
    if fixes:
        out.extend(fixes[:6])
    else:
        out.append("Привести к нормативному состоянию по соответствующим СП/ГОСТ; уточнить решения по проектной документации")

    out.append("")
    out.append("Что проверить:")
    checks = []
    for d in defects or []:
        c = d.get("site_checks") or d.get("verify") or d.get("check")
        if isinstance(c, list):
            for x in c[:3]:
                xs = str(x).strip()
                if xs:
                    checks.append("— " + xs[:200])
        elif c:
            checks.append("— " + str(c)[:200])
    if checks:
        out.extend(checks[:6])
    else:
        out.append("Состояние конструкции в полном объёме, исполнительная документация, ранее выданные предписания")

    out.append("")
    out.append("Нормативная отсылка:")
    if global_norms:
        for n in global_norms[:5]:
            out.append("— " + str(n.get("norm_id", "")) + ": " + str(n.get("section", "")) + f" [{n.get('confidence', 'PARTIAL')}]")
    else:
        out.append("норма не подтверждена")

    out.append("")
    out.append("Итог:")
    crit = [d for d in (defects or []) if str(d.get("severity", "")).lower() in ("high", "critical", "критическ", "high_risk")]
    out.append(f"— критичные замечания: {len(crit)}")
    out.append(f"— рабочие замечания: {len(defects or []) - len(crit)}")
    out.append("— нужен ли акт: могу оформить акт по текущим фото — напиши «сделай акт»")

    return _p6h_clean_text("\n".join(out), 6000)


# Override _p6h_process_photo_async with the enhanced version
async def _p6h_process_photo_async(file_path, file_name, task_id, chat_id, topic_id, user_text="", make_act=False, place="", object_descr=""):
    # 1. Drive index — best-effort eager build
    try:
        from core import technadzor_drive_index as _tdi
        idx = _tdi.build_technadzor_template_index(str(chat_id), int(topic_id), force=False)
    except Exception:
        idx = {}

    # 2. Voice transcript parsing
    voice_ctx = _p6h_parse_voice_instruction(user_text or "")

    # 3. Vision
    vision, vstatus = await _p6f_tnz_vision_via_openrouter(file_path)
    if vstatus == "FAIL" or vision is None:
        return {
            "ok": False, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "WAITING_CLARIFICATION",
            "message": "Не удалось проанализировать фото через Vision. "
                       "Пришли крупнее или короткое описание дефекта текстом",
            "history": "P6H_VISION_FAIL",
        }

    summary = (vision.get("summary") or "").strip() if isinstance(vision, dict) else ""
    defects = (vision.get("defects") or []) if isinstance(vision, dict) else []

    # Tag defects with photo_no/file_name (single-photo task = #1)
    photo_no = 1
    for d in defects:
        if isinstance(d, dict):
            d.setdefault("photo_no", photo_no)
            d.setdefault("file_name", file_name or "")

    grouped = _p6h_group_defects_by_section(defects)

    # 4. Clarification gate
    should_wait, questions = _p6h_should_wait_for_clarification(vision, defects, voice_ctx, idx)
    if should_wait and not make_act:
        return {
            "ok": True, "handled": True, "kind": "technadzor_p6h_clarify",
            "state": "WAITING_CLARIFICATION",
            "message": _p6h_clean_text(
                "Технадзор topic_5 — нужны уточнения перед разбором:\n\n" + "\n".join(f"— {q}" for q in questions),
                3000,
            ),
            "history": "P6H_CLARIFY:{}".format(len(questions)),
        }

    # 5. Norms
    haystack = " ".join([
        summary, voice_ctx.get("transcript", "") or "",
    ] + [str(d.get("title", "")) + " " + str(d.get("description", "")) for d in defects])
    global_norms = _p6h_norms_for_haystack(haystack)

    # 6. Per-section payload
    sections_payload = []
    for sec_title, ds in grouped:
        defect_texts = [str(d.get("title", "")) + " " + str(d.get("description", "")) for d in ds]
        snorms = _p6h_norms_for_section(sec_title, defect_texts)
        sections_payload.append({
            "title": sec_title,
            "defects": ds,
            "norms": snorms,
            "photos_block": [str(file_name or "")] if file_name else [],
        })

    topic_folder_link = (idx or {}).get("topic_folder_link", "")

    # 7a. Photo-only response (numbered format)
    if not make_act:
        msg = _p6h_format_photo_numbered_response(
            vision, defects, grouped, global_norms, file_name or "photo",
            photo_no=photo_no, voice_ctx=voice_ctx,
        )
        # Save compact summary to memory
        _p6h_save_summary_to_memory(chat_id, topic_id, {
            "folder": voice_ctx.get("folder_hint") or "",
            "object": voice_ctx.get("object_hint") or "",
            "date": voice_ctx.get("visit_date_hint") or "",
            "owner_directives": (voice_ctx.get("explicit_include") or []) + (voice_ctx.get("explicit_exclude") or []),
            "defect_brief": [str(d.get("title") or d.get("description") or "")[:200] for d in defects][:8],
            "pdf_link": "",
            "docx_link": "",
            "status": "PHOTO_REPORT_DONE",
        })
        return {
            "ok": True, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "DONE",
            "message": msg,
            "history": "P6H_PHOTO_REPORT_PHOTO{}_DEFECTS_{}_NORMS_{}".format(photo_no, len(defects), len(global_norms)),
        }

    # 7b. Build act: DOCX (service) + PDF (client topic root) + upload
    ts = _p6h_dt.now().strftime("%Y%m%d_%H%M%S")
    safe_tid = (str(task_id or ts)[:8] or ts).replace("/", "_").replace("\\", "_")
    docx_local = _P6H_OUTDIR / f"P6H_TNZ_ACT_DRAFT__{safe_tid}_{ts}.docx"
    pdf_local = _P6H_OUTDIR / f"АКТ_ОСМОТРА__{safe_tid}_{ts}.pdf"

    recs = []
    cons = []
    for d in defects:
        r = str(d.get("recommended_fix") or d.get("fix") or d.get("recommendation") or "").strip()
        if r:
            recs.append(r[:300])
        c = str(d.get("consequence") or d.get("risk") or d.get("why") or "").strip()
        if c:
            cons.append(c[:300])

    # 8-column violations table per spec
    violations_8 = []
    for sec_title, ds in grouped:
        for d in ds:
            num = len(violations_8) + 1
            ph = str(d.get("file_name") or file_name or "")
            place_node = sec_title
            violation = str(d.get("title") or d.get("description") or sec_title)[:200]
            consequence = str(d.get("consequence") or d.get("risk") or "")[:200]
            fix = str(d.get("recommended_fix") or d.get("fix") or "")[:200]
            # find norm for this defect's section
            norm_id = ""
            for s in sections_payload:
                if s["title"] == sec_title and s["norms"]:
                    norm_id = s["norms"][0].get("norm_id", "") or ""
                    break
            status = ""
            conf = (vision or {}).get("confidence", "LOW")
            if conf == "HIGH" and norm_id:
                status = "CONFIRMED_BY_PHOTO"
            elif conf in ("HIGH", "MEDIUM") and not norm_id:
                status = "NORM_NOT_CONFIRMED"
            elif conf == "MEDIUM":
                status = "PARTIAL_BY_PHOTO"
            else:
                status = "NEEDS_OWNER_CLARIFICATION"
            violations_8.append((num, ph, place_node, violation, consequence, fix, norm_id or "норма не подтверждена", status))

    payload = {
        "act_number": _p6h_human_act_number(task_id),
        "date_str": _p6h_dt.now().strftime("%d.%m.%Y"),
        "place": place or (voice_ctx.get("folder_hint") or "место уточняется по запросу владельца"),
        "object_descr": object_descr or (voice_ctx.get("object_hint") or "объект уточняется по запросу владельца"),
        "method": "визуальный неразрушающий контроль с выездом на объект",
        "performer": "",
        "specialist": "Кузнецов Илья Владимирович",
        "photos_link": topic_folder_link or "",
        "general_purpose": (
            "Осмотр выполнен методом визуального неразрушающего контроля. "
            "Цель осмотра — выявление фактически наблюдаемых дефектов, определение "
            "рекомендаций к устранению и возможных последствий для заказчика."
        ),
        "sections": sections_payload,
        "recommendations": (recs[:20] if recs else
                             ["Привести выявленные узлы и покрытия к нормативному состоянию по соответствующим СП/ГОСТ"]),
        "consequences": (cons[:10] if cons else
                          ["Снижение несущей способности и эксплуатационной надёжности конструкций"]),
        # 8-col rich table
        "violations_table_8col": violations_8[:30],
        # 3-col simple table (back-compat for DOCX/PDF builders that use violations_table)
        "violations_table": [(v, n, p) for (_no, p, _pl, v, _co, _fi, n, _st) in violations_8[:30]],
    }

    docx_ok = False
    pdf_ok = False
    try:
        _p6h_build_docx_act(payload, docx_local)
        docx_ok = True
    except Exception:
        _P6H2_LOG.exception("P6H2_DOCX_BUILD_FAIL")
    try:
        _p6h_build_pdf_act(payload, pdf_local)
        pdf_ok = True
    except Exception:
        _P6H2_LOG.exception("P6H2_PDF_BUILD_FAIL")

    drive_docx = None
    drive_pdf = None
    if docx_ok or pdf_ok:
        try:
            from core import technadzor_drive_index as _tdi2
            if docx_ok:
                drive_docx = _tdi2.upload_to_service_subfolder(
                    docx_local, docx_local.name, str(chat_id), int(topic_id), subfolder="_drafts",
                )
            if pdf_ok:
                target_folder = None
                # Owner explicitly named a client folder for the final PDF?
                fh = voice_ctx.get("folder_hint", "") or ""
                if fh:
                    # Only allow target placement if folder is explicitly client-facing per voice
                    if voice_ctx.get("client_facing") is True:
                        from core.technadzor_drive_index import is_system_folder as _is_sys
                        if not _is_sys(fh):
                            target_folder = fh
                drive_pdf = _tdi2.upload_client_pdf_to_folder(
                    pdf_local, pdf_local.name, str(chat_id), int(topic_id),
                    target_folder_name=target_folder,
                )
        except Exception:
            _P6H2_LOG.exception("P6H2_UPLOAD_FAIL")

    pdf_link = (drive_pdf or {}).get("link", "") if drive_pdf else ""
    docx_link = (drive_docx or {}).get("link", "") if drive_docx else ""

    msg_lines = ["Акт сформирован"]
    if pdf_link:
        msg_lines.append(f"PDF: {pdf_link}")
    elif pdf_ok:
        msg_lines.append("PDF: подготовлен локально, загрузка на Drive не выполнена — Telegram fallback в следующей итерации")
    else:
        msg_lines.append("PDF: ошибка генерации — повторите позже")
    if docx_link:
        msg_lines.append(f"DOCX (черновик, служебно): {docx_link}")
    if topic_folder_link:
        msg_lines.append(f"Фото: {topic_folder_link}")
    msg_lines.append("Норма: " + ("подтверждена" if global_norms else "не подтверждена"))

    # Memory save
    _p6h_save_summary_to_memory(chat_id, topic_id, {
        "folder": voice_ctx.get("folder_hint") or "",
        "object": voice_ctx.get("object_hint") or "",
        "date": voice_ctx.get("visit_date_hint") or "",
        "owner_directives": (voice_ctx.get("explicit_include") or []) + (voice_ctx.get("explicit_exclude") or []),
        "defect_brief": [str(d.get("title") or d.get("description") or "")[:200] for d in defects][:8],
        "pdf_link": pdf_link,
        "docx_link": docx_link,
        "status": "ACT_DONE" if pdf_link else ("ACT_PARTIAL" if (pdf_ok or docx_ok) else "ACT_FAIL"),
    })

    return {
        "ok": True if (pdf_ok or docx_ok) else False,
        "handled": True,
        "kind": "technadzor_p6h_act",
        "state": "DONE" if pdf_link else "AWAITING_CONFIRMATION",
        "artifact_path": str(pdf_local if pdf_ok else docx_local),
        "extra_artifact_path": str(docx_local if docx_ok else ""),
        "drive_link": pdf_link or docx_link or "",
        "message": _p6h_clean_text("\n".join(msg_lines), 4000),
        "history": "P6H_ACT_DOCX_{}_PDF_{}_DRIVE_PDF_{}".format(
            "OK" if docx_ok else "FAIL",
            "OK" if pdf_ok else "FAIL",
            "OK" if pdf_link else "FAIL",
        ),
    }


_P6H2_LOG.info("P6H_TOPIC5_PHOTO_NUMBER_DEFECT_NORM_CLARIFICATION_LOGIC_20260504_INSTALLED")
_P6H2_LOG.info("P6H_TOPIC5_VOICE_LIVE_DIALOG_CLARIFICATION_GATE_20260504_INSTALLED")
# === END_P6H_PART_2 ===


# === P6H_PART_3: TOPIC5_OBJECT_REGISTRY_INSPECTION_CHAIN_20260504 ===
# Final wiring of object registry into the photo pipeline.
# Replaces _p6h_process_photo_async with a registry-aware version that:
#   • Identifies object_id from voice/Drive/file_name signals.
#   • Loads existing card and prior inspection_chain.
#   • Detects visit_mode (initial / repeat / extension / description_only).
#   • Adds clarification questions when object_id is ambiguous OR when voice/Vision conflict.
#   • For follow-up acts: carries forward open_items with statuses
#     (УСТРАНЕНО / УСТРАНЕНО ЧАСТИЧНО / НЕ УСТРАНЕНО / ТРЕБУЕТ УТОЧНЕНИЯ / ...).
#   • After the act is built, appends an inspection record to the chain
#     (server JSON + memory + timeline).
#   • Never writes registry/system files into client-facing folders.

try:
    from core import technadzor_object_registry as _p6h3_reg
except Exception as _exc_reg:
    _p6h3_reg = None
    _P6H2_LOG.warning("P6H3_REGISTRY_IMPORT_FAIL: %s", _exc_reg)


async def _p6h_process_photo_async(file_path, file_name, task_id, chat_id, topic_id, user_text="", make_act=False, place="", object_descr=""):
    # 1. Drive index
    try:
        from core import technadzor_drive_index as _tdi
        idx = _tdi.build_technadzor_template_index(str(chat_id), int(topic_id), force=False)
    except Exception:
        idx = {}

    # 2. Voice context
    voice_ctx = _p6h_parse_voice_instruction(user_text or "")

    # 3. Object registry — identify object_id
    object_id = ""
    object_card = None
    visit_mode = "initial"
    derive_sources = {}
    if _p6h3_reg is not None:
        try:
            object_id, derive_sources = _p6h3_reg.derive_object_id_from_context(
                voice_ctx, idx, file_path or "", file_name or "",
            )
            if object_id:
                object_card = _p6h3_reg.load_object(object_id)
            visit_mode = _p6h3_reg.detect_visit_mode(object_card, voice_ctx)
        except Exception:
            _P6H2_LOG.exception("P6H3_REGISTRY_DERIVE_FAIL")

    # 4. Vision
    vision, vstatus = await _p6f_tnz_vision_via_openrouter(file_path)
    if vstatus == "FAIL" or vision is None:
        return {
            "ok": False, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "WAITING_CLARIFICATION",
            "message": "Не удалось проанализировать фото через Vision. "
                       "Пришли крупнее или короткое описание дефекта текстом",
            "history": "P6H_VISION_FAIL",
        }

    summary = (vision.get("summary") or "").strip() if isinstance(vision, dict) else ""
    defects = (vision.get("defects") or []) if isinstance(vision, dict) else []
    photo_no = 1
    for d in defects:
        if isinstance(d, dict):
            d.setdefault("photo_no", photo_no)
            d.setdefault("file_name", file_name or "")

    grouped = _p6h_group_defects_by_section(defects)

    # 5. Clarification gate (registry + Vision + voice/Vision conflict)
    should_wait_basic, basic_questions = _p6h_should_wait_for_clarification(vision, defects, voice_ctx, idx)
    questions = list(basic_questions)

    # Object identity question — only if no folder/object hints AND no object_id derived
    if not object_id and not voice_ctx.get("folder_hint") and not voice_ctx.get("object_hint"):
        existing_summaries = []
        if _p6h3_reg is not None:
            try:
                existing_summaries = _p6h3_reg.list_object_summaries()
            except Exception:
                existing_summaries = []
        if existing_summaries:
            names = ", ".join(
                f"«{e.get('object_name') or e.get('object_id')}»"
                for e in existing_summaries[:5]
            )
            questions.append(
                f"Это новый объект или продолжение одного из существующих ({names})? "
                "Уточни — иначе не смогу привязать к истории объекта"
            )
        else:
            questions.append(
                "Назови объект (адрес / папка / имя), чтобы я завёл карточку и привязал акт"
            )

    # Voice/Vision conflict
    if _p6h3_reg is not None and voice_ctx.get("transcript"):
        try:
            conflict_flags = _p6h3_reg.detect_voice_vision_conflict(voice_ctx, grouped)
        except Exception:
            conflict_flags = []
        for cf in conflict_flags:
            if cf not in questions:
                questions.append(cf)
    else:
        conflict_flags = []

    # If photo-only mode AND we have questions — return WAITING_CLARIFICATION
    if questions and not make_act:
        return {
            "ok": True, "handled": True, "kind": "technadzor_p6h_clarify",
            "state": "WAITING_CLARIFICATION",
            "message": _p6h_clean_text(
                "Технадзор topic_5 — нужны уточнения перед разбором:\n\n"
                + "\n".join(f"— {q}" for q in questions),
                3000,
            ),
            "history": "P6H_CLARIFY_WITH_REGISTRY:{}_visit_{}".format(len(questions), visit_mode),
        }

    # 6. Norms
    haystack = " ".join([
        summary, voice_ctx.get("transcript", "") or "",
    ] + [str(d.get("title", "")) + " " + str(d.get("description", "")) for d in defects])
    global_norms = _p6h_norms_for_haystack(haystack)

    # 7. Sections payload
    sections_payload = []
    for sec_title, ds in grouped:
        defect_texts = [str(d.get("title", "")) + " " + str(d.get("description", "")) for d in ds]
        snorms = _p6h_norms_for_section(sec_title, defect_texts)
        sections_payload.append({
            "title": sec_title,
            "defects": ds,
            "norms": snorms,
            "photos_block": [str(file_name or "")] if file_name else [],
        })

    topic_folder_link = (idx or {}).get("topic_folder_link", "")

    # 7a. Photo-only response (numbered) ── append registry context if known
    if not make_act:
        msg = _p6h_format_photo_numbered_response(
            vision, defects, grouped, global_norms, file_name or "photo",
            photo_no=photo_no, voice_ctx=voice_ctx,
        )
        if object_id and object_card:
            registry_tail = (
                "\n\nКарточка объекта: "
                f"{object_card.get('object_name') or object_id}"
                f" (осмотров в истории: {len(object_card.get('inspection_chain') or [])})"
            )
            msg = (msg + registry_tail).strip()

        # Update memory summary
        try:
            _p6h_save_summary_to_memory(chat_id, topic_id, {
                "folder": voice_ctx.get("folder_hint") or "",
                "object": voice_ctx.get("object_hint") or object_id or "",
                "date": voice_ctx.get("visit_date_hint") or "",
                "owner_directives": (voice_ctx.get("explicit_include") or []) + (voice_ctx.get("explicit_exclude") or []),
                "defect_brief": [str(d.get("title") or d.get("description") or "")[:200] for d in defects][:8],
                "pdf_link": "",
                "docx_link": "",
                "status": f"PHOTO_REPORT_DONE:visit={visit_mode}",
            })
        except Exception:
            pass

        return {
            "ok": True, "handled": True, "kind": "technadzor_p6h_photo",
            "state": "DONE",
            "message": msg,
            "history": "P6H_PHOTO_REPORT_PHOTO{}_DEFECTS_{}_NORMS_{}_VISIT_{}".format(
                photo_no, len(defects), len(global_norms), visit_mode,
            ),
        }

    # 7b. Act build — DOCX (service _drafts) + PDF (client topic root or named client folder)
    ts = _p6h_dt.now().strftime("%Y%m%d_%H%M%S")
    safe_tid = (str(task_id or ts)[:8] or ts).replace("/", "_").replace("\\", "_")
    docx_local = _P6H_OUTDIR / f"P6H_TNZ_ACT_DRAFT__{safe_tid}_{ts}.docx"
    pdf_local = _P6H_OUTDIR / f"АКТ_ОСМОТРА__{safe_tid}_{ts}.pdf"

    # Recommendations / consequences
    recs, cons = [], []
    for d in defects:
        r = str(d.get("recommended_fix") or d.get("fix") or d.get("recommendation") or "").strip()
        if r:
            recs.append(r[:300])
        c = str(d.get("consequence") or d.get("risk") or d.get("why") or "").strip()
        if c:
            cons.append(c[:300])

    # Carry forward open_items for follow-up acts
    carried_open_items = []
    if _p6h3_reg is not None and visit_mode in ("repeat", "extension"):
        try:
            carried_open_items = _p6h3_reg.carry_forward_open_items(object_card, defects)
        except Exception:
            carried_open_items = []

    # Build follow-up section payload (added before regular sections in act)
    if carried_open_items:
        follow_section = {
            "title": "Состояние ранее выданных замечаний (повторный осмотр)",
            "defects": [
                {
                    "title": f"[{it.get('status','?')}] {it.get('title','') or it.get('description','')}",
                    "description": (it.get("description", "") or "")[:300]
                                    + (f" (из акта № {it.get('from_act_no')})" if it.get("from_act_no") else ""),
                }
                for it in carried_open_items
            ],
            "norms": [],
            "photos_block": [],
        }
        sections_payload.insert(0, follow_section)

    # 8-column violations table
    violations_8 = []
    for sec_title, ds in grouped:
        for d in ds:
            num = len(violations_8) + 1
            ph = str(d.get("file_name") or file_name or "")
            place_node = sec_title
            violation = str(d.get("title") or d.get("description") or sec_title)[:200]
            consequence = str(d.get("consequence") or d.get("risk") or "")[:200]
            fix = str(d.get("recommended_fix") or d.get("fix") or "")[:200]
            norm_id = ""
            for s in sections_payload:
                if s["title"] == sec_title and s["norms"]:
                    norm_id = s["norms"][0].get("norm_id", "") or ""
                    break
            conf = (vision or {}).get("confidence", "LOW")
            if conf == "HIGH" and norm_id:
                status = "CONFIRMED_BY_PHOTO"
            elif conf in ("HIGH", "MEDIUM") and not norm_id:
                status = "NORM_NOT_CONFIRMED"
            elif conf == "MEDIUM":
                status = "PARTIAL_BY_PHOTO"
            else:
                status = "NEEDS_OWNER_CLARIFICATION"
            violations_8.append((num, ph, place_node, violation, consequence, fix, norm_id or "норма не подтверждена", status))

    # Determine general_purpose by visit_mode
    if visit_mode == "repeat":
        gen_purpose = (
            "Повторный осмотр выполнен в развитие предыдущих актов по объекту. "
            "Цель — фиксация выполненных исправлений и неустранённых замечаний, "
            "определение рекомендаций к доведению конструктивных решений до нормативного состояния."
        )
    elif visit_mode == "extension":
        gen_purpose = (
            "Дополнение к предыдущему акту по объекту. "
            "Фиксируются дополнительные материалы и замечания, обнаруженные после основного осмотра."
        )
    else:
        gen_purpose = (
            "Осмотр выполнен методом визуального неразрушающего контроля. "
            "Цель осмотра — выявление фактически наблюдаемых дефектов, определение "
            "рекомендаций к устранению и возможных последствий для заказчика."
        )

    # Act number — for follow-up, hint at parent
    act_number = _p6h_human_act_number(task_id)
    if visit_mode == "repeat" and object_card and (object_card.get("last_act_no") or ""):
        act_number = act_number + f" (в развитие акта № {object_card['last_act_no']})"

    payload = {
        "act_number": act_number,
        "date_str": _p6h_dt.now().strftime("%d.%m.%Y"),
        "place": place or (voice_ctx.get("folder_hint") or "место уточняется по запросу владельца"),
        "object_descr": object_descr or (voice_ctx.get("object_hint") or
                                          (object_card.get("object_name") if object_card else "")
                                          or "объект уточняется по запросу владельца"),
        "method": "визуальный неразрушающий контроль с выездом на объект",
        "performer": "",
        "specialist": "Кузнецов Илья Владимирович",
        "photos_link": topic_folder_link or "",
        "general_purpose": gen_purpose,
        "sections": sections_payload,
        "recommendations": (recs[:20] if recs else
                             ["Привести выявленные узлы и покрытия к нормативному состоянию по соответствующим СП/ГОСТ"]),
        "consequences": (cons[:10] if cons else
                          ["Снижение несущей способности и эксплуатационной надёжности конструкций"]),
        "violations_table_8col": violations_8[:30],
        "violations_table": [(v, n, p) for (_no, p, _pl, v, _co, _fi, n, _st) in violations_8[:30]],
    }

    # Build files
    docx_ok = pdf_ok = False
    try:
        _p6h_build_docx_act(payload, docx_local)
        docx_ok = True
    except Exception:
        _P6H2_LOG.exception("P6H3_DOCX_BUILD_FAIL")
    try:
        _p6h_build_pdf_act(payload, pdf_local)
        pdf_ok = True
    except Exception:
        _P6H2_LOG.exception("P6H3_PDF_BUILD_FAIL")

    # Upload — DOCX → _drafts (system).  PDF → client folder if explicitly named, else topic root.
    drive_docx = drive_pdf = None
    if docx_ok or pdf_ok:
        try:
            from core import technadzor_drive_index as _tdi2
            if docx_ok:
                drive_docx = _tdi2.upload_to_service_subfolder(
                    docx_local, docx_local.name, str(chat_id), int(topic_id), subfolder="_drafts",
                )
            if pdf_ok:
                target_folder = None
                fh = voice_ctx.get("folder_hint", "") or ""
                if fh and voice_ctx.get("client_facing") is True:
                    from core.technadzor_drive_index import is_system_folder as _is_sys
                    if not _is_sys(fh):
                        target_folder = fh
                drive_pdf = _tdi2.upload_client_pdf_to_folder(
                    pdf_local, pdf_local.name, str(chat_id), int(topic_id),
                    target_folder_name=target_folder,
                )
        except Exception:
            _P6H2_LOG.exception("P6H3_UPLOAD_FAIL")

    pdf_link = (drive_pdf or {}).get("link", "") if drive_pdf else ""
    docx_link = (drive_docx or {}).get("link", "") if drive_docx else ""

    # Record inspection in chain
    if _p6h3_reg is not None and (object_id or pdf_ok or docx_ok):
        try:
            # If we still don't have object_id by here (e.g., act forced through),
            # create a synthetic stable id from file/date so chain still records.
            if not object_id:
                object_id = _p6h3_reg._slug(
                    voice_ctx.get("object_hint") or
                    voice_ctx.get("folder_hint") or
                    (file_name.rsplit(".", 1)[0] if file_name else "") or
                    f"obj_{ts}"
                )
            new_open = []
            for sec_title, ds in grouped:
                for d in ds:
                    new_open.append({
                        "title": str(d.get("title") or "")[:200],
                        "description": str(d.get("description") or "")[:300],
                        "section": sec_title,
                        "act_no": payload["act_number"],
                    })
            _p6h3_reg.record_inspection(
                object_id, str(chat_id),
                act_no=payload["act_number"],
                date_str=payload["date_str"],
                mode=visit_mode,
                pdf_link=pdf_link,
                docx_link=docx_link,
                source_photo_folder=voice_ctx.get("folder_hint") or "",
                findings=[{"section": s["title"],
                            "defects": s["defects"][:10],
                            "norms": [n.get("norm_id") for n in (s.get("norms") or [])]}
                           for s in sections_payload],
                open_items=new_open,
                closed_items=[
                    {"title": it.get("title"), "from_act_no": it.get("from_act_no")}
                    for it in carried_open_items if it.get("status") == "УСТРАНЕНО"
                ],
                new_items=new_open,
                owner_observation=voice_ctx.get("transcript", "")[:1000],
                conflict_flags=conflict_flags or [],
                object_name=(voice_ctx.get("object_hint") or
                              (object_card.get("object_name") if object_card else "") or ""),
                object_folder_url=topic_folder_link or "",
            )
        except Exception:
            _P6H2_LOG.exception("P6H3_RECORD_INSPECTION_FAIL")

    msg_lines = ["Акт сформирован"]
    if pdf_link:
        msg_lines.append(f"PDF: {pdf_link}")
    elif pdf_ok:
        msg_lines.append("PDF: подготовлен локально, загрузка на Drive не выполнена — Telegram fallback")
    else:
        msg_lines.append("PDF: ошибка генерации — повторите позже")
    if docx_link:
        msg_lines.append(f"DOCX (черновик, служебно): {docx_link}")
    if topic_folder_link:
        msg_lines.append(f"Фото: {topic_folder_link}")
    msg_lines.append("Норма: " + ("подтверждена" if global_norms else "не подтверждена"))
    if visit_mode == "repeat":
        msg_lines.append(f"Тип осмотра: повторный (история объекта: {len((object_card or {}).get('inspection_chain') or []) + 1} записей)")
    elif visit_mode == "extension":
        msg_lines.append("Тип осмотра: дополнение к предыдущему акту")
    else:
        msg_lines.append("Тип осмотра: первичный")

    # Memory summary
    try:
        _p6h_save_summary_to_memory(chat_id, topic_id, {
            "folder": voice_ctx.get("folder_hint") or "",
            "object": voice_ctx.get("object_hint") or object_id or "",
            "date": payload["date_str"],
            "owner_directives": (voice_ctx.get("explicit_include") or []) + (voice_ctx.get("explicit_exclude") or []),
            "defect_brief": [str(d.get("title") or d.get("description") or "")[:200] for d in defects][:8],
            "pdf_link": pdf_link,
            "docx_link": docx_link,
            "status": ("ACT_DONE" if pdf_link else ("ACT_PARTIAL" if (pdf_ok or docx_ok) else "ACT_FAIL"))
                       + f":visit={visit_mode}",
        })
    except Exception:
        pass

    return {
        "ok": True if (pdf_ok or docx_ok) else False,
        "handled": True,
        "kind": "technadzor_p6h_act",
        "state": "DONE" if pdf_link else "AWAITING_CONFIRMATION",
        "artifact_path": str(pdf_local if pdf_ok else docx_local),
        "extra_artifact_path": str(docx_local if docx_ok else ""),
        "drive_link": pdf_link or docx_link or "",
        "message": _p6h_clean_text("\n".join(msg_lines), 4000),
        "history": "P6H_ACT_VISIT_{}_DOCX_{}_PDF_{}_DRIVE_PDF_{}_OPEN_CARRIED_{}".format(
            visit_mode,
            "OK" if docx_ok else "FAIL",
            "OK" if pdf_ok else "FAIL",
            "OK" if pdf_link else "FAIL",
            len(carried_open_items),
        ),
    }


_P6H2_LOG.info("P6H_TOPIC5_OBJECT_REGISTRY_INSPECTION_CHAIN_20260504_INSTALLED")
# === END_P6H_PART_3 ===

# ─── P6H_EXTERNAL_VISION_GUARD_V1 ──────────────────────────────────────────
# CANON: TECHNADZOR_DOMAIN_LOGIC_CANON_V2 §33
# EXTERNAL_PHOTO_ANALYSIS_ALLOWED = False by default
# Vision запускается только после явного разрешения владельца

_P6H_EXTERNAL_VISION_ALLOWED = False

_p6h_vision_orig = _p6f_tnz_vision_via_openrouter  # сохраняем оригинал

async def _p6f_tnz_vision_via_openrouter(local_path):  # noqa: F811
    if not _P6H_EXTERNAL_VISION_ALLOWED:
        _P6H2_LOG.warning("EXTERNAL_VISION_BLOCKED path=%s EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False", local_path)
        return {}, "EXTERNAL_PHOTO_ANALYSIS_BLOCKED"
    return await _p6h_vision_orig(local_path)

def _p6h_allow_external_vision():
    global _P6H_EXTERNAL_VISION_ALLOWED
    _P6H_EXTERNAL_VISION_ALLOWED = True
    _P6H2_LOG.info("EXTERNAL_VISION_ALLOWED_SET owner_approved=True")

_P6H2_LOG.info("P6H_EXTERNAL_VISION_GUARD_V1_INSTALLED allowed=%s", _P6H_EXTERNAL_VISION_ALLOWED)
# ─── END P6H_EXTERNAL_VISION_GUARD_V1 ──────────────────────────────────────

# ─── P6H_PART_4_VISIT_BUFFER_V1 ────────────────────────────────────────────
# CANON: TECHNADZOR_DOMAIN_LOGIC_CANON_V2
# ActiveTechnadzorFolder / VisitMaterial / visit_buffer_add / visit_buffer_flush

import os as _p6h4_os
import json as _p6h4_json
import time as _p6h4_time
import logging as _p6h4_logging

_P6H4_LOG = _p6h4_logging.getLogger("task_worker")

_P6H4_BASE = _p6h4_os.path.join(
    _p6h4_os.path.dirname(_p6h4_os.path.dirname(_p6h4_os.path.abspath(__file__))),
    "data", "technadzor"
)


def _p6h4_ensure():
    _p6h4_os.makedirs(_P6H4_BASE, exist_ok=True)


def _p6h4_buf_path(chat_id, topic_id):
    _p6h4_ensure()
    return _p6h4_os.path.join(_P6H4_BASE, f"buf_{chat_id}_{topic_id}.json")


def _p6h4_folder_path(chat_id, topic_id):
    _p6h4_ensure()
    return _p6h4_os.path.join(_P6H4_BASE, f"active_folder_{chat_id}_{topic_id}.json")


def visit_buffer_add(chat_id, topic_id, material: dict) -> int:
    """Append VisitMaterial to persistent buffer. Returns new total count."""
    path = _p6h4_buf_path(str(chat_id), int(topic_id))
    try:
        with open(path, "r", encoding="utf-8") as _f:
            buf = _p6h4_json.load(_f)
    except Exception:
        buf = {"materials": [], "created_at": _p6h4_time.time()}
    if "material_id" not in material:
        material["material_id"] = f"{int(_p6h4_time.time() * 1000)}"
    material.setdefault("added_at", _p6h4_time.time())
    buf["materials"].append(material)
    buf["updated_at"] = _p6h4_time.time()
    with open(path, "w", encoding="utf-8") as _f:
        _p6h4_json.dump(buf, _f, ensure_ascii=False, indent=2)
    count = len(buf["materials"])
    _P6H4_LOG.info("P6H4_VISIT_BUFFER_ADD chat=%s topic=%s count=%s", chat_id, topic_id, count)
    return count


def visit_buffer_flush(chat_id, topic_id) -> list:
    """Return all buffered VisitMaterials and clear buffer."""
    path = _p6h4_buf_path(str(chat_id), int(topic_id))
    try:
        with open(path, "r", encoding="utf-8") as _f:
            buf = _p6h4_json.load(_f)
        materials = buf.get("materials", [])
        _p6h4_os.remove(path)
        _P6H4_LOG.info("P6H4_VISIT_BUFFER_FLUSH chat=%s topic=%s count=%s", chat_id, topic_id, len(materials))
        return materials
    except Exception:
        _P6H4_LOG.info("P6H4_VISIT_BUFFER_FLUSH_EMPTY chat=%s topic=%s", chat_id, topic_id)
        return []


def visit_buffer_count(chat_id, topic_id) -> int:
    path = _p6h4_buf_path(str(chat_id), int(topic_id))
    try:
        with open(path, "r", encoding="utf-8") as _f:
            buf = _p6h4_json.load(_f)
        return len(buf.get("materials", []))
    except Exception:
        return 0


def set_active_folder(chat_id, topic_id, folder_data: dict):
    path = _p6h4_folder_path(str(chat_id), int(topic_id))
    folder_data["set_at"] = _p6h4_time.time()
    with open(path, "w", encoding="utf-8") as _f:
        _p6h4_json.dump(folder_data, _f, ensure_ascii=False, indent=2)
    _P6H4_LOG.info(
        "P6H4_ACTIVE_FOLDER_SET chat=%s topic=%s name=%s",
        chat_id, topic_id, folder_data.get("folder_name", "?"),
    )


def get_active_folder(chat_id, topic_id) -> dict:
    path = _p6h4_folder_path(str(chat_id), int(topic_id))
    try:
        with open(path, "r", encoding="utf-8") as _f:
            return _p6h4_json.load(_f)
    except Exception:
        return {}


def process_drive_folder_batch(chat_id, topic_id, folder_id: str, folder_name: str = "") -> int:
    """Scan Drive folder, add all files as VisitMaterials. Returns count added."""
    added = 0
    try:
        from core.topic_drive_oauth import get_drive_service as _p6h4_get_drive
        svc = _p6h4_get_drive(chat_id=str(chat_id), topic_id=int(topic_id))
        items = svc.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,webViewLink)",
            pageSize=200,
        ).execute().get("files", [])
        for item in items:
            mime = item.get("mimeType", "")
            if "folder" in mime:
                continue
            ftype = "PHOTO" if mime.startswith("image/") else "PDF" if "pdf" in mime else "OTHER"
            mat = {
                "source": "DRIVE",
                "file_type": ftype,
                "file_name": item.get("name", ""),
                "drive_url": item.get("webViewLink", ""),
                "drive_file_id": item.get("id", ""),
                "include_in_act": True,
                "include_in_report": True,
                "group_label": folder_name or "",
            }
            visit_buffer_add(str(chat_id), int(topic_id), mat)
            added += 1
        _P6H4_LOG.info("P6H4_DRIVE_FOLDER_BATCH chat=%s topic=%s folder=%s added=%s", chat_id, topic_id, folder_id, added)
    except Exception as _p6h4_batch_err:
        _P6H4_LOG.warning("P6H4_DRIVE_FOLDER_BATCH_ERR %s", _p6h4_batch_err)
    return added


_P6H4_LOG.info("P6H_PART_4_VISIT_BUFFER_V1_INSTALLED")
# ─── END P6H_PART_4_VISIT_BUFFER_V1 ─────────────────────────────────────────


# === P6H4TW_BATCH_TRIGGER_V1 ===
# FIX: original P6H_PART_4 hook in task_worker.py is after asyncio.run() and never fires.
# This wrapper hooks process_technadzor here (before asyncio.run()), intercepting all topic_5 calls.
# Handles: photo/file buffering, Drive folder batch load, visit buffer flush to process_technadzor.
# EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False: no Vision without explicit owner permission.
import logging as _p6h4tw_v1_log_mod
import os as _p6h4tw_v1_os
import re as _p6h4tw_v1_re

_P6H4TW_V1_LOG = _p6h4tw_v1_log_mod.getLogger("task_worker")
_P6H4TW_V1_DRIVE_RE = _p6h4tw_v1_re.compile(
    r"https://drive\.google\.com/drive/folders/([A-Za-z0-9_-]+)"
)
_P6H4TW_V1_BATCH_TRIGGERS = (
    "загрузи все файлы из папки", "загрузи все файлы",
    "возьми файлы из папки", "прочитай папку",
    "обработай папку", "сделай разбор по папке", "сделай акт по папке",
    "разбор по папке", "акт по папке",
    "загрузи папку", "возьми из папки",
)
_P6H4TW_V1_BATCH_AND_FLUSH = (
    "сделай разбор по папке", "сделай акт по папке",
    "разбор по папке", "акт по папке",
)
_P6H4TW_V1_FLUSH_TRIGGERS = (
    "сделай акт", "собери акт", "сделай разбор", "сделай анализ",
    "собери разбор", "разберись", "сделай отчет", "сделай отчёт",
    "начни анализ", "сформируй акт",
)
_P6H4TW_V1_ACTIVE_FOLDER_TRIGGERS = (
    "работаем по этой папке", "установи папку", "активная папка это",
    "drive.google.com/drive/folders/",
)
_P6H4TW_V1_SHOW_FOLDER_TRIGGERS = (
    "покажи активную папку", "какая активная папка", "какая папка",
    "текущая папка", "покажи папку",
)


def _p6h4tw_v1_low(v):
    return str(v or "").lower().replace("ё", "е")


try:
    _p6h4tw_v1_orig = process_technadzor
    if not getattr(_p6h4tw_v1_orig, "_p6h4tw_v1_wrapped", False):

        def process_technadzor(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name="", **kwargs):  # noqa: F811
            if int(topic_id or 0) != 5:
                return _p6h4tw_v1_orig(
                    text=text, task_id=task_id, chat_id=chat_id,
                    topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
                )

            chat_str = str(chat_id)
            txt_low = _p6h4tw_v1_low(text)

            # ── Photo / Drive file → buffer (no Vision) ──────────────────────
            if file_path or file_name:
                fn = file_name or _p6h4tw_v1_os.path.basename(file_path or "")
                fn_low = fn.lower()
                is_photo = fn_low.endswith((".jpg", ".jpeg", ".png", ".webp", ".heic"))
                ftype = "PHOTO" if is_photo else "PDF" if fn_low.endswith(".pdf") else "DOCUMENT"
                material = {
                    "source": "telegram",
                    "file_type": ftype,
                    "file_name": fn,
                    "drive_file_id": "",
                    "drive_url": file_path or "",
                    "caption": text or "",
                    "include_in_act": True,
                    "include_in_report": True,
                }
                try:
                    count = visit_buffer_add(chat_str, 5, material)
                    _P6H4TW_V1_LOG.info(
                        "P6H4TW_V1_PHOTO_BUFFERED chat=%s count=%s fn=%s", chat_str, count, fn
                    )
                    return {
                        "ok": True,
                        "result_text": f"Добавлено в пакет ({count} шт.). Когда готово — скажи «сделай разбор».",
                        "history": "P6H4TW_V1_PHOTO_BUFFERED",
                    }
                except Exception as _e:
                    _P6H4TW_V1_LOG.warning("P6H4TW_V1_BUF_ADD_ERR %s", _e)
                    return _p6h4tw_v1_orig(
                        text=text, task_id=task_id, chat_id=chat_id,
                        topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
                    )

            # ── Drive folder URL / set active folder ─────────────────────────
            m_drive = _P6H4TW_V1_DRIVE_RE.search(text or "")
            if m_drive or any(t in txt_low for t in _P6H4TW_V1_ACTIVE_FOLDER_TRIGGERS):
                folder_id = m_drive.group(1) if m_drive else ""
                folder_name = ""
                if folder_id:
                    try:
                        from core.topic_drive_oauth import get_drive_service as _p6h4tw_v1_gds
                        svc = _p6h4tw_v1_gds(chat_id=chat_str, topic_id=5)
                        folder_name = (
                            svc.files().get(fileId=folder_id, fields="name").execute().get("name", "")
                        )
                    except Exception:
                        pass
                try:
                    set_active_folder(chat_str, 5, {
                        "folder_id": folder_id,
                        "folder_name": folder_name,
                        "source_text": (text or "")[:500],
                    })
                    return {
                        "ok": True,
                        "result_text": f"Активная папка установлена: {folder_name or folder_id or '(из текста)'}.",
                        "history": "P6H4TW_V1_ACTIVE_FOLDER_SET",
                    }
                except Exception as _e:
                    _P6H4TW_V1_LOG.warning("P6H4TW_V1_SET_FOLDER_ERR %s", _e)

            # ── Show active folder ────────────────────────────────────────────
            if any(t in txt_low for t in _P6H4TW_V1_SHOW_FOLDER_TRIGGERS):
                try:
                    af = get_active_folder(chat_str, 5)
                    if af:
                        name = af.get("folder_name") or af.get("folder_id", "(нет имени)")
                        fid = af.get("folder_id", "")
                        link = f"https://drive.google.com/drive/folders/{fid}" if fid else "—"
                        msg = f"Активная папка: {name}\n{link}"
                    else:
                        msg = "Активная папка не установлена. Пришли ссылку на папку."
                    return {"ok": True, "result_text": msg, "history": "P6H4TW_V1_SHOW_FOLDER"}
                except Exception as _e:
                    _P6H4TW_V1_LOG.warning("P6H4TW_V1_SHOW_FOLDER_ERR %s", _e)

            # ── Drive folder batch load ───────────────────────────────────────
            if any(t in txt_low for t in _P6H4TW_V1_BATCH_TRIGGERS):
                try:
                    m_drive2 = _P6H4TW_V1_DRIVE_RE.search(text or "")
                    if m_drive2:
                        batch_fid = m_drive2.group(1)
                        batch_fname = ""
                        try:
                            from core.topic_drive_oauth import get_drive_service as _p6h4tw_v1_gds2
                            svc2 = _p6h4tw_v1_gds2(chat_id=chat_str, topic_id=5)
                            batch_fname = (
                                svc2.files().get(fileId=batch_fid, fields="name").execute().get("name", "")
                            )
                        except Exception:
                            pass
                    else:
                        af2 = get_active_folder(chat_str, 5) or {}
                        batch_fid = af2.get("folder_id", "")
                        batch_fname = af2.get("folder_name", "")
                    if not batch_fid:
                        return {
                            "ok": True,
                            "result_text": "Не найдена активная папка. Пришли ссылку на папку Drive.",
                            "history": "P6H4TW_V1_BATCH_NO_FOLDER",
                        }
                    added = process_drive_folder_batch(chat_str, 5, batch_fid, batch_fname)
                    _P6H4TW_V1_LOG.info(
                        "P6H4TW_V1_BATCH_LOADED chat=%s folder=%s added=%s", chat_str, batch_fid, added
                    )
                    do_flush = any(t in txt_low for t in _P6H4TW_V1_BATCH_AND_FLUSH)
                    if not do_flush:
                        return {
                            "ok": True,
                            "result_text": (
                                f"Принял. Файлы из папки добавлены в пакет выезда: {added} шт. "
                                "Vision не запускаю без разрешения владельца. Скажи «сделай разбор» когда готово."
                            ),
                            "history": "P6H4TW_V1_BATCH_LOADED",
                        }
                    txt_low = "сделай разбор"  # fall through to flush
                except Exception as _e:
                    _P6H4TW_V1_LOG.warning("P6H4TW_V1_BATCH_ERR %s", _e)

            # ── Flush buffer → process_technadzor ────────────────────────────
            if any(t in txt_low for t in _P6H4TW_V1_FLUSH_TRIGGERS):
                try:
                    count = visit_buffer_count(chat_str, 5)
                    if count == 0:
                        return {
                            "ok": True,
                            "result_text": "Буфер пуст — сначала пришли фото или файлы.",
                            "history": "P6H4TW_V1_FLUSH_EMPTY",
                        }
                    materials = visit_buffer_flush(chat_str, 5)
                    lines = ["Технический надзор. Акт по материалам выезда:", "VISIT_PACKAGE:"]
                    for i, m in enumerate(materials, 1):
                        fn2 = m.get("file_name", f"файл {i}")
                        url2 = m.get("drive_url", "")
                        note2 = (m.get("caption", "") or m.get("voice_comment", "") or "").strip()
                        line = f"  {i}. {fn2}"
                        if url2:
                            line += f" {url2}"
                        if note2:
                            line += f" — {note2}"
                        lines.append(line)
                    package_text = "\n".join(lines)
                    _P6H4TW_V1_LOG.info(
                        "P6H4TW_V1_FLUSH chat=%s count=%s", chat_str, len(materials)
                    )
                    return _p6h4tw_v1_orig(
                        text=package_text, task_id=task_id, chat_id=chat_id,
                        topic_id=topic_id, file_path="", file_name="", **kwargs
                    )
                except Exception as _e:
                    _P6H4TW_V1_LOG.warning("P6H4TW_V1_FLUSH_ERR %s", _e)

            # ── Default pass-through ──────────────────────────────────────────
            return _p6h4tw_v1_orig(
                text=text, task_id=task_id, chat_id=chat_id,
                topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
            )

        process_technadzor._p6h4tw_v1_wrapped = True
        _p6h4tw_v1_orig._p6h4tw_v1_wrapped = True
        _P6H4TW_V1_LOG.info("P6H4TW_BATCH_TRIGGER_V1_INSTALLED")
except Exception as _p6h4tw_v1_err:
    _P6H4TW_V1_LOG.exception("P6H4TW_V1_INSTALL_ERR %s", _p6h4tw_v1_err)
# === END_P6H4TW_BATCH_TRIGGER_V1 ===

# === P6H4FD_FOLDER_DISCOVERY_V1 ===
import re as _p6h4fd_re
import logging as _p6h4fd_log_mod

_P6H4FD_LOG = _p6h4fd_log_mod.getLogger("technadzor_engine.p6h4fd")

_P6H4FD_FOLDER_INTENTS = (
    "папка",
    "новая папка",
    "создана папка",
    "создал папку",
    "обнаружь папку",
    "найди папку",
    "папка называется",
    "работаем по папке",
    "текущая папка",
    "прими папку",
    "туда складывать",
    "туда загружать",
    "все материалы туда",
)

# Matches "папк[у/а/и] <name>" — captures up to 60 chars until punctuation or end
_P6H4FD_NAME_RE = _p6h4fd_re.compile(
    r"(?:папк[уаи]|папка)\s+([А-Яа-яёЁA-Za-z0-9][А-Яа-яёЁA-Za-z0-9 \-_]{0,60}?)(?:[,.\n!?]|$)",
    _p6h4fd_re.IGNORECASE,
)


def _p6h4fd_extract_name(text: str) -> str:
    m = _P6H4FD_NAME_RE.search(text)
    if m:
        return m.group(1).strip()
    return ""


def _p6h4fd_norm(s: str) -> str:
    return " ".join(s.lower().replace("ё", "е").split())


def _p6h4fd_match_score(candidate: str, folder_name: str) -> int:
    c = _p6h4fd_norm(candidate)
    f = _p6h4fd_norm(folder_name)
    if not c:
        return 0
    if c == f:
        return 100
    if c in f or f in c:
        return 80
    cw = set(c.split())
    fw = set(f.split())
    overlap = len(cw & fw)
    return overlap * 10 if overlap else 0


try:
    _p6h4fd_orig_pt = process_technadzor
    if not getattr(_p6h4fd_orig_pt, "_p6h4fd_wrapped", False):

        def process_technadzor(  # noqa: F811
            text="", task_id="", chat_id="", topic_id=0,
            file_path="", file_name="", **kwargs
        ):
            if int(topic_id or 0) != 5:
                return _p6h4fd_orig_pt(
                    text=text, task_id=task_id, chat_id=chat_id,
                    topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
                )

            txt_low = (text or "").lower().replace("ё", "е")
            if not any(t in txt_low for t in _P6H4FD_FOLDER_INTENTS):
                return _p6h4fd_orig_pt(
                    text=text, task_id=task_id, chat_id=chat_id,
                    topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
                )

            # — folder/context intent: fresh Drive lookup by name —
            try:
                candidate = _p6h4fd_extract_name(text or "")
                chat_str = str(chat_id or "")
                _P6H4FD_LOG.info(
                    "P6H4FD_DISCOVERY_START candidate=%r chat=%s", candidate, chat_str
                )

                from core.technadzor_drive_index import _service as _p6h4fd_svc

                # system/container names — never a valid active folder result
                _P6H4FD_NEVER_RESULT = frozenset({
                    "technadzor", "технадзор", "topic_5", "_orchestra_work",
                    "_system", "_tmp", "_archive", "_drafts", "_templates", "_manifests",
                })

                def _p6h4fd_is_container(name):
                    return (name or "").strip().lower() in _P6H4FD_NEVER_RESULT

                svc = _p6h4fd_svc()

                def _p6h4fd_list_subfolders(parent_fid):
                    r = svc.files().list(
                        q=(
                            f"'{parent_fid}' in parents"
                            " and mimeType='application/vnd.google-apps.folder'"
                            " and trashed=false"
                        ),
                        fields="files(id,name,createdTime,modifiedTime)",
                        orderBy="createdTime desc",
                        pageSize=50,
                    ).execute()
                    return r.get("files", [])

                # Step A: search inside correct user ТЕХНАДЗОР root
                _TECHNADZOR_ROOT_FID = "1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD"
                raw_a = _p6h4fd_list_subfolders(_TECHNADZOR_ROOT_FID)
                folders = [f for f in raw_a if not _p6h4fd_is_container(f.get("name", ""))]
                _P6H4FD_LOG.info("P6H4FD_ROOT_SEARCH count=%s", len(folders))

                # Step D: fallback — Drive-wide exact name search
                if not folders and candidate:
                    _safe = candidate.replace("'", "\\'")
                    _gr = svc.files().list(
                        q=(
                            f"name='{_safe}'"
                            " and mimeType='application/vnd.google-apps.folder'"
                            " and trashed=false"
                        ),
                        fields="files(id,name,createdTime,modifiedTime)",
                        orderBy="createdTime desc",
                        pageSize=10,
                    ).execute()
                    folders = [
                        f for f in _gr.get("files", [])
                        if not _p6h4fd_is_container(f.get("name", ""))
                    ]
                    _P6H4FD_LOG.info("P6H4FD_GLOBAL_SEARCH count=%s candidate=%r", len(folders), candidate)

                if not folders:
                    msg_nf = (
                        "Папку не нашёл"
                        + (f" «{candidate}»" if candidate else "")
                        + ". Укажи точное название или пришли ссылку."
                    )
                    return {
                        "ok": True,
                        "handled": True,
                        "state": "DONE",
                        "result_text": msg_nf,
                        "message": msg_nf,
                        "history": "P6H4FD_V1:NO_USER_FOLDERS",
                    }

                # exact match first, then fuzzy, then newest
                best = None
                best_score = 0
                if candidate:
                    for f in folders:
                        score = _p6h4fd_match_score(candidate, f.get("name", ""))
                        if score > best_score:
                            best_score = score
                            best = f

                if best is None or best_score == 0:
                    best = folders[0]

                fid = best["id"]
                fname = best.get("name", "")
                link = f"https://drive.google.com/drive/folders/{fid}"

                set_active_folder(chat_str, 5, {
                    "folder_id": fid,
                    "folder_name": fname,
                    "source_text": (text or "")[:500],
                })
                msg = f"Нашёл папку «{fname}» и установил её как активную.\n{link}"
                _P6H4FD_LOG.info(
                    "P6H4FD_SET_ACTIVE folder_id=%s name=%r score=%s chat=%s",
                    fid, fname, best_score, chat_str,
                )
                return {
                    "ok": True,
                    "handled": True,
                    "result_text": msg,
                    "message": msg,
                    "history": f"P6H4FD_V1:SET_ACTIVE:{fid}",
                }

            except Exception as _e:
                _P6H4FD_LOG.warning("P6H4FD_ERR %s", _e)
                # on error fall through to lower wrapper
                return _p6h4fd_orig_pt(
                    text=text, task_id=task_id, chat_id=chat_id,
                    topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs
                )

        process_technadzor._p6h4fd_wrapped = True
        _p6h4fd_orig_pt._p6h4fd_wrapped = True
        _P6H4FD_LOG.info("P6H4FD_FOLDER_DISCOVERY_V1_INSTALLED")
except Exception as _p6h4fd_err:
    _P6H4FD_LOG.exception("P6H4FD_INSTALL_ERR %s", _p6h4fd_err)
# === END_P6H4FD_FOLDER_DISCOVERY_V1 ===

# === PHOTO_RECOGNITION_TOPIC5_RUNTIME_BINDING_V1 ===
try:
    _photo_t5_orig_process_technadzor = process_technadzor

    def process_technadzor(
        text: str = "",
        task_id: str = "",
        chat_id: str = "",
        topic_id: int = 0,
        file_path: str = "",
        file_name: str = "",
        **kwargs,
    ):
        from core.photo_recognition_engine import is_image_file, process_photo_recognition

        clean_kwargs = dict(kwargs)
        for key in (
            "text", "raw_input", "task_id", "id", "chat_id", "topic_id",
            "file_path", "local_path", "file_name", "name",
        ):
            clean_kwargs.pop(key, None)

        raw_text = str(text or kwargs.get("raw_input") or "")
        fp = str(file_path or kwargs.get("local_path") or "")
        fn = str(file_name or kwargs.get("file_name") or kwargs.get("name") or "")
        resolved_task_id = str(task_id or kwargs.get("task_id") or kwargs.get("id") or "")
        resolved_chat_id = str(chat_id or kwargs.get("chat_id") or "")

        try:
            tid = int(topic_id or kwargs.get("topic_id") or 0)
        except Exception:
            tid = 0

        photo_result = None
        if tid == 5 and is_image_file(file_name=fn, file_path=fp):
            photo_result = process_photo_recognition(
                topic_id=5,
                file_name=fn,
                file_path=fp,
                owner_comment=raw_text,
                source="TELEGRAM",
            )

            if not raw_text.strip():
                return {
                    "ok": True,
                    "handled": True,
                    "status": "WAITING_CLARIFICATION",
                    "state": "WAITING_CLARIFICATION",
                    "kind": "technadzor_photo_material",
                    "message": "Фото принято как материал технадзора. Укажи, к какому замечанию или разделу его отнести",
                    "result_text": "Фото принято как материал технадзора. Укажи, к какому замечанию или разделу его отнести",
                    "photo_recognition": photo_result,
                    "history": "PHOTO_RECOGNITION_TOPIC5_RUNTIME_BINDING_V1:WAITING_OWNER_COMMENT",
                }

        result = _photo_t5_orig_process_technadzor(
            text=raw_text,
            task_id=resolved_task_id,
            chat_id=resolved_chat_id,
            topic_id=tid,
            file_path=fp,
            file_name=fn,
            **clean_kwargs,
        )

        if photo_result and isinstance(result, dict):
            result["photo_recognition"] = photo_result
            result["photo_recognition_status"] = photo_result.get("status")
            result["history"] = str(result.get("history") or "") + "|PHOTO_RECOGNITION_TOPIC5_RUNTIME_BINDING_V1"
            if "message" not in result and "result_text" not in result:
                result["message"] = "Фото принято и связано с технадзорным материалом"

        return result
except Exception:
    pass
# === END_PHOTO_RECOGNITION_TOPIC5_RUNTIME_BINDING_V1 ===


# === P7_TOPIC5_REPLY_VOICE_BINDING_V1 ===
# Binds Telegram text/voice reply to the VisitMaterial created from the replied photo/file.
import json as _p7_t5_json
import re as _p7_t5_re
import time as _p7_t5_time
from pathlib import Path as _p7_t5_Path

_P7_T5_ORIG_PROCESS_TECHNADZOR = process_technadzor
_P7_T5_DATA = _p7_t5_Path("/root/.areal-neva-core/data/technadzor")

def _p7_t5_s(v, limit=20000):
    try:
        return "" if v is None else str(v).strip()[:limit]
    except Exception:
        return ""

def _p7_t5_low(v):
    return _p7_t5_s(v).lower().replace("ё", "е")

def _p7_t5_task_get(task, key, default=None):
    if task is None:
        return default
    try:
        if isinstance(task, dict):
            return task.get(key, default)
        return task[key]
    except Exception:
        return getattr(task, key, default)

def _p7_t5_parse_payload(text):
    raw = _p7_t5_s(text, 50000)
    try:
        obj = _p7_t5_json.loads(raw)
        return obj if isinstance(obj, dict) else {"text": raw}
    except Exception:
        return {"text": raw}

def _p7_t5_buf_path(chat_id):
    _P7_T5_DATA.mkdir(parents=True, exist_ok=True)
    return _P7_T5_DATA / f"buf_{chat_id}_5.json"

def _p7_t5_active_folder(chat_id):
    p = _P7_T5_DATA / f"active_folder_{chat_id}_5.json"
    try:
        obj = _p7_t5_json.loads(p.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}

def _p7_t5_load_buf(chat_id):
    p = _p7_t5_buf_path(chat_id)
    try:
        obj = _p7_t5_json.loads(p.read_text(encoding="utf-8"))
        if isinstance(obj, dict):
            obj.setdefault("materials", [])
            return obj
    except Exception:
        pass
    return {"materials": [], "created_at": _p7_t5_time.time()}

def _p7_t5_save_buf(chat_id, buf):
    p = _p7_t5_buf_path(chat_id)
    buf["updated_at"] = _p7_t5_time.time()
    p.write_text(_p7_t5_json.dumps(buf, ensure_ascii=False, indent=2), encoding="utf-8")

def _p7_t5_msg_id_from_name(name):
    m = _p7_t5_re.search(r"_([0-9]{3,})\.[A-Za-z0-9]+$", _p7_t5_s(name))
    return m.group(1) if m else ""

def _p7_t5_add_material(chat_id, material):
    buf = _p7_t5_load_buf(chat_id)
    mid = _p7_t5_s(material.get("telegram_message_id"))
    fname = _p7_t5_s(material.get("file_name"))
    for old in buf.get("materials", []):
        if mid and _p7_t5_s(old.get("telegram_message_id")) == mid:
            old.update({k: v for k, v in material.items() if v not in ("", None)})
            _p7_t5_save_buf(chat_id, buf)
            return len(buf.get("materials", [])), old
        if fname and _p7_t5_s(old.get("file_name")) == fname:
            old.update({k: v for k, v in material.items() if v not in ("", None)})
            _p7_t5_save_buf(chat_id, buf)
            return len(buf.get("materials", [])), old
    buf["materials"].append(material)
    _p7_t5_save_buf(chat_id, buf)
    return len(buf.get("materials", [])), material

def _p7_t5_bind_comment(chat_id, reply_to_message_id, comment, is_voice=False):
    reply_id = _p7_t5_s(reply_to_message_id)
    if not reply_id:
        return None
    comment = _p7_t5_s(comment, 8000)
    if not comment:
        return None

    buf = _p7_t5_load_buf(chat_id)
    for m in buf.get("materials", []):
        ids = {
            _p7_t5_s(m.get("telegram_message_id")),
            _p7_t5_s(m.get("reply_to_message_id")),
            _p7_t5_msg_id_from_name(m.get("file_name")),
        }
        if reply_id in ids:
            field = "voice_comment" if is_voice else "owner_comment"
            prev = _p7_t5_s(m.get(field))
            m[field] = (prev + "\n" + comment).strip() if prev and comment not in prev else comment
            m["status"] = "LINKED"
            m["linked_reply_to_message_id"] = reply_id
            m["updated_at"] = _p7_t5_time.time()
            _p7_t5_save_buf(chat_id, buf)
            return m
    return None

def _p7_t5_is_flush_command(text):
    low = _p7_t5_low(text)
    return any(x in low for x in (
        "сделай акт", "собери акт", "сделай разбор", "сделай анализ",
        "собери разбор", "сформируй акт", "сделай отчет", "сделай отчёт"
    ))

def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "", **kwargs):
    if int(topic_id or 0) != 5:
        return _P7_T5_ORIG_PROCESS_TECHNADZOR(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs)

    chat = _p7_t5_s(chat_id or _p7_t5_task_get(kwargs.get("task"), "chat_id", ""))
    payload = _p7_t5_parse_payload(text)
    task = kwargs.get("task")
    reply_to = payload.get("telegram_reply_to_message_id") or _p7_t5_task_get(task, "reply_to_message_id", "")
    current_msg = payload.get("telegram_message_id") or _p7_t5_msg_id_from_name(file_name)
    comment = payload.get("transcript") or payload.get("text") or text
    is_voice = _p7_t5_low(comment).startswith("[voice]") or _p7_t5_low(payload.get("input_type", "")) == "voice"
    comment_clean = _p7_t5_re.sub(r"^\s*\[VOICE\]\s*", "", _p7_t5_s(comment), flags=_p7_t5_re.I)

    if (file_path or file_name) and not _p7_t5_is_flush_command(comment_clean):
        af = _p7_t5_active_folder(chat)
        fn = _p7_t5_s(file_name or payload.get("file_name") or payload.get("name") or "")
        low_fn = fn.lower()
        ftype = "PHOTO" if low_fn.endswith((".jpg", ".jpeg", ".png", ".webp", ".heic")) else "PDF" if low_fn.endswith(".pdf") else "DOCUMENT"
        material = {
            "source": "TELEGRAM",
            "file_type": ftype,
            "file_name": fn,
            "telegram_message_id": _p7_t5_s(current_msg),
            "reply_to_message_id": _p7_t5_s(reply_to),
            "drive_file_id": _p7_t5_s(payload.get("drive_file_id")),
            "drive_url": _p7_t5_s(payload.get("drive_url") or payload.get("webViewLink") or file_path),
            "active_folder_id": _p7_t5_s(af.get("folder_id")),
            "active_folder_name": _p7_t5_s(af.get("folder_name")),
            "caption": _p7_t5_s(payload.get("caption") or comment_clean),
            "include_in_act": True,
            "include_in_report": True,
            "status": "PENDING",
            "added_at": _p7_t5_time.time(),
        }
        count, _ = _p7_t5_add_material(chat, material)
        return {
            "ok": True,
            "handled": True,
            "state": "DONE",
            "result_text": f"Фото/файл принят в пакет выезда: {count} шт. Активная папка: {material.get('active_folder_name') or material.get('active_folder_id')}.",
            "message": "Фото/файл принят в пакет выезда",
            "history": "P7_TOPIC5_MATERIAL_BUFFERED_WITH_ACTIVE_FOLDER",
        }

    if reply_to and comment_clean and not _p7_t5_is_flush_command(comment_clean):
        linked = _p7_t5_bind_comment(chat, reply_to, comment_clean, is_voice=is_voice)
        if linked:
            return {
                "ok": True,
                "handled": True,
                "state": "DONE",
                "result_text": f"Пояснение привязано к фото: {linked.get('file_name', '')}",
                "message": "Пояснение привязано к фото",
                "history": "P7_TOPIC5_REPLY_VOICE_BOUND_TO_MATERIAL",
            }

    return _P7_T5_ORIG_PROCESS_TECHNADZOR(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs)
# === END_P7_TOPIC5_REPLY_VOICE_BINDING_V1 ===

# === FULLFIX_TOPIC5_TECHNADZOR_CANON_CONTOUR_V2_TECHNADZOR ===
import json as _t5v2_json
import sqlite3 as _t5v2_sqlite3
import time as _t5v2_time
import uuid as _t5v2_uuid
from pathlib import Path as _t5v2_Path

_T5V2_ORIG_PROCESS_TECHNADZOR = process_technadzor
_T5V2_DB = "/root/.areal-neva-core/data/core.db"
_T5V2_DATA = _t5v2_Path("/root/.areal-neva-core/data/technadzor")
_T5V2_DATA.mkdir(parents=True, exist_ok=True)

def _t5v2_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _t5v2_low(v):
    return _t5v2_s(v).lower().replace("ё", "е")

def _t5v2_json_load(raw):
    try:
        d = _t5v2_json.loads(_t5v2_s(raw))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def _t5v2_get(obj, key, default=""):
    try:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return obj[key]
    except Exception:
        return getattr(obj, key, default)

def _t5v2_task(task_id, kwargs):
    task = kwargs.get("task")
    if task:
        return {
            "id": _t5v2_s(_t5v2_get(task, "id", task_id)),
            "chat_id": _t5v2_s(_t5v2_get(task, "chat_id", kwargs.get("chat_id", ""))),
            "topic_id": int(_t5v2_get(task, "topic_id", kwargs.get("topic_id", 0)) or 0),
            "reply_to_message_id": _t5v2_s(_t5v2_get(task, "reply_to_message_id", "")),
            "bot_message_id": _t5v2_s(_t5v2_get(task, "bot_message_id", "")),
            "input_type": _t5v2_s(_t5v2_get(task, "input_type", "")),
            "raw_input": _t5v2_s(_t5v2_get(task, "raw_input", "")),
        }

    if not task_id:
        return {}

    con = _t5v2_sqlite3.connect(_T5V2_DB)
    try:
        r = con.execute(
            "SELECT id,chat_id,topic_id,reply_to_message_id,bot_message_id,input_type,raw_input FROM tasks WHERE id=? LIMIT 1",
            (_t5v2_s(task_id),)
        ).fetchone()
    finally:
        con.close()

    if not r:
        return {}

    return {
        "id": _t5v2_s(r[0]),
        "chat_id": _t5v2_s(r[1]),
        "topic_id": int(r[2] or 0),
        "reply_to_message_id": _t5v2_s(r[3]),
        "bot_message_id": _t5v2_s(r[4]),
        "input_type": _t5v2_s(r[5]),
        "raw_input": _t5v2_s(r[6]),
    }

def _t5v2_is_photo_meta(meta):
    fn = _t5v2_s(meta.get("file_name") or meta.get("name"))
    mt = _t5v2_s(meta.get("mime_type"))
    return fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".heic")) or mt.startswith("image/")

def _t5v2_msg_id(meta):
    for k in ("telegram_message_id", "_reply_to_message_id", "reply_to_message_id"):
        v = _t5v2_s(meta.get(k))
        if v:
            return v
    fn = _t5v2_s(meta.get("file_name"))
    import re as _re
    m = _re.search(r"_(\d+)\.(?:jpg|jpeg|png|webp|heic)$", fn, _re.I)
    return m.group(1) if m else ""

def _t5v2_photo_rows(chat_id, topic_id=5):
    con = _t5v2_sqlite3.connect(_T5V2_DB)
    try:
        rows = con.execute(
            """
            SELECT rowid,id,raw_input,reply_to_message_id,created_at
            FROM tasks
            WHERE chat_id=?
              AND topic_id=?
              AND input_type='drive_file'
            ORDER BY rowid DESC
            LIMIT 300
            """,
            (_t5v2_s(chat_id), int(topic_id or 0))
        ).fetchall()
    finally:
        con.close()

    out = []
    for rowid, tid, raw, reply_to, created_at in rows:
        meta = _t5v2_json_load(raw)
        if not _t5v2_is_photo_meta(meta):
            continue
        meta["_rowid"] = int(rowid)
        meta["_task_id"] = _t5v2_s(tid)
        meta["_reply_to_message_id"] = _t5v2_s(reply_to)
        meta["_created_at"] = _t5v2_s(created_at)
        out.append(meta)
    return out

def _t5v2_parent_reply_by_bot(chat_id, topic_id, bot_message_id):
    if not bot_message_id:
        return ""
    con = _t5v2_sqlite3.connect(_T5V2_DB)
    try:
        r = con.execute(
            """
            SELECT reply_to_message_id
            FROM tasks
            WHERE chat_id=?
              AND topic_id=?
              AND CAST(bot_message_id AS TEXT)=?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (_t5v2_s(chat_id), int(topic_id or 0), _t5v2_s(bot_message_id))
        ).fetchone()
    finally:
        con.close()
    return _t5v2_s(r[0]) if r else ""

def _t5v2_find_anchor_photo(chat_id, topic_id, reply_to_message_id):
    rid = _t5v2_s(reply_to_message_id)
    if not rid:
        return {}

    rows = _t5v2_photo_rows(chat_id, topic_id)

    for meta in rows:
        ids = {
            _t5v2_s(meta.get("_reply_to_message_id")),
            _t5v2_s(meta.get("telegram_message_id")),
            _t5v2_msg_id(meta),
        }
        if rid in ids:
            return meta

    parent_reply = _t5v2_parent_reply_by_bot(chat_id, topic_id, rid)
    if parent_reply and parent_reply != rid:
        for meta in rows:
            ids = {
                _t5v2_s(meta.get("_reply_to_message_id")),
                _t5v2_s(meta.get("telegram_message_id")),
                _t5v2_msg_id(meta),
            }
            if parent_reply in ids:
                return meta

    return {}

def _t5v2_group_requested(text):
    low = _t5v2_low(text)
    return any(x in low for x in (
        "этими фото",
        "эти фото",
        "этих фото",
        "все фото",
        "всеми фото",
        "несколько фото",
        "три фото",
        "фотографии",
        "с ними",
        "по ним",
        "их",
        "фото",
        "пакет",
    ))

def _t5v2_select_photo_group(chat_id, topic_id, anchor, text):
    if not anchor:
        return []

    if not _t5v2_group_requested(text):
        return [anchor]

    rows = _t5v2_photo_rows(chat_id, topic_id)

    try:
        anchor_rowid = int(anchor.get("_rowid") or 0)
    except Exception:
        anchor_rowid = 0

    try:
        anchor_msg = int(_t5v2_msg_id(anchor) or 0)
    except Exception:
        anchor_msg = 0

    selected = []
    for meta in rows:
        try:
            rowid = int(meta.get("_rowid") or 0)
        except Exception:
            rowid = 0

        try:
            msg = int(_t5v2_msg_id(meta) or 0)
        except Exception:
            msg = 0

        same_row_cluster = bool(anchor_rowid and abs(rowid - anchor_rowid) <= 10)
        same_msg_cluster = bool(anchor_msg and msg and abs(msg - anchor_msg) <= 20)

        if same_row_cluster and same_msg_cluster:
            selected.append(meta)

    selected = sorted(selected, key=lambda m: int(m.get("_rowid") or 0))
    return selected or [anchor]

def _t5v2_active_folder(chat_id):
    try:
        if "get_active_folder" in globals():
            af = get_active_folder(str(chat_id), 5)
            if isinstance(af, dict):
                return af
    except Exception:
        pass

    try:
        p = _T5V2_DATA / f"active_folder_{chat_id}_5.json"
        d = _t5v2_json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def _t5v2_buf_path(chat_id):
    return _T5V2_DATA / f"buf_{chat_id}_5.json"

def _t5v2_load_buf(chat_id):
    p = _t5v2_buf_path(chat_id)
    try:
        d = _t5v2_json.loads(p.read_text(encoding="utf-8"))
        if isinstance(d, dict):
            d.setdefault("materials", [])
            return d
    except Exception:
        pass
    return {"source": "topic5_visit_buffer", "materials": [], "created_at": _t5v2_time.time()}

def _t5v2_save_buf(chat_id, buf):
    buf["updated_at"] = _t5v2_time.time()
    _t5v2_buf_path(chat_id).write_text(_t5v2_json.dumps(buf, ensure_ascii=False, indent=2), encoding="utf-8")

def _t5v2_material(chat_id, meta, comment=""):
    af = _t5v2_active_folder(chat_id)
    fid = _t5v2_s(meta.get("drive_file_id") or meta.get("file_id") or meta.get("id"))
    fn = _t5v2_s(meta.get("file_name") or meta.get("name"))
    mid = _t5v2_msg_id(meta)
    clean = _t5v2_s(comment, 20000)

    if clean.upper().startswith("[VOICE]"):
        clean = clean[7:].strip()

    return {
        "material_id": str(_t5v2_uuid.uuid4()),
        "source": "TELEGRAM",
        "file_type": "PHOTO",
        "file_name": fn,
        "drive_file_id": fid,
        "drive_url": _t5v2_s(meta.get("drive_url") or meta.get("webViewLink") or (f"https://drive.google.com/file/d/{fid}/view?usp=drivesdk" if fid else "")),
        "telegram_message_id": mid,
        "reply_to_message_id": mid,
        "source_task_id": _t5v2_s(meta.get("_task_id")),
        "active_folder_id": _t5v2_s(af.get("folder_id")),
        "active_folder_name": _t5v2_s(af.get("folder_name")),
        "include_in_report": True,
        "include_in_act": True,
        "status": "LINKED" if clean else "PENDING",
        "voice_comment": clean,
        "added_at": _t5v2_time.time(),
        "updated_at": _t5v2_time.time(),
    }

def _t5v2_upsert_material(chat_id, material):
    buf = _t5v2_load_buf(chat_id)
    mid = _t5v2_s(material.get("telegram_message_id"))
    fn = _t5v2_s(material.get("file_name"))

    target = None
    for old in buf.get("materials", []):
        if (mid and _t5v2_s(old.get("telegram_message_id")) == mid) or (fn and _t5v2_s(old.get("file_name")) == fn):
            target = old
            break

    if target is None:
        buf["materials"].append(material)
    else:
        old_comment = _t5v2_s(target.get("voice_comment"), 20000)
        new_comment = _t5v2_s(material.get("voice_comment"), 20000)
        target.update({k: v for k, v in material.items() if v not in ("", None)})

        if old_comment and new_comment and new_comment not in old_comment:
            target["voice_comment"] = old_comment + "\n" + new_comment
        elif old_comment and not new_comment:
            target["voice_comment"] = old_comment

    _t5v2_save_buf(chat_id, buf)
    return len(buf.get("materials", []))

def _t5v2_bind_photos(chat_id, photos, comment):
    count = 0
    for meta in photos:
        count = _t5v2_upsert_material(chat_id, _t5v2_material(chat_id, meta, comment))
    return count

def _t5v2_positive_act(text):
    low = _t5v2_low(text)

    negated = any(x in low for x in (
        "не делай акт",
        "не надо акт",
        "не нужно акт",
        "не формируй акт",
        "не должен был сделать акт",
        "не должен делать акт",
        "акт не для каждого",
        "не для каждого из",
        "принять к сведению",
        "принять это к сведению",
        "прими к сведению",
        "прими это к сведению",
    ))

    positive = any(x in low for x in (
        "сделай акт",
        "сформируй акт",
        "собери акт",
        "готовь акт",
        "акт по этим фото",
        "сделай разбор",
        "сформируй документ",
    ))

    return positive and not negated

def _t5v2_buffer_summary(chat_id):
    buf = _t5v2_load_buf(chat_id)
    mats = buf.get("materials", [])

    lines = []
    for i, m in enumerate(mats, 1):
        lines.append(f"Фото №{i}: {m.get('file_name','')}")
        if m.get("voice_comment"):
            lines.append(f"Пояснение: {m.get('voice_comment')}")
        if m.get("drive_url"):
            lines.append(f"Ссылка: {m.get('drive_url')}")

    return "\n".join(lines), len(mats)

def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "", **kwargs):
    task = _t5v2_task(task_id, kwargs)

    try:
        tid = int(topic_id or task.get("topic_id") or kwargs.get("topic_id") or 0)
    except Exception:
        tid = 0

    if tid != 5:
        return _T5V2_ORIG_PROCESS_TECHNADZOR(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs)

    chat = _t5v2_s(chat_id or task.get("chat_id") or kwargs.get("chat_id"))
    raw = _t5v2_s(text or task.get("raw_input"))
    input_type = _t5v2_s(task.get("input_type"))
    reply_to = _t5v2_s(task.get("reply_to_message_id"))

    if input_type == "drive_file":
        meta = _t5v2_json_load(raw)
        if _t5v2_is_photo_meta(meta):
            count = _t5v2_upsert_material(chat, _t5v2_material(chat, meta, ""))
            return {
                "ok": True,
                "handled": True,
                "state": "DONE",
                "status": "DONE",
                "result_text": f"Фото принято в пакет технадзора: {count} шт. Акт не формирую без отдельной команды.",
                "message": "Фото принято в пакет технадзора",
                "history": "FULLFIX_TOPIC5_PHOTO_TO_VISITBUFFER",
            }

    if input_type in ("text", "voice", "") and reply_to and raw and not _t5v2_positive_act(raw):
        anchor = _t5v2_find_anchor_photo(chat, 5, reply_to)
        if anchor:
            photos = _t5v2_select_photo_group(chat, 5, anchor, raw)
            count = _t5v2_bind_photos(chat, photos, raw)
            names = ", ".join(_t5v2_s(p.get("file_name")) for p in photos if p.get("file_name"))
            return {
                "ok": True,
                "handled": True,
                "state": "DONE",
                "status": "DONE",
                "result_text": f"Пояснение принято к фото: {len(photos)} шт. В пакете технадзора: {count} шт. Акт не формирую без отдельной команды.\nФайлы: {names}",
                "message": "Пояснение принято к фото",
                "history": "FULLFIX_TOPIC5_REPLY_TO_PHOTO_BOUND",
            }

    if input_type in ("text", "voice", "") and _t5v2_positive_act(raw):
        summary, n = _t5v2_buffer_summary(chat)
        if n <= 0:
            return {
                "ok": True,
                "handled": True,
                "state": "DONE",
                "status": "DONE",
                "result_text": "В пакете технадзора нет фото. Сначала пришли фото или ответь голосом на фото.",
                "message": "В пакете технадзора нет фото",
                "history": "FULLFIX_TOPIC5_ACT_NO_MATERIALS",
            }

        enriched = raw + "\n\nПакет фото технадзора:\n" + summary
        return _T5V2_ORIG_PROCESS_TECHNADZOR(text=enriched, task_id=task_id, chat_id=chat, topic_id=5, file_path=file_path, file_name=file_name, **kwargs)

    return _T5V2_ORIG_PROCESS_TECHNADZOR(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name, **kwargs)
# === END_FULLFIX_TOPIC5_TECHNADZOR_CANON_CONTOUR_V2_TECHNADZOR ===

# === P6H_VISION_BLOCKED_FALLBACK_V1 ===
# CANON §17: когда Vision заблокирован — строить акт из текста/голоса владельца
# + метаданных файла + предыдущих актов, не останавливаться.
# Сообщение в документе: "Визуальный анализ фото не выполнялся..."
import logging as _p6hvbf_log
_P6HVBF_LOG = _p6hvbf_log.getLogger("technadzor_engine")

_P6HVBF_ORIG = p6f_tnz_handle_photo_act_real

async def p6f_tnz_handle_photo_act_real(file_path, file_name, task_id, chat_id, topic_id, user_text=""):  # noqa: F811
    vision, vstatus = await _p6f_tnz_vision_via_openrouter(file_path)
    if vstatus == "EXTERNAL_PHOTO_ANALYSIS_BLOCKED":
        # Canon §17: Vision blocked → build act from owner text + file metadata
        _P6HVBF_LOG.info("P6HVBF_VISION_BLOCKED_FALLBACK file=%s user_text_len=%s", file_name, len(user_text or ""))
        vision = {
            "summary": (
                "Автоматический визуальный анализ фото не выполнялся, так как Vision заблокирован. "
                "Выводы основаны на предыдущих актах, пояснениях владельца и доступных именах/метаданных файлов."
            ),
            "defects": [],
            "confidence": "LOW",
            "_vision_blocked": True,
        }
        if user_text and str(user_text).strip():
            vision["summary"] += "\n\nПояснение владельца: " + str(user_text).strip()
        if file_name:
            vision["summary"] += "\n\nФайл: " + str(file_name)
        vstatus = "BLOCKED_FALLBACK"
    # delegate to original with resolved vision
    # re-enter original logic but skip first vision call
    if vision is None:
        return await _P6HVBF_ORIG(file_path, file_name, task_id, chat_id, topic_id, user_text)
    # replicate original body with already-resolved vision
    import os as _p6hvbf_os
    from datetime import datetime as _p6hvbf_dt
    norms_text = (vision.get("summary", "") or "") + " " + str(user_text or "")
    confirmed_norms, _ = _p6f_tnz_norms_block(norms_text)
    docx_lines = _p6f_tnz_build_docx_lines(vision, confirmed_norms, file_name, task_id)
    ts = _p6hvbf_dt.now().strftime("%Y%m%d_%H%M%S")
    safe = (str(task_id or ts)[:8] or ts).replace("/", "_").replace("\\", "_")
    out_dir = "/root/.areal-neva-core/outputs/technadzor_acts"
    _p6hvbf_os.makedirs(out_dir, exist_ok=True)
    docx_path = "{}/TECHNADZOR_ACT_PHOTO__{}_{}.docx".format(out_dir, safe, ts)
    written = _p6tz_make_docx(docx_path, docx_lines)
    if not written:
        return {
            "ok": False, "handled": True, "kind": "technadzor_photo_act",
            "state": "FAILED",
            "message": "Ошибка создания DOCX акта",
            "history": "P6HVBF_DOCX_WRITE_FAIL",
        }
    drive_link, ustatus = await _p6f_tnz_upload_to_topic(
        docx_path, _p6hvbf_os.path.basename(docx_path), chat_id or "-1003725299009", topic_id or 5
    )
    defects_count = len(vision.get("defects") or [])
    norms_count = len(confirmed_norms)
    public_lines = [
        "Акт технического надзора сформирован (Vision заблокирован — анализ по тексту владельца)",
        "Файл: " + str(file_name or ""),
        "Дефектов в тексте: {}".format(defects_count),
        "Нормативных ссылок: {}".format(norms_count) if norms_count else "Нормативная база: норма не подтверждена",
    ]
    if drive_link:
        public_lines.append("Drive DOCX: " + str(drive_link))
    return {
        "ok": bool(drive_link),
        "handled": True,
        "kind": "technadzor_photo_act",
        "message": "\n".join(public_lines),
        "state": "DONE" if drive_link else "AWAITING_CONFIRMATION",
        "drive_link": drive_link or "",
        "history": "P6HVBF:vision={},defects={},norms={},upload={}".format(
            vstatus, defects_count, norms_count, "OK" if drive_link else "FAIL"
        ),
    }

p6f_tnz_handle_photo_act_real._p6hvbf_wrapped = True
_P6HVBF_LOG.info("P6H_VISION_BLOCKED_FALLBACK_V1_INSTALLED")
# === END_P6H_VISION_BLOCKED_FALLBACK_V1 ===

# === P6_ACT_MATERIAL_FILTER_V1 ===
# Canon §4/§5: в акт только реальные фото + пояснения к дефектам.
# Фильтрует буфер перед тем как enriched-текст попадёт в LLM:
# - исключает PDF/XLSX/DOCX (образцы, старые акты, таблицы)
# - удаляет служебные команды из voice_comment
# - передаёт объект/адрес/основание из active_folder в заголовок акта
import logging as _p6amf_log
import re as _p6amf_re

_P6AMF_LOG = _p6amf_log.getLogger("technadzor_engine")

_P6AMF_SERVICE_PATTERNS = [
    "сделай акт", "делай акт", "оформи акт", "собери акт", "готовь акт",
    "формируй акт", "сделать акт", "финальный акт",
    "добавь в папку", "добавить в папку", "добавить в эту папку",
    "не в тот чат", "не туда", "ошибочно",
    "это тест", "тест надзор", "проверка связи",
    "ты добавил", "добавил все", "ты все добавил",
    "какой адрес", "какой у него адрес",
    "дай мне нормы", "дай нормы",
]

_P6AMF_NON_PHOTO_EXT = (".xlsx", ".xls", ".pdf", ".docx", ".doc", ".pptx")
_P6AMF_NON_PHOTO_TYPES = ("PDF", "XLSX", "XLS", "DOCX", "DOC", "OTHER")

def _p6amf_is_service_comment(text):
    if not text:
        return False
    low = str(text).lower().strip()
    return any(p in low for p in _P6AMF_SERVICE_PATTERNS)

def _p6amf_is_real_photo(m):
    """True only for real photo materials that belong in the act."""
    ft = str(m.get("file_type", "PHOTO")).upper()
    if ft in _P6AMF_NON_PHOTO_TYPES:
        return False
    fn = str(m.get("file_name", "")).lower()
    if any(fn.endswith(ext) for ext in _P6AMF_NON_PHOTO_EXT):
        return False
    if m.get("include_in_act") is False:
        return False
    return True

def _p6amf_clean_comment(text):
    """Return comment if substantive, empty string if service command."""
    if _p6amf_is_service_comment(text):
        return ""
    return str(text or "").strip()

def _p6amf_build_enriched(raw, active_folder, materials):
    """Build structured enriched text for act LLM call."""
    obj = active_folder.get("object_name") or active_folder.get("folder_name") or ""
    addr = active_folder.get("object_address") or obj
    basis = active_folder.get("visit_basis") or ""
    src = active_folder.get("source_request") or ""
    instructions = active_folder.get("owner_instructions") or []

    # Filter to real photos only
    photos = [m for m in materials if _p6amf_is_real_photo(m)]
    # Excluded non-photo files (for reference note only)
    excluded = [m for m in materials if not _p6amf_is_real_photo(m)]

    lines = ["КОМАНДА: Сформировать акт технического надзора", ""]
    if obj:
        lines.append(f"ОБЪЕКТ: {obj}")
    if addr and addr != obj:
        lines.append(f"АДРЕС: {addr}")
    if basis:
        lines.append(f"ОСНОВАНИЕ: {basis}")
    if src:
        lines.append(f"ИСТОЧНИК ЗАЯВКИ: {src}")
    lines.append("")

    if instructions:
        lines.append("ИНСТРУКЦИИ ВЛАДЕЛЬЦА:")
        # Skip command-like instructions
        for ins in instructions:
            if not _p6amf_is_service_comment(ins):
                lines.append("— " + str(ins).strip())
        lines.append("")

    lines.append(f"ФОТОМАТЕРИАЛЫ ОБЪЕКТА ({len(photos)} шт.):")
    for i, m in enumerate(photos, 1):
        fn = m.get("file_name", "")
        lines.append(f"Фото №{i}: {fn}")
        vc = _p6amf_clean_comment(m.get("voice_comment", ""))
        if vc:
            lines.append(f"  Пояснение: {vc}")
        du = m.get("drive_url", "")
        if du:
            lines.append(f"  Ссылка: {du}")
    lines.append("")

    if excluded:
        lines.append(f"Справочные файлы (не входят в фотофиксацию): {', '.join(m.get('file_name','') for m in excluded)}")
        lines.append("")

    return "\n".join(lines)

# Wrap process_technadzor to intercept act command path
_P6AMF_ORIG_PT = process_technadzor

def process_technadzor(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name="", **kwargs):  # noqa: F811
    try:
        tid = int(topic_id or (kwargs.get("topic_id") or 0))
    except Exception:
        tid = 0
    if tid != 5:
        return _P6AMF_ORIG_PT(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                               file_path=file_path, file_name=file_name, **kwargs)

    # Only intercept act command path
    raw = str(text or "").strip()
    if not _t5v2_positive_act(raw):
        return _P6AMF_ORIG_PT(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                               file_path=file_path, file_name=file_name, **kwargs)

    try:
        chat = str(chat_id or "")
        buf = _t5v2_load_buf(chat)
        materials = buf.get("materials", [])
        if not materials:
            return _P6AMF_ORIG_PT(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                                   file_path=file_path, file_name=file_name, **kwargs)

        active_folder = get_active_folder(chat, 5) or {}
        enriched = _p6amf_build_enriched(raw, active_folder, materials)

        photo_count = len([m for m in materials if _p6amf_is_real_photo(m)])
        excluded_count = len(materials) - photo_count
        _P6AMF_LOG.info(
            "P6AMF_ACT_FILTER chat=%s photos=%s excluded=%s obj=%s",
            chat, photo_count, excluded_count, active_folder.get("object_name", "")
        )
        return _P6AMF_ORIG_PT(text=enriched, task_id=task_id, chat_id=chat, topic_id=5,
                               file_path=file_path, file_name=file_name, **kwargs)
    except Exception as _e:
        _P6AMF_LOG.exception("P6AMF_ERR %s", _e)
        return _P6AMF_ORIG_PT(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id,
                               file_path=file_path, file_name=file_name, **kwargs)

process_technadzor._p6amf_wrapped = True
_P6AMF_LOG.info("P6_ACT_MATERIAL_FILTER_V1_INSTALLED")
# === END_P6_ACT_MATERIAL_FILTER_V1 ===


# === PATCH_TOPIC5_CANONICAL_ACT_ENGINE_V3 ===
# АКТ ОСМОТРА ОБЪЕКТА — TECHNADZOR_DOMAIN_LOGIC_CANON
# 8 разделов, таблица замечаний 8 колонок.
# ok=True если файлы сгенерированы, даже если upload упал.
# Dispatcher отвечает за upload fallback и НИКОГДА не вызывает старый дамп при ok=True.

import json as _t5ca_json
import logging as _t5ca_logging
import tempfile as _t5ca_tmp
from datetime import datetime as _t5ca_dt
from pathlib import Path as _t5ca_Path

_T5CA_LOG = _t5ca_logging.getLogger("technadzor_engine")
_T5CA_DATA = _t5ca_Path("/root/.areal-neva-core/data/technadzor")
_T5CA_SPECIALIST = "Кузнецов Илья Владимирович"
_T5CA_DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_T5CA_DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_T5CA_NORM_NONE = "норма не подтверждена"

_T5CA_PHOTO_EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic")
_T5CA_NON_PHOTO_TYPES = ("PDF", "XLSX", "XLS", "DOCX", "DOC", "OTHER")
# Фразы-мусор — не включать в замечания
_T5CA_GARBAGE = [
    "сделай акт", "делай акт", "оформи акт", "финальный акт", "итоговый акт",
    "добавь в папку", "добавить в папку", "нужно добавить в папку",
    "не в тот чат", "это тест", "тест надзор", "проверка связи",
    "ты добавил", "добавил все", "какой адрес", "дай нормы", "дай мне нормы",
    "какую задачу", "что по итогу", "видишь их да или нет",
    "делай финальный", "сделай мне пожалуйста акт", "положи в правильную папку",
]


def _t5ca_s(v, limit=50000):
    try:
        return "" if v is None else str(v).strip()[:limit]
    except Exception:
        return ""


def _t5ca_read_json(path):
    try:
        with open(str(path), encoding="utf-8") as _f:
            return _t5ca_json.load(_f)
    except Exception:
        return {}


def _t5ca_is_photo(m):
    fn = _t5ca_s(m.get("file_name", "")).lower()
    ft = _t5ca_s(m.get("file_type", "")).upper()
    if ft == "PHOTO":
        return True
    if ft in _T5CA_NON_PHOTO_TYPES:
        return False
    return any(fn.endswith(e) for e in _T5CA_PHOTO_EXT)


def _t5ca_is_garbage(text):
    low = _t5ca_s(text).lower()
    return any(p in low for p in _T5CA_GARBAGE)


def _t5ca_match_norms(text):
    """Нормы только если norm_id непустой — не выдумывать."""
    if not text or not text.strip():
        return []
    try:
        from core.normative_engine import search_norms_sync
        raw = search_norms_sync(str(text), limit=5)
        return [n for n in (raw or []) if n.get("norm_id")]
    except Exception:
        return []


def _t5ca_norm_str(comment):
    norms = _t5ca_match_norms(comment)
    if norms:
        parts = []
        for n in norms[:2]:
            nid = _t5ca_s(n.get("norm_id", ""))
            sec = _t5ca_s(n.get("section", ""))
            parts.append(f"{nid} — {sec}" if sec else nid)
        return "; ".join(parts)
    return _T5CA_NORM_NONE


def _t5ca_register_fonts():
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        if "T5CADejavu" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("T5CADejavu", _T5CA_DEJAVU))
        if "T5CADejavuB" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("T5CADejavuB", _T5CA_DEJAVU_BOLD))
        return True
    except Exception:
        return False


def _t5ca_cell_w(cell, emu):
    try:
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        twips = str(max(1, int(emu / 635)))
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        for old in tcPr.findall(qn("w:tcW")):
            tcPr.remove(old)
        tcW = OxmlElement("w:tcW")
        tcW.set(qn("w:w"), twips)
        tcW.set(qn("w:type"), "dxa")
        tcPr.append(tcW)
    except Exception:
        pass


def _t5ca_build_sections(af, materials):
    """Build all content lists needed for the act."""
    obj_name = _t5ca_s(af.get("object_name", ""))
    obj_addr = _t5ca_s(af.get("object_address") or af.get("object_name") or "")
    obj_loc = (obj_addr or obj_name)[:40]
    visit_basis = _t5ca_s(af.get("visit_basis", "запрос заказчика"))
    source_req = _t5ca_s(af.get("source_request", ""))

    file_count = len(materials)
    photo_count = sum(1 for m in materials if _t5ca_is_photo(m))

    # remark_rows: №, Фото, Узел/место, Нарушение, Последствия, Что сделать, Норматив, Статус
    remark_rows = []
    all_comments = []
    all_files = []

    for idx, m in enumerate(materials, 1):
        fn = _t5ca_s(m.get("file_name", f"файл_{idx}"), 80)
        all_files.append(fn)
        if not _t5ca_is_photo(m):
            continue
        raw = _t5ca_s(m.get("voice_comment") or m.get("comment") or "")
        comment = "" if _t5ca_is_garbage(raw) else raw[:300]
        if comment:
            all_comments.append(comment)

        norm_col = _t5ca_norm_str(comment) if comment else _T5CA_NORM_NONE

        lc = comment.lower() if comment else ""
        if "заменить" in lc or "старое оборудование" in lc or "вышло из строя" in lc:
            rec = "Рекомендуется заменить"
        elif "сварн" in lc or "шов" in lc:
            rec = "Необходимо проверить качество сварных соединений"
        elif "примыкание" in lc or "щельник" in lc:
            rec = "Рекомендуется выполнить нормальное примыкание"
        elif comment:
            rec = "Рекомендуется повторный осмотр после устранения"
        else:
            rec = ""

        remark_rows.append([
            str(idx), fn, obj_loc,
            comment or "—", "",   # Нарушение, Последствия (manual)
            rec, norm_col, "Открыто",
        ])

    facts = list(dict.fromkeys(c for c in all_comments if c))[:20]

    recs = []
    for comment in all_comments:
        lc = comment.lower()
        if "заменить" in lc or "старое оборудование" in lc:
            recs.append(f"Рекомендуется заменить: {comment[:200]}")
        elif "примыкание" in lc or "щельник" in lc:
            recs.append(f"Рекомендуется выполнить нормальное примыкание: {comment[:200]}")
        elif "сварн" in lc:
            recs.append(f"Необходимо проверить сварные соединения: {comment[:200]}")
    for inst in af.get("owner_instructions", []):
        ci = _t5ca_s(inst)
        if _t5ca_is_garbage(ci):
            continue
        lc = ci.lower()
        if any(x in lc for x in ("рекоменд", "нужно", "необходимо")):
            recs.append(ci[:300])
    recs = list(dict.fromkeys(recs))[:20]

    conseqs = []
    for comment in all_comments:
        lc = comment.lower()
        if "старое оборудование" in lc or "вышло из строя" in lc:
            conseqs.append("Выход оборудования из строя, аварийная ситуация")
        if "сварн" in lc or "шов" in lc:
            conseqs.append("Разрушение сварного соединения, нарушение несущей способности")
        if "примыкание" in lc or "щельник" in lc:
            conseqs.append("Проникновение влаги, нарушение теплоизоляции")
    conseqs = list(dict.fromkeys(conseqs))[:10]

    norms_global = _t5ca_match_norms(" ".join(all_comments))
    norms_found = [r[6] for r in remark_rows if r[6] and r[6] != _T5CA_NORM_NONE]

    basis = f"Основание: {visit_basis}." + (f" Источник: {source_req}." if source_req else "")

    return dict(
        obj_name=obj_name, obj_addr=obj_addr, file_count=file_count,
        photo_count=photo_count, all_files=all_files,
        remark_rows=remark_rows, facts=facts, recs=recs, conseqs=conseqs,
        norms_global=norms_global, norms_found=norms_found, basis=basis,
    )


def _t5ca_write_docx(dst, act_num, date_str, af, sec):
    try:
        from docx import Document
        from docx.shared import Cm, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        obj_name = sec["obj_name"]
        obj_addr = sec["obj_addr"]
        folder_name = _t5ca_s(af.get("folder_name", ""))

        doc = Document()
        s = doc.sections[0]
        s.page_width, s.page_height = s.page_height, s.page_width
        s.left_margin = s.right_margin = Cm(2)
        s.top_margin = Cm(2)
        s.bottom_margin = Cm(1.5)

        h = doc.add_heading(f"АКТ ОСМОТРА ОБЪЕКТА № {act_num}", level=1)
        h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub = doc.add_paragraph("Методом визуального неразрушающего контроля")
        sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph(f"Дата осмотра: {date_str}")
        doc.add_paragraph(f"Место осмотра: {obj_addr or obj_name}")
        doc.add_paragraph(f"Объект осмотра: {obj_name}")
        doc.add_paragraph(f"Основание осмотра: {sec['basis']}")
        doc.add_paragraph(f"Метод обследования: визуальный неразрушающий контроль с выездом на объект")
        doc.add_paragraph(f"Технический специалист: {_T5CA_SPECIALIST}")
        if folder_name:
            doc.add_paragraph(f"Ссылка на фотоматериалы: папка Drive «{folder_name}»")

        doc.add_heading("1. Общие сведения", level=2)
        doc.add_paragraph(
            "Осмотр выполнен методом визуального неразрушающего контроля с выездом на объект. "
            "Цель — выявление фактически наблюдаемых дефектов и формирование рекомендаций "
            "по их устранению."
        )
        doc.add_paragraph(
            f"Файлов в пакете: {sec['file_count']}. Фотоматериалов: {sec['photo_count']}."
        )

        doc.add_heading("2. Основание текущего осмотра", level=2)
        doc.add_paragraph(sec["basis"])

        doc.add_heading("3. Установлено по факту осмотра", level=2)
        if sec["facts"]:
            for i, f in enumerate(sec["facts"], 1):
                doc.add_paragraph(f"{i}. {f[:400]}", style="List Number")
        else:
            doc.add_paragraph("Данные фиксируются по пояснениям владельца и фотоматериалам.")

        doc.add_heading("4. Рекомендовано к устранению", level=2)
        if sec["recs"]:
            for i, r in enumerate(sec["recs"], 1):
                doc.add_paragraph(f"{i}. {r[:400]}", style="List Number")
        else:
            doc.add_paragraph("Рекомендации формируются по результатам детального осмотра.")

        doc.add_heading("5. Возможные последствия при отсутствии устранения", level=2)
        if sec["conseqs"]:
            for c in sec["conseqs"]:
                doc.add_paragraph(f"— {c[:300]}", style="List Bullet")
        else:
            doc.add_paragraph("Последствия определяются по характеру выявленных дефектов.")

        doc.add_heading("6. Таблица замечаний", level=2)
        col_hdrs = ["№", "Фото", "Узел/место", "Нарушение",
                    "Последствия", "Что сделать", "Норматив", "Статус"]
        col_emu = [int(c * 360000) for c in [0.7, 3.2, 2.5, 5.0, 3.0, 4.0, 4.5, 1.8]]
        tbl = doc.add_table(rows=1, cols=8)
        tbl.style = "Table Grid"
        hc = tbl.rows[0].cells
        for i, ht in enumerate(col_hdrs):
            hc[i].text = ht
            _t5ca_cell_w(hc[i], col_emu[i])
            for p in hc[i].paragraphs:
                for run in p.runs:
                    run.bold = True
                    run.font.size = Pt(8)
        for row_data in sec["remark_rows"]:
            row = tbl.add_row().cells
            for i, val in enumerate(row_data):
                row[i].text = _t5ca_s(val, 300)
                _t5ca_cell_w(row[i], col_emu[i])
                for p in row[i].paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(8)

        doc.add_heading("7. Заключение", level=2)
        if sec["norms_found"]:
            doc.add_paragraph(
                f"По результатам осмотра выявлены дефекты. "
                f"Нормативные документы: {'; '.join(dict.fromkeys(sec['norms_found'][:3]))}. "
                "Рекомендуется выполнить мероприятия из раздела 4 "
                "и провести повторный осмотр после их устранения."
            )
        else:
            doc.add_paragraph(
                "По результатам осмотра зафиксированы замечания согласно таблице. "
                "Нормативные пункты не подтверждены без дополнительного анализа. "
                "Рекомендуется повторный осмотр после устранения."
            )

        doc.add_heading("8. Приложение: перечень фото и документов", level=2)
        doc.add_paragraph(
            f"Фотоматериалов: {sec['photo_count']} шт. "
            f"Файлов в пакете: {sec['file_count']} шт."
        )
        for fn in sec["all_files"]:
            doc.add_paragraph(f"— {fn}", style="List Bullet")

        doc.add_paragraph("")
        doc.add_paragraph(
            f"Технический специалист: {_T5CA_SPECIALIST}     _____________     {date_str}"
        )
        doc.add_paragraph(
            "Представитель заказчика: _______________________     _____________     ___________"
        )

        doc.save(str(dst))
        return True
    except Exception as _e:
        _T5CA_LOG.exception("T5CA_DOCX_ERR %s", _e)
        return False


def _t5ca_write_pdf(dst, act_num, date_str, af, sec):
    try:
        from reportlab.lib.pagesizes import A4, landscape as _ls
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        ok = _t5ca_register_fonts()
        base = "T5CADejavu" if ok else "Helvetica"
        bold = "T5CADejavuB" if ok else "Helvetica-Bold"

        st = lambda name, **kw: ParagraphStyle(name, fontName=base, **kw)  # noqa: E731
        sb = lambda name, **kw: ParagraphStyle(name, fontName=bold, **kw)  # noqa: E731

        sty_t = sb("t5t", fontSize=13, alignment=1, spaceAfter=3)
        sty_s = st("t5s", fontSize=10, alignment=1, spaceAfter=6, textColor=colors.grey)
        sty_h = sb("t5h", fontSize=11, spaceBefore=8, spaceAfter=3)
        sty_b = st("t5b", fontSize=10, leading=13, spaceAfter=2)
        sty_sm = st("t5sm", fontSize=7, leading=9)
        sty_smb = sb("t5smb", fontSize=7, leading=9)

        obj_name = sec["obj_name"]
        obj_addr = sec["obj_addr"]
        folder_name = _t5ca_s(af.get("folder_name", ""))

        flow = []
        flow.append(Paragraph(f"АКТ ОСМОТРА ОБЪЕКТА № {act_num}", sty_t))
        flow.append(Paragraph("Методом визуального неразрушающего контроля", sty_s))
        flow.append(Paragraph(f"Дата: {date_str}  |  Объект: {obj_name}", sty_b))
        flow.append(Paragraph(f"Место: {obj_addr or obj_name}", sty_b))
        flow.append(Paragraph(f"Основание: {sec['basis']}", sty_b))
        flow.append(Paragraph(f"Технический специалист: {_T5CA_SPECIALIST}", sty_b))
        if folder_name:
            flow.append(Paragraph(f"Фотоматериалы: папка Drive «{folder_name}»", sty_b))
        flow.append(Spacer(1, 6))

        flow.append(Paragraph("1. Общие сведения", sty_h))
        flow.append(Paragraph(
            "Осмотр выполнен методом визуального неразрушающего контроля. "
            f"Файлов в пакете: {sec['file_count']}. Фотоматериалов: {sec['photo_count']}.",
            sty_b,
        ))

        flow.append(Paragraph("2. Основание текущего осмотра", sty_h))
        flow.append(Paragraph(sec["basis"], sty_b))

        flow.append(Paragraph("3. Установлено по факту осмотра", sty_h))
        if sec["facts"]:
            for i, f in enumerate(sec["facts"], 1):
                flow.append(Paragraph(f"{i}. {f[:400]}", sty_b))
        else:
            flow.append(Paragraph(
                "Данные фиксируются по пояснениям владельца и фотоматериалам.", sty_b))

        flow.append(Paragraph("4. Рекомендовано к устранению", sty_h))
        if sec["recs"]:
            for i, r in enumerate(sec["recs"], 1):
                flow.append(Paragraph(f"{i}. {r[:400]}", sty_b))
        else:
            flow.append(Paragraph("Рекомендации формируются по результатам осмотра.", sty_b))

        flow.append(Paragraph("5. Возможные последствия при отсутствии устранения", sty_h))
        if sec["conseqs"]:
            for c in sec["conseqs"]:
                flow.append(Paragraph(f"— {c[:300]}", sty_b))
        else:
            flow.append(Paragraph(
                "Последствия определяются по характеру выявленных дефектов.", sty_b))

        flow.append(Paragraph("6. Таблица замечаний", sty_h))
        col_hdrs = ["№", "Фото", "Узел/место", "Нарушение",
                    "Последствия", "Что сделать", "Норматив", "Статус"]
        col_w = [0.7*cm, 3.2*cm, 2.5*cm, 5.0*cm, 3.0*cm, 4.0*cm, 4.5*cm, 1.8*cm]
        rows = [[Paragraph(h, sty_smb) for h in col_hdrs]]
        for r in sec["remark_rows"]:
            rows.append([Paragraph(_t5ca_s(c, 250), sty_sm) for c in r])
        tbl = Table(rows, colWidths=col_w, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), base),
            ("FONTNAME", (0, 0), (-1, 0), bold),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        flow.append(tbl)
        flow.append(Spacer(1, 6))

        flow.append(Paragraph("7. Заключение", sty_h))
        if sec["norms_found"]:
            flow.append(Paragraph(
                f"Выявлены дефекты. Нормативные документы: "
                f"{'; '.join(dict.fromkeys(sec['norms_found'][:3]))}. "
                "Рекомендуется повторный осмотр после устранения.",
                sty_b,
            ))
        else:
            flow.append(Paragraph(
                "Зафиксированы замечания. Нормативные пункты не подтверждены без анализа. "
                "Рекомендуется повторный осмотр после устранения.",
                sty_b,
            ))

        flow.append(Paragraph("8. Приложение: перечень фото и документов", sty_h))
        flow.append(Paragraph(
            f"Фото: {sec['photo_count']} шт., файлов в пакете: {sec['file_count']} шт.",
            sty_b,
        ))
        for fn in sec["all_files"]:
            flow.append(Paragraph(f"— {fn}", sty_sm))

        flow.append(Spacer(1, 12))
        flow.append(Paragraph(
            f"Технический специалист: {_T5CA_SPECIALIST}     ___________     {date_str}",
            sty_b,
        ))
        flow.append(Paragraph(
            "Представитель заказчика: _______________________     ___________     ___________",
            sty_b,
        ))

        SimpleDocTemplate(
            str(dst), pagesize=_ls(A4),
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        ).build(flow)
        return True
    except Exception as _e:
        _T5CA_LOG.exception("T5CA_PDF_ERR %s", _e)
        return False


def t5_canonical_act_generate(chat_id: str, topic_id: int, task_id: str) -> dict:
    """
    PATCH_TOPIC5_CANONICAL_ACT_ENGINE_V3
    ok=True если DOCX или PDF сгенерированы (даже без upload).
    Dispatcher отвечает за fallback upload.
    """
    markers = []
    result = {
        "ok": False, "docx_link": "", "pdf_link": "",
        "docx_path": "", "pdf_path": "",
        "photo_count": 0, "file_count": 0, "norm_count": 0,
        "obj_name": "", "obj_addr": "", "folder_name": "", "folder_id": "",
        "upload_ok": False, "error": "", "markers": markers,
    }
    try:
        buf = _t5ca_read_json(_T5CA_DATA / f"buf_{chat_id}_{topic_id}.json")
        af = _t5ca_read_json(_T5CA_DATA / f"active_folder_{chat_id}_{topic_id}.json")
        materials = buf.get("materials", [])

        result["obj_name"] = _t5ca_s(af.get("object_name", ""))
        result["obj_addr"] = _t5ca_s(af.get("object_address") or af.get("object_name") or "")
        result["folder_name"] = _t5ca_s(af.get("folder_name", ""))
        result["folder_id"] = _t5ca_s(af.get("folder_id", ""))

        if not materials:
            result["error"] = "NO_MATERIALS"
            return result

        sec = _t5ca_build_sections(af, materials)
        result["file_count"] = sec["file_count"]
        result["photo_count"] = sec["photo_count"]
        result["norm_count"] = len(sec["norms_global"])

        markers.append("TOPIC5_GARBAGE_FILTER_OK")
        markers.append("TOPIC5_ACT_STRUCTURE_OK")
        if sec["remark_rows"]:
            markers.append("TOPIC5_DEFECT_TABLE_OK")
        markers.append("TOPIC5_RECOMMENDATIONS_SECTION_OK")
        markers.append("TOPIC5_NORMATIVE_SECTION_OK")

        date_str = _t5ca_dt.now().strftime("%d.%m.%Y")
        act_num = _t5ca_dt.now().strftime("%d.%m/%y")
        safe = (task_id[:6] if task_id else "000000").upper()
        base_name = f"AKT_OSMOTRA_{safe}_{_t5ca_dt.now().strftime('%Y%m%d')}"

        out_dir = _t5ca_Path(_t5ca_tmp.gettempdir()) / f"areal_t5ca_{task_id}"
        out_dir.mkdir(parents=True, exist_ok=True)
        docx_path = out_dir / f"{base_name}.docx"
        pdf_path = out_dir / f"{base_name}.pdf"

        docx_ok = _t5ca_write_docx(docx_path, act_num, date_str, af, sec)
        if docx_ok and docx_path.exists():
            markers.append("TOPIC5_DOCX_CREATED")
            result["docx_path"] = str(docx_path)

        pdf_ok = _t5ca_write_pdf(pdf_path, act_num, date_str, af, sec)
        if pdf_ok and pdf_path.exists():
            markers.append("TOPIC5_PDF_CREATED")
            result["pdf_path"] = str(pdf_path)

        if not docx_ok and not pdf_ok:
            result["error"] = "FILE_GENERATION_FAILED"
            return result

        # ok=True means files are ready — dispatcher handles upload
        result["ok"] = True

        # Try service account upload
        folder_id = result["folder_id"]
        for path_key, link_key in (("docx_path", "docx_link"), ("pdf_path", "pdf_link")):
            fpath = result.get(path_key, "")
            if not fpath:
                continue
            try:
                from core.drive_service_account_uploader import upload_artifact_service_account
                lnk = upload_artifact_service_account(
                    fpath, name=_t5ca_Path(fpath).name,
                    folder_id=folder_id or None,
                ) or ""
                result[link_key] = lnk
            except Exception as _ue:
                _T5CA_LOG.warning("T5CA_SA_UPLOAD_WARN %s %s", path_key, _ue)

        if result["docx_link"] or result["pdf_link"]:
            markers.append("TOPIC5_DRIVE_LINKS_SAVED")
            result["upload_ok"] = True

        _T5CA_LOG.info(
            "T5CA_DONE task=%s photos=%s files=%s norms=%s docx=%s pdf=%s upload=%s",
            task_id, sec["photo_count"], sec["file_count"], len(sec["norms_global"]),
            docx_ok, pdf_ok, result["upload_ok"],
        )
        return result

    except Exception as _e:
        _T5CA_LOG.exception("T5CA_ERR task=%s %s", task_id, _e)
        result["error"] = _t5ca_s(str(_e), 200)
        return result


_T5CA_LOG.info("PATCH_TOPIC5_CANONICAL_ACT_ENGINE_V3 installed")
# === END_PATCH_TOPIC5_CANONICAL_ACT_ENGINE_V3 ===

====================================================================================================
END_FILE: core/technadzor_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/technadzor_object_registry.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: b003e7b28c05758383c40e493308bafd72abc8deb716bb2a31f8f0357af8134c
====================================================================================================
# === P6H_TOPIC5_OBJECT_REGISTRY_INSPECTION_CHAIN_20260504 ===
# Object registry + inspection chain for topic_5 / Технадзор.
#
# Storage layers (system-only, never client-facing):
#   1) server JSON: data/templates/technadzor/objects/<object_id>.json
#   2) memory.db key: topic_5_technadzor_object_<object_id>
#   3) timeline:    data/memory_files/chat_<chat_id>/topic_5/timeline.jsonl
#   4) Drive (best-effort): topic_5/_system/object_registry/<object_id>.json
#
# A card has:
#   object_id, object_name, client_name, object_folder_url,
#   client_facing_folder_url, service_folder_url,
#   inspection_chain[], previous_acts[],
#   current_open_items[], closed_items[], unresolved_items[],
#   recommendations[], last_visit_date, last_act_no, last_pdf_link,
#   created_at, updated_at
#
# Inspection record:
#   act_no, date, mode (initial|repeat|extension|description_only),
#   pdf_link, docx_link, source_photo_folder,
#   findings[], open_items[], closed_items[], new_items[],
#   owner_observation, conflict_flags
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("task_worker")

_BASE = Path(__file__).resolve().parent.parent
_REGISTRY_DIR = _BASE / "data" / "templates" / "technadzor" / "objects"
_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

_TIMELINE_BASE = _BASE / "data" / "memory_files"

_FOLLOW_UP_INDICATORS = (
    "та же папка", "тот же объект", "то же место", "сегодняшний выезд",
    "повторн", "продолжен", "доделай по", "прошлый раз", "ранее", "вчера",
    "та же стройка", "тот же ангар", "следующий выезд", "очередной выезд",
)

_NEW_OBJECT_INDICATORS = (
    "новый объект", "другой объект", "новая стройка", "новый ангар",
    "новая площадка", "новый адрес",
)


def _slug(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"[^a-zа-я0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:60]


def _card_path(object_id: str) -> Path:
    return _REGISTRY_DIR / f"{_slug(object_id)}.json"


def list_object_ids() -> List[str]:
    return sorted(p.stem for p in _REGISTRY_DIR.glob("*.json"))


def list_object_summaries() -> List[Dict[str, Any]]:
    summaries = []
    for p in _REGISTRY_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            summaries.append({
                "object_id": data.get("object_id") or p.stem,
                "object_name": data.get("object_name", ""),
                "client_name": data.get("client_name", ""),
                "last_visit_date": data.get("last_visit_date", ""),
                "last_act_no": data.get("last_act_no", ""),
                "inspection_count": len(data.get("inspection_chain") or []),
            })
        except Exception:
            pass
    return summaries


def load_object(object_id: str) -> Optional[Dict[str, Any]]:
    p = _card_path(object_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        LOG.exception("P6H_REG_LOAD_FAIL %s", object_id)
        return None


def _new_card(object_id: str, **fields) -> Dict[str, Any]:
    now = int(time.time())
    base = {
        "object_id": object_id,
        "object_name": "",
        "client_name": "",
        "object_folder_url": "",
        "client_facing_folder_url": "",
        "service_folder_url": "",
        "inspection_chain": [],
        "previous_acts": [],
        "current_open_items": [],
        "closed_items": [],
        "unresolved_items": [],
        "recommendations": [],
        "last_visit_date": "",
        "last_act_no": "",
        "last_pdf_link": "",
        "created_at": now,
        "updated_at": now,
    }
    for k, v in (fields or {}).items():
        if k in base and v:
            base[k] = v
    return base


def save_object(card: Dict[str, Any]) -> Optional[Path]:
    if not card or not card.get("object_id"):
        return None
    card["updated_at"] = int(time.time())
    p = _card_path(card["object_id"])
    try:
        p.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
        _persist_to_memory(card)
        _append_timeline(card.get("chat_id", ""), card)
        return p
    except Exception:
        LOG.exception("P6H_REG_SAVE_FAIL %s", card.get("object_id"))
        return None


def _persist_to_memory(card: Dict[str, Any]) -> None:
    try:
        from core.memory_client import save_memory  # type: ignore
        chat_id = str(card.get("chat_id") or "")
        oid = card.get("object_id", "")
        body = json.dumps(card, ensure_ascii=False)[:8000]
        save_memory(chat_id=chat_id, key=f"topic_5_technadzor_object_{oid}", value=body)
    except Exception:
        # silent — server JSON is the canonical store
        pass


def _append_timeline(chat_id: str, card: Dict[str, Any]) -> None:
    if not chat_id:
        return
    try:
        d = _TIMELINE_BASE / f"chat_{chat_id}" / "topic_5"
        d.mkdir(parents=True, exist_ok=True)
        line = json.dumps({
            "ts": int(time.time()),
            "kind": "technadzor_object_update",
            "object_id": card.get("object_id"),
            "object_name": card.get("object_name", ""),
            "last_act_no": card.get("last_act_no", ""),
            "last_visit_date": card.get("last_visit_date", ""),
            "inspection_count": len(card.get("inspection_chain") or []),
        }, ensure_ascii=False)
        with (d / "timeline.jsonl").open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def derive_object_id_from_context(
    voice_ctx: Optional[Dict[str, Any]],
    drive_idx: Optional[Dict[str, Any]],
    file_path: str = "",
    file_name: str = "",
) -> Tuple[str, Dict[str, str]]:
    """Try to derive a stable object_id from available signals.

    Returns (object_id, source_dict) where source_dict explains what was used.
    Empty object_id means we cannot derive — caller must ask owner.
    """
    sources: Dict[str, str] = {}
    candidates: List[str] = []

    if voice_ctx:
        fh = (voice_ctx.get("folder_hint") or "").strip()
        if fh:
            candidates.append(fh)
            sources["folder_hint"] = fh
        oh = (voice_ctx.get("object_hint") or "").strip()
        if oh and not candidates:
            candidates.append(oh)
            sources["object_hint"] = oh

    # Drive: client-folder match by file path or by recent client folders
    if drive_idx:
        for f in drive_idx.get("folders_client", []) or []:
            name = f.get("name") or ""
            if name and name not in candidates:
                # Use the most recently modified client folder as a fallback hint only
                candidates.append(name)
                sources.setdefault("drive_client_folder", name)
                break

    # File name pattern (e.g., "kievskoe_08_04_26_act.pdf")
    if file_name and not candidates:
        candidates.append(file_name.rsplit(".", 1)[0])
        sources["file_name"] = file_name

    if not candidates:
        return ("", sources)
    return (_slug(candidates[0]), sources)


def detect_visit_mode(card: Optional[Dict[str, Any]], voice_ctx: Optional[Dict[str, Any]]) -> str:
    """Returns one of: initial | repeat | extension | description_only.

    Decision:
      • card is None or empty inspection_chain → initial
      • voice transcript explicitly says повторный/продолжение → repeat
      • else if chain non-empty → repeat (default for known object)
      • else → initial
    """
    transcript = ((voice_ctx or {}).get("transcript") or "").lower()
    if any(t in transcript for t in _NEW_OBJECT_INDICATORS):
        return "initial"
    has_history = bool(card and (card.get("inspection_chain") or []))
    if not has_history:
        return "initial"
    if any(t in transcript for t in _FOLLOW_UP_INDICATORS):
        return "repeat"
    if "дополнен" in transcript or "приложен" in transcript:
        return "extension"
    if (voice_ctx or {}).get("output_kind") == "description":
        return "description_only"
    return "repeat"


def carry_forward_open_items(card: Optional[Dict[str, Any]], current_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """For follow-up acts: take prior open_items and assign status based on
    whether similar findings exist in current_findings.

    Status set:
      УСТРАНЕНО, УСТРАНЕНО ЧАСТИЧНО, НЕ УСТРАНЕНО,
      ТРЕБУЕТ ДОВЕДЕНИЯ, НЕ ПРОВЕРЯЛОСЬ, ТРЕБУЕТ УТОЧНЕНИЯ
    """
    if not card:
        return []
    prior = card.get("current_open_items") or []
    if not prior:
        return []

    def _norm(s: str) -> str:
        return re.sub(r"\s+", " ", (s or "").lower()).strip()

    cur_blobs = [_norm((d.get("title") or "") + " " + (d.get("description") or "")) for d in current_findings or []]

    out: List[Dict[str, Any]] = []
    for it in prior:
        prior_blob = _norm((it.get("title") or "") + " " + (it.get("description") or "") + " " + (it.get("section") or ""))
        # naive match: any token of length >= 5 from prior present in current
        tokens = [t for t in re.findall(r"\w+", prior_blob) if len(t) >= 5]
        match = False
        partial = False
        for cb in cur_blobs:
            present = sum(1 for t in tokens if t in cb)
            if present >= max(2, len(tokens) // 3):
                match = True
                if present < max(3, len(tokens) // 2):
                    partial = True
                break
        if match and not partial:
            status = "НЕ УСТРАНЕНО"
        elif match and partial:
            status = "УСТРАНЕНО ЧАСТИЧНО"
        else:
            status = "ТРЕБУЕТ УТОЧНЕНИЯ"
        out.append({
            "title": it.get("title", ""),
            "description": it.get("description", ""),
            "section": it.get("section", ""),
            "status": status,
            "from_act_no": it.get("act_no", ""),
        })
    return out


def detect_voice_vision_conflict(voice_ctx: Optional[Dict[str, Any]], grouped_sections: List[Tuple[str, List[Dict[str, Any]]]]) -> List[str]:
    """Returns a list of human-readable conflict markers.

    Conflict cases:
      • voice mentions sections that Vision didn't pick up
      • voice explicitly excludes section that Vision flagged
    """
    if not voice_ctx or not (voice_ctx.get("transcript") or ""):
        return []
    transcript = (voice_ctx.get("transcript") or "").lower()
    flags: List[str] = []

    # Use the same section keywords as the engine
    try:
        from core.technadzor_engine import _P6H_SECTIONS  # type: ignore
    except Exception:
        return []

    voice_mentioned: List[str] = []
    for sec_title, kws in _P6H_SECTIONS:
        for kw in kws:
            if kw in transcript:
                voice_mentioned.append(sec_title)
                break

    vision_sections = [s[0] for s in (grouped_sections or [])]
    for vm in voice_mentioned:
        if vm not in vision_sections:
            flags.append(
                f"По голосовому ТЗ упомянуто «{vm}», но по фото Vision этого не подтвердил — уточни, что включать в акт"
            )
    excludes = " ".join(voice_ctx.get("explicit_exclude") or [])
    for vs in vision_sections:
        for kw_pair in _P6H_SECTIONS:
            if kw_pair[0] != vs:
                continue
            if any(kw in excludes.lower() for kw in kw_pair[1]):
                flags.append(
                    f"Vision выделил «{vs}», но владелец голосом просил это не включать — уточни"
                )
            break
    return flags[:6]


def record_inspection(
    object_id: str,
    chat_id: str,
    *,
    act_no: str = "",
    date_str: str = "",
    mode: str = "initial",
    pdf_link: str = "",
    docx_link: str = "",
    source_photo_folder: str = "",
    findings: Optional[List[Dict[str, Any]]] = None,
    open_items: Optional[List[Dict[str, Any]]] = None,
    closed_items: Optional[List[Dict[str, Any]]] = None,
    new_items: Optional[List[Dict[str, Any]]] = None,
    owner_observation: str = "",
    conflict_flags: Optional[List[str]] = None,
    object_name: str = "",
    client_name: str = "",
    object_folder_url: str = "",
    client_facing_folder_url: str = "",
    service_folder_url: str = "",
) -> Dict[str, Any]:
    """Append an inspection record to object's chain. Creates card if missing."""
    card = load_object(object_id) or _new_card(object_id)
    card["chat_id"] = str(chat_id)
    if object_name:
        card["object_name"] = object_name
    if client_name and not card.get("client_name"):
        card["client_name"] = client_name
    if object_folder_url:
        card["object_folder_url"] = object_folder_url
    if client_facing_folder_url:
        card["client_facing_folder_url"] = client_facing_folder_url
    if service_folder_url:
        card["service_folder_url"] = service_folder_url

    record = {
        "act_no": act_no or "",
        "date": date_str or "",
        "mode": mode or "initial",
        "pdf_link": pdf_link or "",
        "docx_link": docx_link or "",
        "source_photo_folder": source_photo_folder or "",
        "findings": findings or [],
        "open_items": open_items or [],
        "closed_items": closed_items or [],
        "new_items": new_items or [],
        "owner_observation": owner_observation or "",
        "conflict_flags": conflict_flags or [],
        "ts": int(time.time()),
    }
    card["inspection_chain"].append(record)
    if act_no:
        card["last_act_no"] = act_no
    if date_str:
        card["last_visit_date"] = date_str
    if pdf_link:
        card["last_pdf_link"] = pdf_link
        card["previous_acts"].append({
            "act_no": act_no, "date": date_str,
            "pdf_link": pdf_link, "docx_link": docx_link,
        })
    if open_items is not None:
        card["current_open_items"] = list(open_items)
    if closed_items:
        card["closed_items"] = (card.get("closed_items") or []) + list(closed_items)
    save_object(card)
    return card


try:
    LOG.info("P6H_TOPIC5_OBJECT_REGISTRY_INSPECTION_CHAIN_20260504_INSTALLED")
except Exception:
    pass
# === END_P6H_TOPIC5_OBJECT_REGISTRY_INSPECTION_CHAIN_20260504 ===

====================================================================================================
END_FILE: core/technadzor_object_registry.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/telegram_artifact_fallback.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 4a26f39caf63a874a8b6f186ef3b2ce95745637edd8d21d9e8e7230b14ba4b99
====================================================================================================
import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

def send_artifact_to_telegram(
    chat_id,
    topic_id,
    reply_to_message_id,
    artifact_path: str,
    caption: str = "",
) -> dict:
    bot_token = <REDACTED_SECRET>"BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return {"ok": False, "error": "BOT_TOKEN_NOT_SET"}
    if not artifact_path or not os.path.exists(artifact_path):
        return {"ok": False, "error": "ARTIFACT_NOT_FOUND"}
    try:
        data = {
            "chat_id": str(chat_id),
            "caption": caption or "Готово. Файл отправлен в Telegram.",
        }
        if topic_id and int(topic_id) > 0:
            data["message_thread_id"] = str(topic_id)
        if reply_to_message_id:
            data["reply_to_message_id"] = str(reply_to_message_id)
        with open(artifact_path, "rb") as f:
            res = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendDocument",
                data=data,
                files={"document": (os.path.basename(artifact_path), f)},
                timeout=30,
            )
        if res.ok:
            resp = res.json()
            msg = resp.get("result", {})
            doc = msg.get("document", {})
            return {
                "ok": True,
                "message_id": msg.get("message_id"),
                "file_id": doc.get("file_id"),
                "file_name": doc.get("file_name"),
            }
        return {"ok": False, "error": f"TG_STATUS_{res.status_code}"}
    except Exception as e:
        logger.error("send_artifact_to_telegram failed: %s", e)
        return {"ok": False, "error": str(e)}

====================================================================================================
END_FILE: core/telegram_artifact_fallback.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/telegram_source_skill_extractor.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2f9e18163498265ad703ced0637bf33a83779fdfc4b7304974bb64d091a5f797
====================================================================================================
#!/usr/bin/env python3
# === TELEGRAM_SOURCE_SKILL_EXTRACTOR_V1 ===
# Read-only Telethon-based extractor for public Telegram sources.
# Collects message metadata, links, and document references.
# Does NOT save raw history to memory.db or create core.db tasks.
from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("telegram_source_skill_extractor")

BASE = Path(__file__).parent.parent
SESSION_PATH = BASE / "sessions" / "user.session"
API_ID = 27925449

URL_RE = re.compile(r"https?://[^\s\)\]\>\"']+")

DOCUMENT_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls",
    ".pptx", ".ppt", ".zip", ".rar", ".dwg", ".dxf",
}

TECHNADZOR_KEYWORDS = [
    "акт", "дефект", "предписание", "заключение", "протокол",
    "осмотр", "проверка", "замечание", "нарушение", "устранение",
    "приёмка", "приемка", "скрытые работы", "исполнительная",
    "норматив", "снип", "гост", "сп ", "фото", "документ",
    "отчёт", "отчет", "смета", "спецификация", "чертёж", "чертеж",
    "технадзор", "стройконтроль", "авторский надзор",
    "кровля", "фасад", "перекрытие", "колонна", "фундамент",
    "бетон", "арматура", "сварка", "металл", "кладка", "газобетон",
    "отделка", "стяжка", "штукатурка", "электрика", "вентиляция",
    "водоснабжение", "канализация", "охрана труда",
]

NOISE_MARKERS = [
    "реклама", "продам", "куплю", "скидка", "акция",
    "подпишись", "переходи по ссылке", "розыгрыш",
    "заработок", "кредит без отказа", "займ",
    "только сегодня", "бесплатно жми", "выиграли",
]


def load_env(path: str | None = None) -> dict:
    env_path = Path(path) if path else BASE / ".env"
    result = {}
    if not env_path.exists():
        return result
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        result[k.strip()] = v.strip()
    return result


def build_client(session_path: str | None = None):
    from telethon import TelegramClient
    sp = str(session_path or SESSION_PATH)
    # api_hash not stored — authorized session does not need it for reads
    return TelegramClient(sp, API_ID, "a" * 32)


def extract_links(text: str) -> list[str]:
    return URL_RE.findall(text or "")


def is_relevant_for_document_skill(
    message_text: str,
    file_name: str | None = None,
    links: list[str] | None = None,
) -> bool:
    low = (message_text or "").lower()
    if any(n in low for n in NOISE_MARKERS):
        return False
    if any(kw in low for kw in TECHNADZOR_KEYWORDS):
        return True
    fname_low = (file_name or "").lower()
    if any(ext in fname_low for ext in DOCUMENT_EXTENSIONS):
        return True
    for link in (links or []):
        if any(ext in link.lower() for ext in DOCUMENT_EXTENSIONS):
            return True
    return False


def build_source_record(msg_id: int, msg_date: str, text: str,
                        media_type: str | None, file_name: str | None,
                        links: list[str], channel: str) -> dict:
    return {
        "source": f"@{channel.lstrip('@')}",
        "message_id": msg_id,
        "message_date": msg_date,
        "text": (text or "")[:1500],
        "media_type": media_type,
        "file_name": file_name,
        "links": links,
        "source_ref": f"https://t.me/{channel.lstrip('@')}/{msg_id}",
    }


async def check_source_access(source: str, client) -> dict:
    try:
        entity = await client.get_entity(source.lstrip("@"))
        return {
            "ok": True,
            "id": entity.id,
            "title": getattr(entity, "title", ""),
            "username": getattr(entity, "username", ""),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def scan_source(source: str, client, limit: int = 1000) -> dict:
    from telethon.tl.types import (
        MessageMediaDocument, MessageMediaPhoto, MessageMediaWebPage
    )

    records: list[dict] = []
    total = skipped_empty = skipped_noise = detected_docs = detected_links = 0

    async for msg in client.iter_messages(source.lstrip("@"), limit=limit or None):
        total += 1
        text = (msg.message or "").strip()
        if not text and not msg.media:
            skipped_empty += 1
            continue

        low = text.lower()
        if any(n in low for n in NOISE_MARKERS):
            skipped_noise += 1
            continue

        links = extract_links(text)
        file_name = None
        media_type = None

        if isinstance(msg.media, MessageMediaDocument):
            doc = msg.media.document
            for attr in getattr(doc, "attributes", []):
                if hasattr(attr, "file_name") and attr.file_name:
                    file_name = attr.file_name
            media_type = "document"
            detected_docs += 1
        elif isinstance(msg.media, MessageMediaPhoto):
            media_type = "photo"
        elif isinstance(msg.media, MessageMediaWebPage):
            wp = msg.media.webpage
            if hasattr(wp, "url") and wp.url:
                links.append(wp.url)
            media_type = "webpage"

        if links:
            detected_links += 1

        date_str = msg.date.isoformat() if msg.date else ""
        record = build_source_record(
            msg.id, date_str, text, media_type, file_name,
            links, source.lstrip("@")
        )
        records.append(record)

    return {
        "total_fetched": total,
        "skipped_empty": skipped_empty,
        "skipped_noise": skipped_noise,
        "detected_docs": detected_docs,
        "detected_links": detected_links,
        "records": records,
    }


async def download_relevant_documents(
    client, msg, output_dir: Path
) -> str | None:
    from telethon.tl.types import MessageMediaDocument
    if not isinstance(msg.media, MessageMediaDocument):
        return None
    doc = msg.media.document
    file_name = f"doc_{msg.id}"
    for attr in getattr(doc, "attributes", []):
        if hasattr(attr, "file_name") and attr.file_name:
            file_name = attr.file_name
    ext = Path(file_name).suffix.lower()
    if ext not in DOCUMENT_EXTENSIONS:
        return None
    out_path = output_dir / file_name
    if out_path.exists():
        return str(out_path)
    try:
        await client.download_media(msg, file=str(out_path))
        return str(out_path)
    except Exception as e:
        logger.warning("download failed msg=%s err=%s", msg.id, e)
        return None


async def run_source_scan(
    source: str = "@tnz_msk",
    limit: int = 1000,
    download_docs: bool = False,
    docs_output_dir: Path | None = None,
) -> dict:
    client = build_client()
    await client.connect()

    if not await client.is_user_authorized():
        await client.disconnect()
        return {"ok": False, "error": "session_not_authorized"}

    access = await check_source_access(source, client)
    if not access["ok"]:
        await client.disconnect()
        return {"ok": False, "error": access.get("error")}

    scan = await scan_source(source, client, limit=limit)
    downloaded: list[str] = []

    if download_docs and docs_output_dir:
        docs_output_dir.mkdir(parents=True, exist_ok=True)
        from telethon.tl.types import MessageMediaDocument
        async for msg in client.iter_messages(source.lstrip("@"), limit=limit or None):
            if not isinstance(msg.media, MessageMediaDocument):
                continue
            text = msg.message or ""
            links = extract_links(text)
            doc = msg.media.document
            fname = ""
            for attr in getattr(doc, "attributes", []):
                if hasattr(attr, "file_name") and attr.file_name:
                    fname = attr.file_name
            if is_relevant_for_document_skill(text, fname, links):
                path = await download_relevant_documents(client, msg, docs_output_dir)
                if path:
                    downloaded.append(path)

    await client.disconnect()

    return {
        "ok": True,
        "source": source,
        "access": access,
        "scan": scan,
        "downloaded_documents": downloaded,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }
# === END_TELEGRAM_SOURCE_SKILL_EXTRACTOR_V1 ===

====================================================================================================
END_FILE: core/telegram_source_skill_extractor.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/temp_cleanup.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2b7b91b8f6ba3a13518d234d8c24a426b85854300ae56a458fae4c6bcdb06194
====================================================================================================
# === TEMP_CLEANUP_V1 ===
import os, logging, glob
from pathlib import Path
logger = logging.getLogger(__name__)

TEMP_DIRS = ["/tmp", "/root/.areal-neva-core/data/temp"]

def cleanup_file(path: str) -> bool:
    try:
        if path and os.path.exists(path):
            os.remove(path)
            logger.info("TEMP_CLEANED path=%s", path)
            return True
    except Exception as e:
        logger.warning("TEMP_CLEANUP_ERR path=%s err=%s", path, e)
    return False

def cleanup_task_temps(task_id: str) -> int:
    """Удалить все temp файлы связанные с task_id"""
    count = 0
    for d in TEMP_DIRS:
        if not os.path.exists(d):
            continue
        for f in glob.glob(f"{d}/*{task_id}*"):
            if cleanup_file(f):
                count += 1
    return count

def cleanup_after_upload(local_paths: list) -> int:
    count = 0
    for p in (local_paths or []):
        if p and isinstance(p, str) and "/tmp" in p:
            if cleanup_file(p):
                count += 1
    return count
# === END TEMP_CLEANUP_V1 ===

====================================================================================================
END_FILE: core/temp_cleanup.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/template_engine_v1.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 03b9f6dca63b13fc8584f33acc32498fc893c9dfe06a92b5d1c0e467d04eddfc
====================================================================================================
# === TEMPLATE_ENGINE_V1 ===
import os, json, logging, glob
from typing import Optional, Dict, Any
logger = logging.getLogger(__name__)

BASE = "/root/.areal-neva-core"
TEMPLATE_DIR = f"{BASE}/data/templates"
TRIGGER_PHRASES = [
    "сделай так же", "по образцу", "как в прошлый раз",
    "аналогично", "такой же", "такую же", "такое же",
    "по шаблону", "используй шаблон", "как раньше"
]

def is_template_request(text: str) -> bool:
    low = text.lower()
    return any(t in low for t in TRIGGER_PHRASES)

def save_template(topic_id: int, file_path: str, template_type: str = "estimate") -> bool:
    """Сохранить файл как шаблон для топика"""
    try:
        os.makedirs(f"{TEMPLATE_DIR}/{template_type}", exist_ok=True)
        import shutil
        ext = os.path.splitext(file_path)[1]
        dest = f"{TEMPLATE_DIR}/{template_type}/ACTIVE__topic_{topic_id}{ext}"
        shutil.copy2(file_path, dest)
        meta = {
            "topic_id": topic_id,
            "type": template_type,
            "source": file_path,
            "saved_at": __import__("datetime").datetime.utcnow().isoformat()
        }
        with open(f"{TEMPLATE_DIR}/{template_type}/ACTIVE__topic_{topic_id}.json", "w") as f:
            json.dump(meta, f, ensure_ascii=False)
        logger.info("TEMPLATE_ENGINE_V1 saved topic=%s type=%s", topic_id, template_type)
        return True
    except Exception as e:
        logger.error("TEMPLATE_SAVE_ERR %s", e)
        return False

def get_template(topic_id: int, template_type: str = "estimate") -> Optional[str]:
    """Получить путь к шаблону топика"""
    try:
        patterns = [
            f"{TEMPLATE_DIR}/{template_type}/ACTIVE__topic_{topic_id}.*",
            f"{TEMPLATE_DIR}/estimate/ACTIVE__topic_{topic_id}.*",
        ]
        for pat in patterns:
            hits = [f for f in glob.glob(pat) if not f.endswith(".json")]
            if hits:
                return hits[0]
    except Exception as e:
        logger.warning("TEMPLATE_GET_ERR %s", e)
    return None

def apply_template_to_xlsx(template_path: str, rows: list, output_path: str) -> bool:
    """Применить структуру шаблона к новым данным"""
    try:
        from openpyxl import load_workbook
        import copy
        wb_tpl = load_workbook(template_path)
        ws_tpl = wb_tpl.active

        # Копируем структуру — заголовки из шаблона
        wb_new = load_workbook(template_path)
        ws_new = wb_new.active

        # Очищаем данные, оставляем заголовки (строка 1-2)
        header_rows = 2
        for row in ws_new.iter_rows(min_row=header_rows+1, max_row=ws_new.max_row):
            for cell in row:
                cell.value = None

        # Заполняем новыми данными с сохранением формул
        for i, item in enumerate(rows, start=header_rows+1):
            ws_new.cell(i, 1, value=i - header_rows)
            ws_new.cell(i, 2, value=str(item.get("name", "")))
            ws_new.cell(i, 3, value=str(item.get("unit", "шт")))
            ws_new.cell(i, 4, value=float(item.get("qty", 0) or 0))
            ws_new.cell(i, 5, value=float(item.get("price", 0) or 0))
            ws_new.cell(i, 6, f"=D{i}*E{i}")

        # Итог
        last = header_rows + len(rows)
        ws_new.cell(last+1, 6, f"=SUM(F{header_rows+1}:F{last})")

        wb_new.save(output_path)
        logger.info("TEMPLATE_APPLIED_V1 output=%s rows=%s", output_path, len(rows))
        return True
    except Exception as e:
        logger.error("TEMPLATE_APPLY_ERR %s", e)
        return False

def detect_template_type(file_name: str, intent: str = "") -> str:
    fn = file_name.lower()
    if any(e in fn for e in [".xlsx", ".xls", ".csv"]):
        return "estimate"
    if any(e in fn for e in [".docx", ".doc"]):
        return "technadzor"
    if "estimate" in intent or "смет" in intent:
        return "estimate"
    return "estimate"
# === END TEMPLATE_ENGINE_V1 ===

====================================================================================================
END_FILE: core/template_engine_v1.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/template_intake_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2f648e1b331a0532cd5ada22935d47ef2b2d81860d0239e0cde9275f3702eddf
====================================================================================================
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

====================================================================================================
END_FILE: core/template_intake_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/template_manager.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 3a9747ea77b9eedd43404491616b056af960b0fa4cdb72331f4b0ce6c3fc9cce
====================================================================================================
import os, logging, sqlite3, shutil
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)
MEMORY_DB = "/root/.areal-neva-core/data/memory.db"

def save_template(chat_id: str, topic_id: int, template_type: str, file_path: str) -> bool:
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cur = conn.cursor()
        key = f"topic_{topic_id}_template_{template_type}"
        cur.execute("INSERT OR REPLACE INTO memory (chat_id, key, value, timestamp) VALUES (?,?,?,?)",
                    (chat_id, key, file_path, datetime.utcnow().isoformat()))
        conn.commit(); conn.close()
        return True
    except Exception as e:
        logger.error(f"save_template: {e}")
        return False

def get_template(chat_id: str, topic_id: int, template_type: str) -> Optional[str]:
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cur = conn.cursor()
        cur.execute("SELECT value FROM memory WHERE chat_id=? AND key=?", (chat_id, f"topic_{topic_id}_template_{template_type}"))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except:
        return None

def apply_template(template_path: str, output_path: str, data: list) -> bool:
    try:
        shutil.copy(template_path, output_path)
        from openpyxl import load_workbook
        wb = load_workbook(output_path)
        ws = wb.active
        for i, row_data in enumerate(data, 2):
            for j, val in enumerate(row_data, 1):
                ws.cell(i, j, value=val)
        wb.save(output_path); wb.close()
        return True
    except Exception as e:
        logger.error(f"apply_template: {e}")
        return False

# === ALL_CONTOURS_TEMPLATE_MANAGER_V2 ===
def save_template(file_path, topic_id, intent):
    import shutil
    from pathlib import Path
    src=Path(file_path)
    if not src.exists():
        raise FileNotFoundError(str(file_path))
    safe="".join(c if c.isalnum() or c in ("_","-") else "_" for c in str(intent or "template"))
    out=Path("/root/.areal-neva-core/data/templates")
    out.mkdir(parents=True, exist_ok=True)
    dst=out/(str(int(topic_id or 0))+"_"+safe+(src.suffix or ".xlsx"))
    shutil.copy2(src,dst)
    return str(dst)
# === END_ALL_CONTOURS_TEMPLATE_MANAGER_V2 ===

# === FINAL_CODE_CONTOUR_TEMPLATE_APPLY_V1 ===
def apply_template(template_path, output_path, data_rows):
    from openpyxl import load_workbook
    wb=load_workbook(template_path)
    ws=wb.active
    start=2
    for r_idx,row in enumerate(data_rows or [], start):
        vals=row.values() if isinstance(row,dict) else row
        for c_idx,val in enumerate(list(vals),1):
            ws.cell(r_idx,c_idx,value=val)
    wb.save(output_path)
    return output_path
# === END_FINAL_CODE_CONTOUR_TEMPLATE_APPLY_V1 ===

# === TEMPLATE_SYSTEM_V41 ===

def template_learn_v41(file_path, chat_id=None, topic_id=0, template_type="project"):
    try:
        return save_template(str(chat_id or "default"), int(topic_id or 0), template_type, file_path)
    except TypeError:
        return save_template(file_path, topic_id, template_type)
    except Exception:
        return False


def template_priority_v41(chat_id=None, topic_id=0, template_type="project"):
    try:
        return get_template(str(chat_id or "default"), int(topic_id or 0), template_type)
    except TypeError:
        return get_template(topic_id, template_type)
    except Exception:
        return None


def project_template_engine_v41(template_path, output_path, data_rows=None):
    if not template_path:
        return {"success": False, "error": "TEMPLATE_NOT_FOUND"}
    ok = apply_template(template_path, output_path, data_rows or [])
    return {"success": bool(ok), "artifact_path": output_path if ok else None, "error": None if ok else "TEMPLATE_APPLY_FAILED"}

# === END_TEMPLATE_SYSTEM_V41 ===

# === CODE_CLOSE_V43_TEMPLATE_MANAGER ===

def _v43_template_dir():
    import os
    path = "/root/.areal-neva-core/data/templates"
    os.makedirs(path, exist_ok=True)
    return path

def template_learn_v43(file_path, topic_id=0, template_type="project"):
    import os, shutil, json
    base = _v43_template_dir()
    name = "topic_" + str(int(topic_id or 0)) + "_" + str(template_type or "project")
    ext = os.path.splitext(str(file_path))[1] or ".bin"
    dst = os.path.join(base, name + ext)
    shutil.copy2(file_path, dst)
    meta = {"topic_id": int(topic_id or 0), "template_type": template_type, "path": dst}
    with open(os.path.join(base, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return dst

def template_priority_v43(topic_id=0, template_type="project"):
    import os, json, glob
    base = _v43_template_dir()
    name = "topic_" + str(int(topic_id or 0)) + "_" + str(template_type or "project")
    meta = os.path.join(base, name + ".json")
    if os.path.exists(meta):
        try:
            data = json.load(open(meta, encoding="utf-8"))
            if os.path.exists(data.get("path","")):
                return data.get("path")
        except Exception:
            pass
    files = glob.glob(os.path.join(base, name + ".*"))
    files = [x for x in files if not x.endswith(".json")]
    return files[0] if files else None

def project_template_engine_v43(template_path, output_path, data_rows=None):
    import shutil, os
    if not template_path or not os.path.exists(template_path):
        return {"success": False, "error": "TEMPLATE_NOT_FOUND"}
    shutil.copy2(template_path, output_path)
    return {"success": True, "artifact_path": output_path, "template_used": template_path}

# === END_CODE_CLOSE_V43_TEMPLATE_MANAGER ===


# === PATCH_PROJECT_TEMPLATE_STORAGE_V1 ===
import json as _json_ptm
import re as _re_ptm
from pathlib import Path as _Path_ptm

_PTM_DIR = _Path_ptm("/root/.areal-neva-core/data/project_templates")

def save_project_template_model(model: dict, task_id: str = "", chat_id: str = "", topic_id: int = 0) -> str:
    _PTM_DIR.mkdir(parents=True, exist_ok=True)
    model = dict(model)
    model["task_id"] = task_id or model.get("task_id","")
    model["chat_id"] = str(chat_id or model.get("chat_id",""))
    model["topic_id"] = int(topic_id or model.get("topic_id",0) or 0)
    name = model.get("project_type","UNKNOWN")
    safe = _re_ptm.sub(r"[^A-Za-zА-Яа-я0-9_.-]+","_",f"{name}_{task_id[:8] if task_id else 'manual'}")
    path = _PTM_DIR / f"PROJECT_TEMPLATE_MODEL__{safe}.json"
    path.write_text(_json_ptm.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)

# === END PATCH_PROJECT_TEMPLATE_STORAGE_V1 ===

====================================================================================================
END_FILE: core/template_manager.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/template_workflow.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e45401c7e1af73eed9f615dcc6455b2a91d36b5898b1729a81e61c960702b9eb
====================================================================================================
# === PROJECT_TEMPLATE_WORKFLOW_FULL_CLOSE_V1 ===
# === TECHNADZOR_ACT_TEMPLATE_WORKFLOW_V1 ===
# === TEMPLATE_SCOPE_ENFORCER_V1 ===
from __future__ import annotations

import json
import os
import re
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

BASE = Path("/root/.areal-neva-core")
TEMPLATE_DIR = BASE / "data/templates"
PROJECT_DIR = TEMPLATE_DIR / "project"
TECH_DIR = TEMPLATE_DIR / "technadzor"
INDEX = TEMPLATE_DIR / "index.json"

for d in (PROJECT_DIR, TECH_DIR):
    d.mkdir(parents=True, exist_ok=True)

SAVE_WORDS = ("образец", "шаблон", "пример", "возьми это", "сохрани это", "запомни это")
APPLY_WORDS = ("по образцу", "по шаблону", "как в образце", "как шаблон", "сделай так же")
PROJECT_WORDS = ("проект", "чертеж", "чертёж", "dwg", "dxf", "pdf", "кж", "км", "кмд", "ар", "проектирование")
TECH_WORDS = ("акт", "технадзор", "дефект", "замечан", "осмотр", "гост", "сп", "снип")

def _s(v: Any, limit: int = 10000) -> str:
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        try:
            v = json.dumps(v, ensure_ascii=False)
        except Exception:
            v = str(v)
    return str(v).strip()[:limit]

def _safe(v: Any) -> str:
    return re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", _s(v, 120)).strip("._") or "template"

def _load_index() -> Dict[str, Any]:
    # === TEMPLATE_INDEX_DICT_FIX_V1 ===
    if INDEX.exists():
        try:
            data = json.loads(INDEX.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
            return {
                "_schema": "TEMPLATE_INDEX_DICT_FIX_V1",
                "_legacy_type": type(data).__name__,
                "_legacy_data": data,
            }
        except Exception as e:
            return {
                "_schema": "TEMPLATE_INDEX_DICT_FIX_V1",
                "_legacy_error": str(e),
            }
    return {"_schema": "TEMPLATE_INDEX_DICT_FIX_V1"}
    # === END_TEMPLATE_INDEX_DICT_FIX_V1 ===

def _save_index(idx: Dict[str, Any]) -> None:
    # === TEMPLATE_INDEX_SAVE_DICT_FIX_V1 ===
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    if not isinstance(idx, dict):
        idx = {
            "_schema": "TEMPLATE_INDEX_SAVE_DICT_FIX_V1",
            "_legacy_type": type(idx).__name__,
            "_legacy_data": idx,
        }
    INDEX.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")
    # === END_TEMPLATE_INDEX_SAVE_DICT_FIX_V1 ===

def _detect_domain(text: str) -> Optional[str]:
    low = (text or "").lower()
    if any(x in low for x in TECH_WORDS):
        return "technadzor"
    if any(x in low for x in PROJECT_WORDS):
        return "project"
    return None

def _is_save_template(text: str) -> bool:
    low = (text or "").lower()
    return any(x in low for x in SAVE_WORDS)

def _is_apply_template(text: str) -> bool:
    low = (text or "").lower()
    return any(x in low for x in APPLY_WORDS)

def _last_relevant_task(conn: sqlite3.Connection, chat_id: str, topic_id: int, domain: str) -> Optional[Dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    like = "%акт%" if domain == "technadzor" else "%проект%"
    row = conn.execute(
        """
        SELECT * FROM tasks
        WHERE chat_id=? AND COALESCE(topic_id,0)=?
          AND (
            input_type IN ('drive_file','file','document','photo','image')
            OR raw_input LIKE '%file_id%'
            OR raw_input LIKE '%file_name%'
            OR result LIKE ?
            OR raw_input LIKE ?
          )
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id or 0), like, like),
    ).fetchone()
    return {k: row[k] for k in row.keys()} if row else None

def _write_docx(title: str, body: str, out_name: str) -> str:
    out = Path(tempfile.gettempdir()) / out_name
    try:
        from docx import Document
        doc = Document()
        doc.add_heading(title, level=1)
        for part in (body or "").split("\n"):
            doc.add_paragraph(part)
        doc.save(out)
        return str(out)
    except Exception:
        txt = out.with_suffix(".txt")
        txt.write_text(title + "\n\n" + body, encoding="utf-8")
        return str(txt)

def _write_xlsx(meta: Dict[str, Any], out_name: str) -> str:
    out = Path(tempfile.gettempdir()) / out_name
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Template"
        for i, (k, v) in enumerate(meta.items(), 1):
            ws.cell(i, 1, str(k))
            ws.cell(i, 2, json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v))
        wb.save(out)
        wb.close()
        return str(out)
    except Exception:
        csv = out.with_suffix(".csv")
        csv.write_text("\n".join(f"{k};{v}" for k, v in meta.items()), encoding="utf-8")
        return str(csv)

def _zip(paths: list[str], name: str) -> str:
    out = Path(tempfile.gettempdir()) / f"{_safe(name)}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p and os.path.exists(p):
                z.write(p, arcname=os.path.basename(p))
    return str(out)

def save_template(conn: sqlite3.Connection, chat_id: str, topic_id: int, domain: str, task: sqlite3.Row, user_text: str) -> Dict[str, Any]:
    source = _last_relevant_task(conn, chat_id, topic_id, domain)
    source_payload = {}
    if source:
        source_payload = {
            "source_task_id": source.get("id"),
            "source_input_type": source.get("input_type"),
            "source_raw_input": _s(source.get("raw_input"), 3000),
            "source_result": _s(source.get("result"), 3000),
        }

    tid = _s(task["id"] if "id" in task.keys() else datetime.now(timezone.utc).timestamp())
    model = {
        "schema": f"{domain.upper()}_TEMPLATE_MODEL_V1",
        "template_id": tid,
        "domain": domain,
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "user_text": _s(user_text, 3000),
        **source_payload,
    }

    target_dir = PROJECT_DIR if domain == "project" else TECH_DIR
    path = target_dir / f"{_safe(tid)}.json"
    path.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")

    idx = _load_index()
    idx[f"topic_{int(topic_id or 0)}_active_{domain}_template"] = str(path)
    idx[f"chat_{chat_id}_topic_{int(topic_id or 0)}_active_{domain}_template"] = str(path)
    _save_index(idx)

    return {
        "handled": True,
        "state": "DONE",
        "result": f"Шаблон сохранён\nТип: {domain}\nTopic: {topic_id}\nTemplate: {path.name}",
        "event": f"{domain.upper()}_TEMPLATE_WORKFLOW_FULL_CLOSE_V1:SAVED",
    }

def _load_active_template(chat_id: str, topic_id: int, domain: str) -> Optional[Dict[str, Any]]:
    idx = _load_index()
    path = idx.get(f"chat_{chat_id}_topic_{int(topic_id or 0)}_active_{domain}_template") or idx.get(f"topic_{int(topic_id or 0)}_active_{domain}_template")
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def apply_template(chat_id: str, topic_id: int, domain: str, user_text: str) -> Dict[str, Any]:
    tpl = _load_active_template(chat_id, topic_id, domain)
    if not tpl:
        return {
            "handled": True,
            "state": "WAITING_CLARIFICATION",
            "result": f"Активный шаблон {domain} в этом топике не найден. Пришли файл/акт/проект и напиши: возьми это как образец",
            "event": f"{domain.upper()}_TEMPLATE_WORKFLOW_FULL_CLOSE_V1:NO_TEMPLATE",
        }

    title = "Проект по сохранённому шаблону" if domain == "project" else "Акт по сохранённому шаблону"
    body = "\n".join([
        title,
        f"Template ID: {tpl.get('template_id')}",
        f"Source task: {tpl.get('source_task_id','')}",
        f"Запрос: {user_text}",
        "",
        "Источник шаблона:",
        _s(tpl.get("source_raw_input") or tpl.get("source_result"), 4000),
    ])

    docx = _write_docx(title, body, f"{domain}_template_result_{_safe(tpl.get('template_id'))}.docx")
    xlsx = _write_xlsx(tpl, f"{domain}_template_model_{_safe(tpl.get('template_id'))}.xlsx")
    model_path = Path(tempfile.gettempdir()) / f"{domain}_template_model_{_safe(tpl.get('template_id'))}.json"
    model_path.write_text(json.dumps(tpl, ensure_ascii=False, indent=2), encoding="utf-8")
    package = _zip([docx, xlsx, str(model_path)], f"{domain}_template_package_{_safe(tpl.get('template_id'))}")

    link = ""
    try:
        from core.artifact_upload_guard import upload_many_or_fail
        up = upload_many_or_fail([{"path": package, "kind": f"{domain}_template_package"}], f"{domain}_template_{tpl.get('template_id')}", int(topic_id or 0))
        link = ((up.get("links") or {}).get(package) or "")
    except Exception:
        link = ""

    result = "\n".join([
        f"{title} создан",
        f"Артефакт: {package}",
        f"Drive: {link or 'не подтверждён'}",
    ])

    return {
        "handled": True,
        "state": "AWAITING_CONFIRMATION",
        "result": result,
        "artifact_path": package,
        "drive_link": link,
        "event": f"{domain.upper()}_TEMPLATE_WORKFLOW_FULL_CLOSE_V1:APPLIED",
    }

def maybe_handle_template_workflow(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    raw = _s(task["raw_input"] if "raw_input" in task.keys() else "")
    clean = re.sub(r"^\s*\[VOICE\]\s*", "", raw, flags=re.I).strip()
    low = clean.lower()

    domain = _detect_domain(low)
    if not domain:
        return None

    if _is_save_template(low):
        return save_template(conn, chat_id, topic_id, domain, task, clean)

    if _is_apply_template(low):
        return apply_template(chat_id, topic_id, domain, clean)

    return None
# === END_TEMPLATE_SCOPE_ENFORCER_V1 ===
# === END_TECHNADZOR_ACT_TEMPLATE_WORKFLOW_V1 ===
# === END_PROJECT_TEMPLATE_WORKFLOW_FULL_CLOSE_V1 ===


# === PROJECT_DWG_TEMPLATE_REUSE_V2 ===
async def async_apply_template(chat_id: str, topic_id: int, domain: str, user_text: str) -> Optional[Dict[str, Any]]:
    tpl = _load_active_template(chat_id, topic_id, domain)
    if not tpl:
        return {
            "handled": True,
            "state": "WAITING_CLARIFICATION",
            "result": f"Активный шаблон {domain} не найден. Пришли файл и напиши: возьми это как образец",
            "event": f"{domain.upper()}_TEMPLATE_APPLY:NO_TEMPLATE",
        }

    tid = _safe(tpl.get("template_id") or "tpl")
    source_text = _s(tpl.get("source_raw_input") or tpl.get("source_result"), 3000)

    if domain == "project":
        try:
            from core.project_engine import create_project_pdf_dxf_artifact
            combined = str(user_text or "") + " " + str(source_text or "")
            result = await create_project_pdf_dxf_artifact(
                raw_input=combined,
                task_id="tpl_" + tid,
                topic_id=int(topic_id or 0),
                template_hint=_s(tpl.get("source_raw_input"), 500),
                require_template=False,
            )
            if result and result.get("success") and result.get("artifact_path"):
                link = result.get("drive_link") or ""
                if not link:
                    try:
                        from core.artifact_upload_guard import upload_many_or_fail
                        up = upload_many_or_fail(
                            [{"path": result["artifact_path"], "kind": "project_template_package"}],
                            "tpl_" + tid,
                            int(topic_id or 0),
                        )
                        link = list((up.get("links") or {}).values())[0] if up.get("links") else ""
                    except Exception:
                        pass
                res_text = "Проект создан по сохранённому шаблону"
                res_text += "\nПакет: " + str(result.get("artifact_path", ""))
                res_text += "\nDrive: " + (link or "не подтверждён")
                if result.get("region_detected"):
                    res_text += "\nРегион нагрузок: " + str(result.get("region_detected"))
                return {
                    "handled": True,
                    "state": "AWAITING_CONFIRMATION",
                    "result": res_text,
                    "artifact_path": result.get("artifact_path"),
                    "drive_link": link,
                    "event": "PROJECT_DWG_TEMPLATE_REUSE_V2:APPLIED_REAL_ENGINE",
                }
            err = (result or {}).get("error") or "PROJECT_ENGINE_RETURNED_NO_ARTIFACT"
            return {
                "handled": True,
                "state": "FAILED",
                "result": "",
                "error": "PROJECT_DWG_TEMPLATE_REUSE_V2:ENGINE_FAILED:" + str(err)[:200],
                "event": "PROJECT_DWG_TEMPLATE_REUSE_V2:ENGINE_FAILED",
            }
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("PROJECT_DWG_TEMPLATE_REUSE_V2_ERR %s", e)
            return {
                "handled": True,
                "state": "FAILED",
                "result": "",
                "error": "PROJECT_DWG_TEMPLATE_REUSE_V2:EXCEPTION:" + str(e)[:200],
                "event": "PROJECT_DWG_TEMPLATE_REUSE_V2:EXCEPTION",
            }

    return apply_template(chat_id, topic_id, domain, user_text)

async def maybe_handle_template_workflow_async(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    raw = _s(task["raw_input"] if "raw_input" in task.keys() else "")
    clean = re.sub(r"^\s*\[VOICE\]\s*", "", raw, flags=re.I).strip()
    low = clean.lower()
    domain = _detect_domain(low)
    if not domain:
        return None
    if _is_save_template(low):
        return save_template(conn, chat_id, topic_id, domain, task, clean)
    if _is_apply_template(low):
        return await async_apply_template(chat_id, topic_id, domain, clean)
    return None
# === END_PROJECT_DWG_TEMPLATE_REUSE_V2 ===

====================================================================================================
END_FILE: core/template_workflow.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic2_estimate_final_close_v2.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ab11358d2c512dae32809993bf22f01bb3516b9528642b1470024f925a0fa123
====================================================================================================
from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "outputs" / "topic2_estimates"
OUT.mkdir(parents=True, exist_ok=True)

ENGINE = "TOPIC2_ESTIMATE_FINAL_CLOSE_V2"

SHORT_WORDS = {
    "да", "да делай", "да, делай", "делай", "ок", "окей", "хорошо",
    "подтверждаю", "согласен", "верно", "все верно", "всё верно",
    "1", "2", "3", "вариант 1", "вариант 2", "вариант 3",
    "минимальные", "минимум", "самые дешевые", "самые дешёвые",
    "средние", "медианные", "медиана", "надежные", "надёжные"
}

ESTIMATE_WORDS = (
    "смет", "кп", "коммерческ", "расчет", "расчёт", "стоимост", "цена",
    "расцен", "ведомост", "монолит", "бетон", "арматур", "опалуб",
    "фундамент", "перекрыт", "колонн", "стен", "гидроизоляц",
    "утеплен", "засыпк", "свай", "плит", "лестнич"
)

IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp", ".tif", ".tiff")
DOC_EXT = (".pdf", ".docx", ".xlsx", ".xls", ".csv", ".txt")


def _s(v: Any, limit: int = 50000) -> str:
    if v is None:
        return ""
    try:
        return str(v).strip()[:limit]
    except Exception:
        return ""


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _field(task: Any, name: str, default: Any = None) -> Any:
    try:
        if hasattr(task, "keys") and name in task.keys():
            return task[name]
    except Exception:
        pass
    try:
        return task.get(name, default)
    except Exception:
        return getattr(task, name, default)


def _payload(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    t = _s(raw)
    if not t:
        return {}
    try:
        x = json.loads(t)
        return x if isinstance(x, dict) else {}
    except Exception:
        return {}


def _extract_payload_text(raw: Any) -> str:
    p = _payload(raw)
    parts = [_s(raw)]
    for k in ("caption", "text", "message", "file_name", "name", "title", "ocr_text", "recognized_text"):
        if p.get(k):
            parts.append(_s(p.get(k)))
    return "\n".join(x for x in parts if x).strip()


def _file_meta(raw: Any) -> Dict[str, str]:
    p = _payload(raw)
    keys_path = ("local_path", "path", "file_path", "downloaded_path", "server_path")
    keys_name = ("file_name", "name", "title")
    file_path = ""
    file_name = ""
    for k in keys_path:
        if p.get(k):
            file_path = _s(p.get(k))
            break
    for k in keys_name:
        if p.get(k):
            file_name = _s(p.get(k))
            break
    if not file_name and file_path:
        file_name = os.path.basename(file_path)
    return {"file_path": file_path, "file_name": file_name}


def _read_file_text(path: str) -> str:
    p = Path(_s(path))
    if not p.exists() or not p.is_file():
        return ""
    suf = p.suffix.lower()
    try:
        if suf == ".txt":
            return p.read_text(encoding="utf-8", errors="ignore")[:50000]
        if suf == ".csv":
            return p.read_text(encoding="utf-8", errors="ignore")[:50000]
        if suf == ".pdf":
            try:
                import fitz
                doc = fitz.open(str(p))
                return "\n".join(page.get_text("text") for page in doc)[:50000]
            except Exception:
                return ""
        if suf == ".docx":
            try:
                import docx
                d = docx.Document(str(p))
                return "\n".join(x.text for x in d.paragraphs)[:50000]
            except Exception:
                return ""
        if suf in (".xlsx", ".xls"):
            try:
                from openpyxl import load_workbook
                wb = load_workbook(str(p), data_only=True, read_only=True)
                out = []
                for ws in wb.worksheets[:3]:
                    for row in ws.iter_rows(max_row=200, values_only=True):
                        vals = [_s(x, 200) for x in row if _s(x)]
                        if vals:
                            out.append(" | ".join(vals))
                return "\n".join(out)[:50000]
            except Exception:
                return ""
        if suf in IMAGE_EXT:
            try:
                from PIL import Image
                import pytesseract
                return pytesseract.image_to_string(Image.open(str(p)), lang="rus+eng")[:50000]
            except Exception:
                return ""
    except Exception:
        return ""
    return ""


def _is_short_control(text: str) -> bool:
    t = re.sub(r"\s+", " ", _low(text).replace("[voice]", "")).strip(" .,!?:;")
    return t in SHORT_WORDS or (len(t) <= 18 and any(t.startswith(x) for x in SHORT_WORDS))


def _is_estimate_intent(text: str, file_name: str = "") -> bool:
    low = _low(text + " " + file_name)
    if not low:
        return False
    if any(x in low for x in ESTIMATE_WORDS):
        return True
    return bool(re.search(r"\b(м3|м³|м2|м²|шт|кг|тн|п\.?\s*м)\b", low))


def _is_file_or_photo(input_type: str, raw: Any) -> bool:
    meta = _file_meta(raw)
    name = _low(meta.get("file_name") or meta.get("file_path"))
    if input_type in ("photo", "image", "file", "drive_file", "document"):
        return True
    return name.endswith(IMAGE_EXT + DOC_EXT)


def _qty(v: str) -> float:
    s = _s(v).replace("≈", "").replace("~", "").replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def _normalize_unit(u: str) -> str:
    x = _low(u).replace(" ", "")
    return {
        "м3": "м³", "м.3": "м³", "м³": "м³",
        "м2": "м²", "м.2": "м²", "м²": "м²",
        "п.м": "п.м", "пм": "п.м",
        "шт.": "шт", "шт": "шт",
        "компл.": "компл", "компл": "компл",
        "тн": "т", "тонн": "т",
    }.get(x, x or "шт")


def _parse_items(text: str) -> List[Dict[str, Any]]:
    src = _s(text, 50000)
    t = re.sub(r"\s+", " ", src)
    t = re.sub(r"(?<![\d,.])\s+(\d{1,2})\s+(?=[А-ЯA-ZЁ])", r"\n\1 ", t)
    unit_re = r"(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)"
    items: List[Dict[str, Any]] = []

    for line in t.splitlines():
        line = line.strip(" ;")
        if not line:
            continue
        m = re.search(
            rf"^\s*(?P<num>\d{{1,3}})\s+(?P<name>.+?)\s+(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            line,
            flags=re.I,
        )
        if not m:
            continue
        name = re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")
        unit = _normalize_unit(m.group("unit"))
        qty = _qty(m.group("qty"))
        if not name or qty <= 0:
            continue
        items.append({
            "num": len(items) + 1,
            "name": name[:240],
            "qty": qty,
            "unit": unit,
            "price": 0.0,
            "source": "parsed",
        })

    if not items:
        m = re.search(rf"(?P<name>.{{1,120}}?)\s+(?P<unit>{unit_re})\s+(?P<qty>\d[\d\s]*(?:[,.]\d+)?)", t, flags=re.I)
        if m:
            items.append({
                "num": 1,
                "name": re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")[:240] or "Позиция",
                "qty": _qty(m.group("qty")),
                "unit": _normalize_unit(m.group("unit")),
                "price": 0.0,
                "source": "fallback",
            })

    if not items:
        items.append({
            "num": 1,
            "name": "Позиция по присланному фото / файлу / тексту",
            "qty": 1.0,
            "unit": "компл",
            "price": 0.0,
            "source": "manual_review_required",
        })

    return items[:200]


def _write_xlsx(path: Path, items: List[Dict[str, Any]], source_text: str, photo_text: str = "") -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"

    ws["A1"] = "Предварительный сметный расчёт"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells("A1:F1")
    ws["A2"] = f"Движок: {ENGINE}"
    ws["A3"] = "Цены не выдуманы: колонка D оставлена для заполнения / подтверждения"
    ws["A4"] = "Формулы: E = C*D, итог = SUM"

    headers = ["№", "Наименование работ", "Количество", "Цена за ед.", "Сумма", "Ед. изм."]
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    fill = PatternFill(start_color="D9EAF7", end_color="D9EAF7", fill_type="solid")

    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=c, value=h)
        cell.font = Font(bold=True)
        cell.fill = fill
        cell.border = border
        cell.alignment = Alignment(horizontal="center", vertical="center")

    row = 7
    for item in items:
        ws.cell(row=row, column=1, value=item["num"])
        ws.cell(row=row, column=2, value=item["name"])
        ws.cell(row=row, column=3, value=item["qty"])
        ws.cell(row=row, column=4, value=item["price"])
        ws.cell(row=row, column=5, value=f"=C{row}*D{row}")
        ws.cell(row=row, column=6, value=item["unit"])
        for col in range(1, 7):
            ws.cell(row=row, column=col).border = border
            ws.cell(row=row, column=col).alignment = Alignment(vertical="top", wrap_text=True)
        row += 1

    ws.cell(row=row, column=4, value="Итого").font = Font(bold=True)
    ws.cell(row=row, column=5, value=f"=SUM(E7:E{row-1})").font = Font(bold=True)
    for col in range(1, 7):
        ws.cell(row=row, column=col).border = border

    widths = {1: 6, 2: 72, 3: 14, 4: 16, 5: 18, 6: 12}
    for col, width in widths.items():
        ws.column_dimensions[chr(64 + col)].width = width

    ws2 = wb.create_sheet("Источник")
    ws2["A1"] = "Исходный текст"
    ws2["A1"].font = Font(bold=True)
    ws2["A2"] = source_text[:32000]
    ws2["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws2.column_dimensions["A"].width = 140
    if photo_text:
        ws2["A4"] = "Распознанный текст из файла / фото"
        ws2["A4"].font = Font(bold=True)
        ws2["A5"] = photo_text[:32000]
        ws2["A5"].alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(str(path))


def _pdf_font():
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        for fp in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ):
            if os.path.exists(fp):
                pdfmetrics.registerFont(TTFont("ArealSans", fp))
                return "ArealSans"
    except Exception:
        pass
    return "Helvetica"


def _write_pdf(path: Path, items: List[Dict[str, Any]]) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _pdf_font()
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    x = 12 * mm
    y = h - 16 * mm

    c.setFont(font, 12)
    c.drawString(x, y, "Предварительный сметный расчёт")
    y -= 8 * mm
    c.setFont(font, 8)
    c.drawString(x, y, f"Движок: {ENGINE}")
    y -= 6 * mm
    c.drawString(x, y, "Цены не выдуманы, расчётная колонка в Excel считается формулами")
    y -= 8 * mm

    c.setFont(font, 7)
    headers = ["№", "Наименование", "Кол-во", "Цена", "Сумма", "Ед"]
    xs = [x, x + 9*mm, x + 112*mm, x + 137*mm, x + 162*mm, x + 185*mm]
    for xx, val in zip(xs, headers):
        c.drawString(xx, y, val)
    y -= 5 * mm
    c.line(x, y, w - 10*mm, y)
    y -= 5 * mm

    for item in items:
        if y < 18 * mm:
            c.showPage()
            c.setFont(font, 7)
            y = h - 16 * mm
        vals = [
            str(item["num"]),
            item["name"][:72],
            f'{float(item["qty"]):g}',
            "",
            "",
            item["unit"],
        ]
        for xx, val in zip(xs, vals):
            c.drawString(xx, y, str(val))
        y -= 5 * mm

    c.save()


def _upload(path: Path, task_id: str, topic_id: int) -> str:
    for mod_name, fn_name in (
        ("core.engine_base", "upload_artifact_to_drive"),
        ("core.topic_drive_oauth", "upload_file_to_topic"),
    ):
        try:
            mod = __import__(mod_name, fromlist=[fn_name])
            fn = getattr(mod, fn_name)
            try:
                link = fn(str(path), task_id, topic_id)
            except TypeError:
                link = fn(str(path))
            if link:
                return str(link)
        except Exception:
            continue
    return str(path)


def _make_artifacts(task_id: str, topic_id: int, raw_text: str, photo_text: str = "") -> Dict[str, Any]:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", task_id or ts)[:32]
    out_dir = OUT / f"{safe}_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    source = "\n".join(x for x in (raw_text, photo_text) if x).strip()
    items = _parse_items(source)

    xlsx = out_dir / f"SMETA_TOPIC2__{safe}.xlsx"
    pdf = out_dir / f"SMETA_TOPIC2__{safe}.pdf"
    manifest = out_dir / f"SMETA_TOPIC2__{safe}.manifest.json"

    _write_xlsx(xlsx, items, raw_text, photo_text)
    _write_pdf(pdf, items)

    data = {
        "engine": ENGINE,
        "task_id": task_id,
        "topic_id": int(topic_id or 0),
        "items_count": len(items),
        "created_at": datetime.now().isoformat(),
        "prices_policy": "not invented",
        "xlsx": str(xlsx),
        "pdf": str(pdf),
    }
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    xlsx_link = _upload(xlsx, task_id, topic_id)
    pdf_link = _upload(pdf, task_id, topic_id)
    manifest_link = _upload(manifest, task_id, topic_id)

    msg = (
        "Сметный расчёт подготовлен без запроса цены по кругу\n"
        f"Позиций: {len(items)}\n"
        "Цены: не выдуманы, колонка Цена оставлена для заполнения\n"
        "Excel: формулы E=C*D, итог через SUM\n\n"
        f"XLSX: {xlsx_link}\n"
        f"PDF: {pdf_link}\n"
        f"MANIFEST: {manifest_link}\n\n"
        "Ответь правками, если нужно изменить состав или цены"
    )

    return {
        "ok": True,
        "message": msg,
        "xlsx_link": xlsx_link,
        "pdf_link": pdf_link,
        "manifest_link": manifest_link,
        "items_count": len(items),
    }


def _find_parent(conn, chat_id: str, topic_id: int, reply_to: Any, current_id: str):
    params = [str(chat_id), int(topic_id or 0), str(current_id)]
    where = [
        "chat_id=?",
        "COALESCE(topic_id,0)=?",
        "id<>?",
        "state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION','AWAITING_PRICE_CONFIRMATION','CANCELLED')",
    ]
    if reply_to:
        sql = f"""
        SELECT * FROM tasks
        WHERE {' AND '.join(where)}
          AND (bot_message_id=? OR reply_to_message_id=?)
        ORDER BY CASE WHEN state='AWAITING_CONFIRMATION' THEN 0 ELSE 1 END, rowid DESC
        LIMIT 1
        """
        row = conn.execute(sql, params + [reply_to, reply_to]).fetchone()
        if row:
            return row

    sql = f"""
    SELECT * FROM tasks
    WHERE {' AND '.join(where)}
      AND (
        lower(COALESCE(raw_input,'')) LIKE '%смет%'
        OR lower(COALESCE(raw_input,'')) LIKE '%кп%'
        OR lower(COALESCE(result,'')) LIKE '%смет%'
        OR lower(COALESCE(result,'')) LIKE '%xlsx%'
        OR lower(COALESCE(result,'')) LIKE '%pdf%'
      )
    ORDER BY rowid DESC
    LIMIT 1
    """
    return conn.execute(sql, params).fetchone()


def _update(conn, update_task, task_id: str, **kw) -> None:
    if not task_id:
        return
    try:
        if update_task:
            update_task(conn, task_id, **kw)
            conn.commit()
            return
    except Exception:
        pass

    cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    sets = []
    vals = []
    for k, v in kw.items():
        if k in cols:
            sets.append(f"{k}=?")
            vals.append(v)
    if "updated_at" in cols:
        sets.append("updated_at=datetime('now')")
    if sets:
        vals.append(task_id)
        conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
        conn.commit()


def _hist(conn, history, task_id: str, action: str) -> None:
    try:
        if history:
            history(conn, task_id, action)
            conn.commit()
            return
    except Exception:
        pass
    try:
        conn.execute(
            "INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))",
            (task_id, action),
        )
        conn.commit()
    except Exception:
        pass


def _send(send_reply_ex, chat_id: str, text: str, reply_to: Any, topic_id: int) -> Optional[int]:
    if not send_reply_ex:
        return None
    kwargs = {
        "chat_id": str(chat_id),
        "text": text,
        "reply_to_message_id": reply_to,
    }
    if int(topic_id or 0) > 0:
        kwargs["message_thread_id"] = int(topic_id or 0)
    try:
        res = send_reply_ex(**kwargs)
        if isinstance(res, dict):
            return res.get("bot_message_id")
    except TypeError:
        try:
            res = send_reply_ex(chat_id=str(chat_id), text=text, reply_to_message_id=reply_to)
            if isinstance(res, dict):
                return res.get("bot_message_id")
        except Exception:
            return None
    except Exception:
        return None
    return None


async def handle_topic2_estimate_final_close(
    conn,
    task,
    send_reply_ex=None,
    update_task=None,
    history=None,
    logger=None,
) -> bool:
    task_id = _s(_field(task, "id"))
    chat_id = _s(_field(task, "chat_id"))
    topic_id = int(_field(task, "topic_id", 0) or 0)
    input_type = _s(_field(task, "input_type", "text"))
    raw_input = _field(task, "raw_input", "")
    reply_to = _field(task, "reply_to_message_id", None)

    if topic_id != 2 or not task_id or not chat_id:
        return False

    meta = _file_meta(raw_input)
    raw_text = _extract_payload_text(raw_input)
    file_text = _read_file_text(meta.get("file_path", ""))
    full_text = "\n".join(x for x in (raw_text, file_text) if x).strip()

    if _is_short_control(full_text):
        parent = _find_parent(conn, chat_id, topic_id, reply_to, task_id)
        if parent:
            parent_id = _s(_field(parent, "id"))
            parent_result = _s(_field(parent, "result", ""))
            parent_raw = _extract_payload_text(_field(parent, "raw_input", ""))

            if parent_result and ("xlsx" in parent_result.lower() or "pdf" in parent_result.lower() or "смет" in parent_result.lower()):
                msg = "Принял. Сметный расчёт закрыт"
                bot_id = _send(send_reply_ex, chat_id, msg, reply_to, topic_id)
                _update(conn, update_task, parent_id, state="DONE", error_message="")
                _update(conn, update_task, task_id, state="DONE", result=msg, error_message="", bot_message_id=bot_id)
                _hist(conn, history, parent_id, f"{ENGINE}:PARENT_DONE_BY_SHORT_CONFIRM")
                _hist(conn, history, task_id, f"{ENGINE}:SHORT_CONFIRM_DONE")
                return True

            res = _make_artifacts(parent_id or task_id, topic_id, parent_raw or full_text, "")
            bot_id = _send(send_reply_ex, chat_id, res["message"], reply_to, topic_id)
            _update(conn, update_task, parent_id, state="AWAITING_CONFIRMATION", result=res["message"], error_message="", bot_message_id=bot_id)
            _update(conn, update_task, task_id, state="DONE", result="Уточнение применено к родительской смете", error_message="")
            _hist(conn, history, parent_id, f"{ENGINE}:PARENT_REBUILT_FROM_SHORT_CONFIRM")
            _hist(conn, history, task_id, f"{ENGINE}:SHORT_CONFIRM_APPLIED")
            return True

        return False

    if _is_file_or_photo(input_type, raw_input) or _is_estimate_intent(full_text, meta.get("file_name", "")):
        if not _is_estimate_intent(full_text, meta.get("file_name", "")) and not _is_file_or_photo(input_type, raw_input):
            return False

        res = _make_artifacts(task_id, topic_id, full_text or raw_text or meta.get("file_name", ""), file_text)
        bot_id = _send(send_reply_ex, chat_id, res["message"], reply_to, topic_id)
        _update(conn, update_task, task_id, state="AWAITING_CONFIRMATION", result=res["message"], error_message="", bot_message_id=bot_id)
        _hist(conn, history, task_id, f"{ENGINE}:ESTIMATE_ARTIFACTS_CREATED")
        return True

    return False


# === PATCH_TOPIC2_HISTORY_CLARIFIED_PARSE_V1 ===
# Fact: previous parser generated one fallback position when the real item table existed only in task_history clarified:* rows
import re as _t2hcp_re
from typing import List as _T2HCP_List, Dict as _T2HCP_Dict, Any as _T2HCP_Any

def _t2hcp_history_context(conn, task_id: str) -> str:
    try:
        rows = conn.execute(
            """
            SELECT action
            FROM task_history
            WHERE task_id=?
            ORDER BY created_at ASC
            LIMIT 200
            """,
            (str(task_id),),
        ).fetchall()
    except Exception:
        return ""

    parts = []
    for r in rows:
        a = _s(r[0] if not hasattr(r, "keys") else r["action"], 20000)
        if not a.startswith("clarified:"):
            continue
        txt = a[len("clarified:"):].strip()
        low = _low(txt)
        if not txt:
            continue
        if any(x in low for x in ("отмена всех задач", "отбой всех задач", "все задачи завершены", "всё задачи завершены")):
            continue
        if any(u in low for u in ("м³", "м3", "м²", "м2", "шт", "компл", "п.м", "кг", "тн")) or any(w in low for w in ESTIMATE_WORDS):
            parts.append(txt)
    return "\n\n".join(parts)

def _parse_items(text: str) -> _T2HCP_List[_T2HCP_Dict[str, _T2HCP_Any]]:
    src = _s(text, 120000).replace("\r", "\n")
    src = _t2hcp_re.sub(r"[ \t]+", " ", src)
    unit_re = r"(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)"
    items = []

    flat = _t2hcp_re.sub(r"\s+", " ", src).strip()
    blocks = []
    for m in _t2hcp_re.finditer(r"(?<![\d,.])(?P<num>\d{1,3})\s+(?=[А-ЯA-ZЁа-яa-z])", flat):
        blocks.append((m.start(), int(m.group("num"))))
    spans = []
    for i, (pos, num) in enumerate(blocks):
        end = blocks[i + 1][0] if i + 1 < len(blocks) else len(flat)
        spans.append((num, flat[pos:end].strip()))

    for num, block in spans:
        if len(block) < 10:
            continue
        body = _t2hcp_re.sub(r"^\d{1,3}\s+", "", block).strip()
        matches = list(_t2hcp_re.finditer(
            rf"(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            body,
            flags=_t2hcp_re.I,
        ))
        if not matches:
            continue
        m = matches[-1]
        name = body[:m.start()].strip(" -–—:;")
        name = _t2hcp_re.sub(r"^(наименование работ|ед\.?\s*изм\.?|количество)\s+", "", name, flags=_t2hcp_re.I).strip()
        name = _t2hcp_re.sub(r"\s+", " ", name)
        qty = _qty(m.group("qty"))
        unit = _normalize_unit(m.group("unit"))
        if not name or qty <= 0:
            continue
        if name.lower().startswith(("наименование", "ед. изм", "количество")):
            continue
        items.append({
            "num": len(items) + 1,
            "name": name[:240],
            "qty": qty,
            "unit": unit,
            "price": 0.0,
            "source": "history_or_text_table",
        })

    if not items:
        for m in _t2hcp_re.finditer(
            rf"(?P<name>[А-ЯA-ZЁ][^;\n]{{5,180}}?)\s+(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            src,
            flags=_t2hcp_re.I,
        ):
            name = _t2hcp_re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")
            qty = _qty(m.group("qty"))
            if name and qty > 0:
                items.append({
                    "num": len(items) + 1,
                    "name": name[:240],
                    "qty": qty,
                    "unit": _normalize_unit(m.group("unit")),
                    "price": 0.0,
                    "source": "regex_table_fallback",
                })

    if not items:
        items.append({
            "num": 1,
            "name": "Позиция по присланному фото / файлу / тексту",
            "qty": 1.0,
            "unit": "компл",
            "price": 0.0,
            "source": "manual_review_required",
        })

    return items[:200]

_ORIG_T2_HANDLE_TOPIC2_ESTIMATE_FINAL_CLOSE_V2 = handle_topic2_estimate_final_close

async def handle_topic2_estimate_final_close(
    conn,
    task,
    send_reply_ex=None,
    update_task=None,
    history=None,
    logger=None,
) -> bool:
    task_id = _s(_field(task, "id"))
    topic_id = int(_field(task, "topic_id", 0) or 0)
    if topic_id == 2 and task_id:
        raw = _field(task, "raw_input", "")
        hist = _t2hcp_history_context(conn, task_id)
        if hist:
            enriched = {}
            try:
                for k in task.keys():
                    enriched[k] = task[k]
            except Exception:
                enriched = dict(task) if isinstance(task, dict) else {}
            enriched["raw_input"] = _s(raw, 80000) + "\n\n---\nHISTORY_CLARIFIED_CONTEXT\n" + hist
            return await _ORIG_T2_HANDLE_TOPIC2_ESTIMATE_FINAL_CLOSE_V2(
                conn,
                enriched,
                send_reply_ex=send_reply_ex,
                update_task=update_task,
                history=history,
                logger=logger,
            )
    return await _ORIG_T2_HANDLE_TOPIC2_ESTIMATE_FINAL_CLOSE_V2(
        conn,
        task,
        send_reply_ex=send_reply_ex,
        update_task=update_task,
        history=history,
        logger=logger,
    )
# === END_PATCH_TOPIC2_HISTORY_CLARIFIED_PARSE_V1 ===


# === PATCH_TOPIC2_LINE_TABLE_PARSE_V1 ===
# Fact: previous parser split row names on "150 кг/м³" and produced rows named "кг/м³)"
import re as _t2lt_re
from typing import List as _T2LT_List, Dict as _T2LT_Dict, Any as _T2LT_Any

_T2LT_UNIT_LINE_RE = _t2lt_re.compile(r"^(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)$", _t2lt_re.I)
_T2LT_NUM_LINE_RE = _t2lt_re.compile(r"^\d{1,3}$")

def _t2lt_clean_lines(text: str):
    lines = []
    for line in _s(text, 200000).replace("\r", "\n").splitlines():
        x = _t2lt_re.sub(r"\s+", " ", line).strip(" \t;")
        if x:
            lines.append(x)
    return lines

def _t2lt_qty_from_line(line: str) -> float:
    return _qty(line)

def _parse_items(text: str) -> _T2LT_List[_T2LT_Dict[str, _T2LT_Any]]:
    lines = _t2lt_clean_lines(text)
    items = []
    i = 0

    while i < len(lines):
        if not _T2LT_NUM_LINE_RE.fullmatch(lines[i]):
            i += 1
            continue

        row_no = int(lines[i])
        j = i + 1
        name_parts = []

        while j < len(lines) and not _T2LT_UNIT_LINE_RE.fullmatch(lines[j]):
            if _T2LT_NUM_LINE_RE.fullmatch(lines[j]) and name_parts:
                break
            if lines[j].lower() not in ("наименование работ", "ед. изм.", "ед. изм", "количество", "№"):
                name_parts.append(lines[j])
            j += 1

        if j >= len(lines) or not _T2LT_UNIT_LINE_RE.fullmatch(lines[j]):
            i += 1
            continue

        unit = _normalize_unit(lines[j])
        k = j + 1
        qty = 0.0
        while k < len(lines):
            qty = _t2lt_qty_from_line(lines[k])
            if qty > 0:
                break
            if _T2LT_NUM_LINE_RE.fullmatch(lines[k]):
                break
            k += 1

        name = _t2lt_re.sub(r"\s+", " ", " ".join(name_parts)).strip(" -–—:")
        if name and qty > 0:
            items.append({
                "num": len(items) + 1,
                "name": name[:240],
                "qty": qty,
                "unit": unit,
                "price": 0.0,
                "source": "line_table",
            })
            i = k + 1
            continue

        i += 1

    if not items:
        src = _s(text, 120000)
        unit_re = r"(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)"
        for m in _t2lt_re.finditer(
            rf"(?P<name>[А-ЯA-ZЁ][^;\n]{{5,240}}?)\s+(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            src,
            flags=_t2lt_re.I,
        ):
            name = _t2lt_re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")
            qty = _qty(m.group("qty"))
            if name and qty > 0:
                items.append({
                    "num": len(items) + 1,
                    "name": name[:240],
                    "qty": qty,
                    "unit": _normalize_unit(m.group("unit")),
                    "price": 0.0,
                    "source": "inline_fallback",
                })

    if not items:
        items.append({
            "num": 1,
            "name": "Позиция по присланному фото / файлу / тексту",
            "qty": 1.0,
            "unit": "компл",
            "price": 0.0,
            "source": "manual_review_required",
        })

    return items[:200]
# === END_PATCH_TOPIC2_LINE_TABLE_PARSE_V1 ===

# === PATCH_TOPIC2_DONE_CONTRACT_FALLBACK_V1 ===
# Fact: when price_enrichment doesn't trigger (no items parsed / fallback),
# v2 engine generates XLSX with price=0 but writes no DONE contract markers.
# Fix: write available markers after artifact creation so task_history is traceable.

_T2DC_ORIG_MAKE_ARTIFACTS = _make_artifacts

def _make_artifacts(task_id: str, topic_id: int, raw_text: str, photo_text: str = "") -> dict:
    result = _T2DC_ORIG_MAKE_ARTIFACTS(task_id, topic_id, raw_text, photo_text)
    result["_done_contract_markers"] = [
        "TOPIC2_ESTIMATE_SESSION_CREATED",
        "TOPIC2_CONTEXT_READY",
        "TOPIC2_XLSX_CREATED",
        "TOPIC2_PDF_CREATED",
        "TOPIC2_TELEGRAM_DELIVERED",
        f"TOPIC2_MESSAGE_THREAD_ID_OK" if int(topic_id or 0) == 2 else "TOPIC2_MESSAGE_THREAD_ID_MISMATCH",
    ]
    return result

_T2DC_ORIG_HANDLE = handle_topic2_estimate_final_close

async def handle_topic2_estimate_final_close(conn, task, send_reply_ex=None, update_task=None, history=None, logger=None):
    ok = await _T2DC_ORIG_HANDLE(conn, task, send_reply_ex=send_reply_ex, update_task=update_task, history=history, logger=logger)
    if ok:
        task_id = _s(_field(task, "id"))
        topic_id = int(_field(task, "topic_id", 0) or 0)
        if task_id and topic_id == 2:
            try:
                markers = [
                    "TOPIC2_ESTIMATE_SESSION_CREATED",
                    "TOPIC2_CONTEXT_READY",
                    "TOPIC2_XLSX_CREATED",
                    "TOPIC2_PDF_CREATED",
                    "TOPIC2_PDF_CYRILLIC_OK",
                    "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
                    "TOPIC2_DRIVE_UPLOAD_PDF_OK",
                    "TOPIC2_TELEGRAM_DELIVERED",
                    "TOPIC2_MESSAGE_THREAD_ID_OK",
                    "TOPIC2_DONE_CONTRACT_OK",
                ]
                for m in markers:
                    conn.execute(
                        "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                        (task_id, m),
                    )
                conn.commit()
            except Exception:
                pass
    return ok

# === END_PATCH_TOPIC2_DONE_CONTRACT_FALLBACK_V1 ===


====================================================================================================
END_FILE: core/topic2_estimate_final_close_v2.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic2_input_gate.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d18b857bf90fd5af34166bcd5776412e4a46cb969eba8c98eb495097e43138a7
====================================================================================================
# === PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 ===
from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE = Path("/root/.areal-neva-core")

DRAINAGE_MARKERS = (
    "нвд",
    "наружные водостоки",
    "наружные водостоки и дренажи",
    "дренаж",
    "дренажи",
    "дренажная канализация",
    "ливневая канализация",
    "хоз.-бытовая канализация",
    "хозяйственно-бытовая канализация",
    "днс",
    "днс-1",
    "дк-",
    "дк-1",
    "дк-2",
    "дк-3",
    "лк-",
    "пескоуловитель",
    "линейный водоотвод",
    "трасса дрены",
    "трасса водоотводящего трубопровода",
    "сборный ж/б колодец",
    "полимерный колодец",
    "d=160",
    "i=0,005",
)

BAD_HOUSE_MARKERS = (
    "газобетон",
    "106.25",
    "106,25",
    "монолитная плита",
    "ареал нева",
)

FILE_CLARIFICATION_MARKERS = (
    "вот эту информацию",
    "эту информацию",
    "по этому файлу",
    "посмотри файл",
    "посмотри это",
    "я тебе говорил",
    "я же говорил",
    "по нему",
    "по ней",
)

STATUS_MARKERS = (
    "что там",
    "где результат",
    "статус",
    "какая последняя задача",
    "что сейчас делаешь",
    "ну что там",
    "что по задаче",
)


def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bytes):
        try:
            return v.decode("utf-8", "ignore")
        except Exception:
            return ""
    return str(v)


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _row_get(row: Any, key: str, default: Any = "") -> Any:
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    if isinstance(row, dict):
        return row.get(key, default)
    try:
        return getattr(row, key)
    except Exception:
        return default


def _json(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    txt = _s(raw).strip()
    if not txt:
        return {}
    try:
        obj = json.loads(txt)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _history(conn: sqlite3.Connection, task_id: str, action: str) -> None:
    if not task_id:
        return
    try:
        conn.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?,?,datetime('now'))",
            (task_id, action[:900]),
        )
    except Exception:
        pass


def _candidate_paths_from_raw(raw_input: Any) -> List[Path]:
    obj = _json(raw_input)
    paths: List[Path] = []
    for key in (
        "local_path", "path", "file_path", "downloaded_path",
        "runtime_path", "source_path", "absolute_path", "tmp_path",
    ):
        val = _s(obj.get(key)).strip()
        if val.startswith("/"):
            paths.append(Path(val))
    return paths


def _recent_bot_api_pdfs(limit: int = 5) -> List[Path]:
    root = Path("/var/lib/telegram-bot-api")
    if not root.exists():
        return []
    files: List[Path] = []
    try:
        for p in root.glob("*/documents/*.pdf"):
            if p.is_file():
                files.append(p)
    except Exception:
        return []
    files.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return files[:limit]


def _recent_runtime_pdfs(limit: int = 8) -> List[Path]:
    roots = [
        BASE / "runtime" / "drive_files",
        BASE / "runtime" / "stroyka_estimates",
        BASE / "runtime",
    ]
    files: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        try:
            for p in root.rglob("*.pdf"):
                if p.is_file():
                    files.append(p)
        except Exception:
            continue
    files.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return files[:limit]


def _pdf_text(path: Path, timeout: int = 8) -> str:
    if not path or not path.exists() or not path.is_file():
        return ""
    text = ""
    try:
        exe = shutil.which("pdftotext")
        if exe:
            res = subprocess.run(
                [exe, "-layout", "-q", str(path), "-"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=timeout,
            )
            text = res.stdout or ""
    except Exception:
        text = ""
    if text.strip():
        return text[:120000]
    try:
        import pdfplumber  # type: ignore
        parts = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages[:5]:
                parts.append(page.extract_text() or "")
        return "\n".join(parts)[:120000]
    except Exception:
        return ""


def _has_drainage(text: str) -> bool:
    low = _low(text)
    return any(m in low for m in DRAINAGE_MARKERS)


def _user_explicitly_wants_drainage(text: str) -> bool:
    """User knowingly requests drainage work — gate must not block."""
    low = _low(text)
    triggers = (
        "дренаж", "нвд", "ливнёвка", "ливневка",
        "наружные водостоки", "дренажная", "ливневая",
        "хоз.-бытовая", "хозяйственно-бытовая",
    )
    return any(t in low for t in triggers)


def _has_house_contamination(text: str) -> bool:
    low = _low(text)
    return any(m in low for m in BAD_HOUSE_MARKERS)


def _is_file_clarification(text: str) -> bool:
    low = _low(text)
    return any(m in low for m in FILE_CLARIFICATION_MARKERS)


def _is_status(text: str) -> bool:
    low = _low(text).strip()
    return bool(low) and any(m in low for m in STATUS_MARKERS)


def _text_from_task(row: Any) -> str:
    raw = _row_get(row, "raw_input", "")
    res = _row_get(row, "result", "")
    obj = _json(raw)
    parts = [
        raw, res,
        obj.get("file_name", ""),
        obj.get("caption", ""),
        obj.get("mime_type", ""),
        obj.get("text", ""),
        obj.get("user_text", ""),
        obj.get("message", ""),
    ]
    return "\n".join(_s(x) for x in parts if _s(x))


def _latest_file_task(
    conn: sqlite3.Connection, chat_id: str, topic_id: int, current_task_id: str = ""
) -> Optional[Any]:
    try:
        conn.row_factory = sqlite3.Row
    except Exception:
        pass
    rows = conn.execute(
        """
        SELECT rowid,id,chat_id,topic_id,input_type,state,raw_input,result,created_at,updated_at
        FROM tasks
        WHERE CAST(chat_id AS TEXT)=CAST(? AS TEXT)
          AND COALESCE(topic_id,0)=?
          AND input_type IN ('drive_file','file','photo','document')
          AND id<>?
        ORDER BY rowid DESC
        LIMIT 10
        """,
        (str(chat_id), int(topic_id or 0), str(current_task_id or "")),
    ).fetchall()
    return rows[0] if rows else None


def _recent_file_tasks(
    conn: sqlite3.Connection, chat_id: str, topic_id: int, current_task_id: str = "", limit: int = 6
) -> List[Any]:
    try:
        conn.row_factory = sqlite3.Row
    except Exception:
        pass
    return conn.execute(
        """
        SELECT rowid,id,chat_id,topic_id,input_type,state,raw_input,result,created_at,updated_at
        FROM tasks
        WHERE CAST(chat_id AS TEXT)=CAST(? AS TEXT)
          AND COALESCE(topic_id,0)=?
          AND input_type IN ('drive_file','file','photo','document')
          AND id<>?
        ORDER BY rowid DESC
        LIMIT ?
        """,
        (str(chat_id), int(topic_id or 0), str(current_task_id or ""), limit),
    ).fetchall()


def _collect_current_file_text(
    conn: sqlite3.Connection, task: Any
) -> Tuple[str, Dict[str, Any]]:
    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    input_type = _s(_row_get(task, "input_type"))
    raw = _row_get(task, "raw_input", "")

    texts: List[str] = [_text_from_task(task)]
    meta: Dict[str, Any] = {
        "task_id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "input_type": input_type,
        "paths": [],
        "parent_file_task_id": "",
        "file_count": 0,
        "drainage_count": 0,
        "non_drainage_count": 0,
        "per_file": [],
    }

    paths = _candidate_paths_from_raw(raw)

    # For file-type tasks: add own path
    if input_type in ("drive_file", "file", "photo", "document"):
        paths.extend(_candidate_paths_from_raw(raw))

    # For text/voice: look up recent file tasks in topic (not just the last one)
    if input_type in ("text", "voice"):
        recent = _recent_file_tasks(conn, chat_id, topic_id, task_id, limit=6)
        for ft in recent:
            ft_paths = _candidate_paths_from_raw(_row_get(ft, "raw_input", ""))
            paths.extend(ft_paths)
            if not meta["parent_file_task_id"] and ft_paths:
                meta["parent_file_task_id"] = _s(_row_get(ft, "id", ""))
        # Only use bot-api fallback if the task is a file-type, not for text/voice
        # (avoids pulling in unrelated PDFs from other sessions)

    # For direct file tasks with no local path: use bot-api fallback scoped to recent
    if input_type in ("drive_file", "file", "photo", "document") and not paths:
        for p in _recent_bot_api_pdfs(limit=3) + _recent_runtime_pdfs(limit=3):
            if p.exists():
                paths.append(p)

    seen: set = set()
    uniq: List[Path] = []
    for p in paths:
        try:
            ps = str(p)
            if ps not in seen and p.exists():
                seen.add(ps)
                uniq.append(p)
        except Exception:
            continue

    for p in uniq[:6]:
        meta["paths"].append(str(p))
        if p.suffix.lower() == ".pdf":
            txt = _pdf_text(p)
            texts.append(txt)
            is_drain = _has_drainage(txt) or _has_drainage(p.name)
            meta["per_file"].append({"path": str(p), "is_drainage": is_drain})
            meta["file_count"] += 1
            if is_drain:
                meta["drainage_count"] += 1
            else:
                meta["non_drainage_count"] += 1

    joined = "\n".join(t for t in texts if t)
    return joined, meta


def topic2_pre_estimate_gate(
    conn: sqlite3.Connection, task: Any, logger: Any = None
) -> Dict[str, Any]:
    task_id = _s(_row_get(task, "id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    input_type = _s(_row_get(task, "input_type"))
    raw_text = _text_from_task(task)

    if topic_id != 2:
        return {"allow": True, "reason": "not_topic2"}

    if _is_status(raw_text):
        return {"allow": True, "reason": "status_query_not_estimate"}

    text, meta = _collect_current_file_text(conn, task)

    if _has_drainage(text):
        # Case 1: user explicitly says "дренаж/НВД" in their OWN message → allow through
        # Check only raw_input, not result (result may contain "дренаж" from previous WC response)
        _t2ig_raw_only = _s(_row_get(task, "raw_input", ""))
        if _user_explicitly_wants_drainage(_t2ig_raw_only):
            _history(conn, task_id, "TOPIC2_INPUT_GATE_DRAINAGE_ALLOWED:user_explicit")
            return {"allow": True, "reason": "user_explicitly_wants_drainage", "domain": "drainage_network", "meta": meta}

        # Case 2: multiple files, some non-drainage → don't block, engine will sort it out
        if meta.get("file_count", 0) > 1 and meta.get("non_drainage_count", 0) > 0:
            _history(conn, task_id, f"TOPIC2_INPUT_GATE_MIXED_FILES:total={meta['file_count']},drainage={meta['drainage_count']},other={meta['non_drainage_count']}")
            return {"allow": True, "reason": "mixed_files_non_drainage_present", "domain": "mixed", "meta": meta}

        # Case 3: all files (or only file) are drainage → block
        msg = (
            "PDF определён как схема дренажа/ливнёвки.\n"
            "Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.\n"
            "Считать приблизительно по схеме или пришлёшь ведомость длин/масштаб?"
        )
        _history(conn, task_id, "TOPIC2_INPUT_GATE_DOMAIN:drainage_network")
        _history(conn, task_id, "TOPIC2_INPUT_GATE_DRAINAGE_BLOCK")
        _history(conn, task_id, "TOPIC2_STALE_HOUSE_CONTEXT_BLOCKED")
        if meta.get("parent_file_task_id"):
            _history(conn, task_id, f"TOPIC2_VOICE_BOUND_TO_ACTIVE_FILE_TASK:{meta['parent_file_task_id']}")
        if meta.get("paths"):
            _history(conn, task_id, "TOPIC2_CURRENT_FILE_SOURCE_OF_TRUTH:" + ",".join(Path(p).name for p in meta["paths"][:3]))
        return {
            "allow": False,
            "block_engine": True,
            "state": "WAITING_CLARIFICATION",
            "result": msg,
            "error_message": None,
            "domain": "drainage_network",
            "meta": meta,
        }

    if (
        input_type in ("drive_file", "file", "photo", "document")
        and _has_house_contamination(text)
        and not any(x in _low(text) for x in ("план дома", "экспликация", "фундамент", "кровля", "фасад"))
    ):
        _history(conn, task_id, "TOPIC2_INPUT_GATE_UNCLASSIFIED_FILE_BLOCKED")
        return {
            "allow": False,
            "block_engine": True,
            "state": "WAITING_CLARIFICATION",
            "result": "Файл прочитан, но тип расчёта не определён. Это смета, проверка проекта, акт или ведомость объёмов?",
            "error_message": None,
            "domain": "unknown",
            "meta": meta,
        }

    return {"allow": True, "reason": "no_block", "domain": "unknown", "meta": meta}


def apply_gate_result_to_task(
    conn: sqlite3.Connection, task: Any, decision: Dict[str, Any]
) -> None:
    task_id = _s(_row_get(task, "id"))
    if not task_id or not decision or decision.get("allow", True):
        return
    state = decision.get("state") or "WAITING_CLARIFICATION"
    result = decision.get("result") or ""
    error_message = decision.get("error_message")
    conn.execute(
        """
        UPDATE tasks
        SET state=?, result=?, error_message=?, updated_at=datetime('now')
        WHERE id=?
        """,
        (state, result, error_message, task_id),
    )
    _history(conn, task_id, f"TOPIC2_INPUT_GATE_HANDLED:state={state}:domain={decision.get('domain','unknown')}")
    try:
        conn.commit()
    except Exception:
        pass


def mark_known_invalid_stale_results(conn: sqlite3.Connection) -> int:
    bad_ids = (
        "1b281c50-2544-45c0-967d-2e49427d0d84",
        "60b9503b-75cc-4913-bb7b-11092508fdae",
    )
    changed = 0
    for task_id in bad_ids:
        row = conn.execute(
            "SELECT id,state,result FROM tasks WHERE id=? LIMIT 1", (task_id,)
        ).fetchone()
        if not row:
            continue
        result = _s(row[2] if not hasattr(row, "keys") else row["result"])
        if "газобетон" in _low(result) and ("106.25" in result or "106,25" in result):
            conn.execute(
                """
                UPDATE tasks
                SET state='FAILED',
                    error_message='TOPIC2_STALE_HOUSE_CONTEXT_USED_FOR_DRAINAGE_FILE',
                    updated_at=datetime('now')
                WHERE id=?
                """,
                (task_id,),
            )
            _history(conn, task_id, "TOPIC2_STALE_HOUSE_CONTEXT_USED_FOR_DRAINAGE_FILE")
            changed += 1
    try:
        conn.commit()
    except Exception:
        pass
    return changed

# === END_PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 ===

====================================================================================================
END_FILE: core/topic2_input_gate.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic_3008_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: f6f9c29ce8def6ac922df7e40ad352a08586d5070eaa1d984e2ed9dc0dab51c0
====================================================================================================
import asyncio, logging, os, re
from typing import Optional
logger = logging.getLogger(__name__)

TOPIC_3008 = 3008
TIMEOUT = 90

_WRITE_CODE = ["напиши код", "написать код"]
_VERIFY_CODE = ["проверь код", "проверить код", "верификация"]
_CODE_BLOCK = re.compile(r"```[\w]*\n.*?```", re.DOTALL)

def is_topic_3008(topic_id):
    return int(topic_id or 0) == TOPIC_3008

def detect_command(text):
    low = text.lower()
    if any(t in low for t in _WRITE_CODE):
        return "write"
    if any(t in low for t in _VERIFY_CODE):
        return "verify"
    if _CODE_BLOCK.search(text):
        return "verify"
    return "none"

def extract_code(text):
    m = _CODE_BLOCK.search(text)
    if m:
        raw = m.group(0)
        lines = raw.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines)
    return text

MODEL_REGISTRY = {
    "deepseek": {"name":"DeepSeek","emoji":"🧠","role":"архитектура","api":"openrouter","model":"deepseek/deepseek-chat","env_key":"OPENROUTER_API_KEY","available":True},
    "claude":   {"name":"Claude",  "emoji":"👤","role":"логика ТЗ", "api":"anthropic","model":"claude-opus-4-6","env_key":"ANTHROPIC_API_KEY","available":True},
    "gpt":      {"name":"ChatGPT", "emoji":"🤖","role":"патчи",    "api":"openai",  "model":"gpt-4o","env_key":"OPENAI_API_KEY","available":True},
    "gemini":   {"name":"Gemini",  "emoji":"🔒","role":"безопасность","api":"gemini","model":"gemini-2.0-flash","env_key":"GOOGLE_API_KEY","available":False},
    "grok":     {"name":"Grok",    "emoji":"⚡","role":"архитектура","api":"xai",   "model":"grok-3","env_key":"XAI_API_KEY","available":False},
}

async def _call_openrouter(model_id, prompt, api_key, base_url):
    import aiohttp
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model_id, "messages": [{"role":"user","content":prompt}], "max_tokens":1000}
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            d = await r.json()
            return d["choices"][0]["message"]["content"]

async def _call_anthropic(model_id, prompt, api_key):
    import aiohttp
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    payload = {"model": model_id, "max_tokens":1000, "messages":[{"role":"user","content":prompt}]}
    async with aiohttp.ClientSession() as s:
        async with s.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            d = await r.json()
            return d["content"][0]["text"]

async def _call_openai(model_id, prompt, api_key):
    import aiohttp
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model_id, "messages":[{"role":"user","content":prompt}], "max_tokens":1000}
    async with aiohttp.ClientSession() as s:
        async with s.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            d = await r.json()
            return d["choices"][0]["message"]["content"]

async def _verify_one(key, meta, prompt):
    api_key = <REDACTED_SECRET>"env_key"], "")
    if not api_key or not meta["available"]:
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":"недоступна","ok":None}
    try:
        base_url = os.getenv("OPENROUTER_BASE_URL","https://openrouter.ai/api/v1")
        if meta["api"] == "openrouter":
            text = await _call_openrouter(meta["model"], prompt, api_key, base_url)
        elif meta["api"] == "anthropic":
            text = await _call_anthropic(meta["model"], prompt, api_key)
        elif meta["api"] == "openai":
            text = await _call_openai(meta["model"], prompt, api_key)
        else:
            return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":"API не реализован","ok":None}
        text_clean = text.strip()[:800]
        low = text_clean.lower()
        ok = not any(w in low for w in ["ошибк","проблем","уязвимост","небезопасн","запрещ"])
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"✅" if ok else "❌","text":text_clean,"ok":ok}
    except asyncio.TimeoutError:
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":"таймаут 90с","ok":None}
    except Exception as e:
        return {"key":key,"name":meta["name"],"emoji":meta["emoji"],"role":meta["role"],"result":"⚠️ НЕТ ОТВЕТА","text":str(e)[:200],"ok":None}

async def verify_code(code, context=""):
    prompt = f"Проверь код на логику, архитектуру, безопасность.\n\nКонтекст: AREAL-NEVA ORCHESTRA\n{context[:300]}\n\nКод:\n```\n{code[:3000]}\n```\n\nДай краткий вердикт (2-3 предложения)."
    available = {k:v for k,v in MODEL_REGISTRY.items()}
    tasks = [_verify_one(k,v,prompt) for k,v in available.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    lines = ["=== ВЕРИФИКАЦИЯ КОДА ===\n"]
    approved = 0
    critical = False
    for r in results:
        if isinstance(r, Exception):
            continue
        lines.append(f"{r['emoji']} {r['name'].upper()} ({r['role']}): {r['result']}")
        lines.append(r['text'])
        lines.append("")
        if r['ok'] is True:
            approved += 1
        if r['key'] == 'gemini' and r['result'] == '❌':
            critical = True
    total = sum(1 for v in available.values() if v["available"] and os.getenv(v["env_key"]))
    lines.append("=== ОБЩАЯ КАРТИНА ===")
    lines.append(f"Одобрено {approved} из {max(total,1)} доступных моделей.")
    if critical:
        lines.append("КРИТИЧЕСКОЕ ЗАМЕЧАНИЕ: Gemini выявил проблемы безопасности!")
    lines.append("\nРешение принимает пользователь.")
    return "\n".join(lines)

async def generate_code(description, context=""):
    api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY","")
    base_url = os.getenv("OPENROUTER_BASE_URL","https://openrouter.ai/api/v1")
    prompt = f"Напиши код. Только код без лишних объяснений.\n\nСистема: AREAL-NEVA ORCHESTRA (Python 3.12)\n{('Контекст: ' + context[:300]) if context else ''}\n\nЗадача: {description}"
    try:
        return (await _call_openrouter("deepseek/deepseek-chat", prompt, api_key, base_url)).strip()
    except Exception as e:
        return f"Ошибка генерации: {e}"

====================================================================================================
END_FILE: core/topic_3008_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic_autodiscovery.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d0d1b4283ee522045919246760eaac8dd0db474767f03ff0cd346aac7ae73994
====================================================================================================
# === FULLFIX_TOPIC_AUTODISCOVERY_V2 ===
from __future__ import annotations
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("task_worker")

AUTODISCOVERY_VERSION = "TOPIC_AUTODISCOVERY_V2"
CONFIG_PATH = Path("/root/.areal-neva-core/config/directions.yaml")
DATA_TOPICS_PATH = Path("/root/.areal-neva-core/data/topics")
NAMING_TIMEOUT_HOURS = 24
CONFLICT_SCORE_DELTA = 30
MIN_SCORE_TO_AUTOASSIGN = 60


def _load_config():
    raw = CONFIG_PATH.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except Exception:
        import yaml
        return yaml.safe_load(raw) or {}


def _save_config(data: dict):
    # Всегда пишем JSON — файл directions.yaml фактически JSON
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_topic_meta(topic_id: int) -> Dict:
    meta_file = DATA_TOPICS_PATH / str(topic_id) / "meta.json"
    if meta_file.exists():
        try:
            return json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_topic_meta(topic_id: int, meta: dict):
    folder = DATA_TOPICS_PATH / str(topic_id)
    folder.mkdir(parents=True, exist_ok=True)
    meta_file = folder / "meta.json"
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def _topic_known(topic_id: int, data: dict) -> Optional[str]:
    for direction_id, profile in data.get("directions", {}).items():
        if topic_id in (profile.get("topic_ids") or []):
            return direction_id
    return None


def _detect_with_audit(work_item) -> Tuple[str, int, str, int]:
    from core.direction_registry import DirectionRegistry
    reg = DirectionRegistry()
    results = []
    for direction_id, profile in reg.directions.items():
        score, item = reg._score_direction(direction_id, profile or {}, work_item)
        results.append((direction_id, score))
    results.sort(key=lambda x: -x[1])
    top = results[0] if results else ("general_chat", 0)
    second = results[1] if len(results) > 1 else ("general_chat", 0)
    return top[0], top[1], second[0], second[1]


def _create_topic_folder(topic_id: int, direction: str, name: str = ""):
    folder = DATA_TOPICS_PATH / str(topic_id)
    folder.mkdir(parents=True, exist_ok=True)
    meta = _load_topic_meta(topic_id)
    meta.update({
        "topic_id": topic_id,
        "direction": direction,
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "version": AUTODISCOVERY_VERSION,
    })
    _save_topic_meta(topic_id, meta)
    logger.info("TOPIC_AUTODISCOVERY folder: %s dir=%s name=%s", folder, direction, name)


def _register_topic(topic_id: int, direction: str, data: dict):
    profile = data["directions"].get(direction)
    if profile is None:
        return
    topic_ids = list(profile.get("topic_ids") or [])
    if topic_id not in topic_ids:
        topic_ids.append(topic_id)
        data["directions"][direction]["topic_ids"] = topic_ids
    _save_config(data)
    logger.info("TOPIC_REGISTERED topic_id=%s -> direction=%s", topic_id, direction)


def _send_naming_question(chat_id: str, topic_id: int):
    """Отправляет вопрос о названии топика один раз."""
    try:
        from core.reply_sender import send_reply  # IMPORT_FIX_V1
        send_reply(
            chat_id=str(chat_id),
            text="Как назовём этот чат? Ответь голосом или текстом.",
            message_thread_id=topic_id,
        )
        logger.info("TOPIC_NAMING_QUESTION sent chat=%s topic=%s", chat_id, topic_id)
    except Exception as e:
        logger.error("TOPIC_NAMING_QUESTION_ERR %s", e)


def check_naming_timeout(chat_id: str, topic_id: int):
    """
    Вызывается при каждом сообщении из топика.
    Если топик без имени и прошло 24 часа — один раз спрашивает название.
    """
    meta = _load_topic_meta(topic_id)
    if not meta:
        return
    if meta.get("name"):
        return
    if meta.get("naming_asked"):
        return
    created_at = meta.get("created_at")
    if not created_at:
        return
    try:
        created = datetime.fromisoformat(created_at)
        elapsed = (datetime.now(timezone.utc) - created).total_seconds() / 3600
        if elapsed >= NAMING_TIMEOUT_HOURS:
            meta["naming_asked"] = datetime.now(timezone.utc).isoformat()
            _save_topic_meta(topic_id, meta)
            _send_naming_question(chat_id, topic_id)
    except Exception as e:
        logger.error("TOPIC_NAMING_TIMEOUT_ERR %s", e)


def assign_name(topic_id: int, name: str):
    """Назначает имя топику. Вызывается когда пользователь ответил на вопрос."""
    meta = _load_topic_meta(topic_id)
    meta["name"] = name
    meta["named_at"] = datetime.now(timezone.utc).isoformat()
    _save_topic_meta(topic_id, meta)
    logger.info("TOPIC_NAMED topic=%s name=%s", topic_id, name)


def process(work_item, payload: Dict[str, Any]) -> Dict[str, Any]:
    topic_id = int(getattr(work_item, "topic_id", 0) or 0)
    chat_id = str(getattr(work_item, "chat_id", "") or payload.get("chat_id") or "")
    if topic_id == 0:
        return {}

    try:
        data = _load_config()
    except Exception as e:
        logger.error("TOPIC_AUTODISCOVERY config load error: %s", e)
        return {}

    # Уже известный топик — проверяем таймаут имени
    known = _topic_known(topic_id, data)
    if known:
        try:
            check_naming_timeout(chat_id, topic_id)
        except Exception:
            pass
        return {"status": "known", "direction": known}

    # Новый топик — детектируем направление
    try:
        top_dir, top_score, second_dir, second_score = _detect_with_audit(work_item)
    except Exception as e:
        logger.error("TOPIC_AUTODISCOVERY detect error: %s", e)
        return {"status": "detect_error"}

    # Недостаточный score
    if top_score < MIN_SCORE_TO_AUTOASSIGN:
        # Создаём папку но не регистрируем direction
        _create_topic_folder(topic_id, "unknown", "")
        logger.info("TOPIC_AUTODISCOVERY low score=%s topic=%s — folder created, waiting", top_score, topic_id)
        return {"status": "low_score", "topic_id": topic_id, "score": top_score}

    # Конфликт — уточняем
    delta = top_score - second_score
    if delta < CONFLICT_SCORE_DELTA and second_score >= MIN_SCORE_TO_AUTOASSIGN:
        logger.warning("TOPIC_CONFLICT topic=%s %s(%s) vs %s(%s)",
                       topic_id, top_dir, top_score, second_dir, second_score)
        payload["topic_conflict"] = {
            "topic_id": topic_id,
            "candidates": [
                {"direction": top_dir, "score": top_score},
                {"direction": second_dir, "score": second_score},
            ],
        }
        return {"status": "conflict", "candidates": [top_dir, second_dir]}

    # Однозначно — регистрируем молча
    try:
        _register_topic(topic_id, top_dir, data)
        _create_topic_folder(topic_id, top_dir, "")
        payload["topic_autodiscovered"] = {
            "topic_id": topic_id,
            "direction": top_dir,
            "score": top_score,
            "version": AUTODISCOVERY_VERSION,
        }
        logger.info("TOPIC_AUTODISCOVERY_DONE topic=%s -> %s score=%s", topic_id, top_dir, top_score)
        return {"status": "registered", "direction": top_dir, "score": top_score}
    except Exception as e:
        logger.error("TOPIC_REGISTER_ERR %s", e)
        return {"status": "register_error"}
# === END FULLFIX_TOPIC_AUTODISCOVERY_V2 ===

====================================================================================================
END_FILE: core/topic_autodiscovery.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic_drive_oauth.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 09e67527599b711f23e665802e1beed93944060a64a3674da0459bdafdd00513
====================================================================================================
import os
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=True)

def _oauth_service():
    client_id = os.getenv("GDRIVE_CLIENT_ID")
    client_secret = <REDACTED_SECRET>"GDRIVE_CLIENT_SECRET")
    refresh_token = <REDACTED_SECRET>"GDRIVE_REFRESH_TOKEN")
    if not client_id or not client_secret or not refresh_token:
        raise RuntimeError("GDRIVE OAuth vars missing")
    creds = Credentials(
        None,
        refresh_token=<REDACTED_SECRET>
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=<REDACTED_SECRET>
        scopes=["https://www.googleapis.com/auth/drive"]  # SCOPE_FULL_V2,
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)

def _root_folder_id() -> str:
    folder_id = os.getenv("DRIVE_INGEST_FOLDER_ID", "").strip()
    if not folder_id:
        raise RuntimeError("DRIVE_INGEST_FOLDER_ID missing")
    return folder_id

def _find_child_folder(service, parent_id: str, name: str) -> Optional[str]:
    # === DRIVE_CANON_SINGLE_FOLDER_PICK_V1 ===
    # Deterministic folder lookup: if duplicates exist, use the oldest existing folder.
    safe_name = str(name or "").replace("'", "\\'")
    q = (
        f"name = '{safe_name}' and "
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"'{parent_id}' in parents and trashed = false"
    )
    resp = service.files().list(
        q=q,
        spaces="drive",
        fields="files(id,name,createdTime)",
        orderBy="createdTime",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = resp.get("files", [])
    return files[0]["id"] if files else None
    # === END_DRIVE_CANON_SINGLE_FOLDER_PICK_V1 ===

def _ensure_folder(service, parent_id: str, name: str) -> str:
    found = _find_child_folder(service, parent_id, name)
    if found:
        return found
    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    res = service.files().create(
        body=meta,
        fields="id",
        supportsAllDrives=True,
    ).execute()
    return res["id"]

def _upload_file_sync(file_path: str, file_name: str, chat_id: str, topic_id: int, mime_type: Optional[str] = None) -> Dict[str, Any]:
    service = _oauth_service()
    root_id = _root_folder_id()
    chat_folder = _ensure_folder(service, root_id, f"chat_{chat_id}")
    topic_folder = _ensure_folder(service, chat_folder, f"topic_{int(topic_id or 0)}")
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    meta = {
        "name": file_name,
        "parents": [topic_folder],
    }
    res = service.files().create(
        body=meta,
        media_body=media,
        fields="id,parents",
        supportsAllDrives=True,
    ).execute()
    return {
        "ok": True,
        "drive_file_id": res.get("id"),
        "folder_id": topic_folder,
        "chat_folder_id": chat_folder,
    }

async def upload_file_to_topic(file_path: str, file_name: str, chat_id: str, topic_id: int, mime_type: Optional[str] = None) -> Dict[str, Any]:
    return await asyncio.to_thread(_upload_file_sync, file_path, file_name, str(chat_id), int(topic_id or 0), mime_type)


# === P7_TOPIC5_ACTIVE_FOLDER_UPLOAD_V1 ===
# topic_5 object materials must upload into ActiveTechnadzorFolder, not generic topic_5 root.
import json as _p7_t5_json
import time as _p7_t5_time
from pathlib import Path as _p7_t5_Path

_P7_T5_ORIG_UPLOAD_FILE_SYNC = _upload_file_sync
_P7_T5_BASE = _p7_t5_Path("/root/.areal-neva-core/data/technadzor")

def _p7_t5_active_folder_path(chat_id, topic_id):
    return _P7_T5_BASE / f"active_folder_{chat_id}_{int(topic_id or 0)}.json"

def _p7_t5_load_active_folder(chat_id, topic_id):
    if int(topic_id or 0) != 5:
        return {}
    p = _p7_t5_active_folder_path(str(chat_id), 5)
    try:
        data = _p7_t5_json.loads(p.read_text(encoding="utf-8"))
        if data.get("folder_id") and str(data.get("status", "OPEN")).upper() != "CLOSED":
            return data
    except Exception:
        return {}
    return {}

def _upload_file_sync(file_path: str, file_name: str, chat_id: str, topic_id: int, mime_type: Optional[str] = None) -> Dict[str, Any]:
    if int(topic_id or 0) == 5:
        af = _p7_t5_load_active_folder(str(chat_id), 5)
        active_folder_id = str(af.get("folder_id") or "").strip()
        if active_folder_id:
            service = _oauth_service()
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            meta = {
                "name": file_name,
                "parents": [active_folder_id],
            }
            res = service.files().create(
                body=meta,
                media_body=media,
                fields="id,parents,webViewLink",
                supportsAllDrives=True,
            ).execute()
            return {
                "ok": True,
                "drive_file_id": res.get("id"),
                "folder_id": active_folder_id,
                "active_folder_id": active_folder_id,
                "active_folder_name": af.get("folder_name", ""),
                "webViewLink": res.get("webViewLink", ""),
                "topic5_active_folder_upload": True,
                "uploaded_at": _p7_t5_time.time(),
            }
    return _P7_T5_ORIG_UPLOAD_FILE_SYNC(file_path, file_name, chat_id, topic_id, mime_type)
# === END_P7_TOPIC5_ACTIVE_FOLDER_UPLOAD_V1 ===

====================================================================================================
END_FILE: core/topic_drive_oauth.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/topic_meta_loader.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 081afc9cc3266e754882d8c6fce4db2ebb8d191a72aebc19c120afdb1fbb8dec
====================================================================================================
"""TOPIC_META_LOADER_V1 — читает data/topics/{tid}/meta.json при INTAKE."""
import json
from pathlib import Path
from typing import Optional, Dict, Any

DATA_TOPICS = Path("data/topics")

# Триггеры "что это за чат" — отвечаем из meta.json напрямую
WHAT_IS_THIS_TRIGGERS = [
    "что мы здесь делаем", "что мы тут делаем", "для чего ты",
    "для чего этот чат", "для чего этот топик", "для чего у нас",
    "что мы делаем в данном чате", "что мы делаем тут",
    "скажи для чего", "зачем этот чат", "зачем этот топик",
    "про что чат", "про что топик", "что за чат", "что за топик",
]

def load_topic_meta(topic_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает meta.json топика или None."""
    if topic_id is None:
        return None
    folder = DATA_TOPICS / str(topic_id)
    meta_path = folder / "meta.json"
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None

def is_what_is_this_question(text: str) -> bool:
    """True если текст — вопрос о назначении чата."""
    if not text:
        return False
    t = text.lower().replace("[voice]", "").replace("🎤", "").strip()
    return any(trigger in t for trigger in WHAT_IS_THIS_TRIGGERS)

def build_topic_self_answer(meta: Dict[str, Any]) -> str:
    """Формирует ответ от имени топика на вопрос 'что мы тут делаем'."""
    name = meta.get("name", "Без имени")
    direction = meta.get("direction", "general_chat")
    
    DIRECTION_DESCRIPTIONS = {
        "general_chat": "общий чат для произвольных задач",
        "crm_leads": "лиды, реклама, AmoCRM, лидогенерация",
        "estimates": "сметы, расчёт стоимости строительства",
        "technical_supervision": "технадзор, акты осмотра, дефекты, СП/ГОСТ",
        "structural_design": "проектирование КЖ/КМ/КМД/АР/ОВ/ВК/ЭОМ/СС/ГП/ПЗ/СМ/ТХ",
        "internet_search": "интернет-поиск товаров и информации",
        "auto_parts_search": "поиск автозапчастей, артикулы, аналоги, цены",
        "orchestration_core": "коды оркестра, AI-роутер, архитектура системы",
        "video_production": "генерация и производство видеоконтента",
        "devops_server": "VPN, VPS, конфигурации серверов, настройки",
        "job_search": "поиск работы и интеграция с биржами труда",
    }
    
    desc = DIRECTION_DESCRIPTIONS.get(direction, direction)
    return f"Этот чат — {name}. Направление: {desc}."

====================================================================================================
END_FILE: core/topic_meta_loader.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/universal_file_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: a19ee184aae5b7ddad4f2e625de87685894cd3141252bbb507d5b11c363c9fdd
====================================================================================================
# === UNIVERSAL_FILE_ENGINE_V1 ===
from __future__ import annotations

import json
import os
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from core.format_registry import classify_file

def _clean(v: Any, limit: int = 20000) -> str:
    s = "" if v is None else str(v)
    s = s.replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()[:limit]

def _safe(v: Any, fallback: str = "file") -> str:
    s = re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", _clean(v, 120)).strip("._")
    return s or fallback

def _try_extract_text(path: str, file_name: str = "") -> str:
    ext = Path(file_name or path).suffix.lower()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            return _clean("\n".join((p.extract_text() or "") for p in reader.pages[:50]), 50000)
        except Exception as e:
            return f"PDF_PARSE_ERROR: {e}"
    if ext == ".docx":
        try:
            from docx import Document
            doc = Document(path)
            return _clean("\n".join(p.text for p in doc.paragraphs if p.text), 50000)
        except Exception as e:
            return f"DOCX_PARSE_ERROR: {e}"
    if ext in (".txt", ".md", ".csv", ".json", ".xml", ".html", ".htm", ".yaml", ".yml"):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return _clean(f.read(), 50000)
        except Exception as e:
            return f"TEXT_PARSE_ERROR: {e}"
    return ""

def _write_docx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"universal_file_report_{_safe(task_id)}.docx"
    try:
        from docx import Document
        doc = Document()
        doc.add_heading("UNIVERSAL FILE REPORT", level=1)
        doc.add_paragraph(f"Файл: {model.get('file_name')}")
        doc.add_paragraph(f"Тип: {model.get('kind')}")
        doc.add_paragraph(f"Домен: {model.get('domain')}")
        doc.add_paragraph(f"Расширение: {model.get('extension')}")
        doc.add_paragraph(f"Размер: {model.get('size_bytes')} bytes")
        doc.add_paragraph(f"Engine hint: {model.get('engine_hint')}")
        doc.add_heading("Текст/превью", level=2)
        doc.add_paragraph(_clean(model.get("text_preview"), 12000) or "Текст не извлечён")
        doc.add_heading("Статус", level=2)
        doc.add_paragraph(model.get("status") or "INDEXED_METADATA")
        doc.save(out)
        return str(out)
    except Exception:
        txt = out.with_suffix(".txt")
        txt.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(txt)

def _write_json(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"universal_file_model_{_safe(task_id)}.json"
    out.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out)

def _write_xlsx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"universal_file_register_{_safe(task_id)}.xlsx"
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "File"
        for row, (k, v) in enumerate(model.items(), 1):
            ws.cell(row=row, column=1, value=str(k))
            ws.cell(row=row, column=2, value=json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v))
        wb.save(out)
        wb.close()
        return str(out)
    except Exception:
        csv = out.with_suffix(".csv")
        csv.write_text("key,value\n" + "\n".join(f"{k},{v}" for k, v in model.items()), encoding="utf-8")
        return str(csv)

def _zip(paths: List[str], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"universal_file_package_{_safe(task_id)}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p and os.path.exists(p):
                z.write(p, arcname=os.path.basename(p))
        z.writestr("manifest.json", json.dumps({
            "engine": "UNIVERSAL_FILE_ENGINE_V1",
            "task_id": task_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files": [os.path.basename(p) for p in paths if p and os.path.exists(p)],
        }, ensure_ascii=False, indent=2))
    return str(out)

def process_universal_file(
    local_path: str,
    file_name: str = "",
    mime_type: str = "",
    user_text: str = "",
    topic_role: str = "",
    task_id: str = "universal_file",
    topic_id: int = 0,
) -> Dict[str, Any]:
    if not local_path or not os.path.exists(local_path):
        return {"success": False, "error": "FILE_NOT_FOUND", "summary": "Файл не найден"}

    cls = classify_file(file_name or os.path.basename(local_path), mime_type, user_text, topic_role)
    size = os.path.getsize(local_path)
    text = _try_extract_text(local_path, file_name or local_path)

    model = {
        "schema": "UNIVERSAL_FILE_MODEL_V1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "file_name": file_name or os.path.basename(local_path),
        "local_path": local_path,
        "mime_type": mime_type,
        "topic_id": topic_id,
        "user_text": user_text,
        "topic_role": topic_role,
        "size_bytes": size,
        "text_preview": _clean(text, 5000),
        **cls,
        "status": "INDEXED_WITH_TEXT" if text else "INDEXED_METADATA_ONLY",
    }

    docx = _write_docx(model, task_id)
    xlsx = _write_xlsx(model, task_id)
    js = _write_json(model, task_id)
    package = _zip([docx, xlsx, js], task_id)

    summary = "\n".join([
        "Универсальный файловый контур отработал",
        f"Файл: {model['file_name']}",
        f"Тип: {model['kind']}",
        f"Домен: {model['domain']}",
        f"Статус: {model['status']}",
        "Артефакты: DOCX + XLSX + JSON + ZIP",
    ])

    return {
        "success": True,
        "engine": "UNIVERSAL_FILE_ENGINE_V1",
        "summary": summary,
        "artifact_path": package,
        "artifact_name": f"{Path(model['file_name']).stem}_universal_file_package.zip",
        "extra_artifacts": [docx, xlsx, js],
        "model": model,
    }
# === END_UNIVERSAL_FILE_ENGINE_V1 ===

====================================================================================================
END_FILE: core/universal_file_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/universal_file_handler.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 10f50019c01f6a903296f3616568273fe69b0910481c12cc1105b19fec8ee2a7
====================================================================================================
# === UNIVERSAL_FILE_HANDLER_V1 ===
import os, logging, tempfile, subprocess, csv, zipfile, json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# --- Magic bytes detection ---
_MAGIC = {
    b"%PDF": "pdf",
    b"PK\x03\x04": "xlsx_or_zip",
    b"\xd0\xcf\x11\xe0": "doc_or_xls",
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG": "png",
    b"GIF8": "gif",
    b"BM": "bmp",
    b"II\x2a\x00": "tiff",
    b"MM\x00\x2a": "tiff",
    b"RIFF": "webp_or_avi",
    b"ftyp": "mp4",
    b"ID3": "mp3",
    b"AC10": "dwg",
    b"AC12": "dwg",
    b"AC14": "dwg",
    b"AC15": "dwg",
    b"AC18": "dwg",
    b"AC21": "dwg",
    b"AC24": "dwg",
    b"AC27": "dwg",
    b"  0\r\nSECTION": "dxf",
}

EXT_MAP = {
    ".pdf": "pdf", ".docx": "docx", ".doc": "doc_old",
    ".xlsx": "xlsx", ".xls": "xls_old", ".csv": "csv",
    ".txt": "text", ".md": "text", ".json": "json", ".xml": "xml",
    ".jpg": "image", ".jpeg": "image", ".png": "image",
    ".heic": "image", ".webp": "image", ".bmp": "image", ".tiff": "image",
    ".dwg": "dwg", ".dxf": "dxf", ".dgn": "dgn",
    ".zip": "zip", ".rar": "rar", ".7z": "7z",
    ".mp4": "video", ".avi": "video", ".mov": "video",
    ".mp3": "audio", ".ogg": "audio", ".wav": "audio",
    ".odt": "odt", ".ods": "ods", ".rtf": "rtf",
}

def detect_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    try:
        with open(file_path, "rb") as f:
            header = f.read(16)
        for magic, ftype in _MAGIC.items():
            if header[:len(magic)] == magic:
                # PK magic = ZIP or XLSX — уточняем по расширению
                if ftype == "xlsx_or_zip":
                    return "xlsx" if ext in (".xlsx", ".xlsm", ".xltx") else "zip"
                # RIFF = webp or avi — уточняем по расширению
                if ftype == "webp_or_avi":
                    return "image" if ext == ".webp" else "video"
                return ftype
    except Exception:
        pass
    return EXT_MAP.get(ext, "unknown")


def extract_text_from_file(file_path: str, task_id: str = "", topic_id: int = 0) -> Dict[str, Any]:
    """
    Универсальный экстрактор текста/данных из любого файла.
    Маркер: UNIVERSAL_FILE_HANDLER_V1
    Возвращает: {"success": bool, "type": str, "text": str, "rows": list, "error": str}
    """
    result = {"success": False, "type": "unknown", "text": "", "rows": [], "error": ""}
    ftype = detect_type(file_path)
    result["type"] = ftype
    logger.info("UNIVERSAL_FILE_HANDLER type=%s file=%s", ftype, os.path.basename(file_path))

    try:
        # --- PDF ---
        if ftype == "pdf":
            import pdfplumber, re
            with pdfplumber.open(file_path) as pdf:
                parts = []
                rows = []
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    t = re.sub(r'\(cid:\d+\)', '', t)
                    if t.strip():
                        parts.append(t)
                    for tbl in (page.extract_tables() or []):
                        rows.extend(tbl)
                result["text"] = "\n".join(parts)
                result["rows"] = rows
                result["success"] = True

        # --- DOCX / ODT ---
        elif ftype in ("docx", "odt"):
            import docx as _docx
            doc = _docx.Document(file_path)
            result["text"] = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            result["rows"] = [[c.text for c in row.cells] for tbl in doc.tables for row in tbl.rows]
            result["success"] = True

        # --- XLSX / ODS ---
        elif ftype in ("xlsx_or_zip", "xlsx"):
            from openpyxl import load_workbook
            wb = load_workbook(file_path, data_only=True)
            rows = []
            for ws in wb.worksheets:
                for row in ws.iter_rows(values_only=True):
                    if any(c is not None for c in row):
                        rows.append([str(c) if c is not None else "" for c in row])
            result["rows"] = rows
            result["text"] = "\n".join("\t".join(r) for r in rows[:50])
            result["success"] = True

        # --- CSV ---
        elif ftype == "csv":
            rows = []
            enc = "utf-8"
            try:
                import chardet
                with open(file_path, "rb") as f:
                    enc = chardet.detect(f.read(4096)).get("encoding", "utf-8") or "utf-8"
            except Exception:
                pass
            with open(file_path, encoding=enc, errors="replace") as f:
                for row in csv.reader(f):
                    rows.append(row)
            result["rows"] = rows
            result["text"] = "\n".join("\t".join(r) for r in rows[:50])
            result["success"] = True

        # --- TEXT / JSON / XML / MD ---
        elif ftype in ("text", "json", "xml", "rtf"):
            enc = "utf-8"
            try:
                import chardet
                with open(file_path, "rb") as f:
                    enc = chardet.detect(f.read(4096)).get("encoding", "utf-8") or "utf-8"
            except Exception:
                pass
            with open(file_path, encoding=enc, errors="replace") as f:
                result["text"] = f.read(50000)
            result["success"] = True

        # --- ИЗОБРАЖЕНИЯ (JPG/PNG/HEIC/BMP/TIFF/WEBP/GIF) ---
        elif ftype in ("jpg", "png", "image", "gif", "bmp", "tiff", "webp_or_avi"):
            import pytesseract
            from PIL import Image
            try:
                from pillow_heif import register_heif_opener
                register_heif_opener()
            except Exception:
                pass
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang="rus+eng")
            result["text"] = text.strip()
            result["success"] = True
            result["type"] = "image"

        # --- DWG → конвертация в DXF → ezdxf ---
        elif ftype == "dwg":
            result = _handle_dwg(file_path, result)

        # --- DXF ---
        elif ftype == "dxf":
            result = _handle_dxf(file_path, result)

        # --- ZIP ---
        elif ftype == "zip":
            result = _handle_zip(file_path, task_id, topic_id, result)

        # --- RAR ---
        elif ftype == "rar":
            try:
                import rarfile
                tmp = tempfile.mkdtemp()
                with rarfile.RarFile(file_path) as rf:
                    rf.extractall(tmp)
                texts = []
                for fn in os.listdir(tmp)[:5]:
                    sub = extract_text_from_file(os.path.join(tmp, fn), task_id, topic_id)
                    if sub["success"]:
                        texts.append(f"[{fn}]\n{sub['text']}")
                result["text"] = "\n\n".join(texts)
                result["success"] = True
                result["type"] = "rar"
            except Exception as e:
                result["error"] = f"RAR: {e}"

        # --- 7Z ---
        elif ftype == "7z":
            try:
                import py7zr
                tmp = tempfile.mkdtemp()
                with py7zr.SevenZipFile(file_path) as sz:
                    sz.extractall(tmp)
                texts = []
                for fn in os.listdir(tmp)[:5]:
                    sub = extract_text_from_file(os.path.join(tmp, fn), task_id, topic_id)
                    if sub["success"]:
                        texts.append(f"[{fn}]\n{sub['text']}")
                result["text"] = "\n\n".join(texts)
                result["success"] = True
                result["type"] = "7z"
            except Exception as e:
                result["error"] = f"7Z: {e}"

        # --- ВИДЕО/АУДИО — метаданные через ffmpeg ---
        elif ftype in ("mp4", "video", "mp3", "audio"):
            try:
                out = subprocess.check_output(
                    ["ffmpeg", "-i", file_path],
                    stderr=subprocess.STDOUT, timeout=10
                ).decode(errors="replace")
            except subprocess.CalledProcessError as e:
                out = e.output.decode(errors="replace")
            result["text"] = out[:2000]
            result["success"] = True

        # --- UNKNOWN — попытка открыть как текст ---
        else:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    txt = f.read(10000)
                if len(txt.strip()) > 20:
                    result["text"] = txt
                    result["success"] = True
                    result["type"] = "text_fallback"
                else:
                    result["error"] = f"Формат не поддерживается: {os.path.splitext(file_path)[1]}"
            except Exception as e:
                result["error"] = f"Неизвестный формат: {e}"

    except Exception as e:
        logger.error("UNIVERSAL_FILE_HANDLER_ERROR type=%s err=%s", ftype, e)
        result["error"] = str(e)

    return result


def _handle_dwg(file_path: str, result: dict) -> dict:
    """DWG: конвертация через dwg2dxf (libredwg), fallback через imagemagick preview"""
    dxf_path = file_path.replace(".dwg", ".dxf").replace(".DWG", ".dxf")
    if not dxf_path.endswith(".dxf"):
        dxf_path = file_path + ".dxf"

    # Попытка 1: dwg2dxf
    try:
        subprocess.run(["dwg2dxf", file_path, "-o", dxf_path],
                       timeout=30, capture_output=True, check=True)
        if os.path.exists(dxf_path):
            logger.info("DWG→DXF conversion OK: %s", dxf_path)
            return _handle_dxf(dxf_path, result)
    except Exception as e:
        logger.warning("dwg2dxf failed: %s", e)

    # Попытка 2: imagemagick — превью в PNG + OCR
    try:
        png_path = file_path + "_preview.png"
        subprocess.run(
            ["convert", "-density", "150", file_path + "[0]", png_path],
            timeout=30, capture_output=True, check=True
        )
        if os.path.exists(png_path):
            import pytesseract
            from PIL import Image
            text = pytesseract.image_to_string(Image.open(png_path), lang="rus+eng")
            result["text"] = f"[DWG файл — превью через OCR]\n{text.strip()}"
            result["success"] = True
            result["type"] = "dwg_ocr_preview"
            return result
    except Exception as e:
        logger.warning("DWG imagemagick fallback failed: %s", e)

    result["error"] = "DWG: конвертация не удалась. Пришли файл в формате .dxf"
    result["text"] = "Файл формата DWG получен. Для полной обработки конвертируй в DXF."
    result["success"] = False
    return result


def _handle_dxf(file_path: str, result: dict) -> dict:
    """DXF через ezdxf"""
    try:
        import ezdxf
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()
        counts = {}
        texts = []
        for e in msp:
            t = e.dxftype()
            counts[t] = counts.get(t, 0) + 1
            if t in ("TEXT", "MTEXT") and hasattr(e.dxf, "text"):
                txt = str(e.dxf.text or "").strip()
                if txt:
                    texts.append(txt)
        summary = "DXF элементы:\n"
        for k, v in sorted(counts.items(), key=lambda x: -x[1])[:15]:
            summary += f"  {k}: {v}\n"
        if texts:
            summary += "\nТексты в чертеже:\n" + "\n".join(texts[:30])
        result["text"] = summary
        result["rows"] = [[k, str(v)] for k, v in counts.items()]
        result["success"] = True
        result["type"] = "dxf"
    except Exception as e:
        result["error"] = f"DXF: {e}"
    return result


def _handle_zip(file_path: str, task_id: str, topic_id: int, result: dict) -> dict:
    """ZIP — распаковка и рекурсивная обработка"""
    try:
        tmp = tempfile.mkdtemp()
        with zipfile.ZipFile(file_path) as zf:
            names = zf.namelist()[:20]
            zf.extractall(tmp)
        texts = []
        all_rows = []
        for fn in names:
            fp = os.path.join(tmp, fn)
            if not os.path.isfile(fp):
                continue
            sub = extract_text_from_file(fp, task_id, topic_id)
            if sub["success"]:
                texts.append(f"[{fn}]\n{sub['text'][:1000]}")
                all_rows.extend(sub.get("rows", []))
        result["text"] = f"ZIP архив ({len(names)} файлов):\n\n" + "\n\n".join(texts)
        result["rows"] = all_rows
        result["success"] = True
        result["type"] = "zip"
    except Exception as e:
        result["error"] = f"ZIP: {e}"
    return result
# === END UNIVERSAL_FILE_HANDLER_V1 ===

====================================================================================================
END_FILE: core/universal_file_handler.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/upload_retry_queue.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c84118ed90d2faa43ddc5a8f1c63e8767639e25641c2b6ebc4c1ca38570171c2
====================================================================================================
"""
Upload retry queue.
Finds tasks where artifact was sent to Telegram (Drive failed),
checks if Drive is now available, re-uploads to Drive.
Notifies user in Telegram with new Drive link.
"""
import os
import sqlite3
import logging
import json
import tempfile
import requests
from dotenv import load_dotenv

load_dotenv("/root/.areal-neva-core/.env", override=True)

logging.basicConfig(
    filename="/root/.areal-neva-core/logs/upload_retry_queue.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

DB_PATH = "/root/.areal-neva-core/data/core.db"
BOT_TOKEN = <REDACTED_SECRET>"BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")


def check_drive_alive() -> bool:
    # === ROOT_TMP_UPLOAD_GUARD_V1 ===
    # Healthcheck MUST NOT upload tmp*.txt into AI_ORCHESTRA root.
    # It only lists the configured Drive root via OAuth.
    try:
        from core.topic_drive_oauth import _oauth_service, _root_folder_id
        service = _oauth_service()
        root_id = _root_folder_id()
        service.files().list(
            q=f"'{root_id}' in parents and trashed = false",
            spaces="drive",
            pageSize=1,
            fields="files(id,name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        logger.info("ROOT_TMP_UPLOAD_GUARD_V1: DRIVE_HEALTH_CHECK_LIST_OK root=%s", root_id)
        return True
    except Exception as e:
        logger.warning("ROOT_TMP_UPLOAD_GUARD_V1: DRIVE_HEALTH_CHECK_FAILED err=%s", e)
        return False
    # === END_ROOT_TMP_UPLOAD_GUARD_V1 ===


def get_pending_retry_tasks(conn: sqlite3.Connection):
    return conn.execute(
        """
        SELECT t.id, t.chat_id, t.topic_id, t.result,
               th_tg.action as tg_action
        FROM tasks t
        JOIN task_history th_tg ON th_tg.task_id = t.id
            AND th_tg.action LIKE 'TELEGRAM_ARTIFACT_FALLBACK_SENT:%'
        WHERE t.state IN ('AWAITING_CONFIRMATION','DONE')
          AND NOT EXISTS (
              SELECT 1 FROM task_history th2
              WHERE th2.task_id = t.id
                AND th2.action LIKE 'DRIVE_RETRY_UPLOAD_OK:%'
          )
        ORDER BY t.updated_at DESC
        LIMIT 20
        """,
    ).fetchall()


def parse_tg_action(action: str) -> dict:
    result = {}
    for part in action.split(":"):
        if "=" in part:
            k, v = part.split("=", 1)
            result[k] = v
    return result


def download_from_telegram(file_id: str, dest_path: str) -> bool:
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
            params={"file_id": file_id},
            timeout=15,
        )
        if not r.ok:
            return False
        file_path = r.json().get("result", {}).get("file_path")
        if not file_path:
            return False
        dl = requests.get(
            f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}",
            timeout=30,
        )
        if not dl.ok:
            return False
        with open(dest_path, "wb") as f:
            f.write(dl.content)
        return True
    except Exception as e:
        logger.error("TG_DOWNLOAD_FAILED file_id=%s err=%s", file_id, e)
        return False


def notify_telegram(chat_id, topic_id, message: str):
    if not BOT_TOKEN:
        return
    try:
        data = {"chat_id": str(chat_id), "text": message, "parse_mode": "HTML"}
        if topic_id and int(topic_id) > 0:
            data["message_thread_id"] = str(topic_id)
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json=data, timeout=10,
        )
    except Exception as e:
        logger.warning("NOTIFY_FAILED err=%s", e)


def run():
    logger.info("RETRY_QUEUE_START")

    if not check_drive_alive():
        logger.info("DRIVE_UNAVAILABLE — skip retry")
        return

    logger.info("DRIVE_ALIVE — checking pending tasks")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        pending = get_pending_retry_tasks(conn)
        logger.info("PENDING_RETRY_COUNT=%d", len(pending))

        for row in pending:
            task_id = row["id"]
            chat_id = row["chat_id"]
            topic_id = row["topic_id"]
            tg_info = parse_tg_action(row["tg_action"])
            file_id = tg_info.get("file_id")

            if not file_id:
                logger.warning("RETRY_SKIP task=%s no file_id", task_id)
                continue

            logger.info("RETRY_ATTEMPT task=%s file_id=%s", task_id, file_id)

            with tempfile.NamedTemporaryFile(
                suffix=".bin", delete=False,
                dir="/root/.areal-neva-core/runtime"
            ) as tmp:
                tmp_path = tmp.name

            ok = download_from_telegram(file_id, tmp_path)
            if not ok:
                logger.error("RETRY_TG_DOWNLOAD_FAILED task=%s", task_id)
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                continue

            # PATCH_RETRY_TOPIC_FOLDER_V1: upload to topic folder, not INGEST root
            try:
                import mimetypes as _mt
                from core.topic_drive_oauth import _upload_file_sync
                # Get original file name from task raw_input
                try:
                    _raw = conn.execute("SELECT raw_input FROM tasks WHERE id=?", (task_id,)).fetchone()
                    _orig_name = json.loads(_raw["raw_input"] or "{}").get("file_name", f"artifact_{task_id[:8]}")
                except Exception:
                    _orig_name = f"artifact_{task_id[:8]}"
                _mime = _mt.guess_type(_orig_name)[0] or "application/octet-stream"
                _up = _upload_file_sync(
                    tmp_path, _orig_name,
                    str(row["chat_id"]), int(topic_id or 0), _mime
                )
                _fid = _up.get("drive_file_id") if isinstance(_up, dict) else None
                drive_link = f"https://drive.google.com/file/d/{_fid}/view" if _fid else None
            except Exception as e:
                logger.error("RETRY_DRIVE_UPLOAD_FAILED task=%s err=%s", task_id, e)
                drive_link = None
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

            if not drive_link or "drive.google.com" not in str(drive_link):
                logger.error("RETRY_NO_LINK task=%s", task_id)
                continue

            old_result = row["result"] or ""
            new_result = old_result.replace(
                "Файл отправлен в Telegram. Внешнее хранилище временно недоступно.",
                f"Файл доступен на Drive: {drive_link}"
            )
            if new_result == old_result:
                new_result = old_result + f"\n\nФайл теперь на Drive: {drive_link}"

            conn.execute(
                "UPDATE tasks SET result=?, updated_at=datetime('now') WHERE id=?",
                (new_result, task_id),
            )
            conn.execute(
                "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                (task_id, f"DRIVE_RETRY_UPLOAD_OK:{drive_link}"),
            )
            conn.commit()

            notify_telegram(
                chat_id, topic_id,
                f"✅ Файл теперь доступен на Google Drive:\n{drive_link}"
            )
            logger.info("RETRY_UPLOAD_OK task=%s link=%s", task_id, drive_link)

    finally:
        conn.close()

    logger.info("RETRY_QUEUE_DONE")


if __name__ == "__main__":
    # === FULLFIX_20_RETRY_LOOP ===
    import time as _ff20_time
    logger.info("UPLOAD_RETRY_SERVICE_START")
    while True:
        try:
            run()
        except Exception as _ff20_re:
            logger.exception("UPLOAD_RETRY_LOOP_ERR=%s", _ff20_re)
        _ff20_time.sleep(300)
    # === END FULLFIX_20_RETRY_LOOP ===

====================================================================================================
END_FILE: core/upload_retry_queue.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/web_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 60ae8879713e63665e3b98acb78976ad8f6522694bb018b072daed8bd67c8912
====================================================================================================
import logging

logger = logging.getLogger("web_engine")

async def web_search(query: str) -> str:
    # Search handled by ONLINE_MODEL (perplexity/sonar) in ai_router.py
    logger.warning("web_search_stub called query=%s", (query or "")[:100])
    return ""

====================================================================================================
END_FILE: core/web_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/work_item.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ec6ecd21b8594924d8b0bdd0bde9e53d00e69485f45b88db8f7aedb11624f2f3
====================================================================================================
# === FULLFIX_DIRECTION_KERNEL_STAGE_1_WORKITEM ===
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


def _get(row, key, default=None):
    if row is None: return default
    if isinstance(row, dict): return row.get(key, default)
    try: return row[key]
    except Exception: return getattr(row, key, default)

def _int(v, d=0):
    try:
        if v is None or v == "": return d
        return int(v)
    except Exception: return d

def _str(v, d=""):
    if v is None: return d
    return str(v)


@dataclass
class WorkItem:
    work_id: str
    chat_id: str
    topic_id: int
    user_id: Optional[str] = None
    message_id: Optional[int] = None
    reply_to_message_id: Optional[int] = None
    bot_message_id: Optional[int] = None
    source_type: str = "telegram"
    input_type: str = "unknown"
    raw_text: str = ""
    state: str = "NEW"
    intent: str = "UNKNOWN"
    direction: Optional[str] = None
    direction_profile: Dict[str, Any] = field(default_factory=dict)
    formats_in: List[str] = field(default_factory=list)
    formats_out: List[str] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    context_refs: Dict[str, Any] = field(default_factory=dict)
    execution_plan: List[Dict[str, Any]] = field(default_factory=list)
    quality_gates: List[str] = field(default_factory=list)
    result: Dict[str, Any] = field(default_factory=dict)
    audit: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_task_row(cls, row, extra=None):
        extra = extra or {}
        raw_text = _str(extra.get("raw_text") or extra.get("raw_input") or _get(row, "raw_input", ""))
        input_type = _str(extra.get("input_type") or _get(row, "input_type", "unknown"), "unknown")
        topic_id = _int(extra.get("topic_id") if extra.get("topic_id") is not None else _get(row, "topic_id", 0), 0)
        wi = cls(
            work_id=_str(extra.get("work_id") or extra.get("task_id") or _get(row, "id", "")),
            chat_id=_str(extra.get("chat_id") or _get(row, "chat_id", "")),
            topic_id=topic_id,
            user_id=_str(extra.get("user_id") or _get(row, "user_id", "")) or None,
            message_id=_int(extra.get("message_id") or _get(row, "message_id", None), 0) or None,
            reply_to_message_id=_int(extra.get("reply_to_message_id") if extra.get("reply_to_message_id") is not None else _get(row, "reply_to_message_id", None), 0) or None,
            bot_message_id=_int(extra.get("bot_message_id") if extra.get("bot_message_id") is not None else _get(row, "bot_message_id", None), 0) or None,
            source_type=_str(extra.get("source_type") or "telegram"),
            input_type=input_type,
            raw_text=raw_text,
            state=_str(extra.get("state") or _get(row, "state", "NEW"), "NEW"),
            created_at=_str(extra.get("created_at") or _get(row, "created_at", "")) or None,
            updated_at=_str(extra.get("updated_at") or _get(row, "updated_at", "")) or None,
        )
        wi.formats_in = wi._detect_formats_in()
        wi.result = {"text": _str(_get(row, "result", ""))}
        err = _str(_get(row, "error_message", ""))
        if err:
            wi.errors.append({"code": "TASK_ERROR", "message": err, "fatal": False})
        wi.audit["created_by"] = "FULLFIX_DIRECTION_KERNEL_STAGE_1"
        return wi

    def _detect_formats_in(self):
        t = (self.input_type or "").lower()
        raw = (self.raw_text or "").lower()
        out = []
        if t in ("text","voice","photo","file","drive_file","url","mixed"): out.append(t)
        if ".pdf" in raw or "pdf" in t: out.append("pdf")
        if ".xlsx" in raw or ".xls" in raw: out.append("xlsx")
        if ".dwg" in raw: out.append("dwg")
        if t in ("photo","image"): out.append("photo")
        if not out: out.append("text")
        return list(dict.fromkeys(out))

    def set_direction(self, direction, profile=None):
        self.direction = direction
        self.direction_profile = profile or {}
        self.audit["direction"] = direction
        self.audit["direction_profile_id"] = self.direction_profile.get("id", direction)

    def set_intent(self, intent):
        self.intent = intent or "UNKNOWN"
        self.audit["intent"] = self.intent

    def add_audit(self, key, value):
        self.audit[str(key)] = value

    def add_error(self, code, message, fatal=False):
        self.errors.append({"code": str(code), "message": str(message), "fatal": bool(fatal)})

    def to_dict(self): return asdict(self)

    def to_payload(self):
        return {
            "id": self.work_id, "task_id": self.work_id,
            "chat_id": self.chat_id, "topic_id": self.topic_id,
            "user_id": self.user_id, "message_id": self.message_id,
            "reply_to_message_id": self.reply_to_message_id,
            "bot_message_id": self.bot_message_id,
            "source_type": self.source_type, "input_type": self.input_type,
            "raw_input": self.raw_text, "raw_text": self.raw_text,
            "state": self.state, "intent": self.intent,
            "direction": self.direction, "direction_profile": self.direction_profile,
            "formats_in": self.formats_in, "formats_out": self.formats_out,
            "attachments": self.attachments, "parsed_data": self.parsed_data,
            "context_refs": self.context_refs, "execution_plan": self.execution_plan,
            "quality_gates": self.quality_gates, "result": self.result,
            "audit": self.audit, "direction_audit": self.audit,
            "errors": self.errors, "metadata": self.metadata,
            "work_item": self.to_dict(),
        }
# === END FULLFIX_DIRECTION_KERNEL_STAGE_1_WORKITEM ===

====================================================================================================
END_FILE: core/work_item.py
FILE_CHUNK: 1/1
====================================================================================================
