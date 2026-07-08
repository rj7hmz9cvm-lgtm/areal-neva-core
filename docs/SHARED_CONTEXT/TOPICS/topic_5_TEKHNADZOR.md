# topic_5 TEKHNADZOR

GENERATED_AT: 2026-07-08T02:26:11.572799+00:00
GIT_SHA: 1fbf56a6e5e2fa945ed75930ff2fe57c3bd51dc2
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 5
ROLE: Технадзор
DIRECTIONS_BOUND: technical_supervision
CURRENT_STATUS: BROKEN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 6

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
- created:NEW
- reply_sent:topic5_reply_photo_comment_bound
- topic5_reply_photo_comment_bound
- PATCH_GLOBAL_HISTORICAL_MEMORY_RECALL_V1:core_tasks=de9a446a,4b402275,8a72d7d1
- FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:UPDATE_BLOCKED:NO_VALID_ARTIFACT
- FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:NO_VALID_ARTIFACT
- reply_sent:full_contour_guard_failed
- reply_sent:P6H4TW_VOICE_ANNOTATED
- P6H4TW_VOICE_ANNOTATED:DONE
- MANUAL_RERUN_AFTER_TOPIC5_VISIT_MATERIAL_GUARD_FIX
- reply_sent:topic5_direct_visit_material_buffered
- PATCH_TOPIC5_DIRECT_VISIT_MATERIAL_DRIVE_FILE_V1:BUFFERED
- reply_sent:topic5_violation_question_answer
- PATCH_TOPIC5_VIOLATION_QUESTION_NOT_COMMENT_V1:HANDLED
- reply_sent:topic5_full_canon_context_saved
- topic5_full_canon_context_saved
- state:FAILED
- reply_sent:stale_failed

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

