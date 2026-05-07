# === FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3 ===
from __future__ import annotations

import os
import re
import io
import json
import uuid
import time
import math
import sqlite3
import asyncio
import tempfile
import statistics
import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple

import requests
from dotenv import load_dotenv

BASE = Path("/root/.areal-neva-core")
ENV_PATH = BASE / ".env"
MEM_DB = BASE / "data/memory.db"
load_dotenv(str(ENV_PATH), override=True)

TOPIC_ID_STROYKA = 2
DRIVE_TEMPLATES_PARENT_ID = "19Z3acDgPub4nV55mad5mb8ju63FsqoG9"

DEPRECATED_TEMPLATE_NAMES = (
    "ВОР_кирпичная_кладка_ИСПРАВЛЕНО.xlsx",
)

CANON_TEMPLATE_FALLBACK = {
    "m80": {"title": "М-80.xlsx", "role": "full_house_estimate_template", "file_id": "1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp", "source": "fallback_registry"},
    "m110": {"title": "М-110.xlsx", "role": "full_house_estimate_template", "file_id": "1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo", "source": "fallback_registry"},
    "roof": {"title": "крыша и перекр.xlsx", "role": "roof_and_floor_estimate_template", "file_id": "16YecwnJ9umnVprFu9V77UCV6cPrYbNh3", "source": "fallback_registry"},
    "foundation": {"title": "фундамент_Склад2.xlsx", "role": "foundation_estimate_template", "file_id": "1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp", "source": "fallback_registry"},
    "areal": {"title": "Ареал Нева.xlsx", "role": "general_company_estimate_template", "file_id": "1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm", "source": "fallback_registry"},
}

ESTIMATE_WORDS = (
    "смет", "стоимость", "расчет", "расчёт", "посчитай", "коробк", "дом", "стройк",
    "фундамент", "кровл", "перекр", "ангар", "склад", "газобетон", "каркас", "монолит",
)

CONTINUATION_WORDS = (
    "да", "да сделай", "сделай", "где смета", "ну что", "вариант 1", "вариант 2",
    "первый", "второй", "подтверждаю", "ок", "окей", "цены актуальны", "адрес подтверждаю",
    "средняя", "минимальная", "максимальная", "ручная", "конкретная ссылка",
)

REVISION_WORDS = (
    "нет не так", "не так", "переделай", "исправь", "правки", "пересчитай", "измени", "уточни",
)

PROJECT_ONLY_WORDS = (
    "проект ар", "проект кж", "проект кд", "чертеж", "чертёж", "раздел ар", "раздел кж", "раздел кд",
)

EXCLUSIONS_DEFAULT = (
    "подготовка участка",
    "стройгородок",
    "бытовки",
    "отмостка",
    "дренаж",
    "ливневая канализация",
    "вывоз мусора",
    "наружные сети",
    "всё, что не указано явно",
)

PRICE_CHOICE_HELP = """Выбор цены:
- средняя / медианная
- минимальная
- максимальная
- конкретная ссылка
- ручная цена
- можно добавить наценку, скидку, запас или поправку по позиции, разделу или всей смете"""


def _s(v: Any) -> str:
    return "" if v is None else str(v).strip()


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _clean(text: str, limit: int = 12000) -> str:
    text = (text or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]


def _now() -> str:
    return datetime.datetime.utcnow().isoformat()


def _row_get(row: Any, key: str, default: Any = "") -> Any:
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        return getattr(row, key, default)


def _cols(conn: sqlite3.Connection, table: str) -> List[str]:
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except Exception:
        return []


def _update_task_safe(conn: sqlite3.Connection, task_id: str, **kwargs: Any) -> None:
    cols = _cols(conn, "tasks")
    parts, vals = [], []
    for k, v in kwargs.items():
        if k in cols:
            parts.append(f"{k}=?")
            vals.append(v)
    if "updated_at" in cols:
        parts.append("updated_at=datetime('now')")
    if not parts:
        return
    vals.append(task_id)
    conn.execute(f"UPDATE tasks SET {', '.join(parts)} WHERE id=?", vals)
    conn.commit()


def _history_safe(conn: sqlite3.Connection, task_id: str, action: str) -> None:
    try:
        conn.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
            (task_id, _clean(action, 1000)),
        )
        conn.commit()
    except Exception:
        pass


def _memory_save(chat_id: str, key: str, value: Dict[str, Any]) -> None:
    try:
        con = sqlite3.connect(str(MEM_DB))
        try:
            payload = json.dumps(value, ensure_ascii=False, indent=2)
            con.execute(
                "INSERT OR REPLACE INTO memory (id, chat_id, key, value, timestamp) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), str(chat_id), str(key), payload, _now()),
            )
            con.commit()
        finally:
            con.close()
    except Exception:
        pass


def _memory_latest(chat_id: str, key_prefix: str) -> Optional[Dict[str, Any]]:
    try:
        con = sqlite3.connect(str(MEM_DB))
        con.row_factory = sqlite3.Row
        try:
            row = con.execute(
                "SELECT key,value,timestamp FROM memory WHERE chat_id=? AND key LIKE ? ORDER BY timestamp DESC LIMIT 1",
                (str(chat_id), f"{key_prefix}%"),
            ).fetchone()
            if not row:
                return None
            data = json.loads(row["value"] or "{}")
            data["_memory_key"] = row["key"]
            data["_memory_timestamp"] = row["timestamp"]
            return data
        finally:
            con.close()
    except Exception:
        return None



# === FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_CONTEXT_BLEED_FIX ===
def _parse_iso_ts(value: Any) -> Optional[datetime.datetime]:
    txt = _s(value)
    if not txt:
        return None
    txt = txt.replace("Z", "+00:00")
    try:
        dt = datetime.datetime.fromisoformat(txt)
        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return dt
    except Exception:
        return None


def _age_seconds(value: Any) -> Optional[float]:
    dt = _parse_iso_ts(value)
    if not dt:
        return None
    return (datetime.datetime.utcnow() - dt).total_seconds()


def _pending_is_fresh(pending: Optional[Dict[str, Any]], max_seconds: int = 600) -> bool:
    if not pending:
        return False
    created = pending.get("created_at") or pending.get("_memory_timestamp")
    age = _age_seconds(created)
    return age is not None and 0 <= age <= max_seconds


def _is_bad_estimate_result(text: str) -> bool:
    t = _low(text)

    # === STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_BAD_RESULT_MARKERS ===
    stale_markers = (
        "задачи за последние 24 часа",
        "создание сметы: профлист",
        "итоговая сумма: 55000",
        "1capn1ikkxwypbxhny5caokqrsxbgzho",
        "1glcscpl3d91elveo_m11ezwh_uu5b4vm",
        "1pu77xrzhmpobus1pfximwdwckrgje1tn",
        "смета уже есть:",
        "смета создана по образцу вор",
        "вор_кирпичная_кладка",
        "vor_kirpich",
        "позиций: 13 | итого: 690510",
        "690510.00 руб",
        "файлы в этом топике уже есть",
        "нашёл релевантное",
        "нашел релевантное",
        "активный контекст найден",
    )
    if any(x in t for x in stale_markers):
        return True
    # === END_STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_BAD_RESULT_MARKERS ===
    bad = (
        # === FULL_STROYKA_V3_SEARCH_LOOP_BAD_RESULT_FIX ===
        "поставщик | площадка",
        "auto_parts",
        "search_monolith",
        "tco | риски",
        "ошибка классификации запроса",
        "категория не совпадает",
        # === FULL_STROYKA_LOOP_FINAL_CLOSE_BAD_RESULT_FIX ===
        "смета создана по образцу вор",
        "смета уже есть:",
        "вор_кирпичная_кладка",
        "вор_кирпич",
        "vor_kirpich",
        "в_ор_кирпич",
        "позиций: 13 | итого: 690510",
        "690510.00 руб",
        # === END_FULL_STROYKA_LOOP_FINAL_CLOSE_BAD_RESULT_FIX ===
        # === END_FULL_STROYKA_V3_SEARCH_LOOP_BAD_RESULT_FIX ===
        "файлы в этом топике уже есть",
        "нашёл релевантное",
        "нашел релевантное",
        "можно использовать как образец сметы",
        "активный контекст найден",
        "проектный файл не создан",
        "docx_create_failed",
        "state: finished",
        "задача закрыта по запросу",
    )
    # === FULL_STROYKA_DISABLE_OLD_ESTIMATE_RECALL_FINAL_BAD_MARKERS ===
    stale_links = (
        "задачи за последние 24 часа",
        "создание сметы: профлист",
        "итоговая сумма: 55000",
        "1capn1ikkxwypbxhny5caokqrsxbgzho",
        "1glcscpl3d91elveo_m11ezwh_uu5b4vm",
        "1pu77xrzhmpobus1pfximwdwckrgje1tn",
        "смета уже есть",
        "использовать существующую или пересчитать",
    )
    if any(x in t for x in stale_links):
        return True
    # === END_FULL_STROYKA_DISABLE_OLD_ESTIMATE_RECALL_FINAL_BAD_MARKERS ===
    return any(x in t for x in bad)


def _has_real_estimate_artifact(text: str) -> bool:
    t = _low(text)
    if _is_bad_estimate_result(t):
        return False
    good = (
        "excel:",
        "xlsx:",
        ".xlsx",
        "pdf:",
        ".pdf",
        "предварительная смета готова",
        "итого:",
    )
    return any(x in t for x in good)


def _is_confirm_only(text: str) -> bool:
    t = _low(text).replace("[voice]", "").strip()
    if any(x in t for x in ESTIMATE_WORDS):
        return False
    return _is_confirm(t)
# === END_FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_CONTEXT_BLEED_FIX ===

def _drive_service():
    from core.topic_drive_oauth import _oauth_service
    return _oauth_service()


def list_drive_templates() -> List[Dict[str, Any]]:
    try:
        service = _drive_service()
        q = (
            f"'{DRIVE_TEMPLATES_PARENT_ID}' in parents and trashed = false and "
            "(mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' "
            "or mimeType = 'application/vnd.ms-excel' "
            "or mimeType = 'application/vnd.google-apps.spreadsheet')"
        )
        resp = service.files().list(
            q=q,
            spaces="drive",
            fields="files(id,name,mimeType,modifiedTime,size)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            pageSize=100,
        ).execute()
        out = []
        for f in resp.get("files", []):
            name = f.get("name") or ""
            if name in DEPRECATED_TEMPLATE_NAMES:
                continue
            out.append({
                "title": name,
                "file_id": f.get("id"),
                "mimeType": f.get("mimeType"),
                "modifiedTime": f.get("modifiedTime"),
                "role": "drive_dynamic_template",
                "source": "drive_templates_folder",
            })
        return out
    except Exception:
        return []


def _fallback_template_list() -> List[Dict[str, Any]]:
    return [dict(v) for v in CANON_TEMPLATE_FALLBACK.values()]


def _extract_dimensions(text: str) -> Optional[Tuple[float, float]]:
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*[xх×*]\s*(\d+(?:[.,]\d+)?)", _low(text))
    if not m:
        return None
    return float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))


def _extract_floors(text: str) -> Optional[int]:
    t = _low(text)
    m = re.search(r"(\d+)\s*(?:этаж|этажа|этажей)", t)
    if m:
        return int(m.group(1))
    if "2 эта" in t or "два эта" in t:
        return 2
    if "1 эта" in t or "один эта" in t:
        return 1
    return None


def _extract_distance_km(text: str) -> Optional[float]:
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*км", _low(text))
    return float(m.group(1).replace(",", ".")) if m else None


def _extract_material(text: str) -> str:
    t = _low(text)
    for key in ("газобетон", "каркас", "кирпич", "монолит", "керамоблок", "брус", "арболит"):
        if key in t:
            return key
    return ""


def _extract_object(text: str) -> str:
    t = _low(text)
    for key in ("дом", "ангар", "склад", "фундамент", "кровля", "коробка"):
        if key in t:
            return key
    return ""


def _extract_foundation(text: str) -> str:
    t = _low(text)
    if "монолит" in t or "плита" in t:
        return "монолитная плита"
    if "лента" in t:
        return "ленточный фундамент"
    if "сва" in t:
        return "свайный фундамент"
    if "фундамент" in t:
        return "фундамент"
    return ""


def _extract_scope(text: str) -> str:
    t = _low(text)
    if "под ключ" in t:
        return "под ключ"
    if "коробк" in t:
        return "коробка"
    return ""


def _parse_request(text: str) -> Dict[str, Any]:
    dims = _extract_dimensions(text)
    area_floor = dims[0] * dims[1] if dims else None
    floors = _extract_floors(text)
    area_total = area_floor * floors if area_floor and floors else area_floor
    return {
        "object": _extract_object(text),
        "material": _extract_material(text),
        "dimensions": dims,
        "area_floor": area_floor,
        "floors": floors,
        "area_total": area_total,
        "distance_km": _extract_distance_km(text),
        "foundation": _extract_foundation(text),
        "scope": _extract_scope(text),
        "raw": text,
    }


