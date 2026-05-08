# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-05-08T23:50:02.293788+00:00
git_sha_before_commit: 82535ed3c4087a2bbd99020991b7f03e1150fb1c
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: inactive

## GIT_LOG_30
82535ed FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
36b3c2d FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
00af427 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
876e5d2 fix(topic2): PATCH_TOPIC2_WC_PICKER_DRAINAGE_MULTIFILE_V3 — stop WC loop, bind drainage replies to parent, include all 3 user PDFs
5cabdb8 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
844c3ae FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
107186a fix(topic2): TOPIC2_WCG_SQL_FIX_SYNTAX_AND_LIKE_DROP_V1
24e65b0 fix(topic2): TOPIC2_WCG_PRESERVE_DRAINAGE_ERROR_V1 — preserve drainage length error through WCG skip
c956edd fix(topic2): TOPIC2_DRAINAGE_PARENT_GUARD_V2 — bind drainage followups to parent and block silent continue
7c4ea9a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
bce535d PATCH_TOPIC2_DRAINAGE_RECOGNIZE_ALL_V1
a2d244f FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
bf60881 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
0152cb4 fix(topic2): TOPIC2_DRAINAGE_PRICE_ENRICHMENT_CANON_FIX_V1
4479511 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
9196960 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
b07a265 fix(topic2): TOPIC2_DRAINAGE_LENGTH_PROOF_GATE_AND_ONLINE_PRICES_V2
eb76615 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
fd5778e docs: update LATEST_HANDOFF af42c97 — drainage full close, child merge patch
af42c97 fix(topic2): TOPIC2_DRAINAGE_FULL_CLOSE_NO_LOOP_V2 — child merge guard, legend filter, noise tasks closed
859c045 fix(topic2): TOPIC2_DRAINAGE_VAT_GATE_PUBLIC_CLEAN_V1 — VAT gate 22%, source filter, clean public output, Drive upload fix
3343690 fix(topic2): TOPIC2_DRAINAGE_MULTIFILE_REPAIR_CLOSE_V1 — close drainage estimate from two PDFs, send XLSX+PDF to Telegram
5f3e6cc FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
531398c docs: update LATEST_HANDOFF 3421216 — gate+delivery session close
3421216 fix(topic2): gate send fix (dict(task) for sqlite3.Row) + WCG delivery guard on picker cycle
4cedce3 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
db7d006 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
80b0809 fix(topic2): PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 — current file source-of-truth gate blocks stale house context for drainage PDF
6862c04 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
6923bea FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

## GIT_SHOW_STAT_HEAD
commit 82535ed3c4087a2bbd99020991b7f03e1150fb1c
Author: Ila <ilakuznecov@mac.local>
Date:   Sat May 9 02:45:07 2026 +0300

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
 .../ORCHESTRA_FULL_CONTEXT_MANIFEST.json           |  10 +-
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
 docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md       | 130 +++++++++++----------
 .../SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md |  12 +-
 docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md   |  70 +++++------
 docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md         |   6 +-
 docs/SHARED_CONTEXT/TOPICS/topic_0_COMMON.md       |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_11_VIDEO.md       |   4 +-
 .../TOPICS/topic_210_PROEKTIROVANIE.md             |  14 ++-
 docs/SHARED_CONTEXT/TOPICS/topic_2_STROYKA.md      |   4 +-
 .../TOPICS/topic_3008_KODY_MOZGOV.md               |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_4569_CRM_LEADS.md |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_500_VEB_POISK.md  |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_5_TEKHNADZOR.md   |   4 +-
 .../SHARED_CONTEXT/TOPICS/topic_6104_JOB_SEARCH.md |   4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_794_DEVOPS.md     |   4 +-
 .../TOPICS/topic_961_AVTOZAPCHASTI.md              |   4 +-
 docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md          |   6 +-
 68 files changed, 252 insertions(+), 244 deletions(-)

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
tools/__init__.py
tools/topic2_drainage_repair_close.py

## CORE_DB_STATE_COUNTS
- FAILED|2974
- CANCELLED|823
- DONE|580
- ARCHIVED|381

## CORE_DB_OPEN_TASKS
- 0

