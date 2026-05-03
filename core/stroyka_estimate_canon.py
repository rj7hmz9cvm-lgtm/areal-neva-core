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
    FULL_STROYKA_DISABLE_OLD_ESTIMATE_RECALL_FINAL

    Old DONE/ARCHIVED estimate reuse is forbidden for topic_2.
    Reason: it reused stale VOR/proflist artifacts and spammed old Drive links instead of processing current task.
    New estimate requests must be processed from current raw_input only.
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
            wb = load_workbook(template_path)
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
        from openpyxl import load_workbook
        wb = load_workbook(xlsx_path, data_only=False)
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


def _final_summary(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], choice: Dict[str, Any], py_total: float) -> str:
    exclusions = "\n".join(f"- {x}" for x in EXCLUSIONS_DEFAULT)
    nds = py_total * 0.2
    return f"""✅ Предварительная смета готова

Объект: {parsed.get('object') or 'объект'}
Эталон: {template.get('title')}
Лист эталона: {sheet_name or 'не выбран'}
Выбор цены: {choice.get('choice')}
Поправка: {choice.get('percent_adjustment', 0)}%

Разделы:
- Фундамент
- Стены
- Перекрытия
- Кровля
- Логистика
- Накладные расходы

Итого: {py_total:,.0f} руб
НДС 20%: {nds:,.0f} руб
С НДС: {py_total + nds:,.0f} руб

Входит:
- основные строительные работы по указанному ТЗ
- материалы и работы по подтверждённым позициям
- логистика отдельным блоком

Не входит:
{exclusions}""".replace(",", " ")


def _price_confirmation_text(parsed: Dict[str, Any], template: Dict[str, Any], sheet_name: Optional[str], template_prices: str, online_prices: str) -> str:
    exclusions = "\n".join(f"- {x}" for x in EXCLUSIONS_DEFAULT)
    return f"""⏳ Задачу понял

Эталон сметы: {template.get('title')}
Лист эталона: {sheet_name or 'не выбран'}
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

    summary = _final_summary(parsed, template, sheet_name, choice, py_total)
    pdf_path = _create_pdf(task_id, summary)
    xlsx_link = await _upload_or_fallback(chat_id, topic_id, reply_to, xlsx_path, f"stroyka_estimate_{task_id[:8]}.xlsx", "Excel сметы")
    pdf_link = await _upload_or_fallback(chat_id, topic_id, reply_to, pdf_path, f"stroyka_estimate_{task_id[:8]}.pdf", "PDF сметы")

    if not xlsx_link or not pdf_link:
        await _send_text(chat_id, "Произошла ошибка при загрузке файлов, повторяю", reply_to, topic_id)
        _update_task_safe(conn, task_id, state="FAILED", error_message="STROYKA_UPLOAD_FAILED")
        return True

    result = summary + f"\n\n📊 Excel: {xlsx_link}\n📄 PDF: {pdf_link}\n\nДоволен? Да / Уточни / Правки"
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


async def maybe_handle_stroyka_estimate(conn: sqlite3.Connection, task: Any, logger=None) -> bool:
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
