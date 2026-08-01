# direction: product_search

GENERATED_AT: 2026-08-01T13:15:02.691500+00:00
GIT_SHA: ff479c276c86690a3595eb45008a6ed877f9cdf9
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

