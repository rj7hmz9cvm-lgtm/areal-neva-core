#!/usr/bin/env python3
"""
CONTEXT AGGREGATOR
Читает chat_exports -> собирает ONE_SHARED_CONTEXT -> git push
Токен из переменной окружения GITHUB_TOKEN
"""
import os, subprocess
from datetime import datetime

REPO = "rj7hmz9cvm-lgtm/areal-neva-core"
BASE = "/root/.areal-neva-core"

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def aggregate():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN не задан")
        return
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"AGGREGATOR START {timestamp}")
    # TODO: читать /root/AI_ORCHESTRA/chat_exports/
    # TODO: собирать ONE_SHARED_CONTEXT.md
    # TODO: git add -A && git commit -m "AGG: {timestamp}" && git push
    print("TODO: не реализован")

if __name__ == "__main__":
    aggregate()
