# SESSION 2026-07-05 — topic_2 canon live repair

## Scope

This session was limited to AREAL NEVA server runtime at `/root/.areal-neva-core`, topic_2 / STROYKA estimate flow, and the user-provided live task:

`дом два этажа на монолитной плите толщиной 450, размеры 24 на 24, наружные стены полнотелый кирпич, внутренняя отделка гипсокартоном с покраской, ламинат, объект 150 км от Санкт-Петербурга, высокий уровень цен, проживание бригады и строительный лагерь, инженерные коммуникации, внутренняя отделка санузла 4 на 4`.

No `.env` secrets were printed or committed. No GitHub push was done before the final save step.

## Canon Rules Applied

- topic_2 is STROYKA / estimates.
- Fresh complete topic_2 TZ must be treated as a new task, not as a continuation of an older task.
- Current user raw TZ is the SSOT for estimate facts.
- No old template public route: `Шаблон / Лист / Цены из листа` is not allowed for final topic_2 estimate.
- Final estimate is not `DONE` until explicit user confirmation.
- XLSX must be canonical `AREAL_CALC` with 15 columns.
- Internet prices for topic_2 use `OPENROUTER_MODEL_ONLINE=perplexity/sonar`; no DeepSeek search fallback.
- If a fact is not in TZ, it must not be invented.

## Problems Found

1. Fresh complete topic_2 tasks could be merged into an older active/AWAITING task by `PATCH_TOPIC2_FOLLOWUP_BIND_TO_PARENT_TZ_V1`.
2. Fresh complete topic_2 tasks could still route into old `TOPIC2_ESTIMATE_FINAL_CLOSE_V2`, producing old template-style output.
3. Active row generation used hardcoded frame/insulation rows for walls, including `Утепление стен 150 мм`, even when current TZ said brick walls.
4. Active slab parser did not read `толщиной 450` without explicit `мм`, so slab rows fell back to `200 мм`.
5. Price search via `process_ai_task` / search monolith returned `[]` for supplier-price prompts, so topic_2 final showed `PRICE_APPLIED_0` and no applied internet prices.

## Runtime Changes Made

### `core/sample_template_engine.py`

- Added slab thickness recognition for `толщиной 450` and broader `плит...` word forms.
- Added final current-TZ row override for `_p2_build_rows`:
  - brick TZ produces brick masonry rows, not frame/insulation wall rows;
  - slab rows use parsed slab thickness, e.g. `450 мм`;
  - includes engineering communications, brigade accommodation / construction camp, logistics, finishing, overhead rows when present in current TZ.
- Added direct topic_2 Sonar price-search wrapper:
  - loads `.env` internally without printing secrets;
  - requires `OPENROUTER_MODEL_ONLINE == perplexity/sonar`;
  - rejects DeepSeek for search;
  - queries OpenRouter Sonar directly for supplier/price rows;
  - parses `Категория | Поставщик | Цена | URL` into price objects used by XLSX.

### `task_worker.py`

- Added final-order fresh full TZ guard:
  - long complete topic_2 TZ is routed to canonical P3 pipeline as a new task;
  - it is not merged into older parent tasks by followup binding;
  - it clears `reply_to_message_id` for the new canonical run.
- Earlier session patches also guarded topic_2 final estimates so generated XLSX/PDF wait in `AWAITING_CONFIRMATION`, not `DONE`, until explicit user confirmation.

### Existing files touched earlier in the same session

- `core/stroyka_estimate_canon.py`
- `core/topic2_estimate_final_close_v2.py`

Those had already been modified before this final save request and remained in the worktree.

## Live Verification

### Compile

Command:

`python3 -m py_compile core/sample_template_engine.py task_worker.py core/stroyka_estimate_canon.py core/topic2_input_gate.py core/topic2_estimate_final_close_v2.py`

Result:

`PY_COMPILE_OK`

### Final live task

Task id:

`0115efea-ed49-4263-a6f0-a981a760261c`

State:

`AWAITING_CONFIRMATION`

History markers:

- `PATCH_TOPIC2_FRESH_FULL_TZ_FINAL_GUARD_V2:CANON_P3_ROUTE`
- `TOPIC2_PRICE_CHOICE_CONFIRMED:reliable`
- `P3_TOPIC2_FINAL_AWAITING_CONFIRMATION_ROWS_22_PRICE_APPLIED_2`
- `P3_TOPIC2_FINAL_DONE_ROWS_22_PRICE_APPLIED_2`
- `TOPIC2_DONE_ONLY_AFTER_USER_YES_V1:P3_FINAL_WAITING_CONFIRMATION`

Public result included:

- object `24.0x24.0`;
- `2` floors;
- foundation `монолитная плита`;
- walls `кирпич`;
- sections: foundation, walls, floors, roof, finishing, engineering communications, construction camp/accommodation, logistics, overhead;
- price check: partial internet price application, applied positions: `2`;
- XLSX Drive link and PDF Drive link;
- waiting for user confirmation.

### XLSX verification

Generated local XLSX:

`outputs/topic2_p6c_clean/estimate_topic2_canon_0115efea.xlsx`

Confirmed rows:

- `Арматура А500С для плиты 450 мм`
- `Бетон B25 для монолитной плиты 450 мм`
- `Кладка наружных стен из полнотелого кирпича`
- `Инженерные коммуникации`
- `Организация проживания бригады и строительного лагеря`
- `Накладные расходы`

Confirmed absent from final XLSX scan:

- `Утепление стен 150 мм`

Confirmed price sheet:

- `PRICE_SEARCH_OK_SONAR_DIRECT; applied=2`
- `LIVE_CONFIRMED_SONAR` supplier rows with URLs and checked date `2026-07-05`.

## Final Runtime State

- `areal-task-worker.service`: active after restarts.
- systemd unit files were not edited.
- `.env` was not committed or printed.
- Untracked DB files, backups, `.claude`, and runtime/generated directories were not added to Git.

## Remaining Risks / Notes

- Some earlier worktree changes existed before this final save request, especially generated `docs/SHARED_CONTEXT/*` files and other topic/runtime files. They were preserved and not reverted.
- Sonar supplier-price output is now applied partially. It is still dependent on OpenRouter/Sonar availability and the quality of returned supplier rows.
- The final task remains `AWAITING_CONFIRMATION` by canon; it must only become `DONE` after explicit user confirmation.
