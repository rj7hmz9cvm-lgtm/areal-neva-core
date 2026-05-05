#!/usr/bin/env python3
# === TELEGRAM_SOURCE_SKILL_EXTRACTOR_V1 ===
# Read-only Telethon-based extractor for public Telegram sources.
# Collects message metadata, links, and document references.
# Does NOT save raw history to memory.db or create core.db tasks.
from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("telegram_source_skill_extractor")

BASE = Path(__file__).parent.parent
SESSION_PATH = BASE / "sessions" / "user.session"
API_ID = 27925449

URL_RE = re.compile(r"https?://[^\s\)\]\>\"']+")

DOCUMENT_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls",
    ".pptx", ".ppt", ".zip", ".rar", ".dwg", ".dxf",
}

TECHNADZOR_KEYWORDS = [
    "акт", "дефект", "предписание", "заключение", "протокол",
    "осмотр", "проверка", "замечание", "нарушение", "устранение",
    "приёмка", "приемка", "скрытые работы", "исполнительная",
    "норматив", "снип", "гост", "сп ", "фото", "документ",
    "отчёт", "отчет", "смета", "спецификация", "чертёж", "чертеж",
    "технадзор", "стройконтроль", "авторский надзор",
    "кровля", "фасад", "перекрытие", "колонна", "фундамент",
    "бетон", "арматура", "сварка", "металл", "кладка", "газобетон",
    "отделка", "стяжка", "штукатурка", "электрика", "вентиляция",
    "водоснабжение", "канализация", "охрана труда",
]

NOISE_MARKERS = [
    "реклама", "продам", "куплю", "скидка", "акция",
    "подпишись", "переходи по ссылке", "розыгрыш",
    "заработок", "кредит без отказа", "займ",
    "только сегодня", "бесплатно жми", "выиграли",
]


def load_env(path: str | None = None) -> dict:
    env_path = Path(path) if path else BASE / ".env"
    result = {}
    if not env_path.exists():
        return result
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        result[k.strip()] = v.strip()
    return result


def build_client(session_path: str | None = None):
    from telethon import TelegramClient
    sp = str(session_path or SESSION_PATH)
    # api_hash not stored — authorized session does not need it for reads
    return TelegramClient(sp, API_ID, "a" * 32)


def extract_links(text: str) -> list[str]:
    return URL_RE.findall(text or "")


def is_relevant_for_document_skill(
    message_text: str,
    file_name: str | None = None,
    links: list[str] | None = None,
) -> bool:
    low = (message_text or "").lower()
    if any(n in low for n in NOISE_MARKERS):
        return False
    if any(kw in low for kw in TECHNADZOR_KEYWORDS):
        return True
    fname_low = (file_name or "").lower()
    if any(ext in fname_low for ext in DOCUMENT_EXTENSIONS):
        return True
    for link in (links or []):
        if any(ext in link.lower() for ext in DOCUMENT_EXTENSIONS):
            return True
    return False


def build_source_record(msg_id: int, msg_date: str, text: str,
                        media_type: str | None, file_name: str | None,
                        links: list[str], channel: str) -> dict:
    return {
        "source": f"@{channel.lstrip('@')}",
        "message_id": msg_id,
        "message_date": msg_date,
        "text": (text or "")[:1500],
        "media_type": media_type,
        "file_name": file_name,
        "links": links,
        "source_ref": f"https://t.me/{channel.lstrip('@')}/{msg_id}",
    }


