# direction: telegram_automation

GENERATED_AT: 2026-07-29T06:35:02.827731+00:00
GIT_SHA: db5f24da65e7a4aa1e51cec8807fc8e617209d1d
GENERATED_FROM: core.direction_registry.DirectionRegistry

DIRECTION_ID: telegram_automation
TITLE: Telegram automation
ENABLED: True
ENGINE: telegram_pipeline
REQUIRES_SEARCH: False
TOPIC_IDS: []
INPUT_TYPES: ['text', 'voice']
INPUT_FORMATS: ['text']
OUTPUT_FORMATS: ['telegram_text']
QUALITY_GATES: ['reply_thread_required']
ALIASES: ['bot_message_id', 'message_thread_id', 'telegram daemon']
STRONG_ALIASES: []

## BOUND_TOPICS_STATUS
- (no topic_ids bound)

