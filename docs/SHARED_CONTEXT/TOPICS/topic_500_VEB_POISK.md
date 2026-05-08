# topic_500 VEB_POISK

GENERATED_AT: 2026-05-08T22:15:02.814875+00:00
GIT_SHA: fd5778eef413aefddca3bffb0022f25ab810edd2
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 500
ROLE: Интернет-поиск
DIRECTIONS_BOUND: internet_search
CURRENT_STATUS: IDLE_NO_FAILURES_NOT_VERIFIED
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
- b3e5be7|fix(topic500): relax bad-result filter for adaptive output modes
- 0d6a9a4|fix(memory): ARCHIVE_DUPLICATE_GUARD_V1 + topic500 search pollution guard
- 3f53d3f|docs(handoff): update after topic500 adaptive output V1
- 0c15037|feat(topic500): adaptive output by intent mode (9 modes, V1)
- f28a106|fix(topic2/topic500): extend estimate pipeline, offer menu for drive_file, fix search result blocking
- 4aa44eb|fix: close canon contours for topic_5/topic_2/topic_500
- e3d992c|P6G_CLEAN_OLD_TOPIC500_CONTAMINATION_V1: SQL clean task 4883 contamination (point 1 of 5)
- 949c379|P6F_FULL_CODE_CLOSE_REMAINING_CONTOURS_20260504_V1: close revision binding, topic500 sanitizer, photo CV via OpenRouter, TZ params, source labels, technadzor DOCX, project_210 drive, artifact gates
- 709b28a|P3_FINAL_ROUTE_HARD_LOCK_SEARCH_ESTIMATE_20260504_V1: hard-lock topic500 search and topic2 current estimate route
- 4f6af26|P2_FINAL_SEARCH_AND_ESTIMATE_CLOSE_20260504_V1: close topic500 search memory and topic2 final estimate logic
- d4db3fb|P0_RUNTIME_ROUTE_GUARD_TOPIC2_TOPIC500_20260504_V1: block topic500 estimate misroute and force topic2 current estimate route
- bf6cece|TOPIC500_PRE_SEND_VALIDATOR_AND_STARTUP_RECOVERY_HARD_GUARD_V1: pre-send procurement validator and startup recovery hard guard
- dc2f770|FINAL_TOPIC2_TOPIC5_TOPIC500_CLOSE_20260504_V1: close topic2 current TZ route and topic500 search output contract
- a5cdb89|TOPIC2_ESTIMATE_AND_TOPIC500_SEARCH_FULLFIX_V1: strict template estimate pdf and bypass search misroute

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

