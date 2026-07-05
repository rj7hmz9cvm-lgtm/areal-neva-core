# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-07-05T10:24:48.187727+00:00
git_sha_before_commit: 7badda1a81b6fe0d9beb9116753247928b816e8d
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
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
685de4e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
2e5cdc8 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
d0d7133 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6adb83a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
ed66701 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
4ebb0a7 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
66c8f22 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
218963e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c8a9f1c Topic2 canonical estimate live repair
fed18c2 Enforce Sonar-only explicit search policy
a51e72a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7aff8a6 feat(topic2): PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1 — top-level price choice interceptor
3ceedaf fix(topic2): close price choice loop after price enrichment
3723bbe fix(topic2): PATCH_KARKASNIK_SHEET_FIX_V1 — correct sheet for frame houses

## GIT_SHOW_STAT_HEAD
commit 7badda1a81b6fe0d9beb9116753247928b816e8d
Author: root <root@graceful-olive.ptr.network>
Date:   Sun Jul 5 12:54:52 2026 +0300

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
- FAILED|3000
- CANCELLED|859
- DONE|638
- ARCHIVED|381

## CORE_DB_OPEN_TASKS
- 0

## LATEST_TASKS_15
- 489cfefe-3048-4056-8362-2dfc90a3196a|2|text|CANCELLED|Посчитай мне проект который я тебе скидывал последний|✅ Предварительная смета готова

Объект: барнхаус 8.0x12.0 м
Этажей: 1
Площадь застройки: 96.0 м²
Расчётная площадь: 96.0 м²
Фундамент: монолитная плита
Стены: г|2026-07-05 08:09:37
- 16b3b2e6-c3b0-4c27-95ac-854d5b3c9fdd|2|text|FAILED|вот проект|Из какого материала строим?|2026-07-05 08:04:03
- 5a9afade-f25d-466e-8dc7-c7b247cdd24f|2|text|DONE|посчитать работы и материалы согласно проекта|Уточнение добавлено к исходному ТЗ|2026-07-05 07:53:04
- dfdc5ca5-7bb3-48c8-8d66-1b79d279312e|2|text|FAILED|пусто

