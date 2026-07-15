# SESSION HANDOFF — 2026-07-15 topic_2 full canonical PDF estimate live cycle

This is a factual handoff record. It is not a new canon and does not replace existing canon text.

## Applied SSOT and canon

- `docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md`
- `docs/CANON_FINAL/TOPIC_2_CANONICAL_ESTIMATE_CONTRACT.md`
- `docs/SHARED_CONTEXT/TOPICS/topic_2_STROYKA.md`
- `docs/HANDOFFS/LATEST_HANDOFF.md`
- `config/estimate_template_registry.json`

Applied rules:

- topic_2 is STROYKA, direction `estimates / estimate_unified`;
- current project/task context only; old tasks and old estimate rows must not be mixed into a new task;
- missing project facts must block final generation or trigger a precise clarification; invented quantities are forbidden;
- the canonical estimate output is the 15-column AREAL_CALC structure with XLSX formulas;
- internet prices must not start without explicit authorization; search route is Sonar/Perplexity only and DeepSeek search fallback is forbidden;
- final output must contain canonical Telegram text plus Drive XLSX/PDF links;
- `DONE` is allowed only after explicit owner confirmation bound to the corresponding parent task.

## Scoped tracked runtime changes

Only these tracked runtime files were changed for the saved topic_2 work:

- `core/pdf_spec_extractor.py`
  - added bounded ARCHICAD/CAD PDF text-layer extraction from words/blocks and page geometry;
  - added current-project position and geometry extraction from the actual PDF;
  - retained OCR as fallback instead of the primary path when a usable text layer exists;
  - returned project positions, quantities, source evidence and completeness flags for the current file.
- `core/stroyka_estimate_canon.py`
  - isolated a newly uploaded PDF as a new project context;
  - blocked old task/template-row substitution;
  - added current-project volume/completeness gates;
  - preserved explicit user manual rates, VAT mode, logistics and overhead inputs;
  - generated canonical 15-column XLSX and Cyrillic PDF through the orchestra;
  - uploaded XLSX/PDF to Drive and delivered canonical Telegram final text;
  - added missing required lifecycle markers and explicit completion gating;
  - added final metadata line with explicit logistics amount.
- `task_worker.py`
  - allowed an owner-authorized duplicate file to run as a new isolated topic_2 task;
  - prevented late duplicate guards from blocking that explicit new-task route;
  - recognized topic_2 natural estimate choices such as `посчитать смету` without changing neighboring topic behavior;
  - preserved drive-file/project context while handling follow-up choices.

No task-specific UUID is hard-coded in these runtime files.

## Full live verification

### First accepted audit cycle

- Parent: `7b1df476-c1df-4dfd-a65d-e38b2df645d0`
- Telegram final message: `12494`
- Final parent state: `DONE`
- Explicit completion child: `a36c62ed-5f76-4faa-b852-0d795ab2548c`, state `DONE`

### Full repeat-as-new cycle after audit

- New parent: `d019c976-5e46-475d-bcd7-c9f349eb0ea1`
- Source file: `ирина ар проект.pdf`
- Telegram final message: `12496`
- Explicit completion child: `6968cbd9-e233-4652-8da3-b03e6758f1b4`
- Parent state after explicit confirmation: `DONE`
- Completion child state: `DONE`
- Actually open topic_2 tasks after completion: `0`

The repeat-as-new cycle was processed by the worker and canonical engine. Codex did not manually build or replace the estimate.

## Verified project and artifact facts

- PDF pages scanned: `97`
- Current-project positions extracted: `14`
- Estimate rows written: `33`
- Workbook sheets: `AREAL_CALC`, `смета`, `SOURCE_EVIDENCE`, `MISSING_DATA`, `PRICE_AUDIT`, `PROJECT_INFO`
- `AREAL_CALC`: `51 x 15`, `33` numbered rows, `103` formulas
- `смета`: `51 x 15`, `33` numbered rows, `103` formulas
- Stale terms from old projects in final workbook: `0`
- Final PDF: `2` pages, Cyrillic text valid, no `/root`, `/tmp` or raw JSON
- Google Drive metadata readback confirmed a new XLSX and a new PDF for the repeat-as-new cycle.

Final totals:

- Materials: `3 895 920.00 RUB`
- Works: `2 711 598.40 RUB`
- Logistics: `280 000.00 RUB`
- Overhead: `135 579.92 RUB`
- Without VAT: `7 023 098.32 RUB`
- VAT 22%: `0.00 RUB` because the current task explicitly requested calculation without VAT
- Final total: `7 023 098.32 RUB`

Price/search facts:

- explicit manual user rates were used;
- marker `TOPIC2_PRICE_SEARCH_NOT_REQUESTED_NO_INTERNET` is present;
- no Sonar, DeepSeek or search-start marker exists for the verified parent;
- no internet request was made for this task.

## Required marker verification for repeat-as-new parent

Each required marker was present exactly once:

- `TOPIC2_ESTIMATE_SESSION_CREATED`
- `TOPIC2_CONTEXT_READY`
- `TOPIC2_TEMPLATE_SELECTED`
- `TOPIC2_PRICE_ENRICHMENT_DONE`
- `TOPIC2_PRICE_CHOICE_CONFIRMED`
- `TOPIC2_LOGISTICS_CONFIRMED`
- `TOPIC2_XLSX_CREATED`
- `TOPIC2_PDF_CREATED`
- `TOPIC2_PDF_CYRILLIC_OK`
- `TOPIC2_DRIVE_UPLOAD_XLSX_OK`
- `TOPIC2_DRIVE_UPLOAD_PDF_OK`
- `TOPIC2_TELEGRAM_DELIVERED`
- `TOPIC2_MESSAGE_THREAD_ID_OK`
- `TOPIC2_DONE_CONTRACT_OK`

## Verification commands and results

- `python3 -m py_compile core/pdf_spec_extractor.py core/stroyka_estimate_canon.py core/topic2_input_gate.py task_worker.py` -> `OK`
- `git diff --check -- core/pdf_spec_extractor.py core/stroyka_estimate_canon.py task_worker.py` -> `OK`
- `areal-task-worker` -> `active`
- topic_2 memory keys were synchronized to parent `d019c976-5e46-475d-bcd7-c9f349eb0ea1` after completion.

## Server-only backups

- `backups/topic2_full_live_cycle_20260715_184018/`
- `backups/github_save_topic2_20260715_20260715_192844/`

Backups, DB files, runtime artifacts and secrets are server-only and are not part of the GitHub save.

## Not touched and not committed

- `.env`, credentials, tokens and sessions
- `data/core.db`, `data/memory.db`, runtime artifacts and Drive exports
- systemd unit files and launch commands
- `core/ai_router.py`, `core/reply_sender.py`, `core/google_io.py`
- topic_5, topic_210, topic_500 and other neighboring topic logic
- unrelated untracked files already present in the working tree
- no branch was created

## Current status and remaining verification boundary

The current single-PDF project estimate contour is `VERIFIED LIVE` end to end:

`new project -> current PDF extraction -> volume gate -> manual rates/no internet -> canonical XLSX/PDF -> Drive -> Telegram -> explicit confirmation -> DONE -> memory sync`.

This verification does not claim full closure of every topic_2 input form. Separate owner-driven live tests remain for photo-only input, voice continuation, reply/pin continuation, and other multifile/project variants.
