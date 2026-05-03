# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-05-03T09:38:37.091234+00:00
git_sha_before_commit: f78f74d5aeee627b64b7644a495a729ba8d56a98
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: active

## GIT_LOG_30
f78f74d FULL_CONTEXT_AGGREGATOR_V1: publish unified full context
6d24f1e CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
b93e411 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
4c5af54 CANON_ROUTE_FIX_V2: topic500 isolation, list-query guard, estimate plita unblock
6bdfad0 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
d42f9c0 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
247dab0 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
e1b2e4e CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
f543e87 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
8e48c47 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
6bbdf92 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
6b6a07e CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
5188c20 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
6279d4a CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
4b8ddc6 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
2d5e9c5 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
ec39fd4 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
994a04b CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
e9d9676 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
9affd23 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
79c5159 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
f325533 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
20ce0bc CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
d3000b9 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
7128444 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
5197667 P0_LIVE_BUGS_CLOSE_V1: close project index price choice pdf output and search quality
8b2b936 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
c911c80 CLAUDE_BOOTSTRAP_CONTEXT_AUTO_V3: canon locked refresh
88c2635 TAIL_CLOSE_THREE_MISSING_V1: close search markers media group and startup recovery
b7d3a47 AREAL_REFERENCE_FULL_MONOLITH_V1: close owner reference policy index archive and guards

## GIT_SHOW_STAT_HEAD
commit f78f74d5aeee627b64b7644a495a729ba8d56a98
Author: Ila <ilakuznecov@mac.local>
Date:   Sun May 3 12:28:39 2026 +0300

    FULL_CONTEXT_AGGREGATOR_V1: publish unified full context

 .gitignore                                         |     4 +
 docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md    |  7389 +------------
 docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md |    69 +-
 docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md     |    86 +
 docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md          |  3995 +-------
 docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md      |    49 +
 .../ORCHESTRA_FULL_CONTEXT_MANIFEST.json           |  2581 +++++
 .../ORCHESTRA_FULL_CONTEXT_PART_001.md             |  4971 +++++++++
 .../ORCHESTRA_FULL_CONTEXT_PART_002.md             |  5956 +++++++++++
 .../ORCHESTRA_FULL_CONTEXT_PART_003.md             | 10267 +++++++++++++++++++
 .../ORCHESTRA_FULL_CONTEXT_PART_004.md             |  7903 ++++++++++++++
 .../ORCHESTRA_FULL_CONTEXT_PART_005.md             |  8656 ++++++++++++++++
 .../ORCHESTRA_FULL_CONTEXT_PART_006.md             |  3651 +++++++
 .../ORCHESTRA_FULL_CONTEXT_PART_007.md             |  8233 +++++++++++++++
 .../ORCHESTRA_FULL_CONTEXT_PART_008.md             |  8359 +++++++++++++++
 .../ORCHESTRA_FULL_CONTEXT_PART_009.md             |  9129 +++++++++++++++++
 .../ORCHESTRA_FULL_CONTEXT_PART_010.md             |  9355 +++++++++++++++++
 .../ORCHESTRA_FULL_CONTEXT_PART_011.md             |  6994 +++++++++++++
 docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md       |   753 +-
 tools/claude_bootstrap_aggregator.py               |   605 +-
 tools/context_aggregator.py                        |   156 +-
 tools/full_context_aggregator.py                   |   739 ++
 22 files changed, 87365 insertions(+), 12535 deletions(-)

## GIT_CHANGED_FILES_10
.gitignore
core/final_closure_engine.py
core/project_route_guard.py
docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md
docs/SHARED_CONTEXT/CLAUDE_SESSION_START_PROMPT.md
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
docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md
task_worker.py
tools/claude_bootstrap_aggregator.py
tools/context_aggregator.py
tools/full_context_aggregator.py

## CORE_DB_STATE_COUNTS
- FAILED|2846
- CANCELLED|762
- DONE|453
- ARCHIVED|381

## CORE_DB_OPEN_TASKS
- 0

## LATEST_TASKS_15
- ff510d77-cf55-48b7-8555-3e820bfeb819|2|text|DONE|[VOICE] Смету в Excel я увижу или нет? Скажи мне, пожалуйста, мне нужна смета. Так-то вроде диагностика вся верная, да, |Файлы в этом топике уже есть. Нашёл релевантное:

