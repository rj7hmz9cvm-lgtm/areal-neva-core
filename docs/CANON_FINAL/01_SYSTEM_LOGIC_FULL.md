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
§0.3 Запрет тихих операций — требуют явного «да»: Drive, удаление, патчи, БД, Git, systemd.
НАРУШЕНИЕ ЗАФИКСИРОВАНО 28.04.2026: Claude загрузил файл без явного «да».
§0.4 Диагностика первой: logs → db → pin → memory → context → patch.
tail ≤ 40 строк (Claude) / ≤ 20 (GPT/iPhone). grep|head ≤ 30 строк/файл. Не более 5-6 файлов.
§0.5 Порядок патчей (8 шагов):
1. Диагностика 2. Анализ 3. Описать+ждать «да»
4. cp bak && echo BAK_OK
5. Patch через /tmp
6. python3 -m py_compile && echo SYNTAX_OK
7. systemctl restart && sleep 5 && is-active
8. journalctl -n 20 --no-pager
§0.6 Workflow: Claude(ТЗ+верификация) → GPT(патчи) → GPT(вывод) → Claude(сверка) → Пользователь
§0.7 FACT-ONLY: каждое утверждение → file line / log entry / db record. Нет mapping → невалидно.
§0.8 Запрещённые файлы: .env credentials.json *.session token.json google_io.py memory.db-schema ai_router.py reply_sender.py systemd-unit-файлы
§0.8.1 telegram_daemon.py — редактировать только с явного «да» пользователя (не в автоматическом режиме)
§0.9 SSH форматы: Mac=python3 - << 'PYEOF' | Сервер=ssh areal 'bash -s' << 'ENDSSH'. ЗАПРЕЩЕНО heredoc << EOF без кавычек через iPhone.
§0.10 iPhone лимиты: journalctl -n 5 --output=cat | sqlite3 LIMIT 3 | без ssh areal префикса.

## §1. ФИЗИЧЕСКИЙ СЛОЙ
ОС: Ubuntu 24.04 LTS | hostname: graceful-olive.ptr.network
Base: /root/.areal-neva-core/ | Venv: /root/.areal-neva-core/.venv/bin/python3 | Python: 3.12
IP1: 89.22.225.136 — SSH/Management/VPN (WireGuard/Xray)
IP2: 89.22.227.213 — Orchestra API порт 8080
net.ipv4.ip_nonlocal_bind=1 в /etc/sysctl.d/99-nonlocal-bind.conf — обязательно.
orchestra-ip.service — удерживает IP2.
fcntl.flock(LOCK_EX|LOCK_NB) — защита от двойного запуска.
Docker + Flask + threading.Lock() — для webhook.py. Gunicorn — отказ навсегда.

§1.1 Сервисы:
areal-task-worker.service   task_worker.py      ОСНОВНОЙ ✅
telegram-ingress.service    telegram_daemon.py  ОСНОВНОЙ ✅ (active с 28.04)
areal-memory-api.service    memory_api_server.py порт 8091 ✅
areal-telegram-daemon.service — DISABLED НЕ ИСПОЛЬЗОВАТЬ

§1.2 Telegram:
Бот: @ai_orkestra_all_bot | id=8216054898 | Чат: -1003725299009 | Имя: Орик
Topics: CHAT_ZADACH(без номера) STROYKA=topic_2 TEKHNADZOR=topic_5 KODY_MOZGOV=topic_3008
api_id: 27925449
Аккаунты: +79626847001(СК Ареал-Нева, user_primary) +79215851132(Илья NADZOR812, user_secondary)
Сессии: /root/.areal-neva-core/sessions/user.session (69632 байт)
Telethon 1.43.2 в .venv ✅ авторизован
topic_id = message.message_thread_id or 0 → tasks.topic_id при create_task
KORDON СНТ: group_id -1002220455500 | Drive: 1loZ09i-KIE22TDnBACCTjJZce0aPO4ez
Загружено 28.04: 398 файлов (JPG/MP4/MOV/PDF/DOCX), 303 новых, 0 дублей.

