# direction: product_search

GENERATED_AT: 2026-07-25T23:46:07.360449+00:00
GIT_SHA: b9eda8980948726df2b3b2b06ac3b5ab59c1afac
GENERATED_FROM: core.direction_registry.DirectionRegistry

DIRECTION_ID: product_search
TITLE: Товарный поиск
ENABLED: True
ENGINE: search_supplier
REQUIRES_SEARCH: True
TOPIC_IDS: []
INPUT_TYPES: ['text', 'voice', 'photo']
INPUT_FORMATS: ['text', 'photo', 'url']
OUTPUT_FORMATS: ['telegram_table', 'json', 'xlsx']
QUALITY_GATES: ['price_required', 'source_required', 'tco_required']
ALIASES: ['куп', 'цен', 'дешевл', 'товар', 'поставщик', 'заказ']
STRONG_ALIASES: ['avito', 'ozon', 'wildberries', 'авито', 'озон', 'вб']

## BOUND_TOPICS_STATUS
- (no topic_ids bound)

