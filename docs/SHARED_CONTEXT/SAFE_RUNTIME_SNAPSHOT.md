# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-05-08T17:50:02.341457+00:00
git_sha_before_commit: e185e83865a40e0712e8de514a3f56cee666eecb
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: inactive

## GIT_LOG_30
e185e83 fix(topic2): PATCH_SUPPLIER_HONESTY_V1 — fix fake Perplexity в Поставщик
5cff0da FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
433ffeb FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
222202e docs(handoff): CODEX_FULL_CANON_VERIFIED — c94ec497 AWAITING_CONFIRMATION, all phases 1-20 pass
6cf9154 fix(topic2): PATCH_TOPIC2_ADD_PEREKRYTIYA_SECTION_V1 — add missing §5 Перекрытия section
2475eb5 fix(topic2): PATCH_TOPIC2_REALSHEET_PRICES_V3 — real Газобетонный дом prices
10542fd FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7c646dd session(08.05): bigfile activated, topic5 V3 dispatcher, topic2 P6C intercept, c94ec497 FAILED/NOT_PROVEN
8a4de2b feat(bigfile): prepare PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1
c9443ff FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
8feb5f5 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7423725 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
af86bf5 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
981d301 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
f5838bb FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
d36b224 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
3dcb94a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
8760011 fix(topic2): enforce full canonical estimate pipeline without cross-topic regression
e08536b FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
33ce4a6 3 patches: material parse fix, zero-qty filter, price honesty
bf3bb26 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
d7b743d handoff: update HEAD to 81f35b5, mark P1 clarified loop closed
81f35b5 PATCH_P6CF3_CLARIFIED_HISTORY_INCLUDE_V1: fix infinite clarification loop
e7b171e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
96bea6c docs: handoff 08.05 — file_intake_router not called from _handle_drive_file (P0 arch)
74b156c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
b236f02 fix(topic2): session 08.05 — P6C fulltext prep, P3CHK append fix, P2 distance skip, WCPE unblock
e3a016c PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1: hard-enforce Sonar for all price/search calls
4cfd9b6 fix(topic2): close P6E67 loop storm + natural reply message
dc26486 fix(topic2): PATCH_PRICE_REJECT_STORM_FIX_V1 — remove noisy INSERT from V5/V6C rejected path

## GIT_SHOW_STAT_HEAD
commit e185e83865a40e0712e8de514a3f56cee666eecb
Author: Ila <ilakuznecov@mac.local>
Date:   Fri May 8 20:46:43 2026 +0300

    fix(topic2): PATCH_SUPPLIER_HONESTY_V1 — fix fake Perplexity в Поставщик
    
    PATCH_STROYKA_XLSX_15_COLS_V1 писал "Perplexity" в col12 из-за
    неверного HDR_ROW=7 и src_label="Perplexity". Патч переписан:
    - ранний выход по ws.cell(2,12)=="Ареал Нева.xlsx"
    - заполняет только col12 (Поставщик) для template_only строк
    - col11 (Источник цены) уже выставляется основным кодом
    
    Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 core/stroyka_estimate_canon.py | 25 ++++++-------------------
 1 file changed, 6 insertions(+), 19 deletions(-)