1. Таблица Google Sheets
 Ссылки:
https://drive.google.com/file/d/1mH5JCJ8iv-JHbG9PiLM1R0upHWzZ3ydX/view?usp=d|2026-05-03 08:51:32
- 9c69da3c-c3c8-47ea-b2d2-5d9670fc320c|500|search|DONE|Найди  кабель ВВГнг-LS 3×2.5 в СПб, бухта или метр, минимум 4 разных магазина, дай ссылки  и сравнение цен|Файлы в этом топике уже есть. Нашёл релевантное:

1. Файл
 Ссылки:
 - https://stal-avto96.ru/metallocherepitsa/metallocherepitsa-kredo-05-ral-6005-zelenyy-moh/
|2026-05-03 06:18:47
- c0eec3cf-7146-4c65-84a6-eff47c904cac|2|text|DONE|Да сделай|Активный контекст найден
Задача: c0eec3cf-7146-4c65-84a6-eff47c904cac
Статус: NEW
Кратко: Да сделай|2026-05-03 06:18:09
- a526edb7-68c5-41cb-971e-7cc868a4f893|2|text|FAILED|Сделай предварительную смету коробки дома 10×12 м, 2 этажа, газобетон, монолитная плита, кровля двускатная. Объект 120 к|Проектный файл не создан
Причина: DOCX_CREATE_FAILED: 'str' object has no attribute 'get'
Уточни исходные данные или пришли образец проекта|2026-05-03 06:17:57
- 60e8c22a-3a9c-4498-be7e-1dc25476130f|500|text|DONE|[VOICE] Ну что ты, нашел мне кабель, который я у тебя спрашивал или нет?|Да. Вот результат по исходной задаче

Этот чат — ВЕБ ПОИСК. Направление: интернет-поиск товаров и информации.|2026-05-03 06:16:52
- a45866a1-2810-4578-b9d3-dd6234efa8ff|210|text|FAILED|Мне нужно проект плиты монолитной 18-24 под ангар|Проектный файл создан
Раздел: АР
https://docs.google.com/document/d/1cIajKAZAwcugRWoZb74mb9CePUeFFc-1/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd|2026-05-03 06:46:51
- 4cf9e6e5-047a-446c-b225-e9db15ea2ab6|500|text|FAILED|Найди|None|2026-05-03 06:16:43
- 34e1c697-31a9-4754-a7fd-69b3d83dd7fb|500|text|DONE|Для чего этот чат?|Этот чат — ВЕБ ПОИСК. Направление: интернет-поиск товаров и информации.|2026-05-03 06:06:08
- 9251e774-dd91-47ba-a0c0-0fe8224e6e70|500|search|DONE|Найди цену кабеля ВВГнг-LS 3×2.5 в СПб, бухта или метр, минимум 4 разных магазина, дай ссылки  и сравнение цен|Файлы в этом топике уже есть. Нашёл релевантное:

1. Файл
 Ссылки:
 - https://stal-avto96.ru/metallocherepitsa/metallocherepitsa-kredo-05-ral-6005-zelenyy-moh/
|2026-05-03 06:05:42
- 2e52dbd1-1d4b-4f55-b066-51b63024df0f|210|text|DONE|Какие образцы есть по АР, КЖ и КД? Покажи список по разделам, файл не создавай|Проектный файл создан
Раздел: АР
https://docs.google.com/document/d/18CJ-VD-y_8hD5UhK0KeN77tMpNYrLLfq/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd|2026-05-03 06:04:31
- 79c43ee2-1bcf-487b-9ac3-27ec0c4a747e|2|text|DONE|[VOICE] Я же тебе сказал, вариант 2.|Файлы в этом топике уже есть. Нашёл релевантное:

1. У1-02-26-Р-КЖ1.6.pdf
 Можно использовать как образец проектирования

