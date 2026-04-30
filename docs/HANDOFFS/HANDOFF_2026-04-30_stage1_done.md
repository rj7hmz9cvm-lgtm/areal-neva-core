# HANDOFF 2026-04-30 — STAGE 1 ЗАКРЫТ

## Статус
FULLFIX_DIRECTION_KERNEL_STAGE_1 — УСТАНОВЛЕН И ПРИНЯТ

## Коммиты сессии
- 8f9ed54 FULLFIX_DIRECTION_KERNEL_STAGE_1 workitem+registry+26 directions+canon docs
- 282716a SYNTAX_FIX inline comment broke asyncio.wait_for
- a8955bb WIRING FIX payload line before asyncio.wait_for

## Что установлено
- core/work_item.py — WorkItem dataclass, from_task_row, to_payload
- core/direction_registry.py — DirectionRegistry.detect(), scoring, 26 directions
- config/directions.yaml — JSON внутри YAML, 13 active + 13 passive
- docs/ARCHITECTURE/WORKITEM_V1.md — канон
- docs/ARCHITECTURE/DIRECTION_REGISTRY_V1.md — канон
- task_worker.py wiring — payload = _stage1_dir_payload(payload) перед asyncio.wait_for

## Shadow mode
direction детектируется и кладётся в payload.
Старый pipeline не тронут. Маршрутизации нет — Stage 2.

## Smoke (6/6 OK)
- topic=500 "найди avito ozon" → product_search
- topic=961 "drom фара toyota hiace" → auto_parts_search
- topic=2 "сделай смету" → estimates
- topic=2 "технадзор дефект акт" → technical_supervision
- topic=3008 "канон оркестра" → orchestration_core
- topic=0 "привет как дела" → general_chat

## Побочная находка
areal-monitor-jobs плодил 100+ зомби-процессов monitor_jobs.py
Заполнил 3.8GB из 4GB RAM → OOM killer убивал task_worker
Починено вручную (kill -9). Требует отдельного фикса в monitor_jobs.

## Следующий шаг
Stage 2 — Capability Router
ИЛИ сначала фикс areal-monitor-jobs (zombie процессы)

## Сервисы на момент закрытия
TW_ACTIVE NRestarts=0 MainPID живой память 3006MB free
