# === FULLFIX_10_TOTAL_CLOSURE_ENGINE ===
import os
import re
import json
import math
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE = "/root/.areal-neva-core"
CORE_DB = f"{BASE}/data/core.db"
MEM_DB = f"{BASE}/data/memory.db"
ENGINE = "FULLFIX_10_TOTAL_CLOSURE_ENGINE"

PROJECT_WORDS = (
    "проект", "сделай плит", "сделать плит", "плита", "фундамент", "фундаментная",
    "кж", "кд", "ар", "кровля", "стропил", "чертеж", "чертёж", "dwg", "dxf", "pdf"
)

ESTIMATE_WORDS = (
    "смет", "посчитай", "расчет", "расчёт", "стоимость", "цена", "руб", "м2", "м²", "м3", "м³"
)

CONFIRM_WORDS = {"да", "ок", "ok", "хорошо", "подтверждаю", "верно", "все верно", "всё верно", "принято"}
REVISION_WORDS = {"нет", "не так", "переделай", "исправь", "правки", "доработай", "уточни", "уточнение"}

FORBIDDEN_FOUNDATION_WORDS = [
    "стропил", "обреш", "контробреш", "пиломатериал", "кровл", "мауэрлат",
    "балки перекрытия", "план кровли", "спецификация древесины", "спецификация крепежа"
]

FOUNDATION_SHEETS = [
    {"mark": "КЖ", "number": "0", "title": "Титульный лист"},
    {"mark": "КЖ", "number": "1", "title": "Общие данные"},
    {"mark": "КЖ", "number": "2", "title": "Ведомость листов"},
    {"mark": "КЖ", "number": "3", "title": "План фундаментной плиты"},
    {"mark": "КЖ", "number": "4", "title": "План нижнего армирования"},
    {"mark": "КЖ", "number": "5", "title": "План верхнего армирования"},
    {"mark": "КЖ", "number": "6", "title": "Разрез 1-1"},
    {"mark": "КЖ", "number": "7", "title": "Разрез 2-2"},
    {"mark": "КЖ", "number": "8", "title": "Узел края плиты"},
    {"mark": "КЖ", "number": "9", "title": "Узел защитного слоя"},
    {"mark": "КЖ", "number": "10", "title": "Спецификация материалов"},
    {"mark": "КЖ", "number": "11", "title": "Ведомость расхода стали"},
    {"mark": "КЖ", "number": "12", "title": "Пояснительная записка"},
    {"mark": "КЖ", "number": "13", "title": "Контроль качества работ"},
]

NORMATIVE_NOTES = [
    "СП 63.13330.2018 Бетонные и железобетонные конструкции",
    "СП 20.13330.2016 Нагрузки и воздействия",
    "ГОСТ 21.101-2020 Основные требования к проектной и рабочей документации",
    "ГОСТ 21.501-2018 Правила выполнения рабочей документации архитектурных и конструктивных решений",
    "ГОСТ 34028-2016 Прокат арматурный для железобетонных конструкций",
    "ГОСТ 7473-2010 Смеси бетонные",
]

REBAR_WEIGHT_KG_M = {6:0.222,8:0.395,10:0.617,12:0.888,14:1.21,16:1.58,18:2.0,20:2.47,22:2.98,25:3.85}

def clean(v: Any, limit: int = 12000) -> str:
    return str(v or "").replace("\x00", " ").strip()[:limit]

def classify_user_task(raw_input: str) -> str:
    low = clean(raw_input, 2000).lower()
    stripped = low.strip()
    if stripped in CONFIRM_WORDS or any(stripped.startswith(x) for x in ("да", "ок", "подтверж")):
        return "confirm"
    if stripped in REVISION_WORDS or any(x in stripped for x in ("не так", "передел", "исправ", "правк", "уточн", "недоволен")):
        return "revision"
    if any(x in low for x in PROJECT_WORDS):
        return "project"
    if any(x in low for x in ESTIMATE_WORDS):
        return "estimate"
    return "chat"

def classify_project_kind(raw_input: str) -> Tuple[str, str]:
    low = clean(raw_input, 4000).lower()
    if any(x in low for x in ("плит", "фундамент", "бетон", "арматур")):
        return "foundation_slab", "КЖ"
    if any(x in low for x in ("кров", "строп", "обреш", "кд")):
        return "roof", "КД"
    if any(x in low for x in ("архитект", "планиров", "ар ")):
        return "architectural", "АР"
    return "foundation_slab", "КЖ"

def parse_float(v: str, default: float) -> float:
    try:
        return float(str(v).replace(",", "."))
    except Exception:
        return default

