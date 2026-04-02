from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

creds = service_account.Credentials.from_service_account_file(
    "/root/.areal-neva-core/credentials.json",
    scopes=SCOPES
)

service = build("drive", "v3", credentials=creds)

FOLDER_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"

file_metadata = {
    "name": "test_ok.txt",
    "parents": [FOLDER_ID]
}

media = MediaInMemoryUpload(b"OK\n", mimetype="text/plain")

file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields="id"
).execute()

print("UPLOAD_OK:", file.get("id"))
