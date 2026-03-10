from executors.web_search import search_web

def run_sport(query):
    q = query.replace("[SPORT]", "").strip()

    queries = [
        q,
        q + " head to head",
        q + " last matches",
        q + " player stats",
        q + " goals cards lineups"
    ]

    collected = []
    seen = set()

    for item in queries:
        results = search_web(item, 6)
        for r in results:
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            url = r.get("url", "").strip()

            if not title and not body and not url:
                continue

            key = (title, url)
            if key in seen:
                continue

            seen.add(key)
            collected.append({
                "title": title,
                "body": body,
                "url": url
            })

    lines = []
    lines.append("СПОРТИВНЫЙ ОТЧЁТ")
    lines.append("")
    lines.append("Запрос:")
    lines.append(q)
    lines.append("")
    lines.append("Что найдено:")
    lines.append("— очные встречи")
    lines.append("— последние матчи")
    lines.append("— статистика игроков")
    lines.append("— голы и карточки")
    lines.append("")

    if not collected:
        lines.append("Источники не найдены")
        return "\n".join(lines)

    lines.append("Источники:")
    lines.append("")

    for i, s in enumerate(collected[:15], start=1):
        lines.append(f"{i}. {s.get('title', '')}")
        if s.get("body"):
            lines.append(s.get("body", ""))
        if s.get("url"):
            lines.append(s.get("url", ""))
        lines.append("")

    lines.append("Итог:")
    lines.append("Собраны открытые источники для анализа матча")

    return "\n".join(lines)
