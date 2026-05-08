#!/usr/bin/env python3
# TOPIC2_DRAINAGE_MULTIFILE_REPAIR_CLOSE_V1
from __future__ import annotations

import asyncio
import glob
import inspect
import re
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

BASE = Path("/root/.areal-neva-core")
DB = BASE / "data" / "core.db"
OUT_DIR = BASE / "runtime" / "stroyka_estimates" / "drainage_repair"
TASK_ID = "043e5c9f-e8bc-434c-9dad-a66c7e50f917"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DRAINAGE_MARKERS = [
    "НВД", "наружные водостоки", "дренаж", "дренажи", "ливневая", "ДНС", "Дк", "Лк",
    "пескоуловитель", "линейный водоотвод", "d=160", "i=0,005", "колодец",
]

GEO_MARKERS = [
    "глубина", "отметка", "грунтовых вод", "инженерно-геологические", "скважин",
    "промерзания", "супесь", "насыпные грунты",
]


def s(v: Any) -> str:
    return "" if v is None else str(v)


def pdf_text(path: Path) -> str:
    try:
        r = subprocess.run(
            ["pdftotext", "-layout", "-q", str(path), "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=25,
        )
        return r.stdout or ""
    except Exception as e:
        return f"PDFTOTEXT_ERR={e}"


def find_recent_pdfs() -> List[Path]:
    candidates: List[Path] = []
    for pattern in [
        "/var/lib/telegram-bot-api/*/documents/*.pdf",
        "/root/.areal-neva-core/runtime/**/*.pdf",
    ]:
        for raw in glob.glob(pattern, recursive=True):
            p = Path(raw)
            try:
                if p.is_file():
                    candidates.append(p)
            except Exception:
                pass
    candidates = sorted(set(candidates), key=lambda p: p.stat().st_mtime, reverse=True)
    recent = []
    now = datetime.now().timestamp()
    for p in candidates:
        try:
            if now - p.stat().st_mtime <= 8 * 3600:
                recent.append(p)
        except Exception:
            pass
    return recent[:12]


def classify_pdf(path: Path, text: str) -> str:
    low = text.lower().replace("ё", "е")
    name = path.name.lower().replace("ё", "е")
    if any(m.lower().replace("ё", "е") in low for m in DRAINAGE_MARKERS) or "дренаж" in name:
        return "drainage_scheme"
    if any(m.lower().replace("ё", "е") in low for m in GEO_MARKERS) or "отчет" in name or "отчёт" in name:
        return "geology_report"
    return "other_pdf"


def num(x: str) -> float:
    return float(x.replace(",", "."))


def extract_lengths(text: str) -> List[float]:
    vals: List[float] = []
    patterns = [
        r"(?i)\bl\s*=\s*(\d+(?:[,.]\d+)?)\s*м\b",
        r"(?i)\bl\s*[-–]\s*(\d+(?:[,.]\d+)?)\s*м\b",
        r"(?i)длина\s*[-:=]?\s*(\d+(?:[,.]\d+)?)\s*м\b",
        r"(?i)(\d+(?:[,.]\d+)?)\s*(?:п\.?\s*м|м\.?\s*п)\b",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text):
            try:
                v = num(m.group(1))
                if 0.5 <= v <= 500:
                    vals.append(round(v, 2))
            except Exception:
                pass
    out: List[float] = []
    for v in vals:
        if v not in out:
            out.append(v)
    return out


def extract_depths(text: str) -> List[float]:
    vals = []
    for pat in [
        r"(?i)глубин[а-я]*\s*(?:до|от)?\s*(\d+(?:[,.]\d+)?)\s*м",
        r"(?i)на глубине\s*(\d+(?:[,.]\d+)?)\s*м",
    ]:
        for m in re.finditer(pat, text):
            try:
                v = num(m.group(1))
                if 0.2 <= v <= 12:
                    vals.append(round(v, 2))
            except Exception:
                pass
    out = []
    for v in vals:
        if v not in out:
            out.append(v)
    return out


def count_unique(text: str, prefix: str) -> int:
    return len(set(re.findall(rf"{re.escape(prefix)}\s*[-–]?\s*(\d+)", text, flags=re.I)))


def has(text: str, marker: str) -> bool:
    return marker.lower().replace("ё", "е") in text.lower().replace("ё", "е")


def history(conn: sqlite3.Connection, task_id: str, action: str) -> None:
    conn.execute(
        "INSERT INTO task_history (task_id, action, created_at) VALUES (?,?,datetime('now'))",
        (task_id, action[:900]),
    )


def build_items(total_len: float, avg_depth: float, wells_d: int, wells_l: int,
                has_dns: bool, has_pu: bool, source_note: str) -> List[Dict[str, Any]]:
    if total_len <= 0:
        total_len = 6.0

    excavation_m3 = round(total_len * avg_depth * 0.6, 2)
    sand_m3 = round(total_len * 0.12, 2)
    gravel_m3 = round(total_len * 0.35, 2)
    geotextile_m2 = round(total_len * 1.8, 2)

    rows = [
        ("Подготовительные и земляные работы", "Разметка трасс дренажа/ливневки", "м.п.", total_len, 450, 0),
        ("Подготовительные и земляные работы", "Разработка траншей", "м³", excavation_m3, 1900, 0),
        ("Подготовительные и земляные работы", "Вывоз/перемещение лишнего грунта", "м³", round(excavation_m3 * 0.35, 2), 1400, 0),
        ("Геотекстиль / щебень / песок", "Геотекстиль в траншее", "м²", geotextile_m2, 180, 95),
        ("Геотекстиль / щебень / песок", "Песчаная подготовка", "м³", sand_m3, 1300, 1700),
        ("Геотекстиль / щебень / песок", "Щебёночный фильтр", "м³", gravel_m3, 1600, 3200),
        ("Дренажные трубы и обратный фильтр", "Труба дренажная/водоотводящая d=160", "м.п.", total_len, 850, 1250),
        ("Дренажные трубы и обратный фильтр", "Укладка трубы с уклоном i=0,005", "м.п.", total_len, 950, 0),
    ]
    if wells_d:
        rows.append(("Колодцы и дождеприёмники", "Дренажный ревизионный колодец Дк", "шт", wells_d, 6500, 18000))
    if wells_l:
        rows.append(("Колодцы и дождеприёмники", "Ливневый ревизионный колодец Лк", "шт", wells_l, 6500, 16000))
    if has_dns:
        rows.append(("ДНС / насосное оборудование", "Дренажная насосная станция ДНС-1", "компл", 1, 28000, 145000))
    if has_pu:
        rows.append(("Пескоуловители / линейный водоотвод", "Пескоуловитель ПУ-1", "шт", 1, 6500, 22000))
    rows.extend([
        ("Ливневая канализация", "Линейный водоотвод / лотки", "м.п.", max(round(total_len * 0.2, 2), 1), 1100, 2600),
        ("Монтажные работы", "Сборка узлов, подключение колодцев и выпусков", "компл", 1, 45000, 0),
        ("Логистика", "Доставка материалов и инструмента", "рейс", 2, 0, 18000),
    ])

    out = []
    for i, (section, name, unit, qty, work, mat) in enumerate(rows, 1):
        qty = float(qty); work = float(work); mat = float(mat)
        out.append({
            "№": i, "Раздел": section, "Наименование": name, "Ед изм": unit,
            "Кол-во": qty, "Цена работ": work, "Стоимость работ": round(qty * work, 2),
            "Цена материалов": mat, "Стоимость материалов": round(qty * mat, 2),
            "Всего": round(qty * (work + mat), 2),
            "Источник цены": "MANUAL_HIGH_SEGMENT_BY_USER",
            "Поставщик": "ручной высокий сегмент по запросу пользователя",
            "URL": "—", "checked_at": datetime.now().strftime("%Y-%m-%d"),
            "Примечание": source_note,
        })
    return out


def create_xlsx(path: Path, items: List[Dict[str, Any]], meta: Dict[str, Any]) -> Dict[str, float]:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    headers = ["№","Раздел","Наименование","Ед изм","Кол-во","Цена работ","Стоимость работ",
               "Цена материалов","Стоимость материалов","Всего","Источник цены","Поставщик","URL","checked_at","Примечание"]
    wb = Workbook(); ws = wb.active; ws.title = "DRAINAGE_CALC"
    ws["A1"] = "Смета: дренаж / ливневая канализация / наружные сети"
    ws["A2"] = f"Исходные файлы: {', '.join(meta['file_names'])}"
    ws["A3"] = f"Длина по read-back: {meta['total_len']} м; глубина: {meta['avg_depth']} м; статус: {meta['length_status']}"
    ws["A4"] = "Цены: высокий ценовой сегмент по голосовому ТЗ пользователя; без фиктивных интернет-источников"
    for r in range(1, 5):
        ws.cell(r, 1).font = Font(bold=True)
    start = 6
    for c, h in enumerate(headers, 1):
        cell = ws.cell(start, c, h)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9EAF7")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for r, item in enumerate(items, start + 1):
        for c, h in enumerate(headers, 1):
            ws.cell(r, c, item[h])
        ws.cell(r, 7, f"=E{r}*F{r}"); ws.cell(r, 9, f"=E{r}*H{r}"); ws.cell(r, 10, f"=G{r}+I{r}")
    last = start + len(items)
    tr = last + 2; vr = tr + 1; gr = vr + 1
    ws.cell(tr, 2, "ИТОГО без НДС"); ws.cell(tr, 7, f"=SUM(G{start+1}:G{last})")
    ws.cell(tr, 9, f"=SUM(I{start+1}:I{last})"); ws.cell(tr, 10, f"=SUM(J{start+1}:J{last})")
    ws.cell(vr, 2, "НДС 20%"); ws.cell(vr, 10, f"=J{tr}*0.2")
    ws.cell(gr, 2, "ИТОГО с НДС"); ws.cell(gr, 10, f"=J{tr}+J{vr}")
    for r in (tr, vr, gr):
        for c in range(1, 16):
            ws.cell(r, c).font = Font(bold=True)
    for i, w in enumerate([6,26,46,10,12,14,16,16,18,16,22,28,16,14,46], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    thin = Side(style="thin", color="999999")
    for row in ws.iter_rows(min_row=start, max_row=gr, min_col=1, max_col=15):
        for cell in row:
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    wb.save(path)
    works = sum(x["Стоимость работ"] for x in items)
    mats = sum(x["Стоимость материалов"] for x in items)
    no_vat = works + mats; vat = no_vat * 0.2; grand = no_vat + vat
    return {"works": works, "mats": mats, "no_vat": no_vat, "vat": vat, "grand": grand}


def create_pdf(path: Path, items: List[Dict[str, Any]], meta: Dict[str, Any], totals: Dict[str, float]) -> None:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font_path = None
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]:
        if Path(p).exists():
            font_path = p; break
    if font_path:
        pdfmetrics.registerFont(TTFont("RU", font_path)); font = "RU"
    else:
        font = "Helvetica"

    doc = SimpleDocTemplate(str(path), pagesize=landscape(A4), leftMargin=18, rightMargin=18, topMargin=18, bottomMargin=18)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("n", parent=styles["Normal"], fontName=font, fontSize=8, leading=10)
    title = ParagraphStyle("t", parent=styles["Title"], fontName=font, fontSize=14, leading=16)
    story = [
        Paragraph("Смета: дренаж / ливневая канализация / наружные сети", title), Spacer(1, 8),
        Paragraph(f"Файлы: {', '.join(meta['file_names'])}", normal),
        Paragraph(f"Длина: {meta['total_len']} м; глубина: {meta['avg_depth']} м; статус: {meta['length_status']}", normal),
        Paragraph("Цены: высокий ценовой сегмент по голосовому ТЗ пользователя", normal), Spacer(1, 8),
    ]
    data = [["Раздел","Наименование","Ед","Кол-во","Работы","Материалы","Всего"]]
    for item in items:
        data.append([
            Paragraph(item["Раздел"], normal), Paragraph(item["Наименование"], normal),
            item["Ед изм"], f"{item['Кол-во']:.1f}",
            f"{item['Стоимость работ']:,.0f}".replace(",", " "),
            f"{item['Стоимость материалов']:,.0f}".replace(",", " "),
            f"{item['Всего']:,.0f}".replace(",", " "),
        ])
    table = Table(data, colWidths=[105,230,42,55,75,85,75])
    table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), font), ("FONTSIZE", (0,0), (-1,-1), 7),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey), ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story += [table, Spacer(1, 8),
        Paragraph(f"Материалы: {totals['mats']:,.0f} руб".replace(",", " "), normal),
        Paragraph(f"Работы: {totals['works']:,.0f} руб".replace(",", " "), normal),
        Paragraph(f"Без НДС: {totals['no_vat']:,.0f} руб".replace(",", " "), normal),
        Paragraph(f"НДС 20%: {totals['vat']:,.0f} руб".replace(",", " "), normal),
        Paragraph(f"С НДС: {totals['grand']:,.0f} руб".replace(",", " "), normal),
    ]
    doc.build(story)


