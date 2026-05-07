# topic_2 STROYKA

GENERATED_AT: 2026-05-07T17:50:02.575386+00:00
GIT_SHA: b3e5be73bca451c0ed863454767d568630087479
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 2
ROLE: Сметы
DIRECTIONS_BOUND: estimates
CURRENT_STATUS: INSTALLED_NOT_VERIFIED
ACTIVE_TASKS: 0
FAILED_LAST_24H: 3

## DB_STATE_COUNTS
- ARCHIVED: 12
- CANCELLED: 96
- DONE: 129
- FAILED: 109

## LATEST_FAILED
- a7b2879e | STALE_TIMEOUT
- 893436d4 | INVALID_PUBLIC_RESULT
- f43100b3 | TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_ERR:maximum recursion depth exceeded
- c6b40dfc | STROYKA_QG_FAILED:XLSX_VALIDATE_ERROR:maximum recursion depth exceeded
- 8212f685 | STALE_TIMEOUT

## COMMITS_LAST_14D
- 48f9858|docs(handoff): update latest handoff after topic2 and aggregator guard
- c0300fb|fix(topic2): close 4 code gaps — enrichment markers, cyrillic marker, function-object bug, FCG bypass
- 2ece9eb|fix(topic2): close 3 live bugs — poison loop terminate, recursion restore, FCG done bypass
- 62d85b8|fix(topic2): V5B — price source quality gate, raw JSON guard, canonical totals col J
- 168ce5e|fix(topic2): close final V5 code gaps for prices guards totals
- 983ced8|fix(topic2): close 3 remaining V4 gaps (repeat/negative/pdf_missing_question)
- 2353fc3|fix(topic2): close remaining project/pdf/photo/price/artifact gaps V4
- ccab9ed|fix(topic2): PATCH_TOPIC2_FULL_CLOSE_RUNTIME_V3 — all 9 requirements
- 055157b|fix(topic2): PATCH_TOPIC2_FULL_CLOSE_RUNTIME_V2
- ad829c4|fix(topic2): PATCH_TOPIC2_FULL_CANONICAL_CLOSE_ONEPASS_V1 — §9 output + recursion fix
- c7c8755|fix(topic2): inline-fix V1 — replace dead wrappers with body edits
- d1f20a0|fix(topic2): full mega-guards V1 — 6 guards закрытие topic_2 acceptance bugs
- 9420d6a|fix(topic2): stroyka meta-confirm guard + reply chain + xlsx 15 cols + topic210 meta guard
- 58d33aa|fix(topic2): stop T2RFP infinite redirect loop for drive_file re-picks
- b17bca2|fix(topic2): stop WAITING_CLARIFICATION pick loop
- 2ef3f86|fix(topic2): price reply thread isolation + chat-aware price search
- a054796|feat(topic2): canonical template selection, 15-col XLSX, status guard
- 79ba839|fix(topic2): redirect simplified v2 path to full P2/P3 pipeline
- 66a57e1|fix(topic2): route ALL estimates through full P2/P3 pipeline
- d9edd5d|fix(topic2): auto price enrichment + DONE contract markers
- 842c52b|docs(topic2): update chat export for stroyka price choice patch
- ac58cfe|docs(topic2): add 20260506 stroyka in progress report
- 7a9bc69|docs(topic2): add 20260506 stroyka not closed report
- 20020d1|docs(topic2): add 20260506 stroyka price flow handoff
- a27c1ea|CHAT EXPORT topic2_stroyka_price_choice_patch 2026-05-06
- 91b2753|fix(topic2): close stroyka estimate canon runtime contract
- a6df8c0|fix(topic2): extend price confirmation phrases + pending estimate TTL to 24h
- 7b4a634|fix(topic2): fix P6 estimate/vague detection for implicit estimate requests
- b466fa9|fix(topic2): inject historical DONE/FAILED/CANCELLED context into estimate pipeline
- 4d43c1a|fix(sample_template_engine): context enrich + implicit scope for thin topic2 inputs

## MARKERS_LAST_24H
- created:NEW
- clarified:Сделай пожалуйста по полученному заданию
- clarified:У тебя есть размеры дома
- clarified:ну что?
- clarified:
- clarified:Каркас там же написано
- clarified:Возьми это как новый техзадании
- clarified:Ну что ты по двум задачам мне сделаешь или нет
- clarified:2
- clarified:Да жду
- cancelled
- clarified:Отмена задач говорю
- clarified:Необходимо сделать подробную смету с расчётом стоимости материалов по 
- clarified:фундамент
- clarified:У меня же написано всё
- clarified:Все задачи завершены
- clarified:Отбой всех задач
- clarified:отмена всех задач
- TOPIC2_PRICE_CHOICE_CONFIRMED:median
- P3_TOPIC2_CLARIFICATION
- TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_ERR:maximum recursion depth exceeded
- PATCH_TOPIC2_FRESH_ESTIMATE_ROUTE_GUARD_V1:CANON_FALLBACK:BYPASS_P6E67_PARENT_LO
- FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:estimate_generated
- P6E67_PARENT_REVIVED_AS_REVISION_SOURCE:EXACT_REPLY_LINK
- P6E67_REVISION_TEXT_MERGED_FROM_TASK:ee3984f3-4e34-4b62-8512-430b24127d34
- P6E67_CURRENT_TASK_CANCELLED_MERGED_TO_PARENT:c661ab5e-9555-4358-b06f-2301c06310
- P6E67_PARENT_REVIVED_AS_REVISION_SOURCE:LAST_ACTIVE_ESTIMATE_FALLBACK
- P6E67_REVISION_TEXT_MERGED_FROM_TASK:c661ab5e-9555-4358-b06f-2301c06310d1
- P6E67_CURRENT_TASK_CANCELLED_MERGED_TO_PARENT:893436d4-72d2-4bdf-b362-f40d722657
- continued:Покажи мне мой запрос на который ты это посчитал что это был за запрос

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
- TOPIC2_PRICE_ENRICHMENT_DONE
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