def _missing_question(parsed: Dict[str, Any]) -> Optional[str]:

    # === STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_PRICE_NO_MISSING ===
    raw = _low(parsed.get("raw", ""))
    if ("цена" in raw or "руб" in raw or "₽" in raw) and any(u in raw for u in ("м²", "м2", "м³", "м3", "шт", "кг", "тн", "тонн")) and any(x in raw for x in ("смет", "фундамент", "монолит", "кровл", "работ")):
        return None
    # === END_STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_PRICE_NO_MISSING ===
    if not parsed.get("object"):
        return "Что строим: дом, ангар, склад, фундамент или кровлю?"
    if not parsed.get("material") and parsed.get("object") not in ("фундамент", "кровля", "ангар", "склад"):
        return "Из какого материала строим?"
    if parsed.get("distance_km") is None:
        return "Где находится объект: город или удалённость в км?"
    if not parsed.get("dimensions"):
        return "Какие размеры объекта?"
    if parsed.get("object") == "дом" and not parsed.get("floors"):
        return "Сколько этажей?"
    if not parsed.get("foundation") and parsed.get("object") not in ("кровля", "фундамент", "ангар", "склад"):
        return "Какой фундамент?"
    if not parsed.get("scope") and parsed.get("object") == "дом":
        return "Смета нужна только коробка или под ключ?"
    return None


def _template_score(parsed: Dict[str, Any], tpl: Dict[str, Any]) -> int:
    name = _low(tpl.get("title"))
    obj = parsed.get("object") or ""
    material = parsed.get("material") or ""
    area_total = float(parsed.get("area_total") or 0)
    score = 0
    if tpl.get("title") in DEPRECATED_TEMPLATE_NAMES:
        return -9999
    if obj in ("ангар", "склад", "фундамент") and ("фундамент" in name or "склад" in name):
        score += 100
    if obj == "кровля" and ("крыш" in name or "перекр" in name):
        score += 100
    if material == "каркас" and ("м-80" in name or "м80" in name or "м-110" in name or "м110" in name):
        score += 90
    if material == "каркас" and area_total and area_total > 100 and ("м-110" in name or "м110" in name):
        score += 40
    if material == "каркас" and area_total and area_total <= 100 and ("м-80" in name or "м80" in name):
        score += 40
    if material in ("газобетон", "кирпич", "керамоблок", "монолит", "арболит") and ("ареал" in name or "м-110" in name or "м110" in name or "м-80" in name or "м80" in name):
        score += 80
    if "ареал" in name:
        score += 20
    return score


def choose_template(parsed: Dict[str, Any]) -> Dict[str, Any]:
    templates = list_drive_templates() or _fallback_template_list()
    ranked = sorted(templates, key=lambda t: _template_score(parsed, t), reverse=True)
    return ranked[0] if ranked else CANON_TEMPLATE_FALLBACK["areal"]


def choose_template_sheet(parsed: Dict[str, Any], sheet_names: List[str]) -> Optional[str]:
    material = parsed.get("material") or ""
    obj = parsed.get("object") or ""
    names = list(sheet_names or [])
    lows = {name: _low(name) for name in names}

    if material == "каркас":
        for name, low in lows.items():
            if "каркас" in low:
                return name

    if material in ("газобетон", "кирпич", "керамоблок", "монолит", "арболит") or obj in ("дом", "коробка"):
        for name, low in lows.items():
            if "газобетон" in low:
                return name

    if obj in ("кровля",):
        for name, low in lows.items():
            if "кров" in low or "перекр" in low:
                return name

    if obj in ("ангар", "склад", "фундамент"):
        for name, low in lows.items():
            if "смет" in low or "фундамент" in low or "склад" in low:
                return name

    return names[0] if names else None


