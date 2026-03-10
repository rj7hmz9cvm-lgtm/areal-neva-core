from datetime import datetime
from executors.web_search import search_web

def run_sport(query):
    q = query.replace("[SPORT]", "").strip()

    sources = []
    sources.extend(search_web("хоккей " + q + " статистика очные встречи", 6))
    sources.extend(search_web("хоккей " + q + " последние матчи", 6))
    sources.extend(search_web("хоккей " + q + " игроки голы удаления", 6))

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
    lines.append("— голы и удаления")
    lines.append("")

    count = 0
    for s in sources[:12]:
        title = s.get("title", "")
        body = s.get("body", "")
        url = s.get("url", "")
        if not title and not body and not url:
            continue
        count += 1
        lines.append(f"{count}. {title}")
        if body:
            lines.append(body)
        if url:
            lines.append(url)
        lines.append("")

    lines.append("Итог:")
    lines.append("Собраны открытые источники для анализа матча")
    lines.append("Для полного betting-модуля позже подключаются sports APIs без смены архитектуры")

    return "\n".join(lines)
