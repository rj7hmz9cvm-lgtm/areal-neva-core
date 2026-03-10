import concurrent.futures
from executors.web_search import search_web
from executors.sport_executor import run_sport
from executors.content_executor import run_content
from executors.crm_executor import run_crm
from executors.leadgen_executor import run_leadgen
from executors.tour_executor import run_tour
from executors.cad_executor import run_cad
from executors.tables_executor import run_tables
from executors.pdf_mode_executor import run_pdf

def detect_mode(text):
    t = text.lower()

    if t.startswith("[sport]") or "хоккей" in t or "кхл" in t or "нхл" in t:
        return "SPORT"

    if t.startswith("[content]") or "instagram" in t or "youtube" in t or "telegram-канал" in t or "контент" in t:
        return "CONTENT"

    if t.startswith("[crm]") or "amocrm" in t or "лид" in t or "воронк" in t or "бот" in t:
        return "CRM"

    if t.startswith("[leadgen]") or "avito" in t or "авито" in t or "profi" in t or "заказ" in t or "заявк" in t:
        return "LEADGEN"

    if t.startswith("[tour]") or "тур" in t or "маршрут" in t or "байкал" in t or "камчат" in t:
        return "TOUR"

    if t.startswith("[pdf]") or "pdf" in t:
        return "PDF"

    if t.startswith("[cad]") or "dwg" in t or "dxf" in t or "autocad" in t or "чертеж" in t:
        return "CAD"

    if t.startswith("[tables]") or "excel" in t or "google sheets" in t or "таблиц" in t or "график" in t:
        return "TABLES"

    if t.startswith("[tech]") or "смет" in t or "техзаключ" in t or "отопл" in t or "сантех" in t or "проект" in t:
        return "TECH"

    return "SEARCH"

def run_parallel(funcs):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(fn) for fn in funcs]
        for f in futures:
            try:
                results.append(f.result())
            except Exception as e:
                results.append("ERROR\n\n" + str(e))
    return results

def execute(prompt):
    mode = detect_mode(prompt)

    if mode == "SPORT":
        results = run_parallel([
            lambda: run_sport(prompt),
            lambda: str(search_web("хоккей " + prompt, 6)),
            lambda: str(search_web("игроки " + prompt, 6)),
        ])
        return "\n\n".join(results)

    if mode == "CONTENT":
        results = run_parallel([
            lambda: run_content(prompt),
            lambda: str(search_web(prompt + " тренды", 5)),
            lambda: str(search_web(prompt + " примеры", 5)),
        ])
        return "\n\n".join(results)

    if mode == "CRM":
        results = run_parallel([
            lambda: run_crm(prompt),
            lambda: str(search_web(prompt + " amoCRM", 5)),
        ])
        return "\n\n".join(results)

    if mode == "LEADGEN":
        results = run_parallel([
            lambda: run_leadgen(prompt),
            lambda: str(search_web(prompt, 6)),
        ])
        return "\n\n".join(results)

    if mode == "TOUR":
        results = run_parallel([
            lambda: run_tour(prompt),
            lambda: str(search_web(prompt + " цены", 5)),
        ])
        return "\n\n".join(results)

    if mode == "PDF":
        return run_pdf(prompt)

    if mode == "CAD":
        return run_cad(prompt)

    if mode == "TABLES":
        return run_tables(prompt)

    if mode == "TECH":
        results = run_parallel([
            lambda: run_cad(prompt),
            lambda: run_pdf("ТЕХНИЧЕСКИЙ ОТЧЁТ\n\n" + prompt),
            lambda: run_tables(prompt),
            lambda: str(search_web(prompt + " нормы спецификация", 6)),
        ])
        return "\n\n".join(results)

    results = run_parallel([
        lambda: str(search_web(prompt, 8)),
        lambda: str(search_web(prompt + " новости", 5)),
        lambda: str(search_web(prompt + " аналитика", 5)),
    ])
    return "\n\n".join(results)
