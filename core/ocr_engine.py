# === OCR_ENGINE_V1 — по колонкам ===
import logging, os, re
from typing import List, Dict, Any, Optional
logger = logging.getLogger(__name__)

HEADERS = ["№", "Вид работ / Наименование", "Ед.изм", "Кол-во", "Цена", "Сумма"]

def _ocr_image(path: str) -> str:
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(path)
        return pytesseract.image_to_string(img, lang="rus+eng")
    except Exception as e:
        logger.error("OCR_FAIL path=%s err=%s", path, e)
        return ""

def _parse_columns(text: str) -> List[Dict[str, Any]]:
    rows = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    num_re = re.compile(r"^\d+[\.\)]?\s")
    price_re = re.compile(r"\d[\d\s]*[\.,]\d{2}|\d{3,}")

    for line in lines:
        if num_re.match(line):
            prices = price_re.findall(line)
            row = {
                "raw": line,
                "qty":   float(re.sub(r"[^\d.]", "", prices[0])) if len(prices) > 0 else None,
                "price": float(re.sub(r"[^\d.]", "", prices[1])) if len(prices) > 1 else None,
                "total": float(re.sub(r"[^\d.]", "", prices[2])) if len(prices) > 2 else None,
            }
            # название = часть без цифр в начале
            name_part = num_re.sub("", line)
            for p in prices:
                name_part = name_part.replace(p, "", 1)
            row["name"] = name_part.strip()
            rows.append(row)
    return rows

def _write_xlsx(rows: List[Dict], out_path: str) -> bool:
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(HEADERS)
        for i, r in enumerate(rows, start=2):
            ws.append([
                i - 1,
                r.get("name", ""),
                "шт.",
                r.get("qty") or "",
                r.get("price") or "",
                f"=D{i}*E{i}" if r.get("qty") and r.get("price") else "",
            ])
        sum_row = len(rows) + 2
        ws.cell(sum_row, 5).value = "ИТОГО"
        ws.cell(sum_row, 6).value = f"=SUM(F2:F{sum_row-1})"
        wb.save(out_path)
        return True
    except Exception as e:
        logger.error("XLSX_WRITE_FAIL err=%s", e)
        return False

def process_ocr_image(image_path: str, out_dir: str = "/tmp") -> Dict[str, Any]:
    if not os.path.exists(image_path):
        return {"ok": False, "error": "IMAGE_NOT_FOUND"}
    text = _ocr_image(image_path)
    if not text or len(text.strip()) < 10:
        return {"ok": False, "error": "IMAGE_UNREADABLE"}
    rows = _parse_columns(text)
    if not rows:
        # fallback — вернуть сырой текст
        return {"ok": True, "rows": [], "raw_text": text, "xlsx": None}
    out_path = os.path.join(out_dir, f"ocr_{os.path.basename(image_path)}.xlsx")
    ok = _write_xlsx(rows, out_path)
    return {
        "ok": ok,
        "rows": rows,
        "xlsx": out_path if ok else None,
        "row_count": len(rows),
    }
# === END OCR_ENGINE_V1 ===
