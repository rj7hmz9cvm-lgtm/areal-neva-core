# === GOOGLE_SHEETS_NATIVE_EXPORT_V1 ===
from __future__ import annotations
import logging
import os
import re
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

def _safe_title(title: str) -> str:
    t = re.sub(r"[\r\n\t]+", " ", str(title or "Estimate")).strip()
    return re.sub(r"[\\/]+", "_", t)[:90] or "Estimate"

def _creds():
    from dotenv import load_dotenv
    load_dotenv("/root/.areal-neva-core/.env", override=False)
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials(
        None,
        refresh_token=os.environ["GDRIVE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GDRIVE_CLIENT_ID"],
        client_secret=os.environ["GDRIVE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/spreadsheets"],
    )
    creds.refresh(Request())
    return creds

def create_google_sheet(title: str, rows: List[List[Any]], topic_id: int = 0, task_id: str = "") -> Optional[str]:
    try:
        from googleapiclient.discovery import build
        creds = _creds()
        drive = build("drive", "v3", credentials=creds, cache_discovery=False)
        sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
        sheet = sheets.spreadsheets().create(
            body={"properties": {"title": _safe_title(title)}, "sheets": [{"properties": {"title": "Смета"}}]},
            fields="spreadsheetId,spreadsheetUrl",
        ).execute()
        sid = sheet.get("spreadsheetId")
        if not sid:
            return None
        values = [["" if v is None else v for v in (row if isinstance(row, list) else [row])] for row in (rows or [])][:5000]
        if values:
            sheets.spreadsheets().values().update(
                spreadsheetId=sid, range="Смета!A1",
                valueInputOption="USER_ENTERED", body={"values": values},
            ).execute()
        try:
            from core.engine_base import get_drive_topic_folder_id
            folder_id = get_drive_topic_folder_id(int(topic_id or 0))
            if folder_id:
                meta = drive.files().get(fileId=sid, fields="parents").execute()
                old = ",".join(meta.get("parents") or [])
                drive.files().update(fileId=sid, addParents=folder_id, removeParents=old, fields="id").execute()
        except Exception as me:
            logger.warning("SHEETS_MOVE_ERR task=%s err=%s", task_id, me)
        try:
            drive.permissions().create(fileId=sid, body={"role": "reader", "type": "anyone"}, fields="id").execute()
        except Exception:
            pass
        link = drive.files().get(fileId=sid, fields="webViewLink").execute().get("webViewLink") \
               or f"https://docs.google.com/spreadsheets/d/{sid}/edit"
        logger.info("GOOGLE_SHEETS_NATIVE_EXPORT_V1_OK task=%s link=%s", task_id, link)
        return link
    except Exception as e:
        logger.warning("GOOGLE_SHEETS_NATIVE_EXPORT_V1_ERR task=%s err=%s", task_id, e)
        return None
# === END_GOOGLE_SHEETS_NATIVE_EXPORT_V1 ===