async def maybe_upload(path: Path, chat_id: str, topic_id: int) -> str:
    try:
        from core.topic_drive_oauth import upload_file_to_topic
    except Exception as e:
        print(f"DRIVE_IMPORT_ERR={e}"); return ""
    calls = [
        lambda: upload_file_to_topic(str(path), chat_id=str(chat_id), topic_id=int(topic_id)),
        lambda: upload_file_to_topic(file_path=str(path), chat_id=str(chat_id), topic_id=int(topic_id)),
        lambda: upload_file_to_topic(str(path), str(chat_id), int(topic_id)),
    ]
    for fn in calls:
        try:
            res = fn()
            if inspect.isawaitable(res):
                res = await res
            if isinstance(res, dict):
                for k in ("webViewLink", "link", "url", "drive_link", "view_link"):
                    if res.get(k): return str(res[k])
                if res.get("file_id"):
                    return f"https://drive.google.com/file/d/{res['file_id']}/view"
            elif isinstance(res, str) and res.startswith("http"):
                return res
        except TypeError:
            continue
        except Exception as e:
            print(f"DRIVE_UPLOAD_ERR={path.name}:{e}"); continue
    return ""


def send_telegram(chat_id: str, topic_id: int, text: str) -> int:
    from core.reply_sender import send_reply_ex
    res = send_reply_ex(chat_id=str(chat_id), text=text, message_thread_id=int(topic_id))
    if not res.get("ok"):
        raise RuntimeError(f"TELEGRAM_SEND_FAILED:{res}")
    return int(res.get("bot_message_id") or 0)