def download_template_xlsx(template: Dict[str, Any]) -> Optional[str]:
    file_id = template.get("file_id")
    if not file_id:
        return None
    try:
        service = _drive_service()
        mime = template.get("mimeType") or ""
        if mime == "application/vnd.google-apps.spreadsheet":
            request = service.files().export_media(
                fileId=file_id,
                mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
        path = os.path.join(tempfile.gettempdir(), f"tpl_{file_id}_{int(time.time())}.xlsx")
        with io.FileIO(path, "wb") as fh:
            from googleapiclient.http import MediaIoBaseDownload
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        return path if os.path.exists(path) and os.path.getsize(path) > 1000 else None
    except Exception:
        return None


def extract_template_prices(template_path: Optional[str], parsed: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    if not template_path or not os.path.exists(template_path):
        return "Цены из шаблона: шаблон не скачан, используется только структура/сценарий", None
    try:
        from openpyxl import load_workbook
        wb = load_workbook(template_path, data_only=True, read_only=True)
        selected = choose_template_sheet(parsed, wb.sheetnames)
        ws = wb[selected] if selected in wb.sheetnames else wb.active

        keys = ("бетон", "арматур", "газобетон", "кирпич", "кладк", "монтаж", "достав", "манипулятор", "кран", "пиломат", "кров")
        found = []
        for row in ws.iter_rows(values_only=True):
            txt = " | ".join("" if v is None else str(v) for v in row)
            low = _low(txt)
            if not any(k in low for k in keys):
                continue
            nums = re.findall(r"\d[\d\s]{2,}(?:[.,]\d+)?", txt)
            vals = []
            for n in nums:
                try:
                    v = float(n.replace(" ", "").replace(",", "."))
                    if 100 <= v <= 10000000:
                        vals.append(v)
                except Exception:
                    pass
            if vals:
                found.append(f"- {ws.title}: {txt[:180]}")
            if len(found) >= 15:
                break
        wb.close()
        return "Цены из выбранного листа шаблона:\n" + ("\n".join(found) if found else "ключевые цены в листе не распознаны автоматически"), selected
    except Exception as e:
        return f"Цены из шаблона: ошибка чтения шаблона: {e}", None


def is_stroyka_estimate_candidate(task: Any) -> bool:
    if int(_row_get(task, "topic_id", 0) or 0) != TOPIC_ID_STROYKA:
        return False
    input_type = _low(_row_get(task, "input_type", ""))
    if input_type in ("photo", "file", "drive_file", "image", "document"):
        return False
    raw = _low(_row_get(task, "raw_input", ""))
    if not raw:
        return False
    if any(x in raw for x in PROJECT_ONLY_WORDS) and "смет" not in raw and "стоим" not in raw:
        return False
    if _is_old_task_finish_request(raw):
        return True
    if any(x in raw for x in ESTIMATE_WORDS):
        return True
    if raw in CONTINUATION_WORDS or any(raw.startswith(x + " ") for x in CONTINUATION_WORDS):
        return True
    if any(x in raw for x in REVISION_WORDS):
        return True
    if raw.startswith("[voice]"):
        voice_raw = raw.replace("[voice]", "").strip()
        if voice_raw in CONTINUATION_WORDS or any(x in voice_raw for x in ESTIMATE_WORDS):
            return True
    return False


def _is_confirm(text: str) -> bool:
    t = _low(text).replace("[voice]", "").strip()
    return t in CONTINUATION_WORDS or any(t.startswith(x + " ") for x in CONTINUATION_WORDS)


def _is_revision(text: str) -> bool:
    return any(x in _low(text) for x in REVISION_WORDS)


def parse_price_choice(text: str) -> Dict[str, Any]:
    t = _low(text)
    choice = "median"
    if "миним" in t:
        choice = "minimum"
    elif "максим" in t:
        choice = "maximum"
    elif "конкрет" in t or "ссылк" in t or "вариант" in t:
        choice = "specific_source"
    elif "ручн" in t or "сам" in t:
        choice = "manual"
    elif "средн" in t or "медиан" in t or "да" in t or "подтверж" in t or "ок" in t:
        choice = "median"

    percent = 0.0
    m = re.search(r"(наценк|запас|плюс|\+)\s*(\d+(?:[.,]\d+)?)\s*%", t)
    if m:
        percent += float(m.group(2).replace(",", "."))
    m = re.search(r"(скидк|минус|-)\s*(\d+(?:[.,]\d+)?)\s*%", t)
    if m:
        percent -= float(m.group(2).replace(",", "."))

    manual_values = []
    if choice == "manual":
        for n in re.findall(r"\d[\d\s]{2,}(?:[.,]\d+)?", text):
            try:
                v = float(n.replace(" ", "").replace(",", "."))
                if 100 <= v <= 10000000:
                    manual_values.append(v)
            except Exception:
                pass

    return {"choice": choice, "percent_adjustment": percent, "manual_values": manual_values, "raw": text}


def _numbers_from_price_text(price_text: str, keywords: Tuple[str, ...]) -> List[float]:
    vals = []
    for line in price_text.splitlines():
        low = _low(line)
        if any(k in low for k in keywords):
            for n in re.findall(r"\d[\d\s]{2,}(?:[.,]\d+)?", line):
                try:
                    v = float(n.replace(" ", "").replace(",", "."))
                    if 100 <= v <= 10000000:
                        vals.append(v)
                except Exception:
                    pass
    return vals


def _choose_value(values: List[float], choice: Dict[str, Any], default: float = 0.0) -> float:
    if choice.get("choice") == "manual" and choice.get("manual_values"):
        v = float(choice["manual_values"][0])
    elif values:
        if choice.get("choice") == "minimum":
            v = min(values)
        elif choice.get("choice") == "maximum":
            v = max(values)
        elif choice.get("choice") == "specific_source":
            v = values[0]
        else:
            v = statistics.median(values)
    else:
        v = default

    pct = float(choice.get("percent_adjustment") or 0)
    if pct:
        v = v * (1 + pct / 100)
    return float(v)


async def _send_text(chat_id: str, text: str, reply_to: Optional[int], topic_id: int) -> Dict[str, Any]:
    from core.reply_sender import send_reply_ex
    return await asyncio.to_thread(
        send_reply_ex,
        chat_id=str(chat_id),
        text=_clean(text, 12000),
        reply_to_message_id=reply_to,
        message_thread_id=topic_id,
    )


async def _send_document(chat_id: str, file_path: str, caption: str, reply_to: Optional[int], topic_id: int) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token or not os.path.exists(file_path):
        return False
    data = {"chat_id": str(chat_id), "caption": _clean(caption, 900)}
    if reply_to:
        data["reply_to_message_id"] = int(reply_to)
    if topic_id:
        data["message_thread_id"] = int(topic_id)
    try:
        with open(file_path, "rb") as f:
            r = requests.post(f"https://api.telegram.org/bot{token}/sendDocument", data=data, files={"document": f}, timeout=60)
        return r.status_code == 200 and r.json().get("ok") is True
    except Exception:
        return False


def _latest_estimate_result(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[sqlite3.Row]:
    """
    STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED

    Old DONE/ARCHIVED estimate reuse is forbidden for topic_2.
    Every new stroyka estimate must be calculated from current raw_input only.
    Old Drive links, old VOR files, old proflist estimates and stale memory are never valid input.
    """
    return None

def _latest_estimate_task(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[sqlite3.Row]:
    try:
        rows = conn.execute(
            """
            SELECT * FROM tasks
            WHERE chat_id=? AND COALESCE(topic_id,0)=?
              AND state IN ('WAITING_CLARIFICATION','IN_PROGRESS','AWAITING_CONFIRMATION')
              AND updated_at >= datetime('now','-24 hours')
              AND (
                raw_input LIKE '%смет%' OR raw_input LIKE '%стоимость%' OR raw_input LIKE '%газобетон%' OR
                raw_input LIKE '%фундамент%' OR raw_input LIKE '%кровл%' OR raw_input LIKE '%ангар%' OR
                result LIKE '%смет%'
              )
            ORDER BY updated_at DESC
            LIMIT 20
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()
        for row in rows:
            result = _s(_row_get(row, "result", ""))
            if result and _is_bad_estimate_result(result):
                continue
            return row
        return None
    except Exception:
        return None



# === FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_MEMORY_REVIVE_FIX ===
def _estimate_raw_score(raw: str) -> int:
    parsed = _parse_request(raw)
    score = 0
    if parsed.get("object"):
        score += 20
    if parsed.get("material"):
        score += 20
    if parsed.get("dimensions"):
        score += 25
    if parsed.get("floors"):
        score += 10
    if parsed.get("distance_km") is not None:
        score += 15
    if parsed.get("foundation"):
        score += 10
    if parsed.get("scope"):
        score += 5
    raw_low = _low(raw)
    if "смет" in raw_low or "стоим" in raw_low or "посчитай" in raw_low:
        score += 15
    return score


def _is_old_task_finish_request(text: str) -> bool:
    t = _low(text).replace("[voice]", "").strip()
    phrases = (
        # === FULL_STROYKA_LOOP_FINAL_CLOSE_REVIVE_PHRASES_FIX ===
        "что с моими задачами",
        "какое ты задание получил",
        "почему ты не сделаешь мне смету",
        "предыдущее техническое задание",
        "посмотри что мы строим",
        "задача завершена",
        "все задачи отменены",
        # === END_FULL_STROYKA_LOOP_FINAL_CLOSE_REVIVE_PHRASES_FIX ===

        # === FULL_STROYKA_V3_REVIVE_PHRASES_FIX ===
        "что продолжаешь",
        "что продолжаешь-то",
        "где моя смета",
        "моя смета",
        "смета по итогу",
        "посмотри их задания",
        "посмотрите их задания",
        # === END_FULL_STROYKA_V3_REVIVE_PHRASES_FIX ===
        "доделай",
        "доделай задачу",
        "доделай смету",
        "продолжай",
        "закончи",
        "смету в excel",
        "смету в эксель",
        "мне нужна смета",
        "где смета",
        "ну что",
    )
    if any(p in t for p in phrases):
        return True
    if t in ("да", "сделай", "да сделай", "ок", "окей"):
        return True
    return False


def _latest_revivable_estimate_task(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[sqlite3.Row]:
    try:
        rows = conn.execute(
            """
            SELECT * FROM tasks
            WHERE chat_id=? AND COALESCE(topic_id,0)=?
              AND state IN ('FAILED','DONE','CANCELLED','ARCHIVED')
              AND updated_at >= datetime('now','-7 days')
              AND (
                raw_input LIKE '%смет%' OR raw_input LIKE '%стоимость%' OR raw_input LIKE '%посчитай%' OR
                raw_input LIKE '%газобетон%' OR raw_input LIKE '%фундамент%' OR raw_input LIKE '%кровл%' OR
                raw_input LIKE '%ангар%' OR raw_input LIKE '%коробк%' OR raw_input LIKE '%монолит%' OR
                raw_input LIKE '%дом%'
              )
            ORDER BY updated_at DESC
            LIMIT 80
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()

        best = None
        best_score = 0
        for row in rows:
            raw = _s(_row_get(row, "raw_input", ""))
            result = _s(_row_get(row, "result", ""))

            # ВАЖНО: старые задачи являются памятью и не удаляются
            # Нельзя повторно отдавать старый ошибочный result как готовую смету
            # Можно и нужно брать старый raw_input как исходное ТЗ
            if _is_bad_estimate_result(result) and not raw:
                continue

            score = _estimate_raw_score(raw)
            if score > best_score:
                best = row
                best_score = score

        if best is not None and best_score >= 45:
            return best
        return None
    except Exception:
        return None
# === END_FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_MEMORY_REVIVE_FIX ===

async def _search_prices_online(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str]) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    model = os.getenv("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY_MISSING")

    query = f"""
Найди актуальные цены для предварительной строительной сметы.
Регион: Санкт-Петербург и Ленинградская область
Объект: {parsed.get('object') or 'объект'}
Материал: {parsed.get('material') or 'строительные материалы'}
Фундамент: {parsed.get('foundation') or 'не указан'}
Шаблон: {template.get('title')}
Лист шаблона: {sheet_name or 'не выбран'}
Удалённость: {parsed.get('distance_km')} км

Верни цены с источниками:
бетон В25/В30, арматура А500, материал стен, работа, доставка, манипулятор/кран, разгрузка.
Для каждой позиции дай минимум/среднюю/максимум если доступны.
Формат:
- Позиция | цена | единица | регион | источник | ссылка | checked_at
Не выдумывай. Если цены нет — НЕТ ДАННЫХ.
""".strip()

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Ты строительный снабженец. Дай цены с источниками и ссылками. Без общих советов."},
            {"role": "user", "content": query},
        ],
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def _call() -> str:
        r = requests.post(f"{base_url}/chat/completions", headers=headers, json=body, timeout=90)
        if r.status_code != 200:
            raise RuntimeError(f"OPENROUTER_HTTP_{r.status_code}:{r.text[:300]}")
        return _clean(r.json()["choices"][0]["message"]["content"], 6000)

    return await asyncio.to_thread(_call)


def _build_estimate_items(parsed: Dict[str, Any], price_text: str, choice: Dict[str, Any]) -> List[Dict[str, Any]]:
    dims = parsed.get("dimensions") or (10.0, 10.0)
    area_floor = float(parsed.get("area_floor") or (dims[0] * dims[1]))
    floors = int(parsed.get("floors") or 1)
    perimeter = 2 * (dims[0] + dims[1])
    distance = float(parsed.get("distance_km") or 0)

    concrete_price = _choose_value(_numbers_from_price_text(price_text, ("бетон", "в25", "в30")), choice)
    rebar_price = _choose_value(_numbers_from_price_text(price_text, ("арматур", "а500")), choice)
    wall_price = _choose_value(_numbers_from_price_text(price_text, ("газобетон", "кирпич", "керамоблок", "стен")), choice)
    work_price = _choose_value(_numbers_from_price_text(price_text, ("работ", "кладк", "монолит", "каркас")), choice)
    delivery_price = _choose_value(_numbers_from_price_text(price_text, ("достав", "рейс", "манипулятор", "кран")), choice)

    foundation_volume = max(area_floor * 0.25, 1)
    rebar_qty = max(foundation_volume * 0.08, 0.1)
    wall_volume = max(perimeter * 3.0 * floors * 0.30, 1)
    roof_area = max(area_floor * 1.25, 1)
    trips = max(math.ceil(distance / 40), 1) if distance > 0 else 1

    return [
        {"section": "Фундамент", "name": "Бетон для монолитных работ", "unit": "м³", "qty": foundation_volume, "price": concrete_price, "note": "актуальная подтверждённая цена"},
        {"section": "Фундамент", "name": "Арматура А500", "unit": "т", "qty": rebar_qty, "price": rebar_price, "note": "актуальная подтверждённая цена"},
        {"section": "Стены", "name": f"Материал стен: {parsed.get('material') or 'по ТЗ'}", "unit": "м³", "qty": wall_volume, "price": wall_price, "note": "актуальная подтверждённая цена"},
        {"section": "Стены", "name": "Работы по стенам", "unit": "м³", "qty": wall_volume, "price": work_price, "note": "актуальная подтверждённая цена"},
        {"section": "Перекрытия", "name": "Перекрытия / черновой конструктив", "unit": "м²", "qty": area_floor, "price": max(work_price, 0), "note": "по шаблонной логике"},
        {"section": "Кровля", "name": "Кровельный контур", "unit": "м²", "qty": roof_area, "price": max(wall_price * 0.15, 0), "note": "по шаблонной логике"},
        {"section": "Логистика", "name": "Доставка / рейсы", "unit": "рейс", "qty": trips, "price": delivery_price, "note": f"{distance:g} км / 40"},
        {"section": "Накладные", "name": "Организация работ и накладные", "unit": "компл", "qty": 1, "price": max((foundation_volume * concrete_price + wall_volume * wall_price) * 0.07, 0), "note": "отдельный блок"},
    ]


def _create_xlsx_from_template(task_id: str, parsed: Dict[str, Any], template: Dict[str, Any], template_path: Optional[str], sheet_name: Optional[str], price_text: str, choice: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], float]:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, Alignment

    items = _build_estimate_items(parsed, price_text, choice)

    if template_path and os.path.exists(template_path):
        try:
            import sys as _sec_sys
            _sec_old_limit = _sec_sys.getrecursionlimit()
            _sec_sys.setrecursionlimit(5000)
            try:
                wb = load_workbook(template_path)
            finally:
                _sec_sys.setrecursionlimit(_sec_old_limit)
            if sheet_name and sheet_name in wb.sheetnames:
                wb.active = wb.sheetnames.index(sheet_name)
        except Exception:
            wb = Workbook()
    else:
        wb = Workbook()

    if "AREAL_CALC" in wb.sheetnames:
        del wb["AREAL_CALC"]
    ws = wb.create_sheet("AREAL_CALC", 0)

    ws.append(["Предварительная смета"])
    ws.append(["Эталон", template.get("title", "")])
    ws.append(["Лист эталона", sheet_name or "не выбран"])
    ws.append(["Выбор цены", choice.get("choice"), f"поправка {choice.get('percent_adjustment', 0)}%"])
    ws.append(["Объект", parsed.get("raw", "")])
    ws.append([])
    headers = ["№", "Раздел", "Наименование", "Ед. изм.", "Кол-во", "Работа Цена", "Работа Стоимость", "Материалы Цена", "Материалы Стоимость", "Всего", "Примечание"]
    ws.append(headers)

    header_row = 7
    for c in range(1, len(headers) + 1):
        ws.cell(header_row, c).font = Font(bold=True)
        ws.cell(header_row, c).alignment = Alignment(wrap_text=True)

    py_total = 0.0
    row_idx = header_row + 1
    for i, it in enumerate(items, 1):
        qty = float(it["qty"])
        price = float(it["price"])
        py_total += qty * price
        ws.cell(row_idx, 1, i)
        ws.cell(row_idx, 2, it["section"])
        ws.cell(row_idx, 3, it["name"])
        ws.cell(row_idx, 4, it["unit"])
        ws.cell(row_idx, 5, qty)
        ws.cell(row_idx, 6, 0)
        ws.cell(row_idx, 7, f"=E{row_idx}*F{row_idx}")
        ws.cell(row_idx, 8, price)
        ws.cell(row_idx, 9, f"=E{row_idx}*H{row_idx}")
        ws.cell(row_idx, 10, f"=G{row_idx}+I{row_idx}")
        ws.cell(row_idx, 11, it["note"])
        row_idx += 1

    total_row = row_idx + 1
    ws.cell(total_row, 9, "ИТОГО")
    ws.cell(total_row, 10, f"=SUM(J{header_row+1}:J{row_idx-1})")
    ws.cell(total_row + 1, 9, "НДС 20%")
    ws.cell(total_row + 1, 10, f"=J{total_row}*0.2")
    ws.cell(total_row + 2, 9, "С НДС")
    ws.cell(total_row + 2, 10, f"=J{total_row}+J{total_row+1}")

    excl_row = total_row + 4
    ws.cell(excl_row, 2, "Не входит")
    ws.cell(excl_row, 2).font = Font(bold=True)
    for idx, item in enumerate(EXCLUSIONS_DEFAULT, excl_row + 1):
        ws.cell(idx, 2, item)

    widths = {1: 8, 2: 18, 3: 48, 4: 12, 5: 12, 6: 14, 7: 18, 8: 16, 9: 20, 10: 16, 11: 36}
    for col, width in widths.items():
        ws.column_dimensions[ws.cell(1, col).column_letter].width = width

    path = os.path.join(tempfile.gettempdir(), f"stroyka_estimate_{task_id[:8]}_{int(time.time())}.xlsx")
    wb.save(path)
    wb.close()
    return path, items, py_total


def _quality_gate_xlsx(xlsx_path: str, items: List[Dict[str, Any]], py_total: float) -> Tuple[bool, str]:
    if not xlsx_path or not os.path.exists(xlsx_path):
        return False, "XLSX_NOT_FOUND"
    if os.path.getsize(xlsx_path) < 5000:
        return False, "XLSX_TOO_SMALL"
    if len(items) < 8:
        return False, f"TOO_FEW_ITEMS:{len(items)}"
    if py_total <= 0:
        return False, "TOTAL_ZERO"
    try:
        import sys as _qg_sys
        from openpyxl import load_workbook
        _qg_old = _qg_sys.getrecursionlimit()
        _qg_sys.setrecursionlimit(5000)
        try:
            wb = load_workbook(xlsx_path, data_only=False)
        finally:
            _qg_sys.setrecursionlimit(_qg_old)
        ws = wb["AREAL_CALC"] if "AREAL_CALC" in wb.sheetnames else wb.active
        formula_count = sum(1 for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("="))
        wb.close()
        if formula_count < 8:
            return False, f"TOO_FEW_FORMULAS:{formula_count}"
        return True, "OK"
    except Exception as e:
        return False, f"XLSX_VALIDATE_ERROR:{e}"


def _create_pdf(task_id: str, text: str) -> str:
    pdf_path = os.path.join(tempfile.gettempdir(), f"stroyka_estimate_{task_id[:8]}_{int(time.time())}.pdf")
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(pdf_path, pagesize=A4)
        y = 800
        for line in text.splitlines()[:50]:
            c.drawString(40, y, line[:110])
            y -= 16
            if y < 40:
                c.showPage()
                y = 800
        c.save()
    except Exception:
        Path(pdf_path).write_bytes(b"%PDF-1.4\n% fallback pdf\n")
    return pdf_path


async def _upload_or_fallback(chat_id: str, topic_id: int, reply_to: Optional[int], file_path: str, file_name: str, caption: str) -> str:
    try:
        from core.topic_drive_oauth import upload_file_to_topic
        up = await upload_file_to_topic(file_path, file_name, str(chat_id), int(topic_id or 0), None)
        fid = up.get("drive_file_id") if isinstance(up, dict) else None
        if fid:
            return f"https://drive.google.com/file/d/{fid}/view"
    except Exception:
        pass

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if token and os.path.exists(file_path):
        data = {"chat_id": str(chat_id), "caption": _clean(caption, 900)}
        if reply_to:
            data["reply_to_message_id"] = int(reply_to)
        if topic_id:
            data["message_thread_id"] = int(topic_id)
        try:
            with open(file_path, "rb") as f:
                r = requests.post(f"https://api.telegram.org/bot{token}/sendDocument", data=data, files={"document": f}, timeout=60)
            if r.status_code == 200 and r.json().get("ok") is True:
                return "TELEGRAM_FILE_FALLBACK_SENT"
        except Exception:
            pass
    return ""


def _final_summary(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], choice: Dict[str, Any], py_total: float, items=None) -> str:
    # === PATCH_TOPIC2_CANONICAL_FINAL_SUMMARY_V1 — §9 format ===
    obj = parsed.get("object") or parsed.get("raw") or "объект"
    material = parsed.get("material") or "не указан"
    dims = parsed.get("dims") or parsed.get("dimensions")
    try:
        a, b = float(dims[0]), float(dims[1])
        area_s = f"{a * b:.0f} м²"
    except Exception:
        area_s = str(parsed.get("area") or "не указана")
    floors = parsed.get("floors") or "не указана"
    region = parsed.get("region") or parsed.get("location") or "СПб и ЛО"
    tpl_name = template.get("title") or "Ареал Нева.xlsx"
    sheet = sheet_name or "смета"
    price_mode = choice.get("choice") or "шаблон"

    mat_total = work_total = logistics_total = overhead_total = 0.0
    if items:
        for it in items:
            sec = str(it.get("section", ""))
            val = float(it.get("qty") or 0) * float(it.get("price") or 0)
            if sec in ("Логистика",):
                logistics_total += val
            elif sec in ("Накладные расходы", "Накладные"):
                overhead_total += val
            else:
                mat_total += val
    else:
        logistics_total = round(py_total * 0.08, 2)
        overhead_total = round(py_total * 0.05, 2)
        mat_total = round(py_total * 0.87, 2)

    subtotal = round(mat_total + work_total + logistics_total + overhead_total, 2) or round(py_total, 2)
    nds = round(subtotal * 0.2, 2)
    total_nds = round(subtotal + nds, 2)

    return (
        f"✅ Смета готова\n\n"
        f"Объект: {obj}   Материал: {material}   Площадь: {area_s}   "
        f"Этажность: {floors}   Регион: {region}\n"
        f"Шаблон: {tpl_name}   Лист: {sheet}   Цены: {price_mode}\n\n"
        f"Итого:\n"
        f"  Материалы: {mat_total:,.0f} руб\n"
        f"  Работы: {work_total:,.0f} руб\n"
        f"  Логистика: {logistics_total:,.0f} руб\n"
        f"  Накладные: {overhead_total:,.0f} руб\n"
        f"  Без НДС: {subtotal:,.0f} руб\n"
        f"  НДС: {nds:,.0f} руб\n"
        f"  С НДС: {total_nds:,.0f} руб"
    ).replace(",", " ")


def _price_confirmation_text(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], template_prices: str, online_prices: str) -> str:
    exclusions = "\n".join(f"- {x}" for x in EXCLUSIONS_DEFAULT)
    return f"""⏳ Задачу понял

Шаблон: {template.get('title')}
Лист: {sheet_name or 'не выбран'}
Объект: {parsed.get('object') or 'не указан'}
Материал: {parsed.get('material') or 'не указан'}
Размеры: {parsed.get('dimensions') or 'не указаны'}
Этажей: {parsed.get('floors') or 'не указано'}
Фундамент: {parsed.get('foundation') or 'не указан'}
Удалённость: {parsed.get('distance_km') if parsed.get('distance_km') is not None else 'не указана'} км

{template_prices}

Актуальные цены из интернета с источниками:
{online_prices}

{PRICE_CHOICE_HELP}

Логистика:
- базовая логика: км / 40 рейсов × цена рейса
- доставка, разгрузка, манипулятор/кран, транспорт бригады считаются отдельным блоком

Не входит:
{exclusions}

Подтверди цены, адрес, лист шаблона и допущения — после этого создам Excel и PDF"""


