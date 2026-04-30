# NOT_CLOSED — 30.04.2026 ФИНАЛ 04:15

## ЗАКРЫТО КОДОМ И VERIFIED (30.04.2026)

| Что | Патч/Действие | Статус |
|---|---|---|
| drive_file без intent → NEEDS_CONTEXT + меню | PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL | VERIFIED ✅ |
| Worker зависал на _recover_stale_tasks | PATCH_WORKER_PICK_BEFORE_STALE_V1 | VERIFIED ✅ |
| Guard до download | PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1 | VERIFIED ✅ |
| UnboundLocalError _pfin3_menu | PATCH_FIX_PFIN3_MENU_SHADOW_V1 | VERIFIED ✅ |
| Reply choice во всех топиках | PATCH_FILE_CHOICE_PRIORITY_V1 | VERIFIED ✅ |
| Старые DONE/CANCELLED цеплялись как parent | PATCH_FILE_PARENT_STRICT_OPEN_ONLY_V1 | VERIFIED ✅ |
| topic_id=0 захватывал чужие file tasks | PATCH_FILE_PARENT_STRICT_OPEN_ONLY_V1 | VERIFIED ✅ |
| engine_base.py отсутствовал | PATCH_ENGINE_BASE_RESTORE_SA_UPLOAD_V1 | VERIFIED ✅ |
| Drive upload через Direct OAuth | PATCH_DRIVE_DIRECT_OAUTH_V1 | VERIFIED ✅ |
| Telegram fallback если Drive упал | PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1 | VERIFIED ✅ |
| Retry upload из TG в Drive при восстановлении | core/upload_retry_queue.py + cron 10min | VERIFIED ✅ |
| OAuth app → Production | Google Cloud Console | VERIFIED ✅ |
| override.conf без закрывающей кавычки | fix | VERIFIED ✅ |
| Стухшие тестовые задачи topic_id=0 | db cleanup | DONE ✅ |

## НЕ ЗАКРЫТО — P1

- Голосовой confirm при AWAITING_CONFIRMATION (telegram_daemon.py:601)
- PATCH_DUPLICATE_GUARD_V1 — INSTALLED, live-тест не проводился
- PATCH_MULTI_FILE_INTAKE_V1 — INSTALLED, live-тест не проводился
- PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1 — INSTALLED, live-тест не проводился

## НЕ ЗАКРЫТО — P2

- Смета PDF → Excel → Drive end-to-end
- КЖ PDF pipeline
- project_engine end-to-end через Telegram
- Gemini vision live-тест
- Excel формулы =C2*D2 / =SUM
- Нормы СП/ГОСТ в technadzor_engine
- Multi-file один артефакт из комплекта
- Memory/pin перед меню
- Google Sheets интеграция
- Шаблоны end-to-end
- Storage adapter unified layer
- Universal result guard
- MODEL_ROUTER, FALLBACK_CHAIN

## DRIVE + STORAGE АРХИТЕКТУРА (финальная 30.04)

Primary: Direct OAuth → engine_base.upload_artifact_to_drive
Fallback: Telegram sendDocument → core/telegram_artifact_fallback.py
Retry: core/upload_retry_queue.py (cron */10) → TG file_id → Drive
Healthcheck: core/storage_healthcheck.py (cron */30)
Service Account: НЕ подходит для My Drive
google_io.py: НЕ используется для upload

## AUTO-UPDATE 2026-04-30 04:25
- PATCH_RETRY_TOPIC_FOLDER_V1: VERIFIED ✅ — retry загружает в topic папку, не в INGEST корень
- §0.11 ОБЯЗАТЕЛЬНАЯ САМОПРОВЕРКА AI: добавлена в канон
- Drive folder isolation: артефакты только в chat_{id}/topic_{id}/
