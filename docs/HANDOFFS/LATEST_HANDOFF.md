# LATEST HANDOFF — 2026-05-08 ~09:00 MSK
**HEAD**: `e3a016c` + uncommitted patches below  
**Воркер**: active  
**GitHub**: нужен push (см. ниже)

---

## СТАТУС ТОПИКОВ

| Топик | Состояние | Примечание |
|-------|-----------|------------|
| topic_2 СТРОИКА | INSTALLED (не VERIFIED) | 5 патчей session 08.05, live-run d72028da застрял |
| topic_5 ТЕХНАДЗОР | Stable | без изменений |
| topic_500 ПОИСК | INSTALLED (не VERIFIED) | 9 режимов adaptive output |
| topic_210 PROJECT | Active | без изменений |

---

## СЕССИЯ 08.05.2026 — ЧТО НАШЛИ И ЧТО СДЕЛАЛИ

### ПРОБЛЕМА 1: P3CHK заменяет raw_input → бесконечный вопрос

**Симптом**: задача d72028da спрашивает "Уточни этажность" бесконечно  
**Корень**: `PATCH_P3PCG_CLARIFIED_HISTORY_CHECK_V1` (P3CHK) инжектировал `raw_input = "средние"` вместо append → P3E парсил только "средние", не видел ни размеров, ни материала  
**Патч**: `PATCH_P3CHK_PRICE_APPEND_FIX_V2` (sample_template_engine.py append)  
- Вместо `raw_input = clarified` → `raw_input = raw_s + "\nЦены: " + clarified`  
- Теперь P3E получает полный текст ТЗ + цену как суффикс

### ПРОБЛЕМА 2: P6C не парсит JSON с REVISION_CONTEXT

**Симптом**: для задачи с PDF-файлом estimate_raw = только "\nЭтажей: 1"  
**Корень**: `_p6c_meta_20260504(raw_input)` использует строгий `json.loads` — FAIL когда в raw_input после JSON идёт `---REVISION_CONTEXT`. caption="" → вся информация теряется  
**Патч**: `PATCH_P6C_FULLTEXT_ESTIMATE_PREP_V1` (task_worker.py append)  
- Частичный JSON parse (первый `{...}` блок через regex) → caption извлекается  
- Голосовые тексты из `[VOICE]` блоков добавляются в estimate_raw  
- Размеры из filename ("8х12.pdf" → "Размеры объекта: 8 на 12 м")  
- estimate_raw теперь 618 символов с реальным содержимым

### ПРОБЛЕМА 3: "Этажей: 1" не парсится регexpом

**Симптом**: P6CF добавляет "Этажей: 1" → `_p2_floors()` всё равно None → "Уточни этажность"  
**Корень**: regex `(\d+)\s*(?:этаж|этажа|этажей)` ищет цифру ПЕРЕД словом. "Этажей: 1" — цифра ПОСЛЕ → нет матча  
**НЕ ЗАКРЫТО**: Нужен P6CF_V2, меняющий `"\nЭтажей: 1"` → `"\n1 этаж"` (матчится regex). Либо добавить дополнительную проверку в `_p2_floors`

### ПРОБЛЕМА 4: _p2_missing спрашивает город/км

**Симптом**: После фикса размеров и этажей — следующий вопрос "Уточни город или удалённость объекта в км"  
**Корень**: `_p2_missing` проверяет distance_km, для drive_file задач пользователь его не указывает  
**Патч**: `PATCH_P2_MISSING_SKIP_DISTANCE_V1` (sample_template_engine.py append)  
- Убирает проверку distance_km из `_p2_missing`  
- В расчёте `max(float(p["distance_km"] or 0), 1)` — None безопасен  
**Статус**: INSTALLED, НЕ VERIFIED (логирование не подтверждено)

### ПРОБЛЕМА 5: PDF содержимое не читается (ГЛАВНАЯ НЕ ЗАКРЫТАЯ)

**Симптом**: `TOPIC2_PDF_SPEC_EXTRACTOR_STARTED` никогда не появляется в истории d72028da  
**Корень**: P6C route вызывает `handle_topic2_one_big_formula_pipeline_v1` с текстом из caption/filename, НЕ читает сам PDF через `maybe_handle_stroyka_estimate`  
**Правильное решение**: P6C должен скачать PDF из Drive → передать в `maybe_handle_stroyka_estimate` → тот извлекает текст (pdfplumber/OCR) → использует реальное содержимое  
**НЕ ЗАКРЫТО**: требует интеграции Drive download + maybe_handle_stroyka_estimate в P6C route

### ПРОБЛЕМА 6: WCPE блокировал задачи после ответа пользователя

**Симптом**: telegram_daemon ставит state=IN_PROGRESS, но error_message=WCG_SKIP не очищает → WCPE фильтр блокировал задачу навсегда  
**Патч**: `PATCH_WCPE_CLARIFIED_UNBLOCK_V1` (task_worker.py append)  
- Блокирует только WAITING_CLARIFICATION+WCG_SKIP  
- Пропускает IN_PROGRESS+WCG_SKIP (пользователь ответил)  
**Статус**: INSTALLED, работает

---

## ПАТЧИ ТЕКУЩЕЙ СЕССИИ (08.05.2026)

### В task_worker.py (appended):
```
PATCH_WCPE_CLARIFIED_UNBLOCK_V1          — пик-фильтр: разрешить IN_PROGRESS+WCG_SKIP
PATCH_P6C_FULLTEXT_ESTIMATE_PREP_V1      — partial JSON + REVISION_CONTEXT voices + filename dims
```

