#!/usr/bin/env python3
"""
CONTEXT AGGREGATOR v3
Читает GitHub -> собирает ONE_SHARED_CONTEXT.md -> git push
Без обрезки для ключевых файлов
"""
import os, base64, json, urllib.request, urllib.error
from datetime import datetime, timezone
# NO_TRUNCATE_PATHS_V1 — каноны/архитектура/хендоффы/репорты идут полностью
NO_TRUNCATE_PATHS = (
    'docs/CANON_FINAL/',
    'docs/ARCHITECTURE/',
    'docs/HANDOFFS/',
    'docs/REPORTS/',
)

REPO = "rj7hmz9cvm-lgtm/areal-neva-core"
OUTPUT = "docs/SHARED_CONTEXT/ONE_SHARED_CONTEXT.md"

READ_DIRS = [
    "docs/CANON_FINAL",
    "docs/HANDOFFS",
    "docs/REPORTS",
    "docs/ARCHITECTURE",
]

def gh(path, token, method="GET", data=None):
    url = f"https://api.github.com/repos/{REPO}/{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "areal-aggregator"
    })
    if data:
        req.method = method
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} {path}")
        return None

def get_file(path, token):
    r = gh(f"contents/{path}", token)
    if r and "content" in r:
        return base64.b64decode(r["content"]).decode("utf-8", errors="replace"), r.get("sha")
    return None, None

def list_dir(path, token):
    r = gh(f"contents/{path}", token)
    if isinstance(r, list):
        return [(f["name"], f["path"], f["type"]) for f in r]
    return []

def collect_files(token):
    files = {}
    for d in READ_DIRS:
        items = list_dir(d, token)
        for name, path, typ in items:
            if typ == "file" and name.endswith(".md"):
                content, _ = get_file(path, token)
                if content:
                    files[path] = content
                    print(f"  READ {path} ({len(content)} chars)")
    return files

def build_context(files):
    ts = datetime.now(timezone.utc).isoformat()
    lines = [f"# ONE_SHARED_CONTEXT", f"updated_at: {ts}", ""]

    lines.append("## SOURCE FILES")
    for path in sorted(files.keys()):
        lines.append(f"- {path} ({len(files[path])} chars)")
    lines.append("")

    for path, content in files.items():
        if "LATEST_HANDOFF" in path:
            lines.append("## LATEST_HANDOFF (FULL)")
            lines.append(content)
            lines.append("")

    for path, content in files.items():
        if "NOT_CLOSED" in path:
            lines.append("## NOT_CLOSED (FULL)")
            lines.append(content)
            lines.append("")

    lines.append("## CANON_FINAL")
    for path, content in sorted(files.items()):
        if "CANON_FINAL" in path:
            lines.append(f"\n### {path}")
            lines.append(content)
    lines.append("")

    lines.append("## ARCHITECTURE")
    for path, content in sorted(files.items()):
        if "ARCHITECTURE" in path:
            lines.append(f"\n### {path}")
            lines.append(content)
    lines.append("")

    lines.append("## HANDOFFS")
    for path, content in sorted(files.items()):
        if "HANDOFFS" in path and "LATEST_HANDOFF" not in path:
            lines.append(f"\n### {path}")
            lines.append(content)
    lines.append("")

    lines.append("## REPORTS")
    for path, content in sorted(files.items()):
        if "REPORTS" in path and "NOT_CLOSED" not in path:
            lines.append(f"\n### {path}")
            lines.append(content)

    return "\n".join(lines)

def push_file(path, content, token):
    _, sha = get_file(path, token)
    data = {
        "message": f"AGG: ONE_SHARED_CONTEXT {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "content": base64.b64encode(content.encode()).decode(),
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
    r = gh(f"contents/{path}", token, method="PUT", data=data)
    if r and "content" in r:
        print(f"PUSH OK: {r['commit']['sha'][:7]}")
        return True
    print("PUSH FAILED")
    return False

def aggregate():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("ERROR: GITHUB_TOKEN не задан")
        return
    print(f"AGG START {datetime.utcnow().isoformat()}")
    files = collect_files(token)
    print(f"Total: {len(files)} files")
    content = build_context(files)
    print(f"Context size: {len(content)} chars")
    push_file(OUTPUT, content, token)
    print("AGG DONE")

if __name__ == "__main__":
    aggregate()
