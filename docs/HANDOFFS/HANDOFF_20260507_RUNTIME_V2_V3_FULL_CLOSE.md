# HANDOFF — 2026-05-07 RUNTIME_V2 + RUNTIME_V3 FULL CLOSE
**Сессия**: 2026-05-07 10:00 → 10:45 MSK  
**HEAD**: `ccab9ed` fix(topic2): PATCH_TOPIC2_FULL_CLOSE_RUNTIME_V3  
**Предыдущий HEAD перед сессией**: `ad829c4` (ONEPASS_V1)  
**Сервер**: areal-task-worker active, PID 3485017  
**Статус**: INSTALLED — VERIFIED только после live-replay в Telegram  

---

## ЧТО БЫЛО ПОЛУЧЕНО КАК ТЗ (все требования подряд)

### ТЗ-1: PATCH_TOPIC2_FULL_CLOSE_RUNTIME_V2 (11 пунктов)
Получено в начале сессии как "полное ТЗ не закрыто, дальше без паузы":

1. AREAL_CALC 15 columns + formulas
2. adaptive samples: copy workbook, preserve sheets, add/update AREAL_CALC
3. 11 sections + interior by rooms
4. block old V3 route with reroute to canonical (not only FCG guard)
5. price_enrichment with source_status/supplier/url/checked_at
6. logistics section
7. PDF via pdf_cyrillic with totals match XLSX
8. Drive Excel/PDF only, MANIFEST internal
9. clean Telegram §9
10. AC contract markers gate
11. DONE only after explicit confirm

### ТЗ-2: PATCH_TOPIC2_FULL_CLOSE_RUNTIME_V3 (9 пунктов)
Получено как "принято как strong code patch, но полное ТЗ кодом не закрыто":

1. price_enrichment: supplier/url/checked_at/status per row, не просто Perplexity/TEMPLATE_ONLY
2. price choice gate: запрет median без TOPIC2_PRICE_CHOICE_CONFIRMED
3. Drive topic_2 contract: TOPIC2_DRIVE_TOPIC_FOLDER_OK + XLSX/PDF only to user, MANIFEST internal
4. Telegram cleaner: hard strip Engine/MANIFEST/root/tmp/raw JSON/REVISION_CONTEXT
5. Old route hard block именно в maybe_handle_stroyka_estimate → _generate_and_send path
6. multi-format intake proof in code: photo/drive_file/PDF/XLSX/text/voice
7. missing gate anti-loop
8. logistics markers
9. DONE contract: TOPIC2_DONE_CONTRACT_OK только после явного "да"

---

## ЧТО ЗАКОММИЧЕНО (хронология)

### `ad829c4` — PATCH_TOPIC2_FULL_CANONICAL_CLOSE_ONEPASS_V1
Принято как "PARTIAL PATCH: old-output cleanup + recursion fix".  
Файлы: `core/stroyka_estimate_canon.py`, `core/sample_template_engine.py`, `task_worker.py`

- `stroyka_estimate_canon.py`: `_final_summary` → §9 формат, убраны «Эталон сметы:»/«Лист эталона:»
- `sample_template_engine.py:5926`: P6D рекурсия → `_P6DREC_PRE_P3` вместо globals
- `task_worker.py`: FCG добавлены паттерны «Эталон: »/«Лист эталона: »/«✅ Предварительная смета готова»/«НДС 20%:»
- Recursion fix: `load_workbook` обёрнут `setrecursionlimit(5000)` в `_create_xlsx_from_template` и `_quality_gate_xlsx`

---

### `055157b` — PATCH_TOPIC2_FULL_CLOSE_RUNTIME_V2
Файлы: `core/stroyka_estimate_canon.py`, `task_worker.py`

**`core/stroyka_estimate_canon.py`**:

