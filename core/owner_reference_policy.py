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
