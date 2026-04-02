def classify_domain(text: str) -> str:
    low = (text or "").lower()
    if any(k in low for k in ["смет", "расцен", "объем", "объём", "материал", "работ"]):
        return "estimate"
    if any(k in low for k in ["снип", "гост", "сп ", "норма", "норматив"]):
        return "norms"
    if any(k in low for k in ["бетон", "фундамент", "арматур", "опалуб", "монолит", "строит"]):
        return "construction"
    return "default"
