from executors.web_search import search_web, format_sources

def run_sport(query):
    q = query.replace("[SPORT]", "").strip()

    results = []
    results += search_web(q + " head to head statistics", 5)
    results += search_web(q + " last matches", 5)
    results += search_web(q + " players goals cards injuries", 5)

    seen = set()
    unique = []
    for r in results:
        key = (r.get("title", ""), r.get("url", ""))
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    lines = []
    lines.append("СПОРТИВНЫЙ ОТЧЁТ")
    lines.append("")
    lines.append("Запрос:")
    lines.append(q)
    lines.append("")
    lines.append("Разделы:")
    lines.append("— очные встречи")
    lines.append("— последние матчи")
    lines.append("— игроки и статистика")
    lines.append("— голы, карточки, травмы")
    lines.append("")
    lines.append("Источники:")
    lines.append(format_sources(unique, 12))
    lines.append("")
    lines.append("Итог:")
    lines.append("Собраны открытые источники для полного спортивного разбора")

    return "\n".join(lines)
