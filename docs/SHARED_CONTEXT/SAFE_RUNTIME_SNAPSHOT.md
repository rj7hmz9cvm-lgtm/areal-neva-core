# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-07-12T13:25:01.763559+00:00
git_sha_before_commit: 66d279abd75d59aeecda565ecc29b99f2862cd73
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
66d279ab FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
30bae2a5 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
ea7d80d7 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
11c75dd9 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
665a9443 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
d92875b6 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
2a8d5dc8 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
91c6f66c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
ca962c99 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
fcb981f4 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
a9a1483c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6ffdad13 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
578b4de2 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
e5a44bc2 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
61cca70c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c7c5b743 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
43579ef2 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
43b205e4 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
5d1ec30e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
9de78a38 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7200a851 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7960c541 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
cdcacf8f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
df18bff2 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
4327e5d0 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
4952b143 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
f61d7f3b FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
933bf5ff FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
23e35bef FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
a613490d FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

## GIT_SHOW_STAT_HEAD
commit 66d279abd75d59aeecda565ecc29b99f2862cd73
Author: root <root@graceful-olive.ptr.network>
Date:   Sun Jul 12 16:20:17 2026 +0300

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
- FAILED|3053
- CANCELLED|877
- DONE|743
- ARCHIVED|381

## CORE_DB_OPEN_TASKS
- 0

