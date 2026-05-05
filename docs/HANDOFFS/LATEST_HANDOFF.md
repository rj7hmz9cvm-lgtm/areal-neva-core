# LATEST_HANDOFF — 05.05.2026 TOPIC5_TECHNADZOR_FINAL_DOCS

## СЕССИЯ 05.05.2026 — TOPIC5 ТЕХНАДЗОР ДОКУМЕНТАЦИЯ ФИНАЛИЗИРОВАНА

### Что сделано
- Все unified_context файлы созданы/исправлены (12 файлов)
- TOPIC5_DOCUMENT_OUTPUT_CONTRACT.md/.json — задокументирован контракт вывода
- TOPIC5_RUNTIME_USAGE_RULES.md — правила работы с системой
- OWNER_ACT_STYLE_PROFILE.md — полностью переписан из 3 реальных Drive актов
- Исправлены 2 ошибки предыдущей сессии (Susanino фото → UNKNOWN, Novichkovo source ref)

### Статус пакетов (local-check 2026-05-05)
- reportlab: NOT INSTALLED (ModuleNotFoundError)
- python-docx: NOT INSTALLED (ModuleNotFoundError)
- Рабочий путь: TEXT_REPORT → Telegram text

### Открытые вопросы
- Vision 3-й выезд Киевское (04.05.2026) — решение владельца
- reportlab / python-docx — установить?
- @tnz_msk 66 карт на review — одобрить?
- Live tests (11 тестов из ТЗ)

### Запрещённые файлы — не тронуты
- core/normative_engine.py — dirty (+283 lines), НЕ staged

---

# LATEST_HANDOFF — 05.05.2026 10:20 MSK

## СЕССИЯ 05.05.2026 — FOLDER DISCOVERY LIVE CLOSED

### Патчи
| Коммит | Файл | Что |
|---|---|---|
| f1d6763 | final_closure_engine.py | P6H4TW_FCE_TOPIC5_ROUTE_FIX_V1: bypass is_technadzor_intent для folder/context intent в topic_5 |
| f1d6763 | technadzor_engine.py | P6H4FD_FOLDER_DISCOVERY_V1: поиск папки по имени на Drive, set_active_folder |
| e1aa647 | task_worker.py | FCE hook: заменить unbound task_id/raw_input/input_type/reply_to на _task_field() при вызове |
| 8bf752e | task_worker.py | FCE hook send path: _fcv1_tid/_fcv1_reply через _task_field чтобы не падало после handled=True |
| 94e2252 | technadzor_engine.py | поиск внутри system subfolder TECHNADZOR — ОТМЕНЁН следующим |
| 0a5c766 | technadzor_engine.py | исключить системные папки из кандидатов результата |
| 48b1e55 | technadzor_engine.py | ФИНАЛЬНЫЙ: искать в root ТЕХНАДЗОР (1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD), fallback Drive-wide search, state=DONE |

### Контрольный кейс — PASSED ✅
```
raw_input: создана папка тест надзор. Ее надо принять сейчас для проверки работоспособности
task: 5276 DONE
result: Нашёл папку «тест надзор» и установил её как активную.
        https://drive.google.com/drive/folders/1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG
folder_id: 1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG ✅
```

### Архитектура folder discovery
- Trigger: topic_id=5 + folder/context intent (список из 13 фраз в FCE + P6H4FD)
- FCE (_handle_technadzor): bypass is_technadzor_intent → вызов process_technadzor напрямую
- P6H4FD wrapper: поиск в ТЕХНАДЗОР root (1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD) → фильтр системных → fuzzy match → set_active_folder
- Fallback: Drive-wide exact name search если root пуст
- Системные папки (TECHNADZOR, ТЕХНАДЗОР, topic_5, _system и др.) НИКОГДА не становятся active folder

### Drive структура (verified)
- topic_5 folder: 1yWIJdSrypH3BbIozCz-OAw1R6hmnMRHK
- TECHNADZOR (system, пустой): 1vKQM0Z2qBmiKtgeyx95JaNEQAp5mJLOm
- ТЕХНАДЗОР root (user folders здесь): 1s2y5l2mJFTb7P90XVokErXYVzmoH-VtD
- тест надзор (user project): 1Jfw1VKgOi2GgdlimK-HCBw7mx9a_FbKG

---

# LATEST_HANDOFF — 05.05.2026 09:06 MSK (предыдущая сессия)

## СЕРВЕР
IP: 89.22.225.136 | Base: /root/.areal-neva-core
Services: areal-task-worker ACTIVE | telegram-ingress ACTIVE | areal-memory-api ACTIVE

## ВСЕ ПАТЧИ СЕССИИ 30.04.2026 — ФИНАЛЬНЫЙ СТАТУС

