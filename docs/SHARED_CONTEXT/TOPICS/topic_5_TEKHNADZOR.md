# topic_5 TEKHNADZOR

GENERATED_AT: 2026-07-12T12:50:07.689516+00:00
GIT_SHA: 11c75dd92ae4c631bf57c3ca45558c8d5551b225
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
- DONE: 80
- FAILED: 59

## LATEST_FAILED
- 7300d5f5 | STALE_TIMEOUT
- 2d607bf6 | STALE_TIMEOUT
- 68dceab3 | STALE_TIMEOUT
- e9400bf5 | STALE_TIMEOUT
- 3b365ab1 | STALE_TIMEOUT

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- - topic_5 не тянет КЖ/АР без прямой команды

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 25
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

