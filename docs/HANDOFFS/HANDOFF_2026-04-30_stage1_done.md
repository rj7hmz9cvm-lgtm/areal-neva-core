# HANDOFF 2026-04-30 — STAGE 1 ЗАКРЫТ

## Коммиты сессии
- 8f9ed54 FULLFIX_DIRECTION_KERNEL_STAGE_1
- 282716a SYNTAX_FIX
- a8955bb WIRING_FIX

## Установлено
- core/work_item.py
- core/direction_registry.py
- config/directions.yaml (26 directions, 13 active / 13 passive)
- docs/ARCHITECTURE/WORKITEM_V1.md
- docs/ARCHITECTURE/DIRECTION_REGISTRY_V1.md
- task_worker.py: payload = _stage1_dir_payload(payload) перед asyncio.wait_for

## Shadow mode
direction детектируется, кладётся в payload. Старый pipeline не тронут.

## Smoke 6/6 OK
product_search / auto_parts_search / estimates / technical_supervision / orchestration_core / general_chat

## Побочная находка
areal-monitor-jobs плодил 100+ зомби monitor_jobs.py → OOM → убивал task_worker
Починено: KillMode=control-group в systemd override

## Следующий шаг
Stage 2 — Capability Router
