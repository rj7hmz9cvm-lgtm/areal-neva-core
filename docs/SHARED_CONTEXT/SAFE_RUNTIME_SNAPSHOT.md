# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-07-07T19:24:08.536376+00:00
git_sha_before_commit: 75f68ff0c25d5c4594ccc3083e30a8f7c1a4611b
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
75f68ff0 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c68b0dc2 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
0c9de198 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
3eedfd5e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
e4b5fdc5 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
597bf6de FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6720ac21 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
0587311f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
56f547b8 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
0b845913 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c279b6bb FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c4473391 docs: save 2026-07-07 topic2 search ocr handoff
e80be12a Record file memory duplicate guard live repair
8a446fd7 Record memory lifecycle repair handoff
98b5133f Fix topic 500 search delivery and output contract
ed4c3c7b topic2: append live rules and save repair state
0ebd1431 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
5d528b38 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
5050af0a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
cdfc7240 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
5ca02cdd FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
20c42a8c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6bce30b7 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
486f4570 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
835217ef FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
2f5dff4c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
fc44f3ce FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
a939ed12 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
a9784f65 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
931896b5 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

## GIT_SHOW_STAT_HEAD
commit 75f68ff0c25d5c4594ccc3083e30a8f7c1a4611b
Author: root <root@graceful-olive.ptr.network>
Date:   Tue Jul 7 21:54:21 2026 +0300

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
 .../ORCHESTRA_FULL_CONTEXT_MANIFEST.json           |  28 +-
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
 .../ORCHESTRA_FULL_CONTEXT_PART_011.md             |  21 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_012.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_013.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_014.md             |  71 ++-
 .../ORCHESTRA_FULL_CONTEXT_PART_015.md             | 474 +++------------------
 .../ORCHESTRA_FULL_CONTEXT_PART_016.md             | 423 +++++++++++++++++-
 .../ORCHESTRA_FULL_CONTEXT_PART_017.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_018.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_019.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_020.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_021.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_022.md             |   4 +-
 docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md       |  82 ++--
 .../SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md |   4 +-
 docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md   |  66 +--
 docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md         |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_0_COMMON.md       |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_11_VIDEO.md       |   4 +-
 .../TOPICS/topic_210_PROEKTIROVANIE.md             |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_2_STROYKA.md      |  22 +-
 .../TOPICS/topic_3008_KODY_MOZGOV.md               |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_4569_CRM_LEADS.md |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_500_VEB_POISK.md  |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_5_TEKHNADZOR.md   |   4 +-
 .../SHARED_CONTEXT/TOPICS/topic_6104_JOB_SEARCH.md |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_794_DEVOPS.md     |   4 +-
 .../TOPICS/topic_961_AVTOZAPCHASTI.md              |   4 +-
 docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md          |   4 +-
 73 files changed, 755 insertions(+), 696 deletions(-)

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
- FAILED|3052
- CANCELLED|874
- DONE|740
- ARCHIVED|381
- IN_PROGRESS|1

## CORE_DB_OPEN_TASKS
- 1

## LATEST_TASKS_15
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|2|text|IN_PROGRESS|Эти два файла это один объединённый проект. Выведи одним сообщением все найденные объёмы из АР и КР по проекту. Цены не |✅ Проектные позиции и объёмы извлечены

Project facts:
- 18.0 x 36.0
- 648 м2
- 8.54
- стены сэндвич-панель 100 мм
- кровля сэндвич-панель 150 мм
- одноэтажное |2026-07-07 19:22:53
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
- f18ec8db-bc14-4098-a868-dbb3d68b9d90|2|text|DONE|[VOICE] Вся информация есть в проектной документации, там все написано.

УТОЧНЕНИЕ К ИСХОДНОМУ ТЗ:
Эти файлы это один пр|Реплика закрыта: привязка к исходному проекту восстановлена|2026-07-07 12:49:48
- 1d2505b9-1e69-4e54-ba28-ee0558c3ce43|5|text|DONE|[VOICE] Объект Агала Тово Монолит.|Контекст технадзора принят к текущему акту
Объект / адрес: Ропшинское шоссе 198
Основание выезда: запрос заказчика через Авито
Источник заявки: Авито
Фото в пак|2026-07-07 12:40:46
- ae452bae-6957-476e-a76f-45980262b938|5|text|DONE|[VOICE] Это другой объект. Давай назовем этот объект Агалатова монолит. И соответственно какие нарушения ты видишь на фо|Принял как запрос анализа фото по технадзору, а не как пояснение к фото.
Фото в текущем пакете: 29 шт.
DefectCard сформировано/обновлено: 24.
1. Фото: photo_-10|2026-07-07 12:40:10
- 3fb639a0-d76b-44f4-9331-0c72433a9da0|2|text|CANCELLED|[VOICE] вся информация есть в проекте сколько можно ждать то еще тебя проекты документации блять уже невозносимо ждать н|P6E67_MERGED_TO_PARENT_TASK 287a613c-c47d-4fae-9a71-d57fa3f2b762|2026-07-07 12:39:40
- 6629e9f0-e401-4952-bf0d-61cd611448a1|5|text|DONE|[VOICE] Какие нарушения есть на данном фото и есть ли они вообще в принципе?|Пояснение принято к фото: photo_-1003725299009_12203.jpg. В пакете технадзора: 24 шт. Акт не формирую без отдельной команды|2026-07-07 11:14:08

