# direction: product_search

GENERATED_AT: 2026-08-09T09:20:02.680213+00:00
GIT_SHA: 33d5b505648a74e8742a9d35603ab96b3ddf9b88
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

