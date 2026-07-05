# topic_2 STROYKA

GENERATED_AT: 2026-07-05T18:52:22.424013+00:00
GIT_SHA: 89c6bd9d7d6faabb6d8ad2d726b2667082f15f6f
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 2
ROLE: Сметы
DIRECTIONS_BOUND: estimates
CURRENT_STATUS: INSTALLED_NOT_VERIFIED
ACTIVE_TASKS: 0
FAILED_LAST_24H: 7

## DB_STATE_COUNTS
- ARCHIVED: 12
- CANCELLED: 141
- DONE: 199
- FAILED: 143

## LATEST_FAILED
- 7dab7ad1 | STALE_TIMEOUT
- 9c5946d7 | STALE_TIMEOUT
- ea794751 | NO_VALID_ARTIFACT
- 16b3b2e6 | STALE_TIMEOUT
- dfdc5ca5 | STALE_TIMEOUT

## COMMITS_LAST_14D
- 844fafb|topic2: close PDF estimate confirmation flow
- c8a9f1c|Topic2 canonical estimate live repair

## MARKERS_LAST_24H
- created:NEW
- clarified:8х12
- clarified:монолит 200 мм
- clarified:под ключ
- clarified:вот
- clarified:
- rejected:WAITING_CLARIFICATION
- clarified:Ты не слушал моё голосовое
- clarified:2
- clarified:вот задание
- continued:2
- cancelled
- TOPIC2_ADDITIONAL_FACT_MERGED:76183052-f0b9-4444-8759-6d622bcab980
- TOPIC2_ADDITIONAL_FACTS_RECALC_STARTED:76183052-f0b9-4444-8759-6d622bcab980
- TOPIC2_RECALC_CONTEXT_INCLUDES_FACT:пол
- TOPIC2_RECALC_CONTEXT_INCLUDES_FACT:стен
- TOPIC2_RECALC_CONTEXT_INCLUDES_FACT:брус
- TOPIC2_RECALC_CONTEXT_INCLUDES_FACT:перекрыти
- TOPIC2_RECALC_CONTEXT_INCLUDES_FACT:фундамент
- P6_TOPIC2_CURRENT_ESTIMATE_ROUTE
- TOPIC2_ESTIMATE_CONTEXT_HASH:f861303f9bb60f5d
- TOPIC2_PRICE_ENRICHMENT_STARTED
- TOPIC2_PRICE_CHOICE_REQUESTED
- TOPIC2_PRICE_CHOICE_CONFIRMED:max
- PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:CHOICE_BOUND_FROM:7cd5daee-d97d-4dc1-965
- PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:MERGED_TO:8c55479a-65cb-4ce1-bd58-f9f9c0
- PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:PARENT_RAW_ENRICHED
- PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DRIVE_FINAL_START
- TOPIC2_PUBLIC_RESULT_CANON_VIOLATION:missing_canon_header
- TOPIC2_ESTIMATE_FINAL_CLOSE_V2:ESTIMATE_ARTIFACTS_CREATED

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

