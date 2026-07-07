# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-07-07T13:23:40.741663+00:00
git_sha_before_commit: e80be12ae74ba853314f744e5002044348ea5ef1
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
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
ac196d47 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
62d44279 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
69647c2a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
4af2f182 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
0bb8f368 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
267e990f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
a261d92f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
80080415 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
603422f6 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
d0ba4837 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6c3243dd FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
3d0263cc FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

## GIT_SHOW_STAT_HEAD
commit e80be12ae74ba853314f744e5002044348ea5ef1
Author: Ila <ilakuznecov@mac.local>
Date:   Tue Jul 7 00:32:20 2026 +0300

    Record file memory duplicate guard live repair

 ..._FILE_MEMORY_LIVE_DIALOGUE_DUPLICATE_GUARD.json |   56 +
 core/active_dialog_state.py                        |   40 +-
 core/file_context_intake.py                        |   45 +-
 core/file_memory_bridge.py                         |   41 +-
 core/reply_repeat_parent.py                        |   42 +-
 docs/HANDOFFS/LATEST_HANDOFF.md                    |   48 +
 task_worker.py                                     | 1289 +++++++++++++++++++-
 7 files changed, 1505 insertions(+), 56 deletions(-)

## GIT_CHANGED_FILES_10
chat_exports/CHAT_EXPORT__2026-07-07_FILE_MEMORY_LIVE_DIALOGUE_DUPLICATE_GUARD.json
core/active_dialog_state.py
core/file_context_intake.py
core/file_memory_bridge.py
core/ocr_engine.py
core/output_sanitizer.py
core/reply_repeat_parent.py
core/reply_sender.py
core/sample_template_engine.py
core/search_session.py
core/stroyka_estimate_canon.py
docs/CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md
docs/CANON_FINAL/TOPIC_500_UNIVERSAL_SEARCH_CANON.md
docs/HANDOFFS/LATEST_HANDOFF.md
docs/HANDOFFS/SESSION_20260706_TOPIC2_TWO_DAY_SAVE.md
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

## CORE_DB_STATE_COUNTS
- FAILED|3048
- CANCELLED|869
- DONE|740
- ARCHIVED|381
- AWAITING_CONFIRMATION|1

## CORE_DB_OPEN_TASKS
- 1

