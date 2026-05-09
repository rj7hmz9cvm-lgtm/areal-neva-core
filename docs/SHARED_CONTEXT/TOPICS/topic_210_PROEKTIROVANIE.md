# topic_210 PROEKTIROVANIE

GENERATED_AT: 2026-05-09T00:25:02.160257+00:00
GIT_SHA: c533c40450b8f9b0209795e1aee43eec068022fc
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 210
ROLE: КЖ КМ
DIRECTIONS_BOUND: structural_design
CURRENT_STATUS: INSTALLED_NOT_VERIFIED
ACTIVE_TASKS: 0
FAILED_LAST_24H: 4

## DB_STATE_COUNTS
- ARCHIVED: 3
- CANCELLED: 28
- DONE: 84
- FAILED: 30

## LATEST_FAILED
- dd000985 | TASK_WORKER_ARTIFACT_GATE_V1:EMPTY_OR_TOO_SHORT
- 0332e116 | INVALID_RESULT_GATE
- b98e1117 | TASK_WORKER_ARTIFACT_GATE_V1:EMPTY_OR_TOO_SHORT
- f02f874e | INVALID_RESULT_GATE
- cfadbd05 | INVALID_RESULT_GATE

## COMMITS_LAST_14D
- ca312d9|fix(topic210): pile count route and db lock recover guard
- 9420d6a|fix(topic2): stroyka meta-confirm guard + reply chain + xlsx 15 cols + topic210 meta guard
- a277900|docs(normative): add shared normative context for topic_5 and topic_210

## MARKERS_LAST_24H
- created:NEW
- TOPIC2_STALE_PENDING_BLOCKED:pending_task=test-multifile-g:done=True
- state:IN_PROGRESS
- state:FAILED
- reply_sent:invalid_result
- TOPIC210_RECOVERED_FROM_INVALID_RESULT_GATE_PER_CANON_§0
- TASK_WORKER_ARTIFACT_GATE_V1:FAILED:EMPTY_OR_TOO_SHORT
- clarified:сваи жб 150х150
- reply_sent:memory_query
- FINAL_CLOSURE_MEMORY_QUERY_PUBLIC_OUTPUT_V3:LISTED
- reply_sent:result
- P6F_T210_PROJECT_DRIVE_REFS_RETURNED:7
- continued:Задание я тебе уже писал
- TEST_PILE_ROUTE_V1_CHECK
- reply_sent:topic210_pile_count_route_v1
- PATCH_TOPIC210_PILE_COUNT_ROUTE_V1:HANDLED
- TOPIC210_PILE_COUNT_DONE
- PILE_COUNT_RERUN_AFTER_PATCH_RESTART
- TOPIC210_PILE_DIMENSIONS_REQUIRED
- clarified:смотри все есть
- state:FAILED:EXECUTION_TIMEOUT
- reply_sent:execution_timeout
- PILE_COUNT_RERUN_WITH_TEMPLATE_DIMS_10x8
- TOPIC210_PILE_COUNT_TELEGRAM_DELIVERED:10673

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

