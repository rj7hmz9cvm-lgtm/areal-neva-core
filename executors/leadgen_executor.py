from executors.web_search import search_web, format_sources

def run_leadgen(query):
    q = query.replace("[LEADGEN]", "").strip()

    tg = search_web(q + " Telegram", 5)
    av = search_web(q + " Avito", 5)
    pf = search_web(q + " Profi.ru", 5)

    lines = []
    lines.append("ЛИДОГЕНЕРАЦИЯ")
    lines.append("")
    lines.append("Запрос:")
    lines.append(q)
    lines.append("")
    lines.append("Telegram:")
    lines.append(format_sources(tg, 5))
    lines.append("")
    lines.append("Avito:")
    lines.append(format_sources(av, 5))
    lines.append("")
    lines.append("Profi.ru:")
    lines.append(format_sources(pf, 5))

    return "\n".join(lines)
