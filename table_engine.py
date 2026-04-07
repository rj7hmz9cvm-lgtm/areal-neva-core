import pandas as pd
from pathlib import Path
def read(path):
    try:
        p = Path(path); s = p.suffix.lower()
        if s == ".xlsx": df = pd.read_excel(p)
        elif s == ".csv": df = pd.read_csv(p)
        else: return ""
        return ("\n--- TABLE DATA ---\n" + df.head(50).to_string())[:20000]
    except Exception: return ""
