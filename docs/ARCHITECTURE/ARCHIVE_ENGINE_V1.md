# ARCHIVE_ENGINE_V1 — Stage 6

## Назначение
Индексирует завершённую задачу в memory_api после доставки результата.
Shadow mode: POST /archive на 127.0.0.1:8765, timeout=2s. Ошибка — warning, не падает.

## Что пишет
- task_id, chat_id, topic_id
- direction, engine, input_type
- raw_input (до 300 символов)
- result_text (до 500 символов)
- artifact_url / drive_link
- qg_overall, qg_failed (из quality_gate_report)
- search_plan (из payload)

## API
```python
from core.archive_engine import ArchiveEngine, archive_task
record = archive_task(payload, result)
```

## Файл
core/archive_engine.py | FULLFIX_ARCHIVE_ENGINE_STAGE_6
