import requests
from urllib.parse import quote, unquote
import html
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def _clean(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def _clean_url(url):
    if not url:
        return ""
    url = html.unescape(url)
    if "uddg=" in url:
        try:
            url = url.split("uddg=", 1)[1]
        except Exception:
            pass
    url = unquote(url)
    if "&rut=" in url:
        url = url.split("&rut=", 1)[0]
    return url.strip()

def search_web(query, limit=8):
    results = []
    seen = set()

    urls = [
        f"https://html.duckduckgo.com/html/?q={quote(query)}",
        f"https://duckduckgo.com/html/?q={quote(query)}",
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            text = r.text

            blocks = text.split("result__body")
            for block in blocks[1:]:
                title = ""
                body = ""
                href = ""

                if "result__a" in block:
                    try:
                        t = block.split("result__a", 1)[1]
                        title = _clean(t.split(">", 1)[1].split("</a>", 1)[0])
                    except Exception:
                        title = ""

                if "uddg=" in block:
                    try:
                        href = _clean_url(block.split("uddg=", 1)[1].split('"', 1)[0])
                    except Exception:
                        href = ""

                if "result__snippet" in block:
                    try:
                        s = block.split("result__snippet", 1)[1]
                        if "</a>" in s:
                            body = _clean(s.split(">", 1)[1].split("</a>", 1)[0])
                        elif "</div>" in s:
                            body = _clean(s.split(">", 1)[1].split("</div>", 1)[0])
                    except Exception:
                        body = ""

                if not title and not body and not href:
                    continue

                key = (title, href)
                if key in seen:
                    continue
                seen.add(key)

                results.append({
                    "title": title,
                    "url": href,
                    "body": body
                })

                if len(results) >= limit:
                    return results

        except Exception:
            continue

    return results

def format_sources(results, max_items=10):
    if not results:
        return "Источники не найдены"

    lines = []
    idx = 1
    for r in results[:max_items]:
        title = r.get("title", "").strip()
        body = r.get("body", "").strip()
        url = r.get("url", "").strip()

        if not title and not body and not url:
            continue

        lines.append(f"{idx}. {title or 'Без названия'}")
        if body:
            lines.append(body)
        if url:
            lines.append(url)
        lines.append("")
        idx += 1

    if not lines:
        return "Источники не найдены"

    return "\n".join(lines).strip()
