import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("estimate_engine")

TARGET_CATEGORIES = [
    "кровля", "бетон", "арматур", "кладка", "монтаж", "устройство",
    "каркас", "фундамент", "плита", "ростверк", "опалуб", "перекрыт",
    "стяжк", "гидроизоляц", "утепл", "дренаж", "засыпк", "сетка",
]

UNIT_VARIANTS = [
    r"м2", r"м²", r"кв\.?\s*м",
    r"м3", r"м³", r"куб\.?\s*м",
    r"м\.?\s*п\.?", r"п\.?\s*м\.?", r"пог\.?\s*м",
    r"тн", r"тонн?", r"тонна", r"т",
    r"шт\.?",
    r"кг\.?",
]

UNIT_TOKEN_RE = re.compile(
    r"(?<![A-Za-zА-Яа-я])(" + "|".join(UNIT_VARIANTS) + r")(?![A-Za-zА-Яа-я])",
    re.IGNORECASE,
)

NUMBER_TOKEN_RE = re.compile(
    r"(?<!\d)(\d{1,3}(?:[ \u00A0]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)(?!\d)"
)

STRICT_NUMBER_RE = re.compile(
    r"^\s*(\d{1,3}(?:[ \u00A0]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)\s*$"
)

PAIR_RE = re.compile(
    r"(?P<num>\d{1,3}(?:[ \u00A0]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)\s*"
    r"(?P<unit>" + "|".join(UNIT_VARIANTS) + r")",
    re.IGNORECASE,
)


