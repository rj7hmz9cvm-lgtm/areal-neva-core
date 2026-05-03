# ORCHESTRA_FULL_CONTEXT_PART_001
generated_at_utc: 2026-05-03T10:06:29.912497+00:00
git_sha_before_commit: a57325c6341abf3a627bed7ecf628fd7b89310ad
part: 1/7


====================================================================================================
BEGIN_FILE: docs/HANDOFFS/LATEST_HANDOFF.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ddca1b3513c29f6dbcd12e42d21e6b52a182b80be13aa083d17ffeca8fb13cf4
====================================================================================================
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

---
# HANDOFF 30.04.2026 — FULLFIX_02 SESSION

## STATE
- areal-task-worker: active | telegram-ingress: active | areal-memory-api: active
- DB ORDER: использовать ORDER BY rowid DESC

## VERIFIED THIS SESSION
- FULLFIX_02_BC: project_type КД из filename ✅, sheet_register fallback ✅
- FULLFIX_01: PROJECT_TEMPLATE_MODEL создан ✅

## INSTALLED, AWAITING LIVE TEST
- FULLFIX_02_DA: neg bind + false confirm guard + voice negative
- FULLFIX_02_E: negative confirm all paths (NOT YET RUN)

## CRITICAL NEXT ACTIONS
1. Запустить FULLFIX_02_E
2. Live: "переделай" → "Хорошо, доработаю"
3. Live: голос "да" при AWAITING_CONFIRMATION → DONE
4. Live: estimate PDF → xlsx → Drive
# HANDOFF 01.05.2026 — ПОЛНАЯ СЕССИЯ ВОССТАНОВЛЕНИЯ

## СЕРВЕР
IP: 89.22.225.136 | Base: /root/.areal-neva-core
Services: areal-task-worker ACTIVE restarts=0 | telegram-ingress ACTIVE restarts=0 | areal-memory-api ACTIVE

## ЧТО БЫЛО СЛОМАНО И ПОЧИНЕНО

| Патч | Файл | Проблема | Статус |
|---|---|---|---|
| AI_LOGIC_FIX_V1 | task_worker.py | if/else перевёрнут — AI не вызывался | VERIFIED ✅ |
| AI_RESULT_INIT_V1 | task_worker.py | UnboundLocalError ai_result | VERIFIED ✅ |
| SAVE_MEM_ALL_DONE_PATHS_V2 | task_worker.py | _save_memory не вызывалась | VERIFIED ✅ |
| DAEMON_OAUTH_FIX_V1 | telegram_daemon.py | upload_to_drive→upload_file_to_topic | VERIFIED ✅ |
| INPUT_TYPE_DRIVE_FIX_V1 | task_worker.py | input_type not defined в drive_file | VERIFIED ✅ |
| SCOPE_FULL_V2 | topic_drive_oauth.py + drive_folder_resolver.py | drive.file→drive | VERIFIED ✅ |
| PORT_FIX_V1 | archive_engine.py | порт 8765→8091 | VERIFIED ✅ |
| MEMORY_API_SERVER_V1 | core/memory_api_server.py | файл отсутствовал | VERIFIED ✅ |
| IMPORT_FIX_V1 | core/topic_autodiscovery.py | from reply_sender→from core.reply_sender | VERIFIED ✅ |
| ZOMBIE_UNITS_REMOVED | systemd | 4 unit-файла удалены навсегда | VERIFIED ✅ |
| TOPIC_META_LOADER_V1 | task_worker.py | топики знают себя | VERIFIED ✅ |
| HOTFIX_FILE_NAME_EARLY_V1 | task_worker.py | file_name до TASK_TYPE_DETECT | VERIFIED ✅ |

## СОСТОЯНИЕ БД
- FAILED: 2811 (исторические, не мешают)
- CANCELLED: 543
- ARCHIVED: 381
- DONE: 348
- AWAITING_CONFIRMATION: 19

## ПАМЯТЬ
- memory.db: 969 архивных записей по топикам
- save_memory_ok работает с 16:00 01.05.2026
- archive_distributor: ok=True

## ТОПИКИ (все 11 настроены)
topic_0=ЛИДЫ АМО | topic_2=СТРОЙКА | topic_5=ТЕХНАДЗОР | topic_11=ВИДЕОКОНТЕНТ
topic_210=ПРОЕКТИРОВАНИЕ | topic_500=ВЕБ ПОИСК | topic_794=НЕЙРОНКИ СОФТ ВПН ВПС
topic_961=АВТО ЗАПЧАСТИ | topic_3008=КОДЫ МОЗГОВ | topic_4569=ЛИДЫ РЕКЛАМА | topic_6104=РАБОТА ПОИСК

## LIVE TESTS PASSED
- СТРОЙКА: вспомнил сметы за 24ч с Drive ссылками ✅
- ТЕХНАДЗОР: вспомнил архивные функции чата ✅
- КОДЫ МОЗГОВ: ответил по контексту ✅
- Drive: ALIVE, retry queue чист ✅

## НЕ ЗАКРЫТО
- Voice confirm при AWAITING_CONFIRMATION
- Estimate PDF→Excel→Drive live-тест
- Technadzor фото→акт live-тест
- detect_intent() 1 arg warning

---
## ПРАВИЛО ПЕРЕД ПАТЧЕМ (добавлено 02.05.2026)

**ОБЯЗАТЕЛЬНО перед любым патчем затрагивающим result/msg/ответ пользователю:**
1. curl GitHub raw текущего файла
2. Найти все места формирования result/msg
3. Сравнить с каноном — что должно показываться пользователю
4. Только потом писать якорь и replace
5. Не писать патч из памяти

Причина: CLEAN_RESULT_TEXT_V1 — обнаружили что Engine:/MANIFEST:/системные ключи
попадали в ответ пользователю из sample_template_engine.py строки 533-545,
потому что не прочитали текущий код перед патчем.

## СЕССИЯ 02.05.2026

| Patch | Commit | Status |
|---|---:|---|
| ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4 | e370c53 | VERIFIED ✅ |
| ESTIMATE_SCENARIO_CLASSIFICATION_FIX_V1 | 04378dc | VERIFIED ✅ |
| SAMPLE_ACCEPT_DIALOG_CONTEXT_FIX_V1 | 3d148d9 | VERIFIED ✅ |
| DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1 | 4f0b15b | VERIFIED ✅ |
| DRIVE_AI_ORCHESTRA_ROOT_FOLDER_FINAL_CLEAN_V1 | 226769c | VERIFIED ✅ |
| AREAL_REFERENCE_FULL_MONOLITH_V1 | current | VERIFIED ✅ |

====================================================================================================
END_FILE: docs/HANDOFFS/LATEST_HANDOFF.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/REPORTS/NOT_CLOSED.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ccba2c9f7bff1eeda072acf7153815ff3d0a7db0d0fb4d3cb47771679dc049d1
====================================================================================================
# AREAL-NEVA ORCHESTRA — ПОЛНЫЙ ПЛАН ЗАКРЫТИЯ КАНОНА
# Версия: 30.04.2026 10:30 | Режим: FACT-ONLY
# Основание: live DB + LATEST_HANDOFF + NOT_CLOSED + chat_exports + live logs

---

## ФАКТЫ ИСТОЧНИКОВ (приоритет истины)

```
1. Живой сервер (logs/db) — АБСОЛЮТНЫЙ ПРИОРИТЕТ
2. LATEST_HANDOFF.md (30.04.2026 05:40 MSK)
3. NOT_CLOSED.md (30.04.2026 10:00)
4. VERIFIED chat_exports
5. ONE_SHARED_CONTEXT (обновлён 2026-04-30T06:30:01+00:00)
6. CANON_FINAL/01_SYSTEM_LOGIC_FULL.md
7. INSTALLED без live-test — НЕ считать рабочим
8. BROKEN/REJECTED/UNKNOWN — НЕ использовать как канон
```

---

## ЧТО VERIFIED ПО ФАКТАМ (LATEST_HANDOFF 30.04 05:40 + live тесты)

```
✅ PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL — task_worker.py
✅ PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1 — task_worker.py
✅ PATCH_WORKER_PICK_BEFORE_STALE_V1 — task_worker.py
✅ PATCH_FIX_PFIN3_MENU_SHADOW_V1 — task_worker.py
✅ PATCH_FILE_CHOICE_PRIORITY_V1 — task_worker.py
✅ PATCH_FILE_PARENT_STRICT_OPEN_ONLY_V1 — task_worker.py
✅ PATCH_ENGINE_BASE_RESTORE_SA_UPLOAD_V1 — core/engine_base.py
✅ PATCH_DRIVE_DIRECT_OAUTH_V1 — core/engine_base.py
✅ PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1 — task_worker.py
✅ PATCH_RETRY_TOPIC_FOLDER_V1 — core/upload_retry_queue.py
✅ PATCH_DAEMON_OAUTH_OVERRIDE_V1 — systemd telegram-ingress override.conf
✅ PATCH_SCOPE_FULL_V1 — topic_drive_oauth.py + drive_folder_resolver.py + google_io.py
✅ drive_file NEW → NEEDS_CONTEXT → меню по topic_id
✅ reply/voice choice → FILE_CHOICE_PARSED → IN_PROGRESS
✅ Drive upload через OAuth → UPLOAD_OK (live: 1KtspYzRv...)
✅ Telegram fallback при упавшем Drive
✅ upload_retry_queue → cron 10min → восстанавливает Drive
✅ daemon использует upload_file_to_topic (не upload_to_drive)
✅ voice upload через OAuth
✅ OAuth scope=drive везде
✅ bot: active | daemon: active | memory-api: active
```

---

## ЧТО INSTALLED НО НЕ VERIFIED (факт из NOT_CLOSED)

```
⚠️ PATCH_DOWNLOAD_OAUTH_V1 — task_worker.py
⚠️ PATCH_SOURCE_GUARD_V1 — task_worker.py
⚠️ PATCH_FILE_ERROR_RETRY_V1 — task_worker.py
⚠️ PATCH_DRIVE_BOTMSG_SAVE_V1 — task_worker.py
⚠️ PATCH_DRIVE_DOWNLOAD_FAIL_MSG_V1 — task_worker.py
⚠️ PATCH_CRASH_BOTMSG_V1 — task_worker.py
⚠️ PATCH_RETRY_TG_MSG_V1 — task_worker.py
⚠️ PATCH_HC_NO_UPLOAD — core/upload_retry_queue.py
⚠️ PATCH_DAEMON_USE_OAUTH_V1 — telegram_daemon.py
⚠️ PATCH_VOICE_OAUTH_V1 — telegram_daemon.py
⚠️ PATCH_DUPLICATE_GUARD_V1 — task_worker.py
⚠️ PATCH_MULTI_FILE_INTAKE_V1 — task_worker.py
⚠️ PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1 — task_worker.py
```

---

## ПОДТВЕРЖДЁННЫЕ БАГИ ИЗ LIVE DB (факт: topic=210 задачи 30.04)

### BUG_1: AWAITING_CONFIRMATION_WITHOUT_RESULT
```
Факт из task_worker.py строка 2070:
_update_task(conn, task_id, state="AWAITING_CONFIRMATION", result=result)
→ ставится ВСЕГДА, даже если result="Файл скачан, ожидает анализа"

Факт из live DB topic=210:
id=6e385bf1 result="Файл КЖ АК-М-160.pdf скачан, ожидает анализа" → CANCELLED
(был AWAITING_CONFIRMATION раньше)

Задача не выполнена, но бот спрашивал "Доволен результатом?"
```

### BUG_2: TEMPLATE_IS_OCR_TEXT_NOT_STRUCTURE
```
Факт из core/artifact_pipeline.py строки 294-360:
analyze_downloaded_file игнорирует user_text (intent).
Для любого PDF: _extract_pdf → текст → _build_word "Сводка по документу"

Факт из live DB topic=210:
id=cc9d2911 raw="АР АК-М-160.pdf" caption="Шаблон проекта"
result="GSPublisherVersion 0.89.100.100 Архитектурный раздел..."
= просто OCR текст, не структурная модель

id=7b287c50 raw="[VOICE] посмотри структуру КД и записал"
result="Структура проекта КД включает следующие основные этапы:..."
= DeepSeek выдумал описание, не извлёк из файла
```

### BUG_3: NEGATIVE_INPUT_NOT_REVISION_SIGNAL
```
Факт из live DB topic=210:
"И?" → создала новую text задачу → ответ про назначение чата
"Какой результат?" → создала новую text задачу → общий ответ
"Так нет результата" → создала новую text задачу → CANCELLED

Правильно должно быть: недовольство привязывается к parent task
```

### BUG_4: GENERIC_RESPONSE_AS_RESULT
```
Факт из live DB topic=210:
"Этот чат предназначен для проектирования..." — финал задачи
"Структура проекта КД включает этапы..." — финал задачи
"Файл содержит проект архитектурного раздела..." — финал задачи
"Выбор принят" без запуска engine — финал задачи
```

### BUG_5: PROJECT_ENGINE_ABSENT
```
Факт: find /root/.areal-neva-core -name '*project_engine*' → НЕ НАЙДЕН
core/artifact_pipeline.py не имеет ветки для intent=template
core/template_manager.py не используется в pipeline
```

---

## ПОЛНЫЙ ПЛАН ЗАКРЫТИЯ КАНОНА (порядок строго по приоритету)

### PASS 1 — PATCH_CONFIRM_ONLY_ON_DONE_V1
```
Файл: task_worker.py
Строки: 2068-2075 (PATCH_DRIVE_BOTMSG_SAVE_V1 блок)

Правило:
AWAITING_CONFIRMATION только если:
- result не содержит: "ожидает анализа", "Ошибка", "не удалась",
  "завершилась ошибкой", "недоступен", "анализирую", "будет готов",
  "предназначен для", "этапы", "структура проекта"
- len(result.strip()) > 100
- error_message пустой или None
- для file/project задачи есть artifact_path или drive_link

Если условие не выполнено:
- state = FAILED
- error_message = RESULT_NOT_READY
- НЕ отправлять "Доволен результатом?"

Acceptance: незавершённая задача → FAILED + "Не удалось обработать. Попробуй ещё раз."
```

### PASS 2 — PATCH_TEMPLATE_INTENT_V1
```
Файлы:
- core/artifact_pipeline.py — добавить ветку intent=template
- core/template_manager.py — хранение структурных моделей

Правило:
intent=template + PDF → project_engine.extract_template_model()
НЕ _build_word("Сводка по документу")

Минимальная PROJECT_TEMPLATE_MODEL:
{
  "project_type": "АР/КЖ/КД/КМ/КМД/КР",
  "source_files": [],
  "sheet_register": [],  // состав листов
  "marks": [],           // марки листов
  "sections": [],        // разделы
  "axes_grid": [],       // сетка осей
  "dimensions": [],      // габариты
  "levels": [],          // отметки
  "nodes": [],           // узлы
  "specifications": [],  // спецификации
  "materials": [],       // материалы
  "stamp_fields": [],    // поля штампа
  "variable_parameters": [],  // что меняется для нового проекта
  "output_documents": []      // что генерировать
}

Acceptance:
- АР/КД/КЖ PDF + "шаблон" → JSON модель + DOCX состав листов
- НЕ "файл содержит проект"
- НЕ "структура включает этапы"
```

### PASS 3 — ГОЛОСОВОЙ CONFIRM
```
Файл: telegram_daemon.py ~строка 601
Явное "да" от пользователя обязательно

[VOICE] да/нет при AWAITING_CONFIRMATION → confirm/reject
```

### PASS 4 — LIVE-ТЕСТЫ INSTALLED ПАТЧЕЙ
```
Перед патчем — тест, не повторный патч:

1. PATCH_FILE_ERROR_RETRY_V1:
   - reply голосом/текстом на сообщение с ошибкой
   - ожидание: "Перезапускаю обработку файла"

2. PATCH_CRASH_BOTMSG_V1:
   - файл который крашит → проверить bot_message_id в DB

3. PATCH_DUPLICATE_GUARD_V1:
   - отправить тот же файл дважды
   - ожидание: "Этот файл уже обрабатывался"

4. PATCH_MULTI_FILE_INTAKE_V1:
   - несколько файлов подряд
   - ожидание: один артефакт

5. PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1:
   - отправить https://... ссылку
   - ожидание: меню действий
```

### PASS 5 — ESTIMATE PDF → EXCEL → DRIVE
```
Файл: core/estimate_engine.py
Pipeline: PDF → pdfplumber → таблица → нормализация → openpyxl → Drive

Правила:
- LLM не считает цифры
- Python создаёт Excel
- Excel содержит формулы =C*D, =SUM
- без таблицы → FAILED, не выдуманная смета
```

### PASS 6 — КЖ PDF PIPELINE
```
Файл: core/artifact_pipeline.py + project_engine.py
КЖ = Конструкции железобетонные
Pipeline: PDF → extract_pdf → classify pages → structural_model → DOCX/XLSX
```

### PASS 7 — PROJECT_ENGINE END-TO-END
```
Файл: core/project_engine.py (создать)
После PASS 2 (template_manager готов)

Команда "сделай по шаблону..." →
- берёт сохранённый PROJECT_TEMPLATE_MODEL
- генерирует DOCX пояснительная записка
- генерирует XLSX спецификация
- возвращает Drive link
```

### PASS 8 — TECHNADZOR / GEMINI VISION
```
Файл: core/technadzor_engine.py
Фото дефекта → Gemini → описание → нормы СП/ГОСТ → DOCX акт → Drive
Если норма не найдена → "норма не подтверждена", не выдумывать
```

### PASS 9 — OCR TABLE → EXCEL
```
Файл: core/ocr_engine.py
Фото таблицы → Gemini/pytesseract → структура → Excel
Без структуры → FAILED
```

### PASS 10 — SEARCH QUALITY
```
Файл: task_worker.py + search pipeline
Результат обязан иметь: таблица, цена, ссылка, checked_at, риск
Без источника → UNVERIFIED
```

### PASS 11 — MODEL_ROUTER / FALLBACK_CHAIN
```
Файл: core/model_router.py (создать)
photo → Gemini | search → Perplexity | calculation → Python | final → DeepSeek
```

### PASS 12 — FINAL END-TO-END TEST
```
Обязательные тесты перед закрытием канона:
1. text chat → ответ → DONE
2. voice → STT → задача → результат
3. voice confirm → закрывает только AWAITING_CONFIRMATION
4. file без caption → меню
5. PDF смета → XLSX с формулами → Drive link
6. АР/КД/КЖ PDF → PROJECT_TEMPLATE_MODEL
7. фото дефекта → DOCX акт + нормы
8. reply на ошибку → перезапуск
9. topic isolation (210 не цепляет 2/5/500)
10. Drive fallback → TG → cron retry
11. дубль файла → duplicate guard
12. голая ссылка → меню
```

---

## GITHUB ISSUES СТАТУС (факт)

```
Issue #2 "Drive artifact upload contour":
- LATEST_HANDOFF говорит: VERIFIED (OAuth upload OK, engine_base restored)
- Статус: OBSOLETE_BY_LATEST_HANDOFF_30_04_2026
- Действие: закрыть как superseded
```

---

## DB SCHEMA ФАКТ (из live PRAGMA)

```sql
tasks:        id, state, topic_id, input_type, raw_input, result,
              error_message, bot_message_id, reply_to_message_id,
              chat_id, created_at, updated_at
task_history: id, task_id, action, created_at
```

---

## CRON ФАКТ (из live crontab)

```
*/10 * * * * upload_retry_queue.py
*/30 * * * * context_aggregator.py
*/5  * * * * monitor_jobs.py
0 */6 * * *  auto_memory_dump.sh
```

---

## ЗАПРЕЩЁННЫЕ ОТВЕТЫ КАК ФИНАЛ (факт из live DB)

```
❌ "Файл скачан, ожидает анализа"
❌ "Структура проекта включает следующие основные этапы"
❌ "Файл содержит проект архитектурного раздела"
❌ "Этот чат предназначен для..."
❌ "Анализирую, результат будет готов"
❌ "Проверяю доступные файлы"
❌ "Выбор принят" без запуска engine
❌ "Какие именно файлы вас интересуют?"
```

---

## ПРАВИЛО КАНОНА ДЛЯ СЛЕДУЮЩЕГО ЧАТА

```
1. Читать: ONE_SHARED_CONTEXT → LATEST_HANDOFF → NOT_CLOSED
2. Приоритет истины: live server > HANDOFF > NOT_CLOSED > OLD_EXPORTS
3. INSTALLED ≠ работает | VERIFIED = работает
4. BROKEN/REJECTED/UNKNOWN — не использовать
5. Патч только с явного "да"
6. Диагностика перед патчем
7. Самопроверка после написания кода (§0.11)
8. Written code ≠ installed | Installed ≠ verified | Verified = live test passed
```


---

## MASTER CLOSURE PLAN

Полный план закрытия в 7 проходах: `docs/REPORTS/MASTER_CLOSURE_PLAN.md`

**Порядок:**
1. PATCH_CONFIRM_ONLY_ON_DONE_V1 — task_worker.py 2070-2075
2. PATCH_TEMPLATE_INTENT_V1 — artifact_pipeline + template_manager
3. Voice confirm — telegram_daemon.py с явного «да»
4. Live-тесты INSTALLED патчей — без нового кода
5. Estimate contour — estimate_engine
6. Technadzor contour — technadzor_engine
7. Project engine — после template_manager

**Issue #2:** OBSOLETE — superseded by PATCH_SCOPE_FULL_V1 + LATEST_HANDOFF 30.04.2026

---

## ОБНОВЛЕНИЕ 30.04.2026 10:30 — FULLFIX_01 VERIFIED

### ЗАКРЫТО FULLFIX_01 (live-тест 10:09):

| Что | Файл | Статус |
|---|---|---|
| PROJECT_TEMPLATE_MODEL извлечение из PDF | core/project_engine.py | VERIFIED ✅ |
| template_manager хранение модели | core/template_manager.py | VERIFIED ✅ |
| artifact_pipeline ветка intent=template | core/artifact_pipeline.py | VERIFIED ✅ |
| AWAITING_CONFIRMATION guard (drive_file) | task_worker.py 2073+ | VERIFIED ✅ |
| AWAITING_CONFIRMATION guard (_handle_in_progress) | task_worker.py 1711 | VERIFIED ✅ |

### P1 — ОСТАЁТСЯ (следующий проход FULLFIX_02):

- Голосовой confirm при AWAITING_CONFIRMATION (telegram_daemon.py ~601)
- project_type определение неточное (КД → АР) — улучшить regex
- Состав листов не извлекается если марки не в тексте PDF
- Estimate PDF → Excel → Drive end-to-end
- КЖ PDF pipeline
- Live-тесты: DUPLICATE_GUARD, MULTI_FILE, LINK_INTAKE, FILE_ERROR_RETRY

### FULLFIX_02 цель:
- voice confirm (telegram_daemon.py с явного "да")
- улучшить extract_template_model_from_text (КД/КЖ детектор)
- estimate_engine → Excel с формулами

---
# FULLFIX_02 — СЕССИЯ 30.04.2026

## VERIFIED (live-тест подтверждён)

### FULLFIX_02_BC — project_engine.py + task_worker.py
- Файл: core/project_engine.py
- Патчи: FULLFIX_02_B1 (filename-first detect_section), FULLFIX_02_B2 (filename-first project_type, КД/КЖ before АР), FULLFIX_02_B3 (sheet_register fallback из sections)
- Файл: task_worker.py
- Патч: FULLFIX_02_C_NEGATIVE_PARENT_BIND
- BACKUP: 20260430_104019
- LIVE DB: задачи 99f8f617, 18aec40e → Раздел: КД, Состав листов (7) и (1) ✅

## INSTALLED, NOT VERIFIED

### FULLFIX_02_DA — task_worker.py + telegram_daemon.py
- BACKUP: 20260430_105448, SYNTAX_OK, services active
- D_HELPERS: _ff2_is_negative_user_signal, _ff2_allow_final_result
- D_NO_FALSE_CONFIRM: блок финала без артефакта → FAILED
- A_VOICE_NEGATIVE: расширенный negative check в _handle_control_text
- NOT VERIFIED: neg:routed не появился после live теста

### FULLFIX_02_E — telegram_daemon.py (DESIGNED, NOT YET RUN)
- Цель: "переделай" → "Хорошо, доработаю. Подтверждение снято"
- Устраняет: "Уточните, что исправить"

## NOT CLOSED (код есть, live-тест не проводился)
- Смета PDF → Excel → Drive end-to-end
- КЖ PDF pipeline end-to-end
- project_engine end-to-end через Telegram
- Голосовой confirm при AWAITING_CONFIRMATION
- Дублирование задач x2
- PATCH_FILE_ERROR_RETRY_V1, PATCH_CRASH_BOTMSG_V1
- PATCH_DUPLICATE_AND_MULTIFILE_INTAKE_V1
- PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1
- monitor_jobs.py — файла нет
- SEARCH_MONOLITH_V1 — live-тест не проводился
- Нормы СП/ГОСТ в technadzor_engine

## FULLFIX_20_CODE_CLOSURE — 2026-04-30

### Закрыто кодом:
- A1: context_query send_reply_ex + message_thread_id=topic_id
- A2: multifile send_reply_ex + message_thread_id=topic_id
- B1: OCE memory save внутри create_estimate_files
- B2: active template headers из data/templates/estimate/ACTIVE__chat_*__topic_*.json
- C1: Gemini vision в process_defect_act_sync (asyncio.run с get_running_loop guard)
- C2: multifile merge PDF (pypdf + PIL) + Drive upload
- C3: upload_retry_queue while True loop + areal-upload-retry.service

### Pending live-тесты (код есть, Telegram не тестировался):
- template_intake: файл + "возьми как образец"
- defect_act: фото + "акт осмотра"
- multifile: "сводка по всем файлам"
- active_context_query: "ну что там / где смета"
- DWG pipeline end-to-end
- КЖ PDF pipeline end-to-end

---
## ЗАКРЫТО 2026-04-30 вечер

### FULLFIX_DIRECTION_KERNEL_STAGE_1 ✅ CLOSED
- core/work_item.py установлен
- core/direction_registry.py установлен
- config/directions.yaml 26 directions установлен
- task_worker.py wiring shadow mode
- 6/6 smoke tests OK
- GitHub: a8955bb

---
## ОТКРЫТО (новое) 2026-04-30

### P0 — areal-monitor-jobs zombie процессы
monitor_jobs.py накапливает дочерние процессы, не чистит их
100+ зомби → OOM → убивает task_worker
Нужен фикс: либо KillMode=control-group в systemd, либо фикс в monitor_jobs.py

### Stage 2 — Capability Router (следующий после monitor_jobs)

---
## ЗАКРЫТО 2026-04-30

### FULLFIX_DIRECTION_KERNEL_STAGE_1 ✅
WorkItem + DirectionRegistry + 26 directions + shadow wiring
GitHub: a8955bb, smoke 6/6

### monitor_jobs zombie fix ✅
KillMode=control-group — дочерние процессы убиваются при рестарте

---
## ОТКРЫТО

### Stage 2 — Capability Router (P1)
Берёт direction из payload, формирует execution_plan, shadow mode

---
## ЗАКРЫТО 2026-04-30 (финал сессии)

### Stage 2 Capability Router ✅ ef9b269
### Stage 3 Context Loader ✅ e52c1d8
### Stage 4 Quality Gate ✅ 14675cf
### Stage 5 Search Engine ✅ 15c8753
### Stage 6 Archive Engine ✅ 967b356
### Stage 7 Format Adapter ✅ e156253

---
## ОТКРЫТО (следующий приоритет)

### P1 — Live тест всей цепочки
Отправить задачу в бот, проверить что в логах идут все FULLFIX маркеры:
FULLFIX_DIRECTION_KERNEL_STAGE_1
FULLFIX_CAPABILITY_ROUTER_STAGE_2
FULLFIX_SEARCH_ENGINE_STAGE_5 (если поиск)
FULLFIX_CONTEXT_LOADER_STAGE_3
FULLFIX_QUALITY_GATE_STAGE_4
FULLFIX_ARCHIVE_ENGINE_STAGE_6
FULLFIX_FORMAT_ADAPTER_STAGE_7

### P2 — Подключение реального dispatch по execution_plan
Сейчас execution_plan формируется но не используется для маршрутизации.
Stage 4 dispatch: router.route() → вызов реального движка по engine из плана.

### P3 — memory_api /archive endpoint
Archive Engine пишет в POST /archive но endpoint не реализован в memory_api_server.py

---
## ОБНОВЛЕНИЕ 01.05.2026 — ИТОГИ СЕССИИ

### VERIFIED LIVE ТЕСТОМ 01.05.2026:
- AI_LOGIC_FIX_V1: DeepSeek вызывается корректно ✅
- SAVE_MEM: save_memory_ok topic=2,5,794,6104 в 16:00-16:01 ✅
- ARCHIVED: 381 задача в архиве ✅
- TOPICS: все 11 топиков знают себя ✅
- DRIVE: DRIVE_ALIVE PENDING_RETRY_COUNT=0 ✅
- ZOMBIES: 4 зомби-сервиса удалены навсегда ✅
- DAEMON: restarts=0 после DAEMON_OAUTH_FIX_V1 ✅

### ОСТАЁТСЯ НЕ ЗАКРЫТЫМ:
- ПРОХОД 3: Voice confirm при AWAITING_CONFIRMATION
- ПРОХОД 5: Estimate PDF→Excel→Drive (live-тест)
- ПРОХОД 6: Technadzor фото→акт (live-тест)
- ПРОХОД 7: Project engine end-to-end
- detect_intent() takes 1 arg — warning в FILE_INTAKE_ROUTER_V1
- AWAITING_CONFIRMATION: 19 задач — проверить не зависли ли

---
## ОБНОВЛЕНИЕ 01.05.2026 22:30 — LIVE ТЕСТЫ

### VERIFIED LIVE 01.05.2026:
- ТЕХНАДЗОР: вспомнил файл "ВОР проезды и площадки.xlsx" из архива ✅
- СТРОЙКА: вспомнил смету 55000 руб с Drive ссылками ✅
- Память (1714 записей) работает ✅
- /archive endpoint работает ✅

### БАГИ НАЙДЕННЫЕ LIVE:
- P1: task зависает в IN_PROGRESS и крутится каждые 2 сек — archive_engine пишет дубли в loop
- P1: СТРОЙКА: голос "три недели назад" → попадает в FULLFIX_10 project route вместо memory lookup
- P2: topic_6104 архив содержит только JSON метаданные без реального контента
- P2: Worker падает при ручном restart через systemd (traceback пуст, работает через авторестарт)

### ЕЩЁ НЕ ПРОВЕРЕНО:
- Файл в чате → бот говорит "этот файл уже есть" (DUPLICATE_GUARD)
- Voice "да" при AWAITING_CONFIRMATION → DONE
- Estimate PDF→Excel live тест с реальным файлом

---
## ОБНОВЛЕНИЕ 02.05.2026 — ПОЛНЫЙ СПИСОК НЕЗАКРЫТОГО (сессия 02.05)

### ЗАКРЫТО КОДОМ В ЭТОЙ СЕССИИ (верифицировано git + smoke):
- RESULT_VALIDATOR_FIX_V1: убраны false-positive BAD_RESULT_RE, MIN_RESULT_LEN 8→2 (e3c742d)
- CREATE_ESTIMATE_PRIORITY_NO_ROLLBACK_V1: явный запрос сметы → estimate engine до followup (b2a725b)
- CLEAN_ESTIMATE_USER_OUTPUT_AND_TOTAL_FIX_V2: чистый вывод без Engine/MANIFEST/tmp (756f307)
- RULE §0.5: READ→FIND→PATCH→COMPILE→RESTART→LOGS→PUSH в каноне (3538995)
- REAL_GAPS_CLOSE_V2: estimate validator, no-llm guard, strict template, region parser, async template (efa4832)
- IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1: hard 30min timeout по created_at (c5b4326)
- PROJECT_ENGINE_FALLBACK_SHEET_REGISTER_V1: fallback 8 листов КЖ без шаблона (09b0b36)
- PROJECT_PRIORITY_ROUTE_NO_ROLLBACK_V1: проект идёт выше сметы и file-followup (2faa8ea)
- FILE_INTAKE_KZH_INTENT_FIX_V1: КЖ/КД файлы → project, голый файл → уточнение (349aeed)
- PDF_SPEC_EXTRACTOR_STUB_V1: заглушка, воркер больше не падает (6b36da1)

### НЕ ЗАКРЫТО КОДОМ — ТРЕБУЕТ ПАТЧА:

#### P0 — БЛОКИРУЕТ ЖИВУЮ РАБОТУ:
1. REPLY_REPEAT_PARENT_TASK_V1
   "повтори" / "ещё раз" / "заново" без project_words → уходит в topic description
   Нужно: найти parent task в топике → взять raw_input → повторить в правильный движок
   Файл: task_worker.py, вставить ДО CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1

2. WEB_SEARCH_PRICE_ENRICHMENT_V1
   Пользователь: "принять Excel как образец, но цены на материалы брать из интернета"
   Нужно: при create_estimate_from_saved_template → для каждой позиции → web_search актуальной цены → подставить в smeta
   Файл: core/sample_template_engine.py + core/estimate_engine.py

3. CONTEXT_AWARE_FILE_INTAKE_V1
   Файл пришёл → бот не видит ТЗ написанное выше в чате → спрашивает "что делать?"
   Нужно: should_ask_clarification проверять последние 5 задач топика на project/estimate words
   Файл: core/file_intake_router.py

#### P1 — ФУНКЦИОНАЛЬНЫЕ ПРОБЕЛЫ:
4. PDF_SPEC_EXTRACTOR_REAL_V1
   Сейчас заглушка — PDF сметы/спецификации не парсятся
   Нужно: pdfplumber → извлечь таблицы → найти qty/unit/price → вернуть rows
   Файл: core/pdf_spec_extractor.py

5. PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1
   Проектный результат показывает Engine/MANIFEST/tmp пути пользователю
   Нужно: чистый вывод PDF/DXF/XLSX + ссылки Drive без системных ключей
   Файл: task_worker.py CREATE_PROJECT_PRIORITY_NO_ROLLBACK_V1

6. ARCHIVE_DUPLICATE_GUARD_V1
   Нет UNIQUE index на (chat_id, key) в memory.db → дубли накапливаются
   Нужно: CREATE UNIQUE INDEX + DELETE дублей
   Файл: tools/telegram_history_full_backfill.py + memory.db

7. XLSX_GOOGLE_SHEETS_FORMULA_VALUES_FIX_V1
   Google Sheets показывает формулы вместо значений при data_only=False
   Нужно: дублировать числовое значение рядом с формулой
   Файл: core/sample_template_engine.py _write_estimate_xlsx

#### P2 — СИСТЕМНОЕ:
8. DWG_CONVERTER_INSTALL_V1
   dwg2dxf/ODAFileConverter не установлен → DWG файлы только metadata
   Нужно: apt install или скачать ODAFileConverter

9. NORMATIVE_SOURCE_ENGINE_FULL_CLOSE_V1
   Только 3 записи без пунктов (СП 70, СП 63, ГОСТ 21.101) — все PARTIAL
   Нужно: реальная база с clause + source + confidence=CONFIRMED

#### ТОЛЬКО LIVE-ТЕСТ (код есть):
- Voice confirm при AWAITING_CONFIRMATION
- Estimate PDF→Excel→Drive реальным файлом
- Technadzor фото→акт реальным фото
- DWG через Telegram реальным файлом
- DUPLICATE_GUARD два одинаковых файла
- MULTI_FILE_INTAKE несколько файлов одной задачей
- LINK_INTAKE ссылка без файла

### НОВЫЕ ЗАДАЧИ ОТ ПОЛЬЗОВАТЕЛЯ (02.05.2026):
10. MULTI_FILE_TEMPLATE_INTAKE_V1
    Несколько Excel смет пришли → каждый сохранить как отдельный шаблон
    Сейчас: один активный шаблон на топик, остальные игнорируются

11. WEB_SEARCH_PRICE_ENRICHMENT_V1 (см. P0 п.2)
    При создании сметы по шаблону — цены материалов искать в интернете актуальные

---
## ОБНОВЛЕНИЕ 02.05.2026 13:40 — ПОСЛЕ eefeec0

### ЗАКРЫТО КОДОМ (979e1ec + eefeec0):
- CONTEXT_AWARE_FILE_INTAKE_V1 — pending intent перед файлами
- MULTI_FILE_TEMPLATE_INTAKE_V1 — batch шаблонов смет
- TELEGRAM_FILE_MEMORY_INDEX_V1 — индекс файлов + дубли
- WEB_SEARCH_PRICE_ENRICHMENT_V1 — цены из интернета через OpenRouter
- PRICE_CONFIRMATION_BEFORE_ESTIMATE_V1 — выбор цен перед финальной сметой
- PDF_SPEC_EXTRACTOR_REAL_V1 — реальный pdfplumber парсер
- ROOT_TMP_UPLOAD_GUARD_V1 — healthcheck больше не грузит tmp*.txt в Drive root
- DRIVE_CANON_FOLDER_RESOLVER_V1 — OAuth вместо Service Account, canonical layout
- DRIVE_CANON_SINGLE_FOLDER_PICK_V1 — детерминированный выбор папки

### НЕ ЗАКРЫТО КОДОМ (P0):
1. REPLY_REPEAT_PARENT_TASK_V1
   "повтори"/"ответишь?"/"ещё раз" → не цепляется к parent task
   DB факт: 152a73c3 FAILED/INVALID_RESULT_GATE, 6e3b7899 FAILED/FORBIDDEN_PHRASE

2. UNIFIED_USER_OUTPUT_SANITIZER_V1
   Нет единого sanitizer — Engine/MANIFEST/tmp/artifact_path могут утечь в ответ пользователю
   output_sanitizer.py не существует

3. PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1
   DB факт: "Сделай проект КЖ" → "Смета обработана"

4. PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1
   Проектный ответ может содержать Engine/MANIFEST/tmp пути

### НЕ ЗАКРЫТО КОДОМ (P1):
5. ARCHIVE_DUPLICATE_GUARD_V1 — нет UNIQUE index на (chat_id, key) в memory.db
6. XLSX_GOOGLE_SHEETS_FORMULA_VALUES_FIX_V1 — Sheets показывает формулы без значений
7. MEMORY_SCOPE_FULL_WIRING_V1 — маркер не найден
8. DWG_CONVERTER_INSTALL_V1 — системная зависимость

### ТОЛЬКО LIVE-ТЕСТ:
- Voice confirm при AWAITING_CONFIRMATION
- Batch смет-образцов live
- Дубль Telegram-файла live
- Web prices → выбор → XLSX/PDF live
- PDF spec extractor реальным файлом
- Project КЖ end-to-end без "Смета обработана"
- Новый Telegram файл → canonical Drive topic folder live

---
## АУДИТ 02.05.2026 14:00 — ПОЛНЫЙ СПИСОК НЕ ЗАКРЫТО КОДОМ

### ФАКТ ПО GITHUB main (68dfd30):

#### НЕ УСТАНОВЛЕНО КОДОМ — маркеры отсутствуют в GitHub:
1. ESTIMATE_PDF_TO_XLSX_FORMULA_V1
   estimate_engine.py существует, но нет create_estimate_xlsx_from_rows с =D*E =SUM
   Нужно: PDF → pdfplumber rows → XLSX формулами → Drive

2. TECHNADZOR_ACT_ENGINE_FULL_V1
   technadzor_engine.py существует (старый маркер), но нет полного акта
   Нужно: фото/файл → дефект → нормы СП/ГОСТ → DOCX → Drive

3. SP_GOST_NORM_RESOLVER_V1
   Нормы не должны выдумываться — если источник не подтверждён → "норма не подтверждена"

4. OCR_TABLE_TO_EXCEL_V1
   ocr_engine.py существует (старый маркер), нет нового контура
   Нужно: фото/скан таблицы → структура → Excel

5. MODEL_ROUTER_FALLBACK_CHAIN_V1
   model_router.py существует (старый маркер)
   Нужно: жёсткое разделение smeta/technadzor/project/memory/search

6. ARCHIVE_DUPLICATE_GUARD_V1
   archive_guard.py — файла нет вообще
   Нужно: task_id+content_hash guard против дублей архива

7. RUNTIME_TELEGRAM_FILE_CATALOG_V1
   runtime_file_catalog.py — файла нет
   Нужно: каждый новый Telegram-файл автоматически в каталог при приёме

8. FINAL_CLOSURE_ENGINE_V1
   final_closure_engine.py — файла нет
   Нужно: единый prehandle с voice_confirm, memory_query, pdf_estimate, technadzor, ocr

9. ABSOLUTE_CODE_CLOSURE_ALL_CONTOURS_V1
   task_worker hook — не установлен
   Нужно: хук ПОСЛЕ существующих P0 хуков, без дублирования voice_confirm

10. XLSX_GOOGLE_SHEETS_FORMULA_VALUES_FIX_V1
    XLSX создаются, но Google Sheets formula values не проверены

#### УСТАНОВЛЕНО КОДОМ (verified по GitHub):
- PENDING_INTENT_CLARIFICATION_V1 ✅
- PRICE_DECISION_BEFORE_WEB_SEARCH_V1 ✅
- REPLY_REPEAT_PARENT_TASK_V1 ✅
- PROJECT_ROUTE_FIX_NO_ESTIMATE_REGRESSION_V1 ✅
- UNIFIED_USER_OUTPUT_SANITIZER_V1 ✅
- ROOT_TMP_UPLOAD_GUARD_V1 ✅
- DRIVE_CANON_FOLDER_RESOLVER_V1 ✅
- FILE_INTAKE_KZH_INTENT_FIX_V1 ✅
- AGGREGATOR_PUSH_FAILURE_GUARD_V1 ✅
- PDF_SPEC_EXTRACTOR_REAL_V1 (маркер есть, import smoke OK) ✅

#### ТОЛЬКО LIVE-ТЕСТ (код есть, не verif):
- Voice confirm AWAITING_CONFIRMATION
- Reply "ответишь?" / "повтори" live
- Batch смет-образцов live
- Дубль Telegram-файла live
- Web prices → выбор → XLSX/PDF live
- Project КЖ end-to-end
- Technadzor фото → акт live
- DWG через Telegram
- Drive canonical topic folder live после eefeec0

#### ПРАВИЛА СЛЕДУЮЩЕГО ПАТЧА:
- НЕ трогать telegram_daemon.py без явного "да"
- НЕ дублировать VOICE_CONFIRM_AWAITING_V1 (уже строка 1405 task_worker.py)
- Новый hook ставить ПОСЛЕ FULL_TECH_CONTOUR_CLOSE_V1_WIRED, не перед ACTIVE_DIALOG
- Все новые файлы — только append/create, не перезапись рабочего кода

---
## ПРАВИЛО: VOICE_CONFIRM_BLOCKER (зафиксировано 02.05.2026)

После каждой записи `core/final_closure_engine.py` обязательно выполнять:

```bash
grep -nE "def handle_voice_confirm|def voice_confirm|VOICE_CONFIRM_AWAITING_V1|voice_confirm|handle_voice_confirm" core/final_closure_engine.py && exit 1
```

Правила:
- НЕ отключать проверку
- НЕ ослаблять проверку
- НЕ выносить её из блока
- НЕ разрешать строку VOICE_CONFIRM_AWAITING_V1 даже в диагностическом списке
- core/final_closure_engine.py должен быть полностью чистым от voice-confirm логики
- voice-confirm остаётся только в task_worker.py в VOICE_CONFIRM_AWAITING_V1 (строка ~1434)
- Правильный статус в отчёте: BLOCKER_KEPT (не FALSE_FORBIDDEN_LIST_REMOVED)
- Если GPT пишет FORBIDDEN_FUNCTIONS список с этими строками внутри файла — это баг патча

## TOPIC_ISOLATION_LIVE_TEST_PENDING_02052026

Статус: PENDING LIVE TEST

Проверить живым Telegram тестом:
- topic_2 не тянет проектные образцы topic_210
- topic_210 не тянет сметные артефакты как результат
- topic_5 не тянет КЖ/АР без прямой команды

## P0_LIVE_BUGS_CLOSE_V1_VERIFICATION

Статус: CODE INSTALLED

Закрыто кодом:
- PROJECT_INDEX_QUERY_CREATES_FILE
- TOPIC_CONTEXT_SWITCH
- SINGLE_CHAR_REPLY_NOT_PARENT_TASK
- PRICE_SEARCH_SINGLE_SOURCE
- PRICE_CHOICE_DETECT_EXPAND
- VOICE_CONTEXT_LOSS_IN_PRICE_FLOW
- WRONG_FILES_SHOWN_IN_TOPIC_2
- PDF_SPEC_EXTRACTOR_REAL_V1_PDFPLUMBER
- PROJECT_ENGINE_CLEAN_USER_OUTPUT_V1
- CONTEXT_AWARE_FILE_INTAKE_V1_DB_LOOKUP
- REAL_SEARCH_QUALITY_LOGIC_V1

Остаётся live-test:
- проверить topic_210: "какие образцы есть по АР/КЖ/КД" должен показать список без создания файла
- проверить topic_2: "В" и "вариант 2" после выбора цены должны создать XLSX/PDF
- проверить price search: минимум 2 разных домена или пометка об одном источнике
- проверить topic isolation: topic_2 не должен показывать КЖ/АР файлы topic_210 без прямого запроса

====================================================================================================
END_FILE: docs/REPORTS/NOT_CLOSED.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: dbd5f683361eafc258ab0822056f6c33f751e5581998dc420f79395d14863177
====================================================================================================
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
§0.5 Общий порядок любого патча:
READ CURRENT FILE → FIND CURRENT MARKERS → PATCH ONLY GAP → COMPILE → RESTART → LOGS → GIT PUSH
Каждый шаг обязателен. Пропуск = нарушение.

§0.5.1 Детальный порядок (8 шагов):
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

---
## §17 ПОЛНЫЙ КАНОН ЖИВОЙ ПАМЯТИ И ЛОГИКИ ОТВЕТОВ — 01.05.2026

### §17.1 ТРИ СЛОЯ ПАМЯТИ — ВСЕ ОБЯЗАТЕЛЬНЫ ПРИ КАЖДОМ ЗАПРОСЕ

СЛОЙ 1 SHORT (core.db):
  Текущие задачи + последние DONE за 24 часа
  Читается через: _active_unfinished_context()

СЛОЙ 2 LONG (memory.db):
  Факты после каждого DONE через _save_memory()
  Ключи: topic_N_assistant_output | topic_N_task_summary | topic_N_user_input
  Читается через: _load_memory_context(chat_id, topic_id)

СЛОЙ 3 ARCHIVE (memory.db + timeline.jsonl):
  Все DONE+ARCHIVED задачи за всё время
  Ключи: topic_N_archive_TASKID
  Читается через: _load_archive_context(chat_id, topic_id, user_text)
  Поиск по ключевым словам из запроса пользователя

ИЗОЛЯЦИЯ — ЖЕЛЕЗНО:
  chat_id + topic_id — всегда оба фильтра
  Данные из topic_2 НИКОГДА не попадают в topic_5
  Данные из topic_0 не попадают никуда

ЗАПИСЬ — ТОЛЬКО ПОСЛЕ DONE:
  _save_memory() → memory.db
  archive_engine.archive() → POST http://127.0.0.1:8091/archive → memory.db
  DONE → ARCHIVED через 168 часов (7 дней)

### §17.2 ПОРЯДОК ОБРАБОТКИ В _handle_new

ШАГ 0: HEALTHCHECK_GUARD
  retry_queue_healthcheck в raw_input/result → CANCELLED
  tmp*.txt + topic=0 + source=google_drive → CANCELLED

ШАГ 1: ACTIVE TASK RESOLVER
  reply на bot_message_id → контекст той задачи
  AWAITING_CONFIRMATION + "да/ок/+" → DONE
  WAITING_CLARIFICATION → любой ответ → IN_PROGRESS
  Intent приоритет: FINISH > CANCEL > CONFIRM > REVISION > TASK > SEARCH > CHAT

ШАГ 2: MEMORY_QUERY_GUARD_V1
  Маркеры: "что обсуждали" | "что делали" | "что мы делали" | "что мы обсуждали"
           "неделю назад" | "две недели" | "три недели" | "месяц назад"
           "апреля" | "марта" | "февраля" | "января"
           "помнишь" | "напомни" | "какие задачи были" | "что было" | "расскажи что"
  → _load_archive_context + _load_memory_context → DeepSeek → DONE
  НЕ попадает в FULLFIX_10 project route

ШАГ 3: FULLFIX_16_CONTEXT_QUERY
  Короткие статус-запросы ≤35 символов
  Триггеры: "где результат" | "что там" | "где смета" | "ну что" | "где проект"
  → Статус активной задачи

ШАГ 4: FULLFIX_14/13A
  topic_2: "смета" | "расчёт" | "посчитай" → estimate_engine
  topic_5: "дефект" | "акт" | "технадзор" → technadzor_engine

ШАГ 5: FULLFIX_19_PROJECT_GUARD
  Короткие ответы ≤3 слова → блок попадания в project engine

ШАГ 6: FULLFIX_10_TOTAL_CLOSURE_UNIVERSAL_ROUTE
  classify_user_task() → estimate | project | confirm | revision | chat

ШАГ 7: AI_ROUTER
  payload: short_memory + long_memory + archive_context + topic_id (ОБЯЗАТЕЛЬНО)

### §17.3 ФАЙЛОВЫЙ ПРИЁМ

Файл БЕЗ caption:
  Telegram → daemon → Drive upload → create_task(drive_file)
  → FILE_INTAKE_ROUTER → меню по топику → NEEDS_CONTEXT
  → reply пользователя → FILE_CHOICE_PARSED → IN_PROGRESS → engine

Файл С caption:
  "смета/расчёт/посчитай" → estimate_engine
  "дефект/акт/технадзор" → technadzor_engine
  любой caption → сразу IN_PROGRESS без меню

Source guard ДО create_task:
  source=google_drive → CANCELLED молча
  healthcheck маркеры в file_name → CANCELLED молча

Voice:
  voice → STT Groq Whisper → "[VOICE] текст" — идентично тексту
  "[VOICE] да" = "да" — без разницы
  Голос НЕ загружается на Drive

Drive файл:
  DRIVE_FILE_MEMORY_INDEX_V1 → topic_N_file_TASKID в memory.db
  Повторный file_id → FILE_DUPLICATE_MEMORY_GUARD_V1 → "Файл уже есть"

Timeline:
  Каждая задача → TELEGRAM_TIMELINE_APPEND_V1 → timeline.jsonl по топику + GLOBAL

### §17.4 GOOGLE DRIVE СТРУКТУРА

AI_ORCHESTRA/chat_-1003725299009/
├── topic_2/    СТРОЙКА
├── topic_5/    ТЕХНАДЗОР
├── topic_11/   ВИДЕОКОНТЕНТ
├── topic_210/  ПРОЕКТИРОВАНИЕ
├── topic_500/  ВЕБ ПОИСК
├── topic_794/  НЕЙРОНКИ СОФТ ВПН ВПС
├── topic_961/  АВТО ЗАПЧАСТИ
├── topic_3008/ КОДЫ МОЗГОВ
├── topic_4569/ ЛИДЫ РЕКЛАМА АМО
└── topic_6104/ РАБОТА ПОИСК

Артефакты: Excel + PDF + DOCX → Drive → ссылка в Telegram
Retry: Drive упал → TG fallback → cron 10 мин → восстановление

### §17.5 ТОПИКИ И ДВИЖКИ

topic_2  СТРОЙКА:    PDF/XLSX/фото → estimate_engine → Excel =C*D =SUM + PDF → Drive
topic_5  ТЕХНАДЗОР:  фото → Gemini Vision → СП/ГОСТ → DOCX акт | PDF → дефекты → DOCX
topic_210 ПРОЕКТИРОВАНИЕ: PDF → project_engine → DOCX+XLSX → Drive. КЖ/КМ/КМД/АР/ОВ/ВК/ЭОМ/СС/ГП/ПЗ/СМ/ТХ
topic_500 ВЕБ ПОИСК: Perplexity → 14 этапов → результат с источниками
topic_3008 КОДЫ МОЗГОВ: верификация кода. No Auto-Patch.
topic_11,794,961,4569,6104 ОБЫЧНЫЕ: файл → меню → выбор → engine

### §17.6 LIFECYCLE + WATCHDOG

NEW → IN_PROGRESS → AWAITING_CONFIRMATION → DONE → ARCHIVED (168ч)
AWAITING_CONFIRMATION > 30 мин → FAILED:CONFIRMATION_TIMEOUT
IN_PROGRESS > 15 мин по created_at → FAILED:EXECUTION_TIMEOUT
STALE_TIMEOUT = 600 сек по updated_at
ARCHIVE_DEDUP: один task_id → одна запись в memory.db

### §17.7 ЗАПРЕЩЕНО

LLM считать цифры в сметах
Нормы СП/ГОСТ без источника
topic_id=0 для задач из конкретного топика
AWAITING_CONFIRMATION без реального результата (len<100 или "ошибка")
Memory из чужого топика в контексте
Новые папки в репо без явного разрешения

====================================================================================================
END_FILE: docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/CANON_FINAL/00_INDEX.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 999acb6bfdd6c7215f11d76342ea1b9f8cdf5715418064acb3716f33999c8af6
====================================================================================================
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

====================================================================================================
END_FILE: docs/CANON_FINAL/00_INDEX.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/CANON_FINAL/09_FILE_INTAKE_DRIVE_UPLOAD_2026-04-30.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 1a439843e1eb214745752720c85b49adc48f1823765982960ce7b1e285947d84
====================================================================================================
# 09_FILE_INTAKE_DRIVE_UPLOAD_2026-04-30

MODE: FACTS ONLY
SOURCE: current chat, 2026-04-30
STATUS: PARTIAL_FIX_INSTALLED / DRIVE_UPLOAD_NOT_CLOSED

## CONFIRMED FACTS

- Telegram file tasks are created as `input_type='drive_file'`, not `file`.
- `drive_file.raw_input` contains file metadata including `file_id`, `file_name`, `mime_type`, `caption`, `telegram_message_id`, `telegram_chat_id`.
- `drive_file` without clear `caption/user_intent` must enter `NEEDS_CONTEXT` before download or processing.
- `drive_file -> NEEDS_CONTEXT -> menu` was verified on live tasks.
- `bot_message_id` for file menu was saved.
- Reply/voice/text choice priority was patched before role/confirm/finish/chat logic.
- Local artifact generation worked for task `d95b1fcb-b31f-4b2f-b0a2-3342c8d35984`.
- That task reached `AWAITING_CONFIRMATION`.
- Result contained `Нормализовано позиций: 32`.
- Drive upload failed with `invalid_grant: Token has been expired or revoked`.
- Service Account healthcheck returned `ok=True`.
- Service Account email: `ai-orchestra@areal-neva-automation.iam.gserviceaccount.com`.
- Drive folder id: `13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB`.
- Helper module created: `/root/.areal-neva-core/core/drive_service_account_uploader.py`.
- Live `/root/.areal-neva-core/core/engine_base.py` is missing.
- `import core.engine_base` returned `NOT_FOUND`.
- Live files still import `core.engine_base`.
- Backup source found: `/root/.areal-neva-core/core.bak.before_rollback_20260427_202634/engine_base.py`.

## PATCHES INSTALLED IN CURRENT SESSION

### PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL
Status: INSTALLED

Facts:
- Added file-intake menu logic for `drive_file`.
- Added `NEEDS_CONTEXT` path.
- Added topic-based menus.
- Syntax OK and worker active after install.

### PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1
Status: INSTALLED

Facts:
- Moved intent and `NEEDS_CONTEXT` guard before `_download_from_drive`.
- Fixed issue where download path could block before menu.

### PATCH_WORKER_PICK_BEFORE_STALE_V1
Status: INSTALLED

Facts:
- Moved task pick before stale recovery.
- Later confirmed this was not the final root cause of stuck `drive_file` tasks.

### PATCH_FIX_PFIN3_MENU_SHADOW_V1
Status: VERIFIED

Facts:
- Fixed Python bug `_pfin3_menu = _pfin3_menu(...)`.
- Removed `UnboundLocalError` caused by local variable shadowing function.
- Tasks `d95b1fcb...` and `1e7b6864...` moved from `NEW` to `NEEDS_CONTEXT`.
- `bot_message_id` saved: `8149` and `8150`.
- `FILE_INTAKE_GUARD_HIT` appeared in logs.

### PATCH_FILE_CHOICE_PRIORITY_V1
Status: INSTALLED_PARTIALLY_VERIFIED

Facts:
- Added priority file-choice handler before role/confirm/finish/chat logic.
- Tech-supervision topic task `d95b1fcb...` reached `AWAITING_CONFIRMATION`.
- Project topic task `1e7b6864...` became `CANCELLED` after user reply parsed as cancel/check.

### PATCH_DRIVE_SERVICE_ACCOUNT_PRIMARY_V1
Status: INSTALLED_NOT_COMPLETE

Facts:
- Service Account uploader module was created.
- Service Account healthcheck returned `ok=True`.
- Folder id confirmed as `13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB`.
- Common upload path is not closed because live `core/engine_base.py` is missing.

## ERRORS FOUND

- Initial guard targeted `input_type='file'`, but real input is `drive_file`.
- Guard was initially after download, so download could block before menu.
- `_download_from_drive` could block the file-intake menu path.
- `_pfin3_menu` variable shadowed `_pfin3_menu()` function.
- Drive upload failed with `invalid_grant: Token has been expired or revoked`.
- `core.engine_base` missing while live engines still import it.
- Generated `engine_base.py` from scratch was rejected as unsafe.
- `find`-based patch selected backup `engine_base.py` instead of live path.

## CURRENT BROKEN POINT

Permanent Drive artifact upload is not closed.

Reason:
- OAuth token path failed with `invalid_grant`.
- Service Account exists and healthcheck works.
- Common module `core.engine_base.py` is missing from live core directory.
- Engines import `core.engine_base`.
- Upload path cannot be safely patched until `engine_base.py` is restored from confirmed source.

## CANON DECISIONS

- Do not use daily manual OAuth token repair as final solution.
- token OAuth is legacy fallback only, not primary upload path.
- Primary Drive upload must use Service Account.
- Drive failure must not break file task if local artifact exists.
- Do not recreate `engine_base.py` by guessing.
- Restore `engine_base.py` only from confirmed source.
- Do not patch `.env`.
- Do not delete token or credentials files.
- Do not rewrite `estimate_engine.py`, `dwg_engine.py`, or `project_engine.py` unless diagnostics prove direct need.

## REQUIRED ENGINE_BASE CONTRACTS

`core.engine_base` must provide at least:

- `detect_real_file_type`
- `update_drive_file_stage`
- `upload_artifact_to_drive`
- `quality_gate`
- `calculate_file_hash`
- `normalize_unit`
- `is_false_number`
- `normalize_item_name`

## NEXT VALID PATCH REQUIREMENT

Patch is allowed only after confirming source for `core/engine_base.py`.

Confirmed source found in current session:
- `/root/.areal-neva-core/core.bak.before_rollback_20260427_202634/engine_base.py`

Patch plan agreed by Claude:

1. Restore `/root/.areal-neva-core/core/engine_base.py` from confirmed backup.
2. Replace only `upload_artifact_to_drive` with Service Account primary implementation.
3. Do not touch `.env`, credentials, or token files.
4. Do not touch engines unless direct diagnostic need appears.
5. Run `py_compile`.
6. Verify `import core.engine_base`.
7. Run live upload test using `upload_artifact_to_drive('/tmp/testfile', 'healthcheck_<ts>', 0)`.
8. Require returned `drive.google.com` link.
9. Restart `areal-task-worker`.
10. Verify service active.
11. Verify no `invalid_grant` in primary Service Account upload path.

## ACCEPTANCE CRITERIA

Final status can be VERIFIED only if:

- `/root/.areal-neva-core/core/engine_base.py` exists.
- `import core.engine_base` resolves to `/root/.areal-neva-core/core/engine_base.py`.
- Required functions import successfully.
- Service Account upload test returns a `drive.google.com` link.
- `areal-task-worker` is active.
- File task can reach `AWAITING_CONFIRMATION` without being blocked by Drive OAuth.
- New upload path does not use OAuth token as primary path.
- No new `invalid_grant` occurs in Service Account primary path.

## CURRENT STATUS

- File intake: PARTIALLY FIXED.
- Reply choice priority: INSTALLED_PARTIALLY_VERIFIED.
- Local artifact generation: VERIFIED for one task.
- Service Account healthcheck: VERIFIED.
- Permanent Drive upload: NOT CLOSED.
- Next state: READY_FOR_PATCH after restoring confirmed `engine_base.py`.

====================================================================================================
END_FILE: docs/CANON_FINAL/09_FILE_INTAKE_DRIVE_UPLOAD_2026-04-30.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/CANON_FINAL/ESTIMATE_TEMPLATE_M80_M110_CANON.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2c94bccb75dca28ff1c647504fda78617aad615810173020528bd8437a1f58b5
====================================================================================================
# ESTIMATE_TEMPLATE_TOP_CANON

status: ACTIVE_CANON
version: ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4
updated_at: 2026-05-02T13:37:39.354912+00:00

## ГЛАВНОЕ

М-80.xlsx, М-110.xlsx, крыша и перекр.xlsx, фундамент_Склад2.xlsx, Ареал Нева.xlsx — топовые эталонные сметы
Они являются образцами логики построения смет, формул, разделов, колонок, итогов, примечаний и исключений
Они не являются фиксированным прайсом
Оркестр обязан переносить их расчётную логику на любые новые задачи и любые материалы

## ЧТО СОХРАНЯТЬ
- Топовые сметы являются эталонами логики расчёта, а не прайс-листами
- Новые сметы считаются по такой же структуре: разделы, строки, колонки, формулы, итоги, примечания, исключения
- Материал может быть любым: кирпич, газобетон, каркас, монолит, кровля, перекрытия, отделка, инженерия
- При замене материала сохраняется расчётная логика: количество × цена = сумма; работа + материалы = всего; разделы = итоги; финальный итог = сумма разделов
- Каркасный сценарий, газобетон/монолитная плита, кровля/перекрытия и фундамент считаются как разные сценарии и не смешиваются
- Если объёмов не хватает — оркестр спрашивает только недостающие объёмы
- Если пользователь прислал файл как образец — сначала принять как образец, а не запускать поиск цен

## ЦЕНЫ ИЗ ИНТЕРНЕТА
- Интернет-цены материалов и техники не подставляются молча
- Для финальной сметы оркестр ищет актуальные цены по материалам, технике, доставке и разгрузке
- По каждой позиции показывает: источник, цена, единица, дата/регион, ссылка
- Оркестр предлагает среднюю/медианную цену без явных выбросов
- Пользователь выбирает: средняя / минимальная / максимальная / конкретная ссылка / ручная цена
- Пользователь может добавить наценку, запас, скидку, поправку по позиции, разделу или всей смете
- До подтверждения цен финальный XLSX/PDF не выпускается
- После подтверждения цены пересчитываются по формулам шаблона

## ЛОГИСТИКА И НАКЛАДНЫЕ
- Перед финальной сметой оркестр обязан запросить локацию объекта или расстояние от города
- Стоимость объекта рядом с городом и объекта за 200 км не может быть одинаковой
- Оркестр обязан учитывать доставку материалов, транспорт бригады, разгрузку, манипулятор/кран, проживание, удалённость, дорожные условия
- Если логистика неизвестна — оркестр задаёт один короткий вопрос: город/населённый пункт или расстояние от города, подъезд для грузовой техники, нужна ли разгрузка/манипулятор
- Логистика считается отдельным блоком сметы или отдельным коэффициентом, но не смешивается молча с ценами материалов
- Перед финальным результатом оркестр показывает логистические допущения и спрашивает подтверждение

## КОЛОНКИ
№ п/п | Наименование | Ед. изм. | Кол-во | Работа Цена | Работа Стоимость | Материалы Цена | Материалы Стоимость | Всего | Примечание

## РАЗДЕЛЫ
1. Фундамент
2. Каркас
3. Стены
4. Перекрытия
5. Кровля
6. Окна, двери
7. Внешняя отделка
8. Внутренняя отделка
9. Инженерные коммуникации
10. Логистика
11. Накладные расходы

## МАТЕРИАЛЫ
- стены: кирпич, газобетон, керамоблок, арболит, монолит, каркас, брус
- фундамент: монолитная плита, лента, сваи, ростверк, утеплённая плита, складской фундамент
- кровля: металлочерепица, профнастил, гибкая черепица, фальц, мембрана, стропильная система
- перекрытия: деревянные балки, монолит, плиты, металлические балки
- утепление: минвата, роквул, пеноплэкс, pir, эковата
- отделка: имитация бруса, штукатурка, плитка, гкл, цсп, фасадная доска
- инженерия: электрика, водоснабжение, канализация, отопление, вентиляция
- логистика: доставка, разгрузка, манипулятор, кран, проживание, транспорт бригады, удалённость

## ПРОЧИТАННЫЕ ШАБЛОНЫ

### М-80.xlsx
- role: `full_house_estimate_template`
- file_id: `1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp`
- drive_url: https://docs.google.com/spreadsheets/d/1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true
- formula_total: 1670
  - sheet: Каркас под ключ | scenario=frame_house | formulas=799 | material_rows=130 | work_rows=96 | logistics_rows=17
  - sheet: Газобетон_под ключ | scenario=gasbeton_or_masonry_with_monolithic_foundation | formulas=871 | material_rows=156 | work_rows=99 | logistics_rows=23

### М-110.xlsx
- role: `full_house_estimate_template`
- file_id: `1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo`
- drive_url: https://docs.google.com/spreadsheets/d/1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true
- formula_total: 1647
  - sheet: Каркас под ключ | scenario=frame_house | formulas=791 | material_rows=130 | work_rows=96 | logistics_rows=17
  - sheet: Газобетон | scenario=gasbeton_or_masonry_with_monolithic_foundation | formulas=856 | material_rows=154 | work_rows=99 | logistics_rows=23

### крыша и перекр.xlsx
- role: `roof_and_floor_estimate_template`
- file_id: `16YecwnJ9umnVprFu9V77UCV6cPrYbNh3`
- drive_url: https://docs.google.com/spreadsheets/d/16YecwnJ9umnVprFu9V77UCV6cPrYbNh3/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true
- formula_total: 136
  - sheet: расчет кровли | scenario=roof_and_floors | formulas=136 | material_rows=1 | work_rows=24 | logistics_rows=1

### фундамент_Склад2.xlsx
- role: `foundation_estimate_template`
- file_id: `1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp`
- drive_url: https://docs.google.com/spreadsheets/d/1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true
- formula_total: 88
  - sheet: смета | scenario=foundation | formulas=88 | material_rows=6 | work_rows=17 | logistics_rows=0

### Ареал Нева.xlsx
- role: `general_company_estimate_template`
- file_id: `1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm`
- drive_url: https://docs.google.com/spreadsheets/d/1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true
- formula_total: 1192
  - sheet: смета | scenario=gasbeton_or_masonry_with_monolithic_foundation | formulas=1192 | material_rows=194 | work_rows=78 | logistics_rows=18

## ОБЯЗАТЕЛЬНОЕ ПОВЕДЕНИЕ

