# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-08-16T14:50:02.137488+00:00
git_sha_before_commit: bfb2a75b0128d873f3b75c4b65300d066fa54576
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
bfb2a75b01 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
99d3b88097 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6fb9958436 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
50a1f01b20 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
382815ae1f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
8e60cb8782 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
55fb78a08a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
f648a5d1d3 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
bd3b172f3d FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
afef8f3722 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
1bf8b549ec FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6384372450 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
f721f33a7d FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
8f701395ef FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
e412cab3e9 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
bb6bac1d71 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
abd91cd279 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
92f608a305 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
13ba013730 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
0cbf708aeb FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
5fcfe8c0bc FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
0c12dbcb6a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
727c769cd1 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
5acbebdf54 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
b03ef2f0dd FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
95a93e1b3c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
55c918e6ad FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
96034abf75 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7722891693 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
eea2d7045e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

## GIT_SHOW_STAT_HEAD
commit bfb2a75b0128d873f3b75c4b65300d066fa54576
Author: root <root@graceful-olive.ptr.network>
Date:   Sun Aug 16 17:46:15 2026 +0300

    FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

 docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md    |   6 +-
 docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md |   2 +-
 .../SHARED_CONTEXT/DIRECTIONS/auto_parts_search.md |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/cad_dwg.md          |   4 +-
 .../DIRECTIONS/construction_search.md              |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/crm_leads.md        |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/defect_acts.md      |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/devops_server.md    |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/documents.md        |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/email_ingress.md    |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/estimates.md        |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/general_chat.md     |   4 +-
 .../DIRECTIONS/google_drive_storage.md             |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/internet_search.md  |   4 +-
 .../DIRECTIONS/isolated_project_ivan.md            |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/job_search.md       |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/memory_archive.md   |   4 +-
 .../SHARED_CONTEXT/DIRECTIONS/monolith_concrete.md |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/ocr_photo.md        |   4 +-
 .../DIRECTIONS/orchestration_core.md               |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/photo_cleanup.md    |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/product_search.md   |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/roofing.md          |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/social_content.md   |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/spreadsheets.md     |   4 +-
 .../SHARED_CONTEXT/DIRECTIONS/structural_design.md |   4 +-
 .../DIRECTIONS/technical_supervision.md            |   4 +-
 .../DIRECTIONS/telegram_automation.md              |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/video_production.md |   4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/vpn_network.md      |   4 +-
 docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md      |   4 +-
 docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md     |   6 +-
 docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md          |   6 +-
 docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md      |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_MANIFEST.json           |   6 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_001.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_002.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_003.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_004.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_005.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_006.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_007.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_008.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_009.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_010.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_011.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_012.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_013.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_014.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_015.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_016.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_017.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_018.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_019.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_020.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_021.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_022.md             |   4 +-
 docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md       | 200 ++++++++++-----------
 .../SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md |   4 +-
 docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md   |  48 ++---
 docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md         |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_0_COMMON.md       |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_11_VIDEO.md       |   4 +-
 .../TOPICS/topic_210_PROEKTIROVANIE.md             |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_2_STROYKA.md      |   4 +-
 .../TOPICS/topic_3008_KODY_MOZGOV.md               |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_4569_CRM_LEADS.md |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_500_VEB_POISK.md  |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_5_TEKHNADZOR.md   |   4 +-
 .../SHARED_CONTEXT/TOPICS/topic_6104_JOB_SEARCH.md |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_794_DEVOPS.md     |   4 +-
 .../TOPICS/topic_961_AVTOZAPCHASTI.md              |   4 +-
 docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md          |   4 +-
 73 files changed, 269 insertions(+), 269 deletions(-)

## GIT_CHANGED_FILES_10
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
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_018.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_019.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_020.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_021.md
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_022.md
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
- FAILED|3056
- CANCELLED|879
- DONE|753
- ARCHIVED|381

## CORE_DB_OPEN_TASKS
- 0

## LATEST_TASKS_15
- 8be95000-3319-4fdb-b0ac-478b8d6a8ab5|2|text|DONE|3|Выбор цен привязан к основной задаче: reliable|2026-07-27 17:50:46
- 63ffa3d4-092b-4747-b605-ce4495fcebbf|2|text|CANCELLED|[VOICE] Мне нужно сделать расчет ангара. Высота одной стены 7 метров, высота другой стены 8 метров. Размеры 36 на 12. Ну|Выберите уровень цен для сметы:

