# === FULLFIX_ARCHIVE_ENGINE_STAGE_6 ===
from __future__ import annotations
import json
import logging
from typing import Any, Dict, Optional

ARCHIVE_ENGINE_VERSION = "ARCHIVE_ENGINE_V1"
logger = logging.getLogger("task_worker")


class ArchiveEngine:
    """
    Stage 6 shadow mode: индексирует завершённую задачу в memory.db.
    Пишет short_summary, direction, engine, quality_gate_overall.
    Не блокирует доставку при ошибках.
    """

    def archive(self, payload: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "task_id":      str(payload.get("task_id") or payload.get("id") or ""),
            "chat_id":      str(payload.get("chat_id") or ""),
            "topic_id":     int(payload.get("topic_id") or 0),
            "direction":    str(payload.get("direction") or "general_chat"),
            "engine":       str(payload.get("engine") or "ai_router"),
            "input_type":   str(payload.get("input_type") or "text"),
            "raw_input":    str(payload.get("raw_input") or payload.get("raw_text") or "")[:300],
            "result_text":  str((result.get("result") or {}).get("text") or result.get("text") or "")[:500],
            "artifact_url": str(result.get("artifact_url") or result.get("drive_link") or ""),
            "qg_overall":   str((result.get("quality_gate_report") or {}).get("overall") or "unknown"),
            "qg_failed":    json.dumps((result.get("quality_gate_report") or {}).get("failed") or []),
            "search_plan":  json.dumps(payload.get("search_plan") or {}),
            "archive_version": ARCHIVE_ENGINE_VERSION,
            "shadow_mode":  True,
        }

        self._write_to_memory_api(record)
        return record

    def _write_to_memory_api(self, record: Dict[str, Any]):
        import urllib.request, urllib.error
        try:
            body = json.dumps(record).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8765/archive",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=2)
            logger.info("FULLFIX_ARCHIVE_ENGINE_STAGE_6 archived task=%s dir=%s qg=%s",
                        record["task_id"], record["direction"], record["qg_overall"])
        except Exception as e:
            logger.warning("FULLFIX_ARCHIVE_ENGINE_STAGE_6 memory_api unavailable: %s", e)


def archive_task(payload, result):
    return ArchiveEngine().archive(payload, result)
# === END FULLFIX_ARCHIVE_ENGINE_STAGE_6 ===
