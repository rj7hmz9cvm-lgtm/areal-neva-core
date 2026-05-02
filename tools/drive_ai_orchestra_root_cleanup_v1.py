#!/usr/bin/env python3
# === DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1 ===
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

BASE = Path("/root/.areal-neva-core")
ROOT_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
CHAT_FOLDER_NAME = "chat_-1003725299009"
CHAT_ID = "-1003725299009"
TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
REPORT_PATH = BASE / "docs" / "REPORTS" / "DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1_REPORT.md"

CANON_ROOT_FOLDERS = {
    "chat_-1003725299009",
    "ESTIMATES",
    "CANON_FINAL",
    "telegram_exports",
    "CHAT_EXPORTS",
    "_QUARANTINE_ROOT_CLEANUP",
    "AI_ORCHESTRA",
}

TMP_RE = re.compile(r"^tmp[a-z0-9_ -]*\.txt$", re.I)

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def s(v: Any) -> str:
    return "" if v is None else str(v)

def low(v: Any) -> str:
    return s(v).lower().strip()

def env_load() -> None:
    env_path = BASE / ".env"
    try:
        from dotenv import load_dotenv
        load_dotenv(str(env_path), override=True)
        return
    except Exception:
        pass

    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def get_drive_service():
    env_load()

    cid = os.getenv("GDRIVE_CLIENT_ID", "").strip()
    sec = os.getenv("GDRIVE_CLIENT_SECRET", "").strip()
    ref = os.getenv("GDRIVE_REFRESH_TOKEN", "").strip()

    if cid and sec and ref:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = Credentials(
            None,
            refresh_token=ref,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cid,
            client_secret=sec,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        creds.refresh(Request())
        return build("drive", "v3", credentials=creds)

    sys.path.insert(0, str(BASE))
    import google_io
    return google_io.get_drive_service()

def q_escape(name: str) -> str:
    return name.replace("\\", "\\\\").replace("'", "\\'")

def list_children(service, parent_id: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    token = None
    while True:
        res = service.files().list(
            q=f"'{parent_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,modifiedTime,size,webViewLink,parents),nextPageToken",
            pageSize=1000,
            pageToken=token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        out.extend(res.get("files", []))
        token = res.get("nextPageToken")
        if not token:
            break
    return out

def find_child_folder(service, parent_id: str, name: str) -> str | None:
    res = service.files().list(
        q=f"'{parent_id}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder' and name='{q_escape(name)}'",
        fields="files(id,name,mimeType,parents)",
        pageSize=20,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None

def ensure_folder(service, parent_id: str, name: str) -> str:
    existing = find_child_folder(service, parent_id, name)
    if existing:
        return existing

    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    created = service.files().create(
        body=meta,
        fields="id,name,parents",
        supportsAllDrives=True,
    ).execute()
    return created["id"]

def drive_about(service) -> str:
    about = service.about().get(fields="user").execute()
    user = about.get("user", {}) or {}
    return s(user.get("emailAddress") or user.get("displayName") or "UNKNOWN")

def parents(f: Dict[str, Any]) -> List[str]:
    return list(f.get("parents") or [])

def move_file(service, f: Dict[str, Any], target_id: str, target_path: str, moves: List[Dict[str, Any]]) -> None:
    fid = f["id"]
    current = parents(f)

    if target_id in current and ROOT_ID not in current:
        return

    remove_parents = ",".join([p for p in current if p == ROOT_ID])
    add_parents = target_id if target_id not in current else ""

    if not remove_parents and not add_parents:
        return

    kwargs = {
        "fileId": fid,
        "fields": "id,name,parents",
        "supportsAllDrives": True,
    }
    if add_parents:
        kwargs["addParents"] = add_parents
    if remove_parents:
        kwargs["removeParents"] = remove_parents

    service.files().update(**kwargs).execute()

    moves.append({
        "file_id": fid,
        "name": f.get("name"),
        "mimeType": f.get("mimeType"),
        "target": target_path,
    })

def classify_target(f: Dict[str, Any], folders: Dict[str, str]) -> Tuple[str, str]:
    name = s(f.get("name"))
    n = low(name)
    mime = s(f.get("mimeType"))
    is_folder = mime == "application/vnd.google-apps.folder"

    if is_folder and name in CANON_ROOT_FOLDERS:
        return "SKIP_CANON_ROOT_FOLDER", ""

    if is_folder and name == "Образцы смет и проектов":
        return folders["design_references"], "chat_-1003725299009/topic_210/PROJECT_DESIGN_REFERENCES"

    if TMP_RE.match(name) or n.startswith("tmp"):
        return folders["quarantine_tmp"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/tmp_txt"

    if n in {"upload_many_compat_v2.txt"} or "compat" in n:
        return folders["quarantine_service"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/service_tmp"

    if "chat_export" in n or "chat export" in n:
        return folders["telegram_exports_root_imports"], "telegram_exports/_ROOT_IMPORTS"

    if n.endswith(".manifest.json") or mime == "application/json":
        if n.startswith("estimate_"):
            return folders["estimate_manifests"], "ESTIMATES/generated/_manifests"
        if "кж_compact_project" in n or "project" in n or "кж" in n:
            return folders["project_manifests"], "chat_-1003725299009/topic_210/PROJECT_ARTIFACTS/_manifests"
        return folders["quarantine_manifests"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/manifests"

    if name in {"М-80.xlsx", "M-80.xlsx", "М-110.xlsx", "M-110.xlsx", "крыша и перекр.xlsx", "фундамент_Склад2.xlsx", "Ареал Нева.xlsx"}:
        return folders["estimate_templates"], "ESTIMATES/templates"

    if n.startswith("estimate_") or "смет" in n:
        if n.endswith(".xlsx") or "spreadsheet" in mime:
            return folders["estimate_generated"], "ESTIMATES/generated"
        if n.endswith(".pdf"):
            return folders["estimate_generated_pdf"], "ESTIMATES/generated/pdf"
        return folders["estimate_generated"], "ESTIMATES/generated"

    if n.startswith("act_") or "акт" in n or "дефект" in n or "технадзор" in n:
        return folders["technadzor"], "chat_-1003725299009/topic_5/TECHNADZOR"

    if (
        "кж_compact_project" in n
        or "проект" in n
        or "project" in n
        or re.search(r"(^|[^а-яa-z])(ар|кр|кж|кд)([^а-яa-z]|$)", n)
        or n.endswith((".dwg", ".dxf", ".pln"))
    ):
        return folders["project_artifacts"], "chat_-1003725299009/topic_210/PROJECT_ARTIFACTS"

    if n.endswith((".docx", ".doc", ".pdf", ".xlsx", ".xls", ".csv", ".txt", ".zip", ".rar", ".7z")):
        return folders["quarantine_unknown_files"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/unknown_files"

    if is_folder:
        return folders["quarantine_unknown_folders"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/unknown_folders"

    return folders["quarantine_unknown_files"], f"_QUARANTINE_ROOT_CLEANUP/{TS}/unknown_files"

def main() -> int:
    service = get_drive_service()
    account = drive_about(service)
    print("DRIVE_ACCOUNT", account)

    root_meta = service.files().get(
        fileId=ROOT_ID,
        fields="id,name,mimeType,trashed,webViewLink",
        supportsAllDrives=True,
    ).execute()
    print("ROOT_OK", root_meta.get("name"), root_meta.get("id"))

    chat = ensure_folder(service, ROOT_ID, CHAT_FOLDER_NAME)
    topic_0 = ensure_folder(service, chat, "topic_0")
    topic_2 = ensure_folder(service, chat, "topic_2")
    topic_5 = ensure_folder(service, chat, "topic_5")
    topic_210 = ensure_folder(service, chat, "topic_210")

    estimates = ensure_folder(service, ROOT_ID, "ESTIMATES")
    canon_final = ensure_folder(service, ROOT_ID, "CANON_FINAL")
    telegram_exports = ensure_folder(service, ROOT_ID, "telegram_exports")
    quarantine = ensure_folder(service, ROOT_ID, "_QUARANTINE_ROOT_CLEANUP")
    quarantine_ts = ensure_folder(service, quarantine, TS)

    folders = {
        "topic_0": topic_0,
        "topic_2": topic_2,
        "topic_5": topic_5,
        "topic_210": topic_210,
        "estimates": estimates,
        "canon_final": canon_final,
        "telegram_exports": telegram_exports,

        "estimate_templates": ensure_folder(service, estimates, "templates"),
        "estimate_generated": ensure_folder(service, estimates, "generated"),
        "estimate_generated_pdf": ensure_folder(service, ensure_folder(service, estimates, "generated"), "pdf"),
        "estimate_manifests": ensure_folder(service, ensure_folder(service, estimates, "generated"), "_manifests"),

        "design_references": ensure_folder(service, topic_210, "PROJECT_DESIGN_REFERENCES"),
        "project_artifacts": ensure_folder(service, topic_210, "PROJECT_ARTIFACTS"),
        "project_manifests": ensure_folder(service, ensure_folder(service, topic_210, "PROJECT_ARTIFACTS"), "_manifests"),

        "technadzor": ensure_folder(service, topic_5, "TECHNADZOR"),

        "telegram_exports_root_imports": ensure_folder(service, telegram_exports, "_ROOT_IMPORTS"),

        "quarantine_tmp": ensure_folder(service, quarantine_ts, "tmp_txt"),
        "quarantine_service": ensure_folder(service, quarantine_ts, "service_tmp"),
        "quarantine_manifests": ensure_folder(service, quarantine_ts, "manifests"),
        "quarantine_unknown_files": ensure_folder(service, quarantine_ts, "unknown_files"),
        "quarantine_unknown_folders": ensure_folder(service, quarantine_ts, "unknown_folders"),
    }

    before = list_children(service, ROOT_ID)
    root_files_before = [x for x in before if x.get("mimeType") != "application/vnd.google-apps.folder"]
    print("ROOT_CHILDREN_BEFORE", len(before))
    print("ROOT_FILES_BEFORE", len(root_files_before))

    moves: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []

    for f in before:
        name = s(f.get("name"))
        target_id, target_path = classify_target(f, folders)

        if target_id == "SKIP_CANON_ROOT_FOLDER":
            skipped.append({"name": name, "reason": "canonical_root_folder"})
            continue

        if not target_id:
            skipped.append({"name": name, "reason": "no_target"})
            continue

        move_file(service, f, target_id, target_path, moves)

    after = list_children(service, ROOT_ID)
    root_files_after = [x for x in after if x.get("mimeType") != "application/vnd.google-apps.folder"]
    noncanonical_root = [
        x for x in after
        if x.get("mimeType") != "application/vnd.google-apps.folder"
        or x.get("name") not in {
            CHAT_FOLDER_NAME,
            "ESTIMATES",
            "CANON_FINAL",
            "telegram_exports",
            "CHAT_EXPORTS",
            "_QUARANTINE_ROOT_CLEANUP",
        }
    ]

    print("ROOT_CHILDREN_AFTER", len(after))
    print("ROOT_FILES_AFTER", len(root_files_after))
    print("MOVED_COUNT", len(moves))
    print("SKIPPED_COUNT", len(skipped))
    print("NONCANONICAL_ROOT_COUNT", len(noncanonical_root))

    for m in moves[:300]:
        print("MOVED", m["name"], "=>", m["target"])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1_REPORT")
    lines.append("")
    lines.append("status: OK")
    lines.append("timestamp: " + now())
    lines.append("drive_account: " + account)
    lines.append("root_id: " + ROOT_ID)
    lines.append("")
    lines.append("## COUNTS")
    lines.append(f"- root_children_before: {len(before)}")
    lines.append(f"- root_files_before: {len(root_files_before)}")
    lines.append(f"- moved_count: {len(moves)}")
    lines.append(f"- skipped_count: {len(skipped)}")
    lines.append(f"- root_children_after: {len(after)}")
    lines.append(f"- root_files_after: {len(root_files_after)}")
    lines.append(f"- noncanonical_root_count: {len(noncanonical_root)}")
    lines.append("")
    lines.append("## CANONICAL FOLDERS")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_0")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_2")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_5")
    lines.append("- AI_ORCHESTRA/chat_-1003725299009/topic_210")
    lines.append("- AI_ORCHESTRA/ESTIMATES")
    lines.append("- AI_ORCHESTRA/CANON_FINAL")
    lines.append("- AI_ORCHESTRA/telegram_exports")
    lines.append("- AI_ORCHESTRA/_QUARANTINE_ROOT_CLEANUP")
    lines.append("")
    lines.append("## MOVES")
    for m in moves:
        lines.append(f"- `{m['name']}` -> `{m['target']}`")
    lines.append("")
    lines.append("## SKIPPED")
    for s0 in skipped:
        lines.append(f"- `{s0['name']}`: {s0['reason']}")
    lines.append("")
    lines.append("## NONCANONICAL_ROOT_AFTER")
    for x in noncanonical_root[:200]:
        lines.append(f"- `{x.get('name')}` | `{x.get('mimeType')}` | `{x.get('id')}`")
    lines.append("")
    lines.append("## RAW_JSON")
    lines.append("```json")
    lines.append(json.dumps({
        "status": "OK",
        "timestamp": now(),
        "drive_account": account,
        "root_id": ROOT_ID,
        "counts": {
            "root_children_before": len(before),
            "root_files_before": len(root_files_before),
            "moved_count": len(moves),
            "skipped_count": len(skipped),
            "root_children_after": len(after),
            "root_files_after": len(root_files_after),
            "noncanonical_root_count": len(noncanonical_root),
        },
        "moves": moves,
        "skipped": skipped,
        "noncanonical_root_after": [
            {"id": x.get("id"), "name": x.get("name"), "mimeType": x.get("mimeType")}
            for x in noncanonical_root[:500]
        ],
    }, ensure_ascii=False, indent=2))
    lines.append("```")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if len(root_files_after) > 0:
        print("ROOT_FILES_REMAIN_AFTER_CLEANUP")
        for x in root_files_after[:100]:
            print("ROOT_FILE_LEFT", x.get("name"), x.get("mimeType"), x.get("id"))

    print("REPORT_OK", REPORT_PATH)
    print("DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
# === END_DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1 ===
