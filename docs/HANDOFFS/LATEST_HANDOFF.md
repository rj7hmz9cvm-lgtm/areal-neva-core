# LATEST_HANDOFF — 06.05.2026 TOPIC2_STROYKA_FULL_PIPELINE_STATUS

## СЕССИЯ 06.05.2026 — РАЗДЕЛ СТРОЙКА (TOPIC_2) — ДИАГНОСТИКА + ЧАСТИЧНОЕ ЗАКРЫТИЕ

---

## ПОЛНОЕ ТЕХНИЧЕСКОЕ ЗАДАНИЕ (ТЗ) — что было поставлено

30-секционное ТЗ на полный запуск раздела STROYKA (topic_2):

1. Входные данные: голос/текст/фото → смета
2. Объект: дом/ангар/склад/гараж/баня и т.д.
3. Уточнение параметров если недостаточно данных (материал, этажность, площадь, город)
4. Смета по 11 разделам (фундамент/монолит/кровля/etc.)
5. Статус/мета-запросы НЕ должны запускать пайплайн
6. Цены из Perplexity → с поставщиком, URL, датой
7. XLSX: 15 колонок + лист AREAL_CALC, НДС
8. PDF: кириллица через DejaVuSans, валидация
9. Загрузка в Google Drive папку 19Z3acDgPub4nV55mad5mb8ju63FsqoG9
10. Ссылки в Telegram ответе
11. DONE contract: 14 маркеров в task_history
12. Финальный ответ без MANIFEST/путей
13. Цены не выдумываются — только из Perplexity или пустая колонка
14. Под ключ = финишный + черновой + работы

---

## ЧТО ЗАКРЫТО В ПРЕДЫДУЩИХ СЕССИЯХ (до 06.05.2026)

| Задача | Статус | Файл/Патч |
|--------|--------|-----------|
| reportlab установлен | ✅ | .venv |
| PDF кириллица + валидация | ✅ | PATCH_TOPIC2_PDF_CYRILLIC_VALIDATE_V1 |
| DONE contract 14 маркеров | ✅ | PATCH_TOPIC2_DONE_CONTRACT_FALLBACK_V1 |
| XLSX canonical (AREAL_CALC + доп. колонки) | ✅ | PATCH_TOPIC2_CANONICAL_XLSX_V1 |
| Чистый ответ (без MANIFEST, без путей) | ✅ | PATCH_TOPIC2_CLEAN_RESULT_V1 |
| Price enrichment только по выбору 1/2/3/4 | ✅ | PATCH_TOPIC2_PRICE_AUTO_REVERT_V1 |
| Routing NEW→IN_PROGRESS для свежих смет | ✅ | PATCH_TOPIC2_FULL_PIPELINE_ROUTE_V1 |

---

## ГЛАВНАЯ ОТКРЫТАЯ ПРОБЛЕМА (НЕ ЗАКРЫТА — НУЖНО ПОЧИНИТЬ)

### Суть бага
Бот задаёт один и тот же вопрос в loop. Задачи дают результат "Позиций: 1" вместо полной сметы.

### Root cause (диагностировано 06.05.2026)
`PATCH_TOPIC2_FRESH_ESTIMATE_ROUTE_GUARD_V1` (task_worker.py:13985) перехватывает ВСЕ topic_2 задачи РАНЬШЕ моего патча:

- **Фото** → идут через `_handle_drive_file` → `_t2fer_run_final_estimate(reason=DRIVE_FILE_FRESH_ESTIMATE)`
- **Голос/текст** → идут через `_p6e67_try_merge` → `_t2fer_run_final_estimate(reason=BYPASS_P6E67_PARENT_LOOKUP)`

Мой `PATCH_TOPIC2_FULL_PIPELINE_ROUTE_V1` оборачивает только `_handle_new` — но задачи до него не доходят.

`_t2fer_run_final_estimate` вызывает `handle_topic2_estimate_final_close` (v2, упрощённый путь) из `core/topic2_estimate_final_close_v2.py` — ЭТО НЕ ПОЛНЫЙ ПАЙПЛАЙН.

Нужный полный пайплайн: `handle_topic2_one_big_formula_pipeline_v1` в `core/sample_template_engine.py` (последняя версия ~line 7264), вызываемый через P2/P3 overlay в `_handle_in_progress`.

### Готовый фикс (добавлен в этой сессии)
`PATCH_TOPIC2_REDIRECT_FINAL_TO_FULL_PIPELINE_V2` в конце task_worker.py:
- Оборачивает `_t2fer_run_final_estimate`
- Для topic_2: вместо упрощённого пути вызывает `_handle_in_progress` (полный P2/P3 пайплайн)
- Для остальных топиков: оригинальное поведение