| Патч | Файл | Статус |
|---|---|---|
| PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL | task_worker.py | VERIFIED ✅ |
| PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_WORKER_PICK_BEFORE_STALE_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FIX_PFIN3_MENU_SHADOW_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FILE_CHOICE_PRIORITY_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_FILE_PARENT_STRICT_OPEN_ONLY_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_ENGINE_BASE_RESTORE_SA_UPLOAD_V1 | core/engine_base.py | VERIFIED ✅ |
| PATCH_DRIVE_DIRECT_OAUTH_V1 | core/engine_base.py | VERIFIED ✅ |
| PATCH_DRIVE_UPLOAD_AND_TG_FALLBACK_V1 | task_worker.py | VERIFIED ✅ |
| PATCH_DOWNLOAD_OAUTH_V1 | task_worker.py | INSTALLED |
| PATCH_SOURCE_GUARD_V1 | task_worker.py | INSTALLED |
| PATCH_FILE_ERROR_RETRY_V1 | task_worker.py | INSTALLED |
| PATCH_DRIVE_BOTMSG_SAVE_V1 | task_worker.py | INSTALLED |
| PATCH_DRIVE_DOWNLOAD_FAIL_MSG_V1 | task_worker.py | INSTALLED |
| PATCH_CRASH_BOTMSG_V1 | task_worker.py | INSTALLED |
| PATCH_RETRY_TG_MSG_V1 | task_worker.py | INSTALLED |
| PATCH_RETRY_TOPIC_FOLDER_V1 | core/upload_retry_queue.py | VERIFIED ✅ |
| PATCH_HC_NO_UPLOAD | core/upload_retry_queue.py | INSTALLED |
| PATCH_DAEMON_OAUTH_OVERRIDE_V1 | systemd telegram-ingress | VERIFIED ✅ |
| PATCH_DAEMON_USE_OAUTH_V1 | telegram_daemon.py | INSTALLED |
| PATCH_VOICE_OAUTH_V1 | telegram_daemon.py | INSTALLED |
| PATCH_SCOPE_FULL_V1 | core/topic_drive_oauth.py + drive_folder_resolver.py + google_io.py | VERIFIED ✅ |
| PATCH_DUPLICATE_GUARD_V1 | task_worker.py | INSTALLED |
| PATCH_MULTI_FILE_INTAKE_V1 | task_worker.py | INSTALLED |
| PATCH_LINK_INTAKE_NEEDS_CONTEXT_V1 | task_worker.py | INSTALLED |
| §0.11 САМОПРОВЕРКА AI | docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md | VERIFIED ✅ |
| Stale tasks cleanup | data/core.db | DONE ✅ |

## VERIFIED LIVE TESTS (30.04.2026)

- drive_file NEW → NEEDS_CONTEXT → меню по topic_id ✅
- reply/voice choice → FILE_CHOICE_PARSED → IN_PROGRESS ✅
- estimate engine → локальный artifact ✅
- Drive upload через OAuth → UPLOAD_OK ✅
- Telegram fallback при упавшем Drive ✅
- upload_retry_queue → cron 10min → восстанавливает Drive ✅
- retry загружает в topic папку (не INGEST) ✅
- OAuth scope=drive → PATCH_SCOPE_FULL_V1 → invalid_scope исчез ✅
- daemon OAuth через override.conf ✅
- daemon использует upload_file_to_topic (не upload_to_drive) ✅
- voice upload через OAuth ✅
- engine_base.py восстановлен ✅
- FILE_PARENT_STRICT работает ✅
- topic_id=0 не цепляет чужие задачи ✅

## КЛЮЧЕВЫЕ РЕШЕНИЯ СЕССИИ (хронология)

1. **OAuth app в Production** — refresh_token не протухает
2. **engine_base.py восстановлен** из bak (был удалён)
3. **Direct OAuth** заменил Service Account (storageQuotaExceeded)
4. **Telegram fallback** если Drive упал
5. **upload_retry_queue** — cron 10min восстанавливает Drive из TG
6. **retry в topic папку** — не INGEST корень
7. **healthcheck через list API** — не upload (избегаем INGEST загрязнения)
8. **Source guard** — файлы не из telegram → CANCELLED
9. **File error retry** — reply на ошибку → перезапуск файла
10. **Расширенный retry** — поиск по bot_message_id + reply_to + telegram_message_id
11. **Crash bot_message_id save** — при крашe сохранять id для retry
12. **Daemon OAuth override** — добавлены OAuth переменные в systemd
13. **Daemon use OAuth** — заменил upload_to_drive на upload_file_to_topic
14. **Voice OAuth** — voice через upload_file_to_topic
15. **Scope full drive** — заменил drive.file на drive в 3 файлах (РЕШИЛ invalid_scope)

## АРХИТЕКТУРА (финальная)

