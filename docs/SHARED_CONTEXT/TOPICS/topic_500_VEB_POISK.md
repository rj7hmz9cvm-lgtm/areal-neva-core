# topic_500 VEB_POISK

GENERATED_AT: 2026-07-07T16:23:54.433839+00:00
GIT_SHA: 6720ac212228938db58f80474f167bfefc49159c
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 500
ROLE: Интернет-поиск
DIRECTIONS_BOUND: internet_search
CURRENT_STATUS: BROKEN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 17

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
- state:IN_PROGRESS
- STARTUP_RECOVERY_REPLY_SENT_GUARD_V1:TOPIC500_KEEP_AWAITING_CONFIRMATION
- MANUAL_REQUEUE_TOPIC500_CLEAR_BOT_MESSAGE_AFTER_UNIVERSAL_SEARCH_CANON_FIX
- CREATED_AS_NEW_TOPIC500_LIVE_RERUN_AFTER_SEARCH_CANON_FIX
- P6_TOPIC500_DIRECT_SEARCH_MONOLITH_ROUTE
- P6_TOPIC500_SEARCH_AWAITING_CONFIRMATION
- TOPIC500_PROCUREMENT_VALIDATOR_V1:FAILED:SEARCH_OUTPUT_INVALID_UNVERIFIED_SOCIAL
- reply_sent:error
- CREATED_AS_NEW_TOPIC500_LIVE_RERUN_AFTER_SOCIAL_STATUS_VALIDATOR_FIX
- reply_sent:p6_topic500_search_result
- P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
- reply_sent:p6_topic500_bad_result
- P0_RUNTIME_TOPIC500_DIRECT_SEARCH_ROUTE_V1
- P0_RUNTIME_TOPIC500_SEARCH_DONE_V1
- reply_sent:p0_topic500_search_result
- TOPIC500_PROCUREMENT_VALIDATOR_V1:FAILED:SEARCH_OUTPUT_INVALID_NO_DIRECT_LINKS
- TOPIC500_PROCUREMENT_VALIDATOR_V1:ERROR:error
- state:DONE
- topic500_done_command_accepted
- reply_sent:topic500_done_command
- PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1:core_tasks=e97fd869,7369d892,666bdb72
- state:FAILED
- reply_sent:invalid_result
- PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1:core_tasks=e97fd869,5fbffec4,a0737581
- PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1:core_tasks=8eaf56f3,e97fd869,5fbffec4
- reply_sent:topic_context_isolation_guard
- TOPIC_CONTEXT_ISOLATION_GUARD_V1:ANSWERED

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

