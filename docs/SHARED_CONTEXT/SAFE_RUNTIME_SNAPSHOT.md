# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-07-06T08:22:42.141373+00:00
git_sha_before_commit: 5ca02cdd69238e358402491f647ce5c384e8c39a
git_branch: main

## SERVICES
- areal-task-worker: activating
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
5ca02cd FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
20c42a8 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6bce30b FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
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

## GIT_SHOW_STAT_HEAD
commit 5ca02cdd69238e358402491f647ce5c384e8c39a
Author: root <root@graceful-olive.ptr.network>
Date:   Mon Jul 6 10:52:56 2026 +0300

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
 .../ORCHESTRA_FULL_CONTEXT_MANIFEST.json           |  24 +-
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
 .../ORCHESTRA_FULL_CONTEXT_PART_011.md             | 449 +++++++--------------
 .../ORCHESTRA_FULL_CONTEXT_PART_012.md             | 292 +++++++++++++-
 .../ORCHESTRA_FULL_CONTEXT_PART_013.md             | 108 ++++-
 .../ORCHESTRA_FULL_CONTEXT_PART_014.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_015.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_016.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_017.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_018.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_019.md             |   4 +-
 docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md       | 167 ++++----
 .../SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md |  18 +-
 docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md   | 110 ++---
 docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md         |   6 +-
 docs/SHARED_CONTEXT/TOPICS/topic_0_COMMON.md       |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_11_VIDEO.md       |   4 +-
 .../TOPICS/topic_210_PROEKTIROVANIE.md             |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_2_STROYKA.md      |  62 +--
 .../TOPICS/topic_3008_KODY_MOZGOV.md               |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_4569_CRM_LEADS.md |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_500_VEB_POISK.md  |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_5_TEKHNADZOR.md   |   4 +-
 .../SHARED_CONTEXT/TOPICS/topic_6104_JOB_SEARCH.md |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_794_DEVOPS.md     |   4 +-
 .../TOPICS/topic_961_AVTOZAPCHASTI.md              |   4 +-
 docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md          |   6 +-
 70 files changed, 851 insertions(+), 635 deletions(-)

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
- FAILED|3003
- CANCELLED|865
- DONE|658
- ARCHIVED|381
- AWAITING_CONFIRMATION|1

## CORE_DB_OPEN_TASKS
- 1

