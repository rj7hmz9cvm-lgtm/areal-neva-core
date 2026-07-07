# direction: estimates

GENERATED_AT: 2026-07-07T20:54:31.928322+00:00
GIT_SHA: 26126b947eb635b3906c20d062b2d92bbd7112d9
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
- topic_2: INSTALLED_NOT_VERIFIED

