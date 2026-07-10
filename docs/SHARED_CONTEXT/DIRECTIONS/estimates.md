# direction: estimates

GENERATED_AT: 2026-07-10T18:42:32.027249+00:00
GIT_SHA: aa4331dd63e0803a3fea583645ba2328bd868ab1
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

