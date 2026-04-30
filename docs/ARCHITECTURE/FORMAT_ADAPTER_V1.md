# FORMAT_ADAPTER_V1 — Stage 7

## Назначение
Адаптирует результат движка к форматам доставки из formats_out.
Shadow mode: adapted пишется в ai_result["format_adapted"], доставка идёт через старый pipeline.

## Поддерживаемые форматы
telegram_text, telegram_table, xlsx, docx, pdf, json, drive_link, google_sheet, sources, script, mp4, table

## Результат
```json
{
  "format_adapter_version": "FORMAT_ADAPTER_V1",
  "shadow_mode": true,
  "formats_out": ["xlsx", "telegram_text"],
  "outputs": {
    "xlsx": {"type": "xlsx", "url": "https://...", "ready": true},
    "telegram_text": {"type": "telegram_text", "text": "...", "length": 42}
  },
  "primary": {...}
}
```

## API
```python
from core.format_adapter import FormatAdapter, adapt_result
adapted = adapt_result(result, formats_out, payload)
```

## Файл
core/format_adapter.py | FULLFIX_FORMAT_ADAPTER_STAGE_7
