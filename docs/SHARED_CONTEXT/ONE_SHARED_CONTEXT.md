# ONE_SHARED_CONTEXT
updated_at: 2026-04-29T11:00:22.367302+00:00

## SOURCE FILES
- chat_exports/CHAT_EXPORT_FULL_MAX__NEURON_SOFT_VPN_TECH_CHAT__2026-04-24.txt
- chat_exports/CHAT_EXPORT_SYSTEM_PROMPT__UNIVERSAL__2026-04-26.txt
- chat_exports/CHAT_EXPORT__-1003725299009__.txt
- chat_exports/CHAT_EXPORT__-1003725299009__2026-04-23.txt
- chat_exports/CHAT_EXPORT__-1003725299009__GPT-5.4__2026-04-23.txt
- chat_exports/CHAT_EXPORT__AI_Orchestra__2026-04-25.txt
- chat_exports/CHAT_EXPORT__AREAL-NEVA-ORCHESTRA-DEV__2026-04-26.txt
- chat_exports/CHAT_EXPORT__AREAL-NEVA-ORCHESTRA__2026-04-26.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_CORE__2026-04-27.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_ORCHESTRA_CANON_AND_TECH_CONTOUR__2026-04-27.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_ORCHESTRA_CANON_CLOSE__2026-04-28.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_ORCHESTRA_CLAUDE_ANALYSIS__2026-04-26.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_ORCHESTRA_CURRENT_CHAT__2026-04-25.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_ORCHESTRA_TECH_CONTOUR_CHAT__2026-04-24.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_ORCHESTRA_TECH_CONTOUR_CHAT__2026-04-27.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_ORCHESTRA_TECH_CONTOUR_FINAL__.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_ORCHESTRA_TECH_CONTOUR__.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_ORCHESTRA_TECH_CONTOUR__2026-04-24.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_ORCHESTRA__2026-04-26.txt
- chat_exports/CHAT_EXPORT__AREAL_NEVA_TECH_CLOSURE_27_04_2026__2026-04-27.txt
- chat_exports/CHAT_EXPORT__Areal_Neva_Core_Emergency_Fix__2026-04-25.txt
- chat_exports/CHAT_EXPORT__Areal_Neva_Core_Stabilization__2026-04-27.txt
- chat_exports/CHAT_EXPORT__Asimov_Laws_and_Bio__2026-04-27.txt
- chat_exports/CHAT_EXPORT__CLAUDE_SESSION__2026-04-27.txt
- chat_exports/CHAT_EXPORT__DOKAT_3__.txt
- chat_exports/CHAT_EXPORT__NEURON_SOFT_VPN_TECH_CHAT__2026-04-24.txt
- chat_exports/CHAT_EXPORT__NEURON_SOFT_VPN_TECH_CHAT__2026-04-24__DOKAT_4.txt
- chat_exports/CHAT_EXPORT__NEURON_SOFT_VPN_TECH_CHAT__2026-04-27.txt
- chat_exports/CHAT_EXPORT__ORCHESTRA__2026-04-23.txt
- chat_exports/CHAT_EXPORT__TECH_CONTOUR__GPT-5.5__2026-04-24.txt
- chat_exports/CHAT_EXPORT__TOPIC_3008__GPT-5.3__2026-04-23.txt
- chat_exports/CHAT_EXPORT__UNKNOWN_CHAT__.txt
- chat_exports/CHAT_EXPORT__UNKNOWN_CHAT__2026-04-20.txt
- chat_exports/CHAT_EXPORT__UNKNOWN__.txt
- chat_exports/CHAT_EXPORT__UNKNOWN__2026-04-25.txt
- chat_exports/CHAT_EXPORT__areal-neva-core-claude__2026-04-20.txt
- chat_exports/CHAT_EXPORT__areal-neva-core__2026-04-27.txt
- chat_exports/CHAT_EXPORT__areal_neva__2026-04-23.txt
- chat_exports/CHAT_EXPORT__claude_session_29_04_2026__2026-04-29.json
- chat_exports/CHAT_EXPORT__github_ssot_technical_orchestra__2026-04-29.json
- chat_exports/HANDOFF__CLAUDE_TO_NEXT_AI__2026-04-27.txt
- chat_exports/README.md
- chat_exports/ZAPROS_DLY_AI_AGENTOV_2026-04-27.txt
- docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK.md
- docs/ARCHITECTURE/SEARCH_MONOLITH_V1.md
- docs/CANON_FINAL/00_INDEX.md
- docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- docs/REPORTS/NOT_CLOSED.md

