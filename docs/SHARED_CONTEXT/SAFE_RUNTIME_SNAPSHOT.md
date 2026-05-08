# SAFE_RUNTIME_SNAPSHOT
generated_at_utc: 2026-05-08T07:20:02.364331+00:00
git_sha_before_commit: 3dcb94adb675639f423ecd26617e6c1c2d10ba23
git_branch: main

## SERVICES
- areal-task-worker: active
- telegram-ingress: active
- areal-memory-api: active
- areal-claude-bootstrap-aggregator.timer: inactive

## GIT_LOG_30
3dcb94a FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
8760011 fix(topic2): enforce full canonical estimate pipeline without cross-topic regression
e08536b FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
33ce4a6 3 patches: material parse fix, zero-qty filter, price honesty
bf3bb26 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
d7b743d handoff: update HEAD to 81f35b5, mark P1 clarified loop closed
81f35b5 PATCH_P6CF3_CLARIFIED_HISTORY_INCLUDE_V1: fix infinite clarification loop
e7b171e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
96bea6c docs: handoff 08.05 — file_intake_router not called from _handle_drive_file (P0 arch)
74b156c FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
b236f02 fix(topic2): session 08.05 — P6C fulltext prep, P3CHK append fix, P2 distance skip, WCPE unblock
e3a016c PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1: hard-enforce Sonar for all price/search calls
4cfd9b6 fix(topic2): close P6E67 loop storm + natural reply message
dc26486 fix(topic2): PATCH_PRICE_REJECT_STORM_FIX_V1 — remove noisy INSERT from V5/V6C rejected path
0c8518e fix(topic2): TOPIC2_FULL_CLOSE — work/material split, sheet fallback, drive links, xlsx 15-col gate
a216eeb fix(topic2): PATCH_FCG_V2PATH_BYPASS_V1 — extend FDCB bypass to TOPIC2_DONE_CONTRACT_OK
88761b3 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
b3e5be7 fix(topic500): relax bad-result filter for adaptive output modes
272a9bb FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
8c640a7 feat(aggregator): add current context quick start layer
e90165d feat(aggregator): add current context quick start layer
551829d FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
1b1078c docs(handoff): update after GAP-5 and GAP-6 memory fixes
0d6a9a4 fix(memory): ARCHIVE_DUPLICATE_GUARD_V1 + topic500 search pollution guard
ffca836 FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
3f53d3f docs(handoff): update after topic500 adaptive output V1
0c15037 feat(topic500): adaptive output by intent mode (9 modes, V1)
9841d5e FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context
48f9858 docs(handoff): update latest handoff after topic2 and aggregator guard
c0300fb fix(topic2): close 4 code gaps — enrichment markers, cyrillic marker, function-object bug, FCG bypass

## GIT_SHOW_STAT_HEAD
commit 3dcb94adb675639f423ecd26617e6c1c2d10ba23
Author: Ila <ilakuznecov@mac.local>
Date:   Fri May 8 10:15:08 2026 +0300

    FULL_CONTEXT_AGGREGATOR_V1: universal no-truncation model context

 docs/SHARED_CONTEXT/CLAUDE_BOOTSTRAP_CONTEXT.md    |  6 +-
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
 docs/SHARED_CONTEXT/MODEL_BOOTSTRAP_CONTEXT.md     |  6 +-
 docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md          |  6 +-
 docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT.md      |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_MANIFEST.json           | 20 +++---
 .../ORCHESTRA_FULL_CONTEXT_PART_001.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_002.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_003.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_004.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_005.md             | 49 +++++++-------
 .../ORCHESTRA_FULL_CONTEXT_PART_006.md             | 52 +++++++++++----
 .../ORCHESTRA_FULL_CONTEXT_PART_007.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_008.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_009.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_010.md             | 74 ++++++++++++++++++++--
 .../ORCHESTRA_FULL_CONTEXT_PART_011.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_012.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_013.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_014.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_015.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_016.md             |  4 +-
 .../ORCHESTRA_FULL_CONTEXT_PART_017.md             |  4 +-
 docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md       | 64 +++++++++++--------
 .../SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md |  6 +-
 docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md   | 50 +++++++--------
 docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md         |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_0_COMMON.md       |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_11_VIDEO.md       |  4 +-
 .../TOPICS/topic_210_PROEKTIROVANIE.md             |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_2_STROYKA.md      |  6 +-
 .../TOPICS/topic_3008_KODY_MOZGOV.md               |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_4569_CRM_LEADS.md |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_500_VEB_POISK.md  |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_5_TEKHNADZOR.md   |  4 +-
 .../SHARED_CONTEXT/TOPICS/topic_6104_JOB_SEARCH.md |  4 +-
 docs/SHARED_CONTEXT/TOPICS/topic_794_DEVOPS.md     |  4 +-
 .../TOPICS/topic_961_AVTOZAPCHASTI.md              |  4 +-
 docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md          |  4 +-
 68 files changed, 329 insertions(+), 236 deletions(-)

