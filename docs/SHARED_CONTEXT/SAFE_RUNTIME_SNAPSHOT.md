# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-05-09T07:40:02.145670+00:00
git_sha_before_commit: 62a5da22f1c20cb0ad84a06020938053156ddd54
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: inactive

## GIT_LOG_30
62a5da2 fix(topic2): remove hardcoded drainage parent 043e5c9f — dynamic lookup by state
4cb4e75 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
f53ec3b FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7d98580 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
7a5f770 fix(topic210): canonical pile count route
786e4c8 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
c533c40 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
9f7bcac FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
3ac0907 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
ca312d9 fix(topic210): pile count route and db lock recover guard
d79bb95 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
10f6152 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
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

## GIT_SHOW_STAT_HEAD
commit 62a5da22f1c20cb0ad84a06020938053156ddd54
Author: Ila <ilakuznecov@mac.local>
Date:   Sat May 9 10:36:21 2026 +0300

    fix(topic2): remove hardcoded drainage parent 043e5c9f — dynamic lookup by state
    
    PATCH_TOPIC2_REMOVE_HARDCODED_DRAINAGE_PARENT_V1
    
    Root cause: _t2dpg_get_parent used hardcoded task_id without state filter.
    043e5c9f (FAILED/EXECUTION_TIMEOUT) was absorbing new topic_2 tasks.
    Fix: dynamic SELECT by chat_id+topic_id+state=WAITING_CLARIFICATION+error_message=TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN.
    No DB schema change. No hardcoded IDs.
    
    Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 task_worker.py | 44 ++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 44 insertions(+)

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

## CORE_DB_STATE_COUNTS
- FAILED|2979
- CANCELLED|824
- DONE|586
- ARCHIVED|381
- WAITING_CLARIFICATION|3
- AWAITING_CONFIRMATION|1

## CORE_DB_OPEN_TASKS
- 4

