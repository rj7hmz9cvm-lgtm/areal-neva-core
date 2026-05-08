# SINGLE_MODEL_FULL_CONTEXT

GENERATED_AT: 2026-05-08T18:45:02.890213+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
PURPOSE: Один файл с полным контекстом проекта для любой модели
STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test

## CONTENTS
1. SUMMARY (карта статусов всех топиков и направлений)
2. DOCS/HANDOFFS/LATEST_HANDOFF.md (полностью)
3. DOCS/REPORTS/NOT_CLOSED.md (полностью)
4. DOCS/CANON_FINAL/* (полностью)
5. PER_TOPIC: status + last failed + key engine code (head)
6. PER_DIRECTION: profile + bound topics status
7. SOURCE_LINKS

================================================================================
# 1. SUMMARY
================================================================================

## GLOBAL_TOPIC_TABLE
| topic_id | name | status | active | failed_24h |
|----------|------|--------|--------|------------|
| 0 | COMMON | UNKNOWN | 0 | 0 |
| 2 | STROYKA | INSTALLED_NOT_VERIFIED | 1 | 1 |
| 5 | TEKHNADZOR | IDLE_NO_FAILURES_NOT_VERIFIED | 0 | 0 |
| 11 | VIDEO | UNKNOWN | 0 | 0 |
| 210 | PROEKTIROVANIE | IDLE_NO_FAILURES_NOT_VERIFIED | 0 | 0 |
| 500 | VEB_POISK | IDLE_NO_FAILURES_NOT_VERIFIED | 0 | 0 |
| 794 | DEVOPS | UNKNOWN | 0 | 0 |
| 961 | AVTOZAPCHASTI | UNKNOWN | 0 | 0 |
| 3008 | KODY_MOZGOV | UNKNOWN | 0 | 0 |
| 4569 | CRM_LEADS | UNKNOWN | 0 | 0 |
| 6104 | JOB_SEARCH | UNKNOWN | 0 | 0 |

## DIRECTION_TABLE
| direction_id | engine | enabled | topic_ids |
|--------------|--------|---------|-----------|
| general_chat | ai_router | True | [] |
| orchestration_core | ai_router | True | [3008] |
| telegram_automation | telegram_pipeline | True | [] |
| memory_archive | context_search_archive_engine | True | [] |
| internet_search | search_supplier | True | [500] |
| product_search | search_supplier | True | [] |
| auto_parts_search | search_supplier | True | [961] |
| construction_search | search_supplier | True | [] |
| technical_supervision | defect_act | True | [5] |
| estimates | estimate_unified | True | [2] |
| defect_acts | defect_act | True | [] |
| documents | document_engine | True | [] |
| spreadsheets | sheets_route | True | [] |
| google_drive_storage | drive_storage | True | [] |
| devops_server | ai_router | False | [794] |
| vpn_network | ai_router | False | [] |
| ocr_photo | ocr_engine | False | [] |
| cad_dwg | dwg_engine | False | [] |
| structural_design | project_engine | False | [210] |
| roofing | estimate_unified | False | [] |
| monolith_concrete | estimate_unified | False | [] |
| crm_leads | ai_router | False | [4569] |
| email_ingress | email_ingress | False | [] |
| social_content | content_engine | False | [] |
| video_production | video_production_agent | False | [11] |
| photo_cleanup | photo_cleanup | False | [] |
| isolated_project_ivan | ivan_project | False | [] |
| job_search | search_engine | False | [6104] |

## DRIVE_BINDING
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## REFERENCE_REGISTRIES
estimate_template_registry: loaded=True count=5
owner_reference_registry: loaded=True items=11
- M80 | М-80.xlsx | full_house_estimate_template
- M110 | М-110.xlsx | full_house_estimate_template
- ROOF_FLOORS | крыша и перекр.xlsx | roof_and_floor_estimate_template
- FOUNDATION_WAREHOUSE | фундамент_Склад2.xlsx | foundation_estimate_template
- AREAL_NEVA | Ареал Нева.xlsx | general_company_estimate_template

================================================================================
# 2. LATEST_HANDOFF
================================================================================

# LATEST HANDOFF — 2026-05-08 ~18:00 MSK
**HEAD**: `6cf91547d86c51b3e813702f9840a06eb53aab71`
**Воркер**: active (pid=2417955)
**telegram-ingress**: active + bigfile wrapper (areal_telegram_wrapper.py)

---

## СТАТУС ТОПИКОВ

| Топик | Состояние | Примечание |
|-------|-----------|------------|
| topic_2 СТРОИКА | AWAITING_CONFIRMATION c94ec497 / CODEX_FULL_CANON_VERIFIED | bot_msg=10547, total=8 173 431 руб, state исправлен |
| topic_5 ТЕХНАДЗОР | INSTALLED (не VERIFIED) | SA Drive upload fails 403, OAuth fallback в коде, live-тест не пройден |
| topic_500 ПОИСК | INSTALLED (не VERIFIED) | 9 режимов adaptive output |
| topic_210 PROJECT | Active | без изменений |

---

## ЗАКРЫТО В ЭТОЙ СЕССИИ (08.05.2026)

### 1. PATCH_TELEGRAM_BIG_FILE_LOCAL_BOT_API_V1 — ACTIVATED ✅
- `/usr/local/bin/telegram-bot-api` 42MB — бинарь собран, active
- `/etc/systemd/system/telegram-ingress.service.d/bigfile.conf` — скопирован
- Credentials в `/etc/areal/telegram-local-api.env`
- telegram-ingress запущен с areal_telegram_wrapper.py

### 2. PATCH_TOPIC2_REALSHEET_PRICES_V3 — COMMITTED ✅
- commit 2475eb5: real Газобетонный дом prices из шаблона

### 3. PATCH_TOPIC2_ADD_PEREKRYTIYA_SECTION_V1 — COMMITTED ✅
- commit 6cf9154: §5 Перекрытия добавлена (8 строк: опалубка, армирование, бетон, утепление)
- Пересчёт накладных расходов на новый subtotal

### 4. c94ec497 — CODEX FULL CANON VERIFIED ✅
- task_id: c94ec497-4351-43a7-a106-b3dab1633838
- topic_id: 2
- state: AWAITING_CONFIRMATION
- bot_message_id: 10547
- Итого без НДС: 8 173 431.09 руб
- С НДС: 9 808 117 руб
- Excel: https://drive.google.com/file/d/1na8ah3ZwMfQbaGMvs96VpHjhzXM8Slnv/view
- PDF: https://drive.google.com/file/d/10uQ5leWMsCClhE9N5YCdIcMM8vEhFA2Z/view

#### Canonical markers после START_ROWID=89408:
| Маркер | Статус |
|--------|--------|
| FILE_INTAKE_ROUTER_LOCAL_PATH_PASSED | ✅ 89409 |
| FILE_INTAKE_ROUTER_TOPIC2_CANONICAL_ROUTE | ✅ 89410 |
| TOPIC2_PDF_SPEC_EXTRACTOR_STARTED | ✅ 89411 |
| TOPIC2_PDF_SPEC_ROWS_EXTRACTED:7 | ✅ 89412 |
| TOPIC2_PRICE_CHOICE_CONFIRMED:median | ✅ 89413 (публично: "Цены: средние") |
| TOPIC2_LOGISTICS_DISTANCE_KM:30 | ✅ 89414 |
| TOPIC2_PDF_TOTALS_MATCH_XLSX:8173431.09 | ✅ 89417 |
| TOPIC2_DRIVE_TOPIC_FOLDER_OK | ✅ 89418 |
| TOPIC2_DRIVE_LINKS_SAVED | ✅ 89419 |
| TOPIC2_TEMPLATE_SELECTED:Ареал Нева.xlsx | ✅ 89421 |
| TOPIC2_TEMPLATE_FILE_ID:1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm | ✅ 89422 |
| TOPIC2_TEMPLATE_CACHE_USED | ✅ 89423 |
| TOPIC2_XLSX_ROWS_WRITTEN:136 | ✅ 89426 |
| TOPIC2_XLSX_FORMULAS_OK | ✅ 89427 |
| TOPIC2_XLSX_CANON_COLUMNS_OK:15 | ✅ 89428 |
| TOPIC2_PDF_CREATED | ✅ 89429 |
| TOPIC2_PDF_CYRILLIC_OK | ✅ 89430 |
| TOPIC2_DRIVE_UPLOAD_XLSX_OK | ✅ 89431 |
| TOPIC2_DRIVE_UPLOAD_PDF_OK | ✅ 89432 |
| TOPIC2_TELEGRAM_DELIVERED:10547 | ✅ 89433 |
| TOPIC2_FULL_ESTIMATE_MATRIX_ENFORCED | ✅ 89435 |
| TOPIC2_PUBLIC_OUTPUT_CLEAN_OK | ✅ 89436 |
| TOPIC2_BOT_MESSAGE_ID_SAVED:10547 | ✅ 89437 |
| TOPIC2_TELEGRAM_MATCHES_ARTIFACTS | ✅ 89438 |
| TOPIC2_DONE_CONTRACT_OK:total=8173431 | ✅ 89444 |
| TOPIC2_PROJECT_FACTS_READBACK_OK | ✅ CODEX |
| TOPIC2_TEMPLATE_PRICE_COLUMNS_PROVEN | ✅ CODEX |
| TOPIC2_TEMPLATE_PRICE_EXTRACTION_FIXED | ✅ CODEX |
| TOPIC2_FULL_TURNKEY_SCOPE_ENFORCED | ✅ CODEX |
| TOPIC2_XLSX_TOTAL_MANUAL_RECALC_OK:8173431.09 | ✅ CODEX |
| TOPIC2_XLSX_READBACK_OK | ✅ CODEX |
| TOPIC2_PDF_READBACK_OK | ✅ CODEX |
| TOPIC2_TELEGRAM_READBACK_OK | ✅ CODEX |
| TOPIC2_OLD_INVALID_MESSAGE_SUPERSEDED:10540 | ✅ CODEX |
| TOPIC2_OLD_INVALID_MESSAGE_SUPERSEDED:10541 | ✅ CODEX |
| TOPIC2_OLD_INVALID_MESSAGE_SUPERSEDED:10542 | ✅ CODEX |

#### Факты из PDF (runtime/drive_files/mikea_rp3.pdf, 62MB):
- Площадь: 99.91 м²  |  Этажей: 1  |  Материал: Газобетон 400/250/150мм
- Фундамент: Монолитная плита «перевёрнутая чаша»
- Кровля: Фальцевая 185 м² RAL7024
- Фасад: Штукатурка 96м² + цоколь 20м² + рейка 27.1м²
- Окна: 9 типов  |  Двери: 5 типов
- Инженерка: ОВ (3 л.) / ВК (2 л.) / ЭОМ  |  Тёплый пол: лист 37
- Дистанция: 30 км  |  Цены: средние

---

## НЕ СДЕЛАНО / ИЗВЕСТНЫЕ ПРОБЛЕМЫ

| Проблема | Статус |
|----------|--------|
| topic_5 Drive upload (SA 403) | Код OAuth fallback есть, live-тест не пройден |
| telegram-bot-api-local service | systemctl inactive — wrapper стартует binary иначе, live проверить |
| d72028da (8х12.pdf) | DONE/bot=10503, закрыта ранее |

---

## ДИАГНОСТИКА

```bash
# c94ec497 состояние
sqlite3 data/core.db "SELECT state, bot_message_id FROM tasks WHERE id='c94ec497-4351-43a7-a106-b3dab1633838';"
# Ожидаем: AWAITING_CONFIRMATION|10547

# Маркеры CODEX (последние)
sqlite3 data/core.db "SELECT rowid, action FROM task_history WHERE task_id='c94ec497-4351-43a7-a106-b3dab1633838' ORDER BY rowid DESC LIMIT 15;"

# Воркер
systemctl is-active areal-task-worker
tail -5 logs/task_worker.log
```

---

## CANON REFS
- `docs/CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md` — §10 DONE contract
- `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md` — §4, §11.9
- `core/stroyka_estimate_canon.py` — `maybe_handle_stroyka_estimate`
- `runtime/drive_files/mikea_rp3.pdf` — исходный PDF (62MB, 42 страницы)
- Template cache: `data/templates/estimate/cache/1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm__Ареал Нева.xlsx`


================================================================================
# 3. NOT_CLOSED
================================================================================

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

## FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_MEMORY_REVIVE_FIX
status: INSTALLED_NOT_VERIFIED
needs_live_test:
- topic_2: "Доделай мне нормально эту задачу"
- expected: bot finds previous valid estimate task raw_input, does not repeat old file-menu/result, starts STROYKA V3 price confirmation flow


================================================================================
# 4. CANON_FINAL
================================================================================

## CANON_FINAL/00_INDEX.md

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


## CANON_FINAL/01_SYSTEM_LOGIC_FULL.md

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


## CANON_FINAL/09_FILE_INTAKE_DRIVE_UPLOAD_2026-04-30.md

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


## CANON_FINAL/ESTIMATE_TEMPLATE_M80_M110_CANON.md

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



## CANON_FINAL/OWNER_REFERENCE_FULL_WORKFLOW_CANON.md

# OWNER_REFERENCE_FULL_WORKFLOW_CANON

version: AREAL_REFERENCE_FULL_MONOLITH_V1
updated_at: 2026-05-02T20:20:56.522887+00:00

Илья — главный канон

Сметы: М-80, М-110, крыша, фундамент, Ареал Нева — эталон формул и структуры

Проектирование: АР, КР, КЖ, КД, КМ, КМД, ОВ, ВК, ЭО, ЭМ, ЭОС, эскизы, планы участка — разные разделы, не смешивать

Технадзор: акты, дефекты, исполнительные — отдельный контур

Если данных не хватает — один короткий вопрос

counts: {"estimate_files": 6, "design_files": 231, "technadzor_files": 1, "formula_total": 4733, "all_files": 261}


## CANON_FINAL/TECHNADZOR_DOMAIN_LOGIC_CANON.md

# TECHNADZOR_DOMAIN_LOGIC_CANON
# Канон системы технического надзора — логика работы и структура документов

version: TECHNADZOR_DOMAIN_LOGIC_CANON_V1
updated_at: 2026-05-04
status: ACTIVE_CANON
topic: topic_5 / ТЕХНАДЗОР
author: Кузнецов Илья Владимирович

---

## Общая логика системы

Цель системы — не "фото → ответ", а полноценное ведение технадзора по объектам.

```
Входные материалы
→ понимание объекта и задачи
→ сбор истории объекта
→ нормализация всех материалов в карточки фактов
→ анализ дефектов
→ сверка с нормами и предыдущими актами
→ уточнение, если данных не хватает
→ текстовый технадзорный разбор или акт
→ сохранение истории объекта для следующих осмотров
```

---

## 1. Входные материалы

Оркестр принимает как вход:

- фото (одно или пачка)
- папку с фото (Drive folder)
- голос владельца
- текст владельца
- PDF акты (предыдущие или текущие)
- DOCX шаблоны / черновики / замечания
- XLSX реестры замечаний
- скриншоты переписок
- сообщения заказчика или подрядчика
- проектную и исполнительную документацию

**Главный принцип:** любой вход сначала разбирается как источник информации, а не сразу превращается в акт.

---

## 2. Определение контекста

Перед любым действием оркестр обязан понять:

- какой объект
- какая папка объекта на Drive
- какая дата выезда
- это новый осмотр или продолжение старого
- есть ли предыдущие акты
- какие фото относятся к текущему выезду
- кто автор информации: владелец / заказчик / подрядчик / документ / фото
- нужен текстовый разбор или акт
- куда можно сохранять результат

Если объект, папка, режим или задача не ясны — оркестр задаёт **один конкретный вопрос**.

---

## 3. Карточка объекта

По каждому объекту ведётся карточка (ObjectCard):

```
object_id           — уникальный идентификатор объекта
object_name         — название объекта
object_folder_url   — ссылка на Drive папку объекта
client_folder_url   — клиентская папка
service_folder_url  — служебная папка
inspection_chain[]  — цепочка осмотров
previous_acts[]     — список предыдущих актов
current_open_items[]— открытые замечания
closed_items[]      — закрытые замечания
unresolved_items[]  — неустранённые замечания
recommendations[]   — рекомендации
last_visit_date     — дата последнего выезда
last_act_no         — номер последнего акта
```

**Смысл:** следующий осмотр не начинается с нуля, а продолжает историю объекта.

---

## 4. Режимы работы

Оркестр выбирает один из режимов:

| Режим | Условие |
|---|---|
| `INITIAL_INSPECTION` | Объект новый, актов нет |
| `FOLLOWUP_INSPECTION` | Есть один предыдущий акт |
| `NEXT_INSPECTION` | Есть несколько актов, это третий и далее |
| `ADDENDUM` | Нужно дополнить существующий акт |
| `PHOTO_TECH_REPORT` | Только технический разбор без акта |
| `CLARIFICATION_REQUIRED` | Не хватает данных для продолжения |

---

## 5. Карточка наблюдения (ObservationCard)

Все материалы переводятся в единую карточку наблюдения:

```
ObservationCard:
  источник          — OWNER_VOICE / OWNER_TEXT / PHOTO_EVIDENCE /
                      PREVIOUS_ACT / CLIENT_TEXT / CONTRACTOR_TEXT /
                      PROJECT_DOCUMENT / EXECUTIVE_DOCUMENT
  автор             — владелец / заказчик / подрядчик
  тип материала     — фото / голос / текст / документ
  объект            — object_id
  дата              — дата материала
  что утверждается  — суть наблюдения
  к какому фото/документу относится
  подтверждено      — да / нет / частично
  противоречие      — есть / нет
  нужно уточнение   — да / нет
```

**Правило источников:**
- `OWNER_VOICE` / `OWNER_TEXT` — высокий приоритет, но не заменяет техническую проверку
- `CLIENT_TEXT` / `CONTRACTOR_TEXT` — заявление, не доказанный факт; формулировки: "по информации заказчика", "по информации подрядчика", "требуется фотофиксация результата"
- Запрещено писать "устранено" только со слов подрядчика без фотоподтверждения

---

## 6. Карточка дефекта (DefectCard)

Ядро системы. Из DefectCard строится текстовый разбор, акт, таблица замечаний, история объекта.

```
DefectCard:
  фото_no           — порядковый номер фото в выезде
  file_name         — реальное имя файла (IMG_4020.JPG, не Telegram ID)
  source            — PHOTO_EVIDENCE / OWNER_VOICE / PREVIOUS_ACT
  узел_место        — конкретный конструктивный элемент
  что_видно         — фактическое описание без фантазии
  дефект            — что именно не так
  почему_плохо      — техническая причина
  последствия       — что будет если не устранить
  что_исправить     — конкретное действие
  что_проверить     — что измерить / вскрыть / запросить у подрядчика
  норма             — СП / ГОСТ / "норма не подтверждена"
  статус_нормы      — CONFIRMED / PARTIAL / NOT_FOUND
  статус_замечания  — см. раздел 12
  нужна_проверка    — флаг ручной проверки
  вопрос_владельцу  — если нужно уточнение
```

---

## 7. Анализ фото

Фото анализируются как материалы осмотра, а не как случайные картинки.

По каждому фото оркестр формирует DefectCard в формате:

```
Фото №N — IMG_XXXX.JPG

Что видно:
[фактическое описание без фантазии]

Узел / место:
[конкретный элемент, если определяется]

Выявленное замечание:
[что именно не так]

Почему это плохо:
[техническая причина]

Возможные последствия:
[к чему может привести]

Что нужно сделать:
[конкретное действие]

Что проверить на объекте:
[что измерить, вскрыть, запросить]

Нормативная отсылка:
[СП / ГОСТ / "норма не подтверждена"]

Статус:
[подтверждено по фото / частично видно / требует уточнения]
```

Если фото неясное — не выдумывать. Писать "по фото однозначно не определяется" и задавать конкретный вопрос.

---

## 8. Анализ папки с фото (Drive folder)

Если дана папка с фото:

- найти все изображения
- сохранить **реальные имена файлов** (IMG_4020.JPG, не Telegram ID)
- сохранить порядок
- обрабатывать пачками по 10–11 фото
- группировать результаты по секциям, не по порядку фото
- формировать **один общий разбор или один общий акт**
- не делать отдельный акт на каждое фото

Пример разбивки по батчам:
```
batch 1: IMG_5320 – IMG_5330  (11 фото)
batch 2: IMG_5331 – IMG_5341  (11 фото)
batch 3: IMG_5342 – IMG_5352  (11 фото)
...
```

При ошибке части фото — продолжить остальные, проблемные вынести в "требует уточнения".
Если анализ долгий — дать промежуточный ответ в Telegram:
> "Принял. Нашёл папку, предыдущие акты и 61 фото. Начинаю технадзорный разбор."

---

## 9. Голос владельца

Голос владельца = полноценное техническое задание.

Из голоса нужно извлекать:
- объект, папку, дату
- что обнаружено владельцем (→ `owner_observation`)
- что включить / не включать
- нужен акт или разбор
- куда класть результат
- какие фото использовать

Голос имеет **высокий приоритет**, но не заменяет техническую проверку.

Если голос противоречит фото или документам — оркестр **не выбирает молча**, а уточняет.

---

## 10. Предыдущие акты

Если по объекту есть предыдущие акты:

- прочитать PDF / DOCX
- извлечь: замечания, рекомендации, нормы, фотофиксацию, открытые замечания
- сравнить с текущими фото и указаниями владельца

Новый акт должен **отвечать на вопросы:**
- что было выявлено раньше
- что проверялось сейчас
- что устранено / устранено частично / не устранено
- что появилось новое
- что требует доведения
- что не проверялось на текущем выезде

**Новый акт не пишется с нуля если есть история объекта.**

---

## 11. Статусы замечаний

```
НОВОЕ              — выявлено впервые на текущем выезде
ПОДТВЕРЖДЕНО       — подтверждено по фото текущего выезда
ЧАСТИЧНО_ВИДНО     — по фото частично определяется
УСТРАНЕНО          — устранено, подтверждено по фото
УСТРАНЕНО_ЧАСТИЧНО — устранено не полностью
НЕ_УСТРАНЕНО       — не устранено, подтверждено по фото
ТРЕБУЕТ_ДОВЕДЕНИЯ  — работы начаты, не завершены
НЕ_ПРОВЕРЯЛОСЬ     — не попало в фото текущего выезда
ТРЕБУЕТ_УТОЧНЕНИЯ  — недостаточно данных
```

Без статуса follow-up акт считается **неполным**.

---

## 12. Нормативная логика

Оркестр ищет нормативную базу по каждому дефекту.

**Запрещено выдумывать нормы.**

| Ситуация | Действие |
|---|---|
| Найден документ и пункт | Указать документ и пункт |
| Найден только документ | Указать документ без пункта |
| Ничего не найдено | "норма не подтверждена" |
| Дефект очевиден, норма не найдена | Дать техническое замечание и рекомендацию без нормы |

**Базовая нормативная база:**
- СП 16.13330 — стальные конструкции
- СП 70.13330 — несущие и ограждающие конструкции
- СП 28.13330 — защита строительных конструкций от коррозии
- ГОСТ 23118 — конструкции стальные строительные
- СП 48.13330 — организация строительства
- СП 13-102 — обследование несущих строительных конструкций
- ГОСТ 31937 — обследование и мониторинг технического состояния
- СП 63.13330 — бетонные и железобетонные конструкции
- СП 22.13330 — основания зданий и сооружений

---

## 13. Группировка дефектов

Замечания группируются **по смыслу дефектов**, а не по порядку фото.

**Базовые разделы:**
```
2.1 Опорные узлы колонн
    подливка, опирание, зазоры, анкера, опорные плиты, контакт с основанием

2.2 Сварные соединения
    непровар, поры, прожоги, наплывы, отсутствие зачистки, некачественный шов

2.3 Антикоррозионная защита
    отсутствие покрытия, повреждение, коррозия, незащищённые швы, открытый металл

2.4 Основание и водоотведение
    замачивание, отсутствие уклонов, загрязнение основания, риск осадок

2.5 Узлы крепления элементов покрытия
    болтовые соединения, крепления прогонов, смещение элементов, отсутствие затяжки

2.6 Связи, укосины, элементы жёсткости
    неправильное примыкание, отсутствие жёсткости, деформация, некачественный монтаж

2.7 Бетонные и железобетонные конструкции
    трещины, сколы, раковины, отсутствие защитного слоя, дефекты бетонирования

2.8 Кровля / фасад / ограждающие конструкции
    примыкания, герметизация, крепёж, водоотведение, повреждения покрытия

2.9 Прочие замечания
    всё, что не попало в основные разделы
```

**Для других профилей объектов (бетон, кровля, инженерные сети) секции меняются через конфиг профиля**, а не переписыванием логики.

---

## 14. Логика последствий

По каждому дефекту оркестр объясняет последствия. Примеры:

| Дефект | Последствия |
|---|---|
| Плохое опирание колонны | Неравномерная передача нагрузки, деформация, снижение надёжности узла |
| Дефект сварки | Снижение несущей способности, развитие трещин, потеря жёсткости |
| Отсутствие антикоррозионной защиты | Развитие коррозии, уменьшение сечения элемента, сокращение срока службы |
| Замачивание основания | Коррозия опорных элементов, ухудшение работы грунта, локальные просадки |
| Неправильный крепёж | Ослабление соединения, вибрация, смещение, аварийное развитие дефекта |

---

## 15. Логика рекомендаций

Рекомендации — конкретные, без общих фраз.

**Запрещено:** "устранить нарушение"

**Правильно:**
- зачистить сварной шов до металлического блеска
- выполнить повторную сварку дефектного участка
- восстановить антикоррозионное покрытие
- выполнить подливку опорного узла без пустот
- проверить затяжку болтовых соединений и зафиксировать
- выполнить фотофиксацию после устранения
- предоставить исполнительную документацию
- подтвердить соответствие проектному решению
- обеспечить отвод воды от основания
- выполнить повторный осмотр после исправления

---

## 16. Уточнения

Если данных не хватает — оркестр задаёт **конкретный вопрос с привязкой к фото, объекту или акту**.

**Правильно:**
- "Это фото до устранения или после?"
- "Этот узел — опорная часть колонны или крепление покрытия?"
- "Это замечание включать в акт или оставить как рабочее?"
- "Текущий документ делать как третий осмотр или как отдельное дополнение?"
- "Эти фото к тому же объекту или к новому?"
- "Нужно ли фиксировать это как неустранённое из прошлого акта?"
- "Чистовой PDF положить в клиентскую папку объекта?"

**Запрещено:**
- "что строим"
- "что это"
- "пришлите шаблон"
- "пришлите всё заново"
- общий вопрос без привязки к конкретному фото, объекту или акту

---

## 17. Текстовый технадзорный разбор (PHOTO_TECH_REPORT)

Структура ответа если акт не нужен:

```
Технический осмотр по фото

Объект: [название]
Дата / выезд: [дата]
Основание: [по фото текущего выезда / по голосовому ТЗ / с учётом предыдущих актов]
Режим: [первичный / повторный / технический разбор]
Использованные материалы: [фото, голос, документы]

Фото №1 — IMG_XXXX

  Что видно: ...
  Замечание: ...
  Почему опасно: ...
  Как исправить: ...
  Что проверить: ...
  Нормативная отсылка: ...
  Статус: ...

[Фото №2 — ...]

Итоговый вывод:
  1. Критичные замечания: ...
  2. Замечания, требующие устранения: ...
  3. Замечания, требующие уточнения: ...
  4. Что необходимо сделать: ...
  5. Что проверить после устранения: ...
  6. Следующий шаг: нужен ли акт
```

---

## 18. Структура акта осмотра

Если нужен акт — оформляется как документ технадзора владельца:

```
АКТ ОСМОТРА ОБЪЕКТА № ДД.ММ/ГГ

Методом визуального неразрушающего контроля

Дата осмотра: [дата]
Место осмотра: [адрес]
Объект осмотра: [описание объекта]
Метод обследования: визуальный неразрушающий контроль с выездом на объект
Представитель подрядчика: [имя]
Технический специалист: Кузнецов Илья Владимирович
Ссылка на фотоматериалы: [Drive ссылка]

На момент проведения осмотра проектная, рабочая и исполнительная
документация на объект [представлена / не представлена].

1. Общие сведения
   Цель, метод, что проверялось.

2. Сводка по предыдущим актам (если есть)
   Какие акты были. Открытые замечания. Статус исполнения.

3. Основание текущего осмотра
   "Текущий осмотр выполнен в развитие акта № ... от ..."

4. Установлено по факту осмотра

   4.1 [Название секции]
       [Описание дефекта]
       Нормативная отсылка: [СП/ГОСТ]
       Фотоматериалы: IMG_4020.JPG, IMG_4021.JPG, IMG_4022.JPG

   4.2 [Следующая секция]
       ...

5. Рекомендовано к устранению
   1. [Конкретное действие]
   2. ...

6. Возможные последствия при отсутствии устранения
   [Описание]

7. Таблица замечаний
   № | фото | узел/место | нарушение | последствия | что сделать | норматив | статус

   Для повторного осмотра:
   № | замечание | по предыдущему акту | текущее состояние | статус | фото | норматив | что сделать

8. Заключение
   - Устранено: ...
   - Не устранено: ...
   - Требует доведения: ...
   - Новые замечания: ...
   - Что проверить на следующем осмотре: ...

Технический специалист: Кузнецов Илья Владимирович
Дата: [дата]
```

---

## 19. Имена файлов

**Финальный PDF:**
```
Акт_осмотра_<объект>_<дата>.pdf
Пример: Акт_осмотра_ангар_Киевское_шоссе_04_05_2026.pdf
```

**DOCX черновик (только служебно):**
```
Черновик_акта_<объект>_<дата>.docx
```

**Запрещено в имени клиентского PDF:**
- UUID / task_id
- `/root` или системные пути
- `smoke`, `debug`, `tmp`, `draft`

---

## 20. Клиентские и служебные материалы

**Клиентская папка — только:**
- фото объекта (оригиналы от владельца, не трогать)
- итоговый PDF акта

**Служебная папка / `_drafts` — только:**
- DOCX черновики
- JSON индексы
- manifests, logs, кэши
- object registry
- временные файлы

**Клиентскую папку нельзя засорять служебными файлами.**

**Фото клиента запрещено:**
- переименовывать
- перемещать без команды владельца
- удалять
- сжимать

---

## 21. Идемпотентность

Система не должна дублировать фото, акты, записи памяти, object registry.

Для каждого фото хранить:
```
drive_file_id     — уникальный ID файла на Drive
file_name         — реальное имя файла
source_folder_id  — ID папки источника
inspection_date   — дата осмотра
indexed_at        — время индексации
```

Если фото уже индексировано — не копировать, не переименовывать, использовать существующую запись.
Если папка уже создана — не создавать дубль с похожим именем.

---

## 22. Расширяемость на другие профили

Ядро системы универсально:

```
InputItem → ObservationCard → DefectCard → GroupedReport → TextReport / Act
```

Для других направлений меняется **только профиль**:

| Параметр | Металлокаркас | Другой профиль |
|---|---|---|
| Секции | Опорные узлы, сварка, коррозия... | Профиль объекта |
| Нормативная база | СП 16, СП 70, ГОСТ 23118 | Нормы по направлению |
| Vision prompt | "найди дефекты стальных конструкций" | По типу объекта |
| Типовые дефекты | Перечень по металлокаркасу | По профилю |

**Профили для будущего расширения:** бетон, кровля, фасад, инженерные сети, электрика, отделка.

---

## 23. Запрещено в любом документе системы

- JSON, внутренние ID, task_id, /root пути, traceback
- "я не знаю", "пришлите всё заново"
- выдуманные нормы
- выдуманные дефекты
- пустые общие фразы
- акт без фотофиксации
- акт без вывода и рекомендаций
- акт без статуса замечаний при повторном осмотре
- "устранено" только со слов подрядчика

---

## 24. Итоговый принцип

```
Любой материал по объекту
→ понять источник и контекст
→ извлечь факты и заявления
→ отделить доказанное от неподтверждённого
→ собрать дефекты в DefectCard
→ сверить с историей объекта
→ проверить нормы
→ задать точные вопросы при пробелах
→ выдать технадзорный разбор или акт
→ сохранить историю для следующего осмотра
```

Оркестр работает как **помощник технадзора** — понимает, что скинули, зачем, какой документ нужен, есть ли история объекта, и выдаёт документ в стиле реальных актов владельца.

---

## 25. Пути передачи материалов (два равноправных пути)

Владелец передаёт материалы одним из двух путей:

### Путь A — напрямую в Google Drive
- Сам создаёт папку объекта или выезда
- Сам загружает фото, PDF, DOCX, XLSX, видео
- Затем в Telegram голосом или текстом поясняет:
  - что это за папка и объект
  - какая дата выезда
  - что он увидел
  - что нужно сделать
  - нужен разбор или акт

### Путь B — через Telegram
- Скидывает одно или несколько фото/файлов
- Сразу голосом или текстом поясняет:
  - к какому объекту относятся файлы
  - какое нарушение показано
  - какие замечания нужно написать
  - что включить в акт

**Оба пути равноправны. Логика обработки одинакова для обоих.**

---

## 26. Модель задачи технадзора

**Файл сам по себе — не задача.**

```
TechnadzorTask =
  OwnerInstruction (голос или текст владельца)
  + InputFiles     (фото, PDF, DOCX — из Drive или Telegram)
  + ObjectContext  (карточка объекта, история, предыдущие акты)
  + PreviousActs   (если есть)
```

После сборки задачи:

```
TechnadzorTask
→ ObservationCards (нормализация всех источников)
→ DefectCards      (атомарные дефекты по фото и голосу)
→ grouped sections (2.1 Опорные, 2.2 Сварка, ...)
→ один текстовый разбор или один акт
```

**Правила сборки задачи:**

1. Если файлы уже лежат на Drive — найти папку по словам владельца, не требовать повторной загрузки.
2. Если файлы пришли через Telegram — агрегировать несколько файлов в один контекст, не делать отдельную задачу на каждое фото.
3. Если владелец пишет пояснение после нескольких фото — связать пояснение со всей последней пачкой фото.
4. Если владелец пишет пояснения между группами фото — разделить фото на группы по пояснениям:
   ```
   фото 1–3 → "это сварка"       → секция "Сварные соединения"
   фото 4–7 → "это опорные узлы" → секция "Опорные узлы"
   ```
5. Если голос описывает папку ("я загрузил папку сегодняшнего выезда") — связать голос с Drive-папкой по имени или дате, не по URL.

---

## 27. Буфер выезда и агрегация фото

### Буфер выезда (Telegram-путь)
Когда фото приходят через Telegram по одному или пачками:
- каждое фото добавляется в буфер текущего выезда
- сопроводительный текст или голос добавляется как `owner_comment` к последним фото
- буфер хранится локально: `data/memory_files/chat_{id}/topic_5/visit_buffer.json`

```json
{
  "photos": [
    {
      "file_name": "IMG_5320.JPG",
      "owner_comment": "опорный узел, видна щель",
      "added_at": 1234567890
    }
  ],
  "owner_instructions": ["загрузил папку выезда, опорные узлы и сварка"],
  "object_id": "angaar_kievskoe"
}
```

Когда владелец даёт триггер ("сделай разбор", "сделай акт", "подведи итог"):
- буфер сбрасывается
- все фото обрабатываются как одна задача
- результат — один разбор или один акт

### Пакетная обработка (Drive-путь)
Когда дана ссылка на папку или папка найдена по голосу:
- найти все фото в папке
- скачать пачками по 10–11
- Vision на каждую пачку → DefectCards
- агрегировать все DefectCards
- один общий вывод

### Запрещено
- делать 61 акт из 61 фото
- обрабатывать фото без owner_comment или owner_instruction, если контекст нужен
- терять пояснение владельца
- просить повторно загрузить файлы, которые уже есть на Drive или в буфере

### Уточнение при неясной связи
Если оркестр не понял связь файлов и пояснений — задаёт конкретный вопрос:
- "Фото IMG_5320–IMG_5325 относятся к опорным узлам?"
- "Эти фото включать в акт или только в рабочий разбор?"
- "Это новый объект или продолжение объекта ангар Киевское шоссе?"
- "Это фото до устранения или после?"

---

## 28. Язык вывода и именования

### Правило
**Код — английский. Всё, что видит владелец или заказчик — только русский.**

### Запрещено на английском
- названия клиентских файлов
- текст актов и технических разборов
- Telegram-ответы
- названия Drive-папок для клиента
- описания дефектов, рекомендации, выводы
- таблицы акта, подписи к фото
- служебные пояснения владельцу

### Разрешён английский только внутри кода
- имена функций и классов
- внутренние enum и константы
- технические маркеры патчей
- служебные переменные

### Примеры правильных имён клиентских файлов
```
Акт_осмотра_ангар_Киевское_шоссе_04_05_2026.pdf
Технический_разбор_ангар_Киевское_шоссе_04_05_2026.pdf
Черновик_акта_ангар_Киевское_шоссе_04_05_2026.docx
```

### Примеры запрещённых имён
```
inspection_report.pdf
defect_report.pdf
technadzor_summary.pdf
photo_analysis.pdf
batch_report.pdf
```

### Примеры правильных Telegram-ответов
```
Принял. Нашёл папку выезда, 61 фото и предыдущие акты. Начинаю технадзорный разбор.
✓ Принял фото #1 — IMG_5320.JPG
Не удалось проанализировать фото. Пришли крупнее или опиши дефект текстом.
```

### Примеры запрещённых Telegram-ответов
```
Accepted. Found inspection folder and starting batch analysis.
Detected support node issue. Need to verify gap.
```

---

## 29. ActiveTechnadzorFolder — активная рабочая папка

Оркестр поддерживает сущность текущей рабочей папки для topic_5.

```
ActiveTechnadzorFolder:
  chat_id              — id чата
  topic_id             — всегда 5
  object_name          — название объекта
  visit_date           — дата выезда
  drive_folder_url     — ссылка на Drive-папку
  drive_folder_id      — id папки на Drive
  folder_name          — имя папки
  client_facing        — True / False / None (не определено)
  mode_hint            — initial / repeat / extension
  active_since         — время открытия
  last_update          — время последнего обновления
  owner_instructions   — список пояснений владельца
  status               — OPEN / COLLECTING / READY_TO_PROCESS / CLOSED
```

Пока `ActiveTechnadzorFolder` открыта:
- все следующие фото относятся к ней
- все следующие документы относятся к ней
- все голосовые и текстовые пояснения относятся к ней
- команда "сделай разбор/акт" работает именно по ней

`ActiveTechnadzorFolder` не заменяет `ObjectCard`. Это разные сущности:
- `ObjectCard` — постоянная история объекта по всем выездам
- `ActiveTechnadzorFolder` — сессионный контекст текущего рабочего сбора

---

## 30. Команды управления активной папкой

Оркестр обязан понимать следующие команды владельца:

**Открыть / выбрать папку:**
- "работаем по этой папке"
- "открыть папку"
- "это текущий объект"
- "это текущий выезд"

**Информация:**
- "показать активную папку"
- "что сейчас активно"

**Сменить / закрыть:**
- "сменить папку"
- "это другой объект"
- "это другой выезд"
- "закрыть сбор материалов"
- "очистить буфер текущей папки"

**Результат:**
- "сделай разбор"
- "сделай акт"
- "сделай документ"

**Управление материалами:**
- "добавить эти фото к замечанию [название]"
- "это не включать в акт"
- "это включить в акт"
- "это замечание заказчика"
- "это замечание подрядчика"
- "это мои замечания как технадзора"

При смене объекта или папки — не смешивать материалы. Текущий сбор приостанавливается или закрывается.

---

## 31. COLLECTING_VISIT_MATERIALS — режим накопления

До команды "сделай разбор / акт / документ" оркестр находится в режиме:

```
COLLECTING_VISIT_MATERIALS
```

В этом режиме оркестр:
- принимает фото, документы, видео
- принимает голосовые и текстовые пояснения
- связывает пояснения с последними файлами
- обновляет `ActiveTechnadzorFolder`
- **не создаёт финальный документ без команды владельца**

Правильные короткие ответы в режиме накопления:
```
Принял, добавил 3 фото к замечанию «опорные узлы»
Принял, 5 фото связал с разделом «сварные соединения»
Запомнил: это фото не включать в акт
Активная папка: Выезд ангар Киевское ш 04.05.2026
Принял пояснение и связал с последними фото
```

Запрещено в режиме накопления:
- делать акт или разбор на каждое отдельное фото
- отправлять 10 отчётов на 10 фото
- терять голосовые пояснения
- терять связь "фото → замечание"
- смешивать материалы разных папок

---

## 32. VisitMaterial — материал выезда

Атомарная единица сбора в рамках одного выезда.

```
VisitMaterial:
  material_id          — внутренний id
  source               — TELEGRAM / DRIVE
  file_type            — PHOTO / VIDEO / PDF / DOCX / XLSX / TEXT / VOICE / OTHER
  file_name            — реальное имя файла
  drive_url            — ссылка на Drive (если есть)
  telegram_message_id  — id сообщения в Telegram (если пришло через TG)
  added_at             — время добавления
  owner_comment        — пояснение владельца к этому материалу
  group_label          — к какой группе/замечанию относится
  include_in_report    — True / False
  include_in_act       — True / False
  defect_hint          — краткое описание дефекта от владельца
  section_hint         — подсказка по разделу (опорные узлы / сварка / ...)
  status               — PENDING / LINKED / EXCLUDED / PROCESSED
```

Правило связи пояснений с материалами:
- Если владелец пишет комментарий **после** пачки фото → комментарий связывается со всей последней пачкой
- Если владелец пишет комментарии **между** группами фото → каждая группа получает свой комментарий
- Если комментарий пришёл **до** фото → сохраняется как pending и связывается со следующей пачкой

---

## 33. VisitPackage — пакет выезда

Когда владелец даёт команду "сделай разбор / акт / документ", оркестр собирает `VisitPackage`.

```
VisitPackage:
  active_folder        — ActiveTechnadzorFolder
  object_name          — название объекта
  visit_date           — дата выезда
  previous_acts        — список предыдущих актов по объекту
  photos               — список VisitMaterial (file_type=PHOTO)
  videos               — список VisitMaterial (file_type=VIDEO)
  documents            — список VisitMaterial (PDF / DOCX / XLSX)
  owner_instructions   — все голосовые и текстовые ТЗ владельца
  client_comments      — заявления заказчика
  contractor_comments  — заявления подрядчика
  material_groups      — сгруппированные материалы по замечаниям
  excluded_materials   — материалы, исключённые из результата
  requested_output     — act / text_report / document / table
```

После сборки `VisitPackage` — единая схема обработки:

```
VisitPackage
→ ObservationCards (нормализация всех источников)
→ DefectCards      (анализ по фото, голосу, документам)
→ grouped sections (группировка по смыслу дефектов)
→ один текстовый разбор или один документ
```

`VisitPackage` собирается **один раз** по команде владельца. До команды — режим `COLLECTING_VISIT_MATERIALS`.

---

# TECHNADZOR_DOMAIN_LOGIC_CANON_V2
version: TECHNADZOR_DOMAIN_LOGIC_CANON_V2
updated_at: 2026-05-05
source_id: topic5_full_operational_logic_final
extends: TECHNADZOR_DOMAIN_LOGIC_CANON_V1
supersedes: NONE
status: ADDENDUM_NOT_REPLACEMENT

## 1. Главная модель работы

Google Drive = место хранения файлов и рабочий контейнер объекта / выезда

Telegram topic_5 = живой интерфейс управления:
- голосовые пояснения владельца
- текстовые пояснения владельца
- команды
- уточнения
- привязка фото к замечаниям
- привязка файлов к объекту
- команда на итоговый результат

Файлы сами по себе не являются задачей.

Задача = активная папка + файлы + пояснения владельца + объект + история объекта + команда на результат.

Правильная схема:

```
Владелец создаёт или выбирает папку на Google Drive
→ в Telegram говорит, что это за папка, объект, дата, что он увидел и что нужно сделать
→ оркестр открывает ActiveTechnadzorFolder
→ все следующие материалы и пояснения связывает с этой папкой
→ копит материалы
→ по команде "сделай разбор / акт / документ" собирает один общий результат
```

---

## 2. Где хранятся материалы

topic_5 = общая рабочая папка технадзора для владельца и оркестра.

Внутри topic_5 могут быть:

**A. Папки объектов / выездов** — рабочие или клиентские папки по конкретному объекту.
Пример: `topic_5 / Выезд ангар Киевское ш`

**B. Подпапки фото** — фото текущего выезда.
Пример: `topic_5 / Выезд ангар Киевское ш / фото / Выезд 04.05.2026`

**C. Служебные папки** — только для оркестра и владельца:
`topic_5 / TECHNADZOR`, `_templates`, `_drafts`, `_system`, `_manifests`, `_archive`, `_tmp`

**D. Локальные служебные папки сервера (подтверждённые):**
`data/templates/technadzor`, `data/templates/technadzor/objects`,
`data/memory_files/chat_<chat_id>/topic_5`, `/tmp` (временные локальные артефакты)

Пути `outputs/technadzor` и `runtime/technadzor` — статус UNKNOWN до подтверждения live-файлом или кодом.

---

## 3. Клиентские и служебные папки

**Client-facing папка** = папка, которую можно показать или отправить заказчику.

В client-facing папке **разрешено** хранить:
- исходные фото объекта
- чистовой итоговый документ
- чистовой PDF акта
- чистые приложения к акту
- материалы, которые владелец явно разрешил показать заказчику

В client-facing папке **запрещено** хранить:
- черновики, DOCX draft (без отдельной команды владельца), JSON, manifests, logs, debug, temp, cache
- task_id файлы, object registry, runtime files, smoke/test files
- внутренние файлы оркестра, файлы с /root путями
- случайные технические документы

Служебные материалы хранятся вне клиентской папки:
рабочие DOCX, черновики, индексы, кэши, object registry, временные и технические файлы.

DOCX не запрещён вообще — DOCX запрещён в клиентской папке, если это рабочий черновик или служебная версия.
Если владелец явно попросил дать заказчику Word/DOCX/редактируемый документ — можно, но только по отдельной команде.
По умолчанию заказчику отдаётся чистовой PDF или иной явно согласованный формат.

---

## 4. Два равноправных пути передачи материалов

**Путь A — напрямую в Google Drive:**
- владелец создаёт папку объекта/выезда, загружает материалы
- потом в Telegram говорит голосом или текстом: что за папка, объект, дата, что увидел, замечания, нужен акт или разбор
- оркестр находит папку, берёт материалы, не просит повторно загрузить, использует пояснение как ТЗ

**Путь B — через Telegram:**
- владелец скидывает фото/файлы в topic_5, поясняет голосом или текстом
- оркестр агрегирует файлы в текущий сбор, НЕ делает отдельную задачу на каждое фото, НЕ делает отдельный акт на каждое фото
- связывает пояснение с последними файлами
- при необходимости копирует материалы в активную Drive-папку
- если активная папка не задана — задаёт конкретный вопрос

---

## 5. ActiveTechnadzorFolder — поля

```
chat_id
topic_id          = 5
object_name
visit_date
drive_folder_url
drive_folder_id
folder_name
client_facing     flag
mode_hint
active_since
last_update
owner_instructions
status
```

Пока ActiveTechnadzorFolder активна:
- все следующие фото, документы, голосовые пояснения, текстовые замечания относятся к ней
- команды "сделай разбор / акт / документ" работают по ней

---

## 6. Команды управления активной папкой

Оркестр понимает:
- открыть папку / работаем по этой папке / это текущий объект / это текущий выезд
- показать активную папку
- сменить папку / закрыть сбор / очистить буфер текущей папки
- сделать разбор / сделать акт / сделать документ
- добавить эти фото к замечанию
- это не включать в акт / это включить в акт
- это замечание заказчика / подрядчика / мои замечания как технадзора

Если активная папка не задана и пришли материалы:
- есть последняя папка → "Отнести эти материалы к текущей папке '...'?"
- нет папки → "К какой папке/объекту отнести эти материалы?"

---

## 7. Режим COLLECTING_VISIT_MATERIALS

До команды "сделай разбор/акт/документ" оркестр в режиме COLLECTING_VISIT_MATERIALS:
- принимает фото, документы, видео, голосовые пояснения, текстовые замечания
- связывает замечания с файлами
- НЕ создаёт финальный документ без команды владельца

Правильные короткие ответы в режиме накопления:
- "Принял, добавил 3 фото к замечанию 'опорные узлы'"
- "Принял, эти 5 фото связал с разделом 'сварные соединения'"
- "Запомнил: это фото не включать в акт"
- "Активная папка: ..."
- "Принял пояснение и связал его с последними фото"

Запрещено:
- делать акт/задачу/ответ на каждое фото
- отправлять 10 отчётов на 10 фото
- терять голосовые пояснения или связь "фото → замечание"
- смешивать разные папки
- спрашивать "что строим?"
- просить повторно файлы, если они уже есть на Drive или в Telegram

---

## 8. VisitMaterial — поля

```
material_id
source             TELEGRAM / DRIVE
file_type          PHOTO / VIDEO / PDF / DOCX / XLSX / TEXT / VOICE / OTHER
file_name
drive_url
telegram_message_id
added_at
owner_comment
group_label
include_in_report  true/false
include_in_act     true/false
defect_hint
section_hint
status
```

Пример 1: владелец скинул фото 1–3, сказал "это опорные узлы, плохо выполнена подливка"
→ group=опорные узлы, defect_hint=плохая подливка, files=фото 1–3

Пример 2: владелец скинул фото 4–7, написал "это сварные швы, надо проверить качество"
→ group=сварные соединения, defect_hint=проверить качество, files=фото 4–7

Если замечание пришло после нескольких фото → связать с последней пачкой.
Если замечания между пачками → разделить материалы на группы по порядку.

---

## 9. VisitPackage — поля

```
active_folder
object_name
visit_date
previous_acts
photos
videos
documents
owner_instructions
client_comments
contractor_comments
material_groups
excluded_materials
requested_output
```

Схема после сборки:
```
VisitPackage → ObservationCard → DefectCard → grouped sections → один результат
```

---

## 10. ObservationCard — поля и роли источника

Поля: источник, автор, роль автора, тип материала, объект, дата, что утверждается, к каким файлам относится, подтверждено/нет, есть ли противоречие, нужен ли вопрос владельцу.

Роли источника: OWNER / CLIENT / CONTRACTOR / DOCUMENT / PHOTO / PREVIOUS_ACT / UNKNOWN

---

## 11. DefectCard — поля

```
фото №, имя файла, источник, узел/место, что видно, дефект/замечание,
почему плохо, возможные последствия, что исправить, что проверить на объекте,
нормативная отсылка, статус нормы, статус замечания, источник подтверждения,
вопрос владельцу (если нужен)
```

Иерархия источников:
- Голос/текст владельца = техническое ТЗ
- Фото = визуальное подтверждение
- Предыдущий акт = история объекта
- Сообщение заказчика = заявление заказчика (не доказанный факт)
- Сообщение подрядчика = заявление подрядчика (не доказанный факт)
- Проект/исполнительная документация = основание для проверки

Запрещено писать "устранено" только со слов заказчика или подрядчика.

---

## 12. Противоречия

- Владелец сказал одно, фото показывает другое → задать уточнение
- Подрядчик пишет "устранено", фото не подтверждает → "устранение по фото не подтверждено"
- Предыдущий акт фиксирует дефект, текущих фото по узлу нет → "не проверялось на текущем выезде"
- Заказчик сообщает факт без материалов → "по информации заказчика, требуется проверка"
- Подрядчик заявляет о выполнении работ → "по информации подрядчика, требуется фотофиксация и проверка на объекте"

---

## 13. Статусы замечаний

- новое замечание
- подтверждено по фото
- частично видно по фото
- устранено
- устранено частично
- не устранено
- требует доведения
- не проверялось на текущем выезде
- требует уточнения

---

## 14. Нормативная логика

- Найден документ и пункт → указать оба
- Найден только документ → указать без пункта
- Ничего не найдено → "норма не подтверждена"

Запрещено выдумывать пункты СП/ГОСТ.

Если дефект технически очевиден, норма не найдена: описать замечание, последствия, рекомендации, в нормативе указать "норма не подтверждена".

---

## 15. Группировка дефектов

Группировать по смыслу, не по порядку фото.

Базовые разделы:
- опорные узлы
- сварные соединения
- антикоррозионная защита
- основание и водоотведение
- крепления и узлы покрытия
- связи / укосины / элементы жёсткости
- бетонные и железобетонные конструкции
- кровля / фасад / ограждающие конструкции
- прочие замечания

Секции адаптируются через профиль объекта — не хардкодятся под ангар.

---

## 16. Пачки фото

- Не делать отдельный акт/ответ на каждое фото
- Один выезд = один разбор или один документ
- 61 фото = материалы одного выезда ≠ 61 акт
- Фото — приложения/доказательства внутри одного результата

Batch = организация очереди и группировка материалов внутри оркестра.
Batch НЕ означает внешний Vision.
Batch НЕ означает один API request с несколькими фото.
Vision — optional и только после явного разрешения владельца (EXTERNAL_PHOTO_ANALYSIS_ALLOWED=true).

---

## 17. Прогресс при длинной обработке

Запрещено молчать до таймаута.

Примеры:
- "Принял. Нашёл активную папку, материалы и предыдущие акты. Начинаю технадзорный разбор"
- "Обработано 20 из 61 фото"

---

## 18. Предыдущие акты и история объекта

Если акты есть:
- новый документ не пишется с нуля
- учитываются прошлые замечания со статусами
- должен быть раздел "Связь с предыдущими актами"
- фиксируется: что было ранее, что проверяется сейчас, что устранено/не устранено/новое

Если PDF предыдущего акта не распарсился: не выдумывать, писать "предыдущий акт найден, содержание требует ручной сверки".

Если актов нет: создать первичную историю объекта.

---

## 19. Формат результата

- Только разбор → чистый русский текст, без лишних файлов
- Документ → формат по команде владельца (current_supported: PDF / DOCX / XLSX / текст в Telegram)
- Акт → один акт по выезду, не по каждому фото
- Документ для заказчика → только чистовой русский, без task_id, /root, JSON, debug, английских названий

---

## 20. Возможные итоговые форматы

current_supported: PDF, DOCX/Word, XLSX, текстовый разбор в Telegram, таблица/реестр замечаний, приложение к акту.
future_optional: Google Docs (не реализован в текущем коде — не указывать как доступный).

Главное: формат по задаче и назначению документа. Один жёсткий формат не хардкодить.

---

## 21. Имена клиентских файлов

Клиентские и пользовательские файлы называются по-русски.

Правильно:
- `Акт_осмотра_ангар_Киевское_шоссе_04_05_2026.pdf`
- `Технический_разбор_ангар_Киевское_шоссе_04_05_2026.pdf`
- `Реестр_замечаний_ангар_Киевское_шоссе_04_05_2026.xlsx`
- `Черновик_акта_ангар_Киевское_шоссе_04_05_2026.docx`

Запрещено в клиентском имени: task_id, uuid, smoke, tmp, runtime, debug, английские технические названия.

---

## 22. Язык вывода

Всё, что видит владелец или заказчик — русский язык:
Telegram-ответы, акты, разборы, имена клиентских файлов, таблицы, рекомендации, описания дефектов, подписи к фото, выводы.

Английский — только внутри кода: функции, классы, enum, маркеры, переменные, служебные структуры.

---

## 23. Роль голоса владельца

Голос владельца = полноценное техническое ТЗ.

Извлекать: объект, папку, дату, что обнаружено, что включить/не включать, нужен акт или разбор, куда класть результат, какие фото использовать, что проверить по нормам.

Если голос противоречит фото или документам: уточнить у владельца, не выбирать молча.

---

## 24. Тексты заказчика и подрядчика

Учитывать как заявления, не как доказанный факт.

Правильные формулировки:
- "по информации заказчика"
- "по информации подрядчика"
- "подтверждение по фото отсутствует"
- "требуется проверка на объекте"
- "требуется фотофиксация результата"

Запрещено писать "устранено" только со слов подрядчика.

---

## 25. Если активная папка не задана

Спросить: "К какой папке/объекту отнести эти материалы?"
Если есть последний активный объект: "Отнести эти материалы к текущей папке '...'?"

---

## 26. Смена объекта или папки

Если владелец говорит "работаем по новой папке / другой объект / другой выезд":
- закрыть/приостановить текущий сбор
- открыть новую ActiveTechnadzorFolder
- не смешивать материалы разных объектов
- не переносить старые материалы без команды

---

## 27. Структура текстового технадзорного разбора

- объект
- дата / выезд
- основание анализа
- какие материалы использованы
- режим осмотра
- замечания по фото
- последствия
- рекомендации
- нормы
- что требует уточнения
- итоговый вывод
- нужен ли акт

---

## 28. Структура акта осмотра

АКТ ОСМОТРА ОБЪЕКТА №, дата, место, объект, метод обследования, технический специалист, основание осмотра, связь с предыдущими актами (если есть), общие сведения, установлено по факту осмотра, разделы 2.1/2.2/2.3, нормативные отсылки, фотоматериалы, рекомендации, последствия, таблица замечаний, заключение, подпись.

---

## 29. Таблица замечаний

Первичный осмотр:
`№ | фото | узел/место | нарушение | последствия | что сделать | норматив | статус`

Повторный осмотр:
`№ | замечание | что было по пред. акту | текущее состояние | статус | фото тек. осмотра | норматив | что сделать`

---

## 30. Первичный осмотр

- создать первичную историю объекта
- зафиксировать все дефекты, дать рекомендации, указать последствия
- зафиксировать открытые замечания
- сохранить как основу для следующих осмотров

---

## 31. Повторный / следующий осмотр

- не писать документ с нуля
- продолжать историю
- сравнивать старые замечания с текущими материалами
- давать статус каждому замечанию
- добавлять новые замечания
- формировать вывод по динамике устранения

---

## 32. Расширяемость через профили

Ядро одно:
```
InputMaterials → VisitPackage → ObservationCard → DefectCard → GroupedDefects → TextReport/Act/Document
```

Меняются только профили: металлокаркас / бетон / кровля / фасад / инженерные сети / электрика / отделка.

Профиль задаёт: секции, нормы, типовые дефекты, структуру документа.
Профиль может задавать optional vision prompt, но Vision запускается только при EXTERNAL_PHOTO_ANALYSIS_ALLOWED=true и явном разрешении владельца.

---

## 33. Guard внешнего анализа фото

EXTERNAL_PHOTO_ANALYSIS_ALLOWED = False по умолчанию.

Без явного разрешения владельца запрещено:
- OpenRouter Vision
- Google Gemini Vision
- OpenAI Vision
- любой внешний Vision API
- отправка оригиналов фото наружу
- отправка сжатых копий фото наружу
- model fallback по Vision
- смена Vision-модели без команды владельца

Если фото пришли без разрешения на внешний Vision:
- сохранить и привязать материалы к активной папке
- использовать голос/текст владельца
- использовать предыдущие акты
- использовать документы
- если данных не хватает — задать конкретный вопрос
- фото наружу не отправлять

---

## 33a. Drive canonical layer

Любая запись в Drive — только через канонический topic-aware слой:

```
core/topic_drive_oauth.py
upload_file_to_topic
AI_ORCHESTRA/chat_<chat_id>/topic_<topic_id>/
```

Запрещено:
- flat folders (без chat_id / topic_id)
- upload в корень AI_ORCHESTRA
- служебные файлы в client-facing папку
- JSON / logs / debug / manifests / runtime в client-facing папку

---

## 34. Итоговая рабочая схема

```
Владелец → создаёт/выбирает Drive-папку
→ в Telegram: "работаем по этой папке, объект ..., все материалы сюда"
→ Оркестр: открывает ActiveTechnadzorFolder
→ Владелец: загружает фото/документы через Drive или Telegram, поясняет голосом/текстом
→ Оркестр: копит VisitMaterial, связывает пояснения с файлами, НЕ делает документы на каждое фото
→ Владелец: "сделай разбор" / "сделай акт" / "сделай документ"
→ Оркестр: собирает VisitPackage → анализирует → выдаёт один общий результат
```

---

## 34. Главный принцип

```
Google Drive папка = контейнер работы
Telegram           = пояснение и управление
Фото/файлы         = материалы
Голос/текст владельца = техническое ТЗ и привязка замечаний
Оркестр            = связывает файлы с замечаниями и объектом
Финал              = один разбор или один документ по всей задаче
```

---

## 35. Разрешение конфликта §20 vs Vision resize

**§20 TECHNADZOR_DOMAIN_LOGIC_CANON_V1:** "Фото клиента запрещено: сжимать"

**P6H_VISION_RESIZE_V1** создаёт уменьшенную копию фото перед отправкой во внешний Vision API.

**Разрешение:**

Правило §20 означает: нельзя сжимать и сохранять оригинал клиентского фото в изменённом виде.

Resize перед Vision **допустим** при одновременном выполнении всех условий:
1. `EXTERNAL_PHOTO_ANALYSIS_ALLOWED = True` — владелец явно разрешил внешний Vision
2. Resize создаёт **временную копию** в `/tmp` — не на Drive, не в data/
3. Временная копия **удаляется сразу** после Vision-вызова (try/unlink)
4. Оригинал фото **не изменяется** и **не удаляется**
5. Сжатая копия **нигде не сохраняется** постоянно

Если хоть одно условие нарушено — resize запрещён.

Если `EXTERNAL_PHOTO_ANALYSIS_ALLOWED = False` (по умолчанию) — resize не вызывается вообще, §20 не нарушается.


## CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md

# TOPIC_2 STROYKA — CANONICAL ESTIMATE CONTRACT
Версия: v1 | Дата: 2026-05-07 | Статус: CANON_LOCK

## §1. Шаблоны (Drive folder `19Z3acDgPub4nV55mad5mb8ju63FsqoG9`)

| Имя | file_id |
|---|---|
| `М-80.xlsx` | `1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp` |
| `М-110.xlsx` | `1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo` |
| `Ареал Нева.xlsx` | `1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm` |
| `фундамент_Склад2.xlsx` | `1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp` |
| `крыша и перекр.xlsx` | `16YecwnJ9umnVprFu9V77UCV6cPrYbNh3` |

**DEPRECATED** (score=-9999): `ВОР_кирпичная_кладка_ИСПРАВЛЕНО.xlsx`

### Cache rule
`data/templates/estimate/cache/` — runtime mirror. Drive — SSOT.
- если кэш валиден → use cache
- если кэш отсутствует/повреждён → download from Drive по file_id, save в кэш
- если Drive недоступен и кэш валиден → use cache + marker `TOPIC2_TEMPLATE_CACHE_USED`
- если оба недоступны → FAILED `TOPIC2_TEMPLATE_UNAVAILABLE`

## §2. Template scoring rules
- ангар/склад/фундамент → `фундамент_Склад2.xlsx`
- кровля → `крыша и перекр.xlsx`
- каркас + площадь >100 м² → `М-110.xlsx`
- каркас + ≤100 м² → `М-80.xlsx`
- газобетон/кирпич/керамоблок/монолит/арболит → `Ареал Нева.xlsx`
- брус → `Ареал Нева.xlsx`
- default → `Ареал Нева.xlsx`

## §3. Sheet selection
- каркас → лист с «каркас»
- газобетон/кирпич/керамоблок/монолит → лист с «газобетон»
- кровля → лист с «кров» или «перекр»
- ангар/склад/фундамент → лист с «смет», «фундамент» или «склад»
- fallback → первый лист + marker `TOPIC2_TEMPLATE_SHEET_FALLBACK`

## §4. AREAL_CALC sheet — 15 колонок
1. №
2. Раздел
3. Наименование
4. Ед изм
5. Кол-во
6. Цена работ
7. Стоимость работ
8. Цена материалов
9. Стоимость материалов
10. Всего
11. Источник цены
12. Поставщик
13. URL
14. checked_at
15. Примечание

### Формулы
- Стоимость работ = Кол-во × Цена работ
- Стоимость материалов = Кол-во × Цена материалов
- Всего = Стоимость работ + Стоимость материалов
- Final totals только через SUM

### Forbidden XLSX
8-колоночный старый формат: Раздел/Позиция/Ед/Кол/Материал/Работа/Итого/Примечание. Если меньше 15 колонок → state не AC, error `TOPIC2_XLSX_CANON_COLUMNS_MISSING_V1`.

## §5. 11 секций сметы
1. Фундамент
2. Стены / каркас
3. Перекрытия
4. Кровля
5. Окна и двери
6. Внешняя отделка
7. Внутренняя отделка
8. Инженерные коммуникации
9. Логистика
10. Накладные расходы
11. НДС и итоги

### Под ключ → интерьер по комнатам
- **санузел**: гидроизоляция, плитка пол/стены, сантехкомплект
- **кухня**: фартук-плитка, усил.розетки, чистовой пол
- **спальня/гостиная/кабинет**: ламинат+подложка, плинтус, розетки/выключатели, световые точки
- **«тёплый пол / ИК»** → ИК-полы строки
- **«имитация бруса»** → имитация бруса стены
- **клик-фальц/сайдинг/штукатурка/фасад** → отдельные строки материал+работа
- **окна Rehau/профиль/количество** → окна материал + установка

## §6. Price source statuses
- LIVE_CONFIRMED
- PARTIAL
- UNVERIFIED
- TEMPLATE_ONLY
- MANUAL
- PRICE_MISSING

«Средние цены из интернета» → live enrichment через Perplexity, не template median. Без `TOPIC2_PRICE_CHOICE_CONFIRMED` нельзя выводить «median».

### Required price markers
`TOPIC2_PRICE_ENRICHMENT_STARTED` · `TOPIC2_PRICE_ENRICHMENT_DONE` · `TOPIC2_PRICE_SOURCE_FOUND` · `TOPIC2_PRICE_SOURCE_MISSING` · `TOPIC2_PRICE_CHOICE_CONFIRMED:<choice>`

## §7. PDF
- `core/pdf_cyrillic.py` — `create_pdf_with_cyrillic` + `validate_cyrillic_pdf`
- Должен содержать: object, material, template, sheet, pricing mode, logistics, rows summary, totals, VAT, links, clean Cyrillic
- Forbidden: broken Cyrillic, /root paths, empty summary, mismatch с XLSX
- Markers: `TOPIC2_PDF_CREATED` · `TOPIC2_PDF_CYRILLIC_OK` · `TOPIC2_PDF_TOTALS_MATCH_XLSX`

## §8. Drive output
- AI_ORCHESTRA: `13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB`
- topic_2 folder: `1F4qRGBCqjPZIjvkREwiPrQOOrfuRXVjA`
- ESTIMATES: `1fqw-fuUoM0HxHkgL_ZRxE3KFboDvwxsm`
- MANIFEST — внутренний, не показывать пользователю
- Markers: `TOPIC2_DRIVE_UPLOAD_XLSX_OK` · `TOPIC2_DRIVE_UPLOAD_PDF_OK` · `TOPIC2_DRIVE_TOPIC_FOLDER_OK` · `TOPIC2_DRIVE_LINKS_SAVED`

## §9. Final user response (Telegram format)
```
✅ Смета готова

Объект: ...   Материал: ...   Площадь: ...   Этажность: ...   Регион: ...
Шаблон: ...   Лист: ...   Цены: ...   Логистика: ...

Итого:
  Материалы: ...
  Работы: ...
  Логистика: ...
  Накладные: ...
  Без НДС: ...
  НДС: ...
  С НДС: ...

Excel: <link>
PDF: <link>

Подтверди или пришли правки
```

### Forbidden in final response
- «Эталон: М-80.xlsx» как блок
- «Выбор цены: median» без CONFIRMED
- MANIFEST
- Engine
- /root, /tmp
- REVISION_CONTEXT
- raw JSON
- старая 6-секционная сводка

## §10. DONE contract — markers перед AC
- `TOPIC2_TEMPLATE_SELECTED:<name>`
- `TOPIC2_TEMPLATE_FILE_ID:<id>`
- `TOPIC2_TEMPLATE_CACHE_USED` или `TOPIC2_TEMPLATE_DRIVE_DOWNLOADED`
- `TOPIC2_TEMPLATE_SHEET_SELECTED:<sheet>`
- `TOPIC2_XLSX_TEMPLATE_COPY_OK`
- `TOPIC2_XLSX_ROWS_WRITTEN:<n>`
- `TOPIC2_XLSX_FORMULAS_OK`
- `TOPIC2_XLSX_CANON_COLUMNS_OK`
- `TOPIC2_PDF_CREATED`
- `TOPIC2_PDF_CYRILLIC_OK`
- `TOPIC2_DRIVE_UPLOAD_XLSX_OK`
- `TOPIC2_DRIVE_UPLOAD_PDF_OK`
- `TOPIC2_TELEGRAM_DELIVERED`

DONE — только после явного «да» от пользователя.

## §11. Canonical route priority
Для topic_id=2 estimate intent:
1. cancel/status/meta guards
2. file/photo context extraction
3. canonical engine (`topic2_estimate_final_close_v2` / stroyka canonical с 15-col output)
4. **старый template summary route — блокировать**
5. generic LLM fallback запрещён для финала сметы

Если старый route произвёл результат → marker `TOPIC2_OLD_TEMPLATE_ROUTE_BLOCKED_V1`, переотправка через canonical (или FAILED `TOPIC2_CANONICAL_ENGINE_FAILED_AFTER_OLD_ROUTE_BLOCK_V1`).

### Old output blocker — паттерны
- «Эталон:»
- «Лист эталона:»
- «Выбор цены:»
- «Каркас под ключ»
- «Разделы:»
- «НДС 20%»
- «Предварительная смета готова» если нет canonical markers


## CANON_FINAL/TOPIC_500_UNIVERSAL_SEARCH_CANON.md

# TOPIC_500 — UNIVERSAL ADAPTIVE INTERNET SEARCH CANON
Версия: v1 | Дата: 2026-05-07 | Статус: CANON_LOCK

## §1. Core rule
topic_500 — это универсальный адаптивный интернет-поиск, не «цифровой снабженец». Procurement-логика (Avito/Ozon/TCO/seller risk) — ОДИН из режимов, не дефолт.

## §2. 16 поддерживаемых типов задач
1. Факт-поиск
2. Source verification
3. Price/product/marketplace search (procurement)
4. Service/contractor search
5. Legal/normative — ГОСТ/СП/СНиП
6. Construction technology
7. Technical documentation
8. Software/app/download links
9. News/recent changes
10. Company/person/organization lookup
11. Forums (4PDA / appstorrent / apkpure / trashbox)
12. Travel/local/maps
13. Comparison
14. Troubleshooting
15. Image/reference/example
16. General web answer with sources

## §3. Search flow
1. Read user request
2. Detect search intent
3. Detect domain
4. Classify mode (procurement / factual / normative / technical / download / local / news / comparison / open-research)
5. Choose strategy ПО intent (NOT before)
6. Search web with required breadth
7. Verify sources
8. Deduplicate
9. Return по формату intent

## §4. Procurement mode — триггеры
buy / купить / найти где купить · price / цена / стоимость · supplier / поставщик · material / стройматериал · product / товар · marketplace · Avito / Ozon / Wildberries / Drom / Auto.ru · contractor / услуга · spare part / запчасть · OEM / SKU / RAL / thickness / dimensions

### Procurement output (только в этом режиме)
- item · region · offers · price · seller/supplier · url · checked_at · source_status · delivery/pickup если найдено · risk если уместно · TCO если уместно · recommendation

## §5. Output формат для остальных режимов

### Factual
- ответ
- sources
- что подтверждено
- что неуверенно
- date / checked_at если важна свежесть

### Normative
- document/norm name
- clause если найдена
- applicability
- source link
- checked_at
- краткий вывод

### Download/App
- ОДНА best ссылка если просили одну
- platform compatibility
- source safety status
- почему именно эта
- НЕ list если не просили list

### Technical
- cause / fix / command / version
- official docs preferred
- forum sources разрешены когда явно просили (4PDA / appstorrent / apkpure / trashbox)
- cite source / checked_at

### News/Recent
- latest confirmed facts
- timeline если нужен
- source links
- checked_at
- НЕ старый кэш без свежего поиска

### Service/Local
- relevant providers/locations
- region
- contact/link если найдено
- rating/reviews если найдено
- риски если уместно

## §6. Adaptive result count
- «дай одну ссылку» → ОДИН best
- «сравни» → достаточно для comparison
- «исследование» → структурированное summary с selected sources
- procurement → 3-10 offers по доступному качеству
- exact factual → концентрированный ответ + supporting sources

## §7. Forbidden
- fake links
- invented prices
- invented source names
- supplier поля кроме procurement mode
- marketplace-only кроме marketplace mode
- generic «посмотрите в интернете»
- answer без source когда нужна freshness/verification
- смешивание topic_2 estimate output в topic_500
- смешивание topic_210 project output в topic_500
- смешивание topic_5 technadzor output в topic_500

## §8. Cross-topic usage (search как инструмент)
- topic_2 STROYKA — search для prices/materials/suppliers/logistics/норм
- topic_210 PROJECTING — search для норм/technical references/standards
- topic_5 TECHNADZOR — search для ГОСТ/СП/СНиП когда локального канона не хватает
- topic_500 — выделенный универсальный

## §9. Final rule
topic_500 = universal adaptive internet search.
Supplier / price / TCO logic — один из режимов.


================================================================================
# 5. PER_TOPIC
================================================================================

## TOPIC_0_COMMON

STATUS: UNKNOWN
ACTIVE: 0  FAILED_24H: 0
DIRECTIONS_BOUND: Общий

### LAST_FAILED (5)
- 66b9f841 | 2026-05-02 00:23:59 | INVALID_RESULT_GATE
    history: reply_sent:invalid_result
    history: state:FAILED
    history: state:IN_PROGRESS
- 5c19256b | 2026-05-02 00:23:48 | INVALID_RESULT_GATE
    history: reply_sent:invalid_result
    history: state:FAILED
    history: result:Поставщик | Площадка | Тип | Город | Цена | Наличие | Доставка | TCO | Риски | Статус
I canno
- 0de22d01 | 2026-05-01 22:35:29 | PROJECT_LINKS_MISSING
    history: reply_sent:ff10_project_links_missing
    history: FULLFIX_10_PROJECT_LINKS_MISSING
    history: created:NEW
- d65dd41b | 2026-05-01 21:48:52 | CONFIRMATION_TIMEOUT
- 890ac70c | 2026-05-01 21:48:49 | CONFIRMATION_TIMEOUT

### TOPIC_FILE_INLINE
```
# topic_0 COMMON

GENERATED_AT: 2026-05-08T18:45:02.524383+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 0
ROLE: Общий
DIRECTIONS_BOUND: none
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- ARCHIVED: 289
- CANCELLED: 643
- DONE: 207
- FAILED: 2705

## LATEST_FAILED
- 66b9f841 | INVALID_RESULT_GATE
- 5c19256b | INVALID_RESULT_GATE
- 0de22d01 | PROJECT_LINKS_MISSING
- d65dd41b | CONFIRMATION_TIMEOUT
- 890ac70c | CONFIRMATION_TIMEOUT

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- (none)

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 0
chats: 0

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days


```

## TOPIC_2_STROYKA

STATUS: INSTALLED_NOT_VERIFIED
ACTIVE: 1  FAILED_24H: 1
DIRECTIONS_BOUND: Сметы

### LAST_FAILED (5)
- 1d2b38c4 | 2026-05-08 21:14:03 | STALE_TIMEOUT
    history: reply_sent:stale_failed
    history: state:FAILED
    history: reply_sent:drive_file_no_intent_offer
- a7b2879e | 2026-05-07 16:34:34 | STALE_TIMEOUT
    history: reply_sent:stale_failed
    history: state:FAILED
    history: clarified:
- 893436d4 | 2026-05-06 21:05:02 | INVALID_PUBLIC_RESULT
    history: PATCH_TOPIC2_FRESH_ESTIMATE_ROUTE_GUARD_V1:BYPASS_P6E67_PARENT_LOOKUP
    history: TOPIC2_DONE_CONTRACT_OK
    history: TOPIC2_MESSAGE_THREAD_ID_OK
- f43100b3 | 2026-05-06 20:56:47 | TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_ERR:maximum recursion depth exceeded
    history: TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_ERR:maximum recursion depth exceeded
    history: P3_TOPIC2_CLARIFICATION
    history: TOPIC2_PRICE_CHOICE_CONFIRMED:median
- c6b40dfc | 2026-05-06 20:33:30 | STROYKA_QG_FAILED:XLSX_VALIDATE_ERROR:maximum recursion depth exceeded
    history: PATCH_TOPIC2_FRESH_ESTIMATE_ROUTE_GUARD_V1:CANON_FALLBACK:BYPASS_P6E67_PARENT_LOOKUP
    history: TOPIC2_PRICE_CHOICE_CONFIRMED:median
    history: PRICE_BIND_POISON_PARENT_GUARD_V2_BLOCKED_V4:LATEST_PRICE_MENU_FALLBACK

### KEY_ENGINE_CODE (head 250 lines each)
#### core/sample_template_engine.py
```python
# === FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE ===
import os
import re
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List, Tuple

ENGINE = "FULLFIX_13A_SAMPLE_FILE_INTENT_AND_TEMPLATE_ESTIMATE"
BASE = Path("/root/.areal-neva-core")
TEMPLATE_ROOT = BASE / "data" / "templates"
ESTIMATE_TEMPLATE_DIR = TEMPLATE_ROOT / "estimate"
PROJECT_TEMPLATE_DIR = TEMPLATE_ROOT / "project"

SAMPLE_WORDS = (
    "образец", "шаблон", "пример", "как образец", "как шаблон",
    "используй это", "возьми это", "сохрани это", "запомни это",
    "по этому", "по нему", "по ней", "в таком формате", "такой формат"
)

ESTIMATE_WORDS = (
    "смет", "кс-2", "кс2", "ведомост", "спецификац", "расцен", "цена",
    "стоимост", "позици", "материал", "работ", "руб", "xlsx", "excel", "таблиц"
)

PROJECT_WORDS = (
    "проект", "кж", "кд", "ар", "км", "чертеж", "чертёж", "плит", "фундамент",
    "кровл", "стропил", "архитект", "dxf", "dwg", "pdf"
)

FILE_EXT_ESTIMATE = (".xlsx", ".xls", ".csv")
FILE_EXT_PROJECT = (".pdf", ".dxf", ".dwg", ".docx")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_text(v: Any) -> str:
    return str(v or "").strip()


def _json_loads_maybe(v: Any) -> Dict[str, Any]:
    if isinstance(v, dict):
        return v
    s = _safe_text(v)
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}


def _low(v: Any) -> str:
    return _safe_text(v).lower().replace("ё", "е")


def _task_history_insert(conn, task_id: str, action: str) -> None:
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(task_history)").fetchall()]
        if "action" in cols:
            conn.execute(
                "INSERT INTO task_history (task_id,action,created_at) VALUES (?,?,datetime('now'))",
                (task_id, action),
            )
        elif "event" in cols:
            conn.execute(
                "INSERT INTO task_history (task_id,event,created_at) VALUES (?,?,datetime('now'))",
                (task_id, action),
            )
        conn.commit()
    except Exception:
        pass



def _send_reply(chat_id: str, text: str, reply_to_message_id: Optional[int] = None, topic_id: int = 0) -> Optional[int]:  # TOPIC2_REPLY_THREAD_FIX_V1
    try:
        from core.reply_sender import send_reply_ex
        kwargs = {
            "chat_id": str(chat_id),
            "text": text,
            "reply_to_message_id": reply_to_message_id,
        }
        if int(topic_id or 0) > 0:
            kwargs["message_thread_id"] = int(topic_id or 0)  # TOPIC2_REPLY_THREAD_FIX_V1
        res = send_reply_ex(**kwargs)
        if isinstance(res, dict):
            return res.get("bot_message_id")
    except Exception:
        return None
    return None

def _update_task(conn, task_id: str, state: str, result: str = "", error_message: str = "", bot_message_id: Optional[int] = None) -> None:
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)").fetchall()]
        sets = ["state=?", "result=?", "error_message=?", "updated_at=datetime('now')"]
        vals: List[Any] = [state, result, error_message]
        if bot_message_id and "bot_message_id" in cols:
            sets.append("bot_message_id=?")
            vals.append(int(bot_message_id))
        vals.append(task_id)
        conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
        conn.commit()
    except Exception:
        pass


def detect_sample_template_intent(raw_input: Any, input_type: str = "") -> bool:
    payload = _json_loads_maybe(raw_input)
    text = " ".join([
        _safe_text(raw_input),
        _safe_text(payload.get("caption")),
        _safe_text(payload.get("file_name")),
    ])
    low = _low(text)
    if not low:
        return False
    has_sample = any(w in low for w in SAMPLE_WORDS)
    if not has_sample:
        return False
    has_domain = any(w in low for w in ESTIMATE_WORDS + PROJECT_WORDS)
    if has_domain:
        return True
    return any(x in low for x in ("файл", "это", "таблица", "документ"))


def detect_estimate_intent(raw_input: Any) -> bool:
    low = _low(raw_input)
    if not low:
        return False
    if any(w in low for w in ("проект", "фундамент", "плит", "кровл", "стропил", "чертеж", "чертёж")):
        return False
    return any(w in low for w in ("смет", "посчитай", "расчет", "расчёт", "профлист", "монтаж", "цена", "руб", "м2", "м²", "шт", "ведомость"))


def _template_kind_from_text_and_file(text: str, file_name: str) -> str:
    low = _low(text + " " + file_name)
    ext = Path(file_name).suffix.lower()
    if any(w in low for w in ESTIMATE_WORDS) or ext in FILE_EXT_ESTIMATE:
        return "estimate"
    if any(w in low for w in PROJECT_WORDS) or ext in FILE_EXT_PROJECT:
        return "project"
    return "estimate"


def _parse_file_payload(row_raw: Any) -> Dict[str, Any]:
    payload = _json_loads_maybe(row_raw)
    return {
        "file_id": _safe_text(payload.get("file_id")),
        "file_name": _safe_text(payload.get("file_name")),
        "mime_type": _safe_text(payload.get("mime_type")),
        "caption": _safe_text(payload.get("caption")),
        "source": _safe_text(payload.get("source")),
        "telegram_message_id": payload.get("telegram_message_id"),
        "raw_payload": payload,
    }


def _find_latest_related_file(conn, chat_id: str, topic_id: int, current_task_id: str = "", prefer_estimate: bool = True) -> Optional[Dict[str, Any]]:
    rows = []
    try:
        rows = conn.execute(
            """
            SELECT id,chat_id,COALESCE(topic_id,0) AS topic_id,input_type,raw_input,result,created_at,updated_at
            FROM tasks
            WHERE chat_id=?
              AND COALESCE(topic_id,0)=?
              AND input_type='drive_file'
            ORDER BY rowid DESC
            LIMIT 50
            """,
            (str(chat_id), int(topic_id or 0)),
        ).fetchall()
    except Exception:
        rows = []

    if not rows:
        try:
            rows = conn.execute(
                """
                SELECT id,chat_id,COALESCE(topic_id,0) AS topic_id,input_type,raw_input,result,created_at,updated_at
                FROM tasks
                WHERE chat_id=?
                  AND input_type='drive_file'
                ORDER BY rowid DESC
                LIMIT 50
                """,
                (str(chat_id),),
            ).fetchall()
        except Exception:
            rows = []

    best = None
    best_score = -1

    for r in rows:
        raw = r["raw_input"] if hasattr(r, "keys") else r[4]
        payload = _parse_file_payload(raw)
        file_name = payload.get("file_name", "")
        low_name = _low(file_name)
        score = 0
        if any(low_name.endswith(ext) for ext in FILE_EXT_ESTIMATE):
            score += 80
        if any(k in low_name for k in ("smet", "смет", "vor", "кирп", "price", "cost", "ведом")):
            score += 40
        if prefer_estimate and any(low_name.endswith(ext) for ext in FILE_EXT_ESTIMATE):
            score += 30
        if "project_" in low_name or "кж_project" in low_name or "кд_project" in low_name:
            score -= 60
        if "smoke" in low_name:
            score -= 80
        if score > best_score:
            best_score = score
            best = {
                "task_id": r["id"] if hasattr(r, "keys") else r[0],
                "chat_id": r["chat_id"] if hasattr(r, "keys") else r[1],
                "topic_id": r["topic_id"] if hasattr(r, "keys") else r[2],
                "result": r["result"] if hasattr(r, "keys") else r[5],
                "created_at": r["created_at"] if hasattr(r, "keys") else r[6],
                "updated_at": r["updated_at"] if hasattr(r, "keys") else r[7],
                **payload,
                "score": score,
            }

    return best


def _template_paths(kind: str, chat_id: str, topic_id: int) -> Tuple[Path, Path]:
    base_dir = ESTIMATE_TEMPLATE_DIR if kind == "estimate" else PROJECT_TEMPLATE_DIR
    base_dir.mkdir(parents=True, exist_ok=True)
    safe_chat = re.sub(r"[^0-9A-Za-z_-]+", "_", str(chat_id))[:80]
    active = base_dir / f"ACTIVE__chat_{safe_chat}__topic_{int(topic_id or 0)}.json"
    snapshot = base_dir / f"TEMPLATE__chat_{safe_chat}__topic_{int(topic_id or 0)}__{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    return active, snapshot


def save_template_pointer(conn, chat_id: str, topic_id: int, task_id: str, raw_input: Any, input_type: str = "text") -> Tuple[bool, Dict[str, Any], str]:
    payload = _json_loads_maybe(raw_input)
    text = " ".join([_safe_text(raw_input), _safe_text(payload.get("caption"))])

    if input_type == "drive_file":
        file_meta = _parse_file_payload(raw_input)
        file_meta.update({"task_id": task_id, "chat_id": chat_id, "topic_id": topic_id})
    else:
        file_meta = _find_latest_related_file(conn, chat_id, topic_id, task_id, prefer_estimate=True)

    if not file_meta or not file_meta.get("file_id"):
```

#### core/stroyka_estimate_canon.py
```python
# === FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3 ===
from __future__ import annotations

import os
import re
import io
import json
import uuid
import time
import math
import sqlite3
import asyncio
import tempfile
import statistics
import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple

import requests
from dotenv import load_dotenv

BASE = Path("/root/.areal-neva-core")
ENV_PATH = BASE / ".env"
MEM_DB = BASE / "data/memory.db"
load_dotenv(str(ENV_PATH), override=True)

TOPIC_ID_STROYKA = 2
DRIVE_TEMPLATES_PARENT_ID = "19Z3acDgPub4nV55mad5mb8ju63FsqoG9"

DEPRECATED_TEMPLATE_NAMES = (
    "ВОР_кирпичная_кладка_ИСПРАВЛЕНО.xlsx",
)

CANON_TEMPLATE_FALLBACK = {
    "m80": {"title": "М-80.xlsx", "role": "full_house_estimate_template", "file_id": "1yt-RJsGRhO13zmPKNAn6bMuGrpXY7kWp", "source": "fallback_registry"},
    "m110": {"title": "М-110.xlsx", "role": "full_house_estimate_template", "file_id": "1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo", "source": "fallback_registry"},
    "roof": {"title": "крыша и перекр.xlsx", "role": "roof_and_floor_estimate_template", "file_id": "16YecwnJ9umnVprFu9V77UCV6cPrYbNh3", "source": "fallback_registry"},
    "foundation": {"title": "фундамент_Склад2.xlsx", "role": "foundation_estimate_template", "file_id": "1KuoSI4OI7gJoIBPVqBQGXtQnolXKMiDp", "source": "fallback_registry"},
    "areal": {"title": "Ареал Нева.xlsx", "role": "general_company_estimate_template", "file_id": "1DQw2qgMHtq2SqgJJP-93eIArpj1hnNNm", "source": "fallback_registry"},
}

ESTIMATE_WORDS = (
    "смет", "стоимость", "расчет", "расчёт", "посчитай", "коробк", "дом", "стройк",
    "фундамент", "кровл", "перекр", "ангар", "склад", "газобетон", "каркас", "монолит",
)

CONTINUATION_WORDS = (
    "да", "да сделай", "сделай", "где смета", "ну что", "вариант 1", "вариант 2",
    "первый", "второй", "подтверждаю", "ок", "окей", "цены актуальны", "адрес подтверждаю",
    "средняя", "минимальная", "максимальная", "ручная", "конкретная ссылка",
)

REVISION_WORDS = (
    "нет не так", "не так", "переделай", "исправь", "правки", "пересчитай", "измени", "уточни",
)

PROJECT_ONLY_WORDS = (
    "проект ар", "проект кж", "проект кд", "чертеж", "чертёж", "раздел ар", "раздел кж", "раздел кд",
)

EXCLUSIONS_DEFAULT = (
    "подготовка участка",
    "стройгородок",
    "бытовки",
    "отмостка",
    "дренаж",
    "ливневая канализация",
    "вывоз мусора",
    "наружные сети",
    "всё, что не указано явно",
)

PRICE_CHOICE_HELP = """Выбор цены:
- средняя / медианная
- минимальная
- максимальная
- конкретная ссылка
- ручная цена
- можно добавить наценку, скидку, запас или поправку по позиции, разделу или всей смете"""


def _s(v: Any) -> str:
    return "" if v is None else str(v).strip()


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _clean(text: str, limit: int = 12000) -> str:
    text = (text or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:limit]


def _now() -> str:
    return datetime.datetime.utcnow().isoformat()


def _row_get(row: Any, key: str, default: Any = "") -> Any:
    try:
        if hasattr(row, "keys") and key in row.keys():
            return row[key]
    except Exception:
        pass
    try:
        return row[key]
    except Exception:
        return getattr(row, key, default)


def _cols(conn: sqlite3.Connection, table: str) -> List[str]:
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except Exception:
        return []


def _update_task_safe(conn: sqlite3.Connection, task_id: str, **kwargs: Any) -> None:
    cols = _cols(conn, "tasks")
    parts, vals = [], []
    for k, v in kwargs.items():
        if k in cols:
            parts.append(f"{k}=?")
            vals.append(v)
    if "updated_at" in cols:
        parts.append("updated_at=datetime('now')")
    if not parts:
        return
    vals.append(task_id)
    conn.execute(f"UPDATE tasks SET {', '.join(parts)} WHERE id=?", vals)
    conn.commit()


def _history_safe(conn: sqlite3.Connection, task_id: str, action: str) -> None:
    try:
        conn.execute(
            "INSERT INTO task_history (task_id, action, created_at) VALUES (?, ?, datetime('now'))",
            (task_id, _clean(action, 1000)),
        )
        conn.commit()
    except Exception:
        pass


def _memory_save(chat_id: str, key: str, value: Dict[str, Any]) -> None:
    try:
        con = sqlite3.connect(str(MEM_DB))
        try:
            payload = json.dumps(value, ensure_ascii=False, indent=2)
            con.execute(
                "INSERT OR REPLACE INTO memory (id, chat_id, key, value, timestamp) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), str(chat_id), str(key), payload, _now()),
            )
            con.commit()
        finally:
            con.close()
    except Exception:
        pass


def _memory_latest(chat_id: str, key_prefix: str) -> Optional[Dict[str, Any]]:
    try:
        con = sqlite3.connect(str(MEM_DB))
        con.row_factory = sqlite3.Row
        try:
            row = con.execute(
                "SELECT key,value,timestamp FROM memory WHERE chat_id=? AND key LIKE ? ORDER BY timestamp DESC LIMIT 1",
                (str(chat_id), f"{key_prefix}%"),
            ).fetchone()
            if not row:
                return None
            data = json.loads(row["value"] or "{}")
            data["_memory_key"] = row["key"]
            data["_memory_timestamp"] = row["timestamp"]
            return data
        finally:
            con.close()
    except Exception:
        return None



# === FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_CONTEXT_BLEED_FIX ===
def _parse_iso_ts(value: Any) -> Optional[datetime.datetime]:
    txt = _s(value)
    if not txt:
        return None
    txt = txt.replace("Z", "+00:00")
    try:
        dt = datetime.datetime.fromisoformat(txt)
        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return dt
    except Exception:
        return None


def _age_seconds(value: Any) -> Optional[float]:
    dt = _parse_iso_ts(value)
    if not dt:
        return None
    return (datetime.datetime.utcnow() - dt).total_seconds()


def _pending_is_fresh(pending: Optional[Dict[str, Any]], max_seconds: int = 600) -> bool:
    if not pending:
        return False
    created = pending.get("created_at") or pending.get("_memory_timestamp")
    age = _age_seconds(created)
    return age is not None and 0 <= age <= max_seconds


def _is_bad_estimate_result(text: str) -> bool:
    t = _low(text)

    # === STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_BAD_RESULT_MARKERS ===
    stale_markers = (
        "задачи за последние 24 часа",
        "создание сметы: профлист",
        "итоговая сумма: 55000",
        "1capn1ikkxwypbxhny5caokqrsxbgzho",
        "1glcscpl3d91elveo_m11ezwh_uu5b4vm",
        "1pu77xrzhmpobus1pfximwdwckrgje1tn",
        "смета уже есть:",
        "смета создана по образцу вор",
        "вор_кирпичная_кладка",
        "vor_kirpich",
        "позиций: 13 | итого: 690510",
        "690510.00 руб",
        "файлы в этом топике уже есть",
        "нашёл релевантное",
        "нашел релевантное",
        "активный контекст найден",
    )
    if any(x in t for x in stale_markers):
        return True
    # === END_STROYKA_FULL_CHAIN_FINAL_CLOSE_VERIFIED_BAD_RESULT_MARKERS ===
    bad = (
        # === FULL_STROYKA_V3_SEARCH_LOOP_BAD_RESULT_FIX ===
        "поставщик | площадка",
        "auto_parts",
        "search_monolith",
        "tco | риски",
        "ошибка классификации запроса",
        "категория не совпадает",
        # === FULL_STROYKA_LOOP_FINAL_CLOSE_BAD_RESULT_FIX ===
        "смета создана по образцу вор",
        "смета уже есть:",
```

#### core/topic2_estimate_final_close_v2.py
```python
from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "outputs" / "topic2_estimates"
OUT.mkdir(parents=True, exist_ok=True)

ENGINE = "TOPIC2_ESTIMATE_FINAL_CLOSE_V2"

SHORT_WORDS = {
    "да", "да делай", "да, делай", "делай", "ок", "окей", "хорошо",
    "подтверждаю", "согласен", "верно", "все верно", "всё верно",
    "1", "2", "3", "вариант 1", "вариант 2", "вариант 3",
    "минимальные", "минимум", "самые дешевые", "самые дешёвые",
    "средние", "медианные", "медиана", "надежные", "надёжные"
}

ESTIMATE_WORDS = (
    "смет", "кп", "коммерческ", "расчет", "расчёт", "стоимост", "цена",
    "расцен", "ведомост", "монолит", "бетон", "арматур", "опалуб",
    "фундамент", "перекрыт", "колонн", "стен", "гидроизоляц",
    "утеплен", "засыпк", "свай", "плит", "лестнич"
)

IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp", ".tif", ".tiff")
DOC_EXT = (".pdf", ".docx", ".xlsx", ".xls", ".csv", ".txt")


def _s(v: Any, limit: int = 50000) -> str:
    if v is None:
        return ""
    try:
        return str(v).strip()[:limit]
    except Exception:
        return ""


def _low(v: Any) -> str:
    return _s(v).lower().replace("ё", "е")


def _field(task: Any, name: str, default: Any = None) -> Any:
    try:
        if hasattr(task, "keys") and name in task.keys():
            return task[name]
    except Exception:
        pass
    try:
        return task.get(name, default)
    except Exception:
        return getattr(task, name, default)


def _payload(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    t = _s(raw)
    if not t:
        return {}
    try:
        x = json.loads(t)
        return x if isinstance(x, dict) else {}
    except Exception:
        return {}


def _extract_payload_text(raw: Any) -> str:
    p = _payload(raw)
    parts = [_s(raw)]
    for k in ("caption", "text", "message", "file_name", "name", "title", "ocr_text", "recognized_text"):
        if p.get(k):
            parts.append(_s(p.get(k)))
    return "\n".join(x for x in parts if x).strip()


def _file_meta(raw: Any) -> Dict[str, str]:
    p = _payload(raw)
    keys_path = ("local_path", "path", "file_path", "downloaded_path", "server_path")
    keys_name = ("file_name", "name", "title")
    file_path = ""
    file_name = ""
    for k in keys_path:
        if p.get(k):
            file_path = _s(p.get(k))
            break
    for k in keys_name:
        if p.get(k):
            file_name = _s(p.get(k))
            break
    if not file_name and file_path:
        file_name = os.path.basename(file_path)
    return {"file_path": file_path, "file_name": file_name}


def _read_file_text(path: str) -> str:
    p = Path(_s(path))
    if not p.exists() or not p.is_file():
        return ""
    suf = p.suffix.lower()
    try:
        if suf == ".txt":
            return p.read_text(encoding="utf-8", errors="ignore")[:50000]
        if suf == ".csv":
            return p.read_text(encoding="utf-8", errors="ignore")[:50000]
        if suf == ".pdf":
            try:
                import fitz
                doc = fitz.open(str(p))
                return "\n".join(page.get_text("text") for page in doc)[:50000]
            except Exception:
                return ""
        if suf == ".docx":
            try:
                import docx
                d = docx.Document(str(p))
                return "\n".join(x.text for x in d.paragraphs)[:50000]
            except Exception:
                return ""
        if suf in (".xlsx", ".xls"):
            try:
                from openpyxl import load_workbook
                wb = load_workbook(str(p), data_only=True, read_only=True)
                out = []
                for ws in wb.worksheets[:3]:
                    for row in ws.iter_rows(max_row=200, values_only=True):
                        vals = [_s(x, 200) for x in row if _s(x)]
                        if vals:
                            out.append(" | ".join(vals))
                return "\n".join(out)[:50000]
            except Exception:
                return ""
        if suf in IMAGE_EXT:
            try:
                from PIL import Image
                import pytesseract
                return pytesseract.image_to_string(Image.open(str(p)), lang="rus+eng")[:50000]
            except Exception:
                return ""
    except Exception:
        return ""
    return ""


def _is_short_control(text: str) -> bool:
    t = re.sub(r"\s+", " ", _low(text).replace("[voice]", "")).strip(" .,!?:;")
    return t in SHORT_WORDS or (len(t) <= 18 and any(t.startswith(x) for x in SHORT_WORDS))


def _is_estimate_intent(text: str, file_name: str = "") -> bool:
    low = _low(text + " " + file_name)
    if not low:
        return False
    if any(x in low for x in ESTIMATE_WORDS):
        return True
    return bool(re.search(r"\b(м3|м³|м2|м²|шт|кг|тн|п\.?\s*м)\b", low))


def _is_file_or_photo(input_type: str, raw: Any) -> bool:
    meta = _file_meta(raw)
    name = _low(meta.get("file_name") or meta.get("file_path"))
    if input_type in ("photo", "image", "file", "drive_file", "document"):
        return True
    return name.endswith(IMAGE_EXT + DOC_EXT)


def _qty(v: str) -> float:
    s = _s(v).replace("≈", "").replace("~", "").replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def _normalize_unit(u: str) -> str:
    x = _low(u).replace(" ", "")
    return {
        "м3": "м³", "м.3": "м³", "м³": "м³",
        "м2": "м²", "м.2": "м²", "м²": "м²",
        "п.м": "п.м", "пм": "п.м",
        "шт.": "шт", "шт": "шт",
        "компл.": "компл", "компл": "компл",
        "тн": "т", "тонн": "т",
    }.get(x, x or "шт")


def _parse_items(text: str) -> List[Dict[str, Any]]:
    src = _s(text, 50000)
    t = re.sub(r"\s+", " ", src)
    t = re.sub(r"(?<![\d,.])\s+(\d{1,2})\s+(?=[А-ЯA-ZЁ])", r"\n\1 ", t)
    unit_re = r"(м³|м3|м\.3|м²|м2|м\.2|п\.?\s*м|шт\.?|кг|тн|т|компл\.?)"
    items: List[Dict[str, Any]] = []

    for line in t.splitlines():
        line = line.strip(" ;")
        if not line:
            continue
        m = re.search(
            rf"^\s*(?P<num>\d{{1,3}})\s+(?P<name>.+?)\s+(?P<unit>{unit_re})\s+(?P<qty>[~≈]?\s*\d[\d\s]*(?:[,.]\d+)?)",
            line,
            flags=re.I,
        )
        if not m:
            continue
        name = re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")
        unit = _normalize_unit(m.group("unit"))
        qty = _qty(m.group("qty"))
        if not name or qty <= 0:
            continue
        items.append({
            "num": len(items) + 1,
            "name": name[:240],
            "qty": qty,
            "unit": unit,
            "price": 0.0,
            "source": "parsed",
        })

    if not items:
        m = re.search(rf"(?P<name>.{{1,120}}?)\s+(?P<unit>{unit_re})\s+(?P<qty>\d[\d\s]*(?:[,.]\d+)?)", t, flags=re.I)
        if m:
            items.append({
                "num": 1,
                "name": re.sub(r"\s+", " ", m.group("name")).strip(" -–—:")[:240] or "Позиция",
                "qty": _qty(m.group("qty")),
                "unit": _normalize_unit(m.group("unit")),
                "price": 0.0,
                "source": "fallback",
            })

    if not items:
        items.append({
            "num": 1,
            "name": "Позиция по присланному фото / файлу / тексту",
            "qty": 1.0,
            "unit": "компл",
            "price": 0.0,
            "source": "manual_review_required",
        })

    return items[:200]


def _write_xlsx(path: Path, items: List[Dict[str, Any]], source_text: str, photo_text: str = "") -> None:
```

### TOPIC_FILE_INLINE
```
# topic_2 STROYKA

GENERATED_AT: 2026-05-08T18:45:02.576270+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 2
ROLE: Сметы
DIRECTIONS_BOUND: estimates
CURRENT_STATUS: INSTALLED_NOT_VERIFIED
ACTIVE_TASKS: 1
FAILED_LAST_24H: 1

## DB_STATE_COUNTS
- ARCHIVED: 12
- CANCELLED: 103
- DONE: 132
- FAILED: 110
- WAITING_CLARIFICATION: 1

## LATEST_FAILED
- 1d2b38c4 | STALE_TIMEOUT
- a7b2879e | STALE_TIMEOUT
- 893436d4 | INVALID_PUBLIC_RESULT
- f43100b3 | TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_WORKER_ERR:maximum recursion depth exceeded
- c6b40dfc | STROYKA_QG_FAILED:XLSX_VALIDATE_ERROR:maximum recursion depth exceeded

## COMMITS_LAST_14D
- 075edf9|fix(topic2): PATCH_TOPIC2_STALE_PENDING_TASK_GUARD_V1 + LOCAL_BOT_API_404_FIX
- e185e83|fix(topic2): PATCH_SUPPLIER_HONESTY_V1 — fix fake Perplexity в Поставщик
- 6cf9154|fix(topic2): PATCH_TOPIC2_ADD_PEREKRYTIYA_SECTION_V1 — add missing §5 Перекрытия section
- 2475eb5|fix(topic2): PATCH_TOPIC2_REALSHEET_PRICES_V3 — real Газобетонный дом prices
- 7c646dd|session(08.05): bigfile activated, topic5 V3 dispatcher, topic2 P6C intercept, c94ec497 FAILED/NOT_PROVEN
- 8760011|fix(topic2): enforce full canonical estimate pipeline without cross-topic regression
- b236f02|fix(topic2): session 08.05 — P6C fulltext prep, P3CHK append fix, P2 distance skip, WCPE unblock
- e3a016c|PATCH_OPENROUTER_ONLINE_ONLY_FOR_TOPIC2_PRICE_SEARCH_V1: hard-enforce Sonar for all price/search calls
- 4cfd9b6|fix(topic2): close P6E67 loop storm + natural reply message
- dc26486|fix(topic2): PATCH_PRICE_REJECT_STORM_FIX_V1 — remove noisy INSERT from V5/V6C rejected path
- 0c8518e|fix(topic2): TOPIC2_FULL_CLOSE — work/material split, sheet fallback, drive links, xlsx 15-col gate
- a216eeb|fix(topic2): PATCH_FCG_V2PATH_BYPASS_V1 — extend FDCB bypass to TOPIC2_DONE_CONTRACT_OK
- 48f9858|docs(handoff): update latest handoff after topic2 and aggregator guard
- c0300fb|fix(topic2): close 4 code gaps — enrichment markers, cyrillic marker, function-object bug, FCG bypass
- 2ece9eb|fix(topic2): close 3 live bugs — poison loop terminate, recursion restore, FCG done bypass
- 62d85b8|fix(topic2): V5B — price source quality gate, raw JSON guard, canonical totals col J
- 168ce5e|fix(topic2): close final V5 code gaps for prices guards totals
- 983ced8|fix(topic2): close 3 remaining V4 gaps (repeat/negative/pdf_missing_question)
- 2353fc3|fix(topic2): close remaining project/pdf/photo/price/artifact gaps V4
- ccab9ed|fix(topic2): PATCH_TOPIC2_FULL_CLOSE_RUNTIME_V3 — all 9 requirements
- 055157b|fix(topic2): PATCH_TOPIC2_FULL_CLOSE_RUNTIME_V2
- ad829c4|fix(topic2): PATCH_TOPIC2_FULL_CANONICAL_CLOSE_ONEPASS_V1 — §9 output + recursion fix
- c7c8755|fix(topic2): inline-fix V1 — replace dead wrappers with body edits
- d1f20a0|fix(topic2): full mega-guards V1 — 6 guards закрытие topic_2 acceptance bugs
- 9420d6a|fix(topic2): stroyka meta-confirm guard + reply chain + xlsx 15 cols + topic210 meta guard
- 58d33aa|fix(topic2): stop T2RFP infinite redirect loop for drive_file re-picks
- b17bca2|fix(topic2): stop WAITING_CLARIFICATION pick loop
- 2ef3f86|fix(topic2): price reply thread isolation + chat-aware price search
- a054796|feat(topic2): canonical template selection, 15-col XLSX, status guard
- 79ba839|fix(topic2): redirect simplified v2 path to full P2/P3 pipeline

## MARKERS_LAST_24H
- created:NEW
- clarified:
- PATCH_TOPIC2_INLINE_FIX_20260506_V1:V6C_PRICE_REJECTED:no_explicit_token_or_long
- PATCH_TOPIC2_INLINE_FIX_20260506_V1:V5_PRICE_REJECTED:no_explicit_token_or_long
- P6E67_PARENT_NOT_FOUND
- P6E67_PARENT_NOT_FOUND_TERMINAL_GUARD_V1:WAITING_CLARIFICATION
- clarified:Вот документ мне необходимо посчитать стоимость строительства Дом из г
- state:FAILED
- reply_sent:stale_failed
- reply_sent:p6e67_parent_not_found
- P6E67_PARENT_REVIVED_AS_REVISION_SOURCE:LAST_ACTIVE_ESTIMATE_FALLBACK
- P6E67_REVISION_TEXT_MERGED_FROM_TASK:89f1a927-af21-4d77-b287-70e8ecef659c
- P6E67_CURRENT_TASK_CANCELLED_MERGED_TO_PARENT:d72028da-b4ff-424d-a626-790c9da8be
- P6E67_BLOCK_ARTIFACT_GATE_PDF_LINK_MISSING_BEFORE_SEND_EX
- P6C_TOPIC2_IMAGE_OR_FILE_ESTIMATE_ROUTE_TAKEN
- TOPIC2_PRICE_CHOICE_REQUESTED
- clarified:2
- P6E67_BLOCK_ARTIFACT_GATE_PDF_LINK_MISSING_BEFORE_SEND
- P6E67_REVISION_TEXT_MERGED_FROM_TASK:0aaa723d-e506-4cfe-9cfc-7dc20b7ea094
- continued:вот размеры
- continued:вот задание
- TOPIC2_PRICE_CHOICE_CONFIRMED:confirmed
- P3_TOPIC2_CLARIFICATION
- clarified:Там же есть картинка посмотри проект
- clarified:есть в проекте
- clarified:смотри задание и проект
- clarified:ты не видешь что ранее писал?
- clarified:где расчет?
- clarified:ну че
- clarified:заебал

## BLOCKERS_FROM_NOT_CLOSED
- - topic_2 не тянет проектные образцы topic_210
- - topic_210 не тянет сметные артефакты как результат
- - WRONG_FILES_SHOWN_IN_TOPIC_2
- - проверить topic_210: "какие образцы есть по АР/КЖ/КД" должен показать список без создания файла
- - проверить topic_2: "В" и "вариант 2" после выбора цены должны создать XLSX/PDF
- - проверить topic isolation: topic_2 не должен показывать КЖ/АР файлы topic_210 без прямого запроса
- - topic_2: "смету дома 10×12 газобетон монолит 2 этажа 120 км коробка"
- - topic_2: "Доделай мне нормально эту задачу"

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 29
chats: 1

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## NEXT_REQUIRED_PATCH
PATCH_TOPIC2_FULL_GAP_CLOSE_V4

## OPEN_CONTOURS
- P6E2 photo intercept before canonical
- pdf_spec_extractor.py exists but not connected to canonical flow
- ocr_table_engine.py exists but not connected to topic_2 flow
- per-item materials + works internet price search missing
- TOPIC2_MULTIFILE_PROJECT_CONTEXT_* missing
- TOPIC2_REVISION_BOUND_TO_PARENT missing
- TOPIC2_REPEAT_PARENT_TASK missing
- TOPIC2_AFTER_PRICE_CHOICE_GENERATION_STARTED missing
- TOPIC2_FORBIDDEN_FINAL_RESULT_BLOCKED missing
- TOPIC2_PDF_TOTALS_MATCH_XLSX missing
- live verification pending

## REQUIRED_MARKERS
- TOPIC2_ESTIMATE_SESSION_CREATED
- TOPIC2_CONTEXT_READY
- TOPIC2_TEMPLATE_SELECTED
- TOPIC2_PRICE_ENRICHMENT_DONE
- TOPIC2_PRICE_CHOICE_CONFIRMED
- TOPIC2_LOGISTICS_CONFIRMED
- TOPIC2_XLSX_CREATED
- TOPIC2_PDF_CREATED
- TOPIC2_PDF_CYRILLIC_OK
- TOPIC2_DRIVE_UPLOAD_XLSX_OK
- TOPIC2_DRIVE_UPLOAD_PDF_OK
- TOPIC2_TELEGRAM_DELIVERED
- TOPIC2_MESSAGE_THREAD_ID_OK
- TOPIC2_DONE_CONTRACT_OK

## MARKERS_MISSING
- TOPIC2_ESTIMATE_SESSION_CREATED
- TOPIC2_CONTEXT_READY
- TOPIC2_LOGISTICS_CONFIRMED
- TOPIC2_XLSX_CREATED
- TOPIC2_MESSAGE_THREAD_ID_OK
- TOPIC2_DONE_CONTRACT_OK

## REGRESSION_GUARDS
- не возвращать P6E67_PARENT_NOT_FOUND на полное ТЗ
- не возвращать INVALID_PUBLIC_RESULT при наличии markers + Drive ссылок
- не убивать задачи с TOPIC2_PRICE_CHOICE_REQUESTED 30-мин таймаутом
- не плодить новые задачи на короткий ответ 2/да при WAITING_PRICE

## LIVE_VERIFY_COMMANDS
- sqlite3 data/core.db "SELECT id,state FROM tasks WHERE topic_id=2 ORDER BY rowid DESC LIMIT 10"
- journalctl -u areal-task-worker --since '10 minutes ago' | grep -E 'TOPIC2|TPRR|TPTG|TFFE|TDOIP'
- sqlite3 data/core.db "SELECT action FROM task_history WHERE task_id IN (SELECT id FROM tasks WHERE topic_id=2 ORDER BY rowid DESC LIMIT 1)"

## ESTIMATE_TEMPLATE_REGISTRY
loaded: True
- M80 | М-80.xlsx | full_house_estimate_template
- M110 | М-110.xlsx | full_house_estimate_template
- ROOF_FLOORS | крыша и перекр.xlsx | roof_and_floor_estimate_template
- FOUNDATION_WAREHOUSE | фундамент_Склад2.xlsx | foundation_estimate_template
- AREAL_NEVA | Ареал Нева.xlsx | general_company_estimate_template

## OWNER_REFERENCE_REGISTRY
loaded: True
items: 11

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days


```

## TOPIC_5_TEKHNADZOR

STATUS: IDLE_NO_FAILURES_NOT_VERIFIED
ACTIVE: 0  FAILED_24H: 0
DIRECTIONS_BOUND: Технадзор

### LAST_FAILED (5)
- 775a2251 | 2026-05-06 14:24:33 | STALE_NEW_30MIN
    history: state:FAILED:stale_runtime_cleanup_NEW_30min
    history: created:NEW
- f3637754 | 2026-05-06 14:24:33 | STALE_NEW_30MIN
    history: state:FAILED:stale_runtime_cleanup_NEW_30min
    history: created:NEW
- ddfc12b1 | 2026-05-06 15:45:21 | PATCH_TOPIC2_UNBLOCK_PICK_NEXT_V1_CLOSED_BLOCKER
    history: PATCH_TOPIC2_UNBLOCK_PICK_NEXT_V1_CLOSED_BLOCKER
    history: FULLFIX_TOPIC5_REPLY_TO_PHOTO_BOUND
    history: P6F_DAH_BLOCKED_DONE_NO_UPLOAD_OR_TG_HISTORY
- 24ffa14f | 2026-05-06 13:33:07 | INVALID_PUBLIC_RESULT
    history: FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:UPDATE_BLOCKED:INVALID_PUBLIC_RESULT
    history: created:NEW
- 8093deb3 | 2026-05-06 13:33:05 | INVALID_PUBLIC_RESULT
    history: FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:UPDATE_BLOCKED:INVALID_PUBLIC_RESULT
    history: created:NEW

### KEY_ENGINE_CODE (head 250 lines each)
#### core/technadzor_engine.py
```python
# === FINAL_CLOSURE_BLOCKER_FIX_V1_TECHNADZOR_ENGINE ===
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

BASE = Path("/root/.areal-neva-core")
OUT = BASE / "outputs" / "technadzor"
OUT.mkdir(parents=True, exist_ok=True)


def is_technadzor_intent(text: str = "", file_name: str = "") -> bool:
    t = f"{text} {file_name}".lower().replace("ё", "е")
    return bool(re.search(r"\b(акт|технадзор|техническ.*надзор|дефект|замечан|нарушен|освидетельств|стройконтроль|сп|гост|снип)\b", t))


def _norm_refs(text: str) -> str:
    refs = []
    for m in re.findall(r"\b(сп\s*\d+[.\d]*|гост\s*\d+[.\d-]*|снип\s*[\w.\-]+)\b", text or "", flags=re.I):
        refs.append(m.upper().replace("  ", " "))
    return ", ".join(sorted(set(refs))) if refs else "Норма не подтверждена"


def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = "") -> Dict[str, Any]:
    if not is_technadzor_intent(text, file_name):
        return {"ok": False, "handled": False, "reason": "NOT_TECHNADZOR"}

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"TECHNADZOR_ACT__{task_id[:8] or ts}"
    txt_path = OUT / f"{stem}.txt"

    body = [
        "АКТ ТЕХНИЧЕСКОГО НАДЗОРА",
        "",
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Задача: {task_id}",
        f"Топик: {topic_id}",
    ]

    if file_name:
        body.append(f"Файл: {file_name}")

    body.extend(
        [
            "",
            "Исходное описание:",
            (text or "").strip() or "UNKNOWN",
            "",
            "Нормативная база:",
            _norm_refs(text),
            "",
            "Вывод:",
            "Черновик акта создан. Если норматив не подтверждён источником, в акте указано: Норма не подтверждена",
        ]
    )

    txt_path.write_text("\n".join(body) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "handled": True,
        "kind": "technadzor_act",
        "state": "DONE",
        "artifact_path": str(txt_path),
        "message": "Технадзорный акт подготовлен",  # TECHNADZOR_PUBLIC_MESSAGE_NO_LOCAL_PATH_V1
        "history": "FINAL_CLOSURE_BLOCKER_FIX_V1:TECHNADZOR_ACT_CREATED",
    }


# === END_FINAL_CLOSURE_BLOCKER_FIX_V1_TECHNADZOR_ENGINE ===


# === P6_TECHNADZOR_TEMPLATE_AND_ARTIFACT_CLOSE_20260504_V1 ===
# Scope:
# - technadzor sample/template files can be saved as active reference per chat/topic
# - future technadzor acts use active reference metadata
# - produces TXT and DOCX when python-docx exists; no DB schema changes

import json as _p6tz_json
import re as _p6tz_re
from datetime import datetime as _p6tz_datetime
from pathlib import Path as _p6tz_Path

_P6TZ_BASE = _p6tz_Path("/root/.areal-neva-core")
_P6TZ_TEMPLATE_DIR = _P6TZ_BASE / "data/templates/technadzor"
_P6TZ_OUT = _P6TZ_BASE / "outputs/technadzor"
_P6TZ_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
_P6TZ_OUT.mkdir(parents=True, exist_ok=True)

def _p6tz_s(v, limit=12000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6tz_low(v):
    return _p6tz_s(v).lower().replace("ё", "е")

def _p6tz_template_path(chat_id, topic_id):
    safe_chat = _p6tz_re.sub(r"[^0-9a-zA-Z_-]+", "_", str(chat_id or "unknown"))
    return _P6TZ_TEMPLATE_DIR / f"ACTIVE__chat_{safe_chat}__topic_{int(topic_id or 0)}.json"

def _p6tz_is_template_intent(text="", file_name=""):
    low = _p6tz_low(str(text) + " " + str(file_name))
    return any(x in low for x in ("образец", "шаблон", "пример", "как образец", "как шаблон", "возьми его как образец", "сохрани как образец")) and any(x in low for x in ("технадзор", "акт", "замечан", "дефект", "строительный контроль", "стройконтроль"))

def _p6tz_save_template(text="", task_id="", chat_id="", topic_id=0, file_path="", file_name=""):
    meta = {
        "engine": "P6_TECHNADZOR_TEMPLATE_AND_ARTIFACT_CLOSE_20260504_V1",
        "kind": "technadzor_template",
        "status": "active",
        "chat_id": str(chat_id or ""),
        "topic_id": int(topic_id or 0),
        "source_task_id": str(task_id or ""),
        "source_file_path": str(file_path or ""),
        "source_file_name": str(file_name or ""),
        "raw_user_instruction": _p6tz_s(text, 4000),
        "usage_rule": "Use this file as formatting/sample reference for future technadzor acts in same chat/topic",
        "saved_at": _p6tz_datetime.now().isoformat(),
    }
    path = _p6tz_template_path(chat_id, topic_id)
    path.write_text(_p6tz_json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def _p6tz_load_template(chat_id, topic_id):
    path = _p6tz_template_path(chat_id, topic_id)
    if not path.exists():
        return {}
    try:
        return _p6tz_json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _p6tz_refs(text):
    refs = []
    for m in _p6tz_re.findall(r"\b(сп\s*\d+[.\d]*|гост\s*\d+[.\d-]*|снип\s*[\w.\-]+)\b", text or "", flags=_p6tz_re.I):
        refs.append(m.upper().replace("  ", " "))
    return ", ".join(sorted(set(refs))) if refs else "Норма не подтверждена"

def _p6tz_make_docx(path, lines):
    try:
        from docx import Document
        doc = Document()
        for i, line in enumerate(lines):
            if i == 0:
                doc.add_heading(line, level=1)
            elif line == "":
                doc.add_paragraph("")
            else:
                doc.add_paragraph(line)
        doc.save(str(path))
        return str(path)
    except Exception:
        return ""

try:
    _p6tz_orig_is_intent = is_technadzor_intent
    def is_technadzor_intent(text: str = "", file_name: str = "") -> bool:
        low = _p6tz_low(str(text) + " " + str(file_name))
        if _p6tz_is_template_intent(text, file_name):
            return True
        if any(x in low for x in ("технадзор", "акт", "замечан", "дефект", "нарушен", "освидетельств", "стройконтроль", "строительный контроль", "сп ", "гост", "снип")):
            return True
        return _p6tz_orig_is_intent(text, file_name)
except Exception:
    pass

try:
    _p6tz_orig_process = process_technadzor
    def process_technadzor(text: str = "", task_id: str = "", chat_id: str = "", topic_id: int = 0, file_path: str = "", file_name: str = ""):
        if _p6tz_is_template_intent(text, file_name):
            meta_path = _p6tz_save_template(text=text, task_id=task_id, chat_id=chat_id, topic_id=topic_id, file_path=file_path, file_name=file_name)
            return {
                "ok": True,
                "handled": True,
                "kind": "technadzor_template_saved",
                "state": "DONE",
                "artifact_path": str(meta_path),
                "message": "Образец технадзора сохранён для этого топика",
                "history": "P6_TECHNADZOR_TEMPLATE_SAVED",
            }

        if not is_technadzor_intent(text, file_name):
            return {"ok": False, "handled": False, "reason": "NOT_TECHNADZOR"}

        tpl = _p6tz_load_template(chat_id, topic_id)
        ts = _p6tz_datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = str(task_id or ts)[:8] or ts
        stem = f"TECHNADZOR_ACT__{safe}"
        txt_path = _P6TZ_OUT / f"{stem}.txt"
        docx_path = _P6TZ_OUT / f"{stem}.docx"

        lines = [
            "АКТ ТЕХНИЧЕСКОГО НАДЗОРА",
            "",
            f"Дата: {_p6tz_datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Задача: {task_id}",
            f"Топик: {topic_id}",
        ]
        if file_name:
            lines.append(f"Файл: {file_name}")
        if tpl:
            lines.append(f"Образец: {tpl.get('source_file_name') or tpl.get('source_file_path') or 'активный шаблон топика'}")
        lines += [
            "",
            "Исходное описание:",
            _p6tz_s(text, 6000) or "UNKNOWN",
            "",
            "Нормативная база:",
            _p6tz_refs(text),
            "",
            "Выявленные замечания:",
            "1. Требуется заполнение по присланным фото/файлам и описанию",
            "",
            "Требуемые действия:",
            "1. Устранить замечания",
            "2. Предоставить фотофиксацию устранения",
            "3. Повторно предъявить участок работ техническому надзору",
            "",
            "Статус:",
            "Черновик подготовлен по текущим данным",
        ]

        txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        docx_created = _p6tz_make_docx(docx_path, lines)
        return {
            "ok": True,
            "handled": True,
            "kind": "technadzor_act",
            "state": "DONE",
            "artifact_path": docx_created or str(txt_path),
            "extra_artifact_path": str(txt_path),
            "message": "Технадзорный акт подготовлен",
            "history": "P6_TECHNADZOR_ACT_CREATED",
        }
except Exception:
    pass

# === END_P6_TECHNADZOR_TEMPLATE_AND_ARTIFACT_CLOSE_20260504_V1 ===

# === P6C_TECHNADZOR_CONN_COMPAT_TEMPLATE_ACT_CLOSE_20260504_V1 ===
import json as _p6c_te_json
import re as _p6c_te_re
from pathlib import Path as _p6c_te_Path
from datetime import datetime as _p6c_te_datetime

```

#### core/normative_engine.py
```python
# === NORMATIVE_ENGINE_SAFE_V1 ===
from __future__ import annotations
from typing import Any, Dict, List

NORMATIVE_INDEX = [
    {"keywords": ["трещин", "бетон", "монолит", "раковин", "скол"], "norm_id": "СП 70.13330.2012", "section": "Несущие и ограждающие конструкции", "requirement": "Дефекты бетонных и железобетонных конструкций подлежат фиксации, оценке влияния на несущую способность и устранению по проектному решению", "confidence": "PARTIAL"},
    {"keywords": ["бетон", "арматур", "защитный слой", "а500", "b25", "в25"], "norm_id": "СП 63.13330.2018", "section": "Бетонные и железобетонные конструкции", "requirement": "Расчёт и контроль железобетонных конструкций выполняется с учётом класса бетона, арматуры, защитного слоя и требований проектной документации", "confidence": "PARTIAL"},
    {"keywords": ["нагрузк", "фундамент", "плита", "перекрытие", "кж"], "norm_id": "СП 20.13330.2016/2017", "section": "Нагрузки и воздействия", "requirement": "Проверка конструкций выполняется с учётом постоянных, временных и особых нагрузок по расчётным сочетаниям", "confidence": "PARTIAL"},
    {"keywords": ["кровл", "протеч", "мембран", "пароизоляц", "водосток"], "norm_id": "СП 17.13330.2017", "section": "Кровли", "requirement": "Кровельные работы должны обеспечивать водонепроницаемость, надёжное примыкание и соответствие проектным решениям", "confidence": "PARTIAL"},
    {"keywords": ["отделк", "штукатур", "плитк", "стяжк", "покраск"], "norm_id": "СП 71.13330.2017", "section": "Изоляционные и отделочные покрытия", "requirement": "Отделочные покрытия проверяются по основанию, геометрии, сцеплению, ровности и отсутствию видимых дефектов", "confidence": "PARTIAL"},
    {"keywords": ["металл", "сварк", "км", "кмд", "болт", "корроз"], "norm_id": "СП 16.13330.2017", "section": "Стальные конструкции", "requirement": "Стальные конструкции должны соответствовать расчётной схеме, проектным сечениям, качеству сварных и болтовых соединений", "confidence": "PARTIAL"},
    {"keywords": ["проект", "чертеж", "чертёж", "спецификац", "ведомость", "стадия"], "norm_id": "ГОСТ 21.101-2020", "section": "Основные требования к проектной и рабочей документации", "requirement": "Проектная и рабочая документация оформляется с составом, обозначениями и ведомостями по системе проектной документации для строительства", "confidence": "PARTIAL"},
    {"keywords": ["кж", "железобетон", "армирование", "опалуб", "монолит"], "norm_id": "ГОСТ 21.501-2018", "section": "Правила выполнения рабочей документации архитектурных и конструктивных решений", "requirement": "Рабочие чертежи конструктивных решений должны содержать схемы, спецификации, ведомости элементов и данные для производства работ", "confidence": "PARTIAL"},
]

def search_norms_sync(text: str, limit: int = 5) -> List[Dict[str, Any]]:
    hay = (text or "").lower()
    scored = []
    for row in NORMATIVE_INDEX:
        score = sum(1 for kw in row["keywords"] if kw in hay)
        if score:
            item = dict(row)
            item["score"] = score
            scored.append(item)
    scored.sort(key=lambda x: int(x.get("score") or 0), reverse=True)
    return scored[:limit]

def format_norms_for_act(norms: List[Dict[str, Any]]) -> str:
    return "\n".join(f"{n.get('norm_id','')}: {n.get('requirement','')} [{n.get('confidence','PARTIAL')}]" for n in norms or [] if n.get("norm_id"))
# === END_NORMATIVE_ENGINE_SAFE_V1 ===


# === P6H_NORMATIVE_INDEX_EXTRA_V1 ===
# Append-only extension to NORMATIVE_INDEX with technadzor-specific norms
# referenced in real client acts (Киевское 95, металлокаркас, антикоррозия,
# обследование зданий и сооружений, организация строительного контроля).
# Each entry uses confidence=PARTIAL — promote to CONFIRMED only after manual
# review of an authoritative source.
import logging as _p6h_norm_logging

_P6H_NORMATIVE_EXTRA = [
    {
        "keywords": ["антикорроз", "лакокрас", "окрас", "защитное покрытие", "ржавчин"],
        "norm_id": "СП 28.13330.2017",
        "section": "Защита строительных конструкций от коррозии",
        "requirement": "Требования к защите строительных конструкций от коррозии: подготовка поверхности, выбор защитной системы, контроль качества и сохранности покрытия в процессе эксплуатации",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["металлоконструкц", "стальн", "сварн", "ферм", "колонн", "балк", "кмд", "мк", "анкерн"],
        "norm_id": "ГОСТ 23118-2019",
        "section": "Конструкции стальные строительные. Общие технические условия",
        "requirement": "Требования к материалам, изготовлению, монтажу и приёмке стальных строительных конструкций, включая сварные и болтовые соединения, антикоррозионную защиту, маркировку",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["организация строительного контроля", "осс", "стройконтроль", "технадзор", "приёмка", "приемка", "освидетельств"],
        "norm_id": "СП 48.13330.2019",
        "section": "Организация строительства",
        "requirement": "Порядок организации строительного контроля заказчика и подрядчика, освидетельствование скрытых работ, ведение исполнительной документации",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["обследован", "техническое состояние", "категория состояния", "несущ", "предаварийн", "аварийн"],
        "norm_id": "СП 13-102-2003",
        "section": "Правила обследования несущих строительных конструкций зданий и сооружений",
        "requirement": "Порядок и состав обследований несущих конструкций, методы выявления дефектов и повреждений, классификация технического состояния (нормальное, удовлетворительное, ограниченно работоспособное, аварийное)",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["обследован", "мониторинг", "техническое состояние", "категория"],
        "norm_id": "ГОСТ 31937-2024",
        "section": "Здания и сооружения. Правила обследования и мониторинга технического состояния",
        "requirement": "Современные правила обследования и мониторинга технического состояния зданий и сооружений: цели, состав работ, оформление результатов, заключение о категории состояния",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["сварн", "сварка", "шов", "провар", "наплыв", "качество свар"],
        "norm_id": "ГОСТ Р ИСО 17637-2014",
        "section": "Неразрушающий контроль сварных соединений. Визуальный контроль",
        "requirement": "Правила визуального и измерительного контроля сварных соединений: критерии приёмки, фиксация дефектов, оформление результатов",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["опорн", "анкерн", "плита", "опирани", "узел колонн", "подлив"],
        "norm_id": "СП 70.13330.2012",
        "section": "Несущие и ограждающие конструкции — опорные узлы металлоконструкций",
        "requirement": "Опорные узлы стальных колонн должны передавать нагрузку через плотное опирание опорной плиты на фундамент. Подливка под опорные плиты выполняется до проектного состояния, без зазоров, трещин и разрушений",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["укосин", "связи", "диагональн", "горизонтальн связи", "пространственн"],
        "norm_id": "СП 16.13330.2017",
        "section": "Стальные конструкции — пространственные связи",
        "requirement": "Узлы пересечения и крепления связей жёсткости должны обеспечивать пространственную жёсткость каркаса; ослабленные или непроработанные узлы не допускаются",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["основан", "грунт", "замачив", "размыв", "просадк", "водоотвод"],
        "norm_id": "СП 22.13330.2016",
        "section": "Основания зданий и сооружений",
        "requirement": "Подготовка и эксплуатация оснований: водоотвод от фундаментов, защита от замачивания, контроль осадок и просадок, обеспечение проектной несущей способности грунта",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["перекрыт", "ригел", "балк", "несущая способность"],
        "norm_id": "СП 20.13330.2016",
        "section": "Нагрузки и воздействия — перекрытия",
        "requirement": "Перекрытия должны рассчитываться на постоянные и временные нагрузки с учётом особых воздействий; конструктивные решения и сечения элементов должны соответствовать расчётной схеме",
        "confidence": "PARTIAL",
    },
]

try:
    NORMATIVE_INDEX.extend(_P6H_NORMATIVE_EXTRA)
    _p6h_norm_logging.getLogger("task_worker").info(
        "P6H_NORMATIVE_INDEX_EXTRA_V1_INSTALLED added=%d total=%d",
        len(_P6H_NORMATIVE_EXTRA), len(NORMATIVE_INDEX),
    )
except Exception:
    pass
# === END_P6H_NORMATIVE_INDEX_EXTRA_V1 ===


# === P6H5_NORMATIVE_FULL_EXPAND_V1 ===
# Comprehensive normative expansion: исполнительная документация, бетон,
# газобетон/кладка, стальные конструкции, отделка, фасады, ОВ, ВК,
# электрика, пожарная безопасность, охрана труда (35 записей).
# confidence=PARTIAL — promote after manual verification.

_P6H5_NORMATIVE_EXPAND = [
    # --- Блок 1: Исполнительная документация ---
    {
        "keywords": ["исполнительн", "акт скрытых", "скрытые работы", "освидетельств", "исполнительная документация", "кс-2", "кс-3"],
        "norm_id": "РД-11-02-2006",
        "section": "Требования к составу и порядку ведения исполнительной документации",
        "requirement": "Состав и порядок ведения исполнительной документации при строительстве: акты освидетельствования скрытых работ, акты промежуточной приёмки ответственных конструкций, исполнительные схемы",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["журнал работ", "общий журнал", "журнал производства", "ожр", "специальный журнал"],
        "norm_id": "РД-11-05-2007",
        "section": "Порядок ведения общего и специальных журналов работ",
        "requirement": "Порядок ведения общего журнала работ и специальных журналов при строительстве: состав записей, ответственные лица, порядок хранения и передачи",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["авторский надзор", "надзор проектировщик", "проектировщик на объекте", "журнал авторского надзора"],
        "norm_id": "СП 11-110-99",
        "section": "Авторский надзор за строительством зданий и сооружений",
        "requirement": "Порядок осуществления авторского надзора проектировщиков за строительством: состав работ, права и обязанности, журнал авторского надзора",
        "confidence": "PARTIAL",
    },
    # --- Блок 2: Бетон (расширение) ---
    {
        "keywords": ["бетонная смесь", "подвижность смеси", "водоцементн", "класс бетона", "замес бетон", "марка бетона"],
        "norm_id": "ГОСТ 7473-2010",
        "section": "Смеси бетонные. Технические условия",
        "requirement": "Требования к бетонным смесям: классификация, показатели удобоукладываемости, водонепроницаемости, морозостойкости, правила приёмки и контроля",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["прочность бетона", "испытание бетона", "образец-куб", "керн бетон", "контроль прочности бетон"],
        "norm_id": "ГОСТ 18105-2018",
        "section": "Бетоны. Правила контроля и оценки прочности",
        "requirement": "Правила контроля и оценки прочности бетона в конструкциях: методы испытаний, статистический контроль, приёмочные уровни",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["тяжёлый бетон", "тяжелый бетон", "состав бетона", "крупный заполнитель", "щебень бетон"],
        "norm_id": "ГОСТ 26633-2015",
        "section": "Бетоны тяжёлые и мелкозернистые. Технические условия",
        "requirement": "Технические требования к тяжёлым и мелкозернистым бетонам: классы по прочности, морозостойкости, водонепроницаемости, правила приёмки и методы испытаний",
        "confidence": "PARTIAL",
    },
    # --- Блок 3: Газобетон и кладка ---
    {
        "keywords": ["газоблок", "газобетон", "ячеистый бетон", "автоклавный бетон", "d400", "d500", "d600"],
        "norm_id": "ГОСТ 31360-2007",
        "section": "Изделия стеновые неармированные из ячеистого бетона автоклавного твердения",
        "requirement": "Требования к стеновым блокам из ячеистого автоклавного бетона: классы по плотности, прочности, морозостойкости, геометрические параметры, правила приёмки",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["кладка газобетон", "армирование газобетон", "газобетонный блок", "стена из газобетон"],
        "norm_id": "СП 339.1325800.2017",
        "section": "Конструкции с применением автоклавного газобетона",
        "requirement": "Проектирование и возведение конструкций из автоклавного газобетона: кладочные растворы, армирование, обеспечение жёсткости, допустимые деформации",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["кладка", "каменная конструкц", "кирпич", "кладочный раствор", "армокаменн", "кладка блоков"],
        "norm_id": "СП 15.13330.2020",
        "section": "Каменные и армокаменные конструкции",
        "requirement": "Расчёт и проектирование каменных и армокаменных конструкций: требования к материалам, кладке, перевязке швов, анкеровке и армированию",
        "confidence": "PARTIAL",
    },
    # --- Блок 4: Стальные конструкции (расширение) ---
    {
        "keywords": ["проектирование стальных", "расчёт металлоконструкц", "расчет металлоконструкц", "км проект", "стальная конструкц"],
        "norm_id": "СП 294.1325800.2017",
        "section": "Конструкции стальные. Правила проектирования",
        "requirement": "Актуализированные правила проектирования стальных конструкций: расчётные сопротивления, предельные состояния, соединения, устойчивость элементов",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["прокат стальн", "двутавр", "швеллер", "уголок металл", "листовой прокат", "сортовой прокат"],
        "norm_id": "ГОСТ 27772-2015",
        "section": "Прокат для стальных строительных конструкций. Общие технические условия",
        "requirement": "Требования к прокату (двутавры, швеллеры, уголки, листы) для стальных строительных конструкций: марки стали, механические характеристики, допуски, испытания",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["лстк", "тонкостенный профиль", "профиль холодногнутый", "оцинкованный профиль", "лёгкая стальная конструкц"],
        "norm_id": "СП 260.1325800.2016",
        "section": "Конструкции стальные тонкостенные из холодногнутых оцинкованных профилей",
        "requirement": "Проектирование и монтаж ЛСТК: расчёт профилей, узлы соединений, защита от коррозии, контроль качества монтажа",
        "confidence": "PARTIAL",
    },
    # --- Блок 5: Внутренняя отделка (расширение) ---
    {
        "keywords": ["гипсокартон", "гкл", "перегородка гкл", "подвесной потолок", "профиль cd", "профиль ud"],
        "norm_id": "СП 163.1325800.2014",
        "section": "Конструкции с применением гипсокартонных и гипсоволокнистых листов",
        "requirement": "Устройство перегородок, облицовок и подвесных потолков с применением ГКЛ: шаг стоек, крепление, зазоры, огнестойкость, звукоизоляция",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["лист гипсокартонный", "гипсокартон технические", "влагостойкий гкл", "огнестойкий гкл"],
        "norm_id": "ГОСТ 6266-2018",
        "section": "Листы гипсокартонные. Технические условия",
        "requirement": "Технические требования к гипсокартонным листам: типы (ГКЛ, ГКЛВ, ГКЛО), размеры, прочность на изгиб, влагостойкость, маркировка",
        "confidence": "PARTIAL",
    },
    # --- Блок 6: Фасады и тепловая защита ---
    {
        "keywords": ["тепловая защита", "утепление фасад", "теплопотери", "сопротивление теплопередач", "утеплитель стен"],
        "norm_id": "СП 50.13330.2012",
        "section": "Тепловая защита зданий",
        "requirement": "Требования к тепловой защите зданий: нормируемые значения сопротивления теплопередаче, воздухопроницаемости, защита от переувлажнения ограждающих конструкций",
        "confidence": "PARTIAL",
    },
    {
        "keywords": ["сфтк", "фасадная система", "навесной фасад", "вентилируемый фасад", "штукатурный фасад", "утепление стен снаружи"],
        "norm_id": "СП 293.1325800.2017",
        "section": "Системы фасадные теплоизоляционные композиционные с наружными штукатурными слоями",
        "requirement": "Проектирование и монтаж СФТК: состав системы, крепление утеплителя, армирующий слой, декоративное покрытие, контроль адгезии и геометрии",
        "confidence": "PARTIAL",
    },
    {
```

### TOPIC_FILE_INLINE
```
# topic_5 TEKHNADZOR

GENERATED_AT: 2026-05-08T18:45:02.614068+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 5
ROLE: Технадзор
DIRECTIONS_BOUND: technical_supervision
CURRENT_STATUS: IDLE_NO_FAILURES_NOT_VERIFIED
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- ARCHIVED: 21
- CANCELLED: 25
- DONE: 68
- FAILED: 53

## LATEST_FAILED
- 775a2251 | STALE_NEW_30MIN
- f3637754 | STALE_NEW_30MIN
- ddfc12b1 | PATCH_TOPIC2_UNBLOCK_PICK_NEXT_V1_CLOSED_BLOCKER
- 24ffa14f | INVALID_PUBLIC_RESULT
- 8093deb3 | INVALID_PUBLIC_RESULT

## COMMITS_LAST_14D
- 7c646dd|session(08.05): bigfile activated, topic5 V3 dispatcher, topic2 P6C intercept, c94ec497 FAILED/NOT_PROVEN
- b3e5be7|fix(topic500): relax bad-result filter for adaptive output modes
- 0d6a9a4|fix(memory): ARCHIVE_DUPLICATE_GUARD_V1 + topic500 search pollution guard
- 3f53d3f|docs(handoff): update after topic500 adaptive output V1
- 0c15037|feat(topic500): adaptive output by intent mode (9 modes, V1)
- 48eed2e|fix(topic5): filter garbage from act — canon §4/§5 material filter
- bb8e971|fix(topic5): fix vision-blocked condition — {} is not None
- fb24e60|fix(topic5): vision-blocked fallback per canon §17 — DOCX from owner text
- 0e01878|fix(topic5): install python-docx + enable vision via EXTERNAL_PHOTO_ANALYSIS_ALLOWED env
- f28a106|fix(topic2/topic500): extend estimate pipeline, offer menu for drive_file, fix search result blocking
- 967c48f|fix(topic_2/topic_5): close logic gaps in smeta, voice, and act routing
- 4aa44eb|fix: close canon contours for topic_5/topic_2/topic_500
- 998b6ff|fix(topic5): require owner instruction for new files
- 6e85335|fix(topic5): route drive files through full canon guard
- 7abefb9|fix(topic5): clean address extraction regex
- 4d8d5d6|fix(topic5): close full technadzor context contour
- 52bf7b5|fix(topic5): continuous active folder packet
- d9eed5e|fix(topic5): move final gate before worker main
- 7e3bb3e|fix(topic5): final no-clarify gate
- 884ea78|fix(topic5): canon close active folder photo package
- 5b01524|fix(topic5): close technadzor photo reply buffer contour
- 80c6690|Revert "fix(topic5): bind bot replies to recent photo materials"
- 837cf22|fix(topic5): bind bot replies to recent photo materials
- 6588a62|Revert "fix(topic5): force telegram files into visit buffer"
- e934209|fix(topic5): force telegram files into visit buffer
- 46234f9|fix(topic5): bind active folder upload and reply voice material comments
- a277900|docs(normative): add shared normative context for topic_5 and topic_210
- 2deb7c8|docs(technadzor): finalize topic5 logic context and document output contract
- 1405fdb|CHAT EXPORT GPT_TOPIC5_FULL_CLOSE 2026-05-05
- ff753aa|feat(technadzor): P6H_PART_4 topic_5 hook + STT hallucination guard

## MARKERS_LAST_24H
- created:NEW
- reply_sent:topic5_reply_photo_comment_bound
- topic5_reply_photo_comment_bound
- reply_sent:topic5_package_status_continuous
- topic5_package_status_continuous
- reply_sent:topic5_final_act
- FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:TOPIC5_FINAL_ACT_GENERATED
- P8T5_SUPERSEDED_BY_CANONICAL_V2
- P8T5_CANCELLED_OLD_GARBAGE_ACT_V2
- TOPIC5_DRIVE_LINKS_SAVED
- TOPIC5_GARBAGE_FILTER_OK
- TOPIC5_ACT_STRUCTURE_OK
- TOPIC5_DEFECT_TABLE_OK
- TOPIC5_RECOMMENDATIONS_SECTION_OK
- TOPIC5_NORMATIVE_SECTION_OK
- TOPIC5_DOCX_CREATED
- TOPIC5_PDF_CREATED
- reply_sent:topic5_canonical_act_v3
- PATCH_TOPIC5_ACT_DISPATCH_V3:ACT_GENERATED

## BLOCKERS_FROM_NOT_CLOSED
- - topic_5 не тянет КЖ/АР без прямой команды

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 6
chats: 1

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## OWNER_REFERENCE_REGISTRY
loaded: True
items: 11

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days


```

## TOPIC_11_VIDEO

STATUS: UNKNOWN
ACTIVE: 0  FAILED_24H: 0
DIRECTIONS_BOUND: Видео

### LAST_FAILED (5)
- 6abb8aa0 | 2026-05-01 11:33:54 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS
- 83b52b32 | 2026-05-01 10:24:33 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS
- 6b8a3806 | 2026-05-01 12:42:05 | cannot access local variable 'ai_result' where it is not associated with a value
    history: state:FAILED
    history: state:IN_PROGRESS
    history: reply_sent:router_failed

### TOPIC_FILE_INLINE
```
# topic_11 VIDEO

GENERATED_AT: 2026-05-08T18:45:02.642509+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 11
ROLE: Видео
DIRECTIONS_BOUND: video_production
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- DONE: 1
- FAILED: 3

## LATEST_FAILED
- 6abb8aa0 | cannot access local variable 'ai_result' where it is not associated with a value
- 83b52b32 | cannot access local variable 'ai_result' where it is not associated with a value
- 6b8a3806 | cannot access local variable 'ai_result' where it is not associated with a value

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- (none)

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 0
chats: 0

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days


```

## TOPIC_210_PROEKTIROVANIE

STATUS: IDLE_NO_FAILURES_NOT_VERIFIED
ACTIVE: 0  FAILED_24H: 0
DIRECTIONS_BOUND: КЖ КМ

### LAST_FAILED (5)
- cfadbd05 | 2026-05-06 20:57:43 | INVALID_RESULT_GATE
    history: reply_sent:invalid_result
    history: state:FAILED
    history: result:Для создания нового проекта с полным набором разделов (АР, КР, КЖ, КД, КМ, КМД, ОВ, ВК, ЭО, Э
- b71a685b | 2026-05-06 20:32:40 | INVALID_RESULT_GATE
    history: reply_sent:invalid_result
    history: state:FAILED
    history: result:Понял. Буду использовать средние рыночные цены по СПб и ЛО на май 2026 года. 

Типовые расцен
- 6e34406d | 2026-05-06 20:31:44 | NO_VALID_ARTIFACT
    history: reply_sent:full_contour_guard_failed
    history: FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:NO_VALID_ARTIFACT
    history: FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:UPDATE_BLOCKED:NO_VALID_ARTIFACT
- eba6dc80 | 2026-05-06 20:31:31 | NO_VALID_ARTIFACT
    history: reply_sent:full_contour_guard_failed
    history: FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:NO_VALID_ARTIFACT
    history: FULL_CONSTRUCTION_FILE_CONTOUR_CANON_GUARD_V1:UPDATE_BLOCKED:NO_VALID_ARTIFACT
- 540a9ccc | 2026-05-06 20:31:23 | INVALID_RESULT_GATE
    history: reply_sent:invalid_result
    history: state:FAILED
    history: result:Для решения проблемы подтопления подвального этажа необходимо выполнить следующие мероприятия

### KEY_ENGINE_CODE (head 250 lines each)
#### core/project_engine.py
```python
# === PROJECT_ENGINE_V1 ===
"""
core/project_engine.py
Разработка проектной документации по нормам ГОСТ/СНиП/СП
на основе шаблонов пользователя.
Разрешение на создание получено: 29.04.2026
"""
import os, re, logging, tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

SECTION_MAP = {
    "кж":  "КЖ — Конструкции железобетонные",
    "км":  "КМ — Конструкции металлические",
    "кмд": "КМД — Конструкции металлические деталировочные",
    "ар":  "АР — Архитектурные решения",
    "ов":  "ОВ — Отопление и вентиляция",
    "вк":  "ВК — Водоснабжение и канализация",
    "эом": "ЭОМ — Электроосвещение",
    "сс":  "СС — Слаботочные системы",
    "гп":  "ГП — Генеральный план",
    "пз":  "ПЗ — Пояснительная записка",
    "см":  "СМ — Смета",
    "тх":  "ТХ — Технологические решения",
}

SECTION_STRUCTURE = {
    "кж":  ["Армирование", "Схемы", "Спецификация арматуры", "Спецификация материалов"],
    "км":  ["Нагрузки", "Узлы сопряжений", "Спецификация металла"],
    "кмд": ["Деталировка", "Узлы", "Спецификация"],
    "ар":  ["Планы этажей", "Фасады", "Разрезы", "Экспликация помещений"],
    "ов":  ["Схема системы", "Расчёт нагрузок", "Спецификация оборудования"],
    "вк":  ["Схема водоснабжения", "Схема канализации", "Спецификация"],
    "эом": ["Однолинейная схема", "Расчёт нагрузок", "Спецификация"],
}

NORMS_MAP = {
    "кж":  ["СП 63.13330.2018", "ГОСТ 34028-2016", "СП 20.13330.2017"],
    "км":  ["СП 16.13330.2017", "ГОСТ 27772-2015", "СП 20.13330.2017"],
    "ар":  ["СП 118.13330.2022", "ГОСТ 21.501-2018"],
    "ов":  ["СП 60.13330.2020", "ГОСТ 30494-2011"],
    "вк":  ["СП 30.13330.2020", "СП 31.13330.2021"],
    "эом": ["СП 256.1325800.2016", "ПУЭ-7"],
}

SNOW_LOADS = {1: 0.8, 2: 1.2, 3: 1.8, 4: 2.4, 5: 3.2, 6: 4.0, 7: 4.8, 8: 5.6}
WIND_LOADS = {1: 0.17, 2: 0.23, 3: 0.30, 4: 0.38, 5: 0.48, 6: 0.60, 7: 0.73, 8: 0.85}

SPEC_HEADERS = ["№", "Наименование", "Марка/Обозначение", "Ед. изм.", "Кол-во", "Примечание"]
UNITS = {"мм", "м", "м2", "м3", "кг", "т", "шт", "пог.м"}


def detect_section(file_name: str, text: str = "") -> Optional[str]:
    # FULLFIX_02_B1: filename-first section priority
    fn = (file_name or "").lower()
    for key in SECTION_MAP:
        if key in fn:
            return key
    src = ((file_name or "") + " " + (text or "")).lower()
    for key in SECTION_MAP:
        if key in src:
            return key
    return None


def calc_loads(region: int = 3) -> Dict[str, float]:
    return {
        "snow_kPa":  SNOW_LOADS.get(region, 1.8),
        "wind_kPa":  WIND_LOADS.get(region, 0.30),
        "region":    region,
        "note":      f"СП 20.13330.2017 — район {region}",
    }


def normalize_unit(unit: str) -> str:
    u = str(unit or "").strip().lower()
    mapping = {"м2": "м2", "м²": "м2", "м3": "м3", "м³": "м3", "кг": "кг", "т": "т", "шт": "шт", "м": "м", "мм": "мм"}
    return mapping.get(u, u)


def build_specification(items: List[Dict]) -> List[List]:
    rows = [SPEC_HEADERS]
    for i, item in enumerate(items, 1):
        rows.append([
            i,
            item.get("name", ""),
            item.get("mark", ""),
            normalize_unit(item.get("unit", "")),
            item.get("qty", ""),
            item.get("note", ""),
        ])
    return rows


def _write_project_xlsx(section: str, items: List[Dict], loads: Dict, task_id: str) -> str:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    wb = Workbook()
    ws = wb.active
    ws.title = section.upper()

    ws.merge_cells("A1:F1")
    ws["A1"] = SECTION_MAP.get(section, section.upper())
    ws["A1"].font = Font(bold=True, size=13)
    ws["A1"].alignment = Alignment(horizontal="center")

    norms = NORMS_MAP.get(section, [])
    ws["A2"] = "Нормы: " + ", ".join(norms) if norms else ""

    if section in ("кж", "км", "кмд"):
        ws["A3"] = f"Снег: {loads['snow_kPa']} кПа | Ветер: {loads['wind_kPa']} кПа | {loads['note']}"

    spec = build_specification(items)
    start_row = 5
    for r_idx, row in enumerate(spec, start_row):
        for c_idx, val in enumerate(row, 1):
            cell = ws.cell(r_idx, c_idx, value=val)
            if r_idx == start_row:
                cell.font = Font(bold=True)
                cell.fill = PatternFill("solid", fgColor="DDEEFF")

    struct = SECTION_STRUCTURE.get(section, [])
    if struct:
        ws.cell(start_row + len(spec) + 2, 1, "Состав раздела:")
        for i, s in enumerate(struct, 1):
            ws.cell(start_row + len(spec) + 2 + i, 1, f"{i}. {s}")

    tmp = os.path.join(tempfile.gettempdir(), f"project_{section}_{task_id}.xlsx")
    wb.save(tmp)
    return tmp


async def generate_project_section(section: str, items: List[Dict], task_id: str, topic_id: int, region: int = 3) -> Dict[str, Any]:
    res = {"success": False, "excel_path": None, "drive_link": None, "section": section, "error": None}
    try:
        loads = calc_loads(region)
        xl = _write_project_xlsx(section, items, loads, task_id)
        res["excel_path"] = xl

        from core.engine_base import upload_artifact_to_drive, quality_gate
        qg = quality_gate(xl, task_id, "excel")
        if not qg["passed"]:
            res["error"] = f"QualityGate: {qg['errors']}"
            return res

        link = upload_artifact_to_drive(xl, task_id, topic_id)
        if link:
            res["drive_link"] = link
            res["success"] = True
        else:
            res["error"] = "UPLOAD_FAILED"
    except Exception as e:
        logger.error(f"project_engine: {e}", exc_info=True)
        res["error"] = str(e)[:300]
    return res


def project_result_guard(result: Dict) -> Dict:
    if not result.get("success"):
        return result
    if not result.get("excel_path") and not result.get("drive_link"):
        result["success"] = False
        result["error"] = "PROJECT_RESULT_GUARD: нет артефакта"
    return result


async def process_project_file(file_path: str, task_id: str, topic_id: int, raw_input: str = "") -> Dict[str, Any]:
    section = detect_section(file_path, raw_input) or "кж"
    items = []

    try:
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in (table or []):
                            if row and any(row):
                                items.append({
                                    "name": str(row[0] or ""),
                                    "mark": str(row[1] or "") if len(row) > 1 else "",
                                    "unit": str(row[2] or "") if len(row) > 2 else "",
                                    "qty":  str(row[3] or "") if len(row) > 3 else "",
                                })
        elif ext in (".xlsx", ".xls"):
            from openpyxl import load_workbook
            wb = load_workbook(file_path, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row and any(v for v in row if v):
                    items.append({
                        "name": str(row[0] or ""),
                        "mark": str(row[1] or "") if len(row) > 1 else "",
                        "unit": str(row[2] or "") if len(row) > 2 else "",
                        "qty":  str(row[3] or "") if len(row) > 3 else "",
                    })
            wb.close()
    except Exception as e:
        logger.warning(f"project extract: {e}")

    result = await generate_project_section(section, items, task_id, topic_id)
    return project_result_guard(result)
# === END_PROJECT_ENGINE_V1 ===

# === CODE_CLOSE_V43_PROJECT_ENGINE ===

def normative_search_engine_v43(section: str, query: str = ""):
    base = NORMS_MAP.get(section, [])
    if base:
        return {"success": True, "norms": base, "source": "local_norms_map"}
    return {"success": False, "norms": [], "error": "норма не подтверждена"}

def project_validator_v43(result):
    if not isinstance(result, dict):
        return False, "PROJECT_VALIDATOR: empty"
    if result.get("success") is False:
        return False, str(result.get("error") or "PROJECT_VALIDATOR: failed")
    if not (result.get("drive_link") or result.get("excel_path") or result.get("docx_path") or result.get("pdf_path")):
        return False, "PROJECT_VALIDATOR: no_artifact"
    return True, ""

def metal_structure_engine_v43(items, region=3):
    loads = calc_loads(region)
    spec = []
    for item in items or []:
        name = str(item.get("name") or "")
        if any(x in name.lower() for x in ("колонна","балка","ферма","связь","прогон")):
            spec.append(item)
    return {"loads": loads, "items": spec, "norms": NORMS_MAP.get("км", [])}

def project_result_guard_v43(result):
    ok, reason = project_validator_v43(result)
    if not ok:
        result = result if isinstance(result, dict) else {}
        result["success"] = False
        result["error"] = reason
    return result

try:
    _v43_orig_generate_project_section = generate_project_section
    async def generate_project_section(section, items, task_id, topic_id, region=3):
        res = await _v43_orig_generate_project_section(section, items, task_id, topic_id, region)
        res["normative_search"] = normative_search_engine_v43(section)
        if section in ("км","кмд"):
            res["metal_structure"] = metal_structure_engine_v43(items, region)
        return project_result_guard_v43(res)
```

#### core/cad_project_engine.py
```python
# === FULLFIX_07_CAD_PROJECT_DOCUMENTATION_CLOSURE ===
import os
import re
import json
import math
import glob
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE = "/root/.areal-neva-core"
TEMPLATE_DIR = f"{BASE}/data/project_templates"

ENGINE = "FULLFIX_07_CAD_PROJECT_DOCUMENTATION_CLOSURE"

DEFAULT_FOUNDATION_SHEETS = [
    {"mark": "КЖ", "number": "0", "title": "Титульный лист"},
    {"mark": "КЖ", "number": "1", "title": "Общие данные"},
    {"mark": "КЖ", "number": "2", "title": "Ведомость листов"},
    {"mark": "КЖ", "number": "3", "title": "План фундаментной плиты"},
    {"mark": "КЖ", "number": "4", "title": "Разрез 1-1"},
    {"mark": "КЖ", "number": "5", "title": "Схема нижнего армирования"},
    {"mark": "КЖ", "number": "6", "title": "Схема верхнего армирования"},
    {"mark": "КЖ", "number": "7", "title": "Узлы и детали"},
    {"mark": "КЖ", "number": "8", "title": "Спецификация материалов"},
    {"mark": "КЖ", "number": "9", "title": "Ведомость расхода стали"},
]

DEFAULT_ROOF_SHEETS = [
    {"mark": "КД", "number": "0", "title": "Титульный лист"},
    {"mark": "КД", "number": "1", "title": "Общие данные"},
    {"mark": "КД", "number": "2", "title": "Ведомость листов"},
    {"mark": "КД", "number": "3", "title": "План кровли"},
    {"mark": "КД", "number": "4", "title": "План стропильной системы"},
    {"mark": "КД", "number": "5", "title": "Разрезы"},
    {"mark": "КД", "number": "6", "title": "Узлы кровли"},
    {"mark": "КД", "number": "7", "title": "Спецификация древесины"},
    {"mark": "КД", "number": "8", "title": "Спецификация крепежа"},
]

NORMATIVE_NOTES = [
    "СП 63.13330.2018 Бетонные и железобетонные конструкции",
    "СП 20.13330.2016 Нагрузки и воздействия",
    "ГОСТ 21.501-2018 Правила выполнения рабочей документации архитектурных и конструктивных решений",
    "ГОСТ 21.101-2020 Основные требования к проектной и рабочей документации",
    "ГОСТ 34028-2016 Прокат арматурный для железобетонных конструкций",
]

REBAR_WEIGHT_KG_M = {
    6: 0.222,
    8: 0.395,
    10: 0.617,
    12: 0.888,
    14: 1.21,
    16: 1.58,
    18: 2.00,
    20: 2.47,
    22: 2.98,
    25: 3.85,
}

def _clean(v: Any, limit: int = 10000) -> str:
    return str(v or "").replace("\x00", " ").strip()[:limit]

def _safe_name(v: Any) -> str:
    s = re.sub(r"[^A-Za-zА-Яа-я0-9_.-]+", "_", _clean(v, 80))
    return s.strip("_") or "project"

def _font_name() -> str:
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
        for path in candidates:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont("ArealSans", path))
                return "ArealSans"
    except Exception:
        pass
    return "Helvetica"

def _load_templates() -> List[Dict[str, Any]]:
    out = []
    for p in sorted(glob.glob(f"{TEMPLATE_DIR}/PROJECT_TEMPLATE_MODEL__*.json"), key=os.path.getmtime, reverse=True):
        try:
            data = json.loads(Path(p).read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data["template_file"] = p
                out.append(data)
        except Exception:
            pass
    return out

def _choose_template(section: str, topic_id: int = 0) -> Dict[str, Any]:
    templates = _load_templates()
    if not templates:
        return {}
    section = _clean(section).upper()
    for tpl in templates:
        if topic_id and int(tpl.get("topic_id", 0) or 0) == int(topic_id) and _clean(tpl.get("project_type")).upper() == section:
            return tpl
    for tpl in templates:
        if _clean(tpl.get("project_type")).upper() == section:
            return tpl
    return templates[0]

def _num(text: str, default: float) -> float:
    try:
        return float(str(text).replace(",", "."))
    except Exception:
        return default

def _parse_mm(text: str, patterns: List[str], default: int) -> int:
    low = text.lower()
    for pat in patterns:
        m = re.search(pat, low, re.I)
        if m:
            return int(float(m.group(1).replace(",", ".")))
    return default

def parse_project_request(raw_input: str, template_hint: str = "") -> Dict[str, Any]:
    text = _clean(raw_input + " " + template_hint, 6000)
    low = text.lower()

    section = "КЖ"
    project_kind = "foundation_slab"
    if any(x in low for x in ["кров", "строп", "кд"]):
        section = "КД"
        project_kind = "roof"
    if any(x in low for x in [" ар ", "ар.", "архитект", "планиров", "фасад"]):  # SECTION_DETECTION_FIX_V1
        section = "АР"
        project_kind = "architectural"

    length_m = 10.0
    width_m = 10.0
    m = re.search(r"(\d+(?:[,.]\d+)?)\s*[xх×]\s*(\d+(?:[,.]\d+)?)\s*(?:м|m)?", low)
    if m:
        length_m = _num(m.group(1), 10.0)
        width_m = _num(m.group(2), 10.0)

    slab_mm = _parse_mm(low, [
        r"толщин[аы]?\D{0,30}(\d{2,4})\s*мм",
        r"плит[аы]?\D{0,30}(\d{2,4})\s*мм",
        r"бетон\D{0,30}(\d{2,4})\s*мм",
    ], 250)

    sand_mm = _parse_mm(low, [
        r"песчан\D{0,30}(\d{2,4})\s*мм",
        r"песок\D{0,30}(\d{2,4})\s*мм",
    ], 300)

    gravel_mm = _parse_mm(low, [
        r"щеб[её]н\D{0,30}(\d{2,4})\s*мм",
        r"щебень\D{0,30}(\d{2,4})\s*мм",
        r"основан\D{0,30}(\d{2,4})\s*мм",
    ], 150)

    rebar_step_mm = _parse_mm(low, [
        r"шаг\D{0,30}(\d{2,4})\s*мм",
        r"арматур\D{0,40}(\d{2,4})\s*мм",
    ], 200)

    rebar_diam_mm = 12
    md = re.search(r"(?:ø|ф|d|диаметр)\s*(\d{1,2})", low, re.I)
    if md:
        rebar_diam_mm = int(md.group(1))
    else:
        md = re.search(r"арматур[аы]?\D{0,30}(\d{1,2})(?!\d)", low, re.I)
        if md:
            rebar_diam_mm = int(md.group(1))

    concrete_class = "B25"
    mc = re.search(r"\b[вb]\s?(\d{2,3}(?:[,.]\d)?)\b", text, re.I)
    if mc:
        concrete_class = "B" + mc.group(1).replace(",", ".")

    rebar_class = "A500"
    mr = re.search(r"\b[аa]\s?500[сc]?\b", text, re.I)
    if mr:
        rebar_class = "A500C" if "c" in mr.group(0).lower() or "с" in mr.group(0).lower() else "A500"

    return {
        "project_name": "Проект фундаментной плиты" if project_kind == "foundation_slab" else "Проект по образцу",
        "project_kind": project_kind,
        "section": section,
        "length_m": length_m,
        "width_m": width_m,
        "slab_mm": slab_mm,
        "sand_mm": sand_mm,
        "gravel_mm": gravel_mm,
        "rebar_diam_mm": rebar_diam_mm,
        "rebar_step_mm": rebar_step_mm,
        "rebar_class": rebar_class,
        "concrete_class": concrete_class,
        "cover_mm": 40,
        "input": raw_input,
    }

def _normalize_sheet_register(template: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, str]]:
    section = data.get("section") or "КЖ"
    raw = template.get("sheet_register") or []
    sheets: List[Dict[str, str]] = []
    seen = set()

    for i, sh in enumerate(raw, 1):
        if isinstance(sh, dict):
            title = _clean(sh.get("title") or sh.get("name") or sh.get("sheet") or "", 120)
            number = _clean(sh.get("number") or sh.get("num") or str(i), 20)
            mark = _clean(sh.get("mark") or section, 20)
        else:
            title = _clean(sh, 120)
            number = str(i)
            mark = section
        if not title:
            continue
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        sheets.append({"mark": mark, "number": number, "title": title})

    sections = template.get("sections") or []
    if len(sheets) < 6 and sections:
        keys = ["общие", "ведомость", "план", "разрез", "армир", "спецификац", "узел", "фасад", "схема"]
        for sec in sections:
            title = _clean(sec, 120)
            if not title:
                continue
            low = title.lower()
            if not any(k in low for k in keys):
                continue
            if low in seen:
                continue
            seen.add(low)
            sheets.append({"mark": section, "number": str(len(sheets) + 1), "title": title})
            if len(sheets) >= 12:
                break

    base = DEFAULT_ROOF_SHEETS if data.get("project_kind") == "roof" else DEFAULT_FOUNDATION_SHEETS
    for sh in base:
        low = sh["title"].lower()
        if low not in seen:
            sheets.append({"mark": section, "number": str(len(sheets)), "title": sh["title"]})
            seen.add(low)

```

### TOPIC_FILE_INLINE
```
# topic_210 PROEKTIROVANIE

GENERATED_AT: 2026-05-08T18:45:02.679304+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 210
ROLE: КЖ КМ
DIRECTIONS_BOUND: structural_design
CURRENT_STATUS: IDLE_NO_FAILURES_NOT_VERIFIED
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- ARCHIVED: 3
- CANCELLED: 28
- DONE: 81
- FAILED: 26

## LATEST_FAILED
- cfadbd05 | INVALID_RESULT_GATE
- b71a685b | INVALID_RESULT_GATE
- 6e34406d | NO_VALID_ARTIFACT
- eba6dc80 | NO_VALID_ARTIFACT
- 540a9ccc | INVALID_RESULT_GATE

## COMMITS_LAST_14D
- 9420d6a|fix(topic2): stroyka meta-confirm guard + reply chain + xlsx 15 cols + topic210 meta guard
- a277900|docs(normative): add shared normative context for topic_5 and topic_210
- bc58444|COMBINED_TOPIC2_AND_TOPIC210_CLOSE_V1: real topic2 estimate and cad section fix
- 10036c1|TOPIC_ISOLATION_V1: exclude topic_210_500 from FILE_TECH and restore drive scope

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- - topic_2 не тянет проектные образцы topic_210
- - topic_210 не тянет сметные артефакты как результат
- - проверить topic_210: "какие образцы есть по АР/КЖ/КД" должен показать список без создания файла
- - проверить topic isolation: topic_2 не должен показывать КЖ/АР файлы topic_210 без прямого запроса

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 10
chats: 1

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## OWNER_REFERENCE_REGISTRY
loaded: True
items: 11

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days


```

## TOPIC_500_VEB_POISK

STATUS: IDLE_NO_FAILURES_NOT_VERIFIED
ACTIVE: 0  FAILED_24H: 0
DIRECTIONS_BOUND: Интернет-поиск

### LAST_FAILED (5)
- 6719452a | 2026-05-06 19:40:59 | P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
    history: reply_sent:p6_topic500_bad_result
    history: P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
    history: P6_TOPIC500_DIRECT_SEARCH_MONOLITH_ROUTE
- 16129a0c | 2026-05-06 19:40:39 | P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
    history: reply_sent:p6_topic500_bad_result
    history: P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
    history: P6_TOPIC500_DIRECT_SEARCH_MONOLITH_ROUTE
- 58591d8f | 2026-05-05 23:33:25 | IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1
    history: IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1:FAILED
    history: STARTUP_RECOVERY_REPLY_SENT_GUARD_V1:DONE_SKIP_RECOVERY
    history: P6F_DAH_BLOCKED_DONE_NO_UPLOAD_OR_TG_HISTORY
- 7944bb2a | 2026-05-05 22:35:46 | P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
    history: reply_sent:p6_topic500_bad_result
    history: P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
    history: P6_TOPIC500_DIRECT_SEARCH_MONOLITH_ROUTE
- a6e666e8 | 2026-05-05 22:35:40 | IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1
    history: IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1:FAILED
    history: STARTUP_RECOVERY_REPLY_SENT_GUARD_V1:DONE_SKIP_RECOVERY
    history: P6F_DAH_BLOCKED_DONE_NO_UPLOAD_OR_TG_HISTORY

### KEY_ENGINE_CODE (head 250 lines each)
#### core/search_session.py
```python
# === SEARCH_MONOLITH_V2_FULL ===
from __future__ import annotations
import json, logging, os, re, sqlite3, time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("search_session")
BASE = "/root/.areal-neva-core"
MEM_DB = f"{BASE}/data/memory.db"
SEARCH_SESSION_VERSION = "SEARCH_MONOLITH_V2_FULL"
SESSION_TTL_SEC = 7200
MAX_CLARIFICATIONS = 3
RED_FLAGS = ("цена=1","1 руб","договорная","под заказ","нет телефона","нет адреса","только предоплата","без адреса","нет даты","предоплата 100%")
SEARCH_PROFILES = {
    "BUILDING_SUPPLY": ["Ozon","Wildberries","Яндекс Маркет","Петрович","Лемана","ВсеИнструменты","заводы","Avito","VK","Telegram"],
    "AUTO_PARTS": ["OEM cross","Exist","Emex","ZZap","Drom","Auto.ru","EuroAuto","Avito","разборки","Telegram"],
    "CLASSIFIEDS": ["Avito","Юла","VK","Telegram чаты","2ГИС"],
    "GENERAL": ["официальные сайты","маркетплейсы","Avito","2ГИС"],
}
BUILDING_WORDS = ("металлочереп","монтеррей","профлист","утепл","бетон","арматур","цемент","фанер","доска","брус","кровл","кирпич","газобетон","строй","петрович","лемана","всеинструменты","материал")
AUTO_WORDS = ("oem","артикул","запчаст","суппорт","диск","колод","рычаг","стойк","двигател","коробк","бампер","фара","drom","дром","exist","emex","zzap","авто","машин","разбор")
CLASSIFIED_WORDS = ("авито","avito","юла","б/у","бу","объявлен","частник")

def _utc(): return datetime.now(timezone.utc).isoformat()
def _clean(text, limit=12000):
    if text is None: return ""
    if not isinstance(text, str):
        try: text = json.dumps(text, ensure_ascii=False)
        except: text = str(text)
    return re.sub(r"\n{3,}","\n\n",re.sub(r"[ \t]+"," ",text.replace("\r","\n"))).strip()[:limit]
def _safe_int(v, default=0):
    try: return int(v or 0)
    except: return default

@dataclass
class SearchSession:
    chat_id: str; topic_id: int; goal: str
    criteria: Dict[str,Any] = field(default_factory=dict)
    clarifications: List[str] = field(default_factory=list)
    queries: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    best_suppliers: List[Dict[str,Any]] = field(default_factory=list)
    rejected: List[Dict[str,Any]] = field(default_factory=list)
    status: str = "ACTIVE"
    created_at_ts: float = field(default_factory=time.time)
    updated_at: str = field(default_factory=_utc)
    def to_dict(self):
        d = asdict(self); d["version"] = SEARCH_SESSION_VERSION; return d
    @staticmethod
    def from_dict(data):
        return SearchSession(chat_id=str(data.get("chat_id") or ""), topic_id=_safe_int(data.get("topic_id")), goal=str(data.get("goal") or ""), criteria=dict(data.get("criteria") or {}), clarifications=list(data.get("clarifications") or []), queries=list(data.get("queries") or []), sources=list(data.get("sources") or []), best_suppliers=list(data.get("best_suppliers") or []), rejected=list(data.get("rejected") or []), status=str(data.get("status") or "ACTIVE"), created_at_ts=float(data.get("created_at_ts") or time.time()), updated_at=str(data.get("updated_at") or _utc()))

class SearchSessionManager:
    def __init__(self, db_path=MEM_DB):
        self.db_path = db_path; self._ensure()
    def _conn(self):
        c = sqlite3.connect(self.db_path, timeout=20); c.row_factory = sqlite3.Row; return c
    def _ensure(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._conn() as c:
            c.execute("CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_mem_search ON memory(chat_id,key)")
            c.commit()
    def key(self, chat_id, topic_id): return f"topic_{int(topic_id)}_search_session_{chat_id}"
    def get(self, chat_id, topic_id):
        try:
            with self._conn() as c:
                row = c.execute("SELECT value FROM memory WHERE chat_id=? AND key=? ORDER BY timestamp DESC LIMIT 1", (str(chat_id), self.key(chat_id, topic_id))).fetchone()
            if not row: return None
            s = SearchSession.from_dict(json.loads(row["value"]))
            if s.status == "CLOSED" or time.time() - float(s.created_at_ts or 0) > SESSION_TTL_SEC: return None
            return s
        except Exception as e: logger.warning("SEARCH_V2_GET_ERR %s", e); return None
    def save(self, s):
        s.updated_at = _utc()
        k = self.key(s.chat_id, s.topic_id)
        v = json.dumps(s.to_dict(), ensure_ascii=False)[:50000]
        with self._conn() as c:
            c.execute("DELETE FROM memory WHERE chat_id=? AND key=?", (s.chat_id, k))
            c.execute("INSERT OR REPLACE INTO memory (id,chat_id,key,value,timestamp) VALUES (?,?,?,?,?)", (f"{s.chat_id}:{k}", s.chat_id, k, v, _utc()))
            c.commit()
    def get_or_create(self, chat_id, topic_id, goal, criteria=None):
        s = self.get(chat_id, topic_id)
        if s:
            if goal and goal != s.goal: s.clarifications.append(goal)
            if criteria: s.criteria.update({k:v for k,v in criteria.items() if v not in ("",None,[],{})})
            self.save(s); return s
        s = SearchSession(chat_id=str(chat_id), topic_id=int(topic_id or 0), goal=goal, criteria=criteria or {})
        self.save(s); return s
    def close(self, chat_id, topic_id):
        s = self.get(chat_id, topic_id)
        if s: s.status = "CLOSED"; self.save(s)

class CriteriaExtractor:
    def extract(self, text):
        t = _clean(text, 4000); low = t.lower(); c = {}
        c["category"] = self.detect_category(low)
        c["target"] = self.extract_target(t)
        r = re.search(r"(санкт-петербург|спб|питер|ленобласть|москва|мск|казань|екатеринбург|новосибирск)", low)
        if r: c["region"] = r.group(0)
        q = re.search(r"(\d+(?:[,.]\d+)?)\s*(шт|м2|м²|м3|м³|кг|т|пог\.?\s*м|п\.м|лист|упак|м\b)", low)
        if q: c["quantity"] = q.group(0)
        p = re.search(r"(?:до|не дороже|бюджет|максимум|за)\s*(\d[\d\s]{2,})\s*(?:руб|₽)?", low)
        if p: c["budget"] = p.group(1).replace(" ","")
        if "б/у" in low or re.search(r"\bбу\b", low): c["condition"] = "used"
        elif "нов" in low: c["condition"] = "new"
        ral = re.search(r"\bral\s*[\- ]?(\d{4})\b", low)
        if ral: c["ral"] = "RAL " + ral.group(1)
        th = re.search(r"(\d[,.]\d{1,2})\s*мм", low)
        if th: c["thickness_mm"] = th.group(1).replace(",",".")
        oem = re.search(r"\b([A-ZА-Я0-9]{4,}[-/ ]?[A-ZА-Я0-9]{2,})\b", t, re.I)
        if c["category"] == "AUTO_PARTS" and oem: c["oem_or_article"] = oem.group(1)
        return {k:v for k,v in c.items() if v not in ("",None,[],{})}
    def detect_category(self, low):
        if any(w in low for w in AUTO_WORDS): return "AUTO_PARTS"
        if any(w in low for w in BUILDING_WORDS): return "BUILDING_SUPPLY"
        if any(w in low for w in CLASSIFIED_WORDS): return "CLASSIFIEDS"
        return "GENERAL"
    def extract_target(self, text):
        t = _clean(text, 500)
        t = re.sub(r"^\[voice\]\s*","",t,flags=re.I)
        t = re.sub(r"^(найди|найти|поищи|поиск|сколько стоит|цена на|стоимость|подбери)\s+","",t,flags=re.I)
        return re.sub(r"\s+"," ",t).strip()[:220]

class ClarificationEngine:
    def ask(self, session):
        c = session.criteria; q = []
        if not c.get("target") or len(str(c.get("target"))) < 4: q.append("что именно искать")
        if c.get("category") == "AUTO_PARTS":
            if not c.get("oem_or_article"): q.append("OEM/артикул или машина/год/кузов")
            if not c.get("condition"): q.append("новое, контрактное или б/у")
            if not c.get("region"): q.append("город или доставка по РФ")
        elif c.get("category") == "BUILDING_SUPPLY":
            if not c.get("region"): q.append("город/район доставки")
            if "металлочереп" in str(c.get("target","")).lower() and not (c.get("ral") and c.get("thickness_mm")): q.append("толщина, RAL и покрытие")
            if not (c.get("quantity") or c.get("budget")): q.append("объём или бюджет")
        else:
            if not c.get("region"): q.append("город или доставка")
        already = len(session.clarifications)
        if already >= MAX_CLARIFICATIONS: return None
        q = q[:max(0, MAX_CLARIFICATIONS - already)]
        if not q: return None
        return "SEARCH_CLARIFICATION_REQUIRED:\n" + "\n".join(f"{i+1}. {x}" for i,x in enumerate(q))

class QueryExpander:
    def expand(self, session):
        goal = session.goal or session.criteria.get("target","")
        cat = session.criteria.get("category","GENERAL")
        region = session.criteria.get("region","")
        sources = SEARCH_PROFILES.get(cat, SEARCH_PROFILES["GENERAL"])
        base_parts = [goal]
        for k in ("ral","thickness_mm","oem_or_article","quantity","condition","budget"):
            if session.criteria.get(k): base_parts.append(str(session.criteria[k]))
        base = " ".join(base_parts).strip()
        queries = [base, f"{base} {region}".strip(), f"{base} купить {region}".strip(), f"{base} цена наличие {region}".strip(), f"{base} доставка {region}".strip()]
        for src in sources: queries.append(f"{base} {src} {region}".strip())
        seen = set(); out = []
        for q in queries:
            q = re.sub(r"\s+"," ",q).strip()
            if q and q.lower() not in seen: seen.add(q.lower()); out.append(q)
        return out[:14]

class SourcePlanner:
    def plan(self, category): return SEARCH_PROFILES.get(category, SEARCH_PROFILES["GENERAL"])

class RiskScorer:
    def score_text(self, text):
        low = text.lower()
        flags = [f for f in RED_FLAGS if f in low]
        has_src = "http" in low or "source_url" in low
        has_date = re.search(r"\b202[4-9]\b", low)
        if has_src and has_date and not flags: status,trust = "CONFIRMED",80
        elif has_src and not flags: status,trust = "PARTIAL",60
        elif flags: status,trust = "RISK",35
        else: status,trust = "UNVERIFIED",40
        return {"status":status,"trust_score":trust,"red_flags":flags}

class TcoCalculator:
    def instruction(self): return "TCO = цена + доставка + комиссия + добор + риск; если данных нет — НЕ ПОДТВЕРЖДЕНО"

class ResultRanker:
    def instruction(self): return "Ранжирование: CHEAPEST, MOST_RELIABLE, BEST_VALUE, FASTEST, RISK_CHEAP, REJECTED"

class SearchOutputFormatter:
    TABLE_HEADER = "Поставщик | Площадка | Тип | Город | Цена | Наличие | Доставка | TCO | Trust Score | Риски | Статус | Ссылка | checked_at"
    def build_prompt(self, session, queries, sources):
        return f"""SEARCH_MONOLITH_V2_FULL
ЦЕЛЬ: {session.goal}
КРИТЕРИИ: {json.dumps(session.criteria,ensure_ascii=False)}
ПЛОЩАДКИ: {", ".join(sources)}
ФОРМУЛИРОВКИ:\n{chr(10).join("- "+q for q in queries)}
ВЫВОД: {self.TABLE_HEADER}
После таблицы: 1.Что брать и почему 2.Что проверить звонком 3.Что отброшено 4.Данные не подтверждены
ПРАВИЛА: Не выдумывать цены/телефоны/адреса. Без source_url/даты — статус не выше PARTIAL. Красные флаги: {", ".join(RED_FLAGS)}""".strip()
    def ensure(self, text, risk):
        text = _clean(text, 12000)
        if self.TABLE_HEADER not in text: text = self.TABLE_HEADER + "\n" + text
        for h in ("1. Что брать и почему","2. Что проверить звонком","3. Что отброшено","4. Данные не подтверждены"):
            if h not in text: text += f"\n\n{h}\nНЕ ПОДТВЕРЖДЕНО"
        text += f"\n\nRiskScorer: {risk.get('status')} | Trust: {risk.get('trust_score')} | flags: {', '.join(risk.get('red_flags') or []) or 'нет'}"
        return text

class SearchMonolithV2:
    def __init__(self):
        self.sessions = SearchSessionManager(); self.extractor = CriteriaExtractor()
        self.clarifier = ClarificationEngine(); self.expander = QueryExpander()
        self.planner = SourcePlanner(); self.risk = RiskScorer()
        self.tco = TcoCalculator(); self.ranker = ResultRanker(); self.formatter = SearchOutputFormatter()
    def has_active_session(self, chat_id, topic_id): return self.sessions.get(chat_id, topic_id) is not None

    # === SEARCH_SESSION_ISOLATION_FIX_V1 ===
    def _is_new_search_goal(self, user_text, existing, extracted):
        low = _clean(user_text, 1000).lower()
        new_markers = ("найди ", "найти ", "поищи ", "поиск ", "подбери ", "сколько стоит ", "цена на ", "стоимость ")
        if not any(low.startswith(m) for m in new_markers):
            return False

        old_target = str((existing.criteria or {}).get("target") or existing.goal or "").lower()
        new_target = str((extracted or {}).get("target") or user_text or "").lower()
        old_cat = str((existing.criteria or {}).get("category") or "")
        new_cat = str((extracted or {}).get("category") or "")

        if old_cat and new_cat and old_cat != new_cat:
            return True

        old_words = set(w for w in re.findall(r"[а-яa-z0-9]{4,}", old_target) if w not in ("найди","найти","поищи","поиск","купить","цена","стоимость"))
        new_words = set(w for w in re.findall(r"[а-яa-z0-9]{4,}", new_target) if w not in ("найди","найти","поищи","поиск","купить","цена","стоимость"))

        if old_words and new_words:
            overlap = len(old_words & new_words)
            if overlap == 0:
                return True
            if overlap / max(1, min(len(old_words), len(new_words))) < 0.35:
                return True

        return False

    async def run(self, payload, user_text, online_call, online_model, base_system_prompt=""):
        chat_id = str(payload.get("chat_id") or ""); topic_id = int(payload.get("topic_id") or 0)
        user_text = _clean(user_text, 4000)
        existing = self.sessions.get(chat_id, topic_id)
        extracted = self.extractor.extract(user_text)

        if existing and self._is_new_search_goal(user_text, existing, extracted):
            try:
                existing.status = "CLOSED"
                self.sessions.save(existing)
                logger.info("SEARCH_SESSION_ISOLATION_FIX_V1 closed_old_session chat=%s topic=%s old_goal=%s new_goal=%s", chat_id, topic_id, existing.goal, user_text)
            except Exception as e:
```

#### core/search_engine.py
```python
# === FULLFIX_SEARCH_ENGINE_STAGE_5 ===
from __future__ import annotations
from typing import Any, Dict, List, Optional

SEARCH_ENGINE_VERSION = "SEARCH_ENGINE_V1"

DIRECTION_SEARCH_PROFILES = {
    "product_search":      {"sources": ["avito", "ozon", "wildberries"], "strategy": "price_compare"},
    "auto_parts_search":   {"sources": ["drom", "exist", "emex", "zzap"], "strategy": "compatibility"},
    "construction_search": {"sources": ["petrovitch", "lerua", "grand_line"], "strategy": "price_delivery"},
    "internet_search":     {"sources": ["web"], "strategy": "general"},
}

DEFAULT_PROFILE = {"sources": ["web"], "strategy": "general"}


class SearchEngine:
    def plan(self, work_item, payload: Dict[str, Any]) -> Dict[str, Any]:
        direction = getattr(work_item, "direction", None) or payload.get("direction") or "internet_search"
        raw_text = (getattr(work_item, "raw_text", "") or payload.get("raw_input") or "")[:500]
        profile = DIRECTION_SEARCH_PROFILES.get(direction, DEFAULT_PROFILE)

        plan = {
            "query": raw_text,
            "direction": direction,
            "sources": profile["sources"],
            "strategy": profile["strategy"],
            "engine_version": SEARCH_ENGINE_VERSION,
            "shadow_mode": True,
            "status": "planned",
        }
        return plan

    def apply_to_payload(self, work_item, payload: Dict[str, Any]) -> Dict[str, Any]:
        requires_search = bool((payload.get("direction_profile") or {}).get("requires_search"))
        if not requires_search:
            return {}
        plan = self.plan(work_item, payload)
        payload["search_plan"] = plan
        try:
            import logging
            logging.getLogger("task_worker").info(
                "FULLFIX_SEARCH_ENGINE_STAGE_5 dir=%s sources=%s strategy=%s",
                plan["direction"], plan["sources"], plan["strategy"]
            )
        except Exception:
            pass
        return plan


def plan_search(work_item, payload):
    return SearchEngine().apply_to_payload(work_item, payload)
# === END FULLFIX_SEARCH_ENGINE_STAGE_5 ===


# === P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1 ===
# Scope:
# - SearchEngine is no longer decorative shadow-only metadata
# - it produces normalized active search plan for product, auto parts, construction and general web search
# - no network call here; execution is handled by SearchMonolithV2 / ai_router online model

import re as _p6se_re

_P6SE_AUTO_WORDS = (
    "сайлентблок", "саленблок", "сальник", "пыльник", "ваз", "2110", "2114",
    "жигули", "лада", "приора", "гранта", "калина", "нива", "drom", "exist", "emex", "zzap",
    "автозапчаст", "запчаст", "oem", "артикул"
)

_P6SE_ELECTRONICS_WORDS = (
    "iphone", "айфон", "pixel", "google pixel", "телефон", "смартфон", "samsung", "galaxy",
    "xiaomi", "redmi", "honor", "huawei", "pro max", "xl"
)

_P6SE_BUILD_WORDS = (
    "утепл", "каменная вата", "rockwool", "бетон", "арматур", "профлист", "металлочереп",
    "фальц", "клик-фальц", "кирпич", "газобетон", "доска", "брус", "стройматериал"
)

def _p6se_s(v, limit=4000):
    try:
        if v is None:
            return ""
        return str(v).strip()[:limit]
    except Exception:
        return ""

def _p6se_low(v):
    return _p6se_s(v).lower().replace("ё", "е")

def _p6se_direction(raw_text, current="internet_search"):
    low = _p6se_low(raw_text)
    if any(x in low for x in _P6SE_AUTO_WORDS):
        return "auto_parts_search"
    if any(x in low for x in _P6SE_ELECTRONICS_WORDS):
        return "product_search"
    if any(x in low for x in _P6SE_BUILD_WORDS):
        return "construction_search"
    return current or "internet_search"

def _p6se_sources(direction):
    if direction == "auto_parts_search":
        return ["zzap", "exist", "emex", "drom", "auto.ru", "euroauto", "avito", "telegram"]
    if direction == "construction_search":
        return ["petrovich", "lerua", "vseinstrumenti", "ozon", "wildberries", "yandex_market", "avito", "2gis", "supplier_sites"]
    if direction == "product_search":
        return ["ozon", "wildberries", "yandex_market", "dns", "mvideo", "eldorado", "avito", "aliexpress", "official_sites"]
    return ["web", "official_sites", "marketplaces", "classifieds", "2gis"]

def _p6se_strategy(direction):
    if direction == "auto_parts_search":
        return "compatibility_price_availability"
    if direction == "construction_search":
        return "price_delivery_supplier_trust"
    if direction == "product_search":
        return "price_compare_availability"
    return "general_verified_search"

try:
    _p6se_orig_plan = SearchEngine.plan
    def _p6se_plan(self, work_item, payload):
        payload = payload or {}
        raw_text = (
            getattr(work_item, "raw_text", None)
            or payload.get("raw_input")
            or payload.get("normalized_input")
            or payload.get("query")
            or ""
        )
        current = getattr(work_item, "direction", None) or payload.get("direction") or "internet_search"
        direction = _p6se_direction(raw_text, current)
        sources = _p6se_sources(direction)
        plan = {
            "query": _p6se_s(raw_text, 1000),
            "direction": direction,
            "sources": sources,
            "strategy": _p6se_strategy(direction),
            "engine_version": "P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1",
            "shadow_mode": False,
            "status": "active",
            "requires_online": True,
            "must_use_current_query_only": True,
        }
        return plan
    SearchEngine.plan = _p6se_plan

    def _p6se_apply_to_payload(self, work_item, payload):
        payload = payload or {}
        plan = self.plan(work_item, payload)
        payload["search_plan"] = plan
        payload["direction"] = plan["direction"]
        payload["engine"] = "search_supplier"
        payload["requires_search"] = True
        payload["search_sources"] = plan["sources"]
        payload["search_strategy"] = plan["strategy"]
        try:
            import logging
            logging.getLogger("task_worker").info(
                "P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN dir=%s sources=%s strategy=%s",
                plan["direction"], plan["sources"], plan["strategy"]
            )
        except Exception:
            pass
        return plan
    SearchEngine.apply_to_payload = _p6se_apply_to_payload
except Exception:
    pass

# === END_P6_GLOBAL_SEARCH_ENGINE_ACTIVE_PLAN_20260504_V1 ===

# === P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1 ===
try:
    SEARCH_ENGINE_VERSION = "P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1"
    DIRECTION_SEARCH_PROFILES.update({
        "internet_search": {"sources": ["web", "marketplaces", "direct_suppliers"], "strategy": "current_query_price_compare"},
        "product_search": {"sources": ["ozon", "wildberries", "yandex_market", "avito", "direct_suppliers"], "strategy": "current_query_price_compare"},
        "auto_parts_search": {"sources": ["drom", "exist", "emex", "zzap", "avito"], "strategy": "current_query_compatibility_price"},
        "construction_search": {"sources": ["petrovich", "lemanapro", "vseinstrumenti", "direct_suppliers"], "strategy": "current_query_price_delivery"},
    })
except Exception:
    pass

try:
    _p6c_orig_plan_20260504 = SearchEngine.plan
    def _p6c_plan_20260504(self, work_item, payload):
        plan = _p6c_orig_plan_20260504(self, work_item, payload)
        plan["shadow_mode"] = False
        plan["status"] = "active"
        plan["engine_version"] = "P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1"
        return plan
    SearchEngine.plan = _p6c_plan_20260504
except Exception:
    pass
# === END_P6C_SEARCH_ENGINE_ACTIVE_NO_SHADOW_PROFILE_20260504_V1 ===
```

### TOPIC_FILE_INLINE
```
# topic_500 VEB_POISK

GENERATED_AT: 2026-05-08T18:45:02.713586+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 500
ROLE: Интернет-поиск
DIRECTIONS_BOUND: internet_search
CURRENT_STATUS: IDLE_NO_FAILURES_NOT_VERIFIED
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- ARCHIVED: 27
- CANCELLED: 7
- DONE: 55
- FAILED: 34

## LATEST_FAILED
- 6719452a | P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
- 16129a0c | P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
- 58591d8f | IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1
- 7944bb2a | P6_TOPIC500_BLOCKED_BAD_OR_STALE_SEARCH_RESULT
- a6e666e8 | IN_PROGRESS_HARD_TIMEOUT_BY_CREATED_AT_FIX_V1

## COMMITS_LAST_14D
- b3e5be7|fix(topic500): relax bad-result filter for adaptive output modes
- 0d6a9a4|fix(memory): ARCHIVE_DUPLICATE_GUARD_V1 + topic500 search pollution guard
- 3f53d3f|docs(handoff): update after topic500 adaptive output V1
- 0c15037|feat(topic500): adaptive output by intent mode (9 modes, V1)
- f28a106|fix(topic2/topic500): extend estimate pipeline, offer menu for drive_file, fix search result blocking
- 4aa44eb|fix: close canon contours for topic_5/topic_2/topic_500
- e3d992c|P6G_CLEAN_OLD_TOPIC500_CONTAMINATION_V1: SQL clean task 4883 contamination (point 1 of 5)
- 949c379|P6F_FULL_CODE_CLOSE_REMAINING_CONTOURS_20260504_V1: close revision binding, topic500 sanitizer, photo CV via OpenRouter, TZ params, source labels, technadzor DOCX, project_210 drive, artifact gates
- 709b28a|P3_FINAL_ROUTE_HARD_LOCK_SEARCH_ESTIMATE_20260504_V1: hard-lock topic500 search and topic2 current estimate route
- 4f6af26|P2_FINAL_SEARCH_AND_ESTIMATE_CLOSE_20260504_V1: close topic500 search memory and topic2 final estimate logic
- d4db3fb|P0_RUNTIME_ROUTE_GUARD_TOPIC2_TOPIC500_20260504_V1: block topic500 estimate misroute and force topic2 current estimate route
- bf6cece|TOPIC500_PRE_SEND_VALIDATOR_AND_STARTUP_RECOVERY_HARD_GUARD_V1: pre-send procurement validator and startup recovery hard guard
- dc2f770|FINAL_TOPIC2_TOPIC5_TOPIC500_CLOSE_20260504_V1: close topic2 current TZ route and topic500 search output contract
- a5cdb89|TOPIC2_ESTIMATE_AND_TOPIC500_SEARCH_FULLFIX_V1: strict template estimate pdf and bypass search misroute
- 19f619d|CANON_ROUTE_FIX_V3_TOPIC500_ISOLATION: skip file_context_intake for topic_500

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- (none)

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 1
chats: 1

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days


```

## TOPIC_794_DEVOPS

STATUS: UNKNOWN
ACTIVE: 0  FAILED_24H: 0
DIRECTIONS_BOUND: Сервер DevOps

### LAST_FAILED (5)
- d215f564 | 2026-05-01 11:32:54 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS
- 0a33135a | 2026-05-01 11:31:55 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS
- 89eabf76 | 2026-05-01 10:25:04 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS
- b96f8ca8 | 2026-05-01 10:24:54 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS

### TOPIC_FILE_INLINE
```
# topic_794 DEVOPS

GENERATED_AT: 2026-05-08T18:45:02.743728+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 794
ROLE: Сервер DevOps
DIRECTIONS_BOUND: devops_server
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- DONE: 3
- FAILED: 4

## LATEST_FAILED
- d215f564 | cannot access local variable 'ai_result' where it is not associated with a value
- 0a33135a | cannot access local variable 'ai_result' where it is not associated with a value
- 89eabf76 | cannot access local variable 'ai_result' where it is not associated with a value
- b96f8ca8 | cannot access local variable 'ai_result' where it is not associated with a value

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- (none)

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 0
chats: 0

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days


```

## TOPIC_961_AVTOZAPCHASTI

STATUS: UNKNOWN
ACTIVE: 0  FAILED_24H: 0
DIRECTIONS_BOUND: Автозапчасти

### LAST_FAILED (5)
- 8656edda | 2026-05-01 11:33:13 | PROJECT_LINKS_MISSING
    history: reply_sent:ff10_project_links_missing
    history: FULLFIX_10_PROJECT_LINKS_MISSING
    history: created:NEW
- 759c9f79 | 2026-05-01 10:24:09 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS
- 806068b2 | 2026-05-01 12:42:02 | cannot access local variable 'ai_result' where it is not associated with a value
    history: state:FAILED
    history: state:IN_PROGRESS
    history: state:FAILED

### TOPIC_FILE_INLINE
```
# topic_961 AVTOZAPCHASTI

GENERATED_AT: 2026-05-08T18:45:02.773821+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 961
ROLE: Автозапчасти
DIRECTIONS_BOUND: auto_parts_search
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- ARCHIVED: 13
- CANCELLED: 9
- DONE: 4
- FAILED: 3

## LATEST_FAILED
- 8656edda | PROJECT_LINKS_MISSING
- 759c9f79 | cannot access local variable 'ai_result' where it is not associated with a value
- 806068b2 | cannot access local variable 'ai_result' where it is not associated with a value

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- (none)

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 0
chats: 0

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days


```

## TOPIC_3008_KODY_MOZGOV

STATUS: UNKNOWN
ACTIVE: 0  FAILED_24H: 0
DIRECTIONS_BOUND: Мозги оркестра

### LAST_FAILED (5)
- 0ea6de76 | 2026-05-01 12:33:28 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS
- 867712fc | 2026-05-01 12:41:59 | cannot access local variable 'ai_result' where it is not associated with a value
    history: state:FAILED
    history: state:IN_PROGRESS
    history: state:FAILED

### TOPIC_FILE_INLINE
```
# topic_3008 KODY_MOZGOV

GENERATED_AT: 2026-05-08T18:45:02.807792+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 3008
ROLE: Мозги оркестра
DIRECTIONS_BOUND: orchestration_core
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- ARCHIVED: 9
- CANCELLED: 4
- DONE: 21
- FAILED: 2

## LATEST_FAILED
- 0ea6de76 | cannot access local variable 'ai_result' where it is not associated with a value
- 867712fc | cannot access local variable 'ai_result' where it is not associated with a value

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- (none)

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 0
chats: 0

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days


```

## TOPIC_4569_CRM_LEADS

STATUS: UNKNOWN
ACTIVE: 0  FAILED_24H: 0
DIRECTIONS_BOUND: CRM лиды

### LAST_FAILED (5)
- c860d224 | 2026-05-01 10:23:11 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS
- 4b47038e | 2026-05-01 02:14:27 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS
- c62c91d0 | 2026-05-01 02:14:16 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS
- 9f1c61ab | 2026-05-01 02:13:13 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS
- 48bdf7bc | 2026-05-01 02:13:03 | cannot access local variable 'ai_result' where it is not associated with a value
    history: reply_sent:router_failed
    history: state:FAILED
    history: state:IN_PROGRESS

### TOPIC_FILE_INLINE
```
# topic_4569 CRM_LEADS

GENERATED_AT: 2026-05-08T18:45:02.844817+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 4569
ROLE: CRM лиды
DIRECTIONS_BOUND: crm_leads
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- ARCHIVED: 5
- CANCELLED: 4
- DONE: 2
- FAILED: 14

## LATEST_FAILED
- c860d224 | cannot access local variable 'ai_result' where it is not associated with a value
- 4b47038e | cannot access local variable 'ai_result' where it is not associated with a value
- c62c91d0 | cannot access local variable 'ai_result' where it is not associated with a value
- 9f1c61ab | cannot access local variable 'ai_result' where it is not associated with a value
- 48bdf7bc | cannot access local variable 'ai_result' where it is not associated with a value

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- (none)

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 0
chats: 0

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days


```

## TOPIC_6104_JOB_SEARCH

STATUS: UNKNOWN
ACTIVE: 0  FAILED_24H: 0
DIRECTIONS_BOUND: Поиск работы

### LAST_FAILED (5)
- f371d22d | 2026-05-01 22:28:23 | INVALID_RESULT_GATE
    history: reply_sent:invalid_result
    history: state:FAILED
    history: result:В архиве чата найдены повторяющиеся запросы о первом запросе в данном чате. Однако конкретные
- 81355bcf | 2026-05-01 22:26:33 | INVALID_RESULT_GATE
    history: reply_sent:invalid_result
    history: state:FAILED
    history: result:На данный момент информация о первом запросе в этом чате отсутствует в архиве. Если требуется
- b07ceef8 | 2026-05-01 22:19:22 | FORBIDDEN_PHRASE
    history: ROLE_SAVED:поиска работы и интеграции с биржами труда
    history: result:Этот чат предназначен для поиска работы и интеграции с биржами труда. 

За последние 24 часа 
    history: result:За последние 24 часа в этом чате не было выполнено задач. История пуста. Если вам нужно что-т
- 711bdcd3 | 2026-05-01 22:19:04 | FORBIDDEN_PHRASE
    history: ROLE_SAVED:поиска работы и интеграции с биржами труда
    history: result:Этот чат предназначен для поиска работы и интеграции с биржами труда. История задач за послед
    history: reply_sent:result
- 32fe5a92 | 2026-05-01 11:36:19 | PROJECT_LINKS_MISSING
    history: reply_sent:ff10_project_links_missing
    history: FULLFIX_10_PROJECT_LINKS_MISSING
    history: created:NEW

### TOPIC_FILE_INLINE
```
# topic_6104 JOB_SEARCH

GENERATED_AT: 2026-05-08T18:45:02.881056+00:00
GIT_SHA: afdcfad39237ebaaf33b8947f0fdf1b8863db434
GENERATED_FROM: tools/full_context_aggregator.py

TOPIC_ID: 6104
ROLE: Поиск работы
DIRECTIONS_BOUND: job_search
CURRENT_STATUS: UNKNOWN
ACTIVE_TASKS: 0
FAILED_LAST_24H: 0

## DB_STATE_COUNTS
- CANCELLED: 1
- DONE: 3
- FAILED: 6

## LATEST_FAILED
- f371d22d | INVALID_RESULT_GATE
- 81355bcf | INVALID_RESULT_GATE
- b07ceef8 | FORBIDDEN_PHRASE
- 711bdcd3 | FORBIDDEN_PHRASE
- 32fe5a92 | PROJECT_LINKS_MISSING

## COMMITS_LAST_14D
- (none matching topic)

## MARKERS_LAST_24H
- (none)

## BLOCKERS_FROM_NOT_CLOSED
- - P2: topic_6104 архив содержит только JSON метаданные без реального контента

## RUNTIME_FILE_CATALOG_SUMMARY
total_files: 0
chats: 0

## DRIVE_UPLOAD_CONTRACT
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## FORBIDDEN_FILES
- .env
- credentials
- sessions/
- core/ai_router.py
- core/reply_sender.py
- core/google_io.py
- task_worker.py
- telegram_daemon.py
- data/core.db
- data/memory.db

## FACT_SOURCE_LIST
- core.db live state and task_history
- config/directions.yaml via core.direction_registry.DirectionRegistry
- core/runtime_file_catalog.py
- config/estimate_template_registry.json
- config/owner_reference_registry.json
- data/templates/reference_monolith/owner_reference_full_index.json
- docs/REPORTS/NOT_CLOSED.md
- docs/HANDOFFS/LATEST_HANDOFF.md
- git log last 14 days


```

================================================================================
# 6. PER_DIRECTION
================================================================================

## general_chat
engine: ai_router
topic_ids: []
input_types: ['text', 'voice']
output_formats: ['telegram_text']
quality_gates: ['non_empty_answer']
aliases: []

## orchestration_core
engine: ai_router
topic_ids: [3008]
input_types: ['text', 'voice', 'file']
output_formats: ['telegram_text', 'json', 'md']
quality_gates: ['canon_consistency']
aliases: ['оркестр', 'канон', 'kernel', 'workitem', 'direction', 'архитектур']

## telegram_automation
engine: telegram_pipeline
topic_ids: []
input_types: ['text', 'voice']
output_formats: ['telegram_text']
quality_gates: ['reply_thread_required']
aliases: ['bot_message_id', 'message_thread_id', 'telegram daemon']

## memory_archive
engine: context_search_archive_engine
topic_ids: []
input_types: ['text', 'file']
output_formats: ['telegram_text', 'json']
quality_gates: ['verified_sources_only']
aliases: ['chat_exports', 'выгрузк', 'архив', 'memory.db', 'short_memory', 'long_memory']

## internet_search
engine: search_supplier
topic_ids: [500]
input_types: ['text', 'voice']
output_formats: ['telegram_text', 'table', 'sources']
quality_gates: ['sources_required']
aliases: ['найд', 'поиск', 'перплексити', 'в интернете']

## product_search
engine: search_supplier
topic_ids: []
input_types: ['text', 'voice', 'photo']
output_formats: ['telegram_table', 'json', 'xlsx']
quality_gates: ['price_required', 'source_required', 'tco_required']
aliases: ['куп', 'цен', 'дешевл', 'товар', 'поставщик', 'заказ']

## auto_parts_search
engine: search_supplier
topic_ids: [961]
input_types: ['text', 'voice', 'photo']
output_formats: ['telegram_table', 'json']
quality_gates: ['compatibility_required']
aliases: ['авто', 'запчаст', 'фара', 'рычаг', 'суппорт', 'oem', 'разборк', 'toyota', 'hiace']

## construction_search
engine: search_supplier
topic_ids: []
input_types: ['text', 'voice', 'photo']
output_formats: ['telegram_table', 'xlsx']
quality_gates: ['price_required', 'delivery_required']
aliases: ['металлочерепиц', 'профнастил', 'газобетон', 'утеплител', 'арматур', 'ral', 'grand line', 'петрович', 'леруа']

## technical_supervision
engine: defect_act
topic_ids: [5]
input_types: ['text', 'voice', 'photo', 'file']
output_formats: ['telegram_text', 'docx', 'pdf']
quality_gates: ['defect_description_required', 'normative_section_required']
aliases: ['технадзор', 'наруш', 'дефект', 'осмотр', 'замечан', 'снип', 'гост']

## estimates
engine: estimate_unified
topic_ids: [2]
input_types: ['text', 'voice', 'file', 'drive_file']
output_formats: ['xlsx', 'pdf', 'drive_link', 'telegram_text']
quality_gates: ['items_required', 'total_required', 'xlsx_required']
aliases: ['смет', 'расценк', 'ведомост', 'объем работ', 'вор', 'фер', 'тер']

## defect_acts
engine: defect_act
topic_ids: []
input_types: ['text', 'voice', 'photo', 'file']
output_formats: ['docx', 'pdf', 'drive_link']
quality_gates: ['document_required']
aliases: ['акт дефект', 'акт осмотр', 'дефектный акт', 'трещин', 'протечк', 'фото дефект']

## documents
engine: document_engine
topic_ids: []
input_types: ['text', 'voice', 'file', 'drive_file']
output_formats: ['docx', 'pdf', 'drive_link']
quality_gates: ['document_output_required']
aliases: ['docx', 'документ word', 'напиши письмо', 'напиши отчет', 'напиши отчёт']

## spreadsheets
engine: sheets_route
topic_ids: []
input_types: ['text', 'voice', 'file', 'drive_file']
output_formats: ['xlsx', 'google_sheet', 'csv', 'drive_link']
quality_gates: ['table_required']
aliases: ['xlsx', 'excel таблиц', 'google sheets', 'гугл таблиц', 'csv файл']

## google_drive_storage
engine: drive_storage
topic_ids: []
input_types: ['text', 'file', 'drive_file']
output_formats: ['drive_link', 'telegram_text']
quality_gates: ['drive_link_required']
aliases: ['загрузи на drive', 'залей на гугл диск', 'сохрани на drive']

================================================================================
# 7. SOURCE_LINKS
================================================================================

- TOPIC_STATUS_INDEX: docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md
- DIRECTION_STATUS_INDEX: docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md
- SAFE_RUNTIME_SNAPSHOT: docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md
- MANIFEST: docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json
- DirectionRegistry: core/direction_registry.py
- runtime_file_catalog: core/runtime_file_catalog.py
- topic_drive_oauth: core/topic_drive_oauth.py
- ORCHESTRA_FULL_CONTEXT_PARTS: 17 files (full project dump)

