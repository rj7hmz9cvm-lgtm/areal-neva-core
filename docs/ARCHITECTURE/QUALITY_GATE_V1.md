# QUALITY_GATE_V1 — Stage 4

## Назначение
Проверяет результат задачи по списку quality_gates из direction_profile.
Shadow mode: report пишется в payload["quality_gate_report"], не блокирует доставку.

## Типы gates
- Обязательные: non_empty_answer, items_required, total_required, xlsx_required, document_required, drive_link_required, sources_required, price_required, source_required, table_required, defect_description_required, reply_thread_required
- Advisory (не блокируют): tco_required, compatibility_required, delivery_required, normative_section_required, verified_sources_only, canon_consistency

## Результат
```json
{
  "overall": "pass|fail",
  "failed": ["gate1"],
  "advisory": ["gate2"],
  "gates": {"gate1": {"status": "pass|fail|error", "advisory": false}},
  "shadow_mode": true
}
```

## API
```python
from core.quality_gate import QualityGate, run_quality_gate
report = run_quality_gate(payload)
```

## Файл
core/quality_gate.py | FULLFIX_QUALITY_GATE_STAGE_4
