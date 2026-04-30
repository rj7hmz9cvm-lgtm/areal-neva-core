# CHAT_EXPORT — claude_orchestra — 2026-04-30 evening

## SOURCE
- model: Claude Opus 4.7
- chat: -1003725299009 (orchestra)
- exported_at: 2026-04-30 evening MSK
- protocol: §37 EXPORT_CANON

## SYSTEM
Ubuntu 24.04, /root/.areal-neva-core, IP 89.22.225.136
Сервисы (5/5 active): areal-task-worker, telegram-ingress, areal-memory-api, areal-monitor-jobs, areal-upload-retry

## PIPELINE STATE
Базовый pipeline работает. Stage 1 Direction Kernel — proposal, не установлен.

## ЧТО ЗАКРЫТО КОДОМ В ЭТОЙ СЕССИИ

### Утренние коммиты
- 5eb59b9 FINAL_CLOSURE photo_linkage + template_engine + drive_link_mandatory
- 18a91ee TELEGRAM_FALLBACK_V1 Drive fail → send file directly to Telegram
- b92b074 TG_FALLBACK_WIRED в upload_or_fail (Drive fail → Telegram замкнут)

### Вечерние коммиты (если установлены)
- SEARCH_PLANNER_V1 (criteria + clarification + expand + profiles + tco + risk) — установлен в core/search_planner.py + ai_router

## ИСТОРИЯ ОБСУЖДЕНИЙ

### 1. Сверка с каноном
Проверены §1-§11 главного канона + ТЗ Lifecycle. Закрыто кодом большинство пунктов. §19 LIVE VERIFICATION — ни один из 9 сценариев не пройден живым тестом.

### 2. TELEGRAM_FALLBACK при Drive fail
Цепочка замкнута:
- Drive падает → upload_retry_queue (отложенный retry)
- Параллельно → _telegram_fallback_send() (немедленно)
- Возвращает telegram://file/{file_id}
- Пользователь получает файл даже без Drive

### 3. SEARCH_PLANNER_V1
Установлены модули:
- core/search_planner.py: extract_criteria, needs_clarification, expand_queries, plan_sources, classify_supplier, calculate_tco, score_risk, format_search_output
- Профили BUILDING/AUTO/GENERAL
- SEARCH_PLANNER_V1_INJECTED в ai_router.py (расширение SEARCH_SYSTEM_PROMPT)
- SEARCH_PLANNER_WIRE_V1 в process_ai_task

### 4. Архитектурное обсуждение Stage 1
Три позиции: ChatGPT (8 модулей сразу), третий участник (pipeline/state machine), Claude (поэтапно). Финальный синтез — FULLFIX_DIRECTION_KERNEL_STAGE_1 как минимальный shadow-mode слой.

См. docs/ARCHITECTURE/STAGE_1_DIRECTION_KERNEL_PROPOSAL.md

## ERRORS И ИХ ИСПРАВЛЕНИЕ
- EXCEPT_ANCHOR_NOT_FOUND в engine_base — auto-fallback на artifact_upload_guard
- GUARD_ANCHOR_NOT_FOUND — потребовал второй проход через TG_FALLBACK_WIRED
- Scoring mismatch в первом draft DirectionRegistry — исправлен strong_aliases + specificity bonus

## PENDING
- Stage 1 Direction Kernel — код готов, ждёт явного запуска
- §19 LIVE VERIFICATION 9 сценариев — не проводилось
- KZH PDF live test — не проводилось
- Excel формулы =C2*D2 live test — не проводилось

## DECISIONS СЕССИИ
1. Stage 1 в shadow-mode (не переносим execution)
2. 26 направлений в YAML, 13 active / 13 passive
3. Score-based detection с strong_aliases override
4. Tarball для скачивания на Mac → Drive вручную
5. Три параллельных артефакта: GitHub чистый / сервер полный / tarball

## SECRETS
В этом файле — нет. Полная версия со всеми секретами в /root/BACKUPS/areal-neva-core/full_export_2026-04-30_evening/
