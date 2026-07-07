# SESSION 2026-07-07 — topic_2, search policy, file/OCR live close

This handoff records the factual work completed on 2026-07-07. It is a session record, not a replacement for existing canons. No secrets, `.env`, credentials, tokens, DB files, runtime artifacts, Telegram media, or Drive exports are included here.

## Scope

- Main topic: `topic_2` / STROYKA / estimates.
- Related shared contours: internet/product search, file intake, PDF/CAD-PDF extraction, live dialogue, reply/confirmation close.
- Explicitly preserved boundaries: no `.env`, no credentials, no sessions, no systemd launch change, no Git branch creation, no neighboring topic rewrite as part of topic_2 close.

## Search / Internet Rules Verified

- Search route for internet/product/price data must use Sonar/Perplexity only.
- DeepSeek is forbidden for internet/search and forbidden as search fallback.
- For topic_2 price enrichment, cache/memory/archive are checked before fresh Sonar search.
- Topic_2 search is only a tool for prices/materials/suppliers/logistics/norms and must not mix with topic_500 final output.
- Long/product-search output must not expose internal markers or raw JSON to Telegram.

## Topic_2 AR+KR Project Flow Closed

Source task used for live close:

- `7a06ad98-7bd1-4d1c-af57-7b375ade17e1`
- chat: `-1003725299009`
- topic_id: `2`
- source files:
  - `runtime/drive_files/287a613c-c47d-4fae-9a71-d57fa3f2b762_Раздел 3 - АР.pdf`
  - `runtime/drive_files/287a613c-c47d-4fae-9a71-d57fa3f2b762_Раздел 4 - КР.pdf`

Implemented/verified:

- CAD-PDF / project extraction for AR+KR source facts.
- Normalized billable rows for project-derived estimate rows.
- Double-count guard: unit/detail/rollup rows are not all included in `AREAL_CALC`.
- Evidence-only rows are moved to `SOURCE_EVIDENCE`.
- Material and work prices are handled as separate price requirements for each billable row.
- `PRICE_AUDIT` separates `material` and `work` prices.
- `SOURCE_EVIDENCE` is filled for calculated/derived rows.
- XLSX and PDF are regenerated and uploaded to Drive.
- Telegram final is sent with Drive XLSX/PDF links.
- `DONE` is only after explicit owner confirmation.

Final live result:

- Telegram `bot_message_id`: `12369`
- state after owner finish phrase repair: `DONE`
- XLSX: `https://drive.google.com/file/d/1WUnvjSgmVz0L1c-mBZy7HGz1JibWk9IR/view`
- PDF: `https://drive.google.com/file/d/1kO7y_N06NBvI-n2XqSL3IEDSJZTClxqx/view`

Final checked values:

- `AREAL_CALC`: 15 columns, 15 billable rows.
- formulas: work = `E*F`, material = `E*H`, total = `G+I`, final totals through `SUM`.
- `PRICE_AUDIT`: 30 rows = 15 material + 15 work, missing = 0.
- `SOURCE_EVIDENCE`: 35 rows, calculated source missing = 0.
- PDF contains work total, material total, and combined total.
- Missing project data remains explicitly listed:
  - `openings_area_m2`
  - `roof_overhangs`
  - `steel_frame_mass_kg`

## Completion / DONE Fix

Observed failure:

- Owner phrase `Всё я доволен задачей завершена` was routed into clarification/price-choice instead of closing the awaiting parent.
- Parent lookup expected text `Смета готова`, while the current AR+KR final says `Смета по извлечённым позициям готова`.
- DONE guard did not accept the new AR+KR artifact marker set and wrote a misleading `TOPIC2_DONE_BLOCKED_REASON:no_estimate_generated` marker.

Fixed:

- Finish detector recognizes additional owner-close phrases:
  - `задачей завершена`
  - `задача закрыта`
  - `задачей закрыта`
  - `доволен задачей`
  - `доволен результатом`
  - `всё верно`
  - `все верно`
- Parent lookup recognizes `Смета по извлечённым позициям готова`.
- DONE guard accepts the new marker set:
  - `TOPIC2_XLSX_CREATED`
  - `TOPIC2_PDF_CREATED`
  - `TOPIC2_DRIVE_UPLOAD_XLSX_OK`
  - `TOPIC2_DRIVE_UPLOAD_PDF_OK`
  - `TOPIC2_TELEGRAM_DELIVERED`
- Parent task `7a06ad98-7bd1-4d1c-af57-7b375ade17e1` was repaired to `DONE` after explicit owner confirmation.
- Topic_2 memory keys were updated after DONE:
  - `topic_2_user_input`
  - `topic_2_task_summary`
  - `topic_2_assistant_output`

## Verification Commands Run

- `python3 -m py_compile core/stroyka_estimate_canon.py core/pdf_spec_extractor.py core/topic2_estimate_final_close_v2.py task_worker.py core/construction_item_normalizer.py`
- XLSX validation:
  - 15 columns
  - 15 rows
  - formulas OK
  - no forbidden double-count rows
  - `PRICE_AUDIT` 30 rows
  - `SOURCE_EVIDENCE` calculated source missing = 0
- PDF validation:
  - PDF exists locally
  - PDF contains material/work/total values
- Task state validation:
  - parent state = `DONE`
  - result contains Drive XLSX/PDF links
  - memory keys updated after DONE

## Backups Created

- `backups/topic2_final_estimate_rows_work_price_20260707_224848`
- `backups/stroyka_estimate_canon.py.bak_source_evidence_20260707_230602`
- `backups/topic2_done_close_fix_20260707_232242/stroyka_estimate_canon.py.bak`
- `backups/topic2_done_state_repair_20260707_232400`

Server-only backups may contain runtime data and are not for GitHub.

## Remaining Work

- Continue live tests for other topics only as separate scoped tasks.
- Topic_5 TEKHNADZOR still needs separate canon-bound verification.
- Topic_500 universal search still needs separate live regression tests for duplicate phone filtering and source liveness, outside this topic_2 save.
