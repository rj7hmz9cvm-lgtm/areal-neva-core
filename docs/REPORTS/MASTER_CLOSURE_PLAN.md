# AREAL-NEVA ORCHESTRA — MASTER CLOSURE PLAN
Версия: 30.04.2026 | Режим: FACT-ONLY | Источник истины: live server + LATEST_HANDOFF + NOT_CLOSED

---

## ЧАСТЬ 1 — ФАКТЫ (только подтверждённые)

### 1.1 Что VERIFIED в live-тестах (30.04.2026)

По LATEST_HANDOFF 05:40 + выводам терминала:

| Контур | Факт | Источник |
|---|---|---|
| Drive upload OAuth scope=drive | UPLOAD: True 1KtspYz... | live test 05:36 |
| daemon OAuth (override.conf) | BOT STARTED, polling active | journal 05:14 |
| file intake NEW→NEEDS_CONTEXT→меню | FILE_INTAKE_GUARD_HIT в логах | logs |
| voice choice → FILE_CHOICE_PARSED | log: FILE_CHOICE_PARSED intent=template | logs |
| upload_retry_queue cron 10min | RETRY_UPLOAD_OK task=01a41c8d | logs 04:11 |
| topic folder isolation | retry → chat_id/topic_id папка | logs |
| source guard google_drive→CANCELLED | SOURCE_GUARD_SKIP в логах 05:00 | logs |
| engine_base.py восстановлен | import OK, UPLOAD: True | live test |
| OAuth scope=drive везде | grep: drive.file заменён | server 05:36 |
| OAuth refresh_token не протухает | app в Production | Google Console |

### 1.2 Что INSTALLED но НЕ VERIFIED live-тестом

По маркерам в task_worker.py + отсутствию логов:

| Патч | Строки | Что не проверено |
|---|---|---|
| PATCH_DOWNLOAD_OAUTH_V1 | 1807-1835 | OAuth download реального файла |
| PATCH_SOURCE_GUARD_V1 | 1834-1847 | только google_drive файлы видели |
| PATCH_FILE_ERROR_RETRY_V1 | 1029-1055 | reply на ошибку не сработал в тестах |
| PATCH_DRIVE_BOTMSG_SAVE_V1 | 2046-2055 | bot_message_id в задачах пустой |
| PATCH_CRASH_BOTMSG_V1 | 1774-1790 | crash не воспроизводили |
| PATCH_DUPLICATE_GUARD_V1 | 1800 | не тестировали |
| PATCH_MULTI_FILE_INTAKE_V1 | 1846 | не тестировали |
| PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1 | 1095-1118 | не тестировали |
| PATCH_DAEMON_USE_OAUTH_V1 | daemon 707 | "Ошибка обработки" продолжалась |
| PATCH_VOICE_OAUTH_V1 | daemon 844 | не тестировали после патча |

### 1.3 Баги подтверждённые из live БД и Telegram-скринов

**BUG_CONFIRM_UNFINISHED** (подтверждён скринами 04:25-05:04):
- Задача `ae9f6a42` state=AWAITING_CONFIRMATION result="Документ обработан локально, но загрузка в Drive завершилась ошибкой"
- Бот спрашивал "Доволен результатом?" хотя Drive upload упал
- Файл: task_worker.py строки 2070-2075 (PATCH_DRIVE_BOTMSG_SAVE_V1)

**BUG_TEMPLATE_NO_STRUCT** (подтверждён из БД topic=210):
- АР АК-М-160.pdf, КД АК-М-160.pdf, КЖ АК-М-160.pdf
- result = "GSPublisherVersion 0.88... г.Санкт-Петербург..." — сырой OCR текст
- Файл: core/artifact_pipeline.py — intent игнорируется, нет template ветки
- Пользователь ожидал: структурную модель проекта

**BUG_DAEMON_INVALID_SCOPE** (подтверждён логами 04:23-05:31):
- "Drive upload failed: invalid_scope: Bad Request"
- Исправлен PATCH_SCOPE_FULL_V1 в 05:36, но полный live-тест с файлом не завершён

**BUG_ISSUE_2_OBSOLETE** (факт из GitHub):
- Issue #2 "fix permanent Drive artifact upload contour" открыт
- Но LATEST_HANDOFF говорит VERIFIED: engine_base, OAuth, scope=drive
- Issue #2 устарел — требует закрытия как superseded by PATCH_SCOPE_FULL_V1

