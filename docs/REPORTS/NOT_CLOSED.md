# NOT_CLOSED — 28.04.2026

## P1
- Дублирование задач x2
- Голос 00:02 -> revision вместо confirm

## P2
- monitor_jobs.py — НЕТ ФАЙЛА НЕТ CRON
- SEARCH_MONOLITH_V1 — live-тест не проводился
- Промпт Perplexity в ai_router.py — не написан
- Excel =C2*D2 / =SUM — не реализованы
- КЖ PDF pipeline — не реализован
- Нормы СП/ГОСТ — не реализованы

---

## СЕССИЯ 29.04.2026 — ИТОГИ ПАТЧЕЙ

### УСТАНОВЛЕНО (SYNTAX_OK, active, не battle-tested)
- PIPELINE_INTEGRATION_V40: STALE_CONTEXT_GUARD, CACHE_READ, NEGATIVE_SELECTION, FILE_RESULT_GUARD подключены в pipeline
- PIPELINE_INTEGRATION_V41: жёсткий routing, strict search result guard, file/project result guard
- FILE_INTAKE_PROJECT_V41: route_file → project_engine при intent=project
- ESTIMATE_QUALITY_V41: price_normalize_v41, multi_offer_consistency_v41 подключены в _write_xlsx
- TEMPLATE_SYSTEM_V41: template_learn_v41, template_priority_v41, project_template_engine_v41
- get_clarification_message: добавлен пункт "Проектирование / Расчёт нагрузок"
- core/project_engine.py: создан, КЖ/КМ/КМД/АР/ОВ/ВК/ЭОМ/СС/ГП/ПЗ/СМ/ТХ

### P1 БАГ — НЕ ЗАКРЫТ (подтверждён живым тестом 29.04.2026 16:28)
- telegram_daemon.py строка 601: SHORT_VOICE_CONFIRM_WIRED
- голос 00:02-00:04 при AWAITING_CONFIRMATION → revision вместо confirm
- STT работает, текст распознаётся
- но _all_contours_short_voice_confirm перехватывает до worker
- нужно: читать STT текст → если "да/ок/принято" → confirm, иначе revision

### НЕ ЗАКРЫТО (код есть, live-тест не проводился)
- Смета PDF → Excel → Drive link
- КЖ PDF pipeline end-to-end
- DWG/DXF → Excel → Drive link
- Фото дефекта → акт → Drive link
- Шаблон → новый файл → Drive link
- Поиск цены → закупочный ответ с постпроцессингом
- project_engine end-to-end через Telegram

### ПОДТВЕРЖДЕНО ЖИВЫМ ТЕСТОМ
- Смета текстом → ответ получен ✅
- CP8 search type fix ✅
- Drive OAuth token.json ✅
- Worker active NRestarts=0 ✅

---

## ПАТЧИ 29.04.2026 — ФИНАЛЬНЫЙ ПРОХОД V41/V42

### УСТАНОВЛЕНО (SYNTAX_OK, active)
- PIPELINE_INTEGRATION_V41 — task_worker.py — cache read, stale guard, negative selection, file result guard
- FILE_INTAKE_PROJECT_V41 — file_intake_router.py — route_file → project_engine при intent=project
- ESTIMATE_QUALITY_V41 — estimate_engine.py — price_normalize_v41, multi_offer_consistency_v41
- TEMPLATE_SYSTEM_V41 — template_manager.py — template_learn_v41, template_priority_v41
- search_session TABLE — создана в core.db + memory.db
- VOICE_CONFIRM_EMPTY_REVISION_FIX_V42 — telegram_daemon.py — пустой голос не создаёт [REVISION]

### СТАТУС СЕРВИСОВ
- telegram-ingress: active ✅ BOT STARTED 16:38:18
- areal-task-worker: active ✅ NRestarts=0

### НЕ ЗАКРЫТО (live-тест не проводился)
- Голосовой confirm при AWAITING_CONFIRMATION — патч V42 установлен, тест не проводился
- Смета PDF → Excel → Drive
- КЖ PDF pipeline end-to-end
- DWG → Excel → Drive
- Фото дефекта → акт → Drive
- project_engine end-to-end через Telegram
- Поиск с постпроцессингом V41

---

## ИНЦИДЕНТ 29.04.2026 22:17 — ВОССТАНОВЛЕНИЕ ФАЙЛОВ

