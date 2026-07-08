# topic_500 VEB_POISK

GENERATED_AT: 2026-07-08T09:00:02.426251+00:00
GIT_SHA: 810a985820a2bc9485e11c89ff5dcd2ee9d430d6
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 500
ROLE: Интернет-поиск
DIRECTIONS_BOUND: internet_search
CURRENT_STATUS: BROKEN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 5

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
- created:NEW_RERUN_TOPIC500_COREDB_DEDUPE
- PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1:SKIP_TOPIC500_EXPLICIT_SEARCH
- state:IN_PROGRESS
- P6_TOPIC500_DIRECT_SEARCH_MONOLITH_ROUTE
- P6_TOPIC500_CLOSED_STALE_SEARCH_SESSION_BEFORE_RUN
- P6_TOPIC500_SEARCH_AWAITING_CONFIRMATION
- reply_sent:p6_topic500_search_result
- ACTIVE_DIALOG_STATE_V1:SHORT_CONTROL_ACTIVE_TASK
- TOPIC500_CONFIRM_RECOVERY_DONE_FROM_TASK:0a856447-6221-4e6d-9bb6-4ce6caaaed25
- TOPIC500_SUPERSEDED_SEARCH_RESULT_CLOSED_BY_CONFIRMED_RERUN:ad502435-8f05-460b-b
- TOPIC2_META_CONFIRM_NO_CHANGE_GUARD_V1

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

