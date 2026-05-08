# DIRECTION_STATUS_INDEX

GENERATED_AT: 2026-05-08T23:50:02.849764+00:00
GIT_SHA: 82535ed3c4087a2bbd99020991b7f03e1150fb1c
Source: core/direction_registry.DirectionRegistry from config/directions.yaml

| direction | enabled | engine | topic_ids | bound_status |
|-----------|---------|--------|-----------|--------------|
| general_chat | True | ai_router | [] | - |
| orchestration_core | True | ai_router | [3008] | 3008:UNKNOWN |
| telegram_automation | True | telegram_pipeline | [] | - |
| memory_archive | True | context_search_archive_engine | [] | - |
| internet_search | True | search_supplier | [500] | 500:IDLE_NO_FAILURES_NOT_VERIFIED |
| product_search | True | search_supplier | [] | - |
| auto_parts_search | True | search_supplier | [961] | 961:UNKNOWN |
| construction_search | True | search_supplier | [] | - |
| technical_supervision | True | defect_act | [5] | 5:IDLE_NO_FAILURES_NOT_VERIFIED |
| estimates | True | estimate_unified | [2] | 2:INSTALLED_NOT_VERIFIED |
| defect_acts | True | defect_act | [] | - |
| documents | True | document_engine | [] | - |
| spreadsheets | True | sheets_route | [] | - |
| google_drive_storage | True | drive_storage | [] | - |
| devops_server | False | ai_router | [794] | 794:UNKNOWN |
| vpn_network | False | ai_router | [] | - |
| ocr_photo | False | ocr_engine | [] | - |
| cad_dwg | False | dwg_engine | [] | - |
| structural_design | False | project_engine | [210] | 210:INSTALLED_NOT_VERIFIED |
| roofing | False | estimate_unified | [] | - |
| monolith_concrete | False | estimate_unified | [] | - |
| crm_leads | False | ai_router | [4569] | 4569:UNKNOWN |
| email_ingress | False | email_ingress | [] | - |
| social_content | False | content_engine | [] | - |
| video_production | False | video_production_agent | [11] | 11:UNKNOWN |
| photo_cleanup | False | photo_cleanup | [] | - |
| isolated_project_ivan | False | ivan_project | [] | - |
| job_search | False | search_engine | [6104] | 6104:UNKNOWN |

