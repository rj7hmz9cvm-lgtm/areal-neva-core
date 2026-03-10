import asyncio
import sqlite3
from pathlib import Path
from datetime import datetime

class StateManager:
    def __init__(self, db_path: Path = Path("data/state.db")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_messages (
                    message_id  INTEGER NOT NULL,
                    phone       TEXT    NOT NULL,
                    chat_id     INTEGER NOT NULL,
                    processed_at TEXT   NOT NULL,
                    PRIMARY KEY (message_id, phone, chat_id)
                )
            """)
            conn.commit()

    async def is_duplicate(self, message_id: int, phone: str, chat_id: int) -> bool:
        async with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute(
                    "SELECT 1 FROM processed_messages WHERE message_id=? AND phone=? AND chat_id=?",
                    (message_id, phone, chat_id)
                ).fetchone()
            return row is not None

    async def mark_processed(self, message_id: int, phone: str, chat_id: int):
        async with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO processed_messages VALUES (?, ?, ?, ?)",
                    (message_id, phone, chat_id, datetime.utcnow().isoformat())
                )
                conn.commit()
