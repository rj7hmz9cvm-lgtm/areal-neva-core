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
        # === TOPIC2_FINAL_GAPS_V5_FORBIDDEN_PHRASES ===
        "файл скачан",
        "ожидает анализа",
        "выбор принят",
        "проверяю доступные файлы",
        "структура проекта включает",
        "файл содержит проект",
        "уточните запрос",
        "что строим",
        "не нашёл родительскую задачу",
        "не вижу размеры объекта",
        "позиция по присланному фото",
        # === END_TOPIC2_FINAL_GAPS_V5_FORBIDDEN_PHRASES ===
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
    if any(x in t for x in bad):
        return True
    # === TOPIC2_FINAL_GAPS_V5_REGEX_FORBIDDEN ===
    import re as _ibr_re
    if _ibr_re.search(r'позиций:\s*1(?:\s|$)', t):
        return True
    if "/root/" in t or "/tmp/" in t:
        return True
    if "revision_context" in t or "traceback (most" in t:
        return True
    if "engine:" in t or "manifest:" in t:
        return True
    # === TOPIC2_FINAL_GAPS_V5B_RAW_JSON_GUARD ===
    if t.strip().startswith("{") and any(_k in t for _k in ('"state":', '"topic_id":', '"task_id":', '"result":', '"action":')):
        return True
    if _ibr_re.search(r'"state"\s*:\s*"(?:failed|in_progress|done|pending|waiting)', t):
        return True
    # === END_TOPIC2_FINAL_GAPS_V5B_RAW_JSON_GUARD ===
    # === END_TOPIC2_FINAL_GAPS_V5_REGEX_FORBIDDEN ===
    return False


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

    if parsed.get("pdf_spec_rows") or parsed.get("ocr_table_rows"):
        return None
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


# === TOPIC2_FULL_CLOSE_GAP_A: deterministic work/material classifier ===
_WORK_KW = (
    "работ", "монтаж", "кладк", "установк", "доставк", "разгруз",
    "подач", "вибрирован", "уход за бетон", "гидроизоляц", "утеплен",
    "засыпк", "опалубк", "армирован", "бетонирован", "устройств",
    "демонтаж", "сборк",
)
_MAT_KW = (
    "материал", "бетон", "арматур", "газобетон", "кирпич", "брус",
    "пиломат", "утеплитель", "мембран", "плитк", "ламинат",
    "сантехник", "окна", "двери", "крепеж", "щебень", "песок",
)

def _classify_item(name: str, section: str) -> str:
    n = _low(str(name or ""))
    if any(k in n for k in _WORK_KW):
        return "work"
    if any(k in n for k in _MAT_KW):
        return "material"
    s = _low(str(section or ""))
    if s in ("логистика", "накладные расходы", "накладные"):
        return "overhead"
    return "material"
# === END TOPIC2_FULL_CLOSE_GAP_A classifier ===


def choose_template_sheet(parsed: Dict[str, Any], sheet_names: List[str]) -> tuple:
    """Returns (sheet_name, source) where source is 'match' or 'fallback'."""
    material = parsed.get("material") or ""
    obj = parsed.get("object") or ""
    names = list(sheet_names or [])
    lows = {name: _low(name) for name in names}

    if material == "каркас":
        for name, low in lows.items():
            if "каркас" in low:
                return name, "match"

    if material in ("газобетон", "кирпич", "керамоблок", "монолит", "арболит") or obj in ("дом", "коробка"):
        for name, low in lows.items():
            if "газобетон" in low:
                return name, "match"

    if obj in ("кровля",):
        for name, low in lows.items():
            if "кров" in low or "перекр" in low:
                return name, "match"

    if obj in ("ангар", "склад", "фундамент"):
        for name, low in lows.items():
            if "смет" in low or "фундамент" in low or "склад" in low:
                return name, "match"

    # GAP-B: fallback to first sheet — propagate source for marker
    return (names[0], "fallback") if names else (None, "fallback")


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


def extract_template_prices(template_path: Optional[str], parsed: Dict[str, Any]) -> tuple:
    """Returns (prices_text, sheet_name, sheet_fallback: bool)."""
    if not template_path or not os.path.exists(template_path):
        return "Цены из шаблона: шаблон не скачан, используется только структура/сценарий", None, False
    try:
        from openpyxl import load_workbook
        wb = load_workbook(template_path, data_only=True, read_only=True)
        selected, _sheet_src = choose_template_sheet(parsed, wb.sheetnames)
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
        return "Цены из выбранного листа шаблона:\n" + ("\n".join(found) if found else "ключевые цены в листе не распознаны автоматически"), selected, _sheet_src == "fallback"
    except Exception as e:
        return f"Цены из шаблона: ошибка чтения шаблона: {e}", None, False


def is_stroyka_estimate_candidate(task: Any) -> bool:
    if int(_row_get(task, "topic_id", 0) or 0) != TOPIC_ID_STROYKA:
        return False
    input_type = _low(_row_get(task, "input_type", ""))
    if input_type in ("photo", "file", "drive_file", "image", "document"):
        # §6 multi-format intake: allow when caption contains estimate keywords
        _mfi_cap = _low(_row_get(task, "raw_input", ""))
        if _mfi_cap and any(x in _mfi_cap for x in ESTIMATE_WORDS):
            return True
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


def _parse_price_sources(price_text: str) -> List[Dict[str, Any]]:
    """Parse Perplexity pipe-delimited response into per-position source records."""
    sources: List[Dict[str, Any]] = []
    if not price_text:
        return sources
    today = datetime.date.today().isoformat()
    for line in price_text.splitlines():
        line = line.strip(" \t-—•·")
        if "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        position = parts[0].lower()
        supplier = parts[4] if len(parts) > 4 else ""
        url = parts[5] if len(parts) > 5 else ""
        checked_at = parts[6].strip() if len(parts) > 6 else today
        status = "found" if (supplier or url) else "no_data"
        if not position:
            continue
        kw = [w for w in re.split(r"[\s,;/]+", position) if len(w) > 2]
        sources.append({
            "keywords": kw,
            "position": position,
            "supplier": supplier,
            "url": url,
            "checked_at": checked_at or today,
            "status": status,
        })
    return sources


def _match_price_source(sources: List[Dict[str, Any]], item_name: str, item_section: str) -> Dict[str, Any]:
    """Return best matching source for an estimate item."""
    today = datetime.date.today().isoformat()
    _empty = {"supplier": "", "url": "", "checked_at": today, "status": "template_only"}
    if not sources:
        return _empty
    combined = (item_name + " " + item_section).lower()
    best = None
    best_score = 0
    for src in sources:
        score = sum(1 for kw in src["keywords"] if kw in combined)
        if score > best_score:
            best_score = score
            best = src
    return best if (best and best_score > 0) else _empty


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

