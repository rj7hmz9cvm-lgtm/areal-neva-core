# === ESTIMATE_TEMPLATE_POLICY_CONTEXT_V4_TOP_LOGISTICS ===
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

BASE = Path("/root/.areal-neva-core")
REGISTRY_PATH = BASE / "config" / "estimate_template_registry.json"

TRIGGER_RE = re.compile(
    r"(смет|расчет|расч[её]т|стоимость|материал|логист|доставка|удален|удалён|км|кирпич|газобетон|каркас|монолит|фундамент|кровл|перекр|отделк|инженер|плита|дом)",
    re.I,
)

def _s(v: Any) -> str:
    return "" if v is None else str(v)

def _load_registry() -> Dict[str, Any]:
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def build_estimate_template_context(user_text: str = "", limit: int = 12000) -> str:
    text = _s(user_text)
    if not TRIGGER_RE.search(text):
        return ""

    data = _load_registry()
    policy = data.get("estimate_top_templates_logistics_canon_v4") or data.get("estimate_template_formula_price_confirm_v3") or data.get("estimate_template_formula_price_confirm_v2")
    if not isinstance(policy, dict):
        return ""

    lines = []
    lines.append("ESTIMATE_TEMPLATE_CANON: ACTIVE")
    lines.append("Version: ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4")
    lines.append("")
    lines.append("CORE RULE:")
    lines.append("Use top estimate files as scalable calculation templates, not as fixed price lists")
    lines.append("Preserve estimate logic: sections, rows, formulas, columns, totals, notes, exclusions")
    lines.append("Use same logic for any material: brick, gasbeton, frame, monolith, roof, slab, finishing, engineering")
    lines.append("Never mix scenarios without explicit user instruction")
    lines.append("")
    lines.append("TOP TEMPLATE FILES:")
    for src in policy.get("source_files", []):
        lines.append(f"- {src.get('title')} | role={src.get('template_role')} | formulas={src.get('formula_total')} | id={src.get('file_id')}")
    lines.append("")
    lines.append("PRICE CONFIRMATION RULE:")
    lines.append("Do not silently insert material prices")
    lines.append("Before final XLSX/PDF, search current prices online and show source, price, unit, region/date, link")
    lines.append("Propose average/median price and ask user to choose: average / minimum / maximum / specific source / manual price")
    lines.append("User can add markup, discount, reserve, manual correction per position, section or whole estimate")
    lines.append("Final XLSX/PDF is forbidden before price confirmation")
    lines.append("")
    lines.append("LOGISTICS RULE:")
    lines.append("Before final estimate, ask for object location or distance from city")
    lines.append("Ask access conditions: road, truck access, unloading, crane/manipulator need, storage, site restrictions")
    lines.append("Account for delivery, transport, unloading, machinery, crew travel, accommodation if remote")
    lines.append("A house near city and a house 200 km away cannot have the same final cost")
    lines.append("If logistics data is missing, ask one concise clarification before final price")
    lines.append("")
    cols = policy.get("canonical_columns") or []
    if cols:
        lines.append("CANONICAL_COLUMNS:")
        lines.append(" | ".join(_s(x) for x in cols))
        lines.append("")
    sections = policy.get("canonical_sections") or []
    if sections:
        lines.append("CANONICAL_SECTIONS:")
        for i, sec in enumerate(sections, 1):
            lines.append(f"{i}. {sec}")
        lines.append("")
    groups = policy.get("universal_material_groups") or {}
    if groups:
        lines.append("UNIVERSAL_MATERIAL_GROUPS:")
        for k, vals in groups.items():
            if isinstance(vals, list):
                lines.append(f"- {k}: " + ", ".join(_s(v) for v in vals))
        lines.append("")
    return "\n".join(lines)[:limit]

# === END_ESTIMATE_TEMPLATE_POLICY_CONTEXT_V4_TOP_LOGISTICS ===
