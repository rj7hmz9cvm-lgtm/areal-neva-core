# WORKITEM_V1 — PROPOSAL CODE

Файл назначения: core/work_item.py
Статус: NOT INSTALLED

```python
# === FULLFIX_DIRECTION_KERNEL_STAGE_1_WORKITEM ===
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


def _get(row, key, default=None):
    if row is None: return default
    if isinstance(row, dict): return row.get(key, default)
    try: return row[key]
    except Exception: return getattr(row, key, default)


def _int(v, d=0):
    try:
        if v is None or v == "": return d
        return int(v)
    except Exception: return d


def _str(v, d=""):
    if v is None: return d
    return str(v)


@dataclass
class WorkItem:
    work_id: str
    chat_id: str
    topic_id: int
    user_id: Optional[str] = None
    message_id: Optional[int] = None
    reply_to_message_id: Optional[int] = None
    bot_message_id: Optional[int] = None
    source_type: str = "telegram"
    input_type: str = "unknown"
    raw_text: str = ""
    state: str = "NEW"
    intent: str = "UNKNOWN"
    direction: Optional[str] = None
    direction_profile: Dict[str, Any] = field(default_factory=dict)
    formats_in: List[str] = field(default_factory=list)
    formats_out: List[str] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    context_refs: Dict[str, Any] = field(default_factory=dict)
    execution_plan: List[Dict[str, Any]] = field(default_factory=list)
    quality_gates: List[str] = field(default_factory=list)
    result: Dict[str, Any] = field(default_factory=dict)
    audit: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_task_row(cls, row, extra=None):
        # см. полный код в STAGE_1_INSTALL_BLOCK.md
        pass
```

Полная версия с smoke tests в STAGE_1_INSTALL_BLOCK.md
