import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger("drive_folder_resolver")

SERVICE_ACCOUNT_FILE = "/root/.areal-neva-core/credentials.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]  # SCOPE_FULL_V2
SHARED_DRIVE_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
CHAT_ID = "-1003725299009"

def get_or_create_topic_folder(topic_id: int) -> str:
    """Возвращает ID папки для топика. Создаёт, если не существует."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)

    folder_name = f"chat_{CHAT_ID}_topic_{topic_id}"

    # Ищем существующую папку
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    response = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        driveId=SHARED_DRIVE_ID,
        corpora="drive"
    ).execute()

    files = response.get("files", [])
    if files:
        folder_id = files[0]["id"]
        logger.info(f"Папка топика {topic_id} найдена: {folder_id}")
        return folder_id

    # Создаём новую папку в Shared Drive
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "driveId": SHARED_DRIVE_ID,
        "parents": [SHARED_DRIVE_ID]
    }
    folder = service.files().create(
        body=file_metadata,
        fields="id",
        supportsAllDrives=True
    ).execute()

    folder_id = folder["id"]
    logger.info(f"Папка топика {topic_id} создана: {folder_id}")
    return folder_id
