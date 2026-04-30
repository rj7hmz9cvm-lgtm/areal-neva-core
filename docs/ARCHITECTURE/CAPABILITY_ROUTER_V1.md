# CAPABILITY_ROUTER_V1 — Stage 2

## Назначение
Берёт WorkItem с direction (Stage 1), формирует execution_plan. Shadow mode.

## ENGINE_MAP
26 направлений → движок. Fallback: ai_router.

## Шаги плана
1. OCR pre-step (photo input, кроме photo_cleanup)
2. Search pre-step (requires_search=True)
3. Main execute (обязательный)
4. Format adapters (xlsx/docx/pdf)
5. Drive upload (drive_link в formats_out)

## API
```python
from core.capability_router import CapabilityRouter
routing = CapabilityRouter().apply_to_work_item(work_item)
# work_item.execution_plan, formats_out, quality_gates заполнены
```

## Статус
Shadow mode. execution_plan формируется, в payload["engine"] пишется движок.
Stage 4 подключит реальный dispatch.

## Файл
core/capability_router.py | FULLFIX_CAPABILITY_ROUTER_STAGE_2
