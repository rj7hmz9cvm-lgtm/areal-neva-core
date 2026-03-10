import requests
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def search_web(query, limit=8):
    results = []

    urls = [
        f"https://html.duckduckgo.com/html/?q={quote(query)}",
        f"https://duckduckgo.com/html/?q={quote(query)}"
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            text = r.text

            chunks = text.split('result__title')
            for chunk in chunks[1:]:
                title = ""
                href = ""
                body = ""

                if 'result__a' in chunk:
                    part = chunk.split('result__a', 1)[1]
                    if '>' in part and '</a>' in part:
                        title = part.split('>', 1)[1].split('</a>', 1)[0]
                        title = (
                            title.replace("<b>", "")
                            .replace("</b>", "")
                            .replace("&amp;", "&")
                            .replace("&#x27;", "'")
                            .replace("&quot;", '"')
                        )

                if 'uddg=' in chunk:
                    try:
                        href = chunk.split('uddg=', 1)[1].split('"', 1)[0]
                    except Exception:
                        href = ""

                if 'result__snippet' in chunk:
                    try:
                        part = chunk.split('result__snippet', 1)[1]
                        if '>' in part and '</a>' in part:
                            body = part.split('>', 1)[1].split('</a>', 1)[0]
                        elif '>' in part and '</div>' in part:
                            body = part.split('>', 1)[1].split('</div>', 1)[0]
                        body = (
                            body.replace("<b>", "")
                            .replace("</b>", "")
                            .replace("&amp;", "&")
                            .replace("&#x27;", "'")
                            .replace("&quot;", '"')
                        )
                    except Exception:
                        body = ""

                if title or body or href:
                    results.append({
                        "title": title.strip(),
                        "url": href.strip(),
                        "body": body.strip()
                    })

                if len(results) >= limit:
                    return results

        except Exception:
            continue

    return results
