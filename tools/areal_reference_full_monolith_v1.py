#!/usr/bin/env python3
# === AREAL_REFERENCE_FULL_MONOLITH_V1 ===
from __future__ import annotations

import io
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

BASE = Path("/root/.areal-neva-core")
CHAT_ID = "-1003725299009"
MAX_DOWNLOAD = 5 * 1024 * 1024

ROOTS = {
    "ESTIMATES_TEMPLATES": "19Z3acDgPub4nV55mad5mb8ju63FsqoG9",
    "TOPIC_210": "17QGniGggGgYEAD8lIyUK6TjgMIIDKhAq",
    "TOPIC_5": "1yWIJdSrypH3BbIozCz-OAw1R6hmnMRHK",
}

MEMORY_DB = BASE / "data" / "memory.db"
REGISTRY_PATH = BASE / "config" / "owner_reference_registry.json"
CANON_PATH = BASE / "docs" / "CANON_FINAL" / "OWNER_REFERENCE_FULL_WORKFLOW_CANON.md"
REPORT_PATH = BASE / "docs" / "REPORTS" / "AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT.md"
INDEX_PATH = BASE / "data" / "templates" / "reference_monolith" / "owner_reference_full_index.json"
VERSION = "AREAL_REFERENCE_FULL_MONOLITH_V1"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def s(v: Any) -> str:
    return "" if v is None else str(v)

def clean(v: Any, limit: int = 20000) -> str:
    return re.sub(r"\s+", " ", s(v)).strip()[:limit]

def env_load() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(str(BASE / ".env"), override=True)
    except Exception:
        pass

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

def drive_account(service) -> str:
    u = service.about().get(fields="user").execute().get("user", {})
    return s(u.get("emailAddress") or u.get("displayName") or "UNKNOWN")

def list_children(service, parent_id: str) -> List[Dict[str, Any]]:
    out = []
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

def list_recursive(service, parent_id: str, prefix: str) -> List[Dict[str, Any]]:
    out = []
    for f in list_children(service, parent_id):
        item = dict(f)
        item["_path"] = prefix + "/" + s(f.get("name"))
        out.append(item)
        if f.get("mimeType") == "application/vnd.google-apps.folder":
            out.extend(list_recursive(service, f["id"], item["_path"]))
    return out

def size_ok(meta: Dict[str, Any]) -> bool:
    try:
        size = int(meta.get("size") or 0)
        return size > 0 and size <= MAX_DOWNLOAD
    except Exception:
        return False

def download_bytes(service, meta: Dict[str, Any]) -> bytes:
    from googleapiclient.http import MediaIoBaseDownload
    fid = meta["id"]
    mime = s(meta.get("mimeType"))

    if mime == "application/vnd.google-apps.document":
        req = service.files().export_media(fileId=fid, mimeType="text/plain")
    elif mime == "application/vnd.google-apps.spreadsheet":
        req = service.files().export_media(fileId=fid, mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        req = service.files().get_media(fileId=fid, supportsAllDrives=True)

    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
        if buf.tell() > MAX_DOWNLOAD:
            raise RuntimeError("DOWNLOAD_LIMIT_5MB_EXCEEDED")
    return buf.getvalue()

def classify_domain(name: str, path: str, mime: str) -> str:
    low = f"{name} {path} {mime}".lower()
    if any(x in low for x in ["смет", "estimate", "расцен", "м-80", "м-110", "ареал нева", "фундамент_склад", "крыша и перекр"]):
        return "estimate"
    if any(x in low for x in ["технадзор", "дефект", "акт_", "акт ", "исполнительн"]):
        return "technadzor"
    if any(x in low for x in ["проект", "эскиз", "план участка", "посадк", ".dwg", ".dxf", ".ifc", ".pln", "архитект", "спецификац"]):
        return "design"
    if re.search(r"(^|[^а-яa-z0-9])(ар|кр|кж|кд|км|кмд|ов|вк|эо|эм|эос)([^а-яa-z0-9]|$)", low):
        return "design"
    if mime.startswith("image/"):
        return "design"
    return "other"

def discipline(name: str, path: str, mime: str) -> str:
    low = f"{name} {path}".lower()
    checks = [
        ("AR", ["ар", "архитект"]),
        ("KJ", ["кж", "железобет", "плита"]),
        ("KD", ["кд", "стропил", "дерев"]),
        ("KR", ["кр", "конструктив"]),
        ("KM", ["км", "металл"]),
        ("KMD", ["кмд"]),
        ("OV", ["ов", "отоп", "вентиляц"]),
        ("VK", ["вк", "водоснаб", "канализац"]),
        ("EO", ["эо", "эм", "эос", "электр"]),
        ("SPEC", ["спецификац", "ведом"]),
        ("SKETCH", ["эскиз", ".jpg", ".jpeg", ".png", ".webp"]),
        ("GP", ["план участка", "посадк", "генплан"]),
        ("PLN_MODEL", [".pln", "archicad"]),
        ("IFC_MODEL", [".ifc"]),
        ("CAD", [".dwg", ".dxf"]),
    ]
    for code, keys in checks:
        if any(k in low for k in keys):
            return code
    if mime.startswith("image/"):
        return "SKETCH"
    return "DESIGN"

def estimate_role(name: str, path: str) -> str:
    low = f"{name} {path}".lower()
    if "м-80" in low or "m-80" in low:
        return "m80"
    if "м-110" in low or "m-110" in low:
        return "m110"
    if "крыша" in low or "перекр" in low:
        return "roof_floor"
    if "фундамент" in low:
        return "foundation"
    if "ареал нева" in low:
        return "areal_neva"
    return "estimate_reference"

def analyze_xlsx(raw: bytes) -> Dict[str, Any]:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(raw), data_only=False, read_only=False)
    total = 0
    sheets = []
    for ws in wb.worksheets:
        fc = 0
        mat = 0
        work = 0
        logi = 0
        for row in ws.iter_rows():
            vals = []
            for c in row:
                if c.value is None:
                    continue
                val = str(c.value)
                vals.append(val)
                if val.startswith("="):
                    fc += 1
            rt = " ".join(vals).lower()
            if any(x in rt for x in ["материал", "бетон", "арматур", "газобетон", "кирпич", "доска", "кровл"]):
                mat += 1
            if any(x in rt for x in ["работ", "монтаж", "устройств", "кладк", "вязк"]):
                work += 1
            if any(x in rt for x in ["достав", "логист", "разгруз", "манипулятор", "кран", "транспорт", "прожив"]):
                logi += 1
        total += fc
        sheets.append({"sheet_name": ws.title, "formula_count": fc, "material_hits": mat, "work_hits": work, "logistics_hits": logi})
    return {"formula_total": total, "sheets": sheets}

