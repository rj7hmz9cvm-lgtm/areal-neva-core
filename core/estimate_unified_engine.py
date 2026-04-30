# === FULLFIX_14_ESTIMATE_UNIFIED ===
import os, re, logging
logger = logging.getLogger(__name__)
ENGINE = "FULLFIX_14_ESTIMATE_UNIFIED"
RUNTIME_DIR = "/root/.areal-neva-core/runtime"
os.makedirs(RUNTIME_DIR, exist_ok=True)

def parse_estimate_rows(text):
    try:
        from core.sample_template_engine import parse_estimate_items
        rows = parse_estimate_items(text)
        if rows:
            return rows
    except Exception:
        pass
    rows = []
    pat = re.compile(
        r"([а-яёА-ЯЁa-zA-Z][а-яёА-ЯЁa-zA-Z0-9 \-/\.]+?)"
        r"\s+(\d+(?:[.,]\d+)?)\s*"
        r"(м²|м2|м³|м3|п\.м|м\.п|шт|кг|тн|т|компл\.?|л)\s*"
        r"(?:(?:цена|по|x|х)?\s*(\d+(?:[.,]\d+)?)(?:\s*руб)?)?",
        re.IGNORECASE
    )
    for m in pat.finditer(text):
        name = m.group(1).strip().rstrip(",:.")
        if len(name) < 2:
            continue
        qty = float(m.group(2).replace(",", "."))
        unit = m.group(3)
        price = float(m.group(4).replace(",", ".")) if m.group(4) else 0.0
        rows.append({"name": name, "qty": qty, "unit": unit, "price": price, "total": round(qty * price, 2)})
    return rows

def generate_xlsx(rows, task_id):
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    path = os.path.join(RUNTIME_DIR, "estimate_" + task_id[:8] + ".xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Смета"
    ws.merge_cells("A1:F1")
    ws["A1"] = "СМЕТА"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A1"].alignment = Alignment(horizontal="center")
    hdrs = ["№", "Наименование", "Ед.", "Кол-во", "Цена, руб.", "Сумма, руб."]
    for c, h in enumerate(hdrs, 1):
        cell = ws.cell(row=2, column=c, value=h)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="CCCCCC")
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["E"].width = 14
    ws.column_dimensions["F"].width = 14
    for i, row in enumerate(rows, 1):
        r = i + 2
        ws.cell(row=r, column=1, value=i)
        ws.cell(row=r, column=2, value=row["name"])
        ws.cell(row=r, column=3, value=row["unit"])
        ws.cell(row=r, column=4, value=row["qty"])
        ws.cell(row=r, column=5, value=row["price"])
        ws.cell(row=r, column=6, value="=D" + str(r) + "*E" + str(r))
    tr = len(rows) + 3
    ws.cell(row=tr, column=2, value="ИТОГО").font = Font(bold=True)
    ws.cell(row=tr, column=6, value="=SUM(F3:F" + str(tr - 1) + ")").font = Font(bold=True)
    wb.save(path)
    return path

def generate_pdf(rows, task_id):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    path = os.path.join(RUNTIME_DIR, "estimate_" + task_id[:8] + ".pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>СМЕТА</b>", ParagraphStyle("t", parent=styles["Heading1"], fontSize=16, alignment=1)),
        Spacer(1, 10)
    ]
    data = [["№", "Наименование", "Ед.", "Кол-во", "Цена", "Сумма"]]
    total = 0.0
    for i, row in enumerate(rows, 1):
        t = round(row["qty"] * row["price"], 2)
        total += t
        price_s = "%.2f" % row["price"]
        total_s = "%.2f" % t
        data.append([str(i), row["name"], row["unit"], str(row["qty"]), price_s, total_s])
    grand_s = "%.2f" % total
    data.append(["", "ИТОГО", "", "", "", grand_s])
    tbl = Table(data, colWidths=[25, 200, 35, 55, 65, 65])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#555555")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DDDDDD")),
    ]))
    story.append(tbl)
    doc.build(story)
    return path

def process_estimate_task_sync(conn, task_id, chat_id, topic_id, raw_input):
    from core.artifact_upload_guard import upload_many_or_fail
    from core.reply_sender import send_reply_ex
    try:
        rows = parse_estimate_rows(raw_input)
        if not rows:
            return False
        xlsx_path = generate_xlsx(rows, task_id)
        pdf_path = generate_pdf(rows, task_id)
        files = [{"path": xlsx_path, "kind": "estimate"}, {"path": pdf_path, "kind": "estimate_pdf"}]
        up = upload_many_or_fail(files, task_id, topic_id)
        total = sum(r["qty"] * r["price"] for r in rows)
        total_s = "%.2f" % total
        links = []
        for f in files:
            r = up["results"].get(f["path"], {})
            if r.get("success") and r.get("link"):
                links.append(r["link"])
        if links:
            result_text = "Смета готова. Позиций: " + str(len(rows)) + ". Итого: " + total_s + " руб.\n" + "\n".join(links)
        else:
            result_text = "Смета рассчитана. Позиций: " + str(len(rows)) + ". Итого: " + total_s + " руб. (Drive недоступен)"
        conn.execute(
            "UPDATE tasks SET state='AWAITING_CONFIRMATION',result=?,updated_at=datetime('now') WHERE id=?",
            (result_text, task_id)
        )
        conn.execute(
            "INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",
            (task_id, "state:AWAITING_CONFIRMATION")
        )
        conn.commit()
        try:
            _br = send_reply_ex(chat_id=str(chat_id), text=result_text, reply_to_message_id=None)
            _bmid = None
            if isinstance(_br, dict):
                _bmid = _br.get("bot_message_id") or _br.get("message_id")
            elif _br and hasattr(_br, "message_id"):
                _bmid = _br.message_id
            if _bmid:
                conn.execute("UPDATE tasks SET bot_message_id=? WHERE id=?", (str(_bmid), task_id))
                conn.commit()
        except Exception as _se:
            logger.error("ESTIMATE_SEND_ERR task=%s err=%s", task_id, _se)
        return True
    except Exception as e:
        logger.error("ESTIMATE_UNIFIED_ERROR task=%s err=%s", task_id, e)
        return False

async def process_estimate_task(conn, task_id, chat_id, topic_id, raw_input):
    import asyncio
    return await asyncio.get_event_loop().run_in_executor(
        None, process_estimate_task_sync, conn, task_id, chat_id, topic_id, raw_input
    )
# === END FULLFIX_14_ESTIMATE_UNIFIED ===
