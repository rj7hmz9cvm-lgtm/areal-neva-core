# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-07-08T15:29:38.562441+00:00
git_sha_before_commit: d432748b77b272d919057ea9f74c7e6e97efce42
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
d432748b FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
a2496456 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c2915588 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c3b34fee FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
1e721c95 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
1e5d1ca1 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
aa11e51e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
028454d4 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
48de82b7 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6cfef51a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
3250690a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
822e44ce FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
5d2b372a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
9a352d11 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c8638379 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
988685fa FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
55d15654 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c496e76a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7798c026 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
97981aca FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
4970efe7 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
b591dd60 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
4003e7db FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
1bc2f8c8 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
8acca6bd FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
810a9858 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
31837525 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c3d1a6b7 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
b437d511 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c92fdde2 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

## GIT_SHOW_STAT_HEAD
commit d432748b77b272d919057ea9f74c7e6e97efce42
Author: Ila <ilakuznecov@mac.local>
Date:   Wed Jul 8 18:00:08 2026 +0300

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
 docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md       | 160 ++++++++++-----------
 .../SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md |   4 +-
 docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md   |  48 +++----
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
 73 files changed, 249 insertions(+), 249 deletions(-)

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
- CANCELLED|876
- DONE|743
- ARCHIVED|381

## CORE_DB_OPEN_TASKS
- 0

## LATEST_TASKS_15
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
- be35fd19-316c-40d5-9c81-4d648c2083a2|5|text|DONE|[VOICE] Это уже другой акт. Это не Ропшинское шоссе. Это Агалатова монолит.|Контекст технадзора принят к текущему акту
Объект / адрес: Ропшинское шоссе 198
Основание выезда: запрос заказчика через Авито
Источник заявки: Авито
Фото в пак|2026-07-07 12:42:03

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
- fc03d3ed-876d-470c-a037-febc737ee0cb|cancelled|2026-07-07T20:27:39.613944+00:00
- fc03d3ed-876d-470c-a037-febc737ee0cb|TOPIC2_CANONICAL_REROUTE_V2:CANONICAL_HANDLED|2026-07-07 20:27:19
- fc03d3ed-876d-470c-a037-febc737ee0cb|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:clarification|2026-07-07 20:27:19
- fc03d3ed-876d-470c-a037-febc737ee0cb|PATCH_TOPIC2_HISTORICAL_PROJECT_MEMORY_RECALL_V1:core_task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|2026-07-07 20:27:17
- fc03d3ed-876d-470c-a037-febc737ee0cb|TOPIC2_PUBLIC_RESULT_CANON_VIOLATION:missing_canon_header|2026-07-07 20:27:17
- fc03d3ed-876d-470c-a037-febc737ee0cb|TOPIC2_DONE_ONLY_AFTER_USER_YES_V1:BLOCKED_DONE_TO_AWAITING_CONFIRMATION|2026-07-07 20:27:17
- fc03d3ed-876d-470c-a037-febc737ee0cb|PATCH_TOPIC2_ACTIVE_PROJECT_BLOCK_MEMORY_RECALL_V1:SKIP_MEMORY_RECALL_ACTIVE_PROJECT|2026-07-07 20:27:17
- fc03d3ed-876d-470c-a037-febc737ee0cb|created:NEW|2026-07-07T20:27:15.920388+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_DONE_CONTRACT_OK:repaired_after_finish_phrase|2026-07-07 20:24:27
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|state:DONE|2026-07-07 20:24:27
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_DONE_BLOCKED_REASON:no_estimate_generated|2026-07-07 20:24:27
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_EXPLICIT_CONFIRM:from_user_finish_phrase_repaired|2026-07-07 20:24:27
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|cancelled|2026-07-07T20:21:45.749553+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_PRICE_ENRICHMENT_DONE|2026-07-07 20:21:42
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|P3_TOPIC2_CLARIFICATION|2026-07-07 20:21:42
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_PRICE_ENRICHMENT_STARTED|2026-07-07 20:21:42
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_ESTIMATE_CONTEXT_HASH:bb350d328d85a11f|2026-07-07 20:21:42
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|P6_TOPIC2_CURRENT_ESTIMATE_ROUTE|2026-07-07 20:21:42
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|PATCH_TOPIC2_FINAL_DRIVE_FLOW_FIX_V1:FRESH_FALLBACK_BLOCKED_ALREADY_GENERATED|2026-07-07 20:21:41
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|clarified:Отмена задач|2026-07-07T20:21:41.537837+00:00

## MEMORY_DB_COUNT
- 5357

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 33, "updated_at": "2026-07-08T15:29:38.362450+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-07-08T15:29:38.362915+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-07-08T15:29:38.337220+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-07-08T15:29:38.337861+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-07-08T15:29:38.288112+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-07-08T15:29:38.288614+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-07-08T15:29:38.279617+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-07-08T15:29:38.280299+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-07-08T15:29:38.237266+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-07-08T15:29:38.237924+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-08T15:29:38.130096+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-07-08T15:29:38.130009+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-08T15:29:38.129945+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-08T15:29:38.129865+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-08T15:29:38.129811+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-07-08T15:29:38.129750+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-08T15:29:38.129676+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-08T15:29:38.129520+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-08T15:29:38.129330+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-08T15:29:38.129227+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-08T15:29:38.128690+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-07-08T15:29:38.128380+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-08T15:29:38.128277+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-08T15:29:38.128050+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-07-08T15:29:38.127812+00:00

## JOURNAL_AREAL_TASK_WORKER_60
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 10.511s CPU time, 111.5M memory peak, 0B memory swap peak.
areal-task-worker.service: Scheduled restart job, restart counter is at 7694.
Started areal-task-worker.service - Areal Task Worker.
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

## JOURNAL_TELEGRAM_INGRESS_30
2026-07-07 17:01:49,245 INFO DAEMON: Update id=262222474 is handled. Duration 94 ms by bot id=8216054898
2026-07-07 17:01:56,768 INFO DAEMON: Update id=262222475 is handled. Duration 72 ms by bot id=8216054898
2026-07-07 17:02:02,662 INFO DAEMON: Update id=262222476 is handled. Duration 80 ms by bot id=8216054898
2026-07-07 17:02:08,910 INFO DAEMON: Update id=262222477 is handled. Duration 70 ms by bot id=8216054898
2026-07-07 23:06:59,913 INFO DAEMON: STT env check groq=True
2026-07-07 23:06:59,914 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_12358.ogg size=56955 model=whisper-large-v3-turbo
2026-07-07 23:07:00,173 INFO DAEMON: STT http_status=200
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
