# === PDF_SPEC_EXTRACTOR_REAL_V1 ===
from __future__ import annotations

import re
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

UNIT_RE = re.compile(r"\b(м2|м²|м3|м³|п\.?м|пог\.?м|шт|кг|тн|тонн|т|м|мм|компл)\b", re.I)
NUM_RE = re.compile(r"^-?\d+(?:[.,]\d+)?$")


def _s(v: Any) -> str:
    return "" if v is None else str(v).strip()


def _num(v: Any) -> float:
    try:
        return float(_s(v).replace(" ", "").replace(",", "."))
    except Exception:
        return 0.0


def _unit(v: Any) -> str:
    s = _s(v).lower()
    s = s.replace("м2", "м²").replace("м3", "м³").replace("пог.м", "п.м").replace("пм", "п.м")
    return s


def _row_to_item(row: List[Any]) -> Dict[str, Any]:
    cells = [_s(x) for x in row if _s(x)]
    if not cells:
        return {}

    name = ""
    unit = ""
    qty = 0.0
    price = 0.0

    for c in cells:
        if not unit and UNIT_RE.search(c):
            unit = _unit(UNIT_RE.search(c).group(1))
            continue

    nums = []
    for c in cells:
        cleaned = c.replace(" ", "").replace(",", ".")
        if NUM_RE.match(cleaned):
            nums.append(_num(cleaned))

    if nums:
        qty = nums[0]
    if len(nums) >= 2:
        price = nums[1]

    for c in cells:
        cl = c.lower()
        if UNIT_RE.search(c):
            continue
        if NUM_RE.match(c.replace(" ", "").replace(",", ".")):
            continue
        if len(c) >= 3 and not any(x in cl for x in ("итого", "сумма", "всего", "кол-во", "количество", "ед.")):
            name = c
            break

    if not name or qty <= 0:
        return {}

    return {
        "name": name[:240],
        "unit": unit,
        "qty": qty,
        "price": price,
        "total": round(qty * price, 2) if price else 0.0,
        "source": "pdfplumber_table",
    }


def extract_spec(file_path: str, **kwargs) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    errors: List[str] = []

    try:
        import pdfplumber
    except Exception as e:
        return {"rows": [], "error": f"PDFPLUMBER_IMPORT_FAILED: {e}", "stub": False}

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_no, page in enumerate(pdf.pages, 1):
                try:
                    tables = page.extract_tables() or []
                except Exception as e:
                    errors.append(f"page_{page_no}_tables: {e}")
                    tables = []

                for table in tables:
                    for raw_row in table or []:
                        item = _row_to_item(raw_row or [])
                        if item:
                            item["page"] = page_no
                            rows.append(item)

                if not tables:
                    try:
                        text = page.extract_text() or ""
                    except Exception:
                        text = ""
                    for line in text.splitlines():
                        m = re.search(r"(?P<name>.{3,120}?)\s+(?P<qty>\d+(?:[.,]\d+)?)\s*(?P<unit>м2|м²|м3|м³|п\.?м|шт|кг|тн|т|м)\b(?:\s+(?P<price>\d+(?:[.,]\d+)?))?", line, re.I)
                        if not m:
                            continue
                        qty = _num(m.group("qty"))
                        price = _num(m.group("price"))
                        rows.append({
                            "name": _s(m.group("name"))[:240],
                            "unit": _unit(m.group("unit")),
                            "qty": qty,
                            "price": price,
                            "total": round(qty * price, 2) if price else 0.0,
                            "page": page_no,
                            "source": "pdfplumber_text_line",
                        })

        dedup = []
        seen = set()
        for r in rows:
            key = (r.get("name"), r.get("unit"), r.get("qty"), r.get("price"))
            if key in seen:
                continue
            seen.add(key)
            dedup.append(r)

        return {
            "rows": dedup,
            "count": len(dedup),
            "error": "" if dedup else "PDF_SPEC_ROWS_NOT_FOUND",
            "errors": errors[:20],
            "stub": False,
        }
    except Exception as e:
        logger.exception("PDF_SPEC_EXTRACTOR_REAL_V1 failed")
        return {"rows": [], "error": f"PDF_SPEC_EXTRACTOR_FAILED: {e}", "stub": False}


# === END_PDF_SPEC_EXTRACTOR_REAL_V1 ===
