# topic_6104 JOB_SEARCH

GENERATED_AT: 2026-05-07T17:50:02.861155+00:00
GIT_SHA: b3e5be73bca451c0ed863454767d568630087479
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 6104
ROLE: Поиск работы
DIRECTIONS_BOUND: job_search
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- CANCELLED: 1
- DONE: 3
- FAILED: 6

## LATEST_FAILED
- f371d22d | INVALID_RESULT_GATE
- 81355bcf | INVALID_RESULT_GATE
- b07ceef8 | FORBIDDEN_PHRASE
- 711bdcd3 | FORBIDDEN_PHRASE
- 32fe5a92 | PROJECT_LINKS_MISSING

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- - P2: topic_6104 архив содержит только JSON метаданные без реального контента

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