### ЧТО ПРОИЗОШЛО
GPT патч GEMINI_VISION удалил core/file_intake_router.py и другие файлы.
Файлы восстановлены из бэкапов 19:23-19:31.

### ВОССТАНОВЛЕНО ИЗ БЭКАПОВ
- core/file_intake_router.py ← bak.20260429_192333
- core/dwg_engine.py ← bak.20260429_142000
- core/estimate_engine.py ← bak.20260429_185518
- core/project_engine.py ← bak.20260429_193106
- core/template_manager.py ← bak.20260429_192333

### СТАТУС
SYNTAX_OK, active, NRestarts=0

### GEMINI VISION — НЕ ЗАКРЫТО
- core/gemini_vision.py — не создан
- "Анализ фото / Схема" — не добавлен в get_clarification_message
- intent=vision в route_file — не добавлен
- Патч GPT отклонён — удалял файлы


---

## СЕССИЯ 30.04.2026 — ПРИНЯТЫЕ РЕШЕНИЯ

### PATCH_FILE_INTAKE_NEEDS_CONTEXT_V1 — READY FOR DIAGNOSTICS → PATCH

Цель: Орик перестаёт запускать обработку файла без понятной задачи пользователя.
Статус: Логика закрыта. Диагностика + патч следующим шагом.
Файлы: task_worker.py, core/file_intake_router.py
Запрещено трогать: telegram_daemon.py, ai_router.py, reply_sender.py, google_io.py, .env

Полная входная цепочка:
INPUT (file/link/voice/text)
→ voice: STT internal, пользователь не видит
→ связать с предыдущим intent если был в topic_id
→ активная NEEDS_CONTEXT в topic_id? → добавить файл туда
→ duplicate guard (file_id/hash)
→ pin + memory lookup (макс 3 записи)
→ wrong-topic guard
→ если intent ясен → route_file → engine
→ если intent НЕ ясен → NEEDS_CONTEXT + меню по топику
→ ждать выбор (bot_message_id)
→ выбор парсится свободно ("1", "шаблон", "смета", "акт")
→ engine → только НОВЫЙ artifact
→ human ответ
→ AWAITING_CONFIRMATION
→ DONE только после подтверждения
→ memory + pin только после DONE

Главные запреты:
НЕ запускать engine без выбора пользователя
НЕ писать "Получил файл, обрабатываю"
НЕ спрашивать "правки" до результата
НЕ показывать STT текст
НЕ закрывать задачу без artifact
НЕ писать память до DONE
НЕ выдавать исходный файл как результат
НЕ показывать технические статусы пользователю
НЕ запускать engine в NEEDS_CONTEXT
НЕ плодить несколько NEEDS_CONTEXT в одном topic_id

Меню СТРОЙКА: 1.Смета / 2.Объёмы / 3.Excel / 4.Чертёж / 5.Шаблон
Меню ТЕХНАДЗОР: 1.Акт / 2.Ведомость / 3.Дефекты / 4.Нормы СП/ГОСТ / 5.Шаблон
Меню ПРОЕКТИРОВАНИЕ: 1.Шаблон проекта / 2.Структура / 3.Новый документ / 4.Проверить / 5.Таблицы
Меню DEFAULT: 1.Шаблон / 2.Смета / 3.Проект / 4.Новый документ / 5.Распознать / 6.Сохранить
Ссылка без команды: NEEDS_CONTEXT + меню ссылки
Multi-file: одна intake-сессия, одно меню по комплекту
Дубликат: "Этот файл уже был. Тогда делали: [кратко]. Повторить или другое?"
Отмена: "отбой/отмена/не надо" → CANCELLED
Шаблон: TEMPLATE_CANDIDATE pending до DONE
Финальный ответ: "Готово. Сделал [что]. Файл: [link]. Проверь. Всё правильно?"
Result guard: нет artifact → не закрывать
Маркеры лога: FILE_INTAKE_GUARD_HIT / FILE_NEEDS_CONTEXT_SET / FILE_CHOICE_PARSED / FILE_ROUTE_STARTED / FILE_ARTIFACT_READY / FILE_NO_ARTIFACT_BLOCKED
Статус-фильтр: только VERIFIED/INSTALLED/RESTORED
Rollback: если worker не active → откатить оба файла из .bak
Обратная совместимость: текстовые задачи без файлов → старая логика не трогается
