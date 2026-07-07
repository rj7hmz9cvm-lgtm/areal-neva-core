# topic_500 VEB_POISK

GENERATED_AT: 2026-07-07T15:23:49.755085+00:00
GIT_SHA: 56f547b832afc35c6060dc473bef239b1cf1ac0e
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 500
ROLE: Интернет-поиск
DIRECTIONS_BOUND: internet_search
CURRENT_STATUS: BROKEN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 21

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
- state:IN_PROGRESS
- P6_TOPIC500_DIRECT_SEARCH_MONOLITH_ROUTE
- continued:Выполни мне последний поиск снова но с реальными ссы
- continued:Реальными ссылками
- P6_TOPIC500_SEARCH_AWAITING_CONFIRMATION
- reply_sent:p6_topic500_search_result
- revision_accepted
- state:DONE
- reply_sent:revision_ok
- STARTUP_RECOVERY_REPLY_SENT_GUARD_V1:TOPIC500_KEEP_AWAITING_CONFIRMATION
- reply_sent:reply_repeat_parent
- REPLY_REPEAT_PARENT_TASK_V1:ACK:a0737581
- MANUAL_CANON_MARK_FAILED_FALSE_VERIFIED_LINKS
- created:NEW:TOPIC500_RERUN_AFTER_FALSE_LINK_GUARD
- created:NEW:TOPIC500_RERUN_AFTER_ROUTE_VALIDATOR
- P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
- reply_sent:p6_topic500_bad_result
- TOPIC500_PROCUREMENT_VALIDATOR_V1:FAILED:SEARCH_OUTPUT_INVALID_FALSE_VERIFIED
- reply_sent:error
- MANUAL_REQUEUE_TOPIC500_CLEAR_BOT_MESSAGE_AFTER_UNIVERSAL_SEARCH_CANON_FIX
- CREATED_AS_NEW_TOPIC500_LIVE_RERUN_AFTER_SEARCH_CANON_FIX
- TOPIC500_PROCUREMENT_VALIDATOR_V1:FAILED:SEARCH_OUTPUT_INVALID_UNVERIFIED_SOCIAL
- CREATED_AS_NEW_TOPIC500_LIVE_RERUN_AFTER_SOCIAL_STATUS_VALIDATOR_FIX
- P0_RUNTIME_TOPIC500_DIRECT_SEARCH_ROUTE_V1
- P0_RUNTIME_TOPIC500_SEARCH_DONE_V1
- reply_sent:p0_topic500_search_result
- TOPIC500_PROCUREMENT_VALIDATOR_V1:FAILED:SEARCH_OUTPUT_INVALID_NO_DIRECT_LINKS
- TOPIC500_PROCUREMENT_VALIDATOR_V1:ERROR:error
- topic500_done_command_accepted

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