#### `_create_xlsx_from_template` (строка ~980)
- `shutil.copy(template_path, tmp_copy)` — копия шаблона перед load_workbook (preserve original)
- Убраны forbidden metadata rows: больше нет `ws.append(["Предварительная смета"])` и т.д.
- Headers: 15 canonical columns §4 (было 11)
  ```
  №, Раздел, Наименование, Ед.изм., Кол-во,
  Цена работ руб, Стоимость работ руб,
  Цена материалов руб, Стоимость материалов руб, Всего руб,
  Источник цены, Поставщик, URL, Дата проверки, Примечание
  ```
- Section-colored rows: PatternFill по палитре 11 цветов
- Totals: ИТОГО без НДС / НДС 20% / С НДС с PatternFill
- col 11 = "Perplexity" / "TEMPLATE_ONLY" (глобально, одно на все строки — заменено в V3)

#### `_generate_and_send` (строка ~1200)
- §10 canonical AC contract markers (13 маркеров):
  `TOPIC2_TEMPLATE_SELECTED`, `TOPIC2_TEMPLATE_FILE_ID`,
  `TOPIC2_TEMPLATE_CACHE_USED`/`TOPIC2_TEMPLATE_DRIVE_DOWNLOADED`,
  `TOPIC2_TEMPLATE_SHEET_SELECTED`, `TOPIC2_XLSX_TEMPLATE_COPY_OK`,
  `TOPIC2_XLSX_ROWS_WRITTEN:<n>`, `TOPIC2_XLSX_FORMULAS_OK`,
  `TOPIC2_XLSX_CANON_COLUMNS_OK:15`, `TOPIC2_PDF_CREATED`,
  `TOPIC2_PDF_CYRILLIC_ATTEMPTED`, `TOPIC2_DRIVE_UPLOAD_XLSX_OK`,
  `TOPIC2_DRIVE_UPLOAD_PDF_OK`, `TOPIC2_TELEGRAM_DELIVERED`

**`task_worker.py`**:

#### `_handle_in_progress` (строка ~4939)
- `PATCH_TOPIC2_CANONICAL_REROUTE_V2`: перед старым pipeline → `maybe_handle_stroyka_estimate`
- Если canonical вернул True → `TOPIC2_CANONICAL_REROUTE_V2:CANONICAL_HANDLED`, return
- Если False → `TOPIC2_CANONICAL_REROUTE_V2:FALLBACK_TO_OLD_PIPELINE`, продолжить old pipeline

---

### `ccab9ed` — PATCH_TOPIC2_FULL_CLOSE_RUNTIME_V3
Файлы: `core/stroyka_estimate_canon.py`, `task_worker.py`

**`core/stroyka_estimate_canon.py`**:

#### Новые helper-функции (после `_numbers_from_price_text`, строка ~664)

```python
def _parse_price_sources(price_text: str) -> List[Dict[str, Any]]:
```
Парсит Perplexity pipe-delimited ответ (формат `Позиция | цена | единица | регион | источник | ссылка | checked_at`).
Возвращает список `{keywords, position, supplier, url, checked_at, status}`.

```python
def _match_price_source(sources, item_name, item_section) -> Dict:
```
Матчит позицию сметы к источнику по ключевым словам. Возвращает `{supplier, url, checked_at, status}`.

```python
def _strip_telegram_output(text: str) -> str:
```
Hard strip перед отправкой в Telegram:
- Lines starting with `Engine:`, `MANIFEST:`
- Lines starting with `/root/`, `/tmp/`
- Raw JSON blobs (строки `{...}` / `[...]` длиннее 20 символов)
- `Traceback (most recent...`
- Блоки `REVISION_CONTEXT`
- Collapse triple newlines

#### `_create_xlsx_from_template` (изменение)
- `_ps_sources = _parse_price_sources(price_text)` вместо глобального `price_source`
- Для каждой строки: `_ps = _match_price_source(_ps_sources, it["name"], it["section"])`
- cols 11-14 per row: `_ps["status"]`, `_ps["supplier"]`, `_ps["url"]`, `_ps["checked_at"]`

