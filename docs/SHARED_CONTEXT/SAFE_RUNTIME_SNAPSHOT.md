# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-07-16T03:35:02.470377+00:00
git_sha_before_commit: 114f5d75a21e6a3198c3f7c9fa6c91a70298dd9a
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
114f5d75a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
2d7e96550 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
3f0455bb2 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7c3dd990e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
98d9df60b FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
cb0b706de FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
b4841d374 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
b7a843263 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
cfa154c49 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
871018a22 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
9f3d90cd7 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
cd27b0420 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
13f586844 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
647f00cd0 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
537f7f241 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
f58cfc41a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
5f69be84a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
f5e0ba84d FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
d7fb0e6de FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
e6769f074 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
ec6ce8b0c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7fd294c89 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
f84ba3aae FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
689887a3f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
872427ee6 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
0dad687bd FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
596eac79d FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
88c8ba9ff FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
02ce2e72a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
200862314 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

## GIT_SHOW_STAT_HEAD
commit 114f5d75a21e6a3198c3f7c9fa6c91a70298dd9a
Author: root <root@graceful-olive.ptr.network>
Date:   Thu Jul 16 06:30:49 2026 +0300

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
- FAILED|3055
- CANCELLED|878
- DONE|753
- ARCHIVED|381

## CORE_DB_OPEN_TASKS
- 0

