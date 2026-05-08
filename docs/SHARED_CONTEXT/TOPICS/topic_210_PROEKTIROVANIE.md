# topic_210 PROEKTIROVANIE

GENERATED_AT: 2026-05-08T07:20:02.741100+00:00
GIT_SHA: 3dcb94adb675639f423ecd26617e6c1c2d10ba23
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 210
ROLE: КЖ КМ
DIRECTIONS_BOUND: structural_design
CURRENT_STATUS: IDLE_NO_FAILURES_NOT_VERIFIED
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- ARCHIVED: 3
- CANCELLED: 28
- DONE: 81
- FAILED: 26

## LATEST_FAILED
- cfadbd05 | INVALID_RESULT_GATE
- b71a685b | INVALID_RESULT_GATE
- 6e34406d | NO_VALID_ARTIFACT
- eba6dc80 | NO_VALID_ARTIFACT
- 540a9ccc | INVALID_RESULT_GATE

## COMMITS_LAST_14D
- 9420d6a|fix(topic2): stroyka meta-confirm guard + reply chain + xlsx 15 cols + topic210 meta guard
- a277900|docs(normative): add shared normative context for topic_5 and topic_210
- bc58444|COMBINED_TOPIC2_AND_TOPIC210_CLOSE_V1: real topic2 estimate and cad section fix
- 10036c1|TOPIC_ISOLATION_V1: exclude topic_210_500 from FILE_TECH and restore drive scope

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

