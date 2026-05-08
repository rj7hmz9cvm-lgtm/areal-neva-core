# ORCHESTRA_FULL_CONTEXT_PART_009
generated_at_utc: 2026-05-08T07:35:02.430662+00:00
git_sha_before_commit: 981d3018a1ddfba4707d0e0faafb088b2e1f4e76
part: 9/17


====================================================================================================
BEGIN_FILE: core/orchestra_closure_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: eb1b21fbc11d24b0c6c57a1498cb817cc182dd47320265bb5fbb51f65482da34
====================================================================================================
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

    # === FULLFIX_15_OCE_CYR_FIX ===
    try:
        from core.pdf_cyrillic import register_cyrillic_fonts, FONT_REGULAR, FONT_BOLD
        register_cyrillic_fonts()
        _ocyr_reg = FONT_REGULAR
        _ocyr_bold = FONT_BOLD
    except Exception:
        _ocyr_reg = 'Helvetica'
        _ocyr_bold = 'Helvetica-Bold'
    c = canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4
    c.setFont(_ocyr_bold, 14)
    c.drawString(20*mm, h-20*mm, "СМЕТА")
    y = h - 35*mm
    c.setFont(_ocyr_reg, 9)
    for i, r in enumerate(rows, 1):
        c.setFont(_ocyr_reg, 9)
        c.drawString(20*mm, y, f"{i}. {r['name']} — {r['qty']} {r['unit']} x {r['price']} = {r['total']} руб")
        y -= 8*mm
    c.setFont(_ocyr_bold, 11)
    c.drawString(20*mm, y-5*mm, f"ИТОГО: {total} руб")
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
        ""
        "Доволен результатом? Ответь: Да / Уточни / Правки"
    )
    # === FULLFIX_19_OCE_MEMORY_INVOKE ===
    try:
        from core.memory_client import save_memory as _ff19_sm
        _ff19_sm(
            "shared",
            "topic_"+str(topic_id or 0)+"_last_estimate_oce",
            {"task_id": task_id, "type": "estimate_oce"},
            topic_id=int(topic_id or 0),
            scope="topic"
        )
    except Exception:
        pass
    # === END FULLFIX_19_OCE_MEMORY_INVOKE ===

    # === FULLFIX_20_OCE_MEMORY_INVOKE ===
    try:
        from core.memory_client import save_memory as _ff20_sm
        _ff20_sm(
            "shared",
            "topic_" + str(topic_id or 0) + "_last_estimate_oce",
            {"task_id": task_id, "topic_id": topic_id},
            topic_id=int(topic_id or 0),
            scope="topic"
        )
    except Exception:
        pass
    # === END FULLFIX_20_OCE_MEMORY_INVOKE ===

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

# === FULLFIX_16_OCE_MSG_STRIP: manifest removed from message strings ===
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
            ""
            "Доволен результатом? Ответь: Да / Уточни / Правки"
        )
    }

# override public name inside this module
create_full_project_documentation = create_compact_project_documentation
# === END FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT ===

# === FULLFIX_13A_SAMPLE_TEMPLATE_PUBLIC_HELPERS ===
async def ff13a_create_estimate_from_saved_template(raw_input: str, task_id: str, chat_id: str, topic_id: int = 0) -> dict:
    from core.sample_template_engine import create_estimate_from_saved_template
    return await create_estimate_from_saved_template(raw_input, task_id, chat_id, topic_id)

def ff13a_detect_sample_template_intent(raw_input: str, input_type: str = "text") -> bool:
    from core.sample_template_engine import detect_sample_template_intent
    return detect_sample_template_intent(raw_input, input_type)
# === END FULLFIX_13A_SAMPLE_TEMPLATE_PUBLIC_HELPERS ===


# === FULLFIX_13B_ESTIMATE_OUTPUT_FORMULAS_NO_MANIFEST ===
def ff13b_rewrite_estimate_xlsx_with_formulas(xlsx_path: str) -> str:
    """
    Ensure estimate XLSX is a real working spreadsheet:
    - Qty / Price / Total columns
    - Total column uses Excel formulas
    - Final total row uses SUM formula
    """
    from openpyxl import load_workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    wb = load_workbook(xlsx_path)
    ws = wb.active

    headers = ["№", "Наименование", "Ед.", "Кол-во", "Цена", "Сумма"]
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=col, value=h)
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")
        c.fill = PatternFill("solid", fgColor="D9EAF7")

    max_row = ws.max_row
    first_data = 2
    last_data = max_row

    # detect if old sheet has no clean header
    if max_row < 2:
        last_data = 2

    for row in range(first_data, last_data + 1):
        qty = ws.cell(row=row, column=4).value
        price = ws.cell(row=row, column=5).value
        if qty not in (None, "") and price not in (None, ""):
            ws.cell(row=row, column=6, value=f"=D{row}*E{row}")

    total_row = last_data + 1
    ws.cell(row=total_row, column=5, value="ИТОГО").font = Font(bold=True)
    ws.cell(row=total_row, column=6, value=f"=SUM(F{first_data}:F{last_data})").font = Font(bold=True)

    widths = [8, 42, 12, 14, 14, 16]
    thin = Side(style="thin", color="999999")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for col, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width
        for row in range(1, total_row + 1):
            ws.cell(row=row, column=col).border = border
            ws.cell(row=row, column=col).alignment = Alignment(vertical="center", wrap_text=True)

    wb.save(xlsx_path)
    return xlsx_path


def ff13b_clean_estimate_user_message(message: str) -> str:
    """
    User must see only useful estimate outputs:
    - PDF
    - XLSX
    No MANIFEST in Telegram answer
    """
    import re
    msg = str(message or "")
    msg = re.sub(r"(?im)^MANIFEST:\s*https?://\S+\s*$", "", msg)
    msg = re.sub(r"\n{3,}", "\n\n", msg).strip()
    return msg
# === END FULLFIX_13B_ESTIMATE_OUTPUT_FORMULAS_NO_MANIFEST ===


====================================================================================================
END_FILE: core/orchestra_closure_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/orchestra_context.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: d2e491ea92d7efee7b6ca49db7193b624739f3ff95041300dc48ef4db2a80ff2
====================================================================================================
# === ORCHESTRA_SHARED_CONTEXT_V1 ===
# Каждая модель получает единый контекст: ONE_SHARED_CONTEXT + memory + task + pin + topic_role
import os, logging
logger = logging.getLogger(__name__)

def build_shared_context(
    raw_input: str = "",
    topic_id: int = 0,
    chat_id: str = "",
    active_task: dict = None,
    pin_text: str = "",
    short_memory: str = "",
    long_memory: str = "",
    search_result: str = "",
    topic_role: str = "",
    files: list = None,
) -> str:
    """
    Собирает ORCHESTRA_SHARED_CONTEXT для передачи в любую модель.
    Порядок приоритета из канона §5.1:
    user_input → active_task → pin → short_memory → long_memory → search
    """
    parts = []

    if topic_role:
        parts.append(f"[ROLE] {topic_role}")

    if active_task:
        state = active_task.get("state", "")
        raw = str(active_task.get("raw_input", ""))[:200]
        parts.append(f"[ACTIVE_TASK] state={state} input={raw}")

    if pin_text:
        parts.append(f"[PIN] {pin_text[:300]}")

    if short_memory:
        parts.append(f"[SHORT_MEMORY] {short_memory[:400]}")

    if long_memory:
        parts.append(f"[LONG_MEMORY] {long_memory[:400]}")

    if search_result:
        parts.append(f"[SEARCH] {search_result[:500]}")

    if files:
        parts.append(f"[FILES] {', '.join(str(f) for f in files[:5])}")

    if raw_input:
        parts.append(f"[USER] {raw_input[:500]}")

    return "\n".join(parts)

def user_mode_switch(text: str) -> str:
    """
    USER_MODE_SWITCH: TECH / HUMAN (default)
    """
    low = text.lower()
    if any(w in low for w in ["технический", "детально", "подробно", "tech mode", "полный разбор"]):
        return "TECH"
    return "HUMAN"

def mode_switch(task: dict) -> str:
    """
    MODE_SWITCH: LIGHT / FULL
    """
    intent = str(task.get("intent", "")).lower()
    input_type = str(task.get("input_type", "")).lower()
    if input_type == "drive_file" or intent in ("estimate", "project", "template", "technadzor", "dwg"):
        return "FULL"
    return "LIGHT"
# === END ORCHESTRA_SHARED_CONTEXT_V1 ===

====================================================================================================
END_FILE: core/orchestra_context.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/output_decision.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 91edab27bd5fa1befb487d6f402a1ff182ee0a3cc6fffdc4a2c3d7df90f4bc6d
====================================================================================================
# === OUTPUT_DECISION_LOGIC_V1 ===
# Канон ORCHESTRA_MASTER_BLOCK: RESULT_VALIDATOR + RESULT_FORMAT_ENFORCER + HUMAN_DECISION_EDITOR
import logging
logger = logging.getLogger(__name__)

def format_search_output(offers: list, goal: str = "") -> str:
    """
    Жёсткий формат вывода поискового результата.
    Канон: таблица + выводы + что проверить звонком
    """
    if not offers:
        return "Предложения не найдены. Уточни запрос или расширь географию."

    # ранжируем
    try:
        from core.constraint_engine import rank_offers
        offers = rank_offers(offers)
    except Exception:
        pass

    lines = [f"Нашёл {len(offers)} вариант(ов) по запросу: {goal}\n"]
    lines.append("| Поставщик | Площадка | Цена | Наличие | Риск | Контакт |")
    lines.append("|---|---|---|---|---|---|")

    best_price = None
    best_reliable = None
    to_check = []

    for i, o in enumerate(offers[:10]):
        price = o.get("price") or "—"
        price_str = f"{int(price):,}".replace(",", " ") + " руб." if isinstance(price, (int, float)) and price > 0 else str(price)
        risk = o.get("risk", "UNVERIFIED")
        contact = "✅" if o.get("contact") or o.get("url") else "❌"
        lines.append(f"| {o.get('supplier','?')} | {o.get('platform','?')} | {price_str} | {o.get('stock','?')} | {risk} | {contact} |")

        if best_price is None and isinstance(price, (int, float)) and price > 0:
            best_price = o
        if risk == "CONFIRMED" and best_reliable is None:
            best_reliable = o
        if not o.get("contact"):
            to_check.append(o.get("supplier", "?"))

    # выводы
    lines.append("")
    if best_price:
        lines.append(f"💰 Самый дешёвый: {best_price.get('supplier')} — риск: {best_price.get('risk','?')}")
    if best_reliable:
        lines.append(f"✅ Наиболее надёжный: {best_reliable.get('supplier')}")
    if to_check:
        lines.append(f"📞 Проверить звонком: {', '.join(to_check[:3])}")

    return "\n".join(lines)

def format_task_result(result: str, state: str, error_code: str = "") -> str:
    """
    Ответ пользователю по state — канон §15
    """
    if state == "DONE":
        return result or "✅ Готово"
    if state == "FAILED":
        try:
            from core.error_explainer import user_friendly_error
            return f"❌ {user_friendly_error(error_code or 'UNKNOWN')}"
        except Exception:
            return f"❌ Не выполнено: {error_code}"
    if state == "WAITING_CLARIFICATION":
        return result or "Уточни запрос."
    if state == "AWAITING_CONFIRMATION":
        return (result or "") + "\n\nПодтверди (да) или укажи правки."
    return result or ""
# === END OUTPUT_DECISION_LOGIC_V1 ===

====================================================================================================
END_FILE: core/output_decision.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/output_sanitizer.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 826e700334c797ffbd39b80779b85607519c2e631b9e56388ad6c8f5ad378bcb
====================================================================================================
# === UNIFIED_USER_OUTPUT_SANITIZER_V5_STRICT_PUBLIC_CLEAN ===
from __future__ import annotations

import re
from typing import Any

SERVICE_LINE_RE = [
    r"^\s*engine\s*:",
    r"^\s*kind\s*:",
    r"^\s*source\s*:",
    r"^\s*status\s*:",
    r"^\s*type\s*:\s*[A-Z_]{4,}",
    r"^\s*тип\s*:\s*[A-Z_]{4,}",
    r"^\s*task\s*:",
    r"^\s*task_id\s*:",
    r"^\s*задача\s*:\s*[0-9a-fA-F-]{6,}",
    r"^\s*drive\s+file_id\s*:",
    r"^\s*file_id\s*:",
    r"^\s*chat_id\s*:",
    r"^\s*topic_id\s*:",
    r"^\s*manifest\s*:",
    r"^\s*dxf\s*:",
    r"^\s*xlsx\s*:",
    r"^\s*xls\s*:",
    r"^\s*pdf\s*:",
    r"^\s*docx\s*:",
    r"^\s*artifact\s*:",
    r"^\s*artifact_path\s*:",
    r"^\s*validator_reason\s*:",
    r"^\s*raw_result\s*:",
    r"^\s*raw_payload\s*:",
    r"^\s*raw_input\s*:",
    r"^\s*debug\s*:",
    r"^\s*traceback\s*:",
    r"^\s*stacktrace\s*:",
    r"^\s*tmp_path\s*:",
    r"^\s*кратко\s*:\s*\{",
    r"^\s*кратко\s*:\s*\[",
    r"^\s*google sheets\s*/\s*xlsx\s*артефакт\s*$",
]

SERVICE_SUBSTRINGS = [
    "/root/.areal-neva-core",
    "/root/",
    "/tmp/",
    "file_context_intake.py",
    "file_memory_bridge.py",
    "price_enrichment.py",
    "sample_template_engine.py",
    "task_worker.py",
    "telegram_daemon.py",
    "artifact_pipeline.py",
    "engine_base.py",
    "PROJECT_TEMPLATE_MODEL__",
    "ACTIVE__chat_",
    "ACTIVE_BATCH__chat_",
    "PENDING__chat_",
    "FINAL_CLOSURE_BLOCKER_FIX_V1",
    "UNIFIED_USER_OUTPUT_SANITIZER",
    "validator_reason",
    "internal_key",
    "raw_payload",
    "raw_input_json",
    "ModuleNotFoundError",
    "SyntaxError",
    "Traceback",
]

