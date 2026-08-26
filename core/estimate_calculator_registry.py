# === UNIVERSAL_ESTIMATE_CALCULATOR_REGISTRY_V1 ===
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

REGISTRY_VERSION = "UNIVERSAL_ESTIMATE_CALCULATOR_REGISTRY_V1"

ESTIMATE_CALCULATOR: Dict[str, Any] = {
    "id": "universal_estimate_calculator",
    "title": "Универсальный калькулятор смет",
    "status": "active",
    "url": "https://smeta-teplograd.ky3bkuh6at9l.chatgpt.site/",
    "access": "owner_only",
    "modes": {
        "heating_water": "Отопление и водоснабжение",
        "general_estimate": "Общая строительная смета",
    },
    "suppliers": {
        "heating_water": {
            "name": "Теплоград",
            "catalog_url": "https://www.teplograd.ru/catalog/",
        },
        "general_construction": {
            "name": "Петрович",
            "catalog_url": "https://petrovich.ru/catalog/",
        },
        "manual": {
            "name": "Другой поставщик",
            "catalog_url": "",
        },
    },
    "outputs": ["csv", "pdf", "commercial_request"],
}


def get_estimate_calculator() -> Dict[str, Any]:
    return deepcopy(ESTIMATE_CALCULATOR)


def get_supplier(scope: str) -> Dict[str, str]:
    key = (scope or "").strip().lower()
    if key in {"heating", "water", "plumbing", "отопление", "водоснабжение", "сантехника"}:
        return deepcopy(ESTIMATE_CALCULATOR["suppliers"]["heating_water"])
    if key in {"construction", "general", "стройка", "общестроительные"}:
        return deepcopy(ESTIMATE_CALCULATOR["suppliers"]["general_construction"])
    return deepcopy(ESTIMATE_CALCULATOR["suppliers"]["manual"])
# === END_UNIVERSAL_ESTIMATE_CALCULATOR_REGISTRY_V1 ===
