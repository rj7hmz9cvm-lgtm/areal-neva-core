# topic_2 STROYKA

GENERATED_AT: 2026-07-05T17:24:57.966903+00:00
GIT_SHA: 0e17a9baccd6e6ba25b9f1c3cf64d77f99a17be7
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 2
ROLE: Сметы
DIRECTIONS_BOUND: estimates
CURRENT_STATUS: INSTALLED_NOT_VERIFIED
ACTIVE_TASKS: 1
FAILED_LAST_24H: 7

## DB_STATE_COUNTS
- ARCHIVED: 12
- CANCELLED: 141
- DONE: 195
- FAILED: 142
- WAITING_CLARIFICATION: 1

## LATEST_FAILED
- 9c5946d7 | STALE_TIMEOUT
- ea794751 | NO_VALID_ARTIFACT
- 16b3b2e6 | STALE_TIMEOUT
- dfdc5ca5 | STALE_TIMEOUT
- 29331db4 | STALE_TIMEOUT

## COMMITS_LAST_14D
- c8a9f1c|Topic2 canonical estimate live repair

## MARKERS_LAST_24H
- created:NEW
- state:FAILED
- reply_sent:stale_failed
- TOPIC2_ADDITIONAL_FACT_MERGED:353f2eb6-e19e-49e4-ad0d-7b23ef00cd0f
- TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:353f2eb6-e19e-49e4-ad0d-7b23ef00cd0f
- TOPIC2_RECALC_CONTEXT_INCLUDES_FACT:пол
- clarified:[VOICE] Выполнил мне расчет в полном соответствии
- PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_CHILD:353f2eb6-e19e-49e4-ad0d-
- PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_TO_PARENT:f2efa5c0-ad58-4273-9
- P6_TOPIC2_CURRENT_ESTIMATE_ROUTE
- TOPIC2_ESTIMATE_CONTEXT_HASH:9f516ee177e44d08
- P3_TOPIC2_CLARIFICATION
- clarified:8х12
- TOPIC2_ESTIMATE_CONTEXT_HASH:8c34bdf4e32c902d
- clarified:монолит 200 мм
- TOPIC2_ESTIMATE_CONTEXT_HASH:dbb1913d9725e303
- clarified:под ключ
- TOPIC2_ESTIMATE_CONTEXT_HASH:59b40179eb08dff4
- clarified:вот
- TOPIC2_ESTIMATE_CONTEXT_HASH:8a9011f40f58498b
- clarified:
- TOPIC2_BAD_DONE_BLOCKED:no_price_choice_confirmed
- rejected:WAITING_CLARIFICATION
- clarified:Ты не слушал моё голосовое
- TOPIC2_ESTIMATE_CONTEXT_HASH:bf8c14d0bdd97a4c
- TOPIC2_ADDITIONAL_FACT_MERGED:f361b792-dbde-f888-2977-397a969e9fa7
- TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:f361b792-dbde-f888-2977-397a969e9fa7
- PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_CHILD:f361b792-dbde-f888-2977-
- TOPIC2_ADDITIONAL_FACT_MERGED:eed091ac-1bb4-42ec-b389-ad356a260192
- TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:eed091ac-1bb4-42ec-b389-ad356a260192

## BLOCKERS_FROM_NOT_CLOSED
- - topic_2 не тянет проектные образцы topic_210
- - topic_210 не тянет сметные артефакты как результат
- - WRONG_FILES_SHOWN_IN_TOPIC_2
- - проверить topic_210: "какие образцы есть по АР/КЖ/КД" должен показать список без создания файла
- - проверить topic_2: "В" и "вариант 2" после выбора цены должны создать XLSX/PDF
- - проверить topic isolation: topic_2 не должен показывать КЖ/АР файлы topic_210 без прямого запроса
- - topic_2: "смету дома 10×12 газобетон монолит 2 этажа 120 км коробка"
- - topic_2: "Доделай мне нормально эту задачу"

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 29
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

## NEXT_REQUIRED_PATCH
PATCH_TOPIC2_FULL_GAP_CLOSE_V4

## OPEN_CONTOURS
- P6E2 photo intercept before canonical
- pdf_spec_extractor.py exists but not connected to canonical flow
- ocr_table_engine.py exists but not connected to topic_2 flow
- per-item materials + works internet price search missing
- TOPIC2_MULTIFILE_PROJECT_CONTEXT_* missing
- TOPIC2_REVISION_BOUND_TO_PARENT missing
- TOPIC2_REPEAT_PARENT_TASK missing
- TOPIC2_AFTER_PRICE_CHOICE_GENERATION_STARTED missing
- TOPIC2_FORBIDDEN_FINAL_RESULT_BLOCKED missing
- TOPIC2_PDF_TOTALS_MATCH_XLSX missing
- live verification pending

## REQUIRED_MARKERS
- TOPIC2_ESTIMATE_SESSION_CREATED
- TOPIC2_CONTEXT_READY
- TOPIC2_TEMPLATE_SELECTED
- TOPIC2_PRICE_ENRICHMENT_DONE
- TOPIC2_PRICE_CHOICE_CONFIRMED
- TOPIC2_LOGISTICS_CONFIRMED
- TOPIC2_XLSX_CREATED
- TOPIC2_PDF_CREATED
- TOPIC2_PDF_CYRILLIC_OK
- TOPIC2_DRIVE_UPLOAD_XLSX_OK
- TOPIC2_DRIVE_UPLOAD_PDF_OK
- TOPIC2_TELEGRAM_DELIVERED
- TOPIC2_MESSAGE_THREAD_ID_OK
- TOPIC2_DONE_CONTRACT_OK

## MARKERS_MISSING
- TOPIC2_TEMPLATE_SELECTED
- TOPIC2_LOGISTICS_CONFIRMED

## REGRESSION_GUARDS
- не возвращать P6E67_PARENT_NOT_FOUND на полное ТЗ
- не возвращать INVALID_PUBLIC_RESULT при наличии markers + Drive ссылок
- не убивать задачи с TOPIC2_PRICE_CHOICE_REQUESTED 30-мин таймаутом
- не плодить новые задачи на короткий ответ 2/да при WAITING_PRICE

## LIVE_VERIFY_COMMANDS
- sqlite3 data/core.db "SELECT id,state FROM tasks WHERE topic_id=2 ORDER BY rowid DESC LIMIT 10"
- journalctl -u areal-task-worker --since '10 minutes ago' | grep -E 'TOPIC2|TPRR|TPTG|TFFE|TDOIP'
- sqlite3 data/core.db "SELECT action FROM task_history WHERE task_id IN (SELECT id FROM tasks WHERE topic_id=2 ORDER BY rowid DESC LIMIT 1)"

## ESTIMATE_TEMPLATE_REGISTRY
loaded: True
- M80 | М-80.xlsx | full_house_estimate_template
- M110 | М-110.xlsx | full_house_estimate_template
- ROOF_FLOORS | крыша и перекр.xlsx | roof_and_floor_estimate_template
- FOUNDATION_WAREHOUSE | фундамент_Склад2.xlsx | foundation_estimate_template
- AREAL_NEVA | Ареал Нева.xlsx | general_company_estimate_template

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

