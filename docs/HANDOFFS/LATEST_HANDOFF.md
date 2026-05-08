# LATEST HANDOFF — 2026-05-08 ~09:30 MSK
**HEAD**: `81f35b5`
**Воркер**: active

---

## СТАТУС ТОПИКОВ

| Топик | Состояние | Примечание |
|-------|-----------|------------|
| topic_2 СТРОИКА | INSTALLED (не VERIFIED) | 5 патчей session 08.05, d72028da застрял |
| topic_5 ТЕХНАДЗОР | Stable | без изменений |
| topic_500 ПОИСК | INSTALLED (не VERIFIED) | 9 режимов adaptive output |
| topic_210 PROJECT | Active | без изменений |

---

## ГЛАВНАЯ АРХИТЕКТУРНАЯ ПРОБЛЕМА (P0)

### file_intake_router НЕ вызывается из _handle_drive_file

**Это зафиксировано в самом каноне** (01_SYSTEM_LOGIC_FULL.md, строка ~314):
> `file_intake_router не вызывается в _handle_drive_file`

**Что есть**: `core/file_intake_router.py` — **универсальный** обработчик файлов для ВСЕХ топиков:
- Intent detection: estimate / ocr / technadzor / dwg / template / vision / search
- Format priority: DWG > XLSX > DOCX > PDF > IMAGE
- Entry point: `async def route_file(file_path, task_id, topic_id, intent, fmt)`
- Работает для topic_2, topic_5, topic_210 — одинаково

**Что происходит сейчас**: `_handle_drive_file` (task_worker.py ~3906) скачивает файл, но потом:
- НЕ вызывает `file_intake_router.route_file(local_path, ...)`
- Вместо этого идёт через P6C → topic-specific route → берёт только caption из JSON
- PDF содержимое **никогда не читается**
- `TOPIC2_PDF_SPEC_EXTRACTOR_STARTED` никогда не появляется

**Правильная архитектура**:
```
_handle_drive_file(conn, task)
  → скачать PDF/файл по file_id → local_path
  → detect_intent(caption) → intent="estimate"|"technadzor"|...
  → file_intake_router.route_file(local_path, task_id, topic_id, intent)
      → [topic_2] maybe_handle_stroyka_estimate с file_path → PDF OCR → смета
      → [topic_5] technadzor_engine с file_path → анализ дефектов
      → [topic_210] проектирование с file_path → анализ проекта
```

**Где реализовать**: append-only патч в task_worker.py:
- Обернуть `_handle_drive_file` так, чтобы после скачивания файла вызывался `route_file`
- ИЛИ: вызывать `maybe_handle_stroyka_estimate` напрямую для topic_2 drive_file задач

**Этот принцип единый для всех топиков** — нет регрессии, нет дублирования.

---

## ПАТЧИ СЕССИИ 08.05.2026 (запушены в b236f02)

| Патч | Файл | Что |
|------|------|-----|
| PATCH_WCPE_CLARIFIED_UNBLOCK_V1 | task_worker.py | WCG_SKIP не блокирует IN_PROGRESS |
| PATCH_P6C_FULLTEXT_ESTIMATE_PREP_V1 | task_worker.py | partial JSON + VOICE в estimate_raw + dims из filename |
| PATCH_P3PCG_CLARIFIED_HISTORY_CHECK_V1 | sample_template_engine.py | clarified:N → цена (старый патч) |
| PATCH_P3CHK_PRICE_APPEND_FIX_V2 | sample_template_engine.py | append цены к raw_s вместо replace |
| PATCH_P2_MISSING_SKIP_DISTANCE_V1 | sample_template_engine.py | убрать вопрос о расстоянии |

---

## ОТКРЫТЫЕ ПРОБЛЕМЫ (приоритет)

### P0 — АРХИТЕКТУРА: file_intake_router не вызывается (см. выше)
→ Решение: обернуть `_handle_drive_file` чтобы вызывать `route_file` после скачивания

### P1 ЗАКРЫТ — PATCH_P6CF3_CLARIFIED_HISTORY_INCLUDE_V1 (81f35b5)
clarified:* ответы из task_history теперь включаются в estimate_raw → _p2_parse
видит "Фундамент монолитный..." → бесконечный цикл вопросов устранён.
Задача d72028da прошла DONE: 25 позиций, 5 425 839 руб, Excel+PDF в Drive.

