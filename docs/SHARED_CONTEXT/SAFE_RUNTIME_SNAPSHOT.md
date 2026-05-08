# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-05-08T19:20:01.835762+00:00
git_sha_before_commit: 80b0809e73f89fdaa7bc03674b23058e081d6fc3
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: inactive

## GIT_LOG_30
80b0809 fix(topic2): PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 — current file source-of-truth gate blocks stale house context for drainage PDF
6862c04 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6923bea FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
afdcfad FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
075edf9 fix(topic2): PATCH_TOPIC2_STALE_PENDING_TASK_GUARD_V1 + LOCAL_BOT_API_404_FIX
db5dbef FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
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

## GIT_SHOW_STAT_HEAD
commit 80b0809e73f89fdaa7bc03674b23058e081d6fc3
Author: Ila <ilakuznecov@mac.local>
Date:   Fri May 8 22:18:28 2026 +0300

    fix(topic2): PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 — current file source-of-truth gate blocks stale house context for drainage PDF

 core/stroyka_estimate_canon.py |  35 ++++
 core/topic2_input_gate.py      | 432 +++++++++++++++++++++++++++++++++++++++++
 2 files changed, 467 insertions(+)

## GIT_CHANGED_FILES_10
areal_telegram_wrapper.py
core/stroyka_estimate_canon.py
core/topic2_input_gate.py
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

## CORE_DB_STATE_COUNTS
- FAILED|2964
- CANCELLED|823
- DONE|577
- ARCHIVED|381

## CORE_DB_OPEN_TASKS
- 0

## LATEST_TASKS_15
- test-drainage-reply-001|2|text|FAILED|Объект находится 50 км от Санкт-Петербурга цены выше среднего нужно посчитать стоимость работы материалов по данному зап|⏳ Задачу понял

Шаблон: Ареал Нева.xlsx
Лист: смета
Объект: дом
Материал: газобетон
Размеры: (8.5, 12.5)
Этажей: не указано
Фундамент: монолитная плита
Удалённо|2026-05-08 18:50:16
- 60b9503b-75cc-4913-bb7b-11092508fdae|2|text|FAILED|[VOICE] Я тебе говорил про вот эту информацию, посмотри.|✅ Смета готова

