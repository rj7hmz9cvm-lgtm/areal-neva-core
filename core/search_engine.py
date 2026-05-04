# === FULLFIX_SEARCH_ENGINE_STAGE_5 ===
from __future__ import annotations
from typing import Any, Dict, List, Optional

SEARCH_ENGINE_VERSION = "SEARCH_ENGINE_V1"

DIRECTION_SEARCH_PROFILES = {
    "product_search":      {"sources": ["avito", "ozon", "wildberries"], "strategy": "price_compare"},
    "auto_parts_search":   {"sources": ["drom", "exist", "emex", "zzap"], "strategy": "compatibility"},
    "construction_search": {"sources": ["petrovitch", "lerua", "grand_line"], "strategy": "price_delivery"},
    "internet_search":     {"sources": ["web"], "strategy": "general"},
}

DEFAULT_PROFILE = {"sources": ["web"], "strategy": "general"}


class SearchEngine:
    def plan(self, work_item, payload: Dict[str, Any]) -> Dict[str, Any]:
        direction = getattr(work_item, "direction", None) or payload.get("direction") or "internet_search"
        raw_text = (getattr(work_item, "raw_text", "") or payload.get("raw_input") or "")[:500]
        profile = DIRECTION_SEARCH_PROFILES.get(direction, DEFAULT_PROFILE)

        plan = {
            "query": raw_text,
            "direction": direction,
            "sources": profile["sources"],
            "strategy": profile["strategy"],
            "engine_version": SEARCH_ENGINE_VERSION,
            "shadow_mode": True,
            "status": "planned",
        }
        return plan

    def apply_to_payload(self, work_item, payload: Dict[str, Any]) -> Dict[str, Any]:
        requires_search = bool((payload.get("direction_profile") or {}).get("requires_search"))
        if not requires_search:
            return {}
        plan = self.plan(work_item, payload)
        payload["search_plan"] = plan
        try:
            import logging
            logging.getLogger("task_worker").info(
                "FULLFIX_SEARCH_ENGINE_STAGE_5 dir=%s sources=%s strategy=%s",
                plan["direction"], plan["sources"], plan["strategy"]
            )
        except Exception:
            pass
        return plan


def plan_search(work_item, payload):
    return SearchEngine().apply_to_payload(work_item, payload)
# === END FULLFIX_SEARCH_ENGINE_STAGE_5 ===


# === P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1 ===
# Scope:
# - SearchEngine is no longer decorative shadow-only metadata
# - it produces normalized active search plan for product, auto parts, construction and general web search
# - no network call here; execution is handled by SearchMonolithV2 / ai_router online model

import re as _p6se_re

_P6SE_AUTO_WORDS = (
    "сайлентблок", "саленблок", "сальник", "пыльник", "ваз", "2110", "2114",
    "жигули", "лада", "приора", "гранта", "калина", "нива", "drom", "exist", "emex", "zzap",
    "автозапчаст", "запчаст", "oem", "артикул"
)

_P6SE_ELECTRONICS_WORDS = (
    "iphone", "айфон", "pixel", "google pixel", "телефон", "смартфон", "samsung", "galaxy",
    "xiaomi", "redmi", "honor", "huawei", "pro max", "xl"
)

_P6SE_BUILD_WORDS = (
    "утепл", "каменная вата", "rockwool", "бетон", "арматур", "профлист", "металлочереп",
    "фальц", "клик-фальц", "кирпич", "газобетон", "доска", "брус", "стройматериал"
)

def _p6se_s(v, limit=4000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6se_low(v):
    return _p6se_s(v).lower().replace("ё", "е")

def _p6se_direction(raw_text, current="internet_search"):
    low = _p6se_low(raw_text)
    if any(x in low for x in _P6SE_AUTO_WORDS):
        return "auto_parts_search"
    if any(x in low for x in _P6SE_ELECTRONICS_WORDS):
        return "product_search"
    if any(x in low for x in _P6SE_BUILD_WORDS):
        return "construction_search"
    return current or "internet_search"

def _p6se_sources(direction):
    if direction == "auto_parts_search":
        return ["zzap", "exist", "emex", "drom", "auto.ru", "euroauto", "avito", "telegram"]
    if direction == "construction_search":
        return ["petrovich", "lerua", "vseinstrumenti", "ozon", "wildberries", "yandex_market", "avito", "2gis", "supplier_sites"]
    if direction == "product_search":
        return ["ozon", "wildberries", "yandex_market", "dns", "mvideo", "eldorado", "avito", "aliexpress", "official_sites"]
    return ["web", "official_sites", "marketplaces", "classifieds", "2gis"]

def _p6se_strategy(direction):
    if direction == "auto_parts_search":
        return "compatibility_price_availability"
    if direction == "construction_search":
        return "price_delivery_supplier_trust"
    if direction == "product_search":
        return "price_compare_availability"
    return "general_verified_search"

try:
    _p6se_orig_plan = SearchEngine.plan
    def _p6se_plan(self, work_item, payload):
        payload = payload or {}
        raw_text = (
            getattr(work_item, "raw_text", None)
            or payload.get("raw_input")
            or payload.get("normalized_input")
            or payload.get("query")
            or ""
        )
        current = getattr(work_item, "direction", None) or payload.get("direction") or "internet_search"
        direction = _p6se_direction(raw_text, current)
        sources = _p6se_sources(direction)
        plan = {
            "query": _p6se_s(raw_text, 1000),
            "direction": direction,
            "sources": sources,
            "strategy": _p6se_strategy(direction),
            "engine_version": "P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1",
            "shadow_mode": False,
            "status": "active",
            "requires_online": True,
            "must_use_current_query_only": True,
        }
        return plan
    SearchEngine.plan = _p6se_plan

    def _p6se_apply_to_payload(self, work_item, payload):
        payload = payload or {}
        plan = self.plan(work_item, payload)
        payload["search_plan"] = plan
        payload["direction"] = plan["direction"]
        payload["engine"] = "search_supplier"
        payload["requires_search"] = True
        payload["search_sources"] = plan["sources"]
        payload["search_strategy"] = plan["strategy"]
        try:
            import logging
            logging.getLogger("task_worker").info(
                "P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN dir=%s sources=%s strategy=%s",
                plan["direction"], plan["sources"], plan["strategy"]
            )
        except Exception:
            pass
        return plan
    SearchEngine.apply_to_payload = _p6se_apply_to_payload
except Exception:
    pass

# === END_P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1 ===

# === P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1 ===
try:
    SEARCH_ENGINE_VERSION = "P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1"
    DIRECTION_SEARCH_PROFILES.update({
        "internet_search": {"sources": ["web", "marketplaces", "direct_suppliers"], "strategy": "current_query_price_compare"},
        "product_search": {"sources": ["ozon", "wildberries", "yandex_market", "avito", "direct_suppliers"], "strategy": "current_query_price_compare"},
        "auto_parts_search": {"sources": ["drom", "exist", "emex", "zzap", "avito"], "strategy": "current_query_compatibility_price"},
        "construction_search": {"sources": ["petrovich", "lemanapro", "vseinstrumenti", "direct_suppliers"], "strategy": "current_query_price_delivery"},
    })
except Exception:
    pass

try:
    _p6c_orig_plan_20260504 = SearchEngine.plan
    def _p6c_plan_20260504(self, work_item, payload):
        plan = _p6c_orig_plan_20260504(self, work_item, payload)
        plan["shadow_mode"] = False
        plan["status"] = "active"
        plan["engine_version"] = "P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1"
        return plan
    SearchEngine.plan = _p6c_plan_20260504
except Exception:
    pass
# === END_P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1 ===
