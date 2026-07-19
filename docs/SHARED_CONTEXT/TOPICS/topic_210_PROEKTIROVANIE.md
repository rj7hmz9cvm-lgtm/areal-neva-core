# topic_210 PROEKTIROVANIE

GENERATED_AT: 2026-07-19T22:15:02.141466+00:00
GIT_SHA: b6695c31d7f14dd4fa3950508fe6211747215020
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 210
ROLE: КЖ КМ
DIRECTIONS_BOUND: structural_design
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- ARCHIVED: 3
- CANCELLED: 28
- DONE: 88
- FAILED: 32

## LATEST_FAILED
- 4cd74051 | INVALID_RESULT_GATE
- 088df3dc | TASK_WORKER_ARTIFACT_GATE_V1:EMPTY_OR_TOO_SHORT
- dd000985 | TASK_WORKER_ARTIFACT_GATE_V1:EMPTY_OR_TOO_SHORT
- 0332e116 | INVALID_RESULT_GATE
- b98e1117 | TASK_WORKER_ARTIFACT_GATE_V1:EMPTY_OR_TOO_SHORT

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- - topic_2 не тянет проектные образцы topic_210
- - topic_210 не тянет сметные артефакты как результат
- - проверить topic_210: "какие образцы есть по АР/КЖ/КД" должен показать список без создания файла
- - проверить topic isolation: topic_2 не должен показывать КЖ/АР файлы topic_210 без прямого запроса

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 10
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

