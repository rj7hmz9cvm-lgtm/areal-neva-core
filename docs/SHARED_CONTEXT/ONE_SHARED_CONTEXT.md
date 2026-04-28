# ONE_SHARED_CONTEXT
updated_at: 2026-04-28T21:45:12.434653+00:00

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
UNKNOWN

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
## ПАТЧИ СЕССИИ (все applied, SYNTAX_OK, active)

| Патч | Файл | Строка | Суть |
|---|---|---|---|
| FIX_VOICE_GUARD_20260428 | telegram_daemon.py | 961 | substring -> word-boundary |
| FIX_IS_SEARCH_20260428 | task_worker.py | 2266 | SEARCH_PATTERNS -> is_search |
| FIX_SEARCH_CONTEXT_20260428 | task_worker.py | 2248 | свежий поиск без старых результатов |
| FIX_VOICE_REVISION_20260428_V2 | telegram_daemon.py | 880+ | [REVISION] пустой -> strip |
| FIX_VOICE_CONFIRM_IN_PROGRESS_20260428 | telegram_daemon.py | 560 | confirm в IN_PROGRESS |

## СТРОКИ (верифицировано grep)

task_worker.py: 735, 2579, 2291/2664/2968, 2641/2654/2794/2795, 2266, 2248
telegram_daemon.py: 961, 560, 543/558, 899, 1086, 1122, 743-745

## LIVE ТЕСТ OK
- Поиск RAL 8017: osnova.spb.ru 440 + pkmm.ru 801 (без RAL 6005)
- Голос revision -> Принял правки. Переделываю
- AWAITING_CONFIRMATION=0

## НЕ ЗАКРЫТО
P1: дублирование задач x2 / голос 00:02 -> revision вместо confirm
P2: monitor_jobs.py нет / SEARCH_MONOLITH_V1 live-тест не проводился

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
### chat_exports/CHAT_EXPORT__areal-neva-core__2026-04-27.txt
{
  "chat_id": "UNKNOWN",
  "chat_name": "areal-neva-core",
  "exported_at": "2026-04-27T20:00:00Z",
  "source_model": "Claude Sonnet 4.6",
  "system": "Multi-agent AI orchestration infrastructure areal-neva-core. Telegram bots, async task workers, Python agents, Google Drive sync, SQLite-backed state management. Self-hosted Linux server + MacBook Air.",
  "architecture": "Telegram bot -> task_worker.py -> SQLite WAL task queue -> agent handlers (Claude/ChatGPT/Gemini/Grok/DeepSeek/Perplexity) -> results stored in SQLite -> Google Drive sync via Mac",
  "pipeline": "NEW -> IN_PROGRESS -> DONE / FAILED -> ARCHIVED",
  "files": [
    "task_worker.py -> central async worker for task lifecycle",
    "google_io.py -> Google Drive integration with lazy imports",
    "pin_manager.py -> pin state management via SQLite",
    "drive_ingest.py -> Google Drive file ingestion with service file filters",
    "deploy_patch.sh -> deployment script: stop/backup/patch/restart/logs"
  ],
  "code": "Python asyncio / SQLite WAL / Telethon / openpyxl / Bash / Linux server + macOS local",
  "patches": [
    "task_worker_race_condition_guard -> task_worker.py -> voice file availability check -> status: applied_by_terminal",
### chat_exports/CHAT_EXPORT__areal_neva__2026-04-23.txt
﻿{
  "chat_id": "-1003725299009",
  "chat_name": "areal_neva_orchestra",
  "exported_at": "2026-04-23T09:30:00Z",
  "source_model": "claude-sonnet-4-6",
  "system": {
    "server": "89.22.225.136",
    "os": "Ubuntu 24.04",
    "base": "/root/.areal-neva-core",
    "venv": "/root/.areal-neva-core/.venv/bin/python3",
    "bot": "@ai_orkestra_all_bot id=8216054898",
    "db_path": "/root/.areal-neva-core/data/core.db",
    "memory_db": "/root/.areal-neva-core/data/memory.db"
  },
  "architecture": [
    "telegram_daemon.py â€” intake Ð³Ð¾Ð»Ð¾Ñ�/Ñ‚ÐµÐºÑ�Ô¿Ñ„Ð°Ð¹Ð»Ñ‹",
    "task_worker.py â€” Ð¾Ð±Ñ€Ð°Ð±Ð¾Ñ‚ÐºÐ° Ð·Ð°Ð´Ð°Ñ‡, polling",
    "core/ai_router.py â€” routing Ð² LLM (deepseek/openrouter)",
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
P1: дублирование задач x2 / голос 00:02 -> revision вместо confirm
P2: monitor_jobs.py нет / SEARCH_MONOLITH_V1 live-тест не проводился

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
