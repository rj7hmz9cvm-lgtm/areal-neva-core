# DIRECTION_REGISTRY_V1

Канон Stage 1 реестра направлений AREAL-NEVA ORCHESTRA.

## Назначение

DirectionRegistry — детектор направления для каждого WorkItem. Берёт raw_text, topic_id, input_type, formats_in и возвращает один из 26 профилей направлений из config/directions.yaml.

## Источник правды

`config/directions.yaml` — формально YAML, фактически JSON (json.loads первым, yaml как fallback). 26 направлений, разделение active/passive по полю enabled.

## 26 направлений

### Active (13)
- general_chat — fallback общий чат
- orchestration_core — мозги оркестра, topic 3008
- telegram_automation — пайплайн Telegram
- memory_archive — память и архив
- internet_search — общий интернет-поиск, topic 500
- product_search — товарный поиск, strong_aliases avito/ozon/wb
- auto_parts_search — автозапчасти, strong_aliases drom/exist/emex
- construction_search — стройматериалы
- technical_supervision — технадзор, topic 2
- estimates — сметы, topic 2
- defect_acts — акты дефектов
- documents — DOCX
- spreadsheets — XLSX/Sheets
- google_drive_storage — загрузка на Drive

### Passive (13)
devops_server, vpn_network, ocr_photo, cad_dwg, structural_design, roofing, monolith_concrete, crm_leads, email_ingress, social_content, video_production, photo_cleanup, isolated_project_ivan

Passive направления получают penalty -80 в scoring.

## Scoring

| Сигнал | Вклад |
|---|---|
| strong_aliases hit | +200..+250 (overrides domain) |
| topic_id match | +70 + specificity bonus (max +10) |
| aliases | +30 each, max +120 |
| input_type match (если уже есть сигнал) | +15 |
| input_formats match (если уже есть сигнал) | +10 each, max +40 |
| search_signal (если requires_search и токен поиска в тексте) | +25 |
| passive penalty | -80 (capped at 0) |

Tie-break: score DESC → меньше topic_ids первым (более специфичный).

## Контракт API

```python
from core.direction_registry import DirectionRegistry, detect_direction

reg = DirectionRegistry()
profile = reg.detect(work_item)
# profile = {
#   "id": "estimates",
#   "title": "Сметы",
#   "enabled": True,
#   "score": 145,
#   "audit": [...],  # топ-10 кандидатов с reasons
#   ...все поля профиля из directions.yaml
# }
```

## Smoke тесты (приёмка)

- topic_500 + "найди avito ozon" → product_search
- topic_961 + "drom фара toyota hiace" → auto_parts_search
- topic_2 + "сделай смету" → estimates
- topic_2 + "технадзор дефект акт" → technical_supervision
- topic_3008 + "канон оркестра" → orchestration_core
- topic_0 + "привет как дела" → general_chat

Все 6 должны проходить и в pre-patch smoke, и в final smoke.

## Текущий статус

Stage 1 shadow mode: detect() вызывается через `_stage1_dir_payload()` в task_worker, направление пишется в payload, движки не используют его для маршрутизации. Capability Router (Stage 2) подключит direction к execution_plan.

## Расположение

- Код: `core/direction_registry.py`
- Конфиг: `config/directions.yaml`
- Маркер: `FULLFIX_DIRECTION_KERNEL_STAGE_1_DIRECTION_REGISTRY`
