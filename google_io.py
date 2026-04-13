import os, io, logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials

logger = logging.getLogger("google_io")

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDS_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '/root/.areal-neva-core/credentials.json')
PARENT_FOLDER_ID = os.getenv('GDRIVE_PARENT_ID', '')

def get_drive_service():
    if not os.path.exists(CREDS_FILE):
        return None
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

async def upload_to_drive(file_path: str, file_name: str, mime_type: str = None) -> dict:
    try:
        service = get_drive_service()
        if not service:
            return {'ok': False, 'error': 'Drive not configured'}
        
        import mimetypes
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_name)
            mime_type = mime_type or 'application/octet-stream'
        
        file_metadata = {'name': file_name}
        if PARENT_FOLDER_ID:
            file_metadata['parents'] = [PARENT_FOLDER_ID]
        
        with open(file_path, 'rb') as f:
            media = MediaIoBaseUpload(io.BytesIO(f.read()), mimetype=mime_type, resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        return {'ok': True, 'drive_file_id': file.get('id')}
    except Exception as e:
        logger.error("Drive upload failed: %s", e)
        return {'ok': False, 'error': str(e)}
