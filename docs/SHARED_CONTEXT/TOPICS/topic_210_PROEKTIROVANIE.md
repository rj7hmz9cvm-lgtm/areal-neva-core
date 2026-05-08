# topic_210 PROEKTIROVANIE

GENERATED_AT: 2026-05-08T23:40:02.732392+00:00
GIT_SHA: 00af427ad88d1bb346aff4b7dd986acf47f8d250
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 210
ROLE: КЖ КМ
DIRECTIONS_BOUND: structural_design
CURRENT_STATUS: INSTALLED_NOT_VERIFIED
ACTIVE_TASKS: 0
FAILED_LAST_24H: 1

## DB_STATE_COUNTS
- ARCHIVED: 3
- CANCELLED: 28
- DONE: 81
- FAILED: 27

## LATEST_FAILED
- f02f874e | INVALID_RESULT_GATE
- cfadbd05 | INVALID_RESULT_GATE
- b71a685b | INVALID_RESULT_GATE
- 6e34406d | NO_VALID_ARTIFACT
- eba6dc80 | NO_VALID_ARTIFACT

## COMMITS_LAST_14D
- 9420d6a|fix(topic2): stroyka meta-confirm guard + reply chain + xlsx 15 cols + topic210 meta guard
- a277900|docs(normative): add shared normative context for topic_5 and topic_210
- bc58444|COMBINED_TOPIC2_AND_TOPIC210_CLOSE_V1: real topic2 estimate and cad section fix

## MARKERS_LAST_24H
- created:NEW
- TOPIC2_STALE_PENDING_BLOCKED:pending_task=test-multifile-g:done=True
- state:IN_PROGRESS
- state:FAILED
- reply_sent:invalid_result

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