2. 2026-04-27T19:10 [FAILED]: У1-02-26|2026-05-02 21:02:24
- 306ac12b-8a4b-41f0-9d4b-de6842210989|2|text|DONE|[VOICE] Я тебе задал вопрос, ты уточнил, я тебе ответил. Дальше что?|Уточнение к приёму смет принято
Следующие файлы в этом топике остаются образцами сметы
Цены не подставляю без отдельного подтверждения
Финальную смету не создаю|2026-05-02 21:02:03
- 540f1575-9d37-404c-b3bf-b73f9d4d2d30|2|text|FAILED|[VOICE] Ну так и что по итогу с моим вопросом?|None|2026-05-02 21:01:49
- 8c2bbfd5-d270-440a-8780-389ded2b6e68|210|text|DONE|нет я не это спросил|Уточнение к приёму смет принято
Следующие файлы в этом топике остаются образцами сметы
Цены не подставляю без отдельного подтверждения
Финальную смету не создаю|2026-05-02 20:45:34
- 230335dc-7d77-4818-b064-be9cb867d966|210|text|DONE|Какие проектные образцы у тебя есть? Покажи по разделам АР, КЖ, КД|Проектный файл создан
Раздел: АР
https://docs.google.com/document/d/1W7o5DHznaqoIP0Zb8pc7ri7eGTz-Wx78/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd|2026-05-02 20:44:58

## LATEST_FAILED_10
- a526edb7-68c5-41cb-971e-7cc868a4f893|2|Сделай предварительную смету коробки дома 10×12 м, 2 этажа, газобетон, монолитная плита, кровля двускатная. Объект 120 к|INVALID_RESULT_GATE|2026-05-03 06:17:57
- a45866a1-2810-4578-b9d3-dd6234efa8ff|210|Мне нужно проект плиты монолитной 18-24 под ангар|CONFIRMATION_TIMEOUT|2026-05-03 06:46:51
- 4cf9e6e5-047a-446c-b225-e9db15ea2ab6|500|Найди|STALE_TIMEOUT|2026-05-03 06:16:43
- 540f1575-9d37-404c-b3bf-b73f9d4d2d30|2|[VOICE] Ну так и что по итогу с моим вопросом?|INVALID_RESULT_GATE|2026-05-02 21:01:49
- 2af172a3-2251-4787-b2af-5eb11d2bee2c|2|Посчитай смету дома из газобетона 100 м² в 50 км от Питера|INVALID_RESULT_GATE|2026-05-02 20:41:13
- 70258b1e-8326-45b6-a018-7500f865a7e7|2|[VOICE] Посмотри мои предыдущие вопросы, наш диалог, посмотри, вот несколько сообщений назад|INVALID_RESULT_GATE|2026-05-02 13:51:18
- 1a8a5e9f-3321-4177-8bbb-c80d71a47abf|2|[VOICE] Ну а теперь ты точно понимаешь, как делать?|INVALID_RESULT_GATE|2026-05-02 13:50:44
- 1a6cb0a5-f241-4847-932d-563261f18b21|2|[VOICE] При составлении СМЕД ты обязан уточнять еще местоположение объекта, чтобы рассчитывать логистику.|INVALID_RESULT_GATE|2026-05-02 13:42:43
- b9368fcb-48c2-4097-a5b4-948541322642|2|[VOICE] А логика построения ответов, то есть формулы, все понятно тебе полностью?|INVALID_RESULT_GATE|2026-05-02 13:41:07
- d3f1d1ea-2bb8-4251-af63-800645975b2c|210|[VOICE] Ты взял это в работу или нет? Я не понял.|INVALID_RESULT_GATE|2026-05-02 10:30:36

## LATEST_TASK_HISTORY_20
- ff510d77-cf55-48b7-8555-3e820bfeb819|reply_sent:file_tech_followup_v2|2026-05-03 08:51:32
- ff510d77-cf55-48b7-8555-3e820bfeb819|FILE_TECH_CONTOUR_FOLLOWUP_V2:DONE|2026-05-03 08:51:32
- ff510d77-cf55-48b7-8555-3e820bfeb819|created:NEW|2026-05-03T08:51:31.492242+00:00
- 9c69da3c-c3c8-47ea-b2d2-5d9670fc320c|reply_sent:file_tech_followup_v2|2026-05-03 06:18:47
- 9c69da3c-c3c8-47ea-b2d2-5d9670fc320c|FILE_TECH_CONTOUR_FOLLOWUP_V2:DONE|2026-05-03 06:18:47
- 9c69da3c-c3c8-47ea-b2d2-5d9670fc320c|created:NEW|2026-05-03T06:18:47.279744+00:00
- c0eec3cf-7146-4c65-84a6-eff47c904cac|ACTIVE_DIALOG_STATE_V1:SHORT_CONTROL_ACTIVE_TASK|2026-05-03 06:18:09
- c0eec3cf-7146-4c65-84a6-eff47c904cac|created:NEW|2026-05-03T06:18:08.977365+00:00
- a526edb7-68c5-41cb-971e-7cc868a4f893|reply_sent:invalid_result|2026-05-03 06:17:57
- a526edb7-68c5-41cb-971e-7cc868a4f893|state:FAILED|2026-05-03 06:17:57
- a526edb7-68c5-41cb-971e-7cc868a4f893|result:Для создания предварительной сметы коробки дома 10×12 м, 2 этажа, газобетон, монолитная плита, кровля двускатная, объект 120 км от СПб, использую шаблон **М-80.xlsx** как эт|2026-05-03 06:17:42
- a526edb7-68c5-41cb-971e-7cc868a4f893|reply_sent:result|2026-05-03 06:17:24
- a526edb7-68c5-41cb-971e-7cc868a4f893|result:### Предварительная смета коробки дома 10×12 м, 2 этажа, газобетон, монолитная плита, кровля двускатная. Объект 120 км от СПб.