### 1.4 Факты из live БД topic=210 (2026-04-30 02:52-02:56)

Задачи были массово CANCELLED. Причина: пользователь сказал "отмени все задачи".
Не системная уборка. Не FAILED. Реальная отмена пользователем.

Незавершённые до отмены:
- КЖ АК-М-160.pdf — state=NEEDS_CONTEXT → CANCELLED (не обработан)
- КД АК-М-160.pdf — intent=template, result=OCR текст (выполнен неправильно)
- АР АК-М-160.pdf — intent="Шаблон проекта", result=OCR текст (выполнен неправильно)

---

## ЧАСТЬ 2 — ПЛАН ЗАКРЫТИЯ (7 проходов по GPT-анализу + фактам)

**ПРАВИЛО:** написан ≠ установлен ≠ закрыт. Закрыто только после live Telegram-теста.

---

### ПРОХОД 1 — PATCH_CONFIRM_ONLY_ON_DONE_V1
**Приоритет:** ПЕРВЫЙ — без этого все остальные результаты будут некорректно подтверждаться

**Файл:** task_worker.py строки 2070-2075
**Факт:** AWAITING_CONFIRMATION + "Доволен результатом?" ставится всегда

**Правило:**
```
AWAITING_CONFIRMATION разрешён ТОЛЬКО если:
- result не содержит: "ожидает анализа", "Ошибка", "не удалась",
  "завершилась ошибкой", "недоступен", "обработан локально"
- len(result.strip()) > 100 символов
- нет active error_message
- для file/project задачи есть artifact_path ИЛИ drive_link ИЛИ PROJECT_TEMPLATE_MODEL

Если условия не выполнены:
- state = FAILED
- error_message = RESULT_NOT_READY
- Telegram: "Не удалось обработать файл. Попробуй ещё раз или сделай reply."
- НЕ отправлять "Доволен результатом?"
```

**Acceptance:**
- ошибка Drive → FAILED + сообщение, БЕЗ "Доволен?"
- нет артефакта → FAILED + сообщение, БЕЗ "Доволен?"
- есть артефакт и Drive link → AWAITING_CONFIRMATION

---

### ПРОХОД 2 — PATCH_TEMPLATE_INTENT_V1
**Файлы:** core/artifact_pipeline.py + core/template_manager.py

**Факт:** analyze_downloaded_file игнорирует user_text/intent. Строка 297-355: для document делает _extract_pdf → текст → _build_word "Сводка по документу"

**Что нужно:**
intent=template → не summary, а PROJECT_TEMPLATE_MODEL:
```json
{
  "project_type": "АР/КЖ/КД/КМ/КМД/КР",
  "source_files": [],
  "sheet_register": [],
  "marks": [],
  "axes_grid": [],
  "plans": [],
  "sections": [],
  "facades": [],
  "nodes": [],
  "specifications": [],
  "materials": [],
  "variable_parameters": [],
  "output_documents": []
}
```

**Acceptance:**
- АР PDF + intent=template → JSON модель + DOCX состав листов
- КД PDF + intent=template → JSON модель
- НЕ OCR текст

---

### ПРОХОД 3 — VOICE CONFIRM при AWAITING_CONFIRMATION
**Файл:** telegram_daemon.py ~строка 601
**Факт:** голосовое "да/нет" не закрывает задачу AWAITING_CONFIRMATION

**Acceptance:**
- "[VOICE] да" → confirm_result
- "[VOICE] нет/правки" → reject_result/revision
- только для реальной AWAITING_CONFIRMATION

---

### ПРОХОД 4 — LIVE-ТЕСТЫ INSTALLED ПАТЧЕЙ
**Правило:** не патчить повторно до live-теста. Сначала тест, потом фикс по факту.

| Патч | Тест |
|---|---|
| PATCH_FILE_ERROR_RETRY_V1 | reply на "Ошибка обработки" → перезапуск файла |
| PATCH_CRASH_BOTMSG_V1 | crash → bot_message_id сохранился в задаче |
| PATCH_DUPLICATE_GUARD_V1 | отправить тот же файл дважды |
| PATCH_MULTI_FILE_INTAKE_V1 | несколько файлов одновременно |
| PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1 | отправить голую ссылку |
| PATCH_DAEMON_USE_OAUTH_V1 | новый файл → NO invalid_scope |
| PATCH_VOICE_OAUTH_V1 | голосовое → NO invalid_scope |

