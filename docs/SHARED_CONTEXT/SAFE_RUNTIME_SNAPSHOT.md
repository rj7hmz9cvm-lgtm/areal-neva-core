# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-07-06T07:15:02.464951+00:00
git_sha_before_commit: 486f4570381d12c24aff0bb0ac42f8fd338184b9
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
486f457 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
835217e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
2f5dff4 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
fc44f3c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
a939ed1 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
a9784f6 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
931896b FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
ac196d4 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
62d4427 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
69647c2 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
4af2f18 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
0bb8f36 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
267e990 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
a261d92 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
8008041 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
603422f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
d0ba483 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6c3243d FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
3d0263c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7c89f73 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
446f85e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
d8a698f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
dec4e95 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c6faf53 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
3a63f77 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
247bf55 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
4f48f3a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
4a963f6 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
57ea8d1 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
4850e44 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

## GIT_SHOW_STAT_HEAD
commit 486f4570381d12c24aff0bb0ac42f8fd338184b9
Author: Ila <ilakuznecov@mac.local>
Date:   Mon Jul 6 09:55:06 2026 +0300

    FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

 docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md    |  6 +--
 docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md |  2 +-
 .../SHARED_CONTEXT/DIRECTIONS/auto_parts_search.md |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/cad_dwg.md          |  4 +-
 .../DIRECTIONS/construction_search.md              |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/crm_leads.md        |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/defect_acts.md      |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/devops_server.md    |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/documents.md        |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/email_ingress.md    |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/estimates.md        |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/general_chat.md     |  4 +-
 .../DIRECTIONS/google_drive_storage.md             |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/internet_search.md  |  4 +-
 .../DIRECTIONS/isolated_project_ivan.md            |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/job_search.md       |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/memory_archive.md   |  4 +-
 .../SHARED_CONTEXT/DIRECTIONS/monolith_concrete.md |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/ocr_photo.md        |  4 +-
 .../DIRECTIONS/orchestration_core.md               |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/photo_cleanup.md    |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/product_search.md   |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/roofing.md          |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/social_content.md   |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/spreadsheets.md     |  4 +-
 .../SHARED_CONTEXT/DIRECTIONS/structural_design.md |  4 +-
 .../DIRECTIONS/technical_supervision.md            |  4 +-
 .../DIRECTIONS/telegram_automation.md              |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/video_production.md |  4 +-
 docs/SHARED_CONTEXT/DIRECTIONS/vpn_network.md      |  4 +-
 docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md      |  4 +-
 docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md     |  6 +--
 docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md          |  6 +--
 docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md      |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_MANIFEST.json           |  6 +--
 .../ORCHESTRA_FULL_CONTEXT_PART_001.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_002.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_003.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_004.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_005.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_006.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_007.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_008.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_009.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_010.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_011.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_012.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_013.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_014.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_015.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_016.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_017.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_018.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_019.md             |  4 +-
 docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md       | 18 ++++----
 .../SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md |  4 +-
 docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md   | 48 +++++++++++-----------
 docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md         |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_0_COMMON.md       |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_11_VIDEO.md       |  4 +-
 .../TOPICS/topic_210_PROEKTIROVANIE.md             |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_2_STROYKA.md      |  4 +-
 .../TOPICS/topic_3008_KODY_MOZGOV.md               |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_4569_CRM_LEADS.md |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_500_VEB_POISK.md  |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_5_TEKHNADZOR.md   |  4 +-
 .../SHARED_CONTEXT/TOPICS/topic_6104_JOB_SEARCH.md |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_794_DEVOPS.md     |  4 +-
 .../TOPICS/topic_961_AVTOZAPCHASTI.md              |  4 +-
 docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md          |  4 +-
 70 files changed, 172 insertions(+), 172 deletions(-)

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
- FAILED|3002
- CANCELLED|865
- DONE|657
- ARCHIVED|381
- IN_PROGRESS|1

## CORE_DB_OPEN_TASKS
- 1

