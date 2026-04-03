КАНОНИЧЕСКИЙ КОНТЕКСТ AREAL-NEVA CORE

1. ЦЕЛЬ СИСТЕМЫ

Оркестр задач server-first
Любой вход идёт через сервер
Источники:
- Telegram
- Gmail / IMAP
- Google Drive
- лиды / CRM
- automation / reminders / follow-up

Система должна:
- принять вход
- превратить во внутреннюю task
- провести через state machine
- передать в agent / pipeline
- вернуть результат
- не терять контекст по topic
- напоминать о зависших задачах, письмах и правилах автоматизации

2. ГЛАВНЫЙ ПРИНЦИП

Никаких отдельных “самодельных” контуров
Всё должно идти через одно ядро

То есть:
- любой watcher
- любой daemon
- любое напоминание
- любое письмо
- любой лид

в конце обязаны приходить к одному и тому же:
- create_task(...)
- transition_task(..., "INTAKE", ...)

3. ЧТО УЖЕ СОГЛАСОВАНО И ЗАФИКСИРОВАНО

Ядро
- SQLite
- BEGIN IMMEDIATE
- один shared connection
- _write_lock = asyncio.Lock()
- все записи только через transaction()
- Python управляет updated_at
- state machine обязательна

Основные таблицы
- tasks
- artifacts
- state_transitions
- context_sessions
- pinned_messages
- agent_executions
- leads_log
- automation_rules
- automation_events
- followup_state

Topic-aware логика
- каждый Telegram topic = отдельный context
- максимум 1 активная task на topic
- новый topic должен сразу инициализироваться
- новое сообщение в новом topic должно создавать task
- ответ в topic должен идти обратно в тот же thread

Automation layer
- напоминания по расписанию
- follow-up по письмам / задачам
- automation daemon не шлёт сообщения напрямую
- daemon создаёт task, а дальше ядро обрабатывает её как обычную задачу

Lead / Email / Drive
- email ingest создаёт task
- drive ingest создаёт task
- lead ingest создаёт task
- всё упирается в общий pipeline

4. ЧЕГО ДЕЛАТЬ НЕЛЬЗЯ
- нельзя писать отдельную бизнес-логику в Telegram handler
- нельзя делать asyncio.run() внутри уже работающего loop
- нельзя делать sync I/O внутри async worker без to_thread / executor
- нельзя отправлять automation уведомления напрямую в Telegram в обход task core
- нельзя держать несколько разных версий schema.sql, db.py, router.py
- нельзя плодить несколько “канонов” одного и того же файла

5. ГЛАВНЫЕ ИНВАРИАНТЫ

Это нельзя ломать
- один _conn на процесс
- один _write_lock на запись
- transaction() только через BEGIN IMMEDIATE
- все state transitions пишутся в лог
- context_sessions уникален по (chat_id, topic_id)
- followup_state уникален по (source, external_id)
- automation_rules живёт в БД, не в памяти
- новый task после системного срабатывания должен перейти в INTAKE

6. ЧТО БЫЛО ГЛАВНОЙ ПРОБЛЕМОЙ В ПРЕДЫДУЩИХ ИТЕРАЦИЯХ

Проблема была не в архитектуре
Проблема была в том, что мы поверх старых версий файлов писали новые куски и получали конфликтующие ревизии

Поэтому теперь SSOT по коду должен быть от этих 3 файлов:
1. schema.sql
2. core/db.py
3. core/router.py

Все остальные файлы обязаны подчиняться именно этим контрактам

7. СПИСОК 60 БЛОКОВ В СМЫСЛОВОМ ВИДЕ

Блоки 1–10
- schema
- db
- redis state
- state machine
- task creation
- context
- delivery base
- retry
- startup recovery
- smoke tests

Блоки 11–20
- email ingress
- drive ingest
- drive engine
- router integration
- lead ingest
- telegram lead hook
- email lead hook
- lead normalization
- CRM async engine
- lead pipeline

Блоки 21–30
- agent contracts
- agents registry
- worker integration
- lead storage
- Google Sheets export
- lead analytics
- Telegram topic utils
- topic context
- topic ingress
- topic auto reply

Блоки 31–40
- telegram sender
- follow-up basics
- topic/db patch
- active task binding
- no duplicate topic task
- reply routing
- delivery fallback
- local file send
- DLQ
- recovery refinements

Блоки 41–50
- lead enrich
- dedup
- rate limit
- lead storage fixes
- sheets fixes
- analytics fixes
- topic create fixes
- topic handler fixes
- topic integration
- canonical topic flow

Блоки 51–60
- automation schema
- automation engine
- scheduler
- gmail watcher
- followup watcher
- telegram reminder sender
- router automation trigger
- daemon integration
- followup dispatch
- final automation layer

КАНОНИЧЕСКИЙ ФАЙЛ 1
/root/.areal-neva-core/schema.sql

КАНОНИЧЕСКИЙ ФАЙЛ 2
/root/.areal-neva-core/core/db.py

КАНОНИЧЕСКИЙ ФАЙЛ 3
/root/.areal-neva-core/core/router.py

ДОПОЛНИТЕЛЬНОЕ КОРОТКОЕ ТЗ

Работаем только от этих трёх канонических файлов
Все остальные файлы должны быть совместимы именно с ними, а не со старыми версиями

Остальные обязательные слои поверх канона
- core/automation_engine.py
- core/automation_daemon.py
- core/topic_utils.py
- core/topic_context.py
- core/topic_ingress.py
- core/topic_auto_reply.py
- core/telegram_sender.py
- delivery.py
- email_ingress.py
- drive_ingest.py
- lead_ingest.py
- lead_pipeline.py
- crm_engine.py
- task_worker.py

Главное требование

Не генерить новые альтернативные версии schema.sql, db.py, router.py
Только расширять систему вокруг этих контрактов

РИСКИ, КОТОРЫЕ НУЖНО ДОПРОВЕРИТЬ
1. Совместимость task_worker.py с async route_task
2. Совместимость delivery.py с текущим artifacts
3. Совместимость automation_daemon.py с transition_task(..., "INTAKE", ...)
4. Корректность Telegram topic integration
5. Корректность Gmail follow-up логики
6. Отсутствие asyncio.run() внутри уже живого loop
7. Отсутствие sync I/O внутри async без to_thread
8. Отсутствие второй версии db.py в проекте
9. Отсутствие второй версии router.py в проекте
10. Отсутствие расхождения между реальным schema.sql и используемыми полями
