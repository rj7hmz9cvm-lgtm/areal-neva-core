# ORCHESTRA_MASTER_BLOCK — ЦЕЛЕВАЯ АРХИТЕКТУРА ОРКЕСТРА
Версия: v1 | Дата: 28.04.2026 | Верифицировано: Claude + GPT

---

## БЛОК 1 — TECHNICAL FILE PIPELINE

### Цель
Любой файл из Telegram/Drive → полный цикл → артефакт → пользователю.

### Pipeline (8 стадий — все обязательны)
INGESTED → DOWNLOADED → PARSED → CLEANED → NORMALIZED → CALCULATED → ARTIFACT_CREATED → UPLOADED

### Что должно работать
PDF / XLSX / CSV           → XLSX смета с формулами (=C2*D2, =SUM)
Фото таблицы               → XLSX
Фото дефекта               → DOCX/PDF акт + нормы СП/ГОСТ
DWG/DXF                    → отчёт (или FAILED:DWG_NOT_IMPLEMENTED)
Шаблон                     → новый файл по образцу
Несколько файлов           → один артефакт

### Движки
estimate_engine.py         — сметы, объёмы, формулы
ocr_engine.py              — фото → таблица
technadzor_engine.py       — дефекты + нормы СП/ГОСТ/СНиП
dwg_engine.py              — чтение через ezdxf
template_manager.py        — шаблоны
file_intake_router.py      — маршрутизация файлов

### Жёсткое правило
Python считает и создаёт файлы.
LLM анализирует смысл.
LLM НЕ считает финальные цифры.
LLM НЕ создаёт артефакт на глаз.

### FILE_RESULT_GUARD
если input_type = file:
  → обязательно: результат + ссылка + статус
  иначе → FAILED

### Критерий закрытия
файл принят → обработан → артефакт → Drive/GitHub link → Telegram → AWAITING_CONFIRMATION

---

## БЛОК 2 — MULTI-MODEL ORCHESTRA LAYER

### MODEL_ROUTER (1 точка выбора)
если фото/схема       → Gemini
если поиск            → Perplexity
если структурирование → Mistral
если reasoning        → Cerebras
если расчёт           → Python ONLY
если финальный ответ  → DeepSeek
если fallback         → Cloudflare → HuggingFace

### PRE_OPENROUTER_MODEL_LAYER
task_worker → ORCHESTRA_SHARED_CONTEXT → MODEL_ROUTER → specialist models → OpenRouter/DeepSeek → RESULT_VALIDATOR → HUMAN_DECISION_EDITOR → Telegram

### Роли моделей
Gemini     — фото, схемы, таблицы, OCR, visual reasoning
Mistral    — структуризация, нормализация, классификация
Cerebras   — быстрый reasoning, проверка логики
Cohere     — rerank, фильтрация, чистка контекста
Perplexity — внешний поиск (нормы, цены, поставщики, СП/ГОСТ)
DeepSeek   — основной исполнитель, финальная сборка
Claude     — контроль, канон, верификация, ТЗ
GPT        — патчи кода, сервер
Python     — расчёт, Excel, файлы, валидация

### Жёсткое правило
Ни одна модель не отвечает пользователю напрямую.
Финал всегда: validator → HUMAN_DECISION_EDITOR → Telegram.
Модели = инструменты, не конкуренты.

### ORCHESTRA_SHARED_CONTEXT
Каждая модель получает: ONE_SHARED_CONTEXT + memory.db + core.db active task + pin + topic role + history + files

### RESULT_VALIDATOR
Проверить перед отправкой: цена / контакт / ссылка / ТТХ / единица измерения.
Если нет → INVALID_RESULT → не отправлять.

### RESULT_FORMAT_ENFORCER
Обязательно в финале: таблица + выводы (CHEAPEST/MOST_RELIABLE/BEST_VALUE) + блок «что проверить звонком».
Если нет → RESULT_INVALID → доработка.

### HUMAN_DECISION_EDITOR
Технический результат → человеческое решение.
Формат: 1.Что произошло 2.Что это значит 3.Что делать 4.Риски 5.Следующий шаг

### USER_MODE_SWITCH
TECH  → полный технический разбор
HUMAN → коротко и по делу (default)

### FALLBACK_CHAIN
Gemini → Mistral → Cloudflare → HuggingFace
Оркестр не падает никогда.

### MODE_SWITCH
LIGHT — простая задача → 1 модель
FULL  — сложная задача → полный оркестр

### MODEL_REGISTRY
gemini: vision | mistral: text | cerebras: reasoning | perplexity: search | deepseek: final | cloudflare: fallback | hf: fallback
Новая модель = 1 строка.

### EXECUTION_PRIORITY (верифицировано GPT)
FILE > SEARCH > CHAT
Иначе оркестр болтает когда надо считать смету.

---

## БЛОК 3 — GITHUB SSOT + AGGREGATOR

### Архитектура памяти
GitHub = мозг (каноны + логика + shared context)
Сервер = runtime (обработка, memory.db, core.db)
Drive  = резерв (DWG, PDF, фото входящие)

