# === P6H_TOPIC5_TECHNADZOR_TEMPLATE_PHOTO_CLIENT_SAFE_CLOSE_20260504 / DRIVE_INDEX_V1 ===
# Auto-discovery of topic_5 (technadzor) Drive folder contents as style/content
# references — without manual "прими как образец" commands.
#
# Layered classification (file role):
#   PRIMARY_PDF_STYLE         — PDF in topic root or in non-system subfolders (real client acts; main style)
#   SECONDARY_DOCX_REFERENCE  — DOCX in service subfolders (TECHNADZOR / _drafts / _system / _templates)
#   CLIENT_PHOTO_SOURCE       — image/* in topic root or any non-system folder (work-object photos)
#   CLIENT_FINAL_PDF          — PDF artifacts produced earlier (kept in client folders)
#   SYSTEM_TEMPLATE           — DOCX/JSON/manifests in service subfolders
#   OTHER                     — anything else (audio, etc.)
#
# Folder classification:
#   SYSTEM   — name in {_system, _templates, _drafts, _manifests, _archive, _tmp, TECHNADZOR}
#   CLIENT   — anything else (work-object/customer-facing folders)
#
# Index is persisted to:
#   data/templates/technadzor/ACTIVE__chat_<chat_id>__topic_<topic_id>.json
# (filename uses literal chat_id with leading dash, matching existing convention)
#
# In-memory cache TTL = 5 minutes.
from __future__ import annotations

import io
import json
import os
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("task_worker")

_CACHE_TTL_SECONDS = 300
_CACHE: Dict[Tuple[str, int], Tuple[float, Dict[str, Any]]] = {}

_BASE = Path(__file__).resolve().parent.parent
_LOCAL_INDEX_DIR = _BASE / "data" / "templates" / "technadzor"
_LOCAL_INDEX_DIR.mkdir(parents=True, exist_ok=True)
_DOWNLOAD_DIR = _BASE / "data" / "memory_files" / "technadzor_index_cache"
_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Folder names treated as SYSTEM (no client artifacts allowed)
SYSTEM_FOLDER_NAMES = {
    "_system", "_templates", "_drafts", "_manifests", "_archive", "_tmp",
    "technadzor",  # case-insensitive match against TECHNADZOR
}


def is_system_folder(name: str) -> bool:
    """True if the folder is internal/service. Match case-insensitive."""
    if not name:
        return False
    return name.strip().lower() in SYSTEM_FOLDER_NAMES


def is_client_facing_folder(name: str) -> bool:
    """True if the folder is client-facing (object/customer/visit folder)."""
    if not name:
        return False
    return not is_system_folder(name)


def _service():
    from core.topic_drive_oauth import _oauth_service
    return _oauth_service()


def _root_folder_id() -> str:
    from core.topic_drive_oauth import _root_folder_id as r
    return r()


def _find_child(svc, parent_id: str, name: str) -> Optional[str]:
    safe_name = name.replace("'", "\\'")
    res = svc.files().list(
        q=f"'{parent_id}' in parents and name='{safe_name}' and trashed=false",
        fields="files(id,name,mimeType)",
        pageSize=10,
    ).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def _ensure_subfolder(svc, parent_id: str, name: str) -> str:
    fid = _find_child(svc, parent_id, name)
    if fid:
        return fid
    body = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    created = svc.files().create(body=body, fields="id").execute()
    return created["id"]


def _list_folder(svc, folder_id: str, page_size: int = 200) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    page_token = None
    while True:
        res = svc.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id,name,mimeType,modifiedTime,createdTime,size,webViewLink,parents)",
            orderBy="modifiedTime desc",
            pageSize=page_size,
            pageToken=page_token,
        ).execute()
        items.extend(res.get("files", []))
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return items


