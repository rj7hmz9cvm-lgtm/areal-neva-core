#!/usr/bin/env python3
# TOPIC2_DRAINAGE_LENGTH_PROOF_GATE_AND_ONLINE_PRICES_V2
# Requires: length proven from PDF read-back
# Requires: online price lookup via OpenRouter/Sonar for drainage materials
# If length=0: search prices (cache in history), ask user, WC. No fallback.
from __future__ import annotations
import asyncio, glob, inspect, os, re, sqlite3, subprocess, sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from dotenv import load_dotenv

BASE = Path("/root/.areal-neva-core")
sys.path.insert(0, str(BASE))
DB = BASE / "data" / "core.db"
OUT_DIR = BASE / "runtime" / "stroyka_estimates" / "drainage_repair"
TASK_ID = "043e5c9f-e8bc-434c-9dad-a66c7e50f917"
OUT_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE / ".env", override=False)
VAT_RATE = 0.22

DRAINAGE_STRONG = ["нвд","наружные водостоки","наружные водостоки и дренажи",
    "схема дренажной и ливневой канализации","дренажная насосная станция",
    "пескоуловитель","линейный водоотвод","d=160","i=0,005","дк","лк"]
GEO_STRONG = ["инженерно-геологические","бурение геотехнических скважин","скважин",
    "игэ","грунтовых вод","нормативная глубина промерзания","супесь","насыпные грунты"]

def low(t): return str(t or "").lower().replace("ё","е")

def hist(conn, tid, action):
    conn.execute("INSERT INTO task_history(task_id,action,created_at) VALUES(?,?,datetime('now'))",(tid,action[:900],))

def pdf_text(path):
    try:
        r = subprocess.run(["pdftotext","-layout","-q",str(path),"-"],
            stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,timeout=25)
        return r.stdout or ""
    except Exception as e:
        return f"PDFTOTEXT_ERR={e}"

def is_artifact(path, text):
    p = str(path)
    if "/runtime/stroyka_estimates/" in p: return True
    if path.name.lower().startswith("drainage_estimate_"): return True
    h = low(text[:600])
    if "смета:" in h and "дренаж" in h: return True
    return False

def classify(path, text):
    t = low(text); name = low(path.name)
    geo = sum(1 for m in GEO_STRONG if m in t)
    drn = sum(1 for m in DRAINAGE_STRONG if m in t)
    if "отчет" in name or "отчёт" in name or "мистолово" in name: geo += 3
    if "дренаж" in name or "схема" in name: drn += 3
    if geo >= 3 and drn < 5: return "geology_report"
    if drn >= 2: return "drainage_scheme"
    if geo >= 3: return "geology_report"
    return "other_pdf"

def friendly(kind):
    return {"drainage_scheme":"Схема глубинного дренажа.pdf",
            "geology_report":"Отчет_Мистолово_03.26.pdf"}.get(kind,"source.pdf")

def find_user_pdfs():
    now = datetime.now().timestamp()
    candidates = []
    for pat in ["/var/lib/telegram-bot-api/*/documents/*.pdf"]:
        for raw in glob.glob(pat):
            p = Path(raw)
            try:
                if p.is_file() and now - p.stat().st_mtime <= 12*3600:
                    candidates.append(p)
            except: pass
    out = []
    seen_kinds = set()
    for p in sorted(set(candidates), key=lambda x: x.stat().st_mtime, reverse=True):
        txt = pdf_text(p)
        if is_artifact(p, txt): continue
        kind = classify(p, txt)
        if kind in ("drainage_scheme","geology_report") and kind not in seen_kinds:
            out.append({"path":p,"kind":kind,"name":friendly(kind),"text":txt,"chars":len(txt)})
            seen_kinds.add(kind)
    return out

def infer_vat(conn, tid, raw_in, result):
    texts = [raw_in or "", result or ""]
    for row in conn.execute("SELECT action FROM task_history WHERE task_id=? ORDER BY rowid ASC",(tid,)).fetchall():
        texts.append(str(row[0] or ""))
    t = low("\n".join(texts))
    if "topic2_vat_mode_confirmed:with_vat_22" in t: return "WITH_VAT_22"
    if "topic2_vat_mode_confirmed:without_vat" in t: return "WITHOUT_VAT"
    wo = ["без ндс","ндс не нужен","без налога","без учета ндс","без учёта ндс"]
    wv = ["с ндс","с учетом ндс","с учётом ндс","добавь ндс","посчитай с ндс","с налогом"]
    if any(p in t for p in wo): return "WITHOUT_VAT"
    if any(p in t for p in wv): return "WITH_VAT_22"
    return None