### Drive Upload Chain
```
Telegram message → daemon → upload_file_to_topic (OAuth, scope=drive) → topic папка
                                          ↓ если упал
                          create_task drive_file → task_worker
                                          ↓
                              _handle_drive_file → analyze
                                          ↓
                          engine_base.upload_artifact_to_drive (OAuth)
                                          ↓ если упал
                          Telegram sendDocument fallback
                                          ↓ TELEGRAM_ARTIFACT_FALLBACK_SENT
                          cron upload_retry_queue (10min)
                                          ↓ Drive alive?
                          скачать из TG → загрузить в topic папку → DRIVE_RETRY_UPLOAD_OK
```

### Folder Structure
```
AI_ORCHESTRA/
├── chat_-1003725299009/
│   ├── topic_0/   (ЧАТ ЗАДАЧ)
│   ├── topic_2/   (СТРОЙКА)
│   ├── topic_5/   (ТЕХНАДЗОР)
│   ├── topic_210/ (ПРОЕКТИРОВАНИЕ)
│   └── ...
```

При создании нового топика папка создаётся автоматически через `_ensure_folder`.

### Retry Logic
1. Reply на сообщение бота с ошибкой → ищет parent task по:
   - bot_message_id == reply_to
   - reply_to_message_id == reply_to
   - raw_input.telegram_message_id == reply_to
2. Если parent FAILED/AWAITING_CONFIRMATION/CANCELLED + result содержит "ошибка/не удалась"
3. Переводит parent в NEW → worker обрабатывает заново

### Source Guard
- source=telegram → обработка
- source=google_drive → CANCELLED (системный мусор)
- source=other → CANCELLED

## CRON JOBS

```
*/10 * * * * core/upload_retry_queue.py — retry Drive upload из TG
*/30 * * * * tools/context_aggregator.py — обновление контекста
```

## НЕ ЗАКРЫТО — P1

- Голосовой confirm при AWAITING_CONFIRMATION (telegram_daemon.py:601)
- Live-тест полного цикла после PATCH_SCOPE_FULL_V1
- Live-тест PATCH_FILE_ERROR_RETRY_V1 с реальным reply
- Live-тест PATCH_CRASH_BOTMSG_V1
- DUPLICATE_GUARD live-тест
- MULTI_FILE_INTAKE live-тест
- LINK_INTAKE live-тест

## НЕ ЗАКРЫТО — P2

- Смета PDF → Excel → Drive end-to-end
- КЖ PDF pipeline
- project_engine end-to-end
- Gemini vision
- Excel формулы =C2*D2 / =SUM
- Нормы СП/ГОСТ
- Multi-file один артефакт
- Memory/pin перед меню
- Google Sheets интеграция
- Шаблоны end-to-end
- MODEL_ROUTER, FALLBACK_CHAIN
- STT "Олег" — Whisper галлюцинирует имя

## КРИТИЧЕСКИЕ УРОКИ СЕССИИ

1. **Service Account НЕ работает с My Drive** — нужен только OAuth
2. **Refresh token зависит от scope при выдаче** — если код просит scope шире/уже чем токен, падает invalid_scope
3. **systemd Environment не наследуется автоматически** — нужен override.conf для каждого сервиса
4. **bot_message_id критичен для retry** — без него reply не находит parent
5. **AI router цепляет stale задачи** — старые AWAITING_CONFIRMATION загрязняют контекст
6. **drive_ingest подхватывает healthcheck файлы** — поэтому healthcheck через list API


## ОБНОВЛЕНИЕ 30.04.2026 10:00

### Новые баги выявлены в сессии (live наблюдение)

**BUG_CONFIRM_UNFINISHED** — AWAITING_CONFIRMATION без реального результата
- task_worker.py строки 2068-2075
- ТЗ: PATCH_CONFIRM_ONLY_ON_DONE_V1 в NOT_CLOSED

**BUG_TEMPLATE_NO_STRUCT** — шаблон = OCR текст вместо структурной модели
- core/artifact_pipeline.py — intent игнорируется
- core/template_manager.py — не используется
- ТЗ: PATCH_TEMPLATE_INTENT_V1 в NOT_CLOSED

### Факт из live БД topic=210
АР/КД/КЖ PDF файлы обрабатывались как "document" → OCR текст → "Сводка по документу"
Пользователь ожидал: структурную модель проекта с составом листов, марками, параметрами

## ОБНОВЛЕНИЕ 30.04.2026 10:30 — FULLFIX_01_CANON_CLOSE_CORE VERIFIED

### Патчи VERIFIED live-тестом:

| Патч | Файл | Статус |
|---|---|---|
| PATCH_TEMPLATE_MODEL_EXTRACTOR_V1 | core/project_engine.py | VERIFIED ✅ |
| PATCH_PROJECT_TEMPLATE_STORAGE_V1 | core/template_manager.py | VERIFIED ✅ |
| PATCH_TEMPLATE_INTENT_BRANCH_V1 | core/artifact_pipeline.py | VERIFIED ✅ |
| PATCH_CONFIRM_ONLY_ON_DONE_V1 | task_worker.py строки 2073+ | VERIFIED ✅ |
| PATCH_CONFIRM_GUARD_C_V1 | task_worker.py строка 1711 | VERIFIED ✅ |