def classify_technadzor_drive_file(file: Dict[str, Any], parent_folder_name: str = "") -> str:
    """Classify a Drive file by role (returns one of the role strings)."""
    mt = file.get("mimeType", "") or ""
    name = (file.get("name") or "").lower()
    parent = (parent_folder_name or "").strip().lower()
    parent_is_system = parent in SYSTEM_FOLDER_NAMES

    # PDF
    if mt == "application/pdf":
        if parent_is_system:
            return "SYSTEM_TEMPLATE"
        if name.startswith("act") or "акт" in name or "осмотр" in name:
            # PDF in non-system folder with act-like name → primary style
            return "PRIMARY_PDF_STYLE"
        # PDF in client folder, generic — most likely a final client PDF artifact
        return "CLIENT_FINAL_PDF"

    # DOCX
    if mt == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        if parent_is_system:
            return "SYSTEM_TEMPLATE"
        return "SECONDARY_DOCX_REFERENCE"

    # Image
    if mt.startswith("image/"):
        if parent_is_system:
            return "SYSTEM_TEMPLATE"
        return "CLIENT_PHOTO_SOURCE"

    # JSON / manifests / system
    if mt in ("application/json",) or name.endswith((".json", ".log", ".bak", ".tmp")):
        return "SYSTEM_TEMPLATE"

    # Audio (voice notes)
    if mt.startswith("audio/") or mt == "application/ogg":
        return "OTHER"

    return "OTHER"


def _resolve_topic_folder(svc, chat_id: str, topic_id: int) -> Optional[str]:
    root = _root_folder_id()
    chat_folder = _find_child(svc, root, f"chat_{chat_id}")
    if not chat_folder:
        return None
    return _find_child(svc, chat_folder, f"topic_{int(topic_id)}")


def _local_index_path(chat_id: str, topic_id: int) -> Path:
    fname = f"ACTIVE__chat_{chat_id}__topic_{int(topic_id)}.json"
    return _LOCAL_INDEX_DIR / fname


def _drive_url(file: Dict[str, Any]) -> str:
    fid = file.get("id", "")
    if file.get("webViewLink"):
        return file["webViewLink"]
    if file.get("mimeType") == "application/vnd.google-apps.folder":
        return f"https://drive.google.com/drive/folders/{fid}"
    return f"https://drive.google.com/file/d/{fid}/view"


def scan_topic5_drive_templates(chat_id: str, topic_id: int = 5, force: bool = False) -> Dict[str, Any]:
    """Scan Drive topic_<id> contents and return classified listing.

    Cached for 5 min. Pass force=True to refresh.
    """
    key = (str(chat_id), int(topic_id))
    now = time.time()
    if not force and key in _CACHE:
        ts, cached = _CACHE[key]
        if now - ts < _CACHE_TTL_SECONDS:
            return cached

    svc = _service()
    topic_fid = _resolve_topic_folder(svc, chat_id, topic_id)
    result: Dict[str, Any] = {
        "chat_id": str(chat_id),
        "topic_id": int(topic_id),
        "topic_folder_id": topic_fid,
        "topic_folder_link": (
            f"https://drive.google.com/drive/folders/{topic_fid}"
            if topic_fid else None
        ),
        "files": [],
        "folders_system": [],
        "folders_client": [],
        "by_role": {},
        "primary_pdf_style": [],
        "secondary_docx_reference": [],
        "client_photo_source": [],
        "client_final_pdf": [],
        "system_template": [],
        "other": [],
        "ok": False,
        "error": None,
        "scanned_at": int(now),
    }

    if not topic_fid:
        result["error"] = f"topic folder chat_{chat_id}/topic_{topic_id} not found"
        _CACHE[key] = (now, result)
        return result

    try:
        # Walk topic root
        root_items = _list_folder(svc, topic_fid)
        all_records: List[Dict[str, Any]] = []
        sub_folder_walk: List[Tuple[str, str]] = []  # (folder_id, folder_name)
        for it in root_items:
            if it.get("mimeType") == "application/vnd.google-apps.folder":
                if is_system_folder(it["name"]):
                    result["folders_system"].append({
                        "id": it["id"], "name": it["name"],
                        "drive_url": _drive_url(it),
                    })
                else:
                    result["folders_client"].append({
                        "id": it["id"], "name": it["name"],
                        "drive_url": _drive_url(it),
                    })
                sub_folder_walk.append((it["id"], it["name"]))
            else:
                role = classify_technadzor_drive_file(it, parent_folder_name="")
                rec = _build_record(it, role, parent_folder_name="", chat_id=chat_id, topic_id=topic_id)
                all_records.append(rec)

        # Walk one level of subfolders (do not recurse deeper to keep it cheap)
        for sub_fid, sub_name in sub_folder_walk:
            sub_items = _list_folder(svc, sub_fid)
            for it in sub_items:
                if it.get("mimeType") == "application/vnd.google-apps.folder":
                    # nested sub-subfolder — record name only, do not recurse
                    continue
                role = classify_technadzor_drive_file(it, parent_folder_name=sub_name)
                rec = _build_record(it, role, parent_folder_name=sub_name, chat_id=chat_id, topic_id=topic_id)
                all_records.append(rec)

        result["files"] = all_records
        for rec in all_records:
            role = rec["role"]
            bucket = role.lower()
            if bucket == "primary_pdf_style":
                result["primary_pdf_style"].append(rec)
            elif bucket == "secondary_docx_reference":
                result["secondary_docx_reference"].append(rec)
            elif bucket == "client_photo_source":
                result["client_photo_source"].append(rec)
            elif bucket == "client_final_pdf":
                result["client_final_pdf"].append(rec)
            elif bucket == "system_template":
                result["system_template"].append(rec)
            else:
                result["other"].append(rec)
            result["by_role"].setdefault(role, 0)
            result["by_role"][role] += 1

        result["ok"] = True
    except Exception as exc:
        result["error"] = repr(exc)
        LOG.exception("P6H_TOPIC5_DRIVE_INDEX_SCAN_FAIL chat=%s topic=%s", chat_id, topic_id)

    _CACHE[key] = (now, result)
    return result