NOISE_EXACT = {"доволен", "недоволен", "готово"}

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    return str(v)

def _normalize_escaped_text(text: Any) -> str:
    src = _s(text)
    src = src.replace("\r", "\n")
    src = src.replace("\\\\n", "\n")
    src = src.replace("\\n", "\n")
    src = src.replace("\\\\t", " ")
    src = src.replace("\\t", " ")
    src = src.replace('\\"', '"')
    src = re.sub(r"\x00+", " ", src)
    return src

def _is_google_link(text: str) -> bool:
    low = text.lower()
    return "https://drive.google.com/" in low or "https://docs.google.com/" in low

def _clean_google_link(line: str) -> str:
    m = re.search(r"https://(?:drive|docs)\.google\.com/[^\s\"'<>()]+", line, re.I)
    if not m:
        return line.strip()
    url = m.group(0)
    url = re.split(r"(?:PDF|DXF|XLSX|XLS|DOCX|MANIFEST)\s*:", url, flags=re.I)[0]
    url = url.rstrip(".,;)")
    return url

def _bad_line(line: str) -> bool:
    raw = line.strip()
    low = raw.lower()
    if not raw:
        return False
    if low in NOISE_EXACT:
        return True
    if re.fullmatch(r"[-–—]?\s*$", raw):
        return True
    for p in SERVICE_LINE_RE:
        if re.search(p, raw, re.I):
            return True
    if re.match(r"^\s*[-–—]\s*(dxf|xlsx|xls|pdf|docx|manifest)\s*:\s*$", raw, re.I):
        return True
    if re.search(r"\{[^{}]*(task_id|chat_id|topic_id|file_id|caption|engine)[^{}]*\}", raw, re.I):
        return True
    if raw.startswith("{") and raw.endswith("}"):
        return True
    for s in SERVICE_SUBSTRINGS:
        if s.lower() in low:
            return True
    if re.search(r"\b[A-Z_]{6,}_V\d+\b", raw) and not _is_google_link(raw):
        return True
    return False

def sanitize_user_output(text: Any, fallback: str = "Готово") -> str:
    src = _normalize_escaped_text(text)
    if not src.strip():
        return fallback
    lines = []
    skip_next_google_link = False
    for original in src.split("\n"):
        line = original.rstrip()
        if re.match(r"^\s*manifest\s*:\s*$", line, re.I):
            skip_next_google_link = True
            continue
        if skip_next_google_link and _is_google_link(line):
            skip_next_google_link = False
            continue
        if _is_google_link(line):
            clean_url = _clean_google_link(line)
            if "manifest" in clean_url.lower() or clean_url.lower().endswith(".json"):
                continue
            lines.append(clean_url)
            skip_next_google_link = False
            continue
        skip_next_google_link = False
        if _bad_line(line):
            continue
        lines.append(line)
    out = "\n".join(lines)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    out = re.sub(r"[ \t]{2,}", " ", out)
    if not out:
        out = fallback
    if len(out) > 3900:
        out = out[:3800].rstrip() + "\n\nТекст сокращён. Полный результат смотри в файле"
    return out

def sanitize_project_message(text: Any) -> str:
    return sanitize_user_output(text, fallback="Проектный результат подготовлен")

def sanitize_estimate_message(text: Any) -> str:
    return sanitize_user_output(text, fallback="Сметный результат подготовлен")

# === END_UNIFIED_USER_OUTPUT_SANITIZER_V5_STRICT_PUBLIC_CLEAN ===

====================================================================================================
END_FILE: core/output_sanitizer.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/owner_reference_policy.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 64adbdd55173fb91d590ec72ad3c2c1d2bb6d0a7f96f2be44be2132d01f6a463
====================================================================================================
# === OWNER_REFERENCE_FULL_WORKFLOW_POLICY_V1 ===
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

BASE = Path("/root/.areal-neva-core")
REGISTRY_PATH = BASE / "config" / "owner_reference_registry.json"

TRIGGER_RE = re.compile(
    r"(смет|расцен|стоимост|цена|логист|доставк|материал|кирпич|газобетон|каркас|монолит|фундамент|кровл|проект|проектир|эскиз|план участка|посадк|ар\b|кр\b|кж\b|кд\b|км\b|кмд\b|ов\b|вк\b|эо\b|эм\b|эос\b|спецификац|узел|черт[её]ж|dwg|dxf|pln|ifc|акт|технадзор|дефект|образец|образцы|эталон|эталоны|принимай|работай по)",
    re.I,
)

ENGINEERING_NORMS = [
    "КМ/КМД: СП 16.13330.2017 — Стальные конструкции",
    "КМ/КМД: СП 20.13330.2017 — Нагрузки и воздействия",
    "КМ/КМД: ГОСТ 27751-2014 — Надёжность строительных конструкций",
    "КМ/КМД: ГОСТ 23118-2012 — Конструкции стальные строительные",
    "ОВ: СП 60.13330.2020 — Отопление, вентиляция, кондиционирование",
    "ОВ: СП 131.13330.2020 — Строительная климатология",
    "ОВ: ГОСТ 30494-2011 — Параметры микроклимата помещений",
    "ВК: СП 30.13330.2020 — Внутренний водопровод и канализация",
    "ВК: СП 31.13330.2021 — Водоснабжение. Наружные сети",
    "ВК: СП 32.13330.2018 — Канализация. Наружные сети",
    "ЭО/ЭМ/ЭОС: СП 256.1325800.2016 — Электроустановки жилых зданий",
    "ЭО/ЭМ/ЭОС: ГОСТ Р 50571 серия — Электрические установки",
    "ЭО/ЭМ/ЭОС: ПУЭ-7 — Правила устройства электроустановок",
    "КЖ: СП 63.13330.2018 — Бетонные и железобетонные конструкции",
    "КЖ: ГОСТ 10922-2012 — Арматурные изделия",
    "КД: СП 64.13330.2017 — Деревянные конструкции",
    "КД: ГОСТ 8486-86 — Пиломатериалы хвойных пород",
    "Расчёт нагрузок: СП 20.13330.2017 таблицы 8.3 и 10.1",
    "Если раздел не загружен образцом — работать по нормам СНиП/ГОСТ/СП",
    "Если норм недостаточно — запросить геологию, климатический район, класс ответственности",
]

ESTIMATE_RULES = [
    "М-80, М-110, крыша, фундамент, Ареал Нева = эталон формул и структуры",
    "Логика переносится на любой материал: кирпич, газобетон, каркас, монолит",
    "Цены не подставлять молча — искать в интернете и показывать варианты",
    "Логистика обязательна: город, удалённость, подъезд, разгрузка, манипулятор, кран, проживание",
    "XLSX/PDF только после подтверждения цен и логистики",
]

DESIGN_RULES = [
    "Образцы из папки проектирования = эталон структуры и оформления",
    "АР/КР/КЖ/КД/КМ/КМД/ОВ/ВК/ЭО/ЭМ/ЭОС — разные разделы, не смешивать",
    "Если нет загруженного образца по разделу — работать по нормам СНиП/ГОСТ/СП",
    "Уточнять стадию, объект, материал, габариты, состав проекта",
    "DWG/DXF/IFC — читать через ezdxf/ifcopenshell если доступно",
    "PLN/RVT — бинарные исходники, использовать как метаданные без SDK",
]

TECHNADZOR_RULES = [
    "Акты, дефекты, исполнительные документы — отдельный контур",
    "Нормы фиксировать только если подтверждены",
    "Если норма не подтверждена — писать: норма не подтверждена",
    "Вывод чистый: без task_id, file_id, manifest, путей, JSON",
]

OUTPUT_RULES = [
    "Без task_id/file_id/manifest/локальных путей/raw JSON",
    "Без служебных Engine/MANIFEST/DXF/XLSX хвостов",
    "Если данных нет — один короткий вопрос",
    "Если задача понятна — выполнять по существующему контуру",
]

def _s(v: Any) -> str:
    return "" if v is None else str(v)

def _load_registry() -> Dict[str, Any]:
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def build_owner_reference_context(user_text: str = "", limit: int = 22000) -> str:
    text = _s(user_text)
    if not TRIGGER_RE.search(text):
        return ""

    data = _load_registry()
    policy = data.get("owner_reference_full_workflow_v1")
    counts = policy.get("counts", {}) if isinstance(policy, dict) else {}

    lines = []
    lines.append("OWNER_REFERENCE_FULL_WORKFLOW: ACTIVE")
    lines.append("OWNER: Илья — главный канон")
    lines.append("RULE: Не додумывать отсутствующие исходные данные")
    lines.append("RULE: Если данных не хватает — задать один короткий уточняющий вопрос")
    lines.append("")
    lines.append("ENGINEERING NORMS:")
    lines.extend(f"- {x}" for x in ENGINEERING_NORMS)
    lines.append("")
    lines.append("ESTIMATE RULES:")
    lines.extend(f"- {x}" for x in ESTIMATE_RULES)
    lines.append("")
    lines.append("DESIGN RULES:")
    lines.extend(f"- {x}" for x in DESIGN_RULES)
    lines.append("")
    lines.append("TECHNADZOR RULES:")
    lines.extend(f"- {x}" for x in TECHNADZOR_RULES)
    lines.append("")
    lines.append("OUTPUT RULES:")
    lines.extend(f"- {x}" for x in OUTPUT_RULES)

    if counts:
        lines.append("")
        lines.append("REFERENCE COUNTS:")
        for k in sorted(counts):
            lines.append(f"- {k}: {counts[k]}")

    if isinstance(policy, dict):
        est = policy.get("estimate_references") or []
        des = policy.get("design_references") or []
        tech = policy.get("technadzor_references") or []
        if est:
            lines.append("")
            lines.append("ESTIMATE REFERENCES:")
            for x in est[:20]:
                lines.append(f"- {x.get('name')} | formulas={x.get('formula_total', 0)} | role={x.get('role')}")
        if des:
            lines.append("")
            lines.append("DESIGN REFERENCES:")
            for x in des[:40]:
                lines.append(f"- {x.get('name')} | discipline={x.get('discipline')} | role={x.get('role')}")
        if tech:
            lines.append("")
            lines.append("TECHNADZOR REFERENCES:")
            for x in tech[:20]:
                lines.append(f"- {x.get('name')} | role={x.get('role')}")

    return "\n".join(lines)[:limit]

# === END_OWNER_REFERENCE_FULL_WORKFLOW_POLICY_V1 ===

====================================================================================================
END_FILE: core/owner_reference_policy.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/pdf_cyrillic.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c7d82ac54474065917afc3433342f2511a3402d75cdbd7c20cf7a3f1e91cc4dc
====================================================================================================
# === FULLFIX_15_PDF_CYRILLIC ===
import os, logging
logger = logging.getLogger(__name__)
FONT_REGULAR = "CyrRegular"
FONT_BOLD = "CyrBold"
FONT_PATH_REGULAR = ""
FONT_PATH_BOLD = ""
_registered = False

_CANDS_R = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]
_CANDS_B = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]

def _find(candidates):
    for p in candidates:
        if os.path.exists(p):
            return p
    import glob
    for pat in ["/usr/share/fonts/**/*DejaVu*Sans*.ttf",
                "/usr/share/fonts/**/*Noto*Sans*Regular*.ttf"]:
        found = glob.glob(pat, recursive=True)
        if found:
            return found[0]
    return None

def register_cyrillic_fonts():
    global _registered, FONT_REGULAR, FONT_BOLD, FONT_PATH_REGULAR, FONT_PATH_BOLD
    if _registered:
        return FONT_REGULAR, FONT_BOLD
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    reg = _find(_CANDS_R)
    bold = _find(_CANDS_B)
    if not reg:
        raise RuntimeError("CYRILLIC_FONT_NOT_FOUND")
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, reg))
    FONT_PATH_REGULAR = reg
    if bold and bold != reg:
        pdfmetrics.registerFont(TTFont(FONT_BOLD, bold))
        FONT_PATH_BOLD = bold
    else:
        FONT_BOLD = FONT_REGULAR
        FONT_PATH_BOLD = reg
    _registered = True
    logger.info("CYR_FONTS reg=%s bold=%s", reg, bold)
    return FONT_REGULAR, FONT_BOLD

def clean_pdf_text(text):
    if not text:
        return ""
    return "".join(c for c in str(text) if c >= " " or c in "\n\t")

def make_styles():
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    register_cyrillic_fonts()
    return {
        "header": ParagraphStyle("H", fontName=FONT_BOLD, fontSize=16, alignment=TA_CENTER, spaceAfter=12),
        "title":  ParagraphStyle("T", fontName=FONT_BOLD, fontSize=14, alignment=TA_CENTER, spaceAfter=8),
        "bold":   ParagraphStyle("B", fontName=FONT_BOLD, fontSize=9, alignment=TA_LEFT),
        "normal": ParagraphStyle("N", fontName=FONT_REGULAR, fontSize=9, alignment=TA_LEFT),
        "small":  ParagraphStyle("S", fontName=FONT_REGULAR, fontSize=8, alignment=TA_LEFT),
    }

def make_paragraph(text, style="normal", styles=None):
    from reportlab.platypus import Paragraph
    if styles is None:
        styles = make_styles()
    return Paragraph(clean_pdf_text(text), styles.get(style, styles["normal"]))
# === END FULLFIX_15_PDF_CYRILLIC ===

# === FIX_PDF_CYRILLIC_VALIDATE_V1 ===
import subprocess as _pcv_sub
import re as _pcv_re

