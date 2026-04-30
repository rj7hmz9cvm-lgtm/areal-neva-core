# FULLFIX_DIRECTION_KERNEL_STAGE_1 — PROPOSAL

Дата: 2026-04-30 evening
Статус: PROPOSAL (не установлен)
Маркер: FULLFIX_DIRECTION_KERNEL_STAGE_1

## ИСТОРИЯ ОБСУЖДЕНИЯ

Три позиции были рассмотрены:

### Позиция 1 — ChatGPT (архитектурный максималист)
Предложил 8 модулей сразу: WorkItem, Direction Registry, Capability Router, Context Engine, Archive Engine, Search Supplier Engine, Quality Gate, Format Adapters. Конечная архитектура правильная, но порядок внедрения опасен.

### Позиция 2 — Третий участник (инженер pipeline)
Предложил pipeline/state machine модель: Intake → WorkItem → Kernel → Context → Engines → Quality Gate → Output → Archive. Engines изолированы от Telegram, Quality Gate перед выдачей.

### Позиция 3 — Claude (прагматик миграции)
Поэтапно: WorkItem первым (контракт), потом directions.yaml, потом Capability Router. Использовать существующее, не писать с нуля. 5-6 активных направлений из 26.

## СИНТЕЗ — FULLFIX_DIRECTION_KERNEL_STAGE_1

Минимальный shadow-mode слой:
- task_worker создаёт WorkItem (обёртка над tasks row)
- Direction Registry определяет direction
- direction кладётся в payload + audit
- старый pipeline продолжает работать как был

### Что НЕ делает Stage 1
- Не переносит _handle_in_progress
- Не переписывает engines
- Не меняет DB schema
- Не трогает telegram_daemon, reply_sender, ai_router без явного "да"
- Не делает Capability Router, Quality Gate, Format Adapters, Archive Index

## 26 НАПРАВЛЕНИЙ

### Active (13)
orchestration_core, telegram_automation, memory_archive, internet_search, product_search, auto_parts_search, construction_search, technical_supervision, estimates, defect_acts, documents, spreadsheets, google_drive_storage

### Passive (13) — описаны но не активны
devops_server, vpn_network, ocr_photo, cad_dwg, structural_design, roofing, monolith_concrete, crm_leads, email_ingress, social_content, video_production, photo_cleanup, isolated_project_ivan

## SCORING (выверенный)

1. **strong_aliases** (avito/ozon/drom/exist) → +200..+250 — overrides domain
2. **topic_id match** → +70 + specificity bonus (max +10)
3. **regular aliases** → +30 each, max +120
4. **input_type match** → +15 (только если есть другой сигнал)
5. **format match** → +10..+40 (только если есть другой сигнал)
6. **search_signal** → +25 (только для requires_search и при другом сигнале)
7. **passive penalty** → -80 (capped at 0)

Tie-break: score DESC → narrower topic_ids first

## КРИТЕРИИ ПРИЁМКИ

1. core/work_item.py существует
2. core/direction_registry.py существует
3. config/directions.yaml существует
4. docs/ARCHITECTURE/WORKITEM_V1.md существует
5. docs/ARCHITECTURE/DIRECTION_REGISTRY_V1.md существует
6. task_worker создаёт WorkItem
7. direction в work_payload
8. старый pipeline не изменён
9. py_compile OK для всех файлов
10. areal-task-worker active после restart
11. Smoke тесты:
    - topic_500 + "найди avito металлочерепица" → product_search
    - topic_961 + "drom фара toyota hiace" → auto_parts_search
    - topic_2 + "сделай смету" → estimates
    - topic_2 + "технадзор дефект акт" → technical_supervision
    - topic_3008 + "канон оркестра" → orchestration_core
    - topic_0 + "привет как дела" → general_chat
12. git pushed

## ROADMAP

- Stage 2: Capability Router
- Stage 3: Context Engine (вынос из task_worker)
- Stage 4: Quality Gate как отдельный слой
- Stage 5: Search Supplier Engine
- Stage 6: Archive Engine с SQL индексом
- Stage 7: Format Adapter Layer

## КОД

Готовый код в файлах:
- docs/ARCHITECTURE/STAGE_1_WORKITEM_V1_PROPOSAL.md (core/work_item.py)
- docs/ARCHITECTURE/STAGE_1_DIRECTION_REGISTRY_V1_PROPOSAL.md (direction_registry + yaml)
- docs/ARCHITECTURE/STAGE_1_INSTALL_BLOCK.md (полный установочный SSH блок)

## РЕЖИМ УСТАНОВКИ

Один атомарный SSH блок с set -euo pipefail. Pre-patch smoke ДО патча task_worker. Если scoring сломан — упадёт до того как тронуть task_worker. Бэкапы целы.

Запуск: только после явного "да" пользователя.