def _build_record(file: Dict[str, Any], role: str, parent_folder_name: str, chat_id: str, topic_id: int) -> Dict[str, Any]:
    parent_lower = (parent_folder_name or "").strip().lower()
    parent_is_system = parent_lower in SYSTEM_FOLDER_NAMES
    return {
        "file_id": file.get("id"),
        "file_name": file.get("name"),
        "mime_type": file.get("mimeType"),
        "drive_url": _drive_url(file),
        "folder_name": parent_folder_name or "<root>",
        "role": role,
        "client_facing": (not parent_is_system),
        "created_time": file.get("createdTime"),
        "modified_time": file.get("modifiedTime"),
        "size": file.get("size"),
    }


def build_technadzor_template_index(chat_id: str = "-1003725299009", topic_id: int = 5, force: bool = True) -> Dict[str, Any]:
    """Build full topic_5 index, persist to local JSON, return the index dict.

    Persistent path:
        data/templates/technadzor/ACTIVE__chat_<chat_id>__topic_<topic_id>.json
    """
    idx = scan_topic5_drive_templates(chat_id, topic_id, force=force)
    payload = {
        "chat_id": idx.get("chat_id"),
        "topic_id": idx.get("topic_id"),
        "topic_folder_id": idx.get("topic_folder_id"),
        "topic_folder_link": idx.get("topic_folder_link"),
        "scanned_at": idx.get("scanned_at"),
        "ok": idx.get("ok"),
        "error": idx.get("error"),
        "by_role": idx.get("by_role"),
        "folders_system": idx.get("folders_system"),
        "folders_client": idx.get("folders_client"),
        "files": idx.get("files"),
        "primary_pdf_style": idx.get("primary_pdf_style"),
        "secondary_docx_reference": idx.get("secondary_docx_reference"),
        "client_photo_source": idx.get("client_photo_source"),
        "client_final_pdf": idx.get("client_final_pdf"),
        "system_template": idx.get("system_template"),
        "other": idx.get("other"),
        "marker": "P6H_TOPIC5_USE_EXISTING_TEMPLATES_PHOTO_TO_TECH_REPORT_20260504_V1",
        "updated_at": int(time.time()),
    }
    try:
        path = _local_index_path(str(chat_id), int(topic_id))
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        payload["local_index_path"] = str(path)
    except Exception as exc:
        LOG.exception("P6H_TOPIC5_DRIVE_INDEX_PERSIST_FAIL chat=%s topic=%s err=%s", chat_id, topic_id, exc)
    return payload


