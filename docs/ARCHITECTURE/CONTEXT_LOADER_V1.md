# CONTEXT_LOADER_V1 — Stage 3

## Назначение
Загружает контекст задачи: short_memory из memory_api, topic_context из DB.
Пишет в work_item.context_refs. Shadow mode — ошибки не блокируют pipeline.

## Источники
- short_memory: GET http://127.0.0.1:8765/memory?chat_id=&topic_id=&limit=5 (timeout=2s)
- topic_context: SELECT из tasks по chat_id + topic_id, последние 5

## API
```python
from core.context_loader import ContextLoader, load_context
refs = load_context(work_item, db_conn=conn)
# work_item.context_refs заполнен
```

## context_refs структура
- chat_id, topic_id, direction
- short_memory: список записей из memory_api или None
- topic_context: последние 5 задач по теме из DB
- loader_version, shadow_mode

## Файл
core/context_loader.py | FULLFIX_CONTEXT_LOADER_STAGE_3
