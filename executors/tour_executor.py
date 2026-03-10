from executors.web_search import search_web, format_sources

def run_tour(query):
    q = query.replace("[TOUR]", "").strip()

    refs = []
    refs += search_web(q + " route logistics", 5)
    refs += search_web(q + " hotels transport prices", 5)

    lines = []
    lines.append("ТУР-ПАКЕТ")
    lines.append("")
    lines.append("Запрос:")
    lines.append(q)
    lines.append("")
    lines.append("Что собрано:")
    lines.append("— маршрут")
    lines.append("— логистика")
    lines.append("— проживание")
    lines.append("— транспорт")
    lines.append("")
    lines.append("Источники:")
    lines.append(format_sources(refs, 10))

    return "\n".join(lines)
