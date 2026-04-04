import sqlite3, time
# Упрощенная логика для теста связи: пишет всё входящее в базу
def insert_task(chat_id, text):
    with sqlite3.connect("/root/.areal-neva-core/data/memory/core.db") as conn:
        conn.execute("INSERT INTO tasks (chat_id, prompt, status) VALUES (?, ?, 'new')", (str(chat_id), text))
# Здесь должен быть твой реальный код Telethon, вызывающий insert_task()
