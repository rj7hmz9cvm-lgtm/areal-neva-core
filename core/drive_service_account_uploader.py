
import os
import json
import mimetypes
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=True)
logger = logging.getLogger(__name__)

SERVICE_ACCOUNT_EMAIL = "ai-orchestra@areal-neva-automation.iam.gserviceaccount.com"
DEFAULT_FOLDER_ID = os.getenv("DRIVE_INGEST_FOLDER_ID") or os.getenv("AI_ORCHESTRA_FOLDER_ID") or "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"

def _candidate_credentials():
    env = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or os.getenv("SERVICE_ACCOUNT_FILE")
    names = [
        env,
        f"{BASE}/service_account.json",
        f"{BASE}/credentials_service_account.json",
        f"{BASE}/google_service_account.json",
        f"{BASE}/ai-orchestra-service-account.json",
        f"{BASE}/credentials.json",
    ]
    out = []
    for n in names:
        if n and n not in out and Path(n).exists():
            out.append(n)
    return out

def _is_service_account(path: str) -> bool:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data.get("type") == "service_account" and data.get("client_email") == SERVICE_ACCOUNT_EMAIL
    except Exception:
        return False

def get_service_account_credentials_path() -> Optional[str]:
    for p in _candidate_credentials():
        if _is_service_account(p):
            return p
    return None

def upload_artifact_service_account(file_path: str, name: Optional[str] = None, folder_id: Optional[str] = None) -> Optional[str]:
    file_path = str(file_path)
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    cred_path = get_service_account_credentials_path()
    if not cred_path:
        raise RuntimeError("SERVICE_ACCOUNT_CREDENTIALS_NOT_FOUND_OR_WRONG_EMAIL")

    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)
    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    fname = name or os.path.basename(file_path)
    mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    target_folder = folder_id or DEFAULT_FOLDER_ID

    metadata = {"name": fname}
    if target_folder:
        metadata["parents"] = [target_folder]

    media = MediaFileUpload(file_path, mimetype=mime, resumable=True)
    created = service.files().create(
        body=metadata,
        media_body=media,
        fields="id,webViewLink",
        supportsAllDrives=True,
    ).execute()

    fid = created.get("id")
    if not fid:
        raise RuntimeError("DRIVE_UPLOAD_NO_FILE_ID")

    return created.get("webViewLink") or f"https://drive.google.com/file/d/{fid}/view"

def healthcheck() -> dict:
    cred_path = get_service_account_credentials_path()
    if not cred_path:
        return {"ok": False, "error": "SERVICE_ACCOUNT_CREDENTIALS_NOT_FOUND_OR_WRONG_EMAIL"}

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        creds = service_account.Credentials.from_service_account_file(
            cred_path,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        service = build("drive", "v3", credentials=creds, cache_discovery=False)
        about = service.about().get(fields="user,storageQuota").execute()
        return {
            "ok": True,
            "email": SERVICE_ACCOUNT_EMAIL,
            "credentials": cred_path,
            "folder_id": DEFAULT_FOLDER_ID,
            "about": about,
        }
    except Exception as e:
        return {"ok": False, "error": repr(e), "credentials": cred_path, "folder_id": DEFAULT_FOLDER_ID}