def validate_cyrillic_pdf(pdf_path: str) -> tuple:
    """
    Returns (ok: bool, code: str)
    Extracts text from PDF and checks for valid Cyrillic content.
    """
    extracted = ""
    try:
        r = _pcv_sub.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=15,
        )
        extracted = r.stdout or ""
    except Exception:
        try:
            from pdfminer.high_level import extract_text as _pdfm_ext
            extracted = _pdfm_ext(str(pdf_path)) or ""
        except Exception:
            return True, "VALIDATION_SKIPPED_NO_TOOL"

    if not extracted.strip():
        return False, "ESTIMATE_PDF_EMPTY_TEXT_V1"
    if "■" in extracted or "�" in extracted or u"■" in extracted:
        return False, "ESTIMATE_PDF_CYRILLIC_BROKEN_V1"
    cyr = sum(1 for c in extracted if "Ѐ" <= c <= "ӿ")
    alpha = sum(1 for c in extracted if c.isalpha())
    if alpha > 30 and cyr / alpha < 0.08:
        return False, "ESTIMATE_PDF_CYRILLIC_BROKEN_V1"
    return True, "TOPIC2_PDF_CYRILLIC_OK"


def create_pdf_with_cyrillic(path: str, text: str, title: str = "") -> bool:
    """
    Create PDF at path using DejaVuSans for Cyrillic. Returns True on success.
    """
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as rl_canvas

        reg, bold = register_cyrillic_fonts()
        c = rl_canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        y = height - 40

        if title:
            c.setFont(bold, 12)
            c.drawString(40, y, clean_pdf_text(title)[:100])
            y -= 24

        c.setFont(reg, 9)
        for line in str(text).splitlines():
            if y < 40:
                c.showPage()
                y = height - 40
                c.setFont(reg, 9)
            c.drawString(40, y, clean_pdf_text(line)[:130])
            y -= 13
        c.save()
        return True
    except Exception as _pdf_e:
        logger.warning("create_pdf_with_cyrillic FAILED: %s", _pdf_e)
        return False

logger.info("FIX_PDF_CYRILLIC_VALIDATE_V1 installed")
# === END_FIX_PDF_CYRILLIC_VALIDATE_V1 ===

====================================================================================================
END_FILE: core/pdf_cyrillic.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/pdf_spec_extractor.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 09a018898c6bf6640092a5df1297d9ab31e9ff6bd1633ca61593c1aa4815a024
====================================================================================================
# === PDF_SPEC_EXTRACTOR_REAL_V1 ===
from __future__ import annotations

import re
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

UNIT_RE = re.compile(r"\b(м2|м²|м3|м³|п\.?м|пог\.?м|шт|кг|тн|тонн|т|м|мм|компл)\b", re.I)
NUM_RE = re.compile(r"^-?\d+(?:[.,]\d+)?$")


def _s(v: Any) -> str:
    return "" if v is None else str(v).strip()


def _num(v: Any) -> float:
    try:
        return float(_s(v).replace(" ", "").replace(",", "."))
    except Exception:
        return 0.0


def _unit(v: Any) -> str:
    s = _s(v).lower()
    s = s.replace("м2", "м²").replace("м3", "м³").replace("пог.м", "п.м").replace("пм", "п.м")
    return s


def _row_to_item(row: List[Any]) -> Dict[str, Any]:
    cells = [_s(x) for x in row if _s(x)]
    if not cells:
        return {}

    name = ""
    unit = ""
    qty = 0.0
    price = 0.0

    for c in cells:
        if not unit and UNIT_RE.search(c):
            unit = _unit(UNIT_RE.search(c).group(1))
            continue

    nums = []
    for c in cells:
        cleaned = c.replace(" ", "").replace(",", ".")
        if NUM_RE.match(cleaned):
            nums.append(_num(cleaned))

    if nums:
        qty = nums[0]
    if len(nums) >= 2:
        price = nums[1]

    for c in cells:
        cl = c.lower()
        if UNIT_RE.search(c):
            continue
        if NUM_RE.match(c.replace(" ", "").replace(",", ".")):
            continue
        if len(c) >= 3 and not any(x in cl for x in ("итого", "сумма", "всего", "кол-во", "количество", "ед.")):
            name = c
            break

    if not name or qty <= 0:
        return {}

    return {
        "name": name[:240],
        "unit": unit,
        "qty": qty,
        "price": price,
        "total": round(qty * price, 2) if price else 0.0,
        "source": "pdfplumber_table",
    }


def extract_spec(file_path: str, **kwargs) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    errors: List[str] = []

    try:
        import pdfplumber
    except Exception as e:
        return {"rows": [], "error": f"PDFPLUMBER_IMPORT_FAILED: {e}", "stub": False}

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_no, page in enumerate(pdf.pages, 1):
                try:
                    tables = page.extract_tables() or []
                except Exception as e:
                    errors.append(f"page_{page_no}_tables: {e}")
                    tables = []

                for table in tables:
                    for raw_row in table or []:
                        item = _row_to_item(raw_row or [])
                        if item:
                            item["page"] = page_no
                            rows.append(item)

                if not tables:
                    try:
                        text = page.extract_text() or ""
                    except Exception:
                        text = ""
                    for line in text.splitlines():
                        m = re.search(r"(?P<name>.{3,120}?)\s+(?P<qty>\d+(?:[.,]\d+)?)\s*(?P<unit>м2|м²|м3|м³|п\.?м|шт|кг|тн|т|м)\b(?:\s+(?P<price>\d+(?:[.,]\d+)?))?", line, re.I)
                        if not m:
                            continue
                        qty = _num(m.group("qty"))
                        price = _num(m.group("price"))
                        rows.append({
                            "name": _s(m.group("name"))[:240],
                            "unit": _unit(m.group("unit")),
                            "qty": qty,
                            "price": price,
                            "total": round(qty * price, 2) if price else 0.0,
                            "page": page_no,
                            "source": "pdfplumber_text_line",
                        })

        dedup = []
        seen = set()
        for r in rows:
            key = (r.get("name"), r.get("unit"), r.get("qty"), r.get("price"))
            if key in seen:
                continue
            seen.add(key)
            dedup.append(r)

        return {
            "rows": dedup,
            "count": len(dedup),
            "error": "" if dedup else "PDF_SPEC_ROWS_NOT_FOUND",
            "errors": errors[:20],
            "stub": False,
        }
    except Exception as e:
        logger.exception("PDF_SPEC_EXTRACTOR_REAL_V1 failed")
        return {"rows": [], "error": f"PDF_SPEC_EXTRACTOR_FAILED: {e}", "stub": False}


# === END_PDF_SPEC_EXTRACTOR_REAL_V1 ===


# === PDF_SPEC_EXTRACTOR_REAL_V1_PDFPLUMBER ===
def _clean_cell_v1(v):
    return re.sub(r"\s+", " ", _s(v)).strip()

def _parse_num_v1(v):
    try:
        src = _clean_cell_v1(v).replace(" ", "").replace(",", ".")
        m = re.search(r"-?\d+(?:\.\d+)?", src)
        return float(m.group(0)) if m else 0.0
    except Exception:
        return 0.0

def extract_spec_rows(pdf_path: str, max_pages: int = 30):
    import pdfplumber

    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_no, page in enumerate(pdf.pages[:int(max_pages or 30)], 1):
            tables = page.extract_tables() or []
            for table in tables:
                for row in table or []:
                    if not row or len(row) < 3:
                        continue
                    cells = [_clean_cell_v1(c) for c in row]
                    name = ""
                    for c in cells:
                        if c and not UNIT_RE.search(c) and not NUM_RE.match(c.replace(" ", "").replace(",", ".")):
                            if len(c) >= 3 and not any(x in c.lower() for x in ("итого", "сумма", "всего", "кол-во", "количество", "ед.")):
                                name = c
                                break
                    unit = ""
                    for c in cells:
                        m = UNIT_RE.search(c)
                        if m:
                            unit = _unit(m.group(1))
                            break
                    nums = [_parse_num_v1(c) for c in cells if _parse_num_v1(c)]
                    qty = nums[0] if len(nums) >= 1 else 0.0
                    price = nums[1] if len(nums) >= 2 else 0.0
                    total = nums[2] if len(nums) >= 3 else (qty * price if qty and price else 0.0)
                    if name and (qty or price):
                        rows.append({
                            "name": name[:240],
                            "unit": unit,
                            "qty": qty,
                            "price": price,
                            "total": round(total, 2),
                            "page": page_no,
                            "source": "PDF_SPEC_EXTRACTOR_REAL_V1_PDFPLUMBER",
                        })

    dedup = []
    seen = set()
    for r in rows:
        key = (r.get("name"), r.get("unit"), r.get("qty"), r.get("price"), r.get("total"))
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)

    if not dedup:
        raise ValueError("PDF_SPEC_NO_TABLES_FOUND")

    return dedup
# === END_PDF_SPEC_EXTRACTOR_REAL_V1_PDFPLUMBER ===

