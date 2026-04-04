import sqlite3
DB_PATH = "/root/.areal-neva-core/data/memory/core.db"
def save_last_estimate(chat_id, estimate_id, url):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO project_memory VALUES (?, ?, ?)", (chat_id, estimate_id, url))
def get_last_estimate(chat_id):
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT last_estimate_id, last_url FROM project_memory WHERE chat_id = ?", (chat_id,)).fetchone()
