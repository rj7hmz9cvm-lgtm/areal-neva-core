import os
import logging
from voice_engine import transcribe_voice

logger = logging.getLogger("router")

async def route_task(task_id, input_type, content):
    logger.info(f"Routing task {task_id} [type={input_type}]")

    # 1. Если это голос — сначала в текст
    if input_type == 'voice':
        text_content = await transcribe_voice(task_id, content)
        if text_content.startswith("ERROR"):
            return text_content
        content = text_content

    # 2. Логика Content Manager (из Bio)
    # Если в запросе есть ключевые слова для создания медиа
    content_lower = content.lower()
    if any(word in content_lower for word in ["картинку", "изображение", "видео", "рекламный"]):
        logger.info("Media generation request detected")
        # Тут будет вызов image_engine или video_engine
        return f"CONT_MGR_MODE: Принял задачу на генерацию контента: {content}"

    # 3. Обычный текстовый запрос в LLM
    return content # Возвращаем текст для ask_ai.py