§1.3 Google Drive:
AI_ORCHESTRA:        13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB
CANON_FINAL:         1U_IrEOtIJfUVAdjH-kHwms2M2z3FXan0
CHAT_EXPORTS:        14bYA9bHaKahkE8d4IDwWxL4Ojn-G0sDl
chat_-1003725299009: 1vN32Dq45oi939xHIyNoOYkBlBYuy4BuN
chat/topic_2:        1F4qRGBCqjPZIjvkREwiPrQOOrfuRXVjA
КОРДОН СНТ/Фото:     1loZ09i-KIE22TDnBACCTjJZce0aPO4ez
ESTIMATES:           1fqw-fuUoM0HxHkgL_ZRxE3KFboDvwxsm
DRIVE_INGEST:        13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB
Создание в корне My Drive — ЗАПРЕЩЕНО. Экспорты только в CHAT_EXPORTS.

§1.4 OAuth (актуально 28.04.2026 ✅):
1. GDRIVE_REFRESH_TOKEN → протух → invalid_grant
2. Service Account → storageQuotaExceeded
3. Desktop OAuth Mac → token.json → scp → сервер ✅
Путь: /root/.areal-neva-core/token.json
client_id: 55296410358-8bc4pe7a6oat5fimpct5g3ra9qq5ts3c.apps.googleusercontent.com
scope: https://www.googleapis.com/auth/drive | Аккаунт: nadzor812@gmail.com

§1.5 API статус (28.04.2026):
✅ OpenRouter(DeepSeek+Perplexity) | ✅ Google API(Gemini) | ✅ Groq(Whisper)
❌ Anthropic(401) | ❌ OpenAI(429) | ❌ Grok(403) | ❌ DeepSeek direct(402)

§1.6 Модели:
DEFAULT: deepseek/deepseek-chat
ONLINE:  perplexity/sonar
VISION:  google/gemini-2.5-flash
STT:     groq/whisper-large-v3-turbo

§1.7 Стек:
Python 3.12, aiogram, aiosqlite, SQLite(core.db), Redis(core/redis_state.py),
Google Drive API OAuth2, google-auth-oauthlib, pytesseract(✅28.04), ezdxf,
pdfplumber, python-docx, openpyxl, pdf2image, poppler v24.02.0,
Groq API(STT), OpenRouter API(LLM), systemd, fcntl

## §2. АРХИТЕКТУРА

§2.1 FSM:
NEW → INTAKE → NEEDS_CONTEXT → IN_PROGRESS → RESULT_READY → AWAITING_CONFIRMATION → DONE → ARCHIVED
РАСХОЖДЕНИЕ: ТЗ(doc2)+CANON_FULL базовая цепочка NEW→IN_PROGRESS→AWAITING_CONFIRMATION→DONE.
INTAKE/NEEDS_CONTEXT/RESULT_READY — внутренние sub-state. Авторитет: ТЗ+CANON_FULL.

§2.2 Pipeline:
Telegram → telegram_daemon.py → core.db(aiosqlite) → task_worker.py → ai_router.py → OpenRouter → reply_sender.py → Telegram
Голос: voice → telegram_daemon.py → stt_engine.py → Groq Whisper → [VOICE]text → create_task → core.db → task_worker.py

§2.3 Мульти-модельная оркестрация:
Claude     → контроль/канон/проверка/ТЗ
ChatGPT    → патчи/код/сервер
DeepSeek   → основной ответ (DEFAULT_MODEL)
Perplexity → поиск (ONLINE_MODEL)
Gemini     → vision/fallback
ПРАВИЛА: не дублировать ответы, не запускать все одновременно, поиск только Perplexity, основной только DeepSeek, модели=инструменты.

§2.4 Inbox Aggregator (P2 — не реализован):
Unified item: source, external_id, text, user_name, user_id, contact, link, timestamp, attachments, chat_name, topic_id, priority, status
Фильтры: ключевые слова/регион/цена. Spam отсекается ДО create_task.
ЗАПРЕЩЕНО: засорять memory search-результатами.

