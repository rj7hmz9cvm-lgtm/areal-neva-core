# 09_FILE_INTAKE_DRIVE_UPLOAD_2026-04-30

MODE: FACTS ONLY
SOURCE: current chat, 2026-04-30
STATUS: PARTIAL_FIX_INSTALLED / DRIVE_UPLOAD_NOT_CLOSED

## CONFIRMED FACTS

- Telegram file tasks are created as `input_type='drive_file'`, not `file`.
- `drive_file.raw_input` contains file metadata including `file_id`, `file_name`, `mime_type`, `caption`, `telegram_message_id`, `telegram_chat_id`.
- `drive_file` without clear `caption/user_intent` must enter `NEEDS_CONTEXT` before download or processing.
- `drive_file -> NEEDS_CONTEXT -> menu` was verified on live tasks.
- `bot_message_id` for file menu was saved.
- Reply/voice/text choice priority was patched before role/confirm/finish/chat logic.
- Local artifact generation worked for task `d95b1fcb-b31f-4b2f-b0a2-3342c8d35984`.
- That task reached `AWAITING_CONFIRMATION`.
- Result contained `Нормализовано позиций: 32`.
- Drive upload failed with `invalid_grant: Token has been expired or revoked`.
- Service Account healthcheck returned `ok=True`.
- Service Account email: `ai-orchestra@areal-neva-automation.iam.gserviceaccount.com`.
- Drive folder id: `13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB`.
- Helper module created: `/root/.areal-neva-core/core/drive_service_account_uploader.py`.
- Live `/root/.areal-neva-core/core/engine_base.py` is missing.
- `import core.engine_base` returned `NOT_FOUND`.
- Live files still import `core.engine_base`.
- Backup source found: `/root/.areal-neva-core/core.bak.before_rollback_20260427_202634/engine_base.py`.

## PATCHES INSTALLED IN CURRENT SESSION

### PATCH_FILE_INTAKE_NEEDS_CONTEXT_V3_MINIMAL
Status: INSTALLED

Facts:
- Added file-intake menu logic for `drive_file`.
- Added `NEEDS_CONTEXT` path.
- Added topic-based menus.
- Syntax OK and worker active after install.

### PATCH_DRIVE_GUARD_BEFORE_DOWNLOAD_V1
Status: INSTALLED

Facts:
- Moved intent and `NEEDS_CONTEXT` guard before `_download_from_drive`.
- Fixed issue where download path could block before menu.

### PATCH_WORKER_PICK_BEFORE_STALE_V1
Status: INSTALLED

Facts:
- Moved task pick before stale recovery.
- Later confirmed this was not the final root cause of stuck `drive_file` tasks.

### PATCH_FIX_PFIN3_MENU_SHADOW_V1
Status: VERIFIED

Facts:
- Fixed Python bug `_pfin3_menu = _pfin3_menu(...)`.
- Removed `UnboundLocalError` caused by local variable shadowing function.
- Tasks `d95b1fcb...` and `1e7b6864...` moved from `NEW` to `NEEDS_CONTEXT`.
- `bot_message_id` saved: `8149` and `8150`.
- `FILE_INTAKE_GUARD_HIT` appeared in logs.

### PATCH_FILE_CHOICE_PRIORITY_V1
Status: INSTALLED_PARTIALLY_VERIFIED

Facts:
- Added priority file-choice handler before role/confirm/finish/chat logic.
- Tech-supervision topic task `d95b1fcb...` reached `AWAITING_CONFIRMATION`.
- Project topic task `1e7b6864...` became `CANCELLED` after user reply parsed as cancel/check.

### PATCH_DRIVE_SERVICE_ACCOUNT_PRIMARY_V1
Status: INSTALLED_NOT_COMPLETE

Facts:
- Service Account uploader module was created.
- Service Account healthcheck returned `ok=True`.
- Folder id confirmed as `13No7_E7Mwj1n1awNQ-lzbohWGOiEM2PB`.
- Common upload path is not closed because live `core/engine_base.py` is missing.

## ERRORS FOUND

- Initial guard targeted `input_type='file'`, but real input is `drive_file`.
- Guard was initially after download, so download could block before menu.
- `_download_from_drive` could block the file-intake menu path.
- `_pfin3_menu` variable shadowed `_pfin3_menu()` function.
- Drive upload failed with `invalid_grant: Token has been expired or revoked`.
- `core.engine_base` missing while live engines still import it.
- Generated `engine_base.py` from scratch was rejected as unsafe.
- `find`-based patch selected backup `engine_base.py` instead of live path.

## CURRENT BROKEN POINT

Permanent Drive artifact upload is not closed.

Reason:
- OAuth token path failed with `invalid_grant`.
- Service Account exists and healthcheck works.
- Common module `core.engine_base.py` is missing from live core directory.
- Engines import `core.engine_base`.
- Upload path cannot be safely patched until `engine_base.py` is restored from confirmed source.

## CANON DECISIONS

- Do not use daily manual OAuth token repair as final solution.
- token OAuth is legacy fallback only, not primary upload path.
- Primary Drive upload must use Service Account.
- Drive failure must not break file task if local artifact exists.
- Do not recreate `engine_base.py` by guessing.
- Restore `engine_base.py` only from confirmed source.
- Do not patch `.env`.
- Do not delete token or credentials files.
- Do not rewrite `estimate_engine.py`, `dwg_engine.py`, or `project_engine.py` unless diagnostics prove direct need.

## REQUIRED ENGINE_BASE CONTRACTS

`core.engine_base` must provide at least:

- `detect_real_file_type`
- `update_drive_file_stage`
- `upload_artifact_to_drive`
- `quality_gate`
- `calculate_file_hash`
- `normalize_unit`
- `is_false_number`
- `normalize_item_name`

## NEXT VALID PATCH REQUIREMENT

Patch is allowed only after confirming source for `core/engine_base.py`.

Confirmed source found in current session:
- `/root/.areal-neva-core/core.bak.before_rollback_20260427_202634/engine_base.py`

Patch plan agreed by Claude:

1. Restore `/root/.areal-neva-core/core/engine_base.py` from confirmed backup.
2. Replace only `upload_artifact_to_drive` with Service Account primary implementation.
3. Do not touch `.env`, credentials, or token files.
4. Do not touch engines unless direct diagnostic need appears.
5. Run `py_compile`.
6. Verify `import core.engine_base`.
7. Run live upload test using `upload_artifact_to_drive('/tmp/testfile', 'healthcheck_<ts>', 0)`.
8. Require returned `drive.google.com` link.
9. Restart `areal-task-worker`.
10. Verify service active.
11. Verify no `invalid_grant` in primary Service Account upload path.

## ACCEPTANCE CRITERIA

Final status can be VERIFIED only if:

- `/root/.areal-neva-core/core/engine_base.py` exists.
- `import core.engine_base` resolves to `/root/.areal-neva-core/core/engine_base.py`.
- Required functions import successfully.
- Service Account upload test returns a `drive.google.com` link.
- `areal-task-worker` is active.
- File task can reach `AWAITING_CONFIRMATION` without being blocked by Drive OAuth.
- New upload path does not use OAuth token as primary path.
- No new `invalid_grant` occurs in Service Account primary path.

## CURRENT STATUS

- File intake: PARTIALLY FIXED.
- Reply choice priority: INSTALLED_PARTIALLY_VERIFIED.
- Local artifact generation: VERIFIED for one task.
- Service Account healthcheck: VERIFIED.
- Permanent Drive upload: NOT CLOSED.
- Next state: READY_FOR_PATCH after restoring confirmed `engine_base.py`.
