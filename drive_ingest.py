import os, time, sqlite3, logging
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "/root/.areal-neva-core/credentials.json"
FOLDER_ID = os.getenv("DRIVE_INGEST_FOLDER_ID", "root")
CORE_DB = "/root/.areal-neva-core/data/core.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("drive_ingest")

def main():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)
    logger.info(f"Мониторинг папки: {FOLDER_ID}")
    
    while True:
        try:
            results = service.files().list(q=f"'{FOLDER_ID}' in parents", pageSize=10).execute()
            for item in results.get("files", []):
                logger.info(f"Найден файл: {item['name']} ({item['id']})")
            time.sleep(60)
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
