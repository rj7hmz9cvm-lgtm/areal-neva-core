# LATEST_HANDOFF — 30.04.2026 04:45 MSK

## СЕРВЕР
IP: 89.22.225.136 | Base: /root/.areal-neva-core
Services: areal-task-worker ACTIVE | telegram-ingress ACTIVE | areal-memory-api ACTIVE

## ПАТЧИ СЕССИИ 30.04.2026 — ФИНАЛЬНЫЙ СТАТУС

| Патч | Файл | Статус |
|---|---|---|
| PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL | task_worker.py | VERIFIED ✅ |
| PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_WORKER_PICK_BEFORE_STALE_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FIX_PFIN3_MENU_SHADOW_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FILE_CHOICE_PRIORITY_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FILE_PARENT_STRICT_OPEN_ONLY_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_ENGINE_BASE_RESTORE_SA_UPLOAD_V1 | core/engine_base.py | VERIFIED ✅ |
| PATCH_DRIVE_DIRECT_OAUTH_V1 | core/engine_base.py | VERIFIED ✅ |
| PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_DOWNLOAD_OAUTH_V1 | task_worker.py | INSTALLED |
| PATCH_SOURCE_GUARD_V1 | task_worker.py | INSTALLED |
| PATCH_FILE_ERROR_RETRY_V1 | task_worker.py | INSTALLED |
| PATCH_RETRY_TOPIC_FOLDER_V1 | core/upload_retry_queue.py | VERIFIED ✅ |
| PATCH_HC_NO_UPLOAD | core/upload_retry_queue.py | INSTALLED |
| PATCH_DUPLICATE_GUARD_V1 | task_worker.py | INSTALLED |
| PATCH_MULTI_FILE_INTAKE_V1 | task_worker.py | INSTALLED |
| PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1 | task_worker.py | INSTALLED |
| §0.11 САМОПРОВЕРКА AI | docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md | VERIFIED ✅ |

## НОВЫЕ ПРАВИЛА (30.04.2026 финал)

### Source Guard
Файлы не из Telegram (source != "telegram") → CANCELLED автоматически.
Системный мусор из google_drive ingest не попадает в чаты.
Патч: PATCH_SOURCE_GUARD_V1 в _handle_drive_file.

### File Error Retry
Reply на сообщение с ошибкой → автоматический перезапуск файла.
Пользователь не должен повторно кидать файл.
Патч: PATCH_FILE_ERROR_RETRY_V1 в _handle_new.

### Download OAuth
_download_from_drive использует OAuth а не Service Account.
Service Account не имеет доступа к My Drive пользователя.
Патч: PATCH_DOWNLOAD_OAUTH_V1.

### Drive Folder Isolation
Артефакты только в: AI_ORCHESTRA/chat_{chat_id}/topic_{topic_id}/
Retry queue использует topic_drive_oauth._upload_file_sync.
Healthcheck НЕ создаёт файлы в Drive (только list API).

## НЕ ЗАКРЫТО — P1

- Голосовой confirm при AWAITING_CONFIRMATION (telegram_daemon.py:601)
- PATCH_DOWNLOAD_OAUTH_V1 — INSTALLED, live-тест не проводился
- PATCH_SOURCE_GUARD_V1 — INSTALLED, live-тест не проводился
- PATCH_FILE_ERROR_RETRY_V1 — INSTALLED, live-тест не проводился
- PATCH_DUPLICATE_GUARD_V1 — live-тест не проводился
- PATCH_MULTI_FILE_INTAKE_V1 — live-тест не проводился
- PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1 — live-тест не проводился

## НЕ ЗАКРЫТО — P2

- Смета PDF → Excel → Drive end-to-end
- КЖ PDF pipeline
- project_engine end-to-end
- Gemini vision
- Excel формулы =C2*D2 / =SUM
- Нормы СП/ГОСТ
- Multi-file один артефакт
- Google Sheets интеграция
- Шаблоны end-to-end
- MODEL_ROUTER, FALLBACK_CHAIN