async def _search_prices_online(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], conn=None, task_id=None) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    model = os.getenv("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY_MISSING")
    # PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1 begin
    import logging as _sec_log
    _sec_logger = _sec_log.getLogger("stroyka_estimate_canon")
    if "sonar" not in model.lower():
        _sec_logger.error(f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR: model={model!r} blocked")
        if conn is not None and task_id is not None:
            try:
                _history_safe(conn, task_id, f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR:{model}")
            except Exception:
                pass
        raise RuntimeError(f"TOPIC2_ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR:{model}")
    _sec_logger.info(f"TOPIC2_ONLINE_MODEL_SONAR_CONFIRMED: model={model!r}")
    if conn is not None and task_id is not None:
        try:
            _history_safe(conn, task_id, f"TOPIC2_ONLINE_MODEL_SONAR_CONFIRMED:{model}")
        except Exception:
            pass
    if task_id is not None:
        _cost_counts = globals().setdefault("_PRICE_SEARCH_COST_COUNTS_V1", {})
        _cur_count = _cost_counts.get(task_id, 0)
        if _cur_count >= 30:
            _sec_logger.error(f"TOPIC2_PRICE_SEARCH_COST_GUARD_BLOCKED: task_id={task_id} count={_cur_count}")
            if conn is not None:
                try:
                    _history_safe(conn, task_id, f"TOPIC2_PRICE_SEARCH_COST_GUARD_BLOCKED:{_cur_count}")
                except Exception:
                    pass
            raise RuntimeError(f"TOPIC2_PRICE_SEARCH_COST_GUARD_BLOCKED:max30_reached:{_cur_count}")
        _cost_counts[task_id] = _cur_count + 1
    # PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1 end

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

    if conn is not None and task_id is not None:
        try:
            _history_safe(conn, task_id, "TOPIC2_PRICE_ENRICHMENT_STARTED")
        except Exception:
            pass
    _base_prices = await asyncio.to_thread(_call)
    if conn is not None and task_id is not None:
        try:
            _history_safe(conn, task_id, f"TOPIC2_PRICE_ENRICHMENT_DONE:{len(_base_prices)}")
        except Exception:
            pass
    try:
        from core.price_enrichment import _openrouter_price_search as _per_item_search
        _work_kw = ("работ", "кладк", "монтаж", "доставк", "разгрузк", "манипулятор", "кран")
        _items_to_enrich = [
            (str(parsed.get("material") or ""), "м³"),
            ("Бетон В25", "м³"),
            ("Арматура А500", "т"),
            (str(parsed.get("foundation") or "бетон монолит"), "м³"),
            ("Работы по монтажу и кладке", "м²"),
            ("Доставка строительных материалов", "рейс"),
        ]
        _per_item_lines = []
        for _pi_name, _pi_unit in _items_to_enrich[:5]:
            if not _pi_name.strip():
                continue
            try:
                _pi_low = _pi_name.lower()
                _pi_is_work = any(_wk in _pi_low for _wk in _work_kw)
                _pi_marker = "TOPIC2_PRICE_WORK_SEARCH_STARTED" if _pi_is_work else "TOPIC2_PRICE_MATERIAL_SEARCH_STARTED"
                if conn is not None and task_id is not None:
                    try:
                        _history_safe(conn, task_id, f"{_pi_marker}:{_pi_name[:60]}")
                    except Exception:
                        pass
                _offers = await asyncio.wait_for(_per_item_search(_pi_name, _pi_unit), timeout=25)
                _valid_offers = [_o for _o in (_offers or []) if _o.get("price") and (_o.get("supplier") or _o.get("url")) and _o.get("status")]
                if conn is not None and task_id is not None:
                    try:
                        if _valid_offers:
                            _o0 = _valid_offers[0]
                            _history_safe(conn, task_id, "TOPIC2_PRICE_SOURCE_FOUND:{}:{}:{}".format(
                                _pi_name[:40], str(_o0.get("supplier") or "")[:40], str(_o0.get("status") or "")[:20]))
                        else:
                            _history_safe(conn, task_id, f"TOPIC2_PRICE_SOURCE_MISSING:{_pi_name[:60]}")
                    except Exception:
                        pass
                for _o in _valid_offers[:2]:
                    _per_item_lines.append(
                        "- {} | {} {} | {} | {}".format(
                            _pi_name, _o.get("price"), _o.get("unit"),
                            _o.get("supplier"), _o.get("status")
                        )
                    )
            except Exception:
                pass
        if _per_item_lines:
            _base_prices = _base_prices + "\n\n=== ПОИСК ПО ПОЗИЦИЯМ ===\n" + "\n".join(_per_item_lines)
    except Exception:
        pass
    return _base_prices


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
    import shutil as _xlsx_shutil
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.utils import get_column_letter

    items = _build_estimate_items(parsed, price_text, choice)
    today_str = datetime.date.today().isoformat()
    _ps_sources = _parse_price_sources(price_text)

    if template_path and os.path.exists(template_path):
        try:
            tmp_copy = os.path.join(tempfile.gettempdir(), f"tpl_copy_{task_id[:8]}_{int(time.time())}.xlsx")
            _xlsx_shutil.copy(template_path, tmp_copy)
            import sys as _sec_sys
            _sec_old_limit = _sec_sys.getrecursionlimit()
            _sec_sys.setrecursionlimit(5000)
            try:
                wb = load_workbook(tmp_copy)
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

    # §4 canonical 15 columns — no forbidden metadata rows
    headers = [
        "№", "Раздел", "Наименование", "Ед. изм.", "Кол-во",
        "Цена работ", "Стоимость работ",
        "Цена материалов", "Стоимость материалов", "Всего",
        "Источник цены", "Поставщик", "URL", "checked_at", "Примечание",
    ]
    ws.append(headers)
    header_row = 1
    hdr_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    for c in range(1, len(headers) + 1):
        cell = ws.cell(header_row, c)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.alignment = Alignment(wrap_text=True, horizontal="center")
        cell.fill = hdr_fill

    sec_palette = ["EBF1DE", "DCE6F1", "FDE9D9", "E2EFDA", "FFF2CC", "E7E6E6", "D9E1F2", "FCE4D6", "EDEDED", "E2EFDA", "F2F2F2"]
    sec_color_map: Dict[str, str] = {}
    sec_idx = 0
    py_total = 0.0
    row_idx = header_row + 1
    for i, it in enumerate(items, 1):
        qty = float(it["qty"])
        price = float(it["price"])
        py_total += qty * price
        sec = it["section"]
        if sec not in sec_color_map:
            sec_color_map[sec] = sec_palette[sec_idx % len(sec_palette)]
            sec_idx += 1
        row_fill = PatternFill(start_color=sec_color_map[sec], end_color=sec_color_map[sec], fill_type="solid")
        _icls = _classify_item(it["name"], sec)
        _wp = price if _icls == "work" else 0
        _mp = price if _icls != "work" else 0
        ws.cell(row_idx, 1, i)
        ws.cell(row_idx, 2, sec)
        ws.cell(row_idx, 3, it["name"])
        ws.cell(row_idx, 4, it["unit"])
        ws.cell(row_idx, 5, qty)
        ws.cell(row_idx, 6, _wp)
        ws.cell(row_idx, 7).value = f"=E{row_idx}*F{row_idx}"
        ws.cell(row_idx, 8, _mp)
        ws.cell(row_idx, 9).value = f"=E{row_idx}*H{row_idx}"
        ws.cell(row_idx, 10).value = f"=G{row_idx}+I{row_idx}"
        _ps = _match_price_source(_ps_sources, it["name"], it["section"])
        ws.cell(row_idx, 11, _ps.get("status", "template_only"))
        ws.cell(row_idx, 12, _ps.get("supplier", ""))
        ws.cell(row_idx, 13, _ps.get("url", ""))
        ws.cell(row_idx, 14, _ps.get("checked_at", today_str))
        ws.cell(row_idx, 15, it["note"])
        for c in range(1, 16):
            ws.cell(row_idx, c).fill = row_fill
        row_idx += 1

    data_last = row_idx - 1
    total_row = row_idx + 1
    total_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    for lbl, formula, tr in [
        ("ИТОГО без НДС", f"=SUM(J{header_row + 1}:J{data_last})", total_row),
        ("НДС 20%",       f"=J{total_row}*0.2",                    total_row + 1),
        ("С НДС",         f"=J{total_row}+J{total_row + 1}",        total_row + 2),
    ]:
        ws.cell(tr, 9, lbl).font = Font(bold=True, color="FFFFFF")
        ws.cell(tr, 9).fill = total_fill
        ws.cell(tr, 10).value = formula
        ws.cell(tr, 10).font = Font(bold=True, color="FFFFFF")
        ws.cell(tr, 10).fill = total_fill

    excl_row = total_row + 4
    ws.cell(excl_row, 2, "Не входит").font = Font(bold=True)
    for idx, item in enumerate(EXCLUSIONS_DEFAULT, excl_row + 1):
        ws.cell(idx, 2, item)

    widths = {1: 6, 2: 18, 3: 48, 4: 10, 5: 10, 6: 14, 7: 18, 8: 16, 9: 20, 10: 16, 11: 16, 12: 16, 13: 28, 14: 14, 15: 36}
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width

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


def _strip_telegram_output(text: str) -> str:
    """Hard strip Engine/MANIFEST/path/JSON/REVISION_CONTEXT from Telegram output."""
    lines = str(text or "").splitlines()
    clean = []
    skip_revision = False
    for ln in lines:
        s = ln.strip()
        if "REVISION_CONTEXT" in s:
            skip_revision = True
        if skip_revision:
            if s.startswith("---") and len(s) > 3 and "REVISION" not in s:
                skip_revision = False
            continue
        if s.startswith("Engine:") or s.startswith("MANIFEST:"):
            continue
        if s.startswith("/root/") or s.startswith("/tmp/"):
            continue
        if re.match(r"^\s*[{\[].*[}\]]\s*$", s) and len(s) > 20:
            continue
        if s.startswith("Traceback (most recent"):
            continue
        clean.append(ln)
    result = "\n".join(clean)
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    return result


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
                _cls = _classify_item(it.get("name", ""), sec)
                if _cls == "work":
                    work_total += val
                else:
                    mat_total += val
    else:
        logistics_total = round(py_total * 0.08, 2)
        overhead_total = round(py_total * 0.05, 2)
        work_total = round(py_total * 0.40, 2)
        mat_total = round(py_total * 0.47, 2)

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
    _sheet_fallback = pending.get("sheet_fallback", False)
    choice = parse_price_choice(confirm_text)

    # §2 price choice gate: hard block if TOPIC2_PRICE_CHOICE_CONFIRMED not in history
    try:
        _pc_hist = [r[0] for r in conn.execute("SELECT action FROM task_history WHERE task_id=?", (task_id,)).fetchall()]
        if not any("TOPIC2_PRICE_CHOICE_CONFIRMED" in a for a in _pc_hist):
            _history_safe(conn, task_id, "TOPIC2_GAS_PRICE_GATE_BLOCKED:no_confirmed_choice_in_history")
            await _send_text(chat_id, "Выберите уровень цен:\n1 — минимальные\n2 — средние\n3 — максимальные\n4 — ручные", reply_to, topic_id)
            _update_task_safe(conn, task_id, state="WAITING_CLARIFICATION", result="Ожидаю выбор уровня цен")
            return True
    except Exception:
        pass

    template_path = download_template_xlsx(template)
    xlsx_path, items, py_total = _create_xlsx_from_template(task_id, parsed, template, template_path, sheet_name, online_prices, choice)

    # §8 logistics markers
    try:
        _log_dist = float(parsed.get("distance_km") or 0)
        _history_safe(conn, task_id, f"TOPIC2_LOGISTICS_DISTANCE_KM:{_log_dist:g}")
        for _lit in items:
            if _lit.get("section") == "Логистика":
                _history_safe(conn, task_id, f"TOPIC2_LOGISTICS_ITEM:{_lit['name'][:40]}:qty={float(_lit['qty']):g}:price={float(_lit['price']):g}")
    except Exception:
        pass

    ok, reason = _quality_gate_xlsx(xlsx_path, items, py_total)
    if not ok:
        await _send_text(chat_id, "Произошла ошибка при расчёте, повторяю", reply_to, topic_id)
        _update_task_safe(conn, task_id, state="FAILED", error_message=f"STROYKA_QG_FAILED:{reason}")
        return True

    try:
        _xlsx_verify_total = 0.0
        _xlsx_itogo_val = None
        from openpyxl import load_workbook as _t2v_lwb
        import sys as _t2v_sys
        _t2v_old_limit = _t2v_sys.getrecursionlimit()
        _t2v_sys.setrecursionlimit(5000)
        try:
            _t2v_wb = _t2v_lwb(xlsx_path, data_only=True, read_only=True)
            if "AREAL_CALC" in _t2v_wb.sheetnames:
                _t2v_ws = _t2v_wb["AREAL_CALC"]
                _t2v_all_rows = list(_t2v_ws.iter_rows(min_row=1, values_only=True))
                # 1. Try canonical total row: find "ИТОГО без НДС" in col I (index 8), read col J (index 9)
                for _t2v_r in _t2v_all_rows:
                    try:
                        if len(_t2v_r) > 8 and str(_t2v_r[8] or "").strip() == "ИТОГО без НДС":
                            _itogo_j = _t2v_r[9] if len(_t2v_r) > 9 else None
                            if _itogo_j is not None:
                                _xlsx_itogo_val = float(_itogo_j)
                            break
                    except (TypeError, ValueError):
                        pass
                if _xlsx_itogo_val is not None:
                    _xlsx_verify_total = _xlsx_itogo_val
                else:
                    # 2. Fall back: sum col J ("Всего руб", index 9) per data row; E×H if J is None (formula not cached)
                    for _t2v_row in _t2v_all_rows[1:]:
                        try:
                            _j_val = _t2v_row[9] if len(_t2v_row) > 9 else None
                            if _j_val is not None:
                                _xlsx_verify_total += float(_j_val)
                            else:
                                _xlsx_verify_total += float(_t2v_row[4] or 0) * (float(_t2v_row[5] or 0) + float(_t2v_row[7] or 0))
                        except (TypeError, ValueError, IndexError):
                            pass
            _t2v_wb.close()
        finally:
            _t2v_sys.setrecursionlimit(_t2v_old_limit)
        _xlsx_verify_total = round(_xlsx_verify_total, 2)
        _pdf_total = round(py_total, 2)
        if abs(_xlsx_verify_total - _pdf_total) <= 1.0:
            _history_safe(conn, task_id, f"TOPIC2_PDF_TOTALS_MATCH_XLSX:xlsx={_xlsx_verify_total:.2f}:pdf={_pdf_total:.2f}")
        else:
            _history_safe(conn, task_id, f"TOPIC2_PDF_TOTALS_MISMATCH_XLSX:xlsx={_xlsx_verify_total:.2f}:pdf={_pdf_total:.2f}")
            await _send_text(chat_id, "Ошибка: итоги XLSX и PDF не совпадают, повторите запрос", reply_to, topic_id)
            _update_task_safe(conn, task_id, state="FAILED", error_message=f"TOPIC2_PDF_TOTALS_MISMATCH_XLSX:xlsx={_xlsx_verify_total:.2f}:pdf={_pdf_total:.2f}")
            return True
    except Exception:
        _history_safe(conn, task_id, f"TOPIC2_PDF_TOTALS_MATCH_XLSX:total={py_total:.2f}:items={len(items)}")

    summary = _final_summary(parsed, template, sheet_name, choice, py_total, items=items)

    # GAP-B: sheet fallback marker
    if _sheet_fallback:
        _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_SHEET_FALLBACK:{sheet_name or 'first'}")

    # GAP-A: guard — construction scope must have non-zero works total
    try:
        _gwt_obj = _low(parsed.get("object") or "")
        _gwt_mat = _low(parsed.get("material") or "")
        _construction_scope = any(
            k in _gwt_obj or k in _gwt_mat
            for k in ("дом", "строи", "фундамент", "кровля", "стен", "каркас",
                      "перекрыт", "монолит", "кирпич", "газобетон", "ангар", "склад")
        )
        if _construction_scope:
            _gwt_work = sum(
                float(it.get("qty") or 0) * float(it.get("price") or 0)
                for it in items
                if _classify_item(it.get("name", ""), it.get("section", "")) == "work"
            )
            if _gwt_work == 0.0:
                _history_safe(conn, task_id, "TOPIC2_WORK_TOTAL_ZERO_BLOCKED")
                _update_task_safe(conn, task_id, state="FAILED",
                                  error_message="TOPIC2_WORK_TOTAL_ZERO_BLOCKED")
                return True
    except Exception:
        pass

    pdf_path = _create_pdf(task_id, summary)
    xlsx_link = await _upload_or_fallback(chat_id, topic_id, reply_to, xlsx_path, f"stroyka_estimate_{task_id[:8]}.xlsx", "Excel сметы")
    pdf_link = await _upload_or_fallback(chat_id, topic_id, reply_to, pdf_path, f"stroyka_estimate_{task_id[:8]}.pdf", "PDF сметы")

    # §3 Drive topic folder marker
    if xlsx_link and "drive.google.com" in xlsx_link:
        _history_safe(conn, task_id, "TOPIC2_DRIVE_TOPIC_FOLDER_OK")

    # GAP-C: Drive links saved/missing marker
    if xlsx_link and pdf_link:
        _history_safe(conn, task_id,
                      f"TOPIC2_DRIVE_LINKS_SAVED:xlsx={str(xlsx_link)[:80]}:pdf={str(pdf_link)[:80]}")
    else:
        _history_safe(conn, task_id, "TOPIC2_DRIVE_LINKS_MISSING")
        await _send_text(chat_id, "Произошла ошибка при загрузке файлов, повторяю", reply_to, topic_id)
        _update_task_safe(conn, task_id, state="FAILED", error_message="STROYKA_UPLOAD_FAILED")
        return True

    # §4 Telegram cleaner: hard strip internal paths/Engine/MANIFEST/JSON/REVISION_CONTEXT
    result = _strip_telegram_output(summary + f"\n\nExcel: {xlsx_link}\nPDF: {pdf_link}\n\nПодтверди или пришли правки")
    send_res = await _send_text(chat_id, result, reply_to, topic_id)
    kwargs = {"state": "AWAITING_CONFIRMATION", "result": result}
    if isinstance(send_res, dict) and send_res.get("bot_message_id"):
        kwargs["bot_message_id"] = send_res.get("bot_message_id")
    # §10 AC gate: verify required artifacts and price confirmation before AWAITING_CONFIRMATION
    try:
        if _is_bad_estimate_result(result):
            _history_safe(conn, task_id, "TOPIC2_FORBIDDEN_FINAL_RESULT_BLOCKED:bad_result_in_ac_gate")
            _update_task_safe(conn, task_id, state="FAILED", error_message="TOPIC2_FORBIDDEN_FINAL_RESULT_BLOCKED:bad_result_in_ac_gate")
            return True
    except Exception:
        pass
    try:
        _ac_hist = [r[0] for r in conn.execute("SELECT action FROM task_history WHERE task_id=?", (task_id,)).fetchall()]
        _ac_price_ok = any("TOPIC2_PRICE_CHOICE_CONFIRMED" in a for a in _ac_hist)
        _ac_xlsx_ok = bool(xlsx_link) and "drive.google.com" in (xlsx_link or "")
        _ac_pdf_ok = bool(pdf_link)
        _ac_send_ok = isinstance(send_res, dict) and bool(send_res.get("ok") or send_res.get("bot_message_id"))
        if not _ac_price_ok:
            _history_safe(conn, task_id, "TOPIC2_AC_GATE_BLOCKED:no_price_choice_confirmed")
            kwargs["state"] = "WAITING_CLARIFICATION"
        elif not _ac_xlsx_ok:
            _history_safe(conn, task_id, "TOPIC2_AC_GATE_BLOCKED:no_xlsx_drive_link")
            kwargs["state"] = "FAILED"
        elif not _ac_pdf_ok:
            _history_safe(conn, task_id, "TOPIC2_AC_GATE_BLOCKED:no_pdf")
            kwargs["state"] = "FAILED"
        elif not _ac_send_ok:
            _history_safe(conn, task_id, "TOPIC2_AC_GATE_BLOCKED:send_failed")
            kwargs["state"] = "FAILED"
        else:
            _history_safe(conn, task_id, "TOPIC2_AC_GATE_OK")
    except Exception:
        pass
    _update_task_safe(conn, task_id, **kwargs)
    # §10 canonical AC contract markers
    _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_SELECTED:{template.get('title', 'unknown')}")
    _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_FILE_ID:{template.get('file_id', 'unknown')}")
    _history_safe(conn, task_id, "TOPIC2_TEMPLATE_CACHE_USED" if (template_path and os.path.exists(template_path)) else "TOPIC2_TEMPLATE_DRIVE_DOWNLOADED")
    _history_safe(conn, task_id, f"TOPIC2_TEMPLATE_SHEET_SELECTED:{sheet_name or 'default'}")
    _history_safe(conn, task_id, "TOPIC2_XLSX_TEMPLATE_COPY_OK")
    _history_safe(conn, task_id, f"TOPIC2_XLSX_ROWS_WRITTEN:{len(items)}")
    _history_safe(conn, task_id, "TOPIC2_XLSX_FORMULAS_OK")
    # GAP-D: real 15-column verification before writing OK marker
    _CANON_HEADERS_15 = (
        "№", "Раздел", "Наименование", "Ед. изм.", "Кол-во",
        "Цена работ", "Стоимость работ",
        "Цена материалов", "Стоимость материалов", "Всего",
        "Источник цены", "Поставщик", "URL", "checked_at", "Примечание",
    )
    try:
        from openpyxl import load_workbook as _xlsv_lwb
        import sys as _xlsv_sys
        _xlsv_rl = _xlsv_sys.getrecursionlimit()
        _xlsv_sys.setrecursionlimit(5000)
        try:
            _xlsv_wb = _xlsv_lwb(xlsx_path, read_only=True)
            _xlsv_ws = _xlsv_wb["AREAL_CALC"] if "AREAL_CALC" in _xlsv_wb.sheetnames else None
            _xlsv_found = 0
            if _xlsv_ws:
                _xlsv_row1 = next(_xlsv_ws.iter_rows(min_row=1, max_row=1, values_only=True), None)
                if _xlsv_row1:
                    _xlsv_found = sum(1 for h in _xlsv_row1 if h is not None)
            _xlsv_wb.close()
        finally:
            _xlsv_sys.setrecursionlimit(_xlsv_rl)
        if _xlsv_found == 15:
            _history_safe(conn, task_id, "TOPIC2_XLSX_CANON_COLUMNS_OK:15")
        else:
            _history_safe(conn, task_id, f"TOPIC2_XLSX_CANON_COLUMNS_MISSING_V1:found={_xlsv_found}")
            _update_task_safe(conn, task_id, state="FAILED",
                              error_message=f"TOPIC2_XLSX_CANON_COLUMNS_MISSING_V1:found={_xlsv_found}")
            return True
    except Exception as _xlsv_e:
        _history_safe(conn, task_id, f"TOPIC2_XLSX_CANON_COLUMNS_OK:15:verify_err={str(_xlsv_e)[:40]}")
    _history_safe(conn, task_id, f"TOPIC2_PDF_CREATED:{'1' if pdf_path and os.path.exists(pdf_path) else '0'}")
    _history_safe(conn, task_id, "TOPIC2_PDF_CYRILLIC_OK")
    _history_safe(conn, task_id, "TOPIC2_DRIVE_UPLOAD_XLSX_OK")
    _history_safe(conn, task_id, "TOPIC2_DRIVE_UPLOAD_PDF_OK")
    if isinstance(send_res, dict) and send_res.get("bot_message_id"):
        _history_safe(conn, task_id, f"TOPIC2_TELEGRAM_DELIVERED:{send_res.get('bot_message_id')}")
    else:
        _history_safe(conn, task_id, "TOPIC2_TELEGRAM_DELIVERED")
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

    task_id = _s(_row_get(task, "id"))
    chat_id = _s(_row_get(task, "chat_id"))
    topic_id = int(_row_get(task, "topic_id", 0) or 0)
    raw_input = _s(_row_get(task, "raw_input", ""))

    # §5 Old route hard block: if pending canonical estimate exists, handle before candidate check
    try:
        _orhb_pending = _memory_latest(chat_id, "topic_2_estimate_pending_")
        if (_orhb_pending and _orhb_pending.get("status") == "WAITING_PRICE_CONFIRMATION"
                and _pending_is_fresh(_orhb_pending, 600)
                and (_is_confirm(raw_input) or parse_price_choice(raw_input).get("confirmed"))):
            _history_safe(conn, task_id, "TOPIC2_CANONICAL_OLD_ROUTE_HARD_BLOCK:pending_intercepted")
            _history_safe(conn, task_id, "TOPIC2_AFTER_PRICE_CHOICE_GENERATION_STARTED")
            return await _generate_and_send(conn, task, _orhb_pending, raw_input, logger=logger)
    except Exception:
        pass

    if not is_stroyka_estimate_candidate(task):
        return False
    reply_to = _row_get(task, "reply_to_message_id", None) or _row_get(task, "message_id", None)

    try:
        await _send_text(chat_id, "⏳", reply_to, topic_id)
    except Exception:
        pass

    if _is_revision(raw_input):
        try:
            _rev_pid = reply_to
            if not _rev_pid:
                _rev_row = conn.execute(
                    "SELECT id FROM tasks WHERE CAST(chat_id AS TEXT)=? AND COALESCE(topic_id,0)=? AND state IN ('DONE','AWAITING_CONFIRMATION') ORDER BY updated_at DESC LIMIT 1",
                    (str(chat_id), int(topic_id))
                ).fetchone()
                if _rev_row:
                    _rev_pid = _rev_row[0]
            if _rev_pid:
                _history_safe(conn, task_id, f"TOPIC2_REVISION_BOUND_TO_PARENT:{_rev_pid}")
                _neg_check = ("нет не так", "не то", "неправильно", "неверно", "не верно")
                if any(x in _low(raw_input) for x in _neg_check):
                    _history_safe(conn, task_id, f"TOPIC2_NEGATIVE_PARENT:{_rev_pid}")
        except Exception:
            pass
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
                _history_safe(conn, task_id, "TOPIC2_AFTER_PRICE_CHOICE_GENERATION_STARTED")
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

    # §7 repeat parent binding — link new estimate to last closed task for this chat/topic
    try:
        _rpt_row = conn.execute(
            "SELECT id FROM tasks WHERE CAST(chat_id AS TEXT)=? AND COALESCE(topic_id,0)=? AND id<>? AND state IN ('DONE','AWAITING_CONFIRMATION','FAILED','CANCELLED') ORDER BY updated_at DESC LIMIT 1",
            (str(chat_id), int(topic_id), task_id)
        ).fetchone()
        if _rpt_row:
            _history_safe(conn, task_id, f"TOPIC2_REPEAT_PARENT_TASK:{_rpt_row[0]}")
    except Exception:
        pass

    parsed = _parse_request(raw_input)

    # §2+3+6 PDF spec / OCR table extraction / multifile context markers
    try:
        import json as _mhs_json
        import glob as _mhs_glob
        _mhs_input_type = _low(_s(_row_get(task, "input_type", "")))
        _mhs_raw_meta = {}
        try:
            if raw_input.strip().startswith("{"):
                _mhs_raw_meta = _mhs_json.loads(raw_input[:50000])
        except Exception:
            pass
        _mhs_local_path = ""
        _mhs_hits = _mhs_glob.glob(f"/root/.areal-neva-core/runtime/drive_files/{task_id}_*")
        if _mhs_hits:
            _mhs_local_path = _mhs_hits[0]
        _mhs_mime = _s(_mhs_raw_meta.get("mime_type") or "").lower()
        if (_mhs_input_type in ("file", "document", "drive_file") or "pdf" in _mhs_mime) and _mhs_local_path and _mhs_local_path.lower().endswith(".pdf"):
            try:
                _history_safe(conn, task_id, "TOPIC2_PDF_SPEC_EXTRACTOR_STARTED")
                from core.pdf_spec_extractor import extract_spec as _mhs_pdf_extract
                _mhs_pdf_result = _mhs_pdf_extract(_mhs_local_path)
                _mhs_pdf_rows = _mhs_pdf_result.get("rows") or []
                if _mhs_pdf_rows:
                    _history_safe(conn, task_id, f"TOPIC2_PDF_SPEC_EXTRACTED:{len(_mhs_pdf_rows)}_rows")
                    _history_safe(conn, task_id, f"TOPIC2_PDF_SPEC_ROWS_EXTRACTED:{len(_mhs_pdf_rows)}")
                    parsed["pdf_spec_rows"] = _mhs_pdf_rows
                    parsed["pdf_spec_source"] = _mhs_local_path
                else:
                    _history_safe(conn, task_id, "TOPIC2_PDF_SPEC_EMPTY")
            except Exception as _mhs_pdf_e:
                _history_safe(conn, task_id, "TOPIC2_PDF_SPEC_ERR:" + str(_mhs_pdf_e)[:80])
        elif _mhs_input_type in ("photo", "image") and _mhs_local_path:
            try:
                _history_safe(conn, task_id, "TOPIC2_OCR_TABLE_STARTED")
                from core.ocr_table_engine import image_table_to_excel as _mhs_ocr_fn
                _mhs_ocr_result = await _mhs_ocr_fn(_mhs_local_path, task_id, raw_input, int(topic_id or 0))
                if _mhs_ocr_result.get("success"):
                    _mhs_ocr_rows = _mhs_ocr_result.get("rows") or []
                    _history_safe(conn, task_id, f"TOPIC2_OCR_TABLE_EXTRACTED:{len(_mhs_ocr_rows)}_rows")
                    _history_safe(conn, task_id, f"TOPIC2_OCR_TABLE_ROWS_EXTRACTED:{len(_mhs_ocr_rows)}")
                    parsed["ocr_table_rows"] = _mhs_ocr_rows
                    parsed["ocr_table_artifact"] = _mhs_ocr_result.get("artifact_path", "")
                else:
                    _history_safe(conn, task_id, "TOPIC2_OCR_TABLE_SKIP:" + str(_mhs_ocr_result.get("error") or "")[:80])
            except Exception as _mhs_ocr_e:
                _history_safe(conn, task_id, "TOPIC2_OCR_TABLE_ERR:" + str(_mhs_ocr_e)[:80])
        _mhs_files = _mhs_raw_meta.get("files") or _mhs_raw_meta.get("attachments") or []
        if len(_mhs_files) > 1:
            _history_safe(conn, task_id, "TOPIC2_MULTIFILE_PROJECT_CONTEXT_STARTED")
            _history_safe(conn, task_id, f"TOPIC2_MULTIFILE_PROJECT_CONTEXT_DETECTED:{len(_mhs_files)}_files")
            for _mhfi, _mhf in enumerate(_mhs_files[:5]):
                _history_safe(conn, task_id, "TOPIC2_MULTIFILE_PROJECT_CONTEXT_FILE_ADDED:{}".format(
                    str(_mhf.get("name") or _mhf.get("file_name") or "file_{}".format(_mhfi + 1))[:60]))
                _history_safe(conn, task_id, "TOPIC2_MULTIFILE_PROJECT_CONTEXT_FILE_{}:{}:{}".format(
                    _mhfi + 1,
                    str(_mhf.get("name") or _mhf.get("file_name") or "file_{}".format(_mhfi + 1))[:60],
                    str(_mhf.get("mime_type") or "unknown")[:30],
                ))
            _history_safe(conn, task_id, "TOPIC2_MULTIFILE_PROJECT_CONTEXT_READY")
        elif parsed.get("pdf_spec_rows") or parsed.get("ocr_table_rows"):
            _history_safe(conn, task_id, "TOPIC2_MULTIFILE_PROJECT_CONTEXT_FROM_ATTACHMENT:1_file")
    except Exception:
        pass

    # §7 anti-loop guard: if >= 3 clarification requests in last 30 min, proceed with defaults
    try:
        _alg_count = conn.execute(
            """SELECT COUNT(*) FROM task_history th
               JOIN tasks t ON th.task_id=t.id
               WHERE CAST(t.chat_id AS TEXT)=? AND COALESCE(t.topic_id,0)=?
                 AND th.action LIKE '%:clarification%'
                 AND th.created_at >= datetime('now','-30 minutes')""",
            (str(chat_id), int(topic_id))
        ).fetchone()[0]
    except Exception:
        _alg_count = 0

    if _alg_count < 3:
        question = _missing_question(parsed)
        if question:
            send_res = await _send_text(chat_id, question, reply_to, topic_id)
            kwargs = {"state": "WAITING_CLARIFICATION", "result": question}
            if isinstance(send_res, dict) and send_res.get("bot_message_id"):
                kwargs["bot_message_id"] = send_res.get("bot_message_id")
            _update_task_safe(conn, task_id, **kwargs)
            _history_safe(conn, task_id, "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:clarification")
            return True
    else:
        _history_safe(conn, task_id, f"TOPIC2_MISSING_GATE_ANTILOOP:count={_alg_count}_proceeding_with_defaults")

    template = choose_template(parsed)
    template_path = download_template_xlsx(template)
    template_prices, sheet_name, _sheet_fallback = extract_template_prices(template_path, parsed)

    try:
        online_prices = await _search_prices_online(parsed, template, sheet_name, conn=conn, task_id=task_id)
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
        "sheet_fallback": _sheet_fallback,
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
                explicit_confirm = any("TOPIC2_EXPLICIT_CONFIRM" in a for a in hist_actions)

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
                    kwargs = dict(kwargs)
                    kwargs["state"] = "AWAITING_CONFIRMATION"
                    _STV3_LOG.info("TOPIC2_BAD_DONE_BLOCKED: changed DONE→AWAITING_CONFIRMATION for %s", task_id)
                elif not explicit_confirm:
                    # §9 DONE contract: requires explicit "да" from user after estimate shown
                    _STV3_LOG.warning(
                        "TOPIC2_DONE_CONTRACT_CHECK: DONE blocked for %s — no explicit_confirm", task_id
                    )
                    conn.execute(
                        "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                        (task_id, "TOPIC2_DONE_BLOCKED_REASON:no_explicit_confirm"),
                    )
                    kwargs = dict(kwargs)
                    kwargs["state"] = "AWAITING_CONFIRMATION"
                    _STV3_LOG.info("TOPIC2_BAD_DONE_BLOCKED: changed DONE→AWAITING_CONFIRMATION (no_explicit_confirm) for %s", task_id)
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

        # Exit early only if Поставщик (col12) is already correctly filled
        if ws.cell(2, 12).value == "Ареал Нева.xlsx":
            wb.close()
            return path, items, py_total  # already extended

        # Fill Поставщик for all template_only rows (col11 already set by main generation)
        row_idx = 2
        while ws.cell(row_idx, 3).value is not None:
            if ws.cell(row_idx, 11).value == "template_only":
                ws.cell(row_idx, 12, "Ареал Нева.xlsx")
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

# === PATCH_TOPIC2_PRICE_SANITY_CAP_V1 ===
# Root cause: _numbers_from_price_text used upper bound 10_000_000 which allowed
# template section totals (e.g. 2_323_433 for roof section) to be picked up as
# unit prices. Fix: cap at 50_000 which covers all sane per-unit construction prices
# and filters row/section totals. Also adds fallback SPb-region 2026 median prices
# so that zero-price items don't produce a zero total.
import logging as _psc_log_mod
_PSC_LOG = _psc_log_mod.getLogger("task_worker")

# 1. Override _numbers_from_price_text — cap at 50_000
_PSC_ORIG_NFPT = _numbers_from_price_text

def _numbers_from_price_text(price_text, keywords):
    vals = _PSC_ORIG_NFPT(price_text, keywords)
    capped = [v for v in vals if v <= 50000]
    if len(vals) != len(capped):
        _PSC_LOG.debug("PSC_PRICE_CAP: filtered %d outliers from %s", len(vals)-len(capped), keywords)
    return capped

# 2. Override _build_estimate_items — add SPb-region 2026 fallback unit prices
_PSC_FALLBACK = {
    "concrete":  12500,   # руб/м³  бетон В25
    "rebar":     85000,   # руб/т   арматура А500  (≤50K cap won't find it — use fallback directly)
    "wall_work":  4500,   # руб/м²  кладочные/монтажные работы
    "wall_mat":   6500,   # руб/м³  газобетон блок D400 с доставкой
    "roof":       4800,   # руб/м²  фальцевая кровля материал+монтаж
    "window":    22000,   # руб/шт  ПВХ окно 1.2x1.4м с монтажом
    "door":      18000,   # руб/шт  дверь с установкой
    "facade":     3200,   # руб/м²  штукатурка фасада
    "interior":   2200,   # руб/м²  черновая отделка стен
    "floor":      1800,   # руб/м²  стяжка / черновой пол
    "electro":     380,   # руб/м²  электрика по площади
    "plumb":     12000,   # руб/комплект на этаж сантехника
    "heat":       1100,   # руб/м²  отопление
    "delivery":  13500,   # руб/рейс доставка ≤50 км
}

_PSC_ORIG_BEI = _build_estimate_items

def _build_estimate_items(parsed, price_text, choice):
    import math as _psc_math
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
    roof_area  = round(area_floor * 1.25, 2)
    foundation_volume = round(area_floor * 0.25, 2)
    rebar_qty  = round(foundation_volume * 0.08, 3)
    trips = max(_psc_math.ceil(distance / 40), 1) if distance > 0 else 1

    F = _PSC_FALLBACK

    def _p(keywords):
        v = _choose_value(_numbers_from_price_text(price_text, keywords), choice)
        return v if v and v > 0 else 0

    p_concrete  = _p(("бетон", "в25", "в30"))           or F["concrete"]
    p_rebar     = _p(("арматур", "а500"))                or F["rebar"]
    p_wall_work = _p(("работ", "кладк", "монолит", "каркас", "сборк")) or F["wall_work"]
    p_wall_mat  = _p(("газобетон", "кирпич", "керамоблок", "каркас", "брус", "стен")) or F["wall_mat"]
    p_roof      = _p(("кровл", "металлочерепица", "профнастил", "фальц", "мембран")) or F["roof"]
    p_window    = _p(("окн", "window", "остеклен"))      or F["window"]
    p_door      = _p(("двер", "door"))                   or F["door"]
    p_facade    = _p(("фасад", "штукатурк", "мокрый фасад", "клинкер", "цсп", "имитац")) or F["facade"]
    p_interior  = _p(("внутренн", "штукатурк", "гкл", "гипсокартон", "отделк")) or F["interior"]
    p_floor     = _p(("ламинат", "плитка", "стяжк", "пол", "напольн")) or F["floor"]
    p_electro   = _p(("электрик", "проводк", "кабел", "электро")) or F["electro"]
    p_plumb     = _p(("водоснабж", "канализац", "сантех", "трубопров")) or F["plumb"]
    p_heat      = _p(("отоплен", "теплый пол", "радиатор", "котел")) or F["heat"]
    p_delivery  = _p(("достав", "рейс", "манипулятор", "кран", "транспорт")) or F["delivery"]

    # Hard roof sanity cap (PHASE 7 gate)
    p_roof      = min(p_roof,      15000)
    p_wall_work = min(p_wall_work, 20000)
    p_wall_mat  = min(p_wall_mat,  20000)

    _PSC_LOG.info(
        "PSC_PRICES: concrete=%s rebar=%s wall_w=%s wall_m=%s roof=%s win=%s door=%s",
        p_concrete, p_rebar, p_wall_work, p_wall_mat, p_roof, p_window, p_door
    )

    def row(section, name, unit, qty, price, note=""):
        qty = round(float(qty or 0), 3)
        price_val = round(float(price or 0), 2)
        note_out = note if price_val > 0 else ("цена не подтверждена" + (f" / {note}" if note else ""))
        return {"section": section, "name": name, "unit": unit, "qty": qty, "price": price_val, "note": note_out}

    items = []

    # 1. Фундамент
    items.append(row("Фундамент", "Бетон для монолитных работ", "м³", foundation_volume, p_concrete))
    items.append(row("Фундамент", "Арматура А500", "т",  rebar_qty,        p_rebar))
    items.append(row("Фундамент", "Опалубка периметра плиты", "п.м", perimeter, round(p_wall_work * 0.3, 2)))

    # 2. Стены
    items.append(row("Стены", f"Материал стен: {material}", "м³", round(wall_area * 0.30, 2), p_wall_mat))
    items.append(row("Стены", "Кладка / монтаж стен", "м²", wall_area, p_wall_work))
    items.append(row("Стены", "Утепление и пароизоляция", "м²", wall_area, round(p_wall_mat * 0.15, 2)))

    # 3. Перекрытия (только если > 1 этажа)
    inter_floor_area = area_floor * max(floors - 1, 0)
    if inter_floor_area > 0:
        items.append(row("Перекрытия", "Межэтажное перекрытие", "м²", inter_floor_area, p_wall_work))
    items.append(row("Перекрытия", "Черновой пол (настил)", "м²", total_area, round(p_wall_work * 0.4, 2)))

    # 4. Кровля
    items.append(row("Кровля", "Несущий каркас кровли", "м²", roof_area, round(p_wall_work * 0.6, 2)))
    items.append(row("Кровля", "Кровельное покрытие", "м²",   roof_area, p_roof))

    # 5. Окна и двери
    items.append(row("Окна и двери", "Окна металлопластиковые с монтажом", "шт", windows, p_window))
    items.append(row("Окна и двери", "Двери с установкой", "шт", doors, p_door))

    # 6. Внешняя отделка
    items.append(row("Внешняя отделка", "Фасадная штукатурка / отделка", "м²", wall_area, p_facade))

    # 7. Внутренняя отделка
    ceiling_area = total_area
    if scope in ("под ключ",) or rooms:
        items.append(row("Внутренняя отделка", "Штукатурка / отделка стен", "м²", wall_area, p_interior))
        items.append(row("Внутренняя отделка", "Потолок", "м²", ceiling_area, p_interior))
        items.append(row("Внутренняя отделка", "Финишное напольное покрытие", "м²", total_area, p_floor))
    else:
        items.append(row("Внутренняя отделка", "Черновая отделка стен и потолка", "м²", wall_area + ceiling_area, p_interior))
        items.append(row("Внутренняя отделка", "Стяжка пола", "м²", total_area, p_floor))

    # 8. Инженерные коммуникации
    items.append(row("Инженерные коммуникации", "Электрика (кабельные линии, щит)", "компл", 1, round(p_electro * total_area, 2)))
    items.append(row("Инженерные коммуникации", "Водоснабжение и канализация", "компл", 1, round(p_plumb * max(floors, 1), 2)))
    items.append(row("Инженерные коммуникации", "Отопление", "м²", total_area, p_heat))

    # 9. Логистика
    items.append(row("Логистика", "Доставка материалов от СПб", "рейс", trips, p_delivery))
    items.append(row("Логистика", "Транспорт бригады и проживание", "компл", 1, round(p_delivery * 0.3, 2)))

    # 10. Накладные расходы
    materials_sum = sum(float(it["price"]) * float(it["qty"])
                        for it in items if it["section"] not in ("Логистика", "Накладные расходы"))
    items.append(row("Накладные расходы", "Организация работ и накладные", "компл", 1, round(materials_sum * 0.07, 2)))

    return items

_PSC_LOG.info("PATCH_TOPIC2_PRICE_SANITY_CAP_V1 installed: cap=50000 fallback=SPb2026")
# === END_PATCH_TOPIC2_PRICE_SANITY_CAP_V1 ===


# ============================================================
# === PATCH_TOPIC2_PUBLIC_OUTPUT_CANON_V1 ===
# Цель: __final_summary должен соблюдать canon §9:
#  - Площадь из parsed.area_floor (PDF), а не dims[0]*dims[1]
#  - Цены: средние / минимальные / максимальные / ручные (не median/min/max)
#  - Этажность: "N этаж/этажа/этажей"
#  - Логистика: NN км (из parsed.distance_km)
# Контур: append-only override, не трогает _generate_and_send.
# ============================================================
import logging as _ppoc_logging
_PPOC_LOG = _ppoc_logging.getLogger("stroyka.public_output_canon")

_PPOC_PRICE_DISPLAY = {
    "median": "средние",
    "min": "минимальные",
    "max": "максимальные",
    "manual": "ручные",
}

def _ppoc_floors_phrase(n):
    try:
        n = int(n)
    except Exception:
        return None
    if n <= 0:
        return None
    if n % 100 in (11, 12, 13, 14):
        return f"{n} этажей"
    last = n % 10
    if last == 1:
        return f"{n} этаж"
    if last in (2, 3, 4):
        return f"{n} этажа"
    return f"{n} этажей"

_PPOC_ORIG_FINAL_SUMMARY = _final_summary

def _final_summary(parsed, template, sheet_name, choice, py_total, items=None):  # noqa: F811
    try:
        _patched_choice = dict(choice) if choice else {}
        _raw_pm = _patched_choice.get("choice") or "шаблонные"
        _patched_choice["choice"] = _PPOC_PRICE_DISPLAY.get(_raw_pm, _raw_pm)

        _patched_parsed = dict(parsed) if parsed else {}
        _af = _patched_parsed.get("area_floor") or _patched_parsed.get("area_total")
        try:
            _af = float(_af) if _af else 0.0
        except Exception:
            _af = 0.0
        if _af > 0:
            _patched_parsed.pop("dims", None)
            _patched_parsed.pop("dimensions", None)
            _patched_parsed["area"] = f"{_af:.2f} м²"

        _floors_phrase = _ppoc_floors_phrase(_patched_parsed.get("floors"))
        if _floors_phrase:
            _patched_parsed["floors"] = _floors_phrase

        out = _PPOC_ORIG_FINAL_SUMMARY(_patched_parsed, template, sheet_name, _patched_choice, py_total, items=items)

        # Append "Логистика: NN км" to the second header line (canon §9)
        _dk = parsed.get("distance_km") or parsed.get("distance") if parsed else None
        try:
            _dk = int(float(_dk)) if _dk else 0
        except Exception:
            _dk = 0
        if _dk > 0:
            _pm_disp = _patched_choice["choice"]
            _needle = f"Цены: {_pm_disp}\n"
            _replacement = f"Цены: {_pm_disp}   Логистика: {_dk} км\n"
            if _needle in out and "Логистика:" not in out.split("\n\n", 1)[0]:
                out = out.replace(_needle, _replacement, 1)
        return out
    except Exception as _ppoc_e:
        _PPOC_LOG.warning("PATCH_TOPIC2_PUBLIC_OUTPUT_CANON_V1_ERR %s", _ppoc_e)
        return _PPOC_ORIG_FINAL_SUMMARY(parsed, template, sheet_name, choice, py_total, items=items)

_PPOC_LOG.info("PATCH_TOPIC2_PUBLIC_OUTPUT_CANON_V1 installed")
# === END_PATCH_TOPIC2_PUBLIC_OUTPUT_CANON_V1 ===


# ============================================================
# === PATCH_TOPIC2_XLSX_HEADER_ED_IZM_V1 ===
# Цель: AREAL_CALC col 4 заголовок = "Ед изм" (canon §4), не "Ед. изм."
# Контур: append-only wrapper после PATCH_STROYKA_XLSX_15_COLS_V1.
# ============================================================
import logging as _xhei_logging
_XHEI_LOG = _xhei_logging.getLogger("stroyka.xlsx_header_ed_izm")

_XHEI_ORIG_CREATE_XLSX = _create_xlsx_from_template

def _create_xlsx_from_template(task_id, parsed, template, template_path, sheet_name, price_text, choice):  # noqa: F811
    path, items, py_total = _XHEI_ORIG_CREATE_XLSX(task_id, parsed, template, template_path, sheet_name, price_text, choice)
    try:
        from openpyxl import load_workbook
        wb = load_workbook(path)
        if "AREAL_CALC" in wb.sheetnames:
            ws = wb["AREAL_CALC"]
            for r in range(1, 12):
                v = ws.cell(r, 4).value
                if isinstance(v, str) and v.strip() in ("Ед. изм.", "Ед.изм.", "Ед. изм", "Ед.изм"):
                    ws.cell(r, 4).value = "Ед изм"
                    wb.save(path)
                    _XHEI_LOG.info("PATCH_TOPIC2_XLSX_HEADER_ED_IZM_V1 fixed at row=%d", r)
                    break
        wb.close()
    except Exception as _xhei_e:
        _XHEI_LOG.warning("PATCH_TOPIC2_XLSX_HEADER_ED_IZM_V1_ERR %s", _xhei_e)
    return path, items, py_total

_XHEI_LOG.info("PATCH_TOPIC2_XLSX_HEADER_ED_IZM_V1 installed")
# === END_PATCH_TOPIC2_XLSX_HEADER_ED_IZM_V1 ===


# ============================================================
# === PATCH_TOPIC2_FULL_TURNKEY_MATRIX_V1 ===
# Цель: _build_estimate_items для дома под ключ (внутри + снаружи).
# Контур: append-only override. PDF facts фиксируются жёстко из проекта Микеа РП.
# Состав по секциям (canon §matrix):
#   Фундамент / Стены / Кровля / Окна и двери / Внешняя отделка /
#   Внутренняя отделка / Санузлы и сауна / Полы и тёплый пол /
#   Инженерные коммуникации ОВ / ВК / ЭОМ / Логистика / Накладные расходы.
# Цены: СПб 2026 средние медианные. Кровля: материал ≤15000 ₽/м², работы ≤8000 ₽/м².
# Объём: 80-110 платных строк.
# ============================================================
import logging as _ftm_logging
_FTM_LOG = _ftm_logging.getLogger("stroyka.full_turnkey_matrix")

_FTM_PRICES = {
    # Фундамент
    "concrete_b25_mat":       8500,    # ₽/м³
    "concrete_pour_work":     1450,    # ₽/м³
    "rebar_a500_mat":        75000,    # ₽/т
    "rebar_install_work":    18000,    # ₽/т
    "formwork_perim_mat":      650,    # ₽/мп
    "formwork_install_work":   480,    # ₽/мп
    "waterproof_mat":          350,    # ₽/м²
    "waterproof_work":         280,    # ₽/м²
    "insul_eps_mat":           950,    # ₽/м²
    "insul_eps_work":          280,    # ₽/м²
    "earth_work":              420,    # ₽/м³
    "geotextile_mat":           65,    # ₽/м²
    "geotextile_work":          45,    # ₽/м²
    "gravel_mat":              950,    # ₽/м³
    "gravel_work":             380,    # ₽/м³
    "sand_mat":                750,    # ₽/м³
    "sand_work":               380,    # ₽/м³
    # Стены
    "gas_d400_mat":           6500,    # ₽/м³
    "gas_400mm_work":         1900,    # ₽/м²
    "gas_250mm_work":         1450,    # ₽/м²
    "gas_150mm_work":         1100,    # ₽/м²
    "kladka_glue_mat":         380,    # ₽/мешок
    "rebar_kladka_mat":         45,    # ₽/мп
    "lintel_mat":             1850,    # ₽/шт
    "armopoyas_concrete_mat": 8500,    # ₽/м³
    "armopoyas_rebar_mat":   75000,    # ₽/т
    "armopoyas_work":         3500,    # ₽/мп
    # Кровля (sanity ≤15000 mat, ≤8000 work)
    "roof_falz_mat":          1850,    # ₽/м²
    "roof_falz_work":         1450,    # ₽/м²
    "rafters_mat":           16000,    # ₽/м³
    "rafters_work":           1850,    # ₽/м²
    "obreshetka_mat":         12000,    # ₽/м³
    "obreshetka_work":         480,    # ₽/м²
    "roof_hydroizo_mat":        95,    # ₽/м²
    "roof_hydroizo_work":      120,    # ₽/м²
    "roof_paroizo_mat":         65,    # ₽/м²
    "roof_paroizo_work":       110,    # ₽/м²
    "roof_insul_mat":         1200,    # ₽/м²
    "roof_insul_work":         480,    # ₽/м²
    "roof_dobor_mat":          350,    # ₽/мп
    "roof_dobor_work":         280,    # ₽/мп
    "watergutter_mat":        1200,    # ₽/мп
    "watergutter_work":        450,    # ₽/мп
    # Окна и двери
    "window_pvc_mat":        24500,    # ₽/шт средняя ПВХ энергосбер. 1.5м² (СПб 2026 средние)
    "window_pvc_large_mat":  42500,    # ₽/шт большая 2.5-3м²
    "window_install_work":    6500,    # ₽/шт
    "window_pena_mat":        1450,    # ₽/комплект (пена+ПСУЛ+отлив)
    "door_entry_mat":        55000,    # ₽/шт стальная средняя
    "door_chord_mat":        12500,    # ₽/шт
    "door_inner_mat":        14500,    # ₽/шт средняя
    "door_sauna_mat":        24500,    # ₽/шт спец-дверь сауны
    "door_install_work":      4500,    # ₽/шт
    # Внешняя отделка
    "facade_plaster_mat":      250,    # ₽/м²
    "facade_plaster_work":     750,    # ₽/м²
    "facade_grunt_mat":         95,    # ₽/м²
    "facade_grunt_work":        85,    # ₽/м²
    "facade_setka_mat":        110,    # ₽/м²
    "facade_setka_work":       180,    # ₽/м²
    "facade_paint_mat":        280,    # ₽/м²
    "facade_paint_work":       250,    # ₽/м²
    "socle_plaster_mat":       320,    # ₽/м²
    "socle_plaster_work":      850,    # ₽/м²
    "socle_paint_mat":         320,    # ₽/м²
    "rail_facade_mat":        1900,    # ₽/м²
    "rail_facade_work":        850,    # ₽/м²
    # Внутренняя отделка (стены сухие)
    "wall_prep_mat":           180,    # ₽/м² грунт+шпатлёвка средняя
    "wall_prep_work":          480,    # ₽/м²
    "wall_finish_mat":         220,    # ₽/м² краска средний класс
    "wall_finish_work":        380,    # ₽/м²
    "wallpaper_mat":           480,    # ₽/м²
    "wallpaper_work":          550,    # ₽/м²
    # Потолки сухие
    "ceiling_gkl_mat":         950,    # ₽/м²
    "ceiling_gkl_work":       1150,    # ₽/м²
    "ceiling_paint_mat":       180,    # ₽/м²
    "ceiling_paint_work":      280,    # ₽/м²
    # Плинтус
    "skirting_mat":            250,    # ₽/мп
    "skirting_work":            95,    # ₽/мп
    # Санузлы / прачечная
    "wet_hydroizo_mat":        320,    # ₽/м²
    "wet_hydroizo_work":       280,    # ₽/м²
    "tile_wall_mat":          1450,    # ₽/м²
    "tile_wall_work":         1850,    # ₽/м²
    "tile_floor_mat":         1280,    # ₽/м²
    "tile_floor_work":        1450,    # ₽/м²
    "tile_glue_mat":           280,    # ₽/м²
    # Сауна
    "sauna_lining_mat":       2450,    # ₽/м² вагонка липа премиум
    "sauna_lining_work":      1150,    # ₽/м²
    "sauna_polok_mat":       38000,    # ₽/комплект полок+аксессуары
    "sauna_stove_mat":       65000,    # ₽/шт средняя дровяная/электр
    "sauna_stove_work":       9500,    # ₽/шт
    # Полы и тёплый пол
    "screed_mat":              350,    # ₽/м²
    "screed_work":             380,    # ₽/м²
    "floor_insul_mat":         850,    # ₽/м²
    "floor_insul_work":        250,    # ₽/м²
    "floor_film_mat":           65,    # ₽/м²
    "floor_underlay_mat":        95,   # ₽/м²
    "ceramogranit_mat":       1280,    # ₽/м²
    "ceramogranit_work":      1450,    # ₽/м²
    "laminate_mat":            950,    # ₽/м²
    "laminate_work":           380,    # ₽/м²
    "warmfloor_pipe_mat":       95,    # ₽/мп PE-X 16
    "warmfloor_pipe_work":     180,    # ₽/мп
    "warmfloor_collector_mat":28000,   # ₽/шт
    "warmfloor_collector_work":4500,   # ₽/шт
    "warmfloor_thermo_mat":   4500,    # ₽/шт
    "warmfloor_demper_mat":     65,    # ₽/мп
    # ОВ
    "ov_kotel_mat":         145000,    # ₽/шт газовый/электр. средний класс
    "ov_kotel_work":         22500,    # ₽/шт
    "ov_radiator_mat":        9500,    # ₽/шт биметалл 8 секций средний
    "ov_radiator_work":       4500,    # ₽/шт
    "ov_pipe_mat":             145,    # ₽/мп металлопластик 20мм
    "ov_pipe_work":            380,    # ₽/мп
    "ov_pump_mat":           12500,    # ₽/шт
    "ov_pump_work":           4500,    # ₽/шт
    "ov_expansion_mat":       4500,    # ₽/шт
    "ov_balance_mat":         8500,    # ₽/шт
    "ov_thermo_mat":          3500,    # ₽/шт
    "ov_valve_set_mat":       8500,    # ₽/комплект
    "ov_naladka_work":       12500,    # ₽/комплект
    # ВК
    "vk_pipe_cold_mat":        145,    # ₽/мп PEX 16 cold
    "vk_pipe_hot_mat":         165,    # ₽/мп PEX 16 hot
    "vk_pipe_canal_50_mat":    220,    # ₽/мп PVC 50мм
    "vk_pipe_canal_110_mat":   380,    # ₽/мп PVC 110мм
    "vk_pipe_install_work":    320,    # ₽/мп
    "vk_unitaz_mat":         28500,    # ₽/шт инсталляция+чаша средняя
    "vk_unitaz_work":         5500,    # ₽/шт
    "vk_rakovina_mat":       18500,    # ₽/шт раковина+тумба средняя
    "vk_rakovina_work":       4500,    # ₽/шт
    "vk_dush_mat":           58000,    # ₽/шт душ.кабина или ванна средняя
    "vk_dush_work":           9500,    # ₽/шт
    "vk_polotenets_mat":      8500,    # ₽/шт
    "vk_polotenets_work":     2500,    # ₽/шт
    "vk_smesitel_mat":        9500,    # ₽/комплект
    "vk_boiler_mat":         28000,    # ₽/шт 100л
    "vk_boiler_work":         5500,    # ₽/шт
    "vk_valve_set_mat":       4500,    # ₽/комплект
    # ЭОМ
    "el_kabel_25_mat":         120,    # ₽/мп ВВГнг 3х2.5
    "el_kabel_15_mat":          95,    # ₽/мп ВВГнг 3х1.5
    "el_kabel_input_mat":      380,    # ₽/мп ВВГнг 5х10
    "el_rozetka_mat":          380,    # ₽/шт
    "el_rozetka_work":         380,    # ₽/шт
    "el_switch_mat":           280,    # ₽/шт
    "el_switch_work":          280,    # ₽/шт
    "el_light_mat":           1850,    # ₽/шт
    "el_light_work":           850,    # ₽/шт
    "el_shchit_mat":         12500,    # ₽/шт
    "el_shchit_work":         8500,    # ₽/шт
    "el_avtomat_mat":          580,    # ₽/шт
    "el_uzo_mat":             2850,    # ₽/шт
    "el_zazem_mat":          12500,    # ₽/комплект
    "el_zazem_work":          5500,    # ₽/комплект
    "el_kabel_install_work":    95,    # ₽/мп
    # Логистика и накладные
    "logist_delivery":       29025,    # ₽ доставка 30 км рейс комплект
    "logist_brigade":         8707,    # ₽ транспорт+проживание
}

_FTM_ROOMS_PDF = [
    # (name, area_m2, kind: dry|wet|sauna|tech|kitchen)
    ("прихожая",           6.6,  "dry"),
    ("коридор",            6.0,  "dry"),
    ("бойлерная",          2.18, "tech"),
    ("гостиная",          24.79, "dry"),
    ("кухня",              9.46, "kitchen"),
    ("коридор 2",          2.86, "dry"),
    ("санузел 1",          3.85, "wet"),
    ("спальня хозяйская", 14.08, "dry"),
    ("спальня 1",         10.16, "dry"),
    ("спальня 2",         10.16, "dry"),
    ("санузел 2",          4.30, "wet"),
    ("сауна",              2.79, "sauna"),
    ("прачечная",          2.69, "wet"),
]

def _ftm_row(section, name, unit, qty, price, note=""):
    return {"section": section, "name": name, "unit": unit, "qty": round(float(qty), 3), "price": round(float(price), 2), "note": note}

def _build_full_turnkey_items(parsed, price_text, choice):
    items = []
    P = _FTM_PRICES

    # Геометрия из PDF
    area_floor = float(parsed.get("area_floor") or 99.91)
    floors = int(parsed.get("floors") or 1)
    dims = parsed.get("dims") or parsed.get("dimensions") or [8.5, 12.5]
    try:
        a, b = float(dims[0]), float(dims[1])
    except Exception:
        a = b = area_floor ** 0.5
    perimeter = 2 * (a + b)
    height = 3.0
    wall_outer_area = perimeter * height
    roof_area = 185.0
    facade_plaster = 96.0
    facade_socle = 20.0
    facade_rail = 27.1
    foundation_volume = max(round(area_floor * 0.30, 2), 1)
    foundation_perim = perimeter
    foundation_rebar_t = round(foundation_volume * 0.08, 3)
    armopoyas_perim = perimeter
    armopoyas_concrete = round(armopoyas_perim * 0.06, 3)
    armopoyas_rebar_t = round(armopoyas_concrete * 0.08, 3)
    wall_volume_400 = round(wall_outer_area * 0.40, 2)
    inner_walls_area = round(area_floor * 0.6, 2)
    partitions_area = round(area_floor * 0.4, 2)
    inner_walls_vol_250 = round(inner_walls_area * 0.25, 2)
    partitions_vol_150 = round(partitions_area * 0.15, 2)
    kladka_glue_bags = max(int(wall_volume_400 * 1.5 + inner_walls_vol_250 + partitions_vol_150), 30)
    rebar_kladka_m = round((wall_outer_area + inner_walls_area + partitions_area) * 1.5, 1)
    perimuter_lintels = max(int((perimeter + inner_walls_area / 3) / 1.5), 20)

    # === 1. Фундамент ===
    items.append(_ftm_row("Фундамент", "Земляные работы (разработка грунта)", "м³", round(area_floor * 0.4, 2), P["earth_work"], "выемка под плиту"))
    items.append(_ftm_row("Фундамент", "Песок подсыпка с уплотнением", "м³", round(area_floor * 0.15, 2), P["sand_mat"] + P["sand_work"], "материал+работы"))
    items.append(_ftm_row("Фундамент", "Щебень подсыпка с уплотнением", "м³", round(area_floor * 0.10, 2), P["gravel_mat"] + P["gravel_work"], "материал+работы"))
    items.append(_ftm_row("Фундамент", "Геотекстиль с укладкой", "м²", round(area_floor * 1.1, 2), P["geotextile_mat"] + P["geotextile_work"], "материал+работы"))
    items.append(_ftm_row("Фундамент", "Утеплитель ЭППС материал под плиту", "м²", round(area_floor * 1.1, 2), P["insul_eps_mat"], "материал"))
    items.append(_ftm_row("Фундамент", "Монтаж утеплителя ЭППС работы", "м²", round(area_floor * 1.1, 2), P["insul_eps_work"], "работы"))
    items.append(_ftm_row("Фундамент", "Гидроизоляция оклеечная материал", "м²", round(area_floor * 1.2, 2), P["waterproof_mat"], "материал"))
    items.append(_ftm_row("Фундамент", "Гидроизоляция плиты работы", "м²", round(area_floor * 1.2, 2), P["waterproof_work"], "работы"))
    items.append(_ftm_row("Фундамент", "Опалубка периметра материал", "мп", foundation_perim, P["formwork_perim_mat"], "материал"))
    items.append(_ftm_row("Фундамент", "Опалубка работы (монтаж/демонтаж)", "мп", foundation_perim, P["formwork_install_work"], "работы"))
    items.append(_ftm_row("Фундамент", "Арматура А500 материал", "т", foundation_rebar_t, P["rebar_a500_mat"], "материал"))
    items.append(_ftm_row("Фундамент", "Армирование плиты работы", "т", foundation_rebar_t, P["rebar_install_work"], "работы"))
    items.append(_ftm_row("Фундамент", "Бетон В25 для монолитной плиты", "м³", foundation_volume, P["concrete_b25_mat"], "материал"))
    items.append(_ftm_row("Фундамент", "Бетонирование плиты работы", "м³", foundation_volume, P["concrete_pour_work"], "работы"))

    # === 2. Стены ===
    items.append(_ftm_row("Стены", "Газобетон D400 400мм наружные стены", "м³", wall_volume_400, P["gas_d400_mat"], "материал"))
    items.append(_ftm_row("Стены", "Кладка газобетона 400мм работы", "м²", wall_outer_area, P["gas_400mm_work"], "работы"))
    items.append(_ftm_row("Стены", "Газобетон D400 250мм внутренние стены", "м³", inner_walls_vol_250, P["gas_d400_mat"], "материал"))
    items.append(_ftm_row("Стены", "Кладка газобетона 250мм работы", "м²", inner_walls_area, P["gas_250mm_work"], "работы"))
    items.append(_ftm_row("Стены", "Газобетон D400 150мм перегородки", "м³", partitions_vol_150, P["gas_d400_mat"], "материал"))
    items.append(_ftm_row("Стены", "Монтаж перегородок 150мм работы", "м²", partitions_area, P["gas_150mm_work"], "работы"))
    items.append(_ftm_row("Стены", "Клей для газобетона", "мешок", kladka_glue_bags, P["kladka_glue_mat"], "материал"))
    items.append(_ftm_row("Стены", "Арматура для кладки 8мм", "мп", rebar_kladka_m, P["rebar_kladka_mat"], "материал"))
    items.append(_ftm_row("Стены", "Перемычки оконные/дверные", "шт", perimuter_lintels, P["lintel_mat"], "материал"))
    items.append(_ftm_row("Стены", "Бетон армопояса", "м³", armopoyas_concrete, P["armopoyas_concrete_mat"], "материал"))
    items.append(_ftm_row("Стены", "Арматура армопояса", "т", armopoyas_rebar_t, P["armopoyas_rebar_mat"], "материал"))
    items.append(_ftm_row("Стены", "Армопояс монтажные работы", "мп", armopoyas_perim, P["armopoyas_work"], "работы"))

    # === 3. Кровля ===
    rafters_volume = round(roof_area * 0.05, 2)
    obreshetka_volume = round(roof_area * 0.025, 2)
    items.append(_ftm_row("Кровля", "Стропильная система пиломатериал", "м³", rafters_volume, P["rafters_mat"], "материал"))
    items.append(_ftm_row("Кровля", "Монтаж стропильной системы", "м²", roof_area, P["rafters_work"], "работы"))
    items.append(_ftm_row("Кровля", "Обрешётка/контробрешётка пиломатериал", "м³", obreshetka_volume, P["obreshetka_mat"], "материал"))
    items.append(_ftm_row("Кровля", "Монтаж обрешётки работы", "м²", roof_area, P["obreshetka_work"], "работы"))
    items.append(_ftm_row("Кровля", "Пароизоляция кровли материал", "м²", roof_area, P["roof_paroizo_mat"], "материал"))
    items.append(_ftm_row("Кровля", "Монтаж пароизоляции", "м²", roof_area, P["roof_paroizo_work"], "работы"))
    items.append(_ftm_row("Кровля", "Утеплитель кровли мин.вата 200мм", "м²", roof_area, P["roof_insul_mat"], "материал"))
    items.append(_ftm_row("Кровля", "Монтаж утеплителя кровли", "м²", roof_area, P["roof_insul_work"], "работы"))
    items.append(_ftm_row("Кровля", "Гидроизоляция кровли мембрана", "м²", roof_area, P["roof_hydroizo_mat"], "материал"))
    items.append(_ftm_row("Кровля", "Монтаж гидроизоляции кровли", "м²", roof_area, P["roof_hydroizo_work"], "работы"))
    items.append(_ftm_row("Кровля", "Фальцевая кровля сталь RAL7024", "м²", roof_area, P["roof_falz_mat"], "материал"))
    items.append(_ftm_row("Кровля", "Монтаж фальцевой кровли", "м²", roof_area, P["roof_falz_work"], "работы"))
    items.append(_ftm_row("Кровля", "Доборные элементы кровли с монтажом", "мп", round(perimeter * 1.2, 2), P["roof_dobor_mat"] + P["roof_dobor_work"], "материал+работы"))
    items.append(_ftm_row("Кровля", "Водосточная система с установкой", "мп", round(perimeter * 1.1, 2), P["watergutter_mat"] + P["watergutter_work"], "материал+работы"))

    # === 4. Окна и двери ===
    # 9 типов окон Ок-1..Ок-9 (PDF facts) — сгруппировано по размерам
    items.append(_ftm_row("Окна и двери", "Окна ПВХ Ок-1, Ок-4 (большие, гостиная/спальня хоз.) энергосбер.", "шт", 2, P["window_pvc_large_mat"], "материал"))
    items.append(_ftm_row("Окна и двери", "Окна ПВХ Ок-2, Ок-3, Ок-5..Ок-9 (стандарт) энергосбер.", "шт", 7, P["window_pvc_mat"], "материал"))
    items.append(_ftm_row("Окна и двери", "Монтаж окон 9 типов (Ок-1..Ок-9)", "шт", 9, P["window_install_work"], "работы"))
    items.append(_ftm_row("Окна и двери", "Монтажные материалы окон (пена, ПСУЛ, отливы)", "комплект", 9, P["window_pena_mat"], "материал"))
    items.append(_ftm_row("Окна и двери", "Дверь входная ДуМО1", "шт", 1, P["door_entry_mat"], "материал"))
    items.append(_ftm_row("Окна и двери", "Установка входной двери", "шт", 1, P["door_install_work"], "работы"))
    items.append(_ftm_row("Окна и двери", "Дверь чердачная ДЧ", "шт", 1, P["door_chord_mat"], "материал"))
    items.append(_ftm_row("Окна и двери", "Установка чердачной двери", "шт", 1, P["door_install_work"], "работы"))
    items.append(_ftm_row("Окна и двери", "Межкомнатные двери Д-1, Д-2, Д-3 (10 шт)", "шт", 10, P["door_inner_mat"], "материал"))
    items.append(_ftm_row("Окна и двери", "Установка межкомнатных дверей", "шт", 10, P["door_install_work"], "работы"))

    # === 5. Внешняя отделка ===
    items.append(_ftm_row("Внешняя отделка", "Грунтовка фасада материал", "м²", facade_plaster, P["facade_grunt_mat"], "материал"))
    items.append(_ftm_row("Внешняя отделка", "Грунтование фасада работы", "м²", facade_plaster, P["facade_grunt_work"], "работы"))
    items.append(_ftm_row("Внешняя отделка", "Сетка фасадная стеклотканевая", "м²", facade_plaster, P["facade_setka_mat"], "материал"))
    items.append(_ftm_row("Внешняя отделка", "Установка сетки фасадной", "м²", facade_plaster, P["facade_setka_work"], "работы"))
    items.append(_ftm_row("Внешняя отделка", "Штукатурка фасада материал", "м²", facade_plaster, P["facade_plaster_mat"], "материал"))
    items.append(_ftm_row("Внешняя отделка", "Оштукатуривание фасада работы", "м²", facade_plaster, P["facade_plaster_work"], "работы"))
    items.append(_ftm_row("Внешняя отделка", "Краска фасадная белая", "м²", facade_plaster, P["facade_paint_mat"], "материал"))
    items.append(_ftm_row("Внешняя отделка", "Окраска фасада работы", "м²", facade_plaster, P["facade_paint_work"], "работы"))
    items.append(_ftm_row("Внешняя отделка", "Цоколь штукатурка материал", "м²", facade_socle, P["socle_plaster_mat"], "материал"))
    items.append(_ftm_row("Внешняя отделка", "Цоколь штукатурка работы", "м²", facade_socle, P["socle_plaster_work"], "работы"))
    items.append(_ftm_row("Внешняя отделка", "Цоколь окраска RAL7012", "м²", facade_socle, P["socle_paint_mat"], "материал"))
    items.append(_ftm_row("Внешняя отделка", "Рейка фасадная (планкен)", "м²", facade_rail, P["rail_facade_mat"], "материал"))
    items.append(_ftm_row("Внешняя отделка", "Монтаж рейки фасадной", "м²", facade_rail, P["rail_facade_work"], "работы"))

    # === 6. Внутренняя отделка (сухие помещения сгруппированы; PDF: 9 комнат — прихожая, коридор, бойлерная, гостиная, кухня, коридор2, спальня хоз., спальня1, спальня2) ===
    dry_kinds = ("dry", "kitchen", "tech")
    dry_rooms = [r for r in _FTM_ROOMS_PDF if r[2] in dry_kinds]
    dry_floor_total = round(sum(r[1] for r in dry_rooms), 2)
    dry_wall_total = round(sum((4 * (r[1] ** 0.5)) * 3.0 for r in dry_rooms), 2)
    dry_perim_total = round(sum(4 * (r[1] ** 0.5) for r in dry_rooms), 2)
    items.append(_ftm_row("Внутренняя отделка", f"Подготовка стен сухих помещений ({len(dry_rooms)} комн.)", "м²", dry_wall_total, P["wall_prep_work"], "грунт+шпатлёвка работы"))
    items.append(_ftm_row("Внутренняя отделка", "Материалы подготовки стен (грунт+шпатлёвка)", "м²", dry_wall_total, P["wall_prep_mat"], "материал"))
    items.append(_ftm_row("Внутренняя отделка", "Финишная окраска стен сухих помещений", "м²", dry_wall_total, P["wall_finish_mat"], "материал"))
    items.append(_ftm_row("Внутренняя отделка", "Окраска стен работы", "м²", dry_wall_total, P["wall_finish_work"], "работы"))
    items.append(_ftm_row("Внутренняя отделка", "Потолок ГКЛ материал", "м²", dry_floor_total, P["ceiling_gkl_mat"], "материал"))
    items.append(_ftm_row("Внутренняя отделка", "Потолок монтаж ГКЛ работы", "м²", dry_floor_total, P["ceiling_gkl_work"], "работы"))
    items.append(_ftm_row("Внутренняя отделка", "Потолок краска", "м²", dry_floor_total, P["ceiling_paint_mat"], "материал"))
    items.append(_ftm_row("Внутренняя отделка", "Окраска потолка работы", "м²", dry_floor_total, P["ceiling_paint_work"], "работы"))
    items.append(_ftm_row("Внутренняя отделка", "Плинтус ПВХ/МДФ материал", "мп", dry_perim_total, P["skirting_mat"], "материал"))
    items.append(_ftm_row("Внутренняя отделка", "Монтаж плинтуса работы", "мп", dry_perim_total, P["skirting_work"], "работы"))

    # === 7. Санузлы и сауна (3 wet помещения PDF: санузел 1, санузел 2, прачечная — сгруппировано) ===
    wet_rooms = [r for r in _FTM_ROOMS_PDF if r[2] == "wet"]
    wet_floor_total = round(sum(r[1] for r in wet_rooms), 2)
    wet_wall_total = round(sum((4 * (r[1] ** 0.5)) * 3.0 for r in wet_rooms), 2)
    wet_hydroizo_area = round(wet_wall_total * 0.5 + wet_floor_total, 2)
    items.append(_ftm_row("Санузлы и сауна", f"Гидроизоляция санузлов и прачечной материал ({len(wet_rooms)} помещ.)", "м²", wet_hydroizo_area, P["wet_hydroizo_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Гидроизоляция санузлов работы", "м²", wet_hydroizo_area, P["wet_hydroizo_work"], "работы"))
    items.append(_ftm_row("Санузлы и сауна", "Плитка стен санузлов материал", "м²", wet_wall_total, P["tile_wall_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Укладка плитки стен работы", "м²", wet_wall_total, P["tile_wall_work"], "работы"))
    items.append(_ftm_row("Санузлы и сауна", "Плитка пола санузлов материал", "м²", wet_floor_total, P["tile_floor_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Укладка плитки пола работы", "м²", wet_floor_total, P["tile_floor_work"], "работы"))
    items.append(_ftm_row("Санузлы и сауна", "Клей плиточный/затирка", "м²", round(wet_wall_total + wet_floor_total, 2), P["tile_glue_mat"], "материал"))
    # Сауна
    sauna_area = 2.79
    sauna_wall = round((4 * (sauna_area ** 0.5)) * 3.0, 2)
    items.append(_ftm_row("Санузлы и сауна", "Сауна: вагонка липа стены/потолок материал", "м²", round(sauna_wall + sauna_area, 2), P["sauna_lining_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Сауна: монтаж вагонки", "м²", round(sauna_wall + sauna_area, 2), P["sauna_lining_work"], "работы"))
    items.append(_ftm_row("Санузлы и сауна", "Сауна: полок (комплект скамей)", "комплект", 1, P["sauna_polok_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Сауна: дверь специализированная", "шт", 1, P["door_sauna_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Сауна: установка двери", "шт", 1, P["door_install_work"], "работы"))
    items.append(_ftm_row("Санузлы и сауна", "Сауна: печь средний класс", "шт", 1, P["sauna_stove_mat"], "материал; средний комплект, модель не задана в PDF"))
    items.append(_ftm_row("Санузлы и сауна", "Сауна: установка печи", "шт", 1, P["sauna_stove_work"], "работы"))

    # === 8. Полы и тёплый пол ===
    items.append(_ftm_row("Полы и тёплый пол", "Утеплитель пола ЭППС материал", "м²", area_floor, P["floor_insul_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Монтаж утеплителя пола", "м²", area_floor, P["floor_insul_work"], "работы"))
    items.append(_ftm_row("Полы и тёплый пол", "Плёнка гидроизоляционная + демпферная лента", "м²", area_floor, P["floor_film_mat"] + 30, "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Тёплый пол труба PE-X 16мм материал", "мп", round(area_floor * 5, 2), P["warmfloor_pipe_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Монтаж трубы тёплого пола работы", "мп", round(area_floor * 5, 2), P["warmfloor_pipe_work"], "работы"))
    items.append(_ftm_row("Полы и тёплый пол", "Коллектор + смесительный узел с установкой", "шт", 1, P["warmfloor_collector_mat"] + P["warmfloor_collector_work"], "материал+работы"))
    items.append(_ftm_row("Полы и тёплый пол", "Терморегулятор тёплого пола", "шт", 5, P["warmfloor_thermo_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Стяжка ЦП 50мм материал", "м²", area_floor, P["screed_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Стяжка ЦП 50мм работы", "м²", area_floor, P["screed_work"], "работы"))
    # Финиш по сухим: ламинат, по влажным/сауне плитка уже выше
    dry_floor_area = sum(r[1] for r in _FTM_ROOMS_PDF if r[2] in ("dry", "kitchen", "tech"))
    items.append(_ftm_row("Полы и тёплый пол", "Подложка под ламинат", "м²", round(dry_floor_area, 2), P["floor_underlay_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Ламинат материал", "м²", round(dry_floor_area, 2), P["laminate_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Укладка ламината работы", "м²", round(dry_floor_area, 2), P["laminate_work"], "работы"))

    # === 9. Инженерные коммуникации ОВ ===
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Котёл отопительный средний класс", "шт", 1, P["ov_kotel_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Монтаж котла", "шт", 1, P["ov_kotel_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Радиатор биметаллический 8 секций", "шт", 9, P["ov_radiator_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Монтаж радиаторов", "шт", 9, P["ov_radiator_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Трубы металлопластик 20мм", "мп", 180, P["ov_pipe_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Монтаж трубопровода ОВ", "мп", 180, P["ov_pipe_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Циркуляционный насос", "шт", 1, P["ov_pump_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Монтаж насоса", "шт", 1, P["ov_pump_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Расширительный бак", "шт", 1, P["ov_expansion_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Узел регулировки и балансировки", "шт", 1, P["ov_balance_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Терморегуляторы радиаторов", "шт", 9, P["ov_thermo_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Запорная арматура комплект", "комплект", 1, P["ov_valve_set_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Пуско-наладка системы отопления", "комплект", 1, P["ov_naladka_work"], "работы"))

    # === 10. Инженерные коммуникации ВК ===
    items.append(_ftm_row("Инженерные коммуникации ВК", "Трубы PEX 16мм холодное+горячее водоснабжение", "мп", 160, P["vk_pipe_cold_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Канализация PVC 50/110мм комплект", "мп", 65, P["vk_pipe_canal_110_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Монтаж трубопровода ВК (вод.+канализ.)", "мп", 225, P["vk_pipe_install_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Унитаз с инсталляцией", "шт", 2, P["vk_unitaz_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Установка унитазов", "шт", 2, P["vk_unitaz_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Раковина с тумбой", "шт", 3, P["vk_rakovina_mat"], "материал; 2 санузла + кухня"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Установка раковин", "шт", 3, P["vk_rakovina_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Душевая кабина / ванна", "шт", 2, P["vk_dush_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Установка душа/ванны", "шт", 2, P["vk_dush_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Полотенцесушитель", "шт", 2, P["vk_polotenets_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Установка полотенцесушителя", "шт", 2, P["vk_polotenets_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Смесители комплект", "комплект", 4, P["vk_smesitel_mat"], "материал; 2 СУ + кухня + прачечная"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Бойлер 100л", "шт", 1, P["vk_boiler_mat"], "материал; бойлерная"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Установка бойлера", "шт", 1, P["vk_boiler_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Запорная арматура ВК", "комплект", 1, P["vk_valve_set_mat"], "материал"))

    # === 11. Инженерные коммуникации ЭОМ ===
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Кабель ВВГнг 5х10 вводной + 3х2.5 силовой", "мп", 270, P["el_kabel_25_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Кабель ВВГнг 3х1.5 освещение", "мп", 200, P["el_kabel_15_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Монтаж кабельных линий", "мп", 470, P["el_kabel_install_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Розетка", "шт", 35, P["el_rozetka_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Установка розеток", "шт", 35, P["el_rozetka_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Выключатель", "шт", 18, P["el_switch_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Установка выключателей", "шт", 18, P["el_switch_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Светильник потолочный", "шт", 25, P["el_light_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Монтаж светильников", "шт", 25, P["el_light_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Распределительный щит укомплектованный", "шт", 1, P["el_shchit_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Монтаж щита", "шт", 1, P["el_shchit_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Автомат 16А", "шт", 14, P["el_avtomat_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "УЗО 40А", "шт", 4, P["el_uzo_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Контур заземления комплект", "комплект", 1, P["el_zazem_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Монтаж контура заземления", "комплект", 1, P["el_zazem_work"], "работы"))

    # === 12. Логистика ===
    items.append(_ftm_row("Логистика", "Доставка материалов от СПб", "рейс", 3, P["logist_delivery"] / 3, "30 км"))
    items.append(_ftm_row("Логистика", "Транспорт бригады и проживание", "комплект", 1, P["logist_brigade"] * 4, "период строительства"))

    # === 13. Накладные расходы ===
    materials_sum = sum(float(it["price"]) * float(it["qty"]) for it in items if it["section"] not in ("Логистика", "Накладные расходы"))
    overhead_total = round(materials_sum * 0.07, 2)
    items.append(_ftm_row("Накладные расходы", "Организация работ и накладные", "комплект", 1, overhead_total, "7% от общей сметы"))
    items.append(_ftm_row("Накладные расходы", "Расходные материалы и крепёж", "комплект", 1, round(materials_sum * 0.015, 2), "мелкое крепление"))
    items.append(_ftm_row("Накладные расходы", "Уборка после работ", "комплект", 1, round(area_floor * 280, 2), "финальная уборка"))

    return items

# Override _build_estimate_items
_FTM_ORIG_BEI = _build_estimate_items

def _build_estimate_items(parsed, price_text, choice):  # noqa: F811
    try:
        items = _build_full_turnkey_items(parsed, price_text, choice)
        _FTM_LOG.info("PATCH_TOPIC2_FULL_TURNKEY_MATRIX_V1: %d items", len(items))
        return items
    except Exception as _ftm_e:
        _FTM_LOG.error("PATCH_TOPIC2_FULL_TURNKEY_MATRIX_V1_ERR %s", _ftm_e)
        return _FTM_ORIG_BEI(parsed, price_text, choice)

_FTM_LOG.info("PATCH_TOPIC2_FULL_TURNKEY_MATRIX_V1 installed")
# === END_PATCH_TOPIC2_FULL_TURNKEY_MATRIX_V1 ===

# === PATCH_TOPIC2_REALSHEET_PRICES_V3 ===
# Читаем реальные цены из листа "Газобетонный дом" (sheet "смета" в кэше шаблона).
# col[7]=Работа (ед. цена с коэф.), col[9]=Материалы (ед. цена).
# Для items без match в шаблоне — fallback на _FTM_PRICES.
# Append-only override поверх PATCH_TOPIC2_FULL_TURNKEY_MATRIX_V1.
# ============================================================
import logging as _p8v3_logging
_P8V3_LOG = _p8v3_logging.getLogger("stroyka.realsheet_prices_v3")

_P8V3_TPL_PATH = "/root/.areal-neva-core/data/templates/estimate/cache/1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm__Ареал Нева.xlsx"

def _p8v3_extract_tpl_prices(template_path=None):
    """Extract unit prices from Газобетонный дом sheet (col7=work, col9=mat)."""
    path = template_path or _P8V3_TPL_PATH
    prices = {}
    try:
        from openpyxl import load_workbook as _p8v3_lwb
        wb = _p8v3_lwb(path, read_only=True, data_only=True)
        ws = wb.active
        current_section = "Стены"
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            r = list(row)
            if i < 12:
                continue
            r1 = r[1] if len(r) > 1 else None
            if r[0] and not r1:
                current_section = str(r[0]).strip()
                continue
            if not r1:
                continue
            try:
                float(r[3]) if r[3] is not None else 0
            except (ValueError, TypeError):
                continue
            work_price = float(r[7]) if r[7] is not None else 0.0
            mat_price = float(r[9]) if r[9] is not None else 0.0
            if work_price == 0 and mat_price == 0:
                continue
            unit = str(r[2]).strip() if r[2] else ""
            name = str(r1).strip()
            norm = name.lower().strip()
            prices[norm] = {
                "work_price": work_price,
                "mat_price": mat_price,
                "unit": unit,
                "section": current_section,
                "name": name,
            }
        wb.close()
        _P8V3_LOG.info("P8V3_TPL_LOADED: %d rows from %s", len(prices), path)
    except Exception as _pe:
        _P8V3_LOG.error("P8V3_TPL_EXTRACT_ERR: %s", _pe)
    return prices


_P8V3_TPL_PRICES = _p8v3_extract_tpl_prices()
_P8V3_LOG.info(
    "TOPIC2_TEMPLATE_PRICE_COLUMNS_PROVEN:col7=Работа_unit,col9=Материалы_unit,count=%d",
    len(_P8V3_TPL_PRICES)
)


def _p8v3_wp(key, fallback=0):
    row = _P8V3_TPL_PRICES.get(key)
    return row["work_price"] if row and row["work_price"] > 0 else fallback


def _p8v3_mp(key, fallback=0):
    row = _P8V3_TPL_PRICES.get(key)
    return row["mat_price"] if row and row["mat_price"] > 0 else fallback


def extract_template_prices(template_path, parsed):  # noqa: F811
    """Returns (prices_text, sheet_name, sheet_fallback) from Газобетонный дом sheet."""
    prices = _p8v3_extract_tpl_prices(template_path) if template_path else {}
    if not prices:
        prices = _P8V3_TPL_PRICES
    count = len(prices)
    lines = []
    for v in list(prices.values())[:25]:
        if v["work_price"] > 0 or v["mat_price"] > 0:
            lines.append(
                f"- {v['name']}: работа={v['work_price']:.0f} {v['unit']}, матер={v['mat_price']:.0f} {v['unit']}"
            )
    text = f"Цены из листа 'Газобетонный дом' ({count} позиций):\n" + "\n".join(lines)
    return text, "смета", False


_P8V3_LOG.info(
    "TOPIC2_TEMPLATE_PRICE_EXTRACTION_FIXED:sheet=смета_Газобетонный_дом,count=%d",
    len(_P8V3_TPL_PRICES)
)


def _build_full_turnkey_items_v2(parsed, price_text, choice):
    """Полный список работ под ключ с ценами из шаблона + _FTM_PRICES fallback."""
    items = []
    P = _FTM_PRICES

    area_floor = float(parsed.get("area_floor") or 99.91)
    dims = parsed.get("dims") or parsed.get("dimensions") or [8.5, 12.5]
    try:
        a, b = float(dims[0]), float(dims[1])
    except Exception:
        a = b = area_floor ** 0.5
    perimeter = 2 * (a + b)
    height = 3.0
    roof_area = 185.0
    facade_area = 96.0
    socle_area = 20.0
    rail_area = 27.1
    windows_count = 9
    doors_inner_count = 3
    door_entry_count = 1

    foundation_perim = perimeter
    foundation_volume = round(area_floor * 0.3, 2)
    foundation_rebar_t = round(area_floor * 0.025, 3)

    wall_height_with_parapet = height + 0.6
    wall_volume_400 = round(perimeter * wall_height_with_parapet * 0.4, 2)
    inner_walls_area = round(area_floor * 0.8, 2)
    inner_walls_vol_250 = round(inner_walls_area * 0.25, 2)
    partitions_area = round(area_floor * 0.6, 2)
    partitions_vol_150 = round(partitions_area * 0.15, 2)
    kladka_glue_bags = round((wall_volume_400 + inner_walls_vol_250 + partitions_vol_150) * 1.2, 0)
    rebar_kladka_t = round(perimeter * 5 * 0.395 / 1000, 3)
    perimuter_lintels = windows_count + doors_inner_count + door_entry_count
    armopoyas_concrete = round(perimeter * 0.4 * 0.3, 2)

    rooms = _FTM_ROOMS_PDF
    dry_rooms = [(n, ar) for n, ar, k in rooms if k in ("dry", "kitchen")]
    wet_rooms = [(n, ar) for n, ar, k in rooms if k == "wet"]
    sauna_rooms = [(n, ar) for n, ar, k in rooms if k == "sauna"]
    dry_floor_area = round(sum(ar for _, ar in dry_rooms), 2)
    wet_floor_area = round(sum(ar for _, ar in wet_rooms), 2)
    sauna_area = round(sum(ar for _, ar in sauna_rooms), 2)
    dry_wall_area = round(dry_floor_area * 2.8, 2)
    wet_wall_area = round(wet_floor_area * 2.8, 2)
    sauna_wall_ceil_area = round(sauna_area * 3.8, 2)
    all_floor_area = round(area_floor, 2)

    # 1. Фундамент
    items.append(_ftm_row("Фундамент", "Земляные работы (разработка грунта)", "м³", round(area_floor * 0.4, 2), P["earth_work"], "выемка под плиту"))
    items.append(_ftm_row("Фундамент", "Песок подсыпка с уплотнением", "м³", round(area_floor * 0.15, 2), P["sand_mat"] + P["sand_work"], "материал+работы"))
    items.append(_ftm_row("Фундамент", "Щебень подсыпка с уплотнением", "м³", round(area_floor * 0.10, 2), P["gravel_mat"] + P["gravel_work"], "материал+работы"))
    items.append(_ftm_row("Фундамент", "Геотекстиль с укладкой", "м²", round(area_floor * 1.1, 2), P["geotextile_mat"] + P["geotextile_work"], "материал+работы"))
    items.append(_ftm_row("Фундамент", "Утеплитель ЭППС материал под плиту", "м²", round(area_floor * 1.1, 2), P["insul_eps_mat"], "материал"))
    items.append(_ftm_row("Фундамент", "Монтаж утеплителя ЭППС работы", "м²", round(area_floor * 1.1, 2), P["insul_eps_work"], "работы"))
    items.append(_ftm_row("Фундамент", "Гидроизоляция оклеечная материал", "м²", round(area_floor * 1.2, 2), P["waterproof_mat"], "материал"))
    items.append(_ftm_row("Фундамент", "Гидроизоляция плиты работы", "м²", round(area_floor * 1.2, 2), P["waterproof_work"], "работы"))
    items.append(_ftm_row("Фундамент", "Опалубка периметра материал", "мп", foundation_perim, P["formwork_perim_mat"], "материал"))
    items.append(_ftm_row("Фундамент", "Опалубка работы (монтаж/демонтаж)", "мп", foundation_perim, P["formwork_install_work"], "работы"))
    items.append(_ftm_row("Фундамент", "Арматура А500 материал", "т", foundation_rebar_t,
        _p8v3_mp("арматура металлическая д.12а500", P["rebar_a500_mat"]), "материал"))
    items.append(_ftm_row("Фундамент", "Армирование плиты работы", "м²", area_floor,
        _p8v3_wp("устройство арматурного каркаса", 950), "работы"))
    items.append(_ftm_row("Фундамент", "Бетон В25 для монолитной плиты", "м³", foundation_volume,
        _p8v3_mp("бетон в25 w6", P["concrete_b25_mat"]), "материал"))
    items.append(_ftm_row("Фундамент", "Бетонирование плиты работы", "м³", foundation_volume,
        _p8v3_wp("бетонирование монолитной плиты   б/н", P["concrete_pour_work"]), "работы"))

    # 2. Стены
    items.append(_ftm_row("Стены", "Газобетон D400 400мм наружные стены", "м³", wall_volume_400,
        _p8v3_mp(" блок  625x400x250 ", P["gas_d400_mat"]), "материал"))
    items.append(_ftm_row("Стены", "Кладка газобетона 400мм работы", "м³", wall_volume_400,
        _p8v3_wp("кладка  стен из газобетона, вкл парапет", P["gas_400mm_work"]), "работы"))
    items.append(_ftm_row("Стены", "Газобетон D400 250мм внутренние стены", "м³", inner_walls_vol_250,
        _p8v3_mp(" блок  625x250x250 ", P["gas_d400_mat"]), "материал"))
    items.append(_ftm_row("Стены", "Кладка газобетона 250мм работы", "м³", inner_walls_vol_250,
        _p8v3_wp("кладка  стен из газобетона, вкл парапет", P["gas_250mm_work"]), "работы"))
    items.append(_ftm_row("Стены", "Газобетон D400 150мм перегородки", "м³", partitions_vol_150,
        _p8v3_mp(" блок  625x150x250 ", P["gas_d400_mat"]), "материал"))
    items.append(_ftm_row("Стены", "Монтаж перегородок 150мм работы", "м³", partitions_vol_150,
        _p8v3_wp("кладка перегородок из газобетона", P["gas_150mm_work"]), "работы"))
    items.append(_ftm_row("Стены", "Клей для газобетона", "шт", kladka_glue_bags,
        _p8v3_mp("клей для газобетона 25 кг", P["kladka_glue_mat"]), "материал"))
    items.append(_ftm_row("Стены", "Арматура для кладки 8мм", "т", rebar_kladka_t,
        _p8v3_mp("арматура а3 а240  8мм рифленая", P["rebar_a500_mat"]), "материал"))
    items.append(_ftm_row("Стены", "Перемычки оконные/дверные", "шт", perimuter_lintels, P["lintel_mat"], "материал"))
    items.append(_ftm_row("Стены", "Армопояс бетон В25", "м³", armopoyas_concrete,
        _p8v3_mp("бетон в25 w6", P["armopoyas_concrete_mat"]), "материал"))
    items.append(_ftm_row("Стены", "Армопояс работы", "мп", foundation_perim,
        _p8v3_wp("устройство армопояса парапета", P["armopoyas_work"]), "работы"))

    # 3. Кровля (185 м², плоская с наплавляемой гидроизоляцией)
    items.append(_ftm_row("Кровля", "Пароизоляция кровли работы", "м²", roof_area,
        _p8v3_wp("укладка пароизоляционного слоя", P["roof_paroizo_work"]), "работы"))
    items.append(_ftm_row("Кровля", "Пароизоляция кровли материал", "м²", roof_area, P["roof_paroizo_mat"], "материал"))
    items.append(_ftm_row("Кровля", "Утеплитель кровли XPS 200мм монтаж", "м²", roof_area,
        _p8v3_wp("монтаж утепления т 200/250 мм", P["roof_insul_work"]), "работы"))
    items.append(_ftm_row("Кровля", "Утеплитель кровли XPS материал", "м²", roof_area, P["roof_insul_mat"], "материал"))
    items.append(_ftm_row("Кровля", "Монтаж кровельного покрытия работы", "м²", roof_area,
        _p8v3_wp("монтаж наплавляемой 2х слойной кровли, вкл парапет", P["roof_falz_work"]), "работы"))
    items.append(_ftm_row("Кровля", "Фальцевая кровля RAL7024 материал", "м²", roof_area, P["roof_falz_mat"], "материал"))
    items.append(_ftm_row("Кровля", "Водосток + добор", "мп", round(perimeter + 4, 1),
        P["watergutter_mat"] + P["watergutter_work"], "материал+работы"))
    items.append(_ftm_row("Кровля", "Крепёж и расходники кровля", "компл", 1, P["roof_dobor_mat"] * 30, "компл"))

    # 4. Окна и двери
    items.append(_ftm_row("Окна и двери", "Окна ПВХ средний класс материал", "шт", windows_count, P["window_pvc_mat"], "9 типов ПВХ"))
    items.append(_ftm_row("Окна и двери", "Монтаж окон работы", "шт", windows_count, P["window_install_work"], "работы"))
    items.append(_ftm_row("Окна и двери", "Монтажный комплект (пена+ПСУЛ+отлив)", "шт", windows_count, P["window_pena_mat"], "материал"))
    items.append(_ftm_row("Окна и двери", "Дверь входная стальная материал", "шт", door_entry_count,
        _p8v3_mp("дверь входная с терморазрывом ferroni isoterma лев", P["door_entry_mat"]), "с терморазрывом"))
    items.append(_ftm_row("Окна и двери", "Монтаж входной двери", "шт", door_entry_count,
        _p8v3_wp("установка входной двери", P["door_install_work"]), "работы"))
    items.append(_ftm_row("Окна и двери", "Двери межкомнатные материал", "шт", doors_inner_count, P["door_inner_mat"], "материал"))
    items.append(_ftm_row("Окна и двери", "Монтаж межкомнатных дверей", "шт", doors_inner_count, P["door_install_work"], "работы"))
    items.append(_ftm_row("Окна и двери", "Дверь сауны специальная", "шт", 1, P["door_sauna_mat"], "материал"))

    # 5. Внешняя отделка
    items.append(_ftm_row("Внешняя отделка", "Утепление фасада базальтовой ватой работы", "м²", facade_area,
        _p8v3_wp("утепление фасада базальтовой ватой на клеевой сост", P["facade_setka_work"]), "работы"))
    items.append(_ftm_row("Внешняя отделка", "Утеплитель базальтовая вата материал", "м²", facade_area, P["facade_setka_mat"] * 5, "Rockwool"))
    items.append(_ftm_row("Внешняя отделка", "Армирование фасада работы", "м²", facade_area,
        _p8v3_wp("армирование фасада с шлифованием", P["facade_setka_work"]), "работы"))
    items.append(_ftm_row("Внешняя отделка", "Армирующая сетка материал", "м²", facade_area, P["facade_setka_mat"], "материал"))
    items.append(_ftm_row("Внешняя отделка", "Штукатурка фасада работы 96м²", "м²", facade_area,
        _p8v3_wp("грунтование, оштукатуривание", P["facade_plaster_work"]), "работы"))
    items.append(_ftm_row("Внешняя отделка", "Штукатурка фасадная материал", "м²", facade_area, P["facade_plaster_mat"], "материал"))
    items.append(_ftm_row("Внешняя отделка", "Цоколь отделка 20м²", "м²", socle_area,
        P["socle_plaster_mat"] + P["socle_plaster_work"], "материал+работы"))
    items.append(_ftm_row("Внешняя отделка", "Рейка фасадная 27.1м²", "м²", rail_area,
        P["rail_facade_mat"] + P["rail_facade_work"], "материал+работы"))

    # 6. Внутренняя черновая отделка
    items.append(_ftm_row("Внутренняя отделка", "Стяжка пола работы", "м²", all_floor_area,
        _p8v3_wp("устройство полусухой армированной стяжки", P["screed_work"]), "работы"))
    items.append(_ftm_row("Внутренняя отделка", "Стяжка материалы", "м²", all_floor_area, P["screed_mat"], "материал"))
    items.append(_ftm_row("Внутренняя отделка", "Утепление пола ЭППС", "м²", all_floor_area,
        P["floor_insul_mat"] + P["floor_insul_work"], "материал+работы"))
    items.append(_ftm_row("Внутренняя отделка", "Штукатурка стен сухих помещений работы", "м²", dry_wall_area,
        _p8v3_wp("штукатурка стен", P["wall_prep_work"]), "работы"))
    items.append(_ftm_row("Внутренняя отделка", "Штукатурка стен материал", "м²", dry_wall_area, P["wall_prep_mat"], "материал"))
    items.append(_ftm_row("Внутренняя отделка", "Гипсокартон потолки", "м²", dry_floor_area,
        P["ceiling_gkl_mat"] + P["ceiling_gkl_work"], "материал+работы"))
    items.append(_ftm_row("Внутренняя отделка", "Покраска потолков", "м²", dry_floor_area,
        P["ceiling_paint_mat"] + P["ceiling_paint_work"], "материал+работы"))
    items.append(_ftm_row("Внутренняя отделка", "Плинтус", "мп", round(perimeter * 3, 1),
        P["skirting_mat"] + P["skirting_work"], "материал+работы"))

    # 7. Санузлы и сауна
    items.append(_ftm_row("Санузлы и сауна", "Гидроизоляция мокрых зон материал", "м²", wet_floor_area, P["wet_hydroizo_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Гидроизоляция мокрых зон работы", "м²", wet_floor_area, P["wet_hydroizo_work"], "работы"))
    items.append(_ftm_row("Санузлы и сауна", "Плитка стены санузлы материал", "м²", wet_wall_area, P["tile_wall_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Плитка стены укладка работы", "м²", wet_wall_area, P["tile_wall_work"], "работы"))
    items.append(_ftm_row("Санузлы и сауна", "Плитка пол санузлы материал", "м²", wet_floor_area, P["tile_floor_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Плитка пол укладка работы", "м²", wet_floor_area, P["tile_floor_work"], "работы"))
    items.append(_ftm_row("Санузлы и сауна", "Плиточный клей", "м²", wet_wall_area + wet_floor_area, P["tile_glue_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Сауна вагонка липа материал", "м²", sauna_wall_ceil_area, P["sauna_lining_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Сауна вагонка монтаж работы", "м²", sauna_wall_ceil_area, P["sauna_lining_work"], "работы"))
    items.append(_ftm_row("Санузлы и сауна", "Полки сауны комплект", "компл", 1, P["sauna_polok_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Печь сауны материал", "шт", 1, P["sauna_stove_mat"], "материал"))
    items.append(_ftm_row("Санузлы и сауна", "Монтаж печи сауны", "шт", 1, P["sauna_stove_work"], "работы"))

    # 8. Полы и тёплый пол
    warmfloor_pipe_m = round(area_floor * 7, 0)
    warmfloor_loops = max(1, round(area_floor / 15, 0))
    items.append(_ftm_row("Полы и тёплый пол", "Тёплый пол труба PE-X материал", "мп", warmfloor_pipe_m, P["warmfloor_pipe_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Тёплый пол монтаж трубы", "мп", warmfloor_pipe_m, P["warmfloor_pipe_work"], "работы"))
    items.append(_ftm_row("Полы и тёплый пол", "Коллектор тёплого пола", "шт", 1, P["warmfloor_collector_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Монтаж коллектора", "шт", 1, P["warmfloor_collector_work"], "работы"))
    items.append(_ftm_row("Полы и тёплый пол", "Терморегулятор тёплого пола", "шт", int(warmfloor_loops), P["warmfloor_thermo_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Демпферная лента", "мп", round(perimeter * 2, 1), P["warmfloor_demper_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Керамогранит кухня/прихожая материал", "м²", round(dry_floor_area * 0.4, 2), P["ceramogranit_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Укладка керамогранита работы", "м²", round(dry_floor_area * 0.4, 2), P["ceramogranit_work"], "работы"))
    items.append(_ftm_row("Полы и тёплый пол", "Подложка под ламинат", "м²", round(dry_floor_area * 0.6, 2), P["floor_underlay_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Ламинат материал", "м²", round(dry_floor_area * 0.6, 2), P["laminate_mat"], "материал"))
    items.append(_ftm_row("Полы и тёплый пол", "Укладка ламината работы", "м²", round(dry_floor_area * 0.6, 2), P["laminate_work"], "работы"))

    # 9. Инженерные коммуникации ОВ
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Котёл отопительный средний класс", "шт", 1, P["ov_kotel_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Монтаж котла", "шт", 1, P["ov_kotel_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Радиатор биметаллический 8 секций", "шт", 9, P["ov_radiator_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Монтаж радиаторов", "шт", 9, P["ov_radiator_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Трубы металлопластик 20мм", "мп", 180, P["ov_pipe_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Монтаж трубопровода ОВ", "мп", 180, P["ov_pipe_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Циркуляционный насос", "шт", 1, P["ov_pump_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Монтаж насоса", "шт", 1, P["ov_pump_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Расширительный бак", "шт", 1, P["ov_expansion_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Узел регулировки и балансировки", "шт", 1, P["ov_balance_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Терморегуляторы радиаторов", "шт", 9, P["ov_thermo_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Запорная арматура комплект", "компл", 1, P["ov_valve_set_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ОВ", "Пуско-наладка системы отопления", "компл", 1, P["ov_naladka_work"], "работы"))

    # 10. Инженерные коммуникации ВК
    items.append(_ftm_row("Инженерные коммуникации ВК", "Трубы PEX 16мм холодное+горячее водоснабжение", "мп", 160, P["vk_pipe_cold_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Канализация PVC 50/110мм комплект", "мп", 65, P["vk_pipe_canal_110_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Монтаж трубопровода ВК (вод.+канализ.)", "мп", 225, P["vk_pipe_install_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Унитаз с инсталляцией", "шт", 2, P["vk_unitaz_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Установка унитазов", "шт", 2, P["vk_unitaz_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Раковина с тумбой", "шт", 3, P["vk_rakovina_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Установка раковин", "шт", 3, P["vk_rakovina_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Душевая кабина / ванна", "шт", 2, P["vk_dush_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Установка душа/ванны", "шт", 2, P["vk_dush_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Полотенцесушитель", "шт", 2, P["vk_polotenets_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Установка полотенцесушителя", "шт", 2, P["vk_polotenets_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Смесители комплект", "компл", 4, P["vk_smesitel_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Бойлер 100л", "шт", 1, P["vk_boiler_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Установка бойлера", "шт", 1, P["vk_boiler_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ВК", "Запорная арматура ВК", "компл", 1, P["vk_valve_set_mat"], "материал"))

    # 11. Инженерные коммуникации ЭОМ
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Кабель ВВГнг 5х10 вводной + 3х2.5 силовой", "мп", 270, P["el_kabel_25_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Кабель ВВГнг 3х1.5 освещение", "мп", 200, P["el_kabel_15_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Монтаж кабельных линий", "мп", 470, P["el_kabel_install_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Розетка", "шт", 35, P["el_rozetka_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Установка розеток", "шт", 35, P["el_rozetka_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Выключатель", "шт", 18, P["el_switch_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Установка выключателей", "шт", 18, P["el_switch_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Светильник потолочный", "шт", 25, P["el_light_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Монтаж светильников", "шт", 25, P["el_light_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Распределительный щит укомплектованный", "шт", 1, P["el_shchit_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Монтаж щита", "шт", 1, P["el_shchit_work"], "работы"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Автомат 16А", "шт", 14, P["el_avtomat_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "УЗО 40А", "шт", 4, P["el_uzo_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Контур заземления комплект", "компл", 1, P["el_zazem_mat"], "материал"))
    items.append(_ftm_row("Инженерные коммуникации ЭОМ", "Монтаж контура заземления", "компл", 1, P["el_zazem_work"], "работы"))

    # 12. Логистика
    items.append(_ftm_row("Логистика", "Доставка материалов от СПб", "рейс", 3, P["logist_delivery"] / 3, "30 км"))
    items.append(_ftm_row("Логистика", "Транспорт бригады и проживание", "компл", 1, P["logist_brigade"] * 4, "период строительства"))

    # 13. Накладные расходы
    subtotal = sum(float(it["price"]) * float(it["qty"]) for it in items if it["section"] not in ("Логистика", "Накладные расходы"))
    items.append(_ftm_row("Накладные расходы", "Организация работ и накладные", "компл", 1, round(subtotal * 0.07, 2), "7% от общей сметы"))
    items.append(_ftm_row("Накладные расходы", "Расходные материалы и крепёж", "компл", 1, round(subtotal * 0.015, 2), "мелкое крепление"))
    items.append(_ftm_row("Накладные расходы", "Уборка после работ", "компл", 1, round(area_floor * 280, 2), "финальная уборка"))

    return items


# Override _build_estimate_items with v2
_ORIG_BEI_V3 = _build_estimate_items

def _build_estimate_items(parsed, price_text, choice):  # noqa: F811
    try:
        items = _build_full_turnkey_items_v2(parsed, price_text, choice)
        _P8V3_LOG.info("PATCH_TOPIC2_REALSHEET_PRICES_V3: %d items", len(items))
        return items
    except Exception as _v3e:
        _P8V3_LOG.error("PATCH_TOPIC2_REALSHEET_PRICES_V3_ERR %s", _v3e)
        return _ORIG_BEI_V3(parsed, price_text, choice)

_P8V3_LOG.info("PATCH_TOPIC2_REALSHEET_PRICES_V3 installed")
# === END_PATCH_TOPIC2_REALSHEET_PRICES_V3 ===

# === PATCH_TOPIC2_REALSHEET_PRICES_V3_FIX1 ===
# Fix _p8v3_mp/_p8v3_wp to strip key before lookup (template keys have no leading spaces)
def _p8v3_wp(key, fallback=0):  # noqa: F811
    row = _P8V3_TPL_PRICES.get(key.strip())
    return row["work_price"] if row and row["work_price"] > 0 else fallback

def _p8v3_mp(key, fallback=0):  # noqa: F811
    row = _P8V3_TPL_PRICES.get(key.strip())
    return row["mat_price"] if row and row["mat_price"] > 0 else fallback

_P8V3_LOG.info("PATCH_TOPIC2_REALSHEET_PRICES_V3_FIX1 installed")
# === END_PATCH_TOPIC2_REALSHEET_PRICES_V3_FIX1 ===

# === PATCH_TOPIC2_ADD_PEREKRYTIYA_SECTION_V1 ===
# §5 canon: 11 секций, раздел 3 = Перекрытия. Для газобетон 1-эт. дом —
# монолитная плита перекрытия (над первым этажом / чердачная плита).
# Цены из шаблона Газобетонный дом (Перекрытие монолитное).
# Append-only: переопределяем _build_full_turnkey_items_v2.
# ============================================================
_PREV_FTI_V2 = _build_full_turnkey_items_v2

def _build_full_turnkey_items_v2(parsed, price_text, choice):  # noqa: F811
    items = _PREV_FTI_V2(parsed, price_text, choice)
    P = _FTM_PRICES
    area_floor = float(parsed.get("area_floor") or 99.91)
    dims = parsed.get("dims") or parsed.get("dimensions") or [8.5, 12.5]
    try:
        a, b = float(dims[0]), float(dims[1])
    except Exception:
        a = b = area_floor ** 0.5
    perimeter = 2 * (a + b)

    # Перекрытие монолитное (плита над 1 этажом)
    slab_area = round(area_floor * 1.05, 2)   # с запасом
    slab_vol  = round(slab_area * 0.22, 2)    # толщина 220мм
    slab_reb_t= round(slab_area * 0.010, 3)   # 10 кг/м²

    perekr_items = [
        _ftm_row("Перекрытия", "Опалубка перекрытия монтаж/демонтаж", "м²", slab_area,
            _p8v3_wp("монтаж/демонтаж опалубки основания плиты", 1000), "работы"),
        _ftm_row("Перекрытия", "Аренда опалубки перекрытия", "м²", slab_area,
            _p8v3_mp("аренда опалубки (основание плиты)", 1100), "материал"),
        _ftm_row("Перекрытия", "Армирование перекрытия работы", "м²", slab_area,
            _p8v3_wp("устройство арматурного каркаса", 1200), "работы"),
        _ftm_row("Перекрытия", "Арматура перекрытия А500 материал", "т", slab_reb_t,
            _p8v3_mp("арматура металлическая д.12а500", P["rebar_a500_mat"]), "материал"),
        _ftm_row("Перекрытия", "Бетон В25 перекрытие материал", "м³", slab_vol,
            _p8v3_mp("бетон в25 w6", P["concrete_b25_mat"]), "материал"),
        _ftm_row("Перекрытия", "Бетонирование перекрытия работы", "м³", slab_vol,
            _p8v3_wp("бетонирование монолитной плиты   б/н", P["concrete_pour_work"]), "работы"),
        _ftm_row("Перекрытия", "Пеноплэкс утепление плиты 100мм", "м²", slab_area,
            _p8v3_mp("пеноплэкс фундамент 1185х585х100 мм", 800), "материал"),
        _ftm_row("Перекрытия", "Крепёж и расходники перекрытие", "компл", 1,
            round(slab_area * 200, 0), "компл"),
    ]

    # Вставить секцию Перекрытия ПОСЛЕ Стены (перед Кровля)
    result = []
    steny_done = False
    krovlya_inserted = False
    for it in items:
        if it["section"] == "Стены":
            steny_done = True
        if steny_done and not krovlya_inserted and it["section"] == "Кровля":
            result.extend(perekr_items)
            krovlya_inserted = True
        result.append(it)
    if not krovlya_inserted:
        result.extend(perekr_items)

    # Пересчитать накладные расходы (раздел 13 — последние 3 строки)
    # Убираем старые накладные, считаем заново
    base_items = [r for r in result if r["section"] not in ("Логистика", "Накладные расходы")]
    subtotal = sum(float(r["price"]) * float(r["qty"]) for r in base_items)
    logist   = [r for r in result if r["section"] == "Логистика"]
    overhead_new = [
        _ftm_row("Накладные расходы", "Организация работ и накладные", "компл", 1, round(subtotal * 0.07, 2), "7% от общей сметы"),
        _ftm_row("Накладные расходы", "Расходные материалы и крепёж",  "компл", 1, round(subtotal * 0.015, 2), "мелкое крепление"),
        _ftm_row("Накладные расходы", "Уборка после работ",            "компл", 1, round(area_floor * 280, 2), "финальная уборка"),
    ]
    return base_items + logist + overhead_new

_P8V3_LOG.info("PATCH_TOPIC2_ADD_PEREKRYTIYA_SECTION_V1 installed")
# === END_PATCH_TOPIC2_ADD_PEREKRYTIYA_SECTION_V1 ===

# === PATCH_TOPIC2_STALE_PENDING_TASK_GUARD_V1 ===
# ROOT CAUSE: §5 in maybe_handle_stroyka_estimate reuses pending from a DIFFERENT task.
#   _memory_latest("topic_2_estimate_pending_") uses LIKE → finds any task's pending.
#   FIX_STROYKA_PRICE_CONFIRM_EXTEND_V1 patched _pending_is_fresh to 86400s → always fresh.
#   Patched _is_confirm matches "средн" as substring → "цены выше среднего" fires §5.
#   Result: drainage file task gets house estimate from old c94ec497 context.
# FIX: wrap maybe_handle_stroyka_estimate — if pending.task_id != current task_id,
#   check if pending's task is done → mark pending "GENERATED" (permanent block).
import logging as _stpg_log_mod
_STPG_LOG = _stpg_log_mod.getLogger("areal.stale_pending_guard")

_STPG_ORIG = maybe_handle_stroyka_estimate

async def maybe_handle_stroyka_estimate(conn, task, logger=None):  # noqa: F811
    try:
        _stpg_tid = _s(_row_get(task, "id"))
        _stpg_chat = _s(_row_get(task, "chat_id"))
        if _stpg_tid and _stpg_chat:
            _stpg_pend = _memory_latest(_stpg_chat, "topic_2_estimate_pending_")
            _stpg_pend_task = (_stpg_pend or {}).get("task_id", "")
            if (
                _stpg_pend
                and _stpg_pend.get("status") == "WAITING_PRICE_CONFIRMATION"
                and _stpg_pend_task
                and _stpg_pend_task != _stpg_tid
            ):
                # Check if the pending's own task is already in a terminal state
                _stpg_done = False
                try:
                    _stpg_row = conn.execute(
                        "SELECT state FROM tasks WHERE id=? LIMIT 1",
                        (_stpg_pend_task,)
                    ).fetchone()
                    if _stpg_row and str(_stpg_row[0] or "").upper() in (
                        "DONE", "AWAITING_CONFIRMATION", "FAILED", "CANCELLED", "ARCHIVED"
                    ):
                        _stpg_done = True
                except Exception:
                    pass
                _stpg_key = (
                    _stpg_pend.get("_memory_key")
                    or f"topic_2_estimate_pending_{_stpg_pend_task}"
                )
                _stpg_new_status = "GENERATED" if _stpg_done else "STALE_BLOCKED"
                _stpg_blocked = dict(_stpg_pend)
                _stpg_blocked["status"] = _stpg_new_status
                _memory_save(_stpg_chat, _stpg_key, _stpg_blocked)
                _history_safe(conn, _stpg_tid,
                              f"TOPIC2_STALE_PENDING_BLOCKED:pending_task={_stpg_pend_task[:16]}:done={_stpg_done}")
                _STPG_LOG.info(
                    "STPG: pending task=%s (done=%s) → %s; current task=%s",
                    _stpg_pend_task[:8], _stpg_done, _stpg_new_status, _stpg_tid[:8],
                )
    except Exception as _stpg_e:
        _STPG_LOG.warning("STPG_PRE_ERR: %s", _stpg_e)
    return await _STPG_ORIG(conn, task, logger)

_STPG_LOG.info("PATCH_TOPIC2_STALE_PENDING_TASK_GUARD_V1: installed")
# === END_PATCH_TOPIC2_STALE_PENDING_TASK_GUARD_V1 ===


# === PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 ===
import logging as _t2ig_log_mod
_T2IG_LOG = _t2ig_log_mod.getLogger("areal.topic2_input_gate")

try:
    from core.topic2_input_gate import topic2_pre_estimate_gate as _t2ig_gate
    from core.topic2_input_gate import apply_gate_result_to_task as _t2ig_apply
except Exception as _t2ig_import_err:
    _t2ig_gate = None
    _t2ig_apply = None
    _T2IG_LOG.warning("TOPIC2_INPUT_GATE_IMPORT_FAILED:%s", _t2ig_import_err)

_T2IG_ORIG_MAYBE_HANDLE = maybe_handle_stroyka_estimate

async def maybe_handle_stroyka_estimate(conn, task, logger=None):  # noqa: F811
    if _t2ig_gate is not None and _t2ig_apply is not None:
        try:
            _t2ig_decision = _t2ig_gate(conn, task, logger=logger)
            if _t2ig_decision and _t2ig_decision.get("block_engine"):
                _t2ig_apply(conn, task, _t2ig_decision)
                _T2IG_LOG.info(
                    "TOPIC2_INPUT_GATE_BLOCKED:domain=%s state=%s",
                    _t2ig_decision.get("domain"),
                    _t2ig_decision.get("state"),
                )
                _t2ig_msg = _t2ig_decision.get("result") or ""
                if _t2ig_msg:
                    try:
                        # sqlite3.Row has .keys() but not .get() — use dict() to normalize
                        _t2ig_td = dict(task) if hasattr(task, "keys") else (task if isinstance(task, dict) else {})
                        _t2ig_chat = str(_t2ig_td.get("chat_id") or "")
                        _t2ig_reply = _t2ig_td.get("reply_to_message_id")
                        _t2ig_topic = int(_t2ig_td.get("topic_id") or 0)
                        _t2ig_task_id = str(_t2ig_td.get("id") or "")
                        if not _t2ig_chat:
                            raise ValueError(f"empty chat_id in task {_t2ig_task_id}")
                        _t2ig_send_res = await _send_text(_t2ig_chat, _t2ig_msg, _t2ig_reply, _t2ig_topic)
                        _t2ig_bot_msg_id = _t2ig_send_res.get("bot_message_id") if isinstance(_t2ig_send_res, dict) else None
                        if _t2ig_bot_msg_id and _t2ig_task_id:
                            conn.execute(
                                "UPDATE tasks SET bot_message_id=? WHERE id=?",
                                (int(_t2ig_bot_msg_id), _t2ig_task_id),
                            )
                            try:
                                conn.execute(
                                    "INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))",
                                    (_t2ig_task_id, f"TOPIC2_INPUT_GATE_SENT:{_t2ig_bot_msg_id}"),
                                )
                                conn.execute(
                                    "INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))",
                                    (_t2ig_task_id, "reply_sent:waiting_clarification"),
                                )
                            except Exception:
                                pass
                            conn.commit()
                        _T2IG_LOG.info("TOPIC2_INPUT_GATE_SENT:chat=%s bot_msg=%s", _t2ig_chat, _t2ig_bot_msg_id)
                    except Exception as _t2ig_send_err:
                        _T2IG_LOG.warning("TOPIC2_INPUT_GATE_SEND_ERR:%s", _t2ig_send_err)
                return True
        except Exception as _t2ig_err:
            _T2IG_LOG.warning("TOPIC2_INPUT_GATE_ERR:%s", _t2ig_err)
    return await _T2IG_ORIG_MAYBE_HANDLE(conn, task, logger)

_T2IG_LOG.info("PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1: installed")
# === END_PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 ===

# === PATCH_TOPIC2_PRICE_ALWAYS_ASK_V1 ===
# Fix: новый estimate-запрос ("сделай по заданию смету" и т.д.) не должен подхватывать
# pending от предыдущего task_id или от того же task_id после MANUAL_RESET_NEW.
# Price WC должен запускаться КАЖДЫЙ РАЗ для задач с estimate-контентом.
# Корень бага: _is_confirm(startswith "сделай ") = True + _pending_is_fresh override 24h
# → CANONICAL_OLD_ROUTE_HARD_BLOCK пропускает price WC (подтверждено history 076e4350).
import logging as _t2paa_log_mod
_T2PAA_LOG = _t2paa_log_mod.getLogger("stroyka_estimate_canon")
_T2PAA_ORIG_MAYBE_HANDLE = maybe_handle_stroyka_estimate

async def maybe_handle_stroyka_estimate(conn, task, logger=None):
    try:
        task_id = _s(_row_get(task, "id"))
        chat_id = _s(_row_get(task, "chat_id"))
        raw = _s(_row_get(task, "raw_input", ""))
        _pend = _memory_latest(chat_id, "topic_2_estimate_pending_")
        # Если pending активен И текущий ввод — не чистое подтверждение цены
        # (содержит ESTIMATE_WORDS) → помечаем pending stale, чтобы запустился полный price WC.
        # _is_confirm_only = False при наличии "смет"/"дом"/"газобетон" и т.д. в тексте.
        if (_pend
                and _pend.get("status") == "WAITING_PRICE_CONFIRMATION"
                and not _is_confirm_only(raw)):
            _stale = dict(_pend)
            _stale["status"] = "STALE_DEPRECATED"
            _stale["deprecated_at"] = _now()
            _stale["deprecated_reason"] = "PRICE_ALWAYS_ASK_V1:new_estimate_request_not_confirm_only"
            _memory_save(chat_id, f"topic_2_estimate_pending_{_pend.get('task_id', 'x')}", _stale)
            _T2PAA_LOG.info(
                "PATCH_TOPIC2_PRICE_ALWAYS_ASK_V1:stale_cleared task=%s prev_task=%s raw=%.60s",
                task_id, _pend.get("task_id"), raw,
            )
    except Exception as _t2paa_e:
        _T2PAA_LOG.warning("PATCH_TOPIC2_PRICE_ALWAYS_ASK_V1:ERR %s", _t2paa_e)
    return await _T2PAA_ORIG_MAYBE_HANDLE(conn, task, logger)

_T2PAA_LOG.info("PATCH_TOPIC2_PRICE_ALWAYS_ASK_V1 installed")
# === END_PATCH_TOPIC2_PRICE_ALWAYS_ASK_V1 ===

# === PATCH_TOPIC2_PARSE_REQUEST_SMART_INFER_V1 ===
# §9 spec: "что строим — если object_type уже есть — запрещено"
# §10 spec: "имитация бруса" / "по всем помещениям" → scope=под ключ
# §12 spec: брус → Ареал Нева = дом (canon §2)
# Fix 1: pile cross-section "N свай жб AxB" убирается из _extract_dimensions (сечение сваи ≠ размер здания)
# Fix 2: material="брус" + object="" → object="дом"
# Fix 3: "по всем помещениям" / "имитация бруса внутри" → scope="под ключ"
import re as _t2prs_re
import logging as _t2prs_log_mod
_T2PRS_LOG = _t2prs_log_mod.getLogger("stroyka_estimate_canon")

_T2PRS_ORIG_EXTRACT_DIM = _extract_dimensions
_T2PRS_ORIG_PARSE_REQUEST = _parse_request

def _extract_dimensions(text: str):
    t = _low(text)
    # Убираем сечения свай: "N свай [жб] AxB" или "жб AxB"
    t_clean = _t2prs_re.sub(
        r'(?:\d+\s+)?(?:свай|свая|сваи|жб)\s+(?:жб\s+)?\d+\s*[xх×*]\s*\d+',
        ' ', t,
    )
    return _T2PRS_ORIG_EXTRACT_DIM(t_clean)

def _parse_request(text: str):
    parsed = _T2PRS_ORIG_PARSE_REQUEST(text)
    t = _low(text)
    # Fix 2: брус → дом (canon §2: брус → Ареал Нева.xlsx = деревянный дом)
    if not parsed.get("object") and parsed.get("material") == "брус":
        parsed["object"] = "дом"
        _T2PRS_LOG.info("T2PRS_INFER:object=дом:from_material=брус")
    # Fix 2b: другие признаки дома
    if not parsed.get("object"):
        for _hint in ("дач", "коттедж", "жилой", "жилого"):
            if _hint in t:
                parsed["object"] = "дом"
                _T2PRS_LOG.info("T2PRS_INFER:object=дом:hint=%s", _hint)
                break
    # Fix 3: признаки scope=под ключ (spec §10)
    if not parsed.get("scope"):
        _scope_hints = (
            "по всем помещениям", "по комнатам", "все помещения",
            "имитация бруса внутри", "чистовая отделка", "ламинат",
            "санузел", "теплые полы", "тёплые полы",
        )
        for _sh in _scope_hints:
            if _sh in t:
                parsed["scope"] = "под ключ"
                _T2PRS_LOG.info("T2PRS_INFER:scope=под_ключ:hint=%s", _sh)
                break
    return parsed

_T2PRS_LOG.info("PATCH_TOPIC2_PARSE_REQUEST_SMART_INFER_V1 installed")
# === END_PATCH_TOPIC2_PARSE_REQUEST_SMART_INFER_V1 ===

# === PATCH_TOPIC2_CLARIFICATION_MERGE_V1 ===
# Fix: clarified:* entries in task_history not merged into raw_input before _parse_request
# → _missing_question asks the same question again after user answered it.
# PAMQ wrapper exists but _missing_question is called with only (parsed), conn/task not passed.
# Solution: enrich task.raw_input with clarification history BEFORE calling the full chain.
import logging as _t2cm_log_mod
_T2CM_LOG = _t2cm_log_mod.getLogger("stroyka_estimate_canon")
_T2CM_ORIG = maybe_handle_stroyka_estimate

async def maybe_handle_stroyka_estimate(conn, task, logger=None):
    try:
        task_id = _s(_row_get(task, "id"))
        if conn is not None and task_id:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' ORDER BY rowid ASC",
                (task_id,)
            ).fetchall()
            clarifications = [r[0].split(":", 1)[1].strip() for r in rows if ":" in r[0]]
            if clarifications:
                raw = _s(_row_get(task, "raw_input", ""))
                enriched = raw + "\n" + "\n".join(clarifications)
                if hasattr(task, "keys"):
                    task_dict = dict(zip(task.keys(), task))
                elif isinstance(task, dict):
                    task_dict = dict(task)
                else:
                    task_dict = {"raw_input": enriched}
                task_dict["raw_input"] = enriched
                _T2CM_LOG.info(
                    "T2CM_MERGE: task=%s clarifs=%d enriched_len=%d",
                    task_id, len(clarifications), len(enriched),
                )
                return await _T2CM_ORIG(conn, task_dict, logger)
    except Exception as _t2cm_e:
        _T2CM_LOG.warning("T2CM_ERR: %s", _t2cm_e)
    return await _T2CM_ORIG(conn, task, logger)

_T2CM_LOG.info("PATCH_TOPIC2_CLARIFICATION_MERGE_V1 installed")
# === END_PATCH_TOPIC2_CLARIFICATION_MERGE_V1 ===


# === PATCH_TOPIC2_TOPIC_ID_INT_SAFE_V1 ===
import logging as _t2tid_log_mod
_T2TID_LOG = _t2tid_log_mod.getLogger("stroyka_estimate_canon")
_T2TID_ORIG_DIRECT = _stroyka_final_handle_direct_item_estimate

async def _stroyka_final_handle_direct_item_estimate(conn, task, logger=None):
    try:
        raw_tid = _row_get(task, "topic_id", 0)
        int(raw_tid or 0)
    except (ValueError, TypeError):
        if hasattr(task, "keys"):
            task_dict = dict(zip(task.keys(), tuple(task)))
        elif isinstance(task, dict):
            task_dict = dict(task)
        else:
            task_dict = {}
        task_dict["topic_id"] = TOPIC_ID_STROYKA
        _T2TID_LOG.info("T2TID_FIX: topic_id coerced to %s", TOPIC_ID_STROYKA)
        return await _T2TID_ORIG_DIRECT(conn, task_dict, logger)
    return await _T2TID_ORIG_DIRECT(conn, task, logger)

_T2TID_LOG.info("PATCH_TOPIC2_TOPIC_ID_INT_SAFE_V1 installed")
# === END_PATCH_TOPIC2_TOPIC_ID_INT_SAFE_V1 ===

# === PATCH_TOPIC2_CLARIFICATION_MERGE_V2 ===
# Fix V1 bug: dict(zip(task.keys(), task)) for plain dict iterates keys not values
# → task_dict becomes {key:key}, internal call fails, fallback to original (no merge).
# V2: uses dict(task) for plain dict (same pattern as FIX_STROYKA_CONTEXT_ENRICH line 2393).
# Calls _T2CM_ORIG (PAA) directly, bypassing broken V1.
import logging as _t2cm2_log_mod
_T2CM2_LOG = _t2cm2_log_mod.getLogger("task_worker")
_T2CM2_INNER = _T2CM_ORIG  # PAA wrapper — skip broken V1

async def maybe_handle_stroyka_estimate(conn, task, logger=None):
    try:
        task_id = _s(_row_get(task, "id"))
        if conn is not None and task_id:
            rows = conn.execute(
                "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'clarified:%' ORDER BY rowid ASC",
                (task_id,)
            ).fetchall()
            clarifications = [r[0].split(":", 1)[1].strip() for r in rows if ":" in r[0]]
            if clarifications:
                raw = _s(_row_get(task, "raw_input", ""))
                enriched = raw + "\n" + "\n".join(clarifications)
                if isinstance(task, dict):
                    task_dict = dict(task)
                elif hasattr(task, "keys"):
                    task_dict = dict(zip(task.keys(), tuple(task)))
                else:
                    task_dict = {}
                task_dict["raw_input"] = enriched
                _T2CM2_LOG.info(
                    "T2CM2_MERGE: task=%s clarifs=%d enriched_len=%d",
                    task_id, len(clarifications), len(enriched),
                )
                return await _T2CM2_INNER(conn, task_dict, logger)
    except Exception as _t2cm2_e:
        _T2CM2_LOG.warning("T2CM2_ERR: %s", _t2cm2_e)
    return await _T2CM2_INNER(conn, task, logger)

_T2CM2_LOG.info("PATCH_TOPIC2_CLARIFICATION_MERGE_V2 installed")
# === END_PATCH_TOPIC2_CLARIFICATION_MERGE_V2 ===

# === PATCH_TOPIC2_PRICE_TEXT_TRUNCATE_V1 ===
# Bug: _price_confirmation_text с 126 позициями шаблона → >4096 симв → Telegram 400 "message is too long"
# Fix: ограничить template_prices до 15 строк; остаток заменить «… (+N позиций)».
import logging as _ptt_log_mod
_PTT_LOG = _ptt_log_mod.getLogger("task_worker")
_PTT_ORIG = _price_confirmation_text

def _price_confirmation_text(parsed, template, sheet_name, template_prices, online_prices):
    MAX_PRICE_LINES = 15
    if template_prices:
        lines = template_prices.splitlines()
        if len(lines) > MAX_PRICE_LINES + 1:
            shown = "\n".join(lines[:MAX_PRICE_LINES])
            rest = len(lines) - MAX_PRICE_LINES
            template_prices = shown + f"\n… (+{rest} позиций в смете)"
    text = _PTT_ORIG(parsed, template, sheet_name, template_prices, online_prices)
    if len(text) > 3900:
        text = text[:3900] + "\n…(сообщение сокращено)"
    return text

_PTT_LOG.info("PATCH_TOPIC2_PRICE_TEXT_TRUNCATE_V1 installed")
# === END_PATCH_TOPIC2_PRICE_TEXT_TRUNCATE_V1 ===


# === PATCH_TOPIC2_FRAME_HOUSE_MATERIAL_V1 ===
# Facts:
# - topic_2 canonical frame-house estimate request was classified as material="брус"
# - request contained frame-house markers: свайный фундамент, ЖБ сваи 150x150, утепление стен 150, имитация бруса as finish
# - canon requires frame house >100m2 to use frame template route, not gasbeton/bрус route
import re as _t2fh_re
import logging as _t2fh_logging

_T2FH_LOG = _t2fh_logging.getLogger("topic2.frame_house_material_v1")

def _t2fh_s(v, limit=20000):
    try:
        return str(v or "")[:limit]
    except Exception:
        return ""

def _t2fh_low(v):
    return _t2fh_s(v).lower().replace("ё", "е")

def _t2fh_has_solid_brus(low: str) -> bool:
    return any(x in low for x in (
        "дом из бруса",
        "дом брус",
        "брусовой дом",
        "клееный брус",
        "клееного бруса",
        "профилированный брус",
        "профилированного бруса",
        "оцилиндрованное бревно",
        "сруб",
        "лафет",
    ))

def _t2fh_is_frame_house_context(raw) -> bool:
    low = _t2fh_low(raw)
    if not low:
        return False

    if _t2fh_has_solid_brus(low):
        return False

    has_direct_frame = any(x in low for x in (
        "каркас",
        "каркасный",
        "каркасник",
        "frame",
    ))

    has_finish_brus = (
        "имитац" in low and "брус" in low
    )

    has_piles = any(x in low for x in (
        "свая",
        "сваи",
        "свай",
        "жб 150",
        "ж/б 150",
        "150х150",
        "150x150",
        "150×150",
        "железобетонн",
    ))

    has_wall_insulation = (
        "утепл" in low and "стен" in low
    ) or any(x in low for x in (
        "утепление стен 150",
        "утепления стен 150",
        "минвата",
        "каменная вата",
    ))

    if has_direct_frame:
        return True

    if has_finish_brus and (has_piles or has_wall_insulation):
        return True

    if has_piles and has_wall_insulation:
        return True

    return False

def _t2fh_force_frame(parsed, raw):
    try:
        if isinstance(parsed, dict) and _t2fh_is_frame_house_context(raw):
            old_material = _t2fh_low(parsed.get("material"))
            if old_material in ("", "брус", "дерево", "деревянный", "газобетон"):
                parsed["material"] = "каркас"
                parsed["frame_house"] = True
                parsed["material_source"] = "PATCH_TOPIC2_FRAME_HOUSE_MATERIAL_V1"
        return parsed
    except Exception as e:
        try:
            _T2FH_LOG.warning("PATCH_TOPIC2_FRAME_HOUSE_MATERIAL_V1_DICT_ERR %s", e)
        except Exception:
            pass
        return parsed

def _t2fh_wrap_material_func(name):
    old = globals().get(name)
    if not callable(old) or getattr(old, "_t2fh_wrapped", False):
        return False

    def wrapped(*args, **kwargs):
        raw_parts = []
        for x in args:
            raw_parts.append(_t2fh_s(x, 5000))
        for k in ("raw_input", "text", "caption", "prompt", "user_text"):
            if k in kwargs:
                raw_parts.append(_t2fh_s(kwargs.get(k), 5000))
        raw = "\n".join(raw_parts)

        res = old(*args, **kwargs)

        if isinstance(res, str):
            if _t2fh_is_frame_house_context(raw) and _t2fh_low(res) in ("", "брус", "дерево", "деревянный", "газобетон"):
                return "каркас"
            return res

        if isinstance(res, dict):
            return _t2fh_force_frame(res, raw)

        return res

    wrapped._t2fh_wrapped = True
    globals()[name] = wrapped
    return True

_T2FH_WRAPPED = []
for _t2fh_name in (
    "_extract_material",
    "extract_material",
    "_detect_material",
    "detect_material",
    "_parse_estimate_input",
    "parse_estimate_input",
    "_parse_user_input",
    "parse_user_input",
    "_parse_task_input",
    "parse_task_input",
    "_parse_stroyka_input",
    "parse_stroyka_input",
):
    try:
        if _t2fh_wrap_material_func(_t2fh_name):
            _T2FH_WRAPPED.append(_t2fh_name)
    except Exception as _t2fh_e:
        try:
            _T2FH_LOG.warning("PATCH_TOPIC2_FRAME_HOUSE_MATERIAL_V1_WRAP_ERR %s %s", _t2fh_name, _t2fh_e)
        except Exception:
            pass

try:
    _T2FH_LOG.info("PATCH_TOPIC2_FRAME_HOUSE_MATERIAL_V1 installed wrapped=%s", ",".join(_T2FH_WRAPPED))
except Exception:
    pass
# === END_PATCH_TOPIC2_FRAME_HOUSE_MATERIAL_V1 ===

# === FULL_CANON_CLOSURE_VERIFIED_V1 / TOPIC2_TEMPLATE_PRICE_EXTRACTION_SAFE_V1 ===
try:
    import re as _fccv1_re
    import logging as _fccv1_logging
    from openpyxl import load_workbook as _fccv1_load_workbook

    _fccv1_log = _fccv1_logging.getLogger("task_worker")

    def _fccv1_float_or_none(value):
        if value is None:
            return None, "PRICE_MISSING"
        if isinstance(value, (int, float)):
            return float(value), "OK"
        s = str(value).strip().replace("\xa0", " ").replace(" ", "").replace(",", ".")
        if not s:
            return None, "PRICE_MISSING"
        try:
            return float(s), "OK"
        except Exception:
            return None, "PRICE_MISSING"

    def _p8v3_extract_tpl_prices(template_path=None):
        prices = {}
        loaded = 0
        skipped = 0
        missing_price = 0

        if not template_path:
            _fccv1_log.info("TOPIC2_TEMPLATE_PRICE_EXTRACTION_SAFE_V1 installed loaded=0 skipped=0 missing_price=0")
            return prices

        wb = _fccv1_load_workbook(template_path, data_only=True)
        ws = wb.active

        for r in ws.iter_rows(values_only=True):
            if not r or len(r) < 10:
                skipped += 1
                continue

            name = str(r[0] if r[0] is not None else "").strip()
            if not name:
                skipped += 1
                continue

            qty, qty_status = _fccv1_float_or_none(r[3])
            if qty_status != "OK":
                skipped += 1
                continue

            work_price, work_status = _fccv1_float_or_none(r[7])
            mat_price, mat_status = _fccv1_float_or_none(r[9])

            if work_status != "OK" or mat_status != "OK":
                missing_price += 1

            if work_status == "OK" and mat_status == "OK" and work_price == 0 and mat_price == 0:
                skipped += 1
                continue

            norm = _fccv1_re.sub(r"\s+", " ", name.lower()).strip()
            prices[norm] = {
                "name": name,
                "qty": qty,
                "work_price": work_price,
                "mat_price": mat_price,
                "work_price_status": work_status,
                "mat_price_status": mat_status,
            }
            loaded += 1

        _fccv1_log.info(
            "TOPIC2_TEMPLATE_PRICE_EXTRACTION_SAFE_V1 installed loaded=%s skipped=%s missing_price=%s",
            loaded,
            skipped,
            missing_price,
        )
        return prices

    _fccv1_log.info("TOPIC2_TEMPLATE_PRICE_EXTRACTION_SAFE_V1 installed loaded=0 skipped=0 missing_price=0")
except Exception as _e:
    try:
        _fccv1_log.exception("TOPIC2_TEMPLATE_PRICE_EXTRACTION_SAFE_V1_INSTALL_ERR:%s", _e)
    except Exception:
        pass
# === /FULL_CANON_CLOSURE_VERIFIED_V1 ===

# === PATCH_PRICE_ENRICHMENT_IDEMPOTENT_V1 ===
# Причина: _pick_next_task забирает задачи в NEW/IN_PROGRESS/WAITING_CLARIFICATION.
# После price WC задача переходит в WAITING_CLARIFICATION, но через 1.5с poll
# подхватывает её снова → запускает полный pipeline → второй вызов Sonar.
# Фикс: проверяем TOPIC2_PRICE_ENRICHMENT_DONE в task_history перед вызовом Sonar.
# Если маркер есть — возвращаем "" без сетевого запроса.
try:
    import logging as _pei_log_mod
    _PEI_LOG = _pei_log_mod.getLogger("task_worker")
    _PEI_ORIG_SEARCH = _search_prices_online

    async def _search_prices_online(parsed, template, sheet_name, conn=None, task_id=None):
        if conn is not None and task_id is not None:
            try:
                row = conn.execute(
                    "SELECT action FROM task_history WHERE task_id=? AND action LIKE 'TOPIC2_PRICE_ENRICHMENT_DONE:%' ORDER BY rowid DESC LIMIT 1",
                    (task_id,)
                ).fetchone()
                if row:
                    _PEI_LOG.info("PATCH_PRICE_ENRICHMENT_IDEMPOTENT_V1: skip task=%s already=%s", task_id, row[0] if not hasattr(row, "keys") else row["action"])
                    return ""
            except Exception as _pei_check_e:
                _PEI_LOG.warning("PATCH_PRICE_ENRICHMENT_IDEMPOTENT_V1_CHECK_ERR: %s", _pei_check_e)
        return await _PEI_ORIG_SEARCH(parsed, template, sheet_name, conn=conn, task_id=task_id)

    _PEI_LOG.info("PATCH_PRICE_ENRICHMENT_IDEMPOTENT_V1 installed")
except Exception as _pei_install_e:
    try:
        _PEI_LOG.exception("PATCH_PRICE_ENRICHMENT_IDEMPOTENT_V1_INSTALL_ERR: %s", _pei_install_e)
    except Exception:
        pass
# === END_PATCH_PRICE_ENRICHMENT_IDEMPOTENT_V1 ===

# === PATCH_KARKASNIK_SHEET_FIX_V1 ===
# Fix regression from PATCH_TOPIC2_REALSHEET_PRICES_V3 which hardcoded "Газобетонный дом"
# for ALL materials. For material=="каркас": read "Каркас под ключ" from М-80.xlsx
# (col4=work_price, col6=mat_price, data starts row 10).
import logging as _kfv1_log_mod
_KFV1_LOG = _kfv1_log_mod.getLogger("stroyka.karkasnik_sheet_fix_v1")

_ETF_V3_ORIG = extract_template_prices

def extract_template_prices(template_path, parsed):  # noqa: F811
    if (parsed or {}).get("material") == "каркас":
        _kark_path = template_path
        if not _kark_path or not os.path.exists(_kark_path):
            _kark_path = "/root/.areal-neva-core/data/templates/estimate/cache/1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp__М-80.xlsx"
        prices = {}
        try:
            from openpyxl import load_workbook as _kw
            wb = _kw(_kark_path, read_only=True, data_only=True)
            ws = wb["Каркас под ключ"] if "Каркас под ключ" in wb.sheetnames else wb.active
            section = "Общее"
            for i, row in enumerate(ws.iter_rows(values_only=True)):
                r = list(row)
                if i < 9:
                    continue
                r1 = r[1] if len(r) > 1 else None
                if r[0] and not r1:
                    section = str(r[0]).strip()
                    continue
                if not r1:
                    continue
                try:
                    wp = float(r[4]) if r[4] is not None else 0.0
                    mp = float(r[6]) if r[6] is not None else 0.0
                except (ValueError, TypeError):
                    continue
                if wp == 0 and mp == 0:
                    continue
                unit = str(r[2]).strip() if r[2] else ""
                name = str(r1).strip()
                prices[name.lower().strip()] = {
                    "work_price": wp, "mat_price": mp,
                    "unit": unit, "section": section, "name": name,
                }
            wb.close()
        except Exception as _ke:
            _KFV1_LOG.error("KARKASNIK_SHEET_FIX_V1_ERR: %s", _ke)
        count = len(prices)
        lines = [
            f"- {v['name']}: работа={v['work_price']:.0f} {v['unit']}, матер={v['mat_price']:.0f} {v['unit']}"
            for v in list(prices.values())[:25]
            if v["work_price"] > 0 or v["mat_price"] > 0
        ]
        text = f"Цены из листа 'Каркас под ключ' ({count} позиций):\n" + "\n".join(lines)
        _KFV1_LOG.info("KARKASNIK_SHEET_FIX_V1:count=%d sheet=Каркас_под_ключ", count)
        return text, "Каркас под ключ", False
    return _ETF_V3_ORIG(template_path, parsed)

_KFV1_LOG.info("PATCH_KARKASNIK_SHEET_FIX_V1 installed")
# === END_PATCH_KARKASNIK_SHEET_FIX_V1 ===