## LATEST_TASKS_15
- 8414e015-55c7-46dd-99da-f51524eb37ec|2|drive_file|CANCELLED|{"file_id": "1TunRGTRQg-4HJSKsxH-FzKN-3ceT56Me", "file_name": "ирина ар проект.pdf", "mime_type": "application/pdf", "ca|ирина ар проект.pdf принят и прочитан. Нашёл текущие проектные строки:
- явная ВОР/спецификация не найдена

Шаблонные строки из старых смет не подставляю. Подтв|2026-07-10T10:49:50.940580+00:00
- fc03d3ed-876d-470c-a037-febc737ee0cb|2|text|CANCELLED|Мы с тобой последнюю смету считали?|файл принят и прочитан. Нашёл текущие проектные строки:
- явная ВОР/спецификация не найдена

Шаблонные строки из старых смет не подставляю. Подтверди, пожалуйст|2026-07-07T20:27:39.613851+00:00
- 8bf5d72b-2698-4cb3-a27d-5a1f79622aed|2|text|DONE|Задача завершена|Выбери уровень цен: 1 дешёвые / 2 средние / 3 надёжные / 4 вручную|2026-07-07 20:21:07
- e767c66f-d3d2-417d-b04b-56370cf80637|2|text|CANCELLED|Всё верно посчитал?|None|2026-07-07 20:20:49
- 6e6cf69b-9ab0-4456-884f-06181875a906|2|text|DONE|[VOICE] стоимость материалов стеновые панели сэндвич панели 3800 рублей за метр квадратный потолочные сэндвич панели 420|Уточнение добавлено к исходному ТЗ|2026-07-07 20:07:33
- ad69b7c1-8d6c-4007-bb05-f9ce0cfc63bc|2|text|FAILED|[VOICE] Поставь здесь панели ценой 3200 – это стеновые панели и 3600 – это потолочные панели, кровельные.|Что строим: дом, ангар, склад, фундамент или кровлю?|2026-07-07 20:17:03
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|2|text|DONE|Эти два файла это один объединённый проект. Выведи одним сообщением все найденные объёмы из АР и КР по проекту. Цены не |✅ Смета по извлечённым позициям готова

Объект: АР + КР
Файлы: АР + КР
Позиции: 15
Цены: cache/memory/archive + Sonar по недостающим

Не закрыто по проекту:
- o|2026-07-07 20:24:27
- 341cde94-b085-4a37-ae42-abcce3dc32f3|2|text|FAILED|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|341cde94-b085-4a37-ae42-abcce3dc32f3_Раздел 4 - КР.pdf принят и прочитан. Нашёл текущие проектные строки:
- БСТ В30 П4 W4: 0.05 м³
- БСТ В25 П4 W4: 11.08 м³
- Б|2026-07-07 16:48:52
- 5e523179-e0b9-41b9-96b7-08e4fdb3accb|2|text|FAILED|Эти два файла это один проект. Для начала найди и вытащи все объёмы из АР и КР.|Стадия Р_АР.pdf принят и прочитан. Нашёл текущие проектные строки:
- БСТ В30 П4 W4: 0.05 м³
- БСТ В25 П4 W4: 11.08 м³
- БСТ В25 П4 W4: 132.86 м³
- БСТ В25 П4 W4|2026-07-07 16:15:41
- 9d7440b6-a7ab-4600-948f-e1b0e91510d4|2|text|FAILED|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|Стадия Р_АР.pdf принят и прочитан. Нашёл текущие проектные строки:
- БСТ В30 П4 W4: 0.05 м³
- БСТ В25 П4 W4: 11.08 м³
- БСТ В25 П4 W4: 132.86 м³
- БСТ В25 П4 W4|2026-07-07 16:05:42
- e65b555f-62e2-4a86-b203-39b3c1fd110c|2|text|FAILED|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|e65b555f-62e2-4a86-b203-39b3c1fd110c_Раздел 4 - КР.pdf принят и прочитан. Нашёл текущие проектные строки:
- БСТ В30 П4 W4: 0.05 м³
- БСТ В25 П4 W4: 11.08 м³
- Б|2026-07-07 15:58:42
- 83f43cd4-4d12-4192-978b-462f7ad556a5|2|text|CANCELLED|[VOICE] Это другая задача.|None|2026-07-07 14:01:39
- 229c5e93-a610-4b0f-8ad0-b5c2b14b407c|2|text|CANCELLED|[VOICE] Это тут при чем? Я вообще не понимаю.|None|2026-07-07 14:01:28
- b5fa5fbc-a33a-4943-82a8-a9aba939e728|2|text|CANCELLED|[VOICE] Так, ты сможешь мне найти цены по коммерческому предложению и заполнить таблицу так, как мне нужно?|Уточни этажность|2026-07-07T14:02:08.843107+00:00
- e473dafd-f332-4c83-9e36-00a319659cea|2|text|CANCELLED|Я тебе скидывал два проекта который ты должен был объединить в один|Уточни тип фундамента|2026-07-07T13:32:51.693390+00:00

## LATEST_FAILED_10
- ad69b7c1-8d6c-4007-bb05-f9ce0cfc63bc|2|[VOICE] Поставь здесь панели ценой 3200 – это стеновые панели и 3600 – это потолочные панели, кровельные.|STALE_TIMEOUT|2026-07-07 20:17:03
- 341cde94-b085-4a37-ae42-abcce3dc32f3|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 16:48:52
- 5e523179-e0b9-41b9-96b7-08e4fdb3accb|2|Эти два файла это один проект. Для начала найди и вытащи все объёмы из АР и КР.|STALE_TIMEOUT|2026-07-07 16:15:41
- 9d7440b6-a7ab-4600-948f-e1b0e91510d4|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 16:05:42
- e65b555f-62e2-4a86-b203-39b3c1fd110c|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 15:58:42
- 7300d5f5-94eb-488d-95e1-2f0b516740de|5|{"file_id": "1E1iHSjskAwDbfr3xk8EUsD3KP2FBab-i", "file_name": "photo_-1003725299009_12206.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:28
- 2d607bf6-c874-4a5b-9cfd-f7d89b44f866|5|{"file_id": "1eqCReGl0w3ra1m5_Qn0oX9CcYxvWor0v", "file_name": "photo_-1003725299009_12208.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:28
- 68dceab3-4cd1-43cd-92f4-2bed426d2b88|5|{"file_id": "1ebYctoc4X_3venU6COcDVSTDJ_uYnNAA", "file_name": "photo_-1003725299009_12204.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:26
- e9400bf5-ad48-44d3-ba57-ed6cdc261fe7|5|{"file_id": "1j9LcyzClfYSrsqQXWAqITi8WDHHuiwJw", "file_name": "photo_-1003725299009_12205.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:26
- 3b365ab1-9d1d-40c7-92da-ce0c9db43157|5|{"file_id": "1FruamdHLMgllCW3qWggLb3eOcxx_dDFw", "file_name": "photo_-1003725299009_12203.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:24

## LATEST_TASK_HISTORY_20
- 8414e015-55c7-46dd-99da-f51524eb37ec|cancelled|2026-07-10T10:49:50.940725+00:00
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_MISSING_GATE_ANTILOOP_BLOCKED_DEFAULTS:count=3|2026-07-10 10:49:46
- 8414e015-55c7-46dd-99da-f51524eb37ec|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:clarification|2026-07-10 10:49:46
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_PDF_SPEC_EMPTY|2026-07-10 10:49:46
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_PDF_SPEC_EXTRACTOR_STARTED|2026-07-10 10:49:46
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_CLARIFIED_HISTORY_MERGED_BEFORE_GATES|2026-07-10 10:49:46
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_FILE_INTAKE_LOCAL_PATH_OK|2026-07-10 10:49:46
- 8414e015-55c7-46dd-99da-f51524eb37ec|FILE_INTAKE_ROUTER_TOPIC2_CANONICAL_ROUTE|2026-07-10 10:49:46
- 8414e015-55c7-46dd-99da-f51524eb37ec|clarified:да по проекту|2026-07-10T10:49:34.715908+00:00
- 8414e015-55c7-46dd-99da-f51524eb37ec|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:clarification|2026-07-10 10:49:24
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_PDF_SPEC_EMPTY|2026-07-10 10:49:24
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_PDF_SPEC_EXTRACTOR_STARTED|2026-07-10 10:49:24
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_CLARIFIED_HISTORY_MERGED_BEFORE_GATES|2026-07-10 10:49:24
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_FILE_INTAKE_LOCAL_PATH_OK|2026-07-10 10:49:24
- 8414e015-55c7-46dd-99da-f51524eb37ec|FILE_INTAKE_ROUTER_TOPIC2_CANONICAL_ROUTE|2026-07-10 10:49:24
- 8414e015-55c7-46dd-99da-f51524eb37ec|clarified:Считать только по найденным позициям согласно проекта ничего лишнего не выдумывать|2026-07-10T10:49:12.755452+00:00
- 8414e015-55c7-46dd-99da-f51524eb37ec|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:clarification|2026-07-10 10:48:49
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_PDF_SPEC_EMPTY|2026-07-10 10:48:49
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_PDF_SPEC_EXTRACTOR_STARTED|2026-07-10 10:48:49
- 8414e015-55c7-46dd-99da-f51524eb37ec|TOPIC2_CLARIFIED_HISTORY_MERGED_BEFORE_GATES|2026-07-10 10:48:49

## MEMORY_DB_COUNT
- 5360

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 33, "updated_at": "2026-07-12T13:20:11.212872+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-07-12T13:20:11.213500+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-07-12T13:20:11.188655+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-07-12T13:20:11.189356+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-07-12T13:20:11.132230+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-07-12T13:20:11.132708+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-07-12T13:20:11.120712+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-07-12T13:20:11.121376+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-07-12T13:20:11.078428+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-07-12T13:20:11.079342+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-12T13:20:10.976712+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-07-12T13:20:10.976630+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-12T13:20:10.976550+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-12T13:20:10.976423+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-12T13:20:10.976352+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-07-12T13:20:10.976283+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-12T13:20:10.976201+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-12T13:20:10.976038+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-12T13:20:10.975830+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-12T13:20:10.975658+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-12T13:20:10.975271+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-07-12T13:20:10.974982+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-12T13:20:10.974741+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-12T13:20:10.974105+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-07-12T13:20:10.973728+00:00

## JOURNAL_AREAL_TASK_WORKER_60
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 2.645s CPU time, 110.5M memory peak, 0B memory swap peak.
areal-task-worker.service: Scheduled restart job, restart counter is at 7695.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 1.944s CPU time, 110.5M memory peak, 0B memory swap peak.
areal-task-worker.service: Scheduled restart job, restart counter is at 7696.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 6.583s CPU time, 111.5M memory peak, 0B memory swap peak.
areal-task-worker.service: Scheduled restart job, restart counter is at 7697.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 4.188s CPU time.
areal-task-worker.service: Scheduled restart job, restart counter is at 7698.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 10.808s CPU time, 112.1M memory peak, 0B memory swap peak.
areal-task-worker.service: Scheduled restart job, restart counter is at 7699.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 9.616s CPU time.
areal-task-worker.service: Scheduled restart job, restart counter is at 7700.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 6.488s CPU time, 111.1M memory peak, 0B memory swap peak.
areal-task-worker.service: Scheduled restart job, restart counter is at 7701.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 4.875s CPU time, 111.1M memory peak, 0B memory swap peak.
areal-task-worker.service: Scheduled restart job, restart counter is at 7702.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 3.407s CPU time, 110.8M memory peak, 0B memory swap peak.
areal-task-worker.service: Scheduled restart job, restart counter is at 7703.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 4.608s CPU time.
areal-task-worker.service: Scheduled restart job, restart counter is at 7704.
Started areal-task-worker.service - Areal Task Worker.
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=e473dafd-f332-4c83-9e36-00a319659cea reason=missing_canon_header
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=fc03d3ed-876d-470c-a037-febc737ee0cb reason=missing_canon_header
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:672: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),

## JOURNAL_TELEGRAM_INGRESS_30
2026-07-07 23:07:00,174 INFO DAEMON: STT ok transcript_len=97
2026-07-07 23:07:00,279 INFO DAEMON: Task ad69b7c1-8d6c-4007-bb05-f9ce0cfc63bc created state=NEW topic_id=2
2026-07-07 23:07:00,280 INFO DAEMON: Update id=262222478 is handled. Duration 700 ms by bot id=8216054898
2026-07-07 23:07:32,042 INFO DAEMON: STT env check groq=True
2026-07-07 23:07:32,042 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_12362.ogg size=86262 model=whisper-large-v3-turbo
2026-07-07 23:07:32,326 INFO DAEMON: STT http_status=200
2026-07-07 23:07:32,327 INFO DAEMON: STT ok transcript_len=175
2026-07-07 23:07:32,423 INFO DAEMON: Task 6e6cf69b-9ab0-4456-884f-06181875a906 created state=NEW topic_id=2
2026-07-07 23:07:32,423 INFO DAEMON: Update id=262222479 is handled. Duration 724 ms by bot id=8216054898
2026-07-07 23:20:49,317 INFO DAEMON: Task e767c66f-d3d2-417d-b04b-56370cf80637 created state=NEW topic_id=2
2026-07-07 23:20:49,317 INFO DAEMON: Update id=262222480 is handled. Duration 13 ms by bot id=8216054898
2026-07-07 23:21:06,162 INFO DAEMON: Task 8bf5d72b-2698-4cb3-a27d-5a1f79622aed created state=NEW topic_id=2
2026-07-07 23:21:06,162 INFO DAEMON: Update id=262222481 is handled. Duration 14 ms by bot id=8216054898
2026-07-07 23:21:20,137 INFO DAEMON: Update id=262222482 is handled. Duration 95 ms by bot id=8216054898
2026-07-07 23:21:33,734 INFO DAEMON: Update id=262222483 is handled. Duration 216 ms by bot id=8216054898
2026-07-07 23:21:41,607 INFO DAEMON: Update id=262222484 is handled. Duration 85 ms by bot id=8216054898
2026-07-07 23:21:45,831 INFO DAEMON: Update id=262222485 is handled. Duration 85 ms by bot id=8216054898
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