### Live-тест 30.04 10:09

```
Файл: ПРОЕКТ КД кровля 5.pdf → topic_id=210
Task: 2a249e66-8399-4994-8211-dcad82496f18
State: AWAITING_CONFIRMATION
Result: PROJECT_TEMPLATE_MODEL создан
Раздел: АР
Структура: план, расчет, Фасады, Разрез, План
Размеры мм: 940, 730, 2025, 16940, 10730, 360, 2001...
```

### Что закрыто FULLFIX_01:
- PDF проекта → PROJECT_TEMPLATE_MODEL (не OCR summary) ✅
- AWAITING_CONFIRMATION только при валидном результате ✅
- "Доволен результатом?" не показывается при ошибке/пустом result ✅
- template_manager сохраняет модель в data/project_templates/ ✅

### Что осталось не идеальным (следующий проход):
- project_type определяется неточно (КД файл определён как АР)
- Состав листов (0) — марки листов не всегда извлекаются
- Голосовой confirm при AWAITING_CONFIRMATION — не закрыт

---
# HANDOFF 30.04.2026 — FULLFIX_02 SESSION

## STATE
- areal-task-worker: active | telegram-ingress: active | areal-memory-api: active
- DB ORDER: использовать ORDER BY rowid DESC

## VERIFIED THIS SESSION
- FULLFIX_02_BC: project_type КД из filename ✅, sheet_register fallback ✅
- FULLFIX_01: PROJECT_TEMPLATE_MODEL создан ✅

## INSTALLED, AWAITING LIVE TEST
- FULLFIX_02_DA: neg bind + false confirm guard + voice negative
- FULLFIX_02_E: negative confirm all paths (NOT YET RUN)

## CRITICAL NEXT ACTIONS
1. Запустить FULLFIX_02_E
2. Live: "переделай" → "Хорошо, доработаю"
3. Live: голос "да" при AWAITING_CONFIRMATION → DONE
4. Live: estimate PDF → xlsx → Drive
# HANDOFF 01.05.2026 — ПОЛНАЯ СЕССИЯ ВОССТАНОВЛЕНИЯ

## СЕРВЕР
IP: 89.22.225.136 | Base: /root/.areal-neva-core
Services: areal-task-worker ACTIVE restarts=0 | telegram-ingress ACTIVE restarts=0 | areal-memory-api ACTIVE

## ЧТО БЫЛО СЛОМАНО И ПОЧИНЕНО

| Патч | Файл | Проблема | Статус |
|---|---|---|---|
| AI_LOGIC_FIX_V1 | task_worker.py | if/else перевёрнут — AI не вызывался | VERIFIED ✅ |
| AI_RESULT_INIT_V1 | task_worker.py | UnboundLocalError ai_result | VERIFIED ✅ |
| SAVE_MEM_ALL_DONE_PATHS_V2 | task_worker.py | _save_memory не вызывалась | VERIFIED ✅ |
| DAEMON_OAUTH_FIX_V1 | telegram_daemon.py | upload_to_drive→upload_file_to_topic | VERIFIED ✅ |
| INPUT_TYPE_DRIVE_FIX_V1 | task_worker.py | input_type not defined в drive_file | VERIFIED ✅ |
| SCOPE_FULL_V2 | topic_drive_oauth.py + drive_folder_resolver.py | drive.file→drive | VERIFIED ✅ |
| PORT_FIX_V1 | archive_engine.py | порт 8765→8091 | VERIFIED ✅ |
| MEMORY_API_SERVER_V1 | core/memory_api_server.py | файл отсутствовал | VERIFIED ✅ |
| IMPORT_FIX_V1 | core/topic_autodiscovery.py | from reply_sender→from core.reply_sender | VERIFIED ✅ |
| ZOMBIE_UNITS_REMOVED | systemd | 4 unit-файла удалены навсегда | VERIFIED ✅ |
| TOPIC_META_LOADER_V1 | task_worker.py | топики знают себя | VERIFIED ✅ |
| HOTFIX_FILE_NAME_EARLY_V1 | task_worker.py | file_name до TASK_TYPE_DETECT | VERIFIED ✅ |

## СОСТОЯНИЕ БД
- FAILED: 2811 (исторические, не мешают)
- CANCELLED: 543
- ARCHIVED: 381
- DONE: 348
- AWAITING_CONFIRMATION: 19

## ПАМЯТЬ
- memory.db: 969 архивных записей по топикам
- save_memory_ok работает с 16:00 01.05.2026
- archive_distributor: ok=True

