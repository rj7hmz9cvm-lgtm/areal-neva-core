# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-05-09T17:35:02.215215+00:00
git_sha_before_commit: 7aff8a6c8fa2d5b28aa4188a5e888b6d87ae65e1
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: inactive

## GIT_LOG_30
7aff8a6 feat(topic2): PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1 — top-level price choice interceptor
3ceedaf fix(topic2): close price choice loop after price enrichment
3723bbe fix(topic2): PATCH_KARKASNIK_SHEET_FIX_V1 — correct sheet for frame houses
2624bd4 PATCH_PRICE_CONFIRMATION_ROUTING_V1 fix: avoid false positive on 'сделай'
7128b4c PATCH_PRICE_CONFIRMATION_ROUTING_V1: fix price confirmation not recognized
8159c05 fix(price): PATCH_PRICE_ENRICHMENT_IDEMPOTENT_V1 — skip duplicate Sonar on re-poll
9426008 fix(full-canon): FULL_CANON_CLOSURE_VERIFIED_V1 — close 7 live blockers
7cc4523 fix(topic2): classify frame house with imitation timber finish
8b21d75 fix(topic2): price WC always runs + gate stale-context fixes
b8b72d1 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
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

## GIT_SHOW_STAT_HEAD
commit 7aff8a6c8fa2d5b28aa4188a5e888b6d87ae65e1
Author: Ila <ilakuznecov@mac.local>
Date:   Sat May 9 20:30:56 2026 +0300

    feat(topic2): PATCH_TOPIC2_FINAL_DRIVE_SINGLE_GATE_V1 — top-level price choice interceptor
    
    Top-level _handle_new interceptor for topic_2 that catches price choice
    (1/2/3/да делай/etc.) before V4/V5/V6 wrappers, binds to parent task,
    enriches raw with dims from memory.db + drive file JSON, and calls
    handle_topic2_estimate_final_close directly.
    
    Guards: _update_task blocks DONE with /root/ paths for topic_2.
    Fallback: if TOPIC2_PRICE_CHOICE_CONFIRMED: in history but no DONE_WITH_DRIVE_LINKS,
    re-runs Drive finalization on task pickup.
    
    Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 docs/HANDOFFS/LATEST_HANDOFF.md |   62 +--
 task_worker.py                  | 1129 +++++++++++++++++++++++++++++++++++++++
 2 files changed, 1160 insertions(+), 31 deletions(-)

## GIT_CHANGED_FILES_10
core/stroyka_estimate_canon.py
core/topic2_input_gate.py
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
- FAILED|2992
- CANCELLED|833
- DONE|595
- ARCHIVED|381
- WAITING_CLARIFICATION|1

## CORE_DB_OPEN_TASKS
- 1

