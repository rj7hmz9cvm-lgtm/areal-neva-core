import os
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=True)

def _oauth_service():
    client_id = os.getenv("GDRIVE_CLIENT_ID")
    client_secret = os.getenv("GDRIVE_CLIENT_SECRET")
    refresh_token = os.getenv("GDRIVE_REFRESH_TOKEN")
    if not client_id or not client_secret or not refresh_token:
        raise RuntimeError("GDRIVE OAuth vars missing")
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)

def _root_folder_id() -> str:
    folder_id = os.getenv("DRIVE_INGEST_FOLDER_ID", "").strip()
    if not folder_id:
        raise RuntimeError("DRIVE_INGEST_FOLDER_ID missing")
    return folder_id

def _find_child_folder(service, parent_id: str, name: str) -> Optional[str]:
    q = (
        f"name = '{name}' and "
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"'{parent_id}' in parents and trashed = false"
    )
    resp = service.files().list(
        q=q,
        spaces="drive",
        fields="files(id,name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = resp.get("files", [])
    return files[0]["id"] if files else None

def _ensure_folder(service, parent_id: str, name: str) -> str:
    found = _find_child_folder(service, parent_id, name)
    if found:
        return found
    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    res = service.files().create(
        body=meta,
        fields="id",
        supportsAllDrives=True,
    ).execute()
    return res["id"]

def _upload_file_sync(file_path: str, file_name: str, chat_id: str, topic_id: int, mime_type: Optional[str] = None) -> Dict[str, Any]:
    service = _oauth_service()
    root_id = _root_folder_id()
    chat_folder = _ensure_folder(service, root_id, f"chat_{chat_id}")
    topic_folder = _ensure_folder(service, chat_folder, f"topic_{int(topic_id or 0)}")
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    meta = {
        "name": file_name,
        "parents": [topic_folder],
    }
    res = service.files().create(
        body=meta,
        media_body=media,
        fields="id,parents",
        supportsAllDrives=True,
    ).execute()
    return {
        "ok": True,
        "drive_file_id": res.get("id"),
        "folder_id": topic_folder,
        "chat_folder_id": chat_folder,
    }

async def upload_file_to_topic(file_path: str, file_name: str, chat_id: str, topic_id: int, mime_type: Optional[str] = None) -> Dict[str, Any]:
    return await asyncio.to_thread(_upload_file_sync, file_path, file_name, str(chat_id), int(topic_id or 0), mime_type)
