import sqlite3
from datetime import datetime
DB = "/root/.areal-neva-core/data/core.db"
def _norm(v): return str(v or "").lower()
def init():
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS cognitive_journal(id INTEGER PRIMARY KEY, chat_id INTEGER, entry_type TEXT, content TEXT, content_norm TEXT, file_meta TEXT, file_meta_norm TEXT, created_at TEXT)")
        cols = [r[1] for r in c.execute("PRAGMA table_info(cognitive_journal)").fetchall()]
        if "content_norm" not in cols: c.execute("ALTER TABLE cognitive_journal ADD COLUMN content_norm TEXT")
        if "file_meta_norm" not in cols: c.execute("ALTER TABLE cognitive_journal ADD COLUMN file_meta_norm TEXT")
        c.execute("UPDATE cognitive_journal SET content_norm=LOWER(SUBSTR(content,1,3000)) WHERE content_norm IS NULL")
        c.execute("UPDATE cognitive_journal SET file_meta_norm=LOWER(SUBSTR(file_meta,1,500)) WHERE file_meta_norm IS NULL")
def record(chat_id, entry_type, content="", file_meta=""):
    if not content and not file_meta: return
    init()
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO cognitive_journal(chat_id,entry_type,content,content_norm,file_meta,file_meta_norm,created_at) VALUES(?,?,?,?,?,?,?)",
                  (int(chat_id or 0), str(entry_type)[:50], str(content)[:3000], _norm(content)[:3000], str(file_meta)[:500], _norm(file_meta)[:500], datetime.utcnow().isoformat()))
def recall(chat_id, query, limit=8):
    init(); q = _norm(query).strip()
    if len(q) < 3: return ""
    words, out = [w for w in q.split() if len(w) > 2][:6], []
    with sqlite3.connect(DB) as c:
        for w in words:
            rows = c.execute("SELECT content, file_meta, created_at FROM cognitive_journal WHERE (chat_id=? OR ?=0) AND (content_norm LIKE ? OR file_meta_norm LIKE ?) ORDER BY id DESC LIMIT ?", (int(chat_id or 0), int(chat_id or 0), f"%{w}%", f"%{w}%", int(limit))).fetchall()
            for r in rows: out.append(f"[{r[2]}] {r[0]} {r[1]}")
    return "\n--- MEMORY ---\n" + "\n".join(list(dict.fromkeys(out)))[:6000] if out else ""
