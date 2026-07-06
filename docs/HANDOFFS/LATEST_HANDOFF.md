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

---

## Progress 2026-07-06 — session close / topic_2 live repair state

Owner rules for all next work:
- Work only from existing SSOT/canons; no invented canons, branches, architecture, routes, defaults or adjacent-topic behavior.
- If behavior is not written in the canon/SSOT, do not do it by default.
- Every task must be carried to the end unless the owner explicitly stops/cancels it.
- Before any server file/database write: show applied canon/baseline/minimal target, make backup, then patch only the violating file.
- Do not touch systemd, `.env`, launch commands, secrets, `core/ai_router.py`, `core/reply_sender.py`, `core/google_io.py`, neighboring topics, or Git push without explicit owner permission.

Current live result:
- Latest PDF/project estimate task `7dab7ad1-3335-4385-b942-4c734dbdbebe` is `DONE`.
- Confirmation/final child tasks `24e594b9-1ea3-4b82-86ab-e9355021289b` and `39af79c1-80eb-4735-8f4f-61548cf13b2e` are `DONE`.
- Canonical Telegram final was delivered in topic_2 with Drive links:
  - Excel: `https://drive.google.com/file/d/1S27hmlqylphbfzxpn6dx6V56cjl0sfTy/view`
  - PDF: `https://drive.google.com/file/d/16UDyFcYXlkGtG5-ow4RlqI-cXz3-OpHT/view`
- Memory keys `topic_2_user_input`, `topic_2_task_summary`, `topic_2_assistant_output` were updated only after `DONE`.

Runtime diff that exists and must be treated as current working baseline:
- `core/price_enrichment.py`: price search cache for recent Perplexity/Sonar material searches; DeepSeek is not a search fallback.
- `core/stroyka_estimate_canon.py`: VAT default without VAT, 22% wording, canonical artifact naming, final confirmation close, stricter source matching, project rows/materials/work rows logic.
- `core/topic2_estimate_final_close_v2.py`: final artifact bridge and guards against zero/area-only invalid final artifacts.
- `task_worker.py`: topic_2 drive-file picker/clarification routing and canonical generate route for price-confirmed Drive files.

Topic_2 is still not fully closed:
- Overall status remains `PARTIAL LIVE VERIFIED / NOT FULL CANON CLOSED`.
- Remaining live regressions: photo with/without caption, OCR/PDF/XLSX/multifile intake, voice continuation, reply continuation, memory query, pin isolation, file/project variants.
- Estimate logic still needs verification that every project-derived item is from the uploaded project or explicit user text, with missing data asked as clarification and internet/product search used only by canon.
- Final output must remain Drive links in Telegram format, not local paths and not manual Telegram file-send unless explicitly requested.

Do not repeat next time:
- Do not send XLSX/PDF manually into Telegram when canonical final requires Drive links.
- Do not treat examples/templates such as M-80 as a fixed etalon; use them as templates/samples per registry and project facts.
- Do not regenerate prices through internet if valid recent search results are already in memory/cache and canon allows reuse.

Verification at session close:
- `python3 -m py_compile core/stroyka_estimate_canon.py core/price_enrichment.py core/topic2_input_gate.py task_worker.py` -> `PY_COMPILE_OK`.
- `topic_2` task counts at close: `ARCHIVED=12`, `CANCELLED=143`, `DONE=205`, `FAILED=143`.
- Cron GitHub sync was observed as enabled: `*/5 * * * * /root/.areal-neva-core/tools/full_context_aggregator_guard.sh ...`.

---

## Progress 2026-07-06 — two-day topic_2 rules and live repair record

This is a factual handoff record for the work done on 2026-07-05 and 2026-07-06. It is not a new canon and does not rewrite existing canon text.

Applied canon sources:
- `docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md`
- `docs/CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md`
- `docs/SHARED_CONTEXT/TOPICS/topic_2_STROYKA.md`
- `docs/HANDOFFS/LATEST_HANDOFF.md`

Owner operating rules confirmed during the session:
- Before any action, read and apply the relevant SSOT/canon.
- Improvisation is forbidden: if a behavior is not written in SSOT/canon, do not do it by default.
- Existing canons may only be appended to after explicit owner approval; do not rewrite or replace canon text.
- Every task must be carried to completion unless the owner explicitly stops, cancels, or pauses it.
- Before any server write: show canon/baseline/minimal target, make backup, and patch only the scoped file.
- Do not touch systemd, `.env`, launch commands, secrets, `core/ai_router.py`, `core/reply_sender.py`, `core/google_io.py`, neighboring topics, branches, or Git push without explicit owner permission.