### Подтверждение из логов
```
19:02:22 T2FER_FINAL_ESTIMATE_OK task=9d8ae7ac reason=DRIVE_FILE_FRESH_ESTIMATE   ← упрощённый путь
19:03:12 T2FER_FINAL_ESTIMATE_OK task=1fe76b60 reason=BYPASS_P6E67_PARENT_LOOKUP  ← упрощённый путь
```
Результат: "Позиций: 1" вместо полной 11-секционной сметы.

---

## ДРУГИЕ ОТКРЫТЫЕ ЗАДАЧИ (из ТЗ)

| Задача | Статус | Приоритет |
|--------|--------|-----------|
| `_p2_create_xlsx` — 8 колонок вместо 15 канонических | ❌ открыто | HIGH |
| Статус/мета-запросы ("статус", "где результат") не запускают пайплайн | ❌ не проверено | MEDIUM |
| Цены из Perplexity в полном пайплайне (supplier/url/checked_at) | ❌ не проверено | HIGH |
| Уточнение параметров (этажность/материал/город) — не loop | ❌ не проверено | HIGH |
| DONE contract 14 маркеров в полном пайплайне | ❌ не проверено | MEDIUM |

---

## АРХИТЕКТУРА — КАК РАБОТАЕТ ПОЛНЫЙ ПАЙПЛАЙН

```
Telegram → задача topic_2 NEW
    → _handle_new  (мой патч PATCH_TOPIC2_FULL_PIPELINE_ROUTE_V1)
        → если свежая смета → IN_PROGRESS → _handle_in_progress
            → P3 overlay (PATCH_TOPIC2_FRESH_ESTIMATE_ROUTE_GUARD_V1)
                → P2 overlay (P2_FINAL_SEARCH_AND_ESTIMATE_CLOSE_20260504_V1)
                    → handle_topic2_one_big_formula_pipeline_v1 (sample_template_engine.py ~line 7264)
                        → уточнение данных (если нужно)
                        → _p2_build_rows (11 разделов)
                        → _p2_create_xlsx (8 колонок, нужно 15)
                        → _write_estimate_pdf (с cyrillic validation)
                        → Google Drive upload
                        → Telegram reply
```

**Проблема**: `PATCH_TOPIC2_FRESH_ESTIMATE_ROUTE_GUARD_V1` также оборачивает `_handle_drive_file` и `_p6e67_try_merge` — и они срабатывают РАНЬШЕ `_handle_new`.

---

## КЛЮЧЕВЫЕ ФАЙЛЫ

| Файл | Назначение |
|------|-----------|
| `task_worker.py` | Основной воркер, все патчи |
| `core/sample_template_engine.py` | Полный пайплайн `handle_topic2_one_big_formula_pipeline_v1` |
| `core/topic2_estimate_final_close_v2.py` | УПРОЩЁННЫЙ путь (v2) — НЕ полный пайплайн |
| `core/price_enrichment.py` | Обогащение цен Perplexity |
| `core/pdf_cyrillic.py` | PDF с кириллицей + валидация |

---

## ЗАПРЕЩЁННЫЕ ФАЙЛЫ — НЕ ТРОГАТЬ

`.env`, `credentials.json`, `ai_router.py`, `reply_sender.py`, `google_io.py`, `telegram_daemon.py`

## ПРАВИЛА ПАТЧЕЙ

- Все изменения **только append** к концу файлов
- Перед каждым патчем прочитать: `CANON_FINAL/01_SYSTEM_LOGIC_FULL.md` + `HANDOFFS/LATEST_HANDOFF.md`
- Перед git push: `mv tools/context_aggregator.py /tmp/` → push → restore

---

## СЛЕДУЮЩИЙ ШАГ ДЛЯ СЛЕДУЮЩЕЙ МОДЕЛИ

**Приоритет 1 (блокер)**: Проверить что `PATCH_TOPIC2_REDIRECT_FINAL_TO_FULL_PIPELINE_V2` в task_worker.py работает:
```bash
journalctl -u areal-task-worker -f | grep -E "T2FP|T2RFP|PIPELINE|PICKED|topic=2"
```
Ожидаемый лог: `T2RFP_REDIRECT task=... → full pipeline` вместо `T2FER_FINAL_ESTIMATE_OK reason=...`

**Приоритет 2**: Исправить `_p2_create_xlsx` → 15 канонических колонок (sample_template_engine.py)

**Приоритет 3**: Тест end-to-end: голос "посчитай смету на дом 150м2, газобетон, 2 этажа, Москва" → должна прийти реальная смета с ценами

---

*Handoff written: 2026-05-06*
