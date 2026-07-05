# SINGLE_MODEL_CURRENT_CONTEXT

GENERATED_AT: 2026-07-05T22:22:27.440816+00:00
GIT_SHA: dc8998f1d941a94cee3bd2cddc1d082462d7475b
PURPOSE: Быстрый старт для любой модели — только актуальное состояние
FULL_AUDIT: docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md
STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test

## READ_ORDER
1. This SINGLE_MODEL_CURRENT_CONTEXT
2. SINGLE_MODEL_SOURCE
3. Topic/direction file if needed
4. SINGLE_MODEL_FULL_CONTEXT only for audit/dispute
5. ORCHESTRA_FULL_CONTEXT_PART_*.md only for raw dump

## GLOBAL_STATUS
| topic | name | status | active | failed_24h |
|-------|------|--------|--------|------------|
| 2 | STROYKA | INSTALLED_NOT_VERIFIED | 0 | 6 |
| 5 | TEKHNADZOR | UNKNOWN | 0 | 0 |
| 210 | PROEKTIROVANIE | UNKNOWN | 0 | 0 |
| 500 | VEB_POISK | UNKNOWN | 0 | 0 |

## OPEN_BLOCKERS_FROM_NOT_CLOSED
### ЧТО INSTALLED НО НЕ VERIFIED (факт из NOT_CLOSED)
DATE_UNKNOWN
⚠️ PATCH_DOWNLOAD_OAUTH_V1 — task_worker.py
⚠️ PATCH_SOURCE_GUARD_V1 — task_worker.py
⚠️ PATCH_FILE_ERROR_RETRY_V1 — task_worker.py
⚠️ PATCH_DRIVE_BOTMSG_SAVE_V1 — task_worker.py
⚠️ PATCH_DRIVE_DOWNLOAD_FAIL_MSG_V1 — task_worker.py
⚠️ PATCH_CRASH_BOTMSG_V1 — task_worker.py

### P1 — ОСТАЁТСЯ (следующий проход FULLFIX_02):
DATE_UNKNOWN
- Голосовой confirm при AWAITING_CONFIRMATION (telegram_daemon.py ~601)
- project_type определение неточное (КД → АР) — улучшить regex
- Состав листов не извлекается если марки не в тексте PDF
- Estimate PDF → Excel → Drive end-to-end
- КЖ PDF pipeline
- Live-тесты: DUPLICATE_GUARD, MULTI_FILE, LINK_INTAKE, FILE_ERROR_RETRY

### NOT CLOSED (код есть, live-тест не проводился)
DATE_UNKNOWN
- Смета PDF → Excel → Drive end-to-end
- КЖ PDF pipeline end-to-end
- project_engine end-to-end через Telegram
- Голосовой confirm при AWAITING_CONFIRMATION
- Дублирование задач x2
- PATCH_FILE_ERROR_RETRY_V1, PATCH_CRASH_BOTMSG_V1

### Pending live-тесты (код есть, Telegram не тестировался):
DATE_UNKNOWN
- template_intake: файл + "возьми как образец"
- defect_act: фото + "акт осмотра"
- multifile: "сводка по всем файлам"
- active_context_query: "ну что там / где смета"
- DWG pipeline end-to-end
- КЖ PDF pipeline end-to-end

### ОСТАЁТСЯ НЕ ЗАКРЫТЫМ:
DATE_UNKNOWN
- ПРОХОД 3: Voice confirm при AWAITING_CONFIRMATION
- ПРОХОД 5: Estimate PDF→Excel→Drive (live-тест)
- ПРОХОД 6: Technadzor фото→акт (live-тест)
- ПРОХОД 7: Project engine end-to-end
- detect_intent() takes 1 arg — warning в FILE_INTAKE_ROUTER_V1
- AWAITING_CONFIRMATION: 19 задач — проверить не зависли ли