1 — минимальные (самые дешёвые)
2 — средние (медианные)
3 — надёжный поставщик
4 — ручные

Ответь: 1 / 2 / 3 / 4 или: минимальн|2026-07-27T17:51:58.466198+00:00
- 6968cbd9-e233-4652-8da3-b03e6758f1b4|2|text|DONE|Да, доволен, завершай задачу|Подтверждение принято|2026-07-15 15:42:33
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|2|drive_file|FAILED|{"file_id":"1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me","file_name":"ирина ар проект.pdf","mime_type":"application/pdf","caption"||2026-07-27 17:52:29
- a36c62ed-5f76-4faa-b852-0d795ab2548c|2|text|DONE|Да, доволен, завершай задачу|Подтверждение принято|2026-07-15 15:28:43
- f4ec7e8a-969c-4bdc-8899-010e9ce24965|2|text|DONE|Да, доволен, завершай задачу|Подтверждение принято|2026-07-15 14:55:38
- 7b1df476-c1df-4dfd-a65d-e38b2df645d0|2|drive_file|DONE|{"file_id":"1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me","file_name":"ирина ар проект.pdf","mime_type":"application/pdf","caption"|✅ Смета готова

Объект: Индивидуальный жилой дом   Материал: монолитный железобетон и газобетон   Площадь: 151.9 м² (пятно ФП1)   Этажность: 2 надземных этажа +|2026-07-15 15:28:43
- 128047d6-f2e5-41c9-aff2-507f630741dd|2|drive_file|FAILED|{"file_id":"1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me","file_name":"ирина ар проект.pdf","mime_type":"application/pdf","caption"|Принял PDF как новый отдельный проект.
Объект: Индивидуальный жилой дом
Обработано страниц: 97

Подтверждено по ведомостям проекта:
- Арматура всего: 22402 кг
-|2026-07-15 14:52:09
- 59424786-6dd7-4d24-8d92-53ec8bff9435|2|drive_file|FAILED|{"file_id":"1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me","file_name":"ирина ар проект.pdf","mime_type":"application/pdf","caption"|Задача не выполнена: NO_VALID_ARTIFACT|2026-07-15 14:35:16
- 0d725696-a8c4-4545-85e0-9d4acaa91c1a|2|text|DONE|Да доволен завершай|Подтверждение принято|2026-07-15 14:32:02
- 9062c46c-7156-4fd0-96e5-5020c28f8618|2|text|CANCELLED|Работа готова|Смета готова по текущему заданию

Позиций: 1
Итого: 1080000.00 руб

Основа сметы: только текущий текст задачи
Старые сметы, ВОР, профлист и старые Drive-ссылки |2026-07-15 14:32:31
- 4d38f053-7261-4b52-9fed-02f46c7a23a9|2|text|DONE|Задача завершена|Подтверждение принято|2026-07-15 12:02:54
- 543774b0-bb23-46c4-8f46-6ac805a81950|2|text|DONE|4|Выбор цен привязан к основной задаче: manual|2026-07-15 11:57:35
- 137c6019-37af-42b8-bb52-6c354c0f8a69|2|text|DONE|1|Выбор действия по файлу принят: смета|2026-07-15 11:54:45
- 002da0a4-c252-4c87-b548-fad4b69ad757|2|drive_file|DONE|{"file_id": "1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me", "file_name": "ирина ар проект.pdf", "mime_type": "application/pdf", "ca|✅ Смета готова

Объект: Индивидуальный жилой дом   Материал: монолитный железобетон и газобетон   Площадь: 151.9 м² (пятно ФП1)   Этажность: 2 надземных этажа +|2026-07-15 14:32:02

## LATEST_FAILED_10
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|2|{"file_id":"1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me","file_name":"ирина ар проект.pdf","mime_type":"application/pdf","caption"|STROYKA_QG_FAILED:TOO_FEW_ITEMS:0|2026-07-27 17:52:29
- 128047d6-f2e5-41c9-aff2-507f630741dd|2|{"file_id":"1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me","file_name":"ирина ар проект.pdf","mime_type":"application/pdf","caption"|STALE_TIMEOUT|2026-07-15 14:52:09
- 59424786-6dd7-4d24-8d92-53ec8bff9435|2|{"file_id":"1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me","file_name":"ирина ар проект.pdf","mime_type":"application/pdf","caption"|NO_VALID_ARTIFACT|2026-07-15 14:35:16
- ad69b7c1-8d6c-4007-bb05-f9ce0cfc63bc|2|[VOICE] Поставь здесь панели ценой 3200 – это стеновые панели и 3600 – это потолочные панели, кровельные.|STALE_TIMEOUT|2026-07-07 20:17:03
- 341cde94-b085-4a37-ae42-abcce3dc32f3|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 16:48:52
- 5e523179-e0b9-41b9-96b7-08e4fdb3accb|2|Эти два файла это один проект. Для начала найди и вытащи все объёмы из АР и КР.|STALE_TIMEOUT|2026-07-07 16:15:41
- 9d7440b6-a7ab-4600-948f-e1b0e91510d4|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 16:05:42
- e65b555f-62e2-4a86-b203-39b3c1fd110c|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 15:58:42
- 7300d5f5-94eb-488d-95e1-2f0b516740de|5|{"file_id": "1E1iHSjskAwDbfr3xk8EUsD3KP2FBab-i", "file_name": "photo_-1003725299009_12206.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:28
- 2d607bf6-c874-4a5b-9cfd-f7d89b44f866|5|{"file_id": "1eqCReGl0w3ra1m5_Qn0oX9CcYxvWor0v", "file_name": "photo_-1003725299009_12208.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:28

## LATEST_TASK_HISTORY_20
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|PATCH_TOPIC2_DRIVE_FINAL_USE_CANON_GENERATE_V2:DONE|2026-07-27 17:52:29
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_LOGISTICS_DISTANCE_KM:0|2026-07-27 17:52:29
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PRICE_CHOICE_CONFIRMED:reliable|2026-07-27 17:52:26
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|PATCH_TOPIC2_DRIVE_FINAL_USE_CANON_GENERATE_V2:START|2026-07-27 17:52:26
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:PARENT_RAW_ENRICHED|2026-07-27 17:52:26
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|PATCH_TOPIC2_FOUNDATION_MISSING_PRICE_FINAL_GATE_V1:CLEARED|2026-07-27 17:52:26
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_FULL_FOUNDATION_PRICE_SOURCE_SONAR_DONE:formwork_material,formwork_work,rebar_work,sand_work,gravel_work|2026-07-27 17:52:25
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PRICE_SOURCE_FOUND:gravel_work:stroikahome.ru:CONFIRMED|2026-07-27 17:52:25
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Устройство щебеночного основания с уплотнением работы|2026-07-27 17:52:02
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PRICE_CACHE_BEFORE_SONAR:gravel_work|2026-07-27 17:52:02
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PRICE_SOURCE_FOUND:sand_work:Фундамент98:CONFIRMED|2026-07-27 17:52:02
- 63ffa3d4-092b-4747-b605-ce4495fcebbf|cancelled|2026-07-27T17:51:58.466369+00:00
- 63ffa3d4-092b-4747-b605-ce4495fcebbf|continued:Отмена задачи|2026-07-27T17:51:55.040136+00:00
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Устройство песчаной подушки с послойным уплотнением работы|2026-07-27 17:51:53
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PRICE_CACHE_BEFORE_SONAR:sand_work|2026-07-27 17:51:53
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PRICE_SOURCE_FOUND:rebar_work:fundament-spb.com:CONFIRMED|2026-07-27 17:51:53
- 63ffa3d4-092b-4747-b605-ce4495fcebbf|clarified:Отменяю задачу|2026-07-27T17:51:50.915139+00:00
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Армирование фундаментной плиты работы|2026-07-27 17:51:29
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PRICE_CACHE_BEFORE_SONAR:rebar_work|2026-07-27 17:51:29
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PRICE_SOURCE_FOUND:formwork_work:Ds Structures:CONFIRMED|2026-07-27 17:51:29

## MEMORY_DB_COUNT
- 5393

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 33, "updated_at": "2026-08-16T14:46:09.050123+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-08-16T14:46:09.050742+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-08-16T14:46:09.024515+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-08-16T14:46:09.025252+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-08-16T14:46:08.956208+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-08-16T14:46:08.956884+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-08-16T14:46:08.941492+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-08-16T14:46:08.942130+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-08-16T14:46:08.903893+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-08-16T14:46:08.904787+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-08-16T14:46:08.787540+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-08-16T14:46:08.787470+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-08-16T14:46:08.787407+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-08-16T14:46:08.787315+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-08-16T14:46:08.787259+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-08-16T14:46:08.787197+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-08-16T14:46:08.787121+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-08-16T14:46:08.786927+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-08-16T14:46:08.786704+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-08-16T14:46:08.786600+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-08-16T14:46:08.786284+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-08-16T14:46:08.786049+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-08-16T14:46:08.785985+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-08-16T14:46:08.785799+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-08-16T14:46:08.785608+00:00

## JOURNAL_AREAL_TASK_WORKER_60
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 17.361s CPU time, 195.6M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:672: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 25.676s CPU time, 196.2M memory peak, 0B memory swap peak.
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
areal-task-worker.service: Consumed 49.514s CPU time, 110.8M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:672: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 21.222s CPU time, 195.2M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:672: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
Started areal-task-worker.service - Areal Task Worker.

## JOURNAL_TELEGRAM_INGRESS_30
2026-08-04 04:17:38,036 WARNING DAEMON: Sleep for 1.368535 seconds and try again... (tryings = 1, bot id = 8216054898)
2026-08-04 04:18:39,803 INFO DAEMON: Connection established (tryings = 2, bot id = 8216054898)
2026-08-11 04:13:34,029 ERROR DAEMON: Failed to fetch updates - TelegramRetryAfter: Telegram server says - Flood control exceeded on method 'GetUpdates'. Retry in 5 seconds.
Original description: Too Many Requests: retry after 5
(background on this error at: https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this)
2026-08-11 04:13:34,042 WARNING DAEMON: Sleep for 1.000000 seconds and try again... (tryings = 0, bot id = 8216054898)
2026-08-11 04:13:35,077 ERROR DAEMON: Failed to fetch updates - TelegramRetryAfter: Telegram server says - Flood control exceeded on method 'GetUpdates'. Retry in 5 seconds.
Original description: Too Many Requests: retry after 5
(background on this error at: https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this)
2026-08-11 04:13:35,077 WARNING DAEMON: Sleep for 1.346723 seconds and try again... (tryings = 1, bot id = 8216054898)
2026-08-11 04:13:36,456 ERROR DAEMON: Failed to fetch updates - TelegramRetryAfter: Telegram server says - Flood control exceeded on method 'GetUpdates'. Retry in 5 seconds.
Original description: Too Many Requests: retry after 5
(background on this error at: https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this)
2026-08-11 04:13:36,456 WARNING DAEMON: Sleep for 1.748713 seconds and try again... (tryings = 2, bot id = 8216054898)
2026-08-11 04:13:40,283 ERROR DAEMON: Failed to fetch updates - TelegramServerError: Telegram server says - Bad Gateway
2026-08-11 04:13:40,283 WARNING DAEMON: Sleep for 2.357960 seconds and try again... (tryings = 3, bot id = 8216054898)
2026-08-11 04:14:24,871 INFO DAEMON: Connection established (tryings = 4, bot id = 8216054898)
2026-08-14 04:13:14,142 ERROR DAEMON: Failed to fetch updates - TelegramServerError: Telegram server says - Bad Gateway
2026-08-14 04:13:14,151 WARNING DAEMON: Sleep for 1.000000 seconds and try again... (tryings = 0, bot id = 8216054898)
2026-08-14 04:13:15,183 ERROR DAEMON: Failed to fetch updates - TelegramServerError: Telegram server says - Bad Gateway
2026-08-14 04:13:15,183 WARNING DAEMON: Sleep for 1.298419 seconds and try again... (tryings = 1, bot id = 8216054898)
2026-08-14 04:14:27,150 ERROR DAEMON: Failed to fetch updates - TelegramNetworkError: HTTP Client says - Request timeout error
2026-08-14 04:14:27,151 WARNING DAEMON: Sleep for 1.795963 seconds and try again... (tryings = 2, bot id = 8216054898)
2026-08-14 04:14:39,066 INFO DAEMON: Connection established (tryings = 3, bot id = 8216054898)
2026-08-14 04:32:53,293 ERROR DAEMON: Failed to fetch updates - TelegramNetworkError: HTTP Client says - ClientOSError: [Errno 104] Connection reset by peer
2026-08-14 04:32:53,294 WARNING DAEMON: Sleep for 1.000000 seconds and try again... (tryings = 0, bot id = 8216054898)
2026-08-14 04:33:04,408 INFO DAEMON: Connection established (tryings = 1, bot id = 8216054898)
2026-08-15 04:12:12,521 ERROR DAEMON: Failed to fetch updates - TelegramServerError: Telegram server says - Bad Gateway
2026-08-15 04:12:12,530 WARNING DAEMON: Sleep for 1.000000 seconds and try again... (tryings = 0, bot id = 8216054898)
2026-08-15 04:13:11,453 INFO DAEMON: Connection established (tryings = 1, bot id = 8216054898)
