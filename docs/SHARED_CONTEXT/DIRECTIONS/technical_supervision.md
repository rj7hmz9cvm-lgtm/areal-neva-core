# direction: technical_supervision

GENERATED_AT: 2026-07-08T00:30:02.409945+00:00
GIT_SHA: b034a10a23b0248d0540b1e9e9ae38296f1e088a
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
- topic_5: BROKEN