## CURRENT SYSTEM STATE
## СЕРВЕР
IP: 89.22.225.136 | Base: /root/.areal-neva-core
Services: areal-task-worker ACTIVE | telegram-ingress ACTIVE | areal-memory-api ACTIVE
DB: data/core.db (694 задачи) | memory.db (728KB)

## ПАТЧИ СЕССИИ 28-29.04.2026 (все SYNTAX_OK, active)

| Патч | Файл | Суть |
|---|---|---|
| FIX_VOICE_GUARD_20260428 | telegram_daemon.py:961 | substring→word-boundary |
| FIX_IS_SEARCH_20260428 | task_worker.py:2266 | SEARCH_PATTERNS→is_search |
| FIX_SEARCH_CONTEXT_20260428 | task_worker.py:2248 | fresh search без старого контекста |
| FIX_VOICE_REVISION_V2 | telegram_daemon.py:880+ | empty revision fix |
| FIX_VOICE_CONFIRM_IN_PROGRESS | telegram_daemon.py:560 | голос confirm в IN_PROGRESS |
| FIX_CRASHLOOP_3981 | task_worker.py:3981 | NameError p → p=__file__ |
| FIX_CP8_ERROR_CLOSE | task_worker.py | CP8 estimate ошибки → FAILED не повисают |
| FIX_CP8_SEARCH_TYPE | task_worker.py | input_type search → CP8 estimate hook |
| FIX_EMPTY_AI_RETRY | task_worker.py:2297 | retry 3x при chars=0 |
| FIX_DRIVE_OAUTH | task_worker.py:2569 | _download_from_drive_oauth через token.json |
| FIX_ENV_EXPORT | .env:16 | убран export перед GITHUB_TOKEN |

## LIVE ТЕСТ 29.04.2026
- Смета текстом: «Сделай смету: профлист 100 м², цена 450 руб/м²» → ответ получен ✅
- CP8 search type fix → смета теперь ловится из topic_500 ✅
- Drive OAuth → token.json вместо credentials.json ✅

## ACTIVE CANON
### docs/CANON_FINAL/00_INDEX.md
# CANON_FINAL INDEX
Версия: v1 | Дата: 28.04.2026
| Файл | Содержание |
|---|---|
| 01_SYSTEM_LOGIC_FULL.md | Общая логика системы |
| 02_FILE_PIPELINE_FULL.md | Pipeline файлов |
| 03_SEARCH_MONITORING_FULL.md | Поиск + мониторинг |
| 04_MEMORY_PIN_CONTEXT_FULL.md | Память, пины, контекст |
| 05_TASK_LIFECYCLE_INTENT_FULL.md | FSM задач + intent |
| 06_MULTI_MODEL_ORCHESTRA_FULL.md | Мультимодельный оркестр |
| 07_DOMAINS_FULL.md | Домены: стройка, запчасти |
| 08_PATCH_BACKUP_RULES_FULL.md | Правила патчей |
| 09_MODES_FULL.md | Режимы работы |
| 10_LIMITS_SLA_FULL.md | Лимиты и SLA |
| 11_DIAGNOSTICS_FULL.md | Диагностика |
### docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md
# AREAL-NEVA ORCHESTRA — ЕДИНЫЙ МОНОЛИТНЫЙ КАНОН
Версия: v13 + SESSION_28.04.2026 FINAL | Дата: 28.04.2026 | Режим: FACT-ONLY
## §0.0 СИСТЕМНАЯ ИДЕНТИЧНОСТЬ
Система НЕ бот. НЕ чат. НЕ генератор.
Система — это механизм: понимание → действие → результат → фиксация
Обязана: понимать смысл сообщения, ветку диалога, активную задачу, роль чата.
ЗАПРЕЩЕНО: отвечать вне контекста, терять ветку, смешивать темы, отвечать «в общем».
ОТВЕТ всегда: конкретный, по задаче, без сервисных фраз.
Если не хватает данных → один вопрос → сразу дальше работа.
## §0.1 БАЗОВЫЙ ИНВАРИАНТ (НЕИЗМЕНЯЕМЫЙ)
Любой вход               → task_id
Любой task_id            → финальный state
Любой финал              → Telegram-ответ
Любой file-result        → валидный артефакт, НЕ исходник
Любая memory write       → только после DONE
Нет «готово»             → без live verification
## §0. ПРАВИЛА ПОВЕДЕНИЯ AI
§0.2 Главный канон — пользователь. Все решения принимает только пользователь.

