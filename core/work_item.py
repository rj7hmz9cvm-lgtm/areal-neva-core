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
        extra = extra or {}
        raw_text = _str(extra.get("raw_text") or extra.get("raw_input") or _get(row, "raw_input", ""))
        input_type = _str(extra.get("input_type") or _get(row, "input_type", "unknown"), "unknown")
        topic_id = _int(extra.get("topic_id") if extra.get("topic_id") is not None else _get(row, "topic_id", 0), 0)
        wi = cls(
            work_id=_str(extra.get("work_id") or extra.get("task_id") or _get(row, "id", "")),
            chat_id=_str(extra.get("chat_id") or _get(row, "chat_id", "")),
            topic_id=topic_id,
            user_id=_str(extra.get("user_id") or _get(row, "user_id", "")) or None,
            message_id=_int(extra.get("message_id") or _get(row, "message_id", None), 0) or None,
            reply_to_message_id=_int(extra.get("reply_to_message_id") if extra.get("reply_to_message_id") is not None else _get(row, "reply_to_message_id", None), 0) or None,
            bot_message_id=_int(extra.get("bot_message_id") if extra.get("bot_message_id") is not None else _get(row, "bot_message_id", None), 0) or None,
            source_type=_str(extra.get("source_type") or "telegram"),
            input_type=input_type,
            raw_text=raw_text,
            state=_str(extra.get("state") or _get(row, "state", "NEW"), "NEW"),
            created_at=_str(extra.get("created_at") or _get(row, "created_at", "")) or None,
            updated_at=_str(extra.get("updated_at") or _get(row, "updated_at", "")) or None,
        )
        wi.formats_in = wi._detect_formats_in()
        wi.result = {"text": _str(_get(row, "result", ""))}
        err = _str(_get(row, "error_message", ""))
        if err:
            wi.errors.append({"code": "TASK_ERROR", "message": err, "fatal": False})
        wi.audit["created_by"] = "FULLFIX_DIRECTION_KERNEL_STAGE_1"
        return wi

    def _detect_formats_in(self):
        t = (self.input_type or "").lower()
        raw = (self.raw_text or "").lower()
        out = []
        if t in ("text","voice","photo","file","drive_file","url","mixed"): out.append(t)
        if ".pdf" in raw or "pdf" in t: out.append("pdf")
        if ".xlsx" in raw or ".xls" in raw: out.append("xlsx")
        if ".dwg" in raw: out.append("dwg")
        if t in ("photo","image"): out.append("photo")
        if not out: out.append("text")
        return list(dict.fromkeys(out))

    def set_direction(self, direction, profile=None):
        self.direction = direction
        self.direction_profile = profile or {}
        self.audit["direction"] = direction
        self.audit["direction_profile_id"] = self.direction_profile.get("id", direction)

    def set_intent(self, intent):
        self.intent = intent or "UNKNOWN"
        self.audit["intent"] = self.intent

    def add_audit(self, key, value):
        self.audit[str(key)] = value

    def add_error(self, code, message, fatal=False):
        self.errors.append({"code": str(code), "message": str(message), "fatal": bool(fatal)})

    def to_dict(self): return asdict(self)

    def to_payload(self):
        return {
            "id": self.work_id, "task_id": self.work_id,
            "chat_id": self.chat_id, "topic_id": self.topic_id,
            "user_id": self.user_id, "message_id": self.message_id,
            "reply_to_message_id": self.reply_to_message_id,
            "bot_message_id": self.bot_message_id,
            "source_type": self.source_type, "input_type": self.input_type,
            "raw_input": self.raw_text, "raw_text": self.raw_text,
            "state": self.state, "intent": self.intent,
            "direction": self.direction, "direction_profile": self.direction_profile,
            "formats_in": self.formats_in, "formats_out": self.formats_out,
            "attachments": self.attachments, "parsed_data": self.parsed_data,
            "context_refs": self.context_refs, "execution_plan": self.execution_plan,
            "quality_gates": self.quality_gates, "result": self.result,
            "audit": self.audit, "direction_audit": self.audit,
            "errors": self.errors, "metadata": self.metadata,
            "work_item": self.to_dict(),
        }
# === END FULLFIX_DIRECTION_KERNEL_STAGE_1_WORKITEM ===
