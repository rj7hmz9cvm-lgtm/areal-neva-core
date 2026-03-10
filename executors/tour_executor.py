from executors.web_search import search_web

def run_tour(query):
    q = query.replace("[TOUR]", "").strip()
    sources = search_web(q + " маршрут логистика проживание транспорт", 8)

    lines = []
    lines.append("ТУР-ПАКЕТ")
    lines.append("")
    lines.append("Запрос:")
    lines.append(q)
    lines.append("")
    lines.append("Что собрано:")
    lines.append("— логистика")
    lines.append("— маршрут")
    lines.append("— проживание")
    lines.append("— транспорт")
    lines.append("")
    lines.append("Источники:")
    lines.append("")

    for s in sources:
        lines.append(s.get("title",""))
        if s.get("body"):
            lines.append(s.get("body",""))
        if s.get("url"):
            lines.append(s.get("url",""))
        lines.append("")

    return "\n".join(lines)
