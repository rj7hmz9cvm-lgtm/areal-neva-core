# LATEST_HANDOFF — 30.04.2026 03:10 MSK

## СЕРВЕР
IP: 89.22.225.136 | Base: /root/.areal-neva-core
Services: areal-task-worker ACTIVE | telegram-ingress ACTIVE | areal-memory-api ACTIVE

## ПАТЧИ СЕССИИ 30.04.2026 — ВСЕ VERIFIED/INSTALLED

| Патч | Файл | Статус |
|---|---|---|
| CONTEXT_AGGREGATOR_V2 | tools/context_aggregator.py | VERIFIED ✅ |
| PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL | task_worker.py | VERIFIED ✅ |
| PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_WORKER_PICK_BEFORE_STALE_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FIX_PFIN3_MENU_SHADOW_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FILE_CHOICE_PRIORITY_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_ENGINE_BASE_RESTORE_SA_UPLOAD_V1 | core/engine_base.py | VERIFIED ✅ |
| PATCH_DRIVE_DIRECT_OAUTH_V1 | core/engine_base.py | VERIFIED ✅ |
| PATCH_DRIVE_OAUTH_PRIMARY_MYDRIVE_V1 | core/engine_base.py | VERIFIED ✅ |
| PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1 | task_worker.py | INSTALLED |
| core/telegram_artifact_fallback.py | создан | INSTALLED |

## VERIFIED LIVE TESTS

- drive_file NEW → NEEDS_CONTEXT → меню по topic_id ✅
- reply/voice choice → FILE_CHOICE_PARSED → IN_PROGRESS ✅
- estimate engine → локальный artifact → "Нормализовано позиций: 32" ✅
- Drive upload → drive.google.com link → UPLOAD_OK ✅
- OAuth app переведён в Production → refresh_token не протухает ✅
- engine_base.py восстановлен из bak → import OK ✅

## ТЕКУЩАЯ АРХИТЕКТУРА DRIVE UPLOAD

1. Primary: Direct OAuth через `core/engine_base.upload_artifact_to_drive`
   - refresh_token из GDRIVE_REFRESH_TOKEN в .env + systemd override
   - НЕ Service Account (storageQuotaExceeded для My Drive)
   - НЕ google_io.py (drive.file scope ограничен)
2. Fallback: `core/telegram_artifact_fallback.send_artifact_to_telegram`
   - sendDocument через Bot API
   - topic_id > 0 → message_thread_id передаётся
   - topic_id == 0 → message_thread_id не передаётся

## OAUTH СТАТУС

- App: areal-neva-automation → **In Production** ✅
- Client: AI_ORCHESTRA_NEW (Desktop)
- GDRIVE_REFRESH_TOKEN: обновлён в .env и systemd override
- Scope: https://www.googleapis.com/auth/drive (полный)
- Папка: AI_ORCHESTRA (13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB) — обычная My Drive

## НЕ ЗАКРЫТО (требует live-теста)

- Полный Telegram file → artifact → Drive link flow (PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1 установлен, тест не проводился)
- Голосовой confirm при AWAITING_CONFIRMATION (P1 баг, telegram_daemon.py:601)
- Смета PDF → Excel → Drive end-to-end
- КЖ PDF pipeline
- project_engine end-to-end через Telegram
- Gemini live-тест
- Multi-file, duplicate guard, memory/pin перед меню

## СЛЕДУЮЩИЙ ШАГ

1. Живой тест: файл без caption → меню → выбор → artifact → Drive link в Telegram
2. Проверить AWAITING_CONFIRMATION → confirm → DONE
3. Зафиксировать результат в NOT_CLOSED.md
