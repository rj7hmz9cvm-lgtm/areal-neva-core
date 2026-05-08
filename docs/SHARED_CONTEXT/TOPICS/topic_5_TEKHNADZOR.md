# topic_5 TEKHNADZOR

GENERATED_AT: 2026-05-08T17:50:02.624062+00:00
GIT_SHA: e185e83865a40e0712e8de514a3f56cee666eecb
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 5
ROLE: Технадзор
DIRECTIONS_BOUND: technical_supervision
CURRENT_STATUS: IDLE_NO_FAILURES_NOT_VERIFIED
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
- 7c646dd|session(08.05): bigfile activated, topic5 V3 dispatcher, topic2 P6C intercept, c94ec497 FAILED/NOT_PROVEN
- b3e5be7|fix(topic500): relax bad-result filter for adaptive output modes
- 0d6a9a4|fix(memory): ARCHIVE_DUPLICATE_GUARD_V1 + topic500 search pollution guard
- 3f53d3f|docs(handoff): update after topic500 adaptive output V1
- 0c15037|feat(topic500): adaptive output by intent mode (9 modes, V1)
- 48eed2e|fix(topic5): filter garbage from act — canon §4/§5 material filter
- bb8e971|fix(topic5): fix vision-blocked condition — {} is not None
- fb24e60|fix(topic5): vision-blocked fallback per canon §17 — DOCX from owner text
- 0e01878|fix(topic5): install python-docx + enable vision via EXTERNAL_PHOTO_ANALYSIS_ALLOWED env
- f28a106|fix(topic2/topic500): extend estimate pipeline, offer menu for drive_file, fix search result blocking
- 967c48f|fix(topic_2/topic_5): close logic gaps in smeta, voice, and act routing
- 4aa44eb|fix: close canon contours for topic_5/topic_2/topic_500
- 998b6ff|fix(topic5): require owner instruction for new files
- 6e85335|fix(topic5): route drive files through full canon guard
- 7abefb9|fix(topic5): clean address extraction regex
- 4d8d5d6|fix(topic5): close full technadzor context contour
- 52bf7b5|fix(topic5): continuous active folder packet
- d9eed5e|fix(topic5): move final gate before worker main
- 7e3bb3e|fix(topic5): final no-clarify gate
- 884ea78|fix(topic5): canon close active folder photo package
- 5b01524|fix(topic5): close technadzor photo reply buffer contour
- 80c6690|Revert "fix(topic5): bind bot replies to recent photo materials"
- 837cf22|fix(topic5): bind bot replies to recent photo materials
- 6588a62|Revert "fix(topic5): force telegram files into visit buffer"
- e934209|fix(topic5): force telegram files into visit buffer
- 46234f9|fix(topic5): bind active folder upload and reply voice material comments
- a277900|docs(normative): add shared normative context for topic_5 and topic_210
- 2deb7c8|docs(technadzor): finalize topic5 logic context and document output contract
- 1405fdb|CHAT EXPORT GPT_TOPIC5_FULL_CLOSE 2026-05-05
- ff753aa|feat(technadzor): P6H_PART_4 topic_5 hook + STT hallucination guard

## MARKERS_LAST_24H
- created:NEW
- reply_sent:topic5_reply_photo_comment_bound
- topic5_reply_photo_comment_bound
- reply_sent:topic5_package_status_continuous
- topic5_package_status_continuous
- reply_sent:topic5_final_act
- FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:TOPIC5_FINAL_ACT_GENERATED
- P8T5_SUPERSEDED_BY_CANONICAL_V2
- P8T5_CANCELLED_OLD_GARBAGE_ACT_V2
- TOPIC5_DRIVE_LINKS_SAVED
- TOPIC5_GARBAGE_FILTER_OK
- TOPIC5_ACT_STRUCTURE_OK
- TOPIC5_DEFECT_TABLE_OK
- TOPIC5_RECOMMENDATIONS_SECTION_OK
- TOPIC5_NORMATIVE_SECTION_OK
- TOPIC5_DOCX_CREATED
- TOPIC5_PDF_CREATED
- reply_sent:topic5_canonical_act_v3
- PATCH_TOPIC5_ACT_DISPATCH_V3:ACT_GENERATED

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