### ЗАКРЫТ — "Этажей: 1" не парсится regex
`_p6c_prepare_topic2_raw_20260504` добавляет `"\nЭтажей: 1"` но `_p2_floors()` ищет `(\d+)\s*этаж` — число ДО слова.
Нужен P6CF_V2 в task_worker.py (append):
```python
_P6CF2_ORIG = globals().get("_p6c_prepare_topic2_raw_20260504")
if _P6CF2_ORIG and not getattr(_P6CF2_ORIG, "_p6cf2_wrapped", False):
    def _p6c_prepare_topic2_raw_20260504(task_id, raw_input):
        text = _P6CF2_ORIG(task_id, raw_input)
        return text.replace("Этажей: 1", "1 этаж")
    _p6c_prepare_topic2_raw_20260504._p6cf2_wrapped = True
    globals()["_p6c_prepare_topic2_raw_20260504"] = _p6c_prepare_topic2_raw_20260504
    import logging as _p6cf2_log
    _p6cf2_log.getLogger("task_worker").info("PATCH_P6CF2_FLOOR_FORMAT_FIX installed")
```

### P2 — Voice в reply не транскрибируется
telegram_daemon.py FORBIDDEN. Нужен обходной путь в task_worker.py.

### P3 — Верификация полного цикла topic_2
Запустить чистую задачу, проверить маркеры:
```
TOPIC2_PDF_SPEC_EXTRACTOR_STARTED → TOPIC2_PDF_SPEC_ROWS_EXTRACTED
TOPIC2_PRICE_CHOICE_CONFIRMED:median
TOPIC2_TEMPLATE_SELECTED → TOPIC2_XLSX_CANON_COLUMNS_OK:15
TOPIC2_PDF_TOTALS_MATCH_XLSX
TOPIC2_DRIVE_TOPIC_FOLDER_OK → TOPIC2_AC_GATE_OK
TOPIC2_TELEGRAM_DELIVERED
FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:estimate_generated
```

---

## ЗАДАЧА d72028da (застрявшая, для теста)

```
file: 8х12.pdf  file_id: 1-isQhm067W2LDv2Bgm5ewbfyVm2B8QhV
caption: "Надо полную смету на внутреннюю наружную отделку"
voices: газобетон 400, монолитная плита, клик-фальц, имитация бруса, ламинат, тёплые полы
price: "средние" (clarified:2)
dims: 8х12 м (из имени файла)
```

Сброс:
```bash
sqlite3 /root/.areal-neva-core/data/core.db \
  "UPDATE tasks SET state='IN_PROGRESS', error_message='', updated_at=datetime('now') \
   WHERE id='d72028da-b4ff-424d-a626-790c9da8be77';"
```

---

## ДИАГНОСТИКА

```bash
systemctl is-active areal-task-worker

grep "PATCH_P6C_FULLTEXT\|PATCH_P3CHK2\|PATCH_P2_MISSING\|PATCH_WCPE" \
  /root/.areal-neva-core/logs/task_worker.log | tail -10

sqlite3 -readonly /root/.areal-neva-core/data/core.db \
  "SELECT state, substr(error_message,1,50), substr(result,1,80), updated_at \
   FROM tasks WHERE id='d72028da-b4ff-424d-a626-790c9da8be77';"

sqlite3 -readonly /root/.areal-neva-core/data/core.db \
  "SELECT action, created_at FROM task_history \
   WHERE task_id='d72028da-b4ff-424d-a626-790c9da8be77' \
   ORDER BY rowid DESC LIMIT 15;"
```

---

## CANON REFS
- `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md` — §4, §11.9, строка ~314 (file_intake_router bug known)
- `docs/CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md` — §7 PDF pipeline
- `core/file_intake_router.py` — универсальный роутер файлов (уже написан, не подключён)
- `core/stroyka_estimate_canon.py:1930` — `maybe_handle_stroyka_estimate` (PDF OCR внутри)
- `docs/HANDOFFS/LATEST_HANDOFF.md` — этот файл