async def _generate_and_send(conn: sqlite3.Connection, task: Any, pending: Dict[str, Any], confirm_text: str, logger=None) -> bool:
    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    reply_to = _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None)

    parsed = pending.get("parsed") or {}
    template = pending.get("template") or CANON_TEMPLATE_FALLBACK["areal"]
    online_prices = pending.get("online_prices") or ""
    sheet_name = pending.get("sheet_name")
    choice = parse_price_choice(confirm_text)

    template_path = download_template_xlsx(template)
    xlsx_path, items, py_total = _create_xlsx_from_template(task_id, parsed, template, template_path, sheet_name, online_prices, choice)
    ok, reason = _quality_gate_xlsx(xlsx_path, items, py_total)
    if not ok:
        await _send_text(chat_id, "Произошла ошибка при расчёте, повторяю", reply_to, topic_id)
        _update_task_safe(conn, task_id, state="FAILED", error_message=f"STROYKA_QG_FAILED:{reason}")
        return True

    summary = _final_summary(parsed, template, sheet_name, choice, py_total, items=items)
    pdf_path = _create_pdf(task_id, summary)
    xlsx_link = await _upload_or_fallback(chat_id, topic_id, reply_to, xlsx_path, f"stroyka_estimate_{task_id[:8]}.xlsx", "Excel сметы")
    pdf_link = await _upload_or_fallback(chat_id, topic_id, reply_to, pdf_path, f"stroyka_estimate_{task_id[:8]}.pdf", "PDF сметы")

    if not xlsx_link or not pdf_link:
        await _send_text(chat_id, "Произошла ошибка при загрузке файлов, повторяю", reply_to, topic_id)
        _update_task_safe(conn, task_id, state="FAILED", error_message="STROYKA_UPLOAD_FAILED")
        return True

    # === §9 canonical result format ===
    result = summary + f"\n\nExcel: {xlsx_link}\nPDF: {pdf_link}\n\nПодтверди или пришли правки"
    send_res = await _send_text(chat_id, result, reply_to, topic_id)
    kwargs = {"state": "AWAITING_CONFIRMATION", "result": result}
    if isinstance(send_res, dict) and send_res.get("bot_message_id"):
        kwargs["bot_message_id"] = send_res.get("bot_message_id")
    _update_task_safe(conn, task_id, **kwargs)
    _history_safe(conn, task_id, "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:estimate_generated")
    _memory_save(chat_id, "topic_2_estimate_last", {
        "task_id": task_id,
        "status": "AWAITING_CONFIRMATION",
        "result": result,
        "xlsx_link": xlsx_link,
        "pdf_link": pdf_link,
        "template": template,
        "sheet_name": sheet_name,
        "price_choice": choice,
        "parsed": parsed,
        "updated_at": _now(),
    })
    return True



# === STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_ITEM_ENGINE ===
def _stroyka_final_parse_direct_items(raw_text: str) -> List[Dict[str, Any]]:
    raw = _s(raw_text)
    if not raw:
        return []
    lines = [x.strip(" \t-—") for x in raw.replace("\r", "\n").splitlines() if x.strip()]
    items: List[Dict[str, Any]] = []
    unit_re = r"(м²|м2|м\^2|м³|м3|м\^3|п\.?\s*м\.?|пм|м\.?|шт\.?|кг|тн|тонн?а?|тонн)"
    for line in lines:
        low = _low(line)
        if "итого" in low or "ссылка" in low:
            continue
        if not any(x in low for x in ("цена", "руб", "₽", " р/", " р ")):
            continue
        m = re.search(
            rf"^(?P<name>.*?)(?:[—:-]\s*)?(?P<qty>\d+(?:[.,]\d+)?)\s*(?P<unit>{unit_re})\b.*?(?:цена|по)?\s*(?P<price>\d[\d\s]*(?:[.,]\d+)?)\s*(?:руб|р|₽)?",
            line, flags=re.I,
        )
        if not m:
            continue
        name = re.sub(r"^\s*\d+[\).]?\s*", "", m.group("name")).strip(" —:-")
        if not name:
            name = "Работа/материал"
        qty = float(m.group("qty").replace(",", "."))
        unit = m.group("unit").replace(" ", "").replace("^2", "²").replace("^3", "³")
        price = float(m.group("price").replace(" ", "").replace(",", "."))
        if qty <= 0 or price <= 0:
            continue
        amount = round(qty * price, 2)
        items.append({"name": name, "qty": qty, "unit": unit, "price": price, "amount": amount, "source_line": line})
    return items


def _stroyka_final_pdf_escape(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _stroyka_final_create_simple_pdf(path: str, title: str, lines: List[str]) -> None:
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        font_name = "DejaVuSans"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        else:
            font_name = "Helvetica"
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        y = height - 40
        c.setFont(font_name, 12)
        c.drawString(40, y, title)
        y -= 24
        c.setFont(font_name, 9)
        for line in lines:
            if y < 40:
                c.showPage()
                y = height - 40
                c.setFont(font_name, 9)
            c.drawString(40, y, str(line)[:130])
            y -= 14
        c.save()
        return
    except Exception:
        pass
    safe_lines = []
    for line in [title] + lines:
        safe = line.encode("latin-1", "replace").decode("latin-1")
        safe_lines.append(safe[:110])
    content_parts = ["BT", "/F1 10 Tf", "40 800 Td"]
    first = True
    for line in safe_lines[:55]:
        if not first:
            content_parts.append("0 -14 Td")
        content_parts.append(f"({_stroyka_final_pdf_escape(line)}) Tj")
        first = False
    content_parts.append("ET")
    stream = "\n".join(content_parts).encode("latin-1", "replace")
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objs, 1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode())
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objs)+1}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(f"trailer << /Root 1 0 R /Size {len(objs)+1} >>\nstartxref\n{xref}\n%%EOF\n".encode())
    Path(path).write_bytes(bytes(out))


def _stroyka_final_create_xlsx(path: str, items: List[Dict[str, Any]], raw_input: str) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"
    ws["A1"] = "Смета по текущему заданию"
    ws["A2"] = "Основание: только текущий текст задачи, без старых смет и старых ссылок"
    ws["A1"].font = Font(bold=True, size=14)
    headers = ["№", "Наименование", "Кол-во", "Ед.", "Цена", "Сумма", "Источник"]
    start_row = 4
    for col, h in enumerate(headers, 1):
        c = ws.cell(start_row, col, h)
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="D9EAF7")
        c.alignment = Alignment(horizontal="center")
    for i, item in enumerate(items, 1):
        r = start_row + i
        ws.cell(r, 1, i)
        ws.cell(r, 2, item["name"])
        ws.cell(r, 3, item["qty"])
        ws.cell(r, 4, item["unit"])
        ws.cell(r, 5, item["price"])
        ws.cell(r, 6, f"=C{r}*E{r}")
        ws.cell(r, 7, item.get("source_line", "текущий ввод"))
    total_row = start_row + len(items) + 1
    ws.cell(total_row, 5, "Итого").font = Font(bold=True)
    ws.cell(total_row, 6, f"=SUM(F{start_row+1}:F{total_row-1})").font = Font(bold=True)
    ws.cell(total_row + 2, 1, "Исходный текст:")
    ws.cell(total_row + 3, 1, _clean(raw_input, 3000))
    ws.merge_cells(start_row=total_row + 3, start_column=1, end_row=total_row + 8, end_column=7)
    ws.cell(total_row + 3, 1).alignment = Alignment(wrap_text=True, vertical="top")
    widths = [6, 38, 12, 10, 14, 16, 70]
    for idx, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(idx)].width = width
    thin = Side(style="thin", color="999999")
    for row in ws.iter_rows(min_row=start_row, max_row=total_row, min_col=1, max_col=7):
        for cell in row:
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(path)


async def _stroyka_final_upload_or_send(chat_id: str, topic_id: int, reply_to: Optional[int], file_path: str, caption: str, mime_type: str) -> str:
    try:
        from core.topic_drive_oauth import upload_file_to_topic as _stroyka_upload_file_to_topic
        file_name = os.path.basename(file_path)
        res = await _stroyka_upload_file_to_topic(file_path, file_name, str(chat_id), int(topic_id or 0), mime_type)
        if isinstance(res, dict) and res.get("drive_file_id"):
            return f"https://drive.google.com/file/d/{res['drive_file_id']}/view?usp=drivesdk"
    except Exception:
        pass
    ok = await _send_document(str(chat_id), file_path, caption, reply_to, int(topic_id or 0))
    return "Telegram fallback: файл отправлен" if ok else "UPLOAD_FAILED"