## ТОПИКИ (все 11 настроены)
topic_0=ЛИДЫ АМО | topic_2=СТРОЙКА | topic_5=ТЕХНАДЗОР | topic_11=ВИДЕОКОНТЕНТ
topic_210=ПРОЕКТИРОВАНИЕ | topic_500=ВЕБ ПОИСК | topic_794=НЕЙРОНКИ СОФТ ВПН ВПС
topic_961=АВТО ЗАПЧАСТИ | topic_3008=КОДЫ МОЗГОВ | topic_4569=ЛИДЫ РЕКЛАМА | topic_6104=РАБОТА ПОИСК

## LIVE TESTS PASSED
- СТРОЙКА: вспомнил сметы за 24ч с Drive ссылками ✅
- ТЕХНАДЗОР: вспомнил архивные функции чата ✅
- КОДЫ МОЗГОВ: ответил по контексту ✅
- Drive: ALIVE, retry queue чист ✅

## НЕ ЗАКРЫТО
- Voice confirm при AWAITING_CONFIRMATION
- Estimate PDF→Excel→Drive live-тест
- Technadzor фото→акт live-тест
- detect_intent() 1 arg warning

---
## ПРАВИЛО ПЕРЕД ПАТЧЕМ (добавлено 02.05.2026)

**ОБЯЗАТЕЛЬНО перед любым патчем затрагивающим result/msg/ответ пользователю:**
1. curl GitHub raw текущего файла
2. Найти все места формирования result/msg
3. Сравнить с каноном — что должно показываться пользователю
4. Только потом писать якорь и replace
5. Не писать патч из памяти

Причина: CLEAN_RESULT_TEXT_V1 — обнаружили что Engine:/MANIFEST:/системные ключи
попадали в ответ пользователю из sample_template_engine.py строки 533-545,
потому что не прочитали текущий код перед патчем.

## СЕССИЯ 02.05.2026

| Patch | Commit | Status |
|---|---:|---|
| ESTIMATE_TOP_TEMPLATES_LOGISTICS_CANON_V4 | e370c53 | VERIFIED ✅ |
| ESTIMATE_SCENARIO_CLASSIFICATION_FIX_V1 | 04378dc | VERIFIED ✅ |
| SAMPLE_ACCEPT_DIALOG_CONTEXT_FIX_V1 | 3d148d9 | VERIFIED ✅ |
| DRIVE_AI_ORCHESTRA_ROOT_CLEANUP_V1 | 4f0b15b | VERIFIED ✅ |
| DRIVE_AI_ORCHESTRA_ROOT_FOLDER_FINAL_CLEAN_V1 | 226769c | VERIFIED ✅ |
| AREAL_REFERENCE_FULL_MONOLITH_V1 | current | VERIFIED ✅ |

## FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3 — INSTALLED_NOT_VERIFIED
- additive patch only
- core/stroyka_estimate_canon.py added/replaced
- task_worker.py hook only
- topic_id=2 only
- VOR_кирпичная_кладка_ИСПРАВЛЕНО.xlsx moved to deprecated estimate template archive, not destroyed
- dynamic Drive templates folder enabled: parentId 19Z3acDgPub4nV55mad5mb8ju63FsqoG9
- М-80/М-110 sheet selection enabled: Каркас под ключ vs Газобетон/Газобетон_под ключ
- prices from selected template sheet are shown next to online prices
- user price choice supported: median/average, minimum, maximum, specific source, manual price
- markup/discount/reserve percent supported from confirmation text
- final XLSX/PDF forbidden before price and logistics confirmation
- XLSX is created from selected XLSX template with added AREAL_CALC sheet and formulas
- Python calculates, LLM does not calculate final numbers
- VERIFIED requires live Telegram test

## FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3_MEMORY_REVIVE_FIX — INSTALLED_NOT_VERIFIED
- Старые задачи topic_2 считаются памятью, не мусором
- Старый raw_input / ТЗ / голосовые уточнения используются для продолжения задачи
- Старый ошибочный result не отдаётся пользователю как готовая смета
- Команды "доделай", "где смета", "смету в Excel", "ну что", "да сделай" поднимают последнюю валидную сметную задачу за 7 дней
- Продолжение идёт через STROYKA V3: шаблон, лист, цены из шаблона, интернет-цены, выбор цены, подтверждение, XLSX/PDF

## P6F_REVISION_WORDS_EXTEND_AND_TNZ_KWARGS_FIX_V2 — INSTALLED 2026-05-04 20:49 MSK

### task_worker.py
- `_P6E67_REVISION_WORDS` extended 24→36 words (added: «нормальн», «снова», «сделай», «ещё/еще раз», «заново», «повтори», «по новой», «сначала», «новой», «опять», «сделать», «переделать»)
- Reason: live-test rowid 5257 «снова сделай нормально» проскочил мимо revision-detection до фикса

### core/technadzor_engine.py
- `process_technadzor` wrapper signature: добавлен `**kwargs` + try/except TypeError fallback
- Reason: моя P6F-регрессия — `task_worker.py:6826` зовёт `process_technadzor(text=..., conn=conn, task=task)` с лишними kwargs, прежний wrapper падал TypeError