## LATEST_TASKS_15
- 6968cbd9-e233-4652-8da3-b03e6758f1b4|2|text|DONE|Да, доволен, завершай задачу|Подтверждение принято|2026-07-15 15:42:33
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|2|drive_file|DONE|{"file_id":"1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me","file_name":"ирина ар проект.pdf","mime_type":"application/pdf","caption"|✅ Смета готова

Объект: Индивидуальный жилой дом   Материал: монолитный железобетон и газобетон   Площадь: 151.9 м² (пятно ФП1)   Этажность: 2 надземных этажа +|2026-07-15 15:42:33
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
- 8414e015-55c7-46dd-99da-f51524eb37ec|2|drive_file|CANCELLED|{"file_id": "1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me", "file_name": "ирина ар проект.pdf", "mime_type": "application/pdf", "ca|ирина ар проект.pdf принят и прочитан. Нашёл текущие проектные строки:
- явная ВОР/спецификация не найдена

Шаблонные строки из старых смет не подставляю. Подтв|2026-07-10T10:49:50.940580+00:00
- fc03d3ed-876d-470c-a037-febc737ee0cb|2|text|CANCELLED|Мы с тобой последнюю смету считали?|файл принят и прочитан. Нашёл текущие проектные строки:
- явная ВОР/спецификация не найдена

Шаблонные строки из старых смет не подставляю. Подтверди, пожалуйст|2026-07-07T20:27:39.613851+00:00

## LATEST_FAILED_10
- 128047d6-f2e5-41c9-aff2-507f630741dd|2|{"file_id":"1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me","file_name":"ирина ар проект.pdf","mime_type":"application/pdf","caption"|STALE_TIMEOUT|2026-07-15 14:52:09
- 59424786-6dd7-4d24-8d92-53ec8bff9435|2|{"file_id":"1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me","file_name":"ирина ар проект.pdf","mime_type":"application/pdf","caption"|NO_VALID_ARTIFACT|2026-07-15 14:35:16
- ad69b7c1-8d6c-4007-bb05-f9ce0cfc63bc|2|[VOICE] Поставь здесь панели ценой 3200 – это стеновые панели и 3600 – это потолочные панели, кровельные.|STALE_TIMEOUT|2026-07-07 20:17:03
- 341cde94-b085-4a37-ae42-abcce3dc32f3|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 16:48:52
- 5e523179-e0b9-41b9-96b7-08e4fdb3accb|2|Эти два файла это один проект. Для начала найди и вытащи все объёмы из АР и КР.|STALE_TIMEOUT|2026-07-07 16:15:41
- 9d7440b6-a7ab-4600-948f-e1b0e91510d4|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 16:05:42
- e65b555f-62e2-4a86-b203-39b3c1fd110c|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 15:58:42
- 7300d5f5-94eb-488d-95e1-2f0b516740de|5|{"file_id": "1E1iHSjskAwDbfr3xk8EUsD3KP2FBab-i", "file_name": "photo_-1003725299009_12206.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:28
- 2d607bf6-c874-4a5b-9cfd-f7d89b44f866|5|{"file_id": "1eqCReGl0w3ra1m5_Qn0oX9CcYxvWor0v", "file_name": "photo_-1003725299009_12208.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:28
- 68dceab3-4cd1-43cd-92f4-2bed426d2b88|5|{"file_id": "1ebYctoc4X_3venU6COcDVSTDJ_uYnNAA", "file_name": "photo_-1003725299009_12204.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:26

## LATEST_TASK_HISTORY_20
- 6968cbd9-e233-4652-8da3-b03e6758f1b4|PATCH_TOPIC2_READY_DONE_BEFORE_FRUSTRATION_V1:topic2_memory_synced_for:d019c976-5e46-475d-bcd7-c9f349eb0ea1|2026-07-15 15:42:34
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|PATCH_TOPIC2_READY_DONE_BEFORE_FRUSTRATION_V1:topic2_memory_synced|2026-07-15 15:42:34
- 6968cbd9-e233-4652-8da3-b03e6758f1b4|PATCH_TOPIC2_READY_DONE_BEFORE_FRUSTRATION_V1:handled_by_canon_ready_done|2026-07-15 15:42:34
- 6968cbd9-e233-4652-8da3-b03e6758f1b4|TOPIC2_CONFIRM_CHILD_DONE_READY_PHRASE|2026-07-15 15:42:33
- 6968cbd9-e233-4652-8da3-b03e6758f1b4|TOPIC2_DONE_BLOCKED_REASON:no_estimate_generated|2026-07-15 15:42:33
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|state:DONE|2026-07-15 15:42:33
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_DONE_CONTRACT_OK|2026-07-15 15:42:33
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_EXPLICIT_CONFIRM:ready_done_phrase|2026-07-15 15:42:33
- 6968cbd9-e233-4652-8da3-b03e6758f1b4|PATCH_TOPIC2_ACTIVE_PROJECT_BLOCK_MEMORY_RECALL_V1:SKIP_MEMORY_RECALL_ACTIVE_PROJECT|2026-07-15 15:42:33
- 6968cbd9-e233-4652-8da3-b03e6758f1b4|TOPIC2_OWNER_AUTHORIZED_FINALIZATION_FULL_LIVE_20260715|2026-07-15 15:42:33
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_DONE_BLOCKED_UNTIL_EXPLICIT_CONFIRM|2026-07-15 15:40:39
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_AWAITING_CONFIRMATION_WITH_ARTIFACTS|2026-07-15 15:40:39
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_TELEGRAM_DELIVERED|2026-07-15 15:40:39
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_MESSAGE_THREAD_ID_OK|2026-07-15 15:40:39
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_DRIVE_LINKS_SAVED:xlsx=https://drive.google.com/file/d/1QtmRdSIeFBrFXSOwNEjxYm9R-tk0vYUx/view:pdf=https://drive.google.com/file/d/18knXymc3Po2C1ihWRo2j-0LGC025j_Fs/view|2026-07-15 15:40:38
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_DRIVE_UPLOAD_PDF_OK|2026-07-15 15:40:38
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PDF_TOTALS_MATCH_XLSX|2026-07-15 15:40:36
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PDF_CYRILLIC_OK|2026-07-15 15:40:36
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_PDF_CREATED|2026-07-15 15:40:36
- d019c976-5e46-475d-bcd7-c9f349eb0ea1|TOPIC2_DRIVE_TOPIC_FOLDER_OK|2026-07-15 15:40:36

## MEMORY_DB_COUNT
- 5393

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 33, "updated_at": "2026-07-16T03:30:43.399553+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-07-16T03:30:43.400288+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-07-16T03:30:43.373916+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-07-16T03:30:43.374485+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-07-16T03:30:43.315550+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-07-16T03:30:43.316156+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-07-16T03:30:43.300946+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-07-16T03:30:43.301395+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-07-16T03:30:43.262747+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-07-16T03:30:43.263316+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-16T03:30:43.130487+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-07-16T03:30:43.130360+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-16T03:30:43.130118+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-16T03:30:43.129788+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-16T03:30:43.129465+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-07-16T03:30:43.129104+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-16T03:30:43.128913+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-16T03:30:43.128494+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-16T03:30:43.128135+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-16T03:30:43.127952+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-16T03:30:43.127375+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-07-16T03:30:43.126861+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-16T03:30:43.126684+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-16T03:30:43.126289+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-07-16T03:30:43.125934+00:00

## JOURNAL_AREAL_TASK_WORKER_60
Stopping areal-task-worker.service - Areal Task Worker...
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

## JOURNAL_TELEGRAM_INGRESS_30
2026-07-07 23:27:15,922 INFO DAEMON: Task fc03d3ed-876d-470c-a037-febc737ee0cb created state=NEW topic_id=2
2026-07-07 23:27:15,923 INFO DAEMON: Update id=262222486 is handled. Duration 11 ms by bot id=8216054898
2026-07-07 23:27:39,699 INFO DAEMON: Update id=262222487 is handled. Duration 88 ms by bot id=8216054898
2026-07-08 16:10:36,952 ERROR DAEMON: Failed to fetch updates - TelegramNetworkError: HTTP Client says - ClientOSError: [Errno 104] Connection reset by peer
2026-07-08 16:10:36,954 WARNING DAEMON: Sleep for 1.000000 seconds and try again... (tryings = 0, bot id = 8216054898)
2026-07-08 16:10:48,081 INFO DAEMON: Connection established (tryings = 1, bot id = 8216054898)
2026-07-10 13:47:56,774 INFO DAEMON: file_cache is only supported with oauth2client<4.0.0
2026-07-10 13:47:59,524 INFO DAEMON: Task 8414e015-55c7-46dd-99da-f51524eb37ec created state=NEW topic_id=2
2026-07-10 13:47:59,610 INFO DAEMON: Update id=262222488 is handled. Duration 4354 ms by bot id=8216054898
2026-07-10 13:48:37,095 INFO DAEMON: Update id=262222489 is handled. Duration 139 ms by bot id=8216054898
2026-07-10 13:49:12,838 INFO DAEMON: Update id=262222490 is handled. Duration 91 ms by bot id=8216054898
2026-07-10 13:49:34,782 INFO DAEMON: Update id=262222491 is handled. Duration 72 ms by bot id=8216054898
2026-07-10 13:49:51,009 INFO DAEMON: Update id=262222492 is handled. Duration 73 ms by bot id=8216054898
2026-07-14 04:25:35,681 ERROR DAEMON: Failed to fetch updates - TelegramServerError: Telegram server says - Bad Gateway
2026-07-14 04:25:35,695 WARNING DAEMON: Sleep for 1.000000 seconds and try again... (tryings = 0, bot id = 8216054898)
2026-07-14 04:26:12,504 INFO DAEMON: Connection established (tryings = 1, bot id = 8216054898)
2026-07-15 15:36:52,315 INFO DAEMON: Update id=262222493 is handled. Duration 394 ms by bot id=8216054898
2026-07-15 15:43:22,112 INFO DAEMON: Update id=262222494 is handled. Duration 271 ms by bot id=8216054898
2026-07-15 15:48:53,992 INFO DAEMON: Update id=262222495 is handled. Duration 208 ms by bot id=8216054898
2026-07-15 15:54:01,337 INFO DAEMON: Update id=262222496 is handled. Duration 125 ms by bot id=8216054898
2026-07-15 15:58:13,236 INFO DAEMON: Update id=262222497 is handled. Duration 95 ms by bot id=8216054898
2026-07-15 16:33:05,632 INFO DAEMON: Update id=262222498 is handled. Duration 141 ms by bot id=8216054898
2026-07-15 16:43:45,829 INFO DAEMON: Update id=262222499 is handled. Duration 153 ms by bot id=8216054898
2026-07-15 16:44:16,485 INFO DAEMON: Update id=262222500 is handled. Duration 66 ms by bot id=8216054898
2026-07-15 17:23:35,072 INFO DAEMON: Task 9062c46c-7156-4fd0-96e5-5020c28f8618 created state=NEW topic_id=2
2026-07-15 17:23:35,072 INFO DAEMON: Update id=262222501 is handled. Duration 18 ms by bot id=8216054898
2026-07-15 17:23:49,052 INFO DAEMON: Update id=262222502 is handled. Duration 85 ms by bot id=8216054898
2026-07-15 17:24:25,867 INFO DAEMON: Task 0d725696-a8c4-4545-85e0-9d4acaa91c1a created state=NEW topic_id=2
2026-07-15 17:24:25,867 INFO DAEMON: Update id=262222503 is handled. Duration 21 ms by bot id=8216054898
2026-07-15 17:25:08,108 INFO DAEMON: Update id=262222504 is handled. Duration 96 ms by bot id=8216054898
