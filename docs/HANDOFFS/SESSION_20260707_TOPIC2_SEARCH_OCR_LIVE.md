---

# Session handoff — 2026-07-07 topic_2 / search / live dialogue

This is a factual handoff record. It is not a new canon and does not replace existing canons.

## Applied canon / SSOT baseline

- `docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md`: `INSTALLED != VERIFIED`; topic statuses at session time: `topic_2 STROYKA = INSTALLED_NOT_VERIFIED`, `topic_5 TEKHNADZOR = BROKEN`, `topic_500 VEB_POISK = BROKEN`.
- `docs/CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md` §12:
  - estimate facts only from current user task, uploaded project, photo, PDF, OCR text, reply context or explicit clarification;
  - old tasks/pin/context must not be mixed into a new task;
  - missing data requires precise clarification; invented positions/volumes/materials are forbidden;
  - PDF/OCR/voice/reply/pin/fixed-message context belongs to canonical topic_2 flow;
  - internet prices require explicit user authorization or valid cache/memory reuse;
  - topic_2 search route = Sonar/Perplexity only; DeepSeek forbidden;
  - final topic_2 result must be Telegram + Google Drive XLSX/PDF links;
  - `DONE` only after explicit owner confirmation for the parent task.
- `docs/ARCHITECTURE/ORCHESTRA_MASTER_BLOCK.md`: file -> processed -> artifact -> Drive/GitHub link -> Telegram -> `AWAITING_CONFIRMATION`; Perplexity for search, DeepSeek for final answer only.

## What was done today

### Search / internet route

- Verified owner-visible issue: OpenRouter logs showed DeepSeek calls near search work; this violates search canons if the call belongs to internet/search route.
- Existing policy baseline remains: ordinary chat may use `DEFAULT_MODEL=deepseek/deepseek-chat`; internet/search must use `ONLINE_MODEL=perplexity/sonar`; DeepSeek fallback for search is forbidden.
- Further full cross-topic search verification remains open; do not assume all search surfaces are fully closed until live-tested.

### topic_2 live task `287a613c-c47d-4fae-9a71-d57fa3f2b762`

User task: two files are one project; calculate construction cost and material cost by project; if data is missing ask; internet prices only after confirmation. Files attached in project context:

- `/root/.areal-neva-core/runtime/drive_files/287a613c-c47d-4fae-9a71-d57fa3f2b762_Раздел 4 - КР.pdf`
- `/root/.areal-neva-core/runtime/drive_files/287a613c-c47d-4fae-9a71-d57fa3f2b762_Раздел 3 - АР.pdf`

Facts established:

- Multifile context was attached as one project.
- `Раздел 4 - КР.pdf` was processed through `core/pdf_spec_extractor.py` but extractor returned only 8 rows in the live flow.
- The 8-row output is not sufficient for canon: project KR has visible specification tables, including BФм1/floor and truss/foundation schedules.
- Current final artifact was delivered, but it is not a fully canonical estimate because OCR/spec extraction is incomplete.

Current task state after lifecycle repair:

- `state = AWAITING_CONFIRMATION`
- `bot_message_id = 12283`
- Excel: `https://drive.google.com/file/d/1V0T5PRcZqIrvNeGAnDJQ_UextGvHYdXf/view`
- PDF: `https://drive.google.com/file/d/1yuJUrvi5gPmSSpULrWtypMKzINPC0D5R/view`
- `bad_after_98688 = 0`, `recovery_after_98688 = 0`, `sanitize_after_98688 = 0`, `done_contract_after_98688 = 0` in the last live check.

Runtime fixes applied during the session:

- `task_worker.py`
  - widened topic_2 artifact-marker history lookup so old delivered Drive/TG markers are not lost behind noisy history;
  - prevented project parent task with its own PDF/project context from being treated as a child follow-up update;
  - prevented sanitizer from rewriting already canonical Drive XLSX/PDF final text;
  - guarded repeated `TOPIC2_DONE_CONTRACT_OK` writes;
  - blocked automatic `DONE` transition for a delivered topic_2 parent unless `TOPIC2_EXPLICIT_CONFIRM%` exists;
  - restored task `287a...` to `AWAITING_CONFIRMATION` with Drive links after old guards had forced `FAILED`.
