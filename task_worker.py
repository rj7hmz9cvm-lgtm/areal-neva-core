import asyncio, sqlite3, os
from core.google_client import GoogleClient
from core.table_engine import EstimateData, create_estimate_sheet
from core.project_memory import save_last_estimate

DB_PATH = "/root/.areal-neva-core/data/memory/core.db"
CONFIG = "/root/.areal-neva-core/core/config_secrets.json"

async def process_task(chat_id, prompt):
    try:
        g_client = GoogleClient(CONFIG)
        low = prompt.lower()
        if any(x in low for x in ['смета', 'расчет', 'таблиц']):
            data = EstimateData(prompt, vat_enabled='без ндс' not in low)
            url = await create_estimate_sheet(g_client, data, g_client.cfg.get("estimate_template_id"))
            save_last_estimate(chat_id, url.split('/')[-2], url)
            return f"✅ Смета готова: {url}"
        return "❓ Не распознал команду."
    except Exception as e: return f"❌ Ошибка: {e}"

async def main_loop():
    print("Worker: Started")
    while True:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                task = conn.execute("SELECT id, chat_id, prompt FROM tasks WHERE status = 'new' LIMIT 1").fetchone()
                if task:
                    tid, cid, txt = task
                    conn.execute("UPDATE tasks SET status = 'processing' WHERE id = ?", (tid,))
                    conn.commit()
                    res = await process_task(cid, txt)
                    conn.execute("UPDATE tasks SET status = 'done', response = ? WHERE id = ?", (res, tid))
                    conn.commit()
        except: pass
        await asyncio.sleep(2)
if __name__ == "__main__": asyncio.run(main_loop())
