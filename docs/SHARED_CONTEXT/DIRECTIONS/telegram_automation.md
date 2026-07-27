# direction: telegram_automation

GENERATED_AT: 2026-07-27T15:25:02.786376+00:00
GIT_SHA: db39450f1a1a03b5f6c9c563d965538cd8b211b5
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

