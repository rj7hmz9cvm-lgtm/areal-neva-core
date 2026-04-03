import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

def extract_google_id(s: str) -> str:
    if "id=" in s: return s.split("id=")[1].split("&")[0]
    if "/d/" in s: return s.split("/d/")[1].split("/")[0]
    return s

class DriveAdapter:
    def __init__(self, creds_path="/root/.areal-neva-core/credentials.json"):
        self.creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        self.service = build("drive", "v3", credentials=self.creds, cache_discovery=False)

    def download(self, file_id: str) -> bytes:
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return fh.getvalue()

    def upload(self, name: str, data: bytes, folder_id: str = None) -> str:
        media = MediaIoBaseUpload(io.BytesIO(data), resumable=True)
        file_metadata = {"name": name}
        if folder_id:
            file_metadata["parents"] = [folder_id]
        file = self.service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return file.get("id")