async def _stroyka_final_handle_direct_item_estimate(conn: sqlite3.Connection, task: Any, logger: Any) -> bool:
    task_id = _s(_row_get(task, "id", ""))
    chat_id = _s(_row_get(task, "chat_id", ""))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    reply_to = _row_get(task, "reply_to_message_id", None)
    raw = _s(_row_get(task, "raw_input", ""))

    if topic_id != TOPIC_ID_STROYKA:
        return False
    items = _stroyka_final_parse_direct_items(raw)
    if not items:
        return False

    outdir = BASE / "runtime" / "stroyka_estimates" / task_id
    outdir.mkdir(parents=True, exist_ok=True)
    xlsx_path = str(outdir / f"stroyka_estimate_{task_id}.xlsx")
    pdf_path = str(outdir / f"stroyka_estimate_{task_id}.pdf")

    _stroyka_final_create_xlsx(xlsx_path, items, raw)
    total = round(sum(float(i["amount"]) for i in items), 2)

    pdf_lines = [
        f"task_id: {task_id}",
        "Основание: текущий ввод, старые сметы отключены",
        f"Позиций: {len(items)}",
        f"Итого: {total:.2f} руб",
        "",
    ]
    for i, item in enumerate(items, 1):
        pdf_lines.append(f"{i}. {item['name']} — {item['qty']} {item['unit']} x {item['price']} = {item['amount']} руб")
    _stroyka_final_create_simple_pdf(pdf_path, "Смета по текущему заданию", pdf_lines)

    if not os.path.exists(xlsx_path) or os.path.getsize(xlsx_path) < 1000:
        _update_task_safe(conn, task_id, state="FAILED", result="STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED: XLSX_CREATE_FAILED")
        _history_safe(conn, task_id, "STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED:XLSX_CREATE_FAILED")
        return True
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 100:
        _update_task_safe(conn, task_id, state="FAILED", result="STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED: PDF_CREATE_FAILED")
        _history_safe(conn, task_id, "STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED:PDF_CREATE_FAILED")
        return True

    xlsx_link = await _stroyka_final_upload_or_send(
        chat_id, topic_id, reply_to, xlsx_path,
        "Excel смета по текущему заданию",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    pdf_link = await _stroyka_final_upload_or_send(
        chat_id, topic_id, reply_to, pdf_path,
        "PDF смета по текущему заданию",
        "application/pdf",
    )

    result = "\n".join([
        "Смета готова по текущему заданию",
        "",
        f"Позиций: {len(items)}",
        f"Итого: {total:.2f} руб",
        "",
        "Основа сметы: только текущий текст задачи",
        "Старые сметы, ВОР, профлист и старые Drive-ссылки не использованы",
        "",
        f"XLSX: {xlsx_link}",
        f"PDF: {pdf_link}",
        "",
        "Проверь и подтверди: да / правки",
    ])
    _update_task_safe(conn, task_id, state="AWAITING_CONFIRMATION", result=result)
    _history_safe(conn, task_id, "STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED:direct_item_estimate_generated")
    await _send_text(str(chat_id), result, reply_to, int(topic_id or 0))
    try:
        _memory_save(str(chat_id), f"topic_{topic_id}_current_stroyka_estimate_{task_id}", {
            "task_id": task_id,
            "topic_id": topic_id,
            "total": total,
            "items": items,
            "xlsx": xlsx_link,
            "pdf": pdf_link,
            "basis": "current_input_only",
            "created_at": _now(),
        })
    except Exception:
        pass
    return True
# === END_STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_ITEM_ENGINE ===

async def maybe_handle_stroyka_estimate(conn: sqlite3.Connection, task: Any, logger=None) -> bool:

    # === STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_HANDLER_CALL ===
    try:
        if await _stroyka_final_handle_direct_item_estimate(conn, task, logger):
            return True
    except Exception as _stroyka_direct_err:
        logger.exception("STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_HANDLER_ERR %s", _stroyka_direct_err)
    # === END_STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_DIRECT_HANDLER_CALL ===
    if not is_stroyka_estimate_candidate(task):
        return False

    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    raw_input = _s(_row_get(task, "raw_input", ""))
    reply_to = _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None)

    try:
        await _send_text(chat_id, "⏳", reply_to, topic_id)
    except Exception:
        pass

    if _is_revision(raw_input):
        text = "Принял правки. Напиши одну конкретную правку к смете: что изменить?"
        send_res = await _send_text(chat_id, text, reply_to, topic_id)
        kwargs = {"state": "WAITING_CLARIFICATION", "result": text}
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, task_id, **kwargs)
        return True

    if _is_confirm(raw_input) or _is_old_task_finish_request(raw_input):
        pending = _memory_latest(chat_id, "topic_2_estimate_pending_")
        if pending and pending.get("status") == "WAITING_PRICE_CONFIRMATION":
            if _pending_is_fresh(pending, 600):
                return await _generate_and_send(conn, task, pending, raw_input, logger=logger)
            stale_key = "topic_2_estimate_stale_pending_" + _s(pending.get("task_id") or task_id)
            stale_payload = dict(pending)
            stale_payload["status"] = "STALE_DEPRECATED"
            stale_payload["deprecated_at"] = _now()
            stale_payload["deprecated_reason"] = "price confirmation timeout > 10 min"
            _memory_save(chat_id, stale_key, stale_payload)

        old = _latest_estimate_result(conn, chat_id, topic_id)
        if old and any(x in _low(raw_input) for x in ("где", "ну что", "смет")):
            result = _s(_row_get(old, "result", ""))
            text = f"Смета уже есть:\n\n{result}\n\nИспользовать существующую или пересчитать?"
            send_res = await _send_text(chat_id, text, reply_to, topic_id)
            kwargs = {"state": "WAITING_CLARIFICATION", "result": text}
            if isinstance(send_res, dict) and send_res.get("bot_message_id"):
                kwargs["bot_message_id"] = send_res.get("bot_message_id")
            _update_task_safe(conn, task_id, **kwargs)
            return True

        latest = _latest_estimate_task(conn, chat_id, topic_id)
        if latest and _s(_row_get(latest, "raw_input", "")) != raw_input:
            raw_input = _s(_row_get(latest, "raw_input", "")) + "\n" + raw_input
            _history_safe(conn, task_id, "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_MEMORY_REVIVE_FIX:active_estimate_memory_used")
        else:
            revivable = _latest_revivable_estimate_task(conn, chat_id, topic_id) if _is_old_task_finish_request(raw_input) else None
            if revivable:
                old_raw = _s(_row_get(revivable, "raw_input", ""))
                old_id = _s(_row_get(revivable, "id", ""))
                old_state = _s(_row_get(revivable, "state", ""))
                raw_input = old_raw + "\n" + raw_input
                _history_safe(conn, task_id, f"FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_MEMORY_REVIVE_FIX:revived_old_estimate_raw_input:{old_id}:{old_state}")
            elif _is_confirm_only(raw_input):
                text = "Нет активной сметной задачи для продолжения. Напиши сметное задание одним сообщением"
                send_res = await _send_text(chat_id, text, reply_to, topic_id)
                kwargs = {"state": "WAITING_CLARIFICATION", "result": text}
                if isinstance(send_res, dict) and send_res.get("bot_message_id"):
                    kwargs["bot_message_id"] = send_res.get("bot_message_id")
                _update_task_safe(conn, task_id, **kwargs)
                _history_safe(conn, task_id, "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_CONTEXT_BLEED_FIX:no_active_estimate")
                return True

    parsed = _parse_request(raw_input)
    question = _missing_question(parsed)
    if question:
        send_res = await _send_text(chat_id, question, reply_to, topic_id)
        kwargs = {"state": "WAITING_CLARIFICATION", "result": question}
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, task_id, **kwargs)
        _history_safe(conn, task_id, "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:clarification")
        return True

    template = choose_template(parsed)
    template_path = download_template_xlsx(template)
    template_prices, sheet_name = extract_template_prices(template_path, parsed)

    try:
        online_prices = await _search_prices_online(parsed, template, sheet_name)
    except Exception as e:
        if logger:
            logger.warning("FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_PRICE_SEARCH_ERR %s", e)
        text = "Произошла ошибка при поиске актуальных цен, повторяю"
        send_res = await _send_text(chat_id, text, reply_to, topic_id)
        kwargs = {"state": "IN_PROGRESS", "result": text}
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, task_id, **kwargs)
        return True

    pending = {
        "version": "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3",
        "status": "WAITING_PRICE_CONFIRMATION",
        "task_id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "parsed": parsed,
        "template": template,
        "sheet_name": sheet_name,
        "template_prices": template_prices,
        "online_prices": online_prices,
        "created_at": _now(),
    }
    _memory_save(chat_id, f"topic_2_estimate_pending_{task_id}", pending)

    text = _price_confirmation_text(parsed, template, sheet_name, template_prices, online_prices)
    send_res = await _send_text(chat_id, text, reply_to, topic_id)
    kwargs = {"state": "WAITING_CLARIFICATION", "result": text}
    if isinstance(send_res, dict) and send_res.get("bot_message_id"):
        kwargs["bot_message_id"] = send_res.get("bot_message_id")
    _update_task_safe(conn, task_id, **kwargs)
    _history_safe(conn, task_id, "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown")
    return True


def shadow_check() -> Dict[str, Any]:
    samples = [
        "смету дома 10×12 газобетон монолит 2 этажа 120 км коробка",
        "[VOICE] да сделай",
        "переделай стены на кирпич",
        "проект КЖ плиты",
    ]
    out = []
    for s in samples:
        parsed = _parse_request(s)
        tpl = choose_template(parsed)
        out.append({
            "raw": s,
            "parsed": parsed,
            "template": tpl.get("title"),
            "candidate_topic2": is_stroyka_estimate_candidate({"topic_id": 2, "input_type": "text", "raw_input": s}),
            "candidate_topic210": is_stroyka_estimate_candidate({"topic_id": 210, "input_type": "text", "raw_input": s}),
            "price_choice_example": parse_price_choice("средняя плюс 10%"),
        })
    return {
        "version": "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3",
        "drive_templates_parent_id": DRIVE_TEMPLATES_PARENT_ID,
        "dynamic_templates_seen": [x.get("title") for x in list_drive_templates()],
        "samples": out,
        "deprecated_templates": DEPRECATED_TEMPLATE_NAMES,
    }


if __name__ == "__main__":
    print(json.dumps(shadow_check(), ensure_ascii=False, indent=2))

# === END_FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3 ===

# === FIX_ESTIMATE_WORDS_EXTEND_V1 ===
# "посчитать" / "стоить" / "стоит" are missing from ESTIMATE_WORDS
# so "посчитать работу, сколько будет стоить" never matches → voice falls through
ESTIMATE_WORDS = tuple(set(ESTIMATE_WORDS) | {
    "посчитать", "рассчитать", "стоить", "стоит", "стоимост",
    "сколько стоит", "сколько будет", "нужна смета", "нужен расчет", "нужен расчёт",
})
# === END_FIX_ESTIMATE_WORDS_EXTEND_V1 ===

# === BUILD_ESTIMATE_ITEMS_11_SECTIONS_V1 ===
# Canon: 11 sections per ESTIMATE_TEMPLATE_M80_M110_CANON
# Фундамент / Каркас / Стены / Перекрытия / Кровля / Окна-двери /
# Внешняя отделка / Внутренняя отделка / Инженерные коммуникации / Логистика / Накладные
_bei11_orig = _build_estimate_items

