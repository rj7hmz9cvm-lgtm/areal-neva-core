from __future__ import annotations

import json
import time
from flask import Flask, request, Response

import storage_layer

app = Flask(__name__)

def json_response(data, status=200):
    return Response(
        response=json.dumps(data, ensure_ascii=False),
        status=status,
        mimetype="application/json"
    )

@app.route("/", methods=["GET"])
def health():
    return "ok", 200

@app.route("/", methods=["POST"])
def run():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    payload = data.get("payload")

    if payload is None:
        if not prompt:
            return json_response({"ok": False, "error": "no prompt"}, 400)
        payload = {
            "text": prompt,
            "source": "api",
        }

    if isinstance(payload, dict):
        payload.setdefault("source", "api")

    task_id = storage_layer.create_task(
        payload=payload,
        source="api",
        chat_id=data.get("chat_id"),
        msg_id=data.get("msg_id"),
    )

    timeout = int(data.get("timeout") or 1800)
    started = time.time()

    while True:
        task = storage_layer.get_task(task_id)
        if not task:
            return json_response({"ok": False, "error": "task_missing", "task_id": task_id}, 500)

        if task["status"] == "done":
            result = task.get("result")
            stdout = ""

            if isinstance(result, dict):
                if isinstance(result.get("data"), str):
                    stdout = result.get("data", "")
                elif result.get("analysis"):
                    stdout = result.get("analysis", "")
                elif isinstance(result.get("data"), dict) and result["data"].get("summary"):
                    stdout = result["data"].get("summary", "")
                else:
                    stdout = json.dumps(result, ensure_ascii=False)
            else:
                stdout = str(result or "")

            return json_response({
                "ok": True,
                "task_id": task_id,
                "route": task.get("route"),
                "stdout": stdout.strip(),
                "stderr": ""
            }, 200)

        if task["status"] == "failed":
            err = task.get("error")
            stderr = json.dumps(err, ensure_ascii=False) if isinstance(err, (dict, list)) else str(err or "")
            return json_response({
                "ok": False,
                "task_id": task_id,
                "route": task.get("route"),
                "stdout": "",
                "stderr": stderr.strip()
            }, 200)

        if time.time() - started > timeout:
            return json_response({"ok": False, "task_id": task_id, "error": "timeout"}, 504)

        time.sleep(1)

if __name__ == "__main__":
    storage_layer.init_db()
    app.run(host="0.0.0.0", port=8080, threaded=True)
