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

# === FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT ===
# Goal:
# - project PDF must look like compact project album, not sparse text dump
# - one dense A3 landscape sheet frame
# - fewer duplicate sheets
# - plans, sections, nodes, specs placed compactly on each page
# - old FULLFIX_07 renderer must not define the visual quality anymore

def _ff12_font():
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        for name, path in [
            ("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ("Arial", "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"),
        ]:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont(name, path))
                    return name
                except Exception:
                    pass
    except Exception:
        pass
    return "Helvetica"

def _ff12_draw_stamp(c, page_w, page_h, sheet_title, sheet_no, sheet_total, section, font):
    from reportlab.lib.units import mm

    margin = 10 * mm
    c.setLineWidth(0.7)
    c.rect(margin, margin, page_w - 2 * margin, page_h - 2 * margin)

    stamp_w = 185 * mm
    stamp_h = 36 * mm
    sx = page_w - margin - stamp_w
    sy = margin
    c.rect(sx, sy, stamp_w, stamp_h)

    c.line(sx, sy + 10*mm, sx + stamp_w, sy + 10*mm)
    c.line(sx, sy + 20*mm, sx + stamp_w, sy + 20*mm)
    c.line(sx + 45*mm, sy, sx + 45*mm, sy + stamp_h)
    c.line(sx + 135*mm, sy, sx + 135*mm, sy + stamp_h)
    c.line(sx + 160*mm, sy, sx + 160*mm, sy + stamp_h)

    c.setFont(font, 7)
    c.drawString(sx + 3*mm, sy + 26*mm, "СК АРЕАЛ-НЕВА")
    c.drawString(sx + 48*mm, sy + 26*mm, "Индивидуальный жилой дом")
    c.drawString(sx + 138*mm, sy + 26*mm, "Стадия")
    c.drawString(sx + 163*mm, sy + 26*mm, "Лист")

    c.setFont(font, 9)
    c.drawString(sx + 48*mm, sy + 14*mm, str(sheet_title)[:55])
    c.drawString(sx + 138*mm, sy + 14*mm, "П")
    c.drawString(sx + 163*mm, sy + 14*mm, f"{sheet_no}/{sheet_total}")

    c.setFont(font, 7)
    c.drawString(margin + 3*mm, margin + 3*mm, f"{section} · FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT")

def _ff12_table(c, x, y, widths, rows, font, row_h=6, size=7):
    from reportlab.lib.units import mm

    c.setFont(font, size)
    yy = y
    for row in rows:
        xx = x
        max_lines = 1
        split_cells = []
        for val, w in zip(row, widths):
            text = str(val)
            chars = max(8, int(w / (size * 0.55)))
            lines = [text[i:i+chars] for i in range(0, len(text), chars)] or [""]
            split_cells.append(lines[:3])
            max_lines = max(max_lines, len(lines[:3]))
        h = row_h * mm * max_lines
        for cell_lines, w in zip(split_cells, widths):
            c.rect(xx, yy - h, w*mm, h)
            ty = yy - 4*mm
            for line in cell_lines:
                c.drawString(xx + 1.5*mm, ty, line)
                ty -= row_h*mm
            xx += w*mm
        yy -= h
    return yy

def _ff12_draw_plan(c, x, y, w, h, data, calc, font, title):
    from reportlab.lib.units import mm

    L = float(data["length_m"])
    W = float(data["width_m"])
    step = int(data["rebar_step_mm"])
    scale = min(w / max(L, 1), h / max(W, 1))
    rw = L * scale
    rh = W * scale
    x0 = x + (w - rw) / 2
    y0 = y + (h - rh) / 2

    c.setFont(font, 9)
    c.drawString(x, y + h + 4*mm, title)
    c.setLineWidth(1.1)
    c.rect(x0, y0, rw, rh)

    c.setLineWidth(0.25)
    grid = max(3*mm, step / 1000 * scale)
    xx = x0 + grid
    while xx < x0 + rw:
        c.line(xx, y0, xx, y0 + rh)
        xx += grid
    yy = y0 + grid
    while yy < y0 + rh:
        c.line(x0, yy, x0 + rw, yy)
        yy += grid

    c.setFont(font, 7)
    c.drawString(x0, y0 - 5*mm, f"{L:g} м")
    c.saveState()
    c.translate(x0 - 7*mm, y0)
    c.rotate(90)
    c.drawString(0, 0, f"{W:g} м")
    c.restoreState()