## LATEST_TASKS_15
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|2|text|WAITING_CLARIFICATION|Вот это добавь техническое задание по дому|Выбери уровень цен: 1 дешёвые / 2 средние / 3 надёжные / 4 вручную|2026-05-09 17:34:22
- 845efde0-1c3f-4412-b9ce-748c183989a8|2|search|DONE|Так что по ТЗ мне надо чтоб было посчитана разно широкая доска с поднятым ворсом окрашена это на фасады металлочерепица |TOPIC2_ONE_BIG_FINAL_PIPELINE_V1: generated search subtask blocked|2026-05-09 17:25:12
- 95593050-d879-463e-bbfc-129e1c04f526|2|drive_file|DONE|{"file_id": "13uqh4jfWRCqBMYuSbRxqVcexgxAokUIR", "file_name": "8х12.pdf", "mime_type": "application/pdf", "caption": "сд|✅ Предварительная смета готова

Объект: барнхаус 8.0x12.0 м
Этажей: 1
Площадь застройки: 96.0 м²
Расчётная площадь: 96.0 м²
Фундамент: монолитная плита
Стены: к|2026-05-09 17:22:49
- ea71e94d-f854-4ba6-a8cb-0b9703c5e5b0|2|text|DONE|2 средние делвай смету каркас|Выбор цен привязан к основной задаче: median|2026-05-09 16:35:33
- b2512271-c4d4-48c9-827c-0f8d8d9874fe|2|search|DONE|средняя цена логистика база да каркас стены 150 мм утепление поток 250 мм|TOPIC2_ONE_BIG_FINAL_PIPELINE_V1: generated search subtask blocked|2026-05-09 16:07:36
- b57b1bae-32a3-404f-a49c-4d02160a63a5|2|text|FAILED|Сформируй финальную смету XLSX и PDF по канону topic_2
Ценовой уровень: median
Материал: каркас
Шаблон: М-80 или М-110 п|Пришли задание заново — расскажи что нужно сделать.|2026-05-09 17:18:10
- 6cea21c1-f4ca-4ee2-9d7c-465048a750da|2|drive_file|CANCELLED|{"file_id": "1mDC8kYBEGkTq1PJ3X4ESzu8LEwzr-X4e", "file_name": "8х12.pdf", "mime_type": "application/pdf", "caption": "сд|Понял, ничего не меняю. Если понадоблюсь — напишите.|2026-05-09T16:05:29.748877+00:00
- f17b18cd-aec5-444f-a28f-d26ca6044ed6|2|text|DONE|завершены задачи|Активный контекст найден
Задача: f17b18cd-aec5-444f-a28f-d26ca6044ed6
Статус: NEW
Кратко: завершены задачи|2026-05-09 15:39:35
- 57cee6eb-ddd9-4962-9eb9-fed3abfd3919|2|text|FAILED|да сделай документы|Пришли задание заново — расскажи что нужно сделать.|2026-05-09 15:38:17
- d9b4d3d7-6be7-49bd-84b2-e61264266776|2|text|FAILED|Посчитай мне смету по вот этому техническому заданию|⏳ Задачу понял

Шаблон: М-80.xlsx
Лист: смета
Объект: дом
Материал: каркас
Размеры: не указаны
Этажей: не указано
Фундамент: свайный фундамент
Удалённость: 20.0|2026-05-09 14:58:24
- ad80ae4f-2346-4558-a439-3b2b96395bd8|2|text|CANCELLED|[VOICE] У тебя же ведь есть вся информация, я не понимаю. Все, давай отменяй задачу, заебал, блядь.|None|2026-05-09 12:15:18
- 073664f2-f219-481d-aa20-38b2690ee852|2|text|CANCELLED|[VOICE] Сориентируйся по задаче, которую я тебе ставил. Причем тут вообще газобетон, я понять не могу.|Где находится объект: город или удалённость в км?|2026-05-09 12:14:52
- 3142e545-fe4c-4744-8332-a9e72188d2a7|2|text|CANCELLED|[VOICE] Чё это за хуйня?|⏳ Задачу понял

Шаблон: Ареал Нева.xlsx
Лист: смета
Объект: дом
Материал: газобетон
Размеры: (8.5, 12.5)
Этажей: не указано
Фундамент: монолитная плита
Удалённо|2026-05-09 12:13:13
- 5c4ae112-e701-489b-88f3-492070a1b446|2|text|CANCELLED|[VOICE] Отмена задачи я тебе говорю|None|2026-05-09 12:11:13
- fe7035e0-8da8-47f7-ac4c-d33821ed250e|2|text|CANCELLED|[VOICE] У тебя же есть вся информация Давай мне уже смету в конце концов, блядь, заебал|⏳ Задачу понял

Шаблон: фундамент_Склад2.xlsx
Лист: смета
Объект: фундамент
Материал: не указан
Размеры: не указаны
Этажей: не указано
Фундамент: свайный фундам|2026-05-09 12:11:07

## LATEST_FAILED_10
- b57b1bae-32a3-404f-a49c-4d02160a63a5|2|Сформируй финальную смету XLSX и PDF по канону topic_2
Ценовой уровень: median
Материал: каркас
Шаблон: М-80 или М-110 п|STALE_TIMEOUT|2026-05-09 17:18:10
- 57cee6eb-ddd9-4962-9eb9-fed3abfd3919|2|да сделай документы|STALE_TIMEOUT|2026-05-09 15:38:17
- d9b4d3d7-6be7-49bd-84b2-e61264266776|2|Посчитай мне смету по вот этому техническому заданию|STALE_TIMEOUT|2026-05-09 14:58:24
- 952f5635-e6f8-45bd-9b98-6bc996bd71f6|2|[VOICE] Все есть у тебя в чате, в тех заданиях.|STALE_TIMEOUT|2026-05-09 11:47:08
- e375fd12-ddd0-4b4b-956c-25d0ce42dc7f|2|[VOICE] А вы что тут газобетонные блоки? Я тебе какое задание давал? Скажи мне пожалуйста|STALE_TIMEOUT|2026-05-09 11:45:04
- 28345d3b-acc3-45dd-88b5-87aabb1fdc03|2|это залупа|STALE_TIMEOUT|2026-05-09 11:45:18
- e69e83eb-6bf5-45e1-aba7-74c031a05d31|2|Все есть|STALE_TIMEOUT|2026-05-09 10:36:55
- da4c6f8a-c13c-4703-bf8e-57f920b657b3|2|{"file_id": "1DHNTRAtMzC_NE-Bo5Q8E7cSuCHg_vQl8", "file_name": "photo_-1003725299009_10765.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-05-09 11:26:08
- 413a55d6-c438-466a-927a-06b401aea4f9|2|{"file_id": "130Dx5k1hTx7MHj7OtAQH8WYmlB5g-hKv", "file_name": "photo_-1003725299009_10761.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-05-09 09:39:48
- 555f7a1d-fdfa-4608-86ee-fdc7aeddb0ed|2|[VOICE] посчитай мне пожалуйста по техническому заданию которое я тебе сделал мне нужна смета на дом|STALE_TIMEOUT|2026-05-09 08:11:42

## LATEST_TASK_HISTORY_20
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_CANONICAL_REROUTE_V2:CANONICAL_HANDLED|2026-05-09 17:34:22
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown|2026-05-09 17:34:22
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_OLD_PUBLIC_OUTPUT_BLOCKED_BY_PRICE_CHOICE_GATE|2026-05-09 17:34:22
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_PRICE_CHOICE_REQUESTED|2026-05-09 17:34:22
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_PRICE_SOURCE_FOUND:Работы по монтажу и кладке:TSK Company:CONFIRMED|2026-05-09 17:34:22
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_PRICE_WORK_SEARCH_STARTED:Работы по монтажу и кладке|2026-05-09 17:34:07
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_PRICE_SOURCE_FOUND:бетон монолит:betondaily.ru:CONFIRMED|2026-05-09 17:34:07
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:бетон монолит|2026-05-09 17:33:52
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_PRICE_SOURCE_FOUND:Арматура А500:MEPEN:UNVERIFIED|2026-05-09 17:33:52
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Арматура А500|2026-05-09 17:33:33
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_PRICE_SOURCE_FOUND:Бетон В25:beton-spb.ru:UNVERIFIED|2026-05-09 17:33:33
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:Бетон В25|2026-05-09 17:33:25
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_PRICE_ENRICHMENT_DONE:594|2026-05-09 17:33:25
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_PRICE_ENRICHMENT_STARTED|2026-05-09 17:33:20
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_ONLINE_MODEL_SONAR_CONFIRMED:perplexity/sonar|2026-05-09 17:33:20
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_MISSING_GATE_ANTILOOP:count=3_proceeding_with_defaults|2026-05-09 17:33:18
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|TOPIC2_REPEAT_PARENT_TASK:6cea21c1-f4ca-4ee2-9d7c-465048a750da|2026-05-09 17:33:18
- 53897bf2-b320-4fc7-9d3b-a8006cca1e3e|created:NEW|2026-05-09T17:33:17.586140+00:00
- 845efde0-1c3f-4412-b9ce-748c183989a8|TOPIC2_ONE_BIG_FINAL_PIPELINE_V1:blocked_search_subtask|2026-05-09 17:25:12
- 845efde0-1c3f-4412-b9ce-748c183989a8|created:NEW|2026-05-09T17:25:12.139556+00:00

## MEMORY_DB_COUNT
- 5230

## LATEST_MEMORY_20
- topic_2_estimate_pending_53897bf2-b320-4fc7-9d3b-a8006cca1e3e|{
  "version": "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3",
  "status": "WAITING_PRICE_CONFIRMATION",
  "task_id": "53897bf2-b320-4fc7-9d3b-a8006cca1e3e",
  "chat_id": "-1003725299009",|2026-05-09T17:34:22.467502
- topic_2_estimate_pending_95593050-d879-463e-bbfc-129e1c04f526|{
  "version": "FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3",
  "status": "STALE_DEPRECATED",
  "task_id": "95593050-d879-463e-bbfc-129e1c04f526",
  "chat_id": "-1003725299009",
  "topic_|2026-05-09T17:33:18.404100
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-05-09T17:22:53.053506+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-05-09T17:22:53.054286+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-05-09T17:22:53.030713+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-05-09T17:22:53.031660+00:00
- topic_11_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 11, "count": 2, "updated_at": "2026-05-09T17:22:52.969517+00:00", "files": [{"task_id": "a073c181-7a10-426e-8752-7d72dc4ef978", "file_id":|2026-05-09T17:22:52.970032+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-05-09T17:22:52.959781+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-05-09T17:22:52.960335+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-05-09T17:22:52.925402+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-05-09T17:22:52.926136+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-09T17:22:52.862928+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-05-09T17:22:52.862810+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-09T17:22:52.862697+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-09T17:22:52.862608+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-09T17:22:52.862528+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-05-09T17:22:52.862455+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T17:22:52.862368+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T17:22:52.862162+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T17:22:52.861938+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T17:22:52.861839+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T17:22:52.861450+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-05-09T17:22:52.861049+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-09T17:22:52.860916+00:00

## JOURNAL_AREAL_TASK_WORKER_60
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 36.604s CPU time, 106.1M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 28.092s CPU time, 102.7M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Main process exited, code=exited, status=1/FAILURE
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Failed with result 'exit-code'.
areal-task-worker.service: Scheduled restart job, restart counter is at 1.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 18.857s CPU time, 106.2M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 7.922s CPU time, 106.2M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 28.505s CPU time, 106.2M memory peak, 0B memory swap peak.
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
areal-task-worker.service: Consumed 5.663s CPU time, 86.1M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 18.477s CPU time.
Started areal-task-worker.service - Areal Task Worker.

## JOURNAL_TELEGRAM_INGRESS_30
2026-05-09 19:26:36,717 INFO DAEMON: Update id=210388211 is handled. Duration 122 ms by bot id=8216054898
2026-05-09 19:26:46,168 INFO DAEMON: Update id=210388212 is handled. Duration 98 ms by bot id=8216054898
2026-05-09 19:28:33,865 INFO DAEMON: Update id=210388213 is handled. Duration 146 ms by bot id=8216054898
2026-05-09 19:28:44,400 INFO DAEMON: Update id=210388214 is handled. Duration 77 ms by bot id=8216054898
2026-05-09 19:36:00,683 INFO DAEMON: Update id=210388215 is handled. Duration 159 ms by bot id=8216054898
2026-05-09 19:36:12,127 INFO DAEMON: Update id=210388216 is handled. Duration 79 ms by bot id=8216054898
2026-05-09 19:36:22,795 INFO DAEMON: Update id=210388217 is handled. Duration 77 ms by bot id=8216054898
2026-05-09 19:36:29,370 INFO DAEMON: Update id=210388218 is handled. Duration 93 ms by bot id=8216054898
2026-05-09 19:36:40,209 INFO DAEMON: Update id=210388219 is handled. Duration 68 ms by bot id=8216054898
2026-05-09 19:43:36,452 INFO DAEMON: Update id=210388220 is handled. Duration 115 ms by bot id=8216054898
2026-05-09 19:48:14,048 INFO DAEMON: Update id=210388221 is handled. Duration 125 ms by bot id=8216054898
2026-05-09 19:48:18,437 INFO DAEMON: Update id=210388222 is handled. Duration 76 ms by bot id=8216054898
2026-05-09 20:08:48,681 INFO DAEMON: LOCAL_BOT_API_ABSOLUTE_PATH_USED:file_26.pdf
2026-05-09 20:08:48,860 INFO DAEMON: file_cache is only supported with oauth2client<4.0.0
2026-05-09 20:08:51,039 INFO DAEMON: Task 95593050-d879-463e-bbfc-129e1c04f526 created state=NEW topic_id=2
2026-05-09 20:08:51,148 INFO DAEMON: Update id=210388223 is handled. Duration 2467 ms by bot id=8216054898
2026-05-09 20:09:07,215 INFO DAEMON: Update id=210388224 is handled. Duration 84 ms by bot id=8216054898
2026-05-09 20:09:19,132 INFO DAEMON: Update id=210388225 is handled. Duration 128 ms by bot id=8216054898
2026-05-09 20:09:24,010 INFO DAEMON: Update id=210388226 is handled. Duration 75 ms by bot id=8216054898
2026-05-09 20:09:59,398 INFO DAEMON: Update id=210388227 is handled. Duration 316 ms by bot id=8216054898
2026-05-09 20:10:13,259 INFO DAEMON: Update id=210388228 is handled. Duration 84 ms by bot id=8216054898
2026-05-09 20:10:54,120 INFO DAEMON: Update id=210388229 is handled. Duration 152 ms by bot id=8216054898
2026-05-09 20:10:59,298 INFO DAEMON: Update id=210388230 is handled. Duration 115 ms by bot id=8216054898
2026-05-09 20:21:08,532 INFO DAEMON: Update id=210388231 is handled. Duration 127 ms by bot id=8216054898
2026-05-09 20:21:30,902 INFO DAEMON: Update id=210388232 is handled. Duration 84 ms by bot id=8216054898
2026-05-09 20:22:39,713 INFO DAEMON: Update id=210388233 is handled. Duration 123 ms by bot id=8216054898
2026-05-09 20:25:12,142 INFO DAEMON: Task 845efde0-1c3f-4412-b9ce-748c183989a8 created state=NEW topic_id=2
2026-05-09 20:25:12,142 INFO DAEMON: Update id=210388234 is handled. Duration 11 ms by bot id=8216054898
2026-05-09 20:33:17,588 INFO DAEMON: Task 53897bf2-b320-4fc7-9d3b-a8006cca1e3e created state=NEW topic_id=2
2026-05-09 20:33:17,588 INFO DAEMON: Update id=210388235 is handled. Duration 16 ms by bot id=8216054898
