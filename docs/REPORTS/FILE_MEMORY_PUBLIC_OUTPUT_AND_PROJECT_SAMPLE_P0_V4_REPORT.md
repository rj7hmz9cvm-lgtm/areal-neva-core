# FILE_MEMORY_PUBLIC_OUTPUT_AND_PROJECT_SAMPLE_P0_V4

generated_at: 2026-05-02T13:15:27+03:00

fixed:
- public sanitizer removes MANIFEST / DXF / XLSX / task_id / chat_id / topic_id / file_id / raw JSON
- escaped literal newlines are normalized before output
- file memory answer is domain-filtered and limited to max 3 items
- sample command does not return generic file list
- project sample command saves latest project/design file in same chat + topic
- final_closure memory query now triggers on проектные файлы / скидывал / загружал
- final_closure memory query delegates to clean file_memory_bridge output
- prehandle_task_context_v1 count remains 2
- telegram_daemon.py untouched
- no live Telegram runs performed

verification:
- SMOKE_SANITIZER_OK
- SMOKE_SAMPLE_COMMAND_NOT_FILE_LIST_OK
- SMOKE_PROJECT_FILE_LIST_CLEAN_OK
- SMOKE_PROJECT_SAMPLE_LOOKUP
- SMOKE_FINAL_CLOSURE_MEMORY_PUBLIC_OK
