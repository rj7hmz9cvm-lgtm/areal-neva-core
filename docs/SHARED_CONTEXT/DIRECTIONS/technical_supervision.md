# direction: technical_supervision

GENERATED_AT: 2026-07-30T15:35:02.707724+00:00
GIT_SHA: c25232f2f5b0288e438c4430ad589d6b5aa47262
GENERATED_FROM: core.direction_registry.DirectionRegistry

DIRECTION_ID: technical_supervision
TITLE: Технадзор
ENABLED: True
ENGINE: defect_act
REQUIRES_SEARCH: False
TOPIC_IDS: [5]
INPUT_TYPES: ['text', 'voice', 'photo', 'file']
INPUT_FORMATS: ['text', 'photo', 'pdf']
OUTPUT_FORMATS: ['telegram_text', 'docx', 'pdf']
QUALITY_GATES: ['defect_description_required', 'normative_section_required']
ALIASES: ['технадзор', 'наруш', 'дефект', 'осмотр', 'замечан', 'снип', 'гост']
STRONG_ALIASES: []

## BOUND_TOPICS_STATUS
- topic_5: UNKNOWN

