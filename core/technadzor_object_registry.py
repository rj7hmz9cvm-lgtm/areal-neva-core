# === P6H_TOPIC5_OBJECT_REGISTRY_INSPECTION_CHAIN_20260504 ===
# Object registry + inspection chain for topic_5 / Технадзор.
#
# Storage layers (system-only, never client-facing):
#   1) server JSON: data/templates/technadzor/objects/<object_id>.json
#   2) memory.db key: topic_5_technadzor_object_<object_id>
#   3) timeline:    data/memory_files/chat_<chat_id>/topic_5/timeline.jsonl
#   4) Drive (best-effort): topic_5/_system/object_registry/<object_id>.json
#
# A card has:
#   object_id, object_name, client_name, object_folder_url,
#   client_facing_folder_url, service_folder_url,
#   inspection_chain[], previous_acts[],
#   current_open_items[], closed_items[], unresolved_items[],
#   recommendations[], last_visit_date, last_act_no, last_pdf_link,
#   created_at, updated_at
#
# Inspection record:
#   act_no, date, mode (initial|repeat|extension|description_only),
#   pdf_link, docx_link, source_photo_folder,
#   findings[], open_items[], closed_items[], new_items[],
#   owner_observation, conflict_flags
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("task_worker")

_BASE = Path(__file__).resolve().parent.parent
_REGISTRY_DIR = _BASE / "data" / "templates" / "technadzor" / "objects"
_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

_TIMELINE_BASE = _BASE / "data" / "memory_files"

_FOLLOW_UP_INDICATORS = (
    "та же папка", "тот же объект", "то же место", "сегодняшний выезд",
    "повторн", "продолжен", "доделай по", "прошлый раз", "ранее", "вчера",
    "та же стройка", "тот же ангар", "следующий выезд", "очередной выезд",
)

_NEW_OBJECT_INDICATORS = (
    "новый объект", "другой объект", "новая стройка", "новый ангар",
    "новая площадка", "новый адрес",
)