def send_msg(chat_id, topic_id, text):
    from core.reply_sender import send_reply_ex
    if len(text) > 3900: text = text[:3800]+"\n\n[сокращено]"
    res = send_reply_ex(chat_id=str(chat_id), text=text,
                        message_thread_id=int(topic_id) if int(topic_id) else None)
    if not res.get("ok"): raise RuntimeError(f"SEND_FAILED:{res}")
    return int(res.get("bot_message_id") or 0)

def ask_vat(conn, task):
    tid = str(task["id"]); chat_id = str(task["chat_id"]); topic_id = int(task["topic_id"] or 2)
    msg = "Считать с НДС 22% или без НДС?"
    bot_msg = send_msg(chat_id, topic_id, msg)
    conn.execute("UPDATE tasks SET state='WAITING_CLARIFICATION',result=?,bot_message_id=?,"
                 "error_message='TOPIC2_VAT_MODE_REQUIRED',updated_at=datetime('now') WHERE id=?",
                 (msg, bot_msg, tid))
    hist(conn, tid, "TOPIC2_VAT_GATE_CHECKED")
    hist(conn, tid, "TOPIC2_VAT_MODE_REQUIRED")
    hist(conn, tid, f"TOPIC2_VAT_QUESTION_SENT:{bot_msg}")
    conn.commit()
    print(f"VAT_MODE_REQUIRED\nBOT_MESSAGE_ID={bot_msg}")

def num(x): return float(x.replace(",","."))

def extract_lengths(text):
    LEGEND_SKIP = ("уклон", "длина", "диаметр")
    vals = []
    for line in text.splitlines():
        ll = low(line)
        # skip legend/definition lines: "l=6,0 м i - уклон, l - длина, d - диаметр"
        if all(k in ll for k in LEGEND_SKIP): continue
        if not any(k in ll for k in ["i=","d=","дрен","водоотвод","труб","ливнев"]): continue
        for pat in [r"(?i)\bl\s*=\s*(\d+(?:[,.]\d+)?)\s*м\b",
                    r"(?i)длина\s*[-:=]?\s*(\d+(?:[,.]\d+)?)\s*м\b"]:
            for m in re.finditer(pat, line):
                try:
                    v = num(m.group(1))
                    if 0.5 <= v <= 500 and v not in vals: vals.append(round(v,2))
                except: pass
    return vals

def extract_depths(text):
    vals = []
    for pat in [r"(?i)на глубине\s*(\d+(?:[,.]\d+)?)\s*м",
                r"(?i)глубин[а-я]*\s*(?:до|от)?\s*(\d+(?:[,.]\d+)?)\s*м"]:
        for m in re.finditer(pat, text):
            try:
                v = num(m.group(1))
                if 0.2 <= v <= 12 and v not in vals: vals.append(round(v,2))
            except: pass
    return vals

def count_unique(text, prefix):
    return len(set(re.findall(rf"{re.escape(prefix)}\s*[-–]?\s*(\d+)", text, flags=re.I)))

def has(text, marker): return low(marker) in low(text)