## VERIFIED FACTS
## ПАТЧИ СЕССИИ 28-29.04.2026 (все SYNTAX_OK, active)

| Патч | Файл | Суть |
|---|---|---|
| FIX_VOICE_GUARD_20260428 | telegram_daemon.py:961 | substring→word-boundary |
| FIX_IS_SEARCH_20260428 | task_worker.py:2266 | SEARCH_PATTERNS→is_search |
| FIX_SEARCH_CONTEXT_20260428 | task_worker.py:2248 | fresh search без старого контекста |
| FIX_VOICE_REVISION_V2 | telegram_daemon.py:880+ | empty revision fix |
| FIX_VOICE_CONFIRM_IN_PROGRESS | telegram_daemon.py:560 | голос confirm в IN_PROGRESS |
| FIX_CRASHLOOP_3981 | task_worker.py:3981 | NameError p → p=__file__ |
| FIX_CP8_ERROR_CLOSE | task_worker.py | CP8 estimate ошибки → FAILED не повисают |
| FIX_CP8_SEARCH_TYPE | task_worker.py | input_type search → CP8 estimate hook |
| FIX_EMPTY_AI_RETRY | task_worker.py:2297 | retry 3x при chars=0 |
| FIX_DRIVE_OAUTH | task_worker.py:2569 | _download_from_drive_oauth через token.json |
| FIX_ENV_EXPORT | .env:16 | убран export перед GITHUB_TOKEN |

## LIVE ТЕСТ 29.04.2026
- Смета текстом: «Сделай смету: профлист 100 м², цена 450 руб/м²» → ответ получен ✅
- CP8 search type fix → смета теперь ловится из topic_500 ✅
- Drive OAuth → token.json вместо credentials.json ✅
- Worker: active, NRestarts=0 ✅

## НЕ ЗАКРЫТО (тест завтра)
- Смета → Excel файл на Drive (CP8 срабатывает, но upload не протестирован)
- КЖ PDF pipeline (Drive OAuth fix должен помочь)
- Дублирование ответа в разные топики
- Голос 00:02-00:04 → revision вместо confirm
- Нормы СП/ГОСТ в technadzor_engine
- Шаблоны, multi-file

## DB STATE
ARCHIVED: 371 | DONE: 98 | CANCELLED: 165 | FAILED: 60


## ПАТЧИ СЕССИИ 29.04.2026

| Патч | Суть |
|---|---|
| CRON_AGGREGATOR | context_aggregator.py в cron каждый час, ONE_SHARED_CONTEXT.md обновляется автоматически |
## SESSION 29.04.2026 RESULTS

