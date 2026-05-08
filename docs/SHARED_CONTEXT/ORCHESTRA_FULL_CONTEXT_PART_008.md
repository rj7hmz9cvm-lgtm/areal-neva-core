# ORCHESTRA_FULL_CONTEXT_PART_008
generated_at_utc: 2026-05-08T23:45:02.417618+00:00
git_sha_before_commit: 36b3c2db3d693d2ee490f71878f957cc4e6ccac2
part: 8/17


====================================================================================================
BEGIN_FILE: core/project_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 78d74f019c8b179cf8eb33cc618b4099de55b4ae08b382209ad58ab00af35e98
====================================================================================================
# === PROJECT_ENGINE_V1 ===
"""
core/project_engine.py
Разработка проектной документации по нормам ГОСТ/СНиП/СП
на основе шаблонов пользователя.
Разрешение на создание получено: 29.04.2026
"""
import os, re, logging, tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

SECTION_MAP = {
    "кж":  "КЖ — Конструкции железобетонные",
    "км":  "КМ — Конструкции металлические",
    "кмд": "КМД — Конструкции металлические деталировочные",
    "ар":  "АР — Архитектурные решения",
    "ов":  "ОВ — Отопление и вентиляция",
    "вк":  "ВК — Водоснабжение и канализация",
    "эом": "ЭОМ — Электроосвещение",
    "сс":  "СС — Слаботочные системы",
    "гп":  "ГП — Генеральный план",
    "пз":  "ПЗ — Пояснительная записка",
    "см":  "СМ — Смета",
    "тх":  "ТХ — Технологические решения",
}

SECTION_STRUCTURE = {
    "кж":  ["Армирование", "Схемы", "Спецификация арматуры", "Спецификация материалов"],
    "км":  ["Нагрузки", "Узлы сопряжений", "Спецификация металла"],
    "кмд": ["Деталировка", "Узлы", "Спецификация"],
    "ар":  ["Планы этажей", "Фасады", "Разрезы", "Экспликация помещений"],
    "ов":  ["Схема системы", "Расчёт нагрузок", "Спецификация оборудования"],
    "вк":  ["Схема водоснабжения", "Схема канализации", "Спецификация"],
    "эом": ["Однолинейная схема", "Расчёт нагрузок", "Спецификация"],
}

NORMS_MAP = {
    "кж":  ["СП 63.13330.2018", "ГОСТ 34028-2016", "СП 20.13330.2017"],
    "км":  ["СП 16.13330.2017", "ГОСТ 27772-2015", "СП 20.13330.2017"],
    "ар":  ["СП 118.13330.2022", "ГОСТ 21.501-2018"],
    "ов":  ["СП 60.13330.2020", "ГОСТ 30494-2011"],
    "вк":  ["СП 30.13330.2020", "СП 31.13330.2021"],
    "эом": ["СП 256.1325800.2016", "ПУЭ-7"],
}

SNOW_LOADS = {1: 0.8, 2: 1.2, 3: 1.8, 4: 2.4, 5: 3.2, 6: 4.0, 7: 4.8, 8: 5.6}
WIND_LOADS = {1: 0.17, 2: 0.23, 3: 0.30, 4: 0.38, 5: 0.48, 6: 0.60, 7: 0.73, 8: 0.85}

SPEC_HEADERS = ["№", "Наименование", "Марка/Обозначение", "Ед. изм.", "Кол-во", "Примечание"]
UNITS = {"мм", "м", "м2", "м3", "кг", "т", "шт", "пог.м"}


def detect_section(file_name: str, text: str = "") -> Optional[str]:
    # FULLFIX_02_B1: filename-first section priority
    fn = (file_name or "").lower()
    for key in SECTION_MAP:
        if key in fn:
            return key
    src = ((file_name or "") + " " + (text or "")).lower()
    for key in SECTION_MAP:
        if key in src:
            return key
    return None


def calc_loads(region: int = 3) -> Dict[str, float]:
    return {
        "snow_kPa":  SNOW_LOADS.get(region, 1.8),
        "wind_kPa":  WIND_LOADS.get(region, 0.30),
        "region":    region,
        "note":      f"СП 20.13330.2017 — район {region}",
    }


def normalize_unit(unit: str) -> str:
    u = str(unit or "").strip().lower()
    mapping = {"м2": "м2", "м²": "м2", "м3": "м3", "м³": "м3", "кг": "кг", "т": "т", "шт": "шт", "м": "м", "мм": "мм"}
    return mapping.get(u, u)


def build_specification(items: List[Dict]) -> List[List]:
    rows = [SPEC_HEADERS]
    for i, item in enumerate(items, 1):
        rows.append([
            i,
            item.get("name", ""),
            item.get("mark", ""),
            normalize_unit(item.get("unit", "")),
            item.get("qty", ""),
            item.get("note", ""),
        ])
    return rows


def _write_project_xlsx(section: str, items: List[Dict], loads: Dict, task_id: str) -> str:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    wb = Workbook()
    ws = wb.active
    ws.title = section.upper()

    ws.merge_cells("A1:F1")
    ws["A1"] = SECTION_MAP.get(section, section.upper())
    ws["A1"].font = Font(bold=True, size=13)
    ws["A1"].alignment = Alignment(horizontal="center")

    norms = NORMS_MAP.get(section, [])
    ws["A2"] = "Нормы: " + ", ".join(norms) if norms else ""

    if section in ("кж", "км", "кмд"):
        ws["A3"] = f"Снег: {loads['snow_kPa']} кПа | Ветер: {loads['wind_kPa']} кПа | {loads['note']}"

    spec = build_specification(items)
    start_row = 5
    for r_idx, row in enumerate(spec, start_row):
        for c_idx, val in enumerate(row, 1):
            cell = ws.cell(r_idx, c_idx, value=val)
            if r_idx == start_row:
                cell.font = Font(bold=True)
                cell.fill = PatternFill("solid", fgColor="DDEEFF")

    struct = SECTION_STRUCTURE.get(section, [])
    if struct:
        ws.cell(start_row + len(spec) + 2, 1, "Состав раздела:")
        for i, s in enumerate(struct, 1):
            ws.cell(start_row + len(spec) + 2 + i, 1, f"{i}. {s}")

    tmp = os.path.join(tempfile.gettempdir(), f"project_{section}_{task_id}.xlsx")
    wb.save(tmp)
    return tmp


async def generate_project_section(section: str, items: List[Dict], task_id: str, topic_id: int, region: int = 3) -> Dict[str, Any]:
    res = {"success": False, "excel_path": None, "drive_link": None, "section": section, "error": None}
    try:
        loads = calc_loads(region)
        xl = _write_project_xlsx(section, items, loads, task_id)
        res["excel_path"] = xl

        from core.engine_base import upload_artifact_to_drive, quality_gate
        qg = quality_gate(xl, task_id, "excel")
        if not qg["passed"]:
            res["error"] = f"QualityGate: {qg['errors']}"
            return res

        link = upload_artifact_to_drive(xl, task_id, topic_id)
        if link:
            res["drive_link"] = link
            res["success"] = True
        else:
            res["error"] = "UPLOAD_FAILED"
    except Exception as e:
        logger.error(f"project_engine: {e}", exc_info=True)
        res["error"] = str(e)[:300]
    return res


def project_result_guard(result: Dict) -> Dict:
    if not result.get("success"):
        return result
    if not result.get("excel_path") and not result.get("drive_link"):
        result["success"] = False
        result["error"] = "PROJECT_RESULT_GUARD: нет артефакта"
    return result


async def process_project_file(file_path: str, task_id: str, topic_id: int, raw_input: str = "") -> Dict[str, Any]:
    section = detect_section(file_path, raw_input) or "кж"
    items = []

    try:
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in (table or []):
                            if row and any(row):
                                items.append({
                                    "name": str(row[0] or ""),
                                    "mark": str(row[1] or "") if len(row) > 1 else "",
                                    "unit": str(row[2] or "") if len(row) > 2 else "",
                                    "qty":  str(row[3] or "") if len(row) > 3 else "",
                                })
        elif ext in (".xlsx", ".xls"):
            from openpyxl import load_workbook
            wb = load_workbook(file_path, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row and any(v for v in row if v):
                    items.append({
                        "name": str(row[0] or ""),
                        "mark": str(row[1] or "") if len(row) > 1 else "",
                        "unit": str(row[2] or "") if len(row) > 2 else "",
                        "qty":  str(row[3] or "") if len(row) > 3 else "",
                    })
            wb.close()
    except Exception as e:
        logger.warning(f"project extract: {e}")

    result = await generate_project_section(section, items, task_id, topic_id)
    return project_result_guard(result)
# === END_PROJECT_ENGINE_V1 ===

# === CODE_CLOSE_V43_PROJECT_ENGINE ===

def normative_search_engine_v43(section: str, query: str = ""):
    base = NORMS_MAP.get(section, [])
    if base:
        return {"success": True, "norms": base, "source": "local_norms_map"}
    return {"success": False, "norms": [], "error": "норма не подтверждена"}

def project_validator_v43(result):
    if not isinstance(result, dict):
        return False, "PROJECT_VALIDATOR: empty"
    if result.get("success") is False:
        return False, str(result.get("error") or "PROJECT_VALIDATOR: failed")
    if not (result.get("drive_link") or result.get("excel_path") or result.get("docx_path") or result.get("pdf_path")):
        return False, "PROJECT_VALIDATOR: no_artifact"
    return True, ""

def metal_structure_engine_v43(items, region=3):
    loads = calc_loads(region)
    spec = []
    for item in items or []:
        name = str(item.get("name") or "")
        if any(x in name.lower() for x in ("колонна","балка","ферма","связь","прогон")):
            spec.append(item)
    return {"loads": loads, "items": spec, "norms": NORMS_MAP.get("км", [])}

def project_result_guard_v43(result):
    ok, reason = project_validator_v43(result)
    if not ok:
        result = result if isinstance(result, dict) else {}
        result["success"] = False
        result["error"] = reason
    return result

try:
    _v43_orig_generate_project_section = generate_project_section
    async def generate_project_section(section, items, task_id, topic_id, region=3):
        res = await _v43_orig_generate_project_section(section, items, task_id, topic_id, region)
        res["normative_search"] = normative_search_engine_v43(section)
        if section in ("км","кмд"):
            res["metal_structure"] = metal_structure_engine_v43(items, region)
        return project_result_guard_v43(res)
except Exception:
    pass

# === END_CODE_CLOSE_V43_PROJECT_ENGINE ===

# === PROJECT_CLOSE_V44 ===

def normative_search_engine_v44(section: str, query: str = ""):
    norms = NORMS_MAP.get(section, [])
    if norms:
        return {"success": True, "norms": norms, "source": "NORMS_MAP"}
    return {"success": False, "norms": [], "error": "норма не подтверждена"}

def project_validator_v44(result):
    if not isinstance(result, dict):
        return False, "PROJECT_VALIDATOR_EMPTY"
    if result.get("success") is False:
        return False, str(result.get("error") or "PROJECT_VALIDATOR_FAILED")
    if not result.get("section"):
        return False, "PROJECT_VALIDATOR_NO_SECTION"
    if not (result.get("drive_link") or result.get("excel_path") or result.get("docx_path") or result.get("pdf_path")):
        return False, "PROJECT_VALIDATOR_NO_ARTIFACT"
    return True, ""

def metal_structure_engine_v44(items, region=3):
    spec = []
    for item in items or []:
        name = str(item.get("name") or "").lower()
        if any(x in name for x in ("колонна","балка","ферма","связь","прогон","рама","ангар")):
            spec.append(item)
    return {"success": True, "loads": calc_loads(region), "items": spec, "norms": NORMS_MAP.get("км", [])}

def _write_project_docx_v44(section, items, loads, task_id):
    import os, tempfile
    path = os.path.join(tempfile.gettempdir(), f"project_{section}_{task_id}.docx")
    try:
        from docx import Document
        doc = Document()
        doc.add_heading(SECTION_MAP.get(section, section.upper()), level=1)
        doc.add_paragraph("Нормы: " + ", ".join(NORMS_MAP.get(section, [])))
        doc.add_paragraph(f"Снег: {loads.get('snow_kPa')} кПа | Ветер: {loads.get('wind_kPa')} кПа")
        table = doc.add_table(rows=1, cols=6)
        for i, h in enumerate(SPEC_HEADERS):
            table.rows[0].cells[i].text = h
        for n, item in enumerate(items or [], 1):
            row = table.add_row().cells
            row[0].text = str(n)
            row[1].text = str(item.get("name",""))
            row[2].text = str(item.get("mark",""))
            row[3].text = normalize_unit(item.get("unit",""))
            row[4].text = str(item.get("qty",""))
            row[5].text = str(item.get("note",""))
        doc.save(path)
    except Exception:
        with open(path, "w", encoding="utf-8") as f:
            f.write(SECTION_MAP.get(section, section.upper()) + "\n")
            f.write("Нормы: " + ", ".join(NORMS_MAP.get(section, [])) + "\n")
            f.write(str(items or []))
    return path

try:
    _v44_orig_generate_project_section = generate_project_section

    async def generate_project_section(section, items, task_id, topic_id, region=3):
        res = await _v44_orig_generate_project_section(section, items, task_id, topic_id, region)
        loads = calc_loads(region)
        res["normative_search"] = normative_search_engine_v44(section)
        if section in ("км", "кмд"):
            res["metal_structure"] = metal_structure_engine_v44(items, region)
        try:
            docx_path = _write_project_docx_v44(section, items, loads, task_id)
            res["docx_path"] = docx_path
            from core.engine_base import upload_artifact_to_drive
            docx_link = upload_artifact_to_drive(docx_path, task_id, topic_id)
            if docx_link:
                res["docx_link"] = docx_link
        except Exception as e:
            res["docx_error"] = str(e)[:300]
        ok, reason = project_validator_v44(res)
        if not ok:
            res["success"] = False
            res["error"] = reason
        return res
except Exception:
    pass

# === END_PROJECT_CLOSE_V44 ===


# === PATCH_TEMPLATE_MODEL_EXTRACTOR_V1 ===
import re as _re_pte

def extract_template_model_from_text(text: str, file_name: str = "", user_text: str = "") -> dict:
    lines = [l.strip() for l in (text or "").replace("\r","\n").split("\n") if l.strip()]
    # FULLFIX_02_B2: filename-first project type priority, КД/КЖ before АР
    _MARKS_PRI = ("КД","КЖ","КМД","КМ","КР","АР","ОВ","ВК","ЭОМ","СС","ГП","ПЗ","ТХ","СМ")
    project_type = "UNKNOWN"
    for _pt_src in ((file_name or ""), (user_text or ""), (text or "")[:500]):
        _pt_upper = _pt_src.upper()
        for mark in _MARKS_PRI:
            if _re_pte.search(rf"(^|[^А-ЯA-Zа-яa-z]){_re_pte.escape(mark)}([^А-ЯA-Zа-яa-z]|$)", _pt_upper):
                project_type = mark
                break
        if project_type != "UNKNOWN":
            break
    src = f"{file_name} {user_text} {text[:3000]}".upper()
    sheets = []
    for line in lines:
        m = _re_pte.search(r"(АР|КЖ|КД|КР|КМ|КМД|ОВ|ВК|ЭОМ)[\s\-]*(\d+[А-ЯA-Z0-9\-\.]*)\s+(.{4,120})", line, _re_pte.I)
        if m and len(sheets) < 80:
            sheets.append({"mark": m.group(1), "number": m.group(2), "title": m.group(3).strip()})
    section_keys = ("общие данные","исходные данные","расч","план","фасад","разрез","узел","схема","спецификация","ведомость","конструктив","материал")
    sections = []
    seen = set()
    for line in lines:
        if any(k in line.lower() for k in section_keys) and line.lower() not in seen:
            seen.add(line.lower())
            sections.append(line[:160])
        if len(sections) >= 60:
            break
    # FULLFIX_02_B3: sheet_register fallback from extracted structure when explicit sheet marks are absent
    if not sheets and sections:
        _sf_keys = ("общие данные","ведомость","план","фасады","фасад","разрез","узел","спецификация","схема","расч","конструктив")
        _sf_seen = set()
        _sf_seq = 1
        for _sf_line in sections:
            _sf_low = _sf_line.lower()
            if any(k in _sf_low for k in _sf_keys):
                _sf_title = _sf_line[:120].strip()
                if _sf_title and _sf_title.lower() not in _sf_seen:
                    _sf_seen.add(_sf_title.lower())
                    sheets.append({"mark": project_type, "number": str(_sf_seq), "title": _sf_title})
                    _sf_seq += 1
            if _sf_seq > 30:
                break
    axes_letters = sorted(set(_re_pte.findall(r"(?<![А-ЯA-Z])([А-ЯA-Z])(?=\s*[-–]\s*[А-ЯA-Z])", text)))
    axes_numbers = sorted(set(_re_pte.findall(r"(?<!\d)(\d{1,2})(?=\s*[-–]\s*\d{1,2})(?!\d)", text)), key=lambda x: int(x))
    dims = []
    for x in _re_pte.findall(r"(?<!\d)(\d{3,5})(?!\d)", text):
        try:
            v = int(x)
            if 300 <= v <= 50000 and v not in dims:
                dims.append(v)
        except Exception:
            pass
    levels = []
    for v in _re_pte.findall(r"[-+]?\d+[,.]\d{2,3}", text):
        try:
            f = float(v.replace(",","."))
            s = str(f)
            if -20 <= f <= 100 and s not in levels:
                levels.append(s)
        except Exception:
            pass
    mat_keys = ("бетон","арматур","a500","b25","в25","доска","брус","фанера","утепл","профлист","металл","кирпич","газобетон","сталь","с255")
    materials = []
    mat_seen = set()
    for line in lines:
        if any(k in line.lower() for k in mat_keys) and line.lower() not in mat_seen:
            mat_seen.add(line.lower())
            materials.append(line[:180])
        if len(materials) >= 60:
            break
    stamp = {}
    for m in _re_pte.finditer(r"((?:Адрес|По адресу)[:\s]+)([^\n]{5,180})", text, _re_pte.I):
        stamp["address"] = m.group(2).strip()[:200]
        break
    for m in _re_pte.finditer(r"((?:ООО|ОАО|ЗАО|ИП)[^\n]{3,180})", text):
        stamp["developer"] = m.group(1).strip()[:200]
        break
    for m in _re_pte.finditer(r"\b(20\d{2})\b", text):
        stamp["year"] = m.group(1)
        break
    model = {
        "schema": "PROJECT_TEMPLATE_MODEL_V1",
        "project_type": project_type,
        "source_files": [file_name] if file_name else [],
        "sheet_register": sheets,
        "marks": [project_type] if project_type != "UNKNOWN" else [],
        "sections": sections,
        "axes_grid": {"axes_letters": axes_letters[:30], "axes_numbers": axes_numbers[:30]},
        "dimensions": dims[:80],
        "levels": levels[:40],
        "nodes": [x for x in sections if "узел" in x.lower()][:30],
        "specifications": [x for x in sections if any(k in x.lower() for k in ("спецификац","ведомость"))][:30],
        "materials": materials,
        "stamp_fields": stamp,
        "variable_parameters": ["project_name","address","customer","area","floors","axes_grid","dimensions","materials","sheet_register"],
        "output_documents": ["DOCX_PROJECT_TEMPLATE_SUMMARY","JSON_PROJECT_TEMPLATE_MODEL","XLSX_SPECIFICATION_DRAFT"],
        "quality": {
            "has_sheet_register": bool(sheets),
            "has_sections": bool(sections),
            "has_axes_or_dimensions": bool(axes_letters or axes_numbers or dims),
            "has_materials": bool(materials),
            "text_chars": len(text or ""),
            "lines": len(lines),
        }
    }
    return model


def is_valid_project_template_model(model: dict) -> bool:
    if not isinstance(model, dict):
        return False
    q = model.get("quality") or {}
    return bool(
        model.get("schema") == "PROJECT_TEMPLATE_MODEL_V1"
        and q.get("text_chars", 0) > 200
        and (q.get("has_sheet_register") or q.get("has_sections") or q.get("has_axes_or_dimensions") or q.get("has_materials"))
    )


def model_to_text_report(model: dict) -> str:
    lines = ["PROJECT_TEMPLATE_MODEL создан"]
    lines.append(f"Раздел: {model.get('project_type','UNKNOWN')}")
    lines.append("")
    sheets = model.get("sheet_register") or []
    lines.append(f"Состав листов ({len(sheets)}):")
    for s in sheets[:30]:
        lines.append(f"  {s.get('mark','')} {s.get('number','')} {s.get('title','')}".strip())
    if not sheets:
        lines.append("  не извлечён явно")
    lines.append("")
    lines.append("Структура/разделы:")
    for s in (model.get("sections") or [])[:20]:
        lines.append(f"  {s}")
    lines.append("")
    ag = model.get("axes_grid") or {}
    lines.append(f"Оси буквенные: {', '.join(ag.get('axes_letters',[]) or []) or 'не извлечены'}")
    lines.append(f"Оси цифровые: {', '.join(ag.get('axes_numbers',[]) or []) or 'не извлечены'}")
    dims = model.get("dimensions") or []
    lines.append(f"Размеры мм: {', '.join(map(str,dims[:20])) if dims else 'не извлечены'}")
    lines.append("")
    mats = model.get("materials") or []
    lines.append(f"Материалы ({len(mats)}):")
    for m in mats[:15]:
        lines.append(f"  {m}")
    return "\n".join(lines).strip()

# === END PATCH_TEMPLATE_MODEL_EXTRACTOR_V1 ===


# === FULLFIX_03_PROJECT_ARTIFACT_GENERATOR ===
def _ff3_latest_project_template_model(topic_id: int = 0) -> dict:
    import json, os, glob
    base = "/root/.areal-neva-core/data/project_templates"
    files = sorted(glob.glob(os.path.join(base, "PROJECT_TEMPLATE_MODEL__*.json")), key=os.path.getmtime, reverse=True)
    if not files:
        return {}
    topic_id = int(topic_id or 0)
    best = None
    for p in files:
        try:
            data = json.load(open(p, encoding="utf-8"))
            if topic_id and int(data.get("topic_id", 0) or 0) == topic_id:
                return data
            if best is None:
                best = data
        except Exception:
            pass
    return best or {}


def _ff3_extract_project_params(user_text: str) -> dict:
    import re
    txt = str(user_text or "")
    low = txt.lower()

    params = {}
    if "фундамент" in low or "плита" in low:
        params["project_name"] = "Проект фундаментной плиты"
        params["section"] = "КЖ"
    elif "кров" in low or "строп" in low:
        params["project_name"] = "Проект кровли"
        params["section"] = "КД"
    else:
        params["project_name"] = "Проект по образцу"
        params["section"] = ""

    m = re.search(r"(\d+(?:[,.]\d+)?)\s*[xх×]\s*(\d+(?:[,.]\d+)?)\s*м", low)
    if m:
        params["size"] = f"{m.group(1).replace(',', '.')} x {m.group(2).replace(',', '.')} м"

    for label, key in (
        ("толщина", "thickness"),
        ("песчан", "sand"),
        ("щеб", "gravel"),
        ("бетон", "concrete"),
        ("арматур", "rebar"),
    ):
        mm = re.search(label + r"[^0-9]{0,30}(\d{2,4})\s*мм", low)
        if mm:
            params[key] = mm.group(1) + " мм"

    return params


def _ff3_safe_docx_text(value) -> str:
    return str(value or "").replace("\x00", " ").strip()


def create_project_artifact_from_latest_template(user_text: str, task_id: str, topic_id: int = 0) -> dict:
    """
    Создаёт реальный DOCX + XLSX проектный артефакт по последней PROJECT_TEMPLATE_MODEL
    Возвращает пути и Drive-ссылки
    """
    import os, tempfile, json
    from datetime import datetime, timezone

    result = {
        "success": False,
        "error": "",
        "docx_path": "",
        "xlsx_path": "",
        "docx_link": "",
        "xlsx_link": "",
        "template_found": False,
        "project_type": "UNKNOWN",
    }

    # === PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_HOOK_V1 ===
    try:
        _project_template_memory_catalog_sync_absolute_v1(int(topic_id or 210), dry_run=False)
    except Exception:
        pass
    # === END_PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_HOOK_V1 ===
    model = _ff3_latest_project_template_model(topic_id)
    params = _ff3_extract_project_params(user_text)
    if not model:
        result["error"] = "PROJECT_TEMPLATE_MODEL_NOT_FOUND"
        return result

    result["template_found"] = True
    project_type = params.get("section") or model.get("project_type") or "UNKNOWN"
    result["project_type"] = project_type

    safe_task = str(task_id or "manual")[:8]
    out_dir = tempfile.gettempdir()
    docx_path = os.path.join(out_dir, f"project_{project_type}_{safe_task}.docx")
    xlsx_path = os.path.join(out_dir, f"project_{project_type}_{safe_task}.xlsx")

    sheets = model.get("sheet_register") or []
    # === SHEETS_NORMALIZE_V1 ===
    _sheets_raw = sheets
    sheets = []
    for _sh in _sheets_raw:
        if isinstance(_sh, str) and _sh.strip():
            sheets.append({"mark": project_type, "number": str(len(sheets) + 1), "title": _sh.strip()[:120]})
        elif isinstance(_sh, dict):
            sheets.append(_sh)
    # === END_SHEETS_NORMALIZE_V1 ===
    if not sheets:
        for i, sec in enumerate(model.get("sections") or [], 1):
            sheets.append({"mark": project_type, "number": str(i), "title": str(sec)[:120]})

    if not sheets:
        sheets = [
            {"mark": project_type, "number": "1", "title": "Титульный лист"},
            {"mark": project_type, "number": "2", "title": "Общие данные"},
            {"mark": project_type, "number": "3", "title": "План"},
            {"mark": project_type, "number": "4", "title": "Разрезы"},
            {"mark": project_type, "number": "5", "title": "Спецификация"},
        ]

    try:
        from docx import Document
        doc = Document()
        doc.add_heading(_ff3_safe_docx_text(params.get("project_name") or "Проект по образцу"), level=1)
        doc.add_paragraph("Сформировано AREAL-NEVA ORCHESTRA по сохранённой PROJECT_TEMPLATE_MODEL")
        doc.add_paragraph(f"Раздел: {project_type}")
        doc.add_paragraph(f"Дата: {datetime.now(timezone.utc).isoformat()}")

        doc.add_heading("Параметры задания", level=2)
        if params:
            for k, v in params.items():
                doc.add_paragraph(f"{k}: {v}")
        else:
            doc.add_paragraph(_ff3_safe_docx_text(user_text))

        doc.add_heading("Состав проекта по образцу", level=2)
        tbl = doc.add_table(rows=1, cols=3)
        tbl.rows[0].cells[0].text = "Марка"
        tbl.rows[0].cells[1].text = "Лист"
        tbl.rows[0].cells[2].text = "Наименование"
        for sh in sheets:
            row = tbl.add_row().cells
            row[0].text = _ff3_safe_docx_text(sh.get("mark") or project_type)
            row[1].text = _ff3_safe_docx_text(sh.get("number") or "")
            row[2].text = _ff3_safe_docx_text(sh.get("title") or "")

        doc.add_heading("Оси и размеры", level=2)
        ag = model.get("axes_grid") or {}
        doc.add_paragraph("Оси буквенные: " + (", ".join(ag.get("axes_letters") or []) or "не извлечены"))
        doc.add_paragraph("Оси цифровые: " + (", ".join(ag.get("axes_numbers") or []) or "не извлечены"))
        dims = model.get("dimensions") or []
        doc.add_paragraph("Размеры мм: " + (", ".join(map(str, dims[:60])) if dims else "не извлечены"))

        doc.add_heading("Материалы из образца", level=2)
        mats = model.get("materials") or []
        if mats:
            for m in mats[:60]:
                doc.add_paragraph(_ff3_safe_docx_text(m))
        else:
            doc.add_paragraph("Материалы не извлечены из образца")

        doc.add_heading("Техническая структура", level=2)
        for sec in (model.get("sections") or [])[:80]:
            doc.add_paragraph(_ff3_safe_docx_text(sec))

        doc.save(docx_path)
    except Exception as e:
        result["error"] = "DOCX_CREATE_FAILED: " + str(e)[:250]
        return result

    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Состав проекта"
        headers = ["№", "Марка", "Лист", "Наименование", "Источник"]
        for c, h in enumerate(headers, 1):
            ws.cell(1, c, h)
        for i, sh in enumerate(sheets, 2):
            ws.cell(i, 1, i - 1)
            ws.cell(i, 2, sh.get("mark") or project_type)
            ws.cell(i, 3, sh.get("number") or "")
            ws.cell(i, 4, sh.get("title") or "")
            ws.cell(i, 5, ",".join(model.get("source_files") or []))
        ws2 = wb.create_sheet("Параметры")
        ws2.cell(1, 1, "Параметр")
        ws2.cell(1, 2, "Значение")
        for r, (k, v) in enumerate(params.items(), 2):
            ws2.cell(r, 1, k)
            ws2.cell(r, 2, v)
        ws.column_dimensions["D"].width = 70
        ws.column_dimensions["E"].width = 50
        ws2.column_dimensions["A"].width = 30
        ws2.column_dimensions["B"].width = 70
        wb.save(xlsx_path)
        wb.close()
    except Exception as e:
        result["error"] = "XLSX_CREATE_FAILED: " + str(e)[:250]
        return result

    result["docx_path"] = docx_path
    result["xlsx_path"] = xlsx_path

    try:
        from core.engine_base import upload_artifact_to_drive
        docx_link = upload_artifact_to_drive(docx_path, task_id, int(topic_id or 0))
        xlsx_link = upload_artifact_to_drive(xlsx_path, task_id, int(topic_id or 0))
        result["docx_link"] = docx_link or ""
        result["xlsx_link"] = xlsx_link or ""
    except Exception as e:
        result["upload_error"] = str(e)[:250]

    result["success"] = bool(os.path.exists(docx_path) and os.path.getsize(docx_path) > 1000)
    if not result["success"]:
        result["error"] = "PROJECT_ARTIFACT_EMPTY"
    return result

# === END FULLFIX_03_PROJECT_ARTIFACT_GENERATOR ===


# === FULLFIX_05_REAL_PROJECT_ENGINE ===
import os as _os_ff05
import re as _re_ff05
import json as _json_ff05
import math as _math_ff05
import tempfile as _tempfile_ff05
from pathlib import Path as _Path_ff05
from datetime import datetime as _dt_ff05

def _ff05_float(v, default=0.0):
    try:
        return float(str(v).replace(",", "."))
    except Exception:
        return float(default)

def _ff05_int(v, default=0):
    try:
        return int(float(str(v).replace(",", ".")))
    except Exception:
        return int(default)

def _ff05_latest_template(section: str = "КЖ") -> dict:
    base = _Path_ff05("/root/.areal-neva-core/data/project_templates")
    if not base.exists():
        return {}
    files = sorted(base.glob("PROJECT_TEMPLATE_MODEL__*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    section_u = str(section or "").upper()
    fallback = {}
    for p in files[:50]:
        try:
            data = _json_ff05.loads(p.read_text(encoding="utf-8"))
            data["_template_file"] = str(p)
            pt = str(data.get("project_type") or "").upper()
            if not fallback:
                fallback = data
            if pt == section_u:
                return data
        except Exception:
            continue
    return fallback

def _ff05_parse_project_request(raw_input: str, template_hint: str = "") -> dict:
    text = str(raw_input or "")
    low = text.lower()

    section = "КЖ"
    if any(x in low for x in ("кд", "деревян", "стропил", "кровл")):
        section = "КД"
    if any(x in low for x in ("кж", "фундамент", "плит")):
        section = "КЖ"

    length_m = 10.0
    width_m = 10.0
    slab_mm = 200
    sand_mm = 300
    gravel_mm = 100
    concrete_class = "B25"
    rebar_class = "A500C"
    rebar_step_mm = 200
    rebar_diam_mm = 12
    cover_mm = 40

    m = _re_ff05.search(r"(\d+(?:[,.]\d+)?)\s*[xх×]\s*(\d+(?:[,.]\d+)?)\s*м?", low)
    if m:
        length_m = _ff05_float(m.group(1), length_m)
        width_m = _ff05_float(m.group(2), width_m)

    def find_mm(keys, default):
        for key in keys:
            m2 = _re_ff05.search(key + r".{0,40}?(\d{2,4})\s*мм", low)
            if m2:
                return _ff05_int(m2.group(1), default)
        return default

    slab_mm = find_mm(("толщин", "плит", "бетон"), slab_mm)
    sand_mm = find_mm(("песчан", "песок"), sand_mm)
    gravel_mm = find_mm(("щеб", "основан"), gravel_mm)

    m = _re_ff05.search(r"(b|в)\s?(\d{2,3})", low)
    if m:
        concrete_class = "B" + m.group(2)

    m = _re_ff05.search(r"(a|а)\s?500", low)
    if m:
        rebar_class = "A500C"

    m = _re_ff05.search(r"(?:шаг|ячейк).{0,30}?(\d{2,4})\s*мм", low)
    if m:
        rebar_step_mm = _ff05_int(m.group(1), rebar_step_mm)

    m = _re_ff05.search(r"(?:арматур|ø|ф|диаметр).{0,30}?(\d{1,2})\s*мм", low)
    if m:
        rebar_diam_mm = _ff05_int(m.group(1), rebar_diam_mm)

    template = _ff05_latest_template(section)

    return {
        "project_name": "Проект фундаментной плиты" if section == "КЖ" else "Проект КД",
        "section": section,
        "length_m": length_m,
        "width_m": width_m,
        "slab_mm": slab_mm,
        "sand_mm": sand_mm,
        "gravel_mm": gravel_mm,
        "concrete_class": concrete_class,
        "rebar_class": rebar_class,
        "rebar_step_mm": rebar_step_mm,
        "rebar_diam_mm": rebar_diam_mm,
        "cover_mm": cover_mm,
        "template": {
            "project_type": template.get("project_type"),
            "source_files": template.get("source_files") or [],
            "template_file": template.get("_template_file"),
            "sections": template.get("sections") or [],
            "sheet_register": template.get("sheet_register") or [],
            "materials": template.get("materials") or [],
        },
    }

def _ff05_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for fp in candidates:
        if _os_ff05.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("AREALFONT", fp))
                return "AREALFONT"
            except Exception:
                pass
    return "Helvetica"

def _ff05_draw_frame(c, page_w, page_h, title, sheet_no, sheet_total, font):
    from reportlab.lib.units import mm
    c.setLineWidth(0.7)
    c.rect(12*mm, 10*mm, page_w - 24*mm, page_h - 20*mm)
    c.line(12*mm, 28*mm, page_w - 12*mm, 28*mm)
    c.line(page_w - 95*mm, 10*mm, page_w - 95*mm, 28*mm)
    c.line(page_w - 55*mm, 10*mm, page_w - 55*mm, 28*mm)
    c.line(page_w - 25*mm, 10*mm, page_w - 25*mm, 28*mm)

    c.setFont(font, 9)
    c.drawString(15*mm, 18*mm, "AREAL-NEVA")
    c.drawString(page_w - 92*mm, 18*mm, "Стадия: П")
    c.drawString(page_w - 52*mm, 18*mm, f"Лист: {sheet_no}")
    c.drawString(page_w - 22*mm, 18*mm, f"Листов: {sheet_total}")

    c.setFont(font, 13)
    c.drawString(18*mm, page_h - 20*mm, title)
    c.setFont(font, 8)
    c.drawString(18*mm, page_h - 27*mm, "Комплект создан автоматически по задаче пользователя и сохранён как PDF/DXF артефакт")

def _ff05_draw_text(c, x, y, text, font, size=9):
    from reportlab.lib.units import mm
    c.setFont(font, size)
    c.drawString(x*mm, y*mm, str(text))

def _ff05_write_project_pdf(path: str, data: dict) -> str:
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _ff05_font()
    page_w, page_h = landscape(A3)
    c = canvas.Canvas(path, pagesize=landscape(A3))

    L = float(data["length_m"])
    W = float(data["width_m"])
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    rebar_d = int(data["rebar_diam_mm"])
    rebar_step = int(data["rebar_step_mm"])
    cover = int(data["cover_mm"])
    concrete = data["concrete_class"]
    rebar_class = data["rebar_class"]
    sheet_total = 6

    # 1 title / general data
    _ff05_draw_frame(c, page_w, page_h, "Общие данные", 1, sheet_total, font)
    lines = [
        f"Наименование: {data['project_name']}",
        f"Раздел: {data['section']}",
        f"Габарит плиты: {L:g} x {W:g} м",
        f"Толщина плиты: {slab} мм",
        f"Подготовка: песок {sand} мм, щебень {gravel} мм",
        f"Бетон: {concrete}",
        f"Арматура: {rebar_class} Ø{rebar_d} с шагом {rebar_step} мм, защитный слой {cover} мм",
        "Выходные файлы: PDF-комплект + DXF-чертёж со слоями",
    ]
    y = 255
    for line in lines:
        _ff05_draw_text(c, 25, y, line, font, 11)
        y -= 9

    tpl = data.get("template") or {}
    _ff05_draw_text(c, 25, y - 5, "Источник структуры шаблона:", font, 11)
    y -= 15
    src_files = tpl.get("source_files") or []
    _ff05_draw_text(c, 30, y, ", ".join(src_files) if src_files else "не найден сохранённый исходный PDF-шаблон", font, 9)
    y -= 10
    c.showPage()

    # 2 plan
    _ff05_draw_frame(c, page_w, page_h, "План фундаментной плиты", 2, sheet_total, font)
    x0, y0 = 70*mm, 55*mm
    max_w, max_h = 260*mm, 150*mm
    scale = min(max_w/(L*1000), max_h/(W*1000))
    rw, rh = L*1000*scale, W*1000*scale
    c.setLineWidth(1.2)
    c.rect(x0, y0, rw, rh)
    c.setDash(4, 3)
    c.line(x0, y0+rh/2, x0+rw, y0+rh/2)
    c.line(x0+rw/2, y0, x0+rw/2, y0+rh)
    c.setDash()

    # rebar grid
    c.setLineWidth(0.25)
    step_draw = max(0.6*mm, rebar_step*scale)
    xx = x0 + step_draw
    while xx < x0 + rw:
        c.line(xx, y0, xx, y0+rh)
        xx += step_draw
    yy = y0 + step_draw
    while yy < y0 + rh:
        c.line(x0, yy, x0+rw, yy)
        yy += step_draw

    c.setFont(font, 9)
    c.drawString(x0, y0 - 8*mm, f"{L:g} м")
    c.saveState()
    c.translate(x0 - 10*mm, y0)
    c.rotate(90)
    c.drawString(0, 0, f"{W:g} м")
    c.restoreState()
    _ff05_draw_text(c, 25, 240, f"Армирование: {rebar_class} Ø{rebar_d} шаг {rebar_step} мм в двух направлениях", font, 10)
    _ff05_draw_text(c, 25, 230, f"Защитный слой бетона: {cover} мм", font, 10)
    c.showPage()

    # 3 section
    _ff05_draw_frame(c, page_w, page_h, "Разрез 1-1", 3, sheet_total, font)
    bx, by = 60*mm, 70*mm
    total = slab + gravel + sand
    k = 95*mm / total
    layers = [
        ("Фундаментная плита", slab, "Бетон " + concrete),
        ("Щебёночное основание", gravel, "Щебень"),
        ("Песчаная подушка", sand, "Песок"),
    ]
    ycur = by
    c.setLineWidth(0.8)
    for name, thick, note in layers:
        hh = thick * k
        c.rect(bx, ycur, 210*mm, hh)
        c.setFont(font, 10)
        c.drawString(bx + 5*mm, ycur + hh/2, f"{name}: {thick} мм — {note}")
        ycur += hh
    _ff05_draw_text(c, 25, 230, f"Общая конструктивная толщина: {total} мм", font, 10)
    c.showPage()

    # 4 reinforcement
    _ff05_draw_frame(c, page_w, page_h, "Схема армирования", 4, sheet_total, font)
    x0, y0 = 70*mm, 55*mm
    c.rect(x0, y0, rw, rh)
    c.setLineWidth(0.35)
    step_draw = max(1.0*mm, rebar_step*scale)
    xx = x0 + step_draw
    while xx < x0 + rw:
        c.line(xx, y0, xx, y0+rh)
        xx += step_draw
    yy = y0 + step_draw
    while yy < y0 + rh:
        c.line(x0, yy, x0+rw, yy)
        yy += step_draw
    _ff05_draw_text(c, 25, 240, f"Нижняя сетка: {rebar_class} Ø{rebar_d} шаг {rebar_step} мм", font, 10)
    _ff05_draw_text(c, 25, 230, f"Верхняя сетка: {rebar_class} Ø{rebar_d} шаг {rebar_step} мм", font, 10)
    _ff05_draw_text(c, 25, 220, "Выпуски, усиления, проёмы и закладные требуют отдельного задания", font, 9)
    c.showPage()

    # 5 specification
    _ff05_draw_frame(c, page_w, page_h, "Спецификация материалов", 5, sheet_total, font)
    area = L * W
    concrete_m3 = round(area * slab / 1000, 3)
    sand_m3 = round(area * sand / 1000, 3)
    gravel_m3 = round(area * gravel / 1000, 3)
    bars_x = _math_ff05.floor((W*1000 - 2*cover) / rebar_step) + 1
    bars_y = _math_ff05.floor((L*1000 - 2*cover) / rebar_step) + 1
    rebar_m = round((bars_x * L + bars_y * W) * 2, 1)
    spec = [
        ("1", f"Бетон {concrete}", "м3", concrete_m3),
        ("2", "Песчаная подушка", "м3", sand_m3),
        ("3", "Щебёночное основание", "м3", gravel_m3),
        ("4", f"Арматура {rebar_class} Ø{rebar_d}", "п.м", rebar_m),
    ]
    y = 240
    _ff05_draw_text(c, 25, y, "№   Наименование                              Ед.     Кол-во", font, 11)
    y -= 10
    for row in spec:
        _ff05_draw_text(c, 25, y, f"{row[0]:<3} {row[1]:<40} {row[2]:<6} {row[3]}", font, 10)
        y -= 9
    c.showPage()

    # 6 sheet list
    _ff05_draw_frame(c, page_w, page_h, "Ведомость листов", 6, sheet_total, font)
    sheets = [
        ("1", "Общие данные"),
        ("2", "План фундаментной плиты"),
        ("3", "Разрез 1-1"),
        ("4", "Схема армирования"),
        ("5", "Спецификация материалов"),
        ("6", "Ведомость листов"),
    ]
    y = 240
    for n, title in sheets:
        _ff05_draw_text(c, 25, y, f"{n}. {title}", font, 11)
        y -= 9
    c.save()

    return path

def _ff05_write_project_dxf(path: str, data: dict) -> str:
    import ezdxf

    L = float(data["length_m"]) * 1000.0
    W = float(data["width_m"]) * 1000.0
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = int(data["rebar_step_mm"])
    rebar_d = int(data["rebar_diam_mm"])
    concrete = str(data["concrete_class"])
    rebar_class = str(data["rebar_class"])

    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    layers = {
        "KJ-SLAB": 7,
        "KJ-AXIS": 1,
        "KJ-REBAR": 3,
        "KJ-DIMS": 5,
        "KJ-TEXT": 2,
        "KJ-SECTION": 4,
    }
    for name, color in layers.items():
        if name not in doc.layers:
            doc.layers.new(name=name, dxfattribs={"color": color})

    # plan outline
    pts = [(0, 0), (L, 0), (L, W), (0, W), (0, 0)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": "KJ-SLAB", "closed": True})

    # axes
    msp.add_line((L/2, -500), (L/2, W+500), dxfattribs={"layer": "KJ-AXIS"})
    msp.add_line((-500, W/2), (L+500, W/2), dxfattribs={"layer": "KJ-AXIS"})

    # rebar grid
    x = step
    while x < L:
        msp.add_line((x, 0), (x, W), dxfattribs={"layer": "KJ-REBAR"})
        x += step
    y = step
    while y < W:
        msp.add_line((0, y), (L, y), dxfattribs={"layer": "KJ-REBAR"})
        y += step

    # section block at right side
    sx = L + 2500
    sy = 0
    total = slab + gravel + sand
    msp.add_lwpolyline([(sx, sy), (sx+5000, sy), (sx+5000, sy+total), (sx, sy+total), (sx, sy)], dxfattribs={"layer": "KJ-SECTION", "closed": True})
    y1 = sy
    for name, th in [("SAND", sand), ("GRAVEL", gravel), ("SLAB", slab)]:
        msp.add_line((sx, y1), (sx+5000, y1), dxfattribs={"layer": "KJ-SECTION"})
        msp.add_text(f"{name} {th}mm", dxfattribs={"height": 250, "layer": "KJ-TEXT"}).set_placement((sx+5200, y1 + th/2))
        y1 += th
    msp.add_line((sx, y1), (sx+5000, y1), dxfattribs={"layer": "KJ-SECTION"})

    # notes
    msp.add_text(f"FOUNDATION SLAB {L/1000:g}x{W/1000:g}m", dxfattribs={"height": 350, "layer": "KJ-TEXT"}).set_placement((0, -1200))
    msp.add_text(f"SLAB {slab}mm / {concrete}", dxfattribs={"height": 250, "layer": "KJ-TEXT"}).set_placement((0, -1700))
    msp.add_text(f"REBAR {rebar_class} D{rebar_d} STEP {step}mm", dxfattribs={"height": 250, "layer": "KJ-TEXT"}).set_placement((0, -2100))
    msp.add_text(f"SAND {sand}mm / GRAVEL {gravel}mm", dxfattribs={"height": 250, "layer": "KJ-TEXT"}).set_placement((0, -2500))

    doc.saveas(path)
    return path

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "") -> dict:
    data = _ff05_parse_project_request(raw_input, template_hint)
    stamp = _dt_ff05.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_task = _re_ff05.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id or "manual"))[:20]
    out_dir = _Path_ff05(_tempfile_ff05.gettempdir()) / f"areal_project_{safe_task}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = str(out_dir / f"{data['section']}_foundation_slab_{safe_task}.pdf")
    dxf_path = str(out_dir / f"{data['section']}_foundation_slab_{safe_task}.dxf")
    manifest_path = str(out_dir / f"{data['section']}_foundation_slab_{safe_task}.manifest.json")

    res = {
        "success": False,
        "section": data["section"],
        "pdf_path": pdf_path,
        "dxf_path": dxf_path,
        "manifest_path": manifest_path,
        "pdf_link": None,
        "dxf_link": None,
        "manifest_link": None,
        "error": None,
        "data": data,
    }

    try:
        _ff05_write_project_pdf(pdf_path, data)
        _ff05_write_project_dxf(dxf_path, data)

        if not _os_ff05.path.exists(pdf_path) or _os_ff05.path.getsize(pdf_path) < 3000:
            res["error"] = "PDF_NOT_CREATED_OR_TOO_SMALL"
            return res
        if not _os_ff05.path.exists(dxf_path) or _os_ff05.path.getsize(dxf_path) < 1500:
            res["error"] = "DXF_NOT_CREATED_OR_TOO_SMALL"
            return res

        manifest = {
            "schema": "AREAL_PROJECT_ARTIFACT_V1",
            "created_at": _dt_ff05.utcnow().isoformat() + "Z",
            "task_id": task_id,
            "topic_id": topic_id,
            "engine": "FULLFIX_05_REAL_PROJECT_ENGINE",
            "input": raw_input,
            "data": data,
            "files": {
                "pdf": pdf_path,
                "dxf": dxf_path,
            },
        }
        _Path_ff05(manifest_path).write_text(_json_ff05.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        from core.engine_base import upload_artifact_to_drive
        pdf_link = upload_artifact_to_drive(pdf_path, task_id, topic_id)
        dxf_link = upload_artifact_to_drive(dxf_path, task_id, topic_id)
        manifest_link = upload_artifact_to_drive(manifest_path, task_id, topic_id)

        if not pdf_link:
            res["error"] = "PDF_UPLOAD_FAILED"
            return res
        if not dxf_link:
            res["error"] = "DXF_UPLOAD_FAILED"
            return res

        res.update({
            "success": True,
            "pdf_link": str(pdf_link),
            "dxf_link": str(dxf_link),
            "manifest_link": str(manifest_link or ""),
        })
        return res

    except Exception as e:
        res["error"] = str(e)[:500]
        return res

# === END FULLFIX_05_REAL_PROJECT_ENGINE ===


# === FULLFIX_06_FINAL_PROJECT_TEMPLATE_REPLAY ===
import os as _os_ff06
import re as _re_ff06
import json as _json_ff06
import glob as _glob_ff06
import tempfile as _tempfile_ff06
from pathlib import Path as _Path_ff06
from datetime import datetime as _dt_ff06

def _ff06_clean_text(v, limit=5000):
    return str(v or "").replace("\x00", " ").strip()[:limit]

def _ff06_find_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for x in candidates:
        if _os_ff06.path.exists(x):
            return x
    return ""

def _ff06_latest_template(topic_id=0, preferred_section=""):
    base = "/root/.areal-neva-core/data/project_templates"
    files = sorted(
        _glob_ff06.glob(_os_ff06.path.join(base, "PROJECT_TEMPLATE_MODEL__*.json")),
        key=lambda x: _os_ff06.path.getmtime(x),
        reverse=True,
    )
    if not files:
        return {}
    topic_id = int(topic_id or 0)
    preferred_section = _ff06_clean_text(preferred_section).upper()
    best = None
    for fp in files:
        try:
            data = _json_ff06.loads(_Path_ff06(fp).read_text(encoding="utf-8"))
            data["_template_file"] = fp
            pt = _ff06_clean_text(data.get("project_type")).upper()
            dtid = int(data.get("topic_id", 0) or 0)
            if topic_id and dtid == topic_id and preferred_section and pt == preferred_section:
                return data
            if topic_id and dtid == topic_id and not best:
                best = data
            if preferred_section and pt == preferred_section and not best:
                best = data
            if not best:
                best = data
        except Exception:
            continue
    return best or {}

def _ff06_parse_request(raw_input, template_hint=""):
    text = _ff06_clean_text(raw_input, 10000)
    low = text.lower()
    out = {
        "section": "КЖ",
        "project_name": "Проект фундаментной плиты",
        "length_m": 10.0,
        "width_m": 10.0,
        "slab_mm": 200,
        "sand_mm": 300,
        "gravel_mm": 100,
        "concrete_class": "B25",
        "rebar_class": "A500",
        "rebar_diam_mm": 12,
        "rebar_step_mm": 200,
        "raw_input": text,
        "template_hint": template_hint or "",
    }

    if "кд" in low or "кров" in low or "строп" in low:
        out["section"] = "КД"
        out["project_name"] = "Проект кровли"
    if "ар" in low and "фундамент" not in low and "кров" not in low:
        out["section"] = "АР"
        out["project_name"] = "Архитектурный раздел"
    if "кж" in low or "фундамент" in low or "плит" in low:
        out["section"] = "КЖ"
        out["project_name"] = "Проект фундаментной плиты"

    m = _re_ff06.search(r"(\d+(?:[,.]\d+)?)\s*[xх×]\s*(\d+(?:[,.]\d+)?)\s*(?:м|m)?", low)
    if m:
        out["length_m"] = float(m.group(1).replace(",", "."))
        out["width_m"] = float(m.group(2).replace(",", "."))

    def mm(keys, default):
        for key in keys:
            mmx = _re_ff06.search(key + r".{0,40}?(\d{2,4})\s*мм", low)
            if mmx:
                return int(mmx.group(1))
        return default

    out["slab_mm"] = mm(["толщина", "плита", "бетон"], out["slab_mm"])
    out["sand_mm"] = mm(["песчан", "песок"], out["sand_mm"])
    out["gravel_mm"] = mm(["щеб", "основан"], out["gravel_mm"])
    out["rebar_step_mm"] = mm(["шаг"], out["rebar_step_mm"])

    md = _re_ff06.search(r"(?:ø|Ø|ф|диаметр)\s*(\d{1,2})", low)
    if md:
        out["rebar_diam_mm"] = int(md.group(1))
    mc = _re_ff06.search(r"\b[вbВB]\s*([123456789]\d)\b", text)
    if mc:
        out["concrete_class"] = "B" + mc.group(1)
    ma = _re_ff06.search(r"\bA\s*([245]\d{2})\b", text, _re_ff06.I)
    if ma:
        out["rebar_class"] = "A" + ma.group(1)

    return out

def _ff06_sheet_rows(sheet_register, section):
    rows = []
    for i, sh in enumerate(sheet_register or [], 1):
        if isinstance(sh, dict):
            mark = _ff06_clean_text(sh.get("mark") or section, 20) or section
            num = _ff06_clean_text(sh.get("number") or str(i), 30) or str(i)
            title = _ff06_clean_text(sh.get("title") or sh.get("name") or "", 180)
            if not title:
                title = f"Лист {num}"
            rows.append({"mark": mark, "number": num, "title": title})
        else:
            raw = _ff06_clean_text(sh, 180)
            if not raw:
                continue
            rows.append({"mark": section, "number": str(i), "title": raw})
    return rows

def _ff06_material_rows(materials, data):
    rows = []
    for x in materials or []:
        if isinstance(x, dict):
            name = _ff06_clean_text(x.get("name") or x.get("material") or x.get("title") or "Материал", 180)
            unit = _ff06_clean_text(x.get("unit") or x.get("ед") or "шт", 30)
            qty = x.get("quantity", x.get("qty", x.get("count", "-")))
            note = _ff06_clean_text(x.get("note") or "", 120)
            rows.append((name, unit, qty, note))
        else:
            name = _ff06_clean_text(x, 180)
            if name:
                rows.append((name, "по проекту", "-", "из шаблона"))
    if rows:
        return rows[:80]

    L = float(data["length_m"])
    W = float(data["width_m"])
    area = L * W
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = max(int(data["rebar_step_mm"]), 50)
    bars_x = int((W * 1000) / step) + 1
    bars_y = int((L * 1000) / step) + 1
    rebar_m = round((bars_x * L + bars_y * W) * 2, 1)

    return [
        (f"Бетон {data['concrete_class']}", "м3", round(area * slab / 1000, 3), "фундаментная плита"),
        ("Песчаная подушка", "м3", round(area * sand / 1000, 3), ""),
        ("Щебёночное основание", "м3", round(area * gravel / 1000, 3), ""),
        (f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {step}", "п.м", rebar_m, "верхняя и нижняя сетка"),
    ]

def _ff06_register_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font_path = _ff06_find_font()
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont("ArealDejaVu", font_path))
            return "ArealDejaVu"
        except Exception:
            pass
    return "Helvetica"

def _ff06_draw_frame(c, page_w, page_h, sheet, sheet_no, sheet_total, font):
    from reportlab.lib.units import mm
    c.setLineWidth(0.7)
    c.rect(10*mm, 10*mm, page_w - 20*mm, page_h - 20*mm)
    c.rect(page_w - 190*mm, 10*mm, 180*mm, 40*mm)
    c.line(page_w - 190*mm, 30*mm, page_w - 10*mm, 30*mm)
    c.line(page_w - 80*mm, 10*mm, page_w - 80*mm, 50*mm)
    c.line(page_w - 45*mm, 10*mm, page_w - 45*mm, 50*mm)
    c.setFont(font, 8)
    c.drawString(page_w - 187*mm, 42*mm, "AREAL-NEVA")
    c.drawString(page_w - 187*mm, 34*mm, _ff06_clean_text(sheet.get("title"), 80))
    c.drawString(page_w - 77*mm, 34*mm, f"Лист {sheet_no}")
    c.drawString(page_w - 42*mm, 34*mm, f"Листов {sheet_total}")
    c.setFont(font, 14)
    c.drawString(18*mm, page_h - 22*mm, f"{sheet.get('mark')} {sheet.get('number')} — {sheet.get('title')}")

def _ff06_write_pdf(path, data, template, sheets, material_rows):
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _ff06_register_font()
    page_w, page_h = landscape(A3)
    c = canvas.Canvas(path, pagesize=landscape(A3))

    L = float(data["length_m"])
    W = float(data["width_m"])
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = int(data["rebar_step_mm"])
    rd = int(data["rebar_diam_mm"])
    section = data["section"]

    for idx, sheet in enumerate(sheets, 1):
        _ff06_draw_frame(c, page_w, page_h, sheet, idx, len(sheets), font)
        title_low = (sheet.get("title") or "").lower()

        if any(x in title_low for x in ("общие", "данные", "пояснит", "исходн")):
            y = 260
            lines = [
                f"Проект: {data['project_name']}",
                f"Раздел: {section}",
                f"Основа генерации: сохранённый PROJECT_TEMPLATE_MODEL",
                f"Шаблон: {template.get('_template_file', '')}",
                f"Плита: {L:g} x {W:g} м, толщина {slab} мм",
                f"Основание: щебень {gravel} мм, песчаная подушка {sand} мм",
                f"Бетон: {data['concrete_class']}",
                f"Арматура: {data['rebar_class']} Ø{rd}, шаг {step} мм",
            ]
            c.setFont(font, 10)
            for line in lines:
                c.drawString(25*mm, y*mm, line)
                y -= 8

        elif any(x in title_low for x in ("ведомость лист", "состав лист", "листов")):
            y = 260
            c.setFont(font, 10)
            for j, sh in enumerate(sheets, 1):
                c.drawString(25*mm, y*mm, f"{j}. {sh['mark']} {sh['number']} — {sh['title']}")
                y -= 7

        elif any(x in title_low for x in ("план", "плит", "схема")):
            x0, y0 = 70*mm, 60*mm
            scale = min((page_w - 150*mm) / (L * 1000), 115*mm / (W * 1000))
            rw = L * 1000 * scale
            rh = W * 1000 * scale
            c.setLineWidth(1.1)
            c.rect(x0, y0, rw, rh)
            c.setDash(4, 3)
            c.line(x0, y0 + rh / 2, x0 + rw, y0 + rh / 2)
            c.line(x0 + rw / 2, y0, x0 + rw / 2, y0 + rh)
            c.setDash()
            step_draw = max(0.7*mm, step * scale)
            c.setLineWidth(0.25)
            xx = x0 + step_draw
            while xx < x0 + rw:
                c.line(xx, y0, xx, y0 + rh)
                xx += step_draw
            yy = y0 + step_draw
            while yy < y0 + rh:
                c.line(x0, yy, x0 + rw, yy)
                yy += step_draw
            c.setFont(font, 9)
            c.drawString(x0, y0 - 8*mm, f"{L:g} м")
            c.saveState()
            c.translate(x0 - 8*mm, y0)
            c.rotate(90)
            c.drawString(0, 0, f"{W:g} м")
            c.restoreState()
            c.setFont(font, 10)
            c.drawString(25*mm, 260*mm, f"Армирование: {data['rebar_class']} Ø{rd}, шаг {step} мм")

        elif any(x in title_low for x in ("разрез", "сечени", "1-1")):
            bx, by = 55*mm, 70*mm
            total = slab + gravel + sand
            k = 105*mm / total
            ycur = by
            c.setLineWidth(0.9)
            for name, th, note in [
                ("Фундаментная плита", slab, f"Бетон {data['concrete_class']}"),
                ("Щебёночное основание", gravel, "Щебень"),
                ("Песчаная подушка", sand, "Песок"),
            ]:
                hh = th * k
                c.rect(bx, ycur, 230*mm, hh)
                c.setFont(font, 10)
                c.drawString(bx + 5*mm, ycur + hh/2, f"{name}: {th} мм — {note}")
                ycur += hh
            c.setFont(font, 10)
            c.drawString(25*mm, 240*mm, "Разрез 1-1")

        elif any(x in title_low for x in ("армир", "арматур", "сетка")):
            x0, y0 = 70*mm, 60*mm
            scale = min((page_w - 150*mm) / (L * 1000), 115*mm / (W * 1000))
            rw = L * 1000 * scale
            rh = W * 1000 * scale
            c.setLineWidth(1.0)
            c.rect(x0, y0, rw, rh)
            step_draw = max(1.0*mm, step * scale)
            c.setLineWidth(0.35)
            xx = x0 + step_draw
            while xx < x0 + rw:
                c.line(xx, y0, xx, y0 + rh)
                xx += step_draw
            yy = y0 + step_draw
            while yy < y0 + rh:
                c.line(x0, yy, x0 + rw, yy)
                yy += step_draw
            c.setFont(font, 10)
            c.drawString(25*mm, 260*mm, f"Верхняя и нижняя сетки: {data['rebar_class']} Ø{rd}, шаг {step} мм")

        elif any(x in title_low for x in ("специф", "материал", "ведомость объем", "ведомость объём")):
            y = 260
            c.setFont(font, 10)
            c.drawString(25*mm, y*mm, "№")
            c.drawString(40*mm, y*mm, "Наименование")
            c.drawString(170*mm, y*mm, "Ед")
            c.drawString(195*mm, y*mm, "Кол-во")
            c.drawString(230*mm, y*mm, "Примечание")
            y -= 8
            for j, row in enumerate(material_rows[:28], 1):
                c.drawString(25*mm, y*mm, str(j))
                c.drawString(40*mm, y*mm, _ff06_clean_text(row[0], 70))
                c.drawString(170*mm, y*mm, _ff06_clean_text(row[1], 12))
                c.drawString(195*mm, y*mm, _ff06_clean_text(row[2], 18))
                c.drawString(230*mm, y*mm, _ff06_clean_text(row[3], 50))
                y -= 7

        else:
            y = 250
            c.setFont(font, 10)
            c.drawString(25*mm, y*mm, f"Лист выполнен по структуре шаблона: {sheet['title']}")
            y -= 10
            c.drawString(25*mm, y*mm, f"Раздел: {section}")
            y -= 8
            c.drawString(25*mm, y*mm, f"Параметры: {L:g} x {W:g} м, бетон {data['concrete_class']}")

        c.showPage()

    c.save()
    return path

def _ff06_write_dxf(path, data, sheets, material_rows):
    import ezdxf
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    msp = doc.modelspace()

    for layer, color in [("KJ_PLAN", 7), ("KJ_AXES", 2), ("KJ_REBAR", 3), ("KJ_TEXT", 1), ("KJ_SECTION", 5)]:
        if layer not in doc.layers:
            doc.layers.add(layer, color=color)

    L = float(data["length_m"]) * 1000
    W = float(data["width_m"]) * 1000
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = int(data["rebar_step_mm"])

    msp.add_lwpolyline([(0,0), (L,0), (L,W), (0,W), (0,0)], dxfattribs={"layer": "KJ_PLAN"})
    msp.add_line((L/2, 0), (L/2, W), dxfattribs={"layer": "KJ_AXES"})
    msp.add_line((0, W/2), (L, W/2), dxfattribs={"layer": "KJ_AXES"})

    x = step
    while x < L:
        msp.add_line((x, 0), (x, W), dxfattribs={"layer": "KJ_REBAR"})
        x += step
    y = step
    while y < W:
        msp.add_line((0, y), (L, y), dxfattribs={"layer": "KJ_REBAR"})
        y += step

    msp.add_text(f"FOUNDATION SLAB {L/1000:g} x {W/1000:g} m", dxfattribs={"height": 250, "layer": "KJ_TEXT"}).set_placement((0, -700))
    msp.add_text(f"SLAB {slab} mm / GRAVEL {gravel} mm / SAND {sand} mm", dxfattribs={"height": 250, "layer": "KJ_TEXT"}).set_placement((0, -1100))
    msp.add_text(f"REBAR {data['rebar_class']} D{data['rebar_diam_mm']} STEP {step} mm", dxfattribs={"height": 250, "layer": "KJ_TEXT"}).set_placement((0, -1500))

    sx, sy = 0, -3000
    widths = [slab, gravel, sand]
    names = ["SLAB", "GRAVEL", "SAND"]
    cur = sy
    for name, th in zip(names, widths):
        msp.add_lwpolyline([(sx,cur), (sx+L,cur), (sx+L,cur-th), (sx,cur-th), (sx,cur)], dxfattribs={"layer": "KJ_SECTION"})
        msp.add_text(f"{name} {th} mm", dxfattribs={"height": 220, "layer": "KJ_TEXT"}).set_placement((sx + 300, cur - th/2))
        cur -= th

    doc.saveas(path)
    return path

def _ff06_write_xlsx(path, data, sheets, material_rows, template):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    wb = Workbook()

    ws = wb.active
    ws.title = "Ведомость листов"
    ws.append(["№", "Марка", "Лист", "Наименование"])
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")
    for i, sh in enumerate(sheets, 1):
        ws.append([i, sh["mark"], sh["number"], sh["title"]])
    ws.column_dimensions["D"].width = 80

    ws2 = wb.create_sheet("Спецификация")
    ws2.append(["№", "Наименование", "Ед. изм", "Кол-во", "Примечание"])
    for c in ws2[1]:
        c.font = Font(bold=True)
    for i, row in enumerate(material_rows, 1):
        ws2.append([i, row[0], row[1], row[2], row[3]])
    ws2.column_dimensions["B"].width = 70
    ws2.column_dimensions["E"].width = 50

    ws3 = wb.create_sheet("Параметры")
    for k in ["project_name", "section", "length_m", "width_m", "slab_mm", "sand_mm", "gravel_mm", "concrete_class", "rebar_class", "rebar_diam_mm", "rebar_step_mm"]:
        ws3.append([k, data.get(k)])
    ws3.append(["template_file", template.get("_template_file", "")])
    ws3.column_dimensions["A"].width = 25
    ws3.column_dimensions["B"].width = 80

    wb.save(path)
    return path

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", require_template: bool = True) -> dict:
    data = _ff06_parse_request(raw_input, template_hint)
    template = _ff06_latest_template(topic_id, data.get("section"))

    res = {
        "success": False,
        "engine": "FULLFIX_06_FINAL_PROJECT_TEMPLATE_REPLAY",
        "section": data["section"],
        "pdf_path": "",
        "dxf_path": "",
        "xlsx_path": "",
        "manifest_path": "",
        "pdf_link": "",
        "dxf_link": "",
        "xlsx_link": "",
        "manifest_link": "",
        "template_file": "",
        "sheet_count": 0,
        "error": None,
        "data": data,
    }

    if require_template and not template:
        res["error"] = "PROJECT_TEMPLATE_MODEL_NOT_FOUND"
        return res

    sheets = _ff06_sheet_rows((template or {}).get("sheet_register") or [], data["section"])
    if require_template and not sheets:
        res["error"] = "PROJECT_TEMPLATE_MODEL_HAS_EMPTY_SHEET_REGISTER"
        res["template_file"] = (template or {}).get("_template_file", "")
        return res

    if not sheets:
        res["error"] = "NO_TEMPLATE_SHEETS_NO_PROJECT"
        return res

    material_rows = _ff06_material_rows((template or {}).get("materials") or [], data)

    stamp = _dt_ff06.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_task = _re_ff06.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id or "manual"))[:24]
    out_dir = _Path_ff06(_tempfile_ff06.gettempdir()) / f"areal_project_ff06_{safe_task}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = str(out_dir / f"{data['section']}_PROJECT_{safe_task}.pdf")
    dxf_path = str(out_dir / f"{data['section']}_PROJECT_{safe_task}.dxf")
    xlsx_path = str(out_dir / f"{data['section']}_SPEC_{safe_task}.xlsx")
    manifest_path = str(out_dir / f"{data['section']}_MANIFEST_{safe_task}.json")

    try:
        _ff06_write_pdf(pdf_path, data, template, sheets, material_rows)
        _ff06_write_dxf(dxf_path, data, sheets, material_rows)
        _ff06_write_xlsx(xlsx_path, data, sheets, material_rows, template)

        checks = [
            ("PDF_NOT_CREATED", pdf_path, 2500),
            ("DXF_NOT_CREATED", dxf_path, 500),
            ("XLSX_NOT_CREATED", xlsx_path, 1000),
        ]
        for err, fp, min_size in checks:
            if not _os_ff06.path.exists(fp) or _os_ff06.path.getsize(fp) < min_size:
                res["error"] = err
                return res

        manifest = {
            "schema": "AREAL_PROJECT_ARTIFACT_V3",
            "engine": "FULLFIX_06_FINAL_PROJECT_TEMPLATE_REPLAY",
            "created_at": _dt_ff06.utcnow().isoformat() + "Z",
            "task_id": task_id,
            "topic_id": topic_id,
            "input": raw_input,
            "template_file": template.get("_template_file", ""),
            "sheet_count": len(sheets),
            "sheets": sheets,
            "data": data,
            "artifacts": {
                "pdf_path": pdf_path,
                "dxf_path": dxf_path,
                "xlsx_path": xlsx_path,
            },
        }
        _Path_ff06(manifest_path).write_text(_json_ff06.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        from core.engine_base import upload_artifact_to_drive
        pdf_link = upload_artifact_to_drive(pdf_path, task_id, topic_id)
        dxf_link = upload_artifact_to_drive(dxf_path, task_id, topic_id)
        xlsx_link = upload_artifact_to_drive(xlsx_path, task_id, topic_id)
        manifest_link = upload_artifact_to_drive(manifest_path, task_id, topic_id)

        if not pdf_link:
            res["error"] = "PDF_UPLOAD_FAILED"
            return res
        if not dxf_link:
            res["error"] = "DXF_UPLOAD_FAILED"
            return res
        if not xlsx_link:
            res["error"] = "XLSX_UPLOAD_FAILED"
            return res

        res.update({
            "success": True,
            "pdf_path": pdf_path,
            "dxf_path": dxf_path,
            "xlsx_path": xlsx_path,
            "manifest_path": manifest_path,
            "pdf_link": str(pdf_link),
            "dxf_link": str(dxf_link),
            "xlsx_link": str(xlsx_link),
            "manifest_link": str(manifest_link or ""),
            "template_file": template.get("_template_file", ""),
            "sheet_count": len(sheets),
        })
        return res

    except Exception as e:
        res["error"] = str(e)[:500]
        return res

# === END FULLFIX_06_FINAL_PROJECT_TEMPLATE_REPLAY ===

# === FULLFIX_07_PROJECT_DESIGN_CLOSURE ===
import os as _os_ff07
import re as _re_ff07
import json as _json_ff07
import glob as _glob_ff07
import math as _math_ff07
import tempfile as _tempfile_ff07
from pathlib import Path as _Path_ff07
from datetime import datetime as _dt_ff07

def _ff07_clean(v, limit=5000):
    return str(v or "").replace("\x00", " ").strip()[:limit]

def _ff07_template_files():
    base = "/root/.areal-neva-core/data/project_templates"
    return sorted(
        _glob_ff07.glob(_os_ff07.path.join(base, "PROJECT_TEMPLATE_MODEL__*.json")),
        key=lambda x: _os_ff07.path.getmtime(x),
        reverse=True,
    )

def _ff07_load_latest_template(topic_id=0, preferred_section=""):
    files = _ff07_template_files()
    best = {}
    preferred_section = _ff07_clean(preferred_section).upper()
    topic_id = int(topic_id or 0)

    for fp in files:
        try:
            data = _json_ff07.loads(_Path_ff07(fp).read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            data["_template_file"] = fp
            pt = _ff07_clean(data.get("project_type")).upper()
            dtid = int(data.get("topic_id", 0) or 0)

            if topic_id and dtid == topic_id and preferred_section and pt == preferred_section:
                return data
            if preferred_section and pt == preferred_section and not best:
                best = data
            if topic_id and dtid == topic_id and not best:
                best = data
            if not best:
                best = data
        except Exception:
            continue

    return best or {}

def _ff07_parse_request(raw_input, template_hint=""):
    text = _ff07_clean(raw_input, 12000)
    low = text.lower()

    data = {
        "section": "КЖ",
        "project_name": "Проект фундаментной плиты",
        "length_m": 10.0,
        "width_m": 10.0,
        "slab_mm": 200,
        "sand_mm": 300,
        "gravel_mm": 100,
        "concrete_class": "B25",
        "rebar_class": "A500",
        "rebar_diam_mm": 12,
        "rebar_step_mm": 200,
        "raw_input": text,
        "template_hint": template_hint or "",
    }

    if any(x in low for x in ("кров", "строп", "кд")) and not any(x in low for x in ("фундамент", "плит")):
        data["section"] = "КД"
        data["project_name"] = "Проект кровли"
    if any(x in low for x in ("архитектур", " ар ", "раздел ар")) and not any(x in low for x in ("фундамент", "плит", "кров")):
        data["section"] = "АР"
        data["project_name"] = "Архитектурный раздел"
    if any(x in low for x in ("фундамент", "плит", "кж")):
        data["section"] = "КЖ"
        data["project_name"] = "Проект фундаментной плиты"

    m = _re_ff07.search(r"(\d+(?:[,.]\d+)?)\s*[xх×]\s*(\d+(?:[,.]\d+)?)\s*(?:м|m)?", low)
    if m:
        data["length_m"] = float(m.group(1).replace(",", "."))
        data["width_m"] = float(m.group(2).replace(",", "."))

    def find_mm(keys, default):
        for key in keys:
            mm = _re_ff07.search(key + r".{0,45}?(\d{2,4})\s*мм", low)
            if mm:
                return int(mm.group(1))
        return default

    data["slab_mm"] = find_mm(("толщина", "плита", "бетон"), data["slab_mm"])
    data["sand_mm"] = find_mm(("песчан", "песок"), data["sand_mm"])
    data["gravel_mm"] = find_mm(("щеб", "основан"), data["gravel_mm"])
    data["rebar_step_mm"] = find_mm(("шаг",), data["rebar_step_mm"])

    md = _re_ff07.search(r"(?:ø|Ø|ф|диаметр)\s*(\d{1,2})", text, _re_ff07.I)
    if md:
        data["rebar_diam_mm"] = int(md.group(1))

    mc = _re_ff07.search(r"\b[вbВB]\s*([123456789]\d)\b", text)
    if mc:
        data["concrete_class"] = "B" + mc.group(1)

    ma = _re_ff07.search(r"\b[аaАA]\s*([245]\d{2})\b", text)
    if ma:
        data["rebar_class"] = "A" + ma.group(1)

    return data

def _ff07_dedup_titles(rows):
    out, seen = [], set()
    for row in rows:
        title = _ff07_clean(row.get("title"), 160)
        key = title.lower()
        if not title or key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out

def _ff07_sheet_rows_from_template(template, section, data):
    raw = template.get("sheet_register") or []
    rows = []

    for i, sh in enumerate(raw, 1):
        if isinstance(sh, dict):
            rows.append({
                "mark": _ff07_clean(sh.get("mark") or section, 20) or section,
                "number": _ff07_clean(sh.get("number") or str(i), 30) or str(i),
                "title": _ff07_clean(sh.get("title") or sh.get("name") or "", 180),
                "source": "sheet_register",
            })
        else:
            rows.append({
                "mark": section,
                "number": str(i),
                "title": _ff07_clean(sh, 180),
                "source": "sheet_register_raw",
            })

    rows = _ff07_dedup_titles(rows)

    if len(rows) >= 8:
        return rows

    sections = []
    for x in template.get("sections") or []:
        if isinstance(x, dict):
            t = _ff07_clean(x.get("title") or x.get("name") or x.get("text"), 180)
        else:
            t = _ff07_clean(x, 180)
        if t:
            sections.append(t)

    canonical = []
    if section == "КЖ":
        canonical = [
            "Общие данные",
            "Ведомость листов",
            "План фундаментной плиты",
            "Разрез 1-1",
            "Схема армирования нижней сетки",
            "Схема армирования верхней сетки",
            "Узлы армирования и защитные слои",
            "Спецификация материалов",
            "Ведомость расхода стали",
            "Пояснительная записка",
        ]
    elif section == "КД":
        canonical = [
            "Общие данные",
            "Ведомость листов",
            "План кровли",
            "План стропильной системы",
            "Разрезы кровли",
            "Узлы кровли",
            "Схема обрешётки",
            "Спецификация пиломатериалов",
            "Ведомость элементов",
            "Пояснительная записка",
        ]
    elif section == "АР":
        canonical = [
            "Общие данные",
            "Ведомость листов",
            "План этажа",
            "Фасады",
            "Разрезы",
            "План кровли",
            "Экспликация помещений",
            "Спецификация заполнения проёмов",
            "Узлы",
            "Пояснительная записка",
        ]
    else:
        canonical = [
            "Общие данные",
            "Ведомость листов",
            "План",
            "Разрез",
            "Схема",
            "Узлы",
            "Спецификация материалов",
            "Пояснительная записка",
        ]

    for title in canonical:
        rows.append({
            "mark": section,
            "number": str(len(rows) + 1),
            "title": title,
            "source": "canonical_required",
        })

    for sec in sections:
        low = sec.lower()
        if any(k in low for k in ("общие данные", "ведомость", "план", "фасад", "разрез", "узел", "схема", "спецификац", "расчет", "расчёт", "конструктив")):
            rows.append({
                "mark": section,
                "number": str(len(rows) + 1),
                "title": sec[:150],
                "source": "template_sections",
            })

    rows = _ff07_dedup_titles(rows)

    renumbered = []
    for i, row in enumerate(rows[:24], 1):
        row = dict(row)
        row["mark"] = row.get("mark") or section
        row["number"] = str(i)
        renumbered.append(row)

    return renumbered

def _ff07_material_rows(template, data):
    rows = []
    for x in template.get("materials") or []:
        if isinstance(x, dict):
            rows.append({
                "name": _ff07_clean(x.get("name") or x.get("material") or x.get("title") or "Материал", 180),
                "unit": _ff07_clean(x.get("unit") or "шт", 30),
                "qty": x.get("qty", x.get("quantity", "-")),
                "note": _ff07_clean(x.get("note") or "из шаблона", 120),
            })
        else:
            t = _ff07_clean(x, 180)
            if t:
                rows.append({"name": t, "unit": "по проекту", "qty": "-", "note": "из шаблона"})

    L = float(data["length_m"])
    W = float(data["width_m"])
    area = L * W
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = max(int(data["rebar_step_mm"]), 50)
    bars_x = int((W * 1000) / step) + 1
    bars_y = int((L * 1000) / step) + 1
    rebar_m = round((bars_x * L + bars_y * W) * 2, 1)

    calc_rows = [
        {"name": f"Бетон {data['concrete_class']}", "unit": "м3", "qty": round(area * slab / 1000, 3), "note": "фундаментная плита"},
        {"name": "Песчаная подушка", "unit": "м3", "qty": round(area * sand / 1000, 3), "note": ""},
        {"name": "Щебёночное основание", "unit": "м3", "qty": round(area * gravel / 1000, 3), "note": ""},
        {"name": f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {step}", "unit": "п.м", "qty": rebar_m, "note": "верхняя и нижняя сетка"},
    ]

    names = {r["name"].lower() for r in rows}
    for r in calc_rows:
        if r["name"].lower() not in names:
            rows.append(r)

    return rows[:80]

def _ff07_register_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for fp in candidates:
        if _os_ff07.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("ArealDejaVu", fp))
                return "ArealDejaVu"
            except Exception:
                pass
    return "Helvetica"

def _ff07_draw_frame(c, page_w, page_h, sheet, sheet_no, sheet_total, font):
    from reportlab.lib.units import mm

    c.setLineWidth(0.7)
    c.rect(10 * mm, 10 * mm, page_w - 20 * mm, page_h - 20 * mm)
    c.rect(page_w - 190 * mm, 10 * mm, 180 * mm, 42 * mm)
    c.line(page_w - 190 * mm, 32 * mm, page_w - 10 * mm, 32 * mm)
    c.line(page_w - 80 * mm, 10 * mm, page_w - 80 * mm, 52 * mm)
    c.line(page_w - 45 * mm, 10 * mm, page_w - 45 * mm, 52 * mm)

    c.setFont(font, 8)
    c.drawString(page_w - 187 * mm, 44 * mm, "AREAL-NEVA")
    c.drawString(page_w - 187 * mm, 36 * mm, _ff07_clean(sheet.get("title"), 80))
    c.drawString(page_w - 77 * mm, 36 * mm, f"Лист {sheet_no}")
    c.drawString(page_w - 42 * mm, 36 * mm, f"Листов {sheet_total}")

    c.setFont(font, 14)
    c.drawString(18 * mm, page_h - 22 * mm, f"{sheet.get('mark')} {sheet.get('number')} — {sheet.get('title')}")

def _ff07_write_pdf(path, data, template, sheets, materials):
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    font = _ff07_register_font()
    page_w, page_h = landscape(A3)
    c = canvas.Canvas(path, pagesize=landscape(A3))

    L = float(data["length_m"])
    W = float(data["width_m"])
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = int(data["rebar_step_mm"])
    rd = int(data["rebar_diam_mm"])
    section = data["section"]

    for idx, sheet in enumerate(sheets, 1):
        title = sheet.get("title") or ""
        low = title.lower()
        _ff07_draw_frame(c, page_w, page_h, sheet, idx, len(sheets), font)

        if any(x in low for x in ("общие", "данные", "пояснит", "исходн")):
            y = 260
            lines = [
                f"Проект: {data['project_name']}",
                f"Раздел: {section}",
                "Тип выдачи: PDF + DXF + XLSX + MANIFEST",
                f"Шаблон: {template.get('_template_file', '')}",
                f"Плита: {L:g} x {W:g} м, толщина {slab} мм",
                f"Основание: щебень {gravel} мм, песчаная подушка {sand} мм",
                f"Бетон: {data['concrete_class']}",
                f"Арматура: {data['rebar_class']} Ø{rd}, шаг {step} мм",
                f"Листов: {len(sheets)}",
            ]
            c.setFont(font, 10)
            for line in lines:
                c.drawString(25 * mm, y * mm, line)
                y -= 8

        elif any(x in low for x in ("ведомость лист", "состав лист", "листов")):
            y = 260
            c.setFont(font, 10)
            for j, sh in enumerate(sheets, 1):
                c.drawString(25 * mm, y * mm, f"{j}. {sh['mark']} {sh['number']} — {sh['title']}")
                y -= 7
                if y < 35:
                    c.showPage()
                    _ff07_draw_frame(c, page_w, page_h, sheet, idx, len(sheets), font)
                    y = 260

        elif any(x in low for x in ("план", "плит", "схема")) and not any(x in low for x in ("армир", "арматур")):
            x0, y0 = 70 * mm, 60 * mm
            scale = min((page_w - 150 * mm) / (L * 1000), 115 * mm / (W * 1000))
            rw = L * 1000 * scale
            rh = W * 1000 * scale

            c.setLineWidth(1.1)
            c.rect(x0, y0, rw, rh)
            c.setDash(4, 3)
            c.line(x0, y0 + rh / 2, x0 + rw, y0 + rh / 2)
            c.line(x0 + rw / 2, y0, x0 + rw / 2, y0 + rh)
            c.setDash()

            step_draw = max(0.7 * mm, step * scale)
            c.setLineWidth(0.25)

            xx = x0 + step_draw
            while xx < x0 + rw:
                c.line(xx, y0, xx, y0 + rh)
                xx += step_draw

            yy = y0 + step_draw
            while yy < y0 + rh:
                c.line(x0, yy, x0 + rw, yy)
                yy += step_draw

            c.setFont(font, 9)
            c.drawString(x0, y0 - 8 * mm, f"{L:g} м")
            c.saveState()
            c.translate(x0 - 8 * mm, y0)
            c.rotate(90)
            c.drawString(0, 0, f"{W:g} м")
            c.restoreState()

            c.setFont(font, 10)
            c.drawString(25 * mm, 260 * mm, f"Армирование: {data['rebar_class']} Ø{rd}, шаг {step} мм")

        elif any(x in low for x in ("разрез", "сечени", "1-1")):
            bx, by = 55 * mm, 70 * mm
            total = slab + gravel + sand
            k = 105 * mm / total
            ycur = by

            c.setLineWidth(0.9)
            for name, th, note in [
                ("Фундаментная плита", slab, f"Бетон {data['concrete_class']}"),
                ("Щебёночное основание", gravel, "Щебень"),
                ("Песчаная подушка", sand, "Песок"),
            ]:
                hh = th * k
                c.rect(bx, ycur, 230 * mm, hh)
                c.setFont(font, 10)
                c.drawString(bx + 5 * mm, ycur + hh / 2, f"{name}: {th} мм — {note}")
                ycur += hh

            c.setFont(font, 10)
            c.drawString(25 * mm, 240 * mm, "Разрез 1-1")

        elif any(x in low for x in ("армир", "арматур", "сетка")):
            x0, y0 = 70 * mm, 60 * mm
            scale = min((page_w - 150 * mm) / (L * 1000), 115 * mm / (W * 1000))
            rw = L * 1000 * scale
            rh = W * 1000 * scale

            c.setLineWidth(1.0)
            c.rect(x0, y0, rw, rh)

            step_draw = max(1.0 * mm, step * scale)
            c.setLineWidth(0.35)

            xx = x0 + step_draw
            while xx < x0 + rw:
                c.line(xx, y0, xx, y0 + rh)
                xx += step_draw

            yy = y0 + step_draw
            while yy < y0 + rh:
                c.line(x0, yy, x0 + rw, yy)
                yy += step_draw

            c.setFont(font, 10)
            c.drawString(25 * mm, 260 * mm, f"Верхняя и нижняя сетки: {data['rebar_class']} Ø{rd}, шаг {step} мм")

        elif any(x in low for x in ("специф", "материал", "ведомость расход", "ведомость объем", "ведомость объём", "стали")):
            y = 260
            c.setFont(font, 10)
            c.drawString(25 * mm, y * mm, "№")
            c.drawString(40 * mm, y * mm, "Наименование")
            c.drawString(175 * mm, y * mm, "Ед")
            c.drawString(200 * mm, y * mm, "Кол-во")
            c.drawString(235 * mm, y * mm, "Примечание")
            y -= 8

            for j, row in enumerate(materials[:32], 1):
                c.drawString(25 * mm, y * mm, str(j))
                c.drawString(40 * mm, y * mm, _ff07_clean(row["name"], 70))
                c.drawString(175 * mm, y * mm, _ff07_clean(row["unit"], 12))
                c.drawString(200 * mm, y * mm, _ff07_clean(row["qty"], 18))
                c.drawString(235 * mm, y * mm, _ff07_clean(row["note"], 50))
                y -= 7

        elif any(x in low for x in ("узел", "защитн", "слои")):
            c.setFont(font, 10)
            y = 250
            for line in [
                f"Защитный слой бетона принят по СП 63.13330.2018",
                f"Арматура {data['rebar_class']} Ø{rd}, шаг {step} мм",
                "Стыковка и нахлёсты выполнять по рабочей документации",
                "Геометрия узлов уточняется по месту и исполнительным размерам",
            ]:
                c.drawString(25 * mm, y * mm, line)
                y -= 9

        else:
            c.setFont(font, 10)
            y = 250
            for line in [
                f"Лист выполнен в составе комплекта: {title}",
                f"Раздел: {section}",
                f"Параметры: {L:g} x {W:g} м",
                f"Бетон: {data['concrete_class']}",
                f"Шаблон: {template.get('_template_file', '')}",
            ]:
                c.drawString(25 * mm, y * mm, line)
                y -= 8

        c.showPage()

    c.save()
    return path

def _ff07_write_dxf(path, data, sheets, materials):
    import ezdxf

    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    msp = doc.modelspace()

    for layer, color in [
        ("KJ_PLAN", 7),
        ("KJ_AXES", 2),
        ("KJ_REBAR", 3),
        ("KJ_TEXT", 1),
        ("KJ_SECTION", 5),
        ("KJ_SHEETS", 4),
    ]:
        if layer not in doc.layers:
            doc.layers.add(layer, color=color)

    L = float(data["length_m"]) * 1000
    W = float(data["width_m"]) * 1000
    slab = int(data["slab_mm"])
    sand = int(data["sand_mm"])
    gravel = int(data["gravel_mm"])
    step = max(int(data["rebar_step_mm"]), 50)

    msp.add_lwpolyline([(0, 0), (L, 0), (L, W), (0, W), (0, 0)], dxfattribs={"layer": "KJ_PLAN"})
    msp.add_line((L / 2, 0), (L / 2, W), dxfattribs={"layer": "KJ_AXES"})
    msp.add_line((0, W / 2), (L, W / 2), dxfattribs={"layer": "KJ_AXES"})

    x = step
    while x < L:
        msp.add_line((x, 0), (x, W), dxfattribs={"layer": "KJ_REBAR"})
        x += step

    y = step
    while y < W:
        msp.add_line((0, y), (L, y), dxfattribs={"layer": "KJ_REBAR"})
        y += step

    msp.add_text(
        f"FOUNDATION SLAB {L/1000:g} x {W/1000:g} m",
        dxfattribs={"height": 250, "layer": "KJ_TEXT"},
    ).set_placement((0, -700))

    msp.add_text(
        f"SLAB {slab} mm / GRAVEL {gravel} mm / SAND {sand} mm",
        dxfattribs={"height": 250, "layer": "KJ_TEXT"},
    ).set_placement((0, -1100))

    msp.add_text(
        f"REBAR {data['rebar_class']} D{data['rebar_diam_mm']} STEP {step} mm",
        dxfattribs={"height": 250, "layer": "KJ_TEXT"},
    ).set_placement((0, -1500))

    sx, sy = 0, -3000
    cur = sy
    for name, th in [("SLAB", slab), ("GRAVEL", gravel), ("SAND", sand)]:
        msp.add_lwpolyline([(sx, cur), (sx + L, cur), (sx + L, cur - th), (sx, cur - th), (sx, cur)], dxfattribs={"layer": "KJ_SECTION"})
        msp.add_text(f"{name} {th} mm", dxfattribs={"height": 220, "layer": "KJ_TEXT"}).set_placement((sx + 300, cur - th / 2))
        cur -= th

    sheet_x = L + 2000
    sheet_y = 0
    for i, sh in enumerate(sheets, 1):
        msp.add_text(
            f"{i}. {sh['mark']} {sh['number']} {sh['title']}",
            dxfattribs={"height": 220, "layer": "KJ_SHEETS"},
        ).set_placement((sheet_x, sheet_y - i * 350))

    doc.saveas(path)
    return path

def _ff07_write_xlsx(path, data, sheets, materials, template):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment

    wb = Workbook()

    ws = wb.active
    ws.title = "Ведомость листов"
    ws.append(["№", "Марка", "Лист", "Наименование", "Источник"])
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")

    for i, sh in enumerate(sheets, 1):
        ws.append([i, sh["mark"], sh["number"], sh["title"], sh.get("source", "")])

    ws.column_dimensions["D"].width = 80
    ws.column_dimensions["E"].width = 25

    ws2 = wb.create_sheet("Спецификация")
    ws2.append(["№", "Наименование", "Ед. изм", "Кол-во", "Примечание"])
    for c in ws2[1]:
        c.font = Font(bold=True)

    for i, row in enumerate(materials, 1):
        ws2.append([i, row["name"], row["unit"], row["qty"], row["note"]])

    ws2.column_dimensions["B"].width = 70
    ws2.column_dimensions["E"].width = 50

    ws3 = wb.create_sheet("Параметры")
    for k in ["project_name", "section", "length_m", "width_m", "slab_mm", "sand_mm", "gravel_mm", "concrete_class", "rebar_class", "rebar_diam_mm", "rebar_step_mm"]:
        ws3.append([k, data.get(k)])
    ws3.append(["template_file", template.get("_template_file", "")])
    ws3.append(["engine", "FULLFIX_07_PROJECT_DESIGN_CLOSURE"])
    ws3.column_dimensions["A"].width = 28
    ws3.column_dimensions["B"].width = 90

    wb.save(path)
    return path

def _ff07_verify_pdf_pages(path, min_pages):
    try:
        from pypdf import PdfReader
        return len(PdfReader(path).pages) >= int(min_pages)
    except Exception:
        return _os_ff07.path.exists(path) and _os_ff07.path.getsize(path) > 3000

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", require_template: bool = True) -> dict:
    data = _ff07_parse_request(raw_input, template_hint)
    template = _ff07_load_latest_template(topic_id, data.get("section"))

    res = {
        "success": False,
        "engine": "FULLFIX_07_PROJECT_DESIGN_CLOSURE",
        "section": data["section"],
        "pdf_path": "",
        "dxf_path": "",
        "xlsx_path": "",
        "manifest_path": "",
        "pdf_link": "",
        "dxf_link": "",
        "xlsx_link": "",
        "manifest_link": "",
        "template_file": "",
        "sheet_count": 0,
        "error": None,
        "data": data,
    }

    if require_template and not template:
        res["error"] = "PROJECT_TEMPLATE_MODEL_NOT_FOUND"
        return res

    sheets = _ff07_sheet_rows_from_template(template or {}, data["section"], data)
    materials = _ff07_material_rows(template or {}, data)

    if len(sheets) < 8:
        res["error"] = f"SHEET_REGISTER_TOO_SMALL:{len(sheets)}"
        res["template_file"] = (template or {}).get("_template_file", "")
        res["sheet_count"] = len(sheets)
        return res

    stamp = _dt_ff07.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_task = _re_ff07.sub(r"[^A-Za-z0-9_-]+", "_", str(task_id or "manual"))[:24]
    out_dir = _Path_ff07(_tempfile_ff07.gettempdir()) / f"areal_project_ff07_{safe_task}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = str(out_dir / f"{data['section']}_PROJECT_{safe_task}.pdf")
    dxf_path = str(out_dir / f"{data['section']}_PROJECT_{safe_task}.dxf")
    xlsx_path = str(out_dir / f"{data['section']}_SPEC_{safe_task}.xlsx")
    manifest_path = str(out_dir / f"{data['section']}_MANIFEST_{safe_task}.json")

    try:
        _ff07_write_pdf(pdf_path, data, template, sheets, materials)
        _ff07_write_dxf(dxf_path, data, sheets, materials)
        _ff07_write_xlsx(xlsx_path, data, sheets, materials, template)

        checks = [
            ("PDF_NOT_CREATED", pdf_path, 3000),
            ("DXF_NOT_CREATED", dxf_path, 500),
            ("XLSX_NOT_CREATED", xlsx_path, 1000),
        ]
        for err, fp, min_size in checks:
            if not _os_ff07.path.exists(fp) or _os_ff07.path.getsize(fp) < min_size:
                res["error"] = err
                return res

        if not _ff07_verify_pdf_pages(pdf_path, len(sheets)):
            res["error"] = "PDF_PAGE_COUNT_INVALID"
            return res

        manifest = {
            "schema": "AREAL_PROJECT_ARTIFACT_V4",
            "engine": "FULLFIX_07_PROJECT_DESIGN_CLOSURE",
            "created_at": _dt_ff07.utcnow().isoformat() + "Z",
            "task_id": task_id,
            "topic_id": topic_id,
            "input": raw_input,
            "template_file": template.get("_template_file", ""),
            "template_project_type": template.get("project_type", ""),
            "sheet_count": len(sheets),
            "sheets": sheets,
            "materials": materials,
            "data": data,
            "artifacts": {
                "pdf_path": pdf_path,
                "dxf_path": dxf_path,
                "xlsx_path": xlsx_path,
            },
        }
        _Path_ff07(manifest_path).write_text(_json_ff07.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        from core.engine_base import upload_artifact_to_drive

        pdf_link = upload_artifact_to_drive(pdf_path, task_id, topic_id)
        dxf_link = upload_artifact_to_drive(dxf_path, task_id, topic_id)
        xlsx_link = upload_artifact_to_drive(xlsx_path, task_id, topic_id)
        manifest_link = upload_artifact_to_drive(manifest_path, task_id, topic_id)

        if not pdf_link:
            res["error"] = "PDF_UPLOAD_FAILED"
            return res
        if not dxf_link:
            res["error"] = "DXF_UPLOAD_FAILED"
            return res
        if not xlsx_link:
            res["error"] = "XLSX_UPLOAD_FAILED"
            return res

        res.update({
            "success": True,
            "pdf_path": pdf_path,
            "dxf_path": dxf_path,
            "xlsx_path": xlsx_path,
            "manifest_path": manifest_path,
            "pdf_link": str(pdf_link),
            "dxf_link": str(dxf_link),
            "xlsx_link": str(xlsx_link),
            "manifest_link": str(manifest_link or ""),
            "template_file": template.get("_template_file", ""),
            "sheet_count": len(sheets),
            "data": {**data, "template_file": template.get("_template_file", "")},
        })
        return res

    except Exception as e:
        res["error"] = str(e)[:700]
        return res

# === END FULLFIX_07_PROJECT_DESIGN_CLOSURE ===


# === FULLFIX_07_PROJECT_ENGINE_OVERRIDE ===
try:
    from core.cad_project_engine import (
        create_project_pdf_dxf_artifact,
        create_full_project_package,
        is_project_design_request,
        format_project_result_message,
    )
except Exception:
    pass
# === END FULLFIX_07_PROJECT_ENGINE_OVERRIDE ===


# === FULLFIX_08_PROJECT_SIGNATURE_COMPAT_OVERRIDE ===
# Final public project API used by task_worker
# Accepts any old/new call signature and delegates to CAD closure engine

try:
    from core.cad_project_engine import (
        create_project_pdf_dxf_artifact as _ff08_cad_create_project_pdf_dxf_artifact,
        create_full_project_documentation as _ff08_cad_create_full_project_documentation,
    )

    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff08_cad_create_project_pdf_dxf_artifact(
            raw_input,
            task_id,
            int(topic_id or 0),
            str(template_hint or ""),
            *args,
            **kwargs
        )

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff08_cad_create_full_project_documentation(
            raw_input,
            task_id,
            int(topic_id or 0),
            str(template_hint or ""),
            *args,
            **kwargs
        )

except Exception as _ff08_import_error:
    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return {
            "success": False,
            "engine": "FULLFIX_08_PROJECT_SIGNATURE_COMPAT_OVERRIDE",
            "error": "CAD_PROJECT_ENGINE_IMPORT_FAILED: " + str(_ff08_import_error)[:300],
        }

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

# === END FULLFIX_08_PROJECT_SIGNATURE_COMPAT_OVERRIDE ===



# === FULLFIX_09_PROJECT_TEMPLATE_REGISTER_PUBLIC_OVERRIDE ===
try:
    from core.cad_project_engine import (
        create_project_pdf_dxf_artifact as _ff09_create_project_pdf_dxf_artifact,
        create_full_project_documentation as _ff09_create_full_project_documentation,
    )

    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff09_create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff09_create_full_project_documentation(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

except Exception as _ff09_public_e:
    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return {
            "success": False,
            "engine": "FULLFIX_09_PROJECT_TEMPLATE_REGISTER_PUBLIC_OVERRIDE",
            "error": str(_ff09_public_e)[:500],
        }

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

# === END FULLFIX_09_PROJECT_TEMPLATE_REGISTER_PUBLIC_OVERRIDE ===


# === FULLFIX_10_TOTAL_CLOSURE_PUBLIC_PROJECT_OVERRIDE ===
try:
    from core.cad_project_engine import (
        create_project_pdf_dxf_artifact as _ff10_create_project_pdf_dxf_artifact,
        create_full_project_documentation as _ff10_create_full_project_documentation,
    )

    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff10_create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff10_create_full_project_documentation(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

except Exception as _ff10_project_override_error:
    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return {
            "success": False,
            "engine": "FULLFIX_10_TOTAL_CLOSURE_PUBLIC_PROJECT_OVERRIDE",
            "error": str(_ff10_project_override_error)[:300],
        }

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

# === END FULLFIX_10_TOTAL_CLOSURE_PUBLIC_PROJECT_OVERRIDE ===


# === FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT_PUBLIC_OVERRIDE ===
try:
    from core.orchestra_closure_engine import create_compact_project_documentation as _ff12_compact_project

    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff12_compact_project(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff12_compact_project(raw_input, task_id, topic_id, template_hint, *args, **kwargs)
except Exception:
    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return {"success": False, "engine": "FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT_PUBLIC_OVERRIDE", "error": "COMPACT_ENGINE_IMPORT_FAILED"}

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)
# === END FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT_PUBLIC_OVERRIDE ===


# === DWG_DXF_PROJECT_ENGINE_ADAPTER_V1 ===
async def process_dwg_dxf_project_file(file_path: str, task_id: str, topic_id: int, raw_input: str = "", file_name: str = "", mime_type: str = "") -> dict:
    """
    Project-engine adapter for DWG/DXF files.
    This keeps design files inside the project contour instead of returning None in artifact_pipeline.
    """
    try:
        from core.dwg_engine import process_drawing_file
        res = process_drawing_file(
            local_path=file_path,
            file_name=file_name or file_path,
            mime_type=mime_type,
            user_text=raw_input,
            topic_role="проектирование",
            task_id=task_id,
            topic_id=topic_id,
        )
        if not res.get("success"):
            return {"success": False, "error": res.get("error") or "DWG_DXF_PROJECT_FAILED"}
        return {
            "success": True,
            "engine": "DWG_DXF_PROJECT_CLOSE_V1",
            "section": ((res.get("model") or {}).get("section") or "кр"),
            "summary": res.get("summary") or "",
            "artifact_path": res.get("artifact_path") or "",
            "docx_path": res.get("docx_path") or "",
            "xlsx_path": res.get("xlsx_path") or "",
            "json_path": res.get("json_path") or "",
            "model": res.get("model") or {},
        }
    except Exception as e:
        return {"success": False, "error": f"DWG_DXF_PROJECT_ENGINE_ADAPTER_ERR:{e}"}
# === END_DWG_DXF_PROJECT_ENGINE_ADAPTER_V1 ===



# === REAL_GAPS_CLOSE_V2_PROJECT ===
# === PROJECT_LOAD_CALC_REGION_FROM_INPUT_V1 ===
_PROJECT_REGION_MAP_V2 = {
    "москва": 3, "московск": 3, "подмосков": 3,
    "петербург": 3, "санкт-петербург": 3, "ленинград": 3, "спб": 3,
    "нижний новгород": 3, "нижегородск": 3, "воронеж": 3, "рязань": 3,
    "тула": 3, "орёл": 3, "орел": 3, "калуга": 3, "ярославль": 3,
    "кострома": 3, "иваново": 3, "владимир": 3, "смоленск": 3,
    "брянск": 3, "тверь": 3,
    "краснодар": 2, "сочи": 2, "ростов": 2, "ставрополь": 2,
    "астрахань": 2, "волгоград": 2, "крым": 2, "симферополь": 2,
    "казань": 3, "татарстан": 3, "самара": 3, "саратов": 3,
    "ульяновск": 3, "пенза": 3, "оренбург": 4,
    "екатеринбург": 4, "свердловск": 4, "челябинск": 4,
    "пермь": 4, "тюмень": 4, "уфа": 4, "башкортостан": 4,
    "новосибирск": 5, "омск": 5, "томск": 5, "кемерово": 5,
    "красноярск": 5, "иркутск": 5, "бурятия": 5, "барнаул": 5,
    "якутия": 6, "якутск": 6, "хабаровск": 6, "сахалин": 6,
    "мурманск": 6, "ямал": 6, "ямало": 6,
    "магадан": 7, "чукотка": 7, "камчатка": 7, "норильск": 7, "воркута": 7,
}

def parse_region_from_text(text: str, default: int = 3) -> int:
    import re
    low = str(text or "").lower()
    m = re.search(r"район\s*([1-8])", low)
    if m:
        return int(m.group(1))
    m = re.search(r"([1-8])\s*-?\s*й?\s*снеговой", low)
    if m:
        return int(m.group(1))
    for key, region in _PROJECT_REGION_MAP_V2.items():
        if key in low:
            return region
    return default

def calc_loads_from_text(text: str, default_region: int = 3) -> dict:
    return calc_loads(parse_region_from_text(text, default_region))

_rgc2_orig_project_create = create_project_pdf_dxf_artifact

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    region = parse_region_from_text(str(raw_input or "") + " " + str(template_hint or ""))
    forced_input = str(raw_input or "")
    if "снеговой район" not in forced_input.lower() and "район " not in forced_input.lower():
        forced_input = forced_input + "\n" + "Снеговой район " + str(region) + " по автоматически определённому региону"
    try:
        result = await _rgc2_orig_project_create(
            raw_input=forced_input,
            task_id=task_id,
            topic_id=topic_id,
            template_hint=template_hint,
            *args,
            **kwargs,
        )
    except TypeError:
        try:
            result = await _rgc2_orig_project_create(forced_input, task_id, topic_id, template_hint)
        except TypeError:
            result = await _rgc2_orig_project_create(forced_input, task_id, topic_id)

    if isinstance(result, dict):
        result["region_detected"] = region
        result["loads_detected"] = calc_loads(region)
        model = result.get("model") or result.get("data")
        if isinstance(model, dict):
            model.setdefault("region", region)
            model.setdefault("loads", calc_loads(region))
    return result
# === END_PROJECT_LOAD_CALC_REGION_FROM_INPUT_V1 ===
# === END_REAL_GAPS_CLOSE_V2_PROJECT ===

# === PROJECT_ENGINE_FALLBACK_SHEET_REGISTER_V1 ===
# If template sheet_register is absent or too small, project engine must not fail.
# Default KЖ sheet register is used as safe fallback for project artifact generation.

_PROJECT_ENGINE_DEFAULT_KZH_SHEET_REGISTER_V1 = [
    {"mark": "КЖ", "number": "1", "title": "Общие данные"},
    {"mark": "КЖ", "number": "2", "title": "Схема расположения элементов"},
    {"mark": "КЖ", "number": "3", "title": "Армирование. Нижняя сетка"},
    {"mark": "КЖ", "number": "4", "title": "Армирование. Верхняя сетка"},
    {"mark": "КЖ", "number": "5", "title": "Спецификация арматуры"},
    {"mark": "КЖ", "number": "6", "title": "Ведомость материалов"},
    {"mark": "КЖ", "number": "7", "title": "Конструктивные узлы"},
    {"mark": "КЖ", "number": "8", "title": "Схема фундаментной плиты"},
]

try:
    _pefs_orig_ff07_sheet_rows_from_template = globals().get("_ff07_sheet_rows_from_template")
except Exception:
    _pefs_orig_ff07_sheet_rows_from_template = None

def _project_engine_default_sheet_register_v1(section: str = "кж", data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    sec = str(section or "кж").lower()
    mark = "КЖ" if sec in ("кж", "kd", "foundation", "slab") else sec.upper()
    rows = []
    for item in _PROJECT_ENGINE_DEFAULT_KZH_SHEET_REGISTER_V1:
        row = dict(item)
        row["mark"] = mark
        rows.append(row)
    return rows

def _ff07_sheet_rows_from_template(template: Dict[str, Any], section: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    try:
        if callable(_pefs_orig_ff07_sheet_rows_from_template):
            base_rows = _pefs_orig_ff07_sheet_rows_from_template(template or {}, section, data or {})
            if isinstance(base_rows, list):
                rows = [r for r in base_rows if isinstance(r, dict)]
    except Exception as e:
        logger.warning("PROJECT_ENGINE_FALLBACK_SHEET_REGISTER_V1_ORIG_ERR %s", e)

    if len(rows) >= 8:
        return rows

    fallback = _project_engine_default_sheet_register_v1(section or (data or {}).get("section") or "кж", data or {})
    logger.warning("PROJECT_ENGINE_FALLBACK_SHEET_REGISTER_V1_USED section=%s old_len=%s new_len=%s", section, len(rows), len(fallback))
    return fallback
# === END_PROJECT_ENGINE_FALLBACK_SHEET_REGISTER_V1 ===


# === PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1_WRAPPER ===
try:
    _pec_orig_create_project_artifact_from_latest_template = create_project_artifact_from_latest_template

    def create_project_artifact_from_latest_template(user_text: str, task_id: str, topic_id: int = 0) -> dict:
        res = _pec_orig_create_project_artifact_from_latest_template(user_text, task_id, topic_id)
        try:
            from core.project_route_guard import format_project_result_message
            from core.output_sanitizer import sanitize_project_message
            res["user_message"] = sanitize_project_message(format_project_result_message(res, user_text))
        except Exception:
            pass
        return res
except Exception:
    pass
# === END_PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1_WRAPPER ===



# === PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1 ===
def _project_public_clean_v1(text: str) -> str:
    import re
    text = "" if text is None else str(text)
    patterns = [
        r"Engine:[^\n]*\n?",
        r"MANIFEST:[^\n]*\n?",
        r"task_id\s*[:=][^\n]*\n?",
        r"file_id\s*[:=][^\n]*\n?",
        r"/root/[^\s]*",
        r"tmp[a-zA-Z0-9_\-]{6,}\.(?:pdf|xlsx|docx|dxf)",
        r"\{[\"'][a-z_]+[\"']\s*:[^}]{0,300}\}",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text, flags=re.I | re.S)
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def _project_clean_payload_v1(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(v, str) and k.lower() in ("message", "text", "text_result", "result", "error"):
                out[k] = _project_public_clean_v1(v)
            else:
                out[k] = v
        return out
    if isinstance(obj, str):
        return _project_public_clean_v1(obj)
    return obj

try:
    _project_engine_orig_generate_project_section_v1 = generate_project_section
    async def generate_project_section(*args, **kwargs):
        import inspect
        res = _project_engine_orig_generate_project_section_v1(*args, **kwargs)
        if inspect.isawaitable(res):
            res = await res
        return _project_clean_payload_v1(res)
except Exception:
    pass

try:
    _project_engine_orig_process_project_file_v1 = process_project_file
    async def process_project_file(*args, **kwargs):
        import inspect
        res = _project_engine_orig_process_project_file_v1(*args, **kwargs)
        if inspect.isawaitable(res):
            res = await res
        return _project_clean_payload_v1(res)
except Exception:
    pass

try:
    _project_engine_orig_project_result_guard_v1 = project_result_guard
    def project_result_guard(result):
        return _project_clean_payload_v1(_project_engine_orig_project_result_guard_v1(result))
except Exception:
    pass
# === END_PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1 ===


# === PROJECT_SEARCH_FINAL_REGEX_AND_HEADER_FIX_SECTION_DETECTOR ===
_PE_MARKS_FINAL = ("кмд", "кд", "кж", "км", "кр", "ар", "ов", "вк", "эом", "сс", "гп", "пз", "тх", "см")

def _project_section_mark_final(src: str):
    up = str(src or "").upper().replace("Ё", "Е")
    for mark in _PE_MARKS_FINAL:
        m = mark.upper()
        if re.search(rf"(^|[^А-ЯA-Zа-яa-z]){re.escape(m)}([^А-ЯA-Zа-яa-z]|$)", up):
            return mark
    return None

def detect_section(file_name: str, text: str = ""):
    m = _project_section_mark_final(file_name)
    if m:
        return m
    return _project_section_mark_final(text)

def _detect_section(file_name: str, text: str = ""):
    return detect_section(file_name, text)
# === END_PROJECT_SEARCH_FINAL_REGEX_AND_HEADER_FIX_SECTION_DETECTOR ===

# === PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_V1 ===
def _project_template_memory_catalog_sync_absolute_v1(topic_id: int = 210, dry_run: bool = False) -> dict:
    import json as _json_pta1
    import sqlite3 as _sqlite_pta1
    from pathlib import Path as _Path_pta1
    from datetime import datetime as _dt_pta1, timezone as _tz_pta1

    base = _Path_pta1("/root/.areal-neva-core")
    mem_db = base / "data/memory.db"
    out_dir = base / "data/project_templates"

    result = {
        "marker": "PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_V1",
        "ok": False,
        "dry_run": bool(dry_run),
        "sections": [],
        "would_create": [],
        "created": [],
        "index_path": str(out_dir / "PROJECT_TEMPLATE_MODEL__MEMORY_CATALOG_INDEX.json"),
    }

    if not mem_db.exists():
        result["error"] = "MEMORY_DB_NOT_FOUND"
        return result

    conn = _sqlite_pta1.connect(str(mem_db))
    conn.row_factory = _sqlite_pta1.Row
    try:
        row = conn.execute(
            "SELECT value, timestamp FROM memory WHERE key=? ORDER BY timestamp DESC LIMIT 1",
            ("topic_210_file_catalog_autosync",),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        result["error"] = "TOPIC_210_FILE_CATALOG_NOT_FOUND"
        return result

    try:
        catalog = _json_pta1.loads(row["value"])
    except Exception as e:
        result["error"] = "CATALOG_JSON_ERROR: " + str(e)[:160]
        return result

    files = catalog.get("files") if isinstance(catalog, dict) else []
    if not isinstance(files, list):
        files = []

    def _name(item):
        if isinstance(item, dict):
            for k in ("file_name", "name", "title", "original_name"):
                v = str(item.get(k) or "").strip()
                if v:
                    return v
            links = item.get("links")
            if isinstance(links, list):
                for link in links:
                    v = str(link or "").strip()
                    if v:
                        return v[:180]
        return str(item or "").strip()

    def _section(name, item):
        raw = name.lower().replace("ё", "е")
        if isinstance(item, dict):
            raw += " " + str(item.get("direction") or "").lower().replace("ё", "е")
        if "кмд" in raw:
            return "КМД"
        if any(x in raw for x in ("км", "металл", "ферм", "каркас")):
            return "КМ"
        if any(x in raw for x in ("кд", "кровл", "стропил", "дерев", "балк")):
            return "КД"
        if any(x in raw for x in ("кж", "фундамент", "плит", "бетон", "армирован", "цоколь")):
            return "КЖ"
        if any(x in raw for x in ("ар", "архитект", "фасад", "планиров")):
            return "АР"
        return ""

    by_section = {}
    for item in files:
        name = _name(item)
        section = _section(name, item)
        if not name or not section:
            continue
        by_section.setdefault(section, []).append({
            "mark": section,
            "number": str(len(by_section.get(section, [])) + 1),
            "title": name[:180],
            "source": "topic_210_file_catalog_autosync",
        })

    result["sections"] = sorted(by_section.keys())

    existing_sections = set()
    if out_dir.exists():
        for p in out_dir.glob("PROJECT_TEMPLATE_MODEL__*.json"):
            try:
                data = _json_pta1.loads(p.read_text(encoding="utf-8"))
                pt = str(data.get("project_type") or "").upper().strip()
                if pt:
                    existing_sections.add(pt)
            except Exception:
                continue

    for section in sorted(by_section.keys()):
        if section not in existing_sections:
            result["would_create"].append(section)

    result["ok"] = True

    if dry_run:
        return result

    out_dir.mkdir(parents=True, exist_ok=True)
    now = _dt_pta1.now(_tz_pta1.utc).isoformat()

    index = {
        "_schema": "PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_V1",
        "updated_at_utc": now,
        "catalog_timestamp": row["timestamp"],
        "source": "memory.db:topic_210_file_catalog_autosync",
        "sections": result["sections"],
        "counts": {k: len(v) for k, v in by_section.items()},
        "existing_sections": sorted(existing_sections),
        "would_create": result["would_create"],
    }
    (out_dir / "PROJECT_TEMPLATE_MODEL__MEMORY_CATALOG_INDEX.json").write_text(
        _json_pta1.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    for section in result["would_create"]:
        rows = by_section.get(section) or []
        model = {
            "_schema": "PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_V1",
            "project_type": section,
            "topic_id": int(topic_id or 210),
            "updated_at_utc": now,
            "source": "topic_210_file_catalog_autosync",
            "source_files": [r["title"] for r in rows],
            "sheet_register": rows,
            "sections": [r["title"] for r in rows],
            "materials": [],
            "axes_grid": {"axes_letters": [], "axes_numbers": []},
            "dimensions": [],
        }
        path = out_dir / f"PROJECT_TEMPLATE_MODEL__{section}_memory_catalog.json"
        path.write_text(_json_pta1.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
        result["created"].append(str(path))

    return result
# === END_PROJECT_TEMPLATE_MEMORY_CATALOG_SYNC_ABSOLUTE_V1 ===

# === THREE_CONTOURS_FINAL_SOURCE_LOCK_V1 ===
# Project source lock:
# - topic_210 project templates: Образцы проектов from Drive
# - sketch/design references: PROJECT_DESIGN_REFERENCES when folder exists
# - PROJECT_ARTIFACTS is output only and forbidden as source

_FINAL_PROJECT_SAMPLES_FOLDER_ID = "1kcJbrn7XMcov__Z1JdWhKlJMZd7GUkgP"
_FINAL_PROJECT_ROOT_FOLDER_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"

def _final_project_drive_svc_v1():
    try:
        from core.engine_base import _drive_svc_v1
        return _drive_svc_v1()
    except Exception:
        return None

def _final_project_list_folder_v1(folder_id: str):
    svc = _final_project_drive_svc_v1()
    if svc is None:
        return []
    try:
        r = svc.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,size,modifiedTime)",
            pageSize=100,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        return r.get("files") or []
    except Exception:
        return []

def _final_project_find_folder_by_name_v1(name: str) -> str:
    svc = _final_project_drive_svc_v1()
    if svc is None:
        return ""
    try:
        q = "mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + str(name).replace("'", "\\'") + "'"
        r = svc.files().list(
            q=q,
            fields="files(id,name,parents,modifiedTime)",
            pageSize=20,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        files = r.get("files") or []
        return files[0]["id"] if files else ""
    except Exception:
        return ""

def _final_project_section_from_name_v1(name: str) -> str:
    low = str(name or "").lower().replace("ё", "е")
    if "кмд" in low:
        return "КМД"
    if any(x in low for x in ("км", "металл", "ферм", "каркас", "м-80", "м-110", "m-80", "m-110")):
        return "КМ"
    if any(x in low for x in ("кд", "кровл", "строп", "дерев", "балк")):
        return "КД"
    if any(x in low for x in ("кж", "фундамент", "плит", "бетон", "армир", "цоколь")):
        return "КЖ"
    if any(x in low for x in ("ар", "архитект", "фасад", "планиров")):
        return "АР"
    if any(x in low for x in ("эскиз", "eskiz")):
        return "ЭСКИЗ"
    return "UNKNOWN"

def _final_project_section_from_request_v1(text: str) -> str:
    low = str(text or "").lower().replace("ё", "е")
    if "кмд" in low:
        return "КМД"
    if "км" in low or "металл" in low:
        return "КМ"
    if "кд" in low or "кров" in low or "строп" in low:
        return "КД"
    if "ар" in low or "архитект" in low or "эскиз" in low or "эскизн" in low:
        return "ЭСКИЗ" if "эскиз" in low else "АР"
    if "кж" in low or "фундамент" in low or "плит" in low or "бетон" in low or "монолит" in low:
        return "КЖ"
    return "КЖ"

def _final_sync_project_drive_templates_v1(topic_id: int = 210) -> dict:
    import json as _json
    from pathlib import Path as _Path
    from datetime import datetime as _dt, timezone as _tz

    out_dir = _Path("/root/.areal-neva-core/data/project_templates")
    out_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "marker": "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1",
        "ok": False,
        "source_folder": "Образцы проектов",
        "source_folder_id": _FINAL_PROJECT_SAMPLES_FOLDER_ID,
        "design_references_folder": "PROJECT_DESIGN_REFERENCES",
        "project_artifacts_rule": "OUTPUT_ONLY_NOT_SOURCE",
        "synced_sections": [],
    }

    files = _final_project_list_folder_v1(_FINAL_PROJECT_SAMPLES_FOLDER_ID)
    design_folder_id = _final_project_find_folder_by_name_v1("PROJECT_DESIGN_REFERENCES")
    design_files = _final_project_list_folder_v1(design_folder_id) if design_folder_id else []

    by_section = {}
    for f in files:
        name = f.get("name","")
        sec = _final_project_section_from_name_v1(name)
        if sec == "UNKNOWN":
            continue
        by_section.setdefault(sec, []).append(f)

    if design_files:
        by_section.setdefault("ЭСКИЗ", []).extend(design_files)

    now = _dt.now(_tz.utc).isoformat()

    for sec, sec_files in by_section.items():
        clean = [f for f in sec_files if str(f.get("name","")).strip()]
        if not clean:
            continue
        best = max(clean, key=lambda f: int(f.get("size") or 0))
        model = {
            "_schema": "THREE_CONTOURS_FINAL_SOURCE_LOCK_V1",
            "project_type": sec,
            "topic_id": int(topic_id or 210),
            "source": "DRIVE_PROJECT_SOURCES",
            "source_folder_name": "Образцы проектов",
            "source_folder_id": _FINAL_PROJECT_SAMPLES_FOLDER_ID,
            "source_file_id": best.get("id",""),
            "source_file_name": best.get("name",""),
            "source_mime_type": best.get("mimeType",""),
            "source_modifiedTime": best.get("modifiedTime",""),
            "synced_at": now,
            "project_artifacts_forbidden_as_source": True,
            "design_references_folder_id": design_folder_id,
            "sheet_register": [
                {"mark": sec, "number": str(i + 1), "title": f.get("name",""), "file_id": f.get("id","")}
                for i, f in enumerate(clean)
            ],
            "sections": [f.get("name","") for f in clean],
            "materials": [],
            "axes_grid": {"axes_letters": [], "axes_numbers": []},
            "dimensions": [],
        }
        out = out_dir / f"PROJECT_TEMPLATE_MODEL__{sec}_FINAL_SOURCE_LOCK.json"
        out.write_text(_json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
        result["synced_sections"].append(sec)

    result["ok"] = True
    return result

def _final_project_model_for_request_v1(user_text: str, topic_id: int = 210) -> dict:
    import json as _json
    from pathlib import Path as _Path
    _final_sync_project_drive_templates_v1(int(topic_id or 210))
    sec = _final_project_section_from_request_v1(user_text)
    base = _Path("/root/.areal-neva-core/data/project_templates")
    candidates = []
    if sec == "ЭСКИЗ":
        candidates.append(base / "PROJECT_TEMPLATE_MODEL__ЭСКИЗ_FINAL_SOURCE_LOCK.json")
        candidates.append(base / "PROJECT_TEMPLATE_MODEL__АР_FINAL_SOURCE_LOCK.json")
    else:
        candidates.append(base / f"PROJECT_TEMPLATE_MODEL__{sec}_FINAL_SOURCE_LOCK.json")
    candidates.append(base / "PROJECT_TEMPLATE_MODEL__КЖ_FINAL_SOURCE_LOCK.json")
    for p in candidates:
        if p.exists():
            try:
                return _json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {}

def create_project_artifact_from_latest_template(user_text: str, task_id: str, topic_id: int = 0) -> dict:
    import os as _os
    import tempfile as _tempfile
    from datetime import datetime as _dt, timezone as _tz

    result = {
        "success": False,
        "error": "",
        "docx_path": "",
        "xlsx_path": "",
        "docx_link": "",
        "xlsx_link": "",
        "template_found": False,
        "project_type": "UNKNOWN",
    }

    model = _final_project_model_for_request_v1(user_text, int(topic_id or 210))
    if not model:
        result["error"] = "PROJECT_DRIVE_TEMPLATE_NOT_FOUND"
        return result

    params = _ff3_extract_project_params(user_text)
    project_type = _final_project_section_from_request_v1(user_text)
    if project_type == "UNKNOWN":
        project_type = model.get("project_type") or "КЖ"

    result["template_found"] = True
    result["project_type"] = project_type

    safe_task = str(task_id or "manual")[:8]
    out_dir = _tempfile.gettempdir()
    docx_path = _os.path.join(out_dir, f"project_{project_type}_{safe_task}.docx")
    xlsx_path = _os.path.join(out_dir, f"project_{project_type}_{safe_task}.xlsx")

    sheets = model.get("sheet_register") or []
    norm_sheets = []
    for sh in sheets:
        if isinstance(sh, str) and sh.strip():
            norm_sheets.append({"mark": project_type, "number": str(len(norm_sheets)+1), "title": sh.strip()[:160]})
        elif isinstance(sh, dict):
            norm_sheets.append(sh)
    sheets = norm_sheets or [{"mark": project_type, "number": "1", "title": model.get("source_file_name") or "Образец проекта"}]

    try:
        from docx import Document
        doc = Document()
        doc.add_heading(_ff3_safe_docx_text(params.get("project_name") or f"Проект {project_type}"), level=1)
        doc.add_paragraph("Источник: Google Drive / Образцы проектов")
        doc.add_paragraph("PROJECT_ARTIFACTS используется только как выходная папка, не как источник")
        doc.add_paragraph(f"Раздел: {project_type}")
        doc.add_paragraph(f"Образец: {model.get('source_file_name') or ''}")
        doc.add_paragraph(f"Дата: {_dt.now(_tz.utc).isoformat()}")

        doc.add_heading("Текущее задание", level=2)
        doc.add_paragraph(_ff3_safe_docx_text(user_text))

        doc.add_heading("Состав по источникам Drive", level=2)
        tbl = doc.add_table(rows=1, cols=4)
        tbl.rows[0].cells[0].text = "Марка"
        tbl.rows[0].cells[1].text = "Лист"
        tbl.rows[0].cells[2].text = "Наименование"
        tbl.rows[0].cells[3].text = "Drive file id"
        for sh in sheets:
            row = tbl.add_row().cells
            row[0].text = _ff3_safe_docx_text(sh.get("mark") or project_type)
            row[1].text = _ff3_safe_docx_text(sh.get("number") or "")
            row[2].text = _ff3_safe_docx_text(sh.get("title") or "")
            row[3].text = _ff3_safe_docx_text(sh.get("file_id") or "")

        doc.add_heading("Разделы", level=2)
        for sec in (model.get("sections") or [])[:100]:
            doc.add_paragraph(_ff3_safe_docx_text(sec))

        doc.save(docx_path)
    except Exception as e:
        result["error"] = "DOCX_CREATE_FAILED: " + str(e)[:250]
        return result

    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Состав проекта"
        headers = ["№", "Марка", "Лист", "Наименование", "Drive file id", "Источник"]
        for c, h in enumerate(headers, 1):
            ws.cell(1, c, h)
        for i, sh in enumerate(sheets, 2):
            ws.cell(i, 1, i - 1)
            ws.cell(i, 2, sh.get("mark") or project_type)
            ws.cell(i, 3, sh.get("number") or "")
            ws.cell(i, 4, sh.get("title") or "")
            ws.cell(i, 5, sh.get("file_id") or "")
            ws.cell(i, 6, "Образцы проектов / PROJECT_DESIGN_REFERENCES")
        ws2 = wb.create_sheet("Текущее задание")
        ws2.cell(1, 1, "Задание")
        ws2.cell(2, 1, str(user_text or "")[:32000])
        ws2.cell(4, 1, "Запрещено")
        ws2.cell(5, 1, "PROJECT_ARTIFACTS не использовать как источник")
        for col, width in {"D": 80, "E": 45, "F": 45}.items():
            ws.column_dimensions[col].width = width
        ws2.column_dimensions["A"].width = 120
        wb.save(xlsx_path)
        wb.close()
    except Exception as e:
        result["error"] = "XLSX_CREATE_FAILED: " + str(e)[:250]
        return result

    result["docx_path"] = docx_path
    result["xlsx_path"] = xlsx_path

    try:
        from core.engine_base import upload_artifact_to_drive
        result["docx_link"] = upload_artifact_to_drive(docx_path, task_id, int(topic_id or 0)) or ""
        result["xlsx_link"] = upload_artifact_to_drive(xlsx_path, task_id, int(topic_id or 0)) or ""
    except Exception as e:
        result["upload_error"] = str(e)[:250]

    result["success"] = bool(_os.path.exists(docx_path) and _os.path.getsize(docx_path) > 1000)
    if not result["success"]:
        result["error"] = "PROJECT_ARTIFACT_EMPTY"
    try:
        from core.project_route_guard import format_project_result_message
        from core.output_sanitizer import sanitize_project_message
        result["user_message"] = sanitize_project_message(format_project_result_message(result, user_text))
    except Exception:
        pass
    return result

# === END_THREE_CONTOURS_FINAL_SOURCE_LOCK_V1 ===

# === PHOTO_RECOGNITION_TOPIC210_RUNTIME_BINDING_V1 ===
try:
    _photo_210_orig_process_project_file = process_project_file

    async def process_project_file(file_path: str, task_id: str, topic_id: int, raw_input: str = "") -> Dict[str, Any]:
        from pathlib import Path as _PhotoPath
        import json as _photo_json
        import tempfile as _photo_tempfile
        from core.photo_recognition_engine import is_image_file, process_photo_recognition

        fp = str(file_path or "")
        fn = _PhotoPath(fp).name

        try:
            tid = int(topic_id or 0)
        except Exception:
            tid = 0

        if tid == 210 and is_image_file(file_name=fn, file_path=fp):
            card = process_photo_recognition(
                topic_id=210,
                file_name=fn,
                file_path=fp,
                owner_comment=str(raw_input or ""),
                source="TELEGRAM",
                project_context_hint=str(raw_input or ""),
            )

            out_dir = _PhotoPath(_photo_tempfile.gettempdir()) / "areal_project_image_cards"
            out_dir.mkdir(parents=True, exist_ok=True)

            safe_task = str(task_id or "project_image")[:16]
            artifact = out_dir / f"PROJECT_IMAGE_CARD__{safe_task}.json"
            artifact.write_text(_photo_json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")

            return {
                "success": True,
                "section": detect_section(fn, raw_input) or "UNKNOWN",
                "artifact_path": str(artifact),
                "project_image_card": card,
                "status": "PROJECT_IMAGE_CARD_CREATED_NO_VISION_ANALYSIS",
                "error": None,
                "message": "Изображение принято как проектный материал. Визуальный анализ не выполнялся без разрешённой Vision-модели",
            }

        return await _photo_210_orig_process_project_file(
            file_path=file_path,
            task_id=task_id,
            topic_id=topic_id,
            raw_input=raw_input,
        )
except Exception:
    pass
# === END_PHOTO_RECOGNITION_TOPIC210_RUNTIME_BINDING_V1 ===


# === LOAD_CALCULATION_INPUT_BASED_BINDING_V1 ===
def calc_loads_input_based(
    permanent_kpa=None,
    temporary_kpa=None,
    snow_kpa=None,
    wind_kpa=None,
    source_text: str = "",
):
    from core.load_calculation_engine import calculate_loads_fact_only
    return calculate_loads_fact_only(
        permanent_kpa=permanent_kpa,
        temporary_kpa=temporary_kpa,
        snow_kpa=snow_kpa,
        wind_kpa=wind_kpa,
        source_text=source_text,
    )
# === END_LOAD_CALCULATION_INPUT_BASED_BINDING_V1 ===

====================================================================================================
END_FILE: core/project_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/file_intake_router.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: cc90687dbd7f88ca7b05507b9279cbdc19a1bc27cb0b2449c753ac37c7ff1e6b
====================================================================================================
from core.gemini_vision import analyze_image_file  # GEMINI_VISION_V43
import os, logging, asyncio
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

INTENT_TRIGGERS = {
    "estimate": [
        "смет", "расчёт", "расчет", "стоимость", "цена", "бюджет",
        "сделай таблицу", "таблицу", "вытащи объёмы", "вытащи объемы",
        "посчитай объём", "посчитай объем", "объём", "объем",
        "excel", "эксель", "google таблицу", "google таблица", "google sheets",
        "sheets", "спецификац", "ведомост", "бетон", "арматур", "фундамент"
    ],
    "ocr": [
        "распознай таблицу", "распознать таблицу", "распозна", "ocr",
        "скан", "текст с фото", "фото в таблицу"
    ],
    "technadzor": [
        "проверь дефекты", "акт технадзора", "дефекты", "дефект",
        "нарушение", "нарушения", "косяк", "осмотр", "технадзор",
        "проверь фото", "проверь узел", "проверь"
    ],
    "dwg": ["чертёж", "чертеж", "dxf", "dwg", "проект", "автокад"],
    "template": ["сделай так же", "по образцу", "как в", "шаблон"],
    "vision": ["анализ фото", "анализ схемы", "разбери фото", "что на фото", "что на схеме"],
    "search": ["найди в сметах", "поиск по сметам", "искать в старых"],
}
FORMAT_TRIGGERS = {
    "excel": ["excel", "эксель", "xlsx", "иксель"],
    "sheets": ["google sheets", "google таблиц", "гугл таблиц", "sheets", "таблицу на диск", "google sheet"],
    "word": ["word", "ворд", "docx"],
    "docs": ["google docs", "google документ", "гугл документ", "docs"],
}

def detect_intent(text: str) -> Optional[str]:
    if not text: return None
    t = text.lower()
    for intent, triggers in INTENT_TRIGGERS.items():
        if any(tr in t for tr in triggers): return intent
    return None

def detect_format(text: str) -> str:
    t = (text or "").lower()
    if any(x in t for x in FORMAT_TRIGGERS["sheets"]): return "sheets"
    elif any(x in t for x in FORMAT_TRIGGERS["docs"]): return "docs"
    elif any(x in t for x in FORMAT_TRIGGERS["word"]): return "word"
    elif any(x in t for x in FORMAT_TRIGGERS["excel"]): return "excel"
    return "excel"

def format_priority(file_name: str, available_files: list = None) -> str:
    """FORMAT_PRIORITY_V1 — DWG/DXF > XLSX > DOCX > PDF > IMAGE"""
    files = available_files or [file_name]
    # Приоритет по канону §11.9
    for ext in [".dwg", ".dxf"]:
        if any(f.lower().endswith(ext) for f in files):
            return "dwg"
    for ext in [".xlsx", ".xls", ".csv"]:
        if any(f.lower().endswith(ext) for f in files):
            return "excel"
    for ext in [".docx", ".doc"]:
        if any(f.lower().endswith(ext) for f in files):
            return "word"
    for ext in [".pdf"]:
        if any(f.lower().endswith(ext) for f in files):
            return "pdf"
    for ext in [".jpg", ".jpeg", ".png", ".heic", ".webp", ".tiff", ".bmp"]:
        if any(f.lower().endswith(ext) for f in files):
            return "image"
    return "unknown"

def get_topic_role(topic_id: int) -> str:
    try:
        import sqlite3
        conn = sqlite3.connect('/root/.areal-neva-core/data/memory.db')
        cur = conn.cursor()
        cur.execute("SELECT value FROM memory WHERE key = ?", (f"topic_{topic_id}_role",))
        row = cur.fetchone(); conn.close()
        return row[0] if row else ""
    except: return ""

def get_clarification_message(file_name: str, topic_id: int) -> str:
    role = get_topic_role(topic_id)
    base = f"📎 Получил файл «{file_name}».\nЧто с ним сделать?"
    if topic_id == 2 or "СТРОЙКА" in role:
        return base + "\n• Смета / Расчёт\n• Проектирование / Расчёт нагрузок\n• Анализ фото / Схема\n• Распознать таблицу\n• Просто сохранить\n\nВ каком формате?\n• Excel\n• Google Sheets"
    elif topic_id == 5 or "ТЕХНАДЗОР" in role:
        return base + "\n• Проверить дефекты / Составить акт\n• Анализ фото / Схема\n• Распознать таблицу\n• Просто сохранить\n\nВ каком формате?\n• Word\n• Google Docs"
    else:
        return base + "\n• Анализ фото / Схема\n• Распознать таблицу\n• Проверить дефекты\n• Смета / Расчёт\n• Просто сохранить"

# === CANON_PASS_INTAKE_OFFER_SENT ===
_OFFER_SENT = {}
def mark_offer_sent(tid): _OFFER_SENT[tid] = True
def is_offer_sent(tid): return _OFFER_SENT.get(tid, False)
# === END CANON_PASS_INTAKE_OFFER_SENT ===

def should_ask_clarification(raw_input: str, has_file: bool, already_asked: bool = False) -> bool:
    # === ANTI_REPEAT_V1 — не спрашивать если уже спрашивали ===
    if already_asked:
        return False
    if not has_file: return False
    return detect_intent(raw_input) is None


ESTIMATE_FILENAME_TRIGGERS = ["кж","кд","спецификац","ведомост","смет","расход","арматур","бетон","плит","конструкци","фундамент","у1-","у2-","кр-"]

def detect_intent_from_filename(file_name: str) -> Optional[str]:
    fn = (file_name or "").lower()
    if any(t in fn for t in ESTIMATE_FILENAME_TRIGGERS):
        return "estimate"
    if any(t in fn for t in ["акт","дефект","осмотр","технадзор"]):
        return "technadzor"
    if any(t in fn for t in [".dwg",".dxf","чертеж","чертёж"]):
        return "dwg"
    return None

async def route_file(file_path: str, task_id: str, topic_id: int, intent: str, fmt: str = "excel") -> Optional[Dict[str, Any]]:
    try:
        from core.engine_base import detect_real_file_type
        real_type = detect_real_file_type(file_path)
        # === UNIVERSAL_FILE_HANDLER_V1_WIRED ===
        if real_type in ("zip", "rar", "7z", "dwg", "dxf", "video", "mp4", "audio", "text_fallback", "unknown") or intent == "dwg":
            try:
                from core.universal_file_handler import extract_text_from_file
                _ufh = extract_text_from_file(file_path, task_id, topic_id)
                _ufh_text = (_ufh.get("text") or "").strip()
                _ufh_rows = _ufh.get("rows") or []
                if _ufh.get("success") and (_ufh_text or _ufh_rows):
                    _summary = f"\u0424\u0430\u0439\u043b \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u043d ({_ufh.get('type','unknown')}):\n"
                    if _ufh_rows:
                        _summary += f"\u0421\u0442\u0440\u043e\u043a \u0434\u0430\u043d\u043d\u044b\u0445: {len(_ufh_rows)}\n"
                        for row in _ufh_rows[:5]:
                            _summary += "  " + " | ".join(str(c) for c in row if c) + "\n"
                    if _ufh_text:
                        _summary += _ufh_text[:1500]
                    return {"success": True, "text": _summary, "type": _ufh.get("type")}
                else:
                    return {"success": False, "error": _ufh.get("error") or f"\u0424\u043e\u0440\u043c\u0430\u0442 {real_type} \u043d\u0435 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u0442\u0441\u044f"}
            except Exception as _ufh_e:
                return {"success": False, "error": f"UNIVERSAL_HANDLER_ERROR: {_ufh_e}"}
        # === END UNIVERSAL_FILE_HANDLER_V1_WIRED ===
        if real_type in ("csv", "txt") and intent not in ("estimate", "technadzor", "ocr"):
            intent = "estimate"
        if real_type == "dwg":
            intent = "dwg"
        if intent == "estimate":
            if fmt == "sheets":
                from core.sheets_generator import create_google_sheet
                from core.estimate_engine import process_estimate_to_excel
                data = await process_estimate_to_excel(file_path, task_id, topic_id)
                if data.get("excel_path"):
                    from openpyxl import load_workbook
                    wb = load_workbook(data["excel_path"]); ws = wb.active
                    rows = [[cell.value for cell in row] for row in ws.iter_rows()]; wb.close()
                    link = None
                    try:
                        link = create_google_sheet(f"Estimate_{task_id[:8]}", rows)
                    except Exception as e:
                        err_str = str(e)
                        if "403" in err_str or "permission" in err_str.lower() or "quota" in err_str.lower():
                            logger.warning(f"Google Sheets 403/quota -> fallback XLSX: {e}")
                        else:
                            logger.warning(f"create_google_sheet fallback to XLSX: {e}")
                        link = None
                    if link and "docs.google.com" in str(link):
                        return {"success": True, "drive_link": link, "artifact_path": data["excel_path"]}
                    # Fallback: return XLSX artifact
                    return {"success": True, "artifact_path": data["excel_path"], "excel_path": data["excel_path"]}
            else:
                from core.estimate_engine import process_estimate_to_excel
                return await process_estimate_to_excel(file_path, task_id, topic_id)
        elif intent == "ocr":
            from core.ocr_engine import process_image_to_excel
            return await process_image_to_excel(file_path, task_id, topic_id)
        elif intent == "technadzor":
            from core.technadzor_engine import process_defect_to_report
            data = await process_defect_to_report(file_path, task_id, topic_id)
            if not data or not data.get("success"):
                return {"success": False, "error": (data.get("error") if isinstance(data, dict) else None) or "TECHNADZOR_FAILED"}
            rp = data.get("report_path")
            if rp:
                import os as _os
                rp_size = _os.path.getsize(rp) if _os.path.exists(rp) else 0
                if rp_size < 1000:
                    return {"success": False, "error": "DOCUMENT_EMPTY_RESULT: DOCX too small"}
                from docx import Document as _Doc
                _doc = _Doc(rp)
                _has_content = any(p.text.strip() for p in _doc.paragraphs) or len(_doc.tables) > 0
                if not _has_content:
                    return {"success": False, "error": "DOCUMENT_EMPTY_RESULT: no paragraphs or tables"}
            if fmt == "docs" and rp:
                try:
                    from core.docs_generator import create_google_doc
                    from docx import Document
                    doc = Document(rp)
                    content = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                    link = create_google_doc(f"Defect_{task_id[:8]}", content)
                    if link:
                        return {"success": True, "drive_link": link, "artifact_path": rp}
                except Exception as _e:
                    logger.warning(f"create_google_doc fallback to DOCX: {_e}")
            return data
        elif intent == "dwg":
            from core.dwg_engine import process_dwg_to_excel
            return await process_dwg_to_excel(file_path, task_id, topic_id)
        elif intent == "template":
            from core.template_manager import apply_template, get_template
            tmpl = get_template(str(topic_id), topic_id, "estimate")
            if tmpl:
                out = f"/tmp/{task_id}_template.xlsx"
                # Extract real data from source file if possible
                real_rows = []
                try:
                    real_type_t = detect_real_file_type(file_path)
                    if real_type_t in ("xlsx", "zip_or_office"):
                        from openpyxl import load_workbook
                        wb_t = load_workbook(file_path, data_only=True)
                        ws_t = wb_t.active
                        for row_t in ws_t.iter_rows(min_row=2, values_only=True):
                            if row_t and any(v is not None for v in row_t):
                                real_rows.append(list(row_t))
                        wb_t.close()
                    elif real_type_t == "pdf":
                        try:
                            import pdfplumber
                            with pdfplumber.open(file_path) as pdf_t:
                                for page_t in pdf_t.pages:
                                    tables_t = page_t.extract_tables()
                                    for table_t in tables_t:
                                        for row_t in table_t[1:]:
                                            if row_t and any(v for v in row_t if v):
                                                real_rows.append(row_t)
                        except Exception:
                            pass
                except Exception as _te:
                    logger.warning(f"template data extraction failed: {_te}")
                if apply_template(tmpl, out, real_rows): return {"success": True, "excel_path": out}
                elif apply_template(tmpl, out, []): return {"success": True, "excel_path": out}
        elif intent == "vision":
            result = await analyze_image_file(file_path, None)
            return {"success": True, "engine": "gemini_vision", "result_text": result, "text_result": result}
        elif intent == "search":
            from core.search_engine import search_in_estimates
            results = search_in_estimates(file_path, topic_id)
            return {"success": True, "text_result": "\n".join(results[:10])}
        return {"success": False, "error": f"PIPELINE_NOT_EXECUTED: no handler for intent={intent}"}
    except Exception as e:
        logger.error(f"route_file: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

async def handle_multiple_files(file_paths: List[str], task_id: str, topic_id: int, intent: str, fmt: str = "excel") -> Optional[Dict[str, Any]]:
    if intent == "estimate":
        from core.multi_file_orchestrator import merge_estimate_results
        results = []
        for fp in file_paths:
            from core.estimate_engine import process_estimate_to_excel
            r = await process_estimate_to_excel(fp, task_id, topic_id)
            if r: results.append(r)
        return merge_estimate_results(results)
    return None

# === ARK_KZH_KD_TRIGGERS ===
ESTIMATE_FILENAME_TRIGGERS = list(set(ESTIMATE_FILENAME_TRIGGERS + [
    'арк', 'кж', 'кд', 'кр', 'ов', 'вк', 'эо', 'гп',
    'марка', 'раздел', 'спецификация', 'ведомость',
]))

_ARK_SECTION_MAP = {
    'арк': 'estimate', 'кж': 'estimate', 'кд': 'estimate',
    'кр': 'estimate', 'ов': 'estimate', 'вк': 'estimate',
    'эо': 'estimate', 'гп': 'estimate',
}

def detect_intent_from_filename_v2(file_name: str):
    fn = (file_name or '').lower()
    for key, intent in _ARK_SECTION_MAP.items():
        if key in fn:
            return intent
    return detect_intent_from_filename(file_name)
# === END ARK_KZH_KD_TRIGGERS ===

# === ALL_CONTOURS_ROUTE_FILE_V2 ===
try:
    _all_contours_orig_route_file=route_file
except Exception:
    _all_contours_orig_route_file=None
def _ac_words(*groups):
    return ["".join(chr(x) for x in g) for g in groups]
def _ac_has(text, words):
    t=str(text or "").lower()
    return any(w in t for w in words)
async def route_file(file_path, task_id, topic_id=0, *args, **kwargs):
    import inspect
    fp=str(file_path or "")
    raw=" ".join([fp,str(kwargs.get("raw_input") or ""),str(kwargs.get("prompt") or ""),str(kwargs.get("user_text") or "")]+[str(a or "") for a in args])
    template_words=_ac_words((1080,1089,1087,1086,1083,1100,1079,1091,1081,32,1082,1072,1082,32,1096,1072,1073,1083,1086,1085),(1089,1086,1093,1088,1072,1085,1080,32,1096,1072,1073,1083,1086,1085),(1101,1090,1086,32,1096,1072,1073,1083,1086,1085))
    if _ac_has(raw, template_words):
        from core.template_manager import save_template
        return {"success":True,"intent":"template","template_path":save_template(fp,int(topic_id or 0),"template")}
    kzh_words=_ac_words((1082,1078),(1082,1076),(1072,1088,1082),(1082,1088))
    detector=globals().get("detect_intent_from_filename_v2") or globals().get("detect_intent_from_filename")
    intent=detector(fp) if detector else "unknown"
    if intent=="estimate" and _ac_has(fp,kzh_words):
        from core.estimate_engine import process_kzh_pdf
        return await process_kzh_pdf(fp,str(task_id),int(topic_id or 0))
    if _all_contours_orig_route_file is None:
        return {"success":False,"error":"original_route_file_missing","intent":intent}
    res=_all_contours_orig_route_file(fp,task_id,topic_id,*args,**kwargs)
    if inspect.isawaitable(res):
        res=await res
    sheets_words=("google sheets","fmt=sheets","sheets")+tuple(_ac_words((1075,1091,1075,1083,32,1090,1072,1073,1083),(1075,1091,1075,1083,32,1090,1072,1073,1083,1080,1094),(1092,1086,1088,1084,1072,1090,32,115,104,101,101,116,115)))
    if isinstance(res,dict) and _ac_has(raw,sheets_words):
        xl=res.get("excel_path") or res.get("xlsx_path")
        if xl:
            try:
                from core.sheets_generator import create_google_sheet
                sh=create_google_sheet(xl,task_id=task_id,topic_id=topic_id)
                if inspect.isawaitable(sh):
                    sh=await sh
                if sh:
                    res["sheets_link"]=sh.get("url") if isinstance(sh,dict) else str(sh)
                    res["drive_link"]=res.get("drive_link") or res["sheets_link"]
            except Exception as e:
                res["sheets_error"]=str(e)[:300]
    return res
# === END_ALL_CONTOURS_ROUTE_FILE_V2 ===

# === FINAL_CODE_CONTOUR_FILE_INTAKE_V1 ===
try:
    ESTIMATE_FILENAME_TRIGGERS=list(set(ESTIMATE_FILENAME_TRIGGERS+[_f for _f in ["km","kmd"]]))
except Exception:
    pass
try:
    _ARK_SECTION_MAP.update({"km":"estimate","kmd":"estimate"})
except Exception:
    _ARK_SECTION_MAP={"km":"estimate","kmd":"estimate"}
try:
    _final_orig_route_file=route_file
except Exception:
    _final_orig_route_file=None
async def route_file(file_path, task_id, topic_id=0, *args, **kwargs):
    import inspect
    fp=str(file_path or "")
    detector=globals().get("detect_intent_from_filename_v2") or globals().get("detect_intent_from_filename")
    intent=detector(fp) if detector else "unknown"
    low=fp.lower()
    if intent=="estimate" and any(x in low for x in ["km","kmd","kzh","kd","ark","kr"]):
        from core.estimate_engine import process_kzh_pdf
        return await process_kzh_pdf(fp,str(task_id),int(topic_id or 0))
    if _final_orig_route_file is None:
        return {"success":False,"error":"original_route_file_missing","intent":intent}
    res=_final_orig_route_file(fp,task_id,topic_id,*args,**kwargs)
    if inspect.isawaitable(res):
        res=await res
    if isinstance(res,dict) and (kwargs.get("fmt")=="sheets" or str(kwargs.get("raw_input") or "").lower().find("sheets")>=0):
        xl=res.get("excel_path") or res.get("xlsx_path")
        if xl:
            from openpyxl import load_workbook
            wb=load_workbook(xl,data_only=False)
            ws=wb.active
            rows=[[cell.value for cell in row] for row in ws.iter_rows()]
            from core.sheets_generator import create_google_sheet
            sh=create_google_sheet(Path(xl).stem, rows)
            if inspect.isawaitable(sh): sh=await sh
            if sh:
                res["sheets_link"]=sh.get("url") if isinstance(sh,dict) else str(sh)
                res["drive_link"]=res.get("drive_link") or res["sheets_link"]
    return res
# === END_FINAL_CODE_CONTOUR_FILE_INTAKE_V1 ===

# === FILE_INTAKE_KM_V39 ===
try:
    ESTIMATE_FILENAME_TRIGGERS = list(set(list(ESTIMATE_FILENAME_TRIGGERS) + ["км","кмд","металл","конструкц"]))
except Exception:
    pass
try:
    _ARK_SECTION_MAP.update({"км": "estimate", "кмд": "estimate"})
except Exception:
    pass
# === END_FILE_INTAKE_KM_V39 ===

# === FILE_INTAKE_PROJECT_V41 ===

_PROJECT_V41_TRIGGERS = ("кж","км","кмд","ар","ов","вк","эом","сс","гп","пз","тх")

def _v41_project_section_hit(text):
    src = str(text or "").lower()
    import re
    for key in _PROJECT_V41_TRIGGERS:
        if re.search(r"(^|[^а-яa-z0-9])" + re.escape(key) + r"([^а-яa-z0-9]|$)", src, re.I):
            return True
    return False

try:
    _v41_orig_detect_intent = detect_intent
    def detect_intent(file_name: str, raw_input: str = "", *args, **kwargs):
        src = (str(file_name or "") + " " + str(raw_input or "")).lower()
        if _v41_project_section_hit(src):
            return "project"
        return _v41_orig_detect_intent(file_name)  # DETECT_INTENT_FIX_V1
except Exception:
    pass

if "route_file" in globals():
    _v41_orig_route_file = route_file

    async def route_file(file_path, task_id, topic_id=0, intent=None, fmt="excel", *args, **kwargs):
        raw_input = str(kwargs.get("raw_input") or "")
        file_name = str(file_path or "")
        final_intent = intent or detect_intent(file_name, raw_input)

        if final_intent == "project":
            try:
                from core.project_engine import process_project_file
                return await process_project_file(file_path, task_id, topic_id, raw_input)
            except Exception as e:
                return {"success": False, "error": "PROJECT_ENGINE_FAILED: " + str(e)[:300]}

        res = _v41_orig_route_file(file_path, task_id, topic_id, final_intent, fmt, *args, **kwargs)
        import inspect
        if inspect.isawaitable(res):
            res = await res

        if isinstance(res, dict) and res.get("success") is False:
            return res
        if not isinstance(res, dict):
            return {"success": False, "error": "FILE_RESULT_GUARD: route_file returned empty"}
        if not (res.get("drive_link") or res.get("sheets_link") or res.get("doc_link") or res.get("excel_path") or res.get("artifact_path") or res.get("text") or res.get("result")):
            return {"success": False, "error": "FILE_RESULT_GUARD: no usable output"}
        return res

# === END_FILE_INTAKE_PROJECT_V41 ===

# === FILE_INTAKE_PROJECT_SAFE_V42 ===

_PROJECT_V42_TRIGGERS = ("кж","км","кмд","ар","ов","вк","эом","сс","гп","пз","тх")

def _v42_project_choice(raw_input: str) -> bool:
    t = str(raw_input or "").lower()
    return "проектирование" in t or "расчёт нагрузок" in t or "расчет нагрузок" in t

if "route_file" in globals():
    _v42_orig_route_file = route_file

    async def route_file(file_path, task_id, topic_id=0, intent=None, fmt="excel", *args, **kwargs):
        import inspect
        raw_input = str(kwargs.get("raw_input") or "")

        if _v42_project_choice(raw_input):
            try:
                from core.project_engine import process_project_file
                res = await process_project_file(file_path, task_id, topic_id, raw_input)
                if not isinstance(res, dict):
                    return {"success": False, "error": "PROJECT_RESULT_GUARD: empty_payload"}
                if res.get("success") is False:
                    return res
                if not (res.get("drive_link") or res.get("excel_path") or res.get("docx_path") or res.get("pdf_path")):
                    return {"success": False, "error": "PROJECT_RESULT_GUARD: no_artifact"}
                return res
            except Exception as e:
                return {"success": False, "error": "PROJECT_ENGINE_FAILED: " + str(e)[:300]}

        if str(intent or "").lower() == "project" and not _v42_project_choice(raw_input):
            intent = "estimate"

        res = _v42_orig_route_file(file_path, task_id, topic_id, intent, fmt, *args, **kwargs)
        if inspect.isawaitable(res):
            res = await res

        if isinstance(res, dict) and res.get("success") is False:
            return res

        if not isinstance(res, dict):
            return {"success": False, "error": "FILE_RESULT_GUARD: route_file returned empty"}

        if not (res.get("drive_link") or res.get("sheets_link") or res.get("doc_link") or res.get("excel_path") or res.get("artifact_path") or res.get("text") or res.get("result")):
            return {"success": False, "error": "FILE_RESULT_GUARD: no usable output"}

        return res

# === END_FILE_INTAKE_PROJECT_SAFE_V42 ===

# === CODE_CLOSE_V43_FILE_INTAKE ===

def _v43_is_template_learn(raw_input):
    t = str(raw_input or "").lower()
    return "образец" in t or "шаблон" in t or "запомни структуру" in t

def _v43_is_project_choice(raw_input):
    t = str(raw_input or "").lower()
    return "проектирование" in t or "расчёт нагрузок" in t or "расчет нагрузок" in t

if "route_file" in globals():
    _v43_orig_route_file = route_file

    async def route_file(file_path, task_id, topic_id=0, intent=None, fmt="excel", *args, **kwargs):
        import inspect
        raw_input = str(kwargs.get("raw_input") or "")

        if _v43_is_template_learn(raw_input):
            try:
                from core.template_manager import template_learn_v43
                ok = template_learn_v43(file_path, topic_id, intent or "project")
                return {"success": bool(ok), "text": "Шаблон сохранён для топика" if ok else "TEMPLATE_LEARN_FAILED"}
            except Exception as e:
                return {"success": False, "error": "TEMPLATE_LEARN_FAILED: " + str(e)[:300]}

        if _v43_is_project_choice(raw_input):
            try:
                from core.template_manager import template_priority_v43
                template = template_priority_v43(topic_id, "project")
                from core.project_engine import process_project_file
                res = await process_project_file(file_path, task_id, topic_id, raw_input)
                if template:
                    res["template_used"] = template
                return res
            except Exception as e:
                return {"success": False, "error": "PROJECT_ENGINE_FAILED: " + str(e)[:300]}

        if str(intent or "").lower() == "project" and not _v43_is_project_choice(raw_input):
            intent = "estimate"

        res = _v43_orig_route_file(file_path, task_id, topic_id, intent, fmt, *args, **kwargs)
        if inspect.isawaitable(res):
            res = await res

        if isinstance(res, dict) and res.get("success") is False:
            return res
        if not isinstance(res, dict):
            return {"success": False, "error": "FILE_RESULT_GUARD: empty_route_result"}
        if not (res.get("drive_link") or res.get("sheets_link") or res.get("doc_link") or res.get("excel_path") or res.get("artifact_path") or res.get("text") or res.get("result")):
            return {"success": False, "error": "FILE_RESULT_GUARD: no_output"}
        return res

# === END_CODE_CLOSE_V43_FILE_INTAKE ===


# === FILE_INTAKE_KZH_INTENT_FIX_V1 ===
# Bare KЖ/КД/project files are project-context files, not estimate files.
# File upload without explicit user instruction must ask what to do.

import json as _fik_json
import os as _fik_os
import re as _fik_re
from typing import Optional as _FIKOptional

ESTIMATE_FILENAME_TRIGGERS = [
    "смет", "расход", "ведомост", "спецификац",
    "у1-", "у2-", "кр-",
]

PROJECT_FILENAME_TRIGGERS = [
    "кж", "кд", "кмд", "км", "ар",
    "плит", "фундамент", "конструкци", "конструкция",
    "узел", "цоколь", "разрез", "армирован", "чертеж", "чертёж",
]

def _fik_norm_text(value) -> str:
    return str(value or "").lower().replace("ё", "е").strip()

def _fik_word_hit(text: str, words) -> bool:
    t = _fik_norm_text(text)
    for w in words:
        ww = _fik_norm_text(w)
        if not ww:
            continue
        if len(ww) <= 3:
            if _fik_re.search(r"(^|[^а-яa-z0-9])" + _fik_re.escape(ww) + r"([^а-яa-z0-9]|$)", t, _fik_re.I):
                return True
        elif ww in t:
            return True
    return False

def _fik_extract_user_instruction(raw_input: str) -> str:
    """
    Extract only explicit user instruction.
    Ignore file_name/file_id/mime/source metadata, because filename alone must not auto-run pipeline.
    """
    raw = str(raw_input or "").strip()
    if not raw:
        return ""
    try:
        obj = _fik_json.loads(raw)
        if isinstance(obj, dict):
            for key in ("caption", "user_text", "text", "prompt", "comment", "message"):
                val = obj.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
            return ""
    except Exception:
        pass
    if raw.startswith("{") and ("file_name" in raw or "file_id" in raw or "mime_type" in raw):
        return ""
    return raw

def detect_intent_from_filename(file_name: str) -> _FIKOptional[str]:
    fn = _fik_norm_text(_fik_os.path.basename(str(file_name or "")))

    if _fik_word_hit(fn, PROJECT_FILENAME_TRIGGERS):
        return "project"

    if _fik_word_hit(fn, ESTIMATE_FILENAME_TRIGGERS):
        return "estimate"

    if _fik_word_hit(fn, ("акт", "дефект", "осмотр", "технадзор")):
        return "technadzor"

    if _fik_word_hit(fn, (".dwg", ".dxf", "dwg", "dxf", "чертеж", "чертёж")):
        return "dwg"

    return None

def detect_intent_from_filename_v2(file_name: str) -> _FIKOptional[str]:
    return detect_intent_from_filename(file_name)

def should_ask_clarification(raw_input: str, has_file: bool, already_asked: bool = False) -> bool:
    if already_asked:
        return False
    if not has_file:
        return False

    instruction = _fik_extract_user_instruction(raw_input)
    low = _fik_norm_text(instruction)

    service_words = (
        "tmp", "healthcheck", "service_file", "служебный", "синхронизации"
    )
    if _fik_word_hit(low, service_words):
        return False

    explicit_action_words = (
        "сделай", "делай", "создай", "сформируй", "подготовь", "разработай",
        "посчитай", "рассчитай", "проверь", "проанализируй", "выгрузи",
        "сохрани", "возьми", "прими", "используй", "распознай", "обработай",
        "шаблон", "образец", "по образцу", "по шаблону",
        "смет", "проект", "кж", "кд", "км", "кмд", "акт", "технадзор",
        "таблиц", "excel", "xlsx", "pdf", "dxf", "dwg", "ocr",
        "проектирование", "расчет нагрузок", "расчёт нагрузок",
    )

    return not _fik_word_hit(low, explicit_action_words)

try:
    _fik_orig_route_file = route_file
except Exception:
    _fik_orig_route_file = None

async def route_file(file_path, task_id, topic_id=0, intent=None, fmt="excel", *args, **kwargs):
    """
    Final guard:
    - KЖ/KД/project filenames never become estimate automatically
    - if caller passes estimate for project file without explicit estimate command, downgrade to project
    - raw file with no user instruction must return clarification payload
    """
    import inspect as _fik_inspect

    raw_input = str(kwargs.get("raw_input") or kwargs.get("prompt") or kwargs.get("user_text") or "")
    instruction = _fik_extract_user_instruction(raw_input)
    filename_intent = detect_intent_from_filename(str(file_path or ""))

    if not instruction and filename_intent in ("project", "estimate", "technadzor", "dwg"):
        try:
            msg = get_clarification_message(_fik_os.path.basename(str(file_path or "")), int(topic_id or 0))
        except Exception:
            msg = (
                "Файл принят.\n"
                "Что сделать с ним?\n\n"
                "1. Взять как шаблон проекта\n"
                "2. Взять как шаблон сметы\n"
                "3. Взять как шаблон технадзора\n"
                "4. Обработать как обычный файл\n\n"
                "Ответь одним сообщением"
            )
        return {
            "success": False,
            "needs_clarification": True,
            "state": "WAITING_CLARIFICATION",
            "intent": filename_intent,
            "result_text": msg,
            "error": "FILE_INTAKE_NEEDS_CONTEXT",
        }

    low_instruction = _fik_norm_text(instruction)
    explicit_estimate = _fik_word_hit(low_instruction, ("смет", "расход", "ведомост", "спецификац", "расчет", "расчёт", "стоимость", "цена", "объем", "объём"))

    if filename_intent == "project" and str(intent or "").lower() == "estimate" and not explicit_estimate:
        intent = "project"

    if intent is None:
        intent = filename_intent

    if _fik_orig_route_file is None:
        return {"success": False, "error": "original_route_file_missing", "intent": intent}

    res = _fik_orig_route_file(file_path, task_id, topic_id, intent, fmt, *args, **kwargs)
    if _fik_inspect.isawaitable(res):
        res = await res
    return res

# === END_FILE_INTAKE_KZH_INTENT_FIX_V1 ===


# === CONTEXT_AWARE_FILE_INTAKE_V1_ROUTER_WRAPPER ===
try:
    _ca_fir_orig_route_file = route_file
except Exception:
    _ca_fir_orig_route_file = None

async def route_file(file_path, task_id, topic_id=0, intent=None, fmt="excel", *args, **kwargs):
    import inspect
    raw_input = str(kwargs.get("raw_input") or kwargs.get("prompt") or kwargs.get("user_text") or "")
    if not raw_input:
        try:
            from core.file_context_intake import latest_pending_instruction_for_topic
            chat_id = str(kwargs.get("chat_id") or "")
            pending = latest_pending_instruction_for_topic(int(topic_id or 0), chat_id)
            if pending:
                kwargs["raw_input"] = pending
                raw_input = pending
        except Exception:
            pass

    if _ca_fir_orig_route_file is None:
        return {"success": False, "error": "CONTEXT_AWARE_FILE_INTAKE_V1: original_route_file_missing"}

    res = _ca_fir_orig_route_file(file_path, task_id, topic_id, intent, fmt, *args, **kwargs)
    if inspect.isawaitable(res):
        res = await res
    return res

# === END_CONTEXT_AWARE_FILE_INTAKE_V1_ROUTER_WRAPPER ===



# === FILE_INTAKE_SUPPORTED_FORMATS_V1 ===
SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".bmp", ".tiff", ".tif", ".gif", ".svg"}
SUPPORTED_DOCUMENT_FORMATS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".rtf"}
SUPPORTED_CAD_FORMATS = {".dwg", ".dxf", ".ifc", ".pln", ".rvt"}
SUPPORTED_AUDIO_FORMATS = {".ogg", ".mp3", ".wav", ".m4a", ".flac", ".aac"}
SUPPORTED_ARCHIVE_FORMATS = {".zip", ".rar", ".7z"}

def get_supported_file_format_v1(file_name: str) -> str:
    import os
    ext = os.path.splitext(str(file_name or "").lower())[1]
    if ext in SUPPORTED_IMAGE_FORMATS:
        return "image_ocr_vision"
    if ext in SUPPORTED_DOCUMENT_FORMATS:
        return "document"
    if ext in SUPPORTED_CAD_FORMATS:
        if ext == ".pln":
            return "pln_metadata_only"
        if ext == ".rvt":
            return "rvt_metadata_only"
        if ext == ".ifc":
            return "ifc_ifcopenshell"
        return "cad_ezdxf"
    if ext in SUPPORTED_AUDIO_FORMATS:
        return "audio_groq_stt"
    if ext in SUPPORTED_ARCHIVE_FORMATS:
        return "archive_recursive"
    return "unsupported"

def unsupported_format_message_v1(file_name: str) -> str:
    return "Формат файла не читается напрямую. Пришли PDF/DOCX/XLSX или экспортированный чертёж"

try:
    ESTIMATE_FILENAME_TRIGGERS = list(set(ESTIMATE_FILENAME_TRIGGERS + [
        "jpg", "jpeg", "png", "heic", "heif", "webp", "bmp", "tiff", "gif", "svg",
        "dwg", "dxf", "ifc", "pln", "rvt", "zip", "rar", "7z",
        "км", "кмд", "ов", "вк", "эо", "эм", "эос"
    ]))
except Exception:
    pass
# === END_FILE_INTAKE_SUPPORTED_FORMATS_V1 ===


# === CONTEXT_AWARE_FILE_INTAKE_V1_DB_LOOKUP ===
def _context_aware_file_intake_lookup_v1(chat_id: str = "", topic_id: int = 0) -> str:
    import sqlite3
    try:
        conn = sqlite3.connect("/root/.areal-neva-core/data/core.db")
        try:
            if chat_id:
                rows = conn.execute(
                    "SELECT raw_input, input_type, state, result FROM tasks WHERE chat_id=? AND COALESCE(topic_id,0)=? AND state IN ('DONE','AWAITING_CONFIRMATION','IN_PROGRESS','WAITING_CLARIFICATION') ORDER BY updated_at DESC LIMIT 5",
                    (str(chat_id), int(topic_id or 0)),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT raw_input, input_type, state, result FROM tasks WHERE COALESCE(topic_id,0)=? AND state IN ('DONE','AWAITING_CONFIRMATION','IN_PROGRESS','WAITING_CLARIFICATION') ORDER BY updated_at DESC LIMIT 5",
                    (int(topic_id or 0),),
                ).fetchall()
        finally:
            conn.close()
    except Exception:
        rows = []

    for r in rows or []:
        combined = " ".join(str(x or "") for x in r).lower()
        if any(x in combined for x in ("смет", "estimate", "расцен", "стоимость", "цена")):
            return "estimate"
        if any(x in combined for x in ("проект", "кж", "кд", "ар", "эскиз", "км", "кмд", "ов", "вк", "эо")):
            return "project"
        if any(x in combined for x in ("акт", "технадзор", "дефект", "нарушение")):
            return "technadzor"
        if any(x in combined for x in ("образец", "шаблон", "эталон")):
            return "template"
    return ""

try:
    _context_aware_orig_route_file_v1 = route_file
    async def route_file(*args, **kwargs):
        import inspect
        lst = list(args)
        raw_input = str(kwargs.get("raw_input") or kwargs.get("caption") or kwargs.get("user_text") or "")
        chat_id = str(kwargs.get("chat_id") or "")
        topic_id = kwargs.get("topic_id", lst[2] if len(lst) >= 3 else 0)
        current_intent = kwargs.get("intent", lst[3] if len(lst) >= 4 else None)
        final_intent = current_intent

        if not final_intent or str(final_intent).lower() in ("unknown", "none", ""):
            if not raw_input.strip():
                final_intent = _context_aware_file_intake_lookup_v1(chat_id=chat_id, topic_id=int(topic_id or 0))

        if final_intent and final_intent != current_intent:
            if "intent" in kwargs:
                kwargs["intent"] = final_intent
            elif len(lst) >= 4:
                lst[3] = final_intent
            else:
                kwargs["intent"] = final_intent

        res = _context_aware_orig_route_file_v1(*lst, **kwargs)
        if inspect.isawaitable(res):
            res = await res
        return res
except Exception:
    pass
# === END_CONTEXT_AWARE_FILE_INTAKE_V1_DB_LOOKUP ===


# === P6D_FILE_INTAKE_IMAGE_ESTIMATE_KWARGS_CLOSE_20260504_V1 ===
try:
    _p6d_orig_route_file_20260504 = route_file
except Exception:
    _p6d_orig_route_file_20260504 = None

def _p6d_fi_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6d_fi_low(v):
    return _p6d_fi_s(v).lower().replace("ё", "е")

def _p6d_fi_is_image(path, mime=""):
    low = _p6d_fi_low(str(path) + " " + str(mime))
    return low.startswith("image/") or any(x in low for x in (".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff", ".bmp"))

def _p6d_fi_is_estimate_text(raw):
    low = _p6d_fi_low(raw)
    return any(x in low for x in (
        "смет", "стоимость", "расчет", "расчёт", "полная смета", "дом",
        "фундамент", "плита", "каркас", "кровля", "стены", "отделка", "санузел"
    ))

async def route_file(file_path, task_id, topic_id=0, intent=None, fmt="excel", *args, **kwargs):
    import inspect
    fp = _p6d_fi_s(file_path, 3000)
    raw_input = _p6d_fi_s(kwargs.get("raw_input") or kwargs.get("caption") or kwargs.get("user_text") or kwargs.get("prompt") or "", 12000)
    mime_type = _p6d_fi_s(kwargs.get("mime_type") or "", 500)
    final_intent = _p6d_fi_s(intent or kwargs.get("intent") or "", 100)

    if int(topic_id or 0) == 2 and _p6d_fi_is_image(fp, mime_type) and _p6d_fi_is_estimate_text(raw_input):
        try:
            from core import sample_template_engine as _ste
            fake_task = {"id": str(task_id), "raw_input": raw_input, "topic_id": int(topic_id or 0), "input_type": "drive_file"}
            res = _ste.handle_topic2_image_estimate_pipeline_p6d(
                conn=kwargs.get("conn"),
                task=fake_task,
                chat_id=kwargs.get("chat_id"),
                topic_id=int(topic_id or 0),
                raw_input=raw_input,
                local_path=fp,
                full_context=raw_input,
            )
            if inspect.isawaitable(res):
                res = await res
            if res:
                return {"success": True, "intent": "estimate", "engine": "P6D_IMAGE_ESTIMATE_FROM_PHOTO_FULL_CLOSE_20260504_V1", "text": "image estimate handled"}
        except Exception as e:
            return {"success": False, "error": "P6D_IMAGE_ESTIMATE_ROUTE_FAILED:" + str(e)[:500]}

    if _p6d_orig_route_file_20260504 is None:
        return {"success": False, "error": "P6D_ORIGINAL_ROUTE_FILE_MISSING"}

    try:
        res = _p6d_orig_route_file_20260504(fp, task_id, topic_id, final_intent or intent, fmt, *args, **kwargs)
    except TypeError:
        clean_kwargs = {k: v for k, v in kwargs.items() if k not in ("raw_input", "caption", "user_text", "prompt", "mime_type", "conn", "chat_id")}
        res = _p6d_orig_route_file_20260504(fp, task_id, topic_id, final_intent or intent, fmt, *args, **clean_kwargs)

    if inspect.isawaitable(res):
        res = await res
    return res
# === END_P6D_FILE_INTAKE_IMAGE_ESTIMATE_KWARGS_CLOSE_20260504_V1 ===

# === P6E2_FILE_INTAKE_ROUTE_FILE_KWARGS_AND_IMAGE_ESTIMATE_20260504_V1 ===
try:
    _P6E2_ORIG_ROUTE_FILE_20260504 = route_file
except Exception:
    _P6E2_ORIG_ROUTE_FILE_20260504 = None

def _p6e2_fi_s(v, limit=50000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6e2_fi_low(v):
    return _p6e2_fi_s(v).lower().replace("ё", "е")

def _p6e2_fi_is_image(path="", mime_type="", file_name=""):
    low = _p6e2_fi_low(" ".join([path or "", mime_type or "", file_name or ""]))
    return low.startswith("image/") or any(x in low for x in (".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff", ".bmp"))

def _p6e2_fi_estimate_like(text):
    low = _p6e2_fi_low(text)
    return any(x in low for x in ("смет", "расчет", "расчёт", "посчитай", "стоимость", "полная смета"))

async def route_file(file_path, task_id, topic_id=0, intent=None, fmt="excel", *args, **kwargs):
    raw_input = _p6e2_fi_s(kwargs.get("raw_input") or kwargs.get("caption") or kwargs.get("user_text") or kwargs.get("prompt") or "", 100000)
    mime_type = _p6e2_fi_s(kwargs.get("mime_type") or "")
    file_name = _p6e2_fi_s(kwargs.get("file_name") or kwargs.get("name") or "")
    conn = kwargs.get("conn")
    chat_id = kwargs.get("chat_id")
    if int(topic_id or 0) == 2 and _p6e2_fi_is_image(file_path, mime_type, file_name) and _p6e2_fi_estimate_like(raw_input):
        try:
            from core.sample_template_engine import handle_topic2_image_estimate_p6e2
            if conn is not None:
                fake_task = {"id": str(task_id), "raw_input": raw_input, "input_type": "drive_file", "topic_id": int(topic_id or 0), "chat_id": chat_id}
                ok = await handle_topic2_image_estimate_p6e2(conn=conn, task=fake_task, chat_id=chat_id, topic_id=topic_id, raw_input=raw_input, local_path=file_path, file_name=file_name, mime_type=mime_type)
                if ok:
                    return {"success": True, "intent": "estimate", "result_text": "Смета по фото сформирована"}
        except Exception as e:
            return {"success": False, "error": "P6E2_IMAGE_ESTIMATE_ROUTE_FAILED:" + str(e)[:500]}
    if _P6E2_ORIG_ROUTE_FILE_20260504:
        clean = dict(kwargs)
        for k in ("raw_input", "caption", "user_text", "prompt", "mime_type", "conn", "chat_id", "file_name", "name"):
            clean.pop(k, None)
        return await _P6E2_ORIG_ROUTE_FILE_20260504(file_path, task_id, topic_id, intent, fmt, *args, **clean)
    return {"success": False, "error": "P6E2_ORIGINAL_ROUTE_FILE_MISSING"}
# === END_P6E2_FILE_INTAKE_ROUTE_FILE_KWARGS_AND_IMAGE_ESTIMATE_20260504_V1 ===

====================================================================================================
END_FILE: core/file_intake_router.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/ai_router.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 7c5a85800f035842fcd179daf52546522c9c5592891d9f1b6790beaf5143c69d
====================================================================================================
import os
import re
import json
import hashlib
import logging
from typing import Any, Dict, List

# === SEARCH_MONOLITH_V2_IMPORT ===
# AVAILABILITY_CHECK: проверка доступности источника перед поиском
# STALE_CONTEXT_GUARD: не использовать устаревший контекст > 24h
# NEGATIVE_SELECTION: исключать нерелевантные источники

try:
    from core.search_session import run_search_monolith_v2, has_active_search_session
except Exception:
    run_search_monolith_v2 = None
    has_active_search_session = lambda chat_id, topic_id: False
# === END SEARCH_MONOLITH_V2_IMPORT ===

import httpx
from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
ENV_PATH = f"{BASE}/.env"
LOG_PATH = f"{BASE}/logs/ai_router.log"

load_dotenv(ENV_PATH, override=True)
os.makedirs(f"{BASE}/logs", exist_ok=True)

logger = logging.getLogger("ai_router")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(fh)

OPENROUTER_API_KEY = <REDACTED_SECRET>"OPENROUTER_API_KEY", "").strip()
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip().rstrip("/")

DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat").strip() or "deepseek/deepseek-chat"
ONLINE_MODEL = os.getenv("OPENROUTER_MODEL_ONLINE", "perplexity/sonar").strip() or "perplexity/sonar"  # SEARCH_MONOLITH_V1

SEARCH_RE = [
    r"\bнайди\b", r"\bнайти\b", r"\bпоиск\b", r"\bпоищи\b", r"\bsearch\b",
    r"\bцена\b", r"\bстоимость\b", r"\bсколько стоит\b",
    r"\bavito\b", r"\bozon\b", r"\bwildberries\b", r"\bauto\.ru\b", r"\bdrom\b",
    r"\bновости\b", r"\bпогода\b", r"\bкурс\b", r"\bмаркетплейс\b", r"\bссылк", r"\bкупить\b", r"\bзаказать\b", r"\bтовар\b",
    r"озон", r"валбер", r"вайлдбер", r"площадк"
]

BAD_CONTEXT_RE = [
    r"forbidden default model",
    r"traceback",
    r"telegramconflicterror",
    r"voice unavailable",
    r"stt failed",
    r"/root/",
    r"\.log",
    r"\.json"
]

BAD_RESULT_RE = [
    r"\bой\b",
    r"сорян",
    r"дружище",
    r"не переживай",
    r"дай мне немного времени",
    r"я могу помочь",
    r"извини",
    r"извините",
    r"я тут",
    r"уведомлятор",
    r"перегрелся",
    r"😅",
    r"💪",
    r"😎",
    r"непонятно",
    r"уточните",
    r"недостаточно данных",
    r"\bищу\b",
    r"\bнайду\b",
    r"ожидаю уточнения",
    r"ссылк[аи]\s+предоставлю",
    r"готов искать",
    r"могу найти",
    r"укажите,?\s+что именно нужно найти"
]

SYSTEM_PROMPT = """# AREAL-NEVA ORCHESTRA — КАНОНИЧЕСКИЙ СИСТЕМНЫЙ ПРОМПТ
# CANON_SYSTEM_PROMPT_V1

## КТО ТЫ
Ты — исполнительный AI-оркестр системы AREAL-NEVA. Ты не просто отвечаешь на последнее сообщение. Ты понимаешь контекст, смысл, область задачи и текущую ветку разговора.

## ГЛАВНЫЙ ПРИОРИТЕТ КОНТЕКСТА
1. Текущее сообщение пользователя — ВСЕГДА главное
2. Активная задача (если есть и релевантна)
3. PIN (только если совпадает с темой)
4. Краткая память (последние 2-3 релевантных факта)
5. Долгая память (знания и выводы)
6. Архив (только если тема совпадает)
7. Результат поиска (если был)

## ПОНИМАНИЕ ЧАТА
Каждый чат имеет свою роль и специализацию:
- технадзор → думай как технический инспектор
- стройка → думай как прораб/сметчик
- поиск → думай как снабженец
- авто → думай как механик/снабженец запчастей
- оркестр → думай как системный архитектор
Если есть topic_role — это твой рабочий режим.

## РАЗЛИЧЕНИЕ РАЗГОВОР / ЗАДАЧА
РАЗГОВОР ("привет", "как дела", "ты тут", "ок", "спасибо") → короткий ответ, НИКАКИХ задач
ЗАДАЧА = действие + объект + ожидаемый результат → создаётся задача
УТОЧНЕНИЕ к активной задаче → продолжение задачи, не новая
ПОДТВЕРЖДЕНИЕ ("да", "верно", "ок") при AWAITING_CONFIRMATION → DONE
ИСПРАВЛЕНИЕ ("нет", "не так", "переделай") → revision
ЗАВЕРШЕНИЕ ("всё", "готово", "закрывай") → FINISH, перебивает всё

## ПРИОРИТЕТ ИНТЕНТОВ
FINISH > CANCEL > CONFIRM > REVISION > TASK > SEARCH > CHAT

## ПАМЯТЬ — ЧТО ХРАНИТЬ / ЧТО НЕ ХРАНИТЬ
ХРАНИТЬ: результаты задач, выводы, факты, решения
НЕ ХРАНИТЬ: ошибки, "не найдено", "уточните", служебные тексты, трейсбэки

## ПОИСК
Запускать поиск ТОЛЬКО если нужны актуальные внешние данные.
Если [SEARCH_RESULT] есть в контексте — используй ТОЛЬКО его, не выдумывай.
НЕ писать: "ищу", "найду", "ссылки предоставлю" — только готовый результат.

## ОТВЕТ
- Только по сути задачи
- Без болтовни, без эмодзи, без извинений
- Без служебных фраз, путей, json-обрывков, трейсбэков
- Если неясно — ОДИН короткий уточняющий вопрос
- Активная задача не блокирует чат — новые вопросы получают ответ

## ЗАПРЕЩЁННЫЕ ФРАЗЫ
"недостаточно данных" | "не могу" | "уточните" (без причины) | "ожидаю уточнения" |
"готов искать" | "могу найти" | "задача не выполнена" (без кода) | "Задача завершена" (без результата) |
"Не понимаю запрос" | "Готов к выполнению"

## ФАЙЛЫ
Файл принят → обработать → результат в Google Drive → вернуть ссылку.
Сервер не хранит тяжёлые файлы постоянно. Drive = основное хранилище.

## ЦЕЛЬ
Думай как человек: понимай смысл, помни только важное, не засоряй голову мусором, доводи задачу до результата.
""".strip()  # CANON_SYSTEM_PROMPT_V1

SEARCH_SYSTEM_PROMPT = """# SEARCH_MONOLITH_V1 — ЦИФРОВОЙ СНАБЖЕНЕЦ

Ты — закупочный эксперт. Твоя задача НЕ "найти ссылки", а дать закупочное решение.

## ЭТАП 1: РАЗБОР ЗАПРОСА
Извлеки: товар, категорию, бренд, модель, характеристики, артикул/OEM/SKU, город, количество, новое/б/у, аналоги допустимы?, доставка нужна?, приоритет (цена/качество/скорость).
Для стройки: материал, профиль, толщина, RAL, покрытие, ГОСТ/ТУ, единица цены, объём.
Для запчастей: марка, модель, год, кузов, OEM, сторона, рестайлинг/дорестайлинг, новая/б/у/контрактная.

## ЭТАП 2: УТОЧНЕНИЕ (максимум 3 вопроса если данных мало)
Не более 3 вопросов. Дальше работай с тем что есть.

## ЭТАП 3: РАСШИРЕНИЕ ЗАПРОСА (7+ формул)
Ищи по: название+город, название+оптом, название+производитель, артикул/OEM, физпараметры, название+Avito, название+VK/Telegram.

## ЭТАП 4: ЦИФРОВОЙ ДВОЙНИК ТОВАРА
Ищи по физическим параметрам, не по рекламному названию.

## ЭТАП 5: ИСТОЧНИКИ
Проверь: Ozon, Wildberries, Яндекс Маркет, Avito, Петрович, Леруа, ВсеИнструменты, заводы, дилеры, 2ГИС, VK, Telegram, форумы.
Для запчастей: Exist, Emex, ZZap, Drom, Auto.ru, EuroAuto, разборки.

## ЭТАП 6: КЛАССИФИКАЦИЯ ИСТОЧНИКА
Каждому источнику: производитель / дилер / база / оптовик / маркетплейс / частник / разборка / форум.
Доверие: CONFIRMED / PARTIAL / UNVERIFIED / RISK.
checked_at и source_url ОБЯЗАТЕЛЬНЫ. Без них — не выше PARTIAL.

## ЭТАП 7: ТЕХНИЧЕСКИЙ АУДИТ
Для стройки: проверь толщину, RAL, покрытие, слой цинка, жалобы ("тонкий","брак","не тот цвет").
Для запчастей: OEM, сторона, кузов, состояние, жалобы ("не подошло","не та сторона","предоплата").
ЗАПРЕЩЕНО смешивать в одной строке: 0.45 и 0.5, разные RAL, оригинал и аналог, б/у и новое.

## ЭТАП 8: REVIEW TRUST SCORE (0-100)
80-100: живые отзывы с фото и деталями.
60-79: частично подтверждены.
40-59: нужен звонок.
0-39: высокий риск фейка.
Фейки: одинаковые фразы, все в один день, нет фото, профиль пустой.

## ЭТАП 9: SELLER_RISK для VK/Telegram
Автоматически UNVERIFIED пока не подтверждены: цена, дата, контакт, наличие.
Красные флаги: новая группа, боты, только предоплата, скрытые контакты.

## ЭТАП 10: RISK SCORE
Красные флаги: цена сильно ниже рынка, только предоплата, нет телефона/адреса/ИНН, старый прайс, не совпадают ТТХ.

## ЭТАП 11: TCO
итоговая цена = цена + доставка + комиссия + добор + риск − кэшбэк
Учитывай: НДС, минимальная партия, гарантия, возврат, самовывоз.

## ЭТАП 12: РАНЖИРОВАНИЕ
CHEAPEST — самый дешёвый.
MOST_RELIABLE — самый надёжный.
BEST_VALUE — лучший баланс цена/риск/логистика.
FASTEST — самый быстрый.
RISK_CHEAP — дёшево но рискованно.
REJECTED — что отброшено и почему.

## ЭТАП 13: ТАБЛИЦА (обязательна)
Поставщик | Площадка | Тип | Город | Цена | Ед. | TCO | ТТХ совпадают | Trust Score | Риск | Контакт | Ссылка | checked_at | Статус

## ЭТАП 14: ШАБЛОН ЗВОНКА (обязателен)
- Цена актуальна?
- Есть в наличии?
- Цена с НДС или без?
- Доставка сколько и когда?
- Документы/счёт дадут?
- Гарантия/возврат есть?
- Характеристики точно такие?
- Для металла: толщина, покрытие, слой цинка.
- Для запчастей: OEM, сторона, кузов, состояние.

## ЗАПРЕЩЕНО
- Выдавать просто список ссылок без анализа.
- Писать "цена уточняйте" как результат.
- Смешивать разные ТТХ в одном варианте.
- Выдумывать цены и контакты.
- Непроверенные данные как факт.
"""  # END SEARCH_MONOLITH_V1.strip()

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()


def _dedup_text(text: str) -> str:
    seen = set()
    out = []
    for line in text.split("\n"):
        key = line.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(line)
    return "\n".join(out)

def _clean(text: str, limit: int = 12000) -> str:
    text = (text or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]

def _match_any(patterns: List[str], text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t, re.I) for p in patterns)

def _search_intent(text: str, input_type: str) -> bool:
    if (input_type or "").lower() == "search":
        return True
    return _match_any(SEARCH_RE, text)

def _sanitize_block(label: str, value: Any) -> str:
    text = _clean(_s(value), 4000)
    if not text:
        return ""
    if _match_any(BAD_CONTEXT_RE, text):
        return ""
    return f"[TYPE:{label}]\n{text}"

def _dedup_blocks(blocks: List[str]) -> List[str]:
    out = []
    seen = set()
    for block in blocks:
        b = _clean(block, 4000)
        if not b:
            continue
        key = hashlib.sha1(re.sub(r"\s+", " ", b.lower()).encode("utf-8")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        out.append(b)
    return out

def _extract_user_text(payload: Dict[str, Any]) -> str:
    for key in ("normalized_input", "raw_input", "input", "text", "prompt", "message", "transcript"):
        text = _clean(_s(payload.get(key)))
        if text:
            return text
    return ""


def _build_messages(payload: Dict[str, Any], user_text: str) -> List[Dict[str, str]]:
    user_text = _dedup_text(user_text)
    if not user_text.strip():
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "REQUEST:\nпустой запрос"}
        ]

    input_type = _s(payload.get("input_type")).lower() or "text"
    state = _s(payload.get("state")).upper() or "IN_PROGRESS"

    topic_role = _clean(_s(payload.get("topic_role")), 500)
    topic_directions = _clean(_s(payload.get("topic_directions")), 1000)
    system_content = SYSTEM_PROMPT
    # search-followup: если жалуются на ссылки и есть search_context — не давать общие советы
    search_followup_markers = [
        "нерелевант",
        "битые",
        "битые ссылки",
        "ссылки биты",
        "ссылки битые",
        "живые ссылки",
        "ссылки не те",
        "проверь",
        "проверь еще",
        "проверь ещё",
        "ещё раз",
        "еще раз",
        "это не то",
    ]
    if any(m in user_text.lower() for m in search_followup_markers) and payload.get("search_context"):
        system_content += "\n\nFORBIDDEN_SEARCH_ADVICE: ЗАПРЕЩЕНО предлагать Dr.Web, Link Checker, Yandex Safety, Google Safe Browsing, VirusTotal и любые общие сервисы проверки ссылок. Нужно продолжить именно предыдущую поисковую задачу, опираясь на SEARCH_RESULT, без общих советов и без ухода в сторону."
    if topic_role:
        system_content = f"Роль этого чата: {topic_role}\n\n" + system_content
    if topic_directions:
        system_content = system_content + f"\n\nТиповые задачи этого чата: {topic_directions}"


    # === OWNER_REFERENCE_FULL_WORKFLOW_POLICY_V1 ===
    try:
        from core.owner_reference_policy import build_owner_reference_context
        _owner_reference_policy_context = build_owner_reference_context(user_text)
    except Exception as _orp_err:
        logger.warning("OWNER_REFERENCE_POLICY_V1_ERR %s", _orp_err)
        _owner_reference_policy_context = ""
    # === END_OWNER_REFERENCE_FULL_WORKFLOW_POLICY_V1 ===

    # === ESTIMATE_TEMPLATE_POLICY_CONTEXT_V4_TOP_LOGISTICS ===
    try:
        from core.estimate_template_policy import build_estimate_template_context
        _estimate_template_policy_context = build_estimate_template_context(user_text)
    except Exception as _etp_err:
        logger.warning("ESTIMATE_TEMPLATE_POLICY_CONTEXT_V4_ERR %s", _etp_err)
        _estimate_template_policy_context = ""
    # === END_ESTIMATE_TEMPLATE_POLICY_CONTEXT_V4_TOP_LOGISTICS ===

    blocks = _dedup_blocks([
        _sanitize_block("OWNER_REFERENCE_POLICY", _owner_reference_policy_context),
        _sanitize_block("ESTIMATE_TEMPLATE_POLICY", _estimate_template_policy_context),
        _sanitize_block("ACTIVE_TASK", payload.get("active_task_context")),
        _sanitize_block("PIN", payload.get("pin_context")),
        _sanitize_block("SHORT_MEMORY", payload.get("short_memory_context")),
        _sanitize_block("LONG_MEMORY", payload.get("long_memory_context")),
        _sanitize_block("ARCHIVE", payload.get("archive_context")),
        _sanitize_block("SEARCH_RESULT", payload.get("search_context")),
    ])

    user_parts = [
        f"STATE: {state}",
        f"INPUT_TYPE: {input_type}",
    ]
    if blocks:
        user_parts.append("CONTEXT:\n" + "\n\n".join(blocks))
    user_parts.append("REQUEST:\n" + user_text)

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": "\n\n".join(user_parts)},
    ]

def _extract_content(data: Dict[str, Any]) -> str:
    try:
        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
                else:
                    parts.append(_s(item))
            return _clean("\n".join(parts))
        return _clean(_s(content))
    except Exception:
        return _clean(json.dumps(data, ensure_ascii=False)[:2000])

async def _openrouter_call(model: str, messages: List[Dict[str, str]]) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0)) as client:
        r = await client.post(f"{OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=body)
    if r.status_code != 200:
        msg = f"OPENROUTER_HTTP_{r.status_code}: {r.text[:500]}"
        logger.error(msg)
        raise RuntimeError(msg)
    return _extract_content(r.json())

async def process_ai_task(payload: Dict[str, Any]) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    user_text = _dedup_text(_extract_user_text(payload))
    if not user_text:
        return ""

    input_type = _s(payload.get("input_type")).lower()
    _s_chat = _s(payload.get("chat_id"))
    try: _s_topic = int(payload.get("topic_id") or 0)
    except: _s_topic = 0
    is_search = _search_intent(user_text, input_type) or bool(has_active_search_session(_s_chat, _s_topic))
    work_payload = dict(payload)

    if is_search:
        # === SEARCH_MONOLITH_V2_CALL ===
        try:
            if run_search_monolith_v2 is not None:
                _v2 = await run_search_monolith_v2(work_payload, user_text, _openrouter_call, ONLINE_MODEL, SEARCH_SYSTEM_PROMPT)
                _v2 = _clean(_s(_v2), 12000)
                if _v2:
                    logger.info("SEARCH_MONOLITH_V2_OK chars=%s", len(_v2))
                    return _v2
        except Exception as _v2e:
            logger.error("SEARCH_MONOLITH_V2_FAIL err=%s fallback=V1", _v2e)
        # === END SEARCH_MONOLITH_V2_CALL ===
        logger.info(
            "router_search_call model=%s input_type=%s state=%s chars=%s",
            ONLINE_MODEL,
            input_type or "text",
            _s(payload.get("state")).upper() or "IN_PROGRESS",
            len(user_text),
        )
        try:
            search_result = await _openrouter_call(
                ONLINE_MODEL,
                [
                    {"role": "system", "content": SEARCH_SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
            )
        except Exception as e:
            logger.error("search_model_fail err=%s — fallback to DEFAULT_MODEL without search", e)
            search_result = ""

        search_result = _clean(_s(search_result), 4000)
        if not search_result:
            logger.warning("web_search_empty query=%s", user_text[:200])
        else:
            existing = _clean(_s(work_payload.get("search_context")), 4000)
            work_payload["search_context"] = search_result + ("\n\n" + existing if existing else "")
            logger.info("web_search_ok chars=%s", len(search_result))

    logger.info(
        "router_call model=%s input_type=%s state=%s chars=%s is_search=%s",
        DEFAULT_MODEL,
        input_type or "text",
        _s(payload.get("state")).upper() or "IN_PROGRESS",
        len(user_text),
        is_search,
    )

    messages = _build_messages(work_payload, user_text)
    ctx_str = _clean_context("\n\n".join(m.get("content", "") for m in messages))
    if _context_has_answer(ctx_str):
        for m in messages:
            if m.get("role") == "system":
                m["content"] += "\nFORBIDDEN: do not ask clarifying questions. Answer directly."
                break
    # === MODEL_OVERRIDE_V1 ===
    _final_model = work_payload.get("model_override") or DEFAULT_MODEL
    result = await _openrouter_call(_final_model, messages)
    # === END MODEL_OVERRIDE_V1 ===

    if _match_any(BAD_RESULT_RE, result):
        logger.warning("router_result_filtered result=%s", result[:120])
        return ""

    logger.info("router_ok chars=%s", len(result))
    return result



def _clean_context(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r", "\n")
    text = text.replace("\t", " ")
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()[:12000]

def _context_has_answer(text: str) -> bool:
    if not text:
        return False
    return len(text.strip()) > 50

# FORCE CLEAN CONTEXT

SEARCH_SYSTEM_PROMPT = """# TOPIC500_SEARCH_OUTPUT_CONTRACT_20260504_V1

ROLE:
Ты закупочный интернет-поиск для topic_500

OUTPUT MUST BE USEFUL, NOT ANALYTICAL

HARD RULES:
- No long analysis
- No essay
- No fake source numbers like [1], [2]
- No "НЕ ПОДТВЕРЖДЕНО" blocks as final answer
- No duplicated summary sections
- No generic advice
- No old context
- Use only current user query
- If user asks suppliers/prices, return direct supplier rows
- Every row must contain direct URL
- Phone is mandatory when visible in search result; if phone is not visible write "телефон не найден"
- Prefer Saint Petersburg / Ленобласть when requested
- Prefer official supplier/site/marketplace pages over articles
- If exact brand spelling is suspicious, search both original and corrected spelling, but keep original in output

FORMAT STRICTLY:

Найдено: <N> вариантов

| № | Поставщик | Город | Цена | Ед. | Наличие | Доставка | Телефон | Ссылка |
|---|-----------|-------|------|-----|---------|----------|---------|--------|
| 1 | ... | ... | ... | ... | ... | ... | ... | https://... |

Лучший вариант:
<1 строка: поставщик, цена, почему>

Проверить звонком:
1. актуальная цена
2. наличие
3. доставка
4. НДС/счёт
5. точная марка/толщина/размер

Отброшено:
- <только если реально есть что отбросить, кратко>

If fewer than 3 supplier rows are found:
Return what is found and write:
"Найдено меньше 3 прямых поставщиков, нужен повторный поиск по расширенным площадкам"

"""


# === P6F_TOPIC500_CONTEXT_SANITIZER_V1 ===
# FACT: removes old supplier tables / Trust Score / TCO / "НЕ ПОДТВЕРЖДЕНО" / "ЭТАП N"
# / naked [1][2][3] markers from search context BEFORE Perplexity call.
# Exposed as _p6f_ts_sanitize_payload(payload) — used by callers via append-wraps.
import re as _p6f_ts_re
import logging as _p6f_ts_logging

_P6F_TS_LOG = _p6f_ts_logging.getLogger("ai_router")

_P6F_TS_NOISE_PATTERNS = [
    r"(?im)^\s*Trust\s*Score[^\n]*\n?",
    r"(?im)^\s*TCO[^\n]*\n?",
    r"(?im)^\s*НЕ\s*ПОДТВЕРЖД[^\n]*\n?",
    r"(?im)^\s*ЭТАП\s*\d+[^\n]*\n?",
    r"(?im)^\s*Risk\s*Score[^\n]*\n?",
    r"(?im)^\s*Review\s*Trust[^\n]*\n?",
    r"(?im)^\s*\|[^\n]*Поставщик[^\n]*\|[^\n]*\n?",
    r"(?im)^\s*\|[^\n]*Цена[^\n]*\|[^\n]*Источник[^\n]*\n?",
    r"(?<![a-zA-Z0-9.])\[\d+\](?![\(\:])",
]

_P6F_TS_SUPPLIER_TABLE = _p6f_ts_re.compile(
    r"(?ims)\n\s*\|.*?Поставщик.*?\|\s*\n(\s*\|[-: ]+\|.*\n)?(\s*\|.*\n){1,40}",
)

def _p6f_ts_sanitize_text(text):
    if not text:
        return ""
    s = str(text)
    s = _P6F_TS_SUPPLIER_TABLE.sub("\n", s)
    for p in _P6F_TS_NOISE_PATTERNS:
        s = _p6f_ts_re.sub(p, "", s)
    s = _p6f_ts_re.sub(r"\n{3,}", "\n\n", s).strip()
    return s

def _p6f_ts_is_search_topic(payload):
    try:
        return int((payload or {}).get("topic_id", 0) or 0) == 500
    except Exception:
        return False

def _p6f_ts_sanitize_payload(payload):
    """
    Returns a NEW dict (shallow copy) with sanitized search_context and user_text
    for topic_500 procurement search. Other topics pass through unchanged.
    """
    if not isinstance(payload, dict):
        return payload
    if not _p6f_ts_is_search_topic(payload):
        return payload
    out = dict(payload)
    if "search_context" in out and out["search_context"]:
        before_len = len(str(out["search_context"]))
        out["search_context"] = _p6f_ts_sanitize_text(out["search_context"])
        after_len = len(str(out["search_context"]))
        if before_len != after_len:
            _P6F_TS_LOG.info(
                "P6F_TS_SANITIZED_SEARCH_CONTEXT topic=500 chat=%s before=%d after=%d removed=%d",
                out.get("chat_id"), before_len, after_len, before_len - after_len,
            )
    for key in ("raw_input", "normalized_input", "user_text"):
        if key in out and out[key] and isinstance(out[key], str):
            out[key] = _p6f_ts_sanitize_text(out[key])
    return out

try:
    _P6F_TS_LOG.info("P6F_TOPIC500_CONTEXT_SANITIZER_V1_LOADED")
except Exception:
    pass
# === END_P6F_TOPIC500_CONTEXT_SANITIZER_V1 ===

# === P6F_TOPIC500_SANITIZER_AI_ROUTER_BIND_20260504_V1 ===
# FACT: wraps process_ai_task at module level so callers that re-import
# inside functions (e.g., sample_template_engine line 5132) pick up the
# sanitized version on every call.
try:
    _P6F_TS_AR_ORIG_PROCESS_AI_TASK = process_ai_task
    if not getattr(_P6F_TS_AR_ORIG_PROCESS_AI_TASK, "_p6f_ts_ar_wrapped", False):
        async def _p6f_ts_ar_wrapped_process_ai_task(payload):
            try:
                payload = _p6f_ts_sanitize_payload(payload)
            except Exception as _e:
                _P6F_TS_LOG.warning("P6F_TS_AR_SANITIZE_ERR %s", _e)
            return await _P6F_TS_AR_ORIG_PROCESS_AI_TASK(payload)
        _p6f_ts_ar_wrapped_process_ai_task._p6f_ts_ar_wrapped = True
        process_ai_task = _p6f_ts_ar_wrapped_process_ai_task
        _P6F_TS_LOG.info("P6F_TOPIC500_SANITIZER_AI_ROUTER_BIND_INSTALLED")
except Exception as _e:
    _P6F_TS_LOG.exception("P6F_TS_AR_BIND_INSTALL_ERR %s", _e)
# === END_P6F_TOPIC500_SANITIZER_AI_ROUTER_BIND_20260504_V1 ===


# === P6G_PAYLOAD_SANITIZER_EXTENDED_FIELDS_V1 ===
# FACT: extends P6F_TS_sanitize_payload to clean MORE fields where stale
# context can leak: memory_context, archive_context, full_context, history,
# context, pin_context, parent_context.
import logging as _p6g_pse_logging
_P6G_PSE_LOG = _p6g_pse_logging.getLogger("ai_router")

_P6G_PSE_EXTRA_FIELDS = (
    "memory_context", "archive_context", "full_context", "history",
    "context", "pin_context", "parent_context",
)

try:
    _P6G_PSE_ORIG_SANITIZE = _p6f_ts_sanitize_payload
    if not getattr(_P6G_PSE_ORIG_SANITIZE, "_p6g_pse_wrapped", False):
        def _p6f_ts_sanitize_payload(payload):
            out = _P6G_PSE_ORIG_SANITIZE(payload)
            if not isinstance(out, dict):
                return out
            try:
                topic_id = int((out or {}).get("topic_id", 0) or 0)
            except Exception:
                topic_id = 0
            if topic_id != 500:
                return out
            cleaned_count = 0
            for f in _P6G_PSE_EXTRA_FIELDS:
                if f in out and out[f] and isinstance(out[f], str):
                    before = len(out[f])
                    out[f] = _p6f_ts_sanitize_text(out[f])
                    after = len(out[f])
                    if before != after:
                        cleaned_count += 1
            if cleaned_count:
                _P6G_PSE_LOG.info(
                    "P6G_PSE_EXTRA_FIELDS_CLEANED topic=500 fields_changed=%d", cleaned_count,
                )
            return out
        _p6f_ts_sanitize_payload._p6g_pse_wrapped = True
        _P6G_PSE_LOG.info("P6G_PAYLOAD_SANITIZER_EXTENDED_FIELDS_V1_INSTALLED")
except Exception as _e:
    _P6G_PSE_LOG.exception("P6G_PSE_INSTALL_ERR %s", _e)
# === END_P6G_PAYLOAD_SANITIZER_EXTENDED_FIELDS_V1 ===

====================================================================================================
END_FILE: core/ai_router.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/__init__.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
====================================================================================================

====================================================================================================
END_FILE: core/__init__.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/active_dialog_state.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 35e86af58d10e00979f331b0ec69c905597f26583ae97bc756413888989df1a6
====================================================================================================
# === ACTIVE_DIALOG_STATE_V1 ===
# === UNIFIED_CONTEXT_PRIORITY_V1 ===
# === SHORT_CONTROL_SAFE_ROUTER_V1 ===
from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional

BASE = "/root/.areal-neva-core"
MEM_DB = os.path.join(BASE, "data/memory.db")

SHORT_CONTROLS = {
    "да", "ок", "окей", "+", "ага", "делай", "делаем", "дальше", "продолжай",
    "покажи", "скинь", "отбой", "закрывай", "готово", "что дальше", "ну что",
}

def _s(v: Any, limit: int = 4000) -> str:
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        try:
            v = json.dumps(v, ensure_ascii=False)
        except Exception:
            v = str(v)
    return str(v).strip()[:limit]

def clean_voice(text: str) -> str:
    return re.sub(r"^\s*\[VOICE\]\s*", "", text or "", flags=re.I).strip()

def is_short_control(text: str) -> bool:
    t = clean_voice(text).lower().strip(" .,!?:;—-")
    return t in SHORT_CONTROLS or (len(t.split()) <= 3 and any(x in t for x in SHORT_CONTROLS))

def _task_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {k: row[k] for k in row.keys()}

def last_active_task(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        SELECT * FROM tasks
        WHERE chat_id=? AND COALESCE(topic_id,0)=?
          AND state IN ('NEW','IN_PROGRESS','WAITING_CLARIFICATION','AWAITING_CONFIRMATION')
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id or 0)),
    ).fetchone()
    return _task_row_to_dict(row) if row else None

def last_file_task(conn: sqlite3.Connection, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        SELECT * FROM tasks
        WHERE chat_id=? AND COALESCE(topic_id,0)=?
          AND (
            input_type IN ('drive_file','file','document','photo','image')
            OR raw_input LIKE '%file_id%'
            OR raw_input LIKE '%file_name%'
            OR result LIKE '%drive.google%'
            OR result LIKE '%docs.google%'
            OR result LIKE '%.xlsx%'
            OR result LIKE '%.pdf%'
            OR result LIKE '%.docx%'
          )
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (str(chat_id), int(topic_id or 0)),
    ).fetchone()
    return _task_row_to_dict(row) if row else None

def _memory_lookup(chat_id: str, topic_id: int, query: str = "") -> str:
    if not os.path.exists(MEM_DB):
        return ""
    q = f"%{query[:40]}%" if query else "%"
    out = []
    try:
        con = sqlite3.connect(MEM_DB)
        rows = con.execute(
            """
            SELECT key, value, timestamp FROM memory
            WHERE chat_id=? AND key LIKE ?
              AND (
                key LIKE ? OR value LIKE ? OR key LIKE ? OR key LIKE ?
              )
            ORDER BY timestamp DESC
            LIMIT 8
            """,
            (
                str(chat_id),
                f"topic_{int(topic_id or 0)}_%",
                "%file%",
                q,
                "%artifact%",
                "%archive%",
            ),
        ).fetchall()
        con.close()
        for k, v, ts in rows:
            out.append(f"{ts} | {k} | {_s(v, 700)}")
    except Exception:
        return ""
    return "\n".join(out)

def build_active_context(conn: sqlite3.Connection, chat_id: str, topic_id: int, user_text: str = "") -> Dict[str, Any]:
    active = last_active_task(conn, chat_id, topic_id)
    last_file = last_file_task(conn, chat_id, topic_id)
    mem = _memory_lookup(chat_id, topic_id, clean_voice(user_text))
    return {
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "user_text": user_text,
        "active_task": active,
        "last_file": last_file,
        "memory": mem,
        "priority": "input -> reply parent -> active task -> last file -> pin -> short memory -> long memory -> archive",
    }

def maybe_handle_active_dialog(conn: sqlite3.Connection, task: sqlite3.Row, chat_id: str, topic_id: int) -> Optional[Dict[str, Any]]:
    raw = _s(task["raw_input"] if "raw_input" in task.keys() else "")
    text = clean_voice(raw)
    low = text.lower()

    if not text:
        return None

    # === ACTIVE_DIALOG_SKIP_EXPLICIT_ESTIMATE_CREATE_V1 ===
    create_words = (
        "сделай", "создай", "сформируй", "подготовь", "составь",
        "посчитай", "рассчитай", "выгрузи", "сохрани", "оформи"
    )
    estimate_words = (
        "смет", "расчет", "расчёт", "xlsx", "excel", "эксель",
        "pdf", "ндс", "итог", "объем", "объём", "расценк", "позици"
    )
    followup_words = (
        "я тебе скидывал", "уже скидывал", "где файл", "где смета",
        "что дальше", "дальше то что", "ты сделал", "что мы делали",
        "какие последние", "покажи прошл", "найди прошл", "помнишь"
    )
    if (
        any(w in low for w in create_words)
        and any(w in low for w in estimate_words)
        and not any(w in low for w in followup_words)
    ):
        return None
    # === END_ACTIVE_DIALOG_SKIP_EXPLICIT_ESTIMATE_CREATE_V1 ===

    # === ACTIVE_DIALOG_SKIP_EXPLICIT_PROJECT_CREATE_V1 ===
    project_create_words = (
        "сделай", "делай", "создай", "сформируй", "подготовь", "разработай",
        "оформи", "выгрузи", "сохрани", "нарисуй", "собери"
    )
    project_words = (
        "проект", "кж", "кд", "км", "кмд", "ар",
        "фундамент", "фундаментн", "плита", "плиты", "плиту",
        "армирован", "арматур", "dxf", "dwg", "чертеж", "чертёж", "конструктив"
    )
    if (
        any(w in low for w in project_create_words)
        and any(w in low for w in project_words)
        and not any(w in low for w in followup_words)
    ):
        return None
    # === END_ACTIVE_DIALOG_SKIP_EXPLICIT_PROJECT_CREATE_V1 ===

    file_followup = any(x in low for x in (
        "скидывал файл", "скидывал смету", "какой файл", "что дальше", "дальше то что",
        "покажи файл", "где файл", "где смета", "что с файлом", "по этому файлу",
    ))

    if file_followup:
        try:
            from core.file_memory_bridge import build_file_followup_answer
            ans = build_file_followup_answer(str(chat_id), int(topic_id or 0), raw, limit=8)
            if ans:
                return {
                    "handled": True,
                    "state": "DONE",
                    "result": ans,
                    "event": "ACTIVE_DIALOG_STATE_V1:FILE_FOLLOWUP_DONE",
                }
        except Exception as e:
            return {
                "handled": True,
                "state": "FAILED",
                "result": "",
                "error": f"ACTIVE_DIALOG_FILE_FOLLOWUP_ERR:{e}",
                "event": "ACTIVE_DIALOG_STATE_V1:FILE_FOLLOWUP_FAILED",
            }

    if is_short_control(text):
        ctx = build_active_context(conn, chat_id, topic_id, raw)
        active = ctx.get("active_task")
        last_file = ctx.get("last_file")
        if active:
            res = _s(active.get("result") or active.get("raw_input"), 1200)
            return {
                "handled": True,
                "state": "DONE",
                "result": f"Активный контекст найден\nЗадача: {active.get('id')}\nСтатус: {active.get('state')}\nКратко: {res}",
                "event": "ACTIVE_DIALOG_STATE_V1:SHORT_CONTROL_ACTIVE_TASK",
            }
        if last_file:
            res = _s(last_file.get("result") or last_file.get("raw_input"), 1200)
            return {
                "handled": True,
                "state": "DONE",
                "result": f"Последний файловый контекст найден\nЗадача: {last_file.get('id')}\nСтатус: {last_file.get('state')}\nКратко: {res}",
                "event": "ACTIVE_DIALOG_STATE_V1:SHORT_CONTROL_LAST_FILE",
            }

    return None

def save_dialog_event(chat_id: str, topic_id: int, key: str, value: Any) -> None:
    if not os.path.exists(MEM_DB):
        return
    try:
        con = sqlite3.connect(MEM_DB)
        con.execute(
            "INSERT INTO memory(chat_id,key,value,timestamp) VALUES(?,?,?,?)",
            (
                str(chat_id),
                f"topic_{int(topic_id or 0)}_dialog_{key}",
                json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        con.commit()
        con.close()
    except Exception:
        pass
# === END_SHORT_CONTROL_SAFE_ROUTER_V1 ===
# === END_UNIFIED_CONTEXT_PRIORITY_V1 ===
# === END_ACTIVE_DIALOG_STATE_V1 ===

====================================================================================================
END_FILE: core/active_dialog_state.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/archive_distributor.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 27d2d0630d027aeeb85fccc7c64c2907e804ba96faf7eae9be72c49f32230cb8
====================================================================================================
# === ARCHIVE_DISTRIBUTOR_V1 ===
# Читает timeline.jsonl → определяет топик → раскладывает в memory.db
import json, os, re, logging, sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

BASE = Path("/root/.areal-neva-core")
MEM_DB = str(BASE / "data/memory.db")
CHAT_ID = "-1003725299009"

# Сигнатуры топиков по контенту
_TOPIC_SIGNATURES = {
    2:    ["стройк", "смет", "кровл", "фасад", "фундамент", "металлочерепиц", "профнастил",
           "ангар", "бетон", "арматур", "утеплитель", "монтаж", "кж", "ар ", "кд "],
    5:    ["технадзор", "дефект", "акт осмотр", "нарушени", "предписани", "сп ", "гост", "снип",
           "инспекц", "фото дефект"],
    500:  ["найди", "поищи", "цена", "стоимость", "avito", "ozon", "wildberries", "поставщик",
           "купить", "маркет", "ral", "профлист"],
    961:  ["toyota", "hiace", "запчаст", "brembo", "авто", "машин", "vin", "oem", "разборк",
           "двигател", "подвеск"],
    3008: ["код", "python", "патч", "функци", "верификац", "архитектур", "task_worker",
           "telegram_daemon", "оркестр"],
}

def _detect_topic(text: str) -> int:
    low = text.lower()
    scores = {}
    for topic_id, keywords in _TOPIC_SIGNATURES.items():
        scores[topic_id] = sum(1 for kw in keywords if kw in low)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 0  # 0 = общий

def _ensure_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory
        (chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)
    """)

def distribute_timeline(timeline_path: str, chat_id: str = CHAT_ID, dry_run: bool = False) -> dict:
    """
    Читает timeline.jsonl → раскладывает записи в memory.db по топикам.
    Возвращает статистику.
    """
    p = Path(timeline_path)
    if not p.exists():
        return {"ok": False, "reason": "FILE_NOT_FOUND"}

    conn = sqlite3.connect(MEM_DB)
    conn.row_factory = sqlite3.Row
    _ensure_table(conn)

    stats = {"total": 0, "distributed": 0, "skipped": 0, "by_topic": {}}
    seen_keys = set()

    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue

            stats["total"] += 1

            # Собираем текст для классификации
            text_parts = []
            # timeline.jsonl имеет структуру {"timestamp":..., "data": {...}}
            data_block = entry.get("data") or entry
            if isinstance(data_block, dict):
                for field in ["raw_text", "text", "message", "content", "result",
                              "raw_input", "value", "system", "architecture",
                              "pipeline", "memory", "pending", "decisions"]:
                    v = data_block.get(field)
                    if v and isinstance(v, str) and len(v) > 10:
                        text_parts.append(v[:800])
            # тоже проверяем корень
            for field in ["text", "message", "content"]:
                v = entry.get(field)
                if v and isinstance(v, str):
                    text_parts.append(v[:400])
            text = " ".join(text_parts)[:3000]

            if not text or len(text) < 20:
                stats["skipped"] += 1
                continue

            # Определяем топик
            topic_id = _detect_topic(text)

            # Формируем ключ
            ts = entry.get("timestamp") or entry.get("ts") or entry.get("created_at") or "2026"
            ts_short = str(ts)[:10].replace("-", "")
            dedup_key = f"topic_{topic_id}_archive_{ts_short}_{hash(text) % 100000}"

            if dedup_key in seen_keys:
                stats["skipped"] += 1
                continue
            seen_keys.add(dedup_key)

            value = text[:5000]

            if not dry_run:
                # Проверяем нет ли уже такой записи
                existing = conn.execute(
                    "SELECT 1 FROM memory WHERE chat_id=? AND key=?",
                    (chat_id, dedup_key)
                ).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO memory (chat_id, key, value, timestamp) VALUES (?, ?, ?, ?)",
                        (chat_id, dedup_key, value, str(ts)[:19])
                    )

            stats["distributed"] += 1
            stats["by_topic"][topic_id] = stats["by_topic"].get(topic_id, 0) + 1

    if not dry_run:
        conn.commit()
    conn.close()

    return {"ok": True, **stats}

def run_distribution(chat_id: str = CHAT_ID) -> dict:  # CHAT_EXPORTS_POLICY_V1_WIRED
    """Запустить распределение для всех timeline.jsonl чата"""
    results = {}
    chats_dir = BASE / "data/memory_files/CHATS"
    if not chats_dir.exists():
        return {"ok": False, "reason": "NO_CHATS_DIR"}

    for chat_dir in chats_dir.iterdir():
        if not chat_dir.is_dir():
            continue
        timeline = chat_dir / "timeline.jsonl"
        if timeline.exists():
            r = distribute_timeline(str(timeline), chat_id=chat_id)
            results[str(timeline)] = r
            logger.info("ARCHIVE_DISTRIBUTED file=%s stats=%s", timeline, r)

    return {"ok": True, "files": results}

def _load_archive_for_topic(chat_id: str, topic_id: int, user_text: str = "", limit: int = 5) -> str:
    """
    Загрузить архивный контекст для топика из memory.db.
    Используется в _load_archive_context.
    """
    if not os.path.exists(MEM_DB):
        return ""
    conn = sqlite3.connect(MEM_DB)
    conn.row_factory = sqlite3.Row
    try:
        _ensure_table(conn)
        key_pattern = f"topic_{topic_id}_archive_%"
        rows = conn.execute(
            """SELECT key, value FROM memory
               WHERE chat_id=? AND key GLOB ?
               ORDER BY timestamp DESC LIMIT ?""",
            (str(chat_id), key_pattern, limit * 3)
        ).fetchall()

        if not rows:
            return ""

        # Фильтрация по релевантности если есть запрос
        if user_text:
            query_words = set(w for w in user_text.lower().split() if len(w) > 3)
            scored = []
            for row in rows:
                val = str(row["value"]).lower()
                score = sum(1 for w in query_words if w in val)
                scored.append((score, str(row["value"])[:500]))
            scored.sort(reverse=True)
            relevant = [v for s, v in scored if s > 0][:limit]
        else:
            relevant = [str(r["value"])[:500] for r in rows[:limit]]

        return "\n---\n".join(relevant) if relevant else ""
    except Exception as e:
        logger.warning("ARCHIVE_LOAD_ERR topic=%s err=%s", topic_id, e)
        return ""
    finally:
        conn.close()

try:
    from core.chat_exports_policy import get_canonical_exports_dir as _ced
except Exception:
    _ced = None

if __name__ == "__main__":
    print("Running archive distribution...")
    result = run_distribution()
    print(json.dumps(result, ensure_ascii=False, indent=2))
# === END ARCHIVE_DISTRIBUTOR_V1 ===

====================================================================================================
END_FILE: core/archive_distributor.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/archive_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 04fdd1d0f6927a38b62f869f0a020b30b8cc81d798083d607f1a86d3c61c6e1e
====================================================================================================
# === FULLFIX_ARCHIVE_ENGINE_STAGE_6 ===
from __future__ import annotations
import json
import logging
from typing import Any, Dict, Optional

ARCHIVE_ENGINE_VERSION = "ARCHIVE_ENGINE_V1"
logger = logging.getLogger("task_worker")


class ArchiveEngine:
    """
    Stage 6 shadow mode: индексирует завершённую задачу в memory.db.
    Пишет short_summary, direction, engine, quality_gate_overall.
    Не блокирует доставку при ошибках.
    """

    def archive(self, payload: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "task_id":      str(payload.get("task_id") or payload.get("id") or ""),
            "chat_id":      str(payload.get("chat_id") or ""),
            "topic_id":     int(payload.get("topic_id") or 0),
            "direction":    str(payload.get("direction") or "general_chat"),
            "engine":       str(payload.get("engine") or "ai_router"),
            "input_type":   str(payload.get("input_type") or "text"),
            "raw_input":    str(payload.get("raw_input") or payload.get("raw_text") or "")[:300],
            "result_text":  str((result.get("result") or {}).get("text") or result.get("text") or "")[:500],
            "artifact_url": str(result.get("artifact_url") or result.get("drive_link") or ""),
            "qg_overall":   str((result.get("quality_gate_report") or {}).get("overall") or "unknown"),
            "qg_failed":    json.dumps((result.get("quality_gate_report") or {}).get("failed") or []),
            "search_plan":  json.dumps(payload.get("search_plan") or {}),
            "archive_version": ARCHIVE_ENGINE_VERSION,
            "shadow_mode":  True,
        }

        self._write_to_memory_api(record)
        return record

    def _write_to_memory_api(self, record: Dict[str, Any]):
        import urllib.request, urllib.error
        try:
            body = json.dumps(record).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8091/archive",  # PORT_FIX_V1,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=2)
            logger.info("FULLFIX_ARCHIVE_ENGINE_STAGE_6 archived task=%s dir=%s qg=%s",
                        record["task_id"], record["direction"], record["qg_overall"])
        except Exception as e:
            logger.warning("FULLFIX_ARCHIVE_ENGINE_STAGE_6 memory_api unavailable: %s", e)


def archive_task(payload, result):
    return ArchiveEngine().archive(payload, result)
# === END FULLFIX_ARCHIVE_ENGINE_STAGE_6 ===

====================================================================================================
END_FILE: core/archive_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/archive_guard.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 369b05cb9ddf9aaa9f7b05828f3752848557f9e062d44f74b5f5f290723dc64c
====================================================================================================
# === FINAL_CLOSURE_BLOCKER_FIX_V1_ARCHIVE_DUPLICATE_GUARD ===
from __future__ import annotations

import hashlib
import sqlite3
from typing import Any, Dict


def _clean(v) -> str:
    return "" if v is None else str(v).strip()


def content_hash(text: str) -> str:
    return hashlib.sha256(_clean(text).lower().encode("utf-8", "ignore")).hexdigest()


def ensure_archive_guard(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS archive_guard (
            id TEXT PRIMARY KEY,
            task_id TEXT,
            chat_id TEXT,
            topic_id INTEGER DEFAULT 0,
            content_hash TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_archive_guard_hash ON archive_guard(content_hash)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_archive_guard_task ON archive_guard(task_id)")


def should_archive(conn: sqlite3.Connection, task_id: str, chat_id: str, topic_id: int, content: str) -> Dict[str, Any]:
    ensure_archive_guard(conn)
    h = content_hash(content)
    row = conn.execute("SELECT task_id, created_at FROM archive_guard WHERE content_hash=? LIMIT 1", (h,)).fetchone()

    if row:
        return {"ok": False, "duplicate": True, "duplicate_task_id": row[0], "hash": h}

    gid = hashlib.sha1(f"{task_id}:{h}".encode()).hexdigest()
    conn.execute(
        "INSERT OR IGNORE INTO archive_guard (id, task_id, chat_id, topic_id, content_hash) VALUES (?,?,?,?,?)",
        (gid, task_id, str(chat_id), int(topic_id or 0), h),
    )
    return {"ok": True, "duplicate": False, "hash": h}


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_ARCHIVE_DUPLICATE_GUARD ===

====================================================================================================
END_FILE: core/archive_guard.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/artifact_pipeline.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 102fd4ccfe0880b0a831991f3fa9b45a968bf34f21d11c04fb785a7ab5f557e3
====================================================================================================
import os
import re
import csv
import json
import base64
import tempfile
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=True)

def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()

def _clean(text: str, limit: int = 12000) -> str:
    text = (text or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]

def _kind(file_name: str, mime_type: str = "") -> str:
    # === UNIVERSAL_FORMAT_REGISTRY_V1_KIND ===
    # === DWG_DXF_KIND_FIX_V1_ARTIFACT_PIPELINE ===
    try:
        from core.format_registry import classify_file
        return classify_file(file_name, mime_type).get("kind") or "binary"
    except Exception:
        ext = os.path.splitext((file_name or "").lower())[1]
        mime = (mime_type or "").lower()

        # drawing first: mimetypes may classify .dwg/.dxf as image/*
        if ext in (".dwg", ".dxf", ".ifc", ".rvt", ".rfa", ".skp", ".stl", ".obj", ".step", ".stp", ".iges", ".igs") or any(x in mime for x in ("dxf", "dwg", "ifc", "cad", "step", "stp", "iges", "igs")):
            return "drawing"
        if ext in (".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff", ".bmp", ".gif") or mime.startswith("image/"):
            return "image"
        if ext in (".xlsx", ".xls", ".xlsm", ".csv", ".ods", ".tsv") or "spreadsheet" in mime or mime in ("text/csv", "application/vnd.ms-excel"):
            return "table"
        if ext in (".pdf", ".docx", ".doc", ".txt", ".md", ".rtf", ".odt", ".html", ".htm", ".xml", ".json", ".yaml", ".yml") or mime in ("application/pdf", "text/plain"):
            return "document"
        if ext in (".ppt", ".pptx", ".odp", ".key"):
            return "presentation"
        if ext in (".zip", ".7z", ".rar", ".tar", ".gz", ".tgz"):
            return "archive"
        if ext in (".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".m4a", ".ogg"):
            return "media"
        return "binary"
    # === END_DWG_DXF_KIND_FIX_V1_ARTIFACT_PIPELINE ===
    # === END_UNIVERSAL_FORMAT_REGISTRY_V1_KIND ===


# === DOMAIN_CONTOUR_ROUTER_V1 ===
def _artifact_task_id(file_name: str, engine: str = "artifact") -> str:
    base = re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", os.path.splitext(os.path.basename(file_name or engine))[0]).strip("._")
    return (base or engine)[:80]

def _domain_flags(file_name: str, mime_type: str = "", user_text: str = "", topic_role: str = "") -> Dict[str, bool]:
    hay = f"{file_name}\n{mime_type}\n{user_text}\n{topic_role}".lower()
    estimate = any(x in hay for x in ("смет", "расчёт", "расчет", "вор", "ведомость объем", "ведомость объём", "estimate", "xlsx", "xls", "csv"))
    tech = any(x in hay for x in ("технадзор", "дефект", "акт", "осмотр", "нарушен", "предписан", "гост", "снип", "сп ", "фотофиксац", "трещин", "протеч", "скол"))
    project = any(x in hay for x in ("проект", "проектирован", "кж", "кмд", "км", "кр", "ар", "ов", "вк", "эом", "гп", "пз", "чертеж", "чертёж", "dxf", "dwg"))
    return {"estimate": estimate, "tech": tech, "project": project}


# === ESTIMATE_PDF_PACKAGE_V2 ===
def _pdf_escape_v2(text: str) -> str:
    return str(text or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

def _write_simple_pdf_v2(path: str, title: str, lines: List[str]) -> str:
    out = os.path.join(tempfile.gettempdir(), os.path.splitext(os.path.basename(path))[0] + "_estimate_summary.pdf")
    safe_lines = [_pdf_escape_v2(title or "Estimate summary")]
    safe_lines += [_pdf_escape_v2(x) for x in (lines or [])[:40]]

    stream_lines = ["BT", "/F1 11 Tf", "50 790 Td"]
    first = True
    for line in safe_lines:
        if not first:
            stream_lines.append("0 -16 Td")
        first = False
        stream_lines.append(f"({line[:105]}) Tj")
    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("utf-8", errors="ignore")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{i} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)+1}\n".encode())
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode())
    pdf.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())

    with open(out, "wb") as f:
        f.write(pdf)
    return out

def _zip_files_v2(files: List[str], name: str) -> str:
    import zipfile
    out = os.path.join(tempfile.gettempdir(), re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", name or "estimate_package").strip("._") + ".zip")
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in files or []:
            if f and os.path.exists(f):
                z.write(f, arcname=os.path.basename(f))
    return out
# === END_ESTIMATE_PDF_PACKAGE_V2 ===

async def _domain_estimate_artifact(local_path: str, file_name: str, mime_type: str, user_text: str, topic_role: str) -> Optional[Dict[str, Any]]:
    # === DOMAIN_ESTIMATE_PDF_XLSX_PACKAGE_V2 ===
    try:
        from core.estimate_engine import process_estimate_to_excel
        tid = _artifact_task_id(file_name, "estimate_artifact")
        res = await process_estimate_to_excel(local_path, tid, 0)

        if res and (res.get("success") or res.get("excel_path")) and res.get("excel_path"):
            excel_path = res.get("excel_path")
            link = res.get("drive_link") or ""
            lines = [
                f"Файл: {file_name}",
                "Engine: DOMAIN_ESTIMATE_ENGINE_V1",
                f"Drive: {link or 'не подтвержден'}",
                f"Status: {'OK' if excel_path else 'PARTIAL'}",
            ]
            if res.get("error"):
                lines.append(f"Ограничение: {res.get('error')}")

            pdf_path = _write_simple_pdf_v2(excel_path or local_path, "Сметный результат", lines)
            package = _zip_files_v2([excel_path, pdf_path], os.path.splitext(os.path.basename(file_name or "estimate"))[0] + "_estimate_package")

            summary = "Сметный файл обработан\nАртефакты: XLSX + PDF"
            if link:
                summary += f"\nExcel: {link}"
            else:
                summary += "\nExcel создан локально, Drive ссылка не подтверждена"
            summary += "\nPDF включён в ZIP пакет"

            return {
                "summary": summary,
                "artifact_path": package,
                "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_estimate_package.zip",
                "engine": "DOMAIN_ESTIMATE_ENGINE_V1",
                "drive_link": link,
                "extra_artifacts": [excel_path, pdf_path],
            }

        reason = (res or {}).get("error") or "ESTIMATE_ENGINE_NO_ARTIFACT"
        pdf_path = _write_simple_pdf_v2(local_path, "Сметный файл принят без расчётного результата", [
            f"Файл: {file_name}",
            f"Причина: {reason}",
            "Расчётные строки не подтверждены",
        ])
        package = _zip_files_v2([pdf_path], os.path.splitext(os.path.basename(file_name or "estimate"))[0] + "_estimate_diagnostic_package")
        return {
            "summary": f"Сметный файл принят, но расчётные строки не подтверждены\nПричина: {reason}\nСоздан диагностический PDF пакет",
            "artifact_path": package,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_estimate_diagnostic_package.zip",
            "engine": "DOMAIN_ESTIMATE_ENGINE_V1",
            "error": str(reason)[:300],
            "extra_artifacts": [pdf_path],
        }
    except Exception as e:
        pdf_path = _write_simple_pdf_v2(local_path, "Сметный engine недоступен", [
            f"Файл: {file_name}",
            f"Ошибка: {e}",
            "Расчётные строки не подтверждены",
        ])
        package = _zip_files_v2([pdf_path], os.path.splitext(os.path.basename(file_name or "estimate"))[0] + "_estimate_error_package")
        return {
            "summary": f"Сметный engine недоступен: {e}\nСоздан диагностический PDF пакет",
            "artifact_path": package,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_estimate_error_package.zip",
            "engine": "DOMAIN_ESTIMATE_ENGINE_V1",
            "error": str(e)[:300],
            "extra_artifacts": [pdf_path],
        }
    # === END_DOMAIN_ESTIMATE_PDF_XLSX_PACKAGE_V2 ===

async def _domain_technadzor_artifact(local_path: str, file_name: str, mime_type: str, user_text: str, topic_role: str, extracted_text: str = "") -> Optional[Dict[str, Any]]:
    try:
        from core.technadzor_engine import process_technadzor
        tid = _artifact_task_id(file_name, "technadzor_artifact")
        raw = "\n".join(x for x in [user_text or "", extracted_text or "", topic_role or ""] if x).strip()
        res = process_technadzor(
            conn=None,
            task_id=tid,
            chat_id="artifact_pipeline",
            topic_id=0,
            raw_input=raw or "Технический осмотр файла",
            file_name=file_name,
            local_path=local_path,
        )
        if res and res.get("ok"):
            art = res.get("artifact") or {}
            path = art.get("path") or ""
            link = art.get("drive_link") or ""
            summary = _clean(res.get("result_text") or "Акт технического осмотра сформирован", 6000)
            if link and link not in summary:
                summary += f"\n\nДокумент: {link}"
            return {
                "summary": summary,
                "artifact_path": path,
                "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_technadzor_act.docx",
                "engine": "DOMAIN_TECHNADZOR_ENGINE_V1",
                "drive_link": link,
            }
    except Exception as e:
        return {
            "summary": f"Технадзор engine недоступен: {e}",
            "artifact_path": "",
            "artifact_name": "",
            "engine": "DOMAIN_TECHNADZOR_ENGINE_V1",
            "error": str(e)[:300],
        }
    return None

async def _domain_project_document_artifact(local_path: str, file_name: str, mime_type: str, user_text: str, topic_role: str) -> Optional[Dict[str, Any]]:
    try:
        from core.project_document_engine import process_project_document
        tid = _artifact_task_id(file_name, "project_document")
        res = await process_project_document(
            file_path=local_path,
            file_name=file_name,
            user_text=user_text,
            topic_role=topic_role,
            task_id=tid,
            topic_id=0,
        )
        if res and res.get("success"):
            return {
                "summary": _clean(res.get("summary") or "Проектный документ обработан", 6000),
                "artifact_path": res.get("artifact_path"),
                "artifact_name": res.get("artifact_name") or f"{os.path.splitext(os.path.basename(file_name))[0]}_project_document_package.zip",
                "extra_artifacts": res.get("extra_artifacts") or [],
                "engine": "PROJECT_DOCUMENT_ENGINE_V1",
                "model": res.get("model") or {},
            }
    except Exception as e:
        return {
            "summary": f"Project document engine недоступен: {e}",
            "artifact_path": "",
            "artifact_name": "",
            "engine": "PROJECT_DOCUMENT_ENGINE_V1",
            "error": str(e)[:300],
        }
    return None
# === END_DOMAIN_CONTOUR_ROUTER_V1 ===

def _build_word(title: str, summary: str, defects: List[Dict[str, Any]], recommendations: List[str], sources: List[str]) -> str:
    from docx import Document

    fd, out = tempfile.mkstemp(prefix="artifact_", suffix=".docx", dir="/tmp")
    os.close(fd)

    doc = Document()
    doc.add_heading(title or "Результат обработки", level=1)

    if summary:
        doc.add_paragraph(_clean(summary, 12000))

    if sources:
        doc.add_heading("Источники", level=2)
        for s in sources:
            doc.add_paragraph(_s(s))

    doc.add_heading("Замечания", level=2)
    if defects:
        for idx, item in enumerate(defects, 1):
            p = doc.add_paragraph()
            p.add_run(f"{idx}. ").bold = True
            p.add_run(_s(item.get("title")) or "Замечание")
            sev = _s(item.get("severity"))
            if sev:
                p.add_run(f" [{sev}]")
            desc = _s(item.get("description"))
            if desc:
                doc.add_paragraph(desc)
    else:
        doc.add_paragraph("Замечания не выделены")

    doc.add_heading("Рекомендации", level=2)
    if recommendations:
        for r in recommendations:
            doc.add_paragraph(_s(r))
    else:
        doc.add_paragraph("Рекомендации не сформированы")

    doc.save(out)
    return out

def _build_excel(title: str, items: List[Dict[str, str]], summary: str, sources: List[str]) -> str:
    from openpyxl import Workbook

    fd, out = tempfile.mkstemp(prefix="artifact_", suffix=".xlsx", dir="/tmp")
    os.close(fd)

    wb = Workbook()
    ws = wb.active
    ws.title = "Результат"
    ws["A1"] = title or "Табличный результат"
    ws["A2"] = _clean(summary, 1000)

    row = 4
    headers = ["№", "Наименование", "Ед", "Кол-во", "Примечание"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=row, column=col, value=h)
    row += 1

    for idx, item in enumerate(items, 1):
        ws.cell(row=row, column=1, value=idx)
        ws.cell(row=row, column=2, value=_s(item.get("name")))
        ws.cell(row=row, column=3, value=_s(item.get("unit")))
        ws.cell(row=row, column=4, value=_s(item.get("qty")))
        ws.cell(row=row, column=5, value=_s(item.get("note")))
        row += 1

    src = wb.create_sheet("Источники")
    for idx, s in enumerate(sources, 1):
        src.cell(row=idx, column=1, value=_s(s))

    wb.save(out)
    return out

def _extract_pdf(path: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        parts = []
        for page in reader.pages:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                pass
        return _clean("\n".join(parts), 12000)
    except Exception as e:
        return f"PDF_PARSE_ERROR: {e}"

def _extract_docx(path: str) -> str:
    try:
        from docx import Document
        doc = Document(path)
        return _clean("\n".join(p.text for p in doc.paragraphs if p.text), 12000)
    except Exception as e:
        return f"DOCX_PARSE_ERROR: {e}"

def _extract_txt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return _clean(f.read(), 12000)
    except Exception as e:
        return f"TXT_PARSE_ERROR: {e}"

def _extract_table_items(path: str, file_name: str) -> List[Dict[str, str]]:
    rows: List[List[str]] = []
    ext = os.path.splitext((file_name or "").lower())[1]

    try:
        if ext == ".csv":
            with open(path, "r", encoding="utf-8", errors="ignore", newline="") as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    rows.append([_s(x) for x in row])
                    if idx >= 300:
                        break
        else:
            from openpyxl import load_workbook
            wb = load_workbook(path, data_only=True, read_only=True)
            for ws in wb.worksheets[:3]:
                rows.append([f"__SHEET__:{ws.title}"])
                for idx, row in enumerate(ws.iter_rows(values_only=True)):
                    rows.append([_s(x) for x in row])
                    if idx >= 300:
                        break
    except Exception as e:
        rows.append([f"TABLE_PARSE_ERROR: {e}"])

    items: List[Dict[str, str]] = []
    unit_re = re.compile(r"\b(м2|м3|м\.п\.|п\.м\.|шт|кг|тн|т|м)\b", re.I)
    qty_re = re.compile(r"^\d+[.,]?\d*$")

    for row in rows:
        if not row:
            continue
        if len(row) == 1 and _s(row[0]).startswith("__SHEET__:"):
            continue

        cleaned = [_s(x) for x in row if _s(x)]
        if not cleaned:
            continue

        name = cleaned[0]
        unit = ""
        qty = ""
        note = ""

        for cell in cleaned[1:]:
            if not unit:
                m = unit_re.search(cell)
                if m:
                    unit = m.group(1)
                    continue
            if not qty and qty_re.match(cell.replace(" ", "")):
                qty = cell.replace(" ", "")
                continue
            note = (note + " | " + cell).strip(" |") if note else cell

        if len(name) < 2:
            continue

        items.append({
            "name": name[:500],
            "unit": unit[:32],
            "qty": qty[:64],
            "note": note[:500],
        })

        if len(items) >= 500:
            break

    return items

async def _vision_image(path: str, user_text: str, topic_role: str) -> Optional[Dict[str, Any]]:
    api_key = <REDACTED_SECRET>"OPENROUTER_API_KEY") or "").strip()
    if not api_key:
        return None

    base_url = (os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").strip().rstrip("/")
    model = (os.getenv("OPENROUTER_VISION_MODEL") or "google/gemini-2.5-flash").strip()

    ext = os.path.splitext(path)[1].lower().lstrip(".") or "jpeg"
    mime = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"

    try:
        import httpx
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        prompt = (
            "Ты анализируешь строительную фотофиксацию\n"
            f"Роль чата: {topic_role or 'технадзор'}\n"
            f"Задача пользователя: {user_text or 'проанализируй фото'}\n\n"
            "Верни только JSON вида:\n"
            "{\n"
            '  "summary": "краткое резюме",\n'
            '  "defects": [{"title":"...", "description":"...", "severity":"low|medium|high"}],\n'
            '  "recommendations": ["...", "..."]\n'
            "}"
        )

        body = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    ],
                }
            ],
            "temperature": 0.1,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=30.0)) as client:
            r = await client.post(f"{base_url}/chat/completions", headers=headers, json=body)
            r.raise_for_status()
            data = r.json()

        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in content)
        content = _clean(_s(content), 12000)

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {
                "summary": content[:3000],
                "defects": [],
                "recommendations": [],
            }

    except Exception:
        return None

    return None

async def analyze_downloaded_file(local_path: str, file_name: str, mime_type: str = "", user_text: str = "", topic_role: str = "") -> Optional[Dict[str, Any]]:
    kind = _kind(file_name, mime_type)
    sources = [file_name]

    if kind == "image":
        # === OCR_TABLE_TO_EXCEL_FULL_CLOSE_V1_ROUTE ===
        try:
            _ocr_hay = f"{file_name} {mime_type} {user_text} {topic_role}".lower()
            if any(_x in _ocr_hay for _x in ("смет", "таблиц", "вор", "excel", "xlsx", "расчет", "расчёт")):
                from core.ocr_table_engine import image_table_to_excel
                _ocr = await image_table_to_excel(local_path, _artifact_task_id(file_name, "ocr_table"), user_text, 0)
                if _ocr and _ocr.get("success"):
                    return {
                        "summary": _clean(_ocr.get("summary") or "Фото таблицы распознано", 4000),
                        "artifact_path": _ocr.get("artifact_path"),
                        "artifact_name": _ocr.get("artifact_name") or f"{os.path.splitext(os.path.basename(file_name))[0]}_ocr_table_package.zip",
                        "extra_artifacts": _ocr.get("extra_artifacts") or [],
                        "engine": "OCR_TABLE_TO_EXCEL_FULL_CLOSE_V1",
                        "model": {"rows": _ocr.get("rows") or []},
                    }
        except Exception as _ocr_e:
            import logging as _ocr_log
            _ocr_log.getLogger(__name__).warning("OCR_TABLE_TO_EXCEL_FULL_CLOSE_V1_ROUTE_ERR %s", _ocr_e)
        # === END_OCR_TABLE_TO_EXCEL_FULL_CLOSE_V1_ROUTE ===
        # === DOMAIN_TECHNADZOR_IMAGE_ASYNC_VISION_V2 ===
        flags = _domain_flags(file_name, mime_type, user_text, topic_role)
        vision_text = ""
        analysis = None

        if flags.get("tech") or not flags.get("estimate"):
            analysis = await _vision_image(local_path, user_text, topic_role)
            if isinstance(analysis, dict):
                vision_text = json.dumps(analysis, ensure_ascii=False)
            elif analysis:
                vision_text = str(analysis)

            routed = await _domain_technadzor_artifact(local_path, file_name, mime_type, user_text, topic_role, vision_text)
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                routed["engine"] = routed.get("engine") or "DOMAIN_TECHNADZOR_IMAGE_ASYNC_VISION_V2"
                return routed

        if analysis is None:
            analysis = await _vision_image(local_path, user_text, topic_role)

        if not analysis:
            routed = await _domain_technadzor_artifact(local_path, file_name, mime_type, user_text, topic_role, "Фото принято без vision-анализа")
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                return routed
            return None

        summary = _s(analysis.get("summary")) if isinstance(analysis, dict) else _s(analysis)
        summary = summary or "Фото проанализировано"
        defects = analysis.get("defects") if isinstance(analysis, dict) and isinstance(analysis.get("defects"), list) else []
        recommendations = analysis.get("recommendations") if isinstance(analysis, dict) and isinstance(analysis.get("recommendations"), list) else []
        artifact_path = _build_word("Акт замечаний по фотофиксации", summary, defects, [_s(x) for x in recommendations], sources)
        return {
            "summary": summary,
            "artifact_path": artifact_path,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_photo_report.docx",
            "engine": "DOMAIN_TECHNADZOR_IMAGE_ASYNC_VISION_V2",
        }
        # === END_DOMAIN_TECHNADZOR_IMAGE_ASYNC_VISION_V2 ===

    if kind == "table":
        flags = _domain_flags(file_name, mime_type, user_text, topic_role)
        if flags.get("estimate") or not flags.get("project"):
            routed = await _domain_estimate_artifact(local_path, file_name, mime_type, user_text, topic_role)
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                return routed

        items = _extract_table_items(local_path, file_name)
        summary = f"Нормализовано позиций: {len(items)}"
        artifact_path = _build_excel("Сметный/табличный результат", items, summary, sources)
        return {
            "summary": summary,
            "artifact_path": artifact_path,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_estimate.xlsx",
            "engine": "TABLE_FALLBACK_ENGINE",
        }

    if kind == "drawing":
        try:
            from core.dwg_engine import process_drawing_file
            data = process_drawing_file(
                local_path=local_path,
                file_name=file_name,
                mime_type=mime_type,
                user_text=user_text,
                topic_role=topic_role,
                task_id="artifact",
                topic_id=0,
            )
            if data and data.get("success"):
                return {
                    "summary": _clean(data.get("summary") or "DWG/DXF файл обработан", 4000),
                    "artifact_path": data.get("artifact_path"),
                    "artifact_name": data.get("artifact_name") or f"{os.path.splitext(os.path.basename(file_name))[0]}_dwg_dxf_project_package.zip",
                    "extra_artifacts": data.get("extra_artifacts") or [],
                    "engine": "DWG_DXF_PROJECT_CLOSE_V1",
                    "model": data.get("model") or {},
                }
            return {
                "summary": _clean((data or {}).get("summary") or (data or {}).get("error") or "DWG/DXF файл не обработан", 3000),
                "artifact_path": "",
                "artifact_name": "",
                "engine": "DWG_DXF_PROJECT_CLOSE_V1",
                "error": (data or {}).get("error") or "DRAWING_PROCESS_FAILED",
            }
        except Exception as e:
            return {
                "summary": f"DWG/DXF обработка завершилась ошибкой: {e}",
                "artifact_path": "",
                "artifact_name": "",
                "engine": "DWG_DXF_PROJECT_CLOSE_V1",
                "error": str(e)[:300],
            }

    if kind == "document":
        flags = _domain_flags(file_name, mime_type, user_text, topic_role)
        ext = os.path.splitext((file_name or "").lower())[1]
        if ext == ".pdf":
            domain_text = _extract_pdf(local_path)
        elif ext == ".docx":
            domain_text = _extract_docx(local_path)
        else:
            domain_text = _extract_txt(local_path)

        if flags.get("tech"):
            routed = await _domain_technadzor_artifact(local_path, file_name, mime_type, user_text, topic_role, domain_text)
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                return routed

        if flags.get("estimate"):
            routed = await _domain_estimate_artifact(local_path, file_name, mime_type, user_text, topic_role)
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                return routed

        if flags.get("project"):
            routed = await _domain_project_document_artifact(local_path, file_name, mime_type, user_text, topic_role)
            if routed and (routed.get("artifact_path") or routed.get("summary")):
                return routed

        summary = _clean(domain_text, 3000) if domain_text else "Документ обработан"
        artifact_path = _build_word("Сводка по документу", summary, [], [], sources)
        return {
            "summary": summary,
            "artifact_path": artifact_path,
            "artifact_name": f"{os.path.splitext(os.path.basename(file_name))[0]}_document_summary.docx",
            "engine": "DOCUMENT_FALLBACK_ENGINE",
        }

    # === UNIVERSAL_FILE_ENGINE_FALLBACK_V1 ===
    try:
        from core.universal_file_engine import process_universal_file
        data = process_universal_file(
            local_path=local_path,
            file_name=file_name,
            mime_type=mime_type,
            user_text=user_text,
            topic_role=topic_role,
            task_id=_artifact_task_id(file_name, "universal_file"),
            topic_id=0,
        )
        if data and data.get("success"):
            return {
                "summary": _clean(data.get("summary") or "Файл обработан универсальным контуром", 6000),
                "artifact_path": data.get("artifact_path"),
                "artifact_name": data.get("artifact_name") or f"{os.path.splitext(os.path.basename(file_name))[0]}_universal_file_package.zip",
                "extra_artifacts": data.get("extra_artifacts") or [],
                "engine": "UNIVERSAL_FILE_ENGINE_V1",
                "model": data.get("model") or {},
            }
    except Exception as e:
        return {
            "summary": f"Универсальный файловый контур завершился ошибкой: {e}",
            "artifact_path": "",
            "artifact_name": "",
            "engine": "UNIVERSAL_FILE_ENGINE_V1",
            "error": str(e)[:300],
        }
    return None
    # === END_UNIVERSAL_FILE_ENGINE_FALLBACK_V1 ===

# === FIX_DOMAIN_FLAGS_TOPIC_ROLE_ESTIMATE_BLEED_V1 ===
# topic_role for topic_2 = "Топик: СТРОЙКА | Направление: estimates"
# The word "estimate" in topic_role made estimate=True for EVERY file in topic_2.
# Fix: classify estimate only from file_name, mime_type, user_text — not topic_role.
_fdf_orig_domain_flags = _domain_flags

def _domain_flags(file_name: str, mime_type: str = "", user_text: str = "", topic_role: str = "") -> Dict[str, bool]:
    hay_no_role = f"{file_name}\n{mime_type}\n{user_text}".lower()
    estimate = any(x in hay_no_role for x in (
        "смет", "расчёт", "расчет", "вор", "ведомость объем", "ведомость объём",
        "estimate", "xlsx", "xls", "csv"
    ))
    orig = _fdf_orig_domain_flags(file_name, mime_type, user_text, topic_role)
    return {"estimate": estimate, "tech": orig["tech"], "project": orig["project"]}
# === END_FIX_DOMAIN_FLAGS_TOPIC_ROLE_ESTIMATE_BLEED_V1 ===

====================================================================================================
END_FILE: core/artifact_pipeline.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/artifact_upload_guard.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 3cf8290fd123e4a629b65742f93811b6a157d1d05bb63ad6532d3f931bf43b48
====================================================================================================
# === FULLFIX_14_ARTIFACT_UPLOAD_GUARD ===
# === UPLOAD_RETRY_QUEUE_UNIFICATION_V1 ===
# === HEAVY_FILE_STORAGE_POLICY_V1 ===
from __future__ import annotations
import logging
import os
import sqlite3
from typing import Any, Dict

logger = logging.getLogger(__name__)
_DB = "/root/.areal-neva-core/data/core.db"

def _ensure_retry_table(conn: sqlite3.Connection) -> None:
    conn.execute("""CREATE TABLE IF NOT EXISTS upload_retry_queue(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT, task_id TEXT, topic_id INTEGER, kind TEXT,
        attempts INTEGER DEFAULT 0, last_error TEXT,
        created_at TEXT DEFAULT (datetime('now')), last_attempt TEXT
    )""")

def _queue_retry(path: str, task_id: str, topic_id: int, kind: str, error: str) -> None:
    try:
        with sqlite3.connect(_DB, timeout=10) as c:
            _ensure_retry_table(c)
            c.execute(
                "INSERT INTO upload_retry_queue(path,task_id,topic_id,kind,last_error) VALUES(?,?,?,?,?)",
                (str(path), str(task_id), int(topic_id or 0), str(kind or "artifact"), str(error)),
            )
            try:
                c.execute(
                    "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
                    (str(task_id), f"UPLOAD_RETRY_QUEUE_UNIFICATION_V1:QUEUED:{kind}"),
                )
            except Exception:
                pass
            c.commit()
    except Exception as e:
        logger.warning("UPLOAD_RETRY_QUEUE_UNIFICATION_V1_ERR task=%s err=%s", task_id, e)

def _cleanup_heavy(path: str, link: str = "") -> bool:
    try:
        p = str(path or "")
        if not p or not os.path.exists(p):
            return False
        size = os.path.getsize(p)
        is_tmp = p.startswith("/tmp/") or p.startswith("/var/tmp/") or "/runtime/" in p
        if size >= 20 * 1024 * 1024 and is_tmp:
            os.remove(p)
            logger.info("HEAVY_FILE_STORAGE_POLICY_V1_CLEANED path=%s link=%s", p, link)
            return True
    except Exception as e:
        logger.warning("HEAVY_FILE_STORAGE_POLICY_V1_CLEAN_ERR path=%s err=%s", path, e)
    return False

def upload_or_fail(path: str, task_id: str, topic_id: int, kind: str = "artifact") -> Dict[str, Any]:
    if not path or not os.path.exists(str(path)):
        _queue_retry(path, task_id, topic_id, kind, "FILE_NOT_FOUND")
        return {"success": False, "error": "FILE_NOT_FOUND", "path": path, "queued": True}
    size = os.path.getsize(str(path))
    if size < 10:
        _queue_retry(path, task_id, topic_id, kind, "FILE_TOO_SMALL")
        return {"success": False, "error": "FILE_TOO_SMALL", "path": path, "size": size, "queued": True}
    tried = []
    try:
        from core.engine_base import upload_artifact_to_drive
        link = upload_artifact_to_drive(str(path), str(task_id), int(topic_id or 0))
        if link and str(link).startswith("http"):
            _cleanup_heavy(path, link)
            return {"success": True, "link": str(link), "drive_link": str(link),
                    "path": str(path), "kind": kind, "queued": False}
        tried.append("drive:no_link")
    except Exception as e:
        tried.append(f"drive:{e}")
    _queue_retry(path, task_id, topic_id, kind, "DRIVE_UPLOAD_FAILED")
    try:
        from core.engine_base import _telegram_fallback_send
        tg = _telegram_fallback_send(str(path), str(task_id), int(topic_id or 0))
        if tg:
            _cleanup_heavy(path, tg)
            return {"success": True, "link": str(tg), "telegram_link": str(tg),
                    "path": str(path), "kind": kind, "drive_failed": True,
                    "telegram_fallback": True, "queued": True}
    except Exception as e:
        tried.append(f"telegram:{e}")
    return {"success": False, "error": "UPLOAD_FAILED", "path": str(path),
            "size": size, "tried": tried, "queued": True}

def upload_many_or_fail(files, task_id: str, topic_id: int) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    links: Dict[str, str] = {}
    all_ok = True
    for f in files or []:
        if isinstance(f, str):
            path, kind = f, "artifact"
        elif isinstance(f, dict):
            path = f.get("path") or f.get("file") or f.get("artifact_path") or ""
            kind = f.get("kind") or "artifact"
        else:
            path, kind = str(f or ""), "artifact"
        r = upload_or_fail(str(path), str(task_id), int(topic_id or 0), str(kind))
        results[str(path)] = r
        if not (isinstance(r, dict) and r.get("success")):
            all_ok = False
        if isinstance(r, dict):
            link = str(r.get("link") or r.get("drive_link") or r.get("telegram_link") or "")
            if link:
                links[str(path)] = link
    return {"success": all_ok, "results": results, "links": links,
            "queued": any(isinstance(v, dict) and v.get("queued") for v in results.values())}
# === END_HEAVY_FILE_STORAGE_POLICY_V1 ===
# === END_UPLOAD_RETRY_QUEUE_UNIFICATION_V1 ===
# === END FULLFIX_14_ARTIFACT_UPLOAD_GUARD ===

====================================================================================================
END_FILE: core/artifact_upload_guard.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/audit_log.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 46ff0af7219a7e5548d4d189ecadce73909cb9ff63c0e3c64ea62933fa1976b3
====================================================================================================
# === AUDIT_LOG_V1 ===
import os, json, logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "audit.jsonl")

def audit(event: str, task_id: str = "", chat_id: str = "", details: dict = None):
    """Записать аудит-событие"""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "task_id": task_id,
        "chat_id": str(chat_id),
        "details": details or {},
    }
    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning("AUDIT_LOG_WRITE_ERR %s", e)

def tail_audit(n: int = 20) -> list:
    """Последние n записей аудита"""
    try:
        with open(_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [json.loads(l) for l in lines[-n:] if l.strip()]
    except Exception:
        return []
# === END AUDIT_LOG_V1 ===

====================================================================================================
END_FILE: core/audit_log.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/cad_project_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 6024e82541f8e08b15909858aa28306a471adeffab216b8fc3b23b819b273edc
====================================================================================================
# === FULLFIX_07_CAD_PROJECT_DOCUMENTATION_CLOSURE ===
import os
import re
import json
import math
import glob
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE = "/root/.areal-neva-core"
TEMPLATE_DIR = f"{BASE}/data/project_templates"

ENGINE = "FULLFIX_07_CAD_PROJECT_DOCUMENTATION_CLOSURE"

DEFAULT_FOUNDATION_SHEETS = [
    {"mark": "КЖ", "number": "0", "title": "Титульный лист"},
    {"mark": "КЖ", "number": "1", "title": "Общие данные"},
    {"mark": "КЖ", "number": "2", "title": "Ведомость листов"},
    {"mark": "КЖ", "number": "3", "title": "План фундаментной плиты"},
    {"mark": "КЖ", "number": "4", "title": "Разрез 1-1"},
    {"mark": "КЖ", "number": "5", "title": "Схема нижнего армирования"},
    {"mark": "КЖ", "number": "6", "title": "Схема верхнего армирования"},
    {"mark": "КЖ", "number": "7", "title": "Узлы и детали"},
    {"mark": "КЖ", "number": "8", "title": "Спецификация материалов"},
    {"mark": "КЖ", "number": "9", "title": "Ведомость расхода стали"},
]

DEFAULT_ROOF_SHEETS = [
    {"mark": "КД", "number": "0", "title": "Титульный лист"},
    {"mark": "КД", "number": "1", "title": "Общие данные"},
    {"mark": "КД", "number": "2", "title": "Ведомость листов"},
    {"mark": "КД", "number": "3", "title": "План кровли"},
    {"mark": "КД", "number": "4", "title": "План стропильной системы"},
    {"mark": "КД", "number": "5", "title": "Разрезы"},
    {"mark": "КД", "number": "6", "title": "Узлы кровли"},
    {"mark": "КД", "number": "7", "title": "Спецификация древесины"},
    {"mark": "КД", "number": "8", "title": "Спецификация крепежа"},
]

NORMATIVE_NOTES = [
    "СП 63.13330.2018 Бетонные и железобетонные конструкции",
    "СП 20.13330.2016 Нагрузки и воздействия",
    "ГОСТ 21.501-2018 Правила выполнения рабочей документации архитектурных и конструктивных решений",
    "ГОСТ 21.101-2020 Основные требования к проектной и рабочей документации",
    "ГОСТ 34028-2016 Прокат арматурный для железобетонных конструкций",
]

REBAR_WEIGHT_KG_M = {
    6: 0.222,
    8: 0.395,
    10: 0.617,
    12: 0.888,
    14: 1.21,
    16: 1.58,
    18: 2.00,
    20: 2.47,
    22: 2.98,
    25: 3.85,
}

def _clean(v: Any, limit: int = 10000) -> str:
    return str(v or "").replace("\x00", " ").strip()[:limit]

def _safe_name(v: Any) -> str:
    s = re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", _clean(v, 80))
    return s.strip("_") or "project"

def _font_name() -> str:
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
        for path in candidates:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont("ArealSans", path))
                return "ArealSans"
    except Exception:
        pass
    return "Helvetica"

def _load_templates() -> List[Dict[str, Any]]:
    out = []
    for p in sorted(glob.glob(f"{TEMPLATE_DIR}/PROJECT_TEMPLATE_MODEL__*.json"), key=os.path.getmtime, reverse=True):
        try:
            data = json.loads(Path(p).read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data["template_file"] = p
                out.append(data)
        except Exception:
            pass
    return out

def _choose_template(section: str, topic_id: int = 0) -> Dict[str, Any]:
    templates = _load_templates()
    if not templates:
        return {}
    section = _clean(section).upper()
    for tpl in templates:
        if topic_id and int(tpl.get("topic_id", 0) or 0) == int(topic_id) and _clean(tpl.get("project_type")).upper() == section:
            return tpl
    for tpl in templates:
        if _clean(tpl.get("project_type")).upper() == section:
            return tpl
    return templates[0]

def _num(text: str, default: float) -> float:
    try:
        return float(str(text).replace(",", "."))
    except Exception:
        return default

def _parse_mm(text: str, patterns: List[str], default: int) -> int:
    low = text.lower()
    for pat in patterns:
        m = re.search(pat, low, re.I)
        if m:
            return int(float(m.group(1).replace(",", ".")))
    return default

def parse_project_request(raw_input: str, template_hint: str = "") -> Dict[str, Any]:
    text = _clean(raw_input + " " + template_hint, 6000)
    low = text.lower()

    section = "КЖ"
    project_kind = "foundation_slab"
    if any(x in low for x in ["кров", "строп", "кд"]):
        section = "КД"
        project_kind = "roof"
    if any(x in low for x in [" ар ", "ар.", "архитект", "планиров", "фасад"]):  # SECTION_DETECTION_FIX_V1
        section = "АР"
        project_kind = "architectural"

    length_m = 10.0
    width_m = 10.0
    m = re.search(r"(\d+(?:[,.]\d+)?)\s*[xх×]\s*(\d+(?:[,.]\d+)?)\s*(?:м|m)?", low)
    if m:
        length_m = _num(m.group(1), 10.0)
        width_m = _num(m.group(2), 10.0)

    slab_mm = _parse_mm(low, [
        r"толщин[аы]?\D{0,30}(\d{2,4})\s*мм",
        r"плит[аы]?\D{0,30}(\d{2,4})\s*мм",
        r"бетон\D{0,30}(\d{2,4})\s*мм",
    ], 250)

    sand_mm = _parse_mm(low, [
        r"песчан\D{0,30}(\d{2,4})\s*мм",
        r"песок\D{0,30}(\d{2,4})\s*мм",
    ], 300)

    gravel_mm = _parse_mm(low, [
        r"щеб[её]н\D{0,30}(\d{2,4})\s*мм",
        r"щебень\D{0,30}(\d{2,4})\s*мм",
        r"основан\D{0,30}(\d{2,4})\s*мм",
    ], 150)

    rebar_step_mm = _parse_mm(low, [
        r"шаг\D{0,30}(\d{2,4})\s*мм",
        r"арматур\D{0,40}(\d{2,4})\s*мм",
    ], 200)

    rebar_diam_mm = 12
    md = re.search(r"(?:ø|ф|d|диаметр)\s*(\d{1,2})", low, re.I)
    if md:
        rebar_diam_mm = int(md.group(1))
    else:
        md = re.search(r"арматур[аы]?\D{0,30}(\d{1,2})(?!\d)", low, re.I)
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

    return {
        "project_name": "Проект фундаментной плиты" if project_kind == "foundation_slab" else "Проект по образцу",
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

def _normalize_sheet_register(template: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, str]]:
    section = data.get("section") or "КЖ"
    raw = template.get("sheet_register") or []
    sheets: List[Dict[str, str]] = []
    seen = set()

    for i, sh in enumerate(raw, 1):
        if isinstance(sh, dict):
            title = _clean(sh.get("title") or sh.get("name") or sh.get("sheet") or "", 120)
            number = _clean(sh.get("number") or sh.get("num") or str(i), 20)
            mark = _clean(sh.get("mark") or section, 20)
        else:
            title = _clean(sh, 120)
            number = str(i)
            mark = section
        if not title:
            continue
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        sheets.append({"mark": mark, "number": number, "title": title})

    sections = template.get("sections") or []
    if len(sheets) < 6 and sections:
        keys = ["общие", "ведомость", "план", "разрез", "армир", "спецификац", "узел", "фасад", "схема"]
        for sec in sections:
            title = _clean(sec, 120)
            if not title:
                continue
            low = title.lower()
            if not any(k in low for k in keys):
                continue
            if low in seen:
                continue
            seen.add(low)
            sheets.append({"mark": section, "number": str(len(sheets) + 1), "title": title})
            if len(sheets) >= 12:
                break

    base = DEFAULT_ROOF_SHEETS if data.get("project_kind") == "roof" else DEFAULT_FOUNDATION_SHEETS
    for sh in base:
        low = sh["title"].lower()
        if low not in seen:
            sheets.append({"mark": section, "number": str(len(sheets)), "title": sh["title"]})
            seen.add(low)

    fixed = []
    for idx, sh in enumerate(sheets[:20], 1):
        title = _clean(sh.get("title"), 120)
        mark = _clean(sh.get("mark"), 20) or section
        num = _clean(sh.get("number"), 20) or str(idx)
        fixed.append({"mark": mark, "number": num, "title": title})
    return fixed

def _calc_foundation(data: Dict[str, Any]) -> Dict[str, Any]:
    L = float(data["length_m"])
    W = float(data["width_m"])
    area = L * W
    slab_m = data["slab_mm"] / 1000.0
    sand_m = data["sand_mm"] / 1000.0
    gravel_m = data["gravel_mm"] / 1000.0
    step_m = data["rebar_step_mm"] / 1000.0
    d = int(data["rebar_diam_mm"])
    bars_x = int(math.floor(W / step_m)) + 1
    bars_y = int(math.floor(L / step_m)) + 1
    rebar_m_one_layer = bars_x * L + bars_y * W
    rebar_m_total = rebar_m_one_layer * 2
    weight = REBAR_WEIGHT_KG_M.get(d, (d * d) / 162.0)
    rebar_kg = rebar_m_total * weight
    return {
        "area_m2": round(area, 3),
        "concrete_m3": round(area * slab_m, 3),
        "sand_m3": round(area * sand_m, 3),
        "gravel_m3": round(area * gravel_m, 3),
        "bars_x": bars_x,
        "bars_y": bars_y,
        "rebar_m_total": round(rebar_m_total, 1),
        "rebar_kg": round(rebar_kg, 1),
        "rebar_t": round(rebar_kg / 1000.0, 3),
    }

def _frame(c, w, h, title: str, sheet_no: int, total: int, font: str, data: Dict[str, Any]) -> None:
    from reportlab.lib.units import mm
    c.setLineWidth(0.7)
    c.rect(10*mm, 10*mm, w - 20*mm, h - 20*mm)
    c.line(10*mm, 35*mm, w - 10*mm, 35*mm)
    c.line(w - 135*mm, 10*mm, w - 135*mm, 35*mm)
    c.line(w - 80*mm, 10*mm, w - 80*mm, 35*mm)
    c.line(w - 35*mm, 10*mm, w - 35*mm, 35*mm)
    c.setFont(font, 9)
    c.drawString(14*mm, 23*mm, _clean(title, 90))
    c.drawString(w - 132*mm, 23*mm, f"Раздел {data.get('section','КЖ')}")
    c.drawString(w - 77*mm, 23*mm, f"Лист {sheet_no}")
    c.drawString(w - 32*mm, 23*mm, f"Листов {total}")
    c.setFont(font, 7)
    c.drawString(14*mm, 15*mm, f"{ENGINE} · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.setFont(font, 14)
    c.drawString(18*mm, h - 18*mm, _clean(title, 120))
    c.setFont(font, 8)
    c.drawString(18*mm, h - 25*mm, f"{data.get('project_name','Проект')} · {data.get('length_m')}x{data.get('width_m')} м")

def _draw_lines(c, lines: List[str], x_mm: float, y_mm: float, font: str, size: int = 10, step: float = 7.5) -> None:
    from reportlab.lib.units import mm
    y = y_mm
    c.setFont(font, size)
    for line in lines:
        c.drawString(x_mm*mm, y*mm, _clean(line, 150))
        y -= step

def _draw_plan(c, w, h, font: str, data: Dict[str, Any], calc: Dict[str, Any], rebar: bool = False) -> None:
    from reportlab.lib.units import mm
    L = float(data["length_m"])
    W = float(data["width_m"])
    x0 = 55*mm
    y0 = 55*mm
    scale = min((w - 115*mm) / (L * 1000), (h - 130*mm) / (W * 1000))
    rw = L * 1000 * scale
    rh = W * 1000 * scale
    c.setLineWidth(1.2)
    c.rect(x0, y0, rw, rh)
    c.setFont(font, 9)
    c.drawString(x0, y0 - 8*mm, f"{L:g} м")
    c.saveState()
    c.translate(x0 - 8*mm, y0)
    c.rotate(90)
    c.drawString(0, 0, f"{W:g} м")
    c.restoreState()
    c.setDash(5, 3)
    c.line(x0, y0 + rh / 2, x0 + rw, y0 + rh / 2)
    c.line(x0 + rw / 2, y0, x0 + rw / 2, y0 + rh)
    c.setDash()

    if rebar:
        step_px = max(1.8*mm, data["rebar_step_mm"] * scale)
        c.setLineWidth(0.25)
        x = x0 + step_px
        while x < x0 + rw:
            c.line(x, y0, x, y0 + rh)
            x += step_px
        y = y0 + step_px
        while y < y0 + rh:
            c.line(x0, y, x0 + rw, y)
            y += step_px
        txt = f"Армирование: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм, верхняя и нижняя сетка"
    else:
        txt = f"Плита {L:g}x{W:g} м, площадь {calc['area_m2']} м²"

    c.setFont(font, 10)
    c.drawString(25*mm, (h/mm - 42)*mm, txt)

def _draw_section(c, w, h, font: str, data: Dict[str, Any]) -> None:
    from reportlab.lib.units import mm
    bx = 55*mm
    by = 70*mm
    total = data["slab_mm"] + data["gravel_mm"] + data["sand_mm"]
    k = 105*mm / total
    layers = [
        ("Фундаментная плита", data["slab_mm"], f"Бетон {data['concrete_class']}, защитный слой {data['cover_mm']} мм"),
        ("Щебёночное основание", data["gravel_mm"], "Уплотнение послойно"),
        ("Песчаная подушка", data["sand_mm"], "Уплотнение послойно"),
    ]
    y = by
    c.setLineWidth(0.8)
    for name, th, note in reversed(layers):
        hh = th * k
        c.rect(bx, y, 230*mm, hh)
        c.setFont(font, 10)
        c.drawString(bx + 5*mm, y + hh/2, f"{name}: {th} мм · {note}")
        y += hh
    c.setFont(font, 10)
    c.drawString(25*mm, 235*mm, "Разрез 1-1")
    c.drawString(25*mm, 225*mm, f"Армирование: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм")

def _draw_nodes(c, w, h, font: str, data: Dict[str, Any]) -> None:
    from reportlab.lib.units import mm
    c.setFont(font, 11)
    c.drawString(25*mm, 245*mm, "Типовые узлы")
    bx, by = 45*mm, 95*mm
    for i, title in enumerate(["Узел края плиты", "Узел защитного слоя", "Узел основания"], 0):
        x = bx + i * 115*mm
        c.setLineWidth(0.8)
        c.rect(x, by, 90*mm, 75*mm)
        c.line(x, by + 22*mm, x + 90*mm, by + 22*mm)
        c.line(x + 20*mm, by, x + 20*mm, by + 75*mm)
        c.setFont(font, 8)
        c.drawString(x + 4*mm, by + 63*mm, title)
        c.drawString(x + 4*mm, by + 15*mm, f"Защитный слой {data['cover_mm']} мм")
        c.drawString(x + 4*mm, by + 7*mm, f"Ø{data['rebar_diam_mm']} {data['rebar_class']}")

def _spec_rows(data: Dict[str, Any], calc: Dict[str, Any]) -> List[Tuple[str, str, Any, str]]:
    return [
        (f"Бетон {data['concrete_class']} для фундаментной плиты", "м³", calc["concrete_m3"], "по объёму плиты"),
        ("Песчаная подушка", "м³", calc["sand_m3"], "послойное уплотнение"),
        ("Щебёночное основание", "м³", calc["gravel_m3"], "послойное уплотнение"),
        (f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']}", "п.м", calc["rebar_m_total"], "верхняя и нижняя сетка"),
        (f"Арматура {data['rebar_class']} Ø{data['rebar_diam_mm']}", "т", calc["rebar_t"], "расчётный вес"),
    ]

def _draw_spec(c, w, h, font: str, rows: List[Tuple[str, str, Any, str]]) -> None:
    from reportlab.lib.units import mm
    x = 25*mm
    y = 235*mm
    c.setFont(font, 10)
    headers = ["№", "Наименование", "Ед.", "Кол-во", "Примечание"]
    widths = [12*mm, 150*mm, 22*mm, 32*mm, 110*mm]
    c.setLineWidth(0.5)
    cx = x
    for head, ww in zip(headers, widths):
        c.rect(cx, y, ww, 8*mm)
        c.drawString(cx + 2*mm, y + 2.3*mm, head)
        cx += ww
    y -= 8*mm
    for i, row in enumerate(rows, 1):
        vals = [str(i), row[0], row[1], str(row[2]), row[3]]
        cx = x
        for val, ww in zip(vals, widths):
            c.rect(cx, y, ww, 8*mm)
            c.drawString(cx + 2*mm, y + 2.3*mm, _clean(val, 55))
            cx += ww
        y -= 8*mm

def write_project_pdf(path: str, data: Dict[str, Any], template: Dict[str, Any], sheets: List[Dict[str, str]], calc: Dict[str, Any]) -> str:
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    font = _font_name()
    page_size = landscape(A3)
    w, h = page_size
    c = canvas.Canvas(path, pagesize=page_size)
    rows = _spec_rows(data, calc)
    total = len(sheets)

    for idx, sh in enumerate(sheets, 1):
        title = sh["title"]
        low = title.lower()
        _frame(c, w, h, f"{sh['mark']}-{sh['number']} {title}", idx, total, font, data)

        if "титул" in low:
            c.setFont(font, 18)
            c.drawCentredString(w/2, h - 85*mm, data["project_name"])
            c.setFont(font, 14)
            c.drawCentredString(w/2, h - 100*mm, f"Раздел {data['section']}")
            c.setFont(font, 11)
            c.drawCentredString(w/2, h - 116*mm, f"Параметры: {data['length_m']:g}x{data['width_m']:g} м, плита {data['slab_mm']} мм")
            c.drawCentredString(w/2, h - 130*mm, "Сформировано по сохранённому шаблону пользователя")
        elif "общ" in low or "данн" in low:
            lines = [
                f"Наименование: {data['project_name']}",
                f"Раздел: {data['section']}",
                f"Размер плиты: {data['length_m']:g} x {data['width_m']:g} м",
                f"Толщина плиты: {data['slab_mm']} мм",
                f"Основание: щебень {data['gravel_mm']} мм, песок {data['sand_mm']} мм",
                f"Бетон: {data['concrete_class']}",
                f"Арматура: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм",
                f"Площадь: {calc['area_m2']} м², бетон: {calc['concrete_m3']} м³",
                "",
                "Нормативная база:",
            ] + NORMATIVE_NOTES
            _draw_lines(c, lines, 25, 245, font, 10)
        elif "ведомость лист" in low or "состав" in low:
            lines = [f"{i}. {x['mark']}-{x['number']} {x['title']}" for i, x in enumerate(sheets, 1)]
            _draw_lines(c, lines, 25, 245, font, 10)
        elif "план" in low and "арм" not in low:
            _draw_plan(c, w, h, font, data, calc, rebar=False)
        elif "разрез" in low or "сечен" in low:
            _draw_section(c, w, h, font, data)
        elif "ниж" in low and "арм" in low:
            _draw_plan(c, w, h, font, data, calc, rebar=True)
            c.setFont(font, 10)
            c.drawString(25*mm, 220*mm, "Нижняя сетка армирования")
        elif "верх" in low and "арм" in low:
            _draw_plan(c, w, h, font, data, calc, rebar=True)
            c.setFont(font, 10)
            c.drawString(25*mm, 220*mm, "Верхняя сетка армирования")
        elif "арм" in low or "сетк" in low:
            _draw_plan(c, w, h, font, data, calc, rebar=True)
        elif "узел" in low or "детал" in low:
            _draw_nodes(c, w, h, font, data)
        elif "специф" in low or "материал" in low or "стали" in low:
            _draw_spec(c, w, h, font, rows)
        else:
            _draw_lines(c, [
                f"Лист: {title}",
                f"Раздел: {data['section']}",
                f"Размер: {data['length_m']:g}x{data['width_m']:g} м",
                f"Бетон: {data['concrete_class']}",
                f"Арматура: {data['rebar_class']} Ø{data['rebar_diam_mm']} шаг {data['rebar_step_mm']} мм",
            ], 25, 245, font, 10)

        c.showPage()

    c.save()
    return path

def write_project_dxf(path: str, data: Dict[str, Any], calc: Dict[str, Any]) -> str:
    import ezdxf
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    msp = doc.modelspace()

    for name, color in [("KJ_OUTLINE", 7), ("KJ_REBAR", 1), ("KJ_AXES", 3), ("KJ_TEXT", 2), ("KJ_SECTION", 5)]:
        doc.layers.new(name=name, dxfattribs={"color": color})

    L = float(data["length_m"]) * 1000
    W = float(data["width_m"]) * 1000
    step = float(data["rebar_step_mm"])

    pts = [(0,0), (L,0), (L,W), (0,W), (0,0)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": "KJ_OUTLINE", "closed": False})
    msp.add_line((L/2, 0), (L/2, W), dxfattribs={"layer": "KJ_AXES"})
    msp.add_line((0, W/2), (L, W/2), dxfattribs={"layer": "KJ_AXES"})

    x = step
    while x < L:
        msp.add_line((x, 0), (x, W), dxfattribs={"layer": "KJ_REBAR"})
        x += step
    y = step
    while y < W:
        msp.add_line((0, y), (L, y), dxfattribs={"layer": "KJ_REBAR"})
        y += step

    msp.add_text(
        f"{data['project_name']} {data['length_m']:g}x{data['width_m']:g}m",
        dxfattribs={"layer": "KJ_TEXT", "height": 250}
    ).set_placement((0, -900))

    msp.add_text(
        f"{data['concrete_class']} · {data['rebar_class']} D{data['rebar_diam_mm']} step {data['rebar_step_mm']}mm",
        dxfattribs={"layer": "KJ_TEXT", "height": 220}
    ).set_placement((0, -1300))

    sx = L + 1500
    y0 = 0
    layers = [
        ("Sand", data["sand_mm"]),
        ("Gravel", data["gravel_mm"]),
        ("Slab", data["slab_mm"]),
    ]
    for name, th in layers:
        msp.add_lwpolyline([(sx,y0),(sx+4000,y0),(sx+4000,y0+th),(sx,y0+th),(sx,y0)], dxfattribs={"layer": "KJ_SECTION"})
        msp.add_text(f"{name} {th}mm", dxfattribs={"layer": "KJ_TEXT", "height": 160}).set_placement((sx+4200, y0 + th/2))
        y0 += th

    doc.saveas(path)
    return path

def write_project_xlsx(path: str, data: Dict[str, Any], sheets: List[Dict[str, str]], calc: Dict[str, Any], template: Dict[str, Any]) -> str:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

    wb = Workbook()
    ws = wb.active
    ws.title = "Спецификация"

    headers = ["№", "Наименование", "Ед.изм", "Кол-во", "Примечание"]
    rows = _spec_rows(data, calc)

    ws.merge_cells("A1:E1")
    ws["A1"] = f"{data['project_name']} · {data['section']}"
    ws["A1"].font = Font(bold=True, size=13)
    ws["A1"].alignment = Alignment(horizontal="center")

    for c, h in enumerate(headers, 1):
        cell = ws.cell(3, c, h)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="DDEEFF")

    for r, row in enumerate(rows, 4):
        ws.cell(r, 1, r - 3)
        ws.cell(r, 2, row[0])
        ws.cell(r, 3, row[1])
        ws.cell(r, 4, row[2])
        ws.cell(r, 5, row[3])

    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 55
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 16
    ws.column_dimensions["E"].width = 35

    ws2 = wb.create_sheet("Ведомость листов")
    ws2.append(["№", "Марка", "Номер", "Наименование"])
    for i, sh in enumerate(sheets, 1):
        ws2.append([i, sh["mark"], sh["number"], sh["title"]])
    for col in ["A", "B", "C", "D"]:
        ws2.column_dimensions[col].width = 25

    ws3 = wb.create_sheet("Расчёт")
    for k, v in [
        ("Длина, м", data["length_m"]),
        ("Ширина, м", data["width_m"]),
        ("Площадь, м2", calc["area_m2"]),
        ("Бетон, м3", calc["concrete_m3"]),
        ("Песок, м3", calc["sand_m3"]),
        ("Щебень, м3", calc["gravel_m3"]),
        ("Арматура, п.м", calc["rebar_m_total"]),
        ("Арматура, т", calc["rebar_t"]),
    ]:
        ws3.append([k, v])
    ws3.column_dimensions["A"].width = 35
    ws3.column_dimensions["B"].width = 18

    wb.save(path)
    return path

def write_project_manifest(path: str, data: Dict[str, Any], template: Dict[str, Any], sheets: List[Dict[str, str]], calc: Dict[str, Any], files: Dict[str, str], links: Dict[str, str], task_id: str, topic_id: int) -> str:
    manifest = {
        "schema": "AREAL_PROJECT_DOCUMENTATION_PACKAGE_V1",
        "engine": ENGINE,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "topic_id": topic_id,
        "input": data.get("input"),
        "section": data.get("section"),
        "project_kind": data.get("project_kind"),
        "template_file": template.get("template_file"),
        "template_project_type": template.get("project_type"),
        "sheet_count": len(sheets),
        "sheet_register": sheets,
        "parameters": data,
        "calculation": calc,
        "files": files,
        "links": links,
        "normative_notes": NORMATIVE_NOTES,
        "status": "ARTIFACTS_CREATED_AND_UPLOADED",
    }
    Path(path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def _validate_pdf(path: str, min_pages: int) -> Tuple[bool, str]:
    if not os.path.exists(path) or os.path.getsize(path) < 5000:
        return False, "PDF_FILE_TOO_SMALL"
    try:
        from pypdf import PdfReader
        pages = len(PdfReader(path).pages)
        if pages < min_pages:
            return False, f"PDF_PAGE_COUNT_TOO_LOW:{pages}"
    except Exception as e:
        return False, f"PDF_VALIDATE_ERROR:{str(e)[:100]}"
    return True, ""

def _upload(path: str, task_id: str, topic_id: int) -> str:
    from core.engine_base import upload_artifact_to_drive
    link = upload_artifact_to_drive(path, task_id, topic_id)
    return str(link or "")

def create_full_project_package(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "") -> Dict[str, Any]:
    data = parse_project_request(raw_input, template_hint)
    template = _choose_template(data["section"], topic_id)
    sheets = _normalize_sheet_register(template, data)

    if len(sheets) < 8:
        return {
            "success": False,
            "error": f"SHEET_REGISTER_TOO_SHORT:{len(sheets)}",
            "engine": ENGINE,
            "section": data["section"],
            "sheet_count": len(sheets),
        }

    calc = _calc_foundation(data)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_task = _safe_name(task_id)[:20]
    out_dir = Path(tempfile.gettempdir()) / f"areal_project_full_{safe_task}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{data['section']}_project_{safe_task}"
    pdf_path = str(out_dir / f"{base_name}.pdf")
    dxf_path = str(out_dir / f"{base_name}.dxf")
    xlsx_path = str(out_dir / f"{base_name}.xlsx")
    manifest_path = str(out_dir / f"{base_name}.manifest.json")

    res = {
        "success": False,
        "engine": ENGINE,
        "section": data["section"],
        "sheet_count": len(sheets),
        "template_file": template.get("template_file"),
        "pdf_path": pdf_path,
        "dxf_path": dxf_path,
        "xlsx_path": xlsx_path,
        "manifest_path": manifest_path,
        "pdf_link": "",
        "dxf_link": "",
        "xlsx_link": "",
        "manifest_link": "",
        "error": None,
        "data": data,
        "calculation": calc,
    }

    try:
        write_project_pdf(pdf_path, data, template, sheets, calc)
        write_project_dxf(dxf_path, data, calc)
        write_project_xlsx(xlsx_path, data, sheets, calc, template)

        ok, err = _validate_pdf(pdf_path, min_pages=8)
        if not ok:
            res["error"] = err
            return res
        if not os.path.exists(dxf_path) or os.path.getsize(dxf_path) < 1500:
            res["error"] = "DXF_FILE_TOO_SMALL"
            return res
        if not os.path.exists(xlsx_path) or os.path.getsize(xlsx_path) < 3000:
            res["error"] = "XLSX_FILE_TOO_SMALL"
            return res

        pdf_link = _upload(pdf_path, task_id, topic_id)
        dxf_link = _upload(dxf_path, task_id, topic_id)
        xlsx_link = _upload(xlsx_path, task_id, topic_id)

        links = {"pdf": pdf_link, "dxf": dxf_link, "xlsx": xlsx_link}
        files = {"pdf": pdf_path, "dxf": dxf_path, "xlsx": xlsx_path}
        write_project_manifest(manifest_path, data, template, sheets, calc, files, links, task_id, topic_id)
        manifest_link = _upload(manifest_path, task_id, topic_id)

        if not pdf_link:
            res["error"] = "PDF_UPLOAD_FAILED"
            return res
        if not dxf_link:
            res["error"] = "DXF_UPLOAD_FAILED"
            return res
        if not xlsx_link:
            res["error"] = "XLSX_UPLOAD_FAILED"
            return res

        res.update({
            "success": True,
            "pdf_link": pdf_link,
            "dxf_link": dxf_link,
            "xlsx_link": xlsx_link,
            "manifest_link": manifest_link,
        })
        return res
    except Exception as e:
        res["error"] = str(e)[:500]
        return res

def is_project_design_request(text: str) -> bool:
    low = _clean(text, 2000).lower()
    triggers = [
        "создай проект",
        "сделай проект",
        "разработай проект",
        "готовый проект",
        "проект фундамент",
        "проект фундаментной плиты",
        "проект кровли",
        "проект по образцу",
        "проект по шаблону",
        "полный проект",
        "проектная документация",
        "рабочая документация",
        "выдай проект",
        "нужен проект",
    ]
    return any(x in low for x in triggers)

def format_project_result_message(res: Dict[str, Any]) -> str:
    if not res.get("success"):
        return "Проект не создан: " + _clean(res.get("error") or "ошибка генерации", 300)
    data = res.get("data") or {}
    calc = res.get("calculation") or {}
    lines = [
        "Проектная документация создана",
        f"Движок: {res.get('engine')}",
        f"Раздел: {res.get('section')}",
        f"Листов PDF: {res.get('sheet_count')}",
        f"Размер: {data.get('length_m')} x {data.get('width_m')} м",
        f"Плита: {data.get('slab_mm')} мм",
        f"Бетон: {data.get('concrete_class')}",
        f"Арматура: {data.get('rebar_class')} Ø{data.get('rebar_diam_mm')} шаг {data.get('rebar_step_mm')} мм",
        f"Бетон: {calc.get('concrete_m3')} м³",
        f"Арматура: {calc.get('rebar_t')} т",
        "",
        f"PDF: {res.get('pdf_link')}",
        f"DXF: {res.get('dxf_link')}",
        f"XLSX: {res.get('xlsx_link')}",
    ]
    if res.get("manifest_link"):
        lines.append(f"MANIFEST: {res.get('manifest_link')}")
    lines.append("")
    lines.append("Доволен результатом? Ответь: Да / Уточни / Правки")
    return "\n".join(lines)

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "") -> Dict[str, Any]:
    return create_full_project_package(raw_input, task_id, topic_id, template_hint)

# === END FULLFIX_07_CAD_PROJECT_DOCUMENTATION_CLOSURE ===


# === FULLFIX_08_PROJECT_SIGNATURE_COMPAT ===
# Compatibility layer:
# - accepts legacy worker calls with extra positional args
# - exposes create_full_project_documentation for diagnostics and future routes
# - keeps the real FULLFIX_07 CAD generator as the single backend

_FF08_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT = globals().get("create_project_pdf_dxf_artifact")

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    if _FF08_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT is None:
        return {
            "success": False,
            "engine": "FULLFIX_08_PROJECT_SIGNATURE_COMPAT",
            "error": "ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT_NOT_FOUND",
        }

    try:
        return await _FF08_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT(
            raw_input,
            task_id,
            int(topic_id or 0),
            str(template_hint or "")
        )
    except TypeError as e:
        msg = str(e)
        if "positional arguments" not in msg and "argument" not in msg:
            raise
        return await _FF08_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT(
            raw_input,
            task_id,
            int(topic_id or 0)
        )

async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    return await create_project_pdf_dxf_artifact(
        raw_input,
        task_id,
        int(topic_id or 0),
        str(template_hint or ""),
        *args,
        **kwargs
    )

# === END FULLFIX_08_PROJECT_SIGNATURE_COMPAT ===



# === FULLFIX_09_PROJECT_TEMPLATE_REGISTER_REPAIR ===
# Purpose:
# - repaired template models from data/project_templates/*_repaired.json are authoritative
# - never generate project PDF with empty/1-sheet register
# - KЖ fallback = 20 sheets, КД fallback = 21 sheets, АР fallback = 22 sheets

def _ff09_canon_sheet_register(section: str) -> list:
    section = str(section or "").upper().strip()
    if section == "КД":
        return [
            "01 Общие данные",
            "02 План балок перекрытия",
            "03 План стропильной системы",
            "04 План стропильной системы",
            "05 Узлы крепления стропильной системы",
            "06 Спецификация элементов стропильной системы",
            "07 План обрешётки",
            "08 План контробрешётки",
            "09 Узлы кровли",
            "10 Сечения кровельного пирога",
            "11 Узлы карнизного свеса",
            "12 Узлы конька",
            "13 Узлы ендовы",
            "14 Узлы примыкания",
            "15 Узлы проходок",
            "16 Ведомость пиломатериалов",
            "17 Ведомость крепежа",
            "18 Спецификация кровельных материалов",
            "19 Схема монтажа",
            "20 Общие указания",
            "21 Ведомость листов",
        ]
    if section == "АР":
        return [
            "01 Общие данные",
            "02 Ситуационный план",
            "03 План закладных деталей коммуникаций",
            "04 План фундамента",
            "05 План первого этажа",
            "06 План кровли",
            "07 Фасад 1-4",
            "08 Фасад 4-1",
            "09 Фасад А-Д",
            "10 Фасад Д-А",
            "11 Разрез 1-1",
            "12 Разрез 2-2",
            "13 Экспликация помещений",
            "14 Спецификация окон",
            "15 Спецификация дверей",
            "16 Узлы наружных стен",
            "17 Узлы кровли",
            "18 Узлы примыканий",
            "19 Ведомость отделки",
            "20 Общие указания",
            "21 Технико-экономические показатели",
            "22 Ведомость листов",
        ]
    return [
        "01 Общие данные",
        "02 План фундаментной плиты",
        "03 Разрез 1-1",
        "04 Разрез 2-2",
        "05 Схема нижнего армирования",
        "06 Схема верхнего армирования",
        "07 Схема дополнительного армирования",
        "08 Узлы армирования углов",
        "09 Узлы примыкания ленты/ребра",
        "10 Схема закладных деталей",
        "11 Схема выпусков арматуры",
        "12 Схема инженерных проходок",
        "13 План опалубки",
        "14 Спецификация арматуры",
        "15 Спецификация бетона",
        "16 Ведомость материалов основания",
        "17 Ведомость объёмов работ",
        "18 Контрольные отметки",
        "19 Общие указания",
        "20 Ведомость листов",
    ]

def _ff09_load_repaired_template(section: str) -> dict:
    import json as _json_ff09
    from pathlib import Path as _Path_ff09

    section = str(section or "КЖ").upper().strip()
    base = _Path_ff09("/root/.areal-neva-core/data/project_templates")

    candidates = [
        base / f"PROJECT_TEMPLATE_MODEL__{section}_repaired.json",
        base / f"PROJECT_TEMPLATE_MODEL__{section}_manual.json",
    ]

    for path in candidates:
        if not path.exists():
            continue
        try:
            model = _json_ff09.loads(path.read_text(encoding="utf-8"))
            reg = model.get("sheet_register") or []
            if isinstance(reg, list) and len(reg) >= 10:
                model["template_file"] = str(path)
                return model
        except Exception:
            pass

    return {
        "schema": "PROJECT_TEMPLATE_MODEL_V2_CANON_FALLBACK",
        "project_type": section,
        "template_file": "canonical_fallback",
        "sheet_register": _ff09_canon_sheet_register(section),
        "sections": [],
        "materials": [],
    }

_FF09_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT = globals().get("create_project_pdf_dxf_artifact")

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    raw = str(raw_input or "")
    low = raw.lower()

    section = "КЖ"
    if " кд" in low or "кд " in low or "деревян" in low or "стропил" in low or "кровл" in low:
        section = "КД"
    elif " ар" in low or "ар " in low or "архитект" in low or "фасад" in low:
        section = "АР"
    elif " кж" in low or "кж " in low or "фундамент" in low or "плит" in low or "армир" in low:
        section = "КЖ"

    repaired = _ff09_load_repaired_template(section)
    if template_hint:
        try:
            import json as _json_ff09
            hint_obj = _json_ff09.loads(str(template_hint))
            if isinstance(hint_obj, dict):
                hint_obj.update({"sheet_register": repaired.get("sheet_register") or [], "template_file": repaired.get("template_file")})
                template_hint = _json_ff09.dumps(hint_obj, ensure_ascii=False)
        except Exception:
            template_hint = str(repaired.get("template_file") or "")

    if not template_hint:
        template_hint = str(repaired.get("template_file") or "")

    if callable(_FF09_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT):
        res = await _FF09_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT(raw_input, task_id, topic_id, template_hint)
    else:
        res = {"success": False, "error": "ORIGINAL_PROJECT_ENGINE_NOT_FOUND"}

    if isinstance(res, dict):
        data = res.get("data") or {}
        tpl = data.get("template") or {}
        reg = tpl.get("sheet_register") or repaired.get("sheet_register") or _ff09_canon_sheet_register(section)

        if len(reg) < 10:
            reg = _ff09_canon_sheet_register(section)

        tpl["sheet_register"] = reg
        tpl["template_file"] = repaired.get("template_file") or tpl.get("template_file") or "canonical_fallback"
        data["template"] = tpl
        data["sheet_register"] = reg
        res["data"] = data
        res["sheet_count"] = len(reg)
        res["template_file"] = tpl["template_file"]

        msg = str(res.get("message") or "")
        if msg:
            msg = re.sub(r"Листов(?: PDF)?:\s*\d+", f"Листов PDF: {len(reg)}", msg)
            if "Шаблон:" not in msg:
                msg = msg.replace("Раздел:", f"Шаблон: {tpl['template_file']}\nРаздел:", 1)
            res["message"] = msg

    return res

async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

# === END FULLFIX_09_PROJECT_TEMPLATE_REGISTER_REPAIR ===


# === FULLFIX_10_TOTAL_CLOSURE_CAD_OVERRIDE ===
# Purpose:
# - user may write simple natural text: "сделай плиту 12 на 8..."
# - foundation slab must always be КЖ
# - foundation slab must never use КД/roof/wood sheet register
# - generated PDF must pass forbidden-word validation before returning links

from core.orchestra_closure_engine import (
    parse_foundation_request as _ff10_parse_foundation_request,
    foundation_sheets as _ff10_foundation_sheets,
    extract_pdf_text as _ff10_extract_pdf_text,
    validate_foundation_text as _ff10_validate_foundation_text,
    ENGINE as _FF10_ENGINE,
)

_FF10_ORIGINAL_PARSE_PROJECT_REQUEST = globals().get("parse_project_request")
_FF10_ORIGINAL_NORMALIZE_SHEET_REGISTER = globals().get("_normalize_sheet_register")
_FF10_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT = globals().get("create_project_pdf_dxf_artifact")

def parse_project_request(raw_input: str, template_hint: str = "") -> dict:
    data = _ff10_parse_foundation_request(str(raw_input or "") + " " + str(template_hint or ""))
    if data.get("project_kind") == "foundation_slab":
        data["section"] = "КЖ"
        data["project_name"] = "Проект фундаментной плиты"
        return data
    if callable(_FF10_ORIGINAL_PARSE_PROJECT_REQUEST):
        return _FF10_ORIGINAL_PARSE_PROJECT_REQUEST(raw_input, template_hint)
    return data

def _normalize_sheet_register(template: dict, data: dict) -> list:
    if str((data or {}).get("project_kind") or "").lower() == "foundation_slab":
        return _ff10_foundation_sheets()
    if callable(_FF10_ORIGINAL_NORMALIZE_SHEET_REGISTER):
        return _FF10_ORIGINAL_NORMALIZE_SHEET_REGISTER(template, data)
    return _ff10_foundation_sheets()

async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    if not callable(_FF10_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT):
        return {"success": False, "engine": _FF10_ENGINE, "error": "ORIGINAL_PROJECT_ENGINE_NOT_FOUND"}

    res = await _FF10_ORIGINAL_CREATE_PROJECT_PDF_DXF_ARTIFACT(raw_input, task_id, topic_id, template_hint, *args, **kwargs)
    if not isinstance(res, dict):
        return {"success": False, "engine": _FF10_ENGINE, "error": "INVALID_ENGINE_RESULT"}

    data = res.get("data") or parse_project_request(raw_input, template_hint)
    if str(data.get("project_kind") or "").lower() == "foundation_slab":
        res["section"] = "КЖ"
        res["sheet_count"] = len(_ff10_foundation_sheets())
        pdf_path = str(res.get("pdf_path") or "")
        pdf_text = _ff10_extract_pdf_text(pdf_path)
        ok, err = _ff10_validate_foundation_text(pdf_text)
        if not ok:
            res["success"] = False
            res["engine"] = _FF10_ENGINE
            res["error"] = err
            res["message"] = "Проект не создан: проверка PDF не пройдена"
            return res

    res["engine"] = _FF10_ENGINE
    return res

async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
    return await create_project_pdf_dxf_artifact(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

# === END FULLFIX_10_TOTAL_CLOSURE_CAD_OVERRIDE ===


# === FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT_CAD_OVERRIDE ===
try:
    from core.orchestra_closure_engine import create_compact_project_documentation as _ff12_compact_project

    async def create_project_pdf_dxf_artifact(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff12_compact_project(raw_input, task_id, topic_id, template_hint, *args, **kwargs)

    async def create_full_project_documentation(raw_input: str, task_id: str, topic_id: int = 0, template_hint: str = "", *args, **kwargs) -> dict:
        return await _ff12_compact_project(raw_input, task_id, topic_id, template_hint, *args, **kwargs)
except Exception:
    pass
# === END FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT_CAD_OVERRIDE ===

====================================================================================================
END_FILE: core/cad_project_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/capability_router.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 1aee1e85df8d7f5455453865a1ac6b6c8e443edeb29e71de1cda0a58adfcfeec
====================================================================================================
# === FULLFIX_CAPABILITY_ROUTER_STAGE_2 ===
from __future__ import annotations
from typing import Any, Dict, List

ROUTER_VERSION = "CAPABILITY_ROUTER_V1"

ENGINE_MAP = {
    "general_chat":          "ai_router",
    "orchestration_core":    "ai_router",
    "telegram_automation":   "ai_router",
    "memory_archive":        "ai_router",
    "internet_search":       "search_supplier",
    "product_search":        "search_supplier",
    "auto_parts_search":     "search_supplier",
    "construction_search":   "search_supplier",
    "technical_supervision": "defect_act",
    "estimates":             "estimate_unified",
    "defect_acts":           "defect_act",
    "documents":             "document_engine",
    "spreadsheets":          "sheets_route",
    "google_drive_storage":  "drive_storage",
    "devops_server":         "ai_router",
    "vpn_network":           "ai_router",
    "ocr_photo":             "ocr_engine",
    "cad_dwg":               "dwg_engine",
    "structural_design":     "project_engine",
    "roofing":               "estimate_unified",
    "monolith_concrete":     "estimate_unified",
    "crm_leads":             "ai_router",
    "email_ingress":         "email_ingress",
    "social_content":        "content_engine",
    "video_production":      "video_production_agent",
    "photo_cleanup":         "photo_cleanup",
    "isolated_project_ivan": "ai_router",
}

FALLBACK_ENGINE = "ai_router"


def _step(engine, action, params=None, required=True):
    return {"engine": engine, "action": action, "params": params or {}, "required": required, "status": "pending"}


def _plan(direction, profile, work_item):
    engine = profile.get("engine") or ENGINE_MAP.get(direction, FALLBACK_ENGINE)
    formats_out = profile.get("output_formats") or ["telegram_text"]
    requires_search = bool(profile.get("requires_search"))
    quality_gates = profile.get("quality_gates") or []
    input_type = (getattr(work_item, "input_type", "") or "").lower()
    raw_text = (getattr(work_item, "raw_text", "") or "")[:300]

    steps = []
    if input_type in ("photo", "image") and direction != "photo_cleanup":
        steps.append(_step("ocr_engine", "extract_text", required=False))
    if requires_search:
        steps.append(_step("search_supplier", "search", {"query": raw_text, "direction": direction}))
    steps.append(_step(engine, "execute", {"direction": direction, "formats_out": formats_out, "quality_gates": quality_gates}))
    if "xlsx" in formats_out:
        steps.append(_step("format_adapter", "to_xlsx"))
    if "docx" in formats_out or "pdf" in formats_out:
        steps.append(_step("format_adapter", "to_document"))
    if "drive_link" in formats_out:
        steps.append(_step("drive_storage", "upload", required=False))
    return steps, engine


class CapabilityRouter:
    def apply_to_work_item(self, work_item) -> Dict[str, Any]:
        direction = getattr(work_item, "direction", None) or "general_chat"
        profile = getattr(work_item, "direction_profile", {}) or {}
        if not profile:
            profile = {"engine": ENGINE_MAP.get(direction, FALLBACK_ENGINE)}

        steps, engine = _plan(direction, profile, work_item)
        work_item.execution_plan = steps
        work_item.formats_out = profile.get("output_formats") or ["telegram_text"]
        work_item.quality_gates = profile.get("quality_gates") or []
        work_item.add_audit("capability_router", ROUTER_VERSION)
        work_item.add_audit("engine", engine)
        work_item.add_audit("execution_plan_steps", len(steps))
        return {"direction": direction, "engine": engine, "execution_plan": steps,
                "formats_out": work_item.formats_out, "quality_gates": work_item.quality_gates,
                "router_version": ROUTER_VERSION}
# === END FULLFIX_CAPABILITY_ROUTER_STAGE_2 ===

====================================================================================================
END_FILE: core/capability_router.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/capability_router_dispatch.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5289c229f54cd10f2a8a2c42c36b5ceadbaf5e717d8473c4c354d3a390b9ae49
====================================================================================================
# === CAPABILITY_ROUTER_REAL_DISPATCH_V1 ===
from __future__ import annotations

from typing import Any, Dict

def build_execution_plan(input_type: str = "", user_text: str = "", file_name: str = "", mime_type: str = "", topic_id: int = 0) -> Dict[str, Any]:
    low = f"{input_type} {user_text} {file_name} {mime_type}".lower()
    if any(x in low for x in ("dwg", "dxf", "ifc", "чертеж", "чертёж", "проект", "кж", "кмд")):
        engine = "dwg_project"
    elif any(x in low for x in ("смет", "расч", "вор", "xlsx", "xls", "csv")):
        engine = "estimate"
    elif any(x in low for x in ("технадзор", "акт", "дефект", "фото", "jpg", "png", "heic", "сп", "гост")):
        engine = "technadzor"
    elif any(x in low for x in ("найди", "поиск", "цена", "купить")):
        engine = "search"
    else:
        engine = "universal"
    return {
        "router": "CAPABILITY_ROUTER_REAL_DISPATCH_V1",
        "topic_id": int(topic_id or 0),
        "engine": engine,
        "input_type": input_type,
        "file_name": file_name,
        "mime_type": mime_type,
    }

def dispatch_hint(plan: Dict[str, Any]) -> str:
    return str((plan or {}).get("engine") or "universal")
# === END_CAPABILITY_ROUTER_REAL_DISPATCH_V1 ===

====================================================================================================
END_FILE: core/capability_router_dispatch.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/chat_exports_policy.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5dba229a50fdb45fd5e3c6537274316caad7f37759487be75e2c97cad258c4d0
====================================================================================================
# === CHAT_EXPORTS_DEDUP_POLICY_V1 ===
# Канонический источник: chat_exports/ (lowercase)
# CHAT_EXPORTS/ — legacy, не удалять, но игнорировать в агрегаторе
import os, logging
from pathlib import Path
logger = logging.getLogger(__name__)

BASE = Path("/root/.areal-neva-core")
CANONICAL_DIR = BASE / "chat_exports"
LEGACY_DIR = BASE / "CHAT_EXPORTS"

def get_canonical_exports_dir() -> Path:
    return CANONICAL_DIR

def list_canonical_exports() -> list:
    if not CANONICAL_DIR.exists():
        return []
    return sorted(CANONICAL_DIR.rglob("*.json")) + sorted(CANONICAL_DIR.rglob("*.txt"))

def is_legacy_dir(path: str) -> bool:
    return "CHAT_EXPORTS" in str(path) and "chat_exports" not in str(path).lower().replace("CHAT_EXPORTS","")

def dedup_export_files(files: list) -> list:
    """Убрать дубли — если файл есть в обоих dirs, брать из canonical"""
    seen_names = set()
    result = []
    # Сначала canonical
    canonical = [f for f in files if CANONICAL_DIR.name in str(f) and not is_legacy_dir(str(f))]
    legacy = [f for f in files if is_legacy_dir(str(f))]
    for f in canonical:
        seen_names.add(Path(f).name)
        result.append(f)
    for f in legacy:
        if Path(f).name not in seen_names:
            result.append(f)
    return result
# === END CHAT_EXPORTS_DEDUP_POLICY_V1 ===

====================================================================================================
END_FILE: core/chat_exports_policy.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/constraint_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e8ffe41c2f52aef2692c65e65c8b59713ab45ba46f13cbffee21118e00d60382
====================================================================================================
# === CONSTRAINT_ENGINE_V1 ===
import re, logging
logger = logging.getLogger(__name__)

# MULTI_OFFER_CONSISTENCY — все офферы в одном формате
def normalize_offer(offer: dict) -> dict:
    return {
        "supplier":  str(offer.get("supplier") or offer.get("поставщик") or "UNKNOWN"),
        "platform":  str(offer.get("platform") or offer.get("площадка") or ""),
        "seller_type": str(offer.get("seller_type") or "UNKNOWN"),
        "city":      str(offer.get("city") or offer.get("город") or ""),
        "price":     _to_float(offer.get("price") or offer.get("цена") or 0),
        "unit":      str(offer.get("unit") or offer.get("ед") or ""),
        "stock":     str(offer.get("stock") or offer.get("наличие") or "UNKNOWN"),
        "delivery":  str(offer.get("delivery") or offer.get("доставка") or "UNKNOWN"),
        "tco":       _to_float(offer.get("tco") or 0),
        "risk":      str(offer.get("risk") or "UNVERIFIED"),
        "contact":   str(offer.get("contact") or offer.get("контакт") or ""),
        "url":       str(offer.get("url") or offer.get("ссылка") or ""),
        "verified":  bool(offer.get("verified") or False),
    }

def _to_float(v) -> float:
    try:
        return float(re.sub(r"[^\d.]", "", str(v)) or 0)
    except Exception:
        return 0.0

def validate_offer(offer: dict) -> dict:
    """Проверить оффер на минимальное качество"""
    issues = []
    if not offer.get("price") or offer["price"] <= 0:
        issues.append("NO_PRICE")
    if not offer.get("contact") and not offer.get("url"):
        issues.append("NO_CONTACT")
    if offer.get("price") and offer["price"] < 10:
        issues.append("PRICE_TOO_LOW")
    return {"ok": len(issues) == 0, "issues": issues}

def rank_offers(offers: list) -> list:
    """ResultRanker — сортировка по TCO или цене"""
    def score(o):
        tco = o.get("tco") or o.get("price") or 999999
        risk_penalty = {"CONFIRMED": 0, "PARTIAL": 5, "UNVERIFIED": 15, "RISK": 30}.get(o.get("risk","UNVERIFIED"), 15)
        return tco + risk_penalty * 100
    return sorted(offers, key=score)

# CONSTRAINT_ENGINE — ограничения на поиск
_CONSTRAINTS = {
    "price_min": 0,
    "price_max": 999_999_999,
    "region": [],
    "exclude_keywords": ["1 руб", "договорная", "под заказ в пути"],
    "require_contact": False,
    "require_stock": False,
}

def apply_constraints(offers: list, constraints: dict = None) -> list:
    c = {**_CONSTRAINTS, **(constraints or {})}
    result = []
    for o in offers:
        price = _to_float(o.get("price") or 0)
        if price and (price < c["price_min"] or price > c["price_max"]):
            continue
        text = str(o).lower()
        if any(ex.lower() in text for ex in c["exclude_keywords"]):
            continue
        if c["require_contact"] and not o.get("contact"):
            continue
        result.append(o)
    return result
# === END CONSTRAINT_ENGINE_V1 ===

====================================================================================================
END_FILE: core/constraint_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/context_loader.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: b2e7c83efbb7cd1e9893212919ed790834ccaef025265a92c0b40faf6898e8e5
====================================================================================================
# === FULLFIX_CONTEXT_LOADER_STAGE_3 ===
from __future__ import annotations
import asyncio
from typing import Any, Dict, Optional

CONTEXT_LOADER_VERSION = "CONTEXT_LOADER_V1"


def _safe_str(v, default=""):
    if v is None: return default
    return str(v)


class ContextLoader:
    """
    Stage 3 shadow mode: загружает контекст задачи из доступных источников.
    Пишет context_refs в WorkItem. Не блокирует выполнение при ошибках.
    """

    def load(self, work_item, db_conn=None) -> Dict[str, Any]:
        chat_id = _safe_str(getattr(work_item, "chat_id", ""))
        topic_id = int(getattr(work_item, "topic_id", 0) or 0)
        raw_text = _safe_str(getattr(work_item, "raw_text", ""))[:500]
        direction = _safe_str(getattr(work_item, "direction", "general_chat"))

        refs = {
            "chat_id": chat_id,
            "topic_id": topic_id,
            "direction": direction,
            "short_memory": None,
            "long_memory": None,
            "recent_tasks": [],
            "topic_context": None,
            "loader_version": CONTEXT_LOADER_VERSION,
            "shadow_mode": True,
        }

        # short_memory — из memory_api если доступна
        try:
            refs["short_memory"] = self._load_short_memory(chat_id, topic_id)
        except Exception as e:
            refs["short_memory_error"] = str(e)

        # topic_context — последние задачи по теме из DB
        if db_conn is not None:
            try:
                refs["topic_context"] = self._load_topic_context(db_conn, chat_id, topic_id)
            except Exception as e:
                refs["topic_context_error"] = str(e)

        work_item.context_refs = refs
        work_item.add_audit("context_loader", CONTEXT_LOADER_VERSION)
        work_item.add_audit("context_topic_id", topic_id)
        return refs

    def _load_short_memory(self, chat_id, topic_id):
        import urllib.request, json
        url = f"http://127.0.0.1:8765/memory?chat_id={chat_id}&topic_id={topic_id}&limit=5"
        try:
            req = urllib.request.urlopen(url, timeout=2)
            data = json.loads(req.read().decode())
            return data if isinstance(data, (list, dict)) else None
        except Exception:
            return None

    def _load_topic_context(self, db_conn, chat_id, topic_id):
        try:
            import sqlite3
            if hasattr(db_conn, "execute"):
                rows = db_conn.execute(
                    "SELECT id, state, created_at FROM tasks WHERE chat_id=? AND topic_id=? ORDER BY created_at DESC LIMIT 5",
                    (str(chat_id), int(topic_id))
                ).fetchall()
            else:
                rows = []
            return [{"id": r[0], "state": r[1], "created_at": r[2]} for r in rows]
        except Exception:
            return []


def load_context(work_item, db_conn=None):
    return ContextLoader().load(work_item, db_conn)
# === END FULLFIX_CONTEXT_LOADER_STAGE_3 ===

====================================================================================================
END_FILE: core/context_loader.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/data_classification.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 94b1f8b88f75ccb2d032ff2f77790acb7884c5f9e6ec7e7ad0f9277824d6d4bf
====================================================================================================
# === DATA_CLASSIFICATION_V1 ===
# Канон §28.3 — File Routing Canon
import re, logging
logger = logging.getLogger(__name__)

_DOMAIN_MAP = {
    "STROYKA":     ["кровля", "фасад", "фундамент", "кирпич", "бетон", "арматура", "утеплитель",
                    "металлочерепица", "профнастил", "сайдинг", "монтаж", "строительство", "ангар"],
    "ESTIMATES":   ["смета", "ведомость", "объём работ", "вор", "ФЕР", "ТЕР", "расценка", "калькул"],
    "TEHNADZOR":   ["технадзор", "дефект", "акт осмотра", "нарушение", "предписание", "сп ", "гост", "снип"],
    "AUTO":        ["toyota", "hiace", "запчасть", "brembo", "vin", "авто", "машина"],
    "SEARCH":      ["найди", "поищи", "цена", "стоимость", "купить", "поставщик", "avito", "ozon"],
    "DOCS_PDF_DWG": ["dwg", "dxf", "чертёж", "pdf", "docx", "проект"],
    "NEURON_SOFT_VPN": ["vpn", "wireguard", "xray", "vless", "конфиг", "ключ"],
}

def classify_domain(text: str, file_name: str = "") -> str:
    combined = (text + " " + file_name).lower()
    scores = {}
    for domain, keywords in _DOMAIN_MAP.items():
        scores[domain] = sum(1 for kw in keywords if kw.lower() in combined)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "UNSORTED"

def classify_file_type(file_name: str) -> str:
    ext = file_name.lower().rsplit(".", 1)[-1] if "." in file_name else ""
    mapping = {
        "pdf": "PDF", "docx": "DOCX", "doc": "DOCX",
        "xlsx": "XLSX", "xls": "XLSX", "csv": "CSV",
        "dwg": "DWG", "dxf": "DXF",
        "jpg": "IMAGE", "jpeg": "IMAGE", "png": "IMAGE",
        "heic": "IMAGE", "webp": "IMAGE",
        "zip": "ARCHIVE", "rar": "ARCHIVE",
        "mp4": "VIDEO", "mov": "VIDEO",
        "ogg": "AUDIO", "mp3": "AUDIO",
    }
    return mapping.get(ext, "UNKNOWN")

def classify_intent(text: str) -> str:
    low = text.lower()
    if any(w in low for w in ["смета", "посчитай", "расценка", "объём"]):
        return "estimate"
    if any(w in low for w in ["шаблон", "образец", "возьми как"]):
        return "template"
    if any(w in low for w in ["дефект", "акт", "нарушение", "технадзор"]):
        return "technadzor"
    if any(w in low for w in ["проект", "кж", "ар", "кд", "км"]):
        return "project"
    if any(w in low for w in ["найди", "поищи", "цена", "купить"]):
        return "search"
    if any(w in low for w in ["dwg", "dxf", "чертёж"]):
        return "dwg"
    return "text"
# === END DATA_CLASSIFICATION_V1 ===

====================================================================================================
END_FILE: core/data_classification.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/defect_act_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ef8ae207b552886b90aed1104beb8171ccb8159e19e4d1b05796d867afbb1817
====================================================================================================
# === FULLFIX_15_DEFECT_ACT ===
import os, logging
from datetime import date
logger = logging.getLogger(__name__)
ENGINE = "FULLFIX_15_DEFECT_ACT"
RUNTIME_DIR = "/root/.areal-neva-core/runtime"
os.makedirs(RUNTIME_DIR, exist_ok=True)
ACT_PHRASES = ["акт", "дефект", "осмотр", "сделай акт", "по фото", "технадзор", "нарушение"]

def is_defect_act_intent(text, mime_type=""):
    t = (text or "").lower()
    return "image" in (mime_type or "") and any(p in t for p in ACT_PHRASES)

def generate_act_docx(task_id, caption, file_name, object_name="UNKNOWN"):
    from docx import Document
    path = os.path.join(RUNTIME_DIR, "act_" + task_id[:8] + ".docx")
    doc = Document()
    doc.add_heading("АКТ ОСМОТРА / ДЕФЕКТНАЯ ВЕДОМОСТЬ", 0)
    today = date.today().strftime("%d.%m.%Y")
    doc.add_paragraph("Дата: " + today)
    doc.add_paragraph("Объект: " + (object_name or "UNKNOWN"))
    doc.add_paragraph("Основание: фото — " + (file_name or ""))
    table = doc.add_table(rows=1, cols=6)
    table.style = "Table Grid"
    for i, h in enumerate(["№", "Фото/файл", "Описание дефекта", "Локация", "Рекомендация", "Статус"]):
        table.rows[0].cells[i].text = h
    row = table.add_row().cells
    row[0].text = "1"; row[1].text = file_name or ""; row[2].text = caption or "требует уточнения"
    row[3].text = "-"; row[4].text = "Устранить"; row[5].text = "Открыт"
    doc.add_paragraph("Заключение: зафиксированы дефекты, требующие устранения.")
    doc.add_paragraph("Составил: ________________________  Дата: " + today)
    doc.save(path)
    return path

def generate_act_pdf(task_id, caption, file_name, object_name="UNKNOWN"):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
    from reportlab.lib import colors
    from core.pdf_cyrillic import register_cyrillic_fonts, make_styles, make_paragraph, clean_pdf_text, FONT_REGULAR, FONT_BOLD
    path = os.path.join(RUNTIME_DIR, "act_" + task_id[:8] + ".pdf")
    register_cyrillic_fonts()
    styles = make_styles()
    today = date.today().strftime("%d.%m.%Y")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20, bottomMargin=20, leftMargin=20, rightMargin=20)
    story = [
        make_paragraph("АКТ ОСМОТРА / ДЕФЕКТНАЯ ВЕДОМОСТЬ", "header", styles), Spacer(1,8),
        make_paragraph("Дата: " + today, "normal", styles),
        make_paragraph("Объект: " + (object_name or "UNKNOWN"), "normal", styles),
        make_paragraph("Основание: " + (file_name or ""), "normal", styles),
        Spacer(1,10),
    ]
    data = [
        [make_paragraph(h, "bold", styles) for h in ["№", "Файл", "Описание", "Локация", "Рекомендация", "Статус"]],
        [make_paragraph(x, "normal", styles) for x in ["1", clean_pdf_text(file_name or ""), clean_pdf_text(caption or "требует уточнения"), "-", "Устранить", "Открыт"]],
    ]
    tbl = Table(data, colWidths=[22, 70, 150, 55, 80, 50])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#444444")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),FONT_BOLD),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("GRID",(0,0),(-1,-1),0.4,colors.black),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(tbl); story.append(Spacer(1,12))
    story.append(make_paragraph("Заключение: зафиксированы дефекты, требующие устранения.", "normal", styles))
    story.append(make_paragraph("Составил: ________________________  Дата: " + today, "normal", styles))
    doc.build(story)
    return path

def process_defect_act_sync(conn, task_id, chat_id, topic_id, raw_input, file_name="", local_path=""):
    from core.artifact_upload_guard import upload_many_or_fail
    from core.reply_sender import send_reply_ex
    # === FULLFIX_20_GEMINI_DEFECT_SYNC ===
    _ff20_vision_text = ""
    try:
        if local_path and any(str(local_path).lower().endswith(ext) for ext in (".jpg",".jpeg",".png",".webp",".heic")):
            import asyncio as _ff20_aio
            from core.gemini_vision import analyze_image_file as _ff20_gif
            try:
                _ff20_aio.get_running_loop()
            except RuntimeError:
                _ff20_vision_text = _ff20_aio.run(
                    _ff20_gif(local_path, prompt="\u041e\u043f\u0438\u0448\u0438 \u0434\u0435\u0444\u0435\u043a\u0442 \u0434\u043b\u044f \u0430\u043a\u0442\u0430", timeout=60)
                ) or ""
            logger.info("FF20_GEMINI_DEFECT_SYNC len=%s", len(_ff20_vision_text))
    except Exception as _ff20_ve:
        logger.warning("FF20_GEMINI_DEFECT_SYNC_ERR=%s", _ff20_ve)
    if _ff20_vision_text:
        raw_input = str(raw_input or "") + "\n\n\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0434\u0435\u0444\u0435\u043a\u0442\u0430: " + str(_ff20_vision_text)
    # === END FULLFIX_20_GEMINI_DEFECT_SYNC ===
    # === NORMATIVE_DB_V1_WIRED ===
    try:
        import asyncio as _norm_aio
        from core.normative_db import search_norms as _search_norms
        _norm_desc = str(raw_input or "") + " " + str(_ff20_vision_text or "")
        try:
            _norm_loop = _norm_aio.get_running_loop()
            _norm_results = []
        except RuntimeError:
            _norm_results = _norm_aio.run(_search_norms(_norm_desc))
        if _norm_results:
            _norm_lines = ["\n\nНормативные требования:"]
            for _n in _norm_results:
                _norm_lines.append(f"  {_n['norm_id']}: {_n['requirement'][:200]}")
            raw_input = str(raw_input or "") + "\n".join(_norm_lines)
    except Exception as _ne:
        logger.warning("NORMATIVE_DB_V1_WIRED err=%s", _ne)
    # === END NORMATIVE_DB_V1_WIRED ===


    try:
        caption = raw_input or file_name
        docx_path = generate_act_docx(task_id, caption, file_name)
        pdf_path = generate_act_pdf(task_id, caption, file_name)
        files = [{"path": pdf_path, "kind": "act_pdf"}, {"path": docx_path, "kind": "act_docx"}]
        up = upload_many_or_fail(files, task_id, topic_id)
        pdf_r = up["results"].get(pdf_path, {}); docx_r = up["results"].get(docx_path, {})
        lines = ["Акт осмотра готов."]
        if pdf_r.get("success") and pdf_r.get("link"): lines.append("PDF: " + pdf_r["link"])
        if docx_r.get("success") and docx_r.get("link"): lines.append("DOCX: " + docx_r["link"])
        if len(lines) == 1: lines.append("Drive недоступен. Файл: " + (file_name or ""))
        result_text = "\n".join(lines)
        conn.execute("UPDATE tasks SET state='AWAITING_CONFIRMATION',result=?,updated_at=datetime('now') WHERE id=?", (result_text, task_id))
        conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (task_id, "state:AWAITING_CONFIRMATION"))
        conn.commit()
        try:
            _br = send_reply_ex(chat_id=str(chat_id), text=result_text, reply_to_message_id=None)
            _bmid = None
            if isinstance(_br, dict): _bmid = _br.get("bot_message_id") or _br.get("message_id")
            elif _br and hasattr(_br, "message_id"): _bmid = _br.message_id
            if _bmid:
                conn.execute("UPDATE tasks SET bot_message_id=? WHERE id=?", (str(_bmid), task_id))
                conn.commit()
        except Exception as _se:
            logger.error("ACT_SEND_ERR task=%s err=%s", task_id, _se)
        return True
    except Exception as e:
        logger.error("DEFECT_ACT_ERROR task=%s err=%s", task_id, e)
        return False

async def process_defect_act(conn, task_id, chat_id, topic_id, raw_input, file_name="", local_path=""):
    import asyncio
    return await asyncio.get_event_loop().run_in_executor(
        None, process_defect_act_sync, conn, task_id, chat_id, topic_id, raw_input, file_name, local_path
    )
# === END FULLFIX_15_DEFECT_ACT ===

====================================================================================================
END_FILE: core/defect_act_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/direction_registry.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 9a97f853b4f786ce481776317e043e44c142dbf4ada231f8e027bc19d3c64e23
====================================================================================================
# === FULLFIX_DIRECTION_KERNEL_STAGE_1_DIRECTION_REGISTRY ===
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

BASE = Path("/root/.areal-neva-core")
CONFIG_PATH = BASE / "config" / "directions.yaml"
SEARCH_TRIGGER_TOKENS = ["найд","поиск","куп","цена","avito","ozon","wildberries","drom","auto.ru","exist","emex","zzap"]

def _s(v): return "" if v is None else str(v)
def _low(v): return _s(v).lower()


class DirectionRegistry:
    def __init__(self, path=None):
        self.path = Path(path) if path else CONFIG_PATH
        self.data = self._load()
        self.directions = self.data.get("directions", {})

    def _load(self):
        raw = self.path.read_text(encoding="utf-8")
        try: return json.loads(raw)
        except Exception:
            try:
                import yaml
                return yaml.safe_load(raw) or {}
            except Exception as e:
                raise RuntimeError(f"DIRECTION_REGISTRY_LOAD_FAIL path={self.path} err={e}")

    def _score_direction(self, direction_id, profile, work_item):
        raw = _low(getattr(work_item, "raw_text", ""))
        topic_id = int(getattr(work_item, "topic_id", 0) or 0)
        input_type = _low(getattr(work_item, "input_type", ""))
        formats_in = [str(x).lower() for x in getattr(work_item, "formats_in", []) or []]

        score = 0
        reasons = []

        strong = profile.get("strong_aliases") or []
        strong_hits = [a for a in strong if _low(a) and _low(a) in raw]
        if strong_hits:
            score += min(250, 200 + 25 * (len(strong_hits) - 1))
            reasons.append("strong:" + ",".join(strong_hits[:5]))

        topic_ids = profile.get("topic_ids") or []
        topic_match = topic_id in topic_ids
        if topic_match:
            score += 70 + max(0, 10 - len(topic_ids))
            reasons.append(f"topic_id:{topic_id}")

        aliases = profile.get("aliases") or []
        alias_hits = [a for a in aliases if _low(a) and _low(a) in raw]
        if alias_hits:
            score += min(120, 30 * len(alias_hits))
            reasons.append("aliases:" + ",".join(alias_hits[:5]))

        any_signal = bool(strong_hits or topic_match or alias_hits)

        if any_signal:
            input_types = [str(x).lower() for x in profile.get("input_types") or []]
            if input_type and input_type in input_types:
                score += 15
                reasons.append("input_type:" + input_type)
            profile_formats = [str(x).lower() for x in profile.get("input_formats") or []]
            fmt_hits = sorted(set(formats_in).intersection(set(profile_formats)))
            if fmt_hits:
                score += min(40, 10 * len(fmt_hits))
                reasons.append("formats:" + ",".join(fmt_hits))

        if any_signal and bool(profile.get("requires_search")):
            if any(t in raw for t in SEARCH_TRIGGER_TOKENS):
                score += 25
                reasons.append("search_signal")

        if not profile.get("enabled", False):
            score = max(0, score - 80)
            reasons.append("passive_penalty")

        return score, {"direction_id": direction_id, "score": score, "reasons": reasons,
                       "enabled": bool(profile.get("enabled", False)), "topic_ids_count": len(topic_ids)}

    def detect(self, work_item):
        results = []
        for direction_id, profile in self.directions.items():
            score, item = self._score_direction(direction_id, profile or {}, work_item)
            item["profile"] = dict(profile or {})
            results.append(item)

        results.sort(key=lambda r: (-r["score"], r["topic_ids_count"]))

        if not results or results[0]["score"] <= 0:
            best_profile = dict(self.directions.get("general_chat", {}))
            best_profile["id"] = "general_chat"
            best_profile["score"] = 0
            best_profile["audit"] = []
            return best_profile

        winner = results[0]
        out = dict(winner["profile"])
        out["id"] = winner["direction_id"]
        out["score"] = winner["score"]
        out["audit"] = [{k: v for k, v in r.items() if k != "profile"} for r in results[:10]]
        return out


def detect_direction(work_item):
    return DirectionRegistry().detect(work_item)
# === END FULLFIX_DIRECTION_KERNEL_STAGE_1_DIRECTION_REGISTRY ===

====================================================================================================
END_FILE: core/direction_registry.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/document_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 3ccafce81ca7ed0c744d41e2ca489c2ee4208ecbb1d17b278c03fee1a072f588
====================================================================================================
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def parse_document(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"text": "", "tables": [], "metadata": {}, "error": f"File not found: {path}"}
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            return _parse_pdf(path)
        elif ext == ".docx":
            return _parse_docx(path)
        elif ext in (".xlsx", ".xls"):
            return _parse_excel(path)
        elif ext == ".csv":
            return _parse_csv(path)
        else:
            return {"text": "", "tables": [], "metadata": {}, "error": f"Unsupported: {ext}"}
    except Exception as e:
        logger.error(f"parse_document error: {e}")
        return {"text": "", "tables": [], "metadata": {}, "error": str(e)}

def extract_text_from_document(path: str) -> str:
    return parse_document(path).get("text", "")

def extract_tables_from_document(path: str) -> list:
    return parse_document(path).get("tables", [])

def _parse_pdf(path: str) -> Dict[str, Any]:
    import pdfplumber
    text_parts = []
    tables = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: text_parts.append(t)
            for tbl in page.extract_tables():
                if tbl: tables.append(tbl)
    return {"text": "\n".join(text_parts), "tables": tables, "metadata": {"pages": len(pdf.pages)}, "error": ""}

def _parse_docx(path: str) -> Dict[str, Any]:
    from docx import Document
    doc = Document(path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text)
    tables = [[[cell.text for cell in row.cells] for row in t.rows] for t in doc.tables]
    return {"text": text, "tables": tables, "metadata": {"source": path}, "error": ""}

def _parse_excel(path: str) -> Dict[str, Any]:
    import pandas as pd
    sheets = pd.read_excel(path, sheet_name=None)
    text, tables = [], []
    for name, df in sheets.items():
        text.append(f"=== {name} ===\n{df.to_string(max_rows=50)}")
        tables.append({"sheet": name, "data": df.fillna("").to_dict(orient="records")})
    return {"text": "\n".join(text), "tables": tables, "metadata": {"sheets": list(sheets.keys())}, "error": ""}

def _parse_csv(path: str) -> Dict[str, Any]:
    import pandas as pd
    df = pd.read_csv(path)
    text = df.to_string(max_rows=50)
    tables = [{"data": df.fillna("").to_dict(orient="records")}]
    return {"text": text, "tables": tables, "metadata": {"source": path}, "error": ""}

====================================================================================================
END_FILE: core/document_engine.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/drive_content_indexer.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 86a8da0033f275d1ba30d0be51cfc639a9dbc68b75b7e2a5ac2dbec3d0f0cd59
====================================================================================================
# === DRIVE_FILE_CONTENT_MEMORY_INDEX_V1 ===
from __future__ import annotations

import csv
import io
import json
import os
import re
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
MEM_DB = f"{BASE}/data/memory.db"
load_dotenv(f"{BASE}/.env", override=True)

MAX_TEXT = 50000
MAX_ROWS = 300


def _s(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v).strip()


def _clean(text: str, limit: int = MAX_TEXT) -> str:
    text = (text or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]


def _kind(file_name: str, mime_type: str = "") -> str:
    ext = os.path.splitext((file_name or "").lower())[1]
    mime = (mime_type or "").lower()
    if ext in (".xlsx", ".xlsm", ".csv") or "spreadsheet" in mime or mime == "text/csv":
        return "table"
    if ext in (".pdf", ".docx", ".doc", ".txt") or mime in ("application/pdf", "text/plain"):
        return "document"
    return "skip"


def _drive_service():
    from core.topic_drive_oauth import _oauth_service
    return _oauth_service()


def download_drive_file(file_id: str, file_name: str) -> Optional[str]:
    if not file_id:
        return None
    service = _drive_service()
    suffix = os.path.splitext(file_name or "")[1] or ".bin"
    fd, out = tempfile.mkstemp(prefix="drive_content_", suffix=suffix, dir="/tmp")
    os.close(fd)

    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    from googleapiclient.http import MediaIoBaseDownload
    with io.FileIO(out, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return out


def extract_pdf(path: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        parts = []
        for page in reader.pages[:80]:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                pass
        return _clean("\n".join(parts), MAX_TEXT)
    except Exception as e:
        return f"PDF_PARSE_ERROR: {e}"


def extract_docx(path: str) -> str:
    try:
        from docx import Document
        doc = Document(path)
        return _clean("\n".join(p.text for p in doc.paragraphs if p.text), MAX_TEXT)
    except Exception as e:
        return f"DOCX_PARSE_ERROR: {e}"


def extract_txt(path: str) -> str:
    try:
        return _clean(Path(path).read_text(encoding="utf-8", errors="ignore"), MAX_TEXT)
    except Exception as e:
        return f"TXT_PARSE_ERROR: {e}"


def extract_table(path: str, file_name: str) -> str:
    rows: List[str] = []
    ext = os.path.splitext((file_name or "").lower())[1]

    try:
        if ext == ".csv":
            with open(path, "r", encoding="utf-8", errors="ignore", newline="") as f:
                reader = csv.reader(f)
                for idx, row in enumerate(reader):
                    rows.append(" | ".join(_s(x) for x in row))
                    if idx >= MAX_ROWS:
                        break
        else:
            from openpyxl import load_workbook
            wb = load_workbook(path, data_only=True, read_only=True)
            for ws in wb.worksheets[:5]:
                rows.append(f"=== SHEET: {ws.title} ===")
                for idx, row in enumerate(ws.iter_rows(values_only=True)):
                    vals = [_s(x) for x in row if _s(x)]
                    if vals:
                        rows.append(" | ".join(vals))
                    if idx >= MAX_ROWS:
                        break
    except Exception as e:
        rows.append(f"TABLE_PARSE_ERROR: {e}")

    return _clean("\n".join(rows), MAX_TEXT)


def extract_content(local_path: str, file_name: str, mime_type: str = "") -> Dict[str, Any]:
    kind = _kind(file_name, mime_type)
    ext = os.path.splitext((file_name or "").lower())[1]

    if kind == "table":
        text = extract_table(local_path, file_name)
    elif kind == "document":
        if ext == ".pdf":
            text = extract_pdf(local_path)
        elif ext == ".docx":
            text = extract_docx(local_path)
        else:
            text = extract_txt(local_path)
    else:
        text = ""

    return {
        "ok": bool(text and not text.endswith("_PARSE_ERROR")),
        "kind": kind,
        "file_name": file_name,
        "mime_type": mime_type,
        "content": _clean(text, MAX_TEXT),
        "chars": len(text or ""),
    }


def save_file_content_memory(chat_id: str, topic_id: int, task_id: str, file_id: str, file_name: str, mime_type: str, content: str) -> Dict[str, Any]:
    if not content.strip():
        return {"ok": False, "reason": "EMPTY_CONTENT"}

    key = f"topic_{int(topic_id or 0)}_file_content_{task_id}"
    value = json.dumps({
        "task_id": task_id,
        "chat_id": str(chat_id),
        "topic_id": int(topic_id or 0),
        "file_id": file_id,
        "file_name": file_name,
        "mime_type": mime_type,
        "content": _clean(content, MAX_TEXT),
    }, ensure_ascii=False)

    with sqlite3.connect(MEM_DB) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        existing = conn.execute("SELECT 1 FROM memory WHERE chat_id=? AND key=? LIMIT 1", (str(chat_id), key)).fetchone()
        if existing:
            return {"ok": True, "key": key, "dedup": True}
        import hashlib
        mid = hashlib.sha1(f"{chat_id}:{key}".encode()).hexdigest()
        conn.execute(
            "INSERT OR IGNORE INTO memory (id, chat_id, key, value, timestamp) VALUES (?,?,?,?,datetime('now'))",
            (mid, str(chat_id), key, value),
        )
        conn.commit()

    return {"ok": True, "key": key, "dedup": False}


def index_drive_file_content(chat_id: str, topic_id: int, task_id: str, file_id: str, file_name: str, mime_type: str = "") -> Dict[str, Any]:
    local_path = None
    try:
        if _kind(file_name, mime_type) == "skip":
            return {"ok": False, "reason": "UNSUPPORTED_TYPE", "file_name": file_name}

        local_path = download_drive_file(file_id, file_name)
        if not local_path or not os.path.exists(local_path):
            return {"ok": False, "reason": "DOWNLOAD_FAILED", "file_name": file_name}

        extracted = extract_content(local_path, file_name, mime_type)
        if not extracted.get("content"):
            return {"ok": False, "reason": "EXTRACT_EMPTY", "file_name": file_name}

        saved = save_file_content_memory(
            chat_id=str(chat_id),
            topic_id=int(topic_id or 0),
            task_id=str(task_id),
            file_id=str(file_id),
            file_name=str(file_name),
            mime_type=str(mime_type or ""),
            content=str(extracted.get("content") or ""),
        )
        return {
            "ok": bool(saved.get("ok")),
            "reason": "INDEXED" if saved.get("ok") else saved.get("reason"),
            "key": saved.get("key"),
            "dedup": saved.get("dedup", False),
            "kind": extracted.get("kind"),
            "chars": extracted.get("chars"),
            "file_name": file_name,
        }
    except Exception as e:
        return {"ok": False, "reason": f"ERROR:{e}", "file_name": file_name}
    finally:
        if local_path:
            try:
                os.remove(local_path)
            except Exception:
                pass
# === END DRIVE_FILE_CONTENT_MEMORY_INDEX_V1 ===

====================================================================================================
END_FILE: core/drive_content_indexer.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/drive_folder_resolver.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 74da8dc00bdbf6caea745c54e55bb20c0fb180092f6feb58a2135924fbfcc21f
====================================================================================================
# === DRIVE_CANON_FOLDER_RESOLVER_V1 ===
from __future__ import annotations

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger("drive_folder_resolver")

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=True)

DEFAULT_CHAT_ID = "-1003725299009"


def get_or_create_topic_folder(topic_id: int, chat_id: str = "") -> str:
    """
    Canonical Drive layout:
    AI_ORCHESTRA / chat_<chat_id> / topic_<topic_id>

    This resolver MUST NOT use Service Account and MUST NOT create flat folders:
    chat_-1003725299009_topic_2
    """
    from core.topic_drive_oauth import _oauth_service, _root_folder_id, _ensure_folder

    service = _oauth_service()
    root_id = _root_folder_id()
    chat = str(chat_id or os.getenv("TELEGRAM_CHAT_ID") or DEFAULT_CHAT_ID)
    chat_folder = _ensure_folder(service, root_id, f"chat_{chat}")
    topic_folder = _ensure_folder(service, chat_folder, f"topic_{int(topic_id or 0)}")
    logger.info(
        "DRIVE_CANON_FOLDER_RESOLVER_V1_OK chat=%s topic=%s folder=%s",
        chat,
        int(topic_id or 0),
        topic_folder,
    )
    return topic_folder


# === END_DRIVE_CANON_FOLDER_RESOLVER_V1 ===

====================================================================================================
END_FILE: core/drive_folder_resolver.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/duplicate_guard.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 674c881d7bc3af021c821051940aebf69d78a44129626e36b5d68be8f7690403
====================================================================================================
import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

def get_file_id(raw_input: str) -> Optional[str]:
    try:
        return json.loads(raw_input or "{}").get("file_id")
    except Exception:
        return None

def find_duplicate(conn, chat_id: str, topic_id: int, file_id: str) -> Optional[Dict]:
    if not file_id:
        return None
    row = conn.execute(
        """SELECT id, state, substr(result,1,240) result, updated_at
           FROM tasks
           WHERE chat_id=?
             AND COALESCE(topic_id,0)=?
             AND input_type='drive_file'
             AND COALESCE(raw_input,'') LIKE ?
             AND state IN ('DONE','AWAITING_CONFIRMATION')
           ORDER BY updated_at DESC
           LIMIT 1""",
        (str(chat_id), int(topic_id or 0), f'%"file_id": "{file_id}"%'),
    ).fetchone()
    return dict(row) if row else None

def duplicate_message(prev: Dict, file_name: str) -> str:
    prev_result = (prev.get("result") or "").strip()[:160]
    if prev_result:
        return (
            f"Этот файл уже был: {file_name}\n"
            f"Прошлый результат: {prev_result}\n\n"
            f"Что сделать?\n"
            f"1. Повторить обработку\n"
            f"2. Сделать другое\n"
            f"3. Отменить"
        )
    return (
        f"Этот файл уже был: {file_name}\n\n"
        f"Что сделать?\n"
        f"1. Повторить обработку\n"
        f"2. Сделать другое\n"
        f"3. Отменить"
    )

====================================================================================================
END_FILE: core/duplicate_guard.py
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: core/dwg_engine.py
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 52d4a88254ff45a37f7535763c22e5ca09d2bcd1490a60c7e9d770b0833b1859
====================================================================================================
# === DWG_DXF_PROJECT_CLOSE_V1 ===
from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
    "кж": ["СП 63.13330.2018", "СП 20.13330.2016/2017", "ГОСТ 34028-2016", "ГОСТ 21.501-2018"],
    "км": ["СП 16.13330.2017", "СП 20.13330.2016/2017", "ГОСТ 27772-2015", "ГОСТ 21.502-2016"],
    "кмд": ["СП 16.13330.2017", "ГОСТ 23118-2019", "ГОСТ 21.502-2016"],
    "кр": ["СП 20.13330.2016/2017", "ГОСТ 21.501-2018"],
    "ар": ["ГОСТ 21.501-2018", "ГОСТ 21.101-2020", "СП 55.13330.2016"],
    "ов": ["СП 60.13330.2020", "ГОСТ 21.602-2016"],
    "вк": ["СП 30.13330.2020", "ГОСТ 21.601-2011"],
    "эом": ["ПУЭ-7", "СП 256.1325800.2016", "ГОСТ 21.608-2014"],
    "гп": ["СП 42.13330.2016", "ГОСТ 21.508-2020"],
}

ENTITY_PROJECT_HINTS = {
    "LINE": "линейная геометрия",
    "LWPOLYLINE": "полилинии/контуры",
    "POLYLINE": "полилинии/контуры",
    "CIRCLE": "окружности/отверстия",
    "ARC": "дуги",
    "TEXT": "текстовые подписи",
    "MTEXT": "многострочные подписи",
    "DIMENSION": "размеры",
    "INSERT": "блоки/узлы",
    "HATCH": "штриховки",
}

def _clean(v: Any, limit: int = 2000) -> str:
    if v is None:
        return ""
    s = str(v).replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()[:limit]

def _safe_name(v: Any, fallback: str = "drawing") -> str:
    s = re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", _clean(v, 120)).strip("._")
    return s or fallback

def _detect_section(file_name: str = "", user_text: str = "", drawing_text: str = "") -> str:
    hay_sources = [file_name or "", user_text or "", drawing_text[:2000] if drawing_text else ""]
    priority = ("кж", "кмд", "км", "кр", "ар", "ов", "вк", "эом", "гп", "пз")
    for src in hay_sources:
        low = src.lower()
        up = src.upper()
        for key in priority:
            if re.search(rf"(^|[^А-ЯA-Z0-9]){re.escape(key.upper())}([^А-ЯA-Z0-9]|$)", up):
                return key
            if key in low:
                return key
    return "кр"

def _read_bytes_head(path: str, n: int = 64) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read(n)
    except Exception:
        return b""

def _try_read_text(path: str, limit: int = 4_000_000) -> str:
    data = b""
    try:
        with open(path, "rb") as f:
            data = f.read(limit)
    except Exception:
        return ""
    for enc in ("utf-8", "cp1251", "latin-1"):
        try:
            return data.decode(enc, errors="ignore")
        except Exception:
            pass
    return data.decode("latin-1", errors="ignore")

def _file_signature(path: str) -> str:
    head = _read_bytes_head(path, 32)
    if head.startswith(b"AC10"):
        return head[:12].decode("latin-1", errors="ignore")
    txt = head.decode("latin-1", errors="ignore")
    if "SECTION" in _try_read_text(path, 4096).upper():
        return "ASCII_DXF"
    return head[:16].hex()

def _try_convert_dwg_to_dxf(path: str) -> Optional[str]:
    src = Path(path)
    if src.suffix.lower() != ".dwg":
        return None

    tmp = Path(tempfile.mkdtemp(prefix="dwg_convert_"))
    in_dir = tmp / "in"
    out_dir = tmp / "out"
    in_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    safe = in_dir / src.name
    shutil.copy2(src, safe)

    converters = [
        shutil.which("dwg2dxf"),
        shutil.which("ODAFileConverter"),
        shutil.which("ODAFileConverter.exe"),
    ]

    for conv in [c for c in converters if c]:
        try:
            name = os.path.basename(conv).lower()
            if "dwg2dxf" in name:
                out = out_dir / (src.stem + ".dxf")
                subprocess.run([conv, str(safe), str(out)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
                if out.exists() and out.stat().st_size > 100:
                    return str(out)
            else:
                subprocess.run(
                    [conv, str(in_dir), str(out_dir), "ACAD2018", "DXF", "0", "1"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=180,
                )
                found = list(out_dir.rglob("*.dxf"))
                if found:
                    found.sort(key=lambda p: p.stat().st_size, reverse=True)
                    if found[0].stat().st_size > 100:
                        return str(found[0])
        except Exception:
            continue

    return None

def _parse_ascii_dxf(path: str) -> Dict[str, Any]:
    text = _try_read_text(path)
    lines = [x.rstrip("\n") for x in text.splitlines()]
    pairs: List[Tuple[str, str]] = []
    i = 0
    while i + 1 < len(lines):
        code = lines[i].strip()
        value = lines[i + 1].strip()
        pairs.append((code, value))
        i += 2

    entities = []
    current: Optional[Dict[str, Any]] = None
    in_entities = False

    for code, value in pairs:
        if code == "0" and value.upper() == "SECTION":
            current = None
            continue
        if code == "2" and value.upper() == "ENTITIES":
            in_entities = True
            continue
        if code == "0" and value.upper() == "ENDSEC":
            if current:
                entities.append(current)
                current = None
            in_entities = False
            continue
        if not in_entities:
            continue

        if code == "0":
            if current:
                entities.append(current)
            current = {"type": value.upper(), "layer": "", "points": [], "texts": [], "raw": {}}
            continue

        if current is None:
            continue

        current["raw"].setdefault(code, []).append(value)
        if code == "8":
            current["layer"] = value
        elif code in ("1", "2", "3"):
            if value and len(value) <= 500:
                current["texts"].append(value)
        elif code in ("10", "20", "30", "11", "21", "31", "12", "22", "32"):
            try:
                current["points"].append((code, float(str(value).replace(",", "."))))
            except Exception:
                pass

    if current:
        entities.append(current)

    entity_counts = Counter(e.get("type") or "UNKNOWN" for e in entities)
    layer_counts = Counter(e.get("layer") or "0" for e in entities)

    texts = []
    for e in entities:
        for t in e.get("texts") or []:
            if t and t not in texts:
                texts.append(t)
            if len(texts) >= 80:
                break

    x_vals, y_vals = [], []
    for e in entities:
        coords = e.get("points") or []
        for code, val in coords:
            if code in ("10", "11", "12"):
                x_vals.append(val)
            elif code in ("20", "21", "22"):
                y_vals.append(val)

    extents = {}
    if x_vals and y_vals:
        extents = {
            "min_x": min(x_vals),
            "max_x": max(x_vals),
            "min_y": min(y_vals),
            "max_y": max(y_vals),
            "width": max(x_vals) - min(x_vals),
            "height": max(y_vals) - min(y_vals),
        }

    dims = []
    for t in texts:
        for m in re.findall(r"(?<!\d)(\d{2,6})(?!\d)", t):
            try:
                v = int(m)
                if 10 <= v <= 100000:
                    dims.append(v)
            except Exception:
                pass
    dims = sorted(set(dims))[:120]

    return {
        "parse_status": "DXF_PARSED",
        "raw_text_chars": len(text),
        "entities_total": len(entities),
        "entity_counts": dict(entity_counts.most_common(60)),
        "layers": dict(layer_counts.most_common(80)),
        "texts": texts[:80],
        "dimensions_detected": dims,
        "extents": extents,
    }

def _parse_dwg_metadata(path: str) -> Dict[str, Any]:
    p = Path(path)
    sig = _file_signature(path)
    return {
        "parse_status": "DWG_BINARY_METADATA_ONLY",
        "signature": sig,
        "file_size": p.stat().st_size if p.exists() else 0,
        "note": "DWG binary parsed as metadata only. For geometry extraction install ODAFileConverter or dwg2dxf on server; DXF is parsed directly",
    }

def _build_model(local_path: str, file_name: str, mime_type: str = "", user_text: str = "", topic_role: str = "") -> Dict[str, Any]:
    p = Path(local_path)
    ext = p.suffix.lower()
    source_path = str(p)
    converted_from_dwg = False

    if ext == ".dwg":
        converted = _try_convert_dwg_to_dxf(local_path)
        if converted:
            source_path = converted
            ext = ".dxf"
            converted_from_dwg = True

    if ext == ".dxf":
        parsed = _parse_ascii_dxf(source_path)
    elif p.suffix.lower() == ".dwg":
        parsed = _parse_dwg_metadata(local_path)
    else:
        parsed = {
            "parse_status": "UNSUPPORTED_DRAWING_FORMAT",
            "signature": _file_signature(local_path),
            "file_size": p.stat().st_size if p.exists() else 0,
        }

    drawing_text = "\n".join(parsed.get("texts") or [])
    section = _detect_section(file_name, user_text, drawing_text)
    entity_counts = parsed.get("entity_counts") or {}
    layers = parsed.get("layers") or {}
    texts = parsed.get("texts") or []

    output_documents = [
        "DOCX_DWG_DXF_ANALYSIS_REPORT",
        "XLSX_DWG_DXF_ENTITY_REGISTER",
        "ZIP_PROJECT_PACKAGE",
    ]

    if section in ("кж", "км", "кмд", "кр"):
        output_documents.extend(["SPECIFICATION_DRAFT", "STRUCTURAL_DRAWING_REGISTER"])
    if section == "ар":
        output_documents.extend(["ARCHITECTURAL_SHEET_REGISTER", "ROOM_PLAN_REVIEW"])

    risk_flags = []
    if parsed.get("parse_status") == "DWG_BINARY_METADATA_ONLY":
        risk_flags.append("DWG_GEOMETRY_NOT_EXTRACTED_WITHOUT_CONVERTER")
    if not layers:
        risk_flags.append("LAYERS_NOT_FOUND")
    if not entity_counts:
        risk_flags.append("ENTITIES_NOT_FOUND")
    if not texts:
        risk_flags.append("TEXT_LABELS_NOT_FOUND")

    model = {
        "schema": "DWG_DXF_PROJECT_MODEL_V1",
        "source_file": file_name or p.name,
        "source_path": local_path,
        "mime_type": mime_type,
        "topic_role": topic_role,
        "user_text": user_text,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "section": section,
        "section_title": SECTION_MAP.get(section, section.upper()),
        "norms": NORMS_MAP.get(section, []),
        "converted_from_dwg": converted_from_dwg,
        "parse": parsed,
        "layers": layers,
        "entity_counts": entity_counts,
        "texts": texts[:80],
        "dimensions_detected": parsed.get("dimensions_detected") or [],
        "extents": parsed.get("extents") or {},
        "output_documents": output_documents,
        "risk_flags": risk_flags,
        "status": "PARTIAL" if risk_flags else "CONFIRMED",
    }
    return model

def _summary(model: Dict[str, Any]) -> str:
    parse = model.get("parse") or {}
    entity_counts = model.get("entity_counts") or {}
    layers = model.get("layers") or {}
    risk_flags = model.get("risk_flags") or []
    lines = [
        "DWG/DXF проектный контур отработал",
        f"Файл: {model.get('source_file')}",
        f"Раздел: {model.get('section_title')}",
        f"Статус: {model.get('status')}",
        f"Parse: {parse.get('parse_status')}",
        f"Слоёв: {len(layers)}",
        f"Сущностей: {sum(int(v) for v in entity_counts.values()) if entity_counts else 0}",
    ]
    if entity_counts:
        lines.append("Типы сущностей: " + ", ".join(f"{k}:{v}" for k, v in list(entity_counts.items())[:12]))
    if layers:
        lines.append("Слои: " + ", ".join(list(layers.keys())[:20]))
    if model.get("dimensions_detected"):
        lines.append("Размеры/числа из подписей: " + ", ".join(map(str, model.get("dimensions_detected")[:30])))
    if model.get("norms"):
        lines.append("Нормы: " + ", ".join(model.get("norms")))
    if risk_flags:
        lines.append("Ограничения: " + ", ".join(risk_flags))
    lines.append("Артефакты: DOCX отчёт + XLSX реестр + ZIP пакет")
    return "\n".join(lines).strip()

def _write_docx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"dwg_dxf_report_{_safe_name(task_id, 'manual')}.docx"
    try:
        from docx import Document

        doc = Document()
        doc.add_heading("DWG/DXF PROJECT MODEL", level=1)
        doc.add_paragraph(f"Файл: {model.get('source_file')}")
        doc.add_paragraph(f"Раздел: {model.get('section_title')}")
        doc.add_paragraph(f"Статус: {model.get('status')}")
        doc.add_paragraph(f"Parse: {(model.get('parse') or {}).get('parse_status')}")

        doc.add_heading("Нормативная база", level=2)
        norms = model.get("norms") or []
        if norms:
            for n in norms:
                doc.add_paragraph(f"• {n}")
        else:
            doc.add_paragraph("Норма не подтверждена")

        doc.add_heading("Слои", level=2)
        layers = model.get("layers") or {}
        if layers:
            table = doc.add_table(rows=1, cols=2)
            table.style = "Table Grid"
            table.rows[0].cells[0].text = "Слой"
            table.rows[0].cells[1].text = "Кол-во"
            for name, cnt in list(layers.items())[:80]:
                row = table.add_row().cells
                row[0].text = str(name)
                row[1].text = str(cnt)
        else:
            doc.add_paragraph("Слои не извлечены")

        doc.add_heading("Сущности", level=2)
        ents = model.get("entity_counts") or {}
        if ents:
            table = doc.add_table(rows=1, cols=3)
            table.style = "Table Grid"
            table.rows[0].cells[0].text = "Тип"
            table.rows[0].cells[1].text = "Кол-во"
            table.rows[0].cells[2].text = "Назначение"
            for name, cnt in list(ents.items())[:80]:
                row = table.add_row().cells
                row[0].text = str(name)
                row[1].text = str(cnt)
                row[2].text = ENTITY_PROJECT_HINTS.get(str(name), "")
        else:
            doc.add_paragraph("Сущности не извлечены")

        doc.add_heading("Текстовые подписи", level=2)
        texts = model.get("texts") or []
        if texts:
            for t in texts[:60]:
                doc.add_paragraph(f"• {t}")
        else:
            doc.add_paragraph("Текстовые подписи не извлечены")

        doc.add_heading("Проектные выходные документы", level=2)
        for x in model.get("output_documents") or []:
            doc.add_paragraph(f"• {x}")

        doc.add_heading("Ограничения", level=2)
        risks = model.get("risk_flags") or []
        if risks:
            for r in risks:
                doc.add_paragraph(f"• {r}")
        else:
            doc.add_paragraph("Критичных ограничений не выявлено")

        doc.save(out)
        return str(out)
    except Exception:
        txt = out.with_suffix(".txt")
        txt.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(txt)

def _write_xlsx(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"dwg_dxf_register_{_safe_name(task_id, 'manual')}.xlsx"
    try:
        from openpyxl import Workbook
        wb = Workbook()

        ws = wb.active
        ws.title = "Summary"
        rows = [
            ("Файл", model.get("source_file")),
            ("Раздел", model.get("section_title")),
            ("Статус", model.get("status")),
            ("Parse", (model.get("parse") or {}).get("parse_status")),
            ("Нормы", ", ".join(model.get("norms") or [])),
            ("Ограничения", ", ".join(model.get("risk_flags") or [])),
        ]
        for i, (k, v) in enumerate(rows, 1):
            ws.cell(i, 1, k)
            ws.cell(i, 2, v)

        ws2 = wb.create_sheet("Layers")
        ws2.append(["Слой", "Кол-во"])
        for k, v in (model.get("layers") or {}).items():
            ws2.append([k, v])

        ws3 = wb.create_sheet("Entities")
        ws3.append(["Тип", "Кол-во", "Назначение"])
        for k, v in (model.get("entity_counts") or {}).items():
            ws3.append([k, v, ENTITY_PROJECT_HINTS.get(str(k), "")])

        ws4 = wb.create_sheet("Texts")
        ws4.append(["№", "Текст"])
        for i, t in enumerate(model.get("texts") or [], 1):
            ws4.append([i, t])

        ws5 = wb.create_sheet("ModelJSON")
        raw = json.dumps(model, ensure_ascii=False, indent=2)
        for i, line in enumerate(raw.splitlines(), 1):
            ws5.cell(i, 1, line)

        wb.save(out)
        wb.close()
        return str(out)
    except Exception:
        csv = out.with_suffix(".csv")
        lines = ["key,value"]
        lines.append(f"file,{model.get('source_file')}")
        lines.append(f"section,{model.get('section_title')}")
        lines.append(f"status,{model.get('status')}")
        csv.write_text("\n".join(lines), encoding="utf-8")
        return str(csv)

def _write_json(model: Dict[str, Any], task_id: str) -> str:
    out = Path(tempfile.gettempdir()) / f"dwg_dxf_model_{_safe_name(task_id, 'manual')}.json"
    out.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out)

def _zip_artifacts(paths: List[str], task_id: str, source_file: str = "") -> str:
    out = Path(tempfile.gettempdir()) / f"dwg_dxf_project_package_{_safe_name(task_id, 'manual')}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p and os.path.exists(p):
                z.write(p, arcname=os.path.basename(p))
        manifest = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "task_id": task_id,
            "source_file": source_file,
            "files": [os.path.basename(p) for p in paths if p and os.path.exists(p)],
            "engine": "DWG_DXF_PROJECT_CLOSE_V1",
        }
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return str(out)

def process_drawing_file(
    local_path: str,
    file_name: str = "",
    mime_type: str = "",
    user_text: str = "",
    topic_role: str = "",
    task_id: str = "artifact",
    topic_id: int = 0,
) -> Dict[str, Any]:
    if not local_path or not os.path.exists(local_path):
        return {
            "success": False,
            "error": "DRAWING_FILE_NOT_FOUND",
            "summary": "DWG/DXF файл не найден",
        }

    model = _build_model(local_path, file_name or os.path.basename(local_path), mime_type, user_text, topic_role)
    docx = _write_docx(model, task_id)
    xlsx = _write_xlsx(model, task_id)
    js = _write_json(model, task_id)
    package = _zip_artifacts([docx, xlsx, js], task_id, model.get("source_file") or file_name)

    return {
        "success": True,
        "engine": "DWG_DXF_PROJECT_CLOSE_V1",
        "summary": _summary(model),
        "model": model,
        "docx_path": docx,
        "xlsx_path": xlsx,
        "json_path": js,
        "artifact_path": package,
        "artifact_name": f"{Path(file_name or local_path).stem}_dwg_dxf_project_package.zip",
        "extra_artifacts": [docx, xlsx, js],
        "status": model.get("status"),
    }

async def process_drawing_file_async(*args, **kwargs) -> Dict[str, Any]:
    return process_drawing_file(*args, **kwargs)

# === END_DWG_DXF_PROJECT_CLOSE_V1 ===

====================================================================================================
END_FILE: core/dwg_engine.py
FILE_CHUNK: 1/1
====================================================================================================
