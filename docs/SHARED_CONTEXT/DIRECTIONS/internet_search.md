# direction: internet_search

GENERATED_AT: 2026-05-07T17:24:50.064116+00:00
GIT_SHA: 551829d5a33270fde4d9355e2dae407da05e6fb3
GENERATED_FROM: core.direction_registry.DirectionRegistry

DIRECTION_ID: internet_search
TITLE: Интернет-поиск
ENABLED: True
ENGINE: search_supplier
REQUIRES_SEARCH: True
TOPIC_IDS: [500]
INPUT_TYPES: ['text', 'voice']
INPUT_FORMATS: ['text', 'url']
OUTPUT_FORMATS: ['telegram_text', 'table', 'sources']
QUALITY_GATES: ['sources_required']
ALIASES: ['найд', 'поиск', 'перплексити', 'в интернете']
STRONG_ALIASES: []

## BOUND_TOPICS_STATUS
- topic_500: IDLE_NO_FAILURES_NOT_VERIFIED

