# direction: telegram_automation

GENERATED_AT: 2026-08-01T04:42:12.962196+00:00
GIT_SHA: db7b7aaafeb2cc30644643a031cc8be525848076
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

