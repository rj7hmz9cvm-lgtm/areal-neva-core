# === MODEL_ROUTER_V1 ===
def route_model(payload: dict):
    intent = str(payload.get("intent") or "").lower()
    input_type = str(payload.get("input_type") or "").lower()
    is_search = bool(payload.get("is_search"))
    if intent == "vision" or "photo" in input_type or "image" in input_type:
        return "google/gemini-2.5-flash"
    if is_search or intent == "search":
        return "perplexity/sonar"
    if intent in ("estimate", "project", "file", "dwg", "template") or input_type == "drive_file":
        return None
    return "deepseek/deepseek-chat"

def get_fallback_chain(model_id: str) -> list:
    # === FALLBACK_CHAIN_V1 ===
    return {
        "google/gemini-2.5-flash": ["mistralai/mistral-large", "deepseek/deepseek-chat"],
        "perplexity/sonar": ["deepseek/deepseek-chat"],
        "deepseek/deepseek-chat": ["mistralai/mistral-large"],
    }.get(model_id, ["deepseek/deepseek-chat"])
# === END MODEL_ROUTER_V1 ===
