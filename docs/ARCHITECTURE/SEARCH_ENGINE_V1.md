# SEARCH_ENGINE_V1 — Stage 5

## Назначение
Формирует search_plan для задач с requires_search=True.
Shadow mode: plan пишется в payload["search_plan"], реальный поиск — через search_supplier (существующий движок).

## Профили по направлению
- product_search: avito, ozon, wildberries / price_compare
- auto_parts_search: drom, exist, emex, zzap / compatibility
- construction_search: petrovitch, lerua, grand_line / price_delivery
- internet_search: web / general

## search_plan структура
```json
{
  "query": "текст запроса",
  "direction": "product_search",
  "sources": ["avito", "ozon"],
  "strategy": "price_compare",
  "shadow_mode": true,
  "status": "planned"
}
```

## API
```python
from core.search_engine import SearchEngine, plan_search
plan = plan_search(work_item, payload)
```

## Файл
core/search_engine.py | FULLFIX_SEARCH_ENGINE_STAGE_5