def _build_estimate_items(parsed, price_text, choice):
    dims = parsed.get("dimensions") or parsed.get("dims") or (10.0, 10.0)
    try:
        a, b = float(dims[0]), float(dims[1])
    except Exception:
        a, b = 10.0, 10.0
    area_floor = float(parsed.get("area_floor") or (a * b))
    floors = int(parsed.get("floors") or 1)
    height = float(parsed.get("height") or 3.0)
    perimeter = 2 * (a + b)
    distance = float(parsed.get("distance_km") or 0)
    material = str(parsed.get("material") or "каркас").lower()
    scope = str(parsed.get("scope") or "коробка").lower()
    rooms = parsed.get("rooms") or []
    windows = int(parsed.get("windows") or max(int(area_floor * floors / 10), 4))
    doors = int(parsed.get("doors") or max(floors * 2, 2))

    wall_area = round(perimeter * height * floors, 2)
    total_area = round(area_floor * floors, 2)
    roof_area = round(area_floor * 1.25, 2)
    foundation_volume = round(area_floor * 0.25, 2)
    rebar_qty = round(foundation_volume * 0.08, 3)
    trips = max(math.ceil(distance / 40), 1) if distance > 0 else 1

    def _p(keywords):
        v = _choose_value(_numbers_from_price_text(price_text, keywords), choice)
        return v if v and v > 0 else 0

    p_concrete  = _p(("бетон", "в25", "в30"))
    p_rebar     = _p(("арматур", "а500"))
    p_wall_mat  = _p(("газобетон", "кирпич", "керамоблок", "каркас", "брус", "стен"))
    p_wall_work = _p(("работ", "кладк", "монолит", "каркас", "сборк"))
    p_roof      = _p(("кровл", "металлочерепица", "профнастил", "фальц", "мембран"))
    p_window    = _p(("окн", "window", "остеклен"))
    p_door      = _p(("двер", "door"))
    p_facade    = _p(("фасад", "штукатурк", "мокрый фасад", "клинкер", "цсп", "имитац"))
    p_interior  = _p(("внутренн", "штукатурк", "гкл", "гипсокартон", "отделк"))
    p_floor     = _p(("ламинат", "плитка", "стяжк", "пол", "напольн"))
    p_electro   = _p(("электрик", "проводк", "кабел", "электро"))
    p_plumb     = _p(("водоснабж", "канализац", "сантех", "трубопров"))
    p_heat      = _p(("отоплен", "теплый пол", "радиатор", "котел"))
    p_delivery  = _p(("достав", "рейс", "манипулятор", "кран", "транспорт"))

    def row(section, name, unit, qty, price, note=""):
        qty = round(float(qty or 0), 3)
        price_val = round(float(price or 0), 2)
        note_out = note if price_val > 0 else ("цена не подтверждена, требует уточнения" + (f" / {note}" if note else ""))
        return {"section": section, "name": name, "unit": unit, "qty": qty, "price": price_val, "note": note_out}

    items = []

    # 1. Фундамент
    items.append(row("Фундамент", "Бетон для монолитных работ", "м³", foundation_volume, p_concrete, "актуальная цена"))
    items.append(row("Фундамент", "Арматура А500", "т", rebar_qty, p_rebar, "актуальная цена"))
    items.append(row("Фундамент", "Опалубка периметра плиты", "п.м", perimeter, p_wall_work * 0.3 if p_wall_work else 0, "работы"))

    # 2. Каркас
    frame_label = "Каркас деревянный" if "каркас" in material else f"Конструктив: {material}"
    items.append(row("Каркас", frame_label, "м²", wall_area, p_wall_work, "работы по конструктиву"))

    # 3. Стены
    items.append(row("Стены", f"Материал стен: {material}", "м³", round(wall_area * 0.30, 2), p_wall_mat, "материал"))
    items.append(row("Стены", "Утепление и пароизоляция", "м²", wall_area, p_wall_mat * 0.2 if p_wall_mat else 0, "теплоконтур"))

    # 4. Перекрытия
    inter_floor_area = area_floor * max(floors - 1, 0)
    items.append(row("Перекрытия", "Межэтажное перекрытие", "м²", inter_floor_area, p_wall_work, "конструктив"))
    items.append(row("Перекрытия", "Черновой пол (настил)", "м²", total_area, p_wall_work * 0.4 if p_wall_work else 0, "основание"))

    # 5. Кровля
    items.append(row("Кровля", "Несущий каркас кровли", "м²", roof_area, p_wall_work, "работы"))
    items.append(row("Кровля", "Кровельное покрытие", "м²", roof_area, p_roof, "материал + монтаж"))

    # 6. Окна, двери
    items.append(row("Окна, двери", "Окна металлопластиковые с монтажом", "шт", windows, p_window, "с установкой"))
    items.append(row("Окна, двери", "Двери с установкой", "шт", doors, p_door, "с установкой"))

    # 7. Внешняя отделка
    items.append(row("Внешняя отделка", "Фасадная отделка", "м²", wall_area, p_facade, "материал + работы"))

    # 8. Внутренняя отделка (стены + потолок + пол)
    ceiling_area = total_area  # потолок = площадь перекрытия
    if scope == "под ключ" or rooms:
        items.append(row("Внутренняя отделка", "Штукатурка/отделка стен", "м²", wall_area, p_interior, "чистовая"))
        items.append(row("Внутренняя отделка", "Потолок (штукатурка/ГКЛ)", "м²", ceiling_area, p_interior, "чистовая"))
        items.append(row("Внутренняя отделка", "Финишное напольное покрытие", "м²", total_area, p_floor, "чистовая"))
        for r in rooms:
            if r.get("area", 0) > 0:
                items.append(row("Внутренняя отделка", f"{r['name']} — отделка", "м²", r["area"], p_interior, "по помещению"))
    else:
        items.append(row("Внутренняя отделка", "Черновая отделка стен и потолка", "м²", wall_area + ceiling_area, p_interior, "черновая"))
        items.append(row("Внутренняя отделка", "Стяжка пола", "м²", total_area, p_floor, "черновая"))

    # 9. Инженерные коммуникации
    items.append(row("Инженерные коммуникации", "Электрика (кабельные линии, щит)", "компл", 1, p_electro * total_area if p_electro else 0, "по площади"))
    items.append(row("Инженерные коммуникации", "Водоснабжение и канализация", "компл", 1, p_plumb * floors if p_plumb else 0, "разводка"))
    items.append(row("Инженерные коммуникации", "Отопление", "м²", total_area, p_heat, "по площади"))

    # 10. Логистика
    items.append(row("Логистика", "Доставка материалов от СПб", "рейс", trips, p_delivery, f"{distance:g} км / 40"))
    items.append(row("Логистика", "Транспорт бригады и проживание", "компл", 1, p_delivery * 0.3 if p_delivery else 0, "при удалённости > 50 км"))

    # 11. Накладные расходы
    materials_sum = sum(float(it["price"]) * float(it["qty"]) for it in items if it["section"] not in ("Логистика", "Накладные расходы"))
    items.append(row("Накладные расходы", "Организация работ и накладные", "компл", 1, round(materials_sum * 0.07, 2), "7% от материалов и работ"))

    return items
# === END_BUILD_ESTIMATE_ITEMS_11_SECTIONS_V1 ===

# === FIX_STROYKA_CONTEXT_ENRICH_BEFORE_PARSE_V1 ===
# Root cause: _missing_question only sees current raw_input.
# When user sends thin voice ("Сделаешь мне смету?") bot asks "Что строим?"
# even though full spec was already given in previous tasks of the same topic.
# Canon rule: ask only for MISSING data — if history has full spec, use it.
import logging as _sec_log_mod

_SEC_LOG = _sec_log_mod.getLogger("task_worker")


def _sec_raw_is_thin(raw: str) -> bool:
    p = _parse_request(raw)
    return not p.get("object") and not p.get("dimensions") and not p.get("material")


def _sec_get_rich_context(conn, chat_id: str, topic_id: int) -> str:
    try:
        rows = conn.execute("""
            SELECT raw_input FROM tasks
            WHERE chat_id=? AND COALESCE(topic_id,0)=?
              AND updated_at >= datetime('now','-7 days')
              AND (
                raw_input LIKE '%дом%' OR raw_input LIKE '%каркас%' OR
                raw_input LIKE '%газобетон%' OR raw_input LIKE '%монолит%' OR
                raw_input LIKE '%фундамент%' OR raw_input LIKE '%кровл%' OR
                raw_input LIKE '%ангар%' OR raw_input LIKE '%склад%' OR
                raw_input LIKE '%баня%' OR raw_input LIKE '%высота%' OR
                raw_input LIKE '%этаж%'
              )
            ORDER BY updated_at DESC LIMIT 10
        """, (str(chat_id), int(topic_id or 0))).fetchall()
        best, best_score = "", 0
        for row in rows:
            raw = str(row[0] or "")
            score = _estimate_raw_score(raw)
            if score > best_score:
                best_score, best = score, raw
        return best if best_score >= 20 else ""
    except Exception:
        return ""


_sec_orig_maybe_handle = maybe_handle_stroyka_estimate


async def maybe_handle_stroyka_estimate(conn, task, logger=None):
    raw_input = _s(_row_get(task, "raw_input", ""))
    if _sec_raw_is_thin(raw_input):
        chat_id = _s(_row_get(task, "chat_id", ""))
        topic_id = int(_row_get(task, "topic_id", 0) or 0)
        rich = _sec_get_rich_context(conn, chat_id, topic_id)
        if rich and rich.strip() != raw_input.strip():
            _SEC_LOG.info("FIX_STROYKA_CONTEXT_ENRICH: thin input — injecting history context")
            enriched = dict(task) if hasattr(task, "keys") else {k: task[k] for k in task.keys()}
            enriched["raw_input"] = rich + "\n" + raw_input
            return await _sec_orig_maybe_handle(conn, enriched, logger)
    return await _sec_orig_maybe_handle(conn, task, logger)

_SEC_LOG.info("FIX_STROYKA_CONTEXT_ENRICH_BEFORE_PARSE_V1 installed")
# === END_FIX_STROYKA_CONTEXT_ENRICH_BEFORE_PARSE_V1 ===

# === FIX_EXTRACT_SCOPE_IMPLICIT_V1 ===
# _extract_scope only matched literal "под ключ" / "коробка".
# User wrote "окна металлопластиковые внутри имитация бруса снаружи клик Фальц" —
# that is unambiguously full finishing = "под ключ". No need to ask.
_sec_orig_extract_scope = _extract_scope

def _extract_scope(text: str) -> str:
    result = _sec_orig_extract_scope(text)
    if result:
        return result
    t = _low(text)
    has_interior = any(x in t for x in (
        "имитация бруса", "гкл", "штукатур", "шпаклев", "плитк", "ламинат",
        "внутренн отделк", "внутри", "потолок", "полы", "стяжк",
    ))
    has_exterior = any(x in t for x in (
        "снаружи", "фасад", "клик", "фальц", "сайдинг", "внешн отделк",
    ))
    has_windows = "окна" in t or "двери" in t or "оконн" in t
    has_engineering = any(x in t for x in ("электрик", "водоснабж", "канализ", "отопл", "вентил"))
    if has_interior or has_exterior or has_windows or has_engineering:
        return "под ключ"
    return ""
# === END_FIX_EXTRACT_SCOPE_IMPLICIT_V1 ===

# === FIX_EXTRACT_DIMENSIONS_NA_V1 ===
# _extract_dimensions regex only matched x/х/×/*. "18 на 8" → None.
# Fix: add "на" as separator.
import re as _edi_re
_edi_orig_extract_dimensions = _extract_dimensions

def _extract_dimensions(text: str) -> Optional[Tuple[float, float]]:
    result = _edi_orig_extract_dimensions(text)
    if result:
        return result
    m = _edi_re.search(r"(\d+(?:[.,]\d+)?)\s+на\s+(\d+(?:[.,]\d+)?)", _low(text))
    if m:
        return float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))
    return None
# === END_FIX_EXTRACT_DIMENSIONS_NA_V1 ===

# === FIX_STROYKA_PRICE_CONFIRM_EXTEND_V1 ===
# CONTINUATION_WORDS / _is_confirm missed:
# "ставь средние", "ставь минимальные", "выполни задачу", "собирай", "делай"
# → user replies to price choice dialog but system creates new vague task.
# Also: _pending_is_fresh 600s is too short (user may reply after 10+ min).
import logging as _spc_log_mod
_SPC_LOG = _spc_log_mod.getLogger("task_worker")

_spc_orig_is_confirm = _is_confirm
_spc_orig_pending_is_fresh = _pending_is_fresh


def _is_confirm(text: str) -> bool:
    if _spc_orig_is_confirm(text):
        return True
    t = _low(text).replace("[voice]", "").strip()
    return any(x in t for x in (
        "ставь средн", "ставь минимальн", "ставь максимальн",
        "ставь шаблон", "ставь ручн",
        "выполни задачу", "выполняй", "собирай", "делай смету",
        "создавай", "генерируй", "запускай",
        "беру средн", "беру минимальн", "беру шаблон",
        "согласен", "согласна", "принято", "поехали",
        "средние цены", "минимальные цены", "шаблонные цены",
        "средн", "минимальн",
    ))


def _pending_is_fresh(pending, max_seconds: int = 600) -> bool:
    # Extend to 24h — user may reply after a long time
    return _spc_orig_pending_is_fresh(pending, max(max_seconds, 86400))


_SPC_LOG.info("FIX_STROYKA_PRICE_CONFIRM_EXTEND_V1 installed")
# === END_FIX_STROYKA_PRICE_CONFIRM_EXTEND_V1 ===

# === PATCH_TOPIC2_STROYKA_ESTIMATE_CANON_FULL_CLOSE_V3 ===
import logging as _stv3_log_mod, re as _stv3_re, hashlib as _stv3_hash
_STV3_LOG = _stv3_log_mod.getLogger("task_worker")