## LATEST_TASKS_15
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
- 7ea4f0bf-6392-44df-8747-f65f1e9bbcbe|5|text|DONE|[VOICE] Это другая задача.|Комментарий привязан к последнему файлу.|2026-07-07 11:13:12
- 6dd48f26-77c1-443e-a0ee-6d6ea074445e|5|text|DONE|[VOICE] Скажи мне, есть ли на данном фото какие-нибудь нарушения? Что значит задача не выполняется? Есть ли на данных фо|Пояснение принято к фото: photo_-1003725299009_12203.jpg. В пакете технадзора: 24 шт. Акт не формирую без отдельной команды|2026-07-07 11:12:43
- 7300d5f5-94eb-488d-95e1-2f0b516740de|5|drive_file|FAILED|{"file_id": "1E1iHSjskAwDbfr3xk8EUsD3KP2FBab-i", "file_name": "photo_-1003725299009_12206.jpg", "mime_type": "image/jpeg|Файл получил и сохранил в буфер технадзора
Файл: photo_-1003725299009_12206.jpg
Текущий объект: Ропшинское шоссе 198
Текущая папка: тест надзор
Материалов в буф|2026-07-07 12:46:28
- 2d607bf6-c874-4a5b-9cfd-f7d89b44f866|5|drive_file|FAILED|{"file_id": "1eqCReGl0w3ra1m5_Qn0oX9CcYxvWor0v", "file_name": "photo_-1003725299009_12208.jpg", "mime_type": "image/jpeg|Файл получил и сохранил в буфер технадзора
Файл: photo_-1003725299009_12208.jpg
Текущий объект: Ропшинское шоссе 198
Текущая папка: тест надзор
Материалов в буф|2026-07-07 12:46:28
- 68dceab3-4cd1-43cd-92f4-2bed426d2b88|5|drive_file|FAILED|{"file_id": "1ebYctoc4X_3venU6COcDVSTDJ_uYnNAA", "file_name": "photo_-1003725299009_12204.jpg", "mime_type": "image/jpeg|Файл получил и сохранил в буфер технадзора
Файл: photo_-1003725299009_12204.jpg
Текущий объект: Ропшинское шоссе 198
Текущая папка: тест надзор
Материалов в буф|2026-07-07 12:46:26
- e9400bf5-ad48-44d3-ba57-ed6cdc261fe7|5|drive_file|FAILED|{"file_id": "1j9LcyzClfYSrsqQXWAqITi8WDHHuiwJw", "file_name": "photo_-1003725299009_12205.jpg", "mime_type": "image/jpeg|Файл получил и сохранил в буфер технадзора
Файл: photo_-1003725299009_12205.jpg
Текущий объект: Ропшинское шоссе 198
Текущая папка: тест надзор
Материалов в буф|2026-07-07 12:46:26
- 3b365ab1-9d1d-40c7-92da-ce0c9db43157|5|drive_file|FAILED|{"file_id": "1FruamdHLMgllCW3qWggLb3eOcxx_dDFw", "file_name": "photo_-1003725299009_12203.jpg", "mime_type": "image/jpeg|Файл получил и сохранил в буфер технадзора
Файл: photo_-1003725299009_12203.jpg
Текущий объект: Ропшинское шоссе 198
Текущая папка: тест надзор
Материалов в буф|2026-07-07 12:46:24
- f8405584-64a9-4926-8863-b1bfc4a9d113|5|drive_file|FAILED|{"file_id": "1j9_efbI0fO1ex5vTjNrBtrfQ6HtN7Go0", "file_name": "photo_-1003725299009_12207.jpg", "mime_type": "image/jpeg|Файл получил и сохранил в буфер технадзора
Файл: photo_-1003725299009_12207.jpg
Текущий объект: Ропшинское шоссе 198
Текущая папка: тест надзор
Материалов в буф|2026-07-07 12:46:24
- 88d30a38-716a-4960-9621-a94d978608df|5|text|DONE|[VOICE] Отмена задачи.|Пояснение принято к фото: photo_-1003725299009_10122.jpg. В пакете технадзора: 23 шт. Акт не формирую без отдельной команды|2026-07-07 11:10:55

## LATEST_FAILED_10
- 7300d5f5-94eb-488d-95e1-2f0b516740de|5|{"file_id": "1E1iHSjskAwDbfr3xk8EUsD3KP2FBab-i", "file_name": "photo_-1003725299009_12206.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:28
- 2d607bf6-c874-4a5b-9cfd-f7d89b44f866|5|{"file_id": "1eqCReGl0w3ra1m5_Qn0oX9CcYxvWor0v", "file_name": "photo_-1003725299009_12208.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:28
- 68dceab3-4cd1-43cd-92f4-2bed426d2b88|5|{"file_id": "1ebYctoc4X_3venU6COcDVSTDJ_uYnNAA", "file_name": "photo_-1003725299009_12204.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:26
- e9400bf5-ad48-44d3-ba57-ed6cdc261fe7|5|{"file_id": "1j9LcyzClfYSrsqQXWAqITi8WDHHuiwJw", "file_name": "photo_-1003725299009_12205.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:26
- 3b365ab1-9d1d-40c7-92da-ce0c9db43157|5|{"file_id": "1FruamdHLMgllCW3qWggLb3eOcxx_dDFw", "file_name": "photo_-1003725299009_12203.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:24
- f8405584-64a9-4926-8863-b1bfc4a9d113|5|{"file_id": "1j9_efbI0fO1ex5vTjNrBtrfQ6HtN7Go0", "file_name": "photo_-1003725299009_12207.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-07-07 12:46:24
- 936241de-0369-4288-8c37-5b7b53b4af12|500|Нужно найти в регионе Санкт-Петербург в открытых источниках информацию про компаниям, либо частным литом, которые занима|SEARCH_OUTPUT_INVALID_FALSE_VERIFIED|2026-07-07 08:51:38
- c3d3b1db-5985-4984-9959-038fdd761033|500|[VOICE] Вот еще найди мне телефон по данному запросу|CONFIRMATION_TIMEOUT|2026-07-07 09:09:45
- dd14c782-dd44-49d5-b921-04cf278020c8|500|[VOICE] мне надо найти услугу резки алмазных проемов смотри на всем интернет пространстве я же тебе скинул|CONFIRMATION_TIMEOUT|2026-07-07 09:09:40
- 631e3a5b-caa0-437a-afaf-bfd86aa0b46d|500|[VOICE] Самое главное номера телефонов, чтобы были.|CONFIRMATION_TIMEOUT|2026-07-07 09:05:09

## LATEST_TASK_HISTORY_20
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|TOPIC2_DONE_CONTRACT_OK|2026-07-07 13:20:36
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:RESTORED|2026-07-07 13:20:36
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|TOPIC2_DONE_CONTRACT_OK|2026-07-07 13:20:34
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:RESTORED|2026-07-07 13:20:34
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|TOPIC2_DONE_CONTRACT_OK|2026-07-07 13:20:33
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:RESTORED|2026-07-07 13:20:33
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|TOPIC2_DONE_CONTRACT_OK|2026-07-07 13:20:31
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:RESTORED|2026-07-07 13:20:31
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|TOPIC2_DONE_CONTRACT_OK|2026-07-07 13:20:29
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:RESTORED|2026-07-07 13:20:29
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|TOPIC2_DONE_CONTRACT_OK|2026-07-07 13:20:28
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:RESTORED|2026-07-07 13:20:28
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|TOPIC2_DONE_CONTRACT_OK|2026-07-07 13:20:26
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:RESTORED|2026-07-07 13:20:26
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|TOPIC2_DONE_CONTRACT_OK|2026-07-07 13:20:25
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:RESTORED|2026-07-07 13:20:25
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|TOPIC2_DONE_CONTRACT_OK|2026-07-07 13:20:23
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:RESTORED|2026-07-07 13:20:23
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|TOPIC2_DONE_CONTRACT_OK|2026-07-07 13:20:21
- 287a613c-c47d-4fae-9a71-d57fa3f2b762|PATCH_TOPIC2_READY_ARTIFACT_STATE_RECOVERY_V1:RESTORED|2026-07-07 13:20:21

## MEMORY_DB_COUNT
- 5353

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 33, "updated_at": "2026-07-07T13:23:40.519653+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-07-07T13:23:40.520514+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-07-07T13:23:40.496809+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-07-07T13:23:40.497513+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-07-07T13:23:40.437085+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-07-07T13:23:40.437771+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-07-07T13:23:40.426390+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-07-07T13:23:40.426970+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-07-07T13:23:40.383837+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-07-07T13:23:40.384643+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-07T13:23:40.263849+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-07-07T13:23:40.263743+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-07T13:23:40.263659+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-07T13:23:40.263539+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-07T13:23:40.263422+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-07-07T13:23:40.263317+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T13:23:40.263158+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T13:23:40.262915+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T13:23:40.262687+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T13:23:40.262514+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T13:23:40.261901+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-07-07T13:23:40.261349+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T13:23:40.261178+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-07T13:23:40.260802+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-07-07T13:23:40.260481+00:00

## JOURNAL_AREAL_TASK_WORKER_60
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
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

## JOURNAL_TELEGRAM_INGRESS_30
2026-07-07 15:39:38,385 INFO DAEMON: STT env check groq=True
2026-07-07 15:39:38,385 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_12264.ogg size=42169 model=whisper-large-v3-turbo
2026-07-07 15:39:38,748 INFO DAEMON: STT http_status=200
2026-07-07 15:39:38,749 INFO DAEMON: STT ok transcript_len=116
2026-07-07 15:39:38,835 INFO DAEMON: Task 3fb639a0-d76b-44f4-9331-0c72433a9da0 created state=NEW topic_id=2
2026-07-07 15:39:38,835 INFO DAEMON: Update id=262222462 is handled. Duration 678 ms by bot id=8216054898
2026-07-07 15:40:08,604 INFO DAEMON: STT env check groq=True
2026-07-07 15:40:08,604 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_12267.ogg size=48213 model=whisper-large-v3-turbo
2026-07-07 15:40:08,955 INFO DAEMON: STT http_status=200
2026-07-07 15:40:08,956 INFO DAEMON: STT ok transcript_len=115
2026-07-07 15:40:09,060 INFO DAEMON: Task ae452bae-6957-476e-a76f-45980262b938 created state=NEW topic_id=5
2026-07-07 15:40:09,060 INFO DAEMON: Update id=262222463 is handled. Duration 745 ms by bot id=8216054898
2026-07-07 15:40:45,968 INFO DAEMON: STT env check groq=True
2026-07-07 15:40:45,969 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_12270.ogg size=22190 model=whisper-large-v3-turbo
2026-07-07 15:40:46,301 INFO DAEMON: STT http_status=200
2026-07-07 15:40:46,302 INFO DAEMON: STT ok transcript_len=26
2026-07-07 15:40:46,377 INFO DAEMON: Task 1d2505b9-1e69-4e54-ba28-ee0558c3ce43 created state=NEW topic_id=5
2026-07-07 15:40:46,377 INFO DAEMON: Update id=262222464 is handled. Duration 625 ms by bot id=8216054898
2026-07-07 15:41:07,630 INFO DAEMON: STT env check groq=True
2026-07-07 15:41:07,631 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_12273.ogg size=22619 model=whisper-large-v3-turbo
2026-07-07 15:41:07,968 INFO DAEMON: STT http_status=200
2026-07-07 15:41:07,969 INFO DAEMON: STT ok transcript_len=63
2026-07-07 15:41:08,067 INFO DAEMON: Task f18ec8db-bc14-4098-a868-dbb3d68b9d90 created state=NEW topic_id=2
2026-07-07 15:41:08,067 INFO DAEMON: Update id=262222465 is handled. Duration 621 ms by bot id=8216054898
2026-07-07 15:42:02,495 INFO DAEMON: STT env check groq=True
2026-07-07 15:42:02,496 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_12277.ogg size=33254 model=whisper-large-v3-turbo
2026-07-07 15:42:02,740 INFO DAEMON: STT http_status=200
2026-07-07 15:42:02,741 INFO DAEMON: STT ok transcript_len=67
2026-07-07 15:42:02,877 INFO DAEMON: Task be35fd19-316c-40d5-9c81-4d648c2083a2 created state=NEW topic_id=5
2026-07-07 15:42:02,878 INFO DAEMON: Update id=262222466 is handled. Duration 605 ms by bot id=8216054898
