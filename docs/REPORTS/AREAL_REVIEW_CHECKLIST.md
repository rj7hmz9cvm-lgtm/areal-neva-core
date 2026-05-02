# AREAL_REVIEW_CHECKLIST

## Mandatory constraints

- no point patches
- no regression
- no new architecture layers
- no new Drive folder trees
- no duplicate hooks
- CANON_FINAL must not be ignored
- memory.db must receive slim reference data only
- indexer must not download files over 5MB
- topic_2, topic_5, topic_210 must not mix contexts

## Regression guards

- ESTIMATE_TEMPLATE_POLICY_CONTEXT_V4 remains in ai_router.py
- SAMPLE_ACCEPT_DIALOG_CONTEXT_FIX_V1 remains in final_closure_engine.py
- VOICE_CONFIRM_AWAITING_V1 remains only in task_worker.py
- CANON_FINAL absent from .gitignore

## Smoke

- owner reference context triggers on estimate/design/technadzor words
- owner reference context stays empty on neutral chat
- estimate template policy still works
- /archive returns 200
- upload retry service active
- media_group exists
- startup_recovery referenced
- pin_manager referenced

## Pending live-only checks

- topic isolation live Telegram check
- voice confirm live Telegram check
- duplicate guard live Telegram check
