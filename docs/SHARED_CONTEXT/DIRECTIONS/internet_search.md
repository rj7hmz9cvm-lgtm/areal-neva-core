# direction: internet_search

GENERATED_AT: 2026-07-30T01:35:02.255500+00:00
GIT_SHA: 7ce4f69c279f59a74bc967d2d24a2c8bbbcc7b7f
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