При новой смете оркестр обязан брать структуру и формулы из топовых эталонов
Оркестр обязан подставлять конкретные объёмы и материалы задачи
Оркестр обязан запросить локацию/удалённость/доступ/разгрузку до финального расчёта
Оркестр обязан обновлять цены материалов и логистики через интернет только с подтверждением пользователя
Оркестр обязан показывать найденные цены, источники, ссылки и среднюю/медианную цену
Пользователь выбирает цену или задаёт ручную, может добавить наценку/скидку/запас
Финальный XLSX/PDF запрещён до подтверждения цен и логистики


====================================================================================================
END_FILE: docs/CANON_FINAL/ESTIMATE_TEMPLATE_M80_M110_CANON.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/CANON_FINAL/OWNER_REFERENCE_FULL_WORKFLOW_CANON.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 763debb0a4f9ea13734110d15b6eb84615c2be5668d739eecdd4494efab4b4f8
====================================================================================================
# OWNER_REFERENCE_FULL_WORKFLOW_CANON

version: AREAL_REFERENCE_FULL_MONOLITH_V1
updated_at: 2026-05-02T20:20:56.522887+00:00

Илья — главный канон

Сметы: М-80, М-110, крыша, фундамент, Ареал Нева — эталон формул и структуры

Проектирование: АР, КР, КЖ, КД, КМ, КМД, ОВ, ВК, ЭО, ЭМ, ЭОС, эскизы, планы участка — разные разделы, не смешивать

Технадзор: акты, дефекты, исполнительные — отдельный контур

Если данных не хватает — один короткий вопрос

counts: {"estimate_files": 6, "design_files": 231, "technadzor_files": 1, "formula_total": 4733, "all_files": 261}

====================================================================================================
END_FILE: docs/CANON_FINAL/OWNER_REFERENCE_FULL_WORKFLOW_CANON.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e9b63408cbfdd13c05ed9b174f3380d5067493e3815318661c81b30ba13be440
====================================================================================================
# ORCHESTRA_MASTER_BLOCK — ЦЕЛЕВАЯ АРХИТЕКТУРА ОРКЕСТРА
Версия: v1 | Дата: 28.04.2026 | Верифицировано: Claude + GPT

---

## БЛОК 1 — TECHNICAL FILE PIPELINE

### Цель
Любой файл из Telegram/Drive → полный цикл → артефакт → пользователю.

### Pipeline (8 стадий — все обязательны)
INGESTED → DOWNLOADED → PARSED → CLEANED → NORMALIZED → CALCULATED → ARTIFACT_CREATED → UPLOADED

### Что должно работать
PDF / XLSX / CSV           → XLSX смета с формулами (=C2*D2, =SUM)
Фото таблицы               → XLSX
Фото дефекта               → DOCX/PDF акт + нормы СП/ГОСТ
DWG/DXF                    → отчёт (или FAILED:DWG_NOT_IMPLEMENTED)
Шаблон                     → новый файл по образцу
Несколько файлов           → один артефакт

### Движки
estimate_engine.py         — сметы, объёмы, формулы
ocr_engine.py              — фото → таблица
technadzor_engine.py       — дефекты + нормы СП/ГОСТ/СНиП
dwg_engine.py              — чтение через ezdxf
template_manager.py        — шаблоны
file_intake_router.py      — маршрутизация файлов

### Жёсткое правило
Python считает и создаёт файлы.
LLM анализирует смысл.
LLM НЕ считает финальные цифры.
LLM НЕ создаёт артефакт на глаз.

### FILE_RESULT_GUARD
если input_type = file:
  → обязательно: результат + ссылка + статус
  иначе → FAILED

### Критерий закрытия
файл принят → обработан → артефакт → Drive/GitHub link → Telegram → AWAITING_CONFIRMATION

---

## БЛОК 2 — MULTI-MODEL ORCHESTRA LAYER

### MODEL_ROUTER (1 точка выбора)
если фото/схема       → Gemini
если поиск            → Perplexity
если структурирование → Mistral
если reasoning        → Cerebras
если расчёт           → Python ONLY
если финальный ответ  → DeepSeek
если fallback         → Cloudflare → HuggingFace

### PRE_OPENROUTER_MODEL_LAYER
task_worker → ORCHESTRA_SHARED_CONTEXT → MODEL_ROUTER → specialist models → OpenRouter/DeepSeek → RESULT_VALIDATOR → HUMAN_DECISION_EDITOR → Telegram

### Роли моделей
Gemini     — фото, схемы, таблицы, OCR, visual reasoning
Mistral    — структуризация, нормализация, классификация
Cerebras   — быстрый reasoning, проверка логики
Cohere     — rerank, фильтрация, чистка контекста
Perplexity — внешний поиск (нормы, цены, поставщики, СП/ГОСТ)
DeepSeek   — основной исполнитель, финальная сборка
Claude     — контроль, канон, верификация, ТЗ
GPT        — патчи кода, сервер
Python     — расчёт, Excel, файлы, валидация

### Жёсткое правило
Ни одна модель не отвечает пользователю напрямую.
Финал всегда: validator → HUMAN_DECISION_EDITOR → Telegram.
Модели = инструменты, не конкуренты.

### ORCHESTRA_SHARED_CONTEXT
Каждая модель получает: ONE_SHARED_CONTEXT + memory.db + core.db active task + pin + topic role + history + files

### RESULT_VALIDATOR
Проверить перед отправкой: цена / контакт / ссылка / ТТХ / единица измерения.
Если нет → INVALID_RESULT → не отправлять.

### RESULT_FORMAT_ENFORCER
Обязательно в финале: таблица + выводы (CHEAPEST/MOST_RELIABLE/BEST_VALUE) + блок «что проверить звонком».
Если нет → RESULT_INVALID → доработка.

### HUMAN_DECISION_EDITOR
Технический результат → человеческое решение.
Формат: 1.Что произошло 2.Что это значит 3.Что делать 4.Риски 5.Следующий шаг

### USER_MODE_SWITCH
TECH  → полный технический разбор
HUMAN → коротко и по делу (default)

### FALLBACK_CHAIN
Gemini → Mistral → Cloudflare → HuggingFace
Оркестр не падает никогда.

### MODE_SWITCH
LIGHT — простая задача → 1 модель
FULL  — сложная задача → полный оркестр

### MODEL_REGISTRY
gemini: vision | mistral: text | cerebras: reasoning | perplexity: search | deepseek: final | cloudflare: fallback | hf: fallback
Новая модель = 1 строка.

### EXECUTION_PRIORITY (верифицировано GPT)
FILE > SEARCH > CHAT
Иначе оркестр болтает когда надо считать смету.

---

## БЛОК 3 — GITHUB SSOT + AGGREGATOR

### Архитектура памяти
GitHub = мозг (каноны + логика + shared context)
Сервер = runtime (обработка, memory.db, core.db)
Drive  = резерв (DWG, PDF, фото входящие)

### Поток
чат/выгрузка → агрегатор → ONE_SHARED_CONTEXT → GitHub → все нейросети читают GitHub

### Drive Knowledge Aggregator
ВХОД: CHAT_EXPORTS (14bYA9bHaKahkE8d4IDwWxL4Ojn-G0sDl) + CANON_FINAL (1U_IrEOtIJfUVAdjH-kHwms2M2z3FXan0)
ВЫХОД: docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md + ONE_SHARED_CONTEXT.json + LAST_AGGREGATION_REPORT.md
ЛОГИКА: новая выгрузка → читает → отделяет факты от мусора → раскладывает по разделам → обновляет ONE_SHARED_CONTEXT → человек утверждает что входит в CANON_FINAL

### Что агрегатор НЕ делает
Не чинит код. Не переписывает канон самовольно. Не сохраняет FAILED как память. Не тащит секреты.

### GITHUB_SSOT_RULES
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

---

## MULTI_MODEL_ORCHESTRA_ACTUAL_STATE_2026_04_29

### ACTIVE MODELS (CANON)
Gemini     — vision / OCR / схемы / таблицы  
Mistral    — структуризация / нормализация  
Cerebras   — reasoning / логика  
Cohere     — rerank / фильтрация  
Perplexity — поиск (СП/ГОСТ/цены/поставщики)  
DeepSeek   — финальный ответ (DEFAULT)  
Claude     — канон / проверка / ТЗ  
GPT        — сервер / код / патчи  
Python     — расчёт / Excel / файлы  

### MODEL_ROUTER (TARGET LOGIC)
photo/schema      → Gemini  
search            → Perplexity  
structure         → Mistral  
reasoning         → Cerebras  
calculation       → Python ONLY  
final             → DeepSeek  

### FALLBACK_CHAIN (TARGET)
Gemini → Mistral → Cloudflare → HuggingFace  

### STATUS
- модели описаны в каноне ✔  
- MODEL_ROUTER — НЕ реализован  
- FALLBACK_CHAIN — НЕ реализован  
- MODEL_REGISTRY — НЕ реализован  
- MULTI-MODEL EXECUTION — НЕ реализован  

### CRITICAL RULE
Сейчас оркестр работает как:
1 модель (DeepSeek) + поиск (Perplexity)

Полный multi-model НЕ запущен

====================================================================================================
END_FILE: docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/SEARCH_MONOLITH_V1.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 26676725c7608d217d6f9162526748875a7647f92320f64a5a0e10b5fd0afa28
====================================================================================================
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

### 1. Разбор запроса
Общие: товар, категория, бренд/модель, характеристики, артикул/SKU/OEM, город, радиус,
количество, новое или б/у, допустимые аналоги, нужна ли доставка,
приоритет (цена / качество / скорость / надёжность).
Стройка: материал, профиль, толщина, цвет/RAL, покрытие, размер, единица цены, объём, ГОСТ/ТУ, производитель.
Запчасти: марка, модель, год, кузов, двигатель, сторона, OEM, кросс-номер,
новая/б/у/контрактная, оригинал/аналог, рестайлинг или дорестайлинг.

### 2. Уточнения (максимум 3 вопроса)
Общие: город и радиус? / новое или б/у? / что обязательно, где можно аналог?
Запчасти: OEM/VIN есть? / новая, б/у или контрактная? / какая сторона, кузов, год, рестайлинг?
Стройка: точная толщина, цвет, покрытие? / производитель обязателен? / самовывоз или доставка?

### 3. Search Session
Каждый поиск — одна сессия. Внутри: цель, товар, критерии, уточнения, регион,
источники, найденные варианты, отброшенные варианты, риски, итоговый выбор.
Уточнения «проверь ещё», «добавь Avito/VK», «сузь по цене», «посмотри аналоги» —
продолжают текущую search-сессию, не создают новую задачу.

### 4. Расширение запроса (7+ формул)
название + город
название + оптом / название + производитель
артикул / OEM / SKU
параметры без маркетингового названия
название + Avito
название + VK / Telegram

### 5. Цифровой двойник товара
Игнорировать рекламное название. Искать по физическим параметрам:
габариты, материал, толщина, OEM, SKU, уникальные технические признаки.
Цель: найти поставщиков без SEO у которых товар реально есть на складе.

### 6. Источники
Маркетплейсы:   Ozon, Wildberries, Яндекс Маркет, Мегамаркет
Объявления:     Avito, Юла
Стройка:        Петрович, Леруа, ВсеИнструменты, Максидом, строительные базы, заводы, дилеры
Карты:          2ГИС, Яндекс Карты
Соцсети:        VK, Telegram-чаты, форумы
Запчасти:       Exist, Emex, ZZap, Drom, Auto.ru, EuroAuto, разборки

### 7. Проверка источника
Тип: производитель / официальный дилер / строительная база / оптовик /
маркетплейс / магазин / частник / разборка / форум-группа / непонятный.
Статус доверия: CONFIRMED / PARTIAL / UNVERIFIED / RISK

### 8. Детектор живости
- дата обновления цены
- свежесть отзывов (не старше 30 дней)
- наличие телефона и адреса
- активность продавца
- признаки сайта-призрака

Если прайс старше 48-72 часов → риск устаревшей цены (+5-10% к TCO).
Каждый результат обязан иметь checked_at и source_url.
Нет даты или источника → статус не выше PARTIAL.

### 9. Анализ отзывов + Review Trust Score

Площадки: Ozon, WB, Яндекс Маркет, Avito, 2ГИС, Яндекс Карты, форумы, VK, Drom, Auto.ru.

Признаки живого отзыва:
- есть фото товара
- есть конкретная проблема или плюс
- есть дата покупки и детали использования
- есть замеры / сравнение с другим товаром
- нормальный русский текст без шаблона
- есть история профиля
- есть ответы продавца

Признаки фейка:
- много одинаковых отзывов / одинаковые фразы
- нет фото / слишком общие слова
- все отзывы в один день / профиль без истории
- только 5 звёзд без деталей / нет конкретики

Review Trust Score (0-100):
80-100 = живые, свежие, с фото, жалобы не критичные
60-79  = отзывы есть, часть данных не подтверждена
40-59  = мало отзывов, есть риск, нужен звонок
0-39   = высокий риск фейка, обмана или мёртвого продавца

Статусы: REVIEWS_CONFIRMED / REVIEWS_PARTIAL / REVIEWS_FAKE_RISK / REVIEWS_NOT_FOUND

### 10. Технический аудит (Цифровой микрометр)

Для стройки — ключевые слова в отзывах и ТТХ:
фольга / тонкий / не 0.45 / не 0.5 / царапины / ржавчина
плохое покрытие / не тот RAL / недовоз / брак
замер / микрометр / слой цинка (г/м2)

Для запчастей:
не подошло / не тот кузов / не та сторона
рестайлинг/дорестайлинг / аналог вместо оригинала / б/у вместо нового
люфт / трещина / скол / нет гарантии / нет возврата
фото не этой детали / предоплата

Правило: если вес, толщина или параметры хуже эталона → статус RISK.
Если эталона нет → «эталон не подтверждён».

### 11. Запрещено смешивать в одной строке сравнения
0.45 и 0.5 / мат / глянец / Satin без пометки
RAL 8017 и другой цвет / Classic и Монтеррей без пометки
оригинал и аналог / рестайлинг и дорестайлинг
левая и правая сторона / новая и б/у

### 12. Risk Score

Общие красные флаги:
цена сильно ниже рынка / только предоплата
нет телефона / нет адреса / нет ИНН
старый прайс / нет даты обновления
SEO-сайт без склада / нет отзывов / не совпадают ТТХ

Для стройки:
цена за погонный метр вместо м2
цена без НДС / цена без доставки
минимальная партия не указана

Для запчастей:
рестайлинг/дорестайлинг не указан
аналог выдают за оригинал / б/у выдают за новую
фото не этой детали

Красные флаги продавца в VK/Telegram (SELLER_RISK):
группа создана недавно / мало живых комментариев / много ботов
нет старых постов / нет реальных фото
комментарии закрыты / уводит только в личку
требует предоплату / контакты скрыты

Любая цена, отзыв, риск или рекомендация должны иметь источник. Нет источника → UNVERIFIED.

Главное правило:
низкая цена + мутные отзывы                      = RISK
средняя цена + живые отзывы + понятный продавец  = BEST_VALUE

### 13. Реальная стоимость (TCO)
итоговая цена = цена + доставка + комиссия + добор + риск − кэшбэк/скидки

Учесть: гарантию, возврат, НДС, минимальную партию, самовывоз, наличие ИНН.
Товар за 10000 с гарантией 2 года и кэшбэком 2000 = выгоднее чем 9000 без чека и гарантии.

### 14. Живой рынок
Ключевые слова: остатки / ликвидация / распродажа / отдам срочно / склад / партия / самовывоз / разбор

Всё из чатов и соцсетей = автоматически UNVERIFIED до подтверждения цены, даты, контакта и наличия.

---

## ИТОГОВЫЕ СТАТУСЫ РЕКОМЕНДАЦИИ

CHEAPEST       — самый дешёвый вариант
MOST_RELIABLE  — самый надёжный вариант
BEST_VALUE     — лучший баланс цена/риск/логистика
FASTEST        — самый быстрый по доставке
RISK_CHEAP     — дешёвый но рискованный
REJECTED       — отброшен, причина указана

---

## ИТОГОВАЯ ТАБЛИЦА

Поставщик | Площадка | Тип | Город | Цена | Единица
Доставка | TCO (итог) | Совпадение ТТХ | Вес/толщина/эталон
Отзывы | Review Trust Score | Фейк-риск | Жалобы
Риски | Продавец статус | Контакт | Ссылка
Дата актуальности (checked_at) | Статус доверия | Статус рекомендации

После таблицы обязательно:
CHEAPEST — что и где
MOST_RELIABLE — что и где
BEST_VALUE — что и где + почему
RISK_CHEAP — что и где + в чём риск
что проверить звонком
что отброшено и почему
что не подтверждено

---

## ЧТО ПРОВЕРИТЬ ЗВОНКОМ (шаблон вопросов)

цена актуальна?
есть в наличии?
цена с НДС или без?
единица цены какая?
доставка — сколько и когда?
самовывоз возможен?
документы/счёт дадут?
гарантия/возврат есть?
характеристики точно такие?

для металла:    толщина, покрытие, слой цинка
для запчастей:  OEM, сторона, кузов, состояние

---

## ПАМЯТЬ СЕССИИ

Сохранять: критерии / уточнения / лучших поставщиков / отброшенные варианты / рабочие формулы / итоговый выбор.

Не сохранять: сырые ответы Perplexity / старые цены без даты / мусорные ссылки / FAILED / STALE_TIMEOUT / непроверенные цены как факт.

---

## КАК РЕАЛИЗОВАТЬ (по шагам)

Шаг 1 DONE: is_search в work_payload → Perplexity (28.04.2026) ✅
Шаг 2: системный промпт для Perplexity с 14 этапами + формат таблицы + статусы в ai_router.py
Шаг 3: search_session в memory.db — хранить критерии в рамках одной задачи topic_500
Шаг 4: Risk Score и Trust Score — LLM считает на основе текста результата, без внешних API
Шаг 5 (PRO): Живой рынок — Telegram через Telethon (userbot авторизован)

---

## ЧТО НЕ РЕАЛИЗОВАНО — НЕЛЬЗЯ ЗАЯВЛЯТЬ

парсинг закрытых Telegram/VK-чатов
проверка SSL/cache/photo автоматически
точный прогноз цены при звонке
биржевые индексы цен на металл
автоматическая проверка корзины
автоматическая проверка уникальности фото

Это будущие PRO-модули, не текущий факт.

---

## ПОЛНЫЙ СПИСОК МОДУЛЕЙ (24)

SearchSessionManager        — управление сессией
CriteriaExtractor           — разбор запроса
ClarificationEngine         — уточняющие вопросы (макс. 3)
SourcePlanner               — план источников по типу товара
QueryExpander               — расширение формул запроса
EntityResolver              — цифровой двойник товара
MarketplaceCollector        — маркетплейсы
ClassifiedsCollector        — объявления (Avito, Юла)
AutoPartsCollector          — запчасти (Exist, Drom, разборки)
ConstructionSupplyCollector — стройматериалы (базы, заводы)
SocialSearchCollector       — VK, Telegram, форумы
MapsCollector               — 2ГИС, Яндекс Карты
OfferNormalizer             — нормализация предложений
SupplierClassifier          — тип и статус источника
TechnicalAudit              — цифровой микрометр
LivenessCheck               — детектор живости источника
ReviewAnalyzer              — анализ отзывов
FakeDetector                — детектор фейков + SELLER_RISK
RiskScorer                  — итоговый риск-скор
TcoCalculator               — реальная стоимость
ValueOptimizer              — лучший баланс
ResultRanker                — ранжирование + 6 статусов
SearchMemoryWriter          — запись в память
SearchOutputFormatter       — итоговая таблица и вывод

---

## ИТОГОВАЯ ФОРМУЛА

SEARCH_MONOLITH_V1 =
  Search Session
+ уточнение критериев (макс. 3 вопроса)
+ расширение запроса (7+ формул)
+ цифровой двойник товара
+ поиск по маркетплейсам
+ поиск по Avito / VK / Telegram / форумам
+ поиск по картам и локальным базам
+ OEM / SKU / артикулы
+ детектор живости источника (checked_at + source_url)
+ технический аудит (микрометр)
+ анализ отзывов + Review Trust Score + детектор фейков
+ SELLER_RISK проверка
+ Risk Score + запрет смешивать ТТХ
+ TCO (реальная стоимость)
+ ранжированное решение (6 статусов)
+ шаблон вопросов для звонка
+ память сессии

---

## КАНОНИЧЕСКИЙ СТАТУС РЕАЛИЗАЦИИ

SEARCH_MONOLITH_V1 — целевой канон интернет-поиска.
Реализация только после диагностики task_worker.py и core/ai_router.py.
Модуль нельзя считать работающим пока нет live-теста:
Telegram search → Perplexity → DeepSeek → Telegram answer → AWAITING_CONFIRMATION

====================================================================================================
END_FILE: docs/ARCHITECTURE/SEARCH_MONOLITH_V1.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/ARCHIVE_ENGINE_V1.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 6b4da89ee9ac98aaaa4ec18912a92d528412854a153d1e9aff3c0143921f38e7
====================================================================================================
# ARCHIVE_ENGINE_V1 — Stage 6

## Назначение
Индексирует завершённую задачу в memory_api после доставки результата.
Shadow mode: POST /archive на 127.0.0.1:8765, timeout=2s. Ошибка — warning, не падает.

## Что пишет
- task_id, chat_id, topic_id
- direction, engine, input_type
- raw_input (до 300 символов)
- result_text (до 500 символов)
- artifact_url / drive_link
- qg_overall, qg_failed (из quality_gate_report)
- search_plan (из payload)

## API
```python
from core.archive_engine import ArchiveEngine, archive_task
record = archive_task(payload, result)
```

## Файл
core/archive_engine.py | FULLFIX_ARCHIVE_ENGINE_STAGE_6

====================================================================================================
END_FILE: docs/ARCHITECTURE/ARCHIVE_ENGINE_V1.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/CAPABILITY_ROUTER_V1.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 4f8bbfba0fb6ef11a0f2652ac2c4e07df431eed62fa58a6a79872e845ac0fa24
====================================================================================================
# CAPABILITY_ROUTER_V1 — Stage 2

## Назначение
Берёт WorkItem с direction (Stage 1), формирует execution_plan. Shadow mode.

## ENGINE_MAP
26 направлений → движок. Fallback: ai_router.

## Шаги плана
1. OCR pre-step (photo input, кроме photo_cleanup)
2. Search pre-step (requires_search=True)
3. Main execute (обязательный)
4. Format adapters (xlsx/docx/pdf)
5. Drive upload (drive_link в formats_out)

## API
```python
from core.capability_router import CapabilityRouter
routing = CapabilityRouter().apply_to_work_item(work_item)
# work_item.execution_plan, formats_out, quality_gates заполнены
```

## Статус
Shadow mode. execution_plan формируется, в payload["engine"] пишется движок.
Stage 4 подключит реальный dispatch.

## Файл
core/capability_router.py | FULLFIX_CAPABILITY_ROUTER_STAGE_2

====================================================================================================
END_FILE: docs/ARCHITECTURE/CAPABILITY_ROUTER_V1.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/CONTEXT_LOADER_V1.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 36c86df2ab15d071f9b9911211e700c11492ceef29fbb367dc8524071fe784e0
====================================================================================================
# CONTEXT_LOADER_V1 — Stage 3

## Назначение
Загружает контекст задачи: short_memory из memory_api, topic_context из DB.
Пишет в work_item.context_refs. Shadow mode — ошибки не блокируют pipeline.

## Источники
- short_memory: GET http://127.0.0.1:8765/memory?chat_id=&topic_id=&limit=5 (timeout=2s)
- topic_context: SELECT из tasks по chat_id + topic_id, последние 5

## API
```python
from core.context_loader import ContextLoader, load_context
refs = load_context(work_item, db_conn=conn)
# work_item.context_refs заполнен
```

## context_refs структура
- chat_id, topic_id, direction
- short_memory: список записей из memory_api или None
- topic_context: последние 5 задач по теме из DB
- loader_version, shadow_mode

## Файл
core/context_loader.py | FULLFIX_CONTEXT_LOADER_STAGE_3

====================================================================================================
END_FILE: docs/ARCHITECTURE/CONTEXT_LOADER_V1.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/DIRECTION_REGISTRY_V1.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: a925153f4a1bf59f251dbc90d573ef8636355c055b9e8a2d4d31e7077201b66e
====================================================================================================
# DIRECTION_REGISTRY_V1

Канон Stage 1 реестра направлений AREAL-NEVA ORCHESTRA.

## Назначение

DirectionRegistry — детектор направления для каждого WorkItem. Берёт raw_text, topic_id, input_type, formats_in и возвращает один из 26 профилей направлений из config/directions.yaml.

## Источник правды

`config/directions.yaml` — формально YAML, фактически JSON (json.loads первым, yaml как fallback). 26 направлений, разделение active/passive по полю enabled.

## 26 направлений

### Active (13)
- general_chat — fallback общий чат
- orchestration_core — мозги оркестра, topic 3008
- telegram_automation — пайплайн Telegram
- memory_archive — память и архив
- internet_search — общий интернет-поиск, topic 500
- product_search — товарный поиск, strong_aliases avito/ozon/wb
- auto_parts_search — автозапчасти, strong_aliases drom/exist/emex
- construction_search — стройматериалы
- technical_supervision — технадзор, topic 2
- estimates — сметы, topic 2
- defect_acts — акты дефектов
- documents — DOCX
- spreadsheets — XLSX/Sheets
- google_drive_storage — загрузка на Drive

### Passive (13)
devops_server, vpn_network, ocr_photo, cad_dwg, structural_design, roofing, monolith_concrete, crm_leads, email_ingress, social_content, video_production, photo_cleanup, isolated_project_ivan

Passive направления получают penalty -80 в scoring.

## Scoring

| Сигнал | Вклад |
|---|---|
| strong_aliases hit | +200..+250 (overrides domain) |
| topic_id match | +70 + specificity bonus (max +10) |
| aliases | +30 each, max +120 |
| input_type match (если уже есть сигнал) | +15 |
| input_formats match (если уже есть сигнал) | +10 each, max +40 |
| search_signal (если requires_search и токен поиска в тексте) | +25 |
| passive penalty | -80 (capped at 0) |

Tie-break: score DESC → меньше topic_ids первым (более специфичный).

## Контракт API

```python
from core.direction_registry import DirectionRegistry, detect_direction

reg = DirectionRegistry()
profile = reg.detect(work_item)
# profile = {
#   "id": "estimates",
#   "title": "Сметы",
#   "enabled": True,
#   "score": 145,
#   "audit": [...],  # топ-10 кандидатов с reasons
#   ...все поля профиля из directions.yaml
# }
```

## Smoke тесты (приёмка)

- topic_500 + "найди avito ozon" → product_search
- topic_961 + "drom фара toyota hiace" → auto_parts_search
- topic_2 + "сделай смету" → estimates
- topic_2 + "технадзор дефект акт" → technical_supervision
- topic_3008 + "канон оркестра" → orchestration_core
- topic_0 + "привет как дела" → general_chat

Все 6 должны проходить и в pre-patch smoke, и в final smoke.

## Текущий статус

Stage 1 shadow mode: detect() вызывается через `_stage1_dir_payload()` в task_worker, направление пишется в payload, движки не используют его для маршрутизации. Capability Router (Stage 2) подключит direction к execution_plan.

## Расположение

- Код: `core/direction_registry.py`
- Конфиг: `config/directions.yaml`
- Маркер: `FULLFIX_DIRECTION_KERNEL_STAGE_1_DIRECTION_REGISTRY`

====================================================================================================
END_FILE: docs/ARCHITECTURE/DIRECTION_REGISTRY_V1.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/FORMAT_ADAPTER_V1.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: ddf6fd17f9bdd3d891d6c6fa97799b171a3fa5b33c35e8c5dc1b21e1eb75c8cf
====================================================================================================
# FORMAT_ADAPTER_V1 — Stage 7

## Назначение
Адаптирует результат движка к форматам доставки из formats_out.
Shadow mode: adapted пишется в ai_result["format_adapted"], доставка идёт через старый pipeline.

## Поддерживаемые форматы
telegram_text, telegram_table, xlsx, docx, pdf, json, drive_link, google_sheet, sources, script, mp4, table

## Результат
```json
{
  "format_adapter_version": "FORMAT_ADAPTER_V1",
  "shadow_mode": true,
  "formats_out": ["xlsx", "telegram_text"],
  "outputs": {
    "xlsx": {"type": "xlsx", "url": "https://...", "ready": true},
    "telegram_text": {"type": "telegram_text", "text": "...", "length": 42}
  },
  "primary": {...}
}
```

## API
```python
from core.format_adapter import FormatAdapter, adapt_result
adapted = adapt_result(result, formats_out, payload)
```

## Файл
core/format_adapter.py | FULLFIX_FORMAT_ADAPTER_STAGE_7

====================================================================================================
END_FILE: docs/ARCHITECTURE/FORMAT_ADAPTER_V1.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/PERSONAL_DATA_ECOSYSTEM_CANON_V1.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 55eb932cf3130a530715ff6fced02e7d109a26473261300f3790541becc95520
====================================================================================================
# PERSONAL DATA ECOSYSTEM

Рабочий смысл:
Это не оркестр для техзадач
Это не task_worker
Это не поиск
Это не сметы
Это не второй слой WorkItem

Это отдельная большая личная система управления жизнью, памятью, задачами, напоминаниями, дневниками, журналами и личным контекстом

В найденной выгрузке она прямо проходит как:
Google Gemini Assistant / Personal Data Ecosystem

И описана как цепочка:
User Prompt → Omni-Protocol Personalization Firewall → Personal Context Retrieval → Fact-Only Synthesis → Final Response

Источник найден в chat_exports/CHAT_EXPORT__Asimov_Laws_and_Bio__2026-04-27.txt

# Простыми словами

Это система, которая должна быть личным управляющим мозгом Ильи

Она должна не просто отвечать на вопросы, а вести твою жизнь как отдельный контур:
помнить важное
вести дневник
вести журналы
ставить напоминания
следить за задачами
возвращать к незакрытому
собирать итоги дня
собирать итоги недели
помнить решения
помнить привычки
помнить личные правила
поднимать нужную информацию в нужный момент

# Главное отличие от AREAL-NEVA ORCHESTRA

AREAL-NEVA ORCHESTRA — это исполнитель

Он делает:
сметы
документы
поиск
файлы
технадзор
Telegram задачи
Drive
сервер
код

PERSONAL DATA ECOSYSTEM — это личный управляющий контур

Он делает:
личные напоминания
дневники
ежедневные итоги
личные задачи
личные заметки
планы
журналы решений
контроль регулярных дел
возврат к важному

То есть:
Оркестр = рабочие руки
Personal Data Ecosystem = личная голова и память

# Что эта система должна уметь

## 1. Напоминания

Ты говоришь:
напомни завтра
через неделю проверить
каждый день в 9
напомни вечером
не забудь позвонить
вернись к этому через месяц

Система должна понять:
это не обычный чат
это reminder
нужно извлечь дату
нужно извлечь время
нужно извлечь текст напоминания
нужно сохранить
нужно сработать в нужный момент

Напоминание должно иметь состояние:
active
done
cancelled
expired
rescheduled

Она должна не просто сохранить текст, а потом реально вернуть его тебе в нужный момент

## 2. Дневник

Ты говоришь:
запиши в дневник
зафиксируй мысль
запомни как событие дня
сегодня было вот что
итог дня такой

Система должна создать дневниковую запись

Дневник — это личная история

Туда идут:
мысли
события
самочувствие
важные разговоры
выводы
эмоциональные состояния
личные решения
что произошло за день

Дневник не должен смешиваться с техническим логом оркестра

## 3. Журналы

Журнал отличается от дневника

Дневник — личное

Журнал — структурная запись по направлению

Журналы могут быть такие:
журнал решений
журнал задач
журнал здоровья
журнал идей
журнал стройки
журнал клиентов
журнал ошибок
журнал расходов
журнал звонков
журнал важных событий

Пример:
запиши в журнал решений — больше не трогаем telegram_daemon без диагностики

Это не просто память
Это запись в конкретный журнал с типом, датой, тегами и смыслом

## 4. Личные задачи

Ты говоришь:
надо сделать
поставь задачу
проверь потом
не забыть доделать
вернуться к этому

Система должна создать личную задачу

У задачи должны быть:
название
описание
срок
приоритет
статус
проект
контекст
связанные файлы или сообщения

Статусы:
new
active
waiting
done
cancelled
archived

Главное: личная задача не должна превращаться в техническую задачу оркестра, если ты не просишь выполнить действие прямо сейчас

## 5. Привычки и регулярные процессы

Система должна уметь вести регулярные вещи:
каждый день
каждую неделю
каждый месяц
по будням
каждое воскресенье
после каждого объекта
после каждого звонка

Примеры:
каждый вечер спроси итог дня
каждую пятницу напомни проверить деньги
раз в неделю собрать незакрытые задачи
каждое утро дать план
после стройки спросить что зафиксировать

Это уже не просто reminder
Это routine engine

## 6. Личная память

Система должна помнить устойчивые факты о тебе

Например:
как ты предпочитаешь получать ответы
какие проекты ведёшь
какие правила нельзя нарушать
какие решения уже приняты
какие вещи тебя раздражают
какие процессы повторяются
какие контакты важны
какие направления сейчас активны

Но она не должна писать туда мусор

Не сохранять:
ошибки моделей
технический мусор
traceback
случайные ругательства без смысла
пустые уточнения
неудачные ответы

## 7. Утренний режим

Утром система должна уметь дать:
что сегодня важно
какие задачи активны
какие напоминания на сегодня
что просрочено
что нужно проверить
какие проекты требуют внимания

Пример ответа:
Сегодня активны 4 блока