def analyze_file(service, meta: Dict[str, Any]) -> Dict[str, Any]:
    name = s(meta.get("name"))
    path = s(meta.get("_path"))
    mime = s(meta.get("mimeType"))
    domain = classify_domain(name, path, mime)
    item = {
        "name": name,
        "file_id": s(meta.get("id")),
        "mimeType": mime,
        "path": path,
        "size": s(meta.get("size")),
        "modifiedTime": s(meta.get("modifiedTime")),
        "url": s(meta.get("webViewLink")),
        "domain": domain,
    }
    if meta.get("mimeType") == "application/vnd.google-apps.folder":
        item["domain"] = "folder"
        return item

    if domain == "estimate":
        item["role"] = estimate_role(name, path)
        item["formula_total"] = 0
        item["sheets"] = []
        if (
            name.lower().endswith((".xlsx", ".xlsm", ".xls"))
            or mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            or mime == "application/vnd.google-apps.spreadsheet"
        ):
            if mime == "application/vnd.google-apps.spreadsheet" or size_ok(meta):
                try:
                    item.update(analyze_xlsx(download_bytes(service, meta)))
                except Exception as e:
                    item["extract_error"] = clean(type(e).__name__ + ": " + str(e), 500)
            else:
                item["extract_skipped"] = "SIZE_LIMIT_5MB"
    elif domain == "design":
        item["discipline"] = discipline(name, path, mime)
    elif domain == "technadzor":
        item["role"] = "technadzor_reference"
    return item

def slim(policy: Dict[str, Any]) -> Dict[str, Any]:
    def slim_items(items):
        out = []
        for x in items:
            y = {k: v for k, v in x.items() if k not in {"text_preview", "sample_formulas"}}
            if "sheets" in y:
                y["sheets"] = [
                    {k: sh.get(k) for k in ("sheet_name", "formula_count", "material_hits", "work_hits", "logistics_hits")}
                    for sh in y.get("sheets", [])
                ]
            out.append(y)
        return out
    return {
        "version": policy["version"],
        "status": policy["status"],
        "updated_at": policy["updated_at"],
        "counts": policy["counts"],
        "estimate_references": slim_items(policy["estimate_references"][:40]),
        "design_references": slim_items(policy["design_references"][:80]),
        "technadzor_references": slim_items(policy["technadzor_references"][:40]),
    }

