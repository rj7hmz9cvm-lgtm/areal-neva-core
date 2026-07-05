# LATEST HANDOFF — 2026-07-05 topic_2 / STROYKA

**HEAD на момент проверки**: `348fcef`
**Основной SSOT**: `docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md`
**Канон topic_2**: `docs/CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md`
**Рабочий отчёт сессии**: `docs/HANDOFFS/SESSION_20260705_TOPIC2_CANON_LIVE.md`

---

## Статус topic_2

| Топик | Состояние | Примечание |
|-------|-----------|------------|
| topic_2 STROYKA | PARTIAL LIVE VERIFIED / NOT FULL CANON CLOSED | PDF/project estimate task `33bd7b5a-ade8-47a8-b07e-4db4d3cacca8` closed after explicit user confirm; remaining canon gaps below |
| topic_5 TEKHNADZOR | не трогать в рамках topic_2 | соседний топик |
| topic_210 PROJECT | не трогать в рамках topic_2 | соседний топик |
| topic_500 SEARCH | не трогать без отдельной задачи | интернет-поиск только через Sonar по канону |

---

## Что было сделано 2026-07-04 / 2026-07-05 по topic_2

- Восстановлен live text-TZ route для полного нового задания topic_2 без подмешивания старой задачи.
- Исправлен симптом старого загрязнения, когда fresh complete TZ мог уйти в старый followup/template route.
- Для тестовой задачи `0115efea-ed49-4263-a6f0-a981a760261c` подтверждено:
  - плита `450 мм` распознана из текущего задания;
  - кирпичные наружные стены использованы вместо старого утепления/каркасных строк;
  - добавлены инженерные коммуникации, проживание бригады/стройлагерь, логистика, накладные расходы;
  - `Утепление стен 150 мм` отсутствует в финальном XLSX;
  - интернет-цены применялись через `perplexity/sonar`, без DeepSeek search fallback;
  - созданы XLSX/PDF и Drive links;
  - финал удерживается по канону до явного подтверждения пользователя.
- Создан отчёт `docs/HANDOFFS/SESSION_20260705_TOPIC2_CANON_LIVE.md`.
- Live PDF/project task `33bd7b5a-ade8-47a8-b07e-4db4d3cacca8` verified:
  - XLSX/PDF Drive links created;
  - XLSX `AREAL_CALC` uses canonical 15 columns and grouped `Работа / Материалы / Всего` layout;
  - reply `да ок` to bot message `11544` now closes parent task to `DONE`;
  - child confirmation task `103a8493-2347-4f60-9dee-81ee5892ef46` closes to `DONE`;
  - `TOPIC2_EXPLICIT_CONFIRM:from_user_confirm_reply` is written before DONE;
  - `topic_2_user_input`, `topic_2_task_summary`, `topic_2_assistant_output` are updated after DONE.

---

## Факты, найденные после live repair

Диагностика выполнялась по правилу `logs -> db -> pin -> memory -> context -> patch`, без правок runtime.

1. `НДС 20%` всё ещё hardcoded в runtime topic_2:
   - `core/sample_template_engine.py`
   - `core/stroyka_estimate_canon.py`
   - встречаются `НДС 20%`, `*0.2`, `*1.2`.

2. По рабочему требованию topic_2 дальше должен считать НДС так:
   - по умолчанию смета без НДС;
   - если пользователь не указал режим, нужно уточнить: без НДС или с НДС 22%;
   - если выбран НДС, ставка должна быть 22%, а не 20%.

3. Long memory после DONE:
   - для live task `33bd7b5a-ade8-47a8-b07e-4db4d3cacca8` проверено обновление `topic_2_user_input`, `topic_2_task_summary`, `topic_2_assistant_output`;
   - generic topic_2 memory keys заменены со старых майских значений на свежий DONE-result;
   - правило остаётся: память писать только после `DONE`.

4. Active pin содержит старые майские записи:
   - `ebf586ce-3a29-4a22-837b-7c1d55506986` от `2026-05-04`;
   - `9d7e08f8-2d28-4684-b5cd-8dc72ea49317` от `2026-05-01`.
   Нужно проверить, что pin retrieval не загрязняет новые расчёты topic_2.

5. Для task `0115efea...` result содержит `Объект: барнхаус`, хотя raw TZ пользователя был `дом`. Это признак шаблонного текста, который нужно убрать из topic_2 final formatting.

6. Фото/PDF/OCR контур topic_2 остаётся незакрытым:
   - `P6E2 photo intercept before canonical`;
   - `pdf_spec_extractor.py exists but not connected to canonical flow`;
   - `ocr_table_engine.py exists but not connected to topic_2 flow`;
   - multifile project context для topic_2 не закрыт.

---

## Next work / open blockers

Работать только по существующим канонам, без новых направлений и без новых канонов.

1. Patch VAT policy для topic_2:
   - убрать hardcoded `20% / 0.2 / 1.2` из topic_2 runtime paths;
   - default output = без НДС;
   - при неясности спросить пользователя `без НДС или с НДС 22%`;
   - если выбран НДС, считать 22%.

2. Patch topic_2 memory write after DONE:
   - проверить `_save_memory()` path для canonical topic_2 final;
   - обеспечить запись `topic_2_user_input`, `topic_2_task_summary`, `topic_2_assistant_output` после DONE;
   - не писать память до DONE.

3. Проверить pin/reply isolation:
   - reply должен привязываться к parent task по `bot_message_id/reply_to_message_id` и `topic_id=2`;
   - старые active pin не должны подмешивать майские задачи в свежую смету;
   - любые изменения `telegram_daemon.py` только после отдельного явного `да` пользователя.

