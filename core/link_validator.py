# === LINK_VALIDATOR_V1 ===
import logging
logger = logging.getLogger(__name__)

def validate_drive_link(url: str, timeout: int = 5) -> bool:
    """Проверить что Drive ссылка доступна (HEAD request)"""
    if not url or "drive.google" not in url:
        return False
    try:
        import urllib.request
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "Mozilla/5.0")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status < 400
    except Exception as e:
        logger.warning("LINK_VALIDATOR_V1 url=%s err=%s", url[:60], e)
        return False

def extract_drive_link(text: str) -> str:
    """Извлечь Drive ссылку из текста"""
    import re
    m = re.search(r"https://drive\.google\.com/\S+", text)
    return m.group(0) if m else ""
# === END LINK_VALIDATOR_V1 ===