## §3. КЛЮЧЕВЫЕ ФАЙЛЫ
task_worker.py          — основной воркер
telegram_daemon.py      — ingress + voice
core/db.py              — DB layer
core/redis_state.py     — Redis state management
core/ai_router.py       — маршрутизация LLM (ЗАПРЕЩЕНО РЕДАКТИРОВАТЬ)
core/reply_sender.py    — отправка ответов (ЗАПРЕЩЕНО РЕДАКТИРОВАТЬ)
core/stt.py             — Groq Whisper STT контур
stt_engine.py           — STT engine (подтверждён pipeline 27.04)
core/file_intake_router.py — маршрутизация файлов
core/estimate_engine.py — движок смет
core/ocr_engine.py      — OCR движок
core/technadzor_engine.py — технадзор движок
core/dwg_engine.py      — DWG/DXF движок
core/engine_base.py     — базовый класс движков
core/template_manager.py — шаблоны
core/topic_drive_oauth.py — Drive OAuth для топиков (запатчен 28.04)
retry_worker.py         — retry логика задач
media_group.py          — обработка media group
context_engine.py       — сборка контекста для LLM
agent_contract.py       — контракт движков
delivery.py             — доставка результатов
startup_recovery.py     — восстановление задач при старте
drive_ingest.py         — Drive ingestion (PID 1563958, без unit-файла, поднимать вручную)
memory_api_server.py    — Memory API порт 8091
google_io.py            — Drive I/O (ЗАПРЕЩЕНО без разрешения)

## §4. TASK LIFECYCLE

§4.1 Ingress: update_id, message_id, chat_id, topic_id, input_type(text/voice/file/drive_link), raw_input, normalized_input, state=NEW, created_at, error_msg, result_text, bot_message_id, artifact_path
Идемпотентность: update_id → ровно одна задача. Guard через processed_updates.

§4.2 Таймауты:
STT=30с | router=60с | engine=300с(строки 2291/2664/2968) | drive=60с | send=30с | confirmation=300с | stale=600с

§4.3 Валидация файлов по сигнатуре: PDF=%PDF | XLSX=PK\x03\x04

§4.4 FAILED коды:
STALE_TIMEOUT | INTAKE_TIMEOUT(строка 735) | STT_ERROR | ENGINE_TIMEOUT | DOWNLOAD_FAILED | UPLOAD_FAILED | REQUEUE_LOOP(строка 2579) | DUPLICATE_FILE | SOURCE_FILE_VALIDATION

§4.5 Артефакт-манифест: source_file_id, artifact_file_id, artifact_path, artifact_mime, artifact_size, engine, validation_status
drive_link результата ≠ исходный файл.

§4.6 Watchdog: AWAITING_CONFIRMATION → stale watchdog → FAILED:STALE_TIMEOUT (добавлен 28.04)

§4.7 Протокол экспорта:
Папка: 14bYA9bHaKahkE8d4IDwWxL4Ojn-G0sDl
Имя: CHAT_EXPORT__{SYSTEM}__{DATE}.{ext}
Поля: chat_id, exported_at, source_model, system{}, architecture{}, pipeline[], patches[], open_contours[], db_state{}

## §5. КОМАНДЫ БОТА
статус / система / система файл / память / память файл / архив / архив файл
файл / дамп / дамп файл / язон / язон файл / код файл
сброс задач / отбой / отмена
cancel_all_open_tasks(chat_id, topic_id=0): topic_id>0→только топик | topic_id=0→все задачи чата
HUMAN_SHORT(строка 4): да ок ага понял хорошо ясно ладно угу
CHAT AUTO-DONE(строки 1503-1505): орик орек ау вот живой ты тут слышишь эй привет добрый вечер доброе утро добрый день

## §6. ДОМЕНЫ
STROYKA(topic_2):    сметы, чертежи DWG, стройматериалы, Excel
TEKHNADZOR(topic_5): фото дефектов, PDF отчёты, нормы СП/ГОСТ/СНиП
SEARCH(topic_500):   интернет-поиск, цифровой снабженец
KODY_MOZGOV(3008):   верификация моделей, тест задачи

## §7. MEMORY / PIN / CONTEXT
memory.db: /root/.areal-neva-core/data/memory.db
Запись: только после DONE. Long memory: task_summary, assistant_output.
Retrieval: поиск по ключевым словам, не более 3 записей.
Pin: save_pin() после успешной обработки файла.
Context: _active_unfinished_context + _load_memory_context

## §8. ПАТЧИ