Объект: дом   Материал: газобетон   Площадь: 106.25 м²   Этажность: не указана   Регион: СПб и ЛО
Шаблон: Ареал Нева.xlsx   Лист: смета   Цены: |2026-05-08 19:17:11
- 1d2b38c4-8c86-4a44-8442-40be5c94fe89|2|drive_file|FAILED|{"file_id": "1ZJ4CqxlTcrXIL6b5GxE6nh9soo7Ud03h", "file_name": "project_file_2.pdf", "mime_type": "application/pdf", "cap|Принял файл «project_file_2.pdf». Что нужно сделать?

1️⃣ Смета — извлечь позиции, посчитать объёмы, создать Excel
2️⃣ Описание — описать содержимое документа
3|2026-05-08 18:14:03
- 1b281c50-2544-45c0-967d-2e49427d0d84|2|drive_file|CANCELLED|{"file_id": "1I7asWUOoZafUz53auWHeXL4Rr58AxNiK", "file_name": "project_file_1.pdf", "mime_type": "application/pdf", "cap|Принял файл «project_file_1.pdf». Что нужно сделать?

1️⃣ Смета — извлечь позиции, посчитать объёмы, создать Excel
2️⃣ Описание — описать содержимое документа
3|2026-05-08 18:41:18
- c94ec497-4351-43a7-a106-b3dab1633838|2|drive_file|DONE|{"file_id": "1EBmfcyns9UOm4S9tg0CYqCpIIidfLgwl", "file_name": "Открыть Микеа 3 РП 3 (1) (3) (3).pdf", "mime_type": "appl|✅ Смета готова

Объект: дом   Материал: газобетон   Площадь: 99.91 м²   Этажность: 1 этаж   Регион: СПб и ЛО
Шаблон: Ареал Нева.xlsx   Лист: смета   Цены: средн|2026-05-08 18:15:50
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

## LATEST_FAILED_10
- test-drainage-reply-001|2|Объект находится 50 км от Санкт-Петербурга цены выше среднего нужно посчитать стоимость работы материалов по данному зап|STALE_TIMEOUT|2026-05-08 18:50:16
- 60b9503b-75cc-4913-bb7b-11092508fdae|2|[VOICE] Я тебе говорил про вот эту информацию, посмотри.|TOPIC2_STALE_HOUSE_CONTEXT_USED_FOR_DRAINAGE_FILE|2026-05-08 19:17:11
- 1d2b38c4-8c86-4a44-8442-40be5c94fe89|2|{"file_id": "1ZJ4CqxlTcrXIL6b5GxE6nh9soo7Ud03h", "file_name": "project_file_2.pdf", "mime_type": "application/pdf", "cap|STALE_TIMEOUT|2026-05-08 18:14:03
- a7b2879e-14e6-4002-8a06-f73019d40a99|2|{"file_id": "1XRwOwZr2Kpxy-wrAUPrBR2dLqHseg7jS", "file_name": "photo_-1003725299009_10394.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-05-07 13:34:34
- 893436d4-72d2-4bdf-b362-f40d7226570e|2|[VOICE] Я тебе прислал картинку, две картинки и я тебе прислал техническое задание. Мне нужно сделать смету, уточнить ст|INVALID_PUBLIC_RESULT|2026-05-06 18:05:02
- cfadbd05-8b7c-4aca-a5e4-62b8d56398bb|210|[VOICE] Так ты сам должен выбирать то, что тебе нужно, а не спрашивать у меня. У тебя это как образцы для проектирования|INVALID_RESULT_GATE|2026-05-06 17:57:43
- f43100b3-65e8-4412-a3b4-6ab35071825e|2|[VOICE] Так ты должен мне смету посчитать Посмотреть в интернете сколько это стоит И посчитать мне смету Что ты не понял|TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_ERR:maximum recursion depth exceeded|2026-05-06 17:56:47
- c6b40dfc-854b-430b-9ff1-096ba254f8ac|2|[VOICE] Мне необходимо сделать расчет по стоимости работы материалов, взяв за основу средняя стоимость материалов, либо |STROYKA_QG_FAILED:XLSX_VALIDATE_ERROR:maximum recursion depth exceeded|2026-05-06 17:33:30
- 8212f685-b877-466a-a303-f468a00a664b|2|{"file_id": "1y5C9R1BG9a8Nf6MTu1d8MV_Y5LzLw-K6", "file_name": "Отчет_Мистолово_03.26.pdf", "mime_type": "application/pdf|STALE_TIMEOUT|2026-05-06 17:42:46
- 3828ac7a-d425-482f-b1f8-4ec76d27da82|2|{"file_id": "1zVQWoakxbwssZJbXdudubQSMhLv_qSS9", "file_name": "Схема глубинного дренажа.pdf", "mime_type": "application/|STALE_TIMEOUT|2026-05-06 17:42:46

## LATEST_TASK_HISTORY_20
- 60b9503b-75cc-4913-bb7b-11092508fdae|TOPIC2_STALE_HOUSE_CONTEXT_USED_FOR_DRAINAGE_FILE|2026-05-08 19:17:11
- test-drainage-reply-001|reply_sent:stale_failed|2026-05-08 18:50:16
- test-drainage-reply-001|state:FAILED|2026-05-08 18:50:16
- 60b9503b-75cc-4913-bb7b-11092508fdae|CANCELLED:INVALID_STALE_CONTEXT_RESULT|2026-05-08 18:41:18
- 1b281c50-2544-45c0-967d-2e49427d0d84|CANCELLED:INVALID_STALE_CONTEXT_RESULT|2026-05-08 18:41:18
- test-drainage-reply-001|TOPIC2_CANONICAL_REROUTE_V2:CANONICAL_HANDLED|2026-05-08 18:40:12
- test-drainage-reply-001|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown|2026-05-08 18:40:12
- test-drainage-reply-001|TOPIC2_PRICE_SOURCE_FOUND:Работы по монтажу и кладке:ООО ТСК:CONFIRMED|2026-05-08 18:40:12
- test-drainage-reply-001|TOPIC2_PRICE_WORK_SEARCH_STARTED:Работы по монтажу и кладке|2026-05-08 18:40:02
- test-drainage-reply-001|TOPIC2_PRICE_SOURCE_FOUND:монолитная плита:beton-monolit.spb.ru:CONFIRMED|2026-05-08 18:40:02
- test-drainage-reply-001|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:монолитная плита|2026-05-08 18:39:40
- test-drainage-reply-001|TOPIC2_PRICE_SOURCE_FOUND:Арматура А500:stroybazav.ru:UNVERIFIED|2026-05-08 18:39:40
- test-drainage-reply-001|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Арматура А500|2026-05-08 18:39:30
- test-drainage-reply-001|TOPIC2_PRICE_SOURCE_FOUND:Бетон В25:beton-spb.ru:UNVERIFIED|2026-05-08 18:39:30
- test-drainage-reply-001|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Бетон В25|2026-05-08 18:39:21
- test-drainage-reply-001|TOPIC2_PRICE_SOURCE_FOUND:газобетон:TSK Company:CONFIRMED|2026-05-08 18:39:21
- test-drainage-reply-001|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:газобетон|2026-05-08 18:39:09
- test-drainage-reply-001|TOPIC2_PRICE_ENRICHMENT_DONE:1133|2026-05-08 18:39:09
- test-drainage-reply-001|TOPIC2_PRICE_ENRICHMENT_STARTED|2026-05-08 18:39:03
- test-drainage-reply-001|TOPIC2_ONLINE_MODEL_SONAR_CONFIRMED:perplexity/sonar|2026-05-08 18:39:03

## MEMORY_DB_COUNT
- 5196

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-05-08T18:52:04.047424+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-05-08T18:52:04.048531+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-05-08T18:52:04.026041+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-05-08T18:52:04.026747+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-05-08T18:52:03.967965+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-05-08T18:52:03.968882+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-05-08T18:52:03.932204+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-05-08T18:52:03.932902+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T18:52:03.869496+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-05-08T18:52:03.869375+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T18:52:03.869245+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T18:52:03.869100+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T18:52:03.868994+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-05-08T18:52:03.868882+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T18:52:03.868689+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T18:52:03.868460+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T18:52:03.868249+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T18:52:03.868128+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T18:52:03.867720+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-05-08T18:52:03.867340+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T18:52:03.867253+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T18:52:03.866999+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-05-08T18:52:03.866761+00:00
- topic_210_file_fb6aadc5-b372-488a-aede-f3433a030e55|{"task_id": "fb6aadc5-b372-488a-aede-f3433a030e55", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T18:52:03.866645+00:00

## JOURNAL_AREAL_TASK_WORKER_60
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
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 46.862s CPU time, 194.3M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 1.392s CPU time, 81.2M memory peak, 0B memory swap peak.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 1.392s CPU time, 81.2M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 2.253s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 32.421s CPU time, 104.9M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.

## JOURNAL_TELEGRAM_INGRESS_30
2026-05-08 21:00:41,932 INFO DAEMON: Polling stopped
Stopping telegram-ingress.service - AREAL telegram ingress...
telegram-ingress.service: Deactivated successfully.
Stopped telegram-ingress.service - AREAL telegram ingress.
telegram-ingress.service: Consumed 5.288s CPU time, 115.2M memory peak, 0B memory swap peak.
Started telegram-ingress.service - AREAL telegram ingress.
2026-05-08 21:00:44,415 INFO DAEMON: BIG_FILE_LOCAL_BOT_API_USED: local server active
2026-05-08 21:00:44,422 INFO DAEMON: BOT STARTED id=8216054898 username=ai_orkestra_all_bot
2026-05-08 21:00:44,423 INFO DAEMON: Start polling
2026-05-08 21:00:44,423 INFO DAEMON: Run polling for bot @ai_orkestra_all_bot id=8216054898 - 'AREAL-NEVA ORCHESTRA'
2026-05-08 21:07:17,460 INFO DAEMON: Update id=210388094 is handled. Duration 137 ms by bot id=8216054898
2026-05-08 21:08:08,043 INFO DAEMON: LOCAL_BOT_API_ABSOLUTE_PATH_USED:file_5.oga
2026-05-08 21:08:08,044 INFO DAEMON: STT env check groq=True
2026-05-08 21:08:08,044 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10565.ogg size=17525 model=whisper-large-v3-turbo
2026-05-08 21:08:08,312 INFO DAEMON: STT http_status=200
2026-05-08 21:08:08,312 INFO DAEMON: STT ok transcript_len=48
2026-05-08 21:08:08,389 INFO DAEMON: Task 60b9503b-75cc-4913-bb7b-11092508fdae created state=NEW topic_id=2
2026-05-08 21:08:08,389 INFO DAEMON: Update id=210388095 is handled. Duration 484 ms by bot id=8216054898
Stopping telegram-ingress.service - AREAL telegram ingress...
2026-05-08 22:17:31,652 WARNING DAEMON: Received SIGTERM signal
2026-05-08 22:17:31,653 INFO DAEMON: Polling stopped for bot @ai_orkestra_all_bot id=8216054898 - 'AREAL-NEVA ORCHESTRA'
2026-05-08 22:17:31,653 INFO DAEMON: Polling stopped
telegram-ingress.service: Deactivated successfully.
Stopped telegram-ingress.service - AREAL telegram ingress.
telegram-ingress.service: Consumed 2.671s CPU time.
Started telegram-ingress.service - AREAL telegram ingress.
2026-05-08 22:17:34,073 INFO DAEMON: BIG_FILE_LOCAL_BOT_API_USED: local server active
2026-05-08 22:17:34,083 INFO DAEMON: BOT STARTED id=8216054898 username=ai_orkestra_all_bot
2026-05-08 22:17:34,083 INFO DAEMON: Start polling
2026-05-08 22:17:34,084 INFO DAEMON: Run polling for bot @ai_orkestra_all_bot id=8216054898 - 'AREAL-NEVA ORCHESTRA'