def _slug(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"[^a-zа-я0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:60]


def _card_path(object_id: str) -> Path:
    return _REGISTRY_DIR / f"{_slug(object_id)}.json"


def list_object_ids() -> List[str]:
    return sorted(p.stem for p in _REGISTRY_DIR.glob("*.json"))


def list_object_summaries() -> List[Dict[str, Any]]:
    summaries = []
    for p in _REGISTRY_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            summaries.append({
                "object_id": data.get("object_id") or p.stem,
                "object_name": data.get("object_name", ""),
                "client_name": data.get("client_name", ""),
                "last_visit_date": data.get("last_visit_date", ""),
                "last_act_no": data.get("last_act_no", ""),
                "inspection_count": len(data.get("inspection_chain") or []),
            })
        except Exception:
            pass
    return summaries


def load_object(object_id: str) -> Optional[Dict[str, Any]]:
    p = _card_path(object_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        LOG.exception("P6H_REG_LOAD_FAIL %s", object_id)
        return None


def _new_card(object_id: str, **fields) -> Dict[str, Any]:
    now = int(time.time())
    base = {
        "object_id": object_id,
        "object_name": "",
        "client_name": "",
        "object_folder_url": "",
        "client_facing_folder_url": "",
        "service_folder_url": "",
        "inspection_chain": [],
        "previous_acts": [],
        "current_open_items": [],
        "closed_items": [],
        "unresolved_items": [],
        "recommendations": [],
        "last_visit_date": "",
        "last_act_no": "",
        "last_pdf_link": "",
        "created_at": now,
        "updated_at": now,
    }
    for k, v in (fields or {}).items():
        if k in base and v:
            base[k] = v
    return base


def save_object(card: Dict[str, Any]) -> Optional[Path]:
    if not card or not card.get("object_id"):
        return None
    card["updated_at"] = int(time.time())
    p = _card_path(card["object_id"])
    try:
        p.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
        _persist_to_memory(card)
        _append_timeline(card.get("chat_id", ""), card)
        return p
    except Exception:
        LOG.exception("P6H_REG_SAVE_FAIL %s", card.get("object_id"))
        return None


def _persist_to_memory(card: Dict[str, Any]) -> None:
    try:
        from core.memory_client import save_memory  # type: ignore
        chat_id = str(card.get("chat_id") or "")
        oid = card.get("object_id", "")
        body = json.dumps(card, ensure_ascii=False)[:8000]
        save_memory(chat_id=chat_id, key=f"topic_5_technadzor_object_{oid}", value=body)
    except Exception:
        # silent — server JSON is the canonical store
        pass


def _append_timeline(chat_id: str, card: Dict[str, Any]) -> None:
    if not chat_id:
        return
    try:
        d = _TIMELINE_BASE / f"chat_{chat_id}" / "topic_5"
        d.mkdir(parents=True, exist_ok=True)
        line = json.dumps({
            "ts": int(time.time()),
            "kind": "technadzor_object_update",
            "object_id": card.get("object_id"),
            "object_name": card.get("object_name", ""),
            "last_act_no": card.get("last_act_no", ""),
            "last_visit_date": card.get("last_visit_date", ""),
            "inspection_count": len(card.get("inspection_chain") or []),
        }, ensure_ascii=False)
        with (d / "timeline.jsonl").open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def derive_object_id_from_context(
    voice_ctx: Optional[Dict[str, Any]],
    drive_idx: Optional[Dict[str, Any]],
    file_path: str = "",
    file_name: str = "",
) -> Tuple[str, Dict[str, str]]:
    """Try to derive a stable object_id from available signals.

    Returns (object_id, source_dict) where source_dict explains what was used.
    Empty object_id means we cannot derive — caller must ask owner.
    """
    sources: Dict[str, str] = {}
    candidates: List[str] = []

    if voice_ctx:
        fh = (voice_ctx.get("folder_hint") or "").strip()
        if fh:
            candidates.append(fh)
            sources["folder_hint"] = fh
        oh = (voice_ctx.get("object_hint") or "").strip()
        if oh and not candidates:
            candidates.append(oh)
            sources["object_hint"] = oh

    # Drive: client-folder match by file path or by recent client folders
    if drive_idx:
        for f in drive_idx.get("folders_client", []) or []:
            name = f.get("name") or ""
            if name and name not in candidates:
                # Use the most recently modified client folder as a fallback hint only
                candidates.append(name)
                sources.setdefault("drive_client_folder", name)
                break

    # File name pattern (e.g., "kievskoe_08_04_26_act.pdf")
    if file_name and not candidates:
        candidates.append(file_name.rsplit(".", 1)[0])
        sources["file_name"] = file_name

    if not candidates:
        return ("", sources)
    return (_slug(candidates[0]), sources)


def detect_visit_mode(card: Optional[Dict[str, Any]], voice_ctx: Optional[Dict[str, Any]]) -> str:
    """Returns one of: initial | repeat | extension | description_only.

    Decision:
      • card is None or empty inspection_chain → initial
      • voice transcript explicitly says повторный/продолжение → repeat
      • else if chain non-empty → repeat (default for known object)
      • else → initial
    """
    transcript = ((voice_ctx or {}).get("transcript") or "").lower()
    if any(t in transcript for t in _NEW_OBJECT_INDICATORS):
        return "initial"
    has_history = bool(card and (card.get("inspection_chain") or []))
    if not has_history:
        return "initial"
    if any(t in transcript for t in _FOLLOW_UP_INDICATORS):
        return "repeat"
    if "дополнен" in transcript or "приложен" in transcript:
        return "extension"
    if (voice_ctx or {}).get("output_kind") == "description":
        return "description_only"
    return "repeat"


def carry_forward_open_items(card: Optional[Dict[str, Any]], current_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """For follow-up acts: take prior open_items and assign status based on
    whether similar findings exist in current_findings.

    Status set:
      УСТРАНЕНО, УСТРАНЕНО ЧАСТИЧНО, НЕ УСТРАНЕНО,
      ТРЕБУЕТ ДОВЕДЕНИЯ, НЕ ПРОВЕРЯЛОСЬ, ТРЕБУЕТ УТОЧНЕНИЯ
    """
    if not card:
        return []
    prior = card.get("current_open_items") or []
    if not prior:
        return []

    def _norm(s: str) -> str:
        return re.sub(r"\s+", " ", (s or "").lower()).strip()

    cur_blobs = [_norm((d.get("title") or "") + " " + (d.get("description") or "")) for d in current_findings or []]

    out: List[Dict[str, Any]] = []
    for it in prior:
        prior_blob = _norm((it.get("title") or "") + " " + (it.get("description") or "") + " " + (it.get("section") or ""))
        # naive match: any token of length >= 5 from prior present in current
        tokens = [t for t in re.findall(r"\w+", prior_blob) if len(t) >= 5]
        match = False
        partial = False
        for cb in cur_blobs:
            present = sum(1 for t in tokens if t in cb)
            if present >= max(2, len(tokens) // 3):
                match = True
                if present < max(3, len(tokens) // 2):
                    partial = True
                break
        if match and not partial:
            status = "НЕ УСТРАНЕНО"
        elif match and partial:
            status = "УСТРАНЕНО ЧАСТИЧНО"
        else:
            status = "ТРЕБУЕТ УТОЧНЕНИЯ"
        out.append({
            "title": it.get("title", ""),
            "description": it.get("description", ""),
            "section": it.get("section", ""),
            "status": status,
            "from_act_no": it.get("act_no", ""),
        })
    return out


def detect_voice_vision_conflict(voice_ctx: Optional[Dict[str, Any]], grouped_sections: List[Tuple[str, List[Dict[str, Any]]]]) -> List[str]:
    """Returns a list of human-readable conflict markers.

    Conflict cases:
      • voice mentions sections that Vision didn't pick up
      • voice explicitly excludes section that Vision flagged
    """
    if not voice_ctx or not (voice_ctx.get("transcript") or ""):
        return []
    transcript = (voice_ctx.get("transcript") or "").lower()
    flags: List[str] = []

    # Use the same section keywords as the engine
    try:
        from core.technadzor_engine import _P6H_SECTIONS  # type: ignore
    except Exception:
        return []

    voice_mentioned: List[str] = []
    for sec_title, kws in _P6H_SECTIONS:
        for kw in kws:
            if kw in transcript:
                voice_mentioned.append(sec_title)
                break

    vision_sections = [s[0] for s in (grouped_sections or [])]
    for vm in voice_mentioned:
        if vm not in vision_sections:
            flags.append(
                f"По голосовому ТЗ упомянуто «{vm}», но по фото Vision этого не подтвердил — уточни, что включать в акт"
            )
    excludes = " ".join(voice_ctx.get("explicit_exclude") or [])
    for vs in vision_sections:
        for kw_pair in _P6H_SECTIONS:
            if kw_pair[0] != vs:
                continue
            if any(kw in excludes.lower() for kw in kw_pair[1]):
                flags.append(
                    f"Vision выделил «{vs}», но владелец голосом просил это не включать — уточни"
                )
            break
    return flags[:6]


def record_inspection(
    object_id: str,
    chat_id: str,
    *,
    act_no: str = "",
    date_str: str = "",
    mode: str = "initial",
    pdf_link: str = "",
    docx_link: str = "",
    source_photo_folder: str = "",
    findings: Optional[List[Dict[str, Any]]] = None,
    open_items: Optional[List[Dict[str, Any]]] = None,
    closed_items: Optional[List[Dict[str, Any]]] = None,
    new_items: Optional[List[Dict[str, Any]]] = None,
    owner_observation: str = "",
    conflict_flags: Optional[List[str]] = None,
    object_name: str = "",
    client_name: str = "",
    object_folder_url: str = "",
    client_facing_folder_url: str = "",
    service_folder_url: str = "",
) -> Dict[str, Any]:
    """Append an inspection record to object's chain. Creates card if missing."""
    card = load_object(object_id) or _new_card(object_id)
    card["chat_id"] = str(chat_id)
    if object_name:
        card["object_name"] = object_name
    if client_name and not card.get("client_name"):
        card["client_name"] = client_name
    if object_folder_url:
        card["object_folder_url"] = object_folder_url
    if client_facing_folder_url:
        card["client_facing_folder_url"] = client_facing_folder_url
    if service_folder_url:
        card["service_folder_url"] = service_folder_url

    record = {
        "act_no": act_no or "",
        "date": date_str or "",
        "mode": mode or "initial",
        "pdf_link": pdf_link or "",
        "docx_link": docx_link or "",
        "source_photo_folder": source_photo_folder or "",
        "findings": findings or [],
        "open_items": open_items or [],
        "closed_items": closed_items or [],
        "new_items": new_items or [],
        "owner_observation": owner_observation or "",
        "conflict_flags": conflict_flags or [],
        "ts": int(time.time()),
    }
    card["inspection_chain"].append(record)
    if act_no:
        card["last_act_no"] = act_no
    if date_str:
        card["last_visit_date"] = date_str
    if pdf_link:
        card["last_pdf_link"] = pdf_link
        card["previous_acts"].append({
            "act_no": act_no, "date": date_str,
            "pdf_link": pdf_link, "docx_link": docx_link,
        })
    if open_items is not None:
        card["current_open_items"] = list(open_items)
    if closed_items:
        card["closed_items"] = (card.get("closed_items") or []) + list(closed_items)
    save_object(card)
    return card


try:
    LOG.info("P6H_TOPIC5_OBJECT_REGISTRY_INSPECTION_CHAIN_20260504_INSTALLED")
except Exception:
    pass
# === END_P6H_TOPIC5_OBJECT_REGISTRY_INSPECTION_CHAIN_20260504 ===
