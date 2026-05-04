# NOT_CLOSED_20260504_ORCHESTRA_MASTER_CLOSE

Mode: FACT ONLY
Date: 2026-05-04
Source: current ChatGPT/server session, terminal outputs, GitHub main branch verification

---

## Confirmed closed in current session

```text
88c36e3 TOPIC2_REPLY_THREAD_FIX_V1
bf6cece TOPIC500_PRE_SEND_VALIDATOR_AND_STARTUP_RECOVERY_HARD_GUARD_V1
dc2f770 FINAL_TOPIC2_TOPIC5_TOPIC500_CLOSE_20260504_V1
```

Confirmed runtime state:

```text
areal-task-worker active
telegram-ingress active
areal-memory-api active
rowid 5214 topic_id=2   DONE
rowid 5215 topic_id=500 DONE
rowid 5216 topic_id=5   DONE
```

Closed facts:

```text
TOPIC2_REPLY_THREAD_FIX_V1 installed in core/sample_template_engine.py
send_reply_ex receives message_thread_id for topic_id > 0
_t2sp_send and _t2real_send pass topic_id
fallback Telegram API passes message_thread_id
TOPIC500 duplicate/stale/startup-recovery guards installed in task_worker.py
5214/5215/5216 current tasks closed in DB
context_aggregator.py restored after temporary deletion status
```

---

## P0 not closed / not proven

```text
1. TOPIC2_TZ_PARAM_LOCK_V1 not confirmed in current final code checks
2. wall_insulation_mm=250 not confirmed as separate field
3. roof_insulation_mm=300 not confirmed as separate field
4. distance_km=50 reflected in result, but raw_input absolute override block not confirmed
5. wall_type=каркас reflected in result, but strict raw_input lock block not confirmed
6. TOPIC500_CONTEXT_SANITIZER_V1 not confirmed in current ai_router.py
7. clean topic_500 live-test after patches not performed
8. topic_500 result quality not proven against a new request with direct URLs/phones/prices
9. topic_500 validator has markers, but no live proof that invalid result is blocked before Telegram send
10. server git working tree contained untracked runtime/data files
```

---

## P1 functional contour not closed

```text
1. Internet prices for topic_2 estimate not implemented/proven
2. Estimate currently uses template M-110.xlsx / generated assumptions, not confirmed live supplier prices per line
3. Price source labels not proven: LIVE_CONFIRMED / TEMPLATE_FALLBACK_PRICE / USER_ASSUMPTION
4. Material clarification gate not implemented/proven
5. System does not yet prove it asks for insulation type/brand/density when needed before final estimate
```

---

## Required next patch set

### Patch A — `core/sample_template_engine.py`

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

```text
Install TOPIC500_CONTEXT_SANITIZER_V1 on user_text before ONLINE_MODEL call
Remove old supplier tables from context
Remove Trust Score/TCO/НЕ ПОДТВЕРЖДЕНО/ЭТАП N fragments
Remove naked [1]/[2]/[3] source markers without URL
Ensure current user query remains intact
```

### Patch C — live verification after A/B

```text
Fresh topic_2 estimate request
Fresh topic_500 procurement search request
Check logs for Traceback/TypeError/SyntaxError
Check DB state for DONE/AWAITING_CONFIRMATION without STALE_TIMEOUT
Check Telegram target topic for topic_2 message
Check topic_500 output contains 3 direct https URLs, prices, phones or phone-not-found markers
```

---

## Canonical related file

```text
docs/HANDOFFS/HANDOFF_20260504_ORCHESTRA_MASTER_CLOSE.md
```
