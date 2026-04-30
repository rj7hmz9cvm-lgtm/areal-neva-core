# === MODEL_ROUTER_V1 === (расширен FULLFIX_23)
import os

# Доступные через OpenRouter без отдельных ключей
_MISTRAL = "mistralai/mistral-small-3.2-24b-instruct:free"
_CEREBRAS = "meta-llama/llama-4-scout:free"
_DEEPSEEK = "deepseek/deepseek-chat"
_GEMINI = "google/gemini-2.5-flash"
_PERPLEXITY = "perplexity/sonar"

def route_model(payload: dict):
    intent = str(payload.get("intent") or "").lower()
    input_type = str(payload.get("input_type") or "").lower()
    raw = str(payload.get("raw_input") or "").lower()
    is_search = bool(payload.get("is_search"))

    # vision / фото
    if intent == "vision" or "photo" in input_type or "image" in input_type:
        return _GEMINI

    # поиск → Perplexity
    if is_search or intent == "search":
        return _PERPLEXITY

    # файловые задачи → Python engine
    if intent in ("estimate", "project", "file", "dwg", "template") or input_type == "drive_file":
        return None

    # структурирование / нормализация → Mistral
    if intent in ("classify", "normalize", "structure") or any(
        w in raw for w in ["структурир", "нормализ", "классифик", "отсортир"]
    ):
        return _MISTRAL

    # быстрый reasoning → Cerebras (Llama)
    if intent == "reasoning" or any(
        w in raw for w in ["проверь логик", "есть ли ошибк", "найди противореч"]
    ):
        return _CEREBRAS

    # всё остальное → DeepSeek
    return _DEEPSEEK

def get_fallback_chain(model_id: str) -> list:
    # === FALLBACK_CHAIN_V1 ===
    return {
        _GEMINI:     [_MISTRAL, _DEEPSEEK],
        _PERPLEXITY: [_DEEPSEEK],
        _DEEPSEEK:   [_MISTRAL, _CEREBRAS],
        _MISTRAL:    [_DEEPSEEK],
        _CEREBRAS:   [_DEEPSEEK],
    }.get(model_id, [_DEEPSEEK])

def get_model_registry() -> dict:
    # === MODEL_REGISTRY_V1 ===
    return {
        "gemini":     {"model": _GEMINI,     "type": "vision",     "via": "openrouter"},
        "perplexity": {"model": _PERPLEXITY, "type": "search",     "via": "openrouter"},
        "deepseek":   {"model": _DEEPSEEK,   "type": "final",      "via": "openrouter"},
        "mistral":    {"model": _MISTRAL,    "type": "structure",  "via": "openrouter"},
        "cerebras":   {"model": _CEREBRAS,   "type": "reasoning",  "via": "openrouter"},
    }
# === END MODEL_ROUTER_V1 ===
