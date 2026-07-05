# topic_500 VEB_POISK

GENERATED_AT: 2026-07-05T09:24:45.648434+00:00
GIT_SHA: cd360d697ffb2dd461e62bf82ace52f3feff4e3c
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 500
ROLE: Интернет-поиск
DIRECTIONS_BOUND: internet_search
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- ARCHIVED: 27
- CANCELLED: 7
- DONE: 55
- FAILED: 34

## LATEST_FAILED
- 6719452a | P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
- 16129a0c | P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
- 58591d8f | IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1
- 7944bb2a | P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
- a6e666e8 | IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

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