- `core/stroyka_estimate_canon.py`
  - protected active same-task multifile/project pending context from stale-deprecation;
  - added logistics/delivery price-search terms when project distance is present.
- `core/pdf_spec_extractor.py`
  - confirmed exact root cause: OCR/page selection did not include all needed KR pages and stopped early after 8 rows;
  - adjusted KR targeted page order toward end-of-file specification sheets;
  - increased the row threshold before early stop;
  - added page-specific OCR settings for the last KR specification page.

Verification performed:

- `python3 -m py_compile task_worker.py core/stroyka_estimate_canon.py core/pdf_spec_extractor.py` passed after the lifecycle repairs and after the OCR extractor edits.
- Live task `287a...` stopped cycling after final worker reload: no new `TOPIC2_FORBIDDEN_FINAL_RESULT_BLOCKED`, recovery, sanitizer or repeated DONE markers after history id `98688`.
- OCR extractor diagnostic facts:
  - PDF has 26 pages;
  - old fast pages were `[24, 22, 26]` or similar and missed/under-read required tables;
  - corrected targeted order reached `[26, 22, 24]`;
  - full extractor was still too slow for live use: bounded 70-90 second tests timed out;
  - single-page OCR confirmed useful table text on page 26, including BФм1/floor material rows, but the integrated extractor still needs a faster targeted parser path.

## Open blockers / not closed

1. topic_2 OCR/PDF extraction is not closed.
   - Must add a fast targeted KR table parser path for page 26 / BФм1/floor table and truss/foundation sheets.
   - Must not hand-build the estimate manually; orchestra must extract rows and build artifacts itself.
   - Must re-run full live cycle only after extractor returns canonical project rows within a bounded runtime.

2. topic_2 final estimate for task `287a...` is delivered but not accepted as fully canonical.
   - It has Drive links and is stable in `AWAITING_CONFIRMATION`.
   - It must be regenerated by the orchestra after OCR/spec extraction is fixed.
   - It must include construction work + material cost from actual project specs, not invented rows.

3. Search/product-search contour still needs full live verification.
   - DeepSeek must not be used for internet/search under any topic.
   - Duplicate contacts must be filtered by phone number.
   - Links/sites/groups must be checked as live before public output.
   - Long search output should go to Google Drive with a Telegram link when needed.

4. Live reply / memory / file-context contour remains open.
   - Replies, pins, duplicate files, already-uploaded Telegram files, voice continuation and active/short/long/archive memory must work system-wide.
   - When an existing file is found in Telegram memory, the bot must reply/link to the original Telegram file/message, not dump irrelevant old estimates.
   - Completion phrases must close only the relevant parent task and must not cancel unrelated work.

5. topic_5 TEKHNADZOR remains broken by SSOT status and was not repaired today.
   - Needs canon-first verification of file intake, technical documentation binding, normative modules/SP/GOST lookup, live answer logic and final artifact delivery.

6. topic_210 PROEKTIROVANIE remains not verified.
   - Same file/document/OCR/memory/reply principles must be checked under its own canon before any patch.

7. Working tree is dirty and broad.
   - Do not commit broad dirty tree blindly.
   - Safe GitHub save for this stop point is this handoff record plus explicitly scoped files only after review.
   - `.env`, DB files, Telegram artifacts, Drive exports, heavy media, backups and secrets must not be committed.

## Next start point

Start from `core/pdf_spec_extractor.py` only:

1. Read SSOT + topic_2 canon + file/OCR parts again.
2. Inspect current extractor diff and backups:
   - `core/pdf_spec_extractor.py.bak_kr_ocr_page25_fullscan_20260707_1730`
   - `core/pdf_spec_extractor.py.bak_kr_ocr_targeted_pages_20260707_1745`
3. Implement bounded targeted parser for KR specification pages instead of full-page slow OCR loop.
4. Verify extractor on `287a..._Раздел 4 - КР.pdf` returns project rows from page 26 and truss/foundation schedules inside a bounded time.
5. Only then rerun the topic_2 task through the orchestra; do not calculate manually in Codex.
