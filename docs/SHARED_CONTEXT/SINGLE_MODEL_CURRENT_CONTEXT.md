# SINGLE_MODEL_CURRENT_CONTEXT

GENERATED_AT: 2026-05-08T20:10:02.630337+00:00
GIT_SHA: 531398c8bf6e37ce42979d3ad69fc7bafe2a76cf
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
| 2 | STROYKA | INSTALLED_NOT_VERIFIED | 1 | 6 |
| 5 | TEKHNADZOR | IDLE_NO_FAILURES_NOT_VERIFIED | 0 | 0 |
| 210 | PROEKTIROVANIE | IDLE_NO_FAILURES_NOT_VERIFIED | 0 | 0 |
| 500 | VEB_POISK | IDLE_NO_FAILURES_NOT_VERIFIED | 0 | 0 |

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
active: 1
failed_24h: 6
commits_last_7d: 30
recent_commits:
- 3421216|fix(topic2): gate send fix (dict(task) for sqlite3.Row) + WCG delivery guard on picker cycle
- 80b0809|fix(topic2): PATCH_TOPIC2_INPUT_GATE_SOURCE_OF_TRUTH_V1 — current file source-of-truth gate blocks stale house context for drainage 
- 075edf9|fix(topic2): PATCH_TOPIC2_STALE_PENDING_TASK_GUARD_V1 + LOCAL_BOT_API_404_FIX
markers_missing: 6
- TOPIC2_ESTIMATE_SESSION_CREATED
- TOPIC2_CONTEXT_READY
- TOPIC2_LOGISTICS_CONFIRMED
- TOPIC2_XLSX_CREATED
- TOPIC2_MESSAGE_THREAD_ID_OK
- TOPIC2_DONE_CONTRACT_OK
last_failed:
- e425b052 | STALE_TIMEOUT
- acdae011 | STALE_TIMEOUT
- test-gat | STALE_TIMEOUT
blockers:
- - topic_2 не тянет проектные образцы topic_210
- - topic_210 не тянет сметные артефакты как результат
- - WRONG_FILES_SHOWN_IN_TOPIC_2
NEXT_ACTION: live-test / close missing markers: 6

### topic_5 TEKHNADZOR
role: Технадзор
active: 0
failed_24h: 0
commits_last_7d: 30
recent_commits:
- 7c646dd|session(08.05): bigfile activated, topic5 V3 dispatcher, topic2 P6C intercept, c94ec497 FAILED/NOT_PROVEN
- b3e5be7|fix(topic500): relax bad-result filter for adaptive output modes
- 0d6a9a4|fix(memory): ARCHIVE_DUPLICATE_GUARD_V1 + topic500 search pollution guard
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
commits_last_7d: 4
recent_commits:
- 9420d6a|fix(topic2): stroyka meta-confirm guard + reply chain + xlsx 15 cols + topic210 meta guard
- a277900|docs(normative): add shared normative context for topic_5 and topic_210
- bc58444|COMBINED_TOPIC2_AND_TOPIC210_CLOSE_V1: real topic2 estimate and cad section fix
last_failed:
- cfadbd05 | INVALID_RESULT_GATE
- b71a685b | INVALID_RESULT_GATE
- 6e34406d | NO_VALID_ARTIFACT
blockers:
- - topic_2 не тянет проектные образцы topic_210
- - topic_210 не тянет сметные артефакты как результат
- - проверить topic_210: "какие образцы есть по АР/КЖ/КД" должен показать список без создания файла
NEXT_ACTION: investigate latest failed: INVALID_RESULT_GATE

### topic_500 VEB_POISK
role: Интернет-поиск
active: 0
failed_24h: 0
commits_last_7d: 14
recent_commits:
- b3e5be7|fix(topic500): relax bad-result filter for adaptive output modes
- 0d6a9a4|fix(memory): ARCHIVE_DUPLICATE_GUARD_V1 + topic500 search pollution guard
- 3f53d3f|docs(handoff): update after topic500 adaptive output V1
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

