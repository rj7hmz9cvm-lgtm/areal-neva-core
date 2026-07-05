# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-07-05T19:22:21.227548+00:00
git_sha_before_commit: e76a956d9df6276eebb07cb11c33f1256298aa83
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
e76a956 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
89c6bd9 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
d7d987d FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
71e0807 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
844fafb topic2: close PDF estimate confirmation flow
2d6f053 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c5ea64e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
0e17a9b FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
8c11300 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
a9850e9 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
f3e8d1a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
d33ea9c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
1800250 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6807258 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
2270e1e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
81163a9 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
8df212f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
0e7f79f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
62c612f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
ce2832d FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7c14173 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7badda1 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7e53b59 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
cd360d6 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c9f0a8c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
b55ba86 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6b8f749 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
348fcef FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
bef6672 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
44361e7 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

## GIT_SHOW_STAT_HEAD
commit e76a956d9df6276eebb07cb11c33f1256298aa83
Author: root <root@graceful-olive.ptr.network>
Date:   Sun Jul 5 21:52:29 2026 +0300

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
 .../ORCHESTRA_FULL_CONTEXT_MANIFEST.json           |  18 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_001.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_002.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_003.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_004.md             |   4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_005.md             |   6 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_006.md             |   6 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_007.md             |   6 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_008.md             | 147 ++++++++++++++-
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
 docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md       | 208 ++++++++++-----------
 .../SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md |  10 +-
 docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md   | 103 +++++-----
 docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md         |   6 +-
 docs/SHARED_CONTEXT/TOPICS/topic_0_COMMON.md       |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_11_VIDEO.md       |   4 +-
 .../TOPICS/topic_210_PROEKTIROVANIE.md             |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_2_STROYKA.md      |  47 +++--
 .../TOPICS/topic_3008_KODY_MOZGOV.md               |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_4569_CRM_LEADS.md |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_500_VEB_POISK.md  |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_5_TEKHNADZOR.md   |   4 +-
 .../SHARED_CONTEXT/TOPICS/topic_6104_JOB_SEARCH.md |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_794_DEVOPS.md     |   4 +-
 .../TOPICS/topic_961_AVTOZAPCHASTI.md              |   4 +-
 docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md          |   6 +-
 69 files changed, 467 insertions(+), 332 deletions(-)

## GIT_CHANGED_FILES_10
core/file_intake_router.py
core/pdf_spec_extractor.py
core/sample_template_engine.py
core/stroyka_estimate_canon.py
core/topic2_estimate_final_close_v2.py
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
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_018.md
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
telegram_daemon.py

## CORE_DB_STATE_COUNTS
- FAILED|3001
- CANCELLED|863
- DONE|653
- ARCHIVED|381

## CORE_DB_OPEN_TASKS
- 0

