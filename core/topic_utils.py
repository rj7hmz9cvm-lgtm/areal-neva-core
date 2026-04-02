from __future__ import annotations
from typing import Optional

def extract_topic_id(event) -> Optional[int]:
    msg = getattr(event, "message", event)
    reply_to = getattr(msg, "reply_to", None)
    if reply_to is None:
        return None
    if getattr(reply_to, "forum_topic", False):
        return getattr(reply_to, "reply_to_msg_id", None)
    top_id = getattr(reply_to, "reply_to_top_id", None)
    if top_id:
        return top_id
    return None