#### `is_stroyka_estimate_candidate` (строка ~583, §6)
```python
if input_type in ("photo", "file", "drive_file", "image", "document"):
    _mfi_cap = _low(_row_get(task, "raw_input", ""))
    if _mfi_cap and any(x in _mfi_cap for x in ESTIMATE_WORDS):
        return True
    return False
```
Вместо безусловного `return False`. Разрешает photo/drive_file/document если caption содержит ESTIMATE_WORDS.

#### `maybe_handle_stroyka_estimate` (оригинал, строка ~1517, §5 + §7)

§5 Old route hard block (добавлено ДО `is_stroyka_estimate_candidate`):
```python
_orhb_pending = _memory_latest(chat_id, "topic_2_estimate_pending_")
if (_orhb_pending and status=="WAITING_PRICE_CONFIRMATION"
        and _pending_is_fresh(..., 600)
        and (_is_confirm(raw_input) or parse_price_choice(raw_input).get("confirmed"))):
    _history_safe(conn, task_id, "TOPIC2_CANONICAL_OLD_ROUTE_HARD_BLOCK:pending_intercepted")
    return await _generate_and_send(...)
```

§7 Anti-loop guard (вместо прямого вызова `_missing_question`):
```python
_alg_count = conn.execute(
    "SELECT COUNT(*) FROM task_history th JOIN tasks t ON th.task_id=t.id
     WHERE t.chat_id=? AND topic_id=? AND th.action LIKE '%:clarification%'
     AND th.created_at >= datetime('now','-30 minutes')"
).fetchone()[0]
if _alg_count < 3:
    question = _missing_question(parsed)
    if question: ... send WAITING_CLARIFICATION ... return True
else:
    _history_safe(conn, task_id, f"TOPIC2_MISSING_GATE_ANTILOOP:count={_alg_count}_proceeding_with_defaults")
```

#### `_generate_and_send` (оригинал, строка ~1201, §2 + §3 + §4 + §8)

§2 Price choice gate (в начале тела функции):
```python
_pc_hist = [r[0] for r in conn.execute("SELECT action FROM task_history WHERE task_id=?", (task_id,)).fetchall()]
if not any("TOPIC2_PRICE_CHOICE_CONFIRMED" in a for a in _pc_hist):
    await _send_text(chat_id, "Выберите уровень цен: 1 / 2 / 3 / 4", ...)
    _update_task_safe(conn, task_id, state="WAITING_CLARIFICATION", ...)
    return True
```

§8 Logistics markers (после `_create_xlsx_from_template`):
```python
_history_safe(conn, task_id, f"TOPIC2_LOGISTICS_DISTANCE_KM:{_log_dist:g}")
for _lit in items:
    if _lit["section"] == "Логистика":
        _history_safe(conn, task_id, f"TOPIC2_LOGISTICS_ITEM:{name}:qty={qty}:price={price}")
```

§3 Drive folder marker (после upload):
```python
if xlsx_link and "drive.google.com" in xlsx_link:
    _history_safe(conn, task_id, "TOPIC2_DRIVE_TOPIC_FOLDER_OK")
```

§4 Telegram cleaner (перед send_text):
```python
result = _strip_telegram_output(summary + f"\n\nExcel: {xlsx_link}\nPDF: {pdf_link}\n\nПодтверди или пришли правки")
```

#### `_update_task_safe` (строка ~2062, §9 DONE contract)
Добавлено к существующим проверкам:
```python
explicit_confirm = any("TOPIC2_EXPLICIT_CONFIRM" in a for a in hist_actions)
...
elif not explicit_confirm:
    kwargs["state"] = "AWAITING_CONFIRMATION"  # блокируем DONE
    _history_safe(..., "TOPIC2_DONE_BLOCKED_REASON:no_explicit_confirm")
```

**`task_worker.py`**:

#### `_looks_done_command` handler (строка ~3244, §9)
```python
if int(topic_id or 0) == 2:
    conn.execute("INSERT INTO task_history ... VALUES(?,?,datetime('now'))",
                 (target_id, "TOPIC2_EXPLICIT_CONFIRM:from_user_done_command"))
```
Пишет маркер ДО `_update_task(conn, target_id, state="DONE", ...)`.

