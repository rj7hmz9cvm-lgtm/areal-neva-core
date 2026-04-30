# === FULLFIX_15_ESTIMATE_UNIFIED ===
import os, re, logging
logger = logging.getLogger(__name__)
ENGINE = "FULLFIX_15_ESTIMATE_UNIFIED"
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
    # Fallback simple parser: "name qty unit price"
    try:
        import re as _re
        simple_pat = _re.compile(
            r"([а-яёА-ЯЁa-zA-Z][а-яёА-ЯЁa-zA-Z0-9 \-/\.]{1,50}?)"
            r"\s+(\d+(?:[.,]\d+)?)\s*"
            r"(м²|м2|м³|м3|п\.м|м\.п|шт|кг|тн|т|компл|л)\s*"
            r"(?:(?:цена|по|x|х|@)?\s*(\d+(?:[.,]\d+)?)(?:\s*руб(?:\.)?)?)?",
            _re.IGNORECASE | _re.UNICODE
        )
        for m in simple_pat.finditer(text):
            name = m.group(1).strip().rstrip(",:. ")
            if len(name) < 2 or name.lower() in ("сделай","смету","смета","итого","всего"):
                continue
            qty = float(m.group(2).replace(",", "."))
            unit = m.group(3)
            price = float(m.group(4).replace(",", ".")) if m.group(4) else 0.0
            rows.append({"name": name, "qty": qty, "unit": unit, "price": price, "total": round(qty*price, 2)})
        if rows:
            return rows
    except Exception:
        pass
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
        rows.append({"name": name, "qty": qty, "unit": unit, "price": price, "total": round(qty*price, 2)})
    return rows

