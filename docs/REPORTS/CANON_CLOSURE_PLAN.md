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
