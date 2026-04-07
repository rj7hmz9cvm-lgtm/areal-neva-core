from __future__ import annotations

from core.automation_engine import create_rule

async def route_task(text: str, chat_id: int, user_id: int, topic_id: int | None = None) -> dict:
    text_lower = (text or "").lower()

    if "напомни" in text_lower or "проверь" in text_lower:
        rule_id = await create_rule({
            "name": f"user_rule_{chat_id}",
            "type": "schedule",
            "source": "telegram",
            "chat_id": chat_id,
            "topic_id": topic_id,
            "user_id": user_id,
            "message": text,
            "schedule": {"interval_seconds": 86400},
        })
        return {
            "status": "done",
            "route": "automation",
            "summary": f"Правило создано: {rule_id[:8]}"
        }

    return {
        "status": "pending",
        "route": "general",
        "summary": "Передано в общий pipeline"
    }
