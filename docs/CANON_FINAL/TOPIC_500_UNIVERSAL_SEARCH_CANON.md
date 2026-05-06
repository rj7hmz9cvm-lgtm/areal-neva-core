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