## LATEST_TASKS_15
- 39434a00-9c27-42b1-a213-8c09232d75c2|2|text|DONE|Максимально|Подтверждение принято|2026-07-05 19:18:02
- 3621be64-7dd1-49f8-bc96-acd857e88065|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 19:03:59
- b5e9fee5-cada-4fee-8247-0d42bf41bea9|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 18:28:18
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|2|drive_file|DONE|{"file_id": "1aHUalehkGfMtItAJpUeKInLuSUc7V43y", "file_name": "АР_Проект 21Т(1).pdf", "mime_type": "application/pdf", "c|✅ Смета готова

Объект: дом   Материал: не указан   Площадь: 197.81 м²   Этажность: не указана   Регион: СПб и ЛО
Шаблон: Ареал Нева.xlsx   Лист: смета   Цены: |2026-07-05 19:18:02
- 103a8493-2347-4f60-9dee-81ee5892ef46|2|text|DONE|да ок|Подтверждение принято|2026-07-05 17:58:57
- 84392d62-b460-42f0-8329-15d7064af668|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 17:30:49
- 9225f446-cbce-4376-ba14-4cff3ab8828a|2|text|DONE|2|Выбор цен привязан к основной задаче: median|2026-07-05 17:24:15
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|2|drive_file|DONE|{"file_id": "1f_VpraIIeLAgELtAj94IEzbwDQ5h08Qs", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio|✅ Смета готова
Позиций: 12
Итого: 37 035 064 руб
Цены: не выдуманы, Excel содержит формулы и итог

Excel: https://drive.google.com/file/d/1zjtY9gL4YWHGDN-1sT9ly|2026-07-05 17:58:57
- c81e2756-db52-4277-b694-1631c3f75f14|2|text|DONE|2|Выбор цен привязан к основной задаче: median|2026-07-05 12:31:29
- 0f073abf-0aef-4d0e-ac2c-35676ebc999c|2|text|DONE|1|Выбор цен привязан к основной задаче: min|2026-07-05 12:31:07
- 9c5946d7-f37f-488f-bf2c-b2045310238a|2|drive_file|FAILED|{"file_id": "1f_VpraIIeLAgELtAj94IEzbwDQ5h08Qs", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio|PDF прочитан, но сметная ведомость объёмов/спецификация работ в нём не найдена. Смету на 0 руб не создаю. Для канонного расчёта пришли ВОР / спецификацию / разд|2026-07-05 17:14:13
- 9e15be11-1af3-422b-b680-b57b9d633df4|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 12:13:50
- af5de40c-8a9c-4278-a440-da3911c67e2c|2|text|DONE|1|Выбор цен привязан к основной задаче: min|2026-07-05 12:07:24
- 1217e297-c599-45f6-939f-8a800d352397|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 12:05:42
- b1276c2d-3c54-4246-9c36-523ab1600fe8|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 12:00:35

## LATEST_FAILED_10
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
- b57b1bae-32a3-404f-a49c-4d02160a63a5|2|Сформируй финальную смету XLSX и PDF по канону topic_2
Ценовой уровень: median
Материал: каркас
Шаблон: М-80 или М-110 п|STALE_TIMEOUT|2026-05-09 17:18:10

## LATEST_TASK_HISTORY_20
- 39434a00-9c27-42b1-a213-8c09232d75c2|TOPIC2_CONFIRM_CHILD_DONE|2026-07-05 19:18:02
- 39434a00-9c27-42b1-a213-8c09232d75c2|TOPIC2_DONE_BLOCKED_REASON:no_estimate_generated|2026-07-05 19:18:02
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|state:DONE|2026-07-05 19:18:02
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_DONE_CONTRACT_OK|2026-07-05 19:18:02
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_EXPLICIT_CONFIRM:from_user_confirm_reply|2026-07-05 19:18:02
- 39434a00-9c27-42b1-a213-8c09232d75c2|created:NEW|2026-07-05T19:18:00.186705+00:00
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|PATCH_TOPIC2_DRIVE_FINAL_USE_CANON_GENERATE_V2:DONE|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:estimate_generated|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_TELEGRAM_DELIVERED:11574|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_DRIVE_UPLOAD_PDF_OK|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_DRIVE_UPLOAD_XLSX_OK|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_PDF_CYRILLIC_OK|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_PDF_CREATED:1|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_XLSX_CANON_COLUMNS_OK:15|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_XLSX_FORMULAS_OK|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_XLSX_ROWS_WRITTEN:187|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_XLSX_TEMPLATE_COPY_OK|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_TEMPLATE_SHEET_SELECTED:смета|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_TEMPLATE_CACHE_USED|2026-07-05 19:17:47
- 7dab7ad1-3335-4385-b942-4c734dbdbebe|TOPIC2_TEMPLATE_FILE_ID:1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm|2026-07-05 19:17:47

## MEMORY_DB_COUNT
- 5295

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-07-05T19:22:20.999695+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-07-05T19:22:21.000336+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-07-05T19:22:20.978068+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-07-05T19:22:20.978926+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-07-05T19:22:20.929044+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-07-05T19:22:20.929448+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-07-05T19:22:20.919300+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-07-05T19:22:20.920349+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-07-05T19:22:20.886126+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-07-05T19:22:20.886961+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T19:22:20.811707+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-07-05T19:22:20.811631+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T19:22:20.811571+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T19:22:20.811492+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T19:22:20.811436+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-07-05T19:22:20.811372+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T19:22:20.811299+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T19:22:20.811150+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T19:22:20.810956+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T19:22:20.810852+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T19:22:20.810447+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-07-05T19:22:20.810151+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T19:22:20.810058+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T19:22:20.809679+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-07-05T19:22:20.809443+00:00

## JOURNAL_AREAL_TASK_WORKER_60
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 173.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 174.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 175.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 176.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 177.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 178.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 179.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 180.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 181.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 182.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 183.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 184.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 185.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 186.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 187.
Started areal-task-worker.service - Areal Task Worker.

## JOURNAL_TELEGRAM_INGRESS_30
2026-07-05 15:13:49,863 INFO DAEMON: Update id=262222295 is handled. Duration 9 ms by bot id=8216054898
2026-07-05 15:29:58,442 INFO DAEMON: Update id=262222296 is handled. Duration 83 ms by bot id=8216054898
2026-07-05 15:30:57,192 INFO DAEMON: file_cache is only supported with oauth2client<4.0.0
2026-07-05 15:30:59,648 INFO DAEMON: Task 9c5946d7-f37f-488f-bf2c-b2045310238a created state=NEW topic_id=2
2026-07-05 15:30:59,723 INFO DAEMON: Update id=262222297 is handled. Duration 3577 ms by bot id=8216054898
2026-07-05 15:31:06,699 INFO DAEMON: Task 0f073abf-0aef-4d0e-ac2c-35676ebc999c created state=NEW topic_id=2
2026-07-05 15:31:06,699 INFO DAEMON: Update id=262222298 is handled. Duration 8 ms by bot id=8216054898
2026-07-05 15:31:29,864 INFO DAEMON: Task c81e2756-db52-4277-b694-1631c3f75f14 created state=NEW topic_id=2
2026-07-05 15:31:29,864 INFO DAEMON: Update id=262222299 is handled. Duration 10 ms by bot id=8216054898
2026-07-05 15:31:36,844 INFO DAEMON: Update id=262222300 is handled. Duration 80 ms by bot id=8216054898
2026-07-05 20:24:14,083 INFO DAEMON: Task 9225f446-cbce-4376-ba14-4cff3ab8828a created state=NEW topic_id=2
2026-07-05 20:24:14,083 INFO DAEMON: Update id=262222301 is handled. Duration 13 ms by bot id=8216054898
2026-07-05 20:30:48,680 INFO DAEMON: Task 84392d62-b460-42f0-8329-15d7064af668 created state=NEW topic_id=2
2026-07-05 20:30:48,680 INFO DAEMON: Update id=262222302 is handled. Duration 8 ms by bot id=8216054898
2026-07-05 20:52:17,108 INFO DAEMON: Task 103a8493-2347-4f60-9dee-81ee5892ef46 created state=NEW topic_id=2
2026-07-05 20:52:17,108 INFO DAEMON: Update id=262222303 is handled. Duration 12 ms by bot id=8216054898
2026-07-05 21:16:26,111 INFO DAEMON: file_cache is only supported with oauth2client<4.0.0
2026-07-05 21:16:28,568 INFO DAEMON: Task 7dab7ad1-3335-4385-b942-4c734dbdbebe created state=NEW topic_id=2
2026-07-05 21:16:28,802 INFO DAEMON: Update id=262222304 is handled. Duration 3856 ms by bot id=8216054898
2026-07-05 21:17:14,025 INFO DAEMON: Update id=262222305 is handled. Duration 85 ms by bot id=8216054898
2026-07-05 21:28:17,419 INFO DAEMON: Task b5e9fee5-cada-4fee-8247-0d42bf41bea9 created state=NEW topic_id=2
2026-07-05 21:28:17,419 INFO DAEMON: Update id=262222306 is handled. Duration 9 ms by bot id=8216054898
Started telegram-ingress.service - AREAL telegram ingress.
2026-07-05 21:50:31,530 INFO DAEMON: BOT STARTED id=8216054898 username=ai_orkestra_all_bot
2026-07-05 21:50:31,530 INFO DAEMON: Start polling
2026-07-05 21:50:31,561 INFO DAEMON: Run polling for bot @ai_orkestra_all_bot id=8216054898 - 'Partner Zone'
2026-07-05 22:03:58,645 INFO DAEMON: Task 3621be64-7dd1-49f8-bc96-acd857e88065 created state=NEW topic_id=2
2026-07-05 22:03:58,646 INFO DAEMON: Update id=262222308 is handled. Duration 16 ms by bot id=8216054898
2026-07-05 22:18:00,189 INFO DAEMON: Task 39434a00-9c27-42b1-a213-8c09232d75c2 created state=NEW topic_id=2
2026-07-05 22:18:00,190 INFO DAEMON: Update id=262222309 is handled. Duration 21 ms by bot id=8216054898