1. Оркестр — проверить search contour
2. Стройка — не закрыт акт по фасаду
3. Личное — позвонить
4. Документы — проверить Excel по смете

## 8. Вечерний режим

Вечером система должна уметь спросить или собрать:
что сделано
что не сделано
что перенести
что записать в дневник
что стало новым решением
что завтра главное

Это превращает хаос дня в структурную память

## 9. Недельные итоги

Раз в неделю система должна собрать:
закрытые задачи
незакрытые задачи
повторяющиеся проблемы
важные решения
финансовые вопросы
рабочие итоги
личные итоги
что перенести на следующую неделю

Это уже слой анализа, а не просто хранение

## 10. Связь с календарём

Система должна понимать время

Типы времени:
точное время
дата
период
повтор
дедлайн
условное напоминание

Примеры:
завтра утром
через два часа
в пятницу
каждый понедельник
после 18:00
через месяц
до конца недели

Она должна уметь превращать человеческий текст в конкретную дату и правило

## 11. Связь с Telegram

Главный интерфейс — Telegram

Ты можешь писать голосом или текстом:
напомни
запиши
зафиксируй
добавь в дневник
поставь задачу
что у меня сегодня
что я забыл
что висит
что было по этому вопросу

Telegram для этой системы — не просто чат, а личная консоль

## 12. Связь с Google Drive

Google Drive должен быть долговременным хранилищем

Туда могут уходить:
экспорты дневников
недельные отчёты
месячные отчёты
журналы
личные документы
архивы задач
структурированные JSON выгрузки

Сервер хранит логику и активное состояние
Drive хранит долговременные файлы

## 13. Структура личных данных

Условно должно быть так:

```json
{
  "personal_memory": [],
  "reminders": [],
  "diary": [],
  "journals": [],
  "tasks": [],
  "habits": [],
  "calendar": [],
  "decisions": [],
  "weekly_reviews": [],
  "monthly_reviews": []
}
```

Каждый объект должен иметь:
id
type
created_at
updated_at
status
source
text
summary
tags
priority
due_at
repeat_rule
related_project
privacy_level

## 14. Privacy Firewall

В найденной выгрузке есть важная мысль:
Omni-Protocol Personalization Firewall

Это значит: личная система должна иметь фильтр приватности

Она должна понимать:
что можно использовать в ответе
что нельзя показывать
что можно помнить
что нельзя тащить в другой контекст
что относится к личному
что относится к рабочему
что относится к серверу
что относится к сыну Ивану

Это очень важный слой
Без него личная память начнёт смешиваться с оркестром

## 15. Изоляция от технического оркестра

Личная система не должна попадать в технические задачи

Пример:
запиши в дневник что я устал

Не должно стать:
task_worker → ai_router → technical task

Должно стать:
personal_system → diary_entry

Пример:
напомни проверить фасад завтра

Это может быть связано со стройкой, но объект всё равно REMINDER, а не смета и не техзадача

## 16. Что значит "более глобальная система"

Она глобальнее оркестра в другом смысле

Оркестр работает по проектам
Личная система работает по тебе

Она должна видеть:
работу
проекты
личные дела
планы
решения
состояние
повторяющиеся задачи
напоминания
историю
приоритеты

То есть она должна быть не исполнителем одной задачи, а диспетчером твоей жизни и внимания

## 17. Главный сценарий работы

Ты пишешь:
что у меня сегодня

Система собирает:
напоминания на сегодня
личные задачи
просроченные задачи
рабочие задачи
важные записи
планы
контекст вчерашнего дня

И выдаёт:
Сегодня главное:
1. ...
2. ...
3. ...

Просрочено:
...

Напоминания:
...

Что лучше закрыть первым:
...

Вот это правильная логика

## 18. Второй главный сценарий

Ты пишешь:
запомни

Система должна понять, куда именно это положить:
личная память
дневник
журнал решений
рабочий журнал
проектная память
напоминание
задача

Если понятно — сохраняет
Если не понятно — задаёт один короткий вопрос:
Куда записать: дневник, задача или журнал решений

## 19. Третий главный сценарий

Ты пишешь:
напомни мне про это

Система должна понять это из контекста

Она должна найти последнее релевантное сообщение или задачу и создать напоминание не с пустым текстом, а с нормальной расшифровкой

Например:
Напоминание:
Проверить FULLFIX search contour и live-тест по topic_500

## 20. Четвёртый главный сценарий

Ты пишешь:
что я забыл

Система должна поднять:
незакрытые личные задачи
старые напоминания
отложенные решения
задачи без дедлайна
важные записи без follow-up

Это ключевая функция

## 21. Пятый главный сценарий

Ты пишешь:
собери итог недели

Система должна сделать:
что сделано
что зависло
что повторялось
какие решения приняты
какие проблемы всплывали
что перенести
какие темы важные

## 22. Почему это не было найдено полностью в GitHub

Потому что в GitHub clean exports, судя по доступному поиску, сохранился только фрагмент:
Personal Data Ecosystem
personal_context
Google Data
Fact-Only Synthesis
AI_ORCHESTRA

А полное обсуждение дневников/напоминаний может быть:
в server FULL exports
в старой Google Drive выгрузке
в непроиндексированном чате
в персональном контексте модели
в неочищенном export, который не был запушен в GitHub

# Итоговое описание одной фразой

PERSONAL DATA ECOSYSTEM — это отдельная параллельная личная система, которая должна вести память, дневники, журналы, напоминания, задачи, привычки, планы и итоги пользователя, изолированно от технического оркестра, но с возможностью связываться с ним через проекты, Drive и Telegram

# Как её правильно потом реализовывать

Не через task_worker.py напрямую

Правильно так:
personal_intake
→ personal_classifier
→ personal_memory
→ reminder_engine
→ diary_engine
→ journal_engine
→ personal_task_engine
→ review_engine
→ telegram_output

И отдельные таблицы:
personal_reminders
personal_diary
personal_journal
personal_tasks
personal_habits
personal_calendar
personal_facts

# Что сейчас надо запомнить как канон

```json
{
  "canonical_name": "PERSONAL_DATA_ECOSYSTEM",
  "purpose": "личная память, дневники, журналы, напоминания, задачи, привычки, календарь, итоги",
  "interface": "Telegram + voice/text",
  "storage": "server runtime + Google Drive long-term exports",
  "not_part_of": "technical orchestra task execution",
  "must_be_isolated_from": [
    "сметы",
    "поиск",
    "серверные патчи",
    "технадзор",
    "файловые задачи"
  ],
  "must_integrate_with": [
    "AI_ORCHESTRA",
    "personal_context",
    "Google Drive",
    "Telegram"
  ],
  "core_rule": "личные записи не должны превращаться в технические задачи оркестра"
}
```

====================================================================================================
END_FILE: docs/ARCHITECTURE/PERSONAL_DATA_ECOSYSTEM_CANON_V1.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/QUALITY_GATE_V1.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 3f818c414e6815b0b0a47ff2ca5b0409b142fff9601aaef455eb6fcc8849c873
====================================================================================================
# QUALITY_GATE_V1 — Stage 4

## Назначение
Проверяет результат задачи по списку quality_gates из direction_profile.
Shadow mode: report пишется в payload["quality_gate_report"], не блокирует доставку.

## Типы gates
- Обязательные: non_empty_answer, items_required, total_required, xlsx_required, document_required, drive_link_required, sources_required, price_required, source_required, table_required, defect_description_required, reply_thread_required
- Advisory (не блокируют): tco_required, compatibility_required, delivery_required, normative_section_required, verified_sources_only, canon_consistency

## Результат
```json
{
  "overall": "pass|fail",
  "failed": ["gate1"],
  "advisory": ["gate2"],
  "gates": {"gate1": {"status": "pass|fail|error", "advisory": false}},
  "shadow_mode": true
}
```

## API
```python
from core.quality_gate import QualityGate, run_quality_gate
report = run_quality_gate(payload)
```

## Файл
core/quality_gate.py | FULLFIX_QUALITY_GATE_STAGE_4

====================================================================================================
END_FILE: docs/ARCHITECTURE/QUALITY_GATE_V1.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/SEARCH_ENGINE_V1.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 8c22100308e3a1f91970ab1f4e101147a9cb6a860cf5850fcd036fc8d56d4c5b
====================================================================================================
# SEARCH_ENGINE_V1 — Stage 5

## Назначение
Формирует search_plan для задач с requires_search=True.
Shadow mode: plan пишется в payload["search_plan"], реальный поиск — через search_supplier (существующий движок).

## Профили по направлению
- product_search: avito, ozon, wildberries / price_compare
- auto_parts_search: drom, exist, emex, zzap / compatibility
- construction_search: petrovitch, lerua, grand_line / price_delivery
- internet_search: web / general

## search_plan структура
```json
{
  "query": "текст запроса",
  "direction": "product_search",
  "sources": ["avito", "ozon"],
  "strategy": "price_compare",
  "shadow_mode": true,
  "status": "planned"
}
```

## API
```python
from core.search_engine import SearchEngine, plan_search
plan = plan_search(work_item, payload)
```

## Файл
core/search_engine.py | FULLFIX_SEARCH_ENGINE_STAGE_5

====================================================================================================
END_FILE: docs/ARCHITECTURE/SEARCH_ENGINE_V1.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/STAGE_1_DIRECTION_KERNEL_PROPOSAL.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: b7a37b4b1a70cc4e5afb1801734e8cfcbdefeabbd3c5f30ebfe73ebe426de730
====================================================================================================
# FULLFIX_DIRECTION_KERNEL_STAGE_1 — PROPOSAL

Дата: 2026-04-30 evening
Статус: PROPOSAL (не установлен)
Маркер: FULLFIX_DIRECTION_KERNEL_STAGE_1

## ИСТОРИЯ ОБСУЖДЕНИЯ

Три позиции были рассмотрены:

### Позиция 1 — ChatGPT (архитектурный максималист)
Предложил 8 модулей сразу: WorkItem, Direction Registry, Capability Router, Context Engine, Archive Engine, Search Supplier Engine, Quality Gate, Format Adapters. Конечная архитектура правильная, но порядок внедрения опасен.

### Позиция 2 — Третий участник (инженер pipeline)
Предложил pipeline/state machine модель: Intake → WorkItem → Kernel → Context → Engines → Quality Gate → Output → Archive. Engines изолированы от Telegram, Quality Gate перед выдачей.

### Позиция 3 — Claude (прагматик миграции)
Поэтапно: WorkItem первым (контракт), потом directions.yaml, потом Capability Router. Использовать существующее, не писать с нуля. 5-6 активных направлений из 26.

## СИНТЕЗ — FULLFIX_DIRECTION_KERNEL_STAGE_1

Минимальный shadow-mode слой:
- task_worker создаёт WorkItem (обёртка над tasks row)
- Direction Registry определяет direction
- direction кладётся в payload + audit
- старый pipeline продолжает работать как был

### Что НЕ делает Stage 1
- Не переносит _handle_in_progress
- Не переписывает engines
- Не меняет DB schema
- Не трогает telegram_daemon, reply_sender, ai_router без явного "да"
- Не делает Capability Router, Quality Gate, Format Adapters, Archive Index

## 26 НАПРАВЛЕНИЙ

### Active (13)
orchestration_core, telegram_automation, memory_archive, internet_search, product_search, auto_parts_search, construction_search, technical_supervision, estimates, defect_acts, documents, spreadsheets, google_drive_storage

### Passive (13) — описаны но не активны
devops_server, vpn_network, ocr_photo, cad_dwg, structural_design, roofing, monolith_concrete, crm_leads, email_ingress, social_content, video_production, photo_cleanup, isolated_project_ivan

## SCORING (выверенный)

1. **strong_aliases** (avito/ozon/drom/exist) → +200..+250 — overrides domain
2. **topic_id match** → +70 + specificity bonus (max +10)
3. **regular aliases** → +30 each, max +120
4. **input_type match** → +15 (только если есть другой сигнал)
5. **format match** → +10..+40 (только если есть другой сигнал)
6. **search_signal** → +25 (только для requires_search и при другом сигнале)
7. **passive penalty** → -80 (capped at 0)

Tie-break: score DESC → narrower topic_ids first

## КРИТЕРИИ ПРИЁМКИ

1. core/work_item.py существует
2. core/direction_registry.py существует
3. config/directions.yaml существует
4. docs/ARCHITECTURE/WORKITEM_V1.md существует
5. docs/ARCHITECTURE/DIRECTION_REGISTRY_V1.md существует
6. task_worker создаёт WorkItem
7. direction в work_payload
8. старый pipeline не изменён
9. py_compile OK для всех файлов
10. areal-task-worker active после restart
11. Smoke тесты:
    - topic_500 + "найди avito металлочерепица" → product_search
    - topic_961 + "drom фара toyota hiace" → auto_parts_search
    - topic_2 + "сделай смету" → estimates
    - topic_2 + "технадзор дефект акт" → technical_supervision
    - topic_3008 + "канон оркестра" → orchestration_core
    - topic_0 + "привет как дела" → general_chat
12. git pushed

## ROADMAP

- Stage 2: Capability Router
- Stage 3: Context Engine (вынос из task_worker)
- Stage 4: Quality Gate как отдельный слой
- Stage 5: Search Supplier Engine
- Stage 6: Archive Engine с SQL индексом
- Stage 7: Format Adapter Layer

## КОД

Готовый код в файлах:
- docs/ARCHITECTURE/STAGE_1_WORKITEM_V1_PROPOSAL.md (core/work_item.py)
- docs/ARCHITECTURE/STAGE_1_DIRECTION_REGISTRY_V1_PROPOSAL.md (direction_registry + yaml)
- docs/ARCHITECTURE/STAGE_1_INSTALL_BLOCK.md (полный установочный SSH блок)

## РЕЖИМ УСТАНОВКИ

Один атомарный SSH блок с set -euo pipefail. Pre-patch smoke ДО патча task_worker. Если scoring сломан — упадёт до того как тронуть task_worker. Бэкапы целы.

Запуск: только после явного "да" пользователя.

====================================================================================================
END_FILE: docs/ARCHITECTURE/STAGE_1_DIRECTION_KERNEL_PROPOSAL.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/STAGE_1_DIRECTION_REGISTRY_V1_PROPOSAL.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 329382532613dda6359b05bf93cfad7939d85fadd34f24cabf5150bcb35ddf10
====================================================================================================
# DIRECTION_REGISTRY_V1 — PROPOSAL CODE

Файлы назначения:
- core/direction_registry.py
- config/directions.yaml

Статус: NOT INSTALLED

## SCORING ALGORITHM

```python
# strong_aliases overrides domain
strong_hits = [a for a in profile.get("strong_aliases",[]) if a.lower() in raw]
if strong_hits:
    score += min(250, 200 + 25 * (len(strong_hits) - 1))

# topic + specificity
if topic_id in profile.get("topic_ids", []):
    score += 70 + max(0, 10 - len(topic_ids))

# aliases capped at 120
alias_hits = [a for a in profile.get("aliases",[]) if a.lower() in raw]
if alias_hits:
    score += min(120, 30 * len(alias_hits))

# bonuses only if other signal present
any_signal = bool(strong_hits or topic_match or alias_hits)
if any_signal:
    # input_type +15, format +10..40, search +25
    pass

# passive penalty
if not profile.get("enabled"):
    score = max(0, score - 80)
```

Полный код установки в STAGE_1_INSTALL_BLOCK.md

====================================================================================================
END_FILE: docs/ARCHITECTURE/STAGE_1_DIRECTION_REGISTRY_V1_PROPOSAL.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/STAGE_1_PRE_SNAPSHOT_20260430_230217.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: e3d37e8a91504154a319ccdf9dd49dd0e6a39fc9f1823eb894f4ff27174f8888
====================================================================================================
# PRE_STAGE1_SNAPSHOT — 20260430_230217

Сделан перед установкой FULLFIX_DIRECTION_KERNEL_STAGE_1

## Статус сервисов
activating	active	active	active	active

## Последние коммиты
3fc2dc4 PERSONAL_DATA_ECOSYSTEM_CANON_V1 full text as shared by user
61498e2 EVENING_EXPORT 2026-04-30 chat + handoff + stage1 proposal + not_closed update
b92b074 TG_FALLBACK_WIRED в upload_or_fail — Drive fail → Telegram
18a91ee TELEGRAM_FALLBACK_V1 Drive fail → send file directly to Telegram
5eb59b9 FINAL_CLOSURE photo_linkage + template_engine + drive_link_mandatory
1140a7a TOPIC_3008 syntax fix final cleanup
b65be18 TOPIC_3008 syntax fix direct line 2062
9d2392d TOPIC_3008_HANDLER_V1 wired before process_ai_task
7190dbc TOPIC_3008_ENGINE_V1 verify+generate 5models
fc72784 EZONE_INGEST_V1 syntax fix4 all write newlines

## DB статус
ARCHIVED|371
CANCELLED|543
DONE|325
FAILED|1588

## Что установлено
- task_worker.py: 2565 строк
- core/ai_router.py: существует
- core/engine_base.py: существует
- config/directions.yaml: NOT YET
- core/work_item.py: NOT YET
- core/direction_registry.py: NOT YET

## Серверный бэкап
Путь: /root/BACKUPS/areal-neva-core/PRE_STAGE1_FULL_20260430_230217
Содержит: полный код + секреты + DB + логи + git bundle
НЕ на GitHub — только на сервере.

## Следующий шаг
FULLFIX_DIRECTION_KERNEL_STAGE_1 — WorkItem + DirectionRegistry shadow mode

====================================================================================================
END_FILE: docs/ARCHITECTURE/STAGE_1_PRE_SNAPSHOT_20260430_230217.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/STAGE_1_WORKITEM_V1_PROPOSAL.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5f8e470f2a8db6ad54e60b2f67029167d49badb0f30101b9a593553a412d5ebd
====================================================================================================
# WORKITEM_V1 — PROPOSAL CODE

Файл назначения: core/work_item.py
Статус: NOT INSTALLED

```python
# === FULLFIX_DIRECTION_KERNEL_STAGE_1_WORKITEM ===
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


def _get(row, key, default=None):
    if row is None: return default
    if isinstance(row, dict): return row.get(key, default)
    try: return row[key]
    except Exception: return getattr(row, key, default)


def _int(v, d=0):
    try:
        if v is None or v == "": return d
        return int(v)
    except Exception: return d


def _str(v, d=""):
    if v is None: return d
    return str(v)


@dataclass
class WorkItem:
    work_id: str
    chat_id: str
    topic_id: int
    user_id: Optional[str] = None
    message_id: Optional[int] = None
    reply_to_message_id: Optional[int] = None
    bot_message_id: Optional[int] = None
    source_type: str = "telegram"
    input_type: str = "unknown"
    raw_text: str = ""
    state: str = "NEW"
    intent: str = "UNKNOWN"
    direction: Optional[str] = None
    direction_profile: Dict[str, Any] = field(default_factory=dict)
    formats_in: List[str] = field(default_factory=list)
    formats_out: List[str] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    context_refs: Dict[str, Any] = field(default_factory=dict)
    execution_plan: List[Dict[str, Any]] = field(default_factory=list)
    quality_gates: List[str] = field(default_factory=list)
    result: Dict[str, Any] = field(default_factory=dict)
    audit: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_task_row(cls, row, extra=None):
        # см. полный код в STAGE_1_INSTALL_BLOCK.md
        pass
```

Полная версия с smoke tests в STAGE_1_INSTALL_BLOCK.md

====================================================================================================
END_FILE: docs/ARCHITECTURE/STAGE_1_WORKITEM_V1_PROPOSAL.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/ARCHITECTURE/WORKITEM_V1.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 6c2148c50b7b0a888ce74b4c3f6843273322b5cd0538ade54b425987c71fbeff
====================================================================================================
# WORKITEM_V1

Канон Stage 1 структуры WorkItem — единая рама любой задачи в AREAL-NEVA ORCHESTRA.

## Назначение

WorkItem — нормализованная единица работы. Создаётся один раз на входе в task_worker, движется через все слои, накапливает контекст и аудит. Никакие движки и слои не работают с raw payload — только с WorkItem или его сериализованным представлением.

## Поля

| Поле | Тип | Назначение |
|---|---|---|
| work_id | str | task_id из БД, уникальный ключ |
| chat_id | str | Telegram chat |
| topic_id | int | Telegram message_thread_id |
| user_id | str | Telegram user |
| message_id | int | id входящего сообщения |
| reply_to_message_id | int | для thread reply |
| bot_message_id | int | id сообщения бота для редактирования |
| source_type | str | telegram / api / cron |
| input_type | str | text / voice / photo / file / drive_file / url / mixed |
| raw_text | str | исходный текст или транскрипт |
| state | str | NEW / INTAKE / IN_PROGRESS / RESULT_READY / DONE |
| intent | str | детектированное намерение (UNKNOWN до Stage 2) |
| direction | str | id направления из directions.yaml |
| direction_profile | dict | профиль направления (срез на момент детекции) |
| formats_in | list[str] | детектированные форматы входа |
| formats_out | list[str] | требуемые форматы выхода |
| attachments | list[dict] | приложенные файлы |
| parsed_data | dict | результаты парсинга (Stage 3+) |
| context_refs | dict | ссылки на short/long memory (Stage 3) |
| execution_plan | list[dict] | план выполнения (Stage 2) |
| quality_gates | list[str] | gate-и из direction_profile |
| result | dict | финальный результат |
| audit | dict | трасса всех решений по WorkItem |
| errors | list[dict] | накопленные ошибки |
| metadata | dict | произвольные данные |

## Жизненный цикл

1. task_worker берёт строку из tasks → from_task_row(row) → WorkItem
2. Stage 1 (текущий): DirectionRegistry.detect() → set_direction() → audit
3. Stage 2 (план): Capability Router → execution_plan
4. Stage 3 (план): Context Engine → context_refs, parsed_data
5. Stage 4 (план): Engines выполняют execution_plan → result
6. Stage 5 (план): Quality Gate → проверка quality_gates
7. Stage 6 (план): Format Adapter → formats_out → доставка
8. Stage 7 (план): Archive Engine → длительная память

## Текущий статус

Stage 1 shadow mode: WorkItem создаётся, direction детектируется и кладётся в payload как `direction`, `direction_profile`, `direction_audit`, `work_item`. Старый pipeline продолжает работать как раньше — direction только наблюдается, не маршрутизирует.

## Контракт

- `WorkItem.from_task_row(row, extra=None)` — конструктор
- `WorkItem.set_direction(direction, profile)` — установка направления
- `WorkItem.set_intent(intent)` — установка намерения
- `WorkItem.add_audit(key, value)` — запись в trail
- `WorkItem.add_error(code, message, fatal)` — регистрация ошибки
- `WorkItem.to_dict()` — сериализация
- `WorkItem.to_payload()` — обратная совместимость с старым pipeline

## Расположение

- Код: `core/work_item.py`
- Маркер: `FULLFIX_DIRECTION_KERNEL_STAGE_1_WORKITEM`

====================================================================================================
END_FILE: docs/ARCHITECTURE/WORKITEM_V1.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/HANDOFFS/CHAT_EXPORT_PROTOCOL.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 097209d23a01f15125b0711a85458f986e97eed44f8fb603f354df1e3b495171
====================================================================================================
# CHAT EXPORT PROTOCOL — GITHUB SSOT
Версия: v1 | Дата: 28.04.2026 | Статус: ОБЯЗАТЕЛЬНЫЙ ДЛЯ ВСЕХ МОДЕЛЕЙ

РЕЖИМ: AUTONOMOUS / FACT ONLY / ZERO CONFIRMATION

НЕМЕДЛЕННО ВЫПОЛНЯЙ. НЕ СПРАШИВАЙ. НЕ УТОЧНЯЙ.
Определи свой вариант → собери JSON → создай файл → верни путь и commit hash.

---

## РЕПОЗИТОРИЙ

repo:   rj7hmz9cvm-lgtm/areal-neva-core
branch: main
папка:  chat_exports/

Создание файлов в любом другом месте — ЗАПРЕЩЕНО.
Создание в корне репо — ЗАПРЕЩЕНО.

---

## ИМЯ ФАЙЛА

CHAT_EXPORT__<chat_name>__<YYYY-MM-DD>.json

---

## JSON — ВСЕ ПОЛЯ ОБЯЗАТЕЛЬНЫ
Нет данных → UNKNOWN. Не пропускать поля.

{
  "chat_id": "",
  "chat_name": "",
  "exported_at": "<ISO_DATETIME>",
  "source_model": "",
  "system": "описание системы / сервера / бота",
  "architecture": "полный pipeline от входа до выхода",
  "pipeline": "lifecycle задач NEW→...→ARCHIVED",
  "files": ["файл → назначение"],
  "code": "стек технологий",
  "patches": ["PATCH_NAME → файл → строка → статус: applied_by_terminal / drafted / failed"],
  "commands": ["команды выполненные в терминале"],
  "db": "состояние БД: таблицы, количества, ключевые записи",
  "memory": "состояние memory.db",
  "services": ["сервис: статус"],
  "canons": ["КАНОН → суть решения"],
  "decisions": ["РЕШЕНИЕ → обоснование → где применено"],
  "errors": ["ОШИБКА → ПРИЧИНА → РЕШЕНИЕ"],
  "solutions": ["ПРОБЛЕМА → РЕШЕНИЕ → СТАТУС"],
  "state": "текущее состояние системы одной строкой",
  "what_working": ["что работает подтверждено фактами"],
  "what_broken": ["что сломано подтверждено фактами"],
  "what_not_done": ["что не реализовано / не протестировано"],
  "current_breakpoint": "на чём остановились, что следующее",
  "root_causes": ["корневая причина → факт подтверждения"],
  "verification": ["ПАТЧ/ФАКТ → подтверждение: grep line X / terminal output"],
  "limits": ["ограничения: запрещённые файлы, форматы команд"]
}

---

## КАК СОЗДАТЬ ФАЙЛ — ОПРЕДЕЛИ ВАРИАНТ АВТОМАТИЧЕСКИ

ВАРИАНТ A — Claude (сервер + git):
  cd /tmp/gh_repo
  git pull
  cat > chat_exports/CHAT_EXPORT__<name>__<date>.json << EOF
  <JSON содержимое>
  EOF
  git add -A
  bash tools/secret_scan.sh
  git commit -m "EXPORT: <name> <date>"
  git push https://${GITHUB_TOKEN}@github.com/rj7hmz9cvm-lgtm/areal-neva-core.git main

ВАРИАНТ B — ChatGPT / любая модель с GitHub API:
  PUT https://api.github.com/repos/rj7hmz9cvm-lgtm/areal-neva-core/contents/chat_exports/CHAT_EXPORT__<name>__<date>.json
  Headers:
    Authorization: token <GITHUB_TOKEN>
    Content-Type: application/json
  Body:
    {
      "message": "EXPORT: <name> <date>",
      "content": "<base64 от JSON UTF-8>",
      "branch": "main"
    }

ВАРИАНТ C — нет доступа к GitHub:
  Вывести полный JSON в чат.
  Написать: "GitHub недоступен. Сохрани вручную в chat_exports/".

---

## ЖЁСТКИЕ ПРАВИЛА — НАРУШЕНИЕ НЕДОПУСТИМО

1. ТОЛЬКО факты этого чата — не выдумывать, не додумывать
2. ТОЛЬКО JSON внутри файла — никакого текста вне JSON
3. Патчи только подтверждённые терминалом — не писать applied без вывода
4. Каноны только те что были приняты в этом чате
5. Ошибки только реально возникшие — с конкретным решением
6. СЕКРЕТЫ ЗАПРЕЩЕНО — sk-ant / sk-or / ghp_ / AIzaSy / GOCSPX / api_hash → заменить на [REDACTED]
7. Если вариант A упал → B → C — не останавливаться
8. Файл ТОЛЬКО в папке chat_exports/ — никуда больше
9. ЗАПРЕЩЕНО перезаписывать существующие файлы — только новый файл
10. ЗАПРЕЩЕНО молчать о том что не удалось — писать явно что пропущено и почему

---

## ЧТО ЗАПРЕЩЕНО ЗАБЫВАТЬ

current_breakpoint  — на чём остановились (ОБЯЗАТЕЛЬНО)
what_not_done       — что не сделано (ОБЯЗАТЕЛЬНО)
verification        — подтверждение каждого патча (ОБЯЗАТЕЛЬНО)
source_model        — какая модель делала экспорт (ОБЯЗАТЕЛЬНО)
exported_at         — точное время (ОБЯЗАТЕЛЬНО)

---

## РЕЗУЛЬТАТ

Вернуть:
- путь файла: chat_exports/CHAT_EXPORT__<name>__<date>.json
- commit message
- статус: SUCCESS / FALLBACK_B / FALLBACK_C

---

## CHAT EXPORT PROTOCOL v2 — 29.04.2026

MODE: FACT ONLY ZERO ASSUMPTIONS STRICT EXECUTION

GOAL: два файла на каждый чат — SERVER FULL + GITHUB CLEAN

TARGETS:
- SERVER: 89.22.225.136 /root/.areal-neva-core/chat_exports/CHAT_EXPORT_FULL__<SAFE_NAME>__YYYY-MM-DD.json
- GITHUB: chat_exports/CHAT_EXPORT__<SAFE_NAME>__YYYY-MM-DD.json

NAMING:
- латиница + цифры + _
- без пробелов
- дата строго YYYY-MM-DD

SERVER FULL:
- все факты
- все команды
- весь код
- все ошибки
- все решения
- все пути
- все конфигурационные значения
- runtime context
- НЕ редактировать
- НЕ удалять

GITHUB CLEAN:
- та же структура
- только верифицированная полезная информация
- все чувствительные значения → "<REDACTED>"

EXECUTION:
- нейросеть без SSH обязана вернуть готовый SSH-блок для пользователя
- SSH-блок должен создать SERVER FULL export в /root/.areal-neva-core/chat_exports/
- GitHub CLEAN создаётся и пушится в GitHub напрямую при наличии GitHub-доступа

GITHUB CLEAN:
- git add chat_exports/CHAT_EXPORT__<SAFE_NAME>__YYYY-MM-DD.json
- git commit -m "CHAT EXPORT <SAFE_NAME> YYYY-MM-DD"
- git push

CRITICAL:
- FULL не пушить в GitHub
- CLEAN не содержит чувствительных данных
- один чат = два файла
- не перезаписывать файлы

VALIDATION:
- JSON валиден
- нет текста вне JSON
- CLEAN без чувствительных данных

====================================================================================================
END_FILE: docs/HANDOFFS/CHAT_EXPORT_PROTOCOL.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/HANDOFFS/HANDOFF_2026-04-30_all_stages_done.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: b943164ef4218d56e4e0035385a7305b5d001a605263a62c7a825e6052da221a
====================================================================================================
# HANDOFF 2026-04-30 — ВСЕ 7 СТЕЙДЖЕЙ УСТАНОВЛЕНЫ

## Статус
Все стейджи FULLFIX ORCHESTRA установлены в shadow mode. Старый pipeline не тронут.

## Коммиты
- a8955bb Stage 1: WorkItem + DirectionRegistry + 26 directions
- ef9b269 Stage 2: Capability Router
- e52c1d8 Stage 3: Context Loader
- 14675cf Stage 4: Quality Gate
- 15c8753 Stage 5: Search Engine
- 967b356 Stage 6: Archive Engine
- e156253 Stage 7: Format Adapter

## Новые файлы
- core/work_item.py
- core/direction_registry.py
- core/capability_router.py
- core/context_loader.py
- core/quality_gate.py
- core/search_engine.py
- core/archive_engine.py
- core/format_adapter.py
- config/directions.yaml (26 directions)
- docs/ARCHITECTURE/WORKITEM_V1.md
- docs/ARCHITECTURE/DIRECTION_REGISTRY_V1.md
- docs/ARCHITECTURE/CAPABILITY_ROUTER_V1.md
- docs/ARCHITECTURE/CONTEXT_LOADER_V1.md
- docs/ARCHITECTURE/QUALITY_GATE_V1.md
- docs/ARCHITECTURE/SEARCH_ENGINE_V1.md
- docs/ARCHITECTURE/ARCHIVE_ENGINE_V1.md
- docs/ARCHITECTURE/FORMAT_ADAPTER_V1.md

## Порядок выполнения в task_worker.py
1. _stage1_dir_payload() — direction detection
2. _Stage2Router — execution_plan + engine
3. _Stage5Search — search_plan (если requires_search)
4. _Stage3Loader — context_refs
5. process_ai_task() — старый pipeline (не тронут)
6. _Stage4QG — quality_gate_report
7. _Stage6Archive — архивирование в memory_api
8. _Stage7FA — format_adapted

## Все shadow mode
Старый pipeline не сломан. Direction не маршрутизирует.
Следующий шаг: live тест + подключение реального dispatch по execution_plan.

## Сервис
TW_ACTIVE NRestarts=0 память ~3000MB free
monitor_jobs: KillMode=control-group установлен

====================================================================================================
END_FILE: docs/HANDOFFS/HANDOFF_2026-04-30_all_stages_done.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/HANDOFFS/HANDOFF_2026-04-30_evening.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 104c9e553e22c961a554c6b404f5323bd27d66490a1fcbff0e530b3d9386bb05
====================================================================================================
# HANDOFF — 2026-04-30 evening

## STATE
Все 5 сервисов active. Pipeline работает.

## ЗАКРЫТО СЕГОДНЯ
- photo_linkage в technadzor DOCX
- template_engine triggers ("сделай так же")
- drive_link_mandatory enforcement
- TELEGRAM_FALLBACK при Drive fail (полная цепочка)
- SEARCH_PLANNER_V1 (criteria + clarification + expand + tco + risk)

