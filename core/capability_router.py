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
