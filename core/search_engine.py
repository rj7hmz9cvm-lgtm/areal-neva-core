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