## LATEST_TASKS_15
- ca9ca9eb-cb9f-48b0-9819-1b6015bca4a2|2|text|FAILED|готово|Принял правки. Напиши одну конкретную правку к смете: что изменить?|2026-07-06 08:22:11
- a16879c1-5874-4fad-b960-e83e3543f013|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-06 07:38:26
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|2|drive_file|AWAITING_CONFIRMATION|{"file_id": "1qaHdtSP33P8VGsNYYLEJ6EPrfhQ7tAh2", "file_name": "photo_-1003725299009_11648.jpg", "mime_type": "image/jpeg|✅ Смета готова

Объект: фундамент Материал: монолит Площадь: 195.94 м² Этажность: 1 этаж Регион: СПб и ЛО
Шаблон: фундамент_Склад2.xlsx Лист: смета Цены: maximu|2026-07-06 08:13:22
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

## LATEST_FAILED_10
- ca9ca9eb-cb9f-48b0-9819-1b6015bca4a2|2|готово|STALE_TIMEOUT|2026-07-06 08:22:11
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

## LATEST_TASK_HISTORY_20
- ca9ca9eb-cb9f-48b0-9819-1b6015bca4a2|reply_sent:stale_failed|2026-07-06 08:22:11
- ca9ca9eb-cb9f-48b0-9819-1b6015bca4a2|state:FAILED|2026-07-06 08:22:11
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_TELEGRAM_DELIVERED:11789|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_DRIVE_UPLOAD_PDF_OK|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_DRIVE_UPLOAD_XLSX_OK|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_DRIVE_LINKS_SAVED:xlsx=https://drive.google.com/file/d/1QIf2WL6p4rFGsfnCC1rkr8KXemk80cmy/view:pdf=https://drive.google.com/file/d/1bHYHguC8uRh__ydc1Gpxc_0OePdFDM4q/view|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_DRIVE_TOPIC_FOLDER_OK|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_PDF_CYRILLIC_OK|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_PDF_CREATED:1|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_PDF_TOTALS_MATCH_XLSX:xlsx=2588836.88:pdf=2588836.88|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_XLSX_CANON_COLUMNS_OK:15|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_XLSX_FORMULAS_OK|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_XLSX_ROWS_WRITTEN:11|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_XLSX_TEMPLATE_ROWS_BLOCKED_FOR_FOUNDATION_ONLY|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_TEMPLATE_SHEET_SELECTED:смета|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_TEMPLATE_CACHE_USED|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_TEMPLATE_FILE_ID:1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_TEMPLATE_SELECTED:фундамент_Склад2.xlsx|2026-07-06 08:13:22
- ef67a6f0-c6e2-436e-904b-58d2c48ca3a0|TOPIC2_DIRECT_CLEAN_FOUNDATION_FINAL_V1|2026-07-06 08:13:22
- ca9ca9eb-cb9f-48b0-9819-1b6015bca4a2|TOPIC2_REVISION_BOUND_TO_PARENT:11784|2026-07-06 08:12:09

## MEMORY_DB_COUNT
- 5298

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-07-06T08:22:41.905469+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-07-06T08:22:41.905950+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-07-06T08:22:41.881194+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-07-06T08:22:41.881878+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-07-06T08:22:41.826209+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-07-06T08:22:41.826681+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-07-06T08:22:41.813527+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-07-06T08:22:41.813967+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-07-06T08:22:41.779987+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-07-06T08:22:41.780557+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-06T08:22:41.697919+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-07-06T08:22:41.697787+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-06T08:22:41.697705+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-06T08:22:41.697618+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-06T08:22:41.697554+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-07-06T08:22:41.697471+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T08:22:41.697343+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T08:22:41.697112+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T08:22:41.696866+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T08:22:41.696765+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T08:22:41.696436+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-07-06T08:22:41.696142+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T08:22:41.695966+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-06T08:22:41.695693+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-07-06T08:22:41.695432+00:00

## JOURNAL_AREAL_TASK_WORKER_60
areal-task-worker.service: Scheduled restart job, restart counter is at 4432.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4433.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4434.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4435.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4436.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4437.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4438.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4439.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4440.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4441.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4442.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4443.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4444.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4445.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 4446.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.

## JOURNAL_TELEGRAM_INGRESS_30
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
2026-07-06 10:15:03,507 INFO DAEMON: Update id=262222341 is handled. Duration 72 ms by bot id=8216054898
2026-07-06 10:20:59,280 INFO DAEMON: Update id=262222342 is handled. Duration 81 ms by bot id=8216054898
2026-07-06 10:38:26,066 INFO DAEMON: Task a16879c1-5874-4fad-b960-e83e3543f013 created state=NEW topic_id=2
2026-07-06 10:38:26,066 INFO DAEMON: Update id=262222343 is handled. Duration 10 ms by bot id=8216054898
2026-07-06 10:46:56,731 INFO DAEMON: Update id=262222344 is handled. Duration 15 ms by bot id=8216054898
2026-07-06 10:53:33,918 INFO DAEMON: Update id=262222345 is handled. Duration 11 ms by bot id=8216054898
2026-07-06 10:53:42,444 INFO DAEMON: Update id=262222346 is handled. Duration 15 ms by bot id=8216054898
2026-07-06 11:12:08,209 INFO DAEMON: Task ca9ca9eb-cb9f-48b0-9819-1b6015bca4a2 created state=NEW topic_id=2
2026-07-06 11:12:08,209 INFO DAEMON: Update id=262222347 is handled. Duration 20 ms by bot id=8216054898