Topic_2 functional rules clarified and treated as current working baseline:
- `topic_2` / STROYKA estimates must be produced by the orchestra canonical engine, not manually by Codex.
- Estimate input must come from the actual user task, uploaded project, photo, PDF, OCR text, or explicit clarification; old task data must not be mixed into a fresh task.
- Unknown or missing data must be clarified with the user instead of invented.
- Photo/PDF/OCR/voice/reply/pin/fixed-message context must participate in live dialogue according to canon; if a file was already provided, the bot must not ask for the same file again.
- Price search must not run automatically when valid fresh cache/memory already contains the relevant prices.
- When prices are missing or stale and internet prices are needed, search must be confirmed/authorized by the user and use Sonar/Perplexity only; DeepSeek is forbidden for search.
- Topic_2 XLSX output must remain canonical `AREAL_CALC` with 15 columns; the old 8-column XLSX format is forbidden.
- Work and material parts of one operation should stay in one estimate row when they are one smeta position, using work and material columns in the same 15-column row.
- VAT baseline is 22%, not 20%; default estimate output is normally without VAT unless the user selects or confirms a VAT mode.
- The supported VAT mode from the live correction is: materials with VAT, works without VAT.
- Final topic_2 result must be delivered in Telegram with Google Drive links for XLSX and PDF. Local paths or manual file-only delivery are not canonical final output.
- `DONE` is allowed only after explicit owner confirmation.

Tasks and runtime work recorded from the two-day session:
- VAT policy work: removed/avoided `НДС 20%` in checked topic_2 paths, switched visible VAT logic to 22%, and added user-facing clarification for VAT mode.
- PDF/project flow work: waiting-project phrases bind to the subsequent PDF/file, and PDF without caption can bind to the waiting project task instead of asking for the same file again.
- Confirm-close work: reply confirmation such as `да ок` closes the correct topic_2 parent only after explicit confirmation and updates topic_2 memory after `DONE`.
- Search/memory baseline: recent valid Sonar/Perplexity price results should be reused from cache/memory when allowed; internet price search should not be repeated unnecessarily.
- Foundation live task repair:
  - parent task `ef67a6f0-c6e2-436e-904b-58d2c48ca3a0`;
  - VAT correction child `b7b260d1-4d23-4819-ba3c-1970cad5a04b` merged back to the parent;
  - latest Telegram final message: `bot_message_id=11843`;
  - parent remains `AWAITING_CONFIRMATION`, not `DONE`, until explicit owner confirmation;
  - final Drive Excel: `https://drive.google.com/file/d/1KZdfSEuuXoxMWh-93HoVIBI1i9lySfYP/view`;
  - final Drive PDF: `https://drive.google.com/file/d/11sqwkORpp3AilkR2ys2C4qdyeyQ73rS6/view`.
- Foundation XLSX/PDF repair:
  - sand cushion and gravel base are now one mixed row each, with work and material prices in the same `AREAL_CALC` row;
  - material VAT mode uses 22% on material totals only;
  - checked final summary values: materials `1 141 542`, works `1 078 592`, logistics `241 875`, overhead `188 711`, total without VAT `2 650 721`, VAT 22% on materials `251 139`, total with material VAT `2 901 860`.

Verification recorded:
- `python3 -m py_compile task_worker.py core/stroyka_estimate_canon.py core/topic2_input_gate.py core/ocr_engine.py` passed during the live repair.
- PDF text was verified to contain the VAT/material totals.
- No systemd change was made.
- `.env`, `core/ai_router.py`, `core/reply_sender.py`, `core/google_io.py`, and neighboring topics were not touched for this save record.

Open blockers remain:
- Topic_2 overall remains `PARTIAL LIVE VERIFIED / NOT FULL CANON CLOSED`.
- Still needs full live verification for photo with/without caption, OCR/PDF/XLSX/multifile intake, voice continuation, reply continuation, memory query, pin isolation, and file/project variants.
- Still needs verification that every estimate row is sourced from the current project/user input or an explicit clarification/search source.
- Canon append/addendum is not written here; if needed, it must be shown separately and appended only after explicit owner approval.

---

## Progress 2026-07-06 — topic_500 search delivery and output-format checkpoint

This is a factual handoff record for the topic_500 / internet-search work done on 2026-07-06. The task is not fully closed.

Applied canon sources:
- `docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md`
- `docs/CANON_FINAL/TOPIC_500_UNIVERSAL_SEARCH_CANON.md`
- `docs/SHARED_CONTEXT/TOPICS/topic_500_VEB_POISK.md`
- `docs/HANDOFFS/LATEST_HANDOFF.md`

