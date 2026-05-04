# ORCHESTRA_MASTER_CLOSE_20260504_STATUS

Mode: FACT ONLY
Date: 2026-05-04
Scope: facts established in the current ChatGPT/server session and verified GitHub history

---

## 1. GitHub history verification

Repository: `rj7hmz9cvm-lgtm/areal-neva-core`
Branch: `main`

GitHub search confirmed commits are visible through 2026-05-04. Latest visible commit:

```text
88c36e3 TOPIC2_REPLY_THREAD_FIX_V1: send topic2 estimates to original Telegram thread
```

Confirmed recent visible commits:

```text
88c36e3 TOPIC2_REPLY_THREAD_FIX_V1: send topic2 estimates to original Telegram thread
bf6cece TOPIC500_PRE_SEND_VALIDATOR_AND_STARTUP_RECOVERY_HARD_GUARD_V1: pre-send procurement validator and startup recovery hard guard
dc2f770 FINAL_TOPIC2_TOPIC5_TOPIC500_CLOSE_20260504_V1: close topic2 current TZ route and topic500 search output contract
75c8af2 HOTFIX_HANDLE_IN_PROGRESS_WRAPPER_CHAIN_V1: fix handle_in_progress wrapper arity
6f93ff4 TOPIC2_FULL_CLOSE_V1: map wood to frame scenario and block empty estimates
bc58444 COMBINED_TOPIC2_AND_TOPIC210_CLOSE_V1: real topic2 estimate and cad section fix
c9ce862 TOPIC2_DRIVE_AUTH_SINGLE_SOURCE_V1: use google_io drive auth and fail empty estimate
a5cdb89 TOPIC2_ESTIMATE_AND_TOPIC500_SEARCH_FULLFIX_V1: strict template estimate pdf and bypass search misroute
711b6c9 TOPIC_ROUTE_ISOLATION_FULL_V2: allow topic2 file prehandle and keep 210_500 isolated
40f139d TOPIC_ROUTE_ISOLATION_FULL_V1: isolate topic_2_210_500 handlers
```

GitHub history from 2026-04-30 through 2026-05-04 is visible. No evidence in this session that commit history was lost.

---

## 2. Runtime facts from terminal outputs

Latest verified services after final server-side patch:

```text
areal-task-worker active
telegram-ingress active
areal-memory-api active
```

Latest verified DB state for current task set:

```text
rowid 5216 topic_id=5   state=DONE
rowid 5215 topic_id=500 state=DONE
rowid 5214 topic_id=2   state=DONE
```

Task 5214 result fact:

```text
Engine: TOPIC2_REAL_ESTIMATE_FROM_TZ_V2
Object: barnhouse 12.0x8.0 m
Area: 96.0 m²
Foundation: slab 200 mm
Walls: frame
Template: M-110.xlsx
Rows: 20
Total: 3,616,536 RUB
VAT 20%: 723,307 RUB
Total with VAT: 4,339,843 RUB
Drive links returned for Excel, PDF, manifest
```

Task 5215 result fact:

```text
TOPIC500_PRE_SEND_VALIDATOR_AND_STARTUP_RECOVERY_HARD_GUARD_V1:5215_DONE_FROM_LAST_RESULT
FINAL_TOPIC500_SEARCH_DONE_20260504_V1
state=DONE
```

Task 5216 result fact:

```text
This chat = TECHNICAL SUPERVISION / technadzor
Direction: technical supervision, inspection acts, defects, SP/GOST
state=DONE
```

---

## 3. Code facts verified after final patch

### 3.1 `core/sample_template_engine.py`

Confirmed by terminal output after commit `88c36e3`:

```text
TOPIC2_REPLY_THREAD_FIX_V1 is present
_send_reply accepts topic_id
send_reply_ex receives message_thread_id when topic_id > 0
_t2sp_send accepts topic_id
fallback Telegram API receives message_thread_id when topic_id > 0
_t2sp_send direct call sites were updated with topic_id
_t2real_send accepts topic_id
_t2real_send call sites were updated with topic_id
history marker added: TOPIC2_REPLY_THREAD_FIX_V1:SENT_TO_TOPIC_{topic_id}
py_compile passed
services active after restart
```

Conclusion: topic_2 estimate thread routing bug was patched in the currently visible GitHub code.

### 3.2 `task_worker.py`

Confirmed by terminal output after commit `bf6cece`:

```text
TOPIC500_PRE_SEND_VALIDATOR_AND_STARTUP_RECOVERY_HARD_GUARD_V1 present
TOPIC500_PROCUREMENT_VALIDATOR_V1 marker present
STARTUP_RECOVERY_REPLY_SENT_GUARD_V1 marker present
TOPIC500_DUPLICATE_RESULT_LOOP_GUARD_V1 marker present
_send_once_ex wrapper uses exact positional signature: conn, task_id, chat_id, text, reply_to, kind
py_compile passed
services active after restart
```

Confirmed earlier regression:

```text
_handle_in_progress() missing 2 required positional arguments: chat_id and topic_id
```

Regression status:

```text
The traceback existed before the final patches.
After later restarts, services were active and no new current traceback was shown in the final live log window.
```

### 3.3 `core/ai_router.py`

Confirmed from GitHub current file:

```text
SEARCH_SYSTEM_PROMPT override TOPIC500_SEARCH_OUTPUT_CONTRACT_20260504_V1 is present
```