#### Основные параметры:
- **Площадь дома**: |2026-05-03 06:17:24
- a526edb7-68c5-41cb-971e-7cc868a4f893|PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:PROJECT_NEEDS_CONTEXT|2026-05-03 06:16:53
- a526edb7-68c5-41cb-971e-7cc868a4f893|reply_sent:project_route_guard|2026-05-03 06:16:53
- 60e8c22a-3a9c-4498-be7e-1dc25476130f|REPLY_REPEAT_PARENT_TASK_V1:ACK:34e1c697|2026-05-03 06:16:52
- 60e8c22a-3a9c-4498-be7e-1dc25476130f|reply_sent:reply_repeat_parent|2026-05-03 06:16:52
- a45866a1-2810-4578-b9d3-dd6234efa8ff|PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1:PROJECT_CREATED|2026-05-03 06:16:50
- a45866a1-2810-4578-b9d3-dd6234efa8ff|reply_sent:project_route_guard|2026-05-03 06:16:50
- 4cf9e6e5-047a-446c-b225-e9db15ea2ab6|reply_sent:stale_failed|2026-05-03 06:16:44

## MEMORY_DB_COUNT
- 5540

## LATEST_MEMORY_20
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-05-03T09:17:21.945333+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-05-03T09:17:21.946700+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 12, "updated_at": "2026-05-03T09:17:21.907940+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-05-03T09:17:21.908251+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-05-03T09:17:21.893176+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-05-03T09:17:21.893676+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-03T09:17:21.849080+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-05-03T09:17:21.848983+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-03T09:17:21.848766+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-03T09:17:21.848664+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-03T09:17:21.848568+00:00
- topic_2_file_234e52f8-3ce8-4f2f-99c3-7cc22265a151|{"task_id": "234e52f8-3ce8-4f2f-99c3-7cc22265a151", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-03T09:17:21.848446+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-05-03T09:17:21.848321+00:00
- topic_2_file_acecae89-87a8-42da-881a-db41cd0134e6|{"task_id": "acecae89-87a8-42da-881a-db41cd0134e6", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-03T09:17:21.848229+00:00
- topic_2_file_a4956f79-592e-45e3-8f17-925366b5eb2f|{"task_id": "a4956f79-592e-45e3-8f17-925366b5eb2f", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-03T09:17:21.847819+00:00
- topic_2_file_999e36c2-c98b-48e8-a7d0-140e7ef382a9|{"task_id": "999e36c2-c98b-48e8-a7d0-140e7ef382a9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-03T09:17:21.847547+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-03T09:17:21.847078+00:00
- topic_2_file_3d35681d-2c3a-4320-9ff5-c3ddef6bd632|{"task_id": "3d35681d-2c3a-4320-9ff5-c3ddef6bd632", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-03T09:17:21.846847+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-03T09:17:21.846662+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-03T09:17:21.846384+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-03T09:17:21.846250+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-03T09:17:21.845867+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-05-03T09:17:21.845482+00:00

## JOURNAL_AREAL_TASK_WORKER_60
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:623: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
/root/.areal-neva-core/task_worker.py:600: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:600: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  _ts = datetime.datetime.utcnow().isoformat()
/root/.areal-neva-core/task_worker.py:623: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 1min 18.229s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 3.920s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 5.382s CPU time, 58.9M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 3min 13.515s CPU time, 58.9M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 4.565s CPU time.
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:657: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 30.862s CPU time, 85.6M memory peak, 0B memory swap peak.
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
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 4min 45.634s CPU time, 103.7M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
/root/.areal-neva-core/task_worker.py:664: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  "timestamp": datetime.datetime.utcnow().isoformat(),

## JOURNAL_TELEGRAM_INGRESS_30
2026-05-03 09:06:22,821 INFO DAEMON: Task 4cf9e6e5-047a-446c-b225-e9db15ea2ab6 created state=NEW topic_id=500
2026-05-03 09:06:22,821 INFO DAEMON: Update id=262221541 is handled. Duration 12 ms by bot id=8216054898
2026-05-03 09:06:35,836 INFO DAEMON: Update id=262221542 is handled. Duration 129 ms by bot id=8216054898
2026-05-03 09:06:57,666 INFO DAEMON: Update id=262221543 is handled. Duration 79 ms by bot id=8216054898
2026-05-03 09:08:38,596 INFO DAEMON: Task a45866a1-2810-4578-b9d3-dd6234efa8ff created state=NEW topic_id=210
2026-05-03 09:08:38,596 INFO DAEMON: Update id=262221544 is handled. Duration 11 ms by bot id=8216054898
2026-05-03 09:09:12,313 INFO DAEMON: Update id=262221545 is handled. Duration 178 ms by bot id=8216054898
2026-05-03 09:09:25,952 INFO DAEMON: Update id=262221546 is handled. Duration 78 ms by bot id=8216054898
2026-05-03 09:09:32,635 INFO DAEMON: Update id=262221547 is handled. Duration 70 ms by bot id=8216054898
2026-05-03 09:10:20,414 INFO DAEMON: STT env check groq=True openai=True
2026-05-03 09:10:20,415 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_9066.ogg size=20186 model=whisper-large-v3-turbo
2026-05-03 09:10:20,754 INFO DAEMON: STT http_status=200
2026-05-03 09:10:20,754 INFO DAEMON: STT ok transcript_len=64
2026-05-03 09:10:20,818 INFO DAEMON: Task 60e8c22a-3a9c-4498-be7e-1dc25476130f created state=NEW topic_id=500
2026-05-03 09:10:20,818 INFO DAEMON: Update id=262221548 is handled. Duration 623 ms by bot id=8216054898
2026-05-03 09:10:56,087 INFO DAEMON: Update id=262221549 is handled. Duration 79 ms by bot id=8216054898
2026-05-03 09:11:05,291 INFO DAEMON: Update id=262221550 is handled. Duration 104 ms by bot id=8216054898
2026-05-03 09:15:39,838 INFO DAEMON: Task a526edb7-68c5-41cb-971e-7cc868a4f893 created state=NEW topic_id=2
2026-05-03 09:15:39,838 INFO DAEMON: Update id=262221551 is handled. Duration 10 ms by bot id=8216054898
2026-05-03 09:18:08,979 INFO DAEMON: Task c0eec3cf-7146-4c65-84a6-eff47c904cac created state=NEW topic_id=2
2026-05-03 09:18:08,980 INFO DAEMON: Update id=262221552 is handled. Duration 11 ms by bot id=8216054898
2026-05-03 09:18:47,283 INFO DAEMON: Task 9c69da3c-c3c8-47ea-b2d2-5d9670fc320c created state=NEW topic_id=500
2026-05-03 09:18:47,283 INFO DAEMON: Update id=262221553 is handled. Duration 9 ms by bot id=8216054898
2026-05-03 11:51:31,059 INFO DAEMON: STT env check groq=True openai=True
2026-05-03 11:51:31,059 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_9082.ogg size=36671 model=whisper-large-v3-turbo
2026-05-03 11:51:31,339 INFO DAEMON: STT http_status=200
2026-05-03 11:51:31,340 INFO DAEMON: STT ok transcript_len=125
2026-05-03 11:51:31,499 INFO DAEMON: Task ff510d77-cf55-48b7-8555-3e820bfeb819 created state=NEW topic_id=2
2026-05-03 11:51:31,499 INFO DAEMON: Update id=262221554 is handled. Duration 2557 ms by bot id=8216054898
2026-05-03 11:52:28,801 INFO DAEMON: Update id=262221555 is handled. Duration 4 ms by bot id=8216054898