| Patch | File | Status |
|---|---|---|
| CRON_AGGREGATOR | tools/context_aggregator.py | INSTALLED, not battle-tested |
| P0_1_TEXT_ESTIMATE_FORCE_EXCEL_UPLOAD_V1 | core/estimate_engine.py | INSTALLED, not battle-tested |

SYNTAX_OK. Service active, NRestarts=0.

## ALL_CONTOURS PATCH 29.04.2026

| Patch | Status |
|---|---|
| ALL_CONTOURS_ROUTE_FILE_V2 | INSTALLED, not battle-tested |
| ALL_CONTOURS_TECHNADZOR_NORMS_V2 | INSTALLED, not battle-tested |
| ALL_CONTOURS_TEMPLATE_MANAGER_V2 | INSTALLED, not battle-tested |
| ALL_CONTOURS_CP8_DRIVE_LINK_V2 | INSTALLED, not battle-tested |
| ALL_CONTOURS_SHORT_VOICE_CONFIRM_V2 | INSTALLED, not battle-tested |

## NOT CLOSED
# NOT_CLOSED — 28.04.2026

## P1
- Дублирование задач x2
- Голос 00:02 -> revision вместо confirm

## P2
- monitor_jobs.py — НЕТ ФАЙЛА НЕТ CRON
- SEARCH_MONOLITH_V1 — live-тест не проводился
- Промпт Perplexity в ai_router.py — не написан
- Excel =C2*D2 / =SUM — не реализованы
- КЖ PDF pipeline — не реализован
- Нормы СП/ГОСТ — не реализованы


## NEXT PRIORITIES
P1 — реализовать первым:
TECHNICAL_FULL_CONTOUR | MODEL_ROUTER полный | PRE_OPENROUTER_MODEL_LAYER | FALLBACK_CHAIN
RESULT_VALIDATOR | RESULT_FORMAT_ENFORCER | FILE_RESULT_GUARD | INTENT_LOCK
DUPLICATE_TASK_GUARD | PRICE_NORMALIZATION | MULTI_OFFER_CONSISTENCY | CONSTRAINT_ENGINE
AVAILABILITY_CHECK | CONTACT_VALIDATION | REVIEW_SOURCE_WEIGHT | SEARCH_STATE_CONTROL
OUTPUT_DECISION_LOGIC | ORCHESTRA_SHARED_CONTEXT | HUMAN_DECISION_EDITOR | USER_MODE_SWITCH
AGGREGATOR (GAS v1) | MODEL_SPECIALIZATION | MEMORY_FILTER | SECURITY_SCOPE | EXECUTION_PRIORITY

P2 — после P1:
TASK_SPLITTER | MODE_SWITCH | CACHE_LAYER | MODEL_REGISTRY | SEARCH_PRESETS | SEARCH_DEPTH_LIMIT
SOURCE_DEDUPLICATION | TIME_RELEVANCE | REGION_PRIORITY | NEGATIVE_SELECTION | MODEL_RESULT_MERGE
MODEL_VOTING | ARTIFACT_VERSIONING | SOURCE_TRACE | AUDIT_LOG | STALE_CONTEXT_GUARD
LIVE_MARKET_SCAN | ERROR_EXPLAINER | DATA_CLASSIFICATION

P3 — мониторинг рынка:
PRICE_DRIFT_MONITOR | INVENTORY_BURN_MONITOR

---

## УЖЕ ЕСТЬ В КАНОНЕ (НЕ ДЕЛАТЬ ПОВТОРНО)
FSM pipeline | File pipeline 8 стадий | FAILED коды + таймауты | SEARCH 14 этапов
Trust Score 0-100 | SELLER_RISK | TCO | Шаблон звонка | Патч-протокол 8 шагов
GitHub SSOT регламент | secret_scan pre-commit | ROLLBACK_POINT | USER_APPROVAL_GATE
HEALTHCHECK | PRICE_AGING +5-10%

