import os
from openpyxl import Workbook

def run_tables(query):
    q = query.replace("[TABLES]", "").strip()
    os.makedirs("outputs", exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Report"
    ws["A1"] = "TASK"
    ws["B1"] = q
    ws["A2"] = "STATUS"
    ws["B2"] = "OK"
    ws["A3"] = "NOTE"
    ws["B3"] = "Таблица создана автоматически"

    path = "outputs/result.xlsx"
    wb.save(path)

    lines = []
    lines.append("ТАБЛИЦЫ")
    lines.append("")
    lines.append("Задача:")
    lines.append(q)
    lines.append("")
    lines.append("Файл создан:")
    lines.append(path)
    return "\n".join(lines)
