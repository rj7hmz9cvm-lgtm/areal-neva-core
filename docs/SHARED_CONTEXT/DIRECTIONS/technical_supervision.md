# direction: technical_supervision

GENERATED_AT: 2026-07-15T09:30:02.612057+00:00
GIT_SHA: e6ebd5c9f749698d4956e4eb26b1b474c11c4e3a
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