def _strip_manifest(text):
    lines = []
    for line in (text or "").splitlines():
        low = line.lower()
        if ("manifest" in low) and ("drive.google" in low or "docs.google" in low):
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def generate_xlsx(rows, task_id):
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    path = os.path.join(RUNTIME_DIR, "estimate_" + task_id[:8] + ".xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Смета"
    ws.merge_cells("A1:F1")
    ws["A1"] = "СМЕТА"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 22
    thin = Border(left=Side(style="thin"), right=Side(style="thin"),
                  top=Side(style="thin"), bottom=Side(style="thin"))
    hdrs = ["№", "Наименование", "Ед.", "Кол-во", "Цена, руб.", "Сумма, руб."]
    for c, h in enumerate(hdrs, 1):
        cell = ws.cell(row=2, column=c, value=h)
        cell.font = Font(bold=True, size=10)
        cell.fill = PatternFill("solid", fgColor="CCCCCC")
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
        cell.border = thin
    ws.column_dimensions["A"].width = 5
    ws.column_dimensions["B"].width = 42
    ws.column_dimensions["C"].width = 8
    ws.column_dimensions["D"].width = 10
    ws.column_dimensions["E"].width = 15
    ws.column_dimensions["F"].width = 15
    ws.freeze_panes = "A3"
    ws.auto_filter.ref = "A2:F2"
    for i, row in enumerate(rows, 1):
        r = i + 2
        ws.cell(row=r, column=1, value=i).border = thin
        nc = ws.cell(row=r, column=2, value=row["name"])
        nc.alignment = Alignment(wrap_text=True)
        nc.border = thin
        ws.cell(row=r, column=3, value=row["unit"]).border = thin
        ws.cell(row=r, column=4, value=row["qty"]).border = thin
        ws.cell(row=r, column=5, value=row["price"]).border = thin
        fc = ws.cell(row=r, column=6, value="=D" + str(r) + "*E" + str(r))
        fc.border = thin
    tr = len(rows) + 3
    tc = ws.cell(row=tr, column=2, value="ИТОГО")
    tc.font = Font(bold=True)
    tc.border = thin
    sc = ws.cell(row=tr, column=6, value="=SUM(F3:F" + str(tr-1) + ")")
    sc.font = Font(bold=True)
    sc.fill = PatternFill("solid", fgColor="FFFFCC")
    sc.border = thin
    wb.save(path)
    return path

def generate_pdf(rows, task_id):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
    from reportlab.lib import colors
    from core.pdf_cyrillic import register_cyrillic_fonts, make_styles, make_paragraph, clean_pdf_text, FONT_REGULAR, FONT_BOLD
    path = os.path.join(RUNTIME_DIR, "estimate_" + task_id[:8] + ".pdf")
    register_cyrillic_fonts()
    styles = make_styles()
    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=20, bottomMargin=20, leftMargin=20, rightMargin=20)
    story = [make_paragraph("СМЕТА", "header", styles), Spacer(1, 8)]
    hdr_row = [make_paragraph(h, "bold", styles) for h in ["№", "Наименование", "Ед.", "Кол-во", "Цена, руб.", "Сумма, руб."]]
    data = [hdr_row]
    total = 0.0
    for i, row in enumerate(rows, 1):
        t = round(row["qty"] * row["price"], 2)
        total += t
        data.append([
            make_paragraph(str(i), "normal", styles),
            make_paragraph(clean_pdf_text(row["name"]), "normal", styles),
            make_paragraph(row["unit"], "normal", styles),
            make_paragraph(str(row["qty"]), "normal", styles),
            make_paragraph("%.2f" % row["price"], "normal", styles),
            make_paragraph("%.2f" % t, "normal", styles),
        ])
    data.append([
        make_paragraph("", "normal", styles),
        make_paragraph("ИТОГО", "bold", styles),
        make_paragraph("", "normal", styles),
        make_paragraph("", "normal", styles),
        make_paragraph("", "normal", styles),
        make_paragraph("%.2f" % total, "bold", styles),
    ])
    tbl = Table(data, colWidths=[22, 190, 32, 52, 70, 70])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#444444")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), FONT_BOLD),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.4, colors.black),
        ("FONTNAME", (0,-1), (-1,-1), FONT_BOLD),
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#FFFFCC")),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [colors.white, colors.HexColor("#F7F7F7")]),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
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
        files = [{"path": pdf_path, "kind": "estimate_pdf"}, {"path": xlsx_path, "kind": "estimate"}]
        up = upload_many_or_fail(files, task_id, topic_id)
        total = sum(r["qty"] * r["price"] for r in rows)
        total_s = "%.2f" % total
        pdf_r = up["results"].get(pdf_path, {})
        xlsx_r = up["results"].get(xlsx_path, {})
        pdf_ok = pdf_r.get("success") and pdf_r.get("link")
        xlsx_ok = xlsx_r.get("success") and xlsx_r.get("link")
        if pdf_ok and xlsx_ok:
            result_text = "Смета готова.\nПозиций: " + str(len(rows)) + ". Итого: " + total_s + " руб.\nPDF: " + pdf_r["link"] + "\nXLSX: " + xlsx_r["link"]
            state = "AWAITING_CONFIRMATION"
        elif xlsx_ok:
            result_text = "Смета готова (PDF не загружен).\nПозиций: " + str(len(rows)) + ". Итого: " + total_s + " руб.\nXLSX: " + xlsx_r["link"]
            state = "AWAITING_CONFIRMATION"
        elif pdf_ok:
            result_text = "Смета готова (XLSX не загружен).\nПозиций: " + str(len(rows)) + ". Итого: " + total_s + " руб.\nPDF: " + pdf_r["link"]
            state = "AWAITING_CONFIRMATION"
        else:
            result_text = "Смета рассчитана, но загрузка файлов в Drive не выполнена. Позиций: " + str(len(rows)) + ". Итого: " + total_s + " руб."
            state = "FAILED"
            logger.error("ESTIMATE_UPLOAD_FAIL task=%s pdf_err=%s xlsx_err=%s", task_id, pdf_r.get("tried"), xlsx_r.get("tried"))
        result_text = _strip_manifest(result_text)
        conn.execute("UPDATE tasks SET state=?,result=?,updated_at=datetime('now') WHERE id=?", (state, result_text, task_id))
        conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))", (task_id, "state:" + state))
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
# === END FULLFIX_15_ESTIMATE_UNIFIED ===