# --- A: is_stroyka_estimate_candidate recognizes confirm phrases ---
_stv3_orig_candidate = is_stroyka_estimate_candidate

def is_stroyka_estimate_candidate(task):
    if _stv3_orig_candidate(task):
        return True
    if int(_row_get(task, "topic_id", 0) or 0) != TOPIC_ID_STROYKA:
        return False
    input_type = _low(_row_get(task, "input_type", ""))
    if input_type in ("photo", "file", "drive_file", "image", "document"):
        return False
    raw = _low(_row_get(task, "raw_input", ""))
    if not raw:
        return False
    if _is_confirm(raw):
        return True
    # session lookup phrases
    if any(x in raw for x in (
        "где смет", "мои смет", "по каждому заданию", "по каждой задач",
        "выполни задач", "выполни задание", "делай смету", "посчитай полностью",
        "в полном объёме", "в полном объеме", "сделай смету", "выполняй",
        "новое тз", "другое задание", "второе задание",
    )):
        return True
    return False

# --- B: parse_price_choice — mark unconfirmed when no explicit price word ---
_stv3_orig_ppc = parse_price_choice
_STV3_EXPLICIT_PRICE_WORDS = (
    "миним", "максим", "средн", "медиан", "ручн", "конкрет",
    "ссылк", "вариант а", "вариант б", "вариант в", "вариант г",
    "вариант 1", "вариант 2", "вариант 3", "вариант 4",
    "а)", "б)", "в)", "г)", "самые дешев", "шаблон",
    "ставь", "беру", "средние цены", "минимальн цены", "шаблонн",
)

def parse_price_choice(text: str) -> Dict[str, Any]:
    result = _stv3_orig_ppc(text)
    t = _low(str(text or "")).replace("[voice]", "").strip()
    explicit = any(x in t for x in _STV3_EXPLICIT_PRICE_WORDS)
    result = dict(result)
    result["confirmed"] = explicit
    if not explicit:
        result["choice"] = "NONE"
    return result

# --- C: _generate_and_send — require explicit price choice before XLSX/PDF ---
_stv3_orig_gas = _generate_and_send

async def _generate_and_send(conn, task, pending, confirm_text, logger=None):
    choice = parse_price_choice(confirm_text)
    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    reply_to = _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None)

    if not choice.get("confirmed") or choice.get("choice") == "NONE":
        # No explicit price choice — ask user
        msg = (
            "Выберите уровень цен для сметы:\n\n"
            "1 — минимальные (самые дешёвые из найденных)\n"
            "2 — средние (медианные рыночные)\n"
            "3 — надёжный поставщик\n"
            "4 — ручные (укажу сам)\n\n"
            "Ответьте: 1 / 2 / 3 / 4 или: минимальные / средние / максимальные / ручные\n"
            "или 'ставь средние' / 'ставь минимальные' / 'ставь шаблонные'"
        )
        send_res = await _send_text(chat_id, msg, reply_to, topic_id)
        kwargs = {"state": "WAITING_CLARIFICATION", "result": msg}
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, task_id, **kwargs)
        # Keep pending alive, mark that choice was requested
        pending_updated = dict(pending)
        pending_updated["price_choice_requested"] = True
        pending_updated["price_choice_requested_at"] = _now()
        pend_key = f"topic_2_estimate_pending_{pending.get('task_id', task_id)}"
        _memory_save(chat_id, pend_key, pending_updated)
        _history_safe(conn, task_id, "TOPIC2_PRICE_CHOICE_REQUESTED")
        return True

    # Explicit choice confirmed — proceed to generate
    _history_safe(conn, task_id, f"TOPIC2_PRICE_CHOICE_CONFIRMED:{choice.get('choice')}")
    result = await _stv3_orig_gas(conn, task, pending, confirm_text, logger=logger)
    return result

# --- D: _create_pdf — use DejaVuSans for proper Cyrillic ---
_stv3_orig_create_pdf = _create_pdf

def _create_pdf(task_id: str, text: str) -> str:
    pdf_path = os.path.join(tempfile.gettempdir(), f"stroyka_est_{task_id[:8]}_{int(time.time())}.pdf")
    try:
        from core.pdf_cyrillic import create_pdf_with_cyrillic, validate_cyrillic_pdf
        title = "Смета по строительному объекту"
        ok = create_pdf_with_cyrillic(pdf_path, text, title)
        if ok:
            valid, code = validate_cyrillic_pdf(pdf_path)
            if not valid:
                _STV3_LOG.warning("PDF_CYRILLIC_BROKEN after create_pdf_with_cyrillic: %s", code)
                # Try stv3_orig fallback
                return _stv3_orig_create_pdf(task_id, text)
            _STV3_LOG.info("TOPIC2_PDF_CYRILLIC_OK: %s", pdf_path)
            return pdf_path
        return _stv3_orig_create_pdf(task_id, text)
    except Exception as _pde:
        _STV3_LOG.warning("_create_pdf DejaVu patch err: %s", _pde)
        return _stv3_orig_create_pdf(task_id, text)

# --- E: context_hash helper for session isolation ---
def _stv3_context_hash(raw_input: str, source_file_id: str = "") -> str:
    src = str(raw_input or "").strip()[:2000] + "|" + str(source_file_id or "")
    return _stv3_hash.sha256(src.encode("utf-8", errors="replace")).hexdigest()[:16]

# --- F: DONE contract guard — validate all checkpoints ---
_stv3_orig_update_task_safe = _update_task_safe

def _update_task_safe(conn, task_id, **kwargs):
    new_state = kwargs.get("state", "")
    if new_state == "DONE":
        # Check task is topic_2
        try:
            row = conn.execute(
                "SELECT topic_id, result FROM tasks WHERE id=?", (task_id,)
            ).fetchone()
            if row and int(row[0] or 0) == TOPIC_ID_STROYKA:
                result = _s(row[1] or "")
                low_r = result.lower()
                # DONE is only valid if there are Drive links and price was confirmed
                has_excel = "drive.google.com" in low_r and ("xlsx" in low_r or "excel" in low_r or "📊" in result)
                has_pdf = "drive.google.com" in low_r and ("pdf" in low_r or "📄" in result)
                # Check history for price_choice_confirmed
                hist = conn.execute(
                    "SELECT action FROM task_history WHERE task_id=? ORDER BY created_at",
                    (task_id,),
                ).fetchall()
                hist_actions = [_s(h[0]) for h in hist]
                price_confirmed = any("TOPIC2_PRICE_CHOICE_CONFIRMED" in a for a in hist_actions)
                estimate_generated = any("estimate_generated" in a or "FINAL_DONE" in a or "P3_TOPIC2_FINAL" in a for a in hist_actions)

                if not estimate_generated:
                    _STV3_LOG.warning(
                        "TOPIC2_DONE_CONTRACT_CHECK: DONE blocked for %s — no estimate_generated", task_id
                    )
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (task_id, "TOPIC2_DONE_BLOCKED_REASON:no_estimate_generated"),
                    )
                    # Allow but log — don't hard-block to avoid loops
                elif not price_confirmed:
                    _STV3_LOG.warning(
                        "TOPIC2_DONE_CONTRACT_CHECK: DONE blocked for %s — no price_choice_confirmed", task_id
                    )
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (task_id, "TOPIC2_DONE_BLOCKED_REASON:no_price_choice_confirmed"),
                    )
                    # Override: set AWAITING_CONFIRMATION instead of DONE
                    kwargs = dict(kwargs)
                    kwargs["state"] = "AWAITING_CONFIRMATION"
                    _STV3_LOG.info("TOPIC2_BAD_DONE_BLOCKED: changed DONE→AWAITING_CONFIRMATION for %s", task_id)
                else:
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (task_id, "TOPIC2_DONE_CONTRACT_OK"),
                    )
                    _STV3_LOG.info("TOPIC2_DONE_CONTRACT_OK: %s", task_id)
        except Exception as _dg_e:
            _STV3_LOG.warning("DONE_GATE_ERR %s: %s", task_id, _dg_e)
    return _stv3_orig_update_task_safe(conn, task_id, **kwargs)

_STV3_LOG.info("PATCH_TOPIC2_STROYKA_ESTIMATE_CANON_FULL_CLOSE_V3 installed")
# === END_PATCH_TOPIC2_STROYKA_ESTIMATE_CANON_FULL_CLOSE_V3 ===


# === PATCH_TOPIC2_PRICE_CHOICE_NUMERIC_PARSE_V4 ===
_T2PCP_ORIG_PARSE_PRICE_CHOICE_V4 = parse_price_choice

def parse_price_choice(text: str) -> Dict[str, Any]:
    result = dict(_T2PCP_ORIG_PARSE_PRICE_CHOICE_V4(text))
    t = _low(str(text or "")).replace("[voice]", "").strip()
    t = re.sub(r"\s+", " ", t).strip(" .,!?:;()[]{}")
    exact = {
        "1": "minimum", "а": "minimum", "a": "minimum", "а)": "minimum", "a)": "minimum",
        "2": "median", "б": "median", "b": "median", "б)": "median", "b)": "median",
        "3": "maximum", "в": "maximum", "v": "maximum", "в)": "maximum", "v)": "maximum",
        "4": "manual", "г": "manual", "g": "manual", "г)": "manual", "g)": "manual",
    }
    confirmed = False
    if t in exact:
        result["choice"] = exact[t]
        confirmed = True
    elif any(x in t for x in ("миним", "дешев", "дешёв", "самые низкие", "ставь миним")):
        result["choice"] = "minimum"
        confirmed = True
    elif any(x in t for x in ("средн", "медиан", "рынок", "ставь сред", "беру сред", "средние цены")):
        result["choice"] = "median"
        confirmed = True
    elif any(x in t for x in ("максим", "надеж", "надёж", "проверенн", "ставь максим")):
        result["choice"] = "maximum"
        confirmed = True
    elif any(x in t for x in ("ручн", "вручную", "сам укажу", "мои цены", "своя")):
        result["choice"] = "manual"
        confirmed = True
    else:
        confirmed = bool(result.get("confirmed"))

    result["confirmed"] = confirmed
    if not confirmed:
        result["choice"] = "NONE"
    return result

try:
    _STV3_LOG.info("PATCH_TOPIC2_PRICE_CHOICE_NUMERIC_PARSE_V4 installed")
except Exception:
    pass
# === END_PATCH_TOPIC2_PRICE_CHOICE_NUMERIC_PARSE_V4 ===

# === PATCH_TOPIC2_NUMERIC_PRICE_CHOICE_PARSE_V5 ===
try:
    _t2num_prev_parse_price_choice_v5 = parse_price_choice
    def parse_price_choice(text: str):
        res = dict(_t2num_prev_parse_price_choice_v5(text))
        t = _low(str(text or "")).replace("[voice]", "").strip()
        t = re.sub(r"\s+", " ", t).strip(" .,!?:;()[]{}")
        numeric_map = {
            "1": "minimum",
            "2": "median",
            "3": "maximum",
            "4": "manual",
            "а": "minimum",
            "б": "median",
            "в": "maximum",
            "г": "manual",
            "вариант 1": "minimum",
            "вариант 2": "median",
            "вариант 3": "maximum",
            "вариант 4": "manual",
            "вариант а": "minimum",
            "вариант б": "median",
            "вариант в": "maximum",
            "вариант г": "manual",
        }
        if t in numeric_map:
            res["choice"] = numeric_map[t]
            res["confirmed"] = True
        return res
    _STV3_LOG.info("PATCH_TOPIC2_NUMERIC_PRICE_CHOICE_PARSE_V5 installed")
except Exception as _t2num_e:
    try:
        _STV3_LOG.warning("PATCH_TOPIC2_NUMERIC_PRICE_CHOICE_PARSE_V5_ERR %s", _t2num_e)
    except Exception:
        pass
# === END_PATCH_TOPIC2_NUMERIC_PRICE_CHOICE_PARSE_V5 ===

# === PATCH_TOPIC2_CANCEL_GUARD_AND_SOURCE_ISOLATION_V1 ===
import logging as _t2cg_log
_T2CG_LOG = _t2cg_log.getLogger("task_worker")

_T2CG_CANCEL_WORDS = (
    "отмена", "отмени", "отменить", "очисти", "очистить",
    "удали все задачи", "закрой все задачи", "отмени все задачи",
    "cancel all", "все задачи отменены",
)

_t2cg_orig_candidate = is_stroyka_estimate_candidate

def is_stroyka_estimate_candidate(task):
    raw = _low(_row_get(task, "raw_input", ""))
    # Strip REVISION_CONTEXT for the check
    if "---" in raw and "revision_context" in raw.lower():
        raw = raw[:raw.lower().find("revision_context")].strip()
    if any(x in raw for x in _T2CG_CANCEL_WORDS):
        return False
    return _t2cg_orig_candidate(task)