§8.1 До 28.04.2026:
строка 766 — убрано зацикливание подтверждения
file_intake_router — async fix
estimate_engine + dwg_engine — убран лишний await
engine_base.upload_artifact_to_drive — asyncio.run_until_complete fix
pytesseract — установлен ✅
AWAITING_CONFIRMATION — добавлен в stale watchdog
PIN fallback — добавлен
validate_table_items_for_estimate — добавлен
PATCH_REQUEUE_LOOP_ALLOW_ONCE (строка 2579) — добавлен
Engine timeout=300 (строка 2005) — добавлен
intake timeout (строка 690) — добавлен

§8.2 Патчи 28.04.2026 (все SYNTAX_OK, active):
FIX_VOICE_GUARD_20260428       telegram_daemon.py  961  substring→word-boundary (да in задачам=True)
FIX_IS_SEARCH_20260428         task_worker.py      2266 SEARCH_PATTERNS→is_search в work_payload
FIX_SEARCH_CONTEXT_20260428    task_worker.py      2248 свежий поиск→search_context=""
FIX_VOICE_REVISION_20260428_V2 telegram_daemon.py  880+ [REVISION] пустой→_rev_text strip
FIX_VOICE_CONFIRM_IN_PROGRESS  telegram_daemon.py  560  confirm в IN_PROGRESS

## §9. ВЕРИФИЦИРОВАННЫЕ СТРОКИ (grep 28.04.2026)

task_worker.py:
735   PATCH_INTAKE_TIMEOUT watchdog
2579  PATCH_REQUEUE_LOOP_ALLOW_ONCE
2291/2664/2968 asyncio.wait_for ENGINE
2266  is_search в work_payload
2248  _is_fresh_search
2641/2654/2794/2795 get_clarification_message
4     HUMAN_SHORT

telegram_daemon.py:
543/558 CANON_PASS_REPLY_CONFIRM
560   FIX_VOICE_CONFIRM_IN_PROGRESS
743-745 SERVICE_FILE_GUARD
880+  FIX_VOICE_REVISION_V2
899   _handle_duplicate_file_guard
961   FIX_VOICE_GUARD word-boundary
1086  _canon_duplicate_prompt_v2
1122  _handle_universal_duplicate_file_guard_v2
1503-1505 CHAT AUTO-DONE

core/file_intake_router.py:
get_clarification_message — СУЩЕСТВУЕТ ✅ (v13 ошибочно писал «grep пустой»)

## §10. LIVE ТЕСТ 28.04.2026 ✅
Поиск RAL 8017: osnova.spb.ru 440р/м² + pkmm.ru 801р/м² (без RAL 6005 ✅)
Голос revision: 19:20, 19:23, 19:37 → «Принял правки. Переделываю» ✅
DB topic_500: 04db2846 DONE ✅ | 66ebd0c4 DONE ✅ | AWAITING_CONFIRMATION=0 ✅
Сервисы: areal-task-worker ✅ | telegram-ingress ✅ BOT 19:46:28 | areal-memory-api ✅
DB: ARCHIVED 371+, DONE 95+

## §11. SEARCH_MONOLITH_V1 — КАНОН ПОИСКА
Суть: topic_500 = цифровой снабженец. Результат: что/где/почему/риски/звонок.

14 этапов:
1.  Разбор: товар, SKU/OEM, регион, приоритет. Стройка: RAL/толщина/ГОСТ. Запчасти: OEM/рестайлинг/сторона.
2.  Уточнения (макс.3): город? новое/б/у? OEM? самовывоз?
3.  Search Session — уточнения продолжают сессию, НЕ создают новую задачу
4.  Расширение (7+ формул): +город, +оптом, OEM, SKU, без маркетинга, +Avito, +VK/Telegram
5.  Цифровой двойник — по физическим параметрам, не по названию
6.  Источники: Ozon/WB/Avito/2GIS/Exist/Drom/VK/Telegram/форумы
7.  Проверка источника: CONFIRMED/PARTIAL/UNVERIFIED/RISK
8.  Детектор живости: checked_at+source_url обязательны. >48ч → +5-10% TCO
9.  Отзывы + Review Trust Score 0-100
10. Микрометр: толщина/цинк/OEM соответствие
11. Запрет смешивать ТТХ: 0.45/0.5, RAL разные, рестайлинг/дорестайлинг, сторона
12. Risk Score + SELLER_RISK (VK/Telegram: новая группа/боты/без фото/только предоплата)
13. TCO = цена + доставка + комиссия + риск − кэшбэк
14. Живой рынок: остатки/ликвидация → UNVERIFIED до подтверждения

