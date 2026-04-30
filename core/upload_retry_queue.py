"""
Upload retry queue.
Finds tasks where artifact was sent to Telegram (Drive failed),
checks if Drive is now available, re-uploads to Drive.
Notifies user in Telegram with new Drive link.
"""
import os
import sqlite3
import logging
import tempfile
import requests
from dotenv import load_dotenv

load_dotenv("/root/.areal-neva-core/.env", override=True)

logging.basicConfig(
    filename="/root/.areal-neva-core/logs/upload_retry_queue.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

DB_PATH = "/root/.areal-neva-core/data/core.db"
BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")


def check_drive_alive() -> bool:
    try:
        from core.engine_base import upload_artifact_to_drive
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("retry_queue_healthcheck")
            tmp = f.name
        link = upload_artifact_to_drive(tmp, "retry_hc", 0)
        try:
            os.remove(tmp)
        except Exception:
            pass
        return bool(link and "drive.google.com" in str(link))
    except Exception as e:
        logger.warning("DRIVE_HEALTH_CHECK_FAILED err=%s", e)
        return False


def get_pending_retry_tasks(conn: sqlite3.Connection):
    return conn.execute(
        """
        SELECT t.id, t.chat_id, t.topic_id, t.result,
               th_tg.action as tg_action
        FROM tasks t
        JOIN task_history th_tg ON th_tg.task_id = t.id
            AND th_tg.action LIKE 'TELEGRAM_ARTIFACT_FALLBACK_SENT:%'
        WHERE t.state IN ('AWAITING_CONFIRMATION','DONE')
          AND NOT EXISTS (
              SELECT 1 FROM task_history th2
              WHERE th2.task_id = t.id
                AND th2.action LIKE 'DRIVE_RETRY_UPLOAD_OK:%'
          )
        ORDER BY t.updated_at DESC
        LIMIT 20
        """,
    ).fetchall()


def parse_tg_action(action: str) -> dict:
    result = {}
    for part in action.split(":"):
        if "=" in part:
            k, v = part.split("=", 1)
            result[k] = v
    return result


def download_from_telegram(file_id: str, dest_path: str) -> bool:
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getFile",
            params={"file_id": file_id},
            timeout=15,
        )
        if not r.ok:
            return False
        file_path = r.json().get("result", {}).get("file_path")
        if not file_path:
            return False
        dl = requests.get(
            f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}",
            timeout=30,
        )
        if not dl.ok:
            return False
        with open(dest_path, "wb") as f:
            f.write(dl.content)
        return True
    except Exception as e:
        logger.error("TG_DOWNLOAD_FAILED file_id=%s err=%s", file_id, e)
        return False


def notify_telegram(chat_id, topic_id, message: str):
    if not BOT_TOKEN:
        return
    try:
        data = {"chat_id": str(chat_id), "text": message, "parse_mode": "HTML"}
        if topic_id and int(topic_id) > 0:
            data["message_thread_id"] = str(topic_id)
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json=data, timeout=10,
        )
    except Exception as e:
        logger.warning("NOTIFY_FAILED err=%s", e)


def run():
    logger.info("RETRY_QUEUE_START")

    if not check_drive_alive():
        logger.info("DRIVE_UNAVAILABLE — skip retry")
        return

    logger.info("DRIVE_ALIVE — checking pending tasks")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        pending = get_pending_retry_tasks(conn)
        logger.info("PENDING_RETRY_COUNT=%d", len(pending))

        for row in pending:
            task_id = row["id"]
            chat_id = row["chat_id"]
            topic_id = row["topic_id"]
            tg_info = parse_tg_action(row["tg_action"])
            file_id = tg_info.get("file_id")

            if not file_id:
                logger.warning("RETRY_SKIP task=%s no file_id", task_id)
                continue

            logger.info("RETRY_ATTEMPT task=%s file_id=%s", task_id, file_id)

            with tempfile.NamedTemporaryFile(
                suffix=".bin", delete=False,
                dir="/root/.areal-neva-core/runtime"
            ) as tmp:
                tmp_path = tmp.name

            ok = download_from_telegram(file_id, tmp_path)
            if not ok:
                logger.error("RETRY_TG_DOWNLOAD_FAILED task=%s", task_id)
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                continue

            # PATCH_RETRY_TOPIC_FOLDER_V1: upload to topic folder, not INGEST root
            try:
                import mimetypes as _mt
                from core.topic_drive_oauth import _upload_file_sync
                # Get original file name from task raw_input
                try:
                    _raw = conn.execute("SELECT raw_input FROM tasks WHERE id=?", (task_id,)).fetchone()
                    _orig_name = json.loads(_raw["raw_input"] or "{}").get("file_name", f"artifact_{task_id[:8]}")
                except Exception:
                    _orig_name = f"artifact_{task_id[:8]}"
                _mime = _mt.guess_type(_orig_name)[0] or "application/octet-stream"
                _up = _upload_file_sync(
                    tmp_path, _orig_name,
                    str(row["chat_id"]), int(topic_id or 0), _mime
                )
                _fid = _up.get("drive_file_id") if isinstance(_up, dict) else None
                drive_link = f"https://drive.google.com/file/d/{_fid}/view" if _fid else None
            except Exception as e:
                logger.error("RETRY_DRIVE_UPLOAD_FAILED task=%s err=%s", task_id, e)
                drive_link = None
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

            if not drive_link or "drive.google.com" not in str(drive_link):
                logger.error("RETRY_NO_LINK task=%s", task_id)
                continue

            old_result = row["result"] or ""
            new_result = old_result.replace(
                "Файл отправлен в Telegram. Внешнее хранилище временно недоступно.",
                f"Файл доступен на Drive: {drive_link}"
            )
            if new_result == old_result:
                new_result = old_result + f"\n\nФайл теперь на Drive: {drive_link}"

            conn.execute(
                "UPDATE tasks SET result=?, updated_at=datetime('now') WHERE id=?",
                (new_result, task_id),
            )
            conn.execute(
                "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
                (task_id, f"DRIVE_RETRY_UPLOAD_OK:{drive_link}"),
            )
            conn.commit()

            notify_telegram(
                chat_id, topic_id,
                f"✅ Файл теперь доступен на Google Drive:\n{drive_link}"
            )
            logger.info("RETRY_UPLOAD_OK task=%s link=%s", task_id, drive_link)

    finally:
        conn.close()

    logger.info("RETRY_QUEUE_DONE")


if __name__ == "__main__":
    # === FULLFIX_20_RETRY_LOOP ===
    import time as _ff20_time
    logger.info("UPLOAD_RETRY_SERVICE_START")
    while True:
        try:
            run()
        except Exception as _ff20_re:
            logger.exception("UPLOAD_RETRY_LOOP_ERR=%s", _ff20_re)
        _ff20_time.sleep(300)
    # === END FULLFIX_20_RETRY_LOOP ===