### Verify
- python3 -m py_compile: OK
- worker restart: 2026-05-04 20:49:21 MSK
- markers loaded in log: P6F_*_INSTALLED + P6G_*_INSTALLED ✅
- smoke test: «нормальную смету ещё раз, снова сделай» → is_revision=True ✅

## P6G_CLEAN_OLD_TOPIC500_CONTAMINATION — VERIFIED 2026-05-04

| Action | Target | Status |
|---|---|---|
| SQL UPDATE result | tasks.rowid=4883 (topic_id=500, task_id=ceafeca1-fa42-4e66-8499-40955c393d0c) | DONE ✅ |
| INSERT task_history | id=59608, action=P6G_CLEAN_OLD_TOPIC500_CONTAMINATION | DONE ✅ |
| Task preserved | NOT deleted, state=DONE | OK |
| Reason | Pre-P6E4 contamination: «статусё» → «зелёная металлочерепица Монтеррей» в result. Replaced with служебный очищенный текст по канону. |
| Backup | data/db_backups/P6G_CLEAN_OLD_TOPIC500_CONTAMINATION_20260504_210544_core.sqlite (sqlite3 .backup) |
| Push | this commit |

## P6H_TOPIC5_TECHNADZOR_TEMPLATE_PHOTO_CLIENT_SAFE_VOICE_LIVE_CLOSE_20260504 — INSTALLED_NOT_LIVE_TESTED

### Что сделано
Системный технадзорный модуль topic_5 — полный закрывающий контур.

| Файл | Назначение |
|---|---|
| `core/technadzor_drive_index.py` (NEW) | Auto-index Drive topic_5 → классификация PRIMARY_PDF_STYLE / SECONDARY_DOCX_REFERENCE / CLIENT_PHOTO_SOURCE / CLIENT_FINAL_PDF / SYSTEM_TEMPLATE. Folder rules: client-facing vs system. Persisted to `data/templates/technadzor/ACTIVE__chat_<id>__topic_5.json`. Strict refusal to upload non-PDF in client folders / non-system into _drafts. |
| `core/technadzor_object_registry.py` (NEW) | Object cards + inspection_chain. CRUD: derive_object_id_from_context / load_object / save_object / record_inspection / carry_forward_open_items / detect_visit_mode / detect_voice_vision_conflict. Storage: server JSON + memory.db key + timeline.jsonl. |
| `core/normative_engine.py` (APPEND) | NORMATIVE_INDEX расширен 8→18 (СП 28, ГОСТ 23118, СП 48, СП 13-102, ГОСТ 31937, СП 70 опорные узлы, СП 16 связи, СП 22 основания, СП 20 перекрытия, ГОСТ Р ИСО 17637 сварка). |
| `core/technadzor_engine.py` (APPEND P6H_PART_1 + PART_2 + PART_3) | Wrapper around `process_technadzor` для topic_5: voice transcript parser → object_id derivation → Drive index → Vision (OpenRouter Gemini 2.5) → section classifier (12 секций) → clarification gate (без «что строим?») → photo-numbered Telegram output («Фото №N — <file>») → DOCX (python-docx, hyperlinks, в `_drafts` служебно) → PDF A4 (reportlab, кириллица DejaVu, кликабельные ссылки) → upload Drive (DOCX → service `_drafts`, PDF → topic root или явно named client folder) → memory summary `topic_5_technadzor_photo_report_summary` → registry inspection record. Visit modes: initial/repeat/extension/description_only. Carry-forward open_items со статусами УСТРАНЕНО/ЧАСТИЧНО/НЕ УСТРАНЕНО/ТРЕБУЕТ УТОЧНЕНИЯ. |
| `task_worker.py` (APPEND) | P6H_TOPIC5_TASK_WORKER_RUNTIME_VERIFY block — re-emits P6H markers in file log (logger name «task_worker» — fix логгера). |

### Маркеры в worker log (verified 21:56:31)
- P6H_TOPIC5_DRIVE_INDEX_V1_VERIFIED_VIA_TASK_WORKER_RUNTIME ✅
- P6H_TOPIC5_USE_EXISTING_TEMPLATES_PHOTO_TO_TECH_REPORT_20260504_V1_VERIFIED ✅
- P6H_TOPIC5_PHOTO_NUMBER_DEFECT_NORM_CLARIFICATION_LOGIC_20260504_VERIFIED ✅
- P6H_TOPIC5_VOICE_LIVE_DIALOG_CLARIFICATION_GATE_20260504_VERIFIED ✅
- P6H_TOPIC5_OBJECT_REGISTRY_INSPECTION_CHAIN_20260504_VERIFIED ✅
- P6H_TOPIC5_PROCESS_TECHNADZOR_WRAPPED=True ✅

