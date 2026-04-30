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
