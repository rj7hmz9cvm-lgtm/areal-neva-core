# topic_2 STROYKA

GENERATED_AT: 2026-07-06T07:52:42.656452+00:00
GIT_SHA: 20c42a8cf2dbf4520e1f5516b596fa1753c5895f
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 2
ROLE: Сметы
DIRECTIONS_BOUND: estimates
CURRENT_STATUS: INSTALLED_NOT_VERIFIED
ACTIVE_TASKS: 1
FAILED_LAST_24H: 5

## DB_STATE_COUNTS
- ARCHIVED: 12
- AWAITING_CONFIRMATION: 1
- CANCELLED: 143
- DONE: 207
- FAILED: 143

## LATEST_FAILED
- bd0d5ae1 | STALE_TIMEOUT
- 9c5946d7 | STALE_TIMEOUT
- ea794751 | NO_VALID_ARTIFACT
- 16b3b2e6 | STALE_TIMEOUT
- dfdc5ca5 | STALE_TIMEOUT

## COMMITS_LAST_14D
- f5f758c|docs: refresh single model context after topic2 handoff
- d690605|topic2: save canonical live repair handoff
- 844fafb|topic2: close PDF estimate confirmation flow
- c8a9f1c|Topic2 canonical estimate live repair

## MARKERS_LAST_24H
- created:NEW
- continued:1
- MANUAL_RESTART_AS_NEW_FROM_PDF:29331db4-0403-4a5b-8516-88e535202da6
- continued:Необходимо посчитать проект. Проект находится в 100 километров от Санк
- continued:дду
- cancelled
- PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:STALE_PRICE_AND_RESULT_MARKERS_RESET
- clarified:посчитать работы и материалы согласно проекта
- PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_CHILD:5a9afade-f25d-466e-8dc7-
- PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1:MERGED_TO_PARENT:dfdc5ca5-7bb3-48c8-8
- TOPIC2_REPEAT_PARENT_TASK:a82cfa53-b9a6-467e-935c-3e98e1f5d605
- FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:clarification
- TOPIC2_CANONICAL_REROUTE_V2:CANONICAL_HANDLED
- TOPIC2_REVISION_BOUND_TO_PARENT:2
- clarified:вот проект
- TOPIC2_REPEAT_PARENT_TASK:dfdc5ca5-7bb3-48c8-8d66-1b79d279312e
- clarified:Всё есть в проекте
- clarified:Металлоконструкция
- TOPIC2_MISSING_GATE_ANTILOOP_BLOCKED_DEFAULTS:count=3
- state:FAILED
- reply_sent:stale_failed
- TOPIC2_MISSING_GATE_ANTILOOP_BLOCKED_DEFAULTS:count=4
- clarified:Отмена задач
- TOPIC2_CANONICAL_REROUTE_V2:FALLBACK_TO_OLD_PIPELINE
- P3_TOPIC2_FINAL_AWAITING_CONFIRMATION_ROWS_20_PRICE_APPLIED_4
- P3_TOPIC2_FINAL_DONE_ROWS_20_PRICE_APPLIED_4
- TOPIC2_DONE_ONLY_AFTER_USER_YES_V1:P3_FINAL_WAITING_CONFIRMATION
- TOPIC2_ONE_BIG_FINAL_PIPELINE_V1:superseded_by:489cfefe-3048-4056-8362-2dfc90a31
- PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1:TG_EDIT:OK
- PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1:SONAR_SEARCH_OK:8

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
- TOPIC2_ESTIMATE_SESSION_CREATED
- TOPIC2_CONTEXT_READY
- TOPIC2_LOGISTICS_CONFIRMED
- TOPIC2_XLSX_CREATED
- TOPIC2_MESSAGE_THREAD_ID_OK
- TOPIC2_DONE_CONTRACT_OK

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