### Smoke tests (passed)
- py_compile все 5 файлов
- Drive scan topic_5: 4 PRIMARY_PDF_STYLE + 2 SYSTEM_TEMPLATE + 2 CLIENT_PHOTO_SOURCE
- DOCX 38 KB, PDF 53 KB с `/Annot` (кликабельные) + DejaVu (кириллица)
- Voice parser извлекает folder_hint/object_hint/visit_date_hint/client_facing/output_kind
- Clarification gate emits concrete questions, never «что строим?»
- Object registry roundtrip: derive_object_id, save card, carry_forward_open_items, list_summaries
- Worker active, NRestarts=0

### НЕ ВЕРИФИЦИРОВАНО live в Telegram (требует следующего этапа)
- Реальная пачка фото в topic_5 → текстовый разбор «Фото №N»
- Голосовое ТЗ владельца → корректное object linking
- «сделай акт» → DOCX в `_drafts` + PDF A4 в topic root + ссылка в Telegram
- Повторный осмотр того же объекта → carry-forward open_items со статусами

### Backups
- `data/backups/P6H_TOPIC5_TECHNADZOR_TEMPLATE_PHOTO_CLIENT_SAFE_CLOSE_20260504_213228/` (gitignored)
  - technadzor_engine.py.bak / normative_engine.py.bak / task_worker.py.bak
  - core.sqlite + memory.sqlite (sqlite3 .backup)

### Backups для P6G-1 (ранее сегодня) и REVISION_WORDS+TNZ kwargs fix
- См. предыдущие коммиты `c4f3b40`, `e3d992c`

### Forbidden files — НЕ ТРОГАЛИСЬ
- telegram_daemon.py / ai_router.py / google_io.py / reply_sender.py / .env / credentials.json

---

## СЕССИЯ 04.05.2026 — ТЕХНАДЗОРНЫЙ КАНОН ФИНАЛИЗИРОВАН

### Принятые решения по архитектуре topic_5

#### Главная модель
```
Файл сам по себе ≠ задача

TechnadzorTask =
  OwnerInstruction (голос или текст владельца)
  + InputFiles     (фото/PDF/DOCX из Drive или Telegram)
  + ObjectContext  (ObjectCard — история объекта)
  + PreviousActs   (предыдущие акты если есть)
```

#### Два равноправных пути передачи материалов
- **Путь A — Drive**: владелец создаёт папку, загружает файлы, поясняет в Telegram
- **Путь B — Telegram**: файлы + голос/текст → оркестр агрегирует, не делает акт на каждое фото

#### Новые сущности в канон (разделы 29–33)
| Сущность | Назначение |
|---|---|
| `ActiveTechnadzorFolder` | Сессионный контекст текущей рабочей папки (≠ ObjectCard) |
| Команды управления | Словарь команд владельца: открыть, сменить, закрыть, сделать акт |
| `COLLECTING_VISIT_MATERIALS` | Режим накопления до команды "сделай разбор/акт" |
| `VisitMaterial` | Атомарный материал выезда: файл + owner_comment + group_label |
| `VisitPackage` | Агрегат всех материалов → собирается по команде → один результат |

#### 61 фото = один выезд = один акт
- Фото обрабатываются батчами по 10–11
- Все DefectCards агрегируются
- Группируются по секциям (2.1 Опорные, 2.2 Сварка, ...)
- Один финальный ответ в Telegram / один PDF

#### Язык
- Клиентские файлы, акты, Telegram-ответы — **только русский**
- English — только внутри кода (функции, классы, enum, маркеры)

### Что НЕ добавлено в канон (выдумано — отклонено)
- `outputs/technadzor` — не существует на сервере
- `runtime/technadzor` — не существует на сервере
- Google Docs как текущий готовый формат — не реализован

### P6H_PART_4 — INSTALLED (05.05.2026)

| Файл | Патч | Коммит |
|---|---|---|
| `core/technadzor_engine.py` | P6H_PART_4_VISIT_BUFFER_V1: `visit_buffer_add`, `visit_buffer_flush`, `visit_buffer_count`, `set_active_folder`, `get_active_folder`, `process_drive_folder_batch` | `d90b5ad` |
| `task_worker.py` | P6H_PART_4_TASK_WORKER_HOOK_V1: topic_5 mode — фото→буфер+ack, Drive folder URL→set_active_folder, «сделай разбор»→flush+inject→technadzor, [VOICE]→annotate last material | `ff753aa` |
| `core/stt_engine.py` | P6H_STT_HALLUCINATION_GUARD_V1: Groq Whisper фантомы (≤6 символов, "субтитры", "Олег" и т.п.) → `STT_HALLUCINATION_REJECTED` | `ff753aa` |

**Буфер:** `data/technadzor/buf_{chat_id}_{topic_id}.json` — persistent JSON, изолирован по chat_id+topic_id.
**Активная папка:** `data/technadzor/active_folder_{chat_id}_{topic_id}.json`.

