# TNZ_MSK DOCUMENT SKILL EXTRACTION REPORT
Generated: 2026-05-05T07:49:28.101033+00:00

## Diagnostics
- Source: @tnz_msk — «Технадзор без Душнилова [Карабанов]»
- Session: authorized ✅
- Telethon: 1.43.2 ✅
- Mode: LIVE
- Sample limit: 1000

## Scan Statistics
| Metric | Count |
|--------|-------|
| Total messages fetched | 1000 |
| Skipped (empty) | 4 |
| Skipped (noise) | 25 |
| Detected documents | 170 |
| Detected links | 71 |

## Skill Extraction
| Metric | Count |
|--------|-------|
| Records passed to skill extractor | 971 |
| Skill cards extracted | 324 |
| Rejected (noise/no value) | 647 |
| Skill categories | 12 |
| Needs owner review | 183 |

## Skill Categories Extracted
- photo_to_defect_linking: 29 rules
- unknown: 148 rules
- client_facing_language: 17 rules
- defect_description_logic: 22 rules
- act_structure: 77 rules
- recommendation_logic: 3 rules
- normative_reference_handling: 14 rules
- conclusion_logic: 6 rules
- file_workflow: 1 rules
- rabota_poisk_reusable_pattern: 1 rules
- report_structure: 4 rules
- contractor_statement_handling: 2 rules

## Output Files
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.md`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL.json`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/SOURCE_INDEX.json`
- `data/memory_files/TEHNADZOR/source_skills/tnz_msk/LINKED_DOCUMENTS_INDEX.json`

## Rules
- No raw history saved to memory.db ✅
- No core.db tasks created ✅
- No forbidden files touched ✅
- Each extracted rule has source_ref ✅
- RABOTA_POISK reusable pattern documented ✅
