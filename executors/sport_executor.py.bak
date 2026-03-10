from executors.web_search import search_web

def run_sport(query):
    q = query.replace("[SPORT]", "").strip()
    sources = search_web("хоккей " + q + " статистика матчи игроки голы удаления", 10)

    lines = []
    lines.append("СПОРТИВНЫЙ РАЗБОР")
    lines.append("")
    lines.append("Запрос:")
    lines.append(q)
    lines.append("")
    lines.append("Что собрано:")
    lines.append("— открытые источники по матчам")
    lines.append("— статистика игроков")
    lines.append("— голы и удаления")
    lines.append("— новости и аналитика")
    lines.append("")
    lines.append("Источники:")
    lines.append("")

    for s in sources[:10]:
        lines.append(s.get("title",""))
        if s.get("body"):
            lines.append(s.get("body",""))
        if s.get("url"):
            lines.append(s.get("url",""))
        lines.append("")

    lines.append("Итог:")
    lines.append("Найденные данные собраны. Следующий слой внешних API можно будет подключить позже без смены архитектуры")

    return "\n".join(lines)