Review Trust Score: 80-100=живые | 60-79=частично | 40-59=звонок | 0-39=фейк
Статусы рекомендации: CHEAPEST/MOST_RELIABLE/BEST_VALUE/FASTEST/RISK_CHEAP/REJECTED
Статусы отзывов: REVIEWS_CONFIRMED/REVIEWS_PARTIAL/REVIEWS_FAKE_RISK/REVIEWS_NOT_FOUND

Шаблон звонка: цена актуальна? есть? с НДС? единица? доставка? самовывоз? документы? гарантия? ТТХ?
Для металла: толщина/покрытие/цинк. Для запчастей: OEM/сторона/кузов/состояние.

Реализация:
Шаг1 ✅ DONE: is_search→Perplexity (28.04.2026)
Шаг2: промпт в ai_router.py
Шаг3: search_session в memory.db
Шаг4: Risk+Trust через LLM
Шаг5 PRO: Telethon (userbot авторизован)

Нельзя заявлять как работающее: парсинг закрытых чатов, проверка SSL/cache автоматически, биржевые индексы.

24 модуля: SearchSessionManager CriteriaExtractor ClarificationEngine SourcePlanner QueryExpander EntityResolver MarketplaceCollector ClassifiedsCollector AutoPartsCollector ConstructionSupplyCollector SocialSearchCollector MapsCollector OfferNormalizer SupplierClassifier TechnicalAudit LivenessCheck ReviewAnalyzer FakeDetector RiskScorer TcoCalculator ValueOptimizer ResultRanker SearchMemoryWriter SearchOutputFormatter

## §12. GITHUB SSOT (установлено 28.04.2026)
Repo: rj7hmz9cvm-lgtm/areal-neva-core
Token: /root/.areal-neva-core/.env → GITHUB_TOKEN
Структура: docs/CANON_FINAL/ docs/SHARED_CONTEXT/ docs/ARCHITECTURE/ docs/HANDOFFS/ docs/REPORTS/ tools/ scripts/ runtime/.gitkeep
Регламент: только добавление, версионирование v1/v2/v3, secret_scan.sh pre-commit hook.
Паттерны в /root/.areal-neva-core/.secret_patterns (не в репо).

Архитектура SSOT:
GitHub = мозг (каноны + логика + shared context)
Сервер = runtime (обработка, memory.db, core.db)
Drive  = резерв и тяжёлые файлы
Поток: чат/выгрузка → монолит → GitHub → все нейросети читают GitHub

## §13. НЕЗАКРЫТЫЕ КОНТУРЫ

P1:
- Дублирование задач x2
- Голос 00:02 → revision вместо confirm
- get_clarification_message — верификация поведения
- Дублирование topic_id
- Голосовое подтверждение как текст
- Дубликат файла в reply
- file_intake_router не вызывается в _handle_drive_file

P2:
- monitor_jobs.py — НЕТ ФАЙЛА НЕТ CRON
- SEARCH_MONOLITH_V1 — live-тест не проводился
- Промпт Perplexity в ai_router.py
- Excel =C2*D2 / =SUM
- КЖ PDF pipeline
- Нормы СП/ГОСТ/СНиП
- Шаблоны
- Google Sheets (403 NOT IMPLEMENTED)
- context_aggregator.py — заготовка
- ONE_SHARED_CONTEXT.md — не заполнен
- Движки из снапшота
- Intake с предложением действий
- Multi-file поддержка

## §14. GITHUB FRESHNESS AND CHAT EXPORT RULE — ДОПОЛНЕНИЕ

GitHub является единственным публичным SSOT для нейросетей.

GitHub хранит только CLEAN export:
- проверенная информация
- архитектура, решения, патчи, ошибки, текущее состояние
- незакрытые задачи, команды и код без приватных значений

Сервер хранит FULL export:
- полный приватный технический архив
- runtime context, внутренние значения

FULL export сервера запрещено пушить в GitHub.

Для GitHub:
- один чат = один CLEAN файл
- путь: chat_exports/CHAT_EXPORT__<SAFE_NAME>__YYYY-MM-DD.json
- формат: валидный JSON object only, без текста до и после
- без перезаписи существующих файлов
- private/auth/config/access values заменяются на "<REDACTED>"

