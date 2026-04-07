from __future__ import annotations

import pandas as pd

def parse_excel(path: str) -> str:
    # Patch 3: Engine logic with try/except for xlrd
    if path.lower().endswith(".xlsx"):
        sheets = pd.read_excel(path, sheet_name=None, engine="openpyxl")
    else:
        try:
            sheets = pd.read_excel(path, sheet_name=None, engine="xlrd")
        except Exception as e:
            return f"XLS_ERROR: {e}"
            
    out = []
    for name, df in sheets.items():
        try:
            body = df.to_string(index=False)
        except Exception:
            body = df.to_string()
        out.append(f"--- Лист: {name} ---\n{body}")
    return "\n\n".join(out).strip()

def parse_csv(path: str) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1251"):
        try:
            df = pd.read_csv(path, encoding=enc)
            try:
                return df.to_string(index=False).strip()
            except Exception:
                return df.to_string().strip()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return f"CSV_ERROR: {e}"
    return "CSV_ENCODING_ERROR"

def run(ctx: dict) -> dict:
    p = str((ctx.get("file_path") or "")).strip()
    if not p:
        return {"type": "table", "text": "", "error": "empty file_path"}

    lp = p.lower()
    text = ""

    try:
        if lp.endswith((".xlsx", ".xls")):
            text = parse_excel(p)
        elif lp.endswith(".csv"):
            text = parse_csv(p)
        else:
            return {"type": "table", "text": "", "error": "unsupported extension"}
    except Exception as e:
        return {"type": "table", "text": "", "error": f"TABLE_PARSE_ERROR: {e}"}

    return {"type": "table", "text": text}