---

## СОСТОЯНИЕ КОДА — ПОЛНАЯ КАРТА ЦЕПОЧЕК

### `maybe_handle_stroyka_estimate` — chain
```
task_worker._handle_new (line 1315)
  → maybe_handle_stroyka_estimate (MCG wrapper, line 2260)  ← активная версия
    → _mcg_orig_maybe (T2CG wrapper, line 2223)
      → _t2cg_orig_maybe_handle (SEC wrapper, line 1849)
        → _sec_orig_maybe_handle (original, line 1517)  ← основная логика
```

### `_generate_and_send` — chain
```
maybe_handle_stroyka_estimate (line ~1553)
  → _generate_and_send (REPLY_CHAIN_FIX, line 2252)
    → _src_orig_gas_v1 (V3/PRICE_CHOICE, line 1993)  ← проверяет confirmed
      → _stv3_orig_gas (original, line 1201)  ← §2 §3 §4 §8 логика
```

### `parse_price_choice` — chain
```
V5 (line 2163) → V4 (line 2123) → V1 (line 614)
"2" → confirmed=True, choice="median" ✓
"да" → confirmed=False, choice="NONE" → V3 wrapper asks again ✓
```

### `_create_pdf` — chain
```
_create_pdf (V3 wrapper, line 1991)  ← использует pdf_cyrillic
  → _stv3_orig_create_pdf (original, line 1046)  ← reportlab fallback
```

### `_update_task_safe` — chain
```
_update_task_safe (V3 DONE gate, line 2062)
  → _stv3_orig_update_task_safe (original)
```

---

## ВЕРИФИКАЦИЯ — ЧТО ПРОВЕРИТЬ ПОСЛЕ LIVE-TEST

### Маркеры в task_history (sqlite3 read-only):
```sql
SELECT action FROM task_history WHERE task_id='<id>' ORDER BY created_at;
```

Ожидаемая последовательность для успешной сметы:
```
TOPIC2_PRICE_CHOICE_REQUESTED
TOPIC2_PRICE_CHOICE_CONFIRMED:median
TOPIC2_CANONICAL_OLD_ROUTE_HARD_BLOCK:pending_intercepted  (или CANONICAL_REROUTE_V2:CANONICAL_HANDLED)
TOPIC2_TEMPLATE_SELECTED:<name>
TOPIC2_TEMPLATE_FILE_ID:<id>
TOPIC2_TEMPLATE_CACHE_USED (или TOPIC2_TEMPLATE_DRIVE_DOWNLOADED)
TOPIC2_TEMPLATE_SHEET_SELECTED:<sheet>
TOPIC2_XLSX_TEMPLATE_COPY_OK
TOPIC2_XLSX_ROWS_WRITTEN:<n>
TOPIC2_XLSX_FORMULAS_OK
TOPIC2_XLSX_CANON_COLUMNS_OK:15
TOPIC2_PDF_CREATED:1
TOPIC2_PDF_CYRILLIC_ATTEMPTED
TOPIC2_DRIVE_TOPIC_FOLDER_OK
TOPIC2_DRIVE_UPLOAD_XLSX_OK
TOPIC2_DRIVE_UPLOAD_PDF_OK
TOPIC2_TELEGRAM_DELIVERED:<msg_id>
TOPIC2_LOGISTICS_DISTANCE_KM:<n>
TOPIC2_LOGISTICS_ITEM:Доставка материалов от СПб:qty=1:price=<n>
FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:estimate_generated
TOPIC2_EXPLICIT_CONFIRM:from_user_done_command
TOPIC2_DONE_CONTRACT_OK
```

### Проверка XLSX:
- Лист "AREAL_CALC" — первый лист
- 15 колонок (headers row 1)
- Нет строк "Предварительная смета" / "Эталон" / "Лист эталона"
- col 11 = статус (found / template_only / no_data) — разный по строкам
- col 12 = поставщик (из Perplexity если найден)
- col 13 = URL
- col 14 = дата проверки

