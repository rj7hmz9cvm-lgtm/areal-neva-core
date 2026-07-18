# direction: internet_search

GENERATED_AT: 2026-07-18T11:38:33.773347+00:00
GIT_SHA: 3e0f8022d33b38d0b5dc1d4560604285d9ca2315
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
- topic_500: UNKNOWN

