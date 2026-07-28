# topic_2 STROYKA

GENERATED_AT: 2026-07-28T05:30:02.436775+00:00
GIT_SHA: 4d8c40d738ac9674e11ee7dc94dbecc8a3e2ef1d
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 2
ROLE: Сметы
DIRECTIONS_BOUND: estimates
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 1

## DB_STATE_COUNTS
- ARCHIVED: 12
- CANCELLED: 157
- DONE: 257
- FAILED: 169

## LATEST_FAILED
- d019c976 | STROYKA_QG_FAILED:TOO_FEW_ITEMS:0
- 128047d6 | STALE_TIMEOUT
- 59424786 | NO_VALID_ARTIFACT
- ad69b7c1 | STALE_TIMEOUT
- 341cde94 | STALE_TIMEOUT

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- created:NEW
- PATCH_TOPIC2_FRESH_FULL_TZ_CANON_ROUTE_V1:CANON_P3_ROUTE
- TOPIC2_ESTIMATE_CONTEXT_HASH:7e3f8dfd5382d959
- TOPIC2_PRICE_ENRICHMENT_STARTED
- TOPIC2_PRICE_CHOICE_REQUESTED
- PATCH_TOPIC2_ACTIVE_PROJECT_BLOCK_MEMORY_RECALL_V1:SKIP_MEMORY_RECALL_ACTIVE_PRO
- TOPIC2_PRICE_CHOICE_CONFIRMED:reliable
- PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:CHOICE_BOUND_FROM:8be95000-3319-4fdb-b0a
- PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:MERGED_TO:d019c976-5e46-475d-bcd7-c9f349
- PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_FINAL_GATE_V1:SEARCH:щебень,опалубка,армир
- TOPIC2_PRICE_CACHE_BEFORE_SONAR:gravel
- TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Щебень для основания фундаментной плиты
- TOPIC2_PRICE_SOURCE_FOUND:gravel:Гравелит:CONFIRMED
- TOPIC2_MISSING_PRICE_CACHE_SONAR_DONE:gravel
- TOPIC2_PRICE_CACHE_BEFORE_SONAR:formwork_material
- TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Опалубка для монолитной фундаментной плиты 
- TOPIC2_PRICE_SOURCE_FOUND:formwork_material:spb.opalubka.market:PARTIAL
- TOPIC2_PRICE_CACHE_BEFORE_SONAR:formwork_work
- TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Монтаж демонтаж опалубки фундаментной плиты
- TOPIC2_PRICE_SOURCE_FOUND:formwork_work:Ds Structures:CONFIRMED
- TOPIC2_PRICE_CACHE_BEFORE_SONAR:rebar_work
- TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Армирование фундаментной плиты работы
- clarified:Отменяю задачу
- TOPIC2_PRICE_SOURCE_FOUND:rebar_work:fundament-spb.com:CONFIRMED
- TOPIC2_PRICE_CACHE_BEFORE_SONAR:sand_work
- TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Устройство песчаной подушки с послойным упл
- continued:Отмена задачи
- cancelled
- TOPIC2_PRICE_SOURCE_FOUND:sand_work:Фундамент98:CONFIRMED
- TOPIC2_PRICE_CACHE_BEFORE_SONAR:gravel_work

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
total_files: 116
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
- TOPIC2_TEMPLATE_SELECTED
- TOPIC2_PRICE_ENRICHMENT_DONE
- TOPIC2_LOGISTICS_CONFIRMED
- TOPIC2_XLSX_CREATED
- TOPIC2_PDF_CREATED
- TOPIC2_PDF_CYRILLIC_OK
- TOPIC2_DRIVE_UPLOAD_XLSX_OK
- TOPIC2_DRIVE_UPLOAD_PDF_OK
- TOPIC2_TELEGRAM_DELIVERED
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