def get_active_index(chat_id: str = "-1003725299009", topic_id: int = 5) -> Optional[Dict[str, Any]]:
    """Read persisted index from disk, if present."""
    p = _local_index_path(str(chat_id), int(topic_id))
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def primary_template_meta(idx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Most recent PRIMARY_PDF_STYLE record. Falls back to most recent CLIENT_FINAL_PDF."""
    if idx.get("primary_pdf_style"):
        return idx["primary_pdf_style"][0]
    if idx.get("client_final_pdf"):
        return idx["client_final_pdf"][0]
    return None


def secondary_template_meta(idx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if idx.get("secondary_docx_reference"):
        return idx["secondary_docx_reference"][0]
    return None


def ensure_service_subfolder(chat_id: str, topic_id: int, name: str = "_drafts") -> Optional[str]:
    """Create/return id for a SERVICE subfolder (system, never client-facing).

    Refuses to create folders with non-system names.
    """
    if not is_system_folder(name):
        raise ValueError(f"Refusing to create non-system folder via service path: {name}")
    svc = _service()
    topic_fid = _resolve_topic_folder(svc, chat_id, topic_id)
    if not topic_fid:
        return None
    return _ensure_subfolder(svc, topic_fid, name)


def upload_to_service_subfolder(local_path: Path, dst_name: str, chat_id: str, topic_id: int, subfolder: str = "_drafts") -> Optional[Dict[str, Any]]:
    """Upload artifact to topic_<id>/<service-subfolder>/. Subfolder MUST be system."""
    if not is_system_folder(subfolder):
        raise ValueError(f"Refusing to upload to non-system subfolder: {subfolder}")
    return _upload_to_folder(local_path, dst_name, chat_id, topic_id, subfolder, allow_client=False)


def upload_client_pdf_to_folder(local_path: Path, dst_name: str, chat_id: str, topic_id: int, target_folder_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Upload final client PDF.

    If target_folder_name is provided AND it's a non-system (client-facing) folder,
    upload there. Otherwise upload to topic root.

    Refuses anything that isn't .pdf — by spec, client folders accept only photos and final PDFs.
    """
    if not str(local_path).lower().endswith(".pdf"):
        raise ValueError(f"Refusing to upload non-PDF to client folder: {local_path}")
    return _upload_to_folder(local_path, dst_name, chat_id, topic_id, target_folder_name, allow_client=True)


def _upload_to_folder(local_path: Path, dst_name: str, chat_id: str, topic_id: int, target_folder_name: Optional[str], allow_client: bool) -> Optional[Dict[str, Any]]:
    try:
        from googleapiclient.http import MediaFileUpload
        svc = _service()
        topic_fid = _resolve_topic_folder(svc, chat_id, topic_id)
        if not topic_fid:
            return None

        if target_folder_name:
            if is_system_folder(target_folder_name):
                target_id = _ensure_subfolder(svc, topic_fid, target_folder_name)
            else:
                if not allow_client:
                    raise ValueError(f"Client folder upload not allowed via service path: {target_folder_name}")
                # find existing client folder, do NOT auto-create client folders
                target_id = _find_child(svc, topic_fid, target_folder_name)
                if not target_id:
                    LOG.warning("P6H_TOPIC5_CLIENT_FOLDER_NOT_FOUND name=%s — uploading to topic root", target_folder_name)
                    target_id = topic_fid
        else:
            target_id = topic_fid

        body = {"name": dst_name, "parents": [target_id]}
        mime = None
        ln = str(local_path).lower()
        if ln.endswith(".docx"):
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ln.endswith(".pdf"):
            mime = "application/pdf"
        elif ln.endswith(".xlsx"):
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif ln.endswith(".json"):
            mime = "application/json"
        media = MediaFileUpload(str(local_path), mimetype=mime, resumable=False)
        created = svc.files().create(body=body, media_body=media, fields="id,webViewLink,parents").execute()
        return {"id": created["id"], "link": created.get("webViewLink"), "parent_id": target_id, "target_folder_name": target_folder_name}
    except Exception:
        LOG.exception("P6H_TOPIC5_DRIVE_UPLOAD_FAIL name=%s topic=%s sub=%s", dst_name, topic_id, target_folder_name)
        return None


def download_to_local(file_id: str, dst_filename: str) -> Optional[Path]:
    """Download a Drive file to local cache. Returns path or None."""
    try:
        from googleapiclient.http import MediaIoBaseDownload
        svc = _service()
        dst = _DOWNLOAD_DIR / dst_filename
        req = svc.files().get_media(fileId=file_id)
        with io.FileIO(dst, "wb") as buf:
            dl = MediaIoBaseDownload(buf, req)
            done = False
            while not done:
                _, done = dl.next_chunk()
        return dst
    except Exception:
        LOG.exception("P6H_TOPIC5_DRIVE_INDEX_DOWNLOAD_FAIL fid=%s", file_id)
        return None


try:
    LOG.info("P6H_TOPIC5_DRIVE_INDEX_V1_INSTALLED")
except Exception:
    pass
# === END_P6H_TOPIC5_DRIVE_INDEX_V1 ===
