from executors.web_search import search_web, format_sources

def run_content(query):
    q = query.replace("[CONTENT]", "").strip()

    examples = search_web(q + " examples ideas hooks", 6)
    trends = search_web(q + " trends social media", 6)

    lines = []
    lines.append("КОНТЕНТ-ПАКЕТ")
    lines.append("")
    lines.append("Тема:")
    lines.append(q)
    lines.append("")
    lines.append("Заголовок:")
    lines.append(q)
    lines.append("")
    lines.append("Короткий текст:")
    lines.append("Короткий экспертный пост по теме: " + q)
    lines.append("")
    lines.append("Длинный текст:")
    lines.append("Развёрнутый экспертный материал по теме: " + q + " с практической пользой и понятной подачей")
    lines.append("")
    lines.append("ТЗ на фото:")
    lines.append("— общий план")
    lines.append("— детали")
    lines.append("— проблемные зоны")
    lines.append("")
    lines.append("ТЗ на видео:")
    lines.append("— хук")
    lines.append("— основная мысль")
    lines.append("— демонстрация")
    lines.append("— вывод")
    lines.append("")
    lines.append("Примеры и тренды:")
    lines.append(format_sources(examples + trends, 8))

    return "\n".join(lines)
