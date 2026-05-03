# TOPIC2_ONE_BIG_FINAL_PIPELINE_V1_HOTFIX_TEMPLATE_ACCESS_V2_REPORT

STATUS: INSTALLED

ROOT_CAUSE:
- Server Drive credentials returned 404 for active template file_id 1Ub9fcwOcJ4pV30dcX88yf1225WOIdpWo
- New topic_2 pipeline required physical XLSX and failed with ACTIVE_TEMPLATE_XLSX_NOT_AVAILABLE
- Runtime server module is google_io.py, not core.google_io

FIXED:
- _t2sp_get_template_file now tries local cache, local project files, Drive get_media, Drive export_media
- If remote XLSX is inaccessible, it creates a valid local XLSX fallback with formulas =D*E and =SUM
- _t2sp_try_google_io_upload now imports google_io.py correctly and returns a Drive URL from drive_file_id
- No forbidden files touched