def parse_foundation_request(raw_input: str) -> Dict[str, Any]:
    text = clean(raw_input, 5000)
    low = text.lower()
    project_kind, section = classify_project_kind(text)

    length_m = 10.0
    width_m = 10.0
    m = re.search(r"(\d+(?:[,.]\d+)?)\s*(?:на|x|х|×)\s*(\d+(?:[,.]\d+)?)\s*(?:м|m)?", low)
    if m:
        length_m = parse_float(m.group(1), 10.0)
        width_m = parse_float(m.group(2), 10.0)

    def mm(patterns: List[str], default: int) -> int:
        for p in patterns:
            mmv = re.search(p, low, re.I)
            if mmv:
                return int(float(mmv.group(1).replace(",", ".")))
        return default

    slab_mm = mm([
        r"толщин[аы]?\D{0,30}(\d{2,4})\s*мм",
        r"плит[аы]?\D{0,30}(\d{2,4})\s*мм",
        r"\b(\d{2,4})\s*мм\b",
    ], 250)

    sand_mm = mm([r"пес[а-яё]*\D{0,30}(\d{2,4})\s*мм"], 300)
    gravel_mm = mm([r"щеб[а-яё]*\D{0,30}(\d{2,4})\s*мм"], 150)
    rebar_step_mm = mm([r"шаг\D{0,30}(\d{2,4})\s*мм"], 200)

    rebar_diam_mm = 12
    md = re.search(r"(?:ø|ф|d|диаметр)\s*(\d{1,2})", low, re.I)
    if md:
        rebar_diam_mm = int(md.group(1))

    concrete_class = "B25"
    mc = re.search(r"\b[вb]\s?(\d{2,3}(?:[,.]\d)?)\b", text, re.I)
    if mc:
        concrete_class = "B" + mc.group(1).replace(",", ".")

    rebar_class = "A500"
    mr = re.search(r"\b[аa]\s?500[сc]?\b", text, re.I)
    if mr:
        rebar_class = "A500C" if "c" in mr.group(0).lower() or "с" in mr.group(0).lower() else "A500"

    if project_kind == "foundation_slab":
        section = "КЖ"

    return {
        "project_name": "Проект фундаментной плиты",
        "project_kind": project_kind,
        "section": section,
        "length_m": length_m,
        "width_m": width_m,
        "slab_mm": slab_mm,
        "sand_mm": sand_mm,
        "gravel_mm": gravel_mm,
        "rebar_diam_mm": rebar_diam_mm,
        "rebar_step_mm": rebar_step_mm,
        "rebar_class": rebar_class,
        "concrete_class": concrete_class,
        "cover_mm": 40,
        "input": raw_input,
    }

def foundation_sheets() -> List[Dict[str, str]]:
    return [dict(x) for x in FOUNDATION_SHEETS]

def calc_foundation(data: Dict[str, Any]) -> Dict[str, Any]:
    L = float(data["length_m"])
    W = float(data["width_m"])
    area = L * W
    slab_m = int(data["slab_mm"]) / 1000.0
    sand_m = int(data["sand_mm"]) / 1000.0
    gravel_m = int(data["gravel_mm"]) / 1000.0
    step_m = int(data["rebar_step_mm"]) / 1000.0
    d = int(data["rebar_diam_mm"])
    bars_x = int(math.floor(W / step_m)) + 1
    bars_y = int(math.floor(L / step_m)) + 1
    rebar_m_total = (bars_x * L + bars_y * W) * 2
    kg_m = REBAR_WEIGHT_KG_M.get(d, (d*d)/162.0)
    rebar_kg = rebar_m_total * kg_m
    return {
        "area_m2": round(area, 3),
        "concrete_m3": round(area * slab_m, 3),
        "sand_m3": round(area * sand_m, 3),
        "gravel_m3": round(area * gravel_m, 3),
        "rebar_m_total": round(rebar_m_total, 1),
        "rebar_kg": round(rebar_kg, 1),
        "rebar_t": round(rebar_kg / 1000.0, 3),
        "bars_x": bars_x,
        "bars_y": bars_y,
    }

def extract_pdf_text(path: str, limit: int = 200000) -> str:
    if not path or not os.path.exists(path):
        return ""
    text = ""
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        for page in reader.pages:
            text += "\n" + (page.extract_text() or "")
            if len(text) > limit:
                break
    except Exception:
        pass
    return clean(text, limit)

def validate_foundation_text(text: str) -> Tuple[bool, str]:
    low = clean(text, 200000).lower()
    bad = [x for x in FORBIDDEN_FOUNDATION_WORDS if x in low]
    if bad:
        return False, "FORBIDDEN_FOUNDATION_WORDS:" + ",".join(bad[:10])
    required = ["фундамент", "плит", "армат", "бетон"]
    missing = [x for x in required if x not in low]
    if missing:
        return False, "MISSING_REQUIRED_WORDS:" + ",".join(missing)
    return True, ""