async def main() -> None:
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    task = conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1", (TASK_ID,)).fetchone()
    if not task:
        raise SystemExit(f"TASK_NOT_FOUND:{TASK_ID}")
    chat_id = str(dict(task)["chat_id"])
    topic_id = int(dict(task).get("topic_id") or 2)

    pdfs = find_recent_pdfs()
    readbacks = []
    for p in pdfs:
        text = pdf_text(p)
        kind = classify_pdf(p, text)
        if kind in ("drainage_scheme", "geology_report"):
            readbacks.append({"path": p, "name": p.name, "kind": kind, "text": text, "chars": len(text)})

    drainage = [x for x in readbacks if x["kind"] == "drainage_scheme"]
    geology = [x for x in readbacks if x["kind"] == "geology_report"]

    if not drainage:
        raise SystemExit("DRAINAGE_PDF_NOT_FOUND")

    scheme_text = "\n".join(x["text"] for x in drainage)
    geo_text = "\n".join(x["text"] for x in geology)
    all_text = scheme_text + "\n" + geo_text

    lengths = extract_lengths(scheme_text)
    total_len = round(sum(lengths), 2)
    depths = extract_depths(geo_text) or extract_depths(all_text)
    avg_depth = round(max(1.2, min(depths)), 2) if depths else 1.5
    wells_d = count_unique(scheme_text, "Дк")
    wells_l = count_unique(scheme_text, "Лк")
    has_dns = has(scheme_text, "ДНС")
    has_pu = has(scheme_text, "пескоуловитель") or has(scheme_text, "ПУ-1")

    length_status = "READBACK_LENGTHS_FOUND" if total_len > 0 else "APPROX_FROM_SCHEME_NO_FULL_LENGTH_TABLE"
    source_note = f"{length_status}; PDF read-back: drainage={len(drainage)}, geology={len(geology)}"

    items = build_items(total_len, avg_depth, wells_d, wells_l, has_dns, has_pu, source_note)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    xlsx = OUT_DIR / f"drainage_estimate_{TASK_ID[:8]}_{stamp}.xlsx"
    pdf_out = OUT_DIR / f"drainage_estimate_{TASK_ID[:8]}_{stamp}.pdf"
    meta = {"file_names": [x["name"] for x in readbacks], "total_len": total_len,
            "avg_depth": avg_depth, "length_status": length_status}

    totals = create_xlsx(xlsx, items, meta)
    create_pdf(pdf_out, items, meta, totals)

    xlsx_link = await maybe_upload(xlsx, chat_id, topic_id)
    pdf_link = await maybe_upload(pdf_out, chat_id, topic_id)

    public = (
        f"✅ Смета дренажа готова\n\n"
        f"Объект: наружные сети / дренаж / ливневая канализация\n"
        f"Файлы учтены: {', '.join(meta['file_names'])}\n"
        f"Домен: drainage_network\n"
        f"Цены: высокий ценовой сегмент\n"
        f"Статус длин: {length_status}\n"
        f"Длина по read-back: {total_len} м\n"
        f"Расчётная глубина: {avg_depth} м\n\n"
        f"Итого:\n"
        f" Материалы: {totals['mats']:,.0f} руб\n"
        f" Работы: {totals['works']:,.0f} руб\n"
        f" Без НДС: {totals['no_vat']:,.0f} руб\n"
        f" НДС: {totals['vat']:,.0f} руб\n"
        f" С НДС: {totals['grand']:,.0f} руб\n\n"
        f"Excel: {xlsx_link or str(xlsx)}\n"
        f"PDF: {pdf_link or str(pdf_out)}\n\n"
        f"Подтверди или пришли правки"
    ).replace(",", " ")

    bot_msg = send_telegram(chat_id, topic_id, public)

    conn.execute(
        "UPDATE tasks SET state='AWAITING_CONFIRMATION', result=?, bot_message_id=?, error_message=NULL, updated_at=datetime('now') WHERE id=?",
        (public, bot_msg, TASK_ID),
    )

    def h(action: str) -> None:
        history(conn, TASK_ID, action)

    h(f"TOPIC2_DRAINAGE_MULTIFILE_BUNDLE_CREATED:{len(readbacks)}")
    for x in readbacks:
        h(f"TOPIC2_MULTIFILE_BUNDLE_FILE:{x['name']}:kind={x['kind']}:chars={x['chars']}")
    h(f"TOPIC2_DRAINAGE_LENGTHS_STATUS:{length_status}:total_len={total_len}")
    h(f"TOPIC2_DRAINAGE_DEPTH_STATUS:avg_depth={avg_depth}:depths={depths[:10]}")
    h(f"TOPIC2_DRAINAGE_WELLS:dk={wells_d}:lk={wells_l}:dns={int(has_dns)}:pu={int(has_pu)}")
    h(f"TOPIC2_DRAINAGE_XLSX_CREATED:{xlsx}")
    h(f"TOPIC2_DRAINAGE_PDF_CREATED:{pdf_out}")
    if xlsx_link: h(f"TOPIC2_DRAINAGE_DRIVE_XLSX_OK:{xlsx_link}")
    if pdf_link: h(f"TOPIC2_DRAINAGE_DRIVE_PDF_OK:{pdf_link}")
    h(f"TOPIC2_DRAINAGE_TELEGRAM_SENT:{bot_msg}")
    h("TOPIC2_DRAINAGE_REPAIR_CLOSE_AWAITING_CONFIRMATION")
    conn.commit(); conn.close()

    print("DRAINAGE_REPAIR_OK")
    print(f"TASK_ID={TASK_ID}")
    print(f"BOT_MESSAGE_ID={bot_msg}")
    print(f"XLSX={xlsx}")
    print(f"PDF={pdf_out}")
    print(f"XLSX_LINK={xlsx_link}")
    print(f"PDF_LINK={pdf_link}")
    print(f"TOTAL_LEN={total_len}")
    print(f"LENGTH_STATUS={length_status}")
    print(f"GRAND={totals['grand']}")

if __name__ == "__main__":
    asyncio.run(main())
