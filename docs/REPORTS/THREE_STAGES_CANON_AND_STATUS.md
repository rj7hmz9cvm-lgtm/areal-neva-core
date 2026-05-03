# THREE STAGES — CANON LOGIC AND CURRENT STATUS
Version: 2026-05-03 | Mode: FACT-ONLY

## 1. СМЕТА / СТРОЙКА / topic_2

### Откуда образцы
Google Drive: AI_ORCHESTRA / ESTIMATES / templates
Drive folder ID: 19Z3acDgPub4nV55mad5mb8ju63FsqoG9
Файлы: М-80.xlsx, М-110.xlsx, Ареал Нева.xlsx, фундамент_Склад2.xlsx, крыша и перекр.xlsx
Серверный код: /root/.areal-neva-core/core/stroyka_estimate_canon.py

### Как должно работать
1. Задача в topic_2
2. Если есть работы + объёмы + цены — считать по текущему тексту
3. Если данных нет — выбрать шаблон из ESTIMATES/templates
4. Если нужны актуальные цены — искать и предлагать на подтверждение
5. До подтверждения цен XLSX/PDF не создавать
6. После подтверждения Python считает по формулам шаблона
7. Выход: XLSX с формулами + PDF + итог + ссылки
8. После "да" — DONE

### Что запрещено
- Брать файлы из topic_2 как шаблоны (это папка результатов)
- Брать старые сметы из истории
- Считать цифры через LLM
- Подставлять старый Drive-результат как новый

### Статус закрытия
CLOSED_BY_CODE: stroyka_estimate_canon.py подключён, SQL pick bug закрыт, direct item engine добавлен, guard инвариантов добавлен
LIVE_TEST: REQUIRED — по новой смете
CODE_CLOSED: DOCX_CREATE_FAILED class fixed by SHEETS_NORMALIZE_V1 in project_engine.py; sheet_register list[str] normalized before sh.get usage

---

## 2. ПРОЕКТИРОВАНИЕ / topic_210

### Откуда образцы
Google Drive: AI_ORCHESTRA / chat_-1003725299009 / topic_210 / Образцы проектов
Серверная память: /root/.areal-neva-core/data/project_templates/PROJECT_TEMPLATE_MODEL__*.json
Серверный код: /root/.areal-neva-core/core/project_engine.py + project_document_engine.py

Файлы образцов: АР.pdf, КЖ.pdf, КД.pdf, Шувалово Озерки АР/КЖ/КД, Барн КЖ, КЖ Цоколь, Дом у озера, Проект М-80 КД финал, АК-160 PLN+PDF

### Разделы которые система должна понимать
ПЗ, ГП, АР, КЖ, КМ, КМД, КР/КД, ОВ, ВК, ЭОМ, СС, ТХ, СМ

### Как должно работать
1. ТЗ или файл в topic_210
2. Текущее ТЗ — главный источник
3. Структура берётся из Образцы проектов
4. Если есть PROJECT_TEMPLATE_MODEL — использует его
5. Определяет весь состав проекта, не один раздел
6. По каждому разделу берёт нормы из локальной карты норм
7. Формирует полный проектный пакет
8. Выход: DOCX/PDF + спецификации + ведомости + приложения (Excel только приложение)
9. После "да" — DONE

### Пример для ангара
Объект: ангар 24x80 м, монолитная плита, МК каркас, ППУ стены 100мм, ППУ кровля 150мм, высота 5м, ворота в торце
Результат: ПЗ + ГП + АР + КЖ + КМ + КМД + КД + спецификации + ведомости + нормы

### Что запрещено
- Делать только один раздел КЖ без полного пакета
- Выдавать Excel как проект
- Брать случайные старые файлы из истории
- Закрывать DONE без полного проектного пакета
- Отвечать "файлы в топике уже есть" вместо результата

### Статус закрытия
CLOSED_BY_CODE: project_engine.py подключён, PROJECT_TEMPLATE_MODEL извлечение добавлено, КЖ/КД/АР определение по имени файла исправлено, нормы и структура разделов добавлены
LIVE_TEST: REQUIRED — full package route не проверен
CODE_CLOSED_1: list-query/no-file guard exists in project_route_guard.py as CANON_LIST_QUERY_GUARD_V1 and is preserved by final code close
BUG_OPEN_2: data/project_templates/ на сервере не синхронизирован с Drive/Образцы проектов

---

## 3. ИНТЕРНЕТ-ПОИСК / topic_500

### Откуда данные
Только живой интернет через Perplexity/online model
Серверный код: core/search_session.py, core/file_memory_bridge.py, task_worker.py
Drive папка topic_500: ПУСТАЯ (так и должно быть)

### Как должно работать
1. Запрос в topic_500
2. Файловая память НЕ перехватывает запрос
3. Старые задачи НЕ используются как ответ
4. Запрос уходит в живой интернет
5. Собираются источники, ссылки, цены, риски
6. Таблица: Поставщик / Площадка / Тип / Город / Цена / Наличие / Доставка / TCO / Trust Score / Риски / Статус / Ссылка / checked_at
7. Итог: лучший вариант + надёжный + что проверить
8. После "да" — DONE

### Что запрещено
- Отвечать из файловой памяти
- Брать старые документы или сметы
- Давать список ссылок без анализа
- Закрывать DONE при qg=unknown
- Зацикливать задачу

### Статус закрытия
CLOSED_BY_CODE: SearchMonolithV2 подключён, topic_500 изолирован от файлового follow-up (CANON_ROUTE_FIX_V2), формат таблицы Trust Score добавлен, search session memory добавлена
LIVE_TEST: REQUIRED — qg=unknown может зациклить
CODE_GUARD_PRESENT: FILE_TECH_CONTOUR_FOLLOWUP_V2 has topic_500 isolation in task_worker.py; final code close preserves this guard

---

## ОБЩИЙ ФИНАЛЬНЫЙ ФОРМАТ ОТВЕТА БОТА

Задача выполнена
Направление: стройка / проектирование / поиск
Основа: откуда взяты данные
Что сделано: кратко
Артефакты: ссылки
Статус: AWAITING_CONFIRMATION
Подтверди: да / правки / отмена

---

## ИТОГ

Сметы: из ESTIMATES/templates + текущее ТЗ
Проекты: из topic_210/Образцы проектов + PROJECT_TEMPLATE_MODEL
Поиск: только живой интернет

Результат всегда: артефакт или таблица — подтверждение — DONE


---

## CODE CLOSE UPDATE — THREE_STAGES_CODE_CLOSE_FINAL_STRICT_V1
updated_at_utc: 2026-05-03T17:01:50.633925+00:00

CODE_CLOSED_BY:
- ESTIMATE_PRIORITY_FIX_V1
- SHEETS_NORMALIZE_V1
- CANON_LIST_QUERY_GUARD_V1 preserved
- FILE_TECH_CONTOUR_FOLLOWUP_V2 topic_500 isolation preserved

CODE_SCOPE:
- topic_2 estimate/project misroute closed by estimate priority rule
- topic_210 sheet_register string crash closed by normalization
- topic_210 list/no-file route remains non-artifact by existing guard
- topic_500 file-followup isolation remains active by existing task_worker guard

REGRESSION_LOCK:
- task_worker.py not patched
- telegram_daemon.py not patched
- core/reply_sender.py not patched
- google_io.py not patched
- core/ai_router.py not patched
- Drive/OAuth not patched
- lifecycle logic not patched
- memory schema not patched
