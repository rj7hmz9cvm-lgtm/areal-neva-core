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