def save_result_memory(chat_id: str, topic_id: int, raw_input: str, result: str, meta: Dict[str, Any]) -> None:
    try:
        conn = sqlite3.connect(MEM_DB, timeout=10)
        conn.execute("CREATE TABLE IF NOT EXISTS memory (chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        prefix = f"topic_{int(topic_id)}_"
        payload = {
            "engine": ENGINE,
            "raw_input": raw_input,
            "result": result,
            "meta": meta,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        conn.execute(
            "INSERT INTO memory (chat_id,key,value,timestamp) VALUES (?,?,?,datetime('now'))",
            (str(chat_id), prefix + "artifact_result", json.dumps(payload, ensure_ascii=False))
        )
        conn.execute(
            "INSERT INTO memory (chat_id,key,value,timestamp) VALUES (?,?,?,datetime('now'))",
            (str(chat_id), prefix + "task_summary", clean(result, 20000))
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def parse_estimate(raw_input: str) -> List[Dict[str, Any]]:
    text = clean(raw_input, 5000)
    parts = re.split(r"[,;\n]+", text)
    rows = []
    for part in parts:
        p = part.strip()
        if not p:
            continue
        qty_m = re.search(r"(\d+(?:[,.]\d+)?)\s*(м²|м2|м³|м3|шт|п\.?м|кг|т)", p, re.I)
        price_m = re.search(r"(?:по|цена)?\s*(\d+(?:[,.]\d+)?)\s*(?:руб|₽)", p, re.I)
        if qty_m:
            qty = parse_float(qty_m.group(1), 0.0)
            unit = qty_m.group(2).replace("м2","м²").replace("м3","м³")
            price = parse_float(price_m.group(1), 0.0) if price_m else 0.0
            name = re.sub(r"\d+(?:[,.]\d+)?\s*(м²|м2|м³|м3|шт|п\.?м|кг|т)", "", p, flags=re.I)
            name = re.sub(r"(?:по|цена)?\s*\d+(?:[,.]\d+)?\s*(?:руб|₽).*", "", name, flags=re.I).strip(" :-")
            rows.append({
                "name": name or "Позиция сметы",
                "qty": qty,
                "unit": unit,
                "price": price,
                "total": round(qty * price, 2),
            })
    if not rows:
        rows.append({"name": "Позиция сметы", "qty": 1, "unit": "шт", "price": 0, "total": 0})
    return rows

def create_estimate_files(raw_input: str, task_id: str, topic_id: int = 0) -> Dict[str, Any]:
    from openpyxl import Workbook
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

    rows = parse_estimate(raw_input)
    total = round(sum(float(r["total"]) for r in rows), 2)
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id or "estimate"))[:30]
    out_dir = Path(tempfile.gettempdir()) / f"areal_estimate_{safe}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)
    xlsx_path = str(out_dir / f"estimate_{safe}.xlsx")
    pdf_path = str(out_dir / f"estimate_{safe}.pdf")
    manifest_path = str(out_dir / f"estimate_{safe}.manifest.json")

    wb = Workbook()
    ws = wb.active
    ws.title = "Смета"
    ws.append(["№", "Наименование", "Кол-во", "Ед", "Цена", "Сумма"])
    for i, r in enumerate(rows, 1):
        ws.append([i, r["name"], r["qty"], r["unit"], r["price"], r["total"]])
    ws.append(["", "ИТОГО", "", "", "", total])
    wb.save(xlsx_path)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, h-20*mm, "Estimate")
    y = h - 35*mm
    c.setFont("Helvetica", 9)
    for i, r in enumerate(rows, 1):
        c.drawString(20*mm, y, f"{i}. {r['name']} — {r['qty']} {r['unit']} x {r['price']} = {r['total']} руб")
        y -= 8*mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20*mm, y-5*mm, f"TOTAL: {total} руб")
    c.save()

    manifest = {
        "engine": ENGINE,
        "type": "estimate",
        "task_id": task_id,
        "topic_id": topic_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
        "total": total,
        "files": {"xlsx": xlsx_path, "pdf": pdf_path},
    }
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    try:
        from core.engine_base import upload_artifact_to_drive
        xlsx_link = upload_artifact_to_drive(xlsx_path, task_id, topic_id)
        pdf_link = upload_artifact_to_drive(pdf_path, task_id, topic_id)
        manifest_link = upload_artifact_to_drive(manifest_path, task_id, topic_id)
    except Exception as e:
        return {"success": False, "error": "UPLOAD_FAILED:" + str(e)[:300]}

    if not xlsx_link or not pdf_link:
        return {"success": False, "error": "ESTIMATE_LINKS_MISSING"}

    message = (
        "Смета создана\n"
        f"Позиций: {len(rows)}\n"
        f"Итого: {total} руб\n"
        f"PDF: {pdf_link}\n"
        f"XLSX: {xlsx_link}\n"
        f"MANIFEST: {manifest_link or ''}\n\n"
        "Доволен результатом? Ответь: Да / Уточни / Правки"
    )
    return {
        "success": True,
        "engine": ENGINE,
        "type": "estimate",
        "pdf_link": str(pdf_link),
        "xlsx_link": str(xlsx_link),
        "manifest_link": str(manifest_link or ""),
        "message": message,
        "total": total,
        "rows": rows,
    }

# === END FULLFIX_10_TOTAL_CLOSURE_ENGINE ===
