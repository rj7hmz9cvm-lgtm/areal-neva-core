# === OUTPUT_DECISION_LOGIC_V1 ===
# Канон ORCHESTRA_MASTER_BLOCK: RESULT_VALIDATOR + RESULT_FORMAT_ENFORCER + HUMAN_DECISION_EDITOR
import logging
logger = logging.getLogger(__name__)

def format_search_output(offers: list, goal: str = "") -> str:
    """
    Жёсткий формат вывода поискового результата.
    Канон: таблица + выводы + что проверить звонком
    """
    if not offers:
        return "Предложения не найдены. Уточни запрос или расширь географию."

    # ранжируем
    try:
        from core.constraint_engine import rank_offers
        offers = rank_offers(offers)
    except Exception:
        pass

    lines = [f"Нашёл {len(offers)} вариант(ов) по запросу: {goal}\n"]
    lines.append("| Поставщик | Площадка | Цена | Наличие | Риск | Контакт |")
    lines.append("|---|---|---|---|---|---|")

    best_price = None
    best_reliable = None
    to_check = []

    for i, o in enumerate(offers[:10]):
        price = o.get("price") or "—"
        price_str = f"{int(price):,}".replace(",", " ") + " руб." if isinstance(price, (int, float)) and price > 0 else str(price)
        risk = o.get("risk", "UNVERIFIED")
        contact = "✅" if o.get("contact") or o.get("url") else "❌"
        lines.append(f"| {o.get('supplier','?')} | {o.get('platform','?')} | {price_str} | {o.get('stock','?')} | {risk} | {contact} |")

        if best_price is None and isinstance(price, (int, float)) and price > 0:
            best_price = o
        if risk == "CONFIRMED" and best_reliable is None:
            best_reliable = o
        if not o.get("contact"):
            to_check.append(o.get("supplier", "?"))

    # выводы
    lines.append("")
    if best_price:
        lines.append(f"💰 Самый дешёвый: {best_price.get('supplier')} — риск: {best_price.get('risk','?')}")
    if best_reliable:
        lines.append(f"✅ Наиболее надёжный: {best_reliable.get('supplier')}")
    if to_check:
        lines.append(f"📞 Проверить звонком: {', '.join(to_check[:3])}")

    return "\n".join(lines)

def format_task_result(result: str, state: str, error_code: str = "") -> str:
    """
    Ответ пользователю по state — канон §15
    """
    if state == "DONE":
        return result or "✅ Готово"
    if state == "FAILED":
        try:
            from core.error_explainer import user_friendly_error
            return f"❌ {user_friendly_error(error_code or 'UNKNOWN')}"
        except Exception:
            return f"❌ Не выполнено: {error_code}"
    if state == "WAITING_CLARIFICATION":
        return result or "Уточни запрос."
    if state == "AWAITING_CONFIRMATION":
        return (result or "") + "\n\nПодтверди (да) или укажи правки."
    return result or ""
# === END OUTPUT_DECISION_LOGIC_V1 ===
