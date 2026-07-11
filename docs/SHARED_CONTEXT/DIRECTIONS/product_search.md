# direction: product_search

GENERATED_AT: 2026-07-11T20:20:03.375672+00:00
GIT_SHA: d88a8860a83d372aedbadab2e65f00f18f0497c4
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