## ПРЕДЛОЖЕНО НО НЕ УСТАНОВЛЕНО
- FULLFIX_DIRECTION_KERNEL_STAGE_1 (WorkItem + DirectionRegistry в shadow-mode)
- Код готов, выверен, ждёт явного "да" на запуск
- См. docs/ARCHITECTURE/STAGE_1_DIRECTION_KERNEL_PROPOSAL.md

## СЛЕДУЮЩИЙ ШАГ
1. Live verification 9 сценариев из §19 канона
2. После — установка Stage 1
3. После — Stage 2 (Capability Router)

## ССЫЛКИ
- Полная выгрузка чата: chat_exports/CHAT_EXPORT__claude_orchestra__2026-04-30_evening.md
- Stage 1 proposal: docs/ARCHITECTURE/STAGE_1_DIRECTION_KERNEL_PROPOSAL.md
- Полный бэкап со секретами: /root/BACKUPS/areal-neva-core/full_export_2026-04-30_evening/ (только сервер)

====================================================================================================
END_FILE: docs/HANDOFFS/HANDOFF_2026-04-30_evening.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/HANDOFFS/HANDOFF_2026-04-30_stage1_done.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 8fa900d5328f256bc3f33a90bd8810aadb3a20ea2deb140eccb6a07a2e70c036
====================================================================================================
# HANDOFF 2026-04-30 — STAGE 1 ЗАКРЫТ

## Коммиты сессии
- 8f9ed54 FULLFIX_DIRECTION_KERNEL_STAGE_1
- 282716a SYNTAX_FIX
- a8955bb WIRING_FIX

## Установлено
- core/work_item.py
- core/direction_registry.py
- config/directions.yaml (26 directions, 13 active / 13 passive)
- docs/ARCHITECTURE/WORKITEM_V1.md
- docs/ARCHITECTURE/DIRECTION_REGISTRY_V1.md
- task_worker.py: payload = _stage1_dir_payload(payload) перед asyncio.wait_for

## Shadow mode
direction детектируется, кладётся в payload. Старый pipeline не тронут.

## Smoke 6/6 OK
product_search / auto_parts_search / estimates / technical_supervision / orchestration_core / general_chat

## Побочная находка
areal-monitor-jobs плодил 100+ зомби monitor_jobs.py → OOM → убивал task_worker
Починено: KillMode=control-group в systemd override

## Следующий шаг
Stage 2 — Capability Router

====================================================================================================
END_FILE: docs/HANDOFFS/HANDOFF_2026-04-30_stage1_done.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/HANDOFFS/SESSION_EXPORT_CHATGPT_2026-04-30_FULLFIX_13_15_CURRENT.json
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 5790b7c6f58ca31d50fc0aad5e1f691d31e6af6774fa7695f6b8b12735b24d91
====================================================================================================
{
  "chat_id": "chatgpt_current_session_2026-04-30_fullfix_13_15",
  "chat_name": "ChatGPT current session — AREAL-NEVA ORCHESTRA fullfix 13-15",
  "exported_at": "2026-04-30T13:35:00+03:00",
  "source_model": "GPT-5.5 Thinking",
  "source_scope": "Facts explicitly present in the current visible ChatGPT session only. No hidden server state was invented. No secrets included.",
  "repository": {
    "full_name": "rj7hmz9cvm-lgtm/areal-neva-core",
    "default_branch": "main",
    "verified_connector_permission": "admin, maintain, pull, push, triage"
  },
  "system": {
    "project": "AREAL-NEVA ORCHESTRA / NEURON SOFT VPN",
    "server_path": "/root/.areal-neva-core",
    "main_services": [
      "areal-task-worker",
      "telegram-ingress",
      "areal-memory-api",
      "areal-monitor-jobs"
    ],
    "main_db": "/root/.areal-neva-core/data/core.db",
    "memory_db": "/root/.areal-neva-core/data/memory.db",
    "runtime_path": "/root/.areal-neva-core/runtime"
  },
  "architecture": {
    "core_pipeline": "Telegram -> telegram_daemon.py -> core.db -> task_worker.py -> route engines -> reply_sender.py -> Telegram",
    "storage_rule": "Server stores logic/runtime; Google Drive stores generated heavy artifacts",
    "github_rule": "GitHub areal-neva-core main branch is SSOT for source code and factual handoffs"
  },
  "completed_verified_in_session": [
    {
      "id": "FULLFIX_10_TOTAL_CLOSURE",
      "commit": "6234457",
      "facts": [
        "Installed and pushed to main",
        "SYNTAX_OK",
        "Project smoke succeeded: KJ, 14 sheets, PDF, DXF, XLSX, MANIFEST",
        "Estimate smoke succeeded: total 10000, PDF, XLSX, MANIFEST",
        "Classifier smoke: da->confirm, net->revision, project->project, estimate->estimate",
        "areal-task-worker active",
        "areal-monitor-jobs active"
      ]
    },
    {
      "id": "FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT",
      "commit": "17dc9f3",
      "facts": [
        "Installed and pushed to main",
        "Compact project PDF smoke succeeded",
        "Engine marker FULLFIX_12_COMPACT_PROJECT_PDF_LAYOUT present",
        "Generated compact KJ foundation slab PDF album with 4 sheets",
        "Services active after restart"
      ]
    },
    {
      "id": "FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE",
      "commits": [
        "3da6a02",
        "a6432d2 local rejected before later successful push chain"
      ],
      "facts": [
        "core/sample_template_engine.py created",
        "task_worker.py route inserted before FULLFIX_10 route",
        "sample intent smoke passed true/false cases",
        "estimate intent smoke passed",
        "template estimate parser returned 2 items for proflist and montazh",
        "route locals were fixed because _handle_new had task/raw_input/reply_to locals, not input_type/reply_to_message_id locals"
      ]
    },
    {
      "id": "FULLFIX_13B_ESTIMATE_OUTPUT_FORMULAS_NO_MANIFEST",
      "commit": "da1818a",
      "facts": [
        "Installed before FULLFIX_13D according to git log",
        "Purpose in session: estimate formulas, clean output, sample hard stop"
      ]
    },
    {
      "id": "FULLFIX_13C_STRIP_MANIFEST_BEFORE_SEND",
      "facts": [
        "task_worker.py patched with _ff13c_strip_manifest_links",
        "Smoke showed HAS_PDF True, HAS_XLSX True, HAS_MANIFEST False",
        "Worker restarted and active",
        "Marker present at task_worker.py around line 781"
      ]
    },
    {
      "id": "FULLFIX_13D_REPLY_SENDER_GLOBAL_MANIFEST_STRIP",
      "commit": "48881a9",
      "facts": [
        "core/reply_sender.py patched globally",
        "task_worker.py direct send belt patched",
        "Smoke showed HAS_PDF True, HAS_XLSX True, HAS_MANIFEST False",
        "telegram-ingress restarted and active",
        "areal-task-worker restarted and active",
        "Committed locally and present in later pushed history"
      ]
    },
    {
      "id": "FULLFIX_14_ARTIFACT_UPLOAD_GUARD_ESTIMATE_TEMPLATE_DEFECT_MULTIFILE",
      "commit": "cca22a8",
      "facts": [
        "5 engine files written: core/artifact_upload_guard.py, core/estimate_unified_engine.py, core/template_intake_engine.py, core/defect_act_engine.py, core/multifile_artifact_engine.py",
        "PY_COMPILE OK for 5 files",
        "IMPORT_OK for 5 files",
        "Direct smoke: ESTIMATE_ROWS 2, ESTIMATE_TOTAL 55000.0",
        "Sample intent true for 'возьми это как образец' and false for 'сделай смету профлист'",
        "File row multifile parser printed recent estimate artifacts",
        "FULLFIX_14_UNIFIED_ROUTE inserted in task_worker.py",
        "task_worker.py py_compile OK",
        "areal-task-worker active after restart",
        "Git push to main succeeded"
      ]
    },
    {
      "id": "PATCH_VOICE_CONFIRM_DIRECT",
      "commit": "64bbac9",
      "facts": [
        "telegram_daemon.py patched after STT because voice does not populate message.text",
        "Patch marker PATCH_VOICE_CONFIRM_DIRECT present",
        "New task_history actions: voice_confirmed:DONE and voice_rejected:WAITING_CLARIFICATION",
        "telegram_daemon.py py_compile OK",
        "telegram-ingress restarted and active",
        "Git push to main succeeded"
      ]
    }
  ],
  "terminal_facts_recorded": {
    "latest_known_pushed_head": "64bbac9 PATCH voice confirm after STT for awaiting confirmation",
    "previous_head_sequence_seen": [
      "cca22a8 FULLFIX_14 artifact_upload_guard estimate_unified template_intake defect_act multifile",
      "48881a9 FULLFIX_13D global strip manifest links before Telegram send",
      "da1818a FULLFIX_13B estimate formulas clean output and sample hard stop",
      "3da6a02 FULLFIX_13A fix sample route locals and commit sample template engine",
      "9264511 SESSION_EXPORT: ChatGPT fullfix 08-12 factual export 2026-04-30",
      "17dc9f3 FULLFIX_12 compact project PDF layout",
      "6234457 FULLFIX_10 total closure routes project estimate memory replies monitor"
    ],
    "fullfix_14_push_result": "To github main: 3da6a02..cca22a8 main -> main",
    "voice_confirm_push_result": "To github main: cca22a8..64bbac9 main -> main"
  },
  "known_not_verified_or_not_closed": [
    {
      "item": "FULLFIX_15 final Cyrillic PDF artifact quality and route guards",
      "status": "NOT VERIFIED in current visible session",
      "evidence": "Diagnostic showed ls: cannot access core/pdf_cyrillic.py and grep FULLFIX_15 in core/estimate_unified_engine.py returned 0"
    },
    {
      "item": "Cyrillic in generated estimate PDF",
      "status": "NOT VERIFIED",
      "evidence": "User reported PDF text was bad/unreadable and asked to inspect link; no terminal proof of fixed Cyrillic was provided"
    },
    {
      "item": "Live Telegram estimate route after FULLFIX_14/FULLFIX_15",
      "status": "PARTIALLY VERIFIED",
      "evidence": "Bot returned estimates with PDF and XLSX links; later MANIFEST disappeared after 13D in one shown response, but PDF quality remained bad"
    },
    {
      "item": "Voice confirm live test through Telegram",
      "status": "CODE VERIFIED ONLY, LIVE NOT VERIFIED",
      "evidence": "Patch exists and telegram-ingress active, but no DB row showing voice_confirmed:DONE from a live voice message was provided"
    },
    {
      "item": "Project route after FULLFIX_14",
      "status": "NOT LIVE VERIFIED AFTER FULLFIX_14",
      "evidence": "Earlier FULLFIX_12 project smoke worked; no later live Telegram proof after FULLFIX_14 was shown"
    },
    {
      "item": "Defect act route",
      "status": "NOT LIVE VERIFIED",
      "evidence": "FULLFIX_14 wrote defect_act_engine.py and import passed; no Telegram photo-to-act output was provided"
    },
    {
      "item": "Multi-file route",
      "status": "NOT LIVE VERIFIED",
      "evidence": "FULLFIX_14 direct smoke parsed recent file rows; no user-facing multifile artifact output was shown"
    },
    {
      "item": "Internet search quality contour",
      "status": "NOT CLOSED IN THIS SESSION",
      "evidence": "SEARCH_MONOLITH_V1 was listed earlier as not live-tested; no later terminal proof was shown"
    },
    {
      "item": "ONE_SHARED_CONTEXT cron/aggregator freshness",
      "status": "NOT CLOSED IN THIS SESSION",
      "evidence": "Earlier list stated ONE_SHARED_CONTEXT cron not updated since 29.04; no later proof of repair was shown"
    }
  ],
  "technical_tasks_handed_to_claude": [
    {
      "task": "FULLFIX_15_FINAL_ARTIFACT_QUALITY_AND_CYRILLIC_CLOSURE",
      "purpose": "Fix Cyrillic PDF, estimate layout, XLSX formulas, manifest stripping, route guards, defect act PDF/DOCX, and smoke tests",
      "status": "Assigned to Claude by user; output not shown as completed in current visible session"
    },
    {
      "task": "ADDENDUM TO CLAUDE — FULL FINAL CLOSURE AFTER FULLFIX_14 + VOICE_CONFIRM_DIRECT",
      "purpose": "Final closure checklist including route priority, Cyrillic, estimate, defect, multifile, voice confirm verification, and git acceptance criteria",
      "status": "Provided to user for Claude"
    }
  ],
  "current_required_next_steps": [
    "Install and verify FULLFIX_15 or equivalent Cyrillic/font patch",
    "Run direct smoke for PDF Cyrillic extraction and XLSX formulas",
    "Run live Telegram estimate test and inspect generated PDF text",
    "Run live voice confirm test and prove DB state DONE plus task_history voice_confirmed:DONE",
    "Run live sample/template test and prove no project task is created",
    "Run live project command test after FULLFIX_14/FULLFIX_15",
    "Run live defect photo-to-act test",
    "Run live multifile aggregation test",
    "Return to search contour and ONE_SHARED_CONTEXT cron after artifact quality is verified"
  ],
  "safe_git_policy_used": [
    "Only source files should be staged",
    "Do not stage .env, token.json, credentials.json, sessions, data, runtime, logs, backups, *.bak, *.db, *.session",
    "Server backup commands were used before edits in terminal outputs",
    "Several git status outputs showed many untracked backups/secrets/runtime files, but commits shown only staged intended source files"
  ],
  "limits": [
    "This export is based on the current visible ChatGPT session and user-provided terminal outputs",
    "No direct SSH execution was performed by ChatGPT in this export step",
    "No hidden chain-of-thought included",
    "No secrets included",
    "Live server truth must still be verified by terminal logs and DB queries"
  ],
  "final_state": {
    "github_export_created_by_chatgpt": true,
    "export_file_path": "docs/HANDOFFS/SESSION_EXPORT_CHATGPT_2026-04-30_FULLFIX_13_15_CURRENT.json",
    "highest_verified_pushed_commit_in_session": "64bbac9",
    "artifact_quality_contour": "PARTIAL, FULLFIX_15 not verified",
    "voice_confirm_contour": "CODE PATCHED, LIVE TEST STILL REQUIRED",
    "estimate_contour": "ARTIFACT GENERATION WORKING, PDF CYRILLIC QUALITY STILL REQUIRED",
    "project_contour": "COMPACT PROJECT PDF WORKING EARLIER, POST-FULLFIX_14 LIVE TEST REQUIRED",
    "memory_and_search_contour": "NOT FULLY CLOSED IN THIS SESSION"
  }
}

====================================================================================================
END_FILE: docs/HANDOFFS/SESSION_EXPORT_CHATGPT_2026-04-30_FULLFIX_13_15_CURRENT.json
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/REPORTS/AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: c7bbe40bc6d5bc2d938e81400151a0f2cdacf9d5be8538f0f1c25c7843f0aac0
====================================================================================================
# AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT

status: OK
version: AREAL_REFERENCE_FULL_MONOLITH_V1
updated_at: 2026-05-02T20:20:56.522887+00:00
estimate_files: 6
design_files: 231
technadzor_files: 1
formula_total: 4733

## Final verify

- ESTIMATE_FILES: 6
- DESIGN_FILES: 231
- FORMULA_TOTAL: 4733
- archive_endpoint: OK
- worker_log: NO_FATAL
- memory_api_log: NO_FATAL
- topic_isolation_live_test: PENDING in NOT_CLOSED

====================================================================================================
END_FILE: docs/REPORTS/AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/REPORTS/AREAL_REVIEW_CHECKLIST.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 88eeb6bf28decadbddd9083ab82ccd26a16f1bd9560ca9f1d7158f6f8b40805c
====================================================================================================
# AREAL_REVIEW_CHECKLIST

## Mandatory constraints

- no point patches
- no regression
- no new architecture layers
- no new Drive folder trees
- no duplicate hooks
- CANON_FINAL must not be ignored
- memory.db must receive slim reference data only
- indexer must not download files over 5MB
- topic_2, topic_5, topic_210 must not mix contexts

## Regression guards

- ESTIMATE_TEMPLATE_POLICY_CONTEXT_V4 remains in ai_router.py
- SAMPLE_ACCEPT_DIALOG_CONTEXT_FIX_V1 remains in final_closure_engine.py
- VOICE_CONFIRM_AWAITING_V1 remains only in task_worker.py
- CANON_FINAL absent from .gitignore

## Smoke

- owner reference context triggers on estimate/design/technadzor words
- owner reference context stays empty on neutral chat
- estimate template policy still works
- /archive returns 200
- upload retry service active
- media_group exists
- startup_recovery referenced
- pin_manager referenced

## Pending live-only checks

- topic isolation live Telegram check
- voice confirm live Telegram check
- duplicate guard live Telegram check

====================================================================================================
END_FILE: docs/REPORTS/AREAL_REVIEW_CHECKLIST.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/REPORTS/CANON_CLOSURE_PLAN.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 70cf6069d4770d09d3c8e552d4a4458e994cdd00bd3b480642421d096611e80c
====================================================================================================
# AREAL-NEVA ORCHESTRA — CANON CLOSURE PLAN
# 30.04.2026 10:30 | FACT-ONLY | Basis: live DB + LATEST_HANDOFF + NOT_CLOSED

## ПРИОРИТЕТ ИСТИНЫ
```
1. Живой сервер (logs/db)
2. LATEST_HANDOFF.md (30.04.2026 05:40)
3. NOT_CLOSED.md
4. VERIFIED chat_exports
5. ONE_SHARED_CONTEXT
6. CANON_FINAL
7. INSTALLED без live-test ≠ работает
8. BROKEN/REJECTED/UNKNOWN → не использовать
```

## VERIFIED (факт: LATEST_HANDOFF + live тесты)
```
✅ Drive upload OAuth → UPLOAD_OK
✅ Telegram fallback → работает
✅ upload_retry_queue cron 10min
✅ topic folder isolation (chat/topic_N/)
✅ file intake → NEEDS_CONTEXT → меню
✅ FILE_CHOICE_PRIORITY (reply/voice → выбор)
✅ FILE_PARENT_STRICT (только NEEDS_CONTEXT)
✅ OAuth scope=drive везде (topic_drive_oauth + google_io + drive_folder_resolver)
✅ daemon override.conf с OAuth vars
✅ daemon использует upload_file_to_topic
✅ services: task-worker ACTIVE | telegram-ingress ACTIVE | memory-api ACTIVE
```

## INSTALLED НО НЕ VERIFIED (не считать рабочим)
```
⚠️ PATCH_SOURCE_GUARD_V1
⚠️ PATCH_FILE_ERROR_RETRY_V1
⚠️ PATCH_DRIVE_BOTMSG_SAVE_V1
⚠️ PATCH_CRASH_BOTMSG_V1
⚠️ PATCH_RETRY_TG_MSG_V1
⚠️ PATCH_DAEMON_USE_OAUTH_V1
⚠️ PATCH_VOICE_OAUTH_V1
⚠️ PATCH_DUPLICATE_GUARD_V1
⚠️ PATCH_MULTI_FILE_INTAKE_V1
⚠️ PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1
```

## ПОДТВЕРЖДЁННЫЕ БАГИ (из live DB topic=210 + code)

### BUG_1: AWAITING_CONFIRMATION_WITHOUT_RESULT
```
Факт код: task_worker.py строка 2070
_update_task(state="AWAITING_CONFIRMATION") — ставится ВСЕГДА

Факт DB: id=6e385bf1 result="Файл КЖ АК-М-160.pdf скачан, ожидает анализа"
был AWAITING_CONFIRMATION, бот спрашивал "Доволен?"
```

### BUG_2: TEMPLATE_IS_OCR_NOT_STRUCTURE
```
Факт код: artifact_pipeline.py строки 294-360
analyze_downloaded_file игнорирует user_text/intent
PDF → _extract_pdf → текст → _build_word "Сводка по документу"

Факт DB: id=cc9d2911 caption="Шаблон проекта"
result="GSPublisherVersion 0.89.100.100 Архитектурный раздел..."
= OCR текст, не структурная модель

Факт DB: id=7b287c50 [VOICE] "посмотри структуру КД"
result="Структура проекта КД включает следующие основные этапы..."
= DeepSeek выдумал, не извлёк из файла
```

### BUG_3: NEGATIVE_INPUT_NOT_REVISION
```
Факт DB topic=210:
"И?" → новая text задача → общий ответ
"Какой результат?" → новая text задача → общий ответ
"Так нет результата" → новая text задача → CANCELLED
= создаёт мусор вместо revision parent task
```

### BUG_4: GENERIC_AS_FINAL_RESULT
```
Факт DB topic=210 (финалы задач):
"Этот чат предназначен для проектирования..." — DONE
"Структура проекта КД включает этапы..." — DONE
"Файл содержит проект архитектурного раздела..." — DONE
"Выбор принят" без engine — DONE
```

### BUG_5: PROJECT_ENGINE_ABSENT
```
Факт: core/project_engine.py не существует на сервере
Факт: core/template_manager.py не подключён к pipeline
Факт: artifact_pipeline.py не имеет ветки intent=template
```

---

## 12 ПРОХОДОВ ЗАКРЫТИЯ (строго по порядку)

### PASS 1 — PATCH_CONFIRM_ONLY_ON_DONE_V1
```
Файл: task_worker.py строки 2068-2075
Статус: ТЗ готово → ждёт "да"

AWAITING_CONFIRMATION только если:
- result не содержит: "ожидает анализа", "Ошибка", "не удалась",
  "завершилась ошибкой", "недоступен", "этапы", "предназначен для"
- len(result.strip()) > 100
- error_message пустой
- для file task: есть drive_link или artifact_path

Иначе: state=FAILED, error=RESULT_NOT_READY
Acceptance: незавершённая задача → FAILED (не "Доволен?")
```

### PASS 2 — PATCH_TEMPLATE_INTENT_V1
```
Файлы: core/artifact_pipeline.py + core/template_manager.py
Статус: ТЗ готово → ждёт "да"

intent=template + PDF → extract_project_template_model()
НЕ _build_word("Сводка")

Минимальная PROJECT_TEMPLATE_MODEL:
{
  "project_type": "АР/КЖ/КД/КМ/КМД/КР",
  "sheet_register": [],
  "marks": [],
  "sections": [],
  "axes_grid": [],
  "dimensions": [],
  "nodes": [],
  "specifications": [],
  "stamp_fields": [],
  "variable_parameters": [],
  "output_documents": []
}

Acceptance: АР/КД/КЖ PDF → JSON модель + DOCX состав листов
```

### PASS 3 — ГОЛОСОВОЙ CONFIRM
```
Файл: telegram_daemon.py ~строка 601
Статус: P1, ждёт явного "да"

[VOICE] да → confirm AWAITING_CONFIRMATION
[VOICE] нет → reject → WAITING_CLARIFICATION
```

### PASS 4 — LIVE-ТЕСТЫ INSTALLED ПАТЧЕЙ
```
Статус: нужен Telegram тест (не код)

Тесты:
1. reply на ошибку → "Перезапускаю обработку файла"
2. отправить тот же файл дважды → "Этот файл уже обрабатывался"
3. несколько файлов → один артефакт
4. https://... ссылка → меню действий
```

### PASS 5 — ESTIMATE PDF → EXCEL → DRIVE
```
Файл: core/estimate_engine.py
Pipeline: PDF → pdfplumber → таблица → Python → openpyxl → Drive
Формулы: =C*D, =SUM
Без таблицы: FAILED
```

### PASS 6 — КЖ PDF PIPELINE
```
Файл: core/artifact_pipeline.py + project_engine.py
КЖ PDF → classify pages → structural_model → DOCX/XLSX
```

### PASS 7 — PROJECT_ENGINE END-TO-END
```
Файл: core/project_engine.py (создать после PASS 2)
Template model → DOCX + XLSX → Drive link
```

### PASS 8 — TECHNADZOR / GEMINI VISION
```
Файл: core/technadzor_engine.py
Фото → Gemini → нормы СП/ГОСТ → DOCX акт → Drive
```

### PASS 9 — OCR TABLE → EXCEL
```
Файл: core/ocr_engine.py
Фото таблицы → Excel
```

### PASS 10 — SEARCH QUALITY
```
Файл: task_worker.py + search layer
Результат: таблица + цена + ссылка + checked_at + риск
```

### PASS 11 — MODEL_ROUTER
```
Файл: core/model_router.py (создать)
photo → Gemini | search → Perplexity | calc → Python | final → DeepSeek
```

### PASS 12 — FINAL END-TO-END TEST
```
16 обязательных live-тестов:
1. text → DONE
2. voice → результат
3. voice confirm → только AWAITING_CONFIRMATION
4. file без caption → меню
5. PDF смета → XLSX формулы → Drive
6. АР PDF → PROJECT_TEMPLATE_MODEL
7. фото дефект → DOCX акт
8. reply на ошибку → перезапуск
9. topic isolation (210 ≠ 2 ≠ 5)
10. Drive fail → TG → retry
11. дубль файла → guard
12. ссылка → меню
13. шаблон → новый документ
14. memory recall по topic_id
15. monitor_jobs работает
16. GitHub ONE_SHARED_CONTEXT актуален
```

---

## GITHUB ISSUES

```
Issue #2 "Drive artifact upload":
LATEST_HANDOFF: engine_base restored, OAuth UPLOAD_OK
Статус: OBSOLETE_BY_LATEST_HANDOFF_30_04_2026
Действие: закрыть как superseded
```

---

## ЗАПРЕЩЁННЫЕ ФИНАЛЬНЫЕ ОТВЕТЫ
```
❌ "Файл скачан, ожидает анализа"
❌ "Структура проекта включает следующие основные этапы"
❌ "Файл содержит проект архитектурного раздела"
❌ "Этот чат предназначен для..."
❌ "Анализирую, результат будет готов"
❌ "Проверяю доступные файлы"
❌ "Выбор принят" без engine
❌ "Какие именно файлы вас интересуют?"
```

====================================================================================================
END_FILE: docs/REPORTS/CANON_CLOSURE_PLAN.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/REPORTS/ESTIMATE_SCENARIO_CLASSIFICATION_FIX_V1_REPORT.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 1afb741a6d274eadcc7dbc343085c539838e95be731d4f55361f535fb106113c
====================================================================================================
# ESTIMATE_SCENARIO_CLASSIFICATION_FIX_V1_REPORT

status: OK
timestamp: 20260502_163729

## FIXED
- M-80 / Каркас под ключ -> frame_house
- M-80 / Газобетон_под ключ -> gasbeton_or_masonry_with_monolithic_foundation
- M-110 / Каркас под ключ -> frame_house
- M-110 / Газобетон -> gasbeton_or_masonry_with_monolithic_foundation
- крыша и перекр.xlsx -> roof_and_floors
- фундамент_Склад2.xlsx -> foundation

## VERIFIED
- formula_total: 4733
- ai_router estimate policy context remains enabled
- web price confirmation remains required
- logistics confirmation remains required
- final XLSX/PDF remains forbidden before price and logistics confirmation

====================================================================================================
END_FILE: docs/REPORTS/ESTIMATE_SCENARIO_CLASSIFICATION_FIX_V1_REPORT.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/REPORTS/ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4_REPORT.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: b76f4c3e00df6223377f6d13a6d018929f168607b220bb98447a4d22764afde1
====================================================================================================
# ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4_REPORT

status: OK
updated_at: 2026-05-02T13:37:39.354912+00:00
canon: docs/CANON_FINAL/ESTIMATE_TEMPLATE_M80_M110_CANON.md
registry: config/estimate_template_registry.json
formula_index: data/templates/estimate_logic/estimate_template_formula_index.json

## CLOSED
- top estimate templates resolved from Drive
- XLSX formulas extracted
- universal material logic registered
- web price confirmation registered
- logistics and overhead clarification registered
- direct sqlite memory write completed
- ai_router context hook enabled