## GIT_CHANGED_FILES_10
.gitignore
areal_telegram_wrapper.py
core/stroyka_estimate_canon.py
core/technadzor_engine.py
docs/ARCHITECTURE/bigfile_ingress_override.conf.pending
docs/ARCHITECTURE/telegram-bot-api-local.service.template
docs/HANDOFFS/LATEST_HANDOFF.md
docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md
docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md
docs/SHARED_CONTEXT/DIRECTIONS/auto_parts_search.md
docs/SHARED_CONTEXT/DIRECTIONS/cad_dwg.md
docs/SHARED_CONTEXT/DIRECTIONS/construction_search.md
docs/SHARED_CONTEXT/DIRECTIONS/crm_leads.md
docs/SHARED_CONTEXT/DIRECTIONS/defect_acts.md
docs/SHARED_CONTEXT/DIRECTIONS/devops_server.md
docs/SHARED_CONTEXT/DIRECTIONS/documents.md
docs/SHARED_CONTEXT/DIRECTIONS/email_ingress.md
docs/SHARED_CONTEXT/DIRECTIONS/estimates.md
docs/SHARED_CONTEXT/DIRECTIONS/general_chat.md
docs/SHARED_CONTEXT/DIRECTIONS/google_drive_storage.md
docs/SHARED_CONTEXT/DIRECTIONS/internet_search.md
docs/SHARED_CONTEXT/DIRECTIONS/isolated_project_ivan.md
docs/SHARED_CONTEXT/DIRECTIONS/job_search.md
docs/SHARED_CONTEXT/DIRECTIONS/memory_archive.md
docs/SHARED_CONTEXT/DIRECTIONS/monolith_concrete.md
docs/SHARED_CONTEXT/DIRECTIONS/ocr_photo.md
docs/SHARED_CONTEXT/DIRECTIONS/orchestration_core.md
docs/SHARED_CONTEXT/DIRECTIONS/photo_cleanup.md
docs/SHARED_CONTEXT/DIRECTIONS/product_search.md
docs/SHARED_CONTEXT/DIRECTIONS/roofing.md
docs/SHARED_CONTEXT/DIRECTIONS/social_content.md
docs/SHARED_CONTEXT/DIRECTIONS/spreadsheets.md
docs/SHARED_CONTEXT/DIRECTIONS/structural_design.md
docs/SHARED_CONTEXT/DIRECTIONS/technical_supervision.md
docs/SHARED_CONTEXT/DIRECTIONS/telegram_automation.md
docs/SHARED_CONTEXT/DIRECTIONS/video_production.md
docs/SHARED_CONTEXT/DIRECTIONS/vpn_network.md
docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md
docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md
docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_001.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_002.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_003.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_004.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_005.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_006.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_007.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_008.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_009.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_010.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_011.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_012.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_013.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_014.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_015.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_016.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_017.md
docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md
docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md
docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md
docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md
docs/SHARED_CONTEXT/TOPICS/topic_0_COMMON.md
docs/SHARED_CONTEXT/TOPICS/topic_11_VIDEO.md
docs/SHARED_CONTEXT/TOPICS/topic_210_PROEKTIROVANIE.md
docs/SHARED_CONTEXT/TOPICS/topic_2_STROYKA.md
docs/SHARED_CONTEXT/TOPICS/topic_3008_KODY_MOZGOV.md
docs/SHARED_CONTEXT/TOPICS/topic_4569_CRM_LEADS.md
docs/SHARED_CONTEXT/TOPICS/topic_500_VEB_POISK.md
docs/SHARED_CONTEXT/TOPICS/topic_5_TEKHNADZOR.md
docs/SHARED_CONTEXT/TOPICS/topic_6104_JOB_SEARCH.md
docs/SHARED_CONTEXT/TOPICS/topic_794_DEVOPS.md
docs/SHARED_CONTEXT/TOPICS/topic_961_AVTOZAPCHASTI.md
docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md
task_worker.py
tools/verify_local_bot_api.sh

## CORE_DB_STATE_COUNTS
- FAILED|2961
- CANCELLED|822
- DONE|576
- ARCHIVED|381
- AWAITING_CONFIRMATION|1

## CORE_DB_OPEN_TASKS
- 1

