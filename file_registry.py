import sqlite3, sys
from pathlib import Path
from datetime import datetime
_BASE = "/root/.areal-neva-core"
if _BASE not in sys.path: sys.path.insert(0, _BASE)
import document_engine, table_engine
DB, ROOTS = "/root/.areal-neva-core/data/core.db", ["/root/.areal-neva-core/data", "/root/AI_ORCHESTRA"]
def _norm(v): return str(v or "").lower()
def init():
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS file_registry(id INTEGER PRIMARY KEY, chat_id INTEGER, path TEXT UNIQUE, filename TEXT, filename_norm TEXT, suffix TEXT, extracted_text TEXT, extracted_text_norm TEXT, file_mtime REAL, indexed_at TEXT)")
        cols = [r[1] for r in c.execute("PRAGMA table_info(file_registry)").fetchall()]
        if "filename_norm" not in cols: c.execute("ALTER TABLE file_registry ADD COLUMN filename_norm TEXT")
        if "extracted_text_norm" not in cols: c.execute("ALTER TABLE file_registry ADD COLUMN extracted_text_norm TEXT")
def index_file(chat_id, path):
    init(); p = Path(path); s = p.suffix.lower()
    txt = table_engine.read(p) if s in (".xlsx", ".csv") else document_engine.read(p)
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO file_registry(chat_id,path,filename,filename_norm,suffix,extracted_text,extracted_text_norm,file_mtime,indexed_at) VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(path) DO UPDATE SET extracted_text=excluded.extracted_text, extracted_text_norm=excluded.extracted_text_norm",
                  (int(chat_id or 0), str(p), p.name, _norm(p.name), s, txt, _norm(txt), float(p.stat().st_mtime), datetime.utcnow().isoformat()))
    return True
def sync():
    for r in ROOTS:
        rp = Path(r)
        if rp.exists():
            for p in rp.rglob("*"):
                if p.is_file() and p.suffix.lower() in [".pdf", ".docx", ".txt", ".xlsx", ".csv", ".jpg", ".png"]: index_file(0, str(p))
def recall(query, chat_id=0):
    init(); q = _norm(query)
    words, out = [w for w in q.split() if len(w) > 2][:5], []
    with sqlite3.connect(DB) as c:
        for w in words:
            for r in c.execute("SELECT filename, path, substr(extracted_text,1,1000) FROM file_registry WHERE filename_norm LIKE ? OR extracted_text_norm LIKE ? LIMIT 5", (f"%{w}%", f"%{w}%")).fetchall():
                out.append(f"[FILE] {r[0]} ({r[1]})\n{r[2]}")
    return "\n--- FILES ---\n" + "\n\n".join(list(dict.fromkeys(out))) if out else ""