Canon addendum written:
- `docs/CANON_FINAL/TOPIC_500_UNIVERSAL_SEARCH_CANON.md` now has append-only `§11. Append-only addendum 2026-07-06 — long result delivery and contact-first search output`.
- The addendum fixes the contract for long search results: full result goes to Google Drive, Telegram receives the Drive link.
- The addendum fixes public procurement/service-local output: `Profile/поставщик`, `Сайт/ссылка`, `Телефон`, `Цена/условия`, `Город/регион`, `Доставка/выезд`, `Дата проверки`, `Статус проверки`.
- It records that link/profile and phone are the main user-facing fields for contractor/supplier search.
- It records that service comments, internal statuses, unnecessary explanation blocks, and unhelpful risk/comment blocks must not pollute the public result.

Runtime work completed:
- `core/reply_sender.py`: long Telegram replies are written to `data/telegram_artifacts`, uploaded to Google Drive through the existing topic Drive OAuth path, and delivered to Telegram as a Drive link.
- `core/search_session.py`: topic_500 procurement/service-local prompt and postprocess now prefer compact contact-first public output.
- `core/output_sanitizer.py`: internal English search markers are translated for public output, and the old false text "Полный результат смотри в файле" was removed unless a real file/link exists.
- `task_worker.py`: topic_500 search tasks are protected from being swallowed by old confirmation/clarification state, and validator accepts Russian source-status markers.

Live evidence:
- Previous long search result was uploaded to Google Drive and delivered in Telegram:
  - `bot_message_id=11912`
  - Drive file: `https://drive.google.com/file/d/1OP6KUrXNnrYLkpitHUF7TMxhTUCti93m/view`
- Earlier long-result delivery also succeeded:
  - Drive file: `https://drive.google.com/file/d/1TkZ066-n56ElEuAWfN2h3PW2KnpaVk6X/view`
- Worker was restarted by the existing direct `flock ... task_worker.py` method; systemd was not touched.

Open blockers remain:
- The user reports that answer logic is still not fully correct.
- Task completion/finalization appears to be a broader lifecycle/dialogue blocker, not only topic_500.
- Reply continuation, final confirmation, and lifecycle completion must be checked across the relevant canon before further patches.
- This checkpoint is intentionally not marked DONE and should be continued after the owner explains the next failure case.

Verification recorded:
- `python3 -m py_compile core/search_session.py core/reply_sender.py core/output_sanitizer.py task_worker.py core/ai_router.py` passed after the runtime changes.
- `.env` was not touched.
- systemd was not touched.
- No GitHub push was performed during this checkpoint.
## Progress 2026-07-06 — memory/live dialogue topic isolation repair

This is a factual handoff record for the memory, archive, ContextLoader, and live-dialogue context repair done on 2026-07-06. It is not a new canon and does not rewrite existing canon text.

Applied canon / SSOT rules:
- `docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md` §0.3: Git/Drive/DB/patch actions require explicit owner approval.
- `docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md` §0.4: diagnostics first: logs -> db -> pin -> memory -> context -> patch.
- `docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md` §0.5: read current file -> patch only gap -> compile -> restart -> logs.
- `docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md` §0.8: do not expose `.env`, credentials, sessions, tokens, or forbidden files without explicit permission.
- `docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md` §12/§14: GitHub stores only clean safe context; full server export and private values must not be pushed.
- `docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK.md`: GitHub = brain, server = runtime, Drive = reserve; memory context must be isolated by chat/topic.

Server backup:
- Backup directory: `/root/.areal-neva-core/backups/memory_lifecycle_20260706_181724`.
- Contents: `runtime_files_with_secrets.tgz` and `memory.db`.
- Backup intentionally excludes media, PDFs, XLSX artifacts, Telegram artifacts, Drive exports, templates, and heavy runtime output.
- Secrets were backed up only on the server and were not printed or copied into this handoff.

Runtime files patched:
- `memory_api_server.py`: ensures `topic_id` and `scope` columns exist; `/archive` and `/memory` writes preserve `topic_id/scope`; `/memory` GET can filter by `chat_id + topic_id + key`.
- `core/context_loader.py`: short memory now uses live Memory API on `127.0.0.1:8091` with Authorization instead of stale port `8765`.
- `task_worker.py`: topic role and DONE memory writes now populate `topic_id/scope` for role, user input, task summary, and assistant output.
- `core/archive_distributor.py`: archive distribution writes `topic_id/scope` into `memory.db`.

DB maintenance:
- `data/memory.db` was backed up before DB writes.
- Existing concrete topic keys were backfilled from `topic_N_*` prefixes into `memory.topic_id`.
- No memory rows were deleted.
- `topic_0_*` remains topic 0 by design.