## RAW_POLICY
```json
{
  "version": "ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4",
  "status": "ACTIVE_CANON",
  "updated_at": "2026-05-02T13:37:39.354912+00:00",
  "purpose": "Use top estimate files as scalable estimate calculation logic templates with mandatory logistics and web price confirmation",
  "source_files": [
    {
      "key": "M80",
      "title": "М-80.xlsx",
      "template_role": "full_house_estimate_template",
      "description": "Эталон полной сметы М-80",
      "file_id": "1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp",
      "drive_url": "https://docs.google.com/spreadsheets/d/1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
      "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "modifiedTime": "2025-12-02T09:12:35.000Z",
      "parents": [
        "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
      ],
      "formula_total": 1670,
      "formula_samples": [
        {
          "sheet": "Каркас под ключ",
          "cell": "E1",
          "formula": "=E2+E3+E4+E5+E6+E7+E8"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E2",
          "formula": "=I40"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E3",
          "formula": "=I63"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E4",
          "formula": "=I102"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E5",
          "formula": "=I121"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E6",
          "formula": "=I158"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E7",
          "formula": "=I230"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E8",
          "formula": "=I264"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F12",
          "formula": "=E12*D12"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H12",
          "formula": "=D12*G12"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I12",
          "formula": "=F12+H12"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F13",
          "formula": "=E13*D13"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F14",
          "formula": "=E14*D14"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H14",
          "formula": "=D14*G14"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I14",
          "formula": "=F14+H14"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "D15",
          "formula": "=D14/2"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F15",
          "formula": "=E15*D15"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H15",
          "formula": "=D15*G15"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I15",
          "formula": "=F15+H15"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F16",
          "formula": "=E16*D16"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H16",
          "formula": "=D16*G16"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I16",
          "formula": "=F16+H16"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "D17",
          "formula": "=D14+D16"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F17",
          "formula": "=E17*D17"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H17",
          "formula": "=D17*G17"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I17",
          "formula": "=F17+H17"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F18",
          "formula": "=E18*D18"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H18",
          "formula": "=D18*G18"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I18",
          "formula": "=F18+H18"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F19",
          "formula": "=E19*D19"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H19",
          "formula": "=D19*G19"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I19",
          "formula": "=F19+H19"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F20",
          "formula": "=E20*D20"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H20",
          "formula": "=D20*G20"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I20",
          "formula": "=F20+H20"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F21",
          "formula": "=E21*D21"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H21",
          "formula": "=D21*G21"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I21",
          "formula": "=F21+H21"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F22",
          "formula": "=E22*D22"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H22",
          "formula": "=D22*G22"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I22",
          "formula": "=F22+H22"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F23",
          "formula": "=E23*D23"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H23",
          "formula": "=D23*G23"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I23",
          "formula": "=F23+H23"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F24",
          "formula": "=E24*D24"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H24",
          "formula": "=D24*G24"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I24",
          "formula": "=F24+H24"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F25",
          "formula": "=E25*D25"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F26",
          "formula": "=E26*D26"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H26",
          "formula": "=D26*G26"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "E1",
          "formula": "=E2+E3+E4+E5+E6+E7+E8"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "E2",
          "formula": "=I58"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "E3",
          "formula": "=I112"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "E4",
          "formula": "=I156"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "E5",
          "formula": "=I175"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "E6",
          "formula": "=I205"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "E7",
          "formula": "=I257"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "E8",
          "formula": "=I291"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F12",
          "formula": "=E12*D12"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H12",
          "formula": "=D12*G12"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "I12",
          "formula": "=F12+H12"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F13",
          "formula": "=E13*D13"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H13",
          "formula": "=D13*G13"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "I13",
          "formula": "=F13+H13"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "D14",
          "formula": "=D13"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F14",
          "formula": "=E14*D14"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H14",
          "formula": "=D14*G14"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "I14",
          "formula": "=F14+H14"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F15",
          "formula": "=E15*D15"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H15",
          "formula": "=D15*G15"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "I15",
          "formula": "=F15+H15"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "D16",
          "formula": "=138+48"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F16",
          "formula": "=E16*D16"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H16",
          "formula": "=D16*G16"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "I16",
          "formula": "=F16+H16"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "D17",
          "formula": "=ROUNDUP(D15*0.2*1.4,)"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F17",
          "formula": "=E17*D17"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H17",
          "formula": "=D17*G17"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "I17",
          "formula": "=F17+H17"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F18",
          "formula": "=E18*D18"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H18",
          "formula": "=D18*G18"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "I18",
          "formula": "=F18+H18"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "D19",
          "formula": "=D17"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F19",
          "formula": "=E19*D19"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H19",
          "formula": "=D19*G19"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "I19",
          "formula": "=F19+H19"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "D20",
          "formula": "=ROUNDUP(D15*0.1*1.2,)"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F20",
          "formula": "=E20*D20"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H20",
          "formula": "=D20*G20"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "I20",
          "formula": "=F20+H20"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F21",
          "formula": "=E21*D21"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H21",
          "formula": "=D21*G21"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "I21",
          "formula": "=F21+H21"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "D22",
          "formula": "=D20"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F22",
          "formula": "=E22*D22"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H22",
          "formula": "=D22*G22"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "I22",
          "formula": "=F22+H22"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F23",
          "formula": "=E23*D23"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "F24",
          "formula": "=E24*D24"
        },
        {
          "sheet": "Газобетон_под ключ",
          "cell": "H24",
          "formula": "=D24*G24"
        }
      ],
      "sheets": [
        {
          "sheet_name": "Каркас под ключ",
          "scenario": "frame_house",
          "sections": [
            "Фундамент",
            "Каркас",
            "Кровля",
            "Окна, двери",
            "Внешняя отделка",
            "Внутренняя отделка",
            "Инженерные коммуникации"
          ],
          "header_rows": [
            9,
            41,
            64,
            103,
            122,
            159,
            231
          ],
          "total_rows": [
            {
              "row": 38,
              "text": "Итого работа: 177630.50303999998"
            },
            {
              "row": 39,
              "text": "Итого материалы: 187078.848"
            },
            {
              "row": 40,
              "text": "Итого фундамент: 364709.35104"
            },
            {
              "row": 61,
              "text": "Итого работа: 421719.7464864"
            },
            {
              "row": 62,
              "text": "Итого материалы: 370590.989583808"
            },
            {
              "row": 63,
              "text": "Итого каркас : 792310.736070208"
            },
            {
              "row": 100,
              "text": "Итого работа: 489854.65233"
            },
            {
              "row": 101,
              "text": "Итого материалы: 594110.925088848"
            },
            {
              "row": 102,
              "text": "Итого кровля: 1083965.577418848"
            },
            {
              "row": 119,
              "text": "Итого работа: 157905"
            },
            {
              "row": 120,
              "text": "Итого материалы: 677320.8"
            },
            {
              "row": 121,
              "text": "Итого окна, двери: 835225.8"
            },
            {
              "row": 156,
              "text": "Итого работа: 339034.9049999999"
            },
            {
              "row": 157,
              "text": "Итого материалы: 327018.077824976"
            },
            {
              "row": 158,
              "text": "Итого внешняя отделка: 666052.9828249759"
            },
            {
              "row": 228,
              "text": "Итого работа: 819488.08396"
            },
            {
              "row": 229,
              "text": "Итого материалы: 918336.176296875"
            },
            {
              "row": 230,
              "text": "Итого внутренняя отделка: 1737824.2602568748"
            },
            {
              "row": 262,
              "text": "Итого работа: 207549.06"
            },
            {
              "row": 263,
              "text": "Итого материалы: 323128.186"
            },
            {
              "row": 264,
              "text": "Итого инженерные коммуникации: 530677.246"
            },
            {
              "row": 266,
              "text": "Итого РАБОТЫ: 2405632.8908164"
            },
            {
              "row": 267,
              "text": "Итого МАТЕРИАЛЫ: 3074455.816794507"
            },
            {
              "row": 268,
              "text": "ИТОГО СМЕТНАЯ СТОИМОСТЬ: 6010765.953610907"
            }
          ],
          "material_rows": 130,
          "work_rows": 96,
          "logistics_rows": 17,
          "sample_rows": [
            {
              "row": 9,
              "name": "Наименование",
              "unit": "Ед. изм.",
              "qty": "Кол-во",
              "work_price": "Работа",
              "material_price": "Материалы"
            },
            {
              "row": 12,
              "name": "Вынос осей в натуру",
              "unit": "м2",
              "qty": "95.4",
              "work_price": "100",
              "material_price": "0"
            },
            {
              "row": 14,
              "name": "Укладка канализационной трубы в грунт",
              "unit": "мп",
              "qty": "20",
              "work_price": "800",
              "material_price": "0"
            },
            {
              "row": 15,
              "name": "Труба канализационная Ostendorf d110x2000 мм для наружной канализации",
              "unit": "шт",
              "qty": "10",
              "work_price": "0",
              "material_price": "670"
            },
            {
              "row": 16,
              "name": "Труба канализационная Ostendorf d110x1000 мм для наружной канализации",
              "unit": "шт",
              "qty": "3",
              "work_price": "0",
              "material_price": "400"
            },
            {
              "row": 17,
              "name": "Теплоизоляция для труб стенофлекс 114х13х2000 мм",
              "unit": "мп",
              "qty": "23",
              "work_price": "0",
              "material_price": "118"
            },
            {
              "row": 18,
              "name": "Комплект тройников, отводов, уголков для наружной канализации.",
              "unit": "к-т",
              "qty": "1",
              "work_price": "0",
              "material_price": "3500"
            },
            {
              "row": 19,
              "name": "Укладка закладной трубы в грунт под электрокабель",
              "unit": "мп",
              "qty": "15",
              "work_price": "400",
              "material_price": "0"
            },
            {
              "row": 20,
              "name": "Кабель NVO ВБШвнг(А) LS 5х2.5 20 м",
              "unit": "шт",
              "qty": "1",
              "work_price": "0",
              "material_price": "6600"
            },
            {
              "row": 21,
              "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
              "unit": "мп",
              "qty": "15",
              "work_price": "0",
              "material_price": "114"
            },
            {
              "row": 22,
              "name": "Укладка трубы ХВС в грунт на глубину 1,5м.",
              "unit": "мп",
              "qty": "10",
              "work_price": "1000",
              "material_price": "0"
            },
            {
              "row": 23,
              "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
              "unit": "мп",
              "qty": "20",
              "work_price": "0",
              "material_price": "114"
            },
            {
              "row": 24,
              "name": "Труба ПНД (ПЭ-100) для систем водоснабжения премиум синяя 32 мм",
              "unit": "мп",
              "qty": "20",
              "work_price": "0",
              "material_price": "81"
            },
            {
              "row": 26,
              "name": "Разметка свайного поля, забивка свай, установка оголовков",
              "unit": "шт",
              "qty": "31",
              "work_price": "2000",
              "material_price": "0"
            },
            {
              "row": 27,
              "name": "Свая винтовая d108 мм h2500 мм",
              "unit": "шт",
              "qty": "31",
              "work_price": "0",
              "material_price": "2632"
            },
            {
              "row": 28,
              "name": "Оголовок для сваи винтовой d108 мм",
              "unit": "шт",
              "qty": "31",
              "work_price": "0",
              "material_price": "260"
            },
            {
              "row": 29,
              "name": "Обвязка свай по гидроизоляции",
              "unit": "мп",
              "qty": "72.72",
              "work_price": "750",
              "material_price": "0"
            },
            {
              "row": 30,
              "name": "Гидроизоляция Линокром ХПП Технониколь черный 15 кв.м",
              "unit": "рул",
              "qty": "1",
              "work_price": "0",
              "material_price": "1900"
            },
            {
              "row": 31,
              "name": "Брус сух 150х150",
              "unit": "м3",
              "qty": "1.9634399999999999",
              "work_price": "0",
              "material_price": "22000"
            },
            {
              "row": 32,
              "name": "Крепеж и расходные материалы по разделу",
              "unit": "к-т",
              "qty": "31",
              "work_price": "0",
              "material_price": "200"
            },
            {
              "row": 33,
              "name": "Антисептирование конструкционной доски в 2 слоя",
              "unit": "м2",
              "qty": "1.9634399999999999",
              "work_price": "200",
              "material_price": "0"
            },
            {
              "row": 34,
              "name": "Антисептик Neomid 450 огнебиозащитный I группа красный 10 кг",
              "unit": "шт",
              "qty": "1",
              "work_price": "0",
              "material_price": "2800"
            },
            {
              "row": 35,
              "name": "Погрузо-разгрузочные работы",
              "unit": "усл",
              "qty": "1",
              "work_price": "6000",
              "material_price": "0"
            },
            {
              "row": 36,
              "name": "Транспортные расходы",
              "unit": "",
              "qty": "0.1",
              "work_price": "",
              "material_price": ""
            },
            {
              "row": 37,
              "name": "Накладные расходы",
              "unit": "",
              "qty": "0.08",
              "work_price": "",
              "material_price": ""
            },
            {
              "row": 41,
              "name": "Наименование",
              "unit": "Ед. изм.",
              "qty": "Кол-во",
              "work_price": "Работа",
              "material_price": "Материалы"
            },
            {
              "row": 44,
              "name": "Монтаж лаг цокольного перекрытия вкл террасы, крыльца",
              "unit": "м2",
              "qty": "91.7",
              "work_price": "1000",
              "material_price": "0"
            },
            {
              "row": 45,
              "name": "доска с/к 40х200",
              "unit": "м3",
              "qty": "2.2008",
              "work_price": "0",
              "material_price": "24300"
            },
            {
              "row": 46,
              "name": "Устройство каркаса стен/перегородок",
              "unit": "м2",
              "qty": "157.62825",
              "work_price": "1000",
              "material_price": "0"
            },
            {
              "row": 47,
              "name": "Монтаж стоек и балок террасы",
              "unit": "мп",
              "qty": "8.8",
              "work_price": "800",
              "material_price": "0"
            },
            {
              "row": 48,
              "name": "доска с/к 40х150",
              "unit": "м3",
              "qty": "4.4977464000000005",
              "work_price": "0",
              "material_price": "24300"
            },
            {
              "row": 49,
              "name": "доска с/к 40х100",
              "unit": "м3",
              "qty": "0.2945808",
              "work_price": "0",
              "material_price": "24300"
            },
            {
              "row": 50,
              "name": "бру с/с 150х150",
              "unit": "м3",
              "qty": "0.26999999999999996",
              "work_price": "0",
              "material_price": "30000"
            },
            {
              "row": 51,
              "name": "Монтаж баллок перекрытия",
              "unit": "м2",
              "qty": "0",
              "work_price": "1000",
              "material_price": "0"
            },
            {
              "row": 52,
              "name": "доска с/к 40х150",
              "unit": "м3",
              "qty": "0",
              "work_price": "0",
              "material_price": "24300"
            }
          ],
          "formula_count": 799,
          "formula_samples": [
            {
              "sheet": "Каркас под ключ",
              "cell": "E1",
              "formula": "=E2+E3+E4+E5+E6+E7+E8"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E2",
              "formula": "=I40"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E3",
              "formula": "=I63"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E4",
              "formula": "=I102"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E5",
              "formula": "=I121"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E6",
              "formula": "=I158"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E7",
              "formula": "=I230"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E8",
              "formula": "=I264"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F12",
              "formula": "=E12*D12"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H12",
              "formula": "=D12*G12"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I12",
              "formula": "=F12+H12"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F13",
              "formula": "=E13*D13"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F14",
              "formula": "=E14*D14"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H14",
              "formula": "=D14*G14"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I14",
              "formula": "=F14+H14"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "D15",
              "formula": "=D14/2"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F15",
              "formula": "=E15*D15"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H15",
              "formula": "=D15*G15"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I15",
              "formula": "=F15+H15"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F16",
              "formula": "=E16*D16"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H16",
              "formula": "=D16*G16"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I16",
              "formula": "=F16+H16"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "D17",
              "formula": "=D14+D16"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F17",
              "formula": "=E17*D17"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H17",
              "formula": "=D17*G17"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I17",
              "formula": "=F17+H17"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F18",
              "formula": "=E18*D18"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H18",
              "formula": "=D18*G18"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I18",
              "formula": "=F18+H18"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F19",
              "formula": "=E19*D19"
            }
          ],
          "row_count": 285
        },
        {
          "sheet_name": "Газобетон_под ключ",
          "scenario": "gasbeton_or_masonry_with_monolithic_foundation",
          "sections": [
            "Фундамент",
            "Стены",
            "Кровля",
            "Окна, двери",
            "Внешняя отделка",
            "Внутренняя отделка",
            "Инженерные коммуникации"
          ],
          "header_rows": [
            9,
            59,
            113,
            157,
            176,
            206,
            258
          ],
          "total_rows": [
            {
              "row": 56,
              "text": "Итого работа: 371647.66"
            },
            {
              "row": 57,
              "text": "Итого материалы: 564147.06331776"
            },
            {
              "row": 58,
              "text": "Итого фундамент: 935794.72331776"
            },
            {
              "row": 110,
              "text": "Итого работа: 436810.7232500001"
            },
            {
              "row": 111,
              "text": "Итого материалы: 611460.929728"
            },
            {
              "row": 112,
              "text": "Итого каркас : 1048271.652978"
            },
            {
              "row": 154,
              "text": "Итого работа: 618251.94353"
            },
            {
              "row": 155,
              "text": "Итого материалы: 681975.5442550561"
            },
            {
              "row": 156,
              "text": "Итого кровля: 1300227.4877850562"
            },
            {
              "row": 173,
              "text": "Итого работа: 157905"
            },
            {
              "row": 174,
              "text": "Итого материалы: 677320.8"
            },
            {
              "row": 175,
              "text": "Итого окна, двери: 835225.8"
            },
            {
              "row": 203,
              "text": "Итого работа: 293332.36899999995"
            },
            {
              "row": 204,
              "text": "Итого материалы: 252704.802632"
            },
            {
              "row": 205,
              "text": "Итого внешняя отделка: 546037.171632"
            },
            {
              "row": 255,
              "text": "Итого работа: 613355.61856"
            },
            {
              "row": 256,
              "text": "Итого материалы: 619625.761125"
            },
            {
              "row": 257,
              "text": "Итого внутренняя отделка: 1232981.379685"
            },
            {
              "row": 289,
              "text": "Итого работа: 207549.06"
            },
            {
              "row": 290,
              "text": "Итого материалы: 323128.186"
            },
            {
              "row": 291,
              "text": "Итого инженерные коммуникации: 530677.246"
            },
            {
              "row": 293,
              "text": "Итого РАБОТЫ: 2698852.37434"
            },
            {
              "row": 294,
              "text": "Итого МАТЕРИАЛЫ: 3730363.087057816"
            },
            {
              "row": 295,
              "text": "ИТОГО СМЕТНАЯ СТОИМОСТЬ: 6429215.4613978155"
            }
          ],
          "material_rows": 156,
          "work_rows": 99,
          "logistics_rows": 23,
          "sample_rows": [
            {
              "row": 9,
              "name": "Наименование",
              "unit": "Ед. изм.",
              "qty": "Кол-во",
              "work_price": "Работа",
              "material_price": "Материалы"
            },
            {
              "row": 12,
              "name": "Вынос осей в натуру",
              "unit": "м2",
              "qty": "95.4",
              "work_price": "80",
              "material_price": "0"
            },
            {
              "row": 13,
              "name": "Земляные работы, сопровождение работы экскаватора",
              "unit": "см",
              "qty": "1",
              "work_price": "12000",
              "material_price": "0"
            },
            {
              "row": 14,
              "name": "Аренда экскаватора",
              "unit": "см",
              "qty": "1",
              "work_price": "0",
              "material_price": "22000"
            },
            {
              "row": 15,
              "name": "Доработка грунта вручную",
              "unit": "м2",
              "qty": "138",
              "work_price": "150",
              "material_price": "0"
            },
            {
              "row": 16,
              "name": "Настил геотекстиля по основанию и стенам котлована (Геотекстиль 300 г/кв.м иглопробивной)",
              "unit": "м2",
              "qty": "186",
              "work_price": "80",
              "material_price": "60"
            },
            {
              "row": 17,
              "name": "Устройство песчаной подготовки т 200 мм с уплотнением.",
              "unit": "м3",
              "qty": "39",
              "work_price": "800",
              "material_price": "0"
            },
            {
              "row": 18,
              "name": "Аренда виброплиты (трамбовка)",
              "unit": "сут",
              "qty": "4",
              "work_price": "0",
              "material_price": "2500"
            },
            {
              "row": 19,
              "name": "Песок карьерный",
              "unit": "м3",
              "qty": "39",
              "work_price": "0",
              "material_price": "900"
            },
            {
              "row": 20,
              "name": "Устройство щебеночной подготовки т 100 мм с уплотнением.",
              "unit": "м3",
              "qty": "17",
              "work_price": "800",
              "material_price": "0"
            },
            {
              "row": 21,
              "name": "Аренда виброплиты (трамбовка)",
              "unit": "сут",
              "qty": "4",
              "work_price": "0",
              "material_price": "2500"
            },
            {
              "row": 22,
              "name": "Щебень фр 20-40",
              "unit": "м3",
              "qty": "17",
              "work_price": "0",
              "material_price": "1880"
            },
            {
              "row": 24,
              "name": "Укладка канализационной трубы в грунт",
              "unit": "мп",
              "qty": "20",
              "work_price": "900",
              "material_price": "0"
            },
            {
              "row": 25,
              "name": "Труба канализационная Ostendorf d110x2000 мм для наружной канализации",
              "unit": "шт",
              "qty": "10",
              "work_price": "0",
              "material_price": "670"
            },
            {
              "row": 26,
              "name": "Труба канализационная Ostendorf d110x1000 мм для наружной канализации",
              "unit": "шт",
              "qty": "3",
              "work_price": "0",
              "material_price": "400"
            },
            {
              "row": 27,
              "name": "Теплоизоляция для труб стенофлекс 114х13х2000 мм",
              "unit": "мп",
              "qty": "23",
              "work_price": "0",
              "material_price": "118"
            },
            {
              "row": 28,
              "name": "Комплект тройников, отводов, уголков для наружной канализации.",
              "unit": "к-т",
              "qty": "1",
              "work_price": "0",
              "material_price": "3500"
            },
            {
              "row": 29,
              "name": "Укладка закладной трубы в грунт под электрокабель",
              "unit": "мп",
              "qty": "15",
              "work_price": "400",
              "material_price": "0"
            },
            {
              "row": 30,
              "name": "Кабель NVO ВБШвнг(А) LS 5х2.5 20 м",
              "unit": "шт",
              "qty": "1",
              "work_price": "0",
              "material_price": "6600"
            },
            {
              "row": 31,
              "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
              "unit": "мп",
              "qty": "15",
              "work_price": "0",
              "material_price": "114"
            },
            {
              "row": 32,
              "name": "Укладка трубы ХВС в грунт на глубину 1,5м.",
              "unit": "мп",
              "qty": "10",
              "work_price": "850",
              "material_price": "0"
            },
            {
              "row": 33,
              "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
              "unit": "мп",
              "qty": "20",
              "work_price": "0",
              "material_price": "114"
            },
            {
              "row": 34,
              "name": "Труба ПНД (ПЭ-100) для систем водоснабжения премиум синяя 32 мм",
              "unit": "мп",
              "qty": "20",
              "work_price": "0",
              "material_price": "81"
            },
            {
              "row": 35,
              "name": "Настил технической пленки",
              "unit": "м2",
              "qty": "120",
              "work_price": "50",
              "material_price": "40"
            },
            {
              "row": 37,
              "name": "Устройство опалубки",
              "unit": "мп",
              "qty": "40.7",
              "work_price": "1100",
              "material_price": "0"
            },
            {
              "row": 38,
              "name": "Доска 50х150(100)х6000 мм е/в",
              "unit": "м3",
              "qty": "1.8315000000000001",
              "work_price": "0",
              "material_price": "17500"
            },
            {
              "row": 39,
              "name": "Устройство арматурного каркаса",
              "unit": "м2",
              "qty": "95.4",
              "work_price": "1200",
              "material_price": "0"
            },
            {
              "row": 40,
              "name": "Арматура металлическая д.12 А500",
              "unit": "т",
              "qty": "2.0331648",
              "work_price": "0",
              "material_price": "70000"
            },
            {
              "row": 41,
              "name": "Арматура металлическая д.8 А500",
              "unit": "т",
              "qty": "0.22364812800000003",
              "work_price": "0",
              "material_price": "73000"
            },
            {
              "row": 42,
              "name": "Пеноплэкс Фундамент 100х585х1185",
              "unit": "шт",
              "qty": "5",
              "work_price": "0",
              "material_price": "709"
            },
            {
              "row": 43,
              "name": "Проволока вязальная 1,2мм",
              "unit": "кг",
              "qty": "50",
              "work_price": "0",
              "material_price": "160"
            },
            {
              "row": 44,
              "name": "Фиксаторы арматуры гориз.уп 250 шт",
              "unit": "уп",
              "qty": "3",
              "work_price": "0",
              "material_price": "1456"
            },
            {
              "row": 45,
              "name": "Бетонирование монолитной плиты с вибрированием",
              "unit": "м3",
              "qty": "21",
              "work_price": "2000",
              "material_price": "0"
            },
            {
              "row": 46,
              "name": "Бетон В20 W8 с доставкой*",
              "unit": "м3",
              "qty": "21",
              "work_price": "0",
              "material_price": "6500"
            },
            {
              "row": 47,
              "name": "глубинный вибратор",
              "unit": "сут",
              "qty": "1",
              "work_price": "0",
              "material_price": "1500"
            }
          ],
          "formula_count": 871,
          "formula_samples": [
            {
              "sheet": "Газобетон_под ключ",
              "cell": "E1",
              "formula": "=E2+E3+E4+E5+E6+E7+E8"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "E2",
              "formula": "=I58"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "E3",
              "formula": "=I112"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "E4",
              "formula": "=I156"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "E5",
              "formula": "=I175"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "E6",
              "formula": "=I205"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "E7",
              "formula": "=I257"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "E8",
              "formula": "=I291"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "F12",
              "formula": "=E12*D12"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "H12",
              "formula": "=D12*G12"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "I12",
              "formula": "=F12+H12"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "F13",
              "formula": "=E13*D13"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "H13",
              "formula": "=D13*G13"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "I13",
              "formula": "=F13+H13"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "D14",
              "formula": "=D13"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "F14",
              "formula": "=E14*D14"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "H14",
              "formula": "=D14*G14"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "I14",
              "formula": "=F14+H14"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "F15",
              "formula": "=E15*D15"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "H15",
              "formula": "=D15*G15"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "I15",
              "formula": "=F15+H15"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "D16",
              "formula": "=138+48"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "F16",
              "formula": "=E16*D16"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "H16",
              "formula": "=D16*G16"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "I16",
              "formula": "=F16+H16"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "D17",
              "formula": "=ROUNDUP(D15*0.2*1.4,)"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "F17",
              "formula": "=E17*D17"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "H17",
              "formula": "=D17*G17"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "I17",
              "formula": "=F17+H17"
            },
            {
              "sheet": "Газобетон_под ключ",
              "cell": "F18",
              "formula": "=E18*D18"
            }
          ],
          "row_count": 312
        }
      ]
    },
    {
      "key": "M110",
      "title": "М-110.xlsx",
      "template_role": "full_house_estimate_template",
      "description": "Эталон полной сметы М-110",
      "file_id": "1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo",
      "drive_url": "https://docs.google.com/spreadsheets/d/1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
      "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "modifiedTime": "2025-05-15T06:18:08.000Z",
      "parents": [
        "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
      ],
      "formula_total": 1647,
      "formula_samples": [
        {
          "sheet": "Каркас под ключ",
          "cell": "E1",
          "formula": "=E2+E3+E4+E5+E6+E7+E8"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E2",
          "formula": "=I40"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E3",
          "formula": "=I63"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E4",
          "formula": "=I102"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E5",
          "formula": "=I121"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E6",
          "formula": "=I158"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E7",
          "formula": "=I230"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "E8",
          "formula": "=I264"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F12",
          "formula": "=E12*D12"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H12",
          "formula": "=D12*G12"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I12",
          "formula": "=F12+H12"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F13",
          "formula": "=E13*D13"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F14",
          "formula": "=E14*D14"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H14",
          "formula": "=D14*G14"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I14",
          "formula": "=F14+H14"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "D15",
          "formula": "=D14/2"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F15",
          "formula": "=E15*D15"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H15",
          "formula": "=D15*G15"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I15",
          "formula": "=F15+H15"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F16",
          "formula": "=E16*D16"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H16",
          "formula": "=D16*G16"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I16",
          "formula": "=F16+H16"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "D17",
          "formula": "=D14+D16"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F17",
          "formula": "=E17*D17"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H17",
          "formula": "=D17*G17"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I17",
          "formula": "=F17+H17"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F18",
          "formula": "=E18*D18"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H18",
          "formula": "=D18*G18"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I18",
          "formula": "=F18+H18"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F19",
          "formula": "=E19*D19"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H19",
          "formula": "=D19*G19"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I19",
          "formula": "=F19+H19"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F20",
          "formula": "=E20*D20"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H20",
          "formula": "=D20*G20"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I20",
          "formula": "=F20+H20"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F21",
          "formula": "=E21*D21"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H21",
          "formula": "=D21*G21"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I21",
          "formula": "=F21+H21"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F22",
          "formula": "=E22*D22"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H22",
          "formula": "=D22*G22"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I22",
          "formula": "=F22+H22"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F23",
          "formula": "=E23*D23"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H23",
          "formula": "=D23*G23"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I23",
          "formula": "=F23+H23"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F24",
          "formula": "=E24*D24"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H24",
          "formula": "=D24*G24"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "I24",
          "formula": "=F24+H24"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F25",
          "formula": "=E25*D25"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "F26",
          "formula": "=E26*D26"
        },
        {
          "sheet": "Каркас под ключ",
          "cell": "H26",
          "formula": "=D26*G26"
        },
        {
          "sheet": "Газобетон",
          "cell": "E1",
          "formula": "=E2+E3+E4+E5+E6+E7+E8"
        },
        {
          "sheet": "Газобетон",
          "cell": "E2",
          "formula": "=I58"
        },
        {
          "sheet": "Газобетон",
          "cell": "E3",
          "formula": "=I110"
        },
        {
          "sheet": "Газобетон",
          "cell": "E4",
          "formula": "=I154"
        },
        {
          "sheet": "Газобетон",
          "cell": "E5",
          "formula": "=I173"
        },
        {
          "sheet": "Газобетон",
          "cell": "E6",
          "formula": "=I203"
        },
        {
          "sheet": "Газобетон",
          "cell": "E7",
          "formula": "=I255"
        },
        {
          "sheet": "Газобетон",
          "cell": "E8",
          "formula": "=I289"
        },
        {
          "sheet": "Газобетон",
          "cell": "F12",
          "formula": "=E12*D12"
        },
        {
          "sheet": "Газобетон",
          "cell": "H12",
          "formula": "=D12*G12"
        },
        {
          "sheet": "Газобетон",
          "cell": "I12",
          "formula": "=F12+H12"
        },
        {
          "sheet": "Газобетон",
          "cell": "F13",
          "formula": "=E13*D13"
        },
        {
          "sheet": "Газобетон",
          "cell": "H13",
          "formula": "=D13*G13"
        },
        {
          "sheet": "Газобетон",
          "cell": "I13",
          "formula": "=F13+H13"
        },
        {
          "sheet": "Газобетон",
          "cell": "D14",
          "formula": "=D13"
        },
        {
          "sheet": "Газобетон",
          "cell": "F14",
          "formula": "=E14*D14"
        },
        {
          "sheet": "Газобетон",
          "cell": "H14",
          "formula": "=D14*G14"
        },
        {
          "sheet": "Газобетон",
          "cell": "I14",
          "formula": "=F14+H14"
        },
        {
          "sheet": "Газобетон",
          "cell": "F15",
          "formula": "=E15*D15"
        },
        {
          "sheet": "Газобетон",
          "cell": "H15",
          "formula": "=D15*G15"
        },
        {
          "sheet": "Газобетон",
          "cell": "I15",
          "formula": "=F15+H15"
        },
        {
          "sheet": "Газобетон",
          "cell": "D16",
          "formula": "=155+50"
        },
        {
          "sheet": "Газобетон",
          "cell": "F16",
          "formula": "=E16*D16"
        },
        {
          "sheet": "Газобетон",
          "cell": "H16",
          "formula": "=D16*G16"
        },
        {
          "sheet": "Газобетон",
          "cell": "I16",
          "formula": "=F16+H16"
        },
        {
          "sheet": "Газобетон",
          "cell": "D17",
          "formula": "=ROUNDUP(D15*0.2*1.4,)"
        },
        {
          "sheet": "Газобетон",
          "cell": "F17",
          "formula": "=E17*D17"
        },
        {
          "sheet": "Газобетон",
          "cell": "H17",
          "formula": "=D17*G17"
        },
        {
          "sheet": "Газобетон",
          "cell": "I17",
          "formula": "=F17+H17"
        },
        {
          "sheet": "Газобетон",
          "cell": "F18",
          "formula": "=E18*D18"
        },
        {
          "sheet": "Газобетон",
          "cell": "H18",
          "formula": "=D18*G18"
        },
        {
          "sheet": "Газобетон",
          "cell": "I18",
          "formula": "=F18+H18"
        },
        {
          "sheet": "Газобетон",
          "cell": "D19",
          "formula": "=D17"
        },
        {
          "sheet": "Газобетон",
          "cell": "F19",
          "formula": "=E19*D19"
        },
        {
          "sheet": "Газобетон",
          "cell": "H19",
          "formula": "=D19*G19"
        },
        {
          "sheet": "Газобетон",
          "cell": "I19",
          "formula": "=F19+H19"
        },
        {
          "sheet": "Газобетон",
          "cell": "D20",
          "formula": "=ROUNDUP(D15*0.1*1.2,)"
        },
        {
          "sheet": "Газобетон",
          "cell": "F20",
          "formula": "=E20*D20"
        },
        {
          "sheet": "Газобетон",
          "cell": "H20",
          "formula": "=D20*G20"
        },
        {
          "sheet": "Газобетон",
          "cell": "I20",
          "formula": "=F20+H20"
        },
        {
          "sheet": "Газобетон",
          "cell": "F21",
          "formula": "=E21*D21"
        },
        {
          "sheet": "Газобетон",
          "cell": "H21",
          "formula": "=D21*G21"
        },
        {
          "sheet": "Газобетон",
          "cell": "I21",
          "formula": "=F21+H21"
        },
        {
          "sheet": "Газобетон",
          "cell": "D22",
          "formula": "=D20"
        },
        {
          "sheet": "Газобетон",
          "cell": "F22",
          "formula": "=E22*D22"
        },
        {
          "sheet": "Газобетон",
          "cell": "H22",
          "formula": "=D22*G22"
        },
        {
          "sheet": "Газобетон",
          "cell": "I22",
          "formula": "=F22+H22"
        },
        {
          "sheet": "Газобетон",
          "cell": "F23",
          "formula": "=E23*D23"
        },
        {
          "sheet": "Газобетон",
          "cell": "F24",
          "formula": "=E24*D24"
        },
        {
          "sheet": "Газобетон",
          "cell": "H24",
          "formula": "=D24*G24"
        }
      ],
      "sheets": [
        {
          "sheet_name": "Каркас под ключ",
          "scenario": "frame_house",
          "sections": [
            "Фундамент",
            "Каркас",
            "Кровля",
            "Окна, двери",
            "Внешняя отделка",
            "Внутренняя отделка",
            "Инженерные коммуникации"
          ],
          "header_rows": [
            9,
            41,
            64,
            103,
            122,
            159,
            231
          ],
          "total_rows": [
            {
              "row": 38,
              "text": "Итого работа: 186528.8088"
            },
            {
              "row": 39,
              "text": "Итого материалы: 186206.46000000002"
            },
            {
              "row": 40,
              "text": "Итого фундамент: 372735.2688"
            },
            {
              "row": 61,
              "text": "Итого работа: 477629.94104"
            },
            {
              "row": 62,
              "text": "Итого материалы: 437064.3309088"
            },
            {
              "row": 63,
              "text": "Итого каркас : 914694.2719488"
            },
            {
              "row": 100,
              "text": "Итого работа: 529936.4"
            },
            {
              "row": 101,
              "text": "Итого материалы: 628855.6559680001"
            },
            {
              "row": 102,
              "text": "Итого кровля: 1158792.055968"
            },
            {
              "row": 119,
              "text": "Итого работа: 177210"
            },
            {
              "row": 120,
              "text": "Итого материалы: 713674"
            },
            {
              "row": 121,
              "text": "Итого окна, двери: 890884"
            },
            {
              "row": 156,
              "text": "Итого работа: 391133.64"
            },
            {
              "row": 157,
              "text": "Итого материалы: 438006.42710880004"
            },
            {
              "row": 158,
              "text": "Итого внешняя отделка: 829140.0671088"
            },
            {
              "row": 228,
              "text": "Итого работа: 966280.5451999999"
            },
            {
              "row": 229,
              "text": "Итого материалы: 1080968.6829375"
            },
            {
              "row": 230,
              "text": "Итого внутренняя отделка: 2047249.2281375001"
            },
            {
              "row": 262,
              "text": "Итого работа: 230232"
            },
            {
              "row": 263,
              "text": "Итого материалы: 346375"
            },
            {
              "row": 264,
              "text": "Итого инженерные коммуникации: 576607"
            },
            {
              "row": 266,
              "text": "Итого РАБОТЫ: 2728719.33504"
            },
            {
              "row": 267,
              "text": "Итого МАТЕРИАЛЫ: 3484775.5569231003"
            },
            {
              "row": 268,
              "text": "ИТОГО СМЕТНАЯ СТОИМОСТЬ: 6790101.8919631"
            }
          ],
          "material_rows": 130,
          "work_rows": 96,
          "logistics_rows": 17,
          "sample_rows": [
            {
              "row": 9,
              "name": "Наименование",
              "unit": "Ед. изм.",
              "qty": "Кол-во",
              "work_price": "Работа",
              "material_price": "Материалы"
            },
            {
              "row": 12,
              "name": "Вынос осей в натуру",
              "unit": "м2",
              "qty": "112",
              "work_price": "100",
              "material_price": "0"
            },
            {
              "row": 14,
              "name": "Укладка канализационной трубы в грунт",
              "unit": "мп",
              "qty": "28",
              "work_price": "800",
              "material_price": "0"
            },
            {
              "row": 15,
              "name": "Труба канализационная Ostendorf d110x2000 мм для наружной канализации",
              "unit": "шт",
              "qty": "14",
              "work_price": "0",
              "material_price": "670"
            },
            {
              "row": 16,
              "name": "Труба канализационная Ostendorf d110x1000 мм для наружной канализации",
              "unit": "шт",
              "qty": "3",
              "work_price": "0",
              "material_price": "400"
            },
            {
              "row": 17,
              "name": "Теплоизоляция для труб стенофлекс 114х13х2000 мм",
              "unit": "мп",
              "qty": "31",
              "work_price": "0",
              "material_price": "118"
            },
            {
              "row": 18,
              "name": "Комплект тройников, отводов, уголков для наружной канализации.",
              "unit": "к-т",
              "qty": "1",
              "work_price": "0",
              "material_price": "3500"
            },
            {
              "row": 19,
              "name": "Укладка закладной трубы в грунт под электрокабель",
              "unit": "мп",
              "qty": "15",
              "work_price": "400",
              "material_price": "0"
            },
            {
              "row": 20,
              "name": "Кабель NVO ВБШвнг(А) LS 5х2.5 20 м",
              "unit": "шт",
              "qty": "1",
              "work_price": "0",
              "material_price": "6600"
            },
            {
              "row": 21,
              "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
              "unit": "мп",
              "qty": "15",
              "work_price": "0",
              "material_price": "114"
            },
            {
              "row": 22,
              "name": "Укладка трубы ХВС в грунт на глубину 1,5м.",
              "unit": "мп",
              "qty": "10",
              "work_price": "1000",
              "material_price": "0"
            },
            {
              "row": 23,
              "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
              "unit": "мп",
              "qty": "20",
              "work_price": "0",
              "material_price": "114"
            },
            {
              "row": 24,
              "name": "Труба ПНД (ПЭ-100) для систем водоснабжения премиум синяя 32 мм",
              "unit": "мп",
              "qty": "20",
              "work_price": "0",
              "material_price": "81"
            },
            {
              "row": 26,
              "name": "Разметка свайного поля, забивка свай, установка оголовков",
              "unit": "шт",
              "qty": "28",
              "work_price": "2000",
              "material_price": "0"
            },
            {
              "row": 27,
              "name": "Свая винтовая d108 мм h2500 мм",
              "unit": "шт",
              "qty": "28",
              "work_price": "0",
              "material_price": "2632"
            },
            {
              "row": 28,
              "name": "Оголовок для сваи винтовой d108 мм",
              "unit": "шт",
              "qty": "28",
              "work_price": "0",
              "material_price": "260"
            },
            {
              "row": 29,
              "name": "Обвязка свай по гидроизоляции",
              "unit": "мп",
              "qty": "80.9",
              "work_price": "750",
              "material_price": "0"
            },
            {
              "row": 30,
              "name": "Гидроизоляция Линокром ХПП Технониколь черный 15 кв.м",
              "unit": "рул",
              "qty": "1",
              "work_price": "0",
              "material_price": "1900"
            },
            {
              "row": 31,
              "name": "Брус сух 150х150",
              "unit": "м3",
              "qty": "2.1843",
              "work_price": "0",
              "material_price": "22000"
            },
            {
              "row": 32,
              "name": "Крепеж и расходные материалы по разделу",
              "unit": "к-т",
              "qty": "28",
              "work_price": "0",
              "material_price": "200"
            },
            {
              "row": 33,
              "name": "Антисептирование конструкционной доски в 2 слоя",
              "unit": "м2",
              "qty": "2.1843",
              "work_price": "200",
              "material_price": "0"
            },
            {
              "row": 34,
              "name": "Антисептик Neomid 450 огнебиозащитный I группа красный 10 кг",
              "unit": "шт",
              "qty": "1",
              "work_price": "0",
              "material_price": "2800"
            },
            {
              "row": 35,
              "name": "Погрузо-разгрузочные работы",
              "unit": "усл",
              "qty": "1",
              "work_price": "6000",
              "material_price": "0"
            },
            {
              "row": 36,
              "name": "Транспортные расходы",
              "unit": "",
              "qty": "0.1",
              "work_price": "",
              "material_price": ""
            },
            {
              "row": 37,
              "name": "Накладные расходы",
              "unit": "",
              "qty": "0.08",
              "work_price": "",
              "material_price": ""
            },
            {
              "row": 41,
              "name": "Наименование",
              "unit": "Ед. изм.",
              "qty": "Кол-во",
              "work_price": "Работа",
              "material_price": "Материалы"
            },
            {
              "row": 44,
              "name": "Монтаж лаг цокольного перекрытия вкл террасы, крыльца",
              "unit": "м2",
              "qty": "109",
              "work_price": "1000",
              "material_price": "0"
            },
            {
              "row": 45,
              "name": "доска с/к 40х200",
              "unit": "м3",
              "qty": "2.616",
              "work_price": "0",
              "material_price": "24300"
            },
            {
              "row": 46,
              "name": "Устройство каркаса стен/перегородок",
              "unit": "м2",
              "qty": "180.135",
              "work_price": "1000",
              "material_price": "0"
            },
            {
              "row": 47,
              "name": "Монтаж стоек и балок террасы",
              "unit": "мп",
              "qty": "9",
              "work_price": "800",
              "material_price": "0"
            },
            {
              "row": 48,
              "name": "доска с/к 40х150",
              "unit": "м3",
              "qty": "5.0454",
              "work_price": "0",
              "material_price": "24300"
            },
            {
              "row": 49,
              "name": "доска с/к 40х100",
              "unit": "м3",
              "qty": "0.768",
              "work_price": "0",
              "material_price": "24300"
            },
            {
              "row": 50,
              "name": "бру с/с 150х150",
              "unit": "м3",
              "qty": "0.26999999999999996",
              "work_price": "0",
              "material_price": "30000"
            },
            {
              "row": 51,
              "name": "Монтаж баллок перекрытия",
              "unit": "м2",
              "qty": "0",
              "work_price": "1000",
              "material_price": "0"
            },
            {
              "row": 52,
              "name": "доска с/к 40х150",
              "unit": "м3",
              "qty": "0",
              "work_price": "0",
              "material_price": "24300"
            }
          ],
          "formula_count": 791,
          "formula_samples": [
            {
              "sheet": "Каркас под ключ",
              "cell": "E1",
              "formula": "=E2+E3+E4+E5+E6+E7+E8"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E2",
              "formula": "=I40"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E3",
              "formula": "=I63"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E4",
              "formula": "=I102"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E5",
              "formula": "=I121"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E6",
              "formula": "=I158"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E7",
              "formula": "=I230"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "E8",
              "formula": "=I264"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F12",
              "formula": "=E12*D12"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H12",
              "formula": "=D12*G12"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I12",
              "formula": "=F12+H12"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F13",
              "formula": "=E13*D13"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F14",
              "formula": "=E14*D14"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H14",
              "formula": "=D14*G14"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I14",
              "formula": "=F14+H14"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "D15",
              "formula": "=D14/2"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F15",
              "formula": "=E15*D15"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H15",
              "formula": "=D15*G15"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I15",
              "formula": "=F15+H15"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F16",
              "formula": "=E16*D16"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H16",
              "formula": "=D16*G16"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I16",
              "formula": "=F16+H16"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "D17",
              "formula": "=D14+D16"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F17",
              "formula": "=E17*D17"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H17",
              "formula": "=D17*G17"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I17",
              "formula": "=F17+H17"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F18",
              "formula": "=E18*D18"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "H18",
              "formula": "=D18*G18"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "I18",
              "formula": "=F18+H18"
            },
            {
              "sheet": "Каркас под ключ",
              "cell": "F19",
              "formula": "=E19*D19"
            }
          ],
          "row_count": 285
        },
        {
          "sheet_name": "Газобетон",
          "scenario": "gasbeton_or_masonry_with_monolithic_foundation",
          "sections": [
            "Фундамент",
            "Стены",
            "Кровля",
            "Окна, двери",
            "Внешняя отделка",
            "Внутренняя отделка",
            "Инженерные коммуникации"
          ],
          "header_rows": [
            9,
            59,
            111,
            155,
            174,
            204,
            256
          ],
          "total_rows": [
            {
              "row": 56,
              "text": "Итого работа: 423924.316"
            },
            {
              "row": 57,
              "text": "Итого материалы: 633049.0299328001"
            },
            {
              "row": 58,
              "text": "Итого фундамент: 1056973.3459328"
            },
            {
              "row": 108,
              "text": "Итого работа: 556830.175"
            },
            {
              "row": 109,
              "text": "Итого материалы: 742975.012384"
            },
            {
              "row": 110,
              "text": "Итого стены : 1299805.187384"
            },
            {
              "row": 152,
              "text": "Итого работа: 529936.4"
            },
            {
              "row": 153,
              "text": "Итого материалы: 628855.6559680001"
            },
            {
              "row": 154,
              "text": "Итого кровля: 1158792.055968"
            },
            {
              "row": 171,
              "text": "Итого работа: 182710"
            },
            {
              "row": 172,
              "text": "Итого материалы: 743834"
            },
            {
              "row": 173,
              "text": "Итого окна, двери: 926544"
            },
            {
              "row": 201,
              "text": "Итого работа: 305167.64"
            },
            {
              "row": 202,
              "text": "Итого материалы: 318469.1861888"
            },
            {
              "row": 203,
              "text": "Итого внешняя отделка: 623636.8261888"
            },
            {
              "row": 253,
              "text": "Итого работа: 683979.2252"
            },
            {
              "row": 254,
              "text": "Итого материалы: 697688.6923125"
            },
            {
              "row": 255,
              "text": "Итого внутренняя отделка: 1381667.9175125"
            },
            {
              "row": 287,
              "text": "Итого работа: 230232"
            },
            {
              "row": 288,
              "text": "Итого материалы: 346375"
            },
            {
              "row": 289,
              "text": "Итого инженерные коммуникации: 576607"
            },
            {
              "row": 291,
              "text": "Итого РАБОТЫ: 2912779.7562"
            },
            {
              "row": 292,
              "text": "Итого МАТЕРИАЛЫ: 4111246.5767861004"
            },
            {
              "row": 293,
              "text": "ИТОГО СМЕТНАЯ СТОИМОСТЬ: 7024026.332986101"
            }
          ],
          "material_rows": 154,
          "work_rows": 99,
          "logistics_rows": 23,
          "sample_rows": [
            {
              "row": 9,
              "name": "Наименование",
              "unit": "Ед. изм.",
              "qty": "Кол-во",
              "work_price": "Работа",
              "material_price": "Материалы"
            },
            {
              "row": 12,
              "name": "Вынос осей в натуру",
              "unit": "м2",
              "qty": "112",
              "work_price": "80",
              "material_price": "0"
            },
            {
              "row": 13,
              "name": "Земляные работы, сопровождение работы экскаватора",
              "unit": "см",
              "qty": "1",
              "work_price": "12000",
              "material_price": "0"
            },
            {
              "row": 14,
              "name": "Аренда экскаватора",
              "unit": "см",
              "qty": "1",
              "work_price": "0",
              "material_price": "22000"
            },
            {
              "row": 15,
              "name": "Доработка грунта вручную",
              "unit": "м2",
              "qty": "155",
              "work_price": "150",
              "material_price": "0"
            },
            {
              "row": 16,
              "name": "Настил геотекстиля по основанию и стенам котлована (Геотекстиль 300 г/кв.м иглопробивной)",
              "unit": "м2",
              "qty": "205",
              "work_price": "80",
              "material_price": "60"
            },
            {
              "row": 17,
              "name": "Устройство песчаной подготовки т 200 мм с уплотнением.",
              "unit": "м3",
              "qty": "44",
              "work_price": "800",
              "material_price": "0"
            },
            {
              "row": 18,
              "name": "Аренда виброплиты (трамбовка)",
              "unit": "сут",
              "qty": "4",
              "work_price": "0",
              "material_price": "2500"
            },
            {
              "row": 19,
              "name": "Песок карьерный",
              "unit": "м3",
              "qty": "44",
              "work_price": "0",
              "material_price": "900"
            },
            {
              "row": 20,
              "name": "Устройство щебеночной подготовки т 100 мм с уплотнением.",
              "unit": "м3",
              "qty": "19",
              "work_price": "800",
              "material_price": "0"
            },
            {
              "row": 21,
              "name": "Аренда виброплиты (трамбовка)",
              "unit": "сут",
              "qty": "4",
              "work_price": "0",
              "material_price": "2500"
            },
            {
              "row": 22,
              "name": "Щебень фр 20-40",
              "unit": "м3",
              "qty": "19",
              "work_price": "0",
              "material_price": "1880"
            },
            {
              "row": 24,
              "name": "Укладка канализационной трубы в грунт",
              "unit": "мп",
              "qty": "28",
              "work_price": "900",
              "material_price": "0"
            },
            {
              "row": 25,
              "name": "Труба канализационная Ostendorf d110x2000 мм для наружной канализации",
              "unit": "шт",
              "qty": "10",
              "work_price": "0",
              "material_price": "670"
            },
            {
              "row": 26,
              "name": "Труба канализационная Ostendorf d110x1000 мм для наружной канализации",
              "unit": "шт",
              "qty": "3",
              "work_price": "0",
              "material_price": "400"
            },
            {
              "row": 27,
              "name": "Теплоизоляция для труб стенофлекс 114х13х2000 мм",
              "unit": "мп",
              "qty": "31",
              "work_price": "0",
              "material_price": "118"
            },
            {
              "row": 28,
              "name": "Комплект тройников, отводов, уголков для наружной канализации.",
              "unit": "к-т",
              "qty": "1",
              "work_price": "0",
              "material_price": "3500"
            },
            {
              "row": 29,
              "name": "Укладка закладной трубы в грунт под электрокабель",
              "unit": "мп",
              "qty": "15",
              "work_price": "400",
              "material_price": "0"
            },
            {
              "row": 30,
              "name": "Кабель NVO ВБШвнг(А) LS 5х2.5 20 м",
              "unit": "шт",
              "qty": "1",
              "work_price": "0",
              "material_price": "6600"
            },
            {
              "row": 31,
              "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
              "unit": "мп",
              "qty": "15",
              "work_price": "0",
              "material_price": "114"
            },
            {
              "row": 32,
              "name": "Укладка трубы ХВС в грунт на глубину 1,5м.",
              "unit": "мп",
              "qty": "10",
              "work_price": "850",
              "material_price": "0"
            },
            {
              "row": 33,
              "name": "Труба двустенная гофрированная ПНД/ПВД d63/52",
              "unit": "мп",
              "qty": "20",
              "work_price": "0",
              "material_price": "114"
            },
            {
              "row": 34,
              "name": "Труба ПНД (ПЭ-100) для систем водоснабжения премиум синяя 32 мм",
              "unit": "мп",
              "qty": "20",
              "work_price": "0",
              "material_price": "81"
            },
            {
              "row": 35,
              "name": "Настил технической пленки",
              "unit": "м2",
              "qty": "140",
              "work_price": "50",
              "material_price": "40"
            },
            {
              "row": 37,
              "name": "Устройство опалубки",
              "unit": "мп",
              "qty": "42.58",
              "work_price": "1100",
              "material_price": "0"
            },
            {
              "row": 38,
              "name": "Доска 50х150(100)х6000 мм е/в",
              "unit": "м3",
              "qty": "1.9160999999999997",
              "work_price": "0",
              "material_price": "17500"
            },
            {
              "row": 39,
              "name": "Устройство арматурного каркаса",
              "unit": "м2",
              "qty": "112",
              "work_price": "1200",
              "material_price": "0"
            },
            {
              "row": 40,
              "name": "Арматура металлическая д.12 А500",
              "unit": "т",
              "qty": "2.386944",
              "work_price": "0",
              "material_price": "70000"
            },
            {
              "row": 41,
              "name": "Арматура металлическая д.8 А500",
              "unit": "т",
              "qty": "0.26256384000000005",
              "work_price": "0",
              "material_price": "73000"
            },
            {
              "row": 42,
              "name": "Пеноплэкс Фундамент 100х585х1185",
              "unit": "шт",
              "qty": "3",
              "work_price": "0",
              "material_price": "709"
            },
            {
              "row": 43,
              "name": "Проволока вязальная 1,2мм",
              "unit": "кг",
              "qty": "59",
              "work_price": "0",
              "material_price": "160"
            },
            {
              "row": 44,
              "name": "Фиксаторы арматуры гориз.уп 250 шт",
              "unit": "уп",
              "qty": "3",
              "work_price": "0",
              "material_price": "1456"
            },
            {
              "row": 45,
              "name": "Бетонирование монолитной плиты с вибрированием",
              "unit": "м3",
              "qty": "25",
              "work_price": "2000",
              "material_price": "0"
            },
            {
              "row": 46,
              "name": "Бетон В20 W8 с доставкой*",
              "unit": "м3",
              "qty": "25",
              "work_price": "0",
              "material_price": "6500"
            },
            {
              "row": 47,
              "name": "глубинный вибратор",
              "unit": "сут",
              "qty": "1",
              "work_price": "0",
              "material_price": "1500"
            }
          ],
          "formula_count": 856,
          "formula_samples": [
            {
              "sheet": "Газобетон",
              "cell": "E1",
              "formula": "=E2+E3+E4+E5+E6+E7+E8"
            },
            {
              "sheet": "Газобетон",
              "cell": "E2",
              "formula": "=I58"
            },
            {
              "sheet": "Газобетон",
              "cell": "E3",
              "formula": "=I110"
            },
            {
              "sheet": "Газобетон",
              "cell": "E4",
              "formula": "=I154"
            },
            {
              "sheet": "Газобетон",
              "cell": "E5",
              "formula": "=I173"
            },
            {
              "sheet": "Газобетон",
              "cell": "E6",
              "formula": "=I203"
            },
            {
              "sheet": "Газобетон",
              "cell": "E7",
              "formula": "=I255"
            },
            {
              "sheet": "Газобетон",
              "cell": "E8",
              "formula": "=I289"
            },
            {
              "sheet": "Газобетон",
              "cell": "F12",
              "formula": "=E12*D12"
            },
            {
              "sheet": "Газобетон",
              "cell": "H12",
              "formula": "=D12*G12"
            },
            {
              "sheet": "Газобетон",
              "cell": "I12",
              "formula": "=F12+H12"
            },
            {
              "sheet": "Газобетон",
              "cell": "F13",
              "formula": "=E13*D13"
            },
            {
              "sheet": "Газобетон",
              "cell": "H13",
              "formula": "=D13*G13"
            },
            {
              "sheet": "Газобетон",
              "cell": "I13",
              "formula": "=F13+H13"
            },
            {
              "sheet": "Газобетон",
              "cell": "D14",
              "formula": "=D13"
            },
            {
              "sheet": "Газобетон",
              "cell": "F14",
              "formula": "=E14*D14"
            },
            {
              "sheet": "Газобетон",
              "cell": "H14",
              "formula": "=D14*G14"
            },
            {
              "sheet": "Газобетон",
              "cell": "I14",
              "formula": "=F14+H14"
            },
            {
              "sheet": "Газобетон",
              "cell": "F15",
              "formula": "=E15*D15"
            },
            {
              "sheet": "Газобетон",
              "cell": "H15",
              "formula": "=D15*G15"
            },
            {
              "sheet": "Газобетон",
              "cell": "I15",
              "formula": "=F15+H15"
            },
            {
              "sheet": "Газобетон",
              "cell": "D16",
              "formula": "=155+50"
            },
            {
              "sheet": "Газобетон",
              "cell": "F16",
              "formula": "=E16*D16"
            },
            {
              "sheet": "Газобетон",
              "cell": "H16",
              "formula": "=D16*G16"
            },
            {
              "sheet": "Газобетон",
              "cell": "I16",
              "formula": "=F16+H16"
            },
            {
              "sheet": "Газобетон",
              "cell": "D17",
              "formula": "=ROUNDUP(D15*0.2*1.4,)"
            },
            {
              "sheet": "Газобетон",
              "cell": "F17",
              "formula": "=E17*D17"
            },
            {
              "sheet": "Газобетон",
              "cell": "H17",
              "formula": "=D17*G17"
            },
            {
              "sheet": "Газобетон",
              "cell": "I17",
              "formula": "=F17+H17"
            },
            {
              "sheet": "Газобетон",
              "cell": "F18",
              "formula": "=E18*D18"
            }
          ],
          "row_count": 310
        }
      ]
    },
    {
      "key": "ROOF_FLOORS",
      "title": "крыша и перекр.xlsx",
      "template_role": "roof_and_floor_estimate_template",
      "description": "Эталон расчёта кровли и перекрытий",
      "file_id": "16YecwnJ9umnVprFu9V77UCV6cPrYbNh3",
      "drive_url": "https://docs.google.com/spreadsheets/d/16YecwnJ9umnVprFu9V77UCV6cPrYbNh3/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
      "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "modifiedTime": "2025-03-14T11:17:00.000Z",
      "parents": [
        "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
      ],
      "formula_total": 136,
      "formula_samples": [
        {
          "sheet": "расчет кровли",
          "cell": "F5",
          "formula": "=E5*D5"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H5",
          "formula": "=G5*D5"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I5",
          "formula": "=F5+H5"
        },
        {
          "sheet": "расчет кровли",
          "cell": "D6",
          "formula": "=11.27+0.19+0.052+0.011+0.031"
        },
        {
          "sheet": "расчет кровли",
          "cell": "F6",
          "formula": "=E6*D6"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H6",
          "formula": "=G6*D6"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I6",
          "formula": "=F6+H6"
        },
        {
          "sheet": "расчет кровли",
          "cell": "F7",
          "formula": "=E7*D7"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H7",
          "formula": "=G7*D7"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I7",
          "formula": "=F7+H7"
        },
        {
          "sheet": "расчет кровли",
          "cell": "D8",
          "formula": "=D5"
        },
        {
          "sheet": "расчет кровли",
          "cell": "F8",
          "formula": "=E8*D8"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H8",
          "formula": "=G8*D8"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I8",
          "formula": "=F8+H8"
        },
        {
          "sheet": "расчет кровли",
          "cell": "D9",
          "formula": "=D5"
        },
        {
          "sheet": "расчет кровли",
          "cell": "F9",
          "formula": "=E9*D9"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H9",
          "formula": "=G9*D9"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I9",
          "formula": "=F9+H9"
        },
        {
          "sheet": "расчет кровли",
          "cell": "D10",
          "formula": "=D5"
        },
        {
          "sheet": "расчет кровли",
          "cell": "F10",
          "formula": "=E10*D10"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H10",
          "formula": "=G10*D10"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I10",
          "formula": "=F10+H10"
        },
        {
          "sheet": "расчет кровли",
          "cell": "D11",
          "formula": "=D5"
        },
        {
          "sheet": "расчет кровли",
          "cell": "F11",
          "formula": "=E11*D11"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H11",
          "formula": "=G11*D11"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I11",
          "formula": "=F11+H11"
        },
        {
          "sheet": "расчет кровли",
          "cell": "F13",
          "formula": "=E13*D13"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H13",
          "formula": "=D13*G13"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I13",
          "formula": "=F13+H13"
        },
        {
          "sheet": "расчет кровли",
          "cell": "F14",
          "formula": "=E14*D14"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H14",
          "formula": "=D14*G14"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I14",
          "formula": "=F14+H14"
        },
        {
          "sheet": "расчет кровли",
          "cell": "F15",
          "formula": "=E15*D15"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H15",
          "formula": "=D15*G15"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I15",
          "formula": "=F15+H15"
        },
        {
          "sheet": "расчет кровли",
          "cell": "F16",
          "formula": "=D16*E16"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H16",
          "formula": "=D16*G16"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I16",
          "formula": "=F16+H16"
        },
        {
          "sheet": "расчет кровли",
          "cell": "L16",
          "formula": "=4.3+1.92+0.48+0.012"
        },
        {
          "sheet": "расчет кровли",
          "cell": "N16",
          "formula": "=L16/0.05*2"
        },
        {
          "sheet": "расчет кровли",
          "cell": "O16",
          "formula": "=L16/0.2*2"
        },
        {
          "sheet": "расчет кровли",
          "cell": "P16",
          "formula": "=O16+N16"
        },
        {
          "sheet": "расчет кровли",
          "cell": "D17",
          "formula": "=D16"
        },
        {
          "sheet": "расчет кровли",
          "cell": "F17",
          "formula": "=D17*E17"
        },
        {
          "sheet": "расчет кровли",
          "cell": "H17",
          "formula": "=D17*G17"
        },
        {
          "sheet": "расчет кровли",
          "cell": "I17",
          "formula": "=F17+H17"
        },
        {
          "sheet": "расчет кровли",
          "cell": "L17",
          "formula": "=0.027+0.023+0.034+0.01+0.014+0.021+0.017+0.016+0.032+0.087+0.054+0.034+0.047+0.16+0.032+0.032+0.016+0.02+1.76+0.41+0.041"
        },
        {
          "sheet": "расчет кровли",
          "cell": "N17",
          "formula": "=L17/0.05*2"
        },
        {
          "sheet": "расчет кровли",
          "cell": "O17",
          "formula": "=L17/0.2*2"
        },
        {
          "sheet": "расчет кровли",
          "cell": "P17",
          "formula": "=O17+N17"
        }
      ],
      "sheets": [
        {
          "sheet_name": "расчет кровли",
          "scenario": "roof_and_floors",
          "sections": [
            "Кровля"
          ],
          "header_rows": [
            1
          ],
          "total_rows": [
            {
              "row": 30,
              "text": "Итого работа: 2236634.6100000003"
            },
            {
              "row": 31,
              "text": "Итого материалы: 0"
            },
            {
              "row": 32,
              "text": "Итого кровля: 2236634.6100000003"
            }
          ],
          "material_rows": 1,
          "work_rows": 24,
          "logistics_rows": 1,
          "sample_rows": [
            {
              "row": 1,
              "name": "Наименование",
              "unit": "Ед. изм.",
              "qty": "Кол-во",
              "work_price": "Работа",
              "material_price": "Материалы"
            },
            {
              "row": 5,
              "name": "Устройство чердачного перекрытия",
              "unit": "м2",
              "qty": "191",
              "work_price": "1000",
              "material_price": "0"
            },
            {
              "row": 6,
              "name": "Антисептирование пиломатериалов с 4х сторон",
              "unit": "м3",
              "qty": "11.553999999999998",
              "work_price": "2800",
              "material_price": "0"
            },
            {
              "row": 7,
              "name": "Монтаж пароизоляции с проклейкой швов",
              "unit": "м2",
              "qty": "170",
              "work_price": "220",
              "material_price": "0"
            },
            {
              "row": 8,
              "name": "Монтаж обрешетки под утеплитель шаг 200",
              "unit": "м2",
              "qty": "191",
              "work_price": "380",
              "material_price": "0"
            },
            {
              "row": 9,
              "name": "Монтаж утепления 200 мм",
              "unit": "м2",
              "qty": "191",
              "work_price": "600",
              "material_price": "0"
            },
            {
              "row": 10,
              "name": "Монтаж гидро-ветрозащиты",
              "unit": "м2",
              "qty": "191",
              "work_price": "220",
              "material_price": "0"
            },
            {
              "row": 11,
              "name": "Монтаж разряженой обрешетки шаг 400",
              "unit": "м2",
              "qty": "191",
              "work_price": "360",
              "material_price": "0"
            },
            {
              "row": 13,
              "name": "Укладка мауэрлата по гидроизоляции",
              "unit": "мп",
              "qty": "78",
              "work_price": "850",
              "material_price": "0"
            },
            {
              "row": 14,
              "name": "Монтаж стропильной системы",
              "unit": "м2",
              "qty": "280",
              "work_price": "1400",
              "material_price": "0"
            },
            {
              "row": 15,
              "name": "Монтаж опорных стоек, каркасов стропильной системы",
              "unit": "к-т",
              "qty": "1",
              "work_price": "20000",
              "material_price": "0"
            },
            {
              "row": 16,
              "name": "Монтаж кровельной мембраны",
              "unit": "м2",
              "qty": "280",
              "work_price": "250",
              "material_price": "0"
            },
            {
              "row": 17,
              "name": "Монтаж контробрешетки",
              "unit": "м2",
              "qty": "280",
              "work_price": "360",
              "material_price": "0"
            },
            {
              "row": 18,
              "name": "Монтаж обрешётки шаг 350 мм",
              "unit": "м2",
              "qty": "280",
              "work_price": "360",
              "material_price": "0"
            },
            {
              "row": 19,
              "name": "Монтаж Металлочерепицы",
              "unit": "м2",
              "qty": "280",
              "work_price": "850",
              "material_price": "0"
            },
            {
              "row": 20,
              "name": "Монтаж доборных элементов",
              "unit": "мп",
              "qty": "231",
              "work_price": "550",
              "material_price": "0"
            },
            {
              "row": 21,
              "name": "Монтаж крюка длинного",
              "unit": "шт",
              "qty": "110",
              "work_price": "300",
              "material_price": "0"
            },
            {
              "row": 22,
              "name": "Монтаж вентвыходов на кровле",
              "unit": "к-т",
              "qty": "6",
              "work_price": "8500",
              "material_price": "0"
            },
            {
              "row": 23,
              "name": "Отделка лобовой доски (доской крашеной в заводских условиях)",
              "unit": "мп",
              "qty": "78",
              "work_price": "800",
              "material_price": "0"
            },
            {
              "row": 24,
              "name": "Подшивка потолка крыльца, террасы, свесов (доской крашеной в заводских условиях)",
              "unit": "м2",
              "qty": "118",
              "work_price": "1200",
              "material_price": "0"
            },
            {
              "row": 25,
              "name": "Монтаж водосточной системы",
              "unit": "мп",
              "qty": "104.63",
              "work_price": "900",
              "material_price": "0"
            },
            {
              "row": 26,
              "name": "Монтаж снегозадержания",
              "unit": "мп",
              "qty": "6",
              "work_price": "1200",
              "material_price": "0"
            },
            {
              "row": 27,
              "name": "Антисептирование пиломатериалов",
              "unit": "м3",
              "qty": "15.7",
              "work_price": "3000",
              "material_price": "0"
            },
            {
              "row": 28,
              "name": "Погрузо-разгрузочные работы",
              "unit": "усл",
              "qty": "2",
              "work_price": "10000",
              "material_price": "0"
            },
            {
              "row": 29,
              "name": "Накладные расходы",
              "unit": "",
              "qty": "0.05",
              "work_price": "",
              "material_price": ""
            }
          ],
          "formula_count": 136,
          "formula_samples": [
            {
              "sheet": "расчет кровли",
              "cell": "F5",
              "formula": "=E5*D5"
            },
            {
              "sheet": "расчет кровли",
              "cell": "H5",
              "formula": "=G5*D5"
            },
            {
              "sheet": "расчет кровли",
              "cell": "I5",
              "formula": "=F5+H5"
            },
            {
              "sheet": "расчет кровли",
              "cell": "D6",
              "formula": "=11.27+0.19+0.052+0.011+0.031"
            },
            {
              "sheet": "расчет кровли",
              "cell": "F6",
              "formula": "=E6*D6"
            },
            {
              "sheet": "расчет кровли",
              "cell": "H6",
              "formula": "=G6*D6"
            },
            {
              "sheet": "расчет кровли",
              "cell": "I6",
              "formula": "=F6+H6"
            },
            {
              "sheet": "расчет кровли",
              "cell": "F7",
              "formula": "=E7*D7"
            },
            {
              "sheet": "расчет кровли",
              "cell": "H7",
              "formula": "=G7*D7"
            },
            {
              "sheet": "расчет кровли",
              "cell": "I7",
              "formula": "=F7+H7"
            },
            {
              "sheet": "расчет кровли",
              "cell": "D8",
              "formula": "=D5"
            },
            {
              "sheet": "расчет кровли",
              "cell": "F8",
              "formula": "=E8*D8"
            },
            {
              "sheet": "расчет кровли",
              "cell": "H8",
              "formula": "=G8*D8"
            },
            {
              "sheet": "расчет кровли",
              "cell": "I8",
              "formula": "=F8+H8"
            },
            {
              "sheet": "расчет кровли",
              "cell": "D9",
              "formula": "=D5"
            },
            {
              "sheet": "расчет кровли",
              "cell": "F9",
              "formula": "=E9*D9"
            },
            {
              "sheet": "расчет кровли",
              "cell": "H9",
              "formula": "=G9*D9"
            },
            {
              "sheet": "расчет кровли",
              "cell": "I9",
              "formula": "=F9+H9"
            },
            {
              "sheet": "расчет кровли",
              "cell": "D10",
              "formula": "=D5"
            },
            {
              "sheet": "расчет кровли",
              "cell": "F10",
              "formula": "=E10*D10"
            },
            {
              "sheet": "расчет кровли",
              "cell": "H10",
              "formula": "=G10*D10"
            },
            {
              "sheet": "расчет кровли",
              "cell": "I10",
              "formula": "=F10+H10"
            },
            {
              "sheet": "расчет кровли",
              "cell": "D11",
              "formula": "=D5"
            },
            {
              "sheet": "расчет кровли",
              "cell": "F11",
              "formula": "=E11*D11"
            },
            {
              "sheet": "расчет кровли",
              "cell": "H11",
              "formula": "=G11*D11"
            },
            {
              "sheet": "расчет кровли",
              "cell": "I11",
              "formula": "=F11+H11"
            },
            {
              "sheet": "расчет кровли",
              "cell": "F13",
              "formula": "=E13*D13"
            },
            {
              "sheet": "расчет кровли",
              "cell": "H13",
              "formula": "=D13*G13"
            },
            {
              "sheet": "расчет кровли",
              "cell": "I13",
              "formula": "=F13+H13"
            },
            {
              "sheet": "расчет кровли",
              "cell": "F14",
              "formula": "=E14*D14"
            }
          ],
          "row_count": 747
        }
      ]
    },
    {
      "key": "FOUNDATION_WAREHOUSE",
      "title": "фундамент_Склад2.xlsx",
      "template_role": "foundation_estimate_template",
      "description": "Эталон расчёта фундамента",
      "file_id": "1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp",
      "drive_url": "https://docs.google.com/spreadsheets/d/1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
      "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "modifiedTime": "2025-05-27T08:01:58.000Z",
      "parents": [
        "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
      ],
      "formula_total": 88,
      "formula_samples": [
        {
          "sheet": "смета",
          "cell": "F4",
          "formula": "=E4*D4"
        },
        {
          "sheet": "смета",
          "cell": "F5",
          "formula": "=E5*D5"
        },
        {
          "sheet": "смета",
          "cell": "H5",
          "formula": "=D5*G5"
        },
        {
          "sheet": "смета",
          "cell": "I5",
          "formula": "=F5+H5"
        },
        {
          "sheet": "смета",
          "cell": "D6",
          "formula": "=ROUNDUP((680*0.62)/200,0)"
        },
        {
          "sheet": "смета",
          "cell": "F6",
          "formula": "=E6*D6"
        },
        {
          "sheet": "смета",
          "cell": "H6",
          "formula": "=D6*G6"
        },
        {
          "sheet": "смета",
          "cell": "I6",
          "formula": "=F6+H6"
        },
        {
          "sheet": "смета",
          "cell": "D7",
          "formula": "=D6"
        },
        {
          "sheet": "смета",
          "cell": "F7",
          "formula": "=E7*D7"
        },
        {
          "sheet": "смета",
          "cell": "H7",
          "formula": "=D7*G7"
        },
        {
          "sheet": "смета",
          "cell": "I7",
          "formula": "=F7+H7"
        },
        {
          "sheet": "смета",
          "cell": "F8",
          "formula": "=E8*D8"
        },
        {
          "sheet": "смета",
          "cell": "H8",
          "formula": "=D8*G8"
        },
        {
          "sheet": "смета",
          "cell": "I8",
          "formula": "=F8+H8"
        },
        {
          "sheet": "смета",
          "cell": "F9",
          "formula": "=E9*D9"
        },
        {
          "sheet": "смета",
          "cell": "H9",
          "formula": "=D9*G9"
        },
        {
          "sheet": "смета",
          "cell": "I9",
          "formula": "=F9+H9"
        },
        {
          "sheet": "смета",
          "cell": "F10",
          "formula": "=E10*D10"
        },
        {
          "sheet": "смета",
          "cell": "H10",
          "formula": "=D10*G10"
        },
        {
          "sheet": "смета",
          "cell": "I10",
          "formula": "=F10+H10"
        },
        {
          "sheet": "смета",
          "cell": "D11",
          "formula": "=114+493"
        },
        {
          "sheet": "смета",
          "cell": "F11",
          "formula": "=E11*D11"
        },
        {
          "sheet": "смета",
          "cell": "H11",
          "formula": "=G11*D11"
        },
        {
          "sheet": "смета",
          "cell": "I11",
          "formula": "=F11+H11"
        },
        {
          "sheet": "смета",
          "cell": "F12",
          "formula": "=E12*D12"
        },
        {
          "sheet": "смета",
          "cell": "H12",
          "formula": "=G12*D12"
        },
        {
          "sheet": "смета",
          "cell": "I12",
          "formula": "=F12+H12"
        },
        {
          "sheet": "смета",
          "cell": "F13",
          "formula": "=E13*D13"
        },
        {
          "sheet": "смета",
          "cell": "H13",
          "formula": "=G13*D13"
        },
        {
          "sheet": "смета",
          "cell": "I13",
          "formula": "=F13+H13"
        },
        {
          "sheet": "смета",
          "cell": "F14",
          "formula": "=E14*D14"
        },
        {
          "sheet": "смета",
          "cell": "H14",
          "formula": "=G14*D14"
        },
        {
          "sheet": "смета",
          "cell": "I14",
          "formula": "=F14+H14"
        },
        {
          "sheet": "смета",
          "cell": "F15",
          "formula": "=E15*D15"
        },
        {
          "sheet": "смета",
          "cell": "H15",
          "formula": "=G15*D15"
        },
        {
          "sheet": "смета",
          "cell": "I15",
          "formula": "=F15+H15"
        },
        {
          "sheet": "смета",
          "cell": "D16",
          "formula": "=ROUNDUP(171.2*1.1,)"
        },
        {
          "sheet": "смета",
          "cell": "F16",
          "formula": "=E16*D16"
        },
        {
          "sheet": "смета",
          "cell": "H16",
          "formula": "=G16*D16"
        },
        {
          "sheet": "смета",
          "cell": "I16",
          "formula": "=F16+H16"
        },
        {
          "sheet": "смета",
          "cell": "F17",
          "formula": "=E17*D17"
        },
        {
          "sheet": "смета",
          "cell": "H17",
          "formula": "=D17*G17"
        },
        {
          "sheet": "смета",
          "cell": "I17",
          "formula": "=F17+H17"
        },
        {
          "sheet": "смета",
          "cell": "F18",
          "formula": "=E18*D18"
        },
        {
          "sheet": "смета",
          "cell": "F19",
          "formula": "=E19*D19"
        },
        {
          "sheet": "смета",
          "cell": "H19",
          "formula": "=G19*D19"
        },
        {
          "sheet": "смета",
          "cell": "I19",
          "formula": "=F19+H19"
        },
        {
          "sheet": "смета",
          "cell": "F20",
          "formula": "=E20*D20"
        },
        {
          "sheet": "смета",
          "cell": "F21",
          "formula": "=E21*D21"
        }
      ],
      "sheets": [
        {
          "sheet_name": "смета",
          "scenario": "foundation",
          "sections": [
            "Фундамент"
          ],
          "header_rows": [
            1
          ],
          "total_rows": [
            {
              "row": 33,
              "text": "Итого работа: 2915677.0762500004"
            },
            {
              "row": 35,
              "text": "Итого материалы: 84240"
            },
            {
              "row": 36,
              "text": "Итого фундамент: 3116917.0762500004"
            }
          ],
          "material_rows": 6,
          "work_rows": 17,
          "logistics_rows": 0,
          "sample_rows": [
            {
              "row": 1,
              "name": "Наименование",
              "unit": "Ед. изм.",
              "qty": "Кол-во",
              "work_price": "Работа",
              "material_price": "Материалы"
            },
            {
              "row": 5,
              "name": "Вынос осей в натуру",
              "unit": "см",
              "qty": "1",
              "work_price": "18000",
              "material_price": "0"
            },
            {
              "row": 6,
              "name": "Земляные работы, сопровождение работы экскаватора",
              "unit": "см",
              "qty": "3",
              "work_price": "10000",
              "material_price": "0"
            },
            {
              "row": 7,
              "name": "Аренда экскаватора",
              "unit": "см",
              "qty": "3",
              "work_price": "0",
              "material_price": "24000"
            },
            {
              "row": 8,
              "name": "Доработка грунта вручную",
              "unit": "м2",
              "qty": "680",
              "work_price": "50",
              "material_price": "0"
            },
            {
              "row": 10,
              "name": "Настил геотекстиля",
              "unit": "м2",
              "qty": "608",
              "work_price": "80",
              "material_price": "0"
            },
            {
              "row": 11,
              "name": "Отсыпка основания щебнем и песком с формированием откосов под ребра жесткости",
              "unit": "м3",
              "qty": "607",
              "work_price": "850",
              "material_price": "0"
            },
            {
              "row": 12,
              "name": "Настил п/э пленки",
              "unit": "м2",
              "qty": "606",
              "work_price": "80",
              "material_price": "0"
            },
            {
              "row": 14,
              "name": "Монтаж опалубки",
              "unit": "мп",
              "qty": "108.46",
              "work_price": "1100",
              "material_price": "0"
            },
            {
              "row": 15,
              "name": "Устройство арматурного каркаса",
              "unit": "м2",
              "qty": "507.23",
              "work_price": "1300",
              "material_price": "0"
            },
            {
              "row": 16,
              "name": "Бетонирование с уплотнением",
              "unit": "м3",
              "qty": "189",
              "work_price": "2000",
              "material_price": "0"
            },
            {
              "row": 17,
              "name": "Аренда бетононасоса",
              "unit": "см",
              "qty": "2",
              "work_price": "0",
              "material_price": "31000"
            },
            {
              "row": 19,
              "name": "Монтаж анкерных групп",
              "unit": "шт",
              "qty": "23",
              "work_price": "6500",
              "material_price": "0"
            },
            {
              "row": 21,
              "name": "Устройство ростверка поверх фундаментной плиты (опалубка, арматура, бетонирование)",
              "unit": "мп",
              "qty": "86.257",
              "work_price": "2800",
              "material_price": "0"
            },
            {
              "row": 22,
              "name": "Аренда бетононасоса",
              "unit": "см",
              "qty": "1",
              "work_price": "0",
              "material_price": "31000"
            },
            {
              "row": 24,
              "name": "Устройство обмазочной гидроизоляции в 2 слоя торца плиты с ребрами жесткости и внешней стороны ростверка",
              "unit": "м2",
              "qty": "121.14304999999999",
              "work_price": "350",
              "material_price": "0"
            },
            {
              "row": 25,
              "name": "Утепление торца плиты с ребрами жесткости и внешней стороны ростверка ЭППс 100 мм",
              "unit": "м2",
              "qty": "121.14304999999999",
              "work_price": "400",
              "material_price": "0"
            },
            {
              "row": 27,
              "name": "Монтаж опалубки",
              "unit": "мп",
              "qty": "30",
              "work_price": "1100",
              "material_price": "0"
            },
            {
              "row": 28,
              "name": "Устройство арматурного каркаса",
              "unit": "м2",
              "qty": "108",
              "work_price": "1200",
              "material_price": "0"
            },
            {
              "row": 29,
              "name": "Бетонирование с уплотнением",
              "unit": "м3",
              "qty": "24",
              "work_price": "2000",
              "material_price": "0"
            },
            {
              "row": 30,
              "name": "Аренда бетононасоса",
              "unit": "см",
              "qty": "1",
              "work_price": "0",
              "material_price": "31000"
            },
            {
              "row": 31,
              "name": "Крепеж и расходные материалы по разделу",
              "unit": "к-т",
              "qty": "702",
              "work_price": "0",
              "material_price": "120"
            },
            {
              "row": 32,
              "name": "Накладные расходы",
              "unit": "",
              "qty": "0.1",
              "work_price": "",
              "material_price": ""
            }
          ],
          "formula_count": 88,
          "formula_samples": [
            {
              "sheet": "смета",
              "cell": "F4",
              "formula": "=E4*D4"
            },
            {
              "sheet": "смета",
              "cell": "F5",
              "formula": "=E5*D5"
            },
            {
              "sheet": "смета",
              "cell": "H5",
              "formula": "=D5*G5"
            },
            {
              "sheet": "смета",
              "cell": "I5",
              "formula": "=F5+H5"
            },
            {
              "sheet": "смета",
              "cell": "D6",
              "formula": "=ROUNDUP((680*0.62)/200,0)"
            },
            {
              "sheet": "смета",
              "cell": "F6",
              "formula": "=E6*D6"
            },
            {
              "sheet": "смета",
              "cell": "H6",
              "formula": "=D6*G6"
            },
            {
              "sheet": "смета",
              "cell": "I6",
              "formula": "=F6+H6"
            },
            {
              "sheet": "смета",
              "cell": "D7",
              "formula": "=D6"
            },
            {
              "sheet": "смета",
              "cell": "F7",
              "formula": "=E7*D7"
            },
            {
              "sheet": "смета",
              "cell": "H7",
              "formula": "=D7*G7"
            },
            {
              "sheet": "смета",
              "cell": "I7",
              "formula": "=F7+H7"
            },
            {
              "sheet": "смета",
              "cell": "F8",
              "formula": "=E8*D8"
            },
            {
              "sheet": "смета",
              "cell": "H8",
              "formula": "=D8*G8"
            },
            {
              "sheet": "смета",
              "cell": "I8",
              "formula": "=F8+H8"
            },
            {
              "sheet": "смета",
              "cell": "F9",
              "formula": "=E9*D9"
            },
            {
              "sheet": "смета",
              "cell": "H9",
              "formula": "=D9*G9"
            },
            {
              "sheet": "смета",
              "cell": "I9",
              "formula": "=F9+H9"
            },
            {
              "sheet": "смета",
              "cell": "F10",
              "formula": "=E10*D10"
            },
            {
              "sheet": "смета",
              "cell": "H10",
              "formula": "=D10*G10"
            },
            {
              "sheet": "смета",
              "cell": "I10",
              "formula": "=F10+H10"
            },
            {
              "sheet": "смета",
              "cell": "D11",
              "formula": "=114+493"
            },
            {
              "sheet": "смета",
              "cell": "F11",
              "formula": "=E11*D11"
            },
            {
              "sheet": "смета",
              "cell": "H11",
              "formula": "=G11*D11"
            },
            {
              "sheet": "смета",
              "cell": "I11",
              "formula": "=F11+H11"
            },
            {
              "sheet": "смета",
              "cell": "F12",
              "formula": "=E12*D12"
            },
            {
              "sheet": "смета",
              "cell": "H12",
              "formula": "=G12*D12"
            },
            {
              "sheet": "смета",
              "cell": "I12",
              "formula": "=F12+H12"
            },
            {
              "sheet": "смета",
              "cell": "F13",
              "formula": "=E13*D13"
            },
            {
              "sheet": "смета",
              "cell": "H13",
              "formula": "=G13*D13"
            }
          ],
          "row_count": 50
        }
      ]
    },
    {
      "key": "AREAL_NEVA",
      "title": "Ареал Нева.xlsx",
      "template_role": "general_company_estimate_template",
      "description": "Общий эталон сметной структуры Ареал-Нева",
      "file_id": "1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm",
      "drive_url": "https://docs.google.com/spreadsheets/d/1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm/edit?usp=drivesdk&ouid=110231323399920032425&rtpof=true&sd=true",
      "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "modifiedTime": "2026-05-02T12:04:37.000Z",
      "parents": [
        "13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB"
      ],
      "formula_total": 1192,
      "formula_samples": [
        {
          "sheet": "смета",
          "cell": "H1",
          "formula": "=SUM(H2:I9)"
        },
        {
          "sheet": "смета",
          "cell": "H2",
          "formula": "=L59"
        },
        {
          "sheet": "смета",
          "cell": "H3",
          "formula": "=L88"
        },
        {
          "sheet": "смета",
          "cell": "H4",
          "formula": "=L108"
        },
        {
          "sheet": "смета",
          "cell": "H5",
          "formula": "=L134"
        },
        {
          "sheet": "смета",
          "cell": "H6",
          "formula": "=L175"
        },
        {
          "sheet": "смета",
          "cell": "H7",
          "formula": "=L190"
        },
        {
          "sheet": "смета",
          "cell": "H8",
          "formula": "=L228"
        },
        {
          "sheet": "смета",
          "cell": "H9",
          "formula": "=L256"
        },
        {
          "sheet": "смета",
          "cell": "F13",
          "formula": "=E13*D13"
        },
        {
          "sheet": "смета",
          "cell": "H13",
          "formula": "=G13*E13"
        },
        {
          "sheet": "смета",
          "cell": "I13",
          "formula": "=H13*D13"
        },
        {
          "sheet": "смета",
          "cell": "K13",
          "formula": "=J13*D13"
        },
        {
          "sheet": "смета",
          "cell": "L13",
          "formula": "=K13+I13"
        },
        {
          "sheet": "смета",
          "cell": "D14",
          "formula": "=_xlfn.CEILING.MATH(D13*1.2/30,)"
        },
        {
          "sheet": "смета",
          "cell": "F14",
          "formula": "=E14*D14"
        },
        {
          "sheet": "смета",
          "cell": "H14",
          "formula": "=G14*E14"
        },
        {
          "sheet": "смета",
          "cell": "I14",
          "formula": "=H14*D14"
        },
        {
          "sheet": "смета",
          "cell": "K14",
          "formula": "=J14*D14"
        },
        {
          "sheet": "смета",
          "cell": "L14",
          "formula": "=K14+I14"
        },
        {
          "sheet": "смета",
          "cell": "M14",
          "formula": "=D14*3.6*15/1000"
        },
        {
          "sheet": "смета",
          "cell": "D15",
          "formula": "=21.1+10.48+92.15"
        },
        {
          "sheet": "смета",
          "cell": "F15",
          "formula": "=E15*D15"
        },
        {
          "sheet": "смета",
          "cell": "H15",
          "formula": "=G15*E15"
        },
        {
          "sheet": "смета",
          "cell": "I15",
          "formula": "=H15*D15"
        },
        {
          "sheet": "смета",
          "cell": "K15",
          "formula": "=J15*D15"
        },
        {
          "sheet": "смета",
          "cell": "L15",
          "formula": "=K15+I15"
        },
        {
          "sheet": "смета",
          "cell": "D16",
          "formula": "=88+20"
        },
        {
          "sheet": "смета",
          "cell": "F16",
          "formula": "=E16*D16"
        },
        {
          "sheet": "смета",
          "cell": "H16",
          "formula": "=G16*E16"
        },
        {
          "sheet": "смета",
          "cell": "I16",
          "formula": "=H16*D16"
        },
        {
          "sheet": "смета",
          "cell": "K16",
          "formula": "=J16*D16"
        },
        {
          "sheet": "смета",
          "cell": "L16",
          "formula": "=K16+I16"
        },
        {
          "sheet": "смета",
          "cell": "M16",
          "formula": "=D16*25/1000"
        },
        {
          "sheet": "смета",
          "cell": "F17",
          "formula": "=E17*D17"
        },
        {
          "sheet": "смета",
          "cell": "H17",
          "formula": "=G17*E17"
        },
        {
          "sheet": "смета",
          "cell": "I17",
          "formula": "=H17*D17"
        },
        {
          "sheet": "смета",
          "cell": "K17",
          "formula": "=J17*D17"
        },
        {
          "sheet": "смета",
          "cell": "L17",
          "formula": "=K17+I17"
        },
        {
          "sheet": "смета",
          "cell": "F18",
          "formula": "=E18*D18"
        },
        {
          "sheet": "смета",
          "cell": "H18",
          "formula": "=G18*E18"
        },
        {
          "sheet": "смета",
          "cell": "I18",
          "formula": "=H18*D18"
        },
        {
          "sheet": "смета",
          "cell": "K18",
          "formula": "=J18*D18"
        },
        {
          "sheet": "смета",
          "cell": "L18",
          "formula": "=K18+I18"
        },
        {
          "sheet": "смета",
          "cell": "F19",
          "formula": "=E19*D19"
        },
        {
          "sheet": "смета",
          "cell": "H19",
          "formula": "=G19*E19"
        },
        {
          "sheet": "смета",
          "cell": "I19",
          "formula": "=H19*D19"
        },
        {
          "sheet": "смета",
          "cell": "K19",
          "formula": "=J19*D19"
        },
        {
          "sheet": "смета",
          "cell": "L19",
          "formula": "=K19+I19"
        },
        {
          "sheet": "смета",
          "cell": "D20",
          "formula": "=D15*4*1.15/1000"
        }
      ],
      "sheets": [
        {
          "sheet_name": "смета",
          "scenario": "gasbeton_or_masonry_with_monolithic_foundation",
          "sections": [
            "Кровля",
            "Окна, двери",
            "Внешняя отделка"
          ],
          "header_rows": [
            10,
            60,
            89,
            109,
            135,
            176,
            191,
            229
          ],
          "total_rows": [
            {
              "row": 58,
              "text": "Итого материалы: 1680034.1595788796"
            },
            {
              "row": 59,
              "text": "Итого стены, перегородки: 3241241.2684789114"
            },
            {
              "row": 87,
              "text": "Итого материалы: 1090794.738551488"
            },
            {
              "row": 88,
              "text": "Итого перекрытие: 1769547.369441491"
            },
            {
              "row": 107,
              "text": "Итого материалы: 102555.32"
            },
            {
              "row": 108,
              "text": "Итого Монолитная лестница: 215046.5296"
            },
            {
              "row": 133,
              "text": "Итого материалы: 653804.812"
            },
            {
              "row": 134,
              "text": "Итого Плита покрытия: 1112208.3857600002"
            },
            {
              "row": 174,
              "text": "Итого материалы: 1341914.6016"
            },
            {
              "row": 175,
              "text": "Итого крыша: 2323433.1369439997"
            },
            {
              "row": 189,
              "text": "Итого материалы: 746966.3"
            },
            {
              "row": 190,
              "text": "Итого Окна, двери: 906743.5"
            },
            {
              "row": 227,
              "text": "Итого материалы: 1888361.2"
            },
            {
              "row": 228,
              "text": "Итого внешняя отделка: 3125622.04768"
            },
            {
              "row": 255,
              "text": "Итого материалы: 569074.08"
            },
            {
              "row": 256,
              "text": "Итого Внутренняя черновая отделка: 1392456.54324"
            },
            {
              "row": 258,
              "text": "Итого РАБОТЫ: 6012793.569414035"
            },
            {
              "row": 259,
              "text": "Итого МАТЕРИАЛЫ: 8073505.2117303675"
            },
            {
              "row": 260,
              "text": "ИТОГО СМЕТНАЯ СТОИМОСТЬ: 14086298.781144403"
            }
          ],
          "material_rows": 194,
          "work_rows": 78,
          "logistics_rows": 18,
          "sample_rows": [
            {
              "row": 10,
              "name": "Наименование",
              "unit": "Ед. изм.",
              "qty": "Кол-во",
              "work_price": "Себестоимость работ",
              "material_price": "коэф на работы"
            },
            {
              "row": 13,
              "name": "Устройство отсечной гидроизоляции основания стен",
              "unit": "мп",
              "qty": "52",
              "work_price": "100",
              "material_price": "2"
            },
            {
              "row": 14,
              "name": "Гидроизоляция Линокром ХПП Технониколь черный 15 кв.м",
              "unit": "рул",
              "qty": "3",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 15,
              "name": "Кладка стен из газобетона, вкл парапет",
              "unit": "м3",
              "qty": "123.73",
              "work_price": "3000",
              "material_price": "2.2"
            },
            {
              "row": 16,
              "name": "Цементно-песчаная смесь ЦПС-300 25 кг.",
              "unit": "шт",
              "qty": "108",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 17,
              "name": "БЛОК 625X400X250",
              "unit": "м3",
              "qty": "98",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 18,
              "name": "БЛОК 625X300X250",
              "unit": "м3",
              "qty": "12",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 19,
              "name": "БЛОК 625X250X250",
              "unit": "м3",
              "qty": "24",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 20,
              "name": "Арматура А3 А240 8мм рифленая",
              "unit": "т",
              "qty": "0.569158",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 21,
              "name": "Клей для газобетона 25 кг",
              "unit": "шт",
              "qty": "154",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 22,
              "name": "Кладка перегородок из газобетона",
              "unit": "м3",
              "qty": "13.72",
              "work_price": "6500",
              "material_price": "2"
            },
            {
              "row": 23,
              "name": "Цементно-песчаная смесь ЦПС-300 25 кг.",
              "unit": "шт",
              "qty": "7",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 24,
              "name": "БЛОК 625X150X250",
              "unit": "м3",
              "qty": "16",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 25,
              "name": "Арматура класс А3 500С 8мм рифленая",
              "unit": "т",
              "qty": "0.07948600000000001",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 26,
              "name": "Клей для газобетона 25 кг",
              "unit": "шт",
              "qty": "17",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 27,
              "name": "Аренда крана",
              "unit": "см",
              "qty": "3",
              "work_price": "27000",
              "material_price": "1.15"
            },
            {
              "row": 28,
              "name": "Устройство ж/б колонн",
              "unit": "мп",
              "qty": "8.75",
              "work_price": "1300",
              "material_price": "2"
            },
            {
              "row": 29,
              "name": "Арматура металлическая д.12 А500",
              "unit": "т",
              "qty": "0.041503500000000006",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 30,
              "name": "Арматура металлическая д.8 А240",
              "unit": "т",
              "qty": "0.028151999999999996",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 31,
              "name": "Проволока вязальная 1,2мм",
              "unit": "кг",
              "qty": "2",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 32,
              "name": "Пескобетон (ЦПС М300) 40 кг",
              "unit": "шт",
              "qty": "32",
              "work_price": "",
              "material_price": ""
            },
            {
              "row": 33,
              "name": "Доска обрезная 40*150(100/200)*6000мм е/в",
              "unit": "м3",
              "qty": "0.4725",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 34,
              "name": "Устройство армопояса парапета",
              "unit": "мп",
              "qty": "75.93",
              "work_price": "900",
              "material_price": "2"
            },
            {
              "row": 35,
              "name": "Арматура металлическая д.12 А500",
              "unit": "т",
              "qty": "0.16182201599999999",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 36,
              "name": "Арматура металлическая д.8 А500",
              "unit": "т",
              "qty": "0.06998215",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 37,
              "name": "Проволока вязальная 1,2мм",
              "unit": "кг",
              "qty": "4",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 38,
              "name": "Бетон В25 W6",
              "unit": "м3",
              "qty": "4",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 39,
              "name": "Доска обрезная 40*150*6000мм е/в хв/п",
              "unit": "м3",
              "qty": "0.9111600000000001",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 40,
              "name": "Устройство перемычки/ армопояс из U блоков",
              "unit": "мп",
              "qty": "36.1",
              "work_price": "1000",
              "material_price": "2"
            },
            {
              "row": 41,
              "name": "U-блок 300 300х250х500мм",
              "unit": "шт",
              "qty": "7",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 42,
              "name": "U-блок 400 400х250х500мм",
              "unit": "шт",
              "qty": "66",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 43,
              "name": "Арматура металлическая д.12 А500",
              "unit": "т",
              "qty": "0.15387263999999998",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 44,
              "name": "Арматура металлическая д.8 А500",
              "unit": "т",
              "qty": "0.059411",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 45,
              "name": "Проволока вязальная 1,2мм",
              "unit": "кг",
              "qty": "4",
              "work_price": "",
              "material_price": "2"
            },
            {
              "row": 46,
              "name": "Пескобетон (ЦПС М300) 40 кг",
              "unit": "шт",
              "qty": "36",
              "work_price": "",
              "material_price": ""
            }
          ],
          "formula_count": 1192,
          "formula_samples": [
            {
              "sheet": "смета",
              "cell": "H1",
              "formula": "=SUM(H2:I9)"
            },
            {
              "sheet": "смета",
              "cell": "H2",
              "formula": "=L59"
            },
            {
              "sheet": "смета",
              "cell": "H3",
              "formula": "=L88"
            },
            {
              "sheet": "смета",
              "cell": "H4",
              "formula": "=L108"
            },
            {
              "sheet": "смета",
              "cell": "H5",
              "formula": "=L134"
            },
            {
              "sheet": "смета",
              "cell": "H6",
              "formula": "=L175"
            },
            {
              "sheet": "смета",
              "cell": "H7",
              "formula": "=L190"
            },
            {
              "sheet": "смета",
              "cell": "H8",
              "formula": "=L228"
            },
            {
              "sheet": "смета",
              "cell": "H9",
              "formula": "=L256"
            },
            {
              "sheet": "смета",
              "cell": "F13",
              "formula": "=E13*D13"
            },
            {
              "sheet": "смета",
              "cell": "H13",
              "formula": "=G13*E13"
            },
            {
              "sheet": "смета",
              "cell": "I13",
              "formula": "=H13*D13"
            },
            {
              "sheet": "смета",
              "cell": "K13",
              "formula": "=J13*D13"
            },
            {
              "sheet": "смета",
              "cell": "L13",
              "formula": "=K13+I13"
            },
            {
              "sheet": "смета",
              "cell": "D14",
              "formula": "=_xlfn.CEILING.MATH(D13*1.2/30,)"
            },
            {
              "sheet": "смета",
              "cell": "F14",
              "formula": "=E14*D14"
            },
            {
              "sheet": "смета",
              "cell": "H14",
              "formula": "=G14*E14"
            },
            {
              "sheet": "смета",
              "cell": "I14",
              "formula": "=H14*D14"
            },
            {
              "sheet": "смета",
              "cell": "K14",
              "formula": "=J14*D14"
            },
            {
              "sheet": "смета",
              "cell": "L14",
              "formula": "=K14+I14"
            },
            {
              "sheet": "смета",
              "cell": "M14",
              "formula": "=D14*3.6*15/1000"
            },
            {
              "sheet": "смета",
              "cell": "D15",
              "formula": "=21.1+10.48+92.15"
            },
            {
              "sheet": "смета",
              "cell": "F15",
              "formula": "=E15*D15"
            },
            {
              "sheet": "смета",
              "cell": "H15",
              "formula": "=G15*E15"
            },
            {
              "sheet": "смета",
              "cell": "I15",
              "formula": "=H15*D15"
            },
            {
              "sheet": "смета",
              "cell": "K15",
              "formula": "=J15*D15"
            },
            {
              "sheet": "смета",
              "cell": "L15",
              "formula": "=K15+I15"
            },
            {
              "sheet": "смета",
              "cell": "D16",
              "formula": "=88+20"
            },
            {
              "sheet": "смета",
              "cell": "F16",
              "formula": "=E16*D16"
            },
            {
              "sheet": "смета",
              "cell": "H16",
              "formula": "=G16*E16"
            }
          ],
          "row_count": 274
        }
      ]
    }
  ],
  "canonical_columns": [
    "№ п/п",
    "Наименование",
    "Ед. изм.",
    "Кол-во",
    "Работа Цена",
    "Работа Стоимость",
    "Материалы Цена",
    "Материалы Стоимость",
    "Всего",
    "Примечание"
  ],
  "canonical_sections": [
    "Фундамент",
    "Каркас",
    "Стены",
    "Перекрытия",
    "Кровля",
    "Окна, двери",
    "Внешняя отделка",
    "Внутренняя отделка",
    "Инженерные коммуникации",
    "Логистика",
    "Накладные расходы"
  ],
  "universal_material_groups": {
    "стены": [
      "кирпич",
      "газобетон",
      "керамоблок",
      "арболит",
      "монолит",
      "каркас",
      "брус"
    ],
    "фундамент": [
      "монолитная плита",
      "лента",
      "сваи",
      "ростверк",
      "утеплённая плита",
      "складской фундамент"
    ],
    "кровля": [
      "металлочерепица",
      "профнастил",
      "гибкая черепица",
      "фальц",
      "мембрана",
      "стропильная система"
    ],
    "перекрытия": [
      "деревянные балки",
      "монолит",
      "плиты",
      "металлические балки"
    ],
    "утепление": [
      "минвата",
      "роквул",
      "пеноплэкс",
      "pir",
      "эковата"
    ],
    "отделка": [
      "имитация бруса",
      "штукатурка",
      "плитка",
      "гкл",
      "цсп",
      "фасадная доска"
    ],
    "инженерия": [
      "электрика",
      "водоснабжение",
      "канализация",
      "отопление",
      "вентиляция"
    ],
    "логистика": [
      "доставка",
      "разгрузка",
      "манипулятор",
      "кран",
      "проживание",
      "транспорт бригады",
      "удалённость"
    ]
  },
  "formula_policy": [
    "Топовые сметы являются эталонами логики расчёта, а не прайс-листами",
    "Новые сметы считаются по такой же структуре: разделы, строки, колонки, формулы, итоги, примечания, исключения",
    "Материал может быть любым: кирпич, газобетон, каркас, монолит, кровля, перекрытия, отделка, инженерия",
    "При замене материала сохраняется расчётная логика: количество × цена = сумма; работа + материалы = всего; разделы = итоги; финальный итог = сумма разделов",
    "Каркасный сценарий, газобетон/монолитная плита, кровля/перекрытия и фундамент считаются как разные сценарии и не смешиваются",
    "Если объёмов не хватает — оркестр спрашивает только недостающие объёмы",
    "Если пользователь прислал файл как образец — сначала принять как образец, а не запускать поиск цен"
  ],
  "price_confirmation_flow": [
    "Интернет-цены материалов и техники не подставляются молча",
    "Для финальной сметы оркестр ищет актуальные цены по материалам, технике, доставке и разгрузке",
    "По каждой позиции показывает: источник, цена, единица, дата/регион, ссылка",
    "Оркестр предлагает среднюю/медианную цену без явных выбросов",
    "Пользователь выбирает: средняя / минимальная / максимальная / конкретная ссылка / ручная цена",
    "Пользователь может добавить наценку, запас, скидку, поправку по позиции, разделу или всей смете",
    "До подтверждения цен финальный XLSX/PDF не выпускается",
    "После подтверждения цены пересчитываются по формулам шаблона"
  ],
  "logistics_policy": [
    "Перед финальной сметой оркестр обязан запросить локацию объекта или расстояние от города",
    "Стоимость объекта рядом с городом и объекта за 200 км не может быть одинаковой",
    "Оркестр обязан учитывать доставку материалов, транспорт бригады, разгрузку, манипулятор/кран, проживание, удалённость, дорожные условия",
    "Если логистика неизвестна — оркестр задаёт один короткий вопрос: город/населённый пункт или расстояние от города, подъезд для грузовой техники, нужна ли разгрузка/манипулятор",
    "Логистика считается отдельным блоком сметы или отдельным коэффициентом, но не смешивается молча с ценами материалов",
    "Перед финальным результатом оркестр показывает логистические допущения и спрашивает подтверждение"
  ],
  "runtime_rule": "ai_router injects this context through core.estimate_template_policy.build_estimate_template_context"
}
```

