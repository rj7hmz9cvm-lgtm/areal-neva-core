from __future__ import annotations
import re
from collections import defaultdict

UNIT_PATTERNS = ["м3","м2","м.п.","п.м.","мп","шт","тн","т","кг","л","компл","комплект"]
BAD_TOKENS = {"гост","снип","сп","b25","a500","мм","см","м"}

def _norm(s: str) -> str:
    return re.sub(r"\s+"," ",(s or "").strip())

def _find_unit(text: str) -> str:
    low = (text or "").lower()
    for u in UNIT_PATTERNS:
        if u in low:
            return u
    return ""

def _find_qty(text: str) -> str:
    low = (text or "").lower()
    if any(b in low for b in BAD_TOKENS):
        return ""
    matches = re.findall(r"(?<![A-Za-zА-Яа-я])(\d+[.,]?\d*)", text or "")
    for num in matches:
        return num.replace(",",".")
    return ""

def _guess_name(line: str) -> str:
    line = _norm(line)
    line = re.sub(r"\b\d+[.,]?\d*\b","",line)
    for u in UNIT_PATTERNS:
        line = re.sub(re.escape(u),"",line,flags=re.I)
    return _norm(line).strip("-–—:;| ")

def build_estimate_table(text: str) -> dict:
    rows = []
    totals = defaultdict(float)

    for raw in (text or "").splitlines():
        line = _norm(raw)
        if not line or len(line) < 4:
            continue

        unit = _find_unit(line)
        qty = _find_qty(line)

        if not unit and not qty:
            continue

        name = _guess_name(line)
        if len(name) < 3:
            continue

        try:
            val = float(qty) if qty else 0.0
        except:
            val = 0.0

        rows.append({"name":name,"unit":unit,"qty":qty,"note":""})

        if unit and val:
            totals[unit] += val

    out = ["Наименование | Ед.изм | Кол-во | Примечание","--- | --- | --- | ---"]

    for r in rows[:80]:
        out.append(f'{r["name"]} | {r["unit"]} | {r["qty"]} | {r["note"]}')

    if totals:
        out.append("\nИТОГО:")
        for k,v in totals.items():
            out.append(f"{round(v,3)} {k}")

    return "\n".join(out)
