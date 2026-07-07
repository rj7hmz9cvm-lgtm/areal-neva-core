# topic_500 VEB_POISK

GENERATED_AT: 2026-07-07T20:55:02.705915+00:00
GIT_SHA: a18e9d3fcefcda933fa2a61a5bb519e566257dde
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 500
ROLE: Интернет-поиск
DIRECTIONS_BOUND: internet_search
CURRENT_STATUS: BROKEN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 11

## DB_STATE_COUNTS
- ARCHIVED: 27
- CANCELLED: 7
- DONE: 86
- FAILED: 56

## LATEST_FAILED
- 936241de | SEARCH_OUTPUT_INVALID_FALSE_VERIFIED
- c3d3b1db | CONFIRMATION_TIMEOUT
- dd14c782 | CONFIRMATION_TIMEOUT
- 631e3a5b | CONFIRMATION_TIMEOUT
- e6eb903f | CONFIRMATION_TIMEOUT

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- created:NEW
- continued:Выполни мне последний поиск снова но с реальными ссы
- continued:Реальными ссылками
- PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1:core_tasks=e97fd869,7369d892,666bdb72
- state:IN_PROGRESS
- state:FAILED
- reply_sent:invalid_result
- PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1:core_tasks=e97fd869,5fbffec4,a0737581
- PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1:core_tasks=8eaf56f3,e97fd869,5fbffec4
- P6_TOPIC500_DIRECT_SEARCH_MONOLITH_ROUTE
- P6_TOPIC500_SEARCH_AWAITING_CONFIRMATION
- TOPIC500_PROCUREMENT_VALIDATOR_V1:FAILED:SEARCH_OUTPUT_INVALID_NO_DIRECT_LINKS
- reply_sent:error
- reply_sent:topic_context_isolation_guard
- TOPIC_CONTEXT_ISOLATION_GUARD_V1:ANSWERED
- STARTUP_RECOVERY_REPLY_SENT_GUARD_V1:TOPIC500_KEEP_AWAITING_CONFIRMATION
- PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1:SKIP_TOPIC500_EXPLICIT_SEARCH
- TOPIC500_PROCUREMENT_VALIDATOR_V1:FAILED:SEARCH_OUTPUT_INVALID_NO_PRICE
- TOPIC500_PROCUREMENT_VALIDATOR_V1:ERROR:error
- reply_sent:p6_topic500_search_result
- result:Найдены исполнители по алмазной резке проемов в монолите (Санкт-Петербург
- TOPIC500_PROCUREMENT_VALIDATOR_V1:ALLOW_UNVERIFIED:SEARCH_OUTPUT_INVALID_NO_DIRE
- reply_sent:result
- FINAL_TOPIC500_SEARCH_DONE_20260504_V1
- created:NEW_RERUN_TOPIC500_CANON_SEARCH
- P6_TOPIC500_CLOSED_STALE_SEARCH_SESSION_BEFORE_RUN
- TOPIC500_PROCUREMENT_VALIDATOR_V1:FAILED:SEARCH_OUTPUT_INVALID_FALSE_VERIFIED
- created:NEW_RERUN_TOPIC500_AFTER_DEEPSEEK_BLOCK
- created:NEW_RERUN_TOPIC500_COREDB_DEDUPE
- ACTIVE_DIALOG_STATE_V1:SHORT_CONTROL_ACTIVE_TASK

## BLOCKERS_FROM_NOT_CLOSED
- (none)

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 1
chats: 1

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=67
- chat_exports files=67

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