Verification:
- `.venv/bin/python3 -m py_compile memory_api_server.py core/context_loader.py task_worker.py core/archive_distributor.py` -> `PY_COMPILE_OK`.
- `areal-memory-api.service` restarted and active.
- `areal-task-worker.service` restarted and active.
- Memory API health -> `{"status":"ok"}`.
- ContextLoader smoke test for chat `-1003725299009`, topic `2` returned 5 rows with `TOPIC_IDS [2]`.
- `concrete_topic_prefixed_topic0` -> `0`.

Not touched:
- No systemd unit files were edited.
- No launch commands were changed.
- `.env`, credentials, tokens, and sessions were not edited and not printed.
- `core/ai_router.py`, `core/reply_sender.py`, and `core/google_io.py` were not edited in this repair.
- Neighboring topic logic was not intentionally changed.
- No media/artifact folders were backed up or pushed.
- No branch was created.

Open verification:
- Live Telegram scenarios still need separate owner-driven tests: reply continuation, voice continuation, memory query, pin isolation, file/photo/PDF intake, and correct DONE closure per topic.


---

## Progress 2026-07-07 — global file memory / duplicate guard live repair

This is a factual handoff record for the live-dialogue file memory and duplicate-file repair done on 2026-07-07. It is not a new canon and does not replace existing canons.

Applied canon / SSOT rules:
- `docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md`
- `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md` §16.4: file without caption must reply to the file message and enter menu/clarification flow.
- `docs/CANON_FINAL/01_SYSTEM_LOGIC_FULL.md` §17.3: repeated file must trigger `FILE_DUPLICATE_MEMORY_GUARD_V1` / “Файл уже есть”.
- `docs/CANON_FINAL/09_FILE_INTAKE_DRIVE_UPLOAD_2026-04-30.md`: `drive_file.raw_input` contains `file_id`, `file_name`, `mime_type`, `caption`, `telegram_message_id`, `telegram_chat_id`.
- `docs/ARCHITECTURE/WORKITEM_V1.md`: supported input types include `text / voice / photo / file / drive_file / url / mixed`.

Runtime files patched:
- `core/file_context_intake.py`: duplicate guard now covers `drive_file`, `file`, `photo`, `image`, `document`; it preserves `telegram_chat_id`, builds Telegram source links, and returns `reply_to_message_id` for the current file message.
- `task_worker.py`: `drive_file` now runs common file-context prehandle before topic engines through `PATCH_GLOBAL_DRIVE_FILE_CONTEXT_PREHANDLE_V1`; file-like prehandle is allowed even for otherwise isolated topic routes without opening ordinary text routing.
- `core/file_memory_bridge.py`: historical file-memory answers can include the source Telegram message link when metadata exists.
- `core/active_dialog_state.py` and `core/reply_repeat_parent.py`: public helper answers were cleaned from internal task/status wording.

Live evidence:
- Worker restart used the existing direct `flock ... task_worker.py` method; systemd was not touched.
- `python3 -m py_compile task_worker.py core/file_context_intake.py` -> `SERVER_PY_COMPILE_OK`.
- `git diff --check -- task_worker.py core/file_context_intake.py` -> `DIFF_CHECK_OK`.
- Smoke duplicate finder returned `DUP_FOUND True` for `photo` -> `document` and generated `https://t.me/c/3725299009/111`.
- First live-control task `b7f12c67-dup-live-20260707-001` found the real bypass: `drive_file` skipped common duplicate guard and entered topic_2 PDF pipeline.
- After `PATCH_GLOBAL_DRIVE_FILE_CONTEXT_PREHANDLE_V1`, second live-control task `b7f12c67-dup-live-20260707-002` passed:
  - state `WAITING_CLARIFICATION`;
  - `reply_to_message_id=10504`;
  - `bot_message_id=12057`;
  - result starts with `Смотри, этот файл ты уже скидывал`;
  - source line includes `https://t.me/c/3725299009/10504`;
  - log line: `PATCH_GLOBAL_DRIVE_FILE_CONTEXT_PREHANDLE_V1 handled task_id=b7f12c67-dup-live-20260707-002`.

Not touched:
- No systemd unit files were edited.
- `.env`, credentials, tokens, sessions, databases, runtime media, and secrets were not printed or pushed.
- `core/ai_router.py`, `core/reply_sender.py`, and `core/google_io.py` were not edited for this repair.
- No branch was created.

Open verification:
- Need owner-driven live Telegram test with a freshly resent real photo/document/file in the target topics.
- Topic_2 full canon remains partial and still needs separate verification for estimate/photo/OCR/PDF/XLSX/multifile, memory, reply, voice, pin isolation, and DONE closure.
- General live-answer completion and memory behavior remain broader open contours.

Clean export:
- `chat_exports/CHAT_EXPORT__2026-07-07_FILE_MEMORY_LIVE_DIALOGUE_DUPLICATE_GUARD.json`