## GIT_CHANGED_FILES_10
core/sample_template_engine.py
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
- FAILED|2961
- CANCELLED|819
- DONE|573
- ARCHIVED|381
- WAITING_CLARIFICATION|1

## CORE_DB_OPEN_TASKS
- 1

## LATEST_TASKS_15
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|2|text|WAITING_CLARIFICATION|[VOICE] Что не так, скажи?|Пришли задание заново — расскажи что нужно сделать.|2026-05-08 07:20:01
- 524f5853-4243-4833-ae82-116da9202179|2|text|CANCELLED|[VOICE] Так а ты посмотри то, что я тебе писал, еще раз тебе говорю, посмотри последнее задание.|P6E67_MERGED_TO_PARENT_TASK 57c2617a-7975-4282-bffb-2b18577d8b9d|2026-05-08 06:18:34
- 4df9cf88-0843-478b-bef1-9d828d505298|2|text|DONE|[VOICE] Блять, я тебе еще раз говорю Посмотри все то, что мы с тобой писали По этому проекту У тебя же есть вся полность|Нового полного ТЗ для сметы в сообщении нет. Старую смету из памяти не поднимаю|2026-05-08 06:18:17
- 57c2617a-7975-4282-bffb-2b18577d8b9d|2|text|CANCELLED|[VOICE] посмотри проект все увидишь у тебя же есть проект зайди да глянь там же есть вся информация если тебе не хватает|P6E67_MERGED_TO_PARENT_TASK d72028da-b4ff-424d-a626-790c9da8be77|2026-05-08 06:18:36
- 0aaa723d-e506-4cfe-9cfc-7dc20b7ea094|2|text|CANCELLED|[VOICE] Я тебе в предыдущем сообщении уже все выбирал, все давал. Что тебе еще непонятно? Два. Средние цены, средние. Дв|P6E67_MERGED_TO_PARENT_TASK d72028da-b4ff-424d-a626-790c9da8be77|2026-05-08 05:07:19
- 89f1a927-af21-4d77-b287-70e8ecef659c|2|text|CANCELLED|[VOICE] Вот задание, соответственно, если что-то непонятно, мне нужна полностью смета с материалами посчитанная. Соответ|P6E67_MERGED_TO_PARENT_TASK d72028da-b4ff-424d-a626-790c9da8be77|2026-05-08 04:32:16
- d72028da-b4ff-424d-a626-790c9da8be77|2|drive_file|DONE|{"file_id": "1-isQhm067W2LDv2Bgm5ewbfyVm2B8QhV", "file_name": "8х12.pdf", "mime_type": "application/pdf", "caption": "На|✅ Предварительная смета готова

Объект: барнхаус 8.0x12.0 м
Этажей: 1
Площадь застройки: 96.0 м²
Расчётная площадь: 96.0 м²
Фундамент: монолитная плита
Стены: г|2026-05-08 06:54:21
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
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION|2026-05-08 07:20:01
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND|2026-05-08 07:20:01
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION|2026-05-08 07:19:59
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND|2026-05-08 07:19:59
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION|2026-05-08 07:19:58
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND|2026-05-08 07:19:58
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION|2026-05-08 07:19:56
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND|2026-05-08 07:19:56
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION|2026-05-08 07:19:55
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND|2026-05-08 07:19:54
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|clarified:|2026-05-08T07:19:54.650438+00:00
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION|2026-05-08 07:19:53
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND|2026-05-08 07:19:53
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION|2026-05-08 07:19:51
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND|2026-05-08 07:19:51
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION|2026-05-08 07:19:50
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND|2026-05-08 07:19:50
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION|2026-05-08 07:19:48
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND|2026-05-08 07:19:48
- 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9|P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION|2026-05-08 07:19:47

## MEMORY_DB_COUNT
- 5185

## LATEST_MEMORY_20
- topic_500_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 500, "count": 27, "updated_at": "2026-05-08T06:51:36.008370+00:00", "files": [{"task_id": "7b609434-8167-43f5-a52a-beb85e0b4ed5", "file_id|2026-05-08T06:51:36.009345+00:00
- topic_210_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 210, "count": 50, "updated_at": "2026-05-08T06:51:35.989904+00:00", "files": [{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "file_id|2026-05-08T06:51:35.990391+00:00
- topic_5_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 5, "count": 50, "updated_at": "2026-05-08T06:51:35.944124+00:00", "files": [{"task_id": "4b402275-e99b-4d9f-b331-08f2ba2a93be", "file_id":|2026-05-08T06:51:35.944485+00:00
- topic_2_file_catalog_autosync|{"chat_id": "-1003725299009", "topic_id": 2, "count": 50, "updated_at": "2026-05-08T06:51:35.918069+00:00", "files": [{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "file_id":|2026-05-08T06:51:35.918528+00:00
- topic_2_file_c925a897-66ec-435e-8312-15687f4df6d4|{"task_id": "c925a897-66ec-435e-8312-15687f4df6d4", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T06:51:35.861425+00:00
- topic_5_file_4b442bb4-e731-4b17-a359-888e88084ef2|{"task_id": "4b442bb4-e731-4b17-a359-888e88084ef2", "chat_id": "-1003725299009", "topic_id": 5, "input_type": "text", "state": "FAILED", "file_id": "", "file_name": "", "mime_type"|2026-05-08T06:51:35.861336+00:00
- topic_2_file_987c3852-1e34-445f-b80f-368e6042c1ef|{"task_id": "987c3852-1e34-445f-b80f-368e6042c1ef", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T06:51:35.861187+00:00
- topic_2_file_482d7590-50d4-44af-8d42-affd58e1e9d9|{"task_id": "482d7590-50d4-44af-8d42-affd58e1e9d9", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T06:51:35.860822+00:00
- topic_2_file_d68bc8e8-b2de-4cb3-84cf-308225d244de|{"task_id": "d68bc8e8-b2de-4cb3-84cf-308225d244de", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type": |2026-05-08T06:51:35.860653+00:00
- topic_2_file_6a9c665e-6307-4247-a170-fb2847b9633d|{"task_id": "6a9c665e-6307-4247-a170-fb2847b9633d", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "drive_file", "state": "FAILED", "file_id": "1bXXtuHRsXCuxBSRUl8Tj5z6E|2026-05-08T06:51:35.860570+00:00
- topic_2_file_92de809d-9274-48ee-82b4-584058ea4e48|{"task_id": "92de809d-9274-48ee-82b4-584058ea4e48", "chat_id": "-1003725299009", "topic_id": 2, "input_type": "search", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T06:51:35.860505+00:00
- topic_210_file_ce9421cb-5451-4cea-9823-a413b698bc94|{"task_id": "ce9421cb-5451-4cea-9823-a413b698bc94", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T06:51:35.860353+00:00
- topic_210_file_c8619b7e-9ebb-4731-973a-b3f6064bbe38|{"task_id": "c8619b7e-9ebb-4731-973a-b3f6064bbe38", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T06:51:35.860164+00:00
- topic_210_file_42320ab0-c49a-4a08-8f9b-5e38618a4e58|{"task_id": "42320ab0-c49a-4a08-8f9b-5e38618a4e58", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T06:51:35.860083+00:00
- topic_210_file_7dca3b5f-2782-400f-af84-fb030904e917|{"task_id": "7dca3b5f-2782-400f-af84-fb030904e917", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T06:51:35.859773+00:00
- topic_210_file_12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88|{"task_id": "12d77b1a-89c6-41c9-81c6-b6f5cbdc6a88", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "16V3s5DcAvnXj8f-3CcfZE2g5|2026-05-08T06:51:35.859479+00:00
- topic_210_file_b1f8e982-db2e-42de-9046-833287d3567d|{"task_id": "b1f8e982-db2e-42de-9046-833287d3567d", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T06:51:35.859415+00:00
- topic_210_file_eeb0d013-704a-404c-9390-5a06c90ee976|{"task_id": "eeb0d013-704a-404c-9390-5a06c90ee976", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T06:51:35.859236+00:00
- topic_210_file_5ead32f3-23d5-4872-9279-a42460ba5dd1|{"task_id": "5ead32f3-23d5-4872-9279-a42460ba5dd1", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "drive_file", "state": "DONE", "file_id": "1qy-mPcmRZxJIzEnY2Gp8B8J2|2026-05-08T06:51:35.859034+00:00
- topic_210_file_fb6aadc5-b372-488a-aede-f3433a030e55|{"task_id": "fb6aadc5-b372-488a-aede-f3433a030e55", "chat_id": "-1003725299009", "topic_id": 210, "input_type": "text", "state": "DONE", "file_id": "", "file_name": "", "mime_type"|2026-05-08T06:51:35.858934+00:00

## JOURNAL_AREAL_TASK_WORKER_60
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 13.693s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 1min 54.177s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 7.323s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 15.484s CPU time, 83.7M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 1min 7.353s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 27.441s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 11.890s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 9.692s CPU time, 84.2M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 21.834s CPU time, 122.2M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 2.218s CPU time.
Started areal-task-worker.service - Areal Task Worker.
Stopping areal-task-worker.service - Areal Task Worker...
areal-task-worker.service: Failed to kill control group /system.slice/areal-task-worker.service, ignoring: Invalid argument
areal-task-worker.service: Deactivated successfully.
Stopped areal-task-worker.service - Areal Task Worker.
areal-task-worker.service: Consumed 10.116s CPU time, 109.4M memory peak, 0B memory swap peak.
Started areal-task-worker.service - Areal Task Worker.

## JOURNAL_TELEGRAM_INGRESS_30
2026-05-08 09:13:14,266 INFO DAEMON: Update id=262221997 is handled. Duration 149 ms by bot id=8216054898
2026-05-08 09:17:40,132 INFO DAEMON: Update id=262221998 is handled. Duration 90 ms by bot id=8216054898
2026-05-08 09:17:55,715 INFO DAEMON: STT env check groq=True
2026-05-08 09:17:55,715 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10488.ogg size=40094 model=whisper-large-v3-turbo
2026-05-08 09:17:55,999 INFO DAEMON: STT http_status=200
2026-05-08 09:17:56,000 INFO DAEMON: STT ok transcript_len=164
2026-05-08 09:17:56,070 INFO DAEMON: Task 57c2617a-7975-4282-bffb-2b18577d8b9d created state=NEW topic_id=2
2026-05-08 09:17:56,070 INFO DAEMON: Update id=262221999 is handled. Duration 551 ms by bot id=8216054898
2026-05-08 09:18:15,870 INFO DAEMON: STT env check groq=True
2026-05-08 09:18:15,871 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10492.ogg size=39287 model=whisper-large-v3-turbo
2026-05-08 09:18:16,255 INFO DAEMON: STT http_status=200
2026-05-08 09:18:16,256 INFO DAEMON: STT ok transcript_len=161
2026-05-08 09:18:16,327 INFO DAEMON: Task 4df9cf88-0843-478b-bef1-9d828d505298 created state=NEW topic_id=2
2026-05-08 09:18:16,327 INFO DAEMON: Update id=262222000 is handled. Duration 689 ms by bot id=8216054898
2026-05-08 09:18:33,504 INFO DAEMON: STT env check groq=True
2026-05-08 09:18:33,504 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10495.ogg size=25835 model=whisper-large-v3-turbo
2026-05-08 09:18:33,868 INFO DAEMON: STT http_status=200
2026-05-08 09:18:33,870 INFO DAEMON: STT ok transcript_len=88
2026-05-08 09:18:33,943 INFO DAEMON: Task 524f5853-4243-4833-ae82-116da9202179 created state=NEW topic_id=2
2026-05-08 09:18:33,943 INFO DAEMON: Update id=262222001 is handled. Duration 642 ms by bot id=8216054898
2026-05-08 09:19:00,193 INFO DAEMON: Update id=262222002 is handled. Duration 176 ms by bot id=8216054898
2026-05-08 10:18:08,178 ERROR DAEMON: HANDLER_CRASH: Telegram server says - Bad Request: file is too big
2026-05-08 10:18:08,257 INFO DAEMON: Update id=262222003 is handled. Duration 181 ms by bot id=8216054898
2026-05-08 10:19:35,006 INFO DAEMON: STT env check groq=True
2026-05-08 10:19:35,006 INFO DAEMON: STT start file=/root/.areal-neva-core/runtime/voice_queue/voice_1003725299009_10506.ogg size=7450 model=whisper-large-v3-turbo
2026-05-08 10:19:35,340 INFO DAEMON: STT http_status=200
2026-05-08 10:19:35,340 INFO DAEMON: STT ok transcript_len=18
2026-05-08 10:19:35,421 INFO DAEMON: Task 089a9afa-ed1d-44ac-a68d-26d51f4bcdc9 created state=NEW topic_id=2
2026-05-08 10:19:35,421 INFO DAEMON: Update id=262222004 is handled. Duration 578 ms by bot id=8216054898
2026-05-08 10:19:55,083 INFO DAEMON: Update id=262222005 is handled. Duration 438 ms by bot id=8216054898