async def search_drainage_prices_online(conn, tid):
    """Query Perplexity Sonar for drainage material prices in SPb/LO region."""
    api_key = os.getenv("OPENROUTER_API_KEY","").strip()
    base_url = os.getenv("OPENROUTER_BASE_URL","https://openrouter.ai/api/v1").rstrip("/")
    model = os.getenv("OPENROUTER_MODEL_ONLINE","perplexity/sonar").strip() or "perplexity/sonar"
    if not api_key:
        print("OPENROUTER_API_KEY_MISSING — online prices unavailable")
        hist(conn, tid, "TOPIC2_DRAINAGE_PRICE_SEARCH_KEY_MISSING")
        return None, {}
    if "sonar" not in model.lower():
        print(f"ONLINE_MODEL_NOT_SONAR:{model} — skipping")
        hist(conn, tid, f"TOPIC2_DRAINAGE_PRICE_SEARCH_MODEL_GUARD:{model}")
        return None, {}

    query = (
        "Актуальные рыночные цены Санкт-Петербург и Ленинградская область, 2025-2026.\n"
        "Объект: дренаж и ливневая канализация коттеджного участка.\n\n"
        "Найди цены с источниками:\n"
        "1. Труба дренажная гофрированная двустенная d=160мм (КОРСИС SN8 или аналог) — руб/п.м.\n"
        "2. Геотекстиль нетканый 150-200 г/м² (Terram, Typar, ТехноНИКОЛЬ) — руб/м²\n"
        "3. Щебень гранитный фракция 20-40мм — руб/м³\n"
        "4. Песок строительный намывной — руб/м³\n"
        "5. Колодец дренажный ревизионный ∅500 полимерный (Wavin, Политрон) — руб/шт\n"
        "6. Насосная станция дренажная 0.55кВт (Grundfos Unilift, Джилекс, Wilo) — руб/шт\n"
        "7. Пескоуловитель ПУ-1 дорожный пластиковый (Ecoteck, Gidrostroy) — руб/шт\n"
        "8. Лоток водоотводный DN100 пластиковый с решёткой (Hauraton, Gidrostroy) — руб/п.м.\n\n"
        "Формат для каждой позиции:\n"
        "[N]. Позиция | мин. цена | макс. цена | ед. | источник | URL | дата\n\n"
        "Только реальные данные. Если нет — НЕТ ДАННЫХ. Не выдумывай."
    )
    body = {
        "model": model,
        "messages": [
            {"role":"system","content":"Снабженец строительной компании. Только цены с источниками. Без советов."},
            {"role":"user","content":query},
        ],
        "temperature": 0.1,
    }
    headers = {"Authorization":f"Bearer {api_key}","Content-Type":"application/json"}
    try:
        def _call():
            r = requests.post(f"{base_url}/chat/completions", headers=headers, json=body, timeout=90)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP_{r.status_code}:{r.text[:200]}")
            return r.json()["choices"][0]["message"]["content"]
        content = await asyncio.to_thread(_call)
        hist(conn, tid, f"TOPIC2_DRAINAGE_PRICE_SEARCH_SONAR_OK:{len(content)}chars")
        prices = _parse_drainage_prices(content)
        print(f"SONAR_PRICES_PARSED={list(prices.keys())}")
        return content, prices
    except Exception as e:
        hist(conn, tid, f"TOPIC2_DRAINAGE_PRICE_SEARCH_ERR:{str(e)[:120]}")
        print(f"SONAR_PRICE_SEARCH_FAILED: {e}")
        return None, {}

def _parse_drainage_prices(text):
    """Extract numeric prices from Sonar response. Returns dict item → price."""
    prices = {}
    if not text: return prices
    t = low(text)

    def _grab(pattern, lo, hi):
        m = re.search(pattern, t, re.I|re.S)
        if not m: return None
        try:
            v = float(re.sub(r"[\s\xa0 ]","", m.group(1)).replace(",","."))
            return v if lo <= v <= hi else None
        except: return None

    v = _grab(r"труб[а-я]*.*?d=?160[^|]*?\|[^|]*?(\d[\d\s]*)\s*руб", 100, 3000)
    if v: prices["pipe_per_m"] = v

    v = _grab(r"геотекстил[ья][^|]*?\|[^|]*?(\d[\d\s]*)\s*руб", 20, 800)
    if v: prices["geotextile_per_m2"] = v

    v = _grab(r"щебен[ья][^|]*?\|[^|]*?(\d[\d\s]*)\s*руб", 500, 15000)
    if v: prices["gravel_per_m3"] = v

    v = _grab(r"колодец[^|]*?∅?500[^|]*?\|[^|]*?(\d[\d\s]*)\s*руб", 3000, 150000)
    if not v: v = _grab(r"колодец[^|]*?дренаж[^|]*?\|[^|]*?(\d[\d\s]*)\s*руб", 3000, 150000)
    if v: prices["well_per_unit"] = v

    v = _grab(r"насосн[^|]*?станц[^|]*?\|[^|]*?(\d[\d\s]*)\s*руб", 5000, 500000)
    if v: prices["dns_per_unit"] = v

    v = _grab(r"пескоулов[^|]*?\|[^|]*?(\d[\d\s]*)\s*руб", 1000, 80000)
    if v: prices["pu_per_unit"] = v

    v = _grab(r"лоток[^|]*?\|[^|]*?(\d[\d\s]*)\s*руб", 200, 15000)
    if v: prices["channel_per_m"] = v

    return prices

