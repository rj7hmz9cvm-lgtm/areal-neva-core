# LATEST_HANDOFF — 30.04.2026 04:15 MSK

## СЕРВЕР
IP: 89.22.225.136 | Base: /root/.areal-neva-core
Services: areal-task-worker ACTIVE | telegram-ingress ACTIVE | areal-memory-api ACTIVE

## ПАТЧИ СЕССИИ 30.04.2026 — ФИНАЛЬНЫЙ СТАТУС

| Патч | Файл | Статус |
|---|---|---|
| CONTEXT_AGGREGATOR_V2 | tools/context_aggregator.py | VERIFIED ✅ |
| PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL | task_worker.py | VERIFIED ✅ |
| PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_WORKER_PICK_BEFORE_STALE_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FIX_PFIN3_MENU_SHADOW_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FILE_CHOICE_PRIORITY_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FILE_PARENT_STRICT_OPEN_ONLY_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_ENGINE_BASE_RESTORE_SA_UPLOAD_V1 | core/engine_base.py | VERIFIED ✅ |
| PATCH_DRIVE_DIRECT_OAUTH_V1 | core/engine_base.py | VERIFIED ✅ |
| PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_DUPLICATE_GUARD_V1 | task_worker.py | INSTALLED |
| PATCH_MULTI_FILE_INTAKE_V1 | task_worker.py | INSTALLED |
| PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1 | task_worker.py | INSTALLED |
| upload_retry_queue.py | core/ | VERIFIED ✅ |
| core/telegram_artifact_fallback.py | создан | VERIFIED ✅ |
| core/duplicate_guard.py | создан | INSTALLED |
| core/multi_file_intake.py | создан | INSTALLED |
| core/storage_adapter.py | создан | INSTALLED |
| core/storage_healthcheck.py | создан | INSTALLED |
| core/runtime_cleanup.py | создан | INSTALLED |
| tools/canon_updater.py | создан | INSTALLED |
| Stale test tasks cleanup | data/core.db | DONE ✅ |
| Cron upload_retry_queue 10min | crontab | VERIFIED ✅ |
| Cron storage_healthcheck 30min | crontab | INSTALLED |
| override.conf GDRIVE_REFRESH_TOKEN fix | systemd | VERIFIED ✅ |

## VERIFIED LIVE TESTS (30.04.2026)

- drive_file NEW → NEEDS_CONTEXT → меню по topic_id ✅
- reply/voice choice → FILE_CHOICE_PARSED → IN_PROGRESS ✅
- estimate engine → локальный artifact ✅
- Drive upload → drive.google.com link → UPLOAD_OK ✅
- Telegram fallback → artifact в Telegram если Drive упал ✅
- upload_retry_queue → нашёл TG fallback задачу → скачал → загрузил в Drive → RETRY_UPLOAD_OK ✅
- OAuth app → In Production → refresh_token не протухает ✅
- override.conf → GDRIVE_REFRESH_TOKEN исправлен ✅
- engine_base.py восстановлен из bak → import OK ✅
- FILE_PARENT_STRICT: DONE/CANCELLED tasks не цепляются как parent ✅
- topic_id=0 не берёт file tasks из других топиков ✅
- Stale test tasks cancelled ✅

## НОВЫЕ ПРАВИЛА И АРХИТЕКТУРНЫЕ РЕШЕНИЯ (30.04.2026)

### Drive Upload Architecture
Primary: Direct OAuth (core/engine_base.upload_artifact_to_drive)
Fallback: Telegram sendDocument (core/telegram_artifact_fallback.py)
Retry: upload_retry_queue.py каждые 10 минут восстанавливает Drive upload из TG
Service Account: НЕ используется для My Drive (storageQuotaExceeded)
google_io.py: НЕ используется для upload (drive.file scope)

### File Task Isolation Rules
- file-choice parent lookup только среди state='NEEDS_CONTEXT'
- topic_id=0 (ЧАТ ЗАДАЧ) не берёт file tasks из других топиков без точного reply на bot_message_id
- DONE/CANCELLED/FAILED/AWAITING_CONFIRMATION tasks не цепляются как parent
- Проектные топики (≥200) не реагируют на "проверка/просто проверил" как cancel

### Storage Resilience Pattern
1. Drive upload → если OK → Drive link в result
2. Drive upload → если FAIL → Telegram sendDocument → TELEGRAM_ARTIFACT_FALLBACK_SENT в task_history
3. upload_retry_queue (cron 10min) → Drive alive? → скачать из TG → загрузить в Drive → уведомить пользователя → DRIVE_RETRY_UPLOAD_OK в task_history
4. Сервер НЕ является постоянным хранилищем — артефакты удаляются после выдачи

### Cron Jobs
- tools/context_aggregator.py — каждые 30 минут — обновляет ONE_SHARED_CONTEXT.md
- core/upload_retry_queue.py — каждые 10 минут — retry Drive upload из TG fallback
- core/storage_healthcheck.py — каждые 30 минут — проверяет Drive и уведомляет если сломан

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
- Storage adapter unified layer (storage_adapter.py создан, не интегрирован)
- Universal result guard
- MODEL_ROUTER, FALLBACK_CHAIN