УТОЧНЕНИЕ К ИСХОДНОМУ ТЗ:
посчитать работы и материалы согласно проекта|Из какого материала строим?|2026-07-05 08:03:07
- 84d1a6b5-630d-4189-9dd7-b1ba1477456b|2|text|DONE|3|Выбор цен привязан к основной задаче: max|2026-07-05 07:52:01
- 2896fd60-3a3e-407a-b370-ee1891fdc3ac|2|text|DONE|2|Выбор цен привязан к основной задаче: median|2026-07-05 07:47:37
- 929aa2f1-1477-490d-a79b-f37a1e528b91|2|text|CANCELLED|Если есть вопросы задавай|None|2026-07-05 07:31:05
- a82cfa53-b9a6-467e-935c-3e98e1f5d605|2|drive_file|DONE|{"file_id": "1FC_ZKLpC_yQ0kM7WJciJcMFIZW8PZHQm", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio|Закрыто новой сметой TOPIC2_ONE_BIG_FINAL_PIPELINE_V1|2026-07-05 08:09:30
- 88d9fc26-a5f3-44e7-a128-2c615c341289|2|drive_file|CANCELLED|{"file_id": "1jjke-Boab3b8A2DhKiyQT5eIRXWOrYf6", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio||2026-07-05 07:35:01
- 3d00bfb5-f8cd-4bb7-9bdf-7f081b67f380|2|text|DONE|2|Выбор цен привязан к основной задаче: median|2026-07-05 07:13:58
- 29331db4-0403-4a5b-8516-88e535202da6|2|drive_file|FAILED|{"file_id": "1jjke-Boab3b8A2DhKiyQT5eIRXWOrYf6", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio|Принял файл «Стадия Р_АР.pdf». Что нужно сделать?

1️⃣ Смета — извлечь позиции, посчитать объёмы, создать Excel
2️⃣ Описание — описать содержимое документа
3️⃣ |2026-07-05 07:24:54
- ab764f2b-a336-4588-b26c-2e94a4e5f2e3|2|text|FAILED|[VOICE] Необходимо посчитать проект. Проект находится в 100 километров от Санкт-Петербурга. Соответственно, сейчас скину|Не получил Google Drive ссылки XLSX/PDF. Локальные пути заблокированы
Стены: каркасная технология

Учтено из дополнений к ТЗ:
- Этажность: 1 этаж
- Стены: карка|2026-07-05 07:24:54
- 0115efea-ed49-4263-a6f0-a981a760261c|2|text|DONE|Сделай мне расчёт дом два этажа на монолитный плите толщиной 450 размеры дома 24 на 24 наружные стены кирпичные целый ря|✅ Смета готова

Объект: барнхаус 24.0x24.0 м
Этажей: 2
Площадь застройки: 576.0 м²
Расчётная площадь: 1152.0 м²
Фундамент: монолитная плита
Стены: кирпич
Фасад:|2026-07-04 22:29:13
- 34c707f3-cea7-4c51-aa02-638ed3b139af|2|text|DONE|Сделай мне расчёт дом два этажа на монолитный плите толщиной 450 размеры дома 24 на 24 наружные стены кирпичные целый ря|✅ Смета готова

Объект: барнхаус 24.0x24.0 м
Этажей: 2
Площадь застройки: 576.0 м²
Расчётная площадь: 1152.0 м²
Фундамент: монолитная плита
Стены: кирпич
Фасад:|2026-07-04 22:24:32
- 076aca4c-68e5-4b89-b194-4c5c020d299d|2|text|CANCELLED|Сделай мне расчёт дом два этажа на монолитный плите толщиной 450 размеры дома 24 на 24 наружные стены кирпичные целый ря|Уточнение добавлено к исходному ТЗ|2026-07-04 21:52:55

## LATEST_FAILED_10
- 16b3b2e6-c3b0-4c27-95ac-854d5b3c9fdd|2|вот проект|STALE_TIMEOUT|2026-07-05 08:04:03
- dfdc5ca5-7bb3-48c8-8d66-1b79d279312e|2|пусто

УТОЧНЕНИЕ К ИСХОДНОМУ ТЗ:
посчитать работы и материалы согласно проекта|STALE_TIMEOUT|2026-07-05 08:03:07
- 29331db4-0403-4a5b-8516-88e535202da6|2|{"file_id": "1jjke-Boab3b8A2DhKiyQT5eIRXWOrYf6", "file_name": "Стадия Р_АР.pdf", "mime_type": "application/pdf", "captio|STALE_TIMEOUT|2026-07-05 07:24:54
- ab764f2b-a336-4588-b26c-2e94a4e5f2e3|2|[VOICE] Необходимо посчитать проект. Проект находится в 100 километров от Санкт-Петербурга. Соответственно, сейчас скину|STALE_TIMEOUT|2026-07-05 07:24:54
- 5a453d88-7bee-4b61-a510-303fda0b51ef|2|[VOICE] Дом 10х10, два этажа.|STALE_TIMEOUT|2026-07-04 20:06:42
- c82ce66e-0e82-4d62-861b-73413d8a15e2|2|[VOICE] Привет, Орик! Как дела? Отзовись! Все ли у тебя в порядке? Расскажи, как ты себя чувствуешь? Готов ли ты работат|STALE_TIMEOUT|2026-07-04 15:40:25
- 71aa047d-8bce-41cd-9a6e-d5620b28c1ef|0|TEST_AFTER_RESTORE_20260704|INVALID_RESULT_GATE|2026-07-04 14:50:39
- 0b1a2b5f-a924-4c6a-b123-d24d6bdac167|2|{"source": "manual_runtime_requeue", "request": "полный канонический вывод сметы XLSX и PDF без duplicate guard", "reque|NO_VALID_ARTIFACT|2026-07-04 18:31:28
- b57b1bae-32a3-404f-a49c-4d02160a63a5|2|Сформируй финальную смету XLSX и PDF по канону topic_2
Ценовой уровень: median
Материал: каркас
Шаблон: М-80 или М-110 п|STALE_TIMEOUT|2026-05-09 17:18:10
- 57cee6eb-ddd9-4962-9eb9-fed3abfd3919|2|да сделай документы|STALE_TIMEOUT|2026-05-09 15:38:17

## LATEST_TASK_HISTORY_20
- 489cfefe-3048-4056-8362-2dfc90a3196a|PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1:OK:16bJuvB9wXDGjfgBsXKJ24RkD1-ZDUP2H:1cHMBzForY1jWVGLuKGhkz_b0s5Lxgm4n|2026-07-05 08:09:37
- 489cfefe-3048-4056-8362-2dfc90a3196a|cancelled|2026-07-05T08:09:35.645802+00:00
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_PRICE_SOURCE_FOUND:Поставщики стройматериалов:ООО "Союз Балт Строй":Sonar|2026-07-05 08:09:34
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_PRICE_SOURCE_FOUND:Поставщики стройматериалов:ООО "СК-Пласт":Sonar|2026-07-05 08:09:34
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_PRICE_SOURCE_FOUND:Поставщики стройматериалов:ООО "Сантех-Сервис":Sonar|2026-07-05 08:09:34
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_PRICE_SOURCE_FOUND:Поставщики стройматериалов:ООО "АГОС":Sonar|2026-07-05 08:09:34
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_PRICE_SOURCE_FOUND:Поставщики стройматериалов:ООО "НОРДИКС":Sonar|2026-07-05 08:09:34
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_PRICE_SOURCE_FOUND:Поставщики стройматериалов:ООО "НИИ Вектор":Sonar|2026-07-05 08:09:34
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_PRICE_SOURCE_FOUND:Поставщики стройматериалов:ООО "Нестор":Sonar|2026-07-05 08:09:34
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_PRICE_SOURCE_FOUND:Поставщики стройматериалов:ООО "ТД ПетроСтрой":Sonar|2026-07-05 08:09:34
- 489cfefe-3048-4056-8362-2dfc90a3196a|PATCH_TOPIC2_PDF_AND_REAL_SUPPLIERS_V1:SONAR_SEARCH_OK:8|2026-07-05 08:09:34
- 489cfefe-3048-4056-8362-2dfc90a3196a|PATCH_TOPIC2_SUPPLIER_AND_HEAL_V1:TG_EDIT:OK|2026-07-05 08:09:30
- a82cfa53-b9a6-467e-935c-3e98e1f5d605|TOPIC2_ONE_BIG_FINAL_PIPELINE_V1:superseded_by:489cfefe-3048-4056-8362-2dfc90a3196a|2026-07-05 08:09:30
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_DONE_ONLY_AFTER_USER_YES_V1:P3_FINAL_WAITING_CONFIRMATION|2026-07-05 08:09:29
- 489cfefe-3048-4056-8362-2dfc90a3196a|P3_TOPIC2_FINAL_DONE_ROWS_20_PRICE_APPLIED_4|2026-07-05 08:09:29
- 489cfefe-3048-4056-8362-2dfc90a3196a|P3_TOPIC2_FINAL_AWAITING_CONFIRMATION_ROWS_20_PRICE_APPLIED_4|2026-07-05 08:09:29
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_CANONICAL_REROUTE_V2:FALLBACK_TO_OLD_PIPELINE|2026-07-05 08:09:20
- 489cfefe-3048-4056-8362-2dfc90a3196a|clarified:Отмена задач|2026-07-05T08:09:19.865315+00:00
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_CANONICAL_REROUTE_V2:CANONICAL_HANDLED|2026-07-05 08:09:12
- 489cfefe-3048-4056-8362-2dfc90a3196a|TOPIC2_MISSING_GATE_ANTILOOP_BLOCKED_DEFAULTS:count=4|2026-07-05 08:09:12

## MEMORY_DB_COUNT
- 5275

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-07-05T10:24:47.927212+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-07-05T10:24:47.927716+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-07-05T10:24:47.906379+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-07-05T10:24:47.906932+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-07-05T10:24:47.846835+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-07-05T10:24:47.847213+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-07-05T10:24:47.836004+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-07-05T10:24:47.836666+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-07-05T10:24:47.801975+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-07-05T10:24:47.802613+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T10:24:47.727144+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-07-05T10:24:47.727012+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T10:24:47.726936+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T10:24:47.726817+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-07-05T10:24:47.726756+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-07-05T10:24:47.726689+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T10:24:47.726613+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T10:24:47.726444+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T10:24:47.726230+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T10:24:47.726117+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T10:24:47.725760+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-07-05T10:24:47.725473+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T10:24:47.725370+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-07-05T10:24:47.725123+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-07-05T10:24:47.724916+00:00

## JOURNAL_AREAL_TASK_WORKER_60
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 253.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 254.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 255.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 256.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 257.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 258.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 259.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 260.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 261.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 262.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 263.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 264.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 265.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 266.
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),

## JOURNAL_TELEGRAM_INGRESS_30
2026-07-05 10:13:38,199 INFO DAEMON: Task 29331db4-0403-4a5b-8516-88e535202da6 created state=NEW topic_id=2
2026-07-05 10:13:38,261 INFO DAEMON: Update id=262222265 is handled. Duration 3463 ms by bot id=8216054898
2026-07-05 10:13:57,877 INFO DAEMON: Task 3d00bfb5-f8cd-4bb7-9bdf-7f081b67f380 created state=NEW topic_id=2
2026-07-05 10:13:57,877 INFO DAEMON: Update id=262222266 is handled. Duration 10 ms by bot id=8216054898
2026-07-05 10:14:04,389 INFO DAEMON: Update id=262222267 is handled. Duration 85 ms by bot id=8216054898
2026-07-05 10:25:23,433 INFO DAEMON: Update id=262222268 is handled. Duration 79 ms by bot id=8216054898
2026-07-05 10:26:45,664 INFO DAEMON: Update id=262222269 is handled. Duration 94 ms by bot id=8216054898
2026-07-05 10:27:21,269 INFO DAEMON: Update id=262222270 is handled. Duration 79 ms by bot id=8216054898
2026-07-05 10:28:23,362 INFO DAEMON: file_cache is only supported with oauth2client<4.0.0
2026-07-05 10:28:25,673 INFO DAEMON: Task a82cfa53-b9a6-467e-935c-3e98e1f5d605 created state=NEW topic_id=2
2026-07-05 10:28:25,831 INFO DAEMON: Update id=262222271 is handled. Duration 3383 ms by bot id=8216054898
2026-07-05 10:29:51,612 INFO DAEMON: Task 929aa2f1-1477-490d-a79b-f37a1e528b91 created state=NEW topic_id=2
2026-07-05 10:29:51,612 INFO DAEMON: Update id=262222272 is handled. Duration 9 ms by bot id=8216054898
2026-07-05 10:47:37,085 INFO DAEMON: Task 2896fd60-3a3e-407a-b370-ee1891fdc3ac created state=NEW topic_id=2
2026-07-05 10:47:37,085 INFO DAEMON: Update id=262222273 is handled. Duration 8 ms by bot id=8216054898
2026-07-05 10:52:00,279 INFO DAEMON: Task 84d1a6b5-630d-4189-9dd7-b1ba1477456b created state=NEW topic_id=2
2026-07-05 10:52:00,279 INFO DAEMON: Update id=262222274 is handled. Duration 10 ms by bot id=8216054898
2026-07-05 10:52:40,224 INFO DAEMON: Task dfdc5ca5-7bb3-48c8-8d66-1b79d279312e created state=NEW topic_id=2
2026-07-05 10:52:40,224 INFO DAEMON: Update id=262222275 is handled. Duration 9 ms by bot id=8216054898
2026-07-05 10:53:02,850 INFO DAEMON: Task 5a9afade-f25d-466e-8dc7-c7b247cdd24f created state=NEW topic_id=2
2026-07-05 10:53:02,850 INFO DAEMON: Update id=262222276 is handled. Duration 12 ms by bot id=8216054898
2026-07-05 10:53:27,567 INFO DAEMON: Task 16b3b2e6-c3b0-4c27-95ac-854d5b3c9fdd created state=NEW topic_id=2
2026-07-05 10:53:27,567 INFO DAEMON: Update id=262222277 is handled. Duration 12 ms by bot id=8216054898
2026-07-05 10:53:41,162 INFO DAEMON: Update id=262222278 is handled. Duration 164 ms by bot id=8216054898
2026-07-05 10:53:50,286 INFO DAEMON: Update id=262222279 is handled. Duration 78 ms by bot id=8216054898
2026-07-05 10:54:00,981 INFO DAEMON: Update id=262222280 is handled. Duration 91 ms by bot id=8216054898
2026-07-05 11:09:11,500 INFO DAEMON: Task 489cfefe-3048-4056-8362-2dfc90a3196a created state=NEW topic_id=2
2026-07-05 11:09:11,501 INFO DAEMON: Update id=262222281 is handled. Duration 13 ms by bot id=8216054898
2026-07-05 11:09:19,960 INFO DAEMON: Update id=262222282 is handled. Duration 103 ms by bot id=8216054898
2026-07-05 11:09:35,721 INFO DAEMON: Update id=262222283 is handled. Duration 79 ms by bot id=8216054898
