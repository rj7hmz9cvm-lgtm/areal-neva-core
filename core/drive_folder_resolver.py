# === DRIVE_CANON_FOLDER_RESOLVER_V1 ===
from __future__ import annotations

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger("drive_folder_resolver")

BASE = "/root/.areal-neva-core"
load_dotenv(f"{BASE}/.env", override=True)

DEFAULT_CHAT_ID = "-1003725299009"


def get_or_create_topic_folder(topic_id: int, chat_id: str = "") -> str:
    """
    Canonical Drive layout:
    AI_ORCHESTRA / chat_<chat_id> / topic_<topic_id>

    This resolver MUST NOT use Service Account and MUST NOT create flat folders:
    chat_-1003725299009_topic_2
    """
    from core.topic_drive_oauth import _oauth_service, _root_folder_id, _ensure_folder

    service = _oauth_service()
    root_id = _root_folder_id()
    chat = str(chat_id or os.getenv("TELEGRAM_CHAT_ID") or DEFAULT_CHAT_ID)
    chat_folder = _ensure_folder(service, root_id, f"chat_{chat}")
    topic_folder = _ensure_folder(service, chat_folder, f"topic_{int(topic_id or 0)}")
    logger.info(
        "DRIVE_CANON_FOLDER_RESOLVER_V1_OK chat=%s topic=%s folder=%s",
        chat,
        int(topic_id or 0),
        topic_folder,
    )
    return topic_folder


# === END_DRIVE_CANON_FOLDER_RESOLVER_V1 ===
