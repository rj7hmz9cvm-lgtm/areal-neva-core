from __future__ import annotations

import re
from collections import OrderedDict
from typing import Any, Dict, Iterable, List, Optional, Tuple


_PRIORITY = {
    "direct_quantity": 50,
    "quantity": 50,
    "calculated_quantity": 40,
    "derived_quantity": 30,
    "total": 25,
    "position": 20,
    "property": 10,
    "missing": 0,
}


def _s(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _low(value: Any) -> str:
    return _s(value).replace("ё", "е").lower()


def _num(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = _s(value).replace(" ", "").replace(",", ".")
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(m.group(0)) if m else None


def normalize_units(value: Any, unit: str, raw_text: str = "") -> Dict[str, Any]:
    raw_unit = _low(unit or raw_text)
    canonical = _s(unit)
    quantity_type = ""
    if "шт" in raw_unit or "pcs" in raw_unit or "pieces" in raw_unit:
        canonical = "pcs"
    elif "тн" in raw_unit or "тонн" in raw_unit or "тонна" in raw_unit or raw_unit == "т" or raw_unit == "ton":
        canonical = "t"
    elif "кг" in raw_unit or raw_unit == "kg":
        canonical = "kg"
    elif "м2" in raw_unit or "м²" in raw_unit or "m2" in raw_unit or "sqm" in raw_unit or "sq.m" in raw_unit or "кв.м" in raw_unit:
        canonical = "m2"
    elif "м3" in raw_unit or "м³" in raw_unit or "m3" in raw_unit or "куб.м" in raw_unit:
        canonical = "m3"
    elif "п.м" in raw_unit or "пог.м" in raw_unit or "м.п" in raw_unit or "linear meter" in raw_unit or raw_unit == "lm":
        canonical = "m"
    elif raw_unit in ("м", "m"):
        canonical = "m"
    elif raw_unit in ("л", "литр", "l"):
        canonical = "l"
    aliases = {
        "m2": ("м2", "м²", "m2", "sqm", "sq.m", "кв.м"),
        "m3": ("м3", "м³", "m3", "куб.м"),
        "m": ("п.м", "пог.м", "м.п", "м.п.", "lm", "linear meter"),
        "kg": ("кг", "kg"),
        "t": ("т", "тн", "тонн", "тонна", "ton"),
        "pcs": ("шт", "шт.", "pcs", "pieces"),
        "l": ("л", "литр", "l"),
    }
    if canonical == _s(unit):
        for key, variants in aliases.items():
            if any(v in raw_unit for v in variants):
                canonical = key
                break
    if canonical == "m2":
        quantity_type = "area_m2"
    elif canonical == "m3":
        quantity_type = "volume_m3"
    elif canonical == "m":
        quantity_type = "length_m"
    elif canonical == "kg":
        quantity_type = "mass_kg"
    elif canonical == "t":
        quantity_type = "mass_t"
    elif canonical == "pcs":
        quantity_type = "count_pcs"
    elif canonical == "l":
        quantity_type = "liters"
    return {"value": _num(value), "unit": canonical, "raw_unit": unit, "quantity_type": quantity_type}


def public_unit(unit: str, quantity_type: str = "") -> str:
    unit = _s(unit)
    if unit == "m3":
        return "м³"
    if unit == "m2":
        return "м²"
    if unit == "m":
        return "п.м"
    if unit == "pcs":
        return "шт"
    if unit == "l":
        return "л"
    if unit == "kg":
        return "кг"
    if unit == "t":
        return "т"
    return unit


def normalize_material_alias(raw_name: str, raw_text: str = "") -> Dict[str, Any]:
    text = f"{_low(raw_name)} {_low(raw_text)}"
    aliases: List[str] = []
    material_family = "other"
    role = "other"
    properties: Dict[str, Any] = {}
    public_name = _s(raw_name) or "Позиция"

    def thickness() -> Optional[int]:
        m = re.search(r"(\d{2,3})\s*мм", text)
        return int(m.group(1)) if m else None

    if "сэндвич" in text or "sandwich" in text or "wall panel" in text or "roof panel" in text or "wall_panel" in text or "roof_panel" in text:
        material_family = "sandwich_panel"
        role = "roof" if any(x in text for x in ("кров", "roof")) else "wall"
        t = thickness()
        if t:
            properties["thickness_mm"] = t
        public_name = "Кровельные сэндвич-панели" if role == "roof" else "Стеновые сэндвич-панели"
        aliases.extend(["sandwich panel", "сэндвич-панель"])
    elif "гидроизоляц" in text or "waterproof" in text or "мембран" in text:
        material_family = "waterproofing"
        role = "floor"
        public_name = "Гидроизоляция"
    elif "пленэкс" in text or "plenex" in text:
        material_family = "insulation"
        role = "floor"
        properties["brand"] = "Пленэкс"
        public_name = "Пленэкс"
    elif "вилатерм" in text or "vilaterm" in text:
        material_family = "sealant_backer"
        role = "joint"
        properties["brand"] = "Вилатерм"
        public_name = "Вилатерм"
    elif "герметик" in text or "pu-40" in text or "pu40" in text or "sealant" in text:
        material_family = "sealant"
        role = "joint"
        properties["brand"] = "PU-40" if "40" in text else ""
        public_name = "Герметик PU-40" if properties["brand"] else "Герметик"
    elif "песок" in text or "sand" in text:
        material_family = "sand"
        role = "floor"
        public_name = "Песок"
    elif "щеб" in text or "gravel" in text:
        material_family = "gravel"
        role = "foundation"
        public_name = "Щебень"
    elif any(x in text for x in ("бетон", "concrete", "бст", "bst", "bct", "grout")):
        material_family = "concrete"
        role = "grout" if "grout" in text or "подлив" in text else "foundation_beam" if "бфм" in text or "балк" in text else "foundation" if "фм" in text or "фундамент" in text else "slab" if "плит" in text or "пол" in text else "other"
        grade = ""
        m = re.search(r"[вb][\s_]*(\d{1,2}(?:[,. _]\d)?)", text, re.I)
        if m:
            grade = "B" + m.group(1).replace(",", ".").replace(" ", "_").replace(".", "_")
        properties["grade"] = grade or "B25"
        public_name = f"Бетон БСТ {properties['grade'].replace('B', 'В').replace('_', '.')}"
    elif any(x in text for x in ("арматур", "а500", "a500", "а240", "a240", "rebar")):
        material_family = "rebar"
        role = "frame"
        cls = "A500C" if "500" in text else "A240" if "240" in text else ""
        dia = None
        m = re.search(r"(?:^|\D)(\d{1,2})[-–]?\s*(?:а|a)\s*(?:500|240)|\bd\s*(\d{1,2})\b", text)
        if m:
            dia = int(m.group(1) or m.group(2))
        properties.update({"class": cls, "diameter_mm": dia})
        public_name = "Арматура " + (cls or "")
    elif any(x in text for x in ("кирпич", "brick")):
        material_family = "masonry"
        role = "wall"
        properties["type"] = "brick"
        m = re.search(r"m\s?(\d{2,3})|м\s?(\d{2,3})", text, re.I)
        if m:
            properties["grade"] = "M" + (m.group(1) or m.group(2))
        m_t = re.search(r"\bt\s*(\d{2,3})\b", text)
        t = int(m_t.group(1)) if m_t else thickness()
        if t:
            properties["thickness_mm"] = t
        public_name = "Кирпичная кладка"
    elif any(x in text for x in ("блок", "block", "газобетон")):
        material_family = "masonry"
        role = "wall"
        properties["type"] = "block"
        t = thickness()
        if t:
            properties["thickness_mm"] = t
        public_name = "Блоки стеновые"
    elif any(x in text for x in ("доска", "board")):
        material_family = "timber"
        role = "other"
        m = re.search(r"(\d{2,3})\s*[xх*]\s*(\d{2,3})", text)
        if m:
            properties["section_mm"] = f"{m.group(1)}x{m.group(2)}"
        public_name = "Доска"
    elif any(x in text for x in ("брус", "timber beam")):
        material_family = "timber"
        role = "beam"
        public_name = "Брус"
    elif any(x in text for x in ("гкл", "гвл", "гсп", "drywall")):
        material_family = "drywall_partition"
        role = "partition"
        public_name = "Гипсокартон"
    elif any(x in text for x in ("профил", "profile", "швеллер", "уголок")):
        material_family = "profile"
        role = "frame"
        public_name = "Профиль"
    elif any(x in text for x in ("утепл", "insulation", "xps")):
        material_family = "insulation"
        role = "other"
        public_name = "Утеплитель"
    elif any(x in text for x in ("сталь", "steel", "лист", "ферм", "колонн", "балк", "связ", "прогон")):
        material_family = "rolled_steel"
        role = "frame"
        public_name = "Металлоконструкции"

    return {
        "material_family": material_family,
        "role": role,
        "scope": role,
        "properties": properties,
        "public_name": public_name.strip(),
        "aliases": aliases,
    }


def build_canonical_keys(item: Dict[str, Any]) -> Dict[str, str]:
    family = _s(item.get("material_family") or "other")
    role = _s(item.get("role") or "other")
    props = item.get("properties") or {}
    canonical = f"{family}.{role}"
    material = family
    position = canonical
    if family == "concrete":
        grade = _s(props.get("grade") or "B25")
        canonical = f"concrete.{grade}.{role}"
        material = f"concrete.{grade}"
        mark = _s(item.get("mark"))
        position = f"foundation.{mark}.concrete.{grade}" if mark else canonical
    elif family == "sandwich_panel":
        canonical = f"sandwich_panel.{role}"
        t = props.get("thickness_mm")
        material = f"{canonical}.t{t}" if t else canonical
        position = canonical
    elif family == "rebar":
        cls = _s(props.get("class") or "")
        dia = props.get("diameter_mm")
        canonical = "rebar" + (f".{cls}" if cls else "") + (f".d{dia}" if dia else "")
        material = canonical
        position = canonical
    elif family == "timber":
        section = _s(props.get("section_mm") or "")
        canonical = f"timber.{role}" + (f".{section}" if section else "")
        material = canonical
        position = canonical
    elif family == "masonry":
        typ = _s(props.get("type") or "masonry")
        grade = _s(props.get("grade") or "")
        t = props.get("thickness_mm")
        canonical = f"masonry.{typ}" + (f".{grade}" if grade else "") + (f".t{t}" if t else "")
        material = canonical
        position = f"wall.{canonical}"
    elif family in ("waterproofing", "sand", "gravel", "sealant", "insulation", "sealant_backer"):
        brand = _s(props.get("brand") or "")
        canonical = family + (f".{brand}" if brand else "")
        material = canonical
        position = canonical
    return {"canonical_key": canonical, "material_total_key": material, "position_key": position}


def _source_from(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source_file": _s(row.get("source_file")),
        "page": row.get("page"),
        "sheet": row.get("sheet"),
        "table_name": row.get("table_name"),
        "row_text": _s(row.get("row_text") or row.get("text") or row.get("calculation") or row.get("source")),
        "method": _s(row.get("method") or "calculated"),
        "confidence": _s(row.get("confidence") or "direct"),
    }


def canonicalize_construction_item(item: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(item or {})
    raw_name = _s(row.get("public_name") or row.get("item") or row.get("name") or row.get("key") or row.get("material") or row.get("missing_item"))
    raw_text = " ".join(_s(row.get(k)) for k in ("unit", "note", "calculation"))
    alias = normalize_material_alias(raw_name, raw_text)
    item_type = _s(row.get("item_type") or row.get("_item_type") or "quantity")
    unit_info = normalize_units(row.get("value") if row.get("value") is not None else row.get("qty") or row.get("total_volume_m3"), _s(row.get("unit")), raw_text)
    raw_unit_text = _low(row.get("unit") or raw_text)
    if ("шт" in raw_unit_text or "pcs" in raw_unit_text or "pieces" in raw_unit_text) and unit_info.get("unit") == "t":
        unit_info = dict(unit_info)
        unit_info["unit"] = "pcs"
        unit_info["quantity_type"] = "count_pcs"
    props = dict(alias.get("properties") or {})
    if item_type == "property":
        prop_name = _s(row.get("name") or row.get("key"))
        if prop_name:
            props[prop_name] = row.get("value")
    normalized = {
        "canonical_key": "",
        "material_total_key": "",
        "position_key": "",
        "public_name": alias.get("public_name") or raw_name,
        "raw_names": [raw_name] if raw_name else [],
        "aliases": alias.get("aliases") or [],
        "item_type": item_type,
        "material_family": alias.get("material_family"),
        "role": alias.get("role"),
        "scope": alias.get("scope"),
        "operation": _s(row.get("operation")),
        "properties": props,
        "quantity": unit_info,
        "source": _source_from(row),
        "source_items": [row],
        "mark": row.get("mark"),
    }
    normalized.update(build_canonical_keys(normalized))
    return normalized


def deduplicate_construction_items(items: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    groups: "OrderedDict[Tuple[str, str, str, str, str, str], Dict[str, Any]]" = OrderedDict()
    for item in items:
        quantity = item.get("quantity") or {}
        key = (
            _s(item.get("canonical_key")),
            _s(item.get("item_type")),
            _s(quantity.get("quantity_type")),
            _s(quantity.get("unit")),
            _s(item.get("role")),
            _s(item.get("scope")),
        )
        current = groups.get(key)
        if not current:
            groups[key] = dict(item, source_items=list(item.get("source_items") or []))
            continue
        current["raw_names"] = sorted(set((current.get("raw_names") or []) + (item.get("raw_names") or [])))
        current["aliases"] = sorted(set((current.get("aliases") or []) + (item.get("aliases") or [])))
        current.setdefault("source_items", []).extend(item.get("source_items") or [])
        if _PRIORITY.get(_s(item.get("item_type")), 0) > _PRIORITY.get(_s(current.get("item_type")), 0):
            replacement = dict(item, source_items=current["source_items"])
            replacement["raw_names"] = current["raw_names"]
            replacement["aliases"] = current["aliases"]
            groups[key] = replacement
    return {"items": list(groups.values()), "groups": list(groups.keys())}


def aggregate_construction_totals(items: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    totals: "OrderedDict[Tuple[str, str], Dict[str, Any]]" = OrderedDict()
    seen_sources = set()
    for item in items:
        if _s(item.get("item_type")) in ("property", "missing"):
            continue
        quantity = item.get("quantity") or {}
        value = quantity.get("value")
        unit = _s(quantity.get("unit"))
        if value is None or not unit:
            continue
        source = item.get("source") or {}
        source_key = (_s(item.get("material_total_key")), _s(source.get("source_file")), _s(source.get("page")), _s(source.get("row_text")), value, unit)
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)
        key = (_s(item.get("material_total_key")), unit)
        if key not in totals:
            totals[key] = {
                "material_total_key": key[0],
                "public_name": item.get("public_name"),
                "value": 0.0,
                "unit": unit,
                "source_items": [],
            }
        totals[key]["value"] = round(float(totals[key]["value"]) + float(value), 4)
        totals[key]["source_items"].extend(item.get("source_items") or [])
    return {"totals_by_material": list(totals.values())}


def _flatten_items(items: Any) -> List[Dict[str, Any]]:
    if isinstance(items, list):
        return [dict(x) for x in items if isinstance(x, dict)]
    if not isinstance(items, dict):
        return []
    rows: List[Dict[str, Any]] = []
    for key, item_type in (
        ("properties", "property"),
        ("quantities", "direct_quantity"),
        ("calculated_quantities", "calculated_quantity"),
        ("derived_quantities", "derived_quantity"),
        ("positions", "position"),
        ("totals", "total"),
    ):
        for row in items.get(key) or []:
            if isinstance(row, dict):
                copy = dict(row)
                copy["_item_type"] = item_type
                rows.append(copy)
    for name in items.get("missing_items") or []:
        rows.append({"name": name, "_item_type": "missing"})
    return rows


def _normalize_missing(missing: Iterable[Any], present_keys: Iterable[str]) -> List[str]:
    present = set(present_keys)
    result: List[str] = []
    for raw in missing or []:
        name = _s(raw.get("name") if isinstance(raw, dict) else raw)
        key = canonicalize_construction_item({"name": name, "_item_type": "missing"}).get("canonical_key")
        if name in ("wall_panel_area_m2", "gross_wall_panel_area_m2") and any(k.startswith("sandwich_panel.wall") for k in present):
            continue
        if name in ("roof_panel_area_m2", "gross_roof_panel_area_m2") and any(k.startswith("sandwich_panel.roof") for k in present):
            continue
        if "foundation_concrete" in name and any(k.startswith("concrete.") for k in present):
            continue
        if "steel_frame" in name and any(k.startswith("rolled_steel") for k in present):
            continue
        if key not in present and name not in result:
            result.append(name)
    return result


def normalize_construction_items(items: Any, project_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    flat = _flatten_items(items)
    normalized = [canonicalize_construction_item(row) for row in flat]
    dedup = deduplicate_construction_items(normalized)["items"]
    totals = aggregate_construction_totals(dedup)["totals_by_material"]
    present_keys = [x.get("canonical_key") for x in dedup] + [x.get("material_total_key") for x in dedup]
    missing = _normalize_missing((items or {}).get("missing_items") if isinstance(items, dict) else [], present_keys)

    public_groups = []
    public_seen = set()
    for item in dedup:
        if _s(item.get("item_type")) in ("property", "missing"):
            continue
        if _s(item.get("material_family")) == "other":
            continue
        quantity = item.get("quantity") or {}
        if _s(item.get("item_type")) == "position" and not (quantity.get("value") is not None and quantity.get("unit")):
            continue
        public_key = (
            _s(item.get("material_total_key")),
            _s(item.get("item_type")),
            _s(quantity.get("value")),
            _s(quantity.get("unit")),
        )
        if public_key in public_seen:
            continue
        public_seen.add(public_key)
        public_groups.append({
            "canonical_key": item.get("canonical_key"),
            "material_total_key": item.get("material_total_key"),
            "position_key": item.get("position_key"),
            "public_name": item.get("public_name"),
            "value": quantity.get("value"),
            "unit": quantity.get("unit"),
            "public_unit": public_unit(quantity.get("unit"), quantity.get("quantity_type")),
            "quantity_type": quantity.get("quantity_type"),
            "item_type": item.get("item_type"),
            "source_items": item.get("source_items") or [],
        })

    price_seen = set()
    price_items = []
    for item in public_groups:
        key = _s(item.get("material_total_key") or item.get("canonical_key"))
        if not key or key in price_seen:
            continue
        price_seen.add(key)
        price_items.append({
            "material_total_key": key,
            "canonical_key": item.get("canonical_key"),
            "public_name": item.get("public_name"),
            "unit": item.get("unit"),
            "qty": item.get("value"),
        })

    estimate_rows = build_estimate_rows(public_groups, missing)

    return {
        "normalized_items": normalized,
        "deduplicated_items": dedup,
        "public_groups": public_groups,
        "totals_by_material": totals,
        "price_items": price_items,
        "estimate_rows": estimate_rows,
        "missing_items": missing,
    }


def _section_for_item(item: Dict[str, Any]) -> str:
    key = _low(item.get("material_total_key") or item.get("canonical_key") or item.get("public_name"))
    name = _low(item.get("public_name"))
    if "concrete" in key and ("foundation" in key or "в30" in name or "в7.5" in name):
        return "Фундамент"
    if "sandwich_panel.wall" in key:
        return "Стены / панели"
    if "sandwich_panel.roof" in key:
        return "Кровля"
    if "waterproofing" in key or "insulation" in key:
        return "Гидроизоляция / утепление"
    if "rebar" in key:
        return "Арматура / детали"
    if "sealant" in key:
        return "Герметики / вспомогательные материалы"
    if "sand" in key or "concrete" in key:
        return "Пол / плита"
    return "Проектные позиции"


def build_estimate_rows(public_groups: Iterable[Dict[str, Any]], missing_items: Iterable[str] = ()) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in public_groups or []:
        if not isinstance(item, dict):
            continue
        qty = item.get("value")
        if qty is None:
            continue
        source_items = item.get("source_items") or []
        source0 = source_items[0] if source_items and isinstance(source_items[0], dict) else {}
        src = source0.get("source") if isinstance(source0.get("source"), dict) else source0
        rows.append({
            "section": _section_for_item(item),
            "name": item.get("public_name"),
            "unit": public_unit(item.get("unit"), item.get("quantity_type")),
            "qty": qty,
            "work_unit_price": None,
            "material_unit_price": None,
            "work_total": None,
            "material_total": None,
            "total": None,
            "source": {
                "source_type": "PROJECT_POSITION",
                "source_file": _s(src.get("source_file")),
                "page": src.get("page"),
                "table_name": _s(src.get("table_name")),
                "row_text": _s(src.get("row_text")),
                "calculation": _s(src.get("calculation") or source0.get("calculation")),
            },
            "canonical_key": item.get("canonical_key"),
            "position_key": item.get("position_key"),
            "material_total_key": item.get("material_total_key"),
        })
    return rows