def build_items(L, depth, wd, wl, dns, pu, note, online_prices=None):
    # No fallback — caller must ensure L > 0
    if L <= 0:
        raise ValueError("TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN_NO_FALLBACK")
    p = online_prices or {}
    src = "OpenRouter/Sonar (актуальные)" if p else "MANUAL_HIGH_SEGMENT_BY_USER"
    supplier = "онлайн-поиск СПб/ЛО" if p else "ручной высокий сегмент"

    pipe_mat     = p.get("pipe_per_m",        1250)
    geo_mat      = p.get("geotextile_per_m2",   95)
    gravel_mat   = p.get("gravel_per_m3",      3200)
    well_mat     = p.get("well_per_unit",     18000)
    dns_mat      = p.get("dns_per_unit",     145000)
    pu_mat       = p.get("pu_per_unit",       22000)
    channel_mat  = p.get("channel_per_m",      2600)

    ex = round(L * depth * 0.6, 2)
    rows = [
        ("Подготовительные и земляные работы","Разметка трасс дренажа/ливнёвки","м.п.",L,450,0),
        ("Подготовительные и земляные работы","Разработка траншей","м³",ex,1900,0),
        ("Подготовительные и земляные работы","Вывоз/перемещение лишнего грунта","м³",round(ex*0.35,2),1400,0),
        ("Геотекстиль / щебень / песок","Геотекстиль в траншее","м²",round(L*1.8,2),180,geo_mat),
        ("Геотекстиль / щебень / песок","Песчаная подготовка","м³",round(L*0.12,2),1300,1700),
        ("Геотекстиль / щебень / песок","Щебёночный фильтр","м³",round(L*0.35,2),1600,gravel_mat),
        ("Дренажные трубы и обратный фильтр","Труба дренажная/водоотводящая d=160","м.п.",L,850,pipe_mat),
        ("Дренажные трубы и обратный фильтр","Укладка трубы с уклоном i=0,005","м.п.",L,950,0),
    ]
    if wd: rows.append(("Колодцы и дождеприёмники","Дренажный ревизионный колодец Дк","шт",wd,6500,well_mat))
    if wl: rows.append(("Колодцы и дождеприёмники","Ливневый ревизионный колодец Лк","шт",wl,6500,well_mat))
    if dns: rows.append(("ДНС / насосное оборудование","Дренажная насосная станция ДНС-1","компл",1,28000,dns_mat))
    if pu: rows.append(("Пескоуловители / линейный водоотвод","Пескоуловитель ПУ-1","шт",1,6500,pu_mat))
    rows.extend([
        ("Ливневая канализация","Линейный водоотвод / лотки","м.п.",max(round(L*0.2,2),1),1100,channel_mat),
        ("Монтажные работы","Сборка узлов, подключение колодцев и выпусков","компл",1,45000,0),
        ("Логистика","Доставка материалов и инструмента","рейс",2,0,18000),
    ])
    out = []
    for i,(sec,name,unit,qty,work,mat) in enumerate(rows,1):
        qty=float(qty);work=float(work);mat=float(mat)
        out.append({"№":i,"Раздел":sec,"Наименование":name,"Ед изм":unit,"Кол-во":qty,
            "Цена работ":work,"Стоимость работ":round(qty*work,2),
            "Цена материалов":mat,"Стоимость материалов":round(qty*mat,2),
            "Всего":round(qty*(work+mat),2),"Источник цены":src,
            "Поставщик":supplier,
            "URL":"—","checked_at":datetime.now().strftime("%Y-%m-%d"),"Примечание":note})
    return out

def calc_totals(items, vat_mode):
    works = sum(x["Стоимость работ"] for x in items)
    mats  = sum(x["Стоимость материалов"] for x in items)
    no_vat = works + mats
    vat = no_vat * VAT_RATE if vat_mode == "WITH_VAT_22" else 0.0
    return {"works":works,"mats":mats,"no_vat":no_vat,"vat":vat,"grand":no_vat+vat}

