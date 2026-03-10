from executors.web_search import search_web, format_sources

def run_crm(query):
    q = query.replace("[CRM]", "").strip()

    refs = search_web(q + " amoCRM sales pipeline automation", 6)

    lines = []
    lines.append("CRM-ОТЧЁТ")
    lines.append("")
    lines.append("Запрос:")
    lines.append(q)
    lines.append("")
    lines.append("Что делать:")
    lines.append("— квалифицировать клиента")
    lines.append("— определить следующий шаг")
    lines.append("— подготовить текст ответа")
    lines.append("— зафиксировать логику для amoCRM")
    lines.append("")
    lines.append("Черновик ответа:")
    lines.append("Добрый день. Зафиксировал вашу задачу. Для запуска работы нужен короткий созвон и уточнение исходных данных")
    lines.append("")
    lines.append("Полезные источники:")
    lines.append(format_sources(refs, 6))

    return "\n".join(lines)
