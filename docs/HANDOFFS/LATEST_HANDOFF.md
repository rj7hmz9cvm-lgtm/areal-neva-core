# LATEST_HANDOFF — 30.04.2026 05:40 MSK FINAL

## СЕРВЕР
IP: 89.22.225.136 | Base: /root/.areal-neva-core
Services: areal-task-worker ACTIVE | telegram-ingress ACTIVE | areal-memory-api ACTIVE

## ВСЕ ПАТЧИ СЕССИИ 30.04.2026 — ФИНАЛЬНЫЙ СТАТУС

| Патч | Файл | Статус |
|---|---|---|
| PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL | task_worker.py | VERIFIED ✅ |
| PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_WORKER_PICK_BEFORE_STALE_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FIX_PFIN3_MENU_SHADOW_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FILE_CHOICE_PRIORITY_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FILE_PARENT_STRICT_OPEN_ONLY_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_ENGINE_BASE_RESTORE_SA_UPLOAD_V1 | core/engine_base.py | VERIFIED ✅ |
| PATCH_DRIVE_DIRECT_OAUTH_V1 | core/engine_base.py | VERIFIED ✅ |
| PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_DOWNLOAD_OAUTH_V1 | task_worker.py | INSTALLED |
| PATCH_SOURCE_GUARD_V1 | task_worker.py | INSTALLED |
| PATCH_FILE_ERROR_RETRY_V1 | task_worker.py | INSTALLED |
| PATCH_DRIVE_BOTMSG_SAVE_V1 | task_worker.py | INSTALLED |
| PATCH_DRIVE_DOWNLOAD_FAIL_MSG_V1 | task_worker.py | INSTALLED |
| PATCH_CRASH_BOTMSG_V1 | task_worker.py | INSTALLED |
| PATCH_RETRY_TG_MSG_V1 | task_worker.py | INSTALLED |
| PATCH_RETRY_TOPIC_FOLDER_V1 | core/upload_retry_queue.py | VERIFIED ✅ |
| PATCH_HC_NO_UPLOAD | core/upload_retry_queue.py | INSTALLED |
| PATCH_DAEMON_OAUTH_OVERRIDE_V1 | systemd telegram-ingress | VERIFIED ✅ |
| PATCH_DAEMON_USE_OAUTH_V1 | telegram_daemon.py | INSTALLED |
| PATCH_VOICE_OAUTH_V1 | telegram_daemon.py | INSTALLED |
| PATCH_SCOPE_FULL_V1 | core/topic_drive_oauth.py + drive_folder_resolver.py + google_io.py | VERIFIED ✅ |
| PATCH_DUPLICATE_GUARD_V1 | task_worker.py | INSTALLED |
| PATCH_MULTI_FILE_INTAKE_V1 | task_worker.py | INSTALLED |
| PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1 | task_worker.py | INSTALLED |
| §0.11 САМОПРОВЕРКА AI | docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md | VERIFIED ✅ |
| Stale tasks cleanup | data/core.db | DONE ✅ |

## VERIFIED LIVE TESTS (30.04.2026)

- drive_file NEW → NEEDS_CONTEXT → меню по topic_id ✅
- reply/voice choice → FILE_CHOICE_PARSED → IN_PROGRESS ✅
- estimate engine → локальный artifact ✅
- Drive upload через OAuth → UPLOAD_OK ✅
- Telegram fallback при упавшем Drive ✅
- upload_retry_queue → cron 10min → восстанавливает Drive ✅
- retry загружает в topic папку (не INGEST) ✅
- OAuth scope=drive → PATCH_SCOPE_FULL_V1 → invalid_scope исчез ✅
- daemon OAuth через override.conf ✅
- daemon использует upload_file_to_topic (не upload_to_drive) ✅
- voice upload через OAuth ✅
- engine_base.py восстановлен ✅
- FILE_PARENT_STRICT работает ✅
- topic_id=0 не цепляет чужие задачи ✅

## КЛЮЧЕВЫЕ РЕШЕНИЯ СЕССИИ (хронология)

1. **OAuth app в Production** — refresh_token не протухает
2. **engine_base.py восстановлен** из bak (был удалён)
3. **Direct OAuth** заменил Service Account (storageQuotaExceeded)
4. **Telegram fallback** если Drive упал
5. **upload_retry_queue** — cron 10min восстанавливает Drive из TG
6. **retry в topic папку** — не INGEST корень
7. **healthcheck через list API** — не upload (избегаем INGEST загрязнения)
8. **Source guard** — файлы не из telegram → CANCELLED
9. **File error retry** — reply на ошибку → перезапуск файла
10. **Расширенный retry** — поиск по bot_message_id + reply_to + telegram_message_id
11. **Crash bot_message_id save** — при крашe сохранять id для retry
12. **Daemon OAuth override** — добавлены OAuth переменные в systemd
13. **Daemon use OAuth** — заменил upload_to_drive на upload_file_to_topic
14. **Voice OAuth** — voice через upload_file_to_topic
15. **Scope full drive** — заменил drive.file на drive в 3 файлах (РЕШИЛ invalid_scope)

## АРХИТЕКТУРА (финальная)

### Drive Upload Chain
```
Telegram message → daemon → upload_file_to_topic (OAuth, scope=drive) → topic папка
                                          ↓ если упал
                          create_task drive_file → task_worker
                                          ↓
                              _handle_drive_file → analyze
                                          ↓
                          engine_base.upload_artifact_to_drive (OAuth)
                                          ↓ если упал
                          Telegram sendDocument fallback
                                          ↓ TELEGRAM_ARTIFACT_FALLBACK_SENT
                          cron upload_retry_queue (10min)
                                          ↓ Drive alive?
                          скачать из TG → загрузить в topic папку → DRIVE_RETRY_UPLOAD_OK
```