async def check_source_access(source: str, client) -> dict:
    try:
        entity = await client.get_entity(source.lstrip("@"))
        return {
            "ok": True,
            "id": entity.id,
            "title": getattr(entity, "title", ""),
            "username": getattr(entity, "username", ""),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def scan_source(source: str, client, limit: int = 1000) -> dict:
    from telethon.tl.types import (
        MessageMediaDocument, MessageMediaPhoto, MessageMediaWebPage
    )

    records: list[dict] = []
    total = skipped_empty = skipped_noise = detected_docs = detected_links = 0

    async for msg in client.iter_messages(source.lstrip("@"), limit=limit or None):
        total += 1
        text = (msg.message or "").strip()
        if not text and not msg.media:
            skipped_empty += 1
            continue

        low = text.lower()
        if any(n in low for n in NOISE_MARKERS):
            skipped_noise += 1
            continue

        links = extract_links(text)
        file_name = None
        media_type = None

        if isinstance(msg.media, MessageMediaDocument):
            doc = msg.media.document
            for attr in getattr(doc, "attributes", []):
                if hasattr(attr, "file_name") and attr.file_name:
                    file_name = attr.file_name
            media_type = "document"
            detected_docs += 1
        elif isinstance(msg.media, MessageMediaPhoto):
            media_type = "photo"
        elif isinstance(msg.media, MessageMediaWebPage):
            wp = msg.media.webpage
            if hasattr(wp, "url") and wp.url:
                links.append(wp.url)
            media_type = "webpage"

        if links:
            detected_links += 1

        date_str = msg.date.isoformat() if msg.date else ""
        record = build_source_record(
            msg.id, date_str, text, media_type, file_name,
            links, source.lstrip("@")
        )
        records.append(record)

    return {
        "total_fetched": total,
        "skipped_empty": skipped_empty,
        "skipped_noise": skipped_noise,
        "detected_docs": detected_docs,
        "detected_links": detected_links,
        "records": records,
    }


async def download_relevant_documents(
    client, msg, output_dir: Path
) -> str | None:
    from telethon.tl.types import MessageMediaDocument
    if not isinstance(msg.media, MessageMediaDocument):
        return None
    doc = msg.media.document
    file_name = f"doc_{msg.id}"
    for attr in getattr(doc, "attributes", []):
        if hasattr(attr, "file_name") and attr.file_name:
            file_name = attr.file_name
    ext = Path(file_name).suffix.lower()
    if ext not in DOCUMENT_EXTENSIONS:
        return None
    out_path = output_dir / file_name
    if out_path.exists():
        return str(out_path)
    try:
        await client.download_media(msg, file=str(out_path))
        return str(out_path)
    except Exception as e:
        logger.warning("download failed msg=%s err=%s", msg.id, e)
        return None


async def run_source_scan(
    source: str = "@tnz_msk",
    limit: int = 1000,
    download_docs: bool = False,
    docs_output_dir: Path | None = None,
) -> dict:
    client = build_client()
    await client.connect()

    if not await client.is_user_authorized():
        await client.disconnect()
        return {"ok": False, "error": "session_not_authorized"}

    access = await check_source_access(source, client)
    if not access["ok"]:
        await client.disconnect()
        return {"ok": False, "error": access.get("error")}

    scan = await scan_source(source, client, limit=limit)
    downloaded: list[str] = []

    if download_docs and docs_output_dir:
        docs_output_dir.mkdir(parents=True, exist_ok=True)
        from telethon.tl.types import MessageMediaDocument
        async for msg in client.iter_messages(source.lstrip("@"), limit=limit or None):
            if not isinstance(msg.media, MessageMediaDocument):
                continue
            text = msg.message or ""
            links = extract_links(text)
            doc = msg.media.document
            fname = ""
            for attr in getattr(doc, "attributes", []):
                if hasattr(attr, "file_name") and attr.file_name:
                    fname = attr.file_name
            if is_relevant_for_document_skill(text, fname, links):
                path = await download_relevant_documents(client, msg, docs_output_dir)
                if path:
                    downloaded.append(path)

    await client.disconnect()

    return {
        "ok": True,
        "source": source,
        "access": access,
        "scan": scan,
        "downloaded_documents": downloaded,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }
# === END_TELEGRAM_SOURCE_SKILL_EXTRACTOR_V1 ===
