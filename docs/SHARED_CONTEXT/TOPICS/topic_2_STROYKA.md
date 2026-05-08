# topic_2 STROYKA

GENERATED_AT: 2026-05-08T22:40:01.844839+00:00
GIT_SHA: 0152cb470622435e66910978b2d1349f2a68bf76
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 2
ROLE: Сметы
DIRECTIONS_BOUND: estimates
CURRENT_STATUS: INSTALLED_NOT_VERIFIED
ACTIVE_TASKS: 1
FAILED_LAST_24H: 11

## DB_STATE_COUNTS
- ARCHIVED: 12
- CANCELLED: 102
- DONE: 134
- FAILED: 120
- WAITING_CLARIFICATION: 1

## LATEST_FAILED
- 6a535d79 | STALE_TIMEOUT
- f9df5eb5 | STALE_TIMEOUT
- test-mul | STALE_TIMEOUT
- 2c732335 | STALE_TIMEOUT
- test-gat | STALE_TIMEOUT

## COMMITS_LAST_14D
- 0152cb4|fix(topic2): TOPIC2_DRAINAGE_PRICE_ENRICHMENT_CANON_FIX_V1
- b07a265|fix(topic2): TOPIC2_DRAINAGE_LENGTH_PROOF_GATE_AND_ONLINE_PRICES_V2
- af42c97|fix(topic2): TOPIC2_DRAINAGE_FULL_CLOSE_NO_LOOP_V2 — child merge guard, legend filter, noise tasks closed
- 859c045|fix(topic2): TOPIC2_DRAINAGE_VAT_GATE_PUBLIC_CLEAN_V1 — VAT gate 22%, source filter, clean public output, Drive upload fix
- 3343690|fix(topic2): TOPIC2_DRAINAGE_MULTIFILE_REPAIR_CLOSE_V1 — close drainage estimate from two PDFs, send XLSX+PDF to Telegram
- 3421216|fix(topic2): gate send fix (dict(task) for sqlite3.Row) + WCG delivery guard on picker cycle
- 80b0809|fix(topic2): PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 — current file source-of-truth gate blocks stale house context for drainage PDF
- 075edf9|fix(topic2): PATCH_TOPIC2_STALE_PENDING_TASK_GUARD_V1 + LOCAL_BOT_API_404_FIX
- e185e83|fix(topic2): PATCH_SUPPLIER_HONESTY_V1 — fix fake Perplexity в Поставщик
- 6cf9154|fix(topic2): PATCH_TOPIC2_ADD_PEREKRYTIYA_SECTION_V1 — add missing §5 Перекрытия section
- 2475eb5|fix(topic2): PATCH_TOPIC2_REALSHEET_PRICES_V3 — real Газобетонный дом prices
- 7c646dd|session(08.05): bigfile activated, topic5 V3 dispatcher, topic2 P6C intercept, c94ec497 FAILED/NOT_PROVEN
- 8760011|fix(topic2): enforce full canonical estimate pipeline without cross-topic regression
- b236f02|fix(topic2): session 08.05 — P6C fulltext prep, P3CHK append fix, P2 distance skip, WCPE unblock
- e3a016c|PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1: hard-enforce Sonar for all price/search calls
- 4cfd9b6|fix(topic2): close P6E67 loop storm + natural reply message
- dc26486|fix(topic2): PATCH_PRICE_REJECT_STORM_FIX_V1 — remove noisy INSERT from V5/V6C rejected path
- 0c8518e|fix(topic2): TOPIC2_FULL_CLOSE — work/material split, sheet fallback, drive links, xlsx 15-col gate
- a216eeb|fix(topic2): PATCH_FCG_V2PATH_BYPASS_V1 — extend FDCB bypass to TOPIC2_DONE_CONTRACT_OK
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

## MARKERS_LAST_24H
- created:NEW
- clarified:
- PATCH_TOPIC2_INLINE_FIX_20260506_V1:V6C_PRICE_REJECTED:no_explicit_token_or_long
- PATCH_TOPIC2_INLINE_FIX_20260506_V1:V5_PRICE_REJECTED:no_explicit_token_or_long
- P6E67_PARENT_NOT_FOUND
- P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION
- clarified:Вот документ мне необходимо посчитать стоимость строительства Дом из г
- state:FAILED
- reply_sent:stale_failed
- reply_sent:p6e67_parent_not_found
- P6E67_PARENT_REVIVED_AS_REVISION_SOURCE:LAST_ACTIVE_ESTIMATE_FALLBACK
- P6E67_REVISION_TEXT_MERGED_FROM_TASK:89f1a927-af21-4d77-b287-70e8ecef659c
- P6E67_CURRENT_TASK_CANCELLED_MERGED_TO_PARENT:d72028da-b4ff-424d-a626-790c9da8be
- P6E67_BLOCK_ARTIFACT_GATE_PDF_LINK_MISSING_BEFORE_SEND_EX
- P6C_TOPIC2_IMAGE_OR_FILE_ESTIMATE_ROUTE_TAKEN
- TOPIC2_PRICE_CHOICE_REQUESTED
- clarified:2
- P6E67_BLOCK_ARTIFACT_GATE_PDF_LINK_MISSING_BEFORE_SEND
- P6E67_REVISION_TEXT_MERGED_FROM_TASK:0aaa723d-e506-4cfe-9cfc-7dc20b7ea094
- continued:вот размеры
- continued:вот задание
- TOPIC2_PRICE_CHOICE_CONFIRMED:confirmed
- P3_TOPIC2_CLARIFICATION
- clarified:Там же есть картинка посмотри проект
- clarified:есть в проекте
- clarified:смотри задание и проект
- clarified:ты не видешь что ранее писал?
- clarified:где расчет?
- clarified:ну че
- clarified:заебал

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