4. Проверить file/photo/project intake topic_2:
   - фото, PDF, XLSX, голос, reply и multifile должны идти в canonical topic_2 estimate flow;
   - если данных не хватает, задаётся точный уточняющий вопрос;
   - запрещено выдумывать параметры из старых задач.

5. Live tests после patch:
   - text full TZ;
   - reply continuation;
   - voice continuation;
   - photo with/without caption;
   - PDF/project/spec;
   - memory query по topic_2;
   - pin isolation.

---

## Что не трогать

- Не создавать ветки.
- Не push без отдельного разрешения.
- Не менять systemd unit files.
- Не менять рабочий запуск оркестра.
- Не трогать `.env` и секреты.
- Не редактировать `core/ai_router.py`, `core/reply_sender.py`, `core/google_io.py` без отдельного разрешения.
- Не трогать topic_5, topic_210, topic_500 и другие соседние топики в рамках topic_2 fix.

---

## Проверки перед продолжением

```bash
python3 -m py_compile core/sample_template_engine.py core/stroyka_estimate_canon.py core/topic2_input_gate.py core/topic2_estimate_final_close_v2.py task_worker.py
git diff -- docs/HANDOFFS/LATEST_HANDOFF.md docs/HANDOFFS/SESSION_20260705_TOPIC2_CANON_LIVE.md
sqlite3 data/core.db "SELECT id,state,topic_id,input_type,substr(raw_input,1,120),updated_at FROM tasks WHERE topic_id=2 ORDER BY updated_at DESC LIMIT 8;"
sqlite3 data/memory.db "SELECT key,timestamp FROM memory WHERE chat_id='-1003725299009' AND key GLOB 'topic_2_*' ORDER BY timestamp DESC LIMIT 12;"
```

---

## Progress 2026-07-05 — VAT policy patch started

- Backup created: core/sample_template_engine.py.bak_20260705_vat22 and core/stroyka_estimate_canon.py.bak_20260705_vat22.
- Removed forbidden `НДС 20%` from checked topic_2 runtime files.
- Replaced VAT rate with 22% in topic_2 XLSX/PDF/summary VAT formulas.
- Active P3 XLSX route now writes `НДС 22% (не включён)` with VAT amount 0 by default and total payable without VAT.
- Active P3 Telegram summary now says VAT is not included and asks user to answer `с НДС` if a VAT 22% calculation is needed.
- Verified: python3 -m py_compile core/sample_template_engine.py core/stroyka_estimate_canon.py core/topic2_input_gate.py core/topic2_estimate_final_close_v2.py task_worker.py -> PY_COMPILE_OK.
- Not done yet: live Telegram regression test for без НДС / с НДС; broader photo/multifile flow. Memory after DONE and reply confirm closure verified for task `33bd7b5a...`.

---

## Progress 2026-07-05 — live PDF project flow patch

- Backup created: task_worker.py.bak_20260705_pdf_voice_bind.
- Backup created: core/stroyka_estimate_canon.py.bak_20260705_no_waiting_project_revive.
- Backup created: core/topic2_estimate_final_close_v2.py.bak_20260705_drive_markers.
- Added PATCH_TOPIC2_WAITING_PROJECT_FILE_BIND_V1 in task_worker.py before final asyncio.run(main()).
- Voice/text phrase like `сейчас скину проект/PDF/файл` now moves topic_2 task to WAITING_CLARIFICATION with TOPIC2_WAITING_PROJECT_FILE instead of starting estimate.
- PDF drive_file without caption now binds to recent waiting project parent and enters topic_2 file estimate flow instead of DRIVE_FILE_NO_INTENT_OFFER menu.
- Added PATCH_TOPIC2_NO_WAITING_PROJECT_MEMORY_REVIVE_V1 in core/stroyka_estimate_canon.py to stop old estimate raw_input revive for waiting-project phrases.
- Added PATCH_TOPIC2_DRIVE_MARKERS_REQUIRE_LINKS_V1 in core/topic2_estimate_final_close_v2.py: Drive OK markers require real drive/docs links; otherwise MISSING markers are written.
- Verified: python3 -m py_compile task_worker.py core/stroyka_estimate_canon.py core/topic2_estimate_final_close_v2.py core/sample_template_engine.py core/topic2_input_gate.py -> OK.
- Not restarted: systemd/worker launch intentionally not touched. Patch takes effect after normal worker reload/restart.
- Next live test: voice says project will be sent -> bot waits; PDF upload binds to same task; no old raw_input revive marker; final result must contain real XLSX/PDF Drive links.


---

## Progress 2026-07-05 — topic_2 confirm close + memory

- Backup created: `core/stroyka_estimate_canon.py.bak_topic2_confirm_close_20260705`.
- Backup created: `data/core.db.bak_topic2_confirm_close_20260705`.
- Backup created: `data/memory.db.bak_topic2_confirm_memory_20260705`.
- Added `PATCH_TOPIC2_CONFIRM_BEFORE_REVISION_V1` in `core/stroyka_estimate_canon.py`.
- Confirmation phrases like `да ок` are handled before topic_2 revision routing.
- Live verification:
  - parent `33bd7b5a-ade8-47a8-b07e-4db4d3cacca8` -> `DONE`;
  - child `103a8493-2347-4f60-9dee-81ee5892ef46` -> `DONE`;
  - `AWAITING_CONFIRMATION` count for topic_2 -> `0`;
  - generic memory keys `topic_2_user_input`, `topic_2_task_summary`, `topic_2_assistant_output` point to the fresh DONE task.
- Verified: `python3 -m py_compile core/stroyka_estimate_canon.py core/topic2_estimate_final_close_v2.py task_worker.py` -> `PY_COMPILE_OK`.
- Systemd not touched. `.env` not touched. Neighbor topics not touched.
