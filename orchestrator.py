import concurrent.futures
from executors.web_search import search_web, format_sources
from executors.sport_executor import run_sport
from executors.content_executor import run_content
from executors.crm_executor import run_crm
from executors.leadgen_executor import run_leadgen
from executors.tour_executor import run_tour
from executors.cad_executor import run_cad
from executors.tables_executor import run_tables
from executors.pdf_executor import create_pdf

def detect_mode(text):
    t = text.lower()

    if t.startswith("[sport]") or "хоккей" in t or "кхл" in t or "нхл" in t or "football" in t or "soccer" in t or "manchester united" in t or "liverpool" in t:
        return "SPORT"

    if t.startswith("[content]") or "instagram" in t or "youtube" in t or "telegram" in t or "контент" in t or "post" in t:
        return "CONTENT"

    if t.startswith("[crm]") or "amocrm" in t or "лид" in t or "воронк" in t or "бот" in t or "client" in t:
        return "CRM"

    if t.startswith("[leadgen]") or "avito" in t or "авито" in t or "profi" in t or "заказ" in t or "заявк" in t:
        return "LEADGEN"

    if t.startswith("[tour]") or "тур" in t or "маршрут" in t or "байкал" in t or "камчат" in t or "travel" in t:
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
        return run_sport(prompt)

    if mode == "CONTENT":
        return run_content(prompt)

    if mode == "CRM":
        return run_crm(prompt)

    if mode == "LEADGEN":
        return run_leadgen(prompt)

    if mode == "TOUR":
        return run_tour(prompt)

    if mode == "PDF":
        filename = create_pdf(prompt.replace("[PDF]", "").strip(), "pdf_task")
        return "PDF создан\n\n" + filename

    if mode == "CAD":
        return run_cad(prompt)

    if mode == "TABLES":
        return run_tables(prompt)

    if mode == "TECH":
        pdf_file = create_pdf("ТЕХНИЧЕСКИЙ ОТЧЁТ\n\n" + prompt, "tech_report")
        search_refs = search_web(prompt + " нормы спецификация", 8)
        parts = [
            "PDF создан\n\n" + pdf_file,
            run_cad(prompt),
            run_tables(prompt),
            "ИСТОЧНИКИ\n\n" + format_sources(search_refs, 8)
        ]
        return "\n\n".join(parts)

    refs = []
    refs += search_web(prompt, 5)
    refs += search_web(prompt + " новости", 5)
    refs += search_web(prompt + " аналитика", 5)

    return "ПОИСКОВЫЙ ОТЧЁТ\n\n" + format_sources(refs, 12)
