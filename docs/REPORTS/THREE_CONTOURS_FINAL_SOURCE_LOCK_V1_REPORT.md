# THREE_CONTOURS_FINAL_SOURCE_LOCK_V1_REPORT

STATUS: CODE_CLOSED_ALL_THREE_CONTOURS_BY_SOURCE_LOCK

Scope:
- topic_2 / smeta
- topic_210 / project + sketch
- topic_500 / web search isolation

Facts:
- Estimate templates source: Google Drive folder ESTIMATES/templates
- Project templates source: Google Drive folder Образцы проектов
- Sketch/design source: Google Drive folder PROJECT_DESIGN_REFERENCES when present
- Output folder PROJECT_ARTIFACTS is forbidden as source

Code changes:
- core/sample_template_engine.py:
  - topic_2 estimate intent no longer blocked by words фундамент / плита / кровля when smeta intent exists
  - active estimate template is force-synced from ESTIMATES/templates
  - old active template pointers are overwritten for topic_2
  - current raw_input is the only calculation source
  - old task results, old Drive links, old artifacts are forbidden
  - output XLSX starts with visible sheet Смета_текущее_задание
- core/project_engine.py:
  - project model sync reads Образцы проектов
  - sketch sync reads PROJECT_DESIGN_REFERENCES
  - project model is selected by requested section КЖ/КД/КМ/КМД/АР/ЭСКИЗ
  - PROJECT_ARTIFACTS is output-only
- task_worker.py:
  - topic_2 estimate template handler runs before file followup / old estimate fallback

Preserved:
- ESTIMATE_PRIORITY_FIX_V1
- SHEETS_NORMALIZE_V1
- CANON_LIST_QUERY_GUARD_V1
- FILE_TECH_CONTOUR_FOLLOWUP_V2 topic_500 isolation

Not touched:
- .env
- credentials
- sessions
- google_io.py
- memory.db schema
- core/ai_router.py
- telegram_daemon.py
- core/reply_sender.py
- systemd unit files

Verification:
- py_compile passed
- areal-task-worker restarted
- telegram-ingress active
- areal-memory-api active
- secret_scan passed
