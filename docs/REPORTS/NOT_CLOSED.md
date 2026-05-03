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

## FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3
status: INSTALLED_NOT_VERIFIED
needs_live_test:
- topic_2: "смету дома 10×12 газобетон монолит 2 этажа 120 км коробка"
- expected: template selected, correct sheet selected, template prices + online prices with sources + price choice menu
- reply: "средняя плюс 10% да сделай"
- expected: same estimate task continues, XLSX/PDF created from template, Drive or Telegram fallback links returned