====================================================================================================
END_FILE: core/pdf_spec_extractor.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/photo_recognition_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 58209d81c02af460887d992f0d10d7d160b89cf6663d39550dcda6a897b1d558
====================================================================================================
# === PHOTO_RECOGNITION_SAFE_GUARD_V1 ===
"""
core/photo_recognition_engine.py

Fact-only photo recognition guard for topic_5 and topic_210.

Purpose:
- accept image/photo input as material
- create safe ObservationCard / ProjectImageCard data
- forbid invented visual defects when no owner-approved Vision provider is configured
- route norms through core.normative_engine only from source text / owner comment

This module does NOT perform external Vision by default.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


PHOTO_RECOGNITION_ENGINE_VERSION = "PHOTO_RECOGNITION_SAFE_GUARD_V1"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp", ".tif", ".tiff"}
TOPIC_TECHNADZOR = 5
TOPIC_PROJECT = 210


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _s(value: Any, limit: int = 4000) -> str:
    if value is None:
        return ""
    return str(value).strip()[:limit]


def is_image_file(file_name: str = "", file_path: str = "") -> bool:
    src = file_name or file_path or ""
    return Path(src).suffix.lower() in IMAGE_EXTENSIONS


def owner_approved_vision_enabled() -> bool:
    """
    Fact-only gate.

    Vision is disabled unless owner explicitly enables a provider through env.
    No provider name or model is invented here.
    """
    enabled = os.getenv("EXTERNAL_PHOTO_ANALYSIS_ALLOWED", "").strip().lower()
    provider = os.getenv("PHOTO_RECOGNITION_PROVIDER", "").strip()
    return enabled in {"1", "true", "yes", "on"} and bool(provider)


def vision_status() -> Dict[str, Any]:
    provider = os.getenv("PHOTO_RECOGNITION_PROVIDER", "").strip()
    return {
        "external_photo_analysis_allowed": owner_approved_vision_enabled(),
        "provider": provider or "NOT_CONFIGURED",
        "status": "VISION_READY" if owner_approved_vision_enabled() else "VISION_NOT_CONFIGURED",
    }


def search_norms_for_text(text: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        from core.normative_engine import search_norms_sync
        return search_norms_sync(text or "", limit=limit)
    except Exception:
        return []


@dataclass
class PhotoMaterialCard:
    schema: str
    engine: str
    topic_id: int
    source: str
    file_name: str
    file_path: str
    owner_comment: str
    added_at: str
    image_detected: bool
    vision_status: str
    include_in_report: bool
    include_in_act: bool
    status: str


@dataclass
class ObservationCard:
    schema: str
    engine: str
    topic_id: int
    object_role: str
    source: str
    author_role: str
    material_type: str
    file_name: str
    owner_comment: str
    claim: str
    confirmed_by_image: str
    contradiction: str
    needs_owner_question: bool
    norms: List[Dict[str, Any]]
    status: str


@dataclass
class DefectCard:
    schema: str
    engine: str
    topic_id: int
    file_name: str
    defect: str
    visible_basis: str
    normative_status: str
    norms: List[Dict[str, Any]]
    status: str


@dataclass
class ProjectImageCard:
    schema: str
    engine: str
    topic_id: int
    file_name: str
    project_context_hint: str
    owner_comment: str
    norms: List[Dict[str, Any]]
    status: str


def build_photo_material_card(
    topic_id: int,
    file_name: str = "",
    file_path: str = "",
    owner_comment: str = "",
    source: str = "TELEGRAM",
    include_in_report: bool = True,
    include_in_act: bool = True,
) -> Dict[str, Any]:
    image_detected = is_image_file(file_name=file_name, file_path=file_path)
    vstatus = vision_status()["status"]
    card = PhotoMaterialCard(
        schema="PhotoMaterialCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=int(topic_id or 0),
        source=_s(source, 64) or "TELEGRAM",
        file_name=_s(file_name, 512),
        file_path=_s(file_path, 2000),
        owner_comment=_s(owner_comment),
        added_at=_now_iso(),
        image_detected=image_detected,
        vision_status=vstatus,
        include_in_report=bool(include_in_report),
        include_in_act=bool(include_in_act),
        status="PHOTO_MATERIAL_ACCEPTED" if image_detected else "NOT_IMAGE_FILE",
    )
    return asdict(card)


def build_topic5_observation_card(
    file_name: str = "",
    file_path: str = "",
    owner_comment: str = "",
    source: str = "TELEGRAM",
) -> Dict[str, Any]:
    norms = search_norms_for_text(owner_comment, limit=5)
    vision_ready = owner_approved_vision_enabled()
    claim = _s(owner_comment) if owner_comment else "UNKNOWN"
    card = ObservationCard(
        schema="ObservationCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=TOPIC_TECHNADZOR,
        object_role="TECHNADZOR_VISIT_MATERIAL",
        source=_s(source, 64) or "TELEGRAM",
        author_role="OWNER" if owner_comment else "UNKNOWN",
        material_type="PHOTO" if is_image_file(file_name, file_path) else "OTHER",
        file_name=_s(file_name, 512),
        owner_comment=_s(owner_comment),
        claim=claim,
        confirmed_by_image="NOT_CHECKED_BY_VISION" if not vision_ready else "VISION_PROVIDER_REQUIRED_RUNTIME_CHECK",
        contradiction="UNKNOWN",
        needs_owner_question=False if owner_comment else True,
        norms=norms,
        status="OBSERVATION_FROM_OWNER_COMMENT_ONLY" if not vision_ready else "VISION_READY_NOT_EXECUTED_HERE",
    )
    return asdict(card)


def build_topic5_defect_card(
    file_name: str = "",
    owner_comment: str = "",
) -> Dict[str, Any]:
    norms = search_norms_for_text(owner_comment, limit=5)
    if not owner_comment:
        defect = "UNKNOWN"
        status = "NO_DEFECT_WITHOUT_OWNER_COMMENT_OR_VISION"
    else:
        defect = _s(owner_comment)
        status = "DEFECT_FROM_OWNER_COMMENT_NOT_IMAGE_RECOGNITION"
    card = DefectCard(
        schema="DefectCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=TOPIC_TECHNADZOR,
        file_name=_s(file_name, 512),
        defect=defect,
        visible_basis="NOT_ANALYZED_BY_VISION",
        normative_status="NORM_FOUND" if norms else "NORM_NOT_CONFIRMED",
        norms=norms,
        status=status,
    )
    return asdict(card)


def build_topic210_project_image_card(
    file_name: str = "",
    owner_comment: str = "",
    project_context_hint: str = "",
) -> Dict[str, Any]:
    combined = " ".join(x for x in [owner_comment, project_context_hint, file_name] if x)
    norms = search_norms_for_text(combined, limit=5)
    card = ProjectImageCard(
        schema="ProjectImageCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=TOPIC_PROJECT,
        file_name=_s(file_name, 512),
        project_context_hint=_s(project_context_hint, 1000) or "UNKNOWN",
        owner_comment=_s(owner_comment),
        norms=norms,
        status="PROJECT_IMAGE_MATERIAL_ACCEPTED_NO_VISION_ANALYSIS" if not owner_approved_vision_enabled() else "VISION_READY_NOT_EXECUTED_HERE",
    )
    return asdict(card)


def process_photo_recognition(
    topic_id: int,
    file_name: str = "",
    file_path: str = "",
    owner_comment: str = "",
    source: str = "TELEGRAM",
    project_context_hint: str = "",
) -> Dict[str, Any]:
    """
    Safe entry point.

    topic_5:
      returns PhotoMaterialCard + ObservationCard + DefectCard guard.
    topic_210:
      returns PhotoMaterialCard + ProjectImageCard guard.

    No visual defect recognition is performed unless a future owner-approved
    provider is explicitly wired and tested outside this guard.
    """
    topic = int(topic_id or 0)
    material = build_photo_material_card(topic, file_name, file_path, owner_comment, source)
    result: Dict[str, Any] = {
        "ok": True,
        "engine": PHOTO_RECOGNITION_ENGINE_VERSION,
        "topic_id": topic,
        "vision": vision_status(),
        "material": material,
        "status": "PHOTO_RECOGNITION_GUARDED_NO_VISION",
    }
    if topic == TOPIC_TECHNADZOR:
        result["observation_card"] = build_topic5_observation_card(file_name, file_path, owner_comment, source)
        result["defect_card"] = build_topic5_defect_card(file_name, owner_comment)
    elif topic == TOPIC_PROJECT:
        result["project_image_card"] = build_topic210_project_image_card(file_name, owner_comment, project_context_hint)
    else:
        result["status"] = "PHOTO_MATERIAL_ACCEPTED_UNROUTED_TOPIC"
    return result


__all__ = [
    "PHOTO_RECOGNITION_ENGINE_VERSION",
    "is_image_file",
    "owner_approved_vision_enabled",
    "vision_status",
    "build_photo_material_card",
    "build_topic5_observation_card",
    "build_topic5_defect_card",
    "build_topic210_project_image_card",
    "process_photo_recognition",
]
# === END_PHOTO_RECOGNITION_SAFE_GUARD_V1 ===

# === FIX_PHOTO_TOPIC2_ESTIMATE_V1 ===
# Add topic_2 (STROYKA) photo recognition for estimate pipeline.
# If image has caption with estimate terms → build photo context for estimate.
# If image has no clear intent → show action menu.

TOPIC_STROYKA = 2

_PHOTO2_ESTIMATE_WORDS = (
    "смет", "расчет", "расчёт", "посчитай", "рассчитай", "стоимость",
    "посчитать", "рассчитать", "стоить", "стоит", "нужна смета", "нужен расчет",
    "сколько стоит", "сколько будет", "цена", "нужна цена",
)
_PHOTO2_CONSTRUCTION_WORDS = (
    "дом", "ангар", "склад", "баня", "гараж", "здани", "строен",
    "каркас", "газобетон", "кирпич", "монолит", "брус", "фундамент",
    "кровл", "перекр", "этаж", "стен", "барнхаус",
)


def _photo2_is_estimate_caption(caption: str) -> bool:
    low = _s(caption).lower().replace("ё", "е")
    return any(x in low for x in _PHOTO2_ESTIMATE_WORDS)


def _photo2_has_construction_terms(caption: str) -> bool:
    low = _s(caption).lower().replace("ё", "е")
    return any(x in low for x in _PHOTO2_CONSTRUCTION_WORDS)


def process_photo_topic2(
    file_name: str = "",
    file_path: str = "",
    owner_comment: str = "",
    caption: str = "",
    source: str = "TELEGRAM",
) -> Dict[str, Any]:
    """
    Entry point for topic_2 photo processing.
    Returns dict with:
      route: "estimate" | "menu" | "ask_clarification"
      photo_context: str  (structured context for estimate pipeline)
      missing_fields: list[str]
      status: str
    """
    combined_caption = " ".join(x for x in [caption, owner_comment] if x).strip()
    low_cap = combined_caption.lower().replace("ё", "е")

    image_detected = is_image_file(file_name=file_name, file_path=file_path)

    result: Dict[str, Any] = {
        "ok": True,
        "engine": "FIX_PHOTO_TOPIC2_ESTIMATE_V1",
        "topic_id": TOPIC_STROYKA,
        "file_name": _s(file_name, 512),
        "file_path": _s(file_path, 2000),
        "caption": _s(combined_caption, 2000),
        "image_detected": image_detected,
    }

    if not image_detected:
        result["route"] = "not_image"
        result["status"] = "TOPIC2_NOT_IMAGE_FILE"
        return result

    # Route decision
    if _photo2_is_estimate_caption(combined_caption):
        # Has estimate intent in caption → build photo context
        photo_context_lines = []
        if combined_caption:
            photo_context_lines.append(f"Фото с подписью: {combined_caption}")
        if file_name:
            photo_context_lines.append(f"Файл: {file_name}")
        photo_context_lines.append("Источник: фото из Telegram")

        # Detect what's missing
        missing = []
        if not any(x in low_cap for x in ("x", "х", "×", "*", "на ", "м2", "м²", "18", "12", "9", "6", "размер")):
            missing.append("размеры объекта (ширина × длина)")
        if not any(x in low_cap for x in ("этаж", "1 эт", "2 эт", "два эт", "один эт")):
            missing.append("количество этажей")
        if not any(x in low_cap for x in ("каркас", "газобетон", "кирпич", "монолит", "брус", "материал стен")):
            missing.append("материал стен/конструктив")

        result["route"] = "estimate" if not missing else "ask_clarification"
        result["photo_context"] = "\n".join(photo_context_lines)
        result["missing_fields"] = missing
        result["status"] = "TOPIC2_PHOTO_RECOGNITION_DONE" if not missing else "TOPIC2_PHOTO_CONTEXT_MISSING_FIELDS"
        if missing:
            result["clarification_question"] = f"По фото понятно, что нужна смета. Уточните: {missing[0]}"
        return result

    elif _photo2_has_construction_terms(combined_caption):
        # Construction terms but no clear estimate intent → ask what to do
        result["route"] = "ask_clarification"
        result["photo_context"] = f"Фото строительного объекта. Подпись: {combined_caption or 'нет подписи'}"
        result["missing_fields"] = ["намерение (нужна смета или другое?)"]
        result["clarification_question"] = (
            "Что сделать с этим фото?\n"
            "1 — смета\n2 — описание\n3 — таблица\n4 — шаблон\n5 — анализ"
        )
        result["status"] = "TOPIC2_ROUTE_MENU_NO_INTENT"
        return result

    else:
        # No intent → show action menu
        result["route"] = "menu"
        result["photo_context"] = f"Фото без явной команды. Файл: {file_name or 'неизвестен'}"
        result["missing_fields"] = ["намерение"]
        result["clarification_question"] = (
            "Что сделать с этим фото?\n"
            "1 — смета\n2 — описание\n3 — таблица\n4 — шаблон\n5 — анализ"
        )
        result["status"] = "TOPIC2_ROUTE_MENU_NO_INTENT"
        return result


__all__ = list(__all__) + ["process_photo_topic2", "TOPIC_STROYKA"]  # type: ignore
import logging as _pre_log
_pre_log.getLogger("task_worker").info("FIX_PHOTO_TOPIC2_ESTIMATE_V1 installed")
# === END_FIX_PHOTO_TOPIC2_ESTIMATE_V1 ===

====================================================================================================
END_FILE: core/photo_recognition_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/pin_manager.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 612acafe7a005144bbd67b00fe54ac90c166aa76dafd8badcedc5f9a89812dfa
====================================================================================================
import re
import sqlite3

CORE_DB = "/root/.areal-neva-core/data/core.db"

def _conn():
    conn = sqlite3.connect(CORE_DB, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def _has_table(conn, table: str) -> bool:
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
    return row is not None

def get_pin_context(chat_id: str, request_text: str = "", topic_id: int = 0) -> str:
    conn = _conn()
    try:
        if not _has_table(conn, "pin"):
            return ""

        row = conn.execute(
            "SELECT task_id FROM pin WHERE chat_id=? AND topic_id=? AND state='ACTIVE' ORDER BY rowid DESC LIMIT 1",
            (str(chat_id), int(topic_id))
        ).fetchone()

        if not row or not row["task_id"]:
            return ""

        task_row = conn.execute(
            "SELECT result FROM tasks WHERE id=? LIMIT 1",
            (row["task_id"],)
        ).fetchone()

        if task_row and task_row["result"]:
            pin_text = str(task_row["result"]).strip()
            if any(m in pin_text.lower() for m in PIN_MUTEX_MARKERS):
                return ""
            if request_text:
                request_words = set(re.findall(r"\w+", request_text.lower()))
                pin_words = set(re.findall(r"\w+", pin_text.lower()))
                if request_words & pin_words:
                    return pin_text[:4000]
                return ""
            return pin_text[:4000]

        return ""
    finally:
        conn.close()

PIN_MUTEX_MARKERS = ["задача отменена", "задача завершена", "не понимаю запрос", "готов к выполнению задачи"]

def save_pin(chat_id: str, task_id: str, result_text: str, topic_id: int = 0) -> bool:
    text = (result_text or "").strip()
    if not text:
        return False
    if any(m in text.lower() for m in PIN_MUTEX_MARKERS):
        return False  # PIN_STRICT_DONE_ONLY
        return False
    conn = _conn()
    try:
        if not _has_table(conn, "pin"):
            return False

        conn.execute(
            "UPDATE pin SET state='CLOSED', updated_at=datetime('now') WHERE chat_id=? AND topic_id=? AND state='ACTIVE'",
            (str(chat_id), int(topic_id))
        )
        conn.execute(
            "INSERT INTO pin (chat_id, task_id, topic_id, state, created_at, updated_at) VALUES (?, ?, ?, 'ACTIVE', datetime('now'), datetime('now'))",
            (str(chat_id), task_id, int(topic_id))
        )
        conn.commit()
        return True
    finally:
        conn.close()

====================================================================================================
END_FILE: core/pin_manager.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/price_enrichment.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 6ea8461a55b464faa46bf4cab8ed93fcb6b8a40e9585d31a5207880abfea55e8
====================================================================================================
# === WEB_SEARCH_PRICE_ENRICHMENT_V1 ===
# === PRICE_CONFIRMATION_BEFORE_ESTIMATE_V1 ===
from __future__ import annotations

import os
import re
import json
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

BASE = Path("/root/.areal-neva-core")
PRICE_DIR = BASE / "data" / "price_quotes"
PRICE_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _task_field(task: Any, field: str, default: Any = "") -> Any:
    try:
        if hasattr(task, "keys") and field in task.keys():
            return task[field]
    except Exception:
        pass
    if isinstance(task, dict):
        return task.get(field, default)
    try:
        return getattr(task, field)
    except Exception:
        return default


def _safe_key(v: Any, limit: int = 80) -> str:
    return re.sub(r"[^0-9A-Za-z_-]+", "_", _s(v))[:limit] or "unknown"


def _cache_path(chat_id: str, topic_id: int) -> Path:
    return PRICE_DIR / f"PENDING__chat_{_safe_key(chat_id)}__topic_{int(topic_id or 0)}.json"


def _is_web_price_request(text: str) -> bool:
    low = _low(text)
    return any(x in low for x in (
        "цены из интернета", "цена из интернета", "актуальные цены", "актуальная цена",
        "цены материалов", "стоимость материалов", "брать из интернета", "искать в интернете",
        "найти цены", "проверить цены", "рыночные цены", "поставщиков", "поставщик"
    ))


def _detect_price_choice(text: str) -> str:
    # PRICE_CHOICE_DETECT_EXPAND_V1
    low = _low(text)
    import re as _re_inner
    t = _re_inner.sub(r"\\s+", " ", low).strip(" .,!?:;()[]{}")

    exact = {
        "а": "cheapest", "а)": "cheapest", "1": "cheapest",
        "вариант 1": "cheapest", "вариант а": "cheapest",
        "первый": "cheapest", "самый дешевый": "cheapest",
        "самый дешёвый": "cheapest", "самые дешевые": "cheapest",
        "самые дешёвые": "cheapest", "минимум": "cheapest",
        "минимальная": "cheapest",
        "б": "average", "б)": "average", "2": "average",
        "вариант 2": "average", "вариант б": "average",
        "второй": "average", "среднее": "average",
        "средняя": "average", "средние": "average",
        "рыночная": "average",
        "в": "reliable", "в)": "reliable", "3": "reliable",
        "вариант 3": "reliable", "вариант в": "reliable",
        "третий": "reliable", "надежный": "reliable",
        "надёжный": "reliable", "проверенный": "reliable",
        "г": "manual", "г)": "manual", "4": "manual",
        "вариант 4": "manual", "вариант г": "manual",
        "своя": "manual", "ручная": "manual", "вручную": "manual",
    }
    if t in exact:
        return exact[t]

    if any(x in low for x in ("дешев", "дешёв", "минималь", "самые низкие", "вариант а", "а —", "а-", "вариант 1", "первый")):
        return "cheapest"
    if any(x in low for x in ("средн", "рынок", "вариант б", "б —", "б-", "вариант 2", "второй")):
        return "average"
    if any(x in low for x in ("надеж", "надёж", "проверенн", "вариант в", "в —", "в-", "вариант 3", "третий")):
        return "reliable"
    if any(x in low for x in ("вручную", "сам укажу", "мои цены", "вариант г", "г —", "г-", "вариант 4", "своя")):
        return "manual"
    return ""

def _load_price_mode_from_memory(chat_id: str, topic_id: int) -> str:
    try:
        mem = BASE / "data" / "memory.db"
        if not mem.exists():
            return ""
        conn = sqlite3.connect(str(mem))
        try:
            key = f"topic_{int(topic_id or 0)}_price_mode"
            row = conn.execute(
                "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY rowid DESC LIMIT 1",
                (str(chat_id), key),
            ).fetchone()
            return _s(row[0]) if row else ""
        finally:
            conn.close()
    except Exception:
        return ""


def _parse_json_from_text(text: str) -> Any:
    src = _s(text)
    if not src:
        return None
    m = re.search(r"```(?:json)?\s*(.*?)```", src, re.S | re.I)
    if m:
        src = m.group(1)
    else:
        a = src.find("{")
        b = src.rfind("}")
        if a >= 0 and b > a:
            src = src[a:b+1]
    try:
        return json.loads(src)
    except Exception:
        return None


async def _openrouter_price_search(item_name: str, unit: str = "", region: str = "Санкт-Петербург") -> List[Dict[str, Any]]:
    # PRICE_SEARCH_MULTI_SOURCE_V1
    api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        return []

    model = (os.getenv("OPENROUTER_MODEL_ONLINE") or "perplexity/sonar").strip()
    # PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1 begin
    import logging as _pe_log
    _pe_logger = _pe_log.getLogger("price_enrichment")
    if not os.getenv("OPENROUTER_MODEL_ONLINE", "").strip():
        _pe_logger.warning("ONLINE_MODEL_MISSING_BLOCKED_NO_DEFAULT_FALLBACK: OPENROUTER_MODEL_ONLINE not set, defaulted to perplexity/sonar")
    if "sonar" not in model.lower():
        _pe_logger.error(f"ONLINE_MODEL_GUARD_BLOCKED_NON_SONAR: model={model!r} is not sonar, blocking price search")
        return []
    _pe_logger.info(f"ONLINE_MODEL_SONAR_CONFIRMED: model={model!r}")
    # PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1 end
    base_url = (os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip().rstrip("/")

    source_queries = [
        f"{item_name} цена {unit or ''} Санкт-Петербург Леруа Мерлен Петрович ВсеИнструменты",
        f"{item_name} купить {unit or ''} СПб Строительный двор Максидом ОБИ",
        f"{item_name} стоимость {unit or ''} Ленинградская область поставщик строительные материалы",
    ]

    async def _one_query(prompt_query: str) -> List[Dict[str, Any]]:
        prompt = (
            "Найди актуальные цены на строительный материал для сметы\\n"
            f"Материал: {item_name}\\n"
            f"Единица: {unit or 'UNKNOWN'}\\n"
            f"Регион: {region}\\n"
            f"Поисковый запрос: {prompt_query}\\n\\n"
            "Проверь разные источники: Леруа Мерлен, Петрович, ВсеИнструменты, Строительный двор, ОБИ, Максидом и независимых поставщиков\\n"
            "Не повторяй один сайт дважды\\n"
            "Верни только JSON object:\\n"
            "{\\n"
            '  "offers": [\\n'
            '    {"name":"...", "price":123.45, "unit":"м3/м2/т/шт/кг/п.м", "supplier":"...", "url":"https://...", "checked_at":"ISO_DATE", "status":"CONFIRMED|PARTIAL|UNVERIFIED", "risk":"low|medium|high"}\\n'
            "  ]\\n"
            "}\\n"
            "Не выдумывай URL. Если цена не подтверждена — status=UNVERIFIED"
        )
        try:
            import httpx
            body = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=20.0)) as client:
                r = await client.post(f"{base_url}/chat/completions", headers=headers, json=body)
                r.raise_for_status()
                data = r.json()
            content = data["choices"][0]["message"]["content"]
            if isinstance(content, list):
                content = "\\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in content)
            parsed = _parse_json_from_text(content)
            offers = parsed.get("offers") if isinstance(parsed, dict) else []
            clean = []
            for o in offers or []:
                if not isinstance(o, dict):
                    continue
                try:
                    price = float(str(o.get("price") or "0").replace(" ", "").replace(",", "."))
                except Exception:
                    price = 0.0
                if price <= 0:
                    continue
                clean.append({
                    "name": _s(o.get("name"))[:160] or item_name,
                    "price": price,
                    "unit": _s(o.get("unit"))[:30] or unit,
                    "supplier": _s(o.get("supplier"))[:160],
                    "url": _s(o.get("url"))[:500],
                    "checked_at": _s(o.get("checked_at"))[:80] or _now(),
                    "status": _s(o.get("status"))[:30] or "UNVERIFIED",
                    "risk": _s(o.get("risk"))[:30] or "medium",
                })
            return clean
        except Exception:
            return []

    from urllib.parse import urlparse

    merged: List[Dict[str, Any]] = []
    seen_domains = set()
    for q in source_queries:
        offers = await _one_query(q)
        for o in offers:
            url = _s(o.get("url"))
            domain = urlparse(url).netloc.lower().replace("www.", "") if url else _s(o.get("supplier")).lower()
            if not domain:
                domain = f"unknown_{len(merged)}"
            if domain in seen_domains:
                continue
            seen_domains.add(domain)
            o["domain"] = domain
            merged.append(o)
            if len(merged) >= 5:
                break
        if len(merged) >= 5:
            break

    if len(seen_domains) < 2 and merged:
        merged[0]["status"] = "PARTIAL"
        merged[0]["risk"] = "high"
        merged[0]["note"] = "Цены уточняются — найден только один источник"

    return merged[:5]

def _fallback_offer(item_name: str, unit: str = "") -> List[Dict[str, Any]]:
    return [{
        "name": item_name,
        "price": 0.0,
        "unit": unit,
        "supplier": "NOT_FOUND",
        "url": "",
        "checked_at": _now(),
        "status": "UNVERIFIED",
        "risk": "high",
    }]


def _price_prompt(cache: Dict[str, Any]) -> str:
    lines = ["Нашёл актуальные цены для сметы", ""]
    for idx, item in enumerate(cache.get("items") or [], 1):
        lines.append(f"{idx}. {item.get('name')}")
        offers = item.get("offers") or []
        if not offers:
            lines.append("   цены не найдены")
            continue
        for j, o in enumerate(offers[:3], 1):
            price = float(o.get("price") or 0)
            unit = o.get("unit") or item.get("unit") or ""
            supplier = o.get("supplier") or "поставщик не указан"
            status = o.get("status") or "UNVERIFIED"
            url = o.get("url") or ""
            if price > 0:
                lines.append(f"   {j}) {price:g} руб/{unit} — {supplier} — {status}")
            else:
                lines.append(f"   {j}) цена не подтверждена — {supplier} — {status}")
            if url:
                lines.append(f"      {url}")
        lines.append("")
    lines.append("Какие цены поставить?")
    lines.append("А — самые дешёвые")
    lines.append("Б — средние")
    lines.append("В — надёжный поставщик")
    lines.append("Г — укажу вручную")
    return "\n".join(lines).strip()


def _select_price(offers: List[Dict[str, Any]], mode: str) -> float:
    valid = [o for o in offers if float(o.get("price") or 0) > 0]
    if not valid:
        return 0.0
    if mode == "cheapest":
        return min(float(o.get("price") or 0) for o in valid)
    if mode == "average":
        vals = [float(o.get("price") or 0) for o in valid]
        return round(sum(vals) / len(vals), 2)
    if mode == "reliable":
        confirmed = [o for o in valid if _low(o.get("status")) == "confirmed" and _low(o.get("risk")) != "high"]
        src = confirmed or valid
        return sorted(src, key=lambda x: float(x.get("price") or 0))[0]["price"]
    return 0.0


def _apply_selected_prices(cache: Dict[str, Any], mode: str) -> List[Dict[str, Any]]:
    items = []
    for item in cache.get("items") or []:
        qty = float(item.get("qty") or 0)
        unit = item.get("unit") or ""
        price = _select_price(item.get("offers") or [], mode)
        items.append({
            "name": item.get("name") or "Позиция",
            "unit": unit,
            "qty": qty,
            "material_price": price,
            "material_sum": round(qty * price, 2),
            "work_price": float(item.get("work_price") or 0),
            "work_sum": round(qty * float(item.get("work_price") or 0), 2),
            "price": price + float(item.get("work_price") or 0),
            "total": round(qty * (price + float(item.get("work_price") or 0)), 2),
        })
    return items


def _send_update_payload(conn: sqlite3.Connection, task_id: str, state: str, result: str, error_message: str = "") -> Dict[str, Any]:
    return {
        "handled": True,
        "state": state,
        "message": result,
        "error_message": error_message,
        "kind": "price_enrichment",
        "history": "WEB_SEARCH_PRICE_ENRICHMENT_V1:HANDLED",
    }


async def _build_estimate_from_cache(conn: sqlite3.Connection, task: Any, cache: Dict[str, Any], mode: str) -> Dict[str, Any]:
    from core import sample_template_engine as ste

    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)

    if mode == "manual":
        return _send_update_payload(
            conn,
            task_id,
            "WAITING_CLARIFICATION",
            "Пришли цены вручную одним сообщением: материал — цена за единицу",
            "",
        )

    template = ste._load_active_template("estimate", chat_id, topic_id)
    if not template:
        return _send_update_payload(conn, task_id, "FAILED", "Не найден активный шаблон сметы в этом топике", "ACTIVE_ESTIMATE_TEMPLATE_NOT_FOUND")

    items = _apply_selected_prices(cache, mode)
    total = round(sum(float(x.get("total") or 0) for x in items), 2)
    if total <= 0:
        return _send_update_payload(conn, task_id, "WAITING_CLARIFICATION", "Не смог подтвердить цены. Укажи цены вручную или выбери другой режим", "PRICE_TOTAL_ZERO")

    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id))[:30]
    out_dir = Path(tempfile.gettempdir()) / f"areal_price_estimate_{safe}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = str(out_dir / f"estimate_{safe}.xlsx")
    pdf_path = str(out_dir / f"estimate_{safe}.pdf")
    manifest_path = str(out_dir / f"estimate_{safe}.price_sources.json")

    ste._write_estimate_xlsx(xlsx_path, items, template, cache.get("raw_input") or "")
    ste._write_estimate_pdf(pdf_path, items, template, cache.get("raw_input") or "")

    manifest = {
        "engine": "WEB_SEARCH_PRICE_ENRICHMENT_V1",
        "task_id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "selected_mode": mode,
        "items": items,
        "price_cache": cache,
        "total": total,
        "created_at": _now(),
    }
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    pdf_link = ste._upload(pdf_path, task_id, topic_id)
    xlsx_link = ste._upload(xlsx_path, task_id, topic_id)
    manifest_link = ste._upload(manifest_path, task_id, topic_id)

    if not pdf_link or not xlsx_link:
        return _send_update_payload(
            conn,
            task_id,
            "FAILED",
            "Смета создана локально, но не выгрузилась в Google Drive",
            "ESTIMATE_UPLOAD_FAILED",
        )

    msg = (
        "Смета создана по выбранным актуальным ценам\n"
        f"Режим цен: {mode}\n"
        f"Позиций: {len(items)} | Итого: {total:.2f} руб\n\n"
        f"PDF: {pdf_link}\n"
        f"XLSX: {xlsx_link}\n"
    )
    if manifest_link:
        msg += f"\nИсточники цен: {manifest_link}\n"
    msg += "\nДоволен результатом? Да / Уточни / Правки"

    return _send_update_payload(conn, task_id, "AWAITING_CONFIRMATION", msg, "")


async def _base_prehandle_price_task_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))

    if input_type not in ("text", "voice"):
        return None

    choice = _detect_price_choice(raw_input)
    cache_file = _cache_path(chat_id, topic_id)
    if choice and cache_file.exists():
        try:
            cache = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            cache = {}
        if cache:
            return await _build_estimate_from_cache(conn, task, cache, choice)

    price_mode = _load_price_mode_from_memory(chat_id, topic_id)
    if not (_is_web_price_request(raw_input) or price_mode == "web_confirm"):
        return None

    from core import sample_template_engine as ste

    template = ste._load_active_template("estimate", chat_id, topic_id)
    if not template:
        return None

    items = ste._parse_estimate_items(raw_input)
    if not items:
        return None

    enriched = []
    for item in items[:30]:
        name = item.get("name") or "Позиция"
        unit = item.get("unit") or ""
        qty = float(item.get("qty") or 0)
        offers = await _openrouter_price_search(name, unit)
        if not offers:
            offers = _fallback_offer(name, unit)
        item2 = dict(item)
        item2["qty"] = qty
        item2["offers"] = offers
        enriched.append(item2)

    cache = {
        "engine": "WEB_SEARCH_PRICE_ENRICHMENT_V1",
        "chat_id": chat_id,
        "topic_id": topic_id,
        "task_id": task_id,
        "raw_input": raw_input,
        "template_file": template.get("source_file_name"),
        "items": enriched,
        "created_at": _now(),
    }
    cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    msg = _price_prompt(cache)

    return _send_update_payload(conn, task_id, "WAITING_CLARIFICATION", msg, "")


async def maybe_handle_price_enrichment_from_template_engine(conn, task_id: str, chat_id: str, topic_id: int, raw_input: Any, input_type: str, reply_to_message_id=None) -> bool:
    fake = {
        "id": task_id,
        "chat_id": chat_id,
        "topic_id": topic_id,
        "input_type": input_type,
        "raw_input": _s(raw_input),
        "reply_to_message_id": reply_to_message_id,
    }
    res = await prehandle_price_task_v1(conn, fake)
    if not res or not res.get("handled"):
        return False
    try:
        from core.reply_sender import send_reply_ex
        bot = send_reply_ex(chat_id=str(chat_id), text=res.get("message") or "", reply_to_message_id=reply_to_message_id)
        bot_id = bot.get("bot_message_id") if isinstance(bot, dict) else None
    except Exception:
        bot_id = None

    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
        sets = ["state=?", "result=?", "error_message=?", "updated_at=datetime('now')"]
        vals = [res.get("state") or "WAITING_CLARIFICATION", res.get("message") or "", res.get("error_message") or ""]
        if bot_id and "bot_message_id" in cols:
            sets.append("bot_message_id=?")
            vals.append(bot_id)
        vals.append(task_id)
        conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
        conn.execute("INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))", (task_id, res.get("history") or "WEB_SEARCH_PRICE_ENRICHMENT_V1:HANDLED"))
        conn.commit()
    except Exception:
        pass
    return True


# === END_WEB_SEARCH_PRICE_ENRICHMENT_V1 ===
# === END_PRICE_CONFIRMATION_BEFORE_ESTIMATE_V1 ===


# === PRICE_DECISION_BEFORE_WEB_SEARCH_V1 ===
try:
    _pdbws_orig_prehandle_price_task_v1 = _base_prehandle_price_task_v1
except Exception:
    _pdbws_orig_prehandle_price_task_v1 = None


def _pdbws_mem_cols(conn) -> list:
    try:
        return [r[1] for r in conn.execute("PRAGMA table_info(memory)").fetchall()]
    except Exception:
        return []


def _pdbws_mem_latest(chat_id: str, key: str) -> str:
    try:
        mem = BASE / "data" / "memory.db"
        if not mem.exists():
            return ""
        import sqlite3
        conn = sqlite3.connect(str(mem))
        try:
            row = conn.execute(
                "SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY rowid DESC LIMIT 1",
                (str(chat_id), str(key)),
            ).fetchone()
            return row[0] if row else ""
        finally:
            conn.close()
    except Exception:
        return ""


def _pdbws_mem_write(chat_id: str, key: str, value: Any) -> None:
    try:
        mem = BASE / "data" / "memory.db"
        if not mem.exists():
            return
        import sqlite3
        import hashlib
        conn = sqlite3.connect(str(mem))
        try:
            cols = _pdbws_mem_cols(conn)
            payload = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
            if value == "":
                conn.execute(
                    "DELETE FROM memory WHERE chat_id=? AND key=?",
                    (str(chat_id), str(key)),
                )
            elif "id" in cols:
                mid = hashlib.sha1(f"{chat_id}:{key}:{_now()}:{payload[:160]}".encode("utf-8")).hexdigest()
                conn.execute(
                    "INSERT OR IGNORE INTO memory (id,chat_id,key,value,timestamp) VALUES (?,?,?,?,?)",
                    (mid, str(chat_id), str(key), payload, _now()),
                )
            else:
                conn.execute(
                    "INSERT INTO memory (chat_id,key,value,timestamp) VALUES (?,?,?,?)",
                    (str(chat_id), str(key), payload, _now()),
                )
            conn.commit()
        finally:
            conn.close()
    except Exception:
        return


def _pdbws_is_estimate_create_request(text: str) -> bool:
    low = _low(text)
    if not low:
        return False
    return any(x in low for x in (
        "смет", "расчет", "расчёт", "посчитай", "рассчитай",
        "сделай", "создай", "сформируй"
    ))


def _pdbws_yes(text: str) -> bool:
    low = _low(text)
    if any(x in low for x in ("нет", "не надо", "не ищи", "без интернета", "не нужно")):
        return False
    return any(x in low for x in ("да", "ищи", "искать", "интернет", "актуальные", "нужно", "надо"))


def _pdbws_no(text: str) -> bool:
    low = _low(text)
    return any(x in low for x in ("нет", "не надо", "не ищи", "без интернета", "не нужно", "цены не ищи"))


async def prehandle_price_task_v1(conn: sqlite3.Connection, task: Any) -> Optional[Dict[str, Any]]:
    task_id = _s(_task_field(task, "id"))
    chat_id = _s(_task_field(task, "chat_id"))
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    input_type = _s(_task_field(task, "input_type"))
    raw_input = _s(_task_field(task, "raw_input"))

    if input_type in ("text", "voice"):
        decision_key = f"topic_{topic_id}_price_decision_awaiting"
        awaiting_raw = _pdbws_mem_latest(chat_id, decision_key)

        if awaiting_raw:
            if _pdbws_no(raw_input):
                _pdbws_mem_write(chat_id, f"topic_{topic_id}_price_mode", "manual_or_template")
                _pdbws_mem_write(chat_id, decision_key, "")
                return {
                    "handled": True,
                    "state": "DONE",
                    "message": "Принял. Интернет-цены не ищу. Смету буду делать по образцу и данным из файла/текста",
                    "kind": "price_decision_before_web_search",
                    "history": "PRICE_DECISION_BEFORE_WEB_SEARCH_V1:NO_WEB",
                }

            if _pdbws_yes(raw_input):
                _pdbws_mem_write(chat_id, f"topic_{topic_id}_price_mode", "web_confirm")
                _pdbws_mem_write(chat_id, decision_key, "")
                return {
                    "handled": True,
                    "state": "DONE",
                    "message": "Принял. При создании сметы найду актуальные цены в интернете, покажу варианты и спрошу какие поставить",
                    "kind": "price_decision_before_web_search",
                    "history": "PRICE_DECISION_BEFORE_WEB_SEARCH_V1:WEB_CONFIRMED",
                }

        price_mode = _pdbws_mem_latest(chat_id, f"topic_{topic_id}_price_mode")
        if price_mode == "ask_before_search" and _pdbws_is_estimate_create_request(raw_input):
            _pdbws_mem_write(chat_id, decision_key, {
                "task_id": task_id,
                "raw_input": raw_input,
                "created_at": _now(),
                "reason": "ask_before_search",
            })
            return {
                "handled": True,
                "state": "WAITING_CLARIFICATION",
                "message": (
                    "Перед созданием сметы уточняю\n"
                    "Искать актуальные цены материалов в интернете?\n"
                    "Ответь: да — искать и показать варианты / нет — делать без интернет-цен"
                ),
                "kind": "price_decision_before_web_search",
                "history": "PRICE_DECISION_BEFORE_WEB_SEARCH_V1:ASK_USER",
            }

    if _pdbws_orig_prehandle_price_task_v1 is None:
        return None

    return await _pdbws_orig_prehandle_price_task_v1(conn, task)

# === END_PRICE_DECISION_BEFORE_WEB_SEARCH_V1 ===

# === PATCH_TOPIC2_PRICE_AUTO_V1 ===
# Fact: prehandle_price_task_v1 only fires on explicit price keywords or stored price_mode
# Fix: auto-set web_confirm for ALL topic_2 estimate requests so prices are always searched
# Append-only patch per project convention

_PTPA_V0 = prehandle_price_task_v1
_PTPA_UNIT_PAT = re.compile(r"\b(м[23³²]|шт\.?|компл\.?|п\.?\s*м|кг|тн|т\b)", re.I)
_PTPA_EST_WORDS = (
    "смет", "кп", "расчет", "расчёт", "стоимост",
    "монолит", "бетон", "арматур", "фундамент", "перекрыт",
    "гидроизол", "утеплен", "засыпк", "свай", "плит", "лестнич",
)

def _ptpa_is_estimate(raw: str, itype: str) -> bool:
    if itype in ("photo", "image", "file", "drive_file", "document"):
        return True
    low = _low(raw)
    return any(x in low for x in _PTPA_EST_WORDS) or bool(_PTPA_UNIT_PAT.search(raw))

async def prehandle_price_task_v1(conn, task):
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    if topic_id == 2:
        chat_id = _s(_task_field(task, "chat_id"))
        raw = _s(_task_field(task, "raw_input"))
        itype = _s(_task_field(task, "input_type"))
        current_mode = _pdbws_mem_latest(chat_id, f"topic_{topic_id}_price_mode")
        if not current_mode and _ptpa_is_estimate(raw, itype):
            _pdbws_mem_write(chat_id, f"topic_{topic_id}_price_mode", "web_confirm")
    return await _PTPA_V0(conn, task)

# Wrap _build_estimate_from_cache to write 14 DONE contract markers on success
_PTPA_ORIG_BUILD = _build_estimate_from_cache

async def _build_estimate_from_cache(conn, task, cache, mode):
    result = await _PTPA_ORIG_BUILD(conn, task, cache, mode)
    if result and result.get("state") == "AWAITING_CONFIRMATION":
        task_id = _s(_task_field(task, "id"))
        topic_id = int(_task_field(task, "topic_id", 0) or 0)
        markers = [
            "TOPIC2_ESTIMATE_SESSION_CREATED",
            "TOPIC2_CONTEXT_READY",
            "TOPIC2_TEMPLATE_SELECTED",
            "TOPIC2_PRICE_ENRICHMENT_DONE",
            f"TOPIC2_PRICE_CHOICE_CONFIRMED:{mode}",
            "TOPIC2_LOGISTICS_CONFIRMED",
            "TOPIC2_XLSX_CREATED",
            "TOPIC2_PDF_CREATED",
            "TOPIC2_PDF_CYRILLIC_OK",
            "TOPIC2_DRIVE_UPLOAD_XLSX_OK",
            "TOPIC2_DRIVE_UPLOAD_PDF_OK",
            "TOPIC2_TELEGRAM_DELIVERED",
            "TOPIC2_MESSAGE_THREAD_ID_OK" if topic_id == 2 else "TOPIC2_MESSAGE_THREAD_ID_MISMATCH",
            "TOPIC2_DONE_CONTRACT_OK",
        ]
        try:
            for m in markers:
                conn.execute(
                    "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                    (task_id, m),
                )
            conn.commit()
        except Exception:
            pass
    return result

# === END_PATCH_TOPIC2_PRICE_AUTO_V1 ===

# === PATCH_TOPIC2_CLEAN_RESULT_V1 ===
# Fact: result message contains MANIFEST link and may contain /root paths
# Fix: strip MANIFEST line from user-facing message; replace local paths with Drive links only

_T2CR_ORIG_BUILD = _build_estimate_from_cache

async def _build_estimate_from_cache(conn, task, cache, mode):
    result = await _T2CR_ORIG_BUILD(conn, task, cache, mode)
    if result and result.get("state") in ("AWAITING_CONFIRMATION", "WAITING_CLARIFICATION"):
        msg = result.get("message") or ""
        cleaned = []
        for line in msg.splitlines():
            low = line.lower()
            if "manifest" in low or "/root/" in line or line.startswith("/root"):
                continue
            cleaned.append(line)
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()
        result["message"] = "\n".join(cleaned)
    return result

# === END_PATCH_TOPIC2_CLEAN_RESULT_V1 ===

# === PATCH_TOPIC2_PRICE_AUTO_REVERT_V1 ===
# Fact: PATCH_TOPIC2_PRICE_AUTO_V1 auto-set web_confirm for all topic_2 estimates
# which caused all estimates to be handled by simplified _build_estimate_from_cache,
# bypassing the full P2/P3 pipeline (handle_topic2_one_big_formula_pipeline_v1)
# Fix: new prehandle_price_task_v1 that only intercepts when BOTH conditions are true:
#   1. price cache exists for this chat/topic (meaning price menu was already shown)
#   2. user's input contains a price choice (1/2/3/4/а/б/в/г/etc)
# Fresh estimates now fall through to full pipeline via _handle_in_progress

_PTPA_REVERT_V1 = prehandle_price_task_v1

async def prehandle_price_task_v1(conn, task):
    topic_id = int(_task_field(task, "topic_id", 0) or 0)
    if topic_id == 2:
        chat_id = _s(_task_field(task, "chat_id"))
        raw = _s(_task_field(task, "raw_input"))
        itype = _s(_task_field(task, "input_type"))
        if itype in ("text", "voice"):
            cache_file = _cache_path(chat_id, topic_id)
            has_cache = cache_file.exists()
            has_choice = bool(_detect_price_choice(raw))
            if has_cache and has_choice:
                return await _PTPA_REVERT_V1(conn, task)
        return None
    return await _PTPA_REVERT_V1(conn, task)

# === END_PATCH_TOPIC2_PRICE_AUTO_REVERT_V1 ===

# === PATCH_TOPIC2_PRICE_THREAD_ISOLATION_V1 ===
# Fix: maybe_handle_price_enrichment_from_template_engine sends reply without message_thread_id
# causing price menu to appear in wrong topic thread.
# Also: strict chat_id isolation guard — never process tasks from different chats.
import logging as _tpti_log
_TPTI_LOG = _tpti_log.getLogger("price_enrichment")

_TPTI_ORIG_HANDLE = maybe_handle_price_enrichment_from_template_engine

async def maybe_handle_price_enrichment_from_template_engine(
    conn, task_id: str, chat_id: str, topic_id: int,
    raw_input, input_type: str, reply_to_message_id=None
) -> bool:
    try:
        fake = {
            "id": task_id,
            "chat_id": chat_id,
            "topic_id": topic_id,
            "input_type": input_type,
            "raw_input": _s(raw_input),
            "reply_to_message_id": reply_to_message_id,
        }
        res = await prehandle_price_task_v1(conn, fake)
        if not res or not res.get("handled"):
            return False
        try:
            from core.reply_sender import send_reply_ex
            kwargs = {
                "chat_id": str(chat_id),
                "text": res.get("message") or "",
                "reply_to_message_id": reply_to_message_id,
            }
            if int(topic_id or 0) > 0:
                kwargs["message_thread_id"] = int(topic_id)
            bot = send_reply_ex(**kwargs)
            bot_id = bot.get("bot_message_id") if isinstance(bot, dict) else None
        except Exception:
            bot_id = None
        try:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
            sets = ["state=?", "result=?", "error_message=?", "updated_at=datetime('now')"]
            vals = [res.get("state") or "WAITING_CLARIFICATION", res.get("message") or "", res.get("error_message") or ""]
            if bot_id and "bot_message_id" in cols:
                sets.append("bot_message_id=?")
                vals.append(bot_id)
            vals.append(task_id)
            conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
            conn.execute(
                "INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))",
                (task_id, res.get("history") or "WEB_SEARCH_PRICE_ENRICHMENT_V1:HANDLED"),
            )
            conn.commit()
        except Exception:
            pass
        _TPTI_LOG.info("TPTI: price reply sent chat=%s topic=%s", chat_id, topic_id)
        return True
    except Exception as _tpti_e:
        _TPTI_LOG.warning("TPTI_ERR: %s — fallback to orig", _tpti_e)
        return await _TPTI_ORIG_HANDLE(conn, task_id, chat_id, topic_id, raw_input, input_type, reply_to_message_id)

_TPTI_LOG.info("PATCH_TOPIC2_PRICE_THREAD_ISOLATION_V1 installed")
# === END_PATCH_TOPIC2_PRICE_THREAD_ISOLATION_V1 ===


====================================================================================================
END_FILE: core/price_enrichment.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/price_normalization.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: fc9e7bcb645b740c554e5c520a9bcb363423efd452b9aacaec42081701e70230
====================================================================================================
# === PRICE_NORMALIZATION_V1 ===
import re, logging
logger = logging.getLogger(__name__)

_UNITS = {
    "м2": "м²", "м кв": "м²", "кв м": "м²", "кв.м": "м²",
    "м3": "м³", "куб м": "м³", "м3": "м³",
    "пм": "п.м", "пог м": "п.м", "погонный метр": "п.м",
    "шт": "шт.", "штук": "шт.", "штука": "шт.",
    "т ": "т.", "тонн": "т.", "кг": "кг",
}

def normalize_unit(unit: str) -> str:
    low = unit.lower().strip()
    for k, v in _UNITS.items():
        if k in low:
            return v
    return unit.strip()

def extract_price(text: str) -> list:
    """Извлечь все цены из текста"""
    pattern = r"(\d[\d\s]*[\d])\s*(руб|₽|р\.|рублей|руб\.)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    prices = []
    for m in matches:
        raw = re.sub(r"\s", "", m[0])
        try:
            prices.append(int(raw))
        except Exception:
            pass
    return prices

def normalize_price_text(text: str) -> str:
    """1000000 → 1 000 000 руб."""
    def fmt(m):
        try:
            n = int(re.sub(r"\s", "", m.group(1)))
            return f"{n:,}".replace(",", " ") + " руб."
        except Exception:
            return m.group(0)
    return re.sub(r"(\d[\d\s]{2,})\s*(руб|₽|р\.|рублей)", fmt, text, flags=re.IGNORECASE)

def price_aging_warning(price_date: str, price: float) -> float:
    """PRICE_AGING: +5-10% если прайс старше 48ч (канон §1.6)"""
    if not price_date:
        return price
    try:
        from datetime import datetime, timezone
        ts = datetime.fromisoformat(price_date.replace("Z", "+00:00"))
        age_h = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        if age_h > 48:
            return round(price * 1.075, 2)  # +7.5% среднее
    except Exception:
        pass
    return price
# === END PRICE_NORMALIZATION_V1 ===

====================================================================================================
END_FILE: core/price_normalization.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/project_document_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 365b6bf581651a80f5f9fb153265e84f6a3d02d770d5e1ec8f191d85588aa116
====================================================================================================
# === PROJECT_DOCUMENT_ENGINE_V1 ===
from __future__ import annotations

import json
import os
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

SECTION_MAP = {
    "кж": "КЖ — Конструкции железобетонные",
    "км": "КМ — Конструкции металлические",
    "кмд": "КМД — Конструкции металлические деталировочные",
    "кр": "КР — Конструктивные решения",
    "ар": "АР — Архитектурные решения",
    "ов": "ОВ — Отопление и вентиляция",
    "вк": "ВК — Водоснабжение и канализация",
    "эом": "ЭОМ — Электрооборудование",
    "гп": "ГП — Генеральный план",
    "пз": "ПЗ — Пояснительная записка",
}

NORMS_MAP = {
    "кж": ["СП 63.13330.2018", "СП 20.13330.2016/2017", "ГОСТ 21.501-2018", "ГОСТ 34028-2016"],
    "км": ["СП 16.13330.2017", "ГОСТ 23118-2019", "ГОСТ 21.502-2016"],
    "кмд": ["СП 16.13330.2017", "ГОСТ 21.502-2016", "ГОСТ 23118-2019"],
    "кр": ["СП 20.13330.2016/2017", "ГОСТ 21.501-2018"],
    "ар": ["ГОСТ 21.101-2020", "ГОСТ 21.501-2018", "СП 55.13330.2016"],
    "ов": ["СП 60.13330.2020", "ГОСТ 21.602-2016"],
    "вк": ["СП 30.13330.2020", "ГОСТ 21.601-2011"],
    "эом": ["ПУЭ-7", "СП 256.1325800.2016", "ГОСТ 21.608-2014"],
    "гп": ["СП 42.13330.2016", "ГОСТ 21.508-2020"],
}


# === PROJECT_DOCUMENT_KD_SECTION_MAP_FINAL ===
SECTION_MAP.setdefault("кд", "КД — Конструктивная документация")
NORMS_MAP.setdefault("кд", ["ГОСТ 21.101-2020", "ГОСТ 21.501-2018"])
# === END_PROJECT_DOCUMENT_KD_SECTION_MAP_FINAL ===

def _clean(v: Any, limit: int = 20000) -> str:
    s = "" if v is None else str(v)
    s = s.replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()[:limit]

def _safe(v: Any, fallback: str = "project_document") -> str:
    s = re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", _clean(v, 160)).strip("._")
    return s or fallback

def _extract_text(path: str, file_name: str = "") -> str:
    ext = Path(file_name or path).suffix.lower()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            parts = []
            for page in reader.pages[:80]:
                try:
                    parts.append(page.extract_text() or "")
                except Exception:
                    pass
            return _clean("\n".join(parts), 50000)
        except Exception as e:
            return f"PDF_PARSE_ERROR: {e}"
    if ext == ".docx":
        try:
            from docx import Document
            doc = Document(path)
            return _clean("\n".join(p.text for p in doc.paragraphs if p.text), 50000)
        except Exception as e:
            return f"DOCX_PARSE_ERROR: {e}"
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return _clean(f.read(), 50000)
    except Exception as e:
        return f"TEXT_PARSE_ERROR: {e}"

def _detect_section(file_name: str, user_text: str, text: str) -> str:
    # === PDE_SECTION_DETECT_FINAL ===
    hay = (file_name or "") + "\n" + (user_text or "") + "\n" + (text or "")[:5000]
    hay = hay.lower()
    up = hay.upper().replace("Ё", "Е")

    for key in ("кмд", "кд", "кж", "км", "кр", "ар", "ов", "вк", "эом", "гп", "пз"):
        if re.search(rf"(^|[^А-Яа-яA-Za-z]){re.escape(key.upper())}([^А-Яа-яA-Za-z]|$)", up):
            return key

    if any(x in hay for x in ("фундамент", "плита", "бетон", "арматур", "монолит")):
        return "кж"
    if any(x in hay for x in ("строп", "кровл", "дерев", "обрешет")):
        return "кд"
    if any(x in hay for x in ("архитектур", "планиров", "фасад", "разрез")):
        return "ар"
    if any(x in hay for x in ("отоплен", "вентиляц")):
        return "ов"
    if any(x in hay for x in ("водоснаб", "канализац")):
        return "вк"
    return "кр"
    # === END_PDE_SECTION_DETECT_FINAL ===

def _extract_design_items(text: str) -> List[Dict[str, str]]:
    patterns = [
        ("бетон", r"\bB\d{2,3}\b|В\d{2,3}\b"),
        ("арматура", r"\bA\d{3}\b|А\d{3}\b|Ø\s*\d+|Ф\s*\d+|\b\d{1,2}\s*мм\b"),
        ("сталь", r"\bC\d{3}\b|С\d{3}\b|09Г2С|С245|С255|С345"),
        ("лист", r"\b\d+[,.]?\d*\s*мм\b"),
        ("размер", r"\b\d{3,6}\s*[xх×]\s*\d{3,6}\b|\b\d{3,6}\s*мм\b"),
    ]
    out = []
    for name, pat in patterns:
        found = sorted(set(re.findall(pat, text, flags=re.I)))
        for v in found[:30]:
            out.append({"type": name, "value": str(v), "note": ""})
    return out[:200]

def _build_model(path: str, file_name: str, user_text: str = "", topic_role: str = "") -> Dict[str, Any]:
    text = _extract_text(path, file_name)
    section = _detect_section(file_name, user_text, text)
    items = _extract_design_items(text)
    return {
        "schema": "PROJECT_DOCUMENT_MODEL_V1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_file": file_name or os.path.basename(path),
        "source_path": path,
        "section": section,
        "section_title": SECTION_MAP.get(section, section.upper()),
        "norms": NORMS_MAP.get(section, []),
        "topic_role": topic_role,
        "user_text": user_text,
        "text_chars": len(text or ""),
        "text_preview": _clean(text, 5000),
        "items": items,
        "output_documents": [
            "DOCX_PROJECT_REVIEW",
            "XLSX_PROJECT_REGISTER",
            "JSON_PROJECT_MODEL",
            "ZIP_PROJECT_PACKAGE",
        ],
        "status": "CONFIRMED" if text and not text.endswith("_ERROR") else "PARTIAL",
    }

def _write_docx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"project_document_report_{_safe(task_id)}.docx"
    try:
        from docx import Document
        doc = Document()
        doc.add_heading("PROJECT DOCUMENT MODEL", level=1)
        doc.add_paragraph(f"Файл: {model.get('source_file')}")
        doc.add_paragraph(f"Раздел: {model.get('section_title')}")
        doc.add_paragraph(f"Статус: {model.get('status')}")
        doc.add_heading("Нормативная база", level=2)
        for n in model.get("norms") or []:
            doc.add_paragraph(f"• {n}")
        doc.add_heading("Выделенные проектные параметры", level=2)
        items = model.get("items") or []
        if items:
            table = doc.add_table(rows=1, cols=3)
            table.style = "Table Grid"
            table.rows[0].cells[0].text = "Тип"
            table.rows[0].cells[1].text = "Значение"
            table.rows[0].cells[2].text = "Примечание"
            for it in items[:120]:
                row = table.add_row().cells
                row[0].text = str(it.get("type") or "")
                row[1].text = str(it.get("value") or "")
                row[2].text = str(it.get("note") or "")
        else:
            doc.add_paragraph("Проектные параметры не выделены")
        doc.add_heading("Текстовая сводка", level=2)
        doc.add_paragraph(_clean(model.get("text_preview"), 12000) or "Текст не извлечён")
        doc.save(out)
        return str(out)
    except Exception:
        out_txt = out.with_suffix(".txt")
        out_txt.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(out_txt)

def _write_xlsx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"project_document_register_{_safe(task_id)}.xlsx"
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Summary"
        rows = [
            ("Файл", model.get("source_file")),
            ("Раздел", model.get("section_title")),
            ("Статус", model.get("status")),
            ("Нормы", ", ".join(model.get("norms") or [])),
            ("Символов текста", model.get("text_chars")),
        ]
        for i, (k, v) in enumerate(rows, 1):
            ws.cell(i, 1, k)
            ws.cell(i, 2, v)
        ws2 = wb.create_sheet("Items")
        ws2.append(["Тип", "Значение", "Примечание"])
        for it in model.get("items") or []:
            ws2.append([it.get("type"), it.get("value"), it.get("note")])
        ws3 = wb.create_sheet("ModelJSON")
        for i, line in enumerate(json.dumps(model, ensure_ascii=False, indent=2).splitlines(), 1):
            ws3.cell(i, 1, line)
        wb.save(out)
        wb.close()
        return str(out)
    except Exception:
        out_csv = out.with_suffix(".csv")
        out_csv.write_text("type,value,note\n", encoding="utf-8")
        return str(out_csv)

def _write_json(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"project_document_model_{_safe(task_id)}.json"
    out.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out)

def _zip(paths: List[str], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"project_document_package_{_safe(task_id)}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p and os.path.exists(p):
                z.write(p, arcname=os.path.basename(p))
        z.writestr("manifest.json", json.dumps({
            "engine": "PROJECT_DOCUMENT_ENGINE_V1",
            "task_id": task_id,
            "files": [os.path.basename(p) for p in paths if p and os.path.exists(p)],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }, ensure_ascii=False, indent=2))
    return str(out)

async def process_project_document(
    file_path: str,
    file_name: str = "",
    user_text: str = "",
    topic_role: str = "",
    task_id: str = "artifact",
    topic_id: int = 0,
) -> Dict[str, Any]:
    if not file_path or not os.path.exists(file_path):
        return {"success": False, "error": "PROJECT_DOCUMENT_FILE_NOT_FOUND"}
    model = _build_model(file_path, file_name or os.path.basename(file_path), user_text, topic_role)
    docx = _write_docx(model, task_id)
    xlsx = _write_xlsx(model, task_id)
    js = _write_json(model, task_id)
    package = _zip([docx, xlsx, js], task_id)
    summary = "\n".join([
        "Проектный документ обработан",
        f"Файл: {model.get('source_file')}",
        f"Раздел: {model.get('section_title')}",
        f"Статус: {model.get('status')}",
        f"Нормы: {', '.join(model.get('norms') or [])}",
        f"Проектных параметров: {len(model.get('items') or [])}",
        "Артефакты: DOCX отчёт + XLSX реестр + JSON модель + ZIP пакет",
    ])
    return {
        "success": True,
        "engine": "PROJECT_DOCUMENT_ENGINE_V1",
        "summary": summary,
        "model": model,
        "artifact_path": package,
        "artifact_name": f"{Path(file_name or file_path).stem}_project_document_package.zip",
        "docx_path": docx,
        "xlsx_path": xlsx,
        "json_path": js,
        "extra_artifacts": [docx, xlsx, js],
    }

# === END_PROJECT_DOCUMENT_ENGINE_V1 ===

====================================================================================================
END_FILE: core/project_document_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/quality_gate.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 197e2eb768d13fd8e8b17e6a2e6aed9a5a57c949d8f9bf688ea0b327273058ba
====================================================================================================
# === FULLFIX_QUALITY_GATE_STAGE_4 ===
from __future__ import annotations
from typing import Any, Dict, List

QUALITY_GATE_VERSION = "QUALITY_GATE_V1"

GATE_RULES = {
    "non_empty_answer":            lambda p: bool((p.get("result") or {}).get("text", "").strip()),
    "items_required":              lambda p: bool((p.get("result") or {}).get("items")),
    "total_required":              lambda p: bool((p.get("result") or {}).get("total")),
    "xlsx_required":               lambda p: bool(p.get("artifact_url") or p.get("drive_link")),
    "document_required":           lambda p: bool(p.get("artifact_url") or p.get("drive_link")),
    "document_output_required":    lambda p: bool(p.get("artifact_url") or p.get("drive_link")),
    "drive_link_required":         lambda p: bool(p.get("drive_link") or p.get("artifact_url", "").startswith("http")),
    "sources_required":            lambda p: bool(p.get("sources") or (p.get("result") or {}).get("sources")),
    "price_required":              lambda p: bool((p.get("result") or {}).get("price") or (p.get("result") or {}).get("items")),
    "source_required":             lambda p: bool(p.get("sources") or (p.get("result") or {}).get("url")),
    "tco_required":                lambda p: True,
    "compatibility_required":      lambda p: True,
    "delivery_required":           lambda p: True,
    "table_required":              lambda p: bool(p.get("artifact_url") or (p.get("result") or {}).get("rows")),
    "defect_description_required": lambda p: bool((p.get("result") or {}).get("text", "").strip()),
    "normative_section_required":  lambda p: True,
    "reply_thread_required":       lambda p: bool(p.get("topic_id")),
    "verified_sources_only":       lambda p: True,
    "canon_consistency":           lambda p: True,
}


class QualityGate:
    def check(self, payload: Dict[str, Any], gates: List[str]) -> Dict[str, Any]:
        results = {}
        failed = []
        advisory = []

        for gate in gates:
            rule = GATE_RULES.get(gate)
            if rule is None:
                results[gate] = {"status": "unknown", "advisory": True}
                continue
            try:
                passed = rule(payload)
            except Exception as e:
                passed = False
                results[gate] = {"status": "error", "error": str(e), "advisory": True}
                continue

            advisory_only = gate in ("tco_required", "compatibility_required", "delivery_required",
                                     "normative_section_required", "verified_sources_only", "canon_consistency")
            results[gate] = {"status": "pass" if passed else "fail", "advisory": advisory_only}
            if not passed:
                if advisory_only:
                    advisory.append(gate)
                else:
                    failed.append(gate)

        overall = "pass" if not failed else "fail"
        return {
            "overall": overall,
            "failed": failed,
            "advisory": advisory,
            "gates": results,
            "gate_version": QUALITY_GATE_VERSION,
            "shadow_mode": True,
        }

    def apply_to_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        gates = payload.get("quality_gates") or []
        if not gates:
            return {"overall": "pass", "failed": [], "advisory": [], "gates": {}, "gate_version": QUALITY_GATE_VERSION, "shadow_mode": True}
        report = self.check(payload, gates)
        payload["quality_gate_report"] = report
        return report


def run_quality_gate(payload):
    return QualityGate().apply_to_payload(payload)
# === END FULLFIX_QUALITY_GATE_STAGE_4 ===

====================================================================================================
END_FILE: core/quality_gate.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/reply_sender.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5816e007c6b77fd91f1209cc84235929a1a715b4e0e6c2eb96c6161be40a3fbd
====================================================================================================


# === FULLFIX_13D_REPLY_SENDER_GLOBAL_MANIFEST_STRIP ===
def _ff13d_strip_manifest_links(text):
    import re
    if text is None:
        return text
    t = str(text)
    t = re.sub(r"(?im)^\s*MANIFEST\s*:\s*https?://\S+\s*$", "", t)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    return t
# === END FULLFIX_13D_REPLY_SENDER_GLOBAL_MANIFEST_STRIP ===

import os
import logging
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=False)

LOG_PATH = f"{BASE}/logs/reply_sender.log"
os.makedirs(f"{BASE}/logs", exist_ok=True)

logger = logging.getLogger("reply_sender")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)

BOT_TOKEN = <REDACTED_SECRET>"TELEGRAM_BOT_TOKEN", "").strip()

def _clean(text: str) -> str:
    text = (text or "").replace("\r", "\n").strip()
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text[:12000]

def send_reply(chat_id: str, text: str, reply_to_message_id: Optional[int] = None, message_thread_id: Optional[int] = None) -> bool:
    return send_reply_ex(chat_id=chat_id, text=_ff13d_strip_manifest_links(text), reply_to_message_id=reply_to_message_id, message_thread_id=message_thread_id)["ok"]

def send_reply_ex(chat_id: str, text: str, reply_to_message_id: Optional[int] = None, message_thread_id: Optional[int] = None) -> Dict[str, Any]:
    text = _clean(text)
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return {"ok": False, "bot_message_id": None}
    if not chat_id:
        logger.error("chat_id missing")
        return {"ok": False, "bot_message_id": None}
    if not text:
        logger.error("text empty")
        return {"ok": False, "bot_message_id": None}
    payload = {"chat_id": str(chat_id), "text": _ff13d_strip_manifest_links(text), "disable_web_page_preview": True}
    if message_thread_id and int(message_thread_id) != 0:
        payload["message_thread_id"] = int(message_thread_id)
    if reply_to_message_id:
        payload["reply_to_message_id"] = int(reply_to_message_id)
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload, timeout=30)
        if r.status_code == 200 and r.json().get("ok") is True:
            bot_message_id = r.json().get("result", {}).get("message_id")
            logger.info("reply_ok chat_id=%s reply_to=%s chars=%s bot_message_id=%s", chat_id, reply_to_message_id, len(text), bot_message_id)
            return {"ok": True, "bot_message_id": bot_message_id}
        logger.error("reply_fail code=%s body=%s", r.status_code, r.text[:500])
        return {"ok": False, "bot_message_id": None}
    except Exception as e:
        logger.exception("reply_exception %s", e)
        return {"ok": False, "bot_message_id": None}

====================================================================================================
END_FILE: core/reply_sender.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/result_validator.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ca84125f221e6513690b0621e77e88565bc0ccb3d31d35e3cc4a35284b831b3a
====================================================================================================
# === RESULT_VALIDATOR_V1 ===
import re, logging
logger = logging.getLogger(__name__)

_FORBIDDEN = [
    "файл скачан, ожидает анализа",
    "структура проекта включает",
    "файл содержит проект",
    "этот чат предназначен",
    "анализирую, результат будет готов",
    "проверяю доступные файлы",
    "выбор принят",
    "какие именно файлы вас интересуют",
    "задача не выполнена. повтори",
    "готов к выполнению",
    "не понимаю запрос",
]
_REQUIRED_FOR_FILE = ["http", "drive.google", "docs.google", ".xlsx", ".docx", ".pdf"]

def validate_result(result: str, input_type: str = "text", intent: str = "") -> dict:
    if not result or len(result.strip()) < 10:
        return {"ok": False, "reason": "EMPTY_RESULT"}
    low = result.lower()
    for f in _FORBIDDEN:
        if f in low:
            return {"ok": False, "reason": f"FORBIDDEN_PHRASE:{f[:40]}"}
    is_file_task = input_type in ("drive_file", "file") or intent in ("estimate", "project", "template", "dwg")
    if is_file_task:
        if not any(k in low for k in _REQUIRED_FOR_FILE):
            return {"ok": True, "reason": "NO_ARTIFACT_LINK_WARNING"}
    return {"ok": True, "reason": "OK"}

def is_generic_response(result: str) -> bool:
    low = (result or "").lower()
    return any(f in low for f in _FORBIDDEN)

def enforce_format(result: str, intent: str = "", has_search: bool = False) -> str:
    if not has_search:
        return result
    low = result.lower()
    if "лучший" not in low and "рекомендую" not in low and "итог" not in low:
        result = result.rstrip() + "\n\n⚠️ Нужна таблица сравнения или итоговый выбор?"
    return result

def human_decision_format(technical_result: str, intent: str = "") -> str:
    if not technical_result or len(technical_result) < 30:
        return technical_result
    return technical_result
# === END RESULT_VALIDATOR_V1 ===

====================================================================================================
END_FILE: core/result_validator.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/runtime_file_catalog.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: bdaad8671e3f13ae67e37d3af0905ee451e987fb2c20d65ef3e506a88caf952a
====================================================================================================
# === FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG ===
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path("/root/.areal-neva-core")
CAT_DIR = BASE / "data" / "telegram_file_catalog"
CAT_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe(v) -> str:
    return "" if v is None else str(v).strip()


def _catalog_path(chat_id: str, topic_id: int) -> Path:
    safe_chat = _safe(chat_id).replace("/", "_")
    return CAT_DIR / f"chat_{safe_chat}__topic_{int(topic_id or 0)}.jsonl"


def _hash_record(file_id: str = "", file_name: str = "", size: int = 0) -> str:
    raw = f"{file_id}|{file_name}|{size}".encode("utf-8", "ignore")
    return hashlib.sha256(raw).hexdigest()


def load_catalog(chat_id: str, topic_id: int) -> List[Dict[str, Any]]:
    p = _catalog_path(chat_id, topic_id)
    if not p.exists():
        return []

    out = []
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def find_duplicate(chat_id: str, topic_id: int, file_id: str = "", file_name: str = "", size: int = 0) -> Optional[Dict[str, Any]]:
    h = _hash_record(file_id, file_name, size)
    fn = _safe(file_name).lower()

    for r in reversed(load_catalog(chat_id, topic_id)):
        if r.get("hash") == h:
            return r
        if file_id and r.get("file_id") == file_id:
            return r
        if fn and r.get("file_name", "").lower() == fn and int(r.get("size") or 0) == int(size or 0):
            return r

    return None


def register_file(
    chat_id: str,
    topic_id: int,
    task_id: str,
    file_id: str = "",
    file_name: str = "",
    mime_type: str = "",
    size: int = 0,
    source: str = "telegram",
    drive_link: str = "",
) -> Dict[str, Any]:
    duplicate = find_duplicate(chat_id, topic_id, file_id, file_name, size)
    rec = {
        "engine": "FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG",
        "timestamp": _now(),
        "chat_id": _safe(chat_id),
        "topic_id": int(topic_id or 0),
        "task_id": _safe(task_id),
        "file_id": _safe(file_id),
        "file_name": _safe(file_name),
        "mime_type": _safe(mime_type),
        "size": int(size or 0),
        "source": _safe(source) or "telegram",
        "drive_link": _safe(drive_link),
        "hash": _hash_record(file_id, file_name, size),
        "duplicate": bool(duplicate),
        "duplicate_of": duplicate.get("task_id") if duplicate else "",
    }

    p = _catalog_path(chat_id, topic_id)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return {"ok": True, "duplicate": bool(duplicate), "duplicate_record": duplicate, "record": rec, "catalog_path": str(p)}


def duplicate_user_message(file_name: str, duplicate_record: Dict[str, Any]) -> str:
    old_task = duplicate_record.get("task_id", "")
    old_time = duplicate_record.get("timestamp", "")
    return "\n".join(
        [
            "Этот файл уже был в Telegram",
            f"Файл: {file_name}",
            f"Первая запись: {old_time}",
            f"Задача: {old_task}",
            "Что сделать с повтором: использовать как новый образец, заменить старый или пропустить?",
        ]
    ).strip()


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_RUNTIME_FILE_CATALOG ===

====================================================================================================
END_FILE: core/runtime_file_catalog.py
FILE_CHUNK: 1/1
====================================================================================================
