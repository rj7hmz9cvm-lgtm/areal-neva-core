from __future__ import annotations

from pathlib import Path

try:
    from core.document_context import extract_document_context
except Exception:
    def extract_document_context(path_str: str) -> dict:
        return {"ok": False, "text": ""}

ROOTS = [
    Path("/root/.areal-neva-core"),
    Path("/root/AI_ORCHESTRA"),
]

ALLOWED_EXT = {
    ".txt", ".md", ".json", ".csv",
    ".py", ".log",
    ".pdf", ".docx", ".xlsx", ".xls",
    ".jpg", ".jpeg", ".png", ".webp",
    ".dxf", ".dwg",
}

SKIP_DIR_PARTS = {
    ".git", ".venv", "__pycache__", "node_modules",
}

MAX_FILE_SIZE = 3 * 1024 * 1024

def _iter_files():
    for root in ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            try:
                if not p.is_file():
                    continue
                if any(part in SKIP_DIR_PARTS for part in p.parts):
                    continue
                if p.suffix.lower() not in ALLOWED_EXT:
                    continue
                if p.stat().st_size > MAX_FILE_SIZE:
                    continue
                yield p
            except Exception:
                continue

def _safe_read_text(path: Path, limit: int = 12000) -> str:
    for enc in ("utf-8", "cp1251", "latin-1"):
        try:
            return path.read_text(encoding=enc, errors="ignore")[:limit]
        except Exception:
            continue
    return ""

def get_project_context(query: str, limit: int = 5) -> str:
    rows = search_project_files(query, limit=limit)
    if not rows:
        return ""
    parts = ["КОНТЕКСТ ПРОЕКТА"]
    for row in rows:
        parts.append(f"- {row.get('path', '')}")
        snippet = (row.get("snippet") or "").strip()
        if snippet:
            parts.append(snippet[:300])
    return "\n".join(parts)

def search_project_files(query: str, limit: int = 5) -> list[dict]:
    q = (query or "").lower().strip()
    if not q:
        return []

    terms = [x for x in q.split() if len(x) >= 3][:8]
    if not terms:
        return []

    scored: list[tuple[int, dict]] = []

    for path in _iter_files():
        try:
            path_l = str(path).lower()
            score = 0

            for term in terms:
                if term in path_l:
                    score += 5

            ext = path.suffix.lower()
            text = ""
            if ext in {".txt", ".md", ".json", ".csv", ".py", ".log"}:
                text = _safe_read_text(path, 16000)
            else:
                doc_data = extract_document_context(str(path))
                if doc_data.get("ok"):
                    text = (doc_data.get("text") or "")[:8000]

            text_l = text.lower()
            for term in terms:
                if term in text_l:
                    score += 2

            if score <= 0:
                continue

            snippet = ""
            for term in terms:
                idx = text_l.find(term)
                if idx != -1:
                    start = max(0, idx - 120)
                    end = min(len(text), idx + 280)
                    snippet = text[start:end].replace("\n", " ").strip()
                    break

            scored.append((
                score,
                {
                    "path": str(path),
                    "name": path.name,
                    "ext": ext,
                    "snippet": snippet,
                }
            ))
        except Exception:
            continue

    scored.sort(key=lambda x: (-x[0], x[1]["path"]))
    return [item for _, item in scored[:limit]]