## LATEST_FAILED_10
- 341cde94-b085-4a37-ae42-abcce3dc32f3|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 16:48:52
- 5e523179-e0b9-41b9-96b7-08e4fdb3accb|2|Эти два файла это один проект. Для начала найди и вытащи все объёмы из АР и КР.|STALE_TIMEOUT|2026-07-07 16:15:41
- 9d7440b6-a7ab-4600-948f-e1b0e91510d4|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 16:05:42
- e65b555f-62e2-4a86-b203-39b3c1fd110c|2|Эти два файла это один проект. Посчитай стоимость строительства и материалов по проекту. Цены работ и материалов найди в|STALE_TIMEOUT|2026-07-07 15:58:42
- 7300d5f5-94eb-488d-95e1-2f0b516740de|5|{"file_id": "1E1iHSjskAwDbfr3xk8EUsD3KP2FBab-i", "file_name": "photo_-1003725299009_12206.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:28
- 2d607bf6-c874-4a5b-9cfd-f7d89b44f866|5|{"file_id": "1eqCReGl0w3ra1m5_Qn0oX9CcYxvWor0v", "file_name": "photo_-1003725299009_12208.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:28
- 68dceab3-4cd1-43cd-92f4-2bed426d2b88|5|{"file_id": "1ebYctoc4X_3venU6COcDVSTDJ_uYnNAA", "file_name": "photo_-1003725299009_12204.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:26
- e9400bf5-ad48-44d3-ba57-ed6cdc261fe7|5|{"file_id": "1j9LcyzClfYSrsqQXWAqITi8WDHHuiwJw", "file_name": "photo_-1003725299009_12205.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:26
- 3b365ab1-9d1d-40c7-92da-ce0c9db43157|5|{"file_id": "1FruamdHLMgllCW3qWggLb3eOcxx_dDFw", "file_name": "photo_-1003725299009_12203.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:24
- f8405584-64a9-4926-8863-b1bfc4a9d113|5|{"file_id": "1j9_efbI0fO1ex5vTjNrBtrfQ6HtN7Go0", "file_name": "photo_-1003725299009_12207.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:24

## LATEST_TASK_HISTORY_20
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_MULTIFILE_PROJECT_PDF_ATTACHED:Раздел 4 - КР.pdf|2026-07-07 19:22:53
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_PUBLIC_OUTPUT_TOTALS_GROUPED|2026-07-07T19:22:52.723383+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_PUBLIC_OUTPUT_INTERNAL_KEYS_HIDDEN|2026-07-07T19:22:52.723383+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_PUBLIC_OUTPUT_UNITS_NORMALIZED|2026-07-07T19:22:52.723383+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_MISSING_ITEMS_REPORTED|2026-07-07T19:22:52.723383+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_TOTALS_BY_MATERIAL_CALCULATED|2026-07-07T19:22:52.723383+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_CONSTRUCTION_ITEMS_DEDUPED|2026-07-07T19:22:52.723383+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_VOLUME_FACTS_NORMALIZED|2026-07-07T19:22:52.723383+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_PROJECT_POSITIONS_EXTRACTED|2026-07-07T19:22:52.723383+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_PROJECT_BUNDLE_READY|2026-07-07T19:22:52.723383+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|state:FAILED|2026-07-07 19:05:17
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_NORMALIZED_DEDUP_LIVE_TEST_SENT|2026-07-07T18:55:16.381388+00:00
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|state:FAILED|2026-07-07 18:23:44
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|CODEX_ONE_OFF_PROJECT_POSITIONS_ONLY_SENT|2026-07-07 18:13:43
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_SMETA_GENERATION_BLOCKED_BY_POSITIONS_ONLY_MODE|2026-07-07 18:13:43
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_PRICE_SEARCH_BLOCKED_BY_POSITIONS_ONLY_MODE|2026-07-07 18:13:43
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_MISSING_ITEMS_REPORTED|2026-07-07 18:13:43
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_POSITIONS_EXTRACTION_COMPLETE_YES|2026-07-07 18:13:43
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_TOTALS_BY_MATERIAL_CALCULATED|2026-07-07 18:13:43
- 7a06ad98-7bd1-4d1c-af57-7b375ade17e1|TOPIC2_FOUNDATION_TOTALS_CALCULATED|2026-07-07 18:13:43

## MEMORY_DB_COUNT
- 5353

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 33, "updated_at": "2026-07-07T19:24:08.231052+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-07-07T19:24:08.231813+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-07-07T19:24:08.188068+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-07-07T19:24:08.190139+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-07-07T19:24:08.099415+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-07-07T19:24:08.100004+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-07-07T19:24:08.084580+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-07-07T19:24:08.085134+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-07-07T19:24:08.041987+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-07-07T19:24:08.043118+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-07T19:24:07.918683+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-07-07T19:24:07.918575+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-07T19:24:07.918466+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-07T19:24:07.918341+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-07T19:24:07.918244+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-07-07T19:24:07.918152+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T19:24:07.918052+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T19:24:07.917821+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T19:24:07.917582+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T19:24:07.917452+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T19:24:07.917072+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-07-07T19:24:07.916778+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T19:24:07.916667+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T19:24:07.916467+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-07-07T19:24:07.916256+00:00

## JOURNAL_AREAL_TASK_WORKER_60
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
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

## JOURNAL_TELEGRAM_INGRESS_30
2026-07-07 15:42:02,741 INFO DAEMON: STT ok transcript_len=67
2026-07-07 15:42:02,877 INFO DAEMON: Task be35fd19-316c-40d5-9c81-4d648c2083a2 created state=NEW topic_id=5
2026-07-07 15:42:02,878 INFO DAEMON: Update id=262222466 is handled. Duration 605 ms by bot id=8216054898
2026-07-07 16:31:08,460 INFO DAEMON: Task e473dafd-f332-4c83-9e36-00a319659cea created state=NEW topic_id=2
2026-07-07 16:31:08,460 INFO DAEMON: Update id=262222467 is handled. Duration 21 ms by bot id=8216054898
2026-07-07 16:31:32,256 INFO DAEMON: Update id=262222468 is handled. Duration 421 ms by bot id=8216054898
2026-07-07 16:31:39,572 INFO DAEMON: Update id=262222469 is handled. Duration 95 ms by bot id=8216054898
2026-07-07 16:32:51,787 INFO DAEMON: Update id=262222470 is handled. Duration 99 ms by bot id=8216054898
2026-07-07 17:01:10,278 INFO DAEMON: STT env check groq=True
2026-07-07 17:01:10,278 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_12296.ogg size=33543 model=whisper-large-v3-turbo
2026-07-07 17:01:10,605 INFO DAEMON: STT http_status=200
2026-07-07 17:01:10,605 INFO DAEMON: STT ok transcript_len=99
2026-07-07 17:01:10,703 INFO DAEMON: Task b5fa5fbc-a33a-4943-82a8-a9aba939e728 created state=NEW topic_id=2
2026-07-07 17:01:10,704 INFO DAEMON: Update id=262222471 is handled. Duration 721 ms by bot id=8216054898
2026-07-07 17:01:27,522 INFO DAEMON: STT env check groq=True
2026-07-07 17:01:27,523 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_12300.ogg size=12383 model=whisper-large-v3-turbo
2026-07-07 17:01:27,868 INFO DAEMON: STT http_status=200
2026-07-07 17:01:27,869 INFO DAEMON: STT ok transcript_len=37
2026-07-07 17:01:27,943 INFO DAEMON: Task 229c5e93-a610-4b0f-8ad0-b5c2b14b407c created state=NEW topic_id=2
2026-07-07 17:01:27,943 INFO DAEMON: Update id=262222472 is handled. Duration 611 ms by bot id=8216054898
2026-07-07 17:01:38,638 INFO DAEMON: STT env check groq=True
2026-07-07 17:01:38,638 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_12303.ogg size=9164 model=whisper-large-v3-turbo
2026-07-07 17:01:38,945 INFO DAEMON: STT http_status=200
2026-07-07 17:01:38,946 INFO DAEMON: STT ok transcript_len=18
2026-07-07 17:01:39,022 INFO DAEMON: Task 83f43cd4-4d12-4192-978b-462f7ad556a5 created state=NEW topic_id=2
2026-07-07 17:01:39,022 INFO DAEMON: Update id=262222473 is handled. Duration 1571 ms by bot id=8216054898
2026-07-07 17:01:49,245 INFO DAEMON: Update id=262222474 is handled. Duration 94 ms by bot id=8216054898
2026-07-07 17:01:56,768 INFO DAEMON: Update id=262222475 is handled. Duration 72 ms by bot id=8216054898
2026-07-07 17:02:02,662 INFO DAEMON: Update id=262222476 is handled. Duration 80 ms by bot id=8216054898
2026-07-07 17:02:08,910 INFO DAEMON: Update id=262222477 is handled. Duration 70 ms by bot id=8216054898
