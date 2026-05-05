# === LOAD_CALCULATION_ENGINE_FACT_ONLY_V1 ===
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

ENGINE_VERSION = "LOAD_CALCULATION_ENGINE_FACT_ONLY_V1"

def _to_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", "."))
    except Exception:
        return None

def _norms(text: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        from core.normative_engine import search_norms_sync
        return search_norms_sync(text or "", limit=limit)
    except Exception:
        return []

@dataclass
class LoadCalculationResult:
    schema: str
    engine: str
    status: str
    permanent_kpa: Optional[float]
    temporary_kpa: Optional[float]
    snow_kpa: Optional[float]
    wind_kpa: Optional[float]
    supplied_sum_kpa: Optional[float]
    missing_inputs: List[str]
    norms: List[Dict[str, Any]]
    limitations: List[str]

def calculate_loads_fact_only(
    permanent_kpa: Any = None,
    temporary_kpa: Any = None,
    snow_kpa: Any = None,
    wind_kpa: Any = None,
    source_text: str = "",
) -> Dict[str, Any]:
    permanent = _to_float(permanent_kpa)
    temporary = _to_float(temporary_kpa)
    snow = _to_float(snow_kpa)
    wind = _to_float(wind_kpa)

    values = {
        "permanent_kpa": permanent,
        "temporary_kpa": temporary,
        "snow_kpa": snow,
        "wind_kpa": wind,
    }

    missing = [k for k, v in values.items() if v is None]
    present = [v for v in values.values() if v is not None]
    supplied_sum = round(sum(present), 6) if present else None

    return asdict(LoadCalculationResult(
        schema="LoadCalculationResultV1",
        engine=ENGINE_VERSION,
        status="PARTIAL_CALC_INPUT_BASED" if missing else "INPUT_BASED_SUM_READY",
        permanent_kpa=permanent,
        temporary_kpa=temporary,
        snow_kpa=snow,
        wind_kpa=wind,
        supplied_sum_kpa=supplied_sum,
        missing_inputs=missing,
        norms=_norms(source_text or "нагрузки постоянные временные снеговые ветровые сочетания СП 20", limit=8),
        limitations=[
            "Расчёт использует только явно переданные числовые значения",
            "Нормативные таблицы и пункты не подставляются автоматически",
            "Полный расчёт несущей способности не выполняется без расчётной записки и исходных данных",
            "Сочетания нагрузок не рассчитываются без явно заданных коэффициентов / расчётной схемы",
        ],
    ))

def build_load_report_text(result: Dict[str, Any]) -> str:
    lines = [
        "Расчёт нагрузок",
        "",
        f"Статус: {result.get('status', 'UNKNOWN')}",
        f"Постоянные нагрузки, кПа: {result.get('permanent_kpa')}",
        f"Временные нагрузки, кПа: {result.get('temporary_kpa')}",
        f"Снеговые нагрузки, кПа: {result.get('snow_kpa')}",
        f"Ветровые нагрузки, кПа: {result.get('wind_kpa')}",
        f"Сумма переданных нагрузок, кПа: {result.get('supplied_sum_kpa')}",
        "",
        "Недостающие исходные данные:",
    ]

    missing = result.get("missing_inputs") or []
    lines += [f"- {x}" for x in missing] if missing else ["- нет"]

    lines += ["", "Нормативная привязка:"]
    norms = result.get("norms") or []
    if norms:
        for n in norms:
            lines.append(f"- {n.get('norm_id', '')}: {n.get('section', '')}")
    else:
        lines.append("- норма не подтверждена")

    lines += ["", "Ограничения:"]
    for x in result.get("limitations") or []:
        lines.append(f"- {x}")

    return "\n".join(lines).strip()

__all__ = [
    "ENGINE_VERSION",
    "calculate_loads_fact_only",
    "build_load_report_text",
]
# === END_LOAD_CALCULATION_ENGINE_FACT_ONLY_V1 ===
