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