## LATEST_TASKS_15
- c94ec497-4351-43a7-a106-b3dab1633838|2|drive_file|AWAITING_CONFIRMATION|{"file_id": "1EBmfcyns9UOm4S9tg0CYqCpIIidfLgwl", "file_name": "Открыть Микеа 3 РП 3 (1) (3) (3).pdf", "mime_type": "appl|✅ Смета готова

Объект: дом   Материал: газобетон   Площадь: 99.91 м²   Этажность: 1 этаж   Регион: СПб и ЛО
Шаблон: Ареал Нева.xlsx   Лист: смета   Цены: средн|2026-05-08 17:45:48
- 22712334-c39f-436a-90ec-cae5ce56f251|5|text|DONE|сделай акт|Акт осмотра объекта сформирован
Объект: Ропшинское шоссе 198
Фото учтено: 20
Нормативов подтверждено: 2

📄 DOCX: https://docs.google.com/document/d/10J6Wyvom27H|2026-05-08 09:59:54
- ce1d4d0b-7b7a-445e-b0e4-e52e54f001a7|5|text|CANCELLED|сделай акт|Финальный акт технадзора сформирован по текущему пакету фото

Фото в акте: 18
Пояснений учтено: 19
Нормы СП/ГОСТ не выдуманы, конкретные пункты не подставлены б|2026-05-08 09:29:30
- d8a8fbe7-81d7-4190-888c-2d8285c881b9|5|text|CANCELLED|сделай акт|Финальный акт технадзора сформирован по текущему пакету фото

Фото в акте: 18
Пояснений учтено: 20
Нормы СП/ГОСТ не выдуманы, конкретные пункты не подставлены б|2026-05-08 09:03:55
- de13074b-f71d-4523-a17e-8608cd3fd9dd|5|text|DONE|делай|Пакет технадзора активен
Папка: тест надзор
https://drive.google.com/drive/folders/1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG
Фото в пакете: 23 шт
1. photo_-100372529900|2026-05-08 08:28:37
- ac8bce62-7d06-494a-b6e5-bc6719b53359|5|text|DONE|[VOICE] Что по последнему заданию по итогам?|Пояснение принято к фото: photo_-1003725299009_10122.jpg. В пакете технадзора: 23 шт. Акт не формирую без отдельной команды|2026-05-08 08:28:28
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|2|text|CANCELLED|[VOICE] Что не так, скажи?|Пришли задание заново — расскажи что нужно сделать.|2026-05-08 08:27:08
- 524f5853-4243-4833-ae82-116da9202179|2|text|CANCELLED|[VOICE] Так а ты посмотри то, что я тебе писал, еще раз тебе говорю, посмотри последнее задание.|P6E67_MERGED_TO_PARENT_TASK 57c2617a-7975-4282-bffb-2b18577d8b9d|2026-05-08 06:18:34
- 4df9cf88-0843-478b-bef1-9d828d505298|2|text|DONE|[VOICE] Блять, я тебе еще раз говорю Посмотри все то, что мы с тобой писали По этому проекту У тебя же есть вся полность|Нового полного ТЗ для сметы в сообщении нет. Старую смету из памяти не поднимаю|2026-05-08 06:18:17
- 57c2617a-7975-4282-bffb-2b18577d8b9d|2|text|CANCELLED|[VOICE] посмотри проект все увидишь у тебя же есть проект зайди да глянь там же есть вся информация если тебе не хватает|P6E67_MERGED_TO_PARENT_TASK d72028da-b4ff-424d-a626-790c9da8be77|2026-05-08 06:18:36
- 0aaa723d-e506-4cfe-9cfc-7dc20b7ea094|2|text|CANCELLED|[VOICE] Я тебе в предыдущем сообщении уже все выбирал, все давал. Что тебе еще непонятно? Два. Средние цены, средние. Дв|P6E67_MERGED_TO_PARENT_TASK d72028da-b4ff-424d-a626-790c9da8be77|2026-05-08 05:07:19
- 89f1a927-af21-4d77-b287-70e8ecef659c|2|text|CANCELLED|[VOICE] Вот задание, соответственно, если что-то непонятно, мне нужна полностью смета с материалами посчитанная. Соответ|P6E67_MERGED_TO_PARENT_TASK d72028da-b4ff-424d-a626-790c9da8be77|2026-05-08 04:32:16
- d72028da-b4ff-424d-a626-790c9da8be77|2|drive_file|DONE|{"file_id": "1-isQhm067W2LDv2Bgm5ewbfyVm2B8QhV", "file_name": "8х12.pdf", "mime_type": "application/pdf", "caption": "На|✅ Предварительная смета готова

Объект: барнхаус 8.0x12.0 м
Этажей: 1
Площадь застройки: 96.0 м²
Расчётная площадь: 96.0 м²
Фундамент: монолитная плита
Стены: г|2026-05-08 06:54:21
- a7b2879e-14e6-4002-8a06-f73019d40a99|2|drive_file|FAILED|{"file_id": "1XRwOwZr2Kpxy-wrAUPrBR2dLqHseg7jS", "file_name": "photo_-1003725299009_10394.jpg", "mime_type": "image/jpeg|Не вижу размеры объекта на фото/в ТЗ. Пришли размер в формате 7.8х9.0 или фото крупнее|2026-05-07 13:34:34
- f3b2ae30-35cf-4e08-a25d-d3131d351676|5|text|DONE|Что такое цокольная балка где используется|Пояснение принято к фото: photo_-1003725299009_10122.jpg. В пакете технадзора: 23 шт. Акт не формирую без отдельной команды|2026-05-07 12:25:11

## LATEST_FAILED_10
- a7b2879e-14e6-4002-8a06-f73019d40a99|2|{"file_id": "1XRwOwZr2Kpxy-wrAUPrBR2dLqHseg7jS", "file_name": "photo_-1003725299009_10394.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-05-07 13:34:34
- 893436d4-72d2-4bdf-b362-f40d7226570e|2|[VOICE] Я тебе прислал картинку, две картинки и я тебе прислал техническое задание. Мне нужно сделать смету, уточнить ст|INVALID_PUBLIC_RESULT|2026-05-06 18:05:02
- cfadbd05-8b7c-4aca-a5e4-62b8d56398bb|210|[VOICE] Так ты сам должен выбирать то, что тебе нужно, а не спрашивать у меня. У тебя это как образцы для проектирования|INVALID_RESULT_GATE|2026-05-06 17:57:43
- f43100b3-65e8-4412-a3b4-6ab35071825e|2|[VOICE] Так ты должен мне смету посчитать Посмотреть в интернете сколько это стоит И посчитать мне смету Что ты не понял|TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_ERR:maximum recursion depth exceeded|2026-05-06 17:56:47
- c6b40dfc-854b-430b-9ff1-096ba254f8ac|2|[VOICE] Мне необходимо сделать расчет по стоимости работы материалов, взяв за основу средняя стоимость материалов, либо |STROYKA_QG_FAILED:XLSX_VALIDATE_ERROR:maximum recursion depth exceeded|2026-05-06 17:33:30
- 8212f685-b877-466a-a303-f468a00a664b|2|{"file_id": "1y5C9R1BG9a8Nf6MTu1d8MV_Y5LzLw-K6", "file_name": "Отчет_Мистолово_03.26.pdf", "mime_type": "application/pdf|STALE_TIMEOUT|2026-05-06 17:42:46
- 3828ac7a-d425-482f-b1f8-4ec76d27da82|2|{"file_id": "1zVQWoakxbwssZJbXdudubQSMhLv_qSS9", "file_name": "Схема глубинного дренажа.pdf", "mime_type": "application/|STALE_TIMEOUT|2026-05-06 17:42:46
- b71a685b-b129-446b-bd43-e6298b24f8cc|210|[VOICE] Средние цены поставь везде, на работу и на материалы.|INVALID_RESULT_GATE|2026-05-06 17:32:40
- 6e34406d-335c-4209-a3f6-b98e06791e78|210|{"file_id": "1UAv2GC3Ne3D8I-1YCpmmSNH6CrG5ACQi", "file_name": "Отчет_Мистолово_03.26.pdf", "mime_type": "application/pdf|NO_VALID_ARTIFACT|2026-05-06 17:31:44
- eba6dc80-d993-43e8-945b-cf1b48b9d103|210|{"file_id": "1evYG_-JrYks_cJ3D04LTYgdh1CZnWqTT", "file_name": "Схема глубинного дренажа.pdf", "mime_type": "application/|NO_VALID_ARTIFACT|2026-05-06 17:31:31

## LATEST_TASK_HISTORY_20
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_TELEGRAM_MATCHES_ARTIFACTS|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_BOT_MESSAGE_ID_SAVED:10550|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_PUBLIC_OUTPUT_CLEAN_OK|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_FULL_ESTIMATE_MATRIX_ENFORCED|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:estimate_generated|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_TELEGRAM_DELIVERED:10550|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_DRIVE_UPLOAD_PDF_OK|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_DRIVE_UPLOAD_XLSX_OK|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_PDF_CYRILLIC_OK|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_PDF_CREATED:1|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_XLSX_CANON_COLUMNS_OK:15|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_XLSX_FORMULAS_OK|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_XLSX_ROWS_WRITTEN:136|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_XLSX_TEMPLATE_COPY_OK|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_TEMPLATE_SHEET_SELECTED:смета|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_TEMPLATE_CACHE_USED|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_TEMPLATE_FILE_ID:1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_TEMPLATE_SELECTED:Ареал Нева.xlsx|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_AC_GATE_OK|2026-05-08 17:45:48
- c94ec497-4351-43a7-a106-b3dab1633838|TOPIC2_DRIVE_LINKS_SAVED:xlsx=https://drive.google.com/file/d/1DoVqBpRVAJU07y4ycRapVoN5twXal-Pl/view:pdf=https://drive.google.com/file/d/1w7P48KpyKB6gOlO9ytYQRtWRV_lWxSOd/view|2026-05-08 17:45:48

## MEMORY_DB_COUNT
- 5192

## LATEST_MEMORY_20
- topic_2_estimate_last|{
  "task_id": "c94ec497-4351-43a7-a106-b3dab1633838",
  "status": "AWAITING_CONFIRMATION",
  "result": "✅ Смета готова\n\nОбъект: дом   Материал: газобетон   Площадь: 99.91 м²   Э|2026-05-08T17:45:48.806368
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-05-08T17:21:58.286646+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-05-08T17:21:58.287484+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-05-08T17:21:58.266205+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-05-08T17:21:58.267001+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-05-08T17:21:58.217042+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-05-08T17:21:58.217446+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-05-08T17:21:58.183864+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-05-08T17:21:58.184451+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T17:21:58.125300+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-05-08T17:21:58.125204+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T17:21:58.125119+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T17:21:58.125016+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T17:21:58.124929+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-05-08T17:21:58.124810+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T17:21:58.124685+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T17:21:58.124477+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T17:21:58.124274+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T17:21:58.124168+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T17:21:58.123678+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-05-08T17:21:58.123302+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T17:21:58.123220+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T17:21:58.122975+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-05-08T17:21:58.122742+00:00

## JOURNAL_AREAL_TASK_WORKER_60
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 18.990s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 29.962s CPU time, 183.4M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 38.803s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 20.995s CPU time, 202.7M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 3min 27.647s CPU time, 183.5M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 19.029s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 5.185s CPU time.
Started areal-task-worker.service - Areal Task Worker.

## JOURNAL_TELEGRAM_INGRESS_30
2026-05-08 10:48:46,982 INFO DAEMON: Run polling for bot @ai_orkestra_all_bot id=8216054898 - 'AREAL-NEVA ORCHESTRA'
2026-05-08 11:28:26,770 INFO DAEMON: STT env check groq=True
2026-05-08 11:28:26,775 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10511.ogg size=16626 model=whisper-large-v3-turbo
2026-05-08 11:28:27,015 INFO DAEMON: STT http_status=200
2026-05-08 11:28:27,016 INFO DAEMON: STT ok transcript_len=36
2026-05-08 11:28:27,147 INFO DAEMON: Task ac8bce62-7d06-494a-b6e5-bc6719b53359 created state=NEW topic_id=5
2026-05-08 11:28:27,148 INFO DAEMON: Update id=262222006 is handled. Duration 714 ms by bot id=8216054898
2026-05-08 11:28:37,141 INFO DAEMON: Task de13074b-f71d-4523-a17e-8608cd3fd9dd created state=NEW topic_id=5
2026-05-08 11:28:37,141 INFO DAEMON: Update id=262222007 is handled. Duration 21 ms by bot id=8216054898
2026-05-08 11:31:23,246 INFO DAEMON: Task d8a8fbe7-81d7-4190-888c-2d8285c881b9 created state=NEW topic_id=5
2026-05-08 11:31:23,246 INFO DAEMON: Update id=262222008 is handled. Duration 100 ms by bot id=8216054898
2026-05-08 12:05:30,246 INFO DAEMON: Task ce1d4d0b-7b7a-445e-b0e4-e52e54f001a7 created state=NEW topic_id=5
2026-05-08 12:05:30,246 INFO DAEMON: Update id=262222009 is handled. Duration 15 ms by bot id=8216054898
2026-05-08 12:23:20,968 INFO DAEMON: Update id=262222010 is handled. Duration 348 ms by bot id=8216054898
2026-05-08 12:24:15,305 INFO DAEMON: Update id=262222011 is handled. Duration 77 ms by bot id=8216054898
2026-05-08 12:29:45,160 INFO DAEMON: Task 22712334-c39f-436a-90ec-cae5ce56f251 created state=NEW topic_id=5
2026-05-08 12:29:45,160 INFO DAEMON: Update id=262222012 is handled. Duration 19 ms by bot id=8216054898
Stopping telegram-ingress.service - AREAL telegram ingress...
2026-05-08 12:34:29,744 WARNING DAEMON: Received SIGTERM signal
2026-05-08 12:34:29,745 INFO DAEMON: Polling stopped for bot @ai_orkestra_all_bot id=8216054898 - 'AREAL-NEVA ORCHESTRA'
2026-05-08 12:34:29,746 INFO DAEMON: Polling stopped
telegram-ingress.service: Deactivated successfully.
Stopped telegram-ingress.service - AREAL telegram ingress.
telegram-ingress.service: Consumed 3.600s CPU time, 120.7M memory peak, 91.8M memory swap peak.
Started telegram-ingress.service - AREAL telegram ingress.
2026-05-08 12:34:32,497 INFO DAEMON: BIG_FILE_LOCAL_BOT_API_USED: local server active
2026-05-08 12:34:32,503 INFO DAEMON: BOT STARTED id=8216054898 username=ai_orkestra_all_bot
2026-05-08 12:34:32,503 INFO DAEMON: Start polling
2026-05-08 12:34:32,504 INFO DAEMON: Run polling for bot @ai_orkestra_all_bot id=8216054898 - 'AREAL-NEVA ORCHESTRA'
2026-05-08 13:11:00,381 INFO DAEMON: Update id=210388089 is handled. Duration 89 ms by bot id=8216054898
