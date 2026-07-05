# topic_0 COMMON

GENERATED_AT: 2026-07-05T05:54:38.325222+00:00
GIT_SHA: 4c51410fac2f83281d0b9bb2ae7976ea15d48985
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 0
ROLE: Общий
DIRECTIONS_BOUND: none
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 1

## DB_STATE_COUNTS
- ARCHIVED: 289
- CANCELLED: 643
- DONE: 207
- FAILED: 2706

## LATEST_FAILED
- 71aa047d | INVALID_RESULT_GATE
- 66b9f841 | INVALID_RESULT_GATE
- 5c19256b | INVALID_RESULT_GATE
- 0de22d01 | PROJECT_LINKS_MISSING
- d65dd41b | CONFIRMATION_TIMEOUT

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- created:NEW
- state:IN_PROGRESS
- result:Система восстановлена и функционирует в штатном режиме. Готов к обработке
- reply_sent:result
- result:Тест после восстановления системы выполнен. Система функционирует в штатн
- result:Тест после восстановления системы AREAL-NEVA ORCHESTRA выполнен. Система 
- state:FAILED
- reply_sent:invalid_result

## BLOCKERS_FROM_NOT_CLOSED
- (none)

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 0
chats: 0

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days

