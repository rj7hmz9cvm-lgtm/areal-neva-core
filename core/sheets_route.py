# === SHEETS_ROUTE_V1 ===
import os, logging
logger = logging.getLogger(__name__)
CREDENTIALS_PATH = "/root/.areal-neva-core/credentials.json"

def is_sheets_requested(text: str) -> bool:
    # === SHEETS_INTENT_DETECT_V1 ===
    t = (text or "").lower()
    return any(k in t for k in ["таблиц", "sheets", "гугл таблиц", "google sheets"])

async def create_estimate_sheet(rows: list, title: str, chat_id: str, topic_id: int) -> dict:
    if not os.path.exists(CREDENTIALS_PATH):
        return {"success": False, "url": "", "error": "SHEETS_CREDENTIALS_MISSING"}
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        svc = build("sheets", "v4", credentials=creds)
        sheet = svc.spreadsheets().create(body={"properties": {"title": title}}).execute()
        sid = sheet["spreadsheetId"]
        url = f"https://docs.google.com/spreadsheets/d/{sid}/edit"
        header = [["№", "Наименование", "Ед.", "Кол-во", "Цена, руб.", "Сумма, руб."]]
        data_rows = header + [[i+1, r.get("name",""), r.get("unit",""), r.get("qty",0),
                                r.get("price",0), r.get("total",0)] for i, r in enumerate(rows)]
        svc.spreadsheets().values().update(
            spreadsheetId=sid, range="A1",
            valueInputOption="RAW",
            body={"values": data_rows}
        ).execute()
        return {"success": True, "url": url, "sheet_id": sid}
    except Exception as e:
        return {"success": False, "url": "", "error": str(e)}
# === END SHEETS_ROUTE_V1 ===