## LAST CHAT EXPORTS
### chat_exports/CHAT_EXPORT__claude_session_29_04_2026__2026-04-29.json
{
  "chat_id": "claude_session_29_04_2026",
  "chat_name": "AREAL-NEVA ORCHESTRA — Claude Session 28-29.04.2026",
  "exported_at": "2026-04-29T01:45:00+03:00",
  "source_model": "Claude Sonnet 4.6",
  "system": "AREAL-NEVA ORCHESTRA Ubuntu 24.04 89.22.225.136 /root/.areal-neva-core",
  "architecture": "Telegram → telegram_daemon.py → core.db → task_worker.py → ai_router.py → OpenRouter → reply_sender.py → Telegram",
  "pipeline": "NEW → INTAKE → IN_PROGRESS → RESULT_READY → AWAITING_CONFIRMATION → DONE → ARCHIVED",
  "patches": [
    "FIX_VOICE_GUARD_20260428 → telegram_daemon.py:961 → word-boundary → SYNTAX_OK active",
    "FIX_IS_SEARCH_20260428 → task_worker.py:2266 → is_search в payload → SYNTAX_OK active",
    "FIX_SEARCH_CONTEXT_20260428 → task_worker.py:2248 → clear search_context → SYNTAX_OK active",
    "FIX_VOICE_REVISION_V2 → telegram_daemon.py:880+ → empty revision fix → SYNTAX_OK active",
    "FIX_VOICE_CONFIRM_IN_PROGRESS → telegram_daemon.py:560 → голос confirm → SYNTAX_OK active",
    "FIX_CRASHLOOP_3981 → task_worker.py:3981 → NameError p=__file__ → SYNTAX_OK active",
    "FIX_CP8_ERROR_CLOSE → task_worker.py → estimate errors → FAILED не повисают → SYNTAX_OK active",
    "FIX_CP8_SEARCH_TYPE → task_worker.py → input_type search → CP8 estimate hook → SYNTAX_OK active",
    "FIX_EMPTY_AI_RETRY → task_worker.py:2297 → retry 3x при chars=0 → SYNTAX_OK active",
### chat_exports/CHAT_EXPORT__github_ssot_technical_orchestra__2026-04-29.json
{
  "chat_id": "UNKNOWN",
  "chat_name": "github_ssot_technical_orchestra",
  "exported_at": "2026-04-29T00:00:00+02:00",
  "source_model": "ChatGPT GPT-5.5 Thinking",
  "system": "AREAL-NEVA ORCHESTRA: сервер 89.22.225.136, base /root/.areal-neva-core, Telegram bot @ai_orkestra_all_bot, GitHub repo rj7hmz9cvm-lgtm/areal-neva-core, GitHub используется как SSOT для канонов и shared context, сервер используется как runtime, Google Drive оставлен как резерв и хранилище тяжёлых файлов",
  "architecture": "Telegram -> telegram_daemon/task_worker -> ai_router/OpenRouter/DeepSeek -> engines/Python -> validator -> HUMAN_DECISION_EDITOR -> Telegram. GitHub docs/CANON_FINAL и docs/SHARED_CONTEXT являются текстовым SSOT. Сервер хранит runtime, core.db, memory.db, обработку файлов. Drive не является главным мозгом",
  "pipeline": "Базовый lifecycle задач: NEW -> IN_PROGRESS -> AWAITING_CONFIRMATION -> DONE -> ARCHIVED. Для файлового контура целевой pipeline: INGESTED -> DOWNLOADED -> PARSED -> CLEANED -> NORMALIZED -> CALCULATED -> ARTIFACT_CREATED -> UPLOADED",
  "files": [
    "README.md -> описание GitHub SSOT",
    "docs/ARCHITECTURE/SEARCH_MONOLITH_V1.md -> канон интернет-поиска topic_500",
    "docs/CANON_FINAL/00_INDEX.md -> индекс канонов",
    "docs/HANDOFFS/LATEST_HANDOFF.md -> handoff состояния 28.04.2026",
    "docs/REPORTS/NOT_CLOSED.md -> незакрытые задачи",
    "docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK.md -> master architecture block v1",
    "tools/context_aggregator.py -> заготовка агрегатора контекста",
    "tools/secret_scan.sh -> pre-commit secret scan",
    "runtime/.gitkeep -> заглушка runtime без хранения мусора",
### chat_exports/HANDOFF__CLAUDE_TO_NEXT_AI__2026-04-27.txt
﻿AREAL-NEVA ORCHESTRA - SESSION HANDOFF 2026-04-27 02:10 MSK
SOURCE: Claude session 26-27.04.2026
FOR: Next AI - read this FIRST before any action
== SYSTEM STATE ==
Server: 89.22.225.136 Path: /root/.areal-neva-core
Services: areal-telegram-daemon PID 1566302 running since 01:37 (systemd shows inactive but process alive), areal-task-worker ACTIVE, areal-memory-api ACTIVE
== VOICE FIX APPLIED TODAY ==
ROOT CAUSE: telegram_daemon.py line 902-903 referenced CHAT_ONLY_PHRASES (NameError). CANON_PASS13 defined it at line 940 after main() runs.
FIX: sed -i 902-903 commented out with DISABLED_PASS13. Voice now works.
== BROKEN - FIX NEXT ==
P0 CONFIRMATION HANDLER:
- Da after Dovolet? creates NEW task instead of closing existing AWAITING_CONFIRMATION
- Canon 2.1 violation: CONFIRM must close task
- Canon 2.3 violation: reply to bot must NOT create new task
- FIX: grep -n _handle_control_text telegram_daemon.py, read function, verify bot_message_id lookup vs reply_to_message_id
- CHECK: sqlite3 data/core.db SELECT bot_message_id FROM tasks WHERE state=AWAITING_CONFIRMATION LIMIT 5
P1 CHAT INTENT AUTO-CLOSE:
- Conversational responses hang 600s STALE_TIMEOUT
### chat_exports/README.md
# CHAT_EXPORTS — Выгрузки чатов
Сюда сохраняются все экспорты сессий.
Формат имени: CHAT_EXPORT__<имя>__<YYYY-MM-DD>.json
Папка только пополняется. Ничего не удалять, не перезаписывать.
### chat_exports/ZAPROS_DLY_AI_AGENTOV_2026-04-27.txt
﻿ZAPROS K AI-AGENTU — AREAL-NEVA ORCHESTRA
Data: 27.04.2026 09:10 MSK
TY OBYAZAN VYPOLNIT SLEDUYUSCHIE SHAGI PO PORYADKU:
1. Zaydi na Google Drive
2. Prochitay VSE fayly v papke CANON_FINAL id=1U_IrEOtIJfUVAdjH-kHwms2M2z3FXan0
3. Prochitay VSE fayly v papke vygruzki chatov id=14bYA9bHaKahkE8d4IDwWxL4Ojn-G0sDl
4. Glavnyy kanon: id=1k_KIpQ7jD15_w83sMz4WfqoEIINIXTHTaTOtUovf2gU
5. Posle prochteniya — zaydi na server SSH areal (89.22.225.136)
6. Prover zhivoe sostoyanie sistemy komandami nizhe
7. Day reshenie TOLKO po faktam
DIAGNOSTICHESKIE KOMANDY:
ssh areal 'bash -s' << 'ENDSSH'
cd /root/.areal-neva-core
sed -n '475,560p' telegram_daemon.py
sqlite3 data/core.db 'SELECT state, COUNT(*) FROM tasks GROUP BY state'
tail -30 logs/telegram_daemon.log
grep -n 'SHORT_CONFIRM\|CANCEL_PHRASES\|CHAT_ONLY\|FINISH_PHRASES' telegram_daemon.py | head -20
ENDSSH

## BROKEN NOW
## P1
- Дублирование задач x2
- Голос 00:02 -> revision вместо confirm

## P2
- monitor_jobs.py — НЕТ ФАЙЛА НЕТ CRON
- SEARCH_MONOLITH_V1 — live-тест не проводился
- Промпт Perplexity в ai_router.py — не написан
- Excel =C2*D2 / =SUM — не реализованы
- КЖ PDF pipeline — не реализован
- Нормы СП/ГОСТ — не реализованы

## FORBIDDEN
ЗАПРЕЩЕНО: перезатирать, удалять, упрощать каноны.
РАЗРЕШЕНО: только добавление, версионирование v1/v2/v3.
secret_scan.sh обязателен перед push.
USER_APPROVAL_GATE: канон меняется только после явного да.

### Реализация агрегатора
GAS v1   — Drive-агрегатор (читает → индексирует → пишет md/json)
Python v2 — серверный агрегатор с LLM через OpenRouter

---

## ПОЛНЫЙ СПИСОК БЛОКОВ

P1 — реализовать первым:
TECHNICAL_FULL_CONTOUR | MODEL_ROUTER полный | PRE_OPENROUTER_MODEL_LAYER | FALLBACK_CHAIN
RESULT_VALIDATOR | RESULT_FORMAT_ENFORCER | FILE_RESULT_GUARD | INTENT_LOCK
DUPLICATE_TASK_GUARD | PRICE_NORMALIZATION | MULTI_OFFER_CONSISTENCY | CONSTRAINT_ENGINE
AVAILABILITY_CHECK | CONTACT_VALIDATION | REVIEW_SOURCE_WEIGHT | SEARCH_STATE_CONTROL
OUTPUT_DECISION_LOGIC | ORCHESTRA_SHARED_CONTEXT | HUMAN_DECISION_EDITOR | USER_MODE_SWITCH
AGGREGATOR (GAS v1) | MODEL_SPECIALIZATION | MEMORY_FILTER | SECURITY_SCOPE | EXECUTION_PRIORITY

P2 — после P1:
TASK_SPLITTER | MODE_SWITCH | CACHE_LAYER | MODEL_REGISTRY | SEARCH_PRESETS | SEARCH_DEPTH_LIMIT
SOURCE_DEDUPLICATION | TIME_RELEVANCE | REGION_PRIORITY | NEGATIVE_SELECTION | MODEL_RESULT_MERGE
MODEL_VOTING | ARTIFACT_VERSIONING | SOURCE_TRACE | AUDIT_LOG | STALE_CONTEXT_GUARD
LIVE_MARKET_SCAN | ERROR_EXPLAINER | DATA_CLASSIFICATION

P3 — мониторинг рынка:
PRICE_DRIFT_MONITOR | INVENTORY_BURN_MONITOR

---

## УЖЕ ЕСТЬ В КАНОНЕ (НЕ ДЕЛАТЬ ПОВТОРНО)
FSM pipeline | File pipeline 8 стадий | FAILED коды + таймауты | SEARCH 14 этапов
Trust Score 0-100 | SELLER_RISK | TCO | Шаблон звонка | Патч-протокол 8 шагов
GitHub SSOT регламент | secret_scan pre-commit | ROLLBACK_POINT | USER_APPROVAL_GATE
HEALTHCHECK | PRICE_AGING +5-10%

# SEARCH_MONOLITH_V1 — КАНОН ИНТЕРНЕТ-ПОИСКА ОРКЕСТРА
Версия: v1 FINAL | Дата: 28.04.2026 | Топик: topic_500
Статус: ЦЕЛЕВОЙ КАНОН — live-тест не проводился

---

## СУТЬ

Оркестр в topic_500 — не поисковик. Это цифровой снабженец.
Задача: не найти где купить, а дать закупочное решение.

понять задачу → уточнить критерии → найти по всем площадкам
→ проверить риски → посчитать реальную выгоду → выдать решение

Результат всегда:
что брать / где брать / почему / какие риски
что проверить звонком / что отбросить / что не подтверждено

---

## 14 ЭТАПОВ (обязательная последовательность)