### Folder Structure
```
AI_ORCHESTRA/
├── chat_-1003725299009/
│   ├── topic_0/   (ЧАТ ЗАДАЧ)
│   ├── topic_2/   (СТРОЙКА)
│   ├── topic_5/   (ТЕХНАДЗОР)
│   ├── topic_210/ (ПРОЕКТИРОВАНИЕ)
│   └── ...
```

При создании нового топика папка создаётся автоматически через `_ensure_folder`.

### Retry Logic
1. Reply на сообщение бота с ошибкой → ищет parent task по:
   - bot_message_id == reply_to
   - reply_to_message_id == reply_to
   - raw_input.telegram_message_id == reply_to
2. Если parent FAILED/AWAITING_CONFIRMATION/CANCELLED + result содержит "ошибка/не удалась"
3. Переводит parent в NEW → worker обрабатывает заново

### Source Guard
- source=telegram → обработка
- source=google_drive → CANCELLED (системный мусор)
- source=other → CANCELLED

## CRON JOBS

```
*/10 * * * * core/upload_retry_queue.py — retry Drive upload из TG
*/30 * * * * tools/context_aggregator.py — обновление контекста
```

## НЕ ЗАКРЫТО — P1

- Голосовой confirm при AWAITING_CONFIRMATION (telegram_daemon.py:601)
- Live-тест полного цикла после PATCH_SCOPE_FULL_V1
- Live-тест PATCH_FILE_ERROR_RETRY_V1 с реальным reply
- Live-тест PATCH_CRASH_BOTMSG_V1
- DUPLICATE_GUARD live-тест
- MULTI_FILE_INTAKE live-тест
- LINK_INTAKE live-тест

## НЕ ЗАКРЫТО — P2

- Смета PDF → Excel → Drive end-to-end
- КЖ PDF pipeline
- project_engine end-to-end
- Gemini vision
- Excel формулы =C2*D2 / =SUM
- Нормы СП/ГОСТ
- Multi-file один артефакт
- Memory/pin перед меню
- Google Sheets интеграция
- Шаблоны end-to-end
- MODEL_ROUTER, FALLBACK_CHAIN
- STT "Олег" — Whisper галлюцинирует имя

## КРИТИЧЕСКИЕ УРОКИ СЕССИИ

1. **Service Account НЕ работает с My Drive** — нужен только OAuth
2. **Refresh token зависит от scope при выдаче** — если код просит scope шире/уже чем токен, падает invalid_scope
3. **systemd Environment не наследуется автоматически** — нужен override.conf для каждого сервиса
4. **bot_message_id критичен для retry** — без него reply не находит parent
5. **AI router цепляет stale задачи** — старые AWAITING_CONFIRMATION загрязняют контекст
6. **drive_ingest подхватывает healthcheck файлы** — поэтому healthcheck через list API


## ОБНОВЛЕНИЕ 30.04.2026 10:00

### Новые баги выявлены в сессии (live наблюдение)

**BUG_CONFIRM_UNFINISHED** — AWAITING_CONFIRMATION без реального результата
- task_worker.py строки 2068-2075
- ТЗ: PATCH_CONFIRM_ONLY_ON_DONE_V1 в NOT_CLOSED

**BUG_TEMPLATE_NO_STRUCT** — шаблон = OCR текст вместо структурной модели
- core/artifact_pipeline.py — intent игнорируется
- core/template_manager.py — не используется
- ТЗ: PATCH_TEMPLATE_INTENT_V1 в NOT_CLOSED

### Факт из live БД topic=210
АР/КД/КЖ PDF файлы обрабатывались как "document" → OCR текст → "Сводка по документу"
Пользователь ожидал: структурную модель проекта с составом листов, марками, параметрами

## ОБНОВЛЕНИЕ 30.04.2026 10:30 — FULLFIX_01_CANON_CLOSE_CORE VERIFIED

### Патчи VERIFIED live-тестом:

| Патч | Файл | Статус |
|---|---|---|
| PATCH_TEMPLATE_MODEL_EXTRACTOR_V1 | core/project_engine.py | VERIFIED ✅ |
| PATCH_PROJECT_TEMPLATE_STORAGE_V1 | core/template_manager.py | VERIFIED ✅ |
| PATCH_TEMPLATE_INTENT_BRANCH_V1 | core/artifact_pipeline.py | VERIFIED ✅ |
| PATCH_CONFIRM_ONLY_ON_DONE_V1 | task_worker.py строки 2073+ | VERIFIED ✅ |
| PATCH_CONFIRM_GUARD_C_V1 | task_worker.py строка 1711 | VERIFIED ✅ |

### Live-тест 30.04 10:09

```
Файл: ПРОЕКТ КД кровля 5.pdf → topic_id=210
Task: 2a249e66-8399-4994-8211-dcad82496f18
State: AWAITING_CONFIRMATION
Result: PROJECT_TEMPLATE_MODEL создан
Раздел: АР
Структура: план, расчет, Фасады, Разрез, План
Размеры мм: 940, 730, 2025, 16940, 10730, 360, 2001...
```

### Что закрыто FULLFIX_01:
- PDF проекта → PROJECT_TEMPLATE_MODEL (не OCR summary) ✅
- AWAITING_CONFIRMATION только при валидном результате ✅
- "Доволен результатом?" не показывается при ошибке/пустом result ✅
- template_manager сохраняет модель в data/project_templates/ ✅

### Что осталось не идеальным (следующий проход):
- project_type определяется неточно (КД файл определён как АР)
- Состав листов (0) — марки листов не всегда извлекаются
- Голосовой confirm при AWAITING_CONFIRMATION — не закрыт