Для сервера:
- один чат = один FULL файл
- путь: /root/.areal-neva-core/chat_exports/CHAT_EXPORT_FULL__<SAFE_NAME>__YYYY-MM-DD.json
- если у нейросети нет SSH-доступа → вернуть готовый SSH-блок для пользователя без вложенных heredoc

GitHub freshness rule:
- GitHub web UI не является доказательством свежести
- запрещено доверять cached blob/main странице
- перед чтением контекста: получить latest commit SHA ветки main
- читать docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md по exact commit SHA
- сверить updated_at с последним AGG-коммитом
- если mismatch → STALE_GITHUB_CONTEXT → остановка

Источник правды по свежести:
1. latest commit SHA main
2. raw file at exact SHA
3. internal updated_at
4. GitHub UI page — NOT proof

## §0.11 ОБЯЗАТЕЛЬНАЯ САМОПРОВЕРКА AI (30.04.2026)

Правило обязательно для любой нейросети: Claude, ChatGPT, Gemini и других.

### Перед написанием кода AI обязан:
1. Прочитать актуальные каноны (GitHub docs/CANON_FINAL/)
2. Прочитать LATEST_HANDOFF.md и NOT_CLOSED.md
3. Найти все принятые решения по данной теме в текущем чате
4. Убедиться что файлы которые будут изменены — не в списке §0.8 ЗАПРЕЩЁННЫХ
5. Запросить диагностику актуального состояния кода если якорь неизвестен

### После написания кода AI обязан провести самопроверку:
1. §0.3 — есть явное «да» от пользователя?
2. §0.5 — соблюдён порядок: BAK → patch → py_compile → restart → sleep → is-active → journal?
3. §0.8 — не тронуты запрещённые файлы?
4. §0.9 — правильный SSH формат?
5. Якоря — взяты из актуального кода (не из памяти)?
6. Колонки БД — проверены перед INSERT/UPDATE?
7. PYTHONPATH — передан если нужен?
8. Правила изоляции топиков — соблюдены?

### Если самопроверка выявила ошибку:
Молча исправить → провести самопроверку повторно → только потом предложить запуск.

### Drive/Storage правило (30.04.2026):
Артефакты загружаются ТОЛЬКО в папку топика: chat_{chat_id}/topic_{topic_id}/
НЕ в корень INGEST папки.
Используется core/topic_drive_oauth.py:_upload_file_sync или upload_file_to_topic.
engine_base.upload_artifact_to_drive — только для healthcheck и прямых тестов.
При создании нового топика папка создаётся автоматически через _ensure_folder.

### Retry upload правило (30.04.2026):
Если Drive упал → artifact → Telegram (TELEGRAM_ARTIFACT_FALLBACK_SENT в task_history)
core/upload_retry_queue.py (cron */10) → проверяет Drive → если живой → скачивает из TG → загружает в topic папку → уведомляет пользователя → DRIVE_RETRY_UPLOAD_OK в task_history

## §15. ПАТЧИ И ПРАВИЛА СЕССИИ 01.05.2026

### §15.1 Критические фиксы (все VERIFIED live-тестом)

**AI_LOGIC_FIX_V1** — `if ai_result is None: pass / else:` была перевёрнута.
Правило: `if ai_result is None:` → запускать `process_ai_task`. Иначе AI никогда не вызывался.

**AI_RESULT_INIT_V1** — `ai_result = None` обязательно в начале try-блока `_handle_in_progress`.
Без этого Python бросает UnboundLocalError если ни один if-блок не присвоил значение.

**SAVE_MEM_ALL_DONE_PATHS_V2** — `_save_memory` вызывается на ВСЕХ путях DONE:
- done_markers ветка (строка 2487)
- followup/file_success ветка (строка 2506)
- AWAITING_CONFIRMATION ветка (строка 2528)

**DAEMON_OAUTH_FIX_V1** — `telegram_daemon.py` строка 707: `upload_to_drive` заменён на
`upload_file_to_topic` (OAuth). Service Account → invalid_scope → 559 рестартов.

**INPUT_TYPE_DRIVE_FIX_V1** — `input_type = "drive_file"` объявляется в начале
`_handle_drive_file` чтобы не падать при вызове `_quality_gate_artifact`.

**SCOPE_FULL_V2** — `drive.file` → `drive` в `topic_drive_oauth.py` и
`drive_folder_resolver.py`. Scope `drive.file` не позволяет создавать папки.