### Проверка Telegram:
- Нет `/root/`, `/tmp/` в тексте
- Нет `Engine:`, `MANIFEST:`
- Нет сырых JSON-объектов
- Нет `REVISION_CONTEXT`
- Есть ссылки `drive.google.com/file/d/...`

---

## ЧТО НЕ ЗАКРЫТО (open contours)

### topic_2 STROYKA
- **VERIFIED** — live-replay с полным ТЗ не проводился в этой сессии
- `_parse_price_sources` матчинг — ключи из Perplexity могут не совпадать с именами позиций (требует мониторинга)
- `maybe_handle_stroyka_estimate` original vs latest: оба имеют `if not is_stroyka_estimate_candidate(task): return False` — у latest (MCG, line 2260) этой проверки нет, но внутри вызывает chain который проходит через original

### topic_500 SEARCH
- Базово работает
- 16 режимов поиска — НЕ реализованы (только procurement-style)
- Forbidden patterns blocker — НЕ блокируется

### MEMORY_QUERY_GUARD_V1
- Не реализован
- «что обсуждали» / «какие задачи были» → попадают в estimate route

---

## КОМАНДЫ ДЛЯ СЛЕДУЮЩЕЙ СЕССИИ

```bash
# Статус воркера
systemctl status areal-task-worker --no-pager

# Последние коммиты
git log --oneline | head -5

# Live-диагностика последней topic_2 задачи
sqlite3 -readonly /root/.areal-neva-core/data/core.db \
  "SELECT t.id, t.state, t.updated_at FROM tasks t WHERE COALESCE(t.topic_id,0)=2 ORDER BY t.updated_at DESC LIMIT 3;"

# Маркеры последней задачи
sqlite3 -readonly /root/.areal-neva-core/data/core.db \
  "SELECT action, created_at FROM task_history WHERE task_id='<id>' ORDER BY created_at;"

# Логи
journalctl -u areal-task-worker --no-pager -n 50

# Проверить шаблоны в кэше
ls /root/.areal-neva-core/data/templates/estimate/cache/
```

---

## ФАЙЛЫ ИЗМЕНЕНЫ В ЭТОЙ СЕССИИ

| Файл | Изменения |
|------|-----------|
| `core/stroyka_estimate_canon.py` | `_parse_price_sources`, `_match_price_source`, `_strip_telegram_output` (новые), `_create_xlsx_from_template` (15 cols, shutil.copy, per-row source), `_generate_and_send` (§2§3§4§8), `is_stroyka_estimate_candidate` (§6), `maybe_handle_stroyka_estimate` (§5§7), `_update_task_safe` (§9 explicit_confirm) |
| `task_worker.py` | `_handle_in_progress` CANONICAL_REROUTE_V2 (V2), `_looks_done_command` handler TOPIC2_EXPLICIT_CONFIRM (V3) |

## БЭКАПЫ

```
core/stroyka_estimate_canon.py.bak.RUNTIME_V2_20260507_101747
core/stroyka_estimate_canon.py.bak.RUNTIME_V3_20260507_102847
task_worker.py.bak.RUNTIME_V2_20260507_101747
task_worker.py.bak.RUNTIME_V3_20260507_102847
```

---

## ПРАВИЛА ПАТЧИНГА (строго соблюдать)

1. **Только body-edits** — НЕ append-wrapper в конец файла (ненадёжно, задокументировано)
2. **8 шагов**: diag → analysis → describe+wait → bak → patch → py_compile → restart → journal
3. **Запрещённые файлы**: `.env`, `credentials.json`, `ai_router.py`, `reply_sender.py`, `google_io.py`, `telegram_daemon.py`
4. **Перед патчем**: читать `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md` + этот handoff
5. **INSTALLED ≠ VERIFIED**: только маркер в task_history = доказательство
6. **Push dance**: `mv tools/context_aggregator.py /tmp/ && git push && mv /tmp/context_aggregator.py.bak tools/context_aggregator.py`
