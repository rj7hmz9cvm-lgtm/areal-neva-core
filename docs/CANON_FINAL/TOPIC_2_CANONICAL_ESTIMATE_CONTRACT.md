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