**Статус:** INSTALLED_NOT_LIVE_TESTED — py_compile OK, сервисы не перезапускались.
**Vision:** EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False (по умолчанию). Без явного разрешения владельца — не запускать.
**Не реализовано в этой сессии:** `_batch_vision_aggregate` (Vision заблокирован, нет смысла).

### Standalone скрипт gen_act_3rd_visit.py — НАПИСАН, Vision не работает

Скрипт: `tools/gen_act_3rd_visit.py`
Назначение: скачать 61 фото из Drive `1sS1A6iHQHUwjqZGF43wdyRjoLwwAHPse` → Vision → PDF акт 3-го выезда

**Проблема Vision (04.05.2026):**
- OpenRouter `google/gemini-2.5-flash` → 403 "Blocked by Google"
- Причина: Google блокирует конкретный аккаунт/ключ через OpenRouter
- PDF с пустыми разделами был сгенерирован и загружен на Drive (структура правильная)
- **СТАТУС:** Vision заблокирован по канону §1.5 — OpenAI и Anthropic запрещены как провайдеры. OpenRouter+Google блокирует аккаунт (403). Смена модели без явного решения владельца запрещена.
- **EXTERNAL_PHOTO_ANALYSIS_ALLOWED = False** — фото наружу не отправлять без явного разрешения владельца (TECHNADZOR_DOMAIN_LOGIC_CANON_V2 §33)

**Файлы выезда уже скачаны:**
- `data/memory_files/technadzor_index_cache/IMG_5320.JPG` ... `IMG_5381.JPG` (61 фото)
- Можно сразу перезапустить скрипт после смены модели

**Объект:** ангар Киевское шоссе, акт № 04-05/26, третий выезд 04.05.2026
**Предыдущий акт:** № 12-03/26 от 12.03.2026
**Ссылка на папку фото:** https://drive.google.com/drive/folders/1sS1A6iHQHUwjqZGF43wdyRjoLwwAHPse

### Коммиты этой сессии
- `d838855` — TECHNADZOR_DOMAIN_LOGIC_CANON.md (разделы 1–24)
- `e36b320` — разделы 25–28 (пути передачи, модель задачи, буфер, язык)
- `2be1bb3` — разделы 29–33 (ActiveTechnadzorFolder, VisitMaterial, VisitPackage, COLLECTING, команды)
- `9e9c330` — LATEST_HANDOFF обновлён с решениями сессии
- `4bc1f09` — fix(stt): убрать OpenAI fallback → только Groq whisper-large-v3-turbo
- `a5cae41` — P6H4TW batch trigger logger fix + process_drive_folder_batch trigger
- `38270c6` — P6H4TW_BATCH_TRIGGER_V1: fix dead hook — wrapper перенесён в technadzor_engine.py

---

## СЕССИЯ 05.05.2026 — P6H4TW_BATCH_TRIGGER_V1

### Проблема (диагностировано 05.05.2026)
`P6H_PART_4` hook в `task_worker.py` (строка 8394) стоит **после** `asyncio.run(main())` (строка 8275).
При нормальном запуске воркер блокируется в `asyncio.run()`. Код P6H4TW выполняется только после остановки воркера → wrapper на `_handle_new` никогда не устанавливался.
`P6H_PART_4_TASK_WORKER_HOOK_V1_INSTALLED` появлялось только в LOCKED-процессе (немедленно выходит).

### Исправление
`P6H4TW_BATCH_TRIGGER_V1` — новая обёртка appended в `core/technadzor_engine.py` (конец файла).
`process_technadzor` импортируется и оборачивается до `asyncio.run()`. Все topic_5 задачи проходят через неё.

| Файл | Патч | Коммит |
|---|---|---|
| `core/technadzor_engine.py` | P6H4TW_BATCH_TRIGGER_V1: wrap process_technadzor | `38270c6` |

### Подтверждено
```
python3 -c "from core import technadzor_engine as te; print(getattr(te.process_technadzor, '_p6h4tw_v1_wrapped', False))"
→ True
```
Сервисы: active ✅

### P6H_TOPIC5_PROCESS_TECHNADZOR_WRAPPED=False в логе
Это НОРМАЛЬНО. P6H4TW_V1 оборачивает P6H. На верхнем уровне `_p6h_wrapped` не виден.
Реальное состояние: `_p6h4tw_v1_wrapped=True`.

### CODE CLOSED (topic_5 контур)
- topic_5 photo/file buffer ✅
- active folder set/get ✅
- Drive folder batch trigger ✅ (P6H4TW_BATCH_TRIGGER_V1)
- flush to process_technadzor ✅
- external Vision guarded optional (EXTERNAL_PHOTO_ANALYSIS_ALLOWED=False) ✅
- STT hallucination guard ✅
- без Vision: owner comments + filenames + previous acts + clarification

### LIVE SMOKE PENDING
- Telegram: реальное фото в topic_5 → буфер → "сделай разбор"
- Drive folder URL → "загрузи папку" → "сделай акт"
- topic_2 реальный запрос
- topic_500 реальный поиск