### В core/sample_template_engine.py (appended):
```
PATCH_P3PCG_CLARIFIED_HISTORY_CHECK_V1  — check clarified:N in history (старый патч)
PATCH_P3CHK_PRICE_APPEND_FIX_V2         — append price к raw_s вместо replace
PATCH_P2_MISSING_SKIP_DISTANCE_V1       — убрать вопрос о расстоянии
```

---

## ЧТО НЕ ЗАКРЫТО (ПРИОРИТЕТ)

### P1 — КРИТИЧНО: PDF не читается
Задача d72028da имеет PDF "8х12.pdf" с планом дома. Система ДОЛЖНА:
1. Скачать PDF из Drive по `file_id = "1-isQhm067W2LDv2Bgm5ewbfyVm2B8QhV"`
2. Запустить `maybe_handle_stroyka_estimate` (stroyka_estimate_canon.py) — там есть PDF OCR
3. Маркеры: `TOPIC2_PDF_SPEC_EXTRACTOR_STARTED` → `TOPIC2_PDF_SPEC_ROWS_EXTRACTED`
4. Использовать извлечённый текст для расчёта — без дополнительных вопросов

**Где это делается**: `_handle_drive_file` → скачивает PDF → затем нужно вызвать `maybe_handle_stroyka_estimate` с `file_path=local_path`

### P2 — НЕ ЗАКРЫТО: "Этажей: 1" → нужен "1 этаж"
Добавить в task_worker.py append:
```python
# P6CF_V2: fix floor format
_P6CF2_ORIG = globals().get("_p6c_prepare_topic2_raw_20260504")
if _P6CF2_ORIG and not getattr(_P6CF2_ORIG, "_p6cf2_wrapped", False):
    def _p6c_prepare_topic2_raw_20260504(task_id, raw_input):
        text = _P6CF2_ORIG(task_id, raw_input)
        return text.replace("Этажей: 1", "1 этаж")
    _p6c_prepare_topic2_raw_20260504._p6cf2_wrapped = True
    globals()["_p6c_prepare_topic2_raw_20260504"] = _p6c_prepare_topic2_raw_20260504
```

### P3 — НЕ ЗАКРЫТО: Voice в reply не транскрибируется
telegram_daemon.py (FORBIDDEN) обрабатывает reply к боту через text-only handler, не вызывает STT  
Нужен перехват в task_worker.py или отдельный голосовой обработчик

### P4 — Верификация
Запустить новую задачу topic_2 с PDF — проверить полную цепочку маркеров:
```
TOPIC2_PDF_SPEC_EXTRACTOR_STARTED
TOPIC2_PDF_SPEC_ROWS_EXTRACTED
TOPIC2_PRICE_CHOICE_CONFIRMED:median
TOPIC2_AFTER_PRICE_CHOICE_GENERATION_STARTED
TOPIC2_TEMPLATE_SELECTED:<name>
TOPIC2_XLSX_CANON_COLUMNS_OK:15
TOPIC2_PDF_TOTALS_MATCH_XLSX
TOPIC2_DRIVE_TOPIC_FOLDER_OK
TOPIC2_AC_GATE_OK
TOPIC2_TELEGRAM_DELIVERED
FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:estimate_generated
```

---

## ЗАДАЧА d72028da (ЗАСТРЯВШАЯ)

```
id: d72028da-b4ff-424d-a626-790c9da8be77
state: WAITING_CLARIFICATION | WCG_SKIP_WAITING_CLARIFICATION
file: 8х12.pdf (file_id: 1-isQhm067W2LDv2Bgm5ewbfyVm2B8QhV)
caption: "Надо полную смету на внутреннюю наружную отделку"
voices: газобетон 400, монолитная плита, клик-фальц, имитация бруса, ламинат, тёплые полы
price: "средние" (clarified:2 в истории)
dims: 8х12 м (из имени файла)
```

Для ручного сброса:
```bash
sqlite3 /root/.areal-neva-core/data/core.db \
  "UPDATE tasks SET state='IN_PROGRESS', error_message='', updated_at=datetime('now') \
   WHERE id='d72028da-b4ff-424d-a626-790c9da8be77';"
```

---

## ДИАГНОСТИКА

```bash
# Воркер жив?
systemctl is-active areal-task-worker

# Последние патчи установились?
grep "PATCH_P6C_FULLTEXT\|PATCH_P3CHK_PRICE\|PATCH_P2_MISSING\|PATCH_WCPE" \
  /root/.areal-neva-core/logs/task_worker.log | tail -10

# Задача d72028da
sqlite3 -readonly /root/.areal-neva-core/data/core.db \
  "SELECT state, substr(error_message,1,50), substr(result,1,80), updated_at \
   FROM tasks WHERE id='d72028da-b4ff-424d-a626-790c9da8be77';"

# История d72028da (последние 15)
sqlite3 -readonly /root/.areal-neva-core/data/core.db \
  "SELECT action, created_at FROM task_history \
   WHERE task_id='d72028da-b4ff-424d-a626-790c9da8be77' \
   ORDER BY rowid DESC LIMIT 15;"
```

---

## CANON REFS
- `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md`
- `docs/CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md`
- `docs/HANDOFFS/LATEST_HANDOFF.md` (этот файл)