---

### ПРОХОД 5 — ESTIMATE CONTOUR (Смета PDF → Excel → Drive)
**Файлы:** core/estimate_engine.py + core/artifact_pipeline.py
**Факт:** P2 в NOT_CLOSED, не тестировалось

**Pipeline:**
PDF смета → Python extract → нормализация позиций → Excel с формулами → Drive → Telegram link

**Acceptance:**
- PDF сметы → XLSX с формулами =C2*D2 + =SUM
- Drive link в Telegram
- НЕ текстовая смета

---

### ПРОХОД 6 — TECHNADZOR / DEFECT PHOTO / НОРМЫ
**Файлы:** core/technadzor_engine.py + core/artifact_pipeline.py
**Факт:** P2, фото дефекта → OCR текст без акта и норм

**Acceptance:**
- фото дефекта → DOCX/PDF акт + норма (СП/ГОСТ) + Drive link
- если норма не найдена → "норма не подтверждена"

---

### ПРОХОД 7 — PROJECT_ENGINE END-TO-END
**Файл:** core/project_engine.py (создать)
**Зависит от:** ПРОХОД 2 (template_manager)

**После шаблона:** новая команда → генерация проектного документа (DOCX/PDF/XLSX)

---

## ЧАСТЬ 3 — GITHUB ISSUES HYGIENE

**Issue #2** "fix permanent Drive artifact upload contour":
- Статус: OBSOLETE
- Причина: superseded by PATCH_SCOPE_FULL_V1 + PATCH_DAEMON_OAUTH_OVERRIDE_V1 + LATEST_HANDOFF 30.04.2026
- Действие: закрыть как "superseded"

**Правило для новых сессий:**
Приоритет истины:
1. Живой вывод сервера (logs/db)
2. LATEST_HANDOFF
3. NOT_CLOSED
4. VERIFIED chat_exports
5. GitHub Issues — только как задачи, НЕ как факты

---

## ЧАСТЬ 4 — ЗАПРЕЩЁННЫЕ ОТВЕТЫ СИСТЕМЫ

Следующие строки ЗАПРЕЩЕНЫ как финальный ответ пользователю:
- "Файл скачан, ожидает анализа"
- "Анализирую, результат будет готов"
- "Проверяю доступные файлы"
- "Доволен результатом?" — если нет артефакта
- "Структура проекта включает этапы..."
- "Файл содержит проект архитектурного раздела..."
- "Этот чат предназначен для..."
- "Выбор принят" — без запуска engine

---

## ЧАСТЬ 5 — DB SCHEMA (факт из сервера 30.04)

```
tasks:          id, state, topic_id, chat_id, input_type, raw_input, result,
                error_message, bot_message_id, reply_to_message_id, created_at, updated_at
task_history:   id, task_id, action, created_at   ← колонка называется "action" (не "event")
drive_files:    id, task_id, drive_file_id, file_name, mime_type, stage, created_at
pin:            task_id, state, updated_at
processed_updates: (дедупликация)
```

---

## ЧАСТЬ 6 — CRON (факт с сервера)

```
*/10  core/upload_retry_queue.py   — retry Drive upload из TG
*/30  tools/context_aggregator.py  — обновление ONE_SHARED_CONTEXT
*/5   monitor_jobs.py              — мониторинг зависших задач
0 */6 auto_memory_dump.sh          — дамп памяти
```

---

## ПОРЯДОК ЗАКРЫТИЯ

```
ПРОХОД 1 — PATCH_CONFIRM_ONLY_ON_DONE_V1      (task_worker.py)
ПРОХОД 2 — PATCH_TEMPLATE_INTENT_V1           (artifact_pipeline + template_manager)
ПРОХОД 3 — Voice confirm                      (telegram_daemon.py с явного «да»)
ПРОХОД 4 — Live-тесты INSTALLED патчей        (без нового кода, только тесты)
ПРОХОД 5 — Estimate contour                   (estimate_engine)
ПРОХОД 6 — Technadzor contour                 (technadzor_engine)
ПРОХОД 7 — Project engine end-to-end          (project_engine, после template_manager)
```