def save_memory(policy: Dict[str, Any]) -> None:
    val = json.dumps(slim(policy), ensure_ascii=False, indent=2)
    ts = now()
    rows = [
        ("owner_reference_full_workflow_v1", 0),
        ("topic_2_estimate_reference_v1", 2),
        ("topic_210_design_reference_v1", 210),
        ("topic_5_technadzor_reference_v1", 5),
    ]
    conn = sqlite3.connect(str(MEMORY_DB))
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(memory)").fetchall()]
        for key, topic_id in rows:
            rec = {
                "id": str(uuid.uuid4()),
                "chat_id": CHAT_ID,
                "key": key,
                "value": val,
                "timestamp": ts,
                "topic_id": topic_id,
                "scope": "topic",
            }
            use = [c for c in ["id", "chat_id", "key", "value", "timestamp", "topic_id", "scope"] if c in cols]
            conn.execute(
                f"INSERT INTO memory({','.join(use)}) VALUES ({','.join(['?'] * len(use))})",
                [rec[c] for c in use],
            )
        conn.commit()
    finally:
        conn.close()

def main() -> int:
    service = get_drive_service()
    account = drive_account(service)
    print("DRIVE_ACCOUNT", account)

    all_items = []
    for label, folder_id in ROOTS.items():
        meta = service.files().get(fileId=folder_id, fields="id,name,mimeType", supportsAllDrives=True).execute()
        print("ROOT_OK", label, meta.get("name"), folder_id)
        for f in list_recursive(service, folder_id, label):
            if f.get("mimeType") == "application/vnd.google-apps.folder":
                continue
            item = analyze_file(service, f)
            all_items.append(item)
            print("INDEXED", item.get("domain"), item.get("name"))

    estimates = [x for x in all_items if x.get("domain") == "estimate"]
    designs = [x for x in all_items if x.get("domain") == "design"]
    technadzor = [x for x in all_items if x.get("domain") == "technadzor"]
    formula_total = sum(int(x.get("formula_total") or 0) for x in estimates)

    counts = {
        "estimate_files": len(estimates),
        "design_files": len(designs),
        "technadzor_files": len(technadzor),
        "formula_total": formula_total,
        "all_files": len(all_items),
    }

    policy = {
        "version": VERSION,
        "status": "ACTIVE",
        "updated_at": now(),
        "drive_account": account,
        "counts": counts,
        "estimate_references": estimates,
        "design_references": designs,
        "technadzor_references": technadzor,
    }

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    old = {}
    if REGISTRY_PATH.exists():
        try:
            old = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            old = {}
    old["owner_reference_full_workflow_v1"] = policy
    old["active"] = VERSION
    old["topic_isolation"] = {"estimate": 2, "technadzor": 5, "design": 210}
    REGISTRY_PATH.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    CANON_PATH.parent.mkdir(parents=True, exist_ok=True)
    CANON_PATH.write_text(
        "# OWNER_REFERENCE_FULL_WORKFLOW_CANON\n\n"
        f"version: {VERSION}\n"
        f"updated_at: {policy['updated_at']}\n\n"
        "Илья — главный канон\n\n"
        "Сметы: М-80, М-110, крыша, фундамент, Ареал Нева — эталон формул и структуры\n\n"
        "Проектирование: АР, КР, КЖ, КД, КМ, КМД, ОВ, ВК, ЭО, ЭМ, ЭОС, эскизы, планы участка — разные разделы, не смешивать\n\n"
        "Технадзор: акты, дефекты, исполнительные — отдельный контур\n\n"
        "Если данных не хватает — один короткий вопрос\n\n"
        f"counts: {json.dumps(counts, ensure_ascii=False)}\n",
        encoding="utf-8",
    )

    save_memory(policy)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "# AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT\n\n"
        f"status: OK\nversion: {VERSION}\nupdated_at: {policy['updated_at']}\n"
        f"estimate_files: {counts['estimate_files']}\n"
        f"design_files: {counts['design_files']}\n"
        f"technadzor_files: {counts['technadzor_files']}\n"
        f"formula_total: {counts['formula_total']}\n",
        encoding="utf-8",
    )

    print("ESTIMATE_FILES", counts["estimate_files"])
    print("DESIGN_FILES", counts["design_files"])
    print("TECHNADZOR_FILES", counts["technadzor_files"])
    print("FORMULA_TOTAL", counts["formula_total"])

    if counts["estimate_files"] < 5:
        raise RuntimeError("ESTIMATE_FILES_LT_5")
    if counts["design_files"] < 10:
        raise RuntimeError("DESIGN_FILES_LT_10")
    if counts["formula_total"] < 3000:
        raise RuntimeError("FORMULA_TOTAL_LT_3000")

    print("AREAL_REFERENCE_FULL_MONOLITH_INDEX_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
# === END_AREAL_REFERENCE_FULL_MONOLITH_V1 ===
