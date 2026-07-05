# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-07-05T17:24:57.723245+00:00
git_sha_before_commit: 0e17a9baccd6e6ba25b9f1c3cf64d77f99a17be7
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
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
4c51410 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
64dbcda FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
573ccf6 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
93709b3 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
fce2824 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
f1ddd8e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
32438ee FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

## GIT_SHOW_STAT_HEAD
commit 0e17a9baccd6e6ba25b9f1c3cf64d77f99a17be7
Author: root <root@graceful-olive.ptr.network>
Date:   Sun Jul 5 19:55:03 2026 +0300

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
 docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md       | 190 ++++++++++-----------
 .../SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md |   4 +-
 docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md   |  48 +++---
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
 69 files changed, 256 insertions(+), 256 deletions(-)

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
- FAILED|3001
- CANCELLED|863
- DONE|646
- ARCHIVED|381
- WAITING_CLARIFICATION|1

## CORE_DB_OPEN_TASKS
- 1

## LATEST_TASKS_15
- 9225f446-cbce-4376-ba14-4cff3ab8828a|2|text|DONE|2|Выбор цен привязан к основной задаче: median|2026-07-05 17:24:15
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|2|drive_file|WAITING_CLARIFICATION|{"file_id": "1f_VpraIIeLAgELtAj94IEzbwDQ5h08Qs", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio|Не получил Google Drive ссылки XLSX/PDF. Локальные пути заблокированы
Стены: каркасная технология

Учтено из дополнений к ТЗ:
- Стены: каркасная технология
- Фу|2026-07-05 17:24:15
- c81e2756-db52-4277-b694-1631c3f75f14|2|text|DONE|2|Выбор цен привязан к основной задаче: median|2026-07-05 12:31:29
- 0f073abf-0aef-4d0e-ac2c-35676ebc999c|2|text|DONE|1|Выбор цен привязан к основной задаче: min|2026-07-05 12:31:07
- 9c5946d7-f37f-488f-bf2c-b2045310238a|2|drive_file|FAILED|{"file_id": "1f_VpraIIeLAgELtAj94IEzbwDQ5h08Qs", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio|PDF прочитан, но сметная ведомость объёмов/спецификация работ в нём не найдена. Смету на 0 руб не создаю. Для канонного расчёта пришли ВОР / спецификацию / разд|2026-07-05 17:14:13
- 9e15be11-1af3-422b-b680-b57b9d633df4|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 12:13:50
- af5de40c-8a9c-4278-a440-da3911c67e2c|2|text|DONE|1|Выбор цен привязан к основной задаче: min|2026-07-05 12:07:24
- 1217e297-c599-45f6-939f-8a800d352397|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 12:05:42
- b1276c2d-3c54-4246-9c36-523ab1600fe8|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 12:00:35
- f64ed50a-2329-4cc4-8982-b80211e187d3|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 11:53:22
- 437283c2-73a1-4ea9-820c-d7dac38d4c20|2|text|CANCELLED|Да выполни по нему расчёт и по описанию

PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1: FULL RECALC CONTEXT|P6E67_MERGED_TO_PARENT_TASK a82cfa53-b9a6-467e-935c-3e98e1f5d605|2026-07-05 12:13:59
- ea794751-2522-488e-be9c-f76f10a48d93|2|drive_file|FAILED|{"file_id": "1FC_ZKLpC_yQ0kM7WJciJcMFIZW8PZHQm", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio|Задача не выполнена: NO_VALID_ARTIFACT|2026-07-05 11:50:22
- 63c9fde2-ac68-46cb-a0cb-26fad15a4a05|2|text|DONE|2|Выбор цен привязан к основной задаче: median|2026-07-05 11:49:03
- 937d37c3-1df1-4f5f-990a-b75ed7230799|2|text|CANCELLED|Посчитай мне проект который я тебе скидывал последний

PATCH_TOPIC2_ADDITIONAL_FACTS_FULL_RECALC_CANON_RESTORE_V1: FULL |Не получил Google Drive ссылки XLSX/PDF. Локальные пути заблокированы
Стены: каркасная технология

Учтено из дополнений к ТЗ:
- Этажность: 1 этаж
- Стены: карка|2026-07-05T11:50:20.924883Z
- 489cfefe-3048-4056-8362-2dfc90a3196a|2|text|CANCELLED|Посчитай мне проект который я тебе скидывал последний|✅ Предварительная смета готова

Объект: барнхаус 8.0x12.0 м
Этажей: 1
Площадь застройки: 96.0 м²
Расчётная площадь: 96.0 м²
Фундамент: монолитная плита
Стены: г|2026-07-05 08:09:37

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
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DRIVE_LINK_REQUIRED|2026-07-05 17:24:15
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V2_ACTIVE_BEFORE_MAIN:RESULT_SANITIZED|2026-07-05 17:24:15
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|TOPIC2_PDF_NO_VALID_ESTIMATE_ROWS_WAITING_INPUT|2026-07-05 17:24:15
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|PATCH_TOPIC2_FULL_CLOSE_TZ_MATERIALS_PRICE_V2_ACTIVE_BEFORE_MAIN:RESULT_SANITIZED|2026-07-05 17:24:15
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:DRIVE_FINAL_START|2026-07-05 17:24:15
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:PARENT_RAW_ENRICHED|2026-07-05 17:24:15
- 9225f446-cbce-4376-ba14-4cff3ab8828a|PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:MERGED_TO:33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|2026-07-05 17:24:15
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1:CHOICE_BOUND_FROM:9225f446-cbce-4376-ba14-4cff3ab8828a|2026-07-05 17:24:15
- 9225f446-cbce-4376-ba14-4cff3ab8828a|created:NEW|2026-07-05T17:24:14.079990+00:00
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown|2026-07-05 17:23:53
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|TOPIC2_PRICE_CHOICE_CONFIRMED_FROM_CAPTION|2026-07-05 17:23:53
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|TOPIC2_PRICE_CHOICE_CONFIRMED:median|2026-07-05 17:23:53
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|TOPIC2_PRICE_SOURCE_FOUND:Работы по монтажу и кладке:RealZagDom:CONFIRMED|2026-07-05 17:23:53
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|TOPIC2_PRICE_WORK_SEARCH_STARTED:Работы по монтажу и кладке|2026-07-05 17:23:37
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|TOPIC2_PRICE_SOURCE_FOUND:монолитная плита:Петрович:CONFIRMED|2026-07-05 17:23:37
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:монолитная плита|2026-07-05 17:23:30
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|TOPIC2_PRICE_SOURCE_FOUND:Арматура А500:Петрович:CONFIRMED|2026-07-05 17:23:30
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Арматура А500|2026-07-05 17:23:23
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|TOPIC2_PRICE_SOURCE_FOUND:Бетон В25:Mayak Beton:CONFIRMED|2026-07-05 17:23:23
- 33bd7b5a-ade8-47a8-b07e-4db4d3cacca8|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Бетон В25|2026-07-05 17:23:17

## MEMORY_DB_COUNT
- 5285

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-07-05T17:24:57.447436+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-07-05T17:24:57.448028+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-07-05T17:24:57.425490+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-07-05T17:24:57.425974+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-07-05T17:24:57.363374+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-07-05T17:24:57.363671+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-07-05T17:24:57.355001+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-07-05T17:24:57.355384+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-07-05T17:24:57.323169+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-07-05T17:24:57.323643+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T17:24:57.244870+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-07-05T17:24:57.244792+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T17:24:57.244725+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T17:24:57.244629+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T17:24:57.244573+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-07-05T17:24:57.244505+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T17:24:57.244429+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T17:24:57.244230+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T17:24:57.243981+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T17:24:57.243839+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T17:24:57.243492+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-07-05T17:24:57.243208+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T17:24:57.243104+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T17:24:57.242854+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-07-05T17:24:57.242491+00:00

## JOURNAL_AREAL_TASK_WORKER_60
areal-task-worker.service: Scheduled restart job, restart counter is at 783.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 784.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 785.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 786.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 787.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 788.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 789.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 790.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 791.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 792.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 793.
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
areal-task-worker.service: Consumed 54.758s CPU time, 526.9M memory peak, 0B memory swap peak.
areal-task-worker.service: Scheduled restart job, restart counter is at 794.
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),

## JOURNAL_TELEGRAM_INGRESS_30
2026-07-05 11:09:35,721 INFO DAEMON: Update id=262222283 is handled. Duration 79 ms by bot id=8216054898
2026-07-05 14:48:44,950 INFO DAEMON: Update id=262222284 is handled. Duration 171 ms by bot id=8216054898
2026-07-05 14:49:05,737 INFO DAEMON: Update id=262222285 is handled. Duration 8 ms by bot id=8216054898
2026-07-05 14:51:44,304 INFO DAEMON: Task 437283c2-73a1-4ea9-820c-d7dac38d4c20 created state=NEW topic_id=2
2026-07-05 14:51:44,304 INFO DAEMON: Update id=262222286 is handled. Duration 13 ms by bot id=8216054898
2026-07-05 14:53:08,908 INFO DAEMON: Update id=262222287 is handled. Duration 74 ms by bot id=8216054898
2026-07-05 14:53:21,719 INFO DAEMON: Task f64ed50a-2329-4cc4-8982-b80211e187d3 created state=NEW topic_id=2
2026-07-05 14:53:21,720 INFO DAEMON: Update id=262222288 is handled. Duration 7 ms by bot id=8216054898
2026-07-05 15:00:34,279 INFO DAEMON: Task b1276c2d-3c54-4246-9c36-523ab1600fe8 created state=NEW topic_id=2
2026-07-05 15:00:34,279 INFO DAEMON: Update id=262222289 is handled. Duration 8 ms by bot id=8216054898
2026-07-05 15:05:41,563 INFO DAEMON: Task 1217e297-c599-45f6-939f-8a800d352397 created state=NEW topic_id=2
2026-07-05 15:05:41,563 INFO DAEMON: Update id=262222290 is handled. Duration 10 ms by bot id=8216054898
2026-07-05 15:07:23,632 INFO DAEMON: Task af5de40c-8a9c-4278-a440-da3911c67e2c created state=NEW topic_id=2
2026-07-05 15:07:23,632 INFO DAEMON: Update id=262222291 is handled. Duration 8 ms by bot id=8216054898
2026-07-05 15:09:28,052 INFO DAEMON: Update id=262222292 is handled. Duration 139 ms by bot id=8216054898
2026-07-05 15:11:04,051 INFO DAEMON: Update id=262222293 is handled. Duration 68 ms by bot id=8216054898
2026-07-05 15:12:16,762 INFO DAEMON: Update id=262222294 is handled. Duration 72 ms by bot id=8216054898
2026-07-05 15:13:49,863 INFO DAEMON: Task 9e15be11-1af3-422b-b680-b57b9d633df4 created state=NEW topic_id=2
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
