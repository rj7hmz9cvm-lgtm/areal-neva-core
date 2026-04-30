# NOT_CLOSED — 30.04.2026 UPDATE 10:00

## ЗАКРЫТО КОДОМ И VERIFIED (30.04.2026)

| Что | Файл | Патч | Статус |
|---|---|---|---|
| Drive upload OAuth | core/topic_drive_oauth.py + google_io.py + drive_folder_resolver.py | PATCH_SCOPE_FULL_V1 | VERIFIED ✅ |
| Daemon OAuth override | systemd telegram-ingress override.conf | PATCH_DAEMON_OAUTH_OVERRIDE_V1 | VERIFIED ✅ |
| File intake lifecycle | task_worker.py | мн. патчей | VERIFIED ✅ |
| upload_retry_queue | core/upload_retry_queue.py | PATCH_RETRY_TOPIC_FOLDER_V1 | VERIFIED ✅ |
| topic folder isolation | core/topic_drive_oauth.py | PATCH_RETRY_TOPIC_FOLDER_V1 | VERIFIED ✅ |

## НЕ ЗАКРЫТО — P1 (ТЗ готово, ждёт «да»)

---

### PATCH_CONFIRM_ONLY_ON_DONE_V1

**Файл:** `task_worker.py` строки 2068-2075 (PATCH_DRIVE_BOTMSG_SAVE_V1 блок)

**Проблема:**
`AWAITING_CONFIRMATION` + "Доволен результатом?" ставится всегда, даже если:
- `result = "Файл скачан, ожидает анализа"` — задача не выполнена
- `result = "Ошибка..."` — задача упала
- `result = "Документ обработан локально, но загрузка в Drive завершилась ошибкой"` — неполный результат

**Правило:**
```
AWAITING_CONFIRMATION разрешён ТОЛЬКО если:
- result не содержит: "ожидает анализа", "Ошибка", "не удалась", "завершилась ошибкой", "недоступен"
- len(result) > 50 символов (не пустой)
- нет active error_message

Если условия не выполнены:
- state = FAILED
- error_message = "RESULT_NOT_READY"
- НЕ отправлять "Доволен результатом?"
```

**Acceptance:** после патча при ошибке Drive — бот НЕ спрашивает подтверждение, а пишет "Не удалось обработать файл. Попробуй ещё раз."

---

### PATCH_TEMPLATE_INTENT_V1

**Файлы:**
- `core/artifact_pipeline.py` — добавить ветку для intent=template
- `core/template_manager.py` — хранение шаблонов

**Проблема:**
`analyze_downloaded_file` игнорирует `user_text` (intent). Для любого PDF делает:
`_extract_pdf → текст → _build_word "Сводка по документу"` — это пересказ, не шаблон.

Ты говоришь "взять как шаблон проекта" → система должна вернуть структурную модель:
```json
{
  "template_type": "КД / КЖ / АР / КМ",
  "sheets": ["КД1 Общие данные", "КД2 Схема", ...],
  "marks": ["КД", "КЖ", "АР"],
  "sections": ["Исходные данные", "Расчётная часть", "Чертежи", "Спецификации"],
  "parameters": {"area": 175.8, "floors": 1, "location": "..."},
  "standards": ["СП 20.13330", "ГОСТ ..."],
  "stamp_fields": ["Заказчик", "Исполнитель", "Адрес", "Дата"]
}
```

**Acceptance:**
- intent=template → artifact = JSON структурная модель + docx с составом листов
- НЕ просто OCR текст
- Модель сохраняется в `core/template_manager.py`
- Следующее задание может использовать модель для генерации нового документа

---

### Голосовой confirm при AWAITING_CONFIRMATION

**Файл:** `telegram_daemon.py` ~строка 601
**Проблема:** голосовое "да/нет" при AWAITING_CONFIRMATION не закрывает задачу
**Acceptance:** "[VOICE] да" / "[VOICE] нет" обрабатывается как confirm/reject

---

### Live-тесты INSTALLED патчей

| Патч | Файл | Что тестировать |
|---|---|---|
| PATCH_FILE_ERROR_RETRY_V1 | task_worker.py | reply на ошибку → перезапуск файла |
| PATCH_CRASH_BOTMSG_V1 | task_worker.py | crash сохраняет bot_message_id |
| PATCH_DUPLICATE_GUARD_V1 | task_worker.py | отправить тот же файл дважды |
| PATCH_MULTI_FILE_INTAKE_V1 | task_worker.py | несколько файлов одновременно |
| PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1 | task_worker.py | отправить голую ссылку |

## НЕ ЗАКРЫТО — P2

- Смета PDF → Excel → Drive end-to-end
- КЖ PDF pipeline
- project_engine end-to-end (после template_manager)
- Gemini vision live-тест
- Excel формулы =C2*D2 / =SUM
- Нормы СП/ГОСТ в technadzor_engine
- Multi-file один артефакт
- Google Sheets интеграция
- Шаблоны end-to-end
- MODEL_ROUTER, FALLBACK_CHAIN
- STT "Олег" — Whisper галлюцинация имени

## СТРУКТУРА ФАЙЛОВ (по §3 канона)

```
task_worker.py              — основной воркер (PATCH_CONFIRM_ONLY_ON_DONE_V1)
core/artifact_pipeline.py   — pipeline анализа файлов (PATCH_TEMPLATE_INTENT_V1)
core/template_manager.py    — хранение шаблонов проектов (PATCH_TEMPLATE_INTENT_V1)
core/engine_base.py         — базовый класс движков
core/estimate_engine.py     — движок смет ✅
core/ocr_engine.py          — OCR движок ✅
core/technadzor_engine.py   — технадзор движок ✅
core/topic_drive_oauth.py   — Drive OAuth ✅ (scope=drive)
google_io.py                — Drive I/O ✅ (scope=drive)
```

## АРХИТЕКТУРА FINAL (30.04.2026)

```
Telegram → daemon → upload_file_to_topic (OAuth scope=drive)
                         ↓ OK → drive_file_id → create_task → task_worker
                         ↓ download → _download_from_drive (OAuth scope=drive)
                         ↓ analyze → artifact_pipeline.analyze_downloaded_file
                                        ↓ intent=template → template_manager → JSON модель
                                        ↓ intent=estimate → estimate_engine → xlsx
                                        ↓ intent=project  → project_engine (P2)
                                        ↓ intent=ocr      → ocr_engine → docx
                                        ↓ intent=vision   → gemini vision → docx
                         ↓ artifact → upload_artifact_to_drive → topic папка
                         ↓ если Drive упал → TG fallback → cron retry 10min
```
