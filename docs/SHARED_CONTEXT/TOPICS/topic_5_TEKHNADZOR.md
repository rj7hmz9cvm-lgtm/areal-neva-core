# topic_5 TEKHNADZOR

GENERATED_AT: 2026-07-05T08:54:45.487310+00:00
GIT_SHA: c9f0a8cfcdf554cf75a2ea09c3afc9e640c91de6
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 5
ROLE: Технадзор
DIRECTIONS_BOUND: technical_supervision
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- ARCHIVED: 21
- CANCELLED: 25
- DONE: 68
- FAILED: 53

## LATEST_FAILED
- 775a2251 | STALE_NEW_30MIN
- f3637754 | STALE_NEW_30MIN
- ddfc12b1 | PATCH_TOPIC2_UNBLOCK_PICK_NEXT_V1_CLOSED_BLOCKER
- 24ffa14f | INVALID_PUBLIC_RESULT
- 8093deb3 | INVALID_PUBLIC_RESULT

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- - topic_5 не тянет КЖ/АР без прямой команды

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 6
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

## OWNER_REFERENCE_REGISTRY
loaded: True
items: 11

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

