# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-05-07T15:15:30.246489+00:00
git_sha_before_commit: 983ced8149ebd4c84be0c2926296ad19722d0d88
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: inactive

## GIT_LOG_30
983ced8 fix(topic2): close 3 remaining V4 gaps (repeat/negative/pdf_missing_question)
2353fc3 fix(topic2): close remaining project/pdf/photo/price/artifact gaps V4
b46bba5 docs(handoff): RUNTIME_V2+V3 full close — handoff for AI/human continuation
ccab9ed fix(topic2): PATCH_TOPIC2_FULL_CLOSE_RUNTIME_V3 — all 9 requirements
055157b fix(topic2): PATCH_TOPIC2_FULL_CLOSE_RUNTIME_V2
ad829c4 fix(topic2): PATCH_TOPIC2_FULL_CANONICAL_CLOSE_ONEPASS_V1 — §9 output + recursion fix
eb4442a docs(session): canon + handoff + chat export 2026-05-07 session close
c7c8755 fix(topic2): inline-fix V1 — replace dead wrappers with body edits
d1f20a0 fix(topic2): full mega-guards V1 — 6 guards закрытие topic_2 acceptance bugs
9420d6a fix(topic2): stroyka meta-confirm guard + reply chain + xlsx 15 cols + topic210 meta guard
58d33aa fix(topic2): stop T2RFP infinite redirect loop for drive_file re-picks
b17bca2 fix(topic2): stop WAITING_CLARIFICATION pick loop
2ef3f86 fix(topic2): price reply thread isolation + chat-aware price search
a054796 feat(topic2): canonical template selection, 15-col XLSX, status guard
79ba839 fix(topic2): redirect simplified v2 path to full P2/P3 pipeline
66a57e1 fix(topic2): route ALL estimates through full P2/P3 pipeline
d9edd5d fix(topic2): auto price enrichment + DONE contract markers
48eed2e fix(topic5): filter garbage from act — canon §4/§5 material filter
bb8e971 fix(topic5): fix vision-blocked condition — {} is not None
fb24e60 fix(topic5): vision-blocked fallback per canon §17 — DOCX from owner text
0e01878 fix(topic5): install python-docx + enable vision via EXTERNAL_PHOTO_ANALYSIS_ALLOWED env
842c52b docs(topic2): update chat export for stroyka price choice patch
ac58cfe docs(topic2): add 20260506 stroyka in progress report
7a9bc69 docs(topic2): add 20260506 stroyka not closed report
20020d1 docs(topic2): add 20260506 stroyka price flow handoff
a27c1ea CHAT EXPORT topic2_stroyka_price_choice_patch 2026-05-06
91b2753 fix(topic2): close stroyka estimate canon runtime contract
a6df8c0 fix(topic2): extend price confirmation phrases + pending estimate TTL to 24h
7b4a634 fix(topic2): fix P6 estimate/vague detection for implicit estimate requests
b466fa9 fix(topic2): inject historical DONE/FAILED/CANCELLED context into estimate pipeline

## GIT_SHOW_STAT_HEAD
commit 983ced8149ebd4c84be0c2926296ad19722d0d88
Author: Ila <ilakuznecov@mac.local>
Date:   Thu May 7 17:53:58 2026 +0300

    fix(topic2): close 3 remaining V4 gaps (repeat/negative/pdf_missing_question)
    
    - _missing_question: return None when pdf_spec_rows or ocr_table_rows present (spec §2 "before _missing_question")
    - revision block: detect negative sub-type → TOPIC2_NEGATIVE_PARENT marker
    - before _parse_request: TOPIC2_REPEAT_PARENT_TASK binding to last closed task for chat+topic
    
    Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

 core/stroyka_estimate_canon.py | 25 +++++++++++++++++++++----
 1 file changed, 21 insertions(+), 4 deletions(-)