def _ff12_draw_section(c, x, y, w, h, data, font, title):
    from reportlab.lib.units import mm

    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    total = max(slab + sand + gravel, 1)
    c.setFont(font, 9)
    c.drawString(x, y + h + 4*mm, title)

    layer_rows = [
        ("Песчаная подушка", sand, "послойное уплотнение"),
        ("Щебёночное основание", gravel, "послойное уплотнение"),
        ("Фундаментная плита", slab, f"бетон {data['concrete_class']}, защитный слой {data.get('cover_mm',40)} мм"),
    ]

    yy = y
    for name, th, note in layer_rows:
        hh = max(10*mm, h * th / total)
        c.rect(x, yy, w, hh)
        c.setFont(font, 7)
        c.drawString(x + 3*mm, yy + hh/2 - 2*mm, f"{name}: {th} мм — {note}")
        yy += hh

    c.setLineWidth(0.4)
    c.line(x + 5*mm, y + h - 7*mm, x + w - 5*mm, y + h - 7*mm)
    c.line(x + 5*mm, y + h - 13*mm, x + w - 5*mm, y + h - 13*mm)
    c.setFont(font, 7)
    c.drawString(x + 8*mm, y + h - 5*mm, f"{data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм")

def _ff12_draw_nodes(c, x, y, w, h, data, font):
    from reportlab.lib.units import mm

    c.setFont(font, 9)
    c.drawString(x, y + h + 4*mm, "Типовые узлы")
    node_w = w / 3 - 3*mm
    names = ["Край плиты", "Защитный слой", "Основание"]
    for i, name in enumerate(names):
        nx = x + i * (node_w + 4*mm)
        c.rect(nx, y, node_w, h)
        c.setFont(font, 7)
        c.drawString(nx + 2*mm, y + h - 5*mm, name)
        c.line(nx + 4*mm, y + 12*mm, nx + node_w - 4*mm, y + 12*mm)
        c.line(nx + 4*mm, y + 20*mm, nx + node_w - 4*mm, y + 20*mm)
        c.drawString(nx + 2*mm, y + 5*mm, f"Ø{data['rebar_diam_mm']} {data['rebar_class']}")
        c.drawString(nx + 2*mm, y + 28*mm, f"ЗС {data.get('cover_mm',40)} мм")

