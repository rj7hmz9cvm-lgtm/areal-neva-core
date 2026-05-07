# LATEST HANDOFF — 2026-05-07 ~20:00 MSK
**HEAD**: `0d6a9a4` — fix(memory): ARCHIVE_DUPLICATE_GUARD_V1 + topic500 search pollution guard  
**Предыдущий HEAD**: `0c15037`  
**Воркер**: active  
**GitHub**: pushed (0d6a9a4 visible)  
**Детальный handoff**: `HANDOFF_20260507_V4_GAP_CLOSE.md`

---

## СТАТУС ТОПИКОВ

| Топик | Состояние | Примечание |
|-------|-----------|------------|
| topic_2 СТРОИКА | INSTALLED (не VERIFIED) | V5 applied, live-replay pending |
| topic_5 ТЕХНАДЗОР | Stable | без изменений |
| topic_500 ПОИСК | INSTALLED (не VERIFIED) | 9 режимов adaptive output, procurement дефолт |
| topic_210 PROJECT | Active | без изменений |

---

## ЧТО ПРИМЕНЕНО В V5 — `168ce5e`

### PATCH_TOPIC2_FINAL_GAPS_V5 — 4 body edits

| # | Файл | Где | Что |
|---|------|-----|-----|
| 1 | stroyka_estimate_canon.py | `_search_prices_online` | conn/task_id params; per-item markers: TOPIC2_PRICE_MATERIAL_SEARCH_STARTED / TOPIC2_PRICE_WORK_SEARCH_STARTED / TOPIC2_PRICE_SOURCE_FOUND / TOPIC2_PRICE_SOURCE_MISSING |
| 2 | stroyka_estimate_canon.py | `maybe_handle_stroyka_estimate` PDF/OCR block | Alias markers: TOPIC2_PDF_SPEC_EXTRACTOR_STARTED, TOPIC2_PDF_SPEC_ROWS_EXTRACTED, TOPIC2_OCR_TABLE_STARTED, TOPIC2_OCR_TABLE_ROWS_EXTRACTED, TOPIC2_MULTIFILE_PROJECT_CONTEXT_STARTED/FILE_ADDED/READY |
| 3 | stroyka_estimate_canon.py | `_is_bad_estimate_result` + AC gate | 11 new forbidden phrases + regex позиций:1 + /root/ /tmp/ revision_context traceback engine: manifest:; AC gate bad_result check → FAILED |
| 4 | stroyka_estimate_canon.py | `_generate_and_send` totals block | Real openpyxl read-back: TOPIC2_PDF_TOTALS_MATCH_XLSX:xlsx=X:pdf=Y; MISMATCH → FAILED + user message |

---

## ПОЛНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ МАРКЕРОВ (верификация topic_2 после V5)

```
TOPIC2_CANONICAL_PHOTO_ROUTE_FIRST:attempting          # если фото
TOPIC2_CANONICAL_PHOTO_ROUTE_FIRST:handled             # или fallback_to_p6e2
TOPIC2_PDF_SPEC_EXTRACTOR_STARTED                      # если PDF
TOPIC2_PDF_SPEC_EXTRACTED:<N>_rows
TOPIC2_PDF_SPEC_ROWS_EXTRACTED:<N>
TOPIC2_OCR_TABLE_STARTED                               # если фото с таблицей
TOPIC2_OCR_TABLE_EXTRACTED:<N>_rows
TOPIC2_OCR_TABLE_ROWS_EXTRACTED:<N>
TOPIC2_MULTIFILE_PROJECT_CONTEXT_STARTED               # если >1 файл
TOPIC2_MULTIFILE_PROJECT_CONTEXT_FILE_ADDED:<name>
TOPIC2_MULTIFILE_PROJECT_CONTEXT_READY
TOPIC2_PRICE_CHOICE_CONFIRMED:median
TOPIC2_CANONICAL_OLD_ROUTE_HARD_BLOCK:pending_intercepted
TOPIC2_AFTER_PRICE_CHOICE_GENERATION_STARTED
TOPIC2_PRICE_MATERIAL_SEARCH_STARTED:<item>            # per-item
TOPIC2_PRICE_WORK_SEARCH_STARTED:<item>
TOPIC2_PRICE_SOURCE_FOUND:<item>:<supplier>:<status>
TOPIC2_PRICE_SOURCE_MISSING:<item>
TOPIC2_TEMPLATE_SELECTED:<name>
TOPIC2_XLSX_CANON_COLUMNS_OK:15
TOPIC2_PDF_TOTALS_MATCH_XLSX:xlsx=<N>:pdf=<N>
TOPIC2_DRIVE_TOPIC_FOLDER_OK
TOPIC2_LOGISTICS_DISTANCE_KM:<n>
TOPIC2_AC_GATE_OK
TOPIC2_TELEGRAM_DELIVERED:<msg_id>
FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:estimate_generated
TOPIC2_EXPLICIT_CONFIRM:from_user_done_command
TOPIC2_DONE_CONTRACT_OK
```

---

## BUGFIX3 — `2ece9eb` (3 live bugs from DB diagnostics)