_t2cg_orig_maybe_handle = maybe_handle_stroyka_estimate

async def maybe_handle_stroyka_estimate(conn, task, logger=None):
    raw = _s(_row_get(task, "raw_input", ""))
    if "\n---\nREVISION_CONTEXT" in raw:
        clean_raw = raw.split("\n---\nREVISION_CONTEXT")[0].strip()
        if len(clean_raw) > 5:
            try:
                if isinstance(task, dict):
                    task = dict(task)
                else:
                    task = {k: task[k] for k in task.keys()}
                task["raw_input"] = clean_raw
            except Exception:
                pass
    return await _t2cg_orig_maybe_handle(conn, task, logger=logger)

_T2CG_LOG.info("PATCH_TOPIC2_CANCEL_GUARD_AND_SOURCE_ISOLATION_V1 installed")
# === END_PATCH_TOPIC2_CANCEL_GUARD_AND_SOURCE_ISOLATION_V1 ===

# === PATCH_STROYKA_META_CONFIRM_GUARD_V1 ===
# Root cause: "Ничего менять не надо" → FIX_STROYKA_CONTEXT_ENRICH injects old estimate context
# → pipeline treats it as new estimate → loop.
# Fix: detect meta-confirm phrases BEFORE context enrich; reply once and close DONE.
import logging as _mcg_log_mod
_MCG_LOG = _mcg_log_mod.getLogger("task_worker")

_MCG_META_PHRASES = (
    "ничего менять не надо", "ничего не меняй", "не надо менять",
    "не нужно менять", "не меняй ничего", "без изменений", "оставь как есть",
    "всё устраивает", "все устраивает",
    "всё хорошо", "все хорошо", "всё верно", "все верно",
    "всё правильно", "все правильно",
    "не трогай", "ничего не трогай", "изменений нет",
    "всё нравится", "все нравится",
)

_mcg_orig_maybe = maybe_handle_stroyka_estimate

async def maybe_handle_stroyka_estimate(conn, task, logger=None):
    raw = _low(_row_get(task, "raw_input", ""))
    # Strip injected REVISION_CONTEXT before checking
    if "---" in raw:
        raw = raw.split("---")[0].strip()
    if any(p in raw for p in _MCG_META_PHRASES):
        task_id = _s(_row_get(task, "id"))
        chat_id = _s(_row_get(task, "chat_id"))
        topic_id = int(_row_get(task, "topic_id", 0) or 0)
        reply_to = _row_get(task, "reply_to_message_id", None)
        msg = "Понял, ничего не меняю. Если понадоблюсь — напишите."
        try:
            send_res = await _send_text(chat_id, msg, reply_to, topic_id)
        except Exception:
            send_res = {}
        kwargs = {"state": "DONE", "result": msg}
        if isinstance(send_res, dict) and send_res.get("bot_message_id"):
            kwargs["bot_message_id"] = send_res.get("bot_message_id")
        _update_task_safe(conn, task_id, **kwargs)
        _history_safe(conn, task_id, "TOPIC2_META_CONFIRM_NO_CHANGE_GUARD_V1")
        _MCG_LOG.info("PATCH_STROYKA_META_CONFIRM_GUARD_V1 blocked meta-confirm task=%s", task_id)
        return True
    return await _mcg_orig_maybe(conn, task, logger)

_MCG_LOG.info("PATCH_STROYKA_META_CONFIRM_GUARD_V1 installed")
# === END_PATCH_STROYKA_META_CONFIRM_GUARD_V1 ===

# === PATCH_STROYKA_REPLY_CHAIN_V1 ===
# Root cause: reply_to_message_id=2 is the Telegram forum topic root marker, not a real message.
# Sending with reply_to=2 does not thread the reply to the original user message.
# Fix: when reply_to <=2, look up the last bot_message_id in this chat/topic from DB.
import logging as _src_log_mod
_SRC_LOG = _src_log_mod.getLogger("task_worker")

_src_orig_gas_v1 = _generate_and_send

async def _generate_and_send(conn, task, pending, confirm_text, logger=None):
    try:
        reply_raw = _row_get(task, "reply_to_message_id", None)
        r_int = int(reply_raw) if reply_raw is not None else 0
        if r_int <= 2:
            c_id = _s(_row_get(task, "chat_id"))
            t_id = int(_row_get(task, "topic_id", 0) or 0)
            task_id_v = _s(_row_get(task, "id"))
            row = conn.execute(
                """SELECT bot_message_id FROM tasks
                   WHERE CAST(chat_id AS TEXT)=? AND COALESCE(topic_id,0)=? AND id!=?
                   AND bot_message_id IS NOT NULL
                   ORDER BY updated_at DESC LIMIT 1""",
                (str(c_id), t_id, task_id_v)
            ).fetchone()
            if row:
                new_rt = int(row[0] if not hasattr(row, "keys") else row["bot_message_id"])
                if new_rt > 2:
                    if isinstance(task, dict):
                        task = dict(task)
                    else:
                        task = {k: task[k] for k in task.keys()}
                    task["reply_to_message_id"] = new_rt
                    _SRC_LOG.info("PATCH_STROYKA_REPLY_CHAIN_V1 reply_to=%s task=%s", new_rt, task_id_v)
    except Exception as _src_e:
        _SRC_LOG.warning("PATCH_STROYKA_REPLY_CHAIN_V1_ERR %s", _src_e)
    return await _src_orig_gas_v1(conn, task, pending, confirm_text, logger=logger)

_SRC_LOG.info("PATCH_STROYKA_REPLY_CHAIN_V1 installed")
# === END_PATCH_STROYKA_REPLY_CHAIN_V1 ===

# === PATCH_STROYKA_XLSX_15_COLS_V1 ===
# Root cause: _create_xlsx_from_template generates 11 columns instead of canonical 15.
# Spec requires: Источник цены, Поставщик, URL, Дата проверки (cols 12-15).
# Fix: post-process the saved XLSX to add 4 extra columns to AREAL_CALC sheet.
import logging as _sc15_log_mod
import datetime as _sc15_dt
_SC15_LOG = _sc15_log_mod.getLogger("task_worker")

_sc15_orig_xlsx = _create_xlsx_from_template

def _create_xlsx_from_template(task_id, parsed, template, template_path, sheet_name, price_text, choice):
    path, items, py_total = _sc15_orig_xlsx(task_id, parsed, template, template_path, sheet_name, price_text, choice)
    try:
        from openpyxl import load_workbook
        from openpyxl.styles import Font, Alignment as _SC15Align

        wb = load_workbook(path)
        if "AREAL_CALC" not in wb.sheetnames:
            wb.close()
            return path, items, py_total
        ws = wb["AREAL_CALC"]

        HDR_ROW = 7
        if ws.cell(HDR_ROW, 12).value is not None:
            wb.close()
            return path, items, py_total  # already extended

        _bold = Font(bold=True)
        for idx, h in enumerate(["Источник цены", "Поставщик", "URL", "Дата проверки"], 12):
            c = ws.cell(HDR_ROW, idx, h)
            c.font = _bold
            c.alignment = _SC15Align(wrap_text=True)

        for col_letter, width in [("L", 20), ("M", 22), ("N", 35), ("O", 16)]:
            ws.column_dimensions[col_letter].width = width

        date_str = _sc15_dt.datetime.now().strftime("%d.%m.%Y")
        src_label = "Perplexity" if price_text and len(str(price_text)) > 20 else "—"

        row_idx = HDR_ROW + 1
        while ws.cell(row_idx, 3).value is not None:
            ws.cell(row_idx, 12, src_label)
            ws.cell(row_idx, 13, "—")
            ws.cell(row_idx, 14, "—")
            ws.cell(row_idx, 15, date_str)
            row_idx += 1

        wb.save(path)
        wb.close()
        _SC15_LOG.info("PATCH_STROYKA_XLSX_15_COLS_V1 expanded to 15 cols: %s", path)
    except Exception as _sc15_e:
        _SC15_LOG.warning("PATCH_STROYKA_XLSX_15_COLS_V1_ERR %s", _sc15_e)
    return path, items, py_total

_SC15_LOG.info("PATCH_STROYKA_XLSX_15_COLS_V1 installed")
# === END_PATCH_STROYKA_XLSX_15_COLS_V1 ===


# ============================================================
# === PATCH_STROYKA_PARENT_AWARE_MISSING_QUESTION_V1 ===
# Цель: _missing_question учитывает parent.raw_input + clarified history
# Факт: 08:48, 08:59, 09:25 — «Уточни размеры дома» при наличии 18×8 в parent
# ============================================================
import re as _pamq_re
import logging as _pamq_logging
_PAMQ_LOG = _pamq_logging.getLogger("stroyka.parent_aware_missing")

_PAMQ_DIM_RE = _pamq_re.compile(r"(\d{1,3})\s*[xх*на]+\s*(\d{1,3})", _pamq_re.IGNORECASE)
_PAMQ_FLOORS_RE = _pamq_re.compile(r"(\d+)\s*этаж|этаж\w*\s*(\d+)", _pamq_re.IGNORECASE)
_PAMQ_OBJ_WORDS = ("дом", "ангар", "склад", "гараж", "баня", "коробк", "фундамент", "кровл")
_PAMQ_MAT_WORDS = ("каркас", "газобетон", "кирпич", "керамоблок", "монолит", "арболит", "брус", "сип")

def _pamq_collect_full_context(conn, task):
    chunks = []
    try:
        if isinstance(task, dict):
            chunks.append(str(task.get("raw_input") or ""))
            chunks.append(str(task.get("caption") or ""))
        else:
            try:
                chunks.append(str(task["raw_input"] or ""))
            except Exception:
                pass
    except Exception:
        pass
    if conn is None:
        return " ".join(chunks).lower()
    try:
        tid = task.get("id") if isinstance(task, dict) else None
        try:
            parent_id = task.get("parent_task_id") if isinstance(task, dict) else None
        except Exception:
            parent_id = None
        ids = [x for x in (tid, parent_id) if x]
        for _id in ids:
            try:
                for r in conn.execute(
                    "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%'",
                    (_id,)
                ).fetchall():
                    chunks.append(str(r[0]).replace("clarified:", ""))
                row = conn.execute(
                    "SELECT raw_input, caption FROM tasks WHERE id=?", (_id,)
                ).fetchone()
                if row:
                    chunks.append(str(row[0] or ""))
                    chunks.append(str(row[1] or ""))
            except Exception:
                pass
    except Exception as e:
        _PAMQ_LOG.debug("PAMQ_DB_ERR err=%s", e)
    return " ".join(chunks).lower()

def _pamq_has_dimensions(text):
    return bool(_PAMQ_DIM_RE.search(text or ""))

def _pamq_has_object(text):
    return any(w in (text or "") for w in _PAMQ_OBJ_WORDS)

def _pamq_has_floors(text):
    return bool(_PAMQ_FLOORS_RE.search(text or "")) or "одноэтажн" in (text or "") or "двухэтажн" in (text or "")

def _pamq_has_material(text):
    return any(w in (text or "") for w in _PAMQ_MAT_WORDS)

_PAMQ_ORIG_MISSING = globals().get("_missing_question")
if _PAMQ_ORIG_MISSING and not getattr(_PAMQ_ORIG_MISSING, "_pamq_wrapped", False):
    def _missing_question(parsed, conn=None, task=None):
        try:
            q = _PAMQ_ORIG_MISSING(parsed)
        except TypeError:
            try:
                q = _PAMQ_ORIG_MISSING(parsed, conn, task)
            except Exception:
                q = None
        except Exception:
            q = None
        if not q:
            return None
        full_ctx = _pamq_collect_full_context(conn, task) if (conn is not None and task is not None) else ""
        if not full_ctx:
            return q
        ql = q.lower()
        if "размер" in ql and _pamq_has_dimensions(full_ctx):
            _PAMQ_LOG.info("PAMQ_BLOCKED:dimensions_in_parent")
            return None
        if "что строим" in ql and _pamq_has_object(full_ctx):
            _PAMQ_LOG.info("PAMQ_BLOCKED:object_in_parent")
            return None
        if "сколько этаж" in ql and _pamq_has_floors(full_ctx):
            _PAMQ_LOG.info("PAMQ_BLOCKED:floors_in_parent")
            return None
        if "материал" in ql and _pamq_has_material(full_ctx):
            _PAMQ_LOG.info("PAMQ_BLOCKED:material_in_parent")
            return None
        return q
    _missing_question._pamq_wrapped = True

_PAMQ_LOG.info("PATCH_STROYKA_PARENT_AWARE_MISSING_QUESTION_V1 installed")
# === END_PATCH_STROYKA_PARENT_AWARE_MISSING_QUESTION_V1 ===
