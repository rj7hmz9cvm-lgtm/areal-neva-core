# TNZ_MSK SKILL PACKAGE QA REPORT
Generated: 2026-05-05T08:14:06.363985+00:00

## Summary
| Metric | Count |
|--------|-------|
| Original skill cards | 324 |
| Kept after QA | 143 |
| Rejected | 181 |
| Needs owner review (kept) | 66 |
| Normative guard applied | 0 |

## Rejection Rate
181 / 324 = 55%

## Top Rejection Reasons
- noise_hard:в max: 53
- unknown_no_signal: 52
- noise_hard:стажировк: 39
- noise_hard:🤣🤣: 9
- noise_hard:всем привет.: 6
- noise_hard:подписчик: 3
- noise_hard:в мах: 3
- noise_hard:counter-strike: 1
- noise_hard:max': 1
- noise_hard:😃😃: 1
- noise_hard:добрых снов: 1
- noise_hard:геоподоснова: 1
- noise_hard:поправил ссылку: 1
- noise_hard:asmr от: 1
- noise_hard:ой чего нашёл тут в архиве: 1

## QA Rules Applied
1. Hard noise list: MAX/channel promo, jokes, salaries, chatter, unrelated topics
2. unknown category without positive document-composition signal → rejected
3. Category good + weak signal → kept with needs_owner_review=true
4. Normative guard: invented SP/GOST section points removed, marked as unconfirmed
5. No source_ref → always rejected (enforced upstream)

## Status
SKILL_PACKAGE_CLEANED_NOT_CANON
Owner approval required before promotion to technadzor_engine context.

## Output Files
- docs/TECHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL_CLEAN.md
- docs/TECHNADZOR/source_skills/tnz_msk/TECHNADZOR_DOCUMENT_COMPOSITION_SKILL_CLEAN.json
