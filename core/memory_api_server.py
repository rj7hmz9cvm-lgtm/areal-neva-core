# === MEMORY_API_SERVER_V1 ===
"""
Memory API Server — порт 8091
Эндпоинты: GET /health | POST /save | POST /archive
Пишет напрямую в data/memory.db
"""
import json
import logging
import sqlite3
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("memory_api")

BASE = Path("/root/.areal-neva-core")
MEM_DB = BASE / "data" / "memory.db"
PORT = 8091
_lock = threading.Lock()


def _db():
    conn = sqlite3.connect(str(MEM_DB), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table():
    with _lock:
        conn = _db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id TEXT PRIMARY KEY,
                chat_id TEXT,
                key TEXT,
                value TEXT,
                timestamp TEXT,
                topic_id INTEGER DEFAULT 0,
                scope TEXT DEFAULT 'topic'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_chat_topic ON memory(chat_id, topic_id)")
        # ARCHIVE_DUPLICATE_GUARD_V1: enforce uniqueness on (chat_id, key)
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_chat_key_unique ON memory(chat_id, key)")
        conn.commit()
        conn.close()


def _save(chat_id, key, value, topic_id=0, scope="topic"):
    import uuid
    ts = datetime.now(timezone.utc).isoformat()
    rid = str(uuid.uuid4())
    with _lock:
        conn = _db()
        # ARCHIVE_DUPLICATE_GUARD_V1: upsert by (chat_id, key) — never create duplicates
        existing = conn.execute(
            "SELECT id FROM memory WHERE chat_id=? AND key=?",
            (str(chat_id), str(key))
        ).fetchone()
        if existing:
            rid = existing[0] or rid
            conn.execute(
                "UPDATE memory SET value=?, timestamp=?, topic_id=?, scope=? WHERE chat_id=? AND key=?",
                (str(value), ts, int(topic_id), str(scope), str(chat_id), str(key))
            )
        else:
            conn.execute(
                "INSERT INTO memory(id,chat_id,key,value,timestamp,topic_id,scope) VALUES(?,?,?,?,?,?,?)",
                (rid, str(chat_id), str(key), str(value), ts, int(topic_id), str(scope))
            )
        conn.commit()
        conn.close()
    return rid


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info("HTTP %s", format % args)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def _respond(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "ok", "port": PORT, "db": str(MEM_DB)})
        else:
            self._respond(404, {"error": "not found"})

    def do_POST(self):
        try:
            raw = self._read_body()
            data = json.loads(raw) if raw else {}
        except Exception as e:
            self._respond(400, {"error": str(e)})
            return

        if self.path in ("/save", "/archive"):
            chat_id = data.get("chat_id", "unknown")
            topic_id = int(data.get("topic_id") or 0)
            task_id = data.get("task_id", "")
            key = f"topic_{topic_id}_archive_{task_id[:8]}" if task_id else f"topic_{topic_id}_save"
            value = json.dumps(data, ensure_ascii=False)
            rid = _save(chat_id, key, value, topic_id, "archive")
            logger.info("MEMORY_API_SAVE id=%s chat=%s topic=%s", rid, chat_id, topic_id)
            self._respond(200, {"ok": True, "id": rid})
        else:
            self._respond(404, {"error": "not found"})


if __name__ == "__main__":
    _ensure_table()
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    logger.info("MEMORY_API_SERVER_V1 started port=%d db=%s", PORT, MEM_DB)
    server.serve_forever()
# === END MEMORY_API_SERVER_V1 ===
