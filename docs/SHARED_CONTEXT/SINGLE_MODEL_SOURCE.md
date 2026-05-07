# SINGLE_MODEL_SOURCE

GENERATED_AT: 2026-05-07T17:24:50.070946+00:00
GIT_SHA: 551829d5a33270fde4d9355e2dae407da05e6fb3
STATUS_RULE: INSTALLED != VERIFIED; VERIFIED только после live-test

## PRIORITY_OF_TRUTH
1. SAFE_RUNTIME_SNAPSHOT / live core.db
2. docs/HANDOFFS/LATEST_HANDOFF.md
3. docs/REPORTS/NOT_CLOSED.md
4. newest docs/HANDOFFS/*
5. newest chat_exports/*
6. locally synced Google Drive telegram_exports
7. docs/CANON_FINAL/*
8. git log last 14 days
9. code grep
10. UNKNOWN

## READ_ORDER
1. THIS FILE
2. TOPIC_STATUS_INDEX.md
3. DIRECTION_STATUS_INDEX.md
4. required TOPICS/topic_<id>_*.md or DIRECTIONS/<id>.md
5. SAFE_RUNTIME_SNAPSHOT.md
6. ORCHESTRA_FULL_CONTEXT_MANIFEST.json
7. PART files only if needed

## DRIVE_BINDING
DRIVE_UPLOAD_ENGINE: core/topic_drive_oauth.py
AUTH_ENV: GDRIVE_CLIENT_ID / GDRIVE_CLIENT_SECRET / GDRIVE_REFRESH_TOKEN
ROOT_ENV: DRIVE_INGEST_FOLDER_ID
PATH_PATTERN: chat_<chat_id>/topic_<topic_id>
TOPIC_5_SPECIAL: active_folder_override

## REFERENCE_REGISTRIES
estimate_template_registry: loaded=True templates_count=5
owner_reference_registry: loaded=True items=11
AREAL_REFERENCE_REPORT_SUMMARY: # AREAL_REFERENCE_FULL_MONOLITH_V1_REPORT

status: OK
version: AREAL_REFERENCE_FULL_MONOLITH_V1
updated_at: 2026-05-02T20:20:56.522887+00:00
estimate_files: 6
design_files: 231
technadzor_files: 1
for
estimate_templates_top5:
- M80 | М-80.xlsx | full_house_estimate_template
- M110 | М-110.xlsx | full_house_estimate_template
- ROOF_FLOORS | крыша и перекр.xlsx | roof_and_floor_estimate_template
- FOUNDATION_WAREHOUSE | фундамент_Склад2.xlsx | foundation_estimate_template
- AREAL_NEVA | Ареал Нева.xlsx | general_company_estimate_template

## DRIVE_CHAT_EXPORTS_STATUS
STATUS: SYNCED_LOCAL
- /root/.areal-neva-core/chat_exports files=66
- chat_exports files=66

## GLOBAL_TOPIC_TABLE
| topic_id | name | status | active | failed_24h |
|----------|------|--------|--------|------------|
| 0 | COMMON | UNKNOWN | 0 | 0 |
| 2 | STROYKA | INSTALLED_NOT_VERIFIED | 0 | 7 |
| 5 | TEKHNADZOR | IDLE_NO_FAILURES_NOT_VERIFIED | 0 | 0 |
| 11 | VIDEO | UNKNOWN | 0 | 0 |
| 210 | PROEKTIROVANIE | INSTALLED_NOT_VERIFIED | 0 | 5 |
| 500 | VEB_POISK | IDLE_NO_FAILURES_NOT_VERIFIED | 0 | 0 |
| 794 | DEVOPS | UNKNOWN | 0 | 0 |
| 961 | AVTOZAPCHASTI | UNKNOWN | 0 | 0 |
| 3008 | KODY_MOZGOV | UNKNOWN | 0 | 0 |
| 4569 | CRM_LEADS | UNKNOWN | 0 | 0 |
| 6104 | JOB_SEARCH | UNKNOWN | 0 | 0 |

## DIRECTION_TABLE
| direction_id | engine | enabled | topic_ids | quality_gates |
|--------------|--------|---------|-----------|---------------|
| general_chat | ai_router | True | [] | ['non_empty_answer'] |
| orchestration_core | ai_router | True | [3008] | ['canon_consistency'] |
| telegram_automation | telegram_pipeline | True | [] | ['reply_thread_required'] |
| memory_archive | context_search_archive_engine | True | [] | ['verified_sources_only'] |
| internet_search | search_supplier | True | [500] | ['sources_required'] |
| product_search | search_supplier | True | [] | ['price_required', 'source_required', 'tco_required'] |
| auto_parts_search | search_supplier | True | [961] | ['compatibility_required'] |
| construction_search | search_supplier | True | [] | ['price_required', 'delivery_required'] |
| technical_supervision | defect_act | True | [5] | ['defect_description_required', 'normative_section_required'] |
| estimates | estimate_unified | True | [2] | ['items_required', 'total_required', 'xlsx_required'] |
| defect_acts | defect_act | True | [] | ['document_required'] |
| documents | document_engine | True | [] | ['document_output_required'] |
| spreadsheets | sheets_route | True | [] | ['table_required'] |
| google_drive_storage | drive_storage | True | [] | ['drive_link_required'] |
| devops_server | ai_router | False | [794] | [] |
| vpn_network | ai_router | False | [] | [] |
| ocr_photo | ocr_engine | False | [] | [] |
| cad_dwg | dwg_engine | False | [] | [] |
| structural_design | project_engine | False | [210] | [] |
| roofing | estimate_unified | False | [] | [] |
| monolith_concrete | estimate_unified | False | [] | [] |
| crm_leads | ai_router | False | [4569] | [] |
| email_ingress | email_ingress | False | [] | [] |
| social_content | content_engine | False | [] | [] |
| video_production | video_production_agent | False | [11] | [] |
| photo_cleanup | photo_cleanup | False | [] | [] |
| isolated_project_ivan | ivan_project | False | [] | [] |
| job_search | search_engine | False | [6104] | [] |

## SOURCE_LINKS
- CURRENT_CONTEXT (quick start): docs/SHARED_CONTEXT/SINGLE_MODEL_CURRENT_CONTEXT.md
- FULL_CONTEXT (audit): docs/SHARED_CONTEXT/SINGLE_MODEL_FULL_CONTEXT.md
- TOPIC_STATUS_INDEX: docs/SHARED_CONTEXT/TOPIC_STATUS_INDEX.md
- DIRECTION_STATUS_INDEX: docs/SHARED_CONTEXT/DIRECTION_STATUS_INDEX.md
- LATEST_HANDOFF: docs/HANDOFFS/LATEST_HANDOFF.md
- NOT_CLOSED: docs/REPORTS/NOT_CLOSED.md
- SAFE_RUNTIME_SNAPSHOT: docs/SHARED_CONTEXT/SAFE_RUNTIME_SNAPSHOT.md
- MANIFEST: docs/SHARED_CONTEXT/ORCHESTRA_FULL_CONTEXT_MANIFEST.json
- DirectionRegistry: core/direction_registry.py