## LATEST_TASKS_15
- 41b7962e-9c33-4471-805a-75a62a70590c|2|drive_file|WAITING_CLARIFICATION|{"file_id": "1vbiTlbYyc680ghEPWylyiRVmggGqY3w6", "file_name": "photo_-1003725299009_10715.jpg", "mime_type": "image/jpeg|Что строим: дом, ангар, склад, фундамент или кровлю?|2026-05-09 07:38:26
- c245e495-5687-41f8-b74a-b1f7c137bfe9|2|text|WAITING_CLARIFICATION|[VOICE] Нет, это не схема дренажа, посмотри, это план дома. Что, ты не видишь, что ли, я не понимаю?|Нет нового ТЗ для расчёта. Смету по старой памяти не запускаю. Напиши конкретную правку или новое полное ТЗ|2026-05-09 07:37:44
- 8289eda8-c463-4691-8764-df80081075cc|2|text|WAITING_CLARIFICATION|Выполни задачу так как тебе написано|PDF определён как схема дренажа/ливнёвки.
Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.
Считать приблизительно по схеме или п|2026-05-09 07:37:13
- a073c181-7a10-426e-8752-7d72dc4ef978|11|text|AWAITING_CONFIRMATION|[VOICE] Мне необходимо найти или создать видео поздравления в телеграм и в социальные сети с праздником 9 мая.|Смета готова.
Позиций: 1. Итого: 0.00 руб
PDF: https://drive.google.com/file/d/1RlE0YZrM-LrbR0dNxQ-CrETV2rKjsKfq/view?usp=drivesdk
XLSX: https://docs.google.com|2026-05-09 07:36:01
- 29c70635-354b-40ad-853c-cece1cc9f8be|2|text|CANCELLED|выполни задание|PDF определён как схема дренажа/ливнёвки.
Домовую смету не запускаю: текущий файл относится к наружным сетям, а не к дому.
Считать приблизительно по схеме или п|2026-05-09T07:31:24.153389+00:00
- 0a0246a7-2cd3-4072-b34f-1e4ebece93f1|2|drive_file|DONE|{"file_id": "1oCGtooOj64nUfW__VguPn09IpD2KR15-", "file_name": "photo_-1003725299009_10689.jpg", "mime_type": "image/jpeg|TOPIC2_CHILD_MERGED_TO_DRAINAGE_PARENT 043e5c9f-e8bc-434c-9dad-a66c7e50f917|2026-05-09 07:02:36
- f09e5a55-5ce8-462d-a356-681b4f5e796b|210|text|DONE|нужно посчитать сваи жб 150-150 на этот дом|Расчёт количества свай по topic_210

Исходные данные:
• Тип: каркасный дом
• Размер в плане: 24×14 м
• Сваи: ж/б 150×150, длина 2,5 м

Принятый расчётный принци|2026-05-09 00:41:09
- 4cd74051-efb8-470e-81f2-ae93e390a98f|210|text|FAILED|итого?|None|2026-05-09 00:40:42
- 088df3dc-14e0-41d2-9187-ef0fdb58a5b7|210|drive_file|FAILED|{"file_id": "1jdseIFUevlE2GJBwJZLAlnCULxfwL0t-", "file_name": "image.jpeg", "mime_type": "image/jpeg", "caption": "посмо||2026-05-09 00:39:53
- b67bd13d-6be6-449b-b8fc-fc4f4fdd60df|210|text|DONE|а если дом 24 на 14 то сколько|Расчёт количества свай по topic_210

Исходные данные:
• Тип: каркасный дом
• Размер в плане: 24×14 м
• Сваи: ж/б 150×150, длина 2,5 м

Принятый расчётный принци|2026-05-09 00:39:06
- f1fbced5-bed0-42b7-90d8-020fe322b216|210|text|DONE|мне надо посчитать сваи 150-150 жб|Расчёт количества свай по topic_210

Исходные данные:
• Тип: каркасный дом
• Размер в плане: 10×8 м
• Сваи: ж/б 150×150, длина 2,5 м

Принятый расчётный принцип|2026-05-09 00:38:33
- ed118834-bd18-4182-baf4-99f3ea017858|210|text|DONE|Сколько нужно свай ж/б 150х150 длиной 2,5м для каркасного дома 8х10?|Расчёт количества свай по topic_210

Исходные данные:
• Дом: каркасный
• Размер в плане: 10×8 м
• Сваи: ж/б 150×150, длина 2,5 м

Расстановка:
• Расчётный шаг с|2026-05-09 00:15:49
- dd000985-408f-4829-85d3-af9df8309f47|210|drive_file|FAILED|{"file_id": "1ZPraIey7-ZPgfl_tqQFh2rTwteKi823f", "file_name": "photo_-1003725299009_10666.jpg", "mime_type": "image/jpeg||2026-05-09 00:13:53
- 0332e116-3d48-42ac-80c2-6aebbac378dc|210|text|FAILED|выполни|None|2026-05-09 00:09:28
- 530e5e89-f3c4-418e-a974-ca06913f15c9|210|text|DONE|[VOICE] Если у тебя нет нужного образца, используй то, что найдешь в интернете, либо посмотри то, что у тебя есть.|Проектные ссылки из Drive (topic_210) — секция: КЖ

1. [UNKNOWN] Баня.pln (FILE)
 Папка: Образцы проектов
 https://drive.google.com/file/d/1G0obdndF7a6Yo84gyWBZ|2026-05-08 23:50:22

## LATEST_FAILED_10
- 4cd74051-efb8-470e-81f2-ae93e390a98f|210|итого?|INVALID_RESULT_GATE|2026-05-09 00:40:42
- 088df3dc-14e0-41d2-9187-ef0fdb58a5b7|210|{"file_id": "1jdseIFUevlE2GJBwJZLAlnCULxfwL0t-", "file_name": "image.jpeg", "mime_type": "image/jpeg", "caption": "посмо|TASK_WORKER_ARTIFACT_GATE_V1:EMPTY_OR_TOO_SHORT|2026-05-09 00:39:53
- dd000985-408f-4829-85d3-af9df8309f47|210|{"file_id": "1ZPraIey7-ZPgfl_tqQFh2rTwteKi823f", "file_name": "photo_-1003725299009_10666.jpg", "mime_type": "image/jpeg|TASK_WORKER_ARTIFACT_GATE_V1:EMPTY_OR_TOO_SHORT|2026-05-09 00:13:53
- 0332e116-3d48-42ac-80c2-6aebbac378dc|210|выполни|INVALID_RESULT_GATE|2026-05-09 00:09:28
- b98e1117-fff5-4d3e-b799-1eb6ad435faa|210|{"file_id": "1ggTNx1h0lhc7LA5MCiewMX57yd-tXc70", "file_name": "photo_-1003725299009_10651.jpg", "mime_type": "image/jpeg|TASK_WORKER_ARTIFACT_GATE_V1:EMPTY_OR_TOO_SHORT|2026-05-08 23:48:08
- f02f874e-91da-480f-9a1e-d2c5d4553b55|210|По размеру дома ты мне сможешь определить сколько свай мне нужно на него?|INVALID_RESULT_GATE|2026-05-08 23:49:05
- 6a535d79-5368-45d8-b8a4-a4c2133f5223|2|[VOICE] посмотри у тебя есть документы в чате я же тебе скидывал уже ты же попросил чтоб я тебе продублировал|STALE_TIMEOUT|2026-05-08 22:33:52
- f9df5eb5-3746-40c4-a730-bbc1a021dbc1|2|[VOICE] Мне необходимо найти стоимость материалов, как указано в техническом задании, и стоимость работы посмотреть. Выш|STALE_TIMEOUT|2026-05-08 22:33:28
- 043e5c9f-e8bc-434c-9dad-a66c7e50f917|2|[VOICE] Посмотри то, что я тебе писал ранее, у тебя же все есть|EXECUTION_TIMEOUT|2026-05-09 07:03:24
- test-multifile-gate-001|2|[VOICE] У тебя два файла. На одном у тебя схема дренажа, на другом у тебя длинные высоты и все есть. Посмотри оба файла |STALE_TIMEOUT|2026-05-08 20:29:32

## LATEST_TASK_HISTORY_20
- 41b7962e-9c33-4471-805a-75a62a70590c|TOPIC2_CANONICAL_PHOTO_ROUTE_FIRST:handled|2026-05-09 07:38:26
- 41b7962e-9c33-4471-805a-75a62a70590c|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:clarification|2026-05-09 07:38:26
- 41b7962e-9c33-4471-805a-75a62a70590c|TOPIC2_REPEAT_PARENT_TASK:29c70635-354b-40ad-853c-cece1cc9f8be|2026-05-09 07:38:26
- 41b7962e-9c33-4471-805a-75a62a70590c|TOPIC2_INPUT_GATE_MIXED_FILES:total=5,drainage=3,other=2|2026-05-09 07:38:26
- 41b7962e-9c33-4471-805a-75a62a70590c|TOPIC2_CANONICAL_PHOTO_ROUTE_FIRST:attempting|2026-05-09 07:38:25
- 41b7962e-9c33-4471-805a-75a62a70590c|clarified:У тебя есть все задание что ты тупишь|2026-05-09T07:38:24.158460+00:00
- 41b7962e-9c33-4471-805a-75a62a70590c|TOPIC2_CANONICAL_PHOTO_ROUTE_FIRST:handled|2026-05-09 07:38:04
- 41b7962e-9c33-4471-805a-75a62a70590c|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:clarification|2026-05-09 07:38:04
- 41b7962e-9c33-4471-805a-75a62a70590c|TOPIC2_REPEAT_PARENT_TASK:29c70635-354b-40ad-853c-cece1cc9f8be|2026-05-09 07:38:04
- 41b7962e-9c33-4471-805a-75a62a70590c|TOPIC2_INPUT_GATE_MIXED_FILES:total=5,drainage=3,other=2|2026-05-09 07:38:04
- 41b7962e-9c33-4471-805a-75a62a70590c|TOPIC2_CANONICAL_PHOTO_ROUTE_FIRST:attempting|2026-05-09 07:38:03
- 41b7962e-9c33-4471-805a-75a62a70590c|created:NEW|2026-05-09T07:38:02.580046+00:00
- c245e495-5687-41f8-b74a-b1f7c137bfe9|reply_sent:p6_topic2_vague_guard|2026-05-09 07:37:45
- c245e495-5687-41f8-b74a-b1f7c137bfe9|P6_TOPIC2_VAGUE_OLD_MEMORY_BLOCKED|2026-05-09 07:37:44
- c245e495-5687-41f8-b74a-b1f7c137bfe9|TOPIC2_GENERIC_CLARIFICATION_BLOCKED|2026-05-09 07:37:44
- c245e495-5687-41f8-b74a-b1f7c137bfe9|created:NEW|2026-05-09T07:37:43.455889+00:00
- 8289eda8-c463-4691-8764-df80081075cc|reply_sent:waiting_clarification|2026-05-09 07:37:14
- 8289eda8-c463-4691-8764-df80081075cc|TOPIC2_INPUT_GATE_SENT:10711|2026-05-09 07:37:14
- 8289eda8-c463-4691-8764-df80081075cc|TOPIC2_INPUT_GATE_HANDLED:state=WAITING_CLARIFICATION:domain=drainage_network|2026-05-09 07:37:13
- 8289eda8-c463-4691-8764-df80081075cc|TOPIC2_CURRENT_FILE_SOURCE_OF_TRUTH:eba6dc80-d993-43e8-945b-cf1b48b9d103_Схема глубинного дренажа.pdf,mikea_rp3.pdf|2026-05-09 07:37:13

## MEMORY_DB_COUNT
- 5210

## LATEST_MEMORY_20
- active_task|{'task_id': 'a073c181-7a10-426e-8752-7d72dc4ef978', 'type': 'estimate', 'state': 'AWAITING_CONFIRMATION'}|2026-05-09T07:36:01.965919
- topic_11_last_estimate|{'task_id': 'a073c181-7a10-426e-8752-7d72dc4ef978', 'rows': 1, 'total': 0.0, 'bot_message_id': 10705}|2026-05-09T07:36:01.961522
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-05-09T07:22:35.061470+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-05-09T07:22:35.061968+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-05-09T07:22:35.043057+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-05-09T07:22:35.043879+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-05-09T07:22:34.983238+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-05-09T07:22:34.983751+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-05-09T07:22:34.949198+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-05-09T07:22:34.949884+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-09T07:22:34.893136+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-05-09T07:22:34.893025+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-09T07:22:34.892936+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-09T07:22:34.892788+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-09T07:22:34.892714+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-05-09T07:22:34.892604+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T07:22:34.892482+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T07:22:34.892246+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T07:22:34.891975+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T07:22:34.891831+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T07:22:34.891429+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-05-09T07:22:34.891058+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T07:22:34.890932+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T07:22:34.890613+00:00

## JOURNAL_AREAL_TASK_WORKER_60
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
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 32.174s CPU time, 108.6M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 12.179s CPU time, 129.3M memory peak, 22.8M memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 31.680s CPU time.
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:641: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 10min 6.464s CPU time.
Started areal-task-worker.service - Areal Task Worker.

## JOURNAL_TELEGRAM_INGRESS_30
2026-05-09 10:02:35,601 INFO DAEMON: Update id=210388130 is handled. Duration 3006 ms by bot id=8216054898
2026-05-09 10:03:23,387 INFO DAEMON: Update id=210388131 is handled. Duration 78 ms by bot id=8216054898
2026-05-09 10:23:06,737 INFO DAEMON: Update id=210388132 is handled. Duration 16 ms by bot id=8216054898
2026-05-09 10:31:11,511 INFO DAEMON: Task 29c70635-354b-40ad-853c-cece1cc9f8be created state=NEW topic_id=2
2026-05-09 10:31:11,511 INFO DAEMON: Update id=210388133 is handled. Duration 17 ms by bot id=8216054898
2026-05-09 10:31:19,610 INFO DAEMON: Update id=210388134 is handled. Duration 144 ms by bot id=8216054898
2026-05-09 10:31:24,216 INFO DAEMON: Update id=210388135 is handled. Duration 67 ms by bot id=8216054898
2026-05-09 10:35:53,623 INFO DAEMON: LOCAL_BOT_API_ABSOLUTE_PATH_USED:file_16.oga
2026-05-09 10:35:53,623 INFO DAEMON: STT env check groq=True
2026-05-09 10:35:53,623 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10703.ogg size=45953 model=whisper-large-v3-turbo
2026-05-09 10:35:53,890 INFO DAEMON: STT http_status=200
2026-05-09 10:35:53,893 INFO DAEMON: STT ok transcript_len=102
2026-05-09 10:35:54,007 INFO DAEMON: Task a073c181-7a10-426e-8752-7d72dc4ef978 created state=NEW topic_id=11
2026-05-09 10:35:54,007 INFO DAEMON: Update id=210388136 is handled. Duration 516 ms by bot id=8216054898
2026-05-09 10:36:10,578 INFO DAEMON: Update id=210388137 is handled. Duration 115 ms by bot id=8216054898
2026-05-09 10:36:35,788 INFO DAEMON: Update id=210388138 is handled. Duration 71 ms by bot id=8216054898
2026-05-09 10:37:12,417 INFO DAEMON: Task 8289eda8-c463-4691-8764-df80081075cc created state=NEW topic_id=2
2026-05-09 10:37:12,417 INFO DAEMON: Update id=210388139 is handled. Duration 15 ms by bot id=8216054898
2026-05-09 10:37:42,988 INFO DAEMON: LOCAL_BOT_API_ABSOLUTE_PATH_USED:file_17.oga
2026-05-09 10:37:42,988 INFO DAEMON: STT env check groq=True
2026-05-09 10:37:42,988 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10712.ogg size=26879 model=whisper-large-v3-turbo
2026-05-09 10:37:43,346 INFO DAEMON: STT http_status=200
2026-05-09 10:37:43,347 INFO DAEMON: STT ok transcript_len=92
2026-05-09 10:37:43,460 INFO DAEMON: Task c245e495-5687-41f8-b74a-b1f7c137bfe9 created state=NEW topic_id=2
2026-05-09 10:37:43,460 INFO DAEMON: Update id=210388140 is handled. Duration 547 ms by bot id=8216054898
2026-05-09 10:37:59,901 INFO DAEMON: LOCAL_BOT_API_ABSOLUTE_PATH_USED:file_12.jpg
2026-05-09 10:38:00,040 INFO DAEMON: file_cache is only supported with oauth2client<4.0.0
2026-05-09 10:38:02,583 INFO DAEMON: Task 41b7962e-9c33-4471-805a-75a62a70590c created state=NEW topic_id=2
2026-05-09 10:38:02,648 INFO DAEMON: Update id=210388141 is handled. Duration 2748 ms by bot id=8216054898
2026-05-09 10:38:24,231 INFO DAEMON: Update id=210388142 is handled. Duration 81 ms by bot id=8216054898