| Патч | Файл | Что |
|------|------|-----|
| PATCH_PRICE_BIND_LOOP_TERMINATE_V1 | task_worker.py (append) | Если PRICE_BIND_POISON ≥3 раз для LATEST_PRICE_MENU_FALLBACK → FAILED немедленно |
| PATCH_RECURSION_LIMIT_RESTORE | stroyka_estimate_canon.py (body) | try/finally восстанавливает sys.getrecursionlimit() после openpyxl |
| PATCH_FCG_DONE_CONTRACT_BYPASS_V1 | task_worker.py (append) | TOPIC2_DONE_CONTRACT_OK в history → bypass FCG violation check |

Все три патча подтверждены в логе: `PATCH_PRICE_BIND_LOOP_TERMINATE_V1 installed`, `PATCH_FCG_DONE_CONTRACT_BYPASS_V1 installed`

---

## GAP_CLOSE4 — `c0300fb` (4 code gaps from audit)

| Патч | Файл | Что |
|------|------|-----|
| PATCH-GAP1 | stroyka_estimate_canon.py | TOPIC2_PRICE_ENRICHMENT_STARTED + DONE в _search_prices_online |
| PATCH-GAP2 | stroyka_estimate_canon.py | TOPIC2_PDF_CYRILLIC_ATTEMPTED → TOPIC2_PDF_CYRILLIC_OK |
| PATCH-GAP3 | sample_template_engine.py | fix {_p3pcg_has_explicit_price} → "confirmed" (function-object bug) |
| PATCH-GAP4 | task_worker.py | FCG bypass: DONE_CONTRACT_OK → AC_GATE_OK |

---

## TOPIC500 ADAPTIVE OUTPUT — `0c15037`

**PATCH_TOPIC500_ADAPTIVE_OUTPUT_V1** — wrapper вокруг `_p0_runtime_topic500_direct_search_20260504`

| Режим | Триггер (ключевые слова) | Что меняется |
|-------|--------------------------|--------------|
| procurement | купить/цена/поставщик/Avito/Ozon | ничего (стандарт) |
| normative | ГОСТ/СП/СНиП/норматив/стандарт | формат: название, пункт, применимость, ссылка |
| technical | технология/монтаж/инструкция/как сделать | формат: метод, шаги, нормативы, источник |
| download | скачать/APK/4PDA/программа | формат: одна ссылка, платформа, статус |
| news | новость/изменения/актуально | формат: факты, дата, источник |
| service | подрядчик/бригада/услуга/мастер | формат: название, контакт, ссылка, рейтинг |
| comparison | сравни/что лучше/разница | формат: таблица сравнения |
| troubleshooting | не работает/ошибка/как исправить | формат: причина, решение, шаги, docs |
| factual | всё остальное | формат: ответ, источник, что подтверждено |

---

## MEMORY DEDUP — `0d6a9a4`

**GAP-5: ARCHIVE_DUPLICATE_GUARD_V1**
- memory.db: добавлен `UNIQUE INDEX ON memory(chat_id, key)` — дубли блокируются на уровне БД
- task_worker.py lines 1076/1080/1084/3150: `INSERT INTO` → `INSERT OR REPLACE INTO`
- memory_api_server.py `/memory POST`: upsert по (chat_id, key) вместо plain INSERT
- memory_api_server.py `init_db()`: создаёт UNIQUE INDEX при старте
- До фикса: 694 дубля topic_500_task_summary, 7726 строк → 5184 после dedup

**GAP-6: PATCH_TOPIC500_SEARCH_POLLUTION_GUARD_V1**
- Wrapper вокруг `_save_memory` для topic_500: результат > 300 символов → сохраняется truncated summary
- Предотвращает засорение long_memory_context таблицами поставщиков

---

## OPEN CONTOURS (не закрыто)

1. **Live-verify topic_2** — задача с полным ТЗ в Telegram, проверить полную цепочку маркеров
2. **Live-verify topic_500** — проверить adaptive output: normative/factual запрос → правильный формат
3. **inbox_aggregator стабы** — IMAP/Telethon/Profi.ru коннекторы (P2, будущий канал)
4. **`_parse_price_sources` quality** — матчинг ключевых слов требует мониторинга

---

## ДИАГНОСТИКА С НУЛЯ

```bash
# 1. Воркер жив?
systemctl is-active areal-task-worker

# 2. Последние коммиты
git -C /root/.areal-neva-core log --oneline | head -5

# 3. Последняя topic_2 задача
sqlite3 -readonly /root/.areal-neva-core/data/core.db \
  "SELECT id, state, substr(result,1,80), updated_at FROM tasks
   WHERE COALESCE(topic_id,0)=2 ORDER BY updated_at DESC LIMIT 3;"

# 4. Маркеры задачи
sqlite3 -readonly /root/.areal-neva-core/data/core.db \
  "SELECT action, created_at FROM task_history WHERE task_id='TASK_ID' ORDER BY created_at;"
```

---

## CANON REFS

- `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md`
- `docs/CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md`
- `docs/HANDOFFS/LATEST_HANDOFF.md` (этот файл)
