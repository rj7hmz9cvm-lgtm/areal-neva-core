# === FULLFIX_19_MEMORY_CLIENT_V2 ===
import sqlite3, logging, json, uuid
from pathlib import Path

MEMORY_DB = "/root/.areal-neva-core/data/memory.db"
logger = logging.getLogger("memory_client")

def _ensure():
    Path(MEMORY_DB).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(MEMORY_DB, timeout=10) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS memory(
                id TEXT PRIMARY KEY,
                chat_id TEXT,
                key TEXT,
                value TEXT,
                timestamp TEXT,
                topic_id INTEGER DEFAULT 0,
                scope TEXT DEFAULT 'topic'
            )
        """)
        cols = [r[1] for r in c.execute("PRAGMA table_info(memory)").fetchall()]
        if "topic_id" not in cols:
            c.execute("ALTER TABLE memory ADD COLUMN topic_id INTEGER DEFAULT 0")
        if "scope" not in cols:
            c.execute("ALTER TABLE memory ADD COLUMN scope TEXT DEFAULT 'topic'")
        c.execute("CREATE INDEX IF NOT EXISTS idx_memory_chat_topic ON memory(chat_id, topic_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_memory_value ON memory(value)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_memory_key ON memory(key)")
        c.commit()

def save_memory(chat_id, key, value, topic_id=0, scope="topic"):
    try:
        _ensure()
        v = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        with sqlite3.connect(MEMORY_DB, timeout=10) as c:
            row = c.execute(
                "SELECT id FROM memory WHERE chat_id=? AND topic_id=? AND key=?",
                (str(chat_id), int(topic_id or 0), str(key))
            ).fetchone()
            if row:
                c.execute(
                    "UPDATE memory SET value=?, timestamp=datetime('now'), scope=? WHERE id=?",
                    (v, str(scope), row[0])
                )
            else:
                c.execute(
                    "INSERT INTO memory(id, chat_id, topic_id, key, value, scope, timestamp) VALUES(?,?,?,?,?,?,datetime('now'))",
                    (str(uuid.uuid4()), str(chat_id), int(topic_id or 0), str(key), v, str(scope))
                )
            c.commit()
        return True
    except Exception as e:
        logger.error("save_memory err=%s", e)
        return False

def get_memory(chat_id, key, topic_id=0):
    try:
        _ensure()
        with sqlite3.connect(MEMORY_DB, timeout=10) as c:
            r = c.execute(
                "SELECT value FROM memory WHERE chat_id=? AND COALESCE(topic_id,0)=? AND key=? ORDER BY timestamp DESC LIMIT 1",
                (str(chat_id), int(topic_id or 0), str(key))
            ).fetchone()
            return r[0] if r else None
    except Exception as e:
        logger.error("get_memory err=%s", e)
        return None

def search_memory(chat_id, query, topic_id=None, limit=10):
    try:
        _ensure()
        with sqlite3.connect(MEMORY_DB, timeout=10) as c:
            if topic_id is not None:
                rows = c.execute(
                    "SELECT key,value,timestamp FROM memory WHERE chat_id=? AND COALESCE(topic_id,0)=? AND value LIKE ? ORDER BY timestamp DESC LIMIT ?",
                    (str(chat_id), int(topic_id or 0), "%"+str(query)+"%", int(limit))
                ).fetchall()
            else:
                rows = c.execute(
                    "SELECT key,value,timestamp FROM memory WHERE chat_id=? AND value LIKE ? ORDER BY timestamp DESC LIMIT ?",
                    (str(chat_id), "%"+str(query)+"%", int(limit))
                ).fetchall()
            return [{"key": r[0], "value": r[1], "ts": r[2]} for r in rows]
    except Exception as e:
        logger.error("search_memory err=%s", e)
        return []

def get_active_context(chat_id, topic_id=0, limit=5):
    try:
        _ensure()
        with sqlite3.connect(MEMORY_DB, timeout=10) as c:
            rows = c.execute(
                "SELECT key,value FROM memory WHERE chat_id=? AND COALESCE(topic_id,0)=? AND COALESCE(scope,'topic') IN ('topic','active') ORDER BY timestamp DESC LIMIT ?",
                (str(chat_id), int(topic_id or 0), int(limit))
            ).fetchall()
            return [{"key": r[0], "value": r[1]} for r in rows]
    except Exception as e:
        logger.error("get_active_context err=%s", e)
        return []

def list_memory(chat_id, topic_id=None, prefix=None, limit=20):
    try:
        _ensure()
        with sqlite3.connect(MEMORY_DB, timeout=10) as c:
            q = "SELECT key,timestamp FROM memory WHERE chat_id=?"
            params = [str(chat_id)]
            if topic_id is not None:
                q += " AND COALESCE(topic_id,0)=?"
                params.append(int(topic_id or 0))
            if prefix:
                q += " AND key LIKE ?"
                params.append(str(prefix)+"%")
            q += " ORDER BY timestamp DESC LIMIT ?"
            params.append(int(limit))
            rows = c.execute(q, params).fetchall()
            return [{"key": r[0], "ts": r[1]} for r in rows]
    except Exception as e:
        logger.error("list_memory err=%s", e)
        return []
# === END FULLFIX_19_MEMORY_CLIENT_V2 ===