def _ff12_material_rows(data, calc):
    return [
        ["1", f"Бетон {data['concrete_class']} для фундаментной плиты", "м³", calc["concrete_m3"], "по объёму плиты"],
        ["2", "Песчаная подушка", "м³", calc["sand_m3"], "послойное уплотнение"],
        ["3", "Щебёночное основание", "м³", calc["gravel_m3"], "послойное уплотнение"],
        ["4", f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']}", "п.м", calc["rebar_m_total"], "верхняя и нижняя сетка"],
        ["5", f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']}", "т", calc["rebar_t"], "расчётный вес"],
    ]

def _ff12_write_compact_project_pdf(path: str, data: dict, calc: dict) -> str:
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _ff12_font()
    page_w, page_h = landscape(A3)
    c = canvas.Canvas(path, pagesize=landscape(A3))

    section = data["section"]
    sheets = [
        "Общие данные + ведомость листов",
        "План плиты + армирование",
        "Разрезы и узлы",
        "Спецификация + контроль качества",
    ]
    sheet_total = len(sheets)

    # Sheet 1
    _ff12_draw_stamp(c, page_w, page_h, sheets[0], 1, sheet_total, section, font)
    c.setFont(font, 14)
    c.drawString(20*mm, 275*mm, "Проект фундаментной плиты")
    c.setFont(font, 9)
    left_rows = [
        ["Раздел", section],
        ["Тип", "Фундаментная плита"],
        ["Размер", f"{data['length_m']:g} x {data['width_m']:g} м"],
        ["Толщина плиты", f"{data['slab_mm']} мм"],
        ["Основание", f"Песок {data['sand_mm']} мм, щебень {data['gravel_mm']} мм"],
        ["Бетон", data["concrete_class"]],
        ["Арматура", f"{data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм"],
        ["Площадь", f"{calc['area_m2']} м²"],
        ["Объём бетона", f"{calc['concrete_m3']} м³"],
    ]
    _ff12_table(c, 20*mm, 258*mm, [42, 95], left_rows, font, row_h=6, size=8)

    sheet_rows = [[str(i+1), title] for i, title in enumerate(sheets)]
    _ff12_table(c, 180*mm, 258*mm, [15, 110], [["№", "Наименование листа"]] + sheet_rows, font, row_h=6, size=8)

    norm_rows = [["№", "Нормативная база"]] + [[str(i+1), n] for i, n in enumerate(NORMATIVE_NOTES[:6])]
    _ff12_table(c, 20*mm, 165*mm, [15, 250], norm_rows, font, row_h=6, size=7)
    c.showPage()

    # Sheet 2
    _ff12_draw_stamp(c, page_w, page_h, sheets[1], 2, sheet_total, section, font)
    _ff12_draw_plan(c, 20*mm, 65*mm, 235*mm, 165*mm, data, calc, font, "План фундаментной плиты и сетка армирования")
    c.setFont(font, 8)
    notes = [
        f"Нижняя и верхняя сетки: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм",
        f"Защитный слой бетона: {data.get('cover_mm',40)} мм",
        f"Количество стержней по X/Y: {calc['bars_x']} / {calc['bars_y']}",
        f"Общий расход арматуры: {calc['rebar_m_total']} п.м / {calc['rebar_t']} т",
    ]
    y = 245*mm
    for n in notes:
        c.drawString(275*mm, y, n)
        y -= 8*mm
    c.showPage()

    # Sheet 3
    _ff12_draw_stamp(c, page_w, page_h, sheets[2], 3, sheet_total, section, font)
    _ff12_draw_section(c, 20*mm, 60*mm, 170*mm, 105*mm, data, font, "Разрез 1-1")
    _ff12_draw_section(c, 215*mm, 60*mm, 170*mm, 105*mm, data, font, "Разрез 2-2")
    _ff12_draw_nodes(c, 20*mm, 195*mm, 365*mm, 55*mm, data, font)
    c.showPage()

    # Sheet 4
    _ff12_draw_stamp(c, page_w, page_h, sheets[3], 4, sheet_total, section, font)
    rows = [["№", "Наименование", "Ед", "Кол-во", "Примечание"]] + _ff12_material_rows(data, calc)
    _ff12_table(c, 20*mm, 260*mm, [12, 120, 20, 30, 95], rows, font, row_h=7, size=8)

    qc = [
        ["1", "Проверить подготовку основания и уплотнение"],
        ["2", "Проверить защитный слой и фиксаторы арматуры"],
        ["3", "Проверить шаг и диаметр арматуры до бетонирования"],
        ["4", "Принять бетон по паспортам и фактической укладке"],
    ]
    _ff12_table(c, 20*mm, 170*mm, [12, 190], [["№", "Контроль качества"]] + qc, font, row_h=7, size=8)
    c.showPage()

    c.save()
    return path

async def create_compact_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    data = parse_foundation_request(raw_input)
    data["section"] = "КЖ"
    data["project_kind"] = "foundation_slab"
    calc = calc_foundation(data)

    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id or "manual"))[:30]
    out_dir = Path(tempfile.gettempdir()) / f"areal_compact_project_{safe}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = str(out_dir / f"КЖ_COMPACT_PROJECT_{safe}.pdf")
    manifest_path = str(out_dir / f"КЖ_COMPACT_PROJECT_{safe}.manifest.json")

    _ff12_write_compact_project_pdf(pdf_path, data, calc)

    pdf_text = extract_pdf_text(pdf_path)
    valid, reason = validate_foundation_text(pdf_text)

    manifest = {
        "engine": "FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "topic_id": topic_id,
        "input": raw_input,
        "data": data,
        "calc": calc,
        "sheet_count": 4,
        "pdf_text_valid": valid,
        "pdf_text_error": reason,
        "pdf_path": pdf_path,
    }
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    from core.engine_base import upload_artifact_to_drive
    pdf_link = upload_artifact_to_drive(pdf_path, task_id, topic_id)
    manifest_link = upload_artifact_to_drive(manifest_path, task_id, topic_id)

    if not pdf_link:
        return {"success": False, "engine": "FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT", "error": "PDF_UPLOAD_FAILED"}

    return {
        "success": True,
        "engine": "FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT",
        "section": "КЖ",
        "project_kind": "foundation_slab",
        "sheet_count": 4,
        "pdf_path": pdf_path,
        "pdf_link": str(pdf_link),
        "manifest_link": str(manifest_link or ""),
        "data": data,
        "calc": calc,
        "message": (
            "Проект создан компактным PDF-альбомом\\n"
            "Engine: FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT\\n"
            "Раздел: КЖ\\n"
            "Тип: фундаментная плита\\n"
            "Листов: 4\\n"
            f"Размер: {data['length_m']:g} x {data['width_m']:g} м\\n"
            f"Плита: {data['slab_mm']} мм\\n"
            f"Бетон: {data['concrete_class']}\\n"
            f"Арматура: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм\\n"
            f"Бетон: {calc['concrete_m3']} м³\\n"
            f"Арматура: {calc['rebar_t']} т\\n\\n"
            f"PDF: {pdf_link}\\n"
            f"MANIFEST: {manifest_link or ''}\\n\\n"
            "Доволен результатом? Ответь: Да / Уточни / Правки"
        )
    }

# override public name inside this module
create_full_project_documentation = create_compact_project_documentation
# === END FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT ===
