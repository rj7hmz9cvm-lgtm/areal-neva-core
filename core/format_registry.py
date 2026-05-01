# === UNIVERSAL_FORMAT_REGISTRY_V1 ===
# === DWG_DXF_KIND_FIX_V1 ===
from __future__ import annotations

import mimetypes
import os
from typing import Any, Dict

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff", ".bmp", ".gif"}
TABLE_EXT = {".xlsx", ".xls", ".xlsm", ".csv", ".ods", ".tsv"}
DOCUMENT_EXT = {".pdf", ".docx", ".doc", ".txt", ".md", ".rtf", ".odt", ".html", ".htm", ".xml", ".json", ".yaml", ".yml"}
DRAWING_EXT = {".dwg", ".dxf", ".ifc", ".rvt", ".rfa", ".skp", ".stl", ".obj", ".step", ".stp", ".iges", ".igs"}
PRESENTATION_EXT = {".ppt", ".pptx", ".odp", ".key"}
ARCHIVE_EXT = {".zip", ".7z", ".rar", ".tar", ".gz", ".tgz"}
MEDIA_EXT = {".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".m4a", ".ogg"}
KNOWN_EXT = IMAGE_EXT | TABLE_EXT | DOCUMENT_EXT | DRAWING_EXT | PRESENTATION_EXT | ARCHIVE_EXT | MEDIA_EXT

def extension(file_name: str = "") -> str:
    return os.path.splitext((file_name or "").lower())[1]

def classify_file(file_name: str = "", mime_type: str = "", user_text: str = "", topic_role: str = "") -> Dict[str, Any]:
    ext = extension(file_name)
    mime = (mime_type or mimetypes.guess_type(file_name or "")[0] or "").lower()
    hay = f"{file_name}\n{mime}\n{user_text}\n{topic_role}".lower()

    # drawing first: mimetypes may classify .dwg/.dxf as image/*
    if ext in DRAWING_EXT or any(x in mime for x in ("dwg", "dxf", "ifc", "revit", "cad", "step", "stp", "iges", "igs")):
        kind = "drawing"
    elif ext in IMAGE_EXT or mime.startswith("image/"):
        kind = "image"
    elif ext in TABLE_EXT or "spreadsheet" in mime or mime in ("text/csv", "application/vnd.ms-excel"):
        kind = "table"
    elif ext in DOCUMENT_EXT or mime in ("application/pdf", "text/plain", "application/msword") or "wordprocessingml" in mime:
        kind = "document"
    elif ext in PRESENTATION_EXT or "presentation" in mime:
        kind = "presentation"
    elif ext in ARCHIVE_EXT or "zip" in mime or "archive" in mime:
        kind = "archive"
    elif ext in MEDIA_EXT or mime.startswith("video/") or mime.startswith("audio/"):
        kind = "media"
    else:
        kind = "binary"

    if any(x in hay for x in ("смет", "расчёт", "расчет", "вор", "ведомость объем", "ведомость объём", "estimate")):
        domain = "estimate"
    elif any(x in hay for x in ("технадзор", "дефект", "акт", "осмотр", "нарушен", "гост", "снип", "сп ", "трещин", "протеч", "скол")):
        domain = "technadzor"
    elif any(x in hay for x in ("проект", "проектирован", "кж", "кмд", "км", "кр", "ар", "ов", "вк", "эом", "гп", "пз", "dwg", "dxf", "ifc", "чертеж", "чертёж")):
        domain = "project"
    else:
        domain = "general"

    return {
        "kind": kind,
        "domain": domain,
        "extension": ext,
        "mime_type": mime,
        "supported": ext in KNOWN_EXT or bool(mime),
        "engine_hint": {
            "image": "technadzor/photo",
            "table": "estimate/table",
            "drawing": "dwg_dxf/project",
            "document": "document/domain",
            "presentation": "universal",
            "archive": "universal",
            "media": "universal",
            "binary": "universal",
        }.get(kind, "universal"),
    }
# === END_DWG_DXF_KIND_FIX_V1 ===
# === END_UNIVERSAL_FORMAT_REGISTRY_V1 ===