## LATEST_TASKS_15
- b98e1117-fff5-4d3e-b799-1eb6ad435faa|210|drive_file|FAILED|{"file_id": "1ggTNx1h0lhc7LA5MCiewMX57yd-tXc70", "file_name": "photo_-1003725299009_10651.jpg", "mime_type": "image/jpeg||2026-05-08 23:48:08
- f02f874e-91da-480f-9a1e-d2c5d4553b55|210|text|FAILED|По размеру дома ты мне сможешь определить сколько свай мне нужно на него?|Расчёт количества свай — нужны исходные данные:

1. Размер дома в плане (например 8×10 м)
2. Этажность (1 этаж, 1+мансарда, 2 этажа)
3. Стеновой материал (брус,|2026-05-08 23:49:05
- 6a535d79-5368-45d8-b8a4-a4c2133f5223|2|text|FAILED|[VOICE] посмотри у тебя есть документы в чате я же тебе скидывал уже ты же попросил чтоб я тебе продублировал|PDF определён как схема дренажа/ливнёвки.
Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.
Считать приблизительно по схеме или п|2026-05-08 22:33:52
- f9df5eb5-3746-40c4-a730-bbc1a021dbc1|2|text|FAILED|[VOICE] Мне необходимо найти стоимость материалов, как указано в техническом задании, и стоимость работы посмотреть. Выш|PDF определён как схема дренажа/ливнёвки.
Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.
Считать приблизительно по схеме или п|2026-05-08 22:33:28
- 85992edd-85cd-4406-85b5-b08b335cb8af|2|text|DONE|Да жду всё верно|PDF определён как схема дренажа/ливнёвки.
Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.
Считать приблизительно по схеме или п|2026-05-08 21:50:33
- 9a174a37-fc01-4414-97f9-064621356083|2|text|DONE|А смета-то где|PDF определён как схема дренажа/ливнёвки.
Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.
Считать приблизительно по схеме или п|2026-05-08 20:47:30
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|2|text|DONE|[VOICE] Посмотри то, что я тебе писал ранее, у тебя же все есть|✅ Смета дренажа готова

Объект: наружные сети / дренаж / ливневая канализация
Файлы учтены: file_2.pdf   file_1.pdf   file_0.pdf
Цены: онлайн-поиск OpenRouter/S|2026-05-08T23:47:17.592846+00:00
- test-multifile-gate-001|2|text|FAILED|[VOICE] У тебя два файла. На одном у тебя схема дренажа, на другом у тебя длинные высоты и все есть. Посмотри оба файла |⏳ Задачу понял

Шаблон: Ареал Нева.xlsx
Лист: смета
Объект: дом
Материал: газобетон
Размеры: (8.5, 12.5)
Этажей: не указано
Фундамент: монолитная плита
Удалённо|2026-05-08 20:29:32
- 2c732335-4650-439e-9287-0984497b4aa6|2|text|FAILED|[VOICE] Я тебе прислал два файла, там есть все длинные, там есть все размеры, посмотри, пожалуйста, внимательно. Два фай|PDF определён как схема дренажа/ливнёвки.
Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.
Считать приблизительно по схеме или п|2026-05-08 20:20:28
- test-gate-send-fix-001|2|text|FAILED|[VOICE] У тебя два файла. На одном у тебя схема дренажа, на другом у тебя длинные высоты и все есть. Посмотри оба файла |PDF определён как схема дренажа/ливнёвки.
Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.
Считать приблизительно по схеме или п|2026-05-08 20:19:46
- e425b052-455f-46b4-990f-1421b7dac675|2|text|FAILED|[VOICE] У тебя два файла. На одном у тебя схема дренажа, на другом у тебя длинные высоты и все есть. Посмотри оба файла |PDF определён как схема дренажа/ливнёвки.
Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.
Считать приблизительно по схеме или п|2026-05-08 19:40:15
- acdae011-7299-482d-92c2-571f8ccbee0c|2|text|FAILED|[VOICE] необходимо посчитать смету взять ценник высокого ценового сегмента на работу и на материалы и создать по длине и|PDF определён как схема дренажа/ливнёвки.
Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.
Считать приблизительно по схеме или п|2026-05-08 19:39:38
- test-gate-drainage-live-001|2|drive_file|FAILED|{"file_name": "Схема глубинного дренажа.pdf", "mime_type": "application/pdf", "local_path": "/root/.areal-neva-core/runt|Принял файл «Схема глубинного дренажа.pdf». Что нужно сделать?

1️⃣ Смета — извлечь позиции, посчитать объёмы, создать Excel
2️⃣ Описание — описать содержимое д|2026-05-08 19:40:26
- test-drainage-reply-001|2|text|FAILED|Объект находится 50 км от Санкт-Петербурга цены выше среднего нужно посчитать стоимость работы материалов по данному зап|⏳ Задачу понял

Шаблон: Ареал Нева.xlsx
Лист: смета
Объект: дом
Материал: газобетон
Размеры: (8.5, 12.5)
Этажей: не указано
Фундамент: монолитная плита
Удалённо|2026-05-08 18:50:16
- 60b9503b-75cc-4913-bb7b-11092508fdae|2|text|FAILED|[VOICE] Я тебе говорил про вот эту информацию, посмотри.|✅ Смета готова

Объект: дом   Материал: газобетон   Площадь: 106.25 м²   Этажность: не указана   Регион: СПб и ЛО
Шаблон: Ареал Нева.xlsx   Лист: смета   Цены: |2026-05-08 19:17:11

## LATEST_FAILED_10
- b98e1117-fff5-4d3e-b799-1eb6ad435faa|210|{"file_id": "1ggTNx1h0lhc7LA5MCiewMX57yd-tXc70", "file_name": "photo_-1003725299009_10651.jpg", "mime_type": "image/jpeg|TASK_WORKER_ARTIFACT_GATE_V1:EMPTY_OR_TOO_SHORT|2026-05-08 23:48:08
- f02f874e-91da-480f-9a1e-d2c5d4553b55|210|По размеру дома ты мне сможешь определить сколько свай мне нужно на него?|INVALID_RESULT_GATE|2026-05-08 23:49:05
- 6a535d79-5368-45d8-b8a4-a4c2133f5223|2|[VOICE] посмотри у тебя есть документы в чате я же тебе скидывал уже ты же попросил чтоб я тебе продублировал|STALE_TIMEOUT|2026-05-08 22:33:52
- f9df5eb5-3746-40c4-a730-bbc1a021dbc1|2|[VOICE] Мне необходимо найти стоимость материалов, как указано в техническом задании, и стоимость работы посмотреть. Выш|STALE_TIMEOUT|2026-05-08 22:33:28
- test-multifile-gate-001|2|[VOICE] У тебя два файла. На одном у тебя схема дренажа, на другом у тебя длинные высоты и все есть. Посмотри оба файла |STALE_TIMEOUT|2026-05-08 20:29:32
- 2c732335-4650-439e-9287-0984497b4aa6|2|[VOICE] Я тебе прислал два файла, там есть все длинные, там есть все размеры, посмотри, пожалуйста, внимательно. Два фай|STALE_TIMEOUT|2026-05-08 20:20:28
- test-gate-send-fix-001|2|[VOICE] У тебя два файла. На одном у тебя схема дренажа, на другом у тебя длинные высоты и все есть. Посмотри оба файла |STALE_TIMEOUT|2026-05-08 20:19:46
- e425b052-455f-46b4-990f-1421b7dac675|2|[VOICE] У тебя два файла. На одном у тебя схема дренажа, на другом у тебя длинные высоты и все есть. Посмотри оба файла |STALE_TIMEOUT|2026-05-08 19:40:15
- acdae011-7299-482d-92c2-571f8ccbee0c|2|[VOICE] необходимо посчитать смету взять ценник высокого ценового сегмента на работу и на материалы и создать по длине и|STALE_TIMEOUT|2026-05-08 19:39:38
- test-gate-drainage-live-001|2|{"file_name": "Схема глубинного дренажа.pdf", "mime_type": "application/pdf", "local_path": "/root/.areal-neva-core/runt|STALE_TIMEOUT|2026-05-08 19:40:26

## LATEST_TASK_HISTORY_20
- f02f874e-91da-480f-9a1e-d2c5d4553b55|state:FAILED|2026-05-08 23:49:05
- f02f874e-91da-480f-9a1e-d2c5d4553b55|clarified:сваи жб 150х150|2026-05-08T23:48:58.138077+00:00
- b98e1117-fff5-4d3e-b799-1eb6ad435faa|TASK_WORKER_ARTIFACT_GATE_V1:FAILED:EMPTY_OR_TOO_SHORT|2026-05-08 23:48:08
- b98e1117-fff5-4d3e-b799-1eb6ad435faa|created:NEW|2026-05-08T23:48:05.464434+00:00
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|confirmed:DONE|2026-05-08T23:47:17.593154+00:00
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_AWAITING_CONFIRMATION_CLEAN_V1|2026-05-08 23:46:27
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_VAT_PUBLIC_OUTPUT_OK|2026-05-08 23:46:27
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_TELEGRAM_SENT:10648|2026-05-08 23:46:27
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_TELEGRAM_PDF_FALLBACK_SENT|2026-05-08 23:46:27
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_TELEGRAM_XLSX_FALLBACK_SENT|2026-05-08 23:46:27
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_PDF_CREATED:drainage_estimate_clean_043e5c9f_20260509_024617.pdf|2026-05-08 23:46:27
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_XLSX_CREATED:drainage_estimate_clean_043e5c9f_20260509_024617.xlsx|2026-05-08 23:46:27
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_PRICES_SOURCE:OpenRouter/Sonar:mode=average|2026-05-08 23:46:27
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_NO_GENERATED_ARTIFACT_INPUT|2026-05-08 23:46:27
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_SOURCE_FILTER_OK:user_pdfs=3|2026-05-08 23:46:27
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_GENERATE_STARTED|2026-05-08 23:46:17
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_PRICE_CHOICE_CONFIRMED:average|2026-05-08 23:46:17
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_PRICE_CHOICE_MENU_SENT:10645|2026-05-08 23:45:08
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_VAT_MODE:WITHOUT_VAT|2026-05-08 23:45:08
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|TOPIC2_DRAINAGE_LENGTHS_STATUS:PROVEN:total_len=80.0|2026-05-08 23:45:08

## MEMORY_DB_COUNT
- 5201

## LATEST_MEMORY_20
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-05-08T23:48:07.037777+00:00", "files": [{"task_id": "", "file_id": "", "file_name": "photo_-10037252|2026-05-08T23:48:07.038318+00:00
- topic_210_file_content_status_b98e1117-fff5-4d3e-b799-1eb6ad435faa|{"ok": false, "reason": "UNSUPPORTED_TYPE", "file_name": "photo_-1003725299009_10651.jpg"}|2026-05-08T23:48:06.981964
- topic_210_file_b98e1117-fff5-4d3e-b799-1eb6ad435faa|{"task_id": "b98e1117-fff5-4d3e-b799-1eb6ad435faa", "chat_id": "-1003725299009", "topic_id": 210, "file_id": "1ggTNx1h0lhc7LA5MCiewMX57yd-tXc70", "file_name": "photo_-1003725299009|2026-05-08T23:48:06.978977
- topic_210_archive_f02f874e|{"task_id": "f02f874e-91da-480f-9a1e-d2c5d4553b55", "chat_id": "-1003725299009", "topic_id": 210, "direction": "structural_design", "engine": "search_supplier", "input_type": "text|2026-05-08T23:32:20.211178
- topic_2_estimate_pending_test-multifile-gate-001|{
  "version": "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3",
  "status": "GENERATED",
  "task_id": "test-multifile-gate-001",
  "chat_id": "-1003725299009",
  "topic_id": 2,
  "parsed": |2026-05-08T23:32:12.076926
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-05-08T23:22:17.837576+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-05-08T23:22:17.838140+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-05-08T23:22:17.769074+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-05-08T23:22:17.769531+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-05-08T23:22:17.732378+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-05-08T23:22:17.732874+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T23:22:17.682776+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-05-08T23:22:17.682483+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T23:22:17.682325+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T23:22:17.682182+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T23:22:17.682066+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-05-08T23:22:17.681934+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T23:22:17.681771+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T23:22:17.681197+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T23:22:17.680846+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T23:22:17.680633+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T23:22:17.679655+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-05-08T23:22:17.678995+00:00

## JOURNAL_AREAL_TASK_WORKER_60
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 54.712s CPU time, 105.4M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 1.589s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 13.338s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 57.743s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Traceback (most recent call last):
  File "/root/.areal-neva-core/task_worker.py", line 17431, in <module>
    asyncio.run(main())
  File "/usr/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/root/.areal-neva-core/task_worker.py", line 4276, in main
    return await _res
           ^^^^^^^^^^
  File "/root/.areal-neva-core/task_worker.py", line 3849, in main
    _recover_stale_tasks(conn, None)
  File "/root/.areal-neva-core/task_worker.py", line 14861, in _recover_stale_tasks
    return _CTDD_ORIG_RECOVER(conn, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.areal-neva-core/task_worker.py", line 5441, in _recover_stale_tasks
    res = _T500_PSV_ORIG_RECOVER_STALE_TASKS(conn, *args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/.areal-neva-core/task_worker.py", line 1277, in _recover_stale_tasks
    conn.execute("""
sqlite3.OperationalError: database is locked
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Consumed 16.587s CPU time.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
T2WCG_PRESERVE_ERR database is locked
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),

## JOURNAL_TELEGRAM_INGRESS_30
2026-05-09 00:50:30,646 INFO DAEMON: Task 85992edd-85cd-4406-85b5-b08b335cb8af created state=NEW topic_id=2
2026-05-09 00:50:30,646 INFO DAEMON: Update id=210388103 is handled. Duration 18 ms by bot id=8216054898
2026-05-09 01:22:53,881 INFO DAEMON: Update id=210388104 is handled. Duration 202 ms by bot id=8216054898
2026-05-09 01:23:22,928 INFO DAEMON: LOCAL_BOT_API_ABSOLUTE_PATH_USED:file_10.oga
2026-05-09 01:23:22,928 INFO DAEMON: STT env check groq=True
2026-05-09 01:23:22,928 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10618.ogg size=49681 model=whisper-large-v3-turbo
2026-05-09 01:23:23,224 INFO DAEMON: STT http_status=200
2026-05-09 01:23:23,225 INFO DAEMON: STT ok transcript_len=146
2026-05-09 01:23:23,302 INFO DAEMON: Task f9df5eb5-3746-40c4-a730-bbc1a021dbc1 created state=NEW topic_id=2
2026-05-09 01:23:23,302 INFO DAEMON: Update id=210388105 is handled. Duration 508 ms by bot id=8216054898
2026-05-09 01:23:45,717 INFO DAEMON: LOCAL_BOT_API_ABSOLUTE_PATH_USED:file_11.oga
2026-05-09 01:23:45,717 INFO DAEMON: STT env check groq=True
2026-05-09 01:23:45,717 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10621.ogg size=26294 model=whisper-large-v3-turbo
2026-05-09 01:23:45,960 INFO DAEMON: STT http_status=200
2026-05-09 01:23:45,960 INFO DAEMON: STT ok transcript_len=101
2026-05-09 01:23:46,028 INFO DAEMON: Task 6a535d79-5368-45d8-b8a4-a4c2133f5223 created state=NEW topic_id=2
2026-05-09 01:23:46,028 INFO DAEMON: Update id=210388106 is handled. Duration 434 ms by bot id=8216054898
2026-05-09 01:36:37,924 INFO DAEMON: Update id=210388107 is handled. Duration 123 ms by bot id=8216054898
2026-05-09 01:41:35,765 INFO DAEMON: Update id=210388108 is handled. Duration 107 ms by bot id=8216054898
2026-05-09 01:50:40,820 INFO DAEMON: Update id=210388109 is handled. Duration 110 ms by bot id=8216054898
2026-05-09 01:51:16,192 INFO DAEMON: Update id=210388110 is handled. Duration 66 ms by bot id=8216054898
2026-05-09 02:09:20,600 INFO DAEMON: Update id=210388111 is handled. Duration 119 ms by bot id=8216054898
2026-05-09 02:10:26,787 INFO DAEMON: Task f02f874e-91da-480f-9a1e-d2c5d4553b55 created state=NEW topic_id=210
2026-05-09 02:10:26,788 INFO DAEMON: Update id=210388112 is handled. Duration 17 ms by bot id=8216054898
2026-05-09 02:47:17,686 INFO DAEMON: Update id=210388113 is handled. Duration 98 ms by bot id=8216054898
2026-05-09 02:48:02,843 INFO DAEMON: LOCAL_BOT_API_ABSOLUTE_PATH_USED:file_12.jpg
2026-05-09 02:48:03,023 INFO DAEMON: file_cache is only supported with oauth2client<4.0.0
2026-05-09 02:48:05,468 INFO DAEMON: Task b98e1117-fff5-4d3e-b799-1eb6ad435faa created state=NEW topic_id=210
2026-05-09 02:48:05,565 INFO DAEMON: Update id=210388114 is handled. Duration 2862 ms by bot id=8216054898
2026-05-09 02:48:58,197 INFO DAEMON: Update id=210388115 is handled. Duration 73 ms by bot id=8216054898
