import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

CREDS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/root/.areal-neva-core/credentials.json")
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

GOOGLE_EXPORT_MAP = {
    "application/vnd.google-apps.spreadsheet": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xlsx",
    ),
    "application/vnd.google-apps.document": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".docx",
    ),
}


class GoogleIO:
    def __init__(self, creds_path: Optional[str] = None):
        self.creds_path = creds_path or CREDS_PATH
        if not os.path.exists(self.creds_path):
            raise FileNotFoundError(f"credentials not found: {self.creds_path}")

        self.creds = service_account.Credentials.from_service_account_file(
            self.creds_path,
            scopes=SCOPES,
        )
        self.drive = build("drive", "v3", credentials=self.creds, cache_discovery=False)
        self.gs = gspread.authorize(self.creds)

    @staticmethod
    def _escape_q(value: str) -> str:
        return (value or "").replace("\\", "\\\\").replace("'", "\\'")

    @staticmethod
    def _normalize_df(df: pd.DataFrame) -> List[List[Any]]:
        safe = df.copy().astype(object)
        for col in safe.columns:
            safe[col] = safe[col].map(
                lambda x: ""
                if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x)))
                else x
            )
        return [safe.columns.tolist()] + safe.values.tolist()

    def search_file(
        self,
        name: str,
        folder_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        exact: bool = True,
    ) -> List[Dict[str, Any]]:
        esc_name = self._escape_q(name)
        q = f"name = '{esc_name}' and trashed = false" if exact else f"name contains '{esc_name}' and trashed = false"
        if folder_id:
            q += f" and '{folder_id}' in parents"
        if mime_type:
            q += f" and mimeType = '{self._escape_q(mime_type)}'"

        res = self.drive.files().list(
            q=q,
            fields="files(id,name,mimeType,webViewLink,parents,modifiedTime)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        return res.get("files", [])

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        return self.drive.files().get(
            fileId=file_id,
            fields="id,name,mimeType,webViewLink,parents,modifiedTime,size",
            supportsAllDrives=True,
        ).execute()

    def download_file(self, file_id: str, local_path: str) -> str:
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)

        meta = self.get_file_metadata(file_id)
        mime_type = meta.get("mimeType", "")

        if mime_type in GOOGLE_EXPORT_MAP:
            export_mime, _ = GOOGLE_EXPORT_MAP[mime_type]
            request = self.drive.files().export_media(
                fileId=file_id,
                mimeType=export_mime,
            )
        else:
            request = self.drive.files().get_media(
                fileId=file_id,
                supportsAllDrives=True,
            )

        with open(local_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        return local_path

    def upload_file(
        self,
        local_path: str,
        name: Optional[str] = None,
        folder_id: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not os.path.exists(local_path):
            raise FileNotFoundError(local_path)

        body: Dict[str, Any] = {"name": name or Path(local_path).name}
        if folder_id:
            body["parents"] = [folder_id]

        media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)

        return self.drive.files().create(
            body=body,
            media_body=media,
            fields="id,name,mimeType,webViewLink,parents",
            supportsAllDrives=True,
        ).execute()

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            body["parents"] = [parent_id]

        return self.drive.files().create(
            body=body,
            fields="id,name,webViewLink,parents",
            supportsAllDrives=True,
        ).execute()

    def ensure_folder(self, name: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        found = self.search_file(
            name=name,
            folder_id=parent_id,
            mime_type="application/vnd.google-apps.folder",
            exact=True,
        )
        if found:
            return found[0]
        return self.create_folder(name, parent_id)

    def create_sheet(self, title: str, folder_id: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "name": title,
            "mimeType": "application/vnd.google-apps.spreadsheet",
        }
        if folder_id:
            body["parents"] = [folder_id]

        return self.drive.files().create(
            body=body,
            fields="id,name,mimeType,webViewLink,parents",
            supportsAllDrives=True,
        ).execute()

    def open_sheet(self, sheet_id: str):
        return self.gs.open_by_key(sheet_id)

    def _get_worksheet(self, sheet_id: str, worksheet_name: Optional[str] = None):
        sh = self.open_sheet(sheet_id)
        if worksheet_name:
            try:
                return sh.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                pass
        return sh.get_worksheet(0)

    def read_sheet_to_df(self, sheet_id: str, worksheet_name: Optional[str] = None) -> pd.DataFrame:
        ws = self._get_worksheet(sheet_id, worksheet_name)
        rows = ws.get_all_records()
        return pd.DataFrame(rows)

    def write_df_to_sheet(
        self,
        sheet_id: str,
        df: pd.DataFrame,
        worksheet_name: str = "Data",
        clear_first: bool = True,
    ) -> Dict[str, Any]:
        sh = self.open_sheet(sheet_id)

        try:
            ws = sh.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            rows = max(len(df) + 10, 100)
            cols = max(len(df.columns) + 5, 20)
            ws = sh.add_worksheet(title=worksheet_name, rows=str(rows), cols=str(cols))

        if clear_first:
            ws.clear()

        values = self._normalize_df(df)
        ws.update("A1", values, value_input_option="USER_ENTERED")

        return {
            "sheet_id": sheet_id,
            "worksheet": worksheet_name,
            "rows": len(df),
            "cols": len(df.columns),
        }


if __name__ == "__main__":
    GoogleIO()
    print("GOOGLE_IO_READY")
