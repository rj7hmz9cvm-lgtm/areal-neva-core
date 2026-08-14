# direction: internet_search

GENERATED_AT: 2026-08-14T03:10:02.986934+00:00
GIT_SHA: bf0e8f1c0e92b75bd9e20d0f02ebec2a191241b7
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

