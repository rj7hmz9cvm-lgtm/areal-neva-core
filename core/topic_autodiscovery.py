# === FULLFIX_TOPIC_AUTODISCOVERY_V2 ===
from __future__ import annotations
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("task_worker")

AUTODISCOVERY_VERSION = "TOPIC_AUTODISCOVERY_V2"
CONFIG_PATH = Path("/root/.areal-neva-core/config/directions.yaml")
DATA_TOPICS_PATH = Path("/root/.areal-neva-core/data/topics")
NAMING_TIMEOUT_HOURS = 24
CONFLICT_SCORE_DELTA = 30
MIN_SCORE_TO_AUTOASSIGN = 60


def _load_config():
    raw = CONFIG_PATH.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except Exception:
        import yaml
        return yaml.safe_load(raw) or {}


def _save_config(data: dict):
    # Всегда пишем JSON — файл directions.yaml фактически JSON
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_topic_meta(topic_id: int) -> Dict:
    meta_file = DATA_TOPICS_PATH / str(topic_id) / "meta.json"
    if meta_file.exists():
        try:
            return json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_topic_meta(topic_id: int, meta: dict):
    folder = DATA_TOPICS_PATH / str(topic_id)
    folder.mkdir(parents=True, exist_ok=True)
    meta_file = folder / "meta.json"
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def _topic_known(topic_id: int, data: dict) -> Optional[str]:
    for direction_id, profile in data.get("directions", {}).items():
        if topic_id in (profile.get("topic_ids") or []):
            return direction_id
    return None


def _detect_with_audit(work_item) -> Tuple[str, int, str, int]:
    from core.direction_registry import DirectionRegistry
    reg = DirectionRegistry()
    results = []
    for direction_id, profile in reg.directions.items():
        score, item = reg._score_direction(direction_id, profile or {}, work_item)
        results.append((direction_id, score))
    results.sort(key=lambda x: -x[1])
    top = results[0] if results else ("general_chat", 0)
    second = results[1] if len(results) > 1 else ("general_chat", 0)
    return top[0], top[1], second[0], second[1]


def _create_topic_folder(topic_id: int, direction: str, name: str = ""):
    folder = DATA_TOPICS_PATH / str(topic_id)
    folder.mkdir(parents=True, exist_ok=True)
    meta = _load_topic_meta(topic_id)
    meta.update({
        "topic_id": topic_id,
        "direction": direction,
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "version": AUTODISCOVERY_VERSION,
    })
    _save_topic_meta(topic_id, meta)
    logger.info("TOPIC_AUTODISCOVERY folder: %s dir=%s name=%s", folder, direction, name)


def _register_topic(topic_id: int, direction: str, data: dict):
    profile = data["directions"].get(direction)
    if profile is None:
        return
    topic_ids = list(profile.get("topic_ids") or [])
    if topic_id not in topic_ids:
        topic_ids.append(topic_id)
        data["directions"][direction]["topic_ids"] = topic_ids
    _save_config(data)
    logger.info("TOPIC_REGISTERED topic_id=%s -> direction=%s", topic_id, direction)


def _send_naming_question(chat_id: str, topic_id: int):
    """Отправляет вопрос о названии топика один раз."""
    try:
        from core.reply_sender import send_reply  # IMPORT_FIX_V1
        send_reply(
            chat_id=str(chat_id),
            text="Как назовём этот чат? Ответь голосом или текстом.",
            message_thread_id=topic_id,
        )
        logger.info("TOPIC_NAMING_QUESTION sent chat=%s topic=%s", chat_id, topic_id)
    except Exception as e:
        logger.error("TOPIC_NAMING_QUESTION_ERR %s", e)