### Поток
чат/выгрузка → агрегатор → ONE_SHARED_CONTEXT → GitHub → все нейросети читают GitHub

### Drive Knowledge Aggregator
ВХОД: CHAT_EXPORTS (14bYA9bHaKahkE8d4IDwWxL4Ojn-G0sDl) + CANON_FINAL (1U_IrEOtIJfUVAdjH-kHwms2M2z3FXan0)
ВЫХОД: docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md + ONE_SHARED_CONTEXT.json + LAST_AGGREGATION_REPORT.md
ЛОГИКА: новая выгрузка → читает → отделяет факты от мусора → раскладывает по разделам → обновляет ONE_SHARED_CONTEXT → человек утверждает что входит в CANON_FINAL

### Что агрегатор НЕ делает
Не чинит код. Не переписывает канон самовольно. Не сохраняет FAILED как память. Не тащит секреты.

### GITHUB_SSOT_RULES
ЗАПРЕЩЕНО: перезатирать, удалять, упрощать каноны.
РАЗРЕШЕНО: только добавление, версионирование v1/v2/v3.
secret_scan.sh обязателен перед push.
USER_APPROVAL_GATE: канон меняется только после явного да.

### Реализация агрегатора
GAS v1   — Drive-агрегатор (читает → индексирует → пишет md/json)
Python v2 — серверный агрегатор с LLM через OpenRouter

---

## ПОЛНЫЙ СПИСОК БЛОКОВ

P1 — реализовать первым:
TECHNICAL_FULL_CONTOUR | MODEL_ROUTER полный | PRE_OPENROUTER_MODEL_LAYER | FALLBACK_CHAIN
RESULT_VALIDATOR | RESULT_FORMAT_ENFORCER | FILE_RESULT_GUARD | INTENT_LOCK
DUPLICATE_TASK_GUARD | PRICE_NORMALIZATION | MULTI_OFFER_CONSISTENCY | CONSTRAINT_ENGINE
AVAILABILITY_CHECK | CONTACT_VALIDATION | REVIEW_SOURCE_WEIGHT | SEARCH_STATE_CONTROL
OUTPUT_DECISION_LOGIC | ORCHESTRA_SHARED_CONTEXT | HUMAN_DECISION_EDITOR | USER_MODE_SWITCH
AGGREGATOR (GAS v1) | MODEL_SPECIALIZATION | MEMORY_FILTER | SECURITY_SCOPE | EXECUTION_PRIORITY

P2 — после P1:
TASK_SPLITTER | MODE_SWITCH | CACHE_LAYER | MODEL_REGISTRY | SEARCH_PRESETS | SEARCH_DEPTH_LIMIT
SOURCE_DEDUPLICATION | TIME_RELEVANCE | REGION_PRIORITY | NEGATIVE_SELECTION | MODEL_RESULT_MERGE
MODEL_VOTING | ARTIFACT_VERSIONING | SOURCE_TRACE | AUDIT_LOG | STALE_CONTEXT_GUARD
LIVE_MARKET_SCAN | ERROR_EXPLAINER | DATA_CLASSIFICATION

P3 — мониторинг рынка:
PRICE_DRIFT_MONITOR | INVENTORY_BURN_MONITOR

---

## УЖЕ ЕСТЬ В КАНОНЕ (НЕ ДЕЛАТЬ ПОВТОРНО)
FSM pipeline | File pipeline 8 стадий | FAILED коды + таймауты | SEARCH 14 этапов
Trust Score 0-100 | SELLER_RISK | TCO | Шаблон звонка | Патч-протокол 8 шагов
GitHub SSOT регламент | secret_scan pre-commit | ROLLBACK_POINT | USER_APPROVAL_GATE
HEALTHCHECK | PRICE_AGING +5-10%

---

## MULTI_MODEL_ORCHESTRA_ACTUAL_STATE_2026_04_29

### ACTIVE MODELS (CANON)
Gemini     — vision / OCR / схемы / таблицы  
Mistral    — структуризация / нормализация  
Cerebras   — reasoning / логика  
Cohere     — rerank / фильтрация  
Perplexity — поиск (СП/ГОСТ/цены/поставщики)  
DeepSeek   — финальный ответ (DEFAULT)  
Claude     — канон / проверка / ТЗ  
GPT        — сервер / код / патчи  
Python     — расчёт / Excel / файлы  

### MODEL_ROUTER (TARGET LOGIC)
photo/schema      → Gemini  
search            → Perplexity  
structure         → Mistral  
reasoning         → Cerebras  
calculation       → Python ONLY  
final             → DeepSeek  

### FALLBACK_CHAIN (TARGET)
Gemini → Mistral → Cloudflare → HuggingFace  

### STATUS
- модели описаны в каноне ✔  
- MODEL_ROUTER — НЕ реализован  
- FALLBACK_CHAIN — НЕ реализован  
- MODEL_REGISTRY — НЕ реализован  
- MULTI-MODEL EXECUTION — НЕ реализован  

### CRITICAL RULE
Сейчас оркестр работает как:
1 модель (DeepSeek) + поиск (Perplexity)

Полный multi-model НЕ запущен
