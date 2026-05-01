import os, json, sqlite3, uuid
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
DB = "/root/.areal-neva-core/data/memory.db"
TOKEN = os.getenv("MEMORY_API_TOKEN", "mem-eaf522f4934508438010fb3442a9eebd")

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, chat_id TEXT, key TEXT, value TEXT, timestamp TEXT)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_id ON memory(chat_id)")
        conn.commit()

@app.route("/health", methods=["GET"])
def health(): return jsonify({"status": "ok"})

@app.route("/archive", methods=["POST"])
def archive():  # ARCHIVE_ENDPOINT_FIX_V1
    try:
        data = request.get_json(silent=True) or {}
        chat_id = str(data.get("chat_id") or "unknown")
        topic_id = int(data.get("topic_id") or 0)
        task_id = str(data.get("task_id") or str(uuid.uuid4()))
        value = data.get("value") or json.dumps(data, ensure_ascii=False)
        key = f"topic_{topic_id}_archive_{task_id[:8]}"
        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT OR IGNORE INTO memory (id, chat_id, key, value, timestamp) VALUES (?,?,?,?,?)",
                (str(uuid.uuid4()), chat_id, key, str(value), datetime.utcnow().isoformat()))
            conn.commit()
        return jsonify({"ok": True, "key": key}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/memory", methods=["GET"])
def get_memory():
    if request.headers.get("Authorization") != f"Bearer {TOKEN}": return jsonify({"error": "unauthorized"}), 403
    chat_id = request.args.get("chat_id")
    limit = int(request.args.get("limit", 100))
    with sqlite3.connect(DB) as conn:
        rows = conn.execute("SELECT chat_id, key, value, timestamp FROM memory WHERE chat_id=? ORDER BY timestamp DESC LIMIT ?", (chat_id, limit)).fetchall()
    return jsonify([{"chat_id": r[0], "key": r[1], "value": r[2], "timestamp": r[3]} for r in rows])

@app.route("/memory", methods=["POST"])
def post_memory():
    if request.headers.get("Authorization") != f"Bearer {TOKEN}": return jsonify({"error": "unauthorized"}), 403
    data = request.json
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT INTO memory (id, chat_id, key, value, timestamp) VALUES (?,?,?,?,?)", (str(uuid.uuid4()), data["chat_id"], data.get("key", "full_export"), str(data.get("value", "")), datetime.utcnow().isoformat()))
        conn.commit()
    return jsonify({"status": "ok"}), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8091)