## ACTIVE_OR_RECENT_TOPICS
### topic_2 STROYKA
role: Сметы
active: 0
failed_24h: 6
commits_last_7d: 2
recent_commits:
- 844fafb|topic2: close PDF estimate confirmation flow
- c8a9f1c|Topic2 canonical estimate live repair
markers_missing: 2
- TOPIC2_TEMPLATE_SELECTED
- TOPIC2_LOGISTICS_CONFIRMED
last_failed:
- bd0d5ae1 | STALE_TIMEOUT
- 9c5946d7 | STALE_TIMEOUT
- ea794751 | NO_VALID_ARTIFACT
blockers:
- - topic_2 не тянет проектные образцы topic_210
- - topic_210 не тянет сметные артефакты как результат
- - WRONG_FILES_SHOWN_IN_TOPIC_2
NEXT_ACTION: live-test / close missing markers: 2

### topic_5 TEKHNADZOR
role: Технадзор
active: 0
failed_24h: 0
commits_last_7d: 0
last_failed:
- 775a2251 | STALE_NEW_30MIN
- f3637754 | STALE_NEW_30MIN
- ddfc12b1 | PATCH_TOPIC2_UNBLOCK_PICK_NEXT_V1_CLOSED_BLOCKER
blockers:
- - topic_5 не тянет КЖ/АР без прямой команды
NEXT_ACTION: investigate latest failed: STALE_NEW_30MIN

### topic_210 PROEKTIROVANIE
role: КЖ КМ
active: 0
failed_24h: 0
commits_last_7d: 0
last_failed:
- 4cd74051 | INVALID_RESULT_GATE
- 088df3dc | TASK_WORKER_ARTIFACT_GATE_V1:EMPTY_OR_TOO_SHORT
- dd000985 | TASK_WORKER_ARTIFACT_GATE_V1:EMPTY_OR_TOO_SHORT
blockers:
- - topic_2 не тянет проектные образцы topic_210
- - topic_210 не тянет сметные артефакты как результат
- - проверить topic_210: "какие образцы есть по АР/КЖ/КД" должен показать список без создания файла
NEXT_ACTION: investigate latest failed: INVALID_RESULT_GATE

### topic_500 VEB_POISK
role: Интернет-поиск
active: 0
failed_24h: 0
commits_last_7d: 0
last_failed:
- 6719452a | P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
- 16129a0c | P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
- 58591d8f | IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1
NEXT_ACTION: investigate latest failed: P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT

## STRICT_RULES
- INSTALLED != VERIFIED
- VERIFIED только после live-test
- Diagnostics → BAK → PATCH → PY_COMPILE → RESTART → LOGS → DB_VERIFY → GIT_PUSH → FINAL_VERIFY
- Не объявлять закрытым без live-теста
- BROKEN / REJECTED / UNKNOWN не использовать как канон
- chat_id + topic_id обязательны для контекста
- FULL_CONTEXT использовать только для аудита или спора

## ALLOWED_FILES_BY_SCOPE
- core/stroyka_estimate_canon.py — topic_2 estimates
- core/sample_template_engine.py — topic_2 estimates/templates
- core/topic2_estimate_final_close_v2.py — topic_2 legacy/fallback
- core/technadzor_engine.py — topic_5
- core/normative_engine.py — topic_5
- core/project_engine.py — topic_210
- core/search_session.py — topic_500
- tools/full_context_aggregator.py — aggregator

## FORBIDDEN_FILES
- .env / credentials / sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- telegram_daemon.py
- data/core.db / data/memory.db schema
- systemd unit files

## CONDITIONAL_PATCH
- task_worker.py — only with explicit task scope and diagnostics-first

## DRIVE_BINDING
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## REFERENCE_REGISTRIES
estimate_template_registry: loaded=True count=5
owner_reference_registry: loaded=True items=11

## SOURCE_LINKS
- CURRENT_CONTEXT: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md
- SINGLE_MODEL_SOURCE: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/SINGLE_MODEL_SOURCE.md
- FULL_CONTEXT_AUDIT: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md
- TOPIC_STATUS_INDEX: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md
- DIRECTION_STATUS_INDEX: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md
- LATEST_HANDOFF: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/HANDOFFS/LATEST_HANDOFF.md
- NOT_CLOSED_FULL: https://raw.githubusercontent.com/rj7hmz9cvm-lgtm/areal-neva-core/main/docs/REPORTS/NOT_CLOSED.md

