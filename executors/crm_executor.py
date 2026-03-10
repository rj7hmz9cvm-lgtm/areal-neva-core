def run_crm(query):
    q = query.replace("[CRM]", "").strip()

    lines = []
    lines.append("CRM-ЗАДАЧА")
    lines.append("")
    lines.append("Запрос:")
    lines.append(q)
    lines.append("")
    lines.append("Что делать:")
    lines.append("— квалифицировать лид")
    lines.append("— определить следующий шаг")
    lines.append("— подготовить текст ответа")
    lines.append("— определить логику для amoCRM/бота")
    lines.append("")
    lines.append("Черновик ответа клиенту:")
    lines.append("Добрый день. Зафиксировал вашу задачу. Для запуска работы нужен короткий созвон и уточнение исходных данных")
    return "\n".join(lines)