def create_xlsx(path, items, meta, vat_mode, online_price_text=None):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    H = ["№","Раздел","Наименование","Ед изм","Кол-во","Цена работ","Стоимость работ",
         "Цена материалов","Стоимость материалов","Всего","Источник цены","Поставщик","URL","checked_at","Примечание"]
    wb = Workbook(); ws = wb.active; ws.title = "DRAINAGE_CALC"
    ws["A1"] = "Смета: дренаж / ливневая канализация / наружные сети"
    ws["A2"] = f"Исходные файлы: {', '.join(meta['file_names'])}"
    ws["A3"] = f"Длина: {meta['total_len']} м; глубина: {meta['avg_depth']} м; статус: {meta['length_status']}"
    ws["A4"] = "Цены: онлайн-поиск OpenRouter/Sonar (СПб/ЛО)" if meta.get("prices_source") == "sonar" else "Цены: высокий ценовой сегмент по ТЗ"
    ws["A5"] = "НДС: 22%" if vat_mode=="WITH_VAT_22" else "НДС: не применяется"
    for r in range(1,6): ws.cell(r,1).font = Font(bold=True)
    start = 7
    for c,h in enumerate(H,1):
        cell = ws.cell(start,c,h)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid",fgColor="D9EAF7")
        cell.alignment = Alignment(horizontal="center",vertical="center",wrap_text=True)
    for r,item in enumerate(items,start+1):
        for c,h in enumerate(H,1): ws.cell(r,c,item[h])
        ws.cell(r,7,f"=E{r}*F{r}"); ws.cell(r,9,f"=E{r}*H{r}"); ws.cell(r,10,f"=G{r}+I{r}")
    last = start+len(items); tr=last+2
    ws.cell(tr,2,"ИТОГО без НДС" if vat_mode=="WITH_VAT_22" else "ИТОГО")
    ws.cell(tr,7,f"=SUM(G{start+1}:G{last})"); ws.cell(tr,9,f"=SUM(I{start+1}:I{last})"); ws.cell(tr,10,f"=SUM(J{start+1}:J{last})")
    if vat_mode=="WITH_VAT_22":
        vr=tr+1; gr=vr+1
        ws.cell(vr,2,"НДС 22%"); ws.cell(vr,10,f"=J{tr}*0.22")
        ws.cell(gr,2,"ИТОГО с НДС"); ws.cell(gr,10,f"=J{tr}+J{vr}")
    else:
        vr=tr+1; gr=vr
        ws.cell(vr,2,"НДС не применяется"); ws.cell(vr,10,0)
    for r in range(tr,gr+1):
        for c in range(1,16): ws.cell(r,c).font = Font(bold=True)
    for i,w in enumerate([6,26,46,10,12,14,16,16,18,16,22,28,16,14,46],1):
        ws.column_dimensions[get_column_letter(i)].width = w
    thin = Side(style="thin",color="999999")
    for row in ws.iter_rows(min_row=start,max_row=gr,min_col=1,max_col=15):
        for cell in row:
            cell.border = Border(left=thin,right=thin,top=thin,bottom=thin)
            cell.alignment = Alignment(vertical="top",wrap_text=True)
    # Online prices sheet
    if online_price_text:
        ws2 = wb.create_sheet("Цены онлайн (Sonar)")
        ws2["A1"] = "Цены из интернета — OpenRouter / Perplexity Sonar"
        ws2["A2"] = f"Дата запроса: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ws2["A1"].font = Font(bold=True)
        ws2["A2"].font = Font(italic=True)
        for i, line in enumerate(online_price_text.splitlines(), 4):
            ws2.cell(i, 1, line[:500])
        ws2.column_dimensions["A"].width = 120
    wb.save(path)
    return calc_totals(items, vat_mode)

