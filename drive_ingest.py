import json
import logging
import os
import sqlite3
import time
import uuid
from datetime import datetime, timezone

from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = "/root/.areal-neva-core/credentials.json"
FOLDER_ID = "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
CORE_DB = "/root/.areal-neva-core/data/core.db"
CHAT_ID = "-1003725299009"
TOPIC_ID = 0

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("drive_ingest")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [r[1] for r in rows]


def task_exists_for_file(conn: sqlite3.Connection, file_id: str) -> bool:
    try:
        row = conn.execute(
            "SELECT 1 FROM drive_files WHERE drive_file_id=? LIMIT 1",
            (file_id,)
        ).fetchone()
        return row is not None
    except Exception:
        return False


def create_task_for_file(item: dict) -> None:
    file_id = item["id"]
    file_name = item["name"]
    mime_type = item.get("mimeType", "")
    now = utc_now()
    task_id = str(uuid.uuid4())
    raw_input = json.dumps(
        {
            "file_id": file_id,
            "file_name": file_name,
            "mime_type": mime_type,
            "source": "google_drive"
        },
        ensure_ascii=False
    )

    conn = sqlite3.connect(CORE_DB)
    try:
        if task_exists_for_file(conn, file_id):
            return

        task_cols = set(table_columns(conn, "tasks"))
        drive_cols = set(table_columns(conn, "drive_files"))

        task_data = {
            "id": task_id,
            "chat_id": CHAT_ID,
            "input_type": "drive_file",
            "raw_input": raw_input,
            "state": "NEW",
            "topic_id": TOPIC_ID,
            "created_at": now,
            "updated_at": now,
        }
        task_insert_cols = [
            c for c in ["id", "chat_id", "input_type", "raw_input", "state", "topic_id", "created_at", "updated_at"]
            if c in task_cols
        ]
        if not task_insert_cols:
            raise RuntimeError("tasks table has no expected columns")

        task_sql = f"INSERT INTO tasks ({', '.join(task_insert_cols)}) VALUES ({', '.join(['?'] * len(task_insert_cols))})"
        conn.execute(task_sql, [task_data[c] for c in task_insert_cols])

        drive_data = {
            "task_id": task_id,
            "drive_file_id": file_id,
            "file_name": file_name,
            "mime_type": mime_type,
            "stage": "discovered",
            "created_at": now,
        }
        drive_insert_cols = [
            c for c in ["task_id", "drive_file_id", "file_name", "mime_type", "stage", "created_at"]
            if c in drive_cols
        ]
        if drive_insert_cols:
            drive_sql = f"INSERT INTO drive_files ({', '.join(drive_insert_cols)}) VALUES ({', '.join(['?'] * len(drive_insert_cols))})"
            conn.execute(drive_sql, [drive_data[c] for c in drive_insert_cols])

        conn.commit()
        logger.info("ЗАДАЧА СОЗДАНА: %s | %s", task_id, file_name)
    finally:
        conn.close()


def main() -> None:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)

    logger.info("Мониторинг папки: %s", FOLDER_ID)

    while True:
        try:
            results = service.files().list(
                q=f"'{FOLDER_ID}' in parents and trashed=false",
                pageSize=50,
                fields="files(id,name,mimeType,createdTime)"
            ).execute()

            for item in results.get("files", []):
                mime_type = item.get("mimeType", "")
                if mime_type == "application/vnd.google-apps.folder":
                    logger.info("SKIP FOLDER: %s (%s)", item["name"], item["id"])
                    continue
                logger.info("Найден файл: %s (%s)", item["name"], item["id"])
                create_task_for_file(item)

            time.sleep(60)
        except Exception as e:
            logger.error("Ошибка: %s", e)
            time.sleep(60)


if __name__ == "__main__":
    main()