Not confirmed / not present from current visible code:

```text
TOPIC500_CONTEXT_SANITIZER_V1 is not confirmed in current ai_router.py
Current search path still sends user_text directly to ONLINE_MODEL
No confirmed sanitizer block before the model call
```

---

## 4. Regression check

Confirmed historical regression:

```text
Worker crashed due to _handle_in_progress wrapper chain arity mismatch
```

Current confirmed status:

```text
No current confirmed worker crash after final TOPIC2_REPLY_THREAD_FIX_V1 restart
areal-task-worker active
telegram-ingress active
areal-memory-api active
```

Not yet verified by new live test:

```text
fresh topic_2 estimate request after TOPIC2_REPLY_THREAD_FIX_V1
fresh topic_500 procurement search after context sanitizer/validator requirements
```

Conclusion:

```text
No currently confirmed runtime regression after commit 88c36e3
There are still unverified functional gaps listed below
```

---

## 5. Closed items

```text
1. Worker arity crash chain fixed and pushed
2. topic_500 stuck IN_PROGRESS after reply_sent/result was repaired for task 5215
3. topic_500 duplicate result loop guard installed in task_worker.py
4. topic_500 pre-send procurement validator marker installed in task_worker.py
5. startup recovery hard guard installed in task_worker.py
6. task 5215 manually repaired to DONE from last result
7. task 5214 reprocessed and DONE with estimate result
8. task 5216 completed as technadzor chat identity answer
9. tools/context_aggregator.py restored after temporary deletion state
10. topic_2 estimate reply path patched with message_thread_id propagation
11. commit 88c36e3 pushed to GitHub
```

---

## 6. Not closed / not proven

### P0 — confirmed missing or not proven

```text
1. TOPIC2_TZ_PARAM_LOCK_V1 is not confirmed by current final checks
2. wall_insulation_mm=250 is not confirmed as a separate field
3. roof_insulation_mm=300 is not confirmed as a separate field
4. distance_km=50 is reflected in result, but raw_input absolute override block is not confirmed
5. wall_type=каркас is reflected in result, but strict raw_input lock block is not confirmed
6. TOPIC500_CONTEXT_SANITIZER_V1 is not confirmed in current ai_router.py
7. clean topic_500 live-test after patches was not performed
8. topic_500 result quality is not proven against a new request with direct URLs/phones/prices
9. topic_500 validator has markers, but no live proof that invalid result is blocked before Telegram send
10. working tree contained untracked runtime/data files in server git status
```

### P1 — functional contour not closed

```text
1. Internet prices for topic_2 estimate are not implemented/proven
2. Estimate currently uses template M-110.xlsx / generated assumptions, not confirmed live supplier prices per line
3. Price source labels are not proven: LIVE_CONFIRMED / TEMPLATE_FALLBACK_PRICE / USER_ASSUMPTION
4. Material clarification gate is not implemented/proven
5. System does not yet prove it asks for insulation type/brand/density when needed before final estimate
```

---

## 7. Required next patch set

### Patch A — `core/sample_template_engine.py`

Required:

```text
Install/confirm TOPIC2_TZ_PARAM_LOCK_V1
Parse wall insulation from current raw_input near утепл*
Parse roof insulation from current raw_input near кровля
Store wall_insulation_mm and roof_insulation_mm separately
Parse distance_km from current raw_input and forbid memory/template overwrite
Force wooden/beam/frame/barn words to wall_type=каркас and material=каркас
Show both wall and roof insulation in final user result
Write params to manifest for verification
```

### Patch B — `core/ai_router.py`

Required:

```text
Install TOPIC500_CONTEXT_SANITIZER_V1 on user_text before ONLINE_MODEL call
Remove old supplier tables from context
Remove Trust Score/TCO/НЕ ПОДТВЕРЖДЕНО/ЭТАП N fragments
Remove naked [1]/[2]/[3] source markers without URL
Ensure current user query remains intact
```

### Patch C — live verification only after A/B patches

Required:

```text
Fresh topic_2 estimate request
Fresh topic_500 procurement search request
Check logs for Traceback/TypeError/SyntaxError
Check DB state for DONE/AWAITING_CONFIRMATION without STALE_TIMEOUT
Check Telegram target topic for topic_2 message
Check topic_500 output contains 3 direct https URLs, prices, phones or phone-not-found markers
```

---

## 8. Git working tree hygiene

Server terminal output showed untracked files:

```text
data/db_backups/
data/project_templates/
data/templates/estimate/
docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_PART_008.md
```

Status:

```text
Not a runtime code regression
Not clean git tree
Must not commit runtime data blindly
```

Required:

```text
Review .gitignore for runtime/template/cache/db backup paths
Do not commit data/db_backups
Do not commit cache folders
Commit docs/SHARED_CONTEXT only if intentionally generated by context pipeline
```

---

## 9. Final factual conclusion

```text
GitHub history is visible.
Latest code push is visible.
Core worker services are active.
The confirmed worker crash regression is not currently visible after final restart.
The topic_2 Telegram thread routing patch is installed.
The topic_500 status/duplicate/stale guards are installed.
Full closure is not yet proven because TZ param lock, topic_500 context sanitizer, clean live search, internet-price estimate logic, and material clarification gate remain unverified or unimplemented.
```
