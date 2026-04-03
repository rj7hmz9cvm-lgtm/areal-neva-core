import io
import os
from typing import Optional

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

BASE_DIR = "/root/.areal-neva-core"
load_dotenv(f"{BASE_DIR}/.env")
load_dotenv(f"{BASE_DIR}/secrets.env", override=False)

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = os.getenv("GDRIVE_SERVICE_ACCOUNT_FILE", f"{BASE_DIR}/credentials.json").strip()
ROOT_FOLDER_ID = (
    os.getenv("GDRIVE_ROOT_ID")
    or os.getenv("GOOGLE_DRIVE_ROOT_ID")
    or os.getenv("DRIVE_ROOT_FOLDER_ID")
    or os.getenv("ROOT_FOLDER_ID")
    or os.getenv("GDRIVE_FOLDER_ID")
    or os.getenv("AI_ORCHESTRA_FOLDER_ID")
    or ""
).strip()

_drive = None

def _get_drive():
    global _drive
    if _drive is not None:
        return _drive

    if not ROOT_FOLDER_ID:
        raise RuntimeError("GDRIVE_ROOT_ID is empty")

    if not SERVICE_ACCOUNT_FILE or not os.path.isfile(SERVICE_ACCOUNT_FILE):
        raise RuntimeError(f"GDrive service account file not found: {SERVICE_ACCOUNT_FILE}")

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    _drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    return _drive

def upload_bytes(file_bytes: bytes, filename: str, mime_type: str = "application/octet-stream") -> str:
    drive = _get_drive()

    file_metadata = {
        "name": filename,
        "parents": [ROOT_FOLDER_ID],
    }

    media = MediaIoBaseUpload(
        io.BytesIO(file_bytes),
        mimetype=mime_type,
        resumable=True,
    )

    file = drive.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    file_id = file.get("id", "").strip()
    if not file_id:
        raise RuntimeError("Google Drive returned empty file id")

    return file_id

def upload_text(text: str, filename: str) -> str:
    return upload_bytes(
        text.encode("utf-8"),
        filename,
        "text/plain"
    )
