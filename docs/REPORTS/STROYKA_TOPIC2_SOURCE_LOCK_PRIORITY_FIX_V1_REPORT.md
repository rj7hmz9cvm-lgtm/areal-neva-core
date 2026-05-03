# STROYKA_TOPIC2_SOURCE_LOCK_PRIORITY_FIX_V1_REPORT

STATUS: TOPIC2_STROYKA_SOURCE_LOCK_PRIORITY_INSTALLED

Facts fixed:
- topic_2 was still reaching FULL_STROYKA_ESTIMATE_CANON_CLOSE_V3
- topic_2 clarification values were recorded as task_history clarified:* but were not merged into raw_input before the next estimate pass
- search input_type estimate tasks were still able to bypass the template estimate path

Code changes:
- core/sample_template_engine.py: final topic_2 override for estimate intent
- core/sample_template_engine.py: search/text/voice accepted for topic_2 estimate template flow
- task_worker.py: priority hook merges clarified:* history into raw_input before stroyka processing
- task_worker.py: priority hook tries saved Drive template estimate path before stroyka fallback
- existing topic_500 guard preserved

Forbidden untouched:
- .env
- credentials
- sessions
- google_io.py
- memory.db schema
- core/ai_router.py
- telegram_daemon.py
- core/reply_sender.py
- systemd unit files