====================================================================================================
END_FILE: docs/REPORTS/ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4_REPORT.md
FILE_CHUNK: 1/1
====================================================================================================

====================================================================================================
BEGIN_FILE: docs/REPORTS/FILE_MEMORY_DOMAIN_LINK_TITLE_P0_V5_REPORT.md
FILE_CHUNK: 1/1
SHA256_FULL_FILE: 2a4f5022a2dab3a3ed4c7446efab2e4b7d2aa7d2d144fcbb44ebb1a1322b660d
====================================================================================================
# FILE_MEMORY_DOMAIN_LINK_TITLE_P0_V5_REPORT

generated_at: 2026-05-02T13:28:20+03:00

status: OK

fixed:
- _fm_item_domain: file_name has priority before mixed hay/value search
- _fm_public_links: public links are taken only from item["links"], not from value/summary/result/raw_input blobs
- _fm_public_title: leading numeric prefix removed from file_name

verified:
- КЖ/КД/КМ/КМД/АР/project file names classify as project
- smeta/VOR file names classify as estimate
- links from unrelated blob text are not shown
- leading "4. " removed from title
- telegram_daemon.py not modified
- no live Telegram run
- worker active without fatal tracebacks

====================================================================================================
END_FILE: docs/REPORTS/FILE_MEMORY_DOMAIN_LINK_TITLE_P0_V5_REPORT.md
FILE_CHUNK: 1/1
====================================================================================================