## LATEST_TASKS_15
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|2|drive_file|IN_PROGRESS|{"file_id": "1qaHdtSP33P8VGsNYYLEJ6EPrfhQ7tAh2", "file_name": "photo_-1003725299009_11648.jpg", "mime_type": "image/jpeg|Не вижу размеры объекта на фото/в ТЗ. Пришли размер в формате 7.8х9.0 или фото крупнее|2026-07-06 07:14:59
- e3eeed87-4d5c-4dd9-928a-47c9fb101c88|2|text|DONE|Ничего|Понял, ничего не меняю. Если понадоблюсь — напишите.|2026-07-06 05:34:47
- 39af79c1-80eb-4735-8f4f-61548cf13b2e|2|text|DONE|Задача завершена|Подтверждение принято|2026-07-05T22:20:02.789573
- 24e594b9-1ea3-4b82-86ab-e9355021289b|2|text|DONE|Да всё верно|Подтверждение принято|2026-07-05T22:20:02.789573
- dfccdbfe-92e3-4fbb-9e16-5450a3fa6479|2|text|CANCELLED|[VOICE] Все есть в проекте.|None|2026-07-05 20:35:27
- bd0d5ae1-830d-4250-a8d3-4e730864ad60|2|text|FAILED|[VOICE] Работай с той информацией, которая у тебя есть. Мне нужна смета, максимально подробная, но точная.|Уточни этажность|2026-07-05 20:45:23
- 893e166f-7236-4895-9ffa-44e932eb05f2|2|text|CANCELLED|Хорошая работа задача завершена|None|2026-07-05 19:55:48
- a8462a10-ad97-45cc-940b-7137e2ada126|2|text|DONE|Да всё хорошо|Понял, ничего не меняю. Если понадоблюсь — напишите.|2026-07-05 19:55:36
- 39434a00-9c27-42b1-a213-8c09232d75c2|2|text|DONE|Максимально|Подтверждение принято|2026-07-05 19:18:02
- 3621be64-7dd1-49f8-bc96-acd857e88065|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 19:03:59
- b5e9fee5-cada-4fee-8247-0d42bf41bea9|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 18:28:18
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|2|drive_file|DONE|{"file_id": "1aHUalehkGfMtItAJpUeKInLuSUc7V43y", "file_name": "АР_Проект 21Т(1).pdf", "mime_type": "application/pdf", "c|✅ Смета готова

Объект: дом   Материал: газобетон   Площадь: 197.81 м²   Этажность: 2 этажа   Регион: СПб и ЛО
Шаблон: Ареал Нева.xlsx   Лист: смета   Цены: сре|2026-07-05T22:20:02.789573
- 103a8493-2347-4f60-9dee-81ee5892ef46|2|text|DONE|да ок|Подтверждение принято|2026-07-05 17:58:57
- 84392d62-b460-42f0-8329-15d7064af668|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 17:30:49
- 9225f446-cbce-4376-ba14-4cff3ab8828a|2|text|DONE|2|Выбор цен привязан к основной задаче: median|2026-07-05 17:24:15

## LATEST_FAILED_10
- bd0d5ae1-830d-4250-a8d3-4e730864ad60|2|[VOICE] Работай с той информацией, которая у тебя есть. Мне нужна смета, максимально подробная, но точная.|STALE_TIMEOUT|2026-07-05 20:45:23
- 9c5946d7-f37f-488f-bf2c-b2045310238a|2|{"file_id": "1f_VpraIIeLAgELtAj94IEzbwDQ5h08Qs", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio|STALE_TIMEOUT|2026-07-05 17:14:13
- ea794751-2522-488e-be9c-f76f10a48d93|2|{"file_id": "1FC_ZKLpC_yQ0kM7WJciJcMFIZW8PZHQm", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio|NO_VALID_ARTIFACT|2026-07-05 11:50:22
- 16b3b2e6-c3b0-4c27-95ac-854d5b3c9fdd|2|вот проект|STALE_TIMEOUT|2026-07-05 08:04:03
- dfdc5ca5-7bb3-48c8-8d66-1b79d279312e|2|пусто

УТОЧНЕНИЕ К ИСХОДНОМУ ТЗ:
посчитать работы и материалы согласно проекта|STALE_TIMEOUT|2026-07-05 08:03:07
- 29331db4-0403-4a5b-8516-88e535202da6|2|{"file_id": "1jjke-Boab3b8A2DhKiyQT5eIRXWOrYf6", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio|STALE_TIMEOUT|2026-07-05 07:24:54
- 5a453d88-7bee-4b61-a510-303fda0b51ef|2|[VOICE] Дом 10х10, два этажа.|STALE_TIMEOUT|2026-07-04 20:06:42
- c82ce66e-0e82-4d62-861b-73413d8a15e2|2|[VOICE] Привет, Орик! Как дела? Отзовись! Все ли у тебя в порядке? Расскажи, как ты себя чувствуешь? Готов ли ты работат|STALE_TIMEOUT|2026-07-04 15:40:25
- 71aa047d-8bce-41cd-9a6e-d5620b28c1ef|0|TEST_AFTER_RESTORE_20260704|INVALID_RESULT_GATE|2026-07-04 14:50:39
- 0b1a2b5f-a924-4c6a-b123-d24d6bdac167|2|{"source": "manual_runtime_requeue", "request": "полный канонический вывод сметы XLSX и PDF без duplicate guard", "reque|NO_VALID_ARTIFACT|2026-07-04 18:31:28

## LATEST_TASK_HISTORY_20
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|state:AWAITING_CONFIRMATION:file_intake_router|2026-07-06 07:14:59
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|P6E2_CANON_DIMS_NOT_RECOGNIZED|2026-07-06 07:14:59
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|state:AWAITING_CONFIRMATION:file_intake_router|2026-07-06 07:14:56
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|P6E2_CANON_DIMS_NOT_RECOGNIZED|2026-07-06 07:14:56
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|state:AWAITING_CONFIRMATION:file_intake_router|2026-07-06 07:14:53
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|P6E2_CANON_DIMS_NOT_RECOGNIZED|2026-07-06 07:14:53
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|state:AWAITING_CONFIRMATION:file_intake_router|2026-07-06 07:14:50
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|P6E2_CANON_DIMS_NOT_RECOGNIZED|2026-07-06 07:14:50
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|state:AWAITING_CONFIRMATION:file_intake_router|2026-07-06 07:14:47
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|P6E2_CANON_DIMS_NOT_RECOGNIZED|2026-07-06 07:14:47
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|state:AWAITING_CONFIRMATION:file_intake_router|2026-07-06 07:14:44
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|P6E2_CANON_DIMS_NOT_RECOGNIZED|2026-07-06 07:14:44
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|state:AWAITING_CONFIRMATION:file_intake_router|2026-07-06 07:14:41
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|P6E2_CANON_DIMS_NOT_RECOGNIZED|2026-07-06 07:14:41
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|state:AWAITING_CONFIRMATION:file_intake_router|2026-07-06 07:14:38
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|P6E2_CANON_DIMS_NOT_RECOGNIZED|2026-07-06 07:14:38
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|state:AWAITING_CONFIRMATION:file_intake_router|2026-07-06 07:14:35
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|P6E2_CANON_DIMS_NOT_RECOGNIZED|2026-07-06 07:14:34
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|state:AWAITING_CONFIRMATION:file_intake_router|2026-07-06 07:14:32
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|P6E2_CANON_DIMS_NOT_RECOGNIZED|2026-07-06 07:14:32

## MEMORY_DB_COUNT
- 5297

## LATEST_MEMORY_20
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-07-06T07:15:00.048278+00:00", "files": [{"task_id": "", "file_id": "", "file_name": "", "mime_type": "|2026-07-06T07:15:00.049137+00:00
- topic_2_file_content_status_ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|{"ok": false, "reason": "UNSUPPORTED_TYPE", "file_name": "photo_-1003725299009_11648.jpg"}|2026-07-06T07:13:15.467249
- topic_2_file_ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|{"task_id": "ef67a6f0-c6e2-436e-904b-58d2c48ca3a0", "chat_id": "-1003725299009", "topic_id": 2, "file_id": "1qaHdtSP33P8VGsNYYLEJ6EPrfhQ7tAh2", "file_name": "photo_-1003725299009_1|2026-07-06T07:13:15.461116
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-07-06T06:52:39.955677+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-07-06T06:52:39.956502+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-07-06T06:52:39.936081+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-07-06T06:52:39.936637+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-07-06T06:52:39.888581+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-07-06T06:52:39.888955+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-07-06T06:52:39.880335+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-07-06T06:52:39.880860+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-06T06:52:39.782936+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-07-06T06:52:39.782842+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-06T06:52:39.782749+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-06T06:52:39.782564+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-06T06:52:39.782448+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-07-06T06:52:39.782330+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T06:52:39.782172+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T06:52:39.781794+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T06:52:39.781370+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T06:52:39.781247+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T06:52:39.780802+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-07-06T06:52:39.780454+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T06:52:39.780293+00:00

## JOURNAL_AREAL_TASK_WORKER_60
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
PATCH_TOPIC2_PICKER_BYPASS_AND_RESULT_GATE_V1 AC blocked task=ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 reason=too_short_or_empty
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),

## JOURNAL_TELEGRAM_INGRESS_30
2026-07-05 23:35:27,329 INFO DAEMON: Task dfccdbfe-92e3-4fbb-9e16-5450a3fa6479 created state=NEW topic_id=2
2026-07-05 23:35:27,329 INFO DAEMON: Update id=262222322 is handled. Duration 515 ms by bot id=8216054898
2026-07-05 23:39:31,236 INFO DAEMON: Update id=262222323 is handled. Duration 74 ms by bot id=8216054898
2026-07-05 23:42:26,712 INFO DAEMON: Update id=262222324 is handled. Duration 87 ms by bot id=8216054898
2026-07-06 00:11:29,369 INFO DAEMON: Update id=262222325 is handled. Duration 167 ms by bot id=8216054898
2026-07-06 00:21:41,957 INFO DAEMON: Update id=262222326 is handled. Duration 19 ms by bot id=8216054898
2026-07-06 00:35:40,565 INFO DAEMON: Update id=262222327 is handled. Duration 16 ms by bot id=8216054898
2026-07-06 00:50:29,549 INFO DAEMON: Update id=262222328 is handled. Duration 15 ms by bot id=8216054898
2026-07-06 01:05:27,731 INFO DAEMON: Update id=262222329 is handled. Duration 13 ms by bot id=8216054898
2026-07-06 01:06:14,423 INFO DAEMON: Update id=262222330 is handled. Duration 13 ms by bot id=8216054898
2026-07-06 01:15:06,392 INFO DAEMON: Update id=262222331 is handled. Duration 13 ms by bot id=8216054898
2026-07-06 01:17:15,191 INFO DAEMON: Task 24e594b9-1ea3-4b82-86ab-e9355021289b created state=NEW topic_id=2
2026-07-06 01:17:15,191 INFO DAEMON: Update id=262222332 is handled. Duration 15 ms by bot id=8216054898
2026-07-06 01:17:24,406 INFO DAEMON: Task 39af79c1-80eb-4735-8f4f-61548cf13b2e created state=NEW topic_id=2
2026-07-06 01:17:24,406 INFO DAEMON: Update id=262222333 is handled. Duration 13 ms by bot id=8216054898
2026-07-06 04:14:07,220 ERROR DAEMON: Failed to fetch updates - TelegramServerError: Telegram server says - Bad Gateway
2026-07-06 04:14:07,221 WARNING DAEMON: Sleep for 1.000000 seconds and try again... (tryings = 0, bot id = 8216054898)
2026-07-06 04:14:08,256 ERROR DAEMON: Failed to fetch updates - TelegramServerError: Telegram server says - Bad Gateway
2026-07-06 04:14:08,256 WARNING DAEMON: Sleep for 1.296766 seconds and try again... (tryings = 1, bot id = 8216054898)
2026-07-06 04:14:51,253 INFO DAEMON: Connection established (tryings = 2, bot id = 8216054898)
2026-07-06 08:34:31,254 INFO DAEMON: Task e3eeed87-4d5c-4dd9-928a-47c9fb101c88 created state=NEW topic_id=2
2026-07-06 08:34:31,254 INFO DAEMON: Update id=262222334 is handled. Duration 19 ms by bot id=8216054898
2026-07-06 08:34:47,412 INFO DAEMON: Update id=262222335 is handled. Duration 722 ms by bot id=8216054898
2026-07-06 10:13:11,636 INFO DAEMON: file_cache is only supported with oauth2client<4.0.0
2026-07-06 10:13:14,510 INFO DAEMON: Task ef67a6f0-c6e2-436e-904b-58d2c48ca3a0 created state=NEW topic_id=2
2026-07-06 10:13:14,613 INFO DAEMON: Update id=262222336 is handled. Duration 3566 ms by bot id=8216054898
2026-07-06 10:13:32,062 INFO DAEMON: Update id=262222337 is handled. Duration 83 ms by bot id=8216054898
2026-07-06 10:13:43,598 INFO DAEMON: Update id=262222338 is handled. Duration 88 ms by bot id=8216054898
2026-07-06 10:13:51,014 INFO DAEMON: Update id=262222339 is handled. Duration 80 ms by bot id=8216054898
2026-07-06 10:13:58,558 INFO DAEMON: Update id=262222340 is handled. Duration 100 ms by bot id=8216054898
