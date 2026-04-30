# === FULLFIX_FORMAT_ADAPTER_STAGE_7 ===
from __future__ import annotations
from typing import Any, Dict, List

FORMAT_ADAPTER_VERSION = "FORMAT_ADAPTER_V1"

TELEGRAM_MAX = 4096

FORMAT_HANDLERS = {
    "telegram_text": "_to_telegram_text",
    "telegram_table": "_to_telegram_table",
    "xlsx": "_to_xlsx_ref",
    "docx": "_to_docx_ref",
    "pdf": "_to_pdf_ref",
    "json": "_to_json_ref",
    "drive_link": "_to_drive_link",
    "google_sheet": "_to_google_sheet_ref",
    "sources": "_to_sources",
    "script": "_to_telegram_text",
    "mp4": "_to_drive_link",
    "table": "_to_telegram_table",
}


class FormatAdapter:
    def adapt(self, result: Dict[str, Any], formats_out: List[str], payload: Dict[str, Any]) -> Dict[str, Any]:
        adapted = {
            "format_adapter_version": FORMAT_ADAPTER_VERSION,
            "shadow_mode": True,
            "formats_out": formats_out,
            "outputs": {},
        }

        for fmt in (formats_out or ["telegram_text"]):
            handler_name = FORMAT_HANDLERS.get(fmt, "_to_telegram_text")
            handler = getattr(self, handler_name, self._to_telegram_text)
            try:
                adapted["outputs"][fmt] = handler(result, payload)
            except Exception as e:
                adapted["outputs"][fmt] = {"error": str(e)}

        adapted["primary"] = adapted["outputs"].get(formats_out[0] if formats_out else "telegram_text")
        return adapted

    def _to_telegram_text(self, result, payload):
        text = (result.get("result") or {}).get("text") or result.get("text") or ""
        if len(text) > TELEGRAM_MAX:
            text = text[:TELEGRAM_MAX - 3] + "..."
        return {"type": "telegram_text", "text": text, "length": len(text)}

    def _to_telegram_table(self, result, payload):
        rows = (result.get("result") or {}).get("rows") or result.get("rows") or []
        text = (result.get("result") or {}).get("text") or ""
        return {"type": "telegram_table", "rows": rows, "text": text[:TELEGRAM_MAX]}

    def _to_xlsx_ref(self, result, payload):
        url = result.get("artifact_url") or result.get("drive_link") or ""
        return {"type": "xlsx", "url": url, "ready": bool(url)}

    def _to_docx_ref(self, result, payload):
        url = result.get("artifact_url") or result.get("drive_link") or ""
        return {"type": "docx", "url": url, "ready": bool(url)}

    def _to_pdf_ref(self, result, payload):
        url = result.get("artifact_url") or result.get("drive_link") or ""
        return {"type": "pdf", "url": url, "ready": bool(url)}

    def _to_drive_link(self, result, payload):
        url = result.get("drive_link") or result.get("artifact_url") or ""
        return {"type": "drive_link", "url": url, "ready": bool(url)}

    def _to_google_sheet_ref(self, result, payload):
        url = result.get("sheet_url") or result.get("drive_link") or ""
        return {"type": "google_sheet", "url": url, "ready": bool(url)}

    def _to_json_ref(self, result, payload):
        return {"type": "json", "data": result.get("result") or result}

    def _to_sources(self, result, payload):
        sources = result.get("sources") or (result.get("result") or {}).get("sources") or []
        return {"type": "sources", "sources": sources, "count": len(sources)}


def adapt_result(result, formats_out, payload):
    return FormatAdapter().adapt(result, formats_out, payload)
# === END FULLFIX_FORMAT_ADAPTER_STAGE_7 ===
