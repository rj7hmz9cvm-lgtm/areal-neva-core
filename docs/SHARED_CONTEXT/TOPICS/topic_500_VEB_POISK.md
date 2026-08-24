# topic_500 VEB_POISK

GENERATED_AT: 2026-08-24T19:24:56.407032+00:00
GIT_SHA: fe958c03ec8079e8192faf1a32378967610df1f9
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 500
ROLE: Интернет-поиск
DIRECTIONS_BOUND: internet_search
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 1

## DB_STATE_COUNTS
- ARCHIVED: 27
- CANCELLED: 8
- DONE: 87
- FAILED: 57

## LATEST_FAILED
- 0e670fb0 | SEARCH_OUTPUT_INVALID_NO_DIRECT_LINKS
- 936241de | SEARCH_OUTPUT_INVALID_FALSE_VERIFIED
- c3d3b1db | CONFIRMATION_TIMEOUT
- dd14c782 | CONFIRMATION_TIMEOUT
- 631e3a5b | CONFIRMATION_TIMEOUT

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- created:NEW
- state:IN_PROGRESS
- result:Да, в теме. 

Текущие данные по алмазной резке в СПб и ЛО:

1. **"АлмазСт
- TOPIC500_PROCUREMENT_VALIDATOR_V1:FAILED:SEARCH_OUTPUT_INVALID_NO_DIRECT_LINKS
- reply_sent:error
- PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1:SKIP_TOPIC500_EXPLICIT_SEARCH
- P6_TOPIC500_DIRECT_SEARCH_MONOLITH_ROUTE
- P6_TOPIC500_CLOSED_STALE_SEARCH_SESSION_BEFORE_RUN
- P6_TOPIC500_SEARCH_AWAITING_CONFIRMATION
- reply_sent:p6_topic500_search_result
- ACTIVE_DIALOG_STATE_V1:SHORT_CONTROL_ACTIVE_TASK
- cancelled

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

