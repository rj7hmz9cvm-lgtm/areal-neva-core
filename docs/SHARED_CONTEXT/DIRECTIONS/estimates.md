# direction: estimates

GENERATED_AT: 2026-07-20T11:44:51.957759+00:00
GIT_SHA: 09b976236b904485c12c4f054ce58f28c0a404ab
GENERATED_FROM: core.direction_registry.DirectionRegistry

DIRECTION_ID: estimates
TITLE: Сметы
ENABLED: True
ENGINE: estimate_unified
REQUIRES_SEARCH: False
TOPIC_IDS: [2]
INPUT_TYPES: ['text', 'voice', 'file', 'drive_file']
INPUT_FORMATS: ['text', 'pdf', 'xlsx', 'csv', 'photo']
OUTPUT_FORMATS: ['xlsx', 'pdf', 'drive_link', 'telegram_text']
QUALITY_GATES: ['items_required', 'total_required', 'xlsx_required']
ALIASES: ['смет', 'расценк', 'ведомост', 'объем работ', 'вор', 'фер', 'тер']
STRONG_ALIASES: []

## BOUND_TOPICS_STATUS
- topic_2: UNKNOWN

