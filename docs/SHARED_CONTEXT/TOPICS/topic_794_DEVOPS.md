# topic_794 DEVOPS

GENERATED_AT: 2026-05-09T00:25:02.225738+00:00
GIT_SHA: c533c40450b8f9b0209795e1aee43eec068022fc
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 794
ROLE: Сервер DevOps
DIRECTIONS_BOUND: devops_server
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- DONE: 3
- FAILED: 4

## LATEST_FAILED
- d215f564 | cannot access local variable 'ai_result' where it is not associated with a value
- 0a33135a | cannot access local variable 'ai_result' where it is not associated with a value
- 89eabf76 | cannot access local variable 'ai_result' where it is not associated with a value
- b96f8ca8 | cannot access local variable 'ai_result' where it is not associated with a value

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

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

