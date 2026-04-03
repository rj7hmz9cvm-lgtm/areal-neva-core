#!/usr/bin/env python3
import sys, json, os

MAP="/root/.areal-neva-core/data/memory/projects_map.json"

def load():
    if not os.path.exists(MAP):
        return {}
    try:
        with open(MAP, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save(data):
    os.makedirs(os.path.dirname(MAP), exist_ok=True)
    with open(MAP, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main(name: str):
    name = name.strip()
    if not name:
        raise SystemExit("EMPTY_PROJECT")
    data = load()
    if name not in data:
        data[name] = {"disabled_auto_topic_creation": True}
        save(data)
        print(f"REGISTERED_ONLY:{name}")
    else:
        print(f"EXISTS:{name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: sync_projects.py PROJECT_NAME")
    main(sys.argv[1])
