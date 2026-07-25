# direction: internet_search

GENERATED_AT: 2026-07-25T07:45:02.696920+00:00
GIT_SHA: fe528717e27a3ff0951aac75479498c498a5974a
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

