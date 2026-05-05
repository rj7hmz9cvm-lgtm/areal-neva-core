# === PHOTO_RECOGNITION_SAFE_GUARD_V1 ===
"""
core/photo_recognition_engine.py

Fact-only photo recognition guard for topic_5 and topic_210.

Purpose:
- accept image/photo input as material
- create safe ObservationCard / ProjectImageCard data
- forbid invented visual defects when no owner-approved Vision provider is configured
- route norms through core.normative_engine only from source text / owner comment

This module does NOT perform external Vision by default.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


PHOTO_RECOGNITION_ENGINE_VERSION = "PHOTO_RECOGNITION_SAFE_GUARD_V1"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp", ".tif", ".tiff"}
TOPIC_TECHNADZOR = 5
TOPIC_PROJECT = 210


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _s(value: Any, limit: int = 4000) -> str:
    if value is None:
        return ""
    return str(value).strip()[:limit]


def is_image_file(file_name: str = "", file_path: str = "") -> bool:
    src = file_name or file_path or ""
    return Path(src).suffix.lower() in IMAGE_EXTENSIONS


def owner_approved_vision_enabled() -> bool:
    """
    Fact-only gate.

    Vision is disabled unless owner explicitly enables a provider through env.
    No provider name or model is invented here.
    """
    enabled = os.getenv("EXTERNAL_PHOTO_ANALYSIS_ALLOWED", "").strip().lower()
    provider = os.getenv("PHOTO_RECOGNITION_PROVIDER", "").strip()
    return enabled in {"1", "true", "yes", "on"} and bool(provider)


def vision_status() -> Dict[str, Any]:
    provider = os.getenv("PHOTO_RECOGNITION_PROVIDER", "").strip()
    return {
        "external_photo_analysis_allowed": owner_approved_vision_enabled(),
        "provider": provider or "NOT_CONFIGURED",
        "status": "VISION_READY" if owner_approved_vision_enabled() else "VISION_NOT_CONFIGURED",
    }


def search_norms_for_text(text: str, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        from core.normative_engine import search_norms_sync
        return search_norms_sync(text or "", limit=limit)
    except Exception:
        return []


@dataclass
class PhotoMaterialCard:
    schema: str
    engine: str
    topic_id: int
    source: str
    file_name: str
    file_path: str
    owner_comment: str
    added_at: str
    image_detected: bool
    vision_status: str
    include_in_report: bool
    include_in_act: bool
    status: str


@dataclass
class ObservationCard:
    schema: str
    engine: str
    topic_id: int
    object_role: str
    source: str
    author_role: str
    material_type: str
    file_name: str
    owner_comment: str
    claim: str
    confirmed_by_image: str
    contradiction: str
    needs_owner_question: bool
    norms: List[Dict[str, Any]]
    status: str


@dataclass
class DefectCard:
    schema: str
    engine: str
    topic_id: int
    file_name: str
    defect: str
    visible_basis: str
    normative_status: str
    norms: List[Dict[str, Any]]
    status: str


@dataclass
class ProjectImageCard:
    schema: str
    engine: str
    topic_id: int
    file_name: str
    project_context_hint: str
    owner_comment: str
    norms: List[Dict[str, Any]]
    status: str


def build_photo_material_card(
    topic_id: int,
    file_name: str = "",
    file_path: str = "",
    owner_comment: str = "",
    source: str = "TELEGRAM",
    include_in_report: bool = True,
    include_in_act: bool = True,
) -> Dict[str, Any]:
    image_detected = is_image_file(file_name=file_name, file_path=file_path)
    vstatus = vision_status()["status"]
    card = PhotoMaterialCard(
        schema="PhotoMaterialCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=int(topic_id or 0),
        source=_s(source, 64) or "TELEGRAM",
        file_name=_s(file_name, 512),
        file_path=_s(file_path, 2000),
        owner_comment=_s(owner_comment),
        added_at=_now_iso(),
        image_detected=image_detected,
        vision_status=vstatus,
        include_in_report=bool(include_in_report),
        include_in_act=bool(include_in_act),
        status="PHOTO_MATERIAL_ACCEPTED" if image_detected else "NOT_IMAGE_FILE",
    )
    return asdict(card)


def build_topic5_observation_card(
    file_name: str = "",
    file_path: str = "",
    owner_comment: str = "",
    source: str = "TELEGRAM",
) -> Dict[str, Any]:
    norms = search_norms_for_text(owner_comment, limit=5)
    vision_ready = owner_approved_vision_enabled()
    claim = _s(owner_comment) if owner_comment else "UNKNOWN"
    card = ObservationCard(
        schema="ObservationCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=TOPIC_TECHNADZOR,
        object_role="TECHNADZOR_VISIT_MATERIAL",
        source=_s(source, 64) or "TELEGRAM",
        author_role="OWNER" if owner_comment else "UNKNOWN",
        material_type="PHOTO" if is_image_file(file_name, file_path) else "OTHER",
        file_name=_s(file_name, 512),
        owner_comment=_s(owner_comment),
        claim=claim,
        confirmed_by_image="NOT_CHECKED_BY_VISION" if not vision_ready else "VISION_PROVIDER_REQUIRED_RUNTIME_CHECK",
        contradiction="UNKNOWN",
        needs_owner_question=False if owner_comment else True,
        norms=norms,
        status="OBSERVATION_FROM_OWNER_COMMENT_ONLY" if not vision_ready else "VISION_READY_NOT_EXECUTED_HERE",
    )
    return asdict(card)


def build_topic5_defect_card(
    file_name: str = "",
    owner_comment: str = "",
) -> Dict[str, Any]:
    norms = search_norms_for_text(owner_comment, limit=5)
    if not owner_comment:
        defect = "UNKNOWN"
        status = "NO_DEFECT_WITHOUT_OWNER_COMMENT_OR_VISION"
    else:
        defect = _s(owner_comment)
        status = "DEFECT_FROM_OWNER_COMMENT_NOT_IMAGE_RECOGNITION"
    card = DefectCard(
        schema="DefectCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=TOPIC_TECHNADZOR,
        file_name=_s(file_name, 512),
        defect=defect,
        visible_basis="NOT_ANALYZED_BY_VISION",
        normative_status="NORM_FOUND" if norms else "NORM_NOT_CONFIRMED",
        norms=norms,
        status=status,
    )
    return asdict(card)


def build_topic210_project_image_card(
    file_name: str = "",
    owner_comment: str = "",
    project_context_hint: str = "",
) -> Dict[str, Any]:
    combined = " ".join(x for x in [owner_comment, project_context_hint, file_name] if x)
    norms = search_norms_for_text(combined, limit=5)
    card = ProjectImageCard(
        schema="ProjectImageCardV1",
        engine=PHOTO_RECOGNITION_ENGINE_VERSION,
        topic_id=TOPIC_PROJECT,
        file_name=_s(file_name, 512),
        project_context_hint=_s(project_context_hint, 1000) or "UNKNOWN",
        owner_comment=_s(owner_comment),
        norms=norms,
        status="PROJECT_IMAGE_MATERIAL_ACCEPTED_NO_VISION_ANALYSIS" if not owner_approved_vision_enabled() else "VISION_READY_NOT_EXECUTED_HERE",
    )
    return asdict(card)


def process_photo_recognition(
    topic_id: int,
    file_name: str = "",
    file_path: str = "",
    owner_comment: str = "",
    source: str = "TELEGRAM",
    project_context_hint: str = "",
) -> Dict[str, Any]:
    """
    Safe entry point.

    topic_5:
      returns PhotoMaterialCard + ObservationCard + DefectCard guard.
    topic_210:
      returns PhotoMaterialCard + ProjectImageCard guard.

    No visual defect recognition is performed unless a future owner-approved
    provider is explicitly wired and tested outside this guard.
    """
    topic = int(topic_id or 0)
    material = build_photo_material_card(topic, file_name, file_path, owner_comment, source)
    result: Dict[str, Any] = {
        "ok": True,
        "engine": PHOTO_RECOGNITION_ENGINE_VERSION,
        "topic_id": topic,
        "vision": vision_status(),
        "material": material,
        "status": "PHOTO_RECOGNITION_GUARDED_NO_VISION",
    }
    if topic == TOPIC_TECHNADZOR:
        result["observation_card"] = build_topic5_observation_card(file_name, file_path, owner_comment, source)
        result["defect_card"] = build_topic5_defect_card(file_name, owner_comment)
    elif topic == TOPIC_PROJECT:
        result["project_image_card"] = build_topic210_project_image_card(file_name, owner_comment, project_context_hint)
    else:
        result["status"] = "PHOTO_MATERIAL_ACCEPTED_UNROUTED_TOPIC"
    return result


__all__ = [
    "PHOTO_RECOGNITION_ENGINE_VERSION",
    "is_image_file",
    "owner_approved_vision_enabled",
    "vision_status",
    "build_photo_material_card",
    "build_topic5_observation_card",
    "build_topic5_defect_card",
    "build_topic210_project_image_card",
    "process_photo_recognition",
]
# === END_PHOTO_RECOGNITION_SAFE_GUARD_V1 ===
