# NOT CLOSED 2026-05-06 — TOPIC2 STROYKA

Mode: FACT ONLY
Source: live terminal outputs supplied in current chat
Scope: topic_id=2 only

## Not closed by supplied live output

### P0 — Final estimate generation after price bind is not verified

Facts:

- V5 guard printed `PATCH_TOPIC2_PRICE_CHOICE_BIND_AND_FINALIZE_V5_READY_TRUE`
- History contains `TOPIC2_PRICE_CHOICE_CONFIRMED:median` for parent `f1ef9fab-e364-46ac-b0da-ab8ae5c85a21`
- Runtime log contains `PATCH_TOPIC2_PRICE_CHOICE_BIND_V5_GENERATED parent=f1ef9fab-e364-46ac-b0da-ab8ae5c85a21 choice=median`
- Final DB output still shows parent `f1ef9fab-e364-46ac-b0da-ab8ae5c85a21` in `WAITING_CLARIFICATION`
- Final supplied output does not show `TOPIC2_XLSX_CREATED`
- Final supplied output does not show `TOPIC2_PDF_CREATED`
- Final supplied output does not show `TOPIC2_DRIVE_UPLOAD_XLSX_OK`
- Final supplied output does not show `TOPIC2_DRIVE_UPLOAD_PDF_OK`
- Final supplied output does not show `TOPIC2_TELEGRAM_DELIVERED`
- Final supplied output does not show `TOPIC2_DONE_CONTRACT_OK`

Required closure:

```text
After TOPIC2_PRICE_CHOICE_CONFIRMED:median on parent f1ef9fab-e364-46ac-b0da-ab8ae5c85a21,
the engine must continue to final XLSX/PDF generation and delivery.
```

Acceptance:

```text
parent task state becomes DONE or AWAITING_CONFIRMATION only with artifact links
history contains TOPIC2_XLSX_CREATED
history contains TOPIC2_PDF_CREATED
history contains TOPIC2_PDF_CYRILLIC_OK
history contains TOPIC2_DRIVE_UPLOAD_XLSX_OK
history contains TOPIC2_DRIVE_UPLOAD_PDF_OK
history contains TOPIC2_TELEGRAM_DELIVERED
history contains TOPIC2_DONE_CONTRACT_OK
Telegram result contains valid Excel and PDF links
```

### P0 — Topic2 keeps reasking price menu on non-estimate status question

Facts:

- Task `ceac25be-a380-419c-9eec-a7b69b97da44` raw input was `[VOICE] Какая у тебя последняя задача? Ответь мне!`
- It reached `WAITING_CLARIFICATION` and showed price choice menu before V5 requeue
- History shows repeated `TOPIC2_PRICE_CHOICE_REQUESTED` on that task
- This is not a direct estimate task text

Required closure:

```text
Topic2 status/meta questions must answer current active task status, not show price menu.
Only explicit price replies 1/2/3/4 or price words must bind to active price menu.
```

Acceptance:

```text
"Какая последняя задача?" returns current task/status summary
it does not create a new price menu
it does not bind price choice unless raw input contains explicit price choice
```

### P0 — Old bad DONE estimates quarantined, but not regenerated

Facts:

- V4 output: `bad_done_quarantined= 2`
- DB output shows:
  - `edcf944b-d386-43c7-8da6-f040f98e5272 | AWAITING_CONFIRMATION | PATCH_TOPIC2_LEGACY_BAD_DONE_BLOCKED_NO_PRICE_CONFIRM`
  - `9b0626f1-eb6f-4b92-ba6a-9e28cb26be31 | AWAITING_CONFIRMATION | PATCH_TOPIC2_LEGACY_BAD_DONE_BLOCKED_NO_PRICE_CONFIRM`
- No final artifact markers were shown for these tasks after quarantine

Required closure:

```text
Legacy bad DONE estimates must either be regenerated after explicit price confirmation or remain blocked with clear user-visible state.
They must not be counted as complete final estimates.
```

Acceptance:

```text
No legacy task remains in AWAITING_CONFIRMATION with median result and no confirmed price/artifact markers
```

### P1 — Photo recognition estimate contour not verified in current live output

Facts:

- Code markers show `core/photo_recognition_engine.py`
- Log earlier showed `FIX_P6_TOPIC2_PHOTO_ROUTE_V1 skipped: _p6_handle_photo_20260504 not found`
- Existing old photo tasks showed results, but final current patch output did not verify new photo→estimate→XLSX/PDF/Drive flow

Required closure:

```text
Photo in topic_2 with estimate intent must route to photo recognition, then price choice, then XLSX/PDF/Drive artifact generation.
```

Acceptance:

```text
TOPIC2_PHOTO_RECOGNITION_DONE
TOPIC2_PHOTO_CONTEXT_USED
TOPIC2_PRICE_CHOICE_REQUESTED or TOPIC2_PRICE_CHOICE_CONFIRMED
TOPIC2_XLSX_CREATED
TOPIC2_PDF_CREATED
TOPIC2_DRIVE_UPLOAD_XLSX_OK
TOPIC2_DRIVE_UPLOAD_PDF_OK
```

### P1 — Internet price enrichment is not verified in final current output

Facts:

- User requirement: estimate pricing must use internet price check
- Code markers show `core/price_enrichment.py`
- Earlier history contains `FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3:prices_shown`
- Final current output did not show fresh price enrichment markers leading into final artifact generation

Required closure:

```text
Estimate flow must perform price search/enrichment before price choice and final generation.
```

Acceptance:

```text
TOPIC2_PRICE_ENRICHMENT_STARTED
TOPIC2_PRICE_ENRICHMENT_DONE
price menu shown with internet/template price context
confirmed price choice applied to generated XLSX/PDF
```

## Forbidden next actions

- Do not patch `.env`
- Do not patch credentials or sessions
- Do not patch `google_io.py`
- Do not patch `memory.db` schema
- Do not patch `ai_router.py`
- Do not patch `telegram_daemon.py`
- Do not patch `reply_sender.py`
- Do not patch systemd unit files
- Do not change DB schema without explicit permission
- Do not rewrite core architecture

## Next diagnostic required before code patch

```text
Show parent task f1ef9fab-e364-46ac-b0da-ab8ae5c85a21 after V5:
- task row
- task_history actions after 07:42:41
- memory pending estimate keys for topic_2
- code window where V5 calls generation after price bind
- log around PATCH_TOPIC2_PRICE_CHOICE_BIND_V5_GENERATED
- artifact output folders for this task
```
