# DIRECTION_REGISTRY_V1 — PROPOSAL CODE

Файлы назначения:
- core/direction_registry.py
- config/directions.yaml

Статус: NOT INSTALLED

## SCORING ALGORITHM

```python
# strong_aliases overrides domain
strong_hits = [a for a in profile.get("strong_aliases",[]) if a.lower() in raw]
if strong_hits:
    score += min(250, 200 + 25 * (len(strong_hits) - 1))

# topic + specificity
if topic_id in profile.get("topic_ids", []):
    score += 70 + max(0, 10 - len(topic_ids))

# aliases capped at 120
alias_hits = [a for a in profile.get("aliases",[]) if a.lower() in raw]
if alias_hits:
    score += min(120, 30 * len(alias_hits))

# bonuses only if other signal present
any_signal = bool(strong_hits or topic_match or alias_hits)
if any_signal:
    # input_type +15, format +10..40, search +25
    pass

# passive penalty
if not profile.get("enabled"):
    score = max(0, score - 80)
```

Полный код установки в STAGE_1_INSTALL_BLOCK.md
