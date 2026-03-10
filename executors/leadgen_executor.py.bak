from executors.web_search import search_web

def run_leadgen(query):
    q = query.replace("[LEADGEN]", "").strip()
    sources = []
    sources.extend(search_web(q + " Telegram", 5))
    sources.extend(search_web(q + " Avito", 5))
    sources.extend(search_web(q + " Profi.ru", 5))

    lines = []
    lines.append("ЛИДОГЕНЕРАЦИЯ")
    lines.append("")
    lines.append("Запрос:")
    lines.append(q)
    lines.append("")
    lines.append("Найденные источники:")
    lines.append("")

    for s in sources[:15]:
        lines.append(s.get("title",""))
        if s.get("body"):
            lines.append(s.get("body",""))
        if s.get("url"):
            lines.append(s.get("url",""))
        lines.append("")

    return "\n".join(lines)
