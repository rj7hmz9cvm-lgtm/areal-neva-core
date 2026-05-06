# HANDOFF — 2026-05-07 SESSION CLOSE
**Сессия**: 2026-05-06 22:47 → 2026-05-07 ~01:00 MSK
**Текущий HEAD**: `c7c8755` (до push'а этой сессии)
**Сервер**: 89.22.225.136, areal-task-worker active

## ЧТО ЗАКОММИЧЕНО В MAIN

### `d1f20a0` (06.05 22:31) — mega-guards V1 (append-wrappers)
6 wrappers в конец task_worker.py: CANCEL_GUARD · FRESH_ESTIMATE_FALLBACK · PRICE_REPLY_REVIVE · PRICE_TIMEOUT_GUARD · DONE_OVERRIDE_INVALID_PUBLIC · STROYKA_PARENT_AWARE_MISSING_QUESTION.

**Live-test factual conclusion**: 5 из 6 НЕ срабатывают. Append-wrapper в конце файла не цепляет код-путь, если функция уже обёрнута раньше. Документировано в session memory.

### `c7c8755` (06.05 23:50) — INLINE_FIX V1 (body edits)
- `_p6e67_try_merge`: state guard + fresh estimate dispatch перед terminal guard
- FCG `_update_task` wrapper: bypass INVALID_PUBLIC_RESULT при 5 markers + Drive link
- `_t2v5_/_t2v6c_` price-bind: explicit token required, max raw 80 chars
- V1 wrappers (14898-15256) помечены SUPERSEDED

**Live-test (replay 3 задач cf15cc9b/f1ef9fab/71adbe24)**:
- ✅ Маркер `V5/V6C_PRICE_REJECTED:no_explicit_token_or_long` появился (D работает — длинные тексты не считаются price-choice)
- ⚠️ Маркер `FRESH_ESTIMATE_DISPATCHED` НЕ появился — `_find_parent` нашёл parent для cf15cc9b, ушло в P6E67_MERGED, а не в terminal guard

## КРИТИЧЕСКАЯ ПРОБЛЕМА — НЕ ЗАКРЫТА

**`FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3`** (`core/stroyka_estimate_canon.py:1178`) — старый route, перехватывает раньше V2 в `_handle_new` через hook на task_worker.py:1313. Выдаёт пользователю старый формат:
```
✅ Предварительная смета готова

Объект: дом
Эталон: М-80.xlsx
Лист эталона: Каркас под ключ
Выбор цены: median
Разделы:
- Фундамент
- Стены
- Перекрытия
- Кровля
- Логистика
- Накладные расходы
```

Это **не canonical** (только 6 разделов из 11, 8-колоночный XLSX вместо 15, без AREAL_CALC, без template-based copy).

## ЧТО ОПРЕДЕЛИЛИ ЗА СЕССИЮ (новые каноны)

1. `TOPIC_500_UNIVERSAL_SEARCH_CANON.md` — universal adaptive search (16 режимов), procurement — один из них
2. `TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md` — 5 шаблонов / 15-col AREAL_CALC / 11 секций / scoring / sheet selection / DONE contract / final response format
3. **5 шаблонов скачаны** локально в `data/templates/estimate/cache/`:
   - М-80.xlsx (403kb, sheets «Каркас под ключ» + «Газобетон_под ключ»)
   - М-110.xlsx (12kb)
   - Ареал Нева.xlsx (151kb)
   - фундамент_Склад2.xlsx (16kb)
   - крыша и перекр.xlsx (58kb)

## ЧТО НЕ ЗАКРЫТО

### topic_2 STROYKA — главное
- **`PATCH_TOPIC2_FULL_CANONICAL_CLOSE_ONEPASS_V1`** не применён. Backups сделаны, кода нет.
  Должен реализовать:
  - Заменить `_make_artifacts` в V2 на template-based + AREAL_CALC 15 cols
  - Canonical guard в `_handle_new` (line 1310) ДО V3 hook (line 1313)
  - Old output blocker в FCG `_update_task`
  - Drive download on-demand (cache first)
  - 11 секций с интерьером (санузел/кухня/спальня + ИК-полы/имитация бруса)
  - Live price enrichment через `core/price_enrichment.py` + Perplexity
  - PDF через `core/pdf_cyrillic.py` (`create_pdf_with_cyrillic` + `validate_cyrillic_pdf`)
  - Clean Telegram format по контракту §9 TOPIC_2_CANONICAL
- `_p2_create_xlsx` (sample_template_engine.py) — 8 колонок vs 15
- Свободный текст ТЗ (без готовой таблицы) — engine не умеет разложить на секции
- Уточнение параметров может зацикливаться

### topic_500 SEARCH
- Базовая procurement-таблица работает («Поставщик|Площадка|Цена|Ссылка|Проверено»)
- НЕ реализована adaptive output по intent — все идёт через procurement формат
- НЕ реализованы режимы: normative · download · technical · news · comparison · local · factual
- Forbidden patterns blocker отсутствует

### topic_5 ТЕХНАДЗОР
- Стабилен (57 DONE / 52 FAILED за 7д)
- 16 INVALID_RESULT_GATE — акт без артефакта
- Блокер `ddfc12b1` закрыт

### Memory / archive
- `MEMORY_QUERY_GUARD_V1` не перехватывает «что обсуждали», «какие задачи были» → попадают в estimate route → P6E67 terminal
- Archive context для memory-вопросов не подключён к engine

## ФАЙЛЫ ИЗМЕНЁННЫЕ В ЭТОЙ СЕССИИ
- `task_worker.py` (commit `c7c8755`)
- Backup'ы для следующей итерации:
  - `*.bak.PATCH_INLINE_FIX_20260506`
  - `*.bak.PATCH_TOPIC2_FULL_CANONICAL_CLOSE_ONEPASS_V1`
- `~/.claude/settings.json` (allowlist расширен — global)

## КОМАНДЫ ДЛЯ СЛЕДУЮЩЕЙ СЕССИИ
```bash
cd /root/.areal-neva-core
git log --oneline | head -3                # должен видеть c7c8755 и/или session-close commit
ls data/templates/estimate/cache/          # 5 шаблонов в кэше
sqlite3 -readonly data/core.db "SELECT state,COUNT(*) FROM tasks WHERE topic_id=2 AND created_at >= datetime('now','-24 hours') GROUP BY state;"
journalctl -u areal-task-worker --since '5 minutes ago' --no-pager
```

## ПРИОРИТЕТ СЛЕДУЮЩЕЙ СЕССИИ
1. **Реализовать PATCH_TOPIC2_FULL_CANONICAL_CLOSE_ONEPASS_V1** — главный блокер
2. Адаптивный output для topic_500 по 16 режимам
3. MEMORY_QUERY_GUARD_V1 для статусных запросов
4. INVALID_RESULT_GATE топик_5 — акт без артефакта
