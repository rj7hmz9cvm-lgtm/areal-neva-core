# SEARCH_MONOLITH_V1
Версия: v1 FINAL | 28.04.2026 | topic_500
Статус: КАНОН — live-тест не проводился

## СУТЬ
Цифровой снабженец. Не ищет — даёт закупочное решение.
Результат: что брать / где / почему / риски / что проверить звонком

## 14 ЭТАПОВ
1. Разбор запроса
2. Уточнения макс.3
3. Search Session (уточнения = продолжение, не новая задача)
4. Расширение 7+ формул
5. Цифровой двойник (по параметрам, не по названию)
6. Источники (Ozon WB Avito 2GIS Exist Drom VK Telegram)
7. Проверка источника (CONFIRMED/PARTIAL/UNVERIFIED/RISK)
8. Детектор живости (checked_at + source_url обязательны)
9. Отзывы + Review Trust Score 0-100
10. Микрометр (толщина, цинк, OEM)
11. Запрет смешивать ТТХ
12. Risk Score + SELLER_RISK
13. TCO
14. Живой рынок

## TRUST SCORE
80-100 живые / 60-79 частично / 40-59 звонок / 0-39 фейк

## СТАТУСЫ
CHEAPEST / MOST_RELIABLE / BEST_VALUE / FASTEST / RISK_CHEAP / REJECTED

## РЕАЛИЗАЦИЯ
Шаг 1 DONE: is_search -> Perplexity (28.04.2026)
Шаг 2: промпт в ai_router.py
Шаг 3: search_session в memory.db
Шаг 4: Risk+Trust через LLM
Шаг 5 PRO: Telethon