def create_pdf(path, items, meta, totals, vat_mode):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    fp = next((p for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"] if Path(p).exists()), None)
    if fp: pdfmetrics.registerFont(TTFont("RU",fp)); font="RU"
    else: font="Helvetica"
    vat_label = "НДС: 22%" if vat_mode=="WITH_VAT_22" else "НДС: не применяется"
    prices_label = "Цены: онлайн-поиск OpenRouter/Sonar" if meta.get("prices_source")=="sonar" else "Цены: высокий ценовой сегмент"
    doc = SimpleDocTemplate(str(path),pagesize=landscape(A4),leftMargin=18,rightMargin=18,topMargin=18,bottomMargin=18)
    sty = getSampleStyleSheet()
    N = ParagraphStyle("n",parent=sty["Normal"],fontName=font,fontSize=8,leading=10)
    T = ParagraphStyle("t",parent=sty["Title"],fontName=font,fontSize=14,leading=16)
    story = [Paragraph("Смета: дренаж / ливневая канализация / наружные сети",T),Spacer(1,8),
             Paragraph(f"Исходные файлы: {', '.join(meta['file_names'])}",N),
             Paragraph(f"Длина: {meta['total_len']} м; глубина: {meta['avg_depth']} м; статус: {meta['length_status']}",N),
             Paragraph(f"{prices_label}; {vat_label}",N),Spacer(1,8)]
    data=[["Раздел","Наименование","Ед","Кол-во","Работы","Материалы","Всего"]]
    for item in items:
        data.append([Paragraph(item["Раздел"],N),Paragraph(item["Наименование"],N),item["Ед изм"],
                     f"{item['Кол-во']:.1f}",
                     f"{item['Стоимость работ']:,.0f}".replace(",","  "),
                     f"{item['Стоимость материалов']:,.0f}".replace(",","  "),
                     f"{item['Всего']:,.0f}".replace(",","  ")])
    table=Table(data,colWidths=[105,230,42,55,75,85,75])
    table.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),font),("FONTSIZE",(0,0),(-1,-1),7),
                                ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
                                ("GRID",(0,0),(-1,-1),0.25,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story+=[table,Spacer(1,8),
            Paragraph(f"Материалы: {totals['mats']:,.0f} руб".replace(",","  "),N),
            Paragraph(f"Работы: {totals['works']:,.0f} руб".replace(",","  "),N)]
    if vat_mode=="WITH_VAT_22":
        story+=[Paragraph(f"Без НДС: {totals['no_vat']:,.0f} руб".replace(",","  "),N),
                Paragraph(f"НДС 22%: {totals['vat']:,.0f} руб".replace(",","  "),N),
                Paragraph(f"С НДС: {totals['grand']:,.0f} руб".replace(",","  "),N)]
    else:
        story+=[Paragraph(f"Итого без НДС: {totals['grand']:,.0f} руб".replace(",","  "),N),
                Paragraph("НДС: не применяется",N)]
    doc.build(story)

async def maybe_upload(path, chat_id, topic_id):
    try: from core.topic_drive_oauth import upload_file_to_topic
    except: return ""
    for fn in [
        lambda: upload_file_to_topic(file_path=str(path), file_name=path.name, chat_id=str(chat_id), topic_id=int(topic_id)),
        lambda: upload_file_to_topic(str(path), path.name, str(chat_id), int(topic_id)),
    ]:
        try:
            res = fn()
            if inspect.isawaitable(res): res = await res
            if isinstance(res,dict):
                for k in ("webViewLink","link","url","drive_link","view_link"):
                    if res.get(k): return str(res[k])
                if res.get("file_id"): return f"https://drive.google.com/file/d/{res['file_id']}/view"
            if isinstance(res,str) and res.startswith("http"): return res
        except: continue
    return ""

def send_doc(chat_id, topic_id, path, caption):
    token = os.getenv("TELEGRAM_BOT_TOKEN","").strip()
    if not token: raise RuntimeError("TELEGRAM_BOT_TOKEN_MISSING")
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(path,"rb") as fh:
        data={"chat_id":str(chat_id),"caption":caption[:900]}
        if int(topic_id)!=0: data["message_thread_id"]=str(int(topic_id))
        r=requests.post(url,data=data,files={"document":(path.name,fh)},timeout=120)
    js=r.json()
    if r.status_code!=200 or not js.get("ok"):
        raise RuntimeError(f"SEND_DOC_FAILED:{r.status_code}:{r.text[:200]}")
    return int(js["result"]["message_id"])

async def main():
    conn=sqlite3.connect(str(DB)); conn.row_factory=sqlite3.Row
    task=conn.execute("SELECT * FROM tasks WHERE id=? LIMIT 1",(TASK_ID,)).fetchone()
    if not task: raise SystemExit(f"TASK_NOT_FOUND:{TASK_ID}")
    tid=str(task["id"]); chat_id=str(task["chat_id"]); topic_id=int(task["topic_id"] or 2)
    raw_in=str(task["raw_input"] or ""); result=str(task["result"] or "")

    vat_mode = infer_vat(conn, tid, raw_in, result)
    if vat_mode is None:
        ask_vat(conn, task); conn.close(); return

    hist(conn, tid, "TOPIC2_VAT_GATE_CHECKED")
    hist(conn, tid, f"TOPIC2_VAT_MODE_CONFIRMED:{vat_mode}")

    sources = find_user_pdfs()
    if not sources: raise SystemExit("NO_USER_SOURCE_PDFS")
    drainage = [x for x in sources if x["kind"]=="drainage_scheme"]
    geology  = [x for x in sources if x["kind"]=="geology_report"]
    if not drainage: raise SystemExit("DRAINAGE_SOURCE_NOT_FOUND")

    print(f"SOURCES_FOUND={[x['name'] for x in sources]}")

    scheme_text = "\n".join(x["text"] for x in drainage)
    geo_text    = "\n".join(x["text"] for x in geology)
    lengths = extract_lengths(scheme_text)
    total_len = round(sum(lengths),2)
    depths = extract_depths(geo_text)
    avg_depth = round(max(1.2,min(depths)),2) if depths else 1.2
    wells_d=count_unique(scheme_text,"Дк"); wells_l=count_unique(scheme_text,"Лк")
    has_dns=has(scheme_text,"ДНС"); has_pu=has(scheme_text,"пескоуловитель") or has(scheme_text,"ПУ-1")

    print(f"LENGTHS_FOUND={lengths} TOTAL_LEN={total_len}")

    # LENGTH PROOF GATE — no fallback allowed
    if total_len <= 0 or len(lengths) < 1:
        print("LENGTH_NOT_PROVEN — searching prices online then asking user")
        price_text, _ = await search_drainage_prices_online(conn, tid)
        if price_text:
            hist(conn, tid, f"TOPIC2_DRAINAGE_ONLINE_PRICES_CACHED:{len(price_text)}chars")
            conn.commit()

        wc_msg = (
            "Длина трасс дренажа и ливнёвки в PDF не читается — схема графическая, "
            "размерные цепочки не в текстовом слое.\n\n"
            "Пришли, пожалуйста:\n"
            "• Общую длину дренажных труб (в метрах)\n"
            "• Или длины по участкам: Дк-1→Дк-2, Дк-2→ДНС, и т.д.\n\n"
            "После этого пересчитаю смету с актуальными ценами из интернета."
        )
        bot_msg = send_msg(chat_id, topic_id, wc_msg)
        conn.execute(
            "UPDATE tasks SET state='WAITING_CLARIFICATION', result=?, bot_message_id=?, "
            "error_message='TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN', updated_at=datetime('now') WHERE id=?",
            (wc_msg, bot_msg, tid),
        )
        for action in [
            "TOPIC2_DRAINAGE_LENGTH_PROOF_GATE_V1",
            f"TOPIC2_DRAINAGE_LENGTH_NOT_PROVEN:lines={len(lengths)}:total={total_len}",
            "TOPIC2_DRAINAGE_FINAL_ARTIFACTS_BLOCKED",
            f"TOPIC2_DRAINAGE_WC_SENT:{bot_msg}",
        ]:
            hist(conn, tid, action)
        conn.commit(); conn.close()
        print(f"DRAINAGE_LENGTH_GATE_WC_SENT\nBOT_MESSAGE_ID={bot_msg}")
        return

    # LENGTH PROVEN — search prices online before generating
    price_text, online_prices = await search_drainage_prices_online(conn, tid)
    prices_source = "sonar" if online_prices else "manual"
    print(f"ONLINE_PRICES={list(online_prices.keys()) if online_prices else 'NONE — using manual baseline'}")

    length_status = "READBACK_LENGTHS_FOUND"
    note = (f"{length_status}; prices={prices_source}; "
            f"source_filter=user_pdfs_only; drainage={len(drainage)}, geology={len(geology)}")
    items = build_items(total_len, avg_depth, wells_d, wells_l, has_dns, has_pu, note, online_prices)

    stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    xlsx=OUT_DIR/f"drainage_estimate_clean_{tid[:8]}_{stamp}.xlsx"
    pdf_out=OUT_DIR/f"drainage_estimate_clean_{tid[:8]}_{stamp}.pdf"
    meta={"file_names":[x["name"] for x in sources],"total_len":total_len,"avg_depth":avg_depth,
          "length_status":length_status,"prices_source":prices_source}

    totals=create_xlsx(xlsx, items, meta, vat_mode, online_price_text=price_text)
    create_pdf(pdf_out, items, meta, totals, vat_mode)

    xlsx_link=await maybe_upload(xlsx,chat_id,topic_id)
    pdf_link =await maybe_upload(pdf_out,chat_id,topic_id)

    if not xlsx_link: msg_id=send_doc(chat_id,topic_id,xlsx,"Excel: смета дренажа"); print(f"XLSX_DOC_SENT:{msg_id}")
    if not pdf_link:  msg_id=send_doc(chat_id,topic_id,pdf_out,"PDF: смета дренажа"); print(f"PDF_DOC_SENT:{msg_id}")

    if vat_mode=="WITH_VAT_22":
        totals_block=(f"Без НДС: {totals['no_vat']:,.0f} руб\n"
                      f" НДС 22%: {totals['vat']:,.0f} руб\n"
                      f" С НДС: {totals['grand']:,.0f} руб").replace(",","  ")
    else:
        totals_block=f"Итого без НДС: {totals['grand']:,.0f} руб\n НДС: не применяется".replace(",","  ")

    prices_line = "Цены: онлайн-поиск OpenRouter/Sonar" if online_prices else "Цены: высокий ценовой сегмент"
    excel_line=f"Excel: {xlsx_link}" if xlsx_link else "Excel: отправлен файлом"
    pdf_line  =f"PDF: {pdf_link}"   if pdf_link  else "PDF: отправлен файлом"

    public=(f"✅ Смета дренажа готова\n\n"
            f"Объект: наружные сети / дренаж / ливневая канализация\n"
            f"Файлы учтены: {', '.join(meta['file_names'])}\n"
            f"{prices_line}\n"
            f"Длина: {total_len} м; глубина: {avg_depth} м\n\n"
            f"Итого:\n Материалы: {totals['mats']:,.0f} руб\n Работы: {totals['works']:,.0f} руб\n {totals_block}\n\n"
            f"{excel_line}\n{pdf_line}\n\nПодтверди или пришли правки").replace(",","  ")

    dirty=[x for x in ["/root/","runtime","drainage_estimate_"] if x in public]
    if dirty: raise SystemExit(f"PUBLIC_OUTPUT_DIRTY:{dirty}")

    bot_msg=send_msg(chat_id,topic_id,public)
    conn.execute("UPDATE tasks SET state='AWAITING_CONFIRMATION',result=?,bot_message_id=?,"
                 "error_message=NULL,updated_at=datetime('now') WHERE id=?",(public,bot_msg,tid))

    for action in [
        f"TOPIC2_DRAINAGE_SOURCE_FILTER_OK:user_pdfs={len(sources)}",
        "TOPIC2_DRAINAGE_NO_GENERATED_ARTIFACT_INPUT",
        *[f"TOPIC2_DRAINAGE_SOURCE_FILE:{x['name']}:kind={x['kind']}:chars={x['chars']}" for x in sources],
        f"TOPIC2_DRAINAGE_LENGTHS_STATUS:{length_status}:total_len={total_len}",
        f"TOPIC2_DRAINAGE_DEPTH_STATUS:avg_depth={avg_depth}",
        f"TOPIC2_DRAINAGE_PRICES_SOURCE:{prices_source}:keys={list(online_prices.keys()) if online_prices else []}",
        f"TOPIC2_DRAINAGE_XLSX_CREATED:{xlsx.name}",
        f"TOPIC2_DRAINAGE_PDF_CREATED:{pdf_out.name}",
        f"TOPIC2_DRAINAGE_DRIVE_XLSX_OK:{xlsx_link}" if xlsx_link else "TOPIC2_DRAINAGE_TELEGRAM_XLSX_FALLBACK_SENT",
        f"TOPIC2_DRAINAGE_DRIVE_PDF_OK:{pdf_link}"  if pdf_link  else "TOPIC2_DRAINAGE_TELEGRAM_PDF_FALLBACK_SENT",
        f"TOPIC2_DRAINAGE_TELEGRAM_SENT:{bot_msg}",
        "TOPIC2_VAT_PUBLIC_OUTPUT_OK","TOPIC2_DRAINAGE_AWAITING_CONFIRMATION_CLEAN_V1",
    ]: hist(conn,tid,action)
    conn.commit(); conn.close()

    print("DRAINAGE_ESTIMATE_OK")
    print(f"VAT_MODE={vat_mode} BOT_MESSAGE_ID={bot_msg}")
    print(f"TOTAL_LEN={total_len} GRAND={totals['grand']}")

if __name__=="__main__":
    asyncio.run(main())