## GIT_CHANGED_FILES_10
chat_exports/CHAT_EXPORT__CLAUDE_CODE_TOPIC2_CANONICAL_SESSION__2026-05-07.json
core/sample_template_engine.py
core/stroyka_estimate_canon.py
docs/CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md
docs/CANON_FINAL/TOPIC_500_UNIVERSAL_SEARCH_CANON.md
docs/HANDOFFS/HANDOFF_20260507_RUNTIME_V2_V3_FULL_CLOSE.md
docs/HANDOFFS/HANDOFF_20260507_SESSION_CLOSE.md
docs/HANDOFFS/LATEST_HANDOFF.md
task_worker.py

## CORE_DB_STATE_COUNTS
- FAILED|2961
- CANCELLED|815
- DONE|571
- ARCHIVED|381

## CORE_DB_OPEN_TASKS
- 0

## LATEST_TASKS_15
- a7b2879e-14e6-4002-8a06-f73019d40a99|2|drive_file|FAILED|{"file_id": "1XRwOwZr2Kpxy-wrAUPrBR2dLqHseg7jS", "file_name": "photo_-1003725299009_10394.jpg", "mime_type": "image/jpeg|Не вижу размеры объекта на фото/в ТЗ. Пришли размер в формате 7.8х9.0 или фото крупнее|2026-05-07 13:34:34
- f3b2ae30-35cf-4e08-a25d-d3131d351676|5|text|DONE|Что такое цокольная балка где используется|Пояснение принято к фото: photo_-1003725299009_10122.jpg. В пакете технадзора: 23 шт. Акт не формирую без отдельной команды|2026-05-07 12:25:11
- 64eb9797-1a09-4f21-98f2-3671cf6e835c|2|text|DONE|[VOICE] А что мы вообще в принципе обсуждали в чате, скажи мне пожалуйста, вот за два дня последних|✅ Предварительная смета готова

Объект: дом
Эталон: М-80.xlsx
Лист эталона: Каркас под ключ
Выбор цены: median
Поправка: 0.0%

Разделы:
- Фундамент
- Стены
- Пе|2026-05-06 21:35:37
- 1d00cc5d-5f9f-40dc-a63b-98f99dfc4751|2|text|CANCELLED|[VOICE] А еще какие были после этого задачи? Это я понял, а другие...|P6E67_MERGED_TO_PARENT_TASK 71adbe24-ece1-42ca-a7b5-6160b0aded74|2026-05-06 21:05:15
- 67458c2c-49e2-400a-accc-dd911788b03c|2|text|DONE|[VOICE] итак что у нас по задачам скажи пожалуйста какие эти последние ставил|Последняя задача topic_2:
7bb7416b-5a96-4dc2-813b-5984a9cf9a7f
Статус: CANCELLED
✅ Предварительная смета готова

Объект: дом
Эталон: М-80.xlsx
Лист эталона: Кар|2026-05-06 20:53:57
- 2d644d13-7372-48f7-8775-7e973072c3e0|2|text|CANCELLED|[VOICE] А до этого какие задачи я тебе еще отдавал?|Не нашёл родительскую задачу для reply. Пришли исходное ТЗ заново или ответь на последнее сообщение бота с результатом.|2026-05-06 20:10:57
- 8abdbf70-4b70-4ddd-a728-1d79ad710a21|2|text|DONE|[VOICE] какая у нас последняя с тобой задача была скажи мне|Последняя задача topic_2:
7bb7416b-5a96-4dc2-813b-5984a9cf9a7f
Статус: CANCELLED
✅ Предварительная смета готова

Объект: дом
Эталон: М-80.xlsx
Лист эталона: Кар|2026-05-06 20:06:46
- 7bb7416b-5a96-4dc2-813b-5984a9cf9a7f|2|text|CANCELLED|[VOICE] Как понял меня?|✅ Предварительная смета готова

Объект: дом
Эталон: М-80.xlsx
Лист эталона: Каркас под ключ
Выбор цены: median
Поправка: 0.0%

Разделы:
- Фундамент
- Стены
- Пе|2026-05-06T20:06:18.506053+00:00
- cf15cc9b-ce2a-4848-8c58-5f2428c0be1c|2|text|CANCELLED|[VOICE] Мне нужно посчитать дом по газобетонной технологии. Его размеры 8,5 на 12,5 и есть еще поворот. Это его общая дл|P6E67_MERGED_TO_PARENT_TASK 71adbe24-ece1-42ca-a7b5-6160b0aded74|2026-05-06 21:05:08
- ee3984f3-4e34-4b62-8512-430b24127d34|2|text|CANCELLED|[VOICE] Это ты какую считал задачу? Покажи мне к ней ссылку, пожалуйста.|P6E67_MERGED_TO_PARENT_TASK c661ab5e-9555-4358-b06f-2301c06310d1|2026-05-06 18:04:12
- c661ab5e-9555-4358-b06f-2301c06310d1|2|text|CANCELLED|[VOICE] Ничего менять не надо на самом деле.

---
REVISION_CONTEXT
source=EXACT_REPLY_LINK
P6E67_REVISION_FROM_TASK=ee39|P6E67_MERGED_TO_PARENT_TASK 893436d4-72d2-4bdf-b362-f40d7226570e|2026-05-06 18:04:14
- 893436d4-72d2-4bdf-b362-f40d7226570e|2|text|FAILED|[VOICE] Я тебе прислал картинку, две картинки и я тебе прислал техническое задание. Мне нужно сделать смету, уточнить ст|Задача не выполнена: INVALID_PUBLIC_RESULT|2026-05-06 18:05:02
- b5cc2a4a-a28b-4744-a5ab-33b457fd88af|210|text|DONE|[VOICE] хорошо того что нету посмотри в интернете у тебя же стоят все модули мне нужно запроектировать вот эту схему кот|Проектные ссылки из Drive (topic_210) — секция: КЖ

1. [UNKNOWN] Баня.pln (FILE)
 Папка: Образцы проектов
 https://drive.google.com/file/d/1G0obdndF7a6Yo84gyWBZ|2026-05-06 17:57:49
- cfadbd05-8b7c-4aca-a5e4-62b8d56398bb|210|text|FAILED|[VOICE] Так ты сам должен выбирать то, что тебе нужно, а не спрашивать у меня. У тебя это как образцы для проектирования|Проектные ссылки из Drive (topic_210) — секция: КЖ

1. [UNKNOWN] Баня.pln (FILE)
 Папка: Образцы проектов
 https://drive.google.com/file/d/1G0obdndF7a6Yo84gyWBZ|2026-05-06 17:57:43
- f43100b3-65e8-4412-a3b4-6ab35071825e|2|text|FAILED|[VOICE] Так ты должен мне смету посчитать Посмотреть в интернете сколько это стоит И посчитать мне смету Что ты не понял|TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_ERR:maximum recursion depth exceeded|2026-05-06 17:56:47

## LATEST_FAILED_10
- a7b2879e-14e6-4002-8a06-f73019d40a99|2|{"file_id": "1XRwOwZr2Kpxy-wrAUPrBR2dLqHseg7jS", "file_name": "photo_-1003725299009_10394.jpg", "mime_type": "image/jpeg|STALE_TIMEOUT|2026-05-07 13:34:34
- 893436d4-72d2-4bdf-b362-f40d7226570e|2|[VOICE] Я тебе прислал картинку, две картинки и я тебе прислал техническое задание. Мне нужно сделать смету, уточнить ст|INVALID_PUBLIC_RESULT|2026-05-06 18:05:02
- cfadbd05-8b7c-4aca-a5e4-62b8d56398bb|210|[VOICE] Так ты сам должен выбирать то, что тебе нужно, а не спрашивать у меня. У тебя это как образцы для проектирования|INVALID_RESULT_GATE|2026-05-06 17:57:43
- f43100b3-65e8-4412-a3b4-6ab35071825e|2|[VOICE] Так ты должен мне смету посчитать Посмотреть в интернете сколько это стоит И посчитать мне смету Что ты не понял|TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_ERR:maximum recursion depth exceeded|2026-05-06 17:56:47
- c6b40dfc-854b-430b-9ff1-096ba254f8ac|2|[VOICE] Мне необходимо сделать расчет по стоимости работы материалов, взяв за основу средняя стоимость материалов, либо |STROYKA_QG_FAILED:XLSX_VALIDATE_ERROR:maximum recursion depth exceeded|2026-05-06 17:33:30
- 8212f685-b877-466a-a303-f468a00a664b|2|{"file_id": "1y5C9R1BG9a8Nf6MTu1d8MV_Y5LzLw-K6", "file_name": "Отчет_Мистолово_03.26.pdf", "mime_type": "application/pdf|STALE_TIMEOUT|2026-05-06 17:42:46
- 3828ac7a-d425-482f-b1f8-4ec76d27da82|2|{"file_id": "1zVQWoakxbwssZJbXdudubQSMhLv_qSS9", "file_name": "Схема глубинного дренажа.pdf", "mime_type": "application/|STALE_TIMEOUT|2026-05-06 17:42:46
- b71a685b-b129-446b-bd43-e6298b24f8cc|210|[VOICE] Средние цены поставь везде, на работу и на материалы.|INVALID_RESULT_GATE|2026-05-06 17:32:40
- 6e34406d-335c-4209-a3f6-b98e06791e78|210|{"file_id": "1UAv2GC3Ne3D8I-1YCpmmSNH6CrG5ACQi", "file_name": "Отчет_Мистолово_03.26.pdf", "mime_type": "application/pdf|NO_VALID_ARTIFACT|2026-05-06 17:31:44
- eba6dc80-d993-43e8-945b-cf1b48b9d103|210|{"file_id": "1evYG_-JrYks_cJ3D04LTYgdh1CZnWqTT", "file_name": "Схема глубинного дренажа.pdf", "mime_type": "application/|NO_VALID_ARTIFACT|2026-05-06 17:31:31

## LATEST_TASK_HISTORY_20
- a7b2879e-14e6-4002-8a06-f73019d40a99|reply_sent:stale_failed|2026-05-07 13:34:34
- a7b2879e-14e6-4002-8a06-f73019d40a99|state:FAILED|2026-05-07 13:34:34
- a7b2879e-14e6-4002-8a06-f73019d40a99|clarified:|2026-05-07T13:24:32.795848+00:00
- a7b2879e-14e6-4002-8a06-f73019d40a99|reply_sent:p6e2_topic2_image_estimate_result|2026-05-07 13:20:58
- a7b2879e-14e6-4002-8a06-f73019d40a99|P6E2_CANON_DIMS_NOT_RECOGNIZED|2026-05-07 13:20:58
- a7b2879e-14e6-4002-8a06-f73019d40a99|P6E2_TOPIC2_IMAGE_ESTIMATE_ROUTE_TAKEN|2026-05-07 13:20:58
- a7b2879e-14e6-4002-8a06-f73019d40a99|PATCH_TOPIC2_INLINE_FIX_20260506_V1:V5_PRICE_REJECTED:no_explicit_token_or_long|2026-05-07 13:20:58
- a7b2879e-14e6-4002-8a06-f73019d40a99|PATCH_TOPIC2_INLINE_FIX_20260506_V1:V6C_PRICE_REJECTED:no_explicit_token_or_long|2026-05-07 13:20:58
- a7b2879e-14e6-4002-8a06-f73019d40a99|created:NEW|2026-05-07T13:20:58.176105+00:00
- f3b2ae30-35cf-4e08-a25d-d3131d351676|topic5_reply_photo_comment_bound|2026-05-07 12:25:11
- f3b2ae30-35cf-4e08-a25d-d3131d351676|reply_sent:topic5_reply_photo_comment_bound|2026-05-07 12:25:11
- f3b2ae30-35cf-4e08-a25d-d3131d351676|created:NEW|2026-05-07T12:25:10.370041+00:00
- 64eb9797-1a09-4f21-98f2-3671cf6e835c|FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:estimate_generated|2026-05-06 21:05:35
- 64eb9797-1a09-4f21-98f2-3671cf6e835c|TOPIC2_PRICE_CHOICE_CONFIRMED:median|2026-05-06 21:05:23
- 64eb9797-1a09-4f21-98f2-3671cf6e835c|PATCH_TOPIC2_INLINE_FIX_20260506_V1:V5_PRICE_REJECTED:no_explicit_token_or_long|2026-05-06 21:05:23
- 64eb9797-1a09-4f21-98f2-3671cf6e835c|PATCH_TOPIC2_INLINE_FIX_20260506_V1:V6C_PRICE_REJECTED:no_explicit_token_or_long|2026-05-06 21:05:23
- 71adbe24-ece1-42ca-a7b5-6160b0aded74|FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:DIRECT_TENDER_ESTIMATE_GENERATED|2026-05-06 21:05:22
- 71adbe24-ece1-42ca-a7b5-6160b0aded74|P6E67_BLOCK_ARTIFACT_GATE_TXT_LINK_MISSING_BEFORE_SEND_EX|2026-05-06 21:05:22
- 1d00cc5d-5f9f-40dc-a63b-98f99dfc4751|P6E67_CURRENT_TASK_CANCELLED_MERGED_TO_PARENT:71adbe24-ece1-42ca-a7b5-6160b0aded74|2026-05-06 21:05:15
- 71adbe24-ece1-42ca-a7b5-6160b0aded74|P6E67_REVISION_TEXT_MERGED_FROM_TASK:1d00cc5d-5f9f-40dc-a63b-98f99dfc4751|2026-05-06 21:05:15

## MEMORY_DB_COUNT
- 7726

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-05-07T14:51:02.046400+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-05-07T14:51:02.046984+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-05-07T14:51:02.021451+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-05-07T14:51:02.022205+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-05-07T14:51:01.954019+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-05-07T14:51:01.954370+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-05-07T14:51:01.921914+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-05-07T14:51:01.922371+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-07T14:51:01.860485+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-05-07T14:51:01.860411+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-07T14:51:01.860350+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-07T14:51:01.860267+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-07T14:51:01.860214+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-05-07T14:51:01.860149+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-07T14:51:01.860082+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-07T14:51:01.859929+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-07T14:51:01.859744+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-07T14:51:01.859587+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-07T14:51:01.859280+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-05-07T14:51:01.858974+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-07T14:51:01.858885+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-07T14:51:01.858617+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-05-07T14:51:01.858438+00:00
- topic_210_file_fb6aadc5-b372-488a-aede-f3433a030e55|{"task_id": "fb6aadc5-b372-488a-aede-f3433a030e55", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-07T14:51:01.858330+00:00

## JOURNAL_AREAL_TASK_WORKER_60
DRIVE_TOPIC_FOLDER_ENFORCER_V1_FAILED task=893436d4-72d2-4bdf-b362-f40d7226570e err=maximum recursion depth exceeded
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 1min 3.663s CPU time, 116.5M memory peak, 0B memory swap peak.
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
areal-task-worker.service: Consumed 52.506s CPU time, 76.1M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 12.979s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 1min 40.202s CPU time, 127.4M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 7min 27.063s CPU time, 128.1M memory peak, 0B memory swap peak.
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
areal-task-worker.service: Consumed 13.156s CPU time, 78.0M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 9.080s CPU time, 76.9M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 5min 13.728s CPU time, 76.9M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 6.151s CPU time.
Started areal-task-worker.service - Areal Task Worker.

## JOURNAL_TELEGRAM_INGRESS_30
2026-05-06 23:53:56,701 INFO DAEMON: STT env check groq=True
2026-05-06 23:53:56,701 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10382.ogg size=23194 model=whisper-large-v3-turbo
2026-05-06 23:53:56,931 INFO DAEMON: STT http_status=200
2026-05-06 23:53:56,932 INFO DAEMON: STT ok transcript_len=69
2026-05-06 23:53:57,001 INFO DAEMON: Task 67458c2c-49e2-400a-accc-dd911788b03c created state=NEW topic_id=2
2026-05-06 23:53:57,001 INFO DAEMON: Update id=262221962 is handled. Duration 555 ms by bot id=8216054898
2026-05-06 23:54:08,503 INFO DAEMON: STT env check groq=True
2026-05-06 23:54:08,503 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10385.ogg size=16781 model=whisper-large-v3-turbo
2026-05-06 23:54:08,781 INFO DAEMON: STT http_status=200
2026-05-06 23:54:08,782 INFO DAEMON: STT ok transcript_len=61
2026-05-06 23:54:08,843 INFO DAEMON: Task 1d00cc5d-5f9f-40dc-a63b-98f99dfc4751 created state=NEW topic_id=2
2026-05-06 23:54:08,843 INFO DAEMON: Update id=262221963 is handled. Duration 523 ms by bot id=8216054898
2026-05-06 23:54:49,340 INFO DAEMON: STT env check groq=True
2026-05-06 23:54:49,340 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10388.ogg size=24624 model=whisper-large-v3-turbo
2026-05-06 23:54:49,580 INFO DAEMON: STT http_status=200
2026-05-06 23:54:49,581 INFO DAEMON: STT ok transcript_len=91
2026-05-06 23:54:49,653 INFO DAEMON: Task 64eb9797-1a09-4f21-98f2-3671cf6e835c created state=NEW topic_id=2
2026-05-06 23:54:49,653 INFO DAEMON: Update id=262221964 is handled. Duration 492 ms by bot id=8216054898
2026-05-07 09:43:56,042 ERROR DAEMON: Failed to fetch updates - TelegramNetworkError: HTTP Client says - Request timeout error
2026-05-07 09:43:56,043 WARNING DAEMON: Sleep for 1.000000 seconds and try again... (tryings = 0, bot id = 8216054898)
2026-05-07 09:44:07,147 INFO DAEMON: Connection established (tryings = 1, bot id = 8216054898)
2026-05-07 11:49:12,826 ERROR DAEMON: Failed to fetch updates - TelegramNetworkError: HTTP Client says - ClientOSError: [Errno 104] Connection reset by peer
2026-05-07 11:49:12,826 WARNING DAEMON: Sleep for 1.000000 seconds and try again... (tryings = 0, bot id = 8216054898)
2026-05-07 11:49:23,953 INFO DAEMON: Connection established (tryings = 1, bot id = 8216054898)
2026-05-07 15:25:10,374 INFO DAEMON: Task f3b2ae30-35cf-4e08-a25d-d3131d351676 created state=NEW topic_id=5
2026-05-07 15:25:10,374 INFO DAEMON: Update id=262221965 is handled. Duration 13 ms by bot id=8216054898
2026-05-07 16:20:54,939 INFO DAEMON: file_cache is only supported with oauth2client<4.0.0
2026-05-07 16:20:58,180 INFO DAEMON: Task a7b2879e-14e6-4002-8a06-f73019d40a99 created state=NEW topic_id=2
2026-05-07 16:20:58,299 INFO DAEMON: Update id=262221966 is handled. Duration 3902 ms by bot id=8216054898
2026-05-07 16:24:32,869 INFO DAEMON: Update id=262221967 is handled. Duration 79 ms by bot id=8216054898