**IMPORT_FIX_V1** — `core/topic_autodiscovery.py`: `from reply_sender` →
`from core.reply_sender`. Иначе падает при первом срабатывании 24h таймера.

**PORT_FIX_V1** — `archive_engine.py`: порт 8765 → 8091 (канон §1.1).

### §15.2 Сервисы — правило навсегда

ЗАПРЕЩЕНО оставлять сервисы с `Restart=always` без файла скрипта.
При обнаружении зомби-сервиса — `systemctl stop + disable` И `rm unit-файл` И
`systemctl daemon-reload`. Только удаление unit-файла гарантирует невозврат.

Зомби-сервисы 01.05.2026 — удалены навсегда:
- areal-automation-daemon (run_automation_daemon.py — не существовал)
- areal-email-ingress (email_ingress.py — не существовал)
- areal-memory-import (memory_importer_service.py — не существовал)
- areal-memory-router (memory_router_service.py — не существовал)

### §15.3 Архитектура памяти (уточнение)

Три слоя памяти:
1. `_save_memory` → `memory.db` напрямую после DONE (краткосрочная + task_summary)
2. `archive_engine` Stage 6 → `memory_api` порт 8091 → `memory.db` (долгосрочная)
3. `archive_distributor` → `timeline.jsonl` → `memory.db` по топикам (историческая)

Чтение при каждом запросе: `_load_archive_context` → `_load_archive_for_topic` →
релевантные записи по ключевым словам запроса.

DONE → ARCHIVED через 168 часов (7 дней) автоматически.

### §15.4 Топики — правило

11 топиков синхронизированы в `data/topics/{id}/meta.json` через TOPIC_SYNC_FULL_V1.
`TOPIC_META_LOADER_WIRED = True` — оркестр знает название и направление каждого топика.
Новый топик → `topic_autodiscovery.py` → auto-detect direction → создать папку → 24h → спросить название.


## §16. ЕДИНЫЙ КАНОН — CONFIRM/VOICE/ФАЙЛОВЫЙ ПРИЁМ/ТОПИКИ
### Дата: 01.05.2026

### §16.1 ГОЛОС = ТЕКСТ
voice → STT → "[VOICE] текст" → идентично тексту. [VOICE] да = текстовое "да".

### §16.2 ACTIVE TASK RESOLVER — до создания задачи
ШАГ 1. reply на bot_message_id → контекст той задачи
ШАГ 2. AWAITING_CONFIRMATION → "да/ок/+" → DONE | "нет/правки" → WAITING_CLARIFICATION
ШАГ 3. WAITING_CLARIFICATION → любой ответ → IN_PROGRESS
ШАГ 4. Intent: FINISH > CANCEL > CONFIRM > REVISION > TASK > SEARCH > CHAT
Короткие слова НЕ создают задачу без AWAITING_CONFIRMATION в топике.

### §16.3 AWAITING_CONFIRMATION — только если результат реальный
ЗАПРЕЩЕНО если: "ожидает анализа"/"скачан"/"ошибка"/len<100
Файловая задача — только если есть валидный артефакт в Drive.

### §16.4 INTAKE_OFFER_ACTIONS
Файл БЕЗ caption → REPLY на то сообщение с файлом (telegram_message_id) → меню → NEEDS_CONTEXT → ждём → FILE_CHOICE_PARSED → IN_PROGRESS
Файл С caption → сразу IN_PROGRESS.
Source Guard: telegram→обработка | google_drive→CANCELLED | other→CANCELLED
Drive упал → Telegram fallback → cron retry 10 мин → DRIVE_RETRY_UPLOAD_OK

### §16.5 ЛОГИКА ПО ТОПИКАМ
ОБЫЧНЫЕ (topic_11,794,961,4569,6104): файл → REPLY → меню → выбор → engine → Drive

