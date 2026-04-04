import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
class GoogleClient:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.cfg = json.load(f)["google_workspace"]
        self.creds = service_account.Credentials.from_service_account_file(
            self.cfg["service_account_file"], 
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
        )
        self.sheets = build('sheets', 'v4', credentials=self.creds).spreadsheets()
        self.docs = build('docs', 'v1', credentials=self.creds).documents()
        self.drive = build('drive', 'v3', credentials=self.creds).files()
    def share(self, file_id):
        self.drive.permissions().create(fileId=file_id, body={'type': 'user', 'role': 'writer', 'emailAddress': self.cfg["my_email"]}).execute()
    def safe_copy(self, template_id, title, mode='sheet'):
        try:
            return self.drive.copy(fileId=template_id, body={'name': title}).execute()['id']
        except:
            if mode == 'sheet': return self.sheets.create(body={'properties': {'title': title}}).execute()['spreadsheetId']
            return self.docs.create(body={'title': title}).execute()['documentId']