def check_naming_timeout(chat_id: str, topic_id: int):
    """
    Вызывается при каждом сообщении из топика.
    Если топик без имени и прошло 24 часа — один раз спрашивает название.
    """
    meta = _load_topic_meta(topic_id)
    if not meta:
        return
    if meta.get("name"):
        return
    if meta.get("naming_asked"):
        return
    created_at = meta.get("created_at")
    if not created_at:
        return
    try:
        created = datetime.fromisoformat(created_at)
        elapsed = (datetime.now(timezone.utc) - created).total_seconds() / 3600
        if elapsed >= NAMING_TIMEOUT_HOURS:
            meta["naming_asked"] = datetime.now(timezone.utc).isoformat()
            _save_topic_meta(topic_id, meta)
            _send_naming_question(chat_id, topic_id)
    except Exception as e:
        logger.error("TOPIC_NAMING_TIMEOUT_ERR %s", e)


def assign_name(topic_id: int, name: str):
    """Назначает имя топику. Вызывается когда пользователь ответил на вопрос."""
    meta = _load_topic_meta(topic_id)
    meta["name"] = name
    meta["named_at"] = datetime.now(timezone.utc).isoformat()
    _save_topic_meta(topic_id, meta)
    logger.info("TOPIC_NAMED topic=%s name=%s", topic_id, name)


def process(work_item, payload: Dict[str, Any]) -> Dict[str, Any]:
    topic_id = int(getattr(work_item, "topic_id", 0) or 0)
    chat_id = str(getattr(work_item, "chat_id", "") or payload.get("chat_id") or "")
    if topic_id == 0:
        return {}

    try:
        data = _load_config()
    except Exception as e:
        logger.error("TOPIC_AUTODISCOVERY config load error: %s", e)
        return {}

    # Уже известный топик — проверяем таймаут имени
    known = _topic_known(topic_id, data)
    if known:
        try:
            check_naming_timeout(chat_id, topic_id)
        except Exception:
            pass
        return {"status": "known", "direction": known}

    # Новый топик — детектируем направление
    try:
        top_dir, top_score, second_dir, second_score = _detect_with_audit(work_item)
    except Exception as e:
        logger.error("TOPIC_AUTODISCOVERY detect error: %s", e)
        return {"status": "detect_error"}

    # Недостаточный score
    if top_score < MIN_SCORE_TO_AUTOASSIGN:
        # Создаём папку но не регистрируем direction
        _create_topic_folder(topic_id, "unknown", "")
        logger.info("TOPIC_AUTODISCOVERY low score=%s topic=%s — folder created, waiting", top_score, topic_id)
        return {"status": "low_score", "topic_id": topic_id, "score": top_score}

    # Конфликт — уточняем
    delta = top_score - second_score
    if delta < CONFLICT_SCORE_DELTA and second_score >= MIN_SCORE_TO_AUTOASSIGN:
        logger.warning("TOPIC_CONFLICT topic=%s %s(%s) vs %s(%s)",
                       topic_id, top_dir, top_score, second_dir, second_score)
        payload["topic_conflict"] = {
            "topic_id": topic_id,
            "candidates": [
                {"direction": top_dir, "score": top_score},
                {"direction": second_dir, "score": second_score},
            ],
        }
        return {"status": "conflict", "candidates": [top_dir, second_dir]}

    # Однозначно — регистрируем молча
    try:
        _register_topic(topic_id, top_dir, data)
        _create_topic_folder(topic_id, top_dir, "")
        payload["topic_autodiscovered"] = {
            "topic_id": topic_id,
            "direction": top_dir,
            "score": top_score,
            "version": AUTODISCOVERY_VERSION,
        }
        logger.info("TOPIC_AUTODISCOVERY_DONE topic=%s -> %s score=%s", topic_id, top_dir, top_score)
        return {"status": "registered", "direction": top_dir, "score": top_score}
    except Exception as e:
        logger.error("TOPIC_REGISTER_ERR %s", e)
        return {"status": "register_error"}
# === END FULLFIX_TOPIC_AUTODISCOVERY_V2 ===
