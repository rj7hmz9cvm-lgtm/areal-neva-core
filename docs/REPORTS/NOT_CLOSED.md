# NOT_CLOSED — 30.04.2026

## СЕССИЯ 30.04.2026 — ЗАКРЫТО КОДОМ (VERIFIED)

| Что | Патч | Статус |
|---|---|---|
| drive_file без intent → NEEDS_CONTEXT + меню | PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL | VERIFIED ✅ |
| Worker зависал на _recover_stale_tasks | PATCH_WORKER_PICK_BEFORE_STALE_V1 | VERIFIED ✅ |
| Guard до download | PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1 | VERIFIED ✅ |
| UnboundLocalError _pfin3_menu | PATCH_FIX_PFIN3_MENU_SHADOW_V1 | VERIFIED ✅ |
| Reply choice во всех топиках | PATCH_FILE_CHOICE_PRIORITY_V1 | VERIFIED ✅ |
| engine_base.py отсутствовал | PATCH_ENGINE_BASE_RESTORE_SA_UPLOAD_V1 | VERIFIED ✅ |
| Drive upload через Direct OAuth | PATCH_DRIVE_DIRECT_OAUTH_V1 | VERIFIED ✅ |
| OAuth app → Production (не протухает) | Google Cloud Console | VERIFIED ✅ |

## НЕ ЗАКРЫТО — P1

- Голосовой confirm при AWAITING_CONFIRMATION (telegram_daemon.py:601)
- PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1 — INSTALLED, live-тест не проводился

## НЕ ЗАКРЫТО — P2

- Смета PDF → Excel → Drive end-to-end
- КЖ PDF pipeline
- project_engine end-to-end через Telegram
- Gemini vision live-тест
- Excel формулы =C2*D2 / =SUM
- Нормы СП/ГОСТ в technadzor_engine
- Multi-file комплект
- Duplicate guard
- Memory/pin перед меню
- Link intake через NEEDS_CONTEXT
- Google Sheets интеграция
- Шаблоны end-to-end

## DRIVE UPLOAD АРХИТЕКТУРА (финальная на 30.04)

Primary: Direct OAuth (engine_base.upload_artifact_to_drive)
Fallback: Telegram sendDocument (core/telegram_artifact_fallback.py)
Service Account: НЕ подходит для My Drive (storageQuotaExceeded)
google_io.py: НЕ используется для upload (drive.file scope)

## ПРЕДЫДУЩИЕ НЕ ЗАКРЫТЫЕ (из сессий 28-29.04)

- Дублирование задач x2
- monitor_jobs.py — cron установлен, live-тест не проводился
- SEARCH_MONOLITH_V1 — live-тест не проводился
- Промпт Perplexity в ai_router.py
- MODEL_ROUTER — не реализован
- FALLBACK_CHAIN — не реализован
