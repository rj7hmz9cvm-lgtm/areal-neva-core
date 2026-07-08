# topic_2 STROYKA

GENERATED_AT: 2026-07-08T13:30:02.788709+00:00
GIT_SHA: 028454d4f248d234cd9f22a64957b82c44c3764e
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 2
ROLE: Сметы
DIRECTIONS_BOUND: estimates
CURRENT_STATUS: INSTALLED_NOT_VERIFIED
ACTIVE_TASKS: 0
FAILED_LAST_24H: 5

## DB_STATE_COUNTS
- ARCHIVED: 12
- CANCELLED: 154
- DONE: 247
- FAILED: 166

## LATEST_FAILED
- ad69b7c1 | STALE_TIMEOUT
- 341cde94 | STALE_TIMEOUT
- 5e523179 | STALE_TIMEOUT
- 9d7440b6 | STALE_TIMEOUT
- e65b555f | STALE_TIMEOUT

## COMMITS_LAST_14D
- 95e659fb|Save 2026-07-07 topic2 search live session
- c4473391|docs: save 2026-07-07 topic2 search ocr handoff
- ed4c3c7b|topic2: append live rules and save repair state
- f5f758c8|docs: refresh single model context after topic2 handoff
- d690605f|topic2: save canonical live repair handoff
- 844fafb2|topic2: close PDF estimate confirmation flow
- c8a9f1c6|Topic2 canonical estimate live repair

## MARKERS_LAST_24H
- created:NEW
- clarified:Все что у меня есть я тебе отправил
- clarified:Да, считать по найденным проектным позициям. Цены на материалы, изгото
- clarified:да
- clarified:3
- clarified:1
- clarified:Это же ангар это видно из проекта а там один этаж зачем ты спрашиваешь
- clarified:Всё есть технической документации
- PATCH_TOPIC2_ACTIVE_PROJECT_BLOCK_MEMORY_RECALL_V1:SKIP_MEMORY_RECALL_ACTIVE_PRO
- TOPIC2_DONE_ONLY_AFTER_USER_YES_V1:BLOCKED_DONE_TO_AWAITING_CONFIRMATION
- TOPIC2_PUBLIC_RESULT_CANON_VIOLATION:missing_canon_header
- PATCH_TOPIC2_HISTORICAL_PROJECT_MEMORY_RECALL_V1:core_task=287a613c-c47d-4fae-9a
- TOPIC2_REPEAT_PARENT_TASK:287a613c-c47d-4fae-9a71-d57fa3f2b762
- FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:clarification
- TOPIC2_CANONICAL_REROUTE_V2:CANONICAL_HANDLED
- clarified:Отмена задач
- TOPIC2_CANONICAL_REROUTE_V2:FALLBACK_TO_OLD_PIPELINE
- P3_TOPIC2_CLARIFICATION
- clarified:Отмена завершая задачу
- cancelled
- TOPIC2_FRUSTRATION_REPLY_REROUTED:from=229c5e93-a610-4b0f-8ad0-b5c2b14b407c:text
- TOPIC2_FRUSTRATION_REPLY_GUARD_V1:merged_to:b5fa5fbc-a33a-4943-82a8-a9aba939e728
- TOPIC2_FRUSTRATION_REPLY_REROUTED:from=83f43cd4-4d12-4192-978b-462f7ad556a5:text
- TOPIC2_CLARIFICATION_MERGE_V2_SKIPPED_FOR_FRESH_FULL_TZ
- clarified:Отмена говорю всё завершить перестань
- clarified:Ебанат блядь всё отмена
- LIVE_TEST_TOPIC2_BUNDLE_CREATED_BY_CODEX
- TOPIC2_MULTIFILE_PROJECT_OCR_STATUS_SENT
- TOPIC2_MULTIFILE_PROJECT_PDF_ATTACHED:Раздел 4 - КР.pdf
- TOPIC2_MULTIFILE_PROJECT_SPEC_ROWS:Раздел 4 - КР.pdf:18

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
total_files: 62
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
- TOPIC2_PRICE_CHOICE_CONFIRMED
- TOPIC2_LOGISTICS_CONFIRMED
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