ТЕХНИЧЕСКИЕ — своя логика ВМЕСТО общего меню:
topic_2  СТРОЙКА: PDF/XLSX/фото → estimate_engine → Excel =C*D =SUM → Drive. LLM не считает — Python. Без таблицы → FAILED:ESTIMATE_EMPTY_RESULT.
topic_5  ТЕХНАДЗОР: фото → Gemini → норма СП/ГОСТ → DOCX акт. PDF → дефекты тип|место|степень|норма|риск → DOCX. Без нормы → не выдумывать.
topic_210 ПРОЕКТИРОВАНИЕ: АР/КД/КЖ PDF → project_engine → структурная модель → DOCX+XLSX. НЕ OCR текст.
topic_500 ВЕБ ПОИСК: 14-этапный Perplexity → что/где/почему/риски. Без источника → UNVERIFIED.
topic_3008 КОДЫ МОЗГОВ: верификация параллельно. No Auto-Patch. Без кода → WAITING_CLARIFICATION.

### §16.6 DRIVE
AI_ORCHESTRA/chat_-1003725299009/topic_2,5,11,210,500,794,961,3008,4569,6104/
Новые → _ensure_folder автоматически.

### §16.7 ТРЕБУЕТ LIVE-ТЕСТА
Voice confirm | INTAKE_OFFER_ACTIONS | Estimate PDF→Excel | Technadzor фото→акт | DUPLICATE_GUARD | MULTI_FILE | LINK_INTAKE

---
## §17 ЖИВАЯ ПАМЯТЬ, ЛОГИКА ОТВЕТОВ, ФАЙЛЫ — КАНОН 01.05.2026

### §17.1 ТРИ СЛОЯ ПАМЯТИ
СЛОЙ 1 SHORT: core.db — _active_unfinished_context()
СЛОЙ 2 LONG: memory.db — _save_memory() после каждого DONE. Ключи: topic_N_assistant_output | topic_N_task_summary | topic_N_user_input
СЛОЙ 3 ARCHIVE: memory.db + timeline.jsonl — archive_engine → POST /archive. Ключи: topic_N_archive_TASKID. Timeline пишется через TELEGRAM_TIMELINE_APPEND_V1
ИЗОЛЯЦИЯ: chat_id + topic_id — всегда оба. Чужие топики запрещены.

### §17.2 ПОРЯДОК _handle_new
ШАГ 0: HEALTHCHECK_GUARD → CANCELLED
ШАГ 1: ACTIVE_TASK_RESOLVER — reply/confirm/revision/intent
ШАГ 2: MEMORY_QUERY_GUARD_V1 — "что обсуждали/делали/было/неделю назад/апреля/напомни/помнишь" → archive_context → DeepSeek → DONE (не попадает в FULLFIX_10)
ШАГ 3: FULLFIX_16 — короткие статус-запросы ≤35 символов
ШАГ 4: FULLFIX_14/13A — estimate/technadzor
ШАГ 5: FULLFIX_19 — project guard
ШАГ 6: FULLFIX_10 — project/estimate engine
ШАГ 7: AI_ROUTER — DeepSeek + полный контекст памяти

### §17.3 ФАЙЛОВЫЙ ПРИЁМ
Без caption → меню → NEEDS_CONTEXT → reply → engine
С caption → сразу IN_PROGRESS
Source guard ДО create_task: google_drive/healthcheck → CANCELLED
Voice → STT → "[VOICE] текст" — идентично тексту. На Drive не грузится.
Drive файл → DRIVE_FILE_MEMORY_INDEX_V1 → topic_N_file_TASKID в memory.db
Повторный файл → FILE_DUPLICATE_MEMORY_GUARD_V1 → "Файл уже есть"

### §17.4 WATCHDOG
AWAITING_CONFIRMATION > 30 мин → FAILED:CONFIRMATION_TIMEOUT
IN_PROGRESS > 15 мин по created_at → FAILED:EXECUTION_TIMEOUT (IN_PROGRESS_HARD_TIMEOUT_V1)
STALE_TIMEOUT = 600 сек по updated_at

### §17.5 ПАТЧИ 01.05.2026
MEMORY_QUERY_GUARD_V1 | IN_PROGRESS_HARD_TIMEOUT_V1 | ARCHIVE_DEDUP_BY_KEY_V1
DRIVE_FILE_MEMORY_INDEX_V1 | FILE_DUPLICATE_MEMORY_GUARD_V1
TELEGRAM_TIMELINE_APPEND_V1 | LIVE_MEMORY_HELPERS_V1

### §17.6 НЕ РЕАЛИЗОВАНО
Drive содержимое файлов → автоиндексация в memory.db
Telegram история → автосинхронизация