class EstimateEngine:
    @staticmethod
    def _normalize_unit(unit_str: str) -> str:
        if not unit_str:
            return ""
        t = unit_str.lower().replace(" ", "").replace(".", "")
        if t in ("м2", "м²", "квм"):
            return "м2"
        if t in ("м3", "м³", "кубм"):
            return "м3"
        if t in ("мп", "пм", "погм"):
            return "п.м"
        if t in ("тн", "тонн", "тонна", "т"):
            return "тн"
        if t == "шт":
            return "шт"
        if t == "кг":
            return "кг"
        return unit_str.strip()

    @staticmethod
    def _parse_number(value: Any) -> Optional[float]:
        if value is None:
            return None

        if isinstance(value, (int, float)):
            try:
                return float(value)
            except Exception:
                return None

        s = str(value).strip()
        if not s:
            return None

        m = NUMBER_TOKEN_RE.search(s.replace("\u00A0", " "))
        if not m:
            return None

        num = m.group(1).replace(" ", "").replace("\u00A0", "").replace(",", ".")
        try:
            return float(num)
        except Exception:
            return None

    @staticmethod
    def _parse_number_strict(value: Any) -> Optional[float]:
        if value is None:
            return None

        if isinstance(value, (int, float)):
            try:
                return float(value)
            except Exception:
                return None

        s = str(value).strip().replace("\u00A0", " ")
        if not s:
            return None

        m = STRICT_NUMBER_RE.fullmatch(s)
        if not m:
            return None

        num = m.group(1).replace(" ", "").replace(",", ".")
        try:
            return float(num)
        except Exception:
            return None

    @staticmethod
    def _has_target_category(text: str) -> bool:
        t = (text or "").lower()
        return any(cat in t for cat in TARGET_CATEGORIES)

    @staticmethod
    def _extract_pairs(text: str) -> List[Tuple[float, str, str]]:
        out: List[Tuple[float, str, str]] = []
        if not text:
            return out

        for m in PAIR_RE.finditer(text.replace("\u00A0", " ")):
            raw_num = m.group("num")
            raw_unit = m.group("unit")
            qty = EstimateEngine._parse_number(raw_num)
            unit = EstimateEngine._normalize_unit(raw_unit)
            if qty is not None and unit:
                out.append((qty, unit, m.group(0)))
        return out

    @staticmethod
    def _extract_unit_token(text: str) -> Optional[str]:
        if not text:
            return None
        m = UNIT_TOKEN_RE.search(text)
        if not m:
            return None
        return EstimateEngine._normalize_unit(m.group(1))

    @staticmethod
    def _cleanup_name(text: str, matched_fragment: Optional[str] = None) -> str:
        name = str(text or "")
        if matched_fragment:
            name = name.replace(matched_fragment, " ")
        name = re.sub(r"\s+", " ", name)
        name = re.sub(r"^[,;:.\-\s|]+|[,;:.\-\s|]+$", "", name)
        return name.strip()

    @staticmethod
    def _is_bad_name(text: str) -> bool:
        t = (text or "").strip()
        if not t:
            return True
        if t in {"-", "|", "—", ":"}:
            return True
        return False

    @staticmethod
    def _pick_best_pair_from_cells(cells: List[str]) -> Tuple[Optional[Tuple[float, str, str]], Optional[int]]:
        found: List[Tuple[int, Tuple[float, str, str]]] = []
        for idx, cell in enumerate(cells):
            pairs = EstimateEngine._extract_pairs(cell)
            for pair in pairs:
                found.append((idx, pair))

        if not found:
            return None, None

        best_idx, best_pair = found[-1]
        return best_pair, best_idx

    @staticmethod
    def _pick_split_pair_from_cells(cells: List[str]) -> Tuple[Optional[float], Optional[str], Optional[int], Optional[int]]:
        numeric_cells: List[Tuple[int, float]] = []
        unit_cells: List[Tuple[int, str]] = []

        for idx, cell in enumerate(cells):
            n = EstimateEngine._parse_number_strict(cell)
            u = EstimateEngine._extract_unit_token(cell)

            if n is not None:
                numeric_cells.append((idx, n))
            if u is not None:
                unit_cells.append((idx, u))

        if not numeric_cells or not unit_cells:
            return None, None, None, None

        qty_idx, qty = numeric_cells[-1]

        best = None
        for unit_idx, unit in unit_cells:
            dist = abs(unit_idx - qty_idx)
            candidate = (dist, unit_idx, unit)
            if best is None or candidate < best:
                best = candidate

        if best is None:
            return None, None, None, None

        _, unit_idx, unit = best
        return qty, unit, qty_idx, unit_idx

    @staticmethod
    def _row_to_item(row: List[Any], source: str) -> Optional[Dict[str, Any]]:
        cells = [("" if c is None else str(c).strip()) for c in row]
        row_text = " | ".join(cells).strip()
        if not row_text:
            return None

        if not EstimateEngine._has_target_category(row_text):
            return None

        best_pair, best_cell_idx = EstimateEngine._pick_best_pair_from_cells(cells)

        qty = None
        unit = None
        matched_fragment = None
        qty_idx = None
        unit_idx = None

        if best_pair is not None:
            qty, unit, matched_fragment = best_pair
            qty_idx = best_cell_idx
            unit_idx = best_cell_idx
        else:
            row_pairs = EstimateEngine._extract_pairs(row_text)
            if row_pairs:
                qty, unit, matched_fragment = row_pairs[-1]
            else:
                qty, unit, qty_idx, unit_idx = EstimateEngine._pick_split_pair_from_cells(cells)

        if qty is None or unit is None:
            return None

        if abs(float(qty)) < 1e-12:
            return None

        name_parts: List[str] = []
        for idx, cell in enumerate(cells):
            cell_clean = cell.strip()
            if not cell_clean:
                continue

            if qty_idx is not None and idx == qty_idx:
                if matched_fragment and qty_idx == unit_idx:
                    cleaned = EstimateEngine._cleanup_name(cell, matched_fragment)
                    if cleaned and not STRICT_NUMBER_RE.fullmatch(cleaned) and not EstimateEngine._is_bad_name(cleaned):
                        name_parts.append(cleaned)
                continue

            if unit_idx is not None and idx == unit_idx:
                if qty_idx != unit_idx:
                    continue

            if STRICT_NUMBER_RE.fullmatch(cell_clean):
                continue

            if UNIT_TOKEN_RE.fullmatch(cell_clean):
                continue

            if not EstimateEngine._is_bad_name(cell_clean):
                name_parts.append(cell_clean)

        name = " ".join(name_parts).strip()
        name = re.sub(r"\s+", " ", name)

        if not name:
            name = EstimateEngine._cleanup_name(row_text, matched_fragment)

        if EstimateEngine._is_bad_name(name):
            return None

        return {
            "source": source,
            "name": name,
            "unit": unit,
            "qty": qty,
            "raw_row": cells,
        }

    @staticmethod
    def _line_to_item(line: str, line_no: int) -> Optional[Dict[str, Any]]:
        text = (line or "").strip()
        if not text:
            return None

        if not EstimateEngine._has_target_category(text):
            return None

        pairs = EstimateEngine._extract_pairs(text)
        if not pairs:
            return None

        qty, unit, matched_fragment = pairs[-1]

        if abs(float(qty)) < 1e-12:
            return None

        name = EstimateEngine._cleanup_name(text, matched_fragment)

        if EstimateEngine._is_bad_name(name):
            name = text[:80].strip()

        if EstimateEngine._is_bad_name(name):
            return None

        return {
            "source": f"text_line_{line_no}",
            "name": name,
            "unit": unit,
            "qty": qty,
            "raw_text": text,
        }

    @staticmethod
    def _dedupe(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        out = []
        for item in items:
            try:
                qty_float = round(float(item.get("qty")), 6)
            except Exception:
                continue

            key = (
                str(item.get("name", "")).lower().strip(),
                str(item.get("unit", "")).lower().strip(),
                qty_float,
            )
            if key in seen:
                continue
            seen.add(key)
            out.append(item)
        return out

    @staticmethod
    def extract_volumes(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        if parsed_data.get("status") != "ok":
            return {"status": "failed", "error": "Invalid input data"}

        extracted_items: List[Dict[str, Any]] = []
        warnings: List[str] = []

        for table in parsed_data.get("tables", []):
            title = table.get("title", "Unknown Table")
            data = table.get("data", [])
            for row in data:
                try:
                    item = EstimateEngine._row_to_item(row, f"table:{title}")
                    if item:
                        extracted_items.append(item)
                except Exception as e:
                    warnings.append(f"table parse warning [{title}]: {type(e).__name__}")

        text_lines = parsed_data.get("text", "").splitlines()
        for idx, line in enumerate(text_lines, start=1):
            try:
                item = EstimateEngine._line_to_item(line, idx)
                if item:
                    extracted_items.append(item)
            except Exception as e:
                warnings.append(f"text parse warning [line {idx}]: {type(e).__name__}")

        extracted_items = EstimateEngine._dedupe(extracted_items)

        totals_by_unit: Dict[str, float] = {}
        for item in extracted_items:
            try:
                qty_float = float(item["qty"])
                unit = item["unit"]
                totals_by_unit[unit] = round(totals_by_unit.get(unit, 0.0) + qty_float, 6)
            except Exception:
                pass

        totals_by_unit = dict(sorted(totals_by_unit.items(), key=lambda kv: kv[0]))

        return {
            "status": "ok",
            "file_name": parsed_data.get("meta", {}).get("file_name", "unknown"),
            "items_count": len(extracted_items),
            "items": extracted_items,
            "totals_by_unit": totals_by_unit,
            "warnings": warnings[:50],
        }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            parsed_data = json.load(f)
        print(json.dumps(EstimateEngine.extract_volumes(parsed_data), ensure_ascii=False))
    else:
        print("ESTIMATE_ENGINE_READY")
